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
if [ "$passes" -lt 26 ]; then
  echo "run_smoke: only $passes PASS lines (17 functional + 14 cycle/table)" >&2
  exit 1
fi

# The fixed smoke program retires 41 instructions; each HRI line must
# carry the contract's trailing cyc field.
hris=$(printf '%s\n' "$out" | grep -c '^HRI ' || true)
if [ "$hris" -ne 41 ]; then
  echo "run_smoke: $hris HRI lines, want 41" >&2
  exit 1
fi
if printf '%s\n' "$out" | grep '^HRI ' |
     grep -Evq '^HRI pc=[0-9a-f]{4} insn=[0-9a-f]{8} sp=[0-9a-f]{8}>[0-9a-f]{8} msp=[0-9a-f]{8}>[0-9a-f]{8} we=[0-9] addr=[0-9a-f]{8} data=[0-9a-f]{8} mask=[0-9a-f]{2} trap=[0-9] cyc=[0-9]+$'; then
  echo "run_smoke: an HRI line does not match the fixed format with cyc" >&2
  exit 1
fi
