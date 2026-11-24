#!/bin/sh
# Run a hand-derived golden trace through the Bluesim core.
#
#   ./run_golden.sh NNN     NNN is 001..006 or 013..016
#   ./run_golden.sh         run all six in order
#
# The image is tests/golden/NNN.hex.  The generated image package and the
# per-stem testbench are written here and are gitignored.  Standard output
# is exactly the core's output: HRI lines, plus a TRAP line if the model
# traps.  HRI is the Hobbit Retirement Interface, the Hobbit analogue of
# riscv-formal's RVFI; the check is retire-trace comparison against the
# hand-derived trace, not a yosys formal proof.  This script exits 0
# whether or not the trace matches; the caller's differ decides.
set -eu
cd "$(dirname "$0")"

BSC=${BSC_BIN:-}
if [ -z "$BSC" ]; then
  BSC=$(ls -d /opt/homebrew/Cellar/bsc/*/bin/bsc 2>/dev/null | sort | tail -1)
fi
if [ -z "$BSC" ] || [ ! -x "$BSC" ]; then
  echo "bsc not found; set BSC_BIN to the 2026.01 bsc binary" >&2
  exit 1
fi

BLUESPECDIR=$(cd "$(dirname "$BSC")/../libexec/lib" && pwd)
export BLUESPECDIR
PATH=$(dirname "$BSC"):$PATH
export PATH

GEN=generated
mkdir -p "$GEN"

run_one() {
  stem=$1
  case "$stem" in
    001|002|003|004|005|006|009|013|014|015|016|017|018|019|020|021|022|023) ;;
    *) echo "run_golden: no such golden stem: $stem" >&2
       echo "usage: run_golden.sh [001..006]" >&2
       exit 2 ;;
  esac

  img=../tests/golden/$stem.hex
  if [ ! -f "$img" ]; then
    echo "run_golden: missing $img" >&2
    exit 1
  fi

  # The pre-state is the README's for every golden except 017, which runs
  # with PSW.UL set at user level (little-endian data, PRM p. 1-3):
  # PSW 0x8600 = UL | X | S, as 017.md's "Pre-state" says.
  case "$stem" in
    017) startcall='core.startPsw(32'"'"'h00000100, 32'"'"'h00000180, 32'"'"'h00008600);' ;;
    023) startcall='core.startPsw(32'"'"'h00000100, 32'"'"'h00000180, 32'"'"'h00010200);' ;;
    *)   startcall='core.start(32'"'"'h00000100, 32'"'"'h00000180);' ;;
  esac
  # 023 runs on the MMU core with PSW.V = 1 (023.md "Pre-state"): segment
  # 0 paged with its table at 0x1000 (Table 2-1, p. 2-5), page 0 mapped
  # to frame 0 and every other page invalid (Table 2-3, p. 2-7) -- the
  # tables of HobbitCoreMmuTb.bsv.  Its architectural trace is the same
  # as with V = 0, because no instruction it retires touches page 1 up.
  case "$stem" in
    023)
      coredecl='MmuTables tbl <- mkMmuTableMem;
  HobbitCore core <- mkHobbitCoreMmu(phys, imageLength() << 2,
                                     defaultMemCycles(), tbl);'
      tblrules='Reg#(Bit#(2)) tl <- mkReg(0);
  rule loadTables (tl != 2);
    if (tl == 0) tbl.write(32'"'"'h0000, 32'"'"'h00001001);
    else         tbl.write(32'"'"'h1000, 32'"'"'h00000807);
    tl <= tl + 1;
  endrule'
      tblready='(tl == 2) && ' ;;
    *)
      coredecl='HobbitCore core <- mkHobbitCore(phys, imageLength() << 2,
                                  defaultMemCycles());'
      tblrules=''
      tblready='' ;;
  esac

  pkg=GoldenImage_$stem
  tb=GoldenTb_$stem
  python3 mk_image_bsv.py "$img" "$pkg" > "$pkg.bsv"

  cat > "$tb.bsv" <<EOF
package $tb;

import HobbitTypes::*;
import HobbitMmu::*;
import HobbitCore::*;
import HobbitBus::*;
import $pkg::*;

(* synthesize *)
module mkGoldenTb_$stem(Empty);
  HobbitBusMem mem <- mkHobbitBusMem;
  HobbitMem phys <- mkHobbitMemBus(mem);
  $coredecl

  Reg#(Bit#(16)) li <- mkReg(0);
  Reg#(Bool) loaded <- mkReg(False);
  Reg#(Bool) started <- mkReg(False);
  Reg#(Bool) finished <- mkReg(False);
  Reg#(Bit#(32)) cycles <- mkReg(0);

  rule load (!loaded);
    if (zeroExtend(li) < imageLength()) begin
      phys.write(zeroExtend(li) << 2, imageWord(li));
      li <= li + 1;
    end else
      loaded <= True;
  endrule

  // Warm the prefetch buffer from the synchronous read port (p. 4-1
  // instruction-cache assumption), then start the measured run.
  Reg#(Bit#(2)) boot <- mkReg(0);
  $tblrules
  rule askPrefetch (${tblready}loaded && (boot == 0));
    core.prefetchImage();
    boot <= 1;
  endrule
  rule start ((boot == 1) && core.prefetchReady());
    $startcall
    started <= True;
    boot <= 2;
  endrule

  // Stop after the trap retirement, otherwise when the next PC reaches
  // the image length.  The timeout is a guard against a model bug, not a
  // trace rule.
  rule count (started && !finished);
    cycles <= cycles + 1;
    if ((core.halted() || core.atLimit()) && core.quiescent())
      finished <= True;
    else if (cycles > 32'd200000)
      finished <= True;
  endrule

  rule done (finished);
    \$finish;
  endrule
endmodule

endpackage
EOF

  log="$GEN/build_$stem.log"
  "$BSC" +RTS -K512M -RTS -sim -g mkGoldenTb_$stem -u "$tb.bsv" >"$log" 2>&1
  "$BSC" +RTS -K512M -RTS -sim -e mkGoldenTb_$stem -o "sim_golden_$stem" >>"$log" 2>&1

  out=$(./sim_golden_"$stem")
  printf '%s\n' "$out"
  self_check "$stem" "$out"
}

# Two adjudicated facts, checked as diagnostics (stderr only; the script
# still exits 0 and the caller's differ is the verdict):
#   003  RETURN at 0x0006 reads *(CSP+16) and sets SP 0xf0 -> 0x100,
#        next PC 0x000e (p. 3-40, p. 3-9).
#   004  ENTER $0xc0 empties the cache, SP 0x100 -> 0xc0 and
#        MSP 0x180 -> 0xc0 (pp. 3-19/3-20).
self_check() {
  stem=$1
  out=$2
  case "$stem" in
    003)
      if ! printf '%s\n' "$out" |
           grep -q '^HRI pc=0006 .*sp=000000f0>00000100 '; then
        echo "run_golden: 003 assertion failed: RETURN at 0x0006 must report sp 0xf0>0x100 (p. 3-40)" >&2
      fi
      if ! printf '%s\n' "$out" | grep -q '^HRI pc=000e '; then
        echo "run_golden: 003 assertion failed: RETURN at 0x0006 must reach PC 0x000e (p. 3-9)" >&2
      fi
      ;;
    004)
      if ! printf '%s\n' "$out" |
           grep -q '^HRI pc=0006 .*sp=00000100>000000c0 msp=00000180>000000c0 '; then
        echo "run_golden: 004 assertion failed: ENTER \$0xc0 must report sp 0x100>0xc0 and msp 0x180>0xc0 (pp. 3-19/3-20)" >&2
      fi
      ;;
  esac
}

if [ $# -eq 0 ]; then
  for s in 001 002 003 004 005 006 013 014 015 016; do
    run_one "$s"
  done
else
  run_one "$1"
fi
