"""The D/A/R/S stand-in: what the PU's non-microcoded stages leave in the
E stage's registers before the first microinstruction of a KL1-B
instruction runs (docs/pu_microcode_plan.md; M92 p.428, thesis
pp.125-129).

On the machine these stages are driven by the decode entry's nano-code
(Nakashima Fig. 3-22: ACF address calculation, DFF fetch kind, OS1F/OS2F
set-up sources, ODSF set-up destination, EMO1/EMO2 emits, TDPF the tag
branch set-up; docs/psi_microword.md 3a).  The held entries carry those
bits (asm/psdpim.py reads the table), but only some of their meanings
are decoded.  So:

  NANO_ODPF1 (INFERRED, generic): an entry whose nano-code field at
  Fig. 3-22's ODPF position is 1 pops a free list: the S stage loads the
  head register R(10 | EMO1) into MAR2 when ODSF is 0 and into MAR1 when
  ODSF is 1.  Fitted on set_variable (318b reads [MAR2], EMO1 9, ODSF 0)
  and put_list (31d0 reads [MAR1], EMO1 a, ODSF 1); predicted and met by
  every other ODPF 1 entry run here: put_variable, put_vector_1/2,
  write_variable.  Of the whole table, 14 entries have ODPF 1; read (not
  run), the others fit too: set_list, the *_marked_variable forms (pops
  through the MAR ODSF names), proceed (EMO1 0, ODSF 1: MAR1 := R10, the
  finished goal's record, which 216c-216d push on the R1b list,
  pseudo_pimm_microcode.md section 18), collect_list (EMO1 a, ODSF 2:
  the old R1a head is what 30a8 writes from MDR2, so ODSF 2 would be
  MDR2).  rassy's register-file names (binary_reverse_engineering.md
  section 3: 0 cgp, 9 fvp, 10 flp, 11 fgp, 15 hp) name R10, R19, R1a,
  R1b, R1f as the current goal pointer and the free variable, list and
  goal-record pointers and the heap pointer, as M92 p.427 lists them.
  Only ODSF 0 and 1 are run; any other raises.

  EMO2_TAG (MEASURED, pseudo_pimm_microcode.md section 3): the tag a
  constant operand carries is the entry's tag immediate (EMO2): INTo for
  the *_integer forms, ATOMo for the *_atom forms.

  FORMS (OURS): which operand goes where, per operand form, from
  pimm.py's operand readings (docs/pimm_semantics.md).  The A-stage
  address of a goal argument is R10 + argument number (R10: the goal
  record being built, pseudo_pimm_microcode.md section 18), of a
  structure element R02 (the structure pointer).
"""
import mekbn
import pu as _pu

R_REC, R_SP = 0x10, 0x02


def sx16(v):
    v &= 0xffff
    return v - 0x10000 if v & 0x8000 else v


def sx24(v):
    v &= 0xffffff
    return v - 0x1000000 if v & 0x800000 else v


NANO = {'ACF': (49, 47), 'DFF': (45, 44), 'ODPF': (35, 33), 'OS1F': (32, 30),
        'OS2F': (29, 27), 'ODSF': (26, 25), 'TDPF': (22, 20), 'EMO1': (19, 16),
        'EMO2': (15, 10), 'MAF': (9, 0)}
NANO_ODPF1 = True       # switch for injections
ODSF_MAR = {0: 'MAR2', 1: 'MAR1'}   # NANO_ODPF1's destination (check_pu.py injects a swap)


def nano(fw, idx):
    """The decode entry as one 56-bit number: first word's low 16 bits,
    second word's tag byte and value (Fig. 3-22 right-aligned on it)."""
    (v1, _), (v2, t2) = fw.entry(idx)
    n = (v1 & 0xffff) << 40 | t2 << 32 | v2
    return {k: n >> lo & ((1 << (hi - lo + 1)) - 1) for k, (hi, lo) in NANO.items()}


def base(name):
    """pimm.py's method name for a decode-table name."""
    if name.startswith('put_vector_N['):
        return 'put_vector_%d' % int(name[13:15], 16)
    return name.split('[')[0]


# operand form: (MDR1 source, MAR1 source)
#   MDR1: 'y' / 'x' register, 'c16' / 'c24' / 'a24' a constant (tag EMO2)
#   MAR1: 'arg_x' R10 + x, 'arg_op' R10 + the opcode's low four bits, 'sp' R02
FORMS = {
    'set_value': ('y', 'arg_x'), 'set_integer': ('c16', 'arg_x'),
    'set_atom': ('a24', 'arg_op'), 'set_nil': (None, 'arg_x'),
    'set_variable': (None, 'arg_x'), 'set_marked_variable': (None, 'arg_x'),
    'write_marked_variable': (None, None), 'put_marked_variable': (None, None),
    'put_value': ('y', None), 'put_integer': ('c16', None), 'put_atom': ('a24', None),
    'put_nil': (None, None), 'put_list': (None, None), 'put_variable': (None, None),
    'put_vector_0': (None, None), 'put_vector_1': (None, None), 'put_vector_2': (None, None),
    'write_value': ('x', 'sp'), 'write_integer': ('c24', 'sp'), 'write_atom': ('a24', 'sp'),
    'write_nil': (None, 'sp'), 'write_variable': (None, None),
    # U2 (2026-11-26): try_me_else's label, an A-stage address
    # calculation (nano-code DFF 1): MDR1 = the label's absolute address,
    # pc + 2 + c16 as pimm.py's i_try_me_else.  OURS (the A stage).
    'try_me_else': ('label', None),
    # read_variable: the structure element's address, R02 (sp), in MAR1,
    # as write_value's; 34a0 reads [MAR1] itself.  OURS, with support
    # (ref/pu/README.md "U2"): OS1F 6 is source (6), the structure
    # pointer, in the thesis's numbered list of S-stage set-up sources
    # (printed p.128), whose (4) WR fits OS1F 4 in every ODPF 1 entry run;
    # not fitted (read_atom has OS1F 5).  DFF 2's fetch is not used on
    # the path run: 34a0 overwrites MDR1 before anything reads it.
    # EXECUTED in append (read_variable 3 and 4 match pimm.py).
    'read_variable': (None, 'sp'),
    # U3d (2026-11-28): read_variable_without_deref x (entry 345a, the
    # compiled stream program's consumer and producer, cells 28-29): the
    # element's address R02 in MAR1, as read_variable.  OURS (pimm.py's
    # i_read_variable_without_deref: read_variable's data movement), with
    # support: 345a reads R02 and fetches [MAR1] itself, as read_variable's
    # 34a0 does.  Injection 'rvwd_form_arg': MAR1 := R10 + x instead.
    'read_variable_without_deref': (None, 'sp'),
    # the tag-test entries (entries with a tag immediate): the S stage
    # below.  (form, the operand register's field)
    'switch_on_non_list': ('s_tag', 'x'),
    'get_atom': ('s_tag', 'op'),
    # U2 (2026-11-27, third session): get_bound_value x, y (entry 3880,
    # ODPF 4, tag immediate UNDF, like get_atom): the S-stage test on
    # x, and MDR2 := r[y], the bound value (S_CONST).  OURS from pimm.py's
    # i_get_bound_value (unify(reg[x], reg[y])); support: its OS1F is 3,
    # and the thesis's list of set-up sources (printed p.128) numbers (3)
    # the RF entry named by r0-r3 (not fitted: get_atom has OS1F 1).
    # 3880 writes MDR2 into the variable cell (MAR1) and ends, as
    # 3800-3801 do for get_atom with the stamp.
    'get_bound_value': ('s_tag', 'x'),
    # U2 (2026-11-27, sixth session): wait_nil x (entry 3980, ODPF 6, tag
    # immediate ATOMo): the S-stage test on x, pimm.py's i_wait_nil
    # (g_word(x)).  OURS (the operand field, pimm.py's reading).
    'wait_nil': ('s_tag', 'x'),
    # U3d (2026-11-28): wait_atom a (entry 3960, ODPF 6, tag immediate
    # ATOMo; the opcode byte 80 | register, the low 24 bits the atom, as
    # get_atom's c0 | register): the S-stage test on the register the
    # opcode names, and MDR2 := the atom (S_CONST 'a24', as get_atom).
    # OURS (pimm.py's i_wait_atom reading), with support: 3960 forms
    # MDR1 - MDR2, the operand against the constant, before its branch.
    # Injection 'wait_atom_own' (MDR2 the operand, S_MDR2_OWN's reading).
    'wait_atom': ('s_tag', 'op'),
    # U3d: get_nil x (entry 3820, ODPF 6, tag immediate UNDF): the S-stage
    # test on x, as get_value's; 3820 makes MDR2 := nil itself and 3821
    # binds the cell (MAR1, S_ENTRY).  OURS (pimm.py's i_get_nil:
    # unify(reg[x], nil)), with support: rows 0-3 write {ATOMo, 0} or
    # {ATOMx, 0} through MAR1, the variable cell.  Injection
    # 'get_nil_form_y' (the y field, 0 here).
    'get_nil': ('s_tag', 'x'),
    # get_value x, y (entry 38a0, ODPF 6, tag immediate UNDF): the S-stage
    # test on x; the routine reads y itself (38a0, 38b2: MDR2 and MAR2
    # := opda, SD1F 3).  OURS (pimm.py's i_get_value unify(reg[x],
    # reg[y])), with support: row 0 (x unbound) loads A[y] to bind it with.
    'get_value': ('s_tag', 'x'),
    # U2 (2026-11-27, third session): the ODPF 3 start (ODPF3_START
    # below).  The operand is y, dereferenced (pimm.py's
    # i_put_reused_structure: deref(reg[y]), the result to reg[x]): OURS;
    # the side case put_reused_structure 3,0,2 in u2_append.py tells y
    # from x (31ec writes opd9, the x field).
    'put_reused_structure': ('s_odpf3', 'y'),
    # U2 (2026-11-27, fifth session): execute's label, the absolute code
    # address pc + 2 + c16 as pimm.py's i_execute, in MDR2 (no tag).  OURS
    # (the A stage's address calculation), with support: the entry's
    # nano-code is OS1F 2, the thesis's (2) "an operand field of the
    # instruction" (printed p.128), and ODSF 2, the destination read as
    # MDR2 for collect_list (above); the held words then use MDR2 as the
    # code address: 4cc2 R04 := {COD, MDR2}, 4ccf MAR1, R04 := {COD,
    # MDR2}, 4cd3 W10 := {COD, MDR2}.  Only ODSF 2 is run (raises
    # otherwise).  Injection 'execute_mdr1' (the label in MDR1).
    'execute': ('label_mdr2', None),
    # proceed (entry 216c; nano-code ODPF 1, EMO1 0, ODSF 1): no operand
    # (pimm.py's i_proceed takes none); NANO_ODPF1 puts R10, the finished
    # goal's record, in MAR1, which 216c-216d push on the R1b list.  OURS
    # (no operand set-up), U2 seventh session: it moves append's last stop
    # from "no set-up form" into the held routine, at 216c's read of R1b
    # (the goal-record free list, never set: scheduler state the harness
    # does not hold; ref/pu/README.md "Next, for U2").
    'proceed': (None, None),
    # U3 (2026-11-27, first session): enqueue_goal n, label (entry 4c00;
    # nano-code DFF 1, ODPF 1, EMO1 b, ODSF 2).  INFERRED, two parts:
    # (1) the label, pc + 2 + c16 as pimm.py's i_enqueue_goal, in MDR1,
    # as try_me_else's: the four entries with DFF 1 (try_me_else,
    # enqueue_goal, _external, _with_priority) are the ones whose operand
    # is a label, and 4c00 copies MDR1 to W10 before 4c03 stamps it COD
    # for the record's cell 12; (2) the pop of the goal-record list R1b
    # (R(10 | EMO1), NANO_ODPF1) with its head in MAR2 for ODSF 2: 4c00
    # reads [MAR2] into MDR1 and 4c04 makes R1b := that MDR1 (the next
    # record) while 4c05 makes R10 := {HOOKo, old R1b}.  collect_list's
    # ODSF 2 (read, not run) was read as MDR2 (docstring); the two do not
    # agree on one destination, so ENQ_HEAD is kept apart from ODSF_MAR.
    # Injections 'enq_head_mar1', 'enq_label_mdr2'.
    'enqueue_goal': ('label', None),
    # U3 third step (2026-11-27): suspend n, label (entry 1c08; nano-code
    # DFF 0, ODPF 0, OS1F 0, ODSF 0, EMO2 7).  OURS: the label, pc + 2 +
    # c16 as pimm.py's suspend_goal (the entry the goal resumes at), in
    # MDR1, as enqueue_goal's; support: 1c08 stamps MDR1 COD into W10,
    # which 1c0c writes as the record's cell 12, the code, as enqueue_goal's
    # 4c00 / 4c03.  The nano-code does not say where the label goes (DFF
    # 0, unlike the four DFF 1 label entries): not decided.
    'suspend': ('label', None),
    # U3d second step (2026-11-28): calculate_priority_from_minimum x, y
    # (a 22:ED builtin cell, entry 1dda, nano-code ACF 5, DFF 2: neither
    # decided).  OURS: MDR1 = A[x], as put_value's y; support: 1dda tests
    # MDR1 (CNDF 9), 1ddb reads opd9 (A[y]) and tests its tag for INTo,
    # 1ddd keeps MDR1 in W12 and 1dde compares it with 310 (the range
    # check, X = 100 passes, X = 2000 takes 1def).  Run in 'prio' (u3_goals,
    # path c), stopping at 1d94.  Injection 'prio_form_off': STOP at the
    # builtin ('no set-up form').
    'calculate_priority_from_minimum': ('x', None),
}
ENQ_HEAD = {2: 'MAR2'}
LABEL_ODSF = {2: 'MDR2'}    # 'label_mdr2': ODSF -> register (an injection changes it)
# execute's MDR1 after the S stage: STALE (OURS; U2 eighth session, in
# setup()).  The injection 'execute_mdr1_carried' keeps the previous
# instruction's MDR1 instead.
EXECUTE_MDR1_STALE = True
EXECUTE_MDR1_EMO1 = True     # U3: MDR1 := R(10 | EMO1) (in setup())
# Entries whose constant operand is the low 8 bits (format r_r_c8,
# kl1_encoding.md): pu.RULES['sc2f1_ir'] raises where c8 and c16 differ.
IR_C8 = ('put_reused_structure',)

# The ODPF 3 start (INFERRED, U2 2026-11-27, third session).  Thesis
# printed p.129: the nano-code field ODPF controls how the start address
# is generated, its low bits modified by conditions, among them the tag
# test of section 3.3.4; printed p.136 gives the combination for add:
# "if (data.tag==int) start(for_int) else start(for_others)", data the
# dereferenced operand; printed p.133 the 2-bit code of a dereference
# set-up (equal to the immediate / other / ref, with the MRB for KL1) in
# TDAR bits 3-2.  Read here as: for an ODPF 3 entry with a tag immediate
# (EMO2), start = entry | code << 2, code 0 when the dereferenced
# operand's tag equals the immediate (MRB ignored, as pu.DEREF_SETUP),
# 1 otherwise; the dereference leaves no REF, so codes 2 and 3 do not
# arise (raise).  Static evidence (scratch census of the decode table):
# 25 entries have ODPF 3, 19 of them with a tag immediate.  Of those 19,
# 18 have INTo, and 14 of them reach the failure exit (XR := R11, R04 :=
# XR: try_me_else's alternative, the U2 rule for R11), p.136's
# for_others, from entry + 4: the 9 compare / arithmetic entries
# (less_than .. modulo) at entry + 4 itself, with entry + 8 the next
# entry (no third row), and shift_left .. exclusive_or after further
# tests (3b23); the 4 *_extended entries call 0d87 at entry + 4.  The
# 19th, put_reused_structure (immediate 1e, the vector with
# a descriptor): entry 31e8 reads [MAR1] and tests for VDESC (the
# descriptor), 31ec is the other row.  EXECUTED at 31ec (append's list).
# Injections: 'odpf3_entry' (start at the entry whatever the tag),
# 'odpf3_bits10' (the code in bits 1-0).
ODPF3_SHIFT = 2
# S_TDAR_ODPF3 (U3d, 2026-11-28; INFERRED): S_TDAR's multiway set-up holds
# for the ODPF 3 start too: TDAR := the TGT byte of the dereferenced
# operand's tag, column 7 - TDPF.  Decided at put_reused_structure on a
# SHARED list (the stream program's consumer, A0 = {LISTx, cell}: 31ec's
# CNDF 7 EM1 29, the MRB, keeps 31ed from ending, so the structure is not
# reused): 31ee calls 31a1, whose case_branch (JMPF 2, base 31a0) reads
# TDAR.  put_reused_structure's TDPF is 4, column 3, S_TDAR's column for
# switch_on_non_vector; its bytes give 31a0's rows by size: LISTo/x 4 ->
# 31a4 (MAR1 := R1a, the two-cell list, jump 332b), VECT1 8 -> 31a8 (R19,
# one cell), VECT2 a -> 31aa (R1a), VECT3 c -> 31ac, VECT4 e -> 31ae
# (3334, the four-cell allocator), VECT0 6 -> 31a6 (6c21, an error): the
# structure's size class.  Injection 'tdar_odpf3_off' (no TDAR: raises
# at 31a1).
S_TDAR_ODPF3 = True
# get_atom's constant: the atom number, the instruction's low 24 bits, put
# in MDR2 by the S stage with no tag (the routine stamps it: 3800 ATOMo,
# 3804 ATOMx).  OURS: that the S stage leaves the constant in MDR2.
S_CONST = {'get_atom': 'a24', 'get_bound_value': 'y', 'wait_atom': 'a24'}

# The S stage's tag mechanisms (Nakashima's thesis pp.134-137, DOCUMENTED:
# (1) the tag of an operand compared with the entry's tag immediate into
# COND, the p.135 box "MDR1 = data, COND = (A[i].tag==list)"; (2) the
# multiway set-up by the memory operand's tag (TGT into TDAR); (3) the
# start address changed by that comparison, "if (data.tag==list)
# start(for_list) else start(for_others)", the operand dereferenced
# first, p.137 "repeats the fetch until the tag is not ref").  How (3)
# changes the address is not documented:
#
#   S_ENTRY (INFERRED): when the dereferenced operand's tag equals the
#   decode entry's tag immediate (the whole tag, MRB included), the
#   routine starts at the entry itself, with COND = (the operand's OWN
#   tag, before dereference, == the immediate), as in the p.135 box, and
#   MAR1 = the address of the last cell the dereference read.  Decided
#   at 3800-3801 (get_atom on an unbound variable, immediate UNDF: the
#   cell must be bound to {ATOMo, atom}, and 3800 is the word that stamps
#   ATOMo on the constant; entering at entry + 1 binds it untagged: the
#   injection 's_imm_plus1' FAILs) and run at 3300-3301
#   (switch_on_non_list on a list held directly in A0: COND true, the
#   conditional jump to 3305 not taken, 3301 R02 <- MDR1, end: two
#   words, where the thesis's Table 3-6 gives get_list one step, an open
#   tension; entry + 1 gives one word and the same registers there).
#   Discriminated: the start (s_imm_plus1) and MAR1 (s_no_mar1: STOP at
#   3801).  The COND part: s_cond_true changes nothing, but s_cond_false
#   (sixth session) FAILs append at instruction 1 (3300's jump, a cell
#   written at 1ea), so the COND is pinned by its false side.  (Since
#   the seventh session it STOPs at 3309 instead, the write through
#   MAR1, which is STALE for an operand held directly: S_MAR1_DIRECT_
#   STALE.  The old FAIL wrote through the previous instruction's MAR1.)  Joint with S_CONST (OURS) above.  Read, not run: through a REF (COND false) 3300 jumps to
#   3305-3309, which put the variable cell the list was reached through
#   on the R19 list.
#   Any other tag takes the multiway set-up (2): for ODPF 6 entries,
#   S_OTHER_ROW below (sixth session); other chains and other ODPF still
#   raise.
S_ENTRY = 0             # the injections: 's_imm_plus1' 1; 's_imm_row' 'row'

# U2, 2026-11-27, sixth session: the tag test's other side, for ODPF 6
# entries (switch_on_non_list, switch_on_non_integer / _atom, wait_*,
# get_value):
#
#   S_OTHER_ROW (INFERRED): when the dereferenced operand's tag is NOT
#   the immediate's (MRB ignored), the routine starts at entry | (4 |
#   chain) << 2, chain 0 for an operand held directly (no pointer
#   followed, MRB off); any other chain code raises.  So the 32 words
#   behind such an entry are 8 rows of 4: rows 0-3 the immediate's tag,
#   rows 4-7 the others.  Static: switch_on_non_list (3300) rows 4-7
#   (3310, 3314, 3318, 331c) all compute the label (XR := R04 + the IR
#   field, jump 2447), and switch_on_non_integer (32e0) / _atom (32e2),
#   two words apart, interleave the same 8 rows (32f0 .. 32fe: the label
#   again in rows 4-7; rows 0-3 put x := the value, mark or free); the
#   row an operand held directly with its tag's MRB off takes on the
#   immediate's side is the entry itself (S_ENTRY, executed), so chain
#   0 is that operand.  The thesis (printed pp.134-137, DOCUMENTED) has
#   the start address changed by the tag test after the dereference and
#   the dereference report two chain bits to E (Fig. 3-23), which fits a
#   2-bit chain code beside the match bit; which code each chain gets
#   is read from rows 1-3 only (row 1 a marked list, row 2 a freed
#   variable cell, row 3 both, then 247b), not run.  Rows 5-7 differ
#   from row 4 in CNDF only.  The rejected reading, TGT column TDPF by
#   the dereferenced tag (the injection 's_imm_row'), sends LISTo to
#   row 2.  Executed at 3310 (nil).  Injection 'other_row_entry' (the
#   entry for every tag: since the seventh session a STOP at 3309, MAR1
#   STALE, where it FAILed at 12).
#
#   S_TDAR (INFERRED): the S stage's multiway set-up (thesis printed
#   p.134 mechanism (2), "a multiway-branch set-up by the memory
#   operand's tag", DOCUMENTED; the nano-code field TDPF, Fig. 3-22,
#   "set-up of the E-stage tag multiway branch") loads TDAR with the TGT
#   byte of the dereferenced operand's tag from column 7 - TDPF of the
#   KL1 table at 5300, for a later case_branch (pu RULES['jmpf2_case']).
#   The column is read from the shapes of the tables the entries'
#   first case_branch reaches (scratch dumps of image 2): TDPF 4
#   (switch_on_non_vector, 2401 -> 2400) column 3, whose VECT1..VECT6
#   bytes 8..18 land on the six rows 2408-2412 that differ only in EM1
#   1..6, and whose 26 (UNDF, HOOKs) lands on 241a's jump to 24b1;
#   TDPF 2 (write_marked_value 323c -> 3240, put_marked_value 327c ->
#   3280) column 5, byte for byte (REFo 0, REFx 1, INTo/ATOMo/VECT0o/FLTo
#   2, INTx 4 ... VECT0x 7 re-stamped o at 3244-3247, UNDF.. 18 {REFx,
#   XR}); TDPF 0 (switch_on_constant 2425 -> 2420, hash_on_constant 2437
#   -> 2430, switch_on_non_list's label branch 2447 -> 2440) column 7:
#   row 0 the constants (2420 starts the switch on them), 2 the
#   structures, 4 UNDF, 6 the hooks, 8 EXREF, 10 MGHOK/EXMRF (all four
#   jump to 24b1, the suspension path), 12 REF and the rest.  TDPF 1
#   (column 6) is not met.  Executed at 2447 (nil, ATOMo: column 7
#   byte 0, row 2440).  Injections 'tdar_col_tdpf' (column = TDPF),
#   'tdar_col6' (column 6: nil is 0 there too; the side case on VECT0o
#   tells them apart).
#
#   S_MDR2_OWN (OURS, with support): for these entries the S stage
#   leaves the operand as it was before the dereference in MDR2 (ODSF 2
#   is MDR2, as LABEL_ODSF).  Support, read not run: the free-a-cell
#   rows put MDR2 on the R19 list (3309 R19 := MDR2, [MAR1] := the old
#   head), so MDR2 is the REF to the cell the dereference went through;
#   3310's CNDF 9 tests it for REFo.  Executed at 3310 (COND false for
#   nil held directly).
#
#   S_REPORTS (OURS): the chain reports (pu.FLAG_CONDS 'MRP', 'COL') for
#   an operand held directly: COL false; MRP not given (raises if
#   formed).  Injection 'col_true'.
S_OTHER_ROW = 4         # the match bit's row offset; None (injection): the entry
TDAR_COLUMN = lambda tdpf: 7 - tdpf     # noqa: E731 (an injection replaces it)
S_MDR2_OWN = True
S_REPORTS_DIRECT = {'COL': False}
# U2, 2026-11-27, seventh session: for these entries, an operand held
# directly (no pointer followed) leaves MAR1 with a value the harness
# does not know: pu.STALE (OURS).  The S stage loads MAR1 with the last
# cell the dereference read (S_ENTRY); with none read, what MAR1 holds is
# not documented.  STALE may be copied (get_value's 0c0c W1d := MAR1,
# 0c0d XR := W1d) but an address, a write or a test with it raises, so a
# run that ends shows the value does not matter there.  Injection
# 's_mar1_kept' (MAR1 keeps the previous instruction's value, the old
# behaviour).
S_MAR1_DIRECT_STALE = True
# U3, third step (2026-11-27): the other side of the tag test reached
# THROUGH pointers (an operand that is a REF to a variable cell: the
# suspension's first instruction, switch_on_non_list on an unbound
# argument).
#
#   S_CHAIN_ROW (INFERRED; the two reports DOCUMENTED): the row is 4 |
#   code, code = (SRP false) | (COL true) << 1, where the S stage's two
#   dereference reports are those of the thesis (printed p.138, Fig. 3-23,
#   read from the page image 2026-11-27): SRP "every MRB in the chain is
#   off" (the pointers followed and the word reached), COL "the first two
#   pointers' MRBs are off" (the figure's four cases: ref o -> list o
#   yes/yes; list o held directly yes/no; ref o -> ref o -> list x no/yes;
#   ref x -> list o no/no).  The code fits the match side's four rows of
#   switch_on_non_list as read (3300 row 0: held directly, SRP yes COL no;
#   3304 row 1: re-stamps the list LISTx, SRP no; 3308 row 2: frees the
#   variable cell through 3305-3309, COL yes; 330c row 3: both, then
#   247b), not run there: the match side keeps S_ENTRY.  The reports go
#   to the flags MRP (rassy's name for SRP: INFERRED) and COL.  MAR1 is
#   the last cell the dereference read (as S_ENTRY), MDR1 what it read,
#   MDR2 the operand as it was (S_MDR2_OWN).  Injections 'chain_row_srp'
#   (code from SRP true), 'chain_row_off' (raises again).
S_CHAIN_ROW = True
#   S_CHAIN_MAR1_PTR (INFERRED): on these rows MAR1 holds the last pointer
#   the dereference followed, its tag included ({REFx, cell} for a shared
#   variable), not the bare address S_ENTRY gives (tag 0).  Decided at
#   24b1 (switch_on_non_list's suspension path: x := MAR1, and pimm.py
#   leaves the register as it is: the REF to the variable) and 3a34 (MDR1
#   := MAR1, kept in R18, rassy 'sst', the suspension stack's cache: a
#   pointer to the variable, as VPIM's s_PushSuspendStack takes a REF).
#   Injection 'chain_mar1_bare' (the bare address): FAILs at the
#   instruction (A0 rewritten untagged).
S_CHAIN_MAR1_PTR = True
#   S_CHAIN_MATCH (U3d, 2026-11-28; INFERRED): on the immediate's side,
#   an ODPF 6 operand reached through pointers with an MRB on in the chain
#   (SRP false) takes row 1 | COL << 1, the chain code of S_CHAIN_ROW, not
#   the entry.  Decided at the stream program's resumed consumer:
#   switch_on_non_list on {REFx, S}, S bound to a list, takes 3304 (A0 :=
#   {LISTx, cell}: the list re-stamped shared, then 3301), where the entry
#   (3300, COND false) jumps to 3305-3309 and puts S's cell, which the
#   other consumer still holds, on the R19 free list.  With SRP true, for
#   switch_on_non_list and wait_nil the two readings agree: row 0 with
#   COND false and row 2 both free the one cell the single reference
#   reached (3300 -> 3305 / 3308 -> 3305; 3981 frees MAR1, 3988-3989 MAR2
#   = the same cell), so S_ENTRY stands there.  OPEN TENSION: for get_nil
#   (3828), get_bound_value (3888) and get_value (38a8) row 2 first calls
#   0cf1 / 0cf0 (a pointer cell pushed on R19), where the entry's row 0
#   does not; the stream run takes row 0 through a REFo at get_nil
#   (instructions 32, 49, 66) and get_bound_value (41, 58), and pimm.py
#   frees nothing: NOT discriminated.
#   Read, not run: row 1 of get_nil (3824, {ATOMx, 0}) and wait_nil (3984).
#   Injection 'chain_match_off' (the entry, as before).
S_CHAIN_MATCH = True
#   S_CHAIN_ODPF4 (U3d, 2026-11-28; INFERRED): the same rows for an
#   ODPF 4 entry reached through pointers on another tag (get_bound_value
#   x, y with x a REFx to a hooked variable: the compiled stream
#   program's producer binding the stream two consumers wait on).  The
#   32 words behind 3880 are 8 rows of 4 as behind 3300: rows 0-3 bind
#   the variable ([MAR1] := MDR2; rows 2-3 first push the cell on R19
#   through 0cf1-0cf9, as switch_on_non_list's row 2 frees it; rows 1 and
#   3 go on to 0c08), rows 4-7 hand the pair to the unifier (0c0a: MDR2
#   := W18, jump 0c60), each after its own call (0cd0, 0cd4, 0cda,
#   0cdc).  Injection 'chain_odpf4_off' (raises again).
S_CHAIN_ODPF4 = True
#   S_TDAR_ODPF4 (U3d second step, 2026-11-28; INFERRED): an ODPF 4 entry
#   reached through pointers loads TDAR as S_TDAR does (column 7 - TDPF,
#   the dereferenced tag), for pu.RULES['jmpf3_s_tdar'].  Executed at
#   wait_atom's 3979 (TDPF 1, column 6, UNDF -> 16, 3950 -> 3a38).
#   Injection 'tdar_odpf4_off' (no TDAR: STOP at 3979).
S_TDAR_ODPF4 = True
# The injection 'chain_row_srp' (CHAIN_SRP_TRUE: the row from SRP true,
# row 4 = 3310 for a REFx chain) changes nothing on the suspend program's
# path: 3310's CNDF 9 (MDR2, the operand {REFx, X}, a REFo?) is false as
# 3314's CNDF 3 with no ALU (pu.RULES['cnd_noalu_poison'] 'zero').  Since
# U3d it STOPs the stream program at 24 (get_bound_value row 4 for 5,
# 0c74): discriminated there.
CHAIN_SRP_TRUE = False


def last_pointer(mem, own):
    """The last pointer the dereference followed (tag and address): the
    word whose address is the cell reached."""
    w = own
    while mem.get(w[1], (0, 0))[0] & ~1 == 0x06:
        w = mem[w[1]]
    return w


def chain_reports(mem, own, data):
    """The S stage's two dereference reports (Fig. 3-23) for the operand
    own, dereferenced to data: (SRP, COL)."""
    ptrs = []
    w = own
    while w[0] & ~1 == 0x06:
        ptrs.append(w)
        w = mem[w[1]] if len(ptrs) < 64 else (0, 0)
    words = ptrs + [data]
    srp = not any(x[0] & 1 for x in words)
    col = bool(ptrs) and not any(x[0] & 1 for x in words[:2])
    return srp, col


class SStageUnknown(KeyError):
    """An S-stage set-up this stand-in does not model."""


def deref(pu, w):
    """The S stage's dereference (thesis p.137): follow REF cells until
    the tag is not a REF.  Returns (data, address of the last cell read
    or None).  OURS as a mechanism stand-in (DOCUMENTED that it is done
    in the S stage, not how its result is laid out in the registers)."""
    last = None
    while w[0] & ~1 == 0x06:
        last = w[1]
        if last not in pu.mem:
            raise SStageUnknown('S-stage dereference of %x, never written' % last)
        w = pu.mem[last]
    return w, last


def setup(pu, name):
    """Load the E-stage registers for the instruction pu.ir; return the
    start microaddress."""
    fw = pu.fw
    pu.tdar = None          # a multiway set-up never outlives its instruction
    for k in ('MRP', 'COL'):    # nor do the S stage's chain reports (S_REPORTS)
        pu.flags.pop(k, None)
    idx, start, imm = fw.kl1_entries()[name]
    nc = nano(fw, idx)
    form = FORMS.get(base(name))
    if form is None:
        raise KeyError('no set-up form for %s' % name)
    t, v = pu.ir
    mdr, mar = form
    pu.ir_c8 = base(name) in IR_C8
    if mdr == 's_odpf3':
        if nc['ODPF'] != 3 or imm is None:
            raise SStageUnknown('ODPF 3 start for %s: ODPF %d, immediate %s'
                                % (name, nc['ODPF'], imm))
        data, last = deref(pu, pu.an[pu.ir_field(mar)])
        pu.wr[mekbn.MDR1] = data
        if last is not None:
            pu.wr[mekbn.MAR1] = (0, last)
        code = 0 if data[0] & ~1 == imm & ~1 else 1
        if S_TDAR_ODPF3:
            # S_TDAR_ODPF3 (U3d, below): TDAR from the TGT, as ODPF 6
            pu.tdar = ('S', pu.tgt[TDAR_COLUMN(nc['TDPF'])][data[0] & 63])
        if ODPF3_SHIFT is None:         # injection: the entry whatever the tag
            return start
        return start | code << ODPF3_SHIFT
    if mdr == 'label':
        pu.wr[mekbn.MDR1] = (0, (pu.pc + 2 + sx16(v)) & 0xffffffff)
        if nc['ODPF'] == 1 and NANO_ODPF1:
            # enqueue_goal (U3): the pop of R(10 | EMO1) = R1b, the head
            # into ENQ_HEAD (ODSF 2), as NANO_ODPF1
            reg = {'MAR1': mekbn.MAR1, 'MAR2': mekbn.MAR2,
                   'MDR2': mekbn.MDR2}.get(ENQ_HEAD.get(nc['ODSF']))
            if reg is None:
                raise SStageUnknown('label set-up with a pop, ODSF %d: not run here' % nc['ODSF'])
            pu.wr[reg] = (0, pu.r[0x10 | nc['EMO1']][1])
        return start
    if mdr == 'label_mdr2':
        reg = {'MDR1': mekbn.MDR1, 'MDR2': mekbn.MDR2}.get(LABEL_ODSF.get(nc['ODSF']))
        if reg is None:
            raise SStageUnknown('label set-up for %s with ODSF %d: not run here'
                                % (name, nc['ODSF']))
        pu.wr[reg] = (0, (pu.pc + 2 + sx16(v)) & 0xffffffff)
        if EXECUTE_MDR1_EMO1 and reg == mekbn.MDR2:
            # U3 (2026-11-27): the S stage loads R(10 | EMO1) into MDR1, as
            # NANO_ODPF1 reads R(10 | EMO1) for a pop and pu.RULES
            # ['wsel_d_em1'] names R(10 | EM1).  INFERRED: execute's EMO1
            # is 5, rassy's crr = R15, and 4cc0 then makes R15 := R15 - 1
            # (MDR1 - EM2), as proceed's 216d and enqueue_goal's 4c02 do.
            # A harness that does not hold R15 (u2_append) gets STALE, the
            # old behaviour.  Injection 'execute_mdr1_stale' (STALE always).
            pu.wr[mekbn.MDR1] = pu.r.get(0x10 | nc['EMO1'], _pu.STALE)
        elif EXECUTE_MDR1_STALE and reg == mekbn.MDR2:
            # what the S stage leaves in MDR1: STALE (before U3), so
            # 4cc0's R15 := MDR1 - EM2 (RULES['alu_sources']) is STALE too.
            pu.wr[mekbn.MDR1] = _pu.STALE
        return start
    if mdr == 's_tag':
        if imm is None:
            raise SStageUnknown('S-stage tag set-up for %s: no tag immediate' % name)
        own = pu.an[pu.ir_field(mar)]
        data, last = deref(pu, own)
        pu.wr[mekbn.MDR1] = data
        if last is not None:
            pu.wr[mekbn.MAR1] = (0, last)
        elif S_MAR1_DIRECT_STALE and nc['ODPF'] == 6:
            pu.wr[mekbn.MAR1] = _pu.STALE
        if base(name) in S_CONST:
            src = S_CONST[base(name)]
            if src == 'a24':
                pu.wr[mekbn.MDR2] = (0, v & 0xffffff)
            else:
                pu.wr[mekbn.MDR2] = pu.an[pu.ir_field(src)]
        odpf6 = nc['ODPF'] == 6
        if odpf6:
            # S_TDAR, S_MDR2_OWN, S_REPORTS (sixth session, above)
            pu.tdar = ('S', pu.tgt[TDAR_COLUMN(nc['TDPF'])][data[0] & 63])
            if S_MDR2_OWN and base(name) not in S_CONST:
                pu.wr[mekbn.MDR2] = own
            if last is None:
                pu.flags.update(S_REPORTS_DIRECT)
        if S_ENTRY == 'row':    # the injection: every tag takes a TGT row
            return start | pu.tgt[nc['TDPF']][data[0] & 63] << 2
        if data[0] == imm:
            pu.cond, pu.cond_cycle = own[0] == imm, 'S'
            if odpf6 and S_CHAIN_MATCH and last is not None and S_ENTRY == 0:
                # S_CHAIN_MATCH (U3d, below): a chain with an MRB on
                srp, col = chain_reports(pu.mem, own, data)
                if not srp:
                    pu.flags.update(MRP=srp, COL=col)
                    return start | (1 | (2 if col else 0)) << 2
            return start + S_ENTRY
        if odpf6 and data[0] & ~1 != imm & ~1 and last is None and not data[0] & 1:
            # S_OTHER_ROW: another tag, held directly, MRB off: chain 0
            pu.cond, pu.cond_cycle = own[0] == imm, 'S'
            if S_OTHER_ROW is None:
                return start
            return start | S_OTHER_ROW << 2
        if (odpf6 or nc['ODPF'] == 4 and S_CHAIN_ODPF4) and S_CHAIN_ROW \
                and data[0] & ~1 != imm & ~1 and last is not None:
            # S_CHAIN_ROW (U3 third step, above): through pointers
            srp, col = chain_reports(pu.mem, own, data)
            if CHAIN_SRP_TRUE:          # injection 'chain_row_srp'
                srp = True
            pu.flags.update(MRP=srp, COL=col)
            if S_CHAIN_MAR1_PTR:
                pu.wr[mekbn.MAR1] = last_pointer(pu.mem, own)
            if not odpf6 and S_TDAR_ODPF4:
                pu.tdar = ('S', pu.tgt[TDAR_COLUMN(nc['TDPF'])][data[0] & 63])
            pu.cond, pu.cond_cycle = own[0] == imm, 'S'
            return start | (4 | (0 if srp else 1) | (2 if col else 0)) << 2
        raise SStageUnknown('S-stage multiway set-up: %s tag %02x, TDPF %d (row entry UNKNOWN)'
                            % (name, data[0], nc['TDPF']))
    if mdr in ('x', 'y'):
        pu.wr[mekbn.MDR1] = pu.an[pu.ir_field(mdr)]
    elif mdr:
        val = {'c16': sx16(v), 'c24': sx24(v), 'a24': v & 0xffffff}[mdr]
        pu.wr[mekbn.MDR1] = (nc['EMO2'], val & 0xffffffff)
    if mar:
        rec, sp = pu.r.get(R_REC), pu.r.get(R_SP)
        a = {'arg_x': lambda: rec[1] + pu.ir_field('x'),
             'arg_op': lambda: rec[1] + (pu.ir_field('op') & 15),
             'sp': lambda: sp[1]}[mar]()
        pu.wr[mekbn.MAR1] = (0, a & 0xffffffff)
    if nc['ODPF'] == 1 and NANO_ODPF1:
        head = pu.r[0x10 | nc['EMO1']]
        reg = {'MAR1': mekbn.MAR1, 'MAR2': mekbn.MAR2}.get(ODSF_MAR.get(nc['ODSF']))
        if reg is None:
            raise KeyError('ODPF 1 with ODSF %d: not run here' % nc['ODSF'])
        pu.wr[reg] = (0, head[1])
    return start


def dispatch(pu):
    """Decode-table dispatch from the instruction cell pu.ir, as the D
    stage does: the cell's tag picks the class (0x22 GMI = 2, 0x23 KLB = 3,
    as asm/mekbn.py kl1_entries reads the table, MEASURED in
    pseudo_pimm_microcode.md section 3), its top byte the
    opcode, and the held decode table's entry (class << 8 | opcode) the
    start address.  Returns (name, start) after the S-stage set-up.
    An empty entry or another tag raises."""
    name = decode(pu)
    return name, setup(pu, name)


def decode(pu):
    """The decode-table name of the instruction cell pu.ir (dispatch's
    D-stage half)."""
    t, v = pu.ir
    cls = {0x22: 2, 0x23: 3}.get(t)
    if cls is None:
        raise KeyError('instruction tag %02x: no KL1 decode class' % t)
    idx = cls << 8 | (v >> 24) & 255
    names = [n for n, e in pu.fw.kl1_entries().items() if e[0] == idx]
    if not names:
        raise KeyError('decode entry %03x empty' % idx)
    return names[0]
