#!/usr/bin/env python3
"""Lockstep: the unification of two structures (vectors, lists).

    python3 ref/pimm/lockstep_unif.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_unif.py compare

Two lists, or two vectors of the same size, are not unified where
they meet.  PDSS makes a goal of a pseudo-predicate that unifies the
elements when it runs (emulator/unify.c
make_unify_list_list_goal_and_enqueue,
make_unify_vector_vector_goal_and_enqueue, dc_unify_vector_vector2),
so nested structures need no stack: an element pair that is two
structures again makes another goal.  Both models do the same; the
goal's code is the stub unify_step (asm/pimm_stubs.py, 22:01: OURS,
not a PIM/m instruction), which unifies one element pair each time
it is taken.  What PIM/m's firmware did is not known.  PDSS does all
the elements in one reduction and frees a structure whose MRB is off;
here nothing is freed.

The IPL needs it in its linker: ipl_link_table:put_ex_mod/8 sends
get_and_put(A, {B, H}, {B, [D|H]}) to a keyed set, whose
do_get_and_put/5 unifies the stored {B, List} with {B, H}
(asm/kl1decomp.py ipl_link_table).  That runs only when two modules
name the same external module, which no one-file test here does;
loading pimm_patch_mkdir360E.sav (six modules) on the reference model
alone does it 23 times.

Nine parts, each a unification by the bench and then a run:
  flat          {X, Y} = {1, normal}
  both          {X, 2, 3} = {1, Y, 3}
  lists         [1, 2 | T] = [1, 2, 3]
  nested        {X, {Y, 7}, [Z]} = {{normal, 5}, {6, 7}, [8]}
  woken         ipl_pool:hash(X, H, _) waits for X; {X} = {5}: H = 5
  itself        a vector against itself: a goal all the same
  six           a vector of six, the largest with its size in the tag
  last differs  {1, 2, 3} = {1, 2, 4}: the step fails
  sizes differ  {1, {1, 2}} = {1, {1, 2, 3}}: fails one level down
Checked: every variable's value; failure in the last two parts and
nowhere else; the stub was taken in every part; no goal left waiting.

Observed fault injections into the Bluespec, 2026-11-23, restored:
  step: the last element skipped          unif: flat, line 22
  step: b's element from the next cell    unif: flat, line 20
  goal starts at element 1                unif: flat, line 12
  a list has one cell                     unif: lists, line 36
  goal's arguments swapped                unif: flat, line 10
  step: waiting goals not woken           pool, line 157 (the rule is
                                          shared with the merger's step)
NOT caught: "an element's MRB always off" and "always on".  Every
structure here is made by the bench, whose slots always have the MRB
on, and every element is a reference to a bound variable holding a
value stored with its MRB on, so what is taken looks the same.  The
MRB rule (an element is taken with its MRB on if its structure's is)
is from PDSS and is untested.

The same wrong rule in BOTH models, tried on the reference model
alone, is reported by the value checks: the last element skipped, a
list of one cell, b's element from another cell, no unification.

Not run: a vector of seven or more (refused: its size is in memory);
a vector against a list or sizes differing at the top (plain failure
in unify, as before); a unification inside clause code that makes
the goal (get_value on two vectors: only on the reference model, in
the linker); strings and modules (as before).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402

PINNED = dict(parts=9, lines=484)
I = lambda v: (pimm.INT, v)                        # noqa: E731


def script():
    im = pimm.kbndis.Image()
    names = {name: n for n, name in im.sym.items()}
    A = lambda n: (pimm.ATOM, names[n])            # noqa: E731
    s = driver.Script()
    want = []      # (part, [expected terms of its outs]) ; None = unbound

    def part(name, exp):
        want.append((name, exp))

    # 1. {X, Y} = {1, normal}
    s.label('flat')
    s.vector(0, 2, [None, None])
    s.vector(1, 4, [I(1), A('normal')])
    s.unify(0, 1)
    s.run()
    s.out(2)
    s.out(3)
    part('flat', [1, 'normal'])

    # 2. both sides bind: {X, 2, 3} = {1, Y, 3}
    s.label('both')
    s.vector(0, 2, [None, I(2), I(3)])
    s.vector(1, 5, [I(1), None, I(3)])
    s.unify(0, 1)
    s.run()
    s.out(2)
    s.out(6)
    part('both', [1, 2])

    # 3. lists: [1, 2 | T] = [1, 2, 3]
    s.label('lists')
    s.newvar(9)
    s.cons(2, 3, I(2), ('slot', 9))
    s.cons(0, 5, I(1), ('slot', 2))
    s.cons(7, 3, I(3), (pimm.ATOM, 0))
    s.cons(8, 10, I(2), ('slot', 7))
    s.cons(1, 12, I(1), ('slot', 8))
    s.unify(0, 1)
    s.run()
    s.out(9)
    part('lists', [[3]])

    # 4. nested: {X, {Y, 7}, [Z]} = {{normal, 5}, {6, 7}, [8]}
    s.label('nested')
    s.vector(4, 5, [None, I(7)])               # Y in 5
    s.cons(7, 8, None, (pimm.ATOM, 0))         # Z in 8
    s.vector(0, 10, [None, ('slot', 4), ('slot', 7)])     # X in 10
    s.setslot(14, (0, 0))
    s.newvar(14)
    s.unify(14, 10)                            # keeps X
    s.newvar(15)
    s.unify(15, 5)                             # keeps Y
    s.newvar(13)
    s.unify(13, 8)                             # keeps Z
    s.vector(2, 4, [A('normal'), I(5)])
    s.vector(3, 6, [I(6), I(7)])
    s.cons(9, 10, I(8), (pimm.ATOM, 0))
    s.vector(1, 4, [('slot', 2), ('slot', 3), ('slot', 9)])
    s.unify(0, 1)
    s.run()
    s.out(14)
    s.out(15)
    s.out(13)
    part('nested', [('normal', 5), 6, 8])

    # 5. a goal waiting on an element's variable is woken by the step:
    #    ipl_pool:hash(X, H, NewX) waits for X; {X} = {5}
    s.label('woken')
    s.vector(0, 2, [None])
    s.newvar(4)
    s.newvar(5)
    s.arg(1, 2)
    s.arg(2, 4)
    s.arg(3, 5)
    s.spawn(pimm.predicate(im, 'ipl_pool', 'hash/3'), 3)
    s.run()
    s.out(4)
    s.vector(1, 6, [I(5)])
    s.unify(0, 1)
    s.run()
    s.out(4)
    part('woken', [None, 5])

    # 6. a structure against itself: a goal all the same, nothing bound
    s.label('itself')
    s.vector(0, 2, [None, I(4)])
    s.unify(0, 0)
    s.run()
    s.out(2)
    s.out(3)
    part('itself', [None, 4])

    # 7. a vector of six, the largest whose size is in its tag
    s.label('six')
    s.vector(0, 2, [None, None, None, None, None, None])
    s.setslot(14, (0, 0))
    s.newvar(14)
    s.unify(14, 7)                             # keeps the last variable
    s.vector(1, 8, [I(1), I(2), I(3), I(4), I(5), I(6)])
    s.unify(0, 1)
    s.run()
    s.out(2)
    s.out(14)
    part('six', [1, 6])

    # 8. the last elements differ: {1, 2, 3} = {1, 2, 4} fails in the step
    s.label('last differs')
    s.vector(0, 2, [I(1), I(2), I(3)])
    s.vector(1, 5, [I(1), I(2), I(4)])
    s.unify(0, 1)
    s.run()
    part('last differs', [])

    # 9. sizes differ, one level down: {1, {1, 2}} = {1, {1, 2, 3}}
    s.label('sizes differ')
    s.vector(4, 6, [I(1), I(2)])
    s.vector(0, 2, [I(1), ('slot', 4)])
    s.vector(5, 6, [I(1), I(2), I(3)])
    s.vector(1, 9, [I(1), ('slot', 5)])
    s.unify(0, 1)
    s.run()
    part('sizes differ', [])
    return s, want


FAILS = {'last differs', 'sizes differ'}


def check(s, m, want, parts):
    """parts: {label: trace lines}."""
    bad = []
    outs = {}
    for label, w in s.outs:
        outs.setdefault(label, []).append(w)
    stub = m.stubs['$unify_step']['addr']
    for name, exp in want:
        got = [None if m.unbound(w) else m.term(w) for w in outs.get(name, [])]
        if got != exp:
            bad.append((name, got, exp))
        lines = parts.get(name, [])
        failed = 'E fail' in lines
        if failed != (name in FAILS):
            bad.append((name, 'failed' if failed else 'did not fail'))
        if not any(ln.startswith('I %d ' % stub) for ln in lines):
            bad.append((name, 'the step was not taken'))
    if m.nsusp:
        bad.append(('%d goals left waiting' % m.nsusp,))
    return bad


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    if '--reference' in argv:
        parts = dict(s.play())
        print(check(s, s.machine, want, parts), sum(len(v) for v in parts.values()))
        return 0
    kept = {}
    play = s.play

    def keeping():
        for what, lines in play():
            kept[what] = lines
            yield what, lines
    s.play = keeping
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep unif',
                           dict(parts=PINNED['parts'], lines=PINNED['lines']))
    if not ok:
        return 1
    bad = check(s, m, want, kept)
    if bad:
        print('pimm lockstep unif: FAIL %r' % (bad[:3],))
        return 1
    print('pimm lockstep unif: PASS (two vectors, two lists unified through a goal of their '
          'own on the Bluespec core: %d parts, %d trace lines identical to the reference '
          'model; every binding as expected, the two mismatches fail)'
          % (s.counts['parts'], s.counts['lines']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
