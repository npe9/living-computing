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
| STRAP II | find; else reconstruct as a 7030 program run under MCP | C22-6729 (internals), C28-6129 (language) |
| FORTRAN IV | find; else reconstruct last, and the largest | C22-6751; the AWRE S1/S2 trail in `thirdparty_software/` |
| the system tape | rebuilt from the pieces above, in the layout MCP's IPL reads | `mcp_tape_manufacture.md` |

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
