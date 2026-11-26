---
name: stretch-batch-merge
description: Merge one or more verified Stretch branches (agent worktree branches) into master through a batch worktree and a full suite run, then push and clean up. Use whenever finished Stretch work is ready to land on master.
---

# Landing Stretch work on master

Several agents work in this repository at once (hobbit/, pim/, stretch/), so
master moves under you. The rule is that the suite must be green on the
EXACT merged tree before it reaches master.

## Steps

```sh
R=/Users/npe/src/living-computing
S=<session scratchpad>
BASE=$(git -C $R rev-parse master)
git -C $R worktree add $S/batchNN -b batchNN master
cd $S/batchNN
git merge --no-ff <branch1> [<branch2> ...]      # resolve conflicts here
```

1. **Resolve the conflicts in the batch tree.**
   - Deck-count pins sum (see `stretch-suite-verdict`).
   - Timing pins come from whichever side has the newer timing source.
   - For conflicts inside code, ask the authoring agent (SendMessage) when it
     is still alive.
2. **Run the full suite** as a run_in_background command:
   ```sh
   $S/batchNN/stretch/tests/suite_bg.sh run $S/bNN    # private tape, HALT_REPORT, .done verdict
   ```
   Judge `$S/bNN.log` with `stretch-suite-verdict`; `suite_bg.sh status $S/bNN`
   gives the wrapper's GREEN/RED/KILLED. On red, fix in the batch tree and
   re-run.
3. **Check that master's stretch/ has not moved** since the batch base:
   ```sh
   git -C $R diff --stat $BASE master -- stretch    # must print nothing
   ```
   Changes elsewhere (pim/, hobbit/) do not matter. If stretch/ moved, merge
   master into the batch and re-run the suite.
4. **Merge and push** from the main tree, staging nothing by hand:
   ```sh
   cd $R && git merge --no-ff batchNN -m "Merge ...: <what>; suite green (<log facts>)

   Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
   git push origin master
   ```
   The repo is PUBLIC. Third-party papers without redistribution terms stay
   out of git (manifest plus checksums only).
5. **Clean up** merged, clean worktrees: `git worktree remove -f -f <path>`
   (the double `-f` handles locked agent worktrees). Keep a branch that
   another live agent based its work on. Delete only branches you made, with
   `git branch -d` (never `-D` without asking).

## Never

- `git add -A` or `git add .` at the repo root: it sweeps sibling machines'
  work in. Stage by path, or use `git add -u -- stretch` inside a private
  worktree.
- Commit or merge red, or "fix forward" on master.
- Force-push, rewrite history, or delete files you did not create without
  asking the owner.
- Revert with `git checkout <file>` on a file holding uncommitted work. Use
  the exact inverse patch.
- Start agents or a suite when free disk is under 12 GiB (`df -g`).
