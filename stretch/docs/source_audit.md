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
