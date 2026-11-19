#!/bin/sh
# run_formal.sh -- regenerate the Verilog snapshots and run both BMC jobs.
#
#   fixed  expected PASS
#   buggy  expected FAIL with a VCD witness
#
# sby resolves [files] against its own working directory, and the .sby
# files name sources from the repository root, so run sby from there.

set -eu
cd "$(dirname "$0")"
./gen_verilog.sh
root=$(cd ../.. && pwd)
cd "$root"

echo "=== fixed tree (expect PASS) ==="
if sby -f bsv/formal/pim_smoke.sby; then
  echo "fixed: PASS"
else
  echo "fixed: UNEXPECTED FAIL" >&2
  exit 1
fi

echo "=== reverted fetched-operand regression (expect FAIL) ==="
if sby -f bsv/formal/pim_smoke_bug.sby; then
  echo "bug: UNEXPECTED PASS" >&2
  exit 1
else
  echo "bug: FAIL as expected"
  echo "witness: bsv/formal/pim_smoke_bug/engine_0/trace.vcd"
fi
