#!/usr/bin/env python3
"""Lockstep: exception_table:replace_position/3 from the IPL image.

    python3 ref/pimm/lockstep_rpos.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_rpos.py compare

The first predicate with switch_on_constant.  Source
(kernel/builtin/excpt_tbl.kl1; the image's version lacks Dn and DnN):

    replace_position(merge,              2,P,Dn,DnN) :- true | P=1, DnN=Dn.
    replace_position(new_vector,         1,P,Dn,DnN) :- true | P=2, DnN=Dn.
    ...
    replace_position(floating_point_add, N,P,Dn,DnN) :- true | P := N-1, DnN=Dn.
    ...
    otherwise.
    replace_position(_,                  N,P,Dn,DnN) :- true | P=N, DnN=Dn.

The image hashes on the name (12 atoms), then for six of them runs a
switch_on_constant on N.  The source held is a later one: it also has
29 more `P := N-1` clauses (27 of them extended_floating_point_*), whose atoms the image's symbol
table does not have, so they cannot be asked and are not tested.

The oracle is the clauses parsed from the source text (commented-out
lines excluded), restricted to names the image knows.

Observed fault injections into the Bluespec, 2026-11-20, each FAILed
where shown and was restored:
  a match takes the else field           new_instruction 1: the otherwise clause
  no match takes the offset field        new_instruction 0: a clause for the else
  only the first pair compared           new_instruction 2: the otherwise clause
  an unbound key is not noted            new_instruction, position late: no suspension
  the key compared without its tag       an atom numbered as a key: a clause taken
  pairs stepped by one cell              new_instruction 3: the otherwise clause
  labels relative to the pair's first    new_instruction 0: a table cell fetched
    cell

Not caught, and not catchable on this image: an unbound key compared as
a value instead of going straight to the else label.  The reference
cell matches no key and every pair carries the same else label, so the
two behaviours end at the same place; which pair's else field the
machine uses is not observable here.
"""
import io
import os
import re
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import driver  # noqa: E402
import pimm  # noqa: E402

TAR = os.path.join(HERE, '..', '..', 'docs', 'nonlocal', 'pimos.tar.Z')
PINNED = dict(parts=61, lines=1744)


def oracle():
    raw = subprocess.run(['gzip', '-dc', TAR], stdout=subprocess.PIPE, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
        for m in tf.getmembers():
            if m.name.endswith('src/kernel/builtin/excpt_tbl.kl1'):
                text = tf.extractfile(m).read().decode('latin1')
    fixed = re.findall(r'^replace_position\((\w+),\s*(\d+),P,Dn,DnN\) :- true \| '
                       r'P=(\d+), DnN=Dn\.', text, re.M)
    minus = re.findall(r'^replace_position\((\w+),\s*N,P,Dn,DnN\) :- true \| '
                       r'P := N-1, DnN=Dn\.', text, re.M)
    last = re.search(r'^otherwise\.\s*\nreplace_position\(_,\s*N,P,Dn,DnN\) :- true \| '
                     r'P=N, DnN=Dn\.', text, re.M)
    every = re.findall(r'^replace_position\(', text, re.M)
    assert last and len(fixed) + len(minus) + 1 == len(every), (len(fixed), len(minus), len(every))
    table = {(name, int(n)): int(p) for name, n, p in fixed}
    assert len(table) == len(fixed) == 11 and len(set(minus)) == len(minus) == 35

    def f(name, n):
        if (name, n) in table:
            return table[(name, n)]
        if name in minus and isinstance(n, int):
            return n - 1
        return n
    return f, sorted({name for name, _n in table}), minus


def script():
    im = pimm.kbndis.Image()
    number = {name: n for n, name in im.sym.items()}
    s = driver.Script()
    pc = pimm.predicate(im, 'exception_table', 'replace_position/3')
    _f, switched, minus = oracle()
    known = [m for m in minus if m in number]
    assert len(switched) == 6 and len(known) == 6, (switched, known)
    want = []            # (label, name or integer, n)

    def cell(v):
        return (pimm.ATOM, number[v]) if isinstance(v, str) else (pimm.INT, v & 0xffffffff)

    def goal(label, name, n, late=None):
        # slots: 0 P, 1 a late variable
        s.label(label)
        s.newvar(0)
        for i, v in ((1, name), (2, n)):
            if late == i:
                s.newvar(1)
                s.arg(i, 1)
            else:
                s.argc(i, cell(v))
        s.arg(3, 0)
        s.spawn(pc, 3)
        s.run()
        if late:
            s.out(0)
            s.unifyc(1, cell(name if late == 1 else n))
            s.run()
        s.out(0)
        want.append((label, name, n))

    for name in switched:
        for n in range(0, 6):
            goal('%s %d' % (name, n), name, n)
    for name in known:
        for n in (1, 3):
            goal('%s %d' % (name, n), name, n)
    goal('floating_point_add 0', 'floating_point_add', 0)
    goal('another atom', 'normal', 2)
    goal('an integer for the name', 7, 2)
    goal('an atom for the position', 'merge', 'normal')
    goal('a large position', 'new_string', 65538)
    # atom number 2 where the integer 2 is a key; the integer 90 where
    # atom number 90 (merge) is a hash key
    goal('an atom numbered as a key', 'new_module', 'decode')
    goal('an integer numbered as a name', number['merge'], 2)
    goal('a negative position', 'merge', -1)
    goal('merge, name late', 'merge', 2, late=1)
    goal('merge, position late', 'merge', 2, late=2)
    goal('new_instruction, position late, no match', 'new_instruction', 4, late=2)
    goal('floating_point_divide, position late', 'floating_point_divide', 3, late=2)
    goal('another atom, position late', 'normal', 3, late=2)
    return s, want


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep rpos', PINNED)
    if not ok:
        return 1
    f, _switched, _minus = oracle()
    last = {}
    for label, w in s.outs:
        last[label] = w
    bad = []
    for label, name, n in want:
        got = m.term(last[label])
        if got != f(name, n):
            bad.append((label, got, f(name, n)))
    if bad:
        print('pimm lockstep rpos: FAIL, answers differ from the source: %r' % bad[:3])
        return 1
    print('pimm lockstep rpos: PASS (exception_table:replace_position/3 from the IPL '
          'image on the Bluespec core: %d goals, %d trace lines identical to the '
          'reference model; every position the one the source gives, e.g. %r for '
          'new_instruction 3)' % (s.counts['parts'], s.counts['lines'],
                                  m.term(last['new_instruction 3'])))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
