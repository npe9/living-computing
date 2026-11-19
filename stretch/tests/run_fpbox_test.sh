#!/bin/sh
# Build and run mkFpBoxTb, the floating-point box's own testbench
# (bsv/StretchFpBox.bsv).  The pattern and the private build
# directories are run_divbox_test.sh's, for the reasons given there
# (a box tested without instantiating storage; per-job -bdir).
set -e
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
BSV_DIR="$TESTS_DIR/../bsv"
export BLUESPECDIR=/opt/homebrew/Cellar/bsc/2026.01/libexec/lib
export PATH=/opt/homebrew/Cellar/bsc/2026.01/bin:$PATH
BSC=/opt/homebrew/Cellar/bsc/2026.01/bin/bsc
cd "$BSV_DIR"
mkdir -p build-fpbox simbuild-fpbox
"$BSC" -sim -simdir simbuild-fpbox -bdir build-fpbox -info-dir build-fpbox \
       -g mkFpBoxTb -u StretchFpBox.bsv +RTS -K512m -RTS
"$BSC" -sim -simdir simbuild-fpbox -bdir build-fpbox -e mkFpBoxTb \
       -o fpbox_sim +RTS -K512m -RTS
./fpbox_sim
