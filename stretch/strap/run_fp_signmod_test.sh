#!/bin/sh
# run_fp_signmod_test.sh -- assemble programs/fp_signmod.strap with TWO
# (+2.0) and NEGTWO (-2.0) patched from fp_arith_expected.py, run it,
# and check the three stored results of LN/LA/LNA against the expected
# signed encodings. Reads only pre-set constants (no store-close-to-
# fetch). See verify_fp_signmods.py for the assembler bit-exact check.
set -e
STRAP_DIR="$(cd "$(dirname "$0")" && pwd)"; cd "$STRAP_DIR"
eval "$(python3 fp_arith_expected.py)"
NEG=$(python3 -c "print(hex(int('$TWO',16) | (1<<3)))")
python3 - "$TWO" "$NEG" <<PY > /tmp/fpsm.strap
import sys; s=open('programs/fp_signmod.strap').read()
s=s.replace('TWO     DD(BU,64), 0', f'TWO     DD(BU,64), {int(sys.argv[1],16)}')
s=s.replace('NEGTWO  DD(BU,64), 0', f'NEGTWO  DD(BU,64), {int(sys.argv[2],16)}')
open('/tmp/fpsm.strap','w').write(s)
PY
w(){ python3 -c "from strap_asm import assemble;print(assemble(open('/tmp/fpsm.strap').read()).symtab['$1']//64)"; }
exec ./run_program.sh /tmp/fpsm.strap StretchFpSignTb \
    "RNEG:$(w RNEG)=$NEG" "RABS:$(w RABS)=$TWO" "RNA:$(w RNA)=$NEG" "CYCLES<=100000"
