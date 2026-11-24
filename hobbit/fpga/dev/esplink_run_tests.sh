#!/bin/sh
# The EspLink test (sonic.md "The link"): the RTL's framing against the
# ESP32 relay's own C codec.
#
#   sh hobbit/fpga/dev/esplink_run_tests.sh
#
# 1. esplink_ref.c is built with hobbit/fpga/esp32_ethrelay/main/relay.c
#    (the file the ESP32 firmware compiles);
# 2. esplink_vectors.py makes the inputs and, through esplink_ref, the
#    expected link bytes, frames and counters;
# 3. EspLinkTb.bsv runs mkEspLink25M in Bluesim against them.
# Discrimination (observed, 2026-11-24; sonic.md has the table):
#   E1 RTS ignored                    6527 mismatches (start bits under RTS)
#   E2 COBS blocks of 255             4777 (tx bytes; timeout)
#   E3 zero after a 0xFF block        290 (rx frames)
#   E4 type byte out of the CRC       2 (stats, no good frames)
#   E5 minimum frame 13               3 (2 rx frames, stats)
#   E6 wire overflow at 1531          1 (stats)
#   E7 framing not counted            1 (stats)
#   E8 1519-byte tx frame sent        1532 (tx bytes beyond the C's)
#   E9 no 0x01 after a full block     4997 (tx bytes; timeout)
#
# It passes when the testbench prints no MISMATCH line and reaches its
# SUMMARY.  Build products go to a scratch directory (BUILD_DIR keeps it).
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
RELAY=$HERE/../esp32_ethrelay/main

BSC=${BSC_BIN:-$(ls -d /opt/homebrew/Cellar/bsc/*/bin/bsc 2>/dev/null | sort | tail -1)}
if [ -z "$BSC" ] || [ ! -x "$BSC" ]; then
  echo "esplink_run_tests: bsc not found; set BSC_BIN" >&2
  exit 1
fi
BLUESPECDIR=$(cd "$(dirname "$BSC")/../libexec/lib" && pwd)
export BLUESPECDIR
PATH=$(dirname "$BSC"):$PATH
export PATH

BUILD=${BUILD_DIR:-$(mktemp -d "${TMPDIR:-/tmp}/hobbit-esplink.XXXXXX")}
[ -n "${BUILD_DIR:-}" ] || trap 'rm -rf "$BUILD"' EXIT
mkdir -p "$BUILD/src" "$BUILD/obj" "$BUILD/run"

cc -std=c99 -Wall -Werror -O2 -I"$RELAY" -o "$BUILD/esplink_ref" \
   "$HERE/esplink_ref.c" "$RELAY/relay.c"
python3 "$HERE/esplink_vectors.py" "$BUILD/esplink_ref" "$BUILD/run" \
    >"$BUILD/vec.log"

cp "$HERE/Sonic.bsv" "$HERE/EspLink.bsv" "$HERE/EspLinkTb.bsv" "$BUILD/src/"
(
  cd "$BUILD/src"
  bsc +RTS -K512M -RTS -sim -bdir "$BUILD/obj" -simdir "$BUILD/obj" \
      -info-dir "$BUILD/obj" -aggressive-conditions \
      -no-warn-action-shadowing -suppress-warnings G0010:G0024 \
      -g mkEspLinkTb -u EspLinkTb.bsv >"$BUILD/bsc.log" 2>&1 ||
      { cat "$BUILD/bsc.log"; exit 1; }
  bsc +RTS -K512M -RTS -sim -bdir "$BUILD/obj" -simdir "$BUILD/obj" \
      -info-dir "$BUILD/obj" -e mkEspLinkTb -o "$BUILD/sim" \
      >>"$BUILD/bsc.log" 2>&1 || { cat "$BUILD/bsc.log"; exit 1; }
)
(cd "$BUILD/run" && "$BUILD/sim" >"$BUILD/sim.log" 2>&1) || true
nmis=$(grep -c '^MISMATCH' "$BUILD/sim.log" || true)
summary=$(grep '^SUMMARY' "$BUILD/sim.log" || true)
if [ "$nmis" != 0 ] || [ -z "$summary" ]; then
  echo "FAIL esplink: $nmis mismatches (${summary:-no SUMMARY})"
  grep '^MISMATCH' "$BUILD/sim.log" | head -20
  exit 1
fi
echo "PASS esplink: $(sed 's/^esplink_vectors: //' "$BUILD/vec.log"); RTL $summary"
