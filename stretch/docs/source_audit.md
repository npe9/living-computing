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

### `C22-6729` carries a COMPLETE FORMAL GRAMMAR of STRAP II's expression language

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

**G2.2 Buchholz Appendix B** adds six more worked programs, independent
of `C22-6578`.

**G2.3 The arms still refused.** `SRD`, the decimal VFL set, `SWAP`'s
remaining variants. `storeTarget`'s invariant names the ones that will
need a case when they land.

## G3 — Assembler completeness, from `C22-6729`'s grammar

**G3.1** Implement what Appendix C encodes and `tokenize_expr` does not:
`*`, `/`, parentheses, and `**` (noting App. C's 3-bit operator field
has no free code for `**`, which is unresolved). STRAP-1 forbade
parentheses, so scope the change to what the project targets.

**G3.2** Replace `eval_addr_field`'s per-call-site `unit_shift` with
printed p.144's rule -- scaling by the operand's **function** -- and
test it against the listing oracle.

**G3.3** The numbered error-message list (printed p.177) is a rule book
with a column `C28-6129` lacks; it fences `(.n)` behaviour with six
specific errors.

## G4 — Verification infrastructure

**G4.1 Write the atlas oracle.** `run_tests.sh:3057` has said Perf.
Char. Vol. 2's per-instruction atlas is the real timing oracle and that
`perf_char_timing.py` is "shaped for" it. It is still not written, and
**M2's correctness is defined as how much of that residual it closes**.

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
