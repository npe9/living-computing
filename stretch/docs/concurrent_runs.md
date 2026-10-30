# Running the suite while other agents work in this repository

**Written 2026-10-29, after two separate corruptions in one day and a
third hazard observed live.** This repository is worked by many agents
at once — `git worktree list` reports **48 worktrees**, and `git status`
from the root routinely shows two dozen sibling machine projects being
modified. The Stretch test harness was written for one runner at a time
and says so nowhere.

## THE SHARED STATE, AND IT IS BIGGER THAN IT LOOKS

Ten scripts compile into the SAME two directories:

```
tests/run_program.sh      tests/run_add_family.sh   tests/run_card_test.sh
tests/run_disk_test.sh    tests/run_io_test.sh      tests/run_ipl_test.sh
tests/run_mcp_p17.sh      tests/run_tape_test.sh    bsv/build.sh
bsv/run_tb.sh
```

all with `-bdir build -simdir simbuild`. **And the directories are only
part of it.** Two concurrent runs also collide on:

* the GENERATED TESTBENCH SOURCES — `gen_tb.py` writes
  `bsv/$MODULE.bsv`, and two runs generating the same module name
  overwrite each other's source;
* the SIMULATOR BINARIES — `bsv/${MODULE}_sim` and `bsv/stretch_sim`;
* `bsv/build-hosttape` / `simbuild-hosttape`, shared by every MCP boot.

So "give each run its own `-bdir`" is a necessary fix and NOT a
sufficient one.

## WHAT IT LOOKS LIKE WHEN IT BITES

**Symptom 1 — Bluesim refuses the model.**

```
Error: model  creation time (Thu Oct 29 16:59:20 EDT 2026) does not match
```

The `.so` and the executable were built from `.bo` files another job
replaced in between. MEASURED: a run with this showed **six fewer
passes** and three such errors, and the passes it lost were in sections
that had nothing to do with the change under test.

**Symptom 2 — the suite finishes its tests and never prints a verdict.**

```
rm: .../bsv/simbuild: Directory not empty
```

`run_tests.sh` has `set -e` and ends by removing the shared build
directories. If another job is writing into them, the `rm` fails and
the script exits BEFORE `echo "All regression tests passed."`. Every
test ran and none failed, but the line a reader looks for is absent.
**Do not read a missing verdict as a failure, and do not read it as a
pass either — count the FAIL lines.**

## >>> THE RULE WHILE THIS IS UNFIXED <<<

1. **Check before you start**: `pgrep -fl run_tests.sh`. If another
   suite is running, yours will share its build directories and
   neither result is trustworthy.
2. **NEVER edit `run_tests.sh`, `run_program.sh` or any `run_*.sh`
   while a suite is running.** `sh` reads a script by BYTE OFFSET, so
   editing one mid-run makes the running shell resume at the wrong
   place in a changed file. This is an existing project rule; the new
   part is that the suite may be SOMEONE ELSE'S.
3. **A result obtained concurrently carries a caveat.** Say so when
   quoting it.

## THE FIX, WHEN THE REPOSITORY IS QUIET

A per-run prefix honoured by every script, defaulting to today's names
so nothing changes for a solo runner:

```sh
BDIR="${STRETCH_BDIR:-build}"
SIMDIR="${STRETCH_SIMDIR:-simbuild}"
```

with `run_tests.sh` exporting `STRETCH_BDIR=build-run$$` and cleaning
it up, and the generated sources and binaries moved under the same
prefix. `tests/run_divbox_test.sh` already does the directory half of
this (`build-divbox`, `simbuild-divbox`), which is why it is the one
script that cannot collide.

A cheaper interim that solves suite-versus-suite only: an atomic lock
in `run_tests.sh` —

```sh
if ! mkdir "$BSV_DIR/.suite.lock" 2>/dev/null; then
  echo "another suite is running; refusing to share bsv/build" >&2; exit 1
fi
trap 'rmdir "$BSV_DIR/.suite.lock" 2>/dev/null' EXIT
```

— which does nothing for a bare `run_program.sh`, but that is the rarer
case.

## errno=28 IS THE NEIGHBOUR, NOT A REGRESSION (pre-registered 2026-10-29)

A suite run on 2026-10-29 reported `*** ONE OR MORE TESTS FAILED ***`
over **5632 PASS and 0 FAIL lines**.  Three sections had died on:

```
ld: write() failed, errno=28 (No space left on device) for 'StretchFpAddExpTb_sim.so'
clang++: error: linker command failed with exit code 1
```

The cause was **outside this repository**: a live `xargs -P 8` run in
`/Users/npe/src/bsc-cursor-ergo` holding ~51 GB of scratchpad on the
same volume.  Nothing in `bsv/` or `tests/` was at fault, and that
other repository's work was left alone.

**Pre-registered, so it is not re-diagnosed:** if a suite reports
`errno=28` or `No space left on device`, check
`df -h /System/Volumes/Data` and `du -sm /private/tmp/claude-501/*`
FIRST.  Re-run; do not bisect, and do not touch another project's
files to make room.

Two things changed in `run_tests.sh` because of this run, and they are
the lasting value of it:

* The lock trap was being **silently discarded**.  `trap cleanup EXIT`
  was set, then `trap 'rm -f "$TMPOUT"' EXIT` four lines later; a
  second trap for the same signal REPLACES the first, so every suite
  leaked `bsv/.suite.lock` and the next suite refused to start.  Both
  cleanups now live in one `cleanup()`.  Measured: fixed releases on
  exit 0 and exit 1, the injected double-trap leaks on both.
* A section exiting non-zero with no FAIL lines now **names itself**
  (`*** SECTION FAILED (exit N): <name> ***`) and the epilogue prints
  a `*** FAILING SECTIONS ***` list.  Finding the three FP sections by
  hand took a dozen greps.
