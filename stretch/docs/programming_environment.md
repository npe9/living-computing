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

So "the full programming environment" is, in order:

1. **MCP accepting and running jobs**: the operator readies the card
   reader, MCP's input program reads a JOB deck, and the loader loads
   the binary cards and runs the program, with output on the printer.
2. **Binary decks made by this project's own assembler**
   (`strap/strap_asm.py`, which reproduces IBM's assembled words
   bit-exact on every transcribed page) until a STRAP II listing is
   found. Then STRAP II itself can run under MCP as a processor.
3. **FORTRAN** only if a compiler listing turns up. The CHM requests
   in `archival_inventory.md` are where to look.

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
from `strap_asm.py` for a program that prints a line, through MCP's
loader (C28-6379), with output on the printer. Card formats come from
C22-6678-1 and C22-6728-1, cited by page.

**E5. Warm start.** Each MCP run now spends 6.7M steps in IPL. Saving
the disk and core after one IPL (disk plan step D2, extended to core)
would let job tests start from the idle loop.

**E6. On the ULX3S.** The same jobs, with the disk in SDRAM (disk plan
D3-D4) and the reader fed from the SD card.

## Verification

Each step follows AGENTS.md:
- a runnable test with a measured injection;
- the full suite green;
- every format and semantic cited to a page read in the ink.
