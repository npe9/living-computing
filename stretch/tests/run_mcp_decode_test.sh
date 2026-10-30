#!/bin/sh
# run_mcp_decode_test.sh -- WHAT MCP-DECODE BUILT, read before ASSIGN
# throws it away.
#
# >>> WHY THIS CANNOT BE A CHECK IN THE ORDINARY BOOT TESTBENCH. <<<
# MCP-DECODE fills the I/O request table from the punched IOD cards,
# ASSIGN then fails, and ASSIGN's reject path CLEARS the table --
# docs/boot_plan.md: "clearing the reel slot, the assigned bits and the
# mount bits".  So at end of run every word of both request tables reads
# zero, however well or badly DECODE performed.  Measured 2026-10-30:
# TUIORQ's first word is 0x0600001000000000 mid-run and 0 at the end.
#
# This testbench runs until ASSIGN IS ENTERED (half-word 3970, printed
# p.65 line 6) and reads the table there.  The stop is an ADDRESS and not
# a step number on purpose: the window between DECODE's stores and
# ASSIGN's entry is about four thousand steps wide, and a newly
# transcribed page moves it.  An address is the program's own structure.
#
# Same -D HOST_TAPE and the same private -bdir as run_mcp_boot.sh, for
# the reason that file's header gives: a StretchIO.bo built without
# HOST_TAPE is silently wrong for a build with it.
set -e
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
BSV_DIR="$TESTS_DIR/../bsv"
PYTHONPATH="$TESTS_DIR/../strap:$TESTS_DIR"; export PYTHONPATH
export BLUESPECDIR=/opt/homebrew/Cellar/bsc/2026.01/libexec/lib
export PATH=/opt/homebrew/Cellar/bsc/2026.01/bin:$PATH
BSC=/opt/homebrew/Cellar/bsc/2026.01/bin/bsc
MODULE="${1:-StretchMcpDecodeTb}"
: "${STRETCH_TAPE:=/tmp/mcp.tape}"
export STRETCH_TAPE
cd "$TESTS_DIR"
python3 gen_mcp_boot_tb.py "$MODULE" > "$BSV_DIR/$MODULE.bsv"
cd "$BSV_DIR"
mkdir -p build-hosttape simbuild-hosttape
"$BSC" -sim -D HOST_TAPE -simdir simbuild-hosttape -bdir build-hosttape \
       -info-dir build-hosttape -g "mk$MODULE" -u "$MODULE.bsv" \
       +RTS -K512m -RTS
"$BSC" -sim -D HOST_TAPE -simdir simbuild-hosttape -bdir build-hosttape \
       -e "mk$MODULE" -o "${MODULE}_sim" host_tape.c +RTS -K512m -RTS
"./${MODULE}_sim"
