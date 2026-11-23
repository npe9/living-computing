#!/usr/bin/env python3
"""Lockstep: shoen:ground_term/2 from the IPL image.

    python3 ref/pimm/lockstep_ground.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_ground.py compare

The first predicate that reads and builds lists, and the first run of
several goals at once.  Source (kernel/builtin/shoen.kl1):

    ground_term(Term, N_term) :- true |
        ground_term(Term, [], Term1, Wait),
        wait_and_unify(Wait, Term1, N_term).

    ground_term(Term, Data, N_term, Data1) :- vector(Term, L) |
        new_vector(Term1, L),
        wait_vector(L, Term, Term1, Data, N_term, Data1).
    ground_term([H|T], Data, N_term, Data1) :- true |
        N_term = [H1|T1],
        ground_term(H, Data, H1, Data2),
        ground_term(T, Data2, T1, Data1).
    otherwise.
    ground_term(Term, Data, N_term, Data1) :-true | % wait(Term) |
        N_term = Term, Data1 = Data.

    wait_and_unify(Wait, Term, Term1) :- wait(Wait) |
        Term1 = Term.

    wait_vector(0, Vec, Vec1, Data, N_vec, Data1) :- true |
        N_vec = Vec1, Data1 = Data.
    otherwise.
    wait_vector(L, Vec, Vec1, Data, N_vec, Data1) :-
            L1 := L-1,
            vector_element(Vec, L1, D) |
        ground_term(D, Data, D1, Data2),
        set_vector_element(Vec1, L1, _, D1, Vec2),
        wait_vector(L1, Vec, Vec2, Data2, N_vec, Data1).

So N_term is a copy of Term, given only when every leaf of Term is
bound: an unbound leaf makes the first two clauses wait, and a clause
after `otherwise` is not taken while an earlier one waits.  That is the
oracle: the clauses are asserted to be in the source as written here;
the answer must be unbound while any leaf is, and equal to the term
when none is.  Terms here are lists, vectors of up to 6 elements and
atomic values.

New here: switch_on_non_list, switch_on_non_vector, put_nil,
put_reused_structure and read_variable on a list cell, write_variable
with its register used afterwards; for vectors the guards vector and
vector_element, mark_element (nothing: no MRB), and the body built-ins
new_vector and set_vector_element.

Observed fault injections into the Bluespec, 2026-11-20, each FAILed
where shown and was restored:
  switch_on_non_list does not note         an element bound late: one hook, not two
  switch_on_non_list leaves the pointer    [1]: the car read
  switch_on_non_vector's label from the    an integer: the next instruction
    first cell
  switch_on_non_vector does not note       an element bound late: one hook, not two
  put_nil puts integer 0                   an integer: R 1
  write_variable's register one cell on    (caught first by lockstep_asf)
  switch_on_non_list takes a vector        {1,2}: the list clause entered
  switch_on_non_vector gives size + 1      {1,2}: R 4
  guard vector gives size - 1              {1,2}: R 0
  set_vector_element waits for the new     {1,2}: a goal record where the
    element                                  copy should be
  vector box: an unbound element taken     a vector element bound late: R 0
    as its cell, not a reference
  vector box replaces the wrong element    {1,2}: the cell written
  new_vector fills with 1                  {1,2}: M .. 1 for 0
  set_vector_element's outputs swapped     {1,2}: R 2
NOT caught, both because the predicate never asks: vector_element
accepting an index equal to the size (wait_vector counts down from
size - 1), and set_vector_element's copy duplicating an unbound cell
(it only copies vectors new_vector made, whose cells are 0 or already
replaced).  Also not exercised: either built-in waiting for an input.
"""
import io
import os
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import driver  # noqa: E402
import pimm  # noqa: E402

TAR = os.path.join(HERE, '..', '..', 'docs', 'nonlocal', 'pimos.tar.Z')
PINNED = dict(parts=20, lines=5467)

CLAUSES = __doc__[__doc__.index('    ground_term(Term, N_term)'):__doc__.index('So N_term')]


class Vec(list):
    """A vector term (a Python list is a KL1 list)."""


class Late:
    """A leaf unbound when the goal starts, bound to `value` later."""
    def __init__(self, value):
        self.value = value


# name, term, the order in which its Late leaves are bound
def cases():
    a, b = Late(7), Late([8, 9])
    c, d = Late(1), Late('normal')
    return [
        ('an integer', 5, []),
        ('an atom', 'normal', []),
        ('nil', [], []),
        ('[1]', [1], []),
        ('[1,2,3]', [1, 2, 3], []),
        ('[[1,2],[normal]]', [[1, 2], ['normal']], []),
        ('[1|2]', ('|', 1, 2), []),
        ('an element bound late', [1, a, 3], [a]),
        ('the tail bound late', ('|', 1, b), [b]),
        ('two leaves, first then second', [c, d], [c, d]),
        ('two leaves, second then first', [c, d], [d, c]),
        ('the whole term bound late', Late([1, 2]), None),
        ('{1,2}', Vec([1, 2]), []),
        ('{normal}', Vec(['normal']), []),
        ('{1,[2,3],{4}}', Vec([1, [2, 3], Vec([4])]), []),
        ('[{1,2,3,4,5,6}]', [Vec([1, 2, 3, 4, 5, 6])], []),
        ('a vector element bound late', Vec([1, a, 3]), [a]),
        ('two vector elements, last then first', Vec([c, 2, d]), [d, c]),
        ('two vector elements, first then last', Vec([c, 2, d]), [c, d]),
        ('a vector bound late', Late(Vec([1, 2])), None),
    ]


def value(t):
    """The term with every Late leaf replaced by its value."""
    if isinstance(t, Late):
        return value(t.value)
    if isinstance(t, Vec):
        return tuple(value(e) for e in t)
    if isinstance(t, list):
        return [value(e) for e in t]
    if isinstance(t, tuple):
        car, cdr = value(t[1]), value(t[2])
        return [car] + cdr if isinstance(cdr, list) else ('|', car, cdr)
    return t


def check_source():
    raw = subprocess.run(['gzip', '-dc', TAR], stdout=subprocess.PIPE, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
        for m in tf.getmembers():
            if m.name.endswith('src/kernel/builtin/shoen.kl1'):
                text = tf.extractfile(m).read().decode('latin1')
    assert ' '.join(CLAUSES.split()) in ' '.join(text.split()), \
        'the clauses are not in the source as transcribed'


def script():
    im = pimm.kbndis.Image()
    number = {name: n for n, name in im.sym.items()}
    s = driver.Script()
    pc = pimm.predicate(im, 'shoen', 'ground_term/2')
    want = []                 # (label, [expected term or None per OUT])

    def build(t, free, late):
        """An element for Script.cons: a cell, None, or ('slot', n).
        List cells take three slots each from free[0] on: the pointer,
        the car, the cdr.  late[id(leaf)] = the slot of its variable."""
        if isinstance(t, Late):
            return None
        if isinstance(t, int):
            return (pimm.INT, t & 0xffffffff)
        if isinstance(t, str):
            return (pimm.ATOM, number[t])
        if isinstance(t, Vec):
            # the pointer in slot p, its cells in slots p+1 ..
            p, n = free[0], len(t)
            free[0] += n + 1
            assert free[0] <= 16
            es = [build(e, free, late) for e in t]
            for i, leaf in enumerate(t):
                if isinstance(leaf, Late):
                    late[id(leaf)] = p + 1 + i
            for i in range(n):
                s.newvar(p + 1 + i)
            s._op(driver.PTR, p, p + 1, (pimm.VECT0 + 2 * n + 1, 0))
            for i, e in enumerate(es):
                if e is None:
                    continue
                if e[0] == 'slot':
                    s.unify(p + 1 + i, e[1])
                else:
                    s.unifyc(p + 1 + i, e)
            return ('slot', p)
        if t == []:
            return pimm.NIL
        car, cdr = (t[1], t[2]) if isinstance(t, tuple) else (t[0], t[1:])
        p = free[0]
        free[0] += 3
        assert free[0] <= 16
        ecar, ecdr = build(car, free, late), build(cdr, free, late)
        for leaf, slot in ((car, p + 1), (cdr, p + 2)):
            if isinstance(leaf, Late):
                late[id(leaf)] = slot
        # the pointer goes in slot p, its cells are slots p+1 and p+2
        s.newvar(p + 1)
        s.newvar(p + 2)
        s._op(driver.PTR, p, p + 1, (pimm.LIST + 1, 0))
        for slot, e in ((p + 1, ecar), (p + 2, ecdr)):
            if e is None:
                continue
            if e[0] == 'slot':
                s.unify(slot, e[1])
            else:
                s.unifyc(slot, e)
        return ('slot', p)

    for label, term, order in cases():
        s.label(label)
        expect = []
        free, late = [1], {}
        s.newvar(0)                           # N_term
        if order is None:                     # the whole term is a variable
            s.newvar(15)
            s.arg(1, 15)
        else:
            e = build(term, free, late)
            if e[0] == 'slot':
                s.arg(1, e[1])
            else:
                s.argc(1, e)
        s.arg(2, 0)
        s.spawn(pc, 2)
        s.run()
        s.out(0)
        if order is None:
            expect.append(None)
            free = [1]
            e = build(term.value, free, late)
            s.unify(15, e[1])
            s.run()
            s.out(0)
            expect.append(value(term))
        else:
            expect.append(None if order else value(term))
            for i, leaf in enumerate(order):
                free = [10]                   # a late list value is built apart
                e = build(leaf.value, free, {})
                if e[0] == 'slot':
                    s.unify(late[id(leaf)], e[1])
                else:
                    s.unifyc(late[id(leaf)], e)
                s.run()
                s.out(0)
                expect.append(value(term) if i == len(order) - 1 else None)
        want.append((label, expect))
    return s, want


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep ground', PINNED)
    if not ok:
        return 1
    check_source()
    # The answer as it stood at each OUT: the word printed is a
    # reference while the answer is unbound and the term's own word
    # after, and a term once given does not change.
    seen = {}
    for label, w in s.outs:
        seen.setdefault(label, []).append(None if w[0] & ~1 == pimm.REF else m.term(w))
    bad = [(label, seen[label], expect) for label, expect in want if seen[label] != expect]
    if bad:
        print('pimm lockstep ground: FAIL, answers differ from the source: %r' % bad[:3])
        return 1
    print('pimm lockstep ground: PASS (shoen:ground_term/2 from the IPL image on the '
          'Bluespec core, lists and vectors: %d terms, %d trace lines identical to the reference '
          'model; each answer unbound while a leaf is and the term after, e.g. %r)'
          % (s.counts['parts'], s.counts['lines'], seen['{1,[2,3],{4}}'][-1]))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
