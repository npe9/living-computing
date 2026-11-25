#!/bin/sh
# Build and run mkSauMulTb, the serial arithmetic unit's MULTIPLY class (was mkVflBoxTb),
# on mkSAU (bsv/StretchSAU.bsv; fidelity_plan.md A3, 2026-11-25).  The
# script keeps its old name so the suite's section keeps its place.  The
# pattern and the private build directories are run_divbox_test.sh's,
# for the reasons given there (a box tested without instantiating
# storage; per-job -bdir).
set -e
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
BSV_DIR="$TESTS_DIR/../bsv"
export BLUESPECDIR=/opt/homebrew/Cellar/bsc/2026.01/libexec/lib
export PATH=/opt/homebrew/Cellar/bsc/2026.01/bin:$PATH
BSC=/opt/homebrew/Cellar/bsc/2026.01/bin/bsc
cd "$BSV_DIR"
mkdir -p build-vflbox simbuild-vflbox
"$BSC" -sim -simdir simbuild-vflbox -bdir build-vflbox -info-dir build-vflbox \
       -g mkSauMulTb -u StretchSAU.bsv +RTS -K512m -RTS
"$BSC" -sim -simdir simbuild-vflbox -bdir build-vflbox -e mkSauMulTb \
       -o vflbox_sim +RTS -K512m -RTS
./vflbox_sim
