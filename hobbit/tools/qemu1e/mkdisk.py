#!/usr/bin/env python3
"""Make a raw IDE disk image for a 1e PC, sized in whole QEMU cylinders.

1e's devhard.c addresses the disk by CHS from IDENTIFY words 1/3/6
(`hardident`, devhard.c:663-666) and takes its size as C*H*S*512.  QEMU
reports, for a disk without an MBR, 16 heads, 63 sectors and
size/(16*63*512) cylinders (the guess in hw/block/hd-geometry.c), so the
image is made a whole number of 16*63-sector cylinders and that is the
size 1e sees (checked: a 64 MiB image appears as #w/hd0disk of
67092480 bytes = 130*16*63*512).

With --fs, the last sector of that size gets the Plan 9 partition table
in the format `disk/prep` writes (sys/src/cmd/disk/prep.c write_table:
"plan9 partitions\\n" then "%s %d %d\\n" name start end) and `hardpart`
reads (devhard.c:824-890, the sector at cap/512-1): one partition `fs`
covering the disk below the table.  That is the only thing written; the
file system itself is made in the guest by 1e's `disk/kfs -r`.

With --data FILE, the image holds FILE from sector 0 (an archive for
mkext) and is padded to whole cylinders, plus one.

usage: mkdisk.py OUT (--fs MBYTES | --data FILE)
"""
import os
import sys

CYL = 16 * 63 * 512


def main():
    out, kind, arg = sys.argv[1:4]
    if kind == '--fs':
        size = int(arg) * 1024 * 1024 // CYL * CYL
        nsec = size // 512
        with open(out, 'wb') as f:
            f.truncate(size)
            tab = b'plan9 partitions\nfs 0 %d\n' % (nsec - 1)
            f.seek((nsec - 1) * 512)
            f.write(tab + bytes(512 - len(tab)))
        print('%s: %d bytes, %d cylinders, partition fs 0..%d' %
              (out, size, size // CYL, nsec - 1))
    elif kind == '--data':
        n = os.path.getsize(arg)
        size = (n + CYL - 1) // CYL * CYL + CYL
        with open(arg, 'rb') as src, open(out, 'wb') as f:
            while True:
                b = src.read(1 << 20)
                if not b:
                    break
                f.write(b)
            f.truncate(size)
        print('%s: %d bytes of data, image %d bytes' % (out, n, size))
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
