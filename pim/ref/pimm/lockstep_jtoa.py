#!/usr/bin/env python3
"""Lockstep: the Bluespec core against the reference model.

    bsv/build_pimm/sim_pimm_jtoa | python3 ref/pimm/lockstep_jtoa.py

Reads the Bluespec bench's trace on standard input (bsv/PimmJtoaTb.bsv)
and compares it, line by line, with the trace ref/pimm/pimm.py produces
for the same goals: jis_to_ascii:convert_element/2 from the IPL image
for every 16-bit key and an atom; then with an unbound variable that
is bound after the goal has suspended (directly; through a second
variable; and with two goals waiting on it).

The trace format is in docs/pimm_semantics.md ("Trace"); "O cell" is
the bench printing a variable, dereferenced.  The first difference
stops the comparison and is printed with its goal.

Observed fault injections into the Bluespec (bsv/Pimm*.bsv), 2026-11-20,
on the code as it is now (goal box, hooks, wake); each FAILed where
shown and was restored:
  HBox  hash pair target one cell short        key 2121: I 9517 (a data
                                               cell) for I 9518
  HBox  miss label relative to the instruction key 0000: I 9585 for I 9586
  HBox  hash index without the mask            key 2121: took the miss label
  Exec  not_less_than operands swapped         key 0000: I 9589 for I 9597
  Exec  arithmetic result to r[x]              key 2330: R 2 for R 0
  Exec  unbound switch argument not noted      bound: ran on (I 9620)
                                               where the record is written
  DBox  bind writes the next cell              key 0000: M 32769 for M 32768
  DBox  a hooked cell not taken as unbound     bound: Q for the bind's M line
  DBox  binding a hooked variable does not
        report its waiters                     bound: Q for W
  DBox  dereference stops after one hop        chain: I 9619 for I 9385 (the
                                               goal saw V's reference to W as
                                               a value)
  GBox  woken goal not put on the queue        bound: Q for G
  GBox  hooked variable points at the goal,
        not the suspension record              bound: the HOOK cell's value
  GBox  picked-up goal not marked TAKEN        key 0000: status 0 for 2
  GBox  suspended record's arguments from r1   bound: the argument cell
  GBox  queue link not followed at pickup      key 0000: G again for Q
  GBox  wake ignores the status                bound: Q for W
  GBox  second hook on a variable drops the
        first                                  two: the record's next cell
  GBox  wake stops after the first waiter      two: G for the second W
  GBox  new ready goal not linked to the queue two: the record's link cell
Two of these passed until the bench grew the scenario that catches
them: "dereference stops after one hop" needed a chain of two
references, "second hook drops the first" needed two goals on one
variable.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import pimm  # noqa: E402

PINNED = dict(goals=65540, lines=2933430)


def reference():
    """Yield (what, [trace lines]) per goal or scenario: the script of
    bsv/PimmJtoaTb.bsv, operation for operation."""
    m = pimm.Machine()
    pc = pimm.predicate(m.im, 'jis_to_ascii', 'convert_element/2')
    key = (pimm.INT, 0x2341)

    def run():
        try:
            m.run()
        except pimm.Suspend:
            pass

    def out(v):
        m.tr.append('O %02x%08x' % m.deref(v))

    for k in list(range(0x10000)) + ['atom']:
        m.tr = []
        o = m.new_var()
        m.spawn(pc, [(pimm.ATOM, 5) if k == 'atom' else (pimm.INT, k), o])
        run()
        out(o)
        yield ('atom' if k == 'atom' else 'key %04x' % k), m.tr

    # bound: the goal suspends on V, V is bound, the goal finishes
    m.tr = []
    v, o = m.new_var(), m.new_var()
    m.spawn(pc, [v, o])
    run()
    out(o)
    m.unify(v, key)
    run()
    out(o)
    yield 'bound', m.tr

    # chain: V is bound to W first; the goal wakes, finds W through V
    # and suspends again; W is bound and it finishes
    m.tr = []
    v, o = m.new_var(), m.new_var()
    m.spawn(pc, [v, o])
    run()
    out(o)
    w = m.new_var()
    m.unify(v, w)
    run()
    out(o)
    m.unify(w, key)
    run()
    out(o)
    yield 'chain', m.tr

    # two: two goals wait on one V
    m.tr = []
    v, o1 = m.new_var(), m.new_var()
    m.spawn(pc, [v, o1])
    o2 = m.new_var()
    m.spawn(pc, [v, o2])
    run()
    out(o1)
    m.unify(v, key)
    run()
    out(o1)
    out(o2)
    yield 'two', m.tr


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
