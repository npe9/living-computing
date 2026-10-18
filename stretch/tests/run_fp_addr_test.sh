#!/bin/sh
# run_fp_addr_test.sh -- assemble ../decks/fp_addr_invalid.strap with the
# TWO operand patched to +2.0 (fp_arith_expected.py's encoding), run it,
# and check that the accumulator saved after the invalid-address load
# still holds 2.0 and that AD (indicator bit 16, word 11) is set. The
# expected indicator word is AD | MOP | RGZ: the invalid load sets only
# AD (no-op), then the trailing ST sets MOP (to-memory) and RGZ (the
# stored 2.0 is positive) -- bits 16, 55 and 58 = 0x800000000120,
# derived from the manual's ST/result-indicator semantics, not fitted.
set -e
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
# The assembler lives in ../strap now; the verifiers and
# generators import it by module name.
PYTHONPATH="$TESTS_DIR/../strap:$TESTS_DIR"; export PYTHONPATH; cd "$TESTS_DIR"
# UNIQUE temp path, per invocation.  This script used to write a
# FIXED path under /tmp and then re-read it.  mutation_score.py runs
# 12 mutants in parallel, each in its own CLONED TREE -- but /tmp is
# not cloned, so all 12 wrote and re-read the same file.  The race
# failed this test spuriously and made the campaign attribute
# mutants to whichever of these five scripts lost it.  See
# docs/NEXT.md section 4.
OUT="${TMPDIR:-/tmp}/fpad.$$.strap"
eval "$(python3 fp_arith_expected.py)"   # sets TWO=0x...
python3 - "$TWO" <<PY > "$OUT"
import sys
s=open('../decks/fp_addr_invalid.strap').read()
open('$OUT','w').write(s.replace('TWO     DD(BU,64), 0', f'TWO     DD(BU,64), {int(sys.argv[1],16)}'))
PY
SAVE=$(python3 -c "from strap_asm import assemble;print(assemble(open('$OUT').read()).symtab['ACCSAVE']//64)")
exec ./run_program.sh "$OUT" StretchFpAdTb \
    "ACC_unchanged:$SAVE=$TWO" \
    "AD_and_store:11=0x0000800000000120" \
    "CYCLES<=100000"
