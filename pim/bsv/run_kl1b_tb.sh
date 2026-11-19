#!/bin/sh
# Build and run the KL1-B execution testbench with Bluesim.
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

"$BSC" -sim -g mkPimKL1BTb -u PimKL1BTb.bsv
"$BSC" -sim -e mkPimKL1BTb -o sim_kl1b
./sim_kl1b

"$BSC" -sim -g mkPimKL1BFailTb -u PimKL1BFailTb.bsv
"$BSC" -sim -e mkPimKL1BFailTb -o sim_kl1bfail
./sim_kl1bfail

"$BSC" -sim -g mkPimKL1BConstFailTb -u PimKL1BConstFailTb.bsv
"$BSC" -sim -e mkPimKL1BConstFailTb -o sim_kl1bconstfail
./sim_kl1bconstfail

"$BSC" -sim -g mkPimKL1BStructTb -u PimKL1BStructTb.bsv
"$BSC" -sim -e mkPimKL1BStructTb -o sim_kl1bstruct
./sim_kl1bstruct

"$BSC" -sim -g mkPimKL1BIntTb -u PimKL1BIntTb.bsv
"$BSC" -sim -e mkPimKL1BIntTb -o sim_kl1bint
./sim_kl1bint

"$BSC" -sim -g mkPimKL1BWaitTb -u PimKL1BWaitTb.bsv
"$BSC" -sim -e mkPimKL1BWaitTb -o sim_kl1bwait
./sim_kl1bwait

"$BSC" -sim -g mkPimKL1BSetTb -u PimKL1BSetTb.bsv
"$BSC" -sim -e mkPimKL1BSetTb -o sim_kl1bset
./sim_kl1bset

"$BSC" -sim -g mkPimKL1BArithTb -u PimKL1BArithTb.bsv
"$BSC" -sim -e mkPimKL1BArithTb -o sim_kl1barith
./sim_kl1barith

"$BSC" -sim -g mkPimKL1BGetTb -u PimKL1BGetTb.bsv
"$BSC" -sim -e mkPimKL1BGetTb -o sim_kl1bget
./sim_kl1bget

"$BSC" -sim -g mkPimKL1BControlTb -u PimKL1BControlTb.bsv
"$BSC" -sim -e mkPimKL1BControlTb -o sim_kl1bcontrol
./sim_kl1bcontrol

"$BSC" -sim -g mkPimKL1BSuspendTb -u PimKL1BSuspendTb.bsv
"$BSC" -sim -e mkPimKL1BSuspendTb -o sim_kl1bsuspend
./sim_kl1bsuspend

"$BSC" -sim -g mkPimKL1BMiscTb -u PimKL1BMiscTb.bsv
"$BSC" -sim -e mkPimKL1BMiscTb -o sim_kl1bmisc
./sim_kl1bmisc

"$BSC" -sim -g mkPimKL1BJumpTb -u PimKL1BJumpTb.bsv
"$BSC" -sim -e mkPimKL1BJumpTb -o sim_kl1bjump
./sim_kl1bjump
