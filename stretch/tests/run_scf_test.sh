#!/bin/sh
# run_scf_test.sh -- store-close-to-fetch: store 3.0, immediately reload
# the same word, store the result, check it is 3.0 (not the stale 0).
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
OUT="${TMPDIR:-/tmp}/scf.$$.strap"
THREE=$(python3 -c "
import fp_arith_expected as e; print(hex(e.enc(3.0)))")
python3 - "$THREE" <<PY > "$OUT"
import sys; s=open('../decks/store_close_to_fetch.strap').read()
open('$OUT','w').write(s.replace('THREE   DD(BU,64), 0', f'THREE   DD(BU,64), {int(sys.argv[1],16)}'))
PY
w(){ python3 -c "from strap_asm import assemble;print(assemble(open('$OUT').read()).symtab['$1']//64)"; }
exec ./run_program.sh "$OUT" StretchScfTb "R:$(w R)=$THREE" "X:$(w X)=$THREE" "CYCLES<=100000"
