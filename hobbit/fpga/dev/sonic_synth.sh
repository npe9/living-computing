#!/bin/sh
# yosys synth_ecp5 of the SONIC subset and the ESP32 link alone (no place
# and route: the SoC top owns that), one module at a time:
#
#   sh hobbit/fpga/dev/sonic_synth.sh
#
# mkSonic is the engine as it is replayed; mkEspLink25M is the link at the
# ULX3S's 25 MHz and 2.5 Mbaud (10 clocks a bit).  Prints yosys's cell
# statistics per module.  Build products go to a scratch directory
# (BUILD_DIR to keep them).  The pattern is quart/synth.sh.
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
BSC=${BSC_BIN:-$(ls -d /opt/homebrew/Cellar/bsc/*/bin/bsc 2>/dev/null | sort | tail -1)}
BLUESPECDIR=$(cd "$(dirname "$BSC")/../libexec/lib" && pwd)
export BLUESPECDIR
BUILD=${BUILD_DIR:-$(mktemp -d "${TMPDIR:-/tmp}/hobbit-sonic-syn.XXXXXX")}
[ -n "${BUILD_DIR:-}" ] || trap 'rm -rf "$BUILD"' EXIT
mkdir -p "$BUILD/src" "$BUILD/obj"
cp "$HERE/Sonic.bsv" "$HERE/EspLink.bsv" "$BUILD/src/"
cd "$BUILD/src"
for pkg in Sonic EspLink; do
  "$BSC" +RTS -K512M -RTS -verilog -bdir "$BUILD/obj" -vdir "$BUILD/obj" \
      -info-dir "$BUILD/obj" -aggressive-conditions \
      -suppress-warnings G0010:G0024 -u $pkg.bsv \
      >>"$BUILD/bsc.log" 2>&1 || { cat "$BUILD/bsc.log"; exit 1; }
done
for top in mkSonic mkEspLink25M; do
  libs=""
  for cell in $(grep -ho '^  *\(FIFO[0-9A-Za-z]*\|SizedFIFO\|RegFile[A-Za-z]*\|BRAM[0-9A-Za-z]*\|SyncFIFO[0-9A-Za-z]*\) ' \
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
