#!/bin/sh
# The window input box (WinInput.bsv, mkWinInput) at the wire level against
# tools/wininput.py, in Bluesim: docs/simpos/window_hardware_plan.md H5,
# §3.3 (2).  ALL OURS.
#
#   1. python3 -I tools/wininput.py selftest (the model on a few keys and a
#      click), jischeck (the §3.1 table's JIS = psi/kl0.py Str's for all
#      of printing ASCII) and --check bsv/WinKeyTable.bsv (the generated
#      table is the generator's);
#   2. bsc builds mkWinInputTb (scaled timing: a PS/2 bit 12 cycles) and
#      mkWinInputTbBoard (the board's: a bit 2,000 cycles at 25 MHz, the
#      receiver's filter and timeout at their board values);
#   3. each script of win_input/ becomes the two devices' byte streams
#      (wininput.py bytes: the HOST table, HID usage to set 2) and the
#      records the receivers must emit (wininput.py expect: the receivers'
#      model through the KEYS table, §3.1); the bench clocks the bytes into
#      the pins by mkWinPs2Dev and writes the records; wininput.py compare
#      judges them, per device, in order, every field but the time stamp
#      (which must not go backwards).
#   keys    every printing key unshifted and shifted, the named keys, F1-F12,
#           Shift-F1..F7 (pf#12-18) and Shift-F8 (pf#7), Pause (abort),
#           Ctrl-J (lf), Ctrl-G (bell), Ctrl-A, Alt-X
#   mouse   moves, past every edge (clamped), each button
#   faults  a parity error, a bad stop bit, a frame cut off, an unknown code
#           with and without E0, on the keyboard; a packet without bit 3, a
#           parity error and a cut frame on the mouse; good keys and clicks
#           between them (a fault must cost only its own byte or packet)
#   board   `keys` again on mkWinInputTbBoard
# Build in $WIN_BUILD/input (default build-win/input).  No board.
#
# INJECTED FAULTS, each in a private copy of pim/bsv and pim/tools (the
# tree's files never edited).  OBSERVED 2026-11-26; every case not listed
# passed:
#   I1 make/break swapped (a key's record on its break; plan §4's
#      injection): keys, board (a typematic x x x gives one x, and Shift
#      released before Q gives q, not Q). A first `keys` without held keys
#      PASSED this injection, so `down`/`up` were added to the script.
#   I2 parity never checked: faults (a parity error read as the byte)
#   I3 stop bit never checked: faults
#   I4 no timeout (a cut frame never reported): faults (the next frame's
#      bits join it: a stop error, then 4 records too many)
#   I5 bits taken MSB first: all 4
#   I6 the E0 prefix ignored: keys, board (keypad Enter read as cr)
#   I7 Shift ignored: keys, board
#   I8 the mouse's Y not inverted: mouse, faults
#   I9 the mouse position not clamped: mouse
#   I10 no check of the packet's sync bit 3: faults
#   I11 no clock filter: faults (a one-cycle glitch read as an edge; a
#      first `faults` without glitches PASSED it, so glitch faults were added)
set -eu
cd "$(dirname "$0")"

BSC=${BSC_BIN:-}
if [ -z "$BSC" ]; then
  BSC=$(ls -d /opt/homebrew/Cellar/bsc/*/bin/bsc 2>/dev/null | sort | tail -1)
fi
[ -n "$BSC" ] && [ -x "$BSC" ] || { echo "bsc not found; set BSC_BIN" >&2; exit 1; }
BLUESPECDIR=$(cd "$(dirname "$BSC")/../libexec/lib" && pwd)
export BLUESPECDIR
PATH=$(dirname "$BSC"):$PATH
export PATH

B=${WIN_BUILD:-build-win}/input
IN=../tools/wininput.py
mkdir -p "$B/run"

echo "== tools/wininput.py selftest, jischeck, --check WinKeyTable.bsv"
python3 -I "$IN" selftest
python3 -I "$IN" jischeck
python3 -I "$IN" --check WinKeyTable.bsv

echo "== bsc: mkWinInputTb, mkWinInputTbBoard"
for top in mkWinInputTb mkWinInputTbBoard; do
  "$BSC" -sim -u -g $top -bdir "$B" -simdir "$B" -info-dir "$B" WinInputTb.bsv > "$B/bsc_$top.log" 2>&1 \
    || { cat "$B/bsc_$top.log"; exit 1; }
  (cd "$B" && "$BSC" -sim -e $top -bdir . -simdir . -o sim_$top > link_$top.log 2>&1) \
    || { cat "$B/link_$top.log"; exit 1; }
done

status=0
for c in keys:mkWinInputTb mouse:mkWinInputTb faults:mkWinInputTb board:mkWinInputTbBoard; do
  name=${c%%:*}; top=${c#*:}
  script=win_input/$name.txt
  [ "$name" = board ] && script=win_input/keys.txt
  python3 -I "$IN" bytes "$script" "$B/run/win_kbd.hex" "$B/run/win_mouse.hex" "$B/run/win_input_n.hex" > "$B/$name.bytes"
  python3 -I "$IN" expect "$script" "$B/$name.want"
  rm -f "$B/run/win_input_out.txt"
  (cd "$B/run" && "../sim_$top" > sim.log 2>&1) || true
  if ! grep -q "^WinInputTb: .* records" "$B/run/sim.log"; then
    echo "   DIFFERS $name: $(grep -v '^Warning' "$B/run/sim.log" | head -1)"
    status=1; continue
  fi
  cp "$B/run/win_input_out.txt" "$B/$name.got"
  if r=$(python3 -I "$IN" compare "$B/$name.want" "$B/$name.got"); then
    echo "   same  $name: ${r#wininput compare: }; $(sed -n 's/^wininput bytes: //p' "$B/$name.bytes") bytes; $(sed -n 's/^WinInputTb: //p' "$B/run/sim.log")"
  else
    echo "   DIFFERS $name: $r"; status=1
  fi
done
if [ $status -ne 0 ]; then
  echo "run_win_input: FAIL"
  exit 1
fi
echo "run_win_input: PASS"
