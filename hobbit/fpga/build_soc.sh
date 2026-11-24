#!/bin/sh
# Build the Hobbit SoC bitstream for the ULX3S (fpga/README.md, "The SoC"):
# bsc (bsv/HobbitSocCpu.bsv -> mkHobbitSocCpu.v) -> yosys synth_ecp5 ->
# nextpnr-ecp5 -> ecppack.  Products in build/soc (gitignored).
#
#   ./build_soc.sh [SEED]        the SoC with the privileged core
#   ./build_soc.sh stub [SEED]   the periphery only: rtl/cpu_stub.v stands
#                                in for the core (build/soc-stub), to place
#                                and time the adapter, SDRAM controller and
#                                host link while the core does not fit
#
# Nothing here touches the board.
set -eu
cd "$(dirname "$0")"
STUB=0
if [ "${1:-}" = stub ]; then STUB=1; shift; fi
SEED=${1:-1}
B=build/soc
[ $STUB = 1 ] && B=build/soc-stub
mkdir -p "$B"

if [ $STUB = 1 ]; then
  CPUREADS="read_verilog rtl/cpu_stub.v;"
else
BSC=${BSC_BIN:-$(ls -d /opt/homebrew/Cellar/bsc/*/bin/bsc 2>/dev/null | sort | tail -1)}
if [ -z "$BSC" ] || [ ! -x "$BSC" ]; then
  echo "build_soc.sh: bsc not found; set BSC_BIN" >&2
  exit 1
fi
BLUESPECDIR=$(cd "$(dirname "$BSC")/../libexec/lib" && pwd)
export BLUESPECDIR

# Its own -bdir: bsc's .bo files record no flags, and the regression
# suite compiles the same packages in bsv/.
"$BSC" +RTS -K512M -RTS -verilog -g mkHobbitSocCpu -u \
  -vdir "$B" -bdir "$B" -info-dir "$B" \
  -p "../bsv:$BLUESPECDIR/Libraries" ../bsv/HobbitSocCpu.bsv > "$B/bsc.log" 2>&1 \
  || { tail -30 "$B/bsc.log"; exit 1; }
if grep -q 'G0021' "$B/bsc.log"; then
  echo "build_soc.sh: bsc reports a rule that can never fire:" >&2
  grep -A2 G0021 "$B/bsc.log" >&2
  exit 1
fi

# The bsc library cells the netlist instantiates (build.sh does the same).
LIBREADS=""
for m in $(sed -n 's/^  \([A-Z][A-Za-z0-9_]*\)[ #(].*/\1/p' "$B/mkHobbitSocCpu.v" | sort -u); do
  if [ -f "$BLUESPECDIR/Verilog/$m.v" ]; then
    LIBREADS="$LIBREADS read_verilog $BLUESPECDIR/Verilog/$m.v;"
  fi
done

CPUREADS="read_verilog $B/mkHobbitSocCpu.v; $LIBREADS"
fi

yosys -p "$CPUREADS \
          read_verilog rtl/uart8n1.v rtl/hostlink.v rtl/sdram_word.v \
                       rtl/hobbit_soc_mem.v rtl/hobbit_soc.v rtl/ulx3s_hobbit_top.v; \
          synth_ecp5 -top ulx3s_hobbit_top -json $B/top.json" \
      -l "$B/yosys.log" > /dev/null

nextpnr-ecp5 --85k --package CABGA381 --speed 6 \
  --json "$B/top.json" --lpf ulx3s_soc.lpf \
  --textcfg "$B/top.config" \
  --freq 25 --timing-allow-fail --seed "$SEED" \
  --log "$B/nextpnr.log" > /dev/null 2>&1 || {
  echo "build_soc.sh: nextpnr failed; its utilisation and error:" >&2
  grep -E 'Total LUT4s|TRELLIS_COMB|TRELLIS_FF|DP16KD|MULT18X18D|ERROR' "$B/nextpnr.log" | head -12 >&2
  exit 1
}

ecppack --compress "$B/top.config" "$B/hobbit_soc.bit"

echo "=== yosys =========================================================="
sed -n '/=== ulx3s_hobbit_top ===/,/^$/p;/Number of cells:/,/^$/p' "$B/yosys.log" | tail -30
echo "=== nextpnr ========================================================"
grep -E 'TRELLIS_COMB|TRELLIS_FF|DP16KD|MULT18X18D|TRELLIS_RAMW|DCCA|TRELLIS_IO' "$B/nextpnr.log" | tail -8
grep 'Max frequency for' "$B/nextpnr.log" | tail -4
ls -l "$B/hobbit_soc.bit"
