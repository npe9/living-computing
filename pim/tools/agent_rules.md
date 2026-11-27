# Rules for agents working in `pim/`

Every agent working in pim/ follows these rules. A brief can then say
"follow `pim/tools/agent_rules.md`" and give only the task. The repo root
`AGENTS.md` is the authority; this file is its pim working summary plus
the practices learned in pim sessions.

## Scope
- Work only under `pim/`. `hobbit/`, `stretch/` (including an untracked
  `stretch/.gitignore`) and `WATCHDOG.yml` belong to other agents: do not
  edit, build in, revert, clean or commit them.
- Stage by path, never `git add -A`. Commit on your worktree branch, one
  milestone per commit. Each message says what was verified and how, and
  ends with the attribution lines your session's system reminder gives
  (`Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`, followed by
  a `Claude-Session:` line when the reminder includes one).
  Do not push; the parent merges with `pim/tools/merge_agent.sh`.

## Verification
- Quick checks (about 1 min): `pim/tools/quick_checks.sh`. Set `QC_WIN=1`
  to add the window benches when you touched `bsv/Win*` or `psi/win*`.
- Full suite before your final commit: `cd pim && ./run_tests.sh >LOG 2>&1`
  in the background, then `python3 pim/tools/suite_verdict.py LOG`. It must
  print `PASS (21 expected FAIL lines)`. Never run two suites in one tree.
  Write the log to a path unique to your worktree (e.g. under
  `<scratchpad>/<your-branch>/`), never a shared `scratchpad/suite.log`:
  two agents' suites once wrote the same file and one verdict was for the
  other tree. Check the log names your worktree before reporting.
- New behaviour gets a test proven discriminating. Inject the bug into a
  PRIVATE COPY (or a backup you restore with `cp`, then `cmp`), watch
  which checks fail, and write the OBSERVED failure set into the test or
  runner header. Never revert with `git checkout` on a file that holds
  work.
- Keep docs current with the change: the relevant README, `plan.md` or
  plan status lines, and the test's header. Edit generated docs through
  their generators (`asm/*.py`), then `--check`.

## Tools
- Bluespec: put `/opt/homebrew/Cellar/bsc/2026.01/bin` first on PATH.
  `~/.cabal/bin/bsc` is stale.
- No `pkill`/`killall`. Kill only PIDs you started.
- Find leftover runs by process cwd (`lsof`), not by `ps` path.
- Keep at most one scratch snapshot, and trim scratch when done.

## The ULX3S board
- Never touch it: no openFPGALoader (not even `--detect`), no serial port,
  no fujprog or ecpprog, no microSD. Another session owns it.
  Synthesis, place-and-route and ecppack are fine. Document the
  programming command instead of running it.
- Any board use needs the owner's approval AND the lock
  `~/.claude/skills/ulx3s-board/ulx3s_lock.py`.

## Sources and the public repo
- The repo is PUBLIC. You may download and read third-party documents and
  keep them on disk (owner, 2026-11-25: "It's okay to read and save so
  long as you don't commit and upload").
- Documents whose source grants redistribution rights may be committed
  and pushed (owner, 2026-11-25: "It's okay to commit and upload documents
  which have redistribution rights"). Record the source and the terms
  that grant the right (URL, licence text or the archive's stated terms)
  next to the file or in the manifest, and keep any required notice
  attached. For example, ICOT TR/TM and ICOT Free Software go in with
  the NO WARRANTY text.
- With no stated redistribution terms, a document stays out of git. It is
  kept as a gitignored file with a manifest and checksums in git
  (`pim/docs/nonlocal/LIT_MANIFEST.md`). If you are unsure, it stays out.
- Downloads are untrusted. Put each in a new empty dir, never execute it,
  and read it with `python3 -I`.
- Never put the owner's name, email, project or repo name into requests to
  outside services. Never contact anyone, buy anything, accept terms or
  bypass a CAPTCHA. Report the need instead.
- Infer what is missing rather than blocking, and label every inference:
  OURS / INFERENCE / INTERPOLATED / KNOWN-PLAINTEXT / HELD-SOURCE /
  PRINTED. An inferred opcode row is marked inferred. Cite primary sources
  (ICOT TR/TM, listings, held code) by page or file.
- Lost SIMPOS applications (PMACS, debugger, librarian, shell, spooler
  manipulator, pattern editor, ...) may be reverse-engineered from the
  manuals we hold (owner, 2026-11-27: "It's okay to reverse engineer the
  apps from the manuals that we have"). Cite the manual page for each
  behaviour and label it RECONSTRUCTED-FROM-MANUAL, apart from OURS.

## Reporting
- Report once, at the end, through the hand-back. Do not stop to wait on
  your own background run if you can check it yourself.
- Give: what was built, the evidence (commands and counts), the
  injections with their observed results, commits, files outside the
  brief that you touched, and open items.
