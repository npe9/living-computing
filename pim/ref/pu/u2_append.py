#!/usr/bin/env python3
"""U2 harness: a whole KL1 program on ICOT's held microcode (ref/pu/pu.py)
against ref/pimm/pimm.py, instruction after instruction.

The program is the IPL image's own append/3 (scsi_fep_module, cells
6644-6658):

    6644  try_me_else 0, @6658          6651  get_bound_value 2,0,0
    6645  switch_on_non_list 0,0,8      6652  put_value 0,4,0
    6646  read_variable 3,0,0           6653  put_value 2,3,0
    6647  read_variable 4,0,0           6654  execute 3, append/3
    6648  put_reused_structure 0,0,2    6655  wait_nil 0,0,0
    6649  write_value 3,0,0             6656  get_value 1,2,0
    6650  write_variable 3,0,0          6657  proceed 0,0,0
                                        6658  suspend 3, append/3

called as append([a], [], Z): two reductions, 16 instructions on
pimm.py.  pimm.py runs it whole (Machine.run) and its trace (I, R, M
lines) is split at each I line.  The PU then executes the same
instructions in order, its state carried from one to the next (the
argument registers, R02, R11, the free lists, memory); per instruction
the D stage is the held decode table (setup.dispatch) and the
E stage is the held micro-routine to its end.  What is OURS:

  - the A stage: the instruction cell and its address (pu.pc) come from
    pimm.py's trace, in pimm.py's order (the firmware's own next-PC,
    R04, is compared where it writes one);
  - the goal switch before the first instruction: A0-A2 as pimm.py's
    goal_switch leaves them (the firmware's goal records are not run);
  - the free lists (check_pu.seed_lists) and the record area R10;
  - memory: pimm.py's cells (the image and the argument terms) at the
    same addresses, a flat dict.

Comparison (docs/pu_microcode_plan.md "What the same as pimm.py can
mean"), per instruction: every register pimm.py writes (R line) against
An under the address renaming of check_pu.Rename; every cell it writes
(M line) against the firmware's; pimm.py's sp against R02 where pimm.py
moves it; try_me_else's alternative (pimm.py Machine.alt) against R11
(the projection R11 = alt: INFERRED, below).

Prints one line per instruction, then a summary: instructions executed
and matched, held microinstructions executed, and the first stop.
Exit status 0 when every instruction executed matched and the furthest
point is the pinned one (PINNED: a STOP there is the reported furthest
point, not a failure); 1 on a FAIL or a moved furthest point.

    python3 ref/pu/u2_append.py [-v] [--inject NAME]

Before the program, start's held heap-top routine 204b-2052 runs (as
2028 calls it) on a parameter cell: first on five parameters against
its contract (R1f = the parameter rounded up to 16), then on pimm.py's
heap pointer (OURS) to give the run its R1f.

Before the program, the S-stage case that decides setup.S_ENTRY:
get_atom (entry 3800) on an unbound variable, on both models.  Every
write of the firmware to an argument register or a cell with no
pimm.py R / M line is a FAIL.

Also before the program: read_variable on a structure whose element is
a list pointer (LISTo, reached with every MRB off: pimm.py sp_single),
on both models (x, R02 and every memory write compared).  It is the
case that tells the dereference set-up at 34a1 (pu.DEREF_SETUP) from a
TGT column.

Observed 2026-11-27 (ref/pu/README.md "U2"): get_atom ok (3800-3801);
the list-element case ok (34a0-34a2, 3494); the boot contract ok on 5
parameters; 4 of 16 instructions executed and matched (try_me_else
216a, switch_on_non_list on a list 3300-3301, read_variable 3 and 4,
34a0-34a2 and 3494 each), 11 held microinstructions; the first stop is
put_reused_structure (6648): no S-stage set-up form.  (2026-11-26: 2 of
16, a stop at read_variable 34a0, CNDF 7 EM1 28.)
Injections (in-process, no file edited), observed:
  s_imm_plus1     S_ENTRY entry + 1: get_atom FAILs (the cell bound
                  untagged, 00:00000456); append unchanged, 2 of 16,
                  2 words
  s_imm_row       every tag takes the TGT row (column TDPF, 4-word
                  rows): get_atom STOP at 3810 (CNDF a); append STOP at
                  3309 (MCF with EM1 06), 1 of 16 matched
  s_no_mar1       S_ENTRY without MAR1 = the last cell: get_atom STOP
                  at 3801 (MAR1 never set); append unchanged (4 of 16)
  s_cond_true     S_ENTRY's COND forced true: nothing changes (get_atom
                  ok, 4 of 16): the COND part is NOT discriminated
  wide_em1em2     SC2F b read as EM bits 15..4: the boot reads memory
                  1e, never written (POISON since 2026-11-27): the
                  contract STOPs at 204f (the ALU input) on all 5
                  parameters, and the run STOPs in the boot
  cnd2_nonzero    CNDF 2 read as "not zero": the contract FAILs on all
                  5 (aligned +16, unaligned rounded down); the program
                  part is unchanged (2 of 16)
  bit0_clear_off  the bit-0-clear polarity unmodelled: STOP at 2050 on
                  all 5 parameters and in the boot
  (2026-11-27; s_imm_plus1 now also 4 of 16, 10 words, append's
  switch_on_non_list taking one word fewer; cnd2_nonzero 4 of 16)
  deref_imm_other the set-up's codes 0 (= EM2) and 1 (other) swapped:
                  the list-element case FAILs (3490/348f write
                  {VECTx, element} over the element); append STOPs at
                  3490 (ALU input from the POISON read at 34a2), 2 of 16
  deref_bits10    the code in TDAR bits 1-0: both STOP at 3491 (zero
                  word), 2 of 16
  deref_tgt_col0  the set-up read as TGT column 0: append PASSES, 4 of
                  16 (column 0 sends ATOMo to 3494 too); the list-element
                  case STOPs at 3492 (R11 never set): only that case
                  discriminates
  deref_tgt_col5  column EM1 & 7 = 5: the list case STOPs at 3498 (CNDF 7
                  EM1 34), append at 3492 (MCF with EM1 02), 2 of 16
  deref_tgt_col7  column 7: the list case STOPs at 3492, append at 3490,
                  2 of 16
  em1_28_tgt0     EM1 28 read as a case_tag_setup (column 0): both STOP
                  at 34a0 (no ALU input), 2 of 16
  absent_read_raise  a read of memory never written raises: append
                  STOPs at 34a2 (memory 123, the atom), 2 of 16; the
                  list case is unchanged (its 34a2 reads a cell)
  jmpf8_off       JMPF 8 raises again: both STOP at 34a1, 2 of 16

Also before the program (2026-11-27, third session): put_reused_structure
off append's path (reuse_cases): 3,0,2 on a LISTo held in A0, on both
models under the declared difference 'reuse' (tells the operand field y
from x), and 0,0,2 on a LISTx, which must NOT be reused in place: the
model goes on into the allocating arm and stops at 31ee (R04, pc, never
set: REUSE_SHARED_STOP).  Declared differences, as U1's: 'reuse'
(DECLARE_REUSE: the firmware reuses a single-referenced structure in
place, pimm.py never reuses) and 'indirect' (DECLARE_INDIRECT:
write_variable's element is a REF to a new cell).

Observed 2026-11-27, third session: every case above ok; 10 of 16
instructions executed and matched, 20 held microinstructions (+
put_reused_structure 31ec-31ed, write_value 31c9, write_variable
3195-3199, get_bound_value 3880, put_value 31da twice); the first stop
is execute (6654): no set-up form.  The old injections, re-run with the
new rules (the only changes from above): s_imm_plus1 now also STOPs
append at 3881 (get_bound_value entered past its first word: a zero
word), 7 of 16; s_no_mar1 FAILs append at get_bound_value (the binding
written over the wrong cell), 7 of 16; s_cond_true, cnd2_nonzero and
deref_tgt_col0 leave append at 10 of 16 (their other cases as above).
New injections, observed:
  odpf3_entry     the ODPF 3 start ignores the tag (always the entry):
                  append STOPs at 31e9 (ALU input from a read never
                  written: 31e8 read [MAR1] for a descriptor), 4 of 16;
                  both reuse cases STOP at 31e8 (MAR1 never set)
  odpf3_bits10    the code in bits 1-0 (start 31e9): append STOPs at
                  31a3 (case_branch with no set-up), 4 of 16; both reuse
                  cases STOP at 31e9
  em1_29_off      COND = the MRB is OFF: append STOPs at 31ee (R04 never
                  set, the allocating arm), 4 of 16; the LISTo case STOPs
                  there too; the LISTx case FAILs (ended at 31ed after 2
                  words: a shared list reused in place)
  sc2f1_reg       SC2F 1 read as a register R01: append and both reuse
                  cases STOP at 31ec (R01 never set), 4 of 16
  prs_operand_x   the operand taken from x, not y: append PASSES (10 of
                  16: x = y = 0); the 3,0,2 case FAILs (A3 and R02 =
                  {INT, 9}, A3's old value): only that case discriminates
  no_reuse_decl   the declaration 'reuse' off: append FAILs at
                  put_reused_structure (A0 and R02 the reused cell, not
                  pimm.py's new one), 4 of 16; the 3,0,2 case FAILs
  no_indirect_decl the declaration 'indirect' off: append FAILs at
                  write_variable (the new cell f2000000, the element a
                  REF to it, A3 the REF), 6 of 16
  gbv_mdr2_x      get_bound_value's MDR2 from x, not y: append FAILs at
                  get_bound_value (the variable cell bound to a REF to
                  itself), 7 of 16

Observed 2026-11-27, fifth session: every case above ok; 12 of 16
instructions executed and matched, 25 held microinstructions (+ execute
4cc0-4cc3, the fast path, and the second reduction's try_me_else 216a);
the first stop is switch_on_non_list (6645) on nil: the S-stage
multiway set-up for a tag other than the immediate (row entry UNKNOWN).
execute is compared on R04 (the firmware's next PC) against pimm.py's
next instruction, tag COD (seed_execute, compare_execute: the flags and
the STALE registers are OURS).  The old injections give the same
results as listed above, except that those that left append at 10 of
16 now leave it at 12 (s_cond_true, cnd2_nonzero, deref_tgt_col0,
prs_operand_x).  New injections, observed:
  cjump_same      a conditional jump tests its own word's COND: append
                  STOPs at 4cc1 (the COND 4cc1 forms is STALE: MDR1 - R0d),
                  10 of 16
  cjump_false     JMPF b taken when COND is false: STOP at 4cc5 (AS1F 3
                  with AS2F 1, not modelled), 10 of 16
  slit_pending    the slit-check flag set (an event pending): STOP at 4cc5,
                  as cjump_false, 10 of 16
  interrupt_pending  interrupt_all set: 4cc3 does not end; 4cc4 R04 :=
                  the old pc, 4cd3 calls 4cf4: STOP at 1c2c (CNDF 7 EM1 0d),
                  10 of 16, 28 words
  flags_swapped   EM1 19 read as interrupt_all, 21 as slit_check: nothing
                  changes (both clear): which flag is which is NOT
                  discriminated
  as1f2_off       AS1F 2 unmodelled: STOP at 4cc0, 10 of 16
  mcf_unknown_raise  MCF 06 / 07 raise (and, since U3's third step,
                  pu.SUSP_FLAG_OPS off): STOP at 4cc1 (MCF with EM1 07)
  jmpf8_flag_off  JMPF 8 on a flag condition raises: STOP at 4cc2
  cnd3_off        CNDF 3 unmodelled: nothing changes (4cc1's COND is
                  STALE before the rule is asked): NOT discriminated
  execute_mdr1    the label put in MDR1: append FAILs at execute (R04 =
                  {COD, e0008000}, MDR2's old value, for {COD, e00019f4})
  tgif3_em1       TGIF 3's tag from EM1: append FAILs at execute (R04
                  tag 21 BLT for COD)

Observed 2026-11-27, sixth session: every case above ok, and a new side
case, switch_on_non_list 0,0,8 on {VECT0o, 0} (switch_label_case: the
S-stage TDAR column), ok; 14 of 16 instructions executed and matched, 37
held microinstructions (+ switch_on_non_list on nil 3310-3311, 2447,
2440, 2461, 241d, the label branch; wait_nil 3980, 3985; get_value runs
38b0-38b3 to 0c0c); the first stop is get_value (6656) at 0c0c, CNDF 7
EM1 3f, inside the general unifier.  New in the comparison: every
instruction's next PC (compare_next_pc: R04 if the firmware wrote it,
else pc + 1, against pimm.py's next I line), with the A stage's R04 =
{COD, pc + 1} (A_STAGE_R04, OURS) given before each instruction; pimm.py's
sp compared only where pimm.py moves it.  The old injections give the
same results as listed above, except: s_cond_true, deref_tgt_col0,
prs_operand_x, flags_swapped, cnd3_off now leave append at 14 of 16 (37
words); s_imm_row's get_atom now STOPs at 3811 (the JMPF 9 call taken)
instead of 3810 (CNDF a, now modelled); cnd2_nonzero now STOPs append at
wait_nil 3986 (MCF with EM1 02: 3985's end not taken), 13 of 16;
em1_29_off now STOPs at 31a1 (MCF with EM1 0a: 31ee's MCF 08 and R04
are modelled now), 4 of 16.  check_pu.py's injections are unchanged.
New injections, observed:
  jmpf2_off       JMPF 2 raises again: append and the VECT0o case STOP at
                  2447, 12 of 16
  jmpf2_unsigned  EM3 unsigned (2447 -> 2450 | 0): append FAILs at
                  instruction 12 (5 words, no branch: 2450 jumps to 245e,
                  which ends, R04 not written), the VECT0o case FAILs (R04
                  still pc + 1)
  tdar_col_tdpf   the TDAR column = TDPF (0): ATOMo is 4 there, 2444's
                  jump to 24b1 forms MRP: both STOP at 2444, 12 of 16
  tdar_col6       column 6: append PASSES (14 of 16; ATOMo is 0 in both
                  columns); the VECT0o case STOPs at 2446 (VECT0 is 6):
                  only that case discriminates
  other_row_entry the other tags start at the entry: append FAILs at 12
                  (3300 treats nil as a list: 3305-3309 put a cell on the
                  R19 list and R02 := 0, no branch); the VECT0o case STOPs
                  at 3309
  e_on_true       JMPF e taken on COND: append FAILs at 12 (2441-2445
                  write [MAR1], a stale address); the VECT0o case STOPs at
                  2445 (MAR2 never set)
  a_on_false      JMPF a taken on false: append FAILs at wait_nil (3981
                  writes [MAR1]), 13 of 16
  col_true        COL true for a directly held operand: append FAILs at
                  12 (10 words: 2461 falls to 2462, which reads [MAR2],
                  then 247b-2480 put a cell on the R19 list: a cell
                  written); the VECT0o case STOPs at 2462 (MAR2 never set)
  r04_pc          the A stage's R04 = pc: append FAILs at 12 (R04 =
                  the label - 1); the VECT0o case FAILs the same way
  mrb_swapped     EM2 20 = MRB on: append FAILs at 12 (A0 := {ATOMx, 0}),
                  the VECT0o case FAILs (A0 VECT0x)
  mcf08_raise     MCF 08 raises: both STOP at 2461, 12 of 16
  mdr2_own_off    the S stage leaves MDR2 as it was: append PASSES (14 of
                  16: the old MDR2 is not a REFo either); the VECT0o case
                  STOPs at 3310 (ALU input never set): that MDR2 is loaded
                  is discriminated, its value NOT
  cnd8_off        CNDF 8 / a / c unmodelled: STOP at 38b0, still 14 of 16
                  (33 words): the get_value rules are needed to reach 0c0c,
                  NOT discriminated (no comparison before the stop)
  sd1_pairs_off   SD1F 2 / 3 unmodelled: STOP at 38b2 (35 words), as above
  jmpf9_off       JMPF 9 raises: STOP at 38b1 (34 words), as above
  s_cond_false    S_ENTRY's COND forced false (and S_OTHER_ROW's): append
                  FAILs at instruction 1 (3300's jump taken: a cell
                  written at 1ea): the COND's false side is pinned, so a's
                  polarity at 3980 stands on its own
  e_mdr2_col      e taken on COND, MDR2 a REFo (where S_MDR2_OWN applies)
                  and COL true, together: append PASSES (14 of 16, the
                  same 37 words) and so does the VECT0o case: the three
                  are tied; rassy's pool (e 'if not cond') breaks it
Also since these: where pimm.py leaves sp, R02 must not move (the
check other_row_entry now also FAILs: R02 := 0 at 3305); MRP / COL are
cleared at every instruction's set-up.  Re-run of every injection on
the final tree: the results above stand.

Observed 2026-11-27, seventh session: every side case ok; 15 of 16
instructions executed and matched, 49 held microinstructions:
get_value 1,2,0 (nil against the unbound Z1) runs the general unifier
whole, 16 words (38b0-38b3; 0c0c, a JMPF b call taken to 0c15; 0e38,
0e75, the dereference of A2 through its REFo to the UNDF cell, row 0e72
returning; 0c0d, 0c0e, 0802, 0840, 0841, 0864, the binding [cell] :=
nil; 09d0, the end with sw01 clear), and the cell pimm.py binds (its
M line) is compared.  The first stop is proceed (6657), given a set-up
form (setup.FORMS, OURS: no operand), at 216c: R1b (the goal-record
list) never set.  proceed is left there with a reason (README "Next,
for U2"): pimm.py's proceed writes no register or cell and is the last
instruction (no next PC), and the routine is the goal scheduler (R1b,
R14, R0d, R15), state neither model holds.
New in the model (pu.py): CASE_TAG_SETUP (EM1 30-3f), RULES jmpf_b_call,
case_wide, tdar_holds, as1f3_open_unknown (superseded in the eighth
session by alu_sources), MCF_FLAG_OPS with FLAG_CONDS
sw00-sw02, ALF_CONDS with MCF set_alf; setup.S_MAR1_DIRECT_STALE.  The
old injections give the results listed above, except (all re-run):
e_mdr2_col, s_cond_true, deref_tgt_col0, prs_operand_x, flags_swapped,
cnd3_off, tdar_col6 and mdr2_own_off now leave append at 15 of 16 (49
words; e_mdr2_col's tie stands through get_value); cnd8_off,
sd1_pairs_off and jmpf9_off stop before 0c0c as before; MAR1 STALE for an operand held directly
turns these FAILs into STOPs at the first use of MAR1 (a STOP on a
STALE value is weaker evidence than a FAIL against pimm.py: it shows
the path uses a value the harness does not know, not that the value is
wrong): s_cond_false
and s_imm_row STOP at 3309 (instruction 1, CCF: MAR1 STALE), other_row_
entry STOPs append at 3309 (12 of 16) and the VECT0o case at 3309,
e_on_true STOPs at 2445 (12 of 16), a_on_false at 3981 (13 of 16);
cjump_false and slit_pending now call 4cc5 and STOP at 4cc6 (JMPF c
polarity not decided), 10 of 16, 23 words; deref_tgt_col5's list case
now FAILs (3498's EM1 34 is case_tag_setup mdr1 2: the rows run and
write cells) where it stopped at 3498.  New injections, observed:
  jmpf_b_jump     JMPF b a page jump (the old reading): STOP at 0e72
                  (return with an empty micro stack), 14 of 16, 41 words
  cts_as1         case_tag_setup on the AS1 input's tag (the old 3a
                  rule's source): 0c0c's AS1 is MAR1, STALE: STOP at 0c0c,
                  14 of 16, 37 words (with s_mar1_kept as well, MAR1's
                  carried INTo gives column 0 byte 4: the trap at 0e3c)
  case_low4       S8 literally, the byte & 15 (the rival of case_wide):
                  UNDF 18 lands on 0e62, the row that frees a cell bound
                  to an atomic value: FAIL at 14 (17 words: heap 0
                  written with nil, the cell e000800b given the free-list
                  link 11:f2000001 where pimm.py binds it to nil)
  proceed_seeded  (removed in the eighth session: the proceed side cases
                  below replace the probe)
  cts_col_k       column k, not 7 - k: STOP at 0c15 (column 7 gives the
                  REFo 12, which overlaps base 0e38), 14 of 16
  cts_mdr_swapped EM1 even = MDR2, odd = MDR1: 0c0c tests nil (MDR1):
                  column 0 byte 4, 0e3c calls the trap: STOP at 6c21
  case_4bit       a TGT byte over 15 raises: STOP at 0e75 (UNDF 18 in
                  column 5), 14 of 16 (a guard; case_low4 discriminates)
  tdar_one_word   the set-up must be the word just before: STOP at 0802
                  (0c0d's set-up, 0c0e between), 14 of 16 (a guard: the
                  rule is needed, NOT discriminated)
  sw01_set        MCF 04 sets sw01: 0864's COND true, 09d0 falls to 09d1,
                  which binds the cell to {ATOMx, 0}: FAIL at 14 (heap
                  e000800b firmware 03:00000000, pimm.py 02:00000000)
  as1f3_open_raise AS1F 3 with AS2F 2 raises: STOP at 0802, 14 of 16
  s_mar1_kept     MAR1 keeps the previous instruction's value: append
                  PASSES (15 of 16): what MAR1 holds is NOT used on the
                  path (0c0c W1d := MAR1, 0c0d XR := W1d, both dead)
Eighth session, the datapath read from rassy (pu.py RULES alu_sources,
alu_const, as1f3_mar_xr; S1_IMM / S2_IMM; sc2f1_ir 'ext_ir'; setup.
EXECUTE_MDR1_STALE).  On append these change no compared value (4cc0's
R15 := MDR1 - 2 is not compared), so each injection below leaves append
at 15 of 16, 49 words, stop 216c: NOT discriminated here.  as1f2_off and
as1f3_open_raise now also set alu_sources 'old' and give their old
results (STOP at 4cc0, 10 of 16; STOP at 0802, 14 of 16).
  alu_old         the three old ALU rules: 15 of 16 (unchanged)
  const_em3       EM3 as the ALU constant: 15 of 16 (unchanged)
  em_imm_off      S1 5/6/7 registers again (zero_regs): 15 of 16
  as1f3_xr_off    AS1F 3 AS2F 2/3 UNKNOWN: 15 of 16 (0802's result feeds
                  only 0841's POISON alf_equal)
  execute_mdr1_carried  MDR1 as left: 15 of 16
  ext_ir_off      SC2F 1 the old c16s reading: 15 of 16 (31ec's value is
                  loaded into MDR2 and not used)
The proceed side cases (proceed_cases; eighth session; README "Next,
for U2"): proceed's routine on a ready queue built by pimm.py's own
record() and laid out as the firmware's records (seed_proceed,
fw_record: OURS mapping, layout INFERRED), compared with pimm.py's
pick: R04 (the next goal's code), A0..An-1, R10, R14 (pimm.py's rq
after the pick), and no cell written but the freed record (declared:
R1b := it, its cell 0 := {VECT0x, old R1b}).  Cases: the queue empty
with crr 8 and 1 (the empty arm 21b2 entered through 2170 / 217b,
checked in the trace; nothing dispatched, pick 0; pinned stop
EMPTY_STOP 21b3, an ALF 3 shift), one goal of arity 2, and two goals
whose newest has arity 0 .. 11.  All 15 ok.
Injections, observed (append itself unchanged at 15 of 16 in each):
  rec_code_13     cells 12 / 13 swapped: the 13 queued cases FAIL on R04
  args_from_2     arguments from cell 2: the 12 cases of arity > 0 FAIL
                  on the A registers
  empty_fw_goal   a goal given to the firmware while pimm.py's queue is
                  empty: the crr-8 empty case FAILs (the firmware
                  dispatched R04), the crr-1 one STOPs at 217c
  empty_int0      the empty queue as {INT, 0}: the empty cases STOP
                  (2173, 217c), the one-goal case FAILs on R14
  parent_other    cell 14 not R13: the 13 queued cases STOP at 2250
  free_undeclared the freed record's write not declared: all 15 FAIL
  rfar_off        DSTF c a register again: the 12 cases of arity > 0 FAIL
  lc_new          lc conditions after the decrement: arity 4 STOPs at
                  222b, arities 5 .. 11 FAIL (the last A not loaded)
  alf_poison      alf_zero POISON again: all 15 STOP at 216f
  alf_zero_false  alf_zero always false: the crr-1 empty case FAILs (the
                  empty arm not reached through 217b)
  jmpf9_taken_raise  JMPF 9 taken raises: the crr-1 empty case STOPs
                  at 217b (a guard: the target reading is NOT
                  discriminated, both readings land on 21b2)
  jmpf9_cndf_off  no CNDF in a JMPF 9 word: the 13 queued cases STOP at
                  2250 (2215 tests 2213's interrupt flag)
  jmpf_f_off      JMPF f undecided: the 13 queued cases STOP at 2215
  alu_old         all 15 STOP at 216d (AS1F 2 AS2F 1 read as YR)
  em_imm_off      all 15 STOP at 216d (R0d never set)
  const_em3       the 13 queued cases STOP at 217c (216d's R15 - 12), the
                  crr-8 empty case FAILs on its route
  as1f3_xr_off, ext_ir_off, execute_mdr1_carried: no change (NOT
                  discriminated)
Every old injection was re-run (scratch maindiff.py against the run
before the proceed rules).  Their main-run results are unchanged except
three, which now run further: em1_29_off still STOPs at 31a1, now on
its JMPF 2 (MCF 0a with sub-key 2 is rf_lock, recorded); interrupt_
pending STOPs at 1c2f (1c2c's lc_zero is now formed), 10 of 16, 31
words; s_imm_row's get_atom case STOPs at 0cd9 (3811's taken JMPF 9 now
calls its EM).  These also fail proceed side cases (of 15):
a_on_false 14, as1f2_off 15, as1f3_open_raise 15, cjump_false 14,
cjump_same 14, cnd2_nonzero 13, cnd3_off 15, cnd8_off 15, e_mdr2_col 1,
e_on_true 1, interrupt_pending 13, jmpf9_off 14, mcf08_raise 15,
mcf_unknown_raise 15, slit_pending 13.
U3 third step (2026-11-28), re-diffed against a clean 03fb0ffd: three
injections now run further and are still caught.  cnd2_nonzero FAILs at
wait_nil (R04: 3986's MCF EM1 02 sub-key 4 is f_jump, pu.MCF_SUB) where
it stopped there, 13 of 16, 35 words.  deref_tgt_col5 FAILs at
read_variable (reg 3, sp, R04: 3492's MCF likewise) where it stopped,
2 of 16.  interrupt_pending STOPs at 1c31 (read of W15: 1c2e's alf_high
is now formed), 10 of 16, 35 words.  mcf_unknown_raise also switches
pu.RULES['susp_flags'] off (06 / 07 now set the suspension flags) and
is unchanged.  Every other injection is unchanged.
U3 (2026-11-27, first session), the rules pu.RULES['ccf_rassy'],
['wsel_d_em1'], ['jmpf8_goto_if'] and setup.EXECUTE_MDR1_EMO1: this run
and every injection above unchanged (diffed against a clean snapshot),
except where a failing side case now stops one word later, after
2222's CCF 0d (read ++ mar2 MDR2): cjump_same, e_mdr2_col, e_on_true
and lc_new STOP at 222d (an ALU input read from memory never written)
where they stopped at 222b (MAR2 never set), the same cases failing;
odpf3_bits10 STOPs at 31f3 (a STALE condition) where it stopped at 31a3
(4 of 16 either way).  execute_mdr1_carried is now a no-op (execute's
MDR1 is R15's value, STALE here: u2 holds no R15).
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
import pimm  # noqa: E402

APPEND = 6644           # scsi_fep_module append/3 in the IPL image (kbndis)
R_ALT = 0x11            # rassy's register-file 1, 'ap': try_me_else writes it (216a)
NFREE = 32
# The furthest point, pinned: (instructions of pimm.py's run, executed and
# matched, held microinstructions in them, the index of the first stop).
# Any change, forward or back, fails until the pin is updated.
# Owner decision (2026-11-28): this standalone pin stays at 15 of 16, as
# this harness seeds the scheduler (seed_proceed).  Append's 16th
# instruction is counted, 16 of 16, in u3_goals.py's append2 program
# (APPEND16_PINNED), where proceed reads only firmware-written state
# after the 199-word held boot.
PINNED = dict(steps=16, matched=15, words=49, stop=15)


def pimm_run():
    """append([a], [], Z) on pimm.py.  Returns (machine, the state at the
    first instruction, [(pc, cell, lines, after)]): for each instruction
    its trace lines and pimm.py's state after it (reg, sp, alt)."""
    m = pimm.Machine()
    c = m.alloc(2)
    m.mem[c] = (pimm.ATOM, 0x123)
    m.mem[c + 1] = pimm.NIL
    z = m.new_var()
    m.tr = []
    steps = []
    snap = {}

    def state():
        return {'reg': list(m.reg[:16]), 'sp': getattr(m, '_sp', None),
                'alt': getattr(m, 'alt', None)}

    orig = m.event

    def event(text):
        if text.startswith('I '):
            if steps:
                steps[-1][3].update(state())
            else:
                snap.update(state())
                snap['mem'] = dict(m.mem)
            f = text.split()
            steps.append((int(f[1]), (int(f[2][:2], 16), int(f[2][2:], 16)), [], {}))
            marks.append(len(m.tr) + 1)
        elif steps:
            if text.startswith('E') or text == 'Q':
                steps[-1][3].update(state()) if not steps[-1][3] else None
        orig(text)
    marks = []
    m.event = event
    m.run(APPEND, [(pimm.LIST, c), pimm.NIL, z])
    if not steps[-1][3]:
        steps[-1][3].update(state())
    # The R and M lines go to m.tr directly (pimm._Regs / _Mem), not
    # through event(): each instruction's lines are the slice of m.tr
    # from its I line to the next.  (Before 2026-11-27 they were taken
    # from event() alone, which never sees them: every instruction had
    # no R / M lines, and a firmware write was reported as a stray.)
    for k, st in enumerate(steps):
        end = marks[k + 1] - 1 if k + 1 < len(marks) else len(m.tr)
        st[2].extend(ln for ln in m.tr[marks[k]:end] if ln[:2] in ('R ', 'M '))
    return m, snap, steps


# start's heap-top routine (2028 calls 204b): it reads the parameter cell
# 1a0 + 4a (SC2F b immediates, RULES['sc2_wide']), rounds it up to 16
# (CNDF 2, RULES['cnd2_zero'], and the conditional return 2050) and puts
# it in R1f, rassy's 'hp'.  The cell's value comes from outside, the
# loader's memory map (PIMM.PARAM's ihp, "Initial Heap Top Pointer",
# 16'E0000000 on the held Pseudo Multi-PSI): OURS, pimm.py's own heap
# pointer for the same program, so both models' heaps start together.
PARAM_BASE = 0x1a0      # the wide immediate start's words add to (204c, 2032, 2071, ...)
PARAM_HP = PARAM_BASE + 0x4a
HEAP_TOP = 0x204b


def boot_heap_top(p, hp):
    """Run start's held 204b-2052 as a microsubroutine with the parameter
    cell = hp.  Returns the words executed; R1f is left set."""
    p.mem[PARAM_HP] = (pimm.INT, hp)
    return p.call(HEAP_TOP)


def boot_contract():
    """The contract that decides CNDF 2 (with the return's polarity):
    R1f = the parameter rounded up to 16, for aligned and unaligned
    parameters.  Returns a list of failures."""
    bad = []
    for hp in (0xe0000000, 0xe0008003, 0xe000800f, 0xe0008010, 0x1234):
        p = PU.PU()
        try:
            boot_heap_top(p, hp)
        except PU.Unmodelled as e:
            bad.append('hp %x: STOP %s' % (hp, e))
            continue
        want = (hp + 15) & ~15
        if p.r.get(0x1f, (None, None))[1] != want:
            bad.append('hp %x: R1f %s, want %x' % (hp, check_pu.fmt(p.r.get(0x1f)), want))
    return bad


def s_stage_case():
    """The case that decides setup.S_ENTRY: get_atom (a tag immediate of
    UNDF, entry 3800) on an unbound variable, on both models from the
    same state.  pimm.py binds the cell to {ATOM, atom}.  Returns a list
    of failures."""
    import mekbn
    fw = mekbn.Firmware()
    k, atom, var = 5, 0x000456, 0xe0010000
    op = fw.kl1_entries()['get_atom'][0] & 0xe0 | k
    ir = (0x23, op << 24 | atom)
    m = pimm.Machine()
    m.mem[var] = (pimm.UNDF, 0)
    m.reg[k] = (pimm.REF, var)
    pc = len(m.cells)                 # the instruction cell, just past the code
    m.cells.append(ir)
    m.i_get_atom(pc, (ir[1] >> 16) & 255, (ir[1] >> 8) & 255, ir[1] & 255, ir[1] & 0xffff)
    p = PU.PU(fw)
    p.mem[var] = (pimm.UNDF, 0)
    p.an[k] = (pimm.REF, var)
    p.ir, p.pc = ir, m.load + pc
    try:
        name = SU.decode(p)
        n = p.run(SU.setup(p, name))
    except (PU.Unmodelled, KeyError) as e:
        return ['get_atom on an unbound variable: STOP %s' % e]
    bad = []
    if p.mem[var] != m.mem[var]:
        bad.append('get_atom on an unbound variable (%d words): cell %s, pimm.py %s'
                   % (n, check_pu.fmt(p.mem[var]), check_pu.fmt(m.mem[var])))
    if p.an[k] != m.reg[k]:
        bad.append('get_atom: A%d %s, pimm.py %s' % (k, check_pu.fmt(p.an[k]), check_pu.fmt(m.reg[k])))
    return bad


def read_list_element_case():
    """The case that discriminates the dereference set-up at 34a1
    (pu.DEREF_SETUP) from a TGT column: read_variable on a structure whose
    element is a list pointer (LISTo), the structure reached with every
    MRB off (pimm.py sp_single: the element is taken unmarked).  The
    4-way code 'other' runs row 3494 (x := the element, R02 + 1); TGT
    column 0, which sends an atom to 3494 too (and so passes append),
    sends LISTo to 3492.  Returns a list of failures."""
    import mekbn
    fw = mekbn.Firmware()
    x, sp, cell = 3, 0xe0020000, 0xe0030000
    op = fw.kl1_entries()['read_variable'][0] & 0xff
    ir = (0x23, op << 24 | x << 16)
    m = pimm.Machine()
    elem = (pimm.LIST, cell)
    m.mem[sp] = elem
    m.mem[cell] = (pimm.ATOM, 0x77)
    m._sp, m.sp_single = sp, True
    m.i_read_variable(0, x, 0, 0, 0)
    p = PU.PU(fw)
    p.mem[sp] = elem
    p.mem[cell] = (pimm.ATOM, 0x77)
    p.r[SU.R_SP] = (0, sp)
    check_pu.seed_lists(p, NFREE)
    p.ir, p.pc = ir, 0
    mem0 = dict(p.mem)
    try:
        name = SU.decode(p)
        n = p.run(SU.setup(p, name))
    except (PU.Unmodelled, KeyError) as e:
        return ['read_variable on a list element: STOP %s' % e]
    bad = ['read_variable on a list element: firmware wrote %x := %s, pimm.py no write'
           % (a, check_pu.fmt(p.mem[a])) for a in sorted(p.mem) if p.mem[a] != mem0.get(a)]
    if p.an.get(x) != m.reg[x]:
        bad.append('read_variable on a list element (%d words): A%d %s, pimm.py %s'
                   % (n, x, check_pu.fmt(p.an.get(x)), check_pu.fmt(m.reg[x])))
    if p.r[SU.R_SP][1] != m._sp:
        bad.append('read_variable on a list element: R02 %s, pimm.py sp %x'
                   % (check_pu.fmt(p.r[SU.R_SP]), m._sp))
    return bad


def reuse_cases():
    """put_reused_structure off append's path (the 31ec-31ed rules):
    (1) 3,0,2 on a list held directly in A0 with its MRB off: on both
    models, under the declared difference 'reuse' (A3 and R02 against
    pimm.py's reg[3] and sp; A0 untouched) -- tells the operand field y
    from x, which append (0,0,2) cannot;  (2) 0,0,2 on a list with its MRB
    ON (LISTx, shared): the contract is that it is NOT reused in place,
    so the routine must not end at 31ed; it goes on into the allocating
    arm, where the model stops at 31ee (MCF with EM1 08, not modelled):
    pinned as REUSE_SHARED_STOP.  Returns a list of failures."""
    import mekbn
    fw = mekbn.Firmware()
    op = fw.kl1_entries()['put_reused_structure'][0] & 0xff
    bad = []
    cell = 0xe0040000
    for tag, (x, y, z) in ((pimm.LIST, (3, 0, 2)), (pimm.LIST | 1, (0, 0, 2))):
        ir = (0x23, op << 24 | x << 16 | y << 8 | z)
        m = pimm.Machine()
        m.mem[cell], m.mem[cell + 1] = (pimm.ATOM, 1), pimm.NIL
        m.reg[0], m.reg[3] = (tag, cell), (pimm.INT, 9)
        m.tr = []
        m.i_put_reused_structure(0, x, y, z, ir[1] & 0xffff)
        p = PU.PU(fw)
        p.mem[cell], p.mem[cell + 1] = (pimm.ATOM, 1), pimm.NIL
        p.an[0], p.an[3] = (tag, cell), (pimm.INT, 9)
        check_pu.seed_lists(p, NFREE)
        p.ir, p.pc = ir, 0
        an0, mem0 = dict(p.an), dict(p.mem)
        what = 'put_reused_structure %d,%d,%d on %s' % (x, y, z, check_pu.fmt((tag, cell)))
        try:
            name = SU.decode(p)
            n = p.run(SU.setup(p, name))
        except (PU.Unmodelled, KeyError) as e:
            if tag & 1 and getattr(e, 'upc', None) == REUSE_SHARED_STOP:
                continue            # the shared list went on into the allocating arm
            bad.append('%s: STOP %s' % (what, e))
            continue
        if tag & 1:
            bad.append('%s: ended after %d words (%04x), a shared list reused in place'
                       % (what, n, p.trace[-1][0]))
            continue
        rn = check_pu.Rename()
        for a in mem0:
            rn.f2p[a] = rn.p2f[a] = a
        lines = [ln for ln in m.tr if ln[:2] in ('R ', 'M ')]
        after = {'sp': m.sp}
        bad += ['%s: %s' % (what, f) for f in
                compare(p, m, rn, lines, after, name, an0, mem0)]
    return bad


REUSE_SHARED_STOP = 0x31ee


def switch_label_case():
    """switch_on_non_list 0,0,8 on an empty vector {VECT0o, 0} held in A0
    (U2, 2026-11-27, sixth session): the case that tells setup.S_TDAR's
    column 7 (TDPF 0) from column 6, which append's nil cannot (ATOMo is
    0 in both).  On column 7 VECT0o is 0 too, the constants' row 2440, and
    the routine branches to the label as for nil (3310-3311, 2447, 2440,
    2461, 241d); on column 6 it is 6, 2446's jump to 24b1.  pimm.py
    (i_switch_on_non_list): not a list, so pc + 2 + c16; A0 unchanged, no
    cell written.  Returns a list of failures."""
    import mekbn
    fw = mekbn.Firmware()
    op = fw.kl1_entries()['switch_on_non_list'][0] & 0xff
    c16, pc = 8, 0x500
    ir = (0x23, op << 24 | c16)
    w = (pimm.VECT0, 0)
    m = pimm.Machine()
    m.reg[0] = w
    want = m.i_switch_on_non_list(pc, 0, 0, 0, c16)
    p = PU.PU(fw)
    p.an[0] = w
    check_pu.seed_lists(p, NFREE)
    p.ir, p.pc = ir, pc
    p.r[R_PC] = (COD, pc + A_STAGE_R04) if A_STAGE_R04 is not None else PU.STALE
    mem0 = dict(p.mem)
    what = 'switch_on_non_list 0,0,8 on {VECT0o, 0}'
    try:
        name = SU.decode(p)
        n = p.run(SU.setup(p, name))
    except (PU.Unmodelled, KeyError) as e:
        return ['%s: STOP %s' % (what, e)]
    bad = ['%s: firmware wrote %x := %s, pimm.py no write' % (what, a, check_pu.fmt(p.mem[a]))
           for a in sorted(p.mem) if p.mem[a] != mem0.get(a)]
    if p.an.get(0) != m.reg[0]:
        bad.append('%s: A0 %s, pimm.py %s' % (what, check_pu.fmt(p.an.get(0)),
                                              check_pu.fmt(m.reg[0])))
    if p.r.get(R_PC) != (COD, want):
        bad.append('%s (%d words): R04 %s, pimm.py next instruction {COD, %x}'
                   % (what, n, check_pu.fmt(p.r.get(R_PC)), want))
    return bad

# execute (6654, entry 4cc0; U2 2026-11-27, fifth session).  What the
# harness gives it, OURS:
#   - the hardware flags pu.FLAG_CONDS tests: no asynchronous event
#     pending (slit_check) and no interrupt (interrupt_all), as on one PE
#     with no GC request, message or signal (pimm.py has none either);
#   - R0d, W1f (and, until the sixth session, R04: now A_STAGE_R04) as
#     STALE (pu.STALE: values the harness does not know).  R0d was read as a scratch register (47 writers in image 2,
#     none on the path run before execute: those are the DSTF-d words
#     with WRBF clear, since U3d read as W(EM1), pu.RULES['wsel_d_w_em1'];
#     4cc0's select d is SC2F, the EM3 immediate, and no word run reads
#     R0d now; the STALE seed is kept, unread); W1f is written at boot (20a8, W1f := 0,
#     read not run) and by proceed's 21a1-21fe; R04, rassy's 'pc', is the
#     A stage's program counter, given since the sixth session as
#     {COD, pc + 1} (A_STAGE_R04, below) and so no longer STALE.  On
#     the fast path (4cc0-4cc3) R0d and W1f feed only 4cc1's compare and
#     XR, which no word tests or keeps (cjump_time 'prev'), and R04's old
#     value goes to W14 (not compared): a STALE value reaching an
#     argument register, a cell, an address or a tested COND would STOP
#     or FAIL the run, so their values are shown not to matter here.
EXECUTE_FLAGS = {'slit_check': False, 'interrupt_all': False}
EXECUTE_STALE = (('R', 0x0d), ('W', 0x1f))
# U3d second step (2026-11-28): 4cc1's COND (CNDF 3: crr - EM3 of 4cc0
# negative) is now tested, by 4cc2's JMPF 8 (pu.RULES['jmpf8_flag']
# 'goto': crr run out takes execute's slow path 4cc4).  So execute needs
# crr (R15), which the standalone run does not hold (U3's boot writes it
# held, 20a6-20a7, crr := 17).  OURS: R15 = EXECUTE_CRR, not run out (as
# PROCEED_CRR below); before, R15 reached execute STALE and fed only that
# untested COND.  Injection 'execute_crr_stale' (R15 STALE again): STOP
# at 10, 4cc2 (a JMPF 8 with no usable condition).
EXECUTE_CRR = 8
R_PC = 0x04             # rassy's second bank 4, 'pc'
COD = 0x26              # kbn tag COD (the code-address tag 4cc2 stamps from EM2)


def seed_execute(p):
    p.flags.update(EXECUTE_FLAGS)
    if EXECUTE_CRR is not None:
        p.r[0x15] = (pimm.INT, EXECUTE_CRR)
    for f, n in EXECUTE_STALE:
        {'R': p.r, 'W': p.w}[f][n] = PU.STALE


# ---------------------------------------------------------------- proceed
# U2, eighth session: proceed (entry 216c) is the goal scheduler.  What
# the held words do with the state (README "U2", the proceed rows; each
# rule in pu.py):
#   216c-216d  push the finished goal's record (MAR1 = R10, NANO_ODPF1)
#              on R1b's list (rassy fgp): its cell 0 := {VECT0x, old R1b},
#              R1b := R10; R15 (rassy crr) := R15 - 1 (with_constant,
#              EM2 1), set_alf; YR := EM3 = 12 (S2_IMM).
#   216e-216f  R10 := R14 (rassy gsp, the goal stack); crr - 1 negative
#              (216e) or zero (216f, alf_zero) -> 217a; COND := R14 is nil.
#   2170       MAR1 := R14 + 12; R14 nil -> call 21b2 (the empty arm).
#   2171-2173  R16 (rassy ccc) - 1; R04 := cell 12 (the code address);
#   2213-2216  R12 (cpr) := cell 13; cell 14 against R13 (cfpp: another
#              foster parent calls 2250); R14 := cell 15 (the link);
#   2218-2224  lc := cell 0 - 3; A0, A1, ... := cells 1, 2, ... through
#              '++ rfar' (RFAR := 0 at 2215) under the lc loop; end.
# The stand-in below gives the state these words read.  OURS, each item:
#   R1b        one free goal record (FREE_GREC), the list's head;
#   R15, R16   crr and ccc not exhausted (PROCEED_CRR, PROCEED_CCC: > 1,
#              so 216e-216f and 2173 fall to the dequeue; their meaning,
#              a reduction / switch budget, is INFERENCE from the
#              decrements and is not compared);
#   R12, R13   the current priority and foster parent; a queued goal
#              carries the same R13 in cell 14 (one shoen);
#   W1f        0 (start's 20a8 writes W1f := 0, held, read not run);
#   R14        pimm.py's ready queue Machine.rq mapped onto records in
#              the firmware's layout (fw_record), or nil when it is empty
#              (216f / 217a test R14's tag against ATOMo; enqueue_goal's
#              4c06 puts the old R14 in cell 15, so the empty list's end
#              is what R14 held: nil, INFERRED).
# The record layout (INFERRED; pseudo_pimm_microcode.md section 18,
# corrected by this session's datapath): cell 0 {GOAL, arity} (enqueue_goal
# 4c00 YR := the IR's x field (ext_ir 6), 4c01 MDR2 := it stamped GOAL by
# TGIF 3's EM2 3c, 4c03 writes it at R10); cells 1.. the arguments (set_*
# write R10 + x, x from 1: pimm.py's i_enqueue_goal takes argv[1:x+1]);
# 12 {COD, code}, 13 the priority (R12), 14 the foster parent (R13), 15
# the link (enqueue_goal 4c03 MAR2 := R10 + 12 (with_constant EM2 12),
# then four writes of {COD, W10}, R12, R13, R14 in that order; suspend's
# 1c0d-1c10 the same; proceed's reads above take them back the same
# way).  Cells n+1 .. 11 hold what the recycled record held: FILLER.
PROCEED_CRR = 8
PROCEED_CCC = 8
PROCEED_PRIO = (pimm.INT, 0x40000000)
PROCEED_PARENT = (0x39, 0xf5000000)     # FPREC (1c12 stamps it on R13)
FREE_GREC = 0xf4000000
FW_RECS = 0xf6000000
HOOKO, GOAL, VECT0X = 0x0a, 0x3c, 0x11
FILLER = (pimm.INT, 0xdead)
NIL = (pimm.ATOM, 0)
REC_CODE, REC_PRIO, REC_PARENT, REC_LINK = 12, 13, 14, 15   # injection 'rec_code_13' swaps
ARG_BASE = 1            # cell of the first argument (injection 'args_from_2')
EMPTY_LINK = NIL        # the empty queue's R14 (injection 'empty_int0')
REC_PARENT_VALUE = None  # cell 14 as R13 (injection 'parent_other')
# proceed's empty arm (21b2, entered from 2170's call or 217b's JMPF 9)
# stops at its second word: 21b3 is an ALF 3 shift_left of W1f (by EM1
# 15, then 21b4 returns on the sign: bit 16 of W1f), and the shift
# operations are not modelled.  Past it the arm returns, or 21b5 starts
# a search of the goal stacks by priority that reads the Goal Stack
# Entry Table parameters at fixed cells b7 / b6 (PIMM.PARAM's gsesh and
# gseb, INFERENCE), which neither model holds.  So the empty case
# compares only: the arm was entered, no goal was dispatched (R04 and
# the A registers as they were), and no cell but the freed record was
# written; pimm.py's pick returns 0.  The stop is pinned here.
EMPTY_STOP = 0x21b3
EMPTY_ARM = 0x21b2


def fw_record(p, k, code, args, link):
    """Write pimm.py's goal (code a cell index, args) as firmware record k
    (the layout above, OURS mapping); returns its address."""
    a = FW_RECS + 16 * k
    for i in range(1, 12):
        p.mem[a + i] = FILLER
    p.mem[a] = (GOAL, len(args))
    for i, w in enumerate(args):
        p.mem[a + ARG_BASE + i] = w
    p.mem[a + REC_CODE] = (COD, code)
    p.mem[a + REC_PRIO] = PROCEED_PRIO
    p.mem[a + REC_PARENT] = REC_PARENT_VALUE or PROCEED_PARENT
    p.mem[a + REC_LINK] = link
    return a


def seed_proceed(p, ready, crr=None):
    """The scheduler stand-in (OURS, above).  ready: pimm.py's ready queue
    as [(code address, args)], newest first.  Returns the firmware records."""
    p.r[0x1b] = (VECT0X, FREE_GREC)
    p.r[0x15] = (pimm.INT, PROCEED_CRR if crr is None else crr)
    p.r[0x16] = (pimm.INT, PROCEED_CCC)
    p.r[0x12] = PROCEED_PRIO
    p.r[0x13] = PROCEED_PARENT
    p.w[0x1f] = (0, 0)
    p.flags.update(EXECUTE_FLAGS)
    recs, link = [], EMPTY_LINK
    for k, (code, args) in reversed(list(enumerate(ready))):
        a = fw_record(p, k, code, args, link)
        recs.insert(0, a)
        link = (HOOKO, a)
    p.r[0x14] = link
    return recs


def compare_dispatch(p, rec0, r1b0, an0, mem0, want, recs, route=None):
    """proceed's result against pimm.py's pick.  want: None (pick finds no
    goal) or (code address, args, next record index or None)."""
    bad = []
    # the finished goal's record is pushed on R1b's list: declared, as
    # 'reuse' (the cell and value exact; pimm.py frees nothing traced)
    if DECLARE_FREE:
        if p.r.get(0x1b) != (0, rec0[1]) and p.r.get(0x1b) != rec0:
            bad.append('R1b %s, the finished record %s' % (check_pu.fmt(p.r.get(0x1b)),
                                                            check_pu.fmt(rec0)))
        if p.mem.get(rec0[1]) != (VECT0X, r1b0[1]):
            bad.append('the finished record\'s cell 0 %s, want {VECT0x, old R1b}'
                       % check_pu.fmt(p.mem.get(rec0[1])))
    for a in sorted(set(p.mem) | set(mem0)):
        if p.mem.get(a) != mem0.get(a) and not (DECLARE_FREE and a == rec0[1]):
            bad.append('heap %x: firmware wrote %s' % (a, check_pu.fmt(p.mem.get(a))))
    if want is None:
        if p.r.get(R_PC) != an0['R04']:
            bad.append('pimm.py picks no goal; the firmware dispatched R04 %s'
                       % check_pu.fmt(p.r.get(R_PC)))
        ran = [u for u, _ in p.trace[an0['n0']:]]
        # the route to the empty arm: crr exhausted, 216f's alf_zero
        # branch and 217b's JMPF 9; not exhausted, 2170's call
        if route is not None and route not in ran:
            bad.append('the empty arm not reached through %04x' % route)
        if EMPTY_ARM not in ran:
            bad.append('pimm.py picks no goal; the firmware did not take the empty arm (%04x)'
                       % EMPTY_ARM)
        if p.an != an0['an']:
            bad.append('pimm.py picks no goal; the firmware wrote argument registers')
        return bad
    code, args, nxt = want
    if p.r.get(R_PC) != (COD, code):
        bad.append('R04 %s, pimm.py\'s next goal\'s code {COD, %x}'
                   % (check_pu.fmt(p.r.get(R_PC)), code))
    if p.r.get(0x10) != (HOOKO, recs[0]):
        bad.append('R10 %s, the dispatched record {HOOKo, %x}'
                   % (check_pu.fmt(p.r.get(0x10)), recs[0]))
    want14 = NIL if nxt is None else (HOOKO, recs[nxt])
    if p.r.get(0x14) != want14:
        bad.append('R14 %s, pimm.py\'s ready queue after pick %s'
                   % (check_pu.fmt(p.r.get(0x14)), check_pu.fmt(want14)))
    for i, w in enumerate(args):
        if p.an.get(i) != w:
            bad.append('A%d %s, pimm.py %s' % (i, check_pu.fmt(p.an.get(i)), check_pu.fmt(w)))
    # beyond the arity: the loop's minimum of two loads (2219, 2223) may
    # write A1 for an arity 0 or 1 goal, with the record's own cell 2
    for i in sorted(set(p.an) | set(an0['an'])):
        if i >= len(args) and p.an.get(i) != an0['an'].get(i):
            if not (i < 2 and p.an.get(i) == p.mem.get(recs[0] + 1 + i)):
                bad.append('A%d written %s beyond the arity %d'
                           % (i, check_pu.fmt(p.an.get(i)), len(args)))
    return bad


DECLARE_FREE = True
EMPTY_FW_GOAL = False
# The side case's goals: (arity, args).  Arities on both sides of 3 (the
# lc loop's set-up, 2218 lc := arity - 3) up to 11 (the slots 2219-2223
# load; pimm.py: "A goal has 11 argument slots").
DISPATCH_ARITIES = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)


def proceed_case(m, step, arities, crr=None):
    """proceed on the held microcode with pimm.py's ready queue made of
    goals of these arities (newest first); against pimm.py's pick on the
    same queue.  Returns (fails, stop)."""
    q = pimm.Machine()
    want = None
    for k in reversed(range(len(arities))):
        n = arities[k]
        args = [(pimm.INT, 100 * k + i) if i % 2 else (pimm.ATOM, 0x200 + 16 * k + i)
                for i in range(n)]
        q.record(pimm.READY, 1000 + 10 * k, args)
    g = q.pick()
    rq = []
    gs, h = [], g
    if g:
        # the queue as pimm.py held it before pick: g, then g's link on
        h = g
        while h:
            gs.append(h)
            h = q.mem[h + pimm.G_LINK][1]
    for h in gs:
        n = q.mem[h + pimm.G_ARGN][1]
        rq.append((q.mem[h + pimm.G_CODE][1],
                   [q.mem[h + pimm.G_ARGS + i] for i in range(n)]))
    if g:
        # pimm.py's ready queue after pick: q.rq, a record of the walk
        want = (rq[0][0], rq[0][1], gs.index(q.rq) if q.rq else None)
    p = PU.PU()
    check_pu.seed_lists(p, NFREE)
    p.r[SU.R_REC] = (0, check_pu.REC)
    pc, cellv = step[0], step[1]
    p.r[R_PC] = (COD, m.load + pc + 1)
    for i in range(16):
        p.an[i] = (pimm.INT, 0xa000 + i)      # the finished goal's registers (OURS)
    # injection 'empty_fw_goal': the firmware is given a goal while
    # pimm.py's queue is empty (the empty arm's comparison must FAIL)
    recs = seed_proceed(p, rq or ([(m.load + 1000, [])] if EMPTY_FW_GOAL else []), crr)
    p.ir, p.pc = cellv, m.load + pc
    rec0, r1b0 = p.r[SU.R_REC], p.r[0x1b]
    an0 = {'an': dict(p.an), 'R04': p.r.get(R_PC), 'n0': len(p.trace)}
    mem0 = dict(p.mem)
    stop = None
    try:
        name = SU.decode(p)
        p.run(SU.setup(p, name))
    except PU.Unmodelled as e:
        stop = str(e)
    if want is None and stop and stop.startswith('%04x:' % EMPTY_STOP):
        stop = None             # the empty arm's pinned stop (EMPTY_STOP)
    if stop:
        return [], stop
    route = None if want else (0x217b if crr is not None and crr <= 1 else 0x2170)
    return compare_dispatch(p, rec0, r1b0, an0, mem0, want, recs, route), None


def proceed_cases(m, step):
    """The side cases: the queue empty (crr not exhausted, and exhausted:
    217a / 217b's JMPF 9 to the same empty arm); one goal of arity 2 (the
    queue left nil); then two goals, the newest of each arity of
    DISPATCH_ARITIES (dispatched; R14 left at the other)."""
    out = []
    for crr in (PROCEED_CRR, 1):
        bad, stop = proceed_case(m, step, (), crr)
        out.append(('empty queue, crr %d' % crr, bad, stop))
    for q in [(2,)] + [(n, 1) for n in DISPATCH_ARITIES]:
        bad, stop = proceed_case(m, step, q)
        out.append(('queue of arities %s' % (q,), bad, stop))
    return out


def compare_execute(p, m, after):
    """execute: the firmware's next PC, R04, against pimm.py's next
    instruction (the I line after execute's).  The tag must be COD (4cc2
    stamps EM2 under TGIF 3, RULES['tgif3_tag']; the slow-path words
    4cc4, 4ccf stamp COD on R04 too).  pimm.py's i_execute also counts a
    reduction and clears alt; neither has a firmware register compared
    here."""
    want = after.get('next_pc')
    r04 = p.r.get(R_PC)
    if want is None:
        return ['execute: no next instruction in pimm.py\'s trace']
    if PU.is_stale(r04) or r04 is None or r04 != (COD, m.load + want):
        return ['R04 (pc): firmware %s, pimm.py next instruction {COD, %x}'
                % (r04 if PU.is_stale(r04) or r04 is None else check_pu.fmt(r04),
                   m.load + want)]
    return []


# The A stage's R04 (U2, 2026-11-27, sixth session; OURS, with support):
# while an instruction is in E, R04 (rassy's 'pc') holds the address of
# the cell after it, pc + 1, tag COD.  Support: the label branch adds the
# IR field to R04 (3310-3311) and 1 more (2447 YR := #1; 2461 R04 := XR +
# YR), where pimm.py's target is pc + 2 + c16; and switch_on_constant's
# rows (2420, 242c, 243c) put R04 in MAR1 and read the instruction's
# second cell there, pimm.py's cells[pc + 1].  Before 2026-11-27 (sixth
# session) R04 was STALE until execute wrote it.  Injection 'r04_pc'
# (R04 = pc): FAIL at instruction 12 (the label off by one).
A_STAGE_R04 = 1


def compare_next_pc(p, m, pc, after, name, r04_0):
    """Every instruction: the firmware's next PC against pimm.py's next
    instruction.  A firmware that wrote R04 (changed it from the A stage's
    value) branched there, with tag COD; one that did not falls through
    to pc + 1."""
    want = after.get('next_pc')
    if want is None or SU.base(name) == 'execute':
        return []           # the last instruction; execute: compare_execute
    r04 = p.r.get(R_PC)
    if r04 is not r04_0 and r04 != r04_0:
        if PU.is_stale(r04) or r04 != (COD, m.load + want):
            return ['R04 (pc): firmware %s, pimm.py next instruction {COD, %x}'
                    % (r04 if PU.is_stale(r04) else check_pu.fmt(r04), m.load + want)]
        return []
    if want != pc + 1:
        return ['no branch: firmware falls through to %d, pimm.py next instruction %d'
                % (pc + 1, want)]
    return []


def run(verbose=False):
    m, s0, steps = pimm_run()
    rbad = reuse_cases()
    print('%s  put_reused_structure off the path: 3,0,2 on LISTo (reused), 0,0,2 on'
          ' LISTx (not reused)%s' % ('FAIL' if rbad else 'ok  ',
                                     ': ' + '; '.join(rbad) if rbad else ''))
    sbad = s_stage_case()
    print('%s  S stage: get_atom on an unbound variable (entry 3800)%s'
          % ('FAIL' if sbad else 'ok  ', ': ' + '; '.join(sbad) if sbad else ''))
    wbad = switch_label_case()
    print('%s  switch_on_non_list on {VECT0o, 0} (the S-stage TDAR column)%s'
          % ('FAIL' if wbad else 'ok  ', ': ' + '; '.join(wbad) if wbad else ''))
    lbad = read_list_element_case()
    print('%s  read_variable on a list element (the 34a1 set-up)%s'
          % ('FAIL' if lbad else 'ok  ', ': ' + '; '.join(lbad) if lbad else ''))
    pbad = []
    for what, fails, stop in proceed_cases(m, steps[-1]):
        if stop:
            fails = ['STOP ' + stop]
        pbad += ['proceed, %s: %s' % (what, f) for f in fails]
        print('%s  proceed side case, %s%s' % ('FAIL' if fails else 'ok  ', what,
                                              ': ' + '; '.join(fails) if fails else ''))
    bad = boot_contract()
    print('%s  start 204b (heap top) on 5 parameters%s'
          % ('FAIL' if bad else 'ok  ', ': ' + '; '.join(bad) if bad else ''))
    p = PU.PU()
    # the boot's heap top, from pimm.py's heap pointer (OURS, above)
    try:
        nboot = boot_heap_top(p, m.hp)
    except PU.Unmodelled as e:
        print('STOP boot 204b: %s' % e)
        return {'fail': None, 'boot_fail': bad or [str(e)], 'matched': 0, 'stop': ('boot',)}, len(steps)
    # memory: every cell pimm.py holds when the first instruction is taken
    p.mem.update(s0['mem'])
    for i, w in enumerate(s0['reg']):
        p.an[i] = w                       # OURS: the goal switch
    p.r[SU.R_REC] = (0, check_pu.REC)
    check_pu.seed_lists(p, NFREE)
    seed_execute(p)
    rn = check_pu.Rename()
    for a in s0['mem']:
        rn.f2p[a] = rn.p2f[a] = a          # cells present in both: the identity
    out = {'done': 0, 'matched': 0, 'words': 0, 'stop': None, 'fail': None,
           'boot_words': nboot, 'boot_fail': bad + sbad + lbad + rbad + wbad + pbad}
    for k, (pc, cellv, lines, after) in enumerate(steps):
        p.ir, p.pc = cellv, m.load + pc
        if A_STAGE_R04 is not None:
            p.r[R_PC] = (COD, (m.load + pc + A_STAGE_R04) & 0xffffffff)
        r04_0 = p.r.get(R_PC)
        after['next_pc'] = steps[k + 1][0] if k + 1 < len(steps) else None
        # pimm.py's sp is compared only where pimm.py moves it (a branch
        # such as switch_on_non_list on nil leaves it as it was)
        after['sp_moved'] = after.get('sp') != (steps[k - 1][3] if k else s0).get('sp')
        after['r02_0'] = p.r.get(SU.R_SP)   # where it does not, R02 must not move
        name = '?'
        n0 = len(p.trace)
        an0, mem0 = dict(p.an), dict(p.mem)
        try:
            name = SU.decode(p)
            start = SU.setup(p, name)
            p.run(start)
        except (PU.Unmodelled, KeyError) as e:
            out['words'] += len(p.trace) - n0
            out['stop'] = (k, pc, name, str(e))
            print('STOP %2d %5d %-22s %s' % (k, pc, name, e))
            break
        nw = len(p.trace) - n0
        out['words'] += nw
        out['done'] += 1
        fails = compare(p, m, rn, lines, after, name, an0, mem0)
        fails += compare_next_pc(p, m, pc, after, name, r04_0)
        if fails:
            out['fail'] = (k, pc, name, fails)
            print('FAIL %2d %5d %-22s %d words: %s' % (k, pc, name, nw, '; '.join(fails)))
            break
        out['matched'] += 1
        print('ok   %2d %5d %-22s %d words' % (k, pc, name, nw))
        if verbose:
            for c in p.cycles[n0:]:
                print('      %04x %016x' % (c['micro_pc'], c['microword']))
    print('%d of %d instructions executed and matched, %d held microinstructions%s'
          % (out['matched'], len(steps), out['words'],
             '' if not out['stop'] else '; first stop: instruction %d (%d %s)'
             % out['stop'][:3]))
    return out, len(steps)


def compare(p, m, rn, lines, after, name, an0, mem0):
    fails, notes = [], []
    base = SU.base(name)
    covered = set()         # firmware cells a declared difference accounts for
    if base == 'put_reused_structure' and DECLARE_REUSE:
        fails += declare_reuse(p, rn, lines, an0, mem0)
    if base in ('write_variable', 'write_marked_variable') and DECLARE_INDIRECT:
        covered |= declare_indirect(p, m, rn, lines, mem0, notes)
    # what the firmware wrote that pimm.py did not: an argument register or
    # a cell changed by the routine with no R / M line for it
    rl = {int(ln.split()[1]) for ln in lines if ln.startswith('R ')}
    ml = {m.load + int(ln.split()[1]) for ln in lines if ln.startswith('M ')}
    for i in sorted(set(p.an) | set(an0)):
        if p.an.get(i) != an0.get(i) and i not in rl:
            fails.append('reg %d: firmware wrote %s, pimm.py no write'
                         % (i, check_pu.fmt(p.an.get(i))))
    for a in sorted(set(p.mem) | set(mem0)):
        if p.mem.get(a) != mem0.get(a) and rn.f2p.get(a, a) not in ml and a not in covered:
            fails.append('heap %x: firmware wrote %s, pimm.py no write'
                         % (a, check_pu.fmt(p.mem.get(a))))
    for line in lines:
        f = line.split()
        if f[0] not in ('R', 'M'):
            continue
        i, w = int(f[1]), f[2]
        pv = (int(w[:2], 16), int(w[2:], 16))
        if f[0] == 'R':
            if not rn.same(p.an.get(i), pv, False, notes, 'reg %d' % i):
                fails.append('reg %d: firmware %s, pimm.py %s'
                             % (i, check_pu.fmt(p.an.get(i)), check_pu.fmt(pv)))
        else:
            pa = m.load + i
            fa = rn.p2f.get(pa, pa)
            if not rn.same(p.mem.get(fa), pv, False, notes, 'heap'):
                fails.append('heap %x: firmware %s, pimm.py %s'
                             % (pa, check_pu.fmt(p.mem.get(fa)), check_pu.fmt(pv)))
    if base == 'execute':
        fails += compare_execute(p, m, after)
    if base == 'try_me_else':
        # INFERRED projection: R11 (rassy's 'ap') holds the alternative
        # clause, pimm.py's alt (a cell index; the firmware an address)
        r11 = p.r.get(R_ALT)
        want = m.load + after['alt']
        if r11 is None or r11 != (pimm.REF, want):
            fails.append('R11: firmware %s, pimm.py alt {REF, %x}' % (check_pu.fmt(r11), want))
    if after.get('sp') is not None and after.get('sp_moved', True) \
            and base in ('switch_on_non_list', 'read_variable', 'put_reused_structure'):
        r02 = p.r.get(SU.R_SP)
        if r02 is None or rn.f2p.get(r02[1], r02[1]) != after['sp']:
            fails.append('sp: firmware R02 %s, pimm.py %x' % (check_pu.fmt(r02), after['sp']))
    if after.get('sp') is not None and not after.get('sp_moved', True) \
            and p.r.get(SU.R_SP) != after.get('r02_0'):
        fails.append('sp: firmware R02 %s -> %s, pimm.py leaves sp at %x'
                     % (check_pu.fmt(after.get('r02_0')), check_pu.fmt(p.r.get(SU.R_SP)), after['sp']))
    return fails


# The declared difference 'reuse' (as U1's 'indirect' and 'mrb' in
# check_pu.py): the firmware reuses a single-referenced structure in
# place (31ec-31ed: x and R02 := the dereferenced pointer, no cell
# written, no free list popped), where pimm.py never reuses
# (i_put_reused_structure: z new cells, "no reference counts here, so
# nothing is ever reused"; pimm_semantics.md).  Declared only when the
# firmware's x holds the source structure's own address; then pimm.py's
# z new cells are paired with the z reused cells under the renaming, so
# that what write_* put in them later is compared cell by cell.  A
# firmware that allocated is compared with no declaration.
DECLARE_REUSE = True


def declare_reuse(p, rn, lines, an0, mem0):
    x, y, z = p.ir_field('x'), p.ir_field('y'), p.ir_field('z')
    w = an0.get(y)
    while w is not None and w[0] & ~1 == pimm.REF:
        w = mem0.get(w[1])
    fv = p.an.get(x)
    if w is None or fv is None or fv[1] != w[1]:
        return []
    got = [ln.split()[2] for ln in lines if ln.startswith('R %d ' % x)]
    if len(got) != 1:
        return ['reuse: pimm.py wrote reg %d %d times' % (x, len(got))]
    a = int(got[0][2:], 16)
    for i in range(z):
        fa, pa = w[1] + i, a + i
        for k in (rn.p2f.pop(pa, None),):
            if k is not None:
                rn.f2p.pop(k, None)
        old = rn.f2p.pop(fa, None)
        if old is not None:
            rn.p2f.pop(old, None)
        rn.f2p[fa], rn.p2f[pa] = pa, fa
    return []


# The declared difference 'indirect' (U1's, check_pu.py; README "What
# the held words answered" item 1): write_variable (3195-3199) puts in
# the structure element a {REF, c} to a NEW cell c, popped from the
# one-cell list and made UNDF, and gives x {REF, c}; pimm.py makes the
# element itself the variable.  The same term after dereference.
# Declared per M line of pimm.py whose firmware cell holds a REF to a
# cell the firmware wrote in this instruction (a free-list cell: the
# seeded lists are in memory before) holding pimm.py's value:
# that new cell is paired with pimm.py's cell, and the element written
# with the REF is accounted for.
DECLARE_INDIRECT = True


def declare_indirect(p, m, rn, lines, mem0, notes):
    covered = set()
    for ln in lines:
        f = ln.split()
        if f[0] != 'M':
            continue
        pa = m.load + int(f[1])
        pv = (int(f[2][:2], 16), int(f[2][2:], 16))
        fa = rn.p2f.get(pa, pa)
        fv = p.mem.get(fa)
        if not fv or fv[0] & ~1 != pimm.REF or fv[1] in rn.f2p \
                or p.mem.get(fv[1]) == mem0.get(fv[1]) or p.mem.get(fv[1]) != pv:
            continue
        notes.append('heap %x: firmware {REF, new cell %x}, pimm.py the cell itself' % (pa, fv[1]))
        rn.f2p.pop(fa, None)
        rn.p2f.pop(pa, None)
        rn.pair(fv[1], pa)
        covered.add(fa)
    return covered


def _no_mar1():
    d = SU.deref
    SU.deref = lambda pu, w: (d(pu, w)[0], None)


def _cond_true():
    s = SU.setup

    def setup(pu, name):
        start = s(pu, name)
        if SU.FORMS.get(SU.base(name), (None,))[0] == 's_tag':
            pu.cond = True
        return start
    SU.setup = setup


def _cond_false():
    s = SU.setup

    def setup(pu, name):
        start = s(pu, name)
        if SU.FORMS.get(SU.base(name), (None,))[0] == 's_tag':
            pu.cond = False
        return start
    SU.setup = setup


def _e_mdr2_col():
    # the joint alternative to the e polarity, S_MDR2_OWN and COL
    # (advisor 2026-11-27): e taken on COND, MDR2 a REFo, COL true
    PU.CJUMP_TAKEN_ON.update({0xe: True})
    SU.S_REPORTS_DIRECT.update(COL=True)
    s = SU.setup

    def setup(pu, name):
        start = s(pu, name)
        if SU.FORMS.get(SU.base(name), (None,))[0] == 's_tag' \
                and SU.base(name) not in SU.S_CONST:     # where S_MDR2_OWN applies
            pu.wr[SU.mekbn.MDR2] = (pimm.REF, pu.wr.get(SU.mekbn.MDR2, (0, 0))[1])
        return start
    SU.setup = setup


INJECT = {
    's_no_mar1': _no_mar1,
    's_cond_false': _cond_false,    # S_ENTRY's COND part forced false
    'e_mdr2_col': _e_mdr2_col,      # e on COND, MDR2 a REFo, COL true, together      # S_ENTRY's MAR1 part not loaded
    's_cond_true': _cond_true,  # S_ENTRY's COND part forced true
    's_imm_plus1': lambda: setattr(SU, 'S_ENTRY', 1),
    's_imm_row': lambda: setattr(SU, 'S_ENTRY', 'row'),
    'wide_em1em2': lambda: PU.RULES.update(sc2_wide='EM1:EM2'),
    'cnd2_nonzero': lambda: PU.RULES.update(cnd2_zero=False),
    'bit0_clear_off': lambda: PU.RULES.update(j1_bit0_clear_true=False),
    # U2 read_variable (2026-11-27): the dereference multiway set-up at 34a1
    'deref_imm_other': lambda: PU.DEREF_CODE.update(imm=1, other=0),
    'deref_bits10': lambda: setattr(PU, 'DEREF_SHIFT', 0),
    'deref_tgt_col0': lambda: (setattr(PU, 'DEREF_TGT_COLUMN', 0), setattr(PU, 'DEREF_SHIFT', 0)),
    'deref_tgt_col5': lambda: (setattr(PU, 'DEREF_TGT_COLUMN', 5), setattr(PU, 'DEREF_SHIFT', 0)),
    'deref_tgt_col7': lambda: (setattr(PU, 'DEREF_TGT_COLUMN', 7), setattr(PU, 'DEREF_SHIFT', 0)),
    'em1_28_tgt0': lambda: (PU.COND_UNKNOWN.clear(), PU.TGT_COLUMN.update({0x28: 0})),
    'absent_read_raise': lambda: PU.RULES.update(absent_read_poison=False),
    'jmpf8_off': lambda: PU.RULES.update(jmpf8_setup=False),
    # U2 put_reused_structure .. put_value (2026-11-27, third session)
    'odpf3_entry': lambda: setattr(SU, 'ODPF3_SHIFT', None),
    'odpf3_bits10': lambda: setattr(SU, 'ODPF3_SHIFT', 0),
    'em1_29_off': lambda: PU.RULES.update(em1_29_mrb='off'),
    'sc2f1_reg': lambda: PU.RULES.update(sc2f1_ir=None),
    'prs_operand_x': lambda: SU.FORMS.update(put_reused_structure=('s_odpf3', 'x')),
    'no_reuse_decl': lambda: globals().update(DECLARE_REUSE=False),
    'no_indirect_decl': lambda: globals().update(DECLARE_INDIRECT=False),
    'gbv_mdr2_x': lambda: SU.S_CONST.update(get_bound_value='x'),
    # U2 execute (2026-11-27, fifth session)
    'cjump_same': lambda: PU.RULES.update(cjump_time='same'),
    'cjump_false': lambda: PU.CJUMP_TAKEN_ON.update({0xb: False}),
    'slit_pending': lambda: EXECUTE_FLAGS.update(slit_check=True),
    'execute_crr_stale': lambda: globals().update(EXECUTE_CRR=None),
    'interrupt_pending': lambda: EXECUTE_FLAGS.update(interrupt_all=True),
    'flags_swapped': lambda: PU.FLAG_CONDS.update({0x19: 'interrupt_all', 0x21: 'slit_check'}),
    'as1f2_off': lambda: PU.RULES.update(alu_sources='old', as1f2_yr=False),
    # U3 third step: 06 / 07 now set the suspension flags first
    # (pu.SUSP_FLAG_OPS), so the injection turns that off too
    'mcf_unknown_raise': lambda: (PU.MCF_UNKNOWN.clear(), PU.RULES.update(susp_flags=None)),
    'jmpf8_flag_off': lambda: PU.RULES.update(jmpf8_flag=False),
    'cnd3_off': lambda: PU.RULES.update(cnd3_sign=False),
    'execute_mdr1': lambda: SU.LABEL_ODSF.update({2: 'MDR1'}),
    'tgif3_em1': lambda: PU.RULES.update(tgif3_tag='EM1'),
    # U2 switch_on_non_list on nil, wait_nil, get_value (2026-11-27, sixth session)
    'jmpf2_off': lambda: PU.RULES.update(jmpf2_case=None),
    'jmpf2_unsigned': lambda: PU.RULES.update(jmpf2_case='unsigned'),
    'tdar_col_tdpf': lambda: setattr(SU, 'TDAR_COLUMN', lambda t: t),
    'tdar_col6': lambda: setattr(SU, 'TDAR_COLUMN', lambda t: 6),
    'other_row_entry': lambda: setattr(SU, 'S_OTHER_ROW', None),
    'e_on_true': lambda: PU.CJUMP_TAKEN_ON.update({0xe: True}),
    'a_on_false': lambda: PU.CJUMP_TAKEN_ON.update({0xa: False}),
    'col_true': lambda: SU.S_REPORTS_DIRECT.update(COL=True),
    'r04_pc': lambda: globals().update(A_STAGE_R04=0),
    'mrb_swapped': lambda: PU.RULES.update(em2_mrb={0x20: 'on', 0x30: 'off'}),
    'mcf08_raise': lambda: PU.MCF_NAMED.clear(),
    'mdr2_own_off': lambda: setattr(SU, 'S_MDR2_OWN', False),
    'cnd8_off': lambda: PU.RULES.update(cnd8_s1=False),
    'sd1_pairs_off': lambda: PU.RULES.update(sd1_pairs=None),
    'jmpf9_off': lambda: PU.RULES.update(jmpf9_call_if=False),
    # U2 get_value's general unifier (2026-11-27, seventh session)
    'jmpf_b_jump': lambda: PU.RULES.update(jmpf_b_call=False),
    'cts_as1': lambda: setattr(PU, 'CTS_SOURCE', 'as1'),
    'case_low4': lambda: PU.RULES.update(case_wide='low4'),
    'cts_col_k': lambda: setattr(PU, 'CTS_COLUMN', lambda k: k),
    'cts_mdr_swapped': lambda: PU.CTS_MDR.update({0: PU.MDR2, 1: PU.MDR1}),
    'case_4bit': lambda: PU.RULES.update(case_wide=False),
    'tdar_one_word': lambda: PU.RULES.update(tdar_holds=False),
    'sw01_set': lambda: PU.MCF_FLAG_OPS.update({0x04: ('sw01', True)}),
    'as1f3_open_raise': lambda: PU.RULES.update(alu_sources='old', as1f3_open_unknown=False),
    # U2 eighth session: rassy's ALU pair, EM immediates, execute's MDR1
    'alu_old': lambda: PU.RULES.update(alu_sources='old'),
    'const_em3': lambda: PU.RULES.update(alu_const='EM3'),
    'em_imm_off': lambda: setattr(PU, 'EM_IMM', False),
    'as1f3_xr_off': lambda: PU.RULES.update(as1f3_mar_xr=False),
    'execute_mdr1_carried': lambda: setattr(SU, 'EXECUTE_MDR1_STALE', False),
    'ext_ir_off': lambda: PU.RULES.update(sc2f1_ir='c16s'),
    's_mar1_kept': lambda: setattr(SU, 'S_MAR1_DIRECT_STALE', False),
    # eighth session, proceed (the side cases, proceed_cases)
    'rec_code_13': lambda: globals().update(REC_CODE=13, REC_PRIO=12),
    'args_from_2': lambda: globals().update(ARG_BASE=2),
    'empty_int0': lambda: globals().update(EMPTY_LINK=(pimm.INT, 0)),
    'parent_other': lambda: globals().update(REC_PARENT_VALUE=(0x39, 0xf5000010)),
    'free_undeclared': lambda: globals().update(DECLARE_FREE=False),
    'rfar_off': lambda: PU.RULES.update(dstf_c_rfar=False),
    'lc_new': lambda: PU.RULES.update(lc_ops='new'),
    'alf_poison': lambda: setattr(PU, 'ALF_LATCHED', ()),
    'jmpf9_taken_raise': lambda: PU.RULES.update(jmpf9_vlong=False),
    'jmpf9_cndf_off': lambda: PU.RULES.update(jmpf9_cndf=False),
    'jmpf_f_off': lambda: PU.RULES.update(jmpf_f_call_ifnot=False),
    'empty_fw_goal': lambda: globals().update(EMPTY_FW_GOAL=True),
    'alf_zero_false': lambda: setattr(PU, 'alf_cond', lambda latch, name: False),
}


def main(argv):
    if '--inject' in argv:
        nm = argv[argv.index('--inject') + 1]
        INJECT[nm]()
        print('injected: %s' % nm)
    out, n = run('-v' in argv)
    got = dict(steps=n, matched=out['matched'], words=out.get('words'),
               stop=out['stop'][0] if out['stop'] else None)
    if '--inject' not in argv and got != PINNED:
        print('FAIL the furthest point moved: %s, pinned %s (update PINNED)' % (got, PINNED))
        return 1
    return 1 if out['fail'] or out['boot_fail'] else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
