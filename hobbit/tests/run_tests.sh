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
# The shipped kernel image (-H1) and the facts docs/s9term.md reads from it.
python3 "$hobbit/tools/p9exec.py" "$hobbit/tools/plan9-1e/hobbit/s9term" >/dev/null
python3 "$here/test_p9exec.py"
# A3's link is compared with s9term by tools/p9kcmp.py (the linked 9term
# is a build product, made by `p9kbuild.py link` in the long run); here
# the comparison runs on s9term itself and on corrupted copies of it.
python3 "$hobbit/tools/p9kcmp.py" "$hobbit/tools/plan9-1e/hobbit/s9term" >/dev/null
python3 "$here/test_p9kcmp.py"

python3 "$here/test_hobbit_asm.py"
python3 "$here/test_hri_check.py"
python3 "$here/test_cyc_classify.py"
# The timing twin (sem/hobbit_timing.py, plan milestone C2): its base cyc
# equals every golden's hand-derived cyc, and its synthetic rules hold;
# za and zc are checked in run_p9host_tests.sh.
python3 "$here/test_hobbit_timing.py"
python3 "$here/test_sem_extended.py"
# The privileged machine (hobbit_sem.System): CPU escape, CSP = ISP, MMU,
# events -- what tools/p9boot.py boots the shipped kernel with.
python3 "$here/test_sem_system.py"
# A4: the shipped kernel s9term boots on the reference model: pageinit's
# console line, /boot's prompt, the BOOTP request, the no-server path,
# and a replay of the join with the 1e file server through init, rc's
# prompt and `echo hello` at it (A5, ~3 min of it); the idle skip is
# checked against a run without it (tools/p9boot.py, docs/p9boot.md;
# ~6-7 min on a loaded machine).
python3 "$here/test_p9boot.py"
# Our 9term (A3's link) to its first line and to Return at /boot's
# prompt, typed as kbd.c scan codes (~1.5 min); the image is a build
# product: the image tests skip, printing the command, when
# build/p9kbuild/9term (or $HOBBIT_9TERM) is not the recorded image.
python3 "$here/test_own9term.py"
# The terminal (tools/p9term.py): the screen bitmap, the LCD panel built
# from screenupdate's writes, the Mouse Systems mouse on Quart channel 3
# and timed input, at /boot's prompt (~1 min); s9term's gtexture alone;
# and a replay of a live 8½ session as tor to 8½'s first settled screen
# (EightHalfReplayTest, the longest part; P9TERM_8HALF=ls replays the
# mouse-swept window and `ls` in it as well).
python3 "$here/test_p9term.py"
python3 "$here/test_p9shim.py"
# A2 on the reference model: the shipped za/zl run on sem/hobbit_sem.py
# (tools/p9run.py) and reproduce the shipped libc objects byte for byte.
python3 "$here/test_p9run.py"
# A3: every byte of the shipped __.SYMDEF tables past a name's NUL is
# accounted for (libmach's readar replayed; /mips/bin/rl's stack frames).
python3 "$here/test_p9symdef.py"
# A3: the shipped zc reproduces shipped libc.a members, one file from each
# libc directory (a sample of `tools/p9kbuild.py libc --check`: 102 files,
# 94 identical, the 8 others built from assembler -- the long command in
# docs/plan9_boot_plan.md A3).  --check fails on any object that differs:
# observed 2026-11-23 with the expected-to-differ set emptied, `--only
# port/strlen,port/toupper --check` printed "FAILED: port/strlen" and
# exited 1; an --only name with no libc.a member stops the run.
python3 "$hobbit/tools/p9kbuild.py" libc --check -j 3 --build "$tmp/p9kbuild" \
    --only port/toupper,hobbit/getfcr,9sys/fork
# A5: the boot ROM's fpi, rebuilt from the release's sources with the
# shipped za/zc/zl on the model, must equal tools/p9kbuild/fpi.rom (what
# p9boot loads; ~30 s).  Observed 2026-11-23 with one byte of the
# committed fpi.rom changed in a scratch copy: "FAILED: fpi.rom differs",
# exit 1.
python3 "$hobbit/tools/p9kbuild.py" fpi --check -j 3 --build "$tmp/p9kbuild"
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

# 009 (ADDI) now runs on the core too: the interlocked forms were
# implemented for the s9term boot.  022: ORI/ANDI's accumulator write and
# R4 as the destination (the kernel's tas).  023: a wrong-path operand
# read that would fault must not raise the exception (the kernel's
# netadd); the core runs it with PSW.V = 1 and only page 0 mapped
# (023.md "Pre-state"), the reference physically -- the architectural
# trace is the same.  024: CATCH with an absolute and a stack-offset-
# indirect target (the kernel's interrupt return).  Each three ways.
for n in 009 022 023 024; do
    "$hobbit/bsv/run_golden.sh" "$n" > "$tmp/$n.model.raw"
    grep '^HRI ' "$tmp/$n.model.raw" > "$tmp/$n.model"
    python3 "$here/hri_check.py" --dut-lines "$tmp/$n.model" \
        --spec-lines "$here/golden/$n.trace"

    python3 "$hobbit/sem/hobbit_sem.py" --image "$here/golden/$n.hex" \
        --sp 0x100 --msp 0x180 2>/dev/null | grep '^HRI ' > "$tmp/$n.sem"
    python3 "$here/hri_check.py" --dut-lines "$tmp/$n.sem" \
        --spec-lines "$here/golden/$n.trace"
done

# The kernel boot on the core, a short sample (docs/p9boot.md, "The boot
# on the core"): the shipped s9term from the ROM hand-off, physical
# addressing, the first CRET into virtual mode (record 2,064), `main`
# (125,203) and the kernel's first interlocked ORI (tas, 126,600), every
# record compared with the reference boot and every device access
# replayed from it.  300,000 records; the long run is the documented
# `bsv/run_p9kern.sh 2893000`, through `/boot`'s first system call.
"$hobbit/bsv/run_p9kern.sh" 300000 "$tmp/p9kern" > "$tmp/p9kern.out" 2>&1 || {
    tail -20 "$tmp/p9kern.out"
    echo "hobbit: the s9term boot on the core diverged" >&2
    exit 1
}
grep '^P9KERN\|^MATCH' "$tmp/p9kern.out"
grep -q '^125203 main$' "$tmp/p9kern/rec/functions" || {
    echo "hobbit: the s9term boot sample did not reach main" >&2
    exit 1
}

# A2 on the Bluespec core: the shipped 1e za and zl run on the model,
# every retirement compared with the reference run (bsv/run_p9host.sh);
# za's object is compared with the shipped libc.a member.
P9HOST_SIM=bluesim "$here/run_p9host_tests.sh"

# The Verilator build of the same testbench (bsv/build_p9host_vl.sh) on
# the recording the last step left, zc frexp.c: its whole output --
# 1,652,549 HRI lines, cyc included, and the P9HOST lines -- must be
# byte-identical to Bluesim's, and so must the files it wrote
# (docs/bluespec_architecture.md, "Simulators").  About 30 s to build and
# 35 s to run, against Bluesim's 135 s for the same run (2026-11-23,
# heavily loaded machine).  Skipped, loudly, where Verilator is missing.
if command -v "${VERILATOR:-verilator}" > /dev/null 2>&1; then
    work=${P9HOST_WORK:-$hobbit/bsv/p9work}
    "$hobbit/bsv/build_p9host_vl.sh" > "$tmp/vl_build.log" 2>&1 || {
        tail -30 "$tmp/vl_build.log"; echo "hobbit: the Verilator build failed" >&2; exit 1; }
    mkdir -p "$tmp/vl/out"
    P9REC="$work/p9.rec" P9OUT="$tmp/vl/out" "$hobbit/bsv/sim_p9host_vl" \
        > "$tmp/vl/core.log" 2>&1 || {
        tail -5 "$tmp/vl/core.log"; echo "hobbit: the Verilator run failed" >&2; exit 1; }
    # run_p9host.sh touches out/console after the Bluesim run.
    touch "$tmp/vl/out/console"
    if ! cmp "$work/core.log" "$tmp/vl/core.log" || ! diff -r "$work/out" "$tmp/vl/out"; then
        echo "hobbit: Verilator and Bluesim differ on zc frexp.c" >&2
        exit 1
    fi
    echo "verilator: zc frexp.c, $(grep -c '^HRI ' "$tmp/vl/core.log") HRI records and the files written, identical to Bluesim's"
else
    echo "hobbit: SKIPPED the Verilator cross-check (verilator not installed)"
fi

echo "hobbit: all tests passed"
