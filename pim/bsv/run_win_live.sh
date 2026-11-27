#!/bin/sh
# The window hardware with its screen, keyboard and mouse emulated, in
# Bluesim: docs/simpos/window_hardware_plan.md H7s and §4.1 (owner,
# 2026-11-26: "Figure out how to do emulate the mouse, keyboard and screen
# in bluesim.").  ALL OURS.
#
#   run_win_live.sh            the scripted cases (the suite's; no display)
#   run_win_live.sh live [M]   INTERACTIVE, for the owner: builds tools/winview
#                              (SDL2), opens its window, and runs the bench on
#                              it in video mode M (default 3, 640 x 480: the
#                              1080p frame is ~1 s of Bluesim, see `speed`);
#                              kl0 on the probe route redraws after each pause
#                              in the input (WIN_QUIET_MS, 500 receiver ms)
#   run_win_live.sh flood      only the flood case (below)
#   run_win_live.sh speed      Bluesim frames per second, modes 0 and 3
#
# FOR THE OWNER (the live run; bsv/README.md has the same):
#   cd pim/bsv && ./run_win_live.sh live
# The window shows the PSI's screen at 2:1 (frame rows 24-983, mode 3's
# pan, the status band included).  Point with the Mac's own pointer (the
# hardware cursor is off, so the frame stays the software's); a right
# double click opens the system menu.  The screen changes a second or two
# after a pause in the input (kl0 runs again from the boot).  While you
# act the bench is held to the wall clock, so clicks and double clicks are
# timed as you make them.  Cmd-S saves the frame shown as
# build-win/live/interactive/winview_N.pbm; closing the window ends the
# run, saves winview_last.pbm, and the runner then writes PNGs of the saved
# frames, counts the receivers' dropped bytes and kl0's step limits (both
# must be 0), and compares the last frame with the software frame of kl0's
# last run.  The whole log is build-win/live/interactive/sim.log.
#
# THE BENCH (WinLiveTb.bsv): mkWinBoardCore, the composition the board top
# synthesizes (box, scan-out, link, input box), in its sys and pixel clock
# domains; WinHostDev.bsv/.c on its pins: two PS/2 device models on the
# input box's clock and data, the host UART pair on the link's lines, and
# a virtual monitor on the scan-out's composed pixel (DE, sync levels,
# level) that checks the timing against its own mode table (from
# psi/winscan.py MODES, tools/win_kl0_host.py mode) and takes the frame.
# The kl0 host (tools/win_kl0_host.py) is its child.
#
# First, WinHostDev.c's HOST table is dumped and compared with
# tools/wininput.py's (wininput.py hostcheck).
# THE SCRIPTED CASES (each: wininput.py expand -> the host script; the run;
# then the checks):
#   console   (H7s) win_live/console.txt: the console_pwd.json tape's user
#             typed at the PS/2 wire (the system menu by a right double
#             click, Login PIMOS, local / pimos / an empty password, then
#             the console and `pwd`).  Checked: the coordinator script the
#             kl0 host recovers from the input box's records = the tape's
#             (both batches); the PSI side replays the tape to its end; the
#             monitor's frame (through the link, the box, the scan-out) has
#             the sha256 of test_espc.py's CONSOLE_PIN (imported at run
#             time); 0 timing errors, 0 link errors, 0 input errors.
#   password  win_live/password.txt: the menu by the mouse, local, pimos and
#             a password `Sec` (Shift) not ended, on the probe route.
#             Checked: the monitor's frame = the software frame of the same
#             run; 0 timing, link and input errors.
#   Both: the events the kl0 host recovered = `win_kl0_host.py expect`'s,
#   the script run through wininput.py's own models (HOST table, receivers)
#   and the adapter, which share no code with WinHostDev.c or the RTL.
#   viewer    (only if pkg-config finds sdl2) the interactive code path,
#             headless: tools/winview under SDL_VIDEODRIVER=dummy with
#             --fake-events (a key A, a move, a left click pushed into
#             SDL's queue after the first frame); the bench as its client,
#             probe route, 14 frames.  Checked: the kl0 host recovered
#             exactly JIS 'a' and a left click at (10, 20) from the input
#             records (so the viewer path's own key and mouse-packet code
#             in WinHostDev.c, which the scripted cases do not use, is
#             checked); the viewer's last frame = the monitor's last
#             frame = the software frame after those events.
#   budget    win_kl0_host.py selftest-live: --live's step limit set to a
#             one-key run's steps, then 30 keys more: the session survives
#             (no X; 1 kl0 failure, 30 events dropped, the next run works).
#   flood     (only with sdl2) the owner's garbled live run of 2026-11-26,
#             scripted: tools/winview --play win_live/flood.play under
#             SDL_VIDEODRIVER=dummy, mode 3, the bench as its client, the
#             kl0 host with --live.  Motion all the way at 125 and 1,000 Hz,
#             past the window's edges, a right double click, Login PIMOS,
#             the requester's answers typed while the mouse moves, motion
#             while kl0 runs and draws (~900 link frames).  The viewer's E
#             ends the run.  Checked: 0 bytes dropped by the receivers
#             (sim.log's "WinPs2Rx: queue full"), 0 input errors, 0 kl0
#             failures, no StepLimit; the clicks and keys recovered (moves
#             aside: their number depends on timing) = FLOOD_EXPECT; the
#             viewer's last frame = the monitor's = the software frame's
#             mode 3 view (win_kl0_host.py view: the 2:1 OR reduction from
#             the pan).  ~30 s.
#             ON MASTER'S CODE (15db30b4's WinHostDev.c and win_kl0_host.py,
#             in a private copy, with this runner, viewer and play file;
#             observed 2026-11-26): FAILED, 728 bytes dropped, 121 input
#             errors ("code 5": broken packets, as in the owner's run), the
#             clicks recovered: 12 phantom right clicks, the double click at
#             (640, 601) and Login PIMOS's click at (978, 645), Y up to
#             1,023; the frames differ; and no end (that code knows no E).
#             (With the double click 150 ms apart, the same: 1,193 bytes
#             dropped, 184 input errors, 28 phantom right clicks.)  On the
#             first, gentler play file (8 ms motion only) master's code
#             dropped 12 bytes with 3 input errors and a phantom middle
#             click when the machine was loaded, and none in two runs when
#             it was not (those still put the clicks 24 rows too high, and
#             one split the double click into two singles): so 1,000 Hz
#             motion was added.
# Build in $WIN_BUILD/live (default build-win/live).  No board.
#
# INJECTED FAULTS, OBSERVED 2026-11-26, each in a private copy of pim/
# (bsv, tools, psi, ref, asm) with its own build directory; the worktree's
# files were never edited for an injection:
#   V1  WinScanOut: vsync one line late -> console, password: 1 timing
#       error each (the first active line); viewer: 13.  Before the
#       monitor checked the first active line this one PASSED; that check
#       was added for it.
#   V2  WinInput's device model: parity inverted -> console: the script
#       from the receivers is not the tape's; password: input errors in
#       the kl0 host's report.
#   V3  WinHostDev.c: make and break swapped -> password: the events
#       recovered differ from wininput.py's model.  It PASSED before the
#       expect check and a shifted password ("Sec") were added for it.
#   V4  WinLink: the event record's A bytes swapped -> console: the script
#       is not the tape's; password: input errors.  (Before the adapter
#       caught a record it cannot read, this showed as "the kl0 host
#       ended".)
#   V5  WinHostDev.c: 64 frames unanswered, not 8 -> console: 2 link
#       errors, no end; password: no end; viewer: 20 answers, frame differs.
#   V6  the adapter: no double click (DCLICK_MS = 0) -> console: the script
#       is not the tape's.
#   V7  WinScanOut: the border white -> 762,880 timing errors a case
#       (9,917,440 on the viewer's 14 frames).
#   V8  WinScanOut: hsync one pixel wider -> 1,125 timing errors a case
#       (one a line).
#   V9  WinHostDev.c: the viewer's mouse packets with Y not negated ->
#       viewer only (the scripted cases' packets come from wininput.py):
#       the events differ.  It PASSED until the viewer case checked the
#       recovered events (key a, click l at (10, 20)); that check was added.
#   V10 WinHostDev.c: HOST maps usage 04 (A) to S's code -> the hostcheck
#       step: "WinHostDev.c's table differs from HOST at usages 04".
#   V11 the monitor's own mode line: vertical back porch one more ->
#       console, password: 2 timing errors; viewer: 26.  (A first V11
#       changed the RTL configuration's word 8 instead of the monitor's
#       table, was mis-aimed, PASSED, and was replaced by this one.)
# The live fixes' (2026-11-26, the flood and budget cases; same method, one
# private copy, each file restored by copy and checked with cmp):
#   F1  WinHostDev.c: no coalescing or pacing (one host motion event a
#       sample, samples back to back: master's packet a motion event) ->
#       flood: 2,753 bytes dropped, 310 input errors, phantom right and
#       middle clicks, Y 1,023.
#   F2  WinHostDev.c: the pan not added -> flood: the clicks recovered 24
#       rows high ((640, 536), (978, 580)); the frames still agree (they
#       are drawn from those clicks).
#   F3  WinHostDev.c: the bench never held to the wall clock -> flood: the
#       right double click recovered as two singles.  It PASSED at first,
#       with a 150 ms gap between the clicks (INFERENCE: the loaded bench
#       ran under 2.7 times the wall clock, inside the adapter's 400 ms);
#       the play file's
#       gap became 300 ms, which a free bench stretches past 400.
#   F4  WinHostDev.c: the viewer's W stamps ignored (gaps from arrival) ->
#       PASSED: the stamps matter only for clicks made while kl0 blocks
#       the bench, and flood.play has only motion and keys then.  NOT
#       COVERED (an open item).
#   F5  win_kl0_host.py: no rollback under --live -> budget: FAIL (0 kl0
#       failures counted, 2 X lines: the session would end).
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

B=${WIN_BUILD:-build-win}/live
mkdir -p "$B"
B=$(cd "$B" && pwd)
HERE=$(pwd)
T=$(cd ../tools && pwd)
TAPE=$(cd ../psi/fep_bridge_tapes && pwd)/console_pwd.json
WHAT=${1:-scripted}

echo "== bsc: mkWinLiveTb (+ WinHostDev.c)"
"$BSC" -sim -u -g mkWinLiveTb -bdir "$B" -simdir "$B" -info-dir "$B" WinLiveTb.bsv > "$B/bsc.log" 2>&1 \
  || { cat "$B/bsc.log"; exit 1; }
# bsc puts a C file's object next to the C file: link a copy in the build
# directory, so that no WinHostDev.o lands in bsv/
cp WinHostDev.c "$B/WinHostDev.c"
(cd "$B" && "$BSC" -sim -e mkWinLiveTb -bdir . -simdir . -o sim_live WinHostDev.c > link.log 2>&1) \
  || { cat "$B/link.log"; exit 1; }

echo "== WinHostDev.c's HOST table (cc -DWHD_DUMP) against tools/wininput.py's"
cc -DWHD_DUMP -o "$B/whd_dump" WinHostDev.c
"$B/whd_dump" > "$B/host_table.txt"
python3 -I "$T/wininput.py" hostcheck "$B/host_table.txt" || { echo "run_win_live: FAIL"; exit 1; }

# a run directory: the font, an empty self-test stream, the scan
# configuration of mode M with the cursor off, the monitor's mode line
prep() {   # prep DIR MODE
  mkdir -p "$1"
  python3 -I ../psi/winfb.py fonthex "$1/win_font.hex"
  printf '%026x\n' 0 > "$1/win_stream.hex"
  python3 -I "$T/win_kl0_host.py" config "$2" "$1/win_scan.hex"
  python3 -I "$T/win_kl0_host.py" mode "$2" > "$1/mode.txt"
}

field() {  # field REPORT KEY
  python3 -I -c 'import json, sys; v = json.load(open(sys.argv[1])).get(sys.argv[2]); print("" if v is None else v[0] if isinstance(v, list) and v and isinstance(v[0], str) else v)' "$1" "$2"
}

if [ "$WHAT" = speed ]; then
  for m in 0 3; do
    R=$B/speed$m; prep "$R" $m
    : > "$R/empty.host"
    s0=$(python3 -c 'import time; print(time.time())')
    (cd "$R" && WIN_HOSTDEV_MODE=mode.txt WIN_HOSTDEV_SCRIPT=empty.host WIN_HOSTDEV_RUNFRAMES=6 \
      "$B/sim_live" > sim.log 2>&1) || true
    s1=$(python3 -c 'import time; print(time.time())')
    python3 -I -c 'import sys
m, t0, t1 = int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])
ht, vt = {0: (2200, 1125), 3: (800, 525)}[m]
print("   mode %d: 6 frames (+ lock-on) in %.1f s: %.2f frames/s, %.2f M pixel clocks/s" % (m, t1 - t0, 7 / (t1 - t0), 7 * ht * vt / (t1 - t0) / 1e6))' $m "$s0" "$s1"
    grep "^WinHostDev" "$R/sim.log" | sed 's/^/     /'
  done
  exit 0
fi

if [ "$WHAT" = live ]; then
  M=${2:-3}
  R=$B/interactive; prep "$R" "$M"
  ../tools/winview/build.sh "$B/winview"
  SC=2; [ "$M" = 3 ] || SC=1
  (cd "$R" && exec "$B/winview" view.sock --scale $SC) &
  VPID=$!
  sleep 1
  echo "== the bench on the viewer (close the window to stop; Cmd-S saves the frame shown)"
  (cd "$R" && WIN_HOSTDEV_MODE=mode.txt WINVIEW_SOCKET=view.sock \
    WIN_KL0_HOST="python3 -I $T/win_kl0_host.py run --probe --live --report report.json --sw-pbm sw.pbm" \
    "$B/sim_live" 2>&1 | tee sim.log) || true
  kill $VPID 2>/dev/null || true
  wait $VPID 2>/dev/null || true
  echo "== after the session ($R)"
  echo "   receivers' dropped bytes: $(grep -c 'queue full' "$R/sim.log" || true); kl0 StepLimits: $(grep -c StepLimit "$R/sim.log" || true); the whole log: $R/sim.log"
  if [ -s "$R/report.json" ]; then
    echo "   input errors: $(field "$R/report.json" input_errors), kl0 failures survived: $(field "$R/report.json" kl0_failures)"
  fi
  for f in "$R"/winview_*.pbm; do
    [ -f "$f" ] && python3 -I "$T/win_kl0_host.py" png "$f" "${f%.pbm}.png" && echo "   saved: ${f%.pbm}.png"
  done
  if [ -s "$R/sw.pbm" ] && [ -s "$R/winview_last.pbm" ]; then
    python3 -I "$T/win_kl0_host.py" view "$M" "$R/sw.pbm" "$R/sw_view.pbm"
    if cmp -s "$R/sw_view.pbm" "$R/winview_last.pbm"; then
      echo "   the last frame shown = the software frame of kl0's last run (mode $M view)"
    else
      echo "   the last frame shown differs from the software frame of kl0's last run (input after it, or a fault): $R/sw_view.pbm"
    fi
  fi
  exit 0
fi

status=0
run_case() {   # run_case NAME SCRIPT ROUTE...
  name=$1; script=$2; shift 2
  R=$B/$name; rm -rf "$R"; prep "$R" 0
  python3 -I "$T/wininput.py" expand "$script" "$R/input.host"
  (cd "$R" && WIN_HOSTDEV_MODE=mode.txt WIN_HOSTDEV_SCRIPT=input.host WIN_HOSTDEV_PBM=frame.pbm \
    WIN_HOSTDEV_MAXMS=2000000 \
    WIN_KL0_HOST="python3 -I $T/win_kl0_host.py run $* --report report.json" \
    "$B/sim_live" > sim.log 2> host.log) || true
  r=$(grep "^WinHostDev:" "$R/sim.log" || echo "WinHostDev: no summary")
  if ! echo "$r" | grep -q "done; .* 0 timing errors, .* 0 link errors"; then
    echo "   DIFFERS $name: $r"; grep -v '^Warning\|^  ' "$R/host.log" | head -3 | sed 's/^/      /'
    status=1; return
  fi
  if [ ! -s "$R/report.json" ] || [ "$(field "$R/report.json" input_errors)" != 0 ]; then
    echo "   DIFFERS $name: input errors in the kl0 host's report"; status=1; return
  fi
  # the events the kl0 host recovered = the script's by the Python models
  # (wininput.py's HOST table and receivers, the adapter): independent of
  # WinHostDev.c and the RTL
  python3 -I "$T/win_kl0_host.py" expect "$script" > "$R/expect.json"
  if ! python3 -I -c 'import json, sys
s = json.load(open(sys.argv[1]))["script"]
s = s["login"] + s["shell"] if isinstance(s, dict) else s
sys.exit(s != json.load(open(sys.argv[2])))' "$R/report.json" "$R/expect.json"; then
    echo "   DIFFERS $name: the events recovered differ from wininput.py's model of the script"
    status=1; return
  fi
  got=$(shasum -a 256 "$R/frame.pbm" | cut -d' ' -f1)
  sw=$(field "$R/report.json" sw_sha)
  if [ "$got" != "$sw" ]; then
    echo "   DIFFERS $name: the monitor's frame ${got%"${got#????????????????}"} != the software's ${sw%"${sw#????????????????}"}"
    status=1; return
  fi
  extra=""
  if [ -n "$(field "$R/report.json" pin)" ]; then
    pin=$(field "$R/report.json" pin)
    if [ "$(field "$R/report.json" script_equals_tape)" != True ] || [ "$got" != "$pin" ] || \
       [ "$(field "$R/report.json" exchanges_left)" != 0 ]; then
      echo "   DIFFERS $name: script = tape $(field "$R/report.json" script_equals_tape), frame = pin $([ "$got" = "$pin" ] && echo yes || echo no)"
      status=1; return
    fi
    extra=", the script = the tape's, the frame = CONSOLE_PIN"
  fi
  echo "   same  $name: ${r#WinHostDev: }; the monitor's frame = the software's ($(field "$R/report.json" sw_dots) dots)$extra"
}

# the owner's live run, scripted (flood, the header): winview --play
# win_live/flood.play headless, mode 3, the bench as its client
FLOOD_EXPECT='[["mouse", "rr", 640, 560], ["mouse", "l", 978, 604],
 ["key", 9068], ["key", 9071], ["key", 9059], ["key", 9057], ["key", 9068], ["key", 13],
 ["key", 9072], ["key", 9065], ["key", 9069], ["key", 9071], ["key", 9075], ["key", 13],
 ["key", 9043], ["key", 9061], ["key", 9059]]'
flood_case() {
  R=$B/flood; rm -rf "$R"; prep "$R" 3
  (cd "$R" && SDL_VIDEODRIVER=dummy exec "$B/winview" v.sock --scale 2 --dump viewer.pbm \
    --play "$HERE/win_live/flood.play" > viewer.log 2>&1) &
  VPID=$!
  sleep 1
  (cd "$R" && WIN_HOSTDEV_MODE=mode.txt WINVIEW_SOCKET=v.sock WIN_HOSTDEV_PBM=frame.pbm \
    WIN_HOSTDEV_MAXMS=${FLOOD_MAXMS:-400000} \
    WIN_KL0_HOST="python3 -I $T/win_kl0_host.py run --probe --live --report report.json --sw-pbm sw.pbm" \
    "$B/sim_live" > sim.log 2> host.log) || true
  kill $VPID 2>/dev/null || true
  wait $VPID 2>/dev/null || true
  r=$(grep "^WinHostDev:" "$R/sim.log" || echo "WinHostDev: no summary")
  drops=$(grep -c "queue full" "$R/sim.log" || true)
  steplim=$(grep -c "StepLimit" "$R/host.log" || true)
  why=""
  echo "$r" | grep -q "done; .* 0 timing errors, .* 0 link errors" || why="$why; the run: ${r#WinHostDev: }"
  [ "$drops" = 0 ] || why="$why; $drops bytes dropped by the receivers (WinPs2Rx: queue full)"
  [ "$steplim" = 0 ] || why="$why; kl0 StepLimit $steplim times"
  if [ -s "$R/report.json" ]; then
    ev=$(python3 -I -c 'import json, sys
d = json.load(open(sys.argv[1]))
want = json.loads(sys.argv[2])
got = [e for e in d.get("script", []) if e[0] != "move"]
bad = []
if d.get("input_errors") != 0: bad.append("%s input errors" % d.get("input_errors"))
if d.get("kl0_failures", 0) != 0: bad.append("%s kl0 failures" % d.get("kl0_failures"))
if got != want: bad.append("the clicks and keys recovered differ: %s" % json.dumps(got)[:300])
print("; ".join(bad) if bad else "ok")' "$R/report.json" "$FLOOD_EXPECT")
    [ "$ev" = ok ] || why="$why; $ev"
  else
    why="$why; no report from the kl0 host"
  fi
  if [ -s "$R/sw.pbm" ]; then python3 -I "$T/win_kl0_host.py" view 3 "$R/sw.pbm" "$R/sw_view.pbm"; fi
  same=$(cmp -s "$R/viewer.pbm" "$R/frame.pbm" && cmp -s "$R/frame.pbm" "$R/sw_view.pbm" && echo yes || echo no)
  [ "$same" = yes ] || why="$why; the viewer's, the monitor's and the software's (mode 3 view) frames are not all equal"
  if [ -z "$why" ]; then
    echo "   same  flood: ${r#WinHostDev: }; 0 bytes dropped, 0 input errors, no StepLimit; the clicks and keys = the play file's; the viewer's frame = the monitor's = the software's mode 3 view"
  else
    echo "   DIFFERS flood${why}"
    status=1
  fi
}

if [ "$WHAT" = flood ]; then
  ../tools/winview/build.sh "$B/winview" > "$B/winview_build.log" 2>&1 || { cat "$B/winview_build.log"; exit 1; }
  flood_case
  [ $status -eq 0 ] && echo "run_win_live: PASS" || echo "run_win_live: FAIL"
  exit $status
fi

run_case console win_live/console.txt --tape "$TAPE"
run_case password win_live/password.txt --probe

# the interactive kl0 host's step budget and rollback (the header's budget)
bt=$(python3 -I "$T/win_kl0_host.py" selftest-live 2> "$B/budget.log" | tail -1)
case "$bt" in
  *": ok "*) echo "   same  budget: ${bt#win_kl0_host selftest-live: ok }" ;;
  *) echo "   DIFFERS budget: ${bt:-no verdict; see $B/budget.log}"; status=1 ;;
esac

if pkg-config --exists sdl2 2>/dev/null; then
  R=$B/viewer; rm -rf "$R"; prep "$R" 0
  ../tools/winview/build.sh "$B/winview" > "$B/winview_build.log" 2>&1 || { cat "$B/winview_build.log"; exit 1; }
  (cd "$R" && SDL_VIDEODRIVER=dummy exec "$B/winview" v.sock --dump viewer.pbm --fake-events > viewer.log 2>&1) &
  VPID=$!
  sleep 1
  (cd "$R" && WIN_HOSTDEV_MODE=mode.txt WINVIEW_SOCKET=v.sock WIN_HOSTDEV_RUNFRAMES=14 WIN_HOSTDEV_PBM=frame.pbm \
    WIN_KL0_HOST="python3 -I $T/win_kl0_host.py run --probe --report report.json" \
    "$B/sim_live" > sim.log 2> host.log) || true
  kill $VPID 2>/dev/null || true
  wait $VPID 2>/dev/null || true
  r=$(grep "^WinHostDev:" "$R/sim.log" || echo "WinHostDev: no summary")
  sw=$(field "$R/report.json" sw_sha 2>/dev/null || echo none)
  vw=$(shasum -a 256 "$R/viewer.pbm" 2>/dev/null | cut -d' ' -f1)
  # the fake events (winview.c --fake-events: key A down and up, a move to
  # (10, 20), a left click) as the kl0 host recovered them, through
  # WinHostDev.c's mouse packets and keys and the RTL receivers: JIS 'a'
  # (0x2361) and a left click at (10, 20)
  ev=$(python3 -I -c 'import json, sys
d = json.load(open(sys.argv[1]))
print("ok" if d.get("script") == [["key", 0x2361], ["mouse", "l", 10, 20]] and d.get("input_errors") == 0 else d.get("script"))' "$R/report.json" 2>/dev/null || echo "no report")
  if echo "$r" | grep -Eq "done; .* 0 timing errors, [1-9][0-9]* input events up, 0 link errors" && [ "$vw" = "$sw" ] && [ "$ev" = ok ]; then
    echo "   same  viewer: ${r#WinHostDev: }; the events = key a, click l at (10, 20); the viewer's last frame = the software's after them"
  else
    echo "   DIFFERS viewer: $r; viewer frame ${vw:-none}, software ${sw}; events ${ev}"
    status=1
  fi
  flood_case
else
  echo "   (viewer and flood cases skipped: pkg-config finds no sdl2)"
fi

if [ $status -ne 0 ]; then
  echo "run_win_live: FAIL"
  exit 1
fi
echo "run_win_live: PASS"
