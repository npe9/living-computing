#!/usr/bin/env python3
"""Write a tree as a 1e `disk/mkfs -a` archive.

The archive is what 1e's own `disk/mkext` unpacks (sys/src/cmd/disk/mkext.c):
for each file a header line, formatted as mkfs's `arch()` does
(sys/src/cmd/disk/mkfs.c:395-399)

    Bprint(&bout, "%s %luo %s %s %d\\n", newfile, d->mode, d->uid, d->gid, d->length);

followed by exactly `length` bytes of data for a plain file and nothing
for a directory (mode has CHDIR, 0x80000000), parents before children,
and the terminator `end of archive\\n` (mkfs.c:169).  mkext reads it from
standard input with Brdline and stops at the terminator, so trailing
bytes (the rest of a raw disk) are ignored.

The source is either the release tarball itself (SRC ending in .tar.bz2,
members under its top directory `plan9-1e/`) or a host directory.  Use
the tarball: the release has names that differ only in case
(sys/src/cda/lde and sys/src/cda/LDE, devpost/Hb and hb, ...), and an
extraction onto a case-insensitive host file system silently keeps one
of each pair (33 colliding names, 35 tarball entries lost).

As mkfs does without a proto file (mkfs.c:262-266), owner and group are
"sys"; the mode is the owner bits copied to group and other.  The header
has no time field, so mkext dates every file at unpacking.  Names may not
contain blanks (mkext splits the header with getfields) and must fit
NAMELEN-1 = 27 bytes; offenders are refused.  The trees under the
top-level names given are written first, in that order (one pass over
the source each), then everything else in source order.

--overlay DIR adds, after the tree, every path under DIR that the tree
does not have (qemu1e's service files, tools/qemu1e/overlay).
--list FILE writes "path length" (length -1 for a directory) for every
entry, for p9probe.py --walk to compare against.

The output is padded to a whole number of 512-byte sectors, so it can be
attached as a raw IDE disk and read by `disk/mkext < /dev/hd1disk`.

usage: mkarchive.py SRC OUT [--overlay DIR] [--list FILE] [top-level-name ...]
"""
import os
import stat
import sys
import tarfile

CHDIR = 0x80000000


def perm(mode, isdir):
    own = (mode >> 6) & 7
    m = (own << 6) | (own << 3) | own
    return m | (CHDIR if isdir else 0)


def tar_entries(path):
    """(rel, isdir, mode, reader) in tarball order, rel = '/a/b'."""
    t = tarfile.open(path, 'r:bz2')
    for m in t:
        name = m.name.rstrip('/')
        top, _, rest = name.partition('/')
        if not rest:
            continue
        if m.isdir():
            yield '/' + rest, True, m.mode, None
        elif m.isreg():
            yield '/' + rest, False, m.mode, (lambda m=m: t.extractfile(m).read())
        else:
            sys.exit('%s: not a file or directory' % m.name)


def dir_entries(src):
    for dirpath, dirs, files in os.walk(src):
        dirs.sort()
        files.sort()
        for n in dirs + files:
            full = os.path.join(dirpath, n)
            st = os.lstat(full)
            rel = '/' + os.path.relpath(full, src)
            if stat.S_ISDIR(st.st_mode):
                yield rel, True, st.st_mode, None
            elif stat.S_ISREG(st.st_mode):
                yield rel, False, st.st_mode, (lambda full=full: open(full, 'rb').read())


def main():
    args = sys.argv[1:]
    src, out = args[0], args[1]
    args = args[2:]
    overlay = listfile = None
    while args[:1] in (['--overlay'], ['--list']):
        if args[0] == '--overlay':
            overlay = args[1]
        else:
            listfile = args[1]
        args = args[2:]
    tops = args
    seen = set()
    nfile = ndir = nbytes = 0
    listing = []
    with open(out, 'wb') as f:
        def emit(rel, isdir, mode, reader):
            nonlocal nfile, ndir, nbytes
            for c in rel.split('/')[1:]:
                if ' ' in c or '\t' in c or len(c.encode()) > 27:
                    sys.exit('unrepresentable name: %r' % rel)
            parent = rel.rsplit('/', 1)[0]
            if parent and parent not in seen:
                sys.exit('%s before its directory' % rel)
            if rel in seen:
                sys.exit('%s twice' % rel)
            seen.add(rel)
            if isdir:
                f.write(('%s %o sys sys 0\n' % (rel, perm(mode, True))).encode())
                ndir += 1
                listing.append('%s -1' % rel)
                return
            data = reader()
            f.write(('%s %o sys sys %d\n' % (rel, perm(mode, False), len(data))).encode())
            f.write(data)
            nfile += 1
            nbytes += len(data)
            listing.append('%s %d' % (rel, len(data)))

        # the source's order is parents first.  Two passes: the named
        # top-level trees, then everything else.
        def source():
            return tar_entries(src) if src.endswith('.tar.bz2') else dir_entries(src)
        for t in tops:
            for e in source():
                if e[0].split('/')[1] == t:
                    emit(*e)
        for e in source():
            if e[0].split('/')[1] not in tops:
                emit(*e)
        if overlay:
            for rel, isdir, mode, reader in dir_entries(overlay):
                if rel not in seen:
                    emit(rel, isdir, mode, reader)
                    print('overlay: %s' % rel)
        f.write(b'end of archive\n')
        n = f.tell()
        f.write(bytes((-n) % 512 + 512))
    if listfile:
        open(listfile, 'w').write('\n'.join(listing) + '\n')
    print('%s: %d dirs, %d files, %d data bytes' % (out, ndir, nfile, nbytes))


if __name__ == '__main__':
    main()
