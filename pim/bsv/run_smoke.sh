#!/bin/sh
# Assemble and run the PIM/m smoke test with Bluesim.
# Use BSC_BIN to pin a compiler; otherwise take the newest Homebrew Cellar
# install. A bare `bsc` from PATH may be an older cabal build whose bluetcl
# does not match the wrapper.
set -eu
cd "$(dirname "$0")"

BSC=${BSC_BIN:-}
if [ -z "$BSC" ]; then
  BSC=$(ls -d /opt/homebrew/Cellar/bsc/*/bin/bsc 2>/dev/null | sort | tail -1)
fi
if [ -z "$BSC" ] || [ ! -x "$BSC" ]; then
  echo "bsc not found; set BSC_BIN to the 2026.01 bsc binary" >&2
  exit 1
fi

BLUESPECDIR=$(cd "$(dirname "$BSC")/../libexec/lib" && pwd)
export BLUESPECDIR
PATH=$(dirname "$BSC"):$PATH
export PATH

python3 ../asm/pimasm.py --out-dir generated
"$BSC" -sim -g mkPimSmoke -u PimSmoke.bsv
"$BSC" -sim -e mkPimSmoke -o sim_smoke
./sim_smoke
