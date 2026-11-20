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

# Each Bluesim bench exits 0 even when it prints FAIL, so a bare ./sim_kl1b
# cannot fail this script. Capture the output and require a PASS line.
run_bench() {
  name="$1"; shift
  out=$("$@" 2>&1) || { printf '%s\n' "$out"; echo "FAIL: $name crashed"; exit 1; }
  printf '%s\n' "$out"
  printf '%s\n' "$out" | grep -q "PASS" || { echo "FAIL: $name did not print PASS"; exit 1; }
}

"$BSC" -sim -g mkPimKL1BTb -u PimKL1BTb.bsv
"$BSC" -sim -e mkPimKL1BTb -o sim_kl1b
run_bench PimKL1BTb ./sim_kl1b

"$BSC" -sim -g mkPimKL1BFailTb -u PimKL1BFailTb.bsv
"$BSC" -sim -e mkPimKL1BFailTb -o sim_kl1bfail
run_bench PimKL1BFailTb ./sim_kl1bfail

"$BSC" -sim -g mkPimKL1BConstFailTb -u PimKL1BConstFailTb.bsv
"$BSC" -sim -e mkPimKL1BConstFailTb -o sim_kl1bconstfail
run_bench PimKL1BConstFailTb ./sim_kl1bconstfail

"$BSC" -sim -g mkPimKL1BStructTb -u PimKL1BStructTb.bsv
"$BSC" -sim -e mkPimKL1BStructTb -o sim_kl1bstruct
run_bench PimKL1BStructTb ./sim_kl1bstruct

"$BSC" -sim -g mkPimKL1BIntTb -u PimKL1BIntTb.bsv
"$BSC" -sim -e mkPimKL1BIntTb -o sim_kl1bint
run_bench PimKL1BIntTb ./sim_kl1bint

"$BSC" -sim -g mkPimKL1BWaitTb -u PimKL1BWaitTb.bsv
"$BSC" -sim -e mkPimKL1BWaitTb -o sim_kl1bwait
run_bench PimKL1BWaitTb ./sim_kl1bwait

"$BSC" -sim -g mkPimKL1BSetTb -u PimKL1BSetTb.bsv
"$BSC" -sim -e mkPimKL1BSetTb -o sim_kl1bset
run_bench PimKL1BSetTb ./sim_kl1bset

"$BSC" -sim -g mkPimKL1BArithTb -u PimKL1BArithTb.bsv
"$BSC" -sim -e mkPimKL1BArithTb -o sim_kl1barith
run_bench PimKL1BArithTb ./sim_kl1barith

"$BSC" -sim -g mkPimKL1BGetTb -u PimKL1BGetTb.bsv
"$BSC" -sim -e mkPimKL1BGetTb -o sim_kl1bget
run_bench PimKL1BGetTb ./sim_kl1bget

"$BSC" -sim -g mkPimKL1BControlTb -u PimKL1BControlTb.bsv
"$BSC" -sim -e mkPimKL1BControlTb -o sim_kl1bcontrol
run_bench PimKL1BControlTb ./sim_kl1bcontrol

"$BSC" -sim -g mkPimKL1BSuspendTb -u PimKL1BSuspendTb.bsv
"$BSC" -sim -e mkPimKL1BSuspendTb -o sim_kl1bsuspend
run_bench PimKL1BSuspendTb ./sim_kl1bsuspend

"$BSC" -sim -g mkPimKL1BMiscTb -u PimKL1BMiscTb.bsv
"$BSC" -sim -e mkPimKL1BMiscTb -o sim_kl1bmisc
run_bench PimKL1BMiscTb ./sim_kl1bmisc

"$BSC" -sim -g mkPimKL1BJumpTb -u PimKL1BJumpTb.bsv
"$BSC" -sim -e mkPimKL1BJumpTb -o sim_kl1bjump
run_bench PimKL1BJumpTb ./sim_kl1bjump

"$BSC" -sim -g mkPimKL1BNilTb -u PimKL1BNilTb.bsv
"$BSC" -sim -e mkPimKL1BNilTb -o sim_kl1bnil
run_bench PimKL1BNilTb ./sim_kl1bnil

"$BSC" -sim -g mkPimKL1BArgSlotTb -u PimKL1BArgSlotTb.bsv
"$BSC" -sim -e mkPimKL1BArgSlotTb -o sim_kl1bargslot
run_bench PimKL1BArgSlotTb ./sim_kl1bargslot

"$BSC" -sim -g mkPimKL1BSwitchTb -u PimKL1BSwitchTb.bsv
"$BSC" -sim -e mkPimKL1BSwitchTb -o sim_kl1bswitch
run_bench PimKL1BSwitchTb ./sim_kl1bswitch

"$BSC" -sim -g mkPimKL1BNoopTb -u PimKL1BNoopTb.bsv
"$BSC" -sim -e mkPimKL1BNoopTb -o sim_kl1bnoop
run_bench PimKL1BNoopTb ./sim_kl1bnoop

"$BSC" -sim -g mkPimKL1BCpTb -u PimKL1BCpTb.bsv
"$BSC" -sim -e mkPimKL1BCpTb -o sim_kl1bcp
run_bench PimKL1BCpTb ./sim_kl1bcp

"$BSC" -sim -g mkPimKL1BGuardBacktrackTb -u PimKL1BGuardBacktrackTb.bsv
"$BSC" -sim -e mkPimKL1BGuardBacktrackTb -o sim_kl1bgbt
run_bench PimKL1BGuardBacktrackTb ./sim_kl1bgbt

"$BSC" -sim -g mkPimKL1BBindTb -u PimKL1BBindTb.bsv
"$BSC" -sim -e mkPimKL1BBindTb -o sim_kl1bbind
run_bench PimKL1BBindTb ./sim_kl1bbind

"$BSC" -sim -g mkPimKL1BSetAtomTb -u PimKL1BSetAtomTb.bsv
"$BSC" -sim -e mkPimKL1BSetAtomTb -o sim_kl1bsetatom
run_bench PimKL1BSetAtomTb ./sim_kl1bsetatom

"$BSC" -sim -g mkPimKL1BWaitUnboundTb -u PimKL1BWaitUnboundTb.bsv
"$BSC" -sim -e mkPimKL1BWaitUnboundTb -o sim_kl1bwaitunbound
run_bench PimKL1BWaitUnboundTb ./sim_kl1bwaitunbound

"$BSC" -sim -g mkPimKL1BPutAtomTb -u PimKL1BPutAtomTb.bsv
"$BSC" -sim -e mkPimKL1BPutAtomTb -o sim_kl1bputatom
run_bench PimKL1BPutAtomTb ./sim_kl1bputatom

"$BSC" -sim -g mkPimKL1BOtherwiseTb -u PimKL1BOtherwiseTb.bsv
"$BSC" -sim -e mkPimKL1BOtherwiseTb -o sim_kl1botherwise
run_bench PimKL1BOtherwiseTb ./sim_kl1botherwise

"$BSC" -sim -g mkPimKL1BSwitchVecTb -u PimKL1BSwitchVecTb.bsv
"$BSC" -sim -e mkPimKL1BSwitchVecTb -o sim_kl1bswitchvec
run_bench PimKL1BSwitchVecTb ./sim_kl1bswitchvec
