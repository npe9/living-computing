#!/bin/sh
# run_tb.sh -- compile and run one HAND-WRITTEN testbench module.
#
# run_program.sh (in ../strap) covers the usual case: a STRAP program
# whose expected results are checked on the core.  This is for the other
# kind -- a testbench that exercises the model's pure functions directly,
# with no program and no core, such as StretchSvaWidthSweep sweeping every
# half-word through decodeHalfWord.  Same pinned toolchain as build.sh;
# see bsv/README.md "Toolchain".
#
# Usage:  ./run_tb.sh StretchSvaWidthSweep

set -e
if [ $# -ne 1 ]; then echo "usage: $0 ModuleName" >&2; exit 1; fi
MODULE="$1"
export BLUESPECDIR=/opt/homebrew/Cellar/bsc/2026.01/libexec/lib
export PATH=/opt/homebrew/Cellar/bsc/2026.01/bin:$PATH
BSC=/opt/homebrew/Cellar/bsc/2026.01/bin/bsc
cd "$(dirname "$0")"
mkdir -p build simbuild
"$BSC" -sim -simdir simbuild -bdir build -info-dir build -g "mk$MODULE" -u "$MODULE.bsv" +RTS -K512m -RTS
"$BSC" -sim -simdir simbuild -bdir build -e "mk$MODULE" -o "${MODULE}_sim" +RTS -K512m -RTS
"./${MODULE}_sim"
