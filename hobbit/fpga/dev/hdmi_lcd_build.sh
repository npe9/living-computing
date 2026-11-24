#!/bin/sh
# Build the Lcdisp + HDMI test bitstream (ulx3s_plan.md step 4):
# bsc (LcdLcdisp.bsv -> mkLcdisp.v) -> yosys synth_ecp5 -> nextpnr-ecp5 ->
# ecppack.  Also synthesizes mkLcdisp alone, for the device's own block-RAM
# and LUT count.  Products in ../build/lcd (gitignored).  Never programs the
# board.
#
#   sh hobbit/fpga/dev/hdmi_lcd_build.sh [SEED]
set -eu
cd "$(dirname "$0")"
SEED=${1:-2}
OUT=../build/lcd
mkdir -p "$OUT/bsc"

BSC=${BSC_BIN:-$(ls -d /opt/homebrew/Cellar/bsc/*/bin/bsc 2>/dev/null | sort | tail -1)}
BLUESPECDIR=$(cd "$(dirname "$BSC")/../libexec/lib" && pwd)
export BLUESPECDIR

"$BSC" -verilog -g mkLcdisp -u -vdir "$OUT/bsc" -bdir "$OUT/bsc" \
  -info-dir "$OUT/bsc" -p ".:$BLUESPECDIR/Libraries" LcdLcdisp.bsv

LIB="read_verilog -DBSV_NO_INITIAL_BLOCKS $BLUESPECDIR/Verilog/BRAM2.v;
     read_verilog -DBSV_NO_INITIAL_BLOCKS $BLUESPECDIR/Verilog/FIFO2.v"

# the device alone
yosys -q -l "$OUT/yosys_lcdisp.log" -p "
  read_verilog -DBSV_NO_INITIAL_BLOCKS $OUT/bsc/mkLcdisp.v; $LIB
  synth_ecp5 -top mkLcdisp; stat"

# the test bitstream
yosys -q -l "$OUT/yosys_top.log" -p "
  read_verilog -DBSV_NO_INITIAL_BLOCKS $OUT/bsc/mkLcdisp.v; $LIB
  read_verilog hdmi_tmds.v hdmi_scan.v lcd_pattern.v hdmi_lcd_top.v
  synth_ecp5 -top hdmi_lcd_top -json $OUT/hdmi_lcd_top.json; stat"

nextpnr-ecp5 --85k --package CABGA381 --speed 6 \
  --json "$OUT/hdmi_lcd_top.json" --lpf hdmi_lcd.lpf \
  --textcfg "$OUT/hdmi_lcd_top.config" --timing-allow-fail --seed "$SEED" \
  --log "$OUT/nextpnr.log" -q

ecppack --compress "$OUT/hdmi_lcd_top.config" "$OUT/hdmi_lcd_top.bit"

echo "=== mkLcdisp alone (yosys) ==="
sed -n '/Number of cells/,/^$/p' "$OUT/yosys_lcdisp.log" | tail -n +1
echo "=== test top (nextpnr) ==="
grep -E 'TRELLIS_COMB|TRELLIS_FF|DP16KD|EHXPLLL|TRELLIS_IO' "$OUT/nextpnr.log" | tail -5
grep 'Max frequency for clock' "$OUT/nextpnr.log" | tail -3
ls -l "$OUT/hdmi_lcd_top.bit"
