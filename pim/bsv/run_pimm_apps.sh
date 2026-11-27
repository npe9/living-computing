#!/bin/sh
# The commands past the shell, in lockstep: each command of
# ref/pimm/lockstep_shell.py's APPS (or those named) typed at the
# shell's prompt of a saved machine, on the reference model and on the
# Bluespec core, compared line by line, the counts against PINNED and
# the window's text against APPS.  The commands and what the manuals
# print for them: docs/binary_reverse_engineering.md 1.4, "Commands
# past the shell".
#
#   bsv/run_pimm_apps.sh PROMPT.pkl [NAME ...]
#
# PROMPT.pkl is a machine saved at the prompt (bsv/README.md, "The
# lockstep from a saved machine": longrun_ipl.py --load LINK.pkl --go
# --fep --save-prompt PROMPT.pkl).  NOT part of run_tests.sh: the
# pickle is ~1.1 GB, not in git.  The checkpoint is loaded once and its
# heap written once (~0.9 GB of hex); each command is then played from
# it in a process of its own (lockstep_shell.py apps).  The bench is
# run_pimm_shell.sh's (build_shell/); the work directory is removed at
# the end (KEEP=1 keeps it).  Ends with `pimm lockstep apps: PASS` or
# FAIL and the names that failed.
#
# The RESTORE injections (bsv/README.md, "Which RESTOREs the commands
# check"; lockstep_shell.py DROPPED): with INJECT=1, after the
# compares, each RESTORE of DROPPED is dropped in turn from its
# command's script (lockstep_shell.py drop) and the command compared
# again; each must fail at the pinned line, or pass where DROPPED says
# None.  `run_pimm_apps.sh --inject WORK` runs only these, on a work
# directory kept by an earlier KEEP=1 run.  Ends `pimm lockstep apps
# injections: PASS` or FAIL and the pairs that did otherwise.
set -eu
cd "$(dirname "$0")"
BSC=${BSC_BIN:-$(ls -d /opt/homebrew/Cellar/bsc/*/bin/bsc 2>/dev/null | sort | tail -1)}
BLUESPECDIR=$(cd "$(dirname "$BSC")/../libexec/lib" && pwd)
export BLUESPECDIR
PATH=$(dirname "$BSC"):$PATH
export PATH
REF=$(cd ../ref/pimm && pwd)

inject() {
  # inject WORK: the pairs of DROPPED whose command is in WORK
  bad=""
  python3 "$REF/lockstep_shell.py" drops > "$1/drops.txt"
  while read -r name which; do
    [ -d "$1/$name/checkpoint" ] || continue
    d="$1/$name/inj_$which"
    rm -rf "$d"
    mkdir -p "$d/checkpoint"
    ln -s ../generated "$d/generated"
    for f in heap.hex trace want.json; do
      ln -s "../../checkpoint/$f" "$d/checkpoint/$f"
    done
    python3 "$REF/lockstep_shell.py" drop "$which" "$1/$name/checkpoint/script.hex" "$d/checkpoint/script.hex"
    want=$(python3 "$REF/lockstep_shell.py" dropped "$name" "$which")
    # A dropped RESTORE can leave the core running with no more output:
    # with RESTORE 21 (the cdb length) it writes one line and goes
    # silent, and the compare waits for its next line (16 minutes, then
    # killed, 2026-11-25).  So the sim runs in the background into a
    # fifo, a watchdog kills it (its own PID) after INJECT_LIMIT
    # seconds (600 by default; the longest pair takes about a minute),
    # and the compare then reads the end of the trace, which is the
    # FAIL it would print; the sim is also killed once the compare has
    # its line
    rm -f "$d/fifo"
    mkfifo "$d/fifo"
    (cd "$d" && exec ../../sim_pimm_shell > fifo) &
    simpid=$!
    (sleep "${INJECT_LIMIT:-600}" && kill "$simpid" 2>/dev/null) &
    dogpid=$!
    got=$(cd "$d" && python3 "$REF/lockstep_shell.py" compare checkpoint < fifo 2>/dev/null | head -1) || true
    kill "$dogpid" 2>/dev/null || true
    wait "$dogpid" 2>/dev/null || true
    kill "$simpid" 2>/dev/null || true
    wait "$simpid" 2>/dev/null || true
    rm -f "$d/fifo"
    printf 'RESTORE %s dropped, %s: %s\n' "$which" "$name" "$got" | cut -c1-200
    case "$got" in
      *": $want"*) ;;
      *) bad="$bad $name/$which" ;;
    esac
  done < "$1/drops.txt"
  if [ -n "$bad" ]; then
    echo "pimm lockstep apps injections: FAIL:$bad"
    return 1
  fi
  echo "pimm lockstep apps injections: PASS"
}

if [ "${1:-}" = --inject ]; then
  inject "$2"
  exit $?
fi
PKL=$1
shift

mkdir -p build_shell/generated
python3 ../asm/gen_pimm_bsv.py build_shell/generated
"$BSC" -sim -p build_shell/generated:vendor/flute:+ -bdir build_shell -simdir build_shell -info-dir build_shell \
  -g mkPimmShellTb -u PimmDriverTb.bsv > build_shell/compile.log 2>&1 \
  || { cat build_shell/compile.log; exit 1; }
"$BSC" -sim -bdir build_shell -simdir build_shell -e mkPimmShellTb \
  -o build_shell/sim_pimm_shell >> build_shell/compile.log 2>&1 \
  || { cat build_shell/compile.log; exit 1; }

WORK=$(mktemp -d "${TMPDIR:-/tmp}/pimm_apps.XXXXXX")
[ "${KEEP:-}" = 1 ] || trap 'rm -rf "$WORK"' EXIT
mkdir "$WORK/generated"
cp build_shell/generated/pimm_ipl.hex "$WORK/generated/"
cp build_shell/sim_pimm_shell* "$WORK/"
python3 "$REF/lockstep_shell.py" apps "$PKL" "$WORK" "$@"
failed=""
for d in "$WORK"/*/checkpoint; do
  app=$(dirname "$d")
  name=$(basename "$app")
  ln -s ../generated "$app/generated"
  if ! (cd "$app" && ../sim_pimm_shell | python3 "$REF/lockstep_shell.py" compare checkpoint); then
    failed="$failed $name"
  fi
done
if [ -n "$failed" ]; then
  echo "pimm lockstep apps: FAIL:$failed"
  exit 1
fi
echo "pimm lockstep apps: PASS"
if [ "${INJECT:-}" = 1 ]; then
  inject "$WORK"
fi
