#!/bin/sh
# run_add_family.sh -- the 128-cell ADD-family truth table of R23-9694
# printed p.107, run on the model.  See gen_add_family_tb.py's header
# for the page and for what is and is not checked.
#
# This has its own runner rather than a run_program.sh line because
# the checks are generated from a transcribed table, not written out:
# 128 of them would be unreadable on a command line, and a table is
# the right place for a table.
set -e
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHONPATH="$TESTS_DIR/../strap:$TESTS_DIR"; export PYTHONPATH
BSV_DIR="$TESTS_DIR/../bsv"
MODULE="${1:-StretchAddFamilyTb}"
export BLUESPECDIR=/opt/homebrew/Cellar/bsc/2026.01/libexec/lib
export PATH=/opt/homebrew/Cellar/bsc/2026.01/bin:$PATH
BSC=/opt/homebrew/Cellar/bsc/2026.01/bin/bsc

cd "$TESTS_DIR"
python3 gen_add_family_tb.py "$MODULE" > "$BSV_DIR/$MODULE.bsv"
cd "$BSV_DIR"
mkdir -p build simbuild
"$BSC" -sim -simdir simbuild -bdir build -info-dir build -show-schedule \
       -g "mk$MODULE" -u "$MODULE.bsv" +RTS -K512m -RTS
"$BSC" -sim -simdir simbuild -bdir build -e "mk$MODULE" -o "${MODULE}_sim" \
       +RTS -K512m -RTS
"./${MODULE}_sim"
