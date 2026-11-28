#!/usr/bin/env python3
"""U3, second and third steps and U3d's first: KL1 programs on ICOT's held microcode
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
    cell (START_CELL) and its operand a, A0 (STALE; no longer read since
    the third step: 20a1's SC2F a is the immediate b0); W1c (STALE, read by 3375;
    R0d until U3d, when select d with WRBF clear became W(EM1)); which calls of
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
W1f).  Over the boot's words (R, W and A): A0, W1c (R0d before U3d), cells 1ea (1a0 + 4a),
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
the read of the reduction limit at 10 + start's operand a (STALE); and
(U3d) the programs 'suspend' and 'stream' are as pinned (SUSP_PINNED,
STREAM_PINNED and their residuals), stream's answer read from the
firmware's memory equal to pimm.py's; 1 otherwise.

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
  U3 third step (2026-11-28): c_on_true now STOPs at 20a4 (20a1's SC2F a
  immediate b0, 20a3 reads cell b0); every other append2 result above is
  unchanged.  main() also runs the program 'suspend' (SUSP_PINNED, README
  "U3, third step"); the new injections, observed on it (append2
  unchanged by all but sc2_a_opd, whose boot residual gains A00):
  cnd_noalu_poison   STOP 19, 2440 (the resumed switch's COND POISON)
  cnd_noalu_raise    STOP 10, 3314
  f_jump_raise       STOP 10, 3a34 (MCF EM1 02)
  susp_flags_rassy   STOP 10, 3a41 (a STALE COND tested)
  jmpf8_cndf_off     STOP 10, 3a3c
  alf_high_reversed  STOP 12, 1c36 (the arity test takes the big path)
  alf_high_signed    unchanged (sspb positive): not discriminated
  src_c_rfar_off     STOP 12, 1c30 (R0c)
  em1_28_false       FAIL 12: X {HOOKo, record}, want HOOKx
  em1_28_read_off    STOP 12, 1c66
  chain_row_off      STOP 10 (S stage row UNKNOWN)
  chain_row_srp      unchanged (3310 also false): WEAK
  chain_mar1_bare    FAIL 10: A0 written untagged
  interrupt_pending  STOP 12, 1c18
  sc2_a_opd          STOP 12, 3334 (ssp ffffffff: the many-variable path)
  sspb_zero          STOP 12, 3334 (the same)
  long_em1_busy      STOP 16, 4d1b
  adf2_none          STOP 16, 4d20 (the GSET path)
  adf2_pair          STOP 16, 4d3e
  sc2_e_off          STOP 16, 4d1c (W0e)
  gset_ops_off       STOP 16, 4d3b (reverse_sub)
  reverse_sub_plain, shr_by_b  unchanged (priority 0): not discriminated
  r16_queue_only     FAIL 12: R16 3, queue 1 + 1
  guard_alt_undeclared  FAIL 10: R04 against pimm.py's next instruction
  double_hook_undeclared  FAIL 12: X hooked twice by pimm.py
  atom_mrb_undeclared  FAIL 16: X {ATOMx, 0} against {ATOMo, 0}
  deref_reg_undeclared  FAIL 19: A0 := nil, pimm.py no write
  U3d first step (2026-11-28): main() also runs the program 'stream'
  (STREAM_CELLS, compiled by the held PIMOS 3.6 compiler from
  STREAM_SOURCE, re-made by ref/pu/u3d_compile.py; README "U3d, first
  step"): go([1], A, B), 64 of 68 matched + 4 declared skips, 407 held
  words, 5 picks (4 compared), 2 suspends, 1 bind waking 2, answer A = B
  = [1] = pimm.py's.  Every append2 / suspend result above is unchanged
  but for the boot residual W1c (was R0d) and double_hook_undeclared's
  message ("once per goal").  The existing injections' stream results
  are in the README; chain_row_srp, unchanged on suspend, STOPs stream at
  24 (0c74: row 4 instead of 5 at get_bound_value), so it is no longer
  WEAK.  New, observed on stream (append2 / suspend unchanged unless said):
  rvwd_form_arg      FAIL 19 (reg 2)
  get_nil_form_y     STOP 32, 0d22 (MAR1 STALE)
  chain_odpf4_off    STOP 24 (S stage row UNKNOWN for ODPF 4)
  wsel_d_w_off       STOP 24, 0c0a (W18 never set); append2 and suspend
                     MOVED (boot residual R0d)
  chain_match_off    FAIL 35 (A0, and S's cell freed)
  tdar_odpf3_off     STOP 38, 31a1 (case_branch without a set-up)
  w1c_unset          STOP in the boot, 3375 (all three programs)
  guard_alt_retry_off  FAIL 8 (R04)
  chain_link_nil     FAIL 16 (cell 15 nil, want the old hook)
  waiters_raw        FAIL 11; suspend MOVED too (X hooked twice)
  wake_loop_reversed FAIL 24 (woken records' links)
  read_indirect_undeclared  FAIL 37
  read_indirect_carried_off FAIL 42 (put_value's copy)
  fresh_mrb_undeclared      FAIL 38
  fresh_mrb_carried_off     FAIL 41 (get_bound_value's copy)
  sp_set_reused_off  FAIL 38 (sp)
  deref_reg_marked_off  FAIL 35
  setvar_form_op     FAIL 1 (set_marked_variable's record cell)
  answer_poke        FAIL at the answer (A1 = [2])
  wait_atom_plus1    FAIL 31 (R04)
  wait_atom_own      unchanged (the operand is the constant): NOT
                     discriminated
  free_undeclared    FAIL 11 on stream (the given-back record's cell 0)
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
from pimm_layout import G_LINK, G_STATUS, G_CODE, G_ARGN, G_ARGS, SUSPENDED, S_NEXT, S_GOAL  # noqa: E402
from pimm_layout import READY as pimm_layout_READY  # noqa: E402

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
# [b4]: the parameter cell the first noting (3a3c-3a3e, SC2F a's
# immediate b4) and suspend (1c60-1c63) read: taken as PIMM.PARAM's sspb
# (10 : 16'400), the suspension stack base, written as GSEB is (area << 24
# | address, OURS / INFERENCE on the encoding).  3a3f makes R17 (ssp) :=
# [b4] - 1, the empty stack; 1c64 tests [b4] above R17.  Discriminated
# only as 'not ffffffff + 1': [b4] = 0 makes R17 ffffffff and 1c65 takes
# the many-variable path (the injection 'sspb_zero').
SSPB = 0x10000400
PARAM_B4 = (pimm.INT, SSPB)
# [b7]: PIMM.PARAM's gsesh 16'18, the Goal Stack Entry Table's shift count
# (U2's "b7 / b6 = gsesh / gseb by place", INFERENCE; the boot reads [b6]
# as gseb).  Read by the wake path at 4d3a.  OURS; NOT discriminated
# (the woken goal's priority is 0).
GSESH = 0x18
CRR_ARM_END = 0x20a9          # 209f-20a8 run; 20a9-20c0 read, not run
R1B_REFILL, CRR_ARM, FP_GOAL, START_TAIL = 0x3380, 0x209f, 0x20e7, 0x202d
POST_BOOT = {}                # injections: registers the harness rewrites after the boot
# U3 third step: R17 (rassy 'ssp') and R18 ('sst'), the suspension stack's
# pointer and its cache (VPIM D_SuspendStackPtr / D_SuspendStackCache),
# are written by no held word the boot runs (a scan of start, 2000-210e,
# finds no writer); the first noting reads both before it writes them
# (3a33 MAR1 := R18, 3a3c MAR2 := R17) and overwrites both (3a3e, 3a3f).
# OURS: STALE (a value the harness does not know), so a run that ends
# shows the values do not matter on its path.
SUSP_STALE = (0x17, 0x18)
# 'cond interrupt' (pu.FLAG_CONDS 20), read by suspend: OURS, false (a
# single PE, nothing pending), as U2's interrupt_all.
SUSP_FLAGS = {'interrupt': False, 'csbrk': False}
AFTER_BOOT = []               # injections: rule changes made after the boot

PINNED = dict(steps=41, matched=41, stop=None)
PICKS_PINNED = 3              # 2 compared with pimm.py + the boot goal's (firmware only)
BOOT_PINNED = {'2021': 1, '204b': 8, '3380': 132, '209f-20a8': 6, '20e7': 45, '202d-2030': 7}
# With PMPF set (entry 2003's 2022): the boot takes 20a2, MAR1 := R05 +
# b0 (20a1's SC2F a immediate, pu.RULES['sc2_a_imm'], U3 third step;
# before, start's operand a, STALE, and the stop was the read at 20a3):
# 20a3 reads parameter cell b0, the reduction limit, which no harness
# gives: STOP at 20a4 (the compare on it).
PINNED_PMPF_SET = '20a4'
# At each pick, the registers and memory cells proceed's words read whose
# last writer is the harness, in order of the picks (Prov.reads).
RESIDUAL_PINNED = [[], [], []]
# The same walk over the boot's words.
BOOT_RESIDUAL_PINNED = ['W1c', 'cell 1ea', 'cell a0', 'cell b6']
# And over every other instruction's words (pimm.py's cells, the memory
# stand-in, and R04, the A stage's, left out).
PROG_RESIDUAL_PINNED = ['R19', 'cell 0', 'cell 123', 'cell 124', 'cell f2000000',
                        'cell f2000001']

# U3 third step: the program 'suspend', driver([], [], X, X, [], Z): its
# first goal append(X, [], Z) suspends on X, the second append([], [], X)
# binds X and wakes it, the woken goal runs to its end, then the boot
# goal.  23 pimm.py instructions: 22 executed and matched, 1 skipped as
# declared (guard_to_alt: pimm.py's wait_nil after the firmware failed
# switch_on_non_list's guard to the alternative); picks: 3 compared with
# pimm.py (the first goal, the second after the suspend, the woken goal)
# and the boot goal's.
SUSP_PINNED = dict(steps=23, matched=22, skipped=1, stop=None, picks=4, dispatched=3,
                   boot_pick=1, suspends=1, wakes=1)
# What the suspend and the wake read whose last writer is the harness:
# the parameter cells b4 (sspb), b6 (gseb), b7 (gsesh), OURS values.
SUSP_RESIDUAL_PINNED = [('suspend', ['cell b4']), ('wake (get_value)', ['cell b6', 'cell b7'])]
# Every instruction but proceed's: R17 / R18 (SUSP_STALE, read by the
# first noting's 3a33 / 3a3c before 3a3e / 3a3f write them; the STALE
# compare at 3a3c is tested by nothing), R19 (check_pu.seed_lists' cell
# list, the resumed wait_nil's 3980), and the three parameter cells.
SUSP_PROG_RESIDUAL_PINNED = ['R17', 'R18', 'R19', 'cell b4', 'cell b6', 'cell b7']
SUSP_PICK_RESIDUAL_PINNED = [[], [], []]


# U3d first step (2026-11-28): the program 'stream', go([1], A, B) of the
# compiled module work::pc (STREAM_CELLS): c(S, A) suspends on S, c(S, B)
# suspends on S too (the second waiter: 1c73, 1c82-1c86), g([1], S) binds
# S and wakes both (get_bound_value, 3894 -> 0c0a -> 0c60 ... 4d1a), runs
# on to its end, then the two consumers run to theirs, then the boot goal.
# 68 pimm.py instructions: 64 executed and matched, 4 skipped as declared
# (guard_to_alt, the try_me_else between switch and wait_atom included:
# RETRY_SAME_ALT); 5 picks, 4 compared with pimm.py and the boot goal's;
# 2 suspends, 2 goals woken by one bind; the answer A = B = [1] read out
# of the firmware's memory equals pimm.py's.
STREAM_PINNED = dict(steps=68, matched=64, skipped=4, stop=None, picks=5, dispatched=4,
                     boot_pick=1, suspends=2, wakes=2)
# The first suspend reads A01, go's A (the program's input, OURS, as the
# driver's arguments), and b4; the wake b6 / b7, as in 'suspend'.
STREAM_RESIDUAL_PINNED = [('suspend', ['A01', 'cell b4']), ('suspend', ['cell b4']),
                          ('wake (get_bound_value)', ['cell b6', 'cell b7'])]
# R17 / R18 (SUSP_STALE), the seeded free lists R19 and R1a
# (check_pu.seed_lists: R1a since the consumers' put_reused_structure
# takes two-cell lists from it) and their cells' links, and the three
# parameter cells.
STREAM_PROG_RESIDUAL_PINNED = ['R17', 'R18', 'R19', 'R1a', 'cell b4', 'cell b6', 'cell b7',
                               'cell f2000000', 'cell f2000001', 'cell f2000002',
                               'cell f2000003', 'cell f3000000', 'cell f3000002']
STREAM_PICK_RESIDUAL_PINNED = [[], [], []]
# U3d second step, path (a) (README "U3d, second step"): both runs stop,
# pinned, before b(A) runs, so neither has an answer to compare.
# 'slice': 15 enqueue_goals (the 5th's refill 3380 declared, 141 words),
# then execute meets crr 2: its slow path (31 words) is compared as the
# requeue of the goal (cmp_execute_slice); the stop is cell 33.  The one
# residual: cell 70 (4cf7-4d02's read, area 5's Console Break Control
# Table, PIMM.PARAM PRINTED; its value meets nothing tested: csbrk, the
# COND 4d02 tests, is a hardware flag, pu.FLAG_CONDS, OURS false).
SLICE_PINNED = dict(steps=33, matched=16, slices=1, picks=0, words=417,
                    stop=(16, 'cell 33'), residual=([], ['cell 70'], []))
# 'crr_proceed': 11 enqueue_goals, an execute (crr 5: the fast path), three
# proceeds that pick, the fourth meets crr 1 and stops at 219f, the test
# of cell 10 that 219e read.
CRRP_PINNED = dict(steps=26, matched=16, slices=0, picks=3, words=289,
                   stop=(16, '219f: ALU input from a read of memory never written'),
                   residual=([], [], [[], [], [], ['cell 10']]))
STOP_PINS = {'slice': lambda: SLICE_PINNED, 'crr_proceed': lambda: CRRP_PINNED}


def stop_got(out, n):
    st = out['stop']
    return dict(steps=n, matched=out['matched'], slices=out['slices'], picks=out['picks'],
                words=out['words'],
                stop=(st[0], st[2] if st[2] == SLICE_STOP else st[3][:len(
                    '219f: ALU input from a read of memory never written')]) if st else None,
                residual=(out['susp_residual'], sorted(out['prog_residual']), out['residual']))


def stop_moved(out, n, prog):
    return (stop_got(out, n) != STOP_PINS[prog]() or bool(out['fail']) or bool(out['boot_stop'])
            or out['boot_residual'] != BOOT_RESIDUAL_PINNED or out['boot_words'] != BOOT_PINNED)


PROG_PINS = {'suspend': lambda: (SUSP_PINNED, SUSP_RESIDUAL_PINNED, SUSP_PROG_RESIDUAL_PINNED,
                                 SUSP_PICK_RESIDUAL_PINNED),
             'stream': lambda: (STREAM_PINNED, STREAM_RESIDUAL_PINNED,
                                STREAM_PROG_RESIDUAL_PINNED, STREAM_PICK_RESIDUAL_PINNED)}


def susp_got(out, n):
    return dict(steps=n, matched=out['matched'], skipped=len(out['skipped']),
                stop=out['stop'][0] if out['stop'] else None, picks=out['picks'],
                dispatched=out['dispatched'], boot_pick=out['boot_pick'],
                suspends=out['suspends'], wakes=out['wakes'])


def susp_moved(out, n, prog='suspend'):
    pin, sres, pres, kres = PROG_PINS[prog]()
    return (susp_got(out, n) != pin or out['susp_residual'] != sres
            or out['prog_residual'] != pres or out['residual'] != kres
            or out['boot_residual'] != BOOT_RESIDUAL_PINNED or out['boot_words'] != BOOT_PINNED
            or (prog in ANSWER_ARGS and not out.get('answer')))


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


def args_append2(m, lst):
    """driver([a], [], Z1, [b], [], Z2): the first and second steps' program."""
    return [lst([0x123]), pimm.NIL, m.new_var(), lst([0x124]), pimm.NIL, m.new_var()]


def args_suspend(m, lst):
    """driver([], [], X, X, [], Z) (U3 third step, OURS): the first goal
    enqueued, append([], [], X), binds X; the second, append(X, [], Z),
    dispatched first (the newest), suspends on X.  X is held by both
    goals, so both references are marked (REFx, OURS: a compiler would
    mark a variable it passes twice); Z is held once (REFo)."""
    x = m.new_var()
    xr = (x[0] | 1, x[1])
    return [pimm.NIL, pimm.NIL, xr, xr, pimm.NIL, m.new_var()]


# U3d first step (2026-11-28): a compiled KL1 program, a producer and two
# consumers of one stream.  The source is OURS (STREAM_SOURCE, 7 lines);
# the code is the HELD compiler's: PIMOS 3.6's KL1 compiler
# (library/compiler, run on pimm.py from the prompt checkpoint, as R7 /
# R8 compile: lines 'compile', '!package work', 'pc', '!exit'; answered
# 'Compile Succeeded : pc', '"work:: pc" Loaded') made module work::pc,
# whose cells 15-61 (the three predicates' code, after the descriptor
# and go/3's head) are STREAM_CELLS, as ref/pu/u3d_compile.py prints and
# checks them (out of the suite: it needs the 1.1 GB checkpoint).  The
# compiler's choices, none of them ours: g and c compile to the same
# code; go's body enqueues g(L, S) and c(S, B) and executes c(S, A) (the
# first goal executed, the others enqueued in order); S is made by
# set_marked_variable (it is passed to three goals).  The cells hold no
# absolute address (labels are relative): placed at any cell they run
# the same (u3d_compile.py runs them on pimm.py at two placements).
STREAM_SOURCE = """\
:- module pc.
:- public go/3.
go(L, A, B) :- c(S, A), c(S, B), g(L, S).
g([], S) :- S = [].
g([X|L], S) :- S = [X|S1], g(L, S1).
c([], R) :- R = [].
c([X|S], R) :- R = [X|R1], c(S, R1).
"""
STREAM_FIRST = 15             # the module offset of STREAM_CELLS[0], go/3's code
STREAM_CELLS = [
    (0x23, 0x14010000),   # 15  set_value 1,0,0
    (0x23, 0x15020000),   # 16  set_marked_variable 2,0,0
    (0x23, 0x63020007),   # 17  enqueue_goal 2, @26
    (0x23, 0x14010000),   # 18  set_value 1,0,0
    (0x23, 0x14020200),   # 19  set_value 2,2,0
    (0x23, 0x63020018),   # 20  enqueue_goal 2, @46
    (0x23, 0x61020017),   # 21  execute 2, @46
    (0x02, 0x000108c0),   # 22  atom #108c0
    (0x00, 0x00000000),   # 23  integer 0
    (0x24, 0x02000018),   # 24  predicate head
    (0x00, 0x00100000),   # 25  integer 1048576
    (0x23, 0x6800000d),   # 26  try_me_else 0, @41
    (0x23, 0x2a000008),   # 27  switch_on_non_list 0,0,8
    (0x23, 0xa7020000),   # 28  read_variable_without_deref 2,0,0
    (0x23, 0xa7030000),   # 29  read_variable_without_deref 3,0,0
    (0x23, 0x2f060002),   # 30  put_reused_structure 6,0,2
    (0x23, 0x25020000),   # 31  write_value 2,0,0
    (0x23, 0x24050000),   # 32  write_variable 5,0,0
    (0x23, 0xbd010600),   # 33  get_bound_value 1,6,0
    (0x23, 0x34000300),   # 34  put_value 0,3,0
    (0x23, 0x34010500),   # 35  put_value 1,5,0
    (0x23, 0x6102fff4),   # 36  execute 2, @26
    (0x23, 0x68000002),   # 37  try_me_else 0, @41
    (0x23, 0x80000000),   # 38  wait_atom #0
    (0x23, 0xba010000),   # 39  get_nil 1,0,0
    (0x23, 0x60000000),   # 40  proceed 0,0,0
    (0x23, 0x6902ffef),   # 41  suspend 2, @26
    (0x02, 0x000100c2),   # 42  atom #100c2
    (0x00, 0x00000000),   # 43  integer 0
    (0x24, 0x0200002c),   # 44  predicate head
    (0x00, 0x00100000),   # 45  integer 1048576
    (0x23, 0x6800000d),   # 46  try_me_else 0, @61
    (0x23, 0x2a000008),   # 47  switch_on_non_list 0,0,8
    (0x23, 0xa7020000),   # 48  read_variable_without_deref 2,0,0
    (0x23, 0xa7030000),   # 49  read_variable_without_deref 3,0,0
    (0x23, 0x2f060002),   # 50  put_reused_structure 6,0,2
    (0x23, 0x25020000),   # 51  write_value 2,0,0
    (0x23, 0x24050000),   # 52  write_variable 5,0,0
    (0x23, 0xbd010600),   # 53  get_bound_value 1,6,0
    (0x23, 0x34000300),   # 54  put_value 0,3,0
    (0x23, 0x34010500),   # 55  put_value 1,5,0
    (0x23, 0x6102fff4),   # 56  execute 2, @46
    (0x23, 0x68000002),   # 57  try_me_else 0, @61
    (0x23, 0x80000000),   # 58  wait_atom #0
    (0x23, 0xba010000),   # 59  get_nil 1,0,0
    (0x23, 0x60000000),   # 60  proceed 0,0,0
    (0x23, 0x6902ffef),   # 61  suspend 2, @46
]
STREAM_LIST = [1]             # go([1], A, B): the input (OURS); A = B = [1]

# U3d second step (2026-11-28), path (a): the reduction count run out.
# crr (R15, rassy 'crr') is 17 after the boot (20a6-20a7, PMPF reset);
# enqueue_goal takes 1 (4c02), execute 2 (4cc0: MDR1 - EM2), proceed 1
# (216d).  Two programs, OURS sources compiled by the held PIMOS 3.6
# compiler on pimm.py (u3d_compile.py re-makes and checks the cells):
#
# 'slice': go(A) :- b(A), a x 15.  The compiler enqueues the fifteen a's
# and executes b(A), so execute meets crr 2: 4cc0 makes it 0 and 4cc1's
# CNDF 3 (2 - 3 negative) is tested by 4cc2's JMPF 8 (RULES['jmpf8_flag']
# 'goto'): execute's slow path, through the goal switch 4c11 (README "U3d,
# second step").
SLICE_SOURCE = """\
:- module sl.
:- public go/1.
go(A) :- b(A), a, a, a, a, a, a, a, a, a, a, a, a, a, a, a.
a :- true | true.
b(A) :- true | A = ok.
"""
SLICE_CELLS = [
    (0x23, 0x63000012),  # 15  enqueue_goal 0, @35
    (0x23, 0x63000011),  # 16  enqueue_goal 0, @35
    (0x23, 0x63000010),  # 17  enqueue_goal 0, @35
    (0x23, 0x6300000f),  # 18  enqueue_goal 0, @35
    (0x23, 0x6300000e),  # 19  enqueue_goal 0, @35
    (0x23, 0x6300000d),  # 20  enqueue_goal 0, @35
    (0x23, 0x6300000c),  # 21  enqueue_goal 0, @35
    (0x23, 0x6300000b),  # 22  enqueue_goal 0, @35
    (0x23, 0x6300000a),  # 23  enqueue_goal 0, @35
    (0x23, 0x63000009),  # 24  enqueue_goal 0, @35
    (0x23, 0x63000008),  # 25  enqueue_goal 0, @35
    (0x23, 0x63000007),  # 26  enqueue_goal 0, @35
    (0x23, 0x63000006),  # 27  enqueue_goal 0, @35
    (0x23, 0x63000005),  # 28  enqueue_goal 0, @35
    (0x23, 0x63000004),  # 29  enqueue_goal 0, @35
    (0x23, 0x61010008),  # 30  execute 1, @40
    (0x02, 0x000107d2),  # 31  atom #107d2
    (0x00, 0x00000000),  # 32  integer 0
    (0x24, 0x00000021),  # 33  ; predicate head 00000021
    (0x00, 0x00010000),  # 34  integer 65536
    (0x23, 0x60000000),  # 35  proceed 0,0,0   ; no
    (0x02, 0x000107d3),  # 36  atom #107d3
    (0x00, 0x00000000),  # 37  integer 0
    (0x24, 0x01000026),  # 38  ; predicate head 01000026
    (0x00, 0x00020000),  # 39  integer 131072
    (0x23, 0xc00100e7),  # 40  get_atom #100e7
    (0x23, 0x60000000),  # 41  proceed 0,0,0   ; no
]
# 'crr_proceed': go(A) :- a x 11, b(A).  The compiler enqueues b(A) and ten
# a's and executes the eleventh a: crr is 5 at that execute (slow path not
# taken), and runs out at the fourth proceed (216d: 1 - 1; 216e -> 217a;
# 217c PMPF, 217d's JMPF d taken: call 219b), which reads cell 10 (219e),
# in area 5's 'Extended Control Registers (constant area)' (PIMM.PARAM,
# PRINTED): no held source gives it, so the run stops there, pinned.
CRRP_SOURCE = """\
:- module rl.
:- public go/1.
go(A) :- a, a, a, a, a, a, a, a, a, a, a, b(A).
a :- true | true.
b(A) :- true | A = ok.
"""
CRRP_CELLS = [
    (0x23, 0x14010000),  # 15  set_value 1,0,0   ; c8_r
    (0x23, 0x63010013),  # 16  enqueue_goal 1, @37
    (0x23, 0x6300000d),  # 17  enqueue_goal 0, @32
    (0x23, 0x6300000c),  # 18  enqueue_goal 0, @32
    (0x23, 0x6300000b),  # 19  enqueue_goal 0, @32
    (0x23, 0x6300000a),  # 20  enqueue_goal 0, @32
    (0x23, 0x63000009),  # 21  enqueue_goal 0, @32
    (0x23, 0x63000008),  # 22  enqueue_goal 0, @32
    (0x23, 0x63000007),  # 23  enqueue_goal 0, @32
    (0x23, 0x63000006),  # 24  enqueue_goal 0, @32
    (0x23, 0x63000005),  # 25  enqueue_goal 0, @32
    (0x23, 0x63000004),  # 26  enqueue_goal 0, @32
    (0x23, 0x61000003),  # 27  execute 0, @32
    (0x02, 0x000107d2),  # 28  atom #107d2
    (0x00, 0x00000000),  # 29  integer 0
    (0x24, 0x0000001e),  # 30  ; predicate head 0000001e
    (0x00, 0x00010000),  # 31  integer 65536
    (0x23, 0x60000000),  # 32  proceed 0,0,0   ; no
    (0x02, 0x000107d3),  # 33  atom #107d3
    (0x00, 0x00000000),  # 34  integer 0
    (0x24, 0x01000023),  # 35  ; predicate head 01000023
    (0x00, 0x00020000),  # 36  integer 131072
    (0x23, 0xc00100e7),  # 37  get_atom #100e7
    (0x23, 0x60000000),  # 38  proceed 0,0,0   ; no
]


def slice_cells(pc0):
    return list(SLICE_CELLS)


def crrp_cells(pc0):
    return list(CRRP_CELLS)


def args_one_var(m, lst):
    """go(A): A unbound (OURS input); the answer A = ok."""
    return [m.new_var()]


def stream_cells(pc0):
    """work::pc's code (STREAM_CELLS) at cell index pc0: position free."""
    return list(STREAM_CELLS)


def args_stream(m, lst):
    """go([1], A, B) (U3d, OURS input): the list of integers, A and B
    unbound, each held once (REFo)."""
    c = m.alloc(2 * len(STREAM_LIST))
    for i, v in enumerate(STREAM_LIST):
        m.mem[c + 2 * i] = (pimm.INT, v)
        m.mem[c + 2 * i + 1] = (pimm.LIST, c + 2 * i + 2) if i + 1 < len(STREAM_LIST) else pimm.NIL
    return [(pimm.LIST, c), m.new_var(), m.new_var()]


PROGRAM_ARGS = args_append2
PROGRAM_CODE = driver_cells
PROGRAMS = {'append2': (args_append2, driver_cells), 'suspend': (args_suspend, driver_cells),
            'stream': (args_stream, stream_cells), 'slice': (args_one_var, slice_cells),
            'crr_proceed': (args_one_var, crrp_cells)}


def pimm_run():
    """driver([a], [], Z1, [b], [], Z2) on pimm.py.  Returns (machine,
    state at the first instruction, steps): each step (pc, cell, lines,
    after), lines the instruction's R / M / A / G / Q lines."""
    m = pimm.Machine()
    code = PROGRAM_CODE(0)
    a = m.alloc(len(code))
    pc0 = a - m.load
    for i, w in enumerate(PROGRAM_CODE(pc0)):
        m.mem[a + i] = w

    def lst(atoms):
        c = m.alloc(2 * len(atoms))
        for i, at in enumerate(atoms):
            m.mem[c + 2 * i] = (pimm.ATOM, at)
            m.mem[c + 2 * i + 1] = (pimm.LIST, c + 2 * i + 2) if i + 1 < len(atoms) else pimm.NIL
        return (pimm.LIST, c)
    args = PROGRAM_ARGS(m, lst)
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
                     if ln[:2] in ('R ', 'M ', 'A ', 'G ', 'W ') or ln == 'Q')
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
            if f in ('R', 'W', 'A'):
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
    p.mem[0xb4] = PARAM_B4
    p.mem[0xb7] = (pimm.INT, GSESH)
    # U3d: the refill's 3375 reads W1c (select d, EM1 1c: RULES
    # ['wsel_d_w_em1'], where R0d was read before) into the latch w2,
    # which nothing after it uses: OURS, STALE (a value not known).
    # Injection 'w1c_unset': STOP in the boot at 3375.
    if W1C_STALE:
        p.w[0x1c] = PU.STALE
    done = []
    p.step(PMPF_ENTRY if entry is None else entry)  # the entry's flag word (OURS: which)
    done.append(('%04x PMPF' % (PMPF_ENTRY if entry is None else entry), 1))
    done.append(('204b heap top', U2.boot_heap_top(p, hp)))
    done.append(('3380 R1b refill', p.call(R1B_REFILL)))
    done.append(('209f-20a8 R11 R16 R15 W1f', run_upto(p, CRR_ARM, CRR_ARM_END)))
    done.append(('20e7 R13 R12 R14', p.call(FP_GOAL)))
    done.append(('202d-2030 R10', p.run(START_TAIL)))
    return done


W1C_STALE = True              # injection 'w1c_unset'
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


R16_COUNTS_SUSPENDED = True   # injection 'r16_queue_only'


def r16_check(p, what, susp=0):
    """R16 (ccc) = the queue's length + 1 (the running goal): held at the
    boot (20a1 R16 := 2 with 2104's one queued record).  U3 third step:
    + the goals suspended (susp), which suspend's held path 1c08-2224
    leaves counted (it does not write R16): ccc counts the live goals,
    ready, running or waiting (INFERRED: the name 'ccc', rassy's, read
    as a child count, which a shoen needs to see its goals finish; R16
    is 3 after the suspend with one goal queued).  Injection
    'r16_queue_only' (the step-2 reading): FAIL at the suspend."""
    q = chain(p, p.r.get(0x14))
    r16 = p.r.get(0x16)
    n = len(q) + 1 + (susp if R16_COUNTS_SUSPENDED else 0)
    if not r16 or r16[1] != n:
        return ['%s: R16 %s, queue length %d + 1 + %d suspended' % (what, fmt(r16), len(q), susp)]
    return []


def run(verbose=False, entry=None, prog=None):
    globals().update(PROGRAM_ARGS=PROGRAMS[prog or 'append2'][0],
                     PROGRAM_CODE=PROGRAMS[prog or 'append2'][1])
    m, s0, steps, pc0 = pimm_run()
    p = PU.PU()
    p.mem.update(s0['mem'])
    check_pu.seed_lists(p, U2.NFREE)
    U2.seed_execute(p)
    p.flags.update(SUSP_FLAGS)                      # OURS: no interrupt pending
    out = {'done': 0, 'matched': 0, 'words': 0, 'stop': None, 'fail': None, 'picks': 0,
           'dispatched': 0, 'empty': 0, 'boot_pick': 0, 'residual': [], 'boot': None,
           'boot_residual': None, 'boot_stop': None, 'boot_words': None,
           'prog_residual': set(), 'skipped': [], 'suspends': 0, 'wakes': 0,
           'susp_residual': [], 'slices': 0}
    prov = Prov()
    prov.harness(p)
    FRESH.clear()
    INDIRECT.clear()
    del REFILLS[:]
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
    for n in SUSP_STALE:                            # OURS: not known (SUSP_STALE)
        p.r[n] = PU.STALE
        prov.reg[('R', n)] = 'harness'
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
    skip_to = 0
    for k, (pc, cellv, lines, after) in enumerate(steps):
        if k < skip_to:                             # declared: guard_to_alt
            out['skipped'].append((k, pc))
            print('skip %2d %5d (pimm.py only: the firmware failed the guard to the'
                  ' alternative)' % (k, pc))
            continue
        p.ir, p.pc = cellv, m.load + pc
        p.r[R_PC] = (COD, (m.load + pc + 1) & 0xffffffff)
        prov.reg[('R', R_PC)] = 'harness'
        r04_0 = p.r.get(R_PC)
        after['next_pc'] = steps[k + 1][0] if k + 1 < len(steps) else None
        # put_reused_structure always sets sp (U3d: the new cells can lie
        # where the old sp pointed, so a compare of the values misses it)
        after['sp_moved'] = after.get('sp') != prev_after.get('sp') or \
            (SP_SET_REUSED and cell_name(p, cellv) == 'put_reused_structure')
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
        elif base == 'suspend' or any(ln.startswith('W ') for ln in lines):
            # the suspend and the wake: what their held path reads that the
            # harness wrote last (cells pimm.py's memory holds apart)
            out['susp_residual'].append(('suspend' if base == 'suspend' else 'wake (%s)' % base,
                                         sorted(r for r in prov.reads(p, n0, ('R', 'W', 'A'))
                                                if not (r.startswith('cell ') and int(r[5:], 16)
                                                        in s0['mem']))))
            out['prog_residual'] |= set(r for r in prov.reads(p, n0) if r != 'R04' and not (
                r.startswith('cell ') and int(r[5:], 16) in s0['mem']))
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
        elif base in ('set_variable', 'set_marked_variable'):
            fails = cmp_set_variable(p, m, rn, lines, after, name, an0, mem0, r0)
        elif base == 'enqueue_goal':
            fails = cmp_enqueue(p, m, rn, lines, after, prev_after, an0, mem0, r0, fw2pg, pg2fw, n0)
        elif base == 'proceed':
            out['picks'] += 1
            kind, fails = cmp_proceed(p, m, rn, lines, after, an0, mem0, r0, fw2pg, pg2fw,
                                      steps[k + 1][0] if k + 1 < len(steps) else None, n0)
            fails = prov_bad + fails
            out[kind] += 1
            empty = kind
        elif base == 'suspend':
            out['picks'] += 1
            out['suspends'] += 1
            kind, fails = cmp_suspend(p, m, rn, lines, after, an0, mem0, r0, fw2pg, pg2fw,
                                      steps[k + 1][0] if k + 1 < len(steps) else None, n0)
            out[kind] += 1
            empty = kind
        elif base == 'execute' and SLICE_SLOW in [u for u, _ in p.trace[n0:]]:
            out['slices'] += 1
            fails = cmp_execute_slice(p, m, rn, lines, after, an0, mem0, r0, fw2pg, pg2fw, n0)
            base = 'slice'
        elif any(ln.startswith('W ') for ln in lines):
            woken = [m.load + int(ln.split()[1]) for ln in lines if ln.startswith('W ')]
            out['wakes'] += len(woken)
            fails = cmp_wake(p, m, rn, lines, woken, an0, mem0, r0, fw2pg, pg2fw)
            fails += U2.compare_next_pc(p, m, pc, after, name, r04_0)
            base = 'wake'
        else:
            fails = U2.compare(p, m, rn, rl, after, name, an0, mem0)
            if DECLARE_DEREF_REG and base in GUARD_OPS:
                fails = declare_deref_reg(p, an0, fails)
            if DECLARE_FRESH_MRB and base == 'put_reused_structure':
                fails = declare_fresh_mrb(p, rn, lines, after, fails)
            if (DECLARE_FRESH_MRB and FRESH) or (DECLARE_READ_INDIRECT and INDIRECT):
                fails = carried_fresh_mrb(p, rn, fails)
            if DECLARE_READ_INDIRECT and base in ('read_variable', 'read_variable_without_deref'):
                fails = declare_read_indirect(p, m, rn, lines, after, mem0, fails)
            j = guard_to_alt(p, m, steps, k, r0) if DECLARE_GUARD_ALT else None
            if j is not None:
                skip_to = j
            else:
                fails += U2.compare_next_pc(p, m, pc, after, name, r04_0)
        if base in ('enqueue_goal', 'proceed', 'suspend', 'wake', 'slice'):
            fails += r16_check(p, name, out['suspends'] - out['wakes'])
        if fails:
            out['fail'] = (k, pc, name, fails)
            print('FAIL %2d %5d %-22s %d words: %s' % (k, pc, name, nw, '; '.join(fails)))
            break
        out['matched'] += 1
        print('ok   %2d %5d %-22s %d words%s' % (k, pc, name, nw,
                                                ('  pick %d%s' % (out['picks'], {
                                                    'empty': ' (empty)', 'boot_pick': ' (the boot goal:'
                                                    ' firmware only)'}.get(empty, '')))
                                                if base in ('proceed', 'suspend') else ''))
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
        if base == 'slice':
            # the firmware's next KL1 instruction is at cell 33 (R04, 4d01)
            out['stop'] = (k + 1, steps[k + 1][0] if k + 1 < len(steps) else None,
                           SLICE_STOP, '4c15 ends with R04 = 33: the next KL1 instruction'
                           ' is at cell 33, which no held source gives (pinned)')
            print('STOP %2d %5s %-22s %s' % (k + 1, out['stop'][1], SLICE_STOP,
                                             out['stop'][3]))
            break
    print('scheduler state read at each pick whose last writer is the harness (OURS): %s'
          % '; '.join('pick %d %s' % (i + 1, ', '.join(r) or 'none')
                      for i, r in enumerate(out['residual'])))
    print('held state read by the boot whose last writer is the harness (OURS): %s'
          % ', '.join(out['boot_residual']))
    if out['susp_residual']:
        print('read by the suspend / wake paths whose last writer is the harness (OURS): %s'
              % '; '.join('%s %s' % (w, ', '.join(r) or 'none') for w, r in out['susp_residual']))
    out['prog_residual'] = sorted(out['prog_residual'])
    print('read by the other instructions (pimm.py\'s cells and R04 declared apart): %s'
          % ', '.join(out['prog_residual']))
    print('%d of %d instructions executed and matched, %d held microinstructions; '
          '%d picks (%d compared with pimm.py, %d empty, %d the boot goal, firmware only)%s'
          % (out['matched'], len(steps), out['words'], out['picks'], out['dispatched'],
             out['empty'], out['boot_pick'], '' if not out['stop']
             else '; first stop: instruction %d (%d %s)' % out['stop'][:3]))
    if prog in ANSWER_ARGS and not out['stop'] and not out['fail'] and steps:
        # the answer (U3d): each output argument read out of the firmware's
        # memory (fw_term) against pimm.py's (Machine.term)
        if ANSWER_POKE is not None:
            w = s0['reg'][1]
            while w[0] & ~1 == pimm.REF:            # A's list, in the firmware's memory
                w = p.mem.get(w[1])
            ANSWER_CELL[0] = w[1]
            ANSWER_POKE(p)                          # injection 'answer_poke'
        got = [fw_term(p.mem, s0['reg'][i]) for i in ANSWER_ARGS[prog]]
        want = [m.term(s0['reg'][i]) for i in ANSWER_ARGS[prog]]
        out['answer'] = (got, want)
        print('answer: firmware %s, pimm.py %s%s' % (
            ', '.join('A%d = %r' % (i, t) for i, t in zip(ANSWER_ARGS[prog], got)),
            ', '.join('A%d = %r' % (i, t) for i, t in zip(ANSWER_ARGS[prog], want)),
            '' if got == want else ': FAIL'))
        if got != want:
            out['fail'] = (len(steps), None, 'answer', ['answer %r, pimm.py %r' % (got, want)])
    return out, len(steps)


# U3d: the arguments whose terms are the program's answer (go's A and B)
ANSWER_ARGS = {'stream': (1, 2)}
ANSWER_POKE = None            # injection 'answer_poke'


def fw_term(mem, w, depth=0):
    """A term read out of the firmware's memory (U3d), as pimm.py's
    Machine.term reads its own: REF chains followed (any MRB), an
    integer, nil as [], a list as a Python list (or ('|', car, cdr)), an
    unbound or hooked variable as None, anything else as its tag and
    value."""
    n = 0
    while w and w[0] & ~1 == pimm.REF and n < 64:
        c = mem.get(w[1])
        if c is None or c[0] == pimm.UNDF or c[0] & ~1 == HOOKO:
            return None
        w, n = c, n + 1
    if not w or depth > 64:
        return ('?', w)
    t = w[0] & ~1
    if t == pimm.INT:
        return w[1] - (1 << 32) if w[1] >> 31 else w[1]
    if t == pimm.ATOM:
        return [] if w[1] == 0 else ('ATOM', w[1])
    if t == pimm.LIST:
        car, cdr = fw_term(mem, mem.get(w[1]), depth + 1), fw_term(mem, mem.get(w[1] + 1), depth + 1)
        return [car] + cdr if isinstance(cdr, list) else ('|', car, cdr)
    return ('tag %02x' % w[0], w[1])


GUARD_OPS = ('wait_nil', 'wait_list', 'wait_atom', 'wait_integer', 'wait_value', 'wait',
             'switch_on_non_list')
DECLARE_GUARD_ALT = True      # injection 'guard_alt_undeclared'


def guard_to_alt(p, m, steps, k, r0):
    """The declared difference 'guard_to_alt' (U3 third step): on an
    unbound variable the firmware's guard notes it and fails to the
    alternative at once (3a34 / 3a33: R04 := R11, try_me_else's label),
    where pimm.py jumps to the label and fails the next guard on the same
    variable.  Returns the index of pimm.py's step at the firmware's R04
    when that holds: the firmware's R04 is R11 as the instruction found
    it, and every pimm.py step skipped is a guard that writes nothing and
    goes on to the next one.  None otherwise (compare_next_pc decides)."""
    r04, r11 = p.r.get(R_PC), r0.get(0x11)
    if not r04 or PU.is_stale(r04) or r04 != r11 or r04 is r0.get(R_PC):
        return None
    for j in range(k + 2, len(steps)):
        if m.load + steps[j][0] == r04[1]:
            break
        if [ln for ln in steps[j][2] if ln[:2] in ('R ', 'M ')]:
            return None
    else:
        return None
    for i in range(k + 1, j):
        nm = cell_name(p, steps[i][1])
        if nm == 'try_me_else' and RETRY_SAME_ALT and m.load + steps[i][3].get('alt', -1) == r04[1]:
            continue          # U3d: the next clause's try_me_else, to the same alternative
        if nm not in GUARD_OPS:
            return None
    return j


# U3d (the stream program): the compiled code puts a try_me_else between
# the switch and the next guard (cells 37 / 57: the second clause's,
# whose alternative is the same suspend, @41 / @61).  pimm.py runs it on
# the way (it writes nothing, its alt unchanged); the firmware, already
# at the alternative, never sees it.  Declared as part of guard_to_alt
# when that try_me_else's alternative is the firmware's R04.  Injection
# 'guard_alt_retry_off': FAIL at the first suspend's switch.
RETRY_SAME_ALT = True


def cell_name(p, cell):
    """The held decode table name of an instruction cell."""
    ir = p.ir
    p.ir = cell
    try:
        return SU.base(SU.decode(p))
    finally:
        p.ir = ir


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


def cmp_set_variable(p, m, rn, lines, after, name, an0, mem0, r0):
    """set_variable / set_marked_variable x, y (U3d): pimm.py's A line
    (argv[x], a reference to a new variable) against the record's cell
    R10 + x, which pairs the two new variable cells under the renaming;
    then its M line (the variable, UNDF) and R line (register y, the same
    reference) as u2_append.compare, the record cell accounted for."""
    x = p.ir_field('x')
    cell = r0[0x10][1] + x
    al = [ln.split() for ln in lines if ln.startswith('A ')]
    if len(al) != 1 or int(al[0][1]) != x:
        return ['%s: pimm.py A lines %s' % (name, al)]
    pv = (int(al[0][2][:2], 16), int(al[0][2][2:], 16))
    fails = []
    if not rn.same(p.mem.get(cell), pv, False, [], 'argv'):
        fails.append('cell R10+%d (%x): firmware %s, pimm.py argv[%d] %s'
                     % (x, cell, fmt(p.mem.get(cell)), x, fmt(pv)))
    mem1 = dict(mem0)
    mem1[cell] = p.mem.get(cell)
    rl = [ln for ln in lines if ln[:2] in ('R ', 'M ')]
    return fails + U2.compare(p, m, rn, rl, after, name, an0, mem1)


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


def cmp_enqueue(p, m, rn, lines, after, prev, an0, mem0, r0, fw2pg, pg2fw, n0=None):
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
    allowed, more = declare_refill(p, r0, mem0, n0)
    fails += more
    fails += other_writes(p, mem0, {rec, rec + 12, rec + 13, rec + 14, rec + 15} | allowed)
    fails += an_unchanged(p, an0, 'enqueue_goal')
    return fails


DECLARE_REFILL = True         # injection 'refill_undeclared' (U3d second step)


def declare_refill(p, r0, mem0, n0):
    """U3d second step: R1b ran out under the program and the held refill
    3380 ran (4c0b's call in enqueue_goal, after 4c04 popped the last
    record): it carves REFILL_RECORDS 16-cell records from R1f, as in the
    boot.  pimm.py has no goal-record free list, so those cells are the
    firmware's alone: declared, and checked to be the boot's pattern (R1f
    advanced by 16 * REFILL_RECORDS, from the old R1f rounded as the boot;
    the records chained through cell 0, nil-ended, from R1b's new head;
    every other cell of a record zero).  Returns (cells, fails)."""
    if not DECLARE_REFILL or R1B_REFILL not in [u for u, _ in p.trace[n0:]]:
        return set(), []
    lo, hi = r0[0x1f][1], p.r[0x1f][1]
    fails = []
    if hi - lo != 16 * REFILL_RECORDS:
        fails.append('refill: R1f %x -> %x, want + %d' % (lo, hi, 16 * REFILL_RECORDS))
    cells = set(range(lo, hi))
    recs = [lo + 16 * k for k in range(REFILL_RECORDS)]
    if p.r.get(0x1b, (0, None))[1] != lo:
        fails.append('refill: R1b %s, want the first new record %x' % (fmt(p.r.get(0x1b)), lo))
    for k, a in enumerate(recs):
        link = p.mem.get(a)
        if (k + 1 < len(recs) and (not isinstance(link, tuple) or link[1] != recs[k + 1])) \
                or (k + 1 == len(recs) and link != NIL):
            fails.append('refill: record %x cell 0 %s, not the chain' % (a, fmt(link)))
        for c in range(1, 16):
            if p.mem.get(a + c) != (pimm.INT, 0):
                fails.append('refill: record %x cell %d %s' % (a, c, fmt(p.mem.get(a + c))))
    REFILLS.append((lo, hi))
    return cells, fails


REFILLS = []                  # (old R1f, new R1f) of each refill met (run() empties it)


# U3d second step: execute's slow path (4cc4 -> 4cd3 -> 4cf4 / 1c2c ->
# 4cf6-4d02 -> 4d00-4d01 -> 4cd4 -> 4c11 -> 4c25-4c2e -> 4c13-4c15), taken
# when crr runs out (4cc1's CNDF 3: crr - 4cc0's EM3 negative, tested by
# 4cc2's JMPF 8, pu.RULES['jmpf8_flag'] 'goto').  What the held words do:
# the running goal's record R10 becomes a ready goal (cell 0 {GOAL, n},
# cells 1..n A0..An-1 by suspend's counted copy 1c2c, cell 12 {COD, the
# label}, 13 W0e, 14 W1d (R13 as 4c12 loaded it), 15 the old R14), R14 :=
# {HOOKo, that record} (the queue's head), R10 := a fresh record off R1b,
# R16 + 1, R15 := 4d01's crr + 1; then R04 := {INT, 33} (4d00-4d01: MDR2
# := 0x32, R04 := MDR2 + 1, beside the boot goal's {COD, 34}: 2106-2108 put
# 0x32 + 2 in its cell 12), and 4c15 ends: the next KL1 instruction is at
# cell 33, which no held source gives (the boot module's code; PIMM.PARAM
# names area 5's cells 0-3f 'Extended Control Registers (constant
# area)', PRINTED).  pimm.py's execute goes on in the same goal; the
# firmware's requeue is compared as an enqueue_goal of that goal (its
# arguments pimm.py's argument registers, its code pimm.py's next
# instruction) and the run stops there, pinned (SLICE_STOP).  Tried and
# not kept: an OURS proceed at cell 33 meets crr 1 (4cd4 leaves 4cc0's 0,
# 4d01 + 1: the slow path does not give a new quota) and so proceed's own
# run-out arm, the 219e stop of 'crr_proceed' below: the quota's reload
# is the code at 33's work (as the boot's, 20a6, from R05 + b0).
SLICE_SLOW = 0x4cc4           # execute's slow path's first word
SLICE_STOP = 'cell 33'        # the pinned stop's reason (no held code there)
SLICE_R04 = 0x33


def cmp_execute_slice(p, m, rn, lines, after, an0, mem0, r0, fw2pg, pg2fw, n0):
    """The slow path's writes against pimm.py's execute (declared: the
    firmware requeues the goal, pimm.py runs on in it)."""
    fails = []
    rec = r0[0x10][1]
    n = p.ir[1] >> 16 & 0xff                  # execute n, @label: the arity
    want_code = (COD, m.load + after['next_pc']) if after.get('next_pc') is not None else None
    if p.mem.get(rec) != (GOAL, n):
        fails.append('slice: cell 0 %s, want {GOAL, %d}' % (fmt(p.mem.get(rec)), n))
    rl = {int(ln.split()[1]): (int(ln.split()[2][:2], 16), int(ln.split()[2][2:], 16))
          for ln in lines if ln.startswith('R ')}
    for i in range(n):
        pv = rl.get(i, after['reg'][i] if after.get('reg') else None)
        if p.mem.get(rec + 1 + i) != an0.get(i) or not rn.same(p.mem.get(rec + 1 + i), pv,
                                                                False, [], 'A%d' % i):
            fails.append('slice: cell %d %s, A%d %s, pimm.py %s'
                         % (1 + i, fmt(p.mem.get(rec + 1 + i)), i, fmt(an0.get(i)), fmt(pv)))
    if p.mem.get(rec + 12) != want_code:
        fails.append('slice: cell 12 %s, pimm.py\'s next instruction %s'
                     % (fmt(p.mem.get(rec + 12)), fmt(want_code)))
    if p.mem.get(rec + 14) != r0.get(0x13):
        fails.append('slice: cell 14 %s, R13 %s' % (fmt(p.mem.get(rec + 14)), fmt(r0.get(0x13))))
    if p.mem.get(rec + 15) != r0[0x14]:
        fails.append('slice: cell 15 %s, the old R14 %s' % (fmt(p.mem.get(rec + 15)), fmt(r0[0x14])))
    if p.r.get(0x14) != (HOOKO, rec):
        fails.append('slice: R14 %s, want {HOOKo, %x}' % (fmt(p.r.get(0x14)), rec))
    if p.r.get(0x10, (0, None))[1] != r0[0x1b][1] or p.r[0x10][0] != HOOKO:
        fails.append('slice: R10 %s, want the popped record {HOOKo, %x}'
                     % (fmt(p.r.get(0x10)), r0[0x1b][1]))
    if p.r.get(R_PC, (0, None))[1] != SLICE_R04:
        fails.append('slice: R04 %s, want 33 (4d00-4d01)' % fmt(p.r.get(R_PC)))
    if p.r.get(0x15, (0, None))[1] != (r0[0x15][1] - 2 + 1) & 0xffffffff:
        fails.append('slice: R15 %s, want 4cc0\'s crr - 2, + 1 (4d01, 4cd4)' % fmt(p.r.get(0x15)))
    fails += other_writes(p, mem0, {rec, rec + 12, rec + 13, rec + 14, rec + 15}
                          | set(rec + 1 + i for i in range(n)))
    fails += an_unchanged(p, an0, 'slice')
    if not fails:
        fw2pg[rec] = ('slice', after['next_pc'])
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
    kind, more = cmp_pick(p, m, rn, lines, after, an0, fw2pg, pg2fw, next_pc, n0)
    return kind, fails + more


def cmp_pick(p, m, rn, lines, after, an0, fw2pg, pg2fw, next_pc, n0):
    """The scheduler pick at the end of proceed or suspend, against
    pimm.py's G line (or its empty queue, or the boot goal)."""
    fails = []
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


HOOKX = 0x0b
SUSP_CHAIN_LINK = True        # injection 'chain_link_nil' (U3d: cell 15 always nil)
SUSP_WAITERS_ONCE = True      # injection 'waiters_raw' (U3d: pimm.py's hook list as it is)
DECLARE_DOUBLE_HOOK = True    # injection 'double_hook_undeclared'


def m_lines(m, lines):
    """pimm.py's M lines as {absolute address: word}, last write wins."""
    out = {}
    for ln in lines:
        f = ln.split()
        if f[0] == 'M':
            out[m.load + int(f[1])] = (int(f[2][:2], 16), int(f[2][2:], 16))
    return out


def hook_goals(m, var, ml):
    """pimm.py's waiters on a variable cell as the instruction left it
    (ml, its M lines, over m.mem): the goal records its hook chain
    reaches (S_NEXT links, S_GOAL goals), in chain order."""
    def mem(a):
        return ml.get(a, m.mem.get(a))
    w, out = mem(var), []
    if not w or w[0] & ~1 != pimm.HOOK:
        return None
    s = w[1]
    while s and len(out) < 64:
        out.append(mem(s + S_GOAL)[1])
        s = mem(s + S_NEXT)[1]
    return out


def cmp_suspend(p, m, rn, lines, after, an0, mem0, r0, fw2pg, pg2fw, next_pc, n0):
    """suspend (U3 third step): the firmware's suspension record against
    pimm.py's, then the pick.  Compared, as a projection of pimm.py's
    structure: the record's arity, arguments and code (pimm.py's G_ARGN,
    G_ARGS, G_CODE; the firmware's cells 0, 1.., 12), and each variable
    the goal waits on: the firmware's cell {HOOKo / HOOKx, record}
    (1c70-1c81, one goal waiting: the record itself; the MRB that of the
    reference the guard noted, the goal's argument), pimm.py's a hook
    chain whose every entry is the goal.  Declared: pimm.py writes a new record (the
    firmware re-uses the running goal's, R10, and gives back the record
    1c09 popped: 2209 -> 339f), its status and link cells, and one hook
    cell per noting (it notes the variable twice, switch_on_non_list and
    then wait_nil, the guard the firmware's 3a34 skips: 'guard_to_alt').
    The firmware's cells 13-15 (cpr, the foster parent, nil) are checked
    against its own registers (firmware only)."""
    fails = []
    ml = m_lines(m, lines)
    gs = [a - G_STATUS for a, w in ml.items() if w == (pimm.INT, SUSPENDED)
          and a - G_STATUS + G_ARGN in ml]
    if len(gs) != 1:
        return 'suspend', ['pimm.py writes %d suspended records' % len(gs)]
    g = gs[0]
    rec = r0[0x10][1]                     # the running goal's record, re-used
    n = m.mem[g + G_ARGN][1]
    if p.mem.get(rec) != (GOAL, n):
        fails.append('cell 0 %s, want {GOAL, %d}' % (fmt(p.mem.get(rec)), n))
    for i in range(n):
        pv = m.mem[g + G_ARGS + i]
        if not rn.same(p.mem.get(rec + 1 + i), pv, False, [], 'arg'):
            fails.append('cell %d %s, pimm.py argument %s' % (1 + i, fmt(p.mem.get(rec + 1 + i)), fmt(pv)))
    if p.mem.get(rec + 12) != (COD, m.mem[g + G_CODE][1]):
        fails.append('cell 12 %s, pimm.py code {COD, %x}' % (fmt(p.mem.get(rec + 12)),
                                                              m.mem[g + G_CODE][1]))
    vars_ = sorted(a for a, w in ml.items() if w[0] & ~1 == pimm.HOOK)
    # cell 15: nil for the first waiter (1c70-1c81); for a variable other
    # goals already wait on (U3d: 1c66's tag case takes 1c73 on HOOKx,
    # 1c82-1c83 write cell 15 := the variable's old hook, 1c86 / 1c81 the
    # variable := {HOOKx, record}) the old hook, so the waiters are a chain
    # of goal records through cell 15, newest first
    old = [mem0.get(rn.p2f.get(v, v)) for v in vars_]
    link = old[0] if (len(old) == 1 and old[0] and old[0][0] & ~1 == HOOKO
                      and SUSP_CHAIN_LINK) else NIL
    for c, want, what in ((13, r0.get(0x12), 'R12'), (14, r0.get(0x13), 'R13'),
                          (15, link, 'nil' if link == NIL else 'the old hook')):
        if p.mem.get(rec + c) != want:
            fails.append('cell %d %s, want %s %s (firmware only)' % (c, fmt(p.mem.get(rec + c)),
                                                                     what, fmt(want)))
    if not vars_:
        fails.append('pimm.py hooks no variable')
    allowed = set(range(rec, rec + 1 + n)) | {rec + 12, rec + 13, rec + 14, rec + 15}
    for v in vars_:
        fva = rn.p2f.get(v, v)            # the firmware's cell for pimm.py's variable
        allowed.add(fva)
        waiters = hook_goals(m, v, ml)
        # pimm.py's waiters, each once, newest first, against the
        # firmware's chain (the variable's hook, then each record's cell
        # 15), records named as pimm.py's (fw2pg, this goal's rec -> g)
        fwch, w = [], p.mem.get(fva)
        while w and w[0] & ~1 == HOOKO and len(fwch) < 64:
            fwch.append(g if w[1] == rec else fw2pg.get(w[1], ('unmapped', w[1])))
            w = p.mem.get(w[1] + 15)
        once = list(dict.fromkeys(waiters or []))
        if not waiters or waiters[0] != g:
            fails.append('pimm.py variable %x: waiters %r, want %x first' % (v, waiters, g))
        elif len(waiters) > len(once) and not DECLARE_DOUBLE_HOOK:
            fails.append('pimm.py variable %x hooked %d times, the firmware once per goal'
                         % (v, len(waiters)))
        elif fwch != (once if SUSP_WAITERS_ONCE else waiters) or w != NIL:
            fails.append('variable %x: the firmware\'s waiters %r (end %s), pimm.py\'s %r'
                         % (v, fwch, fmt(w), once))
        # the hook's MRB is the noting reference's (1c66 forms tag0 of R18,
        # the noted pointer; 1c80 writes {HOOKo, record} and leaves on a
        # clear MRB, 1c81 rewrites {HOOKx, record}): pimm.py's argument
        # that reaches the variable gives it
        refs = [w for w in (m.mem[g + G_ARGS + i] for i in range(n))
                if w[0] & ~1 == pimm.REF and w[1] == v]
        want = (HOOKO | (refs[0][0] & 1) if refs else None, rec)
        if p.mem.get(fva) != want:
            fails.append('variable %x: %s, want {HOOK%s, %x} (the noted reference\'s MRB)'
                         % (v, fmt(p.mem.get(fva)), 'x' if want[0] == HOOKX else 'o', rec))
    # the record 1c09 popped goes back on R1b (2209 -> 339f): no net allocation
    pop = r0.get(0x1b)
    if not pop or not p.r.get(0x1b) or p.r[0x1b][1] != pop[1]:
        fails.append('R1b %s, want the record given back %s' % (fmt(p.r.get(0x1b)), fmt(pop)))
    else:
        allowed.add(pop[1])
        # its cell 0 as it was, or restamped {VECT0x, the same link} (U3d:
        # 339f's push writes VECT0x; a record fresh from 3380's refill has
        # {REFo, next} there, as proceed's freed record: DECLARE_FREE)
        c0, c00 = p.mem.get(pop[1]), mem0.get(pop[1])
        if c0 != c00 and not (DECLARE_FREE and c00 and c0 == (VECT0X, c00[1])):
            fails.append('record %x given back: cell 0 %s, was %s'
                         % (pop[1], fmt(p.mem.get(pop[1])), fmt(mem0.get(pop[1]))))
    fails += other_writes(p, mem0, allowed)
    if rec in fw2pg:
        pg2fw.pop(fw2pg[rec], None)
    fw2pg[rec], pg2fw[g] = g, rec           # the suspended goal: firmware <-> pimm.py
    kind, more = cmp_pick(p, m, rn, lines, after, an0, fw2pg, pg2fw, next_pc, n0)
    return kind, fails + more


DECLARE_ATOM_MRB = True       # injection 'atom_mrb_undeclared'
WAKE_LOOP_REVERSED = False    # injection 'wake_loop_reversed' (the third step's loop)
DECLARE_DEREF_REG = True      # injection 'deref_reg_undeclared'
DEREF_REG_MARKED = True       # injection 'deref_reg_marked_off' (U3d)


def declare_deref_reg(p, an0, fails):
    """The declared difference 'deref_reg' (U3 third step): a guard
    that dereferenced its argument register leaves the value it reached
    there, MRB off (the resumed goal's switch_on_non_list on {REFx, X},
    X now {ATOMx, 0}: 2447 mrb_off, 2440 writes A0 := {ATOMo, 0}, as it
    rewrites a directly held nil in place); pimm.py keeps the reference.
    Drops a 'reg i: firmware wrote V, pimm.py no write' failure when V is
    the end of A[i]'s reference chain in the firmware's memory with its
    MRB cleared."""
    out = []
    for f in fails:
        i = int(f.split()[1].rstrip(':')) if f.startswith('reg ') and f.endswith(
            'pimm.py no write') else None
        if i is not None:
            w, n, on = an0.get(i), 0, False
            while w and w[0] & ~1 == pimm.REF and n < 16:
                on = on or bool(w[0] & 1)
                w, n = p.mem.get(w[1]), n + 1
            v = p.an.get(i)
            # U3d: or MRB on when a reference on the way had it on (pimm.py's
            # deref marks the result so; the firmware's 3304 re-stamps a list
            # reached through a REFx LISTx)
            if n and w and v and (v == (w[0] & ~1, w[1]) and w[0] not in check_pu.POINTER_TAGS
                                  or DEREF_REG_MARKED and on and v == (w[0] | 1, w[1])):
                print('      declared: A%d := %s, the end of its chain (pimm.py keeps the'
                      ' reference)' % (i, fmt(v)))
                continue
        out.append(f)
    return out


DECLARE_READ_INDIRECT = True  # injection 'read_indirect_undeclared' (U3d)
DECLARE_FRESH_MRB = True      # injection 'fresh_mrb_undeclared' (U3d)
SP_SET_REUSED = True          # injection 'sp_set_reused_off' (U3d)
CARRY_FRESH_MRB = True        # injection 'fresh_mrb_carried_off' (U3d)
CARRY_READ_INDIRECT = True    # injection 'read_indirect_carried_off' (U3d)


FRESH = set()                 # firmware structures declared 'mrb' (run() empties it)


INDIRECT = set()              # firmware cells a register refers to by 'read_indirect'


def carried_fresh_mrb(p, rn, fails):
    """The declared differences carried by a copy (U3d).  'mrb': a later
    register or cell that holds a pointer to a structure declared at its
    put_reused_structure (FRESH) differs from pimm.py's in the MRB alone
    (firmware off, pimm.py on).  'read_indirect': one that holds the
    firmware's reference to a cell of INDIRECT, where pimm.py holds what
    that cell holds."""
    out = []
    for f in fails:
        w = f.replace(',', '').split()
        if ('firmware' in w and 'pimm.py' in w and w[0] in ('reg', 'heap')
                and 'write' not in w):
            try:
                fv = w[w.index('firmware') + 1].split(':')
                pv = w[w.index('pimm.py') + 1].split(':')
                fv, pv = (int(fv[0], 16), int(fv[1], 16)), (int(pv[0], 16), int(pv[1], 16))
            except (ValueError, IndexError):
                fv = pv = None
            if CARRY_FRESH_MRB and fv and fv[1] in FRESH and pv == (fv[0] | 1, rn.f2p.get(fv[1])):
                print('      declared: %s %s holds %s, pimm.py %s (mrb, carried)'
                      % (w[0], w[1].rstrip(':'), fmt(fv), fmt(pv)))
                continue
            if CARRY_READ_INDIRECT and fv and fv[0] & ~1 == pimm.REF and fv[1] in INDIRECT \
                    and rn.same(p.mem.get(fv[1]), pv, False, [], 'carried'):
                print('      declared: %s %s holds %s, pimm.py %s (read_indirect, carried)'
                      % (w[0], w[1].rstrip(':'), fmt(fv), fmt(pv)))
                continue
        out.append(f)
    return out


def declare_fresh_mrb(p, rn, lines, after, fails):
    """The declared difference 'mrb' of U1 (check_pu.py: put_list,
    put_vector_N), met in put_reused_structure (U3d): on a structure it
    may not reuse (the stream program's consumer, A0 a LISTx: 31ec-31ed
    do not end) the firmware takes new cells (31ee -> 31a1 -> 31a4, the
    R1a list) and gives x the new structure MRB off, a single reference;
    pimm.py's i_put_reused_structure takes new cells always and marks
    the pointer MRB on.  Drops 'reg x' when the two differ only in the MRB
    and the firmware's cells are new to the renaming (then its z cells are
    paired with pimm.py's z), and
    the sp compare the unpaired cells made fail, if R02 now pairs."""
    x = p.ir_field('x')
    out, paired = [], False
    for f in fails:
        if f.startswith('reg %d: firmware ' % x):
            fv = p.an.get(x)
            pv = [ln.split()[2] for ln in lines if ln.startswith('R %d ' % x)]
            pv = (int(pv[0][:2], 16), int(pv[0][2:], 16)) if pv else None
            if fv and pv and fv[0] in check_pu.POINTER_TAGS and not fv[0] & 1 \
                    and pv[0] == fv[0] | 1 and fv[1] not in rn.f2p and pv[1] not in rn.p2f:
                for k in range(p.ir_field('z')):      # the z new cells, cell by cell
                    rn.pair(fv[1] + k, pv[1] + k)
                FRESH.add(fv[1])
                paired = True
                print('      declared: A%d := %s, MRB off, pimm.py %s (mrb)' % (x, fmt(fv), fmt(pv)))
                continue
        out.append(f)
    if paired:
        r02 = p.r.get(SU.R_SP)
        out = [f for f in out if not (f.startswith('sp: ') and '->' not in f and r02
                                      and rn.f2p.get(r02[1]) == after.get('sp'))]
    return out


def declare_read_indirect(p, m, rn, lines, after, mem0, fails):
    """The declared difference 'read_indirect' (U3d): reading an element
    of a structure write_variable built.  There the firmware's element is
    {REF, a new cell} and pimm.py's the variable itself (U1's declared
    'indirect', u2_append.declare_indirect, which pairs the new cell with
    pimm.py's element).  So, read from a shared structure (reached through
    a REFx), the firmware's register is a reference to the cell paired
    with pimm.py's element, and the element itself is re-stamped MRB on in
    place (a shared reference now held twice); pimm.py's register is what
    that cell holds (pimm.py's taken; it marks pointers only, and writes
    no cell).  Drops 'reg x' when the firmware's register is {REF / REFx,
    c}, c paired with the element pimm.py read (its sp before the
    instruction) and c's content the same as pimm.py's value; and 'heap a'
    when a held {REF, c} (the firmware's element) and only its MRB was
    turned on."""
    el = after.get('sp')
    el = el - 1 if el is not None else None
    fel = rn.p2f.get(el, el)              # the firmware cell paired with it: the new cell
    out = []
    for f in fails:
        w = f.split()
        if f.startswith('reg ') and ': firmware ' in f and 'pimm.py no write' not in f:
            i = int(w[1].rstrip(':'))
            fv = p.an.get(i)
            pv = [ln.split()[2] for ln in lines if ln.startswith('R %d ' % i)]
            pv = (int(pv[0][:2], 16), int(pv[0][2:], 16)) if pv else None
            if fv and fv[0] & ~1 == pimm.REF and el is not None and rn.f2p.get(fv[1]) == el \
                    and pv and rn.same(p.mem.get(fv[1]), pv, False, [], 'read'):
                print('      declared: A%d := %s, a reference to the cell pimm.py\'s element is'
                      ' (read_indirect)' % (i, fmt(fv)))
                INDIRECT.add(fv[1])
                continue
        if f.startswith('heap ') and 'pimm.py no write' in f:
            a = int(w[1].rstrip(':'), 16)
            old, new = mem0.get(a), p.mem.get(a)
            if old and new and old[0] & ~1 == pimm.REF and old[1] == fel \
                    and new == (old[0] | 1, old[1]):
                print('      declared: element %x re-stamped %s (read_indirect)' % (a, fmt(new)))
                continue
        out.append(f)
    return out


def cmp_wake(p, m, rn, lines, woken, an0, mem0, r0, fw2pg, pg2fw):
    """An instruction that binds a variable goals wait on (U3 third step:
    get_value on the hooked X).  pimm.py's W line names each goal woken;
    its M lines bind the variable and make the record READY at the head
    of its ready queue (G_STATUS, G_LINK).  The firmware (0867 -> 0a5c-
    0a5e, 0a24 -> 0b20-0b23 -> 4d1a-4d1e) binds the variable and pushes
    the waiting record on R14 (cell 15 := the old R14, R14 := {HOOKo,
    record}).  Compared: every pimm.py M line but the woken records' own
    cells against the firmware's memory; each woken record is R14's head
    and its link is the old R14 (pimm.py's G_LINK: its old queue head, or
    the boot record where pimm.py has none, as same_link); nothing else
    written; the A registers unchanged.  Declared: pimm.py's status cell
    (the firmware has none), and the MRB of a non-pointer value: the
    firmware binds the variable, reached by a REFx, to {ATOMx, 0} (0a5c
    mrb_on, 0a5e writes it), pimm.py keeps the MRB on pointers only."""
    fails = []
    ml = m_lines(m, lines)
    own = set()
    for g in woken:
        own |= {g + G_STATUS, g + G_LINK}
    allowed = set()
    for a, pv in sorted(ml.items()):
        if a in own:
            continue
        fa = rn.p2f.get(a, a)             # the firmware's cell (U3d: a renamed variable)
        allowed.add(fa)
        fv = p.mem.get(fa)
        if rn.same(fv, pv, False, [], 'heap'):
            continue
        if DECLARE_ATOM_MRB and fv and pv and fv[0] == pv[0] | 1 and pv[0] not in check_pu.POINTER_TAGS \
                and fv[1] == pv[1]:
            continue
        fails.append('heap %x: firmware %s, pimm.py %s' % (a, fmt(fv), fmt(pv)))
    head = r0.get(0x14)
    # each woken record pushed in pimm.py's W order, so the last woken is
    # the head and each record's link is the one woken before it (U3d:
    # the loop ran reversed, right for one waiter only)
    for g in (reversed(woken) if WAKE_LOOP_REVERSED else woken):
        if g not in pg2fw:
            fails.append('pimm.py wakes record %x, which no suspend made' % g)
            continue
        rec = pg2fw[g]
        allowed.add(rec + 15)
        if p.mem.get(rec + 15) != head:
            fails.append('woken record %x cell 15 %s, want the old R14 %s'
                         % (rec, fmt(p.mem.get(rec + 15)), fmt(head)))
        if not same_link(link_of(p.mem.get(rec + 15), fw2pg), ml.get(g + G_LINK, (0, None))[1]):
            fails.append('woken record %x link %r, pimm.py\'s %r'
                         % (rec, link_of(p.mem.get(rec + 15), fw2pg), ml.get(g + G_LINK)))
        if ml.get(g + G_STATUS) != (pimm.INT, pimm_layout_READY):
            fails.append('pimm.py record %x not made READY' % g)
        head = (HOOKO, rec)
    if p.r.get(0x14) != head:
        fails.append('R14 %s, want the woken record %s' % (fmt(p.r.get(0x14)), fmt(head)))
    fails += other_writes(p, mem0, allowed)
    fails += an_unchanged(p, an0, 'wake')
    return fails


def _wait_atom_plus1():
    """Injection 'wait_atom_plus1' (U3d): wait_atom's MDR2 the atom + 1."""
    s = SU.setup

    def setup(pu, name):
        start = s(pu, name)
        if SU.base(name) == 'wait_atom':
            w = pu.wr[SU.mekbn.MDR2]
            pu.wr[SU.mekbn.MDR2] = (w[0], w[1] + 1)
        return start
    SU.setup = setup


def _answer_poke(p):
    """Injection 'answer_poke' (U3d): one firmware-written cell of the
    answer changed after the run, the car of A's list (2 for 1)."""
    a = ANSWER_CELL[0]
    p.mem[a] = (pimm.INT, 2)


ANSWER_CELL = [None]          # set by run(): the firmware cell of A's first element


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
    # U3d second step (2026-11-28)
    'jmpf8_fall': lambda: PU.RULES.update(jmpf8_flag=True),
    'jmpf_d_off': lambda: PU.RULES.update(jmpf_d_call_ifnot=False),
    'refill_undeclared': lambda: globals().update(DECLARE_REFILL=False),
    'wide_cndf7_off': lambda: PU.RULES.update(sc2_wide_cndf7=False),
    'csbrk_set': lambda: SUSP_FLAGS.update(csbrk=True),
    'gset_219c_off': lambda: PU.GSET_SHIFT_WORDS.discard(0x219c),
    'gset_4c28_off': lambda: PU.GSET_SHIFT_WORDS.discard(0x4c28),
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
    # U3 third step: the suspend / wake rules and declarations
    'cnd_noalu_poison': lambda: PU.RULES.update(cnd_noalu_poison=True),
    'cnd_noalu_raise': lambda: PU.RULES.update(cnd_noalu_poison=False),
    'f_jump_raise': lambda: PU.MCF_SUB.pop((0x02, 4)),
    'susp_flags_rassy': lambda: PU.RULES.update(susp_flags='rassy'),
    'jmpf8_cndf_off': lambda: PU.RULES.update(jmpf8_goto_cndf=False),
    'alf_high_reversed': lambda: setattr(PU, 'ALF_HIGH_REVERSED', True),
    'alf_high_signed': lambda: setattr(PU, 'ALF_HIGH_SIGNED', True),
    'src_c_rfar_off': lambda: PU.RULES.update(src_c_rfar=False),
    'em1_28_false': lambda: PU.RULES.update(em1_28_s1_mrb='false'),
    'em1_28_read_off': lambda: PU.RULES.update(em1_28_s1_read=False),
    'chain_row_off': lambda: setattr(SU, 'S_CHAIN_ROW', False),
    'chain_row_srp': lambda: setattr(SU, 'CHAIN_SRP_TRUE', True),
    'chain_mar1_bare': lambda: setattr(SU, 'S_CHAIN_MAR1_PTR', False),
    'interrupt_pending': lambda: SUSP_FLAGS.update(interrupt=True),
    'sc2_a_opd': lambda: PU.RULES.update(sc2_a_imm=False),
    'sspb_zero': lambda: globals().update(PARAM_B4=(pimm.INT, 0)),
    'long_em1_busy': lambda: PU.RULES.update(long_em1_free=False),
    'adf2_none': lambda: PU.RULES.update(adf2='none'),
    'adf2_pair': lambda: PU.RULES.update(adf2='pair'),
    'sc2_e_off': lambda: PU.RULES.update(sc2_e_em2=False),
    'reverse_sub_plain': lambda: PU.RULES.update(alu_gset='reverse_sub_plain'),
    'shr_by_b': lambda: PU.RULES.update(alu_gset='shr_by_b'),
    'gset_ops_off': lambda: PU.RULES.update(alu_gset=False),
    'r16_queue_only': lambda: globals().update(R16_COUNTS_SUSPENDED=False),
    'guard_alt_undeclared': lambda: globals().update(DECLARE_GUARD_ALT=False),
    'double_hook_undeclared': lambda: globals().update(DECLARE_DOUBLE_HOOK=False),
    'atom_mrb_undeclared': lambda: globals().update(DECLARE_ATOM_MRB=False),
    'deref_reg_undeclared': lambda: globals().update(DECLARE_DEREF_REG=False),
    # U3d first step: the stream program's rules and declarations
    'rvwd_form_arg': lambda: SU.FORMS.update(read_variable_without_deref=(None, 'arg_x')),
    'wait_atom_own': lambda: SU.S_CONST.pop('wait_atom'),
    'get_nil_form_y': lambda: SU.FORMS.update(get_nil=('s_tag', 'y')),
    'chain_odpf4_off': lambda: setattr(SU, 'S_CHAIN_ODPF4', False),
    'wsel_d_w_off': lambda: PU.RULES.update(wsel_d_w_em1=False),
    'chain_match_off': lambda: setattr(SU, 'S_CHAIN_MATCH', False),
    'tdar_odpf3_off': lambda: setattr(SU, 'S_TDAR_ODPF3', False),
    'w1c_unset': lambda: globals().update(W1C_STALE=False),
    'guard_alt_retry_off': lambda: globals().update(RETRY_SAME_ALT=False),
    'chain_link_nil': lambda: globals().update(SUSP_CHAIN_LINK=False),
    'waiters_raw': lambda: globals().update(SUSP_WAITERS_ONCE=False),
    'wake_loop_reversed': lambda: globals().update(WAKE_LOOP_REVERSED=True),
    'read_indirect_undeclared': lambda: globals().update(DECLARE_READ_INDIRECT=False),
    'fresh_mrb_undeclared': lambda: globals().update(DECLARE_FRESH_MRB=False),
    'sp_set_reused_off': lambda: globals().update(SP_SET_REUSED=False),
    'deref_reg_marked_off': lambda: globals().update(DEREF_REG_MARKED=False),
    'answer_poke': lambda: globals().update(ANSWER_POKE=_answer_poke),
    'wait_atom_plus1': lambda: _wait_atom_plus1(),
    'fresh_mrb_carried_off': lambda: globals().update(CARRY_FRESH_MRB=False),
    'read_indirect_carried_off': lambda: globals().update(CARRY_READ_INDIRECT=False),
    'setvar_form_op': lambda: SU.FORMS.update(set_marked_variable=(None, 'arg_op')),
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
    bad = bool(moved or out['fail'] or out['stop'] or out['boot_stop'])
    print('--- the program suspend (U3 third step)')
    out2, n2 = run('-v' in argv, prog='suspend')
    smoved = susp_moved(out2, n2)
    if smoved:
        print('%s the suspend run moved: %s, suspend / wake residual %s, program residual %s,'
              ' pick residual %s; pinned %s, %s, %s, %s'
              % ('MOVED' if inj else 'FAIL', susp_got(out2, n2), out2['susp_residual'],
                 out2['prog_residual'], out2['residual'], SUSP_PINNED, SUSP_RESIDUAL_PINNED,
                 SUSP_PROG_RESIDUAL_PINNED, SUSP_PICK_RESIDUAL_PINNED))
    bad2 = bool(smoved or out2['fail'] or out2['stop'] or out2['boot_stop'])
    print('--- the program stream (U3d, a compiled program: work::pc go([1], A, B))')
    out3, n3 = run('-v' in argv, prog='stream')
    tmoved = susp_moved(out3, n3, 'stream')
    if tmoved:
        print('%s the stream run moved: %s, suspend / wake residual %s, program residual %s,'
              ' pick residual %s, answer %s; pinned %s, %s, %s, %s'
              % ('MOVED' if inj else 'FAIL', susp_got(out3, n3), out3['susp_residual'],
                 out3['prog_residual'], out3['residual'], out3.get('answer'), STREAM_PINNED,
                 STREAM_RESIDUAL_PINNED, STREAM_PROG_RESIDUAL_PINNED, STREAM_PICK_RESIDUAL_PINNED))
    bad3 = bool(tmoved or out3['fail'] or out3['stop'] or out3['boot_stop'])
    bad4 = {}
    for prog, what in (('slice', 'execute\'s slow path, crr run out'),
                       ('crr_proceed', 'proceed with crr run out')):
        print('--- the program %s (U3d second step: %s; a pinned stop)' % (prog, what))
        o4, n4 = run('-v' in argv, prog=prog)
        bad4[prog] = stop_moved(o4, n4, prog)
        if bad4[prog]:
            print('%s the %s run moved: %s, fail %s; pinned %s'
                  % ('MOVED' if inj else 'FAIL', prog, stop_got(o4, n4), o4['fail'],
                     STOP_PINS[prog]()))
    if inj:
        print('injection %s: append2 %s, suspend %s, stream %s, slice %s, crr_proceed %s'
              % (nm, 'MOVED' if bad else 'unchanged', 'MOVED' if bad2 else 'unchanged',
                 'MOVED' if bad3 else 'unchanged',
                 'MOVED' if bad4['slice'] else 'unchanged',
                 'MOVED' if bad4['crr_proceed'] else 'unchanged'))
        return 1 if bad or bad2 or bad3 or any(bad4.values()) else 0
    if bad or bad2 or bad3 or any(bad4.values()):
        return 1
    # PMPF's other value (entry 2003's set_PMPF, 2022): the boot's crr arm
    # reads the reduction limit at R05 + b0, a parameter cell no harness
    # gives: pinned at that stop.
    print('--- the same run entered at 2003 (2022 set_PMPF)')
    out1, _ = run(False, entry=PMPF_SET_ENTRY)
    if not (out1['boot_stop'] or '').startswith(PINNED_PMPF_SET + ':'):
        print('FAIL the PMPF-set run moved: boot stop %r, pinned at %s'
              % (out1['boot_stop'], PINNED_PMPF_SET))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
