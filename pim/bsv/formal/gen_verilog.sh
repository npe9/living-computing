#!/bin/sh
# gen_verilog.sh -- build the Verilog snapshots used by the formal
# checks, from the current BSV tree in pim/bsv.
#
#   build/fixed/mkPimPUFormal.v         current tree (smoke caps)
#   build/buggy/mkPimPUFormal.v         fetched-operand regression
#   build/multiway/mkPimPUFormal.v      current tree, 256-entry tag table
#                                       and 128-entry WCS for the
#                                       multi-way jump property
#   build/multiway_bug/mkPimPUFormal.v  7-bit tagType index regression
#   build/decode_bug/mkPimPUFormal.v    swallowed undefined-opcode error
#   build/fault_bug/mkPimPUFormal.v     badWrite arm removed from `fault`
#
# The formal wrappers need a small amount of environment adaptation on
# the generated Verilog; that is also done here, and nothing in the BSV
# tree is modified:
#
#   * RegFileLoad arrays are capped to the addresses the selected
#     diagnostic touches.  A full 64K x 40 program image makes
#     write_smt2 emit one array-init constraint per address (~100k
#     constraints), which the solvers cannot discharge inside a useful
#     time.  The smoke, decode-error and fault images fit in 128 store
#     words, a 16-entry WCS, 16 decode entries and a 16-entry (unread)
#     jump table.  The multiway image reads the full 256-entry jump
#     table and micro-PCs up to 0x6e, so that variant gets a 256-entry
#     jump table and a 128-entry WCS.
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

  case "$variant" in
    buggy)
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
      ;;
    multiway_bug)
      # The documented tag-jump-table defect: index the table with the
      # 7-bit tag type, silently dropping MRB.  The fixed tree indexes
      # with the full 8-bit tag.
      python3 - "$dir/PimE.bsv" <<'PY'
import sys
p = sys.argv[1]
s = open(p).read()
old = "jumpTable.sub(wordTag(av))"
new = "jumpTable.sub(zeroExtend(tagType(wordTag(av))))"
assert s.count(old) == 1, old
open(p, "w").write(s.replace(old, new))
PY
      ;;
    decode_bug)
      # Swallow the undefined-opcode fault instead of latching it.
      python3 - "$dir/PimE.bsv" <<'PY'
import sys
p = sys.argv[1]
s = open(p).read()
old = "          errorSeen <= True;"
new = "          errorSeen <= False;  // INJECTION: swallow the decode fault"
assert s.count(old) == 1, old
open(p, "w").write(s.replace(old, new))
PY
      ;;
    fault_bug)
      # Drop the badWrite() arm from the top-level fault rule; the
      # unwritable-register write is then silently discarded.
      python3 - "$dir/PimPU.bsv" <<'PY'
import sys
p = sys.argv[1]
s = open(p).read()
old = "(estage.errorReq() || regs.badWrite())"
new = "(estage.errorReq())"
assert s.count(old) == 1, old
open(p, "w").write(s.replace(old, new))
PY
      ;;
  esac

  ( cd "$dir" && "$BSC" -verilog -g mkPimPUFormal \
        -p ".:$BLUESPECDIR/Libraries" -u PimPUFormal.bsv ) >/dev/null

  # Formal-only adaptation of the generated netlist.  Assert every
  # rewrite so a bsc output change cannot silently skip one.  The caps
  # are per-variant: the multi-way test reads the full 256-entry jump
  # table and micro-PCs up to 0x6e; the other checks keep the tight
  # smoke caps.
  python3 - "$dir/mkPimPUFormal.v" "$variant" <<'PY'
import sys
p, variant = sys.argv[1], sys.argv[2]
s = open(p).read()

old = ".WE(store_mem$WE)"
assert old in s, "generated Verilog changed: store write port not found"
s = s.replace(old, ".WE(store_mem$WE & RST_N)")

def set_hi(s, inst, value, fresh):
    marker = f")) {inst}("
    idx = s.index(marker)
    j = s.rfind(".hi(", 0, idx)
    k = s.index(")", j)
    old = s[j:k+1]
    assert old == f".hi({fresh})", (inst, old, fresh)
    return s[:j] + f".hi({value})" + s[k+1:]

s = set_hi(s, "store_mem", "16'd127", "16'd65535")
s = set_hi(s, "pu_decTbl", "8'd15", "8'd255")
if variant in ("multiway", "multiway_bug"):
    s = set_hi(s, "pu_wcs", "15'd127", "15'd32767")
    s = set_hi(s, "pu_jumpTbl", "8'd255", "8'd255")
else:
    s = set_hi(s, "pu_wcs", "15'd15", "15'd32767")
    s = set_hi(s, "pu_jumpTbl", "8'd15", "8'd255")
open(p, "w").write(s)
PY
}

build_variant fixed
build_variant buggy
build_variant multiway
build_variant multiway_bug
build_variant decode_bug
build_variant fault_bug

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

# Images for the multi-way, decode-error and fault programs.  These are
# generated from the same assembler encodings (the script imports
# asm/pimasm.py) and have their own caps in the multiway netlist.
python3 gen_path_images.py formal_images

echo "built build/fixed build/buggy build/multiway build/multiway_bug build/decode_bug build/fault_bug"
