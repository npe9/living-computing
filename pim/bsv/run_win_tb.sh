#!/bin/sh
# The window framebuffer box (WinFbBox.bsv, mkWinFbBox) against the Python
# device layer (psi/winfb.py), in Bluesim: docs/simpos/window_hardware_plan.md
# H0 and H1.  OURS scaffolding throughout (both file headers say why).
#
#   1. python3 -I psi/test_winfb.py: the reference's own unit tests
#      (hand-written bytes and dot counts, the 48-dot 'A' at 16#2341);
#   2. test_11's f822 words, read in memory from the held
#      docs/nonlocal/psdpim.tar.Z, into the bench's font load file;
#   3. bsc builds mkWinFbBoxTb (WinFbBoxTb.bsv) into $WIN_BUILD;
#   4. for every stream `psi/winfb.py streams` names (directed ones and
#      random ones with fixed seeds), the stream is run by both sides and
#      the PBM files (one P4 image per `dump` and one at `end`) and the
#      status files (one status a command) are compared with cmp.
# Everything goes to bsv/build-win/ (WIN_BUILD to override; the root
# .gitignore's build-*/ covers it).  BSC_BIN pins a compiler, as in
# run_fepemu.sh.  No board is touched.
#
# INJECTED FAULTS (AGENTS.md "How work is verified here" 2), each made in
# WinFbBox.bsv from a backup copy, built into a separate WIN_BUILD, then
# undone by copying the backup back (cmp clean, git diff empty).  The
# OBSERVED mismatching streams (PBM and/or status) were:
#   (filled in below from the runs of 2026-11-25)
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

B=${WIN_BUILD:-build-win}
WINFB=../psi/winfb.py
mkdir -p "$B/run"

echo "== psi/test_winfb.py (the Python reference's unit tests)"
python3 -I ../psi/test_winfb.py 2> "$B/test_winfb.log" || { cat "$B/test_winfb.log"; exit 1; }
tail -1 "$B/test_winfb.log"

echo "== test_11.font from the held psdpim archive -> the font load file"
python3 -I "$WINFB" fonthex "$B/run/win_font.hex"

echo "== bsc: mkWinFbBoxTb"
FLAGS="-steps-warn-interval 4000000 -bdir $B -simdir $B -info-dir $B"
"$BSC" -sim -u -g mkWinFbBoxTb $FLAGS WinFbBoxTb.bsv > "$B/bsc.log" 2>&1 || { cat "$B/bsc.log"; exit 1; }
(cd "$B" && "$BSC" -sim -e mkWinFbBoxTb -bdir . -simdir . -o sim_win > link.log 2>&1) || { cat "$B/link.log"; exit 1; }

status=0
for name in $(python3 -I "$WINFB" streams | awk '{print $1}'); do
  python3 -I "$WINFB" gen "$name" > "$B/$name.hex"
  python3 -I "$WINFB" run "$B/$name.hex" "$B/$name.py.pbm" "$B/$name.py.status"
  cp "$B/$name.hex" "$B/run/win_stream.hex"
  rm -f "$B/run/win_frame.pbm" "$B/run/win_status.txt"
  (cd "$B/run" && ./../sim_win > sim.log 2>&1) || { cat "$B/run/sim.log"; status=1; continue; }
  cp "$B/run/win_frame.pbm" "$B/$name.bsv.pbm"
  cp "$B/run/win_status.txt" "$B/$name.bsv.status"
  n=$(grep -c . "$B/$name.py.status" || true)
  imgs=$(( $(wc -c < "$B/$name.py.pbm") / 163853 ))
  cyc=$(sed -n 's/.* commands, \([0-9]*\) cycles/\1/p' "$B/run/sim.log")
  if cmp -s "$B/$name.py.pbm" "$B/$name.bsv.pbm" && cmp -s "$B/$name.py.status" "$B/$name.bsv.status"; then
    echo "   same  $name: $n commands, $imgs PBM images, $cyc cycles"
  else
    echo "   DIFFERS $name: $n commands, $imgs images (cmp $B/$name.py.pbm $B/$name.bsv.pbm; status files likewise)"
    status=1
  fi
done
if [ $status -ne 0 ]; then
  echo "run_win_tb: FAIL"
  exit 1
fi
echo "run_win_tb: PASS"
