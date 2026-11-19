#!/bin/sh
# PIM/m regression suite: assembler, ISA table, Bluesim smoke and
# testbenches, formal BMC.
# Run from anywhere; the script changes to its own directory.
set -eu
cd "$(dirname "$0")"

echo "=== pimasm selftest ==="
python3 asm/pimasm.py --selftest

echo "=== ISA table check ==="
python3 asm/gen_isa_table.py --check

echo "=== Bluesim smoke ==="
bsv/run_smoke.sh

echo "=== Bluesim NU testbench ==="
bsv/run_nu_tb.sh

echo "=== Bluesim SDRAM store testbench ==="
bsv/run_sdram_tb.sh

echo "=== formal BMC (fixed PASS, buggy FAIL) ==="
bsv/formal/run_formal.sh

echo "=== pim suite: PASS ==="
