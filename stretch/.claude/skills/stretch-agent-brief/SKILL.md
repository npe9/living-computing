---
name: stretch-agent-brief
description: Template of standing constraints to paste into every brief for a subagent doing Stretch work (stretch/ in the living-computing repo). Use whenever launching an Agent for Stretch: transcription, model changes, the Bluespec rewrite, synthesis, docs.
---

# Briefing a Stretch agent

A subagent knows only its brief. Every brief needs: the goal, the files to
study first (name the closest existing PATTERN to copy), what is already
ruled out, the definition of done, and the block below, pasted verbatim.
Launch with `isolation: "worktree"` and `run_in_background: true`.

## Paste this block

```
Read AGENTS.md at the repo root first. Rules, all binding:
- Scope: edit, build, clean and commit ONLY under stretch/. Never touch
  hobbit/ or pim/, even if git status shows them modified. Stage by path;
  never `git add -A` / `git add .`.
- Suite: `stretch/tests/suite_bg.sh run <prefix>` (prefix = a path in
  your worktree, no extension), launched as a run_in_background command
  (1-4 h); it sets a private STRETCH_TAPE and STRETCH_HALT_REPORT=1 and
  writes <prefix>.log, .status, .done (verdict GREEN/RED/KILLED) and, if
  killed, .killed. `suite_bg.sh status <prefix>` checks it. Green means
  "All regression tests passed." and no FAIL lines except
  `FAIL (UNREPRODUCED, expected) p359_l41_1e512` / `p359_l42_9e615`.
- Waiting: rely on the run_in_background notification, or
  `suite_bg.sh wait <prefix>`. NEVER wait with `pgrep -f <name>` or any
  loop keyed on a script name: it matches other agents' suites and never
  ends (an agent lost 3.5 h that way, 2026-11-25). If your suite is
  KILLED, report it with the time; do not silently retry.
- New checks must be proven discriminating: inject the bug, record the
  OBSERVED failure set in the test header, revert by the exact inverse
  patch (never `git checkout <file>`), confirm `git diff` is clean.
- Sources: cite the Reference Manual / listings by printed page (and PDF
  page). Many PDFs have no text layer; read the page image. Timing pins
  move only with a source or a proven cause. Unimplemented behaviour
  fails loud.
- Transcriptions: transcribe the printed machine-code column too and
  check it bit-exact with tests/listing_oracle.py before running on the
  model.
- Processes: never pkill/killall by name; kill only PIDs you started.
- Hardware: never program or detect the ULX3S board (another agent uses
  it).
- Toolchain: use the Homebrew bsc that run_tests.sh uses
  (/opt/homebrew/Cellar/bsc/2026.01/bin/bsc), not ~/.cabal/bin/bsc and
  not a development bsc.
- atlas_oracle.py and synthesis: give them their own build directory,
  never the shared stretch/bsv/build.
- Disk: keep at most one scratch snapshot; delete your temp build dirs.
- Never delete by glob in stretch/bsv/.
- The repo is public: no third-party documents without redistribution
  terms in git.
- Commit BEFORE starting a suite run, so the .status head= is the commit
  being verified (a 2026-11-26 run recorded the commit before its change).
- Commit on your worktree branch, one milestone per commit, message says
  what was verified and how, ending with
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
  Do not push; do not merge to master.
Report: branch + HEAD, suite log path and its FAIL lines, what was
verified and how, injection results, anything left undone and why.
```

## Also

- One agent must always be on the idiomatic-Bluespec rewrite
  (`docs/fidelity_plan.md` track A, `docs/microarchitecture_plan.md` §1c).
- Do not give two agents overlapping files. `StretchExecute.bsv` and
  `run_tests.sh` are the usual collision points, so say which arms or
  sections belong to which agent.
- On every "waiting on its own background work" notification that has
  gone on for over ~4 h, run `stretch/tests/agent_health.sh <scratchpad>`:
  it shows each worktree's working processes (by cwd), its newest suite
  log and how it ends (PASS-LINE / FAILED / KILLED / mid), and any
  waiter keyed on a process name. A KILLED log with no working process
  means the agent is stuck, not busy.
- When the agent reports, verify its suite log yourself with
  `stretch-suite-verdict` before merging (`stretch-batch-merge`). An
  agent's confident summary is not evidence.
