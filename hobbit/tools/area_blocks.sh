#!/bin/sh
# area_blocks.sh -- synthesise each Hobbit block as its own ECP5 top.
#
# This is the block-level companion of tools/area_netlist.py (which
# attributes the flat board netlist).  Each block is instantiated with
# minimal stubs for its neighbours so the count is the block's own
# logic, then run through the same yosys `synth_ecp5` flow as
# fpga/build.sh.  Products go to a temporary directory; nothing is
# written into the repository.
#
# Usage:
#   tools/area_blocks.sh [--keep]
#
# Environment: BSC_BIN, YOSYS (defaults resolve the Homebrew installs
# used by fpga/build.sh).
#
# The stack cache is compiled separately because its current worktree
# source is being rewritten by another agent; if that compile fails the
# script reports it and keeps the other rows.  The current-build stack
# cache number comes from tools/area_netlist.py on the flat netlist.

set -eu

ROOT=$(cd "$(dirname "$0")/.." && pwd)
BSC=${BSC_BIN:-$(ls -d /opt/homebrew/Cellar/bsc/*/bin/bsc 2>/dev/null | sort | tail -1)}
if [ -z "$BSC" ] || [ ! -x "$BSC" ]; then
  echo "area_blocks: bsc not found; set BSC_BIN" >&2
  exit 1
fi
BLUESPECDIR=$(cd "$(dirname "$BSC")/../libexec/lib" && pwd)
export BLUESPECDIR
YOSYS=${YOSYS:-yosys}

KEEP=0
[ "${1:-}" = "--keep" ] && KEEP=1
WORK=$(mktemp -d "${TMPDIR:-/tmp}/hobbit_area_blocks.XXXXXX")
SRC=$WORK/src
OUT=$WORK/out
mkdir -p "$SRC" "$OUT"
trap '[ "$KEEP" = 1 ] || rm -rf "$WORK"; [ "$KEEP" = 1 ] && echo "products: $WORK"' EXIT

cp "$ROOT"/bsv/HobbitTypes.bsv "$ROOT"/bsv/HobbitDecode.bsv \
   "$ROOT"/bsv/HobbitUart.bsv "$ROOT"/bsv/HobbitStackCache.bsv "$SRC"/

cat > "$SRC/AreaBlocks.bsv" <<'BSV'
package AreaBlocks;

import Vector::*;
import HobbitTypes::*;
import HobbitDecode::*;
import HobbitUart::*;

// Minimal neighbours.  They are deliberately not models: their job is
// to keep the block under test from being constant-folded away.
(* synthesize *)
module mkAreaStubMem(HobbitMem);
  Reg#(Word) d <- mkReg(0);
  method Action readReq(Word a) = noAction;
  method Word readData() = d;
  method Action write(Word a, Word v);
    d <= v ^ a;
  endmethod
  method Word peek(Word a) = d;
endmodule

module mkAreaStubPf(HobbitPrefetch);
  Reg#(Bit#(64)) d <- mkReg(0);
  rule tick; d <= d + 1; endrule
  method Action startFill() = noAction;
  method Bool filling() = False;
  method Bool ready() = True;
  method Maybe#(Bit#(64)) lineAt(Word a) = tagged Valid (d ^ zeroExtend(a));
endmodule

module mkAreaStubPdu(HobbitPdu);
  Reg#(Word) pcR <- mkReg(0);
  Reg#(DecEntry) eR <- mkReg(0);
  rule tick; eR <= eR + 1; endrule
  method Action enq(Word p);
    pcR <= p;
  endmethod
  method Bool accepting() = True;
  method Bool outValid() = True;
  method PduS3Out out() = PduS3Out { pc: pcR, miss: False, entry: eR };
  method Action deq() = noAction;
endmodule

(* synthesize *)
module mkAreaStubPfTop(HobbitPrefetch);
  HobbitPrefetch p <- mkAreaStubPf;
  return p;
endmodule

(* synthesize *)
module mkAreaStubPduTop(HobbitPdu);
  HobbitPdu p <- mkAreaStubPdu;
  return p;
endmodule

// ---- the blocks ------------------------------------------------------
(* synthesize *)
module mkAreaMem(HobbitMem);
  HobbitMem m <- mkHobbitMem;
  return m;
endmodule

(* synthesize *)
module mkAreaDecode(HobbitDecode);
  HobbitDecode d <- mkHobbitDecode;
  return d;
endmodule

(* synthesize *)
module mkAreaPf(HobbitPrefetch);
  HobbitMem m <- mkAreaStubMem;
  HobbitPrefetch p <- mkHobbitPrefetch(m);
  return p;
endmodule

(* synthesize *)
module mkAreaPdu(HobbitPdu);
  HobbitPrefetch p <- mkAreaStubPf;
  HobbitPdu d <- mkHobbitPdu(p);
  return d;
endmodule

(* synthesize *)
module mkAreaIc(HobbitDecodeStore);
  HobbitPdu p <- mkAreaStubPdu;
  HobbitDecodeStore i <- mkHobbitDecodeStore(p);
  return i;
endmodule

(* synthesize *)
module mkAreaUart(HriWriter);
  HriWriter w <- mkHriWriter(217);
  return w;
endmodule

endpackage
BSV

cat > "$SRC/AreaSc.bsv" <<'BSV'
package AreaSc;
import HobbitTypes::*;
import AreaBlocks::*;
import HobbitStackCache::*;
(* synthesize *)
module mkAreaSc(HobbitStackCache);
  HobbitMem m <- mkAreaStubMem;
  HobbitStackCache s <- mkHobbitStackCache(m, defaultMemCycles());
  return s;
endmodule
endpackage
BSV

echo "== bsc: stable block tops =="
"$BSC" +RTS -K512M -RTS -verilog -g mkAreaUart -u \
  -vdir "$OUT" -bdir "$OUT" -info-dir "$OUT" \
  -p "$SRC:$BLUESPECDIR/Libraries" "$SRC/AreaBlocks.bsv" 2>"$WORK/bsc.log" || {
    cat "$WORK/bsc.log"; exit 1; }

echo "== bsc: stack cache (may be mid-rewrite) =="
if "$BSC" +RTS -K512M -RTS -verilog -g mkAreaSc -u \
     -vdir "$OUT" -bdir "$OUT" -info-dir "$OUT" \
     -p "$SRC:$BLUESPECDIR/Libraries" "$SRC/AreaSc.bsv" \
     >"$WORK/sc.log" 2>&1; then
  SC_OK=1
else
  SC_OK=0
  echo "   stack cache not measurable from this source snapshot:"
  tail -3 "$WORK/sc.log" | sed 's/^/   /'
fi

synth() {
  top=$1
  [ -f "$OUT/$top.v" ] || { echo "   missing $top.v" >&2; return; }
  libreads=""
  for m in $(sed -n 's/^  \([A-Z][A-Za-z0-9_]*\)[ #(].*/\1/p' "$OUT/$top.v" | sort -u); do
    [ -f "$BLUESPECDIR/Verilog/$m.v" ] && libreads="$libreads read_verilog $BLUESPECDIR/Verilog/$m.v;"
  done
  stubreads=""
  for s in mkAreaStubMem mkAreaStubPf mkAreaStubPdu; do
    if [ "$s" != "$top" ] && [ -f "$OUT/$s.v" ]; then
      stubreads="$stubreads read_verilog $OUT/$s.v;"
    fi
  done
  "$YOSYS" -p "read_verilog $OUT/$top.v; $stubreads $libreads synth_ecp5 -top $top -json $OUT/$top.json" \
    -l "$OUT/$top.log" >/dev/null 2>&1 || {
      echo "   yosys failed for $top (see $OUT/$top.log)" >&2; return; }
  awk -v top="$top" '
    /Number of cells:/ { inb=1; next }
    inb && /^[[:space:]]*$/ { inb=0 }
    inb {
      if ($1 ~ /^(LUT4|PFUMX|TRELLIS_FF|CCU2C|DP16KD)$/) v[$1]=$2;
    }
    END {
      printf "%-12s %7d %7d %7d %7d %6d\n", top,
        v["LUT4"], v["PFUMX"], v["TRELLIS_FF"], v["CCU2C"], v["DP16KD"];
    }' "$OUT/$top.log"
}

echo
printf "%-12s %7s %7s %7s %7s %6s\n" block LUT4 PFUMX FF CCU2C BRAM
printf -- "---------------------------------------------------\n"
for top in mkAreaMem mkAreaDecode mkAreaPf mkAreaPdu mkAreaIc mkAreaUart \
           mkAreaStubMem mkAreaStubPfTop mkAreaStubPduTop; do
  synth "$top"
done
if [ "$SC_OK" = 1 ]; then synth mkAreaSc; else
  printf "%-12s %7s %7s %7s %7s %6s\n" mkAreaSc 'n/m' 'n/m' 'n/m' 'n/m' 'n/m'
fi
echo
echo "n/m = source snapshot does not compile; use tools/area_netlist.py"
echo "      on fpga/build/ulx3s_top.json for the in-design stack-cache row."
if [ "$KEEP" = 1 ]; then echo "kept: $WORK"; fi
