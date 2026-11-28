#!/usr/bin/env python3
"""A microcode-level simulator of the PIM/m / PSI-III PU's E stage that
executes ICOT's held KL1 microprogram (rungs U1/U2 of
docs/pu_microcode_plan.md).

The microinstructions are image 2 of PMPSI.DIR/pimm.MEkbn, read from
docs/nonlocal/psdpim.tar.Z through asm/mekbn.py (third-party binary: it
is never copied into the repository, and neither is any dump of it).
Field positions are asm/mekbn.py's FIELDS (Nakashima Fig. 3-25); field
VALUES are the measured readings of docs/pseudo_pimm_microcode.md
sections 8-21, plus the rules in RULES below, each labelled.

What runs here is HELD: every microinstruction executed is the held
word at that microaddress, decoded generically; there is no Python per
KL1-B instruction in the E stage.  What is stood in is hardware the
microprogram does not give:

  - the D/A/R/S stages, which the decode entry's nano-code drives
    (setup.py, OURS per operand form, one nano-code rule INFERRED);
  - the condition multiplexer behind CNDF (COND_RULES, INFERRED each);
  - memory (a dict of 40-bit cells, OURS).

Anything met on an executed path whose meaning is not modelled raises
Unmodelled with the microaddress: "fail loud".

Values are (tag, value) with an 8-bit tag and a 32-bit value.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import mekbn  # noqa: E402
from mekbn import field, bit, flow  # noqa: E402
import pu_store  # noqa: E402
import pu_sysinit  # noqa: E402

M32 = 0xffffffff
# kbn.TAGS values used by name below (asm/kbn.py, from the PIMOS inspector)
INT, ATOM, LIST, REF, UNDF, VECT0 = 0x00, 0x02, 0x04, 0x06, 0x08, 0x10
VECT0x = 0x11

# Work-register numbering of SD1F / ADF / AS1F (mekbn: MEASURED).
XR, MDR1, MDR2, MAR1, MAR2 = 1, 4, 5, 6, 7
WNAME = {XR: 'XR', MDR1: 'MDR1', MDR2: 'MDR2', MAR1: 'MAR1', MAR2: 'MAR2'}


class Unmodelled(Exception):
    """A field value, table or path the simulator does not model."""

    def __init__(self, upc, what):
        Exception.__init__(self, '%04x: %s' % (upc, what))
        self.upc, self.what = upc, what


class Trap(Unmodelled):
    """Control reached the illegal / unimplemented-instruction trap 6c21
    (upper syspsi, resident under the KL1 image; 244 image-2 call sites;
    CORROBORATED, docs/pu_microcode_inference.md section 7 item 4).  A
    trap is an outcome, not a gap in the model."""


TRAP_ILLEGAL = 0x6c21
# rassy's ccf/2 table (RULES['ccf_rassy'], HELD-SOURCE): CCF -> (kind,
# MAR, MDR, step) for the memory operations modelled; the other names
# raise where a strobe bit is set.
CCF_RASSY = {0x08: ('read', 6, 4, False), 0x09: ('read', 7, 4, False),
             0x0a: ('read', 6, 5, False), 0x0b: ('read', 7, 5, False),
             0x0c: ('read', 6, 4, True), 0x0d: ('read', 7, 5, True),
             0x10: ('write', 6, 4, False), 0x11: ('write', 7, 4, False),
             0x12: ('write', 6, 5, False), 0x13: ('write', 7, 5, False),
             0x14: ('write', 6, 4, True), 0x15: ('write', 7, 5, True),
             0x16: ('write', 6, 4, True), 0x17: ('write', 7, 5, True),    # 16, 17 write_stack
             # 0f 'cancel': no memory operation (INFERRED: the name only;
             # executed at 3494, read_variable's end, where the bit reading's
             # read ++ mar2 mdr2 is not used either way: NOT discriminated)
             0x0f: ("cancel", 7, 5, False),
             # 04 'wait': no memory operation, nothing changed (INFERRED: the
             # name; this simulator has no memory latency to wait out).
             # 7 words of image 2 (201f, 202f, 215f, 2167, 408b, 4667, 466a);
             # executed at 202f (start: R10 := MDR1 after 202d's pop, 3349).
             # Injection 'ccf_wait_raise' (u3_goals.py): STOP at 202f.
             0x04: ('wait', 6, 4, False)}
CCF_NAMES = {0x04: 'wait', 0x05: 'undo', 0x06: 'reset_TRB', 0x07: 'read_TRB_top mdr1',
             0x0e: 'set_misc_command mdr1', 0x18: 'unify_write mar1 mdr1',
             0x19: 'unify_write mar2 mdr1', 0x1a: 'unify_write mar1 mdr2',
             0x1b: 'unify_write mar2 mdr2', 0x1c: 'write_byte mar1 mdr1',
             0x1d: 'exec_misc_read mar2 mdr2', 0x1e: 'write_hword mar1 mdr1',
             0x1f: 'exec_misc_write mar2 mdr2'}
SPECIAL_EM = 0x7fff     # S9: JMPF 1 with EM = 7fff, a special form (INFERRED, open)
TGT_KL1 = 0x5300        # sysinit's KL1 tag table, 64 tags x 8 columns
# set-up EM1 -> column by the ALU's AS1 input (the old rule): since U2's
# seventh session every EM1 30-3f is CASE_TAG_SETUP below (3a -> column 2,
# VERIFIED at 2d3e, is one of them); this table is kept for injections.
TGT_COLUMN = {}
# U2, 2026-11-27, seventh session: CNDF 7 with EM1 30-3f is rassy's
# 'case_tag_setup mdrN k' (HELD-SOURCE: cndf_others/5 keys 30-3f, pool
# slots 0106-0115, in the order mdr1 0, mdr2 0, mdr1 1, .. mdr2 7: EM1 even
# names MDR1, odd MDR2, k = (EM1 - 30) >> 1).  TDAR := the TGT byte (KL1
# table 5300) of that MDR's tag, as it stood before the word, from column
# 7 - k (INFERRED: 3a = mdr1 5 is column 2, VERIFIED at 2d3e, and
# setup.S_TDAR's 7 - TDPF).  MEASURED (scratch census, image 2, 165
# words; CCF bits 59..58 against the parity): mdr1 words 00 8, 01 69,
# 10 4, 11 22; mdr2 words 00 7, 01 0, 10 49, 11 6 (a correlation, not
# a proof of the parity: the rule does not lean on it).  Shapes met:
# 0c0c (mdr2 7, column 0 on a REFo: 0e38; REFx 0e3b; LISTx, LISTo and
# the others 0e39, 0e3a, 0e3c, all calls of the trap 6c21: the routine is
# called only for a REF); 0e38 (mdr2 2, column 5: 20 rows 0e60-0e73 for
# bytes 0..19, UNDF 18 -> 0e72); 0c0d (mdr1 1, column 6) and 0840 (mdr2
# 0, column 7).  Admitted in any word whose EM1 is free of the jump
# operand (JMPF 0, 3, 4, 6, 7, 8, a, b, e: all met in the census);
# JMPF 1 / 5 / 9 / d words raise.  Injection 'cts_as1' (CTS_SOURCE
# 'as1'): the tag taken from the ALU's AS1 input, as the old 3a rule did
# (0c0c's AS1 is MAR1).
CASE_TAG_SETUP = True
CTS_SOURCE = 'mdr'
CTS_MDR = {0: MDR1, 1: MDR2}            # EM1 parity -> register (injection 'cts_mdr_swapped')
CTS_COLUMN = lambda k: 7 - k            # noqa: E731 (injection 'cts_col_k')
# The dereference multiway set-up (thesis printed p.133, section 3.3.4.1,
# DOCUMENTED: "the tag of the AS1 bus is ref, equal to an immediate the
# microinstruction gives, or other: a 2-bit code into TDAR bits 3-2"; for
# KL1 a four-way form that also tells the MRB of a ref).  CNDF 7 with
# these EM1 values sets TDAR := code << 2 from the AS1 input's tag;
# 'case_branch' then ORs it into the base.  INFERRED (U2, 2026-11-27),
# decided at 34a1 (read_variable; the oracle wants row 3494, x := the
# element, for an atom).  Evidence that 2d is not a TGT column: the two
# bases 3490 (34a2, after 2d) and 3492 (343a, after 2f) interleave 2-word
# rows in 3490-349f, and no column of 5300 sends ATOMo to 3494 without
# sending some tag to a zero word or a row's second word (column 0:
# LISTx -> 3491, REFx -> 3493); the other 2d site (41b6 -> 41b0) has
# 4-word rows at 41b0/41b4/41b8/41bc.  The codes, read from the rows of
# 3490-349f (EXECUTED: only 'other'):
#   1 other           3494: x := the element (MAR1), R02 + 1 (MCF 20)
#   0 tag == EM2      3490 (EM2 1e at 34a1: VECTo; 3490 stamps VECTx and
#                     tests for VDESC) -- read, not run: raises
#   2 REFo (MRB off)  3498: the cell pointed to goes on the R19 list,
#                     then the 3440 table -- read, not run: raises
#   3 REFx (MRB on)   349c: follow without freeing, the 3460 table --
#                     read, not run: raises
DEREF_SETUP = {0x2d: 4}         # EM1 -> ways; 2f (343a, read_atom..), 2a, 2b read, not run
DEREF_CODE = {'imm': 0, 'other': 1, 'refo': 2, 'refx': 3}   # an injection swaps these
DEREF_SHIFT = 2                 # TDAR bits 3-2 (thesis p.133); an injection moves it
DEREF_TGT_COLUMN = None         # injection only: read the set-up as this TGT column
# CNDF 7 EM1 values that are conditions whose meaning is UNKNOWN: COND
# becomes POISON, which raises if a later word tests it.  28: 24 of its
# 54 words carry a conditional JMPF a/e (a condition, not a set-up); the
# only other word with a branch two words on (572c -> 572e) has a JMPF b
# there, not a case_branch; at 34a0 nothing tests it before read_variable
# ends.  Contributes nothing on the executed path: NOT discriminated.
COND_UNKNOWN = {0x28}
# CNDF 7 with these EM1 values: COND := a hardware flag (U2, 2026-11-27,
# fifth session; INFERRED).  Thesis printed p.144 (psi_microword.md 3):
# CNDF is the branch condition, "rare conditions selected by EM1"
# (DOCUMENTED that CNDF 7's EM1 selects a condition).  The numbering is
# rassy's condition constants in the order the class holds them
# (asm/ptfdump.py pimmutil rassy: 'cond alf_zero' .. 'cond ovf_trap',
# 40 names, then case_gc_setup / case_tag_setup), read as EM1 = the
# position: three independent checks fit it.  Position 9 is over_flow
# and 10 less, where EM1 09 (overflow) and 0a (lt) were found apart from
# rassy (pu_smt, inference doc 6.3 items 4-5); and positions 21-31
# (exsw00 .. COL) carry the very numbers rassy's own flag set/reset
# tables give the same flags (--pairs: set_exsw00 21 .. set_slit_check
# 25 .. set_COL 31, the same for reset_).  So 19 (= 25) is slit_check,
# 21 (= 33, inside the list but outside the 21-31 run) interrupt_all.
# Slit check: "asynchronous events (GC request, packet arrival, signals
# from other PEs) are latched in flag registers and polled once per
# reduction through one summary flag ... called slit-checking" (PIM/p,
# literature_gaps.md [P1] pp. 16, 19, s.5.4; PIM/m's own is TR-715 3.3,
# docs/multi_pe.md: "decoded at a slit of reductions").  execute ends a
# reduction: 4cc0 forms it, 4cc1 branches on it, 4cc2 forms
# interrupt_all, 4cc3 ends unless it holds.  The flags' values are the
# harness's (OURS, PU.flags; an unset flag raises): a single PE with no
# event pending, so both are false.  Which flag is which is NOT
# discriminated on the path run (both false).
# rassy's own decoder confirms the numbering (sixth session, HELD-SOURCE,
# no longer by position): cndf/7's arm 7 hands off to cndf_others/5
# (@3321), a hash switch on EM1 (op cd00 mask 7f, 64 keys, 0..3f); key k's
# arm takes the pool constant at slot 00dc + k for k = 00..27 (the 40
# 'cond' names: 00 alf_zero, 09 over_flow, 0a less, 19 slit_check, 1e
# MRP, 1f COL, 21 interrupt_all), keys 28 / 29 build 'cond tag0', 2c-2f
# '3_way_set_up' / '4_way_set_up' (2e / 2f with '/'), 2a / 2b
# case_gc_setup mdr1 / mdr2 (slots 0104 / 0105), and 30-3f slots
# 0106-0115: case_tag_setup mdr1 0, mdr2 0, .. mdr1 7, mdr2 7 (so 3a is
# case_tag_setup mdr1 5, the column-2 set-up VERIFIED at 2d3e: column
# 7 - k, as setup.S_TDAR; and 3f is case_tag_setup mdr2 7).  Pool slots
# are resolved from each arm's relative 'pmi 49' operand
# (scratch cndo.py; asm/ptfdump.py pimmutil rassy --list).
FLAG_CONDS = {0x19: 'slit_check', 0x21: 'interrupt_all'}
# U2, 2026-11-27, sixth session: EM1 1e and 1f are positions 30 and 31 of
# the same rassy list, 'cond MRP' and 'cond COL' (and rassy's flag
# tables number set_MRP / reset_MRP 30 and set_COL / reset_COL 31, the
# 21-31 run above).  The thesis (printed p.138, Fig. 3-23,
# psi_microword.md 3b, DOCUMENTED) has the S stage's dereference report
# two such bits to the E stage: whether every MRB in the chain was off,
# and whether the first two pointers' MRBs were off (the data can be
# collected).  So 1e / 1f are the S stage's chain reports, formed into
# COND like the other flags.  INFERRED (the name HELD-SOURCE, rassy's key; that they
# are the Fig. 3-23 reports).  Their values are the S stage's
# (setup.py S_REPORTS, OURS): for an operand held directly, no pointer
# followed, COL is false (nothing to collect); MRP is not given (raises).
# Executed at 2440 (switch_on_non_list on nil: CNDF 7 EM1 1f, tested by
# 2461's JMPF e).
FLAG_CONDS.update({0x1e: 'MRP', 0x1f: 'COL'})
# U2, 2026-11-27, seventh session: EM1 10-12 are 'cond sw00' .. 'sw02'
# (positions 16-18 of the same list, HELD-SOURCE), software switches the
# microprogram itself sets and resets with MCF (MCF_FLAG_OPS below).
# Executed at 0864 (get_value: the unifier's binding of an unbound
# variable to an atomic value forms sw01; 09d0 ends when it is clear and
# otherwise 09d1 writes the value again with its MRB on).  sw01 is set by
# the dereference rows that follow a REF with its MRB on (0e3b, 0e61,
# 0e63: MCF 0c) and reset where the first pointer is a REFo (0e75: MCF
# 04): the variable was reached through a shared pointer.  INFERRED (the
# reading of what sw01 records); the names HELD-SOURCE.
FLAG_CONDS.update({0x10: 'sw00', 0x11: 'sw01', 0x12: 'sw02'})
# U3 second session (2026-11-27): EM1 1a is 'cond PMPF' (position 26 of
# the same list, HELD-SOURCE), a flag the firmware sets and resets itself
# (MCF_SUB_FLAGS: the entry vector's 2021 / 2022).  The name: PMP is the
# held parameter file's "Pseudo Multi-PSI" (PIMM.PARAM 'pmp_ncas', "PMP
# Network Comm. Area Size"), so PMPF reads as the Pseudo-Multi-PSI flag:
# INFERENCE.  Fits the boot's two arms at 209f-20a7: set, crr (R15) is
# read from the cell 10 + start's operand a (20a1-20a3), tested against 17
# at 20a4-20a5 (not run), a per-PE reduction limit like the Pseudo PIM/m CSP's
# "Reduction Limit" (pimmcsp next_candidate, PRINTED string); reset, crr
# is 17 (20a6-20a7).  The CSP prints "$GO/PIMos <Start Address> ... = 2000
# (Multi-PSI)" (pimmcsp csp_help_command, PRINTED): the cold start 2000,
# whose path resets PMPF at 2014.  Executed at 209f (formed) and 20a1
# (tested), and in proceed's 217c / 12e3 only under injections.
FLAG_CONDS[0x1a] = 'PMPF'
# CNDF 7 EM1 00-08: 'cond alf_zero' .. 'alf_less_zero' (positions 0-8,
# HELD-SOURCE), the ALU flags latched by MCF set_alf (MCF_NAMED 01).  The
# meaning of each latched flag against the ALU's inputs is not decided:
# COND := POISON (raises if tested), as COND_UNKNOWN.  Formed at 0841
# (EM1 05, alf_equal, in a JMPF 3 word) on 0802's latch; 0864 forms a new
# COND before anything tests it: NOT discriminated.
# U2 eighth session: alf_zero is formed from the latch (alf_cond below):
# the result was 0.  Executed at proceed's 216e (alf_zero on 216d's
# R15 - 1), tested by 216f (crr exhausted: to 217a).  Injections
# 'alf_poison' (POISON again), 'alf_zero_false'.  alf_sign and alf_equal
# stay POISON: alf_cond has their readings, but nothing run tests them
# (0841's alf_equal is overwritten at 0864).
ALF_LATCHED = ('alf_zero',)
ALF_CONDS = {0x00: 'alf_zero', 0x01: 'alf_sign', 0x02: 'alf_carry', 0x03: 'alf_overflow',
             0x04: 'alf_same_tag', 0x05: 'alf_equal', 0x06: 'alf_less', 0x07: 'alf_high',
             0x08: 'alf_less_zero'}
# MCF (bit 18) with these EM1 values: an operation of UNKNOWN meaning on
# state this simulator does not hold (a flag or counter: PSI-II's TYPF
# "counter/flag control", thesis printed p.144).  Recorded in the cycle
# record ('mcf') and nothing else; INFERRED that it touches no register
# or memory the routines run here read.  06: 75 words, 59 of them in
# words that put a freed cell on the R19 list (wait_*, switch_on_*,
# hash_on_constant, 3309) and 4 at execute's / execute_external's ends
# (4cc3, 4cd0, 4ce1, 4cef).  rassy's flag reset table numbers 6
# reset_SUSPF (a reduction-end reset would fit execute; the freeing
# words do not suggest it): not decided.  Executed at 4cc3.  07: 11
# words, all at goal or reduction boundaries: proceed (2170, 217a, 2212
# R04 := the next goal's pc), execute (4cc1), execute_external (4ce0,
# 4ced, 4cf3), suspend (1c60), merge (4040, 4079) and the boot (20a8,
# W1f := 0); rassy's reset table numbers 7 reset_CGCF.  Since U2's
# seventh session the names are HELD-SOURCE by rassy's MCF decoder
# (MCF_FLAG_OPS below: 06 reset_SUSPF, 07 reset_CGCF); what the flags
# do is still not modelled, and nothing run here reads them.  Executed at 4cc1.  (The EM bits 15-10 of
# a page-relative jump word are free of its 10-bit target, so 4cc1's
# EM1 is 07.)  Injection 'mcf_unknown_raise': raises at 4cc1.
MCF_UNKNOWN = {0x06, 0x07}
# U2, 2026-11-27, sixth session: MCF with EM1 08 is pipeline_cancel,
# position 8 of the rassy flag-control table that numbers 6 reset_SUSPF
# and 7 reset_CGCF (ptfdump.py pimmutil rassy --pairs: ... 6 reset_SUSPF,
# 7 reset_CGCF, 8 pipeline_cancel, 9 set_cc).  INFERRED (the name by
# position; HELD-SOURCE table).  Static fit: the words with MCF EM1 08
# are the ones that load R04 (rassy's pc) with a new instruction address
# (2453, 245d, 2461 R04 := XR + YR, the label branch; 31ee XR := R04
# before 31a1's R04 := XR; 2035, execute_first_predicate): a branch must
# discard the instructions the pipeline fetched after it.  This
# simulator has no pipeline (the harness's A stage takes the next
# instruction from pimm.py's order and compares R04): recorded only, as
# MCF_UNKNOWN.  Executed at 2461.  Injection 'mcf08_raise': raises.
MCF_NAMED = {0x08: 'pipeline_cancel'}
# U2, 2026-11-27, seventh session: rassy's MCF decoder, HELD-SOURCE
# (asm/ptfdump.py pimmutil rassy --list: mcf/5 @2ce4 hands the field to
# mc1/2 @355b, a 4-way switch whose key 0 calls mc2/3 @357b and whose keys
# 1, 2, 3 take pool slots 0116, 0117, 0118, '-- lc', '++ gr', '++ sr'
# (each arm's relative 'pmi 29' operand resolved as cndf_others' are,
# key 3f's landing on 0115 = case_tag_setup mdr2 7); mc2/3 is a hash
# switch on a 4-bit key: 0 nop, 1 set_alf, 2 (a sub-switch: set_cc_ovf,
# set_cc_comps, rf_unlock, deref_lock, f_jump, unlock_CPR, reset_exsw00 ..
# reset_COL), 3 / 4 / 5 reset_sw00 / 01 / 02, 6 reset_SUSPF, 7
# reset_CGCF, 8 pipeline_cancel, 9 set_cc, a (the set_ sub-switch), b / c
# / d set_sw00 / 01 / 02, e set_SUSPF, f set_CGCF).  Read as EM1 = mc1's
# key << 4 | mc2's key: INFERRED, and two rules decided before fit it on
# their own: MCF EM1 20 = '++ gr', R02 + 1 (RULES['mcf_20_sp'], decided
# from pimm.py's write_integer; rassy's second register bank names 2
# 'gr'), and EM1 10 = '-- lc' in the counted loops beside CNDF 6
# ('cond lc_one'; R03 is rassy's lc, RULES['as1f3_em2']).  So 08 is
# pipeline_cancel by this table too, and 06 / 07 (MCF_UNKNOWN) are
# reset_SUSPF / reset_CGCF (kept recorded-only: nothing run reads them).
# The sw flags are held (PU.flags) and read by FLAG_CONDS 10-12.
# Executed: 0e75 (04, reset_sw01).  Injection 'sw01_set' (0e75 sets it):
# 0864's COND true, 09d0 does not end.
MCF_FLAG_OPS = {0x03: ('sw00', False), 0x04: ('sw01', False), 0x05: ('sw02', False),
                0x0b: ('sw00', True), 0x0c: ('sw01', True), 0x0d: ('sw02', True)}
# MCF 01, set_alf: the word's ALU flags are latched for 'cond alf_*'
# (ALF_CONDS).  Executed at 0802 (an ALU input not modelled: the latch is
# POISON).
MCF_NAMED[0x01] = 'set_alf'
# U2 eighth session: rassy's set_up_mcf/3 (@cdd) hands mcf/5 the keys
# EM bits 15-14 (mc1), 13-10 (mc2) and 8-4 (a sub-key, EM2 & 1f); mc2's
# key 2 and key a are switches on the sub-key (reset_ / set_: 0 cc_ovf,
# 1 cc_comps, 2 rf_unlock / rf_lock, 3 deref_lock, 4 f_jump, ...), key e
# set_SUSPF.  HELD-SOURCE; recorded only (nothing run here reads them).
# Executed in proceed's dequeue: 2215 set_SUSPF, 2217 rf_lock, 2224
# rf_unlock, which bracket the argument loads.
MCF_NAMED[0x0e] = 'set_SUSPF'
MCF_SUB = {(0x0a, 2): 'rf_lock', (0x02, 2): 'rf_unlock'}
# U3 second session (2026-11-27): PMPF, key 26 of the same two
# sub-switches (HELD-SOURCE: ptfdump.py pimmutil rassy --pairs: under mc2
# key 2 'reset_' 21 exsw00 .. 25 slit_check, 26 PMPF, .. 31 COL; under key
# a 'set_' the same numbers).  MCF EM1 02 / 0a with EM2 & 1f = 1a resets /
# sets the flag that 'cond' position 26 reads (FLAG_CONDS 1a).  INFERRED
# that the set / reset and the condition are one flag (rassy numbers both
# lists alike).  The image's only PMPF writers (scan, image 2): 2014 and
# 2021 reset, 2022 set (the entry vector 2000-2004: 2000 -> 200b .. 2014
# reset, 2001 -> 2021 reset, 2003 -> 2022 set; no held word of either
# image branches to 2001 or 2003), 68e2 reset.  Executed: 2021 (and 2022
# in u3_goals.py's second run).  Only PMPF is admitted: the other keys
# (21 exsw00 .. 31 COL, 20ac's reset_slit_check) are not run and raise.
# Injection 'mcf_pmpf_off' (u3_goals.py): STOP at 2021.
MCF_SUB_FLAGS = {(0x02, 0x1a): ('PMPF', False), (0x0a, 0x1a): ('PMPF', True)}


class _Poison(object):
    """A value with no meaning yet: COND formed by an unknown condition,
    or a memory read of a cell never written (absent_read_poison).  Any
    use raises Unmodelled (the caller checks with is_poison)."""

    def __init__(self, name='POISON'):
        self.name = name

    def __repr__(self):
        return self.name


POISON = _Poison()
# A register value the harness does not know (OURS): a scratch register
# such as R0d at execute, whatever the routine before left there.  It may
# be copied between registers and through the ALU (the result is STALE,
# as is a COND formed from it), but testing it, writing it to memory,
# addressing with it or comparing it with pimm.py raises or FAILs.  So a
# STALE value that reaches the end of a run is shown not to matter on
# that path.  (Distinct from POISON, whose ALU use still raises at once.)
STALE = _Poison('STALE')


# An ALU result whose input source is not decided (RULES
# ['as1f3_open_unknown']): it may only feed a condition or the alf latch,
# which become POISON.
UNKNOWN = _Poison('UNKNOWN')


def is_poison(v):
    return v is POISON


def is_stale(v):
    return v is STALE


# ---------------------------------------------------------------------------
# The rules.  Each entry: the rule, its label and the evidence.  The keys
# are the names injections perturb (check_pu.py); RULES is data so that a
# rule can be switched off and the run observed.
RULES = {
    # Operand-register selects (WRBF clear): 8 = the register in the
    # opcode's low bits, 9 = x, a = y, b = z.  8/9: MEASURED by mekbn
    # (put_atom/put_integer differ in one bit, section 10).  a = y,
    # b = z: INFERRED, decided at 318f (set_variable writes its REF to
    # opda, pimm.py i_set_variable reg[y]) and 31d7 (put_variable,
    # reg[y]); b at 3a69 (add's result to opdb, pimm.py i_add reg[z]).
    'opd_fields': {8: 'op', 9: 'x', 0xa: 'y', 0xb: 'z'},
    # TGIF: 1 stamps the tag immediate on what SD1 loads, 2 on the ALU
    # result (mekbn, VERIFIED / DERIVED).  3: INFERRED, both stamps with
    # the tag taken from EM2 (thesis p.144: "EM2 can also be the DST-Bus
    # tag immediate"), decided at 3193 (write_nil: EM1 = 20, EM2 = 02,
    # and the cell written must be ATOM 0, pimm.py i_write_nil).
    'tgif3_tag': 'EM2',
    # A write with bit 59 set stores MDR2.  INFERRED (section 16 left it
    # open): decided at 31d7 (put_variable: the cell must get the UNDF
    # that 31d6 put in MDR2; MDR1 holds the link just read) and 3001
    # (collect_value: the old head stamped VECT0x is in MDR2).
    'w59_mdr2': True,
    # A write stores the MDR as it stood before its own word (mekbn
    # WRITE_SAME_WORD False; section 16, VERIFIED on new_vector).
    'write_old_mdr': True,
    # U3 (2026-11-27, first session): the memory operation is rassy's
    # CCF value table (CCF_RASSY below), not the strobe bits read one by
    # one.  HELD-SOURCE: ptfdump.py pimmutil rassy --list, ccf/2 (@1b5b),
    # a 32-key switch on CCF (62..58); keys 0, 1, 2, 4, 5, 6, f name atoms
    # (nop, wait_mdr1, wait_mdr2, wait, undo, reset_TRB, cancel), the
    # others take one pool slot each through a relative 'pmi 29' operand
    # (slot = cell + 2 + c16): 03 -> 0076 ... 0e -> 007e, 10 -> 007f ...
    # 1f -> 008e, in the pool's order ', wait_mdr1 mdr2', 'read_TRB_top
    # mdr1', 'read mar1 mdr1', 'read mar2 mdr1', 'read mar1 mdr2', 'read
    # mar2 mdr2', 'read ++ mar1 mdr1', 'read ++ mar2 mdr2',
    # 'set_misc_command mdr1', 'write mar1 mdr1' .. 'write mar2 mdr2',
    # 'write ++ mar1 mdr1', 'write ++ mar2 mdr2', 'write_stack ++ mar1
    # mdr1', 'write_stack ++ mar2 mdr2', then unify_write, write_byte,
    # exec_misc_read, write_hword, exec_misc_write.  It agrees with the
    # bit reading (61 read, 62 write, 60 step, 58 MAR2, 59 MDR2) on 08-0c
    # and 10-14 and 17, and differs on 0d (read ++ mar2 MDR2), 15 (write
    # ++ mar2 MDR2), 16 (write_stack ++ mar1 MDR1), 0e and 0f (not memory
    # reads).  Decided at enqueue_goal's 4c05 / 4c06 (CCF 15): the cells
    # 13 and 14 of the record get MDR2 = R12 and R13, loaded the word
    # before (pseudo_pimm_microcode.md section 18 had left these two
    # writes against the bit reading); proceed's 2213-2214 read them back
    # as the priority and the foster parent.  'write_stack' is stored as
    # 'write' (INFERRED: the name, not its difference, is known).  Off
    # (the injection 'ccf_bits'): the bit reading.
    'ccf_rassy': True,
    # MCF (bit 18) with EM1 = 20 steps the structure pointer R02 by one.
    # INFERRED, decided at 31c7 (write_integer: one word, MCF, EM1 20;
    # pimm.py i_write_integer _sp += 1; set_integer 3182 has neither and
    # does not move sp) and 3193 (write_nil).
    'mcf_20_sp': True,
    # Switch for COND_RULES below (CNDF 9 / b: the tag compared with EM1 /
    # EM2).  In a free-list pop the word that takes the link into the head
    # register compares its tag with ATOMo, the refill's end marker
    # (3368), and the conditional end that follows goes on to the refill
    # (3378 / 337d) when they are equal.  Decided at 31fa/31fb
    # (put_vector_1), 31d1/31d2 (put_list), 318c/318f, 31d6/31d8.
    'cnd9_link': True,
    # R06 and R07 hold zero: {ATOMo, R06} is written where nil stands
    # (section 17), {UNDF, R07} where pimm.py writes UNDF 0 (31d6).
    # INFERRED (OURS as initial state).
    'zero_regs': (0x06, 0x07),
    # JMPF bit 26 (codes b, c, e) makes a page-relative or relative jump
    # conditional; codes 3, 4, 6 jump unconditionally whatever CNDF holds,
    # and their CNDF only forms COND for a later word.  INFERRED from a
    # measurement (ref/pu/README.md "Conditions"): the word after a JMPF
    # 3/4/6 word is zero or an explicit target in 47-83% of cases with or
    # without CNDF (image 2 and syspsi alike), after a b/c/e word in
    # 3-17%; all 23 self-jumping words of image 2 are c or e, 36 of 37 of
    # syspsi (ref/pu/measure.py, pinned).  Decided at 318c (set_variable:
    # JMPF 4 CNDF b must jump over set_marked_variable's words 318d-318e
    # to 318f).  This replaces mekbn.tested() (CNDF != 0) inside the
    # simulator; under it mekbn's flow pins move (measure.py
    # 'mekbn_under_bit26': the call/return separation improves).  Which
    # way a conditional b/c/e jump goes on COND is not decided: raises.
    'bit26_cond': True,
    # The timing of a conditional JMPF b/c/e/a (does it test the COND
    # its own word forms, 'same', or the previous word's, 'prev'?) is
    # 'prev' since U2's fifth session (INFERRED; the evidence below the
    # RULES dictionary, with CJUMP_TAKEN_ON); None raises, 'same' is the
    # injection 'cjump_same'.  A conditional JMPF 1
    # (end, return, jump) tests the COND the PREVIOUS executed word
    # formed: EXECUTED for ends by pu_smt (less_than / not_less_than
    # share a first word).  A word with CNDF 0 leaves COND as it was:
    # EXECUTED at put_variable 31d6-31d8 (31d6 forms COND with CNDF b,
    # 31d7 has CNDF 0, the conditional end 31d8 tests 31d6's COND and
    # matches pimm.py in both arms, the last-cell case included).  With
    # j1_cond_prev_strict (the injection 'cond_prev_strict') a COND not
    # formed by the very previous word raises, and put_variable stops.
    'cjump_time': 'prev',
    'j1_cond_prev_strict': False,
    # A conditional JMPF 1 (EM bit 1) with EM bit 0 set is taken when
    # COND is false.  INFERRED, decided at 31fb/31d2/318f/31d8: the
    # pop's end must be taken when the link is not the end marker.  With
    # EM bit 0 clear: RULES['j1_bit0_clear_true'] below (U2, decided at
    # the return 2050).
    'j1_bit0_false': True,
    # AS1F 3 with AS2F 0: the AS1 bus carries the constant EM2.  INFERRED
    # (thesis p.144: "AS1F modifies AS2F's meaning for constants"; open in
    # mekbn).  Decided at 3321 (the one-cell allocator loads R03 with it);
    # the words that load R03 (rassy's lc) this way carry EM2 13 beside
    # the one-cell list (3321, 3378) and 5 beside the two-cell list (332f,
    # 337b): 16 / 1 - 3 and 16 / 2 - 3, the refill's loop count for a
    # 16-word chunk (README "First routine that would not run").
    'as1f3_em2': True,
    # SC2F b, the "wide" immediate (704 words of image 2; layout open in
    # mekbn): the 10 bits EM2:EM3, zero-extended.  INFERRED.  Static
    # evidence: the 223 words whose wide value is 1a0 carry EM1 0 or a
    # TGIF 1/2 stamp tag (2071 {REFo, 1a0}, 2077 {INTo, 1a0}), so EM1 is
    # not part of the value where it is a tag.  Decided at 204b-204d
    # (start's heap-top routine: 1a0 + 4a is the parameter cell read;
    # the alternative EM1:EM2 reading, the injection 'wide_em1em2', reads
    # 1a + 4 and stops on memory never written).  A wide word whose EM1 is
    # non-zero and not a stamp raises (width UNKNOWN: 16 bits or 10).
    'sc2_wide': 'EM2:EM3',
    # U3 second session: a wide word whose EM1 MCF consumes (bit 18) is
    # EM2:EM3 too; EM1 is MCF's key there.  INFERRED (as the stamp case:
    # EM1 belongs to another field).  6 words of image 2 (EM1 07 x2, 01
    # x2, 08, 30); executed at 20a8 (YR := b8 with MCF EM1 07 reset_CGCF,
    # then 20a9 MAR1 := b8).  Injection 'wide_mcf_off' (u3_goals.py):
    # STOP at 20a8 in the boot.
    'sc2_wide_mcf': True,
    'mcf_sub_flags': True,
    # U3 second session: ALU operation add_with_one (rassy's EM2 3) is
    # a + b + 1.  INFERRED from the name (HELD-SOURCE, mekbn.RASSY_ALU)
    # and decided at 3370, R1b's refill (3380 -> 336b-3375): the link it
    # makes, {REFo, MAR1 + 16 + 1} with MAR1 at the record's cell 15, is
    # the next record's cell 0, so the 8 records are 16-aligned and
    # chained.  Injection 'with_one_plain' (a + b): the links fall one
    # short (cell 15 of the next record) and the third pop's record is
    # misaligned (u3_goals.py, observed in its header).
    'alu_with_one': True,
    # A conditional JMPF 1 with EM bit 0 CLEAR is taken when COND holds:
    # the static agent's INFERRED polarity (pu_microcode_inference.md 6.3
    # item 4, "EM bit 0 = 0 ends if the condition holds"), now EXECUTED on
    # a conditional return at 2050 (start's heap-top rounding, below).
    'j1_bit0_clear_true': True,
    # CNDF 2: COND := the ALU result (32 bits) is zero (rassy's alf_zero;
    # CNDF 5 is the static agent's eq).  INFERRED, decided at 204f-2052:
    # 204f MDR2 := hp & 15 forms COND, 2050 R1f := hp & ~15 and returns
    # if COND, 2051-2052 add 16.  The contract: the heap top start
    # leaves is the parameter rounded UP to 16 (never below it: the cells
    # below are in use).  Under 'not zero' (the injection 'cnd2_nonzero')
    # an unaligned top is rounded DOWN: FAIL.  Jointly with the polarity
    # above (the pair (zero, taken if COND) and (not zero, taken if not
    # COND) are the two that satisfy the contract).
    'cnd2_zero': True,
    # A read of a cell never written gives MDR the value POISON instead
    # of raising at once; any use of it (an ALU input, write data) raises.
    # OURS (the hardware reads whatever is there).  Needed at 34a2: the
    # word that reads [MAR1] where MAR1 holds the element itself, an atom
    # for append, not an address (the next words of a REF row read it;
    # row 3494 does not).  Off (the injection 'absent_read_raise'): the
    # old rule, a read of a cell never written raises at the read.
    'absent_read_poison': True,
    # JMPF 8 (bit 26 with kind 0) sequences as JMPF 0 (falls through) in a
    # word whose CNDF 7 is a dereference set-up (DEREF_SETUP): INFERRED,
    # admitted only in that combination (34a1); thesis printed p.144 (7)
    # says part of condition generation moved from CNDF to JMPF, so bit 26
    # may change what the set-up forms -- not decided, and every other
    # JMPF 8 word still raises.  The JMPF 0 / 8 twins (0517 / 051c with
    # EM1 2b, 0563 / 06bf with 2a) are both followed by a case_branch.
    'jmpf8_setup': True,
    # SC2F 1 with WRBF clear puts a field of the instruction register IR
    # on the S2 bus, not a register R01: the instruction's low 16 bits,
    # sign-extended, tag 0.  INFERRED (U2, 2026-11-27, third session).
    # Thesis printed p.129 (section 3.3.3.5): the S1 bus reaches every
    # register EXCEPT IR, the S2 bus reaches RF, WR and IR, and IR has
    # field extraction (rassy lists the extractions ir/8, ir/16, ir/24
    # and signed forms, binary_reverse_engineering.md section 3).  The
    # image agrees: 46 words read select 1 through SC2F and none of the 26
    # words that write select 1 (DSTF) is in a KL1 instruction routine
    # that reads it; the 8 label words 32f0-32ff add it to R04 (pc) and
    # jump to the label branch 2447 (pimm.py: pc + 2 + sx16(c16)), and
    # wait_vector (3a03, 3a06, 3a0b) subtracts it from the vector's
    # length (pimm.py: c16).  The width per instruction is NOT decided:
    # put_reused_structure is r_r_c8 (n = z), so where its y field is not
    # zero the c8 and c16 readings differ and the read raises
    # (setup.IR_C8).  Executed at 31ec (append's y is 0); the value is not
    # used on the path run (MDR2 is loaded and the routine ends): NOT
    # discriminated.  Off (the injection 'sc2f1_reg'): the old reading,
    # a register R01 never set, raises at 31ec.
    # U2 eighth session: the field is chosen by EM2 & 15, by rassy's
    # ext_ir/2 (@2e72, HELD-SOURCE: a switch on EM2 & 15 whose arms name
    # the pool's '/ ir 16', '/ ir 24', '/ (>> ir 16) 16', ... in order;
    # sc2f/8's arm 1 sets em2_not_free and does not test WRBF): EXT_IR
    # below.  It decides the width: 31ec (put_reused_structure, r_r_c8)
    # carries EM2 4 = ir/8 (c8); the label word 32f0 9 = ir/s16 (pimm.py
    # sx16(c16)); wait_vector 3a03 / 3a06 1 = ir/16 (c16); enqueue_goal
    # 4c00 (WRBF set, the old reading W01) 6 = (ir >> 16)/8, the x field
    # (the arity).  Census of SC2F 1 loads (image 2), EM2 & 15: 1 in 4,
    # 4 in 3, 5 in 1, 6 in 18, 7 in 5, 9 in 22.  'c16s' (the old reading)
    # is the injection 'ext_ir_off'.
    'sc2f1_ir': 'ext_ir',
    # CNDF 7 with EM1 29: COND := the MRB (tag bit 0) of the ALU's AS1
    # input is ON.  INFERRED (U2, 2026-11-27, third session).  Decided at
    # 31ec-31ed (put_reused_structure's 'other' row, MDR1 = the
    # dereferenced structure pointer): 31ed ends (x and R02 := the
    # pointer: the structure reused in place) when COND is false
    # (j1_bit0_false), and falls to 31ee (the allocating arm: a call to
    # 31a1, then 31f0 jumps to put_list) when it holds.  The contract: a
    # structure whose pointer has its MRB on is shared and must not be
    # reused in place; one with its MRB off is single-referenced and is
    # reused (TR-466 4.2: "When the input cons cell is single-referenced,
    # it can be reused as the new output cons cell"; thesis printed p.138,
    # Fig. 3-23: the S stage tells the E stage whether the data reached
    # is collectable).  pu_smt (contract 'reuse_kl1') eliminates every
    # value relation, 'never' and 'always' and keeps the MRB test up to
    # the global end polarity, as for CNDF 5.  Static support for an
    # MRB test on the AS1 input: 0ac9-0acb and 0ace-0ad0 form it from
    # MDR2 alone and then stamp EHOOKo or EHOOKx (EUNDFo or EUNDFx) by
    # it.  Not decided: whether the S stage's chain report (SRP: every
    # MRB in the chain off) takes part; append's operand is held directly
    # (no REF), where the two agree.  Injection 'em1_29_off' (COND = MRB
    # off): append's instruction 4 STOPs at 31ee (MCF with EM1 08), the
    # LISTx side case ends at 31ed (a shared list reused: FAIL).
    'em1_29_mrb': 'on',
    # AS1F 2 puts YR on the AS1 bus.  INFERRED (U2, 2026-11-27, fifth
    # session).  AS1F is in SD1F's numbering (MEASURED, mekbn), whose
    # value 2 is yr in rassy's adder-source table (0 nop, 1 xr, 2 yr,
    # 4 mdr1, 5 mdr2, 6 mar1, 7 mar2; binary_reverse_engineering.md
    # section 3), and the thesis (printed p.126, psi_microword.md 3b) has
    # XR, YR, MDR1/2 reach AS1.  Static: of 446 words with AS1F 2 and
    # AS2F 0, 157 are ALF 3 operations on it alone (shift_left,
    # shift_right_32m by EM2), 112 copies (MAR1 <- as1_2 ...).  The ALU
    # reads YR as it stood before the word (the existing 'old' rule for
    # every ALU input: 0306 'YR <- #1; W1d <- as1_2 - 0' with a zero test
    # is a test of the old YR).  Executed at 4cc0 (execute: R15 := YR,
    # not compared).  Off (the injection 'as1f2_off'): raises.
    'as1f2_yr': True,
    # CNDF 3: COND := the ALU result is negative (bit 31).  INFERRED from
    # rassy's short condition table, in the class's order 'cond carry',
    # 'cond zero', 'cond sign', 'cond same_tag', 'cond equal', 'cond
    # lc_one', read as CNDF 1..6: 2 (zero, RULES['cnd2_zero'], decided at
    # 204f-2052), 5 (eq, pu_smt) and 6 (the counted loops on lc,
    # README "Conditions") fit it independently.  Executed at 4cc1 on a
    # STALE input, where nothing tests it (cjump_time 'prev'): NOT
    # discriminated.
    'cnd3_sign': True,
    # JMPF 8 sequences as JMPF 0 in a word whose CNDF 7 selects a flag
    # condition (FLAG_CONDS): INFERRED, as RULES['jmpf8_setup'], and
    # admitted only there (4cc2, interrupt_all; what bit 26 adds to the
    # condition is not decided).  Off (the injection 'jmpf8_flag_off'):
    # raises at 4cc2.
    'jmpf8_flag': True,
    # JMPF 2 (4-bit; S10, open until now) is a case_branch with a short
    # base: target = (upc + EM3, EM3 signed as in JMPF 4) | TDAR.
    # INFERRED (U2, 2026-11-27, sixth session).  rassy's jmpf table
    # (asm/ptfdump.py pimmutil rassy --list, predicate jmpf/9 @2a5c, a
    # 16-way switch on the JMPF value): arm 2 names 'base' and
    # 'case_branch' and formats its operand with short/3, the form arm 4
    # ('goto', the relative JMPF 4) uses; arm 3 names 'base' and
    # 'case_branch' with long/4 and em2_not_free (the page-relative
    # JMPF 3 case_branch, S8).  HELD-SOURCE for the kind; the base
    # arithmetic is JMPF 4's (mekbn J4_SIGNED).  Static: of the 16 JMPF 2
    # words of image 2, 15 put upc + EM3 on a 16-word boundary (all but
    # 0207: 0202), where 1 in 16 would by chance; e.g. 2447 -> 2440,
    # 2455 -> 2450, 31a1 -> 31a0 (the base 31a3's JMPF 3 also uses),
    # 2425 -> 2420, 2437 -> 2430, 2401 -> 2400, 323c -> 3240, 327c -> 3280.
    # EM2 is free (an ALU operation in 6 of the 16).  The TDAR it ORs in
    # is the S stage's multiway set-up (setup.S_TDAR) when no E-stage
    # set-up precedes it.  Executed at 2447 (switch_on_non_list on nil:
    # 2440 | 0).  Injections: 'jmpf2_off' (raises), 'jmpf2_unsigned'
    # (EM3 unsigned: 2447 -> 2450).
    'jmpf2_case': 'signed',
    # ALF 2/3 with EM2 20 / 30: the MRB off / on operations, the result
    # the AS1 input with its tag's bit 0 cleared / set.  rassy's
    # special_operation/4 (@3030, a switch on EM2): 0 '+', 2
    # add_with_carry, ... 15 shift_right_arithmetic, 32 (20) 'mrb_off',
    # 48 (30) 'mrb_on' (HELD-SOURCE for the names; the value passing
    # unchanged is INFERRED).  Executed at 2447 (MDR2 := mrb_off(MDR1),
    # then 2440 writes it to x: nil stays {ATOMo, 0}).  Injection
    # 'mrb_swapped' (20 = on): the firmware writes A0 := {ATOMx, 0}, FAIL.
    'em2_mrb': {0x20: 'off', 0x30: 'on'},
    # JMPF 9: a call taken "if cond" (rassy's jmpf/9 arm 9: 'call',
    # em1_not_free and em2_not_free, the absolute 16-bit form of arm 5,
    # and the 'if cond' constant; CJUMP_TAKEN_ON's evidence).  INFERRED
    # (HELD-SOURCE for the kind).  Until the eighth session only the arm
    # not taken was modelled; the taken arm's target is now decided
    # (RULES['jmpf9_vlong'] below).  Executed at
    # 38b1 (get_value's row 4: the S stage's COND, x not UNDF, is false).
    'jmpf9_call_if': True,
    # U2 eighth session: the taken arm's target is the absolute 16-bit EM
    # (HELD-SOURCE: rassy jmpf/9 arm 9 prints its target with vlong/2
    # (@32da), convert_to_hex_atom of the whole EM, as arm 5 (JMPF 5, the
    # absolute call mekbn reads) does; the page-relative arms 6, 7, a, b,
    # e, f use long/4 (@32cd: upc & fc00 | EM2 << 4 | EM3)).  Static: of
    # the JMPF 9 words around proceed, 21b8 carries EM 6c21 (the trap,
    # outside image 2), 217b / 220b 21b2 and 2210 21b5 (in-page either
    # way).  Executed taken at 217b (proceed's empty arm with crr
    # exhausted), where both readings land on 21b2: the target reading
    # is HELD-SOURCE plus the static 21b8 -> 6c21, NOT discriminated by
    # execution.  Injection 'jmpf9_taken_raise' restores the old raise.
    'jmpf9_vlong': True,
    'jmpf9_cndf': True,             # pu.cndf_free
    # JMPF f: a page-relative call taken if NOT cond (rassy jmpf/9 arm f,
    # 'call' long and the 'if not cond' pool slot, as arm b is 'if cond';
    # CJUMP_TAKEN_ON's evidence).  HELD-SOURCE (the kind).  Executed at
    # 2215 (proceed's dequeue: call 2250 unless the next goal's cell 14
    # equals R13, the current foster parent), not taken.
    'jmpf_f_call_ifnot': True,
    # U3 (2026-11-27, first session): JMPF 8 in a word that forms no
    # condition of its own (outside jmpf8_setup / jmpf8_flag) is a short
    # goto taken if COND, COND as the word before left it.  HELD-SOURCE
    # for the kind: rassy's jmpf/9 arm 8 (@2afb) names 'goto' and formats
    # its operand with short/3 (@7ef), as arm 4 (the relative JMPF 4,
    # mekbn J4_SIGNED: upc + EM3, signed), and takes the pool slot 00af
    # 'if cond' (CJUMP_TAKEN_ON's evidence).  INFERRED that COND is the
    # previous word's (the cjump_time 'prev' rule).  Executed at 4c01
    # (enqueue_goal): 4c00 forms COND := slit_check (CNDF 7 EM1 19,
    # FLAG_CONDS), and 4c01 goes to 4c08 (XR := R16, YR := R0d, a shift:
    # the priority-bit path, as execute's 4cc5) when it holds; with the
    # flag clear it falls through to the trailer 4c02-4c07.  Off (the
    # injection 'jmpf8_goto_off'): raises at 4c01.
    'jmpf8_goto_if': True,
    # Tension, recorded not resolved: rassy's arm 8 covers EVERY JMPF 8
    # word, but 34a1 (jmpf8_setup) and 4cc2 (jmpf8_flag) still fall
    # through unconditionally here; on the paths run their COND would
    # have to be false for the two readings to agree.
    # U3 (2026-11-27, first session): a register select d (SC1F, SC2F,
    # DSTF) with WRBF set names the register-file entry R(10 | EM1), EM1
    # 0-f, not a work register "W0d".  INFERRED from the image (no rassy
    # arm read: sc1f/7's arm d sits with arms 8-b, not decoded here):
    # the four such writers carry EM1 0, 9, b, 2 (21e4 after a call of
    # 3349, the R1b pop, as 202f R10 := MDR1; 0d93 a list push shaped as
    # 216c-216d), and at the words run no other field of the word uses
    # EM1.  Decided at enqueue_goal's 4c01 (EM1 5): MAR1 := R15, so that
    # 4c02 is R15 := R15 - 1 as proceed's 216d and execute's 4cc0 (before,
    # "W0d" was never set and the run stopped).  Held-out, read not run:
    # the refill's 3365 / 3366 (EM1 0f) take MAR1 := R1f, the heap
    # pointer, the cells a refill would carve.  EM1 10-3f raise, and so
    # does a word where another field also
    # consumes EM1 (em1_other_use: TGIF 1 / 2, CNDF 7, MCF, an EM1 or wide
    # S2 immediate, an EM jump target).  Counter-evidence kept: of the 99
    # words, 14 also use EM1 elsewhere (0517, 0ab4-0abc, 1989, 357c, 3c39,
    # 4172, 4c5f, 63d6, 75a4, 79c9 by CNDF 7 / MCF / SC2F 8), where the
    # reading would double-use the field.  Off (the injection
    # 'wsel_d_off'): W0d again.  Census: 53 of the 99 select-d words
    # are admitted (EM1 0-f, no other EM1 consumer).
    'wsel_d_em1': True,
    # DSTF c: rassy's dstf/5 key 12 prints '++ rfar' (pool slot 95, after
    # '@ r0' .. '@ r1b1' for keys 8-b): the register-file entry that RFAR
    # (DSTF / second-bank 6, 'rfar') names, RFAR then stepped.  INFERRED
    # (name HELD-SOURCE) that the entry is the argument register A[rfar].
    # Executed at proceed's 2219-2223 (the next goal's arguments: 2215
    # R06 := 0, then one '++ rfar' write per argument).  Injection
    # 'rfar_off': DSTF c is a register R0c again.
    'dstf_c_rfar': True,
    # The loop counter lc (R03, rassy's second-bank 3): MCF EM1 10 is
    # mc1's '-- lc' (pool slot 0116, HELD-SOURCE), R03 := R03 - 1; CNDF 6
    # is 'cond lc_one' (the short table's sixth) and CNDF 7 EM1 0d 'cond
    # lc_zero' (cndf_others key 0d), each on lc as it stood before the
    # word.  INFERRED (the names HELD-SOURCE; the timing 'old').  Executed
    # at proceed's 2218-2222, the argument loop; the side case's arities
    # 1-6 and 11 tell the timing (injection 'lc_new': the conditions see
    # the decremented lc).
    'lc_ops': 'old',
    # CNDF 8 / a: COND := the tag of the value on the S1 bus == EM1 / EM2
    # (beside CNDF 9 / b, the ALU's AS1 input).  INFERRED (U2, 2026-11-27,
    # sixth session).  rassy's cndf/7 (@82a, a switch on CNDF): arms 8
    # and 9 both 'cond' (an operand's) 'tag = ' EM1 (em1_not_free), a and
    # b 'tag = ' EM2, 8 / a on one operand of the predicate and 9 / b on
    # the other (HELD-SOURCE).  MEASURED (scratch census, image 2, words
    # not JMPF 1): all 217 CNDF 8 words and all 20 CNDF a words read an
    # S1 source (SC1F or WRBF), 114 and 9 of them with no S1 destination
    # (rtl's 'read X': a read for the condition alone), and 61 / 3 have
    # no ALU operation at all; every CNDF 9 (453) and b (56) word has an
    # ALU input.  Executed at 38b0 (get_value: MAR2 := A[x], EM1 REFo;
    # false for nil, so 38b1's conditional call is not taken).
    # CNDF c: the same on the S1 value with the MRB ignored (tag / 5 =
    # EM1: rassy's arm c, 'cond' 'tag' '/' 5 '=' EM1, the tag's upper 5
    # bits; arm d the same on the other operand).  Census: 100 CNDF c
    # words, every EM1 an 'o' tag (REFo 51, INTo 15, VECTo 11, ...), 12
    # with neither an S1 destination nor an ALU operation; all 232 CNDF
    # d words have an ALU input.  Executed at 38b2 (get_value: A[y], a
    # REF either way).  CNDF d is not run and raises.
    'cnd8_s1': True,
    # SD1F 2 / 3: the S1 value goes to MDR1 and MAR1 / MDR2 and MAR2 at
    # once.  rassy's sd1f/2 (@2959): 0 nop, 1 xr, 2 the pair ', mdr1
    # mar1', 3 ', mdr2 mar2' (the two pool constants just before the
    # jmpf 'if cond' ones), 4 mdr1, 5 mdr2, 6 mar1, 7 mar2 (HELD-SOURCE;
    # 1 and 4-7 are mekbn's MEASURED numbering); thesis printed p.144
    # (psi_microword.md 3, DOCUMENTED): "SD1F codes include writing the
    # same value to MAR1+MDR1 and MAR2+MDR2".  Executed at 38b2
    # (get_value: A[y] into MDR2 and MAR2).
    'sd1_pairs': {2: (MDR1, MAR1), 3: (MDR2, MAR2)},
    # JMPF b: a page-relative CALL taken if cond (not mekbn's page jump;
    # the open conflict of docs/pu_microcode_inference.md S7, decided).
    # U2, 2026-11-27, seventh session; INFERRED, kind HELD-SOURCE.  (1)
    # rassy's jmpf/9 arm b names 'call' with the long (page-relative)
    # operand and 'if cond', as arm f ('call', 'if not cond') and arm 7
    # (the unconditional call, S7 VERIFIED).  (2) The twins 0c0c (JMPF b)
    # and 0c0f / 0c12 (JMPF 7) are the same word, W1d := MAR1 with the
    # set-up EM1 3f, to the same 0c15, whose rows (0e38 -> 0e60-0e76)
    # all end in returns.  (3) MEASURED (scratch census, image 2: from
    # each target, the words reachable before a return or an end, calls
    # taken as returning): of the 47 JMPF b targets, 38 reach only
    # returns, 9 both, none only ends; JMPF 7 (calls) 144 / 42 / 4, JMPF f
    # 24 / 6 / 0, but JMPF 6 (page jumps) 338 / 185 / 510 and JMPF e 130
    # / 15 / 218.  (4) execute's 4cc1 (JMPF b to 4cc5, the slit-check
    # path) is consistent: that path's conditional return 4cd2 would
    # return into 4cc2, the fast path's next word.  Executed taken at
    # 0c0c (get_value: A[y] a REF, 38b2's COND), returning to 0c0d;
    # not taken at 4cc1.  Off (the injection 'jmpf_b_jump'): the old
    # page jump; the return at 0e72 meets an empty micro stack.
    'jmpf_b_call': True,
    # A case_branch (JMPF 3) ORs the whole TGT byte into its base, not
    # only 4 bits, when the base's low bits are free of it: 0e75's base
    # 0e60 takes column 5's bytes 0..19 (rows 0e60-0e73; UNDF 18 ->
    # 0e72, a return).  INFERRED (U2, seventh session; S8's "low 4 bits"
    # was the 2d3f / 31a3 tables'); bytes over 15 elsewhere still need a
    # base whose low bits clear them.  Off (the injection 'case_4bit'):
    # a byte over 15 raises, as before (a guard only).  'low4' (the
    # injection 'case_low4', S8 read literally, byte & 15): UNDF 18 lands
    # on 0e62, the row that frees the cell: FAIL.
    'case_wide': True,
    # TDAR holds from its set-up across words that form nothing (a JMPF 1
    # word, whose CNDF bits are the jump's low address bits), so a
    # case_branch may follow its set-up two words on.  INFERRED (U2,
    # seventh session; rassy names 'tdar' among the registers): the
    # three twins 0c0d -> 0c0e (JMPF 1) -> 0802, 0c10 -> 0c11 -> 0800,
    # 0c13 -> 0c14 -> 0801 all put their set-up (EM1 32 / 33) two words
    # before the JMPF 3.  Executed at 0802.  Off (the injection
    # 'tdar_one_word'): the set-up must be the word just before (the old
    # rule): a guard fires, so the rule is needed, but NOT discriminated
    # (no rival reading of the multiway runs and is compared).
    'tdar_holds': True,
    # AS1F 3 with AS2F not 0 (0802: 'as1_3 - MDR1'; the EM bits there are
    # the JMPF 3 base, not a constant, so RULES['as1f3_em2'] does not
    # apply): the AS1 source is not decided.  The result is UNKNOWN: a
    # word that writes it raises; a COND or an alf latch formed from it
    # is POISON (raises when tested).  OURS (fail loud on use).  At 0802
    # it feeds only CNDF 5 and set_alf, and 0864 forms a new COND before
    # anything tests them: NOT discriminated.
    'as1f3_open_unknown': True,
    # The ALU's input pair, read from rassy (HELD-SOURCE; U2, 2026-11-27,
    # eighth session).  'rassy' supersedes as1f2_yr, as1f3_em2 and
    # as1f3_open_unknown above, which stay only as the injection
    # 'alu_old'.  rassy's as1f_and_as2f/6 (@29b1, a switch on AS1F whose
    # clause k starts 'get_integer A0, k'): 0 '0' and 1 xr, each with
    # as2f/2 (@2efc: 0 '0', 1 yr, 2 mdr1, 3 mdr2); 4 mdr1, 5 mdr2, 6 mar1,
    # 7 mar2 likewise; 2 sets the slot special_case := 1 and calls
    # with_constant/2 (@2f1c), which names the AS1 input by AS2F
    # (0 mdr1, 1 mdr2, 2 mar1, 3 mar2) and leaves AS2 to the constant;
    # 3 calls special_case/5 (@800): AS2F 0 '0' and 1 xr with the
    # constant as AS2 (slot special_case := 1), 2 mar1 and 3 mar2 with
    # xr as AS2 (no constant).  The constant is printed by alf/7's
    # $or$70 / $or$71 (@3d09, @3d1a; '-' through $or$72 / $or$73): EM2,
    # or EM1 when the slot em2_not_free is set (EM2 used by another field).
    # Census (image 2, scratch): with ALF 0/1, EM2 is 1 in 68 of 155
    # (2,0,add), 52 of 97 (2,0,sub), ... 46 of 61 (2,3,sub), 156 of 402
    # (3,1,add): an increment; with AS1F 3 / AS2F 2-3 (no constant) EM2 is
    # spread (0 in 4 of 9).  Held-out check: 220f (AS1F 3 AS2F 1, EM2
    # 12, EM1 the CNDF 9 tag) gives MAR1 := R14 + 12, the goal record's
    # cell 12 that enqueue_goal's trailer writes (4c03: the same 12).
    # So 'a word that loads YR and uses it' (216d, 4cc0) does not use
    # YR at all, and 0802's AS1F 3 / AS2F 2 is MAR1 against XR.
    # ALF 2/3 with a constant (EM2 is the operation, so em2_not_free):
    # EM1, by $or$71's other arm; raises when EM1 is used by MCF, CNDF
    # 7/8/9/c/d, a TGIF stamp or SC2F 8 (not met on a path run).
    # Injections: 'alu_old' (the three old rules), 'const_em3' (EM3 as
    # the constant), 'as1f3_xr_off' (AS1F 3 AS2F 2/3 UNKNOWN again).
    'alu_sources': 'rassy',
    'alu_const': 'EM2',
    'as1f3_mar_xr': True,
}
# rassy's sc1f/7 (@21bf; set_up_sc1f/3 @c68 passes SC1F, WRBF, EM1, EM2,
# EM3 in that order) names S1 selects 0-4 dr, sr, gr, lc, pc, and for 5,
# 6, 7 prints a hex number from EM1, EM2, EM3 (convert_to_hex_atom @d74):
# an immediate, not a register.  sc2f/8 (@24b7; set_up_sc2f/3 @c85, the
# same argument order) prints EM3 for select d.  HELD-SOURCE (the
# listing); INFERRED that the hardware reads the field as rassy prints it.
# Fits the never-set census (R05 549 reads / 14 DSTF writes, R06, R07:
# the README's 'constant or hardware source'): {ATOMo, R06} where nil
# stands = EM2 0, {UNDF, R07} at 31d6 = EM3 0, '1a0 + R05' = a parameter
# cell 1a0 + EM1.  Supersedes RULES['zero_regs'] (kept for 'em_imm_off').
S1_IMM = {5: 'EM1', 6: 'EM2', 7: 'EM3'}
# ext_ir's arms 0-15: (shift, width, signed); 0 and 8 the whole IR
EXT_IR = {0: (0, 32, False), 1: (0, 16, False), 2: (0, 24, False), 3: (16, 16, False),
          4: (0, 8, False), 5: (8, 8, False), 6: (16, 8, False), 7: (24, 8, False),
          8: (0, 32, False), 9: (0, 16, True), 0xa: (0, 24, True), 0xb: (16, 16, True),
          0xc: (0, 8, True), 0xd: (8, 8, True), 0xe: (16, 8, True), 0xf: (24, 8, True)}
S2_IMM = {0xd: 'EM3'}
EM_IMM = True
# The conditional page-relative / relative jumps JMPF a/b/c/e
# (RULES['cjump_time'] above).  U2, 2026-11-27, fifth session: 'prev',
# INFERRED.  (1) Thesis printed p.130 (psi_microword.md 3b, DOCUMENTED):
# the condition is selected into COND one step and branched on the next.
# (2) The conditional END already tests the previous word's COND
# (EXECUTED, pu_smt).  (3) execute 4cc0-4cc1: 4cc0 forms the slit check
# (CNDF 7 EM1 19) and 4cc1, a JMPF b to 4cc5, forms CNDF 3 itself; under
# 'same' 4cc0's slit check would be overwritten untested on every path,
# under 'prev' 4cc1 branches on it.  (4) Static (scratch census, image 2,
# non-self jumps): of the JMPF b words, 27 have no CNDF of their own
# but a CNDF in the word before, 4 the opposite (a: 97 / 51, c: 123 / 23,
# e: 94 / 45).  Polarity, CJUMP_TAKEN_ON: which COND value takes the
# jump, per JMPF code; only b is EXECUTED (4cc1: taken on COND, the slit
# check pending; not taken with no event, the fast path 4cc2-4cc3 that
# sets R04 := the label).  Other codes raise.
#
# U2, 2026-11-27, sixth session: a and e.  rassy's jmpf/9 arms 8-f
# carry one more constant than arms 0-7, and the class's constant pool
# holds, in order, 'if cond' four times, 'if not cond' four times, then
# the same again for jmpf/10 (HELD-SOURCE: ptfdump.py pimmutil rassy
# --list; resolved: each arm's 'pmi 49' operand is a relative reference,
# and arms 8-f of jmpf/9 land on pool slots 00af-00b6 (jmpf/10's on
# 00b7-00be), 00af-00b2 'if cond' and 00b3-00b6 the vector [if, [not,
# cond]], one slot each; sd1f/2's arms 2 / 3 land on 00ad / 00ae, ',
# mdr1 mar1' / ', mdr2 mar2', just before).  So JMPF 8-b are taken "if cond"
# and c-f "if not cond", arms 8-f repeating 4-7's kinds (goto short,
# call, goto long, call long).  Executed: e at 2440 and 2461
# (switch_on_non_list on nil: 2440 must jump to 2461 and 2461 to the
# end 241d for a directly held nil, whose 3310 COND -- MDR2 a REFo -- and
# COL are false; taken on COND, 2441 would put a cell on the R19 list
# and 2462 read [MAR2]), a at 3980 (wait_nil on nil: taken on the
# S stage's COND to the end 3985; not taken, 3981 frees a cell).  This
# also gives b "call long if cond": the existing 'jump taken on COND' at
# 4cc1 agrees on the polarity; the call-or-jump question is not met on
# the path run (4cc1 is not taken) and is recorded open.  Injections:
# 'e_on_true' (e taken on COND), 'a_on_false'.
CJUMP_TAKEN_ON = {0xb: True, 0xa: True, 0xe: False}
# U3 second session: c, rassy's arm c ("goto short", 'if not cond',
# the same constants as above: HELD-SOURCE).  Executed at 20a1 (start:
# taken when PMPF is reset, to 20a6, crr := 17; not taken when set, 20a2
# reads the reduction limit).  Injection 'c_on_true' (u3_goals.py).
CJUMP_TAKEN_ON[0xc] = False

# Conditions.  COND is formed by a word's CNDF and tested by a later
# conditional word (thesis p.130: condition into the flag COND one step,
# branch on it the next); it stands until a word forms a new one.  key:
# CNDF.  A rule returns a bool from the ALU's first input as the word
# saw it (the tag of a register compared with an immediate, M92 p.428).
def _cnd_tag_eq(which):
    def rule(pu, upc, x, a):
        if not RULES['cnd9_link']:
            raise Unmodelled(upc, 'CNDF %x (rule off)' % field(x, 'CNDF'))
        if a is None:
            raise Unmodelled(upc, 'CNDF %x with no ALU input' % field(x, 'CNDF'))
        return a[0] == field(x, which)
    return rule


# CNDF 9: tag of the ALU's AS1 input == EM1.  CNDF b: == EM2.
# INFERRED.  Evidence: CNDF 9 words leave EM1 free (TGIF 0 in 448 of
# 453, image 2) and their EM1 values are tags (ATOMo 105, INTo 94,
# REFo 32, VDESC 26, FPREC 24, SHREC 20, MOD 17, ...); CNDF b words often
# use EM1 for a stamp (TGIF non-zero in 24 of 56) and their EM2 values are
# tags (ATOMo 15, INTo 14, VDESC 4, ...).  Decided at 31fa and 31d1 (EM1
# ATOMo: the refill's last link is {ATOMo, 0}, 3368) and 318c, 3196, 31d6
# (EM2 ATOMo), each tested by the conditional end that follows.
def _signed(v):
    v &= M32
    return v - (1 << 32) if v >> 31 else v


def cndf_free(x):
    """Whether this word's CNDF forms a condition.  Not in a JMPF 1 word:
    rassy's jmpf/9 arm 1 calls special_jump/8 (@30ec), a 15-key switch
    on CNDF, so CNDF selects the special jump's kind (HELD-SOURCE).  Arm 9
    (JMPF 9) prints its target with vlong/2 (@32da), which marks only
    em1_not_free / em2_not_free, not cndf_used (elong/5 @32df does): its
    CNDF is a condition (RULES['jmpf9_cndf'], HELD-SOURCE).  Static: the
    JMPF 9 words with a CNDF (2 in 9, 5 in 1) all carry an ALU add or
    subtract.  Executed at 2214 (CNDF 5, the next goal's foster parent
    against R13, tested by 2215's JMPF f).  Injection 'jmpf9_cndf_off'."""
    if mekbn.jk(x) != 1:
        return True
    return field(x, 'JMPF') == 9 and RULES['jmpf9_cndf']


def alf_cond(latch, name):
    """A 'cond alf_*' on the set_alf latch (ALU inputs a, b, result v).
    alf_zero: v is 0; alf_sign: v negative; alf_equal: a and b equal in
    value.  INFERRED from the names (HELD-SOURCE, rassy positions 0, 1, 5);
    the others are POISON (raise when tested).  A STALE latch gives a
    STALE COND."""
    if latch is POISON or is_poison(latch):
        return POISON
    a, b, v = latch
    if is_stale(v) or is_stale(a) or is_stale(b):
        return STALE
    if name not in ALF_LATCHED:
        return POISON
    if name == 'alf_zero':
        return v & M32 == 0
    if name == 'alf_sign':
        return bool(v >> 31 & 1)
    return a[1] & M32 == b[1] & M32


def lc_cond(pu, upc, k, lc):
    """lc_zero (k 0) / lc_one (k 1) on lc as it stood before the word
    (RULES['lc_ops'] 'old'; 'new': after this word's '-- lc')."""
    if lc is None or is_stale(lc):
        raise Unmodelled(upc, 'lc condition with R03 unset or not known')
    v = lc[1]
    if RULES['lc_ops'] == 'new' and pu._lc_dec:
        v -= 1
    return v & M32 == k


def _cnd5(pu, upc, x, a):
    """CNDF 5: the word's ALU result is zero (eq).  EXECUTED up to one
    global polarity by pu_smt (inference doc 6.3 item 4); eq chosen
    INFERRED, with 'EM bit 0 = 0: end if the condition holds'."""
    if pu.alu_seen is None:
        raise Unmodelled(upc, 'CNDF 5 with no ALU operation')
    return pu.alu_seen[2] & M32 == 0


def _cnd7(pu, upc, x, a):
    """CNDF 7, by EM1: 0a lt (EXECUTED up to the polarity, inference doc
    6.3 item 4), 09 overflow of the add/subtract (INFERRED, item 5), 29
    the MRB of the AS1 input (RULES['em1_29_mrb'], INFERRED), 3a
    the case_tag_setup of a JMPF 3 multiway, 2d the dereference set-up
    (DEREF_SETUP), 28 a condition of UNKNOWN meaning (COND_UNKNOWN: COND
    becomes POISON); the last three are handled in evaluate.  Any other
    EM1 is UNKNOWN and raises."""
    em1 = field(x, 'EM1')
    if pu.alu_seen is None:
        raise Unmodelled(upc, 'CNDF 7 EM1 %02x with no ALU operation' % em1)
    a1, b1, v = pu.alu_seen
    if em1 == 0x0a:
        if field(x, 'ALF') != 1:
            raise Unmodelled(upc, 'CNDF 7 EM1 0a (lt) without a subtract')
        return _signed(a1[1]) < _signed(b1[1])
    if em1 == 0x29 and RULES['em1_29_mrb']:
        if is_poison(a1) or a1 is None:
            raise Unmodelled(upc, 'CNDF 7 EM1 29 with no ALU input')
        on = bool(a1[0] & 1)
        return on if RULES['em1_29_mrb'] == 'on' else not on
    if em1 == 0x09:
        if field(x, 'ALF') not in (0, 1):
            raise Unmodelled(upc, 'CNDF 7 EM1 09 (overflow) without an add/subtract')
        return not -(1 << 31) <= _signed(a1[1]) + (1 if field(x, 'ALF') == 0 else -1) * _signed(b1[1]) < (1 << 31)
    raise Unmodelled(upc, 'CNDF 7 EM1 %02x (condition UNKNOWN)' % em1)


def _cnd2(pu, upc, x, a):
    """CNDF 2: the word's ALU result is zero (RULES['cnd2_zero'])."""
    if pu.alu_seen is None or pu.alu_seen[2] is None:
        raise Unmodelled(upc, 'CNDF 2 with no ALU operation')
    z = pu.alu_seen[2] & M32 == 0
    return z if RULES['cnd2_zero'] else not z


def _cnd3(pu, upc, x, a):
    """CNDF 3: the word's ALU result is negative (RULES['cnd3_sign'])."""
    if not RULES['cnd3_sign']:
        raise Unmodelled(upc, 'CNDF 3 (rule off)')
    if pu.alu_seen is None or pu.alu_seen[2] is None:
        raise Unmodelled(upc, 'CNDF 3 with no ALU operation')
    return bool(pu.alu_seen[2] >> 31 & 1)


def _cnd_s1_tag_eq(which, mask=63):
    """CNDF 8 / a: the tag of the S1-bus value == EM1 / EM2
    (RULES['cnd8_s1'])."""
    def rule(pu, upc, x, a):
        if not RULES['cnd8_s1']:
            raise Unmodelled(upc, 'CNDF %x (condition not known)' % field(x, 'CNDF'))
        v = pu.s1_seen
        if v is None or is_poison(v):
            raise Unmodelled(upc, 'CNDF %x with no S1-bus value' % field(x, 'CNDF'))
        if is_stale(v):
            return STALE
        return v[0] & mask == field(x, which) & mask
    return rule


COND_RULES = {9: _cnd_tag_eq('EM1'), 0xb: _cnd_tag_eq('EM2'), 5: _cnd5, 7: _cnd7, 2: _cnd2,
              3: _cnd3, 8: _cnd_s1_tag_eq('EM1'), 0xa: _cnd_s1_tag_eq('EM2'),
              0xc: _cnd_s1_tag_eq('EM1', 62)}


def em1_other_use(x):
    """Another field of the word consumes EM1 (RULES['wsel_d_em1'] is
    admitted only where none does): a TGIF 1 / 2 stamp, CNDF 7, MCF, an
    EM1 / wide S2 immediate, or a jump whose target is in the EM."""
    if field(x, 'TGIF') in (1, 2) or field(x, 'CNDF') == 7 or bit(x, 18):
        return True
    if field(x, 'SC2F') in (mekbn.SC2_EM1, mekbn.SC2_WIDE):
        return True
    return mekbn.jk(x) not in (0, 2, 4) or field(x, 'JMPF') in (9, 0xd)


def em_jump_busy(x):
    """Does the word's sequencing use EM1/EM2 (a target in the EM bits)?
    JMPF 0 / 8 none; JMPF 1 only when it jumps (mekbn.J1_JUMP); JMPF 4
    and c only EM3 (upc + EM3, as mekbn reads both); every other kind is
    taken to use them."""
    j = field(x, 'JMPF')
    if j in (0, 8) or mekbn.jk(x) == 4:     # 4 / c: upc + EM3
        return False
    if j == 1:
        return bool(field(x, 'EM') & mekbn.J1_JUMP)
    return True


def em2_busy(x):
    """rassy's slot em2_not_free, as far as the fields run here use EM2:
    a jump target, an EM2 tag compare (CNDF a/b/d), a TGIF 3 stamp, an EM2
    or wider S2 immediate, the S1 immediate EM2, an ALF 2/3 operation."""
    return (em_jump_busy(x) or field(x, 'CNDF') in (0xa, 0xb, 0xd)
            or field(x, 'TGIF') == 3 or field(x, 'ALF') in (2, 3)
            or (field(x, 'SD2F') and field(x, 'SC2F') in (9, 0xa, 0xb, 0xc))
            or (field(x, 'SD1F') and field(x, 'SC1F') == 6 and not bit(x, mekbn.WRB_BIT)))


def em1_busy(x):
    return (em_jump_busy(x) or bit(x, 18) or field(x, 'CNDF') in (7, 8, 9, 0xc, 0xd)
            or field(x, 'TGIF') in (1, 2)
            or (field(x, 'SD2F') and field(x, 'SC2F') in (8, 0xa, 0xc))
            or (field(x, 'SD1F') and field(x, 'SC1F') == 5 and not bit(x, mekbn.WRB_BIT)))


class PU:
    def __init__(self, fw=None):
        self.fw = fw or mekbn.Firmware()
        st = pu_store.stores()
        # the KL1 control store: image 2, then syspsi from 6800 up,
        # resident (CORROBORATED, inference doc sections 4 and 7 item 1)
        self.img = st.kl1_wcs
        # the tag-dispatch RAM: sysinit's KL1 table at 5300, [column][tag]
        self.tgt = pu_sysinit.tgt(st, TGT_KL1)
        self.tdar = None        # (cycle, byte) the last case_tag_setup selected
        self.cond_cycle = None  # the cycle whose word formed COND
        self.an = {}            # the An/Xn register file (RF, 32 words): pimm.py reg[]
        self.r = {}             # WRBF clear, selects 01-07, 0c-1f: R01 .. R1f
        self.w = {}             # WRBF set: W00 .. W1f
        self.wr = {XR: None, 'YR': None, MAR1: None, MAR2: None, MDR1: None, MDR2: None}
        self.mem = {}
        self.mstk = []
        self.cond = None        # COND, set by the previous word (None = not formed)
        self.flags = {}         # FLAG_CONDS' hardware flags, set by a harness (OURS)
        self.mcf_log = []       # (upc, EM1) of each MCF_UNKNOWN operation executed
        self.alf = None         # the set_alf latch (MCF_NAMED 01, ALF_CONDS)
        self.ir = None          # the KL1-B instruction (tag, value) in the E stage
        self.pc = None          # its address (the A stage's, OURS: set by a harness)
        self.ir_c8 = False      # the instruction's constant is c8 (setup.IR_C8)
        self.trace = []         # (upc, word)
        self.writes = []        # (upc, address, (tag, value))
        self.cycles = []        # one record per microcycle (README "Trace format")
        self._reads = []
        for z in RULES['zero_regs']:
            self.r[z] = (0, 0)

    # -- operand fields of the instruction in the E stage
    def ir_field(self, which):
        t, v = self.ir
        return {'op': (v >> 24) & 31, 'x': (v >> 16) & 255, 'y': (v >> 8) & 255,
                'z': v & 255}[which]

    def sel_name(self, x, sel):
        if bit(x, mekbn.WRB_BIT):
            if sel == 0xd and RULES['wsel_d_em1']:
                # RULES['wsel_d_em1']: the register-file entry R(10 | EM1)
                if field(x, 'EM1') > 0xf or em1_other_use(x):
                    raise Unmodelled(self._upc, 'select d (WRBF) with EM1 %02x: not decided'
                                     ' (EM1 over f, or used by another field)' % field(x, 'EM1'))
                return ('R', 0x10 | field(x, 'EM1'))
            return ('W', sel)
        opd = RULES['opd_fields']
        if sel in opd:
            return ('A', self.ir_field(opd[sel]))
        return ('R', sel)

    def read_sel(self, upc, x, sel, bus=1):
        if sel == 0 and not bit(x, mekbn.WRB_BIT):
            return (0, 0)
        imm = (S1_IMM if bus == 1 else S2_IMM).get(sel) if EM_IMM else None
        if imm and not bit(x, mekbn.WRB_BIT):
            # an EM-field immediate on the bus (S1_IMM / S2_IMM, rassy)
            v = (0, field(x, imm))
            self._reads.append((imm, v))
            return v
        f, n = self.sel_name(x, sel)
        store = {'W': self.w, 'A': self.an, 'R': self.r}[f]
        if n not in store:
            raise Unmodelled(upc, 'read of %s%02x, never set' % (f, n))
        self._reads.append(('%s%02x' % (f, n), store[n]))
        return store[n]

    def ir_s2(self, upc, x=None):
        """The IR field SC2F 1 puts on the S2 bus (RULES['sc2f1_ir'])."""
        if self.ir is None:
            raise Unmodelled(upc, 'SC2F 1: no instruction in IR')
        if RULES['sc2f1_ir'] == 'ext_ir':
            # rassy ext_ir/2 (@2e72): EM2 & 15 names the field (EXT_IR)
            shift, width, signed = EXT_IR[field(x, 'EM2') & 15]
            v = self.ir[1] >> shift & ((1 << width) - 1)
            if signed and v >> (width - 1):
                v -= 1 << width
            self._reads.append(('IR', (0, v & M32)))
            return (0, v & M32)
        v = self.ir[1] & 0xffff
        if self.ir_c8 and (v >> 8) & 255:
            raise Unmodelled(upc, 'SC2F 1: IR field width UNKNOWN (c8 %d, c16 %d differ)'
                             % (v & 255, v))
        self._reads.append(('IR', (0, v)))
        return (0, (v - 0x10000 if v & 0x8000 else v) & M32)

    def write_sel(self, x, sel, v, out):
        if sel == 0xc and not bit(x, mekbn.WRB_BIT) and RULES['dstf_c_rfar']:
            rfar = self.r.get(6)
            if rfar is None or is_stale(rfar):
                raise Unmodelled(self._upc, 'DSTF c (++ rfar) with RFAR unset')
            out.append((('A', rfar[1]), v))
            out.append((('R', 6), (rfar[0], rfar[1] + 1)))
            return
        out.append((self.sel_name(x, sel), v))

    def stamp_tag(self, x):
        t = field(x, 'TGIF')
        if t == 3:
            return field(x, 'EM2') if RULES['tgif3_tag'] == 'EM2' else field(x, 'EM1')
        return field(x, 'EM1')

    def imm2(self, upc, x, sc2):
        if sc2 == mekbn.SC2_EM1:
            return (0, field(x, 'EM1'))
        if sc2 == mekbn.SC2_EM2:
            return (0, field(x, 'EM2'))
        if sc2 == mekbn.SC2_WIDE and RULES['sc2_wide'] == 'EM2:EM3':
            if field(x, 'EM1') and field(x, 'TGIF') not in (1, 2) \
                    and not (RULES['sc2_wide_mcf'] and bit(x, 18)):
                raise Unmodelled(upc, 'SC2F b with EM1 %02x not a stamp (width UNKNOWN)'
                                 % field(x, 'EM1'))
            return (0, field(x, 'EM') & 0x3ff)
        if sc2 == mekbn.SC2_WIDE and RULES['sc2_wide'] == 'EM1:EM2':
            return (0, field(x, 'EM') >> 4)         # injection only
        raise Unmodelled(upc, 'SC2F %x immediate' % sc2)

    def alu(self, upc, x, old):
        as1, as2 = mekbn.alu_in(x)
        if RULES['alu_sources'] == 'rassy':
            return self._alu_values(upc, x, *self.alu_pair(upc, x, old))
        a = {0: (0, 0), XR: old[XR], MDR1: old[MDR1], MDR2: old[MDR2],
             MAR1: old[MAR1], MAR2: old[MAR2]}.get(as1, 'open')
        if as1 == 3 and as2 == 0 and RULES['as1f3_em2']:
            a = (0, field(x, 'EM2'))
        if as1 == 2 and RULES['as1f2_yr']:
            a = old['YR']
        if as1 == 3 and as2 != 0 and RULES['as1f3_open_unknown']:
            self.as1_seen = UNKNOWN
            self.alu_seen = (UNKNOWN, None, UNKNOWN)
            return UNKNOWN
        if a == 'open':
            raise Unmodelled(upc, 'AS1F %d' % as1)
        b = {0: (0, 0), 1: old['YR'], 2: old[MDR1], 3: old[MDR2]}[as2]
        return self._alu_values(upc, x, a, b, as1 and as1 != 3)

    def alu_const(self, upc, x):
        """The ALU constant of an AS1F 2 / AS1F 3 (AS2F 0-1) word
        (RULES['alu_sources'] 'rassy'): EM2, or EM1 when EM2 is in use."""
        if RULES['alu_const'] == 'EM3':                 # injection only
            return (0, field(x, 'EM3'))
        if not em2_busy(x):
            return (0, field(x, 'EM2'))
        if em1_busy(x):
            raise Unmodelled(upc, 'ALU constant: EM1 and EM2 both in use (field UNKNOWN)')
        return (0, field(x, 'EM1'))

    def alu_pair(self, upc, x, old):
        """(AS1 input, AS2 input, the result tag is AS1's) by rassy's
        as1f_and_as2f/6 (RULES['alu_sources'], above)."""
        as1, as2 = mekbn.alu_in(x)
        reg = {XR: old[XR], MDR1: old[MDR1], MDR2: old[MDR2], MAR1: old[MAR1],
               MAR2: old[MAR2]}
        if as1 == 2:
            return reg[(MDR1, MDR2, MAR1, MAR2)[as2]], self.alu_const(upc, x), True
        if as1 == 3:
            if as2 == 0:
                return (0, 0), self.alu_const(upc, x), False
            if as2 == 1:
                return old[XR], self.alu_const(upc, x), True
            if not RULES['as1f3_mar_xr']:               # injection: the old UNKNOWN
                self.as1_seen = UNKNOWN
                self.alu_seen = (UNKNOWN, None, UNKNOWN)
                return UNKNOWN, None, None
            return reg[(MAR1, MAR2)[as2 - 2]], old[XR], True
        a = (0, 0) if as1 == 0 else reg[as1]
        b = {0: (0, 0), 1: old['YR'], 2: old[MDR1], 3: old[MDR2]}[as2]
        return a, b, as1 != 0

    def _alu_values(self, upc, x, a, b, tag_a):
        if a is UNKNOWN:
            return UNKNOWN
        as1, as2 = mekbn.alu_in(x)
        if is_poison(a) or is_poison(b):
            raise Unmodelled(upc, 'ALU input from a read of memory never written'
                             ' (AS1F %d, AS2F %d)' % (as1, as2))
        if a is None or b is None:
            raise Unmodelled(upc, 'ALU input never set (AS1F %d, AS2F %d)' % (as1, as2))
        if is_stale(a) or is_stale(b):
            # a value the harness does not know: the result is not known
            # either (STALE); a COND formed from it is STALE too (evaluate)
            self.as1_seen = a
            self.alu_seen = (a, b, STALE)
            return STALE
        self.as1_seen = a
        self.alu_seen = (a, b, None)
        alf = field(x, 'ALF')
        mrb = RULES['em2_mrb'].get(field(x, 'EM2')) if alf in (2, 3) and RULES['em2_mrb'] else None
        if mrb:
            # MRB off / on (RULES['em2_mrb']): the AS1 input, tag bit 0 set or cleared
            self.alu_seen = (a, b, a[1])
            t = a[0] & ~1 if mrb == 'off' else a[0] | 1
            if field(x, 'TGIF') & 2:
                raise Unmodelled(upc, 'MRB %s with a TGIF stamp' % mrb)
            return (t, a[1] & M32)
        if alf == 0:
            v = a[1] + b[1]
        elif alf == 1:
            v = a[1] - b[1]
        else:
            op = mekbn.alu_op(x)
            if op == 'pass_as2':
                v = b[1]
            elif op == 'and':
                v = a[1] & b[1]
            elif op == 'or':
                v = a[1] | b[1]
            elif op == 'xor':
                v = a[1] ^ b[1]
            elif op == 'add_with_one' and RULES['alu_with_one']:
                v = a[1] + b[1] + (RULES['alu_with_one'] != 'plain')
            else:
                raise Unmodelled(upc, 'ALU operation %s' % op)
        self.alu_seen = (a, b, v)
        tag = a[0] if tag_a else b[0]
        if field(x, 'TGIF') & 2:
            tag = self.stamp_tag(x)
        return (tag, v & M32)

    def deref_code(self, upc, x):
        """The dereference multiway code (DEREF_SETUP, thesis p.133) of
        the AS1 input's tag.  Only 'other' is executed; the others raise."""
        if self.as1_seen is None:
            raise Unmodelled(upc, 'dereference set-up with no ALU input')
        if is_stale(self.as1_seen):
            raise Unmodelled(upc, 'dereference set-up on a value the harness does not know')
        t = self.as1_seen[0] & 63
        if DEREF_TGT_COLUMN is not None:       # injection only: a TGT column instead
            return self.tgt[DEREF_TGT_COLUMN][t]
        imm = field(x, 'EM2')
        if t & ~1 == REF:
            kind = 'refo' if t == REF else 'refx'
        elif t & ~1 == imm & ~1:
            kind = 'imm'
        else:
            kind = 'other'
        if kind != 'other' and DEREF_CODE == {'imm': 0, 'other': 1, 'refo': 2, 'refx': 3}:
            raise Unmodelled(upc, 'dereference set-up EM1 %02x: tag %02x takes the %s row'
                             ' (read, not run)' % (field(x, 'EM1'), t, kind))
        return DEREF_CODE[kind]

    def _tdar_reaches(self, tdar, cycle):
        """Does the E-stage set-up tdar still stand for a case_branch at
        cycle?  The word just before, or (RULES['tdar_holds']) an earlier
        one with only JMPF 1 words (which form nothing) in between."""
        if tdar[0] == 'S':
            return False
        if tdar[0] == cycle - 1:
            return True
        if not RULES['tdar_holds'] or tdar[0] >= cycle:
            return False
        return all(mekbn.jk(w) == 1 for _, w in self.trace[tdar[0] + 1:cycle])

    def step(self, upc):
        """One microcycle: evaluate every operation of the word at upc from
        the OLD state, then commit them together.  Returns the next upc,
        or None at the end of the machine instruction."""
        cyc = self.evaluate(upc)
        self.commit(cyc)
        return cyc['next']

    def evaluate(self, upc):
        """The microcycle's effects, as a record (TRACE FORMAT in README):
        nothing in the machine state changes here.  Any field value the
        simulator does not model raises Unmodelled(upc, field)."""
        if upc >= len(self.img):
            raise Unmodelled(upc, 'micro_pc outside the control store')
        if upc == TRAP_ILLEGAL:
            raise Trap(upc, 'illegal-instruction trap')
        x = self.img[upc]
        if not x:
            raise Unmodelled(upc, 'zero microinstruction')
        self._upc = upc
        self._lc_dec = bool(bit(x, 18)) and field(x, 'EM1') == 0x10
        self._reads = []
        old = dict(self.wr)
        new = {}            # phase-2 register -> value
        regw = []           # phase-1 register-file writes ((file, n), value)
        memw, memr = [], []
        if bit(x, 63):
            raise Unmodelled(upc, 'DBGF set')
        # phase 1: S1 bus (SC1F -> SD1F), S2 bus (SC2F -> SD2F)
        sc1, sd1 = field(x, 'SC1F'), field(x, 'SD1F')
        self.s1_seen = None
        if sd1:
            pair = RULES['sd1_pairs'].get(sd1) if RULES['sd1_pairs'] else None
            if sd1 not in WNAME and not pair:
                raise Unmodelled(upc, 'SD1F %d' % sd1)
            v = self.s1_seen = self.read_sel(upc, x, sc1)
            if field(x, 'TGIF') & 1 and not is_stale(v):
                v = (self.stamp_tag(x), v[1])
            for r in pair or (sd1,):
                new[r] = v
        elif field(x, 'CNDF') in (8, 0xa, 0xc) and cndf_free(x) and RULES['cnd8_s1']:
            # the S1 bus read for the condition alone ('read X', RULES['cnd8_s1'])
            self.s1_seen = self.read_sel(upc, x, sc1)
        sc2, sd2 = field(x, 'SC2F'), field(x, 'SD2F')
        if sd2:
            if sc2 in (mekbn.SC2_EM1, mekbn.SC2_EM2, mekbn.SC2_WIDE):
                v = self.imm2(upc, x, sc2)
            elif sc2 == 1 and RULES['sc2f1_ir'] and (RULES['sc2f1_ir'] == 'ext_ir'
                                                or not bit(x, mekbn.WRB_BIT)):
                v = self.ir_s2(upc, x)
            else:
                v = self.read_sel(upc, x, sc2, bus=2)
            d = {1: 'YR', 2: MDR1, 3: MDR2}[sd2]
            if d in new:
                raise Unmodelled(upc, 'SD1F and SD2F load one register')
            new[d] = v
        # phase 2: the ALU, to ADF and DSTF
        dst, d = field(x, 'ADF'), field(x, 'DSTF')
        res = None
        self.as1_seen = None
        self.alu_seen = None
        if dst or d or field(x, 'ALF') or field(x, 'AS1F') or field(x, 'AS2F'):
            res = self.alu(upc, x, old)
            if res is UNKNOWN and (dst or d):
                raise Unmodelled(upc, 'AS1F %d with AS2F %d: the result is written, its'
                                 ' source not decided' % mekbn.alu_in(x))
            if dst:
                if dst not in WNAME:
                    raise Unmodelled(upc, 'ADF %d' % dst)
                if dst in new:
                    raise Unmodelled(upc, 'ADF and a bus load one register (%s)' % WNAME[dst])
                new[dst] = res
            if d:
                self.write_sel(x, d, res, regw)
        # MCF
        mcf = None
        flagw = {}          # MCF_FLAG_OPS: flag -> value, committed with the word
        alf = self.alf
        if bit(x, 18):
            if field(x, 'EM1') in MCF_FLAG_OPS:
                name, val = MCF_FLAG_OPS[field(x, 'EM1')]
                flagw[name] = val
                mcf = field(x, 'EM1')
            elif field(x, 'EM1') == 0x01 and 0x01 in MCF_NAMED:
                # set_alf: latch this word's ALU flags (ALF_CONDS reads them)
                if self.alu_seen is None:
                    raise Unmodelled(upc, 'MCF set_alf with no ALU operation')
                alf = POISON if self.alu_seen[2] is UNKNOWN else self.alu_seen
                mcf = 0x01
            elif field(x, 'EM1') == 0x10 and RULES['lc_ops']:
                lc = self.r.get(3)
                if lc is None or is_stale(lc):
                    raise Unmodelled(upc, 'MCF -- lc with R03 unset or not known')
                regw.append((('R', 3), (lc[0], (lc[1] - 1) & M32)))
                mcf = 0x10
            elif (field(x, 'EM1'), field(x, 'EM2') & 0x1f) in MCF_SUB_FLAGS \
                    and RULES['mcf_sub_flags']:
                name, val = MCF_SUB_FLAGS[(field(x, 'EM1'), field(x, 'EM2') & 0x1f)]
                flagw[name] = val
                mcf = field(x, 'EM1')
            elif (field(x, 'EM1'), field(x, 'EM2') & 0x1f) in MCF_SUB:
                mcf = field(x, 'EM1')       # recorded only (MCF_SUB)
            elif field(x, 'EM1') == 0x20 and RULES['mcf_20_sp']:
                sp = self.r.get(2)
                if sp is None or is_stale(sp):
                    raise Unmodelled(upc, 'MCF 20 with R02 unset or not known')
                regw.append((('R', 2), (sp[0], (sp[1] + 1) & M32)))
            elif field(x, 'EM1') in MCF_UNKNOWN or field(x, 'EM1') in MCF_NAMED:
                mcf = field(x, 'EM1')       # recorded only (MCF_UNKNOWN, MCF_NAMED)
            else:
                raise Unmodelled(upc, 'MCF with EM1 %02x' % field(x, 'EM1'))
        # memory (CCF): bit 61 read, 62 write, 60 step; 58 MAR2, 59 MDR2
        rd, wr = bit(x, mekbn.RD_BIT), bit(x, mekbn.MEM_BIT)
        step = bit(x, mekbn.INC_BIT)
        mar = MAR2 if bit(x, mekbn.MAR_SEL_BIT) else MAR1
        mdr = MDR2 if bit(x, mekbn.MDR_SEL_BIT) else MDR1
        if RULES['ccf_rassy'] and (rd or wr or step):
            op = CCF_RASSY.get(field(x, 'CCF'))
            if op is None:
                raise Unmodelled(upc, 'CCF %02x (rassy %s): not modelled'
                                 % (field(x, 'CCF'), CCF_NAMES.get(field(x, 'CCF'), '?')))
            k, mar, mdr, step = op
            rd, wr = k == 'read', k == 'write'
            if k == 'cancel':
                # what 'cancel' leaves in MAR2 / MDR2 (the bit reading's
                # read ++ mar2 mdr2) is not known: STALE, so a path that
                # depends on it fails loud
                for r in (MAR2, MDR2):
                    if r not in new:
                        new[r] = STALE
        if rd or wr:
            if old[mar] is None:
                raise Unmodelled(upc, 'CCF: %s never set' % WNAME[mar])
            if is_stale(old[mar]):
                raise Unmodelled(upc, 'CCF: %s holds a value the harness does not know (STALE)'
                                 % WNAME[mar])
            addr = old[mar][1]
            if rd and wr:
                raise Unmodelled(upc, 'CCF %02x: read and write in one word' % field(x, 'CCF'))
            if wr:
                if mdr == MDR2 and not RULES['w59_mdr2']:
                    raise Unmodelled(upc, 'CCF %02x: write data register' % field(x, 'CCF'))
                if mdr == MDR2 and RULES['w59_mdr2'] == 'MDR1':
                    mdr = MDR1          # injection only
                data = old[mdr] if RULES['write_old_mdr'] else {**old, **new}[mdr]
                if data is None:
                    raise Unmodelled(upc, 'CCF: write of %s, never set' % WNAME[mdr])
                if is_poison(data):
                    raise Unmodelled(upc, 'CCF: write of %s, read from memory never written'
                                     % WNAME[mdr])
                if is_stale(data):
                    raise Unmodelled(upc, 'CCF: write of %s, a value the harness does not know'
                                     ' (STALE)' % WNAME[mdr])
                memw.append((addr, data))
            if rd:
                if addr not in self.mem and not RULES['absent_read_poison']:
                    raise Unmodelled(upc, 'CCF: read of memory %x, never written' % addr)
                if mdr in new:
                    raise Unmodelled(upc, 'CCF: read data and a load meet in %s' % WNAME[mdr])
                new[mdr] = self.mem.get(addr, POISON)
                memr.append((addr, new[mdr]))
            if step:
                if mar in new:
                    raise Unmodelled(upc, 'CCF: step and a load meet in %s' % WNAME[mar])
                new[mar] = (old[mar][0], (addr + 1) & M32)
        elif step:
            raise Unmodelled(upc, 'CCF: bit 60 without a strobe')
        # condition generation (from the old state) and use
        kind, target, falls = flow(upc, x)
        # flow()'s third item is "can fall through": for a jump, end or
        # return that is "conditional"; a call returns, a branch is
        # conditional by kind
        conditional = falls if kind in ('jump', 'end', 'return') else kind == 'branch'
        jf, cnd, em = field(x, 'JMPF'), field(x, 'CNDF'), field(x, 'EM')
        prev_cond = self.cond
        old_r3 = self.r.get(3)
        cond_new, cond_cycle = prev_cond, self.cond_cycle
        tdar = self.tdar
        cycle = len(self.trace)
        em1 = field(x, 'EM1')
        if cnd == 7 and CASE_TAG_SETUP and 0x30 <= em1 <= 0x3f and cndf_free(x):
            # case_tag_setup mdr1 / mdr2 k (CASE_TAG_SETUP): the TGT byte of
            # the named MDR's tag (old value), column 7 - k
            if mekbn.jk(x) == 5 or jf in (9, 0xd):
                raise Unmodelled(upc, 'case_tag_setup in a JMPF %x word (EM1 not free)' % jf)
            src = old[CTS_MDR[em1 & 1]] if CTS_SOURCE == 'mdr' else self.as1_seen
            if src is None or is_poison(src) or is_stale(src) or src is UNKNOWN:
                raise Unmodelled(upc, 'case_tag_setup on %s: %r' % (
                    WNAME[CTS_MDR[em1 & 1]] if CTS_SOURCE == 'mdr' else 'the AS1 input', src))
            tdar = (cycle, self.tgt[CTS_COLUMN((em1 - 0x30) >> 1)][src[0] & 63])
        elif cnd == 7 and cndf_free(x) and em1 in ALF_CONDS:
            # 'cond alf_*' on the set_alf latch (ALF_CONDS, ALF_LATCHED)
            if self.alf is None:
                raise Unmodelled(upc, 'CNDF 7 EM1 %02x (%s): no set_alf latch'
                                 % (em1, ALF_CONDS[em1]))
            cond_new, cond_cycle = alf_cond(self.alf, ALF_CONDS[em1]), cycle
        elif cnd == 7 and cndf_free(x) and em1 == 0x0d and RULES['lc_ops']:
            cond_new, cond_cycle = lc_cond(self, upc, 0, old_r3), cycle      # lc_zero
        elif cnd == 6 and cndf_free(x) and RULES['lc_ops']:
            cond_new, cond_cycle = lc_cond(self, upc, 1, old_r3), cycle      # lc_one
        elif cnd == 7 and mekbn.jk(x) == 0 and field(x, 'EM1') in TGT_COLUMN:
            # case_tag_setup (thesis p.131): the TGT byte of the tag of
            # the ALU's first input, column by EM1 (only 3a -> 2 VERIFIED)
            if self.as1_seen is None:
                raise Unmodelled(upc, 'case_tag_setup with no ALU input')
            if is_stale(self.as1_seen):
                raise Unmodelled(upc, 'case_tag_setup on a value the harness does not know')
            col = TGT_COLUMN[field(x, 'EM1')]
            tdar = (cycle, self.tgt[col][self.as1_seen[0] & 63])
        elif cnd == 7 and mekbn.jk(x) == 0 and field(x, 'EM1') in DEREF_SETUP:
            tdar = (cycle, self.deref_code(upc, x) << DEREF_SHIFT)
        elif cnd == 7 and mekbn.jk(x) == 0 and field(x, 'EM1') in COND_UNKNOWN:
            cond_new, cond_cycle = POISON, cycle
        elif cnd == 7 and cndf_free(x) and field(x, 'EM1') in FLAG_CONDS:
            # a hardware flag (FLAG_CONDS, INFERRED); its value is the harness's
            name = FLAG_CONDS[field(x, 'EM1')]
            if name not in self.flags:
                raise Unmodelled(upc, 'CNDF 7 EM1 %02x: flag %s, value not given'
                                 % (field(x, 'EM1'), name))
            cond_new, cond_cycle = bool(self.flags[name]), cycle
        elif cnd == 7 and mekbn.jk(x) == 0 and field(x, 'EM1') not in (0x09, 0x0a, 0x29):
            raise Unmodelled(upc, 'CNDF 7 EM1 %02x: TGT column or condition UNKNOWN'
                             % field(x, 'EM1'))
        elif cnd and cndf_free(x):
            rule = COND_RULES.get(cnd)
            if rule is None:
                raise Unmodelled(upc, 'CNDF %x (condition not known)' % cnd)
            if self.alu_seen and self.alu_seen[2] is UNKNOWN:
                cond_new, cond_cycle = POISON, cycle    # RULES['as1f3_open_unknown']
            elif is_stale(self.as1_seen) or (self.alu_seen and is_stale(self.alu_seen[2])):
                cond_new, cond_cycle = STALE, cycle     # formed from a value not known
            else:
                cond_new, cond_cycle = rule(self, upc, x, self.as1_seen), cycle
        # sequencing
        if kind == 'jmpf2':
            # case_branch, short base (RULES['jmpf2_case'], INFERRED)
            if not RULES['jmpf2_case']:
                raise Unmodelled(upc, 'JMPF 2 (4-bit; kind not known)')
            d = field(x, 'EM3')
            base = upc + (d - 16 if RULES['jmpf2_case'] == 'signed' and d >= 8 else d)
            if tdar is None or (tdar[0] != 'S' and tdar[0] != cycle - 1):
                raise Unmodelled(upc, 'JMPF 2 case_branch without a set-up (S stage or the'
                                 ' word before)')
            if base & 15 & tdar[1] or tdar[1] > 15:
                raise Unmodelled(upc, 'JMPF 2 case_branch base %04x with TDAR %02x'
                                 % (base, tdar[1]))
            kind, target, falls = 'jump', base | tdar[1], False
            conditional = False
        if jf == 8 and RULES['jmpf8_setup'] and cnd == 7 and field(x, 'EM1') in DEREF_SETUP:
            pass                        # sequences as JMPF 0 (RULES['jmpf8_setup'])
        elif jf == 8 and RULES['jmpf8_flag'] and cnd == 7 and field(x, 'EM1') in FLAG_CONDS:
            pass                        # sequences as JMPF 0 (RULES['jmpf8_flag'])
        elif jf == 9 and RULES['jmpf9_call_if']:
            # a conditional call, "if cond" (RULES['jmpf9_call_if']); only
            # the arm not taken is modelled
            if prev_cond is None or is_poison(prev_cond) or is_stale(prev_cond):
                raise Unmodelled(upc, 'JMPF 9 conditional call with no usable condition')
            if bool(prev_cond):
                if not RULES['jmpf9_vlong']:
                    raise Unmodelled(upc, 'JMPF 9 conditional call taken (target reading not'
                                     ' decided)')
                kind, target, conditional = 'call', em, False   # RULES['jmpf9_vlong']
            else:
                kind, conditional = 'next', False
        elif jf == 0xf and RULES['jmpf_f_call_ifnot']:
            # rassy jmpf/9 arm f: 'call', long (page-relative), 'if not cond'
            if prev_cond is None or is_poison(prev_cond) or is_stale(prev_cond):
                raise Unmodelled(upc, 'JMPF f conditional call with no usable condition')
            if bool(prev_cond):
                kind, conditional = 'next', False
            else:
                kind, target, conditional = 'call', upc & ~0x3ff | em & 0x3ff, False
        elif jf == 8 and RULES['jmpf8_goto_if'] and not cnd:
            # rassy jmpf/9 arm 8: 'goto' short 'if cond' (RULES['jmpf8_goto_if'])
            if prev_cond is None or is_poison(prev_cond) or is_stale(prev_cond):
                raise Unmodelled(upc, 'JMPF 8 conditional goto with no usable condition')
            if bool(prev_cond):
                d = field(x, 'EM3')
                kind, target = 'jump', upc + (d - 16 if mekbn.J4_SIGNED and d >= 8 else d)
            else:
                kind = 'next'
            conditional = False
        elif jf in (8, 9, 0xd, 0xf):
            raise Unmodelled(upc, 'JMPF %x (bit 26 with this kind not decided)' % jf)
        if mekbn.jk(x) == 1 and em == SPECIAL_EM:
            raise Unmodelled(upc, 'JMPF 1 EM 7fff (S9, special form UNKNOWN)')
        cj_taken = None
        if kind == 'branch' or (jf & 8 and mekbn.jk(x) in (3, 4, 6)):
            # conditional JMPF a / b / c / e: RULES['cjump_time'] and
            # CJUMP_TAKEN_ON (INFERRED; only b executed)
            if RULES['cjump_time'] is None:
                raise Unmodelled(upc, 'JMPF %x conditional: timing UNKNOWN' % jf)
            if jf not in CJUMP_TAKEN_ON:
                raise Unmodelled(upc, 'JMPF %x conditional: polarity not decided' % jf)
            tested = prev_cond if RULES['cjump_time'] == 'prev' else cond_new
            if tested is None:
                raise Unmodelled(upc, 'JMPF %x conditional with no condition formed' % jf)
            if is_poison(tested):
                raise Unmodelled(upc, 'JMPF %x conditional tests a condition of UNKNOWN'
                                 ' meaning (COND_UNKNOWN)' % jf)
            if is_stale(tested):
                raise Unmodelled(upc, 'JMPF %x conditional tests a condition formed from a'
                                 ' value the harness does not know (STALE)' % jf)
            cj_taken = bool(tested) == CJUMP_TAKEN_ON[jf]
        if jf == 3:
            # S8 case_branch: base | the TGT byte's low 4 bits, set up by
            # the word just before (a CNDF 7, JMPF 0 word)
            if tdar is None or not self._tdar_reaches(tdar, cycle):
                raise Unmodelled(upc, 'JMPF 3 case_branch without a set-up in the word before')
            if target & (63 if RULES['case_wide'] else 15) & tdar[1]:
                raise Unmodelled(upc, 'JMPF 3 case_branch base %04x overlaps TDAR %02x'
                                 % (target, tdar[1]))
            if tdar[1] > 15 and not RULES['case_wide']:
                raise Unmodelled(upc, 'JMPF 3 TGT byte %02x over 15' % tdar[1])
            target |= tdar[1] & 15 if RULES['case_wide'] == 'low4' else tdar[1]
        if jf == 0xb and RULES['jmpf_b_call'] and kind == 'jump':
            kind = 'call'               # RULES['jmpf_b_call']: taken, it pushes upc + 1
        if mekbn.jk(x) in (3, 4, 6):
            if not RULES['bit26_cond']:
                raise Unmodelled(upc, 'JMPF %x (bit 26 rule off)' % jf)
            if jf & 8 and cj_taken is None:
                raise Unmodelled(upc, 'JMPF %x conditional jump (polarity not decided)' % jf)
            conditional = False
        if kind == 'branch' and cj_taken is not None:
            # JMPF a, a conditional page-relative goto (CJUMP_TAKEN_ON)
            kind, conditional = 'jump', False
        taken = True if cj_taken is None else cj_taken
        if mekbn.jk(x) == 1 and kind in ('jump', 'end', 'return'):
            if kind == 'jump' and em & 4:
                # S2b: a multiway, low target bits ORed in at run time
                # from a source not identified (INFERRED, inference doc 2.2)
                raise Unmodelled(upc, 'JMPF 1 EM bit 2: multiway, low-bit source UNKNOWN')
            if conditional:
                if em & 1 and not RULES['j1_bit0_false']:
                    raise Unmodelled(upc, 'JMPF 1 conditional with EM bit 0 set (rule off)')
                if not em & 1 and not RULES['j1_bit0_clear_true']:
                    raise Unmodelled(upc, 'JMPF 1 conditional with EM bit 0 clear')
                if prev_cond is None:
                    raise Unmodelled(upc, 'JMPF 1 %s? with no condition formed' % kind)
                if is_poison(prev_cond):
                    raise Unmodelled(upc, 'JMPF 1 %s? tests a condition of UNKNOWN meaning'
                                     ' (COND_UNKNOWN)' % kind)
                if is_stale(prev_cond):
                    raise Unmodelled(upc, 'JMPF 1 %s? tests a condition formed from a value'
                                     ' the harness does not know (STALE)' % kind)
                if RULES['j1_cond_prev_strict'] and self.cond_cycle != cycle - 1:
                    raise Unmodelled(upc, 'JMPF 1 %s?: COND not formed by the previous word' % kind)
                taken = not prev_cond if em & 1 else bool(prev_cond)
            elif em & 1:
                raise Unmodelled(upc, 'JMPF 1 %s with EM bit 0' % kind)
        elif conditional:
            raise Unmodelled(upc, 'conditional %s (not decided)' % kind)
        push = pop = False
        if not taken:
            nxt = upc + 1               # the other arm is the next word
        elif kind == 'next':
            nxt = upc + 1
        elif kind == 'jump':
            nxt = target
        elif kind == 'call':
            nxt, push = target, True
        elif kind == 'return':
            if not self.mstk:
                raise Unmodelled(upc, 'JMPF 1 return with an empty micro stack')
            nxt, pop = self.mstk[-1], True
        elif kind == 'end':
            nxt = None
        else:
            raise Unmodelled(upc, 'flow kind %s' % kind)
        return {'cycle': len(self.trace), 'micro_pc': upc, 'microword': x,
                'reg_reads': list(self._reads), 'wr': new, 'reg_writes': regw,
                'mem_reads': memr, 'mem_writes': memw,
                'cond': cond_new, 'cond_cycle': cond_cycle, 'tdar': tdar, 'mcf': mcf,
                'flags': flagw, 'alf': alf,
                'push': upc + 1 if push else None, 'pop': pop,
                'next': nxt}

    def commit(self, c):
        """All of a microcycle's state changes at once."""
        self.wr.update(c['wr'])
        for (f, n), v in c['reg_writes']:
            {'W': self.w, 'A': self.an, 'R': self.r}[f][n] = v
        for a, d in c['mem_writes']:
            self.mem[a] = d
            self.writes.append((c['micro_pc'], a, d))
        self.cond, self.cond_cycle, self.tdar = c['cond'], c['cond_cycle'], c['tdar']
        self.flags.update(c.get('flags') or {})
        if 'alf' in c:
            self.alf = c['alf']
        if c.get('mcf') is not None:
            self.mcf_log.append((c['micro_pc'], c['mcf']))
        if c['push'] is not None:
            self.mstk.append(c['push'])
        if c['pop']:
            self.mstk.pop()
        self.trace.append((c['micro_pc'], c['microword']))
        self.cycles.append(c)
        return c['next']

    def call(self, upc, limit=2000):
        """Run a microsubroutine from upc to its return, as a call word
        would (sub-rung "the allocator": 3320)."""
        self.mstk.append(-1)
        n0 = len(self.trace)
        try:
            while upc != -1:
                if upc is None:
                    raise Unmodelled(self.trace[-1][0], 'end inside a microsubroutine')
                if len(self.trace) - n0 >= limit:
                    raise Unmodelled(upc, 'micro step limit')
                upc = self.step(upc)
        except Unmodelled as e:
            e.words = len(self.trace) - n0
            raise
        return len(self.trace) - n0

    def run(self, upc, limit=2000):
        """Run from upc to the end of the machine instruction."""
        n0 = len(self.trace)
        try:
            while upc is not None:
                if len(self.trace) - n0 >= limit:
                    raise Unmodelled(upc, 'micro step limit')
                upc = self.step(upc)
        except Unmodelled as e:
            # held words completed (committed) before the stop
            e.words = len(self.trace) - n0
            raise
        if self.mstk:
            raise Unmodelled(self.trace[-1][0], 'end with %d return(s) pending' % len(self.mstk))
        return len(self.trace) - n0
