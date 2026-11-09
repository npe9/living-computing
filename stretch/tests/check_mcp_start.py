"""Read MCP's bypass-mode start (road item E1) out of a simulation log.

usage: check_mcp_start.py LOG

The log is StretchMcpStartTb's, tests/run_mcp_start_test.sh.  The checks
read the console the way check_console_text.py does, wherever a message was
typed, and the core's own lines.

WHAT THE START IS, in the console's order:
  the IPL program primes SCOMD with CLOCK and BYPASS (printed p.33 lines
  19-44); the command package answers both; JC4 asks for a job card; the
  input program READs the reader and gets End Exception; MCP tells the
  operator; JC4 polls SJ1FUL.

THE ONE FIXTURE IN IT.  The model's reader holds an empty image and answers
a READ with EE EOP (report 00110).  A real empty hopper is not ready.  So
PRESENT JOB REJECTED is this fixture's, and it goes when E2 and E3 give the
reader a deck.  SERVICE THE CARD READER is what C22-6678-1 says the system
types when it "expects more cards and will not reference the reader until
the system gets the channel signal from the reader".

MEASURED FAILURE SETS.  This checker was run on the logs of whole runs of
the model, one for each state of the four fixes on the way here
(docs/boot_plan.md, "THE START RUNS TO THE READER").  They are cumulative, so
a log also holds every later fault; only the decimal store's row is one fault
alone.  None of those runs had this bench's stop, so
polling_at_zjobc1_200_times fails in all of them, and no_step_cap wherever the
run went to its cap.
  no WRITE end +2 (and none below): the four in-order messages, '//////',
    reader_read_once_ending_ee_eop.
  + WRITE end +2: TIME, BYPASS and PRESENT JOB in order, 'ILLEGAL',
    'ONLINE COMMAND', '//////', no_step_cap.
  + guessed target: TIME in order, 'ILLEGAL', '//////'.
  + blank is 0o20, decimal store still refused: the four in-order messages,
    'MCP ERROR', op_only_at_the_stm_probes [158899],
    reader_read_once_ending_ee_eop.
  all four fixed, run to the old 40M cap: no_step_cap alone, besides the stop.
"""
import re
import sys

from check_console_text import console_text

# The console's messages, in the order they must be typed.
IN_ORDER = [
    "TIME AFTER CALIBRATION 00:00:01",
    "BYPASS COMMAND ACCEPTED.",
    "PRESENT JOB REJECTED - NO JOB CARD.",
    "SERVICE THE CARD READER",
]
# What a fault in the command path types instead.
NEVER = [
    "ILLEGAL",          # ZEREX1, ZABEND: a command refused
    "ONLINE COMMAND",   # BYPASS dispatched one entry high
    "MCP ERROR",        # an interruption MCP treats as its own fault
    "//////",           # the commentator's stack typed as a message
]
# OP is expected at these two: printed p.117 line 7 and p.122 line 7 probe
# for STM on every interruption and clear OP (docs/boot_plan.md).
OP_EXPECTED = {"145014", "145300"}


def checks(log):
    text = console_text(log)
    # The control characters are dropped, and the blanks between words count.
    flat = " ".join(text.split())
    at = 0
    for want in IN_ORDER:
        i = flat.find(want, at)
        yield f"console_types_in_order {want!r}", i >= 0
        if i >= 0:
            at = i + len(want)
    for bad in NEVER:
        yield f"console_never_types {bad!r}", bad not in flat
    ops = set(re.findall(r"OP SET by the instruction at half-word (\d+)", log))
    yield f"op_only_at_the_stm_probes {sorted(ops - OP_EXPECTED)}", ops <= OP_EXPECTED
    rep = "I/O status report, channel 32, EPGK UK EE EOP CS = "
    yield "reader_read_once_ending_ee_eop", \
        len(re.findall(re.escape(rep) + r"00110$", log, re.M)) == 1 \
        and len(re.findall(re.escape(rep), log)) == 1
    yield "polling_at_zjobc1_200_times", \
        "STOPPED DELIBERATELY at half-word 16925" in log
    yield "no_step_cap", "step cap" not in log


def main(argv):
    log = open(argv[1], errors="replace").read()
    fails = 0
    for name, ok in checks(log):
        print(("PASS " if ok else "FAIL ") + name)
        fails += 0 if ok else 1
    print("console:", " ".join(console_text(log).split()))
    if fails:
        print(f"{fails} TEST(S) FAILED")
        return 1
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
