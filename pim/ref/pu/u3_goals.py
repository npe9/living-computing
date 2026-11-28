#!/usr/bin/env python3
"""U3, first step: a multi-goal KL1 program on ICOT's held microcode
(ref/pu/pu.py), whose goal queue is made and taken by the firmware's own
enqueue_goal and proceed, against ref/pimm/pimm.py at every scheduler pick.

The program.  A driver clause, assembled here (OURS: the test's input,
three KL1-B cell kinds the IPL image uses, no micro-routine), enqueues two
goals of the IPL image's own append/3 (scsi_fep_module, cells 6644-6658,
the program of u2_append.py) and proceeds:

    driver(L1, M1, Z1, L2, M2, Z2):
        set_value 1,0   set_value 2,1   set_value 3,2   enqueue_goal 3, append/3
        set_value 1,3   set_value 2,4   set_value 3,5   enqueue_goal 3, append/3
        proceed

called as driver([a], [], Z1, [b], [], Z2).  On pimm.py: 1 + 2 + 2
reductions, 41 instructions; proceed picks append([b], [], Z2) (the
newest), then append([a], [], Z1), then finds the queue empty.

What runs held: every instruction's E stage, including the scheduler:
set_value writes the goal record R10 + x (3187); enqueue_goal (4c00-4c07)
stamps cell 0 {GOAL, n}, writes cells 12-15 ({COD, label}, R12, R13, the
old R14), links the record at the head of R14, pops a fresh record off
R1b into R10 and counts R16 up; proceed (216c-2224) pushes the finished
record on R1b, takes R14's head into R10, loads its code into R04 and its
arguments into A0.., and R14 := its link.  Nothing of the queue is seeded:
R14, R10, R1b and every record cell proceed reads are written by held
words in this run (checked, below).

What is OURS (the stand-ins), each item:
  - the A stage: each instruction cell and its address from pimm.py's
    trace, in pimm.py's order (the firmware's R04 is compared at every
    branch, execute and dispatch);
  - the first goal switch: A0-A5 as pimm.py's goal_switch leaves them
    for the driver (the first goal is not dispatched by proceed);
  - the machine state before the first instruction, which no instruction
    of the program writes first (INITIAL below; each value cites the held
    boot word that writes it, read not run): the goal-record free list
    R1b (NREC records, linked through cell 0 as 216c's push writes them)
    and the record R10 the driver builds into (202d-202f pop R1b into
    R10); R14 = nil, the empty queue (the boot's first record gets
    {ATOMo, R06} as its link at 210a-210b, R06 = 0 at that point:
    INFERENCE); R12 = {INT, 0} (2102); R13 = {FPREC, root record} (20eb);
    R15 = {INT, 17} (20a6-20a7, one arm of the PMPF test at 209f); W1f =
    0 (20a8); R16 = {INT, 1}: rassy's 'ccc', which enqueue_goal counts up
    (4c06-4c07) and proceed's dequeue down (2171-2172), and whose running
    out (2173 falling to 2174) charges crr to the foster parent's record
    (2177 calls 12e0-12ea: R13's cell += R15, R15 := 0).  INFERENCE: the
    count of the foster parent's live goals, so 1 for the driver itself
    (pimm.py counts a spawned goal of a shoen the same way, counted());
    the boot's 20a0-20a1 R16 := {INTo, R06} is read, not run.  With 0
    (injection 'r16_zero') the second pick runs out at 2174 and stops
    at 12e3 (CNDF 7 EM1 1a, rassy's 'cond PMPF', a flag not given);
    the cell free lists and R1f as u2_append.py;
  - memory: pimm.py's cells at the same addresses.

Compared, per instruction (pimm.py's trace split at its I lines):
  - set_value x, y: pimm.py's A line (argv[x]) against the firmware's
    cell R10 + x (the record being built: argv[k] IS cell k, INFERRED from
    3187's write; pseudo_pimm_microcode.md section 18); no other write;
  - enqueue_goal n: pimm.py's new goal record against the firmware's (the
    old R10): {GOAL, n}, the arguments (cells 1..n against pimm.py's), the
    code ({COD, label}), the link (cell 15 = the old R14, which must be
    the firmware record of pimm.py's previous rq, or nil for 0); R14 :=
    {HOOKo, record}; R10 := the popped record; no other cell written;
  - proceed: the PICK.  pimm.py's next goal (its G line) against the
    firmware's dispatch: R04 = {COD, its code}, R10 = {HOOKo, the record
    the firmware made for that goal}, A0.. = pimm.py's R lines, R14 = the
    record of pimm.py's rq after the pick (nil for 0); the only cell
    written is the finished record's cell 0 (pushed on R1b: declared, as
    u2_append's 'free').  The empty pick: the firmware enters the empty
    arm 21b2 and stops at 21b3 (pinned, u2_append.EMPTY_STOP), with R04
    and the A registers unchanged; pimm.py has no G line and ends (Q);
  - at each pick, provenance: R14 as proceed reads it, and every cell of
    the dispatched record proceed reads (0..n, 12-15), were last written
    by a held word of this run (not by the harness);
  - every other instruction: u2_append.compare and compare_next_pc (the
    U2 comparison, unchanged).

    python3 ref/pu/u3_goals.py [-v] [--inject NAME]

Exit 0 when every instruction executed matched, the furthest point is
PINNED and the picks compared are PICKS_PINNED; 1 otherwise.

Observed 2026-11-27 (U3 first session): 41 of 41 instructions executed
and matched, 162 held microinstructions; 3 picks compared (2 dispatching,
1 empty), no mismatch.
Injections (in-process, no file edited), observed (each alone; every
other check unchanged up to the first stop or FAIL):
  reseed_r14         FAIL at 8 (the first pick): provenance, R14 last
                     written by the harness (nothing else differs)
  ccf_bits           STOP at 8, 2250 (cells 13 / 14 from MDR1: cell 14
                     is not R13, the other-parent call)
  jmpf8_goto_off     STOP at 3, 4c01
  wsel_d_off         STOP at 3, 4c01 (W0d never set)
  execute_mdr1_stale STOP at 24 (the second pick), 216e (crr STALE)
  enq_head_mar1      STOP at 3, 4c00 (MAR2 never set)
  enq_label_mdr2     STOP at 3, 4c04 (STALE written)
  enq_label_plus1    FAIL at 3: cell 12 one past pimm.py's code
  pg_swap            FAIL at 8: R10 and R14 against pimm.py's pick
  free_undeclared    FAIL at 24 (the second pick): the freed record's
                     cell 0 (at the first pick it is rewritten unchanged)
  slit_pending       STOP at 3, 4c08 (the JMPF 8 goto taken; ALF shift)
  r16_zero           STOP at 24, 12e3 (ccc run out: cond PMPF)
  crr_two            STOP at 8, 217c (crr run out: cond PMPF)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'pimm'))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import pu as PU  # noqa: E402
import setup as SU  # noqa: E402
import check_pu  # noqa: E402
import u2_append as U2  # noqa: E402
import pimm  # noqa: E402
from pimm_layout import G_LINK, G_CODE, G_ARGN, G_ARGS  # noqa: E402

fmt = check_pu.fmt
COD, R_PC = U2.COD, U2.R_PC
HOOKO, GOAL, VECT0X, FPREC = 0x0a, 0x3c, 0x11, 0x39
NIL = (pimm.ATOM, 0)
OP_SET_VALUE, OP_ENQUEUE, OP_PROCEED = 0x14, 0x63, 0x60

# The machine state no instruction writes first (OURS; module docstring).
NREC = 8
GRECS = 0xf4000000            # the free goal records, 16 cells apart
REC0 = 0xf4800000             # the record the driver builds into
ROOT = 0xf5000000             # the root foster-parent record R13 names
INITIAL = {0x14: NIL, 0x12: (pimm.INT, 0), 0x13: (FPREC, ROOT),
           0x15: (pimm.INT, 17), 0x16: (pimm.INT, 1)}

PINNED = dict(steps=41, matched=41, stop=None)
PICKS_PINNED = 3              # 2 dispatching + the empty one

RESEED = None                 # injection 'reseed_r14': the step after which R14 is re-written
DECLARE_FREE = True
PG_SWAP = False               # injection 'pg_swap'


def driver_cells(pc0):
    """The driver clause at cell index pc0 (OURS)."""
    def kl(op, x=0, y=0, z=0):
        return (0x23, op << 24 | x << 16 | y << 8 | z)
    cells = []
    for k in (0, 3):
        for i in range(3):
            cells.append(kl(OP_SET_VALUE, i + 1, k + i))
        pc = pc0 + len(cells)
        c16 = (U2.APPEND - (pc + 2)) & 0xffff
        cells.append((0x23, OP_ENQUEUE << 24 | 3 << 16 | c16))
    cells.append(kl(OP_PROCEED))
    return cells


def pimm_run():
    """driver([a], [], Z1, [b], [], Z2) on pimm.py.  Returns (machine,
    state at the first instruction, steps): each step (pc, cell, lines,
    after), lines the instruction's R / M / A / G / Q lines."""
    m = pimm.Machine()
    code = driver_cells(0)
    a = m.alloc(len(code))
    pc0 = a - m.load
    for i, w in enumerate(driver_cells(pc0)):
        m.mem[a + i] = w

    def lst(atoms):
        c = m.alloc(2 * len(atoms))
        for i, at in enumerate(atoms):
            m.mem[c + 2 * i] = (pimm.ATOM, at)
            m.mem[c + 2 * i + 1] = (pimm.LIST, c + 2 * i + 2) if i + 1 < len(atoms) else pimm.NIL
        return (pimm.LIST, c)
    args = [lst([0x123]), pimm.NIL, m.new_var(), lst([0x124]), pimm.NIL, m.new_var()]
    m.tr = []
    steps, snap, marks = [], {}, []

    def state():
        return {'reg': list(m.reg[:16]), 'argv': list(m.argv[:16]), 'sp': getattr(m, '_sp', None),
                'alt': getattr(m, 'alt', None), 'rq': m.rq}
    orig = m.event

    def event(text):
        if text.startswith('I '):
            if steps:
                steps[-1][3].update(state())
            else:
                snap.update(state())
                snap['mem'] = dict(m.mem)
                snap['rq'] = m.rq
            f = text.split()
            steps.append((int(f[1]), (int(f[2][:2], 16), int(f[2][2:], 16)), [], {}))
            marks.append(len(m.tr) + 1)
        orig(text)
    m.event = event
    m.run(pc0, args)
    if not steps[-1][3].get('reg'):
        steps[-1][3].update(state())
    for k, st in enumerate(steps):
        end = marks[k + 1] - 1 if k + 1 < len(marks) else len(m.tr)
        st[2].extend(ln for ln in m.tr[marks[k]:end]
                     if ln[:2] in ('R ', 'M ', 'A ', 'G ') or ln == 'Q')
    return m, snap, steps, pc0


class Prov:
    """Who wrote each scheduler register and memory cell last: the firmware
    (a held word's commit) or the harness."""

    def __init__(self):
        self.reg, self.mem = {}, {}

    def harness(self, p):
        for n in p.r:
            self.reg[n] = 'harness'
        for a in p.mem:
            self.mem[a] = 'harness'

    def firmware(self, p, n0):
        for c in p.cycles[n0:]:
            for (f, n), _v in c['reg_writes']:
                if f == 'R':
                    self.reg[n] = 'firmware'
            for a, _v in c['mem_writes']:
                self.mem[a] = 'firmware'


def other_writes(p, mem0, allowed):
    return ['heap %x: firmware wrote %s' % (a, fmt(p.mem.get(a)))
            for a in sorted(set(p.mem) | set(mem0))
            if p.mem.get(a) != mem0.get(a) and a not in allowed]


def an_unchanged(p, an0, what):
    return ['%s: firmware wrote A%d %s' % (what, i, fmt(p.an.get(i)))
            for i in sorted(set(p.an) | set(an0)) if p.an.get(i) != an0.get(i)]


def run(verbose=False):
    m, s0, steps, pc0 = pimm_run()
    p = PU.PU()
    U2.boot_heap_top(p, m.hp)
    p.mem.update(s0['mem'])
    for i, w in enumerate(s0['reg']):
        p.an[i] = w                                 # OURS: the first goal switch
    check_pu.seed_lists(p, U2.NFREE)
    U2.seed_execute(p)
    for k in range(NREC):                           # OURS: INITIAL (R1b's list)
        a = GRECS + 16 * k
        p.mem[a] = (VECT0X, a + 16) if k + 1 < NREC else NIL
    p.r[0x1b] = (VECT0X, GRECS)
    p.r[0x10] = (HOOKO, REC0)
    p.r.update(INITIAL)
    p.w[0x1f] = (0, 0)
    prov = Prov()
    prov.harness(p)
    rn = check_pu.Rename()
    for a in s0['mem']:
        rn.f2p[a] = rn.p2f[a] = a
    fw2pg, pg2fw = {}, {}                           # goal records: firmware <-> pimm.py
    out = {'done': 0, 'matched': 0, 'words': 0, 'stop': None, 'fail': None, 'picks': 0,
           'dispatched': 0, 'empty': 0}
    prev_after = s0
    for k, (pc, cellv, lines, after) in enumerate(steps):
        p.ir, p.pc = cellv, m.load + pc
        p.r[R_PC] = (COD, (m.load + pc + 1) & 0xffffffff)
        prov.reg[R_PC] = 'harness'
        r04_0 = p.r.get(R_PC)
        after['next_pc'] = steps[k + 1][0] if k + 1 < len(steps) else None
        after['sp_moved'] = after.get('sp') != prev_after.get('sp')
        after['r02_0'] = p.r.get(SU.R_SP)
        name = '?'
        n0 = len(p.trace)
        an0, mem0, r0 = dict(p.an), dict(p.mem), dict(p.r)
        base = None
        stop = None
        try:
            name = SU.decode(p)
            base = SU.base(name)
            prov_bad = check_provenance(p, prov) if base == 'proceed' else []
            p.run(SU.setup(p, name))
        except (PU.Unmodelled, KeyError) as e:
            stop = str(e)
        nw = len(p.trace) - n0
        out['words'] += nw
        prov.firmware(p, n0)
        empty = base == 'proceed' and not any(ln.startswith('G ') for ln in lines)
        if stop and not (empty and stop.startswith('%04x:' % U2.EMPTY_STOP)):
            out['stop'] = (k, pc, name, stop)
            print('STOP %2d %5d %-22s %s' % (k, pc, name, stop))
            break
        out['done'] += 1
        rl = [ln for ln in lines if ln[:2] in ('R ', 'M ')]
        if base == 'set_value':
            fails = cmp_set_value(p, rn, lines, an0, mem0, r0)
        elif base == 'enqueue_goal':
            fails = cmp_enqueue(p, m, rn, lines, after, prev_after, an0, mem0, r0, fw2pg, pg2fw)
        elif base == 'proceed':
            out['picks'] += 1
            fails = prov_bad + cmp_proceed(p, m, rn, lines, after, an0, mem0, r0, fw2pg, pg2fw,
                                           steps[k + 1][0] if k + 1 < len(steps) else None, n0)
            out['empty' if empty else 'dispatched'] += 1
        else:
            fails = U2.compare(p, m, rn, rl, after, name, an0, mem0)
            fails += U2.compare_next_pc(p, m, pc, after, name, r04_0)
        if fails:
            out['fail'] = (k, pc, name, fails)
            print('FAIL %2d %5d %-22s %d words: %s' % (k, pc, name, nw, '; '.join(fails)))
            break
        out['matched'] += 1
        print('ok   %2d %5d %-22s %d words%s' % (k, pc, name, nw,
                                                ('  pick %d%s' % (out['picks'], ' (empty)' if empty else ''))
                                                if base == 'proceed' else ''))
        if verbose:
            for c in p.cycles[n0:]:
                print('      %04x %016x' % (c['micro_pc'], c['microword']))
        if PG_SWAP and base == 'enqueue_goal' and len(pg2fw) == 2:
            (g1, f1), (g2, f2) = list(pg2fw.items())     # injection: the map crossed
            pg2fw.update({g1: f2, g2: f1})
            fw2pg.update({f1: g2, f2: g1})
        if RESEED is not None and k == RESEED:
            p.r[0x14] = tuple(p.r[0x14])            # injection: the harness writes R14
            prov.reg[0x14] = 'harness'
        prev_after = after
    print('%d of %d instructions executed and matched, %d held microinstructions; '
          '%d picks compared (%d dispatching, %d empty)%s'
          % (out['matched'], len(steps), out['words'], out['picks'], out['dispatched'],
             out['empty'], '' if not out['stop'] else '; first stop: instruction %d (%d %s)'
             % out['stop'][:3]))
    return out, len(steps)


def check_provenance(p, prov):
    """At proceed's entry: R14, and every cell of R14's head record that
    proceed reads, last written by a held word."""
    bad = []
    if prov.reg.get(0x14) != 'firmware':
        bad.append('provenance: R14 %s last written by the %s' % (fmt(p.r.get(0x14)),
                                                                  prov.reg.get(0x14)))
    h = p.r.get(0x14)
    if h and h[0] == HOOKO:
        n = p.mem.get(h[1], (0, 0))[1]
        for c in list(range(0, n + 1)) + [12, 13, 14, 15]:
            if prov.mem.get(h[1] + c) != 'firmware':
                bad.append('provenance: record %x cell %d last written by the %s'
                           % (h[1], c, prov.mem.get(h[1] + c)))
    return bad


def cmp_set_value(p, rn, lines, an0, mem0, r0):
    """set_value x, y: argv[x] is the record's cell R10 + x."""
    x = p.ir_field('x')
    cell = r0[0x10][1] + x
    al = [ln.split() for ln in lines if ln.startswith('A ')]
    fails = []
    if len(al) != 1 or int(al[0][1]) != x:
        return ['set_value: pimm.py A lines %s' % al]
    pv = (int(al[0][2][:2], 16), int(al[0][2][2:], 16))
    if not rn.same(p.mem.get(cell), pv, False, [], 'argv'):
        fails.append('cell R10+%d (%x): firmware %s, pimm.py argv[%d] %s'
                     % (x, cell, fmt(p.mem.get(cell)), x, fmt(pv)))
    fails += other_writes(p, mem0, {cell})
    fails += an_unchanged(p, an0, 'set_value')
    if [ln for ln in lines if ln[:2] in ('R ', 'M ')]:
        fails.append('set_value: pimm.py wrote %s' % lines)
    return fails


def link_of(w, fw2pg):
    """A firmware link value as pimm.py's: nil -> 0, {HOOKo, r} -> record."""
    if w == NIL:
        return 0
    if w and w[0] == HOOKO and w[1] in fw2pg:
        return fw2pg[w[1]]
    return ('unmapped', w)


def cmp_enqueue(p, m, rn, lines, after, prev, an0, mem0, r0, fw2pg, pg2fw):
    fails = []
    g = after['rq']                       # pimm.py's new record: the queue's head
    rec = r0[0x10][1]                     # the firmware's: the record being built
    n = m.mem[g + G_ARGN][1]
    if g in pg2fw:
        return ['enqueue_goal: pimm.py record %x seen before' % g]
    fw2pg[rec], pg2fw[g] = g, rec
    if p.mem.get(rec) != (GOAL, n):
        fails.append('cell 0 %s, want {GOAL, %d}' % (fmt(p.mem.get(rec)), n))
    for i in range(n):
        pv = m.mem[g + G_ARGS + i]
        if not rn.same(p.mem.get(rec + 1 + i), pv, False, [], 'arg'):
            fails.append('cell %d %s, pimm.py argument %s' % (1 + i, fmt(p.mem.get(rec + 1 + i)), fmt(pv)))
    if p.mem.get(rec + 12) != (COD, m.mem[g + G_CODE][1]):
        fails.append('cell 12 %s, pimm.py code {COD, %x}' % (fmt(p.mem.get(rec + 12)),
                                                              m.mem[g + G_CODE][1]))
    if p.mem.get(rec + 15) != r0[0x14]:
        fails.append('cell 15 %s, the old R14 %s' % (fmt(p.mem.get(rec + 15)), fmt(r0[0x14])))
    if link_of(p.mem.get(rec + 15), fw2pg) != m.mem[g + G_LINK][1]:
        fails.append('link: firmware %s (pimm.py %r), pimm.py\'s link %x'
                     % (fmt(p.mem.get(rec + 15)), link_of(p.mem.get(rec + 15), fw2pg),
                        m.mem[g + G_LINK][1]))
    if p.r.get(0x14) != (HOOKO, rec):
        fails.append('R14 %s, want {HOOKo, %x}' % (fmt(p.r.get(0x14)), rec))
    if p.r.get(0x10) != (HOOKO, r0[0x1b][1]):
        fails.append('R10 %s, want the popped record {HOOKo, %x}' % (fmt(p.r.get(0x10)), r0[0x1b][1]))
    fails += other_writes(p, mem0, {rec, rec + 12, rec + 13, rec + 14, rec + 15})
    fails += an_unchanged(p, an0, 'enqueue_goal')
    return fails


def cmp_proceed(p, m, rn, lines, after, an0, mem0, r0, fw2pg, pg2fw, next_pc, n0):
    fails = []
    fin = r0[0x10][1]                     # the finished goal's record, pushed on R1b
    allowed = set()
    if DECLARE_FREE:
        allowed.add(fin)
        if p.mem.get(fin) != (VECT0X, r0[0x1b][1]):
            fails.append('finished record %x cell 0 %s, want {VECT0x, old R1b}'
                         % (fin, fmt(p.mem.get(fin))))
    fails += other_writes(p, mem0, allowed)
    gl = [ln for ln in lines if ln.startswith('G ')]
    if not gl:                            # the empty pick
        ran = [u for u, _ in p.trace[n0:]]
        if 'Q' not in lines:
            fails.append('pimm.py neither picks a goal nor ends')
        if U2.EMPTY_ARM not in ran:
            fails.append('pimm.py picks no goal; the firmware did not take the empty arm')
        if p.r.get(R_PC) != r0.get(R_PC):
            fails.append('pimm.py picks no goal; the firmware dispatched R04 %s' % fmt(p.r.get(R_PC)))
        fails += an_unchanged(p, an0, 'empty pick')
        return fails
    g = m.load + int(gl[0].split()[1])
    code = m.mem[g + G_CODE][1]
    if next_pc is None or code != m.load + next_pc:
        fails.append('pimm.py\'s pick %x has code %x, its next instruction %r' % (g, code, next_pc))
    if p.r.get(R_PC) != (COD, code):
        fails.append('R04 %s, pimm.py\'s next goal\'s code {COD, %x}' % (fmt(p.r.get(R_PC)), code))
    if g not in pg2fw:
        return fails + ['pimm.py picks record %x, which no enqueue_goal made' % g]
    if p.r.get(0x10) != (HOOKO, pg2fw[g]):
        fails.append('R10 %s, the firmware record of pimm.py\'s pick {HOOKo, %x}'
                     % (fmt(p.r.get(0x10)), pg2fw[g]))
    # pimm.py's rq after its pick: its state when the goal's first
    # instruction is taken (after['rq'])
    want = after['rq']
    if link_of(p.r.get(0x14), fw2pg) != want:
        fails.append('R14 %s (pimm.py %r), pimm.py\'s ready queue after the pick %x'
                     % (fmt(p.r.get(0x14)), link_of(p.r.get(0x14), fw2pg), want))
    n = m.mem[g + G_ARGN][1]
    rl = {int(ln.split()[1]): (int(ln.split()[2][:2], 16), int(ln.split()[2][2:], 16))
          for ln in lines if ln.startswith('R ')}
    for i in range(n):
        if not rn.same(p.an.get(i), rl.get(i), False, [], 'A%d' % i):
            fails.append('A%d %s, pimm.py %s' % (i, fmt(p.an.get(i)), fmt(rl.get(i))))
    for i in sorted(set(p.an) | set(an0)):
        if i >= n and p.an.get(i) != an0.get(i) \
                and not (i < 2 and p.an.get(i) == p.mem.get(pg2fw[g] + 1 + i)):
            fails.append('A%d written %s beyond the arity %d' % (i, fmt(p.an.get(i)), n))
    return fails


def _reseed():
    globals().update(RESEED=7)           # after the second enqueue_goal


def _enq_label(how):
    s = SU.setup

    def setup(pu, name):
        start = s(pu, name)
        if SU.base(name) == 'enqueue_goal':
            lab = pu.wr[SU.mekbn.MDR1]
            if how == 'mdr2':
                pu.wr[SU.mekbn.MDR2], pu.wr[SU.mekbn.MDR1] = lab, PU.STALE
            else:
                pu.wr[SU.mekbn.MDR1] = (lab[0], lab[1] + 1)
        return start
    SU.setup = setup


def _ccf_bits():
    PU.RULES.update(ccf_rassy=False)


INJECT = {
    'reseed_r14': _reseed,
    'ccf_bits': _ccf_bits,
    'jmpf8_goto_off': lambda: PU.RULES.update(jmpf8_goto_if=False),
    'wsel_d_off': lambda: PU.RULES.update(wsel_d_em1=False),
    'execute_mdr1_stale': lambda: setattr(SU, 'EXECUTE_MDR1_EMO1', False),
    'enq_head_mar1': lambda: SU.ENQ_HEAD.update({2: 'MAR1'}),
    'enq_label_mdr2': lambda: _enq_label('mdr2'),
    'enq_label_plus1': lambda: _enq_label('plus1'),
    'pg_swap': lambda: globals().update(PG_SWAP=True),
    'free_undeclared': lambda: globals().update(DECLARE_FREE=False),
    'slit_pending': lambda: U2.EXECUTE_FLAGS.update(slit_check=True),
    'r16_zero': lambda: INITIAL.update({0x16: (pimm.INT, 0)}),
    'crr_two': lambda: INITIAL.update({0x15: (pimm.INT, 2)}),
}


def main(argv):
    if '--inject' in argv:
        nm = argv[argv.index('--inject') + 1]
        INJECT[nm]()
        print('injected: %s' % nm)
    out, n = run('-v' in argv)
    got = dict(steps=n, matched=out['matched'], stop=out['stop'][0] if out['stop'] else None)
    if '--inject' not in argv and (got != PINNED or out['picks'] != PICKS_PINNED):
        print('FAIL the furthest point moved: %s, %d picks; pinned %s, %d picks (update PINNED)'
              % (got, out['picks'], PINNED, PICKS_PINNED))
        return 1
    return 1 if out['fail'] or out['stop'] else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
