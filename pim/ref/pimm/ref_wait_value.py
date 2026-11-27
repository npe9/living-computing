#!/usr/bin/env python3
"""The reference models alone, one PE (pimm.py) and the multi-PE model
(pimm_pe.py, a System of one PE): the guard X = Y (wait_value) on the
words that are neither atomic, a string, a list nor a vector (a module,
a code, a shoen's handle), and the body built-in get_heap_size.

    python3 ref/pimm/ref_wait_value.py      ends `ref wait value: PASS ...`

The site: the IFS sweep's largest first stop, `wait_value on a
structure` (docs/ifs_apps.md 4, five rows: ldlib, dulcinea, consort,
desq, kappa_p), where both models refused X = Y unless both words were
atomic, strings, lists or vectors.  And `get_heap_size at N`
(h907_nseq), which only pimm_pe.py had.

The meaning is VPIM's klb_equal (interpreter/klb_compare.psl.c 91-97):
an atomic X is compared with Y by tag and value, so an atomic X and a Y
that is not are not equal; any other X goes to f_EqualStruct
(functions/f_reduce_passive_unify.psl.c 45-105): two types that differ
are not equal, and SHREC, MOD and COD are equal when tag and value are
(whole tags: from 20h the low bit is not an MRB, so MOD 27h and COD 26h
differ).  Any other type is VPIM's DEBUG "Illegal type": refused, on
both models.  get_heap_size(^Size, ^Used) as pimm.py i_get_heap_size
(VPIM klb_pimos.psl.c kblt_b_get_heap_size: Size one half of the
copying collector's heap; the values OURS).

The goal is lockstep_pstruct.py's, seven cells in the heap:
    p(X, Y, R) :- X = Y | R = 1.
    otherwise.
    p(_, _, R) :- true | R = 0.
R is 1 when X = Y succeeds, 0 when it fails; a goal that waits on an
unbound X or Y suspends, and the part binds it and runs again.  The
words: C is the goal's first cell; M, K, H are {MOD, C}, {COD, C},
{SHREC, C}.  The parts (R worked by hand from the rule above):
  M = M                          1   modules
  M = {MOD, C+1}                 0   two modules
  K = K                          1   codes
  K = {COD, C+2}                 0   two codes
  K = M                          0   a code and a module of one value
  H = H                          1   shoen handles
  H = {SHREC, C+1}               0   two handles
  H = M                          0   a handle and a module, one value
  M = {ATOM, C}                  0   a module and an atom, one value
  {INT, C} = K                   0   an integer X (VPIM's atomic path)
  M = "abc"                      0   a module and a string
  "abc" = K                      0   a string and a code
  M = [1]                        0   a module and a list (the passive
                                     unification's)
  M = V, V = M                   waits on V; bound: 1
  V = K, V = {COD, C+2}          waits on V; bound: 0
  {EXFLT, 0} twice               refused on both: `wait_value on a 3f
                                     word` (no source compares it)
Then, its own goal (lockstep_prio.py's shape): get_heap_size 2, 3;
get_value 2, 0; get_value 3, 1; proceed.  Size must be (MEMORY_CELLS -
HEAP) // 2, Used more than 0 and less than Size, the same on both
models, and the multi-PE model's heap_log must hold that answer.

Observed fault injections (each into a private copy of pimm.py, this
script run on it, 2026-11-27; the failures listed are all of them, the
same on pimm and pimm_pe, which takes pimm.Machine's instruction):
  the old refusal (`wait_value       no answers, the run refused at the
    on a structure`)                 first part (8 lines: answers 0 of
                                     17 and the refusal, each model)
  MOD, COD, SHREC compared by tag    a code and a module: 1 for 0
    less the low bit and value       (2 lines)
  by tag alone (any value equal)     two modules, two codes, a code and
                                     a module, two handles, a handle and
                                     a module, X waits (bound to the
                                     other code): 1 for 0 (12 lines)
  SHREC not compared by value        refused at `handles`, `wait_value
                                     on a 38 word`: answers 5 of 17 and
                                     the refusal (4 lines)
  two types taken as equal           a module and an atom, an integer
                                     and a code, a module and a string,
                                     a string and a code: 1 for 0 (8)
  get_heap_size refused on one PE    refused at once, so no answers: the
    (pimm.Machine)                   refusal, answers 0, Size and Used
                                     missing, each model; and pimm_pe's
                                     heap_log holding an answer the
                                     registers never got (7 lines)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import pimm_pe  # noqa: E402
from pimm_layout import HEAP, MEMORY_CELLS  # noqa: E402

I = lambda v: (pimm.INT, v & 0xffffffff)           # noqa: E731
KLB, BLT = 0x23, 0x22
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
HEAPCODE = [(BLT, 0xfe << 24 | 2 << 16 | 3 << 8),  # get_heap_size 2, 3
            (KLB, 0xbc << 24 | 2 << 16 | 0 << 8),  # get_value 2, 0
            (KLB, 0xbc << 24 | 3 << 16 | 1 << 8),  # get_value 3, 1
            (KLB, 0x60 << 24)]                     # proceed

# a term: ('w', tag, offset from C) a word; ('str', text); ('list', n)
# [n]; ('var', k) the unbound variable in slot k
W = lambda tag, d=0: ('w', tag, d)                 # noqa: E731
M, K, H = W(pimm.MOD), W(pimm.COD), W(pimm.SHREC)
PARTS = [
    ('modules', M, M, [], 1),
    ('two modules', M, W(pimm.MOD, 1), [], 0),
    ('codes', K, K, [], 1),
    ('two codes', K, W(pimm.COD, 2), [], 0),
    ('a code and a module', K, M, [], 0),
    ('handles', H, H, [], 1),
    ('two handles', H, W(pimm.SHREC, 1), [], 0),
    ('a handle and a module', H, M, [], 0),
    ('a module and an atom', M, W(pimm.ATOM), [], 0),
    ('an integer and a code', W(pimm.INT), K, [], 0),
    ('a module and a string', M, ('str', 'abc'), [], 0),
    ('a string and a code', ('str', 'abc'), K, [], 0),
    ('a module and a list', M, ('list', 1), [], 0),
    ('Y waits', M, ('var', 10), [(10, M)], 1),
    ('X waits', ('var', 9), K, [(9, W(pimm.COD, 2))], 0),
]
REFUSED = ('an extended float', W(pimm.EXFLT, -1), W(pimm.EXFLT, -1))
REFUSAL = 'wait_value on a 3f word'


def word(t, c):
    return (t[1], (c + t[2]) if t[1] != pimm.EXFLT else 0)


def build(s, t, into, c):
    if t[0] == 'w':
        s.setslot(into, word(t, c))
    elif t[0] == 'str':
        s.string(into, 8, [ord(ch) for ch in t[1]])
    elif t[0] == 'list':
        s.cons(into, 0, I(t[1]), (pimm.ATOM, 0))
    elif t[0] == 'var':
        s._op(driver.PTR, into, t[1], (pimm.REF, 0))
    else:
        raise ValueError(t)


def script(make):
    s = driver.Script()
    s.make = make
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
    s.label('get_heap_size')
    s.vector(15, 8, HEAPCODE)
    m = s.live()
    hat = s.live_slot[15][1] - m.load
    assert [m.opname(hat + i) for i in range(4)] == [
        'get_heap_size', 'get_value', 'get_value', 'proceed']
    s.newvar(0)
    s.newvar(1)
    s.arg(1, 0)
    s.arg(2, 1)
    s.spawn(hat, 2)
    s.run()
    s.out(0)
    s.out(1)
    want = []
    for label, x, y, binds, r in PARTS + [REFUSED + ([], None)]:
        s.label(label)
        for k in (9, 10, 11):
            s.newvar(k)
        build(s, x, X, a0)
        build(s, y, Y, a0)
        s.newvar(R)
        s.arg(1, X)
        s.arg(2, Y)
        s.arg(3, R)
        s.spawn(at, 3)
        s.run()
        for k, v in binds:
            s.out(R)                                   # unbound: the goal waits
            want.append((label + ', waiting', None))
            s.label('%s: slot %d bound' % (label, k))
            s.unifyc(k, word(v, a0))
            s.run()
        if r is not None:
            s.out(R)
            want.append((label, r))
    del m
    return s, want


def refusing(s):
    """s.play(), its last part refused (lockstep_pstruct.py's)."""
    gen = s.play()
    while True:
        try:
            item = next(gen)
        except StopIteration:
            return
        except pimm.Unimplemented as e:
            s.refused = str(e)
            return
        yield item


def pe():
    return pimm_pe.System(pimm.Machine(), 1).pes[0]


def check(name, make):
    s, want = script(make)
    for _ in refusing(s):
        pass
    m = s.machine
    bad = []
    # each OUT's word as dereferenced when it was made: a reference
    # there was an unbound variable then
    got = [w for _label, w in s.outs]
    heap, got = got[:2], got[2:]
    for (label, r), w in zip(want, got):
        t = None if m.unbound(w) else m.term(m.deref(w))
        if t != r:
            bad.append((name, label, t, r))
    if len(got) != len(want):
        bad.append((name, 'answers', len(got), len(want)))
    if getattr(s, 'refused', None) != REFUSAL:
        bad.append((name, 'refusal', getattr(s, 'refused', None)))
    size = heap[0][1] if heap and heap[0][0] == pimm.INT else None
    used = heap[1][1] if len(heap) > 1 and heap[1][0] == pimm.INT else None
    if size != (MEMORY_CELLS - HEAP) // 2 or used is None or not 0 < used < size:
        bad.append((name, 'get_heap_size', heap))
    if isinstance(m, pimm_pe.PE) and m.heap_log != [(size, used)]:
        bad.append((name, 'heap_log', m.heap_log))
    return bad, (size, used), len(got)


def main():
    bad, heaps = [], []
    for name, make in (('pimm', pimm.Machine), ('pimm_pe', pe)):
        b, h, n = check(name, make)
        bad += b
        heaps.append(h)
    if heaps[0] != heaps[1]:
        bad.append(('get_heap_size differs', heaps))
    if bad:
        print('ref wait value: FAIL %d: %r' % (len(bad), bad))
        return 1
    print('ref wait value: PASS (wait_value on modules, codes and shoen handles on pimm.py '
          'and pimm_pe.py: %d answers each as worked by hand (two of them a goal still waiting, '
          'then going on when bound), an extended float refused on both; get_heap_size Size %d, Used %d on both)'
          % (n, heaps[0][0], heaps[0][1]))
    return 0


if __name__ == '__main__':
    sys.exit(main())
