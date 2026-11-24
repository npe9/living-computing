#!/bin/sh
# Boot the shipped 1e kernel, s9term, on the Bluespec core and compare its
# retirement records with the reference boot's, record by record
# (docs/p9boot.md, "The boot on the core").
#
#   bsv/run_p9kern.sh RECORDS [WORKDIR [RECORD-ARGS...]]
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
# RECORD-ARGS go to `p9coreboot.py record` (p9boot's choices): e.g.
# `--counter-period 0.04 --until 'root is from'` (tests/test_p9boot.py
# PromptTest), or the join's `--type 'il]: =\r' --ether-replay PCAP`.
# P9KERN_KEEP_REC=1 reuses WORKDIR's recording when it was made with the
# same RECORDS and RECORD-ARGS.
#
# P9KERN_STREAM=1 is the long-run form: the reference trace is kept
# compressed (rec/ref.hri.zst), the simulator's output is piped straight
# into the comparison, which stops it at the first difference, and only
# the non-HRI lines are kept (core.log).  Without it both traces are
# plain files (~127 bytes a record each).
set -eu
cd "$(dirname "$0")"
here=$(pwd)
if [ $# -lt 1 ]; then
  echo "usage: run_p9kern.sh RECORDS [WORKDIR]" >&2
  exit 2
fi
n=$1
work=${2:-$here/../build/coreboot/run}
[ $# -ge 2 ] && shift 2 || shift $#
stream=${P9KERN_STREAM:-0}

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

mkdir -p "$work/bo" "$work/sim" "$work/rec"
zflag=
reftrace=$work/rec/ref.hri
if [ "$stream" = 1 ]; then
  zflag=--zstd
  reftrace=$work/rec/ref.hri.zst
fi
key="$n $zflag $*"
if [ "${P9KERN_KEEP_REC:-0}" = 1 ] && [ -f "$work/rec/key" ] &&
   [ "$(cat "$work/rec/key")" = "$key" ] && [ -f "$reftrace" ]; then
  echo "run_p9kern.sh: reusing the recording in $work/rec ($key)"
else
  rm -f "$work/rec/key"
  PYTHONDONTWRITEBYTECODE=1 python3 "$here/../tools/p9coreboot.py" record \
      "$work/rec" --max-steps "$n" $zflag "$@"
  printf '%s\n' "$key" > "$work/rec/key"
fi

if [ "${P9KERN_KEEP_SIM:-0}" != 1 ] || [ ! -x "$work/sim_p9kern" ]; then
  "$BSC" +RTS -K512M -RTS -sim -u -bdir "$work/bo" -simdir "$work/sim" \
      -p "$work/bo:$here:%/Libraries" -g mkP9KernTb P9KernTb.bsv \
      > "$work/build.log" 2>&1 || { tail -30 "$work/build.log"; exit 1; }
  "$BSC" +RTS -K512M -RTS -sim -bdir "$work/bo" -simdir "$work/sim" \
      -p "$work/bo:$here:%/Libraries" -e mkP9KernTb \
      -o "$work/sim_p9kern" p9kern.c >> "$work/build.log" 2>&1 || {
      tail -30 "$work/build.log"; exit 1; }
fi

simstatus=0
fail=0
if [ "$stream" = 1 ]; then
  # The simulator's status is lost in the pipe; a stop at the first
  # difference kills it (SIGPIPE), and the comparison's verdict and the
  # P9KERN report in core.log are what count.
  cmpout=$work/compare.out
  (cd "$work" && P9KREC="$work/rec/boot.rec" P9KCONSOLE="$work/console" \
      ./sim_p9kern 2>&1 | PYTHONDONTWRITEBYTECODE=1 python3 \
      "$here/../tools/p9coreboot.py" compare "$reftrace" - \
      --functions "$work/rec/functions" --side "$work/core.log" \
      > "$cmpout") || fail=1
  grep '^P9KERN' "$work/core.log" || true
  grep -v '^P9KERN' "$work/core.log" | head -20 || true
  cat "$cmpout"
  grep -q '^MATCH' "$cmpout" || fail=1
  grep -q '^P9KERN FAIL' "$work/core.log" && simstatus=1
else
  (cd "$work" && P9KREC="$work/rec/boot.rec" P9KCONSOLE="$work/console" \
      ./sim_p9kern > "$work/core.log" 2>&1) || simstatus=$?
  grep '^P9KERN' "$work/core.log" || true
  grep -v '^HRI \|^P9KERN' "$work/core.log" | head -20 || true

  PYTHONDONTWRITEBYTECODE=1 python3 "$here/../tools/p9coreboot.py" compare \
      "$reftrace" "$work/core.log" --functions "$work/rec/functions" || fail=1
fi
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
