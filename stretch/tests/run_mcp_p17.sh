#!/bin/sh
# run_mcp_p17.sh -- the REAL transcribed printed p.17 against a
# synthetic IOCD card.  See gen_mcp_p17_tb.py's header for what is
# derived and what is invented.
set -e
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHONPATH="$TESTS_DIR/../strap:$TESTS_DIR"; export PYTHONPATH
BSV_DIR="$TESTS_DIR/../bsv"
MODULE="${1:-StretchMcpP17Tb}"
export BLUESPECDIR=/opt/homebrew/Cellar/bsc/2026.01/libexec/lib
export PATH=/opt/homebrew/Cellar/bsc/2026.01/bin:$PATH
BSC=/opt/homebrew/Cellar/bsc/2026.01/bin/bsc
cd "$TESTS_DIR"
python3 gen_mcp_p17_tb.py "$MODULE" $2 > "$BSV_DIR/$MODULE.bsv"
cd "$BSV_DIR"
mkdir -p build simbuild
"$BSC" -sim -simdir simbuild -bdir build -info-dir build -show-schedule \
       -g "mk$MODULE" -u "$MODULE.bsv" +RTS -K512m -RTS
"$BSC" -sim -simdir simbuild -bdir build -e "mk$MODULE" -o "${MODULE}_sim" \
       +RTS -K512m -RTS
"./${MODULE}_sim"
