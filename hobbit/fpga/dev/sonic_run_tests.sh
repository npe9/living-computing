#!/bin/sh
# The SONIC tests (sonic.md):
#
#   1. every trace in sonic_tests/ is re-checked against a fresh
#      p9boot.Sonic (sonic_trace.py check: the trace is what the model
#      does), then
#   2. replayed into the RTL (SonicReplayTb.bsv): every register read, irq
#      level, DMA word and transmitted frame compared with the model's.
#
#   sh hobbit/fpga/dev/sonic_run_tests.sh [TRACE ...]
#
# A trace passes when the Python check has no mismatch, the RTL prints no
# MISMATCH line, and the testbench reaches its SUMMARY with every event.
# Build products go to a scratch directory (BUILD_DIR to keep them), never
# the source tree.  bsc is the newest Homebrew Cellar install, as
# hobbit/bsv/run_uart.sh.
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)

BSC=${BSC_BIN:-$(ls -d /opt/homebrew/Cellar/bsc/*/bin/bsc 2>/dev/null | sort | tail -1)}
if [ -z "$BSC" ] || [ ! -x "$BSC" ]; then
  echo "sonic_run_tests: bsc not found; set BSC_BIN" >&2
  exit 1
fi
BLUESPECDIR=$(cd "$(dirname "$BSC")/../libexec/lib" && pwd)
export BLUESPECDIR
PATH=$(dirname "$BSC"):$PATH
export PATH

BUILD=${BUILD_DIR:-$(mktemp -d "${TMPDIR:-/tmp}/hobbit-sonic.XXXXXX")}
[ -n "${BUILD_DIR:-}" ] || trap 'rm -rf "$BUILD"' EXIT
mkdir -p "$BUILD/src" "$BUILD/obj"
cp "$HERE/Sonic.bsv" "$HERE/SonicReplayTb.bsv" "$BUILD/src/"
(
  cd "$BUILD/src"
  bsc +RTS -K512M -RTS -sim -bdir "$BUILD/obj" -simdir "$BUILD/obj" \
      -info-dir "$BUILD/obj" -aggressive-conditions \
      -no-warn-action-shadowing -suppress-warnings G0010:G0024 \
      -g mkSonicReplayTb -u SonicReplayTb.bsv >"$BUILD/bsc.log" 2>&1 ||
      { cat "$BUILD/bsc.log"; exit 1; }
  bsc +RTS -K512M -RTS -sim -bdir "$BUILD/obj" -simdir "$BUILD/obj" \
      -info-dir "$BUILD/obj" -e mkSonicReplayTb -o "$BUILD/sim" \
      >>"$BUILD/bsc.log" 2>&1 || { cat "$BUILD/bsc.log"; exit 1; }
)

[ $# -gt 0 ] || set -- "$HERE"/sonic_tests/*.trace.gz
fail=0
for t in "$@"; do
  name=$(basename "$t")
  run="$BUILD/run.$name"
  mkdir -p "$run"
  if ! python3 "$HERE/sonic_trace.py" check "$t" >"$run/check.log" 2>&1; then
    echo "FAIL $name: the Python check: $(tail -1 "$run/check.log")"
    fail=1
    continue
  fi
  python3 "$HERE/sonic_trace.py" vectors "$t" "$run" >"$run/vec.log"
  (cd "$run" && "$BUILD/sim" >"$run/sim.log" 2>&1) || true
  nmis=$(grep -c '^MISMATCH' "$run/sim.log" || true)
  summary=$(grep '^SUMMARY' "$run/sim.log" || true)
  want=$(sed -n 's/^sonic_trace: \([0-9]*\) events.*/\1/p' "$run/vec.log")
  if [ "$nmis" != 0 ] || [ -z "$summary" ] ||
     ! printf '%s\n' "$summary" | grep -q "events=$want "; then
    echo "FAIL $name: $nmis mismatches (${summary:-no SUMMARY}; $want events)"
    grep '^MISMATCH\|FAULT' "$run/sim.log" | head -20
    fail=1
  else
    echo "PASS $name: $(tail -1 "$run/check.log" | sed 's/^sonic_trace: //'); RTL $summary"
  fi
done
exit $fail
