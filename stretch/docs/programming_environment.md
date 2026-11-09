# The full programming environment: what it means here, and the road to it

The owner's direction, 2026-11-07: "we want to get the full programming
environment running". This file says what that can mean for a 7030
whose software survives only on paper, and what is in the way.

## What survives, and what does not

| piece | state | source |
|---|---|---|
| MCP, the operating system | transcribed from the March 1963 listing, assembled bit-exact, boots to its idle loop | `docs/MCP_Mar63_*.pdf`, `decks/mcp_bootstrap_p*.strap` |
| MCP's input program, command package, loader and DISK FETCH | transcribed as part of MCP (pp.214-236, p.375, pp.311-318) | same |
| MCP Loader / BSS processor | documentation only | `C28-6379-0_MCP_Loader.pdf` |
| STRAP II, the assembler | internals guide only; its own listing is not located | `C22-6729`; `archival_inventory.md` §2 |
| FORTRAN IV | manual only; no compiler source | `C22-6751_7030_FORTRAN_IV_May63.pdf` |
| a machine-readable system tape | **none survives** | `archival_inventory.md` "Holdings now complete" |

**The target is IBM's environment, not a substitute for it.** The
owner, 2026-11-07: "the goal is to replicate the environment in the best
fidelity that we can", and then: "Even if you can't find all the
documentation, it's fine to recreate to the best of your ability." So
each piece goes through three steps:

1. **Find it.** That means IBM's own listing or deck, in an archive.
   `archival_inventory.md` lists what has been searched, what needs a
   request, and the requests ranked by value.
2. **If it is lost, reconstruct IBM's piece.** Write 7030 code to the
   IBM documentation that describes it: its internal structure, tables,
   formats and messages, cited by page. A reconstruction is labelled
   with the word RECONSTRUCTION in its header, and its sources and
   every guess are listed there. When an original turns up, it replaces
   the reconstruction, and the difference is recorded.
3. **Project tools are scaffolding only.** `strap/strap_asm.py`
   assembles the transcribed listings and the reconstructions until a
   STRAP II runs under MCP. It is never the environment's assembler.

| piece | plan | primary sources for a reconstruction |
|---|---|---|
| MCP | the original, transcribed | the March 1963 listing |
| PROSA, MCP's system library on disk | **reconstruct** what the listing does not hold | C22-6728-1 (formats), DISK FETCH pp.311-318, C22-6678-1 |
| MCP Loader / BSS processor | find; else reconstruct | C28-6379-0 |
| SMAC I, the macro processor | **reconstructed host-side** (`strap/smac.py`, `strap/smac_mcp.py`); **a 7030 version runs the whole language on the model and compiles its own generators** (`decks/smac7030_shell.strap`, `decks/smac_special_library.smac`, `docs/smac_7030.md`) | J28-6128 + errata; C22-6678-1 pp.14-28, 43-46 (`mcp_macros.md`) |
| STRAP II | find; else reconstruct as a 7030 program run under MCP | C22-6729 (internals), C28-6129 (language) |
| FORTRAN IV | find; else reconstruct last, and the largest | C22-6751; the AWRE S1/S2 trail in `thirdparty_software/` |
| the system tape | rebuilt from the pieces above, in the layout MCP's IPL reads | `mcp_tape_manufacture.md` |

**The whole-corpus audit and plan is `reconstruction_plan.md`.** It
lists every IBM piece, its sources, how completely it can be rebuilt,
and the order of work.

How deep each reconstruction can go depends on how much its IBM guide
gives (C22-6729's account of STRAP II's passes and tables, for
example). That is assessed in the ink, one piece at a time, before
any code is written.

## The road, in order

**E1. Let MCP finish its bypass-mode start.** After IPL, MCP's command
package asks DISK FETCH for a type area. Since the M-1 fix
(`boot_plan.md`, "M-1 ADDED ONE") the fetch runs to completion, and it
answers "TYPE NOT IN INDEX" (printed p.312 line 13). The PROSA on the
synthesized system tape (`strap/prosa.py`) is a fixture whose
dictionary and index hold only what the IPL rows pin. **The current
frontier is a faithful PROSA**: the type areas MCP's listing contains,
in the dictionary/index format DISK FETCH searches (C22-6728-1;
printed pp.311-318). Until then no transition command is issued, the
input program never starts, and no card is read.

What that means precisely (2026-11-07). The code is not what is missing:
the overlay type areas are already transcribed. Their PUNID statements
open 22LOADER on printed p.320, 22$DUMP on p.335, 22SCOMD on p.361 and
22$EOJ on p.381 (`decks/mcp_bootstrap_p*.strap`). What is missing:
- **The type areas 11A11DIC and 11B11IND.** C22-6728-1 printed p.96
  names them as the first two type areas of the master tape's second
  file, ahead of 11C11IPL and 11D11MCP. Their contents were made by
  IBM's system build, not assembled from the listing, so no listing of
  them exists. They are **reconstructed**: their format comes from
  C22-6728-1 and from the code that reads them, DISK FETCH (pp.311-318)
  and X SQ SCH (p.316).
- **The overlay type areas, placed in PROSA after 11D11MCP**, with
  index entries pointing at them.

**Done, 2026-11-07:** `strap/prosa_dict.py` builds both type areas
(RECONSTRUCTION, sources in its header), and PROSA now carries all eight
type areas the listing holds. MCP fetches 22SCOMD and enters J COMD.
The command package then echoed the IPL program's `COMD,CLOCK` and
looped typing `//////` (`boot_plan.md`, "THE COMMAND PACKAGE RUNS").

**E1 is done, 2026-11-08.** That loop was a model fault, and three more
stood behind it (`boot_plan.md`, "THE START RUNS TO THE READER"). MCP now
accepts CLOCK and BYPASS, types the time, READs the reader, types `SERVICE
THE CARD READER`, and JC4 polls SJ1FUL for a job card (printed p.391 line
31). `tests/run_mcp_start_test.sh`. That poll is the point where the machine
needs an operator and a deck, so the frontier is now E2 and E3.

Two limits on that. The model's empty reader answers with EE where a real
empty hopper is not ready, so `PRESENT JOB REJECTED - NO JOB CARD.` is the
fixture's. And DISK FETCH has only found 22SCOMD and 22$EOJ on this path;
22LOADER and 22$DUMP wait for a job.

**E2. Operator actions in the harness.** For example, the reader's
START key (unit ready + CS, RefMan printed p.141) and the console's
SIGNAL. This also needs `BEW,$` with a deliverable interruption to stop
counting as a halt, so the run continues into the handler. The shape
was proven in a scratch experiment (`boot_plan.md`, experiment 1).

**E3. A card deck from a host file.** The reader is a fixed 32-word
`Vector` today. A JOB deck needs a file-backed source, the same pattern
as the tape (`StretchTapeSourceFile.bsv`). The card format is 15 words
per card in no-ECC mode and 13 in ECC mode (printed p.140), and
`StretchCardTb` already pins the column-major packing.

**E4. A first job.** The JOB, TYPE and LIM cards, then a binary deck
for a program that prints a line (assembled by `strap_asm.py` as
scaffolding until STRAP II runs), through MCP's
loader (C28-6379), with output on the printer. Card formats come from
C22-6678-1 and C22-6728-1, cited by page.

**E5. Warm start.** Each MCP run now spends 6.7M steps in IPL. Saving
the disk and core after one IPL (disk plan step D2, extended to core)
would let job tests start from the idle loop.

**Order changed by the owner, 2026-11-07:** SMAC I and STRAP II first,
as best-effort reconstructions; then FORTRAN IV on top of both
(`reconstruction_plan.md` §7). The host-side work does not wait for
E1-E5. Running the processors under MCP does.

**E6. STRAP II under MCP**, found or reconstructed (see the table),
assembling a source deck into the binary E4 loads. Then E4's
scaffolding deck is replaced by STRAP II's own output.

**E7. FORTRAN IV**, the same way, after STRAP II.

**E8. On the ULX3S.** The same jobs, with the disk in SDRAM (disk plan
D3-D4) and the reader fed from the SD card.

## Verification

Each step follows AGENTS.md:
- a runnable test with a measured injection;
- the full suite green;
- every format and semantic cited to a page read in the ink.
