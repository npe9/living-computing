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
  # aborting the whole suite on one failure (set -e is for real errors:
  # bsc failing to compile, python raising, etc; a FAIL line from the
  # generated testbench is data, not a shell error). MUST run in the
  # current shell, not a subshell -- `FAILED=1` set inside a subshell
  # (e.g. `( cd x && run ... )`) is discarded when the subshell exits,
  # which silently turned this into a script that always reported
  # success regardless of the smoke test's actual result. Caught by
  # advisor review before it ever shipped that way.
  name="$1"; shift
  echo "=== $name ==="
  "$@" 2>&1 | tee "$TMPOUT" | tail -20
  if grep -q "TEST(S) FAILED" "$TMPOUT"; then FAILED=1; fi
  echo
}

# -- 1. Hand-assembled BSV smoke test (StretchTb.bsv, not STRAP-derived) --
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

# -- 5. XW refill mechanism (see README.md "Gotchas" item 7) --
# Distinctive VALUE=999/COUNT=42 at CTLB, refilled into $X12 via CTLA's
# COUNT=1 forcing exactly one refill on the program's one progressive
# store; expected = CTLB's own packed XW encoding, verbatim.
run "XW refill" ./run_program.sh programs/xw_refill.strap StretchXwRefillTb \
    "X12_after_refill:addrIndex(12)=0x3e70000a80000"

# -- cleanup: generated .bsv testbenches and Bluesim build products are
# not meant to be committed (see .gitignore) --
rm -f "$BSV_DIR"/StretchProblem*Tb.bsv "$BSV_DIR"/StretchFigure*Tb.bsv "$BSV_DIR"/StretchXwRefillTb.bsv
rm -f "$BSV_DIR"/*_sim "$BSV_DIR"/*_sim.so
rm -rf "$BSV_DIR"/build "$BSV_DIR"/simbuild

if [ "$FAILED" -ne 0 ]; then
  echo "*** ONE OR MORE TESTS FAILED ***" >&2
  exit 1
fi
echo "All regression tests passed."
