#!/bin/sh
# The long run: the whole pimos.ipl through the IPL's loader and
# linker on the Bluespec core, compared line by line with the
# reference model (ref/pimm/longrun_ipl.py).  Hours; not part of
# run_tests.sh.
#
#   bsv/run_pimm_longrun.sh [N]      N: only the first N files
#
# It uses the simulator run_pimm_lockstep.sh built, copied to a
# directory of its own so that the suite can run (and rebuild)
# meanwhile.
set -e
cd "$(dirname "$0")"
BSC=${BSC:-$(ls -d /opt/homebrew/Cellar/bsc/*/bin/bsc 2>/dev/null | sort | tail -1)}
BLUESPECDIR=$(cd "$(dirname "$BSC")/../libexec/lib" && pwd)
export BLUESPECDIR
PATH=$(dirname "$BSC"):$PATH
export PATH
REF=$(cd ../ref/pimm && pwd)
[ -x build_pimm/sim_pimm_driver ] || { echo "run bsv/run_pimm_lockstep.sh first" >&2; exit 1; }
WORK=$(mktemp -d "${TMPDIR:-/tmp}/pimm_longrun.XXXXXX")
trap 'rm -rf "$WORK"' EXIT
cp -R build_pimm "$WORK/"
mkdir "$WORK/generated"
cp generated/*.hex "$WORK/generated/"
cd "$WORK"
python3 "$REF/longrun_ipl.py" --script generated/pimm_script.hex "$@"
./build_pimm/sim_pimm_driver | python3 "$REF/longrun_ipl.py" compare "$@"
