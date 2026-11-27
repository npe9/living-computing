#!/bin/sh
# Build and run mkLaPartsTb: laParts, an instruction's look-ahead levels as
# Table A-2's E-box sheet gives them (bsv/StretchLaParts.bsv; fidelity_plan.md
# A5 part 2, 2026-11-27).
# The pattern and the private build directories are run_divbox_test.sh's,
# for the reasons given there (a pure function tested without instantiating
# storage; per-job -bdir).
set -e
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
BSV_DIR="$TESTS_DIR/../bsv"
export BLUESPECDIR=/opt/homebrew/Cellar/bsc/2026.01/libexec/lib
export PATH=/opt/homebrew/Cellar/bsc/2026.01/bin:$PATH
BSC=/opt/homebrew/Cellar/bsc/2026.01/bin/bsc
cd "$BSV_DIR"
mkdir -p build-laparts simbuild-laparts
"$BSC" -sim -simdir simbuild-laparts -bdir build-laparts -info-dir build-laparts \
       -g mkLaPartsTb -u StretchLaParts.bsv +RTS -K512m -RTS
"$BSC" -sim -simdir simbuild-laparts -bdir build-laparts -e mkLaPartsTb \
       -o laparts_sim +RTS -K512m -RTS
./laparts_sim
