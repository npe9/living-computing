#!/bin/sh
# The window framebuffer box (WinFbBox.bsv, mkWinFbBox) against the Python
# device layer (psi/winfb.py), in Bluesim: docs/simpos/window_hardware_plan.md
# H0 and H1; then the scan-out (WinScanOut.bsv, mkWinScanOut) against
# psi/winscan.py and psi/wintmds.py, H2 (steps 5-8 below); then the board
# design's core in three clock domains, H3 (step 9); then the host link,
# H6 (step 10, run_win_link.sh).  OURS scaffolding throughout (both file
# headers say why).
#
#   1. python3 -I psi/test_winfb.py: the reference's own unit tests
#      (hand-written bytes and dot counts, the 48-dot 'A' at 16#2341);
#   2. test_11's f822 words, read in memory from the held
#      docs/nonlocal/psdpim.tar.Z, into the bench's font load file;
#   3. bsc builds mkWinFbBoxTb (WinFbBoxTb.bsv) into $WIN_BUILD;
#   4. for every stream `psi/winfb.py streams` names (directed ones and
#      random ones with fixed seeds), the stream is run by both sides and
#      the PBM files (one P4 image per `dump` and one at `end`) and the
#      status files (one status a command) are compared with cmp; and so
#      for each directed mnemonic stream win_streams/*.txt (assembled by
#      psi/winfb.py asm), with the bench's +stall (it takes no response 3
#      cycles in 8, so the box's queues and credits fill): pipe.txt drives
#      the pipelined stages (H3 follow-up);
#  10. run_win_link.sh (its own header).
#  11. run_win_input.sh (H5, its own header).
#  12. run_win_live.sh (H7s, its own header).
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
#   7. WinTmdsSerTb: mkWinTmdsSer, the pixel clock = the bench clock / 5
#      with offset K, built for K = 0..4 (H3: the five alignments of the
#      pixel clock to the shift clock), the pixel word and `tog` through
#      WinCrossModel (garbage when sampled on the shift edge where the word
#      changes or on the one before the next change); every lane carries the encoders'
#      characters at the clock lane's boundary and one latency;
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
#    where the word changes.  Recorded, not caught (H2).  CAUGHT since H3:
#    see injections H3-1 and H3-8 below, and the pclk -> sclk check of
#    run_win_fpga.sh.
# 15 serializer shifts 1 bit a shift clock, not 2: ser
# 16 one lane's load flag a shift clock late (lane 1 from ph[4]; the
#    plan's "a lane's load phase off by one"): ser
#
# H3, the board design (WinFrame.bsv, WinUlx3s.bsv; plan §5):
#   9. WinUlx3sTb: mkWinCore (the box with the banked two-clock frame, the
#      scan-out behind a sync FIFO in the pixel domain, the self-test FSM
#      drawing winscan.py's mode 0 stream from a load file) on three
#      clocks (system period 27, pixel 10, shift 2), the serializer behind
#      null crossings and WinCrossModel; checks the self-test's frame
#      dumped through the debug port (= the Python PBM), one whole mode 0
#      frame of characters (winscan.py check), and lines 58-60 of serial
#      bits (sercheck).
# H3 INJECTED FAULTS, each in a private copy of pim/bsv and pim/psi in a
# scratch directory (the tree's files never edited); OBSERVED 2026-11-25,
# everything not listed `same`:
#  H3-1 serializer sample enable from phase bit 1 (WinSerSmp = 1, sample
#    age 4) or bit 2 (age 0, the edge where the word changes), WIN_PART=h2:
#    ser K=0..4 and ulx3s serializer ("the logged characters appear at 0
#    latencies"); bits 0 and 3 (ages 1-3 are safe) PASS, as predicted
#  H3-2 free-running phase (e ignored: phn = rotate ph), WIN_PART=h2: ser
#    K=0..4 and ulx3s serializer ("0 boundaries give a steady clock
#    character": the un-reset phase starts at Bluesim's 'hAA.. pattern,
#    not one-hot, and nothing restarts it)
#  H3-2b free-running phase that starts one-hot (ph given the reset):
#    ser K=0 and K=1 and ulx3s serializer fail ("0 latencies"), K=2, 3, 4
#    pass: the K sweep separates good alignments from bad ones
#  H3-3 port B latency claimed 5, not 4 (WinFrameLatB), WIN_PART=h2: all
#    scan cases but rand1 (no ink in its window) and ulx3s scan
#  H3-4 port B's second mux level from the wrong address bits (h[bk1[6:3]]
#    for h[bk2]), WIN_PART=h2: mode0-3, mode2_nocursor, rand4, rand7,
#    rand8, rand9, rand12, ulx3s scan
#  H3-5 port A's read mux select stuck at bank 0 (selA <= 0): all 11
#    H0/H1 streams, all 17 scan cases (the frame dump), ulx3s frame and
#    ulx3s scan
#  H3-6 (SUPERSEDED by P8 below: the wait is gone since the H3 follow-up)
#    the line engine's frame-read wait dropped (no fWait in lineDot):
#    lines, rand_h1_1, rand_h1_2, all 17 scan cases (their streams draw
#    lines), ulx3s frame and scan (self-test done 1,914 cycles early)
#  H3-7 the pixel domain drops the cursor-shape command (SShape ->
#    noAction in mkWinScanPix's dispatch): ulx3s scan only (the H2 bench
#    drives mkWinScanOut directly)
#  H3-8 = H3-1 (bit 1) with WinCrossModel's `unsafe` forced False: PASS.
#    Without the crossing model nothing sees the sample phase; the model is
#    the check, and run_win_fpga.sh's pclk -> sclk delay check is what
#    justifies its window (a sample at age 1-3 is safe when the delay is
#    under one shift period).
# run_win_fpga.sh's checker (tools/win_fpga_check.py) was seen to fail on
# a clock below its frequency (sclk 367.11 at 370.10, seed 2, during the
# build-up), on a DP16KD count other than the expected (157 expected, 156
# built) and on the pclk -> sclk budget (WIN_XDOM_NS=1.0).
# "The cursor drawn into the frame" cannot be injected: the scan-out has
# only the read port; the second dump is the check that it stays out.
# H3 follow-up INJECTED FAULTS (the pipelined engines, WinMemPipe.bsv and
# WinFbBox.bsv), each in a private copy of pim/bsv, pim/psi and pim/tools
# (the tree's files never edited); OBSERVED 2026-11-26 at the final tree,
# everything not listed `same`.  "link" cases are step 10's (run_win_link.sh):
#  P1 a frame response dropped (a read's tag lost when another read follows
#    the next cycle): all 12 box streams, then the first scan case
#    (mode0) never ends: the 1500 s timeout (exit 124), as the scan bench
#    has no watchdog
#  P2 the two response ports swapped: all 12 box streams, then as P1 (scan
#    mode0 never ends, exit 124)
#  P3 the read-modify-write address interlock removed (rReadFrame without
#    !pq.has): rand_h1_1, rand_h1_2, pipe; scan rand1, 2, 3, 5, 6, 7, 9, 11
#  P4 the credit limit one high (cnt <= depth): pipe (only under +stall,
#    which is why the bench stalls its reader) and link glyphs, lines,
#    xor_twice, drop, flip, badlen (the UART back-pressures the box; drop,
#    flip and badlen end in the pipe's own "read on port 0 without a credit")
#  P5 the row's first source word not loaded (the carry runs on from the
#    previous row): copy_overlap, save_restore, rand_h0_1-3, glyphs,
#    rand_h1_1-2, pipe; all 17 scan; ulx3s frame and scan; link glyphs,
#    drop, flip, badlen
#  P6 no drain (the command ends when its last word enters the
#    read-modify-write stage): fill_edges, copy_overlap,
#    save_restore, rand_h0_1-3, rand_h1_1-2; scan mode0-3, mode2_nocursor,
#    rand1-4; the 1500 s timeout came during scan rand5
#  P7 right to left, the carried word's role not flipped: copy_overlap,
#    rand_h1_2, pipe
#  P8 the frame pipe's latency one short (supersedes H3-6): all 12 box
#    streams; all 17 scan; ulx3s frame and scan; all 6 link cases
#  P9 the line merge drops each dot merged into a word after its first
#    (mHas ? mMask : d.bits): lines, rand_h1_1, rand_h1_2, pipe;
#    all 17 scan; ulx3s frame and scan; link lines
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
# and the directed mnemonic streams of this directory (f:NAME = win_streams/NAME.txt)
H01="$H01 $(cd win_streams && ls *.txt | sed 's/^/f:/; s/\.txt$//')"
[ "${WIN_PART:-}" = h2 ] && H01=          # WIN_PART=h2: the scan-out only (injection runs)
for name in $H01; do
  case $name in
    f:*) name=${name#f:}; args=+stall
         python3 -I "$WINFB" asm "win_streams/$name.txt" "$B/$name.hex" ;;
    *)   args=
         python3 -I "$WINFB" gen "$name" > "$B/$name.hex" ;;
  esac
  python3 -I "$WINFB" run "$B/$name.hex" "$B/$name.py.pbm" "$B/$name.py.status"
  cp "$B/$name.hex" "$B/run/win_stream.hex"
  rm -f "$B/run/win_frame.pbm" "$B/run/win_status.txt"
  (cd "$B/run" && ./../sim_win $args > sim.log 2>&1) || { cat "$B/run/sim.log"; status=1; continue; }
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
for tb in mkWinTmdsEncTb:WinTmdsEncTb.bsv:sim_enc mkWinTmdsSerTb:WinTmdsSerTb.bsv:sim_ser mkWinScanOutTb:WinScanOutTb.bsv:sim_scan mkWinUlx3sTb:WinUlx3sTb.bsv:sim_ulx3s; do
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
BABS=$(cd "$B" && pwd)
for k in 0 1 2 3 4; do
  # K: the pixel clock's offset against the shift clock (all five
  # alignments of a phase that runs free from time 0 to the pixel clock);
  # K = 0 is the sim_ser built above
  SER="$BABS/sim_ser"
  if [ $k -ne 0 ]; then
    mkdir -p "$B/serk$k"
    "$BSC" -sim -u -g mkWinTmdsSerTb -D SER_K=$k -steps-warn-interval 4000000 -p "$BABS:+" \
      -bdir "$B/serk$k" -simdir "$B/serk$k" -info-dir "$B/serk$k" WinTmdsSerTb.bsv > "$B/serk$k/bsc.log" 2>&1 || { cat "$B/serk$k/bsc.log"; exit 1; }
    (cd "$B/serk$k" && "$BSC" -sim -e mkWinTmdsSerTb -p "$BABS:+" -bdir . -simdir . -o sim_ser > link.log 2>&1) || { cat "$B/serk$k/link.log"; exit 1; }
    SER="$BABS/serk$k/sim_ser"
  fi
  (cd "$B/ser" && "$SER" > sim.log 2>&1) || { cat "$B/ser/sim.log"; status=1; }
  grep -q "^WinTmdsSerTb: [0-9]* shift clocks" "$B/ser/sim.log" || { echo "   DIFFERS serializer bench:"; cat "$B/ser/sim.log"; status=1; }
  if r=$(python3 -I "$WINSCAN" sercheck "$B/ser/win_ser_px.hex" "$B/ser/win_ser.bin"); then
    echo "   same  serializer K=$k: $r"
  else
    echo "   DIFFERS serializer K=$k: $r"; status=1
  fi
done

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

# ---- H3: the board design's core in three clock domains (WinUlx3sTb)
echo "== WinUlx3sTb: mkWinCore + mkWinTmdsSer, sys / pclk / sclk (the board's self-test, mode0)"
U="$B/ulx3s"
mkdir -p "$U"
cp "$B/run/win_font.hex" "$U/win_font.hex"
python3 -I "$WINSCAN" stream mode0 > "$U/win_stream.hex"
python3 -I "$WINSCAN" config mode0 > "$U/win_scan.hex"
python3 -I "$WINFB" run "$U/win_stream.hex" "$U/py.pbm" "$U/py.status"
# the serializer window: 3 lines from line 58 (frame rows 30-32: the
# test card's non-periodic dots, both edges and the diagonals)
printf '%08x\n%08x\n' $((58 * 2200)) $((3 * 2200)) > "$U/win_ulx3s_tb.hex"
rm -f "$U/win_frame.pbm" "$U/win_tmds.bin" "$U/win_ser.bin" "$U/win_ser_px.hex"
if (cd "$U" && ./../sim_ulx3s > sim.log 2>&1) && grep -q "^WinUlx3sTb: self-test done .* error 0, 81920 words" "$U/sim.log"; then
  echo "   $(grep '^WinUlx3sTb:' "$U/sim.log")"
  if cmp -s "$U/py.pbm" "$U/win_frame.pbm"; then
    echo "   same  ulx3s frame: the self-test's frame = the Python layer's PBM"
  else
    echo "   DIFFERS ulx3s frame: cmp $U/py.pbm $U/win_frame.pbm"; status=1
  fi
  if r=$(python3 -I "$WINSCAN" check mode0 "$U/py.pbm" "$U/win_tmds.bin"); then
    echo "   same  ulx3s scan $r"
  else
    echo "   DIFFERS ulx3s scan: $r"; status=1
  fi
  if r=$(python3 -I "$WINSCAN" sercheck "$U/win_ser_px.hex" "$U/win_ser.bin"); then
    echo "   same  ulx3s serializer: $r"
  else
    echo "   DIFFERS ulx3s serializer: $r"; status=1
  fi
else
  echo "   DIFFERS ulx3s bench: $(grep -v '^Warning' "$U/sim.log" | head -2)"; status=1
fi

# ---- H6: the host link (WinLink.bsv) against tools/winlink.py
if [ "${WIN_PART:-}" != h2 ]; then
  echo "== run_win_link.sh: mkWinLink + the box, UART 8N1 at 4 cycles a bit"
  if WIN_BUILD="$B" ./run_win_link.sh > "$B/run_win_link.log" 2>&1; then
    grep -E "^   same" "$B/run_win_link.log"
  else
    grep -E "DIFFERS|FAIL" "$B/run_win_link.log" || tail -5 "$B/run_win_link.log"
    status=1
  fi
fi

# ---- H5: the input box (WinInput.bsv) against tools/wininput.py
if [ "${WIN_PART:-}" != h2 ]; then
  echo "== run_win_input.sh: mkWinInput, PS/2 at the wire level"
  if WIN_BUILD="$B" ./run_win_input.sh > "$B/run_win_input.log" 2>&1; then
    grep -E "^   same|^wininput" "$B/run_win_input.log"
  else
    grep -E "DIFFERS|FAIL" "$B/run_win_input.log" || tail -5 "$B/run_win_input.log"
    status=1
  fi
fi

# ---- H7s: the board's composition with the screen, keyboard and mouse
# emulated (WinLiveTb.bsv, WinHostDev.bsv/.c), kl0 on the host
if [ "${WIN_PART:-}" != h2 ]; then
  echo "== run_win_live.sh: Login PIMOS typed at the PS/2 wire, drawn through the link, seen by the monitor"
  if WIN_BUILD="$B" ./run_win_live.sh > "$B/run_win_live.log" 2>&1; then
    grep -E "^   same|skipped" "$B/run_win_live.log"
  else
    grep -E "DIFFERS|FAIL" "$B/run_win_live.log" || tail -5 "$B/run_win_live.log"
    status=1
  fi
fi

if [ $status -ne 0 ]; then
  echo "run_win_tb: FAIL"
  exit 1
fi
echo "run_win_tb: PASS"
