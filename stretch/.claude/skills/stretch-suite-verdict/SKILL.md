---
name: stretch-suite-verdict
description: Decide whether a Stretch regression-suite log (stretch/tests/run_tests.sh output) is green, and what to do when it is not. Use whenever a suite run finishes, before any commit or merge, and when reading an agent's reported suite result.
---

# Reading a Stretch suite log

The suite is `cd stretch/tests && ./run_tests.sh` (about 1,200 sections, 1-4 h
on the loaded machine). Its exit code and last line are NOT enough on their
own. Apply every step below.

## Verdict

Runs started with `tests/suite_bg.sh run PREFIX` already write this verdict
to `PREFIX.done` (GREEN / RED / KILLED, with counts). Still read the FAIL
lines yourself before merging. By hand:

```sh
L=<log>
tail -1 "$L"                                   # must be: All regression tests passed.
grep '^FAIL' "$L" | grep -v 'UNREPRODUCED, expected'   # must print NOTHING
grep -c 'UNREPRODUCED, expected' "$L"          # expected: 2 or 4 (see below)
```

- The only acceptable FAIL lines are `FAIL (UNREPRODUCED, expected) p359_l41_1e512`
  and `FAIL (UNREPRODUCED, expected) p359_l42_9e615`. Each may appear once or
  twice. Anything else is red.
- List ALL the unexpected FAIL lines, not just the first. A cluster usually has
  one cause, and reporting only the first hides the rest.
- A log that stops without the final line is an interrupted run, not a pass.
  Find the survivors by their working directory (`lsof -d cwd | grep <tree>`),
  not by `ps` path. Two runs in one tree share the script file.

## When it is red

1. **Is the probe the broken thing?** Check for these tooling causes before
   suspecting the model:
   - a shared tape: no private `STRETCH_TAPE`, so concurrent MCP runs clobber
     each other
   - a stale `bsv/build` that `atlas_oracle.py` wrote into
   - a full disk
   - a second suite in the same tree
2. **Stale pins.** A branch older than a timing change carries old
   `CYCLES`/clock pins. A CYCLES mismatch after a merge, on a deck the branch
   never touched, is usually a pin to take from master, not a regression.
   Move a pin only with a source or a proven cause.
3. **Deck-count pins.** `tests/check_strap2_punch.py` ("A1 decks whose cards
   load to their image") and `tests/check_strap2_vletable.py` ("the decks
   walked") pin the total deck count, with a running history in the trailing
   comment. Two branches that each add decks will both bump the pin, and the
   merged value is the sum. Extend the history comment and do not drop
   either branch's entry.
4. Re-run only after naming a cause. Never re-run until it passes.

## Baseline comparisons

With `STRETCH_HALT_REPORT=1` every program prints
`HALTREPORT cycles=N memreads=M`. To show that a behaviour-preserving change
moved no unpinned clock, diff those lines against a baseline log of the base
commit.
