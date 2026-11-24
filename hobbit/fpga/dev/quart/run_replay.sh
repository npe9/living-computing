#!/bin/sh
# Replay register-access traces into the Quart / interrupt-path RTL and the
# Python models (tools/p9boot.py) and compare (QuartReplayTb.bsv).
#
#   sh hobbit/fpga/dev/quart/run_replay.sh [TRACE ...]
#
# With no arguments: every tests/*.trace (directed) and the kernel's own
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
  echo "run_replay: bsc not found; set BSC_BIN" >&2
  exit 1
fi
BLUESPECDIR=$(cd "$(dirname "$BSC")/../libexec/lib" && pwd)
export BLUESPECDIR
PATH=$(dirname "$BSC"):$PATH
export PATH

BUILD=${BUILD_DIR:-$(mktemp -d "${TMPDIR:-/tmp}/hobbit-quart.XXXXXX")}
[ -n "${BUILD_DIR:-}" ] || trap 'rm -rf "$BUILD"' EXIT
mkdir -p "$BUILD/src" "$BUILD/obj"
cp "$HERE/HobbitQuart.bsv" "$HERE/QuartReplayTb.bsv" \
   "$HERE/../intc/HobbitIntc.bsv" "$BUILD/src/"
(
  cd "$BUILD/src"
  bsc +RTS -K512M -RTS -sim -bdir "$BUILD/obj" -simdir "$BUILD/obj" \
      -info-dir "$BUILD/obj" -no-warn-action-shadowing -aggressive-conditions \
      -g mkQuartReplayTb -u QuartReplayTb.bsv >"$BUILD/bsc.log" 2>&1 ||
      { cat "$BUILD/bsc.log"; exit 1; }
  bsc +RTS -K512M -RTS -sim -bdir "$BUILD/obj" -simdir "$BUILD/obj" \
      -info-dir "$BUILD/obj" -e mkQuartReplayTb -o "$BUILD/sim" \
      >>"$BUILD/bsc.log" 2>&1 || { cat "$BUILD/bsc.log"; exit 1; }
)

if [ $# -eq 0 ]; then
  set -- "$HERE"/tests/*.trace "$HERE/tests/kernel_echo.trace.gz"
fi

fail=0
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
