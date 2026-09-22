# What to do next, and why

A standing work queue for the Stretch model, ordered by dependency.
Written so the next session starts from a decision rather than a
survey.

**This file is the plan, not the record.** The record of *how* each
piece was built lives in `docs/microarchitecture_plan.md`, in the
section comments of `strap/run_tests.sh`, and in commit messages.
When an item here is finished it shrinks to a pointer; it does not
accumulate.

## The bar

Two standards, and every test says which it meets:

* **Transcription** — a listing row checked bit-exactly by a verify
  script. The strongest oracle here.
* **Manual-derived** — hand-written from a primary source, stated as
  the weaker standard in the program's own header.

And one rule that outranks both: **a green test is only evidence about
faults its inputs could have made visible.** Every new test gets an
injection that must fail, at a named address, in *its own* check.

A corollary learned the hard way, three times in one day: **when a
summary of a test claims a rule, check the test actually contains an
input that could break it.** `interrupt_pg0.strap` has four blocks and
three of them exist because an earlier version could not see a rule —
one found by a surviving mutant, one by writing a sentence into this
file that the suite did not support, one by enumerating what the
inputs made visible.

## Done, and where the record lives

| piece | record |
|---|---|
| Storage protection, permanently protected words 1–3 | `run_tests.sh` §"Storage protection, gated on…"; plan A.3; the rule **transcribed** by `verify_ax5b_16086_listing.py` (encoding only — the behavioural test is still hand-written) |
| Address boundary registers + control bit | same file §"…the address boundary registers"; **transcribed** by `verify_ibox1_ensu_listing.py` |
| The interruption mechanism | `run_tests.sh` §"The interruption mechanism"; plan A.3 |

All three are implemented, injected, and in the mutation table. The
boundary registers have both standards. Storage protection's **rule**
now has a deck behind it (`ax5b` 16086 says word 1, DS and "when
enabled" in its own error message) but its **behaviour** test is still
hand-written, and the interruption mechanism is still
**manual-derived only** — which is what the rest of item 1 is for.

## 1. `jb_ax5b` routine 1260 — make the interrupt work deck-verified

The single highest-value item. The write-up's routine index (PDF p.2,
read first-hand, transcribed in `archival_inventory.md`) says 1260
checks *"the mask register, the Interrupt Address register, the
ability to interrupt, the Indicator register, unique interruption for
bits 0-47, I-Box indicators, Upper and Lower Bounds registers and
address monitoring."* That is everything built 2026-09-19 to -21, in
one deck routine.

**pp.41–44 are NOT the prerequisite.** This file said "SSIP's
`160S1`/`160SX1` save/restore harness, reported at `ax5b` pp.41–44".
Read first-hand 2026-09-22, they are 1260's per-indicator blocks,
16071 (`TS`) through 16086 (`DS`). `160S1`/`160SX1` are *call sites*
on p.45 and are still not located; nothing so far has needed them.
Third entry in this file's own "distrust a blocker recorded here"
trap. The page-by-page record is in `archival_inventory.md` §"I-Box
5".

**16086, the DS block, is done** — `programs/ax5b_16086_ds.strap`,
bit-exact via `verify_ax5b_16086_listing.py`, record in
`run_tests.sh` §"I-Box 5 routine 1260's DS block". It is an ENCODING
oracle; storage protection's behavioural test stays hand-written.

**Next three, in order, all unblocked**: 16071 (`TS`), 16083 (`AD`),
16082 (`OP`). Every instruction in them is already implemented.
Skip 16072–16081 — three-line `B`/`CNOP`/`DR` stubs for indicators a
program cannot provoke, not tests. 16084 needs `LVE` and 16085 needs
`EX`, both deferred in item 5.

**Then the indicator walk at 16087/16088 (p.45), and it needs `TI`
first.** `TI` is not in this assembler; its format must come from the
pocket card or the Reference Manual, never from the listing's usage
(AGENTS.md rule 4). The page's layout is settled — the two `TI`s are
full words at odd half-words, 16088 is at 021400.40 — with the
reasoning in `archival_inventory.md`; **read p.45 at 600 dpi, not
200**, which is what made it look inconsistent for a session.

**Caution, paid for** — and note it is about the *boundary* driver,
which finding the indicator-walk driver at 16087/16088 does **not**
discharge: pp.66–79 were *guessed* to hold the positive
boundary-interrupt cases. p.66 read first-hand is the tail of a per-bit
error table, *"UPPER BOUNDARY DATA FAILURE, BIT 9"*. That guess came
from a scouting pass's inference, not from a page. **Find the driver
before transcribing.**

**Do not re-scout these — bounded negatives, 2026-09-21:**
`jb_af1c` never provokes an interruption (no `BE`, `BEW`, mask write,
interruption-address write or table in 282 pages; it provokes real
faults and *polls*). `ja_ax1a` deliberately prevents one — its own
writeup says it "provides an Interrupt hang-up if for some reason the
system should become enabled", and its `INT1` table is all `NOP,0`.

## 2. DF and IF — read routine 1268 first

The two address-monitoring indicators the model does not implement.
p.32: DF suppresses the data fetch and terminates *if its mask bit is
one*; IF interrupts before the instruction that caused it. Both are
mask-dependent, unlike DS.

`jb_ax5b` routine 1268 — *"Checks DF and IF close to data store for
all three memories"* — is the only known deck test of them. **Read it
before designing them**, so the oracle shapes the implementation
rather than being retrofitted to it.

## 3. Smaller open pieces inside what is built

* **Interruption timing.** p.48 permits an interruption at an
  *instruction* boundary; this model takes it at a *quiescent* one
  (look-ahead empty, E-box idle). Later, never earlier. Stated in
  `StretchCore.bsv`, `run_tests.sh` and `bsv/README.md`.
* **An E-box-class interruption instruction** fails loud rather than
  stepping the counter.
* **`BEW`** — "branch enabled and wait" — is modelled as a plain
  enabling branch. `ja_ax1a` p.58 is *reported* to drive it from the
  interval timer and fall through, which would be both the real
  behaviour and a transcribable block. Not verified first-hand.

## 4. Standing practice, after every batch

`python3 strap/mutation_score.py --jobs 12` — each mutant gets its own
APFS-cloned tree, so the real model is never mutated; 53 minutes
rather than 233. It refuses to run on a dirty tree or a non-green
baseline. What remains after parallelising is the serial baseline plus
the slowest single **survivor**, because a survivor is exactly the
mutant nothing stops early.

Read **where** and **how fast** each mutant died, not the count. A
catch far from its own subsystem is a near miss. Last run 32/33,
survivor `ad-bound-off-by-one`, the one documented expected survivor —
but `prot-carve-out-as-or` **moved** to the sibling section and became
a step-cap loop instead of a named-address check. Same count, worse
evidence. Triage into *missing test* / *equivalent mutant* /
*expected* before writing anything.

`python3 strap/line_addresses.py programs/X.strap` prints every
instruction line's address in the listings' octal convention. Every
injection address a new test records should come from it, and it
reproduces the ones already recorded — which is what makes them
checkable rather than folklore.

## 5. Deferred, each its own piece of work

Decimal VFL (`c=1`) and radix conversion; `EX`/`EXIC` (deck oracle:
`ax5b` routine 1262); `RNX`/`LVE`/`LVS`; Transmit backward/`SWAP`/
multi-word; I/O chaining and multiple-block; `LOC` and the
unimplemented `CTL` function codes; channel status reaching the CPU
indicators; the interval timer actually ticking (deck oracle: `ax5b`
routine 1258); 19-bit address truncation (routine 1274).

Out of scope by design: cycle-accurate timing.

## 6. Open questions — record, do not guess

* `BR`'s **absolute value** clause is unexercised: an effective address
  can only go negative through index modification, and `effAddr19`
  carries no sign beside its result.
* `R/`'s ZM clear may be **unreachable** (the divisor is the
  accumulator, which a ZM-setting multiply leaves at zero). Only FP
  paths were checked.
* The **fill loop** that copies `jb_ax5b`'s three-instruction template
  at `16090` into the word-spaced table slots has not been traced. The
  table's *units* are settled — 64 full words, from `160IT` at
  023201.00 to `160DMP` at 023301.00 — with the reasoning in
  `run_tests.sh` §"The interruption mechanism".

Two conventions that are not questions and cost a session each when
forgotten: Reference Manual **PDF page = printed page + 3**, and
`ja_ua1_ssip` is cited by **PDF page** because its listing carries no
printed page numbers.

## Traps this project has paid for

* A bare `*` or `L` assembles as **VFL**, not floating point. Write
  `*(N)`, `L(N)`.
* Give any data section an explicit `SLC`: `DD` emits at the location
  counter, so growing code silently overruns its own constants.
* Compute octal addresses with a helper. Every one written by eye in
  this project has been wrong.
* **Never edit a file while a suite or campaign is reading it** —
  worst of all `run_tests.sh`, which `sh` reads by BYTE OFFSET as it
  goes, so editing a comment anywhere above the live line shifts every
  later offset and the shell resumes mid-token. Kill the run and
  restart; there is no salvaging it.
* A verify script cannot tell you a **label** is on the wrong row: it
  checks what a symbol resolves to, and a misplaced symbol still
  resolves.
* When a rule has more than one implementation, each copy needs its own
  witness. `effAddr18/19/24` (3 copies), the SEOP rule (6), ZM's clear
  (16).
* **A hang address read at the step cap is accurate to one half-word,
  not exactly.** The instruction counter oscillates between a
  self-branch and the half-word after it; the cap samples whichever
  clock it lands on. Measured: caps of 30000/30001 report one, 30002
  the other.
* **Bit offsets are printed in octal and written in decimal.** The
  listings and every address in `run_tests.sh` use octal (`004107.40`
  is bit 32); a program's source is decimal unless a `(8)` radix prefix
  says otherwise — and `(8)` applies to *both* halves of a bit address.
  Use `line_addresses.py`; do not convert by eye.
* **A zero half-word decodes as `BE, 0`** — BranchOrMisc code 000 is
  BRANCH ENABLED. Any program that runs off its own end into untouched
  storage turns the interruption system on.
* **A program cannot poll DS while enabled.** DS is permanently masked,
  so raising it interrupts at once and the mechanism turns it off
  before the next instruction. Observe protection violations through
  the interruption routine; put its marker in words 4–31, which p.31
  exempts from monitoring, or the marker store violates too and the
  machine interrupts forever.
* **Reverting an injection with `cp` can leave a stale
  `__pycache__`**: CPython compares source mtime at one-second
  granularity, so a restore inside the same second is not noticed and
  the injected bytecode is reused. Cost one wrong injection result,
  where injection 2 appeared to break a row injection 1 had broken.
  `rm -rf strap/__pycache__` on both sides of every injection.
* **Distrust a blocker recorded in this file.** THREE times the thing
  stopping work was a claim here, not anything in the machine: "64 call
  sites need refactoring" (43 wrote constants that could never trip the
  rule), "the control-bit polarity needs Appendix C" (p.31 states it
  outright), and "1260 needs SSIP's `160S1` harness, reported at
  pp.41–44" (pp.41–44 are the per-indicator blocks, one of which was
  transcribed the same morning with no harness at all). Re-derive an
  obstacle before accepting it.
