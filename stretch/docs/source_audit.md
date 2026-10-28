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

### Two edition-confusion bugs to fix

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
