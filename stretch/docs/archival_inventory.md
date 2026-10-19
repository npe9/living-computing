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
(`decks/io_reader_printer.strap`). This does NOT yet unblock
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
(`decks/io_tape.strap`, `bsv/StretchIO.bsv` channel 34), with
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
`decks/ibox1_wen_ven_original_addresses.strap`. Reason (1)
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
*different kind* of gap from either: an EX'd subject instruction did
not merely fail to branch afterward -- it never executed at all.
**Half of that is closed as of 2026-09-25: `EX` executes** (the model
fetches the subject, runs it, actuates EXE on a successful subject
branch and steps the instruction counter past the EXECUTE only); see
`bsv/README.md`'s "Executed" entry and `docs/NEXT.md` item 4a. `EXIC`
does not, and still reaches Operation Code Invalid. Any actual run
attempt on one of these five needs SIC (and, for 3/4/5, SVA; for 5's
routine 1262, `EXIC` as well as `EX`) working first, or a narrow slice
chosen specifically to avoid all of it -- the per-program notes below
flag which slices do.

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
1's SIC-CB / SIC-CBZ groups (p.50, `decks/ibox1_sic_cb_cbz.
strap`), the deck's own "HANG UP OR BECOME BD,<next>" self-modifying
mechanism included -- and then the whole of pp.50-51 from 5412.00 to
5461.40 as one span (`decks/ibox1_p43_p51_span.strap`: SIC-CB,
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
in scope; `SVA` (I-Box 3/4/5) and `EXIC` (I-Box 5) remain. `EX` was on
that list until 2026-09-25 and is not any more.

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
machine code (`tests/verify_ibox1_listing.py`).

**`WEN`/`WEN2`/`VEN` (p.51) transcribed and run -- DONE**, as
`decks/ibox1_wen_ven_indicators.strap`
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
in `decks/`.

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

**CORRECTED 2026-09-24: the reasoning above is right about five of
routine 1274's seven subjects and WRONG about a sixth, and the routine
has now been transcribed whole** --
`decks/ax5b_1274_truncation.strap`, 99 rows,
024412.00-024500.00, PDF pp.112-114, bit-exact and wired into the
suite. (It also runs three pages earlier and ends two pages earlier
than this file's page span implied.)

The rejection reasoned that fixed-width BSV arithmetic makes an
over-wide address unrepresentable. True for the five UN-INDEXED
subjects, which reach bit 18 from `SVA` rather than from index
arithmetic. **Not true of 024455.00**, `TI,1,I74K1,I74K2($X1)` printing
`24471.00 80 024472.02 A1`. Its A2 is a 19-bit HALF-WORD address with
I2 = X1 = 32 bits, and the model's Transmit arm sends A2 through
`effAddr19`. **Its failure mode is not an over-wide address but wrong
SCALING inside a perfectly legal 19-bit one**: under the straight-add
this project carried before 2026, the 32 would be 32 half-words rather
than 32 bits, landing on word 024512 instead of 024472, leaving
`I74K2` zero and tripping the deck's own check. Reasoned from the page
plus a reading of the arm; NOT confirmed in simulation, and the
transcription says so.

**The general principle survives intact and is worth restating,
because it was applied correctly and still reached a wrong answer.**
"Check whether the candidate can actually fail before transcribing it"
is right. What went wrong is the SCOPE of the check: the question was
asked about address WIDTH, which is what the routine's title names,
and the one row that discriminates fails on scaling instead. A routine
named "TRUNCATION OF ADDRESSES" turned out to contain a check that is
not about truncation. **When ruling a block out, rule out each of its
rows, not its title.**

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
positionally inferred.

**1242 IS NO LONGER INFERRED, and it is a dedicated routine this list
did not record.** Read first-hand 2026-09-24, PDF p.80, the routine's
own banner in the listing:

```
----1242--- V+CR, V+ICR, V-ICR.
        -THIS TEST IS COMPOSED OF ROUTINES WHICH
        -CHECK THE ABOVE INSTRUCTIONS. ALL MEMORIES
        -WHICH ARE APPLICABLE IN ANY GIVEN TEST
        -ARE UTILIZED.
```

So the count-and-refill index family has a routine of its own, which
matters because that is exactly where the open `refillLegal` question
had to be answered — and 1242's header carries NO refill-address
clause, unlike 1238's "NOPING IF RF IS FROM 1 TO 15" and 1244's
"NO OPPED WHEN... IN THE RANGE OF 1 TO 37 OCTAL". See `docs/NEXT.md`
item 6.

**A CITATION CORRECTION, AND THEN A CORRECTION TO THE CORRECTION --
the second one is the instructive half.** This came to me as "the
routine index at PDF p.2". I rendered p.2, found PURPOSE / PROGRAM
INTRODUCTION / OPERATING PROCEDURE, and wrote here that there is no
routine index there. **That was wrong, and re-rendered first-hand at
200 dpi it is plainly wrong.** PDF p.2 is a **2-UP SCAN**: two printed
pages side by side on one PDF page. Its LEFT half is printed p.1 --
the PURPOSE / INTRODUCTION / OPERATING PROCEDURE I saw, including
loading step "4) Disable Interrupt and Time Clock". Its RIGHT half is
printed p.2, **section 4, PROGRAM PHILOSOPHY**, and that section does
exactly what the original citation said: "Below are listed all of the
routines that are part of this program, and a brief description of
what each tests", followed by all eleven --

    1232  Checks KVNI.
    1234  Checks V + from three memories (Internal, External, and
          Index Memories), V+I, V-I, and the index adder for all eight
          possibilities for each bit position.
    1236  Checks C+I and C-I.
    1238  Checks R and RCZ from all three memories where legal.
    1240  Checks V+C, V+IC, and V-IC.  All three memories are used
          where applicable.
    1242  Checks V+CR, V+ICR, and V-ICR, using all three memories
          where applicable.
    1244  Checks RNX.
    1246  Checks Transmit and Swap using all nine memory combinations
          and testing all modifier bits.
    1248  Checks index modification for all classes of instructions.
    1250  Checks CB, CB+ CB-, and CBR.
    1256  Checks LVE and LVS.

**THE TRAP HAS A NAME: in a 2-up scan, "what is on PDF page N" has TWO
answers, and finding one of them looks exactly like finding the
answer.** I did not look at the right half. The failure was not
sloppiness about the page number -- I rendered the correct page -- it
was stopping once the page had told me something. Cheap tell: a 2-up
scan shows TWO printed page numbers, and printed p.1 and p.2 were both
visible in the render I was reading from.

What survives of the original correction: this deck also carries
routine descriptions as BANNER LINES inside the listing (1246's is at
PDF p.99), so both are true and the banners are the richer source.
p.3 is a writeup-addendum cover and p.4 opens the listing, as stated. Concrete gaps: `RNX` (dedicated section 144),
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
`decks/ibox4_cb_count_branch.strap`, all 5 assertions pass.
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
`decks/ibox4_cbr_refill.strap`: three `CBR` calls on one
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

**THE ROUTINE INDEX, transcribed from the write-up at PDF p.2 (printed
p.2) on 2026-09-21 -- read first-hand, verbatim.** Five routines, and
knowing which is which turns "somewhere in 116 pages" into a page hunt
with a target:

| routine | what the write-up says it checks |
|---|---|
| **1260** | "the mask register, the Interrupt Address register, **the ability to interrupt**, the Indicator register, **unique interruption for bits 0-47**, I-Box indicators, **Upper and Lower Bounds registers and address monitoring** and 'NOP-ing' of illegal instructions" |
| **1268** | "**DF and IF** close to data store for all three memories. (Internal, External, and Index Memories)" |
| **1262** | "EX and EXIC" |
| **1274** | "that those instructions which can have a 19 bit address but use only 18 do in fact truncate the nineteenth bit" |
| **1258** | "the Interval Timer and Time Clock" |

**ROUTINE 1260'S LAYOUT, pp.41-45 read first-hand 2026-09-22.**
`docs/NEXT.md` had carried "SSIP's `I60S1`/`I60SX1` save/restore
harness, reported at `ax5b` pp.41-44" as 1260's prerequisite. Those
pages hold nothing of the kind. What they actually contain, in order:

| pages | what is there |
|---|---|
| pp.41-44 | **the per-indicator turn-on blocks**, I6071 through I6086 -- one per I-Box indicator (`TS`, `CPUS`, `EKJ`, `UNRJ`, `CBJ`, `EPGK`, `UK`, `EE`, `EOP`, `CS`, `RESRVD`, `OP`, `AD`, `USA`, `EXE`, `DS`). Sixteen blocks, but not sixteen tests -- see the triage below. |
| p.45 | **the indicator-walk driver**, I6087/I6088 -- **transcribed** as `decks/ax5b_16087_walk.strap`, six rows bit-exact via `tests/verify_ax5b_16087_listing.py`: `SIC,I60SX1` / `B,I60S1`, `TI,1,BIT0%$X1,$IND` *"SET ONE OF 20-47"*, `TI,1,BIT0%$X1,$MASK` *"SET MASK BIT OF TEST IND BIT"*, `BE,$+.32` *"ENABLE AND AWAIT INTERRUPT"*, then `BD,I60B13%$X6` -- an indexed dispatch into the per-indicator error table `I60B13`, whose entries read *"FAILED TO INTERRUPT ON IND MK / IN 1 MILLISEC."*, then IK, IJ, EK, TS, CPUS, EKJ, UNRJ, CBJ, EPGK, UK, EE, EOP, CS. |

**ROUTINE 1258 AND 1260 TESTs 1-4 -- pp.4-44 mapped 2026-09-24.**
Only TWO banners exist in that whole span: *"----1258---CHK TIME CLOCK
AND INTERVAL TIMER."* (p.5) and *"----1260---CHECK MASK, INDICATOR, AND
INTERRUPT."* (p.8). Entry labels and headers:

| label | octal | PDF p. | header |
|---|---|---|---|
| `I581` | 014012.00 | 6 | *"-TEST 1, CHECK TIME CLOCK STEPPING."* |
| `I587` | 014034.00 | 7 | *"-TEST 2"* (the interval timer) |
| `1601` | 014070.00 | 9 | TEST 1A |
| `1607` | 014167.00 | 12 | TEST 1B |
| `16011` | 014253.40 | 14 | TEST 1C |
| `16041` | 014556.00 | 22 | *"-TEST 2, CHK DATA IN IA."* |
| `16033` | 014626.00 | 24 | *"-TEST 3, CHECK THE ABILITY TO / -INTERRUPT."* |
| `16044` | 014710.00 | 26 | *"-TEST 4, CHK IND REG BITS 20-63, / -CHK 20-24."* |
| `16061` | 015236.00 | 37 | *"-TEST 5, CHK INT, BIT BY BIT."* |

**TEST 5's HEAD is at `16061`/`16064`/`16065`/`16066`, pp.37-44**,
which closes a loose end the pp.45-64 map below had to flag. `16066`
(015360.00, p.40) is a 20-entry dispatch *"-TURN ON MK."* … *"-TURN ON
DS."* feeding the per-indicator turn-on blocks `I6071` (016007.00,
*"-TS"*) through `I6086` (021365.00, *"-DS"*) already recorded here at
pp.41-44. **So pp.37-60 is TEST 5 end to end**, and pp.45-60 is its
tail.

An oddity worth keeping, because it looks like a chain member and is
not. p.9 at 014075.00-014077.40 holds an ADDITIONAL `IC260` update:
`LX,$X13,IC260` / `V+,$X13,BIT0` / `V+,$X13,BIT1` / `V+,$X13,BIT2` /
`SX,$X13,IC260` / `BD,16041`. It is the **abort path** for *"-BIT 24 OF
MASK REG STUCK ON 1, UNABLE / -TO TEST ANY FURTHER BITS."* — credit
TESTs 1A/1B/1C at once and jump to TEST 2. It independently confirms
BIT0/1/2 = TEST 1A/1B/1C, `IC260` = 022737.00, and the `024522 + n`
BIT-table rule a third time.

**ROUTINE 1260'S pp.45-64 -- mapped 2026-09-24, and the earlier note
was right about the TEXT and wrong about the KIND.** This span had
been characterised as "three kinds of test". It is not. **pp.46-59 are
three 48-ENTRY ERROR-MESSAGE TABLES**, each entry three half-words
(`SIC,SEN` / `BD,SERS` / `BD,<resume>`), 48 entries = 144 half-words =
110 octal words per table. The only code in the span is at its seams:

| block | octal | PDF pp. | what it is |
|---|---|---|---|
| `I6087`/`I6088` | 021376.40–021402.00 | 45 | the walk driver, header *"-TURN ON BIT 20-47."*: `SIC,I60SX1` / `B,I60S1` / `TI,1,BIT0($X1),$IND` *"-SET ONE OF 20-47"* / `TI,1,BIT0($X1),$MASK` / `BE,$+.32` *"-ENABLE AND AWAIT INTERRUPT"* / `BD,I60B13($X6)` |
| `I60B13` | 021402.40–021512.00 | 45–48 | table: *"-FAILED TO INTERRUPT ON IND &lt;name&gt; / -IN 1 MILLISEC."* |
| `I6090` | 021512.40–021513.40 | 48 | **the three-way dispatch -- the only interesting code in pp.46-60**: `BD,I60B14($X6)` *"-HI,BEFORE,INTRPTS ENTER HERE."* / `BD,I6093` *"-OK, AT INTRPTS ENTER HERE."* / `BD,I60B15($X6)` *"-LO,AFTER,INTRPTS ENTER HERE."* |
| `I60B14` | 021514.00–021623.40 | 48–51 | table: *"-INTERRUPT TAKEN ON IND &lt;name&gt; / -RECVD HIGHER PRIORITY."* |
| `I60B15` | 021624.00–021733.40 | 51–54 | table: same, *"-RECVD LOWER PRIORITY."* |
| `I6093`/`C`/`D`/`A`/`B` | 021734.00–021743.40 | 55 | the post-interrupt scan, including a **self-modified branch-on-indicator word** `I6093A XW,0,0,0 -BIND` planted by `SVA` |
| `16094` | 021744.00–022053.40 | 55–59 | table: *"-AFTR INTRPT, OR IND NOT ON, IND &lt;name&gt; / -FOUND ON."* |
| `16095` | 022054.00–022061.40 | 59–60 | loop advance; TEST 5 ends, continuity BIT6 at 022061.00 |
| `I6096`–`I6098`… | 022062.00–022214.40 | 61–64 | **TEST 6 -- real code**, header *"-TEST 6 CHKS THAT FREE INSTRUCTION / -IS IN FACT FREE, AND THAT I-BOX / -INDS SET ONLY CORRECT INDS."*; continuity BIT7 at 022214.00 |

Two caveats kept with the table. (i) pp.49, 50, 56, 57, 58 were
established **by arithmetic** from both read endpoints -- 48 x 3
half-words spans exactly those pages -- not read page by page. (ii)
**pp.45-60 is TEST 5's TAIL, not TEST 5**: `16095`'s `CB+,$X1,16063`
branches to a loop head earlier than p.45, and `I6087`'s own comment
says "BIT 20-47" while the p.8 write-up says TEST 5 covers bits 0-47.

**AND THE TWO PRIORITY MECHANISMS MUST BE KEPT APART, which is the
reason this table earns its place.** *Interruption selection*
(Reference Manual printed p.48: of several actuated, unmasked
indicators, the leftmost wins) decides which interrupt ENTRY is taken
-- and that is what pp.48-54 test. *Actuation priority* (printed p.51:
one cause that could set two indicator BITS turns on only the
higher-priority one) is a different thing entirely, and **nothing in
this span touches it.** The tell is in the driver: `TI,1,BIT0($X1),$IND`
transmits exactly ONE bit, so with one indicator on, "RECVD HIGHER
PRIORITY" can only mean the interrupt landed at a table slot BEFORE
the expected one. These are per-bit tests of the interrupt vectoring,
and they cannot bear on actuation arbitration at all. An earlier note
calling pp.49-54 "the priority tests" invited exactly that conflation.

A free cross-check fell out of reading the four tables' indicator
names in order: MK IK IJ EK TS CPUS EKJ UNRJ CBJ EPGK UK EE EOP CS
**RESRVD** OP AD USA EXE DS DF IF LC PF ZD IR LS PSH XPFP XPO XPH XPL
XPU ZM RU TF UF VF XF BTR DTR PG0…PG6 -- 48 names, matching
`bsv/StretchTypes.bsv` exactly (`ind_MK`=0 … 41-47 PG0-PG6). One
difference: the deck NAMES indicator 14 `RESRVD`; `StretchTypes.bsv`
leaves 14 unnamed.

**ROUTINE 1260'S BOUNDARY TESTS -- located 2026-09-23**, correcting a
guess `NEXT.md` had carried since the scouting pass. It claimed
pp.66-79 held "the positive boundary-interrupt cases". Scanning
pp.46-86 for BOUND/MONITOR and reading the hits:

| page | sub-test |
|---|---|
| p.65 | *"TEST 7 CHKS BOUNDARY CONTROL."* / *"CHK UPPER BOUNDARY DATA."* -- driver at I6099/I60100, per-bit error table `I60B17` |
| p.67 | tail of the upper-boundary error table (BIT10–BIT17) |
| p.68 | *"CHK LOWER BOUNDARY DATA."* (driver I60102/I60103) and *"CHK BOUNDARY CONTROL BIT."* |
| pp.69–70 | the lower-boundary error table, bits 32–49 |
| p.71 | *"FETCH FROM X-1 TO CHK UB COMP."*, *"FROM X-3 TO CHK LB COMP."* |

pp.65-70 are **register data-path tests** -- can each field hold each
of its bits. p.71 is the **comparison** test, i.e. the address
monitoring actually firing, which is what "positive boundary-interrupt
cases" meant. The guess was wrong in range (65-71, not 66-79) and in
kind (mostly data, not interrupts).

**p.68's two sub-tests, read first-hand.** The lower-boundary driver
is I60102/I60103 at 022264.40-022274.00 and mirrors the upper one
exactly: eighteen iterations, `SV,$X3,$LB` into word 3 bits 32-49,
four NOPs, read back, `KV`, and on mismatch `B,I60B18($X2)` into a
per-bit table whose entries pp.69-70 print as *"LOWER BOUNDARY DATA
FAILURE, BIT 32"* upward. Then the control-bit test at
022274.40-022306.40 sets word 3 bit 57 from `BIT57` and checks it
reads back (*"UNABLE TO SET BNDRY CNTRL TO 1."*), then clears it with
`Z,$UB` and checks again (*"...TO 0."*).

**A third confirmation of the BIT table's rule**: this page's
`LX,$X1,BIT57` prints `24613.02 10`, and 024522 + 57 = 024613. The
rule read off p.114 holds at bit 57 as well as at 0, 17 and 18.

**p.65 is transcribed and runs**
(`decks/ax5b_16099_ub_data.strap`): eighteen iterations,
because the upper boundary is word 3 bits 0-17. It catches a dropped
boundary bit and **names it** -- injecting
`boundaryReg <= (v & ~(64'b1 << 46))` halts at 022263.00, the table's
"UPPER BOUNDARY DATA FAILURE, BIT 17" entry.

**ROUTINE 1262 -- "TEST EX AND EXIC", read first-hand 2026-09-23.**
It begins at PDF p.87 and runs to ~p.110. Its purpose block, read at
600 dpi and transcribed verbatim:

```
----1262----TEST EX AND EXIC.
-THIS TEST IS COMPOSED OF THREE BASIC
-TESTS WHICH CHECK THE ABOVE TWO
-INSTRUCTIONS AS FOLLOWS.
    -TEST 1 CHECKS THE EXECUTION OF
        -ALL CLASSES OF INSTRUCTIONS
        -AND THAT ILLEGAL EXECUTES WILL
        -SET THE CORRECT INDICATORS.
    -TEST 2 CHECKS THE OPERATION OF
        -THE EXIC INSTRUCTION.  ILLEGAL
        -COMBINATIONS ARE USED TO CHECK
        -THAT THE CORRECT INDICATORS
        -ARE SET.
    -TEST 3 CHECKS THE ILLEGAL COMBINATIONS
        -OF EX AND EXIC.
```

**WHAT THE EXIC BLOCKS PIN DOWN**, read first-hand from PDF p.101,
which is the clearest page. Each block repeats one shape per
instruction class:

```
LVI,$X1,<err>   SVA,$X1,I62ITE     point the interrupt table entry
LVI,$X1,I62SUB  SVA,$X1,I62PSI     set the PSEUDO-IC to the subject
LX,$X1,I62EXF   SX,$X1,I62SUB      plant the subject instruction
Z,$IND  Z,$MASK  Z,$L  Z,$R        clear indicators, mask, accumulator
LV,$X2,I62PSI                      remember the pseudo-IC
EXIC,I62PSI                        <- the instruction under test
BD,<next>
<err>  SIC,SEN / B,SERS   "-INT WHEN EXIC TO / -A FLT PT INSTRUCT."
<next> LX,$X1,$L
       SIC,SEN / BXVZ,SERS "-SUBJ INST WAS FLT PT / -AND WAS NOT EXECUTED."
       V+I,$X2,0.32  KV,$X2,I62PSI
       SIC,SEN / BZXE,SERS "-PSEUDO IC NOT STEPPED .32 CORRECTLY
                            / -WHEN SUBJ INST WAS IMMED IX."
```

Three separate rules per class, each with its own error message:
1. `EXIC` to that class must **not** interrupt;
2. the subject instruction must actually **execute** (checked by its
   effect -- here `$L`, the accumulator's left half);
3. the **pseudo-IC must be stepped** by the subject instruction's
   length -- `.32`, one half-word -- which the block verifies by adding
   `0.32` to the saved value and comparing (`V+I` then `KV`).

Classes seen on p.101 alone: MISC, FLT PT, FULL WD VFL, IMMED IX.
Sighted by OCR on neighbouring pages and NOT yet read first-hand, so
treat as pointers rather than quotations: p.92 "TEST 1CA, ENABLE
AFTER EX", "TEST 1CB, CHK ADR MONITOR", "TEST 1CC, CHK EX OF BRANCH
AND EXE"; p.98 "EXIC RELINQUISHES CONTROL TO INSTRUCT", "PSEUDO IC
UNCHANGED BY EXIC"; p.99 "TEST 2B, CHK EXIC OF NON BRANCH".

**This is the oracle `NEXT.md` section 5 wanted for `EX`/`EXIC`,** and
reading it first is what item 2 asks for -- let the oracle shape the
implementation rather than retrofitting one. It pairs with Reference
Manual p.45's definition of indicator 18: "*Execute Exception (EXE).
An instruction was executed under control of the EXECUTE or the
EXECUTE INDIRECT AND COUNT operations that attempted to change the
contents of the instruction counter. The subject operation was
suppressed.*"

**Unblocking value**: `EX` is what 1268 cases 1B/1C need (`EX,$X3`,
`EX,$R`) and what 1260 blocks 16084/16085 need. **`EX` is implemented
as of 2026-09-25**, so 1268 1B/1C are unblocked on that count; 16084
still wants `LVE` and 16085 is an `EX` block whose surrounding 1260
machinery is the remaining question. The behavioural coverage lives in
`decks/ex_subject.strap`, `ex_exe.strap` and
`ex_monitor.strap`; 1262 TEST 1B and TEST 1CC remain ENCODING
transcriptions, because running them needs SSIP and the 64-word
interrupt table, not because `EX` is missing.

**ROUTINE 1268 TEST 1 -- transcribable, and what the pen marks mean.**
Test 2 is transcribed (see below). Test 1, the store-to-INSTRUCTION-
-fetch half at PDF p.110, is not, and the reason is worth recording
because the page carries HANDWRITTEN annotations on exactly the rows
that matter. At 600 dpi they are a reader's explanation, not a
correction:

* `I682 XW,0,0,0` prints `0.00 00 000000.00 00`, and its second
  half-word is boxed in pen with "LVI" written in the comment column.
  That is a note that the slot is OVERWRITTEN at run time -- the block
  does `SX,$X1,I682` twice, first with `I68K1`'s word (`Z,$X2` + NOP)
  and then with `I68K2`'s (`LVI,$X2,(8)777777.40` + NOP) -- so what
  executes there is not what the listing prints.
* `LX,$X2,$X2` at 024343.00 is circled. It reads X2 from its own word,
  which changes nothing but SETS THE INDEX RESULT INDICATORS from X2's
  value (Ref. Manual p.23), which is how the following `BXVZ,SERS`
  observes whether the LVI or the stale `Z` ran.

So the printed machine code is the assembler's own output and is
trustworthy; the marks explain the self-modification. **Case 1A is
transcribed and runs** --
`decks/ax5b_1681_if_close_to_ds.strap`, ten rows bit-exact
via `tests/verify_ax5b_1681_listing.py`, with `I68K1`/`I68K2`
transcribed from p.111 at their printed addresses rather than
manufactured. Cases 1B and 1C use `EX,$X3` and `EX,$R`; they were
blocked on `EX` until 2026-09-25 and are not any more (`NEXT.md`
item 4a).

**What running it buys, and what it provably cannot.** `LX`/`SX` move
a whole 64-bit word, so the block plants an arbitrary INSTRUCTION
through `packIndexWord`/`unpackIndexWord` and then executes it --
which makes it a witness for that round trip. Zeroing `count` in
`packIndexWord` halts it at SERS, the deck's own error path, because
IBM bit 31 is part of the planted `LVI`'s J field. But the existing
`index-spare-bits-zeroed` mutant (IBM bits 26-27) **cannot** be caught
here: the planted words are `0x0004920000001800` and
`0xffffe50100001800`, and both already have sign, flag and spare zero.
Computed from the assembled words, not guessed -- and it means that
mutant keeps its 23-minute near-miss catch in the I-Box 3 SVA
section.

**The sixteen blocks triaged** (read from pp.41-44, not inferred):

* **16072-16081** (`CPUS`, `EKJ`, `UNRJ`, `CBJ`, `EPGK`, `UK`, `EE`,
  `EOP`, `CS`, `RESRVD`) are three lines each -- `B,I6093` to the next
  test, a `CNOP` commented *"CANT TURN ON"*, and `DR%BU,64,8,64`.
  Error-report placeholders for indicators a program cannot provoke on
  its own. Ten of the sixteen, and nothing to transcribe in any of
  them.
* **16084** (`USA`) turns on its indicator with `LVE`; **16085**
  (`EXE`) with `EX`. Both instructions are deferred in `NEXT.md` §5,
  so both blocks are blocked on an implementation, not on a harness.
* **I6071** (`TS`) is **transcribed** -- 016007.00-016012.40,
  `decks/ax5b_16071_ts.strap`, eight rows checked by
  `tests/verify_ax5b_16071_listing.py`. It is an INTERVAL TIMER test:
  Reference Manual p.44, "4. Time Signal (TS). The interval timer has
  become zero." The block loads the timer with the value one, spins
  512 times on a `CB` to itself, and asks `BTS` whether TS came on.
  That makes it a second deck oracle for the timer, eight rows against
  routine 1258's whole routine, and it is in place BEFORE the timer is
  implemented. **SINCE SUPERSEDED (2026-10-16): the timer and the time
  clock now step** — one 1,024-per-second oscillator dividing the
  0.3 µs model clock by the exact rational 78125/24
  (`bsv/StretchTiming.bsv`), the countdown, the reload, the unused
  bits 19-27 and TS on the 1→0 edge in `bsv/StretchStorage.bsv`'s
  `oscillatorStep`, checked by
  `decks/interval_timer_steps.strap`, which makes every
  assertion 1258 TEST 2 and this block make (the ones that do not need
  the SIC/SERS error harness). What still blocks RUNNING I6071 and
  1258 themselves is unchanged: both fall through into the SIC/SERS
  reporting harness and the `%IQSZ` print macros, none of which is
  transcribed. It also gives `BTS` (indicator 4) and an `LCI` count
  field -- the field `strap/README.md`'s Gotchas item 16 records as
  having once been encoded wrongly. The pocket card's footnote (a) on
  the interval-timer row (`microarchitecture_plan.md` A.10) explains
  the instruction choice: that register is "read-only except for
  store-value/count/refill/address", so `SV` is one of the few
  operations that can write it at all. And the block must be running
  **disabled** -- word 1 is permanently protected (Ref. Manual p.31)
  and p.45 suppresses such a store "while the interruption system was
  enabled" -- which is not shown in its eight rows but follows from
  those two pages. Note the symmetry with I6086, which uses the SAME
  instruction on the SAME word as its DS provocation, enabled,
  expecting suppression.
* **I6082** (`OP`) and **I6083** (`AD`) are **transcribed** --
  contiguous at 017225.00-017234.40,
  `decks/ax5b_16082_op_ad.strap`, fifteen rows checked by
  `tests/verify_ax5b_16082_16083_listing.py`. They exist for one row
  pair: `BOP,I6088` prints `21400.47 C2` and `BAD,I6088` prints
  `21400.50 42` -- the same target through indicator 15 and indicator
  16. The 6-bit indicator number sits at bits 19-24 while the listing
  prints bits 18-23 as octal and 24-31 as hex, so the number
  STRADDLES the two printed fields. Moving OP from 15 to 14 leaves
  the octal pair at `.47` untouched and shows up only in the hex
  byte; a check reading one field would miss it. Both rows also carry
  bit 18 of their target set, making these the **third and fourth
  witnesses that I6088 is at 021400.40** -- and the first from a page
  other than 43-45. (Provenance: the witness is the printed code read
  off pp.41-42 at 600 dpi, not the passing rows -- `I6088`'s
  021400.40 is a `SYN` input to the check, chosen so the rows match.
  What the rows add is that this assembler places bit 18 where the
  listing places it.)

**THE `BIT` TABLE, found and read first-hand on PDF p.114.** Three
pages of this routine name a `BIT<n>` symbol -- I6071 uses `BIT18`
(p.41, printed 024544.00) and the indicator-walk driver uses
`BIT0%$X1` (p.45, first operand printed 24522) -- which made
`BIT<n>` = 024522 + n a reasonable guess. It is no longer a guess.
Under the heading **"-COMMON CONSTANTS FOR FETCH ONLY"**, p.114
prints the table itself:

| symbol | source | printed | address |
|---|---|---|---|
| `BIT0` | `XW,(8)400000.00,0,0` | `400000.00 00 000000.00 00` | 024522.00 |
| `BIT1` | `XW,(8)200000.00,0,0` | `200000.00 00 000000.00 00` | 024523.00 |
| ... | | | |
| `BIT17` | `XW,(8)1.00,0,0` | `1.00 00 000000.00 00` | 024543.00 |
| `BIT18` | `XW,(8).40,0,0` | `0.40 00 000000.00 00` | 024544.00 |
| `BIT19` | `XW,(8).20,0,0` | `0.20 00 000000.00 00` | 024545.00 |
| ... | | | |
| `BIT24` | `DD(BU,64,8),(8)...010...` | 22 octal digits, bit 24 | 024552.00 |
| `BIT25` | `XW,0,0,0,4` | `0.00 40 000000.00 00` | 024553.00 |
| ... to `BIT35` | | | 024565.00 |

So **`BIT<n>` is the full word whose only set bit is bit n**, and the
table runs from 024522.00 at one word per bit. Read the printed code,
not the name: `BIT18`'s `0.40 00` is bits 0-17 zero and the octal pair
40 = 100000, i.e. bit 18. `BIT0`'s `400000.00` is bit 0. The
arithmetic guessed from two other pages is exactly right, and
**`BIT0` = 024522.00 is now a printed fact**, which the eventual `TI`
transcription of p.45 will need.

Note the encoding variety in one table: bits 0-23 are `XW` value
fields, bit 24 needs a `DD(BU,64,8)`, and bits 25-35 move into `XW`'s
COUNT and REFILL operands (`XW,0,0,0,4`, `XW,0,131072,0`). The
programmer used whichever pseudo-op could reach the bit.

**TRANSMIT IMMEDIATE, and where it came from.** p.45's driver needed
`TI`, which this assembler did not have. Its format came from the
**pocket card X22-6533**, read first-hand 2026-09-22, never from the
listing (AGENTS.md rule 4). pcard-1: *"TRANSMIT--Strap Format: OP, J,
A1(I1), A2(I2)"*, with eight mnemonics -- `T`, `TI`, `TB`, `TBI`,
`SWAP`, `SWAPI`, `SWAPB`, `SWAPBI`. pcard-3's "TRANSMIT OPERATIONS"
box gives the word:

```
|   ADDRESS   |1000| I |   ADDRESS   | J |FD|BI|10| I |
0            18  24   28  32          51  55    58 60 63

SWAP  ab110      Instr'n Modifiers = ab
T     ab010        a = 0, forward       a = 1, backward
                   b = 0, direct count  b = 1, immediate count
```

A1 is a 24-bit **bit** address with index I1 at 28-31; the literal
1000 at 24-27 is the one `SIC`, `BRANCH ON BIT` and `INPUT-OUTPUT`
share; A2 is a 19-bit **half-word** address with index I2 at 60-63;
`J` is four bits at 51-54 and, with the immediate modifier, IS the
count. Written into `opcodes.TRANSMIT_CODES` and
`strap_asm.enc_transmit`, that layout reproduced **both** printed
half-words of **both** `TI` rows on p.45 with nothing read off the
page. Only `TI` has a listing witness here; the other seven are
card-only, stated in the table the way `CB_CODES` states its own
provenance.

**A hazard the encoder creates.** `StretchExecute.bsv`'s Transmit arm
moves exactly one word and ignores both the immediate-count bit and
`J`, so a count other than 1 now assembles correctly and executes
*wrongly* rather than failing loud -- against this project's
convention. Recorded in `TRANSMIT_CODES`, `strap_asm.py`'s format
list, `strap/README.md` and `docs/NEXT.md`.

**A free corroboration between the two transcriptions.** `I60K7` is
023050.00 (from I6082's `LX,$X4,I60K7`, p.41) and `I60K16` is
023061.00 (from I6086's `LX,$X4,I60K16`, p.43). Those are 9768 and
9777, nine words apart for nine in the index, so `I60K<n>` is a
regular table at **023041 + n words**. Two externals read from two
different pages agree under one rule, which neither page states.
Observed alongside it, not concluded: `SIC,I60SX1` on p.45 prints
`23041.00 80`, so I60SX1 occupies exactly that implied base word.
Whether the K table starts at a `I60K0` that is the same location, or
this is coincidence, is not settled by anything read so far.
* **I6086** (`DS`) is transcribed; see below.

**`I60S1` IS TRANSCRIBED** (`decks/ax5b_160s1_clr_inds.strap`,
81 rows) **and it is an INDICATOR-CLEARING SUBROUTINE at 022741.00 on
PDF pp.83-84**, not a save/restore harness — read first-hand
2026-09-23. Its own comment reads *"SUBROUTINE TO CLR INDS 0-19, AND
CHK THAT THEY ARE CLRD."* It clears each permanently-masked indicator
with `TI,1,11.0,$X1` and checks it went off, reporting per indicator:
*"UNABLE TO CLEAR MK."*, *"…CLR IK OR ABOVE IND."*, then IJ, EK, TS,
CPUS. About forty rows; every instruction in it is implemented.

`I60S1`/`I60SX1` are **call sites** on p.45 (`SIC` stores the return
link at `I60SX1`, `B` enters `I60S1`). Both are **located** from those
rows' own printed address fields: `SIC,I60SX1` prints `23041.00 80`
so I60SX1 = **023041.00**, and `B,I60S1` prints `22741.10 00` so
I60S1 = **022741.00** (on PDF p.82-83 by the address scan). Nothing
transcribed has needed the subroutine's body. Note that 023041.00 is
also the base the `I60K<n>` constant table is numbered from -- see
below; whether I60SX1 is literally `I60K0`'s word or merely adjacent
is not settled by anything read.

**I6086, the DS block, is transcribed** --
`decks/ax5b_16086_ds.strap`, nineteen half-words checked
bit-exactly by `tests/verify_ax5b_16086_listing.py` against the
printed machine code at octal 021365.00-021376.00. It is the deck's
own test of storage protection and its error message states the rule
this project had only from the Reference Manual: *"SV TO 1.0 FAILS TO
SET DS WHEN ENABLED."* -- word 1 (one of p.31's permanently protected
locations), the DS indicator, and the enable gate. It polls DS only
after `I6086A BD,$+.32` disables the system, independently confirming
the "a program cannot poll DS while enabled" rule. Four encodings no
listing in this project had checked: `BDS`, `BADZ` (the trailing-Z
"and zero the indicator" grammar, until now only inferred from
C22-6531 Appendix A's footnote), `SVA` into `$IA`, and `DD(BU,32,8)`
printed as 11 octal digits.

**p.45's address column, re-read at 600 dpi.** A 200 dpi render gave
`021400.00` for the row labelled I6088 and the page then looked a
half-word short. At 600 dpi the six rows print 021376.40, 021377.00,
**021400.40**, 021401.40, 021402.00 — with 021377.40 between the
second and third. So both `TI` instructions are FULL WORDS at ODD
half-words (021377.40 and 021400.40), each straddling a word boundary
per Reference Manual p.39; the apparent short arithmetic was a full
word read as a half. The transcribed block agrees independently:
`B,I6088` prints `21400.50 00`, and bit 18 — the top bit of that
octal pair — is one. Two witnesses, one printed and one encoded.
(Handwritten reader's marks sit beside 021377.00 and 021377.40; the
printed text under them is intact.)

**`TI` is the one instruction 1260's driver needs and this project
does not have.** It is not in `strap/opcodes.py`. Per AGENTS.md rule
4 its format must come from the pocket card or the Reference Manual,
never from the listing's usage -- so p.45 stays untranscribed until
it does.

Two of these map straight onto open work. **1260** covers everything
implemented on 2026-09-19 to -21 -- mask, interruption address,
interruption, boundary registers, address monitoring -- and its "unique
interruption for bits 0-47" is the per-indicator priority walk whose
landing code is at PDF pp.45/48.

**A CORRECTION THIS DOCUMENT OWED ITSELF.** This paragraph used to
read "**1268 is the only known deck test of DF and IF**, the two
address-monitoring indicators this model still does not implement;
when they are written, that routine is the oracle." That is wrong, and
the paragraph twenty lines below -- calling 1268 "Look-Ahead
store-to-fetch/store-to-load forwarding" -- was right. The two
readings sat in the same file until the routine was read first-hand on
2026-09-22. Its own header (PDF p.110) is *"1268 -- IF AND DF CLOSE TO
DS"*, and its error messages are *"EXECUTED OLD INSTRUCTION FROM
EXT."* and *"LOADED OLD DATA FROM EXT MEM."*: the wrong **value**
arrived, not an indicator failed to set. `DF`/`IF` are the Data Fetch
and Instruction Fetch **paths**, "close to DS" is close to a Data
Store, and nothing in the routine writes a mask, sets a boundary
register, branches on DF or IF, or touches protected storage.
**~~The DF and IF indicators have no deck oracle in this document.~~
FALSE, corrected 2026-09-24 — and the sentence was wrong in the one
document where it was easiest to check.** Routine 1260 **TEST 8C**,
PDF pp.76-83 (labels I60127-I60146, octal 022546.00-022732.40), is a
dedicated test of exactly those two indicators. Verified first-hand at
400 dpi; its title row reads

```
I60127  LVI,$X1,I60AD1  -TEST 8C CHECKS DF + IF UNDER 4 CONDS,  23063.03 01  022546.00
                        -1. DISABL MASK 0 FETCH OK IND NO INT
                        -2. DIAABL MASK 1 FETCH OK NO IND NO INT
                        -3. ENABLE MASK 0 FETCH OK IND ON NO INT
                        -4. ENABLE MASK 1 NO FETCH IND ON INTRPT
```

and this deck's own write-up (PDF p.8) says TEST 8 checks "THAT THE
CORRECT INDICATORS AD, DS, DF, IF ARE TURNED ON AND THAT CORRECT
TERMINATIONS AND SUPPRESSIONS OCCUR WHEN VARIOUS ILLEGAL ADDRESSES ARE
USED WITH MASK BITS SET TO BOTH ONE AND ZERO."

The paragraph above is still correct **about routine 1268** — it is a
forwarding test — but the conclusion it drew about the whole document
did not follow from that and was never re-checked.

**Two more blocks in the same span that this file does not record:**
* **TEST 8B, PDF p.75** (I60123-I60Z1, 022513.00-022545.40): DS with
  the system disabled and enabled, *plus store suppression* --
  "-SX ABOVE UB WAS NOT NOPED, DATA WAS STORED WHEN ENABLED."  A
  second and richer DS oracle beyond the transcribed I6086 block.
* **TEST 7, PDF pp.71-74** (I60105-I60122): polls DF with
  `BDFZ`/`BZDFZ` throughout, on the boundary-compare path.

**And the I6071-I6086 gap has an explanation, so it is not read as
absence again.** The sixteen per-indicator turn-on blocks run TS(4) to
DS(19) and stop. That is not because DF(20) and IF(21) go untested; it
is because they get their own dedicated TEST 8C.

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
about (~3 pages, 6 sub-cases, no interrupt/timer entanglement) -- this
reading is the correct one, see the correction above, and its TEST 2
is now transcribed AND run
(`decks/ax5b_1683_df_close_to_ds.strap`); the feature is in
fact modelled, so the deck is an oracle for existing behaviour rather
than a target for new work; and routine 1274 (address-truncation
checks for `LX/SX/Refill/StoreZero/Transmit`, pp.112-116) looked like
**the single cleanest, most isolable cross-validation target found
across all five documents** on first read, but turned out to be
untestable by construction once checked against this model's actual
address types -- see I-Box 1's `WEN`/`WEN2`/`VEN` entry above for the
reasoning and for what got transcribed instead.

## Recommended next steps, in order

1. ~~**Transcribe the STRETCH MAINTENANCE COMPOOL** (DCP manual, PDF
   pp. 129-130) -- the shared symbol table every other diagnostic deck
   depends on.~~ **DONE.** `decks/dcp_maintenance_compool.strap`,
   verified against the manual's own printed address column
   (`tests/verify_dcp_maintenance_compool.py`, wired into
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
   `decks/ibox1_wen_ven_indicators.strap`, all 5 assertions
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
   instead -- `decks/ibox4_cb_count_branch.strap` (plain
   `CB`) and `decks/ibox4_cbr_refill.strap` (`CBR`'s own
   refill mechanism), all 10 assertions across both pass, after adding
   the missing `CB[R][Z][H|+|-]` mnemonic table (`opcodes.py`'s
   `CB_CODES`) over an encoder/decoder that already implemented the
   full field space. See I-Box 4's own entry above for both.
   **Update**: both pages' printed machine-code columns have now been
   transcribed too and every assembled half-word matched against them
   (`tests/verify_ibox4_listing.py`, 137 checks) -- the CB/CB+/CBR/
   CBR+ encodings, LX/SX, and the XW index-word layout are thereby
   validated against IBM's assembler itself, not just the pocket card
   and the model's self-consistency. Same for I-Box 1's WEN block
   (`tests/verify_ibox1_listing.py`). See `strap/README.md` "Gotchas"
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
prose/reference. Each transcribed program in `../decks/` cites
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
| `jb_ax5b_ibox-5.pdf` (116pp) | I-Box 5 diagnostic | Source | routine index transcribed (p.2); 1260's pp.41-45 read first-hand; **every transcribable block of 1260's pp.41-44 transcribed** -- I6071, I6082, I6083, I6086 (`ax5b_16071_ts.strap`, `ax5b_16082_op_ad.strap`, `ax5b_16086_ds.strap`); interrupt/timer/boundary/EX -- the largest unmodeled-hardware concentration |
| `jb_af1c_floating-point.pdf` (282pp) | **Floating-point (PAU) diagnostic**, SMFF-1C, JB AF1C, Apr 15 1961, SSIP-controlled | Source | IN PROGRESS -- its routine F200 (LOAD TEST) drove out and verified the assembler's FP sign-modifier loads (LN/LA/LNA), bit-exact vs its printed code (`../tests/verify_fp_signmods.py`), and exposed a real look-ahead store-close-to-fetch gap (see plan). Running a full block still needs branch-on-bit (`BB`/`BB1`/`BZB`, decoded not executed) and the SSIP framework; blocks using divide/double wait for stage 4e. |
| `ja_bb6b_worst_pat_test.pdf` (20pp) | Worst-pattern memory test | Source | NOT YET -- runnable against `StretchMemory.bsv` (the interleaved units); a memory-model codesign target |
| `ja_bm6a_unique_adr_test.pdf` (11pp) | Unique-address memory test | Source | NOT YET -- memory-model target |
| `ja_bp6a_memory_patterns_test.pdf` (6pp) | Memory-patterns test | Source | NOT YET -- smallest memory test, good first memory codesign target |
| `ja_ua1_ssip.pdf` (52pp; **pp.7-52 an unbroken STRAP listing**) | SSIP (System Test Program supervisor), JA UA1, "SSIP CBD 2-9-61" | Source | RUN (partial): `ssip_sip17_reset` (SIP16/SIP17, PDF pp.17-18, bit-exact vs `../tests/verify_ssip_sip17_listing.py`), which named the five instruction-exception indicators and settled that slot 14 is not one. CORRECTED 2026-09-19: this row previously described the file as framework prose only. It is not. pp.1-6 are the writeup and the Maintenance Tape Control Card; p.7 opens with the source line "PRINID, SSIP CBD 2-9-61 JA UA1" and p.52 closes with `END,%8@100.` at 002732.71. The listing is 1-up fanfold with NO printed page numbers, so it is cited by PDF page, unlike every other tape here. It also explains the SIC/BEW pass-fail idiom the transcriptions reproduce externally. |
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

Cross-reference discipline (per this survey): every `../decks/
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

**THAT SENTENCE USED TO READ "Beyond bitsavers, no other archive is
known to hold 7030 software or documentation not represented here."
IT IS FALSE, and was corrected 2026-10-19.** What IS true, and was
re-verified by diffing the four bitsavers listings (`/`, `ce/`,
`diag/`, `mcp/`) against `ls docs/*.pdf`, is narrower and worth
stating exactly:

**bitsavers' `pdf/ibm/7030/` tree is held completely -- 52 of 52,
filename for filename.** There is no `bits/IBM/7030/`, and
`bitsavers.org/magtape/` 404s (`pdf/ibm/magtape/` is a different
thing and is NOT fully held).

Known to exist elsewhere and NOT held:

| Where | What | Why it matters |
|---|---|---|
| `bitsavers.org/pdf/ibm/7950/` | `Harvest_prelim_May57.pdf`, `Harvest_Nov1957.pdf`, `R22-9789_7950_HAP_III_Ref_Man_1962.pdf` | The 7950 Harvest is the Stretch attachment, and `ka_ua1`'s own header reads "DIAGNOSTIC CONTROL PROGRAM FOR 7030/7950 EDP SYSTEM" -- the harness being transcribed targets both machines |
| `bitsavers.org/pdf/ibm/magtape/` | `A22-6589-1_magTapeReference_Jun62.pdf` | The 729-family tape reference. Tape device timing is the one area `docs/timing_oracle.md` has no source for at all |
| Computer History Museum, catalog 102633187 | *IBM 7030 Master Control Program MCP Preliminary Reference Manual*, Nov 1961, 136pp | Predates every MCP document held (earliest is J22-6559, Dec 1960; C22-6678-1 is Jun 1964). **Catalogued, not digitised** at any guessable path; would need a CHM request |

**AND THE LARGEST GAP IS ONE THIS REPO CAN NAME PRECISELY, because
IBM's own index of it is sitting in `docs/`.**
`7030_SystemTestPrograms_Aug61.pdf` is the acceptance-test schedule;
its program list and write-ups enumerate the diagnostic universe, and
**fourteen of those programs have no surviving listing in any archive
surveyed.** Several are squarely on this project's path:

* **JB AV1B / AV1C, VARIABLE FIELD LENGTH (`SMFV-1`)** -- the VFL
  diagnostic. `bsv/StretchVFL.bsv` has no historical oracle at all,
  where `StretchFP.bsv` has `jb_af1c`. This is the single most
  valuable missing document for this project.
* **KA AT1 "RAW SPEED 1"** and **KA BT1 "MEM TIMER"** -- programs that
  MEASURE and PRINT instruction and memory times. A second timing
  oracle independent of Performance Characteristics, which is exactly
  what `docs/timing_oracle.md`'s rebuild verdict asks for.
* **JA EE3 (Basic Exchange/tape with interrupts on)**, **JA CE1/CE2
  (729-IV)**, **JA ES1 (operator's console)**, **JA NE4/NE5/NE6
  (printer, reader, punch)** -- device-level oracles for everything
  in `StretchIO.bsv` that currently has none.
* **JA UD1A "TAPE LOAD"** -- builds the maintenance master tape and
  defines its control-card format. Distinct from the held `ka_ul1`,
  which is a card-deck loader.

The maintenance tape holds up to 32 programs (switches 0-31); the
Aug-1961 schedule populates only 0-15, so more decks existed than even
this index names. A request to CHM naming exact IBM file numbers --
**JB AV1C, KA AT1, KA BT1 first** -- is far likelier to succeed than a
general ask.

One roster was not checked: the DCP's own test-ID schedule inside
`ka_ua1_diagnostic_ctl_pgm.pdf` is a second potential index of
programs and may name more.


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
