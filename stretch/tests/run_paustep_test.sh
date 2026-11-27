#!/bin/sh
# Build and run mkPauStepTb, the parallel arithmetic unit's STEPPING test (A4 step 3),
# on mkPAU (bsv/StretchPAU.bsv; fidelity_plan.md A4, 2026-11-26 step 3).
# The pattern and the private build directories are run_divbox_test.sh's,
# for the reasons given there (a box tested without instantiating
# storage; per-job -bdir).
set -e
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
BSV_DIR="$TESTS_DIR/../bsv"
export BLUESPECDIR=/opt/homebrew/Cellar/bsc/2026.01/libexec/lib
export PATH=/opt/homebrew/Cellar/bsc/2026.01/bin:$PATH
BSC=/opt/homebrew/Cellar/bsc/2026.01/bin/bsc
cd "$BSV_DIR"
mkdir -p build-paustep simbuild-paustep
"$BSC" -sim -simdir simbuild-paustep -bdir build-paustep -info-dir build-paustep \
       -g mkPauStepTb -u StretchPAU.bsv +RTS -K512m -RTS
"$BSC" -sim -simdir simbuild-paustep -bdir build-paustep -e mkPauStepTb \
       -o paustep_sim +RTS -K512m -RTS
./paustep_sim
