#!/usr/bin/env python3
"""Lockstep: the shoen, stage 1: create_shoen, start_shoen, termination.

    python3 ref/pimm/lockstep_shoen.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_shoen.py compare
    python3 ref/pimm/lockstep_shoen.py --reference       the reference alone:
                                                         the value checks, the
                                                         trace length

A shoen is PIMOS's unit of control: a set of goals with a control
stream in and a report stream out.  Stage 1 is create_shoen (22:E0),
start_shoen (22:E1) and the shoen's end, driven through the IMAGE'S
OWN shoen:execute/4 (cell 15550):

    execute(Code, Argv, Control, Report) :- true |
        create_shoen(0, -1, -1, Code, Argv, RawReport, Shoen),
        control(Control, Shoen), report(RawReport, Report).

so the consumers are the image's control/2 (cell 15727: [start|C]
calls start_shoen) and report/2 (cell 15818: 8 becomes `started`, 12
`terminated`).  The paths taken here do not reach put_console, which
report/2 uses only for a message it does not know.

Where each thing comes from (docs/pimm_semantics.md "Shoen"):
  PIM/m-sourced   the two encodings and operand directions (PIMOS
                  library/assembler/inst_tab.kl1:332-362, klb_opr.kl1:
                  144-154, library/compiler/blt.kl1:537-601); that
                  create_shoen's outputs are its input registers in
                  the image (cell 15553: 22:e0040506, 00:00010001);
                  the handle's tag 38h SHREC (debugger/inspector/
                  tagtbl.kl1); the report codes 8 and 12 (the image's
                  report/2; macro/pimos/pimos/pimos.vmac:177-199);
                  dormant until `start`, `terminated` at the end
                  (manual, e-shoen.tex:117-262).
  carried over    from PDSS and VPIM, the siblings, NOT PIM/m-sourced:
                  the count of a shoen's goals and child shoen and its
                  end at zero (PDSS emulator/emulate.c:340, shoen.c:
                  123-178, 280-309); the first goal an apply, parked
                  until start (PDSS dc_apply, goal.c:310-334); 8
                  before the state changes, 12 alone while the control
                  stream is open (VPIM functions/f_shoen_control.psl.c:
                  324-330, f_shoen_with_fp.psl.c:86).
  OURS            the shoen record and the goal's shoen in its status
                  cell (asm/pimm_layout.py); NewShoen = Shoen; the
                  priorities and the mask dropped; no resource, so 6
                  (resource_low) is never reported, which is probably
                  NOT what the machine did.

Eleven parts, on a bare machine.  EXPECT below says what each must
leave: the printed values, and for every shoen made so far its count,
status and parent read from its record in memory.  For the first
eight parts it was derived from the design by hand BEFORE the first
run and held on the first run of both models, but for three slips of
the test's own (the stub part's report is raw integers; the stream
the bench closes is not unbound; four, not five, shoen had been made
by execute/4).  The last three parts were added after: `unified
inside` was tried on the reference model first, and its H (the hash
of a vector) is not checked.
  run             Code = the code predicate_to_code gives for
                  jis_to_ascii:convert/2, Argv = {"abc" in JIS, A},
                  Control = [start|C], C unbound: A = "abc" (by
                  asm/psdpim.py's table, not the IPL's converter),
                  Report = [started, terminated | unbound]; the
                  record: count 0, terminated, no parent.
  dormant         Control unbound: A unbound, Report unbound, count
                  1, dormant; apply's stub is never taken.
  late start      Control = [start|_] now: as `run`.
  suspended       Code = ipl_pool:hash/3 on an unbound X: the goal
                  suspends INSIDE the shoen (+1, -1): Report =
                  [started | unbound], count 1, started.
  woken           the bench binds X = -7: H = 7, NewX = -7, Report =
                  [started, terminated | unbound], count 0.
  nested          the outer shoen's code is shoen:execute/4 itself
                  (a code from predicate_to_code), its Argv = {the
                  code of convert/2, {JIS, A}, [start|C2], Report2}.
                  Expected from the design: the outer's first goal
                  apply makes execute/4 (2, then 1 when apply ends);
                  that makes the inner shoen (2), its control/2 (3)
                  and goes on as report/2, which waits (4, 3); the
                  inner runs and ends, which takes one off the outer
                  (2).  The two left are control/2, waiting on C2,
                  and report/2, waiting on the inner's raw report:
                  they are the OUTER's goals, and the image ends them
                  only by remove_shoen and by a closed report stream,
                  which are stage 2.  So: A = "abc", Report2 =
                  [started, terminated | unbound], the outer Report =
                  [started | unbound] with NO terminated, the outer's
                  record count 2, started; the inner's count 0,
                  terminated, its parent the outer.  OBSERVED: so.
  nested: the inner report closed
                  the bench closes the inner's raw report stream
                  itself (its tail's address read from the reference
                  model's shoen record, a SLOT operation), as
                  remove_shoen will: report/2 ends, Report2 =
                  [started, terminated], the outer's count 1 (its
                  control/2), still started, still no terminated.
  waiting         the two stubs spawned by the bench: create_shoen
                  with MaxPrio unbound waits for it, start_shoen
                  waits for the handle; then as `run`, the report raw
                  ([8, 12 | unbound]).  The Report variable is bound
                  to the stub's by get_value: the report tail is
                  followed through a reference.
  code unbound    Code unbound: create_shoen does not wait; apply
                  waits INSIDE the shoen (a waiting built-in's goal
                  is counted): [started | unbound], count 1.
  code bound      the bench binds it: as `run`.
  unified inside  hash/3 on X = {1, 2} with NewX given as {1, V}: the
                  goal of unify_step that NewX = X makes is the
                  shoen's; V = 2, then terminated.
Thirteen goals are left waiting, as counted by hand (WAITING).

Fault injections into the Bluespec, OBSERVED 2026-11-23.  Made in a
copy of the tree (bsv/, asm/, ref/), each built and run by
`bsv/run_pimm_lockstep.sh shoen`, that is on THIS test alone: what
the other thirty-three tests say of them was not run.  The copy
restored and rebuilt clean: PASS.  First difference:
  the count starts at 0 (terminated a reduction early)  run, line 65
  no -1 when a goal suspends                     suspended, line 184
  8 reported after the goal is released                run, line 124
  the parked goal ready at create                       run, line 71
  the parent not decremented at the end             nested, line 757
  the child not counted on its parent               nested, line 242
  an output register written (cleared) before the inputs are read:
    the write itself is the difference                  run, line 63
  the goal's shoen not taken from its status cell      run, line 157
  a woken goal loses its shoen                         run, line 301
  a waiting built-in's goal not counted                run, line 238
  a unification's goal not counted          unified inside, line 226
  a suspended goal written as the root's         suspended, line 160
  the status left `started` at the end                 run, line 581
  the current shoen kept when the queue empties      waiting, line 6
  create_shoen does not wait for MaxPrio            waiting, line 94
NOT caught (PASS), all three refusals, which no part runs because a
refusal stops the reference model and the driver cannot play one:
  a failure inside a shoen not refused
  a shoen started twice not refused
  a priority that is no integer not refused

The same wrong rule in BOTH models (made in the reference, run with
--reference, so only this file's own checks and the pinned trace
length speak), OBSERVED 2026-11-23:
  the count starts at 0          caught: four `terminated`, count -1
  no -1 when a goal suspends     caught: `suspended` count 2, no
                                 terminated in `woken`
  the parent not decremented     caught: the outer's count 3
  the child not counted          caught: the outer's count 1
  a waiting built-in's goal not counted, a unification's goal not
  counted, a woken goal loses its shoen, terminated never reported,
  started reported twice, the current shoen kept between runs
                                 caught, each by a count or a report
  the parked goal ready at create
                                 caught: the reference stops (the
                                 goal runs twice)
  8 reported after the goal is released
                                 no VALUE differs: the report reads
                                 the same.  Caught by the trace
                                 length (4521 lines for 4423) and by
                                 a check on the reference's trace
                                 added for it (in `run`, the
                                 message's cells are written before
                                 the goal's W line).
So the ORDER of `started` and the goal's release shows in no value;
that order is VPIM's, not PIM/m's.

The refusals, OBSERVED BY HAND 2026-11-23, outside the suite (four
one-off scripts on a built copy; the two traces identical up to the
refusal, the reference raising Unimplemented, the Bluespec ending
`E unimp`):
  a goal failing inside a shoen (ipl:close/1 applied to {5}): at
    get_nil, cell 7874, not `E fail`
  a shoen started twice (Control = [start, start | _]): at the second
    start_shoen, cell 15755
  the closed Control [start]: remove_shoen, cell 15792 (stage 1; since
    stage 2 remove_shoen is implemented and this runs, in
    lockstep_shoen2.py `closed control`)
  create_shoen's stub with an atom for MinPrio

Not run at all: stop_shoen, abort_shoen, add_shoen_resource,
allow_shoen_resource_report, shoen_profile, create_profiling_shoen,
raise (no handler in either model: refused as any unknown instruction
is); a report stream that a consumer has bound; a shoen ended BY the
end of its child (the step up from a parent's count reaching 0: with
the image's code a parent always keeps the child's report/2, see
`nested` here and in lockstep_shoen2.py); a merger inside a shoen;
three shoen deep.  shoen_statistics, remove_shoen and the closed
Control lists the IPL's monitors send are stage 2: lockstep_shoen2.py.

Re-pinned for stage 2 (2026-11-23), 4423 -> 4495 trace lines, no value
changed: the shoen record has two more cells (asm/pimm_layout.py), so
each of the eight shoen made writes SH_REDUCTIONS and SH_REMOVE at
create (16 lines), and every end of a run of a goal inside a shoen
writes SH_REDUCTIONS before the count (56 lines).  Counted on the
reference's trace: 64 writes of the reductions cells, 8 of the remove
cells.  The injections above were run before that change.
Re-pinned for shoen stage 3 (2026-11-23), 4495 -> 4511 trace lines, no
value changed: the shoen record has one more cell, SH_MASK, written at
create (8 shoen made: 8 lines), and start_shoen empties the parked
list, SH_GOAL := 0 (8 starts: 8 lines); counted on the reference's
trace (both writes, nothing else new).  The test now finds the first
goal's record after the shoen record and the Report variable (where
create_shoen writes it), SH_GOAL being 0 once the shoen is started;
the line numbers of the injections above are from before.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import lockstep_cons as cons  # noqa: E402
import pimm_layout as L  # noqa: E402

PINNED = dict(parts=11, lines=5534)
I = lambda v: (pimm.INT, v & 0xffffffff)           # noqa: E731
TEXT = 'abc'
ABC = (8, [ord(c) for c in TEXT])
STATUS = {L.DORMANT: 'dormant', L.STARTED: 'started', L.TERMINATED: 'terminated'}


def stream(*msgs, closed=False):
    """A report stream as pimm.Machine.term gives it: the messages,
    then an unbound tail (or [] when closed)."""
    if closed:
        return list(msgs)
    out = None
    for m in reversed(msgs):
        out = ('|', m, out)
    return out


# What each part must leave, derived from the design by hand (see the
# header), not read from a model: the values printed, in order, and
# every shoen made so far as (count, status, parent: its number among
# the shoen, None for the root).
DONE3 = [(0, 'terminated', None)] * 3
# R8 (2026-11-25): a shoen has no resource until it is given some, so
# its first goal parks and resource_low is reported; the bench answers
# as PIMOS's task manager does (driver.Script.fund_parked), and the goal
# is released after resource_added
FUNDED = ('started', 'resource_low', 'resource_added')
EXPECT = [
    ('run', [ABC, stream(*FUNDED, 'terminated')],
     [(0, 'terminated', None)]),
    ('dormant', [None, None],
     [(0, 'terminated', None), (1, 'dormant', None)]),
    ('late start', [ABC, stream(*FUNDED, 'terminated')],
     [(0, 'terminated', None), (0, 'terminated', None)]),
    ('suspended', [None, stream(*FUNDED)],
     [(0, 'terminated', None), (0, 'terminated', None), (1, 'started', None)]),
    ('woken', [7, -7, stream(*FUNDED, 'terminated')],
     [(0, 'terminated', None), (0, 'terminated', None), (0, 'terminated', None)]),
    ('nested', [ABC, stream(*FUNDED, 'terminated'), stream(*FUNDED)],
     [(0, 'terminated', None), (0, 'terminated', None), (0, 'terminated', None),
      (2, 'started', None), (0, 'terminated', 3)]),
    ('nested: the inner report closed', [stream(*FUNDED, 'terminated', closed=True),
                                         stream(*FUNDED)],
     [(0, 'terminated', None), (0, 'terminated', None), (0, 'terminated', None),
      (1, 'started', None), (0, 'terminated', 3)]),
    ('waiting', [ABC, stream(L.REPORT_STARTED, L.REPORT_RESOURCE_LOW, L.REPORT_RESOURCE_ADDED,
                           L.REPORT_TERMINATED)],
     DONE3 + [(1, 'started', None), (0, 'terminated', 3), (0, 'terminated', None)]),
    ('code unbound', [None, stream(*FUNDED)],
     DONE3 + [(1, 'started', None), (0, 'terminated', 3), (0, 'terminated', None),
              (1, 'started', None)]),
    ('code bound', [ABC, stream(*FUNDED, 'terminated')],
     DONE3 + [(1, 'started', None), (0, 'terminated', 3), (0, 'terminated', None),
              (0, 'terminated', None)]),
    ('unified inside', [2, stream(*FUNDED, 'terminated')],
     DONE3 + [(1, 'started', None), (0, 'terminated', 3), (0, 'terminated', None),
              (0, 'terminated', None), (0, 'terminated', None)]),
]
# Goals left waiting at the end, by hand: control/2 on its open
# Control and report/2 on the raw report's open tail for each of the
# six shoen made by execute/4 at the root (12), and the nested outer's
# control/2 of the inner, which lives in the outer (1); the inner's
# report/2 ended when the bench closed its stream, and the stubs of
# `waiting` are done.
WAITING = 13
INNER = 4           # the nested inner shoen, whose report the bench closed


def handles(lines, load):
    """The shoen records whose handle a register was given, in order,
    as memory addresses relative to the load address (from the R lines:
    a cell of tag 38h)."""
    out = []
    for ln in lines:
        if ln[0] == 'R' and ln.split()[2].startswith('38'):
            a = int(ln.split()[2][2:], 16) - load
            if a not in out:
                out.append(a)
    return out


def script():
    im = pimm.kbndis.Image()
    names = {name: n for n, name in im.sym.items()}
    A = lambda n: (pimm.ATOM, names[n])            # noqa: E731
    stubs = pimm.Machine().stubs
    execute4 = pimm.predicate(im, 'shoen', 'execute/4')

    def modobj(name):
        return (pimm.MOD, im.load + [x for x in im.mods if x['name'] == name][0]['addr'] + 1)

    def code(mod, pred):
        """A code object made by the bench (for a predicate that is not
        public, which predicate_to_code would not give)."""
        return (pimm.COD, im.load + pimm.predicate(im, mod, pred))

    s = driver.Script()

    def p2c(mod, name, arity, out):
        s.argc(1, modobj(mod))
        s.argc(2, A(name))
        s.argc(3, I(arity))
        s.newvar(out)
        s.arg(4, out)
        s.spawn(stubs['predicate_to_code']['addr'], 4)
        s.run()

    def execute(code_slot, argv_slot, control_slot, report_slot):
        """shoen:execute(Code, Argv, Control, Report), the image's."""
        s.arg(1, code_slot)
        s.arg(2, argv_slot)
        s.arg(3, control_slot)
        s.arg(4, report_slot)
        s.spawn(execute4, 4)

    def convert_goal():
        """Slots 0 the code of jis_to_ascii:convert/2, 2 its arguments
        {TEXT in JIS, A}, A in slot 5."""
        p2c('jis_to_ascii', 'convert', 2, 0)
        s.string(1, 16, cons.jis(TEXT))
        s.vector(2, 4, [('slot', 1), None])

    # (a) [start|C], C left unbound: the goal runs, the shoen ends
    s.label('run')
    convert_goal()
    s.cons(3, 6, A('start'), None)                 # C in 7
    s.newvar(8)
    execute(0, 2, 3, 8)
    s.run()
    s.fund_parked(9)                               # R8: resource_low answered
    s.out(5)
    s.out(8)

    # (b) no start: dormant; then the Control stream is bound late
    s.label('dormant')
    convert_goal()
    s.newvar(3)
    s.newvar(8)
    execute(0, 2, 3, 8)
    s.run()
    s.out(5)
    s.out(8)
    s.label('late start')
    s.cons(9, 6, A('start'), None)
    s.unify(3, 9)
    s.run()
    s.fund_parked(10)
    s.out(5)
    s.out(8)

    # (c) the shoen's goal suspends: ipl_pool:hash(X, ^H, ^NewX) on an
    # unbound X; no `terminated` until the bench binds X
    s.label('suspended')
    s.setslot(0, code('ipl_pool', 'hash/3'))
    s.vector(2, 4, [None, None, None])             # X in 4, H in 5, NewX in 6
    s.cons(3, 9, A('start'), None)
    s.newvar(8)
    execute(0, 2, 3, 8)
    s.run()
    s.fund_parked(10)
    s.out(5)
    s.out(8)
    s.label('woken')
    s.unifyc(4, I(-7))
    s.run()
    s.out(5)
    s.out(6)
    s.out(8)

    # (d) nested: the outer shoen's code is shoen:execute/4 itself,
    # which makes the inner shoen (convert/2) and its control/2 and
    # report/2 IN the outer
    s.label('nested')
    convert_goal()                                 # 0 code, 2 argv, A in 5
    s.cons(3, 6, A('start'), None)                 # the inner Control
    s.newvar(8)                                    # the inner Report
    p2c('shoen', 'execute', 4, 9)
    s.vector(10, 11, [('slot', 0), ('slot', 2), ('slot', 3), ('slot', 8)])
    s.cons(1, 11, A('start'), None)                # the outer Control
    s.newvar(13)                                   # the outer Report
    execute(9, 10, 1, 13)
    s.run()
    s.fund_parked(14)                              # the outer, then the inner
    s.out(5)
    s.out(8)
    s.out(13)
    # The inner's report/2 can only end when its raw report stream is
    # closed, which remove_shoen will do (stage 2).  The bench closes
    # it itself: the unbound tail is in the inner's shoen record.
    s.label('nested: the inner report closed')
    m = s.live()
    # the newest shoen record (R8: the live trace since the funding no
    # longer holds the inner's handle)
    inner = max({c[1] for c in m.mem.values() if c[0] == pimm.SHREC})
    s.setslot(14, m.mem[inner + L.SH_REPORT])
    s.unifyc(14, pimm.NIL)
    s.run()
    s.out(8)
    s.out(13)

    # (f) the built-ins waiting: the stubs' own goals, spawned by the
    # bench (root).  create_shoen with MaxPrio unbound waits for it;
    # start_shoen waits for the handle.
    s.label('waiting')
    convert_goal()
    s.argc(1, I(0))
    s.newvar(9)                                    # MaxPrio
    s.arg(2, 9)
    s.argc(3, I(-1))
    s.arg(4, 0)
    s.arg(5, 2)
    s.newvar(8)                                    # Report
    s.arg(6, 8)
    s.newvar(10)                                   # Shoen
    s.arg(7, 10)
    s.spawn(stubs['create_shoen']['addr'], 7)
    # (the Bluespec driver does not wait for a SPAWN: the next
    # operation must be one it waits for, not an argument)
    s.newvar(11)
    s.arg(1, 10)
    s.arg(2, 11)
    s.spawn(stubs['start_shoen']['addr'], 2)
    s.run()
    s.unifyc(9, I(-1))
    s.run()
    s.fund_parked(12)
    s.out(5)
    s.out(8)

    # (g) Code unbound: create_shoen does not wait for it; the shoen's
    # first goal, apply, does, INSIDE the shoen (a waiting built-in's
    # goal is one of the shoen's), until the bench binds it
    s.label('code unbound')
    p2c('jis_to_ascii', 'convert', 2, 9)
    s.newvar(0)
    s.string(1, 16, cons.jis(TEXT))
    s.vector(2, 4, [('slot', 1), None])
    s.cons(3, 6, A('start'), None)
    s.newvar(8)
    execute(0, 2, 3, 8)
    s.run()
    s.fund_parked(10)
    s.out(5)
    s.out(8)
    s.label('code bound')
    s.unify(0, 9)
    s.run()
    s.out(5)
    s.out(8)

    # (h) two vectors unified inside a shoen: ipl_pool:hash(X, ^H,
    # ^NewX) with X = {1, 2} and NewX given as {1, V}: the goal of
    # unify_step that NewX = X makes is one of the shoen's
    s.label('unified inside')
    s.setslot(0, code('ipl_pool', 'hash/3'))
    s.vector(1, 8, [I(1), I(2)])
    s.vector(3, 10, [I(1), None])                  # V in 11
    s.vector(2, 4, [('slot', 1), None, ('slot', 3)])
    s.cons(12, 13, A('start'), None)
    s.newvar(15)
    execute(0, 2, 12, 15)
    s.run()
    s.fund_parked(14)
    s.out(11)
    s.out(15)
    return s


def snapshot(m, outs, known):
    """What a part left, read from the reference machine's memory as
    the part ends: the printed words as terms, every shoen record."""
    vals = [None if m.unbound(w) else m.term(w) for w in outs]
    recs = []
    for a in known:
        sh = m.load + a
        parent = m.mem[sh + L.SH_PARENT][1]
        recs.append((pimm.signed(m.mem[sh + L.SH_COUNT][1]),
                     STATUS.get(m.mem[sh + L.SH_STATUS][1]),
                     known.index(parent - m.load) if parent else None))
    return vals, recs


def first_goal(m, sh):
    """The first goal's record.  Since shoen stage 3 SH_GOAL is the
    list of parked goals and start_shoen empties it (writes 0): the
    record then is found where create_shoen wrote it, after the shoen
    record and the Report variable (its order of allocation)."""
    g = m.mem[sh + L.SH_GOAL][1]
    return g if g else sh + L.SH_SIZE + 1


def check(m, snaps, parts):
    bad = []
    if [k for k, _v, _r in EXPECT] != list(snaps):
        return [('parts', list(snaps))]
    for k, vals, recs in EXPECT:
        if snaps[k] != (vals, recs):
            bad.append((k, snaps[k], (vals, recs)))
    known = handles([ln for lines in parts.values() for ln in lines], m.load)
    stub = m.stubs['apply']['addr']
    for a in known:
        sh = m.load + a
        # the first goal: a goal of apply's stub, of this shoen, taken
        g = first_goal(m, sh)
        if (m.mem[g + L.G_CODE][1] - m.load, m.mem[g + L.G_ARGN][1],
                m.mem[g + L.G_STATUS][1]) != (stub, 2, a << 2 | L.TAKEN):
            bad.append(('first goal of the shoen at %d' % a,))
        # the report tail: an unbound cell (but the one the bench closed)
        t = m.deref(m.mem[sh + L.SH_REPORT])
        if m.unbound(t) == (known.index(a) == INNER):
            bad.append(('report tail of the shoen at %d' % a, t))
    # `started` is reported BEFORE the first goal is released (VPIM's
    # order): in `run`, the message's two new cells, {INT, 8} then an
    # unbound cell after it, are written before the goal's W line
    g = first_goal(m, m.load + known[0]) - m.load
    lines = parts['run']
    car = '%02x%08x' % (pimm.INT, L.REPORT_STARTED)
    wrote = [i for i, ln in enumerate(lines[:-1])
             if ln[0] == 'M' and ln.split()[2] == car
             and lines[i + 1] == 'M %d %02x%08x' % (int(ln.split()[1]) + 1, pimm.UNDF, 0)]
    if not wrote or 'W %d' % g not in lines or wrote[0] > lines.index('W %d' % g):
        bad.append(('started is not reported before the goal is released',))
    # the dormant shoen's goal does not run: nothing of apply's stub
    if any(ln.startswith('I %d ' % stub) for ln in parts['dormant']):
        bad.append(('the goal of a dormant shoen ran',))
    us = 'I %d ' % m.stubs['$unify_step']['addr']
    if not any(ln.startswith(us) for ln in parts['unified inside']):
        bad.append(('no goal of unify_step inside the shoen',))
    # apply waited inside the shoen: its stub's instruction taken twice
    if sum(ln.startswith('I %d ' % stub) for ln in parts['code unbound'] + parts['code bound']) != 2:
        bad.append(('apply did not wait inside the shoen',))
    for k, n in (('create_shoen', 2), ('start_shoen', 2)):
        at = 'I %d ' % m.stubs[k]['addr']
        if sum(ln.startswith(at) for ln in parts['waiting']) != n:
            bad.append(('%s did not wait' % k,))
    if m.nsusp != WAITING:
        bad.append(('%d goals left waiting, expected %d' % (m.nsusp, WAITING),))
    return bad


def main(argv):
    s = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    kept, snaps, known = {}, {}, []
    play = s.play

    def keeping():
        for what, lines in play():
            kept[what] = lines
            for a in handles(lines, s.machine.load):
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
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep shoen',
                           dict(parts=PINNED['parts'], lines=PINNED['lines']))
    if not ok:
        return 1
    bad = check(m, snaps, kept)
    if bad:
        print('pimm lockstep shoen: FAIL %r' % (bad[:3],))
        return 1
    print('pimm lockstep shoen: PASS (create_shoen, start_shoen and termination on the '
          'Bluespec core, %d trace lines identical to the reference model: the image\'s '
          'shoen:execute/4 runs a goal in a shoen and reports started, terminated; a '
          'shoen not started stays dormant; one whose goal suspends ends when the goal '
          'does; a nested shoen ends and its parent, holding its control/2, does not)'
          % s.counts['lines'])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
