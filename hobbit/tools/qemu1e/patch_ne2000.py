#!/usr/bin/env python3
"""Patch a 1e 386 kernel's NE2000 probe so it finds QEMU's ne2k_isa.

sys/src/9/pc/ether2000.c `reset` reads the station-address PROM with
16-bit remote DMA into `ushort buf[16]` and accepts a board only if

        buf[0x0E] == 0x57 && buf[0x0F] == 0x57

-- it expects each PROM byte in the low half of a word, high half 0 ("We
asked for shorts, we got shorts, although the PROM is a byte array").
QEMU's NE2000 duplicates every PROM byte into both halves
(hw/net/ne2000.c `ne2000_reset`), so the words read are 0x5757 and the
probe rejects the card: observed with `-trace ne2000_*` (data-port reads
0x5252 0x5454 0x0000 0x1212 0x3434 0x5656 ... 0x5757 0x5757) and the
kernel's "#l: no free devices".

8c compiled each test as

        0f b7 44 24 XX      movzwl XX(%esp),%eax
        83 f8 57            cmp    $0x57,%eax

This script changes the two `movzwl` (0f b7) to `movzbl` (0f b6), so the
tests read the low byte only -- the byte the source means.  The station
address (`ctlr->ea[i] = buf[i]`) already takes the low byte.  Exactly one
match is required; the file is otherwise untouched.

usage: patch_ne2000.py in-kernel out-kernel
"""
import re
import sys

PAT = re.compile(rb'\x0f\xb7\x44\x24(.)\x83\xf8\x57\x75.'
                 rb'\x0f\xb7\x44\x24(.)\x83\xf8\x57\x74.', re.S)


def main():
    src, dst = sys.argv[1:3]
    b = bytearray(open(src, 'rb').read())
    m = list(PAT.finditer(b))
    if len(m) != 1:
        sys.exit('%s: %d matches of the NE2000 PROM test, want 1' % (src, len(m)))
    o = m[0].start()
    assert b[o + 1] == 0xb7 and b[o + 11] == 0xb7
    b[o + 1] = 0xb6
    b[o + 11] = 0xb6
    open(dst, 'wb').write(b)
    va = 0x80001020 + o - 0x20     # 386 a.out: 32-byte header, text at 0x80001020
    print('%s: patched movzwl->movzbl at file 0x%x and 0x%x (va 0x%x, 0x%x)'
          % (dst, o + 1, o + 11, va, va + 10))


if __name__ == '__main__':
    main()
