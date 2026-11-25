#!/bin/sh
# run_fixture_test.sh -- the disk's two arcs and the console's paper as
# block RAM, tested alone: ../bsv/StretchFixtureTest.bsv (its header has
# the checks and the observed injection failure sets).  2026-11-25,
# docs/fidelity_plan.md F0.  Own -bdir/-simdir, like run_fpcommit_test.sh.
set -e
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
BSV_DIR="$TESTS_DIR/../bsv"
export BLUESPECDIR=/opt/homebrew/Cellar/bsc/2026.01/libexec/lib
export PATH=/opt/homebrew/Cellar/bsc/2026.01/bin:$PATH
BSC=/opt/homebrew/Cellar/bsc/2026.01/bin/bsc
cd "$BSV_DIR"
mkdir -p build-fixture simbuild-fixture
"$BSC" -sim -simdir simbuild-fixture -bdir build-fixture \
       -info-dir build-fixture \
       -g mkFixtureTb -u StretchFixtureTest.bsv +RTS -K512m -RTS
"$BSC" -sim -simdir simbuild-fixture -bdir build-fixture \
       -e mkFixtureTb -o fixture_sim +RTS -K512m -RTS
./fixture_sim
