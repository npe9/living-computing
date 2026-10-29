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

---

# The other methodology pages, read 2026-10-29

The VFL section above was read first because the divide question
forced it. These are the rest, and two of them turn out to contain
ARCHITECTURAL STATEMENTS rather than only methodology.

## Floating point — PDF 40-41

**Method:** *"Sequences of operations were generated and timed by
GENER."* Simulator output, not hardware measurement — which the
project already records, and which these pages confirm in the authors'
own words.

**Data:** *"A normalized floating point one (1) was the initial operand
unless otherwise specified… The execution of large numbers of
consecutive operations caused a time increase due to shifting in some
cases (normalized add is one example). The addition of 10 thousand
ones involves preshifting and post normalization time."*

So the FP columns are **1 + 1 + 1 … ten thousand times**, with the
exponent climbing and dragging pre-shift and normalisation time in. A
model matching those numbers has matched that sequence, not floating
point in general.

**Operand placement:** external `100011₈`-`100014₈` without
forwarding, `1000011₈` with; I-box operands index registers 9-12
(9 with forwarding); internal always `$R`, the accumulator's right
half — and the authors note `$R` changing under successive double-length
operations *"introduced a large factor of time… by large exponent
differences"*.

### >>> TWO MORE CLASSES OF UNREPRESENTATIVE COLUMN <<<

**"To memory" operations are WORST CASE**, not typical:

> *"Repeated 'to memory' operations lead to queuing for the LAAR, and
> the present measurements on these instructions actually refer to the
> WORST POSSIBLE SITUATIONS, not often realized in actual practice."*

Named: `ST`, `SLO`, `SRD`, `SRT`, `D/`, `LFT`, `M+`, `M+MG`. Calibrate
a store against those pages and you have calibrated the worst case.

**And the forwarding columns contain almost no memory traffic at all:**

> *"Forwarding merely means using the same operand address. For
> fetch-type instructions, 'forwarding on consecutive fetch' actually
> occurs, and **only one true memory fetch is made for the entire
> sequence of 10,000 instructions**."*

One fetch in ten thousand instructions. Those columns measure a fully
forwarded pipeline; they say nothing about per-instruction memory cost.

## Transmit — PDF 105, and the model already agrees

> *"**LA is emptied before the actual transmission of information.**"*

**The model does this**, and did before the page was read: Transmit is
not `isEboxClass`, so it goes through `iboxHazard`, whose default arm
is `Bool h = True; // anything not listed (Transmit, I/O, EX...):
drain first`. An independent corroboration of existing behaviour.

(Operands: external in the two lowest memory boxes, internal at
`4.0`-`9.0`, index operands `$2`-`$14`, i.e. words 18-30.)

## Index arithmetic — PDF 108, and one REQUIREMENT the model does not meet

Statements about the machine, not the measurement:

* *"In SX, no memory fetch is necessary. This is not true for SV, SC
  and SR. This explains the large difference in timing."*
* *"All successful refill action requires memory fetches. All direct
  index arithmetic instructions except SX require memory fetches. **No
  memory fetch is required for immediate index arithmetic.**"*
* *"Concurrent E-box activity can overlap much of the I-box time. This
  is, of course, not possible if the LA is empty."*
* > *"**The RNX instruction requires the draining of LA.**"*

> **>>> THE LAST ONE IS AN OPEN REQUIREMENT. <<<** `iboxHazard`'s
> `DirIndex` arm — which is where `dixop_RNX` lands — does NOT drain:
> it waits only if a level holds the effective address, or the refill
> word for `V+CR`. RNX is unimplemented today (it reaches the DirIndex
> default and sets OP, the one entry still true on
> `StretchExecute`'s original scope list), so nothing is wrong now.
> **When RNX is built, `iboxHazard` needs a case for it**, and this
> page is the citation.

The fetch list is also a cross-check on `prepareExec`: these are
I-box-class instructions, so they do not go through `fetchesOperand`,
but "all direct index arithmetic except SX require memory fetches" is
the same kind of statement and should agree with whatever the index
arms do.

## Still unread

`INSTRUCTION SEQUENCE GENERATION AND TIMING` (around PDF 36), which is
GENER's own description and governs every number in the volume.

---

# GENER itself — PDF 37-39, and it bounds the precision of every number

`INSTRUCTION SEQUENCE GENERATION AND TIMING` describes the program that
produced the whole volume. It governs every column in it.

## How a number is made

1. **One instruction is replicated.** GENER takes the instruction at a
   location, ORs **two masks** into it, stores it, and repeats —
   *"This series is then reproduced until a thousand instructions are
   available"*. So a page's sequence is a THOUSAND COPIES of one
   instruction, varied only by the masks.
2. **A count branch closes the loop**: *"after which a count branch
   (with an original count of 10) is inserted"*, and *"this sequence
   is then executed 10 times"*. 1,000 × 10 = **10,000 executions**,
   which is the "10,000 instructions" the floating-point notes refer
   to.
3. **It is timed by the INTERVAL TIMER.** Figure 1's flow chart reads
   `SET INTERVAL TIMER TO 0.32 (1/1024 SECOND)` then `WAIT FOR TIME
   SIGNAL`, `EXECUTE SEQUENCE`, `MULTIPLY BY 100`, `CONVERT TO
   DECIMAL`.
4. *"the measured elapsed time is multiplied by 100 to produce the
   execution time for 1 million instructions; the seconds now indicate
   integer micro-seconds"* — so a printed figure is **µs per
   instruction**, extrapolated from 10,000 of them.

Branches are handled specially, the branch address being rewritten to
the loop's own location, *"which allows any instruction sequence to be
constructed and timed"*.

> **AND THE INSTRUMENT IS ONE THIS MODEL IMPLEMENTS.** The 1/1024-second
> interval timer that produced these numbers is the same timer
> `StretchCore`'s `rl_clock` steps through its exact-rational divider,
> and `decks/interval_timer_steps.strap` pins. The oracle and the model
> share a clock.

## >>> THE PRECISION BOUND, STATED BY THE AUTHORS <<<

> *"The results are calculated to two fractional positions and compare
> exactly to representative timings when the loop is actually executed
> one thousand times. **The last digit in each number may be in error
> by one unit.**"*

**So every figure in the atlas is ±0.01 µs**, and a model difference
below that is noise, not a discrepancy. Any calibration should carry
that tolerance explicitly — `docs/spec_timing.md`'s residuals (the
connective path's 2.40 µs offset, `VflInt`'s 0.281 µs mean) are far
above it and so are real, but a future box tuned to the third decimal
would be fitting the error bar.

And the preface says what the volume is: *"The following are
REPRESENTATIVE times of 7030 instructions. They will be updated when
more information becomes available."* Provisional, by its authors'
own description.

## What this adds to the per-class caveats above

Every figure carries **one count-branch per thousand instructions**
amortised into it, because that is how the loop closes. It is small —
a tenth of a percent — but it is systematic, it is in every number, and
it is part of the "constant offset expected" that
`docs/spec_timing.md` already records without a mechanism. Now there is
a mechanism.
