#!/usr/bin/env python3
"""Lockstep: current_node and calculate_priority_from_current.

    python3 ref/pimm/lockstep_prio.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_prio.py compare
    python3 ref/pimm/lockstep_prio.py --reference       the reference alone

current_node(^NodeNumber, ^TotalNode), 22:EE r_r (PIMOS library/
assembler/inst_tab.kl1, library/compiler/blt.kl1:655: two outputs, no
input).  "The node number will be a value between 0 and (TotalNode -
1) inclusive" (PIMOS manual, e-builtin.tex current_node).  One node
here: 0 and 1 (OURS; PDSS gives the same, emulator/blt_system.c
blt_b_current_node).  Its sites in the image are top:go1/4 (cell
17391), which goes on to supply_atom_number, and exception_table:
translate/2,4, which go on to current_processor; neither is modelled
at this commit, so it is run on four cells of code the bench writes:

    p(X, Y) :- current_node(X, Y).      current_node 2, 3; get_value 2, 0;
                                        get_value 3, 1; proceed

calculate_priority_from_current(X, ^Y), 22:EC r_r, X in -4096..4096
(manual, e-builtin.tex).  The manual gives no formula; PDSS's
(emulator/blt_system.c blt_b_rltv) with the range 0..4096 (OURS, as
calculate_priority_from_minimum's) and the current priority at the
top of it, 4096 (OURS; PDSS starts a shoen's goals at its maximum,
emulator/shoen.c:100,166): Y = 4096 + X for X < 0, 4096 for X >= 0.
Run at the image's site, shoen:execute/7 (cell 15515):

    execute(Code, Argv, Min, Max, Mask, Control, Report) :- integer(Min),
        0 =< Min =< 4096, integer(Max), 0 =< Max =< 4096, Max >= Min |
        calculate_priority_from_current(H, I), H := Min - 4096,
        calculate_priority_from_current(K, L), K := Max - 4096,
        create_shoen(I, L, Mask, Code, Argv, Raw, Shoen), ...

where each built-in is met with its input unbound and so becomes a
goal of its stub, woken when the subtraction binds it (the object
code: asm/kl1decomp.py shoen).  create_shoen drops the priorities
(stage 1), so what is checked is the value the stub writes to its
output register, read from the trace: Min and Max back.  And at the
stub with the bench's own inputs, the ends and the middle of the
range, one input bound late.

Parts and what each must leave (written from the formula above
before the first run):
  node        X, Y unbound: 0, 1; then X = 0, Y = 1 given: succeeds
              (Z, bound by the bench after the goal, prints 7)
  stubs       X = -4096, -4095, -1, 0, 1, 4095, 4096, -100 give 0, 1,
              4095, 4096, 4096, 4096, 4096, 3996; X bound late to
              -1000 gives 3096 (the variable is printed before and
              after; the value is read at the end, so both show 3096;
              that it waited is checked by the stub's instruction
              being taken twice)
  execute/7   Min 100, Max 200 on jis_to_ascii:convert/2 of "abc" in
              a shoen: the stub writes 200, then 100 (the goal
              woken last runs first: the ready queue is newest
              first, as found on the first run); the goal gives
              "abc", the report [started, terminated | _]
At the end two goals wait: execute/7's control/2 on its open Control
and report/2 on the raw report's open tail.

Observed fault injections into the Bluespec, 2026-11-23, each run
alone (bsv/run_pimm_lockstep.sh prio) and restored from a copy:
  current_node: TotalNode 2          node, line 24: R 3 2 for 1
  current_node: NodeNumber 1         node, line 23: R 2 1 for 0
  from_current: the range test       stubs, line 14: X = -4096 refused
    unsigned (as _from_minimum's)
  from_current: X >= 0 not clamped   stubs, line 98: X = 1 gives 4097
  from_current: 4096 - X for X < 0   stubs, line 14: X = -4096 gives 8192
  from_current: Y = X                stubs, line 14: X = -4096 gives -4096
Six of six caught.

NOT caught: a value outside -4096..4096 (refused on both models, not
run); the formula for any priority but 4096 (there is no other).
Re-pinned at the merge with shoen stage 2 (2026-11-23), 1077 -> 1087
trace lines, both models still identical and every check passing.
Part 3 runs shoen:execute/7, and the only change merged under this
test is shoen stage 2, whose record has two more cells (SH_REDUCTIONS,
SH_REMOVE) and writes its reduction count at the end of each run; that
the 10 lines are those writes is expected, not counted line by line.
Re-pinned for shoen stage 3 (2026-11-23), 1087 -> 1089 trace lines, no
value changed: the shoen record has one more cell, SH_MASK, written at
create (1 shoen made: 1 lines), and start_shoen empties the parked
list, SH_GOAL := 0 (1 starts: 1 lines); counted on the reference's
trace (both writes, nothing else new).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import lockstep_cons as cons  # noqa: E402

PINNED = dict(parts=3, lines=1089)
I = lambda v: (pimm.INT, v & 0xffffffff)           # noqa: E731
KLB, BLT = 0x23, 0x22
TEXT = 'abc'
ABC = (8, [ord(c) for c in TEXT])
STUB_IN = (-4096, -4095, -1, 0, 1, 4095, 4096, -100)
LATE = -1000
EXPECT = {
    'node': [0, 1, 7],
    'stubs': [0, 1, 4095, 4096, 4096, 4096, 4096, 3996, 3096, 3096],
    'execute/7': [ABC, ('|', 'started', ('|', 'terminated', None))],
}
# the stub's output register at execute/7: Max first, its goal being
# woken last (the ready queue is newest first)
WROTE = [200, 100]
WAITING = 2


def script():
    im = pimm.kbndis.Image()
    stubs = pimm.Machine().stubs
    s = driver.Script()

    # 1. current_node on code of the bench (a vector's cells)
    s.label('node')
    code = [(BLT, 0xee << 24 | 2 << 16 | 3 << 8),     # current_node 2, 3
            (KLB, 0xbc << 24 | 2 << 16 | 0 << 8),     # get_value 2, 0
            (KLB, 0xbc << 24 | 3 << 16 | 1 << 8),     # get_value 3, 1
            (KLB, 0x60 << 24)]                        # proceed
    s.vector(15, 8, code)
    m = s.live()
    at = s.live_slot[15][1] - m.load
    assert [m.opname(at + i) for i in range(4)] == [
        'current_node', 'get_value', 'get_value', 'proceed']
    s.newvar(0)
    s.newvar(1)
    s.arg(1, 0)
    s.arg(2, 1)
    s.spawn(at, 2)
    s.run()
    s.out(0)
    s.out(1)
    s.argc(1, I(0))
    s.argc(2, I(1))
    s.spawn(at, 2)
    s.run()
    s.newvar(2)
    s.unifyc(2, I(7))
    s.out(2)

    # 2. calculate_priority_from_current at its stub
    s.label('stubs')
    stub = stubs['calculate_priority_from_current']['addr']
    for v in STUB_IN:
        s.argc(1, I(v))
        s.newvar(0)
        s.arg(2, 0)
        s.spawn(stub, 2)
        s.run()
        s.out(0)
    s.newvar(1)
    s.newvar(0)
    s.arg(1, 1)
    s.arg(2, 0)
    s.spawn(stub, 2)
    s.run()
    s.out(0)
    s.unifyc(1, I(LATE))
    s.run()
    s.out(0)

    # 3. the image's shoen:execute/7
    s.label('execute/7')
    s.argc(1, (pimm.MOD, im.load + [x for x in im.mods if x['name'] == 'jis_to_ascii'][0]['addr'] + 1))
    names = {name: n for n, name in im.sym.items()}
    s.argc(2, (pimm.ATOM, names['convert']))
    s.argc(3, I(2))
    s.newvar(0)
    s.arg(4, 0)
    s.spawn(stubs['predicate_to_code']['addr'], 4)
    s.run()
    s.string(1, 16, cons.jis(TEXT))
    s.vector(2, 4, [('slot', 1), None])             # A in slot 5
    s.cons(3, 6, (pimm.ATOM, names['start']), None)
    s.newvar(8)
    s.arg(1, 0)
    s.arg(2, 2)
    s.argc(3, I(100))
    s.argc(4, I(200))
    s.argc(5, I(-1))
    s.arg(6, 3)
    s.arg(7, 8)
    s.spawn(pimm.predicate(im, 'shoen', 'execute/7'), 7)
    s.run()
    s.out(5)
    s.out(8)
    return s


def wrote(m, lines):
    """The values calculate_priority_from_current's stub wrote to its
    output register (r2: asm/pimm_stubs.py), from the trace."""
    at = 'I %d ' % m.stubs['calculate_priority_from_current']['addr']
    out = []
    for i, ln in enumerate(lines):
        if ln.startswith(at):
            for nx in lines[i + 1:]:
                if nx.startswith('I '):
                    break
                if nx.startswith('R 2 '):
                    out.append(pimm.signed(int(nx.split()[2][2:], 16)))
    return out


def check(m, outs, parts):
    bad = []
    for k, want in EXPECT.items():
        got = [None if m.unbound(m.deref(w)) else m.term(w) for lab, w in outs if lab == k]
        if got != want:
            bad.append((k, got, want))
    # the late input: the stub's instruction taken twice, the first
    # time making the goal that waits
    at = 'I %d ' % m.stubs['calculate_priority_from_current']['addr']
    n = sum(ln.startswith(at) for ln in parts.get('stubs', []))
    if n != len(STUB_IN) + 2:
        bad.append(('the stub taken %d times' % n,))
    got = wrote(m, parts.get('execute/7', []))
    if got != WROTE:
        bad.append(('execute/7: the stub wrote', got, WROTE))
    if m.nsusp != WAITING:
        bad.append(('%d goals left waiting, expected %d' % (m.nsusp, WAITING),))
    return bad


def main(argv):
    s = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    kept = {}
    play = s.play

    def keeping():
        for what, lines in play():
            kept[what] = lines
            yield what, lines
    s.play = keeping
    if '--reference' in argv:
        n = sum(len(v) for _k, v in s.play())
        bad = check(s.machine, s.outs, kept)
        print(bad, n)
        return 1 if bad else 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep prio', PINNED)
    if not ok:
        return 1
    bad = check(m, s.outs, kept)
    if bad:
        print('pimm lockstep prio: FAIL %r' % (bad[:3],))
        return 1
    print('pimm lockstep prio: PASS (current_node and calculate_priority_from_current on the '
          'Bluespec core, %d trace lines identical to the reference model: one node, 0 of 1; '
          'the priority from the current at its stub and at shoen:execute/7, where it waits '
          'for its input and gives Min and Max back)' % s.counts['lines'])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
