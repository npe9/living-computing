#!/bin/sh
# Run a 1st Edition Plan 9 program on the Bluespec core and compare it,
# retirement by retirement, with the same program on the reference model
# (A2 of docs/plan9_boot_plan.md).
#
#   ./run_p9host.sh TREE BINARY [ARG ...]
#
# TREE is the process's file tree (its `/` and working directory); it is
# copied, so the run leaves it alone.  BINARY is a file in
# tools/plan9-1e/hobbit/bin, or a path.
#
#   1. tools/p9run.py runs BINARY on sem/hobbit_sem.py in a copy of TREE
#      and writes the recording (boot memory, start state, every kernel
#      entry) and the reference HRI trace;
#   2. P9HostTb.bsv + p9host.c boot the recording on the core and replay
#      the kernel entries, checking the machine's arguments at each;
#   3. tools/p9trace_cmp.py compares the two traces (every field but
#      cyc; the stub's records dropped);
#   4. every file the Bluespec run wrote -- taken from the *model's*
#      memory at each write call -- and its console are compared with
#      the reference run's.
#
# $P9CWD is the program's working directory, as a path under TREE (the
# kernel's sources include ../port/...).
#
# Everything is left in p9work/ (gitignored).  P9HOST_KEEP_SIM=1 reuses
# an existing simulator (the testbench does not depend on the program).
set -eu
cd "$(dirname "$0")"
here=$(pwd)
if [ $# -lt 2 ]; then
  echo "usage: run_p9host.sh TREE BINARY [ARG ...]" >&2
  exit 2
fi
tree=$1; bin=$2; shift 2
case "$bin" in
  */*) ;;
  *) bin="$here/../tools/plan9-1e/hobbit/bin/$bin" ;;
esac

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

work=$here/p9work
rm -rf "$work"
mkdir -p "$work/out"
cp -R "$tree" "$work/ref"

status=0
PYTHONDONTWRITEBYTECODE=1 python3 "$here/../tools/p9run.py" \
    --root "$work/ref" --cwd "${P9CWD:-}" \
    --record "$work/p9.rec" --hri "$work/ref.hri" \
    "$bin" "$@" > "$work/ref.console" 2> "$work/ref.status" || status=$?
cat "$work/ref.status"
# The reference run must have run the program to its exits.  One that
# stopped early (a refused system call, an instruction the reference
# model refuses, the step limit) leaves a short trace, and the Bluespec
# run would "match" it.  The exit *string* is not checked: a program
# whose main returns exits with libc's `_exits<>` quirk
# (docs/plan9_boot_plan.md), which is not a failure.
if ! grep -q '^p9run: exits(' "$work/ref.status"; then
  echo "run_p9host.sh: the reference run did not reach exits; nothing to compare with" >&2
  exit 1
fi
echo "P9HOST reference: $(wc -l < "$work/ref.hri" | tr -d ' ') retirements, $(grep -c '^E ' "$work/p9.rec" || true) kernel entries"

if [ "${P9HOST_KEEP_SIM:-0}" != 1 ] || [ ! -x sim_p9host ]; then
  "$BSC" +RTS -K512M -RTS -sim -g mkP9HostTb -u P9HostTb.bsv > "$work/build.log" 2>&1 || {
      tail -30 "$work/build.log"; exit 1; }
  "$BSC" +RTS -K512M -RTS -sim -e mkP9HostTb -o sim_p9host p9host.c >> "$work/build.log" 2>&1 || {
      tail -30 "$work/build.log"; exit 1; }
fi

simstatus=0
P9REC="$work/p9.rec" P9OUT="$work/out" ./sim_p9host > "$work/core.log" 2>&1 || simstatus=$?
grep '^P9HOST' "$work/core.log" || true
grep -v '^HRI \|^P9HOST' "$work/core.log" | head -20 || true

fail=0
python3 "$here/../tools/p9trace_cmp.py" "$work/ref.hri" "$work/core.log" || fail=1
if [ "$simstatus" != 0 ]; then
  echo "run_p9host.sh: the simulator stopped with status $simstatus" >&2
  fail=1
fi

# The console and every file the model wrote.
touch "$work/out/console"
if cmp -s "$work/out/console" "$work/ref.console"; then
  echo "P9HOST console: $(wc -c < "$work/out/console" | tr -d ' ') bytes, identical to the reference run's"
else
  echo "run_p9host.sh: the console differs from the reference run's" >&2
  fail=1
fi
for f in $(cd "$work/out" && find . -type f ! -name console | sed 's|^\./||'); do
  if cmp -s "$work/out/$f" "$work/ref/$f"; then
    echo "P9HOST file $f: $(wc -c < "$work/out/$f" | tr -d ' ') bytes, identical to the reference run's"
  else
    echo "run_p9host.sh: $f differs from the reference run's" >&2
    fail=1
  fi
done
exit $fail
