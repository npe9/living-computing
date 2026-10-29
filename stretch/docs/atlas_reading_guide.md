# How to read Perf. Char. Vol. 2's atlas — the authors' own notes

**Written 2026-10-29, after discovering that the atlas's divide pages
cannot calibrate a divide.** `docs/microarchitecture_roadmap.md` M1 and
M2 both name Vol. 2's per-instruction atlas as THE oracle — "this is
where the atlas becomes the oracle", with M2's correctness "measured by
how much of the residual it closes". That is right in general and
WRONG FOR AT LEAST ONE OPERATION, and the volume says so itself on
pages nobody had read as a set.

Vol. 2's methodology and commentary pages are **PDF 110-116** (cite Vol.
2 by PDF page — see the offset table). They say what was measured, with
what operands, and which results the authors consider invalid. Read
them before using any column.

## >>> THE OPERANDS ARE NOT GENERIC, AND FOR SOME INSTRUCTIONS THEY ARE DEGENERATE <<<

PDF 113, verbatim:

> *"A standard operand (444 ..... 4)₁₆ was used for both binary and
> decimal type operations."*

with named exceptions, each chosen to exercise a particular path:

| instruction | what was actually fed | why, in the authors' words |
|---|---|---|
| `+` | accumulator a low-order +1, memory operand +(444…4)₁₆ | *"to provide for continual recomplementation where the sign of the instruction was inverted (subtract)"* |
| `M+` | accumulator +(444…4)₁₆, memory operand **+1** | *"again to provide for recomplementation"* |
| `*`, `*+`, **`/`** | accumulator and factor the standard operand, **memory operand +1** | *"to provide some control of the data during repeated execution"* |
| `CV`, `DCV` | accumulator +1 at offset 20 | so a double convert's result stays legal decimal |

**So the divide pages divide by ONE**, and then, under repeated
execution, by zero — which is the other half of the story:

> PDF 114: *"For divide, \*24\* shows a zero divide condition. Again it
> was probably generated during the course of repeated execution."*
>
> PDF 115, note 8: *"The error marks on divide instructions (pp. 127,
> 154, 177) are due the use of a zero divider."*

A zero divisor takes Table 2's short path — 3 pre-execution + 2
execution cycles "instead of previous" — so **the reduction loop never
runs on the pages that are supposed to measure it.** PDF 41 says the
same thing outright: *"The present measurements for /, D/ and R/ do not
give a realistic timing… The average divide time should be about
10 µs."*

## THE "INDEXING" COLUMNS DO NOT TEST INDEX ARITHMETIC

PDF 113:

> *"The columns are then repeated for the case of operand indexing.
> Here the effective address was modified by an index register
> **containing zero**."*

So those columns measure the indexing PATH's cost, not the effect of an
index value. A model whose indexed and unindexed timings differ only by
the path will match them, and that is not evidence the index arithmetic
is right.

## THE THREE RUNS, AND WHAT "FORWARDING" MEANS HERE

PDF 114 describes three passes over the VFL set:

* **NO FORWARDING, DIRECT ADDRESSING** — operands cycle through four
  consecutive locations, `(150000.0)₈ … (150003.0)₈` then back,
  *"to provide maximum speed benefits from the STRETCH memory-box
  configuration"*. For I-box operands, `$X0…$X3`.
* **FORWARDING, DIRECT ADDRESSING** — one fixed location, so
  look-ahead can forward level to level.
* **IMMEDIATE ADDRESSING** — the to-memory instructions are omitted,
  being undefined for immediate operands.

PDF 115 note 5 defines the word: *"'forwarding' is being used in the
same context as for floating point instructions, meaning IDENTICAL
OPERAND ADDRESS."* Not a general bypass — the same address.

## THE COMMENTARY, WHICH IS A SPEC FOR M2

PDF 115's eight numbered notes are the most directly usable
look-ahead statements in the volume:

1. *"All VFL instructions require an operation code LA level."*
2. *"All VFL 'to memory' operations require memory fetches."*
3. *"The number of LA data levels are DOUBLED whenever word boundary
   crossover is present."*
4. *"VFL stores with word boundary crossover involve a 'sequential
   store' situation. The second store level cannot be loaded into LA
   until the LAAR is no longer busy processing the first store level."*
5. forwarding = identical operand address (above).
6. *"Actual fetch-type forwarding action is possible only for
   consecutive fetch-type VFL instructions with no word boundary
   crossover."*
7. *"'Store-close-to-fetch' forwarding is present for consecutive 'to
   memory' VFL instructions with no word boundary crossover."*
8. the divide error marks (above).

Note 3 independently corroborates Table A-2's doubling rule, which
`docs/NEXT.md` already records. **Notes 4, 6 and 7 are interlock and
forwarding rules stated in prose**, and M2's plan currently derives
forwarding from the CE pages alone.

## BRANCHES: WHAT "SUCCESS" MEANS IN THOSE COLUMNS

PDF 111:

> *"'Consecutive' means that each instruction called for a branch to
> the next instruction. 'Non-consecutive' means that the branch was to
> a location from one to four instructions from the one being
> executed. For CBR type, the 'success' refers to a SUCCESSFUL REFILL
> in which the register is refilled with its original contents. A one
> was in the count field. For an unsuccessful CBR the branch was
> unsuccessful and thus no refill. The original count in the count
> field in this case was greater than 10,000."*

So a "successful" CBR column is count = 1 with a refill, and an
"unsuccessful" one is count > 10,000. Comparing a model's CBR against
either column without matching that count is comparing two different
operations.

## THE RULE THIS ESTABLISHES

> **Before calibrating any box against an atlas page, read the
> methodology for that instruction class and check what operand was
> fed.** The authors flagged the degenerate cases; the flags are in the
> notes pages, not on the data pages, and a column of microseconds
> carries no warning on its face.

The remaining classes — floating point, index, branch, I/O — have their
own methodology pages in the same range and have NOT yet been read with
this question in mind.
