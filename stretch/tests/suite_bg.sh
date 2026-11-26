#!/bin/bash
# suite_bg.sh -- run the Stretch regression suite so that its end, or its death, is always recorded.
#
#   tests/suite_bg.sh run    PREFIX   run the suite of THIS tree (the tree holding this script),
#                                     in the foreground; launch it with run_in_background
#   tests/suite_bg.sh wait   PREFIX   block until that run has ended; print its verdict
#   tests/suite_bg.sh status PREFIX   one-line state: RUNNING / GREEN / RED / KILLED / DEAD
#
# PREFIX is a path without an extension, e.g. $S/b55.  Files written:
#   PREFIX.log     the suite's output
#   PREFIX.status  pid=, start=, tree=, head=, tape= (written at start)
#   PREFIX.done    end=, exit=, verdict=, unexpected=, expected=, last= (written at the end)
#   PREFIX.killed  on SIGTERM/INT/HUP: the signal, the time and a process snapshot
#
# Why this exists (2026-11-25): an agent's suite died with "Terminated: 15" and its
# hand-written waiter (`pgrep -f run_tests.sh`) kept matching another agent's suite,
# so the death went unnoticed for 3.5 h.  This waits on ITS OWN pid only, and a
# killed run leaves a .done that says so.
#
# Verdict rules (as in .claude/skills/stretch-suite-verdict): GREEN needs the
# last line "All regression tests passed." and no FAIL line other than
# "FAIL (UNREPRODUCED, expected) ...".  STRETCH_TAPE defaults to PREFIX.tape;
# STRETCH_HALT_REPORT defaults to 1.  SUITE_BG_CMD replaces ./run_tests.sh, only
# to test this wrapper.
set -u
cmd=${1:-}; P=${2:-}
[ -n "$cmd" ] && [ -n "$P" ] || { sed -n '3,6p' "$0"; exit 2; }
here=$(cd "$(dirname "$0")" && pwd -P)

verdict() {   # $1 = log: print "verdict unexpected expected"
  local u e last
  u=$(grep '^FAIL' "$1" 2>/dev/null | grep -vc 'UNREPRODUCED, expected')
  e=$(grep -c 'UNREPRODUCED, expected' "$1" 2>/dev/null)
  last=$(tail -1 "$1" 2>/dev/null)
  if [ "$u" = 0 ] && [ "$last" = "All regression tests passed." ]; then echo "GREEN $u $e"
  else echo "RED $u $e"; fi
}

case $cmd in
run)
  [ -e "$P.status" ] && ! [ -e "$P.done" ] && kill -0 "$(sed -n 's/^pid=//p' "$P.status")" 2>/dev/null \
    && { echo "suite_bg: $P is already running" >&2; exit 2; }
  rm -f "$P.done" "$P.killed"
  : "${STRETCH_TAPE:=$P.tape}" "${STRETCH_HALT_REPORT:=1}"; export STRETCH_TAPE STRETCH_HALT_REPORT
  {
    echo "pid=$$"; echo "start=$(date '+%F %T')"; echo "tree=$here"
    echo "head=$(git -C "$here" rev-parse --short HEAD 2>/dev/null)"; echo "tape=$STRETCH_TAPE"
  } > "$P.status"
  child=
  killtree() {   # this run's own descendants only, by parent pid -- never by name
    local c; for c in $(pgrep -P "$1"); do killtree "$c"; done; kill -TERM "$1" 2>/dev/null
  }
  on_sig() {
    { echo "signal=$1"; echo "time=$(date '+%F %T')"; echo "--- processes at the time:"
      ps -ax -o pid,ppid,etime,command | cut -c1-220; } > "$P.killed"
    [ -n "$child" ] && killtree "$child"
    { echo "end=$(date '+%F %T')"; echo "exit=signal $1"; echo "verdict=KILLED"
      echo "last=$(tail -1 "$P.log" 2>/dev/null | cut -c1-160)"; } > "$P.done"
    exit 143
  }
  trap 'on_sig TERM' TERM; trap 'on_sig INT' INT; trap 'on_sig HUP' HUP
  cd "$here" || exit 2
  if [ -n "${SUITE_BG_CMD:-}" ]; then sh -c "$SUITE_BG_CMD" > "$P.log" 2>&1 &
  else ./run_tests.sh > "$P.log" 2>&1 & fi
  child=$!
  wait "$child"; rc=$?
  set -- $(verdict "$P.log")
  { echo "end=$(date '+%F %T')"; echo "exit=$rc"; echo "verdict=$1"
    echo "unexpected=$2"; echo "expected=$3"; echo "last=$(tail -1 "$P.log" | cut -c1-160)"; } > "$P.done"
  cat "$P.done"
  [ "$1" = GREEN ]
  ;;
status)
  if [ -e "$P.done" ]; then awk -F= '$1=="verdict"{v=$2} $1=="end"||$1=="unexpected"||$1=="expected"||$1=="exit"{o=o" "$0} END{print v o}' "$P.done"
  elif [ -e "$P.status" ] && kill -0 "$(sed -n 's/^pid=//p' "$P.status")" 2>/dev/null; then
    echo "RUNNING since $(sed -n 's/^start=//p' "$P.status"); log $(grep -c '^===' "$P.log" 2>/dev/null) sections, last write $(( $(date +%s) - $(stat -f %m "$P.log" 2>/dev/null || echo 0) ))s ago"
  elif [ -e "$P.status" ]; then echo "DEAD: pid gone, no .done (killed by SIGKILL or a reboot?); last: $(tail -1 "$P.log" 2>/dev/null | cut -c1-160)"
  else echo "NONE: no $P.status"; fi
  ;;
wait)
  [ -e "$P.status" ] || { echo "suite_bg: no $P.status" >&2; exit 2; }
  pid=$(sed -n 's/^pid=//p' "$P.status")
  while ! [ -e "$P.done" ] && kill -0 "$pid" 2>/dev/null; do sleep 30; done
  "$0" status "$P"; [ -e "$P.killed" ] && head -2 "$P.killed"
  grep -q '^verdict=GREEN' "$P.done" 2>/dev/null
  ;;
*) sed -n '3,6p' "$0"; exit 2 ;;
esac
