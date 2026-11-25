#!/bin/sh
# Build and run HobbitArithTb: the shared divider (divUnit) and the
# one-product multiplier (mulArith) against the forms they replaced
# (docs/fpga_area.md, milestone 1).  Its own -bdir/-simdir, so it never
# shares .bo files with the suite's other builds.
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

b=../build/arith
mkdir -p "$b"
"$BSC" +RTS -K512M -RTS -sim -g mkHobbitArithTb -u -bdir "$b" -simdir "$b" \
    -p "$b:.:%/Libraries" HobbitArithTb.bsv > "$b/build.log" 2>&1 || {
    tail -30 "$b/build.log"; exit 1; }
"$BSC" +RTS -K512M -RTS -sim -e mkHobbitArithTb -bdir "$b" -simdir "$b" \
    -o "$b/sim_arith" >> "$b/build.log" 2>&1 || { tail -30 "$b/build.log"; exit 1; }

out=$("$b/sim_arith")
printf '%s\n' "$out" | head -20

if printf '%s\n' "$out" | grep -q '^FAIL'; then
  echo "run_arith: FAIL ($(printf '%s\n' "$out" | grep -c '^FAIL ') failing checks)" >&2
  exit 1
fi
if ! printf '%s\n' "$out" | grep -q '^SUMMARY arith: [0-9]* operand pairs, 0 failures$'; then
  echo "run_arith: the testbench did not reach its summary" >&2
  exit 1
fi
