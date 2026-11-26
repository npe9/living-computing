#!/bin/sh
# Build and run mkSauStepTb, the serial arithmetic unit's STEPPED-ADD test (half (b), 2026-11-25),
# on mkSAU (bsv/StretchSAU.bsv; fidelity_plan.md A3, 2026-11-25).
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
mkdir -p build-saustep simbuild-saustep
"$BSC" -sim -simdir simbuild-saustep -bdir build-saustep -info-dir build-saustep \
       -g mkSauStepTb -u StretchSAU.bsv +RTS -K512m -RTS
"$BSC" -sim -simdir simbuild-saustep -bdir build-saustep -e mkSauStepTb \
       -o saustep_sim +RTS -K512m -RTS
./saustep_sim
