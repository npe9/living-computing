#!/bin/sh
# Build (and optionally run) the Stretch model with the Homebrew bsc
# toolchain, which has a complete, matched standard library -- unlike
# the cabal-installed bsc that may be earlier on PATH, which does not.
# See bsv/README.md "Toolchain" for the full story.
#
# Usage:
#   ./build.sh          # compile only
#   ./build.sh run      # compile (if needed) and run the testbench

set -e
export BLUESPECDIR=/opt/homebrew/Cellar/bsc/2026.01/libexec/lib
export PATH=/opt/homebrew/Cellar/bsc/2026.01/bin:$PATH
BSC=/opt/homebrew/Cellar/bsc/2026.01/bin/bsc
cd "$(dirname "$0")"
mkdir -p build simbuild

"$BSC" -sim -simdir simbuild -bdir build -info-dir build -show-schedule -g mkStretchTb -u StretchSmoke.bsv +RTS -K512m -RTS
# No core rule may be blocked by another core rule (see check_schedule.py
# for why bsc cannot assert this itself at the synthesized boundary).
python3 check_schedule.py build/mkStretchCore.sched
"$BSC" -sim -simdir simbuild -bdir build -e mkStretchTb -o stretch_sim +RTS -K512m -RTS

if [ "$1" = "run" ]; then
  ./stretch_sim
fi
