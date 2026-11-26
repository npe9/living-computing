#!/bin/sh
# The window host link (WinLink.bsv, mkWinLink) against tools/winlink.py, in
# Bluesim: docs/simpos/window_hardware_plan.md H6, its RTL half.  ALL OURS.
#
#   1. python3 -I tools/winlink.py selftest (the CRC's check value
#      0x29b1, the receiver model on a lost byte and a bad LEN);
#   2. bsc builds mkWinLinkTb (WinLinkTb.bsv: a host on both UART lines,
#      4 clock cycles a bit, the box behind the link);
#   3. for each case, a psi/winfb.py stream is encoded into frames
#      (winlink.py encode, a final dump appended, maybe a line fault
#      injected), sent down the line, and everything read back up is
#      judged by winlink.py check: every record's CRC, the error records
#      (= the receiver model's), the statuses (= psi/winfb.py's for the
#      commands the model accepts) and every dump (= psi/winfb.py's frame).
# The line faults are the plan's §4 injection "drop one byte: the CRC
# failure is reported, not drawn", plus a flipped bit and a bad LEN; each
# case's expected error records come from the model, so the check fails
# if the board reports more, fewer or other errors, or draws a dropped
# frame.  Build in $WIN_BUILD/link (default build-win/link).  No board.
#
# INJECTED FAULTS in WinLink.bsv, each in a private copy of pim/bsv, pim/psi
# and pim/tools (the tree's files never edited).  OBSERVED 2026-11-26; every
# case not listed passed:
#   L1 the frame CRC never checked: drop (error records [(3, 6)] for
#      [(1, 5), (3, 5)]: the cut frame was drawn), flip (none reported)
#   L2 no sequence check: drop, flip, badlen (each lacks its SEQ error)
#   L3 a frame that fails its CRC still drawn (its error still sent): drop,
#      flip (the statuses carry the bad frame's)
#   L4 the receiver's bits taken MSB first (the bench's host receiver is
#      the same module, so both ends): all 6 (5 end in the bench's
#      "no end after 200000000 cycles"; xor_twice's up bytes do not parse)
#   L5 the data record's word bytes low first: all 6 (dump 0 differs)
#   L6 the hunt takes any byte as a frame start: drop, badlen (a LEN error
#      at every byte until a frame lines up again); a clean stream never
#      hunts, so the clean cases and flip (one whole bad frame) pass
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

B=${WIN_BUILD:-build-win}/link
WINFB=../psi/winfb.py
LINK=../tools/winlink.py
mkdir -p "$B/run"

echo "== tools/winlink.py selftest"
python3 -I "$LINK" selftest
python3 -I "$WINFB" fonthex "$B/run/win_font.hex"

echo "== bsc: mkWinLinkTb"
"$BSC" -sim -u -g mkWinLinkTb -steps-warn-interval 4000000 -bdir "$B" -simdir "$B" -info-dir "$B" \
  WinLinkTb.bsv > "$B/bsc.log" 2>&1 || { cat "$B/bsc.log"; exit 1; }
(cd "$B" && "$BSC" -sim -e mkWinLinkTb -bdir . -simdir . -o sim_link > link.log 2>&1) || { cat "$B/link.log"; exit 1; }

# name:stream:encode options (byte numbers: a frame is 18 bytes)
CASES="glyphs:glyphs: lines:lines: xor_twice:xor_twice: drop:glyphs:--drop_100 flip:glyphs:--flip_300 badlen:glyphs:--flip_56"
status=0
for c in $CASES; do
  name=${c%%:*}; rest=${c#*:}; stream=${rest%%:*}; opts=$(echo "${rest#*:}" | tr '_' ' ')
  python3 -I "$WINFB" gen "$stream" > "$B/$name.stream"
  # shellcheck disable=SC2086
  python3 -I "$LINK" encode "$B/$name.stream" "$B/run/win_link_in.hex" $opts
  printf '%x\n' "$(grep -c . "$B/run/win_link_in.hex")" > "$B/run/win_link_n.hex"
  rm -f "$B/run/win_link_out.hex"
  (cd "$B/run" && ./../sim_link > sim.log 2>&1) || true
  if ! grep -q "^WinLinkTb: .* answers" "$B/run/sim.log"; then
    echo "   DIFFERS $name: $(grep -v '^Warning' "$B/run/sim.log" | head -1)"
    status=1; continue
  fi
  cp "$B/run/win_link_in.hex" "$B/$name.in.hex"; cp "$B/run/win_link_out.hex" "$B/$name.out.hex"
  if r=$(python3 -I "$LINK" check "$B/$name.in.hex" "$B/$name.out.hex"); then
    echo "   same  $name ($stream${opts:+ $opts}): ${r#winlink check: }; $(sed -n 's/^WinLinkTb: //p' "$B/run/sim.log")"
  else
    echo "   DIFFERS $name: $r"; status=1
  fi
done
if [ $status -ne 0 ]; then
  echo "run_win_link: FAIL"
  exit 1
fi
echo "run_win_link: PASS"
