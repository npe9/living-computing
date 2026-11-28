#!/bin/sh
# Build and run mkBranchTimingTb: the I-box time of a count and branch and
# of a branch on an index indicator (bsv/StretchBranchTiming.bsv; Perf.
# Char. Vol. 1 Table 8, printed p.3-14, PDF 32; Vol. 2 PDF 112;
# fidelity_plan.md A7 part 2, 2026-11-28).  The pattern and the private
# build directories are run_xmit_timing_test.sh's.
set -e
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
BSV_DIR="$TESTS_DIR/../bsv"
export BLUESPECDIR=/opt/homebrew/Cellar/bsc/2026.01/libexec/lib
export PATH=/opt/homebrew/Cellar/bsc/2026.01/bin:$PATH
BSC=/opt/homebrew/Cellar/bsc/2026.01/bin/bsc
cd "$BSV_DIR"
mkdir -p build-branchtiming simbuild-branchtiming
"$BSC" -sim -simdir simbuild-branchtiming -bdir build-branchtiming -info-dir build-branchtiming \
       -g mkBranchTimingTb -u StretchBranchTiming.bsv +RTS -K512m -RTS
"$BSC" -sim -simdir simbuild-branchtiming -bdir build-branchtiming -e mkBranchTimingTb \
       -o branchtiming_sim +RTS -K512m -RTS
./branchtiming_sim
