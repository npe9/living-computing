#!/bin/sh
# run_program.sh -- assemble a STRAP program and run it on the mkStretchCore
# Bluespec model in one step: strap_asm.py -> gen_tb.py -> bsc -> Bluesim.
#
# Usage:
#   ./run_program.sh programs/problem_2_1.strap StretchProblem21Tb \
#       "DOG_rotated:32=0x91a2b3c4d5e6f780"
#
# Each trailing argument is a check: LABEL:WORD_ADDR_EXPR=EXPECTED_HEX_OR_DEC
# (see gen_tb.py). The generated .bsv is written into ../bsv/ (a sibling of
# this directory) alongside the hand-written model, compiled with the same
# pinned Homebrew toolchain as bsv/build.sh (see bsv/README.md "Toolchain"),
# and run.

set -e
STRAP_DIR="$(cd "$(dirname "$0")" && pwd)"
BSV_DIR="$STRAP_DIR/../bsv"

if [ $# -lt 2 ]; then
  echo "usage: $0 program.strap ModuleName [LABEL:ADDR=EXPECTED ...]" >&2
  exit 1
fi

PROGRAM="$1"; MODULE="$2"; shift 2

export BLUESPECDIR=/opt/homebrew/Cellar/bsc/2026.01/libexec/lib
export PATH=/opt/homebrew/Cellar/bsc/2026.01/bin:$PATH
BSC=/opt/homebrew/Cellar/bsc/2026.01/bin/bsc

python3 "$STRAP_DIR/gen_tb.py" "$PROGRAM" "$MODULE" "$@" > "$BSV_DIR/$MODULE.bsv"

cd "$BSV_DIR"
mkdir -p build simbuild
"$BSC" -sim -simdir simbuild -bdir build -info-dir build -g "mk$MODULE" -u "$MODULE.bsv" +RTS -K512m -RTS
"$BSC" -sim -simdir simbuild -bdir build -e "mk$MODULE" -o "${MODULE}_sim" +RTS -K512m -RTS
"./${MODULE}_sim"
