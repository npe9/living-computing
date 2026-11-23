#!/usr/bin/env python3
"""Make the 1e distribution boot floppy bootable without DOS.

The release's floppy image `sys/lib/pcdisk` is a FAT12 1.44 MB disk whose
boot sector (written by `disk/format -b`, sys/src/cmd/disk/format.c
`bootprog`) loads the file in the *first* root-directory slot, if that file
is `PLAN9   SYS`, to 0x0800:0000 and jumps there (bootprog bytes
0xd7..0xe1 compare the slot with "PLAN9   SYS"; 0x11a..0x14d load 128
sectors at 0x0800:0000 and `ljmp $0x800,$0`).  `format.c` puts
/386/b.com there when given `-b` (`dosfile(fd, "/386/b.com", "PLAN9",
"SYS")`), but the shipped image was made without it: its first slot is
`B.COM`, and it has no PLAN9.SYS, so as shipped it boots only from DOS
(`C> a:b.com`, sys/doc/pcconfig.ms step 21).

b.com is a DOS .COM: its first instructions (sys/src/boot/pc/l.s) copy
DS:0000..FFFF to 0x80000 and jump to 0x8000:lowcore, with lowcore linked
at 0x8008011d -- i.e. they assume the image sits at DS:0100, after a
256-byte PSP.  The boot sector leaves it at DS:0000.  So PLAN9.SYS here
is b.com behind a 256-byte prefix that starts `jmp 0x100` (e9 fd 00):
the prefix stands in for the PSP, and b.com runs exactly as DOS would
run it.  This is the one substitution in the boot path; it is documented
in docs/qemu_1e_server.md.

If a fourth argument is given, that file replaces ::9DOS (the kernel
b.com loads by default, `fd!0!9dos`): used for the NE2000-patched kernel
(patch_ne2000.py).  The floppy has no room for a second kernel.

usage: mkfloppy.py pcdisk b.com out.img [9dos]
"""
import os
import shutil
import struct
import subprocess
import sys


def main():
    pcdisk, bcom, out = sys.argv[1:4]
    shutil.copyfile(pcdisk, out)
    os.chmod(out, 0o644)
    if len(sys.argv) > 4:
        subprocess.check_call(['mcopy', '-i', out, '-o', '-m', sys.argv[4], '::9DOS'])
    b = open(bcom, 'rb').read()
    sysfile = bytes([0xe9, 0xfd, 0x00]) + bytes(253) + b
    assert len(sysfile) <= 128 * 512, 'boot sector loads 128 sectors'
    tmp = out + '.plan9sys'
    open(tmp, 'wb').write(sysfile)
    subprocess.check_call(['mcopy', '-i', out, '-o', tmp, '::PLAN9.SYS'])
    subprocess.check_call(['mattrib', '-i', out, '+r', '+h', '+s', '::PLAN9.SYS'])
    os.unlink(tmp)

    img = bytearray(open(out, 'rb').read())
    bps, spc, nres, nfat, nroot = struct.unpack_from('<HBHBH', img, 11)
    fatsz = struct.unpack_from('<H', img, 22)[0]
    root = (nres + nfat * fatsz) * bps
    ents = [img[root + 32 * i: root + 32 * i + 32] for i in range(nroot)]
    idx = [i for i, e in enumerate(ents) if bytes(e[:11]) == b'PLAN9   SYS']
    assert len(idx) == 1, idx
    i = idx[0]
    e0, ei = bytes(ents[0]), bytes(ents[i])
    img[root:root + 32] = ei
    img[root + 32 * i: root + 32 * i + 32] = e0
    # the boot sector reads 128 consecutive sectors from the start cluster:
    # the file must be contiguous.
    fat = img[nres * bps: (nres + fatsz) * bps]

    def nxt(c):
        v = struct.unpack_from('<H', fat, c * 3 // 2)[0]
        return v >> 4 if c & 1 else v & 0xfff
    c = struct.unpack_from('<H', ei, 26)[0]
    first = c
    n = 1
    while True:
        v = nxt(c)
        if v >= 0xff8:
            break
        assert v == c + 1, 'PLAN9.SYS not contiguous'
        c = v
        n += 1
    open(out, 'wb').write(img)
    print('%s: PLAN9.SYS %d bytes, clusters %d..%d, root slot 0 (was %d)'
          % (out, len(sysfile), first, c, i))


if __name__ == '__main__':
    main()
