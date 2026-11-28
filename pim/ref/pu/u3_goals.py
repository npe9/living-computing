#!/usr/bin/env python3
"""U3, second step: a multi-goal KL1 program on ICOT's held microcode
(ref/pu/pu.py), started by the firmware's own boot words and run through
the firmware's own enqueue_goal and proceed, against ref/pimm/pimm.py at
every scheduler pick.

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

The boot (second step, 2026-11-27).  Before the driver, start's held words
write the scheduler state the program reads (the first step's INITIAL
stand-in, gone), in this order (boot(); 199 held words, pinned):
  - 2021, entry 2001's word: reset_PMPF (MCF EM1 02, EM2 1a; the cold
    start 2000 resets it at 2014 too, on a path that stops at 2007 here);
  - 204b-2052, start's heap top: R1f := the parameter 1a0 + 4a rounded up
    to 16 (u2_append, unchanged);
  - 3380 (2065's call in 2063's refill sequence): R1b's refill carves 8
    records of 16 cells from R1f, cell 0 the link (the first {VECT0x,
    next}, the others {REFo, next}: 3370's TGIF stamp, a held answer
    where the first step's seed had VECT0x throughout), the last nil;
    R1f += 80.  pu.RULES['alu_with_one'] decided here;
  - 209f-20a8, start's crr arm: R11 := {INTo, 36}; R16 := {INTo, 2} (20a0's
    S1 immediate EM2 = 2, pu.S1_IMM, moved to R16 at 20a1); COND := PMPF
    (209f) and 20a1's JMPF c ('goto if not cond', rassy) takes 20a6: R15 :=
    {INTo, 17}; W1f := 0 (20a8).  20a9-20c0 (parameter copies, R0e, R07)
    are read, not run: they read the cells b8 / ba, which nothing gives;
  - 20e7-210b (whole, 45 words): W1a := [a0]; R13 := {FPREC, record 0}
    and its 16 cells; [1a0 + 4f] := R13; R12 := {INTo, 0} (2102); R14 :=
    {HOOKo, record 1} (2104), the boot goal: cell 0 {GOAL, 0}, cell 12
    {COD, 34} (2106-2108's immediates EM3 2 + 50), 13 {INTo, 0}, 14 R13,
    15 nil (210a-210b, 209e); [[b6]] := R14 (the Goal Stack Entry Table
    entry for priority 0: INFERENCE);
  - 202d-2030: R10 := a third record off R1b (3349); 'end'.
So R13, R12, R14, R15, R16, W1f, R1b's list and R10 are firmware-written
(boot_check: the refill's first three records are R13, R14 and R10, the
other five stay on R1b, nil-ended).

R16 (rassy 'ccc') is settled by the boot: 2 = the queue's length (the
boot goal) + 1 (the goal about to run, the boot module's first goal, here
the driver).  Checked after the boot and after every enqueue_goal and
proceed (r16_check): R16 = length of R14's chain + 1 throughout.  The first
step's two readings (0, the queue length; 1, the live goals with an empty
queue) were both on an OURS start; the README's "20a0-20a1 gives 0" was
read before S1_IMM and is withdrawn.

What is still OURS, each item:
  - the boot's inputs: the entry (2001's reset of PMPF rather than 2003's
    set: the Pseudo PIM/m CSP prints "$GO/PIMos <Start Address> ... = 2000
    (Multi-PSI)", whose path resets it; the second run below takes 2003);
    the parameter cells 1a0 + 4a (pimm.py's heap pointer, as U2), a0
    (PARAM_A0) and b6 (GSEB, PIMM.PARAM's gseb (10 : 16'B800) written as
    area << 24 | address: the encoding is INFERENCE); start's instruction
    cell (START_CELL) and its operand a, A0 (STALE: 20a1 reads it and 20a6
    overwrites what it fed); R0d (STALE, read by 3375); which calls of
    start run (2053's other refills and 2070 / 208e, 209f's tail, 20c2 are
    not run) and in what order;
  - the A stage: each instruction cell and its address from pimm.py's
    trace, in pimm.py's order (the firmware's R04 is compared at every
    branch, execute and dispatch);
  - the driver's arguments A0-A5 (the boot module is entered by
    execute_first_predicate, 2032, which passes none; read, not run);
  - the cell free lists R19 / R1a (check_pu.seed_lists) and memory:
    pimm.py's cells at the same addresses.

The walks (Prov.reads, pinned): at each pick, the R / W registers and
memory cells proceed's words read whose last writer is the harness: none
at any of the three picks (RESIDUAL_PINNED; the first step had R13 and
W1f).  Over the boot's words (R, W and A): A0, R0d, cells 1ea (1a0 + 4a),
a0 and b6 (BOOT_RESIDUAL_PINNED).  Over every other instruction (R04 and
pimm.py's cells declared apart): R19 and two of its seeded cells
(f2000000-1), and the cells 0, 123 and 124 (34a2, read_variable's pre-read
of an atomic element: the atoms' values taken as addresses, never
written, POISON, unused) (PROG_RESIDUAL_PINNED).

The third pick is not compared with pimm.py.  Under the two appends the
firmware's queue holds the boot goal where pimm.py's is empty, so
pimm.py's third proceed finds nothing (Q) while the firmware's dispatches
the boot goal: R04 = its cell 12 ({COD, 34}), R10 = {HOOKo, record 1}, R14
:= its link, nil; A0 / A1 its cells 1-2 (the arity-0 rule below).  It is
counted apart (out['boot_pick'], pinned 1): checked against the boot's own
writes only.  The empty arm 21b2 is not reached in this run any more (it
was the first step's third pick); u2_append's proceed side cases still
run it (the empty queue, crr 8).  Where a link or R14 is the boot record
and pimm.py's is 0 (the enqueue's cell 15, R14 after the second pick),
the compare takes that as the declared difference (same_link).

What runs held: every instruction's E stage, including the scheduler:
set_value writes the goal record R10 + x (3187); enqueue_goal (4c00-4c07)
stamps cell 0 {GOAL, n}, writes cells 12-15 ({COD, label}, R12, R13, the
old R14), links the record at the head of R14, pops a fresh record off
R1b into R10 and counts R16 up; proceed (216c-2224) pushes the finished
record on R1b, takes R14's head into R10, loads its code into R04 and its
arguments into A0.., and R14 := its link.

Compared, per instruction (pimm.py's trace split at its I lines):
  - set_value x, y: pimm.py's A line (argv[x]) against the firmware's
    cell R10 + x (the record being built: argv[k] IS cell k, INFERRED from
    3187's write; pseudo_pimm_microcode.md section 18); no other write;
  - enqueue_goal n: pimm.py's new goal record against the firmware's (the
    old R10): {GOAL, n}, the arguments (cells 1..n against pimm.py's), the
    code ({COD, label}), the link (cell 15 = the old R14, which must be
    the firmware record of pimm.py's previous rq, or the boot record for
    0); R14 := {HOOKo, record}; R10 := the popped record; no other cell
    written; R16 = queue + 1;
  - proceed: the PICK.  pimm.py's next goal (its G line) against the
    firmware's dispatch: R04 = {COD, its code}, R10 = {HOOKo, the record
    the firmware made for that goal}, A0.. = pimm.py's R lines, R14 = the
    record of pimm.py's rq after the pick (the boot record for 0); the
    only cell written is the finished record's cell 0 (pushed on R1b:
    declared, as u2_append's 'free'); R16 = queue + 1.  The boot goal's
    pick: above;
  - at each pick, provenance: R14 as proceed reads it, and every cell of
    the dispatched record proceed reads (0..n, 12-15), were last written
    by a held word of this run (not by the harness);
  - every other instruction: u2_append.compare and compare_next_pc (the
    U2 comparison, unchanged).

    python3 ref/pu/u3_goals.py [-v] [--inject NAME]

Exit 0 when every instruction executed matched, the furthest point, the
picks, the boot's word counts and the three walks are as pinned, and the
second run (entered at 2003: set_PMPF, 2022) stops where pinned: at 20a3,
the read of the reduction limit at 10 + start's operand a (STALE); 1
otherwise.

Observed 2026-11-27 (U3 second session): the boot 199 held words; 41 of
41 instructions executed and matched, 173 held microinstructions; 3 picks,
2 compared with pimm.py and 1 the boot goal (firmware only), no mismatch;
no harness-written state read at any pick.
Injections (in-process, no file edited), observed (each alone; every
other check unchanged up to the first stop or FAIL).  Since the second
step a run that stops early also prints MOVED (its pins are not reached);
the observed point is the first STOP / FAIL line.
  reseed_r14         FAIL at 8 (the first pick): provenance, R14 last
                     written by the harness (nothing else differs)
  ccf_bits           STOP at 8, 2250 (cells 13 / 14 from MDR1: cell 14
                     is not R13, the other-parent call; the rule changed
                     after the boot)
  ccf_bits_boot      the same before the boot: STOP in the boot, 334e
                     (3349's pop read through the bit reading)
  jmpf8_goto_off     STOP at 3, 4c01 (changed after the boot)
  jmpf8_goto_off_boot  STOP in the boot, 3370 (the refill's JMPF 8)
  wsel_d_off         STOP at 3, 4c01 (W0d never set)
  execute_mdr1_stale STOP at 24 (the second pick), 216e (crr STALE)
  enq_head_mar1      STOP at 3, 4c00 (MAR2 never set)
  enq_label_mdr2     STOP at 3, 4c04 (STALE written)
  enq_label_plus1    FAIL at 3: cell 12 one past pimm.py's code
  pg_swap            FAIL at 8: R10 and R14 against pimm.py's pick
  free_undeclared    FAIL at 8 (the first pick): the freed record's cell
                     0 (the refill left {REFo, next} there, the push
                     writes {VECT0x, old R1b}; at 24 in the first step,
                     whose seed had VECT0x already)
  slit_pending       STOP at 3, 4c08 (the JMPF 8 goto taken; ALF shift)
  setv_addr_op       FAIL at 0: set_value's cell compare (R10 + 1 empty,
                     the cell written at R10 + 4)
  rec_poke           FAIL at 3: enqueue_goal's argument compare (cell 2
                     rewritten by the harness before the enqueue)
  rfar_off           FAIL at 8: the pick's A-register compare (A0, A2)
  re-homed as post-boot harness rewrites (were INITIAL edits):
  empty_int0         R14 := {INT, 0}: FAIL at the boot check (R14 not the
                     refill's second record)
  r16_zero           R16 := 0: FAIL at the boot check (R16 0, queue 1 + 1)
  crr_two            R15 := 2: STOP at 8 (the first pick), 217d (crr run
                     out: 217c forms PMPF, now given; 217d's JMPF d, a
                     conditional call, is not decided); 217c in the first
                     step
  new (second step):
  c_on_true          JMPF c taken on COND: the boot takes 20a2, STOP at
                     20a3 (as the second run)
  pmpf_cond_off      STOP in the boot, 209f (cond PMPF unknown)
  mcf_pmpf_off       STOP in the boot, 2021 (MCF EM1 02 raises)
  wide_mcf_off       STOP in the boot, 20a8 (SC2F b with MCF's EM1 07)
  with_one_plain     add_with_one as a + b: FAIL at the boot check (R10
                     STALE, R1b's list e00080b0 e00080c0 e00080cf 0: the
                     links one short)
  r13_harness        R13 rewritten (same value) after the boot: no STOP
                     or FAIL; MOVED, the pick walk R13 at all three picks
                     and the program walk R13 (residual pins)
  r16_plus1          R16 + 1 after the boot: FAIL at the boot check
  ccf_wait_raise     CCF 04 'wait' raises: STOP in the boot, 202f
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

# The boot (held, U3 second session; module docstring "The boot"): the
# scheduler state no instruction of the program writes first is written
# by start's own words, run before the driver.  What the boot still needs
# from outside (OURS): the PMPF entry, two parameter cells, start's
# instruction cell and its operand (STALE), and the order of the calls.
PMPF_ENTRY = 0x2021           # entry 2001's word: reset_PMPF (2000's path resets at 2014)
PMPF_SET_ENTRY = 0x2022       # entry 2003's word: set_PMPF (the second run)
START_CELL = (0x23, 0x7b << 24)   # start (decode 37b), operands 0: OURS
GSEB = 0x1000b800             # [b6]: PIMM.PARAM gseb (10 : 16'B800) as area << 24 | address (OURS)
PARAM_A0 = (pimm.INT, 0)      # [a0]: a parameter cell, meaning not read (OURS)
CRR_ARM_END = 0x20a9          # 209f-20a8 run; 20a9-20c0 read, not run
R1B_REFILL, CRR_ARM, FP_GOAL, START_TAIL = 0x3380, 0x209f, 0x20e7, 0x202d
POST_BOOT = {}                # injections: registers the harness rewrites after the boot
AFTER_BOOT = []               # injections: rule changes made after the boot

PINNED = dict(steps=41, matched=41, stop=None)
PICKS_PINNED = 3              # 2 compared with pimm.py + the boot goal's (firmware only)
BOOT_PINNED = {'2021': 1, '204b': 8, '3380': 132, '209f-20a8': 6, '20e7': 45, '202d-2030': 7}
# With PMPF set (entry 2003's 2022): the boot takes 20a2, whose address is
# start's operand a (STALE): STOP in the boot, at 20a3 (the read).
PINNED_PMPF_SET = '20a3'
# At each pick, the registers and memory cells proceed's words read whose
# last writer is the harness, in order of the picks (Prov.reads).
RESIDUAL_PINNED = [[], [], []]
# The same walk over the boot's words.
BOOT_RESIDUAL_PINNED = ['A00', 'R0d', 'cell 1ea', 'cell a0', 'cell b6']
# And over every other instruction's words (pimm.py's cells, the memory
# stand-in, and R04, the A stage's, left out).
PROG_RESIDUAL_PINNED = ['R19', 'cell 0', 'cell 123', 'cell 124', 'cell f2000000',
                        'cell f2000001']

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
            self.reg[('R', n)] = 'harness'
        for n in p.w:
            self.reg[('W', n)] = 'harness'
        for a in p.mem:
            self.mem[a] = 'harness'

    def firmware(self, p, n0):
        for c in p.cycles[n0:]:
            self.commit(c)

    def commit(self, c):
        for (f, n), _v in c['reg_writes']:
            if f in ('R', 'W'):
                self.reg[(f, n)] = 'firmware'
        for a, _v in c['mem_writes']:
            self.mem[a] = 'firmware'

    def reads(self, p, n0, files=('R', 'W')):
        """Walk the words run since n0 in order: every register-file entry
        (of files) a word read, and every memory cell it read, whose last
        writer was the harness.  Run before firmware(n0)."""
        reg, mem = dict(self.reg), dict(self.mem)
        res = set()
        for c in p.cycles[n0:]:
            for nm, _v in c['reg_reads']:
                if nm[:1] in files and len(nm) == 3:
                    key = (nm[0], int(nm[1:], 16))
                    if reg.get(key, 'harness') != 'firmware':
                        res.add('%s%02x' % key)
            for a, _v in c['mem_reads']:
                if mem.get(a, 'harness') != 'firmware':
                    res.add('cell %x' % a)
            for (f, n), _v in c['reg_writes']:
                if f in files:
                    reg[(f, n)] = 'firmware'
            for a, _v in c['mem_writes']:
                mem[a] = 'firmware'
        return res


def other_writes(p, mem0, allowed):
    return ['heap %x: firmware wrote %s' % (a, fmt(p.mem.get(a)))
            for a in sorted(set(p.mem) | set(mem0))
            if p.mem.get(a) != mem0.get(a) and a not in allowed]


def an_unchanged(p, an0, what):
    return ['%s: firmware wrote A%d %s' % (what, i, fmt(p.an.get(i)))
            for i in sorted(set(p.an) | set(an0)) if p.an.get(i) != an0.get(i)]


def run_upto(p, upc, stop):
    """Run held words from upc until the next would be stop (a declared
    boundary inside a routine: the rest is read, not run)."""
    n0 = len(p.trace)
    while upc != stop:
        if upc is None or upc == -1:
            raise PU.Unmodelled(p.trace[-1][0], 'left the routine before %04x' % stop)
        upc = p.step(upc)
    return len(p.trace) - n0


def boot(p, hp, entry=None):
    """start's held words, in place of the old INITIAL stand-in (module
    docstring "The boot").  Returns [(what, words)]; raises Unmodelled."""
    p.ir = START_CELL                               # OURS: start's cell
    p.an[0] = PU.STALE                              # OURS: its operand a (A0), not known
    p.mem[0xa0] = PARAM_A0                          # OURS: parameter cells
    p.mem[0xb6] = (pimm.INT, GSEB)
    done = []
    p.step(PMPF_ENTRY if entry is None else entry)  # the entry's flag word (OURS: which)
    done.append(('%04x PMPF' % (PMPF_ENTRY if entry is None else entry), 1))
    done.append(('204b heap top', U2.boot_heap_top(p, hp)))
    done.append(('3380 R1b refill', p.call(R1B_REFILL)))
    done.append(('209f-20a8 R11 R16 R15 W1f', run_upto(p, CRR_ARM, CRR_ARM_END)))
    done.append(('20e7 R13 R12 R14', p.call(FP_GOAL)))
    done.append(('202d-2030 R10', p.run(START_TAIL)))
    return done


REFILL_RECORDS = 8            # 3380's records (observed); the boot pops 3 (R13, R14, R10)


def boot_check(p, hp):
    """The boot's records: R13 (the foster parent), R14 (the boot goal)
    and R10 come off R1b's refill, which carved REFILL_RECORDS 16-cell
    records from the heap top hp; the rest stay on R1b, chained through
    cell 0 to nil."""
    fails = []
    recs = [hp + 16 * k for k in range(REFILL_RECORDS)]
    got = [(n, p.r.get(n)) for n in (0x13, 0x14, 0x10)]
    if [w[1] if isinstance(w, tuple) else None for _, w in got] != recs[:3]:
        fails.append('boot: R13 / R14 / R10 %s, want the refill\'s first three records %s'
                     % (', '.join(fmt(w) for _, w in got), ', '.join('%x' % a for a in recs[:3])))
    a, rest = p.r.get(0x1b), []
    while isinstance(a, tuple) and a != NIL and len(rest) < 64:
        rest.append(a[1])
        a = p.mem.get(a[1])
    if rest != recs[3:] or a != NIL:
        fails.append('boot: R1b\'s list %s (end %s), want %s'
                     % (' '.join('%x' % r for r in rest), fmt(a), ' '.join('%x' % r for r in recs[3:])))
    return fails


def chain(p, w):
    """R14's queue as a list of records (cell 15 links, nil-ended)."""
    out = []
    while w and w[0] == HOOKO and len(out) < 64:
        out.append(w[1])
        w = p.mem.get(w[1] + 15)
    return out if w == NIL else out + [('end', w)]


def r16_check(p, what):
    """R16 (ccc) = the queue's length + 1 (the running goal): held at the
    boot (20a1 R16 := 2 with 2104's one queued record)."""
    q = chain(p, p.r.get(0x14))
    r16 = p.r.get(0x16)
    if not r16 or r16[1] != len(q) + 1:
        return ['%s: R16 %s, queue length %d + 1' % (what, fmt(r16), len(q))]
    return []


def run(verbose=False, entry=None):
    m, s0, steps, pc0 = pimm_run()
    p = PU.PU()
    p.mem.update(s0['mem'])
    check_pu.seed_lists(p, U2.NFREE)
    U2.seed_execute(p)
    out = {'done': 0, 'matched': 0, 'words': 0, 'stop': None, 'fail': None, 'picks': 0,
           'dispatched': 0, 'empty': 0, 'boot_pick': 0, 'residual': [], 'boot': None,
           'boot_residual': None, 'boot_stop': None, 'boot_words': None,
           'prog_residual': set()}
    prov = Prov()
    prov.harness(p)
    try:
        done = boot(p, m.hp, entry)
    except PU.Unmodelled as e:
        out['boot_stop'] = str(e)
        print('STOP boot: %s' % e)
        return out, len(steps)
    out['boot'] = done
    out['boot_words'] = dict((w.split()[0], k) for w, k in done)
    out['boot_residual'] = sorted(prov.reads(p, 0, ('R', 'W', 'A')))
    prov.firmware(p, 0)
    globals().update(BOOTREC=p.r[0x14][1] if p.r.get(0x14, (0,))[0] == HOOKO else None)
    print('boot: %s; %d held words' % (', '.join('%s (%d)' % d for d in done),
                                       sum(n for _, n in done)))
    for f in AFTER_BOOT:                            # injections
        f()
    for n, v in POST_BOOT.items():                  # injections
        if v is None:
            v = p.r[n]                              # the same value, rewritten
        elif v == 'plus1':
            v = (p.r[n][0], p.r[n][1] + 1)
        p.r[n] = v
        prov.reg[('R', n)] = 'harness'
    for i, w in enumerate(s0['reg']):
        p.an[i] = w                                 # OURS: the first goal's arguments
    r16_bad = boot_check(p, (m.hp + 15) & ~15) + r16_check(p, 'after the boot')
    rn = check_pu.Rename()
    for a in s0['mem']:
        rn.f2p[a] = rn.p2f[a] = a
    fw2pg, pg2fw = {}, {}                           # goal records: firmware <-> pimm.py
    prev_after = s0
    if r16_bad:
        out['fail'] = (-1, None, 'boot', r16_bad)
        print('FAIL boot: %s' % '; '.join(r16_bad))
        steps = []
    for k, (pc, cellv, lines, after) in enumerate(steps):
        p.ir, p.pc = cellv, m.load + pc
        p.r[R_PC] = (COD, (m.load + pc + 1) & 0xffffffff)
        prov.reg[('R', R_PC)] = 'harness'
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
        if base == 'proceed':
            out['residual'].append(sorted(prov.reads(p, n0)))
        else:                                       # the rest of the program (s0's cells: declared)
            out['prog_residual'] |= set(r for r in prov.reads(p, n0) if r != 'R04' and not (
                r.startswith('cell ') and int(r[5:], 16) in s0['mem']))
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
            kind, fails = cmp_proceed(p, m, rn, lines, after, an0, mem0, r0, fw2pg, pg2fw,
                                      steps[k + 1][0] if k + 1 < len(steps) else None, n0)
            fails = prov_bad + fails
            out[kind] += 1
            empty = kind
        else:
            fails = U2.compare(p, m, rn, rl, after, name, an0, mem0)
            fails += U2.compare_next_pc(p, m, pc, after, name, r04_0)
        if base in ('enqueue_goal', 'proceed'):
            fails += r16_check(p, name)
        if fails:
            out['fail'] = (k, pc, name, fails)
            print('FAIL %2d %5d %-22s %d words: %s' % (k, pc, name, nw, '; '.join(fails)))
            break
        out['matched'] += 1
        print('ok   %2d %5d %-22s %d words%s' % (k, pc, name, nw,
                                                ('  pick %d%s' % (out['picks'], {
                                                    'empty': ' (empty)', 'boot_pick': ' (the boot goal:'
                                                    ' firmware only)'}.get(empty, '')))
                                                if base == 'proceed' else ''))
        if verbose:
            for c in p.cycles[n0:]:
                print('      %04x %016x' % (c['micro_pc'], c['microword']))
        if PG_SWAP and base == 'enqueue_goal' and len(pg2fw) == 2:
            (g1, f1), (g2, f2) = list(pg2fw.items())     # injection: the map crossed
            pg2fw.update({g1: f2, g2: f1})
            fw2pg.update({f1: g2, f2: g1})
        if POKE is not None and k == POKE[0]:
            p.mem[p.r[0x10][1] + POKE[1]] = POKE[2]
            prov.mem[p.r[0x10][1] + POKE[1]] = 'harness'
        if RESEED is not None and k == RESEED:
            p.r[0x14] = tuple(p.r[0x14])            # injection: the harness writes R14
            prov.reg[('R', 0x14)] = 'harness'
        prev_after = after
    print('scheduler state read at each pick whose last writer is the harness (OURS): %s'
          % '; '.join('pick %d %s' % (i + 1, ', '.join(r) or 'none')
                      for i, r in enumerate(out['residual'])))
    print('held state read by the boot whose last writer is the harness (OURS): %s'
          % ', '.join(out['boot_residual']))
    out['prog_residual'] = sorted(out['prog_residual'])
    print('read by the other instructions (pimm.py\'s cells and R04 declared apart): %s'
          % ', '.join(out['prog_residual']))
    print('%d of %d instructions executed and matched, %d held microinstructions; '
          '%d picks (%d compared with pimm.py, %d empty, %d the boot goal, firmware only)%s'
          % (out['matched'], len(steps), out['words'], out['picks'], out['dispatched'],
             out['empty'], out['boot_pick'], '' if not out['stop']
             else '; first stop: instruction %d (%d %s)' % out['stop'][:3]))
    return out, len(steps)


def check_provenance(p, prov):
    """At proceed's entry: R14, and every cell of R14's head record that
    proceed reads, last written by a held word."""
    bad = []
    if prov.reg.get(('R', 0x14)) != 'firmware':
        bad.append('provenance: R14 %s last written by the %s' % (fmt(p.r.get(0x14)),
                                                                  prov.reg.get(('R', 0x14))))
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


BOOTREC = None                # the boot's goal record (2104-210b), set by run()


def link_of(w, fw2pg):
    """A firmware link value as pimm.py's: nil -> 0, {HOOKo, r} -> record;
    the boot's record -> 'boot' (the declared difference: under the
    driver's goals the firmware's queue holds the boot goal, pimm.py's is
    empty)."""
    if w == NIL:
        return 0
    if w == (HOOKO, BOOTREC):
        return 'boot'
    if w and w[0] == HOOKO and w[1] in fw2pg:
        return fw2pg[w[1]]
    return ('unmapped', w)


def same_link(fw, pg):
    """The firmware's link against pimm.py's; the boot record stands where
    pimm.py has none (declared)."""
    return fw == pg or (fw == 'boot' and pg == 0)


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
    if not same_link(link_of(p.mem.get(rec + 15), fw2pg), m.mem[g + G_LINK][1]):
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
    if not gl and BOOTREC is not None and p.r.get(0x10) == (HOOKO, BOOTREC):
        # pimm.py's queue is empty; the firmware's holds the boot goal and
        # dispatches it (firmware only: checked against the boot's own
        # writes, not against pimm.py)
        if 'Q' not in lines:
            fails.append('pimm.py neither picks a goal nor ends')
        if p.r.get(R_PC) != p.mem.get(BOOTREC + 12) or p.r.get(R_PC, (0,))[0] != COD:
            fails.append('boot goal: R04 %s, the record\'s cell 12 %s'
                         % (fmt(p.r.get(R_PC)), fmt(p.mem.get(BOOTREC + 12))))
        if p.r.get(0x14) != p.mem.get(BOOTREC + 15) or p.r.get(0x14) != NIL:
            fails.append('boot goal: R14 %s, the record\'s link %s'
                         % (fmt(p.r.get(0x14)), fmt(p.mem.get(BOOTREC + 15))))
        for i in sorted(set(p.an) | set(an0)):
            if p.an.get(i) != an0.get(i) and not (i < 2 and p.an.get(i) == p.mem.get(BOOTREC + 1 + i)):
                fails.append('boot goal: A%d written %s' % (i, fmt(p.an.get(i))))
        return 'boot_pick', fails
    if not gl:                            # the empty pick
        ran = [u for u, _ in p.trace[n0:]]
        if 'Q' not in lines:
            fails.append('pimm.py neither picks a goal nor ends')
        if U2.EMPTY_ARM not in ran:
            fails.append('pimm.py picks no goal; the firmware did not take the empty arm')
        if p.r.get(R_PC) != r0.get(R_PC):
            fails.append('pimm.py picks no goal; the firmware dispatched R04 %s' % fmt(p.r.get(R_PC)))
        fails += an_unchanged(p, an0, 'empty pick')
        return 'empty', fails
    g = m.load + int(gl[0].split()[1])
    code = m.mem[g + G_CODE][1]
    if next_pc is None or code != m.load + next_pc:
        fails.append('pimm.py\'s pick %x has code %x, its next instruction %r' % (g, code, next_pc))
    if p.r.get(R_PC) != (COD, code):
        fails.append('R04 %s, pimm.py\'s next goal\'s code {COD, %x}' % (fmt(p.r.get(R_PC)), code))
    if g not in pg2fw:
        return 'dispatched', fails + ['pimm.py picks record %x, which no enqueue_goal made' % g]
    if p.r.get(0x10) != (HOOKO, pg2fw[g]):
        fails.append('R10 %s, the firmware record of pimm.py\'s pick {HOOKo, %x}'
                     % (fmt(p.r.get(0x10)), pg2fw[g]))
    # pimm.py's rq after its pick: its state when the goal's first
    # instruction is taken (after['rq'])
    want = after['rq']
    if not same_link(link_of(p.r.get(0x14), fw2pg), want):
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
    return 'dispatched', fails


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


def _poke_record():
    # the harness writes the record's cell 2 before the first enqueue_goal
    globals().update(POKE=(2, 2, (pimm.INT, 0xbad)))


POKE = None                   # injection 'rec_poke': (before step k, cell, value)


def _post_boot(n, v):
    POST_BOOT[n] = v


def _r13_harness():
    POST_BOOT[0x13] = None                # placeholder: the same value, rewritten (run)


INJECT = {
    'setv_addr_op': lambda: SU.FORMS.update(set_value=('y', 'arg_op')),
    'rec_poke': _poke_record,
    'rfar_off': lambda: PU.RULES.update(dstf_c_rfar=False),
    'reseed_r14': _reseed,
    'ccf_bits': lambda: AFTER_BOOT.append(_ccf_bits),
    'jmpf8_goto_off': lambda: AFTER_BOOT.append(lambda: PU.RULES.update(jmpf8_goto_if=False)),
    # the same two rule changes made before the boot (where the refill
    # and the pop already use them)
    'ccf_bits_boot': _ccf_bits,
    'jmpf8_goto_off_boot': lambda: PU.RULES.update(jmpf8_goto_if=False),
    'wsel_d_off': lambda: PU.RULES.update(wsel_d_em1=False),
    'execute_mdr1_stale': lambda: setattr(SU, 'EXECUTE_MDR1_EMO1', False),
    'enq_head_mar1': lambda: SU.ENQ_HEAD.update({2: 'MAR1'}),
    'enq_label_mdr2': lambda: _enq_label('mdr2'),
    'enq_label_plus1': lambda: _enq_label('plus1'),
    'pg_swap': lambda: globals().update(PG_SWAP=True),
    'free_undeclared': lambda: globals().update(DECLARE_FREE=False),
    'slit_pending': lambda: U2.EXECUTE_FLAGS.update(slit_check=True),
    # re-homed (U3 second session): post-boot harness rewrites of R14,
    # R16, R15 (were INITIAL edits)
    'empty_int0': lambda: _post_boot(0x14, (pimm.INT, 0)),
    'r16_zero': lambda: _post_boot(0x16, (pimm.INT, 0)),
    'crr_two': lambda: _post_boot(0x15, (pimm.INT, 2)),
    # the boot's rules and checks (U3 second session)
    'c_on_true': lambda: PU.CJUMP_TAKEN_ON.update({0xc: True}),
    'pmpf_cond_off': lambda: PU.FLAG_CONDS.pop(0x1a),
    'mcf_pmpf_off': lambda: PU.RULES.update(mcf_sub_flags=False),
    'wide_mcf_off': lambda: PU.RULES.update(sc2_wide_mcf=False),
    'with_one_plain': lambda: PU.RULES.update(alu_with_one='plain'),
    'r13_harness': _r13_harness,
    'r16_plus1': lambda: _post_boot(0x16, 'plus1'),
    'ccf_wait_raise': lambda: PU.CCF_RASSY.pop(0x04),
}


def residual_moved(out):
    return (out['residual'] != RESIDUAL_PINNED or out['boot_residual'] != BOOT_RESIDUAL_PINNED
            or out['boot_words'] != BOOT_PINNED or out['prog_residual'] != PROG_RESIDUAL_PINNED)


def main(argv):
    inj = '--inject' in argv
    if inj:
        nm = argv[argv.index('--inject') + 1]
        INJECT[nm]()
        print('injected: %s' % nm)
    out, n = run('-v' in argv)
    got = dict(steps=n, matched=out['matched'], stop=out['stop'][0] if out['stop'] else None)
    moved = (got != PINNED or out['picks'] != PICKS_PINNED or out['boot_pick'] != 1
             or out['dispatched'] != 2 or residual_moved(out))
    if moved:
        print('%s the furthest point moved: %s, %d picks (%d compared, %d boot goal), boot %s,'
              ' residual %s, boot residual %s; pinned %s, %d picks, boot %s, residual %s,'
              ' boot residual %s' % ('MOVED' if inj else 'FAIL', got, out['picks'],
                                     out['dispatched'], out['boot_pick'], out['boot_words'],
                                     out['residual'], out['boot_residual'], PINNED, PICKS_PINNED,
                                     BOOT_PINNED, RESIDUAL_PINNED, BOOT_RESIDUAL_PINNED))
    if inj:
        return 1 if out['fail'] or out['stop'] or out['boot_stop'] or moved else 0
    if moved or out['fail'] or out['stop'] or out['boot_stop']:
        return 1
    # PMPF's other value (entry 2003's set_PMPF, 2022): the boot's crr arm
    # reads the reduction limit at 10 + start's operand a, which the
    # harness does not know: pinned at that stop.
    print('--- the same run entered at 2003 (2022 set_PMPF)')
    out1, _ = run(False, entry=PMPF_SET_ENTRY)
    if not (out1['boot_stop'] or '').startswith(PINNED_PMPF_SET + ':'):
        print('FAIL the PMPF-set run moved: boot stop %r, pinned at %s'
              % (out1['boot_stop'], PINNED_PMPF_SET))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
