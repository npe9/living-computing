#!/bin/sh
# MCP's IPL with MCP's OWN IOD deck, printed p.1 (strap/prosa.py,
# MCP_IODS_P1), then what it typed on the console.
#
# Its own tape path, for the reason run_mcp_assign_test.sh gives: this
# fixture declares a different machine (four tape units, p.1's cards).
# The console is read by tests/check_console_text.py rather than by
# word index -- see that file for why.
set -e
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG="${TMPDIR:-/tmp}/mcp_p1deck.$$.log"
PROSA_IOD_DECK=P1 STRETCH_TAPE="${TMPDIR:-/tmp}/mcp.p1deck.tape" \
  "$TESTS_DIR/run_mcp_assign_test.sh" StretchMcpP1DeckTb > "$LOG" 2>&1 \
  || { cat "$LOG"; rm -f "$LOG"; exit 1; }
grep -v '^CONSOLE ' "$LOG" | tail -12
status=0
PYTHONPATH="$TESTS_DIR/../strap" python3 "$TESTS_DIR/check_console_text.py" "$LOG" "$@" || status=$?
rm -f "$LOG"
exit $status
