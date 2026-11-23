#!/usr/bin/env python3
"""Write a host directory tree as a 1e `disk/mkfs -a` archive.

The archive is what 1e's own `disk/mkext` unpacks (sys/src/cmd/disk/mkext.c):
for each file a header line, formatted as mkfs's `arch()` does
(sys/src/cmd/disk/mkfs.c:395-399)

    Bprint(&bout, "%s %luo %s %s %d\\n", newfile, d->mode, d->uid, d->gid, d->length);

followed by exactly `length` bytes of data for a plain file and nothing
for a directory (mode has CHDIR, 0x80000000), parents before children,
and the terminator `end of archive\\n` (mkfs.c:169).  mkext reads it from
standard input with Brdline and stops at the terminator, so trailing
bytes (the rest of a raw disk) are ignored.

As mkfs does without a proto file (mkfs.c:262-266), owner and group are
"sys"; the mode is the owner bits of the host file copied to group and
other.  Names may not contain blanks (mkext splits the header with
getfields) and must fit NAMELEN-1 = 27 bytes; offenders are refused.

The output is padded to a whole number of 512-byte sectors, so it can be
attached as a raw IDE disk and read by `disk/mkext < '#w/hd1disk'`.

--overlay DIR adds, after the tree, every path under DIR that SRCDIR
does not have (qemu1e's service files, tools/qemu1e/overlay).

usage: mkarchive.py SRCDIR OUT [--overlay DIR] [top-level-name ...]
"""
import os
import stat
import sys

CHDIR = 0x80000000


def mode_of(st):
    own = (st.st_mode >> 6) & 7
    m = (own << 6) | (own << 3) | own
    if stat.S_ISDIR(st.st_mode):
        m |= CHDIR
    return m


def main():
    src, out = sys.argv[1], sys.argv[2]
    tops = sys.argv[3:]
    overlay = None
    if tops[:1] == ['--overlay']:
        overlay, tops = tops[1], tops[2:]
    nfile = ndir = nbytes = 0
    with open(out, 'wb') as f:
        def emit(rel, st, base=src):
            nonlocal nfile, ndir, nbytes
            for c in rel.split('/')[1:]:
                if ' ' in c or '\t' in c or len(c.encode()) > 27:
                    sys.exit('unrepresentable name: %r' % rel)
            if stat.S_ISDIR(st.st_mode):
                f.write(('%s %o sys sys 0\n' % (rel, mode_of(st))).encode())
                ndir += 1
                return
            data = open(os.path.join(base, rel.lstrip('/')), 'rb').read()
            f.write(('%s %o sys sys %d\n' % (rel, mode_of(st), len(data))).encode())
            f.write(data)
            nfile += 1
            nbytes += len(data)

        names = tops or sorted(os.listdir(src))
        for top in names:
            p = os.path.join(src, top)
            st = os.lstat(p)
            emit('/' + top, st)
            if not stat.S_ISDIR(st.st_mode):
                continue
            for dirpath, dirs, files in os.walk(p):
                dirs.sort()
                files.sort()
                for d in dirs:
                    full = os.path.join(dirpath, d)
                    emit('/' + os.path.relpath(full, src), os.lstat(full))
                for fn in files:
                    full = os.path.join(dirpath, fn)
                    st = os.lstat(full)
                    if stat.S_ISREG(st.st_mode):
                        emit('/' + os.path.relpath(full, src), st)
        if overlay:
            for dirpath, dirs, files in os.walk(overlay):
                dirs.sort()
                files.sort()
                for n in dirs + files:
                    full = os.path.join(dirpath, n)
                    rel = '/' + os.path.relpath(full, overlay)
                    if not os.path.lexists(os.path.join(src, rel.lstrip('/'))):
                        emit(rel, os.lstat(full), overlay)
                        print('overlay: %s' % rel)
        f.write(b'end of archive\n')
        n = f.tell()
        f.write(bytes((-n) % 512 + 512))
    print('%s: %d dirs, %d files, %d data bytes' % (out, ndir, nfile, nbytes))


if __name__ == '__main__':
    main()
