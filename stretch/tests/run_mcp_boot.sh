#!/bin/sh
# run_mcp_boot.sh -- boot MCP'S OWN BOOTSTRAP on the model, from the
# merged image of all thirteen transcribed pages (docs/boot_plan.md
# M3, the step after the transcription).
#
# THIS IS A DIAGNOSTIC AND IT IS EXPECTED TO FAIL while the model is
# still missing what the bootstrap needs.  What it reports is WHERE
# it stops, which is the point: see gen_mcp_boot_tb.py's header.
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
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
# The assembler lives in ../strap now; the verifiers and
# generators import it by module name.
PYTHONPATH="$TESTS_DIR/../strap:$TESTS_DIR"; export PYTHONPATH
BSV_DIR="$TESTS_DIR/../bsv"
MODULE="${1:-StretchMcpBootTb}"
export BLUESPECDIR=/opt/homebrew/Cellar/bsc/2026.01/libexec/lib
export PATH=/opt/homebrew/Cellar/bsc/2026.01/bin:$PATH
BSC=/opt/homebrew/Cellar/bsc/2026.01/bin/bsc
: "${STRETCH_TAPE:=/tmp/mcp.tape}"
export STRETCH_TAPE
cd "$TESTS_DIR"
python3 gen_mcp_boot_tb.py "$MODULE" > "$BSV_DIR/$MODULE.bsv"
cd "$BSV_DIR"
mkdir -p build-hosttape simbuild-hosttape
"$BSC" -sim -D HOST_TAPE -simdir simbuild-hosttape -bdir build-hosttape \
       -info-dir build-hosttape -show-schedule -g "mk$MODULE" -u "$MODULE.bsv" \
       +RTS -K512m -RTS
"$BSC" -sim -D HOST_TAPE -simdir simbuild-hosttape -bdir build-hosttape \
       -e "mk$MODULE" -o "${MODULE}_sim" host_tape.c +RTS -K512m -RTS
"./${MODULE}_sim"
