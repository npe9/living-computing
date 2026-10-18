#!/bin/sh
# run_disk_test.sh -- assemble and run ../decks/io_disk.strap via
# gen_disk_tb.py (which patches in control-word values gen_tb.py's plain
# CLI can't -- see that script's own header) instead of gen_tb.py
# directly. Mirrors run_io_test.sh's bsc/Bluesim invocation exactly.
#
# Usage: ./run_disk_test.sh [ModuleName]   (default: StretchIoDiskTb)

set -e
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
# The assembler lives in ../strap now; the verifiers and
# generators import it by module name.
PYTHONPATH="$TESTS_DIR/../strap:$TESTS_DIR"; export PYTHONPATH
BSV_DIR="$TESTS_DIR/../bsv"
MODULE="${1:-StretchIoDiskTb}"

export BLUESPECDIR=/opt/homebrew/Cellar/bsc/2026.01/libexec/lib
export PATH=/opt/homebrew/Cellar/bsc/2026.01/bin:$PATH
BSC=/opt/homebrew/Cellar/bsc/2026.01/bin/bsc

cd "$TESTS_DIR"
python3 gen_disk_tb.py "$MODULE" > "$BSV_DIR/$MODULE.bsv"

cd "$BSV_DIR"
mkdir -p build simbuild
"$BSC" -sim -simdir simbuild -bdir build -info-dir build -show-schedule -g "mk$MODULE" -u "$MODULE.bsv" +RTS -K512m -RTS
"$BSC" -sim -simdir simbuild -bdir build -e "mk$MODULE" -o "${MODULE}_sim" +RTS -K512m -RTS
"./${MODULE}_sim"
