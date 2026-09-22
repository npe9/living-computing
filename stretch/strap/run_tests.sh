#!/bin/sh
# run_tests.sh -- the full regression suite: the hand-assembled BSV smoke
# test plus every STRAP program in programs/ that has a verified expected
# result. Exists because these invocations (and, for Figure 7, the
# expected-result derivation) previously lived only in conversation
# scrollback and had to be reconstructed from scratch more than once --
# see strap/README.md "Gotchas" item 7's postscript.
#
# Usage: ./run_tests.sh          (from stretch/strap/)

set -e
STRAP_DIR="$(cd "$(dirname "$0")" && pwd)"
BSV_DIR="$STRAP_DIR/../bsv"
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
run "Branch-on-Bit sets an indicator bit" ./run_program.sh programs/bb_indicator.strap StretchBBIndTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/bb_indicator.strap").read()).symtab["PASS"]//32)')"

# -- 0d''''. Store Zero to the indicator register (Z,$IND) clears bits
# 20-63 (p.41): BB1 sets AH, Z,$IND clears it, BB confirms it is off.
# Halts at PASS iff the clear took effect (folded into `ind`, since
# writeWord(11) is a no-op). Injection (fold removed): halts at FAIL.
# This is the diagnostic's own indicator reset before each test.
run "Store Zero clears the indicator register" ./run_program.sh programs/z_ind_clear.strap StretchZIndTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/z_ind_clear.strap").read()).symtab["PASS"]//32)')"

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
run "Index result indicators (LVNI, LCI, LRI, C+I)" ./run_program.sh programs/index_result_indicators.strap StretchIndexResultIndTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/index_result_indicators.strap").read()).symtab["PASS"]//32)')"

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
run "B(IND) routine, all five groups (model)" ./run_program.sh programs/ibox1_bind.strap StretchIbox1BindTb \
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
run "B(IND) XL/XE/XH blocks (indicator register written by SV)" ./run_program.sh programs/ibox1_bind_ind.strap StretchIbox1BindIndTb \
    "PC=4240"          # 004110.00, the half-word after IBIN55's second NOP

run "Storage protection, gated on the interrupt enable bit" ./run_program.sh programs/storage_protection.strap StretchProtTb \
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

run "Storage protection: the address boundary registers" ./run_program.sh programs/storage_protection_boundary.strap StretchProtBndTb \
    "PC=4305"          # 004150.40; hand-written, not a listing fact
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
#   python3 line_addresses.py programs/storage_protection_boundary.strap
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
# Block 16086 is IBM's own test of the same rule, and its error
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
# comes AFTER "16086A BD,$+.32", never before.  That is the "a program
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
# labelled 16088 at 021400.00, and the page then looked a half-word
# short.  Re-read at 600 dpi it prints 021400.40.  The encoding here
# says the same independently -- "B,16088" prints "21400.50 00" and
# bit 18 is the top bit of that octal pair -- but note that L16088's
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
# The 16086 fragment cannot run: it needs 16085B's all-NOP interrupt
# table (built by 16085A), the SEN/SERS error harness and the constant
# 160K16.  storage_protection.strap remains the behavioural test and
# remains hand-written; what changed is that its rule now has a deck
# behind it.  Four injections, each with its own named failure set,
# are recorded in verify_ax5b_16086_listing.py's header.

run "I-Box 5 routine 1260's indicator walk + TRANSMIT IMMEDIATE (jb_ax5b p.45)" python3 verify_ax5b_16087_listing.py
# THE BLOCK docs/NEXT.md HAS POINTED AT SINCE 2026-09-21, and the
# reason it waited: it needed an instruction this assembler did not
# have.  Six half-words -- set one indicator bit in word 11, set its
# mask bit in word 12, "BE,$+.32  -ENABLE AND AWAIT INTERRUPT", and a
# BD that is reached only if the machine did NOT interrupt, dispatching
# into the per-indicator error table 160B13 indexed by X6.  It is the
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
# label 160B13.  Dropping the index field in enc_branch_or_misc fails
# this row and only this row.
#
# THREE SYMBOLS LOCATED, each from its own row's printed address field:
# 160SX1 = 023041.00, 160S1 = 022741.00, 160B13 = 021402.40.
# docs/NEXT.md had carried 160S1/160SX1 as "not located" ever since the
# claim that they were a prerequisite was disproved.  And BIT0 =
# 024522.00 for the third independent time (p.114's table prints it,
# 16071's BIT18 implies it, this row's A1 field states it).
#
# THE HAZARD THIS CREATES, stated because the assembler can now emit
# Transmit at all: StretchExecute.bsv's Transmit arm moves exactly ONE
# word and ignores both the immediate-count bit and J, so a count other
# than 1 would assemble correctly and execute wrongly rather than
# failing loud.  Every count in this block is 1.  Recorded in
# TRANSMIT_CODES, in strap_asm.py's format list and in strap/README.md.

run "I-Box 5 routine 1260's TS block, bit-exact (jb_ax5b p.41)" python3 verify_ax5b_16071_listing.py
# THE INTERVAL TIMER GETS A SECOND DECK ORACLE, eight rows long.
# Reference Manual p.44: "4. Time Signal (TS).  The interval timer has
# become zero."  16071 loads the timer with the value ONE, spins 512
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
# from this one.  Note the symmetry with 16086, which uses the SAME
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

run "I-Box 5 routine 1260's OP and AD blocks, bit-exact (jb_ax5b pp.41-42)" python3 verify_ax5b_16082_16083_listing.py
# TWO MORE BLOCKS FROM THE SAME ROUTINE, and they exist for one row
# pair.  16082 and 16083 are contiguous (017225.00-017234.40) and both
# branch to the SAME target through DIFFERENT indicator numbers:
#
#     BOP,16088   21400.47 C2      indicator 15
#     BAD,16088   21400.50 42      indicator 16
#
# WHY THAT PAIR IS WORTH A FILE.  enc_branch_ind puts the 6-bit
# indicator number at bits 19-24, and the listing prints bits 18-23 as
# an octal pair and 24-31 as hex -- so the number STRADDLES the two
# printed fields, five bits in one and one in the other.  Two rows with
# the same address and adjacent numbers differ in BOTH fields at once.
# The injection proves the point: moving OP from 15 to 14 leaves the
# octal pair at .47 untouched and shows up ONLY in the hex byte, which
# a check reading one field would have missed.  The 16086 block's
# BDS/BADZ (19 and 16) never exercised a number whose top bit differs.
#
# A THIRD AND FOURTH WITNESS FOR 16088 AT 021400.40, and this time from
# pp.41-42 rather than pp.43-45.  Both rows carry bit 18 of the target
# set.  The address a 200 dpi render got wrong is now agreed on by two
# pages and three encodings -- but note the provenance: L16088's .40 is
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
# both fall through into the SEN/SERS error harness and 16093, none of
# it transcribed, and 160K7's contents are not printed on these pages.
# The block's SHAPE -- store a word over a zeroed full-word slot, two
# NOPs, then fall straight INTO the slot -- reads like self-modifying
# code planting an invalid operation code, which is what "-OP" and
# "UNABLE TO TURN OP ON." would need; that is inference and the
# program's header says so.

run "The interruption mechanism (fire, one instruction, return)" ./run_program.sh programs/interrupt_pg0.strap StretchIntPg0Tb \
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
# "160IT  DR%BU,64,8@,64" at 023201.00 with the next symbol 160DMP at
# 023301.00 -- a gap of octal 100, exactly 64 WORDS, holding the 48
# maskable indicators with room over.  The three consecutive HALF-words
# at 16090 (p.48, "HI,BEFORE / OK, AT / LO,AFTER ... INTRPTS ENTER
# HERE") that looked like half-word slots are a TEMPLATE copied into
# those word slots -- p.86 has "160K6  BD,16090" as a single half-word
# at 023047.00.  See docs/NEXT.md for the full reasoning.
#
# Ten injections; every address reproducible with
#   python3 line_addresses.py programs/interrupt_pg0.strap
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
# NOT IMPLEMENTED, stated in StretchCore: the interruption is taken at a
# QUIESCENT boundary (look-ahead empty, E-box idle) rather than p.48's
# instruction boundary; on the real machine an interruption drains the
# look-ahead, so the two coincide when the levels are empty and this one
# is otherwise LATER, never earlier.  An E-box-class interruption
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

run "TRANSMIT: what is honoured, and what is refused out loud" ./run_program.sh programs/transmit_scope.strap StretchTransmitScopeTb \
    "PC=4248" "DST1:2177=0x9249249249249249" "DST2:2178=0" "DST3:2179=0" \
    "DST4:2180=0" "DST5:2181=0" "DST6:2182=0" "SRC:2176=0x9249249249249249"
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

run "BR (Branch Relative)" ./run_program.sh programs/br_relative.strap StretchBrRelTb \
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

run "BB branch-if-off variants (BZB1, BZBN, BZBZ)" ./run_program.sh programs/bb_branch_if_off.strap StretchBbOffTb \
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
# programs/op_ad_indicators.strap below, so KNOWN_GAP is empty and the
# ratchet holds at "every indicator the model writes is named by some
# program".  That is a floor, not a ceiling: see the caveat above.

run "OP and AD indicators (both polarities)" ./run_program.sh programs/op_ad_indicators.strap StretchOpAdIndTb \
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

run "AD by SIC below 16.0 (the other trigger)" ./run_program.sh programs/ad_sic_indicator.strap StretchAdSicTb \
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

run "Index result indicators: OFF states and clearing" ./run_program.sh programs/index_indicators_off.strap StretchIndexIndOffTb \
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

run "Index compares set XF (a fixed bug with no test)" ./run_program.sh programs/cmp_sets_index_flag.strap StretchCmpXfTb \
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

run "Branch target modified by an index register" ./run_program.sh programs/branch_index_modified.strap StretchBrIdxTb \
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

run "Address modification by a NEGATIVE index value" ./run_program.sh programs/index_negative_modifier.strap StretchNegIdxTb \
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

run "Negative index modification on the FP path (third copy)" ./run_program.sh programs/fp_negative_modifier.strap StretchFpNegIdxTb \
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

run "Mask register fixed and writable fields (word 12)" ./run_program.sh programs/mask_register_fields.strap StretchMaskTb \
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

run "ZM's normalized term and exponent bound" ./run_program.sh programs/fp_zm_terms.strap StretchFpZmTb \
    "PC=3352"          # 003214.00; hand-written, not a listing fact

run "ZM on the DOUBLE multiply (the copy nothing tested)" ./run_program.sh programs/fp_zm_terms_double.strap StretchFpZmDblTb \
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

run "Every FP operation but MULTIPLY clears ZM" ./run_program.sh programs/fp_zm_cleared.strap StretchFpZmClrTb \
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
cd "$STRAP_DIR"

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
run "I-box timing: CB loop" ./run_program.sh programs/ibox_timing_cb.strap StretchTimingCbTb \
    "X1_count:addrIndex(1)=0" \
    "CYCLES<=300"

# -- 1c. Look-ahead timing microbenchmark: four full-word VFL loads,
# E-box-bound with fetch-ahead (~115 clocks, measured 120) vs ~172
# executed serially; the bound of 140 fails if the overlap is lost
# (as it was when the E-box busy wait preempted preparation).
run "Look-ahead timing: four loads" ./run_program.sh programs/la_timing_loads.strap StretchTimingLaTb \
    "ACC_right:9=4" \
    "CYCLES<=140"

# -- 1d. I-box run-ahead benchmark: a ten-iteration L/+/ST loop closed
# by V+ and CB. E-box-bound with the I-box instructions hidden (~800
# clocks, measured 807) vs ~1120 if the I-box waited for the levels to
# drain each time; bound 900.
run "Look-ahead timing: L/+/ST/V+/CB loop" ./run_program.sh programs/la_timing_loop.strap StretchTimingLoopTb \
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
run "Look-ahead: branch guess + recovery" ./run_program.sh programs/la_branch_guess.strap StretchGuessTb \
    "X1_4:addrIndex(1)=0x1000000000000" \
    "X2_2:addrIndex(2)=0x800000000000" \
    "X3_zero:addrIndex(3)=0" \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/la_branch_guess.strap").read()).symtab["DONE"]//32)')" \
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
run "FP compare block (jb_af1c F202A15-20 on the model)" ./run_program.sh programs/fp_compare_f202a.strap StretchFpCmpTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_compare_f202a.strap").read()).symtab["PASS"]//32)')"

# -- 1i''. Companion block from the start of the same routine (F202A1-6,
# p.30): FP compares in the NORMAL exponent range, including the AE
# (equal) outcome (FPK0 vs FPK0). Encoding bit-for-bit, then the model
# run halts at PASS iff every compare sets the expected indicator.
run "FP compare block (jb_af1c F202A1-6, encoding)" python3 verify_fp_compare_a1_listing.py
run "FP compare block (jb_af1c F202A1-6 on the model)" ./run_program.sh programs/fp_compare_f202a1.strap StretchFpCmpA1Tb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_compare_f202a1.strap").read()).symtab["PASS"]//32)')"

# -- 1i'''. KR Compare-for-Range (jb_af1c F202G11-18, p.45): eight
# sub-tests pairing AH-on (BB1,$AH gate) with AH-off (Z,$IND gate) over
# five operand pairs. Encoding bit-for-bit, then the model run halts at
# PASS iff KR obeys p.91 (sets AE=acc-low when AH on, leaves AL/AH).
# Injection (KR AE forced off): halts at SERS at G15.
run "FP compare block (jb_af1c F202G KR range, encoding)" python3 verify_fp_compare_g_listing.py
run "FP compare block (jb_af1c F202G KR range on the model)" ./run_program.sh programs/fp_compare_f202g.strap StretchFpCmpGTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_compare_f202g.strap").read()).symtab["PASS"]//32)')"

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
run "FP M+ block (jb_af1c F204A5 on the model)" ./run_program.sh programs/fp_arith_f204a5.strap StretchFpAdd5Tb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f204a5.strap").read()).symtab["PASS"]//32)')"

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
run "FP M+ sign modifiers (jb_af1c F204B on the model)" ./run_program.sh programs/fp_arith_f204b.strap StretchFpAddBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f204b.strap").read()).symtab["PASS"]//32)')" \
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
run "FP M+ unchanged registers (jb_af1c F204C on the model)" ./run_program.sh programs/fp_arith_f204c.strap StretchFpAddCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f204c.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- 1i''''''''. jb_af1c F204D (pp.60-64): the indicators ADD TO MEMORY
# sets -- MOP, RLZ/RN, RZ, RGZ, PSH on/off, LC, LS on/off, and the
# five exponent-range indicators one at a time -- sixteen sub-tests.
# First run caught a look-ahead ordering bug: Z,$IND ran ahead of the
# unretired L(U) level that sets XPL. An I-box store to words 7-15 now
# drains the look-ahead (StretchIBox.bsv eboxRegister) -- see the
# program header.
run "FP M+ indicators (jb_af1c F204D, encoding)" python3 verify_fp_arith_f204d_listing.py
run "FP M+ indicators (jb_af1c F204D on the model)" ./run_program.sh programs/fp_arith_f204d.strap StretchFpAddDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f204d.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- 1i'''''''''. jb_af1c F204E (p.65): the normalization modifier on
# ADD TO MEMORY -- ignored when the result is a flagged operand (XFP
# or XFN), applied when it is the unflagged survivor of XFN + N or an
# N + N sum. First run caught fpAdd suppressing normalization of an
# unflagged survivor (E4: FPK7 came back unnormalized, FPK6 expected)
# -- see the program header.
run "FP M+ normalization modifier (jb_af1c F204E, encoding)" python3 verify_fp_arith_f204e_listing.py
run "FP M+ normalization modifier (jb_af1c F204E on the model)" ./run_program.sh programs/fp_arith_f204e.strap StretchFpAddETb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f204e.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- 1k. jb_af1c F205A (p.66): ADD TO MAGNITUDE (+MG) arithmetic checks,
# nine sub-tests -- flagged operands dominating, an N + N sum, and the
# forced-zero case (XFN accumulator + negative XFP operand: exponent
# of the survivor, zero fraction), checked in the accumulator's left
# half at offset 68 / 116. First run caught the flagged-operand path
# skipping the forced-zero rule -- see the program header.
run "FP +MG arithmetic (jb_af1c F205A, encoding)" python3 verify_fp_arith_f205a_listing.py
run "FP +MG arithmetic (jb_af1c F205A on the model)" ./run_program.sh programs/fp_arith_f205a.strap StretchFpMgATb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f205a.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- 1k'. jb_af1c F205B (pp.67-72): +MG / +MGA / -MG / -MGA over every
# memory-sign / accumulator-sign combination, thirty-two sub-tests,
# each checking the accumulator at offset 68 and its sign bit at
# $SB+.4. Establishes that the result keeps the accumulator's own sign
# (forced zeros included) -- see the program header.
run "FP +MG sign modifiers (jb_af1c F205B, encoding)" python3 verify_fp_arith_f205b_listing.py
run "FP +MG sign modifiers (jb_af1c F205B on the model)" ./run_program.sh programs/fp_arith_f205b.strap StretchFpMgBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f205b.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- 1k''. jb_af1c F205C + F205D (pp.73-74): +MG leaves the right half,
# the sign byte's bits 0-3 and 5-7 and the left half's bits 60-63
# alone (zeros and ones), and the LS indicator: on for x + (-x), off
# for 0 + 0, off for a forced zero, off for a propagated flagged
# operand -- see the program header.
run "FP +MG unchanged registers and LS (jb_af1c F205C/D, encoding)" python3 verify_fp_arith_f205cd_listing.py
run "FP +MG unchanged registers and LS (jb_af1c F205C/D on the model)" ./run_program.sh programs/fp_arith_f205cd.strap StretchFpMgCDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f205cd.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- 1l. jb_af1c F206A (pp.75-77): ADD MAGNITUDE TO MEMORY (M+MG),
# fifteen arithmetic checks -- the same flagged-operand dominance as
# +MG but with the result in storage, and the forced zero that keeps
# the ADDRESSED operand's sign and exponent (A9), plus the
# normalization modifier over flagged and N results (A10-A15). A9
# caught fpAdd applying +MG's forced-zero rule in the to-memory
# direction -- see the program header.
run "FP M+MG arithmetic (jb_af1c F206A, encoding)" python3 verify_fp_arith_f206a_listing.py
run "FP M+MG arithmetic (jb_af1c F206A on the model)" ./run_program.sh programs/fp_arith_f206a.strap StretchFpMgMemATb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f206a.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- 1l'. jb_af1c F206B (pp.78-84): ADD MAGNITUDE TO MEMORY over every
# memory-sign / accumulator-sign / N / A combination, thirty-two
# sub-tests, each checking ROS's exponent and fraction at offset 4 and
# its sign bit by BZB/BB. Establishes that the accumulator operand's
# sign is the one assumed positive, and that the result keeps the
# ADDRESSED operand's own sign whatever the sum's -- B19 caught the
# model storing the sum's. See the program header.
run "FP M+MG sign modifiers (jb_af1c F206B, encoding)" python3 verify_fp_arith_f206b_listing.py
run "FP M+MG sign modifiers (jb_af1c F206B on the model)" ./run_program.sh programs/fp_arith_f206b.strap StretchFpMgMemBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f206b.strap").read()).symtab["PASS"]//32)')" \
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
run "FP M+MG unchanged registers (jb_af1c F206C on the model)" ./run_program.sh programs/fp_arith_f206c.strap StretchFpMgMemCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f206c.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP M+MG indicators (jb_af1c F206D, encoding)" python3 verify_fp_arith_f206d_listing.py
run "FP M+MG indicators (jb_af1c F206D on the model)" ./run_program.sh programs/fp_arith_f206d.strap StretchFpMgMemDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f206d.strap").read()).symtab["PASS"]//32)')" \
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
run "FP load double (jb_af1c F207A on the model)" ./run_program.sh programs/fp_arith_f207a.strap StretchFpLoadDblATb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f207a.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- 1m'. jb_af1c F207B (p.90) and F207C/F207D (p.90): the rest of
# LOAD DOUBLE. B, that bits 108-127 survive a DL (ones stay ones, zeros
# stay zeros -- the twenty bits below the double fraction). C, that the
# sign byte's flag bits 5-7 are zeroed. D, that the data flag
# indicators follow the ADDRESSED operand's flags. C1 caught the E-box
# register interlock below.
run "FP load double unchanged registers (jb_af1c F207B, encoding)" python3 verify_fp_arith_f207b_listing.py
run "FP load double unchanged registers (jb_af1c F207B on the model)" ./run_program.sh programs/fp_arith_f207b.strap StretchFpLoadDblBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f207b.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP load double flags and indicators (jb_af1c F207C/D, encoding)" python3 verify_fp_arith_f207cd_listing.py
run "FP load double flags and indicators (jb_af1c F207C/D on the model)" ./run_program.sh programs/fp_arith_f207cd.strap StretchFpLoadDblCDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f207cd.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- 1j'. E-box-register-close-to-fetch: an E-box instruction writes one
# of words 7-15 and the very next instruction addresses that word as a
# storage operand. The sibling of store-close-to-fetch below, for the
# registers storeTarget() deliberately does not report. Found by
# jb_af1c F207C1; this exact pair read the stale sign byte before the
# fix.
run "Look-ahead: E-box-register-close-to-fetch" ./run_program.sh programs/ebox_register_close_to_fetch.strap StretchEboxRegScfTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/ebox_register_close_to_fetch.strap").read()).symtab["PASS"]//32)')" \
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
run "FP load double with flag (jb_af1c F207E on the model)" ./run_program.sh programs/fp_arith_f207e.strap StretchFpLoadDblETb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f207e.strap").read()).symtab["PASS"]//32)')" \
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
run "FP add double (jb_af1c F208A1-A20 on the model)" ./run_program.sh programs/fp_arith_f208a.strap StretchFpAddDblATb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f208a.strap").read()).symtab["PASS"]//32)')" \
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
run "FP add double signs (jb_af1c F208B1-B7 on the model)" ./run_program.sh programs/fp_arith_f208b.strap StretchFpAddDblBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f208b.strap").read()).symtab["PASS"]//32)')" \
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
run "FP add double unchanged regs (jb_af1c F208C1-C2 on the model)" ./run_program.sh programs/fp_arith_f208c.strap StretchFpAddDblCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f208c.strap").read()).symtab["PASS"]//32)')" \
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
run "FP add double indicators (jb_af1c F208D1-D6 on the model)" ./run_program.sh programs/fp_arith_f208d1_6.strap StretchFpAddDblDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f208d1_6.strap").read()).symtab["PASS"]//32)')" \
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
run "FP add double exp range (jb_af1c F208D7-D11 on the model)" ./run_program.sh programs/fp_arith_f208d7_11.strap StretchFpAddDblETb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f208d7_11.strap").read()).symtab["PASS"]//32)')" \
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
run "FP add double magnitude (jb_af1c F209A1-A9 on the model)" ./run_program.sh programs/fp_arith_f209a.strap StretchFpAddDblMgATb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f209a.strap").read()).symtab["PASS"]//32)')" \
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
run "FP add double magnitude signs (jb_af1c F209B1-B8 on the model)" ./run_program.sh programs/fp_arith_f209b1_8.strap StretchFpAddDblMgBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f209b1_8.strap").read()).symtab["PASS"]//32)')" \
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
run "FP add double magnitude signs 2 (jb_af1c F209B9-B13 on the model)" ./run_program.sh programs/fp_arith_f209b9_13.strap StretchFpAddDblMgCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f209b9_13.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# jb_af1c F209B14-B16 (p.105): the last three, with BOTH signs
# negative -- DLN accumulator and FPK40 operand -- closing F209B's
# grid. With these the routine is transcribed end to end, 015365.40
# to 015574.40 across three programs, each ending where the next
# begins. Still no forced zero anywhere in F209B.
run "FP add double magnitude signs 3 (jb_af1c F209B14-B16, encoding)" python3 verify_fp_arith_f209b14_16_listing.py
run "FP add double magnitude signs 3 (jb_af1c F209B14-B16 on the model)" ./run_program.sh programs/fp_arith_f209b14_16.strap StretchFpAddDblMgDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f209b14_16.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# jb_af1c F209C (pp.105-106): "UNCHANGED REGISTERS" for D+MG. Unlike
# F208C, which checked only sign byte bits 5-7 with a 3-bit field at
# 10.5, this checks all EIGHT bits at 10.0 -- so C2 covers the sign
# (bit 4) as well as the flags. Two injections halt on it (SIC stores
# 015614.40): not restoring the accumulator's own sign, and taking the
# sign byte's flags from the result instead of from accS.
run "FP add double magnitude unchanged regs (jb_af1c F209C1-C2, encoding)" python3 verify_fp_arith_f209c_listing.py
run "FP add double magnitude unchanged regs (jb_af1c F209C1-C2 on the model)" ./run_program.sh programs/fp_arith_f209c.strap StretchFpAddDblMgETb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f209c.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# jb_af1c F209D1-D5 (pp.106-107): D+MG's arithmetic result indicators
# RLZ, RZ, RGZ and RN. D1 and D2 load the accumulator NEGATIVE with
# DLN, and D+MG assumes it positive for the addition -- so the sign
# has to be restored before the INDICATORS are set, not merely before
# the sign byte is written. Restoring it only at the byte write leaves
# F209C passing and halts at D1's BZRLZ (SIC stores 015620.00).
run "FP add double magnitude indicators (jb_af1c F209D1-D5, encoding)" python3 verify_fp_arith_f209d1_5_listing.py
run "FP add double magnitude indicators (jb_af1c F209D1-D5 on the model)" ./run_program.sh programs/fp_arith_f209d1_5.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f209d1_5.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# F209D6-D9, the Lost Significance half of the same routine. D7 (zero
# plus zero must NOT set LS) is the printed source of the exception
# clause in the F208D5 LS fix; D9 is the first LS question put to the
# flagged path, where fpAddDouble returns a survivor whole.
run "FP add double magnitude LS indicator (jb_af1c F209D6-D9, encoding)" python3 verify_fp_arith_f209d6_9_listing.py
run "FP add double magnitude LS indicator (jb_af1c F209D6-D9 on the model)" ./run_program.sh programs/fp_arith_f209d6_9.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f209d6_9.strap").read()).symtab["PASS"]//32)')" \
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
run "FP add double magnitude forced zero (jb_af1c F209E1-E4 on the model)" ./run_program.sh programs/fp_arith_f209e1_4.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f209e1_4.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# F209E5-E8 reach the same forced zero from the other side: FPK43 is
# FPK37 with its sign bit set, so D+MG adds a NEGATIVE operand of
# larger magnitude instead of subtracting a positive one. E6 and E8 use
# D-MGA, whose A-then-minus double inversion lands on the same
# arithmetic by a different route through strip_fp_sign.
run "FP add double magnitude forced zero (jb_af1c F209E5-E8, encoding)" python3 verify_fp_arith_f209e5_8_listing.py
run "FP add double magnitude forced zero (jb_af1c F209E5-E8 on the model)" ./run_program.sh programs/fp_arith_f209e5_8.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f209e5_8.strap").read()).symtab["PASS"]//32)')" \
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
run "FP add double magnitude forced zero, LS off (jb_af1c F209E9 on the model)" ./run_program.sh programs/fp_arith_f209e9.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f209e9.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- F210 STORE ROUNDED. A1-A2 are the diagnostic that drove writing
# SRD's execute arm (it decoded but set OP-invalid before this). Both
# are the flagged case: a 96-bit all-ones accumulator fraction, so the
# +1 at IBM 60 carries the whole way out, the overflow is lost and the
# exponent is unchanged -- expecting FK35 (XFP) and FPK59 (XFN) with a
# ZERO fraction, plus a BZB on the stored sign bit.
run "FP store rounded (jb_af1c F210A1-A2, encoding)" python3 verify_fp_arith_f210a1_2_listing.py
run "FP store rounded (jb_af1c F210A1-A2 on the model)" ./run_program.sh programs/fp_arith_f210a1_2.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f210a1_2.strap").read()).symtab["PASS"]//32)')" \
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
run "FP store rounded, N range (jb_af1c F210A3-A4 on the model)" ./run_program.sh programs/fp_arith_f210a3_4.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f210a3_4.strap").read()).symtab["PASS"]//32)')" \
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
run "FP store rounded, unnormalized overflow (jb_af1c F210A5 on the model)" ./run_program.sh programs/fp_arith_f210a5.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f210a5.strap").read()).symtab["PASS"]//32)')" \
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
run "FP store rounded, normalization suppressed (jb_af1c F210A6-A7 on the model)" ./run_program.sh programs/fp_arith_f210a6_7.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f210a6_7.strap").read()).symtab["PASS"]//32)')" \
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
run "FP store rounded, normalization process (jb_af1c F210A8 on the model)" ./run_program.sh programs/fp_arith_f210a8.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f210a8.strap").read()).symtab["PASS"]//32)')" \
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
run "FP store rounded, unchanged registers (jb_af1c F210B on the model)" ./run_program.sh programs/fp_arith_f210b.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f210b.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# F210C "ACCUMULATOR FLAGS TO MEMORY FLAGS" guards the other half of
# p.96's storage-word sentence: the accumulator flag bits go to storage
# bits 61-63. F210A checked bit 60 (the sign) with its BZB questions
# and nothing had looked at 61-63. C1 pre-loads ROS with ONES before
# zeroing the accumulator, which makes it a test of copying rather than
# of leaving alone.
run "FP store rounded, flags to memory (jb_af1c F210C, encoding)" python3 verify_fp_arith_f210c_listing.py
run "FP store rounded, flags to memory (jb_af1c F210C on the model)" ./run_program.sh programs/fp_arith_f210c.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f210c.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# F210D "TESTS OF INDICATORS" closes F210 out, and D2 is the LOST CARRY
# oracle recorded as missing since A5. Every block from A1 to C2 checked
# what SRD STORED and never asked about an indicator. D1 asks that MOP
# comes on; D2 clears LC, runs the same 96-ones operand A5 uses, and
# asks that the rounding overflow set LC. A5 and D2 are the two halves
# of one rule -- what the overflow did to the word, and to the
# indicator -- and the model takes both from the same lostCarry.
run "FP store rounded, MOP and LC indicators (jb_af1c F210D, encoding)" python3 verify_fp_arith_f210d_listing.py
run "FP store rounded, MOP and LC indicators (jb_af1c F210D on the model)" ./run_program.sh programs/fp_arith_f210d.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f210d.strap").read()).symtab["PASS"]//32)')" \
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
run "FP store low order (jb_af1c F211A1-A2 on the model)" ./run_program.sh programs/fp_arith_f211a1_2.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f211a1_2.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# F211A3-A4 are the first UNFLAGGED SLO, and so the first exercise of
# its headline rule: the stored exponent is the accumulator's MINUS 48.
# A1-A2 are both flagged, where the exponent is kept unchanged, so
# neither can see the subtraction. A3 stores FPK28's fraction at
# 256-48=208 (FPK44) and A4 stores FPK38's at 50-48=2 (FPK39); the
# listing's own comments say "EXP+208" and "EXPONENT++2".
run "FP store low order, exponent minus 48 (jb_af1c F211A3-A4, encoding)" python3 verify_fp_arith_f211a3_4_listing.py
run "FP store low order, exponent minus 48 (jb_af1c F211A3-A4 on the model)" ./run_program.sh programs/fp_arith_f211a3_4.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f211a3_4.strap").read()).symtab["PASS"]//32)')" \
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
run "FP store low order, normalization modifier (jb_af1c F211A7-A10 on the model)" ./run_program.sh programs/fp_arith_f211a7_10.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f211a7_10.strap").read()).symtab["PASS"]//32)')" \
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
run "FP store low order, unchanged registers and MOP (jb_af1c F211B-C on the model)" ./run_program.sh programs/fp_arith_f211bc.strap StretchFpAddDblMgFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f211bc.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- F212 SHIFT FRACTION. The first block to exercise SHF as the 96-BIT
# -- operation Reference Manual p.102 describes ("only accumulator bits
# -- 12-107 participate"); the arm shifted only the 48-bit high half
# -- before this. A1-A11 cannot see that (DL zeroes the low half and
# -- they shift LEFT); A12 can, and does -- see that program's header.
run "FP shift fraction, left-shift walk (jb_af1c F212A1-A11, encoding)" python3 verify_fp_arith_f212a1_11_listing.py
run "FP shift fraction, left-shift walk (jb_af1c F212A1-A11 on the model)" ./run_program.sh programs/fp_arith_f212a1_11.strap StretchFpShfATb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f212a1_11.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"
run "FP shift fraction, 96-bit lost carry and right-shift walk (jb_af1c F212A12-A23, encoding)" python3 verify_fp_arith_f212a12_23_listing.py
run "FP shift fraction, 96-bit lost carry and right-shift walk (jb_af1c F212A12-A23 on the model)" ./run_program.sh programs/fp_arith_f212a12_23.strap StretchFpShfBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f212a12_23.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"
run "FP shift fraction, LC off / self-modifying / norm-mod / flagged (jb_af1c F212A24-A30, encoding)" python3 verify_fp_arith_f212a24_30_listing.py
run "FP shift fraction, LC off / self-modifying / norm-mod / flagged (jb_af1c F212A24-A30 on the model)" ./run_program.sh programs/fp_arith_f212a24_30.strap StretchFpShfCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f212a24_30.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

# -- Program store compare with an OBSERVABLE difference. F212A25 above
# -- is the diagnostic's own store-then-execute row, but it patches
# -- bits the shift ignores, so stale and fresh are both no-ops there:
# -- it proves the machine does not hang, not that the re-fetch saw the
# -- new word. This one makes the two outcomes different.
run "FP shift fraction, sign/modifier combinations (jb_af1c F212B, encoding)" python3 verify_fp_arith_f212b_listing.py
run "FP shift fraction, sign/modifier combinations (jb_af1c F212B on the model)" ./run_program.sh programs/fp_arith_f212b.strap StretchFpShfDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f212b.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"
run "FP shift fraction, unchanged registers (jb_af1c F212C, encoding)" python3 verify_fp_arith_f212c_listing.py
run "FP shift fraction, unchanged registers (jb_af1c F212C on the model)" ./run_program.sh programs/fp_arith_f212c.strap StretchFpShfETb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f212c.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"
run "FP shift fraction, indicator tests (jb_af1c F212D, encoding)" python3 verify_fp_arith_f212d_listing.py
run "FP shift fraction, indicator tests (jb_af1c F212D on the model)" ./run_program.sh programs/fp_arith_f212d.strap StretchFpShfFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f212d.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP add to fraction (jb_af1c F212XA, encoding)" python3 verify_fp_arith_f212xa_listing.py
run "FP add to fraction (jb_af1c F212XA on the model)" ./run_program.sh programs/fp_arith_f212xa.strap StretchFpAddFracTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f212xa.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP add to fraction, sign and modifiers (jb_af1c F212XB, encoding)" python3 verify_fp_arith_f212xb_listing.py
run "FP add to fraction, sign and modifiers (jb_af1c F212XB on the model)" ./run_program.sh programs/fp_arith_f212xb.strap StretchFpAddFracBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f212xb.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP add to fraction, unchanged regs (jb_af1c F212XC, encoding)" python3 verify_fp_arith_f212xc_listing.py
run "FP add to fraction, unchanged regs (jb_af1c F212XC on the model)" ./run_program.sh programs/fp_arith_f212xc.strap StretchFpAddFracCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f212xc.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP add to exponent, range table (jb_af1c F213A1-A9, encoding)" python3 verify_fp_arith_f213a1_9_listing.py
run "FP add to exponent, range table (jb_af1c F213A1-A9 on the model)" ./run_program.sh programs/fp_arith_f213a1_9.strap StretchFpAddExpTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f213a1_9.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP add to exponent, normalization (jb_af1c F213A10-A13, encoding)" python3 verify_fp_arith_f213a10_13_listing.py
run "FP add to exponent, normalization (jb_af1c F213A10-A13 on the model)" ./run_program.sh programs/fp_arith_f213a10_13.strap StretchFpAddExpNTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f213a10_13.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP add to exponent, sign modifiers (jb_af1c F213B, encoding)" python3 verify_fp_arith_f213b_listing.py
run "FP add to exponent, sign modifiers (jb_af1c F213B on the model)" ./run_program.sh programs/fp_arith_f213b.strap StretchFpAddExpBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f213b.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP add to exponent, unchanged regs (jb_af1c F213C, encoding)" python3 verify_fp_arith_f213c_listing.py
run "FP add to exponent, unchanged regs (jb_af1c F213C on the model)" ./run_program.sh programs/fp_arith_f213c.strap StretchFpAddExpCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f213c.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP add to exponent, result indicators (jb_af1c F213D1-D4, encoding)" python3 verify_fp_arith_f213d1_4_listing.py
run "FP add to exponent, result indicators (jb_af1c F213D1-D4 on the model)" ./run_program.sh programs/fp_arith_f213d1_4.strap StretchFpAddExpDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f213d1_4.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP add to exponent, range indicators (jb_af1c F213D5-D9, encoding)" python3 verify_fp_arith_f213d5_9_listing.py
run "FP add to exponent, range indicators (jb_af1c F213D5-D9 on the model)" ./run_program.sh programs/fp_arith_f213d5_9.strap StretchFpAddExpETb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f213d5_9.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP add immediate to exponent (jb_af1c F213XA, encoding)" python3 verify_fp_arith_f213xa_listing.py
run "FP add immediate to exponent (jb_af1c F213XA on the model)" ./run_program.sh programs/fp_arith_f213xa.strap StretchFpAddExpImmTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f213xa.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP add immediate, sign and mod combs (jb_af1c F213XB, encoding)" python3 verify_fp_arith_f213xb_listing.py
run "FP add immediate, sign and mod combs (jb_af1c F213XB on the model)" ./run_program.sh programs/fp_arith_f213xb.strap StretchFpAddExpImmBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f213xb.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP add immediate, unchanged regs (jb_af1c F213XC, encoding)" python3 verify_fp_arith_f213xc_listing.py
run "FP add immediate, unchanged regs (jb_af1c F213XC on the model)" ./run_program.sh programs/fp_arith_f213xc.strap StretchFpAddExpImmCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f213xc.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP multiply arithmetic checks (jb_af1c F214A, encoding)" python3 verify_fp_arith_f214a_listing.py
run "FP multiply arithmetic checks (jb_af1c F214A on the model)" ./run_program.sh programs/fp_arith_f214a.strap StretchFpMulTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f214a.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP multiply sign and modifiers (jb_af1c F214B, encoding)" python3 verify_fp_arith_f214b_listing.py
run "FP multiply sign and modifiers (jb_af1c F214B on the model)" ./run_program.sh programs/fp_arith_f214b.strap StretchFpMulBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f214b.strap").read()).symtab["POR5"]//32)')" \
    "SEN:712=0"

run "FP multiply unchanged regs (jb_af1c F214C, encoding)" python3 verify_fp_arith_f214c_listing.py
run "FP multiply unchanged regs (jb_af1c F214C on the model)" ./run_program.sh programs/fp_arith_f214c.strap StretchFpMulCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f214c.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP multiply indicator tests (jb_af1c F214D, encoding)" python3 verify_fp_arith_f214d_listing.py
run "FP multiply indicator tests (jb_af1c F214D on the model)" ./run_program.sh programs/fp_arith_f214d.strap StretchFpMulDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f214d.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP multiply double arithmetic (jb_af1c F214XA, encoding)" python3 verify_fp_arith_f214xa_listing.py
run "FP multiply double arithmetic (jb_af1c F214XA on the model)" ./run_program.sh programs/fp_arith_f214xa.strap StretchFpMulDblATb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f214xa.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP multiply double unchanged regs (jb_af1c F214XB, encoding)" python3 verify_fp_arith_f214xb_listing.py
run "FP multiply double unchanged regs (jb_af1c F214XB on the model)" ./run_program.sh programs/fp_arith_f214xb.strap StretchFpMulDblBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f214xb.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP load factor arithmetic (jb_af1c F215A, encoding)" python3 verify_fp_arith_f215a_listing.py
run "FP load factor arithmetic (jb_af1c F215A on the model)" ./run_program.sh programs/fp_arith_f215a.strap StretchFpLftATb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f215a.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP load factor sign and modifiers (jb_af1c F215B, encoding)" python3 verify_fp_arith_f215b_listing.py
run "FP load factor sign and modifiers (jb_af1c F215B on the model)" ./run_program.sh programs/fp_arith_f215b.strap StretchFpLftBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f215b.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP load factor changed regs (jb_af1c F215C, encoding)" python3 verify_fp_arith_f215c_listing.py
run "FP load factor changed regs (jb_af1c F215C on the model)" ./run_program.sh programs/fp_arith_f215c.strap StretchFpLftCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f215c.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP load factor unchanged regs (jb_af1c F215D, encoding)" python3 verify_fp_arith_f215d_listing.py
run "FP load factor unchanged regs (jb_af1c F215D on the model)" ./run_program.sh programs/fp_arith_f215d.strap StretchFpLftDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f215d.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP load factor result indicators (jb_af1c F215E, encoding)" python3 verify_fp_arith_f215e_listing.py
run "FP load factor result indicators (jb_af1c F215E on the model)" ./run_program.sh programs/fp_arith_f215e.strap StretchFpLftETb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f215e.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP load factor normalization modifier (jb_af1c F215F, encoding)" python3 verify_fp_arith_f215f_listing.py
run "FP load factor normalization modifier (jb_af1c F215F on the model)" ./run_program.sh programs/fp_arith_f215f.strap StretchFpLftFTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f215f.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP multiply and add arithmetic (jb_af1c F216A, encoding)" python3 verify_fp_arith_f216a_listing.py
run "FP multiply and add arithmetic (jb_af1c F216A on the model)" ./run_program.sh programs/fp_arith_f216a.strap StretchFpMulAddATb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f216a.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP multiply and add sign and modifiers (jb_af1c F216B, encoding)" python3 verify_fp_arith_f216b_listing.py
run "FP multiply and add sign and modifiers (jb_af1c F216B on the model)" ./run_program.sh programs/fp_arith_f216b.strap StretchFpMulAddBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f216b.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP multiply and add unchanged regs (jb_af1c F216C, encoding)" python3 verify_fp_arith_f216c_listing.py
run "FP multiply and add unchanged regs (jb_af1c F216C on the model)" ./run_program.sh programs/fp_arith_f216c.strap StretchFpMulAddCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f216c.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP multiply and add indicators (jb_af1c F216D, encoding)" python3 verify_fp_arith_f216d_listing.py
run "FP multiply and add indicators (jb_af1c F216D on the model)" ./run_program.sh programs/fp_arith_f216d.strap StretchFpMulAddDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f216d.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP divide arithmetic (jb_af1c F217A, encoding)" python3 verify_fp_arith_f217a_listing.py
run "FP divide arithmetic (jb_af1c F217A on the model)" ./run_program.sh programs/fp_arith_f217a.strap StretchFpDivATb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f217a.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP divide sign and modifiers (jb_af1c F217B, encoding)" python3 verify_fp_arith_f217b_listing.py
run "FP divide sign and modifiers (jb_af1c F217B on the model)" ./run_program.sh programs/fp_arith_f217b.strap StretchFpDivBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f217b.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP divide unchanged regs (jb_af1c F217C, encoding)" python3 verify_fp_arith_f217c_listing.py
run "FP divide unchanged regs (jb_af1c F217C on the model)" ./run_program.sh programs/fp_arith_f217c.strap StretchFpDivCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f217c.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP divide indicators (jb_af1c F217D, encoding)" python3 verify_fp_arith_f217d_listing.py
run "FP divide indicators (jb_af1c F217D on the model)" ./run_program.sh programs/fp_arith_f217d.strap StretchFpDivDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f217d.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP divide double arithmetic (jb_af1c F217WA, encoding)" python3 verify_fp_arith_f217wa_listing.py
run "FP divide double arithmetic (jb_af1c F217WA on the model)" ./run_program.sh programs/fp_arith_f217wa.strap StretchFpDivDblATb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f217wa.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP divide double sign and modifiers (jb_af1c F217WB, encoding)" python3 verify_fp_arith_f217wb_listing.py
run "FP divide double sign and modifiers (jb_af1c F217WB on the model)" ./run_program.sh programs/fp_arith_f217wb.strap StretchFpDivDblBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f217wb.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP divide double changed regs (jb_af1c F217WC, encoding)" python3 verify_fp_arith_f217wc_listing.py
run "FP divide double changed regs (jb_af1c F217WC on the model)" ./run_program.sh programs/fp_arith_f217wc.strap StretchFpDivDblCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f217wc.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP divide double unchanged regs (jb_af1c F217WD, encoding)" python3 verify_fp_arith_f217wd_listing.py
run "FP divide double unchanged regs (jb_af1c F217WD on the model)" ./run_program.sh programs/fp_arith_f217wd.strap StretchFpDivDblDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f217wd.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP divide double remainder underflow (jb_af1c F217WE, encoding)" python3 verify_fp_arith_f217we_listing.py
run "FP divide double remainder underflow (jb_af1c F217WE on the model)" ./run_program.sh programs/fp_arith_f217we.strap StretchFpDivDblETb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f217we.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP reciprocal divide arithmetic (jb_af1c F217XA, encoding)" python3 verify_fp_arith_f217xa_listing.py
run "FP reciprocal divide arithmetic (jb_af1c F217XA on the model)" ./run_program.sh programs/fp_arith_f217xa.strap StretchFpRecipDivATb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f217xa.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP reciprocal divide sign and modifiers (jb_af1c F217XB, encoding)" python3 verify_fp_arith_f217xb_listing.py
run "FP reciprocal divide sign and modifiers (jb_af1c F217XB on the model)" ./run_program.sh programs/fp_arith_f217xb.strap StretchFpRecipDivBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f217xb.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP reciprocal divide unchanged regs (jb_af1c F217XC, encoding)" python3 verify_fp_arith_f217xc_listing.py
run "FP reciprocal divide unchanged regs (jb_af1c F217XC on the model)" ./run_program.sh programs/fp_arith_f217xc.strap StretchFpRecipDivCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f217xc.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP reciprocal divide indicators (jb_af1c F217XD, encoding)" python3 verify_fp_arith_f217xd_listing.py
run "FP reciprocal divide indicators (jb_af1c F217XD on the model)" ./run_program.sh programs/fp_arith_f217xd.strap StretchFpRecipDivDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f217xd.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP store root arithmetic (jb_af1c F218A, encoding)" python3 verify_fp_arith_f218a_listing.py
run "FP store root arithmetic (jb_af1c F218A on the model)" ./run_program.sh programs/fp_arith_f218a.strap StretchFpSqrtATb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f218a.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP store root sign and modifiers (jb_af1c F218B, encoding)" python3 verify_fp_arith_f218b_listing.py
run "FP store root sign and modifiers (jb_af1c F218B on the model)" ./run_program.sh programs/fp_arith_f218b.strap StretchFpSqrtBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f218b.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP store root unchanged regs (jb_af1c F218C, encoding)" python3 verify_fp_arith_f218c_listing.py
run "FP store root unchanged regs (jb_af1c F218C on the model)" ./run_program.sh programs/fp_arith_f218c.strap StretchFpSqrtCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f218c.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP store root indicators (jb_af1c F218D, encoding)" python3 verify_fp_arith_f218d_listing.py
run "FP store root indicators (jb_af1c F218D on the model)" ./run_program.sh programs/fp_arith_f218d.strap StretchFpSqrtDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f218d.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP noisy mode add/load (jb_af1c F219A-D, encoding)" python3 verify_fp_arith_f219a_listing.py
run "FP noisy mode add/load (jb_af1c F219A-D on the model)" ./run_program.sh programs/fp_arith_f219a.strap StretchFpNoisyATb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f219a.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP noisy mode multiply/divide/root (jb_af1c F219K-P2, encoding)" python3 verify_fp_arith_f219b_listing.py
run "FP noisy mode multiply/divide/root (jb_af1c F219K-P2 on the model)" ./run_program.sh programs/fp_arith_f219b.strap StretchFpNoisyBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f219b.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP noisy mode add/load double (jb_af1c F219P3-S, encoding)" python3 verify_fp_arith_f219c_listing.py
run "FP noisy mode add/load double (jb_af1c F219P3-S on the model)" ./run_program.sh programs/fp_arith_f219c.strap StretchFpNoisyCTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f219c.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP noisy mode multiply/divide double (jb_af1c F219T-Y, encoding)" python3 verify_fp_arith_f219d_listing.py
run "FP noisy mode multiply/divide double (jb_af1c F219T-Y on the model)" ./run_program.sh programs/fp_arith_f219d.strap StretchFpNoisyDTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f219d.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "FP noisy mode fraction/exponent ops (jb_af1c F219Z-C1A, encoding)" python3 verify_fp_arith_f219e_listing.py
run "FP noisy mode fraction/exponent ops (jb_af1c F219Z-C1A on the model)" ./run_program.sh programs/fp_arith_f219e.strap StretchFpNoisyETb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/fp_arith_f219e.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "PAU gates SHF0 loop (jb_af1c, encoding)" python3 verify_pau_shf0_listing.py
# The accumulator checks are NOT optional decoration: measured by
# injection, this block reports no error either when the effective
# address ignores its index register or when the loop runs once
# instead of twice.  ACCL/ACCR are what catch both -- see the
# program's own header.
run "PAU gates SHF0 loop (indexed VFL + CBR+ on the model)" ./run_program.sh programs/pau_shf0.strap StretchPauShf0Tb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/pau_shf0.strap").read()).symtab["PASS"]//32)')" \
    "ACCL:8=1501199875790165" "ACCR:9=6148914691236167680"

run "PAU gates SHFR1/SHFR2 (jb_af1c, encoding)" python3 verify_pau_shfr12_listing.py
# ACCL/ACCR again, and for a sharper reason than in SHF0: measured by
# injection, these blocks do NOT catch a wrong index through their own
# branches even though their expected values live in separate tables --
# both sides are indexed by the same register.  See the program header.
run "PAU gates SHFR1/SHFR2 (shift right one and two on the model)" ./run_program.sh programs/pau_shfr12.strap StretchPauShfR12Tb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/pau_shfr12.strap").read()).symtab["PASS"]//32)')" \
    "ACCL:8=375299968947541" "ACCR:9=6148914691236167680"

run "PAU gates CHKSSR (jb_af1c, encoding)" python3 verify_pau_chkssr_listing.py
# No ACCL/ACCR here, and that is the point: unlike the shift blocks,
# CHKSSR uses no index register and has a separate error exit per case,
# so it discriminates through its OWN branches -- two square-root
# injections halt it at SERS.
run "PAU gates CHKSSR (store root, one bit walked down the radicand)" ./run_program.sh programs/pau_chkssr.strap StretchPauChkSsrTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/pau_chkssr.strap").read()).symtab["PASS"]//32)')"

run "PAU gates CHKSSR multi-bit roots (jb_af1c, encoding)" python3 verify_pau_chkssr2_listing.py
# These four earn their place by a measured margin over the sweep
# above: an injection making the root trial ignore previously accepted
# root bits leaves ALL FOURTEEN single-bit cases passing and halts all
# four of these.  See the program header.
run "PAU gates CHKSSR multi-bit roots (perfect squares with several root bits)" ./run_program.sh programs/pau_chkssr2.strap StretchPauChkSsr2Tb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/pau_chkssr2.strap").read()).symtab["PASS"]//32)')"

run "PAU gates SRTE30 (jb_af1c, encoding)" python3 verify_pau_srte30_listing.py
# The block that found the 49-bit radicand bug: a single fraction bit
# at IBM 59 with an ODD exponent, halting if the root comes back zero.
# Its own message is "SHIFT R1-BIT LOST".
run "PAU gates SRTE30 (store root, odd exponent, 49-bit radicand)" ./run_program.sh programs/pau_srte30.strap StretchPauSrte30Tb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/pau_srte30.strap").read()).symtab["PASS"]//32)')"

run "IBOX-2 load index control check (jb_ax2a, encoding)" python3 verify_ibox2_load_index_listing.py
# The first block from jb_ax2a; the tape had never been opened.  Nothing
# else in the suite touches $X0, and only one other program uses
# BXCZ/BXVZ.  Two injections -- index register 0 reading back as zero,
# and XVZ derived from the whole index word -- are both caught by the
# block's own branches.
run "IBOX-2 load index control check (LX into \$X0, BXCZ/BXVZ)" ./run_program.sh programs/ibox2_load_index.strap StretchIbox2LoadIndexTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/ibox2_load_index.strap").read()).symtab["PASS"]//32)')"

run "IBOX-2 KV and KVI check (jb_ax2a, encoding)" python3 verify_ibox2_kv_kvi_listing.py
# Nothing else in the suite uses KV, KVI, BXL, BXH or BXE.  Reversing
# the index compare's high and low is caught by the block's own
# branches.
run "IBOX-2 KV and KVI check (index compare, all three of XL/XE/XH)" ./run_program.sh programs/ibox2_kv_kvi.strap StretchIbox2KvKviTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/ibox2_kv_kvi.strap").read()).symtab["I0210"]//32)')"

run "IBOX-4 progressive index V+ICR / V-I (jb_ax4b, encoding)" python3 verify_ibox4_prog_ix_v_listing.py
# Chosen by measurement: uses KC and the shared progressive-index path,
# both shown unreachable by a combined nine-way injection.  KC comparing
# always HIGH, and progressiveIndex never advancing the value, each halt
# it.  Note the injections must be pointed the RIGHT WAY -- the block
# asserts EQUAL, so "always equal" cannot fail it.
run "IBOX-4 progressive index V+ICR / V-I (KC, SR, progressive value)" ./run_program.sh programs/ibox4_prog_ix_v.strap StretchIbox4ProgIxVTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/ibox4_prog_ix_v.strap").read()).symtab["PASS"]//32)')"

run "IBOX-1 C+I chain (ja_ax1a, encoding)" python3 verify_ibox1_cpi_chain_listing.py
# Closes C+I and SC, two of the seven measured gaps.  The block has no
# SERS: each step manufactures the next branch instruction out of the
# count arithmetic, so breaking C+I HANGS the machine (step cap) and
# breaking SC runs it off into zeroed storage (PC=0) -- two of the
# three failure signatures, neither of them a halt at 1416.
run "IBOX-1 C+I chain (self-modifying branch chain, C+I and SC)" ./run_program.sh programs/ibox1_cpi_chain.strap StretchIbox1CpiChainTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/ibox1_cpi_chain.strap").read()).symtab["PASS"]//32)')"

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
p = assemble(open("programs/ibox1_cmi_chain.strap").read())
h = lambda w, f: (w << 14) | (f << 8)
print(" ".join("%s:%d=0x%016x" % (n, p.symtab[n] // 64,
      (h(p.symtab[t] // 64, 0o04) << 32) | h(p.symtab[n] // 64, 0o44))
      for n, t in (("IBP71", "IBP76"), ("IBP76", "IBP73"),
                   ("IBP73", "IBP74"), ("IBP74", "IBP72"))))')
run "IBOX-1 C-I chain (self-modifying branch chain, C-I)" ./run_program.sh programs/ibox1_cmi_chain.strap StretchIbox1CmiChainTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/ibox1_cmi_chain.strap").read()).symtab["PASS"]//32)')" \
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
p = assemble(open("programs/ibox1_vpc_chain.strap").read())
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
run "IBOX-1 V+C chain (self-modifying branch chain, V+C)" ./run_program.sh programs/ibox1_vpc_chain.strap StretchIbox1VpcChainTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/ibox1_vpc_chain.strap").read()).symtab["PASS"]//32)')" \
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
run "IBOX-4 R refill (effective address, not the index field)" ./run_program.sh programs/ibox4_refill.strap StretchIbox4RefillTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/ibox4_refill.strap").read()).symtab["PASS"]//32)')" \
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
run "IBOX-4 RCZ (refill on count zero)" ./run_program.sh programs/ibox4_rcz.strap StretchIbox4RczTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/ibox4_rcz.strap").read()).symtab["PASS"]//32)')" \
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
run "IBOX-4 R from external memory (two sequential reads)" ./run_program.sh programs/ibox4_r_extmem.strap StretchIbox4RExtmemTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/ibox4_r_extmem.strap").read()).symtab["PASS"]//32)')" \
    "SEN:712=0"

run "IBOX-4 refill address gate (jb_ax4b, encoding)" python3 verify_ibox4_refill_nop_listing.py
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
#                         entry of the routine's own error table
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
run "IBOX-4 refill address gate (locn 0 refills, 1-15 do not)" ./run_program.sh programs/ibox4_refill_nop.strap StretchIbox4RefillNopTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/ibox4_refill_nop.strap").read()).symtab["PASS"]//32)')"

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
run "IBOX-4 RCZ zero gating (all 18 count bits)" ./run_program.sh programs/ibox4_rcz_zerogate.strap StretchIbox4RczZeroGateTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/ibox4_rcz_zerogate.strap").read()).symtab["PASS"]//32)')"

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
p = assemble(open("programs/ibox1_vpic_chain.strap").read())
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
run "IBOX-1 V+IC chain (two phases: value, then count)" ./run_program.sh programs/ibox1_vpic_chain.strap StretchIbox1VpicChainTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/ibox1_vpic_chain.strap").read()).symtab["PASS"]//32)')" \
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
p = assemble(open("programs/ibox1_vpcr_refill.strap").read())
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
run "IBOX-1 V+CR refill (direct index, all three fields)" ./run_program.sh programs/ibox1_vpcr_refill.strap StretchIbox1VpcrRefillTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/ibox1_vpcr_refill.strap").read()).symtab["PASS"]//32)')" \
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
p = assemble(open("programs/ibox1_vic_chain.strap").read())
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
run "IBOX-1 V-IC chain (self-modifying branch chain, V-IC)" ./run_program.sh programs/ibox1_vic_chain.strap StretchIbox1VicChainTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/ibox1_vic_chain.strap").read()).symtab["PASS"]//32)')" \
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
p = assemble(open("programs/ibox1_vicr_chain.strap").read())
ha = lambda n: p.symtab[n] // 32
bd = lambda n: ((ha(n) >> 1) << 14) | ((ha(n) & 1) << 13) | (0b001 << 10)
out = ["REFILLED_IBP31:%d=0x%016x" % (ha("IBP31") >> 1, p.words[ha("IBPA4") >> 1])]
for link, tgt in (("IBP46", "IBP49"), ("IBP49", "IBP50"),
                  ("IBP50", "IBP52"), ("IBP52", "IBP53")):
    w = ha(link) >> 1
    out.append("%s:%d=0x%016x" % (link, w, (bd(tgt) << 32) | (p.words.get(w, 0) & 0xffffffff)))
print(" ".join(out))')
run "IBOX-1 V-ICR chain (refill over a live instruction pair)" ./run_program.sh programs/ibox1_vicr_chain.strap StretchIbox1VicrChainTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/ibox1_vicr_chain.strap").read()).symtab["PASS"]//32)')" \
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
p = assemble(open("programs/ibox1_lvni.strap").read())
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
run "IBOX-1 LVNI (load value negative immediate)" ./run_program.sh programs/ibox1_lvni.strap StretchIbox1LvniTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/ibox1_lvni.strap").read()).symtab["PASS"]//32)')" \
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
run "IBOX-1 KVNI (compare value negative immediate)" ./run_program.sh programs/ibox1_kvni.strap StretchIbox1KvniTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/ibox1_kvni.strap").read()).symtab["PASS"]//32)')"

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
run "IBOX-1 KCI (compare count immediate, indicator reset)" ./run_program.sh programs/ibox1_kci.strap StretchIbox1KciTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/ibox1_kci.strap").read()).symtab["PASS"]//32)')"

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
run "IBOX-1 V-I (subtract from value immediate, SX of the whole word)" ./run_program.sh programs/ibox1_vmi.strap StretchIbox1VmiTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/ibox1_vmi.strap").read()).symtab["PASS"]//32)')"

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
run "IBOX-1 V+ICR (refill, executed as two instructions)" ./run_program.sh programs/ibox1_vpicr.strap StretchIbox1VpicrTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/ibox1_vpicr.strap").read()).symtab["PASS"]//32)')"

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
run "IBOX-3 LR (load refill from all three memories)" ./run_program.sh programs/ibox3_lr.strap StretchIbox3LrTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/ibox3_lr.strap").read()).symtab["PASS"]//32)')"

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
run "IBOX-3 LRI (refill immediate, every bit of the field)" ./run_program.sh programs/ibox3_lri.strap StretchIbox3LriTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/ibox3_lri.strap").read()).symtab["PASS"]//32)')"

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
run "IBOX-3 SVA into a floating-point instruction (18-bit address field)" ./run_program.sh programs/ibox3_sva_fp.strap StretchIbox3SvaFpTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/ibox3_sva_fp.strap").read()).symtab["I2234"]//32)')"

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
run "IBOX-3 SVA into a direct index instruction (19-bit, into a register)" ./run_program.sh programs/ibox3_sva_dix.strap StretchIbox3SvaDixTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/ibox3_sva_dix.strap").read()).symtab["I2230A"]//32)')"

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
run "IBOX-3 SVA into a full-word instruction (24-bit, three memories)" ./run_program.sh programs/ibox3_sva_full.strap StretchIbox3SvaFullTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/ibox3_sva_full.strap").read()).symtab["I2221A"]//32)')"

run "Program store compare: store then EXECUTE the modified instruction" ./run_program.sh programs/store_then_execute.strap StretchStoreExecTb \
    "RESULT:$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/store_then_execute.strap").read()).symtab["RESULT"]//64)')=0x20"

# -- 1j. Store-close-to-fetch: store a word then immediately reload it;
# the load must read the new value, not the stale one. The hazard the FP
# sign-modifier codesign exposed; fixed by tracking each E-box level's
# store target (plan stage 3a note). This exact pattern failed before.
run "Look-ahead: store-close-to-fetch" ./run_scf_test.sh

# -- 2. Problem 2.1: Cyclic Bit Shifting --
run "Problem 2.1" ./run_program.sh programs/problem_2_1.strap StretchProblem21Tb \
    "DOG_rotated:32=0x6e5d4c3b2a19087f" \
    "CYCLES<=140"

# -- 3. Problem 2.2 Method 1: Length of an Unknown File --
# Answer lands in X1's VALUE field (top 24 bits of the packed IndexWord,
# StretchTypes.bsv addr:w[63:40]), not the plain word -- 28 bits, shifted:
# 28 << 40 = 0x1c0000000000. See README.md "Units": ImmIndex/V+ operate in
# raw bit-count units, and X1 IS an index register (addrIndex(1) = 17).
run "Problem 2.2 Method 1" ./run_program.sh programs/problem_2_2_method1.strap StretchProblem22Tb \
    "X1_len:addrIndex(1)=0x1c0000000000"

# -- 3b. Problem 2.2 Method 2: same problem, VFL immediate addressing +
# progressive indexing instead. Same expected answer (28 bits) as
# Method 1 above, by construction (reuses Method 1's own test data) --
# see programs/problem_2_2_method2.strap's header for how X1 ends up
# holding exactly the length rather than an absolute address.
run "Problem 2.2 Method 2" ./run_program.sh programs/problem_2_2_method2.strap StretchProblem22M2Tb \
    "X1_len:addrIndex(1)=0x1c0000000000"

# -- 3c. Problem 2.2 Method 3's algorithm: Connective (CT0110, i.e.
# XOR) + BRZ instead of K + BAE. Two of the seven manual lines are
# substituted for already-verified Method 2 equivalents (LVE/SIC are
# unimplemented -- see programs/problem_2_2_method3.strap's header for
# the full account); same expected answer (28 bits) either way.
run "Problem 2.2 Method 3 (algorithm)" ./run_program.sh programs/problem_2_2_method3.strap StretchProblem22M3Tb \
    "X1_len:addrIndex(1)=0x1c0000000000"

# -- 4. Reference Manual Figure 7: Progressive Indexing --
# Expected final memory (words holding the ten records' R/S/T fields) is
# derived, not hand-computed: run
#     python3 - <<'PY'
#     import sys; sys.path.insert(0, '.')
#     from strap_asm import assemble
#     prog = assemble(open('programs/figure7_progressive_indexing.strap').read())
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
run "Figure 7 Progressive Indexing" ./run_program.sh programs/figure7_progressive_indexing.strap StretchFigure7Tb \
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
run "I-Box 1 WEN/WEN2/VEN (RGZ/RZ indicators)" ./run_program.sh programs/ibox1_wen_ven_indicators.strap StretchIboxWenTb \
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
run "I-Box 1 WEN/WEN2/VEN at original listing addresses" ./run_program.sh programs/ibox1_wen_ven_original_addresses.strap StretchIboxWenOrigTb \
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
run "I-Box 1 SIC-CB / SIC-CBZ (verbatim, own pass/fail)" ./run_program.sh programs/ibox1_sic_cb_cbz.strap StretchIboxSicTb \
    $(python3 ibox1_expected.py programs/ibox1_sic_cb_cbz.strap ISBI \
        ISCBA:ISCBB ISCBB:ISCBC ISCBC:ISCBD ISCBD:ISCBH ISCBH:ISCBI ISCBI:ISCBK)

# -- 4b-bis. BRANCH ON BIT (BB family) acceptance: a self-checking
# chain over an all-zeros word W where the ONLY path to the PASS halt
# (label DONE) requires correct condition testing (branch-on-1 vs
# branch-on-0) AND correct bit modification on both a taken branch
# (BBN invert) and a NOT-taken branch (BB1 set). Any wrong result falls
# into a distinct BEW,$ HANG, so PC alone says pass (DONE) or fail
# (which HANG). See programs/bb_branch_on_bit.strap for the injections.
run "Branch-on-Bit (BB/BZB family, self-checking)" ./run_program.sh programs/bb_branch_on_bit.strap StretchBBTb \
    "PC=$(python3 -c 'from strap_asm import assemble; print(assemble(open("programs/bb_branch_on_bit.strap").read()).symtab["DONE"]//32)')"

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
run "I-Box 1 pp.43-51 span (20 test groups, verbatim)" ./run_program.sh programs/ibox1_p43_p51_span.strap StretchIboxSpanTb \
    $(python3 ibox1_expected.py programs/ibox1_p43_p51_span.strap IBY \
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
run "I-Box 4 CB (Count and Branch)" ./run_program.sh programs/ibox4_cb_count_branch.strap StretchIboxCbTb \
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
run "I-Box 4 CBR (Count, Branch, and Refill)" ./run_program.sh programs/ibox4_cbr_refill.strap StretchIboxCbrTb \
    "X2_call1_taken:addrIndex(2)=0xc800000000000" \
    "X3_call2_taken:addrIndex(3)=0xc800000000000" \
    "X4_call3_not_taken:addrIndex(4)=0x0" \
    "X5_no_refill_yet:addrIndex(5)=0x6f0000040029" \
    "X6_refilled:addrIndex(6)=0xde00fffc0000"

# -- 5. XW refill mechanism (see README.md "Gotchas" item 7) --
# Distinctive VALUE=999/COUNT=42 at CTLB, refilled into $X12 via CTLA's
# COUNT=1 forcing exactly one refill on the program's one progressive
# store; expected = CTLB's own packed XW encoding, verbatim.
run "XW refill" ./run_program.sh programs/xw_refill.strap StretchXwRefillTb \
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

# -- cleanup: generated .bsv testbenches and Bluesim build products are
# not meant to be committed (see .gitignore) --
rm -f "$BSV_DIR"/StretchProblem*Tb.bsv "$BSV_DIR"/StretchFigure*Tb.bsv "$BSV_DIR"/StretchXwRefillTb.bsv "$BSV_DIR"/StretchIoReaderPrinterTb.bsv "$BSV_DIR"/StretchIoTapeTb.bsv "$BSV_DIR"/StretchIboxWenTb.bsv "$BSV_DIR"/StretchIboxCbTb.bsv "$BSV_DIR"/StretchIboxCbrTb.bsv
rm -f "$BSV_DIR"/*_sim "$BSV_DIR"/*_sim.so
rm -rf "$BSV_DIR"/build "$BSV_DIR"/simbuild

if [ "$FAILED" -ne 0 ]; then
  echo "*** ONE OR MORE TESTS FAILED ***" >&2
  exit 1
fi
echo "All regression tests passed."
