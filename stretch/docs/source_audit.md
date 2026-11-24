# What the corpus contains that this project has never read

*Started 2026-10-27, in answer to "have you gone through all the OCR'd
work and put it in the plan?" The honest answer was no, and this file
is the audit that makes the gap measurable instead of vague.*

## The method, and why it is a measurement rather than an impression

`docs/ocr/` holds **24 documents, 283,351 lines** of machine-read
primary source. There has never been a per-document record of what has
been mined, so "have we read it?" could only be answered by feel.

The proxy used here is objective and cheap: **how often does each
document's own citation ID appear anywhere in the project's prose and
code** (`docs/*.md`, `bsv/*.bsv`, `strap/*.py`, `tests/*.py`,
`decks/*.strap`). It is a proxy, not a measure of understanding -- a
document can be cited once and understood, or fifty times for one
sentence -- but across 24 documents the spread is wide enough to be
informative, and the extremes are unambiguous.

## The census

| document | lines | cites | cites/1000 lines |
|---|---|---|---|
| `C22-6728-1` MCP Sys Analysis Guide | 49,152 | **15** | **0.3** |
| `Planning_A_Computer_System` (Buchholz) | 19,302 | **8** | **0.4** |
| `R23-9695` CE Intro Pgmg Vol 3 | 10,708 | **6** | **0.6** |
| `C22-6729` STRAP II Sys Analysis Guide | 28,201 | **21** | **0.7** |
| `R23-9732` 7101 CPU CE Manual | 23,527 | **19** | **0.8** |
| `ADescriptionOfStretch_Dec59` | 2,049 | 3 | 1.5 |
| `C22-6728` MCP Sys Analysis Guide | 47,826 | 78 | 1.6 |
| `J22-6559` MCP User's Guide | 1,068 | 3 | 2.8 |
| `22-6530-2` Reference Manual | 21,221 | 66 | 3.1 |
| `Bloch` Engineering Design of Stretch | 1,552 | 5 | 3.2 |
| `N22-0085` MCP RefMan Update | 607 | 2 | 3.3 |
| `R23-9694` CE Intro Pgmg Vol 2 | 7,639 | 30 | 3.9 |
| `X28-6131` MCP Pocket Card | 217 | 1 | 4.6 |
| `C22-6578` Programming Examples | 4,828 | 26 | 5.4 |
| `C28-6379-0` MCP Loader | 2,167 | 13 | 6.0 |
| `C22-6678-1` MCP Reference | 6,886 | 97 | 14 |
| `C28-6129` STRAP-II | 9,503 | 153 | 16 |
| `7030_Performance_Characteristics_Vol2` | 10,719 | 341 | 32 |
| `TR00.722` Stretch I-Unit Design | 2,326 | 76 | 33 |
| `C22-6531` STRAP (1960) | 6,010 | 218 | 36 |
| `X22-6533` Pocket Card | 1,088 | 91 | 84 |
| `7030_Performance_Characteristics_Vol1` | 3,023 | 341 | 113 |
| `MCP_Mar63` listing, both volumes | 23,732 | 2,265 | 95 |

## >>> THE FINDING: ~168,000 LINES ARE ESSENTIALLY UNMINED, AND THREE OF THE FIVE BIGGEST GAPS ARE ON THE CRITICAL PATH <<<

The five documents at the top of that table total **168,000 lines** --
**59% of the corpus** -- against 69 citations between them. And they
are not peripheral:

* **`C22-6728-1`, the MCP System Analysis Guide, is the largest
  document in the corpus and the least read.** It documents MCP's
  internals. It has **49 hits for "IOD CARD"**, 38 for "I-O REQUEST",
  19 for "REQUEST TABLE" and 13 for "IOREQ" -- which are exactly the
  questions this project spent a session deriving from a listing's
  progressive-indexing increments and a step-cap bisection.
* **`R23-9732`, the 7101 CPU CE manual, is the machine's own
  engineering manual** and the look-ahead is the largest absent
  structure in the model (`docs/microarchitecture_roadmap.md` M2).
  `docs/spec_lookahead.md` was assembled mostly from the Performance
  Characteristics volumes.
* **`C22-6729` is STRAP II's compiler internals**, and the assembler
  has repeatedly had to derive card semantics from listings.

### The one-line proof that this is not a theoretical cost

`docs/mcp_io_tables.md` records `TLAST` as an open question with "two
readings, neither settled", after a search of all 72 transcribed decks
established that nothing writes it. The guide, at line 10966 of the
"-1" edition, appears to say:

> `TLAST` (.18) -- "1 bit, indicates the last plus one word of this
> I-O request table"

A sentinel PAST the end -- which settles it in favour of the second
reading, that a `DRZ`-zero `TLAST` on every real entry is correct and
nothing need write it. **One grep, against a question that cost a
subagent and a commit.**

*(Needs rendering before it is cited as fact: the OCR is a finding
aid, per `docs/ocr/README.md`.)*

## What this file becomes

Three audits of the gap documents are under way. Their findings land
below as **plan items**, and the goal of the exercise is the thing
asked for: a clear set of objectives for after MCP runs, so the work
can be finished rather than extended.

## Audit 1 of 4: `R23-9695`, CE Introduction to Programming Vol 3

**10,708 lines, 6 citations.** Done by hand rather than delegated,
because the other four gap documents are out with agents.

### What it actually is, and this was not known

Volume 3 is **the input-output volume.** Its own headings: "Introduction
to 7030 Input-Output" (line 131), Figure 7-1 "7030 Input-Output Section"
(254), Figure 7.1-1 "Card Format" (332), the 7553 Card Punch (345), a
1403-2 printer schematic (541), carriage control codes (585), "Console
Entry and Display Devices" (784), the numerical display/switch code set
(924-950), binary switches (955), control word and index word (1396,
1404).

The project's six citations are all to **Appendix A and the abbreviation
glossary** -- `docs/NEXT.md` cites p.118's storage-assignment table and
pp.128-134's glossary. **Chapter 7, the entire I/O chapter, has never
been cited**, in a project whose current blocker is an I/O table.

### Finding 1: an independent confirmation of the card layout

`strap/cards.py` derives a card as 80 columns x 12 bits = 15 words from
`R23-9702` Figure 4.3-1, and `tests/verify_card_columns.py` pins
12 bits per column because the IOD card's field map (column 32 = bit
372) rests on it. Vol 3 says the same thing from a different manual:

> *"In the no-ECC mode, the entire contents of a card appear in core
> storage as 15 full words. In the ECC mode, a card is treated as 13
> full words. These 13 words correspond to 78 card columns, with the
> last two columns ignored."* (line 300)
>
> *"VFL instructions, with a field length of 12 specified, facilitate
> the handling of standard IBM coded information, one character at a
> time."* (line 308)

**Two independent sources, one layout**, and the ECC remark matches
`cards.py`'s own note about two columns being thrown away. This is the
kind of corroboration the project wants and had not got.

### Finding 2: the console switch encoding, which the Reference Manual does not give

Reference Manual printed p.150 says a console READ returns "the three
words scanned from the console switches" and stops there. Vol 3 gives
the contents:

* a **four-bit code set** for the numerical display and switches (lines
  928-950): `0000`-`1001` are the digits 0-9, `1010` is a decimal point,
  `1011` a minus sign, `1100`-`1111` blank, and `1111` *"is generated
  when no digit key is depressed"*;
* **32 binary toggle switches** in two sets of 16, grouped by fours, and
  on a READ *"the settings of the binary switches make up the first four
  bytes of the third input word, from left to right, with bit 0
  reflecting the state of the leftmost light"* (line 955);
* on a WRITE, *"the contents of the second output word are displayed in
  the numerical display, from left to right, starting with bits 0
  through 3 for the leftmost digit"* (line 915).

**The model is not wrong here, and that is worth saying.**
`bsv/StretchIO.bsv` treats the three switch words as opaque
(`consoleSwitchWord`), and `tests/gen_mcp_boot_tb.py:496-520` already
documents the path correctly from `C22-6678-1` p.29 -- time in binary
keys 0-23, date in 32-55 -- with word 0 deliberately zero so MCP takes
printed p.22 line 12's `KFI(BU,24),0,40 -NO TIME ENTERED` branch. What
Vol 3 adds is **the encoding behind the opacity**, which nothing has
needed yet and which the next console path will.

### Plan item: the SECOND console read

printed p.22 line 5 is `RD(SEOP), 0.0($15), XDCW2 -GET IPL OPTIONS`
and is understood. **printed p.23 line 44 is a second one --
`RD(SEOP), 0.0($15), XDCW2 -GET CHANNEL AND UNIT` -- and nothing in
`docs/` discusses it.** With Vol 3's code set now in hand, what MCP
reads there is checkable rather than guessable. Whether it is on the
boot's live path is the first thing to establish.

### Gap list for this document

| chapter | worth mining? |
|---|---|
| 7.0 Introduction to I/O, Figure 7-1 | **yes** -- a block diagram of the I/O section |
| 7.1 Card reader / punch, card format | **mined above** |
| 7.1.x 1403-2 printer, carriage control codes | **yes** if the printer is ever more than a stand-in |
| Console entry and display devices | **mined above** |
| Control word / index word (1396, 1404) | cross-check against the Reference Manual's Figure 35 |
| Appendix A storage assignment, glossary | already cited |

## Audit 2 of 4: `C22-6728` / `C22-6728-1`, MCP System Analysis Guide

**97,000 lines across two editions, ~13 of 550 printed pages cited.**
The full report is long; what follows is what changes the project.

### >>> RETRACTED: THE IOD FIELD IS AT CARD COLUMNS 63-72, NOT 32-36 <<<

`a62b6ba` derived the IOD card's field as five columns at 32-36, by
dividing `Y UTOE`'s offset of 372 bits by 12 bits per column, and
`tests/verify_card_columns.py` asserts it as
`yutoe_372_is_column_32_one_based`. **The arithmetic is right and the
proposition is false.**

`Y UCBF1` does not hold the raw card image. It holds **SCA6's output,
six bits per character.** The guide says so: printed p.66, *"Uncode
uses two subroutines, SCA6 and SBRK8, respectively to convert the card
to BCD"* and *"Y UTOE is the symbolic location of the reference number
on a BCD IOD card. Cards are converted to BCD into Y UCBF1."*

**The clincher is in the listing and I verified it myself.** Line 2156
of `docs/ocr/MCP_Mar63_001-249.txt` is `VF,YUCBF1+.54`, the second
argument of the same call sequence:

```
 54 / 6  =  9.00  -> character 10 = column 10, and CF,53 -> columns 10-62
 54 / 12 =  4.50  -> MID-COLUMN.  Impossible for a character-string argument.
```

**54 is not divisible by 12.** Under my reading that argument lands
half way through a column, which no character string can do. Under the
six-bit reading it is column 10, and 53 characters from there is
columns 10-62 -- exactly the documented statement field.

And the rest closes on it:

* `372 / 6` = 62 exactly -> **column 63**; `372 + 60 = 432 = 72 x 6`,
  so the field **ends exactly at column 72**, the documented last
  column of the IOD statement area (73-80 are program ID).
* `LF(BU,60,6), YUTOE` reads **ten six-bit bytes**, and `C22-6678-1`
  printed p.9 gives I/O Reference Number = **cols 63-66** (four) and
  Absolute Exit = **cols 67-72** (six). Four plus six is ten.
* The listing's own comment on the `SYN` names both: *"LOCATION OF
  REF # AND TOE"*.

**PRECISION GUARD, because the correction is narrower than it looks.**
`strap/cards.py::card_words_cols` and the 12-bit-per-column card model
are **right**, and `R23-9702` Figure 4.3-1 is right -- SCA6 itself
reads the card that way (`CF,80`). Two things are wrong and only two:

1. the division of **`Y UCBF1`'s bit offset** by 12;
2. the stated *motivation* for `card_words_cols` -- "ten six-bit
   fields, two per column, which no single character can punch". After
   SCA6 there is **one** six-bit character per column, and columns
   63-72 are ten ordinary BCD characters a keypunch produces. The
   raw-column capability is still correct and still useful; its
   justification was not.

> **AND IT IS A CANDIDATE ROOT CAUSE OF THE EMPTY REQUEST TABLE.** If
> the fixture punches the reference number anywhere but columns 63-66,
> the IOD decodes with reference number **0**.

### The fixture cannot work, and now that is citable

printed p.98: *"The assignment of absolute units from IOD cards will be
done for MCP at IPL time through a **modified decode-assign-move
routine** (SB22, Figure 50)."* The guide then enumerates **four cases**
by normal/abnormal IPL x mode, the mode coming from the `MCPP` card
unless the operator overrides at the console. The minimal one -- normal
IPL, unoverlapped -- requires MCP IOD cards defining **a card reader
and output tape units**.

**One blank IOD card satisfies none of them**, and a card blank but for
`B` in column 1 never reaches Decode at all: Uncode masks field 1
against `Y TYPMK` and takes the error return.

### Two things the project recorded as unknown, printed in the guide

* **The four-bit equipment type codes.** `tests/run_tests.sh:2748` says
  "what remains invented is the equipment table's four-bit codes, which
  are on a page nobody has transcribed." printed p.68 gives six:
  `0001` disk, `0010` console, `0011` card reader, `0100` card punch,
  `0101` printer, `1000` tape. (Caveat: this is the `TIOREQ` *request*
  type; whether it is the same encoding as the channel status table's
  `SEQUIP` is likely but not stated. `1000` being non-contiguous with
  `0101` is a strong fingerprint for the comparison.)
* **`TLAST`** -- narrowed, as recorded earlier in this file.

### Two edition-confusion bugs -- BOTH FIXED 2026-10-28, and an edition concordance

> **>>> THE RULE THIS ESTABLISHES: NEVER CARRY A BARE FIGURE NUMBER OR
> PAGE BETWEEN THE TWO EDITIONS OF `C22-6728`. <<<** They renumber, and
> the collision is not benign -- the base edition's Figure 44 is the
> chart this project depends on, while `-1`'s Figure 44 is "The
> Relocation Table Structure", a different chart that would read as
> plausible. Always name the form number WITH the figure.

**Verified, both editions, PDF page == printed page.** That offset is
not assumed. In `-1`, two running heads confirm it: "Debugging Aids
215" on PDF page 215, "Debugging Aids 221" on PDF page 221. In the base
edition, three: "System Operation Programs" 85, 87 and 91, each on the
PDF page of the same number.

**Every page in the table below was read off a page marker, not derived
from the +5 pattern.** The pattern does not in fact hold: Chart 1 moves
90 -> 99 (+9) and Chart 2 moves 92 -> 100 (+8). The figure NUMBERS move
by 5; the PAGES do not move by a constant, and an inferred page here
was wrong by one before it was checked.

| chart | `C22-6728` (base) | `C22-6728-1` |
|---|---|---|
| The Initialization Program - Chart 1 | **Figure 44, p.90** | **Figure 49, p.99** |
| The Initialization Program - Chart 2 (decode-assign-move) | **Figure 45, p.92** | **Figure 50, p.100** |
| The Relocation Table Structure | -- | Figure 44 (the collision) |

**AND THE ROUTINE LABEL CHANGED WITH IT, which is the worse trap.**
The base edition reads "decode-assign-move routine (**X20B**, Figure
45)"; `-1` reads "decode-assign-move routine (**SB22**, Figure 50)".
This project cites `SB22`, which is the `-1` name, so a search for
`SB22` in the base edition returns nothing and would read as the
routine being absent rather than renamed.


The renumbering is pinned by the *same sentence* in both editions:
base, "At X13 (Figure 44), the initialization program proc-"; `-1`,
"At X13 (Figure 49), the initialization program proc-".

### The two bugs as originally found



* `docs/mcp_io_tables.md:102` cites "`C22-6728-1` ... its §215 UPDATE 30
  writeup". In `-1`, printed p.215 is **Debugging Aids**; UPDATE-30 is
  printed pp.228-239. The citation mixes a `-1` form number with a base
  page number.
* **Figure numbers differ by 5 across the IPL block.** The project cites
  base numbers (`gen_mcp_p17_tb.py:175` cites "p.90's Figure 44"); in
  `-1` that chart is **Figure 49, printed p.99**.

## Audit 3 of 4: `R23-9732`, 7101 CPU CE Reference Manual

### >>> FIRST, A CORRECTION TO THIS FILE'S OWN METHOD <<<

The census above put this manual among the gaps on 19 citations in
23,527 lines. **That reading is wrong, and the way it is wrong matters
for the whole audit.** `docs/spec_lookahead.md`'s provenance block
records that a prior delegated agent rendered and read CE PDF pp. 92,
93, 96, 104, 114, 117, 171, 172 and 175 -- the highest-value look-ahead
pages in the volume. The nineteen citations are **concentrated, not
absent.**

> **SO CITATION DENSITY CONFLATES "NEVER READ" WITH "READ AND CITED
> CONCISELY."** It is still the right first cut -- it found a 49,000-line
> document cited fifteen times and that one WAS unread -- but a low
> score is a question, not a verdict, and each gap document has to be
> checked against the project's own provenance notes before it is
> called unmined. The two documents this file has now examined properly
> fell on opposite sides of exactly that distinction.

### What is genuinely unmined here

* ~22 further look-ahead flow-diagram pages (95, 97-103, 105-113,
  115, 116, 118, 119);
* **the complete LA timer inventory, Table 3.4.1**;
* **Section 4 Procedure 1** (pp. 273-279), filed as a field-service
  adjustment procedure and in fact the best memory-timing source in
  the volume;
* Tables 3.3.1/3.3.2/3.3.4, the PAU trigger, logic-area and datapath
  gate inventories;
* **the PAU/SAU timing-chart category (pp. 225-243)**, which does give
  numbered per-cycle charts.

### The status of "no per-action look-ahead cycle count" CHANGES

`docs/spec_lookahead.md` §1123 marks this `[NOT IN THE SOURCES]`, and
`docs/microarchitecture_roadmap.md` M2 correction 4 says any LA-internal
count in the Bluespec is invented and must say so.

**That survives as to a NUMBER** -- Index 3-1 lists eleven diagnostic
categories and the only timing-chart category is Cat 8, PAU; there is
no LA timing-chart category. **But the LA's per-action timing has a
named hardware structure, and this manual inventories it completely:
thirteen timers**, each with its phase triggers and ALD page --
operand check, operand correct, transfer bus, transfer indicator,
arithmetic bus, indicator register, houseclean, LA houseclean over, LA
indicator test, store data, LA-to-Instruction-Unit, clear index, write
index. Every LA action in Figures 3.2.3-3.2.27 is drawn as a vertical
swim-lane under one of them.

> **AND THE AGENT REFUSED THE INFERENCE THAT WOULD HAVE BEEN WRONG**,
> which is worth recording as much as the finding. "Two triggers = two
> cycles" is rejected on three grounds: the column headers are logical
> combinations (`E`, `E·M`, `E+M`, `M`) and so overlapping states, not
> a sequential chain; the arithmetic bus timer has **three** triggers
> (EE/E/M), so there is no uniform two-stage model; and **the clock is
> two-phase A/B**, so "one phase" is ambiguous between one A-or-B pulse
> and an A+B pair -- a factor of two straight into the model. The
> manual's own control glossary is the evidence: "1 PULSE … either an A
> or a B pulse", "2 PULSE … either A and B or B and A", "3 PULSE …
> either ABA or BAB".
>
> **So `[NOT IN THE SOURCES]` should be REWRITTEN, not deleted**: the
> count has a named structure and known pages, and the A/B-pulse
> mapping must come from a clock-timing source rather than from
> counting triggers.

### One arbitration finding, and a warning not to over-read it

Figures 3.2.3 and 3.2.26 show a numbered priority scheme -- `3RD
PRIORITY CHKR`, `REQUEST 4TH PRIORITY FOR I CHKR`, implemented with
"no N req" hold lines. **This is access to the I CHECKER (the ECC /
parity unit), not the memory bus.** Roadmap stage M3 is about memory
and bus arbitration and must not absorb this by name similarity.

## Audit 4 of 4: `C22-6729`, Buchholz, and the two early papers

### `C22-6729` carries a complete ENCODING of STRAP II's expression language

> CORRECTED 2026-11-07 (`reconstruction_plan.md`; printed p.198 re-read in
> the ink). The original heading said "COMPLETE FORMAL GRAMMAR", which
> overstates the source. Appendix C is the bit encoding of an expression
> STRAP II has already parsed. It is not a grammar. The eight 3-bit operator
> codes on p.198 (`.+ .L .R U- * / + -`) use the whole field, so there is
> no `**`. Which forms are legal (GETFLD's syntax matrix, printed pp.83-84)
> is described, but its cells are never printed, so the grammar must be
> derived and the derivation marked as such.

Appendix C, printed pp.197-201, is the bit-level encoding of what STRAP
II actually parsed: an operator is nine bits -- a 1-bit exists flag, a
**3-bit operator code**, and a 5-bit datum reference number.
`strap/strap_asm.py`'s `tokenize_expr` accepts `+`, `-`, bit-address
dots, symbols, `$sys` and a radix prefix, and has **no `*`, `/`, `**`
or parentheses**. Sixteen plan items came out of this document; the two
that bear on work done this week:

* **Entry modes are a three-bit code** (printed p.21), and `(8)` octal
  and `(.n)` are **peers in the same field** -- `(r)` radix is `010`,
  `(.n)` parenthetical integer is `011`. `(.n)` is a leading entry
  mode, not an afterthought, and the radix may be **2-16**.
* **`(.39)9` is corroborated.** Appendix C gives a gp as an exists
  flag, **six bits of n** (so n is 0-63), and "a coded expression for
  the entry to be **OR'ed into the field**", repeatable. And the forms
  where a gp is forbidden are **`SYN`, `DR`, `DDI`, `DRZ`** -- `XW` is
  not among them, so `T PREFT XW, T IOREQ, 0, (.39)9` is legal and the
  reading that gives its count field `9 << 6` = 576 stands.
* **Address-term scaling is stated in prose with a worked example**
  (printed p.144): *"if the address SAM + 10 is to be inserted into an
  18-bit address, the routine adds 10 full words; if a 19-bit address,
  it adds 10 half words; if a 24-bit address, it adds 10 bits … the
  addition is determined by the FUNCTION of the address, not the size
  of the field."* That is the same family as the `effAddr18`/`effAddr19`
  bug, and it says the choice is a property of the operand's function
  -- a cleaner invariant than the per-call-site constants
  `eval_addr_field` uses today, and testable against the listing
  oracle. **It does not settle the bare-integer-as-address gap**, which
  is a different question; do not conflate them.

### Buchholz Appendix A is an independent cross-check, barely touched

A.3 (registers and special addresses), A.4 (operations and modifiers),
A.5 (**the 64 indicators with class codes** -- what
`opcodes.INDICATOR_BITS` follows), A.2 (instruction formats with bit
boundaries), Appendix B (six worked programs). Cleanly OCR'd and
independent of the Reference Manual.

### The early papers: dated, and two misleading figures flagged

* `ADescriptionOfStretch_Dec59` is **mostly as-designed**, but its body
  carries timing numbers **its own author retracted on a separate
  errata sheet**, and its indicator table is a genuinely earlier
  design. Cite A.5, not Johnson's Table 3.
* `Bloch_EngrDesOfStretch_1959` is as-designed and **superseded by
  `Planning` ch.14, which is its own revision** -- but the discussion
  transcript at the end is primary source found nowhere else. Its
  "765 different types of instructions" **disagrees with its own
  figure's total of 735**; do not cite either.

### >>> AND ONE FLAG FROM THE AUDIT IS A FALSE ALARM, WHICH I CHECKED RATHER THAN PROPAGATED <<<

The report suggests the roadmap "may have mis-attributed Bloch's 2.0 µs
memory cycle to Buchholz". **It has not.** The project cites **2.1 µs
to Buchholz §14.1**, `docs/ocr/Planning_A_Computer_System.txt` line 2089
reads *"2.1 microseconds"*, and
`docs/microarchitecture_roadmap.md:130` already records that Perf.
Char.'s measured **2.2** is preferred over it. Nothing to fix.

> A "may have" from a delegated audit is a question, exactly as a low
> citation count is. This session has already paid for the habit of
> acting on one before checking.

### A real reconciliation item, though

Bloch's discussion transcript says *"**There is no such thing** [as a
machine cycle] … each unit has a clock … between 200 and 300
millimicroseconds"*, while `docs/exchange_and_io.md:1533` reasons about
"the CPU runs on 0.3 µs cycles **from a master oscillator**". The 7101
CE manual's two-phase A/B clock (audit 3) sits between them. **One
paragraph of reconciliation is owed**, and it matters because the whole
cycle-accuracy goal is denominated in that unit.

---

# THE GOAL SET

*What the audit was for. Phase A is the current blocker; everything
after it is the "what else" list, ordered, with the evidence for why
each item is on it and what would finish it.*

## Phase A — finish MCP. Three items, all now citable.

**A1. Punch the IOD card at columns 63-72.** `C22-6678-1` printed p.9:
I/O Reference Number **cols 63-66**, Absolute Exit **cols 67-72**. The
fixture's `TERMINATOR_CARD` is blank, and a card blank but for `B` in
column 1 never reaches Decode -- Uncode masks field 1 against
`Y TYPMK` and takes the error return. *Done when `T IOREQ` is
non-empty at the ASSIGN call.*

**A2. Supply the cards case 1 actually requires.** printed p.98: IPL
assignment is a **modified** decode-assign-move (SB22, Figure 50) with
four cases; the minimal one -- normal IPL, unoverlapped -- needs IOD
cards defining **a card reader and output tape units**. *Done when
ASSIGN sets the disposition bit.*

**A3. Supply the `MCPP` card.** printed p.101: the mode is taken from
the MCP parameter card unless the operator overrides at the console.
Without it the case selection is undefined. *Done when the mode is a
chosen value rather than whatever zero decodes to.*

**A4. Find where the boot is spinning, and what it is waiting for.**
Added 2026-10-28, and it REPLACES the conf-count hunt rather than
extending it. Twelve hypotheses named every writer of `$10` and found
each one doing what the listing says; the 417 wrong-way recoveries that
follow are sourced as correct (Perf Char PDF 41 excludes CB-family and
the eight index indicators from guessing, and the model implements both
exclusions). So the conf counts are not corrupted -- **the boot never
reaches the code that fills them.** It is spinning in an MCP loop at
step ~6.12M whose closing branch is an arithmetic-indicator branch
taken every iteration, at an exact 61-cycle period.

*The instrument:* log the recovery target `o.next` at `StretchCore`
1142, map the half-word PC through the listing, and read what MCP is
testing. One run. *Done when the spinning loop is named in the listing
and the indicator it waits on is identified.* The three SWAPs already
located nearby -- half-words 3006, 3388, 3391 and 3970 -- bracket it,
and 3970 is a 12-word context swap, so the loop is in MCP's
post-context-switch path, not in the IPL bootstrap.

**Why this ordering matters:** A1-A3 are about feeding MCP the right
cards. A4 is about whether it then runs. A4 is cheap, it is upstream of
the symptom every earlier item chased, and it is the only item whose
answer is currently unknown rather than merely unwritten.

> **RENDER FIRST, BEFORE WRITING ANY OF IT:** `-1` printed **pp.99-100**
> (Figures 49-50) is the flowchart of the project's own p.17/p.18 code
> and the highest-value page pair in either volume; and `-1` printed
> **p.72**, Assign's configuration-change section, which decides
> whether the "phantom request" is a defect or the documented initial
> entry.

## G1 — Cycle accuracy. The roadmap, with the audit's corrections folded in.

| stage | state | what the audit adds |
|---|---|---|
| **M0** harness | **done** -- two-sided `CYCLES=N+-T`, measured baseline | the atlas oracle is still **unwritten**; that is M0's real remainder |
| **M2** look-ahead | `LaKind` landed (no-op); level occupancy **built and reverted** | **13 named timers** (Table 3.4.1) with ALD pages; ~22 unmined flow pages (95, 99-119) |
| **M1** datapath | blocked on M2 | **PAU/SAU timing charts pp.225-243 give numbered per-cycle charts** -- the first real per-cycle source |
| **M3** memory/bus | not started | **§4 Procedure 1, pp.273-279** -- filed as field service, actually the best memory-timing source in the volume |
| **M4** error detection | deliberately last | the I-checker priority scheme (3rd/4th) is **checker arbitration, not the memory bus** -- do not absorb it into M3 by name |

**G1.0, and it gates the rest: reconcile the clock unit.** Bloch's
discussion transcript denies a machine cycle exists; the project reasons
from a 0.3 µs master oscillator; the 7101 manual has a **two-phase A/B
clock** where "one phase" is ambiguous by a factor of two. *Cycle
accuracy is denominated in this unit and it is currently three
different units.*

**G1.0 answered for the CPU, 2026-11-08: `clock_unit.md`.** One model clock
is one A-or-B pulse slot, 0.3 µs, and A+B is the 0.6 µs control cycle, so the
model's unit needs no change. Fig 2.10.1's 600 NSEC was checked in the ink by a
second reader. The period is nominal, since no page read prints the frequency;
memory, Exchange, disk and the timer are off this grid; Table 6's 11.2 µs fits
no outcome and stays open.

**G1.1 Finish M2 properly**: a level is a PART of an instruction, which
needs the kind field (done), a level carrying only its own part, and an
E-box consuming a sequence instead of one whole `di`. The reverted
I-box-level change goes back in unchanged once results stop being
timing-dependent.

## G2 — Close the instruction set. The best-measured activity in the project.

**G2.1 The worked-example worklist.** Six run, four found bugs; **31
problem headings survive OCR in `C22-6578` with visible gaps, so ~45
exist and ~40 remain.** This is the highest-yield-per-hour work on
record here and it needs no new infrastructure.

*Counted again 2026-11-08 (the 2026-10-29 re-census below has the method):
`C22-6578` has 44 problems; **eleven have run, 33 remain.** Chapter 1 is
finished; the next in book order is Problem 2.3.  The batch just run, 1.1,
1.2, 1.3, 1.4, 1.5, 1.7, 1.8 and 1.9, found **no wrong result in anything
the model executed**, and that is the measured yield: see "G2.1, THE FIRST
BATCH" below.*

*Counted again 2026-11-15: **twenty have run, 24 remain** (2.8, which is
transcribed but cannot run, and Chapters 3 and 4).  Chapter 2 is finished
as far as the model can take it; the next in book order is Problem 3.1.
Problems 2.3-2.7 and 2.9-2.12 again found **no wrong result in anything the
model executed** -- and found nine defects in seven of the PRINTED methods,
which the model's agreement with a hand trace is what shows.  See "G2.1,
CHAPTER 2" below.*

**G2.2 Buchholz Appendix B** adds six more worked programs, independent
of `C22-6578`.

**G2.3 The arms still refused.** The decimal VFL set, `SWAP`'s
remaining variants.  (`SWAP` was STALE here: all four forms and the
zero count were already built, 2026-10-23 and 2026-11-08 -- `docs/NEXT.md`
"EVERY OP THE MODEL STILL SETS".)  **Decimal stage 1 is built (2026-11-16):** decimal
`L`, `LWF`, `+`/`-`, `+MG`, `M+`, `M+1`/`M-1`, `M+MG`, signed `ST` and
`SRD`, the sums through the decimal box `mkDecBox`
(`bsv/StretchDecBox.bsv`); `decks/vfl_decimal_add.strap`.  **Stage 2,
the same day:** decimal `K`/`KF` and `KE`/`KFE`/`KR`/`KFR` in both
radices (printed pp.65-67; `decks/vfl_decimal_compare.strap`, Figure 15
as printed).  **Stage 3, the same day:** `LTRS` in both radices, and
decimal `*`/`*+`/`/`, which printed pp.68-70 define as LOAD TRANSIT AND
SET's action with DTR, not as arithmetic (`decks/vfl_ltrs.strap`).
**Then, the same day, the last three:** `RNX` (printed p.27;
`decks/rnx.strap`, `decks/ibox4_rnx_run.strap`), `DCV` in both radices
(printed p.74, the converter box `mkCvtBox`; `decks/vfl_dcv.strap` runs
Figure 19 whole) and decimal `LFT` (printed p.69;
`decks/vfl_lft_decimal.strap`).  **No operation the manual defines is
refused for want of an arm.**  What still sets OP besides the machine's
own cases is three open model limits (crossing `M+`, a tail below word
32, three reads) -- `docs/NEXT.md` "EVERY OP THE MODEL STILL SETS". `storeTarget`'s invariant names the ones that will
need a case when they land.

## G3 — Assembler completeness, from `C22-6729`'s grammar

**G3.1** Implement what Appendix C encodes and `tokenize_expr` does not:
`*`, `/`, parentheses, and `**` (noting App. C's 3-bit operator field
has no free code for `**`, which is unresolved). STRAP-1 forbade
parentheses, so scope the change to what the project targets.

*Status 2026-11-16: DONE; `**` read as a numeric DD's operator, one page against.* The target, the host
STRAP II (`strap/strap2`), already parsed `*`, `/` and arithmetic
parentheses (`getfld.py`) and evaluated them (`value.py`). Only
strap_asm refused them. It now takes them on a separate path
(`_arith_bi`), reached only by a field with `*`, `/` or a non-radix
parenthesis. That path copies `value.py`'s arithmetic, which is CHOSEN
there because no page gives `*` or `/` on a bit address. **Appendix C cannot code
`**`.** Printed p.107 (MQDNUM) lists it among "the current
arithmetic operations which may be specified on a numeric DD":
"Third order operations **(powering)", with "the exponent ... an
integer in the range 2^-18 < n < 2^+18". A numeric DD is evaluated at
once to a floating word and never coded, so Appendix C needs no code
for it. `dnum.py` has it. In an address field both assemblers refuse
it. **One page reads the other way, and this is not settled.** The
glossary, printed p.204, says: "Priority of Operations -- When
arithmetic operations are specified in an instruction field, there is
a definite order by which they are combined ... 1st order operation +
and -. 2nd order operation * and /. 3rd order operation **." Its
"orders" are p.107's words for MQDNUM, and p.207 calls a numeric DD's
operands its "'address' field". So it is read here as the numeric
DD's. C28-6129 names no `**` anywhere. Its "Address Arithmetic"
(printed p.31, PDF p.35, OCR) offers "addition, subtraction,
multiplication and division". Its numeric DD (printed pp.27-28, OCR)
lists "addition (+), subtraction (-), multiplication (*) and division
(/)". So C28-6129 does not settle where `**` belongs. A printed listing
with `**` outside a DD would overturn this reading. Printed p.207 adds that "Implied multiplication is not allowed in
field arithmetic". Three decks strap_asm refused now assemble to
strap2's image: `repro_address_multiply` (0007C70F 00083000) and the
two Problem 4.6 Method 3 decks. No deck that assembled before changed
(hashed). Checks: `tests/check_field_arithmetic.py` (38 checks, five
injections); `check_problem_4_dd_refusals.py` now asserts the word.
strap_asm's DD(N) arithmetic (`1/720`, `$N`) is refused, as before.

*Follow-up 2026-11-17: SYN, CW, transmit's J and `(N+1)` alone.*
strap_asm refused `Q SYN, N*2`, `CW, SAM*2, N*2` and `T, N/4, ...`, and
read `(N+1)` alone as an index on a null address. strap2 takes all
four, and strap_asm now agrees with it on each.

- **A SYN keeps its two parts.** This is DERIVED. Printed p.13 says the
  vle holds "its value or the coded expression of the value". Chart RD
  (p.54) puts a symbol's info, or the VALUE of its expression, in the
  list. p.57's workspace data are "I-value and B-value". p.59 Box 6
  combines the two only "if the result is ... to be made an integer,
  i.e., Vvint". INSERT adds them by function (p.144). Fig. 22 (p.191)
  does not tabulate the function, so where the parts are stored is not
  printed.
- **strap_asm classifies by the computed parts.** No bit part is an
  integer (`N*2`, `SAM/1.0`). No integer part is a bit address. Both is
  mixed, kept in `SymTab.sym_ipart`.
- **The mixed case was wrong without arithmetic too.** `QM SYN, SAM+N`
  then `B, QM` gave 800 half words; strap2 gives 808.
- **CW (SCW, S18CF, S18RF) and the register fields (J's STJFLD, LV's)**
  take `(B >> 6) + I`, as strap2's inserters do. An index takes
  strap2's S/X rule (the bit part's word, otherwise the integer part). `CW, SAM+1` gave word 400;
  strap2 gives 401.
- **`(N+1)` alone.** Printed p.85, Boxes 43, 44 and 49: "If there was no
  operator to make the parentheses arithmetic, the coded expression is
  set to indicate a sub-expression". strap_asm now treats an operator
  inside (including a unary minus or a point) as making it arithmetic.
  This is CHOSEN, as in strap2, because Box 76 draws no test. `($1)`
  stays an index (MCP printed p.126).

All 825 decks hash the same under both assemblers before and after.
`check_field_arithmetic.py` is at 113 checks, with eleven injections
measured.

**G3.2** Replace `eval_addr_field`'s per-call-site `unit_shift` with
printed p.144's rule -- scaling by the operand's **function** -- and
test it against the listing oracle.

*Status 2026-11-16: DONE.* `strap_asm.eval_addr_field` takes the
address's function by p.144's INSERT routine name (`ADDRESS_FUNCTION`:
a field shift and a function shift each), and every call site names
its routine. The host already had this rule in `pass2.py`'s inserters.
**Both assemblers broke p.144's own example.** The page says "To fill
the addresses in the instruction TI, 7, SAM + 10, PAT + 10, the routine
adds 10 full words to both addresses". strap_asm added 10 bits to A1
and 10 half words to A2. strap2's `STTI`/`STT19A` did the same. Both
now add words. C28-6129 printed p.4 writes the format `OP, J, A18(I),
A'18(I')`. Its printed p.33 (PDF p.37) says "An integer in an 18-bit
field counts full words", which is a second manual's rule agreeing with
p.144. No listing row in the corpus writes an integer in a transmit
address. The listing oracle does pin LX/SX's function:
`verify_ibox4_refill_listing.py` fails on "SX, $X0, 8" if `S18X` is
set to the field's units. strap_asm also left an integer
`SYN` symbol unscaled in LX/SX, where strap2 counted words; it now
counts words too. Every deck's image is unchanged under both assemblers
(hashed before and after). `tests/check_address_function.py` (27
checks) records its injections. **Open:** `SSIC24`, `S24CW` and
`S1918A`. p.144 says only "error-flagged if more than 19 [18] bits are
specified". That suggests a function the page does not state, and the
error flag is not implemented.

**G3.3** The numbered error-message list (printed p.177) is a rule book
with a column `C28-6129` lacks; it fences `(.n)` behaviour with six
specific errors.

*Status 2026-11-16: DONE for the six, in the host STRAP II.* The six
are 65 (MQDD), 68, 82 and 108 (GETFLD), and 94 and 95 (DECODE). They
are on printed pp.177-178, whose column is the logic area. The page
gives the number, area and text but not the condition, so each
condition has its own source:
- **65:** printed p.100 Boxes 27-29, "another radix at this point would
  be an error".
- **78:** the message's own words (a zero divisor, ignored).
- **82:** DERIVED. The message gives the action, not the condition. It
  is given here for every `(.0)` g.p.
- **95:** C28-6129 printed p.25's complement rule.
- **108:** printed p.204's "SYN, DR, DDI, and DRZ cannot have a gp".
- **68:** DERIVED. Appendix C's 6-bit n gives n > 63; before, that n
  was silently coded modulo 64.
- **94:** DERIVED. The two refusals were already there, unnumbered.

Added: 65 (it was 67), 68 for n > 63, the notes 82, 95 and 78, and 94.
`tests/check_strap2_gp_messages.py` has 29 checks. Its expected text is
typed from the page, not imported from `errtab`. Seven injections were
measured. No deck's image changed. The other messages on the list were
sorted by a grep of `strap/strap2` for each number on p.177 (46-95).
Given: 47-50, 54-56, 59, 61, 63, 65-68, 75-79, 82, 84, 85, 87, 88, 91,
94, 95. Not given: 46, 51-53, 57, 58, 60, 62, 64, 69-74, 80, 81, 83, 86,
89, 90, 92, 93. Message 71 (SUBSCRIPT WRITTEN AS BIT) is detected but
refused unnumbered (`value.py`), as 94 was. The open items, among them 68's own stated condition, are in
`docs/NEXT.md`, "ASSEMBLER COMPLETENESS (G3)".
*2026-11-17:* the 7030 deck's GETFLD now gives the same two g.p.
messages. Before, measured on the model, it coded `A(.70)1` with n = 6
and gave `A(.0)5` no note. Now it halts with ERRC 168 for n > 63 and
notes 82 for n = 0. The four new cases are in
`check_strap2_7030_getfld.py`, and `docs/strap2_7030.md` describes the
change.

## G4 — Verification infrastructure

**G4.1 Write the atlas oracle.** `run_tests.sh:3057` has said Perf.
Char. Vol. 2's per-instruction atlas is the real timing oracle and that
`perf_char_timing.py` is "shaped for" it. **M2's correctness is defined
as how much of that residual it closes**.

*Status 2026-11-16: written, first measurement taken, transcription complete.* The oracle is in
`docs/atlas_oracle.md`. **All 139 atlas pages are transcribed**
(`tests/perf_char_vol2_atlas.txt`, 28,272 times; the fast self-check
`tests/check_atlas_data.py` is in `run_tests.sh`). The 60 floating-point
pages, PDF 42-101, came with two cross-check rules: forwarding twins and
the PDF 104 FP quotations. The last 46 pages also came on 2026-11-16:
VFL with forwarding, PDF 143-169, and VFL immediate, PDF 171-189. With
them came five more rules: `vfwd`, `vfwdib`, `index`, `immf` and `immn`.
PDF 114 says the I-box operand should not change with forwarding;
`vfwdib` finds 2,007 exact pairs and 94 near of 2,148. Eight cells are
uncertain, each with a NOTE. `tests/atlas_oracle.py` ran 6,265 cases
in about an hour; with the new pages `--list` reports 12,353 cases with
a generator (run time unmeasured). Its residual predates PDF 143-189: mean −18.9 clocks,
median −7.1, 7% exact. The largest single cause is that the model's VFL
time does not depend on the operation. FP residuals were then
unmeasured: the oracle had no FP generator.

*Status 2026-11-17: all but 989 transcribed cells now have a
generator, and each new generator has been measured on its own pages.*
`tests/atlas_oracle.py` gained generators for the VFL INTERNL columns,
the floating-point pages (PDF 42-101), the VFL immediate pages (PDF
171-189) and CV/DCV, each built from the volume's own method pages (PDF
40-41, 113-115, quoted in `docs/atlas_oracle.md`), with the facts the
volume does not print marked CHOSEN. `--list` now reports 27,655 cases
with a generator and 989 without; `--selftest` has eight checks, four
new, each proven discriminating by injection. Measured (residual =
model − printed, clocks):
- FP, 9,406 cases: 5% exact, median −1.02, mean −3.10. Fetch from
  memory at half the 7030's rate; I-box and to-memory stores 10-25 too
  cheap; $R operands short; divide short; SHF has no amount term.
- VFL INTERNL, 3,908: 3% exact, median −7.10. The model charges an
  accumulator operand as an external one; the 7030 adds about 4 clocks
  (10 with crossover).
- VFL IMMED., 1,604: 41% exact, median −0.00. Immediate compares and
  `/I` (a data effect) are long.
- CV/DCV, 384: within 0.2 clocks, but fitted to these pages, so not
  independent.
Remaining:
- the open items for the model listed in that doc's "What remains";
- generators for NONCON/CBR, internal transmit operands, PDF 110, the
  I-box refill rows and PDF 104 (989 cells), each needing a fact the
  pages do not print;
- one full run of all 27,655 cases (the generators were run page-set by
  page-set), and a `--sample` mode short enough for M2's inner loop.

**G4.2 Keep the probe guard honest.** `verify_no_probes.py` caught three
real accidents in one day; add a check for anything else that looks
like instrumentation as it is invented.

## G5 — The render and mine queue, in priority order

1. `-1` **pp.99-100** -- Figures 49-50, the IPL flowchart (A1-A3)
2. `-1` **p.72** -- Assign's configuration change (is the phantom real?)
3. MCP listing **p.41 line 37** -- confirm `Y UCBF1+.372` (OCR reads `.2372`)
4. 7101 **pp.225-243** -- PAU/SAU per-cycle charts (G1/M1)
5. 7101 **pp.273-279** -- §4 Procedure 1, memory timing (G1/M3)
6. 7101 **pp.95, 99-119** -- the LA flow diagrams (G1/M2)
7. `-1` **pp.73-78** -- Assign charts; the reject logic is only here
8. `C22-6729` **pp.197-204** -- Appendices C and E, the grammar (G3)
9. Buchholz **A.2-A.5 and Appendix B** -- the independent cross-check
10. `-1` **p.261** / base **p.246** -- `SEQUIP`'s 4-bit codes against p.68's

## What stays out, and why

**The FPGA and the SD-card disk.** The arithmetic is encouraging -- an
emulated 2.1 µs memory cycle is ~52 clocks at 25 MHz, a 353 arc is
exactly eight SD blocks, and putting the disk in SDRAM moves
flash-translation pauses off the critical path. **None of it is
reachable until MCP boots**, and starting it now trades a near goal for
a distant one.

---

# PHASE A PROGRESS

## A1 is DONE: MCP reads a real IOD card -- 2026-10-28

The column map came from `C22-6678-1` printed pp.7-10, **verified in the
OCR rather than derived**: `1` = B, `2-9` = IODNAME, `10-62` =
statement, `63-66` = I/O reference number (four octal digits), `67-72` =
absolute exit (six octal digits), `73-80` = program id. The manual's
own words settle why the fixture must punch 63-72: those columns are
*"left blank by the problem program"* and filled by STRAP II, and the
cards MCP reads at IPL are the compiler's **output** cards.

MCP's answer walked forward through three states, which is the useful
part:

| fixture | MCP's answer |
|---|---|
| blank IOD (statement empty) | X ERR 24, "IO ASSIGNMENTS CANNOT BE MADE" -- phantom request on DISK |
| `IOD,READER,XRDEXIT`, comma punched 4-8 | **X ERR 22, "INCORRECT CARD TYPE WITHIN IODS"** |
| same, separator punched 0-3-8 | **decodes; READER's request count = 1** |

### >>> THE SUBFIELD SEPARATOR IS PUNCHED 0-3-8, NOT 4-8 <<<

`strap/cards.py`'s table, from `C22-6678` Appendix F, gives comma = 4-8
and quote = 0-3-8 -- and **already flags these two** as "precisely the
slots where the conventional commercial code and the 7030's
48-character set disagree". Measured two independent ways against MCP's
own SCA6 and SBRK8:

* **Behaviourally.** With 4-8 the first broken-out field came back as
  `'IOD-READ'` -- eight characters, the separator rendered as a dash,
  the field never broken, SBRK8's eight-character limit exceeded, and
  Uncode's error return taken. With 0-3-8: `'IOD'`, `'READER'`,
  `'XRDEXIT'`, three fields, exactly as a comma should do.
* **Bit-exactly.** SCA6's output words match the card computed as a
  continuous six-bit stream **only** when the separator maps to the
  A-set **comma** code 27. With the quote's code 12, word 1 does not
  match.

`cards.py` is deliberately **not** changed:
`tests/verify_c22_6678_appendix_f.py` pins it to the manual and the
manual still says what it says. Which of the three is wrong -- our
reading of Appendix F, Appendix F itself, or SCA6's table sitting a
keypunch convention away from it -- is **open**, and Appendix F is on
the render queue.

### A method note worth keeping

The two card-buffer checks were hardcoded hex against a blank-statement
card. They now **derive from the card text** (`_sca6_word()`), which
turns them into a test *of* SCA6's conversion rather than a recording of
one run, and makes them proof against drift when the card changes.
**Re-recording a magic number is the lazy fix; deriving it is the
cheap one, and it was cheap here.** Establishing it also settled the
packing: SCA6 writes a continuous six-bit stream, so word 0's low four
bits carry the top of character eleven.

## What A1 did NOT fix, and what that leaves

`T IOREQ` is still empty and READER's `MACH CONF` count is still zero,
so `TCHEK` will still reject. Two things remain, and they are A2 and
the render:

* **A2**: printed p.98's minimal case needs IOD cards for **a card
  reader AND output tape units**. Only the reader exists.
* **The render**: `-1` printed p.72, Assign's configuration-change
  section, which says "the equipment count is generated for the
  validity check table". If that is where the conf counts come from,
  the question is why it generates none -- and that is a different
  question from the one A1 answered.

## THE RENDER OF `-1` PRINTED p.72, AND WHAT IT SETTLES -- 2026-10-28

Queue item 2, rendered from the PDF rather than read out of OCR. Three
things it gives, all verbatim.

### 1. ASSIGN's linkage, which independently confirms a derivation

```
     LVI, $15, Y
     B, TASIGN
Y    XW, A, B, C
     (Return)
```

> **A** is the status of the machine: `0` -- no configuration change has
> taken place; `≠0` -- configuration change has taken place.
> **B** is the exit disposition: `0` -- next PP has been assigned
> successfully and is ready for Move; `≠0` -- next PP has been rejected
> and cannot be given to Move.
> **C** is the Assign entry mode: `0` -- overlapped mode; `≠0` --
> unoverlapped mode.

printed p.27's caller is `X242 XW, -1, 0, 0, 4`, so **A = -1**:
*configuration change has taken place*. That is the same conclusion
`75be218` reached from the other end -- by decoding the index word's
`addr`/`sign`/`flag` bits and the `BZXVZ` branch sense -- and the two
derivations never touched each other. **B is the disposition bit** the
project already tracks through printed p.80 line 25.

**And C = 0 means OVERLAPPED**, while the fixture's MCPP card says
`BYPASS`, which printed p.98 calls unoverlapped. That is not
necessarily a contradiction -- C comes from MCP's own caller, not from
the card -- but it is the first place the two could disagree and is
worth a line in the plan.

### 2. The configuration-change section's three functions, verbatim

> 1. All requests reserving units that have become unavailable due to a
>    machine configuration change must be relieved of these units. At
>    the same time these relieved requests must be marked so that they
>    have priority in re-assignment (pseudo-unoverlapped).
> 2. **The equipment count is generated for the validity check table.
>    This table contains the equipment code and count and a zero field
>    for the requested count for a PP.**
> 3. The multi-unit count table is generated. This gives the total
>    number of tapes on a channel. The format of the table is half-word:
>    `.0-.17` the channel number and `.18-.21` the unit count. Along
>    with this, the largest count per channel is stored for PP request
>    checking.

**Function 2 settles the open question.** printed p.64's table is the
validity check table, its three bytes are "the equipment code and
count and a zero field for the requested count", and the count **is
supposed to be generated** by this section. So the conf bytes coming
out of the boot as zero is a **defect**, not documented behaviour --
which is what the plan needed to know before spending anything on it.

**Function 3 gives a layout the project did not have**: the multi-unit
count table is half-words of `channel .0-.17` and `unit count .18-.21`.
`T CHCUC` is at `003661` = word 1969, and nothing has looked at it.

### 3. What it does NOT give, stated so nobody looks again

It does not say how the count is generated, only that it is. The code
is printed p.72 lines 16-30 of the listing, already transcribed, and
two hypotheses about it have now been refuted before being asserted:
the `code*24 - 16` arithmetic is correct (five decks), and lines 23/25/26
all take offset 0 in the source, so the `LI(BU,1),1` feeding `M+` is not
an offset mismatch. **The next step is to watch `T EQUIP` as `TA9A`
reads it**, which the step-cap bisection can do without instrumenting
the model.

## THE CONF COUNT: SIX DECKS GREEN, AND THE WINDOW IS 100,000 STEPS -- 2026-10-28

`-1` printed p.72, rendered, says the equipment count "is generated for
the validity check table", so the boot leaving every conf byte at zero
is a defect. Four hypotheses have now been tested and **all four are
refuted**, each before it was asserted:

| hypothesis | how it died |
|---|---|
| the `code*24 - 16` arithmetic is wrong | `mcp_p72_conf_offset.strap`, green |
| lines 23/25/26 have mismatched offsets | the SOURCE carries no offset operand on any of the three, so all are offset 0 |
| the loop does not reach the equipped channels | `T CHSXW` carries **count 36** and `TB9B CB+, TIXF, TA9A` advances one word, covering words 2814-2849 -- channels 0 and 32-35 are all inside it |
| **`TA9` runs before the channel status table is built** | **the bisection below** |

### The new deck

`decks/mcp_p72_conf_add.strap` carries the same sequence three
instructions further -- through `LI(BU,1),1` and
`M+, T DISK(T IXG)` -- and checks the **conf byte**. It passes: row 0's
conf byte goes `0x20` to `0x21`, the other twenty-three do not move.
**Six decks over p.72's two loops, all green.**

### The bisection, non-perturbing as before

| steps | `T CHSXW` | CST 2814 / 2846 | conf table |
|---|---|---|---|
| 4,000,000 | `0xa00000` (partial) | 0 / 0 | static |
| 6,000,000 | **0** | 0 / 0 | static |
| **6,100,000** | word 2814 | **built, TEQUIP 1 / 3** | **still static** |
| 6,200,000 | word 2814 | built | **cleared** |

> **SO THE CHANNEL STATUS TABLE IS FULLY BUILT BEFORE `TA9`'s CLEAR
> RUNS**, and the hypothesis that `TA9` reads an empty table is dead.
> When the loop runs it has correct data, a correct count, a correct
> stride, and a sequence proven correct in isolation -- and adds
> nothing.

**That is the same shape as the look-ahead bug** (`a2b210e`): right in a
deck, wrong in the boot. The window is now **6,100,000 to 6,200,000**,
one hundred thousand steps, which is where to instrument -- **narrow
first, instrument second**, and log the LEVEL's `pc`, not `pcReg`.

### A fifth hypothesis, refuted, and the window narrows to 30,000 steps

`S YCOCH` looked like a free witness for whether `TA9A`'s body reaches
line 26: printed p.72 line 42 writes it (`SF(BU,17), S YCOCH+.2, 46`),
and line 42 is *after* line 26, so finding it written inside the window
would prove the add executed. Measured:

| steps | `S YCOCH` (word 1134) | conf table |
|---|---|---|
| 6,000,000 | 0 | static |
| **6,120,000** | **35** | **still static** |
| 6,150,000 | 35 | cleared |

**It is written BEFORE the conf clear.** p.72's clear loop (lines 10-12)
runs *before* the per-channel loop that contains line 42, so if line 42
had written it the order would be the other way round. `S YCOCH` is
populated earlier -- by the communication-region move, which
`docs/boot_plan.md` already records -- and **is not a witness for line
26.** Hypothesis five, refuted.

> **What it buys instead is a tighter window.** The conf clear now sits
> between **6,120,000 and 6,150,000 steps** -- thirty thousand, down
> from a hundred thousand -- and that is small enough that a log of
> every store in it will be readable.

**The next instrument, specified so it is not got wrong a second time:**
log at the **generation** site of the store (`StretchExecute`'s VflInt
`M+` arm), printing the LEVEL's `pc` rather than `pcReg`, guarded on the
conf table's address range, and check the run's final table against the
bisection numbers above to prove the trace describes the same
execution. All three of those rules were bought with retractions
earlier in this work.

## >>> THE CONF COUNT: BOTH INDEX REGISTERS ARE ZERO, AND IT IS 2^18 WRITES TO WORD 0 <<< 2026-10-28

Instrumented inside the window, to the specification written before
starting: at the store's **generation** site, with the final table
checked against the bisection to prove the trace describes the same
execution.

### The chain, measured

**1. `M+` never adds a conf count.** Logging every `M+` store that
targets words 1962-1964 over the whole boot gives **three** hits:

```
MPLUS word 1963 off  0 len 8    flat byte  8 = READER's REQUEST count
MPLUS word 1964 off 56 len 8    flat byte 23 = TAPE's REQUEST count
MPLUS word 1964 off 56 len 8    TAPE again, 0 -> 1 -> 2
```

All three are printed p.66 line 3's `M+1, T RCAD`. **printed p.72 line
26's conf add never fires.** (The instrument was proved able to fire
first -- unguarded it logs 60 stores before the window closes -- so the
negative is evidence rather than silence.)

**2. `TA9A`'s body IS entered, and writes the wrong place.** Filtering
every four-bit `CM` write -- `T CHCNT` is `SYN(BU,4), 0.20`, so length
four is line 16's signature:

```
262144  word 0  off 20  len 4
```

**2^18 writes to word 0.** `262144 = 2^18` is the Reference Manual's
own "a count field of zero is interpreted as 2^18", and offset 20 with
length 4 is `T CHCNT` exactly.

**3. Both index registers are zero while their source words are
right.** Index registers X0-X15 live at words 16-31, so `TIXH` = `$2`
is word 18 and `TIXF` = `$10` is word 26. Probed mid-loop at 6,500,000
steps:

| | value | count | refill |
|---|---|---|---|
| `$2` (`T IXH`) | **0** | **0** | **0** |
| `$10` (`T IXF`) | **0** | **0** | **0** |
| `T MUCTX` word 1965 | `0x01ec400000000000` -- correct | | |
| `T CHSXW` word 1130 | `0x02bf800000900000` -- correct | | |

printed p.72 line 4 is `LX, T IXF, T CHSXW` and line 15 is
`LX, T IXH, T MUCTX`. **Both load from correct, non-zero words, and
both registers end up entirely zero.** That accounts for every symptom:
`T IXF`'s count of zero gives 2^18 iterations, `T IXH`'s value of zero
puts every write on word 0, and `T EQUIP(T IXF)` reads word 0 -- zero
-- so line 18's `BRZ` skips the add on all 262,144 passes.

### The mechanism this points at, labelled as a hypothesis

**Zero in value, count AND refill is the signature of being
OVERWRITTEN, not of a failed load.** `StretchCore.bsv:154` declares
`xSnap <- mkReg(replicate(0))` -- sixteen zero index words -- and line
523, in `rl_recover`, does `st.restoreIndex(xSnap)`. A restore that
runs with `xSnap` still at its reset value, or with a snapshot older
than the `LX`, writes exactly what is measured.

`rl_recover` fires only on a wrong branch guess, and the snapshot is
taken at the guess (`StretchCore.bsv:1332`), so the pair looks correct
on its face. **What is not established is whether a branch level can
survive a `cancelAll()` and recover against a stale snapshot** -- which
is the same subsystem, and the same shape, as the look-ahead bug fixed
in `a2b210e`.

**NOT A CONCLUSION.** It is the first hypothesis of this investigation
that has not yet been tested, and six have died already. The test is to
log `xSnap`'s contents and the `branchSeq` at `rl_recover`, in the same
window, with the same provenance check.

### The xSnap hypothesis is refuted, and so is one of my own refutations

**`rl_recover` is not the culprit.** Logging `xSnap` and the live
registers at `StretchCore.bsv:523` over 6,318 firings: in every case
where a live register was non-zero, **the snapshot matched it exactly**
(`xSnap[10]` = `live[10]` = `0x0025400002540000`). The restore puts
back what was there. Seventh hypothesis, refuted.

**And it exposed that an earlier refutation of mine was too coarse.**
"`TA9` runs before the channel status table is built" was dismissed by
comparing the CST build against the **clear** (p.72 lines 9-12). But
`LX, T IXF, T CHSXW` is **line 4**, earlier than the clear, so that
comparison never tested the thing it was taken to test.

### >>> A DATASET THAT WAS GARBAGE, AND THE TREE IS WHAT SAID SO <<<

The re-run bisection produced four identical rows. `git status` showed
why: a leftover `step_cap=6500000` in the testbench meant the bracket
script's `replace("step_cap=40000000,", ...)` **never matched**, so
every run used the same cap regardless of its `N`.

**The script had no assertion that the substitution happened** -- the
same hole as the probe that silently never applied earlier today, and
the fix is the same one: it now asserts the canonical cap is present
before substituting. Four rows of plausible, identical, meaningless
numbers is exactly what this project's memory file calls "two facts
from one run that cannot both be true", and the only reason it was
caught is that deterministic runs are not supposed to disagree with
earlier ones.

### What the corrected bisection actually shows

| steps | `T CHSXW` (1130) | `$10` = `T IXF` (word 26) | conf table |
|---|---|---|---|
| 6,000,000 | **0** | `0x0025400002540000` | static |
| 6,040,000 | correct | **`0x02c7c00000100000`** -> word **2847** | static |
| 6,110,000 | correct | word 2847 | static |

**`$10` is not permanently zero.** At 6,040,000 it holds a valid
pointer into the channel status table -- word 2847 is channel 33, the
printer -- so the index machinery works and `LX` loads. The conf table
is still static at 6,110,000, so `TA9`'s clear has not run yet.

> **SO THE QUESTION NARROWS AGAIN: what zeroes `T IXF` between its load
> at p.72 line 4 and `TA9A`'s loop?** Both registers are entirely zero
> during the 2^18 passes, and both were fine shortly before. That is
> the next measurement, and it is a bisection between 6,110,000 and
> 6,500,000 on word 26 alone.

**Seven hypotheses tested, seven refuted.** Every one of them died to a
measurement rather than an argument, and two of the seven were my own
earlier refutations being re-examined.

## Refutation log, continued: naming the writer that zeroes `$10`

Method: one instrumented build per question, every diagnostic
cycle-stamped from a single free-running counter in `StretchStorage` so
all events share one timeline (the provenance rule). Two builds --
`ixw5` without the counter, `ixw6` with it -- agree on 12 special-path
writes to word 26, 3 of them zeroing a live `$10`, with identical
`was` values, so `rl_dbg_cyc` did not manufacture the effect.

**The complete ordered census settled what six hypotheses could not.**
Every write to `xreg[10]` from all three paths (`writeIndex`,
the special-address store path, `restoreIndex`) in one run, 491 events:
the last event leaving `$10` non-zero is index 227, and the kill is

    [6122846] Z arm        -> 0          (was 0x0175800000180578)
    [6122869] writeIndex   -> 0x01d3000000000000
    [6123192] SWAP hw 3391 -> 0x02c7c00000100000   (x.dst == 26)
    [6123422] SWAP hw 3970 -> 0                    (x.src == 26)
    [6124063+] restoreIndex every 61 cycles to the cap

### H9 REFUTED: the read side is correct

`readWordResp` (storage printed line 787) *does* apply `lookupSpecial`,
so Transmit/Swap reads word 26 as `xreg[10]` and not as raw core. The
hypothesis that a swap filled the save area with zeros because its read
bypassed the special-register alias is dead.

### H10 REFUTED: the swap phase machine is never stale

`xmitSwapPhase` and `xmitReadIssued` are reset at neither of the three
`xmitPending <= o.xmitStart` sites (`StretchCore` 303, 1103, 1149), so a
swap abandoned mid-flight could in principle leave phase at 2 and make
the next swap write a stale `xmitSwapHeld` with no read at all. An
instrument at all three start sites fired **zero** times in the whole
boot. The latent fragility is real and worth closing, but it is not
this bug.

### H11 REFUTED: the `Z` (clear) arm is behaving correctly

Both groups of `Z` instructions that clear a word in 16..31 were given
full address provenance (`bm.addr`, `bm.idx`, the index value and sign):

* **Group 1 -- `bmidx=15`, index value stepping 0x40 (one word) --
  clears `zw=16..30` and STOPS BEFORE WORD 31.** This is the listing's
  "CLEAR LOWER REGISTERS" loop (printed p.2, under the banner "CLEAR
  7030 LOWER REGISTERS AND STORAGE"), and stopping one short of word 31
  is exactly right: word 31 is `$15`, the loop's own counter. The model
  reproduces this correctly.
* **Group 2 -- `zw=26, bm.addr=0x34, bm.idx=0`, unindexed.** 0x34 = 52
  half-words; 52*32 = 1664 bits; 1664/64 = word 26. A deliberate,
  constant-address Store Zero to `$10`. A second one clears word 19
  (`$3`) from `bm.addr=0x26`. MCP clears these index registers on
  purpose.

So the Z arm is not the defect, and neither clear is a units error.

### What the 8 bouncing writes were: ordinary context switching

`SWAP` at half-word 3391 (8 words) and half-word 3006 (8 words)
alternate, exchanging `$10` between `0x02c7c00000100000` and
`0x0175800000180578` four times each. That is MCP saving and restoring
a context, and it is correct behaviour, not corruption. The kill is a
*different* swap -- half-word 3970, 12 words -- whose partner word read
zero.

> **THE DEFECT HAS MOVED UPSTREAM AND CHANGED SHAPE.** It is no longer
> "something zeroes `$10`". Every writer is now named and each one is
> doing what the listing tells it to. The live question is why the
> 12-word save area that SWAP 3970 exchanges into words around 26 is
> zero.

### A downstream consequence, recorded and NOT to be chased yet

After the kill the machine runs `rl_recover` every 61 cycles until the
step cap -- 417 wrong-way branch recoveries. `rl_recover` clears
`recover` itself, so it is being re-armed each time at `StretchCore`
1142: the I-box mispredicts the same branch forever. That is a livelock
in MCP's own code, consistent with a count-controlled loop whose count
is zero, and it is a *consequence* of the kill rather than a second
model bug.

### Settled in passing: the `effAddr18`/`effAddr19` units bug was REAL and IS FIXED

They live in `StretchExecute.bsv` (435-492), not `StretchTypes.bsv`,
which is why a search for them in the latter comes back empty. The
comment there records the bug in its own words -- the two helpers
"previously added the value STRAIGHT to a word or half-word address,
which is wrong by 64x and 32x respectively" -- and the present code
converts to the 24-bit bit-address domain first (`{raw,6'b0}`,
`{raw,5'b0}`), adds the index value unscaled, and then takes only the
applicable part (`[23:6]`, `[23:5]`). That matches Reference Manual
printed pp.20-21: "the missing low-order bits, if any, are always
assumed to be zero" and "only the applicable part of the effective
address is used", corroborated by printed p.41's index-increment table
equating "H add half to value" with bit position 18 and "+ add one to
value" with bit position 17 -- weights 2**5 and 2**6 over a value field
of bits 0-23. `effAddr24` needed no change because its instruction
address is already a bit address.

### H12 REFUTED, and the model comes out correct: the recovery loop is legitimate

The 417 wrong-way recoveries at a fixed 61-cycle period were labelled a
consequence without being measured, so the label was checked.

`StretchCore:1136` guesses **unconditionally not taken** --

    Bool taken = (o.next != h.pc + ((h.len == Full) ? 2 : 1));
    if (taken) begin la.cancelAll(); recover <= tagged Valid o.next; end

-- so every taken branch costs one recovery, and 417 recoveries at an
exact 61-cycle period is 417 iterations of a 61-cycle loop whose
back-edge is taken. The guess direction is sourced: Buchholz PDF 263,
design decision 4, *"the instruction unit proceeds as if the branch will
fail"*, with TR00.722 PDF 30 recording that the study "did not clearly
indicate an advantage either way".

**The promising version of the defect was that the model guesses a
branch the real machine never guessed.** Perf Char PDF 41 is explicit:
*"The following branches, however, involve conditions known to the
I-box and are executed entirely within the I-box: CB and variants;
B ind for XF, XVLZ, XVZ, XVGZ, XCZ, XL, XE, XH."* MCP's loops close
with `CB+`, `CBR+` and `C3`, so if the model guessed those, recovery's
`st.restoreIndex(xSnap)` would undo the CB's own count decrement and a
counting loop would never terminate -- which is exactly what a fixed
61-cycle recovery period looks like.

**It does not.** The guess site (`StretchCore` 1321-1336) is guarded

    di matches tagged BranchInd .bi &&& !indexIndicator(bi.indNum)

so the eight index indicators are excluded by name, and CB-family is
not `BranchInd` at all -- it falls through to the I-box-class arm and
executes in the I-box without a level or a guess. Both exclusions in
Perf Char PDF 41 are faithfully implemented.

So the spinning loop closes on a genuine arithmetic-indicator branch
that is taken every iteration, and paying one recovery per iteration is
correct behaviour -- the case Buchholz names as the guess's known
weakness, *"an unusual situation in a problem with a very high
probability that the branch will always be taken"*.

> **>>> THE PATH IS EXHAUSTED, AND THAT IS THE RESULT. <<<** Twelve
> hypotheses, every writer of `$10` named, every one of them doing what
> the listing tells it to, and the recovery loop sourced as correct.
> The conf counts are not zero because something corrupts them. **They
> are zero because the boot never reaches the point that fills them**
> -- it is spinning in an MCP loop at step ~6.12M. That reframes the
> question from "what is the model corrupting?" to "what is MCP waiting
> for?", which is a question about the boot's progress and is answered
> by the PC of the spinning loop, not by another writer hunt.

**Method note worth keeping.** The eleven refutations before this one
each pushed the question one frame upstream -- conf table, then `$10`,
then which writer, then why the save area. That regress is the tell
that the symptom's cause is not where the digging is. The cheap
check that broke it was reading the guess classification against a
sourced list instead of instrumenting a thirteenth time.

### >>> A CONFOUND IN THE SECTION ABOVE, FOUND BY PRE-REGISTERING THE NEXT RUN <<<

The claim "the boot is spinning in an MCP loop at step ~6.12M", written
two commits ago and used to justify Phase A4, rests on runs whose
`step_cap` was **6,140,000** -- a reduction I made to keep the
instrumented logs small. The canonical cap is **40,000,000**.

**The tail of every one of those runs is at the cap by construction.**
So "it is still issuing wrong-way recoveries when the log ends" is not
evidence of a hang. It is evidence that the log ended. This is the same
error as "a step count dropping from 22M to 6M means it ran faster"
(recorded in the working-method notes: it halted) wearing different
clothes -- a number that comes from the harness being read as a number
that comes from the machine.

**What survives the confound.** The 61-cycle period is real and
measured across ~16,000 cycles, so there IS a tight loop. What does not
survive is "spinning" in the sense of *forever*.

**And the arithmetic points the other way.** `TA9A` was measured
earlier running **262,144 = 2^18** times. At 61 cycles an iteration
that is ~16.0M cycles, which on top of the ~6.1M already elapsed is
~22M -- and the boot's known full length is **22,048,336 steps**. So
the loop is very likely FINITE and simply truncated by the reduced cap.

**2^18 is also exactly the width of the index count field** (IBM bits
28-45). A count-controlled loop entered with its count at ZERO
decrements, wraps, and runs 2^18 times. That is the signature of this
loop, and it reconnects the count question to the symptom without
needing anything to be corrupted after the fact.

> **THE OPEN QUESTION IS THEREFORE NOT "WHERE IS IT STUCK" BUT "WHY IS
> A LOOP COUNT ZERO WHEN THE LOOP IS ENTERED".** A4's instrument is
> still the right one -- it names the loop -- but outcome (d) of its
> pre-registration (`$S/prereg_a4.md`) is live, and the first thing to
> read off the next full-cap suite run is the boot's own step count.

### CONFOUND RESOLVED: outcome (d). The loop is finite, and the project had already measured it.

`tests/gen_mcp_boot_tb.py:942`, written long before this session, says
of the stretch of boot that reaches `T A9`'s code: **"the run is 16
MILLION STEPS longer"**. That is the number, independently recorded:

    ~6.1M steps   to reach the loop
    ~16.0M steps  in it            (2^18 iterations x 61 cycles = 15,990,784)
    ~22.0M total  against a known full boot of 22,048,336 steps

So the loop **terminates**, the boot completes, and the MCP bootstrap
section of the suite passes at the canonical 40,000,000 cap. The
"spinning in an MCP loop" framing was an artifact of the 6,140,000 cap
I set for log size, exactly as pre-registered outcome (d) said it might
be. **Phase A4 as originally written is withdrawn.**

> **>>> WHAT IS LEFT IS A BETTER QUESTION THAN THE ONE I STARTED WITH.
> <<<** A loop runs **262,144** times and eats **16 of the boot's 22
> million steps** -- roughly three quarters of the entire bootstrap.
> 2^18 is exactly the width of the index count field (IBM bits 28-45),
> so this is a count-controlled loop entered with its count at ZERO,
> which decrements, wraps, and runs the field's full range. MCP does
> not intend that. **The defect is not that a count gets zeroed after
> the fact; it is that the loop is ENTERED with count zero.**

That is a sharp, falsifiable question with a cheap instrument: name the
loop's count register, then log every write to it between the last
correct load and the loop's first iteration. It also explains why the
earlier probes found `$2` and `$10` reading zero *mid-loop* while
`TCHSXW`/`TMUCTX` were correct -- mid-loop is after the wrap, so a zero
there is the consequence, not the cause, and every probe placed there
was downstream of the event by up to 16 million steps.

**Three method notes, all paid for in this session.**

1. **A harness number is not a machine number.** The cap produced the
   tail; the tail was read as behaviour. This file already recorded the
   same error as "22M to 6M means it ran faster" -- it meant it halted.
   Recognising the pattern in the abstract did not stop me repeating it.
2. **Pre-registering outcomes caught it, and nothing else did.** The
   confound surfaced while writing outcome (d) for a run not yet made,
   two commits after the bad conclusion was already committed. Writing
   down what each result WOULD mean is what made the reduced cap
   visible as an assumption.
3. **Check the repo for the number before measuring it.** "16 MILLION
   STEPS" was sitting in a comment in the very testbench being
   instrumented. A grep for the magnitude would have found it before
   any of the six instrumented builds.

### >>> THE SWAP IS NAMED, AND IT IS `T ASSIGN`'s OWN PROLOGUE <<<

Half-word 3970 is word 1985, octal 3701, and printed **p.65 line 9** is

    003701.00   T ASSIGN   SWAP I,12,$1,T ASAVE   -SAVE INDEXES

**Every measured detail matches.** The instrument reported a 12-word
SWAP at half-word 3970 with `x.src == 26`; the listing says 12 words
starting at `$1`. Twelve words from `$1` is words **17-28**, which
contains word 26 (`$10` = `T IXF`) and deliberately spares `$0` and
`$13`-`$15` -- and `$15` is used two instructions later as `020($15)`,
so sparing it is necessary and the range is self-confirming.

> **SO `$10` GOING TO ZERO AT ASSIGN ENTRY IS CORRECT, AND INTENDED.**
> `SWAP` is how MCP saves indexes: the caller's live registers go out
> to `T ASAVE` and `T ASAVE`'s contents come in. One instruction both
> saves and restores. On a first entry `T ASAVE` is zero, so ASSIGN
> necessarily begins with a zero index set. Nothing is corrupted.

**This retires the writer hunt completely.** Every write to `$10` in
the boot is now not merely "legitimate" but traced to a named
instruction at a named listing address.

### And the loop is correct too, on the pass that was measured

Printed **p.72 line 4** is the load the loop depends on:

    004215.00   T AD   LX,TIXF,TCHSXW   -BEGINNING OF CHAN STAT TABLE

`T CHSXW` (word 1130) was measured as `0x02bf800000900000` -- address
word 2814, count 36 -- and the census shows `$10` loaded and walked
**2849 down to 2814 with the count going 36, 35, 34, ...**, which is
exactly `T CHSXW`'s 36-word span. **The loop runs 36 times and is
right.**

> **>>> THEREFORE THE 2^18 PASS IS A SECOND, DIFFERENT ENTRY TO THE
> SAME LOOP. <<<** `TB9B CB+,TIXF,TA9A` is reached on some path that
> does NOT pass p.72 line 4's `LX,TIXF,TCHSXW`, so it counts on
> whatever the ASSIGN-entry SWAP left behind -- zero -- and a count
> field of zero means 2^18 (Reference Manual). The 262,144 writes to
> `word 0 off 20 len 4` are `T CHCNT` resolved against a zero index:
> `T CHCNT` is `SYN(BU,4), 0.20`, a TEMPLATE with offset 20 and no
> base, so a zero index puts it at word 0.

**The question is now a control-flow question about a named routine,
which is the most tractable form it has taken.** Which branch reaches
`TA9A` without the load? printed p.72 has the candidates in view
already -- line 25's `L,TUNITK(TIXF)`, line 38's `LV,TIXG,TIXF` -- and
p.65's ASSIGN prologue runs `BB,TASGNP,TOD` and
`BB,TIBPRC(TIXE),TB8` before any of them. If MCP's intended path always
passes the `LX` and the model's does not, the defect is a branch
condition, not an address and not a store.

### Two checks on the section above, one of which I had taken on trust

**1. `T MUCTX` has count zero BY DESIGN, and that is not the defect.**
printed **p.290**:

    T MUCTX   XW,TCHCUC,0,0   -CONSTANT TO THE BEGINNING OF CNT TBL

An index word whose value is `T CHCUC` with sign, **count and refill
all zero**. It is a base pointer, not a counter, so
`LX,TIXH,TMUCTX` (printed p.72 line 15) is *supposed* to leave `$2`
with count zero. The loop's count comes from `$10` via line 4's
`LX,TIXF,TCHSXW`, which carries 36. The earlier probe table that
recorded `T MUCTX` as "correct" was right, and reading its zero count
as suspicious would have been a thirteenth false lead.

**2. The "16 MILLION STEPS" comment does name this interval -- checked,
because I had cited it as corroboration without reading it.**
`gen_mcp_boot_tb.py`'s comment is a *ratchet history* of indicator sets
as successive listing pages were transcribed, not a direct measurement
of a loop. But the entry in question is

    printed pp.66-72 as well, so T A9's own code runs ... and the
    run is 16 MILLION STEPS longer

i.e. **adding pp.66-72 -- which is the `T ADA` region -- lengthened the
boot by 16 million steps.** So it corroborates the interval, and more
specifically than claimed: it attributes the 16M to `T A9`'s own code
executing. The arithmetic (2^18 x 61 = 15,990,784) and the comment are
two independent witnesses to the same thing.

**It also shows the 16M growth was observed before and accepted as
normal.** The comment's concern was the indicator set, not the step
count. A number that large went by as unremarkable because nothing was
asserting against it -- which is the same gap `docs/microarchitecture_roadmap.md`
opens with ("a stage with no oracle is a stage whose bugs survive").

### Where this leaves the question, stated precisely

The loop body is reached only by falling through from `004224.40` or by
its own back-edge: a lookup of every listing line citing `004225`
returns **one**, the definition itself, so nothing branches into
`T ADA`. Yet the 262,144 writes land at **word 0** offset 20, which
requires `$2 == 0`, and the count reached 2^18, which requires `$10`'s
count `== 0`. **Both registers zero means neither `LX` at p.72 lines 4
and 15 took effect on that pass**, while the fall-through path to the
loop crosses both.

The one event known to zero exactly those registers is `T ASSIGN`'s
prologue `SWAP I,12,$1,T ASAVE` (words 17-28), measured entering
**exactly once**, at ~6.12M -- after the correct 36-iteration pass at
~6.01M.

> **THE NEXT MEASUREMENT, AND IT SHOULD BE AT THE CANONICAL
> 40,000,000 CAP:** log every execution of `004215` (`T AD`),
> `004224.40` and `004225` (`T ADA`) with `$2` and `$10` beside it. If
> `T ADA` runs without `004215` preceding it, the loop is being
> re-entered by a path the listing does not show and the model's
> control flow is wrong. If both `LX`s execute and the registers are
> still zero, the `LX` instruction itself is at fault for an index
> word read from a special address. Those are the two arms, and they
> are distinguishable in one run.

## A4 MEASURED AT THE CANONICAL 40,000,000 CAP -- what is established, and what is not

Four runs, all at the real cap, instrumented in the testbench's run
rule (which sees every instruction whichever unit executes it) and at
`StretchExecute`'s one general `st.writeIndex` site, where the
instruction's **own** `pc` is in scope rather than the I-box's
running-ahead `pcReg`.

### Established

1. **The boot runs to step 22,118,685 and completes.** It does not
   hang. The confound resolution above is confirmed directly.
2. **`$10` changes 113 times in 22 million steps**, and `execute()`
   performs **105** index writes to it. Both are tiny numbers, and they
   agree.
3. **`$10` is zeroed at step 6,123,419, at `pc=3972`** -- two
   half-words past 3970, the I-box running ahead of `T ASSIGN`'s
   `SWAP I,12,$1,T ASAVE`. This independently confirms the SWAP
   identification from the listing.
4. **`$10` then stays zero from step 6,123,419 until ~22,116,090 --
   about 16 million steps**, three quarters of the boot. The 16M is
   therefore not a loop whose counter is being decremented; it is 16
   million steps during which `$10` is never written at all.
5. **No index write to `$10` originates anywhere in the p.72 region.**
   The writer PCs are 1021 (36 times -- the loop that works), 4020,
   4035, 4010, 3137, 3047, 4622, 4583, 4025, 1034, 4576, 4006, 3332,
   3131. **4378 (`TA9`'s `LX,TIXF,TCHSXW`) is absent, and so is every
   PC in the loop's body.**
6. **The transcription is right.** `decks/mcp_bootstrap_p72.strap` has
   `SLC, (8)4215.0`, `TA9  LX, TIXF, TCHSXW` at line 4, `TCHSXW SYN,
   (8)2152.0` (= word 1130), `TIXF SYN, $10`, and
   `TB9B  CB+, TIXF, TA9A` at line 51. The loop does count on `$10`.
7. **The correct 36-iteration pass is a DIFFERENT routine**, at
   `pc` 1010-1031, not p.72. The two were conflated earlier in this
   session because both load count 36 from `T CHSXW`.

> **THE SHARP OPEN QUESTION: `TA9`'s `LX` and `TB9B`'s `CB+` both name
> `TIXF`, both are transcribed correctly, the loop body demonstrably
> executes -- and `$10` is never written in that region across 16
> million steps.** Those cannot all be true of a machine executing
> that code as written. Something in the p.72 region is not executing
> as an index operation.

### >>> THAT QUESTION IS ANSWERED, AND THE ANSWER WAS THE ASSEMBLER -- 2026-10-29 <<<

The last sentence above was right and the search was looking in the
wrong place. Nothing in the p.72 region failed to execute as an index
operation; **`LX, TIXF, TCHSXW` was ASSEMBLED with no index register at
all.** `TIXF` is `SYN, $10` and `$10` is itself a `SYN` -- MCP printed
p.61 lines 32 and 39 -- and `strap_asm.py` recorded `SYN, $N` only ONE
level deep, so a chained `SYN` lost its register and the instruction
compiled with `j = 1664 & 0xF = 0`. Word 0 is `addrZero`, the permanent
zero whose writes are ignored, which is exactly "the loop body executes
and `$10` is never written."

Thirteen model-side hypotheses were refuted before the defect was found,
and it was never in the Bluespec. `tests/verify_syn_chain_reg.py` now
pins it with eight checks.

**Items 1, 3 and 4 of the Established list above are SUPERSEDED.**
Re-measured today on the fixed assembler, same testbench, same tape,
same ending (PC 239, all 55 checks passing):

| | before the fix | now |
|---|---|---|
| boot completes at step | 22,118,685 | **6,140,103** |
| `$10`'s last change | ~22,116,090 | **6,137,982** |
| steps from that change to the halt | ~2,595, after 16M of silence | **2,121, with no silent stretch at all** |
| `$10` first reads zero at step | 6,123,419 | 6,117,533 |

**The sixteen million steps are gone**, and that is the whole finding:
`$10` is now written continuously up to two thousand steps before the
machine halts, instead of being abandoned for three quarters of the
boot. The boot is 3.6x shorter because the dead stretch was the defect's
signature, not work.

> **AND THIS SECTION'S OWN WARNING APPLIES TO THE NEW NUMBERS TOO.**
> The `$10` figures above are VALUE-CHANGE counts sampled once per step,
> which is a different instrument from the old "113 times", so 113 and
> today's 164 are **not comparable** and no conclusion is drawn from the
> difference. What is comparable is WHERE the last change falls relative
> to the halt, because both runs end at the same place.

### NOT established, and the reason is my own instrument

**`tadaN` counts STEP-SAMPLES, NOT ITERATIONS.** The run rule fires
once per step and `core.getPC()` holds the same value for as long as an
instruction occupies the machine -- measured directly: `pc=4378`
appears on **23 consecutive steps**. So every per-PC count in these
runs is a residence time, not an execution count, and the "159 body
samples" figure means nothing about iterations.

**This puts the 2^18 = 262,144 figure back in question.** It came from
counting `CM` stores of `word 0 off 20 len 4`, which is per-execution
and so is probably sound, but it has not been re-measured at the
canonical cap in this session, and it is in tension with finding 5: a
loop closing on `CB+,TIXF` 262,144 times must write `$10` 262,144
times, and the measurement says it writes it never.

> **ONE OF THOSE TWO MEASUREMENTS IS WRONG, AND THAT IS THE NEXT
> THING TO SETTLE** -- before any model change. Re-count the `CM`
> stores and the `CB+` executions **in the same run**, from
> `StretchExecute`'s store path and its index-write path, so the two
> numbers cannot come from different builds. This project has a
> written rule about exactly that and it is the third time this
> session it has mattered.

### Method notes from the four runs

* A probe at `StretchCore`'s `rl_idx` reported **zero** writes to
  `$10` in a boot that demonstrably writes it 105 times. That rule's
  own comment says it handles "Part 2 of a progressive-indexing
  instruction" -- it is not the general path. **Read the rule's comment
  before trusting its silence**, which is the same lesson as the
  `execute()`-versus-run-rule probe already recorded.
* `readIndex(2)` and `readIndex(10)` in one rule is a `(G0002)` port
  conflict. `snapshotIndex()` returns all sixteen in one call and is
  the right instrument for watching index registers from a testbench.
* "build errors: 0" was a **false green** once: the generator died with
  a Python `NameError`, so `bsc` never ran and there was no `^Error:`
  line to match. A grep for the absence of errors is only meaningful
  if the thing that produces them actually ran. Check the exit status.

## THE 2^18 FIGURE RESOLVED: word 0 is the PERMANENT-ZERO REGISTER

Settled by counting both numbers in **one** build, as the rule
requires, and then by one line of `StretchTypes.bsv`:

    WordAddr addrZero = 0;   // permanently 0, writes ignored

**Word 0 is the 7030's hardwired zero register.** So the earlier
finding -- "262,144 writes to `word 0 off 20 len 4`" -- was counting
stores that the machine *discards by design*. `T CHCNT` is
`SYN(BU,4), 0.20`, a template with offset 20 and no base, so an index
of zero resolves it to word 0, and every one of those stores went into
the bit bucket.

> **>>> SO THAT FINDING WAS NEVER A CAUSE, AND NOT EVEN AN EFFECT ON
> STORAGE. IT WAS A RESTATEMENT OF `$2 == 0` IN DIFFERENT UNITS. <<<**
> Six measurements in this session were spent downstream of it.

**And it does not reproduce at the canonical cap.** In one run:

| count | measured |
|---|---|
| field stores of shape (word 0, off 20, len 4) | **0** |
| ALL four-bit field stores, whole boot | **36** -- at words 552, 674, 675, none at word 0 |
| index writes to `$10`, same run | **105** |

The 36 proves the instrument fires, so the zero is evidence and not
silence. The four sites probed are the generic VFL field stores
(`insertFieldBits(prefetch[0], off, len_, ...)`); `CM0000` is the
CONNECT family and may store by another path, so the honest statement
is: **either the CONNECT store is routed elsewhere, or these stores do
not happen at the canonical cap.** Which of those does not matter,
because word 0 absorbs them either way.

### What survives, and it is the same single question

The contradiction that prompted this -- "a loop closing on
`CB+,TIXF` 262,144 times must write `$10` 262,144 times, and the
measurement says never" -- **dissolves**: the 262,144 was not an
iteration count of anything. The 105 index writes stand.

> **THE QUESTION IS NOW UNPOLLUTED AND SINGULAR: why does
> `TA9  LX, TIXF, TCHSXW` at half-word 4378 never write `$10`?**
> `decks/mcp_bootstrap_p72.strap` places it correctly (`SLC, (8)4215.0`,
> `TCHSXW SYN, (8)2152.0` = word 1130, `TIXF SYN, $10`); the testbench
> run rule sees the I-box PC resident on 4378 for 23 steps; and
> `StretchExecute`'s one general index-write site, which carries the
> instruction's own `pc`, never reports 4378. Three arms remain:
> `execute()` is never called with that `pc`; it is called and
> `doIdxWrite` is false; or the instruction decodes to something other
> than an index load.

# >>>>>> ROOT CAUSE FOUND, AND IT IS AN ASSEMBLER BUG <<<<<<

**A SYN to a SYN to an index register lost the register.** Found
2026-10-28, with MCP's own listing as the witness, after thirteen
refuted hypotheses about the model.

## The chain of evidence, each link measured

`execute()` was asked directly what it does with printed p.72 line 4:

    TA9DIX  code=1  di_j=0  xo_do=1  xo_reg=0  xo_val=0x02bf800000900000

`code=1` is `dixop_LX`, so it decodes as LX. `xo_val` is **exactly
`T CHSXW`'s contents** -- word 2814, count 36 -- so the address field is
right and the fetch is right. But **`di_j=0`**: the decoded instruction
names index register **0**, not 10.

The decoder is not at fault (`j: hw[12:9]`, and the listing's second
printed field is bits [12:8], giving `$2` -> 4 and `$10` -> 20, both
exactly 2*j). **The instruction word in memory had j=0:**

| | word 2189 left half | `j` |
|---|---|---|
| standalone `decks/mcp_bootstrap_p72.strap` | `0x011a9410` | **10** |
| merged MCP-IPL tape image | `0x011a8010` | **0** |

Same address field, same opcode, one field different.

## The cause, in one line of `strap_asm.py`

`SymTab.sys_alias` keeps a symbol defined as `SYN, $N` **as** the system
symbol, so `$N`'s register-field/address-field duality survives: in a
register field it yields `N`, in an address field `(16+N)*64`. It was
recorded by

    if (len(body) > 1 and re.fullmatch(r"\$[A-Za-z0-9]+", body) ...):
        symtab.sys_alias[up] = body[1:]

-- which matches only a body that is **literally** `$...`. MCP's source,
printed **p.61 lines 32 and 39**, and again on printed **p.287**:

    T X1    SYN, $10    -TEMPORARY INDEX
    T IXF   SYN, TX1    --MACH CONF CHANGE-- CHAN. SCAN IX

`T IXF` names index register 10 through **two** levels. The second SYN's
body is `TX1`, a symbol and not a `$`, so no alias was recorded and
`TIXF` fell back to its numeric value -- 1664, the bit address of word
26. And

    1664 & 0xF = 0

which is the `j=0` that was measured. **The arithmetic closes.**

## Why it is a bug and not a transcription error

The deck is faithful; the listing says `SYN, TX1` twice, in two
independent places. And C22-6531 printed **p.31** calls SYN an **"EXACT
SUBSTITUTION"** in which the properties of Y "are **TRANSFERRED** to A".
The assembler already honoured that for data descriptions (`sym_dds`)
and for integer classification (`sym_int`) -- both inherited through a
bare-symbol SYN. **The system-symbol alias is the same kind of property
and was the one that was not.** The fix makes it transitive, which is
what the printed rule says it always was.

## Why nothing caught it for so long

> **>>> THE PAGE'S OWN DECK DEFINES `TIXF SYN, $10` DIRECTLY -- ONE
> LEVEL -- SO printed p.72 ASSEMBLED CORRECTLY IN ISOLATION. <<<** Only
> the MERGED image, where printed p.61's chained definition wins, ever
> carried `j=0`. Every per-page test passed. The new verifier therefore
> checks the standalone deck AND the merge **and asserts that they
> agree**, because their disagreement in exactly one field is what this
> bug was.

And the failure mode is the quiet one this project keeps finding: the
address field was correct, the value fetched was correct, `doIdxWrite`
was set, no indicator was raised, nothing was refused. **The right value
went to the wrong register, silently.**

## What it explains

`LX, TIXF, TCHSXW` loaded `$0` instead of `$10`, so `$10` kept whatever
`T ASSIGN`'s prologue `SWAP I,12,$1,T ASAVE` left in it -- zero, which
is correct for that SWAP -- and printed p.72's channel scan then ran
with a zero index and a zero count. That is the whole symptom the
session began with, and every model component it passed through was
behaving correctly.

> **AND IT IS WHY THIRTEEN HYPOTHESES ABOUT THE MODEL ALL FAILED.** The
> defect was never in the Bluespec. The instrumentation campaign was not
> wasted -- it is what eliminated the model, one named writer at a time,
> until the only thing left was the instruction word itself -- but the
> lesson is cheaper than the route: **when every reader of a value is
> innocent, suspect the value.** Two assemblies of the same source line
> differing in one field is a five-line Python check, and it was
> available on day one.

## The test and its measured injection

`tests/verify_syn_chain_reg.py`, registered second in the suite. Eight
checks: one, two and three levels of chaining; that the ADDRESS field
and the numeric value are untouched; the merged image's word `004215`
by J field and by whole half-word; and that the standalone deck agrees
with the merge.

**Injection, measured:** removing the transitive arm fails **five of
eight**, including the named address -- merged word `004215`, printed
p.72 line 4, J field 0 instead of 10 -- while "one level (`TX1 SYN,
$10`)" still passes, which is what isolates transitivity as the thing
under test.

# >>>>>> PHASE A RE-AUDITED AGAINST THE CODE, 2026-10-29 <<<<<<

The Phase A section above describes a fixture that no longer exists.
**All three punching tasks are done**; the prose was written before
they landed. What follows corrects it, and the correction changes the
shape of the work: **Phase A is ONE blocking item plus one piece of
genuinely missing A2, not three items.**

## A1 — done, and its DONE-CRITERION IS RETIRED, not merely unmet

The punching is correct: `strap/iocd.py:215-216, 262-271` writes the
reference number to columns 63-66 and the absolute exit to 67-72, and
raises on a wrong digit count. Measured over `prosa.MCP_IODS`:
`MCPRDR` -> `0001`/`004000`, `MCPOUT1` -> `0002`/`004000`, `MCPOUT2`
-> `0003`/`004000`.

**But the criterion "done when `T IOREQ` is non-empty" was retired by
commit `782f6af`** and this file never caught up: `T IOREQ` is the
PROBLEM-PROGRAM request table that MCP-DECODE builds for a job, and no
job is loaded, so empty is CORRECT. The request counts live in printed
p.64's table. The two were conflated.

> **AND A1 HAS NO DIRECT REGRESSION COVERAGE.**
> `tests/verify_card_columns.py` checks the BIT ARITHMETIC that column
> 63 is bit 372 — it never calls `iod_card_text`. The only boot checks
> derived from the card text are `mcp_ucbf1_0/1`, which cover SCA6
> output words 0-1, i.e. roughly columns 1-21. **Columns 63-72 are
> asserted nowhere.**

## A2 — the doc is stale AND A2 is genuinely incomplete

Stale: `MCP_IODS` (`strap/prosa.py:368-378`) has had the reader and
TWO OUTPUT TAPES since `782f6af`; `TERMINATOR_CARD` (`:379`) is now a
marker tuple whose blank fields are never punched. The deck is nine
cards — five IOCD, three IOD, one MCPP — landing at 2870-3004,
starting exactly at `X IN END`.

**Incomplete, and this is the finding.** printed p.98 case 1, read at
the ink rather than from a summary:

> *"The card reader is assigned to MCP… **The output tape units are
> assigned to MCP** and the necessary tables are constructed… **unit
> and file area tables are formed for the input tapes**, but they are
> not put under MCP ownership until a system command changes the
> operating status to overlapped."*

Three things, and the deck supplies two. **The input tapes are
missing.** Corroborated inside the model: `decks/mcp_bootstrap_p31.strap:90`
reads a spool INPUT tape IOD number out of the communication region
(`LV, $14, SRTAPE`, "BYPASS GET SPOOL REAL TYPE IOD NUMBER"), which
with no input-tape IOD is zero. Note also `prosa.py:291` gives channel
34 only two units and both are consumed by the output tapes.

## A3 — the card IS punched, and is bit-exact against MCP's own literals

Not an unused helper. `prosa.py:528, 532-534` punches it as card 9 at
word 2990, and it matches the listing's comparands exactly:

| | fixture | MCP's literal |
|---|---|---|
| cols 10-13 | `0o2040410020042004` | `XMCPP DD(BU,48)`, `decks/mcp_bootstrap_p35.strap:71` |
| cols 14-15 | `0o42001002` | `XBYPS DD(BU,24)`, `decks/mcp_bootstrap_p36.strap:123` |

It also **terminates the IOD scan correctly**: `decks/mcp_bootstrap_p25.strap:129`
loops while bit 132 is one, and that bit is 1 for `IOCD` and `IOD` and
**0 for `MCPP`**.

**Its criterion is unmet for an ORDERING reason, not a card reason.**
p.31's mode read is reached only from p.30, and the chain
p.27 -> p.28 -> p.29 -> p.30 -> p.31 is cut at p.27 line 13's
`BZXCZ, XERROR`. The current boot never executes the MCPP read.

> **A3's OWN OPEN QUESTION IS ALREADY ANSWERED.** `strap/iocd.py:299-307`
> says `C22-6728-1` p.96's mode-field width "is on the render queue in
> docs/source_audit.md". It is not on that queue and does not need to
> be: `decks/mcp_bootstrap_p31.strap:63` reads **24 bits = two columns,
> 14-15**, and compares against `ON`/`OF`/`BY`. The rest are never read.

## What the testbench actually asserts — the failure, as the expected state

There is **no check** for `T IOREQ`, for p.64's validity-check table,
for the MACH CONF counts, or for the disposition bit. What is asserted
is the whole error path: `mcp_x_err_ad` = `0x00CE600000000000`
(= `001471.40`, p.27 line 13 taken), ten console words of
"IO ASSIGNMENTS CAN NOT BE MADE", and `pc_check = 239`. **When Phase A
succeeds, twelve checks move at once.**

## Did the SYN fix explain it? Partly, and the reject SURVIVED

The MACH-CONF-zero symptom is plausibly explained — p.72's scan ran on
a zero index, and two post-fix corroborations are already in the
testbench (`S YPRCH` now 33, the printer's channel; AH -> AE). **But
the reject did not move.** Commit `6925932` changed exactly two
expectations, and `mcp_x_err_ad`, the console words and `pc_check` were
not among them. So either the conf counts are still zero for a second
reason, or they are now non-zero and ASSIGN rejects for a different
one.

> **>>> THE NEXT ACTION IS ONE MEASUREMENT, AND IT NEEDS NO NEW CODE.
> <<<** Read words **1962-1964** (the validity-check table) and
> **1787-1789** (`T IOREQ`) after one boot and compare against the
> pre-fix rows recorded in `docs/mcp_io_tables.md:264-278` — DISK
> (0,0,1), CONSOLE (1,0,0), READER (37,0,0), EXTRA (0,0,0), TAPE
> (0,0,0), conf bytes all zero, three type bytes corrupted.
>
> **Non-zero conf ⇒ the SYN fix closed the counts and the reject has a
> NEW cause** (most likely the missing input tapes, or `X242`'s
> `C = 4` against rendered p.72's "C = 0 means overlapped", flagged
> earlier in this file and never followed up).
> **Still zero ⇒ the two were independent all along.**

## Phase A, restated

1. **Measure 1962-1964 and 1787-1789 after one boot.** Everything is
   downstream of this. No instrumentation, no new code.
2. **Supply the INPUT-tape IODs p.98 case 1 names**, and whatever tape
   units `bsv/StretchIO.bsv` must present for them.
3. **Reconcile `X242`'s `C = 4`** (`decks/mcp_bootstrap_p27.strap:61`)
   against rendered p.72's entry-mode meaning. A reading, not a run.
4. **Add the checks that are missing**, so the criteria become
   mechanically observable: the conf table at 1962-1964; `S COM RG`
   (word 1129) bits .8/.9 for A3's mode; the MCPP card's arrival at
   2990; and the IOD card's columns 63-72.

# >>>>>> G2.1, THE FIRST BATCH, 2026-11-08: EIGHT EXAMPLES, CHAPTER 1 FINISHED <<<<<<

Problems 1.1-1.5 and 1.7-1.9, read in the ink, every printed method run:
`decks/problem_1_{1,2,3,4,5,7,8}.strap`, `problem_1_5_method1.strap`,
`problem_1_9_method{1,2}.strap`.

**What it found:**

* **One unbuilt arm, now built: backward `SWAP`.** `SWAPB`/`SWAPBI` were
  refused out loud (OP), so no result was silently wrong.  It is 1.2's
  printed statement, and it fell to one line.
* **No wrong result anywhere else.** 1.4, 1.5, 1.7, 1.8 and 1.9 passed
  against the model as it stood, including 1.7's free-instruction entry,
  which this section's 2026-10-29 note called the runner-up target, and
  10,000 words of 1.9 compared one by one.  So the table's `C22-6578` row
  becomes **1 / 4 on bugs, plus 1 / 8 on a refused arm.** The earlier
  conclusion that this document is the lowest-yielding of the three stands
  and is now stronger.

**Open, and not decided here:**

1. **An IBM document conflict about the exponent's minus zero.**
   `C22-6578` printed p.5, Problem 1.1 Method 3 comment (b): an
   unnormalized LWF-store changes a "minus zero" exponent to "plus zero".
   Reference Manual printed p.83: the unnormalized `LWF` loads it and "A
   minus 0 exponent can be stored by an unnormalized FLOATING POINT
   STORE which specifies no sign modification."  The model follows the
   manual.  **The check pins the manual's value and says so in its label;
   the printed claim was not changed to agree, it is recorded as
   contradicted.** A grep of `docs/ocr/` found no third witness; `jb_af1c`
   is the unswept place that might hold one.
2. **`C22-6578` printed p.6, Problem 1.3 comment (a)'s `SWAPBI` line cannot
   be run as printed**: "SWAPBI, K, DOG + N-K-1" has one address where the
   instruction has two, and the address is wrong unless N = 2K.  The deck
   runs N = 4, K = 2, where it is right, and N = 9, K = 6 with the address
   worked out by hand, DOG + K-1, and labelled as not printed.
3. **`RNX` stays refused.** Problem 1.8 simulates it and passes, so the
   page gives a sequence to compare against, but the arm writes two index
   registers and a store, with the no-op range and the AD/DS/DF clauses of
   printed p.27.  Not small; `jb_ax4b` routine 1244 is its test plan.
4. Not run, each for a stated reason in its deck: 1.1 Method 2 comment (b)
   (a zero count overwrites all of core) and 1.7 comment (c) (needs a second
   interruption inside the two-instruction window).

# >>>>>> G2.1, CHAPTER 2, 2026-11-15: PROBLEMS 2.3 TO 2.12, NINE RUN, ONE BLOCKED <<<<<<

`C22-6578` printed pp.14-25, read in the ink, every printed method
transcribed.  Decks `decks/problem_2_{3,4,5,6,7,9,10,11,12}.strap`,
`problem_2_3_method4.strap`, `problem_2_6_method3.strap`,
`problem_2_8.strap` (not run); `tests/run_tests.sh` section 3d, fourteen
registered runs, **333 checks, all passing as written** (the section was
run on its own, exactly as registered; the full suite was not).

**The model: no wrong result in anything it executed.**  That includes,
each for the first time in a worked example: a data-flag interruption
(`$VF`) through a table entry the program swaps in (2.12); `LVE`/`SVA`
against a `SIC`'s 24-bit address (2.7); a store into the instruction that
follows it (2.9); `KFI`, `M+` into an index value field, `*`/`/` with `$RM`
(2.9, 2.10, 2.12); `CONNECT` leaving the rest of the accumulator alone
(2.4); `(V+ICR)`'s refill inside the instruction (2.6 Method 3).  So the
table's `C22-6578` row gains nine problems and no model bug.

**The model: one refusal, known.**  Decimal VFL (G2.3): 2.3 Method 4's
`L(DU)`/`LWF(D)` and 2.8's `+(D)` set OP.  2.3 Method 4 is registered as a
pinned refusal whose labels carry the hand-derived values; 2.8 does not
halt once its add is refused and is not registered.  The first OP that run
reported was the add's, at half-word 2006, not the `LCV(DU)` before it --
not examined further.

*2026-11-16, G2.3 stage 1 built (decimal `+`, `L`, `LWF`, `ST`, `SRD`, the
`M+` family, through `mkDecBox`):* 2.3 Method 4's refusal is flipped -- its
three words now carry the hand-derived values, and pass.  2.8, run with
`ASM=strap2`, computes product 1's total as the program as printed does on
this data (`36`: the printed `+(D,48,8)` is signed, so E's last byte is a
sign byte -- traced before the run) and then loops in `KOMF` without
writing product 2; the loop is not traced and 2.8 stays unregistered
(`docs/NEXT.md` G2.3).

*2026-11-16, later: 2.8 traced and registered.*  The loop is the printed
program's, not the model's: `KOMF`'s `KF(BU,24)` compares three bytes with
the accumulator's N D (11111111) (printed pp.56, 65), never the one-byte
mark the following `V+I, $2, 1.0` assumes.  Registered as printed (a
deliberate stop in the loop), with `KF(BU,8)` (halts, 36/8/44: the pre-run
trace's values), and with the signed ADD made `DU` too (the statement's
375/80/455).  Two new rows in the defect table below; `docs/NEXT.md` G2.3.

**The assembler (`strap_asm`): two findings, both with reproducers and a
section in `docs/NEXT.md`, neither fixed.**  The host STRAP II
(`strap/strap2`) is right on both.

1. A `DD` in mode `D`/`DU` is assembled as a binary integer
   (`decks/repro_dd_decimal_mode.strap`; C22-6531 printed pp.28-29).
2. A blank after a radix specifier, `(2) 10`, is refused
   (`decks/repro_radix_blank.strap`, `tests/check_radix_blank.py`;
   C22-6578 printed p.21).  **Fixed 2026-11-23** (C22-6729 printed
   p.20, GETCHA drops blanks; `strap/README.md` "Next steps" item 10).

Not findings: `strap_asm`'s comment mark is `!`, so the printed `'`
comments are written `!'`; a symbol in a `DD` data field (2.10's
`DD(BU, 18), N`) is refused by STRAP II too.

**The printed programs: nine defects in seven methods, each worked by hand
from the Reference Manual** (eleven in eight since 2.8 was traced, below).  Seven of the nine were then run AS PRINTED and
the model agreed with the hand trace; 2.3 Method 3's is not run (it does not
terminate) and 2.12's is pinned only as far as what TEMP is left holding.
Each deck's header has the argument.

| Problem | Printed | What it does | Right |
|---|---|---|---|
| 2.3 M2 | `BZXCZ, $-1.0` | loops on the ST: first nibble twelve times | `$-2.0` |
| 2.3 M3, pair 3 | `ST(B,4,3) (V+I)` | count never moves; not run | `(V+IC)` |
| 2.5 | `B, LODE` after a key | one byte too many per key | `B, CAB` |
| 2.6 M3 | `K(BU,4)` | every compare HIGH after a fixup; does not sort | `KF` |
| 2.6 M3 | fixup after the last `(V+ICR)` | addresses through the refilled `$1` | -- |
| 2.7 | offset `-18` | key A goes to table 2A | `-19` |
| 2.9 | last `B, MPLUS` | bits 19-23 left in the sum | `B, KMINUS` |
| 2.9 | K-type, K = 1 | `$1` overwritten before it is read | -- |
| 2.12 | mask saved in `INST+1.0` | that word is TEMP, reused | -- |
| 2.8 | `KOMF KF(BU,24)(V+I)` | never matches: loops past the list | `KF(BU,8)` |
| 2.8 | `+(D, 48, 8)` | E's last digit read as a sign: 36, 8, 44 | `+(DU, 48, 8)` |

Also recorded, without a run: 2.6 Method 4 does not assemble as
printed (`BZXCZ, $3, TEST`) and has three more visible defects -- it is
transcribed in `problem_2_6_method3.strap`'s header; 2.8 prints the label
`LCON` twice; 2.11's statement says `$R` where its program stores in `R`.

**Open, and not decided here:**

1. ~~**2.8 and 2.3 Method 4 wait on the decimal arm.**~~  Both run since
   G2.3 stage 1; 2.8 registered 2026-11-16 (its stored digits carry zone
   0000 -- observed on the model, not derived by hand).
2. **2.6 Method 4 was not run.**  Running it means choosing four
   corrections; that would test the deck's rewrite, not IBM's program.
3. **2.9's K = 1 defect and 2.6 Method 3's last-compare defect have no
   corrected form in the decks** -- each needs more than a one-word change.
4. Every "printed defect" above rests on one reading of the ink and one
   reading of the manual, by one reader.  The model agreeing shows the
   model and the reader read the manual the same way; it does not make a
   third witness.  The pages are legible; the uncertain characters are
   listed in the deck headers (2.3 Method 4's `LWF(D,` comma; 2.6 comment
   (b)'s `($)`).

# >>>>>> G2 RE-CENSUSED, 2026-10-29: THE POOL G2.1 SIZES IS THE LOWEST-YIELDING <<<<<<

G2.1 says "Six run, four found bugs; ~45 exist and ~40 remain" and
sizes the pool from `C22-6578`. A census corrects the counts and —
more usefully — shows the sizing is pointed at the **wrong document**.

## The counts

* **`C22-6578` has exactly 44 problems, not ~45.** All 44 `^PROBLEM`
  headings recovered (1.1-1.9, 2.1-2.12, 3.1-3.10, 4.1-4.13), matching
  its own table of contents. **41 remain.**
* **NINE worked examples are done, not six.** The campaign six are
  {RefMan Fig 12, Fig 14, P1.6, `R23-9694` p.51 Ex.3, p.82, A4.8};
  RefMan Fig 7, P2.1 and P2.2 predate the framing and were mined as
  ordinary decks.
* **`docs/NEXT.md:13658-13662` contradicts itself**: it says the
  Reference Manual "has 49 numbered figures, of which **13** are
  programs", then lists **fifteen** (7, 8, 9, 10, 12, 14, 15, 17, 18,
  19, 21, 28, 29, 31, 33). All fifteen carry programs; **12 remain.**

## >>> AND THE HIT RATE INVERTS THE PLAN <<<

| document | finds / attempts |
|---|---|
| **Reference Manual program figures** | **2 / 2** |
| `R23-9694` | 1 / 2 |
| `C22-6578` | **1 / 4** |

G2.1 sizes the worklist from `C22-6578`, which is the **lowest**-yielding
of the three. The Reference Manual's figures are two-for-two and there
are twelve of them left.

## Three stale claims, each with a consequence

**(a) `/`, `CV` and `LTRCV` are BUILT and three files still call them
refused** — `bsv/README.md`'s census (dated 2026-10-25),
`tests/audit_opcode_coverage.py`'s `ENCODING_ONLY` set, and
`NEXT.md:1382`. The arms are at `StretchExecute.bsv:2860`, `:3442`,
`:3514`, each with a deck and a registration. By this project's own
rule — a scope list is a measurement with a date on it — all three want
re-dating.

**(b) `VflAddr.i2` is decoded and read NOWHERE.** Extracted at
`StretchDecode.bsv:117`; the only `.i2` reads in the model are I/O and
Transmit. Reference Manual printed p.21: *"In the variable field
instructions, the 19 bits which form the length, byte size, and offset
field are indexed as a single field. Carries between parts of this
field, if present, are not suppressed."* `strap_asm.py:134-138` already
records it, but it is **absent from `bsv/README.md`'s "decoded but not
executed" list**, so the scope list does not know.

**(c) `SWAPB`/`SWAPBI`'s refusal rests on a false premise — CORRECTED
IN `bsv/README.md` TODAY.** That file said "nothing in this corpus
encodes one … building them would be manual-derived with no oracle."
`C22-6578` prints `SWAPBI` twice, **printed p.5 Problem 1.2 Method 1**
(`SWAPBI, 2, DOG +1.0, CAT +1.0`) and **printed p.6 Problem 1.3**.
Verified at the OCR. Backward SWAP is buildable with two printed
oracles and is the cheapest of the four items left on
`StretchExecute`'s scope list.

**(d) Problem 4.5's recorded blocker is the wrong one.**
`NEXT.md:13678-13690` says it is blocked on `$AOC`/`$LZC`, which were
**built on 2026-10-20**. Its real blocker is (b): its own comment says
*"The second I field in a VFL instruction can be used to index the
field length and byte size besides the offset."*

## What is actually blocked — and it is never the source

Every candidate document is already in `docs/` with OCR. **The blocked
axis is INSTRUCTION-blocked**: `RNX` (RefMan Fig 9), decimal VFL plus
`KE`/`KR`/`KFE`/`KFR` (Figs 15, 17, 18; problems 2.3, 2.8, 4.2),
`DCV` (Fig 19 — one arm away, and the only printed oracle for the
radix-conversion family), and the `i2` field (4.5).

## The one to do next: Reference Manual FIGURE 21, printed p.77

Three connective statements that shift the 128-bit accumulator left ten
places: `C0011(BU,54,8),8.10,74` / `C0011(BU,64,8),9.0,10` /
`C0000(BU,10,8),0,0`.

**The discriminator is measured, not aesthetic.** Words 8 and 9 ARE the
accumulator (`StretchTypes.bsv:62-63`). A census of **1,219**
connective statements across every deck found **ZERO** naming word 8 or
9 as a storage operand. Figure 21 does it twice — both operands the
same register, an unexercised read-modify-write ordering case, in an
arm whose offset handling `bsv/README.md` records as having been wrong
once already ("built as a rounded-down byte offset on three strands of
manual reading, and fifty-six sections of `jb_af1c` killed it"). Its
note 1 also reasons about avoiding a **partial field**, which is
explicitly not implemented for connectives.

Three statements, every arm built, source in hand, and the document it
comes from is two-for-two.

**Runner-up, to take second rather than instead: `C22-6578` Problem
1.7, printed pp.9-10** — interrupt free-instruction entry, two
statements, targeting what `NEXT.md:1491` calls the single
highest-value item (the interruption mechanism is manual-derived only).
Its comment (d) states a corner no deck exercises: *"The SIC action is
not performed unless the ensuing branch is successful, and even then it
is performed AFTER the execution of the branch."*

## G2.2, BUCHHOLZ APPENDIX B

*Begun 2026-11-15.* Appendix B of `Planning_A_Computer_System.pdf`,
"Programming Examples", is printed pp.292-304 (PDF 317-329): three pages
of notation and then **seven tables, B.1 to B.7** (the item above says
six; B.6's section carries two tables, the large bit matrix and the
8-by-8 one). The notation is the book's own -- operations spelled out,
`(FN)`/`(FU)`/`(VBU, L, BS)` mode symbols, addresses as `word.bit` -- and
**Appendix A.4 (printed pp.277-284, PDF 302-309) gives the mnemonic in
parentheses after every spelled-out name**, so no mapping is inferred
from usage. The book prints neither data nor results; each deck supplies
data and derives its expected words by hand. The locations are the
book's (100.0 up), so the halt PC checks the Location column.

The decks are `decks/buchholz_b*.strap`; the tests are the "BUCHHOLZ
APPENDIX B" group in `tests/run_tests.sh`.

| Table | Printed | Deck | Exercises | Status |
|---|---|---|---|---|
| B.1 Polynomial evaluation | p.295 | `buchholz_b1_polynomial` | `LX`, `L(N)`, `*(N)`, `+(N)`, `CB-`, `ST(U)` | **passes 7 of 7** against the model as it stood; two data injections observed |
| B.2 Cube-root extraction | pp.296-297 | `buchholz_b2_cube_root` (as printed), `buchholz_b2_cube_root_srd_substituted` | `E+I`, `F+`, `R/`, VFL `L(B,12,1)`, `+I`, `/I`, **VFL `SRD`**, `CB` | **FINDING: VFL `SRD` was unbuilt** and refused at 105.32 (`decks/repro_vfl_srd.strap`, `NEXT.md`); as printed the root was wrong for four of eight N. **BUILT 2026-11-16: `verify_buchholz_b2.py printed` passes, 32 of 32 over eight N, and is registered.** With `SRD` replaced by the Reference Manual's equivalent (`+MGI`, `ST`; printed p.64): **32 of 32 over eight N**, each root inside the book's "48-bit accuracy, except for a possible rounding error" |
| B.3 Matrix multiplication | p.298 | `buchholz_b3_matrix_multiply` | `DL(U)` of `XFNZERO`, `LFT(N)`, `*+(N)`, `SRD(N)`, `V+I`, `CBR+`, `CBR`, `LX` from an index register | **passes 13 of 13** against the model as it stood, including a 49-bit sum that floating `SRD` must round and all five final index words; three data injections observed |
| B.4 Decimal numbers to a normalized FLP vector | pp.299-300 | `buchholz_b4_decimal_vector` | `LCV(V+I)(DU,60,6)` at offset 68, `*(N)` by operand 8.0, `SRT(N)`, `/(N)`, `CBR+`, `CB+` | **passes 31 of 31** against the model as it stood, the book's 25 numbers; zone bits shown not to matter; three data injections observed |
| B.5 Editing a typed message | pp.301-303 | `buchholz_b5_edit_message` | `CI0011` with byte size 1, `C0011`, `CM0101`, `CT0001`, `CT1001`, `CM0000`, the left-zeros count as an index operand, `BRZ`/`BZRZ`, `LC`, `SX`, `BXCZ` | **passes 11 of 11** against the model as it stood; three data injections observed, one of them note (13)'s error stop. The book's `ADD TO VALUE, X1, 7.17` names the LZC register; a 19-bit address holds 7.0 (Reference Manual printed p.76) |
| B.6 Transposition of a large bit matrix | pp.303-304 | `buchholz_b6_bit_matrix_transpose` | `C0011(V+I)` with an **indexed offset**, `V-ICR`, `ST(V+IC)`, `LCI`, `V+C`, `BZXCZ` | **FINDING, AND IT IS THE BOOK'S: the table as printed does not transpose.** Its `(VBU, 1, 1)` makes each `CONNECT 0011` replace eight accumulator bits (the book's own sec. 7.14, printed pp.90-91; Reference Manual printed p.75), so every stored word keeps only its last bit. The model does what both sources say: `verify_buchholz_b6.py printed` passes on exactly that, 256 of 256 words. With `(VBU, 1, 8)`, `verify_buchholz_b6.py corrected`: **the 128-by-128 transpose, 256 of 256 words**, A untouched, three index words. Two data injections observed |
| B.7 Transposition of an 8-by-8 bit matrix | p.304 | `buchholz_b7_8x8_transpose` | `Z` into the accumulator, `C0111(V+I)(BU,8,1)` with an indexed offset, `V-IC`, `BZXCZ`, `ST` | **passes 7 of 7** against the model as it stood; two data injections observed |

**What the seven found.** One unbuilt operation in the model (VFL
`SRD`, B.2; built 2026-11-16), one error in the book (B.6's byte size), and no wrong
result in anything the model executed. Five tables run as printed
(B.1, B.3, B.4, B.5, B.7). Not exercised by any of them: decimal
arithmetic, `SIC`, the I-O operations, Transmit, the indicator-setting
mode symbol `Z`, and index mode `H`.

**The readings that were not mechanical**, each argued in its deck's
header: B.1's `COUNT AND BRANCH` sense (A.4 p.284 words the on-off
modifier the other way round from the notation's `F`, printed p.293;
settled by the table's own note); B.3's bare `P` and `N` as word
counts; B.5's `ADD TO VALUE, X1, 7.17`, which names the left-zeros
counter and assembles as address 7.0; B.5's `LOAD COUNT` from the word
part of an index value (Reference Manual printed p.24).


# >>>>>> G2.1, CHAPTER 3, 2026-11-16: TEN PROBLEMS, CHAPTER 3 FINISHED <<<<<<

`C22-6578` chapter 3, "Floating-Point Arithmetic", printed pp.26-34,
Problems 3.1-3.10.  Every printed method was read from the page images
and transcribed as printed, and every one runs.  The expected values were
derived by hand from the Reference Manual, with pages cited in each
deck's header.  The long truncating sequences are checked against
`tests/problem_3_expected.py`, a calculator written from the same
manual pages, whose `--self` checks are registered.  Each problem is
proven discriminating by a data-side injection on a copy of its deck,
and the result is recorded in the header as OBSERVED.  All decks use
`ASM=strap2` (see items 1-2 below).  The counts below do not change this
section's earlier tables.

| Problem | Deck(s) | Registered checks | Status |
|---|---|---|---|
| 3.1 integer and fraction parts | `problem_3_1` | 9 + PC | pass |
| 3.2 integer part into the count of $1 | `problem_3_2` | 3 + PC | pass |
| 3.3 degree-20 polynomial | `problem_3_3_method{1,2,3}` | 3, 2, 3 + PC each | pass |
| 3.4 trapezoidal rule | `problem_3_4_method{1,2}` | 6 + PC each | pass; **the page's program never forms the integral** (NEXT.md ch.3 item 3) |
| 3.5 tan(pi/4), continued fraction | `problem_3_5` | 10 + PC | pass |
| 3.6 scalar product, LFT / *+ / SRD | `problem_3_6` | 3 + PC | pass |
| 3.7 cube root | `problem_3_7` | 9 + PC | pass |
| 3.8 VFL integers to normalized FP | `problem_3_8_positive` | 29 + PC | pass |
| 3.8 comment (b), EPLUS removed | `problem_3_8_no_eplus` | 29 + PC | pass against the page's claim; **the manual's p.87 text disagrees** (item 5) |
| 3.8 on signed data | `problem_3_8` | 2 + PC; 27 held back | **model fault**: address-8 sign (item 4) |
| 3.9 double-precision compare | `problem_3_9_method1_{less,equal,greater}`, `problem_3_9_method2_{page_fault,less}` | 4 + PC each; page_fault 5 + PC; 4 indicator words held back | pass; **the indicator store is dropped** (item 6) |
| 3.10 integer part of log2 N | `problem_3_10` | 3 + PC | pass |

**What it found** (docs/NEXT.md, "C22-6578 CHAPTER 3: WHAT THE PAGES
FOUND", items 1-6; each item has a reproducer deck):

1-2. **`strap_asm.py` refuses two printed forms.**  The first is
   `DD(N), 0.0X48`, a zero fraction with an exponent; the reproducer is
   `problem_3_dd_zero_fraction`.  The second is a bare `*, X` taking the
   dds of its symbol, C22-6578 p.30 comment (c); the reproducer is
   `problem_3_bare_op_symbol_dds`.  The host STRAP II assembles both.
3. **A fault in the book.**  Problem 3.4's M+ leaves the accumulator
   unchanged, so the closing multiply takes the wrong value.
4. **MODEL FAULT, FIXED 2026-11-16.**  A floating-point operand at
   address 8 took its sign from accumulator bit 60 instead of the sign
   byte, on fetch and on store.  This is against Reference Manual p.80.
   The reproducer, `problem_3_fp_address_8_sign`, is registered and
   passes.
5. **UNSETTLED.**  A normalized ADD whose sum is non-zero only in the
   low 48 bits.  The model normalizes it.  Manual pp.82 and 87 say the
   result is a zero.  C22-6578's own comment (b) agrees with the model,
   and its comment (a) agrees with the manual.  The reproducer is
   `problem_3_fp_add_low_half_zero`, and `jb_af1c` is the third witness
   to look in.
6. **MODEL LIMITATION, LIFTED 2026-11-16.**  A VFL store into the
   indicator register, word 11, was dropped silently (a documented
   simplification in `StretchStorage.bsv`).  It now lands in bits 20-63
   as Reference Manual printed p.37 says.  The reproducer,
   `problem_3_vfl_store_to_indicators`, is registered and passes.

**Two of the page's claims about its own programs are pinned and hold
on the model:**

* Problem 3.9's p.34 counter-example: Method 2 calls the smaller number
  high.
* Problem 3.7's "round-off error in the last iteration".

**Held-back checks, restored 2026-11-16 with the two fixes:**

* Problem 3.8's 27 checks on signed data.
* The four 3.9 indicator words.

Both are ordinary checks in `tests/run_tests.sh` again, and pass.

Chapter 4 ("Special Problems", printed p.35 on) has not been started.

# >>>>>> G2.1, CHAPTER 4, 2026-11-15: THE LAST CHAPTER, FROM ITS LAST PROBLEM BACKWARDS <<<<<<

`C22-6578`'s contents page (PDF 4) lists four chapters and eight
appendices: 1 Instruction Arithmetic Unit Instructions (1.1-1.9),
2 Variable Field Length Instructions (2.1-2.12), 3 Floating-Point
Arithmetic (3.1-3.10), 4 Special Problems (4.1-4.13).  There is no
Chapter 5, so this batch is Chapter 4 taken from 4.13 towards 4.1.
The counts above are not edited; this section adds to them.

**4.11 was built first because 4.12 and 4.13 both call it** ("Assume
the existence of the previous exp (x) program", printed p.46).

**How a floating result is checked here, and what that does not pin.**
There is no independent bit-exact model of the 7030's double-length
arithmetic in the project, so a result word is compared with the real
number the page defines, within a bound derived from the printed
program, not with a word (`tests/verify_problem_4_fp.py`).  The
measured floor is in each deck: 4.11 catches a coefficient wrong by one
part in 1E10 and passes one wrong by one part in 1E13.

**Assembler refusals the chapter runs into**, each with a reproducer and
held by `tests/check_problem_4_dd_refusals.py` (8 checks): arithmetic in
a DD(N) entry, `$N`/`$PI`, a zero DD(N), and `*` in an address (the last
is G3.1).  `docs/NEXT.md`, "G2.1 CHAPTER 4: WHAT THE ASSEMBLER REFUSES
IN A DD(N)".  The decks run on marked substitutes.

## The problems, in the order run

### 4.11 EXP, printed pp.45-46 -- `decks/problem_4_11.strap` -- PASSES as the model stood

11 exact checks and the PC, 12 within-bound checks
(`tests/verify_problem_4_fp.py 4.11`).  Exercises `KMG`, `D*`, `D+`
normalized and unnormalized, a signed VFL `ST` out of a floating
accumulator, `SHFL`, `*`, `E+`, `LA(U)` on `$L`, and two connectives on
the accumulator's exponent bits, in one printed subroutine.  **No wrong
result.**  Three printed errata (a factorial with a zero too many, a
missing comma, an offset one short of the bit its comment names) and one
unstated loss of accuracy (1.39 |x| units, 847 measured at x = 709), all
in the deck's header and in `NEXT.md`.

### 4.12 transcendental function, printed pp.46-47 -- `decks/problem_4_12.strap` -- PASSES as the model stood

2 exact checks and the PC, 6 within-bound checks
(`tests/verify_problem_4_fp.py 4.12`).  f(pi) = 2x e**(e**-x) /
sqrt(1 - e**-x) = 6.7071807483152..., read from `$L` and `$SB` where
the printed `BEW` leaves it: 2.31 units from the program's own number,
2.14 from the page's.  Adds to 4.11: `LN`, `E+I(U)`, `+`, **`SRT(N), $L`
-- STORE ROOT whose storage operand is the accumulator's left half** --
and `R/`.  **No wrong result.**  The page's comment (d), that it and EXP
assemble together with "no multiply defined symbol", holds.  One
uncertain reading, in the typeset formula only (an e with a bar over
it, read e**-x from the program and from 4.13).

### 4.13 numerical integration, printed pp.47-51 -- `decks/problem_4_13.strap` -- PASSES as the model stood

9 exact checks and the PC, 2 within-bound checks
(`tests/verify_problem_4_fp.py 4.13`).  The book's last and largest
program: MAIN, the 8-point Legendre-Gauss subroutine LEGQ8, the
integrand SUBR and EXP, about a hundred printed statements, assembled
together.  ANS = 2.72454650263143, 2.11 units from the rule worked from
the page (2.72454650263141, 3.11 units, since 2026-11-16, when the printed
`DD(N), 1.0` is assembled as STRAP II makes it, one unit below 1).  Adds: **a `SIC, SUBR; NOP` word used as data, read by `LVE`
and stored by `SVA` into two branches (self-modification, both words
read back)**, `LFT` with `*N+` and `*+`, `SRD`, `SLO` with a sum kept in
two words, `D-`, `E-I(U)`, `*N`, and three levels of `$15` linkage.
**No wrong result.**

* **A misprint in the ink**: `LEGQ8X`'s fourth abscissa is printed
  `.18343 46434 95650`; the Legendre-Gauss node is `.18343 46424 95650`.
  Run as printed.  It is worth 5.3E-11 in the answer and the check
  follows it (the expected value is computed from the nodes as
  assembled); correcting it moves the model's ANS and the expected value
  together.
* **`SRD` is built.**  "G2.3 The arms still refused" above lists it; it
  ran here.  `bsv/README.md` already says so.
* What is checked is the 8-point RULE, 2.724546, not the integral,
  2.723620: the integrand goes as sqrt(x) at 0.

### 4.10 natural logarithm, printed pp.44-45 -- `decks/problem_4_10.strap` -- A MODEL BUG, FIXED 2026-11-16

**FIXED 2026-11-16: all six arguments pass, and `--known-wrong` is off.**
The record of the find follows.

Run at six arguments (`tests/verify_problem_4_fp.py 4.10:<x>`), 2 exact
checks and the PC plus 4 within-bound checks each.  **x = .75, 3, 1E6
pass; x = 2.5, .001, 1E-300 fail the three series checks and nothing
else.**  Cause, decided from the Reference Manual: location 8 addressed as
a floating-point operand must carry `$SB` bits 4-7 as its sign (printed
p.37); the model uses word 8's bits 60-63, so `*(N), $L` squares a
negative Z to -Z**2.  Reproducer `decks/repro_fp_operand_location8.strap`;
`docs/NEXT.md` "LOCATION 8 AS A FLOATING-POINT OPERAND".  The three
failing runs are registered `--known-wrong` (they pass only while exactly
those checks fail).  **It is the first wrong result in anything the
model executed from `C22-6578` since the table above's one bug find,
through the nine problems of Chapter 1 ("G2.1, THE FIRST BATCH") and
4.11-4.13.**  Also exercises `F+`/`F-` (add to fraction), `/`,
`L(B,12,1)` and `-I(BU,1)` turning a floating exponent into a VFL integer
and back -- all right.  A fourth printed erratum: sqrt2 printed
1.41421356205080.

### 4.9 cosine, Method 1, printed pp.42-43 -- `decks/problem_4_9_method1.strap` -- BOTH LOCATION-8 BUGS

**SETTLED 2026-11-16: THE PRINTED `SRDN,$L` IS THE VFL SRD, AND THE BOOK'S
COSF IS WRONG IN THE INK.**  C28-6129 printed p.10 gives `$L` the dds
(BU,64,8) and printed p.6 says the dds picks the class;
`tests/check_srdn_dollar_l.py` pins both assemblers.  At offset 0 it "is
equivalent to a STORE" (Reference Manual printed p.64), so word 8 gets
word 9.  With the VFL SRD built, `4.9m1` checks that (word 8 = word 9,
TEMP, x2) and `4.9m1fp` the card with `SRDN(N)` (the cosine, read as the
accumulator, and `$SB` 4-7): five arguments each, all pass, no
`--known-wrong`.  Method 2 on the same page prints `SRD(N), $L`, with the
floating dds (its section below), which is the page's own evidence that
Method 1's dds-less card is the slip.

**CORRECTED 2026-11-16.**  The operand bug is fixed, and x = -.1's
`TEMP_A_squared` passes.  The "lost store" was not a store into location
8.  The printed `SRDN,$L` has no dds, so both assemblers compile it as
the VFL STORE ROUNDED (code 101101), by C22-6578 printed p.30's rule: "An
operation which could be either VFL or floating-point is assumed VFL".
The model does not implement that operation, and it turns OP on.  The FP
`SRDN(N), $L` stores into location 8 correctly since the fix.
`repro_fp_store_location8` now pins that form.  The W8 checks stay
`--known-wrong` while this is OPEN (docs/NEXT.md).  The record of the
find follows.

`tests/verify_problem_4_fp.py 4.9m1:<x>`, six arguments run, four
registered (five since 2026-11-16: `1X-2` and `.125`).  `D*(N), $L` squares a negative A to -A**2 (the operand bug of
4.10), and `SRDN,$L` -- a STORE into location 8 -- is lost, leaving the
accumulator's own bits 60-63 where p.96 stores the sign and flags (second
reproducer `decks/repro_fp_store_location8.strap`).  Only x = .125
passes, and by luck -- and since 2026-11-16 only when written `1X-2`,
exactly 1/8: `.125` as STRAP II assembles it is one unit low and fails
like .1 (registered --known-wrong; NEXT.md "DD(N) 1.0 IS 1 - 2^-48").  Erratum: the statement says "Create 2 pi x" for
"cos 2 pi x".  Method 2 (printed p.43) was set aside here as having
"the same `D*(N), $L` and `SRDN, $L`"; **read at 300 dpi 2026-11-16 its
last store is `SRD(N), $L`, with a dds** -- the floating store, run below.

### 4.6 8 x 8 bit transpose, printed pp.39-40 -- `decks/problem_4_6_method{1,2,3}.strap`, `problem_4_6_method3_n5.strap` -- PASSES as the model stood

Three methods, four runs, every word worked by hand in the deck headers
(9, 7, 7 and 7 exact checks and the PC), **assembled by the host STRAP
II** (`ASM=strap2`): Method 3's `SF(BU,N*N,N), LOC` is printed with the
page's own remark that STRAP II multiplies in the data description, and
strap2 does (the same word as `SF(BU,64,8)`), so no card is substituted.
Method 1 exchanges single bits with `LF`/`SF` (C0011/CM0101) under
`(V+ICR)` and `V+C`; Methods 2 and 3 OR eight one-bit bytes a row into
the accumulator (`C0111(BU,8,1)(V+IC)`, offset indexed by half words in
`$2`) and store the right half.  Method 3 also runs at N = 5, the page's
"or any integer not exceeding 8": `SF(BU,25,5)` truncating 8-bit result
bytes to 5 (Reference Manual printed p.75), with the word's other 39 bits
untouched.  **No wrong result, no printed erratum.**  Two readings: the
connect is printed `C0 111` in Method 2 (both assemblers squeeze the
blank to the same word), and Method 1's `N($3)` is right as printed (an
integer in a 24-bit VFL address counts bits, C28-6129 Section I printed
pp.8-9).

### 4.7 64 x 64 bit transpose, printed pp.40-41 -- `decks/problem_4_7_method{1,2}.strap` -- PASSES as the model stood; Method 2 is wrong AS PRINTED

`tests/verify_problem_4_matrix.py`, three runs, each the 64 rows, the
index words and saved index cells, the accumulator, guards and the PC,
worked from the data and the statement, not the model.  Method 1 is 4.6
Method 1 with N = 64, as the page says (2016 bit exchanges).  Method 2
transposes 8 x 8 blocks in the accumulator; the column block's connect
at offset 71-r runs past the accumulator's left end, which the model
handles as the partial-field rule says (printed p.76).  **Two printed
errata in Method 2**: a comma for a semicolon (STRAP II refuses the card;
supplied), and **`XW2 XW,LOC,7,XW222`: `$2` counts 7 and is stepped 8
times a block**, so it is refilled a row early and 1500 of the 4096 bits
come out wrong.  Run as printed (checked against a trace of the printed
statements, which the verifier asserts gives the transpose with 8; the
model matches it word for word) and corrected (the transpose).  **No
model finding.**  `docs/NEXT.md`, "PROBLEMS 4.6-4.8".

### 4.8 product of square matrices, printed p.42 -- `decks/problem_4_8.strap` -- PASSES as the model stood; wrong AS PRINTED

`tests/verify_problem_4_matrix.py 4.8`, two runs, 64 elements, `$2`-`$4`,
XW22, guards and the PC each.  `LFT(U)`, `*+(N)`, `SRD(N)`, `DL(U)`,
`CBR+`, `CB`, and `V-ICR,$3,N*N-1.0` and `DD(N),0` assembled as printed
by strap2 (strap_asm refuses both; the earlier Chapter 4 decks
substituted).  L and R are small integers, so every element is an exact
word.  **Printed erratum: `V+I,$3,N` and `V+I,$2,N` advance N half
words, not N words** (C28-6129 Section I printed pp.8-9), so the printed
program forms sum Lw[4i+k] Rw[j+4k] and 63 of 64 elements are wrong; it
is self-consistent because `N*N-1.0` is also counted in half words (31.0).
Run as printed (the model matches the trace) and corrected (L * R).
**No model finding.**  Assembler side: `repro_address_multiply.strap`'s
header said `N*N-1.0` assembles to 63.0; it is 31.0, and strap2 agrees.

### 4.5 scalar product of compressed sparse vectors, printed pp.38-39 -- `decks/problem_4_5.strap` -- PASSES as the model stood; wrong as printed when x_1 y_1 is non-zero

**The first printed program to index a field LENGTH.**  `LF(BU,25),
$LZC-0.2,128-25; LV,$1,8.0` puts the left-zeros count at `$1`'s value
bits 2-8, and the second I field adds index bits 3-18 to instruction
bits 35-50 (Reference Manual printed p.56), so `CT0011(BU,0),XBMAGE,
0($1)` takes the count as its length; `LV,$2,7.32; V+,$2,18.0` turns the
all-ones count, at the half-word bit, into a word index.  The double sum
keeps its low half in the accumulator across `L(U),PRODT` (p.88, bits
60-127 not changed), and the data makes that low half carry ~32 bits, so
words 8 and 9 are checked as well as PRODT.  `tests/verify_problem_4_matrix.py
4.5`, `4.5n37`, `4.5k0`: 13 checks and the PC each, worked by a trace of
the printed statements asserted equal to the exact sum of x_k y_k, all
assembled by strap2 as printed.  **No model finding**: N = 40 and N = 37
pass, KEYVEC left with the last common bit, location 7, $1-$3 restored
from sentinels.

* **Wrong as printed when x_1 and y_1 are both non-zero** -- a case the
  page does not exclude, not a misprint.  `$LZC` = 0 makes the indexed
  length 0, which is 64 (p.56): both CT0011 count the whole image words,
  and `CM0000` at `KEYVEC+0.1` clears 64 bits, bit 0 of SAVEX ($1's saved
  value) included and KEYVEC's bit 0 not, so every pass finds k = 0
  again.  Run as `4.5k0`: the program forms one wrong product ten times
  (-1006433504772300 for the statement's 1185029187485492); the model
  matches the trace word for word, the crossing CONNECT TO MEMORY
  included.  No correction supplied.

### 4.4 compression of a sparse vector, printed pp.37-38 -- `decks/problem_4_4.strap` -- PASSES as the model stood

`tests/verify_problem_4_matrix.py 4.4`, 33 checks and the PC: the 24
SVEC words, $1-$3, location 7, words 8-10, guards, worked from the
statement.  One image bit at a time by `C0011(BU,1)(V+IC),0.01($1)` and
RZ; `LWF(U)`/`ST(U)` move each kept word whole -- the data has the three
flags in several combinations and two unnormalized fractions, so a
plain `L` (flags to zero, p.88) would show; `STORE ZERO` (p.31) and `CB+`
over the rest.  `END` as a location-field label assembles under strap2.
**No model finding, no printed erratum.**  Unexcluded case, not run: a
dense vector leaves `$3`'s count 0 at END, so `CB+` counts it to 2**18-1
and Z stores past the vector.

### 4.3 bit image of a sequence of numbers, printed p.37 -- `decks/problem_4_3.strap` -- PASSES as the model stood

`tests/verify_problem_4_matrix.py 4.3`, 9 checks and the PC: BIMAGE,
$1, $2, location 7, words 8-10, guards.  `L(U)` and `BZRZ` decide what is
zero, and the Reference Manual says a zero FRACTION (printed p.85, "RZ
is turned on for all zero result fractions"; p.88, LOAD's indicators "as
in ADD"): the data has seven zero fractions that are not zero words
(an exponent, a minus, flags, all three) and twelve non-zero words
including a fraction of 1 and exponents of +-1000.  `CM1111(BU,1)(V+I)`
sets the bit; BIMAGE starts all ones so `Z, BIMAGE` is seen; word 10
shows `L` (not `LWF`) zeroing the flag bits.  **No model finding, no
printed erratum.**

### 4.9 cosine, Method 2, printed p.43 -- `decks/problem_4_9_method2.strap` -- PASSES as the model stood; one printed erratum

cos pi x by the series to K = 12 in x**2, then `D*(N),$L; E+I(U),1;
D-(N),WON`: 2 cos**2 - 1.  **Its last store is printed `SRD(N), $L`,
with a dds** (Method 1 prints `SRDN,$L`, the VFL form): the floating
store into location 8, so Method 2 does not wait on the VFL SRD.
Assembled by strap2 with KONST's `$PI/12*$PI/11` ... and `WON DD(N),
1.0` as printed (every KONST word truncated, under one unit; WON is
1 - 2**-48).  `tests/verify_problem_4_fp.py 4.9m2:<x> DECK ASM=strap2`,
five arguments in the statement's -1/8..1/8 (1X-2, -1X-2, .1, -.1, .03):
2 exact checks ($2, $SB plus with no flags) and the PC, 4 within --
TEMP 1 unit, the answer (word 8 with $SB's sign, p.80) 4 units from the
program's own number, and from the page's exact series and from cos 2 pi
x by a bound worked from the deck as it stands.  Model 0.17-2.26 units
from the program, 2.61-6.99 from cos; the series cut is .02 units at
x = 1/8, so "terms up to K = 12 would be adequate" holds.  **No model
finding.**

* **Printed erratum: `E+I, (U), 1`.**  STRAP II refuses it (message 40,
  EXTRA FIELDS: the dds stands as a field after the comma); supplied
  `E+I(U), 1`.  The earlier "refused by strap_asm (undefined symbol U)"
  is the same card.
* Reading: `KONST($ 2)` has a blank in the ink; strap2 makes the same
  word as `KONST($2)`.

## Where Chapter 4 stands, 2026-11-16

Run, newest last: 4.11, 4.12, 4.13, 4.10, 4.9 Method 1, 4.6 (three
methods), 4.7 (two), 4.8, 4.5, 4.4, 4.3, 4.9 Method 2.  **Two model bugs, one cause (location 8 as a
floating-point operand and as a store), both FIXED 2026-11-16; the
"lost" 4.9 store was the VFL SRD, see above; four assembler refusals,
ten printed errata, and two unexcluded cases (4.5 with k1 = 0, 4.4
with a dense vector).**  Not reached: 4.2 (decimal VFL, refused), 4.1
(VFL square root).  The note that the second
I field is "decoded and read NOWHERE" (above, "(b)") is out of date:
`vflSecondIndex` (`StretchExecute.bsv`) indexes length, byte size and
offset as one field, and 4.6 Methods 2-3 and 4.7 Method 2 ran on it
(offset indexing by half words, `0($2)`, `7($3)`, `64-8($3)`); 4.5, the
first printed program to index the field LENGTH, ran on it too.
