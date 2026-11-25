#!/usr/bin/env python3
"""The file-system population of the boot route (step 3l, route step B5).
OURS: SIMPOS's file system is lost (TR-524 describes it in prose), and no
disk image of a PSI is held.  What is mounted here is what a PSI-III that
had the Pseudo PIM/m installed would hold, built from the HELD psdpim
archive (docs/nonlocal/psdpim.tar.Z) and its HELD installation text:

    psdpim/INSTALL (read 2026-11-25, verbatim lines):
      copy ./PMPSI.DIR/pimm.MEkbn to >sys>csp>PMPSI.DIR on the PSI.
      copy ./FONT.DIR/* to font:(logical name on SIMPOS) on the PSI
      copy ./INSTALL.DIR/*.ptf to >sys>csp>INSTALL.DIR and ...
      copy ./INSTALL.DIR/login.com to me:(logical name on SIMPOS).
      copy ./SYSTEM.DIR/PIMM.* to >sys>csp>SYSTEM.DIR on the PSI.
      copy ./SYSTEM.DIR/*.init to me:(logical name of SIMPOS)on the PSI.

Labels of each part:
  - the placement of each file: HELD (the lines above);
  - the file contents and sizes: HELD (the archive's members; contents are
    kept only for the text files the route reads, the 16-bit JIS words of
    login.com and the two *.init files, newline 0x000a);
  - `me:` = `>sys>user>pmpsi`: INFERENCE.  The held login.com defines
    `"me" := [ "user:pmpsi" ]`, and `user:` is `>sys>user` (INFERENCE from
    TM-143 p3 and every held home directory `>sys>user>NAME`,
    docs/simpos/subsystems/shell.md §4.1);
  - `font:`: not placed.  Its directory is not named by any held line
    (OURS: the seven FONT.DIR files are left out; nothing on the route
    reads a font file);
  - the directories `>sys>csp>MPSI.DIR` and `>sys>csp>PIMOS.DIR` named by
    login.com's `define` are made empty (OURS: login.com names them; no
    held line says what they hold, and nothing on the route reads them);
  - every file's version is 1 (OURS: TR-524 PDF p9, folio 8, "The version
    ... is assigned by the file system and incremented every time a file
    is newly created"; a copy is a new file).  login.com's own first line
    gives `icpsi277::>sys>csp>INSTALL.DIR>login.com.8`, the version of the
    copy it was made from, not of the installed copy.

`population()` returns [(absolute path, size in bytes, codes or None)].
`mount(m)` makes the tree on kl0 machine M as instances of the stand-ins
simpos##directory and simpos##binary_file (psi/standin/) and stores the
root in directory's class slot `root` (the slot TR-056 PDF p22, folio 20,
names).  mount is OURS throughout; nothing here runs in the machine.
"""
import io
import os
import subprocess
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
TAR = os.path.join(HERE, '..', 'docs', 'nonlocal', 'psdpim.tar.Z')

ME = '>sys>user>pmpsi'          # INFERENCE (module docstring)
# HELD placement (psdpim/INSTALL): archive directory -> (target, selector)
PLACEMENT = [
    ('PMPSI.DIR/pimm.MEkbn', '>sys>csp>PMPSI.DIR'),
    ('INSTALL.DIR/*.ptf', '>sys>csp>INSTALL.DIR'),
    ('INSTALL.DIR/login.com', ME),
    ('SYSTEM.DIR/PIMM.*', '>sys>csp>SYSTEM.DIR'),
    ('SYSTEM.DIR/*.init', ME),
]
EMPTY_DIRS = ['>sys>csp>MPSI.DIR', '>sys>csp>PIMOS.DIR']    # OURS
TEXT = ('login.com', 'boot.init', 'usercom.init')           # contents kept


def _members():
    raw = subprocess.run(['gzip', '-dc', TAR], stdout=subprocess.PIPE, check=True).stdout
    t = tarfile.open(fileobj=io.BytesIO(raw))
    out = {}
    for mem in t.getmembers():
        if mem.isreg() and mem.name.startswith('psdpim/') and '..' not in mem.name.split('/'):
            out[mem.name[len('psdpim/'):]] = t.extractfile(mem).read()
    return out


def _match(pat, name):
    d, f = pat.rsplit('/', 1)
    nd, nf = name.rsplit('/', 1) if '/' in name else ('', name)
    if d != nd:
        return False
    if f.startswith('*'):
        return nf.endswith(f[1:])
    if f.endswith('*'):
        return nf.startswith(f[:-1])
    return nf == f


def codes_of(raw):
    """The 16-bit words of a SIMPOS text file (high byte first, MEASURED on
    login.com: 615 row-0x23 and 576 row-0x21 words, 33 words 0x000a)."""
    return [raw[i] << 8 | raw[i + 1] for i in range(0, len(raw) - 1, 2)]


_POP = None


def population():
    global _POP
    if _POP is None:
        out = []
        mem = _members()
        for name in sorted(mem):
            for pat, target in PLACEMENT:
                if _match(pat, name):
                    base = name.rsplit('/', 1)[1]
                    raw = mem[name]
                    out.append((target + '>' + base, len(raw), codes_of(raw) if base in TEXT else None))
        _POP = out
    return _POP


def text_of(codes):
    """ASCII for the JIS letters/punctuation of CODES, '\\n' for 0x000a
    (for tests and messages only)."""
    import ptfdump as P
    return ''.join('\n' if c == 0x0a else P.ch(c) for c in codes)


def mount(m):
    """Make the tree on machine M (see the module docstring).  -> root."""
    import kl0 as K
    dirs = {}

    def directory(path):
        if path in dirs:
            return dirs[path]
        d = K.make_instance(m, 'simpos##directory')
        name = path.rsplit('>', 1)[1] if path else ''
        m.set_slot(d, 'name', K.Str(name))
        m.set_slot(d, 'full_name', K.Str(path or '>'))
        m.set_slot(d, 'entries', K.NIL)
        dirs[path] = d
        if path:
            parent = directory(path.rsplit('>', 1)[0])
            m.set_slot(d, 'parent', parent)
            add(parent, name, d)
        return d

    def add(d, name, node):
        m.set_slot(d, 'entries', K.Cons(K.Vec([K.Str(name), node]), m.get_slot(d, 'entries')))

    root = directory('')
    for p in EMPTY_DIRS:
        directory(p)
    for path, size, codes in population():
        d, base = path.rsplit('>', 1)
        f = K.make_instance(m, 'simpos##binary_file')
        m.set_slot(f, 'name', K.Str(base))
        m.set_slot(f, 'version', 1)
        m.set_slot(f, 'size', size)
        m.set_slot(f, 'full_name', K.Str('%s.%d' % (path, 1)))
        if codes is not None:
            s = K.Str('')
            s.set_codes(codes)
            m.set_slot(f, 'contents', s)
        add(directory(d), base, f)
    m.set_slot(K.ClassRef('simpos##directory'), 'root', root)
    # step 3l, B7 (OURS): the alias every world sees, `user` := [">sys>user"]
    # (INFERENCE: TM-143 p3 and the held homes >sys>user>NAME, shell.md
    # §4.1), and the one registered user (standin/user.esp's head
    # comment: name INFERENCE, password and rank OURS)
    if 'simpos##world' in m.lib.templates:
        m.set_slot(K.ClassRef('simpos##world'), 'system',
                   K.Cons(K.Cons(K.Str('user'), K.Cons(K.Str('>sys>user'), K.NIL)), K.NIL))
    if 'simpos##user' in m.lib.templates:
        m.reset()
        U = K.ClassRef('simpos##user')
        for _ in m.solve_send(U, 'register', [K.Str(USER), K.Str(PASSWORD), K.Atom('general'), U]):
            break
    return root


USER, PASSWORD = 'pmpsi', 'pmpsi'   # INFERENCE (the name), OURS (the password)
