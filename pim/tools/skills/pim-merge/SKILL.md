---
name: pim-merge
description: Merge a finished agent worktree branch into master for the living-computing pim/ project - scope check, overlap, merge --no-ff, doc checks and PSI tests (plus window benches when relevant), push, worktree and branch cleanup - in one command with one-line output. Use whenever a pim agent hands back a branch to merge, or when asked to merge/land/integrate pim agent work.
---

# Merging a pim agent branch

One command does the whole procedure:

```sh
/Users/npe/src/living-computing/pim/tools/merge_agent.sh BRANCH -m "Merge <milestone>: <what was verified and how>" --push
```

- It checks that you are on master, that pim/ is clean, and that the
  branch touches nothing outside `pim/`. It prints the files both sides
  changed, then merges with `--no-ff`.
- It runs `pim/tools/quick_checks.sh`: ten doc checks, savpreds, ptfdump,
  fepread and every `psi/test_*.py`, which takes about 1 min. It adds
  `bsv/run_win_tb.sh` (about 2 min) when the merge touched `bsv/Win*` or
  `psi/win*`.
- With `--push` it pushes, then unlocks and removes the worktree and runs
  `git branch -d` on the branch.
- The commit trailer is appended if missing.

Exit codes:

| Code | Meaning | What to do |
|---|---|---|
| 0 | done | Nothing. |
| 1 | a check failed | The merge commit is left unpushed. Read the log the script names, fix it or undo it with `git reset --merge ORIG_HEAD` (that is a history change: only on your own unpushed merge). |
| 2 | precondition failed | Fix what it names. |
| 3 | conflict | The merge is left in progress. Resolve it (keep both sides of README sections, using `python3 -I` edit scripts), `git add` by path, `git commit --no-edit`, then rerun with `--no-merge --push`. |

Before merging, read the agent's report for:
- edits outside its brief;
- open items;
- downloads (allowed to keep on disk, never committed).

The full suite is not run here: the agent ran it and reported
`suite_verdict.py`'s line. Run it yourself (skill `pim-suite-verdict`)
only when the report lacks that line or the merge had a conflict in code.
