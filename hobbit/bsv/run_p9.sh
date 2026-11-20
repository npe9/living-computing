#!/bin/sh
# Load a 1st Edition Plan 9 `z` binary on the model and run it over the
# A1 syscall shim (tools/p9exec.py writes the image, tools/p9shim.py
# writes the stub and the file table, P9BootTb.bsv runs it).
#
#   ./run_p9.sh                    cat, the default (its 1 Kbyte boot
#                                  window holds both `_main` and `main`),
#                                  reading tools/plan9-1e/sys/src/9/hobbit/raml.s
#   ./run_p9.sh echo               any file in tools/plan9-1e/hobbit/bin
#   ./run_p9.sh cat FILE           cat FILE's bytes through the shim
#
# The shim serves one host file as stdin; cat with argc = 1 reads it and
# writes it to the console, so the run is byte-checked against FILE.
#
# The image package, the shim package and the simulator are build
# products (gitignored).
set -eu
cd "$(dirname "$0")"
here=$(pwd)
bin=${1:-cat}
file=${2:-"$here/../tools/plan9-1e/sys/src/9/hobbit/raml.s"}

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
python3 "$here/../tools/p9shim.py" --emit P9Shim.bsv \
    --file "$file" "$here/../tools/plan9-1e/hobbit/bin/$bin"

rm -f p9.console
"$BSC" +RTS -K512M -RTS -sim -g mkP9BootTb -u P9BootTb.bsv
"$BSC" +RTS -K512M -RTS -sim -e mkP9BootTb -o sim_p9
./sim_p9 > p9.log 2>&1 || {
    cat p9.log
    echo "run_p9.sh: the model stopped with a nonzero status" >&2
    exit 1
}

grep '^P9SHIM' p9.log || true
if [ ! -f p9.console ]; then
    echo "run_p9.sh: no console output; cat wrote nothing" >&2
    exit 1
fi
if cmp -s p9.console "$file"; then
    bytes=$(wc -c < p9.console | tr -d ' ')
    echo "P9SHIM CONSOLE match: $file, $bytes bytes byte-exact"
else
    echo "run_p9.sh: p9.console does not match $file" >&2
    cmp p9.console "$file" >&2 || true
    exit 1
fi
if ! grep -q '^P9SHIM EXIT status=0' p9.log; then
    echo "run_p9.sh: the run did not exit 0" >&2
    exit 1
fi
