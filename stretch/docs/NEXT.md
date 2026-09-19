# What to do next, and why

A standing work queue for the Stretch model, ordered by dependency.
Written so the next session starts from a decision rather than a
survey. Detail for every item is in `docs/microarchitecture_plan.md`;
this file is the plan, not the record.

## The bar

Two standards, and every test says which it meets:

* **Transcription** — a listing row checked bit-exactly by a verify
  script. The strongest oracle here.
* **Manual-derived** — hand-written from a primary source, stated as
  the weaker standard in the program's own header.

And one rule that outranks both: **a green test is only evidence about
faults its inputs could have made visible.** Every new test gets an
injection that must fail, at a named address, in *its own* check.

## 1. Storage protection (blocked on a refactor — do this first)

`bsv/StretchExecute.bsv` reaches `st.writeWord` from **64 call sites**.
Protection needs one place that both suppresses the store and reports
it, because the execute stage owns the single per-instruction write to
`indicators`. A DWire from storage does not schedule: bsc pulls the
read into the rule predicate and it conflicts with the write (G0004,
confirmed with `-show-range-conflict`; `schedule (writeWord) SB (...)`
does not parse in this bsc).

**The refactor**: route all 64 through one execute-side helper —
an `ActionValue#(Bool)` returning whether the store was suppressed —
so the indicator decision happens where `ind` lives.

Then the behaviour, all sourced:

* Enable bit: BE sets, BD clears, BEW sets; unconditional, before the
  branch (p.40). Reset = disabled (p.53).
* Locations 1, 2, 3 are permanently protected regardless of the
  boundary registers (p.31). 0 and 4–31 never signal.
* A protected **store** always suppresses and raises DS, with no
  mask-dependent branch, because DS is permanently masked on (p.32).
* All of it gated on the enable bit (p.45).

**The test already exists in the decks**: SSIP's SIP16
(`programs/ssip_sip17_reset.strap`) writes words 1, 2, 3 and 12, and
the deck guards it with a `BD` commented *"disable before reset of
protected area"*. It must succeed disabled and be suppressed enabled.
Deck-derived, not hand-written.

Do **not** add the enable bit alone: nothing observes it, so it would
be untested state.

## 2. The interruption mechanism

Spec with verbatim citations: see the interrupt section of
`microarchitecture_plan.md`. Mask (word 12) and the boundary registers
already exist as storage; the IAR is word 2.

Order: leftmost actuated masked indicator's number N → turn that
indicator off → EIA = IAR + N → fetch and execute **one** instruction,
instruction counter **not** stepped. Enable bit gates everything.

Known gap: neither SSIP nor the DCP ever *provokes* an interruption —
both are harnesses that start disabled. Provoking code lives in the
per-device tapes (`jb_af1c`, `ja_ax1a`). Scout there before writing
hand-written tests.

## 3. Standing practice, after every batch

`python3 strap/mutation_score.py` — it refuses to run on a dirty tree
or a non-green baseline, and restores on signal. Read **where** and
**how fast** each mutant was caught, not just the count: a catch far
from its own subsystem is a near miss, and it is how the flag/count
confound surfaced.

Triage survivors into *missing test* / *equivalent mutant* / *expected*
before writing anything. `ad-bound-off-by-one` is the one documented
expected survivor.

## 4. Deferred, each its own piece of work

Decimal VFL (`c=1`) and radix conversion; `EX`/`EXIC`; `RNX`/`LVE`/
`LVS`; Transmit backward/`SWAP`/multi-word; I/O chaining and multiple-
block; `LOC` and the unimplemented `CTL` function codes; channel status
reaching the CPU indicators; the interval timer actually ticking.

Out of scope by design: cycle-accurate timing.

## 5. Open questions — record, do not guess

* `BR`'s **absolute value** clause is unexercised: an effective address
  can only go negative through index modification, and `effAddr19`
  carries no sign beside its result.
* R/'s ZM clear may be **unreachable** (the divisor is the accumulator,
  which a ZM-setting multiply leaves at zero). Only FP paths were
  checked.
* `ja_ua1_ssip` has a full listing at **PDF pp.7–52**, 1-up fanfold
  with no printed page numbers — cite by PDF page.
  `docs/archival_inventory.md` implies prose-only and needs correcting.
* Reference Manual **PDF page = printed page + 3**.

## Traps this project has paid for

* A bare `*` or `L` assembles as **VFL**, not floating point. Write
  `*(N)`, `L(N)`.
* Give any data section an explicit `SLC`: `DD` emits at the location
  counter, so growing the code silently overruns its own constants.
* Compute octal addresses with a helper. Every one written by eye in
  this project has been wrong.
* Never edit a file while a suite or campaign is reading it.
* A verify script cannot tell you a **label** is on the wrong row: it
  checks what a symbol resolves to, and a misplaced symbol still
  resolves.
* When a rule has more than one implementation, each copy needs its own
  witness. Three instances so far: `effAddr18/19/24` (3 copies), the
  SEOP rule (6), ZM's clear (16).
