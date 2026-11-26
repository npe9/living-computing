#!/bin/sh
# Build and run mkPauMixTb, the parallel arithmetic unit's MIXED-CLASS test (new with the merge),
# on mkPAU (bsv/StretchPAU.bsv; fidelity_plan.md A4, 2026-11-26).
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
mkdir -p build-paumix simbuild-paumix
"$BSC" -sim -simdir simbuild-paumix -bdir build-paumix -info-dir build-paumix \
       -g mkPauMixTb -u StretchPAU.bsv +RTS -K512m -RTS
"$BSC" -sim -simdir simbuild-paumix -bdir build-paumix -e mkPauMixTb \
       -o paumix_sim +RTS -K512m -RTS
./paumix_sim
