#!/usr/bin/env python3
"""Lockstep: system_timer and set_timer, the model's clock advancing.

    python3 ref/pimm/lockstep_timer.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_timer.py compare
    python3 ref/pimm/lockstep_timer.py --reference       the reference alone

system_timer(^X1, ^X2), 23:78 r_r, a guard with no input
(library/compiler/blt.kl1:287-288): "The upper 16 bits of the time (in
1/16 msec units) that has passed since the processor on which this
predicate is running was booted is unified with X1, and the lower 32
bits are unified with X2.  Suspend, Exception: None" (PIMOS manual,
e-builtin.tex:1537-1549).  VPIM gives X1 = 0 and X2 the current time
(src/interpreter/klb_pimos.psl.c kblt_system_timer).  THE CLOCK
(2026-11-24; it stood at 0 before): one tick every 423 instructions
executed, counted before the instruction that reads it (pimm.py
INSTRUCTIONS_PER_TICK: 615 KLIPS on append, M92 p. 425, at this image's
11 instructions an append reduction; equal cost per instruction is
OURS), 48 bits.

set_timer(Time, ^Wakeup), 22:FF r_r, a body built-in, Time the input
(blt.kl1:702-704).  VPIM's account (the comment before
kblt_system_timer): if the time asked for (a system timer value) has
come, Wakeup is unified at once with the timer's value, else at the
earliest time after (so Wakeup is now, the timer's low 32 bits); "T2 is after T1 :- T2 &- T1 < 2^(W-1)", &-
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
                 (These two parts run fewer than 423 instructions:
                 the clock is still 0.)
  later          (2026-11-24) the image's append/3 (scsi_fep_module)
                 over a list of 107 integers, ~1,180 instructions
  system_timer, later   the same four cells: X1 = 0, X2 = the
                 instructions before it (counted in the trace) // 423
                 = 2 (1,204 // 423; 1,204 // 400 would be 3)
  set_timer, later      Time 1, reached: Wakeup = now, 2, not 1.
                 Pins 2 parts / 166 lines -> 5 / 2805, these parts'
                 lines; the first two unchanged.
  alarm          (R8, 2026-11-25) set_timer to a time still to come,
                 now + 3 ticks (now the reference's clock when the
                 script is made, nothing runs between): Wakeup W1 is
                 left unbound, the alarm armed
  alarm: again   set_timer to now + 5: the alarm already armed is
                 cancelled, its W1 bound to [] (VPIM kblt_b_set_timer:
                 "unify old wakeup variable with []"), W2 unbound
  alarm: fired   the bench's ALARM (nothing to run): the clock moved on
                 to the alarm's time, and the run's first goal switch
                 binds W2 to the timer's low 32 bits, which is the
                 time asked for (VPIM f_WakeupGoalByAlarmClock binds
                 the time of the interrupt); the goal waiting on W2
                 (the image's ipl_pool:hash(W2, H, NewX)) is woken
                 then and gives H, and no goal is left waiting
                 Pins 5 parts / 2805 lines -> 8 / 2939, these parts'
                 lines; the first five unchanged.
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
  (2026-11-24, the clock advancing)
  the clock stands still            system_timer, later, line 16: R 3 0
                                    for 2
  a tick every 400 instructions     system_timer, later, line 16: R 3 3
                                    for 2
  set_timer answers the time asked  set_timer, line 35 (as above)
NOT run: a time still to come (refused), a non-integer Time.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402

PINNED = dict(parts=8, lines=2939)
TIMER_AT = []
ALARM_AT = []          # the two times asked for, as the script made them
I = lambda v: (pimm.INT, v & 0xffffffff)           # noqa: E731
KLB = 0x23
REACHED = (0, -1, -16, -2147483647)
LATE = -5
LONG = 107
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
    s.timer_code = at
    TIMER_AT[:] = [at]
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
    # the clock advances (2026-11-24): the image's append/3
    # (scsi_fep_module, 11 instructions an element) over a list of
    # LONG integers, then system_timer again on the same four cells,
    # then set_timer to time 1, reached: Wakeup is now, not 1
    s.label('later')
    s.setslot(4, pimm.NIL)
    for k in range(LONG):
        a, b = (5, 4) if k % 2 == 0 else (4, 5)
        s.cons(a, 6, I(k), ('slot', b))
    lst = 5 if LONG % 2 else 4
    s.newvar(8)
    s.arg(1, lst)
    s.argc(2, pimm.NIL)
    s.arg(3, 8)
    s.spawn(pimm.predicate(pimm.kbndis.Image(), 'scsi_fep_module', 'append/3'), 3)
    s.run()
    s.label('system_timer, later')
    s.newvar(0)
    s.newvar(1)
    s.arg(1, 0)
    s.arg(2, 1)
    s.spawn(s.timer_code, 2)
    s.run()
    s.out(0)
    s.out(1)
    s.label('set_timer, later')
    s.argc(1, I(1))                     # a time reached, before now
    s.newvar(2)
    s.arg(2, 2)
    s.spawn(stub, 2)
    s.run()
    s.out(2)
    # the alarm (R8): a time still to come, armed; again, the first
    # Wakeup bound to []; the clock moved on, the second bound to it
    s.label('alarm')
    t1 = (s.live().timer() + 3) & 0xffffffff
    s.argc(1, I(t1))
    s.newvar(3)
    s.arg(2, 3)
    s.spawn(stub, 2)
    s.run()
    s.out(3)
    s.label('alarm: again')
    t2 = (s.live().timer() + 5) & 0xffffffff
    ALARM_AT[:] = [t1, t2]
    s.argc(1, I(t2))
    s.newvar(4)
    s.arg(2, 4)
    s.spawn(stub, 2)
    s.run()
    s.out(3)
    s.out(4)
    # a goal waiting on W2: the image's ipl_pool:hash(W2, H, NewX)
    s.newvar(5)
    s.newvar(6)
    s.arg(1, 4)
    s.arg(2, 5)
    s.arg(3, 6)
    s.spawn(pimm.predicate(pimm.kbndis.Image(), 'ipl_pool', 'hash/3'), 3)
    s.run()
    s.label('alarm: fired')
    s.alarm()
    s.run()
    s.out(4)
    s.out(5)
    return s


def clock_at(parts, label, addr):
    """The clock as the source of the rule gives it (pimm.py
    INSTRUCTIONS_PER_TICK): the instructions before the first one at
    addr in part `label`, counted over the parts in the order run."""
    n = 0
    for lab, lines in parts.items():
        for ln in lines:
            if ln.startswith('I '):
                if lab == label and ln.startswith('I %d ' % addr):
                    return n // pimm.INSTRUCTIONS_PER_TICK
                n += 1
    return None


def check(m, outs, parts):
    bad = []
    t = clock_at(parts, 'system_timer, later', TIMER_AT[0])
    w = clock_at(parts, 'set_timer, later', m.stubs['set_timer']['addr'])
    got = {k: [m.term(w) for lab, w in outs if lab == k]
           for k in ('system_timer, later', 'set_timer, later')}
    if not t or got['system_timer, later'] != [0, t]:
        bad.append(('system_timer, later', got['system_timer, later'], t))
    if got['set_timer, later'] != [w]:
        bad.append(('set_timer, later', got['set_timer, later'], w))
    for k, want in EXPECT.items():
        if k.endswith('later'):
            continue
        got = [None if m.unbound(m.deref(w)) else m.term(w) for lab, w in outs if lab == k]
        if got != want:
            bad.append((k, got, want))
    at = 'I %d ' % m.stubs['set_timer']['addr']
    n = sum(ln.startswith(at) for ln in parts.get('set_timer', []))
    if n != len(REACHED) + 2:
        bad.append(('the stub taken %d times' % n,))
    got = {k: [None if m.unbound(m.deref(w)) else m.term(w) for lab, w in outs if lab == k]
           for k in ('alarm', 'alarm: again', 'alarm: fired')}
    # read at the end: W1 [], W2 the time asked for
    t2 = pimm.signed(ALARM_AT[1])
    want = {'alarm': [[]], 'alarm: again': [[], t2]}
    for k in want:
        if got[k] != want[k]:
            bad.append((k, got[k], want[k]))
    # W2 was unbound until the fire: hash/3's goal on it is woken (a W
    # line) in `alarm: fired` and in no part before, and gives H
    woke = [lab for lab, lines in parts.items() for ln in lines
            if ln[0] == 'W' and lab.startswith('alarm')]
    if woke != ['alarm: fired'] or got['alarm: fired'][0] != t2 or \
            not isinstance(got['alarm: fired'][1], int):
        bad.append(('alarm: fired', got['alarm: fired'], woke))
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
          'trace lines identical to the reference model: the clock at 0 and then 2 ticks '
          'after 1,204 instructions; '
          'set_timer to a time reached wakes at once with 0, and waits for its input)'
          % s.counts['lines'])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
