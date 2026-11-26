# pim/tools

| File | What it does |
|---|---|
| `mkfepcard.py` | Builds the FEP emulator's SD-card image. |
| `quick_checks.sh` | Runs the one-minute checks: the ten `asm/*.py --check`, savpreds, ptfdump, fepread and every `psi/test_*.py`. Set `QC_WIN=1` to add `bsv/run_win_tb.sh`. Prints one line per failure and a verdict line. |
| `suite_verdict.py LOG` | Gives a one-line verdict on a `run_tests.sh` log: PASS with exactly the 21 intended formal-BMC FAIL lines, or the unexpected lines. It was checked on a real passing log and on three mutated copies: an extra FAIL line, a missing expected line, and a truncated log. Each mutation gives FAIL. |
| `merge_agent.sh BRANCH -m MSG [--push]` | Merges an agent worktree branch. It checks that the branch changed only `pim/`, prints the overlap with master, merges with `--no-ff`, runs `quick_checks.sh`, then pushes and removes the worktree. First used for the espc register-cache merge (7bdf943e). |
| `agent_rules.md` | The standing rules every pim agent follows, so briefs give only the task. |
| `skills/` | Claude Code skills: `pim-merge`, `pim-agent-brief` and `pim-suite-verdict`. Each is a pointer to the scripts above. They are installed by symlink from `~/.claude/skills/<name>`. |
