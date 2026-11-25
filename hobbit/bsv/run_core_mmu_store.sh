#!/bin/sh
# Build and run the core/MMU byte-store fault check (HobbitCoreMmuStoreTb):
# a byte store into an unmapped page raises exception 9 at its PC.
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

"$BSC" +RTS -K512M -RTS -sim -g mkHobbitCoreMmuStoreTb -u HobbitCoreMmuStoreTb.bsv
"$BSC" +RTS -K512M -RTS -sim -e mkHobbitCoreMmuStoreTb -o sim_core_mmu_store

out=$(./sim_core_mmu_store)
printf '%s\n' "$out"

if printf '%s\n' "$out" | grep -q '^FAIL'; then
  echo "run_core_mmu_store: FAIL" >&2
  exit 1
fi
passes=$(printf '%s\n' "$out" | grep -c '^PASS ' || true)
if [ "$passes" -ne 6 ]; then
  echo "run_core_mmu_store: $passes PASS lines, want 6" >&2
  exit 1
fi
printf '%s\n' "$out" | grep '^CORE MMU STORE RESULT 6 PASS 0 FAIL$' >/dev/null || {
  echo "run_core_mmu_store: final count line missing or wrong" >&2
  exit 1
}
