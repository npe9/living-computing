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

**The prerequisite this file recorded never existed.** It said
"SSIP's `160S1`/`160SX1` save/restore harness, reported at `ax5b`
pp.41–44". Those pages are 1260's per-indicator blocks, 16071 (`TS`)
through 16086 (`DS`). All four transcribable ones were done without
any harness — and then the driver itself (p.45) was done too. Third
entry in this file's own "distrust a blocker recorded here" trap.
`160S1` = 022741.00 and `160SX1` = 023041.00, read off the driver's
own printed address fields; nothing has needed either. The
page-by-page record is in `archival_inventory.md` §"I-Box 5".

**16086, the DS block, is done** — `programs/ax5b_16086_ds.strap`,
bit-exact via `verify_ax5b_16086_listing.py`, record in
`run_tests.sh` §"I-Box 5 routine 1260's DS block". It is an ENCODING
oracle; storage protection's behavioural test stays hand-written.

**So are 16082 (`OP`), 16083 (`AD`) and 16071 (`TS`)** —
`ax5b_16082_op_ad.strap` and `ax5b_16071_ts.strap`, records in
`run_tests.sh`. **That is every transcribable block on pp.41–44.**
What remains there is out of reach for a stated reason: 16072–16081
are three-line `B`/`CNOP`/`DR` stubs for indicators a program cannot
provoke, 16084 needs `LVE` and 16085 needs `EX`, both deferred in
item 5.

**16071 changes item 5's timer entry.** It is a second, eight-row deck
oracle for the interval timer — Reference Manual p.44, *"Time Signal
(TS). The interval timer has become zero."* — and it is in place
*before* the timer is implemented, which is the order item 2 asks for.
Routine 1258 is no longer the only oracle, and is no longer the
cheapest.

**The indicator walk at 16087/16088 (p.45) is done** —
`programs/ax5b_16087_walk.strap`, and it brought **TRANSMIT/SWAP into
the assembler** (all eight mnemonics, from pocket card X22-6533; only
`TI` has a listing witness). Record in `run_tests.sh` §"…indicator
walk + TRANSMIT IMMEDIATE".

**That immediately exposed a silent bug, now fixed.** Making Transmit
encodable made two long-standing `bsv/README.md` claims testable for
the first time — and two-thirds of one was false. The decoder
discarded bit 57, so a forward `SWAP` executed as a one-word Transmit;
and the count was never read, so a multi-word Transmit moved one word.
Both silent. The decoder now captures bit 57 and the arm honours only
an immediate count of one (Ref. Manual pp.30-31: immediate 0 means
*sixteen*; a direct count lives in a register this arm never reads, so
all of them are refused). Guard:
`programs/transmit_scope.strap`, six blocks, five injections, one per
rule. Record in `run_tests.sh` §"TRANSMIT: what is honoured…".

**The boundary driver is found, and the guess it replaces was wrong
in range AND in kind.** This file said pp.66–79 held "the positive
boundary-interrupt cases" — an inference from a scouting pass, not a
page. Scanning pp.46–86 for BOUND/MONITOR on 2026-09-23 and reading
the hits gives the real layout:

| page | sub-test |
|---|---|
| p.65 | *"TEST 7 CHKS BOUNDARY CONTROL."* / *"CHK UPPER BOUNDARY DATA."* — driver at 16099/160100 |
| p.67 | tail of the upper-boundary error table (BIT10–BIT17) |
| p.68 | *"CHK LOWER BOUNDARY DATA."* (driver 160102/160103) and *"CHK BOUNDARY CONTROL BIT."* |
| pp.69–70 | the lower-boundary error table, bits 32–49 |
| **p.71** | *"FETCH FROM X-1 TO CHK UB COMP."*, *"FROM X-3 TO CHK LB COMP."* |

pp.65–70 test whether the **registers hold their bits**; **p.71** tests
whether the **comparison fires**, and p.71 is what "positive
boundary-interrupt cases" actually means.

**p.65 is transcribed and runs** — `programs/ax5b_16099_ub_data.strap`,
sixteen rows bit-exact, and it **catches a boundary fault and names
the bit**: dropping IBM bit 17 from `boundaryReg` halts it at
022263.00, the error table's eighteenth entry. Record in
`run_tests.sh` §"…TEST 7".

**p.68 is transcribed and runs too** —
`programs/ax5b_160102_lb_ctl.strap`: the lower-boundary loop and the
control-bit test, 37 rows bit-exact, and it localises a fault to the
bit (drop IBM 49 → the table's "BIT 49" entry; drop IBM 57 → `SERS`
with *"UNABLE TO SET BNDRY CNTRL TO 1."*).

**p.71, the comparisons, is transcribed** —
`programs/ax5b_160105_compare.strap`, 52 rows bit-exact on first
assembly. This is the block the item always wanted: it sets bounds,
**enables**, fetches outside them and expects an address-monitoring
interruption (*"UB HAS X, LB HAS X-2. FETCH FROM X+1 TO CHK UB COMP,
FROM X-3 TO CHK LB COMP, AND FROM X-1 TO CHECK WITHIN RANGE"*). It is
also the first use of `TI` outside the page it was derived from.

**ENCODING ONLY, and this is where the harness finally matters.** It
cannot run without `160S1`'s body (SSIP's save/restore at 022741.00),
the interruption table `160IT` at 023201.00, and `BOUND0`/`BOUND1` at
023302/023303. Every earlier block in this routine was transcribed
*without* a harness, which is why the file's original "prerequisite"
claim was wrong. This one needs it for real.

**`160S1` IS TRANSCRIBED** — `programs/ax5b_160s1_clr_inds.strap`,
pp.83-84, 81 rows bit-exact — **and it is not what this file has ever
called it.** PDF p.83, 022741.00. The original claim was "SSIP's
`160S1`/`160SX1` save/restore harness"; the correction after that said
they were "call sites… still not located". Both were wrong about what
it *is*. Its own comment:

> `160S1  SX,$X1,160DMP   -SUBROUTINE TO CLR INDS 0-19,`
> `       BMKZ,$+.32      -AND CHK THAT THEY ARE CLRD.`

It is a **clear-indicators-0-19 subroutine local to routine 1260** —
it clears each permanently-masked indicator with
`TI,1,11.0,$X1` (Transmit Immediate into word 11) and checks it went
off, with a per-indicator message: *"UNABLE TO CLEAR MK."*, *"…CLR IK
OR ABOVE IND."*, then IJ, EK, TS, CPUS. Roughly forty rows, every
instruction already implemented, and it needs no harness of its own.

So the comparison block's real dependencies are `160S1` (now
transcribed), the interruption table `160IT` at 023201.00, and
`BOUND0`/`BOUND1` — none of them the mythical SSIP harness.

**And transcribing it found an assembler bug.** `160S1`'s one `XW`
row was the single mismatch in 45: `XW`'s fourth operand is **three
bits** (IBM 25-27, the index flag plus two spare) and `strap_asm.py`
masked it to one, so `,4` and `,2` encoded as zero and `,1` set the
flag instead of the second spare. p.114's own table settles it —
`BIT25` is `XW,0,0,0,4`, `BIT26` `,2`, `BIT27` `,1`. Fixed.

**Next on item 1**: the interruption table `160IT` at 023201.00 and
`BOUND0`/`BOUND1` at 023302/023303, after which the p.71 comparison
block can run.

**Do not re-scout these — bounded negatives, 2026-09-21:**
`jb_af1c` never provokes an interruption (no `BE`, `BEW`, mask write,
interruption-address write or table in 282 pages; it provokes real
faults and *polls*). `ja_ax1a` deliberately prevents one — its own
writeup says it "provides an Interrupt hang-up if for some reason the
system should become enabled", and its `INT1` table is all `NOP,0`.

## 2. DF and IF — and routine 1268 is NOT their oracle

**DF IS DONE except its mask-dependent half.** Classes 1 and 3 are
implemented and tested — `dfSignal` in `StretchExecute.bsv`, four
programs, twenty-six injections — and class 2 is moot. What is left of
this ITEM is **IF, all of it**, plus the mask-dependent half (which DS
does not have either, and which needs a termination mechanism the
model lacks). Read the rest of this section for what was settled on
the way, because the correction below is the reason it took a
re-reading of the primary source rather than a deck.

p.32 (PDF page 35 of `22-6530-2_7030RefMan.pdf`; printed page + 3)
is the whole of the primary source, and it gives a CLOSED LIST rather
than a rule to generalise:

> *Address monitoring for Data Fetch includes: 1. The effective
> address of all fetch-type operations with a direct address. 2. The
> effective address at each level of the LOAD VALUE EFFECTIVE
> operation with the exception of the final effective address which is
> loaded into the specified index register. 3. The refill address used
> in index refill operations and the operations REFILL and REFILL ON
> COUNT ZERO.*

**Class 1: done.** Four opcode-gated call sites — VFL `L`/`+`/`K`,
connective `C`/`CT`, the direct-index loads and compares, the
floating-point arithmetic class. NOT one guard at the single
`st.readWordReq` they all funnel through, and that is the design
decision worth keeping: a read-modify-write STORE (`ST`, `M+`, `SV`,
`SC`, `SR`, `SVA`, `CM`, `BB`'s bit change) reads its word through that
same path, and p.32 puts those on the DS side — a fetch-type operation
is one whose contents "are not subject to change". Half the test
program is stores for exactly that reason, and the injection that adds
`dixop_SV` to the predicate is what makes those lines evidence.

**Class 2 is moot**: LVE decodes Operation Code Invalid in this model.

**Class 3: DONE.** All eleven refill reads signal, across three
programs and eighteen injections:

* `df_refill_alarm.strap` — `R` and `RCZ`, both paths (index register,
  and the external-memory one that takes two sequential reads).
* `df_refill_index_alarm.strap` — `CBR`, `V+CR`, `V+ICR`, `V-ICR`.
* `df_refill_vfl_alarm.strap` — the five progressive-indexing refills
  in the two VFL-format arms: `L`/`+`/`K` through a shared trailing
  block, `ST`/`M+` inline, and the connectives repeating the same
  split with `C`/`CT` trailing and `CM` inline.

**Every signal sits INSIDE its own suppression gate**, because a
refill that is computed and then skipped reads nothing and p.32
monitors addresses "actually used". Three things that gate on:
`refillLegal`, RCZ's and CBR's count conditions, and — in the two
trailing blocks — the `vflReadsUsed >= 2` arm that suppresses the whole
operation. Every one of those has a paired negative block and an
injection that hoists the signal outside it.

**Two placement details worth keeping.** In `evalBranch` the signal
must come AFTER `o.ind = setIndexResultIndicatorsF(ind0, x1)`, which
assigns from `ind0` and would discard it. And `connectiveOp` carries
its OWN copy of the trailing block, so a check on `vflIntOp`'s says
nothing about it — both copies need their own blocks and their own
injections.

**The mask-dependent half is not done, for DF or DS.** p.32: "if the
DF mask bit is one, the data fetch is suppressed and the operation
terminated". The INDICATOR is set either way — the mask decides only
what happens next — so setting it needed no mask read at all, which is
why class 1 landed without touching `StretchStorage`'s mask. But
termination needs a mechanism this model does not have, and
`protViolates`' scope note now says so in one place for all three
indicators. The test program runs the mask-ZERO case only and says
why.

**IF is untouched.** Its own spec is an interruption-TIMING rule —
"the interruption occurs before execution of the instruction causing
the indication and after execution of all preceding instructions has
been completed or terminated" — which belongs with item 3, and its
other half ("the entire branch operation, including any counting, bit
changing, or index alteration, is suppressed") touches every branch
arm. Deliberately a separate commit.

### CORRECTION, 2026-09-24: THERE *IS* A DECK ORACLE, AND IT IS IN A DOCUMENT THIS PROJECT HAD ALREADY READ

**`jb_ax5b` routine 1260 TEST 8C, PDF pp.76-83, octal
022546.00-022732.40, labels 160127-160146.** Verified first-hand at
400 dpi. Its own title row:

```
160127  LVI,$X1,160AD1  -TEST 8C CHECKS DF + IF UNDER 4 CONDS,  23063.03 01  022546.00
                        -1. DISABL MASK 0 FETCH OK IND NO INT
                        -2. DIAABL MASK 1 FETCH OK NO IND NO INT
                        -3. ENABLE MASK 0 FETCH OK IND ON NO INT
                        -4. ENABLE MASK 1 NO FETCH IND ON INTRPT
```

It is a dedicated test of the **DF and IF INDICATORS** across the
enable bit and the mask bit, and condition 4 is the **MASK-DEPENDENT
HALF** — "NO FETCH ... INTRPT" — which this file recorded as needing
"a termination mechanism this model does not have". There is an oracle
for it. The deck's own write-up (PDF p.8) states the whole of TEST 8:
*"AN ELEMENTARY CHECK TO DETERMINE THAT THE CORRECT INDICATORS AD, DS,
DF, IF ARE TURNED ON AND THAT CORRECT TERMINATIONS AND SUPPRESSIONS
OCCUR WHEN VARIOUS ILLEGAL ADDRESSES ARE USED WITH MASK BITS SET TO
BOTH ONE AND ZERO."*

**So DF was built here to the weaker standard when a stronger one was
available**, roughly thirty pages before routine 1268 in the very
document whose misreading created this item. The four DF programs say
"no listing this project has read tests DF at all"; that is now false
and their notes are superseded.

**This is the FOURTH time "distrust a blocker recorded in this file"
has paid out**, and the first time the blocker was one this file had
already been corrected once about. The correction below about 1268 is
still right — 1268 *is* a forwarding test — but it drew a false GLOBAL
conclusion from a true local one, and nothing re-checked it.

**Reported alongside it, same sweep, also unrecorded here:**
* **TEST 8B, PDF p.75** (160123-160Z1, 022513.00-022545.40) — a
  second, richer DS oracle covering enabled/disabled *and* store
  suppression: *"-SX ABOVE UB WAS NOT NOPED, DATA WAS STORED WHEN
  ENABLED."*
* **TEST 7, PDF pp.71-74** (160105-160122) polls DF with `BDFZ`/`BZDFZ`
  throughout — a second DF oracle, on the boundary-compare path.
* **p.32's BRANCH clause is still manual-only.** Every IF case in
  TEST 8C is straight-line fall-through into a below-LB region; none
  branches into one. "the entire branch operation ... is suppressed"
  has no deck test in this corpus.
* **A discrepancy in the header itself, flagged not smoothed.**
  Condition 1 reads "IND" where the code (`BZIFZ`/`BZDFZ`, branch on
  indicator ZERO, error on fall-through) expects the indicator NOT
  set, and condition 2 reads "NO IND". Re-read first-hand at 400 dpi:
  line 1 does say "IND". Line 2 of the same header also carries the
  typo "DIAABL", so a typo is plausible — but that is a guess, and the
  code is the thing to build against.

**TEST 8C CASES 3 AND 4 ARE NOW TRANSCRIBED** —
`programs/ax5b_160_test8c.strap` +
`verify_ax5b_160_test8c_listing.py`, PDF pp.80-83, octal
022640.40-022733.40, **119 rows bit-exact**, one unbroken half-word
run (the continuity bridge on p.81 closes the gap between the cases).

Cases 3 and 4 were chosen over the disabled controls because they are
the **mask-dependent pair**: both enable the system, case 3 runs with
the mask bit zero and case 4 with it one, which is exactly p.32's
rule. Their error messages are the contract read against each other —
case 3 fails with "WAS NOPED" (it must have fetched), case 4 with "WAS
EXECUTED" (it must not have).

**`CNOP` is alignment-dependent and it is the trap in that block.** On
p.80 the preceding `BE` sits on a `.40` half-word so `CNOP` emits
NOTHING; on p.82 the `BE` sits on `.00` so it emits a filler `NOP` at
022722.40. Case 3 is 56 source lines / 55 code rows, case 4 is 56/56.
The assembler already reproduces both from the same source line.

**Four more confirmations of the BIT table** (024522 + n): BIT14,
BIT20, BIT21, BIT57 all land. And because the deck sets mask bit 20
for the DF half and 21 for the IF half, the block is the **deck's own
statement that DF is 20 and IF is 21** — numbering this project had
taken from the manual.

**REMAINING ON THIS ITEM, in order:**
1. **IF itself is still unimplemented.** TEST 8C is now its acceptance
   test; it is an encoding oracle until the model can run it.
2. **The mask-dependent half of DF and DS** — case 4 is the oracle.
3. **p.32's BRANCH clause has no deck test anywhere in this corpus.**
   Every IF case in TEST 8C is straight-line fall-through into a
   below-LB region; none branches into one. "the entire branch
   operation ... is suppressed" stays manual-only, and the
   `ds_terminates_branch.strap` work is the nearest thing to it.

**THIS ITEM USED TO SAY `jb_ax5b` ROUTINE 1268 WAS "the only known
deck test of them". That was a misreading, and it is corrected.**
Read first-hand 2026-09-22, the routine's own header is *"1268 — IF
AND DF CLOSE TO DS"* and its error messages are *"EXECUTED OLD
INSTRUCTION FROM EXT."* and *"LOADED OLD DATA FROM EXT MEM."* — the
wrong **value** arrived, not an indicator failed to set (compare
1260's *"UNABLE TO TURN AD ON."*). `DF`/`IF` there are the Data Fetch
and Instruction Fetch **paths**; "close to DS" is close to a Data
Store. It is a look-ahead forwarding test, and
`archival_inventory.md` already said so in one of the two places it
described the routine.

**~~So DF and IF have no deck oracle anywhere read so far~~ — FALSE,
see the correction at the top of this item.** Routine 1268 is not
their oracle; routine 1260 TEST 8C is.

**What 1268 turned out to be good for.** Both halves are transcribed
and **run**: `ax5b_1683_df_close_to_ds.strap` (test 2, the load side)
and `ax5b_1681_if_close_to_ds.strap` (test 1A, the
instruction-fetch side). Records in `run_tests.sh`. In both, the
encoding is the discriminating standard and the run is a regression
guard — measured, neither witnesses forwarding, because the deck's
spacing is too gentle for this model's pipeline. Test 1A does witness
something the project had no direct test for: the `LX`/`SX` **index-word
round trip**, since it plants an arbitrary instruction through
`packIndexWord` and executes it.

**Left on 1268**: cases 1B and 1C, blocked on `EX` (item 5).

## 3. Smaller open pieces inside what is built

* **Interruption timing.** p.48 permits an interruption at an
  *instruction* boundary; this model takes it at a *quiescent* one
  (look-ahead empty, E-box idle). Later, never earlier. Stated in
  `StretchCore.bsv`, `run_tests.sh` and `bsv/README.md`.

  **THE DISCRIMINATOR EXISTS AND IS ALREADY IN `strap/programs/`** —
  found 2026-09-24 after an 839-page sweep that expected it elsewhere.
  Routine 1260 brackets every provoked interruption between an enable
  and a disable **one instruction apart**, and in this model
  `intDueCalc` returns Invalid the moment `irqEn` goes false, so a
  pending interruption simply evaporates and the block falls through
  its "we did not interrupt" path. From the already-transcribed
  `ax5b_160105_compare.strap`:

  ```
      BE,  $+.32
      LX,  $X13, 0($X2)        ! -FETCH FROM UB, BC IS 1.
      BD,  $+.32
  ```

  `ax5b_16087_walk.strap` is tighter still — **zero** instructions of
  slack between the `BE,$+.32` and the `BD` that would clear it. The
  same bracket appears on `ax5b` PDF pp.45, 71, 72, 74 and 80.

  **Three qualifications, all load-bearing.** (1) Both blocks are
  ENCODING-ONLY and unrun — they need `160S1`'s body and the `160IT`
  table — so the honest statement is "the deck would catch a late
  interruption", not "this model fails today". (2) The verdict is
  instruction-class dependent, and this repo already has measured
  evidence of about one instruction of lateness: `run_tests.sh`'s
  `df_data_fetch_alarm` note records a VFL `ST` holding the E-box a
  call longer than a `BB`-style store, which is exactly the shape that
  loses a one-instruction bracket. (3) **Nothing anywhere compares a
  STORED instruction counter against an expected address** — SSIP's 48
  interrupt-table entries all do `SIC,INTZ`, and its write-up explains
  the printout as *"the address of the instruction following the one
  causing the interrupt"*, but that value is printed for a human, never
  `KV`'d against an expectation. That would be the strong
  discriminator and no deck contains it.

  **Bounded negatives from the same sweep** (839 pages OCR'd): of
  `jb_ax2a` (203pp), `jb_ax3a` (215pp) and `jb_ax4b` (193pp), the ONLY
  interrupt-related hits are their operating procedures — *"Disable
  Interrupt and Time Clock"*. `ja_ax1a` is the one I-Box deck run with
  interrupts ENABLED, and its own index lists only `BEW — Interrupt by
  IT` as interrupt-intending. And `ax5b` pp.46-64, undescribed in
  `archival_inventory.md` and the obvious place to look, turn out to be
  the per-indicator unique-interruption tests (pp.46-48), the priority
  tests (pp.49-54) and an after-the-fact indicator scan (pp.55-59) —
  all timeout- or set-based, **none of them timing discriminators**.
* **An E-box-class interruption instruction** fails loud rather than
  stepping the counter.
* **`BEW`** — "branch enabled and wait" — is modelled as a plain
  enabling branch. **VERIFIED FIRST-HAND 2026-09-23, and this bullet
  used to be wrong in both halves.** It said `ja_ax1a` p.58 drives it
  from the interval timer "and fall through, which would be both the
  real behaviour and a transcribable block".

  Reference Manual **printed p.40** (PDF page 43) settles what it
  does: *"This instruction provides a means of stopping program
  execution. The interruption mechanism is enabled, and the
  instruction counter contents are replaced with bits 0-18 of the
  effective address of the operation as in BRANCH ENABLED. However, no
  further instruction will be executed until after an interruption
  occurs."* So `BEW` **BRANCHES** — it does not fall through — and the
  distinctive part is the WAIT that follows the branch.

  `ja_ax1a` p.58 does have the block, under a `%BEW%` banner ("BRANCH
  ENABLED + WAIT") followed by a `%SIC-BEW%` one, and the shape agrees
  with the manual rather than with this bullet: each
  `BEW,ISBEnn` is followed by a `BD,$` at the FALL-THROUGH address and
  then by its target, so the hang is what a machine that failed to
  branch would reach. `ISBE37 BEW,ISBE38` prints `6031.60 00` at
  `006030.40`; bit 18 is set, so the target is `006031.40`, which is
  `ISBE38` — two half-words past the `BD,$`.

  **AND THE BLOCK CANNOT WITNESS THE WAIT.** Since `BEW` always
  branches, control reaches the target whether the wait is modelled or
  not; the `BD,$` is unreachable on any machine that branches at all.
  It is an ENCODING oracle (strong — it covers `BEW` and the `SIC`
  prefix on `BEW`, neither of which any transcription here has) plus a
  weak run test. Same shape as the "a deck can be the WEAKER test"
  trap below.

  **What the wait would cost.** A test that could see it needs an
  instruction at the target that must NOT run until an interruption
  arrives — and the only source of one here is the interval timer,
  which this model does not tick (`bsv/README.md` scope). So
  implementing `BEW`'s wait is coupled to making the timer run, and
  the four blocks on p.58 all set `$IT` first for exactly that reason.
  Transcribe the encodings first; they stand on their own.

## 4. Standing practice, after every batch

`python3 strap/mutation_score.py --jobs 12` — each mutant gets its own
APFS-cloned tree, so the real model is never mutated; 53 minutes
rather than 233. It refuses to run on a dirty tree or a non-green
baseline. What remains after parallelising is the serial baseline plus
the slowest single **survivor**, because a survivor is exactly the
mutant nothing stops early.

Read the **SURVIVOR** list, and the count. Triage into *missing test*
/ *equivalent mutant* / *expected* before writing anything.

**Do NOT read the section column as "the catcher".** It is the FIRST
section to fail, because each mutant runs with `FAIL_FAST=1` — so for
a broad fault it names whatever broad test runs earliest, which says
nothing about coverage. This file used to say "a catch far from its
own subsystem is a near miss", and that rule gave the wrong answer
every time it was applied (see below). To find out whether a rule
actually has a witness, re-run that one mutant with `FAIL_FAST` unset
and read the whole list of failing sections.

**Run 2026-09-23: 38/39, survivor `ad-bound-off-by-one`** — the one
documented expected survivor, after DF landed. All three DF mutants
caught by the sections written for them: `df-index-fetch-unsignalled`
and `df-store-read-signals-fetch` by "DF: the data-fetch address
alarm, p.32 class 1", `df-refill-signals-before-gate` by "DF on a
refill address: R and RCZ". `prot-carve-out-as-or` is still in its own
section.

**AND THE DF SECTION DISPLACED TWO first-fail LABELS**, which is the
`prot-carve-out-as-or` story again and is recorded for the same
reason: the count did not move, the named evidence did.
`int-mask-ignored` and `vfl-length-zero-is-zero` now both report
"first-fail: DF: ... class 1". Neither is a regression, and for
`int-mask-ignored` it is not even an accident —
`df_data_fetch_alarm.strap` sets DF's mask bit to zero and depends on
NOT interrupting, so a model that ignores the mask changes its control
flow. That makes the DF program a genuine SECOND witness of p.48's
mask rule, independent of `interrupt_pg0`. But the label still says
nothing about which section *covers* either rule; per the rule below,
only a re-run with `FAIL_FAST` unset does.

**Run 2026-09-22: 32/33, survivor `ad-bound-off-by-one`.**
`prot-carve-out-as-or` was back in its own section, so the regression
the run before it flagged was resolved.

**ALL FOUR "NEAR MISSES" IN THAT RUN WERE WRONG**, for two different
reasons, and both were the measurement rather than the model.

*Two were a `/tmp` race.* Five test scripts — `run_fp_addr_test.sh`,
`run_fp_exp_test.sh`, `run_fp_test.sh`, `run_fp_signmod_test.sh`,
`run_scf_test.sh` — wrote a *fixed* path under `/tmp` and re-read it.
The campaign runs 12 mutants in parallel, each in its own **cloned
tree** — but `/tmp` is not cloned, so all twelve raced on one file and
`FAIL_FAST` named whichever script lost. Run serially, both
`seop-ignored-on-backspace*` mutants are caught by `io_tape` at
exactly the checks their entries name. Each script now uses
`${TMPDIR:-/tmp}/<name>.$$.strap`.

*Two were the `FAIL_FAST` label*, and this is the more embarrassing
one because the rule that produced them was written in this file.
`imm-count-low-bits` and `vfl-length-zero-is-zero` were both recorded
as "caught only by the catch-all smoke test". Re-run with `FAIL_FAST`
unset:

| mutant | sections that fail |
|---|---|
| `imm-count-low-bits` | **10**, including `IBOX-1 KCI`, `IBOX-3 LRI`, `IBOX-1 C+I`, `C-I` — named for the very instructions the rule governs |
| `vfl-length-zero-is-zero` | **38**, most of them FP and VFL sections on its own subsystem |

Both rules are heavily witnessed. **There are no near misses in this
campaign.** `mutation_score.py` now prints the column as
`first-fail:` so it cannot be read as the catcher.

**AND THE COUNT HID AN UNTESTED RULE.** Both ZM mutants reported
"caught by their own section" — truthfully — while mutating the *same*
line. p.99's ZM rule is implemented twice in `StretchFP.bsv`,
character for character, in `fpMul` and `fpMulDouble`; both mutants
used that line as their pattern and `apply()` did
`replace(old, new, 1)`. Injecting the same fault directly into
`fpMulDouble` and running the whole suite gave **3059 PASS, 0 FAIL**.
Now: `mutation_score.py` refuses a pattern that does not match exactly
once, the two mutants carry their preceding line to disambiguate them,
`zm-double-*` target the second copy, and
`programs/fp_zm_terms_double.strap` is the witness. 36 mutants.

**So: a mutation score is evidence about the sites the table names,
and nothing else.** Before trusting one, check the table can still
reach every site it claims — that check is now automatic.

`python3 strap/line_addresses.py programs/X.strap` prints every
instruction line's address in the listings' octal convention. Every
injection address a new test records should come from it, and it
reproduces the ones already recorded — which is what makes them
checkable rather than folklore.

## 4a. `EX`/`EXIC` — the oracle is read; implement from it

**The highest-leverage unimplemented instruction**, because four
already-located transcription targets wait on it: `jb_ax5b` routine
1268 cases 1B/1C (`EX,$X3`, `EX,$R`) and routine 1260 blocks 16084
(`LVE`) / 16085 (`EX`).

### THE OPERATION SPEC, READ FIRST-HAND 2026-09-24 — printed p.50 (PDF 53)

This item used to carry the E-box design as a *proposal* and the
manual only by reference. The manual states the whole contract:

> **Execute (EX).** *"Bits 0-18 of the effective address form the
> address of the location of a subject instruction that is fetched and
> executed. Subject instructions of EXECUTE may occupy any addressable
> location. An effective address of EXECUTE that is below 32.00
> (including addresses between 1.00 and 3.32) is not monitored by the
> address monitoring mechanism; that is, indicator IF cannot be
> actuated by these addresses."*

> **Execute Indirect and Count (EXIC).** *"Bits 0-18 of the full-word
> addressed by bits 0-17 of the effective address are used as a
> pseudo-instruction counter. The contents of the pseudo-instruction
> counter address the location of a subject instruction that is
> fetched and executed. **After the subject instruction has been
> fetched but prior to its execution, the pseudo-instruction counter
> is stepped. If the subject instruction is half-length, the
> pseudo-instruction counter is stepped once; if full-length,
> twice.**... Pseudo-instruction counters may occupy any of the index
> registers as well as main core storage locations but **cannot occupy
> locations addressed between 0 and 15**. Subject instructions of
> EXECUTE INDIRECT AND COUNT may occupy any available locations with
> **addresses 32.00 and greater**."*

Those last two sentences are, word for word, the deck's **TEST 3A**
(pseudo-IC < 15) and **TEST 3B** (subject < 32).

**The EXE rule, printed p.49 (PDF 52):** *"the subject instruction is
not allowed to change the state of the interruption system or replace
the contents of the instruction counter. The execution exception
indicator (EXE) is turned on by any branch operation of a subject
instruction in which the condition for a successful branch is met.
When indicator EXE is actuated, the branch and all associated
operations are not performed. The suppressed actions include the
disabling in BRANCH DISABLED, the enabling in BRANCH ENABLED or BRANCH
ENABLED AND WAIT, the counting and refilling in COUNT, BRANCH AND
REFILL, and so on."* — so EXE suppresses far more than the branch.

Same page, **confirming the design recorded below**: *"When an
execution operation is initiated in the main program, the instruction
counter is stepped in normal fashion as in all operations of the main
program. However, **it is never stepped during the execution of any
subject instruction** even if the subject instruction is again one of
the execution instructions."*

**And p.50 on monitoring and interruption**: *"address monitoring is
always in force during (1) EXECUTE and (2) EXECUTE INDIRECT AND COUNT,
except for the address of the location of the FIRST LEVEL
pseudo-instruction counter. Second, at the completion, termination, or
suppression of an execution operation, interruption is always
permitted."* — which is what the deck's 1CA/2CA ("ENABLE AFTER
EX/EXIC") and 1CB/2CB ("CHK ADR MONITOR") test.

**USA, printed p.45:** *"A LOAD VALUE EFFECTIVE, EXECUTE, or EXECUTE
INDIRECT AND COUNT operation has been in progress for longer than one
millisecond (several hundred indirect addressing cycles). The
operation is terminated wherever it may be and the program
proceeds."* The deck builds a chain of **2049** for this.

### ROUTINE 1262'S BLOCK MAP (PDF pp.87-110, 023304.00-024332.00)

| part | PDF pp. | addresses | entry | what it checks |
|---|---|---|---|---|
| head | 87 | 023304.00-023307.00 | `162` | prints ID, `BD,1621` |
| TEST 1A | 88-89 | 023310.00-023373.00 | `1621` | EX must not relinquish control; seven memory combinations |
| TEST 1B | 90-91 | 023373.40-023442.00 | `16212` | EX of each non-branch class, **two** checks per class |
| TEST 1C | 92-94 | 023442.40-023551.00 | `16218` | 1CA enable-after-EX, 1CB address monitor, 1CC EX of branch + EXE |
| TEST 1D | 95 | 023551.40-023576.00 | `16241` | EXE and USA indicators |
| TEST 2A | 96-98 | 023576.40-023704.40 | `16247` | EXIC must not relinquish control |
| TEST 2B | 99-102 | 023705.00-024000.00 | `16260` | EXIC of each class, **three** rules per class |
| TEST 2C | 103-105 | 024000.40-024107.40 | `16271` | 2CA/2CB/2CC, the EXIC twins of 1C |
| TEST 2D | 106 | 024110.00-024135.40 | `16294` | EXE and USA for EXIC |
| TEST 3A | 107-108 | 024136.00-024151.00 | `162100` | pseudo-IC less than 15 |
| TEST 3B | 108 | 024151.40-024162.00 | — | subject instruction less than 32 |
| constants | 109 + p.110 top | 024172.00-024332.00 | `162K1`..`162EXI` | incl. the 64-word `162INT` table at 024220.00 |

Continuity bits corroborate the partition: 1A=BIT0 ... 2D=BIT7, TEST
3=BIT8, and the exit mask `%8@777000.0` is exactly nine ones. Nine
sub-tests, nine bits.

**TWO EXTENT CORRECTIONS.** 1262 does **not** end at p.109 — its last
row, `162EXI LVI,$X1,%8@777777.40`, is at 024332.00 on the **top line
of PDF p.110**, above routine 1268's header. And `162EXI` is
*referenced* on pp.90, 92, 103 and 107 while being *defined* past
where anyone would look.

**A HEADER THAT MISDESCRIBES ITS OWN TEST, flagged not smoothed.** The
routine header says test 3 checks "THE ILLEGAL COMBINATIONS OF EX AND
EXIC". 3A and 3B are both **EXIC-alone address-range** violations.
There is no EX-with-EXIC combination test in test 3; the nearest thing
is TEST 1A's two-level EX-of-EX. Do not go hunting for tests that are
not there.

### FIRST TRANSCRIPTION TARGET: TEST 3A, `162100`, 024136.00-024151.00, 23 rows

Chosen over the smaller head of `1621` (13 rows) for reasons that are
about evidence, not size: it is a **whole sub-test** entered by one
`BD,162100`; both its error messages are **inline in its own comment
column** rather than an index into a shared table, so a failure names
itself; it encodes **EXIC**, the harder arm; and its three messages
*are* the suppression contract — no interrupt on the illegal
pseudo-IC, AD set, the instruction NOPed — which is exactly p.50's
"cannot occupy locations addressed between 0 and 15".

**AND IT AVOIDS AN ASSEMBLER PREREQUISITE.** TEST 1A and 1D use
progressive-indexing notation `%$X1@` (`SX,$X2,162INT%$X1@`) that
appears in **no** existing `strap/programs/*.strap`, so they would
carry an assembler change as well. 3A uses none of it, and its one
exotic row (`%8@DD%BU,32,8@,3740 -ILLEGAL OP.`) is *already*
transcribed and bit-exact-verified here as `160K7` in
`ax5b_160k_constants.strap`.

**Not candidates:** TEST 1D and 2D depend on `16084A`/`16084B`, which
belong to routine 1260 — and 16084 is itself one of the blocks blocked
on EX.

**Routine 1262 is its deck oracle and has been read first-hand**
(2026-09-23, PDF pp.87–110; purpose block and the p.101 EXIC blocks
transcribed in `archival_inventory.md`). Its own header: *"TEST EX
AND EXIC"*, in three parts — test 1 the execution of **all classes**
of instruction plus the indicators illegal executes set; test 2 the
`EXIC` instruction; test 3 the **illegal combinations** of the two.

**What p.101 pins down, three rules per instruction class**, each with
its own error message: `EXIC` to that class must not interrupt; the
subject instruction must actually execute; and the **pseudo-IC must be
stepped by the subject's length** (`.32` for a half-word), which the
deck checks with `V+I` then `KV`.

Pair it with Reference Manual p.45 on indicator 18 (EXE): an
instruction executed under `EX`/`EXIC` that *"attempted to change the
contents of the instruction counter"* is **suppressed**.

Design from those, then transcribe 1262 as the acceptance test — the
order item 2 asks for and did not get.

**AND IT FITS THE MACHINERY THAT IS ALREADY THERE** — read out of
`StretchExecute.bsv`'s `mkEBox` and `StretchCore.bsv`'s
`rl_exec_resume` on 2026-09-23, so this part is *verified structure*,
not a sketch. `execute()` is a pure function and Bluespec will not let
it recurse, which is the obvious reason to think `EX` is hard. It
isn't, because the E-box already has a **bail-out and resume** path
for instructions that need an operand word:

* `start()` runs `execute()`; if it returns `needsRead`, the E-box
  issues the read, stores the instruction in `held`, and returns
  Invalid;
* `resume()` collects the word into `prefetch` and **re-runs
  `execute()` with the same held instruction**.

*Proposed* (not yet built): `EX`'s arm returns `needsRead` = the
subject's address, exactly like any operand fetch. Then `resume()`,
seeing the held instruction is `EX`/`EXIC`, **decodes the fetched word
and installs the SUBJECT as the held instruction** — `execute(... ,
decode(v), emptyPrefetch, 0)` instead of re-running the `EX`. The
subject's own `needsRead` then works normally, because it is now the
held instruction. No recursion, no second `execute()` instantiation,
and the cycle it costs is one the bail-out already pays.

Two consequences that fall out of that shape and match the sources:
* the instruction counter advances past the **`EX`**, because
  `commitNext` uses the held `pc`/`len` — which is what Ref. Manual
  p.45 requires, a subject that tries to change the IC being
  *suppressed* with EXE set;
* `EXIC` additionally steps its **pseudo-IC** by the subject's length,
  which is routine 1262's third check per class (`.32` for a
  half-word).

## 5. Deferred, each its own piece of work

Decimal VFL (`c=1`) and radix conversion; `RNX`/`LVE`/`LVS`;
Transmit backward/`SWAP`/
multi-word; I/O chaining and multiple-block; `LOC` and the
unimplemented `CTL` function codes; channel status reaching the CPU
indicators; 19-bit address truncation (routine 1274).

### THE INTERVAL TIMER — the rate is SOURCED, and 1258 is located

**`microarchitecture_plan.md` A.7/A.10 say the step rate "remains to
source". It is Reference Manual printed p.34 (PDF 37)**, read
first-hand 2026-09-24:

> *"It is continually stepped down by pulses originating from a stable
> oscillator. Each time the oscillator delivers a pulse, the value of
> the timer is read out, decremented by one, and returned to core
> storage. **The oscillator operates at 1,024 (2¹⁰) cycles per second,
> or a pulse about every millisecond.** Bits 0-8 show time in seconds.
> A full cycle is about 8½ minutes.*
>
> *The timer runs whenever the machine is operating, which includes
> also the execution of BRANCH ENABLED AND WAIT. **Whenever it goes
> from one to zero, it turns on the time signal indicator... The next
> oscillator pulse then sets the timer to all ones unless the program
> in the meantime has changed its contents. The timer does not stop
> after reaching zero.**"*

At `StretchTiming`'s 0.3 µs per model clock that is **one tick every
~3255 model clocks**. p.35 adds that the time clock is a 36-bit
up-counter in bits 28-63 driven by *the same* oscillator, "the two
clocks are updated consecutively in the same time interval".

**THE RELOAD RULE IS THE LOAD-BEARING DETAIL, and getting it wrong
breaks the whole suite.** Faithful to p.34 — TS only on the 1→0
transition, reload to all ones — the model starts at 0, reloads on the
first pulse, and takes 2¹⁹-1 ticks (~1.7×10⁹ model clocks) to come
back round, so no existing test ever sees TS. A naive "decrement; at
zero set TS" wraps every ~3255 clocks, and since the model forces mask
bits 0-19 to one, TS (indicator 4) is ALWAYS masked on and would
outrank DS and every PG indicator in the leftmost-wins scan. Every
enabled program would take a TS interruption it never took before.

**And the reload rule has a deck witness**: routine 1258 block
1589/15810, *"-INTERVAL TIMER FAILS TO STEP FROM 000000.0 TO
777777.40"*, with `158K1 = 777777.40` — all ones in bits 0-18.

**p.34 ALSO STATES A RULE `ax5b_16071_ts.strap` CURRENTLY INFERS.**
That program's header says the disabled-execution requirement "is
entailed by two manual pages, not transcribed from this page". p.34
states it outright and names the instruction: *"The only store-type
operations that may store in the left half of location 1... are STORE
VALUE, STORE COUNT, STORE REFILL, and STORE VALUE IN ADDRESS, and
these operations can be performed only when the interruption system is
disabled. When enabled, these operations will turn on indicator DS,
data store, and be suppressed."* Same failure mode as the
boundary-polarity correction: the overview chapter was read, the
chapter twenty pages later was not.

**A THIRD DF INTERACTION, recorded**: p.34 says the timer *"cannot be
read if indicator DF, data fetch, is masked on and the interruption
system is enabled"*.

**ROUTINE 1258 IS LOCATED**: `jb_ax5b` **PDF pp.5-7** — the FIRST
listing pages, immediately after the write-up, not in the tail where
the routine-index order suggests. Octal **014002.00-014063.40**, ~94
code/data rows, which would make it the largest single transcription
in this project (about 1.2× `160s1`). Header: *"1258---CHK TIME CLOCK
AND INTERVAL TIMER... TEST 1 IS A CURSORY CHECK OF THE TIME CLOCK TO
SEE THAT IT STEPS CORRECTLY WITHIN THE CORRECT INTERVAL OF TIME. TEST
2 CHECKS THAT THE INTERVAL TIMER STEPS WITHIN THE ALLOTTED AMOUNT OF
TIME, AND THAT EACH POSITION CAN HOLD BOTH A ONE AND A ZERO."*

**It is a far better timer oracle than 16071**, which only witnesses
"TS comes on". 1258 witnesses the tick RATE (twice, "1 MSEC"), the
RELOAD to all ones, the bits-19-23 clearing from p.34's programming
note, the decrement by exactly one, and the whole TIME CLOCK with its
carry between halves. Every instruction it uses is already
implemented. **But it cannot run until the time clock exists too** —
Test 1 is half the routine and the model has no clock at all
(`StretchStorage.bsv`'s `intervalTimerAndClock` is one register that
nothing steps).

**Do NOT shorten the tick period to make tests cheaper.** Test 1
checks the clock stepped by EXACTLY ONE between two reads about 78
model clocks apart; below ~78 clocks per tick it steps twice and Test
1 fails for the wrong reason. Raise `gen_tb.py`'s step cap instead.

**Implementation hazards, read out of the model** and recorded so the
next attempt does not rediscover them: the tick must be gated on
`StretchCore`'s `tick` PulseWire (a free-running rule in
`StretchStorage` would count down while the harness is still loading
storage, the way `rule intDueCalc` fires unguarded); it becomes a
SECOND writer of `intervalTimerAndClock` and a FOURTH, non-exclusive
writer of `indicators`, both of which this file's own comments say
must be funnelled to one writer (the `storeW` RWire is the shape it
already uses); and any new reader of those registers joins the G0095
path the `mkConfigReg` choices exist to break.

Out of scope by design: cycle-accurate timing.

## 6. Open questions — record, do not guess

**Does `refillLegal` apply to refills other than `R`/`RCZ`?** STILL
OPEN — but as of 2026-09-24 it is open *with affirmative evidence
against closing it by symmetry*, which is a stronger position than the
absence it used to rest on.

The 1-15 gate is sourced for `R`/`RCZ` only, by `jb_ax4b` routine 1238
test 2G/2H. A **different** refill-address no-op rule, over a
**different range**, is sourced for `RNX` by TWO independent primary
sources:

* Reference Manual printed **p.27** (PDF 30), read first-hand
  2026-09-24, "Rename (RNX)": *"When either the old or the new name of
  the index refers to one of the locations **0-31**, the instruction is
  executed as no-operation and indicator AD is set."*
* `jb_ax4b` routine **1244** ("Checks RNX"), whose header item 4 is
  *"CHECK THAT THE INSTRUCTION IS NO OPPED WHEN EITHER THE OLD OR THE
  NEW REFILL FIELD OF IX REG 0 LIES IN THE RANGE OF **1 TO 37
  OCTAL**"* — 1-31 decimal — with two indexed error tables
  (*"RNX FAILS TO NOP WHEN IX 0 INITIAL REFILL ADDRESS IS nn."*).

**Two operations, two different ranges, each stated separately.** That
is the 1961 documentation treating this as PER-OPERATION, and it is
the reason not to extend either rule to `CBR`/`V+CR`/`V+ICR`/`V-ICR`
by symmetry.

**And note the manual is not systematically silent about such gates.**
It states RNX's and omits `R`/`RCZ`'s — yet `R`/`RCZ`'s demonstrably
exists, because the deck measured it. So silence is weak evidence in
*either* direction for the remaining four.

The only general statement anywhere is printed **p.22**: *"A refill
address of zero will replace the index word with all zeros"* — which
corroborates 2G's positive case and nothing else.

**Swept and negative**, so it need not be redone: routine 1238 in full;
routine **1242** (which is the dedicated `V+CR`/`V+ICR`/`V-ICR`
routine — see the correction below); routine 1248 test 5's progressive
blocks; routine 1250 (`CB`/`CBR`); `ja_ax1a`'s refill blocks;
`jb_ax2a`/`jb_ax3a`/`jb_ax5b` have no refill *operation* at all.
Every refill XW exercised in the corpus decodes to a high address or
an index register 16-31. The one low-address refill XW that exists —
`142XW4`, refill field 9 = `$R`, in routine 1242 — is **defined and
never referenced**, so it witnesses nothing.

If this is ever to be closed it needs a source outside the five I-Box
decks and the Reference Manual. `R23-9732_Manual04_7101_CPU_Jan63` and
`TR00.722_Stretch_I-Unit_Design_Mar60` are the untouched places where
an I-box refill-address decode rule would live; neither has been
searched.

**A SECOND DF SITE, RECORDED HERE BECAUSE IT IS NOT REACHABLE YET.**
The same p.27 paragraph continues: *"If the interrupt system is
enabled and if the old name is both out of bounds and invalid, the AD
and **DS** indicators are set. If the new name is both out of bounds
and invalid, the AD and **DF** indicators are set."* So `RNX` is an
address-alarm site for both DS and DF. It is moot today — `RNX`
decodes Operation Code Invalid in this model — but whoever implements
`RNX` owes those two clauses, and routine 1244's four-part header
(with its two indexed error tables) is a complete test plan for it.

**~~One boundary discrepancy to settle if `RNX` is implemented~~ —
RESOLVED 2026-09-24, and the manual was self-consistent all along.**
p.27 says `RNX` no-ops for locations 0-31; the deck sweeps 1-37 octal
(1-31). Printed **p.34**'s left column, read first-hand, is the same
rule split by address class: item **8** is *"Neither the old nor the
new name in a RENAME instruction may refer to location 0"* and item
**7** is *"In the operation RENAME, neither the old nor new name of
the index register can be in the range 1 through 15."* Location 0 +
the special registers 1-15 + the index registers 16-31 = p.27's 0-31.
So the deck simply does not test 0; there is no conflict to settle,
only a case with no deck witness.


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
  (16). **The MUTATION TABLE is subject to this rule too**, and broke
  it: two ZM mutants both hit `fpMul` because their pattern also
  matched `fpMulDouble` and `apply()` replaced only the first, so one
  copy of p.99's rule was untested by the suite *and* invisible to the
  campaign — 3059 PASS against a deliberate fault. A pattern matching
  twice is a tooling bug, not a mutant; `mutation_score.py` now
  refuses one.
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
* **`run_tests.sh` must not be edited while ANYTHING is running** —
  not "remember that `sh` reads by byte offset", just don't touch it.
  Violated twice in two days despite being on this list, the second
  time while a suite was 1290 checks in. Start the edit *after* the
  run reports, or kill the run first.
* **A direct-index address is HALF-WORD granular**, 18-bit word plus a
  one-bit half-word select — so an encoding oracle cannot see a
  special register's bit offset within its half-word. Measured:
  moving `$LB` from (3,32) to (3,33), (3,40) or even (3,63) fails
  nothing; (3,31) and (4,32) do. That bits 32-49 are the lower
  boundary comes from the pocket card and p.31, not from any listing
  row. Found by trying the obvious injection and watching it survive.
* **A substitution can discard the thing that makes a test useful.**
  Routine 1260's boundary driver branches into an EIGHTEEN-entry
  error table, `B,160B17($X3)`, indexed — so the halt address names
  which bit failed. A first transcription collapsed it to one hang;
  an injected bit-17 fault then branched past its end into untouched
  storage, decoded `BE,0` and ran to 0. Still "caught", but unable to
  say what. When a deck spaces a table, the spacing is the diagnosis.
* **A summary column is not a measurement.** `mutation_score.py`
  printed the first failing section; this file read it as "the
  catcher" and built a near-miss rule on it. Every application of
  that rule was wrong. The tell: ask what the number would look like
  if the thing it names were merely *earliest* rather than *causal* —
  and if you cannot tell the two apart from the summary, go get the
  raw output. Both retractions today came from reading full logs
  instead of a one-line attribution.
* **An instrument that runs in parallel needs its isolation checked,
  not assumed.** `mutation_score.py` gives each mutant its own cloned
  tree — and five test scripts then wrote a FIXED `/tmp` path outside
  it, so twelve jobs raced on one file and the campaign blamed
  whichever script lost. Ask what a parallel job touches that the
  clone does not cover: `/tmp`, build caches, `__pycache__`. Three
  separate bugs this session were the same shape — shared state behind
  apparent isolation. A fourth was self-inflicted: running a test in a
  tree a background job was mid-rebuild in, which `bsc` reported as a
  stale `.bo`.
* **When one document says a thing twice, check it does not say two
  different things.** `archival_inventory.md` described routine 1268
  in two paragraphs twenty lines apart — once as the deck test of the
  DF/IF *indicators*, once as a look-ahead *forwarding* test. Only the
  second was right, and `NEXT.md` item 2 was built on the first for a
  year of work. A summary is not a source; the routine's own header
  settled it in one reading.
* **A deck can be the WEAKER test.** Routine 1268's forwarding check
  passes on this model even with the store-queue drain removed,
  because it spaces its store and load one instruction apart — tight
  enough for the real machine's look-ahead, not for this model's
  shallower pipeline. The hand-written `ebox_register_close_to_fetch`
  catches what the 1961 diagnostic misses. Transcription is the
  stronger standard for *encodings*; it is not automatically the
  stronger standard for *behaviour*.
* **A claim nothing can express is a claim nothing checks.**
  `bsv/README.md` said Transmit backward/`SWAP`/multi-word all set
  indicator 15; only `backward` did, for as long as the assembler
  could not encode a Transmit at all. The corollary above is usually
  applied to tests; it applies to prose too, and the tell is the same
  — ask what input could falsify the sentence, and check that one
  exists.
* **Distrust a blocker recorded in this file.** FOUR times the thing
  stopping work was a claim here, not anything in the machine, and the
  fourth is the worst because the claim had already been corrected
  once: "DF and IF have no deck oracle anywhere read so far" (routine
  1260 TEST 8C, `jb_ax5b` PDF pp.76-83, is exactly that oracle, thirty
  pages before the routine whose misreading produced the claim — and
  the correction that fixed the local misreading left the global
  conclusion standing). The other three: "64 call
  sites need refactoring" (43 wrote constants that could never trip the
  rule), "the control-bit polarity needs Appendix C" (p.31 states it
  outright), and "1260 needs SSIP's `160S1` harness, reported at
  pp.41–44" (pp.41–44 are the per-indicator blocks, one of which was
  transcribed the same morning with no harness at all). Re-derive an
  obstacle before accepting it.
* **An interruption-reporting check needs room for the interruption.**
  A violation reported through a routine is only visible after the
  machine has actually taken the interruption, and this model takes it
  at a QUIESCENT boundary (look-ahead empty, E-box idle), not at the
  instruction boundary p.48 names — later, never earlier, as
  `StretchCore.bsv` says. The two storage-protection programs violate
  with a `BB` bit change and get away with one instruction of slack;
  `df_data_fetch_alarm.strap` violates with a VFL `ST`, which bails
  out once for its read-modify-write read, and one instruction was not
  enough. It halted with DS **on** in word 11 and word 6 still zero,
  which reads exactly like a protection bug and is not one. When a
  check fails, dump the indicator word before theorising: `run_program.sh`
  takes extra `label:addr=expected` checks and a deliberately wrong
  expected value prints the actual.
* **A check that cannot fail is not a check, and indicators make that
  easy to miss.** `df_data_fetch_alarm.strap`'s second block tested
  RGZ to prove an unmonitored load still landed — but the FIRST block
  had already left RGZ on, so the line could not have failed. Any
  indicator asserted more than once needs clearing in between, and the
  clear is part of the test, not tidying.
* **Neighbouring bit numbers need a check of their own.** DF is 20 and
  IF is 21. An injection that swaps them and an injection that removes
  the signal entirely both halt at the same address, so neither proves
  the *number* — until a line asserts the neighbour is OFF.
* **A branch target of `$+1.0` is wrong after a HALF-WORD instruction.**
  `CBR` is half-word format, so `$+1.0` from it is the *second*
  half-word of a following full-word instruction, not the next
  instruction. Written that way, `df_refill_index_alarm.strap` decoded
  garbage, raised OP, interrupted into a zero table entry — and still
  PASSED, because the interruption returned and every later check ran.
  The only sign was one line of stderr: "interruption instruction at
  4766 is E-box class -- not implemented". **Read the model's stderr on
  a green run**; a program can pass while doing something else entirely.
  `$+.32` is the next half-word; `$+1.0` is right only after a
  full-word instruction.
* **`run_tests.sh`'s PASS-line count is NOT a count of checks.** `run`
  does `tail -20 "$TMPOUT"` — deliberately, and its own comment
  explains why it must not be a pipeline — so every section's log is
  capped at twenty lines. On the 2026-09-23 run, **133 of 349
  sections were truncated**, so "3213 PASS" counts *displayed lines*
  and understates the real number by an unknown, varying amount. It is
  not even a stable proxy: adding a 32-row transcription moved it by
  19. Commit messages earlier that day quoted it as though it were a
  measurement; the green/red conclusions were still sound, because
  those came from `EXIT=0` and zero `TEST(S) FAILED`, but the number
  was not what it was called. **Report sections, not PASS lines**:
  `grep -c '^=== '` against `grep -c 'TEST(S) FAILED'`, plus the exit
  status. This is "a summary column is not a measurement" again, one
  level down — and the first version of the trap did not stop it,
  because the number *looked* like a count of checks.
* **A correction that fixes a local misreading can leave a false
  GLOBAL conclusion standing.** This file once said `jb_ax5b` routine
  1268 was "the only known deck test" of DF and IF. Reading 1268
  first-hand proved it is a look-ahead forwarding test, and the item
  was rewritten to say so — correctly. But the rewrite also asserted
  "so DF and IF have no deck oracle anywhere read so far", which does
  not follow from 1268 being the wrong routine, and nothing ever
  re-checked it. DF was then implemented to the weaker,
  manual-derived standard while routine 1260 TEST 8C sat thirty pages
  earlier in the same PDF, titled "TEST 8C CHECKS DF + IF UNDER 4
  CONDS". **When a correction retracts the reason for a claim, retract
  the claim too, or re-derive it.** The tell is a sentence that starts
  "so" and widens the scope of what was just disproved.
