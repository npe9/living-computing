#!/usr/bin/env python3
"""check_schedule.py -- guard against a core rule silently blocking another.

The core's every-clock rules (rl_la_fetch, rl_ic_controls) cannot carry
`fire_when_enabled`: they share bus channels with the exported `mem`
interface, and at mkStretchCore's synthesized boundary bsc must assume
the harness could call those methods in a ticked clock (plan §1c step
5a). So nothing at compile time asserts that no CORE rule is ever
blocked by another core rule -- a future edit that makes, say,
rl_prepare conflict with rl_ic_controls would compile and simply drop
clocks. This reads bsc's `-show-schedule` output for mkStretchCore and
fails if any rl_* rule lists another rl_* rule (or a __me_check) among
its "Blocking rules"; exported harness methods (mem_*, io_*, setPC ...)
are the only blockers allowed.

The .sched file is written only by a bsc invocation that actually
elaborates mkStretchCore (an up-to-date .ba is not re-elaborated), so
EVERY script that compiles a testbench passes -show-schedule
(build.sh and the tests/run_*.sh runners); then the schedule exists
whenever the core file does, whichever script built it first.

Usage: check_schedule.py build/mkStretchCore.sched
"""
import re, sys

def main(path):
    text = open(path).read()
    rules = text.split("Rule schedule", 1)[1] if "Rule schedule" in text else text
    fails = 0
    checked = 0
    for m in re.finditer(r"^Rule: (\S+)\n(.*?)(?=^Rule: |\Z)", rules, re.S | re.M):
        name, body = m.group(1), m.group(2)
        if not name.startswith("rl_"):
            continue
        checked += 1
        bm = re.search(r"Blocking rules:\s*(.*)", body)
        blockers = [b.strip() for b in bm.group(1).split(",") if b.strip()] if bm else []
        core_blockers = [b for b in blockers if b.startswith("rl_") or b.startswith("__me_check")]
        if core_blockers:
            print(f"FAIL {name} is blocked by core rule(s): {', '.join(core_blockers)}")
            fails += 1
        else:
            print(f"PASS {name}: blockers are harness methods only ({len(blockers)})")
    if checked == 0:
        print("FAIL no rl_* rules found in", path)
        fails += 1
    print("ALL TESTS PASSED" if fails == 0 else f"{fails} TEST(S) FAILED")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
