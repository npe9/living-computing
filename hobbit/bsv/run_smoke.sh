#!/bin/sh
# Build and run the ATT92010 Hobbit Bluesim smoke test.
# Use BSC_BIN to pin a compiler; otherwise take the newest Homebrew Cellar
# install.  A bare `bsc` from PATH may be a cabal build whose bluetcl does
# not match the wrapper.
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

# The image, not a BSV literal, is the program.  SmokeImage.bsv is a
# build product and is gitignored.
python3 mk_image_bsv.py smoke.hex SmokeImage > SmokeImage.bsv

# The 256-word register-vector memory makes bsc's elaborator deep; give
# the Haskell runtime a larger stack than its 33 KB default.
"$BSC" +RTS -K512M -RTS -sim -g mkHobbitSmoke -u HobbitSmoke.bsv
"$BSC" +RTS -K512M -RTS -sim -e mkHobbitSmoke -o sim_smoke

out=$(./sim_smoke)
printf '%s\n' "$out"

if printf '%s\n' "$out" | grep -q '^FAIL'; then
  echo "run_smoke: FAIL" >&2
  exit 1
fi
passes=$(printf '%s\n' "$out" | grep -c '^PASS ' || true)
if [ "$passes" -lt 5 ]; then
  echo "run_smoke: only $passes PASS lines" >&2
  exit 1
fi
