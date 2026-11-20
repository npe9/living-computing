#!/usr/bin/env python3
"""Lockstep: the Bluespec core against the reference model.

    python3 ref/pimm/lockstep_jtoa.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_jtoa.py compare

The test is one script of operations (ref/pimm/driver.py).  The
Bluespec driver bench (bsv/PimmDriverTb.bsv) executes it and prints
its trace, read here on standard input and compared, line by line,
with the trace ref/pimm/pimm.py produces playing the same script: jis_to_ascii:convert_element/2 from the IPL image
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
import driver  # noqa: E402
import pimm  # noqa: E402

PINNED = dict(parts=65540, lines=2933430)
KEY = (pimm.INT, 0x2341)


def script():
    s = driver.Script()
    pc = pimm.predicate(pimm.kbndis.Image(), 'jis_to_ascii', 'convert_element/2')

    def goal(arg_slot, out_slot):
        s.arg(1, arg_slot)
        s.arg(2, out_slot)
        s.spawn(pc, 2)

    for k in list(range(0x10000)) + ['atom']:
        s.label('atom' if k == 'atom' else 'key %04x' % k)
        s.newvar(1)
        s.argc(1, (pimm.ATOM, 5) if k == 'atom' else (pimm.INT, k))
        s.arg(2, 1)
        s.spawn(pc, 2)
        s.run()
        s.out(1)

    # the goal suspends on V; V is bound; the goal finishes
    s.label('bound')
    s.newvar(0)
    s.newvar(1)
    goal(0, 1)
    s.run()
    s.out(1)
    s.unifyc(0, KEY)
    s.run()
    s.out(1)

    # V is bound to W first: the goal wakes, finds W through V and
    # suspends again; W is bound and it finishes
    s.label('chain')
    s.newvar(0)
    s.newvar(1)
    goal(0, 1)
    s.run()
    s.out(1)
    s.newvar(2)
    s.unify(0, 2)
    s.run()
    s.out(1)
    s.unifyc(2, KEY)
    s.run()
    s.out(1)

    # two goals wait on one V
    s.label('two')
    s.newvar(0)
    s.newvar(1)
    goal(0, 1)
    s.newvar(2)
    goal(0, 2)
    s.run()
    s.out(1)
    s.unifyc(0, KEY)
    s.run()
    s.out(1)
    s.out(2)
    return s


def main(argv):
    s = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    ok, _m = driver.compare(s, sys.stdin, 'pimm lockstep jtoa', PINNED)
    if not ok:
        return 1
    print('pimm lockstep jtoa: PASS (convert_element/2 from the IPL image on the '
          'Bluespec core: %d goals and scenarios, %d trace lines identical to the '
          'reference model)' % (s.counts['parts'], s.counts['lines']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
