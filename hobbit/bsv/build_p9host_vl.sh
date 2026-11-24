#!/bin/sh
# Build sim_p9host_vl: P9HostTb.bsv + p9host.c on Verilator, the fast
# twin of Bluesim's sim_p9host (docs/bluespec_architecture.md,
# "Simulators").  run_p9host.sh calls this when P9HOST_SIM=verilator.
#
#   1. bsc -verilog -use-dpi -D P9HOST_FLAT: one Verilog module for the
#      whole testbench (P9HostTb.bsv says why it must be one), with the
#      BDPI imports as `import "DPI-C"`.  Its own -bdir, because bsc's .bo
#      files do not record -D, and the Bluesim build's are in bsv/.
#   2. p9host.c, unchanged, compiled with -Dp9h_poll=p9h_poll_c: the
#      driver wraps p9h_poll to learn the exit status (vl_main.cpp).
#   3. verilator --no-timing.  bsc puts every C call of a clock in one
#      `always @(negedge CLK)` block and follows each with `#0`, and it
#      computes, inside the block, every value a later call needs, so the
#      `#0`s carry nothing here (STMTDLY is the warning that they are
#      ignored).  With --timing, Verilator did honour them, but then did
#      not re-evaluate the continuous assignments that read what the block
#      wrote after its last resumption, and a stack-cache refill never
#      started (observed 2026-11-23 on echo; the -O0 build failed
#      differently).  --no-timing runs the block as one piece, as Bluesim
#      runs the rules.
#
# Products: ../build/verilator/p9host/ (gitignored) and bsv/sim_p9host_vl.
set -eu
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
  echo "build_p9host_vl.sh: verilator not found (brew install verilator)" >&2
  exit 1
fi

b=$here/../build/verilator/p9host
mkdir -p "$b"

"$BSC" +RTS -K512M -RTS -verilog -use-dpi -D P9HOST_FLAT \
    -g mkP9HostTb -u -vdir "$b" -bdir "$b" -info-dir "$b" \
    P9HostTb.bsv

${CC:-cc} -O2 -Dp9h_poll=p9h_poll_c -c p9host.c -o "$b/p9host.o"

# Verilator's makefile does not see a change to a prebuilt object, so
# the binary is removed to force the link.
rm -f "$b/obj/VmkP9HostTb" "$here/sim_p9host_vl"
"$VERILATOR" --cc --exe --build -j "${VL_JOBS:-4}" -O3 \
    --x-assign fast --x-initial fast --no-timing \
    -Wno-fatal -Wno-lint -Wno-style -Wno-STMTDLY \
    --top-module mkP9HostTb -y "$BLUESPECDIR/Verilog" -Mdir "$b/obj" \
    -CFLAGS "-O2 -DVL_TOP=VmkP9HostTb -DVL_TOP_H='\"VmkP9HostTb.h\"' -DVL_USER_FINISH -DVL_P9HOST" \
    "$b/mkP9HostTb.v" "$here/vl_main.cpp" "$b/p9host.o"
cp "$b/obj/VmkP9HostTb" "$here/sim_p9host_vl"
