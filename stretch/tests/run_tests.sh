#!/bin/sh
# run_tests.sh -- the full regression suite: the hand-assembled BSV smoke
# test plus every STRAP program in ../decks/ that has a verified expected
# result. Exists because these invocations (and, for Figure 7, the
# expected-result derivation) previously lived only in conversation
# scrollback and had to be reconstructed from scratch more than once --
# see strap/README.md "Gotchas" item 7's postscript.
#
# Usage: ./run_tests.sh          (from stretch/strap/)

set -e
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
# The assembler lives in ../strap now; the verifiers and
# generators import it by module name.
PYTHONPATH="$TESTS_DIR/../strap:$TESTS_DIR"; export PYTHONPATH
BSV_DIR="$TESTS_DIR/../bsv"
TMPOUT="$(mktemp)"
trap 'rm -f "$TMPOUT"' EXIT

FAILED=0

# A LINE CONTINUATION MUST BE A SINGLE BACKSLASH.  "\\" at end of line
# is an ESCAPED backslash: the command ends there and the next line
# becomes its own command ("PC=4239: command not found").  sh -n
# accepts it, and so does a check that just counts the arguments `run`
# receives -- both the correct and the broken form pass five, because
# the stray backslash IS the fifth.  That check was written to catch
# this exact bug and could not see it.  This one looks at the file.
if grep -qE '\\\\$' "$0"; then
  echo "refusing to run: a line in $0 ends in a doubled backslash," >&2
  grep -nE '\\\\$' "$0" >&2
  echo "which splits that command in two at runtime." >&2
  exit 2
fi

run() {
  # run NAME -- prints a header, runs "$@", tracks pass/fail without
  # aborting the whole suite on one failure. Deliberately NOT
  # `"$@" | tee ... | tail`: a pipeline's exit status is its last
  # stage's (tail's), which is ~always 0, so piping would silently
  # swallow a real build/toolchain failure (bsc erroring out,
  # strap_asm.py raising) as a "pass" with no PASS/FAIL lines at all --
  # caught by advisor review, which is also how the *previous* version
  # of this function was caught running the smoke test in a subshell,
  # discarding `FAILED=1` set there when the subshell exited (verified
  # fixed by deliberately breaking StretchSmoke.bsv's own check and
  # confirming this function reports it).
  name="$1"; shift
  echo "=== $name ==="
  status=0
  "$@" > "$TMPOUT" 2>&1 || status=$?
  tail -20 "$TMPOUT"
  if [ "$status" -ne 0 ] || grep -q "TEST(S) FAILED" "$TMPOUT"; then
    FAILED=1
    # FAIL_FAST=1 stops at the first failing section instead of running
    # the whole suite.  Default OFF, so an ordinary run still reports
    # EVERY failure -- which is what you want when judging a change.
    # It exists for MUTATION SCORING (mutation_score.py): a mutant that
    # the suite catches should cost seconds, not the full ~13 minutes,
    # and only SURVIVORS need a complete run.  Never use it to decide
    # whether a change is good; one failure is not the failure list.
    if [ -n "$FAIL_FAST" ]; then
      echo "FAIL_FAST: stopping at first failing section ($name)"
      exit 1
    fi
  fi
  echo
}

# -- 0. SYN pseudo-op (strap_asm.py, pure Python, no Bluesim needed --
# see test_syn.py's own header) --
run "SYN pseudo-op" python3 test_syn.py

# -- 0b. DCP Maintenance Compool transcription (SYN symbol table from
# the DCP manual, PDF pp.129-130) -- verifies every resolved symbol
# against the manual's own printed address column. Pure Python, same
# reasoning as 0 above. See verify_dcp_maintenance_compool.py's header.
run "DCP Maintenance Compool" python3 verify_dcp_maintenance_compool.py

# -- 0c. SLC pseudo-op (strap_asm.py, pure Python -- see test_slc.py) --
run "SLC pseudo-op" python3 test_slc.py

# -- 0d. I-Box 1 WEN2/WEN/VEN assembled VERBATIM at the listing's own
# octal addresses (via SLC) and compared bit-for-bit against the
# machine code printed in docs/ja_ax1a_ibox-1.pdf p.51 -- IBM's own
# STRAP output as the oracle. Pure Python, no Bluesim.
run "I-Box 1 listing bit-exact comparison" python3 verify_ibox1_listing.py

# -- 0d'. BRANCH ON BIT (BB/BB1/BBN/BBZ/BZB/BZB1/BZBN/BZBZ) encoding
# checked field-by-field against the exact bit positions StretchDecode
# reads (X22-6533 pocket card / Reference Manual p.41). Pure Python.
run "Branch-on-Bit encoding field check" python3 verify_bb_encoding.py

# -- 0d''. Branch on Bit assembled bit-for-bit against the machine code
# printed in the floating-point diagnostic jb_af1c (p.40, routine
# F202D). IBM's own STRAP output; also exercises a full-word instruction
# placed at a half-word (.40) boundary, straddling a word.
run "Branch-on-Bit listing bit-exact (jb_af1c)" python3 verify_bb_listing.py

# -- 0d'''. BB changing an INDICATOR-register bit (p.41): BB1,$AH sets
# the AH indicator, then BB,$AH branches on it. Halts at PASS iff the
# indicator write took effect (folded into `ind`, since writeWord(11)
# is a no-op). Injection (fold removed): halts at FAIL. Unblocks the
# BB1,$AH pre-set in jb_af1c's KR range-compare routine F202G.
run "Branch-on-Bit sets an indicator bit" ./run_program.sh ../decks/bb_indicator.strap StretchBBIndTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/bb_indicator.strap").read()).symtab["PASS"]//32)')"

# -- 0d''''. Store Zero to the indicator register (Z,$IND) clears bits
# 20-63 (p.41): BB1 sets AH, Z,$IND clears it, BB confirms it is off.
# Halts at PASS iff the clear took effect (folded into `ind`, since
# writeWord(11) is a no-op). Injection (fold removed): halts at FAIL.
# This is the diagnostic's own indicator reset before each test.
run "Store Zero clears the indicator register" ./run_program.sh ../decks/z_ind_clear.strap StretchZIndTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/z_ind_clear.strap").read()).symtab["PASS"]//32)')"

# -- 0d5. The index flag and RESULT indicators, for the immediate index
# operations that were not setting them.  Ref. Manual p.25, under
# SUBTRACT IMMEDIATE FROM COUNT: "The index flag and index result
# indicators are set in all of the preceding immediate index arithmetic
# operations."  That covers LVI, LVNI, LCI, LRI, C+I and C-I, none of
# which did.
#
# HAND-WRITTEN, not transcribed, and that wants saying.  C-I got its
# witness from the deck (jb_ax4b routine 1238 test 3 does C-I then
# BXCZ, and without the fix that loop never ends); LVI got one from the
# I/O test's whole-indicator-word check.  For the other four there is
# no deck witness to find: the diagnostics verify a count or value by
# COMPARING it and branching on the COMPARISON indicators, never on the
# operation's own result indicators -- jb_ax4b routine 1236, a whole
# routine "Checks C+I and C-I", is C+I then KC then BXE throughout.  So
# these four rest on the manual, and this program keeps that honest at
# the weaker of the two standards used in this suite.
#
# Measured, one injection per arm: LVNI halts at 002101.40, LCI at
# 002103.40, LRI at 002105.40, C+I at 002107.40 -- each on its own
# failure line, so the four are independent.  (The first attempt at
# those injections was INERT and reported success; see the program
# header.)  XF is not covered: every index word here has flag 0.
run "Index result indicators (LVNI, LCI, LRI, C+I)" ./run_program.sh ../decks/index_result_indicators.strap StretchIndexResultIndTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/index_result_indicators.strap").read()).symtab["PASS"]//32)')"

run "B(IND) routine, all five groups (ja_ax1a, encoding)" python3 verify_ibox1_bind_listing.py
# ja_ax1a pp.24-25's "BRANCH ON I BOX INDICATORS", all five groups --
# XF, XCZ, XVLZ, XVZ, XVGZ -- every indicator an index load sets.  70
# checks: 14 label addresses against the addresses the page prints
# beside them, 56 rows of machine code.
#
# It pins the index FLAG indicator, which nothing else did: every index
# word in index_result_indicators.strap has flag 0, so that program
# covers the RESULT indicators only.  It also pins the BRANCH-AND-ZERO
# CLEAR -- the mnemonic grammar is a leading Z for "branch if the bit is
# OFF" and a trailing Z for "turn the bit off after testing", and each
# group walks its indicator through both polarities before clearing it.
#
# Four injections, measured:
#   LX sets no indicators     -> IBIN1  (004023.40, "hang up if bit off")
#   trailing-Z does not clear -> IBIN4  (004025.40, "hang up if bit on")
#   XVZ never set             -> IBIN22 (004044.40, "hang up if bit off")
#   XVGZ never set            -> IBIN29 (004053.40, "hang up if bit off")
# Each halts at the line whose own comment names that failure.  The deck
# diagnoses itself; that is what transcription buys over a hand-written
# vector.
#
# AND ONE INJECTION THAT PASSED, which is the block's honest limit:
# setting all five unconditionally to 1 on every index load passes the
# whole routine (re-measured after the XVGZ group was added).  Every group checks its indicator ON, and
# the only OFF it checks is the one the trailing Z produces -- never an
# indicator off because its condition is false.  A green result here is
# evidence that each indicator can be turned on and cleared, not that
# the conditions discriminate.  For that, see index_result_indicators
# and the KV/KC compare programs, where an indicator being OFF is what
# the branch depends on.
#
# A second claim I wrote here was false and the injection caught it: I
# expected "XVZ computed as not-XVGZ" to fail in the XVZ group, and it
# passes, because XVZ is only ever observed under a word whose value IS
# zero.  Recorded in the program header.
#
# The three seed words are the reason the groups can share: IBXWZO is
# value -1, flag 1, count 0 -- negative, flagged and zero-count at once,
# which the listing calls "COMMON XW FOR XF,XCZ,XVLZ" -- and IBXWZ1 and
# IBXWZ2 are value 0 and value 1, count 1, for XVZ and XVGZ.  The three
# walk the value negative, zero and positive while leaving the other
# fields alone, which is the only way one routine reaches all three.  See the program header for the XW
# fourth-field discrepancy between this tape and jb_ax4b, now narrowed
# to the four-operand form alone.
run "B(IND) routine, all five groups (model)" ./run_program.sh ../decks/ibox1_bind.strap StretchIbox1BindTb \
    "PC=4196"          # 004062.00, the half-word after the routine's last printed line

run "B(IND) XL/XE/XH blocks (ja_ax1a, encoding)" python3 verify_ibox1_bind_ind_listing.py
# ja_ax1a pp.25-26's IBIN35-IBIN55: the three "RESTART OF ROUTINE"
# sections that test BRANCH ON XL, XE and XH -- the only places in the
# deck that write the INDICATOR REGISTER through ordinary storage, and
# the tail of the routine, ending where "COMPARE VALUE %KV%" begins.
#
# It is a different mechanism from the five groups above.  Those reach
# their indicators through an index LOAD, so the deck sets them by
# choosing a seed word.  XL is an index COMPARISON indicator and no
# index load touches it, so the deck pokes the bit in by hand:
#
#   LX, $X1, IBXWZ        set XW to zero
#   LV, $X1, IBXWZ6       load bit 20, %XL IND%
#   SV, $X1, $IND+.32     store in IND reg.
#
# The same shape three times with one constant changing: value bit 20,
# 21, 22 -> indicator bit 52, 53, 54 = XL, XE, XH.
#
# $IND is word 11 and SV stores the 24-bit value field at a BIT
# address, so the store covers IBM bits 32-55; value bit 20 lands at
# 32+20 = 52, which is XL.  The Reference Card's footnote c -- only
# indicator bits 0-19 are read-only -- is what that permission is.
#
# THIS BLOCK FOUND A REAL GAP, fail-first.  st.writeWord(11) was a
# deliberate no-op, so the block hung at IBIN36 (004063.40), the deck's
# own "hang up if bit off" -- exactly the line predicted from reading
# the storage path, before any change was made.  The fix folds the
# half-word into the `ind` value the execute stage already writes once
# per instruction, which is the same technique the BB arm used for a
# single bit; all four index half-word stores (SV, SC, SR, SVA) go
# through it, not just the witnessed one.  See bsv/README.md "Scope".
#
# THE THREE BLOCKS ARE NOT REDUNDANT, measured: a fold that keeps only
# indicator bit 52 passes the XL block and halts at IBIN43 (004073.40),
# the XE block's first check.  Transcribing all three is what makes the
# store's bit placement testable rather than just its existence.
#
# One transcription note.  Five XH rows read as ...72/...32 at a small
# crop and are ...73/...33; the assembler disagreed and was right.  What
# flagged it before the re-render was the encoding pattern -- bits 19-23
# hold the indicator address and the op byte's high bit splits each
# pair, so XCZ/XVLZ = 24, XVZ/XVGZ = 25, XL/XE = 26, and XH must be 27;
# an XH sharing 26 would make BZXH and BZXL the same instruction.
run "B(IND) XL/XE/XH blocks (indicator register written by SV)" ./run_program.sh ../decks/ibox1_bind_ind.strap StretchIbox1BindIndTb \
    "PC=4240"          # 004110.00, the half-word after IBIN55's second NOP

run "Storage protection, gated on the interrupt enable bit" ./run_program.sh ../decks/storage_protection.strap StretchProtTb \
    "PC=4241"          # 004110.40; hand-written, not a listing fact
# THE FIRST PIECE OF THE INTERRUPT SYSTEM, and the smallest one a
# program can observe.  p.45 defines DS/DF/IF as raised "while the
# interruption system was enabled", so the enable bit had to come with
# it -- adding that bit alone would have been untested state.
#
# p.31: locations 1, 2 and 3 are permanently protected "regardless of
# the contents of the boundary registers or the setting of the boundary
# control bit"; 0 and 4-31 never signal.  p.32 on a store: "Since this
# indicator [DS] is permanently masked on, storing in core storage is
# always suppressed" -- no mask-dependent branch, unlike DF and IF.
# p.40: BE enables, BD disables, BEW enables, all unconditionally and
# before the branch.
#
# THE DECK SAID IT FIRST.  SSIP's SIP16 rewrites words 1, 2 and 3 and a
# BD guards it, commented "DISABLE BEFORE RESET OF PROTECTED AREA".
# This program is that behaviour in both directions.
#
# HOW IT IS BUILT, and why not the obvious way.  A first attempt had
# storage suppress the store at its single writeWord choke point and
# report it back on a wire; that does not schedule -- bsc lifts the
# wire's read into the rule predicate, which conflicts with the same
# rule writing it.  So the decision is made on the EXECUTE side, by one
# shared predicate, protViolates.  Of the 64 st.writeWord sites, 43
# write a CONSTANT special-register address (accumulator halves, sign
# byte, zeros/ones counts, remainder, factor) -- all in 4-31, which
# p.31 says never signal -- so only the computed-address stores are
# guarded.  One rule in one function, twenty mechanical uses of it.
#
# REWRITTEN 2026-09-21, when the interruption mechanism landed.  This
# program used to read DS directly with "BZB,$DS,$", which was only
# ever possible because interruptions did not exist.  DS is indicator
# 19 and mask bits 0-19 are permanently 1 (p.48), so an ENABLED machine
# raising DS interrupts at once and the mechanism turns that indicator
# off before forming the address -- it is gone before the next
# instruction.  Measured when this test first failed: n=19, eia=19,
# pc=4234, running away to 0 because the interruption address register
# had never been set.  The violation is now observed through the
# routine at table entry 19, which is how the machine reports it, and
# the test is stronger for it: it witnesses the suppression AND the
# interruption that p.32 and p.48 together require.  It is also why the
# decks poll indicators with the system DISABLED.
#
# Two injections, re-measured against the rewritten program, and the
# gating is two-sided:
#   protection never fires  -> 004106.00  BZB, 3.0, $   the ENABLED case;
#                                         the store landed and cleared the bit
#   ignores the enable bit  -> 004102.40  BZB, 3.0, $   the DISABLED case;
#                                         the store was wrongly suppressed
#
# THE BOUNDARY REGISTERS ARE THE SECTION BELOW; what is still not
# implemented is DF and IF (both mask-dependent, unlike DS), full
# operation TERMINATION -- p.32 says the whole operation is terminated,
# this suppresses the STORE only, so a BB whose write is suppressed
# still takes its branch -- and the straddling rule.  Nothing
# transcribed distinguishes them.

run "Storage protection: the address boundary registers" ./run_program.sh ../decks/storage_protection_boundary.strap StretchProtBndTb \
    "PC=4305"          # 004150.40; hand-written, not a listing fact

run "DS terminates the whole operation: a suppressed BB does not branch" ./run_program.sh ../decks/ds_terminates_branch.strap StretchDsTermTb \
    "PC=4262"          # 004123.00; hand-written, not a listing fact
# OPERATION TERMINATION, and the deviation protViolates' own note had
# named since DS was written: "this suppresses only the store, so a BB
# whose write is suppressed still branches."  It no longer does.
#
# p.32 on DS: "storing in core storage is always suppressed, AND THE
# OPERATION IS ALWAYS TERMINATED."  The branch is part of the
# operation.  Corroborated from the other direction on the same page,
# for IF: "the entire branch operation, including any counting, bit
# changing, or index alteration, is suppressed" -- the manual saying
# plainly that this machine suppresses whole branch operations.
#
# TWO CONDITIONS GATE IT AND BOTH ARE MEASURED.  A BB with mod == 00
# changes nothing, so it is not store-type at all and must still
# branch; and protViolates carries the enable gate, which is what lets
# the program plant a bit in a word it is about to protect.
#
# THE FIRST VERSION OF THIS PROGRAM COULD NOT SEE THE FIRST CONDITION.
# Its only BB on the protected word was the modifying one, so the
# injection dropping the mod == 00 exemption SURVIVED -- a condition
# asserted in a comment and witnessed by nothing.  Block 1 exists
# because of that survivor, and the re-run catches it.
#
# AND A GUARD CAME OUT ON THE SAME EVIDENCE.  storeViolates carried a
# "bw != 11" term for the indicator register; protViolates ALREADY
# returns False for word 11 (below 32, outside 1-3), the injection
# dropping the term changed nothing, and a guard whose comment must
# explain its own redundancy is decoration.  protViolates is the single
# authority on which addresses signal.
#
# Three injections, re-run after block 1 was added:
#   termination removed      -> 004122.40  WRONG (the branch was taken)
#   mod==00 exemption gone   -> 004110.00  B,$ (a pure test was suppressed)
#   DS not set on suppress   -> 004116.40  BZB, 6.0, $
#
# SCOPE, said plainly: only BRANCH ON BIT.  The other store-type
# operations -- VFL ST/M+, SX/SV/SC/SR, SVA, CM -- have side effects of
# their own that "terminated" presumably also suppresses, and none of
# that is implemented or tested.  BB was taken first because its side
# effect is a BRANCH, which a PC check can see.

run "IF: the instruction-fetch address alarm (p.32 classes 1 and 2)" ./run_program.sh ../decks/if_branch_alarm.strap StretchIfBrTb \
    "PC=4307"          # 004153.40; hand-written, not a listing fact
# BOTH IMPLEMENTED HALVES OF IF, AND THE MASK-DEPENDENT SUPPRESSION.  p.32 lists three classes for
# Instruction Fetch: class 1 "the location of each instruction to be
# executed", class 2 "the branch address of all successful branch
# operations", class 3 the EX/EXIC subject.  NO LONGER MOOT: EX is
# implemented as of 2026-09-25 and the subject's location IS monitored
# -- see the four "EX:" sections below and ../decks/ex_monitor.strap.
# EXIC's half stays moot until EXIC is implemented.
# Its deck oracle is routine 1260 TEST 8C, transcribed beside this
# (encoding only: running it needs SSIP's I60S1/I60SX1 harness).
#
# WHERE CLASS 1 GOES, and two obvious sites that are both wrong.  NOT
# at fetchReq: the instruction buffers prefetch speculatively and p.32
# monitors instructions TO BE EXECUTED, so a word fetched and then
# discarded by a taken branch must not raise IF.  NOT in rl_prepare
# either: that rule already calls execute(), so setting the indicator
# there makes a second writer of `indicators` in one rule -- the G0004
# shape StretchStorage's comments describe.  It goes INSIDE execute(),
# keyed on the instruction's own `pc`, which every dispatch path
# already passes: the one place that sees exactly the instructions
# that execute.
#
# AND IT NEEDED A PARAMETER, the only invasive part.  p.32 class 1
# excepts "the single instructions at the effective interruption
# address which are executed when an interruption occurs".  rl_prepare
# knows that as isValid(intPC); execute() cannot see it.  So a Bool
# rides through ebox.exec/ebox.start and lives in the E-box's `held`
# tuple -- resume() re-runs execute() for the same instruction and must
# answer the exemption the same way both times.
#
# THE FALL-THROUGH ARRANGEMENT IS THE CLASS-1 TEST.  Control reaches
# PRE, below the lower boundary, and falls straight through into
# FALLIN, the first word of the area.  No branch enters, so class 2
# cannot contribute.  Same shape TEST 8C uses -- "SV,$X2,$LB" pointed
# at the label that follows.
#
# CLASS 2 CAN NO LONGER BE ISOLATED, AND ITS INJECTION NOW SURVIVES.
# A real loss of discrimination, recorded rather than left to be
# found.  When class 2 was the only implemented half, removing it
# halted the program -- measured.  Now a branch into the area sets IF
# via class 2 AND the target executes and sets it again via class 1:
# same indicator, indistinguishable.  They separate only when the
# MASK-DEPENDENT half lands, because a protected branch target then
# suppresses the whole branch operation and control never arrives, so
# class 1 never fires.
#
# A SENTENCE IN p.32 IS AMBIGUOUS AND THE DECK SETTLES IT.  "...the
# entire branch operation ... is suppressed.  The address boundaries
# are ignored if the mask bit is zero."  Read alone the last sentence
# could mean IF never sets with the mask at zero.  It sets: TEST 8C
# case 3 is titled "ENABLE MASK 0 FETCH OK IND ON NO INT" and errors
# with "-INSTRUCT FETCH BELOW LB FAILS TO SET IF, NO INT, MASK 0,
# ENABLED."  So the sentence attaches to the SUPPRESSION before it,
# matching the general rule two paragraphs earlier.
#
# A NEAR-MISS IN THE PROGRAM'S OWN DATA, kept because it would have
# gone green.  ABOVE first landed at 004300.40 -- the SECOND HALF of
# FALLIN's word -- because DD does not align after a half-word B.  UB
# then equalled LB, p.31's half-open area was EMPTY, nothing signalled,
# and the program would have passed while testing nothing.  An explicit
# SLC fixes it.
#
# Four injections, observed:
#   class 1 removed               -> 004106.40  BZB, $IF, $
#   class 1 sets DF (20) not IF   -> 004106.40  BZB, $IF, $
#   interruption-addr exemption   -> SURVIVES.  Nothing here interrupts,
#     dropped                        so the exemption is unwitnessed;
#                                    TEST 8C has the interrupt table and
#                                    does not run.
#   class 2 removed               -> SURVIVES, subsumed by class 1 above.
#
# THE MASK-DEPENDENT HALF IS HERE TOO, added after the four blocks
# above.  p.32: "If the branch address of a successful branch operation
# is such that control would pass into a protected area, the entire
# branch operation, INCLUDING ANY COUNTING, BIT CHANGING, OR INDEX
# ALTERATION, is suppressed."  That enumeration is the specification.
#
# WHAT IS SUPPRESSED, AND WHAT IS NOT.  Suppressed: the branch itself
# and the INDEX ALTERATION (the shared deferred index write and
# VflInt's progressive update).  NOT suppressed: BIT CHANGING, because
# BRANCH ON BIT issues its st.writeWord inside its own arm, before
# execute()'s commit point.  DS solved that shape one arm over with
# `storeViolates`; doing the same for IF needs the branch-target test
# moved into that arm.  Two thirds of a sentence, said as two thirds.
#
# AND FIGURE 11 SAYS THE WORD IS "SUPPRESSED", NOT "TERMINATED".
# Reference Manual printed p.43's Indicator List gives DS class "P,S"
# and DF/IF "P,S*,C" with "*Class S when mask is one; otherwise Class
# C" -- S = suppressed, C = completed.  p.32's "terminated" is the
# storage-protection chapter using the word loosely; p.45 and p.51 both
# say suppressed.  See docs/NEXT.md 5a.
#
# Three suppression injections, observed:
#   suppression removed            -> 004302.00  WRONG2, inside the area
#   suppression NOT gated on mask  -> 004117.00  block 4b's B,$ guard
#   maskedOn reads bit 20 not 21   -> 004302.00  WRONG2
#
# BLOCK 4b EXISTS FOR THE MIDDLE ONE.  Without a taken branch into the
# area with the mask at ZERO, removing the gate changes nothing here.
#
# ALSO UNWITNESSED: ifSignal's "a >= 32" guard, which exists because
# p.45 says "Branching to an address below 32 also actuates the
# indicator [AD]" and p.32 says an AD address "cannot actuate any of
# the address alarm indicators".  Seeing it needs control actually at
# words 1-3 -- the boundary registers themselves -- whose contents
# would then execute.  The model does not raise AD there either.

run "Clause 1's DS survives a protected branch target (p.52)" ./run_program.sh ../decks/df_bb_if_ds.strap StretchDfBbIfDsTb \
    "PC=4186"          # 004055.00; hand-written from the manual, no deck oracle
# THE OBSERVABLE THE SECTION BELOW FIXED AND COULD NOT WITNESS.  Its
# block E runs IF's mask at ZERO deliberately, because a mask of one
# re-routes the injection that witnesses its own headline finding.  So
# the interaction needed its own program, and NO MODEL CHANGE -- the
# fix was already right, it just had no test.
#
# THE CASE: a MODIFYING BB whose data word is protected AND whose
# branch target is protected AND with IF's mask bit at one.  Under the
# old `ifSuppress = wouldBranch && ...`, ifSuppress fired, the whole
# bit-change block was skipped, and CLAUSE 1's DS ACTUATION WAS LOST.
# Reading ifSuppress off `takeBranch` restores it, because takeBranch
# is already false when the instruction was never allowed to test the
# bit.  DS is the ONLY observable difference -- ifSignal and the branch
# commit stay gated on takeBranch and do not move.
#
# WHY "SUPPRESSED" AND "DS IS ACTUATED" ARE COMPATIBLE AT ALL, which is
# the sentence the whole program rests on.  Printed p.52: "the
# suppression of an instruction must necessarily exclude the following
# operations: 1.  The actuation of those indicators, associated with
# the instruction, of Class S, and indicators DF and IF when their mask
# bits are zero."  And DS is Class S by name on the same page.  A
# suppression may not eat a Class-S actuation -- least of all via a
# SECOND suppression.
#
# Six injections, every halt OBSERVED, each anchored on a WHOLE LINE
# rather than a token, because the bare token `takeBranch` occurs four
# times in the arm and a token-level sed would have built a different
# mutant than the row claims.  The headline row halts at 004017.00.
#
# AND INJECTION 6 IS WHY THIS PROJECT CHECKS DESTINATION VALUES.
# Making the suppressed write happen anyway passed EVERY indicator and
# marker check in the program and was caught only by the closing
# "BZB, PROT.0, $" -- the value check.  A model that "suppresses" by
# writing the wrong thing is invisible to indicators.
#
# TWO NON-VACUITY ARGUMENTS, because a clean run cannot distinguish
# "correct" from "cannot fail".  Block A is not vacuous and injection 1
# proves it: for ifSuppress to become true under that mutation, both
# maskedOn(ind_IF) and ifViolates(TGTIN) must have been true, so the
# halt is direct evidence that "BB1,12.21" really set IF's mask bit and
# that TGTIN really was inside the area.  "BB,8.0,$" is not vacuous and
# injections 2 and 3 prove it.  By contrast "BB,7.0,$" genuinely CANNOT
# fire here -- DF's mask is zero throughout -- and is labelled
# belt-and-braces rather than coverage.
#
# ONE CORRECTION TO THE SECTION BELOW'S HEADER, recorded here because
# that file was not edited: it says p.52's clause-3 sentence "wraps
# into the first two lines of printed p.53".  It does not -- it wraps
# from the bottom of p.52's LEFT column to the top of p.52's RIGHT
# column.  Printed p.53 is a different section.

run "DF class 1's FIFTH site: read-only BRANCH ON BIT (p.52)" ./run_program.sh ../decks/df_bb_readonly.strap StretchDfBbRoTb \
    "PC=4313"          # 004154.40; hand-written from the manual, no deck oracle
# THE SITE THE PREVIOUS COMMIT DISCOVERED WAS MISSING.  Printed p.52
# gives BRANCH ON BIT three clauses, and the model had none of them:
#   1. bits 60 and 61 NOT both zero -> "The instruction is suppressed
#      without a test of the addressed bit, and indicator DS is
#      actuated."   (storeViolates existed; see the finding below)
#   2. both zero and the DF mask bit ONE -> suppressed, DF actuated.
#   3. both zero and the DF mask bit ZERO -> "Indicator DF is actuated
#      but does not cause suppression of the instruction."
# Clause 3 is why this was a gap in the INDICATOR and not only in the
# suppression: a read-only BB on a protected word raised NOTHING.
#
# THE ENCODING IS CHECKED AGAINST THE DECODER, NOT INFERRED.
# StretchDecode takes modAbc = w[3:1], and IBM bit n is BSV bit 63-n,
# so modAbc[2:1] IS IBM bits 60-61 and modAbc[0] is IBM 62, the branch
# condition.  p.52's "not both zero" is literally the arm's existing
# `changes`, read from the other side.
#
# AND IT FOUND A SECOND BUG, which is why the brief asked whether
# clause 1 already matched.  IT DID NOT.  The model suppressed clause
# 1's branch and bit change but still COMPUTED THE BRANCH CONDITION
# FROM THE TESTED BIT, and then signalled IF from the branch target of
# an instruction p.52 says was never decided -- the same page's AD
# sentence forbids exactly that shape ("suppressed ... since no bit can
# be tested to complete its execution.  Indicator IF cannot be
# actuated.").  Fixed by splitting `wouldBranch` (the bit said branch)
# from `takeBranch = wouldBranch && !noTest` (the machine was allowed
# to look), and reading everything downstream off takeBranch.
# MEASURED, not argued: reverting that one call halts at 004150.40.
#
# Eight injections, every halt address OBSERVED, none survived.  They
# were applied by a helper that ASSERTS THE OLD TEXT OCCURS EXACTLY
# ONCE and PRINTS THE DIFF before running -- no sed, because a silent
# no-match is indistinguishable from a measured null.
#
# THE REGRESSION THAT NEARLY HAPPENED AND DID NOT, worth keeping: the
# mask register resets to 0xFFFFF000_00000000, so DF's mask bit 20 is
# ZERO by default.  ds_terminates_branch.strap block 1 is a read-only
# BB on a protected word with the system enabled -- it now takes clause
# 3, sets DF, and still branches.  Had the reset been mask-one it would
# have been suppressed and hung.
#
# ONE OBSERVABLE OF THE SAME ROOT CAUSE IS STILL UNTESTED and is said
# so rather than left to be found: `ifSuppress` also gates the bit
# change, so a modifying BB with a protected data word AND a protected
# target AND IF's mask at one used to lose clause 1's DS actuation
# entirely.  Reading ifSuppress off takeBranch restores it, but block E
# runs IF's mask at ZERO deliberately (a mask of one would re-route the
# injection that witnesses the finding above), so this needs its own
# block.

run "DF SUPPRESSED on a refill address: R, RCZ, CBR, V+CR, V+ICR, V-ICR (p.32 class 3)" ./run_program.sh ../decks/df_refill_suppress.strap StretchDfRfSuppTb \
    "PC=4443"          # 004255.40; hand-written to TEST 8C's shape, not a transcription
# THE OTHER HALF OF THE PREVIOUS COMMIT'S "plain gap with no excuse".
# Six of the eleven class-3 refill sites now suppress: CBR/CBRZ, V+CR,
# V+ICR, V-ICR, and R/RCZ on both their index-register and
# external-memory paths.
#
# THE FIVE PROGRESSIVE-INDEXING SITES ARE UNTOUCHED, and the line
# between them got a STRUCTURAL confirmation nobody expected.  Printed
# p.53's "An alert of Class S during progressive indexing suppresses
# only the indexing portion of the operation" is not merely a different
# rule -- it is item 3 under "EXECUTION TERMINATED", on the facing
# column from "Execution Suppressed".  Terminate, not suppress.  The
# two mechanisms are separated by the manual's own headings.
#
# AND printed p.52 TURNS OUT TO BE A BETTER SOURCE THAN p.45 FOR THE
# HARD HALF.  p.45 leaves open whether a suppressed count-branch-refill
# still BRANCHES.  p.52 works this exact case by name: if a STORE
# INSTRUCTION COUNTER IF COUNT, BRANCH AND REFILL runs as an EXECUTE
# subject with the refill address protected, "the entire subject
# instruction is still suppressed but only indicator DF is actuated ...
# Indicator DF is actuated since THE TEST FOR THE REFILLING IS
# INDEPENDENT OF THE TEST FOR A SUCCESSFUL BRANCH."  It does not
# branch -- and it endorses the shape the model already had, with
# doRefill computed from the count alone and never from `take`.
#
# ONE SITE NEEDED MORE THAN A ONE-LINE GATE.  In evalBranch the test
# had to move BEFORE the prefetch bail-out: inserting it beside the
# dfSignal call would still have ISSUED the refill read and landed the
# word in prefetch[slot] before skipping the arm.  That is a
# control-flow reshape of a function SIC shares, which is why four
# extra regressions were run (StretchIboxSicTb, StretchIboxSpanTb,
# StretchIboxCbrTb, StretchMaskTb) on top of the fourteen expected.
#
# NINE INJECTIONS, NONE SURVIVED -- AND A TENTH THAT DID, recorded as a
# bounded gap in the TEST rather than dressed up.  Making the evalBranch
# suppression fire only on the second pass (so the read is issued, then
# the arm skipped) yields ALL TESTS PASSED.  The bound is stateable: a
# refill read writes no storage, sets no indicator, and the model
# exposes no cycle or read count to the program, so the only trace is
# the prefetch slot -- and its one consumer, SIC, requests its read
# only `if (o.taken ...)`, which a suppressed CBRZ never is.  The
# ordering is justified by p.45's "the fetch did not take place", not
# by a test.
#
# THE INERTNESS SWEEP CAUGHT AN IDIOM THE PREVIOUS ONE WOULD HAVE
# MISSED.  mask_register_fields.strap sets DF's mask bit in the OCTAL
# spelling "BB1,(8)14.24" (word octal 14 = 12, bit octal 24 = 20),
# which none of $MASK / BIT20 / 12.20 / LBIT20 matches.  Inert anyway
# -- it never enables the system and issues no refill -- but the sweep
# only found it because it looked for the value, not the spelling.
#
# ONE OPEN QUESTION LEFT IN THE CODE RATHER THAN DECIDED BY INVENTION:
# on R/RCZ's external-memory path, if the OPERAND word is also
# protected, the suppressed arm no longer reaches the DS signal it used
# to set.  p.52 item 1 argues DS should still actuate; p.32's "if an
# address ... is not actually used, it will not be monitored" argues it
# should not.  No deck witnesses it and the inertness sweep shows no
# program in the suite reaches the combination.  The uniform
# "deliberately nothing at all" shape was taken to match the reviewed
# class-1 sites, and it is reversible in one line.

run "DF SUPPRESSED: the mask-dependent half (p.32/p.45 class 1)" ./run_program.sh ../decks/df_fetch_suppress.strap StretchDfSuppTb \
    "PC=4387"          # 004221.40; hand-written to TEST 8C's shape, not a transcription
# THE HALF THAT WAS MISSING.  dfSignal has always turned the indicator
# ON -- printed p.32 says that happens whatever the mask bit is -- but
# "if the DF mask bit is one, the data fetch is suppressed and the
# operation terminated" needed a mechanism this model did not have.
# Now it does: dfSuppresses(st, a) = maskedOn(st, ind_DF) &&
# protViolates(st, a), asked at the four class-1 dfSignal sites, and
# when it fires THE WHOLE ARM IS SKIPPED -- no read, no result, no
# result indicators, no progressive-index update, no class-3 refill.
#
# "THE WHOLE ARM" IS SOURCED, not assumed.  printed p.32 says only
# "the data fetch is suppressed"; printed p.45's entry for indicator
# 20 is the one that settles it: "If the corresponding mask bit was
# one, the fetch did not take place, and THE ENTIRE OPERATION WAS
# SUPPRESSED.  If the mask bit was zero, the operation was completed
# normally."  And `next` is deliberately untouched, because printed
# p.52's list of what a suppression must NOT exclude ends with "3. The
# stepping of the instruction counter."
#
# EVERY CHECK OBSERVES THE DESTINATION'S VALUE, never the operation's
# own result indicators -- 8C's own probe shape.  Preload the
# destination with a distinctive value, put a DIFFERENT value in the
# protected word, then ask what the destination holds.  A model that
# "suppressed" by writing zero would pass an indicator check and fail
# this one.
#
# Three blocks matching TEST 8C's own four conditions: A disabled +
# mask 1 (fetch proceeds, DF off), B enabled + mask 0 at all four
# sites (DF sets, operation proceeds), C enabled + mask 1 at all four
# sites (DF sets, operation suppressed, interruption marks word 7).
#
# Seven injections, seven distinct observed halt addresses, none
# survived.  One went AGAINST EXPECTATION and is the reason block A is
# not decoration: dropping the ENABLE gate from the suppression was
# expected to add nothing, since protViolates already carries an
# irqEnabled() gate for dfSignal.  It discriminates -- the suppression
# then fires while DISABLED, and A's value check catches it at
# 004112.00.
#
# THE "classification mismatch" LINES ARE EXPECTED, not a defect, and
# they are the same accepted path ad_indicator.strap's AD guard
# already documents: the core probes an operand-fetching E-box
# instruction by running execute() with no operand and expecting a
# bail-out, and a SUPPRESSED operation reads nothing, so it completes
# during the probe.  The core detects that, says so, and commits the
# probe as the execution.  DF is set, the accumulator is untouched,
# the IC steps.
#
# INERTNESS PROVEN, NOT ASSUMED.  The change can only bite where DF's
# mask bit 20 is ONE.  Swept both idioms -- the wholesale $MASK write
# and the bit-20 setters.  Of the $MASK writers that actually run,
# both do "Z,$MASK"; of the bit-20 setters, only ax5b_160_test8c*
# (encoding-only, never executed) and this program set it to one.
#
# AND IT CARRIES A CORRECTION TO THIS PROJECT'S OWN ACCOUNTING.  "DF
# class 1 is complete" was FALSE, and was false before this change.
# **Class 1 has FIVE sites, not four.**  printed p.52 gives the fifth
# for BRANCH ON BIT: "since a protected effective bit address in
# BRANCH ON BIT could result in the destruction of information, alert
# DS or DF may occur if: ... 2. The addressed bit is specified to
# remain unconditionally unchanged, and the DF mask bit is one.  The
# instruction is suppressed without a test of the addressed bit, and
# indicator DF is actuated.  3. The addressed bit is specified to
# remain unconditionally unchanged, and the DF mask bit is zero.
# Indicator DF is actuated but does not cause suppression of the
# instruction."  Verified first-hand at 300 dpi.
#
# The BitBranch arm computes storeViolates = changes && protViolates()
# and never calls dfSignal, so **a READ-ONLY BB (bits 60 and 61 both
# zero) on a protected word raises NEITHER indicator today.**  Clause
# 3 makes that a gap in the INDICATOR, not only in the suppression.
# Not built here: it is a fifth site whose suppression would have to
# interact with the branch commit point one arm over, and it deserves
# its own program.  See docs/NEXT.md item 2.
#
# TWO FURTHER GAPS, kept distinct because they are different kinds.
# Progressive-indexing refills are SCOPED OUT: printed p.53 says "An
# alert of Class S during progressive indexing suppresses only the
# indexing portion of the operation" -- a different mechanism,
# terminate rather than suppress.  R/RCZ/CBR/V+CR/V+ICR/V-ICR refills
# are a PLAIN GAP with no excuse: p.32 class 3 names them as their own
# category and p.45's "entire operation" applies to them too.
#
# ONE THING LABELLED AN INFERENCE IN THE CODE, because the deck cannot
# settle it: that suppression also kills the result indicators, the
# progressive update and the index-result indicators.  p.52's list
# reads exhaustive, so it follows by closure -- but the manual never
# says it, and 8C case 4 re-actuates the indicators with a fresh LX
# before testing them, so no deck row decides it either way.

run "DF: the data-fetch address alarm, p.32 class 1" ./run_program.sh ../decks/df_data_fetch_alarm.strap StretchDfTb \
    "PC=4306"          # 004151.00; hand-written, not a listing fact
# THE THIRD ADDRESS ALARM, and the first subsystem this project has
# implemented from the Reference Manual with no deck anywhere to check
# it against.  p.32: "When an address alarm is caused by a data address
# used in a fetch-type operation, indicator DF is turned on... A
# fetch-type operation is one in which the contents of an addressed
# storage location are read out for use but are not subject to change."
#
# p.32 GIVES A CLOSED LIST, not a rule to generalise, and this is
# CLASS 1 of its three: "the effective address of all fetch-type
# operations with a direct address."  Class 2, each level of LOAD VALUE
# EFFECTIVE, is moot -- LVE decodes Operation Code Invalid here.  Class
# 3, "the refill address used in index refill operations and the
# operations REFILL and REFILL ON COUNT ZERO", is NOT implemented: the
# model issues a refill read at eleven sites and none of them signals.
# Both are said in the program and on protViolates rather than left to
# be found.
#
# NOT ONE GUARD AT THE ONE READ THEY ALL FUNNEL THROUGH, and that is
# the decision worth keeping.  Every operand word this model reads
# leaves through a single st.readWordReq in mkEBox -- but a
# read-modify-write STORE (VFL ST/M+, SX/SV/SC/SR, SVA, CM, BB's bit
# change) reads its word through that same path, and p.32 puts those on
# the DS side: their contents ARE "subject to change".  So DF is set at
# four opcode-gated sites instead, one per instruction format -- VFL
# L/+/K, connective C/CT, the direct-index loads and compares, and the
# floating-point arithmetic class -- and half the program is stores.
#
# THE MASK IS NEVER READ, and p.32 is why: "If the DF mask bit is one,
# the data fetch is suppressed and the operation terminated.  If the DF
# mask bit is zero, the operation proceeds normally."  The INDICATOR
# goes on either way; the mask decides only what happens next.  So
# turning it on needs no mask bit, and suppression/termination -- the
# mask-dependent half, which DS does not have either -- stays
# unimplemented.  The program runs the mask-ZERO case only and says so,
# because nothing it could write for mask-one would pass for the right
# reason.
#
# THE NOPS AFTER EACH STORE ARE NOT PADDING -- OR THEY WERE NOT WHEN
# THIS WAS WRITTEN.  A DS violation is reported by INTERRUPTING, and
# this model USED TO take an interruption at a QUIESCENT boundary
# rather than the instruction boundary p.48 names.
#
# THAT DIVERGENCE WAS MEASURED AND FIXED 2026-09-25 (see the
# "Interruption timing" section and docs/NEXT.md item 3), so the slack
# these NOPs buy is expected to be unnecessary now.  IT HAS NOT BEEN
# RE-MEASURED HERE: the sweep was run on ../decks/int_timing_bracket.strap,
# not on this file, so the paragraph below is true of the old model and
# is expected-false rather than known-false of the new one.  Left in
# place deliberately rather than deleted on an analogy.  A VFL ST bails out
# once for its read-modify-write read, so it holds the E-box a call
# longer than the BB-style stores the two storage_protection programs
# use.  Measured: with one instruction of slack the check halted with DS
# ON in word 11 and word 6 still zero, which reads exactly like a
# protection bug and is not one.
#
# EIGHT INJECTIONS, each predicted before it was run, each landing on
# the predicted address.  Reproduce any row with
#   python3 line_addresses.py ../decks/df_data_fetch_alarm.strap
#
#   VFL fetch guard removed         -> 004107.00  BZB, $DF,  $
#   K dropped from that predicate   -> 004114.00  BZB, $DF,  $
#   ST ADDED to that predicate      -> 004127.00  BB,  $DF,  $   (after ST)
#   direct-index guard removed      -> 004132.40  BZB, $DF,  $
#   SV ADDED to that predicate      -> 004141.00  BB,  $DF,  $   (after SV)
#   floating-point guard removed    -> 004144.40  BZB, $DF,  $
#   connective guard removed        -> 004147.40  BZB, $DF,  $
#   dfSignal sets IF (21) not DF    -> 004107.00  BZB, $DF,  $
#
# THE TWO "ADDED" ROWS ARE THE ONES THAT EARN THE STORE BLOCKS.  Without
# them the store halves of this program are lines that cannot fail, and
# the claim that DF and DS are separated would be untested -- the funnel
# design would pass everything else here.  Both are standing mutants:
# df-store-read-signals-fetch and df-index-fetch-unsignalled in
# mutation_score.py.
#
# AND THE "SETS IF" ROW ONLY MEANS SOMETHING BECAUSE OF ONE LINE.  DF is
# 20 and IF is 21; removing the signal and moving it one bit left halt
# at the same address, so "BB, $IF, $" sits beside the first check to
# assert the neighbour is OFF.  Without it the bit NUMBER is assumed
# rather than tested.

run "DF on a refill address: R and RCZ (p.32 class 3)" ./run_program.sh ../decks/df_refill_alarm.strap StretchDfRfTb \
    "PC=4285"          # 004136.40; hand-written, not a listing fact
# THE OTHER HALF OF p.32'S CLASS 3, and the manual's own seam: "the
# refill address used in index refill operations and the operations
# REFILL and REFILL ON COUNT ZERO".  This covers the two NAMED
# operations, both their paths -- the index-register one and the
# external-memory one that takes two sequential reads.  The nine
# refill reads that progressive indexing and count-branching issue are
# still unmonitored, and that is said on protViolates and in NEXT.md
# rather than left to be found.
#
# THE SIGNAL SITS INSIDE BOTH SUPPRESSION GATES, and that is the whole
# content of the placement.  refillLegal suppresses a refill address of
# 1-15 -- a DECK fact, routine 1238's TEST 2G against TEST 2H, "CHK
# REFILL FRM LOCN 0" and "CHK NO REFILL FRM LOCNS 1 THROUGH 17" -- and
# RCZ "acts only if its count is zero" (p.26).  A refill either gate
# suppresses READS NOTHING, and p.32 opens "all storage addresses
# ACTUALLY USED by the CPU in the course of an operation are subject to
# address monitoring."  Block 2 runs RCZ with a count of seven whose
# refill field names the monitored word, which is what makes that a
# tested claim; injection 3 hoists the signal one line outward and
# block 2 is what catches it.
#
# ONLY A REFILL ADDRESS OF 32 OR MORE CAN EVER SIGNAL, which is why the
# monitored area here is ordinary core and nothing else.  p.31's
# carve-out means 0 and 4-31 never signal; 1-15 are suppressed by
# refillLegal anyway and 16-31 are the index registers.
#
# Five injections, each predicted before it was run, each landing on
# the predicted address.  Reproduce any row with
#   python3 line_addresses.py ../decks/df_refill_alarm.strap
#
#   index-register signal removed   -> 004107.00  BZB, $DF,  $
#   external-memory signal removed  -> 004124.40  BZB, $DF,  $
#   signal hoisted OUTSIDE the gate -> 004114.40  BB,  $DF,  $  (after RCZ,
#                                       count 7 -- the refill never happened)
#   external path signals `rw` too  -> 004133.00  BB,  $DF,  $  (after R on a
#                                       word INSIDE the area, which R rewrites,
#                                       so p.32 puts its read on the DS side)
#   dfSignal sets IF (21) not DF    -> 004107.00  BZB, $DF,  $

run "DF on a refill address: CBR, V+CR, V+ICR, V-ICR (p.32 class 3)" ./run_program.sh ../decks/df_refill_index_alarm.strap StretchDfRfxTb \
    "PC=4282"          # 004135.00; hand-written, not a listing fact
# THE OTHER HALF OF THE SAME SENTENCE: "the refill address used in
# INDEX REFILL OPERATIONS".  The companion above covers the two
# operations p.32 names outright; this covers the refills COUNT AND
# BRANCH and the index-arithmetic operations issue when a count reaches
# zero.  With it, all eleven refill reads in StretchExecute.bsv signal
# except the five in the two VFL-format arms, which are the last piece
# of DF and are a control-flow reshape rather than an insertion.
#
# EVERY BLOCK IS PAIRED, count-one against count-five.  p.26: CBR "is
# identical to COUNT AND BRANCH, except that in addition the index word
# specified by J is refilled if the count reached zero", and V+ICR
# likewise.  A refill that does not happen reads nothing, so each
# signal sits inside its own count gate and the count-five block is
# what makes that a tested claim -- injections 2 and 4 hoist the CBR
# and V+CR signals one line outward and those blocks catch them.
#
# AN OPEN QUESTION THIS DOES NOT ANSWER, recorded in docs/NEXT.md.
# refillLegal -- a refill address of 1-15 is suppressed -- is applied
# to R and RCZ ONLY, on routine 1238's TEST 2G/2H.  Reference Manual
# pp.25-26 were read for this program and describe R, RCZ, V+ICR, CB
# and CBR WITHOUT MENTIONING THE RULE; the deck established it
# empirically for the REFILL operations alone.  So whether these four
# suppress the same way is unsourced in both directions, and the
# asymmetry now in the model is untested either way.  Not resolved by
# symmetry here, which is what AGENTS.md rule 4 forbids.
#
# AND THE FIRST VERSION OF THIS PROGRAM PASSED WHILE DOING SOMETHING
# ELSE.  Block 2's CBR branched to "$+1.0", but CBR is HALF-WORD
# format, so that target is the SECOND half-word of the full-word BB
# beneath it.  It decoded garbage, raised OP, and the machine
# interrupted into a zero table entry -- and the run still said ALL
# TESTS PASSED, because the interruption returned and every later check
# ran.  The only sign was one line of stderr, "interruption instruction
# at 4766 is E-box class -- not implemented".  Read the model's stderr
# on a GREEN run.
#
# Six injections, each predicted before it was run, each landing on the
# predicted address.  Reproduce any row with
#   python3 line_addresses.py ../decks/df_refill_index_alarm.strap
#
#   CBR signal removed              -> 004107.00  BZB, $DF,  $
#   CBR signal OUTSIDE its gate     -> 004114.40  BB,  $DF,  $  (count 5)
#   V+CR signal removed             -> 004116.40  BZB, $DF,  $
#   V+CR signal OUTSIDE its gate    -> 004121.40  BB,  $DF,  $  (count 5)
#   V+ICR signal removed            -> 004123.40  BZB, $DF,  $
#   V-ICR signal removed            -> 004130.40  BZB, $DF,  $

run "DF on a refill address: the VFL-format arms (p.32 class 3)" ./run_program.sh ../decks/df_refill_vfl_alarm.strap StretchDfRfvTb \
    "PC=4290"          # 004141.00; hand-written, not a listing fact
# THE LAST FIVE OF THE ELEVEN, and with them p.32's class 3 is
# complete: every refill read in StretchExecute.bsv now signals.  These
# are the refills PROGRESSIVE INDEXING issues from the two VFL-format
# arms, and they are the only ones that needed control flow reshaped
# rather than a line inserted.
#
# TWO SHAPES, EACH APPEARING TWICE.  L, + and K resolve their
# progressive update through a SHARED TRAILING BLOCK -- their own read
# never collides with a refill read, since they write only the
# accumulator and the indicators -- while ST and M+ resolve it INLINE,
# because their completion is a storage write that cannot share an
# execute() call with a new read request.  The connectives repeat the
# split exactly: C and CT through a trailing block, CM inline.  And
# connectiveOp carries its OWN COPY of that trailing block, so a check
# on vflIntOp's says nothing about it -- which is why blocks 5 and 6
# below exist and why injections 5 and 6 target the second copy.
#
# THE RESHAPE, and why it is not an insertion.  The trailing block
# reads "if (vflNeedsRefill && vflReadsUsed >= 2) setOpInvalid; else
# if (vflNeedsRefill && ...) needsRead = refill; else ...".  The first
# arm SUPPRESSES THE WHOLE OPERATION (a crossing-field read plus a
# refill would need a third prefetch slot), so no refill read happens
# there and the signal cannot sit beside that test -- it has to move
# inside the else.  And it needs its own vflNeedsRefill guard on top,
# because the block runs for EVERY progressive VFL operation, refill or
# not.  Injections 2 and 6 are exactly that guard removed.
#
# THE INDEX VALUE POINTS OUTSIDE THE AREA AND THE REFILL FIELD POINTS
# INSIDE, which is what makes each block name one address.  A
# progressive VFL operation monitors its operand address too (class 1,
# already covered), so a value inside would light DF whether the refill
# signalled or not; and for ST, M+ and CM the operand address is a
# STORE, so a value inside would raise DS and interrupt as well.  The
# "BB, 6.0, $" lines confirm those writes stayed silent.
#
# Seven injections, each predicted before it was run, each landing on
# the predicted address.  Reproduce any row with
#   python3 line_addresses.py ../decks/df_refill_vfl_alarm.strap
#
#   vflIntOp trailing signal removed  -> 004107.40  BZB, $DF,  $
#   vflIntOp trailing, guard removed  -> 004114.00  BB,  $DF,  $  (count 5)
#   ST inline signal removed          -> 004116.40  BZB, $DF,  $
#   M+ inline signal removed          -> 004123.00  BZB, $DF,  $
#   CT trailing signal removed        -> 004127.40  BZB, $DF,  $
#   CT trailing, guard removed        -> 004133.00  BB,  $DF,  $  (count 5)
#   CM inline signal removed          -> 004135.40  BZB, $DF,  $
# THE BOUNDARY REGISTERS, the second half of address monitoring.  Word
# 3 holds the upper boundary in bits 0-17, the lower in 32-49 and the
# boundary control bit at 57 (p.31 -- upper is named first and sits
# LOWER in the word).  The area is HALF-OPEN: p.31, "all words in
# subsequent locations up to, but not including, the address in the
# upper boundary register", and "if it is equal or smaller, no words
# are contained in the core storage area", which needs no guard of its
# own because the comparison is already false for every address.
#
# THE CONTROL-BIT POLARITY WAS NOT AN OPEN QUESTION.  This project's
# plan carried "still to source from Appendix C" in two places; p.31
# settles it in one sentence -- zero signals for a comparand INSIDE the
# area, one for a comparand OUTSIDE.  The p.15 overview had been read
# and the operand-designation chapter twenty pages later had not.  The
# cost of that was two "open question" entries and an unimplemented
# subsystem; the fix was rendering two pages.
#
# THE 0-31 CARVE-OUT GATES THE COMPARE, it does not sit beside it.
# p.31 says monitoring of 0-31 is INDEPENDENT of the boundary
# registers.  Written as "permanent OR boundary", a set control bit
# makes words 4-31 signal -- they are outside every area a program can
# name -- and those are exactly the 43 constant-address st.writeWord
# sites that go unguarded on the argument that 4-31 never signal.  The
# carve-out is what keeps that argument true, which is why the program
# stores to word 4 with the control bit set.
#
# HOW THE BOUNDARIES GET LOADED, and the layout that makes it work.
# SSIP's SIP16 resets word 2 with LVI then SV; the same pair loads a
# boundary because SV writes its 24-bit value into bits 0-23 of a
# half-word, so a WORD-ALIGNED bit address lands with its word number
# in bits 0-17 of that half -- where both boundary registers live.  And
# SV preserves the low seven bits it read back, so a store to the lower
# half leaves bit 57, the control bit, alone.
#
# Seven injections, each predicted before it was run.  Every address
# below is reproducible with
#   python3 line_addresses.py ../decks/storage_protection_boundary.strap
# which prints the row it names -- so these are checkable, not folklore:
#
#   boundaries never consulted     -> 004111.00  BB,  WLOW, $
#   lower exclusive (>= -> >)      -> 004111.00  BB,  WLOW, $
#   upper/lower fields swapped     -> 004111.00  BB,  WLOW, $  (area empty)
#   upper inclusive (< -> <=)      -> 004121.00  BZB, WABOVE, $
#   control-bit polarity inverted  -> 004106.00  BZB, WBELOW, $
#   address-invalid exemption gone -> 004147.00  BB,  6.0, $
#   carve-out written as OR        -> step cap, and the REASON is the
#     point.  With the control bit set that mutation makes words 4-31
#     signal -- and word 6 is where DS's interruption routine writes its
#     marker.  So the mutation makes the REPORTING MECHANISM ITSELF
#     violate: the marker store is suppressed, DS comes on again, and
#     the machine interrupts forever.  It is self-defeating in exactly
#     the way that shows why the carve-out is structural.  Worth
#     stating plainly that this is a WEAKER witness than the named
#     address it used to have (004130.40, before the rewrite below).
#
# ALL OF THESE WERE RE-MEASURED 2026-09-21 against the rewritten
# program.  This test, like its companion above, used to poll DS with
# BZDSZ; it now checks the interruption routine's marker instead, for
# the reason given in that section.  THE MARKER LIVES IN WORD 6 AND HAS
# TO: p.31 exempts locations 0 and 4-31 from monitoring, and with the
# control bit set every address outside the monitored area signals, so
# a marker anywhere in ordinary core would be suppressed and raise DS
# again.  Word 4 is already this program's witness THAT the carve-out
# works, so the marker uses a different one.
#
# A HANG ADDRESS IS ACCURATE TO ONE HALF-WORD, NOT EXACTLY, and that is
# a property of the harness rather than of any test.  A hang is a
# branch to itself, and the instruction counter OSCILLATES between the
# branch's address and the half-word after it while it spins; the step
# cap samples whichever clock it lands on.  Measured directly, by
# generating the same testbench three times against the PRE-REWRITE
# version of this program: caps of 30000 and 30001 reported 004135.00,
# a cap of 30002 reported 004134.40, one half-word apart.  Every other
# injection in this file happens to sample the branch's own address,
# which is why it took one landing on the other phase to notice.
#
# AND THE OFFSET IS OCTAL.  004107.40 is word 04107, bit 32.  The
# program's own source is DECIMAL unless "(8)" says otherwise, so the
# boundary control bit is written "3.57" there and printed "3.71" by
# line_addresses.py.  The first draft of this block recorded ".32" for
# every one of these, which is the decimal offset -- caught by running
# the new tool over storage_protection.strap above and watching it
# reproduce that section's ".40" addresses exactly.
#
# NOT IMPLEMENTED, stated in protViolates: DF and IF (both
# mask-dependent, unlike DS), full operation TERMINATION, and the
# straddling rule (p.31: a field crossing a boundary always signals --
# this compares one word address per store, not a field's extent).

run "I-Box 1 ENSU: the boundary word, bit-exact (ja_ax1a p.56)" python3 verify_ibox1_ensu_listing.py
# THE BOUNDARY REGISTERS GET A TRANSCRIPTION.  They were implemented on
# 2026-09-19 from Reference Manual p.31 and tested only by hand-written
# programs -- the weaker of this project's two standards.  This block is
# IBM's own assembler printing a boundary word, which checks the field
# placement with no dependence on the model or on my reading of p.31:
#
#   bits 0-17  = octal 777777 = 262143   the UPPER boundary
#   bits 32-49 = octal 40     = 32       the LOWER boundary
#   bits 56-63 = hex 40 = 0100 0000      BIT 57 SET: the control bit
#
# and the deck's comment on the line above reads "-32.0-262143.".  Upper,
# lower and the control bit, each printed where p.31 says it lives.
#
# THE POLARITY GETS A SECOND WITNESS, which is the part that was an open
# question in this project for months: control bit ONE means "a signal
# is obtained for a comparand OUTSIDE the specified area", and here a
# housekeeping routine sets it to guard everything outside its own
# working area.  That is the natural use of that polarity, from a
# programmer who had the machine.
#
# IT ALSO NAMES $MASK: "SX,$X1,$MASK" prints as "14.03 10", octal 14 =
# decimal word 12.  opcodes.py's SYSTEM_SYMBOLS had every other special
# register and not that one; it does now, on this row.
#
# WHAT THIS IS NOT.  It is an ENCODING oracle, not a behavioural one.
# Run against this model's 98,304 installed words, the deck's own
# setting -- lower 32, upper 262143, signal OUTSIDE -- monitors nothing
# except the permanently protected words 1-3: everything installed above
# 31 is inside the area, and everything above it is address-invalid and
# exempt (p.32).  So it pins where the fields are, not what the model
# does with them; storage_protection_boundary.strap remains the
# behavioural test, and remains hand-written.

run "I-Box 5 routine 1260's DS block, bit-exact (jb_ax5b pp.43-44)" python3 verify_ax5b_16086_listing.py
# THE DECK THAT TESTED THIS HARDWARE, found by reading pp.41-45 of
# jb_ax5b first-hand on 2026-09-22.  Storage protection and the
# interruption mechanism were both implemented from the Reference
# Manual and tested only by hand-written programs -- the weaker of
# this project's two standards, stated as such in their own headers.
# Block I6086 is IBM's own test of the same rule, and its error
# message spells it out in eight words:
#
#     "SV TO 1.0 FAILS TO SET DS WHEN ENABLED."
#
# WORD 1, DS, AND THE ENABLE GATE -- the three things protViolates
# implements, asserted by a programmer with the machine in front of
# them.  storage_protection.strap picked WORD 3 out of p.31's three
# permanently protected locations; the deck picks word 1, and the two
# together are the pair p.31 names.  "WHEN ENABLED" is the p.45 clause
# that put the enable bit into this model at all.
#
# AND IT DISABLES BEFORE IT POLLS.  The BDS that reads the indicator
# comes AFTER "I6086A BD,$+.32", never before.  That is the "a program
# cannot poll DS while enabled" trap in docs/NEXT.md -- paid for here
# by a rewrite of storage_protection.strap -- confirmed independently
# by the deck's own instruction order.
#
# FOUR ENCODINGS NO LISTING HAD CHECKED: BDS "21375.51 C2" (branch on
# indicator 19), BADZ "21376.10 46" (branch on indicator 16 and zero
# it -- the trailing-Z grammar, until now inferred from C22-6531
# Appendix A's footnote and never seen printed), SVA into $IA
# "2.13 D0", and DD(BU,32,8) printed as 11 octal digits, a row shape
# listing_oracle.py did not have.  Nineteen half-words, all nineteen
# right on the first assembly.
#
# AND A RESOLUTION LESSON.  A 200 dpi render of p.45 put the row
# labelled I6088 at 021400.00, and the page then looked a half-word
# short.  Re-read at 600 dpi it prints 021400.40.  The encoding here
# says the same independently -- "B,I6088" prints "21400.50 00" and
# bit 18 is the top bit of that octal pair -- but note that I6088's
# .40 is a SYN, an INPUT to the check, so the PASS is not the witness;
# the two readings are.  What the row adds is that this assembler puts
# bit 18 where the listing puts it, which the third injection below
# witnesses by removing it.  With .40 settled, p.45 is
# self-consistent: the two TI instructions there are FULL WORDS at ODD
# half-words (021377.40 and 021400.40, legal per Reference Manual
# p.39), each straddling a word boundary, and the "BE,$+.32  -ENABLE
# AND AWAIT INTERRUPT" after them lands at 021401.40 with its printed
# target 021402.00.  The apparent half-word-short arithmetic was a
# full word read as a half, at a resolution too low to see it.
#
# WHAT THIS IS NOT.  An ENCODING oracle, like the ENSU block above.
# The I6086 fragment cannot run: it needs I6085B's all-NOP interrupt
# table (built by I6085A), the SEN/SERS error harness and the constant
# I60K16.  storage_protection.strap remains the behavioural test and
# remains hand-written; what changed is that its rule now has a deck
# behind it.  Four injections, each with its own named failure set,
# are recorded in verify_ax5b_16086_listing.py's header.

run "I-Box 5 routine 1260's indicator walk + TRANSMIT IMMEDIATE (jb_ax5b p.45)" python3 verify_ax5b_16087_listing.py
# THE BLOCK docs/NEXT.md HAS POINTED AT SINCE 2026-09-21, and the
# reason it waited: it needed an instruction this assembler did not
# have.  Six half-words -- set one indicator bit in word 11, set its
# mask bit in word 12, "BE,$+.32  -ENABLE AND AWAIT INTERRUPT", and a
# BD that is reached only if the machine did NOT interrupt, dispatching
# into the per-indicator error table I60B13 indexed by X6.  It is the
# deck's own version of what interrupt_pg0.strap does hand-written from
# Reference Manual p.48.
#
# TRANSMIT IMMEDIATE CAME FROM THE POCKET CARD, NOT THIS LISTING, which
# is AGENTS.md rule 4.  X22-6533 pcard-1: "TRANSMIT--Strap Format: OP,
# J, A1(I1), A2(I2)", eight mnemonics T/TI/TB/TBI and the four SWAPs.
# pcard-3's "TRANSMIT OPERATIONS" box:
#
#   |   ADDRESS   |1000| I |   ADDRESS   | J |FD|BI|10| I |
#   0            18  24   28  32          51  55    58 60 63
#   SWAP ab110   T ab010    a = forward/backward, b = direct/immediate
#
# opcodes.TRANSMIT_CODES carries that diagram; strap_asm.enc_transmit
# implements it; and it then reproduced BOTH printed half-words of BOTH
# TI rows with nothing read off the page.  Only TI has a listing
# witness -- the other seven are card-only, and the table says so,
# following the CB_CODES precedent.
#
# TWO FULL WORDS AT ODD HALF-WORDS, 021377.40 and 021400.40, each
# straddling a word boundary (Ref. Manual p.39).  That is what made
# this page look a half-word short for a session when its addresses
# were read at 200 dpi.  The straddle was tested in isolation before
# this block was written, because no other program in the suite places
# a full word at an odd half-word.
#
# A 600 DPI CORRECTION, and the injection that makes it matter.  The
# last row is "21402.44 06", not "...00" -- the low digit was lost at
# 200 dpi under an ink smudge.  With 06 the row decomposes cleanly:
# bit 18 set so the target is 021402.40, code 001 = BD, literal 000000,
# index 0110 = $X6, and 021402.40 is exactly where the page prints the
# label I60B13.  Dropping the index field in enc_branch_or_misc fails
# this row and only this row.
#
# THREE SYMBOLS LOCATED, each from its own row's printed address field:
# I60SX1 = 023041.00, I60S1 = 022741.00, I60B13 = 021402.40.
# docs/NEXT.md had carried I60S1/I60SX1 as "not located" ever since the
# claim that they were a prerequisite was disproved.  And BIT0 =
# 024522.00 for the third independent time (p.114's table prints it,
# I6071's BIT18 implies it, this row's A1 field states it).
#
# THE HAZARD THIS CREATES, stated because the assembler can now emit
# Transmit at all: StretchExecute.bsv's Transmit arm moves exactly ONE
# word and ignores both the immediate-count bit and J, so a count other
# than 1 would assemble correctly and execute wrongly rather than
# failing loud.  Every count in this block is 1.  Recorded in
# TRANSMIT_CODES, in strap_asm.py's format list and in strap/README.md.

run "LVS: multiple indexing (RefMan printed p.28)" ./run_program.sh ../decks/lvs_multiple_indexing.strap StretchLvsTb \
    "R1_sum:42=0xf600000000000" "R2_algebraic:43=0x3208000000000" \
    "R3_bits25to63_kept:44=0x16000001c0009" \
    "R4_empty_mask_clears:45=0" "R5_single:46=0x9a00000000000"
# THE OPERATION WHOSE ADDRESS FIELD IS NOT AN ADDRESS.  Reference
# Manual printed p.28, "Multiple Indexing": "bits 0-15 of the address
# part of the instruction are used to indicate which index registers
# participate... When bit position n contains a one, the register Xn
# participates."
#
# MCP printed p.4 line 23 is "LVS,$X1,$X12,$X14  -WORDS PRECEEDING
# MCP", and $X1 is the index the TRANSMIT five rows later uses to find
# MCP inside the buffer -- so this and the MULTI-WORD TRANSMIT section
# above are one piece of work in two halves.  The ASSEMBLER has
# encoded LVS since the MCP transcriptions needed it
# (verify_lvs_encoding.py); the MODEL set Operation Code Invalid on it
# until 2026-10-19.
#
# Five rules, all from p.28:
#   * the mask is a MASK -- step 1 sums MCP's own X12/X14 pairing, so
#     a model reading the address field as a number fails;
#   * the addition is ALGEBRAIC, "taking into account the sign, bit
#     24, of all quantities" -- step 2 sums a positive and a larger
#     negative and must come back negative;
#   * "BITS 25-63 OF THE INDEX WORD SPECIFIED BY J REMAIN UNCHANGED"
#     -- step 3 puts a count and a refill in the destination first and
#     every result is stored with SX, the WHOLE index word, so the
#     surviving fields are visible beside the value that changed.
#     This is the half a careless implementation loses by writing a
#     whole index word;
#   * an EMPTY MASK clears the value field;
#   * one participant is a copy.
#
# THE UNITS ARE NOT THE OBVIOUS ONES and the deck's header says so: a
# value operation's address part is "bits 0-18 ... as bits 0-18 OF THE
# VALUE FIELD" (printed p.25), so "LVI,$X12,100" leaves the value at
# 3200.  The expected words above are therefore sums of multiples of
# 32.
#
# BITS 16-19 vs 16-18: p.28's prose says "Bits 16-19 ... are ignored"
# and the SAME page's format diagram ends ADDRESS at 18, with bit 19
# the high bit of J; X22-6533's IMMEDIATE INDEX ARITHMETIC row agrees
# with the diagram.  Figure and pocket card beat the sentence, and
# both the model and strap_asm.py record the discrepancy where they
# implement it.

run "MULTI-WORD TRANSMIT (RefMan printed p.30)" ./run_program.sh ../decks/transmit_multiword.strap StretchXmitTb \
    "A0:44=0xA000000000000001" "A1:45=0xA000000000000002" \
    "A2:46=0xA000000000000003" "A3:47=0xA000000000000004" \
    "B0:51=0xB000000000000001" "B1:52=0xB000000000000002" \
    "B2:53=0xB000000000000003" "C0:55=0xC000000000000001" \
    "OVL0:56=0xD000000000000001" "OVL1:57=0xD000000000000002" \
    "OVL2:58=0xD000000000000003" "OVL3:59=0xD000000000000004" \
    "OVL4:60=0xD000000000000004" \
    "E0:77=0xE000000000000001" "E15:92=0xE000000000000010"
# THE ARM USED TO EXECUTE EXACTLY ONE SHAPE -- a one-word IMMEDIATE-
# count forward transmit -- and set Operation Code Invalid on every
# other, "conservative by construction" in its own comment.  MCP
# printed p.4 line 28 is an eleven-word DIRECT-count transmit, so
# MCP's IPL was never moved; see the MCP boot section below for how
# that stayed invisible for weeks.
#
# Five rules, all from Reference Manual printed p.30:
#   * a DIRECT count, read from the named index register's count
#     field -- MCP's own shape;
#   * an IMMEDIATE count;
#   * a direct count of ONE, which the old arm refused even though it
#     would have executed it correctly;
#   * ASCENDING, ONE WORD AT A TIME -- the deck shifts a block DOWN by
#     one word, which a descending implementation smears and a
#     snapshot-then-store implementation could not do without four
#     words of hidden state;
#   * an IMMEDIATE count of ZERO IS SIXTEEN ("a zero count field
#     indicates the maximum count of 16 full words").
#
# NOTHING IS WRITTEN BACK, which is what made this cheap.  Same page:
# "The count field in the index register is not changed as a result
# of the operation, and the index result indicators are not
# affected."  So rl_xmit is rl_io's shape with the device taken out
# and no index write-back at all.
#
# rl_xmit's ADDRESS-INVALID CHECK IS LOAD-BEARING.  p.30 on a direct
# count of zero: it "is interpreted as 2^18... such a count is never
# valid.  It is not detected, however, until the data transmission
# actually encounters an invalid or protected address."  2^18 words
# is the whole 18-bit address space, so the first version of the rule
# -- without the check -- wrapped and zeroed every word of core when
# MCP ran it.  Backward transmission and SWAP still set OP and are
# deliberately not tested here; their encodings are pinned by the
# jb_ax4b routine 1246 transcriptions.

run "MCP'S OWN BOOTSTRAP RUNS (boot_plan.md M3)" ./run_mcp_boot.sh StretchMcpBootTb
# THE EXPECTED VALUES CHANGED ON 2026-10-18 WHEN THE DISK LANDED, and
# the change is the useful part.  This section asserts the indicator
# register EXACTLY, as a ratchet.  It used to read 0xA040 -- three
# result indicators with OP clear -- and that was an ARTIFACT:
#
#   printed p.4 line 29 is "REL(SEOP),0.0($X0)  -RELEASE DISK",
#   channel ZERO.  With nothing installed there the model rejected it
#   with Unit Not Ready; line 30 branched to X ERR 12, which is on
#   printed p.15 and OUTSIDE the loaded image; the machine ran into
#   zeros; a zero half-word is BRANCH ENABLED, which enabled the
#   interrupt system with UNRJ pending; and the interrupt RESET THE
#   INDICATOR REGISTER.  The test was measuring the register after
#   the wipe.
#
# Channel 0 now holds the disk, the RELEASE succeeds, MCP runs the
# path it was written to run -- and the OP bit that had been there
# all along became visible.  TWO instructions on that path were
# refused, not one, and the first attribution named only the first:
#
#   p.4 line 28, "T,$11,X BUFER($X1),X BS END  -MOVE MCP IPL", an
#   eleven-word direct-count TRANSMIT.  Built 2026-10-18.
#
#   p.4 line 23, "LVS,$X1,$X12,$X14  -WORDS PRECEEDING MCP",
#   multiple indexing.  Built 2026-10-19.  The two belong together:
#   $X1 is the index the TRANSMIT five rows later uses to find MCP
#   inside the buffer.
#
# WITH BOTH BUILT THERE IS NO OP BIT in the bootstrap.  **The model
# refuses nothing MCP's bootstrap executes**, and this time that is
# measured rather than read off a register an interrupt had just
# cleared.
#
# ===================================================================
# AND SINCE 2026-10-19 THIS SECTION RUNS AN OPERATING SYSTEM
# ===================================================================
# Two changes took it from "the bootstrap finishes" to "MCP
# initializes the machine and diagnoses it":
#
#   A PROSA RECORD ON THE TAPE (strap/prosa.py).  The bootstrap read
#   its dictionary out of empty tape, so every size came back zero.
#   The record's SHAPE is derived from printed p.4 lines 19-27 and
#   its dictionary offsets are chosen; what it CARRIES is real --
#   printed pp.15-18 assembled, eighty words, which land at
#   000621.00 because printed p.15 line 7 is "SLC,X BS END" and that
#   is exactly where the TRANSMIT delivers them.
#
#   A COUNT AND BRANCH TO ITS OWN ADDRESS IS NOT A HALT
#   (StretchCore.bsv's isHalt).  printed p.4 line 32 is "CB,0,$", the
#   131,071-iteration wait after RELEASE DISK, and `halted()` meant
#   "branched to its own address" -- so the run used to end after ONE
#   decrement with everything pp.15-18 do behind it.
#
# WHAT THE MACHINE NOW DOES, in order, all of it checked above:
#   IPLs from tape; sizes core by faulting (98,304 words); finds the
#   IPL channel; spaces the tape mark; fetches PROSA; reads the
#   dictionary, computes the offset with LVS and MOVES ITSELF with
#   TRANSMIT; LOCATEs the disk and WRITEs PROSA to it, polling with
#   CCW; puts the size it measured into the communication region at
#   S ROOF; hunts the buffer for an IOCD card; finds none and reports
#   "-NO IOCD DETECTED"; enters the ERROR ROUTINE; walks all 32
#   exchange channels looking for a console; finds none; leaves the
#   failing address in the R register "-DISPLAY ERROR ADDRESS IN";
#   and stops at printed p.6 line 1, **"BD,$  -LOOP"**, which is
#   IBM's own halt.
#
# SO THE REMAINING OP AND AD ARE THE CONSOLE HUNT, not a surprise:
# Exchange LOC and GONG are unimplemented (boot_plan.md M3++ A4
# builds them with the console), and the walk addresses channels with
# nothing at them.  A machine with no IOCD cards and no console is
# exactly what this model is, and MCP said so.
#
# IT COSTS ABOUT THREE MINUTES, because MCP's delay loop is 131,071
# iterations and they are now actually executed.  That is the price
# of the section being about an operating system rather than about a
# bootstrap.
#
# AND AD IS THE TRANSMIT NOW RUNNING.  Line 24 takes the count out of
# the PROSA record's dictionary and THIS TAPE HAS NO PROSA -- 369
# bootstrap words and a mark, nothing else -- so the count field is
# zero, which RefMan printed p.30 says means 2^18 and "is never
# valid... not detected until the data transmission actually
# encounters an invalid or protected address".  The transmit walks up
# out of installed core and stops with AD, which is the manual's own
# answer.  AD here is the tape being short, not the model being
# wrong.
#
# The run now stops at 000124.40, printed p.4 line 32's "CB,0,$" --
# MCP's delay loop after RELEASE DISK.  The harness halts on "an
# instruction branched to its own address", which is the BEW,$ idiom
# it was built for and is also exactly this loop.  A HARNESS LIMIT,
# not a model one.
# IBM's operating system, executing on this model, off a tape built
# from the thirteen transcribed pages.  It runs end to end and hands
# off to printed p.15's MCP INITIALIZATION, which is not transcribed.
#
# WHAT EACH CHECK IS FOR is in gen_mcp_boot_tb.py; the two that carry
# the claim are:
#   mcp_end_of_prosa_bit_X0 -- printed p.4 line 37's
#     "CM1111(BU,1),$0 +.25 -END OF PROSA FILE" sets word 16 bit 25,
#     and NOTHING EARLIER IN ALL THIRTEEN PAGES WRITES IT.  That bit
#     is the difference between finishing and stopping somewhere
#     quiet.
#   mcp_x_err_ad = 0 -- every error site does "SIC,X ERR AD" first
#     and the instruction counter is never zero inside the bootstrap,
#     so zero means NO ERROR SITE EVER RAN.
# and mcp_x_s_roof says MCP MEASURED THE MACHINE: printed p.2's
# sizing loop found 98,304 words, which is StretchMemory's
# InstalledWords, six units.
#
# THREE MODEL GAPS HAD TO CLOSE FIRST, and the order they surfaced in
# is the argument for running before fixing.  None was top of the
# predicted list:
#   1. ADDRESS INVALID ON A STORE PAST INSTALLED CORE.  printed p.2's
#      clearing loop has NO TERMINATING COUNT -- AD is the only thing
#      that ends it.  The model raised AD for floating-point operands
#      and nowhere else, so the loop wrapped the 24-bit address field
#      and started again from the bottom.  RefMan printed p.21.
#   2. LVE, printed p.3 line 10, without which $15 never gets the
#      channel number and SPFL goes to channel zero.
#   3. SPACE FILE, control code 077, and a tape mark for it to find.
#
# IT HALTS AT PC 0 AND THAT IS THE HAND-OFF, not a failure: printed
# p.4's "B,X 10" goes to 000622.00, one word past X BS END, so the
# machine runs into the zeros above the image.  When printed p.15 is
# transcribed, that becomes a real entry point.

run "INITIAL PROGRAM LOAD from a host file, 19 words (boot_plan.md M0+M1)" ./run_ipl_file_test.sh StretchIplFileTb
# THE SIXTEEN-WORD CEILING, LIFTED.  The IPL test above boots a
# four-word image out of mkTapeSourceVector and proves the SEQUENCE.
# It cannot prove the SCALE: a path that silently truncated at
# sixteen words would pass it unchanged.  This one mounts a 19-word
# image from a real file through mkTapeSourceFile (BDPI) and checks
# MARKER, the last word -- so a truncating path fails there AND
# NOWHERE ELSE, with the program still running and both stores still
# landing.
#
# AND THE SCALE IS WHY IT MATTERS.  MCP's IPL bootstrap is 369 words
# (printed p.2: count 0o560 = 368 plus the control word).  Sixteen is
# not within a factor of twenty of that, so boot_plan.md M3 was
# unattemptable until this existed.
#
# IT BUILDS WITH -D HOST_TAPE AND ITS OWN -bdir, and both are load
# bearing.  import "BDPI" has no Verilog back end -- bsc emits VPI
# wrappers and yosys then cannot resolve the symbol -- so the package
# must never reach a bitstream hierarchy, which is why StretchIO
# selects it behind `ifdef rather than a parameter.  And the two
# builds differ only by that -D while bsc's .bo files record nothing
# about it: a StretchIO.bo built the other way is silently wrong and
# the symptom is a tape that reads zeros, not a compile error.

run "INITIAL PROGRAM LOAD: the machine boots from a tape image (Ref. Man. printed p.126)" ./run_ipl_test.sh StretchIplTb
# THE MACHINE LOADS ITSELF.  docs/boot_plan.md M1's exit test, and it
# transcribes nothing: ../decks/ipl_boot.strap is three instructions
# written here, assembled here, wrapped by mktape.py's own
# pack_control_word, and read off the simulated tape by the hardware
# sequence Reference Manual printed p.126 specifies.
#
# NOTHING IS PRE-LOADED INTO CORE STORAGE.  gen_tb.generate(ipl=True)
# suppresses the program-word load rule entirely, so core starts at
# zero and the tape has to fill it.  Pre-loading would make every
# check below pass even if the IPL read moved nothing -- which is the
# whole reason the flag exists.
#
# THE SEQUENCE, all of it already built: iplStart() plants p.126's
# fixed control word (data address 4, chain 1, count 1, refill 4) and
# reads ONE word; the count exhausts; CHAINING refills from location
# 4, which now holds the word just read off the tape; that word is a
# control word naming where the program goes and how long it is; the
# rest loads under it; and the CPU starts at its data word address.
# Chaining was built two days earlier for exactly this and needed no
# change.
#
# THREE CHECKS THAT SEPARATE FAILURE MODES.  ipl_program_executed is
# end-to-end -- it can only pass if the tape was read, the chain
# refilled, the words landed, and the CPU started in the right place.
# The two loaded-word checks distinguish "the program ran from
# somewhere" from "the program was loaded where p.126 says".  The PC
# check confirms it reached its own halt.  237 clocks, measured.
#
# "BD" IS THE FIRST INSTRUCTION BECAUSE p.126 REQUIRES IT: "the first
# instruction of a program loaded by means of the initial program
# loading technique must be BRANCH DISABLED."  MCP's own bootstrap
# obeys the same rule at its printed p.2 line 24.

run "mktape.py builds an IPL tape image (Ref. Man. printed p.126)" python3 verify_mktape.py
# THE TAPE IMAGE FORMAT, AND IT NEEDED NO TRANSCRIPTION TO SETTLE.
# Two primary sources fix it between them.  ka_ul1 ("LOAD AND TAPE
# WRITE UTILITY", 13 Oct 1961) writes an IPL tape with ONE W against
# one control word -- no tape mark, no label, no header record, so a
# bootable 7030 tape is just its words.  Reference Manual printed
# p.126 fixes what the first of those words is: the exchange plants a
# FIXED control word (data address 4, chain 1, count 1, refill 4),
# reads ONE word into location 4, and refills FROM location 4 -- so
# the tape's first word IS a control word, and it immediately becomes
# the active one.
#
# MCP'S OWN BOOTSTRAP IS THIS SHAPE, which is the corroboration:
# printed p.2 assembles CW(CR),X IPL BS,X BS END-X IPL BS,1 at octal
# 40 -- dataAddr 000041.00, count 0o560 = 368, refill 1 -- with
# "X IPL BS  BD,X BEGIN" immediately after it, matching p.126's "the
# first instruction ... must be BRANCH DISABLED".
#
# WHAT THIS CHECKS AND WHAT IT DOES NOT.  It round-trips the image
# through the byte-for-byte reader bsv/sd_reference/host_tape.c uses
# (big-endian, byte 0 = IBM bits 0-7) and compares every word against
# the assembly, plus five properties of the control word.  It does
# NOT run the model: the IPL mechanism that would consume this does
# not exist yet (docs/boot_plan.md M1).  Settling and testing the
# format first, before the hardware that reads it, is the whole point
# of that milestone order.

run "M+1, Add One to Memory -- the sixth VFL integer arm" ./run_program.sh ../decks/vfl_m_plus_one.strap StretchMPlusOneTb \
    "f6_two_increments_at_w63_58:134=576460752303423493" \
    "f64_whole_word:135=1001" \
    "f4_at_bit_offset_8:136=4503599627370496" \
    "fcarry_255_plus_1_carries:137=72057594037927936"
# MCP PRODUCED THIS GAP AND THE AUDIT CAUGHT IT.  M+1 is the FOURTH
# instruction of IBM's operating system (printed p.2 line 34), and
# until 2026-10-17 the model set Operation Code Invalid on it -- so
# boot_plan.md M3 could have transcribed the whole bootstrap and
# never run a line.  audit_opcode_coverage.py failed the suite the
# first time a program used the mnemonic, which is what that ratchet
# is for.
#
# NOT A DECK TEST, and the program says so.  MCP's rows pin M+1's
# ENCODING bit-exactly; they cannot pin its EXECUTION, because
# running the bootstrap is the goal rather than a tool.  This is a
# hand-written behavioural test against X22-6533's "M+1  Add One to
# Memory  abc101011" and is weaker than a deck oracle.
#
# THE EXPECTATIONS ARE DERIVED, NOT OBSERVED, and the first draft got
# three of four wrong against a CORRECT model by assuming VFL fields
# are right-justified in the word.  They are not: a field at bit
# address A length L occupies IBM bits A..A+L-1, w[63-A : 64-A-L], so
# the increment lands at w[64-A-L].  The program header carries the
# derivation for all four.
#
# The signed case is deliberately NOT tested: MCP uses (BU,6) and no
# source here states the signed interpretation, so writing a test
# would mean inventing its expectation.

run "MCP's IPL bootstrap, printed p.2, bit-exact (MCP_Mar63 PDF p.9)" python3 verify_mcp_bootstrap_p2.py
# THE FIRST PAGE OF IBM's OPERATING SYSTEM IN THIS CORPUS, and the
# first rule-3 check against MCP rather than a diagnostic deck.  All
# six symbols the page defines land at its printed LOCATION column
# and all sixteen machine-code rows match character for character,
# including the IPL control word RefMan p.126 refills from location 4.
#
# GETTING HERE COST FOUR CORRECTIONS, three of them to this project
# rather than to the transcription:
#   - listing_oracle could not print an index or control word (the
#     four-group vvvvvv.vv+ fff cccccc rrrrrr form).
#   - CW's COUNT field needed C22-6531 p.12's integer-vs-bit-address
#     rule, which had been applied only to the two address fields.
#     The count came out eight times too large.
#   - "M+1" is a DIGIT ONE, not "M+I".  Read as M+I the operand
#     becomes an immediate and encode_vfl_immediate left-justifies it
#     per RefMan p.56, which is why the first attempt put the bit
#     part at position 18 and lost the word part.
#   - And the trailing byte is B0, not 80.  At 200 dpi AND at 600 dpi
#     that glyph read as an 8; at 900 dpi it is unmistakably a B.
#     X22-6533 settles the instruction independently: "M+1  Add One
#     to Memory  abc101011", and BU gives a=1 b=0 c=0.
#
# docs/listing_typography.md 11 now carries the B/8 case.

run "M+MG, Add Magnitude to Memory -- the seventh VFL integer arm" ./run_program.sh ../decks/m_plus_mg.strap StretchMPlusMgTb \
    "PC=2064" \
    "mg_t1:1043=105" \
    "mg_t2_acc_sign_ignored:1044=105" \
    "mg_t3_forced_zero:1045=0x80" \
    "mg_t4_same_sign:1046=0x280"
# MCP PRODUCED THIS GAP TOO, and it produced it VISIBLY.  The
# bootstrap's error routine (printed p.5 lines 12-17) folds the
# failing instruction's address into the message it prints on the
# operator's console, and two M+MG(BU) adds are how it does it -- so
# with the operation refused as Operation Code Invalid the console
# printed the message's own placeholder, "000000.0", and the rest of
# the sentence came out right.  A wrong ADDRESS in a correct
# diagnostic is exactly the failure that an end-to-end boot test with
# no field-level check would have passed.
#
# The whole operation is two sentences of Reference Manual printed
# p.62 -- a positive accumulator sign is assumed, and a sum of
# opposite sign to the storage operand stores zero bytes with the
# sign byte untouched -- and Figure 13 on that page tabulates every
# combination.  The deck transcribes two of its rows (3- plus 5+ ->
# 0-, 5- plus 3+ -> 2-) and takes the other two cases from MCP's own
# unsigned use.  Both rules have a measured injection; see the deck
# header.
#
# NOT THE FLOATING-POINT M+MG of RefMan pp.88-89, which has its own
# opcode and its own thirty-two-sub-test deck from jb_af1c routine
# F206B (decks/fp_arith_f206b.strap).  Same mnemonic, different
# instruction.
#
# THE NEGATIVE SIGN MODIFIER IS STILL UNREACHABLE from STRAP: C22-6531
# Appendix A footnote 4 gives the N suffix, this assembler implements
# only I, and the written-minus "M-MG" is witnessed for the
# floating-point operation alone.  docs/NEXT.md carries it.

run "Figure 14 -- IBM's own sign-modifier example, and the N suffix" ./run_program.sh ../decks/fig14_sign_modifiers.strap StretchFig14Tb \
    "PC=2062" \
    "fig14_note1_a_minus_b:1774=0xaaaaaaaaaa00c880" \
    "fig14_notes234:1775=0xc80000c88000c8"
# Reference Manual printed p.64, Figure 14 "Sign Modifier Example",
# transcribed statement for statement at IBM's own addresses: form
# A-B, |A-B|, -|A-B| and A(bar)-B and store them consecutively.  All
# four of the figure's notes are reproduced.
#
# IT SETTLES THE "N" SUFFIX, which docs/NEXT.md had carried as
# unimplementable.  C22-6531 Appendix A footnote 4 -- transcribed in
# docs/c22_6531_appendix_a.md -- gives VFL operations the suffixes
# "I Immediate, N Negative, NI Negative Immediate", and the item said
# a blanket strip-a-trailing-N rule would capture LN, a real FP
# operation.  True of a rule at the top of classify_vfl_or_fp; the
# strip now happens inside the VFL branch, after the data description
# has already returned the floating-point modes N and U.  Figure 14's
# "STN(B,24,8)" and "STN(BU,16,8)" are the usage witness: a VFL data
# description on a VFL operation.
#
# THE DECK CAUGHT ITS OWN TRANSCRIBER FIRST.  Line 1 was typed
# "L(BU,24,8)" against a page printing "L (B, 24, 8)"; an unsigned
# 24-bit load takes the eight-bit sign byte as magnitude, so the
# accumulator held 76800 instead of 300 and note 1 stored 0x2A0C00
# instead of 0xC880.  The arithmetic identified it exactly.
#
# NOTE 4 ASSERTS AN ABSENCE and no injection on N can move it -- the
# figure says "the same result would have been obtained if the
# negative sign modifier had not been used".  printed p.63 is the
# rule: "If the unsigned modifier is specified, the negative sign
# modifier has no effect on the field stored."
#
# Second of IBM's worked examples run on this model.  The first,
# Figure 12 on printed p.61, found that every unsigned subtract was
# an addition.

run "THE REAL printed pp.17-18 execute -- IOCD cards into the CST" ./run_mcp_p17.sh
# >>> decks/mcp_bootstrap_p17.strap IS CHECKED BIT-FOR-BIT AGAINST THE
# LISTING AND HAD NEVER EXECUTED A ROW.  It does now. <<<
#
# "PROCESS IOCD CARDS SETTING UP CST AND LST" runs end to end against
# a synthetic card: it clears the working area with a 1000-word
# TRANSMIT, hunts for the card, identifies it against X IOCD,
# converts its Hollerith channel number to 35, presets 64 channel
# status table entries and indexes to the right one, clears the
# not-available flag, looks up the equipment code and stores it.
#
# >>> AND PRINTED p.18 NOW RUNS WITH IT, so this is the card LOOP and
# no longer one pass through it. <<<  p.18 starts at (8)713.0, which
# is contiguous with p.17's last row at 000712.00, and ends with "B,
# X131" -- back into p.17 line 26.  The two pages are one program and
# are now run as one.
#
# THE CARD STRIDE IS A PUNCHED CARD, which is the derivation this
# merge produced.  p.18 line 43 is "V+I, $13, 15.0" -- advance to the
# next card by FIFTEEN WORDS.  Fifteen 64-bit words is 960 bits, and
# 960 is 80 columns x 12 rows: one IBM card, read as a bit image with
# nothing left over.  The field map in the section below was derived
# from the increments WITHIN a card; this is the number that says the
# card ends where a card ends.
#
# THE RUN EXITS AT X 19, which is the IOCD loop running out of cards
# and not a failure -- the generator's header says so at the point
# where the halt is planted.
#
# >>> A CORRECTION, AND IT IS THE WORST KIND THIS PROJECT CAN MAKE.
# An earlier version of this paragraph said: 'The page's own comment
# on that row is "X 19 IS THE NORMAL END".'  THE PAGE SAYS NO SUCH
# THING.  Printed p.17 line 31's comment is "-NOT AN IOCD CARD".
# "X 19 IS THE NORMAL END" was a heading I wrote in
# gen_mcp_p17_tb.py's own commentary, and writing it up here turned
# my own paraphrase into a quotation attributed to a 1963 listing.
# Every other quoted comment in this file was checked against the
# page; this one was invented, in a file whose entire purpose is
# citing primary sources. <<<
#
# AND IT WAS WRONG AS A FACT TOO, which printed p.19 settles.  X 19
# is not an end at all.  Its first row is
#
#     X19   KF(BU,36),XIOD,12      -COMPARE AGAINST * IOD *
#
# -- thirty-six bits is THREE COLUMNS, the characters "IOD" -- and
# the row after it is "X ERR 19  SIC,X ERR AD" / "BZAEZ,X ERROR"
# commented "-NOT AN IOD CARD EITHER".  So X 19 asks whether the card
# that failed the IOCD test is an IOD card, which is exactly what
# C22-6728 printed p.88 says comes next: "Three types of control
# cards are used: 1. I-O Configuration Definitions (IOCD)  2. MCP
# IOD's (IOD)  3. MCP Parameters (MCPP)."  Reaching the X 19 halt
# means the deck ran out of IOCD cards and initialization moved on.
#
# >>> AND THE TABLE ITSELF IS PRINTED.  C22-6728 printed p.246 =
# PDF p.246, "APPENDIX A -- SYMBOLIC I-O CONTROL TABLES", Figures 137
# and 138.  EVERY BIT THIS SECTION DERIVES IS A NAMED FIELD ON THAT
# PAGE, and the names are the listing's own words: <<<
#
#   bit  printed name   the row that writes it      its comment
#    25  SCHAVL         p.17 l.44 .25($3)           "CHANNEL AVAILABLE"
#    27  SMULTI         p.18 l.9  .27($3)           "MULTI BIT TO ON"
#    29  SUNASG         p.18 l.7  .29($3)           "ASSIGN BIT"
#  0-26  SUNAA          p.18 l.5  SV, $15, 0.0($3)  "UNIT STATUS TABLE
#        "Address of Unit                            ADDRESS IN CST"
#         Status Table"
#  52-55 SEQUIP         p.17 l.54 ST(BU,4), .52     "INSERT IN CST"
#  59-62 SUNITK         p.18 l.30/37 at .59         "UNIT COUNT IN CST"
#
# and in the UNIT status table entry, which $15 walks:
#
#    27  SDISPO         p.18 l.23 .27($15)          "TAPE DISPOSITION"
#    28  SUNAVL         p.18 l.21 .28($15)          "UNIT AVAILABLE"
#    29  SUNASG         p.18 l.22 .29($15)          "UNIT NOT ASSIGNED"
#    39  SSEL           p.18 l.24 .39($15)          "SELECT STATUS"
#
# Ten for ten.  SDISPO is disposition, SSEL is select, SUNAVL is unit
# available: the 1963 comments and the 1963 field names are the same
# words, and this project put them together from opposite ends
# without having seen either page name the other.  The page also
# states outright what CB+'s one-word step was used to derive -- "AN
# ENTRY IN THESE TABLES CONSISTS OF ONE WORD" -- and names the
# program: "The tables are constructed by the Initializer program at
# IPL time from IOCD cards defining the I-O configuration."
#
# ONE AMBIGUITY, AND THE CODE RESOLVES IT.  Figure 138's tick labels
# do not survive magnification well enough to fix the right-hand edge
# of SEQUIP and SUNITK.  MCP settles both: the equipment code is
# stored by "ST(BU,4), .52", four bits at 52, so SEQUIP is 52-55; and
# SUNITK must be EXACTLY 59-62, because p.18 line 30 sets a SINGLE
# bit at .59 under the comment "UNIT COUNT IN CST TO 8", and one bit
# at the left of a field means eight only if the field is four bits
# wide.  A five-bit field would make that row write sixteen.  The
# project's standing principle running the other way for once: the
# page exists, its drawing is ambiguous, and the program
# disambiguates the drawing.
#
# THE CST ENTRY IS DERIVED ONE PRINTED LINE AT A TIME and the
# generator now reads as that list:
#
#   p.17 l.22  preset            bit 25 not available, 29 not assigned
#   p.17 l.44  CM0000(BU,1),.25  bit 25 off -- channel IS available
#   p.17 l.54  ST(BU,4)          bits 52-55 = equipment code 6
#   p.18 l.5   SV, $15, 0.0($3)  UST address into bits 0-23
#   p.18 l.7   CM0000(BU,1),.29  "MEANINGLESS ASSIGN BIT" off
#   p.18 l.9   CM1111(BU,1),.27  MULTI bit on
#   p.18 l.42  CM0000(BU,17)     X17 clears SEVENTEEN bits of it again
#
# and comes out 0x1000000600.  Every bit of that word is accounted
# for by a row of the listing; nothing in it is an observation
# promoted to an expectation.
#
# ONE CORRECTION WORTH THE SPACE: the first expectation put the UST
# address one bit too low, because I wrote the index value as a
# 25-bit field spanning bits 0-24.  SV stores the value AND its sign:
# the 24-bit address lands at bits 0-23 and the SIGN at bit 24.  The
# measurement was off by exactly a factor of two per bit of
# misalignment, which is how a field-width mistake announces itself.
#
# WHY LINE 42 RUNS AT ALL, since it is the row that throws the
# address away: p.18 line 32 compares $15's count against 8, line 4
# had just SET it to 8, and this card carries no unit entries -- so
# the compare is equal and line 33's "BXE, X17" fires, the branch
# commented "NO UNITS AT ALL ON MULTI CHANNEL".  A channel with no
# units gets no unit status table, so MCP takes the table address
# back out of the entry.
#
# THAT MAKES THE THIRD CHECK THE WITNESS FOR THE FIRST.  $15 lives at
# word 31, and reaching X17 means its count was never decremented, so
# the word still holds the UST base and the 8 that line 4 put there.
# The entry's value depends on which way line 33 went; this check is
# what says which way that was, independently of the entry.
#
# This is the page, not a paraphrase of it.  The neighbouring decks
# transcribe p.17's rows by hand; this runs the transcription.
#
# A TESTBENCH OF ITS OWN, because gen_tb's ipl=True path preloads
# NOTHING on purpose -- "core storage starts empty and the tape fills
# it" -- and the cards, X IOCD and the equipment table live at
# addresses the transcribed tape does not carry.  Preloading them
# into the MCP boot test would weaken the one invariant that test
# exists to protect.  There is no IPL here and nothing to undermine.
#
# DERIVED vs INVENTED, as always: the card's field map, the equipment
# table's 29-bit entry layout, and the one-word-per-channel CST
# indexing are DERIVED from the page's own instructions.
#
# AND TWO THINGS CROSSED THAT LINE when the card code turned up in
# C22-6678-1's Appendix F.  X IOCD's pattern is now the four
# characters IOCD punched -- 0x801408840820, top bit set because "I"
# is 12-9 -- instead of a constant chosen to have that bit set.  And
# the equipment letters are now PUNCHED CHARACTERS: the card's was
# 0xABC, which puts seven holes in one column and is not any
# character, where p.17 line 46 reads twelve bits commented "-SECOND
# LETTER OF ... EQUIPMENT CODE" and advances TWO columns.  Which
# letter means which equipment is still invented; that it is a letter
# is not.
#
# TWO THINGS THE RUN TAUGHT, both of them fixture bugs rather than
# model bugs, and both worth keeping:
#
#   THE FILL PATTERN IS CARD-SHAPED.  gen_tb fills unwritten core
#   with 0xAAAA..., whose bit 44 is SET -- so "BB, 1.44($4)" finds a
#   card in uninitialised memory on its first test.  The page then
#   walked noise and took its "NOT AN IOCD CARD" exit, which is the
#   correct response.  The buffer is now explicitly zeroed, standing
#   in for the rest of the assembled system that would really be
#   there.
#
#   CHANNEL AVAILABLE IS ACTIVE-LOW.  Line 43's BB branches AWAY,
#   past line 44, when the card's bit is ONE; line 44 -- the row
#   commented "-YES * CHANNEL AVAILABLE FLAG TO ON" -- runs only when
#   it is ZERO.  Setting it to one left the CST's not-available flag
#   standing while every other check passed, which is how the sense
#   was identified.
#
# TWO MEASURED INJECTIONS FOR THE p.18 PATH, both in the FIXTURE and
# not in the deck -- mcp_bootstrap_p18.strap is checked bit-for-bit
# against the listing by verify_mcp_bootstrap_p18.py, so an injection
# that edited it would be testing a different page.
#
#   1. CLEAR THE TAPE FLAG on the matched equipment entry.  p.18 line
#      2 is "BZB, -.1($1), X18" -- "-TAPE EQUIPMENT TYPE ENTRY" --
#      and X18 is (8)740.40, the empty low half of p.18's LAST word,
#      i.e. the first instruction of untranscribed p.19.  Observed:
#      PC 961, which is 30752/32, the X18 halt; the CST entry falls
#      back to 0x400000600; and the UST counter word loses its 8.
#      THE ENTRY'S FALLBACK VALUE IS EXACTLY WHAT THIS SECTION
#      ASSERTED BEFORE p.18 WAS MERGED, so the injection measures
#      p.18's contribution as a difference.
#
#   2. REMOVE THE CARD'S LETTER FROM THE EQUIPMENT TABLE.  Observed:
#      PC 182, which is 5824/32 -- X ERROR, MCP's "WRONG EQUIPMENT
#      CODE" exit -- and the entry stops at 0x400000000, available
#      but with no code and the "not assigned" bit still standing,
#      because p.18 never ran.
#
# AND THE 29TH BIT OF AN EQUIPMENT ENTRY IS A TAPE FLAG, NOT A SPARE.
# The section below derives the entry as 24 bits of Hollerith letter
# plus a 4-bit code plus "1 spare"; p.18 line 2 tests that spare bit
# and branches on it.  The structure's own page is still missing, but
# the second program to read it has now named its last field.

run "p.18's UNIT loop -- a card carrying units, and the unit count" ./run_mcp_p17.sh StretchMcpP17UnitsTb units
# >>> THE SAME TWO PAGES, WITH UNIT COLUMNS ON THE CARD, which sends
# printed p.18 down its OTHER arm: lines 13-24's per-unit loop and
# lines 32-37's count.  EVERY CHECK PASSED ON THE FIRST RUN, each one
# predicted from the listing before the simulator was built. <<<
#
# A UNIT IS A PUNCHED COLUMN, and the increments say so twice over.
# p.18 line 13 is "CT0011(V+I)(BU,12), .12($4)" -- read TWELVE bits,
# advance TWELVE -- so a unit entry is twelve rows, one column.  The
# card stride confirms it from the other end: 80 columns x 12 rows =
# 960 bits = line 43's fifteen words.  Lines 16-17 then test single
# ROWS of that column, ten and twelve bits BACK from where the read
# left $4, and p.17's walk left $4 at card+216 -- column 18.
#
# THE TWO UNITS ARE PUNCHED DIFFERENTLY ON PURPOSE.  The page's
# comments read backwards against what X15 1 and X15 2 do: line 16 is
# commented "-UNIT AVAILABLE" and branches to X15 2, which does NOT
# set the bit the listing calls "UNIT AVAILABLE BIT ON".  Punching
# both units the same way would measure nothing about that.  Unit 1
# takes the X15 2 route, unit 2 the X15 1 route, and the two UST
# words come out differing in exactly bit 28 -- so the routing is a
# measurement and not a reading of the comments.  Same shape as the
# tens/units split that caught the progressive-indexing misread.
#
# A UST ENTRY IS ONE WORD, derived twice independently: X15 1/X15 2
# write bits .27 .28 .29 .39 of ($15), all inside one word, and CB+
# steps $15 by "one in bit position 17" -- 64 bits.
#
# >>> AND THIS IS THE RUN THAT EXERCISES THE UNSIGNED SUBTRACT. <<<
# Lines 34-37 are "LFI(BU,18), 8.0" / "-(BU,18), $15+.28" /
# "ST(BU,4), .59($3)": eight, minus what is LEFT of the counter, into
# the CST entry.  Two units leave the counter at 6, and the entry's
# count field comes out 2.  THE "-(BU,18)" IS THE OPERATION FIGURE 12
# ON PRINTED p.61 CAUGHT THIS WEEK -- every unsigned subtract was
# being done as an addition -- and the no-units run cannot reach it,
# because line 33's "BXE, X17" jumps over it.  So the two modes
# together are what make the repair tested by MCP and not only by
# IBM's own worked example.
#
# "8.0" IS EIGHT, NOT 512, and the deck header has the evidence: the
# immediate assembles into the 24-bit address field as 000010.00 --
# word 8, bit 0 -- and an 18-bit operand taken from that field's bits
# 0-17 is the WORD number, 512 >> 6 = 8.  The subtrahend has the same
# shape: "$15+.28" is word 31 bit 28, and eighteen bits from there is
# exactly the count field.  Worth pinning rather than assuming: 512
# would have given 512-6 = 506 and ST's low four bits are 10, a
# number small and plausible enough to pass a glance.
#
# THE COUNT FIELD IS BITS 59-62, derived from the pair of rows that
# write it.  Line 37 stores FOUR bits at offset .59; line 30 -- the
# "eight units" arm -- sets ONE bit at the same offset and is
# commented "UNIT COUNT IN CST TO 8".  One bit at the left of a
# four-bit field IS eight, so the field runs 59-62 and not 56-59.
#
# AND X17 IS NOT REACHED HERE, so the UST address line 5 stored
# SURVIVES in the entry's bits 0-23 -- which is the point of line 5
# having stored it.  The no-units run has the same entry with those
# bits cleared, so the two modes separate "the entry" from "the
# counter that decided what went in it", which a single mode cannot.
#
# THE INJECTION IS p.18's OWN "IOCD PUNCHED INCORRECTLY".  Punch a
# unit column on a row that is NEITHER of the two the page tests and
# both BBs miss: line 19's "SIC, XERRAD" and line 20's "B, XERROR"
# fire.  Observed PC 182 = 5824/32, X ERROR, with the UST entirely
# untouched and the counter still at 8.  This one reaches X ERROR
# from INSIDE p.18, unlike the equipment-table injection on the
# section above, which reaches it from p.17's lookup and so only
# proves p.18 was never entered.
#
# AND IT CORROBORATED SIC's FIELD RULE, 19 bits, from MCP.  X ERR AD
# came back 0x0074eaaaaaaaaaaa over 0xAAAA... fill: nineteen bits of
# 000723.40 at the left and the rest undisturbed.  Reference Manual
# printed pp.41-42: the counter goes "in bits 0-18 of the half-word",
# "other bits of the half-word are not disturbed", and the stored
# value "always address[es] the instruction whose location is next
# higher in storage than the branch instruction to which SIC is
# prefixed".  XERR18 is at 000722.40, its inner "B, XERROR" is the
# right half at 000723.00, and 000723.40 is X15 1 -- the next
# half-word.  All three clauses of the rule in one word, measured
# from a 1963 program's error exit rather than from a deck written to
# test it.

run "p.18's EIGHT-unit arm -- the counter runs out, and p.18 is covered" ./run_mcp_p17.sh StretchMcpP17Units8Tb units8
# >>> p.18's LAST UNTESTED BRANCH.  Eight units run the counter out,
# so line 28's CB+ stops branching and line 30 -- "CM1111(BU,1),
# .59($3)", commented "UNIT COUNT IN CST TO 8" -- runs INSTEAD of
# lines 32-37's subtract.  With this, every branch of printed p.18 has
# been executed. <<<
#
# TWO ARMS WRITE THE SAME FIELD BY DIFFERENT MEANS, and the value
# alone CANNOT tell them apart: the subtract would give 8 - 0 = 8,
# which is exactly what line 30's single bit gives.  That is worth
# saying plainly, because it is the reason this section needed more
# than one check.
#
# SO TWO MORE COLUMNS ARE PUNCHED PAST THE EIGHTH, and without them
# the test is vacuous twice over.  Punching exactly eight leaves two
# things that could have ended the loop -- the counter running out, or
# the ninth column being blank and line 14's BRZ taking it -- and
# nothing in the run distinguishes them.  Columns 9 and 10 are
# punched, on row +0 so a loop that ran on would write a UST word
# with bit 28 SET, visibly different from the eight before it rather
# than merely present.  "The ninth column was never read" then
# becomes a measurement, and it is the only thing in either units run
# that separates line 30's arm from lines 32-37's.
#
# AND THE CYCLE COUNT IS IDENTICAL -- 20176 with the two extra
# columns punched and 20176 without -- which is the same fact from
# the other side: two punched columns that cost nothing were not
# looked at.
#
# THE INJECTION LEAVES THE EIGHTH COLUMN BLANK, so seven units are
# punched and the BRZ, not the counter, ends the list.  Observed, all
# three moving together:
#   CST entry        0x...60e, not 0x...610 -- the count field at bits
#                    59-62 reads SEVEN, and 7 is a value only the
#                    SUBTRACT can produce; line 30 can only write 8
#   $15 (word 31)    value +7 words, counter remainder 1, not 0
#   UST entry 7      empty
# and entries 8 and 9 stay untouched, because the blank column
# stopped the walk before the punched ones.  That is the pair of arms
# separated by measurement: 8 with the counter at 0 from line 30,
# 7 with the counter at 1 from the subtract.

run "MCP's whole per-card path, printed p.17, over a synthetic IOCD card" ./run_program.sh ../decks/mcp_p17_card.strap StretchP17CardTb \
    "PC=2087" \
    "p17_channel_number:1080=0x8c00000000000" \
    "p17_equipment_code:1081=0x600" \
    "p17_card_walk_ended:1082=0x1099800002c0000"
# Find the card, identify it, convert its channel number, look up its
# equipment code -- lines 12-16, 26-36 and 46-54 run together over
# one synthetic card.
#
# THE CARD'S FIELD MAP IS DERIVED FROM THE PAGE'S OWN INCREMENTS,
# which is the result this deck records.  Under progressive indexing
# the effective address IS the index value and the address field is
# the INCREMENT, so the walk reads straight off the four rows:
#
#   offset  len  field              instruction            advance
#        0    8  card type          CT0111(V+I)(BU,8),1.44     108
#      108   48  IOCD identifier    L(V+I)(BU,48),.48+.2        50
#      158    7  tens column        CT0011(V+I)(BU,7),.12       12
#      170   16  units column       CT0011(V+I)(BU,16),.22      22
#      192   12  equipment letter   L(V+I)(BU,12),.24           24
#      204    1  channel available  BB,.12($4)            no advance
#
# AND THE HUNT'S TEST FALLS ON THE IDENTIFIER'S LEADING BIT: line 13
# is "BB, 1.44($4)" with the comment "-IF ZONE BIT OF IOCD", and 1.44
# is 108 bits -- exactly where the identifier starts.  The hunt steps
# a WHOLE WORD, because the pocket card gives CB+ as "Add one in bit
# position 17" and bit 17 of a 24-bit bit address is 64 bits, which
# is what line 12's "-TEST 14 WORDS" means.
#
# >>> AND THE CARD'S COLUMN FORMAT IS PRINTED.  C22-6728 printed
# p.88, found through that document's own INDEX ("IOCD CARDS ... 88"):
#
#   "The IOCD cards ... have the following fixed fields:
#      Cols. 10-13 -- Card Type: contains the characters, IOCD.
#      Cols. 14-15 -- Channel Number: contains the decimal number of
#                     the channel.
#      Cols. 16-17 -- Equipment: must contain one of the following
#                     codes:  CN Console  DK Disk  PR Printer
#                             PU Punch    TP Tape  RD Reader"
#
# EVERY FIELD ABOVE IS CONFIRMED, including the one this file had
# labelled an inference rather than a derivation: the keyword IS the
# literal string IOCD.  And the page explains something no amount of
# reading p.17 would have given -- the six codes' second letters are
# N, K, R, U, P, D, ALL DISTINCT -- which is why line 46 reads twelve
# bits and not twenty-four.  The card's CONTENTS are no longer
# invented; what remains invented is the equipment table's four-bit
# codes, which are on a page nobody has transcribed. <<<
#
# THE THIRD CHECK WAS PREDICTED WRONG TWICE and both corrections are
# facts about the page.  The value is buffer+408, not +384: line 46's
# L advances $4 by its own address field AFTER reading, so the walk
# does not stop at the last field it reads.  The count is 11, not 10:
# CB+ decrements only on a MISS, and the BB that finds the card
# branches away before the fourth step.
#
# THE INJECTION IS CAUGHT BY THE CARD'S OWN IDENTIFICATION.
# Progressive indexing made not to advance reads the identifier at
# the card-type offset, the compare against X IOCD fails, and BZAE
# takes the "NOT AN IOCD CARD" exit.  The hunt is untouched -- BB and
# CB+ are not progressive -- so it shows the WALK failing while the
# SEARCH still works, which is the whole distinction the geometry is
# about.

run "MCP's equipment-code lookup, printed p.17 lines 46-54" ./run_program.sh ../decks/mcp_p17_equipment_code.strap StretchP17EqpTb \
    "PC=2064" \
    "p17_equipment_code_in_cst:1064=0x600" \
    "p17_search_examined_four_slots:1065=0x106b40000180000"
# The last piece of p.17's per-card work: take the second letter of a
# card's Hollerith equipment code, search X EQP T for it, and put the
# matching four-bit code in the channel status table entry.
#
# THE TABLE'S LAYOUT IS DERIVED FROM THE CODE THAT READS IT, which is
# the point of this deck as much as the execution is.  X EQP T sits
# on an untranscribed page, so its CONTENTS are a fixture -- but its
# SHAPE follows:
#   * "KF(V+I)(BU,24), .29($1)" compares TWENTY-FOUR bits and, under
#     progressive indexing, advances $1 by the address field --
#     TWENTY-NINE.  An entry is 29 bits and only its first 24 are the
#     comparand.
#   * "L(BU,4), -.5($1)" then reads FOUR bits five back from where
#     the match left $1, i.e. the entry's bits 24-27.
#   entry = [24-bit Hollerith letter][4-bit equipment code][1 spare]
# Same kind of derivation the PROSA dictionary's shape got from
# printed p.4: the program that reads a structure is a primary source
# for the structure, even when the structure's own page is missing.
#
# THE SECOND CHECK IS THE WHOLE INDEX WORD, value and count, and the
# COUNT is the better half -- it says HOW MANY SLOTS WERE EXAMINED,
# four for the fourth entry, which a search that found the right
# answer the wrong way could not reproduce.  I noticed that by
# getting the expectation wrong: asserting the value field alone
# failed by exactly 6 << 18.
#
# THE INJECTION IS CAUGHT BY MCP'S OWN ERROR EXIT.  Progressive
# indexing made not to advance leaves the search comparing the first
# entry ten times, the count runs out, and CBZ takes the "WRONG
# EQUIPMENT CODE" branch -- a 1963 bootstrap's error path firing for
# the right reason.

run "MCP's Hollerith channel-number conversion, printed p.17 lines 32-36" ./run_program.sh ../decks/mcp_p17_channel_number.strap StretchP17ChanTb \
    "PC=2062" \
    "p17_tens_times_ten:1041=0x7800000000000" \
    "p17_channel_number:1042=0x8c00000000000" \
    "p17_index_advanced:1043=0x104220000000000"
# >>> THE FOUR ROWS THAT THREE DAYS OF WORK WERE FOR, run exactly as
# the page writes them, progressive indexing included. <<<
#
#   X132    CT0011(V+I)(BU,7), .12($4)   -TEST TENS POSITION
#           LCV(DU,8,4), $LZC+.3, 46     -CONVERT TO OCTAL NUMBER
#   X132AA  CT0011(V+I)(BU,16), .22($4)  -TEST UNITS POSITION
#           +(BU,4), $LZC+.3, 46         -FORM CHANNEL NUMBER
#
# A HOLLERITH DIGIT IS A POSITION, NOT A VALUE -- one punch among
# several rows of a card column.  CONNECT FOR TEST discards its
# result and sets only the counts, so running it over the column
# leaves the number of zeros to the left of the punch, THE DIGIT
# ITSELF, in the left-zeros counter.  "$LZC+.3" is word 7 bit 20, so
# an eight-bit field there is the counter's low nibble over four zero
# bits: the tens digit followed by a zero.  LOAD CONVERTED reads that
# as two decimal digits and leaves tens*10 at offset 46; the second
# CONNECT FOR TEST puts the units digit in the counter and the
# four-bit add finishes the number.
#
# THREE THINGS HAD TO EXIST AND NONE WAS REACHABLE ON MONDAY: KF,
# which two rows earlier decides the card IS an IOCD card; LCV; and
# the connective counts.  Each alone was not enough -- building LCV
# without the counters converts nothing, because the counter is where
# its input comes from.  That is exactly why boot_plan.md A2 looked
# finished and was not.
#
# THE INDEX-ADVANCE CHECK IS NOT DECORATION.  Under progressive
# indexing the EFFECTIVE ADDRESS IS THE INDEX VALUE and the address
# field is the INCREMENT, not an offset.  The deck was first built on
# the other reading, with the punches twelve and thirty-four bits in;
# it reported a tens digit of 7 -- the all-zero count, that field
# being empty -- and a units digit of 3, WHILE THE ADVANCE CHECK
# PASSED.  Walking right and reading wrong is only distinguishable
# because the two are checked separately.
#
# The injection, LCV copying the digit bits instead of converting
# them, reads 0x30 as 48 and makes the channel 53 -- moving the two
# value checks and not the advance, which is the other half of the
# same split.

run "The connective counts at word 7 (pp.75-76)" ./run_program.sh ../decks/connective_counts.strap StretchConnCntTb \
    "PC=2086" \
    "cnt_punch_at_left:1079=0x2000" \
    "cnt_punch_two_in:1080=0x20000002000" \
    "cnt_punch_at_right:1081=0x60000002000" \
    "cnt_no_punch:1082=0x70000000000" \
    "cnt_four_punches:1083=0x8000" \
    "cnt_cm_counts_contracted:1084=0x9000000c000"
# Reference Manual printed p.75: "Two counts describing the result
# field are available after a connective operation.  The seven-bit
# all-ones counter, bits 44-50 of location 7 ... The seven-bit
# left-zeros counter, bits 17-23 of location 7, contains a count of
# [p.76] the number of zeros in the result field that are to the left
# of the most significant one-bit."
#
# ARRIVED VIA MCP, and not obviously from the counters' names.
# Printed p.17 lines 32-36 convert an IOCD card's channel number out
# of Hollerith, and a Hollerith digit is one punch among several
# rows -- so CONNECT FOR TEST over the column leaves THE DIGIT ITSELF
# as the left-zeros count, which MCP reads back as "$LZC+.3".
# Building LCV alone did not make that page run; this is the rest of
# it.
#
# THE SPLIT IN p.76 IS WHAT THE DECK IS SHAPED AROUND: "In CONNECT
# and CONNECT FOR TEST, the counts are made on the result field with
# byte size eight.  In CONNECT TO MEMORY, the counts are made on the
# result field after it is converted to the byte size of the storage
# operand."  Blocks 1-5 are the first case and block 6 the second,
# and the injection that forces a wrong result-field width moves the
# five and not the sixth.
#
# ONE INFERENCE, LABELLED: the all-zero case, which the page does not
# state.  With no one-bit there is nothing for the zeros to be to the
# left of, so the count is the field width -- block 4.
#
# >>> THE SCHEDULING IS WHY THIS TOOK TEN ATTEMPTS, and the shape of
# the answer is in StretchStorage: **writeWord does not write the
# counter fields at all.**  Routing them through it makes every
# connective a conflict, because a CONNECT TO MEMORY stores its
# result through a DYNAMIC address in the same arm and bsc cannot see
# that the address is not 7.  Nine arrangements of CRegs, ports and
# call sites each moved the conflict rather than removing it; giving
# each counter exactly ONE writer removed it.  The cost is a
# documented simplification -- a program storing to word 7 leaves the
# counts alone -- which is the same one this model already makes for
# the indicator register at word 11. <<<

run "LCV, Load Converted -- decimal to binary, pp.71-73" ./run_program.sh ../decks/load_converted.strap StretchLcvTb \
    "PC=2082" \
    "lcv_mcp_shape:1059=37" \
    "lcv_at_offset_46:1060=0x9400000000000" \
    "lcv_six_digits:1061=123456" \
    "lcv_signed_magnitude:1062=37" \
    "lcv_signed_indicators:1063=0x90" \
    "lcv_n_modifier_magnitude:1064=37" \
    "lcv_n_modifier_indicators:1065=0x90"
# >>> WITH THIS, BOTH OPERATIONS THAT STOOD BETWEEN MCP AND KNOWING
# WHAT DEVICES IT IS RUNNING ON ARE BUILT.  docs/boot_plan.md A2 is
# closed: KF on 2026-10-19, LCV today. <<<
#
# Reference Manual printed p.72: "The addressed storage field is
# converted as an integer from decimal to binary or from binary to
# decimal depending on the setting of the radix modifier.  THE
# ACCUMULATOR IS CLEARED AND THE CONVERTED FIELD IS PLACED INTO IT AT
# THE SPECIFIED OFFSET."
#
# THE MODEL REFUSED LCV OUTRIGHT, and the reason it did was a
# misreading of one bit.  The VFL arm sets Operation Code Invalid on
# the decimal modifier across the board, because decimal arithmetic
# is unimplemented.  But printed p.71 says of the radix conversions:
# "bit 53, the radix modifier, DESCRIBES THE FORMAT OF THE ORIGINAL
# FIELD and also determines the type of conversion".  On LCV the bit
# selects a DIRECTION, not decimal arithmetic -- so the guard was
# refusing the operation's normal case.  The audit had this recorded
# as "building it means building decimal mode, not one arm", which
# was wrong and is corrected there.  Decimal ARITHMETIC is still
# unimplemented and still refused.
#
# Blocks 1 and 2 are MCP's own shape, printed p.17 line 34's
# "LCV(DU,8,4),$LZC+.3,46" -- two decimal digits -- run at offset 0
# and at MCP's own offset of 46.
#
# TWO INJECTIONS, MEASURED, separating the conversion from the
# placement.  A raw copy of the digit bits in place of the conversion
# fails FIVE value checks (55 for 37, 1193046 for 123456) and NEITHER
# indicator check, since a BCD field read as binary is still negative
# and still short of fifteen digits.  Ignoring the offset fails T2
# ALONE, and fails it to exactly T1's value -- which is what makes
# running the same conversion at two offsets worth the extra
# instructions.
#
# ONLY DECIMAL-TO-BINARY IS BUILT.  The other direction wants
# repeated division by ten and nothing in the corpus calls for it; a
# binary source sets OP rather than being silently wrong.

run "C22-6578 Problem 1.6 -- three methods, IBM's own cross-check" ./run_program.sh ../decks/problem_1_6.strap StretchP16Tb \
    "PC=2066" \
    "p16_method1_bbn_lvs:1050=0x11800000000000" \
    "p16_comment_b_vplus:1051=0x11800000000000" \
    "p16_comment_f_cm1100:1052=0x11800000000000"
# "Subtract the value field $1 from that of $14 and put the result in
# the value field of $14."  Method 1 flips the sign bit of $1's value
# field and adds with LVS; comment (b) offers "V+, $14, 17.0" in
# place of the LVS, and comment (f) offers "CM1100(BU, 1), 17.24" in
# place of the BBN.  All three are here, so the page supplies its own
# cross-check and a disagreement is the failure rather than a number
# somebody has to believe.
#
# "17.24" IS NOT A DATA ADDRESS.  Index register n lives at word
# 16+n, so word 17 IS $1, and bit 24 of an index word is the value
# field's sign.  Method 1 reaches into the index register file
# through ordinary storage addressing to flip one bit; method (f)
# does the same with a one-bit CONNECT TO MEMORY.  That they agree
# with each other and with V+ is a statement about the index
# registers being addressable as storage at all.
#
# FIRST EXTERNAL EXERCISE OF LVS, which was built 2026-10-19 from
# Reference Manual printed p.28 and until now driven only by a deck
# written here beside it.  Comment (a) is the rule that deck was
# built against -- "the index registers to be added together must all
# be different from each other.  The J field, however, may refer to
# any index register" -- and Method 1 is an instance of it, J = $14
# while the summed registers are $1 and $14.
#
# The injection partitions the three by which uses LVS: with LVS
# ignoring the summed signs, R1 and R3 read 130.0 and R2 still reads
# 70.0.

run "R23-9694 p.51 Ex.3 -- overlapping TRANSMIT, and the order is the point" ./run_program.sh ../decks/ce_vol2_transmit_fill.strap StretchCeXmitTb \
    "PC=2051" \
    "xmit_source_500_kept:500=0x123456789abcdef0" \
    "xmit_first_501:501=0x123456789abcdef0" \
    "xmit_middle_550:550=0x123456789abcdef0" \
    "xmit_last_600:600=0x123456789abcdef0" \
    "xmit_601_untouched:601=0xaaaaaaaaaaaaaaaa"
# "Assume that location 500 contains a particular configuration
# which, for test purposes, the customer engineer wishes to store in
# location 501 through 600" -- LCI a count of 100, then "T, $X7,
# 500.0, 501.0", with the remark "500 to 501, 501 to 502, 502 to 503,
# etc."
#
# THE OVERLAP IS THE POINT.  Source and destination differ by one
# word, so each word is written before it is read as the next source
# and ONE word is smeared across a hundred.  A model that gathered
# all hundred source words before storing any, or that copied from
# the high end down, would move the original contents up by one
# instead.  The facing Example 2 states which it must be: of a move
# that must NOT propagate, "backward transmission must be used so
# that each location is used for sending before it is used for
# receiving".
#
# FIRST EXERCISE OF THE DIRECT-COUNT TRANSMIT FROM AN INDEPENDENT
# SOURCE, and the first anywhere that depends on the copy ORDER
# rather than only on the count and the endpoints.
#
# 601 IS A FENCE.  A transmit running one word long would be
# invisible to every other check; the injection that runs one word
# SHORT moves only the 600 check, which is what that one is for.

run "IBM's own MULTIPLY/STORE ROOT/DIVIDE self-check (R23-9694 p.82)" ./run_program.sh ../decks/ce_vol2_sqrt_check.strap StretchSqrtChkTb \
    "PC=2056" \
    "sqrt_temp_holds_the_root:1041=0x4c000000000000"
# R23-9694 printed p.82, the Programming Example under STORE ROOT:
# "Assume a short routine is to check the operation of the
# instructions MULTIPLY, DIVIDE, and STORE ROOT.  One method is to
# multiply a number by itself to form the square of the number, then
# divide the square of the number by the original number and compare
# the result with the result of a STORE ROOT instruction."
#
# A SELF-CHECKING PROGRAM, which is a different kind of oracle from
# anything else in this suite.  No expected value was derived or
# transcribed: IBM wrote the comparison and the error branch, and the
# test is whether 200 iterations reach NEXT rather than ERROR.
#
# PC 2056 is NEXT and 2057 is ERROR, one half-word apart, so the
# check is simply which of IBM's two exits the machine took.
#
# TEMP IS CHECKED AS WELL AS THE BRANCH, deliberately.  A STORE ROOT
# that stored nothing would leave TEMP at its initial value and the
# comparison would be against whatever the quotient happened to be --
# the branch alone could pass on a coincidence.  TEMP = 3.0 says the
# root was actually computed and stored.
#
# THE INJECTION IS THE POINT.  STORE ROOT made to store the
# accumulator instead of its root puts 9.0 in TEMP and halts at
# ERROR: a 1961 diagnostic routine detecting, unmodified, the fault
# it was written to detect.
#
# NUMBER is 3.0 -- positive with an exponent well within the N range,
# as the page requires, and exact in the 48-bit fraction at every
# step (3, 9, sqrt(9), 9/3), so the test is about the four
# instructions and not about rounding.

run "C22-6578 A4.8 integer-address and point identities" python3 verify_c22_6578_a4_addresses.py
# C22-6578 Appendix A4.8 states, and this suite had never checked, how
# a BARE INTEGER in an address field becomes a bit address: "the
# integer address is treated as an integer of the subfield ... the
# left margin of the subfield is placed in juxtaposition with the
# leading bit of the address field", with a table giving the subfield
# size per instruction class.  Nine worked equivalences on printed
# pp.63-64, each "X is equivalent to Y", checked by assembling both
# spellings and comparing the words.
#
# **IT WAS A CONFIRMED BUG, in the floating-point path.**
# strap/README.md "Next steps" item 5 had this rule recorded as
# implemented for VFL Immediate only and, everywhere else, as
# "untested ... not yet a confirmed bug".  The appendix pins it:
# "SRT(N), 215 is equivalent to SRT(N), 215.0", so a bare integer in
# an FP address is a WORD count.  strap_asm.py called eval_expr,
# which returns a pure BIT count, so it meant three words.  Two of
# the seven pairs failed before the fix (SRT and E-); five already
# passed, which is why nothing had noticed.
#
# THE BLAST RADIUS WAS MEASURED, NOT ASSUMED.  The fix also brings
# the per-term half of C22-6531 p.11's rule to FP addresses, so
# "SYM+5" becomes SYM plus five WORDS rather than five bits.  Every
# one of the 271 decks was assembled and its image hashed before and
# after: all 271 byte-identical, because every one writes dotted
# addresses or bare labels there -- exactly as README item 5 had
# predicted without being able to test it.
#
# TWO KNOWN GAPS, carried as a RATCHET rather than quietly dropped: a
# TRAILING point on a symbolized INTEGER ("M." should be 5.0, "M.M"
# should be 5.5).  Both live in the expression tokenizer that every
# address in the corpus goes through, neither is used by any deck,
# and neither has a witness beyond this appendix.  A pair that starts
# passing is reported as news and fails the script, so the list
# cannot rot.

run "The ADD family's 128-cell sign table (R23-9694 p.107)" ./run_add_family.sh
# >>> THE LARGEST SINGLE ORACLE IN THIS SUITE: 128 CELLS OF IBM'S OWN
# NUMBERS, ALL FOUR ADD OPERATIONS, EVERY SIGN AND MODIFIER. <<<
#
# R23-9694 (7030 CE Introductory Programming, Vol. 2) printed p.107
# tabulates "the storage or accumulator field that is produced by all
# possible combinations of operations, sign modifiers, operand signs,
# and relative magnitudes of operands" -- ADD, ADD TO MAGNITUDE, ADD
# TO MEMORY and ADD MAGNITUDE TO MEMORY, each plain / N / U / U&N,
# against eight (memory, accumulator) sign pairs.
#
# Every operation in it was built in this repository on 2026-10-19,
# and the table passed 128 for 128 on its first run.
#
# TWO INJECTIONS, MEASURED, and they partition the table cleanly:
#   fieldToSM dropping the negative sign modifier on an unsigned
#     field -- the bug Reference Manual Figure 12 caught with ONE
#     cell -- fails 16: rows 3 and 7, the two TO-ACCUMULATOR "U,N"
#     rows.  It cannot reach the to-memory ones, because for those
#     the modifier belongs to the accumulator and never passes
#     through fieldToSM at all.
#   the p.57 to-memory rule removed (bit 52 inverting the ACCUMULATOR
#     sign rather than the storage field's) fails 32: rows 9, 11, 13
#     and 15, every to-memory N row and nothing else.
# The two together are the page's own structure, recovered from the
# model by breaking it in two places.
#
# THE SECOND INJECTION CLOSES A LOOP.  That p.57 rule was written
# earlier the same day with a comment saying it was inert and could
# not be exercised, because nothing could spell the modifier.  The N
# suffix -- C22-6531 footnote 4, witnessed by Reference Manual Figure
# 14 -- made "M+N" and "M+MGN" spellable, and this table now drives
# them.  The table could not have been run a commit earlier.
#
# NOT CHECKED, and the page marks them so it is worth saying: the
# FOUR "*" cells turn on LOST CARRY, and the underlined cells differ
# from the corresponding floating-point operation.  Values only here;
# the lost-carry cells are listed in the generator so the next person
# need not re-read the page.
#
# ("Four", not eight, and this comment said eight for one commit.
# Settled by re-rendering the table body at 300 dpi: the stars fall
# on ADD TO MEMORY, U columns 3 and 7, and ADD TO MEMORY, U,N columns
# 1 and 5 -- 1-based as the page prints them.  The same render
# confirmed all sixteen transcribed rows character by character and
# showed that the UNDERLINES occur only in those same two unsigned
# ADD TO MEMORY rows; the ADD, ADD TO MAGNITUDE and ADD MAGNITUDE TO
# MEMORY blocks carry none.)
#
# The checks are generated from the transcribed table rather than
# written on a command line -- 128 of them would be unreadable, and a
# table is the right place for a table.  See gen_add_family_tb.py.

run "K and a nonzero offset -- the low bits do not participate" ./run_program.sh ../decks/compare_offset.strap StretchKOffTb \
    "PC=2084" \
    "k_low_bits_do_not_participate:1070=0x24" \
    "k_offset_zero:1071=0x24" \
    "k_high_part_higher:1072=0x22" \
    "k_high_part_zero:1073=0x28"
# Reference Manual printed p.65, COMPARE: "The contents of the
# accumulator LEFT OF THE SPECIFIED OFFSET are algebraically compared
# with the addressed operand.  THE BITS TO THE RIGHT OF THE OFFSET DO
# NOT PARTICIPATE IN THE COMPARISON."
#
# The arm shifted the OPERAND left by the offset and compared it
# against the whole accumulator instead.  Same answer whenever the
# accumulator's low `offset` bits are zero; a different one when they
# are not, because those bits then break a tie the page excludes them
# from.  Accumulator 0x101 against an eight-bit 1 at offset 8: the
# manual says equal, the old code said high.
#
# NOTHING IN THIS SUITE CAUGHT IT AND NOTHING COULD.  At offset 0, or
# whenever the high parts already differ, the two readings agree --
# and that covers every K in several hundred listing-verified
# sections.  Blocks 2, 3 and 4 are here to show exactly that: they
# pass both before and after.  The case was untested, not wrong.
#
# THE INJECTION IS THE DECK'S OWN HISTORY.  It was written to fail
# against the model as it stood and did, with T1 = 0x22 and the other
# three passing; the one-line fix turned T1 to 0x24 and moved nothing
# else.  Found while building KF, recorded in docs/NEXT.md rather
# than fixed blind, and then fixed with a deck that failed first.

run "KF, Compare Field -- the bounded accumulator operand, p.65" ./run_program.sh ../decks/compare_field.strap StretchKFTb \
    "PC=2102" \
    "kf_equal:1080=0x24" \
    "kf_acc_lower:1081=0x28" \
    "kf_acc_higher:1082=0x22" \
    "kf_bit_above_field_ignored:1083=0x24" \
    "kf_acc_sign_not_used:1084=0x94" \
    "kf_signed_field_excludes_sign_byte:1085=0x22"
# COMPARE FIELD, Reference Manual printed p.65.  K compares everything
# left of the offset WITH ITS REAL SIGN; KF compares a field "the same
# length in bytes as the field from storage exclusive of the sign
# byte", assumes a POSITIVE sign for it, and -- the page says this
# outright -- gives "no indication ... if there is a one-bit in the
# accumulator to the left of the field".
#
# Blocks 4 and 5 are those two sentences and are why the deck exists;
# the injection that routes KF through K's path moves those two checks
# and no others.  The other four shapes agree between the two
# operations, which is exactly why nothing already in this suite could
# have caught KF being wrong.
#
# EVERY BLOCK ALSO WITNESSES "the arithmetic result indicators are not
# affected", for free and by accident.  The deck stores the whole
# indicator register, and the expected values are not the bare
# comparison bit: each block's LOAD leaves its own RGZ (or RLZ+RN)
# standing through the KF.  The first run expected bare bits and
# reported six failures whose every extra bit was that clause being
# honoured.
#
# ARRIVED VIA MCP, printed p.17 line 30, "KF(BU,48),X IOCD" -- the
# compare that decides whether a card image IS an IOCD card.  One of
# the two operations standing between MCP and knowing what devices it
# has; LCV, the other, needs decimal mode and is still unbuilt
# (docs/boot_plan.md A2).

run "+MG, Add to Magnitude -- Reference Manual Figure 12" ./run_program.sh ../decks/plus_mg.strap StretchPlusMgTb \
    "PC=2086" \
    "pmg_fig12_x_minus_y:1064=70" \
    "pmg_fig12_larger_is_x:1065=100" \
    "pmg_fig12_forced_zero:1066=0" \
    "pmg_fig12_larger_is_y:1067=100" \
    "pmg_sign_byte_unchanged:1068=0x880" \
    "pmg_clamp_clears_entire_acc:1069=0" \
    "pmg_positive_keeps_low_byte:1070=767"
# ADD TO MAGNITUDE, the VFL form (abc100001), the to-accumulator twin
# of M+MG and the last operation the opcode audit still listed in its
# own blind spot.  Reference Manual printed p.60 defines it in three
# sentences -- the accumulator operand is assumed positive, a positive
# result is stored, a NEGATIVE result clears the ENTIRE accumulator,
# and the sign byte register is not changed either way.
#
# BLOCKS 1 AND 2 ARE IBM'S OWN PROGRAM.  Figure 12 on printed p.61,
# "given two 64-bit unsigned binary numbers x and y, put the larger of
# the two in the accumulator": L, then -MG, then +.  Both branches are
# run, because the figure's note 1 ("x-y if x >= y, 0 if x < y") IS
# the operation -- the ordinary sum in one branch and the forced zero
# in the other.
#
# >>> AND FIGURE 12 FOUND A BUG THAT HAD NOTHING TO DO WITH +MG. <<<
#
# The figure would not run: "-MG(BU,64,8),Y,0" computed x PLUS y.
# fieldToSM returned sign 0 for every unsigned field and dropped the
# negative sign modifier entirely, so **every unsigned subtract in the
# model was an addition**.  printed p.60 states the rule under ADD:
# "Unsigned fields are considered positive BEFORE THIS MODIFIER IS
# APPLIED", and p.57's Sign Control table lists "Unsigned, use -" as
# bits 51-52 = 11, a named combination that was unreachable.
#
# MCP RELIES ON IT.  Printed p.18 line 35 is "-(BU,18),$15+.28
# -COMPUTE THE NUMBER OF ...", an unsigned subtract whose answer would
# have been wrong the moment the bootstrap reached that page -- which
# it has not yet, so no existing test could have caught this.  Only
# one deck in the corpus spells an unsigned written-minus at all.
#
# THE ASSEMBLER LEARNED "-MG" FROM THE SAME FIGURE.  It carries a VFL
# data description on a VFL operation, which settles the written-minus
# spelling for VFL rather than only for the floating-point family;
# strap/opcodes.py's VFL_INT_WRITTEN_MINUS cites it and holds "-MG"
# alone.  "M-" and "M-MG" stay out, because nothing spells them.

run "Connective byte size -- the expansion, p.75" ./run_program.sh ../decks/connective_byte_size.strap StretchConnBsTb \
    "PC=2082" \
    "conn_expand_21_3:1052=0x6060204" \
    "conn_expand_offset8:1053=0x606020400" \
    "conn_rest_of_acc_untouched:1054=0xff00000006060204" \
    "conn_cm_contract:1055=3476" \
    "conn_bs8_unchanged:1056=3476" \
    "conn_offset_is_bits:1057=0xc0c0408"
# THE CONNECTIVES ARE NOT A FLAT BIT FIELD, and this arm treated them
# as one until 2026-10-19.  Reference Manual printed p.75, "Byte
# Size": "If the byte size of the storage operand is less than eight,
# each byte is converted into an eight-bit byte before processing by
# the addition of high-order zeros...  Consequently, the result bytes
# always have a byte size of eight", and "the accumulator operand has
# a definite length; it is composed of as many bytes as there are in
# the addressed storage field".  So a 21-bit field at byte size 3 is
# seven bytes and FIFTY-SIX bits of accumulator, not twenty-one.
# CONNECT TO MEMORY contracts back the same way, dropping the
# high-order bits of each result byte.
#
# BYTE SIZE EIGHT IS BIT-IDENTICAL TO WHAT CAME BEFORE, which is why
# the thirty-odd connective sections already in this suite do not
# move: every full byte masks to 0xFF and a short high-order byte
# masks to exactly the bits inside the field length, so the
# participation mask is the old flat `fieldMask`.  The deck checks
# that explicitly (T5), and the bsEff injection leaves T5 and T6
# passing while the other four fail.
#
# T6 RECORDS A HYPOTHESIS THIS SUITE KILLED.  The connective offset
# was built as a BYTE offset, rounded down, on three strands that all
# pointed that way: p.75 ("the field is processed in eight-bit bytes
# starting with the offset"), p.57's exact analogue for decimal ("a
# multiple of four by ignoring the two low-order bits of the
# offset"), and MCP's own "LF(BU,21,3),X ERR AD,1" carrying offset
# ONE while the two M+MG that consume its result carry 8 and 0 --
# which, measured on the bootstrap, is the difference between the
# console printing the error address (0,0,0,6,6,2,4) and printing
# every digit doubled (0,0,0,12,12,4,8).
#
# **FIFTY-SIX SECTIONS FAILED**: all of jb_af1c and the PAU gates,
# because the floating-point diagnostic checks every single result
# with "CT0110(BU,60),ROS,4" -- a connective at OFFSET 4 -- and that
# comparison needs the four bits honoured.  IBM's own diagnostic
# outranks a three-strand reading of the manual.  The offset is bits;
# T6 asserts the doubling, and its injection is the rounding.
#
# So MCP's console address comes out doubled, and that is an open
# question about those four instructions rather than about this one
# line.  docs/NEXT.md carries both measurements.
#
# ARRIVED VIA MCP, like M+1 and M+MG before it, and it is the last of
# the four instructions that build the error routine's console
# message.  With it the bootstrap prints its own error address.

run "MCP's IPL bootstrap, printed p.3, bit-exact (MCP_Mar63 PDF p.10)" python3 verify_mcp_bootstrap_p3.py
# FIND IPL CHANNEL NUMBER, IO TEST, SPACE OVER TAPE MARK -- the page
# that continues p.2 (p.2 ends at 000052.00 with a half word, p.3
# begins at 000052.40) and the page that settles the tape layout:
# the bootstrap record is followed by a TAPE MARK, because line 35
# spaces over one before reading anything else.
#
# EIGHTEEN SYMBOLS AND THIRTY-EIGHT OF THIRTY-NINE MACHINE-CODE ROWS.
# The thirty-ninth, line 6, is a standoff and is named rather than
# bent: the page prints 0011 in bits 24-27 where X22-6533's
# INPUT-OUTPUT OPERATIONS format puts the literal 1000.  The channel
# address and the whole second half-word match this assembler
# exactly, and the byte was re-rendered at 1800 dpi beside line 7's
# 80 to rule out the glyph -- it is a 3.  Line 6 is the only I-O
# instruction in the corpus whose channel operand is a plain literal
# rather than an indexed 0($15); every indexed one prints 8.
#
# TWO THINGS THE PROJECT GAINED, both needed before this would run:
#   - SPFL, the first of C28-6129 Appendix B's I-O FUNCTION
#     pseudo-operations.  It is CONTROL with the code supplied: the
#     page prints 000077 in the code field and .15 = CTLSEOP in bits
#     50-55, and Reference Manual p.132 gives "077 Space File".  Only
#     SPFL is implemented -- for the other nineteen the evidence
#     would be a name resembling a name in another document's table,
#     which rule 4 forbids and which would assemble silently if wrong.
#   - REL with no second operand, which RefMan p.111 licenses
#     ("not used; ignored") and MCP writes three times on pp.3-4.
#
# AND THE B/8 TRAP IN REVERSE, for the third time in this corpus:
# line 10's trailing byte reads 80 at 900 dpi and is B0.  THE
# ARITHMETIC CAUGHT IT BEFORE THE EYE DID -- LVE is 11011 at bits
# 23-27, so bits 24-27 are 1011 and the nibble has to be B.  Decode
# the opcode field first, then look at the glyph.

run "LVS's participation mask, both rows MCP prints (RefMan p.28)" python3 verify_lvs_encoding.py
# THE ONE 7030 INSTRUCTION WHOSE ADDRESS FIELD IS NOT AN ADDRESS.
# Reference Manual printed p.28, "Multiple Indexing": bits 0-15 of
# the address part say which of X0-X15 take part, bit n for Xn; J is
# the destination; there is no I field.
#
# TWO ROWS, NOT ONE, and that is the point of a separate file.  MCP
# printed p.4 line 23 sets bits 12 and 14; printed p.15 line 17 sets
# 11, 12 and 14.  One row pins a mask only at the bits it happens to
# set; two with different sets pin position against register number
# in five places at once.
#
# THE MANUAL CONTRADICTS ITS OWN FIGURE about where the address part
# ends -- the prose says bits 16-19 are ignored, the diagram on the
# same page and X22-6533 both end ADDRESS at 18 and start J at 19.
# The figures win and the discrepancy is recorded in
# verify_lvs_encoding.py; both MCP rows leave 16-18 zero either way.

run "MCP's IPL bootstrap, printed p.4, bit-exact (MCP_Mar63 PDF p.11)" python3 verify_mcp_bootstrap_p4.py
# FETCH PROSA -- the page where the bootstrap stops being about the
# tape and starts being about the program it is loading.  It reads one
# PROSA record against printed p.14's chained control-word table, runs
# it through p.3's IO TEST status loop, takes the record apart with
# four LX/SC pairs, sums two of the counts with LVS, and TRANSMITs the
# MCP IPL down to X BS END -- the bootstrap copying the next stage
# over itself, which is why p.3's SPACE OVER TAPE MARK had to run
# first.  Then it releases the disk and branches to X 10 on printed
# p.15, MCP INITIALIZATION proper.
#
# TWELVE SYMBOLS AND ALL THIRTY-SEVEN MACHINE-CODE ROWS.  Ten
# externals are SYN'd, every one of them from the page that DEFINES
# it rather than from this page's own bytes: pp.2, 3, 5, 13, 14 and
# 15.  A SYN taken from the row that uses it makes that row prove
# nothing.
#
# THE PAGE PROVES THE BLANKS RULE IN IBM's OWN OUTPUT: line 6 writes
# "SIC,XERRAD" and line 8 writes "SIC,X ERR AD", and both print the
# identical 000551.00 80.  Two spellings, one symbol.

run "MCP's IPL bootstrap, printed pp.5-6, bit-exact (MCP_Mar63 PDF pp.12-13)" python3 verify_mcp_bootstrap_p5_p6.py
# THE ERROR ROUTINE -- where every "B,X ERROR" on printed pp.2-4
# lands.  It looks the failing address up in a table, builds a console
# message out of it with LF and two M+MG's, then HUNTS FOR A CONSOLE:
# if the communication region has no console channel it walks all 32
# channels of the basic exchange, issuing a deliberately invalid CTL
# to see which answer, a LOC to see which are tape, and a GONG to find
# the console.  Then it writes the message and rings the gong.
#
# TWO PAGES IN ONE FILE, FOR AN EVIDENCE REASON, not convenience.
# p.5 branches to X 1B ERR and X 1D ERR, which p.6 defines; p.6
# branches to X 1A ERR and X6 ERR, which p.5 defines.  Transcribed
# separately each file would have to SYN the other's labels from the
# very rows under test, and a SYN is an input to a check rather than a
# witness.  Together: fourteen labels placed from the instruction
# stream and all FIFTY-THREE machine-code rows checked.
#
# GONG IS NEW; LF ONLY LOOKED NEW, and the asymmetry is the lesson.
#   GONG went in to SPFL's two-source standard -- RefMan printed p.150
#   gives the IBM 7152 console's whole CONTROL table as 016, 017, 116
#   and "177 Sound Gong", and the listing prints 000177 with .15 =
#   CTLSEOP.  (177 is Backspace File on the 729 IV: same octal,
#   different device, which is what a per-device table means.)
#   LF is the connective C0011, which this assembler has always had.
#   It is absent from X22-6533 page 2's opcode table, so it looked
#   like a missing instruction -- but decoding the word first showed
#   bits 51-59 = 001100111, the card's C with xxxx = 0011, and RefMan
#   printed p.168 puts connectives in a box with no Modifiers footer
#   because bits 51-54 ARE the connective.  The tell was that the
#   decoded "modifier" bits contradicted the written (BU).
#   BEFORE IMPLEMENTING A MNEMONIC, DECODE ONE OF ITS ASSEMBLED WORDS.
#
# AND THE FIRST CROSS-DECK REFERENCE in this corpus: S YCOCH, the
# console's channel number, is defined on printed p.37 under PUNID
# 11C11IPL, where these pages are 11E11BSP.  Separate assemblies,
# which is what TAIL exists to make work.

run "MCP's error messages, printed pp.9-12 (MCP_Mar63 PDF pp.16-19)" python3 verify_mcp_bootstrap_p9_p12.py
# THE AREA CONTAINING ERROR MESSAGES -- thirty-one message blocks,
# thirty-six labels, one hundred and ten printed rows.  Four pages in
# one file because the page breaks fall INSIDE messages: X MS 05B's
# control code is the last row of p.9 and its text the second row of
# p.10.
#
# >>> WHAT A PASS HERE DOES NOT MEAN <<<
# The listing prints NOTHING in the BINARY OUTPUT column for an
# (IQS*)DD row.  No character code is checked and none can be from
# this listing; strap/charsets.py's IQS table rests on Reference
# Manual printed p.166 alone, and says so at length.
#
# WHAT IT DOES MEAN is the COUNTING, checked thirty-one times.  A
# converted DD steps the location counter eight bits per character
# with the end-of-statement character not compiled, so the next
# printed location states exactly how long the message is.  That is
# what fixes the trailing blanks -- " EKJ ON CCW OF IPL CW" has none,
# " CBJ DETECTED IN IO TEST ROUTINE " has one -- which no amount of
# staring at a drum printer would settle.  Injecting ONE extra
# character into the first message moves X MSG 01 from 000260.00 to
# 000261.00 and the check fails, so it is not vacuous.
#
# FOUR THINGS THE ASSEMBLER LEARNED HERE, each forced by a row:
#   - ENTRY MODES.  "(IQS*)DD(BU,64,8), TEXT*" is a prefix in front of
#     the op, its datum is NOT split on commas (MCP writes commas
#     inside one), and blanks in it are characters.  C28-6129 printed
#     p.16: the last character of the prefix is the programmer's
#     END-OF-STATEMENT CHARACTER and "is not compiled" -- so (IQSX)
#     is mode IQS terminated by X, not a fifth mode.
#   - charsets.py, the 48 and 89 Character Sets off Reference Manual
#     printed p.166, read twice independently and agreeing.
#   - Blanks inside a radix literal are GROUPING: the control codes
#     are written "(2)1111 1101".
#   - CNOP pads to the next HALF word with zeros before laying down a
#     NOP.  Printed p.9 line 39's code ends at 000307.20 and line
#     40's NOP prints at 000307.40, which is the only filling that
#     puts the NOP in the second half word.
#
# And listing_oracle gained the 8-bit DD print shape, three octal
# digits, which is a third of the checkable output on these pages.

run "MCP's IPL bootstrap, printed p.13, bit-exact (MCP_Mar63 PDF p.20)" python3 verify_mcp_bootstrap_p13.py
# THE PAGE THAT DEFINES WHAT THE OTHERS HAVE BEEN SYN-ING.  X S ROOF
# and XW SR were SYN'd from here by printed p.2's transcription -- the
# first MCP page this project read -- and X ERR AD by pp.3-6's.  Here
# the assembler places them from the instruction stream instead, which
# is the whole difference between an input to a check and a witness.
#
# X IPL K SETTLES THE TWO-NUMBER QUESTION.  printed p.2's IPL control
# word counts 0o560 = 368 words, X BS END - X IPL BS, the record the
# tape holds.  X IPL K is "1.0 + X BS END - X IPLBS" and comes out
# 000561.00 = 369, one more, including its own control word.  Both
# are right; mcp_tape_manufacture.md 2.1 flagged the reconciliation as
# unsourced and this row is the listing's own arithmetic doing it.
#
# AND THE XW COUNT FIELD IS IN WORDS -- a bug this page caught.  Line
# 35 writes the count as a bare integer, "XW,0.0,29,XW IND", and the
# listing prints 000035.  Line 36 writes the same kind of number in
# word.bit form, "XW,X IPLK+33.0,20.0", and the listing prints 000024.
# The assembler shifted NEITHER, so line 36 came out 0002400, sixty-
# four times too large.  C22-6531 printed p.12's rule had been applied
# to XW's REFILL and to CW's COUNT and not to XW's own COUNT.  THIRD
# INSTANCE OF THE SAME BUG CLASS; no existing program writes a dotted
# XW count, which is why nothing caught it before.

run "MCP's IPL bootstrap, printed p.14, bit-exact (MCP_Mar63 PDF p.21)" python3 verify_mcp_bootstrap_p14.py
# PROSA CWS -- the bootstrap's LAST page, and thirty-nine chained
# control words checked in the four-group form the listing prints
# them in.  Each fetches one PROSA record of 513 words into X BUFER,
# 512 words further along than the one before, chaining by refilling
# from $+1.0.  The thirty-eight chained ones are CW(CDSC) -- C28-6129
# printed p.14's "Count Disregarding Record, Skip and Chain", flags
# 110 -- and the thirty-ninth is CW(CR), flags 000, which is what
# stops the channel.
#
# THE COUNT AND THE ADDRESS CHECK EACH OTHER, thirty-nine times.  The
# statements write ",513," and the listing prints 001001 octal = 513;
# the addresses step 0o1000 words at a time against operands written
# 0, 512., 1024., so the decimal-to-octal conversion is confirmed
# independently on every row.
#
# X BS END IS WHAT printed p.2's IPL CONTROL WORD COUNTS TO.  p.2's
# CW(CR) counts X BS END - X IPL BS = 0o621 - 0o41 = 0o560 = 368
# words, and until now p.2's transcription SYN'd X BS END from this
# page.  Here the assembler places it.
#
# AND A TYPO THAT IS IBM's.  Line 22's comment reads "-FETCH ONE
# PROSA REXORD" -- X, not C -- where thirty-eight others say RECORD.
# Verified at 600 dpi.  It compiles to nothing and it is the proof
# that these rows were keyed by hand rather than generated.

run "MCP INITIALIZATION, printed p.15, bit-exact (MCP_Mar63 PDF p.22)" python3 verify_mcp_bootstrap_p15.py
# THE PAGE THE BOOTSTRAP BRANCHES TO.  printed p.14's last
# instruction is "B,X 10"; X 10 is line 17 of this page, at
# 000622.00.  Seventeen rows, all seventeen first attempt.
#
# It does NOT make the boot run further, and that is worth being
# plain about: the page ends in "LOC(SEOP),0.0,0.0 -POSITION TO ARC
# ZERO" and a three-test disk check (EKJ, UNRJ, CBJ).  Transcribing
# it turns "halts at PC 0, one word past X BS END" into "stops at a
# LOCATE, wanting a 7612/353".  What it buys is the knowledge of
# exactly which device answers next and what it is asked.
#
# THE INDICATOR ENCODING CHECKS ITSELF THREE WAYS.  Lines 29, 31 and
# 33 print 000133.03 46, 000133.03 C6 and 000133.04 46; reading bits
# 19-24 as the indicator number gives 6, 7 and 8 -- EKJ, UNRJ, CBJ --
# which is exactly what the row comments say, and the branch address
# in all three is X ERROR = 000133.00, known from printed p.5.
#
# TWO SYMBOLS ARE WEAKER EVIDENCE THAN THE REST and the deck says so:
# S MCP and S ROOF are communication-region symbols read off this
# page's own binary output, because the page defining them has not
# been transcribed.

run "MCP INITIALIZATION, printed p.16, bit-exact (MCP_Mar63 PDF p.23)" python3 verify_mcp_bootstrap_p16.py
# "WRITE PROSA ON DISK AND FETCH FROM MCPS TAPE" -- thirty-one rows,
# every one with binary output, all thirty-one first attempt.
#
# Line 11's comment is the one to read: "-ASSEMBLED CW".  The control
# word the write uses is BUILT AT RUN TIME -- SX stores a computed
# length into X PRO WR and the W names X PRO WR as its control word.
# A disk model has to answer a control word the program wrote, not
# one the assembler laid down.
#
# FOUR EXTERNALS COME FROM PAGES READ MONTHS APART and all four are
# branch targets, so a wrong value would print a wrong address: X9 A
# and X9 A 3A from printed p.4, X7 1 and X7 3 from printed p.3.

run "MCP INITIALIZATION, printed p.17, bit-exact (MCP_Mar63 PDF p.24)" python3 verify_mcp_bootstrap_p17.py
# "PROCESS IOCD CARDS SETTING UP CST AND LST" -- forty-two rows, and
# THIS IS WHERE MCP LEARNS WHAT MACHINE IT IS ON.  It does not know
# its own configuration; it reads one IOCD card per unit, converts
# the channel number out of Hollerith with two CT0011s and an LCV,
# looks the two-letter equipment code up in X EQP T, and fills in the
# channel and unit status tables.  So "which devices must the model
# present" is answered by the IOCD deck, not by the model -- which is
# what makes strap/cards.py part of booting MCP and not only part of
# running diagnostics.
#
# The densest VFL of any MCP page so far: three connectives in their
# indexed progressive form, two CM1111 and a CM0000 against single
# bits, an LCV with a (DU,8,4) radix conversion, and a load with a
# NEGATIVE offset whose address field prints 777777.73.
#
# ONE GLYPH CORRECTION, AND THE 8/B HAZARD'S THIRD OUTING.  Line 42,
# "V+,$3,$5", prints 000025.06 B0.  It read as 80 at 200 dpi AND
# AGAIN at 900 dpi, in a column where nearly every neighbour really
# is 80.  THE ASSEMBLER DISAGREEING IS WHAT CAUGHT IT; 1800 dpi then
# settled it.  First time a higher-resolution render was already in
# hand and the eye still supplied the expected glyph.

run "MCP INITIALIZATION, printed p.18, bit-exact (MCP_Mar63 PDF p.25)" python3 verify_mcp_bootstrap_p18.py
# The UNIT STATUS TABLE half of printed p.17's IOCD processing:
# twenty-eight rows, up to eight units per channel.
#
# THE PAGE FOUND AN ASSEMBLER GAP, which is why it is worth a section
# of its own rather than a line in the previous one.  Line 34 is
# "LFI(BU,18),8.0", the first LFI in this corpus.  LF is the
# connective C0011; C22-6531 Appendix A printed p.58 FOOTNOTE 10 --
# the one C, CM and CT carry -- ends "This operation code is also
# subject to Footnote 3", and footnote 3 is the "I" suffix for
# immediate addressing.  strap_asm.py stripped that suffix only for
# VFL_INT_CODES, so LFI raised a KeyError.
#
# AND THE FIX WAS NOT THE OBVIOUS ONE.  Stripping the suffix alone
# still gave the wrong word, because a VFL-immediate operand written
# as a BIT ADDRESS was being evaluated as a raw bit count.  Reference
# Manual p.56 says the operand is the LEFTMOST `length` bits of the
# effective address, so one unit of the operand is 2**(24-length) in
# A24 -- "8.0" means 8, packs to 8<<6 = 512, and prints 000010.00,
# which is what the page prints.  Evaluated as 512 it would pack to
# 32768 and print 002000.00.  The page settles it twice over: line 35
# subtracts the units remaining from that value and line 37 stores
# the difference in FOUR bits, which 512 would not fit.
#
# C22-6578 Problem 2.2 Method 2's "LI(BU,7), 127" is unchanged --
# a plain integer passes through eval_addr_field untouched -- and
# both Problem 2.2 sections and the VFL-format DF section were
# re-run against the change before it landed.
#
# docs/c22_6531_appendix_a.md records the appendix, its page offset
# and the one place it is incomplete.

run "MCP's error table, printed pp.7-8 (MCP_Mar63 PDF pp.14-15)" python3 verify_mcp_bootstrap_p7_p8.py
# X ERR DD -- THE LAST TWO PAGES OF THE BOOTSTRAP TO BE TRANSCRIBED,
# and the index to all the rest: seventy-eight VF half words, one pair
# per error code, holding the address of the site that failed and the
# address of the message to print for it.  printed p.5's
# "X ERR SH KV,$1,0.0($2)" is the loop that scans it.
#
# THE TABLE CHECKS ITS OWN LENGTH.  printed p.8 line 31 is
# "X E DD K SYN,$-X ERR DD -SIZE OF ERROR TABLE" and the listing
# prints 000047.00+ -- thirty-nine words, which is what seventy-eight
# half words occupy and what thirty-nine distinct error codes need.
# The table's extent was never assumed.
#
# AND THE TWO TRANSCRIPTIONS CROSS-CHECK.  The thirty-nine message
# labels are SYN'd here but PLACED by mcp_bootstrap_p9_p12.strap and
# _p13.strap from their own instruction streams, and the verifier
# asserts the two agree before checking a single row.  IT EARNED ITS
# KEEP IMMEDIATELY: the first run failed on X MSG 25, because the
# generator that wrote these SYNs had converted the bit part of
# 000513.30 out of octal.  Three statements -- the page's printed VF,
# the SYN, and the other program's placement -- now have to coincide.
#
# THREE THINGS THE TABLE SAYS ABOUT MCP:
#   - EIGHT ENTRIES SHARE FIVE MESSAGES.  000432.00 appears four
#     times under four different descriptive comments.  Several
#     distinct failures deliberately print the same text.
#   - THE TABLE IS NOT IN ERROR-CODE ORDER (the code-10 pair sits
#     between 05E and 06), which rules out indexing by code and fits
#     X ERR IN being a SEARCH word scanned by p.5's KV loop.
#   - X ERR 20 AND X ERR 21 ARE "BD,$", NOT "SIC,X ERR AD".  Their
#     messages are "NO CONSOLE DEFINED" and "NO CONSOLE AVAILABLE":
#     with no console there is nothing to print to, so there is
#     nothing to store an address for.  They just halt.
#
# WHAT THE ASSEMBLER LEARNED HERE: DR (Data Reservation, which emits
# nothing and whose width is checked by what follows it), and that a
# BARE "CW" with no secondary is legal and means all three flags zero
# -- printed p.8 writes it twice and both print 000.
# AND ONE SUBSTITUTION: line 34's "X MSG CW(.25)1" is a BIT
# DESIGNATION, set bit 25, which is the chain flag; written CW(CCR)
# here, which C28-6129 printed p.14 defines as the same three bits.
# Inventing the general semantics of bit designations from one row is
# what rule 4 forbids; the checked row proves the substitution.

run "The STRETCH MAINTENANCE COMPOOL, 65 symbols (ka_ua1 PDF pp.129-130)" python3 verify_dcp_compool.py
# THE ROSETTA STONE, and the first piece of the Diagnostic Control
# Program transcribed.  docs/archival_inventory.md: "the single
# highest-leverage page in the whole find... resolves symbols
# referenced by EVERY OTHER 7030 diagnostic deck in bitsavers' diag/
# directory... without it, every other listing's symbols are
# dangling."  51 entries on PDF p.129, 14 on p.130.
#
# NOT A rule-3 CHECK, and the file says so.  A SYN emits no code, so
# there is no machine-code column to compare.  What the page does
# print on every row is the RESOLVED ADDRESS, so the oracle is the
# assembler's symbol table against that column: 55 genuine checks and
# 10 circular, the circular ones being rows with no offset of their
# own whose base this transcription back-computed.
#
# THE OPERATOR PRINTS AS "&" AND IT IS ADDITION, settled by arithmetic
# rather than by looking at the glyph -- which at 600 dpi is
# unmistakably an ampersand and unmistakably not a plus.  41 of 41
# offset rows resolve correctly under "addition, decimal offset, octal
# address", and the decisive row is MNTCTL, which prints NO operator
# glyph at all and still sums.  p.130 confirms the convention
# independently: its address column runs 7 -> 10 with no 8 or 9.
#
# "ETAP7" IS AS PRINTED -- IBM's own typo between EQTAP6 and EQTAP8,
# confirmed at 600 dpi off a rule line.  Third deck typo this corpus
# preserves, beside "PSEDUO" and "COUSE".

run "I-Box 5 routine 1260's TS block, bit-exact (jb_ax5b p.41)" python3 verify_ax5b_16071_listing.py
# THE INTERVAL TIMER GETS A SECOND DECK ORACLE, eight rows long.
# Reference Manual p.44: "4. Time Signal (TS).  The interval timer has
# become zero."  I6071 loads the timer with the value ONE, spins 512
# times on a COUNT AND BRANCH to itself, then asks BTS whether TS came
# on; failing that it reports "UNABLE TO TURN TS ON."
#
# EVERY STEP OF THAT IS PRINTED SOMEWHERE, none of it read off a
# symbol's name.  PDF p.114, "-COMMON CONSTANTS FOR FETCH ONLY",
# prints the BIT table: BIT<n> is the word whose only set bit is bit
# n, one word per bit from BIT0 at 024522.00, and BIT18's own row
# ("XW,(8).40,0,0" -> "0.40 00 000000.00 00") has bit 18 set.  The
# pocket card X22-6533-1 (docs/microarchitecture_plan.md A.10) puts
# the interval timer at word 1 bits 0-18, so bit 18 is its low-order
# bit -- the value one -- and the card's footnote (a) says that
# register is "read-only except for store-value/count/refill/address",
# which is why the deck reaches it with SV and not a general store.
#
# WHAT THE ROWS DO NOT SHOW: the system must be DISABLED here.  Word 1
# is permanently protected (p.31) and p.45 raises DS and suppresses
# the store when such a reference happens "while the interruption
# system was enabled".  Entailed by two manual pages, not transcribed
# from this one.  Note the symmetry with I6086, which uses the SAME
# instruction on the SAME word as its DS provocation, enabled,
# expecting suppression -- the two blocks are storage_protection.
# strap's two directions, written by IBM.
#
# docs/NEXT.md §5 defers "the interval timer actually ticking" and
# names routine 1258 as the oracle for it.  This is a much smaller
# second one, inside a routine already being transcribed, and it is in
# place BEFORE the timer is implemented -- which is the order
# docs/NEXT.md item 2 asks for: let the oracle shape the
# implementation rather than retrofitting it.
#
# THREE ENCODINGS.  BTS "21400.42 42" is indicator 4, a fourth widely-
# spaced number through the field that straddles the printed octal/hex
# boundary (BOP 15, BAD 16, BDS 19, BADZ 16 are the others).  LCI
# "1000.11 02" is 512 as an 18-bit COUNT in the top 18 bits of the
# 19-bit field rather than an address -- strap/README.md's Gotchas item
# 16 records that field being encoded wrongly once, and this is a
# second independent witness.  CB "16010.50 48" is a count-and-branch
# to ITSELF, and "$" is this block's only operand that is not an
# external symbol, so it is its only real address check.
#
# A LESSON RECORDED IN THE VERIFY SCRIPT.  Two of that file's three
# injection results were written down as PREDICTIONS before being run,
# and both were wrong: TS 4->5 moves the HEX byte and not the octal
# pair (4 and 5 differ only in the bit that lands at 24), and breaking
# enc_branch_or_misc fails NOTHING here because a count-and-branch has
# its own encoder.  The header now carries what the injections
# actually did, with the wrong predictions beside them.

run "The interval timer and the time clock step (Ref. Man. printed pp.34-35)" ./run_program.sh ../decks/interval_timer_steps.strap StretchIntervalTimerTb \
    "timer_decrement:2628=0x400000000000" \
    "timer_reload:2629=0xffffe00000000000" \
    "timer_unused_bits_cleared:2630=0x400000000000" \
    "PC=5179" \
    "CYCLES<=19000"
# THE FIRST RUNNABLE TEST OF THE OSCILLATOR, and it makes the deck
# oracle above executable rather than merely transcribed.  Both
# counters live in word 1 and are driven by ONE 1,024 c/s source
# (printed p.34, p.35, both read first-hand and quoted in the
# program's header): the interval timer in bits 0-18 steps DOWN, the
# time clock in bits 28-63 steps UP, bits 19-27 are unused and are
# cleared by the first step-down.
#
# THE RELOAD NEEDS NO SPECIAL CASE, which is the finding.  p.34
# describes the step off zero as a reload -- "sets the timer to all
# ones" -- but 0 - 1 mod 2**19 IS all ones, so a plain modular
# decrement realises the printed rule exactly, including the "unless
# the program in the meantime has changed its contents" clause.  The
# deck agrees bit-for-bit (1258 TEST 2, 0 -> 777777.40).  NEXT.md's
# feared "a naive wrap fires TS every 3255 clocks" never had a way in;
# the only thing that can go wrong is testing the NEW value instead of
# the old, which injection I3 catches.
#
# THE TICK RATE IS AN EXACT RATIONAL AND IS NOT ROUNDED.
# (1/1024)s / 0.3us = 78125/24, so 24 ticks are exactly 78,125 model
# clocks: 19 intervals of 3255 and 5 of 3256, no long-run drift.
# Rounding to 3255 would run ~64 ppm fast with unbounded accumulated
# error -- invisible now, unattributable during cycle-accuracy work.
# The +-1 jitter is the honest part, not a compromise: p.34 calls the
# source "a stable oscillator" with no stated relation to the 0.3 us
# machine cycle, so a fixed integer period would be the artefact.
#
# SIX BLOCKS, each failing to its own self-branch so the halt PC names
# the failure: steps down by one; the reload; bits 19-23 cleared; a
# BTS asserting TS is STILL OFF (the discriminator for the edge, since
# block 4 cannot tell old==1 from new==0); TS fires on 1->0; the clock
# steps UP by one; and a store into word 1 that must not reach the
# clock.  That last block exists because injection I8 would otherwise
# have been a null -- a clobbered clock just restarts from zero and
# still steps by one.
#
# THE HALT IDIOM IS "B,$", NOT THE HOUSE "BEW,$", and that is
# deliberate: BEW enables the system, TS is on by then, mask bits 0-19
# are permanently one, so a BEW would take a TS interruption into a
# table this program does not have.  Do not "fix" it.
#
# EIGHT INJECTIONS, ALL OBSERVED, NO NULLS; all six CYCLES<= benches
# are unchanged, including StretchIboxSpanTb at 4003 clocks, the only
# one long enough to cross a pulse.  A scan of all 194 run_program.sh
# benches found exactly two that reference storage word 1 --
# ex_monitor.strap and ibox4_prog_ix_v.strap -- and both pass.
#
# UNTESTED, and said here rather than left to be discovered: bit 24 of
# the timer field (STRAP's word.bit notation stops at 23, so this
# tests 19-23, the same five the deck tests); the AD indicator for a
# store into word 1's right half (the suppression is modelled, the
# alarm is not); and TS OR-ed over a same-clock clear, which has no
# deck witness.

run "I-Box 5 routine 1260's OP and AD blocks, bit-exact (jb_ax5b pp.41-42)" python3 verify_ax5b_16082_16083_listing.py
# TWO MORE BLOCKS FROM THE SAME ROUTINE, and they exist for one row
# pair.  I6082 and I6083 are contiguous (017225.00-017234.40) and both
# branch to the SAME target through DIFFERENT indicator numbers:
#
#     BOP,I6088   21400.47 C2      indicator 15
#     BAD,I6088   21400.50 42      indicator 16
#
# WHY THAT PAIR IS WORTH A FILE.  enc_branch_ind puts the 6-bit
# indicator number at bits 19-24, and the listing prints bits 18-23 as
# an octal pair and 24-31 as hex -- so the number STRADDLES the two
# printed fields, five bits in one and one in the other.  Two rows with
# the same address and adjacent numbers differ in BOTH fields at once.
# The injection proves the point: moving OP from 15 to 14 leaves the
# octal pair at .47 untouched and shows up ONLY in the hex byte, which
# a check reading one field would have missed.  The I6086 block's
# BDS/BADZ (19 and 16) never exercised a number whose top bit differs.
#
# A THIRD AND FOURTH WITNESS FOR I6088 AT 021400.40, and this time from
# pp.41-42 rather than pp.43-45.  Both rows carry bit 18 of the target
# set.  The address a 200 dpi render got wrong is now agreed on by two
# pages and three encodings -- but note the provenance: I6088's .40 is
# a SYN, an INPUT to the check, so the PASS is not the witness.  The
# witness is the printed code, ".47" = 100111 and ".50" = 101000, read
# at 600 dpi.  The rows add that the assembler places bit 18 where the
# listing does.
#
# AND ONE HONEST NEGATIVE, recorded in the verify script rather than
# quietly dropped: breaking CNOP's full-word alignment fails NOTHING
# here, because at 017227.00 the counter is already word-aligned and
# this block's CNOP emits nothing either way.  This file does not
# witness CNOP; verify_ibox1_ensu_listing.py does, where the CNOP lands
# on an odd half-word.
#
# WHAT THIS IS NOT.  An ENCODING oracle again.  Neither block can run:
# both fall through into the SEN/SERS error harness and I6093, none of
# it transcribed, and I60K7's contents are not printed on these pages.
# The block's SHAPE -- store a word over a zeroed full-word slot, two
# NOPs, then fall straight INTO the slot -- reads like self-modifying
# code planting an invalid operation code, which is what "-OP" and
# "UNABLE TO TURN OP ON." would need; that is inference and the
# program's header says so.

run "The interruption mechanism (fire, one instruction, return)" ./run_program.sh ../decks/interrupt_pg0.strap StretchIntPg0Tb \
    "PC=4289" "MARK:2240=0x8000000000000000" "MARK2:2241=0x8000000000000000" \
    "ORDER:2242=0x8000000000000000"
    # 004140.40; hand-written, not a listing fact
# THE INTERRUPTION ITSELF.  p.48: "interruption requires the mask bit
# to be 1, the indicator bit to be 1, and the mechanism to be enabled",
# and then "a mechanism develops the number of the leftmost actuated
# indicator whose mask bit is one.  After this leftmost indicator has
# been turned off, the developed number is added to the contents of the
# interruption address register to form the effective interruption
# address.  This address does not replace the contents of the
# instruction counter but is used to fetch a single instruction."
#
# WHY PG0 AND PG2.  p.46: "Program Indicators Zero through Six
# (PG0-PG6).  These indicators are set by programming only."  41-47 sit
# inside the settable mask range, so the provocation needs no
# arithmetic fault and no I/O -- and both writes are sanctioned in
# terms: p.48 says mask bits 12.20-12.47 "can be set or changed by ...
# BRANCH ON BIT", and p.41 lets BRANCH ON BIT reach indicator bits
# 20-63.  Both of those paths were already tested here before this
# program used them.
#
# THE UNITS ARE WORDS.  p.48: "a table of 48 successive FULL-WORD
# locations", and the interruption address register "contains 18 bits
# and has address 2.0".  HWRONG is planted at exactly the address
# half-word indexing would reach instead, so the two readings cannot
# both pass.
#
# AND THE DECK AGREES, checked because a scouting pass suggested it
# might not.  jb_ax5b PDF p.86 declares the interruption table
# "I60IT  DR%BU,64,8@,64" at 023201.00 with the next symbol I60DMP at
# 023301.00 -- a gap of octal 100, exactly 64 WORDS, holding the 48
# maskable indicators with room over.  The three consecutive HALF-words
# at I6090 (p.48, "HI,BEFORE / OK, AT / LO,AFTER ... INTRPTS ENTER
# HERE") that looked like half-word slots are a TEMPLATE copied into
# those word slots -- p.86 has "I60K6  BD,I6090" as a single half-word
# at 023047.00.  See docs/NEXT.md for the full reasoning.
#
# Ten injections; every address reproducible with
#   python3 line_addresses.py ../decks/interrupt_pg0.strap
#
#   mechanism never fires        -> 004110.00  BZB, MARK, $   (the routine
#                                              never ran)
#   enable bit ignored           -> 004105.40  BZB, $PG0, $   (it fired in
#                                              the DISABLED phase and cleared PG0)
#   EIA in half-words, not words -> 004424.40  HWRONG
#   EIA one word low             -> 004450.00  E40
#   EIA one word high            -> 004452.00  E42
#   mask ignored                 -> 004122.00  BZB, $PG0, $   (unmasked PG0
#                                              was taken and cleared)
#   counter never replaced by a  -> 004126.00  NORET
#     successful branch
#   counter always replaced,     -> 004452.00  E42
#     even on fall-through
#   rightmost masked indicator   -> 004135.40  WRONG
#     instead of leftmost
#
# THOSE LAST TWO ARE WHY BOTH ARMS NEED THEIR OWN WITNESS.  p.48 says
# the instruction counter "is stepped neither before nor during" the
# interruption instruction, "however, [it] can be replaced as the
# result of a successful branching operation" -- two rules in one
# sentence, and a model can get either one right while getting the
# other wrong.  Never replacing passes both fall-through blocks and
# strands the branching one at NORET.  ALWAYS replacing passes the
# branching block and sends the fall-through blocks to the NEXT table
# slot, E42.  Block 3 exists because writing the summary of blocks 1
# and 2 made it plain neither could see the branch clause.
#   indicator not turned off     -> step cap, and p.48 says why: "if the
#     interruption instruction does not disable the system ... another
#     succeeding interruption will be caused by the new leftmost
#     selected indicator before the execution of an instruction
#     addressed by the instruction counter."  The model loops exactly as
#     described, so there is no address to name -- the halt is the
#     manual's own prediction, not a missing check.
#
# THE MASK BLOCK IS HERE BECAUSE THE FIRST BLOCK COULD NOT SEE THE MASK.
# With only block 1, replacing "indicators & mask" with "indicators"
# passed everything: the sole indicator turned on was also the one
# masked, so both rules give the same answer.  A SURVIVING injection is
# the "green test is only evidence about faults its inputs could have
# made visible" rule landing on this file.  Block 2 leaves PG0 actuated
# and UNMASKED beside a masked PG2, so ignoring the mask takes the
# wrong -- further left -- indicator and clears it.
#
# IMPLEMENTED 2026-09-25, where this used to read "NOT IMPLEMENTED".
# The interruption was taken at a QUIESCENT boundary (look-ahead empty,
# E-box idle) rather than p.48's instruction boundary -- LATER, never
# earlier.  Measured at THREE instructions of lateness where p.48 allows
# zero, and fixed by dropping one term from armInterrupt; see the
# "Interruption timing" section for the sweep.  An E-box-class interruption
# instruction fails loud rather than stepping the counter.
#
# LEFTMOST PRIORITY IS BLOCK 4, and it was added because blocks 1-3
# could not see it: each actuates exactly ONE masked indicator, so a
# model choosing the RIGHTMOST masked one passed all of them.  Block 4
# actuates PG4 (45) and PG5 (46) while PG0 (41) is still on and still
# UNMASKED from block 2, so three different wrong rules give three
# different answers -- ignore the mask and 41 is chosen, take the
# rightmost and 46 is, take the leftmost masked and 45 is.
#
# The ORDER is observed without any instruction that can report two
# things at once: PG4's routine SETS a bit and falls through, PG5's
# BRANCHES on that same bit, so the branch is taken exactly when PG4
# went first -- and that branch is also what moves the counter off
# WRONG, which hangs.  It witnesses three rules together: leftmost
# rather than rightmost; only THAT indicator turned off, since PG5 must
# still be actuated to cause the second interruption; and the second
# interruption arriving before the counter's own next instruction, which
# is p.48's programming note in one block.

run "SSIP SIP16/SIP17 reset blocks (ja_ua1_ssip, encoding)" python3 verify_ssip_sip17_listing.py
# FIRST TRANSCRIPTION FROM ja_ua1_ssip, the System Test Program's
# supervisor.  Its listing is PDF pp.7-52, 1-up fanfold with NO printed
# page numbers, so it is cited by PDF page -- unlike every other tape
# here.  (archival_inventory.md implies this tape is prose only; it is
# not, and that note needs correcting.)
#
# SIP17 walks indicators 0 through 19 IN NUMERIC ORDER, one
# branch-on-indicator-and-clear each, then sweeps the rest with a single
# SX into word 11.  That makes it a self-checking table of two things at
# once -- the indicator NUMBERING for bits 0-19 and the
# branch-on-indicator ENCODING rule -- so an error anywhere in that
# range shows as exactly one row's mismatch.  Twenty independent checks
# in twenty-two half-words, all green on the first assembly.
#
# IT NAMES THE INDICATORS NOTHING ELSE REACHES.  OP (15), AD (16), USA
# (17), EXE (18), DS (19) are the instruction-exception group;
# op_ad_indicators.strap pins OP and AD by hand FROM THE MANUAL, and
# this is a DECK naming all five.
#
# TWO THINGS THE LISTING SETTLES INDEPENDENTLY.
#   * SLOT 14 IS NOT AN INDICATOR.  Every other row is a
#     branch-on-indicator; 001601.00 is a plain "B,$.32", stepping over
#     bit 14 because there is nothing there to test.  INDICATOR_BITS has
#     always had a gap at 14 -- this is a second witness to it, from a
#     programmer who had the machine.
#   * THE DECKS SPELL INDICATOR 5 "CPU".  The Reference Manual's Figure
#     11 calls it "CPU Signal (CPUS)" and this project took CPUS from
#     there; SSIP writes BCPUZ.  Both are now in INDICATOR_BITS as an
#     alias.
#
# SIP16, the block above it, is transcribed too, and it is the one that
# matters for the interrupt system: it resets the system's OWN control
# state -- word 1 (interval timer), word 2 (interruption address), word
# 3 (boundary registers) and word 12 (mask).  Words 1, 2 and 3 are the
# PERMANENTLY PROTECTED area (p.31), and a BD guarded the sequence,
# commented "DISABLE BEFORE RESET OF PROTECTED AREA".  That is the
# deck's own witness for what p.45 states -- DS/DF/IF are raised only
# "while the interruption system was enabled" -- and when protection is
# implemented here this block is the natural test: it must succeed
# disabled and be suppressed enabled.
#
# A LABEL ERROR THIS FOUND, in my own earlier transcription: SIP17
# labels the BXVLZ at 001571.00, not the BMKZ chain at 001572.00.  The
# verify script could not have caught it -- it checks the address a
# symbol resolves to, and a symbol on the wrong row still resolves to
# something.  Reading further up the page for the next block is what
# caught it.
#
# Encoding-only, deliberately: the block ends by branching to an
# external return, so running it needs a harness this does not have.
# The listing oracle is the strongest encoding check in the project and
# stands on its own.

run "Indicator coverage audit (ratchet)" python3 audit_indicator_coverage.py
run "Opcode coverage audit (ratchet)" python3 audit_opcode_coverage.py
# The same question one level up: not which INDICATORS nothing looks at,
# but which OPERATIONS nothing exercises.  Also a ratchet.
#
# IT EARNED ITS KEEP ON THE FIRST RUN.  It found BR -- BRANCH RELATIVE
# -- listed in bsv/README.md among the implemented unconditional
# branches and implemented by the model as an ABSOLUTE branch identical
# to B.  Two primary sources say otherwise: the X22-6533 pocket card
# gives B = 010000000 and BR = 011000000, a DIFFERENT operation code
# named "Branch Relative"; and Reference Manual p.42 says "a simple
# storage of the instruction counter without branching action is
# accomplished by STORE INSTRUCTION COUNTER IF BRANCH RELATIVE with a
# branch address of 0" -- an address of 0 producing NO BRANCHING ACTION
# only works if it is a displacement.  The old absolute reading would
# have branched to 0.0, which p.39 separately calls an invalid
# branching address, so it was wrong twice over.
#
# BR was first made to set OP instead of branching wrongly, because the
# base, sign and units were not established by anything read at the
# time -- implementing it then would have been a guess dressed as a
# fix.  A later research pass found p.40, which states all three, and
# it is now implemented from that source; see br_relative below.  The
# refusal to guess cost one commit and bought a correct
# implementation.
#
# Of the 22 unused mnemonics, 15 are documented scope limits that reach
# setOpInvalid -- only five VFL integer arms exist (L, ST, +, M+, K),
# which accounts for the ten compare/convert codes.  The other SEVEN
# are implemented and simply undriven, and that is the actionable list:
# BZB1/BZBN/BZBZ (branch-if-off with set-one / invert / set-zero) and
# the four I/O Suppress-End-Of-Op forms.

run "TRANSMIT: what is honoured, and what is refused out loud" ./run_program.sh ../decks/transmit_scope.strap StretchTransmitScopeTb \
    "PC=4246" "SRC:2176=0x9249249249249249" \
    "DST1:2240=0x9249249249249249" "DST2:2248=0" \
    "DST3a:2256=0x9249249249249249" "DST3b:2257=0x9249249249249249" \
    "DST4a:2304=0x9249249249249249" "DST4z:2319=0x9249249249249249" \
    "DST5:2368=0x9249249249249249" "DST6:2376=0"
# THREE OF THE SIX BLOCKS FLIPPED ON 2026-10-18, from "refused" to
# "happens", because multi-word and direct-count TRANSMIT are built.
# DST3, DST4 and DST5 used to be asserted ZERO and are now asserted to
# have RECEIVED -- DST3 both of its two words, DST4 its first and its
# SIXTEENTH (p.30: "a zero count field indicates the maximum count of
# 16 full words"), DST5 by the direct-count path with index 1's count
# loaded first.  decks/transmit_multiword.strap is the deck that pins
# the new behaviour in detail; this one keeps its original job, the
# SCOPE, one block per rule.
#
# DST2 AND DST6 ARE STILL ZERO, and that is what the file is for now:
# SWAP in either direction and BACKWARD transmission are still refused
# out loud.
    # 004114.00; hand-written from Ref. Manual pp.30-31 and the card
# A CLAIM IN bsv/README.md THAT WAS TWO-THIRDS FALSE, found 2026-09-22.
# Its "decoded but not executed (sets indicator 15, OP, and no-ops)"
# list has always named "Transmit backward/SWAP/multi-word".  Only
# BACKWARD was true:
#
#   * StretchDecode matched sub-ops 010 (Transmit) and 110 (Swap) in
#     ONE condition and recorded NEITHER -- StretchTypes' Transmit
#     struct had no `swap` field -- so a forward SWAP arrived at the
#     execute stage indistinguishable from a Transmit and was executed
#     as one;
#   * the execute arm moves one word and never read the count, so any
#     multi-word Transmit moved one word.
#
# Both SILENT: no indicator, no failure, a wrong store.  DEMONSTRATED
# before fixing: "SWAPI,1,SRC,DST" left SRC alone and copied it into
# DST (0x9249249249249249) with OP clear.
#
# WHY IT COULD STAY FALSE.  Neither was reachable from STRAP -- this
# assembler could not encode Transmit at all until TRANSMIT_CODES
# landed the same day, for jb_ax5b p.45.  A README claim that nothing
# can express is a claim nothing can break, which is this project's
# own corollary applied to prose instead of a test.
#
# THE FIX reads bit 57 (Ref. Manual pp.30-31: "modifier bits 55-57 ...
# 57 = bidirectional (swap)", agreeing with the card's ab010/ab110)
# and gates on a count it can honour.  pp.30-31 also give the count:
# index J bits 28-45, 0 meaning 2^18; or immediate, bits 51-54, where
# **0 MEANS SIXTEEN**.  So "one word" is exactly immCount=1 and j=1 --
# a "j==0 means none" reading would let a sixteen-word transmit pass.
# A DIRECT count lives in a register this arm never reads, so every
# direct count is refused: conservative by construction, refusing a
# direct count of one it would have executed correctly rather than
# executing a direct count of n as one word.
#
# FIVE INJECTIONS, each naming one block, each observed -- and the
# program hangs at the FIRST failing block, so every rule needed its
# own injection rather than one that breaks three:
#   decoder stops capturing bit 57  -> 004102.40  (SWAPI moved a word)
#   count check removed             -> 004104.40  (TI,2 moved a word)
#   j == 1 relaxed to j <= 1        -> 004106.40  (TI,0 = SIXTEEN)
#   immediate modifier ignored      -> 004110.40  (T,1 direct count)
#   backward check removed          -> 004112.40  (TBI moved a word)
#
# THREE OF THOSE FIVE NO LONGER DESCRIBE A LIVE RULE, 2026-10-18, and
# saying so is better than quietly deleting them: the count check, the
# "j == 1" test and the immediate-modifier test were the machinery of
# a refusal that no longer exists.  What guards those three blocks now
# is the opposite assertion -- the destination words must have
# RECEIVED, and for block 4 the sixteenth of them -- plus
# decks/transmit_multiword.strap's fifteen checks.  The two injections
# that still bite, SWAP and backward, are the two blocks still
# asserting a refusal.
#
# THE SURVIVOR THAT TAUGHT THE MOST.  Block 6 was first written TB --
# backward with a DIRECT count -- and removing the backward check
# changed NOTHING, because the count rule refuses every direct count
# anyway.  The block could not witness the rule it was written to
# guard.  TBI (backward, immediate count one) makes oneWordForward
# TRUE, so only the backward check can refuse it, and the injection
# then bites.
#
# AND BLOCK 1 IS WHAT KEEPS THE FIX HONEST: TI with an immediate count
# of one must STILL STORE.  DST1 is checked in every run above and
# passes under all five injections, so "OP on everything" is excluded.
# It is also the shape jb_ax5b p.45 actually uses.

run "BR (Branch Relative)" ./run_program.sh ../decks/br_relative.strap StretchBrRelTb \
    "PC=4103"          # 004003.40; hand-written, not a listing fact
# BR IS NOW IMPLEMENTED, and this replaces br_unimplemented.strap.
# p.40 verbatim: "This instruction causes the absolute value of the
# effective address to be added to the instruction counter contents.
# Bits 0-18 of the sum replace the instruction counter contents."  The
# base is the STEPPED counter (p.39 steps it before execution), so the
# address field is a DISPLACEMENT in half-words and the 19-bit wrap is
# "bits 0-18 of the sum".
#
# THE ROUTE HERE IS THE POINT.  audit_opcode_coverage.py found BR listed
# among the implemented branches and executed as an ABSOLUTE branch
# identical to B -- contradicted by the pocket card, which gives B and
# BR different operation codes and names BR "Branch Relative".  It was
# then left UNIMPLEMENTED rather than guessed at, because the base, sign
# and units were unestablished.  A research pass found p.40, which
# settles all three, so it is implemented FROM A SOURCE.  Refusing to
# guess cost one commit and bought a correct implementation.
#
# CASE 1 IS THE MANUAL'S OWN WORKED EXAMPLE AND DOES NOT DISCRIMINATE.
# p.42: "a simple storage of the instruction counter WITHOUT BRANCHING
# ACTION is accomplished by STORE INSTRUCTION COUNTER IF BRANCH RELATIVE
# with a branch address of 0."  A zero displacement must land on the
# fall-through -- but so does a BR that does nothing at all, which is
# what the unimplemented version did.  It is kept because it is the
# manual's own statement and the thing that broke the absolute reading;
# CASE 2, a displacement of two, is what actually discriminates.
# Measured: before the fix this program halted at 004002.00, the "no
# branch" hang.
#
# KNOWN LIMIT, in the code too: p.40 says ABSOLUTE VALUE, and an
# effective address can only go negative through index modification.
# effAddr19 returns an unsigned result with no sign beside it, so an
# index-modified BR whose effective address goes negative uses the
# wrapped value, not the magnitude.  Nothing transcribed exercises it.

run "BB branch-if-off variants (BZB1, BZBN, BZBZ)" ./run_program.sh ../decks/bb_branch_if_off.strap StretchBbOffTb \
    "PC=2834"          # 002611.00; hand-written, not a listing fact
# Three of the seven implemented-but-undriven operations the opcode
# audit named.  bb_branch_on_bit and bb_indicator drive the branch-IF-ON
# half of the family (BB, BB1, BBZ, BBN); the branch-IF-OFF forms that
# also CHANGE the bit had no coverage at all.
#
# THE RULE IT REALLY PINS is the one that is easy to get wrong -- p.41:
# "WHETHER OR NOT the branch was taken, the tested bit is set".  Step 2
# is that case alone: the bit is ON, so a BZBN does not branch, and it
# must still be inverted.
#
# Three injections, three distinct halts, all predicted:
#   modifier applied only when the branch is taken
#                              -> 002603.40  the BB,SCR,$ after BZBN,
#                                            i.e. exactly the p.41 case
#   branch polarity inverted   -> 002601.00  "BZB1 should have branched"
#   set-to-one writes zero     -> 002601.40  T1's "hang up if bit off"
#
# Remaining from that list: the four I/O Suppress-End-Of-Op forms.

# Which indicators does the model WRITE that no program ever NAMES?
# Static, one second, and it runs as a ratchet: a new indicator write
# with no program looking at it fails here instead of landing silently.
#
# It exists because of the hole above.  A model that set all five index
# result indicators unconditionally to 1 passed 300+ sections, since
# every check everywhere branched IF ON.  That was found by attacking a
# green suite; this looks for the same shape across all 56 indicators at
# once.
#
# IT IS A REFERENCE AUDIT, NOT A DISCRIMINATION AUDIT, and its header
# says so: it answers "does any program mention this", never "would any
# program notice if it were wrong".  XF was named by several programs
# and pinned by none until ibox1_bind.strap.
#
# It needed three corrections before its output meant anything, each a
# mechanism programs use that I had not accounted for: BRANCH ON BIT
# against word 11 (ZM, via F214D6's BZB,11.33), the $<IND> symbol as an
# operand (NM, via F219's BB1,$NM), and stripping comments.  The first
# version reported 29 gaps, most of them its own blind spots.  An audit
# that has not been audited is a claim, not a measurement.
#
# The gap it found -- OP and AD -- is now closed by
# ../decks/op_ad_indicators.strap below, so KNOWN_GAP is empty and the
# ratchet holds at "every indicator the model writes is named by some
# program".  That is a floor, not a ceiling: see the caveat above.

run "LVE, Load Value Effective -- indirect addressing, three address widths" ./run_program.sh ../decks/lve_indirect.strap StretchLveTb \
    "lve_full_and_half:1294=0x0143400001434000" \
    "lve_fp_and_indexed:1295=0x0143400001c34000" \
    "lve_target_j_ignored:1296=0x0143400000000000" \
    "PC=2594"
# MCP's bootstrap pinned LVE's ENCODING (printed p.3 line 10 assembles
# bit-for-bit); this pins its EXECUTION, and the two are separately
# earned.  Reference Manual printed p.29: the effective address names a
# HALF WORD, that half word is decoded far enough to work out ITS
# effective address, and THAT goes into the index register named by the
# original instruction's J.  The target's operation is not executed and
# the target's own J is ignored.
#
# ALL THREE WIDTHS GIVE THE SAME ANSWER, which is the design of the
# test.  The target's address field is 24, 19 or 18 bits wide by class,
# and p.21 extends the short ones "with the necessary low-order zeros",
# so three targets of three classes pointing at ONE datum must all
# produce that datum's bit address.  A width bug is off by 32x or 64x,
# not by a little.  The widths are StretchDecode's svaReplaceAddr --
# jb_ax3a printed p.140's six-case table -- exercised here in the LVE
# direction rather than the SVA one.
#
# A CHAIN IS REFUSED OUT LOUD.  p.29 makes a chained LVE an iteration
# with a one-millisecond bound and indicator USA; this E-box runs one
# instruction per step with no inner loop, so a target that is itself
# an LVE sets OP rather than being silently truncated to one level.
# The program checks that too.

run "OP and AD indicators (both polarities)" ./run_program.sh ../decks/op_ad_indicators.strap StretchOpAdIndTb \
    "PC=2462"          # 002317.00; hand-written, not a listing fact
# The two indicators the audit found written-but-unwatched.  HAND-WRITTEN
# from the manual and from the README's own claim -- the weaker standard
# -- because no deck block transcribed so far reaches either bit.
#
#   OP (15) "Operation Code Invalid".  bsv/README.md says instructions
#   decoded but not executed "set indicator 15, OP, and no-op, matching
#   real-machine behavior for a suppressed instruction".  24 setOpInvalid
#   sites, and neither half of that claim was checked.  LVE is out of
#   scope here, so it must set OP and leave $X1 alone; both are checked.
#
#   AD (16) "Address Invalid".  Reference Manual p.20: an effective word
#   address beyond the installed core sets AD and the instruction "is
#   executed as a NO OPERATION".  The core is six units, InstalledWords
#   = 98304 = (8)300000, so L(N),(8)400000.0 is off the end.  AD must
#   come on and the accumulator must be untouched; both are checked.
#
# BOTH POLARITIES, which is the whole lesson of index_indicators_off:
# each bit is checked OFF after an ordinary instruction FIRST and only
# then ON after the offending one.  Three injections, three distinct
# halts, all predicted:
#   OP never set        -> 002305.40  (BZB,$OP,$ after the LVE)
#   AD never set        -> 002311.00  (BZB,$AD,$ after the off-core load)
#   both forced ON      -> 002300.40  (the FIRST off-check, after an
#                                      ordinary LX)
# That last one is the analogue of the injection that passed everywhere
# before index_indicators_off existed.  Here it fails.
#
# EXPECTED NOISE, and a real interaction worth knowing about.  This
# program makes StretchCore print "E-box instruction at 2449 executed at
# preparation (classification mismatch)".  It is not a defect and it is
# not spurious: the core probes an operand-fetching E-box instruction by
# running execute() with no operand and expecting it to bail out with
# the address it wants, but the AD guard skips the operand read
# entirely, so the instruction COMPLETES during what was meant to be a
# side-effect-free probe.  The core detects exactly that, says so, and
# commits the probe as the execution -- which is why AD is set and the
# accumulator is untouched.  The classification cannot know in advance,
# because AD depends on the effective address.

run "AD by SIC below 16.0 (the other trigger)" ./run_program.sh ../decks/ad_sic_indicator.strap StretchAdSicTb \
    "PC=2573"          # 002406.40; hand-written, not a listing fact
# AD's SECOND trigger, and a separate program on purpose.  AD is
# SET-ONLY -- nothing in the model clears it, and BRANCH ON BIT cannot,
# because Reference Manual p.41 only lets BB change indicator positions
# 20-63 and AD is bit 16.  So appending this case to op_ad_indicators
# would find AD already on and its check would prove nothing.  A fresh
# program is what makes the on-check discriminating.
#
# The rule, Reference Manual p.42: "the instruction counter may be
# stored in any available location with 19-bit address 16.0 or above"
# -- below that AD is set and NOTHING IS STORED.  $FT is word 14, the
# Factor register: below 16.0, freely writable, no side effects.  Set
# its bit 0, aim SIC at it, and since SIC stores the counter into bits
# 0-18 of the target half-word and the counter's top bit is 0 here, a
# store that actually happened would clear that bit.  One BZB then
# separates "nothing stored" from "something was", with no compare.
#
# BOTH HALVES MEASURED SEPARATELY, because one injection cannot
# separate them -- dropping the ha < 32 test both skips AD and performs
# the store, so it only proves whichever check comes first:
#   AD never set                   -> 002404.00  the BZB,$AD,$
#   AD set but the store happens   -> 002405.00  the BZB,$FT,$
#
# AND ONE INJECTION THAT PASSED, a fact about the model: relaxing the
# READ-bail guard from "o.taken && ha >= 32" to "ha >= 0", so a SIC
# below 16.0 fetches its target before discarding it, changes nothing
# observable -- the AD branch suppresses the store regardless.  That
# guard is an optimisation, not a correctness requirement.

run "Index result indicators: OFF states and clearing" ./run_program.sh ../decks/index_indicators_off.strap StretchIndexIndOffTb \
    "PC=2346"          # 002225.00; hand-written, so this is not a listing fact --
                       # if the program's layout changes, update it deliberately
# THE CONTROL FOR A HOLE THE DECK LEFT OPEN.  ibox1_bind.strap pins all
# five index result indicators ON, and the only OFF it checks is the one
# the trailing-Z clear produces -- never an indicator off because its
# condition is false.  Measured: a model that sets XF, XCZ, XVLZ, XVZ and
# XVGZ unconditionally to 1 passes that whole deck routine, and passes
# index_result_indicators.strap too, whose checks are all branch-IF-ON.
#
# This is the complement.  HAND-WRITTEN from the Reference Manual, which
# is the weaker of the two standards here and says so in its header: the
# deck has no block that checks these off.  p.24 -- an index load sets
# the flag and result indicators FROM THE LOADED WORD -- makes all five
# assigned, so a load must clear the ones whose condition is false.
#
# Every off-check follows an on-state, so each one tests CLEARING rather
# than mere absence.  The three words are the deck's own seed constants
# (IBXWZO, IBXWZ2, IBXWZ1), walking the value negative, positive, zero.
#
# Two injections, failing at different lines, each where the semantics
# predict:
#   all five forced ON        -> 002202.00, BXVZ,$  (first off-check)
#   sets but never clears     -> 002203.40, BXF,$   (first clear-check,
#                                after the second load)
# The first is exactly the injection that passes everywhere else.
#
# TWO LATER ADDITIONS, both from mutation_score.py.
#
# THE FLAG/COUNT CONFOUND.  The three words above are the deck's own
# seed constants, and in ALL THREE flag == (count == 0).  That made
# every purpose-written index-indicator program blind to a model
# reporting XF from the COUNT field: that mutation was caught 300
# sections later by an I/O test, by accident.  WFLAG (flag 1, count 1)
# and WNOFLG (flag 0, count 0) vary the two independently, one in each
# direction, and the mutation now halts here at 002211.40.  A green
# suite and two empty audits did not show this; only mutation did.
#
# NEGATIVE ZERO.  p.24 sets XVLZ when the value is "non-zero AND
# negative", so minus zero must leave XVLZ off and XVZ on.  Dropping
# the non-zero term SURVIVED the whole suite.  The word is a raw DD
# literal because the assembler normalises -0 in an XW value field to
# +0; the mutation now halts at 002215.00.

run "Index compares set XF (a fixed bug with no test)" ./run_program.sh ../decks/cmp_sets_index_flag.strap StretchCmpXfTb \
    "PC=2964"          # 002712.00; hand-written, not a listing fact
# mutation_score.py mutated setIndexCmpIndicatorsF to leave XF alone and
# the mutation SURVIVED the entire suite.  That is not hypothetical:
# StretchExecute's own comment on that function records it as a bug that
# WAS there -- "This helper used to set only XL/XE/XH, so all five
# compares left XF stale" -- fixed earlier in the project, with nothing
# written that would notice it coming back.  A documented past fix with
# no regression test is an invitation to reintroduce it silently.
#
# p.24 for KV/KC and p.25 for KVI/KVNI/KCI, same words: "the index-flag
# and index-comparison indicators are set in each of the last two
# operations".  XF is bit 38, so BRANCH ON BIT can drive it to a known
# state first (p.41 allows positions 20-63) -- which is what makes both
# directions testable: force XF wrong, compare, require the compare to
# have corrected it.  BOTH directions, because a compare that merely
# ORed the flag in would pass the first half.  Measured: the mutation
# now halts at 002703.00.

run "Branch target modified by an index register" ./run_program.sh ../decks/branch_index_modified.strap StretchBrIdxTb \
    "PC=3022"          # 002747.00; hand-written, not a listing fact
# Replacing "o.target = effAddr19(st, bm.addr, bm.idx)" with the raw
# address -- dropping index modification of branch targets entirely --
# SURVIVED the whole suite.  effAddr19 returns the raw address when idx
# is 0, so a survivor means exactly one thing: not one program in 160+
# branched through an index register.  The feature was completely
# unexercised.
#
# TWO CASES, AND THE SECOND ONE WAS MISSING UNTIL AN AUDIT CAUGHT IT.
# The original program used a POSITIVE index value, and effAddr19 reads
# "(x.sign == 1) ? (raw - m) : (raw + m)" -- a positive value takes the
# same branch whether or not the sign is honoured.  So it died only to a
# mutation that dropped modification ENTIRELY, and what it pinned was
# "modification happens", NOT "the sign is honoured".  Four places
# (a commit message, the plan doc, fp_negative_modifier's header and
# mutation_score.py) claimed a three-row table in which all three
# effAddr helpers had their SIGNED rule pinned; for effAddr19 that was
# false.  Case 2 uses a negative value and closes it: measured, mutating
# effAddr19 to "return raw + m" now halts at 002744.00, the "the SIGN
# was ignored" line, and passed before.
#
# p.20-21 "Address Modification" plus p.39, which applies it to
# branching like anything else.  UNITS ARE THE TRICK: effAddr19 adds
# the index value's low 19 bits to a HALF-WORD address while the value
# field is a BIT address, so a value of 1 moves the target one
# half-word.  LVI cannot express that (it shifts its immediate left by
# five), so the offset comes from an XW whose value is the bit address
# (8)0.01.  Measured: the mutation now halts at TGT, 002741.00, the
# deck-style "hang up: the index was ignored".

run "Address modification by a NEGATIVE index value" ./run_program.sh ../decks/index_negative_modifier.strap StretchNegIdxTb \
    "PC=3472"          # 003310.00; hand-written, not a listing fact
# Replacing effAddr24's signed add with an unconditional one -- dropping
# the index value's SIGN -- survived the whole suite.  effAddr24 is the
# address-modification helper behind every bit-addressed instruction, so
# a survivor means not one program in 160+ ever indexes with a NEGATIVE
# value.  Index words with negative values are everywhere in the suite;
# none was being used as a MODIFIER.
#
# NOT THE SAME GAP as the branch test above.  That one closed
# effAddr19, the 19-bit half-word helper the branches use, and
# effAddr19 keeps its OWN copy of the sign test.  Closing one said
# nothing about the other: two helpers, two mutations, two tests.  A
# single "index modification works" test would have looked like
# coverage of both.
#
# p.20-21: the SIGNED value field is added to the address field.  SCR's
# bit 0 is set and the BZB addresses SCR2 -- one word ABOVE it --
# modified by an index one word NEGATIVE, so the effective address comes
# back to SCR.  With the sign ignored it runs the other way to DUMMY,
# whose bit is zero; BZB branches when the bit is off, so the wrong
# address hangs.  Measured: the mutation halts at 003302.40.

run "Negative index modification on the FP path (third copy)" ./run_program.sh ../decks/fp_negative_modifier.strap StretchFpNegIdxTb \
    "PC=3598"          # 003407.00; hand-written, not a listing fact
# THE THIRD COPY OF ONE RULE.  p.20-21's signed address modification is
# written out three independent times in this model:
#   effAddr18  floating point           <- this program
#   effAddr19  branches                 <- branch_index_modified.strap
#   effAddr24  bit-addressed operations <- index_negative_modifier.strap
# Each was mutated separately and EACH SURVIVED until its own program
# existed.  Closing one said nothing about the others.  A test named
# "index modification works" would have implied all three, and how many
# copies exist is a fact about the code that has to be looked up --
# no test can report it.
#
# Same shape as the effAddr24 program: FPVAL holds a non-zero fraction,
# the load addresses FPA2 one word above it with an index value of one
# NEGATIVE, and DUMMY sits on the far side as the wrong answer, zero and
# therefore unequal.  Measured: the mutation halts at 003401.40.
#
# UNITS, RECORDED AS AN OPEN OBSERVATION.  effAddr18 adds the index
# value truncated to 18 bits to a WORD address, so a value of 1 moves
# one WORD; effAddr24 adds the same field to a BIT address, where 1
# moves one bit.  The value field is a 24-bit BIT address, so the two
# helpers read one field in different units.  That may be right -- the
# FP address field is itself an 18-bit word address -- but nothing
# transcribed pins it and this program does not settle it.  It pins the
# SIGN only.

run "Mask register fixed and writable fields (word 12)" ./run_program.sh ../decks/mask_register_fields.strap StretchMaskTb \
    "PC=3229"          # 003116.40; hand-written, not a listing fact
# A FIX WHOSE OWN COMMENT SAID NO TEST WOULD NOTICE IT.
# StretchStorage.bsv, on the mask register: "...the register, its write
# masker and StretchTypes' own comment all said 0-19 while the code did
# 0-15.  NOTHING DRIVES WORD 12 IN THE TRANSCRIBED DIAGNOSTIC, SO THIS
# WAS NEVER CAUGHT BY A TEST -- found by a code review against the
# Appendix A field table."  A corrected boundary with nothing to stop it
# being undone is the same shape as the compares' XF, except the code
# states it outright.
#
# The rule, Reference Manual p.45 and the Appendix A field table: mask
# bits 0-19 are permanently ONE, 20-47 are program settable, 48-63 are
# permanently ZERO.  All three regions are checked.
#
# BIT 16 IS THE WHOLE POINT, not bit 0.  The old code forced only IBM
# 0-15, so bits 16-19 were writable; the corrected code forces 0-19.
# Only an attempt to CLEAR bit 16 that must fail separates them -- bit 0
# passes under both and proves nothing.  Measured: reverting the masker
# and the register's initial value to the pre-fix 0-15 boundary halts at
# 003101.00, the bit-16 check, and nowhere else.
#
# There is no $ symbol for word 12, so it is addressed numerically:
# word 12 is octal 14 and the bit is an octal fraction, so (8)14.20 is
# word 12 bit 16.

run "ZM's normalized term and exponent bound" ./run_program.sh ../decks/fp_zm_terms.strap StretchFpZmTb \
    "PC=3352"          # 003214.00; hand-written, not a listing fact

run "ZM on the DOUBLE multiply (the copy nothing tested)" ./run_program.sh ../decks/fp_zm_terms_double.strap StretchFpZmDblTb \
    "PC=3480"          # 003314.00; hand-written, not a listing fact
# THE SAME RULE, THE OTHER IMPLEMENTATION.  p.99's ZM rule is written
# TWICE in StretchFP.bsv, character for character:
#
#     line 732  fpMul        (*)     covered by fp_zm_terms.strap
#     line 929  fpMulDouble  (D*)    covered by NOTHING until now
#
# MEASURED 2026-09-22, and this is the number that matters: changing
# line 929's "(e > -1024)" to "(e >= -1024)" and running the WHOLE
# suite gave 3059 PASS, 0 FAIL.  A rule of the machine with no witness
# anywhere in the project, sitting behind a 32/33 mutation score.
#
# THE MUTATION TABLE COULD NOT SEE IT EITHER, and that is the part
# worth remembering.  Both ZM mutants used that identical line as
# their search pattern, and mutation_score.apply() did
# replace(old, new, 1) -- so BOTH mutated fpMul, both were reported
# "caught" by the section above, and fpMulDouble was never touched.
# The score was right, the evidence was not.  mutation_score.py now
# REFUSES a pattern that does not match exactly once (see _ambiguous),
# the two old mutants carry their preceding line to disambiguate them,
# and zm-double-drops-normalized-term / zm-double-exponent-bound
# target this copy.
#
# This program is fp_zm_terms.strap's three cases with D* for *: a
# zero product is zero whichever length the multiply keeps, and the
# exponent sum is the same, so the same constants drive the same three
# branches.  Case 3 is the one that bites -- injecting ">=" at line 929
# halts it at 003306.40, its own "BB,$ZM,$", not at PASS.
#
# docs/NEXT.md's trap list has said for a long time that "when a rule
# has more than one implementation, each copy needs its own witness",
# and names ZM's clear at 16 copies.  This is that trap found on the
# INSTRUMENT rather than the model.
# Two mutation survivors, both ZM.  fpMul sets it as
# "normalized && zero && (e > -1024)" (p.99), and jb_af1c F214D6 -- the
# first and only test of ZM anywhere in the transcribed diagnostic --
# pins the indicator's EXISTENCE, not its two qualifying terms.
#
# THE NORMALIZED TERM was already characterised in the plan doc, after
# an injection "wrong in the most useful way yet": the only F214
# multiply where dropping `normalized` changes anything is C1, and C1
# checks REGISTERS, not indicators.  The campaign rediscovered that
# without being told, which is the right confirmation for a gap that was
# found by reasoning.  THE EXPONENT BOUND is new -- nothing transcribed
# lands a zero product ON the boundary, so > and >= are the same.
#
# The constants are built from the format directly (fpFromWord: ef at
# 63, em at 62-53, es at 52, fraction at 51-4) because the pool has
# nothing with a zero fraction at a chosen exponent.  A multiply by a
# zero-fraction operand gives a zero product whose exponent is the SUM,
# so -512 x -512 lands on exactly -1024, the boundary itself.
#
# CASE 1 IS A POSITIVE CONTROL AND NOT OPTIONAL: without it a model that
# never set ZM would pass both off-checks.  Measured, three distinct
# halts:
#   ZM never set            -> 003201.40, case 1   (the control)
#   normalized term dropped -> 003204.00, case 2
#   bound >= instead of >   -> 003206.40, case 3
#
# ONE TRAP, ON RECORD AND WALKED INTO ANYWAY: a bare `*` is AMBIGUOUS
# and assembles as a 64-bit VFL instruction (op 0x80), not an FP
# multiply -- exactly as a bare `L` does.  It must be written `*(N)`.
# The first version of this program used `*` and failed in a way that
# looked like a model bug.

run "Every FP operation but MULTIPLY clears ZM" ./run_program.sh ../decks/fp_zm_cleared.strap StretchFpZmClrTb \
    "PC=3846"          # 003603.00; hand-written, not a listing fact
# ONE RULE, SIXTEEN COPIES -- the largest instance of the pattern so
# far, and found the same way as the six SEOP copies: by grepping a
# distinctive line, not by any coverage audit.  ZM is a MULTIPLY-ONLY
# indicator, so every other FP arm has to turn it off, and
# "ind = setBit(ind, ind_ZM, 0)" is written out once per arm.
#
# WHAT WITNESSED IT BEFORE: one copy.  The plan doc records that "never
# clearing ZM halts D5's ZM row at 017331.00".  One of sixteen.
#
# TEN ARMS ARE COVERED HERE -- L, +, /, LFT, DL, M+, F+, D+, D/, E+ --
# by one program rather than ten, because the copies are uniform.  Each
# case sets ZM with a normalized multiply whose product is
# order-of-magnitude zero, CONFIRMS IT IS ON, runs the operation, and
# requires it off.  The confirm step is not decoration: without it a
# model that never set ZM would pass every off-check.
#
# Measured, one mutation per arm, each halting at its OWN check.
#
# F+ IS IN THE LIST BECAUSE ITS MUTATION PASSED.  The first version of
# this program described F+ in its header and did not test it.  A
# description is not coverage, and only the mutation told them apart.
#
# R/ IS DELIBERATELY ABSENT.  Its case hung, and not because of a model
# bug: for RECIPROCAL DIVIDE the divisor is the ACCUMULATOR (p.94,
# operands interchanged), and R/'s ZM clear sits inside the else of
# "if (r.zd)".  ZM can only be on after a multiply that left an
# order-of-magnitude ZERO product in the accumulator, so the divisor is
# always zero, r.zd always fires, and the clear is always skipped.
# Reaching it needs a non-zero accumulator while ZM stays on, and every
# FP operation clears ZM on the way past -- so the line is recorded as
# POSSIBLY-UNREACHABLE, not as dead code, since no non-FP path was
# checked.  A branch upstream making a downstream line unreachable is
# the mechanism the plan doc already names; here it caught a test
# DESIGN, not the model.
#
# THE CONSTANTS NEED AN EXPLICIT SLC.  DD emits at the location
# counter, so a data section after the code sits wherever the code ends
# -- and growing this program from six cases to eleven ran the code
# straight over ZF0 and NZF0, silently.  The symptom was case 1, the
# FIRST check, failing with identical source that had passed minutes
# before: the multiply's operand was no longer zero.

# -- 0e. I-Box 4 routine 150's CB / CB+ / CBR / CBR+ blocks (plus their
# LX/SX setup and XW index words) assembled verbatim at the listing's
# own addresses and compared against docs/jb_ax4b_ibox-4.pdf pp.155/159's
# printed machine code -- the first external check of CB_CODES, LX/SX,
# and the packed index-word layout. Pure Python, no Bluesim.
run "I-Box 4 listing bit-exact comparison" python3 verify_ibox4_listing.py

# -- 1. Hand-assembled BSV smoke test (StretchSmoke.bsv, not STRAP-derived) --
cd "$BSV_DIR"
run "bsv smoke test (make run)" make run
# -- 1b. StretchDecode's instruction formats swept against the length
# tag jb_ax3a p.140 states, over all 2^14 half-words (both with the
# address field zeroed and all ones).  Not a program: it drives
# decodeHalfWord directly.
#
# It exists because dirIndexOp's SVA arm picks its address width off
# bits 24-27 and 26-27 rather than off decodeHalfWord, which is what
# p.140 describes and what hardware can actually do -- the width is
# combinational on the length tag and cannot consult a table of which
# operation codes are assigned.  Measured, and the reason for the
# change: taking the class from the decode instead disagrees with p.140
# on 768 of the 32768 half-words, all of them the three 7-bit codes
# ending in 10 that isValidFpCode does not list (1101010, 1111010,
# 1111110).  Bits 26-27 say FP and 18 bits; the decode says Invalid and
# the width fell back to 19.
#
# The sweep checks TWO different things, and it is worth being exact
# about which protects what.
#
# (a) It probes svaReplaceAddr itself -- the function dirIndexOp calls
# -- at every half-word, in three ways, because one probe turned out to
# check much less than it looked like:
#
#   EXTENT        substitute an all-zero and an all-one value, XOR the
#                 results: the differing bits are the ones replaced.
#   PRESERVATION  nothing OUTSIDE those bits may differ from the
#                 original half-word.  Needed because a constant
#                 clobber CANCELS out of every XOR probe, and the
#                 transcribed blocks read back with LX then KV, which
#                 compares the value field and never sees the op byte.
#   ORDER         walk a one-hot value through IBM bits 0-23; require
#                 one bit per step, the first at the half-word's top
#                 bit, strictly decreasing, and a prefix as long as the
#                 width.  Needed because EXTENT is blind to a
#                 PERMUTATION -- all-zero and all-one are symmetric
#                 under reordering.
#
# MEASURED, and the reason all three exist: swapping two bits of the
# value field passes the extent probe AND all 277 sections.  The
# transcribed blocks test IBM bits 22-23 (ibox3_sva_full) and all-ones
# patterns over 0-17 (ibox3_sva_fp, _dix), where a swap of two ones is
# invisible.  Negative controls, each firing on its own probe: the
# permutation reports "not placed top-down, in order"; returning
# {v, 8'b0} reports "changed bits outside the replaced field"; putting
# the decode-based class test back reports the 768 mismatches again.
#
# This is also the only check anywhere that can see the width change
# itself: the bit rule is a strict superset of the decode rule (every
# fpop_* ends in 10), so no ASSIGNED operation code moves and every
# transcribed block passes either way.  A green suite is not evidence
# for that change; the sweep is.
#
# (b) It checks that every format decodeHalfWord DOES recognize sits
# inside the tag class p.140 assigns it. That is NOT protecting SVA any
# more -- SVA no longer consults the decode -- it protects the decode
# tables, which fetch and execute do depend on, and whose disagreement
# with the tag is what made the old width wrong. Negative control:
# changing tryCountBranch's literal from 1001 to 0001 reports 1536
# mismatches. (Adding a bogus FP code does NOT break it -- Fp is tried
# last and every code ending in 00 is already claimed by an earlier
# format, which the testbench header works out.)
run "SVA width vs jb_ax3a p.140 (all 2^14 half-words)" ./run_tb.sh StretchSvaWidthSweep
cd "$TESTS_DIR"

# Timing bounds ("CYCLES<=N", the clock count at halt with one clock =
# one 0.3 us E-box cycle). History: stage 1 (memory units behind the
# MBCU) measured 94 for Problem 2.1 and 2714 for the pp.43-51 span;
# stage 2a (prefetch) 54 and 2065; stage 2b (per-class I-box/E-box time
# budgets from IBM's tables, E-box time not yet overlapped) 113 and
# 4006. Bounds carry ~10-25% slack; they catch timing regressions and
# tighten as later stages add overlap (docs/microarchitecture_plan.md).
# -- 1b. Instruction-unit timing microbenchmark: ten taken CBs in a
# NOP/CB loop (see the program's header for the table arithmetic, 250
# clocks + first fetch). Measured 291 at stage 2b; the excess is the
# branch-restart fetch latency the real CB sequence overlaps (Blosk
# fig.8) and this model does not yet -- a stage-3 target, so the bound
# is deliberately tight at 300.
run "I-box timing: CB loop" ./run_program.sh ../decks/ibox_timing_cb.strap StretchTimingCbTb \
    "X1_count:addrIndex(1)=0" \
    "CYCLES<=300"

# -- 1c. Look-ahead timing microbenchmark: four full-word VFL loads,
# E-box-bound with fetch-ahead (~115 clocks; the note here said
# "measured 120" and the figure is 113 -- re-measured 2026-09-25 and
# stale INDEPENDENTLY of the interruption-timing change, since the
# PRE-fix model also gives 113) vs ~172
# executed serially; the bound of 140 fails if the overlap is lost
# (as it was when the E-box busy wait preempted preparation).
run "Look-ahead timing: four loads" ./run_program.sh ../decks/la_timing_loads.strap StretchTimingLaTb \
    "ACC_right:9=4" \
    "CYCLES<=140"

# -- 1d. I-box run-ahead benchmark: a ten-iteration L/+/ST loop closed
# by V+ and CB. E-box-bound with the I-box instructions hidden (~800
# clocks, measured 807) vs ~1120 if the I-box waited for the levels to
# drain each time; bound 900.
run "Look-ahead timing: L/+/ST/V+/CB loop" ./run_program.sh ../decks/la_timing_loop.strap StretchTimingLoopTb \
    "SUM:38=10" \
    "X2_value:addrIndex(2)=0x2800000000000" \
    "CYCLES<=900"

# -- 1e. Branch guess and wrong-way recovery (plan §6d): one branch on
# RZ taken against the not-taken guess (the index arithmetic run ahead
# must be undone), one not taken (it must stand). The halt PC (label
# DONE) is derived from the assembled symbol table rather than hard-
# coded, so it tracks layout (full-word instructions are half-word
# aligned -- Gotchas item 19). Injection (recovery's index restore
# removed): X1 comes back 5.0 instead of 4.0 (observed: one of the two
# run-ahead adds had executed when the branch resolved).
run "Look-ahead: branch guess + recovery" ./run_program.sh ../decks/la_branch_guess.strap StretchGuessTb \
    "X1_4:addrIndex(1)=0x1000000000000" \
    "X2_2:addrIndex(2)=0x800000000000" \
    "X3_zero:addrIndex(3)=0" \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/la_branch_guess.strap").read()).symtab["DONE"]//32)')" \
    "CYCLES<=260"

# -- 1f. Floating-point arithmetic (stage 4c, StretchFP.bsv): L, *, +
# and ST in normalized single precision, operands and expected results
# built in Python from the 7030 format (fp_arith_expected.py). Divide
# is deferred to the multi-cycle arithmetic unit (stage 4e).
run "Floating point: L / * / + / ST" ./run_fp_test.sh

# -- 1g. Address Invalid (Reference Manual p.20): a floating-point load
# from a word beyond the installed core (98304 words) sets AD and no-ops.
# Injection (boundary moved to the 18-bit type max) fails both checks.
run "Address Invalid (AD, no-op)" ./run_fp_addr_test.sh

# -- 1h. Floating-point exponent and shift ops (Reference Manual
# pp.101-102): E+I (add immediate to exponent), E+ (add to exponent),
# SHF (shift fraction). Injection G (E+ subtracts) fails the E+ check.
run "Floating point: E+ / E+I / SHF" ./run_fp_exp_test.sh

# -- 1i. FP sign-modifier loads (LN/LA/LNA), the assembler gap the
# floating-point diagnostic jb_af1c drove out. verify_fp_signmods.py
# checks the encoding bit-for-bit against jb_af1c's printed machine
# code (pure Python); run_fp_signmod_test runs LN/LA/LNA on the model.
run "FP sign modifiers (encoding vs jb_af1c)" python3 verify_fp_signmods.py
run "FP sign modifiers (LN/LA/LNA on the model)" ./run_fp_signmod_test.sh

# -- 1i'. First real jb_af1c block RUN on the model: routine F202A
# sub-tests 19/20 (docs/jb_af1c_floating-point.pdf p.33), FP compares
# of FPK2 against FPK26 (XFP range) and FPK21 (N range), each expecting
# AL on. verify_fp_compare_listing.py checks the transcription (code +
# the three constants) bit-for-bit against the printed machine code;
# the run halts at PASS iff the FP compare sets exactly AL (a wrong
# indicator branches to the substituted SERS FAIL halt). Injection
# (AL/AH swapped in StretchExecute's FP compare arm): halts at SERS
# (PC 1416) instead of PASS (9782), as predicted.
run "FP compare block (jb_af1c F202A15-20, encoding)" python3 verify_fp_compare_listing.py
run "FP compare block (jb_af1c F202A15-20 on the model)" ./run_program.sh ../decks/fp_compare_f202a.strap StretchFpCmpTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_compare_f202a.strap").read()).symtab["PASS"]//32)')"

# -- 1i''. Companion block from the start of the same routine (F202A1-6,
# p.30): FP compares in the NORMAL exponent range, including the AE
# (equal) outcome (FPK0 vs FPK0). Encoding bit-for-bit, then the model
# run halts at PASS iff every compare sets the expected indicator.
run "FP compare block (jb_af1c F202A1-6, encoding)" python3 verify_fp_compare_a1_listing.py
run "FP compare block (jb_af1c F202A1-6 on the model)" ./run_program.sh ../decks/fp_compare_f202a1.strap StretchFpCmpA1Tb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_compare_f202a1.strap").read()).symtab["PASS"]//32)')"

# -- 1i'''. KR Compare-for-Range (jb_af1c F202G11-18, p.45): eight
# sub-tests pairing AH-on (BB1,$AH gate) with AH-off (Z,$IND gate) over
# five operand pairs. Encoding bit-for-bit, then the model run halts at
# PASS iff KR obeys p.91 (sets AE=acc-low when AH on, leaves AL/AH).
# Injection (KR AE forced off): halts at SERS at G15.
run "FP compare block (jb_af1c F202G KR range, encoding)" python3 verify_fp_compare_g_listing.py
run "FP compare block (jb_af1c F202G KR range on the model)" ./run_program.sh ../decks/fp_compare_f202g.strap StretchFpCmpGTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_compare_f202g.strap").read()).symtab["PASS"]//32)')"

# -- 1i''''. FP Add-to-Memory arithmetic checks (jb_af1c F204A1-3, p.53):
# ENCODING only. The transcription assembles bit-for-bit against the
# page (M+, CT0110, VFL BU load/store). The model run reaches PASS but
# is NOT wired here: it is not yet a discriminating test of M+ (its XFP
# operands and "error if fractions added" check pass even for an M+ that
# leaves the sum unchanged) -- see the program header and the plan's FP
# row. Encoding is the verified part.
run "FP add-to-memory block (jb_af1c F204A, encoding)" python3 verify_fp_arith_f204a_listing.py

# -- 1i'''''. Discriminating M+ (Add to Memory) test: jb_af1c F204A5
# (p.53). N-range operands FPK35 + FPK39; the sum is checked against a
# precomputed FPK32 via CT0110 + BRGZ, so a wrong M+ fails. Encoding
# bit-for-bit, then the model run halts at PASS iff M+ is correct.
# Injection (fpAdd drops the added operand): halts at SERS. Unlike
# F204A1-3, this catches a broken M+ (its operands share an exponent,
# so the sum genuinely changes).
run "FP M+ block (jb_af1c F204A5, encoding)" python3 verify_fp_arith_f204a5_listing.py
run "FP M+ block (jb_af1c F204A5 on the model)" ./run_program.sh ../decks/fp_arith_f204a5.strap StretchFpAdd5Tb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f204a5.strap").read()).symtab["PASS"]//32)')"

# -- 1i''''''. Sign-modifier combinations on ADD TO MEMORY: jb_af1c F204B
# (pp.55-58), sixteen sub-tests of M+ / M+A / M- / M-A over every
# memory-sign / accumulator-sign combination, each checking the result
# fraction (CT0110 on bits 0-59) and the sign bit (BB/BZB on ROS bit
# 60). Establishes p.81-82's rule (A on the storage operand, N on the
# accumulator) and p.82's zero-sign rule. Encoding bit-for-bit (183
# words), then the model run halts at PASS iff all sixteen pass; SEN
# (the error SIC's word) must still be 0. First run caught a real bug
# (the zero-result sign on an exponent tie took the storage operand's
# sign) -- see the program header.
run "FP M+ sign modifiers (jb_af1c F204B, encoding)" python3 verify_fp_arith_f204b_listing.py
run "FP M+ sign modifiers (jb_af1c F204B on the model)" ./run_program.sh ../decks/fp_arith_f204b.strap StretchFpAddBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f204b.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- 1i'''''''. jb_af1c F204C (p.59): ADD TO MEMORY leaves $L, $R and the
# sign byte register untouched -- zeros stay zeros, ones stay ones,
# checked with connectives over the full 64-bit halves (offset 64 = L)
# and the 8-bit sign byte at 10.0. First run caught the model's
# accumulator layout (sign in bit 0 of word 8, a 127-bit magnitude,
# and word 10 holding its LOW byte): now 128 magnitude bits with the
# sign byte at IBM bits 0-7 of word 10, sign in bit 4 -- see the
# program header.
run "FP M+ unchanged registers (jb_af1c F204C, encoding)" python3 verify_fp_arith_f204c_listing.py
run "FP M+ unchanged registers (jb_af1c F204C on the model)" ./run_program.sh ../decks/fp_arith_f204c.strap StretchFpAddCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f204c.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- 1i''''''''. jb_af1c F204D (pp.60-64): the indicators ADD TO MEMORY
# sets -- MOP, RLZ/RN, RZ, RGZ, PSH on/off, LC, LS on/off, and the
# five exponent-range indicators one at a time -- sixteen sub-tests.
# First run caught a look-ahead ordering bug: Z,$IND ran ahead of the
# unretired L(U) level that sets XPL. An I-box store to words 7-15 now
# drains the look-ahead (StretchIBox.bsv eboxRegister) -- see the
# program header.
run "FP M+ indicators (jb_af1c F204D, encoding)" python3 verify_fp_arith_f204d_listing.py
run "FP M+ indicators (jb_af1c F204D on the model)" ./run_program.sh ../decks/fp_arith_f204d.strap StretchFpAddDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f204d.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- 1i'''''''''. jb_af1c F204E (p.65): the normalization modifier on
# ADD TO MEMORY -- ignored when the result is a flagged operand (XFP
# or XFN), applied when it is the unflagged survivor of XFN + N or an
# N + N sum. First run caught fpAdd suppressing normalization of an
# unflagged survivor (E4: FPK7 came back unnormalized, FPK6 expected)
# -- see the program header.
run "FP M+ normalization modifier (jb_af1c F204E, encoding)" python3 verify_fp_arith_f204e_listing.py
run "FP M+ normalization modifier (jb_af1c F204E on the model)" ./run_program.sh ../decks/fp_arith_f204e.strap StretchFpAddETb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f204e.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- 1k. jb_af1c F205A (p.66): ADD TO MAGNITUDE (+MG) arithmetic checks,
# nine sub-tests -- flagged operands dominating, an N + N sum, and the
# forced-zero case (XFN accumulator + negative XFP operand: exponent
# of the survivor, zero fraction), checked in the accumulator's left
# half at offset 68 / 116. First run caught the flagged-operand path
# skipping the forced-zero rule -- see the program header.
run "FP +MG arithmetic (jb_af1c F205A, encoding)" python3 verify_fp_arith_f205a_listing.py
run "FP +MG arithmetic (jb_af1c F205A on the model)" ./run_program.sh ../decks/fp_arith_f205a.strap StretchFpMgATb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f205a.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- 1k'. jb_af1c F205B (pp.67-72): +MG / +MGA / -MG / -MGA over every
# memory-sign / accumulator-sign combination, thirty-two sub-tests,
# each checking the accumulator at offset 68 and its sign bit at
# $SB+.4. Establishes that the result keeps the accumulator's own sign
# (forced zeros included) -- see the program header.
run "FP +MG sign modifiers (jb_af1c F205B, encoding)" python3 verify_fp_arith_f205b_listing.py
run "FP +MG sign modifiers (jb_af1c F205B on the model)" ./run_program.sh ../decks/fp_arith_f205b.strap StretchFpMgBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f205b.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- 1k''. jb_af1c F205C + F205D (pp.73-74): +MG leaves the right half,
# the sign byte's bits 0-3 and 5-7 and the left half's bits 60-63
# alone (zeros and ones), and the LS indicator: on for x + (-x), off
# for 0 + 0, off for a forced zero, off for a propagated flagged
# operand -- see the program header.
run "FP +MG unchanged registers and LS (jb_af1c F205C/D, encoding)" python3 verify_fp_arith_f205cd_listing.py
run "FP +MG unchanged registers and LS (jb_af1c F205C/D on the model)" ./run_program.sh ../decks/fp_arith_f205cd.strap StretchFpMgCDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f205cd.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- 1l. jb_af1c F206A (pp.75-77): ADD MAGNITUDE TO MEMORY (M+MG),
# fifteen arithmetic checks -- the same flagged-operand dominance as
# +MG but with the result in storage, and the forced zero that keeps
# the ADDRESSED operand's sign and exponent (A9), plus the
# normalization modifier over flagged and N results (A10-A15). A9
# caught fpAdd applying +MG's forced-zero rule in the to-memory
# direction -- see the program header.
run "FP M+MG arithmetic (jb_af1c F206A, encoding)" python3 verify_fp_arith_f206a_listing.py
run "FP M+MG arithmetic (jb_af1c F206A on the model)" ./run_program.sh ../decks/fp_arith_f206a.strap StretchFpMgMemATb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f206a.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- 1l'. jb_af1c F206B (pp.78-84): ADD MAGNITUDE TO MEMORY over every
# memory-sign / accumulator-sign / N / A combination, thirty-two
# sub-tests, each checking ROS's exponent and fraction at offset 4 and
# its sign bit by BZB/BB. Establishes that the accumulator operand's
# sign is the one assumed positive, and that the result keeps the
# ADDRESSED operand's own sign whatever the sum's -- B19 caught the
# model storing the sum's. See the program header.
run "FP M+MG sign modifiers (jb_af1c F206B, encoding)" python3 verify_fp_arith_f206b_listing.py
run "FP M+MG sign modifiers (jb_af1c F206B on the model)" ./run_program.sh ../decks/fp_arith_f206b.strap StretchFpMgMemBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f206b.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- 1l''. jb_af1c F206C (p.85) + F206D (pp.86-88), the last two blocks
# of the ADD MAGNITUDE TO MEMORY family: C, that M+MG leaves both
# accumulator halves and the whole sign byte untouched (zeros and
# ones); D, the LS indicator (on for a cancellation, off for both
# operands zero, off for a forced zero, off for a propagated flagged
# result) and the five exponent-range indicators XPFP/XPO/XPH/XPL/XPU,
# one sub-test each with the other four checked off. D1 vs D3 is the
# discriminating pair for fpAdd's `sum != 0` forced-zero guard --
# removing it halts D1 at 014304.40. Both passed as the model stood.
run "FP M+MG unchanged registers (jb_af1c F206C, encoding)" python3 verify_fp_arith_f206c_listing.py
run "FP M+MG unchanged registers (jb_af1c F206C on the model)" ./run_program.sh ../decks/fp_arith_f206c.strap StretchFpMgMemCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f206c.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP M+MG indicators (jb_af1c F206D, encoding)" python3 verify_fp_arith_f206d_listing.py
run "FP M+MG indicators (jb_af1c F206D on the model)" ./run_program.sh ../decks/fp_arith_f206d.strap StretchFpMgMemDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f206d.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- 1m. jb_af1c F207A (p.89): LOAD DOUBLE, the first double-precision
# instruction -- DL is LOAD plus "accumulator bits 60-107 are set to
# zero" (Ref. Manual p.96), the low half of the 96-bit double fraction.
# Five sub-tests, each checking bits 0-59 against the operand and bits
# 60-107 against zero, with the right half pre-filled with ones first
# so the second check bites: making DL leave the right half alone halts
# at 014461.00. A3-A5 also cover the normalization modifier over the
# XFP, XFN and N ranges.
run "FP load double (jb_af1c F207A, encoding)" python3 verify_fp_arith_f207a_listing.py
run "FP load double (jb_af1c F207A on the model)" ./run_program.sh ../decks/fp_arith_f207a.strap StretchFpLoadDblATb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f207a.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- 1m'. jb_af1c F207B (p.90) and F207C/F207D (p.90): the rest of
# LOAD DOUBLE. B, that bits 108-127 survive a DL (ones stay ones, zeros
# stay zeros -- the twenty bits below the double fraction). C, that the
# sign byte's flag bits 5-7 are zeroed. D, that the data flag
# indicators follow the ADDRESSED operand's flags. C1 caught the E-box
# register interlock below.
run "FP load double unchanged registers (jb_af1c F207B, encoding)" python3 verify_fp_arith_f207b_listing.py
run "FP load double unchanged registers (jb_af1c F207B on the model)" ./run_program.sh ../decks/fp_arith_f207b.strap StretchFpLoadDblBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f207b.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP load double flags and indicators (jb_af1c F207C/D, encoding)" python3 verify_fp_arith_f207cd_listing.py
run "FP load double flags and indicators (jb_af1c F207C/D on the model)" ./run_program.sh ../decks/fp_arith_f207cd.strap StretchFpLoadDblCDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f207cd.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- 1j'. E-box-register-close-to-fetch: an E-box instruction writes one
# of words 7-15 and the very next instruction addresses that word as a
# storage operand. The sibling of store-close-to-fetch below, for the
# registers storeTarget() deliberately does not report. Found by
# jb_af1c F207C1; this exact pair read the stale sign byte before the
# fix.
run "Look-ahead: E-box-register-close-to-fetch" ./run_program.sh ../decks/ebox_register_close_to_fetch.strap StretchEboxRegScfTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/ebox_register_close_to_fetch.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- 1m''. jb_af1c F207E (p.92): LOAD DOUBLE WITH FLAG, the one thing
# DLWF does that DL does not -- the addressed operand's flag bits reach
# the sign byte's positions 5-7 and the TF/UF/VF indicators, where DL
# zeroes the sign byte's copy. E1 loads flags of zero over ones, E2
# flags of ones over zeros (FK0 is zero everywhere but its flags, so
# the arithmetic checks all pass and only the flags can fail). Making
# DLWF zero the flags like DL halts at 014602.40. This is also the
# block that puts a real DLWF encoding under the listing oracle.
run "FP load double with flag (jb_af1c F207E, encoding)" python3 verify_fp_arith_f207e_listing.py
run "FP load double with flag (jb_af1c F207E on the model)" ./run_program.sh ../decks/fp_arith_f207e.strap StretchFpLoadDblETb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f207e.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- 1n. jb_af1c F208A1-A20 (pp.93-96): ADD DOUBLE, the first
# double-precision ARITHMETIC. A1-A9 unflagged, each building a genuine
# 96-bit fraction in the accumulator (DL for bits 0-59, a C0011 of
# another constant's fraction into offset 20 for 60-107) and adding a
# storage operand the machine extends with 48 zeros, then checking the
# low order fraction, the high order fraction, the exponent and --
# where a carry leaves the top -- BZLC. A10-A14 take the operands into
# the XFP/XFN ranges, where the result is one operand whole and the
# question is whether its low half comes with it. Two injections, two
# halts: D+ reading only the high 48 bits halts at 014617.40 (A1); the
# flagged path dropping the survivor's low half halts at 014732.00
# (A10) with A1-A9 still passing. A15-A19 are the normalization
# modifier: A15-A18 keep a flagged survivor so normalization is
# suppressed, and A19 is the first double-precision result the model
# actually normalizes -- normalizing only its high 48 bits halts at
# 015014.00. A20 closes the routine and is the only sub-test whose
# result exponent is checked on its own -- 12 bits at accumulator
# offset 116 (IBM 0-11) rather than folded into a 60-bit check -- and
# the only one that normalizes on the unflagged path, so dropping the
# normalization exponent adjustment there halts at A20 alone.
run "FP add double (jb_af1c F208A1-A20, encoding)" python3 verify_fp_arith_f208a_listing.py
run "FP add double (jb_af1c F208A1-A20 on the model)" ./run_program.sh ../decks/fp_arith_f208a.strap StretchFpAddDblATb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f208a.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# jb_af1c F208B (pp.96-98): ADD DOUBLE's seven sign-and-modifier
# combinations -- D+, D+A, D-, D-A against both accumulator signs, each
# checked on both fraction halves and then on the sign bit itself with
# BB/BZB. The first block in double precision that SUBTRACTS: every
# operand F208A adds is positive on the unflagged path, so replacing
# the unlike-signs magnitude subtraction with an addition leaves the
# whole of F208A green and halts at B3's low order check (015055.40),
# as does making D+ read the raw operand sign instead of the
# modifier-applied one. Needed D-/D-A rules in strap_asm.py; the model
# needed nothing.
run "FP add double signs (jb_af1c F208B1-B7, encoding)" python3 verify_fp_arith_f208b_listing.py
run "FP add double signs (jb_af1c F208B1-B7 on the model)" ./run_program.sh ../decks/fp_arith_f208b.strap StretchFpAddDblBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f208b.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# jb_af1c F208C (p.98): "TEST UNCHANGED REGISTERS" -- what D+ must
# leave alone, namely accumulator right bits 44-63 (IBM 108-127,
# outside the 96-bit fraction) and sign byte bits 5-7, the data flags.
# C2 caught a real bug: it sets the whole sign byte to ones with
# CM1111 and adds FPK0, whose own flags are 000, and an all-ones
# accumulator has EF=1 so the add takes the FLAGGED path, which
# returns the storage operand WHOLE. The model wrote that operand's
# flags into the sign byte; p.86 says bits 5-7 remain unchanged.
# Reverting the fix halts on C2's flag check: SIC stores 015143.00,
# the half-word after the BRGZ at 015142.40 that guards the
# CT1100(BU,3) at 015141.00.
run "FP add double unchanged regs (jb_af1c F208C1-C2, encoding)" python3 verify_fp_arith_f208c_listing.py
run "FP add double unchanged regs (jb_af1c F208C1-C2 on the model)" ./run_program.sh ../decks/fp_arith_f208c.strap StretchFpAddDblCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f208c.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# jb_af1c F208D1-D6 (pp.98-99): ADD DOUBLE's Lost Carry and Lost
# Significance indicators. D1 against D2 is one modifier apart -- the
# same addition unnormalized then normalized -- and D3 against D4 is
# p.96's "at least one operand is non-zero" clause. D5 caught a real
# bug: LS was testing the 97-bit intermediate sum, but an unnormalized
# add can carry out of the top with all 96 low bits zero, and what
# lands in the accumulator is then 96 zeros. Reverting the fix halts
# at D5's BZLS (SIC stores 015164.40). D6 is the one sub-test that
# says anything about the flagged path's indicators: a flagged result
# with a zero fraction must still leave LS off.
run "FP add double indicators (jb_af1c F208D1-D6, encoding)" python3 verify_fp_arith_f208d1_6_listing.py
run "FP add double indicators (jb_af1c F208D1-D6 on the model)" ./run_program.sh ../decks/fp_arith_f208d1_6.strap StretchFpAddDblDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f208d1_6.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# jb_af1c F208D7-D11 (pp.99-100): the exponent-range half of the same
# routine -- one sub-test per indicator (XPFP, XPO, XPH, XPL, XPU),
# each asserting its own is on and the others off. This is the ONLY
# place in the suite that checks D+'s range indicators at all: making
# D+ never report a propagated exponent flag leaves F208A, F208B,
# F208C and F208D1-D6 all green and halts at D7's XPFP check (SIC
# stores 015173.00). The "off" lists are not uniform -- D7 checks five
# including ZM at 11.33, D8-D11 only four -- and are transcribed as
# printed.
run "FP add double exp range (jb_af1c F208D7-D11, encoding)" python3 verify_fp_arith_f208d7_11_listing.py
run "FP add double exp range (jb_af1c F208D7-D11 on the model)" ./run_program.sh ../decks/fp_arith_f208d7_11.strap StretchFpAddDblETb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f208d7_11.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# jb_af1c F209A (pp.101-102): ADD DOUBLE TO MAGNITUDE, nine arithmetic
# checks -- the first exercise of D+MG. It proves the instruction is
# decoded and that it computes what D+ computes, but NOT its
# magnitude-specific rules: every operand in all nine sub-tests is
# positive, so no sum is ever negative and the forced zero is never
# reached. Disabling every addMag rule in fpAddDouble and the sign
# restore in the D+MG arm leaves this program passing. F209B, with its
# DLN accumulators and D-MG/D-MGA operands, is what will cover them.
run "FP add double magnitude (jb_af1c F209A1-A9, encoding)" python3 verify_fp_arith_f209a_listing.py
run "FP add double magnitude (jb_af1c F209A1-A9 on the model)" ./run_program.sh ../decks/fp_arith_f209a.strap StretchFpAddDblMgATb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f209a.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# jb_af1c F209B1-B8 (pp.102-104): D+MG's sign and modifier
# combinations -- D+MG, D+MGA, D-MG, D-MGA against both accumulator
# signs. This is the block F209A could not be: two of D+MG's four
# magnitude rules are covered, both by B5, the first sub-test with a
# DLN accumulator. Not forcing the accumulator sign positive halts at
# B5's low order check (015433.40); not restoring the accumulator's
# own sign afterward halts at B5's sign bit check (015437.40).
# Still NOT covered: either forced-zero arm. Disabling both leaves all
# eight passing -- every sub-test checks a non-zero result, so no sum
# comes out negative. B9-B13 are the next place to look.
run "FP add double magnitude signs (jb_af1c F209B1-B8, encoding)" python3 verify_fp_arith_f209b1_8_listing.py
run "FP add double magnitude signs (jb_af1c F209B1-B8 on the model)" ./run_program.sh ../decks/fp_arith_f209b1_8.strap StretchFpAddDblMgBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f209b1_8.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# jb_af1c F209B9-B13 (pp.104-105): the same sweep with the MEMORY
# operand negative (FPK40, and FK119 which holds identical bits).
# Also does not reach the forced zero, and now the reason is clear:
# throughout F209B the accumulator sits at exponent +50 and the
# operand at +2, so the accumulator dominates by 48 places and no sum
# can come out negative. The forced zero has its own routine, F209E
# "TEST FORCED ZERO RESULT" (p.107), whose E1 adds two constants at
# the SAME exponent. PASS here is at 015543.00, where B14 begins --
# F209B runs to B16, not transcribed.
run "FP add double magnitude signs 2 (jb_af1c F209B9-B13, encoding)" python3 verify_fp_arith_f209b9_13_listing.py
run "FP add double magnitude signs 2 (jb_af1c F209B9-B13 on the model)" ./run_program.sh ../decks/fp_arith_f209b9_13.strap StretchFpAddDblMgCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f209b9_13.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# jb_af1c F209B14-B16 (p.105): the last three, with BOTH signs
# negative -- DLN accumulator and FPK40 operand -- closing F209B's
# grid. With these the routine is transcribed end to end, 015365.40
# to 015574.40 across three programs, each ending where the next
# begins. Still no forced zero anywhere in F209B.
run "FP add double magnitude signs 3 (jb_af1c F209B14-B16, encoding)" python3 verify_fp_arith_f209b14_16_listing.py
run "FP add double magnitude signs 3 (jb_af1c F209B14-B16 on the model)" ./run_program.sh ../decks/fp_arith_f209b14_16.strap StretchFpAddDblMgDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f209b14_16.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# jb_af1c F209C (pp.105-106): "UNCHANGED REGISTERS" for D+MG. Unlike
# F208C, which checked only sign byte bits 5-7 with a 3-bit field at
# 10.5, this checks all EIGHT bits at 10.0 -- so C2 covers the sign
# (bit 4) as well as the flags. Two injections halt on it (SIC stores
# 015614.40): not restoring the accumulator's own sign, and taking the
# sign byte's flags from the result instead of from accS.
run "FP add double magnitude unchanged regs (jb_af1c F209C1-C2, encoding)" python3 verify_fp_arith_f209c_listing.py
run "FP add double magnitude unchanged regs (jb_af1c F209C1-C2 on the model)" ./run_program.sh ../decks/fp_arith_f209c.strap StretchFpAddDblMgETb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f209c.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# jb_af1c F209D1-D5 (pp.106-107): D+MG's arithmetic result indicators
# RLZ, RZ, RGZ and RN. D1 and D2 load the accumulator NEGATIVE with
# DLN, and D+MG assumes it positive for the addition -- so the sign
# has to be restored before the INDICATORS are set, not merely before
# the sign byte is written. Restoring it only at the byte write leaves
# F209C passing and halts at D1's BZRLZ (SIC stores 015620.00).
run "FP add double magnitude indicators (jb_af1c F209D1-D5, encoding)" python3 verify_fp_arith_f209d1_5_listing.py
run "FP add double magnitude indicators (jb_af1c F209D1-D5 on the model)" ./run_program.sh ../decks/fp_arith_f209d1_5.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f209d1_5.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# F209D6-D9, the Lost Significance half of the same routine. D7 (zero
# plus zero must NOT set LS) is the printed source of the exception
# clause in the F208D5 LS fix; D9 is the first LS question put to the
# flagged path, where fpAddDouble returns a survivor whole.
run "FP add double magnitude LS indicator (jb_af1c F209D6-D9, encoding)" python3 verify_fp_arith_f209d6_9_listing.py
run "FP add double magnitude LS indicator (jb_af1c F209D6-D9 on the model)" ./run_program.sh ../decks/fp_arith_f209d6_9.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f209d6_9.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# F209E1-E4 "TEST FORCED ZERO RESULT". The first block anywhere in
# jb_af1c that reaches fpAddDouble's UNFLAGGED forced zero: FPK37 and
# FPK38 share exponent 0031 with |FPK37| > |FPK38|, so subtracting
# FPK37 from the accumulator's magnitude gives a negative sum. Turning
# the forced-zero guard off halts E1 (SIC stores 015677.00) and leaves
# F209A/C/D green, so nothing else in the suite covers it. It pins the
# result fraction and the sign but NOT the exponent -- both CT0110s
# cover IBM 12-107 only.
run "FP add double magnitude forced zero (jb_af1c F209E1-E4, encoding)" python3 verify_fp_arith_f209e1_4_listing.py
run "FP add double magnitude forced zero (jb_af1c F209E1-E4 on the model)" ./run_program.sh ../decks/fp_arith_f209e1_4.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f209e1_4.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# F209E5-E8 reach the same forced zero from the other side: FPK43 is
# FPK37 with its sign bit set, so D+MG adds a NEGATIVE operand of
# larger magnitude instead of subtracting a positive one. E6 and E8 use
# D-MGA, whose A-then-minus double inversion lands on the same
# arithmetic by a different route through strip_fp_sign.
run "FP add double magnitude forced zero (jb_af1c F209E5-E8, encoding)" python3 verify_fp_arith_f209e5_8_listing.py
run "FP add double magnitude forced zero (jb_af1c F209E5-E8 on the model)" ./run_program.sh ../decks/fp_arith_f209e5_8.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f209e5_8.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# F209E9 closes F209 out. Six rows: clear LS with BLSZ, run E8's
# arithmetic (which the listing itself annotates "FORCED ZERO RESULT"),
# ask once that LS came out OFF. It is the suite's only oracle for the
# !forcedZero term in r.ls = (res.frac == 0) && !(a.frac == 0 &&
# b.frac == 0) && !forcedZero -- F208D5 forced the res.frac term and
# F209D7 the both-zero term, but a forced zero HAS a zero result
# fraction, so without that term LS would come on and nothing until now
# both produced a forced zero and asked about LS.
run "FP add double magnitude forced zero, LS off (jb_af1c F209E9, encoding)" python3 verify_fp_arith_f209e9_listing.py
run "FP add double magnitude forced zero, LS off (jb_af1c F209E9 on the model)" ./run_program.sh ../decks/fp_arith_f209e9.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f209e9.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- F210 STORE ROUNDED. A1-A2 are the diagnostic that drove writing
# SRD's execute arm (it decoded but set OP-invalid before this). Both
# are the flagged case: a 96-bit all-ones accumulator fraction, so the
# +1 at IBM 60 carries the whole way out, the overflow is lost and the
# exponent is unchanged -- expecting FK35 (XFP) and FPK59 (XFN) with a
# ZERO fraction, plus a BZB on the stored sign bit.
run "FP store rounded (jb_af1c F210A1-A2, encoding)" python3 verify_fp_arith_f210a1_2_listing.py
run "FP store rounded (jb_af1c F210A1-A2 on the model)" ./run_program.sh ../decks/fp_arith_f210a1_2.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f210a1_2.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# F210A3-A4, the UNFLAGGED (N range) case A1-A2 never reach, and the
# complement of their coverage. Injecting the rounding one place LOW
# (IBM 59, inside the kept fraction) halts A3 at 016020.40 while A1-A2
# stays green. Neither block sees a rounding placed one place HIGH
# (IBM 61): A3's fraction is zero so nothing carries either way, and
# A4's low half is all ones so everything does. Together they pin the
# BOUNDARY -- the rounding one lands in the discarded half -- not the
# exact bit.
run "FP store rounded, N range (jb_af1c F210A3-A4, encoding)" python3 verify_fp_arith_f210a3_4_listing.py
run "FP store rounded, N range (jb_af1c F210A3-A4 on the model)" ./run_program.sh ../decks/fp_arith_f210a3_4.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f210a3_4.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# F210A5 closes F210A "ARITHMETIC CHECKS". It is the unflagged
# analogue of A1: a 96-bit all-ones fraction in the N range at exponent
# +2, so the rounding overflows out of the kept 48 bits -- and the
# expected result FPK67 still has exponent +2. That is the unnormalized
# rule, "the overflow bit does not enter storage but sets LC", and A5
# is the only sub-test where it meets an exponent that would move if
# the carry were absorbed the way a normalized operation absorbs it.
# A1/A2 are flagged (exponent left alone by a different rule) and
# A3/A4 never overflow out of the kept 48.
run "FP store rounded, unnormalized overflow (jb_af1c F210A5, encoding)" python3 verify_fp_arith_f210a5_listing.py
run "FP store rounded, unnormalized overflow (jb_af1c F210A5 on the model)" ./run_program.sh ../decks/fp_arith_f210a5.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f210a5.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# F210A6-A7, the routine's "TEST NORMALIZATION MODIFIER" section and
# the first SRD(N) in the diagnostic -- every sub-test through A5 is
# SRD(U), so the model's normalized path had never run. In the XFP and
# XFN ranges "normalization, if specified, is suppressed", and the
# expected results FK109/FK110 are still unnormalized, which is what
# makes these the oracle for that clause. Honouring the modifier for
# flagged operands halts A6 at 016047.00 with A1-A5 green: A1/A2 are
# flagged too but round to a ZERO fraction, and normalizing zero shifts
# nothing.
run "FP store rounded, normalization suppressed (jb_af1c F210A6-A7, encoding)" python3 verify_fp_arith_f210a6_7_listing.py
run "FP store rounded, normalization suppressed (jb_af1c F210A6-A7 on the model)" ./run_program.sh ../decks/fp_arith_f210a6_7.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f210a6_7.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# F210A8 "TEST NORMALIZATION PROCESS" closes F210A, and is the one
# sub-test in the routine where SRD actually normalizes: FK47
# (exponent +50, fraction 000fffffffff) with FK22's all-ones low half
# rounds to 001000000000, which shifts ELEVEN places left to
# 800000000000 and takes the exponent to +39 -- exactly FK52. Forcing
# the unflagged path never to normalize halts it at 016062.00 with
# A1-A7 green; A6/A7 survive because they are flagged, where the
# normalization was already suppressed.
run "FP store rounded, normalization process (jb_af1c F210A8, encoding)" python3 verify_fp_arith_f210a8_listing.py
run "FP store rounded, normalization process (jb_af1c F210A8 on the model)" ./run_program.sh ../decks/fp_arith_f210a8.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f210a8.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# F210B "TEST UNCHANGED REGISTERS" is the oracle for one sentence of
# p.96: "the entire accumulator and its sign byte register remain
# unchanged throughout the operation". Nothing in F210A checks it --
# every sub-test there reads ROS, never the accumulator -- and the
# model satisfies it only by not writing them. B1 sets all three to
# zero and B2 to ones, each running one SRD(U) and then asking three
# separate questions (L0-63, R0-63, SB0-7). B2 is the stronger: an
# all-ones accumulator has EF=1 so the flagged path runs, and the sign
# byte's sign and all three flag bits are set.
run "FP store rounded, unchanged registers (jb_af1c F210B, encoding)" python3 verify_fp_arith_f210b_listing.py
run "FP store rounded, unchanged registers (jb_af1c F210B on the model)" ./run_program.sh ../decks/fp_arith_f210b.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f210b.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# F210C "ACCUMULATOR FLAGS TO MEMORY FLAGS" guards the other half of
# p.96's storage-word sentence: the accumulator flag bits go to storage
# bits 61-63. F210A checked bit 60 (the sign) with its BZB questions
# and nothing had looked at 61-63. C1 pre-loads ROS with ONES before
# zeroing the accumulator, which makes it a test of copying rather than
# of leaving alone.
run "FP store rounded, flags to memory (jb_af1c F210C, encoding)" python3 verify_fp_arith_f210c_listing.py
run "FP store rounded, flags to memory (jb_af1c F210C on the model)" ./run_program.sh ../decks/fp_arith_f210c.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f210c.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# F210D "TESTS OF INDICATORS" closes F210 out, and D2 is the LOST CARRY
# oracle recorded as missing since A5. Every block from A1 to C2 checked
# what SRD STORED and never asked about an indicator. D1 asks that MOP
# comes on; D2 clears LC, runs the same 96-ones operand A5 uses, and
# asks that the rounding overflow set LC. A5 and D2 are the two halves
# of one rule -- what the overflow did to the word, and to the
# indicator -- and the model takes both from the same lostCarry.
run "FP store rounded, MOP and LC indicators (jb_af1c F210D, encoding)" python3 verify_fp_arith_f210d_listing.py
run "FP store rounded, MOP and LC indicators (jb_af1c F210D on the model)" ./run_program.sh ../decks/fp_arith_f210d.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f210d.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- F211 STORE LOW ORDER. A1-A2 are the diagnostic that drove SLO's
# execute arm, the second instruction this series has implemented from
# its own test. Both are the flagged case, where the accumulator's
# exponent is kept and normalization suppressed, so neither exercises
# the headline rule -- the stored exponent is the accumulator's MINUS
# 48 -- which waits for F211A3. SLO needs its own fpNormalize48 because
# noisy mode enters ONES from the right here, where SRD's normalization
# is explicitly unaffected by it.
run "FP store low order (jb_af1c F211A1-A2, encoding)" python3 verify_fp_arith_f211a1_2_listing.py
run "FP store low order (jb_af1c F211A1-A2 on the model)" ./run_program.sh ../decks/fp_arith_f211a1_2.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f211a1_2.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# F211A3-A4 are the first UNFLAGGED SLO, and so the first exercise of
# its headline rule: the stored exponent is the accumulator's MINUS 48.
# A1-A2 are both flagged, where the exponent is kept unchanged, so
# neither can see the subtraction. A3 stores FPK28's fraction at
# 256-48=208 (FPK44) and A4 stores FPK38's at 50-48=2 (FPK39); the
# listing's own comments say "EXP+208" and "EXPONENT++2".
run "FP store low order, exponent minus 48 (jb_af1c F211A3-A4, encoding)" python3 verify_fp_arith_f211a3_4_listing.py
run "FP store low order, exponent minus 48 (jb_af1c F211A3-A4 on the model)" ./run_program.sh ../decks/fp_arith_f211a3_4.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f211a3_4.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# F211A7-A10, the routine's "TEST NORMALIZATION MODIFIER" section and
# the first SLO(N) anywhere -- A1-A6 are all SLO(U). A7/A8 check that a
# FLAGGED accumulator exponent suppresses the shift (FK26 and FK30 are
# still unnormalized). A9 is the real normalization: FPK53's fraction
# has 46 leading zeros, so +50 goes through -48 to +2 and then 46
# places left to -44 (FK51). A10 drives the exponent out of range to
# -1073 and expects FK112, whose exponent field is -49 = 1073 - 1024.
#
# A10 CAUGHT A REAL BUG in fpMakeExp, which is shared by fpAdd,
# fpAddDouble, SRD and SLO: it wrote em = 0 on a generated flag, where
# the machine keeps the low ten bits of the magnitude and uses EF only
# to mark the overflow. Nothing else in the suite pins that -- A9
# normalizes too but stays in range.
run "FP store low order, normalization modifier (jb_af1c F211A7-A10, encoding)" python3 verify_fp_arith_f211a7_10_listing.py
run "FP store low order, normalization modifier (jb_af1c F211A7-A10 on the model)" ./run_program.sh ../decks/fp_arith_f211a7_10.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f211a7_10.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# F211B-C close F211 out. B1 is the SLO analogue of F210B: all three
# registers set to ones, one SLO(U), then three questions that none of
# them moved. C is the interesting one by OMISSION -- its whole
# indicator test is BMOPZ/BZMOP, and there is no LC question anywhere
# in F211 where F210D2 had one for SRD. That matches p.97, which lists
# no LOST CARRY among SLO's indicators because a shift has no carry to
# lose; the model was written that way from the page, and the listing
# agrees by leaving the question out.
run "FP store low order, unchanged registers and MOP (jb_af1c F211B-C, encoding)" python3 verify_fp_arith_f211bc_listing.py
run "FP store low order, unchanged registers and MOP (jb_af1c F211B-C on the model)" ./run_program.sh ../decks/fp_arith_f211bc.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f211bc.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- F212 SHIFT FRACTION. The first block to exercise SHF as the 96-BIT
# -- operation Reference Manual p.102 describes ("only accumulator bits
# -- 12-107 participate"); the arm shifted only the 48-bit high half
# -- before this. A1-A11 cannot see that (DL zeroes the low half and
# -- they shift LEFT); A12 can, and does -- see that program's header.
run "FP shift fraction, left-shift walk (jb_af1c F212A1-A11, encoding)" python3 verify_fp_arith_f212a1_11_listing.py
run "FP shift fraction, left-shift walk (jb_af1c F212A1-A11 on the model)" ./run_program.sh ../decks/fp_arith_f212a1_11.strap StretchFpShfATb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f212a1_11.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"
run "FP shift fraction, 96-bit lost carry and right-shift walk (jb_af1c F212A12-A23, encoding)" python3 verify_fp_arith_f212a12_23_listing.py
run "FP shift fraction, 96-bit lost carry and right-shift walk (jb_af1c F212A12-A23 on the model)" ./run_program.sh ../decks/fp_arith_f212a12_23.strap StretchFpShfBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f212a12_23.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"
run "FP shift fraction, LC off / self-modifying / norm-mod / flagged (jb_af1c F212A24-A30, encoding)" python3 verify_fp_arith_f212a24_30_listing.py
run "FP shift fraction, LC off / self-modifying / norm-mod / flagged (jb_af1c F212A24-A30 on the model)" ./run_program.sh ../decks/fp_arith_f212a24_30.strap StretchFpShfCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f212a24_30.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- Program store compare with an OBSERVABLE difference. F212A25 above
# -- is the diagnostic's own store-then-execute row, but it patches
# -- bits the shift ignores, so stale and fresh are both no-ops there:
# -- it proves the machine does not hang, not that the re-fetch saw the
# -- new word. This one makes the two outcomes different.
run "FP shift fraction, sign/modifier combinations (jb_af1c F212B, encoding)" python3 verify_fp_arith_f212b_listing.py
run "FP shift fraction, sign/modifier combinations (jb_af1c F212B on the model)" ./run_program.sh ../decks/fp_arith_f212b.strap StretchFpShfDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f212b.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"
run "FP shift fraction, unchanged registers (jb_af1c F212C, encoding)" python3 verify_fp_arith_f212c_listing.py
run "FP shift fraction, unchanged registers (jb_af1c F212C on the model)" ./run_program.sh ../decks/fp_arith_f212c.strap StretchFpShfETb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f212c.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"
run "FP shift fraction, indicator tests (jb_af1c F212D, encoding)" python3 verify_fp_arith_f212d_listing.py
run "FP shift fraction, indicator tests (jb_af1c F212D on the model)" ./run_program.sh ../decks/fp_arith_f212d.strap StretchFpShfFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f212d.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP add to fraction (jb_af1c F212XA, encoding)" python3 verify_fp_arith_f212xa_listing.py
run "FP add to fraction (jb_af1c F212XA on the model)" ./run_program.sh ../decks/fp_arith_f212xa.strap StretchFpAddFracTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f212xa.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP add to fraction, sign and modifiers (jb_af1c F212XB, encoding)" python3 verify_fp_arith_f212xb_listing.py
run "FP add to fraction, sign and modifiers (jb_af1c F212XB on the model)" ./run_program.sh ../decks/fp_arith_f212xb.strap StretchFpAddFracBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f212xb.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP add to fraction, unchanged regs (jb_af1c F212XC, encoding)" python3 verify_fp_arith_f212xc_listing.py
run "FP add to fraction, unchanged regs (jb_af1c F212XC on the model)" ./run_program.sh ../decks/fp_arith_f212xc.strap StretchFpAddFracCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f212xc.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP add to exponent, range table (jb_af1c F213A1-A9, encoding)" python3 verify_fp_arith_f213a1_9_listing.py
run "FP add to exponent, range table (jb_af1c F213A1-A9 on the model)" ./run_program.sh ../decks/fp_arith_f213a1_9.strap StretchFpAddExpTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f213a1_9.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP add to exponent, normalization (jb_af1c F213A10-A13, encoding)" python3 verify_fp_arith_f213a10_13_listing.py
run "FP add to exponent, normalization (jb_af1c F213A10-A13 on the model)" ./run_program.sh ../decks/fp_arith_f213a10_13.strap StretchFpAddExpNTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f213a10_13.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP add to exponent, sign modifiers (jb_af1c F213B, encoding)" python3 verify_fp_arith_f213b_listing.py
run "FP add to exponent, sign modifiers (jb_af1c F213B on the model)" ./run_program.sh ../decks/fp_arith_f213b.strap StretchFpAddExpBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f213b.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP add to exponent, unchanged regs (jb_af1c F213C, encoding)" python3 verify_fp_arith_f213c_listing.py
run "FP add to exponent, unchanged regs (jb_af1c F213C on the model)" ./run_program.sh ../decks/fp_arith_f213c.strap StretchFpAddExpCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f213c.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP add to exponent, result indicators (jb_af1c F213D1-D4, encoding)" python3 verify_fp_arith_f213d1_4_listing.py
run "FP add to exponent, result indicators (jb_af1c F213D1-D4 on the model)" ./run_program.sh ../decks/fp_arith_f213d1_4.strap StretchFpAddExpDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f213d1_4.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP add to exponent, range indicators (jb_af1c F213D5-D9, encoding)" python3 verify_fp_arith_f213d5_9_listing.py
run "FP add to exponent, range indicators (jb_af1c F213D5-D9 on the model)" ./run_program.sh ../decks/fp_arith_f213d5_9.strap StretchFpAddExpETb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f213d5_9.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP add immediate to exponent (jb_af1c F213XA, encoding)" python3 verify_fp_arith_f213xa_listing.py
run "FP add immediate to exponent (jb_af1c F213XA on the model)" ./run_program.sh ../decks/fp_arith_f213xa.strap StretchFpAddExpImmTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f213xa.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP add immediate, sign and mod combs (jb_af1c F213XB, encoding)" python3 verify_fp_arith_f213xb_listing.py
run "FP add immediate, sign and mod combs (jb_af1c F213XB on the model)" ./run_program.sh ../decks/fp_arith_f213xb.strap StretchFpAddExpImmBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f213xb.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP add immediate, unchanged regs (jb_af1c F213XC, encoding)" python3 verify_fp_arith_f213xc_listing.py
run "FP add immediate, unchanged regs (jb_af1c F213XC on the model)" ./run_program.sh ../decks/fp_arith_f213xc.strap StretchFpAddExpImmCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f213xc.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP multiply arithmetic checks (jb_af1c F214A, encoding)" python3 verify_fp_arith_f214a_listing.py
run "FP multiply arithmetic checks (jb_af1c F214A on the model)" ./run_program.sh ../decks/fp_arith_f214a.strap StretchFpMulTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f214a.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP multiply sign and modifiers (jb_af1c F214B, encoding)" python3 verify_fp_arith_f214b_listing.py
run "FP multiply sign and modifiers (jb_af1c F214B on the model)" ./run_program.sh ../decks/fp_arith_f214b.strap StretchFpMulBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f214b.strap").read()).symtab["POR5"]//32)')" \
    "SEN:712=0"

run "FP multiply unchanged regs (jb_af1c F214C, encoding)" python3 verify_fp_arith_f214c_listing.py
run "FP multiply unchanged regs (jb_af1c F214C on the model)" ./run_program.sh ../decks/fp_arith_f214c.strap StretchFpMulCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f214c.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP multiply indicator tests (jb_af1c F214D, encoding)" python3 verify_fp_arith_f214d_listing.py
run "FP multiply indicator tests (jb_af1c F214D on the model)" ./run_program.sh ../decks/fp_arith_f214d.strap StretchFpMulDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f214d.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP multiply double arithmetic (jb_af1c F214XA, encoding)" python3 verify_fp_arith_f214xa_listing.py
run "FP multiply double arithmetic (jb_af1c F214XA on the model)" ./run_program.sh ../decks/fp_arith_f214xa.strap StretchFpMulDblATb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f214xa.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP multiply double unchanged regs (jb_af1c F214XB, encoding)" python3 verify_fp_arith_f214xb_listing.py
run "FP multiply double unchanged regs (jb_af1c F214XB on the model)" ./run_program.sh ../decks/fp_arith_f214xb.strap StretchFpMulDblBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f214xb.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP load factor arithmetic (jb_af1c F215A, encoding)" python3 verify_fp_arith_f215a_listing.py
run "FP load factor arithmetic (jb_af1c F215A on the model)" ./run_program.sh ../decks/fp_arith_f215a.strap StretchFpLftATb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f215a.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP load factor sign and modifiers (jb_af1c F215B, encoding)" python3 verify_fp_arith_f215b_listing.py
run "FP load factor sign and modifiers (jb_af1c F215B on the model)" ./run_program.sh ../decks/fp_arith_f215b.strap StretchFpLftBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f215b.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP load factor changed regs (jb_af1c F215C, encoding)" python3 verify_fp_arith_f215c_listing.py
run "FP load factor changed regs (jb_af1c F215C on the model)" ./run_program.sh ../decks/fp_arith_f215c.strap StretchFpLftCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f215c.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP load factor unchanged regs (jb_af1c F215D, encoding)" python3 verify_fp_arith_f215d_listing.py
run "FP load factor unchanged regs (jb_af1c F215D on the model)" ./run_program.sh ../decks/fp_arith_f215d.strap StretchFpLftDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f215d.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP load factor result indicators (jb_af1c F215E, encoding)" python3 verify_fp_arith_f215e_listing.py
run "FP load factor result indicators (jb_af1c F215E on the model)" ./run_program.sh ../decks/fp_arith_f215e.strap StretchFpLftETb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f215e.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP load factor normalization modifier (jb_af1c F215F, encoding)" python3 verify_fp_arith_f215f_listing.py
run "FP load factor normalization modifier (jb_af1c F215F on the model)" ./run_program.sh ../decks/fp_arith_f215f.strap StretchFpLftFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f215f.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP multiply and add arithmetic (jb_af1c F216A, encoding)" python3 verify_fp_arith_f216a_listing.py
run "FP multiply and add arithmetic (jb_af1c F216A on the model)" ./run_program.sh ../decks/fp_arith_f216a.strap StretchFpMulAddATb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f216a.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP multiply and add sign and modifiers (jb_af1c F216B, encoding)" python3 verify_fp_arith_f216b_listing.py
run "FP multiply and add sign and modifiers (jb_af1c F216B on the model)" ./run_program.sh ../decks/fp_arith_f216b.strap StretchFpMulAddBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f216b.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP multiply and add unchanged regs (jb_af1c F216C, encoding)" python3 verify_fp_arith_f216c_listing.py
run "FP multiply and add unchanged regs (jb_af1c F216C on the model)" ./run_program.sh ../decks/fp_arith_f216c.strap StretchFpMulAddCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f216c.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP multiply and add indicators (jb_af1c F216D, encoding)" python3 verify_fp_arith_f216d_listing.py
run "FP multiply and add indicators (jb_af1c F216D on the model)" ./run_program.sh ../decks/fp_arith_f216d.strap StretchFpMulAddDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f216d.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP divide arithmetic (jb_af1c F217A, encoding)" python3 verify_fp_arith_f217a_listing.py
run "FP divide arithmetic (jb_af1c F217A on the model)" ./run_program.sh ../decks/fp_arith_f217a.strap StretchFpDivATb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f217a.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP divide sign and modifiers (jb_af1c F217B, encoding)" python3 verify_fp_arith_f217b_listing.py
run "FP divide sign and modifiers (jb_af1c F217B on the model)" ./run_program.sh ../decks/fp_arith_f217b.strap StretchFpDivBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f217b.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP divide unchanged regs (jb_af1c F217C, encoding)" python3 verify_fp_arith_f217c_listing.py
run "FP divide unchanged regs (jb_af1c F217C on the model)" ./run_program.sh ../decks/fp_arith_f217c.strap StretchFpDivCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f217c.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP divide indicators (jb_af1c F217D, encoding)" python3 verify_fp_arith_f217d_listing.py
run "FP divide indicators (jb_af1c F217D on the model)" ./run_program.sh ../decks/fp_arith_f217d.strap StretchFpDivDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f217d.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP divide double arithmetic (jb_af1c F217WA, encoding)" python3 verify_fp_arith_f217wa_listing.py
run "FP divide double arithmetic (jb_af1c F217WA on the model)" ./run_program.sh ../decks/fp_arith_f217wa.strap StretchFpDivDblATb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f217wa.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP divide double sign and modifiers (jb_af1c F217WB, encoding)" python3 verify_fp_arith_f217wb_listing.py
run "FP divide double sign and modifiers (jb_af1c F217WB on the model)" ./run_program.sh ../decks/fp_arith_f217wb.strap StretchFpDivDblBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f217wb.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP divide double changed regs (jb_af1c F217WC, encoding)" python3 verify_fp_arith_f217wc_listing.py
run "FP divide double changed regs (jb_af1c F217WC on the model)" ./run_program.sh ../decks/fp_arith_f217wc.strap StretchFpDivDblCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f217wc.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP divide double unchanged regs (jb_af1c F217WD, encoding)" python3 verify_fp_arith_f217wd_listing.py
run "FP divide double unchanged regs (jb_af1c F217WD on the model)" ./run_program.sh ../decks/fp_arith_f217wd.strap StretchFpDivDblDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f217wd.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP divide double remainder underflow (jb_af1c F217WE, encoding)" python3 verify_fp_arith_f217we_listing.py
run "FP divide double remainder underflow (jb_af1c F217WE on the model)" ./run_program.sh ../decks/fp_arith_f217we.strap StretchFpDivDblETb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f217we.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP reciprocal divide arithmetic (jb_af1c F217XA, encoding)" python3 verify_fp_arith_f217xa_listing.py
run "FP reciprocal divide arithmetic (jb_af1c F217XA on the model)" ./run_program.sh ../decks/fp_arith_f217xa.strap StretchFpRecipDivATb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f217xa.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP reciprocal divide sign and modifiers (jb_af1c F217XB, encoding)" python3 verify_fp_arith_f217xb_listing.py
run "FP reciprocal divide sign and modifiers (jb_af1c F217XB on the model)" ./run_program.sh ../decks/fp_arith_f217xb.strap StretchFpRecipDivBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f217xb.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP reciprocal divide unchanged regs (jb_af1c F217XC, encoding)" python3 verify_fp_arith_f217xc_listing.py
run "FP reciprocal divide unchanged regs (jb_af1c F217XC on the model)" ./run_program.sh ../decks/fp_arith_f217xc.strap StretchFpRecipDivCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f217xc.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP reciprocal divide indicators (jb_af1c F217XD, encoding)" python3 verify_fp_arith_f217xd_listing.py
run "FP reciprocal divide indicators (jb_af1c F217XD on the model)" ./run_program.sh ../decks/fp_arith_f217xd.strap StretchFpRecipDivDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f217xd.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP store root arithmetic (jb_af1c F218A, encoding)" python3 verify_fp_arith_f218a_listing.py
run "FP store root arithmetic (jb_af1c F218A on the model)" ./run_program.sh ../decks/fp_arith_f218a.strap StretchFpSqrtATb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f218a.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP store root sign and modifiers (jb_af1c F218B, encoding)" python3 verify_fp_arith_f218b_listing.py
run "FP store root sign and modifiers (jb_af1c F218B on the model)" ./run_program.sh ../decks/fp_arith_f218b.strap StretchFpSqrtBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f218b.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP store root unchanged regs (jb_af1c F218C, encoding)" python3 verify_fp_arith_f218c_listing.py
run "FP store root unchanged regs (jb_af1c F218C on the model)" ./run_program.sh ../decks/fp_arith_f218c.strap StretchFpSqrtCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f218c.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP store root indicators (jb_af1c F218D, encoding)" python3 verify_fp_arith_f218d_listing.py
run "FP store root indicators (jb_af1c F218D on the model)" ./run_program.sh ../decks/fp_arith_f218d.strap StretchFpSqrtDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f218d.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP noisy mode add/load (jb_af1c F219A-D, encoding)" python3 verify_fp_arith_f219a_listing.py
run "FP noisy mode add/load (jb_af1c F219A-D on the model)" ./run_program.sh ../decks/fp_arith_f219a.strap StretchFpNoisyATb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f219a.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP noisy mode multiply/divide/root (jb_af1c F219K-P2, encoding)" python3 verify_fp_arith_f219b_listing.py
run "FP noisy mode multiply/divide/root (jb_af1c F219K-P2 on the model)" ./run_program.sh ../decks/fp_arith_f219b.strap StretchFpNoisyBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f219b.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP noisy mode add/load double (jb_af1c F219P3-S, encoding)" python3 verify_fp_arith_f219c_listing.py
run "FP noisy mode add/load double (jb_af1c F219P3-S on the model)" ./run_program.sh ../decks/fp_arith_f219c.strap StretchFpNoisyCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f219c.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP noisy mode multiply/divide double (jb_af1c F219T-Y, encoding)" python3 verify_fp_arith_f219d_listing.py
run "FP noisy mode multiply/divide double (jb_af1c F219T-Y on the model)" ./run_program.sh ../decks/fp_arith_f219d.strap StretchFpNoisyDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f219d.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP noisy mode fraction/exponent ops (jb_af1c F219Z-C1A, encoding)" python3 verify_fp_arith_f219e_listing.py
run "FP noisy mode fraction/exponent ops (jb_af1c F219Z-C1A on the model)" ./run_program.sh ../decks/fp_arith_f219e.strap StretchFpNoisyETb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/fp_arith_f219e.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "PAU gates SHF0 loop (jb_af1c, encoding)" python3 verify_pau_shf0_listing.py
# The accumulator checks are NOT optional decoration: measured by
# injection, this block reports no error either when the effective
# address ignores its index register or when the loop runs once
# instead of twice.  ACCL/ACCR are what catch both -- see the
# program's own header.
run "PAU gates SHF0 loop (indexed VFL + CBR+ on the model)" ./run_program.sh ../decks/pau_shf0.strap StretchPauShf0Tb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/pau_shf0.strap").read()).symtab["PASS"]//32)')" \
    "ACCL:8=1501199875790165" "ACCR:9=6148914691236167680"

run "PAU gates SHFR1/SHFR2 (jb_af1c, encoding)" python3 verify_pau_shfr12_listing.py
# ACCL/ACCR again, and for a sharper reason than in SHF0: measured by
# injection, these blocks do NOT catch a wrong index through their own
# branches even though their expected values live in separate tables --
# both sides are indexed by the same register.  See the program header.
run "PAU gates SHFR1/SHFR2 (shift right one and two on the model)" ./run_program.sh ../decks/pau_shfr12.strap StretchPauShfR12Tb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/pau_shfr12.strap").read()).symtab["PASS"]//32)')" \
    "ACCL:8=375299968947541" "ACCR:9=6148914691236167680"

run "PAU gates CHKSSR (jb_af1c, encoding)" python3 verify_pau_chkssr_listing.py
# No ACCL/ACCR here, and that is the point: unlike the shift blocks,
# CHKSSR uses no index register and has a separate error exit per case,
# so it discriminates through its OWN branches -- two square-root
# injections halt it at SERS.
run "PAU gates CHKSSR (store root, one bit walked down the radicand)" ./run_program.sh ../decks/pau_chkssr.strap StretchPauChkSsrTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/pau_chkssr.strap").read()).symtab["PASS"]//32)')"

run "PAU gates CHKSSR multi-bit roots (jb_af1c, encoding)" python3 verify_pau_chkssr2_listing.py
# These four earn their place by a measured margin over the sweep
# above: an injection making the root trial ignore previously accepted
# root bits leaves ALL FOURTEEN single-bit cases passing and halts all
# four of these.  See the program header.
run "PAU gates CHKSSR multi-bit roots (perfect squares with several root bits)" ./run_program.sh ../decks/pau_chkssr2.strap StretchPauChkSsr2Tb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/pau_chkssr2.strap").read()).symtab["PASS"]//32)')"

run "PAU gates SRTE30 (jb_af1c, encoding)" python3 verify_pau_srte30_listing.py
# The block that found the 49-bit radicand bug: a single fraction bit
# at IBM 59 with an ODD exponent, halting if the root comes back zero.
# Its own message is "SHIFT R1-BIT LOST".
run "PAU gates SRTE30 (store root, odd exponent, 49-bit radicand)" ./run_program.sh ../decks/pau_srte30.strap StretchPauSrte30Tb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/pau_srte30.strap").read()).symtab["PASS"]//32)')"

run "IBOX-2 load index control check (jb_ax2a, encoding)" python3 verify_ibox2_load_index_listing.py
# The first block from jb_ax2a; the tape had never been opened.  Nothing
# else in the suite touches $X0, and only one other program uses
# BXCZ/BXVZ.  Two injections -- index register 0 reading back as zero,
# and XVZ derived from the whole index word -- are both caught by the
# block's own branches.
run "IBOX-2 load index control check (LX into \$X0, BXCZ/BXVZ)" ./run_program.sh ../decks/ibox2_load_index.strap StretchIbox2LoadIndexTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/ibox2_load_index.strap").read()).symtab["PASS"]//32)')"

run "IBOX-2 KV and KVI check (jb_ax2a, encoding)" python3 verify_ibox2_kv_kvi_listing.py
# Nothing else in the suite uses KV, KVI, BXL, BXH or BXE.  Reversing
# the index compare's high and low is caught by the block's own
# branches.
run "IBOX-2 KV and KVI check (index compare, all three of XL/XE/XH)" ./run_program.sh ../decks/ibox2_kv_kvi.strap StretchIbox2KvKviTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/ibox2_kv_kvi.strap").read()).symtab["I0210"]//32)')"

run "IBOX-4 progressive index V+ICR / V-I (jb_ax4b, encoding)" python3 verify_ibox4_prog_ix_v_listing.py
# Chosen by measurement: uses KC and the shared progressive-index path,
# both shown unreachable by a combined nine-way injection.  KC comparing
# always HIGH, and progressiveIndex never advancing the value, each halt
# it.  Note the injections must be pointed the RIGHT WAY -- the block
# asserts EQUAL, so "always equal" cannot fail it.
run "IBOX-4 progressive index V+ICR / V-I (KC, SR, progressive value)" ./run_program.sh ../decks/ibox4_prog_ix_v.strap StretchIbox4ProgIxVTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/ibox4_prog_ix_v.strap").read()).symtab["PASS"]//32)')"

run "IBOX-1 C+I chain (ja_ax1a, encoding)" python3 verify_ibox1_cpi_chain_listing.py
# Closes C+I and SC, two of the seven measured gaps.  The block has no
# SERS: each step manufactures the next branch instruction out of the
# count arithmetic, so breaking C+I HANGS the machine (step cap) and
# breaking SC runs it off into zeroed storage (PC=0) -- two of the
# three failure signatures, neither of them a halt at 1416.
run "IBOX-1 C+I chain (self-modifying branch chain, C+I and SC)" ./run_program.sh ../decks/ibox1_cpi_chain.strap StretchIbox1CpiChainTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/ibox1_cpi_chain.strap").read()).symtab["PASS"]//32)')"

run "IBOX-1 C-I chain (ja_ax1a, encoding)" python3 verify_ibox1_cmi_chain_listing.py
# The C+I routine's sibling, immediately after it in the listing, with
# the same self-modifying structure and the opposite sign.  Closes C-I,
# one of the five gaps left after the C+I block.  Its third step
# subtracts MINUS one, so the sequence is -1, -3, +1, -2 and the chain
# runs backwards and then forwards through the same six words.
# MEASURED, and the measurement changed the check: with C-I made a
# no-op the block still REACHES ITS EXIT.  Its chain ends two words
# short of the next test, so a count that never moves sends the first
# link straight to the fall-through instead of hanging -- the one
# failure signature this structure cannot produce.  What does
# discriminate is the block's real output: the four half-words it
# manufactures, whose values the listing's own comments name.  Under
# the no-op injection all four hold 4723.04 (the count that never
# changed) instead of 4722/4717/4720/4716.  "Reaches PASS" is not a
# check for a block whose failure mode is ENDING EARLY.
# The four expected words are DERIVED, not written out: each link must
# end up holding a branch to the next link (modifier 04, the one COM04
# adds) beside the untouched "BD,$" of its own second half (modifier
# 44).  Only those two modifiers are literals -- they are exactly what
# the listing's comments assert.
CMI_CHECKS=$(python3 -c 'from strap_asm import assemble
p = assemble(open("../decks/ibox1_cmi_chain.strap").read())
h = lambda w, f: (w << 14) | (f << 8)
print(" ".join("%s:%d=0x%016x" % (n, p.symtab[n] // 64,
      (h(p.symtab[t] // 64, 0o04) << 32) | h(p.symtab[n] // 64, 0o44))
      for n, t in (("IBP71", "IBP76"), ("IBP76", "IBP73"),
                   ("IBP73", "IBP74"), ("IBP74", "IBP72"))))')
run "IBOX-1 C-I chain (self-modifying branch chain, C-I)" ./run_program.sh ../decks/ibox1_cmi_chain.strap StretchIbox1CmiChainTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/ibox1_cmi_chain.strap").read()).symtab["PASS"]//32)')" \
    $CMI_CHECKS

run "IBOX-1 V+C chain (ja_ax1a, encoding)" python3 verify_ibox1_vpc_chain_listing.py
# V+C, the DIRECT-INDEX "add to value and count", and the fourth of the
# eight confirmed-uncovered index operations to be closed.  Not to be
# confused with V+ (everywhere in the suite), V+I, V+IC or V+ICR: this
# is the half-word direct form, and the listing annotates its two
# effects on consecutive lines -- "ADD TO VALUE A HALF" then "DIMINISH
# COUNT BY ONE".
#
# FOUND BY READING THE TAPE'S OWN ROUTINE LIST.  ja_ax1a pp.3-4 name
# every operation the program covers, one line each, IN PROGRAM ORDER.
# Cross-referencing that order against the blocks already transcribed
# bounded V+C to before p.33, and two low-resolution renders found the
# banner.  That is the third time reading a routine list first has
# paid, and it is the same one-page render that would have prevented
# the wrong "LR is blocked" entry.
#
# It checks itself COMPLETELY, like ibox1_vic_chain and unlike
# ibox1_cmi_chain: IBG44-IBG51 are eight branch-to-self half-words and
# the four tests store over ALL EIGHT -- the value after each V+C into
# one, the count (through ISTOY by SC then LV, which multiplies it by
# 64, then V+ COM04 for the branch opcode) into another -- and every
# one is on the path IBG44 -> IBG47 -> IBG45 -> IBG46 -> IBG48 ->
# IBG51 -> IBG49 -> IBG50 -> IBG52.
#
# Measured, and the signature splits exactly as the block's structure
# predicts: with V+C decrementing the count twice, the two words
# holding only VALUE-path links still pass while all four COUNT-path
# words are wrong and the exit is never reached.
VPC_CHECKS=$(python3 -c 'from strap_asm import assemble
p = assemble(open("../decks/ibox1_vpc_chain.strap").read())
ha = lambda n: p.symtab[n] // 32
bd = lambda n: ((ha(n) >> 1) << 14) | ((ha(n) & 1) << 13) | (0b001 << 10)
chain = (("IBG44", "IBG47"), ("IBG45", "IBG46"), ("IBG46", "IBG48"),
         ("IBG47", "IBG45"), ("IBG48", "IBG51"), ("IBG49", "IBG50"),
         ("IBG50", "IBG52"), ("IBG51", "IBG49"))
words = {}
for link, tgt in chain:
    w, half = ha(link) >> 1, ha(link) & 1
    base = p.words.get(w, 0)
    hi, lo = words.get(w, ((base >> 32) & 0xffffffff, base & 0xffffffff))
    words[w] = (bd(tgt), lo) if half == 0 else (hi, bd(tgt))
print(" ".join("W%o:%d=0x%016x" % (w, w, (words[w][0] << 32) | words[w][1])
               for w in sorted(words)))')
run "IBOX-1 V+C chain (self-modifying branch chain, V+C)" ./run_program.sh ../decks/ibox1_vpc_chain.strap StretchIbox1VpcChainTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/ibox1_vpc_chain.strap").read()).symtab["PASS"]//32)')" \
    $VPC_CHECKS

run "IBOX-4 R refill (jb_ax4b, encoding)" python3 verify_ibox4_refill_listing.py
# R (Refill), routine 1238 test 1's first check -- AND THE BLOCK THAT
# CAUGHT A REAL BUG.  execute()'s arm read `st.readIndex(bm.idx)`, but
# bm.idx is IBM bits 28-31, the register that MODIFIES the address, not
# the operand.  Ref. Manual p.26 says R replaces the word at the
# EFFECTIVE ADDRESS with the word its refill field names, and the
# listing agrees: "R,$X15" assembles to 37.02 00 -- address 037, word
# 31, which IS index register 15 -- with idx = 0.  So the model
# refilled $X0 from $X0 and never touched $X15.
#
# FOUND BY SCREENING, CONFIRMED BY INJECTION, THEN CAUGHT BY THE DECK.
# R and RCZ are implemented and appeared in zero programs; poisoning
# both left 293 sections passing.  I-Box 4's routine list named where
# they are tested ("1238 Checks R and RCZ from all three memories where
# legal").  Transcribed, the block halted at SERS with SEN =
# 005313.00 -- its first check, "REFILLED X15 FROM LOCN 1 INSTEAD OF
# LOCN 20" -- and passes with the arm corrected.  The fix landed WITH
# its test, which is the point: a correction with no test behind it is
# the mistake the SVA width change nearly was.
#
# ONE CHECK PROVES IT with four BIT words (BIT_n = a 64-bit word with
# IBM bit n set) and nothing else, and which FIELD each bit lands in is
# the trick: BIT59 -> REFILL = 020, the seed; BIT13 -> VALUE = 020,
# loaded into $X0 which IS word 020, planting the expected result at
# the refill source in one move; BIT14 and BIT16 -> 010 and 002, decoys
# stored at words 8 and 1.
#
# SCOPE the fix keeps, stated rather than hidden: an index word held
# outside index core storage needs two SEQUENTIAL reads (the word at
# the effective address, then the word its refill names), which is the
# shape V+CR has and this arm does not.  That case is left invalid, and
# the rest of routine 1238 -- which checks "all three memories" -- is
# what should drive it.  RCZ is still driven by nothing.
run "IBOX-4 R refill (effective address, not the index field)" ./run_program.sh ../decks/ibox4_refill.strap StretchIbox4RefillTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/ibox4_refill.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "IBOX-4 RCZ (jb_ax4b, encoding)" python3 verify_ibox4_rcz_listing.py
# RCZ (Refill on Count Zero), routine 1238 test 3's first check, and
# the LAST operation the whole-opcode screen found implemented and
# driven by nothing.  Six half-words: I38K1 is an index word whose
# COUNT IS ZERO and whose refill names I38XW3, so the single RCZ must
# fire; KV compares.  The listing's error text is the specification --
# "RCZ FAILS TO REFILL WHEN CT ZERO".
#
# I38XW3 is deliberately unlike anything else in storage (value
# 123456.76, count 543210, refill 123456) so a refill that happened but
# landed elsewhere cannot compare equal by accident.
#
# WHY ibox4_refill AND NOT THIS BLOCK CAUGHT THE OPERAND BUG, which is
# worth knowing before trusting either: execute() used to read
# `st.readIndex(bm.idx)` where the operand is the EFFECTIVE ADDRESS,
# and here the two COINCIDE -- "RCZ,$X0" addresses word 020 = word 16 =
# index register 0, and its idx field is also 0, so the old arm passed
# this check by luck.  Test 1's "R,$X15" addresses word 037 = word 31
# with idx = 0, where they differ, and that is the one that halted.  A
# block only discriminates where its operands make the wrong answer
# different from the right one.
#
# Measured: with RCZ made never to refill, the run halts at SERS with
# SEN = 005551.00, the deck's own check.
run "IBOX-4 RCZ (refill on count zero)" ./run_program.sh ../decks/ibox4_rcz.strap StretchIbox4RczTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/ibox4_rcz.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "IBOX-4 R from external memory (jb_ax4b, encoding)" python3 verify_ibox4_r_extmem_listing.py
# Routine 1238 test 2's first case, "OP ADR IS EM, RF ADR IS EM", and
# the block that drove the two-sequential-read form into execute().
#
# ibox4_refill and ibox4_rcz both address an INDEX REGISTER, which the
# arm reads combinationally -- one read and done.  This case addresses
# EXTERNAL MEMORY: I38RFL is an ordinary storage word (a NOP pair used
# as scratch), SX plants an index word over it, and R must refill it in
# place.  That needs the word at the effective address AND then the word
# its refill field names, which is V+CR's shape and for the same
# reason: a value from the first read decides the address of the
# second.  Until this block that case was setOpInvalid with the scope
# stated.
#
# MEASURED BOTH WAYS: against the setOpInvalid arm it halts at SERS
# with SEN = 005503.00, the deck's own "FAILED TO REFILL EXT MEM FRM
# EXT MEM"; with the two-read form it passes.
#
# AND NOTE WHICH CASES COULD HAVE FOUND IT.  The listing's four are
# 2A (EM/EM), 2B (EM/XS), 2C (XS/EM) and 2D (XS/XS); only 2A and 2B
# have the OPERAND outside index core storage, so 2C and 2D pass under
# either implementation.  Same asymmetry as ibox4_rcz against the
# operand bug -- cite the case that separates them, not the one that
# happens to agree.
#
# 2B IS ALSO HERE, and it is DECK COVERAGE rather than a second
# discriminator: its refill SOURCE is an index register where 2A's is
# external memory, but the model services both reads through one
# deferred-address channel, so no injection in this arm fails 2B while
# 2A passes.  Tried it -- the corrupted-second-read injection halts 2A
# first.  Said here so the pair is not cited as two independent
# witnesses when it is one.
run "IBOX-4 R from external memory (two sequential reads)" ./run_program.sh ../decks/ibox4_r_extmem.strap StretchIbox4RExtmemTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/ibox4_r_extmem.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "IBOX-4 refill address gate (jb_ax4b, encoding)" python3 verify_ibox4_refill_nop_listing.py
run "IBOX-4 routine 1244: RNX's refill-address NOP gate (jb_ax4b PDF pp.90-98)" python3 verify_ibox4_rnx_nop_listing.py
run "IBOX-4 routine 1246: TRANSMIT and SWAP (jb_ax4b PDF pp.99-100, 112-113)" python3 verify_ax4b_1246_transmit_swap_listing.py
run "IBOX-4 routine 1246 TEST 2A/2B: the forward-backward and direct-immediate modifiers (jb_ax4b PDF pp.109-111)" python3 verify_ax4b_1246_modifiers_listing.py
run "EXIC: the pseudo-instruction counter, and the step sized by the subject's length" ./run_program.sh ../decks/exic_subject.strap StretchExicSubjTb \
    "PC=6223" \
    "PSICA:3264=0x320280003302800" "PSICB:3265=0x320c80003306800" \
    "PSICC:3266=0x32168000330a800" "PSICD1:3267=0x32228000330e800" \
    "PSICD2:3268=0x322880003312800" "PSICE:3269=0x323280003316800" \
    "PSICF:3270=0x32488000331a800" "PSICH:3271=0x325b2000331e800" \
    "PSICI:3272=0x326280003322800" \
    "RESA:3333=0x29cbb829c" "RESB:3334=0xfac688fac" "RESD:3335=0x2ef53705d" \
    "RESE:3336=0xfac688fac" "RESF1:3337=0x29cbb829c" "RESF2:3338=0xfac688fac" \
    "RESF3:3339=0x5372ef0a6" "RESG:3340=0x5372ef0a6" "RESH:3341=0x2ef53705d" \
    "MARKC:3332=0x8000000000000000" "SUBJH:3222=0x340d4100325a800" \
    "PSICG:21=0x325200000000000"
# **EXIC IS IMPLEMENTED**, and StretchCore.bsv needed no change -- the
# same result EX got, for the same reason: HeldOp carries the
# EXECUTE's own pc/len across the subject swap.
#
# THE STEP IS THE WHOLE INSTRUCTION.  Printed p.50: "After the subject
# instruction has been fetched but prior to its execution, the
# pseudo-instruction counter is stepped.  If the subject instruction is
# half-length, the pseudo-instruction counter is stepped once; if
# full-length, twice."  Both lengths are covered, using TEST 2B's own
# LV / V+I / KV / BZXE idiom.
#
# AND A SENTENCE docs/NEXT.md 4a NEVER QUOTED, which is its own rule:
# "When EXECUTE INDIRECT AND COUNT is a subject instruction in a
# multi-leveled execution operation, EACH pseudo-instruction counter
# involved is appropriately stepped between the fetching and executing
# of its corresponding subject instruction."  Block D is the only block
# in either program whose subject is itself an execution operation, so
# it is the ONLY one that separates "each counter stepped by its own
# subject's length" from "every counter stepped by the final
# instruction's".  Injection I16 exists because a review flagged D as
# unproven: under it the inner counter steps correctly and the outer
# does not, which is why the failing row names the outer one.
#
# THE COUNTER WORD IS DATA AND IS NEVER EXECUTED -- the contract
# routine 1262 TEST 2A checks with "-INST AT PSIC WAS EXECUTED."  Block
# H makes it falsifiable here: PSICH is itself a live instruction,
# "Z,SUBJH", whose execution would zero the word holding the subject.
# Injection I14 runs the counter word instead of reading it.
#
# TWO ESTIMATES FROM THE EX IMPLEMENTATION WERE WRONG, and were
# verified rather than trusted.  (1) exSubjectAddr CANNOT be reused at
# all, not even with another case: it answers "where is the subject"
# from the INSTRUCTION, while EXIC's subject address is a function of a
# word that must be FETCHED FIRST.  resume() went from three shapes to
# five.  (2) The step is a STORAGE WRITE, so it costs its own clock --
# a module method may be called once per rule and a subject may itself
# write storage.  The E-box writes the step, installs the subject and
# sets a sticky subjReady, and canResume() honours that flag in place
# of the read handshake.  Nothing observes the extra clock, verified
# rather than asserted: `held` stays Valid so ebox.busy() blocks
# armInterrupt and armRemove, resumeReady blocks armPrepare, and
# rl_prepare no-ops on busyFor(OwnerIbox) -- exactly the state during a
# read.  check_schedule.py still passes all ten core rules.
#
# Sixteen injections, every halt OBSERVED, none survived.

run "EX: the subject is fetched and executed, control returns after the EXECUTE" ./run_program.sh ../decks/ex_subject.strap StretchExSubjTb \
    "PC=5144" "RESA:2755=0x29cbb829c" "RESB:2756=0xfac688fac" \
    "MARKC:2754=0" "MARKD:2757=0x8000000000000000"
# **EX IS IMPLEMENTED.**  The largest unimplemented instruction with a
# READ oracle, and the one four transcription targets were waiting on.
# Printed p.50: "Bits 0-18 of the effective address form the address of
# the location of a subject instruction that is fetched and executed.
# Subject instructions of EXECUTE may occupy any addressable location."
#
# THE STRUCTURE IS A SWAP, NOT A NESTED CALL, and that choice is what
# made it fit.  The EX arm bails with `needsRead` = the word holding
# the subject and touches nothing else; mkEBox.resume() then recognises
# the held instruction as an EXECUTE, decodes the fetched word, and
# replaces held.di with the SUBJECT while keeping held.pc and held.len
# -- the EXECUTE's.  Everything follows from that: `fallthrough` is the
# half-word after the EXECUTE, a subject needing an operand bails
# normally because it IS the held instruction by then, and a subject
# that is itself an EXECUTE bails again and the swap repeats, one level
# per clock.
#
# RECURSION WAS REJECTED FOR A CONCRETE REASON: BSV inlines functions,
# so a second execute() call in resume() is a second instantiation of
# the whole datapath and a second st.writeWord writer in one rule --
# the G0004 shape StretchStorage.bsv documents.  resume() has exactly
# ONE execute() call site.
#
# AND StretchCore.bsv NEEDED NO CHANGE AT ALL, which is the good news
# about the swap.  commitNext and rl_exec_resume's `taken` read pc/len
# back out of ebox.pending(), so keeping the EXECUTE's pc/len inside
# HeldOp makes printed p.49's rule fall out with zero edits to the
# instruction unit: "it is never stepped during the execution of any
# subject instruction even if the subject instruction is again one of
# the execution instructions."  The only other file touched is
# StretchIBox.bsv, COMMENT-ONLY.
#
# TWO DETAILS THE PLAN'S PROPOSAL DID NOT FORESEE, both real and both
# from the deck: a FULL-LENGTH SUBJECT AT AN ODD HALF-WORD straddles
# two storage words and needs a second read before it can be decoded
# (1262 TEST 1CC's own I62B6 is exactly that shape); and the CLASS-1
# ALARM OF AN INTERMEDIATE LEVEL must be carried forward, because that
# level's indicator word was thrown away when it bailed.
#
# Fifteen injections across the four programs, every halt OBSERVED,
# NONE survived.  Each was applied by a substitution that exits with
# ABORT unless its anchor occurs exactly once, printing the diff first.

run "EXIC: the two address restrictions, and the Data Store alarm on its own effective address" ./run_program.sh ../decks/exic_addr.strap StretchExicAddrTb \
    "PC=7223" \
    "RESA:3842=0x390080003901000" "RESA2:3843=0x29cbb829c" "RESC:3844=0x29cbb829c" \
    "PSICA_X0:16=0x390200000000000" "X15:31=0x3c0421000000000" \
    "PSICB:3713=0x7c8000007d000" "PSICC:3714=0x8280000081000" \
    "PSICD:3777=0x390880003909000" "DSMARK:6=0x8000000000000000"
# EXIC's TWO ADDRESS RESTRICTIONS, which EX does not have -- printed
# p.50: "Pseudo-instruction counters may occupy any of the index
# registers as well as main core storage locations but cannot occupy
# locations addressed between 0 and 15" and "Subject instructions of
# EXECUTE INDIRECT AND COUNT may occupy any available locations with
# addresses 32.00 and greater."  Contrast EX: "Subject instructions of
# EXECUTE may occupy any addressable location."
#
# AND A THIRD RULE NOBODY HAD QUOTED, found by reading the page rather
# than treating the p.50 paragraph as the whole contract.  Printed
# p.32's Data Store list, item 5, verified first-hand: **"The effective
# address of EXECUTE INDIRECT AND COUNT."**  It is in the DATA STORE
# list, not Data Fetch -- which is exactly right, because the counter
# gets WRITTEN when it is stepped.  So DS applies, and with it p.32's
# store-type rule: "Since this indicator is permanently masked on,
# storing in core storage is always suppressed, and THE OPERATION IS
# ALWAYS TERMINATED."
#
# INJECTION I12 IS A FINDING, NOT A NULL, and it is why the
# termination sits BEFORE the read.  The plausible "set DS and carry
# on" reading makes DS **vanish entirely**: a call that bails has its
# whole indicator word discarded by execute()'s tail, so DS never
# reaches the register AND the counter is stepped inside the protected
# area.  Independent evidence for the ordering.
#
# THE COUNTER'S BOUNDARY IS THE ONE OPEN QUESTION, flagged rather than
# smoothed.  p.50 says "between 0 and 15"; routine 1262 TEST 3A's three
# messages all say "LESS THAN 15".  NO DECK ROW DISCRIMINATES -- the
# deck's counter is word 9, illegal under either reading.  The manual
# was taken (pw < 16), backed structurally: 0-15 are the special
# registers and 16-31 the index registers, which the same sentence
# EXPRESSLY ALLOWS.  Block A2 pins word 16 as legal and block A pins
# word 15 as illegal, so a deck row with a counter at word 15 would
# visibly contradict block A.  The R/RCZ precedent -- where the obvious
# "refill < 16" was wrong because 0 refills -- is why this is flagged.
#
# ONE RULE IS NOT IMPLEMENTED AND IS NOW REACHABLE where it was merely
# hypothetical for EX: printed p.51 item (d), "If the address of the
# location of the subject instruction ... is both protected and
# invalid, indicator IF will be actuated.  Indicator AD will not be
# actuated ... unless the IF mask bit is zero."  For EXIC "invalid" now
# means something (below 32.00).  This arm raises AD and never IF.

run "EX: the EXE indicator, and the whole subject operation suppressed" ./run_program.sh ../decks/ex_exe.strap StretchExExeTb \
    "PC=5684" "RESD:3074=0x80000" "MARKE:3075=0x555555555"
# THE EXE RULE IS NOT "THE BRANCH IS CANCELLED" -- IT IS "THE OPERATION
# IS SUPPRESSED", and that distinction forced the shape of the code.
# Printed p.49: "The execution exception indicator (EXE) is turned on
# by any branch operation of a subject instruction in which the
# condition for a successful branch is met.  When indicator EXE is
# actuated, the branch and all associated operations are not performed.
# The suppressed actions include the disabling in BRANCH DISABLED, the
# enabling in BRANCH ENABLED or BRANCH ENABLED AND WAIT, the counting
# and refilling in COUNT, BRANCH AND REFILL, and so on."  Printed p.45
# item 18 says it from the other side: "The subject operation was
# suppressed."
#
# SO IT COULD NOT BE DECIDED AT execute()'s COMMIT POINT, where the IF
# branch-suppression clause already lives.  By the time `next !=
# fallthrough` is known, st.setIrqEnabled (the BE/BD/BEW arm) and
# st.writeWord (SIC, BRANCH ON BIT) are Actions ALREADY TAKEN.  Hence
# five per-arm decisions instead of one central one.  The single
# reordering this forced is moving the BE/BD/BEW enable change BELOW
# evalBranch in the unconditional arm -- safe, because that evalBranch
# reads the instruction and the index registers only, never the enable
# bit.  Injection I9 is the one that proves it matters: hoisting the
# enable change back above the guard leaves the machine ENABLED after a
# subject BE, and the program catches it via DF.

run "EX: the EXE rule over a BRANCH ON INDICATOR subject, including its clear" ./run_program.sh ../decks/ex_exe_bind.strap StretchExBindTb \
    "PC=7697"
# THIS PROGRAM EXISTS TO PIN AN INFERENCE SO A LATER DECK ROW CAN
# CONTRADICT IT VISIBLY.  p.49's list of suppressed actions ends "and
# so on" and does NOT name a branch-on-indicator's trailing-Z CLEAR.
# Reading p.45 item 18's "the subject operation was suppressed" to
# cover it is an INFERENCE, and it is labelled as one in the model.
#
# THERE IS NO DECK WITNESS: 1262 TEST 1CC's branch-on-indicator subject
# class is on PDF p.92 and the transcription begins at I6225 on p.93.
# Injection I15 is the only one in the whole set that separates "the
# branch was suppressed" from "the OPERATION was suppressed" -- it
# suppresses the branch but merges o.ind, so the clear lands, and the
# program halts.  If p.92 is ever transcribed and disagrees, this is
# the test that will fail rather than a comment nobody reads.

run "EX: the subject location's address alarm, and p.50's below-32 carve-out" ./run_program.sh ../decks/ex_monitor.strap StretchExMonTb \
    "PC=6705" "MARKP:3392=0" "MARKB:3393=0" "MARKC:3394=0" "MARKD:3395=0"
# THE SUBJECT'S OWN LOCATION IS ADDRESS-MONITORED, and the authority is
# a contrast rather than a single sentence.  Printed p.32 class 1 is
# "the location of each instruction to be executed" -- and a subject IS
# executed.  Printed p.51 item (d) corroborates: "If the address of the
# location of the subject instruction of EXECUTE or EXECUTE INDIRECT
# AND COUNT is both protected and invalid, indicator IF will be
# actuated" -- against item (c), where a BRANCH target that is both
# raises AD only, "because an instruction has not been fetched."
#
# AND ifViolates' `a >= 32` GUARD IS A DIFFERENT RULE THAT HAPPENS TO
# AGREE NUMERICALLY -- checked rather than assumed, and the call site
# says so.  That guard is justified by p.45 on AD ("Branching to an
# address below 32 also actuates the indicator") plus p.32's "an
# address which actuates AD cannot actuate any of the address alarm
# indicators": for a BRANCH below 32 the machine raises AD INSTEAD of
# IF.  For an EXECUTE below 32 it raises NEITHER, because p.50 says the
# subject may occupy any addressable location, so there is no invalid
# address to report.  The two coincide today only because this model
# does not raise AD for a low branch either.  A later AD implementation
# must not reach for this guard.
#
# THE CARRIED ALARM IS OR-ED ACROSS LEVELS, NOT OVERWRITTEN, and
# injection I4 is the one that catches the difference.

run "Interruption timing: the deck's BE / one instruction / BD bracket" ./run_program.sh ../decks/int_timing_bracket.strap StretchIntTimingTb \
    "PC=4246"          # 004113.00; hand-written to routine 1260's shape
# THE DECK HAS BEEN CARRYING THE DISCRIMINATOR ALL ALONG.  Routine 1260
# brackets every provoked interruption between an enable and a disable
# ONE INSTRUCTION APART -- ax5b_160105_compare.strap, "BE,$+.32 /
# LX,$X13,0($X2) / BD,$+.32" -- and printed p.48 allows ZERO
# instructions of lateness.  This model allowed THREE.
#
# Measured, not argued.  Sweeping N filler instructions before the BD
# against the PRE-FIX model: N=0,1,2 all halt at the "we did not
# interrupt" check; N=3 and N=4 pass.  Post-fix N=0 passes.
#
# AND THE PLAN'S STATED MECHANISM WAS WRONG, which changed the cost.
# docs/NEXT.md attributed the loss to the I-box racing past the
# provoking instruction and executing the BD.  It does not race:
# StretchIBox's iboxHazard drains the look-ahead before EVERY
# unconditional branch, BD included, citing Perf. Char. p.3-18 ("BD ...
# empty the LA completely").  The real cause was one term in
# armInterrupt -- "ebusy == 0", the CHARGED TIME of the instruction just
# retired from a look-ahead level, not a structural busy.  rl_prepare
# never waited for it, so every I-box instruction that fitted inside the
# budget ran first, the BD among them.  The plan's story implied
# restructuring the look-ahead; the fix is deleting a predicate term.
#
# A SHARPER PRIMARY SOURCE THAN THE ONE THIS PROJECT HAD BEEN CITING.
# Everyone quotes p.48's "Interruption Action" paragraph.  The SAME PAGE
# under "Mask Register" pins it harder: "If the bit of the mask is 1 and
# the interruption system enabled, occurrence of the corresponding
# condition will cause program interruption AT THE END OF THE OPERATION
# DURING WHICH THE INDICATOR IS TURNED ON."  That ties the interruption
# to the operation that SET the indicator, which is exactly the clause
# the old behaviour violated.
#
# THE PROVOKER IS DELIBERATELY E-BOX CLASS, and that is why this test
# exists rather than interrupt_pg0.strap catching it years ago: an
# I-box-class provoker is charged an `ibusy` budget that rl_prepare
# already honours, so it lands at the instruction boundary anyway.  A
# BB1-style bracket would have measured nothing.
#
# ONE INJECTION SENT A CHANGE BACK, which is the discipline worth
# copying.  The author also made interruptDue() combinational in
# StretchStorage.bsv, suspecting the latch was a second cause.
# Injection 3 -- relatch it ALONE, with ebusy already dropped -- PASSES.
# So the latch is not what the deck's bracket would catch, and
# StretchStorage.bsv went back to pristine on measured evidence rather
# than staying changed on plausibility.
#
# TIMING INVARIANCE MEASURED, not assumed: the three CYCLES benchmarks
# give 113 and 807 before the fix and 291/113/807 after -- identical.
#
# ONE LINE OF THE FIX IS UNTESTED AND CANNOT BE TESTED BY THIS SUITE,
# stated here rather than left to be discovered: "ebusy <= eb;" in
# rl_interrupt has no injection that could catch it, because the three
# CYCLES benchmarks never enable interrupts and every interrupting test
# checks a halt address rather than a clock count.
#
# AND THE HARDER HALF IS UNTOUCHED.  An I-box-class instruction that the
# I-box has already run AHEAD of a pending level is committed and cannot
# be taken back, so an indicator set by a level is still not reported
# before an I-box instruction that overtook it.  iboxHazard keeps that
# narrow but does not close it; closing it needs the `recover` path
# generalised from wrong-way branches to interruptions.  Recorded in
# docs/NEXT.md item 3 as a write-up, not attempted.

run "IBOX-4 routine 1246 TEST 1B/1C/1D/1G: the memory pairings (jb_ax4b PDF pp.101-106)" python3 verify_ax4b_1246_memories_listing.py
# 176 ROWS, FOUR OF THE EIGHT REMAINING SUB-TESTS, and the CUT IS
# PRINCIPLED RATHER THAN FATIGUE.  The nine TEST 1 sub-tests are a 3x3
# of sending x receiving memory -- {EXT I46D4, IX $X4, INT $L} against
# {EXT I46D2, IX $X3, INT $R}.  1A (already done) is EXT->EXT.  These
# four are the only cells where an operand KIND first enters; the four
# left are cross-products of kinds already witnessed.  All eight pages
# were read first-hand so that is a measurement, not a guess.  Left:
# 1E 007102.00, 1F 007132.00, 1H 007212.00, 1I 007242.00.
#
# THE VERDICT ON "1B-1I ARE MORE ROWS, NOT MORE KINDS": HALF RIGHT, and
# the honest answer is that the 1A transcriber was very nearly right.
# Right about mnemonics -- not one of the seventeen is new, each
# appears in 3 to 138 other verify files -- and right about shape, same
# 44-row order, same six error pairs, same branch offsets.  Wrong only
# in that the operand KIND changes: A1 and A2 take REGISTER addresses
# ($L word 0o10, $R word 0o11, $X3 0o23, $X4 0o24) instead of memory
# constants.  And that is new to ROUTINE 1246, not to the repo -- grep
# found registers in TRANSMIT address fields already in
# verify_ax5b_160_test6 and verify_ax5b_16087.
#
# COMPLETENESS IS PROVED INDEPENDENTLY OF THE RUN, which matters
# because check_rows only checks rows it is handed: each sub-test spans
# 24 words = 48 half-word slots, minus 4 two-slot instructions (two T,
# two L(BU)) = 44 rows.  Four sub-tests, 176.
#
# THE SIBLINGS' MEASURED NULL SURVIVES, with 3x the transmit rows and
# two operand kinds they lack.  All sixteen T rows across pp.101-108
# print 02 for bits 50-55, so bit 50 = 0, and the only three A2
# operands in all of TEST 1 are I46D2 (word-aligned), $X3 and $R --
# word addresses, so bit 50 CANNOT be 1.  By arithmetic, not by glyph.
#
# Nine injections.  The signature one is strap_asm's index base
# (16+n)*64 -> (17+n)*64: 19 rows, every $X-in-address row in all four
# blocks, and the $R/$L rows untouched -- NEITHER SIBLING CAN PRODUCE
# IT.  Two more separate $R from $L by moving one and not the other.
#
# AND ONE OF THE TWO NULLS IS THE METHOD CATCHING ITSELF.  Injection
# N-B was the author's FIRST attempt at N-4: enc_branch_on_bit and
# enc_transmit have TEXTUALLY IDENTICAL A1 clauses, so the patch landed
# on the wrong encoder, no BRANCH ON BIT row exists in range, and the
# run came back green.  That is exactly the false null the
# confirm-it-applied discipline exists to catch, recorded rather than
# quietly dropped.
#
# TWO DECK TYPOS inside the range, both clean wrong characters rather
# than ragged correct ones: 006777.00's "-IX STG DROPS ALL BITS," ends
# in a COMMA (bowl plus a descending tail identical to the commas on
# the same line, where the neighbouring periods are bare bowls), and
# 007052.00's heading carries a STRAY COMMA after "TO".  Two more on
# pages not transcribed are recorded so nobody re-discovers them.
#
# A CORRECTION TO THE BRIEF THAT COMMISSIONED IT: TEST 1A is the FIRST
# of the nine, at 006742.00 on p.100, not the ninth.  They run 1A..1I
# in address order across pp.100-108.

# 119 ROWS, BOTH SUB-TESTS, NO CUT -- 007272.00-007372.00, contiguous
# under one SLC across three pages.  It also turns the sibling
# section's arithmetic endpoint into a measurement: 007372.00 is the
# printed location of p.111's last row.
#
# **BIT 55 IS NOW WITNESSED SET, and as a clean MATCHED PAIR** -- the
# thing the section above could not supply:
#
#   007277.00  T, $X2,I46D5,I46D2   7430.00 80 007425.04 20   (p.109)
#   007321.40  TB,$X2,I46D5,I46D2   7430.00 80 007425.05 20   (p.110)
#
# Same A1, same A2, same J, same hex byte.  ONE OCTAL DIGIT, 04 -> 05,
# and that is bit 55.  Structural twin of the sibling's T/SWAP bit-57
# pair -- but it moves the OCTAL column where that one moves the HEX
# column.  Between the two files all three of the banner's modifier
# bits are now pinned by a matched pair.  Reference Manual printed
# p.30, re-read first-hand here rather than quoted from the sibling:
# "The choice between forward and backward transmission is specified
# by modifier bit 55.  A zero specifies forward transmission; a one
# specifies backward transmission."
#
# `TB` is this block's only genuine repo first, and the row sits at an
# ODD half-word so it straddles a word boundary as well.  TBI, SWAPI,
# SWAPB and SWAPBI remain card-only with zero listing rows anywhere.
#
# BIT 56 IS WITNESSED SET BUT IS NEITHER A FIRST NOR A MATCHED PAIR,
# and the file says so rather than claiming the stronger result: the
# TI/T comparison on p.111 differs in J as well, so both columns move,
# and grep found every existing TI row in the repo already printing A0.
# First in the ax4b deck; corroboration for the project.
#
# A PRIMARY-SOURCE QUOTE THAT RETIRES A SUBSTITUTION THIS PROJECT HAD
# BEEN MAKING ON CONVENTION.  Printed p.30: "In immediate count
# operations, the full word count is specified by instruction bits
# 51-54."  That is why the deck spells the J field BOTH WAYS within
# three pages -- "T,$X2,..." and "TB,$X2,..." on pp.109-110 (direct, so
# 51-54 name an index register) against "TI,1,..." on p.111
# (immediate, so 51-54 ARE the count) -- and the printed octal pairs
# agree (04 -> J=2, 02 -> 1).  So the sibling file's $X1 -> 1
# substitution is what IBM's own assembler did, not a convention this
# project invented.  It also explains TEST 2B's design: load a DIRECT
# count of 2 then issue TI with immediate count 1, error "-TRANSMIT
# IMMEDIATE USES / -A DIRECT COUNT."; load a direct count of 1 then
# issue T with J=2, error "-TRANSMIT DIRECT USES / -AN IMMEDIATE
# COUNT."
#
# THE DECK LABELS THE BRANCH AS THE GOOD PATH IN ITS OWN HAND.  At
# 007336.00, "BZXVZ,I4622" carries the comment "-OK" -- the only one in
# either 1246 file.  First-hand evidence for this project's
# branch-polarity rule rather than inherited convention.  (An inference
# from one two-character comment, and flagged as such; no check rests
# on it.)
#
# Seven injections, observed.  Two pairs are designed to SEPARATE
# adjacent modifier bits on a single row: TI (0,1,0)->(0,0,0) moves the
# hex byte only while (0,1,0)->(1,1,0) moves the octal pair only, which
# splits bits 56 and 55 on row 007346.40; TB (1,0,0)->(0,0,0) and
# ->(1,0,1) do the same for bits 55 and 57.  One result was not what a
# guess would say: INDICATOR_BITS["XCZ"] 48->49 moves the TOP bit of
# the hex byte (40->C0), colliding with XVLZ.
#
# THE SIBLING'S MEASURED NULL IS CONFIRMED, NOT BROKEN.  Masking
# enc_transmit's A2 to clear bit 50 still changes nothing: every A2
# here is I46D1 or I46D2, both word-aligned.  Across both 1246 files
# there are now EIGHT transmit rows and all eight are A2-word-aligned,
# so the null is a stronger statement than either file could make
# alone.
#
# TWO GARBLES, BOTH DECK TYPOS, and "FOWARD" is the harder call because
# a DROPPED LETTER HAS NO GLYPH TO INSPECT.  Settled by PITCH: on the
# line above, FORWARD occupies seven cells spanning 402 px = 57.4
# px/cell; FOWARD occupies six cells spanning 346 px = 57.7 px/cell.
# Identical pitch, one fewer cell, and no gap anywhere.  Damage
# degrades a glyph in place; it does not delete a character and close
# the 57-px hole behind it.  "INNEDIATE" is settled by shape: both N's
# carry a single unbroken diagonal between full-height verticals with
# no stray ink where an M's second diagonal would be.
#
# CONSTANT-BLOCK HANDLING WORTH COPYING: rather than SYN the I46D*
# constants -- which would make every transmit operand an INPUT -- the
# program re-lays that block from its own SLC as UNASSERTED source, so
# the location counter computes the addresses and the printed A1/A2
# fields genuinely check them.  No row of it is asserted, so nothing
# duplicates the sibling section.

# THE FIRST LISTING WITNESS FOR PLAIN **T** AND FOR **SWAP** IN THIS
# REPO.  Before this block, opcodes.TRANSMIT_CODES said so itself --
# "WITNESSED: only TI ... The other seven are from the card alone and
# have no listing row in this project yet."  T gains 3 rows, SWAP 1.
# Five of the eight (TB, TBI, SWAPI, SWAPB, SWAPBI) remain card-only.
#
# AND THE PAIR IS THE BEST-CONTROLLED ONE THIS PROJECT HAS:
#
#   007374.40  T,   $X1,I46D1,I46D4   7424.00 80 007427.02 20
#   007405.00  SWAP,$X1,I46D1,I46D4   7424.00 80 007427.02 60
#
# Same J, same A1, same A2, same indices -- ONE printed hex digit
# apart, and that digit is IBM bit 57.  Stronger than the RNX pair
# above, where the two rows also differ in their operands.  Reference
# Manual printed p.30: "The choice between unidirectional and
# bidirectional transmission is specified by modifier bit 57.  A zero
# specifies unidirectional transmission; a one specifies bidirectional
# transmission."
#
# 119 checks over 102 rows in four blocks: preamble (p.99), TEST 1A
# EXT-MEM-to-EXT-MEM (p.100), TEST 2C the transmit/swap modifier bit
# (p.112), and the constants.  The transcriber took 2C rather than the
# adjacent 1B-1I DELIBERATELY and said why: 2C is the only place in the
# routine where SWAP appears at all, and 1B is a near-clone of 1A that
# "adds rows, not kinds."  Next block if anyone continues: TEST 1B at
# 006772.00, PDF p.101.
#
# ONE MEASURED NULL with its arithmetic: masking enc_transmit's A2
# field to clear bit 50 (the A2 half-word select) changes NOTHING.  All
# four T/SWAP rows name word-aligned constants, so bit 50 is already
# zero, and only a Transmit with an ODD-HALF-WORD A2 could catch it --
# routine 1246 has none.
#
# A NEGATIVE ON THE TWO SWAP CLAIMS, which is what this block was
# partly sent to look for.  Reference Manual printed p.51 says a SWAP
# against a protected address actuates BOTH DS and DF, and printed p.43
# Figure 11's footnote S says suppression does not apply "during EX,
# EXIC, T, and SWAP" -- both verified verbatim here.  This deck is
# evidence for NEITHER: the banner names no protection, bounds or
# indicator clause, TEST 2C touches two ordinary words in the routine's
# own constant block, no DS/DF/IF is branched on anywhere in range, and
# the deck runs with interrupts disabled.  That is consistent with the
# wider finding in docs/NEXT.md 5b -- the actuation-priority rule has
# no deck oracle anywhere.
#
# Six injections, observed, aimed at the modifier bits because that is
# what the block is about:
#   TRANSMIT_CODES["SWAP"] -> T's code     1 row (hex 60->20, and the
#       row then prints IDENTICALLY to the T row above it)
#   TRANSMIT_CODES["T"] -> SWAP's          3 rows (hex 20->60)
#   TRANSMIT_CODES["T"] bit 56             3 rows (hex 20->A0)
#   TRANSMIT_CODES["T"] bit 55             3 rows -- OCTAL PAIR moves
#       02->03, hex byte unchanged.  Three injections on one mnemonic,
#       three different printed effects.
#   DIR_INDEX_CODES["KC"] -> KV's          1 row, and it collides
#       EXACTLY with the KV row three lines up.
#   enc_transmit A1 (bitaddr24 >> 5)       4 rows, every digit

# A SECOND REFILL-ADDRESS NO-OP RULE, over a DIFFERENT range from the
# 1-15 rule the block above establishes for R/RCZ -- and the affirmative
# evidence this project uses against closing the refillLegal question
# by symmetry.  Routine 1244's header: "-4. CHECK THAT THE INSTRUCTION
# IS / -NO OPPED WHEN EITHER THE / -OLD OR THE NEW REFILL FIELD / -OF
# IX REG 0 LIES IN THE / -RANGE OF 1 TO 37 OCTAL."
#
# THE FIRST LISTING WITNESS FOR **RNX** IN THIS REPO.  No verify_*.py
# contained an RNX row before; the name appeared only in opcodes.py's
# table, the coverage audit, and two comments.  (It is in
# DIR_INDEX_CODES, not MISC_CODES.)  Encoding only: StretchDecode
# defines dixop_RNX so the word decodes, but StretchExecute's default
# arm sets OP -- "RNX, LVE: out of scope".
#
# AND THE DECK'S OWN AUTHORS KNEW THE ZERO BOUNDARY WAS OPEN.  PDF p.98
# ships the sweep as "I44XW3 XW,1.0,31,0" -- 1 to 37 octal -- and puts
# a SPARE TRIPLE beside it, "I44XWC XW,0.0,32,0" pointing at the
# "ADDRESS IS 0." entries of both error tables, under the comment "-IF
# 0 BECOMES ILLEGAL FOR RNX, USE THE / -FOLLOWING THREE INDEX WORDS TO
# REPLACE / -THOSE DIRECTLY ABOVE."  Reference Manual printed p.27 says
# locations 0-31; the deck walks 1-31 and carries the patch.  Neither is
# wrong: the gap is a HEDGE, not an error.  Verified first-hand.
#
# Five injections, observed.  The two RNX ones are the point: they move
# only the two RNX rows, and they move them in the TWO DIFFERENT
# printed columns -- top bit of the 5-bit field lands in the octal
# pair, bottom bit in the hex byte.  A check reading one column would
# miss one of them.
#
# ONE INJECTION THIS BLOCK DOES NOT CATCH, recorded rather than swept
# up: dropping "LRI" from IMM_INDEX_COUNT_OPS leaves every row
# unchanged.  The reason is arithmetic -- both LRI operands here are
# word-aligned, and for a word-aligned operand (bits>>6)<<1 and bits>>5
# are the same number.  So those rows witness LRI's opcode and J field
# and say nothing about which field layout is right.

# Routine 1238 test 2 cases 2G and 2H -- the REFILL ADDRESS GATE, and
# the reason they are ONE program.  The routine header states the rule
# as "NOPING IF RF IS FROM 1 TO 15", and the obvious way to write that
# -- suppress a refill addressed below 16 -- is WRONG.  Test 2 pins the
# boundary from both sides in adjacent cases: 2G "CHK REFILL FRM LOCN
# 0" (word 0 DOES refill, from the permanently protected zero) and 2H
# "CHK NO REFILL FRM LOCNS 1 THROUGH 17" (octal, so 1-15, suppressed).
#
# MEASURED ALL THREE WAYS:
#   no suppression        2G passes, 2H halts at 005674.00, the first
#                         entry of the routine's own error table --
#                         whose text, read first-hand at PDF p.70, is
#                         "-FAILED TO NOP WHEN RF ADR IS 1." under a
#                         header "-YOU CAME TO THIS ERROR TABLE FROM
#                         13825".  ("DID REFILL" is the in-line comment
#                         on a different row; this program STUBS the
#                         table as bare halts, so that row had never
#                         been read.)
#   refill >= 16          2G halts at SERS, 2H passes
#   refill == 0 or >= 16  both pass
#
# 2H IS THE MOST SELF-MODIFYING BLOCK IN THE SUITE.  Each pass, two
# SVAs patch the ADDRESS FIELDS of two instructions further down:
# I3824's "LRI,$X0,0.0" gets the next refill location and I3825's
# "$B,0" gets the next error-table entry.  LVI plants a known value, R
# must leave it alone, KVI checks, and V+I/C-I/BXCZ walk the location
# and count the loop down.  (The listing's "$B,0" is the dollar prefix
# marking an opcode assembled as a patchable word -- same convention as
# "$L%BU" and "$RNX" in ja_ax1a's constants.)
#
# AND THE CONTROL CAUGHT A BUG IN THE TEST BEFORE IT CAUGHT ONE IN THE
# MODEL.  The "refill >= 16" injection PASSED when it should have
# failed, because the entry point was END,I3822 -- after the 2G section
# -- so 2G never ran: a two-case block that executed one case, green.
# Fixed to enter at I382G.  A control is worth running even when you
# expect it to confirm what you already believe.
run "IBOX-4 refill address gate (locn 0 refills, 1-15 do not)" ./run_program.sh ../decks/ibox4_refill_nop.strap StretchIbox4RefillNopTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/ibox4_refill_nop.strap").read()).symtab["PASS"]//32)')"

run "IBOX-4 RCZ zero gating (jb_ax4b, encoding)" python3 verify_ibox4_rcz_zerogate_listing.py
# Routine 1238 test 3's second half, the complement of ibox4_rcz: RCZ
# must NOT refill while the count is NON-zero, walked over EVERY ONE of
# the 18 count bits.  LC takes h[31:14] -- the top 18 bits of the
# addressed HALF-WORD -- so stepping $X14 through BIT0, BIT1, ... loads
# counts 2^17, 2^16, ... 2^0 in turn.  That is what "zero gating"
# means: RCZ's zero test has to look at all of them.
#
# Measured: with the test narrowed to the low 8 count bits, 2^17
# misreads as zero, RCZ wrongly fires on pass one, and the run halts at
# 005732.00 -- entry 0 of the routine's error table, the 2^17 entry.
# The table names which count bit was missed.
#
# AND IT FOUND A SECOND MODEL BUG, without whose fix it cannot run at
# all.  The loop does C-I then BXCZ back to back, so the branch reads
# XCZ from the C-I -- and C-I did not set the index result indicators.
# Every DIRECT index load (LV/LC/LR) already set them; six IMMEDIATE
# arms did not.  Without the fix the loop never terminates: a step cap
# spinning at 005553.40.  C+I, LVI, LVNI, LCI and LRI have the SAME gap
# and nothing drives them, so they are left alone -- the note on the
# C-I arm says what would settle each.
run "IBOX-4 RCZ zero gating (all 18 count bits)" ./run_program.sh ../decks/ibox4_rcz_zerogate.strap StretchIbox4RczZeroGateTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/ibox4_rcz_zerogate.strap").read()).symtab["PASS"]//32)')"

run "IBOX-1 V+IC chain (ja_ax1a, encoding)" python3 verify_ibox1_vpic_chain_listing.py
# V+IC, and with it the LAST of the eight modeled index operations a
# coverage screen found in zero suite programs.  The largest of the
# eight, left until last for that reason.
#
# THE ONLY TWO-PHASE BLOCK IN THE SUITE, and that is why it is worth
# its length.  Every other self-modifying chain here manufactures its
# links and branches through them.  This one proves the VALUE and the
# COUNT separately: phase 1 (IBM2-IBM7) stores each V+IC result over
# one branch-to-self and each COUNT into a plain data word
# (IBM29-IBM34, "COUNT FIELD STORAGE"), and phase 2 -- the listing's
# "RESTART OF ROUTINE" -- reads those counts back, adds IBM59 (a 0.4
# constant annotated "TO CONVERT C TO BD, C") and stores the sums over
# a SECOND chain.  IBM8 marks the seam, "PROVE ADD TO VALUE"; IBM23 is
# the hinge, "TO PROVE COUNTING OPN".
#
# AN ASYMMETRY THAT READS LIKE AN ERROR AND IS NOT, worked out before
# the block would assemble sensibly: IBM2 and IBM7 apply V+ COM04
# before storing their count, IBM3-IBM6 store the RAW count, and phase
# 2 adds IBM59's 4 to all six alike.  So IBM53 and IBM43 end up with 8
# in the low bits and the rest with 4 -- and since the branch code at
# IBM bits 19-21 is BE = 000, BD = 001, B = 010, the first two become B
# and the rest BD.  All six branch unconditionally to the addresses the
# listing names, which is why it calls them all "BD".  Confirmed in the
# run: W4477 and W4504 carry code 010, the other ten 001.
#
# Measured, and the signature splits exactly on the phase boundary:
# with V+IC decrementing the count twice, all SIX value-chain words
# still pass and all SIX count-chain words fail.
VPIC_CHECKS=$(python3 -c 'from strap_asm import assemble
p = assemble(open("../decks/ibox1_vpic_chain.strap").read())
ha = lambda n: p.symtab[n] // 32
br = lambda t, c: ((ha(t) >> 1) << 14) | ((ha(t) & 1) << 13) | (c << 10)
chain = [("IBM9", "IBM11", 1), ("IBM11", "IBM15", 1), ("IBM15", "IBM21", 1),
         ("IBM21", "IBM19", 1), ("IBM19", "IBM27", 1), ("IBM27", "IBM23", 1),
         ("IBM43", "IBM45", 2), ("IBM45", "IBM47", 1), ("IBM47", "IBM49", 1),
         ("IBM49", "IBM51", 1), ("IBM51", "IBM53", 1), ("IBM53", "IBM55", 2)]
words = {}
for link, tgt, code in chain:
    w, half = ha(link) >> 1, ha(link) & 1
    base = p.words.get(w, 0)
    hi, lo = words.get(w, ((base >> 32) & 0xffffffff, base & 0xffffffff))
    words[w] = (br(tgt, code), lo) if half == 0 else (hi, br(tgt, code))
print(" ".join("W%o:%d=0x%016x" % (w, w, (words[w][0] << 32) | words[w][1])
               for w in sorted(words)))')
run "IBOX-1 V+IC chain (two phases: value, then count)" ./run_program.sh ../decks/ibox1_vpic_chain.strap StretchIbox1VpicChainTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/ibox1_vpic_chain.strap").read()).symtab["PASS"]//32)')" \
    $VPIC_CHECKS

run "IBOX-1 V+CR refill (ja_ax1a, encoding)" python3 verify_ibox1_vpcr_refill_listing.py
# V+CR's first test, the section immediately after V+C on the same page
# and the fifth of the eight confirmed-uncovered index operations.
#
# WHAT IS NEW, narrowly: V+ICR's refill is closed by ibox1_vpicr and
# V-ICR's by ibox1_vicr_chain, but both are IMMEDIATE.  This is the
# DIRECT-INDEX refill -- the arm whose operand half-word comes from
# storage (IBG59, value 4) rather than from the instruction.
#
# ALL THREE FIELDS OF THE REFILLED INDEX WORD ARE CHECKED, each by its
# own link: the value goes straight to IBG57, the count through ISTOY
# by SC/LV, and the refill through ISTOY by SR/LV.  The chain runs
# IBG57 -> IBG61 -> IBG58 -> IBG64 and every manufactured half-word is
# on it.
#
# MEASURED, and the deck predicted its own failure.  The listing
# annotates the two stores after the V+CR "IF NOT SV WILL BE B,IBG63"
# and "WHICH WILL CAUSE HANG UP".  With direct-index V+CR made never to
# refill, IBG57 comes out holding exactly B,003766.00 -- IBG63 -- and
# the run stops there, because IBG63's own first half-word (3766.04, a
# constant) decodes as a branch to itself.  The deck laid its constants
# out so that a failed refill lands on a self-branch.
VPCR_CHECKS=$(python3 -c 'from strap_asm import assemble
p = assemble(open("../decks/ibox1_vpcr_refill.strap").read())
ha = lambda n: p.symtab[n] // 32
bd = lambda n: ((ha(n) >> 1) << 14) | ((ha(n) & 1) << 13) | (0b001 << 10)
words = {}
for link, tgt in (("IBG57", "IBG61"), ("IBG58", "IBG64"), ("IBG61", "IBG58")):
    w, half = ha(link) >> 1, ha(link) & 1
    base = p.words.get(w, 0)
    hi, lo = words.get(w, ((base >> 32) & 0xffffffff, base & 0xffffffff))
    words[w] = (bd(tgt), lo) if half == 0 else (hi, bd(tgt))
print(" ".join("W%o:%d=0x%016x" % (w, w, (words[w][0] << 32) | words[w][1])
               for w in sorted(words)))')
run "IBOX-1 V+CR refill (direct index, all three fields)" ./run_program.sh ../decks/ibox1_vpcr_refill.strap StretchIbox1VpcrRefillTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/ibox1_vpcr_refill.strap").read()).symtab["PASS"]//32)')" \
    $VPCR_CHECKS

run "IBOX-1 V-IC chain (ja_ax1a, encoding)" python3 verify_ibox1_vic_chain_listing.py
# V-IC ("add to value immediate + count"), one of EIGHT modeled index
# operations a coverage screen found in ZERO of the 140 programs this
# file references -- the others V+C, V+CR, LVNI, LRI, KVNI, V+IC and
# V-ICR.  The screen is only sound for the ZERO side, and not even
# there on its own: these decks MANUFACTURE instructions at runtime by
# storing into instruction fields, which a static scan cannot see.  So
# it was confirmed by injection -- poisoning all eight at once left
# every section passing.
#
# THIS BLOCK CHECKS ITSELF COMPLETELY, which is unusual and is the
# contrast with ibox1_cmi_chain above.  IBP19 through IBP28 are ten
# branch-to-self half-words, and the four tests store over EIGHT of
# them: the value after each V-IC into one, and the count -- routed
# through ISTOY by SC then LV, which multiplies it by 64 and so turns a
# count into a word address, then V+ COM04 to set the branch opcode --
# into another.  All eight lie on the path IBP19 -> IBP26 -> IBP24 ->
# IBP22 -> IBP20 -> IBP28 -> IBP27 -> IBP23 -> IBP25 -> IBP21, so here
# "reaches the exit" really does mean all eight came out right, where
# for the C-I chain it meant nothing.  The word checks are kept anyway
# so a failure says WHICH link broke.
#
# IBP17 is the step worth having: V-IC subtracts a NEGATIVE immediate
# and V+I then adds one, so the count falls while the value rises --
# the two halves of the operation moving opposite ways.
#
# Measured, with the eight-op poison still in place: V-IC decrementing
# the count twice hangs the block on a branch-to-self (step cap) and
# reports every COUNT-path link wrong while W4611 -- the one word
# holding only a VALUE-path link, which the count cannot reach -- still
# passes.  A signature that specific is what makes the block diagnostic
# rather than merely red.
# The eight expected half-words are DERIVED, not written out: each link
# must hold a BD (branch code 001 at IBM bits 19-21, which is what
# COM04's +4 sets) to the link the listing's comments name.
VIC_CHECKS=$(python3 -c 'from strap_asm import assemble
p = assemble(open("../decks/ibox1_vic_chain.strap").read())
ha = lambda n: p.symtab[n] // 32
bd = lambda n: ((ha(n) >> 1) << 14) | ((ha(n) & 1) << 13) | (0b001 << 10)
chain = dict((("IBP19", "IBP26"), ("IBP22", "IBP20"), ("IBP23", "IBP25"),
              ("IBP24", "IBP22"), ("IBP25", "IBP21"), ("IBP26", "IBP24"),
              ("IBP27", "IBP23"), ("IBP28", "IBP27")))
words = {}
for link, tgt in chain.items():
    w, half = ha(link) >> 1, ha(link) & 1
    base = p.words.get(w, 0)
    hi, lo = words.get(w, ((base >> 32) & 0xffffffff, base & 0xffffffff))
    words[w] = (bd(tgt), lo) if half == 0 else (hi, bd(tgt))
print(" ".join("W%o:%d=0x%016x" % (w, w, (words[w][0] << 32) | words[w][1])
               for w in sorted(words)))')
run "IBOX-1 V-IC chain (self-modifying branch chain, V-IC)" ./run_program.sh ../decks/ibox1_vic_chain.strap StretchIbox1VicChainTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/ibox1_vic_chain.strap").read()).symtab["PASS"]//32)')" \
    $VIC_CHECKS

run "IBOX-1 V-ICR chain (ja_ax1a, encoding)" python3 verify_ibox1_vicr_chain_listing.py
# V-ICR, the companion of V-IC on the facing page and the second of the
# eight confirmed-uncovered index operations to be closed.
#
# WHAT IS NEW HERE is narrower than the block is long: SR already
# appears in ibox1_vpicr, ibox3_lr and ibox4_prog_ix_v, and V+ICR's
# refill is closed by ibox1_vpicr.  The new surface is V-ICR's own
# count-and-refill arm, driven BOTH ways -- one V-ICR that must refill
# and one that must not -- plus the IBP30-IBP32 trick, which has no
# parallel anywhere else in the suite.
#
# THAT TRICK IS THE REASON TO WANT THE BLOCK.  IBPA4 is not a constant,
# it is TWO INSTRUCTIONS sharing a word: a NOP and a B,IBP33.  IBPA3
# carries count 1 and refill IBPA4, so one V-ICR drives the count to
# zero, the refill reloads the index register FROM THAT WORD, and SX
# writes it straight over IBP31 where it is executed as the pair it
# always was.  An index word and an instruction pair are the same 64
# bits and the deck uses that identity as its test.
#
# Measured, and the signature is the deck's own: with V-ICR made never
# to refill, the run stops at PC 4894 -- octal 004617.00, which is
# IBP32, the half-word the listing labels "HANG UP" -- and IBP31 holds
# the un-refilled index word instead of IBPA4's.  The four chain links
# are then never stored at all.
VICR_CHECKS=$(python3 -c 'from strap_asm import assemble
p = assemble(open("../decks/ibox1_vicr_chain.strap").read())
ha = lambda n: p.symtab[n] // 32
bd = lambda n: ((ha(n) >> 1) << 14) | ((ha(n) & 1) << 13) | (0b001 << 10)
out = ["REFILLED_IBP31:%d=0x%016x" % (ha("IBP31") >> 1, p.words[ha("IBPA4") >> 1])]
for link, tgt in (("IBP46", "IBP49"), ("IBP49", "IBP50"),
                  ("IBP50", "IBP52"), ("IBP52", "IBP53")):
    w = ha(link) >> 1
    out.append("%s:%d=0x%016x" % (link, w, (bd(tgt) << 32) | (p.words.get(w, 0) & 0xffffffff)))
print(" ".join(out))')
run "IBOX-1 V-ICR chain (refill over a live instruction pair)" ./run_program.sh ../decks/ibox1_vicr_chain.strap StretchIbox1VicrChainTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/ibox1_vicr_chain.strap").read()).symtab["PASS"]//32)')" \
    $VICR_CHECKS

run "IBOX-1 LVNI (ja_ax1a, encoding)" python3 verify_ibox1_lvni_listing.py
# LVNI, load value negative immediate, and the seventh of the eight
# confirmed-uncovered index operations.  The smallest self-checking
# block in the suite: twenty half-words and no constants outside
# itself -- the V+ operand IBH39 is a BD,$ sitting INSIDE the block,
# used as data.
#
# It works BECAUSE the result is negative.  Each test loads minus an
# immediate, adds the one fixed positive half-word, and stores the sum
# over a branch-to-self; the four immediates (.32, 1.0, 1.32, 2.0) step
# the four sums DOWN by half-words, walking back through the chain
# IBH34 -> IBH38 -> IBH36 -> IBH37 -> IBH35 -> IBH40.  IBH35 is the one
# link never rewritten: the listing annotates it "REMAINS BD,IBH 40".
#
# "REACHES PASS" IS NOT A CHECK HERE, and this is the clearest case of
# that in the suite.  With LVNI made to load PLUS -- that is, made into
# LVI -- every sum comes out too large and IBH34 becomes a branch to
# 004312.00, which is IBH40, THE EXIT.  The block jumps past its own
# chain and halts normally: all three manufactured words are wrong and
# the PC check still passes.  Measured, not assumed, and the reason the
# word checks below exist.
LVNI_CHECKS=$(python3 -c 'from strap_asm import assemble
p = assemble(open("../decks/ibox1_lvni.strap").read())
ha = lambda n: p.symtab[n] // 32
bd = lambda n: ((ha(n) >> 1) << 14) | ((ha(n) & 1) << 13) | (0b001 << 10)
words = {}
for link, tgt in (("IBH34", "IBH38"), ("IBH36", "IBH37"),
                  ("IBH37", "IBH35"), ("IBH38", "IBH36")):
    w, half = ha(link) >> 1, ha(link) & 1
    base = p.words.get(w, 0)
    hi, lo = words.get(w, ((base >> 32) & 0xffffffff, base & 0xffffffff))
    words[w] = (bd(tgt), lo) if half == 0 else (hi, bd(tgt))
print(" ".join("W%o:%d=0x%016x" % (w, w, (words[w][0] << 32) | words[w][1])
               for w in sorted(words)))')
run "IBOX-1 LVNI (load value negative immediate)" ./run_program.sh ../decks/ibox1_lvni.strap StretchIbox1LvniTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/ibox1_lvni.strap").read()).symtab["PASS"]//32)')" \
    $LVNI_CHECKS

run "IBOX-1 KVNI (ja_ax1a, encoding)" python3 verify_ibox1_kvni_listing.py
# KVNI, compare value NEGATIVE immediate -- the sign-flipped twin of
# KVI (closed by ibox2_kv_kvi) and the sixth of the eight
# confirmed-uncovered index operations.
#
# FOUND BY THE MAP: ja_ax1a's routine list gives KVNI one line, "Same
# as KV", and because that list is in PROGRAM ORDER it placed the block
# between the C-I block (pp.38-39, ibox1_cmi_chain) and the KCI block
# (pp.40-41, ibox1_kci), both already transcribed.  One page render
# found it.
#
# Purely hang-based, like ibox1_kci: no SERS, nothing stored, every
# check a branch-to-self that must NOT be taken or a branch-forward
# that must be.  Three checks name the indicator that must be OFF (BXL,
# BXH, BXE) and three the one that must be ON in the branch-and-zero
# form (BZXEZ, BZXLZ, BZXHZ), so it separates "indicator set" from
# "branch on it and clear it".
#
# THE OPERANDS STRADDLE ZERO, which is the point of testing the
# negative form: the first group loads MINUS (1 in bit 0) and compares
# against +400000.0 expecting EQUAL -- a case only KVNI can pass,
# because the immediate is negated first.
#
# Measured: with the negation removed so KVNI behaves as KVI, the run
# halts at 004747.40 -- the FIRST check, the BXL the listing annotates
# "HANG UP IF LOW" -- because minus compares low against a positive
# immediate instead of equal.
run "IBOX-1 KVNI (compare value negative immediate)" ./run_program.sh ../decks/ibox1_kvni.strap StretchIbox1KvniTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/ibox1_kvni.strap").read()).symtab["PASS"]//32)')"

run "IBOX-1 KCI (ja_ax1a, encoding)" python3 verify_ibox1_kci_listing.py
# The listing's own COMPARE COUNT IMMEDIATE test, closing KCI.  Pure
# hang-based: every check is a branch that must or must not be taken.
# It pins the 18-bit immediate at both ends (all ones, one in bit 0,
# one in bit 17) and it runs "branch and leave the indicator on",
# "hang if it went off", "hang if it stayed on" three deep, which no
# other block in the suite does.  Measured: KCI forced to compare
# EQUAL always hangs at 004766.00, the "hang up if not XL" after
# IKCI2 -- the block asserts LOW there, so "always equal" is the way
# the injection has to point.
run "IBOX-1 KCI (compare count immediate, indicator reset)" ./run_program.sh ../decks/ibox1_kci.strap StretchIbox1KciTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/ibox1_kci.strap").read()).symtab["PASS"]//32)')"

run "IBOX-1 V-I (ja_ax1a, encoding)" python3 verify_ibox1_vmi_listing.py
# V-I as a DIRECT IMMEDIATE OPCODE -- not the "V-I" that is a
# progressive modifier on a VFL instruction, which ibox4_prog_ix_v
# already reaches through progressiveIndex().  Two facilities, one
# spelling; the distinction cost a wrong-way injection once.
# The block subtracts 777776.0 and adds 777777.0 back, so the
# sign-magnitude adder runs in both directions, and its last store is
# an SX of the whole index word over the pair IBP10/IBP11 -- the value
# half must be right AND the word must be stored whole.  Measured:
# V-I made a no-op leaves IBP13 branching to itself at 004562.40.
run "IBOX-1 V-I (subtract from value immediate, SX of the whole word)" ./run_program.sh ../decks/ibox1_vmi.strap StretchIbox1VmiTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/ibox1_vmi.strap").read()).symtab["PASS"]//32)')"

run "IBOX-1 V+ICR (ja_ax1a, encoding)" python3 verify_ibox1_vpicr_listing.py
# Closes V+ICR's REFILL path, the last of the five gaps that is not
# blocked.  The first test loads count 1, runs ONE V+ICR to take the
# count to zero, and stores the REFILLED word with SX over IBN1 --
# where it is then EXECUTED: IBM70's word is not an index word at all
# but "NOP,0" followed by "BD,IBN3", which is what the deck means by
# "IBN1 SHOULD NOW BE TWO VALID OP".  The refill has to deliver that
# word bit for bit, because the machine runs it.  The second test is
# the complementary case -- a V+ICR whose count does NOT reach zero --
# and checks value, count and refill through three SEPARATE
# manufactured branches.  The block is also a store-close-to-fetch
# test at distance two, which the deck's own comments name ("SPACE FOR
# STORE CLOSE TO" / "INSTRUCT FETCH INTERLOCK"); it passed first run.
# Measured: deleting the count decrement stops the refill firing and
# the machine spins on IBN1's untouched "BE,$" at 004526.00.
run "IBOX-1 V+ICR (refill, executed as two instructions)" ./run_program.sh ../decks/ibox1_vpicr.strap StretchIbox1VpicrTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/ibox1_vpicr.strap").read()).symtab["PASS"]//32)')"

run "IBOX-3 LR (jb_ax3a, encoding)" python3 verify_ibox3_lr_listing.py
# Closes LR, the last of the nine index operations the combined
# injection found unreachable -- and CORRECTS a claim: LR was recorded
# as blocked because I-Box 1's only LR test round-trips the refill
# through the indicator register, which this model keeps read-only.
# I-Box 3's routine 1230 tests the same operation with no indicator
# register in it at all.  A tape's test for an operation is not the
# only test for it.
# Each block runs the same LR three times -- from external memory, from
# index core storage ($X1, word 17) and from internal memory ($R,
# word 9) -- so an LR that worked only on real storage fails here.
# Measured: LR loading a zeroed half-word (the nine-way injection's own
# LR fault) halts at SERS, PC=1416.
run "IBOX-3 LR (load refill from all three memories)" ./run_program.sh ../decks/ibox3_lr.strap StretchIbox3LrTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/ibox3_lr.strap").read()).symtab["PASS"]//32)')"

run "IBOX-3 LRI (jb_ax3a, encoding)" python3 verify_ibox3_lri_listing.py
# Routine 1230's other half.  It is named "TEST LOAD REFILL AND LOAD
# REFILL IMMED."; ibox3_lr took the LR part from p.200 and left this.
# LRI was one of the eight confirmed-uncovered index operations.
#
# ONE TEST IS SIX HALF-WORDS and turns on the two IMMEDIATE FORMS being
# different: LVI,$X2,<n>. loads the expected VALUE (Ref. Manual p.25 --
# value operations take the address part shifted left five, so "<n>."
# is 64*n), LRI,$X0,<n> loads a bare count into the REFILL field, and
# SR then writes that 18-bit refill into bits 0-17 of a half-word,
# where reading it back as a 24-bit value multiplies it by 64 again.
# The same octal digits appear in both operands and KV still compares
# equal.  The deck is relying on exactly that difference lining up.
#
# THE WHOLE SWEEP IS HERE, all twenty tests, and the reason is measured
# rather than assumed.  This repository already found that bit sweeps
# are field-width tests whose value is at the two EDGES.  The refill
# field is IBM bits 46-63, and each edge catches only its own fault:
# LRI dropping bit 63 halts at SEN = 033177.40, the FIRST test, while
# LRI dropping bit 46 halts at SEN = 033262.40, the EIGHTEENTH.
# Neither injection is visible to the other end of the sweep, so taking
# a sample from one end would have left the other unpinned.
run "IBOX-3 LRI (refill immediate, every bit of the field)" ./run_program.sh ../decks/ibox3_lri.strap StretchIbox3LriTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/ibox3_lri.strap").read()).symtab["PASS"]//32)')"

run "IBOX-3 SVA into a floating-point instruction (jb_ax3a, encoding)" python3 verify_ibox3_sva_fp_listing.py
# SVA was setOpInvalid, which is what made I-Box 3, -4 and -5 usable
# only in slices chosen to avoid it.  This is the listing's own SVA
# test, and it found TWO things the Reference Manual does not say.
#
# (1) THE THIRD ADDRESS WIDTH IS FLOATING POINT.  p.29 gives "18, 19 or
# 24 bits" and attributes 18 only to TRANSMIT/SWAP second half-words,
# so SVA was first written with two widths.  The deck's error messages
# settle it: a DIRECT INDEX target that "FAILS TO STORE BIT 18" is
# broken, and an FP target that "STORES BIT 18" is broken.  FP's
# address is 18 bits (a/b/c modifiers at 18-20); every other
# half-length format has 19.
#
# (2) AN INDEX REGISTER MUST ROUND-TRIP ALL 64 BITS.  packIndexWord
# wrote 2'b00 into IBM bits 26-27, so LX-then-SX rewrote them.  The
# deck's comment names the dependency -- "A FP INSTRUCT BITS 26 AND 27
# OF WHICH ARE 10" -- and with them zeroed the template decoded as a
# branch-on-indicator, SVA used 19 bits, and "STORES BIT 18" fired.
# Confirmed by reading back what SIC recorded (SEN = 030342.40, the
# fourth of the block's six checks) before the fix.
#
# Measured: SVA made a no-op halts at the FIRST check, "fails to store
# any bits in 0-17" (SEN = 030330.40).
run "IBOX-3 SVA into a floating-point instruction (18-bit address field)" ./run_program.sh ../decks/ibox3_sva_fp.strap StretchIbox3SvaFpTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/ibox3_sva_fp.strap").read()).symtab["I2234"]//32)')"

run "IBOX-3 SVA into a direct index instruction (jb_ax3a, encoding)" python3 verify_ibox3_sva_dix_listing.py
# The 19-bit half of the width rule, and the reason both blocks are
# here: they are the SAME SIX CHECKS with two comparisons reversed.
# After storing a lone bit 18 and comparing against I22K3D, the FP
# target must be LOW (bit 18 not stored) and this one must be HIGH
# (bit 18 stored).  Neither block alone establishes the rule.
# The target is $X3 -- word 19, index core storage -- so this also
# covers SVA writing a half-word into a register word rather than into
# ordinary memory.
# Measured: forcing the 18-bit rule for every class halts this block at
# its fourth check, "fails to store bit 18" (SEN = 030311.40).  That
# injection cannot affect the FP block, whose target already decodes as
# Fp and so takes the same arm either way -- which is why the pair is
# what pins the two widths, and why only this half of it was run.
run "IBOX-3 SVA into a direct index instruction (19-bit, into a register)" ./run_program.sh ../decks/ibox3_sva_dix.strap StretchIbox3SvaDixTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/ibox3_sva_dix.strap").read()).symtab["I2230A"]//32)')"

run "IBOX-3 SVA into a full-word instruction (jb_ax3a, encoding)" python3 verify_ibox3_sva_full_listing.py
# The THIRD width, 24 -- and the one neither other block could reach.
# Both of their templates are half-length (I22K2 op 0x60, I22K4 op
# 0x30), so dirIndexOp's `instrLen(h) == Full` arm was implemented from
# Ref. Manual p.29 alone and driven by nothing at all.  Measured both
# ways: with that arm forced to the 19-bit path the other 274 sections
# ALL still pass, and this one halts at SERS on its first check with
# SEN = 030176.00, "SVA above bit to ext mem failed".
#
# The listing also STATES the whole width rule, which p.29 does not.
# The comment block closing the series (p.140) gives the machine's own
# length tag, read outward from bit 27:
#   bit 27 = 1         direct index 19    bits 24-27 = 1000   full wd  24
#   bits 26-27 = 10    FP           18    bits 23-27 = 10000  immed ix 19
#   bits 25-27 = 100   CB/BIND      19    bits 23-27 = 00000  misc     19
# Those six patterns partition bits 23-27 exactly, so it is a decision
# and not a priority order, and decodeHalfWord agrees case for case.
# The trio is now tight in both directions: this block fails if SVA
# stores too FEW bits for a full word, and the direct-index block's
# sixth check ("store some bits in 19-23") fails if it stores too many.
#
# Two data bits, 22 and 23, both above a 19-bit field, each stored to
# all three memories -- I22WRK (external), $R (word 9, internal) and
# $X1 itself (word 17, index core storage).  $R is the one path of the
# three that no earlier SVA block covers.
run "IBOX-3 SVA into a full-word instruction (24-bit, three memories)" ./run_program.sh ../decks/ibox3_sva_full.strap StretchIbox3SvaFullTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/ibox3_sva_full.strap").read()).symtab["I2221A"]//32)')"

run "Program store compare: store then EXECUTE the modified instruction" ./run_program.sh ../decks/store_then_execute.strap StretchStoreExecTb \
    "RESULT:$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/store_then_execute.strap").read()).symtab["RESULT"]//64)')=0x20"

# -- 1j. Store-close-to-fetch: store a word then immediately reload it;
# the load must read the new value, not the stale one. The hazard the FP
# sign-modifier codesign exposed; fixed by tracking each E-box level's
# store target (plan stage 3a note). This exact pattern failed before.
run "Look-ahead: store-close-to-fetch" ./run_scf_test.sh

run "I-Box 5 routine 1260 TEST 7: upper-boundary data, bit-exact (jb_ax5b p.65)" python3 verify_ax5b_16099_listing.py
run "I-Box 5 routine 1260 TEST 7 ON THE MODEL (all 18 boundary bits)" ./run_program.sh ../decks/ax5b_16099_ub_data.strap StretchAx5b16099Tb \
    "PC=18730"         # 022225.00, where the listing continues
# THE DRIVER docs/NEXT.md ASKED FOR, found 2026-09-23.  Item 1 warned
# that "pp.66-79 were GUESSED to hold the positive boundary-interrupt
# cases" -- a scouting pass's inference, not a page -- and said FIND
# THE DRIVER BEFORE TRANSCRIBING.  Scanning pp.46-86 for BOUND/MONITOR
# and reading the hits gives the real layout:
#
#   p.65  "TEST 7 CHKS BOUNDARY CONTROL." / "CHK UPPER BOUNDARY DATA."
#         <- this block, driver at I6099/I60100
#   p.67  "CHK LOWER BOUNDARY DATA." and "CHK BOUNDARY CONTROL BIT."
#   p.71  "FETCH FROM X-1 TO CHK UB COMP." / "FROM X-3 TO CHK LB COMP."
#         <- the COMPARISON tests, i.e. the positive address-monitoring
#            cases the plan was actually after
#
# So pp.65-70 test whether the REGISTERS HOLD THEIR BITS and p.71 tests
# whether the comparison FIRES.  The guess was wrong in range and kind.
#
# THE BLOCK is eighteen iterations, because the upper boundary is word
# 3 bits 0-17 -- exactly eighteen bits.  Write BIT<n> into $UB, four
# NOPs (the deck's own spacing), read back, KV, and on mismatch branch
# into the per-bit error table I60B17 INDEXED by $X3, which steps by
# 1.32 because each entry is three half-words.
#
# IT CATCHES A BOUNDARY FAULT AND NAMES THE BIT.  StretchStorage.bsv
# holds word 3 in a dedicated register, so dropping one bit of it is
# precisely the fault this block hunts.  Injecting
#   addrUpperBoundary: boundaryReg <= (v & ~(64'b1 << 46));
# -- IBM bit 17 -- halts at 022263.00, the table's EIGHTEENTH entry,
# "UPPER BOUNDARY DATA FAILURE, BIT 17".  Clean it halts at PASS.
#
# AND THE TABLE'S SIZE IS LOAD-BEARING.  A first version collapsed the
# eighteen entries into ONE hang; the bit-17 injection then branched
# past its end into untouched storage, decoded BE,0 (NEXT.md's trap
# list) and ran the counter to 0 -- caught, but unable to say WHICH
# bit.  Keeping the deck's shape is what turns "something broke" into
# "bit 17 broke".
#
# Encoding injections, observed, one row each: LCI's immediate-index
# code (022215.40), KV's direct-index code (022222.40), XE's indicator
# number (022223.00).

run "I-Box 5 routine 1260 TEST 7: lower boundary + control bit (jb_ax5b p.68)" python3 verify_ax5b_160102_listing.py
run "I-Box 5 routine 1260 TEST 7b ON THE MODEL (18 LB bits + control bit)" ./run_program.sh ../decks/ax5b_160102_lb_ctl.strap StretchAx5b160102Tb \
    "PC=18830"         # 022307.00, where the listing continues
# THE REST OF TEST 7, from p.68 -- the other register and the control
# bit.  The upper half is the section above.  The lower loop mirrors it
# with three differences: it stores through $LB (word 3 bits 32-49),
# indexes its error table with $X2, and that table is I60B18 at
# 022313.40, whose entries pp.69-70 print as "LOWER BOUNDARY DATA
# FAILURE, BIT 32" upward.
#
# THE CONTROL-BIT TEST is the neat one.  Word 3 bit 57 is the boundary
# control bit (p.31: it "determines which condition will cause an
# address monitoring signal").  The deck sets it from BIT57, reads word
# 3 back, moves the refill field with "SR,$X1,$X1", and compares
# against BIT11 -- because bit 57 sits at refill position 57-46 = 11.
# Then "Z,$UB" clears it and it compares against I00Z.
#
# IT LOCALISES A FAULT TO THE BIT, both halves, addresses computed
# BEFORE the runs and both hit:
#   drop IBM bit 49 (bottom of the lower boundary)
#       -> 18890 = 022313.40 + 17*1.32, the table's "BIT 49" entry
#   drop IBM bit 57 (the control bit)
#       -> 1416 = 001304.00 = SERS, via the first BZXE,
#          "UNABLE TO SET BNDRY CNTRL TO 1."
#
# AND A LIMIT WORTH KNOWING, found by trying the obvious encoding
# injection and watching it SURVIVE.  Moving $LB within its half-word
# -- (3,32) -> (3,33), (3,40), even (3,63) -- fails nothing.  A
# direct-index address is 19 bits: an 18-bit word plus a ONE-BIT
# half-word select, so the offset inside the half-word is not encoded.
# (3,31) and (4,32) do fail.  So this oracle pins $LB to word 3's
# second half-word and no further; that bits 32-49 specifically are the
# lower boundary comes from the pocket card and p.31.
#
# A FOURTH CONFIRMATION OF THE BIT TABLE: BIT57 prints 24613, BIT11
# prints 24535, and 024522 + 57 = 024613, 024522 + 11 = 024535.

run "BEW and SIC-BEW, bit-exact (ja_ax1a p.58)" python3 verify_ax1a_bew_listing.py
# THE HALT IDIOM, FINALLY CHECKED AGAINST A LISTING.  Every program in
# this suite ends with "BEW, $" and nothing here had ever checked BEW's
# encoding against printed machine code.  The SIC prefix ON a BEW is a
# combination no other transcription covers.  31 rows, ja_ax1a p.58's
# "%BEW% **** BRANCH ENABLED + WAIT" and "%SIC-BEW% **** STORE IC IF
# BRANCH ENABLED + WAIT" blocks.
#
# AND IT CORRECTS docs/NEXT.md, which said this block drove BEW "from
# the interval timer and fall through".  It does not.  Reference Manual
# printed p.40: "The interruption mechanism is enabled, and the
# instruction counter contents are replaced with bits 0-18 of the
# effective address of the operation as in BRANCH ENABLED.  However, no
# further instruction will be executed until after an interruption
# occurs."  BEW BRANCHES and then waits, and the listing agrees -- the
# "BD,$" after each BEW sits at the FALL-THROUGH address, the hang a
# machine that failed to branch would reach:
#
#   ISBE37  BEW,ISBE38   6031.60 00   at 006030.40
#           BD,$         6031.04 00   at 006031.00
#   ISBE38  BD,$+.32     6032.04 00   at 006031.40
#
# 0o60 has bit 18 set, so the target is 006031.40 -- two half-words
# past the hang.
#
# ENCODING ONLY, AND DELIBERATELY NOT RUN.  Because BEW always
# branches, control reaches the target whether the WAIT is modelled or
# not, so no arrangement of these rows could witness it.  Seeing the
# wait needs an instruction at the target that must not execute until
# an interruption arrives, and the only source of one here is the
# interval timer -- which this model does not tick (bsv/README.md
# scope).  That is why all four blocks load $IT first.  Recorded so the
# section is not mistaken for evidence about the wait.
#
# Four injections, each naming a DIFFERENT set of rows:
#   BEW's code 0b100 -> 0b101  -> 006030.40, 006033.40, 006037.00,
#                                 006042.00, 006045.40      (5 rows)
#   BE's  code 0b000 -> 0b010  -> 006030.00, 006033.00, 006036.40,
#                                 006041.40, 006044.40      (5 rows)
#   NOP's code 0b110 -> 0b111  -> 006034.40                 (1 row)
#   enc_sic's literal 1000     -> 006045.00                 (1 row)
#
# THE FIRST RUN OF THOSE WAS WRONG, and is recorded because the failure
# mode is silent.  Without clearing __pycache__ between injections all
# three reported the SAME five rows -- the first injection's answer,
# replayed from stale bytecode, since cp-restore within one second
# leaves the .pyc newer than its source.  The tell was a restored tree
# that still failed while "git diff" showed nothing.

run "I-Box 5 routine 1260 TEST 6: the free instruction and the I-Box indicators (jb_ax5b PDF pp.61-64)" python3 verify_ax5b_160_test6_listing.py
# THE LARGEST SINGLE TRANSCRIPTION IN THIS REPO: 159 rows, 182
# half-words, 022062.00-022214.40, one unbroken run, TEST 6 header to
# continuity update.  Header: "-TEST 6 CHKS THAT FREE INSTRUCTION / -IS
# IN FACT FREE, AND THAT I-BOX / -INDS SET ONLY CORRECT INDS."
#
# ITS FIRST OUTPUT LINE IS A TILING ASSERTION, "TILING OK: 159 rows,
# 182 half-words", and that is not decoration.  check_rows reads each
# listed location independently, so it would never notice a MISSING
# row.  At this size that matters more than at twenty.
#
# THE MEASURED NULL IS THE MOST VALUABLE THING IN THE BLOCK.  Injecting
# INDICATOR_BITS["XCZ"] 48 -> 49 fails ZERO rows.  The reason is
# arithmetic: XCZ, XVLZ, XVZ, XVGZ, XL and XH never reach the encoder
# here at all -- they appear only inside hand-written octal immediates
# on the KVI rows, which the assembler takes as literals.  The only
# index indicator this block ENCODES is XE, on its BXE/BZXE rows.
#
# SO A TEST WHOSE WHOLE SUBJECT IS SEVEN INDEX INDICATORS IS A LISTING
# WITNESS FOR THE NUMBERING OF EXACTLY ONE OF THEM.  The other six rest
# on Figure 11 (printed p.43), not on these pages.  Anyone tempted to
# call 159 green rows broad coverage of the index indicators should read
# that sentence first; it is the caveat the transcriber most wanted
# carried forward, and no amount of row count substitutes for it.
#
# Seven injections, observed.  The two bit-18 mask injections are
# deliberately tiny and that IS the design: only rows whose branch
# target is a ".40" half-word can move, and almost everything here aims
# at ".00" or carries address 0 (the NOPs).
#   DIR_INDEX_CODES["SR"] bit 23        16 rows (octal pair)
#   MISC_CODES["NOP"] 0b110 -> 0b010    27 rows -- every NOP
#   branch-on-indicator addr19 & ~1      1 row
#   uncond-branch/misc addr19 & ~1       2 rows
#   INDICATOR_BITS["XE"] 53 -> 52       15 rows, HEX BYTE ONLY; the
#       octal pair does not move at all
#   IMM_INDEX_CODES["KVI"] 0100 -> 0101 15 rows -- every KVI
#   INDICATOR_BITS["XCZ"] 48 -> 49       MEASURED NULL, see above
#
# THE DECK'S OWN SPELLINGS ARE KEPT, all read at 600 dpi: "-XVGV" at
# 022123.00 where the error two rows later says "-XVGZ NOT SET
# CORRECTLY."; "XVD" at 022135.00, which is not an indicator at all
# (XVZ is meant); and "-XL AND XH NOT CLRD OK" at 022203.00, the only
# message in the block with no terminal period.
#
# TWO CLEAR-GROUP COMMENTS UNDERSTATE THEIR OWN CONSTANT: "-CLR XVLZ
# AND XVZ." (617777) and "-CLR XVLZ AND XVGZ." (627777) both also have
# bit 2 clear, i.e. XCZ cleared too.  The constants are right for the
# hardware; the comments just do not list it.
#
# THE NOPS ARE CONJECTURE AND LABELLED AS SUCH.  Most groups put two
# between the SR and the KVI; two groups have none; and nothing a NOP
# can do could change what the KVI reads (printed p.40: NO OPERATION's
# "address and index fields are not interpreted, so they cannot cause
# any indicators to be actuated").  That they are the "free instruction
# ... in fact free" of the header is a plausible reading, not a sourced
# one, and the two groups without them show they are not structurally
# required.
#
# The transcriber cut ELEVEN SOURCE LINES EARLIER than asked, at I6096
# rather than I6098, and gave the reason: cut at I6098 the block
# contains NO label reference that is not a SYN -- zero genuine internal
# address witnesses.  Extending back buys two real ones, a forward
# reference 18 half-words long and a backward one 175 half-words long.

run "I-Box 5 routine 1260 TEST 8B: DS disabled/enabled + store suppression (jb_ax5b PDF p.75)" python3 verify_ax5b_160_test8b_listing.py
# A SECOND, RICHER DS ORACLE than the transcribed I6086 block, and the
# acceptance test for the half of DS this suite calls suppression.
# 52 rows.  Header: "-TEST 8B CHKS DS WITH SYSTEMS / -DISABLED, AND
# ENABLED."  Its three error messages are the contract:
#   "-SX OUT OF BOUNDS SETS DS WHEN / -SYSTEM DISABLED."
#   "-NO INTERRUPT OCCURED ON AN / -SX ABOVE UB."      [sic, one R]
#   "-SX ABOVE UB WAS NOT NOPED, DATA / -WAS STORED WHEN ENABLED."
#
# THE LAST ONE IS THE POINT.  The enabled half stores above the upper
# boundary and then does "L(BU),I60AD1" + "BRZ,$+1.32", demanding the
# target still read ZERO.  IBM's own suite requires the store to be
# NOPED, not merely flagged -- which is the observable Figure 11 (p.43)
# calls Class S.  See docs/NEXT.md 5a.
#
# TWO ENCODINGS NO LISTING HERE HAD WITNESSED: "BZDSZ" and "BRZ".  BRZ
# matters as PROVENANCE -- indicator RZ = 57 reached this project from
# the IBM 7030 Reference Card's "INDICATOR LIST" via
# bsv/StretchTypes.bsv, whose 48-63 run cites that card and nothing
# else.  No deck listing had confirmed it until these two rows.
#
# Six injections, observed.  The last two exist because the first four
# all mutate opcode or modifier fields and NONE touches bit 18:
#   INDICATOR_BITS["DS"] 19->18            -> 2 rows
#   INDICATOR_BITS["RZ"] 57->56            -> 2 rows
#   DIR_INDEX_CODES["SX"] one bit          -> 6 rows
#   MODE_DEFAULT_BS["BU"] 8->4             -> 2 rows (the two L(BU)s)
#   uncond-branch addr19 mask, bit 18 -> 0 -> 3 rows
#   branch-on-indicator addr19 mask, same  -> 3 rows
# Those six rows are exactly the block's ".40" targets; every ".00"
# target is untouched, which is the bit-18 rule measured from the one
# direction the opcode injections cannot reach.

run "I-Box 5 routine 1260 TEST 8C: the DF/IF deck oracle (jb_ax5b PDF pp.80-83)" python3 verify_ax5b_160_test8c_listing.py
run "I-Box 5 routine 1260 TEST 8C cases 1-2: the DISABLED controls (jb_ax5b PDF pp.76-78)" python3 verify_ax5b_160_test8c_disabled_listing.py
# THE OTHER HALF OF TEST 8C, and it settles a discrepancy this suite
# recorded as open.  114 rows, cases 1 and 2 contiguous.
#
# THE HEADER'S LINE 1 IS A TYPO.  It reads "-1. DISABL MASK 0 FETCH OK
# IND NO INT" where the CODE requires the indicator NOT set.  Four
# independent lines of evidence: (1) cases 1 and 2's indicator branches
# are BIT-IDENTICAL in polarity -- BZDFZ prints "...12 44"/"...52 44"
# and BZIFZ "...12 C4" in both -- so whatever BZ means, the two cases
# assert the SAME thing, and "IND" cannot be right unless line 2's "NO
# IND" is also wrong; (2) the failure text inverts only at case 3,
# which prints "-CAUSES DF NOT TO BE SET" where 1 and 2 print "-CAUSES
# DF TO BE SET"; (3) the grammar B[Z]<ind>[Z] makes the leading Z
# branch when the indicator is OFF, and here the branch is the OK path;
# (4) line 2 of the same header spells DISABL as "DIAABL".
#
# AND THE DISABLED CASES ARE NOT REDUNDANT WITH EACH OTHER.  Disabled,
# the deck asserts the mask bit is IRRELEVANT: case 2 sets DF's AND
# IF's mask bits to ONE and still demands the fetch proceed ("-UNABLE
# TO FETCH ABOVE UB WITH / -MASK 1, SYSTEM DISABLED."), where case 4 --
# enabled, mask 1 -- demands the same fetch be SUPPRESSED.  That pair
# is the enable gate stated from both sides, and it is the rule the
# model's protViolates leans on.
#
# CNOP IS INVERTED RELATIVE TO CASES 3/4.  Here case 1 emits the filler
# NOP (at 022567.40) and case 2 emits nothing; in cases 3/4 the earlier
# case was the silent one.  Measured inside a single injection: mutating
# NOP's code fails THREE rows -- the two written NOPs AND case 1's CNOP
# filler -- while case 2's CNOP contributes nothing at all.
#
# Four injections, observed:
#   INDICATOR_BITS["IF"] 21->22  -> 022571.00, 022627.00        (2 rows)
#   INDICATOR_BITS["DF"] 20->19  -> 022556.40, 022614.00        (2 rows)
#   UNCOND_BRANCH_CODES["NOP"]   -> 3 rows, incl. the CNOP filler
#   UNCOND_BRANCH_CODES["BD"]    -> 11 rows (every BD in the block)

# THE DECK ORACLE FOR DF AND IF -- and finding it corrected a claim
# this project had already built on.  docs/NEXT.md and
# archival_inventory.md both said "DF and IF have no deck oracle
# anywhere read so far".  DF was then implemented from Reference Manual
# p.32 alone, to the weaker standard, while THIS test sat thirty pages
# earlier in a document already read.
#
# HOW THE FALSE CLAIM GOT THERE, because the shape recurs: this file
# correctly disproved that routine 1268 was the oracle -- 1268 is a
# look-ahead forwarding test -- and then wrote "so DF and IF have no
# deck oracle anywhere", which does not follow, and nothing re-checked
# it.  A correction that retracts the REASON for a claim must retract
# the claim or re-derive it.  Fourth instance of "distrust a blocker
# recorded in this file", and the first where the blocker had already
# been corrected once.
#
# TEST 8C's own title, PDF p.76 at 022546.00:
#   I60127 LVI,$X1,I60AD1  -TEST 8C CHECKS DF + IF UNDER 4 CONDS,
#                          -1. DISABL MASK 0 FETCH OK IND NO INT
#                          -2. DIAABL MASK 1 FETCH OK NO IND NO INT
#                          -3. ENABLE MASK 0 FETCH OK IND ON NO INT
#                          -4. ENABLE MASK 1 NO FETCH IND ON INTRPT
#
# CASES 3 AND 4 ARE THE MASK-DEPENDENT PAIR, which is why these two and
# not the disabled controls.  Both enable; case 3 runs mask 0 and case
# 4 mask 1, which is exactly p.32's rule.  Their error messages are the
# contract read against each other -- case 3 fails with "WAS NOPED" (it
# must have fetched), case 4 with "WAS EXECUTED" (it must not have).
# That is the oracle for the mask-dependent half this suite records as
# unimplemented.
#
# CNOP IS ALIGNMENT-DEPENDENT and is the trap in this block.  On p.80
# the preceding BE sits on a .40 half-word, the next is already
# word-aligned, and CNOP emits NOTHING -- the address column steps
# straight from 022662.40 to 022663.00.  On p.82 the BE sits on .00 and
# CNOP emits a filler NOP at 022722.40.  Case 3 is 56 source lines / 55
# code rows; case 4 is 56/56.  The assembler reproduces both from the
# same source line, so the program keeps CNOP rather than expanding it.
#
# FOUR MORE CONFIRMATIONS OF THE BIT TABLE (024522 + n): BIT14, BIT20,
# BIT21, BIT57.  And because the deck sets mask bit 20 for the DF half
# and mask bit 21 for the IF half, this block is the DECK'S OWN
# statement that DF is indicator 20 and IF is 21 -- numbering this
# project had taken from the manual.
#
# ENCODING ONLY: running it needs SSIP's I60S1/I60SX1, the 64-word
# table at I60IT, and IF, which this model does not implement at all.
# This is IF's acceptance test, waiting for IF.
#
# Three injections, and the third was PREDICTED WRONG, which is kept
# because it is the CNOP point in miniature:
#   INDICATOR_BITS["IF"] 21 -> 22  -> 022664.00, 022724.00     (2 rows)
#   INDICATOR_BITS["DF"] 20 -> 19  -> 022651.40, 022710.40     (2 rows)
#   p.82 CNOP -> NOP               -> NOTHING.  There CNOP already
#                                     emits a NOP, so it is the same
#                                     program.
#   p.80 CNOP -> NOP               -> 72 rows: it emits nothing there,
#                                     so a hand-written NOP inserts a
#                                     half-word and shifts four labels
#                                     and every row after it.

run "I-Box 5 routine 1262 TEST 1CA/1CB: the two disabled-state exceptions (jb_ax5b PDF p.92)" python3 verify_ax5b_162_test1cab_listing.py
# **THE ORACLE, WRITTEN BEFORE THE IMPLEMENTATION**, the way
# ax5b_16071_ts.strap was.  27 rows, 023442.40-023460.00, abutting the
# TEST 1B section with nothing between.  These two blocks are the deck
# test for printed p.50's two exceptions that OVERRIDE THE DISABLED
# STATE -- 1CA for "interruption is always permitted at the completion
# of an execution operation", 1CB for "address monitoring is always in
# force during EX and EXIC".  Neither is implemented yet; see
# docs/execution_operations.md.
#
# THE "-ILLEGAL OP CODE." WORD PLAYS A **THIRD** ROLE HERE, and this
# project has now seen the same 00000003740 word do three different
# jobs.  In TEST 1CC it is an ENABLE-STATE PROBE, used twice in
# opposite polarities.  In TEST 3A/3B it is a HIGHER-PRIORITY DECOY
# that protects AD from being consumed by the interruption.  Here it is
# a **PRE-CHARGE**: it actuates OP in passing while the system is
# disabled, so that the EX's completion boundary has something to
# deliver.  Three prongs, in order of strength: the deck's own error
# text says so ("-NO INT TAKEN ON EX / -WHEN OP SET." asserts OP was
# ALREADY set); the interrupt vector is planted AFTER the illegal word,
# so if it could interrupt where it stands the block would break rather
# than report; and nothing between it and the EX clears OP.
#
# AND THE EX's SUBJECT IS SETTLED FROM THE PRINT, not from the shape of
# the neighbouring block.  023447.00 prints "23446.52 00" -- pair 52 =
# 101010, bit 18 = 1 -> 023446.40, which is the SVA, not the illegal
# word three half-words back.  Better than "a subject chosen to do
# nothing": the subject is provably IDEMPOTENT, because nothing between
# 023446.00 and 023447.00 touches $X1, so re-executing the SVA stores
# the same address into the same word.
#
# THE BLOCK IS DISABLED, on three independent grounds from its own
# rows, and the third is the cleanest: both SVAs name I62ITE with NO
# "+.32", so the landing is 024320.00, which p.109 prints as "BD,$".
# 1CB is therefore entered STILL DISABLED and needs no BD of its own --
# and it has none.
#
# THE MASK ASYMMETRY IS THE POINT, and it corrects a reading in the
# research note.  1CA does "Z,$IND" and NO mask setup; 1CB must run
# "TI,1,I00O,$MASK".  The reason is printed p.48: mask bits 0-19 are
# permanently one, and **OP is indicator 15 while IF is 21**.  I00O is
# the ALL-ONES word, so that TI turns on every settable bit 20-47, not
# "the relevant one".
#
# THE STAR IS A MATCHED BIT-18 PAIR INSIDE 28 HALF-WORDS: the two EX
# rows print pair 52 (bit 18 = 1) and pair 12 (bit 18 = 0).  And
# injection 2 makes it falsifiable -- masking bit 18 off every branch
# and misc address moves EXACTLY ONE row, 023447.00, while 023455.00
# sits there as the control.  Note 023455.00's pair reads identically
# whether the field is 19 bits or 18; 023447.00's does not.
#
# Five injections plus a MEASURED NULL WITH A LIVENESS PROOF under the
# same patched build: indexing enc_dir_index moves nothing here (no
# parenthesised index in 27 rows), while a constructed
# "SX,$X2,I00O($X1)" moves 024503.05 11 -> 12 and its unindexed twin
# does not.
#
# ONE REPO FIRST after grep knocked the rest down: "EX,$-.32" is the
# first SELF-RELATIVE EX and the first BACKWARD one -- every other EX
# operand anywhere in the corpus is a label or a register.
#
# NO DECK TYPO AND NO SCAN DAMAGE in 27 rows.  The one candidate was in
# the READING, not the deck: see docs/listing_typography.md 10 on rule
# lines forging serifs.  "CNTRLS" got the pitch test and is an
# abbreviation, not a dropped letter -- six consecutive cells at 60.6
# px with no blank.

run "I-Box 5 routine 1262 TEST 1CC: EX of a branch, and EXE (jb_ax5b PDF pp.93-94)" python3 verify_ax5b_162_test1cc_listing.py
# THE SPECIFICATION FOR THE **EXE** INDICATOR, as executable checks.
# Reference Manual printed p.49: "The execution exception indicator
# (EXE) is turned on by any branch operation of a subject instruction
# in which the condition for a successful branch is met.  When
# indicator EXE is actuated, the branch and all associated operations
# are not performed.  The suppressed actions include the disabling in
# BRANCH DISABLED, the enabling in BRANCH ENABLED or BRANCH ENABLED
# AND WAIT, the counting and refilling in COUNT, BRANCH AND REFILL."
# 81 rows, FOURTEEN error entries.
#
# BUT ONLY THREE OF THAT PARAGRAPH'S CLAUSES ARE WITNESSED HERE -- BE,
# BD and BB.  There is no COUNT-BRANCH-AND-REFILL subject and no BEW
# subject anywhere in 1CC, so the counting-and-refilling suppression
# is stated by the manual and left UNWITNESSED by the deck.  Worth
# knowing before implementing it.
#
# AND IT RETIRES AN OPEN QUESTION FROM TEST 3A.  That block records an
# unexplained "-ILLEGAL OP." data word standing in the straight-line
# instruction path.  1CC shows what it is: a PROBE FOR THE ENABLE
# STATE.  An invalid operation code sets OP, which is permanently
# masked on, so executing one interrupts IF AND ONLY IF the
# interruption system is enabled.  1CC uses the same word twice in
# OPPOSITE polarities and the neighbouring error text proves the
# reading -- after EX of a BE whose enabling must have been suppressed
# the probe must NOT interrupt ("-SYSTEM ENABLED AFTER EX OF / -A BE
# INSTRUCTION."), and after a real BE followed by EX of a BD whose
# disabling must have been suppressed it MUST ("-SYSTEM DISABLED AFTER
# EX OF / -A BD INSTRUCTION.").
#
# THE INTERRUPT VECTOR IS A 64-ENTRY TABLE FILL, not a single write.
# I62K1 = "BD,I62ITE" and I62K6 = "B,I62ITE+.32" are each a full word
# holding the same half-word branch twice; I62ITE is a full word of two
# self-loops, "BD,$" at .00 and "B,$" at .40.  A loop fills all 64
# table words with one or the other, so WHICH HALF an interruption
# lands on is what the constant chooses: I62K6 leaves the system as it
# found it, I62K1 lands with it disabled.  SVA then plants the handler
# address in the matching half, rewriting only the address part so the
# landing keeps its own B or BD.
#
# Five injections, observed, chosen to move DIFFERENT printed columns:
#   UNCOND_BRANCH_CODES["BE"]  -> 1 row, octal pair only
#   BB_CODES["BB"]             -> 2 rows, hex byte only
#   MISC_CODES["EX"]           -> 4 rows (more EX than the rest of the
#                                 repo together)
#   CB_CODES["CB+"]            -> 2 rows, hex byte
#   DIR_INDEX_CODES["SX"]      -> 2 rows, hex byte
# The two BB rows also exercise BOTH of listing_oracle.word_at()'s
# full-word paths: one is an odd half-word whose instruction straddles
# two words, the other is not.

run "I-Box 5 routine 1262 TEST 3A: EXIC's illegal pseudo-IC (jb_ax5b PDF pp.107-108)" python3 verify_ax5b_162_test3a_listing.py
run "I-Box 5 routine 1262 TEST 3B: EXIC subject below 32 (jb_ax5b PDF p.108)" python3 verify_ax5b_162_test3b_listing.py
# THE SECOND HALF OF ONE REFERENCE MANUAL PARAGRAPH.  TEST 3A checks the
# pseudo-IC rule; 3B checks the sentence right after it, printed p.50:
# "Subject instructions of EXECUTE INDIRECT AND COUNT may occupy any
# available locations with addresses 32.00 and greater."  32 rows,
# 024151.40-024171.00, three error entries, all on PDF p.108.
#
# AND A TYPOGRAPHIC TRAP IN THE SOURCE PDF worth knowing before anyone
# reads that page: the right column of PDF p.53 OPENS with "15.  Subject
# instructions of ..." where the "15." is the TAIL of the left column's
# last sentence, not a list number.  A skimming reader mis-parses it as
# item 15 of a numbered list and loses the paragraph it belongs to.
#
# THREE ADDRESS WITNESSES, NONE ADJACENT TO THE SLC -- better anchored
# than 3A, because TEST 3B's first row carries no label.  I62104
# (024157.40) is twelve half-words downstream and IC262 (024171.00)
# thirty-one, and IC262's CONTENT is all zeros so only its address
# witnesses anything; the file says so rather than counting the row.
#
# Seven injections, observed.  The last is the only one outside
# opcodes.py and the only one that tests the block's headline claim:
#   strap_asm.eval_system_symbol index base (16+n)*64 -> (17+n)*64
#       -> 3 rows.  The FIRST $X1 of "LX,$X1,$X1" does NOT move -- it is
#          a J field (reg_context=True), not an address.
#   INDICATOR_BITS["XE"] 53 -> 52
#       -> 1 row, OCTAL PAIR UNCHANGED at 32, only the hex byte moves.
#          Independently reproduces 3A's AD 16->17 lesson.
#   UNCOND_BRANCH_CODES["NOP"] -> 1 row (024170.40) -- proves the gap
#          filler really is a NOP and really lands at .40.
#
# FIRSTS: the first row in the repo with an index register in an
# IMMEDIATE-INDEX VALUE field ("LVI,$X1,$X0" -> "20.03 01", pinning $X0
# at word 16 -- every other $X0 in a verify file is a J field), and the
# first computed self-relative target with BIT 18 SET ("B,$+1.0").
#
# TWO GLYPH CALLS SETTLED BY MEASUREMENT, not by eye, and both recorded
# in the file.  "EXITC" in the heading: monospace pitch fitted on a
# four-N line gives 60.1 px/cell at 600 dpi, and the heading measures 34
# cells against 33 for "...OF EXIC LESS", with two vertical strokes
# where "-EXIC LESS" has one.  FIVE letters is established; I-vs-T in
# the fourth is NOT separable, and "EXITC" is the recorded reading.
# Separately: letter O measures 50-51 px on this page and digit 0 44-45,
# and the glyph after SEN is 44 -- so it is SEN0, digit zero.
# verify_ax5b_1258_test2_listing.py's "SENO" is probably wrong; it is
# SYN'd in both files, so no encoding depends on it and neither file was
# changed to chase it.

# THE FIRST TRANSCRIPTION TARGET FOR EX/EXIC, chosen because it is a
# whole sub-test entered by one BD, its error messages are INLINE in
# its own comment column rather than an index into a shared table (so
# a failure names itself), and it encodes EXIC -- the harder arm.
#
# ITS THREE MESSAGES ARE THE SPEC, and they are Reference Manual
# printed p.50 restated: "Pseudo-instruction counters may occupy any
# of the index registers as well as main core storage locations but
# cannot occupy locations addressed between 0 and 15."  The deck uses
# word 9 ($R) and checks that no interruption occurs, that AD is set,
# and that the instruction is NOPed.
#
# A SECOND, INDEPENDENT WITNESS FOR EXIC's ENCODING, and the first
# with a SYSTEM-SYMBOL operand: "EXIC,$R" at 024145.00.  TEST 2B only
# ever writes "EXIC,I62PSI".
#
# MANUAL AND DECK DISAGREE AT THE BOUNDARY, recorded not resolved:
# p.50 says "between 0 and 15", all three deck messages say "LESS THAN
# 15".  This block uses word 9, illegal under either reading, so it
# does not discriminate 15 itself.
#
# AN UNEXPLAINED ROW, recorded the way ax5b_16082_op_ad.strap records
# what it could not trace.  024144.40 holds "%8@DD%BU,32,8@,3740
# -ILLEGAL OP." -- the same word routine 1260's I60K7 prints -- sitting
# in the STRAIGHT-LINE instruction path between "Z,$X1" and "EXIC,$R".
# It is systematic, not a slip: TEST 3B repeats the identical
# Z,$X1/DD/EXIC triple.  Nothing on those pages explains it.  The
# row's ENCODING is settled regardless, which is what is checked.
#
# Five injections, observed: EXIC's code (1 row); INDICATOR_BITS["AD"]
# 16->17, which moves the HEX byte only because 16 and 17 differ solely
# in the bit landing at 24 (1 row); enc_branch_ind dropping the clear
# bit, the field nothing else in the block exercises (1 row); BD's code
# (2 rows); LVI's code (3 rows).

run "I-Box 5 routine 1262 head and TEST 1A: EX across three memories (jb_ax5b PDF pp.87-89)" python3 verify_ax5b_162_test1a_listing.py
# 109 ROWS, the routine head plus all of TEST 1A, 023304.00-023373.00,
# abutting the section below at 023373.40.
#
# "THE SEVEN MEMORY COMBINATIONS" IN THE DECK'S OWN WORDS, at
# 023316.40: "-CHECK SEVEN POSSIBILITIES OF / -EXECUTES IN 3 MEMORIES."
# The three memories -- MAIN core, INDEX storage and the INTERNAL
# registers -- share one address space on this machine.  Three
# one-level cases, one per memory, then FOUR of the nine possible
# two-level chains: MAIN->MAIN, MAIN->IX, MAIN->INTERNAL, then
# MAIN->IX->MAIN, MAIN->INTERNAL->MAIN, MAIN->IX->IX, MAIN->INT->INT.
#
# AND CASES 4-7 ARE UNREADABLE WITHOUT THE DOUBLED K-WORD.  PDF p.109
# makes I62K2/K3/K4 full WORDS holding the SAME HALF-WORD TWICE --
# 024173.00 and 024173.40 both print "24321.12 00".  So "LX,$X2,I62K2"
# loads all 64 bits into word 18 and "EX,$X2" works whichever half its
# bit 18 selects.  The doubling is what lets ONE register hold a whole
# intermediate level.
#
# TEST 1A IS TWO BLOCKS, NOT ONE.  Before the seven comes
# 023312.40-023316.00, "-CHECK THAT EX WILL NOT RELINQUISH / -CONTROL."
# -- and that block's error path is exactly the failure mode
# ex_subject.strap's first injection produces (the subject installed
# under its OWN pc/len, halting on WRONGA).  The deck and the model
# test the same thing from opposite sides.
#
# WOULD THE MODEL'S EX SATISFY ALL SEVEN?  Read on paper, nothing run:
# cases 1-5 yes, and cases 6-7 yes BY CONSTRUCTION -- but **nothing in
# the repo demonstrates two levels BOTH in registers.**  ex_subject's
# two-level block keeps both in main storage and 1268 1B/1C is one
# level deep.  Named as the next behavioural test rather than assumed.
#
# AND THE ADDRESS-MONITORING ANSWER IS RIGHT BY COINCIDENCE, which the
# transcriber corrected in their own draft rather than leaving.  For
# cases 2/3/6/7 the observable is correct -- no IF, no AD, as p.50
# requires -- while NEITHER rule is implemented: ifViolates' `a >= 32`
# guard exists for p.45's AD reason, and the two agree only because
# this model does not raise AD for a low branch either.  A later AD
# implementation would break it.
#
# THE ROUTINE HEADER IS WRONG TWICE, not once.  Already known: it calls
# TEST 3 "THE ILLEGAL COMBINATIONS OF EX AND EXIC" where 3A and 3B are
# both EXIC-alone address-range checks.  NEW: its TEST 1 lines describe
# 1B and 1CC and omit BOTH of 1A's subjects.  It under-describes TEST 1
# as well as mis-describing TEST 3.
#
# TWO DECK TYPOS, and the second is settled WITHOUT a glyph argument.
# 023304.00 prints "-UPDATE INDENT." where every other routine prints
# "-UPDATE IDENT." -- pitch shows a letter was ADDED (seven glyphs at
# 58.5 px/cell against "UPDATE" at 61), and the intruding N is clean.
# 023310.40 prints "-SETUP 8D INT TBL, AND INT ADR." for BD, and the
# decisive evidence is INTRA-DECK: TEST 1CC's sibling stanza prints
# "-DO BB, SETUP BD INT TBL." with a clean B while loading the SAME
# I62K1 constant.  Glyph measurement is only the second leg (two closed
# bowls, no left stem, against the B of "TBL" nine cells later on the
# same row).
#
# Five injections, observed, and TWO PREDICTED VALUES WERE WRONG AND
# WERE CORRECTED TO THE OBSERVED ONES before the docstring was written:
# the CNOP row prints "000000.34 00" (not .32), and 49 is NOT a free
# indicator number -- a script over INDICATOR_BITS reports 14 is the
# ONLY value in 0-63 the table does not hold, since 48's neighbours are
# XVLZ=49 and XVZ=50.
#
# THE STRONGEST SINGLE CROSS-CHECK IS ALSO THE CNOP WITNESS:
# "EX,I623" at 023313.40 prints "23315.12 00", pair 12, bit 18 = 0 ->
# 023315.00.  023314.40 is an odd half-word, so the CNOP there MUST
# emit its filler NOP; had it emitted nothing, I623 would sit at
# 023314.40 and this pair would read 52.  It reads 12.
#
# All eight EX rows print pair 12, bit 18 = 0 throughout -- stated
# plainly rather than dressed up, and contrast 1CC's "EX,I62B6" at
# 24205.52 where it is 1.

run "I-Box 5 routine 1262 TEST 1B: EX of each class (jb_ax5b PDF pp.90-91)" python3 verify_ax5b_162_test1b_listing.py
# THE FIRST LISTING WITNESS FOR **EX** IN THIS SUITE.  MISC_CODES["EX"]
# appears in no other program here; the only prior mention anywhere is
# ax5b_1681_if_close_to_ds.strap's header, "1B and 1C need EX,
# deferred" -- this is that block.  76 rows, five instruction classes.
#
# WHY 1B HAS TWO CHECKS PER CLASS WHERE 2B HAS THREE, measured off the
# bit-18 decodes rather than assumed: in all five classes the address
# planted into I62ITE is the row IMMEDIATELY AFTER the EX, so an
# interruption and an ordinary fall-through land in the same place and
# no separate "-INT WHEN EX TO" message is possible.  2B's EXIC blocks
# plant a distinct handler and so can distinguish the two.
#
# THE DECK'S OWN SUFFIXES ARE INCONSISTENT AND THAT IS PRESERVED:
# "INST." vs "INSTR.", "DESTROYED" vs "DESTROYS", "-FLT PT" with no
# period where its siblings have one, "-TO SSIP" with no period where
# the identical row on p.110 prints "-TO SSIP.".
#
# TWO NON-NORMALISATIONS A TIDY-UP WOULD BREAK SILENTLY.  The Z,$R /
# Z,$L order INVERTS between the FLT PT and FULL WD VFL classes, and
# both orders assemble to the same two encodings -- so the check passes
# either way and only the comment records which the deck wrote.  And
# BZXVZ plays opposite roles: a skip OVER the error in DIR IX and
# IMMED IX, the jump TO it in MISC (whose subject instruction I62EXM
# IS "Z,$X1", so the index value it tests is zeroed by the subject).
#
# NO CNOP IN THIS RANGE, AND THAT IS A FINDING.  Both full-word L(BU)
# rows land word-aligned by ordinary flow, so the deck needed no
# alignment pseudo-op -- even though p.109's constants area is full of
# them.  Stated so nobody inserts one.
#
# Four injections, observed:
#   MISC_CODES["EX"] 0b010 -> 0b110      -> 5 rows (one per class)
#   DIR_INDEX_CODES["SR"] one bit        -> 1 row  (SR appears once)
#   INDICATOR_BITS["XCZ"] 48 -> 49       -> 2 rows
#   INDICATOR_BITS["RZ"] 57 -> 14        -> 2 rows
# RZ was moved to 14 rather than a neighbour because every single-bit
# neighbour of 57 is ALREADY another indicator's number, so a
# neighbour perturbation is a table collision rather than a clean
# fault; 14 is the only number in 0-63 the table does not hold.

run "I-Box 5 routine 1262 TEST 1D: USA on a 2049-level chain, and EXE (jb_ax5b PDF p.95)" python3 verify_ax5b_162_test1d_listing.py
# **THE ORACLE FOR THE USA TIMEOUT**, and the only one in the corpus.
# 42 rows, 023551.40-023576.00.
#
# IT BUILDS THE CHAIN AT RUN TIME.  "LX,$X2,I62K4" loads p.109's
# "I62K4 EX,$L" -- a FULL WORD holding two EX half-words -- as a
# template; the loop stores that word, then two SVAs write $X3 into the
# two address fields with "V+I,$X3,(8)0.40" between them, so each pass
# lays down TWO EXECUTEs each aimed at the half-word after it.
#
# AND "WHY 2049" IS NOW DERIVED FROM THE PRINT, where
# docs/execution_operations.md 4 had it as conjecture ("presumably
# 2048+1").  Two printed fields settle it: "LVI,$X3,I6084A+.32" ->
# 17245.47 01 gives I6084A = 017245.00, and "SVA,$X1,I6084B" ->
# 21245.03 D0 gives I6084B = 021245.00.  The difference is 0o2000 =
# 1024 words = 2048 half-words, and 017245.00 THROUGH 021245.00
# INCLUSIVE IS 2049 HALF-WORDS.  2049 is the chain's length.
#
# THREE OUTCOMES, ONE PASS PATH, which is what makes it an oracle for
# TWO rules at once: USA fires and the interruption is taken at the
# completion of the execution operation WHILE DISABLED -> the only
# pass; USA fires without an interruption -> "-2049 SUCCESSIVE EXECUTES
# FAIL TO COUSE / -INT BUT DO SET USA."; USA never fires -> "-...FAIL
# TO SET USA AND FAIL TO CAUSE INTERRUPT."  So 1D is the only deck
# witness for USA and a SECOND witness for printed p.50's exception 2.
#
# Note "Z,$IND / Z,$MASK" clears every SETTABLE mask bit, so nothing
# outside the permanently-masked 0-19 range can interrupt -- and USA is
# 17.  Contrast 1CB, which must do "TI,1,I00O,$MASK" because IF is 21.
#
# "COUSE" IS A DECK TYPO, AND WIDTH IS NOT WHAT SETTLES IT -- the file
# says so explicitly.  The A of "CAUSE" two rows up measures 51 px and
# the disputed glyph 52.  SHAPE settles it: the disputed glyph is a
# closed oval with a continuous outline, no apex and no crossbar, like
# the O of "TO" on the same row; the correct A two rows above has a
# pointed apex, a crossbar and two open legs.  (The A of "FAIL" on the
# same row measures only 37 px because it is inked heavily enough to
# half-fill its counter -- which is what a DEGRADED CORRECT letter
# looks like, as against a clean wrong one.)
#
# AND "-ILLEGAL OP CODE," ENDS IN A COMMA, not a period -- a verdict
# the transcriber had to revisit after catching their own clipped
# segmentation window.  This chain's comma is a rounded blob with a
# notch bitten out of its lower left and a tail descending past the
# baseline; its period has neither.  Both are present and measured.
#
# A SCAN SPECK WAS CORRECTLY NOT TRANSCRIBED: 400 dpi reads
# "CHECK. ." at 023575.00; at 600 dpi the real period is 30x39 sitting
# on the baseline and the second mark is 14x15 FLOATING five px clear
# of it, two pitch cells right.  Too small for this printer's period
# and the wrong shape for its comma.
#
# Eleven injections across this file and the 2CA/2CB one, all observed.
# **Injection 1 turns the 1CA/1CB file's documented NULL into a HIT**:
# that file had to prove liveness with a CONSTRUCTED case because it
# contains no parenthesised index; TEST 1D has three, and the same
# patch moves all three.  No constructed case was needed anywhere here.
# Injections 3 and 4 separate bit 30 from bit 29 BY DIRECTION -- under
# 3 this file's rows LOSE hex bit 30 while 2CB's GAINS it; under 4
# BUSA gains bit 29 while BEXEZ loses it, in one patch.
#
# THREE REPO FIRSTS, each grepped first: the first INDEX-MODIFIED SVA
# ("SVA,$X3,I6084A($X1)" -- every other SVA anywhere takes a bare
# label), the first branch on USA WITHOUT the reset suffix (making this
# the first block to hold a clear=0/clear=1 pair on indicator
# branches), and the first label-minus-word-offset in an
# immediate-index field.

run "I-Box 5 routine 1262 TEST 2CA/2CB: the disabled-state exceptions for EXIC (jb_ax5b PDF p.103)" python3 verify_ax5b_162_test2cab_listing.py
# THE EXIC TWINS of TEST 1CA/1CB, 31 rows, 024000.40-024020.00,
# abutting TEST 2B's last row at 024000.00.  One file because the two
# ranges abut, share the TEST 2C header and the same disabled state,
# and **2CA's pass path IS 2CB's entry** (interrupt -> I62ITE ->
# I6272).
#
# **AND IT REVERSES A GUESS THIS PROJECT RECORDED.**
# docs/listing_typography.md 10 found that a dashed rule line crossing
# a digit "1" forges a letter-I top bar, and noted p.103's `ICB` as
# "not yet checked -- the same artefact is the LIKELY explanation."
# Measured: **the rule misses the glyph by six pixels** (rule
# y1971-1976, y1977 blank, glyph y1978-2045), and the glyph is a
# 17 px BARE STROKE that TAPERS at both ends rather than carrying a
# flag and a foot.  On the same page the digit 2 of "-TEST 2C," and
# "-TEST 2CA," both measure 41 px and the letter I of "MONITOR" ON THE
# SAME ROW measures 13.  **p.103 really does print a letter I.**
#
# IT HAPPENED TWICE ON p.103 AND NOT AT ALL ON p.92 -- 024020.40 prints
# "-TEST ICC, ..." with the same bare stroke -- which is what makes it
# a DECK TYPO rather than damage: a duplicated card would have
# reproduced p.92's digit, so this is a keypunch that went wrong the
# same way twice.  The two verdicts are kept apart in the file: that
# the GLYPH is a letter I is measured; that "2CB" is what BELONGS there
# is an inference from the comment being character-for-character
# p.92's and the label column reading I6272 between I6271 and I6273.
#
# TWO HONEST NEGATIVES the bit-18 frame forced out, stated rather than
# padded: **no row in this range has bit 18 set at all**, so this block
# cannot witness the rule and inherits it from TEST 1D.  And **the EXIC
# exclusion is CONSISTENT here, not WITNESSED** -- both EXIC rows print
# pair 16 with bit 18 = 0, and an assembler wrongly treating the
# operand as a 19-bit half-word address would print exactly the same,
# because I62PSI is word-aligned.  It rests on printed p.50, which is
# what rule 4 is for.
#
# Every null in this file's injection table carries a liveness proof
# FROM THE SAME RUN -- the same confirmed patched line moved rows in
# the TEST 1D file.  Injections 5 and 6 separate EX from EXIC: 5 moves
# 1D only, 6 moves this file only.

run "I-Box 5 routine 1262 TEST 2A: EXIC must not relinquish control (jb_ax5b PDF pp.96-98)" python3 verify_ax5b_162_test2a_listing.py
# 137 ROWS, THE WHOLE BLOCK, 023576.40-023704.40 end to end.  Closure
# is arithmetic: (0o23704 - 0o23576) x 2 + 1 = 141 half-words, four of
# which are full-word VFL loads, so the pages print 137 rows.
#
# "MUST NOT RELINQUISH CONTROL" MEANS **FOUR** PLACES CONTROL MUST NOT
# GO, and the block map's six words undercount it.  The deck plants a
# trap at each and checks none fired:
#   0. the INTERRUPTION address       (SVA,$X1,I62ITE)
#   1. the half-word AFTER the PSEUDO-IC -- trap at I62BR1 = 024323.40,
#      which is the RIGHT HALF of the very word 024323.00 that holds
#      the pseudo-IC
#   2. the half-word AFTER the SUBJECT -- trap at I62BR2 = 024325.00
#   3. **INTO the pseudo-IC word ITSELF**
#
# VIOLATION 3 IS THE ONE NOBODY WOULD HAVE GUESSED, and it is a real
# contract on EXIC: p.109 prints I62PSI at 024323.00 as a REAL
# INSTRUCTION, "LX,$X0,0".  The deck zeroes $X0 before and checks it
# after -- "-INST AT PSIC WAS EXECUTED."  **The pseudo-IC word must be
# read as DATA and never executed.**  TEST 2B contains no such check.
#
# Trap 2's placement is arithmetic, shown rather than asserted: I62SUB
# is 024324.00 and the subject I62EXV is "L(BU),I00O", printed with a
# two-word machine code, so it is FULL length and occupies 024324.00
# AND 024324.40 -- making the next instruction location 024325.00,
# exactly where I62BR2 sits.  A half-length subject would have put the
# trap at 024324.40.
#
# "SEVEN MEMORY COMBINATIONS" HAS AN ANALOGUE AND IT IS **TWO**, and
# the deck says so in its own header: "CHECK THAT EXIC WILL NOT /
# RELINQUISH CONTROL,AND THE TWO / POSSIBLE MEMORY COMBINATIONS."  Only
# the PSEUDO-IC moves -- the EXIC is in the main program both times
# (it is the instruction under test) and the subject is in main storage
# both times (p.50 requires subjects at 32.00+).  The whole difference
# is "EXIC,I62PSI" against "LX,$X2,I62PSI / EXIC,$X2".
#
# AND ITS STEPPING CHECK IS STRICTLY WEAKER THAN 2B's, IN THE OPPOSITE
# POLARITY -- worth knowing before reading one out of the other.  2B
# demands the pseudo-IC stepped by EXACTLY the subject's length
# (V+I,$X2,<step> / KV / BZXE).  2A is "KVI,$X1,I62SUB / BXE" against
# "-PSEUDO IC UNCHANGED BY EXIC.", which errors only when it is still
# EQUAL to where it started: **2A merely demands that it CHANGED.**
#
# THREE PASSES, NOT THREE TESTS, and pass 0 is the odd one: it plants
# everything and runs one EXIC but CHECKS NOTHING ELSE -- it never
# zeroes $X0/$R/$L/$IND/$MASK, so it structurally cannot check
# execution or stepping.  Passes 1 and 2 are the same shape row for
# row; saying so IS the verdict, and the seven small differences are
# all transcribed rather than normalised.
#
# A FIFTH BIT-18 EXCLUSION CLASS, with its own citation.  Printed p.50:
# EXIC's pseudo-IC is "the full-word addressed by BITS 0-17 of the
# effective address" -- so EXIC's operand is an 18-bit WORD address and
# its rows are NOT bit-18 witnesses.  Note this DIFFERS from EX, whose
# operand is a 19-bit half-word address with bit 18 live (TEST 1CC
# prints "EX,I62B6" as 24205.52).  Proven by a measured null WITH a
# liveness check: forcing bit 18 off for EXIC moved none of the three
# EXIC rows (both targets word-aligned), while a constructed
# "EXIC,I62BR1" moved 024323.56 -> 024323.16 under the same patch.
#
# TWELVE TIER-1 ADDRESS WITNESSES against the sibling 2B file's four,
# six at ".40" and six at ".00" -- and the same source tokens produce
# both, which is what shows bit 18 is COMPUTED and not copied.  The
# cleanest pair crosses the two files: "B,$+1.0" prints bit 18 = 0 here
# and 1 in 2B; "BD,$+.32" prints 1 here and 0 there.
#
# FOUR POLARITIES OF TWO INDICATORS IN ONE BLOCK -- BRZ and BZRZ, BXE
# and BZXE -- each right for its own check, all settled from the
# printed hex rather than from prose.  Bit 29 is zero in all twelve, so
# nothing clears.
#
# ZERO SCAN DAMAGE IN 137 ROWS.  One DECK TYPO, settled by measuring
# the same word on the parallel line: 023624.00 prints "PSIC ON MAIN"
# where 023606.40 prints "IN MAIN" -- an 11 px bare stroke there
# against a 44 px round glyph here, clean and fully inked, where damage
# would leave a ragged I.  And one authoring quirk settled by PITCH
# rather than forced into the typo/damage binary: "CONTROL,AND" has no
# space after the comma, and cell measurement (50.0 px/cell, word gaps
# at 99-101 px) shows the cells are ADJACENT -- nothing was dropped,
# the deck printed no space.

run "I-Box 5 routine 1262 TEST 2B, EXIC by class (jb_ax5b PDF p.101)" python3 verify_ax5b_162_exic_listing.py
run "I-Box 5 routine 1262 TEST 2B: the two ends around it (jb_ax5b PDF pp.99-100, 102)" python3 verify_ax5b_162_test2b_head_tail_listing.py
# THE SECTION ABOVE IS THE MIDDLE OF THIS TEST; these are its ends.
# 76 rows, 023705.00-023742.00 and 023770.00-024000.00.  76 + the
# sibling's 43 = 119, and 023705.00 through 024000.00 inclusive IS 119
# half-words -- so TEST 2B is now covered end to end with no hole.  The
# overlap was checked on the ASSEMBLED IMAGE rather than the row lists:
# of the words between the two segments only 023742 exists, as the left
# half of this file's last head row.
#
# WHAT THE "THREE RULES PER CLASS" ACTUALLY ARE, established from the
# pages rather than from a block map: (a) the EXIC must NOT INTERRUPT;
# (b) the subject must have EXECUTED; (c) the PSEUDO-INSTRUCTION
# COUNTER must be stepped BY THE SUBJECT'S LENGTH.
#
# AND THE DIFFERENCE FROM TEST 1B's TWO RULES IS STRUCTURAL, NOT
# ADDITIVE.  Plain EX has no pseudo-IC at all, so rule (c) CANNOT exist
# for it -- 1B sweeps the same five classes with (a) and (b) only.
# Whoever implements EXIC after EX is adding a counter, not a check.
#
# THE DECK MAKES THE MANUAL'S "ONCE / TWICE" EXECUTABLE.  Printed p.50:
# "If the subject instruction is half-length, the pseudo-instruction
# counter is stepped once; if full-length, twice."  The four
# half-length classes check "V+I,$X2,0.32"; the FULL WD VFL class,
# whose subject is the full-word "L(BU),I00O", checks "V+I,$X2,1.0" at
# 023772.40 against "-PSEUDO IC NOT STEPPED 1.0 CORRECTLY / -WHEN SUBJ
# INST WAS VFL FULL WD."  Printed codes 0.45 05 against 1.05 05.
#
# TWO IDIOMS FOR RULE (c), and DIR IX is the odd one out: it checks the
# pseudo-IC ABSOLUTELY, with no before-snapshot and no $X2, while the
# other four take a before-snapshot and add.  Both are here.
#
# THE STAR BIT-18 DECODE, because it is the cleanest in the repo:
# I62PSI and I62BR1 are the TWO HALVES OF THE SAME WORD 024323,
# distinguished by nothing but bit 18.  "SVA,$X1,I62BR1" prints
# 24323.43 D0 (pair 43, bit 18 = 1) against "SVA,$X1,I62PSI" printing
# 24323.03 D0 -- same word, same J, same op byte, one bit.
#
# BRANCH POLARITY SETTLED BY ARITHMETIC, and BOTH SHAPES ARE HERE:
# BXVZ,SERS prints 1304.31 42, and hex 42 gives branchOn = 1, so it
# branches when XVZ is ON; BZXE,SERS prints 1304.32 C0, branchOn = 0.
# That is the right way round -- rule (b) errors when the reloaded
# index value IS zero (the subject never ran), rule (c) errors when the
# KV came out UNEQUAL.  Note the trailing Z of "BXVZ" is part of the
# INDICATOR NAME XVZ, not a clear: the clear bit is 0 in both bytes.
#
# NOT ONE GARBLED GLYPH IN 76 ROWS -- no ragged letter, no clean wrong
# letter.  What the block has instead is three clean-print DECK
# AUTHORING inconsistencies, recorded not corrected: 023771.40 says
# "-SUBJ INST WAS FLT PT" while standing in the FULL WD VFL class (its
# own rule-(c) message two rows later WAS updated, so clone-and-edit
# ran one way here and the other way on p.101); "-MISC" alone lacks a
# trailing period; and 023732.00 ends in a COMMA, settled by the
# descender against the period one row above.
#
# Six injections.  The sixth is a MEASURED NULL WITH A LIVENESS PROOF,
# a sharper form than this project's usual null -- see docs/NEXT.md's
# traps.  Masking bit 18 off for LX/SX moved ZERO of the 11 LX/SX rows;
# under the SAME patch a constructed "LX,$X1,I62SUB+.32" moves
# 024324.42 -> 024324.02.  So the encoder demonstrably moved by exactly
# bit 18 and the data simply cannot reach it.
#
# THAT NULL EXPOSED A LATENT ASSEMBLER GAP, recorded in docs/NEXT.md
# 5d and deliberately NOT fixed: strap_asm.py does not enforce printed
# p.23's 18-bit rule for LX/SX, so "LX,$X1,<label at a .40>" encodes
# bit 18 = 1, which no 7030 LX can mean.  A sweep of every ROWS tuple
# in every verify file parses 453 LX/SX rows and finds ZERO with bit 18
# set, so it bites nothing.  Not fixed because the manual says what the
# HARDWARE ignores, not what STRAP-1 EMITTED -- truncating, erroring
# and emitting-as-written are all defensible and no listing row decides
# it.

# ROUTINE 1262 IS THE DECK ORACLE FOR EX/EXIC, the highest-leverage
# unimplemented instruction in this model -- routine 1268 cases 1B/1C
# and routine 1260 blocks 16084/16085 all wait on it.  43 half-words,
# and the first listing witness in this suite for EXIC's encoding and
# for BZXVZ and BZXE.
#
# TEST 2B sweeps five instruction classes (DIR IX, IMMED IX, MISC, FLT
# PT, FULL WD VFL), checking three rules each, every rule with its own
# error entry: EXIC to that class must not interrupt; the subject must
# actually execute; and the PSEUDO-IC must be stepped by the SUBJECT'S
# LENGTH.
#
# THE PSEUDO-IC RULE IS LITERAL, NOT FOLKLORE.  This page shows only
# ".32", which alone cannot tell "stepped by the subject's length" from
# "always .32".  PDF p.102 settles it -- the FULL WD VFL class checks
# with "V+I,$X2,1.0" against "-PSEUDO IC NOT STEPPED 1.0 CORRECTLY /
# -WHEN SUBJ INST WAS VFL FULL WD."
#
# DO NOT READ THE CLASS OFF THE ERROR TEXT.  The deck's messages are
# clone-and-edit artifacts in BOTH directions: "-WHEN SUBJ INST WAS
# IMMED IX." appears under MISC and under FLT PT here, copied from the
# IMMED IX block on PDF p.99 where it is correct; and on p.102 the VFL
# block's pseudo-IC message was updated while its execute-check message
# still says "-SUBJ INST WAS FLT PT".  Class identity comes from the
# header comment and the "LX,$X1,<reg>" row.
#
# BZXVZ vs BXVZ IS SEMANTIC and must not be normalised.  MISC does no
# Z,$X1/Z,$L/Z,$R beforehand and expects the subject to have zeroed the
# index value, so NONZERO is the error (BZXVZ); FLT PT and VFL clear
# $L/$R and expect a nonzero result, so ZERO is the error (BXVZ).
#
# CITED BY PDF PAGE, and that is not a slip: jb_ax5b's LISTING pages
# carry no printed page numbers at all -- the "12 11 10 9" down the
# left margin is fanfold carriage-tape line numbering, and the only
# printed numbers are in the front write-up, which is scanned 2-up.
#
# Encoding only.  Rule (a) works by planting a handler into interrupt
# table entry I62ITE and awaiting an interruption, so a RUN needs the
# 64-word table, I60S1 and the I62EX* subject constants -- and EXIC is
# not EXECUTED by this model at all.  It is in MISC_CODES, so the
# ASSEMBLER encodes it; that is the whole distinction.
#
# Four injections, each naming a different set of rows:
#   MISC_CODES["EXIC"] 0b011 -> 0b111   -> 023754.40, 023767.00  (2)
#   MISC_CODES["Z"]    0b100 -> 0b101   -> 7 rows
#   DIR_INDEX_CODES["SVA"] one bit      -> 4 rows
#   INDICATOR_BITS["XVZ"] 50 -> 51      -> 023744.40, 023757.40  (2)

run "I-Box 5 routine 1260's constants + interrupt table (jb_ax5b p.86)" python3 verify_ax5b_160k_listing.py
# THE HARNESS THE p.71 COMPARISON DRIVER NEEDS, and it settles three
# things earlier transcriptions here had to leave open or infer.
#
# I60K7 IS THE ILLEGAL OP.  ax5b_16082_op_ad.strap SYN'd it from p.41
# and listed under "NOT TRACED": "WHAT I60K7 CONTAINS.  Only its
# address, 023050.00, is printed here.  The block's SHAPE ... reads
# like self-modifying code planting an invalid operation code ...
# Nothing on these pages says so."  p.86 says so:
#     I60K7  %8@DD%BU,32,8@,3740   -ILLEGAL OP, NO. 31.
#
# I60K16 IS "BD,I6086A", confirming ax5b_16086_ds.strap's external.
#
# THE INTERRUPT TABLE IS 64 WORDS, STATED RATHER THAN REASONED.
# "I60IT DR%BU,64,8@,64" sits at 023201.00 and I60DMP at 023301.00,
# 0o100 words later.  This suite's "The interruption mechanism"
# section had REASONED the units were "64 full words, from I60IT at
# 023201.00 to I60DMP at 023301.00" -- the DR row states the 64.
#
# And I60K12 is the table's DEFAULT ENTRY, "BD,I6010A" twice: every
# interruption disables and branches to what p.71 labels "-ALL INTRPTS
# EXCEPT AD ENTER HERE."  I60XW1 -- "XW,0,64,I60IT", count 64, refill
# the table -- is what the comparison driver's CB+ loop walks to copy
# that entry into all 64 slots.
#
# IT ALSO EXPOSED THE THIRD ASSEMBLER GAP THIS ROUTINE HAS FOUND.
# "C+I,$X1,I60DMP" at 023044.00 prints "23301.03 00" -- the label's
# WORD address in bits 0-17 -- and count-type immediates evaluated a
# label to a BIT address, which wrapped.  They now use eval_addr_field
# with shift 6, exactly as XW's refill field already did, so a label
# scales >>6 and a bare integer counts words ("LCI,$X1,18" unchanged).
# The first two: TRANSMIT/SWAP not encodable at all (found by p.45's
# TI) and XW's fourth operand masked to one bit (found by I60S1's
# single XW row).  Each was one row using a feature nothing else did.
#
# Injections, observed: count-immediates back to eval_expr (023044.00,
# the row that found it); C+I's immediate-index code (023044.00); BD's
# branch code (all ten BD rows).

run "I-Box 5 routine 1258 TEST 1: time clock steps (jb_ax5b PDF pp.5-6)" python3 verify_ax5b_1258_test1_listing.py
# THE BLOCK TEST 2 SITS ON.  46 rows in three contiguous pieces, each
# with its own SLC: routine 158's preamble (014002.00-014004.40),
# routine 1258's CONSTANT POOL (014006.00-014011.00, four full words),
# and TEST 1 proper from entry I581 (014012.00-014033.40, 36 half-words,
# the whole of PDF p.6).
#
# IT RETIRES FOUR OF TEST 2'S INPUT CAVEATS, which is the point of
# transcribing backwards into the preamble.  TEST 2 had to SYN IC258,
# ICK258, I58K1 and I58K2 as unwitnessed inputs; this file DEFINES
# all four from their own printed constant-pool rows at exactly those
# addresses -- including the two constants TEST 2's reload and
# bits-19-23 assertions rest on.  It also settles a glyph question TEST
# 2 left open WITHOUT measuring a glyph: ICK258 prints 600000 octal =
# bits 0 and 1 set = "test 1 done" + "test 2 done", which makes
# 014033.00's "24522.32 B0" BIT0 with a digit zero, one word below TEST
# 2's BIT1 at 024523.  An encoding decided a typography call.
#
# THE ONE CUT IS FORCED, and the reason is a positive finding about the
# listing.  014005.00's source row is the %IQSZ ident macro -- read at
# 600 dpi as "(IQSZ)DD(BU,64,8),1258   Z", with this printer's "(" and
# ")" drawn as % and a currency glyph, fixed by the same page's
# "XW,(8)777777.40,0,0".  The listing prints a LOCATION for it and NO
# MACHINE CODE AT ALL.  Substituting DD(BU,64,8),1258 would assert a row
# shape the page does not print and deposit a fabricated word, so the
# program SLCs across it and takes the ident word as a SYN.
#
# CNOP IS KEPT VERBATIM and its silence here is witnessed by the PAGE,
# not by this check -- stated in the file so nobody reads more into it.
# 014004.40 is already the second half of word 014004, so the counter
# stands at 014005.00 and the listing prints neither location nor code
# for the CNOP line.  But the next row re-establishes the counter with
# SLC,(8)14006.0, so NO row here would move if CNOP misbehaved.
# verify_ax5b_160_test8c_disabled_listing.py is the file that witnesses
# both CNOP branches from assembled output.
#
# WHAT THE BLOCK IS, for the model: word 1's clock bits 28-63 are
# exactly the COUNT (28-45) and REFILL (46-63) fields of an index word,
# so "LX,$X0,1.0" reads the whole 36-bit clock as ONE index word and
# SR/SC split it.  Reference Manual printed p.24, read first-hand: SR
# and SC each "replace bits 0-17 of the half word specified by bits 0-18
# of the effective address.  Bits 18-24 ... are set to zero."  "Z,$X2"
# zeroes index register 2 AS STORAGE WORD 18, which is why those rows
# assemble to 22/23/24/25 octal.  Unlike TEST 2, TEST 1 only READS word
# 1, so it needs no BD for the AD-on-store rule.
#
# A DEFECT IN THE DECK, flagged as an observation and not as intent: the
# carry path does not reach the field that is compared.  BZXVZ at
# 014023.00 skips the carry step while the incremented low half is
# nonzero; only a wrap falls through to 014023.40's "C+I,$X3,1.0".
# Reference Manual printed p.25: "ADD IMMEDIATE TO COUNT (C+I): Bits
# 0-17 ... are added to the COUNT field, bits 28-45" -- while 014026.00's
# KV compares bits 0-24, the VALUE field, which is where SC put the old
# high half.  So block I585 would report a spurious "-BITS 28-45 ARE NOT
# CORRECT" on the one entry in 2^18 where the low half wraps, and V+I
# would have propagated the carry.  C+I and V+I differ by one letter in
# source and one nibble in print ("1.07 00" against "1.07 05") -- the
# C+I injection below measures exactly that pair.  Intent is not
# recoverable from the page, so no claim is made about it.
#
# Five injections, observed.  The SR/SC pair is the designed one: refill
# and count are ONE BIT APART in the 5-bit direct-index code and that
# bit lands inside the printed HEX BYTE (no octal pair moves), while the
# misc Z code sits at bits 19-21, above the octal/hex boundary (only the
# octal pair moves).  Two injections, two different printed fields.
#   DIR_INDEX_CODES["SR"] -> SC's code   2 rows
#   DIR_INDEX_CODES["SC"] -> SR's code   2 rows
#   MISC_CODES["Z"] 0b100 -> 0b000       5 rows, spanning two blocks
#   IMM_INDEX_CODES["C+I"] -> V+I's      1 row
#   enc_branch_or_misc drops bit 18      1 row -- and EXACTLY one row in
#       the whole transcript carries bit 18 (014032.00 "BD,$+.32" ->
#       "14032.44 00", pair 0o44 = 100100).  The two SIC rows also show a
#       set top bit in that column, but SIC's operand is a 24-bit BIT
#       address, so its pair is a bit offset within the word, not a
#       half-word select.  Noted so the column is not misread.
#
# TWO OF TEST 2'S INJECTIONS WERE MEASURED HERE AND FAIL ZERO ROWS,
# recorded so nobody repeats the experiment: "enc_count_branch & ~1" is
# null (the single CB row targets word-aligned 014016.00), and dropping
# C+I from IMM_INDEX_COUNT_OPS is null ("1.0" yields imm19 = 2 on the
# shift-6 and shift-5 paths alike).
#
# ONE DECK-TO-DECK DIFFERENCE, checked specifically because it looked
# like a glyph call: this page shows "RET", with NO trailing glyph after
# the T, where fp_arith_f205a.strap and fp_arith_f206a.strap record the
# identical "SIC,RET1 / B,IDF1" idiom in the identical prologue slot.
# Those FP prologues are outside their transcribed ranges, so no printed
# address exists to compare against.  Treat it as a real difference
# between decks, not a reading error.

run "I-Box 5 routine 1258 TEST 2: the interval timer (jb_ax5b PDF p.7)" python3 verify_ax5b_1258_test2_listing.py
# THE REAL INTERVAL-TIMER ORACLE.  The already-transcribed I6071 block
# is 8 rows and witnesses only "TS comes on"; this is 48 rows and
# witnesses the tick RATE ("-INTERVAL TIMER FAILS TO STEP IN / -ONE
# MILLISEC"), the DECREMENT BY ONE ("-...FROM 000000.4 TO 000000.0"),
# the RELOAD TO ALL ONES ("-...FROM 000000.0 TO 777777.40", with
# constant I58K1 printing 777777.40 00 -- ones in bits 0-18), and the
# bits-19-23 clearing ("-...FROM 000001.77 TO 000001.00").
#
# Routine 1258 sits on PDF pp.5-7 -- the FIRST listing pages, right
# after the write-up, NOT in the tail where the routine numbering would
# put it.  TEST 1 (the time clock) is deliberately not transcribed: the
# model has no time clock at all, so it is further from running.
#
# THE DECK WIDENS ITS OWN MESSAGE WHERE IT WIDENS ITS OWN TEST.  Blocks
# I588 and I5810 say "IX n CONTAINS ITS NEW VALUE, 0-18."; block I5812
# -- the one whose constant I58K2 carries bits 19-23 -- says "0-23."
# That is Reference Manual printed p.34's programming note stated by
# the deck as the SCOPE OF ITS OWN COMPARISON, not merely implied.
#
# THIRTEEN bit-18 branch-target self-checks against the page's own
# label column, against I6071's one.  That is the concrete sense in
# which it is the better oracle.  The BIT table rule 024522+n holds
# three more times here (BIT1, BIT17, BIT18), each read off an encoding
# and then matched against p.114's own printing.
#
# ENCODING ONLY, and the rate claim is the reason it must stay so: "-ONE
# MILLISEC" and the three 256-count spins are WALL-CLOCK assertions an
# encoding oracle cannot check.  They are the acceptance criterion for a
# model whose timer actually ticks -- see docs/NEXT.md item 5.
#
# Four injections, observed, and the last two are the interesting ones:
#   INDICATOR_BITS["XE"] 53->52  -> 6 rows, HEX byte only
#   INDICATOR_BITS["XE"] 53->51  -> 6 rows, OCTAL pair only
#     (complements: one indicator apart in opposite directions moves two
#      DIFFERENT printed fields, which is what a field straddling the
#      octal/hex boundary looks like from either side)
#   IMM_INDEX_COUNT_OPS loses LCI -> 3 rows
#   enc_count_branch target & ~1 -> 1 of the 3 CB rows.  Only
#     "CB,$X1,I587A" has a .40 target; the other two are word-aligned,
#     so the same fault is invisible there.

run "I-Box 5 routine 1260's I60S1, bit-exact (jb_ax5b pp.83-84)" python3 verify_ax5b_160s1_listing.py
run "I-Box 5 routine 1260's I60S1 TAIL, incl. the return (jb_ax5b PDF p.85)" python3 verify_ax5b_160s1_tail_listing.py
# TWENTY-SIX ROWS, AND THE LAST TWO ARE WHY.  The section above stops at
# 023021.00; this one runs 023021.40-023041.00 and reaches the RETURN,
# which nobody had read:
#
#     023040.40         LX,$X1,I60DMP     23301.02 10
#     023041.00  I60SX1 $BD,0             0.04 00
#
# I60S1 RETURNS VIA A BRANCH DISABLED.  Every 1260/1262 block that opens
# "SIC,I60SX1 / B,I60S1" therefore runs DISABLED afterwards unless it
# enables for itself, and no BE exists anywhere in either half.  The
# caller's SIC supplies only the address: Reference Manual printed p.41,
# "the instruction counter contents [are] stored in bits 0-18 of the
# half word specified by bits 0-18 of the effective storage address.
# OTHER BITS OF THE HALF WORD ARE NOT DISTURBED" -- so the BD stands.
# Printed p.40: "Branch Disabled (BD).  This operation disables the
# interruption mechanism, and then performs the same operation as
# BRANCH."
#
# THAT ONE ROW CLOSED AN OPEN QUESTION about routine 1262's TEST 3A and
# 3B -- see the TEST 3B section and docs/NEXT.md item 6.  It is the
# clearest case this project has of a named next step paying off: the
# 3B block did not guess, it named the two pages that would decide the
# question, and reading them decided it.
#
# KEPT SEPARATE FROM THE HEAD DELIBERATELY, not by accident, and the
# reason is in the file: both halves are bit-exact and independently
# checked, this project already splits routines by page and case (8C
# against 8C_disabled, 3A against 3B), and folding 26 rows into a
# committed passing file buys tidiness at the cost of touching
# something that works.  What DID have to change was the NAME -- it
# arrived as "ax5b_160s1_clear_inds" beside the committed
# "ax5b_160s1_clr_inds", which is a trap the next reader would pay for.
#
# Five injections, observed.  The first is the one that matters:
#   UNCOND_BRANCH_CODES["BD"] 001 -> 010   1 row, 023041.00 -- the row
#       the whole answer rests on, and nothing else moves with it.
#   INDICATOR_BITS["OP"] 15 -> 14          1 row; OCTAL PAIR UNCHANGED,
#       only the hex byte moves.
#   enc_branch_ind drops the clear bit     5 rows -- and the five
#       BZXL,SERS rows are NOT among them, because branches on an INDEX
#       indicator go through a different encoder.  A measured structural
#       fact, not a guess about the encoder.
#   IMM_INDEX_CODES["KVI"] 0100 -> 0101    4 rows (023037.00's KV is
#       untouched, which separates KV from KVI).
#   DIR_INDEX_CODES["KV"] 01001 -> 01011   1 row.
#
# "-UNABLE OT CLR OP OR ABOVE IND." at 023024.00 is the LISTING'S OWN
# TYPO and is kept verbatim; the four sibling messages all read "TO".

run "I-Box 5 routine 1262's interrupt entry and constant pool (jb_ax5b PDF p.109)" python3 verify_ax5b_162_int_entry_listing.py
run "I-Box 5 routine 1274: TRUNCATION OF ADDRESSES, 99 rows (jb_ax5b PDF pp.112-114)" python3 verify_ax5b_1274_truncation_listing.py
run "I-Box 5's BIT TABLE, the SYN table and END (jb_ax5b PDF pp.114-116)" python3 verify_ax5b_bit_table_listing.py
# THE TABLE THE WHOLE PROJECT RESTED ON AND NO FILE CHECKED.  Dozens of
# transcriptions SYN into "BIT<n> = 024522 + n" as an INPUT; until now
# not one verify script had a ROWS entry on it.  81 rows + 82 symbol
# assertions + 1 END assertion, one contiguous SLC from 024501.00,
# sealed below by routine 1274's printed I74PSI at 024500.00 and above
# by END's printed 024622.00.
#
# THE RULE HOLDS FOR ALL 64, checked row by row off the LOCATION column
# rather than at the endpoints: p.114 runs BIT0 024522.00 to BIT35
# 024565.00 (0o43 = 35, 36 unbroken rows), p.115 BIT36 024566.00 to
# BIT63 024621.00, and across the page break 0o24621-0o24522 = 0o77 =
# 63.  No gap, no repeat, no off-by-one.
#
# BUT THE BLOCK IS **NOT** 64 XWs, and that is the find.  BIT24 is a
# raw "(8)DD(BU),0 000 000 010 ..." -- because IBM bit 24 is the index
# word's VALUE SIGN, and STRAP's XW,VALUE,COUNT,REFILL,FLAG has no
# operand that sets the sign ALONE: the sign only arrives via a
# negative VALUE, which also writes magnitude bits.  A word with bit 24
# and nothing else is UNREACHABLE through XW, so the deck drops to a
# data definition for exactly that one row.  The control is five rows
# earlier: I00VO is "XW,(8)-777777.77,0,0" -> sign set, but with all 24
# magnitude bits alongside.  So the ADDRESS sequence is unbroken while
# the SOURCE FORM has an exception at one row -- which is precisely why
# the brief said to check all 64 and not the endpoints.
#
# The bit is carried by a different FIELD in five bands: BIT0-23 VALUE,
# BIT24 the sign, BIT25-27 the 3-bit flag, BIT28-45 COUNT, BIT46-63
# REFILL.  Ten injections pin them apart -- "sign << 39" moves I00VO
# ALONE and leaves BIT24 unmoved, proving BIT24 is not an XW negative
# value; "dds_length_bits 64 -> 32" moves BIT24 ALONE, proving it is a
# DD with no length modifier.
#
# ONE REPO FIRST that survived grep: "DD(BU)" with NO length/padding
# modifier.  Every other DD in the repo writes DD(BU,64,8) or
# DD(BU,32,8), so dds_length_bits' "if length_expr is None: return 64"
# default had never been exercised.
#
# TWO NULLS WITH THEIR ARITHMETIC, and the pair is instructive: two
# DIFFERENT lines in dds_length_bits both read "return 64", and only
# one of them fires here.  Patching the other changes nothing.  That
# pair is exactly why a patch must be confirmed APPLIED rather than
# inferred from a green run.
#
# AND ONE INJECTION IS DELIBERATELY WEAK, labelled as such: shifting
# the SLC by 64 fails 139 of 164 rows identically.  It distinguishes
# almost nothing -- compare the one-row injections above -- and is kept
# to show what a non-discriminating injection looks like next to real
# ones.
#
# SENO / SEN0 IS SETTLED, and the decisive argument uses no glyph at
# all.  p.114 prints "SENO SYN,SEN0" -> "1311.00+", and p.116 DEFINES
# "SEN0 SYN,(8)1311.0" = that same value.  A symbol cannot be SYN'd to
# itself, so the two spellings MUST differ whatever the widths say: it
# is an ALIAS, letter-O SENO defined as digit-zero SEN0.
# ax5b_1258_test2.strap's "SENO SYN,SENO" self-SYN was wrong.
#
# THE TRANSCRIBER OVERRODE THIS SECTION'S BRIEF ON ONE SPELLING, with
# evidence, and was right: I00O, not I000.  The row's own comment is
# "-INDX WD. OF ONES." against I00Z's "-ZERO INDX WD." -- O for Ones, Z
# for Zero -- and the trailing glyph measures 51 px against 43 and 42
# for the two zeros in the same token.  The four files still spelling
# it I000 have been unified, with assembled output proved unchanged.

# THE WHOLE ROUTINE, uncut: 99 rows carrying printed machine code,
# 024412.00-024500.00.  Banner: "----I274---TRUNCATION OF ADDRESSES. /
# -THIS PROGRAM CHECKS THOSE INSTRUCTIONS WHICH / -USE ONLY PART OF
# THEIR ADDRESS FIELD."  Seven checks, one per subject: LX, SX, REFILL,
# EXIC, STORE ZERO, and TRANSMIT twice (left and right half-word).
#
# "THE NINETEENTH BIT" IS IBM BIT 18 -- nineteen address bits numbered
# from zero end at 18 -- and bit 18 is the half-word select, which is
# why every subject here addresses a full word.
#
# AND IT CORRECTS docs/archival_inventory.md, which rejected routine
# 1274 as "untestable by construction ... fixed-width arithmetic makes
# representing an address wider than architecturally valid impossible."
# TRUE OF FIVE OF THE SEVEN SUBJECTS, which are un-indexed and reach
# bit 18 from SVA rather than from index arithmetic.  NOT true of
# 024455.00, "TI,1,I74K1,I74K2($X1)" -> "24471.00 80 024472.02 A1",
# whose A2 is a 19-bit HALF-WORD address with I2 = X1 = 32 bits.  Its
# failure mode is wrong SCALING inside a perfectly legal 19-bit
# address: the model's Transmit arm sends A2 through effAddr19, and
# under the straight-add this project carried before 2026 the 32 would
# be 32 half-words instead of 32 bits, landing on word 024512 instead
# of 024472, leaving I74K2 zero and tripping the deck's own check.
# Reasoned from the page plus a reading of the arm; NOT confirmed in
# simulation, and the file says so.
#
# THE BRANCH-POLARITY SHAPE HERE IS THE OTHER ONE, and the transcriber
# checked rather than inverting to match a warning.  This block never
# does "branch to OK, fall through to the error pair": every check is
# SIC,SEN and THEN a conditional branch TO SERS, so branch-taken IS the
# error path.  The proof the reading is right is the odd one out -- six
# checks end BXVZ because correct truncation leaves the target holding
# I74K1's all-ones value, and BZXVZ at 024447.00 is inverted because
# STORE ZERO's subject writes zero, so success means the value IS zero.
# One instruction's semantics flipping one branch is not something a
# misreading produces.
#
# Six injections, observed, and the first two are a matched pair that
# splits the printed columns:
#   enc_dir_index drops IBM bit 18        4 rows, OCTAL PAIR only --
#       exactly the four whose target is an odd half-word; the three
#       even-target SVAs are silent
#   DIR_INDEX_CODES["SVA"] 11101 -> 11100 5 rows, HEX BYTE only
#   enc_imm_index drops IBM bit 18        7 rows, DISJOINT from the
#       first -- two different address encoders, separately pinned
#   enc_transmit swaps I1 (28-31) and I2 (60-63)  2 rows, and it lands
#       in a DIFFERENT printed half-word in each
#   XW refill eval_addr_field 6 -> 0      1 row
#   enc_dir_index narrowed off the TOP    MEASURED NULL: the widest
#       direct-index address here is 024501.40 = half-word 10561, and
#       IBM bit 0 of a 19-bit field weighs 2^18 = 262144.  Nothing
#       reaches it.
#
# ONE REPO FIRST, after grepping every verify file: TRANSMIT WITH THE
# INDEX ON A2 (I2, bits 60-63), at 024455.00.  Every other transcribed
# Transmit leaves I2 zero, so bits 60-63 had never been pinned against
# a printed word here.  Four further "firsts" were claimed in an early
# draft and then KNOCKED OUT by grep before the file was finished --
# R/REFILL, LV, and a label in XW's refill field all had witnesses
# already.  The corrected claim is in the file.
#
# RULE 4 IS FLAGGED HONESTLY AND LOUDLY: the narrative of WHAT EACH
# SUBJECT DOES -- Refill reloading an index word, EXIC running a
# pseudo-IC, Store Zero clearing a word, Transmit resolving A1/A2 --
# is CONJECTURE FROM LISTING USAGE.  No primary-source statement was
# found for those four, and for Refill the repo's own
# docs/microarchitecture_plan.md reads differently.  The ENCODING check
# does not rest on any of it.

# WHAT AN INTERRUPT LANDING ACTUALLY LOOKS LIKE, 54 rows, the whole of
# p.109, 024172.00-024331.00.
#
#     024320.00  I62ITE  BD,$   "-ALL INTERRUPTS ENTER HERE."  24320.04 00
#     024320.40          B,$                                   24320.50 00
#
# ONE FULL WORD HOLDING TWO SELF-LOOPS, and the routine picks which one
# an interruption lands on by which CONSTANT it fills the table with:
# I62K1 is "BD,I62ITE" (pair 04 -> bit 18 = 0 -> the BD half) and I62K6
# is "B,I62ITE+.32" (pair 50 -> bit 18 = 1 -> the B half).  Each is a
# full word holding the same half-word twice, so one SX writes it into a
# table entry and a loop fills all 64.
#
# THE RULE IS TRANSPARENCY, NOT ENABLE-STATE, and the file says so
# because the obvious generalisation is wrong: it is NOT "enabled tests
# use the B half".  Block I6225 is disabled throughout and also uses
# I62ITE+.32.  The B half is used where the landing must not CHANGE the
# enable state because the block is about to measure it; the BD half
# where disabling costs nothing.  3A and 3B both plant into the BD half.
#
# WHAT SVA REWRITES, sourced rather than assumed.  Reference Manual
# printed p.29: "The first 18, 19, or 24 bits of the value field of the
# index word specified by J replace THE ADDRESS FIELD of the instruction
# specified by the effective address", width "determined from the
# instruction operation code".  A half-word branch's address field is
# bits 0-18 -- bit 18 INCLUDED -- so SVA plants the half-word select too
# and never touches the BD.
#
# Six injections, observed.  The pair that carries the block:
#   UNCOND_BRANCH_CODES["BD"] 001 -> 100   11 rows INCLUDING 024320.00,
#       and NOT 024320.40 -- which is exactly the point of the pair.
#   CNOP alignment removed (FULL,0 -> HALF,0)  7 symbols + 15 rows, and
#       sharper than a global slide: rows before the first odd-half-word
#       CNOP do not move, and nothing below 024320.00 moves, because the
#       SLC re-anchors.
#
# THREE MEASURED NULLS, each with its arithmetic, recorded so nobody
# repeats them.  I62INT at 024220.00 prints "100.00" -- a DR RESERVE
# SIZE, 0o100 = 64 words, not a machine word; no row is asserted and no
# word fabricated (SLC across, SYN the label).  The check that it is a
# size: 024220 + 0o100 = 024320, which is where I62ITE is printed.  (The
# manual calls the table "48 successive full-word locations"; the deck
# reserves 64.)  024325.40 is a gap before a word-aligned XW and the
# listing prints nothing there.  And the four CNOPs are a free four-way
# check: the two at odd half-words print "0.30 00", the two already
# aligned print nothing and get no address column.
#
# ONE CONJECTURE, flagged in the file and not promoted: that the table
# still holds I62K1 when 3B runs.  pp.94-107 were not swept.  The
# internal argument is that if it held I62K6, 3B's SVA would plant into
# a half nothing reaches and the landing would be the untouched "B,$"
# self-loop, so the block could not pass.  That is an argument, not a
# page.

# THE ROUTINE THIS PLAN MYTHOLOGISED.  docs/NEXT.md opened with
# "Prerequisite: SSIP's I60S1/I60SX1 save/restore harness, reported at
# ax5b pp.41-44.  Nothing from 1260 can run without it."  Every clause
# was wrong.  It is local to routine 1260, not SSIP's.  It CLEARS
# INDICATORS 0-19 rather than saving or restoring anything.  It is at
# pp.83-84, 022741.00, not pp.41-44.  And four blocks of 1260 were
# transcribed without it before anyone opened the page.  Its own
# comment: "-SUBROUTINE TO CLR INDS 0-19, AND CHK THAT THEY ARE CLRD."
#
# What it IS needed for is the p.71 comparison driver, which calls it.
#
# THE SHAPE, once per indicator: branch-on-indicator-and-zero to skip
# if already clear, then TI,1,11.0,$X1 -- Transmit Immediate one word
# FROM word 11, the indicator register, INTO $X1 -- then KVI against
# that indicator's mask and a branch to SERS naming it.  MK, IK, IJ,
# EK, TS, CPUS, EKJ, UNRJ, CBJ, EPGK, UK, EE, EOP, CS, "IND NO. 14".
# Eighty-one rows.
#
# FIFTEEN USES OF TRANSMIT IMMEDIATE, every one "13.00 80 000021.02
# A0", each a full word at an odd half-word.  Before TRANSMIT_CODES
# landed today this routine could not have been assembled at all.
#
# AND IT FOUND AN ASSEMBLER BUG, which is the best reason to transcribe
# a deck.  Its ONE XW row, at 023016.00, was the single mismatch in 45:
# expected flag byte 46, produced 06.  XW's fourth operand is THREE
# bits -- IBM 25-27, the index flag plus the two spare bits -- and
# strap_asm.py masked it to one, so ",4" and ",2" both encoded as zero
# and ",1" set the flag instead of the second spare.  p.114's own BIT
# table settles it in three adjacent rows: BIT25 is "XW,0,0,0,4",
# BIT26 ",2", BIT27 ",1", printing bits 25, 26 and 27.  Only one
# existing program passed a non-zero fourth operand
# (op_ad_indicators.strap's WOTHER, never inspected).
#
# Injections, observed: enc_transmit's A1 as a half-word address (all
# fifteen TI rows); MK's indicator number (022741.40); XW's fourth
# operand masked back to one bit (023016.00 -- the row that found it).

run "I-Box 5 routine 1260 TEST 7: the COMPARISON driver (jb_ax5b p.71)" python3 verify_ax5b_160105_listing.py
run "I-Box 5 routine 1260 TEST 7: where the COMPARISON is checked (jb_ax5b PDF pp.72-73)" python3 verify_ax5b_160_test7_compare_listing.py
run "I-Box 5 routine 1260 TEST 7: the boundary sweep and its exit (jb_ax5b PDF p.74)" python3 verify_ax5b_160_test7_sweep_listing.py
# TEST 7 IS NOW COVERED END TO END by three non-overlapping files:
# p.71 (setup), pp.72-73 (the checks), and this, p.74, 50 rows,
# 022461.00-022512.40.  The next label, 022513.00, is TEST 8B's head.
#
# IT UPGRADES TWO OF THE NEIGHBOURING FILE'S ASSUMPTIONS.  pp.72-73 had
# to SYN I60121 and I60122; this page DEFINES both at exactly those
# addresses, so two inputs become witnessed rows from the other side.
#
# AND IT ANSWERS THE WRAPAROUND QUESTION pp.72-73 raised, in three
# parts -- the middle one being the real find.  **The wrap is the
# loop's TERMINATION CONDITION, not a curiosity.**  Traced across all
# three files: LB rises one word per pass and X2 at I60214 holds LB+3.
# On the last pass LB = 0o777775, so X2 before the V+I is 2^24-128
# bits; +128 carries out of bit 0, the carry is ignored, magnitude goes
# to zero, XVZ sets, and "BXVZ,I60122" at 022505.00 takes the exit.
# That is the ONLY way this loop ends -- and "LV,$X2,$X2" at 022504.40
# exists purely to re-derive XVZ, since every row between the V+I and
# it touches X13 rather than X2.  It also confirms p.71's header
# exactly: the final X = UB = 0o777777.
#
# IT ALSO CORRECTS A CITATION, one page off, in a way worth noting
# because the slip PROPAGATED.  Printed p.21 does NOT contain "this
# overflow bit ... is ignored" -- that sentence is on printed p.20,
# under Address Modification, and governs adding an index to an
# instruction address.  The rule for the V+I that produces the zero
# here is printed p.24's "The overflow which may occur in index
# arithmetic is ignored."  bsv/StretchExecute.bsv's address-modification
# comment cites p.21 for the p.20 sentence -- cosmetic there, since it
# is the right rule for the right step -- but pp.72-73's docstring
# reused that citation for a DIFFERENT step, where it is the wrong
# rule.  A one-page slip in a comment became a wrong citation two files
# later.
#
# THIRD PART, and the honest one: the wrap still DECIDES NOTHING about
# the 0-31 carve-out.  The fetch at 022477.00 reads word 0 on that
# pass, word 0 never signals under either control-bit setting, and the
# deck expects no signal anyway.  Both readings agree, so the row
# discriminates nothing.
#
# Fourteen injections, eleven with observed failures and THREE MEASURED
# NULLS with their arithmetic (DS 19->18 moves nothing because only
# BZDFZ/BXVZ appear; BU's default byte size because there is no VFL
# row; LCI because only LVI/V+I/V-I are used).
#
# THE FOUR ADDRESS-MASK INJECTIONS TURN THE BIT-18 TABLE FROM ASSERTED
# INTO WITNESSED, and they partition exactly: thirteen rows carry a
# half-word select with bit 18 set, and those thirteen are precisely
# the union of the four disjoint failing sets.  A FOURTEENTH row prints
# a pair with its top bit set -- 022510.00's "1311.40 80" -- and the
# masks leave it untouched, because that 40 is octal 40 = bit 32, a bit
# offset rather than a half-word select.  The exclusion rule this
# project states everywhere is here MEASURED rather than argued.

# THE CONTINUATION OF THE SECTION ABOVE, 92 rows, 022401.40-022460.40,
# picking up exactly where p.71's file stops at 022401.00.  p.71 is the
# SETUP and carries no error messages at all; pp.72-73 are where the
# comparison's verdict is checked, and every error message lives here.
#
# IT IS A DIRECT ORACLE FOR protViolates, not a transitive one.  Every
# reference in range is a FETCH, so the model path is dfSignal, whose
# entire body is `protViolates(st, a) ? setBit(ind, ind_DF, 1) : ind`.
# It CALLS the predicate rather than carrying its own copy of the
# interval rule, so this deck checks the function under review.
#
# BOTH ARMS OF THE CONTROL-BIT TERNARY ARE WITNESSED, which is why the
# transcription runs to p.73 and not p.72.  Every TI on p.72 moves
# BOUND1 (bit 57 SET) into location 3; at 022442.40 p.73 moves BOUND0
# (bit 57 CLEAR) and fetches between the bounds -- "-FETCH FRM LB+1,
# UB-1, BC IS 0." -- demanding a signal.  And the HALF-OPEN interval
# [lower, upper) is witnessed ACROSS the two files: p.71 fetches from
# UB with BC 1 and expects a signal, this block fetches UB-1 with the
# same control bit and demands NO signal.
#
# MY CONJECTURE ABOUT THE 0-31 CARVE-OUT WAS WRONG, and the transcriber
# tested it instead of confirming it.  TEST 7's header says "RANGE OF X
# IS FROM 000040 THRU 777777 OCTAL", and 0o40 = 32 looked like the deck
# respecting the never-signal set for locations 0 and 4-31.  It is not.
# The sweep's seed is I60XW3 at 023067.00 (PDF p.86), printing
# "101.00 00" -- so X2 enters holding word 0o101 = 65 and the FIRST X
# is UB = 0o103, not 0o40.  The header's upper endpoint is exact; its
# lower endpoint is not what the code does.  **The deck neither
# confirms nor refutes the carve-out.**  Best guess for the header,
# flagged as conjecture in the file: a comment left behind by an
# earlier value of I60XW3.
#
# ALL THREE HEADER GARBLES ARE DECK TYPOS, NOT SCAN DAMAGE, and the
# method for telling them apart is worth keeping: compare the suspect
# glyph against a CORRECT INSTANCE OF THE SAME LETTER on the same or an
# adjacent line.  Scan damage leaves a ragged correct letter; a deck
# typo prints a clean wrong one.  All three print clean wrong letters.
#   TAFLE for TABLE -- glyph 3 is a crisp F, full top and mid bars, no
#       trace of either of B's bowls, and the SAME LINE prints a clean
#       two-bowled B nine characters later in "UB HAS X".
#   TETCH for FETCH -- glyph 1's stem is CENTRED under its top bar and
#       there is NO mid bar; this printer's F puts its stem at the LEFT
#       end of the bar and carries a mid bar (see "FROM" four
#       characters later).  A dashed form rule runs through the top of
#       the row, but a rule cannot move a stem to the middle of a
#       letter nor delete a mid bar.
#   YB for UB -- two straight diagonal arms meeting a short central
#       stem; this printer's U has parallel verticals and a round
#       bottom.  Y and U are adjacent keys on the 026, which is the
#       only one of the three with an obvious mechanism.
# The same habit recurs inside the transcribed range: FITCH at
# 022432.40 (and the SAME MESSAGE spells FETCH correctly one line
# above), FRM at 022444.40, and "-TO SSIP" at 022434.40 with no period
# where 022457.00 has one.
#
# Eight injections, observed.  The two that WITNESS the bit-18 rule
# rather than asserting it are the addr19 masks on the two different
# code paths -- exactly the .40-target rows move and every .00 target
# is untouched (10 rows and 3 rows respectively).  Two measured NULLs
# with their arithmetic: INDICATOR_BITS["DS"] 19->18 moves nothing
# because the only branch-on-indicator mnemonics in range are
# BDFZ/BZDFZ/BXVZ, so no row's bits 19-24 carry 19; and
# MODE_DEFAULT_BS["BU"] 8->4 moves nothing because that default is used
# only when a VFL data description is assembled and there is no VFL row
# here.
#
# ONE ROW TRANSCRIBED AS PRINTED AND NOT EXPLAINED: 022452.40 writes
# "SV,$X14,I60AD3" where both parallel blocks write $X13, and the
# printed machine code AGREES with the printed source (index field 14
# against 13).  Whether the shipped deck's first-interrupt flag for the
# between-bounds case is ever set is not decidable from these pages.

# THE BLOCK ITEM 1 HAS WANTED SINCE THE SCOUTING PASS.  pp.65 and 68
# test whether the boundary REGISTERS HOLD THEIR BITS; this one tests
# whether the COMPARISON FIRES.  The deck's own summary:
#
#   -TEST THE COMPARE CKTS, SETUP INTERRUPT TABLE.  UB HAS X, LB HAS
#   -X-2.  FETCH FROM X+1 TO CHK UB COMP, FROM X-3 TO CHK LB COMP,
#   -AND FROM X-1 TO CHECK WITHIN RANGE OF X IS FROM 000040 THRU
#   -777777 OCTAL.
#
# Upper bound X, lower bound X-2, three fetches -- above, below,
# inside -- swept across the range.  It builds the interruption table
# in a CB+ loop, points entry 16 at I60107, calls SSIP's save/restore
# through "SIC,I60SX1 / B,I60S1", clears I60AD1/I60AD3, sets the
# bounds, ENABLES with "BE,$+.32", fetches, and lands at one of the
# deck's two labelled entries: I60107 "-AD INTRPTS ENTER HERE." and
# I6010A "-ALL INTRPTS EXCEPT AD ENTER HERE."
#
# AND IT USES TRANSMIT IMMEDIATE.  "TI,1,BOUND1,3.0" moves one word
# into word 3 -- the boundary register itself -- a FULL WORD at an ODD
# half-word (022365.40 straddling into 022366.00), the same shape as
# p.45's.  Until TRANSMIT_CODES landed this block could not have been
# assembled at all; this is TI's first use outside the page it came
# from, and it encodes right on the first try.
#
# ENCODING ONLY, for a specific reason rather than a general one: it
# needs I60S1's body (SSIP save/restore at 022741.00, still not
# transcribed), the interruption table I60IT at 023201.00, and
# BOUND0/BOUND1 at 023302/023303.  That is the harness item 1 has
# always needed -- and this is the first block where the need is real
# rather than assumed.  Fifty-two rows, right on the first assembly.
#
# Injections, observed: enc_transmit's immediate-count bit (the TI row,
# 022365.40); BD's branch code (all seven BD rows); BZB's modifier
# (022357.00, the one branch-on-bit).

run "I-Box 5 routine 1268 test 1A, bit-exact (jb_ax5b p.110)" python3 verify_ax5b_1681_listing.py
run "I-Box 5 routine 1268 test 1A, ON THE MODEL (self-modifying execution)" ./run_program.sh ../decks/ax5b_1681_if_close_to_ds.strap StretchAx5b1681Tb \
    "PC=20937"         # 024344.40, where the listing continues into test 1B
# THE INSTRUCTION-FETCH HALF of routine 1268, and the neatest block in
# it.  The deck plants a whole word over location I682 TWICE and then
# FALLS INTO I682 and executes what is there -- first [Z,$X2 | NOP],
# then [LVI,$X2,(8)777777.40 | NOP].  "LX,$X2,$X2" re-reads X2 without
# changing it, purely so the index result indicators describe X2 (Ref.
# Manual p.23); the following BXVZ tests them, and value-zero means the
# stale Z ran: "EXECUTED OLD INSTRUCTION FROM EXT."
#
# THE PEN MARKS ON p.110 ARE A READER'S NOTE, resolved at 600 dpi
# BEFORE transcribing: the XW's second half-word is boxed with "LVI"
# written beside it (the slot is overwritten at run time, so what
# executes is not what the listing prints) and "LX,$X2,$X2" is circled
# (the indicator trick).  Explanations, not corrections.
#
# THE RUN WITNESSES THE LX/SX INDEX-WORD ROUND TRIP, which is worth
# more here than the forwarding it cannot see.  LX and SX move a WHOLE
# 64-bit word, so an arbitrary INSTRUCTION is planted through
# packIndexWord/unpackIndexWord.  Injecting packIndexWord to zero
# `count` (IBM 28-45) halts the program at 1416 = 001304.00 = SERS --
# the deck's OWN error path -- because IBM bit 31 lives in `count` and
# is part of the planted LVI's J field, so the plant stops being
# "LVI,$X2" and X2 stays zero.  Dropping `addr` bit 23 also fails, but
# at PC 0, chaotically.
#
# AND A MUTANT IT PROVABLY CANNOT HELP, computed rather than guessed.
# The existing index-spare-bits-zeroed mutant zeroes IBM bits 26-27.
# The planted words are I68K1 = 0x0004920000001800 and
# I68K2 = 0xffffe50100001800; sign, flag AND SPARE are already zero in
# both, so that mutant cannot change what is planted and this block
# passes under it.  It stays the campaign's slowest near-miss, caught
# 23 minutes away by "IBOX-3 SVA into a floating-point instruction".
# Knowing WHY a test cannot catch something beats hoping it does.
#
# WHAT THE RUN DOES NOT WITNESS: look-ahead forwarding.  Two NOPs sit
# between the store and the fetch -- gentler even than test 2, which is
# already too gentle for this model.  Regression guard, not oracle.

run "I-Box 5 routine 1268 test 2, bit-exact (jb_ax5b p.111)" python3 verify_ax5b_1683_listing.py
run "I-Box 5 routine 1268 TEST 1B/1C: IF close to DS via EXECUTE (jb_ax5b PDF pp.110-111)" python3 verify_ax5b_1268_test1bc_listing.py
run "I-Box 5 routine 1268's entry, tail and CONSTANT POOL (jb_ax5b PDF pp.110-111)" python3 verify_ax5b_1268_tail_pool_listing.py
# SMALL AND WORTH MORE THAN ITS ROW COUNT.  27 rows in two blocks --
# 024376.00-024411.00 and 024333.00-024335.40 -- and with them ROUTINE
# 1268 IS NOW CONTIGUOUSLY CHECKED from 024333.00 to 024411.00 across
# five files that abut exactly.
#
# IT CONVERTS FIVE ASSUMPTIONS INTO WITNESSES, in three other files at
# once.  IC268 024405.00, ICK268 024406.00, 168K1 024407.00, 168K2
# 024410.00 and 168K3 024411.00 were SYN'd inputs in every 1268 file;
# one SLC at 024376.0 running unbroken to 024411.00 now checks each
# against TWO independent printed columns -- the page's location column
# and the machine-code column of the rows that name them.  A sixth,
# CROSS-PAGE check falls out of the entry block: p.110's "Z,IC268" at
# 024335.00 prints "24405.22 00".
#
# AND IT CORRECTS A GENERALISATION THIS PROJECT MADE THREE WEEKS' WORTH
# OF ARGUMENT ON.  ICK268 prints 600000 octal = bits 0 and 1 = TWO --
# yet routine 1268 has SIX lettered sub-tests (1A/1B/1C, 2A/2B/2C).
# There is no contradiction: the continuity constant counts
# `V+,$X13,BITn` UPDATES, and 1268 performs exactly two, because
# 1A/1B/1C are one test swept across three memories sharing bit 0 and
# 2A/2B/2C are the other sharing bit 1.  The banner says it outright:
# "-THIS TEST IS COMPOSED OF TWO ROUTINES."  Both update rows are now
# transcribed -- BIT0 at 024362.40 in the section above, BIT1 at
# 024401.00 here -- so three rows close the loop.
#
# THE TEST 8A/8D ARGUMENT SURVIVES, and docs/NEXT.md 5b now says why
# precisely: it never rested on "bits = sub-tests" as a rule.  All
# sixteen of routine 1260's bits were individually located and matched
# to a NAMED sub-test, so that enumeration is closed by the list, not
# by the arithmetic.  1268 is what the alternative reading would have
# looked like had one bit been unaccounted for.
#
# THE BIT-18 EXCLUSION TURNS OUT TO HAVE FOUR OPERAND CLASSES, NOT TWO,
# and the new one has a DIFFERENT REASON from the familiar bit-address
# case.  Printed p.23: "In the majority of these operations, 19 bits of
# the effective address are used in order to permit addressing of
# half-words.  THE TWO EXCEPTIONS USE ONLY 18 BITS OF THE EFFECTIVE
# ADDRESS BECAUSE THEY REQUIRE FULL-WORD OPERANDS."  Those two are LX
# and SX -- so their pair carries bit 18 = 0 structurally, because the
# field is NARROWER, not because the bit means something else.  V+ and
# KV are NOT the exceptions (printed p.24 on KV: "the half-word
# addressed by bits 0-18"), so they are checked normally.
#
# AND THE SIC CASE IS UNDECIDABLE FROM THE DIGITS -- measured, not
# argued.  Injection 9 re-reads enc_sic's operand as a 19-bit half-word
# address and fails ZERO rows, because every SIC offset in this block
# is 0 or 32 and 32 bits IS one half-word, so both readings produce
# numerically identical six bits.  Injection 10 (+1 on the address)
# fails all three SIC rows, showing only that the field is live.  The
# manual settles the reading; the print cannot.
#
# Eleven injections, every failure set observed, every patch confirmed
# applied before running.  Notable ones: bit 18 cleared in
# enc_branch_or_misc fails EXACTLY the two odd-half-word targets and
# leaves the six even ones silent; two extra half-words spliced into
# the tail fails 16 rows INCLUDING ALL FIVE SYMBOL ASSERTIONS, each one
# full word high, which is the check that the pool addresses are really
# computed rather than asserted.
#
# A CNOP CORRECTION THE TRANSCRIBER MADE AGAINST THEIR OWN FIRST DRAFT,
# by measuring: the 024404.40 CNOP IS load-bearing here.  Deleting it
# leaves an all-zero half-word, because assemble() records a rounding
# gap only for an INSTRUCTION and strap_asm excludes XW.  So this file
# witnesses CNOP's NOP EMISSION though not its round-up -- XW's own
# alignment does that.  The p.110 CNOP is a genuine null.
#
# ONE ROW IS DELIBERATELY ABSENT AND THE ABSENCE IS ASSERTED: 024336.00,
# the ident word, prints a location and NO machine code.  Rather than
# fabricate a word the file SLCs across it, SYNs the label from the
# LOCATION column, and then asserts that word 024336 is absent from the
# assembled image.

# THE GAP BETWEEN THE TWO SECTIONS AROUND IT.  30 rows,
# 024344.40-024363.00 -- exactly where ax5b_1681_if_close_to_ds.strap
# says it stopped ("a BEW,$ exit at 024344.40, where the listing
# continues into test 1B ... 1B and 1C need EX").
#
# WHY 1B AND 1C NEED EXECUTE, which is what the deferral was about.
# Test 1A plants a word over a location and FALLS INTO IT -- only
# possible for a location in the instruction stream.  Index storage
# (word 19) and word 9 are not, so 1B and 1C reach them with EX:
# plant [Z,$X2|NOP], three NOPs, plant [LVI,$X2,(8)777777.40|NOP] over
# it, then "EX,$X3" (resp. "EX,$R") and "LX,$X2,$X2" to set the
# indicators.  (That reading of WHY is an inference from the rows'
# shape and is flagged as conjecture in the file; EX's semantics are
# sourced, printed p.49.)
#
# BRANCH POLARITY IS THE MINORITY SHAPE HERE, and the file proves it
# from the ENCODING rather than from prose.  No branch to an OK label
# exists in the 30 rows; both bodies end "SIC,SEN" then "BXVZ,SERS",
# so branch-taken IS the error path.  Both BXVZ rows print
# "1304.31 42": enc_branch_ind puts branchOn at bit 30, and hex 42 =
# 0100_0010 over bits 24-31 gives bit 30 = 1 (branch when ON) and bit
# 29 (clear) = 0.  A BZXVZ would print 40.
#
# IT DOES NOT BEAR ON protViolates, and the near-miss is recorded so
# nobody re-finds it and gets excited.  "DF CLOSE TO DS" names the
# data-fetch and data-store PATHS; "close" is about TIME.  Nothing in
# range writes location 3, touches the mask, or branches on DS/DF/IF.
# Printed p.32 does say an EX subject's location is IF-monitored "when
# this location is in main storage" -- but 1B's and 1C's subjects are
# word 19 and word 9, which are not.  The overlap is vocabulary, not
# mechanism.
#
# THE LABEL COLUMN IS EMPTY FOR ALL 30 ROWS, so SYMBOLS is literally
# empty -- there is not even an SLC-placed anchor to argue about, and
# the only genuinely witnessed addresses are two self-relative rows.
# Said plainly rather than padded.
#
# Seven injections, observed, and TWO OF THE AGENT'S OWN PREDICTIONS
# WERE WRONG and are named in the file: LX 00001->00010 was predicted
# to move both printed columns and moves only the hex byte, and EX
# 010->101 was predicted to print 25 and prints 26.  The reason the
# columns split is arithmetic, not luck: a direct-index code is 5 bits
# at 23-27 so only its top bit is in the octal pair, a misc code is 3
# bits at 19-21 so it is wholly inside the pair, and an indicator
# number straddles at 19-24.
#
# ONE MEASURED NULL with its reason: forcing enc_branch_ind's `clear`
# bit to zero moves nothing, because neither BXVZ carries a trailing Z
# so the bit is already zero in both rows.  That field is this block's
# one blind spot and it is arithmetic, not luck.
#
# THE SIC ROWS ARE EXCLUDED FROM THE BIT-18 TABLE, and this block has
# the cleanest statement of why: SIC's operand is a 24-bit BIT address,
# so "SIC,SEN0+.32" printing "1311.40 80" has 40 = octal 40 = 32 bits,
# which is the "+.32" in the source.  THE TRAP IS THAT 32 BITS IS ALSO
# ONE HALF-WORD, so the digits look identical under the wrong reading.
# The arithmetic settles it, not the digits.

run "I-Box 5 routine 1268 test 2, ON THE MODEL (the deck's own logic)" ./run_program.sh ../decks/ax5b_1683_df_close_to_ds.strap StretchAx5b1683Tb \
    "PC=20988"         # 024376.00, where the listing continues
# DOCS/NEXT.md ITEM 2 WAS BUILT ON A MISREADING, corrected here.  It
# called routine 1268 "the only known deck test" of the DF and IF
# ADDRESS-MONITORING INDICATORS and said to read it before designing
# them.  Read first-hand, the routine's own header (PDF p.110) is
# "1268 -- IF AND DF CLOSE TO DS", and its error messages settle it:
# "EXECUTED OLD INSTRUCTION FROM EXT." (test 1) and "LOADED OLD DATA
# FROM EXT MEM." (test 2).  Routine 1260's indicator blocks say
# "UNABLE TO TURN AD ON." when an INDICATOR fails; these say the wrong
# VALUE arrived.  DF and IF are the Data Fetch and Instruction Fetch
# PATHS; "close to DS" is close to a Data Store.  1268 is a look-ahead
# store-to-fetch / store-to-load forwarding test.  Nothing in it writes
# a mask, sets a boundary register, branches on DF or IF, or touches
# protected storage -- I68K3 is ordinary storage at 024411.00.
#
# docs/archival_inventory.md contained BOTH readings, twenty lines
# apart; the "Look-Ahead store-to-fetch/store-to-load forwarding" one
# was right.  So the DF and IF INDICATORS have NO deck oracle in this
# document, and item 2 has to fall back on Reference Manual p.32.
#
# WHAT THE BLOCK DOES, three times: zero a destination, load X1 with an
# index word of ones, STORE it, immediately LOAD it back, and branch to
# the error routine if what came back is zero.  The destinations are
# I68K3 (external), $X4 (index storage) and $R (internal).
#
# TWO STANDARDS, AND THEY ARE NOT EQUAL.  The ENCODING check is
# discriminating: Z's misc code, the misc literal, and XVZ's indicator
# number each fail their own rows (6, 6 and 3), recorded in the verify
# script.  The RUN passes, and MEASURED 2026-09-22 it does NOT witness
# forwarding on this model: removing StretchStorage.bsv's
# "&& !storeQ.notEmpty" store-queue drain leaves this block green AND
# leaves store_close_to_fetch.strap green, while
# ebox_register_close_to_fetch.strap fails two checks (SEN
# 0x0700e00000000000 for 0, halt 1416 for 14343).  The guard is
# witnessed -- by the hand-written E-box test, not by the deck's.
#
# WHY THE DECK IS THE WEAKER TEST HERE, which is worth knowing before
# reaching for a deck as an oracle: it spaces its store and load one
# instruction apart, tight enough for the real machine's look-ahead and
# not tight enough for this model's shallower pipeline, so the store
# queue has drained before the load issues.  The E-box test
# manufactures a tighter overlap on purpose.  A 1961 diagnostic being
# too GENTLE for a 2026 model is the reverse of the usual direction.
#
# So the run is a regression guard today and becomes a real oracle when
# the look-ahead's LAAR forwarding replaces the ordering rule --
# StretchStorage.bsv's own comment says that is stage 3.

# -- 2. Problem 2.1: Cyclic Bit Shifting --
run "Problem 2.1" ./run_program.sh ../decks/problem_2_1.strap StretchProblem21Tb \
    "DOG_rotated:32=0x6e5d4c3b2a19087f" \
    "CYCLES<=140"

# -- 3. Problem 2.2 Method 1: Length of an Unknown File --
# Answer lands in X1's VALUE field (top 24 bits of the packed IndexWord,
# StretchTypes.bsv addr:w[63:40]), not the plain word -- 28 bits, shifted:
# 28 << 40 = 0x1c0000000000. See README.md "Units": ImmIndex/V+ operate in
# raw bit-count units, and X1 IS an index register (addrIndex(1) = 17).
run "Problem 2.2 Method 1" ./run_program.sh ../decks/problem_2_2_method1.strap StretchProblem22Tb \
    "X1_len:addrIndex(1)=0x1c0000000000"

# -- 3b. Problem 2.2 Method 2: same problem, VFL immediate addressing +
# progressive indexing instead. Same expected answer (28 bits) as
# Method 1 above, by construction (reuses Method 1's own test data) --
# see ../decks/problem_2_2_method2.strap's header for how X1 ends up
# holding exactly the length rather than an absolute address.
run "Problem 2.2 Method 2" ./run_program.sh ../decks/problem_2_2_method2.strap StretchProblem22M2Tb \
    "X1_len:addrIndex(1)=0x1c0000000000"

# -- 3c. Problem 2.2 Method 3's algorithm: Connective (CT0110, i.e.
# XOR) + BRZ instead of K + BAE. Two of the seven manual lines are
# substituted for already-verified Method 2 equivalents (LVE/SIC are
# unimplemented -- see ../decks/problem_2_2_method3.strap's header for
# the full account); same expected answer (28 bits) either way.
run "Problem 2.2 Method 3 (algorithm)" ./run_program.sh ../decks/problem_2_2_method3.strap StretchProblem22M3Tb \
    "X1_len:addrIndex(1)=0x1c0000000000"

# -- 4. Reference Manual Figure 7: Progressive Indexing --
# Expected final memory (words holding the ten records' R/S/T fields) is
# derived, not hand-computed: run
#     python3 - <<'PY'
#     import sys; sys.path.insert(0, '.')
#     from strap_asm import assemble
#     prog = assemble(open('../decks/figure7_progressive_indexing.strap').read())
#     LIST = prog.symtab['LIST']; words = dict(prog.words)
#     def get_bits(a, n):
#         v = 0
#         for i in range(n):
#             w, b = divmod(a + i, 64); v = (v << 1) | ((words.get(w, 0) >> (63 - b)) & 1)
#         return v
#     def set_bits(a, n, val):
#         for i in range(n):
#             w, b = divmod(a + i, 64); m = 1 << (63 - b)
#             words[w] = (words.get(w, 0) & ~m) | (m if (val >> (n - 1 - i)) & 1 else 0)
#     for i in range(10):
#         base = LIST + 20 * i
#         R, T = get_bits(base, 7), get_bits(base + 15, 5)
#         set_bits(base + 7, 8, (R + T) & 0xFF)
#     for w in range(LIST // 64, (LIST + 200 - 1) // 64 + 1):
#         print(f"word[{w}] = {words[w]:016x}")
#     PY
# (records are 20 bits each: R=7 bits/BU, S=8 bits/BU stored with R+T,
# T=5 bits/BU; LIST is padded so no record's S field crosses a word
# boundary -- see the .strap file's own comment). Reproduced here as the
# literal checks below so this script doesn't need to invoke Python twice.
run "Figure 7 Progressive Indexing" ./run_program.sh ../decks/figure7_progressive_indexing.strap StretchFigure7Tb \
    "w36:36=0x910000000a0a0" \
    "w37:37=0xb0c08c0e10d1018" \
    "w38:38=0xe1220f1429016311" \
    "w39:39=0x183921a4131c4800"

# -- 4b. I-Box 1 diagnostic (docs/ja_ax1a_ibox-1.pdf p.51, WEN/WEN2/VEN):
# VFL binary-unsigned Load correctly sets RGZ for a nonzero unsigned
# value and RZ for zero -- see docs/archival_inventory.md "6. The five
# I-Box diagnostic test programs" for how this candidate was chosen
# (the smallest self-contained runnable fragment found, after routine
# 1274's address-truncation test turned out to be untestable by
# construction on this model's typed WordAddr/HWordAddr widths).
run "I-Box 1 WEN/WEN2/VEN (RGZ/RZ indicators)" ./run_program.sh ../decks/ibox1_wen_ven_indicators.strap StretchIboxWenTb \
    "X1_RGZ_ones:addrIndex(1)=0xc800000000000" \
    "X2_RZ_zeros:addrIndex(2)=0xc800000000000" \
    "X3_RGZ_ones_again:addrIndex(3)=0xc800000000000" \
    "X4_notRZ_ones:addrIndex(4)=0xc800000000000" \
    "X5_notRGZ_zeros:addrIndex(5)=0xc800000000000"

# -- 4b'. The same three routines placed at the listing's OWN addresses
# (words 2860-2865, constants at 3138-3139) via SLC -- the first
# program to run above the old 256-word core window (MemWords is now
# the full 18-bit space). Verified discriminating: with MemWords put
# back to 256, all 5 checks fail (fetches above the window read 0).
run "I-Box 1 WEN/WEN2/VEN at original listing addresses" ./run_program.sh ../decks/ibox1_wen_ven_original_addresses.strap StretchIboxWenOrigTb \
    "X1_RGZ_ones:addrIndex(1)=0xc800000000000" \
    "X2_RZ_zeros:addrIndex(2)=0xc800000000000" \
    "X3_RGZ_ones_again:addrIndex(3)=0xc800000000000" \
    "X4_notRZ_ones:addrIndex(4)=0xc800000000000" \
    "X5_notRGZ_zeros:addrIndex(5)=0xc800000000000"

# -- 4b''. I-Box 1's SIC-CB and SIC-CBZ test groups (p.50), verbatim at
# octal 5412-5432, run with the deck's OWN pass/fail mechanism: each
# SIC rewrites the "BD,$" hang after it into "BD,<next hang>", and the
# block ends by walking that chain. A branch to itself halts this
# model, so PC alone says pass (halted at the substituted BEW at
# 5432.40) or fail (halted at the un-rewritten hang). Expected words
# derived from the assembled program by sic_cb_expected.py.
run "I-Box 1 SIC-CB / SIC-CBZ (verbatim, own pass/fail)" ./run_program.sh ../decks/ibox1_sic_cb_cbz.strap StretchIboxSicTb \
    $(python3 ibox1_expected.py ../decks/ibox1_sic_cb_cbz.strap ISBI \
        ISCBA:ISCBB ISCBB:ISCBC ISCBC:ISCBD ISCBD:ISCBH ISCBH:ISCBI ISCBI:ISCBK)

# -- 4b-bis. BRANCH ON BIT (BB family) acceptance: a self-checking
# chain over an all-zeros word W where the ONLY path to the PASS halt
# (label DONE) requires correct condition testing (branch-on-1 vs
# branch-on-0) AND correct bit modification on both a taken branch
# (BBN invert) and a NOT-taken branch (BB1 set). Any wrong result falls
# into a distinct BEW,$ HANG, so PC alone says pass (DONE) or fail
# (which HANG). See ../decks/bb_branch_on_bit.strap for the injections.
run "Branch-on-Bit (BB/BZB family, self-checking)" ./run_program.sh ../decks/bb_branch_on_bit.strap StretchBBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("../decks/bb_branch_on_bit.strap").read()).symtab["DONE"]//32)')"

# -- 4b'''. pp.43-51 as ONE verbatim span, octal 5123.00-5461.40: the
# deck's whole index-branching section (CB, CB+, CBH, CB-, CBZ, CBZ+,
# CBZ-, CBZH, CBR, CBR+, CBR-, CBRH, CBRZ, CBRZ+, CBRZ-, CBRZH), then
# SIC-CB, SIC-CBZ, SIC-B,ZIND, SIC-B,IND and WEN2/WEN/VEN -- twenty
# consecutive test groups flowing into each other exactly as the deck
# lays them out, one substituted BEW at 5462.00. The count-and-branch
# groups' own SX value tests pin the H/+/- units (32/64/-64 bits) --
# the model's old +1/+2/-2 hangs at the first incrementing group.
# Every SX-stored index word and SIC/SV-rewritten hang checked plus the
# halt PC (ibox1_expected.py).
run "I-Box 1 pp.43-51 span (20 test groups, verbatim)" ./run_program.sh ../decks/ibox1_p43_p51_span.strap StretchIboxSpanTb \
    $(python3 ibox1_expected.py ../decks/ibox1_p43_p51_span.strap IBY \
        IBR8=XW:IBR9+\(8\).04,0,-1 IBR18=XW:IBR19+\(8\).04,0,-1 \
        IBR28=XW:IBR29+\(8\).04,0,-1 IBR38=XW:IBR39+\(8\).04,0,-1 \
        IBR52=XW:IBR53+\(8\).04,0,-1 IBR66=XW:IBR67+\(8\).04,0,-1 \
        IBR80=XW:IBR81+\(8\).04,0,-1 IBR94=XW:IBR95+\(8\).04,0,-1 \
        IBR100=COPY:IBRA10 \
        IBR106=XW:IBR107+\(8\).04,1,IBRA12 IBR107=COPY:IBRA12 \
        IBR113=XW:IBR114+\(8\).04,1,IBRA14 IBR114=COPY:IBRA14 \
        IBR120=XW:IBR121+\(8\).04,1,IBRA16 IBR121=COPY:IBRA16 \
        IBR138=XW:IBR139+\(8\).04,1,IBRA18 IBR139=COPY:IBRA18 \
        IBR156=XW:IBR157+\(8\).04,1,IBRA20 IBR157=COPY:IBRA20 \
        IBR174=XW:IBR175+\(8\).04,1,IBRA22 IBR175=COPY:IBRA22 \
        IBR192=XW:IBR193+\(8\).04,1,IBRA24 IBR193=COPY:IBRA24 \
        ISCBA:ISCBB ISCBB:ISCBC ISCBC:ISCBD ISCBD:ISCBH ISCBH:ISCBI ISCBI:ISCBK \
        ISBIA:ISBIB ISBIB:ISBIC ISBIC:ISBID ISBID:ISBIH ISBIH:ISBII ISBII:ISBIK) \
    "CYCLES<=4400"

# -- 4c. I-Box 4 diagnostic (docs/jb_ax4b_ibox-4.pdf p.155, routine 150
# "CB AND CBR TEST", the plain CB mnemonic): Count and Branch
# decrements count and branches iff nonzero, and (v=00) never touches
# the value field -- see docs/archival_inventory.md "I-Box 4" for how
# this candidate was chosen (section 138's "$R" system symbol doesn't
# parse and was rejected; section 150 needed only a mnemonic-table
# addition over an already-fully-implemented encoder/decoder, added
# to opcodes.py as CB_CODES).
run "I-Box 4 CB (Count and Branch)" ./run_program.sh ../decks/ibox4_cb_count_branch.strap StretchIboxCbTb \
    "X1_final:addrIndex(1)=0x3e70000000000" \
    "X2_step1_taken:addrIndex(2)=0xc800000000000" \
    "X3_step2_taken:addrIndex(3)=0xc800000000000" \
    "X4_step3_taken:addrIndex(4)=0xc800000000000" \
    "X5_step4_not_taken:addrIndex(5)=0x0"

# -- 4d. I-Box 4 diagnostic (docs/jb_ax4b_ibox-4.pdf p.159, routine 150,
# the IBR96-IBR99 block): "CBR" (Count, Branch, and Refill) -- exercises
# CountBranch's own refill mechanism (doRefill/needsRead/prefetch), a
# code path distinct from xw_refill.strap's V+ICR-based refill test.
# See ibox4_cbr_refill.strap's own header for the full transcription
# and non-vacuousness account.
run "I-Box 4 CBR (Count, Branch, and Refill)" ./run_program.sh ../decks/ibox4_cbr_refill.strap StretchIboxCbrTb \
    "X2_call1_taken:addrIndex(2)=0xc800000000000" \
    "X3_call2_taken:addrIndex(3)=0xc800000000000" \
    "X4_call3_not_taken:addrIndex(4)=0x0" \
    "X5_no_refill_yet:addrIndex(5)=0x6f0000040029" \
    "X6_refilled:addrIndex(6)=0xde00fffc0000"

# -- 5. XW refill mechanism (see README.md "Gotchas" item 7) --
# Distinctive VALUE=999/COUNT=42 at CTLB, refilled into $X12 via CTLA's
# COUNT=1 forcing exactly one refill on the program's one progressive
# store; expected = CTLB's own packed XW encoding, verbatim.
run "XW refill" ./run_program.sh ../decks/xw_refill.strap StretchXwRefillTb \
    "X12_after_refill:addrIndex(12)=0x3e70000a80000"

# -- 6. Simulated Input-Output subsystem (StretchIO.bsv): RD/W/CCW/REL
# against a simulated card reader (channel 32) and printer (channel
# 33), plus two discriminating checks -- a wrong-unit RD given to the
# printer (Exchange Program Check) and a channel with no device
# installed (Unit Not Ready Reject), the latter reached through an
# index register rather than a literal specifically to exercise the
# channel-address field's own index arithmetic (Reference Manual
# p.111). Expected control-word values are derived in gen_io_tb.py
# from the manual's own p.124 control-word-update rules (with one
# documented, deliberate deviation: this model's WRITE does not
# reproduce the real Exchange's "+2" double-buffering quirk -- see
# StretchIO.bsv). Not a Reference Manual worked example -- this
# project's first purpose-written program for a feature the manual
# doesn't happen to walk through an instance of.
run "The opcode table against the manual's own COMPLETE OPERATION AND MODIFIER LIST" python3 verify_refman_p168_opcodes.py
# >>> 22-6530-2 printed pp.168-169 = PDF pp.171-172 is the normative
# opcode table for the whole machine, and this project had never
# opened it.  strap/README.md's "Next steps" item 2 asked for exactly
# this cross-check and named a worse source for it. <<<  Found by the
# back-matter sweep, two sections after the card code was found the
# same way.
#
# ALL TEN CLASSES, TWO-WAY, AND EVERY ONE AGREES: 24 VFL integer and
# radix conversion, 29 floating point, 16 direct index, 16 immediate
# index, 6 unconditional branch, 5 miscellaneous, 11 input-output, 3
# connective, 16 index branching, 8 transmit, plus the P-field
# indexing modes.  Two-way means a mnemonic present on one side and
# not the other fails too, which is the half that catches an
# operation quietly added to the assembler.
#
# THE CHECK IS ON THE TEMPLATES, NOT ONLY THE NUMBERS.  The page
# states each code as a pattern over a named bit range --
# "ssbxxxxx1iiii" for VFL over bits 51-63, "nssxxxxx10iiii" for
# floating point over 18-31, "jjjjxxxx1iiii" for direct index over
# 19-31, "jjjj10000xxxx" for IMMEDIATE index over the same bits --
# and opcodes.py stores a different slice of each.  The verifier
# applies the template's own rule and compares.  THE
# IMMEDIATE-INDEX RULE DIFFERS FROM THE OTHER THREE: its x's are at
# the END with nothing trailing them, so its stored code is the
# printed digits unchanged while the others carry a literal 1 or 10
# underneath.  A number-only comparison would pass with that
# misread.
#
# TWO VALUES MOVED FROM A SUMMARY TO THE MANUAL.  opcodes.py's own
# comments credit the X22-6533 POCKET CARD for CONNECTIVE_SUFFIX and
# IO_OP.  A pocket card is a summary of this page; now the page says
# it.
#
# AND THE P FIELD IS PRINTED.  "INDEXING MODES FOR VARIABLE FIELD
# LENGTH OPERATIONS; Instruction bits 32-34" gives 000 direct, 100
# immediate, 001 V+, 010 V+C, 011 V+CR, 101 V-, 110 V-C, 111 V-CR.
# That is the field this project spent a session on from the other
# end -- progressive indexing, where the effective address IS the
# index value -- and it is also "4 for immediate and 0 for direct",
# which settled LFI on MCP printed p.18 by comparing one field of one
# assembled word against the listing.
#
# THREE MEASURED INJECTIONS:
#   1. Give CT the wrong connective suffix -> "connective_codes =
#      {'CT': (31, 23)}", the stored value against the printed one.
#   2. Delete SVA from DIR_INDEX_CODES -> the two-way mnemonic check
#      names it, which a value comparison alone could not.
#   3. Apply the VFL rule to the FLOATING POINT block, i.e. misread
#      "nssxxxxx10iiii" as "ssbxxxxx1iiii" -> caught.

run "The card code is PRINTED: C22-6678-1 Appendix F" python3 verify_c22_6678_appendix_f.py
# >>> strap/cards.py ASSERTED THAT NO 7030 DOCUMENT GAVE THE CARD CODE
# DIRECTLY.  C22-6678-1 printed p.56 = PDF p.56, "APPENDIX F.
# CHARACTER CODES", gives it directly. <<<  Four columns -- Character,
# IQS, BCD, Punches -- under the header "The following table lists the
# octal codes, by character, for eight-bit IQS, six-bit BCD, and the
# corresponding column binary punches."
#
# docs/NEXT.md had listed C22-6678-1 as one of three unchecked
# candidates for exactly this and nobody had opened it, while a
# derivation was built and defended at length.  That is the lesson
# more than the table is.
#
# THE DERIVATION IS KEPT AND MEASURED rather than deleted.
# cards.punches_from_grid() still builds the answer out of the 48
# Character Set grid on Reference Manual printed p.166 -- its four
# occupied columns ARE the four zone punches, its sixteen rows ARE the
# digit punches -- and this checks how far that argument gets.  IT
# GETS 48 OF 52 ROWS, AND THE FOUR IT MISSES ARE THE WHOLE POINT:
#
#     char   Appendix F   the grid derivation
#     '      0-3-8        4-8            <- transposed
#     ,      4-8          0-3-8          <- transposed
#     ;      11-0         not in the grid at all
#     :      NO PUNCHES   0-2-8
#
# The quote and the comma have each other's punches; the 7030 spends
# 11-0 on a semicolon and gives the colon NO CARD CODE AT ALL -- an
# IQS code of 165 and a blank Punches column.  Those are precisely the
# slots where the conventional commercial code and the 7030's
# 48-character set disagree, and the derivation was justified on the
# grounds that the code "belongs to the CARD and the keypunch, not to
# the computer" -- true of the letters and digits, false of exactly
# the punctuation, which is the only place it could have mattered.
# THE FOUR-CHARACTER GAP IS A RATCHET: it is spelled out as a literal
# and compared whole, so moving a character into or out of it fails.
#
# AND THE COLON CAME OFF THE CARD-READER DECK because of this, which
# is the finding reaching something: ../decks are punched through this
# table, and a character the 7030 cannot punch should not be on one.
#
# THE LAST TWO CHECKS ARE WHY THE PAGE WAS OPENED.  p.17 line 30
# compares 48 bits against X IOCD; the identifier field is columns
# 10-13, four columns, four characters.  Appendix F's punches, packed
# in the bit order Reference Manual printed p.138 prints (row 12
# first), give 0x801408840820 -- and its LEADING bit is set because
# "I" is 12-9, a 12-zone letter, which is exactly what line 13's
# "BB, 1.44($4)" tests under the comment "-IF ZONE BIT OF IOCD".  The
# MCP p.17 testbench now computes its identifier this way instead of
# carrying an invented constant.
#
# TWO MEASURED INJECTIONS, both caught by name:
#   1. Give "," the CONVENTIONAL code 0-3-8 -- i.e. assume exactly
#      what the derivation assumed.  "',': [0, 3, 8] vs printed 4-8".
#   2. Give ":" a code.  Two checks move: the punch comparison names
#      it, and the blank-cell list drops from three entries to two.

run "PUNCHED CARDS: an ASCII deck read on the IBM 7503" ./run_card_test.sh StretchCardTb
# SIMH-STYLE IN, PUNCHES OUT.  strap/cards.py turns a line of text into
# the 960 bits a real card presents -- 80 columns of 12 punch rows,
# fifteen 64-bit words exactly -- and ../decks/card_reader.strap does
# two ordinary RDs against channel 32 and knows nothing about any of
# it.  Every expectation is computed from the deck text, so a pass
# means the words the machine read ARE the words that line punches to.
#
# THE LAYOUT IS SOURCED, not assumed.  R23-9702, the 7503/7614 CE
# manual, Figure 4.3-1 "Data Bit Relation -- Card to Data Word",
# printed p.21, all 72 filled cells read at 600 dpi: the twelve rows
# run 12, 11, 0, 1-9 with the 12 row most significant, column 1 first,
# and A COLUMN STRADDLES A BYTE BOUNDARY at one and a half bytes each.
# Packing twelve-bit columns end to end produces exactly that.
#
# THE PUNCH PATTERNS ARE PRINTED, and this section used to say they
# were not.  R23-9702 printed p.21 is still right about the HARDWARE:
# "The data punched in the IBM card used with the 7030 System is in a
# binary form.  Each card punch position is a possible data bit, with
# a punched hole representing the data bit", and there is no card-code
# table in its 86 pages, by design -- the mapping is not the READER's
# business.  The conclusion drawn from that, that therefore no 7030
# document could give the mapping, DOES NOT FOLLOW: it is the
# software's business, and C22-6678-1 printed p.56 prints it.  See the
# section below.  A unit manual's silence is evidence about that unit,
# not about the corpus.
#
# TWO CARDS, BECAUSE ONE WOULD HAVE PASSED.  Before this, every RD
# restarted the reader at device index 0 and card 2 came back
# bit-for-bit as card 1 -- a 32-word buffer, not a card reader.  A
# 7503 FEEDS.  StretchIO.bsv "CARD FEED"; io_reader_printer.strap
# passed throughout, because its second reader RD is SKIP-flagged and
# never reached a check.

run "Input-Output (reader/printer)" ./run_io_test.sh StretchIoReaderPrinterTb

# -- 7. Simulated tape drive (StretchIO.bsv, channel 34): RD/W/CCW plus
# CTL's two implemented tape functions, REWIND and BACKSPACE BLOCK
# (octal 136/176, p.132). Unlike the reader/printer test, this one's
# whole point is proving tape position is a persistent, mutable
# register -- two successive RDs must return different data, REWIND
# must reset it to 0, BACKSPACE BLOCK must move it back by exactly
# one (and reject at the load point with Exchange Program Check, per
# p.136), and an over-large count must trigger End Exception against
# the tape's own (deliberately small) capacity, not the reader/
# printer's. Expected values derived in gen_tape_tb.py by walking the
# same position transitions io_tape.strap's own header documents.
#
# STEPS 10-11 close the opcode audit's list: RD(SEOP) and CTL(SEOP),
# the last two operations the model implemented and nothing drove.  A
# SEOP form must not set the control word's EOP bit on completion
# (p.121).  ORDER IS THE WHOLE TRICK: CTL reads the CHANNEL's existing
# control word instead of adopting a fresh one from storage, so its eop
# has to be 0 going in, and only a preceding SEOP operation leaves it
# that way -- the same shape as io_reader_printer's W(SEOP) before its
# REL(SEOP).  RD(SEOP) adopts CTLW7 wholesale and finishes without
# setting eop; CTL(SEOP) REWIND then reads that word back and must
# write it out untouched, so CCWL must equal CCWK bit for bit.
#
# STEPS 12-15 close the rest of the SEOP rule.  "if (!seop) cw.eop = 1"
# is written out SIX times in this model -- normal completion, the End
# Exception path, CTL REWIND, BACKSPACE BLOCK's two sub-cases, and REL.
# Steps 10-11 and io_reader_printer drive three; these drive the other
# three, which had survived their mutations for 11 minutes apiece.
# Each expectation is the existing NON-SEOP one with eop=0 -- compare
# exp_ccwI and exp_ccwJ, the same operations without SEOP -- so the
# predictions come from values the suite already verifies.  Measured,
# one mutation per copy, each failing exactly ONE check and the right
# one: end exception -> CCWP, backspace at the load point -> CCWM,
# backspace success -> CCWO.
#
# ONE RULE, SIX COPIES.  This is the effAddr lesson in a second place:
# a test of one copy says nothing about the others, and how many copies
# exist is a fact about the code, not something a test can report.
#
# Two injections, and the second is why BOTH checks exist:
#   RD ignores its SEOP flag  -> CCWK fails (and CCWL with it, since
#                                CCWL inherits the same control word)
#   CTL ignores its SEOP flag -> CCWL fails ALONE, CCWK still passing
# The difference in each case is the single EOP bit, 0x1662.. against
# 0x1660...  Without CCWL, a CTL that ignored SEOP would be invisible.
run "Input-Output (tape)" ./run_tape_test.sh StretchIoTapeTb

# -- THE DISK (IBM 7612 synchronizer + 353 storage), channel 0 --------
# docs/disk_subsystem.md.  Thirteen checks, none of them through a
# peek method: every one is either a core word the program read BACK
# off the platter or a control word a COPY CONTROL WORD left behind.
# A peek would check that the model wrote what the model wrote.
#
# THE FOUR RULES IT PINS, each from the disk chapter and not from the
# Exchange's:
#
#   LOCATE SETS AN ARC and READ/WRITE start at that arc's FIRST word
#   (printed p.161).  A model that carried a word position forward the
#   way the tape does would read back the wrong words.
#
#   A SHORT WRITE ZERO-FILLS THE REST OF ITS ARC (printed p.160: "the
#   remainder of the last arc will be automatically filled with
#   zeros").  The destination buffers are pre-filled with all ones in
#   the deck, so "fill" and "never transferred" are distinguishable.
#
#   THE ARC REGISTER ADVANCES BY ITSELF (printed p.161: "As successive
#   arcs are used, this register is increased by one for each arc").
#   Step 3's WRITE names no arc and its data has to land in arc 1.
#
#   THE CONTROL WORD KEEPS ONLY TWO FIELDS (printed p.158: "No use is
#   made of control word flag bits or refill field").  CTLW1 is
#   patched with CHAIN, MULTIPLE, SKIP and a refill pointing at CTLW2.
#   ON THE EXCHANGE THAT WORD WOULD CHAIN -- Figure 36's "Chain and
#   continue" row, which this model implements and IPL depends on --
#   and on the disk it must transfer once and come back with all four
#   fields zero.  That is the sharpest check in the file: the same
#   control word, two different machines.
#
# CHANNEL 0 IS NOT AN INVENTION.  MCP printed p.15 line 26 and p.16
# lines 13 and 22 all address the disk with a left effective address
# of zero, and both pages are transcribed bit-exactly in decks/.  The
# cost was io_reader_printer.strap's unit-not-ready test, which used
# to mean "channel 0, nothing there" and now says channel 31.
run "THE DISK: LOCATE, arcs, the zero-filled tail, and flags discarded" ./run_disk_test.sh StretchIoDiskTb

# -- cleanup: generated .bsv testbenches and Bluesim build products are
# not meant to be committed (see .gitignore) --
rm -f "$BSV_DIR"/StretchProblem*Tb.bsv "$BSV_DIR"/StretchFigure*Tb.bsv "$BSV_DIR"/StretchXwRefillTb.bsv "$BSV_DIR"/StretchIoReaderPrinterTb.bsv "$BSV_DIR"/StretchIoTapeTb.bsv "$BSV_DIR"/StretchIoDiskTb.bsv "$BSV_DIR"/StretchXmitTb.bsv "$BSV_DIR"/StretchLvsTb.bsv "$BSV_DIR"/StretchIboxWenTb.bsv "$BSV_DIR"/StretchIboxCbTb.bsv "$BSV_DIR"/StretchIboxCbrTb.bsv
rm -f "$BSV_DIR"/*_sim "$BSV_DIR"/*_sim.so
rm -rf "$BSV_DIR"/build "$BSV_DIR"/simbuild

if [ "$FAILED" -ne 0 ]; then
  echo "*** ONE OR MORE TESTS FAILED ***" >&2
  exit 1
fi
echo "All regression tests passed."
