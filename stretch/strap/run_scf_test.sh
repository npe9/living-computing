#!/bin/sh
# run_scf_test.sh -- store-close-to-fetch: store 3.0, immediately reload
# the same word, store the result, check it is 3.0 (not the stale 0).
set -e
STRAP_DIR="$(cd "$(dirname "$0")" && pwd)"; cd "$STRAP_DIR"
THREE=$(python3 -c "
import fp_arith_expected as e; print(hex(e.enc(3.0)))")
python3 - "$THREE" <<PY > /tmp/scf.strap
import sys; s=open('programs/store_close_to_fetch.strap').read()
open('/tmp/scf.strap','w').write(s.replace('THREE   DD(BU,64), 0', f'THREE   DD(BU,64), {int(sys.argv[1],16)}'))
PY
w(){ python3 -c "from strap_asm import assemble;print(assemble(open('/tmp/scf.strap').read()).symtab['$1']//64)"; }
exec ./run_program.sh /tmp/scf.strap StretchScfTb "R:$(w R)=$THREE" "X:$(w X)=$THREE" "CYCLES<=100000"
