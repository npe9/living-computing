#!/bin/sh
# The window box's drawing cycles (WinFbBox.bsv's header table).  OURS.
# For each mnemonic stream in bsv/win_measure/ (psi/winfb.py asm format),
# the stream is run through the WinFbBoxTb built by run_win_tb.sh, and the
# cycle count is printed less the count of `empty` (reset and the final
# dump), so each figure is the command's own.  Run run_win_tb.sh first;
# WIN_BUILD names its build directory (default build-win).  It checks
# nothing: the figures are recorded by hand in WinFbBox.bsv's header.
# No board is touched.
set -eu
cd "$(dirname "$0")"
BSC=${BSC_BIN:-}
if [ -z "$BSC" ]; then
  BSC=$(ls -d /opt/homebrew/Cellar/bsc/*/bin/bsc 2>/dev/null | sort | tail -1)
fi
PATH=$(dirname "$BSC"):$PATH
export PATH
B=${WIN_BUILD:-build-win}
[ -x "$B/sim_win" ] || { echo "win_measure: no $B/sim_win; run run_win_tb.sh first" >&2; exit 1; }
M="$B/measure"
mkdir -p "$M"
cp "$B/run/win_font.hex" "$M/win_font.hex"
SIM=$(cd "$B" && pwd)/sim_win
base=
for n in empty clear xorfill scroll glyph100 diag saverest; do
  python3 -I ../psi/winfb.py asm "win_measure/$n.txt" "$M/win_stream.hex"
  c=$(cd "$M" && "$SIM" | sed -n 's/.* commands, \([0-9]*\) cycles/\1/p')
  [ -n "$c" ] || { echo "win_measure: $n did not finish" >&2; exit 1; }
  [ -z "$base" ] && base=$c
  printf '%-9s %9d  (%d in all)  %s\n' "$n" $((c - base)) "$c" "$(grep -v '^end' "win_measure/$n.txt" | head -1)"
done
