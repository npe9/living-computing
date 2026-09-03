#!/bin/sh
# run_fp_test.sh -- assemble programs/fp_arith.strap, patch the TWO/THREE
# operand words and the R1-R3 expected result words from
# fp_arith_expected.py (single-precision 7030 floating point, built in
# Python from the same format the model uses), and run it on the model.
# Same post-assembly-patch pattern as run_io_test.sh.
set -e
STRAP_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$STRAP_DIR"
eval "$(python3 fp_arith_expected.py)"
python3 - "$TWO" "$THREE" <<PY > /tmp/fp_patched.strap
import sys
two, three = int(sys.argv[1],16), int(sys.argv[2],16)
s = open('programs/fp_arith.strap').read()
s = s.replace('TWO     DD(BU,64), 0', f'TWO     DD(BU,64), {two}')
s = s.replace('THREE   DD(BU,64), 0', f'THREE   DD(BU,64), {three}')
open('/tmp/fp_patched.strap','w').write(s)
PY
exec ./run_program.sh /tmp/fp_patched.strap StretchFpTb \
    "R1:$(python3 -c "from strap_asm import assemble;print(assemble(open('/tmp/fp_patched.strap').read()).symtab['R1']//64)")=$R1" \
    "R2:$(python3 -c "from strap_asm import assemble;print(assemble(open('/tmp/fp_patched.strap').read()).symtab['R2']//64)")=$R2" \
    "R3:$(python3 -c "from strap_asm import assemble;print(assemble(open('/tmp/fp_patched.strap').read()).symtab['R3']//64)")=$R3" \
    "CYCLES<=100000"
