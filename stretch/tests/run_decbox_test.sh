#!/bin/sh
# Build and run mkDecBoxTb, the decimal adder box's own testbench
# (bsv/StretchDecBox.bsv).  The pattern and the private build
# directories are run_divbox_test.sh's, for the reasons given there
# (a box tested without instantiating storage; per-job -bdir).
set -e
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
BSV_DIR="$TESTS_DIR/../bsv"
export BLUESPECDIR=/opt/homebrew/Cellar/bsc/2026.01/libexec/lib
export PATH=/opt/homebrew/Cellar/bsc/2026.01/bin:$PATH
BSC=/opt/homebrew/Cellar/bsc/2026.01/bin/bsc
cd "$BSV_DIR"
mkdir -p build-decbox simbuild-decbox
"$BSC" -sim -simdir simbuild-decbox -bdir build-decbox -info-dir build-decbox \
       -g mkDecBoxTb -u StretchDecBox.bsv +RTS -K512m -RTS
"$BSC" -sim -simdir simbuild-decbox -bdir build-decbox -e mkDecBoxTb \
       -o decbox_sim +RTS -K512m -RTS
./decbox_sim
