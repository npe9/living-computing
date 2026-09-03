#!/bin/sh
# run_fp_addr_test.sh -- assemble programs/fp_addr_invalid.strap with the
# TWO operand patched to +2.0 (fp_arith_expected.py's encoding), run it,
# and check that the accumulator saved after the invalid-address load
# still holds 2.0 and that AD (indicator bit 16, word 11) is set. The
# expected indicator word is AD | MOP | RGZ: the invalid load sets only
# AD (no-op), then the trailing ST sets MOP (to-memory) and RGZ (the
# stored 2.0 is positive) -- bits 16, 55 and 58 = 0x800000000120,
# derived from the manual's ST/result-indicator semantics, not fitted.
set -e
STRAP_DIR="$(cd "$(dirname "$0")" && pwd)"; cd "$STRAP_DIR"
eval "$(python3 fp_arith_expected.py)"   # sets TWO=0x...
python3 - "$TWO" <<PY > /tmp/fpad.strap
import sys
s=open('programs/fp_addr_invalid.strap').read()
open('/tmp/fpad.strap','w').write(s.replace('TWO     DD(BU,64), 0', f'TWO     DD(BU,64), {int(sys.argv[1],16)}'))
PY
SAVE=$(python3 -c "from strap_asm import assemble;print(assemble(open('/tmp/fpad.strap').read()).symtab['ACCSAVE']//64)")
exec ./run_program.sh /tmp/fpad.strap StretchFpAdTb \
    "ACC_unchanged:$SAVE=$TWO" \
    "AD_and_store:11=0x0000800000000120" \
    "CYCLES<=100000"
