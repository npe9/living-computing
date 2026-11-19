#!/bin/sh
# run_formal.sh -- regenerate the Verilog snapshots and run the formal
# checks.
#
#   fixed tree          expected PASS
#   injected variant    expected FAIL with a VCD witness
#
# sby resolves [files] against its own working directory, and the .sby
# files name sources from the repository root, so run sby from there.

set -eu
cd "$(dirname "$0")"
./gen_verilog.sh
root=$(cd ../.. && pwd)
cd "$root"

expect_pass () {
  name=$1
  cfg=$2
  echo "=== $name (expect PASS) ==="
  if sby -f "$cfg"; then
    echo "$name: PASS"
  else
    echo "$name: UNEXPECTED FAIL" >&2
    exit 1
  fi
}

expect_fail () {
  name=$1
  cfg=$2
  vcd=$3
  echo "=== $name (expect FAIL with VCD) ==="
  if sby -f "$cfg"; then
    echo "$name: UNEXPECTED PASS" >&2
    exit 1
  else
    rc=$?
    echo "$name: FAIL as expected (rc=$rc)"
    if [ ! -s "$vcd" ]; then
      echo "$name: missing VCD $vcd" >&2
      exit 1
    fi
    echo "witness: $vcd"
  fi
}

expect_pass "fixed smoke"        bsv/formal/pim_smoke.sby
expect_fail "buggy smoke"        bsv/formal/pim_smoke_bug.sby \
            bsv/formal/pim_smoke_bug/engine_0/trace.vcd

expect_pass "multiway fixed"     bsv/formal/pim_multiway.sby
expect_fail "multiway bug"       bsv/formal/pim_multiway_bug.sby \
            bsv/formal/pim_multiway_bug/engine_0/trace.vcd

expect_pass "decode error fixed" bsv/formal/pim_decode_error.sby
expect_fail "decode error bug"   bsv/formal/pim_decode_error_bug.sby \
            bsv/formal/pim_decode_error_bug/engine_0/trace.vcd

expect_pass "fault fixed"        bsv/formal/pim_fault.sby
expect_fail "fault bug"          bsv/formal/pim_fault_bug.sby \
            bsv/formal/pim_fault_bug/engine_0/trace.vcd
