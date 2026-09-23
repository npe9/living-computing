#!/bin/sh
# run_fp_test.sh -- assemble programs/fp_arith.strap, patch the TWO/THREE
# operand words and the R1-R3 expected result words from
# fp_arith_expected.py (single-precision 7030 floating point, built in
# Python from the same format the model uses), and run it on the model.
# Same post-assembly-patch pattern as run_io_test.sh.
set -e
STRAP_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$STRAP_DIR"
# UNIQUE temp path, per invocation.  This script used to write a
# FIXED path under /tmp and then re-read it.  mutation_score.py runs
# 12 mutants in parallel, each in its own CLONED TREE -- but /tmp is
# not cloned, so all 12 wrote and re-read the same file.  The race
# failed this test spuriously and made the campaign attribute
# mutants to whichever of these five scripts lost it.  See
# docs/NEXT.md section 4.
OUT="${TMPDIR:-/tmp}/fp_patched.$$.strap"
eval "$(python3 fp_arith_expected.py)"
python3 - "$TWO" "$THREE" <<PY > "$OUT"
import sys
two, three = int(sys.argv[1],16), int(sys.argv[2],16)
s = open('programs/fp_arith.strap').read()
s = s.replace('TWO     DD(BU,64), 0', f'TWO     DD(BU,64), {two}')
s = s.replace('THREE   DD(BU,64), 0', f'THREE   DD(BU,64), {three}')
open('$OUT','w').write(s)
PY
exec ./run_program.sh "$OUT" StretchFpTb \
    "R1:$(python3 -c "from strap_asm import assemble;print(assemble(open('$OUT').read()).symtab['R1']//64)")=$R1" \
    "R2:$(python3 -c "from strap_asm import assemble;print(assemble(open('$OUT').read()).symtab['R2']//64)")=$R2" \
    "R3:$(python3 -c "from strap_asm import assemble;print(assemble(open('$OUT').read()).symtab['R3']//64)")=$R3" \
    "CYCLES<=100000"
