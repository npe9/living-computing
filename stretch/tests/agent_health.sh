#!/bin/bash
# agent_health.sh -- one screen on every live Stretch worktree: is its agent working, waiting, or stuck?
#
#   tests/agent_health.sh [EXTRA_DIR ...]
#
# For each git worktree of this repository (the main tree included), and for any
# suite_bg.sh PREFIX.status found in the worktrees or in EXTRA_DIRs (scratchpads):
#   - branch, commits on it not on master (stretch/ only), uncommitted stretch/ files
#   - processes whose CURRENT DIRECTORY is inside the tree (lsof), the reliable way
#     to see what runs there (a ps path can be another tree's, and two runs in one
#     tree share one script file)
#   - the newest *suite*.log under the tree or EXTRA_DIRs, its age and how it ends
#     (pass line / "Terminated" / mid-section)
# and, machine-wide, every shell whose command line waits on `pgrep -f`: a waiter
# keyed on a script NAME matches other agents' runs and never ends (2026-11-25).
# Read-only: it changes nothing and kills nothing.
set -u
here=$(cd "$(dirname "$0")" && pwd -P)
R=$(git -C "$here" rev-parse --show-toplevel)
now=$(date +%s)
age() { local m; m=$(stat -f %m "$1" 2>/dev/null || echo "$now"); echo "$(( (now - m) / 60 ))m"; }
ending() {   # how a suite log ends
  local l; l=$(tail -1 "$1" 2>/dev/null)
  case $l in
    "All regression tests passed.") echo "PASS-LINE" ;;
    *Terminated*|*Killed*) echo "KILLED: $l" ;;
    *"ONE OR MORE TESTS FAILED"*) echo "FAILED ($(grep '^FAIL' "$1" | grep -vc 'UNREPRODUCED, expected') unexpected FAIL lines)" ;;
    *) if tail -3 "$1" | grep -q 'Terminated'; then echo "KILLED: $(tail -3 "$1" | grep -m1 Terminated)"; else echo "mid: $(echo "$l" | cut -c1-90)"; fi ;;
  esac
}
lsofcwd=$(lsof -d cwd -Fpn 2>/dev/null | awk '/^p/{p=substr($0,2)} /^n/{print p, substr($0,2)}')

git -C "$R" worktree list --porcelain | awk '/^worktree /{print substr($0,10)}' | while read -r W; do
  [ -d "$W/stretch" ] || continue
  b=$(git -C "$W" rev-parse --abbrev-ref HEAD 2>/dev/null)
  ahead=$(git -C "$W" rev-list --count master..HEAD -- stretch 2>/dev/null)
  dirty=$(git -C "$W" status --porcelain -- stretch 2>/dev/null | wc -l | tr -d ' ')
  procs=$(echo "$lsofcwd" | awk -v w="$W/" -v r="$R" 'index($2"/", w)==1 && (w!=r"/" || index($2, r"/.claude/worktrees/")!=1) {print $1}' | sort -u)
  busy=""
  for p in $procs; do c=$(ps -o command= -p "$p" 2>/dev/null | cut -c1-60); case $c in *run_tests*|*bsc*|*_sim*|*bluetcl*|*yosys*|*nextpnr*) busy="$busy [$p ${c%% -*}]";; esac; done
  echo "== $W"
  echo "   branch $b; $ahead stretch commits not on master; $dirty uncommitted stretch files"
  echo "   working processes:${busy:- none}"
  log=$(find "$W/stretch" -maxdepth 3 -name '*suite*.log' -type f 2>/dev/null | xargs ls -t 2>/dev/null | head -1)
  [ -n "$log" ] && echo "   newest suite log: $log ($(age "$log") old) -> $(ending "$log")"
done

for D in "$R/.claude/worktrees" "$@"; do
  [ -d "$D" ] || continue
  for st in $(find "$D" -maxdepth 4 -name '*.status' -type f 2>/dev/null); do
    P=${st%.status}; [ -e "$P.log" ] || continue
    echo "== suite_bg $P: $("$here/suite_bg.sh" status "$P")"
  done
  if [ "$D" != "$R/.claude/worktrees" ]; then
    for log in $(find "$D" -maxdepth 2 -name '*suite*.log' -type f -mmin -720 2>/dev/null); do
      [ -e "${log%.log}.status" ] && continue
      echo "== log $log ($(age "$log") old) -> $(ending "$log")"
    done
  fi
done

echo "== waiters keyed on a process NAME (they match other agents' runs):"
ps -ax -o pid=,etime=,command= | grep -E 'until[^|]*pgrep -f|while[^|]*pgrep -f' | grep -v grep | cut -c1-40 | sed 's/^/   /' || true
