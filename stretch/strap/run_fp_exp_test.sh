#!/bin/sh
# run_fp_exp_test.sh -- assemble programs/fp_exp_shift.strap with TWO/ONE
# patched from fp_exp_expected.py, run it, and check the three stored
# results (E+I, E+, SHF) against the Python-derived expected words.
set -e
STRAP_DIR="$(cd "$(dirname "$0")" && pwd)"; cd "$STRAP_DIR"
eval "$(python3 fp_exp_expected.py)"
python3 - "$TWO" "$ONE" <<PY > /tmp/fpe.strap
import sys
s=open('programs/fp_exp_shift.strap').read()
s=s.replace('TWO     DD(BU,64), 0', f'TWO     DD(BU,64), {int(sys.argv[1],16)}')
s=s.replace('ONE     DD(BU,64), 0', f'ONE     DD(BU,64), {int(sys.argv[2],16)}')
open('/tmp/fpe.strap','w').write(s)
PY
w(){ python3 -c "from strap_asm import assemble;print(assemble(open('/tmp/fpe.strap').read()).symtab['$1']//64)"; }
exec ./run_program.sh /tmp/fpe.strap StretchFpExpTb \
    "EPLI:$(w REPLI)=$REPLI" \
    "EPL:$(w REPL)=$REPL" \
    "SHF:$(w RSHF)=$RSHF" \
    "CYCLES<=100000"
