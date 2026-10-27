# Getting it right microarchitecturally: a staged plan

**Target, stated 2026-10-26: a structurally faithful register-transfer
model.** `docs/structural_audit.md` says what is missing. This says in
what order to build it, and — the part that matters — **how each stage
is checked**.

## The organising principle: build what you can check

The ordering below is by ORACLE AVAILABILITY, not by architectural
layering. The reason is a measurement from 2026-10-26:

> `eboxClocks` charged every floating-point instruction three clocks
> for as long as it existed — a `SRT` cost the same as a load. Of
> **5,540 checks, exactly one noticed**, and only by running out of
> its step cap. The `jb_af1c` decks exercise floating point hard but
> assert VALUES; MCP's bootstrap contains ONE floating-point
> instruction, in the unchanged class.

A stage with no oracle is a stage whose bugs survive. So the harness
comes first, and each stage after it must move a number that someone
measured in 1961.

## M0 — the measurement harness. Before any structure.

**`CYCLES<=` is a one-sided bound** (nine decks use it) and cannot
detect a model that is too FAST, which is what every missing-overlap
error looks like. Needed instead:

* `CYCLES=n±tol`, and a report of the measured figure on pass as well
  as fail, so a drift is visible before it crosses a threshold;
* a **single-instruction harness** that runs one operation in a loop
  and reports microseconds, comparable directly against Volume 2's
  per-instruction atlas. `tests/perf_char_timing.py` already holds the
  transcribed tables and self-tests against them.

**Make the accidental oracle deliberate.** `ce_vol2_sqrt_check.strap`
caught the flat-3 bug by exhausting its step cap. That is a tripwire,
not an oracle. Give the decks that execute expensive arithmetic an
explicit cycle assertion.

**Deliverable:** a failing test. Pick one atlas page, assert the model
against it, and let it fail by the known offset. Nothing below is
verifiable until something fails for a reason you can name.

## >>> ORDERING CORRECTED, 2026-10-26: M1 IS BLOCKED ON M2 <<<

This file ordered the datapath before the look-ahead. **That is
backwards, and it was tested.** The exact VFL timing formula —
derived from the manual and matching Vol. 2's cycle-exact page at 24
rows of 24 — was applied, and the MCP boot went from 22,048,336 steps
to 6,015,582 with twenty-six checks failing on a UNIT NOT READY
REJECT in the IPL's IO TEST.

**The surplus in the present timing numbers IS the overlap.**
`budgetClocks` feeds `ibusy`, which "covers the instruction's own
memory waits when memory is free". With no look-ahead, the memory
access hides inside the instruction's budget; the atlas's figures
were measured on a machine where the look-ahead covered it instead.
Cut the budget to the measured value and the read no longer fits.

So: **M2 first.** The timing arithmetic is already solved on paper
and recorded in `docs/NEXT.md`; it becomes applicable — and becomes
the test that M2 works — only once the overlap exists.

## M1 — the arithmetic datapath: A, B, C, D, X, Z, ADDER OUTPUT

**Why first among the structures:** the timing tables are conditional
on OPERAND VALUES, and `eboxClocks(DecodedInstr)` is never given the
operands. Table 2 adds cycles "for each additional pre-shift of 4",
"for each additional norm. of 6", "if recomplement is necessary"; the
divide loop is "data dependent". Table 3's COMMENTS column is the same
shape — `M+`: "Unlike signs AB > CD, add .6(x/y + 1)".

`StretchFP.bsv` already derives the shift and normalize counts to
produce the ANSWERS. The structural change is to make them available
to timing, which is the same change the working registers need.

**`ADDER OUTPUT` is bits 3-102** — a hundred-bit path, which is the
PAU's double-precision field (12-107) seen from the adder's end. Width
it from the index, not from the accumulator.

**Oracle:** Volume 2's atlas, per instruction. **Target:** close the
measured `VflInt` residual of 0.281 us mean / 1.20 worst.

**Expect a floor.** Part of that residual is missing overlap, not
datapath — see M2. Do not tune M1 past the point where the error stops
being structured; `docs/NEXT.md` records a rule that halved the error
and was rejected for contradicting printed p.3-10.

## M2 — the look-ahead. The largest absent structure.

46 triggers across 41 named fields. `docs/spec_lookahead.md` has the
design; four corrections from it belong here:

1. **Levels are per-instruction, and Table A-2 gives the counts** —
   FP 1-2, VFL 2-3 (doubled on word-boundary crossover, +1 for
   progressive indexing, 6 worst case), guessed branch 4, I/O 2,
   Transmit 2+N — and **every I-box instruction loads a level too**.
   That is what actually throttles the I-box.
2. **The machine compares against ONE address register and FORWARDS**,
   including fetch-to-fetch. The plan's conservative
   compare-against-every-earlier-level can only delay, never corrupt,
   so it is safe — but it is the wrong mechanism.
3. **Two LAARs, switchable, defaulting to one.** The CE pages showing
   two are stamped 2/1/62; every "+ LAAR" time in Perf. Char. Tables
   4-9 is stamped 3/8/61, measured on the one-LAAR machine. Run every
   published-timing oracle in the one-LAAR configuration.
4. **No source gives a per-action look-ahead cycle count.** The three
   CE figures whose titles promise timing name timers and print no
   durations. The implementable model is CONDITION-DRIVEN. Any
   LA-internal count written in Bluespec is invented and must say so.

> **>>> THIS IS WHERE THE ATLAS BECOMES THE ORACLE. <<<** Volume 2's
> numbers are THROUGHPUT over thousand-instruction sequences from the
> 1961 `GENER` simulator — measured on a machine WITH overlap. The
> model has none, so part of every offset is the missing look-ahead.
> **M2's correctness is measured by how much of the residual it
> closes**, and that is a far better test than any deck.

## M3 — memory and bus arbitration

Six memory units, interleaving, and a priority order quoted in
Buchholz: **exchange and disk synchronizer > CPU operand fetch
(look-ahead) > CPU instruction fetch**, eight channels; the E-box is
not a requester at all. The plan's "exchange > disk" ordering is
unsourced. `TR00.722`'s "IC controls have priority" is intra-I-box MAB
arbitration and must NOT be merged with the MBCU rule.

**Memory cycle is 2.2 us** (Perf. Char.), not the 2.1 in §A.7, which
matches neither source — Buchholz says 2.0.

**Oracle, and it is already in hand:** every atlas page has columns for
`EXTERNL OPERAND`, `INTERNL OPERAND` and `WB XOVR` — external versus
internal memory, and word-boundary crossover. Those columns measure
memory structure directly, and the model currently reproduces only one
of them.

## M4 — error detection. Last, and honestly.

A residue tree exists in hardware: `CD RESIDUE`, `RESIDUE OF AB`,
`GENERATED RESIDUE FIRST/SECOND LEVEL`, per-register `PARITY`
triggers. The model has none.

**It has no oracle and nothing needs it.** The indicators it would
drive — `EE`, `CS`, the data flags — are already recorded in
`StretchIO.bsv` as not propagated, pending the interrupt-enable state.
Build it when something asks, not to complete a table.

## The constraint that will bite: bsc scheduling

Six concurrently firing units with shared buses need **explicit
arbitration modules with single-writer methods**, not one big rule.
This is not hypothetical — on 2026-10-26 a two-line change that wrote
the accumulator sign byte twice in one rule was refused outright:

```
Rule `RL_rl_exec_resume' uses methods that conflict in parallel:
  st_accSignByte.write(...) and st_accSignByte.write(...)
```

`execute()` is ONE rule and `writeWord` is ONE method. Design the
buses as modules with single-writer methods from the start, and
expect to rediscover G0004 early in M2 rather than late.

## What stays out

**Gate level.** `R23-9732` references 1,993 logic pages and reproduces
about 285 lines of them; the ALD set is a separate document. The
delays it does print are sub-cycle — 580, 175, 150 ns against a 300 ns
clock — and a Bluespec rule firing IS a clock edge, so intra-cycle
delay has nowhere to live. See `docs/structural_audit.md`.
