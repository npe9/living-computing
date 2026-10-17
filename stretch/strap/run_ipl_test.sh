#!/bin/sh
# run_ipl_test.sh -- boot the model from a tape image (boot_plan.md M1).
# Mirrors run_tape_test.sh exactly; the only difference is the
# generator, which emits a testbench that pre-loads NOTHING into core
# storage and calls core.iplStart() instead of core.setPC().
set -e
STRAP_DIR="$(cd "$(dirname "$0")" && pwd)"
BSV_DIR="$STRAP_DIR/../bsv"
MODULE="${1:-StretchIplTb}"
export BLUESPECDIR=/opt/homebrew/Cellar/bsc/2026.01/libexec/lib
export PATH=/opt/homebrew/Cellar/bsc/2026.01/bin:$PATH
BSC=/opt/homebrew/Cellar/bsc/2026.01/bin/bsc
cd "$STRAP_DIR"
python3 gen_ipl_tb.py "$MODULE" > "$BSV_DIR/$MODULE.bsv"
cd "$BSV_DIR"
mkdir -p build simbuild
"$BSC" -sim -simdir simbuild -bdir build -info-dir build -show-schedule -g "mk$MODULE" -u "$MODULE.bsv" +RTS -K512m -RTS
"$BSC" -sim -simdir simbuild -bdir build -e "mk$MODULE" -o "${MODULE}_sim" +RTS -K512m -RTS
"./${MODULE}_sim"
