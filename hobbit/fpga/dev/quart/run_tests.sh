#!/bin/sh
# The Quart / interrupt-path tests:
#
#   1. QuartUnitTb.bsv: what the RTL does that the Python model has no
#      counterpart for (pin waveforms, TX FIFO full, RX overrun and framing,
#      the counter period in clocks), checked against the data sheet.
#   2. QuartReplayTb.bsv: register-access traces replayed into the RTL and
#      the Python models (tools/p9boot.py), compared access by access.
#
#   sh hobbit/fpga/dev/quart/run_tests.sh [TRACE ...]
#
# With TRACE arguments only those traces are replayed (no unit test).
# With no arguments: the unit test, every tests/*.trace (directed) and the
# kernel's own
# boot trace tests/kernel_echo.trace.gz (captured with quart_trace.py
# capture from the p9boot run named in its first line).  A trace passes
# when quart_trace.py's fresh Python models reproduce every captured value,
# the RTL prints no MISMATCH line, and the testbench reaches its SUMMARY.
#
# Build products go to a scratch directory (BUILD_DIR to keep them), never
# the source tree.  bsc is the newest Homebrew Cellar install (as
# hobbit/bsv/run_uart.sh).
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)

BSC=${BSC_BIN:-$(ls -d /opt/homebrew/Cellar/bsc/*/bin/bsc 2>/dev/null | sort | tail -1)}
if [ -z "$BSC" ] || [ ! -x "$BSC" ]; then
  echo "run_tests: bsc not found; set BSC_BIN" >&2
  exit 1
fi
BLUESPECDIR=$(cd "$(dirname "$BSC")/../libexec/lib" && pwd)
export BLUESPECDIR
PATH=$(dirname "$BSC"):$PATH
export PATH

BUILD=${BUILD_DIR:-$(mktemp -d "${TMPDIR:-/tmp}/hobbit-quart.XXXXXX")}
[ -n "${BUILD_DIR:-}" ] || trap 'rm -rf "$BUILD"' EXIT
mkdir -p "$BUILD/src" "$BUILD/obj"
cp "$HERE/HobbitQuart.bsv" "$HERE/QuartReplayTb.bsv" "$HERE/QuartUnitTb.bsv" \
   "$HERE/../intc/HobbitIntc.bsv" "$BUILD/src/"
build() {   # top module, package file, simulator
  (
    cd "$BUILD/src"
    bsc +RTS -K512M -RTS -sim -bdir "$BUILD/obj" -simdir "$BUILD/obj" \
        -info-dir "$BUILD/obj" -no-warn-action-shadowing \
        -aggressive-conditions -g "$1" -u "$2" >"$BUILD/bsc.log" 2>&1 ||
        { cat "$BUILD/bsc.log"; exit 1; }
    bsc +RTS -K512M -RTS -sim -bdir "$BUILD/obj" -simdir "$BUILD/obj" \
        -info-dir "$BUILD/obj" -e "$1" -o "$3" \
        >>"$BUILD/bsc.log" 2>&1 || { cat "$BUILD/bsc.log"; exit 1; }
  )
}
build mkQuartReplayTb QuartReplayTb.bsv "$BUILD/sim"

fail=0
if [ $# -eq 0 ]; then
  build mkQuartUnitTb QuartUnitTb.bsv "$BUILD/unit"
  (cd "$BUILD" && ./unit >"$BUILD/unit.log" 2>&1) || true
  grep '^FAIL' "$BUILD/unit.log" || true
  unit=$(grep '^UNIT' "$BUILD/unit.log" || true)
  case "$unit" in
    "UNIT pass="*" fail=0") echo "PASS unit: $unit" ;;
    *) echo "FAIL unit: ${unit:-no UNIT line}"; fail=1 ;;
  esac
  set -- "$HERE"/tests/*.trace "$HERE/tests/kernel_echo.trace.gz"
fi

for t in "$@"; do
  name=$(basename "$t")
  run="$BUILD/run.$name"
  mkdir -p "$run"
  case "$t" in
    *.gz) gunzip -c "$t" >"$run/trace" ;;
    *) cp "$t" "$run/trace" ;;
  esac
  if ! python3 "$HERE/quart_trace.py" vectors "$run/trace" \
        "$run/vectors.hex" >"$run/py.log" 2>&1; then
    echo "FAIL $name: the Python replay: $(tail -1 "$run/py.log")"
    fail=1
    continue
  fi
  (cd "$run" && "$BUILD/sim" >"$run/sim.log" 2>&1) || true
  nmis=$(grep -c '^MISMATCH' "$run/sim.log" || true)
  summary=$(grep '^SUMMARY' "$run/sim.log" || true)
  if [ "$nmis" != 0 ] || [ -z "$summary" ]; then
    echo "FAIL $name: $nmis mismatches ($summary)"
    grep '^MISMATCH' "$run/sim.log" | head -20
    fail=1
  else
    echo "PASS $name: $(sed -n 's/^quart_trace: .*: //p' "$run/py.log"); $summary; $(grep '^FAULTS' "$run/sim.log")"
  fi
done
exit $fail
