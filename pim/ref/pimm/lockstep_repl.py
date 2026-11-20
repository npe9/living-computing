#!/usr/bin/env python3
"""Lockstep: exception_table:replace_argument/3 from the IPL image.

    python3 ref/pimm/lockstep_repl.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_repl.py compare

The first predicate that reads structures.  Source
(kernel/builtin/excpt_tbl.kl1), which has two more arguments than the
image's version, Dn and DnN, passed through unchanged:

    replace_argument(merge,          {A,B},  ArgV,Dn,DnN) :- true | ArgV={B,A}, DnN=Dn.
    replace_argument(new_vector,     {A,B},  ArgV,Dn,DnN) :- true | ArgV={B,A}, DnN=Dn.
    replace_argument(new_string,     {A,B,C},ArgV,Dn,DnN) :- true | ArgV={C,A,B}, DnN=Dn.
    replace_argument(new_instruction,{A,B,C},ArgV,Dn,DnN) :- true | ArgV={C,A,B}, DnN=Dn.
    replace_argument(new_module,     {A,B},  ArgV,Dn,DnN) :- true | ArgV={B,A}, DnN=Dn.
    replace_argument(set_vector_element,
                                 {A,B,C,D,E},ArgV,Dn,DnN) :- true | ArgV={A,B,D,C,E}, DnN=Dn.
    otherwise.
    replace_argument(_,               V,     ArgV,Dn,DnN) :- true | ArgV=V, DnN=Dn.

New here: wait_vector_N (N = 2, 3, 5), read_variable,
put_reused_structure, and hash_on_constant on atoms.

The oracle is those clauses parsed from the source text (the name, the
pattern's variables, the answer's variables; Dn and DnN dropped), so
the expected answer is the permutation the source gives.  Vectors are
built by the script (driver.Script.vector) and the answer is read back
out of memory.

Observed fault injections into the Bluespec, 2026-11-20, each FAILed
where shown and was restored:
  wait_vector accepts any vector size      merge with 3 elements: the clause taken
  wait_vector leaves the structure pointer merge, 2 elements: the element read
  wait_vector does not note the variable   vector bound late: no suspension
  read_variable does not advance           merge, 2 elements: R 3
  read_variable copies an unbound element  first element unbound: R 0 = 08.. for a reference
  put_reused_structure one cell short      the next part's first variable
  put_reused_structure tags from r[y] as   vector bound late: R 1 = 06.. for 17..
    held, not dereferenced
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
PINNED = dict(parts=14, lines=600)


def oracle():
    raw = subprocess.run(['gzip', '-dc', TAR], stdout=subprocess.PIPE, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
        for m in tf.getmembers():
            if m.name.endswith('src/kernel/builtin/excpt_tbl.kl1'):
                text = tf.extractfile(m).read().decode('latin1')
    rules = re.findall(r'^replace_argument\((\w+),\s*\{([\w,]+)\},\s*ArgV,Dn,DnN\) :- true \| '
                       r'ArgV=\{([\w,]+)\}, DnN=Dn\.', text, re.M)
    table = {name: (pat.split(','), ans.split(',')) for name, pat, ans in rules}
    assert len(rules) == len(table) == 6, rules
    last = re.search(r'^otherwise\.\s*\nreplace_argument\(_,\s*V,\s*ArgV,Dn,DnN\) :- true \| '
                     r'ArgV=V, DnN=Dn\.', text, re.M)
    assert last and last.start() > text.index('replace_argument(set_vector_element')

    def f(name, v):
        if name in table and isinstance(v, tuple) and len(v) == len(table[name][0]):
            env = dict(zip(table[name][0], v))
            return tuple(env[x] for x in table[name][1])
        return v
    return f, table


def script():
    im = pimm.kbndis.Image()
    number = {name: n for n, name in im.sym.items()}
    s = driver.Script()
    pc = pimm.predicate(im, 'exception_table', 'replace_argument/3')
    _f, table = oracle()
    want = []            # (label, name or integer, elements or None)

    def atom(name):
        return (pimm.ATOM, number[name])

    def elems(n, base):
        # integers, an atom, and (from the third on) nothing special
        out = [(pimm.INT, base + i) for i in range(n)]
        out[-1] = atom('normal')
        return out

    def show(e):
        return im.atom(e[1]) if e[0] == pimm.ATOM else pimm.signed(e[1])

    def goal(label, name, es, late=None):
        # slots: 0 the vector, 1 ArgV, 2 a late variable, 4.. the elements
        s.label(label)
        s.vector(0, 4, es)
        s.newvar(1)
        first = atom(name) if isinstance(name, str) else (pimm.INT, name)
        if late == 'name':
            s.newvar(2)
            s.arg(1, 2)
        else:
            s.argc(1, first)
        if late == 'vector':
            s.newvar(2)
            s.arg(2, 2)
        else:
            s.arg(2, 0)
        s.arg(3, 1)
        s.spawn(pc, 3)
        s.run()
        if late == 'name':
            s.out(1)
            s.unifyc(2, first)
            s.run()
        if late == 'vector':
            s.out(1)
            s.unify(2, 0)
            s.run()
        s.out(1)
        want.append((label, name, tuple(None if e is None else show(e) for e in es)))

    for i, (name, (pat, _ans)) in enumerate(sorted(table.items())):
        goal('%s, %d elements' % (name, len(pat)), name, elems(len(pat), 10 * (i + 1)))
    goal('merge with 3 elements', 'merge', elems(3, 70))
    goal('new_string with 2 elements', 'new_string', elems(2, 80))
    goal('set_vector_element with 3 elements', 'set_vector_element', elems(3, 90))
    goal('another atom', 'normal', elems(2, 100))
    goal('an integer', 5, elems(3, 110))
    goal('merge, name bound late', 'merge', elems(2, 120), late='name')
    goal('new_string, vector bound late', 'new_string', elems(3, 130), late='vector')
    # an element that is an unbound variable is carried over as that
    # variable: bound afterwards, it shows in the answer
    s.label('merge, first element unbound')
    es = [None, (pimm.INT, 141)]
    s.vector(0, 4, es)
    s.newvar(1)
    s.argc(1, atom('merge'))
    s.arg(2, 0)
    s.arg(3, 1)
    s.spawn(pc, 3)
    s.run()
    s.out(1)
    s.unifyc(4, (pimm.INT, 140))
    s.out(4)
    want.append(('merge, first element unbound', 'merge', (140, 141)))
    return s, want


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep repl', PINNED)
    if not ok:
        return 1
    f, _table = oracle()
    last = {}
    for label, w in s.outs:
        last.setdefault(label, w)        # the answer is the first OUT of slot 1 ...
    for label, w in s.outs:
        if label != 'merge, first element unbound':
            last[label] = w              # ... or the last, when it was bound late
    bad = []
    for label, name, es in want:
        expect = f(name, es)
        got = m.term(last[label])
        if got != expect:
            bad.append((label, got, expect))
    if bad:
        print('pimm lockstep repl: FAIL, answers differ from the source: %r' % bad[:3])
        return 1
    print('pimm lockstep repl: PASS (exception_table:replace_argument/3 from the IPL '
          'image on the Bluespec core: %d goals, %d trace lines identical to the '
          'reference model; every answer the vector the source gives, e.g. %r for '
          'set_vector_element)' % (s.counts['parts'], s.counts['lines'],
                                   m.term(last['set_vector_element, 5 elements'])))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
