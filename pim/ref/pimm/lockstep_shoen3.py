#!/usr/bin/env python3
"""Lockstep: the shoen, stage 3: the exception path, stop and abort.

    python3 ref/pimm/lockstep_shoen3.py --script FILE    write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_shoen3.py compare
    python3 ref/pimm/lockstep_shoen3.py --reference      the reference alone:
                                                         the value checks, the
                                                         trace length

Stage 3 of the shoen (stages 1, 2: lockstep_shoen.py, lockstep_shoen2.py):
a goal's reduction failure inside a shoen and raise (22:F2) reported
as the exception message, stop_shoen (22:E2) with start after stop,
abort_shoen (22:E3), and current_processor (22:EB), which the image's
exception_table:translate/4 calls.  Everything runs through the
IMAGE'S OWN code: shoen:execute/4 and execute/7, control/2, report/2,
which hands {2, Kind, Info, NewCode, NewArgv} to exception_table:
translate/4 (current_node, current_processor, set_vector_element on
Info's element 0, translate1/4: 9 -> reduction_failure, 16 -> raised),
shoen:raise/3 and ground_term/2, and the three monitors, whose
exception clause prints the kind and Info and answers NewCode = their
dummy/2 (get_dummy_code/1: put_structured_constant module#M,
predicate_to_code) and NewArgv = {{Kind, Info}, Shut};
top:top_level_monitor/4's first clause sends `abort` when its third
argument is bound, and every monitor answers `aborted` with [].

Where each thing comes from (docs/pimm_semantics.md "Shoen"):
  PIM/m-sourced   the encodings and directions (inst_tab.kl1:334-351,
                  blt.kl1:537-552); the message {2, Kind, Info, NewCode,
                  NewArgv}, 1 aborted, 11 stopped (pimos.vmac:177-199,
                  the image's report/2); Kind the firmware's exception
                  number, 9 reduction_failure, 16 raised (pimos.vmac:
                  331-349), and the firmware's Info {Pe, Code, ArgV} and
                  {Pe, Info, Data} (kernel/builtin/excpt_tbl.kl1,
                  "FIRMWARE FORMAT", the 1992 PIM/m translator; the
                  image's translate/4 reads element 0 as Pe); the tag
                  1 << (16 + n) of exception n (manual e-shoen.tex, the
                  tag table) and the mask rule, the innermost shoen whose
                  mask AND the tag is not 0 (e-shoen.tex:57); the
                  replacement of the failing goal (or of raise) by the
                  goal NewCode/NewArgv, the shoen not terminating until
                  the handler binds them (e-shoen.tex:59-60, 773); start
                  restarting a stopped shoen, abort final, `terminated`
                  after `aborted` (e-shoen.tex:136-158, 212-218).
  carried over    from VPIM (f_reduce_exception_handler.psl.c
                  f_Failure_Sub, f_Raise_Sub): NewCode, NewArgv made
                  first, the goal apply(NewCode, NewArgv) enqueued in
                  the current shoen, then Info, then the report; raise
                  waits for Tag only (klb_body_blt_shoen.psl.c
                  kblt_b_raise); stopped/aborted reported before the
                  state changes, stop and abort of a terminated shoen
                  only reporting (f_shoen_control.psl.c:392-530); from
                  PDSS (goal.c:302-335): a goal of an aborted shoen
                  discarded, one of a stopped shoen parked, when taken
                  from the ready queue; current_processor = 0, 1, 1
                  (blt_system.c).
  OURS            Pe = 0; the failing goal's Code its predicate's entry
                  (the suspend's label) and ArgV r[0..arity); a failure
                  counted as one reduction; the record's SH_MASK cell and
                  the parked list in SH_GOAL; the check at every pickup
                  inside a shoen (a walk up the parents); an aborted
                  shoen TERMINATED at once (12 at once after 1, its
                  reductions and one off its parent's count then), its
                  inner shoen silent; abort of the goal's own shoen or
                  one above refused; an exception no shoen accepts
                  refused.

Fifteen parts, on a bare machine.  EXPECT gives what each leaves: the
values printed (Report streams, the monitors' Control and Shut), the
console, and every shoen's (count, status, parent, remove cell, mask)
from its record.  The values the test does NOT take from a model: the
codes (close_fep/2, ipl:dummy/2, top:dummy/2 from the image's
predicate table), ArgV and Data (what the bench gave), control/2's
message (its text, decoded from JIS), statistics(H, L) (counted on the
trace: one per execute, execute_external, `E done` AND `E fail`), the
reduction cells (the same count; a child's only if it terminated).
EXPECT was written from the design rules after the reference model's
first run of the script (so it is not a blind prediction); the
Bluespec matched the reference on ITS first run, all fourteen parts,
7092 lines (the fifteenth, below, was added after the injections, and
matched on its first run too).  That the handler's goal belongs to the
failing goal's shoen, so that the shoen waits for it, is seen by the
trace only (the both-models injection below): the Report's order is
the same either way.
  failure         ipl:close_fep(shut, 0) in a shoen (no clause for an
                  atom), ipl_monitor: Report = [started,
                  exception(reduction_failure, {0, close_fep/2, {shut,
                  0}}, ipl:dummy/2, {{reduction_failure, ..}, shut}),
                  terminated, statistics_started, statistics(0, 10),
                  return_resource(0, 0)]; console "EXCEPTION WAS OCCURRED
                  in IPL : error code:", the atom, the vector, then the
                  statistics lines.
  failure, mask 1 << 25   the same through shoen:execute/7 at the root
                  (mask reduction_failure's bit alone), bios_monitor:
                  top:dummy/2; the record's mask 1 << 25.
  raise/3         shoen:raise(3, {shut, 1}, X) as the code: exception(
                  raised, {0, {shut, 1}, X}, ..), X unbound.
  raise in control/2   the outer's code execute/4, the inner's Control
                  [start, shut | C2]: control/2 (an outer goal) raises
                  512 with fatal_error("Illegal control message 〜q") and
                  `shut` on the OUTER's Report; both shoen end normally.
  stop            hash/3 suspended in a shoen; `stop`: [started,
                  stopped], status stopped; X bound: the woken goal is
                  PARKED (E park), H unbound, count still 1; `start`:
                  released (its W line), H = 7, terminated, the list 0.
  abort inner     the inner (hash/3 suspended) inside an outer, its
                  Control bound to [abort]: the inner's Report [started,
                  aborted, terminated, return_resource(0, 0)] (control/2
                  then removes it), the OUTER's count from 3 to 0 and the
                  outer terminated; X bound after: the woken goal is
                  DISCARDED (E aborted), H unbound.
  abort outer     the same nesting under top_level_monitor/4, its
                  trigger bound: the outer aborted, removed (aborted ->
                  [] -> remove_shoen), Shut = shut, the outer's count
                  left at 3; the inner still `started` with count 1, its
                  Report [started | _]; X and its Control bound after:
                  the inner's goal and the inner's control/2 (a goal of
                  the outer) both discarded.
  raise/3, tag 3, mask 1   raise/3 again, Tag 3, under execute/7 with
                  mask 1: the manual's rule (1 AND 3 is not 0) takes it,
                  VPIM's (mask AND tag = tag) would refuse.
Five goals are left waiting (WAITING, by hand).

Observed fault injections into the Bluespec, 2026-11-23, one at a time
in a private copy of pim/ (the restore is the copy; the clean copy then
PASSED), `bsv/run_pimm_lockstep.sh shoen3`, the first difference:
  the handler's apply goal not counted   part 0 (failure), line 197: the
                                         count's write missing
  Info's Pe 1                            failure, line 200: M .. 1 for 0
  ArgV from r1 on                        failure, line 198
  Code one cell on                       failure, line 201: ..2151 for ..2150
  Kind 10 for 9                          failure, line 204
  NewCode and NewArgv swapped            failure, line 206
  a failure not counted as a reduction   failure, line 213: the reductions cell
  stop leaves the status started         part 5 (stop: stopped), line 28
  start leaves the parked list           failure, line 142 (every start
                                         writes the 0)
  a stopped shoen's goal not parked      part 6, line 10: the goal runs
  an aborted shoen's goal not discarded  part 10, line 10: the goal runs
  abort only reports                     part 9, line 29
  abort leaves the parent's count        part 9, line 34
  abort reports 12 for 1                 part 9, line 22
  raise waits for Info and Data too      part 2 (raise/3), line 461
  current_processor's first output 1     failure, line 331
  the mask not kept (0 written)          failure, line 83
NOT caught (the Bluespec PASSED all 7092 lines of the fourteen parts
then):
  - VPIM's mask rule (accept only if mask AND tag = tag) for the
    manual's (not 0): every tag was one bit.  The fifteenth part was
    added for it, and with it the injection FAILS: part 14 (raise/3,
    tag 3, mask 1), line 611, `E unimp` for the message's first write
    (re-run 2026-11-23; on the reference the same rule stops the model,
    `an exception (tag 3) no shoen accepts`); not reading the mask
    still PASSED all 8375 lines then;
  - NOT READING the mask at all (the current shoen always taking the
    report): every exception's own shoen accepts it; a shoen that
    refuses it needs execute/7 inside a shoen, an apply of 7
    arguments, over the bench's 6 (not run);
  - start releasing only the first parked goal: one goal is parked.
Wrong rules in BOTH models (the reference alone, --reference, the
value checks; each in a private copy):
  Pe 1                       caught (the Report's Info)
  a failure not a reduction  caught (statistics(0, 8) for (0, 10))
  VPIM's mask rule           NOT caught by the fourteen parts; caught,
                             loudly, with the fifteenth (as above)
  the outermost accepting    NOT caught (no part has two accepting
  shoen, not the innermost   shoen on the chain of the failing goal)
  abort without terminated   caught (the Reports)
  a stopped shoen runs on    caught, loudly: the shoen ends while
                             stopped and the later start is refused
  the handler's goal made    NOT caught by the values: only the pinned
  in the root, not in the    length (6960 for 7092, fourteen parts) sees it; the
  failing goal's shoen       shoen then ends before its handler runs,
                             but the Report's order is the same.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import lockstep_cons as cons  # noqa: E402
import lockstep_shoen as stage1  # noqa: E402
import lockstep_shoen2 as stage2  # noqa: E402
import pimm_layout as L  # noqa: E402

PINNED = dict(parts=15, lines=8375)
I = lambda v: (pimm.INT, v & 0xffffffff)           # noqa: E731
STATUS = {L.DORMANT: 'dormant', L.STARTED: 'started', L.TERMINATED: 'terminated',
          L.REMOVED: 'removed', L.STOPPED: 'stopped'}


def script():
    im = pimm.kbndis.Image()
    names = {name: n for n, name in im.sym.items()}
    A = lambda n: (pimm.ATOM, names[n])            # noqa: E731
    stubs = pimm.Machine().stubs
    P = lambda m, p: pimm.predicate(im, m, p)      # noqa: E731
    execute4 = P('shoen', 'execute/4')
    ipl_monitor = P('ipl', 'ipl_monitor/3')
    bios_monitor = P('top', 'bios_monitor/3')
    top_monitor = P('top', 'top_level_monitor/4')

    def modobj(name):
        return (pimm.MOD, im.load + [x for x in im.mods if x['name'] == name][0]['addr'] + 1)

    s = driver.Script()

    def p2c(mod, name, arity, out):
        s.argc(1, modobj(mod))
        s.argc(2, A(name))
        s.argc(3, I(arity))
        s.newvar(out)
        s.arg(4, out)
        s.spawn(stubs['predicate_to_code']['addr'], 4)
        s.run()

    def goal(pc, *slots):
        for i, k in enumerate(slots):
            s.arg(i + 1, k)
        s.spawn(pc, len(slots))

    def code(mod, pred, slot):
        s.setslot(slot, (pimm.COD, im.load + P(mod, pred)))

    # (a) a reduction failure in a shoen: ipl:close_fep(shut, 0) has no
    # clause for an atom; ipl:ipl_monitor/3 at the root answers the
    # exception with ipl:dummy/2 and {{Kind, Info}, Shut}
    s.label('failure')
    code('ipl', 'close_fep/2', 0)
    s.vector(2, 4, [A('shut'), I(0)])
    s.cons(3, 6, A('start'), None)                 # C in 7
    s.newvar(8)                                    # Report
    goal(execute4, 0, 2, 3, 8)
    s.newvar(9)                                    # Shut
    goal(ipl_monitor, 8, 7, 9)
    s.run()
    for k in (8, 7, 9):
        s.out(k)

    # (b) the same through shoen:execute/7 at the root, mask 1 << 25
    # (reduction_failure's bit alone), priorities 0..4096; the monitor
    # top:bios_monitor/3, which answers with top:dummy/2
    s.label('failure, mask 1 << 25')
    code('ipl', 'close_fep/2', 0)
    s.vector(2, 4, [A('shut'), I(0)])
    s.cons(3, 6, A('start'), None)                 # C in 7
    s.newvar(8)                                    # Report
    s.setslot(10, I(0))
    s.setslot(11, I(4096))
    s.setslot(12, I(1 << 25))
    goal(P('shoen', 'execute/7'), 0, 2, 10, 11, 12, 3, 8)
    s.newvar(9)                                    # Shut
    goal(bios_monitor, 8, 7, 9)
    s.run()
    for k in (8, 9):
        s.out(k)

    # (c) the image's own raise/3 as a shoen's code: raise(3, {shut, 1},
    # X), X unbound: ground_term waits for nothing (Info is ground), the
    # built-in raise(3, Info', X); bios_monitor answers
    s.label('raise/3')
    code('shoen', 'raise/3', 0)
    s.vector(1, 4, [A('shut'), I(1)])
    s.newvar(6)                                    # X
    s.vector(2, 10, [I(3), ('slot', 1), ('slot', 6)])
    s.cons(3, 13, A('start'), None)                # C in 14
    s.newvar(8)                                    # Report
    goal(execute4, 0, 2, 3, 8)
    s.newvar(9)                                    # Shut
    goal(bios_monitor, 8, 14, 9)
    s.run()
    for k in (8, 9, 6):
        s.out(k)

    # (d) raise from the image's control/2: the outer shoen's code is
    # execute/4, the inner's (convert/2) Control [start, shut | C2]:
    # `shut` is no control message, so the inner's control/2, a goal of
    # the OUTER, raises 512 there; bios_monitor on each Report
    s.label('raise in control/2')
    p2c('jis_to_ascii', 'convert', 2, 0)
    s.string(1, 16, cons.jis('abc'))
    s.vector(2, 4, [('slot', 1), None])            # A in 5
    s.cons(6, 14, A('shut'), None)                 # C2 in 15
    s.cons(3, 11, A('start'), ('slot', 6))
    s.newvar(8)                                    # the inner Report
    p2c('shoen', 'execute', 4, 13)
    s.vector(4, 9, [('slot', 0), ('slot', 2), ('slot', 3), ('slot', 8)])
    s.cons(1, 6, A('start'), None)                 # the outer Control, C1 in 7
    s.newvar(2)                                    # the outer Report
    goal(execute4, 13, 4, 1, 2)
    s.newvar(10)                                   # the inner's Shut
    goal(bios_monitor, 8, 15, 10)
    s.newvar(11)                                   # the outer's Shut
    goal(bios_monitor, 2, 7, 11)
    s.run()
    for k in (5, 8, 2, 10, 11):
        s.out(k)

    # (e) stop: ipl_pool:hash/3 on an unbound X, Control [start | C]; the
    # bench then sends stop, binds X, sends start
    s.label('stop')
    code('ipl_pool', 'hash/3', 0)
    s.vector(2, 12, [None, None, None])            # X in 12, H in 13, NewX in 14
    s.cons(3, 6, A('start'), None)                 # C in 7
    s.newvar(8)                                    # Report
    goal(execute4, 0, 2, 3, 8)
    s.run()
    s.out(8)
    s.label('stop: stopped')
    s.cons(15, 4, A('stop'), None)                 # C' in 5
    s.unify(7, 15)
    s.run()
    s.out(8)
    s.label('stop: woken, parked')
    s.unifyc(12, I(-7))
    s.run()
    s.out(13)
    s.out(8)
    s.label('stop: started again')
    s.cons(14, 9, A('start'), None)
    s.unify(5, 14)
    s.run()
    s.out(13)
    s.out(8)

    # (f) abort of an inner shoen by its control stream: the outer's code
    # is execute/4, the inner's hash/3 on an unbound X, its Control
    # [start | C2]; the bench then binds C2 = [abort]
    s.label('abort inner')
    code('ipl_pool', 'hash/3', 0)
    s.vector(2, 12, [None, None, None])            # X in 12, H in 13
    s.cons(3, 10, A('start'), None)                # C2 in 11
    s.newvar(8)                                    # the inner Report
    p2c('shoen', 'execute', 4, 9)
    s.vector(1, 4, [('slot', 0), ('slot', 2), ('slot', 3), ('slot', 8)])
    s.cons(2, 5, A('start'), None)                 # the outer Control, C1 in 6
    s.newvar(3)                                    # the outer Report
    goal(execute4, 9, 1, 2, 3)
    s.run()
    for k in (8, 3):
        s.out(k)
    s.label('abort inner: aborted')
    s.cons(15, 4, A('abort'), pimm.NIL)
    s.unify(11, 15)
    s.run()
    for k in (8, 3):
        s.out(k)
    s.label('abort inner: woken')
    s.unifyc(12, I(-7))
    s.run()
    s.out(13)

    # (g) abort of an outer shoen by top:top_level_monitor/4, its third
    # argument bound: the outer's code is execute/4, the inner's hash/3
    # on an unbound X with Control [start | C2]
    s.label('abort outer')
    code('ipl_pool', 'hash/3', 0)
    s.vector(2, 12, [None, None, None])            # X in 12, H in 13
    s.cons(3, 10, A('start'), None)                # C2 in 11
    s.newvar(8)                                    # the inner Report
    p2c('shoen', 'execute', 4, 9)
    s.vector(1, 4, [('slot', 0), ('slot', 2), ('slot', 3), ('slot', 8)])
    s.cons(2, 5, A('start'), None)                 # the outer Control, C1 in 6
    s.newvar(3)                                    # the outer Report
    goal(execute4, 9, 1, 2, 3)
    s.newvar(10)                                   # the trigger
    s.newvar(15)                                   # Shut
    goal(top_monitor, 3, 6, 10, 15)
    s.run()
    s.out(3)
    s.label('abort outer: aborted')
    s.unifyc(10, I(1))
    s.run()
    for k in (3, 15, 8):
        s.out(k)
    s.label('abort outer: woken')
    s.unifyc(12, I(-7))
    s.unifyc(11, pimm.NIL)
    s.run()
    for k in (13, 8):
        s.out(k)

    # (h) raise/3 again, Tag 3 (two bits), in a shoen of execute/7 at
    # the root with mask 1: the manual's rule accepts (1 AND 3 is not 0),
    # VPIM's (mask AND tag = tag) would refuse
    s.label('raise/3, tag 3, mask 1')
    code('shoen', 'raise/3', 0)
    s.vector(1, 4, [A('shut'), I(1)])
    s.newvar(6)                                    # X
    s.vector(2, 10, [I(3), ('slot', 1), ('slot', 6)])
    s.cons(3, 13, A('start'), None)                # C in 14
    s.newvar(8)                                    # Report
    s.setslot(11, I(0))
    s.setslot(12, I(4096))
    s.setslot(15, I(1))
    goal(P('shoen', 'execute/7'), 0, 2, 11, 12, 15, 3, 8)
    s.newvar(9)                                    # Shut
    goal(bios_monitor, 8, 14, 9)
    s.run()
    for k in (8, 9, 6):
        s.out(k)
    return s


# ---- what each part must leave ------------------------------------------
def C(mod, pred):
    """A code object as Machine.term gives it, from the image's own
    table of predicates (not from the model)."""
    return ('COD', pimm.predicate(pimm.kbndis.Image(), mod, pred))


CLOSE_FEP = C('ipl', 'close_fep/2')
IPL_DUMMY, TOP_DUMMY = C('ipl', 'dummy/2'), C('top', 'dummy/2')
STATS = stage2.STATS
STREAM = stage1.stream
# the message shoen:control/2 raises with for `shut` (its otherwise
# clause: raise(512, fatal_error("Illegal control message 〜q"), A))
ILLEGAL = 'Illegal control message 〜q'


def exception(kind, info, code):
    """exception(Kind, Info, NewCode, NewArgv) as the monitors leave it:
    NewCode their dummy/2, NewArgv {{Kind, Info}, shut} (Shut is bound
    by the end: the image's ipl_monitor/3, bios_monitor/3)."""
    return ('exception', kind, info, code, ((kind, info), 'shut'))


def ended(i, *before):
    return ('started',) + before + ('terminated', 'statistics_started', STATS(i),
                                    ('return_resource', 0, 0))


FAIL_INFO = (0, CLOSE_FEP, ('shut', 0))            # {Node, Code, ArgV}
# (count, status, parent, SH_REMOVE, SH_MASK) of every shoen made so far
R0 = [(0, 'removed', None, 0, -1)]
R1 = R0 + [(0, 'removed', None, 0, 1 << 25)]
R2 = R1 + [(0, 'removed', None, 0, -1)]
R3 = R2 + [(0, 'removed', None, 0, -1), (0, 'removed', 3, 0, -1)]
STOP = lambda st, n=1: R3 + [(n, st, None, 0, -1)]   # noqa: E731
R5 = STOP('terminated', 0)
AB = lambda o, i: R5 + [o, i]                      # noqa: E731
R7 = AB((0, 'terminated', None, 0, -1), (1, 'removed', 6, 0, -1))
AO = lambda o, i: R7 + [o, i]                      # noqa: E731
EXPECT = [
    ('failure',
     [STREAM(*ended(0, exception('reduction_failure', FAIL_INFO, IPL_DUMMY)), closed=True),
      ['statistics'], 'shut'],
     ['EXCEPTION WAS OCCURRED in IPL : error code:', 'reduction_failure', 'vector',
      'Statistics in Resource:', STATS(0), 'SCSI-FEP END********'],
     R0),
    ('failure, mask 1 << 25',
     [STREAM(*ended(1, exception('reduction_failure', FAIL_INFO, TOP_DUMMY)), closed=True),
      'shut'],
     ['EXCEPTION WAS OCCURRED in BIOS : error code:', 'reduction_failure', 'vector'],
     R1),
    ('raise/3',
     [STREAM(*ended(2, exception('raised', (0, ('shut', 1), None), TOP_DUMMY)), closed=True),
      'shut', None],
     ['EXCEPTION WAS OCCURRED in BIOS : error code:', 'raised', 'vector'],
     R2),
    ('raise in control/2',
     [(8, [97, 98, 99]), STREAM(*ended(4), closed=True),
      STREAM(*ended(3, exception('raised', (0, ('fatal_error', ILLEGAL), 'shut'), TOP_DUMMY)),
             closed=True),
      'shut', 'shut'],
     ['EXCEPTION WAS OCCURRED in BIOS : error code:', 'raised', 'vector'],
     R3),
    ('stop', [STREAM('started')], [], STOP('started')),
    ('stop: stopped', [STREAM('started', 'stopped')], [], STOP('stopped')),
    ('stop: woken, parked', [None, STREAM('started', 'stopped')], [], STOP('stopped')),
    ('stop: started again', [7, STREAM('started', 'stopped', 'started', 'terminated')], [], R5),
    ('abort inner', [STREAM('started'), STREAM('started')], [],
     AB((3, 'started', None, 0, -1), (1, 'started', 6, 0, -1))),
    ('abort inner: aborted',
     [STREAM('started', 'aborted', 'terminated', ('return_resource', 0, 0), closed=True),
      STREAM('started', 'terminated')], [], R7),
    ('abort inner: woken', [None], [], R7),
    ('abort outer', [STREAM('started')], [],
     AO((3, 'started', None, 0, -1), (1, 'started', 8, 0, -1))),
    ('abort outer: aborted',
     [STREAM('started', 'aborted', 'terminated', ('return_resource', 0, 0), closed=True),
      'shut', STREAM('started')], [],
     AO((3, 'removed', None, 0, -1), (1, 'started', 8, 0, -1))),
    ('abort outer: woken', [None, STREAM('started')], [],
     AO((3, 'removed', None, 0, -1), (1, 'started', 8, 0, -1))),
    ('raise/3, tag 3, mask 1',
     [STREAM(*ended(10, exception('raised', (0, ('shut', 1), None), TOP_DUMMY)), closed=True),
      'shut', None],
     ['EXCEPTION WAS OCCURRED in BIOS : error code:', 'raised', 'vector'],
     AO((3, 'removed', None, 0, -1), (1, 'started', 8, 0, -1)) + [(0, 'removed', None, 0, 1)]),
]
# The goals left waiting, by hand: `stop` and `abort inner` leave their
# root shoen's control/2 and report/2 (no monitor closes them); `abort
# outer` the inner's report/2, a goal of the aborted outer that waits on
# the inner's report stream.  The goals discarded were woken first.
WAITING = 5
# the lines that say a goal was discarded or parked, per part
TAKEN = {'stop: woken, parked': ['E park'], 'abort inner: woken': ['E aborted'],
         'abort outer: woken': ['E aborted', 'E aborted']}


def jis_text(v):
    """A 16-bit string as text: JIS rows 21h (the space, the wave dash)
    and 23h (the letters), the only ones in ILLEGAL."""
    if isinstance(v, tuple) and len(v) == 2 and v[0] == 16:
        out = ''
        for c in v[1]:
            if c >> 8 == 0x23:
                out += chr(c & 0xff)
            else:
                out += {0x2121: ' ', 0x2141: '〜'}.get(c, '?')
        return out
    if isinstance(v, list):
        return [jis_text(x) for x in v]
    if isinstance(v, tuple):
        return tuple(jis_text(x) for x in v)
    return v


def console(lines, m):
    """display_console's values: an integer, a string's text, an atom's
    name, 'vector' for a vector (only its pointer is on the trace)."""
    out = []
    for x in stage2.console(lines, m):
        if isinstance(x, tuple):
            t, v = x
            if t & ~1 == pimm.ATOM:
                x = m.im.atom(v)
            elif pimm.VECT0 <= t & ~1 <= pimm.VECT0 + 14:
                x = 'vector'
        out.append(x)
    return out


def counted(m, lines):
    """stage 2's count of reductions on the trace, plus one for each
    `E fail` (a reduction failure ends its goal as a proceed would: the
    manual's dequeues and executes less suspensions); `E aborted` and
    `E park` add none."""
    own, cur, marks = {}, 0, []
    for ln in lines:
        if ln[0] == 'G':
            g = int(ln.split()[1])
            cur = m.mem[m.load + g + L.G_STATUS][1] >> 2
        elif ln in ('E done', 'E fail') or (ln[0] == 'I' and m.opname(int(ln.split()[1]))
                                            in ('execute', 'execute_external')):
            own[cur] = own.get(cur, 0) + 1
        marks.append(dict(own))
    return marks


def check(m, snaps, parts):
    bad = []
    if [k for k, _v, _c, _r in EXPECT] != list(snaps):
        return [('parts', list(snaps))]
    lines = [ln for k, _v, _c, _r in EXPECT for ln in parts[k]]
    known = stage1.handles(lines, m.load)
    stage2.counted = counted                      # the rule with E fail
    stats, own, total = stage2.expected_stats(m, lines, known)
    for k, vals, cons_, recs in EXPECT:
        got_vals, got_recs = snaps[k]
        want = stage2.fill(vals, stats, known)
        if jis_text(got_vals) != want:
            bad.append((k, 'values', jis_text(got_vals), want))
        c = console(parts[k], m)
        wantc = []
        for x in stage2.fill(cons_, stats, known):
            wantc += list(x[1:]) if isinstance(x, tuple) else [x]
        if c != wantc:
            bad.append((k, 'console', c, wantc))
        if got_recs != recs:
            bad.append((k, 'records', got_recs, recs))
        taken = [ln for ln in parts[k] if ln in ('E park', 'E aborted')]
        if taken != TAKEN.get(k, []):
            bad.append((k, 'discarded or parked', taken))
    # every statistic was printed, and the reduction cells: the trace's
    if sum(len(v) for v in stats.values()) != 6:
        bad.append(('statistics on the trace', stats))
    # (a child's total is added to its parent at its termination: the
    # inner shoen of `abort outer` never terminates, so its reductions
    # are in no parent's cell)
    ended_ = {a for a in known
              if m.mem[m.load + a + L.SH_STATUS][1] in (L.TERMINATED, L.REMOVED)}

    def total_t(a):
        par = lambda c: m.mem[m.load + c + L.SH_PARENT][1]   # noqa: E731
        return own.get(a, 0) + sum(total_t(c) for c in ended_ if par(c) == m.load + a)
    for a in known:
        if m.mem[m.load + a + L.SH_REDUCTIONS][1] != total_t(a):
            bad.append(('reductions of the shoen at %d' % a,
                        m.mem[m.load + a + L.SH_REDUCTIONS][1], total_t(a)))
    # the goal parked in `stop` is the one released by `stop: started
    # again`, and the parked list is empty after
    park = parts['stop: woken, parked']
    g = [ln for ln in park[:park.index('E park')] if ln[0] == 'G'][-1].split()[1]
    if 'W ' + g not in parts['stop: started again'] or m.mem[m.load + known[5] + L.SH_GOAL][1]:
        bad.append(('stop: the parked goal not released',))
    if m.nsusp != WAITING:
        bad.append(('%d goals left waiting, expected %d' % (m.nsusp, WAITING),))
    return bad


def snapshot(m, outs, known):
    vals = [None if m.unbound(w) else m.term(w) for w in outs]
    recs = []
    for a in known:
        sh = m.load + a
        parent = m.mem[sh + L.SH_PARENT][1]
        recs.append((pimm.signed(m.mem[sh + L.SH_COUNT][1]),
                     STATUS.get(m.mem[sh + L.SH_STATUS][1]),
                     known.index(parent - m.load) if parent else None,
                     m.mem[sh + L.SH_REMOVE][1], pimm.signed(m.mem[sh + L.SH_MASK][1])))
    return vals, recs


def main(argv):
    s = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    if '--dump' in argv:
        m = None
        for what, lines in s.play():
            m = s.machine
            print('==', what, len(lines))
            for k, w in s.outs:
                if k == what:
                    print('  ', m.term(w))
            for ln in lines:
                if ln[0] in 'GEWC' or ln.startswith('I') and m.opname(int(ln.split()[1])) in (
                        'raise', 'abort_shoen', 'stop_shoen', 'suspend', 'start_shoen'):
                    print('    ', ln, m.opname(int(ln.split()[1])) if ln[0] == 'I' else '')
        return 0
    kept, snaps, known = {}, {}, []
    play = s.play

    def keeping():
        for what, lines in play():
            kept[what] = lines
            for a in stage1.handles(lines, s.machine.load):
                if a not in known:
                    known.append(a)
            snaps[what] = snapshot(s.machine, [w for k, w in s.outs if k == what], known)
            yield what, lines
    s.play = keeping
    if '--reference' in argv:
        n = sum(len(v) for _k, v in s.play())
        bad = check(s.machine, snaps, kept)
        if n != PINNED['lines']:
            bad.append(('%d trace lines, pinned %d' % (n, PINNED['lines']),))
        print(bad, n)
        return 1 if bad else 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep shoen3',
                           dict(parts=PINNED['parts'], lines=PINNED['lines']))
    if not ok:
        return 1
    bad = check(m, snaps, kept)
    if bad:
        print('pimm lockstep shoen3: FAIL %r' % (bad[:3],))
        return 1
    print('pimm lockstep shoen3: PASS (the exception path, stop_shoen and abort_shoen on '
          'the Bluespec core, %d trace lines identical to the reference model)'
          % s.counts['lines'])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
