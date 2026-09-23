#!/bin/sh
# run_fp_signmod_test.sh -- assemble programs/fp_signmod.strap with TWO
# (+2.0) and NEGTWO (-2.0) patched from fp_arith_expected.py, run it,
# and check the three stored results of LN/LA/LNA against the expected
# signed encodings. Reads only pre-set constants (no store-close-to-
# fetch). See verify_fp_signmods.py for the assembler bit-exact check.
set -e
STRAP_DIR="$(cd "$(dirname "$0")" && pwd)"; cd "$STRAP_DIR"
# UNIQUE temp path, per invocation.  This script used to write a
# FIXED path under /tmp and then re-read it.  mutation_score.py runs
# 12 mutants in parallel, each in its own CLONED TREE -- but /tmp is
# not cloned, so all 12 wrote and re-read the same file.  The race
# failed this test spuriously and made the campaign attribute
# mutants to whichever of these five scripts lost it.  See
# docs/NEXT.md section 4.
OUT="${TMPDIR:-/tmp}/fpsm.$$.strap"
eval "$(python3 fp_arith_expected.py)"
NEG=$(python3 -c "print(hex(int('$TWO',16) | (1<<3)))")
python3 - "$TWO" "$NEG" <<PY > "$OUT"
import sys; s=open('programs/fp_signmod.strap').read()
s=s.replace('TWO     DD(BU,64), 0', f'TWO     DD(BU,64), {int(sys.argv[1],16)}')
s=s.replace('NEGTWO  DD(BU,64), 0', f'NEGTWO  DD(BU,64), {int(sys.argv[2],16)}')
open('$OUT','w').write(s)
PY
w(){ python3 -c "from strap_asm import assemble;print(assemble(open('$OUT').read()).symtab['$1']//64)"; }
exec ./run_program.sh "$OUT" StretchFpSignTb \
    "RNEG:$(w RNEG)=$NEG" "RABS:$(w RABS)=$TWO" "RNA:$(w RNA)=$NEG" "CYCLES<=100000"
