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

"$BSC" -sim -simdir simbuild -bdir build -info-dir build -g mkStretchTb -u StretchSmoke.bsv +RTS -K512m -RTS
"$BSC" -sim -simdir simbuild -bdir build -e mkStretchTb -o stretch_sim +RTS -K512m -RTS

if [ "$1" = "run" ]; then
  ./stretch_sim
fi
