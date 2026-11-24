#!/bin/sh
# Boot smoke test: diags.dsk to the Alto Executive.
#
# Standard: REGRESSION ONLY.  The pass condition is the SHA-256 of the
# display field the model writes after ALTO_CYCLES microcycles, recorded
# from this model on 2026-11-24 when the frame was inspected by eye and
# showed the Executive banner and prompt.  It is not a primary-source
# oracle: it detects change, not correctness.  A primary oracle (the
# printed Alto microcode listings) is still to be acquired; see
# ../docs/README.md.
#
# Discrimination, observed 2026-11-24 (see ../README.md, "Tests"):
# the injected bug listed there changes the frame hash and this script
# exits 1; with the injection reverted it exits 0.
#
# Needs rom/rom_arrays.h and disks/diags.dsk held locally (MANIFESTs).
set -e
# bsc install; keep in step with the Makefile (bluetcl must be on PATH).
BSC_HOME=${BSC_HOME:-/opt/homebrew/Cellar/bsc/2026.01}
export PATH="$BSC_HOME/bin:$PATH" BLUESPECDIR="${BLUESPECDIR:-$BSC_HOME/libexec/lib}"
HERE=$(cd "$(dirname "$0")/.." && pwd)
CYCLES=${CYCLES:-60000000}
GOLDEN="$HERE/tests/golden/diags_exec_60M.sha256"

test -f "$HERE/disks/diags.dsk" || { echo "SKIP: disks/diags.dsk not held (disks/MANIFEST.md)"; exit 2; }
(cd "$HERE" && make -s sim)

T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
(cd "$T" && ALTO_DISK="$HERE/disks/diags.dsk" ALTO_CYCLES=$CYCLES \
    ALTO_FRAME="$T/frame.pbm" "$HERE/build/alto-sim" >"$T/log" 2>&1) \
  || { tail -20 "$T/log"; echo "FAIL: simulator exited non-zero"; exit 1; }
test -f "$T/frame.pbm" || { echo "FAIL: no display field written"; exit 1; }

got=$(shasum -a 256 "$T/frame.pbm" | cut -d' ' -f1)
if [ "${RECORD:-0}" = 1 ]; then
  echo "$got" >"$GOLDEN"; cp "$T/frame.pbm" "$HERE/build/diags_exec.pbm"
  echo "recorded $got (frame copied to build/diags_exec.pbm for inspection)"; exit 0
fi
want=$(cat "$GOLDEN")
if [ "$got" = "$want" ]; then echo "PASS: diags.dsk Executive frame $got"; exit 0; fi
cp "$T/frame.pbm" "$HERE/build/diags_exec_FAIL.pbm"
echo "FAIL: frame $got, expected $want (build/diags_exec_FAIL.pbm)"; exit 1
