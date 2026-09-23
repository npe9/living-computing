#!/bin/sh
# run_fp_exp_test.sh -- assemble programs/fp_exp_shift.strap with TWO/ONE
# patched from fp_exp_expected.py, run it, and check the three stored
# results (E+I, E+, SHF) against the Python-derived expected words.
set -e
STRAP_DIR="$(cd "$(dirname "$0")" && pwd)"; cd "$STRAP_DIR"
# UNIQUE temp path, per invocation.  This script used to write a
# FIXED path under /tmp and then re-read it.  mutation_score.py runs
# 12 mutants in parallel, each in its own CLONED TREE -- but /tmp is
# not cloned, so all 12 wrote and re-read the same file.  The race
# failed this test spuriously and made the campaign attribute
# mutants to whichever of these five scripts lost it.  See
# docs/NEXT.md section 4.
OUT="${TMPDIR:-/tmp}/fpe.$$.strap"
eval "$(python3 fp_exp_expected.py)"
python3 - "$TWO" "$ONE" <<PY > "$OUT"
import sys
s=open('programs/fp_exp_shift.strap').read()
s=s.replace('TWO     DD(BU,64), 0', f'TWO     DD(BU,64), {int(sys.argv[1],16)}')
s=s.replace('ONE     DD(BU,64), 0', f'ONE     DD(BU,64), {int(sys.argv[2],16)}')
open('$OUT','w').write(s)
PY
w(){ python3 -c "from strap_asm import assemble;print(assemble(open('$OUT').read()).symtab['$1']//64)"; }
exec ./run_program.sh "$OUT" StretchFpExpTb \
    "EPLI:$(w REPLI)=$REPLI" \
    "EPL:$(w REPL)=$REPL" \
    "SHF:$(w RSHF)=$RSHF" \
    "CYCLES<=100000"
