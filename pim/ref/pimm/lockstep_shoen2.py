#!/usr/bin/env python3
"""Lockstep: the shoen, stage 2: shoen_statistics, remove_shoen, the
image's monitors.

    python3 ref/pimm/lockstep_shoen2.py --script FILE    write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_shoen2.py compare
    python3 ref/pimm/lockstep_shoen2.py --reference      the reference alone:
                                                         the value checks, the
                                                         trace length

Stage 2 of the shoen (stage 1: lockstep_shoen.py): shoen_statistics
(22:E6) and remove_shoen (22:E4), driven by the IMAGE'S OWN monitors
on the report of its own shoen:execute/4 (cell 15550).  The three
monitors, ipl:ipl_monitor/3 (cell 8275), top:bios_monitor/3 (17721)
and top:top_level_monitor/4 (17596), answer `terminated` with Control
= [statistics], a closed list, so the image's control/2 calls
shoen_statistics and then, on [], remove_shoen; they skip
statistics_started and return_resource; ipl_monitor shows
statistics(H, L) with display_console ("Statistics in Resource:", H,
L), the top ones skip it; on [] they bind Shut = shut (ipl_monitor
first shows "SCSI-FEP END********").  None of the paths taken reaches
put_console (report/2 uses it only for a message it does not know,
the monitors not at all): display_console is implemented on both
models.  ipl:wait_finish/1, which halts, is not spawned.

Where each thing comes from (docs/pimm_semantics.md "Shoen"):
  PIM/m-sourced   the encodings and directions (inst_tab.kl1, blt.kl1);
                  the codes 10, {9, H, L}, {14, H, L} and [] (the
                  image's report/2, pimos.vmac:177-199); H:L twice the
                  number of reductions, the descendants included, exact
                  after termination (manual e-shoen.tex:234-236); a
                  reduction = dequeues and executes less suspensions
                  (e-shoen.tex:388-395), i.e. one per execute /
                  execute_external and one per proceed.
  carried over    10 then {9, ..} at once on a terminated shoen (VPIM
                  f_shoen_control.psl.c:691-727); remove of a
                  terminated shoen: return_resource, the close (VPIM
                  :547-575); remove of one not terminated: a flag, the
                  removal at termination, 12, 14, [] (VPIM
                  f_shoen_with_fp.psl.c:69-71); counting at proceed and
                  execute and a child's total added to its parent at
                  its termination (PDSS emulate.c:333-365, shoen.c:293).
  OURS            the two new record cells (asm/pimm_layout.py), the
                  cell written once at the end of each run; a stub's
                  goal counted as one reduction; return_resource(0, 0)
                  (no resource model); statistics of a running shoen =
                  the count as it stands (the manual allows an
                  undercount); NewShoen = Shoen; resource_low (6) is
                  never reported, probably NOT what the machine did.

The value of statistics(H, L) is NOT read from the model: the test
counts the reductions on the trace itself (counted(): per shoen, each
execute or execute_external I line and each `E done`, given to the
shoen of the goal of the last G line), and for each shoen_statistics
instruction on the trace (its handle from the R lines) expects twice
that count, up to that line, of the shoen and the shoen below it.
The record's reduction cell at the end must equal the trace's count
too.  Observed (equal to the trace's count, first run of both
models): convert/2 on "abc" in a shoen is 12 reductions,
statistics(0, 24); the nested outer 11 of its own (execute/4's apply,
the inner's control/2 and report/2) + the inner's 12, statistics(0,
46); hash/3 4, statistics(0, 8) after termination and (0, 0) while
it ran (its goal had not yet run); padding/3 3, statistics(0, 6).

Seven parts, on a bare machine.  EXPECT says what each leaves: the
values printed, the console, and for every shoen so far (count,
status, parent, remove cell) from its record.  The first six parts
were derived from the design by hand before the first run and held
on it, but for one slip of the test's own (its check that every
statistic was printed counted the console's marker twice); the
Bluespec agreed on its first run.  `external` was added after, when
the injection `execute_external not counted` was not caught.
  ipl_monitor     convert/2 on {"abc" in JIS, A}, Control [start|C],
                  ipl_monitor(Report, C, Shut) at the root: A = "abc",
                  Report = [started, terminated, statistics_started,
                  statistics(H, L), return_resource(0, 0)] CLOSED, C =
                  [statistics], Shut = shut; console "Statistics in
                  Resource:", H, L, "SCSI-FEP END********"; the record
                  count 0, removed.
  nested          the outer's code is execute/4 (inner: convert/2),
                  bios_monitor on each Report: both Reports as above,
                  both Shut = shut, both records removed.  The OUTER
                  TERMINATES now (in stage 1 it could not): the step
                  that takes it to 0 is the end of the inner's
                  report/2, which is the outer's goal (observed:
                  shoen:report/2, cell 15818), NOT the inner's own
                  termination: with the image's code the child's
                  report/2 always outlives the child, so "a parent
                  terminated within its child's termination" is still
                  never run.
  closed control  Control = [start], closed at once: control/2 calls
                  remove_shoen before the goal has run, so the remove
                  is pending (remove cell 1); at termination 12, 14
                  and [] together: Report = [started, terminated,
                  return_resource(0, 0)], top_level_monitor's Shut =
                  shut (its own control tail gets [statistics], read
                  by nobody).
  running         hash/3 on an unbound X, Control = [start, statistics
                  | C]: statistics while it runs, (0, 0).
  running: woken  X bound: terminated after it.
  running: removed  C = [statistics]: a second statistics, (0, 8), then
                  remove: return_resource, closed.
  external        padding(1, "ab", C) (execute_external to
                  builtin_utility:append_string/3) in a shoen,
                  bios_monitor: C = "ab" and three zero bytes.
No goal is left waiting (WAITING = 0).

Fault injections into the Bluespec, OBSERVED 2026-11-23, each in a
private copy of the tree (bsv/, asm/, ref/), built and run by
`bsv/run_pimm_lockstep.sh shoen2` (this test alone), the copy then
restored and rebuilt clean: PASS.  First difference (part, line):
  statistics off by one reduction (2(n+1))     ipl_monitor, 779: the
                                               vector's L cell 1a for 18
  9 before 10                                  ipl_monitor, 770
  remove does not close the stream             ipl_monitor, 799
  return_resource after the close              ipl_monitor, 792
  the parent not decremented at a child's end  nested, 840
  the exec stage's count not reset per goal    ipl_monitor, 208
  a child's total not added to its parent      nested, 840
  execute_external not counted                 external, 289 (before
                                               the part `external`
                                               was added: PASS, no
                                               execute_external ran
                                               inside a shoen)
  a suspension counted as a reduction          nested, 351
  a remove before termination not honoured     closed control, 633
  a terminated shoen's remove only flagged     ipl_monitor, 792
  the reductions cell written after the count  ipl_monitor, 208
NOT caught (PASS): a shoen removed twice not refused (no part removes
twice: a refusal stops the reference and the driver cannot play one).

The same wrong rule in BOTH models (made in the reference, run with
--reference: only this file's value checks and the pinned length
speak), OBSERVED 2026-11-23, all caught by the value checks:
  statistics off by one reduction     statistics(0, 26) for (0, 24)
  9 before 10                         the Report's order
  statistics = the reductions, not twice   (0, 12) for (0, 24)
  a child's total not added           the outer (0, 22) for (0, 46),
                                      its cell 11 for 23
  a suspension counted as a reduction the outer (0, 52) for (0, 46)
  execute_external not counted        `external` (0, 4) for (0, 6)
                                      (PASS before that part existed)
  remove does not close the stream    Report open, Shut unbound, no
                                      "SCSI-FEP END********"
Those are caught because H, L are derived from the trace by the
test's own rule; a wrong RULE that both the models and the test share
(what a reduction is) is not: the rule is the manual's profile
formula, and PIM/m's own count is not known to be the same.

Not run: stop_shoen, abort_shoen, add_shoen_resource,
allow_shoen_resource_report, shoen_profile, raise (refused); a
statistic H above 0 (needs 2**31 reductions); shoen_statistics or
remove_shoen waiting on an unbound handle (their stubs); a removed
shoen given
statistics or removed again; three shoen deep; a parent terminated
within its child's termination (see `nested`).

Re-pinned for shoen stage 3 (2026-11-23), 4690 -> 4702 trace lines, no
value changed: the shoen record has one more cell, SH_MASK, written at
create (6 shoen made: 6 lines), and start_shoen empties the parked
list, SH_GOAL := 0 (6 starts: 6 lines); counted on the reference's
trace (both writes, nothing else new).  The line numbers of the injections
above are from before.
Re-pinned for R8 (2026-11-25), 4702 -> 6172 trace lines: a shoen starts
with no resource.  The image's monitors (ipl_monitor/3, bios_monitor/3,
top_level_monitor/4) answer resource_low on the Control with
add_resource(16#"3FFFFFFF", 16#"FFFFFFFF") and allow_resource_report,
so their reports gain resource_low, resource_added,
resource_report_allowed and the Control streams the two messages;
`closed control` and `running` have no monitor on a live Control, and
the bench funds them (driver.Script.fund_parked).  return_resource is
now that amount less what the trace counts as consumed (RETURNED).  The
fault injections above were observed before R8.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import lockstep_cons as cons  # noqa: E402
import lockstep_shoen as stage1  # noqa: E402
import pimm_layout as L  # noqa: E402

PINNED = dict(parts=7, lines=6172)
I = lambda v: (pimm.INT, v & 0xffffffff)           # noqa: E731
TEXT = 'abc'
ABC = (8, [ord(c) for c in TEXT])
STATUS = {L.DORMANT: 'dormant', L.STARTED: 'started', L.TERMINATED: 'terminated',
          L.REMOVED: 'removed'}


def STATS(i, j=0):
    """In EXPECT: the j-th statistics(H, L) reported by the i-th shoen
    made, H and L as the trace says they must be (expected_stats)."""
    return ('STATS', i, j)


def script():
    im = pimm.kbndis.Image()
    names = {name: n for n, name in im.sym.items()}
    A = lambda n: (pimm.ATOM, names[n])            # noqa: E731
    stubs = pimm.Machine().stubs
    execute4 = pimm.predicate(im, 'shoen', 'execute/4')
    ipl_monitor = pimm.predicate(im, 'ipl', 'ipl_monitor/3')
    bios_monitor = pimm.predicate(im, 'top', 'bios_monitor/3')
    top_monitor = pimm.predicate(im, 'top', 'top_level_monitor/4')

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

    def convert_goal():
        """Slots 0 the code of jis_to_ascii:convert/2, 2 its arguments
        {TEXT in JIS, A}, A in slot 5."""
        p2c('jis_to_ascii', 'convert', 2, 0)
        s.string(1, 16, cons.jis(TEXT))
        s.vector(2, 4, [('slot', 1), None])

    # (a) the IPL's own monitor: shoen:execute(Code, Argv, [start|C],
    # Report), ipl:ipl_monitor(Report, C, Shut), both at the root
    s.label('ipl_monitor')
    convert_goal()
    s.cons(3, 6, A('start'), None)                 # C in 7
    s.newvar(8)                                    # Report
    goal(execute4, 0, 2, 3, 8)
    s.newvar(9)                                    # Shut
    goal(ipl_monitor, 8, 7, 9)
    s.run()
    for k in (5, 8, 7, 9):
        s.out(k)

    # (b) nested: the outer's code is shoen:execute/4, which makes the
    # inner (convert/2) and the inner's control/2 and report/2 IN the
    # outer; top:bios_monitor/3 at the root for each of the two
    s.label('nested')
    convert_goal()                                 # 0 code, 2 argv, A in 5
    s.cons(3, 6, A('start'), None)                 # the inner Control, C2 in 7
    s.newvar(8)                                    # the inner Report
    p2c('shoen', 'execute', 4, 9)
    s.vector(10, 11, [('slot', 0), ('slot', 2), ('slot', 3), ('slot', 8)])
    s.cons(1, 11, A('start'), None)                # the outer Control, C1 in 12
    s.newvar(13)                                   # the outer Report
    goal(execute4, 9, 10, 1, 13)
    s.newvar(14)                                   # the inner's Shut
    goal(bios_monitor, 8, 7, 14)
    s.newvar(15)                                   # the outer's Shut
    goal(bios_monitor, 13, 12, 15)
    s.run()
    for k in (5, 8, 13, 14, 15):
        s.out(k)

    # (c) the Control stream closed at once, [start]: control/2 calls
    # start_shoen, then remove_shoen BEFORE the shoen's goal has run;
    # top:top_level_monitor/4 at the root
    s.label('closed control')
    convert_goal()
    s.cons(3, 6, A('start'), pimm.NIL)
    s.newvar(8)                                    # Report
    goal(execute4, 0, 2, 3, 8)
    s.newvar(9)                                    # the monitor's control tail
    s.newvar(10)                                   # its abort trigger: never bound
    s.newvar(11)                                   # Shut
    goal(top_monitor, 8, 9, 10, 11)
    s.run()
    s.fund_parked(12)                              # R8: the task manager's answer
    for k in (5, 8, 9, 11):
        s.out(k)

    # (d) statistics while the shoen runs: ipl_pool:hash/3 on an unbound
    # X, Control = [start, statistics | C], no monitor
    s.label('running')
    s.setslot(0, (pimm.COD, im.load + pimm.predicate(im, 'ipl_pool', 'hash/3')))
    s.vector(2, 12, [None, None, None])            # X in 12, H in 13, NewX in 14
    s.cons(9, 10, A('statistics'), None)           # C in 11
    s.cons(3, 6, A('start'), ('slot', 9))
    s.newvar(8)                                    # Report
    goal(execute4, 0, 2, 3, 8)
    s.run()
    s.fund_parked(15)
    s.out(8)
    s.label('running: woken')
    s.unifyc(12, I(-7))
    s.run()
    s.out(13)
    s.out(8)
    s.label('running: removed')
    s.cons(15, 4, A('statistics'), pimm.NIL)
    s.unify(11, 15)
    s.run()
    s.out(8)

    # (e) a goal of the shoen that goes on in another module:
    # scsi_fep_module:padding(1, "ab", C) ends in execute_external
    # builtin_utility:append_string/3; top:bios_monitor/3 at the root
    s.label('external')
    s.setslot(0, (pimm.COD, im.load + pimm.predicate(im, 'scsi_fep_module', 'padding/3')))
    s.string(1, 8, [ord('a'), ord('b')])
    s.vector(2, 4, [I(1), ('slot', 1), None])      # C in 6
    s.cons(3, 7, A('start'), None)                 # K in 8
    s.newvar(9)                                    # Report
    goal(execute4, 0, 2, 3, 9)
    s.newvar(10)                                   # Shut
    goal(bios_monitor, 9, 8, 10)
    s.run()
    for k in (6, 9, 10):
        s.out(k)
    return s


def stream(*msgs, closed=True):
    return stage1.stream(*msgs, closed=closed)


# R8: a shoen starts with no resource (VPIM _INIT_SHOEN_RESOURCE), so
# its first goal parks and resource_low is reported.  The image's own
# monitors answer add_resource(16#"3FFFFFFF", 16#"FFFFFFFF") and
# allow_resource_report, as PIMOS's task manager does (kernel/init/
# init.kl1:84-89); where no monitor listens, the bench gives the same
# (driver.Script.fund_parked).  What is returned at removal is that
# amount less the resource consumed, which is the shoen's statistic.
FUND = (0x3FFFFFFF << 32) | 0xFFFFFFFF
LOW = ('started', 'resource_low', 'resource_added')
MONITORED = LOW + ('resource_report_allowed',)


def RETURNED(i):
    """In EXPECT: return_resource(H, L) of the i-th shoen made, FUND
    less twice the reductions the trace counts for it and the shoens
    below it (expected_stats), all of them done by its removal."""
    return ('RETURNED', i)


def ended(i):
    return MONITORED + ('terminated', 'statistics_started', STATS(i), RETURNED(i))

# What each part must leave, derived by hand from the design BEFORE the
# first run: the values printed, the console's lines (display_console),
# and every shoen made so far as (count, status, parent, SH_REMOVE).
# STATS is statistics(H, L), H, L from the reductions counted on the
# trace (expected_stats).
EXPECT = [
    ('ipl_monitor',
     [ABC, stream(*ended(0)),
      [('add_resource', 0x3FFFFFFF, -1), 'allow_resource_report', 'statistics'], 'shut'],
     ['Statistics in Resource:', STATS(0), 'SCSI-FEP END********'],
     [(0, 'removed', None, 0)]),
    ('nested',
     [ABC, stream(*ended(2)), stream(*ended(1)), 'shut', 'shut'],
     [],
     [(0, 'removed', None, 0), (0, 'removed', None, 0), (0, 'removed', 1, 0)]),
    ('closed control',
     [ABC, stream(*LOW, 'terminated', RETURNED(3)),
      [('add_resource', 0x3FFFFFFF, -1), 'allow_resource_report', 'statistics'], 'shut'],
     [],
     [(0, 'removed', None, 0), (0, 'removed', None, 0), (0, 'removed', 1, 0),
      (0, 'removed', None, 1)]),
    ('running',
     [stream('started', 'statistics_started', STATS(4), *LOW[1:], closed=False)],
     [],
     [(0, 'removed', None, 0), (0, 'removed', None, 0), (0, 'removed', 1, 0),
      (0, 'removed', None, 1), (1, 'started', None, 0)]),
    ('running: woken',
     [7, stream('started', 'statistics_started', STATS(4), *LOW[1:], 'terminated',
                closed=False)],
     [],
     [(0, 'removed', None, 0), (0, 'removed', None, 0), (0, 'removed', 1, 0),
      (0, 'removed', None, 1), (0, 'terminated', None, 0)]),
    ('running: removed',
     [stream('started', 'statistics_started', STATS(4), *LOW[1:], 'terminated',
             'statistics_started', STATS(4, 1), RETURNED(4))],
     [],
     [(0, 'removed', None, 0), (0, 'removed', None, 0), (0, 'removed', 1, 0),
      (0, 'removed', None, 1), (0, 'removed', None, 0)]),
    ('external',
     [(8, [ord('a'), ord('b'), 0, 0, 0]), stream(*ended(5)), 'shut'],
     [],
     [(0, 'removed', None, 0), (0, 'removed', None, 0), (0, 'removed', 1, 0),
      (0, 'removed', None, 1), (0, 'removed', None, 0), (0, 'removed', None, 0)]),
]
WAITING = 0         # every goal ends: the monitors at [], control/2, report/2


def console(lines, m):
    """What display_console was given, from the C and S lines: an
    integer, or a string's text."""
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if ln[0] == 'C':
            t, v = int(ln[2:4], 16), int(ln[4:], 16)
            if t & ~1 == pimm.STRG:
                words = []
                i += 1
                while i < len(lines) and lines[i][0] == 'S':
                    words.append(int(lines[i][4:], 16))
                    i += 1
                d = words[0]
                typ, pad = (d >> 24) & 7, (d >> 27) & 3
                size = 1 << typ
                per = 32 // size
                el = [(w >> (32 - size * (k + 1))) & ((1 << size) - 1)
                      for w in words[1:] for k in range(per)]
                out.append(''.join(map(chr, el[:len(el) - pad])))
                continue
            out.append(pimm.signed(v) if t & ~1 == pimm.INT else (t, v))
        i += 1
    return out


def counted(m, lines):
    """The reductions on the trace, independently of the model's
    counter: for each line index, the running count per shoen (its
    record's address relative to the load address, 0 for the root) of
    execute and execute_external instructions and of `E done` lines,
    each given to the shoen of the goal taken last (a G line; the
    shoen read from the goal record's status cell, whose shoen bits
    never change).  The rule: the PIMOS manual's reduction count,
    dequeues and executes less suspensions (e-shoen.tex:388-395), is
    one per execute and one per proceed."""
    own, cur, marks = {}, 0, []
    for ln in lines:
        if ln[0] == 'G':
            g = int(ln.split()[1])
            cur = m.mem[m.load + g + L.G_STATUS][1] >> 2
        elif ln == 'E done' or (ln[0] == 'I' and m.opname(int(ln.split()[1]))
                                in ('execute', 'execute_external')):
            own[cur] = own.get(cur, 0) + 1
        marks.append(dict(own))
    return marks


def expected_stats(m, lines, known):
    """statistics(H, L) for every shoen_statistics on the trace, in
    order, per shoen: twice the reductions (PIMOS manual e-shoen.tex:
    234) counted on the trace up to that instruction, of the shoen and
    of the shoen below it.  The handle is the instruction's register x,
    as the R lines left it."""
    marks = counted(m, lines)
    parent = {a: m.mem[m.load + a + L.SH_PARENT][1] - m.load
              if m.mem[m.load + a + L.SH_PARENT][1] else None for a in known}

    def total(a, own):
        return own.get(a, 0) + sum(total(c, own) for c in known if parent[c] == a)
    regs, out = {}, {}
    for i, ln in enumerate(lines):
        if ln[0] == 'R':
            _r, n, w = ln.split()
            regs[int(n)] = (int(w[:2], 16), int(w[2:], 16))
        elif ln[0] == 'I' and m.opname(int(ln.split()[1])) == 'shoen_statistics':
            v = int(ln.split()[2][2:], 16)
            h = m.deref(regs[(v >> 16) & 255])
            a = h[1] - m.load
            n = 2 * total(a, marks[i])
            out.setdefault(a, []).append(('statistics', n >> 32, pimm.signed(n & 0xffffffff)))
    return out, marks[-1] if marks else {}, total


def fill(v, stats, known, spent=None):
    """EXPECT's value with each STATS(i, j) replaced by the statistic
    the trace gives (a tuple), or by its two numbers (flat=True, for
    the console)."""
    if isinstance(v, tuple) and v[:1] == ('STATS',):
        got = stats.get(known[v[1]], [])
        return got[v[2]] if v[2] < len(got) else ('no statistic', v)
    if isinstance(v, tuple) and v[:1] == ('RETURNED',):
        n = FUND - spent(known[v[1]])
        return ('return_resource', n >> 32, pimm.signed(n & 0xffffffff))
    if isinstance(v, list):
        return [fill(x, stats, known, spent) for x in v]
    if isinstance(v, tuple):
        return tuple(fill(x, stats, known, spent) for x in v)
    return v


def check(m, snaps, parts):
    bad = []
    if [k for k, _v, _c, _r in EXPECT] != list(snaps):
        return [('parts', list(snaps))]
    lines = [ln for k, _v, _c, _r in EXPECT for ln in parts[k]]
    known = stage1.handles(lines, m.load)
    stats, own, total = expected_stats(m, lines, known)

    def spent(a):
        return 2 * total(a, own)
    for k, vals, cons_, recs in EXPECT:
        got_vals, got_recs = snaps[k]
        want = fill(vals, stats, known, spent)
        if got_vals != want:
            bad.append((k, 'values', got_vals, want))
        c = console(parts[k], m)
        wantc = []
        for x in fill(cons_, stats, known, spent):
            wantc += list(x[1:]) if isinstance(x, tuple) else [x]
        if c != wantc:
            bad.append((k, 'console', c, wantc))
        if got_recs != recs:
            bad.append((k, 'records', got_recs, recs))
    # every statistic was printed: as many STATS in EXPECT as
    # shoen_statistics on the trace
    marks = set(re.findall(r"\('STATS', \d+, \d+\)", str(EXPECT)))
    if sum(len(v) for v in stats.values()) != len(marks):
        bad.append(('statistics on the trace', stats))
    # the record's count of reductions: the trace's, of the shoen and
    # its descendants (all of them terminated by the end)
    for a in known:
        if m.mem[m.load + a + L.SH_REDUCTIONS][1] != total(a, own):
            bad.append(('reductions of the shoen at %d' % a,
                        m.mem[m.load + a + L.SH_REDUCTIONS][1], total(a, own)))
    # nested: the outer terminates in a run of the inner's report/2 (a
    # goal of the outer), after the inner has terminated
    nl = parts['nested']
    outer, inner = known[1], known[2]
    at = ['M %d %02x%08x' % (a + L.SH_STATUS, pimm.INT, L.TERMINATED) for a in (inner, outer)]
    if not all(x in nl for x in at) or nl.index(at[0]) > nl.index(at[1]):
        bad.append(('nested: the outer did not terminate after the inner',))
    else:
        g = int([ln for ln in nl[:nl.index(at[1])] if ln[0] == 'G'][-1].split()[1])
        if (m.mem[m.load + g + L.G_CODE][1] - m.load != pimm.predicate(m.im, 'shoen', 'report/2')
                or m.mem[m.load + g + L.G_STATUS][1] >> 2 != outer):
            bad.append(('nested: the outer did not terminate at the end of report/2',))
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
                     m.mem[sh + L.SH_REMOVE][1]))
    return vals, recs


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
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep shoen2',
                           dict(parts=PINNED['parts'], lines=PINNED['lines']))
    if not ok:
        return 1
    bad = check(m, snaps, kept)
    if bad:
        print('pimm lockstep shoen2: FAIL %r' % (bad[:3],))
        return 1
    print('pimm lockstep shoen2: PASS (shoen_statistics and remove_shoen on the Bluespec '
          'core, %d trace lines identical to the reference model)' % s.counts['lines'])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
