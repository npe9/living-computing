#!/bin/sh
# run_loader_deck.sh -- MCP's JOB CONTROL BINARY LOADER (printed
# pp.320-334) loads a deck STRAP II punched.  See gen_loader_deck_tb.py.
set -e
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHONPATH="$TESTS_DIR/../strap:$TESTS_DIR"; export PYTHONPATH
BSV_DIR="$TESTS_DIR/../bsv"
MODULE="${1:-StretchLoaderDeckTb}"
shift 2>/dev/null || true
export BLUESPECDIR=/opt/homebrew/Cellar/bsc/2026.01/libexec/lib
export PATH=/opt/homebrew/Cellar/bsc/2026.01/bin:$PATH
BSC=/opt/homebrew/Cellar/bsc/2026.01/bin/bsc
cd "$TESTS_DIR"
mkdir -p "$BSV_DIR/build-loader" "$BSV_DIR/simbuild-loader"
python3 gen_loader_deck_tb.py "$MODULE" "$@" > "$BSV_DIR/$MODULE.bsv"
cd "$BSV_DIR"
"$BSC" -sim -simdir simbuild-loader -bdir build-loader -info-dir build-loader \
       -g "mk$MODULE" -u "$MODULE.bsv" +RTS -K512m -RTS
"$BSC" -sim -simdir simbuild-loader -bdir build-loader -e "mk$MODULE" -o "${MODULE}_sim" \
       +RTS -K512m -RTS
"./${MODULE}_sim"
