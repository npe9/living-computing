# Archival inventory: what's recoverable from bitsavers' 7030 collection

Follow-up to a broader archival survey (not done in this repo) that
catalogued which historical Stretch software survives *in some form* --
manuals, System Analysis Guides, language references -- versus what's
lost outright. This document is the next step that survey called for:
a file-by-file inventory of bitsavers' `ibm/7030/diag/`, `ibm/7030/ce/`,
and `ibm/7030/mcp/` directories (plus two top-level documents), asking
specifically: does this PDF contain *actual instruction-level source
code*, or only architectural/procedural description of code that isn't
here? That distinction is the difference between a transcription target
and a design reference.

No machine-readable Stretch artifact (tape image, card-deck dump, disk
image) has been found anywhere in this pass or the one before it. That
remains the single biggest preservation gap. Everything below is a scan
of a printed document -- reconstructable, in every real sense, only by
hand transcription or OCR against a genuine assembler (this repo's).

Five documents were inventoried in depth; a sixth data point (the
directory listings themselves) is recorded for completeness. All PDFs
were pulled directly from bitsavers.org.

**Download gotcha**: bitsavers 403s a bare `curl -sL <url>` (blocks the
default curl User-Agent). Use `curl -sL -A "Mozilla/5.0" -e
"http://bitsavers.org/" <url>`.

## Bottom line, ranked by what's actually transcribable today

1. **The Diagnostic Control Program (DCP) manual is not a manual --
   pages 19-152 of `diag/ka_ua1_diagnostic_ctl_pgm.pdf` are a complete,
   continuous STRAP source listing** of the 7030's diagnostic test
   harness, ~130 printed pages, one unbroken control section (`F1`,
   octal 004000-016500). This is the largest block of real, reconstructable
   Stretch source code found in either archival pass. It is *not*
   immediately runnable on this project's model, though -- see caveats
   below -- so it's a transcription target, not a next milestone.
2. **The STRAP II and MCP System Analysis Guides are excellent
   specifications, not source listings.** Both explicitly say so of
   themselves (the MCP guide's preface states outright that it
   "complement[s] the MCP program listing" -- a separate document not
   found on bitsavers). They document internal logic in enough detail
   (calling sequences, register conventions, complete bit-layouts,
   box-by-box flowcharts referencing real internal symbols) to
   *reimplement* STRAP II's and MCP's control-flow logic from scratch,
   but contain almost no verbatim STRAP mnemonics for the routines
   themselves.
3. **The MCP Loader manual is a complete external wire-format spec**
   (18 binary-card classes, 5 internal table layouts, the full
   diagnostic-message catalog) with zero source for the loader's own
   internals -- enough to write a compatible reimplementation of deck
   parsing, not to recover IBM's code.
4. **The System Test Programs overview is a pure index** (which test
   exercises what, in what order) with zero source of its own -- but it
   correctly predicts, from internal evidence, that the DCP manual (#1)
   supersedes an "obsolete" loader program it names -- independent
   corroboration of finding #1 before that finding was even read.

## 1. Diagnostic Control Program (`diag/ka_ua1_diagnostic_ctl_pgm.pdf`)

154 PDF pages. Bundles two documents: pp. 1-18 are a short operator's
procedures manual (prose); **pp. 19-152 are a complete STRAP assembly
listing**, control section `F1`
(`PRINID KA UA1 DIAGNOSTIC CONTROL PROGRAM FOR 7030/7950 EDP SYSTEM BY
J.C. HANNIGAN`), terminated `END,F1`. Scanned fanfold printout, no OCR
text layer, but legible: STRAP mnemonics, octal source-address column,
and machine-code-encoding column throughout.

**Continuity independently verified** (not just sampled) across the
three page ranges an initial pass skipped -- the octal address column
runs unbroken through all of them, with no missing folios or scan
gaps. This is a completeness claim earned by checking, not assumed from
partial sampling.

The DCP is the master harness: it IPLs, reads a schedule of test-program
IDs, loads and checksums each named diagnostic test off a "master tape,"
sequences their execution, formats console/printer output, and -- via
its Utility section (control sections `J1`/`J2`) -- builds and maintains
that master tape from individual test decks. That last piece is exactly
the "how are individual tests loaded and sequenced" mechanism, present
in full, not just described.

**High-value sub-ranges, worth transcribing before anything else**:
- **The STRETCH MAINTENANCE COMPOOL** (p. 131) -- a `SYN` table of
  shared symbolic-address definitions. This is the single highest-
  leverage page in the whole find: it's the Rosetta stone that resolves
  symbols referenced by *every other* 7030 diagnostic deck in
  bitsavers' `diag/` directory, not just this one. Transcribe it first,
  regardless of what else gets transcribed -- without it, every other
  listing's symbols are dangling.
- **Memory Compare routine** (`G5`, pp. 92-93) and **Panel Dump
  routine** (`H7`, pp. 125-129, dumping LC, index/boundary/channel
  registers, both accumulator halves, indicator/mask/remainder/factor/
  transit registers -- close to a complete map of 7030 programmer-
  visible state) are self-contained: no tape drive, card reader, or
  channel I/O needed to run them. These are the two candidates for
  actually assembling and running something from this find on the
  Bluespec model today, matching this project's established pattern of
  only claiming what's been run and checked.

**Why this wasn't (yet) a "run the DCP" milestone**: the DCP as a whole
assumes tape drives, a card reader, a printer, a typewriter console, and
the `%SEOP` (suppress end of operation) channel-command primitives
throughout. Transcribing all ~130 pages without being able to run the
result would produce a large, unverifiable artifact -- exactly the
failure mode this project's "verify every claim by running it" ethos
exists to avoid.

**Update, same day**: a simulated Input-Output subsystem now exists
(`bsv/StretchIO.bsv`) -- `RD`/`W`/`CCW`/`REL` against two fixed devices
(a card reader, a printer), verified end to end
(`strap/programs/io_reader_printer.strap`). This does NOT yet unblock
DCP-scale transcription, though, for two separate reasons: (1) the DCP
needs `CTL`/`LOC` (tape rewind/backspace/selection codes) and chaining/
multiple-block operation, none of which this first I/O milestone
implements; (2) more fundamentally, the DCP's own memory footprint
(octal 004000-016500, ~5400 words) far exceeds what `StretchStorage`
can currently hold -- raising `MemWords` from 256 high enough to fit it
was tried and sent `bsc`'s elaborator to 1.5TB+ RAM with no sign of
finishing (see `bsv/README.md` "Toolchain" item 8); that needs a
BRAM-backed storage rewrite first, a separate, larger undertaking. This
is still a large, tractable transcription target for later, with a much
more concrete list of prerequisites than before, not a near-term
milestone.

**Update, second day**: a tape drive now exists too
(`strap/programs/io_tape.strap`, `bsv/StretchIO.bsv` channel 34), with
real position persistence across instructions and two of `CTL`'s tape
function codes -- REWIND and BACKSPACE BLOCK (octal 136/176,
Reference Manual p.132), read from the External Units chapter this
same session. This closes part of reason (1) above but not all of it:
the DCP's `%SEOP` usage is now representable (`RD`/`W`/`REL`/`CTL`
SEOP forms all decode and, except `RD SEOP`/`CTL SEOP` specifically,
are exercised), and rewind/backspace are real, but SPACE FILE, WRITE
TAPE MARK, BACKSPACE FILE, and chaining/multiple-block operation are
still not implemented -- likely needed by a program that manages
actual tape files rather than single blocks, which the DCP's master
tape almost certainly does. Reason (2), the `MemWords`/BRAM storage
blocker, is completely untouched by this update and remains the larger
prerequisite.

## 2. STRAP II System Analysis Guide (`C22-6729`, top-level)

211 pages, ~65% sampled directly (front matter, both main-pass flow
charts, the complete Common-Section subroutine set, a representative
cross-section of Pass 1/Pass 2 subroutines, all of Serviceability Aids,
Relocation Pseudo-Ops, and Appendices A-H); the rest is index-table-
enumerated but not individually read.

IBM's internal documentation of STRAP II's own implementation logic --
NOT a user's guide to the STRAP language (that's a separate document,
see #5 below). Documents ~50 routines across two assembly passes, each
with a full calling sequence, register conventions, restrictions, and a
box-by-box flowchart detailed enough to read as structured pseudocode.
Appendices give complete bit-level formats for every internal data
structure (expanded instruction unit, symbol/tail/indicator tables,
coded-expression encoding, all relocatable binary card formats) and a
full 148-entry error-message catalog. pp. 111-113 derive the division
algorithm (Newton-Raphson reciprocal expansion) used by STRAP II's own
DD-statement precision arithmetic -- genuine algorithmic depth.

**Verdict**: sufficient to reconstruct STRAP II's logic and data
structures as a *specification*, not to transcribe as literal source.
The preface names a separate "STRAP II Assembly Listing" (Form
C28-6129) as where the actual STRAP-mnemonic source lives.

**C28-6129 checked and resolved**: bitsavers' `C28-6129_STRAP-
II_with_update_Apr63.pdf` is the **STRAP-II language Reference
Manual** -- input format, pseudo-ops, DD statement rules, address
arithmetic -- for programmers *writing* STRAP-II code, not a listing of
STRAP-II's own implementation. Confirmed by reading its own front
matter and table of contents. The actual "STRAP II Assembly Listing"
the System Analysis Guide's preface refers to is **not on bitsavers**
under this or any form number found so far. Worth a dedicated search
elsewhere, but don't expect to find it by re-fetching C28-6129.

## 3. MCP System Analysis Guide (`mcp/C22-6728-1`)

280 pages, ~110 sampled (front matter, full Interrupt Control section,
Job Control, IPL/Restart, System I/O intro, Actuator I/O, Commentator/
Debugging Aids, Appendix A I/O tables).

Its own preface states it "complement[s] the MCP program listing" -- an
explicit admission this is a companion document, not the listing.
Nonetheless it's excellent for reconstructing MCP's *architecture and
control-flow logic*: the complete interrupt-dispatch mechanism (SIT/
SIPT structure, PTOE format, the maskable-interrupt routine, the
receptor's interrupt-stacking state machine, a 36-entry error-code
table), the job-control state machine (JC1/JC4, three I-O assignment
tables fully bit-mapped), and I/O control table layouts at the bit
level (Channel/Unit Status/Area Tables). Dozens of named entry points
per subsystem are catalogued with page citations (see the raw notes for
the full list -- it's large enough to be a ready-made index for a
future transcription pass).

What's missing: full STRAP instruction bodies for almost every routine
-- flowcharts describe behavior in English-labeled boxes, not STRAP
mnemonics. The exceptions are calling-sequence/linkage snippets (a
handful of pages), not routine bodies. Recommendation from this pass:
locate the actual "MCP program listing" the preface refers to -- it's a
distinct document, not yet found on bitsavers.

## 4. MCP Loader manual (`mcp/C28-6379-0`)

24 PDF pages, read in full. Actual title is "Loader and BSS Processor"
-- about half the document covers the FORTRAN Binary/Symbolic
Subroutine processor, not the MCP loader itself. Complete external
wire-format spec: 18 binary-card class formats, 5 internal table
layouts, the full diagnostic-message set. Zero source for the loader's
own internals -- behavior given only as prose, per-card-class.

Bonus: pp. 15-16 contain small, genuine STRAP source examples (system
symbols `$MCP`/`$RESLD`/`$ABEOJ`/`$ABSUB`, pseudo-ops `SYN`/`SLC`/`SEM`/
`ENTER`/`XW`) -- compact enough to use as a hand-checkable syntax test
for this project's own assembler.

## 5. System Test Programs overview (`diag/7030_SystemTestPrograms_Aug61.pdf`)

46 pages, read in full. "STRETCH SYSTEM CERTIFICATION" -- an
acceptance-test index and run sequence, not a library index: 22
programs in recommended run order, each with equipment tested and a
one-line functional description, plus maintenance-switch semantics and
a Stretch memory map (control/dispatch at 64-192, tape loader at
(8)100-(8)777, all test programs run above (8)1000). Zero source-level
content -- confirmed as intentional scope (the doc itself says listings
live in the separate per-program PDFs it indexes).

**Notable finding**: this document independently flags its own listed
loader/dispatcher programs (`JA UC1`/`JA UD1`, "Maintenance Tape" and
"Tape Load") as *"Programs becoming obsolete,"* and from that plus a
`KA`-vs-`JA`/`JB` naming-prefix pattern, predicts that
`ka_ua1_diagnostic_ctl_pgm` is their successor -- **matching, from
entirely independent evidence, finding #1's discovery that that exact
file contains the DCP's complete source listing.** Two agents converged
on the same conclusion from different documents without seeing each
other's work -- a useful cross-check, not just a coincidence to note.

Also flags a systematic one-revision-letter drift between this Aug-1961
index and the individual diag/ PDFs (e.g. list `JB AF1C` / writeup
`JB AF1B` / bitsavers filename `jb_af1c`) -- expect every individual
diag PDF to be one revision ahead of what this index describes.

## Recommended next steps, in order

1. **Transcribe the STRETCH MAINTENANCE COMPOOL** (DCP manual, p. 131)
   -- the shared symbol table every other diagnostic deck depends on.
   Small, self-contained, unlocks everything else.
2. **Transcribe and run the Memory Compare (pp. 92-93) and Panel Dump
   (pp. 125-129) routines** from the DCP listing -- self-contained, no
   I/O environment needed, genuinely runnable and verifiable on the
   existing Bluespec model today. This would be the next real codesign
   milestone from this find, in the same shape as every prior one:
   assemble real historical source, run it, check the result.
3. **Inventory the five I-Box test programs**
   (`ja_ax1a_ibox-1` through `jb_ax5b_ibox-5`, per the System Test
   Programs overview) next. Per that overview, they enumerate specific
   instruction classes exercised -- unconditional branch, direct/
   immediate index arithmetic, index branching, SIC, store-zero,
   compare, index load/store, transmit/swap, clock/timer/mask-
   indicator/interrupt/boundary/execute -- a checklist that maps
   directly onto this model's implemented-vs-not scope, and (per the
   overview's own description) each writeup PDF likely contains its
   own listing. Same shape as the worked examples that have driven
   every prior gap-find in this project.
4. Locate the actual **MCP program listing** and **STRAP II Assembly
   Listing** (Form C28-6129 on bitsavers is the *wrong* document for
   the latter, as established above) -- both explicitly referenced as
   separate companion documents by their respective System Analysis
   Guides, neither found on bitsavers so far.
5. Longer-term: `ja_ua1_ssip` (foundational dependency nearly every
   other diagnostic test needs resident), `jb_af1c_floating-point` and
   the VFL circuitry test (`JB AV1C`, exercises Stretch's signature
   FP/VFL extensions), and the `ce/` Customer Engineering manuals
   (not yet inventoried in this pass).

## Sources

All from `bitsavers.org/pdf/ibm/7030/`:
- `diag/ka_ua1_diagnostic_ctl_pgm.pdf` -- Diagnostic Control Program
  (manual + complete source listing)
- `C22-6729_7030_STRAP_II_Sys_Analysis_Guide.pdf` -- STRAP II internals
- `mcp/C22-6728-1_7030_MCP_Sys_Analysis_Guide.pdf` -- MCP internals
- `mcp/C28-6379-0_MCP_Loader.pdf` -- Loader and BSS Processor
- `diag/7030_SystemTestPrograms_Aug61.pdf` -- acceptance test index
- `C28-6129_STRAP-II_with_update_Apr63.pdf` -- STRAP-II language
  reference manual (checked, confirmed NOT the assembly listing)

Raw per-document agent reports (routine-by-routine tables, page-by-page
citations) are preserved in `archival_inventory_notes.md` in this same
directory for anyone doing the actual transcription work.
