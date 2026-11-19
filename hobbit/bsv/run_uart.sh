#!/bin/sh
# Build and run the Hobbit UART / HRI-writer Bluesim testbench.
# Same compiler resolution as run_smoke.sh: the newest Homebrew Cellar bsc,
# its matching BLUESPECDIR, and a larger Haskell stack.  All build products
# go to a scratch directory, never the source tree.
set -eu
cd "$(dirname "$0")"

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

BUILD=${BUILD_DIR:-$(mktemp -d "${TMPDIR:-/tmp}/hobbit-uart.XXXXXX")}
trap 'rm -rf "$BUILD"' EXIT

# Copy the sources so bsc never sees (or creates) a .bo next to them: a
# stale in-tree object would make bsc choose between two copies of a
# package, and the source tree must stay free of build products.
mkdir -p "$BUILD/src" "$BUILD/obj"
cp HobbitTypes.bsv HobbitUart.bsv HobbitUartTb.bsv "$BUILD/src/"

(
  cd "$BUILD/src"
  "$BSC" +RTS -K512M -RTS -sim -bdir "$BUILD/obj" -simdir "$BUILD/obj" \
         -info-dir "$BUILD/obj" -g mkUartTb -u HobbitUartTb.bsv
  "$BSC" +RTS -K512M -RTS -sim -bdir "$BUILD/obj" -simdir "$BUILD/obj" \
         -info-dir "$BUILD/obj" -e mkUartTb -o "$BUILD/sim_uart"
)

out=$("$BUILD/sim_uart")
printf '%s\n' "$out"

if printf '%s\n' "$out" | grep -q '^FAIL'; then
  echo "run_uart: FAIL" >&2
  exit 1
fi
if ! printf '%s\n' "$out" | grep -q '^SUMMARY pass=10 fail=0$'; then
  echo "run_uart: did not get SUMMARY pass=10 fail=0" >&2
  exit 1
fi
