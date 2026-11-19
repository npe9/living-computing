#!/bin/sh
# Build the ULX3S (LFE5U-85F, CABGA381) bitstream for the ATT92010 Hobbit
# model: bsc Verilog -> yosys synth_ecp5 -> nextpnr-ecp5 -> ecppack.
#
# Every product lands in ./build, which is gitignored.  The program image is
# regenerated from ../bsv/smoke.hex on every run, so the FPGA and the Bluesim
# smoke test execute the same bytes.
#
# Toolchain used on this machine (see README.md):
#   bsc        2026.01
#   yosys      0.51
#   nextpnr    0.6 (ecp5)
#   ecppack    1.4
set -eu
cd "$(dirname "$0")"

BUILD=build
mkdir -p "$BUILD"

# --- bsc ------------------------------------------------------------------
# BLUESPECDIR is mandatory for this bsc build, and -p REPLACES the default
# package path, so the bundled Libraries directory must be listed explicitly
# after our own two search directories.
BSC=${BSC_BIN:-$(ls -d /opt/homebrew/Cellar/bsc/*/bin/bsc 2>/dev/null | sort | tail -1)}
if [ -z "$BSC" ] || [ ! -x "$BSC" ]; then
  echo "build.sh: bsc not found; set BSC_BIN to the 2026.01 bsc binary" >&2
  exit 1
fi
BLUESPECDIR=$(cd "$(dirname "$BSC")/../libexec/lib" && pwd)
export BLUESPECDIR
PATH=$(dirname "$BSC"):$PATH
export PATH

# The image, not a BSV literal, is the program.  mk_image_bsv.py emits the
# package SmokeImage with imageLength()/imageWord().  The -bdir directory is
# added to the head of bsc's package path, so the freshly generated copy in
# build/ is the one compiled.
python3 ../bsv/mk_image_bsv.py ../bsv/smoke.hex SmokeImage > "$BUILD/SmokeImage.bsv"

# bsc resolves -vdir relative to the working directory; the source is in
# ../bsv, so -vdir keeps the generated Verilog out of the source tree.
# -bdir is added to the head of the package path automatically; only ../bsv
# and the bundled Libraries need to be listed.
"$BSC" +RTS -K512M -RTS -verilog -g mkHobbitUlx3s -u \
  -vdir "$BUILD" -bdir "$BUILD" -info-dir "$BUILD" \
  -p "../bsv:$BLUESPECDIR/Libraries" \
  ../bsv/HobbitUlx3s.bsv

# --- yosys ----------------------------------------------------------------
# The board top is the Verilog wrapper ulx3s_top, not the Bluespec module:
# the LPF constrains the wrapper's board pins (CLK, BTN1, led, ftdi_*,
# wifi_en), so ulx3s_top must be the synthesis top.  mkHobbitUlx3s is
# instantiated inside it and yosys checks the whole hierarchy.
#
# bsc leaves a few library cells un-inlined (today SizedFIFO and BRAM2 from
# the block-RAM retirement queue; FIFO2 on the older netlist; and RegFile --
# bsc does NOT inline RegFile, so an inferred memory appears as an instance
# of `RegFile', with `RegFileLoad' when the array carries a load file).
# Read exactly the library models the netlist instantiates: that keeps the
# design closed without dragging in the distribution's other readmem-based
# RAM models, which yosys cannot parse here.
LIBREADS=""
for m in $(sed -n 's/^  \([A-Z][A-Za-z0-9_]*\)[ #(].*/\1/p' "$BUILD/mkHobbitUlx3s.v" | sort -u); do
  if [ -f "$BLUESPECDIR/Verilog/$m.v" ]; then
    LIBREADS="$LIBREADS read_verilog $BLUESPECDIR/Verilog/$m.v;"
  fi
done
if [ -z "$LIBREADS" ]; then
  echo "build.sh: no bsc library cells found in the generated Verilog" >&2
  exit 1
fi

yosys -p "read_verilog $BUILD/mkHobbitUlx3s.v; \
          read_verilog ../bsv/HobbitUlx3sTop.v; \
          $LIBREADS \
          synth_ecp5 -top ulx3s_top -json $BUILD/ulx3s_top.json" \
      -l "$BUILD/yosys.log"

# --- nextpnr --------------------------------------------------------------
# --timing-allow-fail lets the flow still produce a bitstream when the 25 MHz
# target is missed; the measured frequency and the critical path are in
# build/nextpnr.log and quoted in README.md, and the check below is loud.
nextpnr-ecp5 --85k --package CABGA381 --speed 6 \
  --json "$BUILD/ulx3s_top.json" \
  --lpf ulx3s_85f.lpf \
  --textcfg "$BUILD/ulx3s_top.config" \
  --freq 25 --timing-allow-fail --seed 1 \
  --log "$BUILD/nextpnr.log"

# --- ecppack --------------------------------------------------------------
ecppack --compress "$BUILD/ulx3s_top.config" "$BUILD/hobbit_ulx3s.bit"

# --- report ---------------------------------------------------------------
echo
echo "=== yosys cell counts ==============================================="
sed -n '/Number of cells:/,/^$/p' "$BUILD/yosys.log" | sed -n '1,60p'
echo
echo "=== nextpnr utilisation and timing =================================="
grep -E 'Total LUT4s|logic LUTs|carry LUTs|RAM LUTs|RAMW LUTs|Total DFFs|Total DP16KD|TRELLIS_FF|Max frequency|Max delay' \
  "$BUILD/nextpnr.log" | sed -n '1,40p'
echo
echo "=== nextpnr critical path ==========================================="
sed -n '/Critical path report/,/^$/p' "$BUILD/nextpnr.log" | head -30
echo
echo "=== bitstream ======================================================="
ls -l "$BUILD/hobbit_ulx3s.bit"

if grep -q 'Max frequency for clock.*FAIL' "$BUILD/nextpnr.log"; then
  echo
  echo "build.sh: WARNING: 25 MHz timing NOT met (see the nextpnr report above)" >&2
fi
