#!/bin/sh
# Build and run mkFpCommitTb (bsv/StretchFpCommitTest.bsv): fpStoreClass
# AND fpArithClass exercised with NO STORAGE INSTANTIATED.
#
# A SEPARATE SCRIPT for the same reason run_divbox_test.sh is one -- this
# testbench has no deck and cannot go through run_program.sh.  The point
# of step 2's first family is that a pure function needs no machine
# around it to be tested, and this script is what demonstrates it: it
# builds one module out of StretchFpCommitTest.bsv and runs it.
set -e
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
BSV_DIR="$TESTS_DIR/../bsv"
export BLUESPECDIR=/opt/homebrew/Cellar/bsc/2026.01/libexec/lib
export PATH=/opt/homebrew/Cellar/bsc/2026.01/bin:$PATH
BSC=/opt/homebrew/Cellar/bsc/2026.01/bin/bsc
cd "$BSV_DIR"
# PRIVATE BUILD DIRECTORIES.  bsc writes one set of .bo per -bdir, so a
# job sharing build/ and simbuild/ with the suite corrupts its
# neighbours -- run_divbox_test.sh's header records the six passes and
# three "model creation time does not match" errors that cost.
mkdir -p build-fpcommit simbuild-fpcommit
"$BSC" -sim -simdir simbuild-fpcommit -bdir build-fpcommit \
       -info-dir build-fpcommit \
       -g mkFpCommitTb -u StretchFpCommitTest.bsv +RTS -K512m -RTS
"$BSC" -sim -simdir simbuild-fpcommit -bdir build-fpcommit \
       -e mkFpCommitTb -o fpcommit_sim +RTS -K512m -RTS
./fpcommit_sim
