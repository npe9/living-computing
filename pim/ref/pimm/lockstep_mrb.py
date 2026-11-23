#!/usr/bin/env python3
"""Lockstep: set_vector_element in place, under the MRB.

    python3 ref/pimm/lockstep_mrb.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_mrb.py compare

ipl_module:deref_and_set/4 (object code, asm/kl1decomp.py), its last
clause:

    deref_and_set(A, B, C, D) :- wait(C) |
        set_vector_element(A, B, C, _, E),
        D = E.

"providing the path to the vector is single", set_vector_element
updates in place (PIM/m paper, M92 p. 430; PDSS
blt_b_set_vector_element).  The cases, each a vector {1, 2, 3} whose
element 1 is set to 77; the test knows the vector's address from its
private reference machine and gives the argument's word itself:

  held        the vector as the driver's slot gives it (marked): a
              copy.  The old vector must still read {1, 2, 3}.
  single      the vector's word with its MRB off: in place.  The new
              vector is at the old address.
  marked ref  a marked reference to a variable bound to the unmarked
              word: a copy (dereference carries the reference's MRB).
  plain ref   an unmarked reference to such a variable: in place.
  variable    unmarked, but element 1 is an unbound variable's cell:
              a copy, ours (the cell is never overwritten).  The
              variable is then bound to 5: the old vector reads
              {1, 5, 3}, the new one {1, 77, 3}.

Each is checked by content and address, not only by the trace: both
models share the rule, so the trace alone would not show a wrong one.
In `single` and `plain ref` the driver's slot still points at the
vector, against the bit it was given: there the old vector reads
{1, 77, 3}, which is what in place means.

The rule's soundness on real code is not shown here.  A probe on the
reference model (not in the repository) poisoned every vector updated
in place and found no later read of one in 21 of the lockstep scripts;
that covers only the paths those scripts run.

Observed fault injections into the Bluespec, 2026-11-23, each FAILed
where shown and was restored:
  - in place although the vector is marked (PimmVBox go): ptab part 0,
    line 2930 (an element written where the reference allocates a copy)
  - never in place: ground part 12, line 85 (a copy where the reference
    writes the element)
  - in place over an unbound variable's cell: mrb part 4 (variable),
    line 31 (77 written at the cell)
  - in place, Old given as the new element: ground part 12, line 86
  - in place, the next cell written: ground part 12, line 85; the
    simulator then ran on without output and had to be stopped
All five are trace mismatches, found before this test's own checks
run, because the reference model was right.  The same wrong rule put
in BOTH models, tried on the reference model alone:
  - always in place: this test's checks report ('held', 'in place'),
    ('held', 'old', (1, 77, 3)), ('marked ref', 'in place'),
    ('marked ref', 'old', (1, 77, 3))
  - in place over a variable's cell: the unification of the variable
    with 5 fails (Fail unify (0, 77) (0, 5)), an exception, not a
    reported check
Not run by any test: a vector of more than a few cells updated in
place in this test (the loader tests do that, checked by the module
objects' contents); read_variable from a vector whose word is
unmarked.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import driver  # noqa: E402
import pimm  # noqa: E402

PINNED = dict(parts=5, lines=220)
V3 = pimm.VECT0 + 6
INT = pimm.INT
#        name          how the argument is made         variable  in place
CASES = (('held',       'slot',                          False,    False),
         ('single',     'word',                          False,    True),
         ('marked ref', 'refx',                          False,    False),
         ('plain ref',  'ref',                           False,    True),
         ('variable',   'word',                          True,     False))


def script():
    im = pimm.kbndis.Image()
    pc = pimm.predicate(im, 'ipl_module', 'deref_and_set/4')
    s = driver.Script()
    want = []
    for name, how, var, inplace in CASES:
        s.label(name)
        s.vector(0, 1, [(INT, 1), None if var else (INT, 2), (INT, 3)])
        s.newvar(5)
        addr = s.live() and s.live_slot[0][1]
        if how == 'slot':
            s.arg(1, 0)
        elif how == 'word':
            s.argc(1, (V3, addr))
        else:
            s.newvar(6)
            s.unifyc(6, (V3, addr))
            ref = s.live() and s.live_slot[6][1]
            s.argc(1, (pimm.REF + (how == 'refx'), ref))
        s.argc(2, (INT, 1))
        s.argc(3, (INT, 77))
        s.arg(4, 5)
        s.spawn(pc, 4)
        s.run()
        if var:
            s.unifyc(2, (INT, 5))
        s.out(0)
        s.out(5)
        was = (1, 5, 3) if var else (1, 77, 3) if inplace else (1, 2, 3)
        want.append((name, addr, inplace, was))
    return s, want


def check(s, m, want):
    bad = []
    got = {}
    for label, w in s.outs:
        got.setdefault(label, []).append(w)
    for name, addr, inplace, was in want:
        old, new = got[name]
        if m.unbound(new) or new[0] & ~1 != V3:
            bad.append((name, 'no new vector', new))
            continue
        if old[1] != addr:
            bad.append((name, 'the old vector moved'))
        if (new[1] == addr) != inplace:
            bad.append((name, 'in place' if new[1] == addr else 'copied'))
        if m.term(new) != (1, 77, 3):
            bad.append((name, 'new', m.term(new)))
        if m.term(old) != was:
            bad.append((name, 'old', m.term(old)))
    return bad


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep mrb', PINNED)
    if not ok:
        return 1
    bad = check(s, m, want)
    if bad:
        print('pimm lockstep mrb: FAIL %r' % bad[:4])
        return 1
    print('pimm lockstep mrb: PASS (set_vector_element under the MRB on the Bluespec core, '
          '%d cases, %d trace lines identical to the reference model: in place when the '
          'vector is reached with every MRB off, at the same address; a copy, the old '
          'vector unchanged, when the vector or a reference to it is marked or the '
          'element is an unbound variable)' % (s.counts['parts'], s.counts['lines']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
