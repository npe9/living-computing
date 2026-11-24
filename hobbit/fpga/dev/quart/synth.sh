#!/bin/sh
# yosys synth_ecp5 of the Quart and the interrupt-path devices alone (no
# place and route: the SoC top owns that), one module at a time:
#
#   sh hobbit/fpga/dev/quart/synth.sh
#
# mkHobbitQuartSynth is the Quart at board-ish parameters (25 MHz clock:
# 1302 clocks a bit = 19200 baud on channel 0, C/T clock 25 MHz * 1152 /
# 125000 = 230400 Hz).  Prints yosys's cell statistics per module.  Build
# products go to a scratch directory (BUILD_DIR to keep them).
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
BSC=${BSC_BIN:-$(ls -d /opt/homebrew/Cellar/bsc/*/bin/bsc 2>/dev/null | sort | tail -1)}
BLUESPECDIR=$(cd "$(dirname "$BSC")/../libexec/lib" && pwd)
export BLUESPECDIR
BUILD=${BUILD_DIR:-$(mktemp -d "${TMPDIR:-/tmp}/hobbit-quart-syn.XXXXXX")}
[ -n "${BUILD_DIR:-}" ] || trap 'rm -rf "$BUILD"' EXIT
mkdir -p "$BUILD/src" "$BUILD/obj"
cp "$HERE/HobbitQuart.bsv" "$HERE/../intc/HobbitIntc.bsv" "$BUILD/src/"
cd "$BUILD/src"
"$BSC" +RTS -K512M -RTS -verilog -bdir "$BUILD/obj" -vdir "$BUILD/obj" \
    -info-dir "$BUILD/obj" -aggressive-conditions -u HobbitQuart.bsv \
    >"$BUILD/bsc.log" 2>&1 || { cat "$BUILD/bsc.log"; exit 1; }
"$BSC" +RTS -K512M -RTS -verilog -bdir "$BUILD/obj" -vdir "$BUILD/obj" \
    -info-dir "$BUILD/obj" -aggressive-conditions -u HobbitIntc.bsv \
    >>"$BUILD/bsc.log" 2>&1 || { cat "$BUILD/bsc.log"; exit 1; }
for top in mkHobbitQuartSynth mkHobbitIrq mkHobbitIoctl mkHobbitIncon; do
  libs=""
  for cell in $(grep -ho '^  *\(FIFO[0-9A-Za-z]*\|SizedFIFO\|RegFile[A-Za-z]*\|BRAM[0-9A-Za-z]*\) ' \
                "$BUILD/obj/$top.v" | sort -u); do
    libs="$libs read_verilog $BLUESPECDIR/Verilog/$cell.v;"
  done
  yosys -q -p "read_verilog $BUILD/obj/$top.v; $libs
               synth_ecp5 -top $top; tee -o $BUILD/$top.stat stat" \
      >"$BUILD/$top.yosys.log" 2>&1 || { tail -20 "$BUILD/$top.yosys.log"; exit 1; }
  echo "== $top"
  grep -E 'Number of cells|LUT4|PFUMX|L6MUX21|CCU2C|TRELLIS_FF|TRELLIS_DPR16X4|DP16KD' \
      "$BUILD/$top.stat"
done
