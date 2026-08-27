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

Ten documents were inventoried in depth (five general 7030 documents
plus the five I-Box diagnostic test programs, see #6 below); a sixth
data point beyond those (the directory listings themselves) is
recorded for completeness. All PDFs were pulled directly from
bitsavers.org.

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
5. **The five I-Box diagnostic test programs are, like the DCP, complete
   STRAP source listings** (787 pages combined) -- and every one of
   them turns out to depend on `SIC` as its own internal subroutine
   call/return mechanism, not just as a nominally-tested instruction.
   That single shared dependency blocks running any of the five
   end-to-end more than any individual instruction-class gap does. See
   #6 below for per-program findings and the specific slices (I-Box
   5's address-truncation routine, I-Box 4's Refill/CB sections, I-Box
   1's `WEN`/`WEN2`/`VEN`) that avoid it.

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
- **The STRETCH MAINTENANCE COMPOOL** (PDF pp. 129-130, corrected --
  originally cited as "p. 131" in this doc, but p. 131 is actually
  control section `J1A1` "Utility Control Routine"; verified by reading
  the actual page and cross-checked against p. 92 landing exactly on
  Memory Compare, confirming this PDF's page numbering has zero offset
  from the citations used throughout this doc, so 131 was simply
  wrong) -- a `SYN` table of shared symbolic-address definitions, 65
  entries (51 on p.129, 14 more continuing onto p.130 -- an earlier
  pass of this doc undercounted, having only checked p.129), header
  "STRETCH MAINTENANCE COMPOOL, NOVEMBER 20, 1961", terminating in
  blank lines partway down p. 130. This is the single highest-leverage
  page in the whole find: it's the Rosetta stone that resolves symbols
  referenced by *every other* 7030 diagnostic deck in bitsavers'
  `diag/` directory, not just this one. Transcribed and verified --
  see "Recommended next steps" item 1 below. Transcribe it first,
  regardless of what else gets transcribed -- without it, every other
  listing's symbols are dangling.
- **Memory Compare routine** (`G5`, pp. 92-93) and **Panel Dump
  routine** (`H7`, pp. 125-129, dumping LC, index/boundary/channel
  registers, both accumulator halves, indicator/mask/remainder/factor/
  transit registers -- close to a complete map of 7030 programmer-
  visible state) need no tape drive, card reader, or channel I/O to
  run -- but "self-contained" as originally written here overstated it:
  reading the actual routine bodies (not just this summary) shows `G5`
  branches to external `H`-prefixed routines outside its own control
  section (`B,H1A1A2` "print heading", `B,H5A4`, `B,H6B` "encode
  number of failures"), and both routines lean on DCP print-formatting
  macros (`%IQSZ`/`%IQS*`) with no counterpart in this simulated model.
  Actually assembling and running either one needs those dependencies
  resolved first, not just `SYN` -- see `bsv/README.md`/this project's
  memory file for the corrected, narrower scope. These remain the two
  best candidates for
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

**Update, third day**: reason (2) is now investigated, not untouched.
A throwaway BRAM probe (8192 words, `mkBRAM1Server`) elaborated in
0.275 seconds -- versus the plain-`Vector` attempt's 5+ minute,
1.5TB+-RAM hang at the same word count -- confirming the elaboration
blocker really is solvable and cheaply, not just theoretically.
That's the good news; it is not the same as the blocker being *fixed*.
Checking all ~26 `readWord`/`writeWord` call sites in
`StretchExecute.bsv`/`StretchVFL.bsv`/`StretchCore.bsv` found that all
but two pass a runtime-computed address, meaning BRAM's read latency
can't be confined to a few call sites -- nearly every VFL/FP/Transmit/
Connective/IoOp case arm in `execute()`, plus instruction fetch
itself, would need converting from a single combinational read into a
multi-cycle sequence. That's a rewrite of the core's control
structure, not an addition like the `pendingIdxWrite`/`ioPending` FSMs
were -- see `bsv/README.md` "Toolchain" item 8 and "Next steps" item 6
for the full scope breakdown. Still the concrete prerequisite for any
DCP-scale transcription, now with a real cost estimate instead of a
question mark.

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

## 6. The five I-Box diagnostic test programs (`diag/ja_ax1a_ibox-1.pdf` through `diag/jb_ax5b_ibox-5.pdf`)

787 PDF pages across the five documents (60/203/215/193/116), all
scanned STRAP-1 fanfold listings with no text layer, run in the SSIP
(Sense Switch Interrogation Program)-controlled sequence I-Box 1 -> 2
-> 3 -> 4 -> 5, each gating the next ("designed to run only after
[prior tests] have passed"). Surveyed in parallel by five agents, each
reading full front matter plus an evenly-spaced sample of the source
body (not full transcription -- see "Recommended next steps" above for
why this is an inventory pass, not a transcription pass). All five:
"Programs becoming obsolete: None."

**Notable finding, true across all five documents, not just one**:
**`SIC` (Store Instruction Counter If) is not merely one of several
tested instruction classes here -- in every one of these five programs
it IS the subroutine call/return and error-report idiom the deck's own
control flow depends on** (the universal pattern is `SIC,<label>`
immediately followed by `B,<label>`, assembling to opcode field `80`
throughout). `bsv/README.md` lists SIC as decoded-but-not-executed (a
no-op). That means **none of these five programs can be run end-to-end
against the model as a black box, independent of whatever instruction
class each one nominally targets** -- a more load-bearing blocker than
any single missing mnemonic. Three of the five (I-Box 3, 4, 5) have a
second, similarly structural blocker: **`SVA`** (also NOT executed,
per README) used as a self-modifying-code mechanism to patch operand/
address fields into scratch instruction templates before falling
through to execute them. Any actual run attempt on one of these five
needs SIC (and, for 3/4/5, SVA) working first, or a narrow slice
chosen specifically to avoid both -- the per-program notes below flag
which slices do.

### I-Box 1 (`ja_ax1a_ibox-1.pdf`, 60 pages)

Purpose (verbatim): tests "1) Unconditional Branch 2) Direct Index
Arithmetic except RNX, LVE, SVA 3) Immediate Index Arithmetic except
LVS 4) Index Branching 5) Store Instruction Counter if" -- the
program's own stated exclusion list (RNX/LVE/SVA/LVS) matches this
model's own scope gaps exactly. Routines include the `B`/`BD`/`NOP`
family, `LX/SX`, `LV/SV`, `LC/SC`, `LR/SR`, `V+`/`V+C`/`V+CR`,
`KV`/`KC`, all immediate forms (`LVI/LVNI/LCI/LRI/KVNI/KCI`), a
16-variant `CB`/`CBR` family, and Branch-on-Indicator both via LX
side-effects and (in three sub-tests) via a direct store to word 11
(Indicators) -- the latter is its own small extra gap, since
`bsv/README.md` documents that generic STORE to word 11 is a no-op
here. Also contains a large "Y-Z Control Sequences" section (pp.51-56)
that is untestable *by construction* on this model: it validates
instruction-fetch handoff between Y/Z pipeline registers, which don't
exist here, so it would trivially pass without exercising anything.
Beyond SIC and word-11-store: `BEW` "wait for Interval Timer signal"
hangs on real hardware but branches straight through here (matches
"NOT MODELED AT ALL: interrupts... interval timer"), and `ENSU`'s
memory-protection boundary-register setup is similarly unenforceable.
Cross-validation candidates: the CB/CBR family (largest, most
regression-test-shaped block) and `WEN`/`WEN2`/`VEN` (~9 instructions,
the smallest self-contained runnable fragment found in any of the five
documents). Whole program is based at word 1536 (octal 3000) --
like the DCP, exceeds `StretchStorage`'s current 256-word window, so
any candidate needs re-assembly at a low `SLC` address, not in-place
extraction.

### I-Box 2 (`jb_ax2a_ibox-2.pdf`, 203 pages)

Purpose (verbatim): "1) Store Zero in Index Internal and External
Memory. 2) Compare Value and Compare Count in Internal, External and
Index Memories. 3) Proper Index Selection." The most model-compatible
of the five: LX/SX/SR/SC/SV, KV/KC/KVI/KCI, Store Zero, Branch on
Indicator (including the clear-modifier form, confirmed to match
`StretchExecute.bsv`'s `bi.clear` field exactly), and VFL `L` are all
in the model's executed set, and the program's own "three memories"
language turns out not to be a gap at all -- external/index/internal
memory all resolve inside the model's single unified memory-mapped
register file (confirmed directly against the source: parallel
`Z,I16DMP` / `Z,$X1` / `Z,$R` triads for the same test against each of
the three). One unresolved indicator mnemonic, `BXF`, doesn't match
any name in `StretchTypes.bsv`'s indicator table -- worth a targeted
look if this program is ever transcribed. Beyond SIC (the call/return
blocker described above), every routine's ident line also carries the
`%IQSZ` print macro `archival_inventory.md` already flags as having no
model counterpart, and control flow leans on SSIP-resident externals
(`SSW ERS SERS RET SEN ...`) resolved outside this document -- not
self-contained, same shape as the DCP's Memory Compare/Panel Dump
caveat. Revision-drift note: writeup dated April 5 1961, but the
source listing header reads February 6 1961 -- the listing predates
its own writeup by two months, a new and larger instance of the
project's previously-noted writeup/deck drift pattern.

### I-Box 3 (`jb_ax3a_ibox-3.pdf`, 215 pages)

Purpose (verbatim): "test for the proper loading and storing of the
index registers." One continuous STRAP listing (not several named
control sections). Six routines, each an exhaustive bit-by-bit sweep
(all 64 bits, all 16 index registers) of one op against all three
memories: `XCS` (LX/SX/LV/SV/LC/SC/LR/SR, also builds a ~60-entry
`SIC`-based interrupt table), `1222` (`SVA` -- ~a quarter of the whole
document, plus adjacent-bit-corruption checks against FP- and
direct-index-format instruction words), `1224` (SC), `1226` (LV, plus
LVI at the very end), `1228` (LC), `1230` (LR, plus LRI bit-swept at
the end). The near-exhaustive per-bit/per-register sweep structure
makes `LX/SX/LV/SV/LC/SC/LR/SR` here about as close to a complete
oracle as this project is likely to find for that instruction group.
`SVA`'s dedicated section is the largest single concrete gap in any of
the five documents. Tentative, unconfirmed revision-prefix drift noted
(title page reads "JB AX3", one sampled source-page ID card looked
like "JA AX3A" -- low-contrast scan, worth a direct look before citing
as fact).

### I-Box 4 (`jb_ax4b_ibox-4.pdf`, 193 pages)

Purpose (verbatim): "test of the direct index arithmetic instructions
and the transmit and swap operations." Eleven numbered routines
(132/134/136/138/140/142/144/146/148/150/156); two mid-sequence ones
(136: C+I/C-I, 140: V+C/V+IC/V-IC) weren't directly sampled and are
positionally inferred. Concrete gaps: `RNX` (dedicated section 144),
`SVA` (section 148's *entire* index-modification test relies on SVA
to record what address each instruction computed -- another
structural, not just topical, SVA dependency), Transmit backward and
Swap (section 146's own stated test plan explicitly covers
forward/backward x direct/immediate x transmit/swap -- 2 of the 3
modifier axes are out of scope, only forward-direct-transmit is
covered by the model), and `LVE`/`LVS` (section 156, the whole final
and one of the largest sections). Strong cross-validation candidates:
section 138 (Refill/RCZ, self-contained, no external dependencies
observed -- best candidate found in this document, similar shape to
DCP's Memory Compare) and section 150 (the CB/CBH/CBZ/CBR family,
large and self-contained). Two routine slots (labels `152`/`154`) are
deliberate `NOP` placeholders with a "DUMMY PROGRAM" comment, not
missing content.

### I-Box 5 (`jb_ax5b_ibox-5.pdf`, 116 pages)

Purpose (verbatim): tests "the time clock, interval timer, mask and
indicator registers, interrupt system, boundary control, execute
instructions, Look-Ahead forwarding, and the proper truncation of
addresses for those instructions which use only part of their address
field." **The single largest concentration of unmodeled hardware
found in any document surveyed in this project**: one routine alone
(1260, mask/indicator/interrupt, ~68% of the whole document) exercises
interrupts, mask/indicator registers, and upper/lower boundary
registers simultaneously -- all four items on `bsv/README.md`'s "NOT
MODELED AT ALL" list, at once, in one place. `EX`/`EXIC` (routine
1262) and `SIC` (used as this program's own self-check mechanism, not
just incidentally) are also entirely out of scope, and `SVA` is again
the self-modifying-code mechanism the diagnostic relies on throughout
-- meaning even the parts of this program that test in-scope hardware
can't run without SIC+SVA support first. Two real bright spots:
routine 1268 (Look-Ahead store-to-fetch/store-to-load forwarding,
pp.110-112) is the cheapest routine in the whole document to reason
about (~3 pages, 6 sub-cases, no interrupt/timer entanglement) despite
testing an unmodeled feature; and routine 1274 (address-truncation
checks for `LX/SX/Refill/StoreZero/Transmit`, pp.112-116) is **the
single cleanest, most isolable cross-validation target found across
all five documents** -- five concrete, independently checkable
assertions ("-LX FAILS TO TRUNCATE BIT 19" etc.) against instructions
already in the model's executed set, no interrupt machinery involved.

## Recommended next steps, in order

1. ~~**Transcribe the STRETCH MAINTENANCE COMPOOL** (DCP manual, PDF
   pp. 129-130) -- the shared symbol table every other diagnostic deck
   depends on.~~ **DONE.** `strap/programs/dcp_maintenance_compool.strap`,
   verified against the manual's own printed address column
   (`strap/verify_dcp_maintenance_compool.py`, wired into
   `run_tests.sh`). 65 entries total (51 on p.129, 14 more --
   `ACA`..`AIDNTB` -- continuing onto p.130; the original "51 entries"
   count here only covered p.129). Getting a real oracle for this
   required resolving two format questions in the source scan, both
   now documented in the transcription's own header comment and in the
   project memory file: the ambiguous glyph between a base symbol and
   its bit-offset is STRAP-1's `+` operator (grammar argument, C22-6531
   pp.9-11 -- STRAP-1 has no other arithmetic operator); and the DCP
   listing's own compiled-address column prints word numbers and bit
   offsets in **octal**, while STRAP-1 *source* always writes them in
   **decimal** -- confirmed exactly against every transcribed row (46
   decimal offset prints as octal 56, etc.), which also gave every base
   symbol's true value directly from the table's own zero-offset rows
   with no need to hunt for an independent defining label elsewhere in
   the 130-page listing.
2. **Transcribe and run the Memory Compare (pp. 92-93) and Panel Dump
   (pp. 125-129) routines** from the DCP listing -- no tape/card/
   channel I/O needed, but (corrected from an earlier, overstated
   "self-contained" claim here -- see the "Notable finding" above)
   NOT dependency-free: both branch to external `H`-prefixed routines
   outside their own control sections and lean on DCP print-formatting
   macros (`%IQSZ`/`%IQS*`) this model has no counterpart for.
   Attempting either one means either transcribing the H-series
   routines too and deciding what those macros should mean on this
   simulated printer, or picking a narrower slice of one routine that
   avoids both. Real codesign-milestone shape once unblocked; not a
   quick win on its own.
3. ~~**Inventory the five I-Box test programs**
   (`ja_ax1a_ibox-1` through `jb_ax5b_ibox-5`, per the System Test
   Programs overview) next.~~ **DONE, see "6. The five I-Box diagnostic
   test programs" above.** All five downloaded and surveyed. Headline
   finding: `SIC` is every one of the five programs' own subroutine
   call/return mechanism, not just a tested subject -- a bigger,
   shared blocker to actually *running* any of them than any single
   missing instruction class. Best near-term transcription/cross-
   validation candidates identified: I-Box 5's routine 1274
   (address-truncation checks against LX/SX/Refill/StoreZero/
   Transmit, all in-scope, no interrupt machinery involved -- the
   cleanest target found across all five documents), I-Box 4's
   section 138 (Refill/RCZ, self-contained) and section 150 (the
   CB/CBR family), and I-Box 1's `WEN`/`WEN2`/`VEN` (smallest
   self-contained runnable fragment, ~9 instructions). Biggest
   concrete instruction-level gaps confirmed with real test coverage
   behind them: `SVA` (structural self-modifying-code dependency in
   I-Box 3/4/5, plus I-Box 3's dedicated ~50-page section), `RNX`
   (I-Box 4), `LVE`/`LVS` (I-Box 4's entire final section), Transmit
   backward/Swap (I-Box 4), and the whole interrupt/mask/indicator/
   timer/boundary system plus EX/EXIC (I-Box 5's routine 1260 alone,
   ~68% of that document).
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
- `diag/ja_ax1a_ibox-1.pdf` -- I-Box test 1 (unconditional branch,
  direct/immediate index arithmetic, index branching, SIC)
- `diag/jb_ax2a_ibox-2.pdf` -- I-Box test 2 (store zero, compare
  value/count, index selection)
- `diag/jb_ax3a_ibox-3.pdf` -- I-Box test 3 (index register load/store)
- `diag/jb_ax4b_ibox-4.pdf` -- I-Box test 4 (direct index arithmetic,
  transmit, swap)
- `diag/jb_ax5b_ibox-5.pdf` -- I-Box test 5 (clock/timer/mask/
  indicator/interrupt/boundary/EX/lookahead/address truncation)

Raw per-document agent reports (routine-by-routine tables, page-by-page
citations) are preserved in `archival_inventory_notes.md` in this same
directory for anyone doing the actual transcription work.
