#!/bin/sh
# Build and run the ATT92010 event-processing testbench.
# Compiler resolution is the same as run_smoke.sh.
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

"$BSC" +RTS -K512M -RTS -sim -g mkHobbitEventTb -u HobbitEventTb.bsv
"$BSC" +RTS -K512M -RTS -sim -e mkHobbitEventTb -o sim_event

out=$(./sim_event)
printf '%s\n' "$out"

if printf '%s\n' "$out" | grep -q '^FAIL'; then
  echo "run_event: FAIL" >&2
  exit 1
fi
passes=$(printf '%s\n' "$out" | grep -c '^PASS ' || true)
if [ "$passes" -ne 41 ]; then
  echo "run_event: $passes PASS lines, want 41" >&2
  exit 1
fi
printf '%s\n' "$out" | grep '^EVENT RESULT 41 PASS 0 FAIL$' >/dev/null || {
  echo "run_event: final count line missing or wrong" >&2
  exit 1
}
