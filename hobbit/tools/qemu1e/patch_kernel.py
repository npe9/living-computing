#!/usr/bin/env python3
"""Patch a shipped 1e 386 kernel (9dos/9pc) for two QEMU differences.

Each patch is a byte-pattern match on 8c's code for one source line;
exactly one match is required, and nothing else in the file changes.
Both are documented, with the observations that found them, in
docs/qemu_1e_server.md.

ne2000 -- sys/src/9/pc/ether2000.c `reset` accepts a board only if
    `buf[0x0E] == 0x57 && buf[0x0F] == 0x57`, where buf is the
    station-address PROM read with 16-bit remote DMA into `ushort buf[16]`
    ("We asked for shorts, we got shorts, although the PROM is a byte
    array").  QEMU's NE2000 duplicates each PROM byte into both halves
    (`-trace ne2000_*`: data-port reads ... 0x5757 0x5757), so the words
    are 0x5757 and the probe fails ("#l: no free devices").  The two
    `movzwl XX(%esp),%eax; cmp $0x57,%eax` become `movzbl`: the test
    reads the low byte, the byte the source means.

ident -- sys/src/9/pc/devhard.c `hardident` issues IDENTIFY (0xEC) and
    sleeps until `cmddone` (`cp->cmd == 0`); `hardintr` reads the data
    and sets `cp->cmd = Cident2` (0xFF, "pseudo command for post Cident
    interrupt") before its `wakeup`.  QEMU completes IDENTIFY and raises
    IRQ14 during the `outb` of the command, before the process reaches
    `sleep`, so the wakeup finds no sleeper and `sleep` then sees
    cmd == 0xFF and waits for ever (`-trace ide_*,pic_*`: one IRQ14, 256
    data words read, no further IDE command; boot stops at "fs...").  A
    real 1992 drive takes milliseconds, so the race never showed.  The
    patch stores 0 instead of Cident2: `cmddone` is then true, and
    `hardident`'s `if(cp->cmd == Cident2) tsleep(...)` (waiting for the
    extra interrupt QEMU never sends) is skipped.

probe -- devhard.c `hardprobe` (called by `hardparams` right after
    `hardident` to check the last sector) smallocs `buf` but never sets
    `cp->buf = buf`, so `hardintr`'s Cread case (`if(addr){ ... inss }`)
    leaves the sector in the drive.  A real drive accepts the next command
    anyway; QEMU ignores commands while DRQ is set, so the next one (the
    SET FEATURES of `hardsetbuf`) never completes and attach hangs
    (`-trace ide_*`: status 0x58 after the probe's IRQ14, then 0xEF with
    no IRQ).  The patch rewrites hardprobe's register set-up

        cp->dp = dp; cp->status = 0; cp->nsecs = 1; cp->sofar = 0;

    (22 bytes) as

        cp->buf = buf; cp->sofar = 0; cp->status = 0; cp->nsecs = 1;

    dropping `cp->dp = dp`, which `hardident(dp)` -- hardprobe's only
    predecessor in its only caller, `hardparams` -- has just set; hardprobe
    already sets `cp->buf = 0` after the sleep.

With --strip, the symbol and pc/line tables are dropped (header words
syms, spsz, pcsz set to 0, file cut after text+data), as `strip` would;
386/9pc (583,255 bytes with symbols) then fits on the floppy in place of
9DOS.

usage: patch_kernel.py [--strip] in-kernel out-kernel
"""
import re
import sys

TEXTVA = 0x80001020     # 386 a.out: 32-byte header, then text at 0x80001020


def ne2000(b):
    pat = re.compile(rb'\x0f\xb7\x44\x24.\x83\xf8\x57\x75.'
                     rb'\x0f\xb7\x44\x24.\x83\xf8\x57\x74.', re.S)
    m = list(pat.finditer(b))
    if len(m) != 1:
        sys.exit('ne2000: %d matches, want 1' % len(m))
    o = m[0].start()
    b[o + 1] = 0xb6
    b[o + 11] = 0xb6
    return [o + 1, o + 11]


def ident(b):
    # if(cp->cmd == Cread) cp->cmd = 0; else cp->cmd = Cident2;
    #   cmp $0x20,%eax; jne L; andl $0,off(%reg); ... L: movl $0xff,off(%reg)
    pat = re.compile(rb'\x83\xf8\x20\x75.\x83\x65(.)\x00.{0,40}?'
                     rb'\xc7\x45\1\xff\x00\x00\x00', re.S)
    m = list(pat.finditer(b))
    if len(m) != 1:
        sys.exit('ident: %d matches, want 1' % len(m))
    o = m[0].end() - 4
    assert b[o] == 0xff
    b[o] = 0x00
    return [o]


def probe(b):
    # cp in %edx, cp->cmd = Cread (0x20) at 0x1c, then the 22 bytes:
    old = bytes.fromhex('8b542414' 'c7421c20000000'
                        '8b4c241c' '894a44'        # cp->dp = dp      (0x44)
                        '83623c00'                 # cp->status = 0   (0x3c)
                        'c74234' '01000000'        # cp->nsecs = 1    (0x34)
                        '83623800')                # cp->sofar = 0    (0x38)
    new = bytes.fromhex('8b442410' '894230'        # cp->buf = buf    (0x30)
                        '31c0' '894238' '89423c'   # sofar = status = 0
                        '40' '894234'              # nsecs = 1
                        '909090')
    o = [m.start() for m in re.finditer(re.escape(old), b)]
    if len(o) != 1:
        sys.exit('probe: %d matches, want 1' % len(o))
    o = o[0]
    # buf is the smalloc result hardprobe stored at 0x10(%esp)
    assert b[o - 0x63:o - 0x5f] == bytes.fromhex('89442410'), 'buf slot'
    s = o + 11
    assert len(new) == len(old) - 11
    b[s:s + len(new)] = new
    return [s]


def main():
    args = sys.argv[1:]
    strip = args[:1] == ['--strip']
    if strip:
        args = args[1:]
    src, dst = args
    b = bytearray(open(src, 'rb').read())
    if strip:
        import struct
        magic, text, data, bss, syms, entry, spsz, pcsz = struct.unpack('>8I', b[:32])
        assert magic == 0x1eb, hex(magic)       # I_MAGIC, 386
        b = b[:32 + text + data]
        struct.pack_into('>8I', b, 0, magic, text, data, bss, 0, entry, 0, 0)
    for name, f in (('ne2000', ne2000), ('ident', ident), ('probe', probe)):
        offs = f(b)
        print('%s: %s at file %s (va %s)' % (dst, name,
              ' '.join('0x%x' % o for o in offs),
              ' '.join('0x%x' % (TEXTVA + o - 0x20) for o in offs)))
    open(dst, 'wb').write(b)


if __name__ == '__main__':
    main()
