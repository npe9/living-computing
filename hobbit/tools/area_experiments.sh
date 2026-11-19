#!/bin/sh
# area_experiments.sh -- measure the candidate area fixes on the ECP5 flow.
#
# Each experiment is a small, complete top synthesised with the same
# `synth_ecp5` the board uses:
#
#   * program memory: a 256x32 single-write register array versus a
#     256x32 block RAM, both with a registered read address (the board's
#     mkHobbitMem read timing);
#   * stack-cache array: a 64x32 register file with one write port and a
#     combinational 64:1 read, versus the board's vector update;
#   * decoded store: a 32x192 register file with one write port and a
#     combinational 32:1 read, versus the current 192-bit BSV block;
#   * UART writer: the current serial double-dabble writer, with the
#     synthesis area knobs (share -aggressive, abc2, noabc9) tried on it;
#   * unused-interface pruning: proof by grepping the flat netlist for
#     the testbench-only method names.
#
# Usage:
#   tools/area_experiments.sh [path/to/ulx3s_top.json]
#
# The JSON defaults to fpga/build/ulx3s_top.json; run fpga/build.sh or
# the yosys step first.  Products go to a temporary directory.

set -eu

ROOT=$(cd "$(dirname "$0")/.." && pwd)
JSON=${1:-$ROOT/fpga/build/ulx3s_top.json}
YOSYS=${YOSYS:-yosys}
BSC=${BSC_BIN:-$(ls -d /opt/homebrew/Cellar/bsc/*/bin/bsc 2>/dev/null | sort | tail -1)}
if [ -z "$BSC" ] || [ ! -x "$BSC" ]; then
  echo "area_experiments: bsc not found; set BSC_BIN" >&2
  exit 1
fi
BLUESPECDIR=$(cd "$(dirname "$BSC")/../libexec/lib" && pwd)
export BLUESPECDIR
WORK=$(mktemp -d "${TMPDIR:-/tmp}/hobbit_area_exp.XXXXXX")
trap 'rm -rf "$WORK"' EXIT

synth() {
  top=$1
  shift
  extra=$*
  "$YOSYS" -p "read_verilog $WORK/$top.v; $extra synth_ecp5 -top $top -json $WORK/$top.json" \
    -l "$WORK/$top.log" >/dev/null 2>&1 || {
      echo "   yosys failed for $top $extra" >&2; return; }
  awk -v top="$top" -v label="${extra:-reference}" '
    /Number of cells:/ { inb=1; next }
    inb && /^[[:space:]]*$/ { inb=0 }
    inb {
      if ($1 ~ /^(LUT4|PFUMX|TRELLIS_FF|CCU2C|DP16KD)$/) v[$1]=$2;
    }
    END {
      printf "%-22s %-18s %6d %6d %6d %6d %4d\n", top, label,
        v["LUT4"], v["PFUMX"], v["TRELLIS_FF"], v["CCU2C"], v["DP16KD"];
    }' "$WORK/$top.log"
}

echo "== 1. flat board netlist =="
if [ -f "$JSON" ]; then
  python3 "$ROOT/tools/area_netlist.py" "$JSON"
else
  echo "   no $JSON (run the yosys step of fpga/build.sh first)"
fi

echo
echo "== 2. unused testbench-only interface methods =="
if [ -f "$JSON" ]; then
  for s in cacheWord readMem minSp maxSp refills instrs folded peek; do
    n=$(grep -c "$s" "$JSON" || true)
    printf "   %-10s occurrences in netlist: %s\n" "$s" "${n:-0}"
  done
  echo "   (0 means yosys already removed the logic; there is no area to reclaim)"
else
  echo "   skipped: no JSON"
fi

# ------------------------------------------------------------------
# Memory and register-file experiments.  The read timing is the
# board's: the address is registered, the array output is the next
# cycle.  A block RAM infers from the same shape.
# ------------------------------------------------------------------
cat > "$WORK/mem_reg.v" <<'V'
module mem_reg(input clk, input we,
               input [7:0] waddr, input [31:0] wdata,
               input [7:0] raddr, output [31:0] rdata);
  reg [31:0] m [0:255];
  reg [7:0] ra;
  integer i;
  initial for (i = 0; i < 256; i = i + 1) m[i] = 0;
  always @(posedge clk) begin
    ra <= raddr;
    if (we) m[waddr] <= wdata;
  end
  assign rdata = m[ra];
endmodule
V
cat > "$WORK/mem_bram.v" <<'V'
module mem_bram(input clk, input we,
                input [7:0] waddr, input [31:0] wdata,
                input [7:0] raddr, output reg [31:0] rdata);
  reg [31:0] m [0:255];
  integer i;
  initial for (i = 0; i < 256; i = i + 1) m[i] = 0;
  always @(posedge clk) begin
    if (we) m[waddr] <= wdata;
    rdata <= m[raddr];
  end
endmodule
V
cat > "$WORK/reg_64x32.v" <<'V'
module reg_64x32(input clk, input we,
                 input [5:0] waddr, input [31:0] wdata,
                 input [5:0] raddr, output [31:0] rdata);
  reg [31:0] m [0:63];
  integer i;
  initial for (i = 0; i < 64; i = i + 1) m[i] = 0;
  always @(posedge clk) if (we) m[waddr] <= wdata;
  assign rdata = m[raddr];
endmodule
V
cat > "$WORK/reg_32x192.v" <<'V'
module reg_32x192(input clk, input we,
                  input [4:0] waddr, input [191:0] wdata,
                  input [4:0] raddr, output [191:0] rdata);
  reg [191:0] m [0:31];
  integer i;
  initial for (i = 0; i < 32; i = i + 1) m[i] = 0;
  always @(posedge clk) if (we) m[waddr] <= wdata;
  assign rdata = m[raddr];
endmodule
V

for t in mem_reg mem_bram reg_64x32 reg_32x192; do
  synth "$t" ""
done

# ------------------------------------------------------------------
# UART writer: current source, built as its own top.
# ------------------------------------------------------------------
mkdir -p "$WORK/src" "$WORK/uart"
cp "$ROOT/bsv/HobbitTypes.bsv" "$ROOT/bsv/HobbitUart.bsv" "$WORK/src/"
cat > "$WORK/src/UartOnly.bsv" <<'BSV'
package UartOnly;
import HobbitTypes::*;
import HobbitUart::*;
(* synthesize *)
module mkAreaUart(HriWriter);
  HriWriter w <- mkHriWriter(217);
  return w;
endmodule
endpackage
BSV
"$BSC" +RTS -K512M -RTS -verilog -g mkAreaUart -u \
  -vdir "$WORK/uart" -bdir "$WORK/uart" -info-dir "$WORK/uart" \
  -p "$WORK/src:$BLUESPECDIR/Libraries" "$WORK/src/UartOnly.bsv" \
  >"$WORK/uart.log" 2>&1 || { cat "$WORK/uart.log"; exit 1; }
cp "$WORK/uart/mkAreaUart.v" "$WORK/mkAreaUart.v"
for variant in "" "share -aggressive;" "share -aggressive; share -aggressive;" \
               "share -aggressive; opt -full;"; do
  synth mkAreaUart "$variant"
done
# abc2 and noabc9 are synth_ecp5 options, not pre-passes.
for opt in -abc2 -noabc9; do
  "$YOSYS" -p "read_verilog $WORK/mkAreaUart.v; synth_ecp5 $opt -top mkAreaUart -json $WORK/u$opt.json" \
    -l "$WORK/u$opt.log" >/dev/null 2>&1 || { echo "   synth_ecp5 $opt failed"; continue; }
  awk -v opt="$opt" '
    /Number of cells:/ { inb=1; next }
    inb && /^[[:space:]]*$/ { inb=0 }
    inb { if ($1 ~ /^(LUT4|PFUMX|TRELLIS_FF|CCU2C|DP16KD)$/) v[$1]=$2; }
    END { printf "%-22s %-18s %6d %6d %6d %6d %4d\n", "mkAreaUart", "synth_ecp5 " opt,
          v["LUT4"], v["PFUMX"], v["TRELLIS_FF"], v["CCU2C"], v["DP16KD"]; }' \
    "$WORK/u$opt.log"
done

echo
echo "The reader should compare each reference with the block it replaces:"
echo "  mem_reg   -- 256x32 FF array, one write port (the board has 3 writers)"
echo "  mem_bram  -- 256x32 block RAM, one write port"
echo "  reg_64x32 -- 64x32 register file with a 64:1 read mux"
echo "  reg_32x192-- 32x192 register file with a 32:1 read mux"
echo "Separately synthesised blocks do not add to the flat design; see"
echo "docs/area_analysis.md for the reconciliation."
