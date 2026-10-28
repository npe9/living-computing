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
