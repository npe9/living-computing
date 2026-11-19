#!/bin/sh
# Prove the FPGA top's UART output end to end in Bluesim.
#
# BoardUartTb mirrors mkHobbitUlx3s's datapath (see its header) and decodes
# its txd line as 8N1 at 217 clocks/bit.  The decoded text must equal the
# smoke test's 41 HRI lines byte for byte; the smoke run itself is the
# reference, so the comparison is between two independently built
# simulations of the same image, not against a stored file.
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

# The image is a build product, as for the smoke test.
python3 mk_image_bsv.py smoke.hex SmokeImage > SmokeImage.bsv

"$BSC" +RTS -K512M -RTS -sim -g mkBoardTb -u BoardUartTb.bsv
"$BSC" +RTS -K512M -RTS -sim -e mkBoardTb -o sim_board

ref=$(./run_smoke.sh 2>/dev/null | grep '^HRI ' || true)
hris=$(printf '%s\n' "$ref" | grep -c '^HRI ' || true)
if [ "$hris" -ne 41 ]; then
  echo "run_board_tb: smoke gave $hris HRI lines, want 41" >&2
  exit 1
fi

board=$(./sim_board | python3 -c '
import sys
bs = [int(l.split()[1], 16) for l in sys.stdin if l.startswith("RXB ")]
sys.stdout.write("".join(chr(b) for b in bs))
')

if [ "$board" != "$ref" ]; then
  echo "run_board_tb: FAIL -- UART text differs from the smoke HRI lines" >&2
  printf '%s\n' "$board" | head -3 >&2
  printf '%s\n' "$ref" | head -3 >&2
  exit 1
fi

bytes=$(printf '%s' "$board" | wc -c | tr -d ' ')
echo "board UART: 41 lines, $bytes bytes byte-identical to the smoke HRI"
