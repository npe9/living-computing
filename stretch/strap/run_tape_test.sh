#!/bin/sh
# run_tape_test.sh -- assemble and run programs/io_tape.strap via
# gen_tape_tb.py (which patches in control-word values gen_tb.py's plain
# CLI can't -- see that script's own header) instead of gen_tb.py
# directly. Mirrors run_io_test.sh's bsc/Bluesim invocation exactly.
#
# Usage: ./run_tape_test.sh [ModuleName]   (default: StretchIoTapeTb)

set -e
STRAP_DIR="$(cd "$(dirname "$0")" && pwd)"
BSV_DIR="$STRAP_DIR/../bsv"
MODULE="${1:-StretchIoTapeTb}"

export BLUESPECDIR=/opt/homebrew/Cellar/bsc/2026.01/libexec/lib
export PATH=/opt/homebrew/Cellar/bsc/2026.01/bin:$PATH
BSC=/opt/homebrew/Cellar/bsc/2026.01/bin/bsc

cd "$STRAP_DIR"
python3 gen_tape_tb.py "$MODULE" > "$BSV_DIR/$MODULE.bsv"

cd "$BSV_DIR"
mkdir -p build simbuild
"$BSC" -sim -simdir simbuild -bdir build -info-dir build -g "mk$MODULE" -u "$MODULE.bsv" +RTS -K512m -RTS
"$BSC" -sim -simdir simbuild -bdir build -e "mk$MODULE" -o "${MODULE}_sim" +RTS -K512m -RTS
"./${MODULE}_sim"
