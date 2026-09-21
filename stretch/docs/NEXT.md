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

## 2. The interruption mechanism — DONE (2026-09-21)

`programs/interrupt_pg0.strap`, seven injections, one of which
**survived the first round and is why the program has a second block**
— see below. Spec with verbatim citations: the interrupt section of
`microarchitecture_plan.md`.

Implemented: leftmost actuated **masked** indicator's number N → turn
that indicator off → EIA = IAR + N **in words** → fetch and execute
**one** instruction, instruction counter **not** stepped. The enable
bit gates everything.

**Implemented but NOT witnessed**, and listed below rather than left in
that sentence: "the instruction counter can be replaced as the result
of a successful branching operation" (p.48). Both blocks of
`interrupt_pg0.strap` use an interruption instruction that falls
through, so the branch arm of `commitNext` has no test. An untested
path described as tested is the failure this project keeps a rule
about.
`StretchStorage`'s `intDueCalc` decides; `StretchCore`'s `rl_interrupt`
takes it; `commitNext` is the one place the counter is committed.

**A surviving injection is worth more than six caught ones.** Replacing
`indicators & mask` with `indicators` passed the whole first version:
the only indicator the program turned on was also the one it masked, so
honouring the mask and ignoring it give the same answer. The second
block leaves PG0 actuated and *unmasked* beside a masked PG2, so a
model ignoring the mask takes the further-left indicator and clears it.
This is the project's own rule — a green test is only evidence about
faults its inputs could have made visible — landing on a test written
by someone who knows the rule.

**A PROGRAM CANNOT POLL DS — and both storage-protection tests had to
be reworked to find that out.** DS is indicator 19 and mask bits 0–19
are permanently 1 (p.48), so the instant an *enabled* machine raises
DS it takes an interruption, and the mechanism turns that indicator off
before forming the address. By the time the next instruction runs, DS
is gone. `storage_protection.strap` and
`storage_protection_boundary.strap` both read DS directly with
`BZB,$DS,$` / `BZDSZ,$`, and both were green only because interruptions
did not exist; with the mechanism in, both ran away to address 0 —
interrupting to word 19 with the interruption address register never
set. Measured, not guessed: `n=19 eia=19 pc=4234`.

They now observe the violation the way the machine actually reports it,
through the routine at table entry 19, which makes them *stronger*
tests — they witness the suppression **and** the interruption that
p.32 and p.48 together require, where before they saw only a bit. It
is also why the decks poll indicators with the system disabled.

**The marker has to live in words 4–31.** p.31: locations "0 and 4
through 31, inclusive, never cause an address monitoring signal". With
the boundary control bit set, every address *outside* the monitored
area signals — so a marker in ordinary core would itself be suppressed,
raise DS again, and interrupt forever. Word 6 is in the carve-out and
cannot. That the carve-out is load-bearing here, for a second and
quite different reason, is worth noticing.

**A zero half-word decodes as `BE, 0`.** BranchOrMisc code 000 is
BRANCH ENABLED, so a machine that runs off the end of a program into
untouched storage *enables the interruption system*. That was always
true and never mattered; now it does. It broke the smoke test's RNX
check, which stepped 40 clocks and hoped. Anything that runs past its
own code can now take an interruption — worth knowing before writing
the next hand-written program.

### Still open here, each its own piece

* **A BRANCHING interruption instruction.** p.48: the instruction
  counter "can be replaced as the result of a successful branching
  operation", and p.48-49's correction-routine pattern is exactly that
  — "a subroutine entered by STORE-INSTRUCTION-COUNTER-IF-BRANCH-
  DISABLED and returned by BRANCH ENABLED". `commitNext` implements it
  in one place; nothing exercises it. The block is short: mask one more
  program indicator, put `B, RESUME` in its table slot, and make the
  instruction the counter would have returned to a hang, so restoring
  the counter instead of branching fails at a named address.
* **Leftmost PRIORITY between two MASKED indicators** has no witness.
  Both blocks have exactly one masked indicator actuated, so "leftmost"
  is untested — a model picking the rightmost masked one passes today.
  Needs two masked indicators on at once and a way to observe which
  routine ran *first*; p.48 says the second interruption follows
  immediately, "before the execution of an instruction addressed by the
  instruction counter", so both routines run and only the ORDER
  distinguishes them.
* **Timing**: p.48 permits an interruption at an *instruction*
  boundary; this model takes it at a *quiescent* one (look-ahead empty,
  E-box idle). Later, never earlier.
* **An E-box-class interruption instruction** fails loud rather than
  stepping the counter.
* **`BEW`** — "branch enabled and wait" — is still modelled as a plain
  enabling branch. `ja_ax1a` p.58 is reported to drive it from the
  interval timer and fall through, which is the real behaviour and a
  transcribable block.

### Where the provoking code actually is — scouted 2026-09-21

That scouting is done, and the guess in the old entry was wrong in
both directions. **Everything in this section is a SCOUTING REPORT, not
a transcription**: page and line are cited so the next session can go
straight there, but nothing below has been verified first-hand or
assembled bit-exactly, and none of it may be cited as established
until it has been.

* **`jb_af1c` does NOT provoke one — bounded negative.** No `BE`, no
  `BEW`, no mask write, no interruption-address write, no table, across
  all 282 pages (OCR'd twice, every candidate chased). It provokes real
  faults — divide-by-zero at PDF p.156 sets ZD — and then *polls* with
  branch-on-indicator into SSIP's `SERS`. Its 37 `BD`s are all "make
  sure interrupts are off", never a halt. Its writeup (p.3) has the
  operator set *Interrupt disable* at the console before loading.
* **`ja_ax1a` does NOT provoke one either, deliberately.** Its own
  writeup (p.2): the housekeeping routine "provides an **Interrupt
  hang-up** if for some reason the system should become enabled", and
  "since the major portion of the program is run in a disabled mode, it
  became necessary to place all enabling type instructions at the end."
  Its `INT1` table (p.59) is all `NOP,0`, falling through to the
  end-of-program routine.
* **`jb_ax5b` (I-Box 5) DOES — this is the one.** Routine 1260, PDF
  p.45, reported as: `TI,1,BIT0%$X1¤,$IND` (set one of indicators
  20-47), `TI,1,BIT0%$X1¤,$MASK` — *"SET MASK BIT OF TEST IND BIT"* —
  then `BE,$+.32` *"ENABLE AND AWAIT INTERRUPT"*, falling through to an
  error path *"FAILED TO INTERRUPT ON IND MK"*, looped over every
  maskable indicator. That is exactly the shape of
  `programs/interrupt_pg0.strap`, arrived at independently from p.48.
  **Transcribing it needs SSIP's `160S1`/`160SX1` save/restore harness
  (`ax5b` pp.41-44) first.**

### Two leads worth taking before the rest of the mechanism

1. **`ja_ax1a` p.56, `ENSU`** — reported as a short, self-contained
   block that loads the interruption address, zeroes the mask, and sets
   the **address boundary registers** from a literal, with the
   assembled boundary word printed beside it and a comment reading it
   out as *32.0 - 262143*. §1a's boundary-register work is
   manual-derived only; this would give it a **transcription**, which
   is the standard that outranks it. Smallest high-value item on this
   list.
2. **`jb_ax5b` pp.66-79** — reported as TEST 7 / 8A / 8B, the
   *positive* boundary-interrupt cases (mask set, interruption
   expected). Not read by the scouting pass. p.80's TEST 8C case 3 was
   read and is the *negative* case: mask zeroed, a fetch above the
   upper boundary must set no DF and cause no interruption.

## 3. Standing practice, after every batch

`python3 strap/mutation_score.py` — it refuses to run on a dirty tree
or a non-green baseline, and restores on signal. Read **where** and
**how fast** each mutant was caught, not just the count: a catch far
from its own subsystem is a near miss, and it is how the flag/count
confound surfaced.

Triage survivors into *missing test* / *equivalent mutant* / *expected*
before writing anything. `ad-bound-off-by-one` is the one documented
expected survivor.

Last run 2026-09-19, after the boundary registers: **29/30**, survivor
`ad-bound-off-by-one` as expected. `prot-carve-out-as-or` was caught in
2.2 min by its own section — a catch where it was aimed, not a near
miss.

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

* ~~Is the interruption table indexed in WORDS or HALF-WORDS?~~
  **SETTLED 2026-09-21, from the deck, first-hand: WORDS.** Opened and
  closed the same day, which is worth recording because of *how* it
  closed.

  A scouting pass reported `jb_ax5b` PDF p.48 as three *consecutive
  half-words* commented "HI,BEFORE", "OK, AT" and "LO,AFTER"
  *"INTRPTS ENTER HERE"* — which reads like half-word spacing between
  adjacent indicator numbers, against p.48's "a table of **48
  successive full-word locations**". Reading both pages myself
  dissolved it:

  * p.48 of the listing does have those three lines at 021512.40,
    021513.00 and 021513.40, labelled `16090`.
  * p.86 declares the table: `160IT  DR%BU,64,8¤,64` at **023201.00**,
    with the next symbol `160DMP` at **023301.00** — a gap of octal
    100, exactly **64 words**. The neighbouring `160INT ...,65` at
    023100.00 reserves exactly 65 words by the same arithmetic. The
    table is word-spaced, and 64 slots comfortably holds the 48
    maskable indicators (`160XW2  XW,0,48,0` carries the count 48).
  * p.86 also has `160K6  BD,16090` as a *single half-word* at
    023047.00, assembling to `21512.44 00`.

  So `16090` is a three-instruction **template** that the test copies
  into word-spaced table slots — the comments mean "interrupts arriving
  before/at/after the expected indicator execute THIS", not "this
  address is that slot". Deck and manual agree. Still not traced
  first-hand: the fill loop that does the copying.

  The model was already word-indexed from p.48, and
  `interrupt_pg0.strap` plants `HWRONG` at the half-word-indexed
  address, so the injection for it fails at a named address either way.
* `BR`'s **absolute value** clause is unexercised: an effective address
  can only go negative through index modification, and `effAddr19`
  carries no sign beside its result.
* R/'s ZM clear may be **unreachable** (the divisor is the accumulator,
  which a ZM-setting multiply leaves at zero). Only FP paths were
  checked.
* ~~`ja_ua1_ssip` has a full listing at PDF pp.7–52 and
  `archival_inventory.md` implies prose-only~~ — **corrected
  2026-09-19.** The boundaries were checked against the pages, not
  recalled: p.6 is the Maintenance Tape Control Card, p.7 opens with
  `PRINID, SSIP CBD 2-9-61 JA UA1`, p.52 closes with `END` at
  002732.71. Still cite it by PDF page: 1-up fanfold, no printed page
  numbers, unlike every other tape here.
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
