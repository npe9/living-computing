#!/bin/sh
# run_mcp_assign_test.sh -- MCP'S ASSIGN SUCCEEDING, on a machine that
# has the units MCP asks for.
#
# >>> WHAT THIS SECTION IS FOR. <<<  The default fixture declares ONE
# available tape unit (strap/prosa.py's TAPE_UNITS_ONE_SHORT), and MCP's
# own deck asks for TWO output tapes -- MCP_IODS' MCPOUT1 and MCPOUT2.
# So the third I/O request cannot be satisfied, ASSIGN rejects, and MCP
# halts in X6ERR printing "EXHAUSTED ALL CHANNELS".  That is CORRECT
# behaviour and run_mcp_boot.sh keeps twelve checks on it.
#
# This run declares the machine C22-6728-1 printed p.98's minimal IPL
# case describes -- a card reader and output tape unitS -- by selecting
# TAPE_UNITS_BOTH_AVAILABLE.  MCP then assigns all three requests and
# carries on to T MOVE.
#
# WHY IT STOPS AT T MOVE (half-word 5144, printed p.27's own
# "TMOVE SYN, (8)5014.0" = word 2572).  Two reasons, and neither is
# convenience: the request table is cleared by paths downstream of
# ASSIGN, and past T MOVE the run falls into storage that no
# transcribed page fills, so the end of the run says nothing at all.
# The stop is an ADDRESS rather than a step count because a newly
# transcribed page moves step numbers and does not move p.27.
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
MODULE="${1:-StretchMcpAssignTb}"
# >>> ITS OWN TAPE PATH, AND THAT IS NOT TIDINESS. <<<
# This fixture declares a DIFFERENT MACHINE from the other two sections
# (two available tape units instead of one), so its tape is not
# interchangeable with theirs.  Each script regenerates the tape before
# building, so sharing one path would work sequentially and break the
# moment anything ran out of order or in parallel.  A separate path
# makes the difference impossible to get wrong.
: "${STRETCH_TAPE:=/tmp/mcp.assign.tape}"
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
