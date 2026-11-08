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
# The testbench's own checks count too: a run that reports a FAILED check
# fails here, whatever MCP typed.
if grep -q "TEST(S) FAILED" "$LOG"; then status=1; fi
# Printed p.159 line 8, "LVE,0,K IOD RN-.32" at 220023.40 (half-word
# 147495), is a CHAINED LVE.  MCP runs it disabled, so a model that
# refuses the chain does not divert the counter: the OP waits as an
# indicator, and the run reaches the same stop with the same console.
# The core's own "OP SET" line is what tells the two apart (measured,
# docs/boot_plan.md).
if grep -q "OP SET by the instruction at half-word 147495$" "$LOG"; then
  echo "FAIL p159_chained_lve_refused: OP set by the LVE at 220023.40"
  status=1
fi
# THE DISK'S TWO REPORTS, and no End Exception.  MCP's IPL writes 24
# arcs to the disk; a disk too small for them ends that WRITE with EE,
# MCP receives the EE when it first enables, and its error path reaches
# the same BEW,$ the testbench's pc_check pins -- so the PC cannot tell
# the two runs apart, and these lines can.  The four EOPs are DISK
# FETCH's (printed pp.311-318), all through p.177's IOD routine: LOCATE
# and READ of the dictionary's first arc (p.317 lines 23-31), then LOCATE
# and READ of the index arc (lines 35-43).  The second pair needs MCP's
# interrupt queue to unstack correctly, which needed M-1 to subtract
# (decks/vfl_m_minus_one.strap); before that fix there were two.
#
# EIGHT SINCE 2026-11-07, when PROSA gained its reconstructed dictionary
# and index (strap/prosa_dict.py) and DISK FETCH stopped answering
# "TYPE NOT IN INDEX".  The fetch of 22SCOMD adds four more: LOCATE and
# READ of the dictionary arc for type 22 (p.312 lines 17-26), then
# LOCATE and READ of the type area (p.312 line 51 on).  The run now
# stops at J COMD, the command package's entry (gen_mcp_boot_tb.py).
#
# MEASURED 2026-11-07 (the end was then 149580, K UNSTC): with the host
# build put back on mkDiskSourceSmall (StretchIO.bsv), exactly
# p1_disk_end_exception and p1_disk_eop_reports ("0 channel-0 EOP
# reports") failed, while the testbench's PC checks PASSED -- MCP's EE path
# ended at the same BEW,$.  The end is now 156886 (gen_mcp_boot_tb.py), so
# re-measured below in run_tests.sh's entry.
REP="StretchCore: I/O status report, channel 0, EPGK UK EE EOP CS ="
if grep -q "$REP 00100$" "$LOG"; then
  echo "FAIL p1_disk_end_exception: channel 0 reported EE"
  status=1
fi
n=$(grep -c "$REP 00010$" "$LOG" || true)
if [ "$n" != 8 ]; then
  echo "FAIL p1_disk_eop_reports: $n channel-0 EOP reports, expected 8"
  status=1
fi
PYTHONPATH="$TESTS_DIR/../strap" python3 "$TESTS_DIR/check_console_text.py" "$LOG" "$@" || status=$?
rm -f "$LOG"
exit $status
