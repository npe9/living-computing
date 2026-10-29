#!/bin/sh
# Build and run mkDivBoxTb, the iterative floating-point divide box's
# own testbench (bsv/StretchDivBox.bsv).
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
       -g mkDivBoxTb -u StretchDivBox.bsv +RTS -K512m -RTS
"$BSC" -sim -simdir simbuild-divbox -bdir build-divbox -e mkDivBoxTb \
       -o divbox_sim +RTS -K512m -RTS
./divbox_sim
