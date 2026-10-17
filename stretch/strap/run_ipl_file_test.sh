#!/bin/sh
# run_ipl_file_test.sh -- boot from a tape image in a host file
# (docs/boot_plan.md M0 step 1 + M1).
#
# TWO THINGS DIFFER FROM run_ipl_test.sh AND BOTH MATTER.
#
# -D HOST_TAPE makes StretchIO instantiate mkTapeSourceFile instead of
# mkTapeSourceVector, and bsv/host_tape.c is linked in to serve it.
#
# A SEPARATE -bdir.  The two builds differ only by a -D, and bsc's .bo
# files carry no record of that: a StretchIO.bo built without
# HOST_TAPE is silently wrong for a build with it, and the failure is
# a tape that reads zeros rather than a compile error.  build-hosttape
# keeps them apart.
set -e
STRAP_DIR="$(cd "$(dirname "$0")" && pwd)"
BSV_DIR="$STRAP_DIR/../bsv"
MODULE="${1:-StretchIplFileTb}"
export BLUESPECDIR=/opt/homebrew/Cellar/bsc/2026.01/libexec/lib
export PATH=/opt/homebrew/Cellar/bsc/2026.01/bin:$PATH
BSC=/opt/homebrew/Cellar/bsc/2026.01/bin/bsc
: "${STRETCH_TAPE:=/tmp/stretch_ipl_big.tape}"
export STRETCH_TAPE
cd "$STRAP_DIR"
python3 gen_ipl_file_tb.py "$MODULE" > "$BSV_DIR/$MODULE.bsv"
cd "$BSV_DIR"
mkdir -p build-hosttape simbuild-hosttape
"$BSC" -sim -D HOST_TAPE -simdir simbuild-hosttape -bdir build-hosttape \
       -info-dir build-hosttape -show-schedule -g "mk$MODULE" -u "$MODULE.bsv" \
       +RTS -K512m -RTS
"$BSC" -sim -D HOST_TAPE -simdir simbuild-hosttape -bdir build-hosttape \
       -e "mk$MODULE" -o "${MODULE}_sim" host_tape.c +RTS -K512m -RTS
"./${MODULE}_sim"
