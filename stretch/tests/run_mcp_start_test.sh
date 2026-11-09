#!/bin/sh
# MCP's bypass-mode start (road item E1): IPL with MCP's own IOD deck, the
# command package's CLOCK and BYPASS, the input program's READ of the
# reader, and JC4 polling for a job card.  What it checks, and the measured
# failure sets, are in tests/check_mcp_start.py.
#
# Its own tape path, for the reason run_mcp_assign_test.sh gives.
set -e
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG="${TMPDIR:-/tmp}/mcp_start.$$.log"
PROSA_IOD_DECK=P1 STRETCH_TAPE="${TMPDIR:-/tmp}/mcp.start.tape" \
  "$TESTS_DIR/run_mcp_assign_test.sh" StretchMcpStartTb > "$LOG" 2>&1 \
  || { tail -40 "$LOG"; rm -f "$LOG"; exit 1; }
status=0
if grep -q "TEST(S) FAILED" "$LOG"; then
  grep -E "^FAIL|TEST\(S\) FAILED" "$LOG"
  status=1
fi
PYTHONPATH="$TESTS_DIR/../strap:$TESTS_DIR" python3 "$TESTS_DIR/check_mcp_start.py" "$LOG" || status=$?
rm -f "$LOG"
exit $status
