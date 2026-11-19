#!/bin/sh
# Build and run the TIMER1/TIMER2 testbench.
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

"$BSC" +RTS -K512M -RTS -sim -g mkHobbitTimerTb -u HobbitTimerTb.bsv
"$BSC" +RTS -K512M -RTS -sim -e mkHobbitTimerTb -o sim_timer

out=$(./sim_timer)
printf '%s\n' "$out"

if printf '%s\n' "$out" | grep -q '^FAIL'; then
  echo "run_timer: FAIL" >&2
  exit 1
fi
passes=$(printf '%s\n' "$out" | grep -c '^PASS ' || true)
if [ "$passes" -lt 30 ]; then
  echo "run_timer: only $passes PASS lines" >&2
  exit 1
fi
if ! printf '%s\n' "$out" | grep -q '^SUMMARY timer: done$'; then
  echo "run_timer: the testbench did not reach its summary" >&2
  exit 1
fi
