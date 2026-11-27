#!/bin/sh
# The lockstep from a saved machine: PIMOS on the Bluespec core from the
# end of the IPL's link, or from the shell's prompt, through the lines
# typed, compared line by line with the reference model
# (ref/pimm/lockstep_shell.py).  Minutes to an hour; NOT part of
# run_tests.sh, since the saved machines (~1.1 GB pickles, not in git)
# take the IPL's link to make:
#
#   python3 ref/pimm/longrun_ipl.py --reference --save LINK.pkl
#   python3 ref/pimm/longrun_ipl.py --load LINK.pkl --go --fep --save-prompt PROMPT.pkl
#
#   bsv/run_pimm_shell.sh PKL [--type LINE ...]
#
# The bench (mkPimmShellTb, bsv/PimmDriverTb.bsv) is built in
# build_shell/, its generated files there too, so that the suite can run
# (and rebuild build_pimm/ and generated/) meanwhile.  The checkpoint's
# files (the heap, ~0.9 GB of hex; the reference's trace) go to a
# directory of their own, removed at the end (KEEP=1 keeps it).
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
"$BSC" -sim -p build_shell/generated:vendor/flute:+ -bdir build_shell -simdir build_shell -info-dir build_shell \
  -g mkPimmShellTb -u PimmDriverTb.bsv > build_shell/compile.log 2>&1 \
  || { cat build_shell/compile.log; exit 1; }
"$BSC" -sim -bdir build_shell -simdir build_shell -e mkPimmShellTb \
  -o build_shell/sim_pimm_shell >> build_shell/compile.log 2>&1 \
  || { cat build_shell/compile.log; exit 1; }

WORK=$(mktemp -d "${TMPDIR:-/tmp}/pimm_shell.XXXXXX")
[ "${KEEP:-}" = 1 ] || trap 'rm -rf "$WORK"' EXIT
mkdir "$WORK/generated"
cp build_shell/generated/pimm_ipl.hex "$WORK/generated/"
cp build_shell/sim_pimm_shell* "$WORK/"
python3 "$REF/lockstep_shell.py" make "$PKL" "$WORK/checkpoint" "$@"
cd "$WORK"
./sim_pimm_shell | python3 "$REF/lockstep_shell.py" compare checkpoint
