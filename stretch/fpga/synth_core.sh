#!/bin/sh
# synth_core.sh -- yosys area measurement of a synthesis boundary of the
# model for the ECP5 (ULX3S), by the method of docs/fpga_feasibility.md
# §9.2.  RECONSTRUCTED 2026-11-24: §9.2 names `out_pnr/synth_core.sh`, which
# was never committed and is not on this machine (fidelity_plan.md F0).
# This script follows §9.2's four recorded changes to stock synth_ecp5:
#   (a) `stat` after map_ffs, before LUT mapping, so DP16KD, MULT18X18D and
#       TRELLIS_FF are banked even if LUT mapping never ends;
#   (b) the coarse stage pasted from `help synth_ecp5` (yosys 0.51) with
#       `share` removed;
#   (c) -noabc9 (stock abc): its LUT4 figure is a PESSIMISTIC upper bound,
#       up to ~2.5x (§9.6.1), and must not be used to exclude a device;
#   (d) write_rtlil checkpoints after coarse and after map_ffs.
# BRAM1.v and the other bsc library modules are read as real Verilog
# (hierarchy -libdir), not blackboxed, so DP16KD is a mapping result.
#
# Usage: fpga/synth_core.sh OUTDIR [TOP] [flat|hier]
#   TOP   default mkStretchCore (any (* synthesize *) module in bsv/)
#   flat  flatten in coarse, as §9.2 did (comparable with §9.3)
#   hier  keep bsc's module boundaries: `stat` then reports every
#         synthesized module separately (F0's per-module LUT4; F1's
#         per-box delta).  Default hier.
# Outputs in OUTDIR: vdir/ (bsc Verilog), logs/synth.ys, logs/synth.log,
# coarse.il, ffs.il, and the two stat blocks in the log ("STAT-FFS",
# "STAT-FINAL").  Run when no suite is running: the whole core took ~3 h
# at full load (2026-10-16).
set -eu
OUT=${1:?usage: synth_core.sh OUTDIR [TOP] [flat|hier]}
TOP=${2:-mkStretchCore}
MODE=${3:-hier}
HERE=$(cd "$(dirname "$0")/.." && pwd)
# The bsc bsv/build.sh uses (the ~/.cabal one rejects +RTS -K512m).
BSC=${BSC:-/opt/homebrew/Cellar/bsc/2026.01/bin/bsc}
BLUESPECDIR=${BLUESPECDIR:-/opt/homebrew/Cellar/bsc/2026.01/libexec/lib}
export BLUESPECDIR
mkdir -p "$OUT/vdir" "$OUT/vbuild" "$OUT/vinfo" "$OUT/logs"
OUT=$(cd "$OUT" && pwd)

# The .bsv file that declares TOP.
SRC=$(grep -l "module $TOP\b" "$HERE"/bsv/*.bsv | grep -v 'Tb\.bsv$' | head -1)
[ -n "$SRC" ] || { echo "no bsv file declares $TOP" >&2; exit 1; }
( cd "$HERE/bsv" && "$BSC" -verilog -vdir "$OUT/vdir" -bdir "$OUT/vbuild" \
    -info-dir "$OUT/vinfo" -p "$OUT/vbuild:%/Libraries:." \
    -g "$TOP" -u "$(basename "$SRC")" +RTS -K512m -RTS ) > "$OUT/logs/bsc.log" 2>&1

FLAT=""; [ "$MODE" = flat ] && FLAT=flatten
YS="$OUT/logs/synth.ys"
{
  for v in "$OUT"/vdir/*.v; do echo "read_verilog -defer $v"; done
  echo "read_verilog -lib -specify +/ecp5/cells_sim.v +/ecp5/cells_bb.v"
  echo "hierarchy -check -top $TOP -libdir $BLUESPECDIR/Verilog"
  cat <<YS
# coarse, from \`help synth_ecp5\` (yosys 0.51), \`share\` removed (§9.2 b)
proc
$FLAT
tribuf -logic
deminout
opt_expr
opt_clean
check
opt -nodffe -nosdff
fsm
opt
wreduce
peepopt
opt_clean
techmap -map +/cmp2lut.v -D LUT_WIDTH=4
opt_expr
opt_clean
techmap -map +/mul2dsp.v -map +/ecp5/dsp_map.v -D DSP_A_MAXWIDTH=18 -D DSP_B_MAXWIDTH=18 -D DSP_A_MINWIDTH=2 -D DSP_B_MINWIDTH=2 -D DSP_NAME=\$__MUL18X18
chtype -set \$mul t:\$__soft_mul
alumacc
opt
memory -nomap
opt_clean
write_rtlil $OUT/coarse.il
synth_ecp5 -noabc9 -top $TOP -run map_ram:map_luts
write_rtlil $OUT/ffs.il
tee -o $OUT/logs/stat_ffs.txt stat
synth_ecp5 -noabc9 -top $TOP -run map_luts:
tee -o $OUT/logs/stat_final.txt stat
YS
} > "$YS"
yosys -l "$OUT/logs/synth.log" -q -s "$YS"
echo "done: $OUT/logs/stat_ffs.txt $OUT/logs/stat_final.txt"
