#!/usr/bin/env python3
"""Refuse debug instrumentation in committed files.

>>> WHY THIS EXISTS, AND IT IS NOT HYPOTHETICAL. <<<  On 2026-10-27 a
`git add -A` swept ten probe checks into tests/gen_mcp_boot_tb.py.  The
full suite then reported 5576 PASS lines, zero FAIL lines and "ONE OR
MORE TESTS FAILED" -- because `run()` only echoed `tail -20` and the ten
failures had scrolled past it.  The same day a bisection left a reduced
`step_cap` behind, and a watchpoint left `$display`s in
bsv/StretchStorage.bsv and bsv/StretchCore.bsv.

None of that is a discipline problem worth a reminder; it is a
mechanical problem with a mechanical check.  A probe is a MEASUREMENT,
not a change, and `git add -A` cannot tell the difference -- so this
can.
"""
import sys, os, re, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
fails = 0


def bad(where, why):
    global fails
    print(f"FAIL {where}: {why}")
    fails += 1


# 1. Probe labels and the impossible expectation used to read a word out
#    of a run by making a check fail on purpose.
MARKERS = (
    ("PROBE_", "a probe check label"),
    ("0xDEADBEEFDEADBEEF", "the impossible expectation a probe uses"),
    ("0xdeadbeefdeadbeef", "the impossible expectation a probe uses"),
)
for path in sorted(glob.glob(os.path.join(HERE, "*.py"))):
    if os.path.basename(path) == os.path.basename(__file__):
        continue
    text = open(path).read()
    for marker, why in MARKERS:
        if marker in text:
            bad(os.path.relpath(path, ROOT), f"contains {marker} -- {why}")

# 2. Watchpoint $displays left in the model.
for path in sorted(glob.glob(os.path.join(ROOT, "bsv", "*.bsv"))):
    text = open(path).read()
    for marker in ('$display("WATCH', '$display("CMW'):
        if marker in text:
            bad(os.path.relpath(path, ROOT),
                f"contains {marker} -- a debug watchpoint")

# 3. The MCP boot's step cap must be the canonical one.  A bisection sets
#    it low and a forgotten one makes the boot silently stop early, which
#    looks like a pass.
CANON_CAP = 40000000
boot = os.path.join(HERE, "gen_mcp_boot_tb.py")
caps = re.findall(r"step_cap\s*=\s*(\d+)", open(boot).read())
if not caps:
    bad("tests/gen_mcp_boot_tb.py", "no step_cap found at all")
else:
    # EVERY cap must be canonical, and the COUNT is not the point.
    #
    # This used to demand `caps == ['40000000']` -- exactly one
    # occurrence -- and on 2026-10-30 that refused a legitimate change:
    # gen_mcp_boot_tb.py now emits a SECOND testbench
    # (StretchMcpDecodeTb, which stops at ASSIGN's entry to read what
    # MCP-DECODE built before the reject path clears it), and it passes
    # its own perfectly canonical step_cap.  Two canonical caps are not
    # a probe.
    #
    # The guard is NOT weakened by this.  What it exists to catch is a
    # REDUCED cap left behind by a bisection, which makes the boot stop
    # early and every later check read a half-finished machine -- and a
    # reduced cap anywhere in the file still fails here.  Requiring all
    # of them to be canonical is exactly as strong against that as
    # requiring one of them to be.
    offenders = sorted(set(c for c in caps if c != str(CANON_CAP)))
    if offenders:
        bad("tests/gen_mcp_boot_tb.py",
            f"step_cap(s) {offenders} are not the canonical {CANON_CAP} "
            f"(found {caps})")
    else:
        print(f"PASS all {len(caps)} boot step_cap(s) are the canonical "
              f"{CANON_CAP}")

if fails:
    print(f"{fails} TEST(S) FAILED")
    sys.exit(1)
print("PASS no probe labels, impossible expectations or watchpoints in "
      "committed files")
print("ALL TESTS PASSED")
