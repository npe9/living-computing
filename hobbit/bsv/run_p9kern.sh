#!/bin/sh
# Boot the shipped 1e kernel, s9term, on the Bluespec core and compare its
# retirement records with the reference boot's, record by record
# (docs/p9boot.md, "The boot on the core").
#
#   bsv/run_p9kern.sh RECORDS [WORKDIR]
#
# RECORDS is how many records of the reference boot to record and compare
# (125203 reaches `main`).  The reference boot is recorded first
# (tools/p9coreboot.py record), the core then runs on bsv/P9KernTb.bsv
# with bsv/p9kern.c answering device reads from the recording, and
# tools/p9coreboot.py compare stops at the first record that differs.
#
# Everything is built in WORKDIR (default build/coreboot/run), with its
# own -bdir and -simdir, so this never shares .bo files with the suite.
# P9KERN_KEEP_SIM=1 reuses the simulator already built there.
#
# P9KERN_SIM picks the simulator: `bluesim` (the default, WORKDIR/sim_p9kern)
# or `verilator` (WORKDIR/sim_p9kern_vl, built by build_p9kern_vl.sh in
# WORKDIR/vl, its own -bdir).  Both print the same core.log byte for byte
# and exit with the same status (docs/bluespec_architecture.md,
# "Simulators").
set -eu
cd "$(dirname "$0")"
here=$(pwd)
if [ $# -lt 1 ]; then
  echo "usage: run_p9kern.sh RECORDS [WORKDIR]" >&2
  exit 2
fi
n=$1
work=${2:-$here/../build/coreboot/run}

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

sim=${P9KERN_SIM:-bluesim}
case "$sim" in
  bluesim|verilator) ;;
  *) echo "run_p9kern.sh: P9KERN_SIM must be bluesim or verilator, not $sim" >&2
     exit 2 ;;
esac

mkdir -p "$work/bo" "$work/sim" "$work/rec"
work=$(cd "$work" && pwd)
PYTHONDONTWRITEBYTECODE=1 python3 "$here/../tools/p9coreboot.py" record \
    "$work/rec" --max-steps "$n"

if [ "$sim" = verilator ]; then
  simbin=sim_p9kern_vl
else
  simbin=sim_p9kern
fi
if [ "${P9KERN_KEEP_SIM:-0}" = 1 ] && [ -x "$work/$simbin" ]; then
  :
elif [ "$sim" = verilator ]; then
  "$here/build_p9kern_vl.sh" "$work" > "$work/build.log" 2>&1 || {
      tail -30 "$work/build.log"; exit 1; }
else
  "$BSC" +RTS -K512M -RTS -sim -u -bdir "$work/bo" -simdir "$work/sim" \
      -p "$work/bo:$here:%/Libraries" -g mkP9KernTb P9KernTb.bsv \
      > "$work/build.log" 2>&1 || { tail -30 "$work/build.log"; exit 1; }
  "$BSC" +RTS -K512M -RTS -sim -bdir "$work/bo" -simdir "$work/sim" \
      -p "$work/bo:$here:%/Libraries" -e mkP9KernTb \
      -o "$work/sim_p9kern" p9kern.c >> "$work/build.log" 2>&1 || {
      tail -30 "$work/build.log"; exit 1; }
fi

simstatus=0
(cd "$work" && P9KREC="$work/rec/boot.rec" P9KCONSOLE="$work/console" \
    "./$simbin" > "$work/core.log" 2>&1) || simstatus=$?
grep '^P9KERN' "$work/core.log" || true
grep -v '^HRI \|^P9KERN' "$work/core.log" | head -20 || true

fail=0
python3 "$here/../tools/p9coreboot.py" compare "$work/rec/ref.hri" \
    "$work/core.log" --functions "$work/rec/functions" || fail=1
touch "$work/console"
if cmp -s "$work/console" "$work/rec/console"; then
  echo "P9KERN console: $(wc -c < "$work/console" | tr -d ' ') bytes, identical to the reference boot's"
else
  echo "run_p9kern.sh: the console differs from the reference boot's" >&2
  fail=1
fi
if [ "$simstatus" != 0 ]; then
  echo "run_p9kern.sh: the simulator stopped with status $simstatus" >&2
  fail=1
fi
exit $fail
