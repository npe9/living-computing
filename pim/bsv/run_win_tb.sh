#!/bin/sh
# The window framebuffer box (WinFbBox.bsv, mkWinFbBox) against the Python
# device layer (psi/winfb.py), in Bluesim: docs/simpos/window_hardware_plan.md
# H0 and H1; then the scan-out (WinScanOut.bsv, mkWinScanOut) against
# psi/winscan.py and psi/wintmds.py, H2 (steps 5-8 below).  OURS scaffolding throughout (both file headers say why).
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
# run_fepemu.sh.  WIN_PART=h2 skips step 4 (for scan-out injection runs).
# No board is touched.
#
# INJECTED FAULTS (AGENTS.md "How work is verified here" 2), each made in
# WinFbBox.bsv from a backup copy, built into a separate WIN_BUILD, then
# undone by copying the backup back (cmp clean, git diff empty).  The
# OBSERVED mismatching streams (PBM and/or status), 2026-11-25; every
# stream not listed stayed byte-identical:
#   1 bit order (the dump sends words LSB-leftmost; plan §4 (1)):
#       all 11
#   2 exclusive_or acts as set (plan §4 (2)): all 11
#   3 glyph record x and y swapped (plan §4 (3)):
#       glyphs, rand_h1_1, rand_h1_2
#   4 the fill's right-edge mask one dot short (plan §4 (4)):
#       all but lines (10)
#   5 copy: the source's last word one short (jHi = (sx+w-2)>>4):
#       copy_overlap, rand_h0_1, rand_h0_2, rand_h0_3, rand_h1_2
#   6 restore draws with the slot's x and y swapped:
#       save_restore, rand_h0_1..3, rand_h1_1, rand_h1_2
#   7 overlapping copy, rows always top-down:
#       copy_overlap, rand_h0_1..3, rand_h1_1, rand_h1_2
#   8 overlapping copy, words always left to right:
#       copy_overlap, rand_h0_2
#   9 line: Bresenham's x step on e2 > dy, not >=:
#       lines, rand_h1_1, rand_h1_2
#  10 save: the overflow check one word short (need >= size):
#       save_restore, rand_h1_2
# A first pass missed 5 and 6 in the directed streams (only the random
# ones caught them: save_restore saved at x = y, copy_overlap had no
# source ending on a word's first dot); both streams were then changed
# and every injection re-run, giving the sets above.
#
# H2, the scan-out (WinScanOut.bsv; plan §2.2, §2.6, §4):
#   5. python3 -I psi/test_winscan.py: the TMDS and scan-out references'
#      unit tests (DVI 1.0's printed control characters and its "460
#      unique" data characters, hand-worked encodings, the drm_edid.c
#      mode lines);
#   6. WinTmdsEncTb: mkWinTmdsEnc on psi/winscan.py `encvec 1` (every byte
#      from every disparity state, constant runs, random data with blanking
#      bursts), each character = wintmds.encode, running disparity <= 8;
#   7. WinTmdsSerTb: mkWinTmdsSer, the pixel clock = the bench clock / 5;
#      every lane carries the encoders' characters at the clock lane's
#      boundary and one latency;
#   8. WinScanOutTb, for every `winscan.py cases` case: the stream drawn,
#      the frame dumped (= the Python layer's PBM), one frame + 2-3 lines
#      captured from the frame-start mark, the frame dumped again (= the
#      same PBM: the cursor never enters it); `winscan.py check` decodes
#      every clock (DVI 1.0 Fig. 3-6) against the timing model and the
#      view (sync levels, DE, pixels, equal channels, CTL = 0 on channels
#      1 and 2, the frame mark once, the cursor move landing at the next
#      frame), bounds the running disparity, and re-encodes the expected
#      stream with wintmds.encode, which must equal the capture.
#
# H2 INJECTED FAULTS, each made in a private copy of the pim files in a
# scratch directory (the tree's files were never edited), run with
# WIN_PART=h2.  OBSERVED, 2026-11-25; the encoder bench (enc), the
# serializer bench (ser) and the 17 scan cases (mode0-3, mode2_nocursor,
# rand1-12); everything not listed stayed `same`:
#  1 hsync one dot late (hsA from ha + hf + 1): all 17 scan cases
#    (C1C0 differs from the timing model at the sync start); enc, ser same
#  2 disparity update: cnt += bal whatever q_m[8] (first branch): enc and
#    all 17 scan cases (the running-disparity bound; pixels decode right)
#  3 disparity branch flipped ((cnt > 0 && bal < 0) || ...): enc and all
#    17 (disparity 40 > 8)
#  4 control characters for C1C0 = 01 and 10 swapped: enc and all 17
#  5 pixel bit order (dot 15 - k -> k, 1:1 path): mode0, mode1, mode2,
#    mode2_nocursor, rand2-5, rand7, rand8, rand10 (the 2:1 cases,
#    mode3, rand6, rand9, rand11, rand12, use the other path; rand1's
#    window shows no ink)
#  6 cursor mask ignored (the image drawn over the whole 16 x 16): mode0-3,
#    rand1-6, rand8, rand9, rand11
#  7 cursor x one pixel off: mode0-3, rand1-6, rand8, rand9, rand11
#  8 mode 0's letterbox x0 321 (the BSV table only): mode0
#  9 2:1 fetch reads one row twice (rowB = rA): mode3, rand6, rand9,
#    rand11, rand12 (all the 2:1 cases)
# 10 serializer D0/D1 swapped: ser
# 11 cursor position not latched at the frame start (pending used at
#    once): mode2, rand1-4, rand6, rand8, rand10-12 (the move lands
#    mid-frame)
# 12 the word queue's dequeue misses a window cut by the active area's end
#    (no lineEnd): rand1, rand2, rand8 ("WinScanOut: word queue overflow")
# 13 vsync polarity ignored: mode2, mode3, mode2_nocursor, rand1, rand4,
#    rand6, rand8, rand10 (the -V cases)
# 14 serializer samples the pixel word on ph[4], not ph[2]: NOTHING fails.
#    With ideal phase-locked clocks every sample phase gives a consistent
#    stream; only a timing constraint (H3) can see a sample on the edge
#    where the word changes.  Recorded, not caught.
# 15 serializer shifts 1 bit a shift clock, not 2: ser
# 16 one lane's load flag a shift clock late (lane 1 from ph[4]; the
#    plan's "a lane's load phase off by one"): ser
# "The cursor drawn into the frame" cannot be injected: the scan-out has
# only the read port; the second dump is the check that it stays out.
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
H01=$(python3 -I "$WINFB" streams | awk '{print $1}')
[ "${WIN_PART:-}" = h2 ] && H01=          # WIN_PART=h2: the scan-out only (injection runs)
for name in $H01; do
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

# ---- H2: the scan-out (WinScanOut.bsv) against psi/winscan.py, wintmds.py
echo "== psi/test_winscan.py (the TMDS and scan-out references' unit tests)"
python3 -I ../psi/test_winscan.py 2> "$B/test_winscan.log" || { cat "$B/test_winscan.log"; exit 1; }
tail -1 "$B/test_winscan.log"
WINSCAN=../psi/winscan.py
for tb in mkWinTmdsEncTb:WinTmdsEncTb.bsv:sim_enc mkWinTmdsSerTb:WinTmdsSerTb.bsv:sim_ser mkWinScanOutTb:WinScanOutTb.bsv:sim_scan; do
  top=${tb%%:*}; rest=${tb#*:}; src=${rest%%:*}; exe=${rest#*:}
  echo "== bsc: $top"
  "$BSC" -sim -u -g "$top" $FLAGS "$src" > "$B/bsc_$exe.log" 2>&1 || { cat "$B/bsc_$exe.log"; exit 1; }
  (cd "$B" && "$BSC" -sim -e "$top" -bdir . -simdir . -o "$exe" > "link_$exe.log" 2>&1) || { cat "$B/link_$exe.log"; exit 1; }
done

mkdir -p "$B/enc" "$B/ser"
python3 -I "$WINSCAN" encvec 1 > "$B/enc/win_tmds_in.hex"
(cd "$B/enc" && ./../sim_enc > sim.log 2>&1) || { cat "$B/enc/sim.log"; status=1; }
grep -q "^WinTmdsEncTb: [0-9]* characters" "$B/enc/sim.log" || { echo "   DIFFERS tmds encoder bench:"; cat "$B/enc/sim.log"; status=1; }
if r=$(python3 -I "$WINSCAN" enccheck "$B/enc/win_tmds_in.hex" "$B/enc/win_tmds_out.hex"); then
  echo "   same  tmds encoder: $r"
else
  echo "   DIFFERS tmds encoder: $r"; status=1
fi
(cd "$B/ser" && ./../sim_ser > sim.log 2>&1) || { cat "$B/ser/sim.log"; status=1; }
grep -q "^WinTmdsSerTb: [0-9]* shift clocks" "$B/ser/sim.log" || { echo "   DIFFERS serializer bench:"; cat "$B/ser/sim.log"; status=1; }
if r=$(python3 -I "$WINSCAN" sercheck "$B/ser/win_ser_px.hex" "$B/ser/win_ser.bin"); then
  echo "   same  serializer: $r"
else
  echo "   DIFFERS serializer: $r"; status=1
fi

for name in $(python3 -I "$WINSCAN" cases); do
  python3 -I "$WINSCAN" stream "$name" > "$B/scan_$name.hex"
  python3 -I "$WINFB" run "$B/scan_$name.hex" "$B/scan_$name.py.pbm" "$B/scan_$name.py.status"
  cp "$B/scan_$name.hex" "$B/run/win_stream.hex"
  python3 -I "$WINSCAN" config "$name" > "$B/run/win_scan.hex"
  rm -f "$B/run/win_frame.pbm" "$B/run/win_frame2.pbm" "$B/run/win_tmds.bin"
  (cd "$B/run" && ./../sim_scan > sim_scan.log 2>&1) || { cat "$B/run/sim_scan.log"; status=1; continue; }
  if ! grep -q "^WinScanOutTb: drawn" "$B/run/sim_scan.log"; then
    # Bluesim's $finish(1) exits 0: the bench's or the RTL's own message
    echo "   DIFFERS scan $name: $(grep -v '^Warning' "$B/run/sim_scan.log" | head -1)"
    status=1; continue
  fi
  if ! cmp -s "$B/scan_$name.py.pbm" "$B/run/win_frame.pbm" || \
     ! cmp -s "$B/scan_$name.py.pbm" "$B/run/win_frame2.pbm"; then
    echo "   DIFFERS scan $name: the frame before or after the scan is not the Python layer's"
    status=1; continue
  fi
  if r=$(python3 -I "$WINSCAN" check "$name" "$B/scan_$name.py.pbm" "$B/run/win_tmds.bin"); then
    echo "   same  scan $r"
  else
    echo "   DIFFERS scan $name: $r"; status=1
  fi
done

if [ $status -ne 0 ]; then
  echo "run_win_tb: FAIL"
  exit 1
fi
echo "run_win_tb: PASS"
