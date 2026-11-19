#!/bin/sh
# Build and run the integrated core/MMU/event testbench: PSW.V = 1, a
# fetch translation fault, and the p. 1-38 exception sequence.
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

"$BSC" +RTS -K512M -RTS -sim -g mkHobbitCoreMmuTb -u HobbitCoreMmuTb.bsv
"$BSC" +RTS -K512M -RTS -sim -e mkHobbitCoreMmuTb -o sim_core_mmu

out=$(./sim_core_mmu)
printf '%s\n' "$out"

if printf '%s\n' "$out" | grep -q '^FAIL'; then
  echo "run_core_mmu: FAIL" >&2
  exit 1
fi
passes=$(printf '%s\n' "$out" | grep -c '^PASS ' || true)
if [ "$passes" -ne 12 ]; then
  echo "run_core_mmu: $passes PASS lines, want 12" >&2
  exit 1
fi
printf '%s\n' "$out" | grep '^CORE MMU RESULT 12 PASS 0 FAIL$' >/dev/null || {
  echo "run_core_mmu: final count line missing or wrong" >&2
  exit 1
}
