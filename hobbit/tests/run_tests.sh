#!/bin/sh
# The hobbit/ regression suite. Run from anywhere; it does not change the
# caller's directory, and it fails at the first failed gate.
#
#   1. evidence gates: Plan 9 opcode/mnemonic cross-check against the printed
#      tables, and the Chapter 4 timing table against Table 3-1;
#   2. pure-Python tests: parcel assembler/disassembler, the HRI trace differ,
#      the hand-derived golden traces;
#   3. the Bluesim smoke test (17 checks) and, for each golden program, the
#      HRI record of the core and of the one-instruction model, each compared
#      field by field with the hand-derived trace.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
hobbit=$(dirname "$here")
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

python3 "$hobbit/tools/check_optab.py"
python3 "$hobbit/tools/check_timing.py"

python3 "$here/test_hobbit_asm.py"
python3 "$here/test_hri_check.py"
python3 "$here/test_sem_extended.py"
python3 "$here/golden/check_golden.py"

"$hobbit/bsv/run_smoke.sh"
"$hobbit/bsv/run_uart.sh"

for n in 001 002 003 004 005 006; do
    "$hobbit/bsv/run_golden.sh" "$n" > "$tmp/$n.model.raw"
    grep '^HRI ' "$tmp/$n.model.raw" > "$tmp/$n.model"
    python3 "$here/hri_check.py" --dut-lines "$tmp/$n.model" \
        --spec-lines "$here/golden/$n.trace"

    python3 "$hobbit/sem/hobbit_sem.py" --image "$here/golden/$n.hex" \
        --sp 0x100 --msp 0x180 2>/dev/null | grep '^HRI ' > "$tmp/$n.sem"
    python3 "$here/hri_check.py" --dut-lines "$tmp/$n.sem" \
        --spec-lines "$here/golden/$n.trace"
done

# 007-012 exercise instructions the Bluespec core does not implement yet
# (MUL, DIV, ADDI, TADD, MOVA, LDRAA).  The spec model must still reproduce
# its hand-derived golden trace; no core comparison exists for them.
for n in 007 008 009 010 011 012; do
    python3 "$hobbit/sem/hobbit_sem.py" --image "$here/golden/$n.hex" \
        --sp 0x100 --msp 0x180 2>/dev/null | grep '^HRI ' > "$tmp/$n.sem"
    python3 "$here/hri_check.py" --dut-lines "$tmp/$n.sem" \
        --spec-lines "$here/golden/$n.trace"
done

echo "hobbit: all tests passed"
