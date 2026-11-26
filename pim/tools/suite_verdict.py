#!/usr/bin/env python3
"""One-line verdict on a pim/run_tests.sh log.

Usage: python3 tools/suite_verdict.py LOG

Prints `PASS (21 expected FAIL lines)` and exits 0 when the log ends with
`=== pim suite: PASS ===` and every line containing FAIL is one of the
intended formal BMC `_bug` lines (exactly 21: the section header, and per
bug case one "expect FAIL" header, three SBY lines and one "FAIL as
expected" line, for four cases).  Otherwise prints FAIL, the reason, and
each unexpected FAIL line with its line number (at most 40), and exits 1.
"""
import re
import sys

EXPECTED_COUNT = 21
BUGS = ("pim_smoke_bug", "pim_multiway_bug", "pim_decode_error_bug",
        "pim_fault_bug")

ALLOWED = [
    re.compile(r"^=== formal BMC \(fixed PASS, buggy FAIL\) ===$"),
    re.compile(r"^=== (buggy smoke|multiway bug|decode error bug|fault bug)"
               r" \(expect FAIL with VCD\) ===$"),
    re.compile(r"^SBY [\d:]+ \[bsv/formal/(%s)\] engine_0: Status returned "
               r"by engine: FAIL$" % "|".join(BUGS)),
    re.compile(r"^SBY [\d:]+ \[bsv/formal/(%s)\] summary: engine_0 \(.*\) "
               r"returned FAIL$" % "|".join(BUGS)),
    re.compile(r"^SBY [\d:]+ \[bsv/formal/(%s)\] DONE \(FAIL, rc=2\)$"
               % "|".join(BUGS)),
    re.compile(r"^(buggy smoke|multiway bug|decode error bug|fault bug): "
               r"FAIL as expected \(rc=2\)$"),
]


def verdict(lines):
    fails = [(i + 1, l.rstrip("\n")) for i, l in enumerate(lines)
             if "FAIL" in l]
    unexpected = [(n, l) for n, l in fails
                  if not any(p.match(l.strip()) for p in ALLOWED)]
    expected = len(fails) - len(unexpected)
    tail = [l.strip() for l in lines if l.strip()][-1:]
    passed = tail == ["=== pim suite: PASS ==="]
    reasons = []
    if not passed:
        reasons.append("last line is %r, not the suite PASS line"
                       % (tail[0] if tail else ""))
    if unexpected:
        reasons.append("%d unexpected FAIL lines" % len(unexpected))
    if expected != EXPECTED_COUNT:
        reasons.append("%d expected FAIL lines, want %d"
                       % (expected, EXPECTED_COUNT))
    return passed and not reasons, reasons, unexpected, expected


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip().splitlines()[2])
        return 2
    with open(argv[1], errors="replace") as f:
        lines = f.readlines()
    ok, reasons, unexpected, expected = verdict(lines)
    if ok:
        print("PASS (%d expected FAIL lines)" % expected)
        return 0
    print("FAIL: " + "; ".join(reasons))
    for n, l in unexpected[:40]:
        print("  %d: %s" % (n, l[:200]))
    if len(unexpected) > 40:
        print("  ... %d more" % (len(unexpected) - 40))
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
