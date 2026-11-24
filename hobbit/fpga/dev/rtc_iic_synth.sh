#!/bin/sh
# yosys synth_ecp5 of mkRtc and mkIic alone (ULX3S 85F cell counts for
# rtc.md / iic.md).  mkRtc is synthesised at the board's 25 MHz with the
# model's start time.  Products in ./build (gitignored).  Run from any
# directory; the $readmemh files resolve against this one.
set -eu
cd "$(dirname "$0")"
BSC=${BSC_BIN:-$(ls -d /opt/homebrew/Cellar/bsc/*/bin/bsc 2>/dev/null | sort | tail -1)}
BLUESPECDIR=$(cd "$(dirname "$BSC")/../libexec/lib" && pwd)
export BLUESPECDIR
mkdir -p build
"$BSC" -verilog -g mkRtc -u -vdir build -bdir build -info-dir build -p + Rtc.bsv >/dev/null 2>&1
"$BSC" -verilog -g mkIic -u -vdir build -bdir build -info-dir build -p + Iic.bsv >/dev/null 2>&1
LIB="read_verilog -defer $BLUESPECDIR/Verilog/RegFileLoad.v; read_verilog -defer $BLUESPECDIR/Verilog/FIFO2.v"
# -defer: RegFileLoad's default file="" must not be elaborated (yosys
# would try to $readmemh it); only the instance's parameters are.
yosys -q -l build/synth_rtc.log -p "read_verilog -defer build/mkRtc.v; $LIB;
  chparam -set ticksPerSec 25000000 -set startBcd 56'h93010301120000 mkRtc;
  synth_ecp5 -top mkRtc -json build/mkRtc.json; tee -o build/stat_rtc.txt stat"
yosys -q -l build/synth_iic.log -p "read_verilog -defer build/mkIic.v; $LIB;
  synth_ecp5 -top mkIic -json build/mkIic.json; tee -o build/stat_iic.txt stat"
for d in rtc iic; do
  echo "== mk$(echo $d | sed 's/r/R/;s/^i/I/')"
  grep -E '^ +(LUT4|PFUMX|L6MUX21|CCU2C|TRELLIS_FF|TRELLIS_DPR16X4|DP16KD|MULT18X18D) ' build/stat_$d.txt
done
