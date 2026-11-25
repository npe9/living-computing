#!/usr/bin/env python3
"""Lockstep: the order a merger passes messages on, two and three
senders bound in one step (the merger's list, 2026-11-24).

    python3 ref/pimm/lockstep_merge.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_merge.py compare
    python3 ref/pimm/lockstep_merge.py --reference       the reference alone

The rule under test (docs/pimm_semantics.md, merge).  VPIM
(f_reduce_merger_unify.psl.c: the MGHOK cell), KLIC (runtime/gmerge.c)
and PDSS (emulator/unify.c, active_unify_stream_list) all pass a list
bound to a merger input on to the output AT THE UNIFICATION, so the
messages of two inputs reach the output in the order the inputs were
bound.  Here the merger is a goal of the stub merge_in on each input
(asm/pimm_stubs.py); a woken one goes on the merger's list, which is
taken before the ready queue, the goals woken since the last pickup
at its front in the order they were woken.  So the order is the
unifications' order, as in the three sources; that it happens at the
next goal switch and not inside the unification is OURS.  Before
2026-11-24 a woken merge_in went on the ready queue like any goal,
newest first, so two inputs bound in one step were passed on in the
REVERSE order.

The site: ipl_pool:keyed_set/2 (the IPL's keyed pool, lockstep_pool.py),
whose first act is merge(D, E), A = E: the bench's stream A is the
merger's input.  The bench binds A to a vector of inputs (TR-466 3.3:
one more merger input per element; each element's goal is made ready
and suspends on its unbound stream), runs, then binds the inputs, each
to one put(Key, Value, Old) and an unbound tail, in an order that is
not the elements' order, all before one run.  The pool answers each
put with the old value, so the answers show the order the requests
reached it:
  two senders     {I1, I2}, bound I2 (put(1, 200)) then I1 (put(1, 100)):
                  I2's Old = {}, I1's Old = {200}
  three senders   {I1, I2, I3}, bound I1 (put(7, 1)), I3 (put(7, 3)),
                  I2 (put(7, 2)): {}, {1}, {3}
Then every tail is closed: the merger's count reaches 0, its output is
[] and the pool ends; no goal may be left waiting.
Under the rule before 2026-11-24 the reference gives two senders
I2 {100}, I1 {} and three senders I1 {3}, I3 {2}, I2 {} (run with the
pre-change pimm.py, 2026-11-24): the last-bound input first.  So
this test, on both models before the change, FAILs its answers while
the traces agree.

Observed fault injections into the Bluespec, 2026-11-24, each run
alone (bsv/run_pimm_lockstep.sh merge) and restored from a copy:
  a woken merge_in put on the ready     two senders: the pool, its input a
    queue (the rule before)             vector, line 139: G 32790 (picked)
                                        for M 32790 (its link written 0)
  the woken goals listed newest first   two senders: the inputs bound,
                                        line 28: M 32833 for M 32825 (the
                                        other input's goal linked)
  the ready queue taken before the      two senders: the inputs bound,
    merger's list                       line 55: G 32798 for G 32833
The splice onto a list that is not empty (2026-11-24): two parts,
`chained` and `chained, the second input first`, put two mergers in a
chain (code in heap cells: merge 1, 2; merge 2, 3; get_value 0, 3;
proceed, so M1's output is M2's input) and bind M1's two inputs in one
step. The first woken goal passes its message to M2's input and wakes
M2's goal while the second is still on the merger's list, so the
pickup splices M2's goal in front of it, its link the second's
address. The messages reach the output in the order the inputs were
bound: [1, 2], and [2, 1] the other way (worked by hand from the rule
above). On the reference these two parts make 2 of the script's 18
splices, the only ones onto a non-empty list (lockstep_shell.py's
counter).
Observed fault injection, 2026-11-24 (bsv/PimmGBox.bsv, restored from
a copy, its checksum compared after):
  the woken goals spliced on with the   chained: the inputs bound, line
    list's earlier goals dropped (the   41: M 33138 0000000000 for
    link written 0 for the old head)    00e0008193 (the link to the
                                        second goal)
Before these parts it was caught by no lockstep test (it was also passed by
lockstep_atom, lockstep_pool and lockstep_scsi --part 1; in
ref_scsi.py's six IPL parts all 2,051 splices are onto an empty list).
It is also caught by the lockstep from the shell's prompt
(lockstep_shell.py, bsv/run_pimm_shell.sh, outside the suite; on the
checkpoint made with the login ID 1, before P-f3): FAIL at
line 8,429, 1,609 instructions after the prompt, M 77708415 0000000000
for 00e4a3cf57. In that window 88 of 804 splices are onto a non-empty
list (in the whole typed-shutdown run from the cached machine, 300 of
5,859).

The real site whose order this changes is the user table of PIMOS's
task layer (utility/pool/k_bag.kl1, under kernel/task/int_hdl.kl1's
env_check), met only in the whole IPL after the login: the reference's
longrun (ref/pimm/longrun_ipl.py) shows it, and the Bluespec meets it
in the lockstep from a saved machine (lockstep_shell.py, outside the
suite; docs/pimos_roadmap.md R6).

A vector of seven or more (2026-11-25, `seven senders`): a merger input
bound to a long vector, {VECT0+14|o, a} -> {VDESC, the first element},
the size (as the linker lays one out; lockstep_alt.py `vector 7`), was
refused on both models until the compiler met one on the primer's
sample1 (two vectors of 9; lockstep_shell.py APPS compile_sample1).
No source bounds the arity (TR-466 3.3 "as many input streams as the
arity of the vector"; KLIC runtime/gmerge.c:81-104 takes any size;
VPIM f_reduce_merger_unify.psl.c f_Unify_MGHOK_VECT_Sub takes a long
one, with a WARNING).  The merger here is OURS, code in heap cells:
merge 1, 2; get_value 0, 2; proceed (p(A, O): A the input of a merger
whose output is O).  A is bound to a vector of seven whose elements are
[1], [2], [3], an unbound input, [], [6], [7]; after a run the fourth
is bound to [4].  One ready goal per element, the first element's
first, so the last element's runs first: O = [7, 6, 3, 2, 1, 4], closed
when the count is back at 0 (worked by hand; the same on the
reference, both OUTs read at the end).
Observed fault injections, 2026-11-25 (bsv/PimmStages.bsv rule
mergeVecL, each run alone with bsv/run_pimm_lockstep.sh merge and
restored from a copy, compared with cmp):
  the elements read from the descriptor   seven senders: the input bound
    cell, not from its first element      to the vector, line 50: A 1
                                          0de0008254 for 05e000825b
  the size one short                      the same part, line 98: I 18557
                                          for A 1 05e0008263
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402

PINNED = dict(parts=15, lines=2438)
I = lambda v: (pimm.INT, v & 0xffffffff)       # noqa: E731

# (label, the vector's size, [(element, key, value)] in the order bound,
#  the answers in that order as Machine.term shows them)
PARTS = [
    ('two senders', 2, [(1, 1, 200), (0, 1, 100)], [(), (200,)]),
    ('three senders', 3, [(0, 7, 1), (2, 7, 3), (1, 7, 2)], [(), (1,), (3,)]),
]


def script():
    im = pimm.kbndis.Image()
    names = {name: n for n, name in im.sym.items()}
    pc = pimm.predicate(im, 'ipl_pool', 'keyed_set/2')
    s = driver.Script()
    answers = []
    for label, n, binds, _want in PARTS:
        s.label(label + ': the pool, its input a vector')
        s.newvar(0)
        s.arg(1, 0)
        s.argc(2, I(4))
        s.spawn(pc, 2)
        s.run()
        s.vector(1, 2, [None] * n)                # the inputs in slots 2..
        s.unify(0, 1)
        s.run()
        s.label(label + ': the inputs bound')
        m = s.live()
        inputs = [s.live_slot[2 + i] for i in range(n)]
        olds, tails = [], []
        for elem, key, value in binds:
            # the request in 11..14 (Old in 14), its list cell in 9, 10
            s.vector(5, 11, [(pimm.ATOM, names['put']), I(key), I(value), None])
            s.cons(6, 9, ('slot', 5), None)
            s.setslot(7, inputs[elem])
            s.unify(7, 6)
            m = s.live()
            olds.append(s.live_slot[14])
            tails.append(s.live_slot[10])
        s.run()
        for c in olds:
            s.setslot(7, c)
            s.out(7)
        s.label(label + ': the tails closed')
        for c in tails:
            s.setslot(7, c)
            s.unifyc(7, (pimm.ATOM, 0))
        s.run()
        answers.append((label, len(binds)))
    for label, order in CHAINED:
        chained(s, label, order)
    long_vector(s)
    del m
    return s, answers


# Two mergers in a chain, M1's output M2's input: two inputs of M1
# bound in one step (in this order: the elements), each to [message |
# an unbound tail]; then the tails closed (in the order given too).
CHAINED = [('chained', (0, 1)), ('chained, the second input first', (1, 0))]
KLB, GMI = 0x23, 0x22


def chained(s, label, order):
    """The splice onto a list that is not empty (pimm.py pick, the
    Bluespec's GBox Pickup): the first of M1's two woken goals passes
    its message to M2's input and wakes M2's goal while the second is
    still on the merger's list; M2's goal goes in front of it, its
    link the second's.  Code in heap cells (OURS):
        merge 1, 2; merge 2, 3; get_value 0, 3; proceed
    i.e. chain(A, O): merge(O) gives M2's input in r2, merge(r2) M1's
    in r3, and A is M1's input."""
    s.label(label + ': the chain')
    code = [(GMI, 0xf0 << 24 | 1 << 16 | 2 << 8),     # merge 1, 2
            (GMI, 0xf0 << 24 | 2 << 16 | 3 << 8),     # merge 2, 3
            (KLB, 0xbc << 24 | 0 << 16 | 3 << 8),     # get_value 0, 3
            (KLB, 0x60 << 24)]                        # proceed
    for k in range(len(code)):
        s.newvar(k)
    m = s.live()
    a0 = s.live_slot[0][1]
    assert [s.live_slot[k][1] for k in range(len(code))] == list(range(a0, a0 + len(code)))
    for k, c in enumerate(code):
        s.unifyc(k, c)
    m = s.live()
    at = a0 - m.load
    assert [m.opname(at + i) for i in range(4)] == ['merge', 'merge', 'get_value', 'proceed']
    s.newvar(4)                                   # A, M1's input
    s.newvar(5)                                   # O, M2's output
    s.arg(1, 4)
    s.arg(2, 5)
    s.spawn(at, 2)
    s.run()
    s.vector(6, 7, [None, None])                  # {I1, I2} in slots 7, 8
    s.unify(4, 6)
    s.run()
    s.label(label + ': the inputs bound')
    tails = {}
    for e in order:
        s.cons(9, 10 + 2 * e, I(e + 1), None)     # [e + 1 | T] in slots 10.., 11..
        tails[e] = 11 + 2 * e
        s.unify(7 + e, 9)
    s.run()
    s.out(5)
    s.label(label + ': the tails closed')
    for e in order:
        s.unifyc(tails[e], (pimm.ATOM, 0))
    s.run()
    s.out(5)


# A merger input bound to a vector of seven (a long vector: {VECT0+14|o,
# a} -> {VDESC, the first element}, the size, as the linker lays one
# out; lockstep_alt.py `vector 7`).  Its elements: [1], [2], [3], an
# input left unbound, [], [6], [7]; then the fourth bound to [4].
LONG = 7
LONG_WANT = [7, 6, 3, 2, 1, 4]


def long_vector(s):
    s.label('seven senders: the merger')
    code = [(GMI, 0xf0 << 24 | 1 << 16 | 2 << 8),     # merge 1, 2
            (KLB, 0xbc << 24 | 0 << 16 | 2 << 8),     # get_value 0, 2
            (KLB, 0x60 << 24)]                        # proceed
    for k in range(len(code)):
        s.newvar(k)
    m = s.live()
    a0 = s.live_slot[0][1]
    for k, c in enumerate(code):
        s.unifyc(k, c)
    m = s.live()
    at = a0 - m.load
    assert [m.opname(at + i) for i in range(3)] == ['merge', 'get_value', 'proceed']
    s.newvar(14)                                  # A, the input
    s.newvar(15)                                  # O, the output
    s.arg(1, 14)
    s.arg(2, 15)
    s.spawn(at, 2)
    s.run()
    s.label('seven senders: the input bound to the vector')
    for k in range(3 + LONG):
        s.newvar(k)
    m = s.live()
    a0 = s.live_slot[0][1]
    assert [s.live_slot[k][1] for k in range(3 + LONG)] == list(range(a0, a0 + 3 + LONG))
    s.unifyc(0, (pimm.VDESC, a0 + 3))
    s.unifyc(1, I(LONG))
    s.unifyc(2, I(LONG))
    for e in range(LONG):
        if e == 3:
            continue
        if e == 4:
            s.unifyc(3 + e, (pimm.ATOM, 0))
            continue
        s.cons(11, 12, I(e + 1), (pimm.ATOM, 0))
        s.unify(3 + e, 11)
    s._op(driver.PTR, 10, 0, (pimm.VECT0 + 15, 0))
    m = s.live()
    assert m.vsize(m.deref(s.live_slot[10])) == LONG
    s.unify(14, 10)
    s.run()
    s.out(15)
    s.label('seven senders: the fourth input bound')
    s.cons(11, 12, I(4), (pimm.ATOM, 0))
    s.unify(6, 11)
    s.run()
    s.out(15)


def check(s, m):
    bad = []
    got = {}
    for label, w in s.outs:
        got.setdefault(label.split(':')[0], []).append(w)
    # chained: O after the inputs are bound, then after the tails are
    # closed; the messages in the order the inputs were bound
    for label, order in CHAINED:
        a, b = (e + 1 for e in order)
        want = [[a, b], [a, b]]       # read at the end: the same list
        t = [m.term(w) for w in got.get(label, [])]
        if t != want:
            bad.append((label, t, want))
    # seven senders: the merger makes one ready goal per element, the
    # first element's first, so the newest, the last element's, runs
    # first: 7, 6, then [] (the fifth) only ends its input, the fourth
    # waits on its stream, 3, 2, 1; then 4 when it is bound, and its []
    # closes the output (the count back to 0).  Read at the end: the
    # same list both times
    t = [m.term(m.deref(w)) for w in got.get('seven senders', [])]
    if t != [LONG_WANT, LONG_WANT]:
        bad.append(('seven senders', t, [LONG_WANT, LONG_WANT]))
    for label, _n, _binds, want in PARTS:
        ws = got.get(label, [])
        t = []
        for w in ws:
            d = m.deref(w)
            t.append(None if m.unbound(d) else m.term(d))
        if t != want:
            bad.append((label, t, want))
    if m.nsusp:
        bad.append(('%d goals left waiting' % m.nsusp,))
    return bad


def main(argv):
    s, _answers = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    if '--reference' in argv:
        n = sum(len(v) for _k, v in s.play())
        bad = check(s, s.machine)
        print(bad, n)
        return 1 if bad else 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep merge', PINNED)
    if not ok:
        return 1
    bad = check(s, m)
    if bad:
        print('pimm lockstep merge: FAIL %r' % (bad[:3],))
        return 1
    print('pimm lockstep merge: PASS (a merger under ipl_pool:keyed_set/2 on the Bluespec '
          'core, %d trace lines identical to the reference model: two and three inputs '
          'bound in one step, out of the elements\' order, reach the pool in the order they '
          'were bound; the merger closed and no goal left waiting; an input bound to a '
          'vector of seven)' % s.counts['lines'])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
