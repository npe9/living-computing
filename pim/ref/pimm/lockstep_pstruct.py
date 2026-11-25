#!/usr/bin/env python3
"""Lockstep: the guard X = Y (wait_value) on nested structures, lists,
long vectors and strings: the general passive unification.

    python3 ref/pimm/lockstep_pstruct.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_pstruct.py compare
    python3 ref/pimm/lockstep_pstruct.py --reference       the reference alone

The site that needs it: compiling the primer's sample1 (lockstep_shell.py
APPS compile_sample1) stopped on both models at wait_value on two
vectors whose elements are vectors: pimos::keyed_bag if_empty/4
(utility/pool/k_bag.kl1:155, `if_empty({Key,Data,Next},Key,YorN,E)`)
comparing the compiler's head-position keys, {car, {arg, 1}} against
{variable(N), 7} and the like (library/compiler/index.kl1:787
new_register(car(Pos), CarReg)).  The models compared atomic elements
only, and refused the rest.

The meaning is VPIM's (functions/f_reduce_passive_unify.psl.c
f_EqualStruct and f_Equal_Sub; structures/str_passive_unify.psl.c, the
unify stack; docs/pimm_semantics.md wait_value): depth first, with an
explicit stack of frames (crp, size, X's and Y's first element).  Each
pair of elements is dereferenced: an unbound X is noted and the guard
fails there, then an unbound Y; types that differ are not equal;
integers, atoms, modules and codes by tag and value; strings by
descriptor and words; the null vector is equal; a list or a vector (a
long one after its size) pushes the frame in hand, even one at its
end, so a list's cdr takes a frame.  The stack holds 512 frames
(_LOCAL_MEM_UNIFY_STACK_AREA_SIZE 0x800 words, basics/bsc_mem_map.psl.c
:90, a frame of 4 words); a 513th is refused on both models (VPIM
suspends there, with a DEBUG warning and no variable to wake the goal).

The goal is OURS, seven cells in the heap (lockstep_alt.py's way):
    p(X, Y, R) :- X = Y | R = 1.
    otherwise.
    p(_, _, R) :- true | R = 0.
try_me_else @4; wait_value 0, 1; get_integer 2, 1; proceed; otherwise
3, @0; get_integer 2, 0; proceed.  R is 1 when X = Y succeeds, 0 when
it fails; when an unbound element is met first the goal suspends on it
(otherwise), and the part binds it and runs again.  The parts (PARTS
below, R as worked by hand from the rule above):
  {a, {b, 1}} = {a, {b, 1}}             1  the compiler's key, nested
  {a, {b, 1}} = {a, {b, 2}}             0  differing two levels down
  {a, {b, 1}} = {a, {c, 1}}             0  ... in the inner vector's first
  {a, {b, 1}} = {a, b}                  0  a vector against an atom
  {a, {b, 1}} = {a, {b, 1, 2}}          0  inner vectors of two sizes
  [1, 2, 3] = [1, 2, 3]                 1  lists, the cdr a frame each
  [1, 2, 3] = [1, 2]                    0  the shorter ends: [] against [3]
  [1, 2, 3] = [1, 2 | 3]                0  a list against an integer
  {[1, {2}], x} = {[1, {2}], x}         1  a list in a vector in a list
  {[1, {2}], x} = {[1, {3}], x}         0
  {"abc"} = {"abc"}                     1  a string element
  {"abc"} = {"abd"}                     0
  {"abc"} = {abc}                       0  a string against an atom
  {7 of 1..7} = {7 of 1..7}             1  long vectors
  {7 of 1..7} = {1..6, 8}               0  the last element
  {7 of 1..7} = {8 of 1..8}             0  long vectors of two sizes
  {{7 of 1..7}} = {{7 of 1..7}}         1  a long vector as an element
  {} = {}, {{}} = {{}}                  1  the null vector, an element
  {a} = {n}                             0  an atom and the integer of its number
  {C, 1} = {C, 1}                       1  C a code ({COD, the goal's first cell})
  {C} = {C'}                            0  two codes
  {C} = {M}                             0  a code and a module of one value
                                           (COD 26h, MOD 27h: not the MRB bit)
  {{1}, 2} = {{1}, 3}                   0  differing after a pop
  {{1}, V} = {{1}, 2}                   waits on V after a pop; V = 2: 1
  {V, 2} = {1, 3}                       waits on V (X's element first,
                                           though element 1 differs);
                                           V = 1: 0
  {1, 2} = {1, W}                       waits on W; W = 2: 1
  {[V | T]} = {[1, 2]}                  waits on V; V = 1: waits on T;
                                           T = [2]: 1
  a list of 513 cells = itself          1  512 frames, the stack full
  a list of 514 cells = itself          refused on both models
The refused part has no OUT: the reference's Unimplemented ends its
play (refusing() makes it the core's `E unimp` line), and the bench
has no operation left after that RUN.

Observed fault injections into the Bluespec (bsv/PimmPBox.bsv), each
built and run alone from a copy, 2026-11-25 (the first difference of
each; the trace lines are the goal's I lines, 32768.. its seven cells):
  the end of the frame in hand taken     after a pop, line 33: I 32770
    as the end (no pop)                  (R = 1) for I 32772 (otherwise)
  the modules' and codes' branch         codes, line 29: E unimp for
    removed                              I 32770
  a module and a code compared by        a code and a module, line 25:
    tag less the low bit and value       I 32770 for I 32772
  an unbound Y taken as not equal        Y waits, line 30: I 32773
                                         (R = 0) for M 33311 (the
                                         suspension)
  a frame at its end not pushed          the refusal, line 2077: I 32770
                                         for E unimp (514 cells pass)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402

PINNED = dict(parts=35, lines=5515)
I = lambda v: (pimm.INT, v & 0xffffffff)           # noqa: E731
KLB = 0x23
X, Y, R = 12, 13, 14
CODE = [(KLB, 0x68 << 24 | 2),                     # try_me_else @4
        (KLB, 0xa4 << 24 | 0 << 16 | 1 << 8),      # wait_value 0, 1
        (KLB, 0xb9 << 24 | 2 << 16 | 1),           # get_integer 2, 1
        (KLB, 0x60 << 24),                         # proceed
        (KLB, 0x6a << 24 | 3 << 16 | 0xfffa),      # otherwise 3, @0
        (KLB, 0xb9 << 24 | 2 << 16 | 0),           # get_integer 2, 0
        (KLB, 0x60 << 24)]                         # proceed
NAMES = ['try_me_else', 'wait_value', 'get_integer', 'proceed', 'otherwise',
         'get_integer', 'proceed']

# Terms: an int; ('a', name) an atom; 'nil'; a tuple, a vector; ('list',
# [items], tail); ('str', [codes]) an 8-bit string; ('long', [ints]);
# ('var', k) the unbound variable in slot k (9, 10 or 11)
A = lambda n: ('a', n)                             # noqa: E731
L = lambda *xs, tail='nil': ('list', list(xs), tail)   # noqa: E731
S = lambda t: ('str', [ord(ch) for ch in t])       # noqa: E731
LONG = lambda xs: ('long', list(xs))               # noqa: E731
V = lambda k: ('var', k)                           # noqa: E731
KEY = (A('normal'), (A('abnormal'), 1))
NEST = (L(1, (2,)), A('normal'))

# (label, X, Y, [(variable slot, value) bound after a run, in order],
#  R as worked by hand)
PARTS = [
    ('key', KEY, KEY, [], 1),
    ('key, two down', KEY, (A('normal'), (A('abnormal'), 2)), [], 0),
    ('key, the inner first', KEY, (A('normal'), (A('normal'), 1)), [], 0),
    ('key and an atom', KEY, (A('normal'), A('abnormal')), [], 0),
    ('key, inner sizes', KEY, (A('normal'), (A('abnormal'), 1, 2)), [], 0),
    ('lists', L(1, 2, 3), L(1, 2, 3), [], 1),
    ('lists, shorter', L(1, 2, 3), L(1, 2), [], 0),
    ('lists, an integer tail', L(1, 2, 3), L(1, 2, tail=3), [], 0),
    ('nested', NEST, NEST, [], 1),
    ('nested, differing', NEST, (L(1, (3,)), A('normal')), [], 0),
    ('strings', (S('abc'),), (S('abc'),), [], 1),
    ('strings, differing', (S('abc'),), (S('abd'),), [], 0),
    ('a string and an atom', (S('abc'),), (A('normal'),), [], 0),
    ('long', LONG(range(1, 8)), LONG(range(1, 8)), [], 1),
    ('long, the last', LONG(range(1, 8)), LONG([1, 2, 3, 4, 5, 6, 8]), [], 0),
    ('long, sizes', LONG(range(1, 8)), LONG(range(1, 9)), [], 0),
    ('long in a vector', (LONG(range(1, 8)),), (LONG(range(1, 8)),), [], 1),
    ('null', ((), ()), ((), ()), [], 1),
    ('an atom and its number', (A('normal'),), (('number', 'normal'),), [], 0),
    ('codes', (('cod', 0), 1), (('cod', 0), 1), [], 1),
    ('codes, two', (('cod', 0),), (('cod', 2),), [], 0),
    ('a code and a module', (('cod', 0),), (('mod', 0),), [], 0),
    ('after a pop', ((1,), 2), ((1,), 3), [], 0),
    ('after a pop, waits', ((1,), V(9)), ((1,), 2), [(9, 2)], 1),
    ('X waits', (V(9), 2), (1, 3), [(9, 1)], 0),
    ('Y waits', (1, 2), (1, V(10)), [(10, 2)], 1),
    ('a list waits', (L(V(9), tail=V(10)),), (L(1, 2),), [(9, 1), (10, L(2))], 1),
    ('513 cells', 'long list 513', 'same', [], 1),
]
REFUSED = ('514 cells', 'long list 514')


class Builder:
    def __init__(b, s, atoms):
        b.s = s
        b.atoms = atoms

    def const(b, t):
        if isinstance(t, int):
            return I(t)
        if t == 'nil':
            return (pimm.ATOM, 0)
        if t == ():
            return (pimm.VECT0, 0)
        if isinstance(t, tuple) and t[0] == 'a':
            return (pimm.ATOM, b.atoms[t[1]])
        if isinstance(t, tuple) and t[0] == 'number':
            return I(b.atoms[t[1]])
        if isinstance(t, tuple) and t[0] in ('cod', 'mod'):
            return (pimm.COD if t[0] == 'cod' else pimm.MOD, b.code + t[1])
        return None

    def elem(b, t, lo):
        """A vector or list element: a constant cell, or ('slot', k)
        with t built in slot k from slots lo.. (k = lo)."""
        c = b.const(t)
        if c is not None:
            return c, lo
        if t[0] == 'var':
            return ('slot', t[1]), lo
        b.build(t, lo, lo + 1)
        return ('slot', lo), lo + 1

    def build(b, t, into, lo):
        """Slot `into` := t, slots lo.. its scratch (below 9)."""
        s = b.s
        c = b.const(t)
        if c is not None:
            s.setslot(into, c)
        elif t[0] == 'str':
            s.string(into, 8, t[1])
        elif t[0] == 'list':
            b.list(t[1], t[2], into, lo)
        elif t[0] == 'long':
            b.long(t[1], into, lo)
        else:
            elems, k = [], lo
            for e in t:
                c, k = b.elem(e, k)
                elems.append(c)
            assert k + len(t) <= 9, t
            s.vector(into, k, elems)

    def list(b, items, tail, into, lo):
        s = b.s
        h = [lo, lo + 1]
        cdr, k = b.elem(tail, lo + 2)
        for e in reversed(items):
            car, k2 = b.elem(e, k)
            assert k2 + 2 <= 9
            s.cons(h[1], k2, car, cdr)
            cdr = ('slot', h[1])
            h.reverse()
        s._op(driver.PTR, into, cdr[1], (pimm.LIST + 1, 0))

    def long(b, xs, into, lo):
        s = b.s
        n = len(xs)
        assert lo + 3 + n <= 12
        for k in range(lo, lo + 3 + n):
            s.newvar(k)
        m = s.live()
        a0 = s.live_slot[lo][1]
        assert [s.live_slot[k][1] for k in range(lo, lo + 3 + n)] == list(range(a0, a0 + 3 + n))
        s.unifyc(lo, (pimm.VDESC, a0 + 3))
        s.unifyc(lo + 1, I(n))
        s.unifyc(lo + 2, I(n))
        for i, v in enumerate(xs):
            s.unifyc(lo + 3 + i, I(v))
        s._op(driver.PTR, into, lo, (pimm.VECT0 + 15, 0))
        del m


def long_list(s, n, into):
    """Slot `into` := [1, 2, .., n], built from the tail in slots 0..3."""
    h = [0, 1]
    cdr = (pimm.ATOM, 0)
    for v in range(n, 0, -1):
        s.cons(h[1], 2, I(v), cdr)
        cdr = ('slot', h[1])
        h.reverse()
    s._op(driver.PTR, into, cdr[1], (pimm.LIST + 1, 0))


def script():
    im = pimm.kbndis.Image()
    atoms = {name: n for n, name in im.sym.items()}
    s = driver.Script()
    s.label('the goal')
    for k in range(len(CODE)):
        s.newvar(k)
    m = s.live()
    a0 = s.live_slot[0][1]
    assert [s.live_slot[k][1] for k in range(len(CODE))] == list(range(a0, a0 + len(CODE)))
    for k, c in enumerate(CODE):
        s.unifyc(k, c)
    m = s.live()
    at = a0 - m.load
    assert [m.opname(at + i) for i in range(len(CODE))] == NAMES
    b = Builder(s, atoms)
    b.code = a0
    want = []
    for label, x, y, binds, r in PARTS + [REFUSED + ('same', [], None)]:
        s.label(label)
        for k in (9, 10, 11):
            s.newvar(k)
        if isinstance(x, str):
            long_list(s, int(x.split()[-1]), X)
        else:
            b.build(x, X, 0)
        if y == 'same':
            s._op(driver.PTR, Y, X, (pimm.LIST + 1, 0))
        else:
            b.build(y, Y, 0)
        s.newvar(R)
        s.arg(1, X)
        s.arg(2, Y)
        s.arg(3, R)
        s.spawn(at, 3)
        s.run()
        for k, v in binds:
            s.label('%s: slot %d bound' % (label, k))
            if isinstance(v, int):
                s.unifyc(k, I(v))
            else:
                b.build(v, 0, 1)
                s.unify(k, 0)
            s.run()
        if r is not None:
            s.out(R)
        want.append((label, r))
    del m
    return s, want


def check(s, m, want):
    bad = []
    got = [w for _label, w in s.outs]
    for (label, r), w in zip(want, got):
        d = m.deref(w)
        t = None if m.unbound(d) else m.term(d)
        if t != r:
            bad.append((label, t, r))
    if len(got) != len(want) - 1:
        bad.append(('answers', len(got), len(want) - 1))
    if getattr(s, 'refused', None) != 'wait_value: the unify stack full (512 frames)':
        bad.append(('refusal', getattr(s, 'refused', None)))
    return bad


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    orig = s.play
    s.play = lambda: refusing(s, orig)
    if '--reference' in argv:
        n = sum(len(v) for _k, v in s.play())
        bad = check(s, s.machine, want)
        print(bad, n)
        return 1 if bad else 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep pstruct', PINNED)
    if not ok:
        return 1
    bad = check(s, m, want)
    if bad:
        print('pimm lockstep pstruct: FAIL %r' % (bad[:3],))
        return 1
    print('pimm lockstep pstruct: PASS (wait_value on nested vectors, lists, long vectors '
          'and strings on the Bluespec core, %d parts, %d trace lines identical to the '
          'reference model: %d answers as worked by hand, four goals that waited on an '
          'element and went on when it was bound, 512 frames passed and the 513th refused '
          'on both)' % (s.counts['parts'], s.counts['lines'], len(want) - 1))
    return 0


def refusing(s, orig):
    """s.play(), its last part refused: the reference's Unimplemented
    is the core's `E unimp` line, the part's trace up to there kept."""
    gen = orig()
    while True:
        try:
            item = next(gen)
        except StopIteration:
            return
        except pimm.Unimplemented as e:
            s.refused = str(e)
            yield 'the refusal', s.machine.tr + ['E unimp']
            return
        yield item


if __name__ == '__main__':
    sys.exit(main(sys.argv))
