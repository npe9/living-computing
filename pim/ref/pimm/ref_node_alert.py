#!/usr/bin/env python3
"""The reference models alone, one PE (pimm.py) and the multi-PE model
(pimm_pe.py, a System of one PE): the IFS sweep's next three stops
(docs/ifs_apps.md 4, 2026-11-27).

    python3 ref/pimm/ref_node_alert.py      ends `ref node alert: PASS ...`

1. `wait_value of a variable with itself` (ldlib, mssd, aya, H9-07):
   the guard X = Y with X and Y one unbound variable waits on it, as
   VPIM's klb_equal does ("when undefined, it suspends even if both
   point to the same variable", interpreter/klb_compare.psl.c 36-43;
   PDSS passive_unify case REF the same); INFERENCE for PIM/m, whose
   microcode is not held.  Both models (pimm_pe.py takes pimm.Machine's).
2. `enqueue_goal_to_processor` (mgtp_n, mmi, H9-07, multialign):
   Goal@node(N) on the one-PE pimm.py makes the goal here for any
   integer N, as PDSS (compiler/outp.kl1 360-363: enqueue_to_node is
   compiled to enqueue_goal; doc.e/pdss.tex 71-72) and KLIC on one node
   (runtime/sched.c 277-289) do.  DECLARED DIFFERENCE, OURS: PIM/m
   raises range_overflow for a node outside the shoen's range (PIMOS
   manual e-shoen.tex 491-514); the multi-PE model keeps that refusal
   (pimm_pe.py node_number), which this test checks too.
3. `set_heap_alert` (h907_nseq): set_heap_alert(Size, ^Alarm), 22:FD,
   VPIM interpreter/klb_pimos.psl.c 163-181 and 209-351, the firing
   functions/f_event_self_int.psl.c 67-116: Alarm = Used at once when
   Used > Size; else armed, bound to Used at the first goal switch
   after Used passes Size; a second request binds the first Alarm to
   []; Size >= the heap's Size (range_overflow) and a Size not an
   integer (illegal_input) are refused, loud; an unbound Size waits
   (its stub); the armed Alarm is a root of the collector (VPIM
   structures/str_gc_pre_post.psl.c 2.11).

The goals (cells in the heap, as ref_wait_value.py builds them):
  p(X, Y, R) :- X = Y | R = 1.  otherwise.  p(_, _, R) :- true | R = 0.
      (ref_wait_value.py's CODE)
  q(R, P) :- true | r(R)@node(P).     r(R) :- true | R = 1.
      enqueue_goal_to_processor r1, @3; (arity 1); proceed;
      @3: get_integer 0, 1; proceed
The parts, R worked by hand:
  p(V, V, R)                     waits on V; V = 3: R = 1
  p([V], [V], R)                 waits on V (inside the lists, the
                                 passive unification's); V = a: R = 1
  p(V, W, R)                     waits on V; V = W: woken, it meets
                                 one variable twice and waits on W;
                                 W = 7: R = 1
  pimm.py:  q(R, N), N = 0, 1, 5, -1    R = 1 each (the goal made here)
            q(R, P), P unbound          waits (to_processor); P = 3: R = 1
            q(R, foo)                   refused `enqueue_goal_to_processor
                                        (2, ...), 1 arguments`
  pimm_pe.py: q(R, 0)                   R = 1
            q(R, 1)                     refused `Goal@node(1) of 1 nodes:
                                        range_overflow, not modelled`
set_heap_alert is called on a bare machine of each model, the heap's
use moved by allocating (U = Used before each step, S = Size):
  Size U - 1                     Alarm = U at once (Used > Size)
  Size U                         armed (Used = Size is not past it)
  Size U + 10                    the earlier Alarm = []; armed again
  cells allocated to Used = U+10  the goal switch: still unbound
  1 more                         the goal switch: Alarm = U + 11, cleared
  Size an unbound variable       a waiting goal; bound to U + 100 and
                                 run: armed at U + 100, the goal's Alarm
                                 the armed one
  a collection                   the armed Alarm moved to the to-space,
                                 still unbound; alloc past it and the
                                 goal switch: bound to the use then
  Size S - 1                     armed (accepted)
  Size S                         refused (range_overflow)
  Size foo                       refused (illegal_input)

Observed fault injections (each into a private copy of ref/pimm, this
script run on it, 2026-11-27; the failures listed are all of them):
  the old refusal (`wait_value of a     both models refused at the first
    variable with itself`)              part: answers 0 of 13 and 0 of 8,
                                        the refusal (4 lines)
  X = X taken as equal (the identity    p(V, V) and p(V, W) (after V = W)
    shortcut VPIM's comment rules out)  answer 1 where they wait, each
                                        model (4 lines); p([V], [V])
                                        still waits (passive's own path)
  the old enqueue refusal (only 0)      pimm: refused at N = 1, `(0, 1),
                                        1 arguments`, answers 8 of 13
                                        (2 lines); pimm_pe unchanged
  the old refusal at the stub only      pimm: the bound `q(R, P)` (P = 3)
    (i_to_processor, `or w[1] != 0`)    refused, `enqueue_goal_to_processor
                                        (0, 3)`, answers 12 of 13 (2
                                        lines); pimm_pe unchanged
  pimm_pe's range check removed         pimm_pe: node 1 of 1 thrown to a
    (node_number)                       PE that is not there, refused
                                        otherwise (`code at .. has no
                                        predicate head`; 1 line)
  set_heap_alert: Alarm = Used at once  `Size U` bound to U, not armed,
    on Used >= Size (not >)             and so no [] for it at the next
                                        request (2 lines each model)
  the firing on >= (not >)              fired at Used = Size (`up to
                                        Size` bound, `1 more` one short:
                                        2 lines each model)
  the earlier Alarm not given []        `Size U + 10: the first Alarm`
                                        unbound (1 line each model)
  Size == the heap's Size accepted      `Size S` armed, not refused (1
    (> for >=)                          line each model)
  the Alarm not a root of the           the collection: the alarm's old
    collector (pimm_gc.py)              cell dead, KeyError on its deref
                                        (1 line each model)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import pimm_gc  # noqa: E402
import pimm_pe  # noqa: E402
from ref_wait_value import CODE, NAMES  # noqa: E402

I = lambda v: (pimm.INT, v & 0xffffffff)           # noqa: E731
KLB, BLT = 0x23, 0x22
X, Y, R, P = 12, 13, 14, 11
QCODE = [(KLB, 0x65 << 24 | 1 << 16 | 1),          # enqueue_goal_to_processor r1, @3
         (KLB, 1 << 24),                           # its arity
         (KLB, 0x60 << 24),                        # proceed
         (KLB, 0xb9 << 24 | 0 << 16 | 1),          # @3: get_integer 0, 1
         (KLB, 0x60 << 24)]                        # proceed
QNAMES = ['enqueue_goal_to_processor', None, 'proceed', 'get_integer', 'proceed']
FOO = (pimm.ATOM, 0x123)


def script(make, nodes, refused_node):
    s = driver.Script()
    s.make = make
    s.label('the goals')
    for k in range(len(CODE)):
        s.newvar(k)
    m = s.live()
    a0 = s.live_slot[0][1]
    for k, c in enumerate(CODE):
        s.unifyc(k, c)
    m = s.live()
    at = a0 - m.load
    assert [m.opname(at + i) for i in range(len(CODE))] == NAMES
    s.vector(15, 8, QCODE)
    m = s.live()
    qat = s.live_slot[15][1] - m.load
    assert [m.opname(qat + i) for i in (0, 2, 3, 4)] == [n for n in QNAMES if n]
    want = []

    def p(label, x, y, binds):
        s.label(label)
        s.newvar(R)
        s.arg(1, x)
        s.arg(2, y)
        s.arg(3, R)
        s.spawn(at, 3)
        s.run()
        for k, cell, done in binds:
            s.out(R)
            want.append((label + ', waiting', None))
            s.label('%s: slot %d bound' % (label, k))
            if isinstance(cell, int) and cell < 0:
                s.unify(k, -cell)
            else:
                s.unifyc(k, cell)
            s.run()
        s.out(R)
        want.append((label, 1))

    s.newvar(9)
    p('p(V, V)', 9, 9, [(9, I(3), True)])
    s.newvar(9)
    s.cons(X, 1, ('slot', 9), (pimm.ATOM, 0))
    s.cons(Y, 3, ('slot', 9), (pimm.ATOM, 0))
    p('p([V], [V])', X, Y, [(9, (pimm.ATOM, 0x55), True)])
    s.newvar(9)
    s.newvar(10)
    p('p(V, W)', 9, 10, [(9, -10, False), (10, I(7), True)])

    def q(label, node, bind=None):
        s.label(label)
        s.newvar(R)
        if node is None:
            s.newvar(P)
        else:
            s.setslot(P, node)
        s.arg(1, R)
        s.arg(2, P)
        s.spawn(qat, 2)
        s.run()
        if bind is not None:
            s.out(R)
            want.append((label + ', waiting', None))
            s.label(label + ': bound')
            s.unifyc(P, bind)
            s.run()
        s.out(R)
        want.append((label, 1))

    for n in nodes:
        q('q(R, %d)' % n, I(n))
    if make is pimm.Machine:
        q('q(R, P)', None, I(3))
    s.label('refused')
    s.newvar(R)
    s.setslot(P, refused_node)
    s.arg(1, R)
    s.arg(2, P)
    s.spawn(qat, 2)
    s.run()
    s.out(R)
    return s, want


def refusing(s):
    gen = s.play()
    while True:
        try:
            next(gen)
        except StopIteration:
            return
        except pimm.Unimplemented as e:
            s.refused = str(e)
            return


def pe():
    return pimm_pe.System(pimm.Machine(), 1).pes[0]


def check_goals(name, make, nodes, refused_node, refusal):
    s, want = script(make, nodes, refused_node)
    refusing(s)
    m = s.machine
    bad = []
    got = [w for _label, w in s.outs]
    for (label, r), w in zip(want, got):
        t = None if m.unbound(w) else m.term(m.deref(w))
        if t != r:
            bad.append((name, label, t, r))
    if len(got) != len(want):
        bad.append((name, 'answers', len(got), len(want)))
    if getattr(s, 'refused', None) != refusal:
        bad.append((name, 'refusal', getattr(s, 'refused', None)))
    return bad, len(got)


def call(m, size):
    """set_heap_alert(Size, ^Alarm) with r0 = Size, r1 its output; the
    output word, or the refusal's text."""
    m.reg[0] = size
    m.reg[1] = (pimm.INT, 0xdead)
    try:
        m.i_set_heap_alert(0, 0, 1, 0, 0)
    except pimm.Unimplemented as e:
        return str(e)
    return m.reg[1]


def term(m, w):
    w = m.deref(w)
    return None if m.unbound(w) else m.term(w)


def check_alert(name, make):
    m = make()
    bad = []
    size, u = m.heap_size()
    a = call(m, I(u - 1))
    if term(m, a) != u:
        bad.append((name, 'Size U - 1', term(m, a), u))
    a1 = call(m, I(u))
    if not isinstance(a1, tuple) or term(m, a1) is not None or m.heap_alert_size != u:
        bad.append((name, 'Size U', a1 if isinstance(a1, str) else term(m, a1), m.heap_alert_size))
    u = m.heap_size()[1]
    a2 = call(m, I(u + 10))
    if isinstance(a1, tuple) and term(m, a1) != []:
        bad.append((name, 'Size U + 10: the first Alarm', term(m, a1)))
    if not isinstance(a2, tuple) or term(m, a2) is not None:
        bad.append((name, 'Size U + 10', a2))
    # the heap's use up to Size exactly (the fresh Alarm took a cell)
    m.alloc(u + 10 - m.heap_size()[1])
    m.goal_switch(m.steps + 1000)
    if isinstance(a2, tuple) and term(m, a2) is not None:
        bad.append((name, 'up to Size', term(m, a2)))
    m.alloc(1)
    m.goal_switch(m.steps + 1000)
    if not isinstance(a2, tuple) or term(m, a2) != u + 11 or m.heap_alert_var is not None:
        bad.append((name, '1 more', isinstance(a2, tuple) and term(m, a2), m.heap_alert_var))
    # an unbound Size: the stub's goal waits; bound, it runs
    u = m.heap_size()[1]
    v = m.new_var()
    out = call(m, v)
    m.unify(v, I(u + 100))
    m.run()
    armed = m.heap_alert_var
    if armed is None or m.heap_alert_size != u + 100 or term(m, out) is not None \
            or m.deref(out) != m.deref(armed):
        bad.append((name, 'Size unbound', m.heap_alert_size, out, armed))
    # a collection: the armed Alarm is a root
    try:
        pimm_gc.collect(m)
        w = m.deref(m.heap_alert_var)
        lo = m.heap_lo
        if not m.unbound(w) or not lo <= w[1] < m.hp:
            bad.append((name, 'collection', w))
        s = m.heap_alert_size
        u = m.heap_size()[1]
        if u <= s:
            m.alloc(s - u + 1)
        m.goal_switch(m.steps + 1000)
        if m.heap_alert_var is not None or term(m, w) != m.heap_size()[1]:
            bad.append((name, 'collection: the alarm', term(m, w)))
    except (KeyError, pimm.Unimplemented, RuntimeError) as e:
        bad.append((name, 'collection', repr(e)))
    m.heap_alert_var = m.heap_alert_size = None     # (after a failure: the rest goes on)
    size = m.heap_size()[0]
    a = call(m, I(size - 1))
    if not isinstance(a, tuple) or term(m, a) is not None:
        bad.append((name, 'Size S - 1', a))
    a = call(m, I(size))
    if not isinstance(a, str) or 'range_overflow' not in a:
        bad.append((name, 'Size S', a))
    a = call(m, FOO)
    if not isinstance(a, str) or 'illegal_input' not in a:
        bad.append((name, 'Size foo', a))
    return bad


def main():
    bad = []
    b, n1 = check_goals('pimm', pimm.Machine, (0, 1, 5, -1), FOO,
                        'enqueue_goal_to_processor %r, 1 arguments' % (FOO,))
    bad += b
    b, n2 = check_goals('pimm_pe', pe, (0,), I(1),
                        'Goal@node(1) of 1 nodes: range_overflow, not modelled')
    bad += b
    for name, make in (('pimm', pimm.Machine), ('pimm_pe', pe)):
        bad += check_alert(name, make)
    if bad:
        print('ref node alert: FAIL %d: %r' % (len(bad), bad))
        return 1
    print('ref node alert: PASS (X = X on one variable waits on it, on pimm.py and pimm_pe.py; '
          'Goal@node(N) made here for any integer on pimm.py (%d answers), node 1 of 1 still '
          'refused on pimm_pe.py (%d answers); set_heap_alert at once, armed, cancelled with [], '
          'fired past Size, waiting on Size, a root of the collector, Size >= the heap and a non-'
          'integer refused, on both)' % (n1, n2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
