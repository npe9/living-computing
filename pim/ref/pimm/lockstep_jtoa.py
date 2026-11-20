#!/usr/bin/env python3
"""Lockstep: the Bluespec core against the reference model.

    bsv/build_pimm/sim_pimm_jtoa | python3 ref/pimm/lockstep_jtoa.py

Reads the Bluespec bench's trace on standard input (bsv/PimmJtoaTb.bsv)
and compares it, line by line, with the trace ref/pimm/pimm.py produces
for the same goals: jis_to_ascii:convert_element/2 from the IPL image
for every 16-bit key, then an atom, then an unbound variable.

A trace line is one event (docs/pimm_semantics.md "Trace"):
    I pc cell      an instruction is taken
    R n cell       register n is written
    M addr cell    a memory cell is written (addr less the load address)
    E how          the reduction ends: done, fail, susp
    O cell         (bench) the second argument, dereferenced, afterwards

The first difference stops the comparison and is printed with its goal.

Observed fault injections (2026-11-20), each restored afterwards:
  in the Bluespec (bsv/Pimm*.bsv); each FAILed at the place shown:
  hash pair target one cell short (HBox)   goal 8481 (key 2121): I 9517,
                                           a data cell, for I 9518
  not_less_than operands swapped (Exec)    goal 0: went on to I 9589 for
                                           the next clause at I 9597
  arithmetic result to r[x] (Exec)         goal 9008 (key 2330): R 2 for R 0
  hash miss label relative to the
  instruction, not its own cell (HBox)     goal 0: I 9585 for I 9586
  hash index without the mask (HBox)       goal 8481: took the miss label
  unbound switch argument not noted (Exec) goal 65537 (unbound): ran on to
                                           the otherwise clause for E susp
  deref stops at the first cell (DBox)     goal 0: O 06e0008000 (still a
                                           reference) for O 000000003f
  bind writes the wrong cell (DBox)        goal 0: the same O line; the M
                                           line alone did not show it,
                                           because the trace prints the
                                           address the box meant
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import pimm  # noqa: E402
import gen_pimm_bsv  # noqa: E402

PINNED = dict(goals=65538, lines=2015622)


def reference():
    """Yield (goal description, [trace lines]) per goal."""
    m = pimm.Machine(heap=gen_pimm_bsv.LOCKSTEP_HEAP)
    pc = pimm.predicate(m.im, 'jis_to_ascii', 'convert_element/2')

    def goal(arg0):
        out = m.new_var()
        m.tr = []
        try:
            m.run(pc, [arg0, out])
        except pimm.Suspend:
            m.abandon()
        tr, m.tr = m.tr, None
        tr.append('O %02x%08x' % m.deref(out))
        return tr
    for k in range(0x10000):
        yield 'key %04x' % k, goal((pimm.INT, k))
    yield 'atom', goal((pimm.ATOM, 5))
    yield 'unbound', goal(m.new_var())


def main():
    lines = goals = 0
    src = sys.stdin
    for what, want in reference():
        for i, w in enumerate(want):
            got = src.readline().rstrip('\n')
            if got != w:
                print('pimm lockstep jtoa: FAIL at goal %d (%s), line %d of its trace'
                      % (goals, what, i))
                print('  reference: %s' % w)
                print('  bluespec:  %s' % (got or '(end of trace)'))
                for prev in want[max(0, i - 3):i]:
                    print('  after:     %s' % prev)
                return 1
        lines += len(want)
        goals += 1
    extra = src.readline()
    if extra:
        print('pimm lockstep jtoa: FAIL, the Bluespec trace goes on: %s' % extra.strip())
        return 1
    got = dict(goals=goals, lines=lines)
    if got != PINNED:
        print('pimm lockstep jtoa: FAIL, counts %r, pinned %r' % (got, PINNED))
        return 1
    print('pimm lockstep jtoa: PASS (convert_element/2 from the IPL image on the '
          'Bluespec core: %d goals, %d trace lines identical to the reference model)'
          % (goals, lines))
    return 0


if __name__ == '__main__':
    sys.exit(main())
