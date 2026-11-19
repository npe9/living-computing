#!/bin/sh
# gen_verilog.sh -- build the two Verilog snapshots used by the formal
# smoke check, from the current BSV tree in pim/bsv.
#
#   build/fixed/mkPimPUFormal.v   current tree
#   build/buggy/mkPimPUFormal.v   same tree with the E-stage fetched-operand
#                           regression reintroduced (see patch below)
#
# The formal wrapper (pim_smoke_formal.v) needs a small amount of
# environment adaptation on the generated Verilog; that is also done
# here, and nothing in the BSV tree is modified:
#
#   * RegFileLoad arrays are capped to the addresses this diagnostic
#     touches.  A full 64K x 40 program image makes write_smt2 emit one
#     array-init constraint per address (~100k constraints), which the
#     solvers cannot discharge inside a useful time; the program uses
#     PC 0..12, data address 100, WCS 0..14, decode opcodes 0..14, and
#     never reads the jump table.
#   * The local-store write port is gated with RST_N.  RegFileLoad has
#     no reset, so the arbitrary initial state of the PU could commit a
#     spurious write on the first clock edge before the reset takes
#     effect.  In the BSV the run rule is off during reset, so gating
#     the port restores the invariant without changing post-reset
#     behaviour.
#
# Use BSC_BIN to pin a compiler; otherwise take the newest Homebrew
# bsc, as run_smoke.sh does.

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

SRC=..

build_variant () {
  variant=$1
  dir="build/$variant"
  rm -rf "$dir"
  mkdir -p "$dir"
  for f in PimTypes PimStages PimALU PimE PimPU PimPUFormal; do
    cp "$SRC/$f.bsv" "$dir/"
  done

  if [ "$variant" = buggy ]; then
    # PimE used to read a stale fetched operand in rselFetch (the
    # PimE.bsv:131 regression).  The rewritten E stage cannot express
    # that exact mistake because the R stage now attaches the fetched
    # word to the instruction it belongs to; reintroduce the same
    # defect by dropping the fetched operand when E loads.
    python3 - "$dir/PimE.bsv" <<'PY'
import sys
p = sys.argv[1]
s = open(p).read()
assert "fromMaybe(wordInt(0), eFetched)" in s, "rselFetch shape changed"
old = "          eFetched <= x.fetched;"
new = "          eFetched <= Invalid;  // REGRESSION: drop the R-stage fetch"
assert s.count(old) == 1, old
open(p, "w").write(s.replace(old, new))
PY
  fi

  ( cd "$dir" && "$BSC" -verilog -g mkPimPUFormal \
        -p ".:$BLUESPECDIR/Libraries" -u PimPUFormal.bsv ) >/dev/null

  # Formal-only adaptation of the generated netlist.  Assert every
  # rewrite so a bsc output change cannot silently skip one.
  python3 - "$dir/mkPimPUFormal.v" <<'PY'
import sys
p = sys.argv[1]
s = open(p).read()
subs = [
    (".WE(store_mem$WE)", ".WE(store_mem$WE & RST_N)"),
    (".hi(16'd65535)", ".hi(16'd127)"),   # local store 128 words
    (".hi(15'd32767)", ".hi(15'd15)"),    # WCS 16 microinstructions
    (".hi(8'd255)",    ".hi(8'd15)"),     # decode and jump tables 16
]
for old, new in subs:
    assert old in s, f"generated Verilog changed: {old!r} not found"
    s = s.replace(old, new)
open(p, "w").write(s)
PY
}

build_variant fixed
build_variant buggy

# Images for the capped memories.  Assemble from a private directory so
# the check does not depend on whatever the smoke test last left in
# bsv/generated (and does not write there).  The assembler output is one
# word per line; keep exactly the range the capped RegFileLoad instances
# read.
mkdir -p build/images formal_images
python3 "$SRC/../asm/pimasm.py" --out-dir build/images >/dev/null
head -128 build/images/program.hex > formal_images/program.hex
for n in wcs decode jump; do
  head -16 "build/images/$n.hex" > formal_images/$n.hex
done

echo "built build/fixed/mkPimPUFormal.v and build/buggy/mkPimPUFormal.v"
