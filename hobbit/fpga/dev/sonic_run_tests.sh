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
# Discrimination (observed, 2026-11-24; sonic.md has the table):
#   S1 FCS not inverted        join 534, directed 9 mismatches
#   S2 isr write-one-to-set    join 2264, directed 27
#   S3 Bc without Brd          join pass, directed 1238
#   S4 mpt not counted         join pass, directed 2
#   S5 fragments 16 apart      join pass, directed 9
#   S6 Lpkt at rbwc <= eobc    join pass, directed 1143
#   S7 rrp wraps at rea+16     join 1232, directed 1
#   S8 irq ignores imr         join 4, directed 10
#   S9 rcr Pro ignored         join pass, directed 595
#   S10 bad frame accepted     join pass, directed 1235
#   S11 bad frame over 2K faults  join pass, directed 46
#   S12 Pktrx before the writes   join pass, directed 2 (irq order)
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
