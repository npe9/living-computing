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

## 1. Storage protection — DONE (2026-09-19)

Implemented and tested: `programs/storage_protection.strap`, three
injections, two-sided gating. The enable bit (BE/BD/BEW, p.40) and the
permanently protected locations 1–3 (p.31), with DS always suppressing
a store (p.32) and the whole thing gated on the enable bit (p.45).

**The "64 call sites" obstacle was not real.** 43 of them write a
*constant* special-register address — accumulator halves, sign byte,
zeros/ones counts, remainder, factor — all in words 4–31, which p.31
says never signal. Only the computed-address stores can land in the
protected area, and they share one predicate, `protViolates`. The
wire-from-storage design that would not schedule was never needed.

## 1a. The boundary registers — DONE (2026-09-19)

Extends §1 the same day; it does not supersede it. §1 is the
permanently protected words 1–3, this is the program-settable area.

`programs/storage_protection_boundary.strap`, seven injections. Word 3
holds the upper boundary in bits 0–17, the lower in 32–49 and the
control bit at 57 (p.31 — note that upper is named first and sits
lower in the word). The area is **half-open**, `[lower, upper)`; upper
≤ lower means an empty area and needs no separate guard.

**The control-bit polarity was never an open question.** This project's
plan carried “still to source from Appendix C” in two places; p.31 of
the same Reference Manual says it in one sentence — zero signals for a
comparand *inside* the area, one signals for a comparand *outside*. The
p.15 overview had been read and the operand-designation chapter twenty
pages later had not.

**The 0–31 carve-out gates the boundary compare, it does not sit beside
it.** Written as `permanent || boundary`, a set control bit makes words
4–31 — the special registers — signal, because they are outside every
area a program can name. Those are exactly the 43 constant-address
`st.writeWord` sites that go unguarded. The carve-out is what keeps
that argument true.

Still open here, and each is its own piece: **DF and IF** (both
mask-dependent, unlike DS), full operation **termination** (p.32
terminates the whole operation; this suppresses only the store, so a
`BB` whose write is suppressed still branches), and the **straddling
rule** (p.31: a field crossing a boundary always signals — this
compares one word address per store, not a field's extent).

## 1b. Original entry, kept for the reasoning (superseded)

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

`python3 strap/line_addresses.py programs/X.strap` prints the address
of every instruction line, in the listings' octal convention. Every
injection address a new test records should come from it, and it will
also reproduce the ones already recorded — which is what makes them
checkable rather than folklore.

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
* **A hang address read at the step cap is accurate to one half-word,
  not exactly.** A hang is a branch to itself, and the instruction
  counter oscillates between the branch's address and the half-word
  after it while it spins; the cap samples whichever clock it lands on.
  Measured on one mutant: caps of 30000 and 30001 report the half-word
  *after* the spinning branch, 30002 reports the branch itself. Every
  other injection recorded in `run_tests.sh` happens to sample the
  branch's own address, which is why this went unnoticed until an
  injection landed on the other phase.
* **Bit offsets are printed in octal and written in decimal.** The
  listings and every address in `run_tests.sh` use octal (`004107.40`
  is bit 32); a program's own source is decimal unless a `(8)` radix
  prefix says otherwise (`3.57` is IBM bit 57). Use
  `strap/line_addresses.py`, which prints the listings' convention, and
  do not convert either by eye.
