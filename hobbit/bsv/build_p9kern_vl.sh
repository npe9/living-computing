#!/bin/sh
# Build the Verilator twin of run_p9kern.sh's sim_p9kern: P9KernTb.bsv +
# p9kern.c (docs/bluespec_architecture.md, "Simulators";
# docs/p9boot.md, "The boot on the core").  run_p9kern.sh calls this
# when P9KERN_SIM=verilator.
#
#   bsv/build_p9kern_vl.sh DIR
#
# builds DIR/sim_p9kern_vl, with every intermediate in DIR/vl (its own
# -bdir: bsc's .bo files do not record -D, and the Bluesim build's .bo
# files do not have it).
#
#   1. bsc -verilog -use-dpi -D P9KERN_FLAT: the board memory inlined, so
#      the whole testbench, core included, is ONE Verilog module and every
#      Action/ActionValue C call is in its one `always @(negedge CLK)`
#      block, in Bluesim's order (build_p9host_vl.sh says why).  The pure
#      C function pk_peek (the table walk's and the event unit's reads)
#      is in continuous assignments, as bsc writes any pure function.
#   2. p9kern.c, unchanged.
#   3. verilator --no-timing (build_p9host_vl.sh says why).  vl_main.cpp
#      without VL_P9HOST: the simulator exits 0 at the testbench's $finish,
#      as Bluesim's does whatever $finish is passed (vl_main.cpp); the
#      verdict is run_p9kern.sh's comparison.
set -eu
if [ $# -ne 1 ]; then
  echo "usage: build_p9kern_vl.sh DIR" >&2
  exit 2
fi
mkdir -p "$1"
out=$(cd "$1" && pwd)
cd "$(dirname "$0")"
here=$(pwd)

BSC=${BSC_BIN:-}
if [ -z "$BSC" ]; then
  BSC=$(ls -d /opt/homebrew/Cellar/bsc/*/bin/bsc 2>/dev/null | sort | tail -1)
fi
if [ -z "$BSC" ] || [ ! -x "$BSC" ]; then
  echo "bsc not found; set BSC_BIN to the 2026.01 bsc binary" >&2
  exit 1
fi
BLUESPECDIR=$(cd "$(dirname "$BSC")/../libexec/lib" && pwd)
export BLUESPECDIR
VERILATOR=${VERILATOR:-verilator}
if ! command -v "$VERILATOR" > /dev/null 2>&1; then
  echo "build_p9kern_vl.sh: verilator not found (brew install verilator)" >&2
  exit 1
fi

b=$out/vl
mkdir -p "$b"

"$BSC" +RTS -K512M -RTS -verilog -use-dpi -D P9KERN_FLAT \
    -g mkP9KernTb -u -vdir "$b" -bdir "$b" -info-dir "$b" \
    P9KernTb.bsv

# The flat build's promise, checked: one module, one negedge block.
if [ "$(grep -c '^module ' "$b/mkP9KernTb.v")" != 1 ] ||
   [ "$(grep -c 'always@(negedge CLK)' "$b/mkP9KernTb.v")" != 1 ]; then
  echo "build_p9kern_vl.sh: mkP9KernTb.v is not one module with one negedge block" >&2
  exit 1
fi

${CC:-cc} -O2 -c p9kern.c -o "$b/p9kern.o"

# Verilator's makefile does not see a change to a prebuilt object, so
# the binary is removed to force the link.
rm -f "$b/obj/VmkP9KernTb" "$out/sim_p9kern_vl"
"$VERILATOR" --cc --exe --build -j "${VL_JOBS:-4}" -O3 \
    --x-assign fast --x-initial fast --no-timing \
    -Wno-fatal -Wno-lint -Wno-style -Wno-STMTDLY \
    --top-module mkP9KernTb -y "$BLUESPECDIR/Verilog" -Mdir "$b/obj" \
    -CFLAGS "-O2 -DVL_TOP=VmkP9KernTb -DVL_TOP_H='\"VmkP9KernTb.h\"' -DVL_USER_FINISH" \
    "$b/mkP9KernTb.v" "$here/vl_main.cpp" "$b/p9kern.o"
cp "$b/obj/VmkP9KernTb" "$out/sim_p9kern_vl"
