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
NOT caught: the woken goals spliced on with the list's earlier goals
dropped (the link written 0 for the old head).  It changes nothing
unless a merge_in is woken while the merger's list holds goals, which
needs a merger's output to reach another merger's input; with the one
merger here it cannot happen, and in ref_scsi.py's six IPL parts it
never does (2,051 splices, every one onto an empty list, counted on
the reference 2026-11-24).  Also passed by lockstep_atom, lockstep_pool
and lockstep_scsi --part 1 with it injected.  Three of four caught.
The case IS met in PIMOS: in the typed-shutdown run from the cached
machine (longrun_ipl.py --type shutdown --type yes), 300 of 5,859
splices go onto a non-empty list (counted on the reference,
2026-11-24).  So the front-splice order is live there and checked on
the reference model only, not in lockstep.

The real site whose order this changes is the user table of PIMOS's
task layer (utility/pool/k_bag.kl1, under kernel/task/int_hdl.kl1's
env_check), met only in the whole IPL after the login: the reference's
longrun (ref/pimm/longrun_ipl.py) shows it, the Bluespec is not run
that far (docs/pimos_roadmap.md R6).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402

PINNED = dict(parts=6, lines=1614)
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
    del m
    return s, answers


def check(s, m):
    bad = []
    got = {}
    for label, w in s.outs:
        got.setdefault(label.split(':')[0], []).append(w)
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
          'were bound; the merger closed and no goal left waiting)' % s.counts['lines'])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
