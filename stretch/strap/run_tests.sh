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
  if [ "$status" -ne 0 ] || grep -q "TEST(S) FAILED" "$TMPOUT"; then FAILED=1; fi
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

# -- 0e. I-Box 4 routine 150's CB / CB+ / CBR / CBR+ blocks (plus their
# LX/SX setup and XW index words) assembled verbatim at the listing's
# own addresses and compared against docs/jb_ax4b_ibox-4.pdf pp.155/159's
# printed machine code -- the first external check of CB_CODES, LX/SX,
# and the packed index-word layout. Pure Python, no Bluesim.
run "I-Box 4 listing bit-exact comparison" python3 verify_ibox4_listing.py

# -- 1. Hand-assembled BSV smoke test (StretchSmoke.bsv, not STRAP-derived) --
cd "$BSV_DIR"
run "bsv smoke test (make run)" make run
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
