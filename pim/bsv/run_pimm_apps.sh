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
set -eu
cd "$(dirname "$0")"
BSC=${BSC_BIN:-$(ls -d /opt/homebrew/Cellar/bsc/*/bin/bsc 2>/dev/null | sort | tail -1)}
BLUESPECDIR=$(cd "$(dirname "$BSC")/../libexec/lib" && pwd)
export BLUESPECDIR
PATH=$(dirname "$BSC"):$PATH
export PATH
REF=$(cd ../ref/pimm && pwd)
PKL=$1
shift

mkdir -p build_shell/generated
python3 ../asm/gen_pimm_bsv.py build_shell/generated
"$BSC" -sim -p build_shell/generated:+ -bdir build_shell -simdir build_shell -info-dir build_shell \
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
