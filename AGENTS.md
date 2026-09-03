# AGENTS.md

Instructions for AI agents (Claude Code and others) working in this
repository.

## Autonomy

The owner has granted standing permission to **act independently**
(2026-09-02, in-session: "put in agents.md that you can act
independently"). Concretely:

- Pick the next piece of work yourself when told to "keep going" or
  when the current task is finished. Prefer the "next steps" lists in
  `stretch/bsv/README.md`, `stretch/strap/README.md`, and
  `stretch/docs/archival_inventory.md`, in that order of authority,
  but use judgment: a documented candidate that turns out infeasible
  on inspection should be recorded as such, not attempted.
- Commit finished, verified work without asking, one milestone per
  commit, with a message that says what was verified and how.
- Push to `origin` (github.com/npe9/living-computing, private)
  without asking.
- Edit any file in the repo, add files, and update the docs and the
  regression suite as part of the same change.
- Do not ask "shall I proceed?" questions. State assumptions in the
  commit message and the docs, and proceed.

Still ask first for: destructive git operations (history rewrites,
force pushes, branch deletion), deleting files you did not create in
the session, and anything outside this repository.

## Current direction (2026-09-03)

The owner has asked for the model to become the real 7030
microarchitecture: pipelining, look-ahead, and "the other tricks they
did". The staged plan, sources and oracles are in
`stretch/docs/microarchitecture_plan.md`; work from it, keep it
current, and keep the existing regression suite green at every stage
-- it is the correctness oracle for the rewrite.

## How work is verified here

Every claim in the docs is backed by something runnable. Follow the
established pattern:

1. `cd stretch/strap && ./run_tests.sh` is the whole regression suite
   (pure-Python assembler tests, then the Bluesim smoke test, then
   every STRAP program). It must be green before a commit. A full run
   takes roughly ten minutes; run it in the background and keep
   working.
2. New behavior gets a test that is proven **discriminating**: inject
   the specific bug it is meant to catch (in the assembler or in
   `StretchExecute.bsv`), watch the predicted checks fail and nothing
   else, revert, and confirm `git diff` is clean. Write the observed
   failure set into the test's header, not the predicted one.
   Revert an injection by reversing the exact patch (or `git stash`
   the real work first), never with `git checkout <file>` on a file
   that holds uncommitted work: that reverts the work too, and it has
   happened once (the SIC implementation, restored from the session's
   own edit scripts).
3. For anything transcribed from a historical listing, transcribe the
   printed machine-code column too and check it with
   `stretch/strap/listing_oracle.py` before running on the model
   (`verify_ibox1_listing.py` / `verify_ibox4_listing.py` are the
   pattern). IBM's own assembler output is the strongest oracle in
   the project.
4. Encodings and semantics come from primary sources in
   `stretch/docs/` (the Reference Manual, C22-6531, the pocket card,
   the listings), cited by page. Several PDFs have no text layer;
   read the page image. Never infer an instruction's meaning from
   listing usage alone.

## Conventions

- Model scope is "decode completely, execute partially, document the
  rest": an unimplemented instruction fails loud, never silently.
- Generated testbenches (`stretch/bsv/*Tb.bsv`, `build/`, `simbuild/`,
  `*_sim*`) are build products and are gitignored. Never delete by
  glob in `stretch/bsv/`; the hand-written smoke test was lost that
  way twice before it was renamed `StretchSmoke.bsv`.
- Docs to keep current with any change: the relevant README(s), the
  test program's own header comment, and `docs/archival_inventory.md`
  when a transcription target's status changes.
- The project memory file (outside the repo) records session-level
  reasoning; the repo docs must stand on their own without it.
