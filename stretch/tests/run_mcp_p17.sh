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
# THE MODULE NAME AND THE MODE MUST AGREE.  The generator rejects an
# unknown mode, but a TYPO'D one that happens to be empty would
# silently build the no-units test under the units module's name and
# PASS -- a green section testing the wrong thing, which is the one
# failure this suite cannot see.
case "${2:-}" in
  "")      expect="StretchMcpP17Tb" ;;
  units)   expect="StretchMcpP17UnitsTb" ;;
  units8)  expect="StretchMcpP17Units8Tb" ;;
  disk)    expect="StretchMcpP17DiskTb" ;;
  *) echo "run_mcp_p17.sh: unknown mode '$2'" >&2; exit 1 ;;
esac
if [ "$MODULE" != "$expect" ]; then
  echo "run_mcp_p17.sh: mode '${2:-<none>}' builds $expect, not $MODULE" >&2
  exit 1
fi
python3 gen_mcp_p17_tb.py "$MODULE" $2 > "$BSV_DIR/$MODULE.bsv"
cd "$BSV_DIR"
mkdir -p build simbuild
"$BSC" -sim -simdir simbuild -bdir build -info-dir build -show-schedule \
       -g "mk$MODULE" -u "$MODULE.bsv" +RTS -K512m -RTS
"$BSC" -sim -simdir simbuild -bdir build -e "mk$MODULE" -o "${MODULE}_sim" \
       +RTS -K512m -RTS
"./${MODULE}_sim"
