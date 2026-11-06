#!/usr/bin/env bash
# merge_gate.sh -- the MCP-listing subset of run_tests.sh, for landing
# a batch of transcribed pages without waiting on the full suite.
#
# It runs the SAME run lines run_tests.sh runs, selected by script
# name, so it cannot drift from the suite: a check added to
# run_tests.sh under one of these names is in the gate the next time
# the gate runs.  It is a gate, not a replacement -- the full suite
# still runs before every other batch lands, because a transcription
# can break a check this subset does not select (2026-11-05: the
# label floor in check_listing_reading, and the p.44 tail-block scan).
#
# Usage: cd tests && ./merge_gate.sh      (exit 1 on any failure)
cd "${GATE_DIR:-$(dirname "$0")}" || exit 2
export PYTHONPATH="../strap:../tools:.${PYTHONPATH:+:$PYTHONPATH}"

SELECT='verify_mcp_page\.py|verify_mcp_bootstrap_p[0-9_p]+\.py|check_mcp_body_image|check_symbol_spellings|verify_merge_dds_guard|check_instruction_label_dds|check_comment_mark|check_listing_reading|check_statement_confirm'

fails=0 ran=0
run() {
  local name="$1"; shift
  ran=$((ran + 1))
  local out
  if ! out="$("$@" 2>&1)"; then
    fails=$((fails + 1))
    echo "FAIL [$name]"
    printf '%s\n' "$out" | grep -E '^FAIL|Error|error:' | head -5 | sed 's/^/    /'
  fi
}

start=$(date +%s)
while IFS= read -r line; do
  eval "$line"
done < <(grep -E '^run ' run_tests.sh | grep -E "python3 ($SELECT)")

echo "merge gate: $ran checks, $fails failed, $(( $(date +%s) - start ))s"
[ "$fails" -eq 0 ]
