#!/usr/bin/env python3
"""Lockstep: the IPL's file decoder on whole module-information and GC areas.

    python3 ref/pimm/lockstep_gca.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_gca.py compare

ipl_file_decoder:decode_module_info/6 on modules of the real
pimm_kernel360E.sav, from the word after a module's two names up to
and including the 1000h that ends its GC area: the magic number, the
information vector, then every element of the GC area.  The argument
roles are read from the object code (asm/kl1decomp.py):

    decode_module_info(In, Rest, Result, AT0, AT, Status)

and Result is [[], Info | Elements] (the magic number is checked to be
an integer and dropped).  The test plays the reader and the atom table
as lockstep_deca.py does (its serve()).

Oracle, asm/unlsav.py's reading of the same words:
  - the information vector, in full.  It has 8 elements in every
    module, so decodeModInfo_1's guard vector(A, _) is here the size
    guard on a long vector (a descriptor), run for the first time;
  - the elements, their number and kinds in order;
  - an ordinary term is struct(Term), the term in full;
  - a module element (0900, two atoms) is module(A1) and an external
    call (0A00, two atoms, an arity, a package part) is
    extCall(A1, pred(A2/Arity)).  That shape is the object code's:
    the oracle only confirms that the atoms and the arity are the
    file's, in those places.  The second atom of a module element and
    the package part are not in the result;
  - all the words are taken, Status is normal, both streams end.

Modules: the MODULES smallest whose areas hold only these kinds, one
with an empty GC area, and the largest GC area in the file (shoen).

New here: put_atom.

Observed fault injections into the Bluespec, 2026-11-20, each FAILed
where shown and was restored:
  put_atom gives an integer          module 0: R 0 = 00:0000000c for 02:0000000c
  write_nil does not advance         module 0: the next cell written one low
  write_nil writes integer 0         module 0: M = 00:00000000 for 02:00000000
  long vector: info gives size + 1   module 0: R 0 = 9 for 8
  the guard vector fails on a long   module 0: the next clause is taken
    vector

Not caught: put_atom writing the register named by bits 23-16 instead
of the opcode's low five bits.  Every put_atom run here is put_atom 0
with an atom below 10000h, so both are register 0.
"""
import io
import os
import struct
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import unlsav  # noqa: E402
import lockstep_deca as deca  # noqa: E402

PINNED = dict(parts=7, lines=108136, elements=39)
MODULES = 5


def plain(p):
    """A term lockstep_deca.shown can show, of any size."""
    if p[0] in ('int', 'atom'):
        return True
    if p[0] == 'string':
        return p[2] in (8, 16)
    return p[0] in ('vector', 'list') and len(p[1]) >= 1 and all(plain(e) for e in p[1])


def areas(fname='pimm_kernel360E.sav'):
    """(module name, words, atoms known before, the top-level terms)
    for every module of the kernel file, in file order."""
    raw = subprocess.run(['gzip', '-dc', deca.OBJ], stdout=subprocess.PIPE, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
        for m in tf.getmembers():
            if m.name.endswith('/' + fname):
                data = tf.extractfile(m).read()
    words = list(struct.unpack('>%dH' % (len(data) // 2), data))
    r = unlsav.Reader(words)
    magic, nmod, _sep = r.rd(), r.rd(), r.rd()
    if magic in (0x5702, 0x5802):
        r.i += 2 + ((words[r.i] << 16) | words[r.i + 1])
    out, depth, inner, tops = [], [0], unlsav.parse_term, []

    def outer(rd):
        i, before = rd.i, dict(rd.atoms)
        depth[0] += 1
        try:
            p = inner(rd)
        finally:
            depth[0] -= 1
        if depth[0] == 0:
            tops.append((i, rd.i, before, p))
        return p
    unlsav.parse_term = outer
    try:
        for _ in range(nmod):
            del tops[:]
            mod = unlsav.parse_module(r)
            a, b = tops[0][0], tops[-1][1] + 1
            assert words[b - 1] == 0x1000
            out.append((mod[1][0][1], words[a:b], tops[0][2], [t[3] for t in tops]))
    finally:
        unlsav.parse_term = inner
    return out


def chosen():
    ok = [a for a in areas()
          if a[3][0][0] == 'int' and plain(a[3][1])
          and all(p[0] in ('module', 'extcall') or plain(p) for p in a[3][2:])]
    by = sorted(ok, key=lambda a: len(a[1]))
    some = [a for a in by if len(a[3]) > 2][:MODULES]
    return [by[0]] + some + [by[-1]]


def atom(a, known):
    return '#%x' % deca.number(a[0], known.get(a[0], a[1]))


def expected(terms, names):
    """The Result as pimm.Machine.term shows it."""
    out = [[], deca.shown(terms[1])]
    for p in terms[2:]:
        if p[0] == 'module':
            out.append(('module', atom(p[1], names)))
        elif p[0] == 'extcall':
            out.append(('extCall', atom(p[1], names),
                        ('pred', ('/', atom(p[2], names), p[3]))))
        else:
            out.append(('struct', deca.shown(p)))
    return out


def script():
    im = pimm.kbndis.Image()
    s = driver.Script()
    pc = pimm.predicate(im, 'ipl_file_decoder', 'decode_module_info/6')
    names = {name: n for n, name in im.sym.items()}
    want, elements = [], 0
    for n, (name, words, before, terms) in enumerate(chosen()):
        label = 'module %d: %s, %d words, %d elements' % (n, name, len(words), len(terms) - 2)
        s.label(label)
        for i in (0, 1, 2, 3, 4, 7):
            s.newvar(i)
        s.arg(1, 0)
        s.arg(2, 1)
        s.arg(3, 2)
        s.arg(4, 7)
        s.arg(5, 3)
        s.arg(6, 4)
        s.spawn(pc, 6)
        s.live()
        table = {k: deca.number(k, v) for k, v in before.items()}
        at, atq, feed = deca.serve(s, s.live_slot[0], s.live_slot[7], list(words), table,
                                   names, [])
        assert not feed, (label, len(feed))
        s.setslot(5, at)
        s.setslot(6, atq)
        for i in (1, 2, 3, 4, 5, 6):
            s.out(i)
        want.append((label, expected(terms, {})))
        elements += len(terms) - 2
    s.elements = elements
    return s, want


def check(s, m, want):
    got = {}
    for label, w in s.outs:
        got.setdefault(label, []).append(w)
    bad = []
    for label, exp in want:
        unlfs, obj, at, status, tail, atail = got[label][-6:]
        if m.term(obj) != exp:
            bad.append((label, m.term(obj), exp))
        if not (m.unbound(tail) and unlfs == tail and m.unbound(atail) and at == atail):
            bad.append((label, 'streams left'))
        if m.term(status) != 'normal':
            bad.append((label, m.term(status)))
    return bad


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    pinned = dict(PINNED)
    elements = pinned.pop('elements')
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep gca', pinned)
    if not ok:
        return 1
    bad = check(s, m, want)
    if bad or s.elements != elements:
        print('pimm lockstep gca: FAIL, %d elements (pinned %d); answers differ: %s'
              % (s.elements, elements, repr(bad[:1])[:600]))
        return 1
    print('pimm lockstep gca: PASS (the IPL file decoder on the module information and '
          'whole GC areas of %d modules of the real pimm_kernel360E.sav on the Bluespec '
          'core: %d GC elements, %d trace lines identical to the reference model; every '
          'result as asm/unlsav.py reads the same words)'
          % (s.counts['parts'], s.elements, s.counts['lines']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
