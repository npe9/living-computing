#!/bin/sh
# Synthesis-only area of mkHobbitSocCpu (no placement), for the SoC's
# area budget (fpga/README.md, "Area").
#
#   ./area_cpu.sh NAME [BSVDIR]
#
# BSVDIR (default ../bsv) lets a measurement variant be compiled from a
# copy of the sources; everything lands in build/area-NAME.  BSC_FLAGS adds
# bsc options (e.g. -opt-undetermined-vals -unspecified-to X).
set -eu
cd "$(dirname "$0")"
NAME=$1
SRC=${2:-../bsv}
B=build/area-$NAME
mkdir -p "$B"
BSC=${BSC_BIN:-$(ls -d /opt/homebrew/Cellar/bsc/*/bin/bsc 2>/dev/null | sort | tail -1)}
BLUESPECDIR=$(cd "$(dirname "$BSC")/../libexec/lib" && pwd)
export BLUESPECDIR
"$BSC" +RTS -K512M -RTS -verilog -g mkHobbitSocCpu -u ${BSC_FLAGS:-} \
  -vdir "$B" -bdir "$B" -info-dir "$B" \
  -p "$SRC:$BLUESPECDIR/Libraries" "$SRC/HobbitSocCpu.bsv" > "$B/bsc.log" 2>&1 \
  || { tail -20 "$B/bsc.log"; exit 1; }
LIBREADS=""
for m in $(sed -n 's/^  \([A-Z][A-Za-z0-9_]*\)[ #(].*/\1/p' "$B/mkHobbitSocCpu.v" | sort -u); do
  [ -f "$BLUESPECDIR/Verilog/$m.v" ] && LIBREADS="$LIBREADS read_verilog $BLUESPECDIR/Verilog/$m.v;"
done
yosys -p "read_verilog $B/mkHobbitSocCpu.v; $LIBREADS \
          synth_ecp5 -top mkHobbitSocCpu -json $B/cpu.json" -l "$B/yosys.log" > /dev/null
sed -n '/=== mkHobbitSocCpu ===/,/^$/p' "$B/yosys.log" | tail -1
grep -E '^ +(LUT4|PFUMX|L6MUX21|CCU2C|TRELLIS_FF|TRELLIS_DPR16X4|DP16KD|MULT18X18D) ' "$B/yosys.log" | tail -8
