#!/usr/bin/env python3
"""Where the held package template files (.ptf) and their ESP source are,
and a read-only, data-only extraction of them into a scratch directory.

OURS (tooling).  The locations are from `docs/binary_reverse_engineering.md`
§4 (psdpim, pimosobj) and `docs/archive_search_notes.md` "Task 4" (the IFS
kappa2 and utter archives).  Nothing from an archive is executed: members
are read with `gzip -dc` + tarfile and written as plain files, after
refusing absolute paths, `..` components and anything that is not a
regular file.

    python3 -I psi/held.py extract DIR      extract into DIR (must be new or empty)
    python3 -I psi/held.py check DIR        list what DIR holds against the table

The extraction layout (relative to DIR):
    ptf/<pkg>.ptf                      the eleven package template files
    src/paragraph/*.esp                pimos.tar.Z src_util/paragraph (83 files)
    src/kappa2/...                     kappa2.tar.Z, every regular file
    src/utter/...                      utter.tar.Z, every regular file
"""
import io
import os
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
NONLOCAL = os.path.normpath(os.path.join(HERE, '..', 'docs', 'nonlocal'))
IFS = os.path.join(NONLOCAL, 'ifs')

# package -> (archive relative to docs/nonlocal, member path)
PTF = {
    'pimfep': ('psdpim.tar.Z', 'psdpim/INSTALL.DIR/pimfep.ptf'),
    'pimscsi': ('psdpim.tar.Z', 'psdpim/INSTALL.DIR/pimscsi.ptf'),
    'pimmcsp': ('psdpim.tar.Z', 'psdpim/INSTALL.DIR/pimmcsp.ptf'),
    'pimmutil': ('psdpim.tar.Z', 'psdpim/INSTALL.DIR/pimmutil.ptf'),
    'mpsicspR': ('psdpim.tar.Z', 'psdpim/INSTALL.DIR/mpsicspR.ptf'),
    'paragraph': ('pimosobj.tar.Z', 'object/paragraph.ptf'),
    'kappa': ('ifs/kbms-clp/simpos/kappa2.tar.Z', 'kappa2/ptf/kappa.ptf'),
    'fts': ('ifs/natural-lang/simpos/utter.tar.Z', 'PTF/fts.ptf'),
    'qxt': ('ifs/natural-lang/simpos/utter.tar.Z', 'PTF/qxt.ptf'),
    'sancho2': ('ifs/natural-lang/simpos/utter.tar.Z', 'PTF/sancho2.ptf'),
    'tour': ('ifs/natural-lang/simpos/utter.tar.Z', 'PTF/tour.ptf'),
}
# source trees: name -> (archive, member prefix, keep-suffixes or None = all)
SRC = {
    'paragraph': ('pimos.tar.Z', 'pimos/src_util/paragraph/', ('.esp',)),
    'kappa2': ('ifs/kbms-clp/simpos/kappa2.tar.Z', '', None),
    'utter': ('ifs/natural-lang/simpos/utter.tar.Z', '', None),
}


def _tar(archive):
    raw = subprocess.run(['gzip', '-dc', os.path.join(NONLOCAL, archive)],
                         stdout=subprocess.PIPE, check=True).stdout
    return tarfile.open(fileobj=io.BytesIO(raw))


def _safe(name):
    parts = [p for p in name.split('/') if p not in ('', '.')]
    if name.startswith('/') or '..' in parts or not parts:
        return None
    return os.path.join(*parts)


def extract(dest):
    if os.path.exists(dest) and os.listdir(dest):
        raise SystemExit('held: %s is not empty; extract into a new directory' % dest)
    os.makedirs(dest, exist_ok=True)
    cache = {}
    n = 0
    for pkg, (arch, mem) in PTF.items():
        tf = cache.setdefault(arch, _tar(arch))
        m = tf.getmember(mem)
        assert m.isreg(), mem
        os.makedirs(os.path.join(dest, 'ptf'), exist_ok=True)
        with open(os.path.join(dest, 'ptf', pkg + '.ptf'), 'wb') as f:
            f.write(tf.extractfile(m).read())
        n += 1
    for name, (arch, prefix, keep) in SRC.items():
        tf = cache.setdefault(arch, _tar(arch))
        for m in tf.getmembers():
            if not m.isreg() or not m.name.startswith(prefix):
                continue
            if keep and not m.name.endswith(keep):
                continue
            rel = _safe(m.name[len(prefix):])
            if rel is None:
                print('held: refused member %r' % m.name)
                continue
            out = os.path.join(dest, 'src', name, rel)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, 'wb') as f:
                f.write(tf.extractfile(m).read())
            n += 1
    print('held: %d files extracted into %s' % (n, dest))


def ptf_path(root, pkg):
    return os.path.join(root, 'ptf', pkg + '.ptf')


_TARS = {}


def _cached(archive):
    if archive not in _TARS:
        _TARS[archive] = _tar(archive)
    return _TARS[archive]


def ptf_bytes(pkg, root=None):
    """The bytes of package PKG's .ptf: from an extraction ROOT if given,
    else straight from the archive in memory (nothing written)."""
    if root:
        with open(ptf_path(root, pkg), 'rb') as f:
            return f.read()
    arch, mem = PTF[pkg]
    return _cached(arch).extractfile(mem).read()


def src_files(name, root=None, suffixes=None):
    """{relpath: bytes} of source tree NAME (see SRC), from ROOT or in memory."""
    out = {}
    if root:
        base = os.path.join(root, 'src', name)
        for dp, _dn, fn in os.walk(base):
            for f in fn:
                p = os.path.join(dp, f)
                rel = os.path.relpath(p, base)
                if suffixes and not rel.lower().endswith(suffixes):
                    continue
                with open(p, 'rb') as fh:
                    out[rel] = fh.read()
        return out
    arch, prefix, keep = SRC[name]
    tf = _cached(arch)
    for m in tf.getmembers():
        if not m.isreg() or not m.name.startswith(prefix):
            continue
        if keep and not m.name.endswith(keep):
            continue
        rel = _safe(m.name[len(prefix):])
        if rel is None or (suffixes and not rel.lower().endswith(suffixes)):
            continue
        out[rel] = tf.extractfile(m).read()
    return out


# window M10 (2026-11-26): single held IFS sources the Pmacs tests compile
# (psi/test_espc.py Window.test_win_m10_*), read in memory, never written:
# name -> (archive under docs/nonlocal, member, member of an inner tar or
# None).  The archives are ICOT IFS releases in git (docs/nonlocal/
# IFS_MANIFEST.md rows for disc, cal-esp and papyrus).
MEMBERS = {
    'exshow': ('ifs/natural-lang/simpos/disc.tar.Z', 'exshow.esp', None),
    'cal_pmacs': ('ifs/kbms-clp/simpos/cal-esp.tar.Z', 'cal2.12/cal_pmacs.esp', None),
    'dedit': ('ifs/kbms-clp/simpos/cal-esp.tar.Z', 'deb2.12/dedit.esp', None),
    'my_select': ('ifs/solver-prover/simpos/papyrus.tar.Z', 'source.tar', './demo/EDITOR/my_select.esp.1'),
    # the Pmacs reconstruction (2026-11-27, docs/simpos/subsystems/pmacs.md
    # §6): papyrus editors that send the reconstructed selectors
    'my_syntax': ('ifs/solver-prover/simpos/papyrus.tar.Z', 'source.tar', './demo/EDITOR/my_syntax.esp.1'),
    'my_delete': ('ifs/solver-prover/simpos/papyrus.tar.Z', 'source.tar', './demo/EDITOR/my_delete.esp.1'),
    'my_point': ('ifs/solver-prover/simpos/papyrus.tar.Z', 'source.tar', './demo/EDITOR/my_point.esp.1'),
}


def member_text(name):
    """The source text of MEMBERS[NAME], decoded byte for byte (latin-1:
    the comments' JIS escapes are kept as they are; the code is ASCII)."""
    arch, mem, inner = MEMBERS[name]
    raw = _cached(arch).extractfile(mem).read()
    if inner is not None:
        raw = tarfile.open(fileobj=io.BytesIO(raw)).extractfile(inner).read()
    return raw.decode('latin-1')


def present(root):
    """The packages whose .ptf is in ROOT."""
    return [p for p in PTF if root and os.path.exists(ptf_path(root, p))]


def main(argv):
    if len(argv) == 2 and argv[0] == 'extract':
        extract(argv[1])
        return 0
    if len(argv) == 2 and argv[0] == 'check':
        have = present(argv[1])
        print('held: %d of %d packages present: %s' % (len(have), len(PTF), ' '.join(have)))
        return 0 if len(have) == len(PTF) else 1
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
