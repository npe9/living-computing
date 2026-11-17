#!/bin/sh
# Build and run mkCvtBoxTb, the radix converter box's own testbench
# (bsv/StretchCvtBox.bsv).  The pattern and the private build
# directories are run_divbox_test.sh's, for the reasons given there
# (a box tested without instantiating storage; per-job -bdir).
set -e
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
BSV_DIR="$TESTS_DIR/../bsv"
export BLUESPECDIR=/opt/homebrew/Cellar/bsc/2026.01/libexec/lib
export PATH=/opt/homebrew/Cellar/bsc/2026.01/bin:$PATH
BSC=/opt/homebrew/Cellar/bsc/2026.01/bin/bsc
cd "$BSV_DIR"
mkdir -p build-cvtbox simbuild-cvtbox
"$BSC" -sim -simdir simbuild-cvtbox -bdir build-cvtbox -info-dir build-cvtbox \
       -g mkCvtBoxTb -u StretchCvtBox.bsv +RTS -K512m -RTS
"$BSC" -sim -simdir simbuild-cvtbox -bdir build-cvtbox -e mkCvtBoxTb \
       -o cvtbox_sim +RTS -K512m -RTS
./cvtbox_sim
