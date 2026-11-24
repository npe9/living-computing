#!/usr/bin/env python3
"""Lockstep: system_timer and set_timer, the model's clock at 0.

    python3 ref/pimm/lockstep_timer.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_timer.py compare
    python3 ref/pimm/lockstep_timer.py --reference       the reference alone

system_timer(^X1, ^X2), 23:78 r_r, a guard with no input
(library/compiler/blt.kl1:287-288): "The upper 16 bits of the time (in
1/16 msec units) that has passed since the processor on which this
predicate is running was booted is unified with X1, and the lower 32
bits are unified with X2.  Suspend, Exception: None" (PIMOS manual,
e-builtin.tex:1537-1549).  VPIM gives X1 = 0 and X2 the current time
(src/interpreter/klb_pimos.psl.c kblt_system_timer).  THE CLOCK IS
OURS: no time passes on this model, it stands at 0, so X1 = 0, X2 = 0.

set_timer(Time, ^Wakeup), 22:FF r_r, a body built-in, Time the input
(blt.kl1:702-704).  VPIM's account (the comment before
kblt_system_timer): if the time asked for (a system timer value) has
come, Wakeup is unified at once with the timer's value, else at the
earliest time after; "T2 is after T1 :- T2 &- T1 < 2^(W-1)", &-
unsigned mod 2^W.  With the clock at 0 a time reached, (0 - Time) mod
2^32 < 2^31, gives Wakeup = 0; a time still to come is refused (it
would never come).  22:FF is ALSO modname_to_module in the PIMOS
assembler's table (library/assembler/inst_tab.kl1:371 and 373, both
r_r): the bits are one instruction on the machine; both models take it
as set_timer, which is what the source of the site pim:go/4 reaches
says (bios/boot/sysTman.kl1 create/3, `system_timer(_,NowL) |
set_timer(NowL,W)`).  That was the stop of pim:go/4 with the device
(rung S0): system_timer_manager:create/3, then set_timer.

Parts:
  system_timer   on four cells of code the bench writes (as
                 lockstep_prio.py runs current_node):
                     p(X, Y) :- system_timer(X, Y).
                 system_timer 2, 3; get_value 2, 0; get_value 3, 1;
                 proceed: X = 0, Y = 0
  set_timer      at its stub, Time 0, -1, -16, -2147483647 (all
                 reached): Wakeup 0 each; then Time unbound: the
                 built-in waits, and answers 0 when Time = -5.
The real sites are in pimm_bios360E.sav (96,474 words; sysTman
create/3 and physical_alarm_timer_device's do_set_alarm/4 and
check_and_set_alarm/6) and each goes on into a module that file does
not hold (an external call the lockstep bench cannot play): NOT run.

Observed fault injections into the Bluespec (bsv/PimmStages.bsv), each
run alone (bsv/run_pimm_lockstep.sh timer) and restored from a copy,
2026-11-24:
  system_timer X2 = 1               system_timer, line 24: R 3 1 for 0
  system_timer X1 written to r[y]   system_timer, line 23: R 3 for R 2
  set_timer Wakeup = Time           set_timer, line 35: R 2 ffffffff
                                    for 0 (Time -1)
NOT run: a time still to come (refused), a non-integer Time.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402

PINNED = dict(parts=2, lines=166)
I = lambda v: (pimm.INT, v & 0xffffffff)           # noqa: E731
KLB = 0x23
REACHED = (0, -1, -16, -2147483647)
LATE = -5
# the outputs as they end (the waiting one is bound by then); the wait
# itself is checked by the stub taken twice for it
EXPECT = {'system_timer': [0, 0], 'set_timer': [0] * len(REACHED) + [0, 0]}


def script():
    stubs = pimm.Machine().stubs
    s = driver.Script()
    s.label('system_timer')
    code = [(KLB, 0x78 << 24 | 2 << 16 | 3 << 8),     # system_timer 2, 3
            (KLB, 0xbc << 24 | 2 << 16 | 0 << 8),     # get_value 2, 0
            (KLB, 0xbc << 24 | 3 << 16 | 1 << 8),     # get_value 3, 1
            (KLB, 0x60 << 24)]                        # proceed
    s.vector(15, 8, code)
    m = s.live()
    at = s.live_slot[15][1] - m.load
    assert [m.opname(at + i) for i in range(4)] == [
        'system_timer', 'get_value', 'get_value', 'proceed']
    s.newvar(0)
    s.newvar(1)
    s.arg(1, 0)
    s.arg(2, 1)
    s.spawn(at, 2)
    s.run()
    s.out(0)
    s.out(1)
    s.label('set_timer')
    stub = stubs['set_timer']['addr']
    for v in REACHED:
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
    return s


def check(m, outs, parts):
    bad = []
    for k, want in EXPECT.items():
        got = [None if m.unbound(m.deref(w)) else m.term(w) for lab, w in outs if lab == k]
        if got != want:
            bad.append((k, got, want))
    at = 'I %d ' % m.stubs['set_timer']['addr']
    n = sum(ln.startswith(at) for ln in parts.get('set_timer', []))
    if n != len(REACHED) + 2:
        bad.append(('the stub taken %d times' % n,))
    if m.nsusp:
        bad.append(('%d goals left waiting' % m.nsusp,))
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
        print(bad, n, len(kept))
        return 1 if bad else 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep timer', PINNED)
    if not ok:
        return 1
    bad = check(m, s.outs, kept)
    if bad:
        print('pimm lockstep timer: FAIL %r' % (bad[:3],))
        return 1
    print('pimm lockstep timer: PASS (system_timer and set_timer on the Bluespec core, %d '
          'trace lines identical to the reference model: the clock at 0, X1 = X2 = 0; '
          'set_timer to a time reached wakes at once with 0, and waits for its input)'
          % s.counts['lines'])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
