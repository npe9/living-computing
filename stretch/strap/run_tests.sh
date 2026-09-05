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
