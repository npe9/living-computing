#!/bin/sh
# Build and run mkFpDivSketchTb (was mkDivBoxTb), the standalone divide
# sketch mkFpDivBox's own testbench, and mkPauDivTb (was mkCoreDivBoxTb),
# the divide class of mkPAU, the parallel arithmetic unit
# (bsv/StretchPAU.bsv, which holds both since 2026-11-26; fidelity_plan.md
# A4).
#
# A SEPARATE SCRIPT because the box is DELIBERATELY STANDALONE: nothing
# in StretchCore instantiates it yet, so it has no deck and cannot go
# through run_program.sh.  Testing an arithmetic box without
# instantiating all of storage is the point -- it is how Flute keeps
# mkIntDiv testable apart from its CPU.
set -e
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
BSV_DIR="$TESTS_DIR/../bsv"
export BLUESPECDIR=/opt/homebrew/Cellar/bsc/2026.01/libexec/lib
export PATH=/opt/homebrew/Cellar/bsc/2026.01/bin:$PATH
BSC=/opt/homebrew/Cellar/bsc/2026.01/bin/bsc
cd "$BSV_DIR"
# >>> PRIVATE BUILD DIRECTORIES, AND THIS IS NOT A STYLE CHOICE. <<<
# The first version of this script used the shared `build`/`simbuild`,
# and the suite then reported SIX FEWER passes and
#   Error: model creation time (...) does not match
# in three later sections -- Bluesim's symptom for a .so and executable
# built from clobbered .bo files.  bsc writes one set of .bo per -bdir,
# so any job sharing them corrupts its neighbours; the project already
# learned this once (see the note in docs about per-job -bdir/-simdir).
# build-* and simbuild-* are gitignored for the same reason.
mkdir -p build-divbox simbuild-divbox
"$BSC" -sim -simdir simbuild-divbox -bdir build-divbox -info-dir build-divbox \
       -g mkFpDivSketchTb -u StretchPAU.bsv +RTS -K512m -RTS
"$BSC" -sim -simdir simbuild-divbox -bdir build-divbox -e mkFpDivSketchTb \
       -o divbox_sim +RTS -K512m -RTS
./divbox_sim
# mkDivBox, the box the core instantiated (2026-11-15), now mkPAU's divide
# class: same file, its own testbench, checked against the `/` and `%` it
# replaced.
"$BSC" -sim -simdir simbuild-divbox -bdir build-divbox -info-dir build-divbox \
       -g mkPauDivTb -u StretchPAU.bsv +RTS -K512m -RTS
"$BSC" -sim -simdir simbuild-divbox -bdir build-divbox -e mkPauDivTb \
       -o coredivbox_sim +RTS -K512m -RTS
./coredivbox_sim
