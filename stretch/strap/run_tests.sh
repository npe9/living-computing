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

# -- 1. Hand-assembled BSV smoke test (StretchSmoke.bsv, not STRAP-derived) --
cd "$BSV_DIR"
run "bsv smoke test (make run)" make run
cd "$STRAP_DIR"

# -- 2. Problem 2.1: Cyclic Bit Shifting --
run "Problem 2.1" ./run_program.sh programs/problem_2_1.strap StretchProblem21Tb \
    "DOG_rotated:32=0x6e5d4c3b2a19087f"

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
    "w37:37=0xa0a00b0c08c0e1" \
    "w38:38=0xd1018e1220f1429" \
    "w39:39=0x16311183921a413" \
    "w40:40=0x1c48000000000000"

# -- 4b. I-Box 1 diagnostic (docs/ja_ax1a_ibox-1.pdf p.51, WEN/WEN2/VEN):
# VFL binary-unsigned Load correctly sets RGZ for a nonzero unsigned
# value and RZ for zero -- see docs/archival_inventory.md "6. The five
# I-Box diagnostic test programs" for how this candidate was chosen
# (the smallest self-contained runnable fragment found, after routine
# 1274's address-truncation test turned out to be untestable by
# construction on this model's typed WordAddr/HWordAddr widths).
run "I-Box 1 WEN/WEN2/VEN (RGZ/RZ indicators)" ./run_program.sh programs/ibox1_wen_ven_indicators.strap StretchIboxWenTb \
    "X1_RGZ_ones:addrIndex(1)=0x640000000000" \
    "X2_RZ_zeros:addrIndex(2)=0x640000000000" \
    "X3_RGZ_ones_again:addrIndex(3)=0x640000000000" \
    "X4_notRZ_ones:addrIndex(4)=0x640000000000" \
    "X5_notRGZ_zeros:addrIndex(5)=0x640000000000"

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
    "X2_step1_taken:addrIndex(2)=0x640000000000" \
    "X3_step2_taken:addrIndex(3)=0x640000000000" \
    "X4_step3_taken:addrIndex(4)=0x640000000000" \
    "X5_step4_not_taken:addrIndex(5)=0x0"

# -- 4d. I-Box 4 diagnostic (docs/jb_ax4b_ibox-4.pdf p.159, routine 150,
# the IBR96-IBR99 block): "CBR" (Count, Branch, and Refill) -- exercises
# CountBranch's own refill mechanism (doRefill/needsRead/prefetch), a
# code path distinct from xw_refill.strap's V+ICR-based refill test.
# See ibox4_cbr_refill.strap's own header for the full transcription
# and non-vacuousness account.
run "I-Box 4 CBR (Count, Branch, and Refill)" ./run_program.sh programs/ibox4_cbr_refill.strap StretchIboxCbrTb \
    "X2_call1_taken:addrIndex(2)=0x640000000000" \
    "X3_call2_taken:addrIndex(3)=0x640000000000" \
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
