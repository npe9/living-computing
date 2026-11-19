#!/bin/sh
# Board-level build check for the ULX3S / ECP5 target (plan.md WP4.3).
#
# Reproducible from a clean tree: regenerates the hex images, recompiles
# PimUlx3s.bsv to Verilog, synthesizes with Yosys, places/routes with
# nextpnr-ecp5, and packs a bitstream with ecppack into a fresh build
# directory.  Nothing from a previous run is reused.
#
# WP2 decision gate: plan.md and bsv/README.md record the flow as not
# hardware-ready.  This script reports the measured Fmax and always prints
# that gate; a timing miss is not a build failure.  It exits nonzero only
# for tool/flow errors (missing tool, missing constraint file, synthesis,
# place-and-route, or bitstream packing).
#
# Required tools and the versions this check was written against:
#   bsc            2026.01 (set BSC_BIN to override; otherwise the newest
#                  Homebrew Cellar install is used, as in run_smoke.sh)
#   yosys          0.51
#   nextpnr-ecp5   0.6
#   ecppack        Project Trellis 1.4
# Override the build directory with FPGA_BUILD_DIR (must be a path that
# may be deleted and recreated).
set -eu
cd "$(dirname "$0")"

BUILD=${FPGA_BUILD_DIR:-fpga_build}
TARGET_MHZ=25

die() {
  echo "run_fpga_build: $*" >&2
  exit 1
}

# --- Tool discovery -------------------------------------------------
BSC=${BSC_BIN:-}
if [ -z "$BSC" ]; then
  BSC=$(ls -d /opt/homebrew/Cellar/bsc/*/bin/bsc 2>/dev/null | sort | tail -1)
fi
if [ -z "$BSC" ] || [ ! -x "$BSC" ]; then
  die "bsc not found; set BSC_BIN to the 2026.01 bsc binary"
fi
BLUESPECDIR=$(cd "$(dirname "$BSC")/../libexec/lib" && pwd)
export BLUESPECDIR
PATH=$(dirname "$BSC"):$PATH
export PATH

for tool in python3 yosys nextpnr-ecp5 ecppack; do
  command -v "$tool" >/dev/null 2>&1 || die "required tool not found: $tool"
done
[ -f ulx3s_85f.lpf ] || die "missing constraint file: bsv/ulx3s_85f.lpf"
[ -f Top.v ] || die "missing board top: bsv/Top.v"
[ -f RegFileLoad.v ] || die "missing memory wrapper: bsv/RegFileLoad.v"

# --- Fresh build directory -----------------------------------------
rm -rf "$BUILD"
mkdir -p "$BUILD/bsc" "$BUILD/verilog"
echo "== build dir: bsv/$BUILD"

# --- Hex images (PimUlx3s reads generated/*.hex at elaboration) -----
echo "== assembling generated/*.hex"
python3 ../asm/pimasm.py --out-dir generated

# --- Bluespec -> Verilog -------------------------------------------
echo "== bsc: PimUlx3s -> Verilog"
"$BSC" -verilog -u -g mkPimUlx3s \
  -bdir "$BUILD/bsc" -vdir "$BUILD/verilog" \
  PimUlx3s.bsv

# --- Yosys synthesis ------------------------------------------------
# Run from bsv/ so the RegFileLoad file parameters ("generated/*.hex")
# resolve.  The board top is Top.v's ulx3s_top.
echo "== yosys: synth_ecp5"
yosys -l "$BUILD/yosys.log" -p "
  read_verilog \"$BUILD/verilog/mkPimUlx3s.v\" RegFileLoad.v Top.v \"$BLUESPECDIR/Verilog/FIFO2.v\" \"$BLUESPECDIR/Verilog/SizedFIFO.v\";
  synth_ecp5 -top ulx3s_top -json \"$BUILD/ulx3s_top.json\"
" > "$BUILD/yosys.console" 2>&1 || {
  cat "$BUILD/yosys.console" >&2
  die "yosys synthesis failed (see bsv/$BUILD/yosys.log)"
}
[ -s "$BUILD/ulx3s_top.json" ] || die "yosys produced no netlist"

# --- place and route ------------------------------------------------
# --timing-allow-fail is the WP2 gate: a timing miss must not fail the
# check, only a real flow error must.
echo "== nextpnr-ecp5: place and route"
nextpnr-ecp5 --85k --package CABGA381 --speed 6 \
  --json "$BUILD/ulx3s_top.json" \
  --lpf ulx3s_85f.lpf \
  --textcfg "$BUILD/ulx3s_top.config" \
  --log "$BUILD/nextpnr.log" \
  --seed 1 --timing-allow-fail \
  > "$BUILD/nextpnr.console" 2>&1 || {
  cat "$BUILD/nextpnr.console" >&2
  die "nextpnr place-and-route failed (see bsv/$BUILD/nextpnr.log)"
}
[ -s "$BUILD/ulx3s_top.config" ] || die "nextpnr produced no placed/routed config"

# --- bitstream ------------------------------------------------------
echo "== ecppack: bitstream"
ecppack --compress \
  --input "$BUILD/ulx3s_top.config" \
  --bit "$BUILD/ulx3s_top.bit" \
  > "$BUILD/ecppack.console" 2>&1 || {
  cat "$BUILD/ecppack.console" >&2
  die "ecppack failed"
}
[ -s "$BUILD/ulx3s_top.bit" ] || die "ecppack produced no bitstream"

# --- report ---------------------------------------------------------
FMAX_LINE=$(grep "Max frequency for clock" "$BUILD/nextpnr.log" | tail -1 || true)
FMAX_MHZ=$(printf '%s\n' "$FMAX_LINE" | sed -n 's/.*: \([0-9][0-9.]*\) MHz.*/\1/p')
[ -n "$FMAX_MHZ" ] || die "nextpnr log has no clock frequency; flow did not close"

echo
echo "== FPGA build check result"
echo "   bitstream:    bsv/$BUILD/ulx3s_top.bit"
echo "   target clock: ${TARGET_MHZ} MHz (ulx3s_85f.lpf)"
echo "   measured Fmax: ${FMAX_MHZ} MHz"
case "$FMAX_LINE" in
  *FAIL*)
    echo "   timing: FAILED against ${TARGET_MHZ} MHz (expected; see plan.md WP2)"
    ;;
  *)
    echo "   timing: met ${TARGET_MHZ} MHz in this run"
    echo "   note: plan.md/bsv/README.md record a 10.22 MHz ceiling from an"
    echo "         earlier netlist; this measurement contradicts that record."
    echo "         The WP2 decision is not changed by this script."
    ;;
esac
echo
echo "WP2 GATE: NOT HARDWARE-READY. The bitstream is a downstream"
echo "plausibility artifact only. No claim rests on it, and it must not be"
echo "presented as a working PIM/m (plan.md WP2, bsv/README.md). A timing"
echo "miss, if any, is reported above and is not a build failure."
echo "== FPGA build check: PASS (flow completed)"
exit 0