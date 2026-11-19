#!/bin/sh
# Load a 1st Edition Plan 9 `z` binary on the model and start at its
# entry (tools/p9exec.py writes the image, P9BootTb.bsv runs it).
#
#   ./run_p9.sh                    cat, the default (its 1 Kbyte boot
#                                  window holds both `_main` and `main`)
#   ./run_p9.sh echo               any file in tools/plan9-1e/hobbit/bin
#
# The image package and the simulator are build products (gitignored).
set -eu
cd "$(dirname "$0")"
here=$(pwd)
bin=${1:-cat}

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

python3 "$here/../tools/p9exec.py" --image "p9.img" --entry-bsv P9Entry.bsv \
    "$here/../tools/plan9-1e/hobbit/bin/$bin"
python3 mk_image_bsv.py p9.img P9Image > P9Image.bsv

"$BSC" +RTS -K512M -RTS -sim -g mkP9BootTb -u P9BootTb.bsv
"$BSC" +RTS -K512M -RTS -sim -e mkP9BootTb -o sim_p9
./sim_p9
