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
   them turns out to depend on `SIC`, verified directly (not just
   trusted from an agent report -- see #6's "Verification") to be a
   single packed test-and-branch instruction whose embedded branch
   this model doesn't yet execute. That means virtually every test
   block's pass/continue/fail branch silently fails and falls through
   to whatever's next in memory instead -- a bigger, shared blocker to
   running any of the five end-to-end than any individual
   instruction-class gap. See #6 below for per-program findings and
   the specific slices (I-Box 5's address-truncation routine, I-Box
   4's Refill/CB sections, I-Box 1's `WEN`/`WEN2`/`VEN`) that avoid it.

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

**Update, later**: reason (2) is CLOSED. Storage is BRAM-backed
(`bsv/README.md` "Toolchain" item 8, `docs/phase2_arm_inventory.md`)
and `MemWords` is the full 18-bit space, so the DCP's octal
004000-016500 footprint fits with room to spare; the assembler also
has `SLC` now, so a listing can be placed at its own addresses rather
than re-based. First program run at real historical addresses:
`strap/programs/ibox1_wen_ven_original_addresses.strap`. Reason (1)
(CTL/LOC codes, chaining) still stands for the DCP as a whole.

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

**Notable finding, true across all five documents, not just one, and
independently verified directly against two of them (not taken on an
agent's word -- see "Verification" below)**: **`SIC` (Store
Instruction Counter If) is not a separate instruction from the `B`/
`CB`/branch-on-indicator line that follows it in the source -- `SIC`
and that following line are ONE 64-bit instruction.** `SIC`'s own
format (per `StretchDecode.bsv`'s cited manual page, "bits 32-63
specify the half-word branch instruction used") packs a conditional
IC-store into the left half-word and an embedded branch (unconditional
`B`, `CB`, or branch-on-indicator -- all three observed) into the
right half-word of the *same* word. So this is a test-and-branch
primitive, not a call/return convention (there's no evidence here of a
saved return address -- "call/return" was this pass's first-draft
mischaracterization, corrected below). `bsv/StretchExecute.bsv`
currently handles `tagged Sic` with nothing but
`ind = setOpInvalid(ind)` -- it performs neither the conditional store
nor the embedded branch. Since practically every test block in these
five decks ends in exactly this SIC-plus-embedded-branch pair as its
pass/continue/fail logic, the practical effect on this model is that
**every one of those branches silently fails to happen, and execution
just falls through into whatever word comes next in memory** -- a
concrete, confirmed break in program control flow, not merely "errors
go unreported." Three of the five (I-Box 3, 4, 5) have a second,
independently structural blocker: **`SVA`** (also NOT executed, per
README) used as a self-modifying-code mechanism to patch operand/
address fields into scratch instruction templates before falling
through to execute them. And I-Box 5's routine 1262 (`EX`/`EXIC`) is a
*different kind* of gap from either: `EX`/`EXIC` isn't even given its
own decode tag (falls through to the generic `Unimplemented` no-op),
so an EX'd subject instruction doesn't merely fail to branch
afterward -- it never executes at all. Any actual run attempt on one
of these five needs SIC (and, for 3/4/5, SVA; for 5's routine 1262,
`EX`/`EXIC`) working first, or a narrow slice chosen specifically to
avoid all of it -- the per-program notes below flag which slices do.

**Verification**: the "SIC is one packed instruction" claim above was
checked two ways, not trusted from subagent reports (which described
the pattern as "call/return"/"subroutine mechanism," a
plausible-sounding but unverified reading -- caught before being
trusted further, and advisor correctly pushed back on the listing
evidence alone the first time, since an address-column reading can't
by itself distinguish "one packed instruction" from "two half-word
instructions that happen to sit in the same word").

1. **Primary source, decisive**: `22-6530-2_7030RefMan.pdf` printed
   p.41, "Storage of Instruction Counter" / "Store Instruction Counter
   If (SIC)". Direct quotes: *"Any half-length branching operation...
   can be converted to a full-word instruction... This is done by
   prefixing any of the above instructions except BRANCH ON BIT with
   the operation STORE INSTRUCTION COUNTER IF... Bits 32-63 specify
   the half-word branch instruction used."* And: *"This instruction
   may always be prefixed to one of the half-word branching
   instructions. **It is executed if and only if the associated
   branching is successful.**"* This settles it outright: SIC is
   always one 64-bit instruction (a prefix fused with its branch, not
   two independent fetches), and the IC-store is conditioned on the
   embedded branch's own success -- not a separate condition. It also
   means the branch executes with its own ordinary semantics
   (unconditional, CB, or BI) as part of the same instruction, so a
   model that doesn't perform SIC's embedded branch takes none of
   these branches at all, regardless of what the embedded op would
   have decided on its own.
2. **Listing cross-check, including the case that could have falsified
   it**: `jb_ax2a_ibox-2.pdf` p.6 and `ja_ax1a_ibox-1.pdf` p.50 both
   show the `SIC` line and its embedded branch line landing inside the
   same 64-bit span in the resolved-address column -- e.g.
   `SIC,SENO+.32` -> `006501.00` immediately followed by `B,SSW` ->
   `006501.40`; `SIC,ISCBA` -> `005413.00` followed by
   `CB,SX1,ISCB2` -> `005413.40` (two different embedded-branch
   shapes, plain `B` and conditional `CB`, confirmed in the same
   pass). One instance (`ISCB2`) starts at bit 32 of word 005414
   rather than bit 0 -- initially flagged as a possible problem for
   reading (A) (a word-straddling SIC would falsify a bit-0-only
   theory) -- but its own embedded `CB` resolves cleanly to
   `005415.00`, the very next half-word, confirming SIC is a true
   64-bit span that can start at *either* half-word boundary, not
   something restricted to word-aligned starts. No case found that
   contradicts the primary source.

`bsv/StretchExecute.bsv`'s `tagged Sic` arm at the time did only
`ind = setOpInvalid(ind)` -- performed neither the store nor the
embedded branch, confirming the "control flow silently falls through"
finding stood on solid ground, not a guess.

**Update: SIC is now implemented** (Reference Manual pp.41-42 semantics,
`bsv/README.md` "Executed"), and the first diagnostic block has been
run VERBATIM with its own SIC-driven pass/fail chain intact -- I-Box
1's SIC-CB / SIC-CBZ groups (p.50, `strap/programs/ibox1_sic_cb_cbz.
strap`), the deck's own "HANG UP OR BECOME BD,<next>" self-modifying
mechanism included -- and then the whole of pp.50-51 from 5412.00 to
5461.40 as one span (`strap/programs/ibox1_p43_p51_span.strap`: SIC-CB,
SIC-CBZ, SIC-B,ZIND, SIC-B,IND, WEN2/WEN/VEN, five groups flowing into
each other), which also exposed that the model's direct index ops
never set the index indicators (fixed). Then extended back to 5247.00
(pp.46-49: the CBR/CBR+/CBR-/CBRH/CBRZ/CBRZ+/CBRZ-/CBRZH groups, twelve
groups in all), which settled the CB family's H/+/- units at 32/64
bits (the model had 1/2) -- `strap/README.md` "Gotchas" 18 -- and
then to 5123.00 (pp.43-46: CB/CB+/CBH/CB-/CBZ/CBZ+/CBZ-/CBZH, once the
assembler had CNOP): the deck's ENTIRE index-branching section, twenty
groups, runs verbatim. Every half-word of pp.43-51 (497) matches the
listing's printed code. The next group up, "LOAD + STORE REFILL IN
INTERNAL MEMORY" (p.43), stores into the indicator register
(SR,$X1,$IND+.32) -- the word-11-store gap noted above -- so that is
where the span stops. The shared blocker this section describes is
therefore lifted for every block whose only other needs are already
in scope; `SVA` (I-Box 3/4/5) and `EX`/`EXIC` (I-Box 5) remain.

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
like the DCP, exceeded `StretchStorage`'s then-256-word window, so
the first candidates were re-based at the assembler's default origin.
**No longer necessary**: `MemWords` now covers the whole address
space and `SLC` is implemented, and the WEN block below has since
been re-run at its listed addresses (octal 5454-5461) with its
assembled words matched bit-for-bit against the listing's own printed
machine code (`strap/verify_ibox1_listing.py`).

**`WEN`/`WEN2`/`VEN` (p.51) transcribed and run -- DONE**, as
`strap/programs/ibox1_wen_ven_indicators.strap`
(`StretchIboxWenTb`, wired into `run_tests.sh`). Loads a VFL
binary-unsigned all-ones word (`WEN2`/`VEN`) and an all-zeros word
(`WEN`), each followed by a Branch-on-Indicator checking `RGZ`/`RZ`
respectively -- genuinely behavioral (exercises `StretchALU.bsv`'s
`fieldToSM` forcing `sign=0` for unsigned mode together with
`StretchExecute.bsv`'s `setResultIndicatorsF`), unlike routine 1274
below. `WEN6`/`WEN7` (the source's own all-zero/all-one data words)
were independently located at p.59, not assumed. The original's own
pass/fail mechanism (`SIC`-embedded branches, deliberate infinite-loop
hangs) was deliberately NOT reproduced -- per the `SIC` finding above,
none of it would fire on this model anyway -- each check instead
writes a distinctive marker into its own index register on the pass
path (via `LVI`, an `ImmIndex` op that -- per
`StretchExecute.bsv`'s `ImmIndex` arm -- doesn't itself touch
`RGZ`/`RZ`, so marker writes never disturb a still-pending check),
checked externally by the testbench exactly like every other program
in `strap/programs/`.

Verified non-vacuous twice, the second time after advisor review
caught that the first version wasn't actually discriminating: checking
only "RGZ fires after ones" and "RZ fires after zeros" (3 assertions,
`X1`/`X2`/`X3`) cannot distinguish a correct implementation from one
that sets RGZ and RZ identically or swapped, since neither hypothetical
bug happens to touch the ONE indicator each assertion tests. Two more
assertions were added (`X4`/`X5`, not in the original source) checking
the OPPOSITE direction: that RZ does NOT fire after loading ones, and
RGZ does NOT fire after loading zeros. Confirmed this closes the gap
by temporarily patching `StretchExecute.bsv` itself to swap RGZ/RZ's
bit assignments in `setResultIndicatorsF`, rebuilding, and confirming
all 5 assertions fail under that exact bug (they do, and the original
3-assertion version would NOT have caught it -- worth remembering:
"branch fires when expected" and "branch doesn't fire when the
opposite is expected" are two different claims, and a swapped-output
bug can satisfy the first while failing the second only if both
directions are actually checked). Reverted the patch, confirmed
`StretchExecute.bsv` diffs clean against git, re-ran clean to confirm
all 5 assertions pass.

**Routine 1274 (`docs/archival_inventory.md`'s earlier "cleanest
target" pick) rejected, with reasons, not attempted**: before writing
any `.strap`, checked whether this model's address-truncation
behavior could actually fail, per the general principle "an
untestable-by-construction candidate wastes the same effort as a real
one, so check first" (this project's Y-Z Control Sequences finding
above is the same failure mode). `StretchTypes.bsv` types `WordAddr`/
`HWordAddr` as exactly `Bit#(18)`/`Bit#(19)`, and every one of
LX/SX/Refill/StoreZero/Transmit's address computations
(`StretchExecute.bsv`'s `effAddr18`/`effAddr19`/`effAddr24`, and the
explicit `ea[18:1]` half-word-to-word narrowing used by LX/SX/Refill)
stays within those exact widths by construction -- BSV's fixed-width
arithmetic makes representing an address wider than architecturally
valid impossible, not merely unlikely. A transcribed version of
routine 1274 would necessarily pass, exercising nothing -- exactly the
scenario advisor warned to check for before transcribing. `WEN`/
`WEN2`/`VEN` was picked instead for being both small and, unlike
1274, actually capable of failing.

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
register file (single-source finding, from one agent's reading of
parallel `Z,I16DMP` / `Z,$X1` / `Z,$R` triads for the same test
against each of the three -- plausible and cheap, worth a second look
before fully relying on it, unlike the SIC finding above which this
pass verified directly). One unresolved indicator mnemonic, `BXF`,
doesn't match any name in `StretchTypes.bsv`'s indicator table --
worth a targeted look if this program is ever transcribed. Beyond SIC
(the test-and-branch blocker described above), every routine's ident
line also carries the
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

**Section 138 (Refill/RCZ) rejected -- REJECTED, not transcribed.**
Read pp.58-60 (routines 1381-1387): every single check in the section
is built on `KV,$X15,$R` -- comparing X15's refilled value against a
system symbol `$R` that this project's assembler does not recognize
(`strap_asm.py`'s `eval_system_symbol` raises `unsupported system
symbol $'R'`; confirmed by direct call, not inference). `$R`'s meaning
isn't recoverable from the listing's usage alone (it's compared
against X15 after a bare `R,$X15` Refill from various octal locations,
but that's consistent with more than one plausible reading -- e.g. "the
refill field's own value" vs. some other refill-related quantity -- and
guessing from usage is exactly the "listing-address inference alone"
mistake this project corrected twice already for the SIC finding, see
I-Box 1's entry above). Supporting `$R` would mean inventing its
semantics from a scanned listing rather than transcribing a defined
instruction, unlike section 150 below where the gap is a missing
mnemonic table over an encoder (`enc_count_branch`) that already
accepts the full v/refill/branch-on-zero modifier space. No narrow
slice of section 138 avoids `$R`: it appears in every block sampled
(1381 through 1387). Rejected without writing any `.strap` code;
moving to section 150 instead.

**Section 150 (CB/CBR family), plain `CB` mnemonic transcribed and
run -- DONE.** Read pp.155-165 (routine 150, "----1250---CB AND CBR
TEST"). Before transcribing anything, checked whether the model
actually implements the fields the source's mnemonics would need:
`StretchDecode.bsv`'s `tryCountBranch` decodes `v`/`refill`/
`branchIfZero` from the raw instruction, and `StretchExecute.bsv`'s
`CountBranch` arm consults all three (`delta` from `cb.v`, `doRefill`
from `cb.refill`, and `take = (cb.branchIfZero==1) ? (newCount==0) :
(newCount!=0)`) -- so, unlike section 138's `$R`, this was a genuine
gap only in the *assembler's mnemonic table* (`strap_asm.py` only
ever encoded plain `CB`, v=00/refill=0/bz=0), not in the model or
decoder. Added the full 16-mnemonic table (`CB[R][Z][H|+|-]`) to
`opcodes.py` as `CB_CODES`, sourced from the pocket card's own "INDEX
BRANCHING" legend (pcard-3.png) and cross-checked against 8 of the 16
variants actually occurring in this section's listing (`CB`/`CB+`/
`CBH`/`CB-` on p.155-156, `CBR`/`CBR+` on p.159, `CBRZH`/`CBRZ-` on
p.165) -- not inferred from usage alone. Verified all 16 encode with
the intended bit pattern by direct extraction before writing any test.
Transcribed the plain `CB` block (routine 150's `IBR1`-`IBR9`, the
safest slice: v=00, no dependency on the model's own documented-
uncertain "add half"/"add one" unit mapping, `bsv/README.md`:146) as
`strap/programs/ibox4_cb_count_branch.strap`, all 5 assertions pass.
Deliberately did NOT reproduce the source's own pass/fail-signaling
mechanism (a self-modifying-code idiom: storing X1's packed IndexWord
over a NOP placeholder and depending on its VALUE field lining up with
a BranchOrMisc instruction's ADDRESS field) -- same substitution
principle as `WEN`/`WEN2`/`VEN`: keep the actual instructions under
test, replace the pass/fail plumbing with `LVI` markers the testbench
reads directly. Verified non-vacuous by flipping the branch-condition
sense in `StretchExecute.bsv`'s `CountBranch` arm, rebuilding, and
confirming all 4 branch-decision assertions then fail; reverted,
`git diff` on `StretchExecute.bsv` confirmed clean.

**`CBR` (routine 150's `IBR96`-`IBR99`, p.159) transcribed and run --
DONE.** Exercises a code path nothing else in the suite touches:
`CountBranch`'s own refill mechanism (`doRefill = (cb.refill == 1) &&
(x1.count == 0)`, `needsRead`/`prefetch` bail-out,
`unpackIndexWord(prefetch[0])`) -- distinct from `xw_refill.strap`'s
refill, which goes through `V+ICR`/progressive-indexing instead, a
different arm entirely. Transcribed as
`strap/programs/ibox4_cbr_refill.strap`: three `CBR` calls on one
index register (count 3->2->1->0), the first two branching without
refilling, the third not branching but refilling from a distinct XW
literal -- matching the source's own comments exactly ("COUNT 3 TO
2,BR,NO REFILL" / "COUNT 2 TO 1,BR,NO REFILL" / "COUNT 1 TO 0,NO BR,
REFILL"). Needed a mid-sequence snapshot (X1's state after call 2,
before call 3's refill) that the testbench -- which only reads final
register state after halt -- can't see directly; solved using this
project's own memory-mapped index-register convention
(`StretchTypes.bsv` `addrIndexBase=16`), confirmed real (not just an
assembler-side convenience) by reading `StretchStorage.bsv`'s
`readWord`/`writeWord`: addresses 16-31 alias directly into the same
`xreg` array `readIndex`/`writeIndex` use. `LX,$5,$X1` therefore
genuinely copies X1's current packed state into X5 at that exact
program point. All 5 assertions pass (2 branch-taken, 1 branch-not-
-taken, 1 mid-sequence "no premature refill" full-word compare, 1
post-refill "refilled from the right word, verbatim" full-word
compare). Verified non-vacuous with a refill-specific bug injection
(a branch-sense flip wouldn't exercise this code at all): dropped
`CountBranch`'s refill guard (`doRefill = (cb.refill == 1) &&
(x1.count == 0)` -> `doRefill = (cb.refill == 1)`), rebuilt, and
confirmed the actual failure was bigger than predicted going in --
not just the mid-sequence check but 3 of 5 assertions (`X4`/`X5`/`X6`)
fail, since refilling on every call also corrupts X1's own refill
field after the first call, cascading into the branch decision on
call 3 too. Reverted, `git diff` on `StretchExecute.bsv` confirmed
clean. See the file's own header for the full account, including the
correction of an initial (wrong) prediction of which assertions the
injected bug would flip -- caught before committing, not after.

Of the 16 total `CB[R][Z][H|+|-]` mnemonic variants: 2 (`CB`, `CBR`)
have been transcribed into a `.strap` program and actually run through
Bluesim, with a targeted, verified-non-vacuous bug injection each; a
further 6 (`CB+`/`CBH`/`CB-`, `CBR+`, `CBRZH`/`CBRZ-`) were confirmed
to occur in this section's own listing (used to validate the mnemonic
table's correctness, see above) but have not themselves been executed
as a test; the remaining 8 (`CBZ`/`CBZH`/`CBZ+`/`CBZ-`, `CBRH`,
`CBR-`, `CBRZ`, `CBRZ+`) are implemented, encode correctly (verified
by direct bit-extraction, not by listing occurrence), but have neither
been observed in this document's sampled pages nor executed -- a
smaller, well-scoped remaining gap, not a rejected candidate.

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
checks for `LX/SX/Refill/StoreZero/Transmit`, pp.112-116) looked like
**the single cleanest, most isolable cross-validation target found
across all five documents** on first read, but turned out to be
untestable by construction once checked against this model's actual
address types -- see I-Box 1's `WEN`/`WEN2`/`VEN` entry above for the
reasoning and for what got transcribed instead.

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
   finding (checked directly against two source pages, not taken on
   an agent's word -- see #6's "Verification"): `SIC` and its
   following branch line are actually ONE packed 64-bit
   test-and-branch instruction, whose embedded branch this model
   doesn't yet execute -- meaning virtually every test block's
   pass/continue/fail branch silently fails and falls through instead,
   a bigger shared blocker to actually *running* any of these five
   than any single missing instruction class. **Update**: I-Box 1's
   `WEN`/`WEN2`/`VEN` (smallest self-contained runnable fragment, ~9
   instructions) has since been transcribed and run --
   `strap/programs/ibox1_wen_ven_indicators.strap`, all 5 assertions
   pass (grown from 3 to 5 after advisor review found the original
   version couldn't discriminate a swapped-indicator bug), see I-Box
   1's own entry above. I-Box 5's routine 1274 (address-truncation
   checks) looked like the cleanest candidate on first read but turned
   out untestable by construction (this model's `WordAddr`/`HWordAddr`
   types make the checked failure mode structurally impossible) --
   rejected before transcribing, also detailed in I-Box 1's entry
   above. Of the two remaining candidates: I-Box 4's section 138
   (Refill/RCZ) was rejected -- every check depends on a `$R` system
   symbol this assembler doesn't recognize and can't safely infer the
   meaning of; section 150 (the CB/CBR family) was transcribed and run
   instead -- `strap/programs/ibox4_cb_count_branch.strap` (plain
   `CB`) and `strap/programs/ibox4_cbr_refill.strap` (`CBR`'s own
   refill mechanism), all 10 assertions across both pass, after adding
   the missing `CB[R][Z][H|+|-]` mnemonic table (`opcodes.py`'s
   `CB_CODES`) over an encoder/decoder that already implemented the
   full field space. See I-Box 4's own entry above for both.
   **Update**: both pages' printed machine-code columns have now been
   transcribed too and every assembled half-word matched against them
   (`strap/verify_ibox4_listing.py`, 137 checks) -- the CB/CB+/CBR/
   CBR+ encodings, LX/SX, and the XW index-word layout are thereby
   validated against IBM's assembler itself, not just the pocket card
   and the model's self-consistency. Same for I-Box 1's WEN block
   (`strap/verify_ibox1_listing.py`). See `strap/README.md` "Gotchas"
   item 15 for the print format; use it on any future transcription.
   Biggest concrete instruction-level gaps confirmed with real test
   coverage behind them: `SVA` (structural self-modifying-code
   dependency in I-Box 3/4/5, plus I-Box 3's dedicated ~50-page
   section), `RNX` (I-Box 4), `LVE`/`LVS` (I-Box 4's entire final
   section), Transmit backward/Swap (I-Box 4), the whole
   interrupt/mask/indicator/timer/boundary system (I-Box 5's routine
   1260 alone, ~68% of that document), and `EX`/`EXIC` (I-Box 5's
   routine 1262 -- a harder gap than SIC's, since EX'd subject
   instructions have no decode tag at all and so never execute, not
   just fail to branch afterward).
4. Locate the actual **MCP program listing** and **STRAP II Assembly
   Listing** (Form C28-6129 on bitsavers is the *wrong* document for
   the latter, as established above) -- both explicitly referenced as
   separate companion documents by their respective System Analysis
   Guides, neither found on bitsavers so far.
5. Longer-term: `ja_ua1_ssip` (foundational dependency nearly every
   other diagnostic test needs resident -- and note it carries a full
   STRAP listing at PDF pp.7-52, not prose alone, as its table row now
   records; SIP16/SIP17 are transcribed), `jb_af1c_floating-point` and
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

---

# Complete extant-software survey (bitsavers `ibm/7030/`, 2026-09-03)

A full inventory of every surviving piece of 7030 software (source
listings) and software documentation found on bitsavers, downloaded
into `docs/`, with cross-references to the implementation that models
or runs it. "Source" = an actual instruction-level listing; "Doc" =
prose/reference. Each transcribed program in `../strap/programs/` cites
its source PDF and page in its own header comment; this table is the
reverse index (source -> transcription/implementation).

## Diagnostics (`diag/`) -- STRAP source listings

| File | What | Kind | Modeled / transcribed |
|---|---|---|---|
| `7030_SystemTestPrograms_Aug61.pdf` | Index of all system test programs | Doc | the map used to pick I-Box targets |
| `ja_ax1a_ibox-1.pdf` (60pp) | I-Box 1 diagnostic | Source | RUN: `ibox1_wen_ven_indicators`, `ibox1_wen_ven_original_addresses`, `ibox1_sic_cb_cbz`, `ibox1_p43_p51_span` (20 groups, pp.43-51); bit-exact vs `verify_ibox1_listing.py` |
| `jb_ax2a_ibox-2.pdf` (203pp) | I-Box 2 diagnostic | Source | surveyed (archival pass); SVA/SIC blockers |
| `jb_ax3a_ibox-3.pdf` (~200pp) | I-Box 3 diagnostic | Source | surveyed; SVA (~50pp section), SIC |
| `jb_ax4b_ibox-4.pdf` (~200pp) | I-Box 4 diagnostic | Source | RUN: `ibox4_cb_count_branch`, `ibox4_cbr_refill`; bit-exact vs `verify_ibox4_listing.py` (pp.155/159); section 138 rejected ($R), the pp.58-62 KV/$R pages sourced the Appendix-A system symbols |
| `jb_ax5b_ibox-5.pdf` (~200pp) | I-Box 5 diagnostic | Source | surveyed; interrupt/timer/boundary/EX -- the largest unmodeled-hardware concentration |
| `jb_af1c_floating-point.pdf` (282pp) | **Floating-point (PAU) diagnostic**, SMFF-1C, JB AF1C, Apr 15 1961, SSIP-controlled | Source | IN PROGRESS -- its routine F200 (LOAD TEST) drove out and verified the assembler's FP sign-modifier loads (LN/LA/LNA), bit-exact vs its printed code (`../strap/verify_fp_signmods.py`), and exposed a real look-ahead store-close-to-fetch gap (see plan). Running a full block still needs branch-on-bit (`BB`/`BB1`/`BZB`, decoded not executed) and the SSIP framework; blocks using divide/double wait for stage 4e. |
| `ja_bb6b_worst_pat_test.pdf` (20pp) | Worst-pattern memory test | Source | NOT YET -- runnable against `StretchMemory.bsv` (the interleaved units); a memory-model codesign target |
| `ja_bm6a_unique_adr_test.pdf` (11pp) | Unique-address memory test | Source | NOT YET -- memory-model target |
| `ja_bp6a_memory_patterns_test.pdf` (6pp) | Memory-patterns test | Source | NOT YET -- smallest memory test, good first memory codesign target |
| `ja_ua1_ssip.pdf` (52pp; **pp.7-52 an unbroken STRAP listing**) | SSIP (System Test Program supervisor), JA UA1, "SSIP CBD 2-9-61" | Source | RUN (partial): `ssip_sip17_reset` (SIP16/SIP17, PDF pp.17-18, bit-exact vs `../strap/verify_ssip_sip17_listing.py`), which named the five instruction-exception indicators and settled that slot 14 is not one. CORRECTED 2026-09-19: this row previously described the file as framework prose only. It is not. pp.1-6 are the writeup and the Maintenance Tape Control Card; p.7 opens with the source line "PRINID, SSIP CBD 2-9-61 JA UA1" and p.52 closes with `END,%8@100.` at 002732.71. The listing is 1-up fanfold with NO printed page numbers, so it is cited by PDF page, unlike every other tape here. It also explains the SIC/BEW pass-fail idiom the transcriptions reproduce externally. |
| `ja_uc1a_maintenance_tape.pdf` | Maintenance-tape builder | Source | needs full tape/channel I/O |
| `ka_ua1_diagnostic_ctl_pgm.pdf` (154pp) | Diagnostic Control Program (DCP), control section F1, pp.19-152 an unbroken STRAP listing | Source | RUN (partial): `dcp_maintenance_compool` (SYN symbol table pp.129-130, verified vs the printed address column); Memory Compare/Panel Dump need CTL/LOC + H-routines + print macros |
| `ka_ex1_bx-0.pdf`, `ka_ex1b_bx-0.pdf` | BX-0 (exchange/box) test | Source | needs the exchange as a real bus requester |
| `ka_ul1_load_and_tape_write_util.pdf` | Loader / tape-write utility | Source | needs tape I/O |

## Master Control Program (`mcp/`) -- the operating system

| File | What | Kind |
|---|---|---|
| `MCP_Mar63_001-249.pdf` + `MCP_Mar63_250-445.pdf` (451pp) | **IBM 7030 Master Control Program source listing**, "new version 03-15-63" -- the OS source the System Analysis Guide's companion reference pointed to, now LOCATED (previously flagged missing above) | Source |
| `C22-6728_/-1_7030_MCP_Sys_Analysis_Guide.pdf` | MCP System Analysis Guide (calling sequences, flowcharts) | Doc |
| `C22-6678-1_7030_MCP_Reference_Jun64.pdf` | MCP Reference Manual | Doc |
| `J22-6559_MCP_UsersGuide_Dec60.pdf` | MCP User's Guide | Doc |
| `C28-6379-0_MCP_Loader.pdf`, `N22-0085_MCP_RefMan_Upd_May63.pdf` | MCP loader / reference update | Doc |

The MCP is a full operating system; running any of it needs the
interrupt system, the exchange, tapes and the console -- a long-horizon
target, but the source now exists in `docs/` for study and eventual
transcription.

## Customer-engineering (`ce/`) and engineering reports -- documentation

| File | What |
|---|---|
| `R23-9732_Manual04_7101_CPU_Jan63.pdf` (297pp) | 7101 CPU CE manual: section-3 flow/block/timing charts (figs 3.1.x I-unit sequencers, 3.2.x look-ahead, 3.3.x PAU, 3.8.x FP timing) -- the gate-level reference for the microarchitecture stages |
| `R23-9713_7101_Maint_Console_1961.pdf` | Maintenance console CE manual -- the console controls (start/stop, display/store, single step, repeat) |
| `R23-9694/9695_CE_Intro_Pgmg_Vol2/3` | CE introductory programming |
| `R23-9702_7503_Card_Rdr_7614_Rdr_Ctl_CE` | Card reader/control CE manual |
| `Planning_A_Computer_System.pdf` (Buchholz 1962) | The design book: ch.14 CPU, ch.15 look-ahead -- primary source for the microarchitecture (`microarchitecture_plan.md`) |
| `TR00.722_Stretch_I-Unit_Design_Mar60.pdf` (Blosk) | The I-unit design report -- registers, data paths, timing diagrams |
| `TR00.03000.703_StretchVM_59.pdf` (Cocke & Kolsky) | Look-ahead ("virtual memory") simulation study -- the level/counter/interlock logic |
| `Bloch_EngrDesOfStretch_1959.pdf`, `ADescriptionOfStretch_Dec59.pdf` | Engineering-design overviews |
| `7030_Performance_Characteristics_Vol1/2_Mar61.pdf` | Timing tables + measured benchmark listings -- the stage-5 timing oracles |
| `22-6530-2_7030RefMan.pdf`, `C22-6531_/6578`, `C28-6129_STRAP-II`, `X22-6533_PocketCard` | The ISA/assembler references cited throughout `../bsv/` and `../strap/` |

## Building on top of this -- the codesign queue (in priority order)

1. **The floating-point diagnostic** (`jb_af1c`): transcribe a block
   exercising `+ * L ST K E+ SHF` and run it against `StretchFP.bsv`.
   First real historical FP source validating the stage-4c arithmetic.
2. **The memory tests** (`ja_bp6a` smallest first): run against the
   interleaved `StretchMemory.bsv` -- the first source to exercise the
   real memory model rather than a single BRAM.
3. **The DCP Memory Compare / Panel Dump** (once CTL/LOC and the
   H-routines are in): the largest self-contained DCP slices.
4. **MCP fragments** (once interrupts + exchange exist): the OS source.

Cross-reference discipline (per this survey): every `../strap/programs/
*.strap` transcription names its source file and page range in its
header; `../bsv/*.bsv` cite the Reference Manual / pocket card page for
each encoding and semantic; `microarchitecture_plan.md` Appendix A
cites the primary source for every specification fact. This table is
the reverse index from surviving source -> implementation.

## Holdings now complete: the full bitsavers `ibm/7030/` collection

As of 2026-09-03 all 52 PDFs under bitsavers' `pdf/ibm/7030/` (top level
+ `diag/`, `ce/`, `mcp/`) are downloaded into `docs/`; a diff confirmed
nothing is missing, and there is no `bits/IBM/7030/` software-image
directory (404) -- consistent with the standing finding that no
machine-readable system tape survives. Documentation added in the final
pass, beyond the source listings and design reports surveyed above:

| File | What | Relevance |
|---|---|---|
| `7030_Opcode_List.pdf` (99pp) | Assembled-word opcode listing | Decoder verification -- the cross-check `bsv/README.md` "Next steps" item 1 called for (rendered pages, OCR is noisy on digits) |
| `C22-6729_7030_STRAP_II_Sys_Analysis_Guide.pdf` (211pp) | STRAP II internals (calling sequences, flowcharts, one worked source example) | Enough to reconstruct STRAP II's logic; the assembler's own listing is still separate/unlocated |
| `C22-6751_7030_FORTRAN_IV_May63.pdf` (37pp) | IBM 7030 FORTRAN IV | The FORTRAN IV documentation (compiler source not surfaced) |
| `TR00.719_Stretch_Multiprogramming_May60.pdf` (14pp) | Stretch multiprogramming design | The interrupt/supervisor design behind MCP -- for the interrupt-system stage |
| `R23-9713_7101_Maint_Console_1961.pdf` (49pp) | Maintenance console CE manual | The console controls (start/stop, display/store, single step, repeat) -- an open feature |
| `R23-9702_7503_Card_Rdr_7614_Rdr_Ctl_CE_1961.pdf` (86pp) | Card reader / control CE | External-unit detail for the exchange |
| `C28-6379-0_MCP_Loader.pdf` (24pp), `N22-0085_...Upd` (12pp), `X28-6131_MCP_PocketCard.pdf` (2pp), `C22-6728_...Guide.pdf` (270pp, base rev) | MCP loader / reference update / pocket card / base System Analysis Guide | MCP operation reference |
| `D22-6513_7030_genInfo_1960.pdf` (26pp) | General information | Overview |
| `A22-6552_/-1_physPlan.pdf` | Physical planning | Installation (the six-memory-unit configuration) |
| `1956_fallJCC.pdf`, `1959_fallJCC.pdf`, `LASL_Jun61Article.pdf`, `ADescriptionOfStretch`, `Bloch_EngrDesOfStretch` | Conference papers / LASL / overviews | Historical design context |
| `X22-6533_7030_PocketCard.pdf` (4pp) | Reference card (PDF; `pcard-*.png` are the working images) | The special-storage/indicator/mnemonic tables (see plan Appendix A.9-A.10) |

Beyond bitsavers, no other archive is known to hold 7030 software or
documentation not represented here.


## Third-party Stretch software (non-IBM): documentation trail

The languages/systems built for Stretch installations outside IBM --
LASL's IVY (and COLASL), AWRE's S1/S2 FORTRAN, and MITRE's Stretch LISP
1.5 / MATHLAB -- are documented in `thirdparty_software/README.md`
(citations, access status, and the one freely-downloadable item). Unlike
IBM's 7030 software, no source code for any of them is known to survive,
and the primary papers are paywalled (ACM) or bot-protected (FAS/OSTI).
Provenance summary: IVY/COLASL in Lazarus, LA-6943-H (LASL, 1978); AWRE
S1/S2 in Ron Bell's BCS Fortran-jubilee article (Glennie's Stretch
FORTRAN); MATHLAB in Engelman's 1965 FJCC paper (the LISP-based MITRE
system).
