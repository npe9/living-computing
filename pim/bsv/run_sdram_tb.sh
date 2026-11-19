#!/bin/sh
# Build and run the PIM/m SDRAM-backed local-store testbench with Bluesim.
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

"$BSC" -sim -g mkPimSdramTb -u PimSdramStoreTb.bsv
"$BSC" -sim -e mkPimSdramTb -o sim_sdram_tb
./sim_sdram_tb
