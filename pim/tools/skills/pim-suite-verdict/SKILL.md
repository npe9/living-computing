---
name: pim-suite-verdict
description: Run or judge the full pim regression suite (pim/run_tests.sh) and get a one-line verdict - PASS with exactly the 21 intended formal-BMC FAIL lines, or the unexpected FAIL lines with line numbers - instead of reading the 7000-line log. Use whenever the pim suite is run, a suite log needs checking, or an agent claims the suite passed.
---

# The pim suite verdict

Run the suite in the background, then judge its log:

```sh
cd /Users/npe/src/living-computing/pim   # or the agent's worktree pim/
./run_tests.sh > "$SCRATCH/suite.log" 2>&1   # run_in_background (it is long)
python3 tools/suite_verdict.py "$SCRATCH/suite.log"
```

- A good run prints `PASS (21 expected FAIL lines)`, exit 0.
- Otherwise it prints `FAIL: <reasons>` and up to 40 unexpected FAIL
  lines, exit 1. The reasons can be: the last line is not
  `=== pim suite: PASS ===`, unexpected FAIL lines, or an expected count
  other than 21.
- The 21 allowed lines are the formal BMC header, and for each of
  `pim_smoke_bug`, `pim_multiway_bug`, `pim_decode_error_bug` and
  `pim_fault_bug`: the "expect FAIL" header, three SBY lines and the
  "FAIL as expected" line.
- If a new intentional-failure case is added to `bsv/formal`, update
  `EXPECTED_COUNT` and `BUGS` in `tools/suite_verdict.py` in the same
  commit.

Never run two suites in one tree. The suite builds into shared `bsv/`
build dirs, so check by process cwd first:
`lsof -a -d cwd -c python3 -c bsc`.

For the 1-minute subset, use `tools/quick_checks.sh`.
