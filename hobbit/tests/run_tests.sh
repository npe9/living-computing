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
# The 1e executable reader: `_main` must still begin with main9.s's MOV.
python3 "$hobbit/tools/p9exec.py" "$hobbit/tools/plan9-1e/hobbit/bin/echo" >/dev/null

python3 "$here/test_hobbit_asm.py"
python3 "$here/test_hri_check.py"
python3 "$here/test_sem_extended.py"
python3 "$here/test_p9shim.py"
# A2 on the reference model: the shipped za/zl run on sem/hobbit_sem.py
# (tools/p9run.py) and reproduce the shipped libc objects byte for byte.
python3 "$here/test_p9run.py"
python3 "$here/golden/check_golden.py"

"$hobbit/bsv/run_smoke.sh"
"$hobbit/bsv/run_uart.sh"
# The FPGA top's own UART output, decoded at 217 clocks/bit, must equal the
# smoke test's HRI lines (run_board_tb.sh runs both and compares them).
"$hobbit/bsv/run_board_tb.sh"
# MMU, event processing, and the two integrated in the core.
"$hobbit/bsv/run_mmu.sh"
"$hobbit/bsv/run_event.sh"
"$hobbit/bsv/run_core_mmu.sh"
# The bus face and the timers behind it.
"$hobbit/bsv/run_bus.sh"
"$hobbit/bsv/run_timer.sh"
# A1: 1e `cat` reads a real file through the syscall shim, prints it over
# the model's `write` byte-exactly, and exits 0 (run_p9.sh checks both and
# fails otherwise).
if ! "$hobbit/bsv/run_p9.sh" > "$tmp/p9.out" 2>&1; then
    tail -20 "$tmp/p9.out"
    echo "hobbit: the A1 cat run failed" >&2
    exit 1
fi
grep '^P9SHIM' "$tmp/p9.out"
# The same with a file longer than cat's 8,192-byte buffer: read returns
# 8192, then the 2,450-byte remainder, then 0.
if ! "$hobbit/bsv/run_p9.sh" cat \
        "$hobbit/tools/plan9-1e/sys/src/9/hobbit/trap.c" > "$tmp/p9b.out" 2>&1; then
    tail -20 "$tmp/p9b.out"
    echo "hobbit: the A1 cat run on trap.c failed" >&2
    exit 1
fi
grep '^P9SHIM' "$tmp/p9b.out"

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

# 013 exercises the one-parcel Table 1-15 row 11 forms MOV.CS, SHL3.CS,
# SHR3.CS and MOVA.SS.  014 exercises the stack-offset-indirect word modes
# 0xE (MOV.IS, MOV.II, MOV.SI and the three/five-parcel *Roffset:W forms);
# 015 exercises the indirect byte/half modes 0x8-0xB as stores and loads.
# 016 exercises operands outside the stack cache's window: absolute
# words and bytes, a pointer into memory, a word an ENTER flushed, and a
# RETURN across a frame larger than the cache.
# Both the core and the spec model must reproduce each hand-derived trace
# (the core implements all of these forms).
for n in 013 014 015 016; do
    "$hobbit/bsv/run_golden.sh" "$n" > "$tmp/$n.model.raw"
    grep '^HRI ' "$tmp/$n.model.raw" > "$tmp/$n.model"
    python3 "$here/hri_check.py" --dut-lines "$tmp/$n.model" \
        --spec-lines "$here/golden/$n.trace"

    python3 "$hobbit/sem/hobbit_sem.py" --image "$here/golden/$n.hex" \
        --sp 0x100 --msp 0x180 2>/dev/null | grep '^HRI ' > "$tmp/$n.sem"
    python3 "$here/hri_check.py" --dut-lines "$tmp/$n.sem" \
        --spec-lines "$here/golden/$n.trace"
done

# 017 pins little-endian data (PSW.UL, PRM pp. 1-3/1-4): the same three-way
# check with the PSW of its own pre-state, 0x8600 (017.md).  1st Edition
# Plan 9 runs every process this way.
"$hobbit/bsv/run_golden.sh" 017 > "$tmp/017.model.raw"
grep '^HRI ' "$tmp/017.model.raw" > "$tmp/017.model"
python3 "$here/hri_check.py" --dut-lines "$tmp/017.model" \
    --spec-lines "$here/golden/017.trace"
python3 "$hobbit/sem/hobbit_sem.py" --image "$here/golden/017.hex" \
    --sp 0x100 --msp 0x180 --psw 0x8600 2>/dev/null | grep '^HRI ' > "$tmp/017.sem"
python3 "$here/hri_check.py" --dut-lines "$tmp/017.sem" \
    --spec-lines "$here/golden/017.trace"

# 018: a mispredicted branch squashes the wrong-path instruction on a
# loop's second pass (found by 1e's echo).  019: both operands indirect,
# indirect CALL/JMP, ENTER's memory targets, DQM with a constant (the
# forms 1e's echo and za needed).  020: a folded unconditional JMP costs
# 0 (found as a cyc-only difference on 1e's za).  021: DQM with a block
# source (1e's zc copies structures with it).  Each three ways.
for n in 018 019 020 021; do
    "$hobbit/bsv/run_golden.sh" "$n" > "$tmp/$n.model.raw"
    grep '^HRI ' "$tmp/$n.model.raw" > "$tmp/$n.model"
    python3 "$here/hri_check.py" --dut-lines "$tmp/$n.model" \
        --spec-lines "$here/golden/$n.trace"

    python3 "$hobbit/sem/hobbit_sem.py" --image "$here/golden/$n.hex" \
        --sp 0x100 --msp 0x180 2>/dev/null | grep '^HRI ' > "$tmp/$n.sem"
    python3 "$here/hri_check.py" --dut-lines "$tmp/$n.sem" \
        --spec-lines "$here/golden/$n.trace"
done

# A2 on the Bluespec core: the shipped 1e za and zl run on the model,
# every retirement compared with the reference run (bsv/run_p9host.sh);
# za's object is compared with the shipped libc.a member.
"$here/run_p9host_tests.sh"

echo "hobbit: all tests passed"
