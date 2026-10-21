# What to do next, and why

A standing work queue for the Stretch model, ordered by dependency.
Written so the next session starts from a decision rather than a
survey.

**This file is the plan, not the record.** The record of *how* each
piece was built lives in `docs/microarchitecture_plan.md`, in the
section comments of `tests/run_tests.sh`, and in commit messages.
When an item here is finished it shrinks to a pointer; it does not
accumulate.

## WHERE THIS STANDS, 2026-10-21 — read this first

MCP's **printed pp.17, 18 and 19 execute as one program**: an IOCD
card loop that reads a punched card, converts its Hollerith channel
number, looks up the equipment, builds the channel and unit status
tables, loops for the next card and exits through MCP's own
`X ERROR`. Four testbench modes cover it (no units / units / eight
units / disk). The card the fixture feeds it is a real one — the
column format is printed and the characters are punched through the
7030's own card code.

**The four things to pick from next**, in the order they unblock
things:

1. **`boot_plan.md` A3's remaining piece** — getting the IOCD cards
   onto the system tape the way the real system did, rather than
   preloaded by a testbench. The card format is now known; what is
   missing is more of MCP's loader.
2. **p.19 lines 27-53** — transcribed and bit-exact, but never
   executed. They move the status tables into upper storage using
   `$5`, `$8`, `$11`, `$12`, `$13`, none of which the testbench sets
   up. Running them needs that context from pages not yet
   transcribed.
3. **The back-matter sweep's worklist** (section below) — six ranked
   items, two already consumed. `C22-6728` printed 247-260, the rest
   of Appendix A, is the largest.
4. **Printed p.20 onward**, continuing the transcription.

**One caveat carried forward, deliberately not in this file's
worklist**: the look-ahead's store-fetch interlock is correct
architecturally and the suite agrees, but `waitFor` is documented in
`StretchLookAhead.bsv` as "done conservatively for any earlier
level". The real LAAR resolved these conflicts with specific timing.
That is fine while the order is MCP-first; it belongs to
`docs/microarchitecture_plan.md` and will need revisiting when the
ordering flips to cycle accuracy.

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
now has a deck behind it (`ax5b` I6086 says word 1, DS and "when
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
"SSIP's `I60S1`/`I60SX1` save/restore harness, reported at `ax5b`
pp.41–44". Those pages are 1260's per-indicator blocks, I6071 (`TS`)
through I6086 (`DS`). All four transcribable ones were done without
any harness — and then the driver itself (p.45) was done too. Third
entry in this file's own "distrust a blocker recorded here" trap.
`I60S1` = 022741.00 and `I60SX1` = 023041.00, read off the driver's
own printed address fields; nothing has needed either. The
page-by-page record is in `archival_inventory.md` §"I-Box 5".

**I6086, the DS block, is done** — `decks/ax5b_16086_ds.strap`,
bit-exact via `verify_ax5b_16086_listing.py`, record in
`run_tests.sh` §"I-Box 5 routine 1260's DS block". It is an ENCODING
oracle; storage protection's behavioural test stays hand-written.

**So are I6082 (`OP`), I6083 (`AD`) and I6071 (`TS`)** —
`ax5b_16082_op_ad.strap` and `ax5b_16071_ts.strap`, records in
`run_tests.sh`. **That is every transcribable block on pp.41–44.**
What remains there is out of reach for a stated reason: 16072–16081
are three-line `B`/`CNOP`/`DR` stubs for indicators a program cannot
provoke, 16084 needs `LVE` and 16085 needs `EX`, both deferred in
item 5.

**I6071 changes item 5's timer entry.** It is a second, eight-row deck
oracle for the interval timer — Reference Manual p.44, *"Time Signal
(TS). The interval timer has become zero."* — and it is in place
*before* the timer is implemented, which is the order item 2 asks for.
Routine 1258 is no longer the only oracle, and is no longer the
cheapest.

**The indicator walk at I6087/I6088 (p.45) is done** —
`decks/ax5b_16087_walk.strap`, and it brought **TRANSMIT/SWAP into
the assembler** (all eight mnemonics, from pocket card X22-6533; only
`TI` has a listing witness). Record in `run_tests.sh` §"…indicator
walk + TRANSMIT IMMEDIATE".

**That immediately exposed a silent bug, now fixed.** Making Transmit
encodable made two long-standing `bsv/README.md` claims testable for
the first time — and two-thirds of one was false. The decoder
discarded bit 57, so a forward `SWAP` executed as a one-word Transmit;
and the count was never read, so a multi-word Transmit moved one word.
Both silent. The decoder now captures bit 57, and **as of 2026-10-18
the arm honours any FORWARD count, immediate or direct** -- Reference
Manual printed p.30, with immediate 0 meaning *sixteen* and a direct
count read from the named index register's count field. It used to
honour only an immediate count of one, refusing every direct count
because the register went unread; MCP's printed p.4 line 28 is an
eleven-word direct-count transmit, so that refusal was stopping IBM's
operating system from moving itself into storage. SWAP and backward
are still refused. Guards: `decks/transmit_scope.strap` (six blocks,
one per rule -- three of them flipped from refusal to execution) and
`decks/transmit_multiword.strap` (fifteen checks on p.30's five
rules). Record in `run_tests.sh` §"TRANSMIT: what is honoured…" and
§"MULTI-WORD TRANSMIT".

**The boundary driver is found, and the guess it replaces was wrong
in range AND in kind.** This file said pp.66–79 held "the positive
boundary-interrupt cases" — an inference from a scouting pass, not a
page. Scanning pp.46–86 for BOUND/MONITOR on 2026-09-23 and reading
the hits gives the real layout:

| page | sub-test |
|---|---|
| p.65 | *"TEST 7 CHKS BOUNDARY CONTROL."* / *"CHK UPPER BOUNDARY DATA."* — driver at I6099/I60100 |
| p.67 | tail of the upper-boundary error table (BIT10–BIT17) |
| p.68 | *"CHK LOWER BOUNDARY DATA."* (driver I60102/I60103) and *"CHK BOUNDARY CONTROL BIT."* |
| pp.69–70 | the lower-boundary error table, bits 32–49 |
| **p.71** | *"FETCH FROM X-1 TO CHK UB COMP."*, *"FROM X-3 TO CHK LB COMP."* |

pp.65–70 test whether the **registers hold their bits**; **p.71** tests
whether the **comparison fires**, and p.71 is what "positive
boundary-interrupt cases" actually means.

**p.65 is transcribed and runs** — `decks/ax5b_16099_ub_data.strap`,
sixteen rows bit-exact, and it **catches a boundary fault and names
the bit**: dropping IBM bit 17 from `boundaryReg` halts it at
022263.00, the error table's eighteenth entry. Record in
`run_tests.sh` §"…TEST 7".

**p.68 is transcribed and runs too** —
`decks/ax5b_160102_lb_ctl.strap`: the lower-boundary loop and the
control-bit test, 37 rows bit-exact, and it localises a fault to the
bit (drop IBM 49 → the table's "BIT 49" entry; drop IBM 57 → `SERS`
with *"UNABLE TO SET BNDRY CNTRL TO 1."*).

**p.71, the comparisons, is transcribed** —
`decks/ax5b_160105_compare.strap`, 52 rows bit-exact on first
assembly. This is the block the item always wanted: it sets bounds,
**enables**, fetches outside them and expects an address-monitoring
interruption (*"UB HAS X, LB HAS X-2. FETCH FROM X+1 TO CHK UB COMP,
FROM X-3 TO CHK LB COMP, AND FROM X-1 TO CHECK WITHIN RANGE"*). It is
also the first use of `TI` outside the page it was derived from.

**ENCODING ONLY, and this is where the harness finally matters.** It
cannot run without `I60S1`'s body (SSIP's save/restore at 022741.00),
the interruption table `I60IT` at 023201.00, and `BOUND0`/`BOUND1` at
023302/023303. Every earlier block in this routine was transcribed
*without* a harness, which is why the file's original "prerequisite"
claim was wrong. This one needs it for real.

**`I60S1` IS TRANSCRIBED** — `decks/ax5b_160s1_clr_inds.strap`,
pp.83-84, 81 rows bit-exact — **and it is not what this file has ever
called it.** PDF p.83, 022741.00. The original claim was "SSIP's
`I60S1`/`I60SX1` save/restore harness"; the correction after that said
they were "call sites… still not located". Both were wrong about what
it *is*. Its own comment:

> `I60S1  SX,$X1,I60DMP   -SUBROUTINE TO CLR INDS 0-19,`
> `       BMKZ,$+.32      -AND CHK THAT THEY ARE CLRD.`

It is a **clear-indicators-0-19 subroutine local to routine 1260** —
it clears each permanently-masked indicator with
`TI,1,11.0,$X1` (Transmit Immediate into word 11) and checks it went
off, with a per-indicator message: *"UNABLE TO CLEAR MK."*, *"…CLR IK
OR ABOVE IND."*, then IJ, EK, TS, CPUS. Roughly forty rows, every
instruction already implemented, and it needs no harness of its own.

So the comparison block's real dependencies are `I60S1` (now
transcribed), the interruption table `I60IT` at 023201.00, and
`BOUND0`/`BOUND1` — none of them the mythical SSIP harness.

**And transcribing it found an assembler bug.** `I60S1`'s one `XW`
row was the single mismatch in 45: `XW`'s fourth operand is **three
bits** (IBM 25-27, the index flag plus two spare) and `strap_asm.py`
masked it to one, so `,4` and `,2` encoded as zero and `,1` set the
flag instead of the second spare. p.114's own table settles it —
`BIT25` is `XW,0,0,0,4`, `BIT26` `,2`, `BIT27` `,1`. Fixed.

**Next on item 1**: the interruption table `I60IT` at 023201.00 and
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
022546.00-022732.40, labels I60127-I60146.** Verified first-hand at
400 dpi. Its own title row:

```
I60127  LVI,$X1,I60AD1  -TEST 8C CHECKS DF + IF UNDER 4 CONDS,  23063.03 01  022546.00
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
* **TEST 8B, PDF p.75** (I60123-I60Z1, 022513.00-022545.40) — a
  second, richer DS oracle covering enabled/disabled *and* store
  suppression: *"-SX ABOVE UB WAS NOT NOPED, DATA WAS STORED WHEN
  ENABLED."*
* **TEST 7, PDF pp.71-74** (I60105-I60122) polls DF with `BDFZ`/`BZDFZ`
  throughout — a second DF oracle, on the boundary-compare path.
* **p.32's BRANCH clause is still manual-only.** Every IF case in
  TEST 8C is straight-line fall-through into a below-LB region; none
  branches into one. "the entire branch operation ... is suppressed"
  has no deck test in this corpus.
* **The header discrepancy is RESOLVED: line 1's "IND" is a typo, and
  the code requires DF and IF NOT set.** Settled 2026-09-24 by
  transcribing cases 1 and 2 themselves
  (`ax5b_160_test8c_disabled.strap`, 114 rows). Four independent
  lines of evidence, strongest first: (1) cases 1 and 2's indicator
  branches are **bit-identical in polarity** — `BZDFZ` prints `...12
  44` / `...52 44` and `BZIFZ` prints `...12 C4` in both — so
  whatever `BZ` means, the two cases assert the SAME thing, and "IND"
  on line 1 cannot be right unless "NO IND" on line 2 is also wrong;
  (2) the failure text inverts exactly where the expectation does —
  cases 1 and 2 print "-CAUSES DF TO BE SET, NO INT." while case 3,
  whose header says "IND ON", prints "-CAUSES DF **NOT** TO BE SET";
  (3) the mnemonic grammar `B[Z]<ind>[Z]` makes the leading Z branch
  when the indicator is OFF, and in both disabled cases the branch is
  the OK path; (4) the same header line 2 spells DISABL as "DIAABL",
  so it is demonstrably typo-prone.

  **And the two disabled cases are NOT redundant with each other.**
  Disabled, the deck asserts the mask bit is IRRELEVANT: case 2 sets
  DF's and IF's mask bits to ONE and still demands the fetch proceed
  ("-UNABLE TO FETCH ABOVE UB WITH / -MASK 1, SYSTEM DISABLED."),
  where case 4 — enabled, mask 1 — demands the same fetch be
  suppressed. That pair is the enable gate stated from both sides.

  **Caveat the transcription records**: this settles what the DECK's
  code requires, not what the hardware did. The manual's own answer is
  p.32's "the DS, DF and IF indicators cannot be turned on when the
  system is disabled", which agrees.

**TEST 8C CASES 3 AND 4 ARE NOW TRANSCRIBED** —
`decks/ax5b_160_test8c.strap` +
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

**IF CLASS 2 IS IMPLEMENTED** — "the branch address of all successful
branch operations", `ifSignal` in `StretchExecute.bsv` at execute()'s
single commit point, tested by `decks/if_branch_alarm.strap`.
Deliberately the half WITHOUT the strong oracle, because it is the
half that is self-contained: it needs no new plumbing, whereas class 1
needs the interruption-address exemption threaded (below).

**DF'S MASK-DEPENDENT HALF IS IMPLEMENTED** — 2026-09-24,
`dfSuppresses(st, a) = maskedOn(st, ind_DF) && protViolates(st, a)`, at
the four class-1 `dfSignal` sites; when it fires the whole arm is
skipped and `next` is left alone so the IC still steps. Sourced from
printed p.32 (the rule), printed p.45 indicator 20 (*"the fetch did not
take place, and **the entire operation was suppressed**"*, which is what
licenses skipping the arm rather than only the fetch) and printed p.52
item 3 (the IC still steps). Tested by
`decks/df_fetch_suppress.strap` + `StretchDfSuppTb`, seven
injections, none survived. **Every check observes the DESTINATION'S
VALUE rather than the operation's result indicators** — a model that
"suppressed" by writing zero would pass an indicator check and fail
this one.

### CLOSED 2026-09-25 — the fifth site is built, and it exposed a second bug

All three of printed p.52's `BRANCH ON BIT` clauses are implemented in
the `BitBranch` arm, tested by `decks/df_bb_readonly.strap` +
`StretchDfBbRoTb`, eight injections, none survived. **The encoding was
checked against the decoder rather than inferred**: `StretchDecode`
takes `modAbc = w[3:1]` and IBM bit *n* is BSV bit 63−*n*, so
`modAbc[2:1]` **is** IBM bits 60-61 — p.52's "not both zero" is
literally the arm's existing `changes`, read from the other side.

**AND CLAUSE 1 DID NOT ALREADY MATCH, which is the second finding.**
The model suppressed clause 1's branch and bit change but still
*computed the branch condition from the tested bit*, then signalled IF
from the branch target of an instruction p.52 says was never decided —
forbidden by the same page's AD sentence (*"suppressed … since no bit
can be tested to complete its execution. **Indicator IF cannot be
actuated.**"*). Fixed by splitting `wouldBranch` from `takeBranch =
wouldBranch && !noTest`. Measured, not argued.

**STILL UNTESTED, and recorded rather than left to be rediscovered:**
`ifSuppress` also gates the bit change, so a modifying `BB` with a
protected data word AND a protected target AND IF's mask at one used to
lose clause 1's DS actuation entirely. The fix restores it, but the
test block runs IF's mask at zero deliberately (a mask of one re-routes
the injection that witnesses the finding above), so this wants its own
block.

### CLOSED 2026-09-25 — the refill suppression gap

Six of the eleven class-3 sites now suppress: `CBR`/`CBRZ`, `V+CR`,
`V+ICR`, `V-ICR`, and `R`/`RCZ` on both paths.
`decks/df_refill_suppress.strap` + `StretchDfRfSuppTb`, nine
injections, none survived.

**The scope line got a structural confirmation.** Printed p.53's
progressive-indexing sentence is not merely a different rule — it is
item 3 under **"Execution Terminated"**, on the facing column from
"Execution Suppressed". The two mechanisms are separated by the
manual's own headings, so the five progressive-indexing sites stay out
of scope on the page's authority rather than on judgement.

**And printed p.52 is a better source than p.45 for the hard half.**
p.45 leaves open whether a suppressed count-branch-refill still
branches; p.52 works the case by name and says it does not, *"since the
test for the refilling is independent of the test for a successful
branch"* — endorsing the shape the model already had.

**ONE INJECTION SURVIVED and the gap is bounded rather than waved at:**
making `evalBranch`'s suppression fire only on the second pass (read
issued, then arm skipped) still passes. A refill read writes no
storage, sets no indicator, and the model exposes no cycle or read
count to a STRAP program, so the only trace is the prefetch slot — and
its one consumer, `SIC`, requests its read only `if (o.taken …)`, which
a suppressed `CBRZ` never is. The ordering rests on p.45's wording, not
on a test.

**ONE OPEN QUESTION LEFT IN THE CODE rather than decided by
invention:** on `R`/`RCZ`'s external-memory path, if the OPERAND word
is also protected, the suppressed arm no longer reaches the `DS` signal
it used to set. p.52 item 1 argues DS should still actuate; p.32's *"if
an address … is not actually used, it will not be monitored"* argues it
should not. No deck witnesses it, no program in the suite reaches the
combination, and it is reversible in one line.

### CORRECTION, 2026-09-24: "DF class 1 is complete" WAS FALSE, and was false before that change

**Class 1 has FIVE sites, not four.** The fifth is read-only BRANCH ON
BIT, and printed p.52 gives it explicitly — verified first-hand at 300
dpi:

> *"since a protected effective bit address in BRANCH ON BIT could
> result in the destruction of information, alert DS or DF may occur
> if: 1. The addressed bit is not specified to remain unconditionally
> unchanged; that is, bits 60 and 61 of the instruction are not both
> zero. The instruction is suppressed without a test of the addressed
> bit, and indicator DS is actuated. 2. The addressed bit is specified
> to remain unconditionally unchanged, and the DF mask bit is one. The
> instruction is suppressed without a test of the addressed bit, and
> indicator DF is actuated. **3. The addressed bit is specified to
> remain unconditionally unchanged, and the DF mask bit is zero.
> Indicator DF is actuated but does not cause suppression of the
> instruction.**"*

The BitBranch arm computes `storeViolates = changes && protViolates(st,
bw)` and never calls `dfSignal`. So **a read-only `BB` (bits 60 and 61
both zero) against a protected word raises NEITHER indicator today** —
and clause 3 makes that a gap in the INDICATOR, not merely in the
suppression. It is its own piece of work: the fifth site's suppression
has to interact with the branch commit point one arm over, so it wants
its own program rather than a line added to an existing one.

**Note the shape of this error, because it is one this project has now
made twice.** The completeness claim was written when four sites were
found and all four were handled; nothing was miscounted, the fifth was
simply never looked for, and the claim was phrased as though the search
had been exhaustive. That is the same shape as the DF-has-no-oracle
claim § 2's earlier CORRECTION retracts. **"All N sites are done" is a
claim about a SEARCH, not about the code, and it needs the search
stated.**

**TWO FURTHER DF GAPS, deliberately kept distinct because they are
different kinds of thing:**

* **Progressive-indexing refills are SCOPED OUT, not missing.** Printed
  p.53: *"An alert of Class S during progressive indexing suppresses
  only the indexing portion of the operation."* That is a different
  mechanism — terminate, not suppress — and implementing it is separate
  work.
* **`R`, `RCZ`, `CBR`, `V+CR`, `V+ICR`, `V-ICR` refills are a plain
  gap with no excuse.** Printed p.32 class 3 names them as their own
  category, so p.45's "entire operation was suppressed" applies to them
  directly.

**AND ONE THING LABELLED AN INFERENCE IN THE CODE ITSELF**, because no
deck can settle it: that suppression also kills the result indicators,
the progressive update and the index-result indicators. p.52's list is
framed as everything that survives, so it follows by closure — but the
manual never says it, and TEST 8C case 4 re-actuates the indicators
with a fresh `LX` before testing them, so the oracle is silent too.
This is the same open question § 6 already records; it now has a second
instance.

**REMAINING ON THIS ITEM — REWRITTEN 2026-09-25, because the first two
entries were DONE and this file still listed them as open.**

~~1. IF CLASS 1~~ — **DONE**, commit `5fbb8b0`. `execute()` carries
`if (!atIntAddr) ind = ifSignal(st, pc[18:1], ind);` and
`decks/if_branch_alarm.strap` + `StretchIfBrTb` is wired into the
suite. Everything the old entry prescribed was followed: the signal
sits at dispatch rather than `fetchReq`, it is computed inside
`execute()` from `pc` to avoid the G0004 second-writer shape, and
p.32's interruption-address exemption is threaded as one `Bool`.

~~2. The mask-dependent half of DF, DS and IF~~ — **DONE for DF and
IF, and WRONG ABOUT DS.** IF's landed with class 2; DF's landed in
`9b49f3a` (the four class-1 sites), `939605f` (the fifth site and the
six refill sites). **DS has no mask-dependent half to implement**:
printed p.32 says *"Since this indicator is permanently masked on,
storing in core storage is always suppressed, and the operation is
always terminated"*, and mask bits 0-19 are permanently one. The
model's own comment above `protViolates` has said so all along. This
entry asked for something that cannot exist.

**HOW BOTH ENTRIES WENT STALE IS THE SAME SHAPE THIS FILE KEEPS
RECORDING.** Neither was miscounted or mis-implemented — the work was
done, committed, and wired in, and nobody re-read the list that said it
was pending. A plan item is a claim about the CURRENT STATE, and a
claim about state decays silently: nothing fails, nothing warns, and
the next reader is handed work that is already finished or impossible.
This is the fourth instance in two days, after "DF has no deck oracle
anywhere", "class 1 is complete", and two agent briefs asserting a
block was untranscribed. **Before handing out an item from this list,
check it against the code and the suite — the same way you would grep
before claiming a block is untranscribed.**

3. **p.32's branch-SUPPRESSION clause still has no deck test anywhere
   in this corpus** — "the entire branch operation, including any
   counting, bit changing, or index alteration, is suppressed". Class
   2 now sets the indicator; suppressing the branch is the
   mask-dependent half, and `ds_terminates_branch.strap` is the
   nearest thing to it (DS's termination, which IS implemented).

4. **`ifSignal`'s `a >= 32` guard is unwitnessed**, and its injection
   survived. Testing it needs a taken branch to words 1-3, whose
   contents would then execute — and those are the boundary registers
   that define the monitored area. The model also does not raise AD
   for a low branch (p.45), so the case is doubly unmodelled.

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

**Left on 1268**: cases 1B and 1C. They were blocked on `EX`; `EX`
is implemented as of 2026-09-25 (item 4a), and their ENCODING is
already transcribed as `decks/ax5b_1268_test1bc.strap`, so what is
left is a runnable slice, not a missing instruction.

## 3. Smaller open pieces inside what is built

* **Interruption timing. MEASURED AND MOSTLY CLOSED, 2026-09-25.**
  This bullet's claim was tested rather than believed, and it was
  right about the *conclusion* and wrong about the *mechanism*.

  **The mechanism it names does not apply.** It says a `BD` clears a
  pending interruption because the I-box races past the provoking
  instruction. It does not race: `iboxHazard`'s `BranchOrMisc` arm is
  `h = (x.code != 3'b110)`, so every unconditional branch — `BD`
  included — drains the look-ahead before it executes (Perf. Char.
  p.3-18, *"BD … empty the LA completely"*). **The real cause was one
  term**: `armInterrupt` waited for `ebusy == 0`, the CHARGED TIME of
  the instruction just removed from a look-ahead level — not a
  structural busy, and not something `rl_prepare` waits for. So every
  I-box instruction that fitted inside the E-box's charged budget ran
  first, `BD` among them.

  **How late, measured.** `decks/int_timing_bracket.strap`: a VFL
  `ST` whose store is suppressed (DS, indicator 19, permanently
  masked), bracketed `BE` / `ST` / `BD`, with N `NOP`s of slack before
  the `BD`. Observed halts, before the fix: N=0 → 004110.40 (`CHK`,
  no interruption), N=1 → 004111.00, N=2 → 004111.40, **N=3 → PASS**,
  N=4 → PASS. **Three instructions of lateness where p.48 allows zero
  and the deck leaves one.**

  **Fixed, by deleting one term from one predicate** in
  `StretchCore.bsv`: `armInterrupt` no longer waits for `ebusy`. The
  bracket program then passes at N=0, halting at 004113.00 (`PASS`).

  **There is a SECOND line in the change, and NOTHING TESTS IT.**
  `rl_interrupt` now ends with `ebusy <= eb;`, as every other arm
  does. It is necessary — before the fix `rl_interrupt` could not fire
  while `ebusy != 0`, so it never had to decrement it; now it can, and
  without the line the E-box's charged clock would freeze for one
  cycle. But no injection removes it and no test could see it if it
  were wrong: the three `CYCLES<=` benchmarks never enable the
  interruption system, and the tests that do interrupt check halt
  addresses, not cycles. Stated here rather than left to be found.

  **The other candidate was measured and ruled out.** `interruptDue()`
  is latched — an every-clock rule publishing its answer one clock
  after the indicator is written — and its own comment says that clock
  is one "which no program can observe". Restoring the latch with the
  `ebusy` term already gone, the bracket program still passes. So the
  latch is not what the deck's bracket would have caught, the comment
  stands, and `StretchStorage.bsv` is left alone.

  **What is still open, and it is the harder half.** An I-box-class
  instruction the I-box has already run AHEAD of a pending level is
  committed and cannot be taken back, so an indicator set by a level
  is still not reported before an I-box instruction that overtook it.
  `iboxHazard` keeps that narrow — unconditional branches, branches on
  non-index indicators and stores to E-box registers all drain first —
  but does not close it. Closing it needs the look-ahead to be able to
  unwind, which is the `recover` path generalised from wrong-way
  branches to interruptions.

  **`run_tests.sh` is STALE on this** (two places: the
  `df_data_fetch_alarm` note near "THE NOPS AFTER EACH STORE ARE NOT
  PADDING", and the `interrupt_pg0` note "NOT IMPLEMENTED, stated in
  StretchCore"), and the bracket program is **not yet in the suite**.
  Its run line is
  `run "…" ./run_program.sh decks/int_timing_bracket.strap StretchIntTimingTb "PC=4246"`.

  **THE DISCRIMINATOR EXISTS AND IS ALREADY IN `decks/`** —
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
  ENCODING-ONLY and unrun — they need `I60S1`'s body and the `I60IT`
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

`python3 tests/mutation_score.py --jobs 12` — each mutant gets its own
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
`decks/fp_zm_terms_double.strap` is the witness. 36 mutants.

**So: a mutation score is evidence about the sites the table names,
and nothing else.** Before trusting one, check the table can still
reach every site it claims — that check is now automatic.

`python3 strap/line_addresses.py decks/X.strap` prints every
instruction line's address in the listings' octal convention. Every
injection address a new test records should come from it, and it
reproduces the ones already recorded — which is what makes them
checkable rather than folklore.

## 4a. BOTH EXECUTION OPERATIONS ARE BUILT — `EX` 2026-09-25, `EXIC` 2026-09-29

**`EX` executes.** The arm is in `StretchExecute.bsv` (the
`BranchOrMisc` misc code `010`), the subject swap is in `mkEBox`'s
`resume()`, and the EXE suppression is in the five branch arms.
Driven by `decks/ex_subject.strap` (subject with an operand
of its own, two-level `EX`, the subject word left intact, a
full-length subject straddling two storage words), `ex_exe.strap` (the
EXE rule over BB / unconditional / CB / SIC / BE / BD),
`ex_exe_bind.strap` (the EXE rule over BRANCH ON INDICATOR, including
the trailing-Z CLEAR) and `ex_monitor.strap` (p.32 class 1 on the
subject's location, p.50's below-32 carve-out, the subject held in a
register, and the two-level accumulation of the alarm). **Fifteen
injections, every one observed and every one caught**; each program's
header carries its own table with the halt address and the source row.
`EX` has left `audit_opcode_coverage.py`'s `ENCODING_ONLY` set.

**`EXIC` EXECUTES TOO (2026-09-29).** Its arm is the misc code `011`
beside `EX`'s `010`; `exicPsicAddr` is its address function; `ExicCtx`
and `HeldOp.exic` carry the level's state; `mkEBox.resume()` grew from
three shapes to five; and `subjReady` gives the step its own clock.
Driven by `decks/exic_subject.strap` and `exic_addr.strap`,
sixteen injections, every halt observed, none survived. `EXIC` has
left `audit_opcode_coverage.py`'s `ENCODING_ONLY` set, which is now
`RNX` alone.

**THE ESTIMATE THIS ITEM USED TO CARRY WAS WRONG IN TWO WAYS, and both
are worth keeping**, because they are the shape of "reuse" estimates
in general. It said `EXIC` needed "its own `exSubjectAddr` case (one
indirection more), a pseudo-IC step between fetch and execution sized
by the subject's length, and its two address restrictions".

* **`exSubjectAddr` CANNOT BE REUSED AT ALL, not even with another
  case.** That function answers "where is the subject" from the
  INSTRUCTION. `EXIC`'s subject address is not a function of the
  instruction: it is a function of a word that must be fetched first.
  So `EXIC` has a separate `exicPsicAddr` returning the COUNTER's word
  address, `HeldOp` carries a new `Maybe#(ExicCtx)` whose Valid-ness
  is the invariant "`di` is an EXIC whose counter has been read", and
  `resume()` dispatches on that before anything else.
* **THE STEP IS A STORAGE WRITE, AND THAT COSTS A CLOCK.** A module
  method may be called once per rule, and a subject instruction may
  itself write storage, so the step and the subject cannot share a
  clock — which is, conveniently, exactly what p.50 describes ("after
  the subject instruction has been fetched but prior to its
  execution"). `mkEBox` writes the step, installs the subject and sets
  `subjReady`; `canResume()` honours that flag IN PLACE OF the read
  handshake, so the next `rl_exec_resume` runs the subject with no
  read outstanding. Nothing else can observe the extra clock: `held`
  stays Valid, so `ebox.busy()` blocks the interruption and look-ahead
  arms and `canResume()` blocks `rl_prepare`, exactly as during a
  read. **`StretchCore.bsv` still needed no change**; the only other
  file touched was `StretchIBox.bsv`, comment-only, as for `EX`.

**AND A THIRD RULE THIS ITEM NEVER MENTIONED**, found by reading
printed p.32 for this work rather than taking the p.50 paragraph as
the whole contract: *"Address monitoring for Data Store includes: ...
5. The effective address of EXECUTE INDIRECT AND COUNT."* The counter
is read AND written, so it is a store-type address, and p.32's
store-type rule is *"storing in core storage is always suppressed, and
the operation is always terminated"* (p.45 item 19: "The operation was
suppressed"). The arm therefore raises **DS** and terminates BEFORE
the counter is read. The same page also settles a question `EX` had to
argue around: *"Address monitoring for Instruction Fetch includes: ...
3. The location of the subject instruction of the EXECUTE and EXECUTE
INDIRECT AND COUNT operations WHEN THIS LOCATION IS IN MAIN
STORAGE"* — so for `EXIC` `ifViolates`' `a >= 32` guard is p.32's own
wording, not a different rule that agrees numerically.

**WHAT `EX` DELIBERATELY DOES NOT DO**, each a bounded negative rather
than a guess:
* **`USA`** (p.45 item 17), the one-millisecond timeout — "the
  operation is terminated wherever it may be and the program
  proceeds... this indicator is the only means of breaking out of a
  loop that occurs as a result of a programming error in the use of
  execution operations or indirect addressing." An `EX` chain that
  closes on itself spins one clock per level in this model until the
  harness's step cap. `StretchCore` does keep a clock counter, so the
  missing piece is not a clock but a *number*: how many of this model's
  clocks a millisecond is, which needs a documented cycle time and a
  documented count (the deck builds a chain of **2049**, which is a
  number about the machine, not about this model). Timing claims here
  need a documented number behind them (AGENTS.md), so this is left
  undone rather than approximated.
* **p.50's two special exceptions.** "Address monitoring is always in
  force during (1) EXECUTE and (2) EXECUTE INDIRECT AND COUNT" and "at
  the completion, termination, or suppression of an execution
  operation, interruption is always permitted" — both of which
  override the *disabled* state. `protViolates` gates on
  `st.irqEnabled()` at some thirty call sites and `interruptDue` gates
  on the same bit, so honouring either needs an "execution operation
  in progress" state threaded through `StretchStorage`. That is its
  own piece of work, and it is what the deck's 1CA/1CB/2CA/2CB test.
* **The EXE suppression of BRANCH ON INDICATOR's indicator CLEAR** is
  an inference from p.49's "and so on" plus p.45 item 18's "the
  subject operation was suppressed", with **no deck witness**: 1262
  TEST 1CC's branch-on-indicator subject class is on PDF p.92, outside
  the transcribed range. Flagged in the arm itself.
* **A Class S alert arising during a subject instruction** (p.52's
  "may not cause full suppression of the instruction", p.53 item 2b).
  None of it is implemented.

**Unblocked now that both execute**: `jb_ax5b` routine 1268 cases
1B/1C (`EX,$X3`, `EX,$R`) and routine 1260 blocks 16084 (`LVE`) /
16085 (`EX`).

**WHAT `EXIC` DELIBERATELY DOES NOT DO**, beyond the four `EX`
negatives above, which it inherits unchanged:
* **printed p.51 item (d)** — "If the address of the location of the
  subject instruction of EXECUTE or EXECUTE INDIRECT AND COUNT is both
  protected and invalid, indicator IF will be actuated. Indicator AD
  will not be actuated as a result of this invalid address unless the
  IF mask bit is zero." For `EXIC` "invalid" now has a meaning it does
  not have for `EX` (below 32.00), so the corner is REACHABLE here
  where it was hypothetical there. The arm raises AD and never IF.
* **THE COUNTER'S 0-15 BOUNDARY IS THE MANUAL'S, AND THE DECK SAYS
  SOMETHING ELSE.** p.50: "cannot occupy locations addressed between 0
  and 15". Routine 1262 TEST 3A's three error messages: "LESS THAN
  15". No row discriminates — the deck's counter is word 9, illegal
  under either reading. The model takes `pw < 16`, which is the
  manual's reading and the only one the storage map supports (0-15 are
  the special registers; 16-31 are the index registers, which the same
  sentence expressly ALLOWS, and `exic_addr.strap` block A2 pins word
  16 as legal). A deck row with a counter at word 15 would decide it.
* **p.32's suppression is worded "storing in CORE STORAGE is always
  suppressed"** while p.50 expressly lets a counter live in an index
  register. The model applies the boundary test uniformly; nothing
  read for this work says what the boundary registers do to a
  register-resident counter, and no deck row reaches it.

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
| TEST 1B | 90-91 | 023373.40-023442.00 | `I6212` | EX of each non-branch class, **two** checks per class |
| TEST 1C | 92-94 | 023442.40-023551.00 | `16218` | 1CA enable-after-EX, 1CB address monitor, 1CC EX of branch + EXE |
| TEST 1D | 95 | 023551.40-023576.00 | `16241` | EXE and USA indicators |
| TEST 2A | 96-98 | 023576.40-023704.40 | `16247` | EXIC must not relinquish control |
| TEST 2B | 99-102 | 023705.00-024000.00 | `16260` | EXIC of each class, **three** rules per class |
| TEST 2C | 103-105 | 024000.40-024107.40 | `16271` | 2CA/2CB/2CC, the EXIC twins of 1C |
| TEST 2D | 106 | 024110.00-024135.40 | `16294` | EXE and USA for EXIC |
| TEST 3A | 107-108 | 024136.00-024151.00 | `I62100` | pseudo-IC less than 15 |
| TEST 3B | 108 | 024151.40-024162.00 | — | subject instruction less than 32 |
| constants | 109 + p.110 top | 024172.00-024332.00 | `I62K1`..`I62EXI` | incl. the 64-word `I62INT` table at 024220.00 |

Continuity bits corroborate the partition: 1A=BIT0 ... 2D=BIT7, TEST
3=BIT8, and the exit mask `%8@777000.0` is exactly nine ones. Nine
sub-tests, nine bits.

**TWO EXTENT CORRECTIONS.** 1262 does **not** end at p.109 — its last
row, `I62EXI LVI,$X1,%8@777777.40`, is at 024332.00 on the **top line
of PDF p.110**, above routine 1268's header. And `I62EXI` is
*referenced* on pp.90, 92, 103 and 107 while being *defined* past
where anyone would look.

**A HEADER THAT MISDESCRIBES ITS OWN TEST, flagged not smoothed.** The
routine header says test 3 checks "THE ILLEGAL COMBINATIONS OF EX AND
EXIC". 3A and 3B are both **EXIC-alone address-range** violations.
There is no EX-with-EXIC combination test in test 3; the nearest thing
is TEST 1A's two-level EX-of-EX. Do not go hunting for tests that are
not there.

### FIRST TRANSCRIPTION TARGET: TEST 3A, `I62100`, 024136.00-024151.00, 23 rows

Chosen over the smaller head of `1621` (13 rows) for reasons that are
about evidence, not size: it is a **whole sub-test** entered by one
`BD,I62100`; both its error messages are **inline in its own comment
column** rather than an index into a shared table, so a failure names
itself; it encodes **EXIC**, the harder arm; and its three messages
*are* the suppression contract — no interrupt on the illegal
pseudo-IC, AD set, the instruction NOPed — which is exactly p.50's
"cannot occupy locations addressed between 0 and 15".

**AND IT AVOIDS AN ASSEMBLER PREREQUISITE.** TEST 1A and 1D use
progressive-indexing notation `%$X1@` (`SX,$X2,I62INT%$X1@`) that
appears in **no** existing `decks/*.strap`, so they would
carry an assembler change as well. 3A uses none of it, and its one
exotic row (`%8@DD%BU,32,8@,3740 -ILLEGAL OP.`) is *already*
transcribed and bit-exact-verified here as `I60K7` in
`ax5b_160k_constants.strap`.

**Not candidates:** TEST 1D and 2D depend on `I6084A`/`I6084B`, which
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

**BUILT, 2026-09-25, exactly as proposed here.** `EX`'s arm returns
`needsRead` = the word holding the subject, exactly like any operand
fetch. Then `resume()`, seeing the held instruction is an `EX`
(`exSubjectAddr` returns Valid), **decodes the fetched word and
installs the SUBJECT as the held instruction** — `execute(...,
decode(hw0, hw1), emptyPrefetch, 0)` instead of re-running the `EX`.
The subject's own `needsRead` then works normally, because it is now
the held instruction. No recursion, no second `execute()`
instantiation, and the cycle it costs is one the bail-out already
pays. Two details the proposal did not foresee: a full-length subject
beginning at an odd half-word straddles two storage words and needs a
second read before it can be decoded at all (1262 TEST 1CC's own
`I62B6` is that shape), and the class-1 address alarm for an
intermediate level's subject location has to be carried forward
because a bailing call's indicator word is discarded.

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
indicators; `LOC` and the unimplemented `CTL` function codes.

~~19-bit address truncation (routine 1274)~~ — **REMOVED 2026-09-25.
It was never a model gap.** `StretchTypes` types `WordAddr`/`HWordAddr`
as exactly `Bit#(18)`/`Bit#(19)`, so five of routine 1274's seven
subjects truncate by construction. The sixth, 024455.00, discriminates
on SCALING rather than width, and the model is already correct there —
it sends Transmit's A2 through `effAddr19`. What was actually deferred
was TRANSCRIBING the routine, and that is done:
`verify_ax5b_1274_truncation_listing.py`, 99 rows, in the suite.

### THE INTERVAL TIMER — the rate is SOURCED, and 1258 is located

**DONE 2026-10-16. The timer and the time clock step.** Everything
below is the research that made it cheap; it is kept because every
hazard it predicted was real. What landed:
`bsv/StretchTiming.bsv`'s `oscPulseNumer`/`oscPulseDenom` divide the
0.3 µs model clock by the **exact rational 78125/24** rather than
rounding 3255.2083 (Bresenham: 24 ticks are exactly 78125 clocks, 19
intervals of 3255 and 5 of 3256, no long-run drift);
`StretchCore.bsv`'s `rl_clock` carries the accumulator and pulses
`st.oscillatorPulse()`, gated on `tick` exactly as the hazard note
below demands; `StretchStorage.bsv`'s `oscillatorStep` is the ONE
writer of `intervalTimerAndClock` and does the countdown, the unused
bits 19-27, the time clock's count-up and TS's 1→0 edge, with
`commitIndicators` the ONE writer of `indicators` — the `storeW`
funnel shape this note predicted. The reload needed no special case:
0 − 1 modulo 2¹⁹ *is* all ones, so the faithful rule and the plain
modular decrement coincide, and the "naive wrap every 3255 clocks"
disaster below never had a way in.
`decks/interval_timer_steps.strap` checks the six
behaviours, and the one-instruction `BTS` before its block 4 is what
separates "TS on the 1→0 edge" from "TS when the new value is zero"
(injection: halts at F3T). The six `CYCLES<=` benchmarks are
unchanged to the clock, including the 4003-cycle I-Box 1 span, which
is the only one longer than a tick. One thing this note did NOT
predict: `oscillatorPulse` is part of the `StretchStorage` interface
and therefore also an exported `mem_` method at `mkStretchCore`'s
boundary, so a plain `mkPulseWire` made it conflict with `rl_clock`
and broke that rule's `fire_when_enabled` (G0005). `mkPulseWireOR`
fixes it; see the comment on `oscPulse`.

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
I589/I5810, *"-INTERVAL TIMER FAILS TO STEP FROM 000000.0 TO
777777.40"*, with `I58K1 = 777777.40` — all ones in bits 0-18.

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

**It is a far better timer oracle than I6071**, which only witnesses
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

## 5a. FIGURE 11 — the normative class table this project did not know about

**Reference Manual printed p.43 (PDF 46), "Indicator List".** Found
2026-09-24 and verified first-hand at 400 dpi. It has a **Class**
column that says, per indicator, what happens to the instruction the
indicator fires in:

```
19  DS   1   P,S       Data Store
20  DF   m   P,S*,C    Data Fetch
21  IF   m   P,S*,C    Instruction Fetch
*Class S when mask is one;  otherwise Class C.
```

and the legend defines the classes:

* **C** — the execution of the instruction during which the indicator
  is actuated is **completed**.
* **H** — ... is **terminated**.
* **S** — ... is **suppressed**, *except during EX, EXIC, T and SWAP*.

**THIS CORRECTS TERMINOLOGY THIS PROJECT HAS COMMITTED.** The DS work
was built from p.32's sentence "storing in core storage is always
suppressed, and the operation is always terminated", and the program
is called `ds_terminates_branch.strap`. p.32 is the storage-protection
chapter using "terminated" loosely. The INSTRUCTION SEQUENCING chapter
is where the three words are defined, and it is unambiguous — printed
**p.45** gives the same answer in prose:

> *"19. Data Store (DS). ... **The operation was suppressed.**"*
> *"20. Data Fetch (DF). ... If the corresponding mask bit was one,
> the fetch did not take place, and **the entire operation was
> suppressed**. If the mask bit was zero, the operation was completed
> normally."*
> *"21. Instruction Fetch (IF). ... If the corresponding mask bit was
> one, the fetch or branch did not take place and **the entire
> operation was suppressed**. If the mask bit was zero, the
> instruction was executed normally."*

and printed **p.51** separates the two words outright: *"the execution
of the instruction in progress is either carried through to completion
or entirely suppressed before beginning action on the alert. When
neither is possible, however, execution of the instruction is
terminated."* **Terminated has only three ways in** (p.52-53): a Class
H machine-malfunction alert, a Class S alert inside `T`/`SWAP`/`EX`/
`EXIC`, or a Class S alert during progressive indexing.

**So the behaviour implemented is right and the name is wrong.**
Mask-zero DF/IF is Class C — "completed" — which is exactly what the
model does. Mask-one is Class S, SUPPRESSED. Nothing outside
`T`/`SWAP`/`EX`/`EXIC` is terminated.

### WHAT SUPPRESSION LEAVES BEHIND — p.52, and it reads as exhaustive

> *"In order to allow continuous computer operation, the suppression
> of an instruction must necessarily exclude the following operations:
> 1. The actuation of those indicators, associated with the
> instruction, of Class S, and indicators DF and IF when their mask
> bits are zero. 2. The actuation of indicators that were caused by
> conditions unrelated to the instruction in execution. 3. **The
> stepping of the instruction counter.** 4. **The changing of the
> state of the interruption system** which occurred as specification
> of BRANCH ENABLED, BRANCH DISABLED, or BRANCH ENABLED AND WAIT."*

Two consequences the model does not yet implement, both stated rather
than inferred: **a suppressed `BD` still disables** (and `BE`/`BEW`
still enable), and the instruction counter still steps.

**AND ONE CONSEQUENCE THAT IS AN INFERENCE, labelled as such.** The
list is framed as everything that survives, so by closure the result
indicators, the progressive-index update and a direct-index store's
index-result indicators are all suppressed. The manual never says so
in those words. **The deck cannot settle it either**: TEST 8B and TEST
8C both re-actuate the indicators with a fresh `LX,$Xn,$Xn` before
testing them, precisely so they do not depend on what a suppressed
operation left behind. So a green 8B/8C is NOT confirmation of this
choice.

### TWO MORE RULES FROM p.51, both unimplemented

* **ACTUATION PRIORITY, which is not the same as interruption
  priority.** *"in the event of such an alert, only the indicator of
  higher priority is actuated. The order ... is the same as the order
  shown on the indicator list except that **IF has priority over
  AD**."* Worked examples: `M+` on a protected operand actuates **DS
  only, DF unchanged**; `SWAP` actuates **both**, because its two
  transmissions are separate alerts; a branch address both invalid and
  protected actuates **AD only** ("an instruction has not been
  fetched").
* **AND THAT PRECEDENCE IS ITSELF MASK-DEPENDENT**: for an `EX`/`EXIC`
  subject address both protected and invalid, *"indicator IF will be
  actuated. Indicator AD will not be actuated ... **unless the IF mask
  bit is zero**."*

## 5b. TWO SEARCHES CLOSED, 2026-09-24 — both negative, both useful

### TEST 8A AND TEST 8D DO NOT EXIST, and the deck says so in a constant

`NEXT.md` and `archival_inventory.md` both carried an open item to find
them, on the strength of routine 1260's own setup comment at PDF p.75:
*"-SETUP BD, I60107 INTERRUPT TABLE / -FOR TESTS 8B, 8C, 8D"*. **TEST
8's lettering runs 8B, 8C and stops.** There is no 8A and no 8D.

The decisive argument is not a page-by-page search — it is the deck's
**expected continuity constant**, read first-hand at 400 dpi on PDF
p.83:

    IC260  XW,0,0,0                  -CONTINUITY REG 1260.   022737.00
    ICK260 XW,(8)777774.00,0,0                               022740.00

Every sub-test of 1260 ends `LX,$X13,IC260 / V+,$X13,BIT<n> /
SX,$X13,IC260`, and at the end the routine does `KV,$X13,ICK260` and
reports *"-CONTINUITY ERROR."* on mismatch. **777774 octal as an 18-bit
field is `111111111111111100` — bits 0-15 set, bits 16-17 clear — so
the deck itself states that routine 1260 has EXACTLY SIXTEEN
sub-tests**, and all sixteen are named:

| bit | sub-test | | bit | sub-test |
|---|---|---|---|---|
| BIT0 | TEST 1A (p.11) | | BIT8 | TEST 7 part 1 (p.65) |
| BIT1 | TEST 1B (p.13) | | BIT9 | TEST 7 part 2 (p.68) |
| BIT2 | TEST 1C (p.21) | | BIT10 | TEST 7 part 3 (p.74) |
| BIT3 | TEST 2 (p.23) | | BIT11 | TEST 8B (p.75) |
| BIT4 | TEST 3 (p.25) | | BIT12 | TEST 8C case 1 (p.77) |
| BIT5 | TEST 4 (p.36) | | BIT13 | TEST 8C case 2 (p.79) |
| BIT6 | TEST 5 (p.60) | | BIT14 | TEST 8C case 3 (p.81) |
| BIT7 | TEST 6 (p.64) | | BIT15 | TEST 8C case 4 (p.83) |

No bit is left over, so there is no room for an 8A or an 8D. **This is
a better kind of closure than an exhaustive read**: a search can only
ever report "I did not find it", but a full enumeration whose slots are
all spoken for reports "it is not there." The same mechanism
independently confirms routine 1258: `ICK258` = `(8)600000.00` = bits 0
and 1 = exactly two tests, which is what the routine has.

**REFINEMENT, 2026-09-25 — the constant counts CONTINUITY-BIT UPDATES,
not "sub-tests", and the two only coincide sometimes.** Routine 1268
makes the distinction visible: `ICK268` also prints `600000` = two bits,
but 1268 has SIX lettered sub-tests (1A/1B/1C, 2A/2B/2C). It performs
exactly TWO `V+,$X13,BITn` updates — BIT0 at 024362.40 and BIT1 at
024401.00, both now transcribed and checked — because 1A/1B/1C are one
test swept across three memories sharing bit 0, and 2A/2B/2C are the
other sharing bit 1. Its banner says so in words: *"-THIS TEST IS
COMPOSED OF TWO ROUTINES"*.

**The TEST 8A/8D conclusion is unaffected**, and it is worth being
precise about why rather than just asserting it: that argument did not
rest on "bits = sub-tests" as a general rule. All sixteen of routine
1260's bits were individually located and matched to a named sub-test,
so the enumeration is closed by the *list*, not by the arithmetic. Had
even one bit been unaccounted for, 1268 shows what the alternative
reading would have been. **State the rule as "one bit per continuity
update" and check what the updates actually are; do not read a bit
count as a test count.**

Corroborating closures, each checked separately: the octal is
**contiguous across the TEST 7 / TEST 8B seam** (022512.40 → 022513.00,
both pages in one 400 dpi crop, no gap for an 8A); routine 1260 **ends
immediately after 8C case 4** with `BD,162` at 022736.40 → 023304.00,
routine 1262's entry; and the p.8 write-up **never letters TEST 8 at
all**, describing it in one unlettered paragraph as *"AN ELEMENTARY
CHECK TO DETERMINE THAT THE CORRECT INDICATORS AD, DS, DF, IF ARE
TURNED ON AND THAT CORRECT TERMINATIONS AND SUPPRESSIONS OCCUR..."*.

The p.88 "8D" sighting is **stale boilerplate**, confirmed at 400 dpi:
it is the same five-line interrupt-table-fill idiom as 1260's `I60123`,
sitting in routine 1262 with the comment carried over unedited, and
1262's own write-up numbers its tests 1/2/3 with suffixes 1A…3B.

**Leave the p.75 comment as it stands. A setup comment naming a test
that does not exist is itself the finding** — and note "8A" is absent
even from that comment. Conjecture, flagged and NOT to be promoted:
TEST 8's four indicators are AD, DS, DF, IF; 8B is DS and 8C is DF+IF;
AD gets no lettered sub-test because TEST 7 already gives it a
dedicated interrupt entry (`I60107`, p.71) and the `I6082`/`I6083`
blocks (pp.41-42) already turn it on.

### THE ACTUATION-PRIORITY RULE HAS NO DECK ORACLE — implement it from the manual or not at all

Reference Manual printed p.51 (PDF 54), verified verbatim: *"In a few
cases, the general description of indicators shows that a single cause
should actuate two indicators. However, in the event of such an alert,
only the indicator of higher priority is actuated. The order of
priorities ... is the same as the order shown on the indicator list
except that **IF has priority over AD**."* Its four worked examples:
(a) ADD TO MEMORY → DS only, DF unchanged; (b) SWAP → **both** DS and
DF, "because each of the two attempted transmissions causes different
alerts"; (c) branch address invalid *and* protected → AD only, IF
unchanged; (d) EX/EXIC subject address protected *and* invalid → IF
actuated, AD not, "unless the IF mask bit is zero".

**Searched and not found:** `jb_ax5b` pp.4-116 in full, plus `jb_ax4b`'s
routine inventory and routine 1246. Nothing anywhere arranges a double
alert. The reason is structural, not accidental, and that is what makes
the negative trustworthy:

* **Every protection test bounds its addresses to the valid range.**
  TEST 7's own header (p.71): *"RANGE OF X IS FROM 000040 THRU 777777
  OCTAL."* Valid but protected → a single cause by construction.
* **Every invalid-address test uses addresses that are invalid but not
  protected** — 1262 TEST 3A and 3B, 1260's `I6082`/`I6083`.
* **1262's `16219`/`16272` "CHK ADR MONITOR"** put an EX/EXIC *subject*
  above UB — example (d) minus the invalid half. They check that the
  interrupt happened and the instruction was NOPed, never "and AD
  stayed off".
* **The signature that would make a witness never appears**: an
  operation followed by TWO indicator branches, one asserting A on and
  one asserting B still off. Supporting detail: across pp.4-44 no
  `BZ<IND>` form for AD/DS/DF/IF/OP/USA/EXE occurs at all — only
  `BOP`, `BAD`, `BUSA`, `BEXE`, `BDS`, `BADZ`, every one branch-on-ON.
* **`jb_ax4b` cannot hold the SWAP witness.** Routine 1246's banner
  (PDF p.99) is *"TEST TRANSMIT AND SWAP"* with nine memory pairings
  and three modifier bits — no protection, bounds or indicator clause —
  and the deck's own loading procedure (printed p.1) says *"Disable
  Interrupt and Time Clock"*.

**So this is a Reference-Manual-only claim.** That does not forbid
implementing it, but it changes what implementing it means: there would
be no deck to check it against, and the project's bar (§ The bar) is
deck-verified behaviour. If it is implemented, the code must say
plainly that its oracle is p.51 and nothing else — the same standing
that DF was wrongly given once already (see § 2's CORRECTION).

**One near-miss, re-verified first-hand rather than taken on trust**,
because it deliberately involves both DS and AD: 1260's `I6086` block
at p.44 turns AD on with its own `SV,$X4,1.32` as part of the DS setup,
then at 021375.40 does `BADZ,$+.32` whose target 021376.00 **is its own
fall-through** — so both paths converge unconditionally and the only
effect is CLEARING AD. Two causes, two indicators, no arbitration. Not
a witness. (The same "branch that goes nowhere, written for its
clearing side effect" idiom appears at 8B's 022517.00.)

### TWO CORROBORATIONS OF COMMITTED MODEL CODE, found while verifying something else

Both read first-hand at 300 dpi, both worth adding to
`bsv/StretchExecute.bsv` next time that file is open (it was owned by
other work when they were found, which is the only reason they are
parked here):

**The interrupt-entry IF exemption has a SECOND, more explicit source.**
`execute()`'s `atIntAddr` gate currently cites printed p.32 class 1,
which states the rule as an exception clause. Printed p.48 states it
outright, in its own sentence: *"The instruction fetch indicator (IF)
cannot be turned on when this instruction is fetched even though it
might lie in the protected area of core storage."* That is a better
citation than the one in the file.

**`ifViolates`'s `a >= 32` gate is sourced twice too.** Printed p.50,
under EXECUTE: *"An effective address of EXECUTE that is below 32.00
(including addresses between 1.00 and 3.32) is not monitored by the
address monitoring mechanism; that is, indicator IF cannot be actuated
by these addresses."*

### THE BIT-18 EXCLUSION HAS FOUR OPERAND CLASSES, NOT TWO

This project states its bit-18 rule in many files as: the top bit of the
printed octal pair is the half-word select, EXCEPT for bit-address
operands (`SIC`, TRANSMIT's A1) where it is a bit offset. That is right
as far as it goes and **it misses a third category with a different
reason**, sourced 2026-09-25:

* **Branch targets** — bit 18 IS the half-word select. Printed p.39:
  *"The address field, bits 0-18, represents the branch address."*
* **`LX` and `SX`** — EXCLUDED, and **not for `SIC`'s reason**. Printed
  p.23: *"In the majority of these operations, 19 bits of the effective
  address are used in order to permit addressing of half-words. **The
  two exceptions use only 18 bits of the effective address because they
  require full-word operands.**"* Confirmed by printed p.24 on `SX`:
  *"stored in the full-word memory location specified by bits 0-17 of
  the effective address."* So their pair carries bit 18 = 0 structurally
  — not because it means something else, but because the field is
  narrower.
* **`V+` and `KV`** — bit 18 IS the half-word select; these are *not*
  the two exceptions. Printed p.24 on `KV`: *"the half-word addressed by
  bits 0-18 of the effective address"*.
* **`SIC` and TRANSMIT's A1** — EXCLUDED because the operand is a 24-bit
  BIT address, so the pair is a bit offset within the word. Printed
  p.41.

**And the `SIC` case is UNDECIDABLE FROM THE DIGITS, which was measured
rather than argued.** An injection that re-reads `enc_sic`'s operand as
a 19-bit half-word address fails ZERO rows in routine 1268, because
every `SIC` offset there is 0 or 32 — and 32 bits is exactly one
half-word, so the two readings produce numerically identical six bits.
The manual settles it; no amount of staring at the print can.

### A free cross-check, and one difference

Reading the indicator names off routine 1260's four 48-entry error
tables gives all 48 in order, matching `bsv/StretchTypes.bsv` exactly.
**One difference: the deck NAMES indicator 14 `RESRVD`, where
`StretchTypes.bsv` leaves 14 unnamed.** Harmless, and worth a comment
there if anyone is in the file.

## 5c. LISTING TYPOGRAPHY — the leading glyph is the LETTER I, and the repo spells it wrong

Full evidence in **`docs/listing_typography.md`**. Settled 2026-09-24 by
measurement, very high confidence; nothing here is a judgement call.

**The primary-source rule**, `C22-6531` printed p.10, verified
first-hand: *"A symbol is any sequence of six or fewer alphabetic and
numeric characters conforming to the following conditions: 1. It
contains only alphameric characters. **2. Its first character is
specifically alphabetic.**"* So `160123`, `1581` and `14412` were never
legal STRAP-1 symbols.

**The measurement.** 11,826 glyphs in `jb_ax5b`'s pure-digit columns and
4,066 in `jb_ax4b`'s give the floor for "digit": narrowest printed digit
24 px, 99% at 30 px or wider. Letter I runs **10-18 px**. The
populations do not overlap, and the shapes differ too — this chain's
digit 1 has an upper-left flag and a full-width base serif, the letter
has neither. 15 mixed rows carry both glyphs; 197 name-field tokens were
sampled across both decks and **not one label begins with a digit**.

**The scheme, confirmed:** letter `I` + the routine's last two digits
for body labels (`I60`, `I74`, `I46`, `I58`, `I44`), and `IC`/`ICK` +
the last three for continuity registers (`IC260`, `ICK258`). The repo
already reads `IC260` with a letter I and `14412` with a digit — the
same convention, spelled two ways.

**Two independent signs the `L` prefix was a workaround, not a reading.**
`strap_asm.py` enforces alphabetic-first (which is *why* `L` was
invented) but does not enforce the six-character limit — and **82 of 195
distinct `L1…` symbols are seven characters**, over that limit. Every
corrected form fits: `L160107`(7) → `I60107`(6). And the repo spells the
same symbol both ways in different files: `L100Z`/`L1000` against
`I00Z`/`I000`.

**NO CHECK ANYWHERE IS WRONG — only spelling**, and that was verified
rather than assumed. `listing_oracle.py`'s row tuples carry the disputed
names in a `note` field that is interpolated into the PASS line and
never parsed. `check_rows(symbols=…)` does assert, but the name is only
a key that must exist, so a consistent rename is identical and a
half-way one fails loudly with `KeyError`. Nearly all the disputed
symbols are `SYN`'d externals whose bits come from a printed octal
address. **Zero `.bsv` files carry an affected spelling.**

**The one place it would have reached emitted bits** is the ident row
(`I58ID %IQSZ…,I258` at 014005.00) — whose operand is the routine
number. That row prints no machine code and is deliberately not
transcribed, so the cut that was forced for an unrelated reason is what
kept the error harmless. Corrected in place, along with the banner
(`----I258---`).

**THE MASS RENAME IS DEFERRED AND IS ITS OWN COMMIT.** 47 files, plus 21
program and 21 verify **filenames**. It is cosmetic, it is large, and it
must be all-or-nothing per symbol. Do it mechanically, run the suite,
and do nothing else in that commit.

**How the two measuring agents diverged is worth keeping**, because
neither was careless. One measured pp.112-114 and found the glyphs
separable; the other measured pp.71-73 and reported they were not. Same
deck, opposite conclusions. The second was checking a real claim — that
a label's lead and the `I` of `INT` on the same row are the same glyph —
and it is true, *because both are letter I*. What they never measured is
the third discriminating glyph on that same row: the comment's own `1`,
at 36 px with flag and serif. The row reads `-CLR INT 1.` **They
measured carefully and stopped one glyph early.** A comparison that
finds two things equal proves nothing until you know what the third
thing looks like.

**Separately settled: letter O and digit 0 ARE distinguishable**, 15-22%
apart, which contradicts `ax5b_1258_test2.strap`'s header ("This
printer's letter O and digit 0 are the same glyph"). p.114's pool row is
an **alias**, `SENO SYN,SEN0` — letter-O name, digit-zero value — not
the meaningless self-`SYN` that file describes. Confidence moderate:
it rests on a ratio rather than a gulf. But a symbol cannot be `SYN`'d
to itself, so the two spellings must differ whatever the widths say.

## 5d. `EXIC`'s THREE RULES, and a latent assembler gap

**BUILT AGAINST THIS, 2026-09-29.** `decks/exic_subject.strap` uses
TEST 2B's own idiom for rule (c) — `LV` / `V+I` / `KV` / `BZXE` —
and covers BOTH step sizes, so the "once / twice" sentence below is
executable in this model now and not only in the deck. See item 4a.

### What routine 1262 TEST 2B actually checks — the oracle `EXIC` was built against

Transcribed 2026-09-25 end to end (`ax5b_162_test2b_head_tail.strap`
for the two ends, `ax5b_162_exic_classes.strap` for the middle).
Entry `I6260`, 023705.00-024000.00, five non-branch classes, **three
rules each**:

* **(a) the `EXIC` must not interrupt** — the class's error label is
  planted in `I62ITE` via `SVA`, so an interruption lands on
  `SIC,SEN`/`B,SERS`.
* **(b) the subject must have executed** — reload the register the
  subject writes, then `SIC,SEN` + `B{Z}XVZ,SERS`.
* **(c) the pseudo-instruction counter must be stepped BY THE
  SUBJECT'S LENGTH** — `KV,$X2,I62PSI` + `SIC,SEN` + `BZXE,SERS`.

**The difference from TEST 1B's two rules is STRUCTURAL, not
additive.** Plain `EX` has no pseudo-IC at all, so (c) cannot exist for
it. 1B sweeps the same five classes with (a) and (b) only. Anyone
implementing `EXIC` after `EX` is adding a counter, not a third check.

**AND THE DECK MAKES THE MANUAL'S "once / twice" EXECUTABLE.** Printed
p.50: *"If the subject instruction is half-length, the
pseudo-instruction counter is stepped once; if full-length, twice."*
The four half-length classes check `V+I,$X2,0.32`; the FULL WD VFL
class, whose subject is the full-word `L(BU),I00O`, checks
`V+I,$X2,1.0` at 023772.40 against *"-PSEUDO IC NOT STEPPED 1.0
CORRECTLY / -WHEN SUBJ INST WAS VFL FULL WD."* Printed codes `0.45 05`
against `1.05 05`. That is the rule as a runnable test, not a
paraphrase.

**Two idioms for rule (c), and DIR IX is the odd one out**: it checks
the pseudo-IC ABSOLUTELY (`LVI,$X1,I62SUB+.32` / `KV,$X1,I62PSI`, no
before-snapshot), while the other four check it RELATIVELY (`LV,$X2`
before, `V+I,$X2,<step>` after, `KV,$X2`). Both are transcribed.

### A LATENT GAP IN `strap_asm.py`, measured inert — RECORDED, NOT FIXED

**The assembler does not enforce printed p.23's 18-bit rule for `LX`
and `SX`.** Verified first-hand: `LX,$X1,LBL+.32` assembles to octal
pair 42, i.e. **bit 18 = 1**, which no 7030 `LX` can mean — p.23 says
*"The two exceptions use only 18 bits of the effective address because
they require full-word operands."*

**It bites nothing today, and that is a measurement rather than a
hope:** a sweep of every `ROWS` tuple in every `verify_*.py` parses
**453 `LX`/`SX` rows and finds ZERO with bit 18 set.** Every operand in
the corpus is word-aligned.

**Deliberately NOT fixed, and the reason is rule 4.** The manual states
what the HARDWARE ignores; it does not state what STRAP-1's assembler
emitted when handed a half-word offset on an `LX`. Truncating, erroring
and emitting-as-written are all defensible, no listing row exercises
the case, and picking one would be inventing a fact about the
assembler. If a deck row ever turns up with a non-word-aligned `LX`
operand, that row decides it.

## 5e. `USA`, and why the obvious implementation would fail the deck

Full working in **`docs/execution_operations.md`**, 2026-09-29.

**THE NUMBER EXISTS.** *IBM 7030 Performance Characteristics Vol. 1*,
printed p.3-2, verified first-hand: *"The times are listed (table 2) in
terms of the basic machine cycles, which is presently **0.3
microsecond**."* So **1 ms = 3333⅓ model clocks**, and the figure
`StretchTiming.bsv` and `microarchitecture_plan.md` already assert now
has a page behind it, which AGENTS.md requires.

**AND THE OBVIOUS IMPLEMENTATION WOULD FAIL THE DECK — this is the
finding, not the number.** The model chains one `EX` level per clock
and charges the whole `EX` once at dispatch. A literal "fire `USA` at
3333 clocks" timer therefore reaches **2049 clocks on the deck's
2049-level chain — under threshold. `USA` never fires and TEST 1D
fails.** *The number alone is insufficient: it has to be SPENT at the
documented rate.* Two shapes work and they agree — charge Table 6's
per-level recipe in `resume()` (~20 clocks/level) against 3333, or
count levels against `1000 µs ÷ per-level µs`.

**Bounded negative:** there is **no single documented per-`EX`-level
charge.** Table 6 (printed p.3-12) gives `EX` as six additive terms,
two of which are "always begins/ends with Look-ahead drain" — not
scalars. Only a bound survives: **~110–160 `EX` levels per ms.** Do not
quote p.45's *"several hundred indirect addressing cycles"* for `EX` —
Table 4 shows that parenthetical is about **`LVE`** (4.8/3.6/3.0 µs per
level → 208/278/333 per ms, which is exactly "several hundred").

**A RULE-4 GAP FOUND EN ROUTE, and it is the same change.**
`StretchTiming.bsv`'s misc arm reads
`case (x.code) 3'b100: 3; 3'b001: 8; default: 14; endcase  // Z / RCZ / R`.
**`EX` is misc `3'b010`, so it falls into `default: 14` — a value
sourced for `R`.** Verified first-hand. `EX`'s timing currently
inherits another instruction's number with no source of its own.

### The disabled-state exceptions — sized, and cheaper than feared

* **Exception 1 ("address monitoring is always in force during EX and
  EXIC") is ONE TERM IN ONE FUNCTION, not thirty edits.**
  `protViolates` ends `st.irqEnabled() && installed(a) && signalled`;
  making it `(st.irqEnabled() || st.execOpInProgress())` changes all
  ~30 call sites with zero textual churn — and that is the right
  granularity, because "always in force" covers DS, DF **and** IF,
  exactly the set `protViolates` gates. **~20-30 lines.**
* **Exception 2 ("interruption is always permitted at the completion,
  termination or suppression of an execution operation") is the
  expensive half, ~40-60 lines**, because `intDueCalc` returns Invalid
  whenever `!irqEn`. Needs a second *ungated* latched output, a
  one-shot `execBoundary` **register** (not a wire — `intDueCalc` is a
  clock behind), and a term in `armInterrupt`. p.50's Programming Note
  bounds it to one interruption per boundary, which clearing in
  `rl_interrupt` gives free. **The E-box interface does NOT need
  reshaping.**
* It rides the 2026-09-25 interruption-timing edge rather than needing
  a new one — and note that fix's untested `ebusy <= eb;` line would
  gain a second caller and still be untested.

### And it is DECK-VERIFIED work, not manual-only — five blocks, none transcribed

| block | PDF | octal | entry | tests |
|---|---|---|---|---|
| TEST 1CA | 92 | 023442.40-023450.00 | `I6218` | exception 2 only |
| TEST 1CB | 92 | 023450.40-023460.00 | `I6219` | exception 1, delivered by exception 2 |
| TEST 1D | 95 | 023551.40-023576.00 | `I6241` | **`USA` on 2049 AND exception 2** |
| TEST 2CA | 103 | 024000.40-024007.40 | `I6271` | exception 2 for `EXIC` |
| TEST 2CB | 103 | 024010.00-024020.00 | `I6272` | exception 1 for `EXIC`, incl. the pseudo-IC carve-out |

*"-2049 SUCCESSIVE EXECUTES FAIL TO SET / -USA AND FAIL TO CAUSE
INTERRUPT."* — TEST 1D's own words.

**TEST 1D REQUIRES THE TIMEOUT AND EXCEPTION 2 JOINTLY**: `Z,$MASK`
clears the settable mask, `USA` (17) is permanently masked, the system
is disabled, and the only pass path is an interruption. Neither piece
can be validated by 1D alone, so they are one change.

**TEST 1CA is the cheapest to transcribe and run** — 11 rows, one
inline data word, one message, needs nothing from `EXIC` — and should
be written BEFORE the implementation, the way `ax5b_16071_ts.strap`
was. Its mechanism is worth knowing: the `-ILLEGAL OP CODE.` word at
023445.40 is in the STRAIGHT-LINE stream, not the `EX`'s subject; it
actuates OP while disabled, nothing interrupts, the vector is planted,
and then `EX,$-.32` executes a **harmless** subject — so the
interruption must occur *at the EX's completion* although disabled.
2CA is built identically, which is what shows the harmless subject is
design rather than an off-by-one.

## 5f. A MEASURED OFF-BY-ONE IN THE MEMORY MODEL — the cycle is 2.4 µs, not 2.1

Found 2026-10-16 while sizing the SDRAM back end, and verified
first-hand in `bsv/StretchMemory.bsv`'s `mkMemoryUnit`:

```
      busy    <= fromInteger(memCycleClocks);   // = 7, on the REQUEST clock
    end else begin
      if (busy != 0) busy <= busy - 1;          // only when NO new request
```

`memCycleClocks = 7` is commented *"2.1 us at 0.3 us per clock"*, and
7 × 0.3 = 2.1 is right. **But the decrement sits in the `else` arm**,
so it never runs on the request clock itself. Trace it: the request at
clock 0 sets `busy` to 7; clocks 1-7 decrement it to 0; `free()` first
reads true at **clock 8**. The unit's period is **8 clocks = 2.4 µs**,
a 14% overstatement of the real machine's core cycle.

**It is a discrepancy against the file's own header**, not against a
reading of the manual, so nothing needs re-sourcing. Buchholz §14.1 and
Perf. Char. agree on 2.1 µs and `memCycleClocks = 7` encodes that
correctly; only the decrement placement is wrong.

**NOT FIXED HERE, deliberately.** Changing it shifts every `CYCLES<=`
bound in the suite and would land in the middle of other work. It also
wants deciding alongside `memReadClocks`, where the same analysis found
the read deadline is **1,200 ns rather than 1,500** (`dataOut <= Valid
raw` at `readDue == 1` presents what was written by the end of the
previous clock). Do both at once, re-measure the six benchmarks, and
say in the commit what moved.

**It matters more than 14% suggests**, because the user's goal is cycle
accuracy: a systematic +1 on every memory access is exactly the kind of
error the Performance Characteristics comparison (§ docs/timing_oracle.md,
in progress) exists to catch — and a reminder that the timing model's
*constants* being sourced does not make its *mechanics* right.

## 5g. THE TIMING ORACLE HAS BEEN RUN, AND THE VERDICT IS *REBUILD* — `docs/timing_oracle.md`

Finished 2026-10-16. The question §5f left open — whether cycle
accuracy is a correction or a rewrite — now has an answer sourced to
Performance Characteristics Vol. 2's measured per-instruction times.
**The per-instruction scalar is the wrong shape.** Five independent
legs, the second being the one that settles it:

1. **The measured spread exceeds what the model charges.** Transmit
   runs 14.47-312.88 µs (21.6×) against a flat 4.20. `LVS`
   6.48-31.78 against 3.00. `BAL` 7.20-19.78 against 3.60.
2. **`CBR`'s error changes sign inside one instruction**: 7.20 model
   vs 11.14 measured taken, 6.60 vs 4.52 untaken. A constant can be
   wrong; **a constant whose error inverts within one instruction is
   the wrong shape.**
3. **IBM's own page titles are the schema.** Vol. 2 indexes time by
   opcode, operand location, indexing, forwarding, word-boundary
   crossing, field spec, data case, alignment, and surrounding
   stream — nine variables. `iboxCycles(DecodedInstr, Bool taken)`
   sees three.
4. **Vol. 1 §3's tables carry unevaluated symbolic terms** — `LAAR`,
   `LAdr`, `LAMT` — and the model drops every one, keeping only the
   scalar part. Printed p.3-10's Table 4 is explicit: `SV,SC,SR` is
   "4.2 µsec + dec + LAAR" where `LV,LC,LR` is "4.2 µsec + dec".
   Same scalar, different term. The model gives both `default: 8`.
5. **`EX`/`EXIC` get a constant where IBM gives a six-term recipe**,
   and `StretchTiming.bsv:49` sends both into `default: 14`, a value
   sourced for `R`.

Of 33 tabled deltas, **29 have the model too fast.**

### THE SIX `CYCLES<=` BOUNDS DO NOT CONSTRAIN THIS, and that is the finding to act on

They are one-sided upper bounds, and they were self-calibrated against
the model's own stage-2b output. **A model that got arbitrarily faster
would pass all six.** Any future timing work needs two-sided bounds
taken from Vol. 2, not from the model.

### ONE BOUNDED CORRECTION IS DONE — and the survey found one wrong variable where the page shows TWO

**APPLIED 2026-10-16 in `bsv/StretchTiming.bsv`'s `eboxClocks`.** It
computed the SAU byte count as `ceil(effLength(length) /
effByteSize(bs))`. That is Table 3's `x/y` — the right shape — **with
both variables read wrong.**

Verified first-hand at Vol. 1 **printed p.3-10 (PDF p.28**; the survey
cites 3-8, which is the Table 3 continuation, not the variable list):

> `x`   Field length in unsigned operations - field length minus the
>       byte size in signed operations
> `y`   8 in binary operations and byte size in decimal operations

So `y` is the SAU's *effective* byte width — **8 in binary mode
whatever the instruction declares** — and `x` **drops the sign byte in
signed operations**, which the survey missed. Both facts are already
decoded: `VflMod { unsign, invert, decimal }` sits in the payload
(`StretchTypes.bsv:412-416`), so this needed no new decode.

**THE MEASURED COLUMN WAS RE-READ FIRST-HAND, and the survey's numbers
all stand.** Vol. 2 **printed p.110 = PDF p.117**, header *"VFL
INSTRUCTION M+ / NO FORWARDING / DIRECT ADDRESSING / OFFSET 0 /
INSTRUCTION AT FULL WORD ADDRESS"*, column **NO INDEXING / EXTERNL
OPERAND**. The page carries **24 rows, not the 9 the survey tabled**.
One scare resolved the survey's way: `(D,64,4)` is **15.01**, and the
15.00 in the adjacent cell is the *indexed* column — the OCR runs the
label and the first number together (`10,64,4115.01`), so this is a
row where text extraction cannot be trusted and the render settles it.

| field spec | model before | corrected | measured | before | after |
|---|---|---|---|---|---|
| `(BU,1,8)` | 6.60 | 6.60 | 6.63 | −0.03 | −0.03 |
| `(BU,8,8)` | 6.60 | 6.60 | 6.63 | −0.03 | −0.03 |
| `(BU,16,8)` | 7.20 | 7.20 | 6.93 | +0.27 | +0.27 |
| `(BU,32,8)` | 8.40 | 8.40 | 7.84 | +0.56 | +0.56 |
| `(BU,48,8)` | 9.60 | 9.60 | 9.02 | +0.58 | +0.58 |
| `(BU,64,8)` | 10.80 | 10.80 | 9.61 | +1.19 | +1.19 |
| `(B,1,1)` | 6.60 | 6.60 | 6.63 | −0.03 | −0.03 |
| `(B,8,1)` | 10.80 | **6.60** | 6.93 | +3.87 | **−0.33** |
| `(B,16,1)` | 15.60 | **7.20** | 7.23 | +8.37 | **−0.03** |
| `(B,32,1)` | 25.20 | **8.40** | 8.42 | +16.78 | **−0.02** |
| `(B,48,1)` | 34.80 | **9.60** | 9.61 | +25.19 | **−0.01** |
| `(B,64,1)` | 44.40 | **10.80** | 10.80 | +33.60 | **0.00** |
| `(DU,4,4)` | 6.60 | 6.60 | 6.63 | −0.03 | −0.03 |
| `(DU,8,4)` | 7.20 | 7.20 | 6.93 | +0.27 | +0.27 |
| `(DU,16,4)` | 8.40 | 8.40 | 7.84 | +0.56 | +0.56 |
| `(DU,32,4)` | 10.80 | 10.80 | 10.21 | +0.59 | +0.59 |
| `(DU,48,4)` | 13.20 | 13.20 | 12.60 | +0.60 | +0.60 |
| `(DU,64,4)` | 15.60 | 15.60 | 14.40 | +1.20 | +1.20 |
| `(D,4,4)` | 6.60 | 6.60 | 6.63 | −0.03 | −0.03 |
| `(D,8,4)` | 7.20 | **6.60** | 6.93 | +0.27 | **−0.33** |
| `(D,16,4)` | 8.40 | **7.80** | 7.84 | +0.56 | **−0.04** |
| `(D,32,4)` | 10.80 | **10.20** | 10.21 | +0.59 | **−0.01** |
| `(D,48,4)` | 13.20 | **12.60** | 12.60 | +0.60 | **0.00** |
| `(D,64,4)` | 15.60 | **15.00** | 15.01 | +0.59 | **−0.01** |

**Mean |error| 4.02 → 0.28 µs; worst case 33.60 → 1.20.** Ten rows
change, **every one of the ten improves**, and the other fourteen come
out byte-identical. A fix that moves only what was broken, and moves
all of it the right way, is the shape a correct fix has — and the ten
that moved are exactly the signed rows and the decimal rows, which is
what p.3-10 predicts and not something a fitted constant would give.

Two details the arithmetic forced, both recorded rather than tuned:

- **A signed field narrower than its own byte size** would underflow
  `x`. The code falls back to the full length when `len <= bs`, which
  is also what `(B,1,1)`'s measured 6.63 wants.
- The residual is no longer a bias but a **band, −0.33 to +1.20**,
  and the +0.6-to-+1.2 end is all long unsigned fields. That is the
  next VFL question, and it is small enough to wait for the rebuild.

**THE SUITE CANNOT SEE THIS FIX, and that had to be checked rather
than hoped.** Every one of the **1,106** VFL and connective field
specs in `decks/` is `(BU,n,8)` — 1,042 of them `(BU,64,8)` —
unsigned and byte size 8, where both corrections are the identity. So
the budget that gates dispatch does not move for any deck, no
`CYCLES<=` bound shifts, and **a passing suite is not evidence for
this change.** The evidence is the Vol. 2 table above. The same
caveat governs §5f's memory off-by-one: both pending timing fixes make
the model faster, all six bounds are one-sided, and a green run would
say nothing about either.

**THE CONNECTIVE ARM WAS LEFT ALONE, on purpose.** `eboxClocks`'s
`Connective` case has the identical `ceil(effLength/effByteSize)`, but
`ConnInstr` carries **no `VflMod`** — no sign bit, no radix bit — so
p.3-10's `x` and `y` have no referent, and p.3-10 belongs to Table 3,
*"EQUATIONS FOR SAU INSTRUCTIONS"*, whose list (ST, L, M+, K, KI, KF,
KR, KRI, KE, LTRS, LCV …) does not include the connectives. **Vol. 2
has no connective page**: all 66 of its instruction headers are VFL
arithmetic. Fixing it by analogy would be exactly the inference rule 4
forbids, so the declared byte size stays and the gap is recorded here.

**A THIRD IGNORED VARIABLE, found on the same page.** Every VFL page
carries a second data case headed **"INVERT SIGN OF INSTRUCTION"** —
27 occurrences across Vol. 2 — and it is not small: `(BU,48,8)` runs
**13.20 against 9.02**, +4.18 µs for the same field spec. That is
`VflMod.invert`, the one bit of the three the model decodes and no
part of timing consults. Table 3's comment column is the source
(*"Unlike signs AB > CD, add .6(x/y + 1)"* for `M+`), but the measured
deltas do not match that expression as read — +0.60 where it predicts
+1.20 on `(BU,8,8)` — so this is **recorded as an open question, not
a formula.** It belongs to the rebuild.

Two more corrections in the same bucket, deliberately **not** folded
into this commit so the attribution stays clean, and not yet
arithmetic-checked: `DirIndex default: 8` lumps `SV/SC/SR` (measured
7.81) with `LV/LC/LR` (5.42) and `V+/KV` (5.27), where Vol. 1 printed
p.3-10's Table 4 gives `SV,SC,SR` as *"4.2 µsec + dec + LAAR"* against
`LV,LC,LR` at *"4.2 µsec + dec"* — same scalar, one extra term; and
`V+CR`/`V±ICR` charge refill unconditionally.

### WHAT THE REAL END-TO-END ORACLE IS

Vol. 1 §4's measured whole-program times cross-referenced to Vol. 2's
STRAP listings — **GERB2 matrix inversion, 20×20, 0.14 s** (source at
Vol. 2 printed pp.3-7) is the highest-value target, with MXM16, PRIMC
and the Monte Carlo behind it. Vol. 1 Table 10 is *not* it: that is
the Execution Frequency Chart for weather programs whose source is not
in Vol. 2.

**Rule 3 cannot be applied to these listings.** They are OCR'd STRAP
source with **no machine-code column**, so there is nothing to
transcribe and check with `listing_oracle.py`. This is the weakest
verification posture of any oracle this project uses, and the fact
needs saying in whatever commit leans on it.

### SEQUENCING — THIS IS PHASE 2, AND IT IS THE SAME WORK AS THE REWRITE

The user's order is **MCP first, then cycle accuracy**, so nothing
here redirects the Exchange/disk/interval-timer work. What matters is
that this survey reached `docs/resuscitation_roadmap.md`'s conclusion
independently and from different evidence: **the idiomatic-Bluespec
multi-cycle-box rewrite and cycle accuracy are one job, not two.**
Legs 3 and 4 are both statements that the timing function needs
machine state the scalar table cannot see — LAAR busy, forwarding
hits, LA level occupancy — which is exactly what the box rewrite
builds. Vol. 2 should become **the acceptance test for that rebuild**,
not a table copied into `StretchTiming.bsv`.

The gating unknown, recorded and not guessed: whether the CE manuals
give `LAAR`/`LAdr`/`LAMT` as functions of machine state, or only as
names. If they do not, cycle accuracy is bounded by what Vol. 2
measures and no better.

## 5h. MCP BOOTS FROM TAPE, NOT DISK — the MCP critical path is reordered

Established 2026-10-16 by the disk study (`docs/disk_subsystem.md`,
1,449 lines) and **verified first-hand before being acted on**, because
it contradicts what this session had been saying out loud.

`C22-6678-1` **printed p.29 = PDF p.29** (footer *"Operating With MCP
29"*), under INITIALIZING THE SYSTEM:

> "Basically, the initialization program reads the MCP portion of the
> master system tape into core storage and **writes a copy of the
> entire tape on the disk in the PROSA area**."

The figure on the same page draws it: *Master System Tape* →
*Initialization Program* → *MCP in Core Storage*, with a second arrow
**into** *Entire System on Disk Storage*. The procedure agrees —
*"3. Press IPL key. 4. Press Signal key on the adapter unit for the
channel on which the **master system tape** is mounted"* — and so does
Input: *"The current MCP master system tape is file protected and
mounted on any tape unit dialed to zero."*

**So the disk is a write target at IPL, not the boot source.** Both
halves of the earlier claim were wrong in different ways: MCP *does*
require a disk (p.6's minimum config, and the disk is absent from the
same page's list of what the system can survive without), but it never
boots from one. p.32's "Disk IPL" is a **card deck** that reloads from
PROSA *after* a tape IPL has already succeeded, and its failure path
says twice that "the system must be reinitialized by a tape IPL".

**WHAT THIS CHANGES.** The MCP gate is the **tape IPL path** —
Exchange + a 729-class tape unit + the channel-signal IPL mechanism
(RefMan p.126) + the interrupt system — and the disk is the cheap part:
~100–170 code lines for the boot-sufficient subset against the
Exchange's 1,150–1,950 (`docs/exchange_and_io.md` §6.2). Sequencing
work by "the disk is the hard gate" would have put two orders of
magnitude of effort in the wrong place.

The hardware IPL mechanism is also **structurally incapable** of
targeting a disk, by three independent routes: it needs a channel
signal from a unit *"accommodated by the exchange"*; it stores a fixed
control word *"in the control word location for the channel"*, which
p.161 says the disk does not have; and that word's chain flag and
refill are fields p.158 says the disk discards.

### THE EXCHANGE HAS AN ENCODING ORACLE BUT NOT A RUNNABLE ONE

`docs/bx0_exchange_decks.md` (977 lines) settles the BX-0 question
three ways rather than one. **Not** a runnable deck oracle: printed
p.2 says BX-0 is *"exclusively a manually operated test, since it is
independent of the CPU"* — there is no instruction stream to execute.
**But yes** a bit-exact encoding oracle for the control word, with the
three machine-code groups decoded and checked mechanically rather than
by eye (flag byte octal-additive, multiple `20` / chain `40`, 4
samples; count group = **count × 16 + 2·chain**, 14/14; refill = low
byte of target address, hex, 9/9), plus the primary-source STRAP
control-word mnemonic table from printed p.14. That feeds `strap/`
with no model needed.

**THE MOST ACTIONABLE THING IN EITHER REPORT** is a list of documents
this project does not have and should go looking for, now named:
`docs/7030_SystemTestPrograms_Aug61.pdf` — in the repo, never mined —
carries the acceptance-test PROGRAM LIST, and the CPU-side Exchange
diagnostics on it are **`JA EE3`** (BX/TAPE), **`JA NE4`**
(Printer/BX), **`JA ES1D`** (I/O single channel), **`JA CE1`/`CE2`**
(tape) and **`JA NE5`/`NE6`** (reader/punch). None is in `docs/`.
Those are the `jb_ax5b`-class decks for the CPU↔Exchange instruction
interface — the oracle the tape IPL path actually needs. For the disk,
Perf. Char. Vol. 1 pp.5-5 and 5-8 name three more: *"High-Speed
Exchange"*, *"Disk"*, and the **SEVA Disk Routine** (*"will exercise
all possible disk operations"*). Acquiring any of these outranks more
analysis of what is already here.

### THREE SMALLER THINGS WORTH NOT LOSING

- **Exchange channels start at 32, and now that is sourced.**
  `C22-6678-1` p.32's dump-device table names *"CH 32, UN0 / CH 33 /
  CH 34"* on a real MCP machine. `bsv/StretchIO.bsv` already picks
  32/33/34 and the choice had rested on nothing.
- **The disk's 18 MiB is a structural dependency, not a line count.**
  2,097,152 words × 72 bits ≈ 18 MiB per unit — 21× the entire core
  store, which this project models as registers. It is not a Bluespec
  `Vector` and not on-chip BRAM on any ULX3S part, so it needs a
  file-backed/BDPI or sparse hash-of-arcs representation. `StretchIO.bsv`
  met the small version of this and solved it by pre-loading fixed
  `Vector`s *because* bsc's `$fopen`/`$fgetc` are Actions; that does not
  scale here. This is the piece that touches `docs/fpga_feasibility.md`.
- **The MCP source listing is still unread**, so the boot-sufficient
  disk subset above is manual-derived, not observed.
  `MCP_Mar63_001-249.pdf` + `MCP_Mar63_250-445.pdf` (451 pages, no text
  layer) are in `docs/` and are the authority on what MCP's driver
  actually issues. Grepping those renders for `$CCW`/`$LOC` against the
  disk IOD would turn inference into finding.

Two conflicts are recorded unresolved rather than averaged: the disk's
full-stroke seek is **265 ms** at printed p.157 and **180 ms** in
p.158's table, and p.158 prints "Words per file 2,097,512" where every
other figure gives 2,097,152 (transposed digits).

## 5i. THE TAPE PATH — and the MCP listing turns out to be rule-3 checkable

Three studies, 2026-10-16: `docs/tape_unit_contract.md` (825 lines),
`docs/tape_data_path.md` (1,049), `docs/mcp_tape_manufacture.md` (736).

### THE GATING FACT, verified first-hand

**MCP's listing carries a printed BINARY OUTPUT column**, so
`AGENTS.md` rule 3 applies to it unmodified. Rendered and read
directly at `MCP_Mar63_001-249.pdf` PDF p.10 (its own header says
`PAGE NUMBER 3`): the column header is
`LINE  LOCATION  BINARY OUTPUT  NAME  STATEMENT  LOCATION` and the
rows print `000053.40 80 / 023000.22 80` — character-for-character
what `listing_oracle.fmt_half()` already emits. Coverage is ~80%
listing-wide, ~90-100% on pure code, absent on control-card pages.

This was the one fact separating "tedious but tractable" from "not
worth attempting", and it came out the right way. **Note the PDF→
printed offset is NOT constant** — vol 1 duplicates pp.1-2 and has
three blanks, vol 2 runs +249 at PDF 60 and +250 at PDF 160 — so every
citation must be checked against the page's own printed PAGE NUMBER.

### TWO PROJECTS, TWO ORDERS OF MAGNITUDE APART

| | size | at this repo's demonstrated rate |
|---|---|---|
| **MCP's IPL bootstrap**, printed pp.2-14 | ~550 lines, ~350 rule-3 rows, 369 words of object code | **~4 days** |
| **All of MCP**, pp.1-445 | ~23,700 lines, ~19,000 rows | **~198 days ≈ 6.5 months** |

Rate basis: 5,100 rule-3 rows and 15,984 `.strap` lines over 53 days
(2026-08-24 → 2026-10-16) = 96 rows/day, from git history. The 198-day
figure assumes linearity and **that is flagged as unlikely**: the
corpus is 242 *independent* programs, while MCP is one 97-section
program with `TAIL`-scoped symbols crossing sections, so partial
transcriptions will not assemble standalone.

**So the bootstrap is the target**, and it is ~1.3× the largest
program already in the corpus. The same page proves it: PDF p.10 is
literally `*** FIND IPL CHANNEL NUMBER ***`, `*** IO TEST ***` and
`-SPACE OVER TAPE MARK`.

### RESOLVED: THE BOOTSTRAP *LOADS* FROM TAPE ALONE, AND *RUNS* INTO THE DISK

Settled 2026-10-16 by reading MCP printed pp.12, 13 and 14 directly,
which is what §5i previously called "the highest-value read
remaining". The answer splits the milestone in two and **does not
invalidate the critical path below.**

**Printed p.14 is titled `PROSA CWS` and it is a DATA TABLE, not a
read the bootstrap performs to load itself.** 42 chained
`CW(CDSC),n +X BUFER,513,$+1.0` entries labelled `X PROSA`, and the
page's last line is the one that settles it:

```
43*  000621.00+  +00000000  NULL  X BS END  SYN,$  - END OF THE MCP IPL BS ROUTINE
```

`X BS END` is the symbol p.2's IPL control word measures its own count
against — `CW(CR),X IPL BS,X BS END-X IPL BS,1`, which is the printed
`0o560` = 368. So **the PROSA control words are carried inside the
368-word bootstrap image**, loaded from tape along with everything
else. p.13 confirms the shape, being "BOOTSTRAP DEFINITIONS" and "IPL
BOOTSTRAP PARAMETERS": `X IPL K SYN, 1.0 + X BS END - X IPLBS  - SIZE
OF BOOTSTRAP`, and `X BUFER SYN, X IN END+ 2000.0` placing the PROSA
target at octal 011406 = word 4,870, far outside the bootstrap itself.

**But the bootstrap does use them.** p.12's message block includes
`PROSA ARC COUNT INCORRECT` alongside `IO CONFIGURATION DEFINED
INCORRECTLY` and `IO TABLES CAN NOT BE FORMED` — the bootstrap
validates PROSA arc counts, so it reaches the disk while running.

**THE MILESTONES, AND THE SPLIT IS THE USEFUL PART:**

| | needs | disk? |
|---|---|---|
| **A. The machine IPLs from tape and begins executing MCP's bootstrap** | items 1-5 below | **no** |
| **B. The bootstrap runs to completion** | A + the disk model (~100-170 lines, §5h) | yes |

Milestone A is a real, demonstrable result — a 7030 recreation
executing IBM's own system software from a tape image — and it is
reachable without touching the disk. The disk joins at B, earlier
than "after MCP boots" but still the cheap part. **Nothing in the
ordering below changes.**

Pages 3-10 are the bootstrap's code and have not been read line by
line here; pp.11-14 are messages, definitions and the CW table. The
claim above rests on p.2, p.12, p.13, p.14 and RefMan p.126.

### `ka_ul1` IS THE FIND, and it settles layer 0

"LOAD AND TAPE WRITE UTILITY, KA UL1, 13 Oct 1961" — a card loader
that, with console switch 37 set, **writes an IPL tape**, listing and
printed machine code included. Four things no manual states:

- **The whole IPL tape is written by ONE `W` against one control
  word — no tape mark, no label.** A bootable 7030 tape has no
  mandatory preamble. This is what makes manufacturing one tractable.
- It issues **`LOCATE` unconditionally, even for drive 0**.
- **`UNLOAD` assembles to right effective address `000137`** — octal
  137 verbatim. Independent confirmation against IBM's own assembler
  that `strap_asm.py` is right not to apply the `>>6` word-address
  conversion to `CTL`'s second field.
- Every operation is the **SEOP** form, completion polled by `CCW` +
  `BB` on **control-word bit 24**.

`C28-6379-0_MCP_Loader.pdf` is **not** the boot path — it is the job
loader plus the FORTRAN BSS processor, and `archival_inventory.md` §4
already recorded it read in full. My brief asserted otherwise; the
brief was wrong.

### TWO CORRECTNESS BLOCKERS, both ABOVE the data source

Neither is fixed by `StretchTapeSource.bsv`, and both are nearer the
critical path than the media question:

1. **The FSM ignores `chain`.** The IPL control word chains, and
   Figure 36's `multiple 0 / chain 1 / count zero / not end of block`
   row is literally "Chain and continue". With chain ignored, **IPL
   reads one word and stops.**
2. **Nothing ever writes control-word bit 24, the SEOP status bit** —
   and both `ka_ul1`'s driver and MCP's own bootstrap poll it
   (`BB,X IPL BS+.24 ... -IO OPERATION COMPLETED`, visible on PDF
   p.10). **The real driver idiom would hang on this model.**

**A CONFLICT IN THE IPL CONTROL WORD, recorded rather than averaged,
and MCP's half of it is now verified first-hand.** Rendered at
`MCP_Mar63_001-249.pdf` PDF p.9, its own header `PAGE NUMBER 2`, under
`MCP INITIALIZATION BOOTSTRAP`, line 17 prints the control word's
binary output in full:

```
15*  000040.00                                    SLC,(8)40.0
17*  000040.00  000041.00+ 000 000560 000001      CW(CR),X IPL BS,X BS END-X IPL BS,1
                                                 -IPL CW FOR READING IN IPL BOOTSTRAP
                                                 -RECORD FROM SOURCE TAPE
                                                 -ONE IN REFILL FIELD IDENTIFIES IPLCW
24*  000041.00  000043.44 00     X IPL BS  BD,X BEGIN   -DISABLE AND START IPL
25*  000041.40  000000.00+       VF,0                   -SLOT FOR TAPE CW
26*  000042.00  000000.00+ ...   XW,0                   -SLOT FOR DISK CW
```

So data address `000041.00`, **count `0o560` = 368**, **refill = 1** —
not the `count=1, refill=4` the Exchange-side study read off RefMan
p.126.

**RESOLVED 2026-10-16, and both studies were right about different
words.** RefMan printed p.126 (PDF 129, footer "126 IBM 7030") read
first-hand. The fixed control word the *hardware* plants is:

> Data word address = 4 · Chain flag = 1 · Multiple flag = 0 ·
> Skip flag = 0 · **Count = 1** · **Refill address = 4**

and step 3 says what that buys:

> "The first word read from the unit is stored in the special core
> storage location referred to by means of address 4. Since the fixed
> control word is then exhausted, its refill address causes the next
> control word to be fetched from location 4. **Location 4 at this
> time should contain another control word** specifying the address at
> which the word immediately following should be stored, and the
> number of words to be read from the unit. Reading then proceeds
> normally."

**So it is a two-stage bootstrap and the two words are both real.**
The hardware's word reads exactly ONE word off the tape; that word is
MCP's own `CW(CR)` with count `0o560` = 368 and refill 1; chaining is
the mechanism that hands over from the first to the second. Nothing
needs retiring, and **chaining is not optional for IPL** — it is the
whole hinge, which is why §5i lists it as blocker 1.

Three more things the page settles, all verified on it:

- **"The first instruction of a program loaded by means of the initial
  program loading technique must be BRANCH DISABLED."** MCP's line 24
  is `X IPL BS  BD,X BEGIN  -DISABLE AND START IPL`. Primary source
  and primary artefact agreeing on a detail neither needed from the
  other.
- **"A program can be loaded by the initial loading technique only
  from a unit having the selection address 0"** — which is what
  `C22-6678-1` p.29's "dialed to zero" means, and it is why the
  one-unit-per-channel simplification survives IPL.
- **EOP and EE are NOT turned on at the completion of IPL**, and the
  first channel signal does not set the CS status bit. A model that
  raises them would break the bootstrap.

And on the signal key, the apparent contradiction with RefMan p.136's
"There is no signal key on the tape units" also dissolves here:
p.126 says loading "is started by a channel upon the depression of the
SIGNAL or START key on **any unit accommodated by that channel
address**" — the key belongs to the channel's units collectively, and
on a 729 the equivalent is the not-ready→ready transition `ja_uc1a`
tells the operator to perform.

Note also lines 25-26: the bootstrap reserves a **"SLOT FOR TAPE CW"
and a "SLOT FOR DISK CW"** adjacently, which is the same tape/disk
ambiguity as the p.14 PROSA reads above, showing up in the first
twenty-six lines of the program.

Also from the manual, and it corrects `C22-6678-1` p.29's wording:
RefMan printed p.136 says flatly **"There is no signal key on the tape
units"** — a channel signal from a 729 comes from not-ready→ready or
REWIND completion, which is exactly what `ja_uc1a`'s loading procedure
tells the operator to do ("Make Tape Unit Not Ready then Ready").

### THE MEDIA QUESTION IS THE EASY HALF, and it is measured

microSD, 1-bit SD bus, raw LBA. Synthesised on this machine with
yosys 0.51 `synth_ecp5`: the whole SD tape path is **788 LUT4, 720 FF,
112 CCU2C, 2 DP16KD**, and deleting `tapeImg`'s sixteen 64-bit
registers gives most of it back — net **≈ −237 LUT4, −304 FF,
+112 CCU2C**, or +0.27% of the ~41,070 CCU2C that actually decides the
part. The baseline reproduced `fpga_feasibility.md` §2.4 exactly,
which is what makes the delta comparable.

- **`bsc`'s file primitives are NOT a blocker**, and the answer was in
  the user's own tree: `~/src/alto-bluespec/src/Disk.bsv:18-23` reads
  a Diablo 31 pack through *value*-typed `import "BDPI"`. The tape
  analogue was written, built and **run** — six streaming words out of
  a real host file. `StretchIO.bsv`'s header claim that `$fopen`/
  `$fgetc` being Actions forced pre-loaded `Vector`s should be amended.
- **The split into two packages is forced at synthesis, not codegen**:
  `bsc -verilog` emits a `.v` for a BDPI module quite happily, then
  `yosys: ERROR: Can't resolve function name '\$imported_host_tape_read_word'`.
- **Pinout verified, not recalled**, from `ulx3s_v20.lpf` and
  `/opt/homebrew/share/trellis/.../iodb.json`: `sd_clk` H2 (`PCLKT6_0`),
  `sd_cmd` J1, `sd_d[0..3]` J3/H1/K1/K2, LVCMOS33, **all on bank 6**.
  **No card-detect and no write-protect** — both pads are commented
  "not connected" — and the SD lines are **shared with the ESP32**.
- **Clock domain is the one real constraint.** A 512-byte sector
  refills in ~0.98 ms at 25 MHz but **~7.37 ms at a 3.3333 MHz core
  clock**, against 8.19 ms of buffered play: 11% margin versus 8×.
  **Put the reader in the 25 MHz domain** with SyncFIFOs.
- **The tape byte rate this session used was ~2× too high.** This
  repo's own `docs/exchange_and_io.md:1112` quotes RefMan p.130: a 729
  IV at 556 bpi has a 170 µs average word period = **21.25 µs/byte =
  47 kB/s**, not the ~10⁵ B/s I asserted.

### WHAT WAS ACTUALLY CHANGED IN THE MODEL

`bsv/StretchTapeSource.bsv` (new) and the `StretchIO`/`StretchCore`
wiring. The tape read was a **combinational, random-access,
always-ready value method** — `readTapeWord(TapeIndex i) = tapeImg[i]`
— which no magnetic tape has ever resembled and which no external
source can implement. It is now request/ready/response, spelled the
same way `StretchStorage` spells it, whose header had already written
down this exact lesson for core storage: *"callers must NOT assume any
fixed latency, which is exactly the assumption the previous BRAM
version baked in."* The tape was the last device still making it.

`readTapeWord` survives as the testbench's window only;
`writeTapeWord` is still both paths, because writes are posted rather
than acknowledged — itself a simplification a card will force open.

`bsv/sd_reference/` holds the measured SD design, **not compiled by
`build.sh`**, with a README on the three things to take from it when
the boundary moves: the 24-bit word address (the in-tree `TapeIndex`
is four bits), `atEnd` in the response, and the `Server`/`mkConnection`
idiom that matches the local SDRAM driver. Two independent designs
converged on request/response, which is better evidence than either.

**UNRESOLVED AND NOT PAPERED OVER:** `capacity = maxBound` on the SD
leg makes `io_tape.strap`'s End Exception path unreachable on
hardware. The image's true word count needs a home — header sector,
build parameter, or the drive keeping its own limit. Neither the
agent nor I picked one.

## 5j. PLACE AND ROUTE RAN — and the part is decided by carry, not by storage

`docs/fpga_feasibility.md` gained §9 (~1,250 lines) on 2026-10-16, with
every script, log, RTLIL checkpoint and nextpnr report beside it. The
headline is a correction to §2.2.1 of the same document.

**SUPERSEDED THE SAME DAY, and the answer is a measured negative.**
Both whole-core runs finished ~20 minutes after the first hand-back
and both were routed. There is no one-unit 45F Fmax **because the
one-unit core does not place on a 45F** — and it fails on
combinational logic, not on anything the note had been watching:

```
ONE-UNIT mkStretchCore on LFE5U-45F (nextpnr)
  TRELLIS_IO       10 /   245     4%
  DP16KD           64 /   108    59%   <- exactly as predicted
  MULT18X18D       36 /    72    50%
  TRELLIS_FF    15505 / 43848    35%
  TRELLIS_COMB 362285 / 43848   826%   <- FAILS
  ERROR: no BELs remaining to implement cell type 'TRELLIS_COMB'
```

| configuration | COMB | DP16KD | MULT | |
|---|---|---|---|---|
| six-unit, 85F | **448%** | 184% | 23% | fails |
| one-unit, 45F | **826%** | 59% | 50% | fails |
| one-unit, 85F | **433%** | 30% | 23% | fails |

**NO CONFIGURATION FITS ANY ULX3S, AND THE BINDING CONSTRAINT IS
COMBINATIONAL LOGIC, NOT BLOCK RAM.** Everything §2.2 and §2.2.1 said
would fit does fit — block RAM, multipliers, flip-flops, IO are all
comfortable. The note's entire device discussion was organised around
block RAM, which turns out to be the easy axis. Whole-core LUT4 is
**283,931** (six-unit) / **271,449** (one-unit).

The CCU2C calibration that produced the earlier estimate is vindicated
and superseded: it predicted 365,803 COMB against an actual 375,223,
within 2.6%. **The verdict also survives the `-noabc9` caveat** —
granting abc9 its largest observed advantage (2.6×) still leaves
~186,000 COMB against the 85F's 83,640, i.e. 2.2× over. For `share`
to rescue it, it would have to remove more than half of all
combinational logic, and it has failed to terminate three times.

**THIS IS NOW THE MEASURED ARGUMENT FOR THE REWRITE.** Nothing in the
roadmap's effort table addresses a 4.3× logic overrun; items 2-9 are
about getting a design onto a board, and none of them makes the design
fit. The obvious candidate does not scale either — moving
`StretchIO`'s register images into a DP16KD targets 8,102 LUT4, about
**3% of 271,449**, and eliminating all three register files outright
does not approach 4×. What it points at is §6's own sentence, *"a
byte-serial datapath is small; a 5,019-line combinational one is 100k
lines of Verilog"* — i.e. the multi-cycle E-box / idiomatic-Bluespec
rewrite of AGENTS.md plan §1c. **§5g reached the same conclusion from
timing and §9 now reaches it from area. The number is 4.3×.**

**TWO AGENTS REACHED THIS INDEPENDENTLY, from different evidence.**
The synthesis study got there from yosys cell counts on the full
102,173-line `mkStretchCore.v` (459 s CPU, 11.1 GB peak RSS, main
storage blackboxed, `share` removed by hand and disclosed); the P&R
study got there from nextpnr's own refusal. They agree on the verdict
and on the cause, which is worth more than either alone.

**AND THE SYNTHESIS SIDE SAYS WHERE THE LOGIC IS.** Subtracting the
separately measured `mkStretchStorage` (13,427 LUT4) and
`mkStretchIO` (8,102) from the whole-core total leaves **~191,000
LUT4 for E-box + instruction unit + look-ahead + decode**. The
**17,634 `CCU2C` = 70,536 bits of adder** — far more addition than any
one instruction performs, which is the signature of *every
instruction arm computing its own result in parallel while a mux
picks one*. That is `StretchExecute.bsv`'s 5,019-line combinational
`execute()`, described in cell counts.

Two things that are NOT the problem, and both were suspected:
**multipliers** (36 `MULT18X18D` fits even a 45F's 72 — the floating
point unit is not what is big) and **block RAM** (the axis the whole
note was organised around).

### AND A SECOND, HARDER NUMBER: 844 LUT LEVELS — IT WOULD NOT MAKE 3.333 MHz EITHER

Measured 2026-10-16 with `depth_census.py`, a P&R-free logic-depth
census written by the `ulx3s-experiments` Flute session and shared
across (`~/src/ulx3s-experiments/flute-ulx3s/scripts/depth_census.py`).
**It is the only structural timing signal available to this project**,
because the design does not place and so nextpnr will never report a
critical path for it. Run on the routed-but-unplaceable one-unit
netlist `core1h.json` (436 MB): 36 s, 2.5 GB RSS. Full output kept at
`docs/depth_census_core1h.txt`.

```
endpoint pins: 55958
deepest endpoint groups (max depth, #bits, register.port):
  844.6  x64    core.st_indicators.DI
  839.8  x64    core.st_accLeft.DI
  839.7  x64    core.st_indicators.CE
  837.7  x64    core.st_remainder.DI
  447.0  x64    core.st_zerosOnesCounts.DI
  374.8  x1024  core.st_xreg.DI
  372.5  x64    core.st_accRight.DI
  ...
  368.9  x64    core.st_intervalTimerAndClock.DI
```

**The deepest path runs through a DIVIDE and lands on the indicator
register** — the trace is `core.dvs__h524305_LUT4_Z_40_...` through
hundreds of LUT4/L6MUX21/PFUMX levels into `core.st_indicators`. One
combinational `execute()` performs a division and updates the
indicators in a single clock. And it is not one stray path:
**~3.2% of the 55,958 endpoints sit at depth ≥349**, about 1,790 of
them, which is a population.

**WHAT IT MEANS, with the arithmetic shown.** §9's own calibration
measured pure 64-bit carry chains closing at **143.45 MHz on a 45F**;
a 64-bit chain is ~16 CCU2C levels, so **0.436 ns per level on
dedicated carry routing — the FASTEST path type the ECP5 has.** At
that optimistic rate:

| depth | delay | implied Fmax |
|---|---|---|
| 844 levels | 367.7 ns | **2.72 MHz** |
| 365 levels (the 3.2% population) | 159.0 ns | 6.29 MHz |

**The 0.3 µs machine cycle is 3.333 MHz = 300 ns. So the design does
not make its own target clock, by an optimistic bound, even before
considering that it does not fit.** General soft logic is slower than
dedicated carry — `depth_census.py`'s own header says ECP5 routing is
70-80% of path delay — so the true figure is worse; at a rough
1.0 ns/level it is ~1.2 MHz.

**THIS RETIRES §3's STANDING ASSUMPTION.** That section said "the
3.333 MHz target makes closure *plausible* — plausible is not
measured." It is now measured and it is not plausible. The low target
clock was the one thing that made the area problem look survivable;
it does not survive a 844-level combinational path.

**AND IT IS A SHARPER ARGUMENT FOR THE REWRITE THAN AREA WAS.** The
area finding (4.3× over) left open whether the idiomatic rewrite buys
enough, and §9 was honest that this was structural reasoning rather
than measurement. Depth is different: a multi-cycle box *by
construction* puts registers between the stages that are currently one
combinational cone, and the register names at the top of the census —
`st_indicators`, `st_accLeft`, `st_remainder`, `st_accRight`,
`st_xreg` — are exactly the E-box state the rewrite would stage.
**The census is also the regression metric that was missing**: it runs
in 36 s against a JSON, needs no P&R, and can be run per-commit while
the rewrite proceeds.

### THE CHEAPEST USEFUL NEXT STEP, 2-3 DAYS

**Make the per-module numbers measurable.** `mkEBox` cannot be
synthesised on its own today because it takes interface arguments, so
bsc refuses separate code generation; add a wrapper, trim the 129
test ports behind a board top level, and wire `bsc -verilog` +
`synth_ecp5` (~10 min CPU) into the loop. That converts "4.3× too
big" from a verdict into **a per-module budget the rewrite can be
steered against, and a utilisation regression metric this project
does not have today.** Do this before starting the rewrite, not
during it.

Revised effort, with the dominant item changed: logic reduction via
the idiomatic rewrite, 212,567 → under ~80,000 LUT4, **20-40 days,
highly uncertain**; first light 27-53 days, against the 3-7 days the
note originally carried.

**THE REAL OPEN QUESTION IS WHETHER THE REWRITE BUYS 4.3×.** The
argument that it does is structural — time-multiplexing N parallel
instruction arms onto one datapath is an N-fold saving on the shared
parts, and it is what the real 7030 E-box did — but **it is reasoning,
not a measurement**, and nothing here has measured it. The wrapper
above is what would turn it into one.

Two self-corrections inside that correction, both recorded: CCU2C is
not perfectly invariant across LUT mapping (41,060 → 40,936, 0.3%),
and the failing cell name (`st_xreg_8`'s write mux) is an
illustration rather than evidence — at 433% nextpnr would fail on
something.

**The 91.57 MHz figure below is the MEMORY SUBSYSTEM and must not be
quoted as the core's.**

### What was measured

| | result |
|---|---|
| **CCU2C**, six-unit core | **41,060** |
| **CCU2C**, one-unit core | **41,070** — ten cells apart |
| MULT18X18D | **36**, measured twice on independent elaborations |
| whole-core DP16KD | 384, identical to `mkStretchStorage` alone |
| whole-core TRELLIS_FF | 12,449 (28% of a 45F) |
| `mkMBCU` 1 unit on 45F | **91.57 MHz**, 59.3% DP16KD |
| `mkStretchIO` on 45F | 98.83 / 106.51 MHz (seeds 1/3) |
| six-unit storage on 85F | nextpnr **refuses to place** |

**THE CARRY LOGIC IS ENTIRELY CPU AND NONE OF IT IS MEMORY.** Dropping
from six memory units to one removes 320 block RAMs and ~1,179
flip-flops and moves the carry count by ten cells in forty-one
thousand. At a measured 2.15 TRELLIS_COMB per CCU2C (calibrated on a
purpose-built adder netlist), that is **≈82,100 COMB for carry alone —
1.87× the 45F's 43,848 and 98% of the 85F's 83,640.**

So **the one-unit build does not fit a 45F either**, and not for the
reason anyone was watching. §2.2.1's "a 45F could run the whole
transcribed corpus with storage entirely in block RAM" is correct
*about block RAM* — 64 of 108 DP16KD — and wrong about the part. **It
is the arithmetic that picks the device.**

Two more device exclusions now have independent grounds: **MULT18X18D
= 36 excludes the 12F/25F** (28 available), a third reason after block
RAM and LUTs; and §2.2's six-unit arithmetic is now **a router result,
not a calculation** — nextpnr says `Unable to place cell
'core.mbcu_units_2_ram_memory...', no BELs remaining for DP16KD`.
Also settled, a §7 open question: `--12k` exposes 24,288 LUT4 and 56
DP16KD, i.e. the 25F's numbers.

### THE ONE THING THAT COULD OVERTURN IT

The capacity verdict is taken **with yosys's `share` pass dropped**,
and `share` is precisely the pass that shares arithmetic. It was
probed directly from a post-coarse RTLIL checkpoint and **did not
terminate** in a 25-minute cap. The log root-causes it: `share`
enumerates activation patterns per arithmetic cell against every
`MUX_st_xreg_N$write$SEL` signal — quadratic in exactly the
register-file index muxes §1.2 already named as this design's size
problem. **What `share` does to 2,291 `$alu` cells is the open
question on which the device choice turns.**

### A BLOCKER §3.5 IMPLIED BUT NEVER QUANTIFIED

**`mkStretchCore` cannot be handed to nextpnr at all**: 3,894 port
bits against ~197 IO on CABGA381. Every whole-core P&R number will
need the non-pruning harness §9 builds (shift-register-driven inputs,
registered outputs, pipelined XOR fold), validated at +0.8% / +0.2%
LUT4 on two modules.

### AND A SELF-CORRECTION WORTH KEEPING

The study first concluded "use `-noabc9` for this model" from the MBCU
anomaly, **then tested it and was wrong.** A four-cell controlled
experiment shows abc9 is usually much better (2.6× on `mkStretchIO`),
and the `-noabc9` `mkStretchIO` netlist **failed to place on a 45F on
all three seeds** at 47% nominal utilisation where the abc9 netlist
routed at 98.83 MHz. The one-unit MBCU is an outlier, not a rule.
Separately, the MBCU anomaly is abc9's LUT mapper and **not** the
`unitOf`/`indexOf` edit: staged `stat` is monotonic at every stage
until `map_luts`, and `-noabc9` restores monotonicity.

### THE MACHINE WAS NEVER QUIET, AND IT WAS NEVER THIS PROJECT

Load ran 90-299 all session. **Verified first-hand: 446
`qemu-system-x86_64` processes**, belonging to
`~/src/inferno64-branches/parallelgc`. Agent and build jobs run at
**nice 5** against QEMU's **nice 0**, and `renice -n 0` exits 0 while
silently doing nothing (non-root cannot lower nice on macOS).
Effective throughput was 4-25% of one core — `bsc` spent 2m16s of CPU
over 19 minutes of wall clock. **Every "the machine is busy, I will
queue this" decision in this session was pacing around someone else's
VMs**, and the queued full suite never ran at all. Two sibling agents
were caught live in genuine tool pathologies (`SHARE` at 1h33m, `ABC9`
with a 50-minute-frozen log), so the starvation is real but it is not
the whole story.

**§2.6's "nextpnr is unrecoverable" is retracted in §9.0**, and the
cause is now known: that search used `find / -maxdepth 4` and the four
working arm64 builds sit at depth 6.

## 5k. THE MCP CRITICAL PATH, IN DEPENDENCY ORDER

Synthesised 2026-10-16 from §5h, §5i and §5j. Everything below is
specified by a source already read; none of it is blocked on research.
**The order is forced by dependencies, not preference.**

### Model work — nothing boots until all five exist

**ORDER CORRECTED 2026-10-16.** This list first put tape records
first, reasoning that "End of Block" is a COLUMN in Figure 36 so
chaining could not be written without them. `docs/tape_unit_contract.md`
§2.2 gives a different order — **5, 8, 6, 7 (IPL works), then 1, 2,
then 3, 4** — and it is right, for a reason worth keeping:

> For IPL the fixed word is `count = 1, chain = 1`, and after one word
> the count is zero **mid-record**. Figure 36's row for
> (multiple 0, chain 1, count zero, end-of-block **No**) is **"Chain
> and continue"** — exactly what IPL needs. A model that simply never
> reports end-of-block therefore gets the IPL hand-over right. What it
> gets wrong is the *second* control word's completion: (0,0,0,No)
> gives "Disconnect, then end op." where a real end-of-block would
> give "End operation" — a difference in whether a disconnect signal
> is sent, not in whether the bootstrap loads.

So records are **not** a prerequisite for milestone A; they are a
prerequisite for honesty about block termination, and for the whole
CONTROL table. Numbering below is kept as-is for cross-reference with
the contract; **do them in the order 5, 8, 6, 7, 1, 2, 3, 4.**

1. **Tape blocks (records).** ~50-70 lines, replacing the flat
   `Vector` with a byte image plus a record table (`RecDesc = {start,
   length}`, a tape mark being a one-byte record). It unlocks the
   whole remaining CONTROL table at once — SPACE BLOCK, SPACE FILE,
   BACKSPACE FILE, WRITE TAPE MARK — which `StretchIO.bsv` currently
   declines for exactly this reason.
2. **Chaining, per Figure 36.** The complete 16-row table is already
   transcribed in `docs/exchange_and_io.md` §3.3 with its supporting
   rules, so this is implementation, not research. **Without it IPL
   reads one word and stops** (§5i, resolved against RefMan p.126).
3. **The SEOP status bit, control-word bit 24.** Nothing writes it
   today. Both `ka_ul1`'s driver and MCP's own bootstrap poll it with
   `CCW` + `BB`; **the real driver idiom hangs without it.**
4. **The IPL mechanism itself.** `StretchIO.bsv:288` says verbatim
   that there is none. RefMan p.126 specifies it completely: plant
   the fixed control word (addr 4, chain 1, count 1, refill 4) in the
   signalling channel's control-word location, READ, let the refill
   chain to location 4, then send the initial-start signal; the CPU
   executes the instruction at that control word's data word address
   **without placing it in the instruction counter**. Note EOP, EE and
   CS must NOT be set on completion.
5. **`SPFL`, `LOC`, and `UNLOAD` as distinct from `REWIND`.**
   `StretchExecute.bsv:3372,:3376` has the first two unimplemented and
   the third conflated. MCP's bootstrap uses `SPFL(SEOP)` on its
   third page — **and `LOC(SEOP)` on its fifth, to ask each channel
   whether it is a tape** (§6f). Both now have listing witnesses.

   **HALF DONE, 2026-10-17: `SPFL` ASSEMBLES.** `strap_asm.py` gained
   `IO_FUNCTION_OPS`, the first of C28-6129 Appendix B's twenty I-O
   function pseudo-operations, checked bit-exact against printed p.3
   line 35 (`000000.00 8F 000077.15 00`). The MODEL still rejects
   control code 077 and that is what remains of this item. **Only
   `SPFL` went in** — the other nineteen would be a name matched to a
   name in a different document's table, which is rule 4 inference;
   `mcp_tape_manufacture.md` now carries the whole family with its
   evidence, row by row, so the next one to go in has its case
   already written down.

   **`SPFL` LANDED IN THE MODEL on 2026-10-18** (control code 077 as
   an `untilMark` transfer) and **`LOC` IS NOW HALF BUILT**, which is
   the part of this item that needs restating rather than ticking.

   LOCATE IS TWO OPERATIONS WEARING ONE MNEMONIC. C22-6531 Appendix A
   printed p.57 lists it once — "E LOC Locate (same as Select Unit)"
   — and the Reference Manual describes it twice, in two chapters:

   * **On a disk channel it is a SEEK.** Printed p.160: "the right
     effective address… specifies the arc address". **Built**, with
     the arc address register, the arc-addressed READ and WRITE, the
     short write's zero-filled tail, and the control word's flags and
     refill discarded (printed p.158). Driven by `decks/io_disk.strap`
     — eighteen checks, none through a peek method. See
     `docs/disk_subsystem.md` §9a.
   * **On an Exchange channel it is SELECT UNIT.** Still Operation
     Code Invalid, because this model has one unit per channel and no
     selection hierarchy to navigate. **This is the form MCP's ERROR
     ROUTINE uses** (printed p.5 line 36, §6f), so the half that is
     left is exactly the half this item was opened for.

   So the item stays open, with its scope now one half of one
   mnemonic plus `UNLOAD`-vs-`REWIND`.

### Artifact work — can proceed in parallel with the above

6. **Transcribe MCP's IPL bootstrap**, printed pp.2-14, ~350 rule-3
   rows, **~4 days** at this repo's measured rate. The listing has a
   BINARY OUTPUT column (§5i), so `listing_oracle.py` applies and
   every row is checked. ~1.3× the largest program already in the
   corpus. **Do items 1-5 first or in parallel** — a transcription
   that cannot be run is not verified in the way this project means.
7. **Assemble and wrap as a tape image.** `ka_ul1` settles the
   format: one `W`, no tape mark, no label, no preamble. The first
   word of the image is MCP's own control word.
8. **`mkTapeSourceFile`** behind the existing `TapeSource` interface.
   Value-typed `import "BDPI"` is proven to work — built and run, see
   `bsv/sd_reference/`. Amend `StretchIO.bsv`'s header, which still
   claims `$fopen`/`$fgetc` being Actions forces pre-loaded `Vector`s.
9. **`mkTapeSourceSD`** for the board. Measured at ≈ −237 LUT4,
   −304 FF, +112 CCU2C net. Put the reader in the 25 MHz domain, not
   the core clock (11% margin versus 8×).

### RESOLVED — it does not reorder anything, and it names the first milestone

The open question was whether MCP's bootstrap needs a populated disk.
**It does not need one to LOAD; it does need one to FINISH** (§5i,
settled from printed pp.12-14). So:

- **Milestone A — the machine IPLs from tape and starts executing
  MCP's bootstrap.** Items 1-5 and 6-8 above. **No disk.** This is a
  real result on its own: a 7030 recreation running IBM's own system
  software off a tape image.
- **Milestone B — the bootstrap runs to completion.** Adds the disk
  model, ~100-170 lines for the boot-sufficient subset (§5h). The
  bootstrap carries a 42-entry `PROSA CWS` table and can report
  `PROSA ARC COUNT INCORRECT`, so it reaches the disk while running.

**Aim at A.** It is the smallest thing that would let the user say
they booted real IBM systems software on their recreation, and it is
reachable without the disk, without the Exchange's full
channel/control/unit hierarchy, and without all 445 pages of MCP.

### What is NOT on the critical path, despite looking like it

- **The disk**, for boot purposes — MCP writes it at IPL, does not
  read from it (§5h), subject to the caveat above.
- **Cycle accuracy** — the user's order is MCP first (§5g).
- **Six memory units.** Every transcribed deck row sits below word
  14,104, inside a single 16,384-word unit, and §5j shows unit count
  barely moves the FPGA numbers anyway.

## 5l. THE BOOT PLAN — `docs/boot_plan.md`

Written 2026-10-16 in answer to "get MCP and all other extant code
booting". Two things in it are not obvious from §5h-§5k:

**THE FIRST MILESTONE NEEDS NO TRANSCRIPTION.** A ten-line program
written by hand, assembled here, wrapped as a tape image, IPL'd from
a file in Bluesim and from the SD card on the board. Prove the path
before investing in content; transcribing MCP first and *then*
finding the IPL path broken is the expensive mistake available.

**THE DIAGNOSTIC CONTROL PROGRAM OUTRANKS MCP AS THE FIRST REAL
TARGET.** `ka_ua1_diagnostic_ctl_pgm.pdf` pp.19-152 is the master
harness: it IPLs, reads a schedule, loads and checksums each test off
a master tape, and via `J1`/`J2` **builds that tape from individual
decks**. It is the harness for the **243 programs already
transcribed** — nothing else makes the existing corpus run as a
system. Machine-code column verified by render. ~75 days whole, but
sliceable, and no disk is known to be required.

**And the cheapest high-value action in the whole plan is two pages**:
the STRETCH MAINTENANCE COMPOOL at PDF pp.129-130, 65 `SYN` entries,
which `archival_inventory.md` calls the Rosetta stone resolving
symbols referenced by *every other* deck in `docs/diag/`. Until it
exists every other listing's symbols dangle. Do it regardless of what
else happens.

Two assumptions in the plan are flagged there as unchecked: that DCP
needs no disk (nothing has looked), and how much disk MCP's bootstrap
really needs (`$IPLD`, printed pp.15-36, 3 of 22 pages sampled).

## 5m. THE COMPOOL'S `&` IS ADDITION — settled by arithmetic, 11 rows out of 11

Raised and resolved 2026-10-16 while starting the two-page STRETCH
MAINTENANCE COMPOOL (`ka_ua1_diagnostic_ctl_pgm.pdf` PDF pp.129-130),
which `docs/boot_plan.md` makes the cheapest high-value action in the
plan.

**THE PROBLEM.** The page header is `@STRETCH MAINTENANCE COMPOOL,
NOVEMBER 20, 1961` and the rows run
`EBMAIN  SYN,ECTL1&.01 ... 4006.01&`. Rendered at **600 dpi, cropped
to one column**, the operator glyph is unmistakably an ampersand form
— closed lower loop, diagonal — and **not** a `+`, even though the
MCP listing prints an ordinary `+` in the structurally identical
place (`000041.00+ 000 000560 000001`). Transcribing it wrong would
corrupt 65 definitions that `archival_inventory.md` says *every other
deck in `docs/diag/`* depends on.

**THE RESOLUTION IS ARITHMETIC, NOT GLYPH-READING.** Every row on the
page is its own check, because the listing prints both the expression
and the resulting address. Taking the operator as addition, the
offset as a DECIMAL bit count and the address column as OCTAL:

| symbol | expression | predicted | printed |
|---|---|---|---|
| `EBMAIN` | `ECTL1 + .1` | `.01` | `.01` |
| `EBBLNK` | `ECTL1 + .46` | `.56` | `.56` |
| `ETAPCM` | `ECTL2 + .12` | `.14` | `.14` |
| `EB16CH` | `ECTL2 + .61` | `.75` | `.75` |
| **`MNTCTL`** | **`ECTL2 + .62`** | **`.76`** | **`.76`** |
| `EBDRSP` | `ECTL3 + .17` | `.21` | `.21` |
| `EDPLOC` | `ECTL3 + .32` | `.40` | `.40` |
| `EQRDR2` | `EQAV1 + .16` | `.20` | `.20` |
| `EQRDR4` | `EQAV1 + .48` | `.60` | `.60` |
| `EQTAP8` | `EQAV7 + .48` | `.60` | `.60` |

**11 of 11**, and the decisive one is `MNTCTL`: its row prints
`SYN, ECTL2.62` with **no operator glyph at all**, and the arithmetic
still comes out. A row where the character is simply absent and the
sum still holds is independent evidence that the character is an
operator and that the operator is addition — evidence that does not
depend on reading the glyph.

**WHAT TO WRITE.** `+`, with the print recorded as a substitution in
the transcription's header, exactly the way `%8@n` -> `(8)n` and
`$BD,0` -> `BD,0` are already handled. The glyph is consistent with
the 12-zone punch, which prints `&` on BCDIC chains and `+` on EBCDIC
ones — **that remains a hypothesis about WHY and nothing rests on
it.** What the transcription rests on is the eleven-row check.

**A NOTE ON METHOD.** The first instinct here was to settle a
character by looking at it harder, and 600 dpi made it *more*
confident and *less* useful — the glyph really is an ampersand. The
page turned out to carry its own oracle: an expression and its
evaluated address on every line. **When a listing prints both an
expression and its result, the arithmetic outranks the typography.**

### TRANSCRIBED, 2026-10-16 — 65 symbols, 55 genuine checks, 0 failures

`decks/dcp_compool.strap` + `tests/verify_dcp_compool.py`,
wired into `run_tests.sh` (392 -> 393 run lines). 51 entries from PDF
p.129 and 14 from p.130.

**It is not a rule-3 check and the files say so.** A `SYN` emits no
code, so there is no machine-code column to compare. What the page
*does* print on every row is the resolved address, so the oracle is
the assembler's symbol table against that column. Of 65 symbols, **55
are genuine** and **10 are circular by construction** — the rows with
no offset of their own, whose base symbols (`ECTL1-4`, `EQAV1-7`,
`EDCP1`, `ACA`) are defined elsewhere in the DCP and were
back-computed here from the printed results. The circular ones are
reported separately by the verifier rather than counted as passes.

**p.130 confirmed the convention independently.** Its address column
runs `0.00& 1.00& ... 7.00& 10.00& 11.00& ... 15.00&` — **octal,
skipping 8 and 9** — against decimal offsets `ACA+8.0 ... ACA+13.0`.
A second page, a different table, same decimal-offset/octal-address
rule.

**AND A SELF-CAUGHT OVERCLAIM.** The first draft of the verifier
computed p.130's addresses from `ACA` plus the offsets and wrote them
as though the listing printed them. It had never been read. The
column was then rendered and read, the values were right, and the
comment now says they were read — but **the check cost two minutes
and the assertion would otherwise have been exactly the kind this
file's traps list is full of.** Deriving a value and printing it in
the column labelled "what the listing says" is the same error as
quoting an agent's number without a render.

### STILL OPEN, and smaller

The `&` in the address column (`4006.00&`) and the binary column
(`&00000000`) sits where MCP prints a `+` sign. Nothing in this
project reads those columns for the COMPOOL, since a `SYN` emits no
code, so it does not block the transcription — but it is unexplained
and should not be silently normalised if a later listing needs it.

## 5n. CHAINING IS NOW TESTED — 39/39, and the test caught my error not the model's

`io_tape.strap` gains a sixteenth block and `gen_tape_tb.py` five
checks, 34 -> 39. Chaining went in earlier today with the commit
message saying plainly that the suite never took the new branch; it
does now.

**THE SHAPE IS IPL's, deliberately.** RefMan printed p.126's fixed
control word is chain 1, count 1, refill 4 — it reads exactly one
word and refills from the address in its refill field. `CTLWA` is
count 1, chain 1, refill -> `CTLWB`; `CTLWB` is count 3 into a
different block. After a REWIND to the load point, tape word 0 lands
in `CHBLK1` and words 1-3 in `CHBLK2`.

**THE DISCRIMINATOR EARNED ITS KEEP.** The block was designed so that
a model ignoring the chain flag stops after one word: `CHBLK1` passes
and all three `CHBLK2` checks read zero. On the first run **`CHBLK1`
failed too**, which the design says means something different — the
transfer never happened at all — so the next step was to decode
rather than to touch the model.

`CCWQ` came back as `CTLWA` unmodified except `ee = 1`: End
Exception, "the unit runs out of material". **The REWIND had not
happened.** `io_tape.strap` writes CTL codes in DECIMAL with the
octal in the comment — `CTL, 0($1), 94  !REWIND (octal 136)` — and
the new block had been written `136`, a different and unimplemented
code. The tape was still at position 16 from the End Exception step
above, so the read took an immediate EE and moved nothing. **The
model was right and the test was wrong**, and the only reason that
was obvious in one step is that the checks were built to tell the two
failures apart.

`CCWQ` is independently discriminating from the content checks: a
model ignoring the chain flag would leave `CTLWA`'s own exhausted
word in the exchange's copy (dataAddr `CHBLK1`+1, chain 1), where the
passing value is `CTLWB` walked to completion (dataAddr `CHBLK2`+3,
count 0, chain 0).

**Still not covered**: p.123's "count zero means 2**18" on a refilled
control word, and every Figure 36 row other than
(multiple 0, chain 1, count zero, end-of-block No) — the model cannot
reach the end-of-block rows at all until records exist.

## 5o. THE SEOP BIT — half of `tape_unit_contract.md`'s rule 31 is an INFERENCE, and the model would hang either way

Found 2026-10-16 while starting `boot_plan.md` M1's cheapest item.
**Do not implement rule 31 as written.**

`docs/tape_unit_contract.md` §2.2 item 8 says: *"The SEOP status bit
must be set at issue and cleared at completion (rule 31)."* The first
half is quoted; the second is not.

**WHAT THE MANUAL ACTUALLY SAYS**, Reference Manual p.121, via this
repo's own extract in `docs/exchange_and_io.md` §3.11:

> "At the time an SEOP instruction is given, the SEOP bit in the
> control word is set to one. **As the result of this, the EOP bit in
> the control word (and therefore in the indicator register) is not
> turned on** unless it is accompanied by unit check or end exception."

That is the bit's whole stated purpose: **it suppresses EOP.** There
is no sentence anywhere in §3.11 about the exchange clearing it when
the operation finishes. The field table confirms the bit itself —
bit 24, `w[39]`, "Status: Suppress End of Operation (SEOP)" — so the
model's `ControlWord.seop` is in the right place; it is the dynamics
that are unsourced.

**WHY IT CANNOT BE GUESSED.** Both real drivers poll it. MCP's own
bootstrap, on the page rendered for §5i:

```
42*  000074.00  ...  X8 1  CCW,0($15),X IPL BS      -GET STATUS BITS
45*  000076.00  ...        BB,X IPL BS+.24,X 8 1    -IF SEOP OFF
```

and `ka_ul1`'s tape-write routine does the same. If the bit is set at
issue and never cleared, a loop that spins while it is 1 never
terminates. If it is cleared and a loop spins while it is 0, the same.
**The model hangs on one reading and works on the other, and nothing
read so far distinguishes them.**

Note MCP's own comment is `-IF SEOP OFF`, which reads as though OFF is
the interesting state — consistent with "set at issue, cleared at
completion" — but a comment is not an encoding, and this project has
been wrong about a branch polarity from a comment before (see
`ax5b_160_test8b` in §2).

**CHECK 1 IS DONE, AND IT IS A CONFIRMED NEGATIVE.** Reference Manual
printed p.121 (PDF 124) was rendered and read whole, both columns.
`exchange_and_io.md` §3.11's extract is **faithful** — it dropped
nothing. The SEOP section covers: the bit being set at issue; EOP
being suppressed unless accompanied by unit check or end exception;
exceptional conditions (EPGK, UK, EE) not being suppressed; a channel
signal during an SEOP not turning on EOP; and RELEASE SEOP. **No
sentence on the page says the exchange clears the bit at completion.**

Two things the whole page did yield:

- **The only clearing-adjacent language on the page is about RELEASE
  SEOP**, not about completion: *"If the addressed unit is executing
  an instruction at the time RELEASE SEOP is given, the SEOP bit is
  **temporarily** set in the control word."* "Temporarily" implies
  something clears it, and the page never says what. It is a hint,
  not a rule, and it is about a different instruction.
- **The model's REL arm is corroborated**: *"RELEASE SEOP can be used
  to turn off EPGK, UK, EE, CS as well as any previously set EOP bits
  in the control word"*, which is exactly what MCP's
  `REL(SEOP),0.0($15)  -CLEAR EE AND EOP STATUS BIT` is doing.
  `StretchExecute.bsv:3381` already clears epgk/uk/ee/cs on REL.
  **But it also clears `seop`, and p.121 says REL SEOP *sets* it
  temporarily** — a second, smaller discrepancy, recorded here and
  not acted on.

**RESOLVED, 2026-10-16: THE BIT IS CLEARED AT COMPLETION**, on the
strongest evidence available short of a manual sentence — and the
decisive step was a rule-3 check, not a reading.

MCP printed p.3 line 45 prints

```
45*  000076.00  000041.30 80  000074.34 02   BB,X IPL BS+.24,X 8 1
```

and this repo's assembler, given `BB, XIPLBS+.24, X81` with
`XIPLBS = (8)41.0` and `X81 = (8)74.0`, emits

```
first half-word  000041.30 80      second half-word  000074.34 02
```

**character-for-character identical.** So the instruction is `BB`,
not one of its seven siblings, and `strap/opcodes.py`'s `BB_CODES`
has `BB: (0b00, 1)` — **branch when the bit is ONE**. `X 8 1` is the
`CCW` two rows above it. Therefore MCP's bootstrap **spins while bit
24 is set and falls through when it clears.**

So the exchange clears the SEOP bit at completion, or IBM's own
bootstrap never leaves this loop. `ka_ul1`'s tape-write routine is an
independent second witness on a different printer by a different
author, and p.121's *"the SEOP bit is **temporarily** set"* for
RELEASE SEOP is consistent with something clearing it.

**THE EVIDENCE IS STILL USAGE-BASED AND THAT IS SAID PLAINLY.** No
sentence in the manual states the clearing rule; p.121 was read whole
and does not contain one. What makes this different from the
inference rule 4 forbids is that the *instruction's* meaning is not
being guessed — it is bit-exact against the print — and two
independent IBM programs are structurally unable to work without the
behaviour. That is weaker than a quotation and much stronger than a
plausible reading, and the implementation should carry exactly that
caveat.

**IMPLEMENTED 2026-10-16**, set at issue in `StretchExecute.bsv`'s
RD/W arm and cleared at both of `rl_io`'s terminal paths. io_tape is
39/39, identical to baseline — as predicted, since every `CCW` in
that program is read *after* completion and so sees 0 under both the
old behaviour (never set) and the new (set, then cleared).

**AND IT IS UNOBSERVABLE BY ANY PROGRAM THIS MODEL CAN RUN, which is
the part worth knowing.** `StretchCore.bsv`'s arm conditions are all
`!isValid(ioPending)` — `armIdx`, `armResume`, `armRemove`,
`armInterrupt`, `armPrepare`, every one of them — so **no instruction
executes while a transfer is pending.** Transfers are synchronous
from the program's point of view. A driver polling bit 24 therefore
reads it *after* completion, every time, and finds 0 on the first
iteration.

Three consequences, none of them reasons not to have done it:

- **MCP's polling loop will terminate, but it will not spin.** The
  model does not reproduce the wait, only its exit. That is the right
  outcome for booting and the wrong one for timing.
- **The bit cannot be given a test in this model.** Unlike chaining,
  which was untested only until someone wrote the test, this is
  untestable by construction until I/O overlaps execution. Recorded
  as a different category of gap.
- **It is a stage-3 look-ahead item.** `StretchIO.bsv`'s header
  already calls synchronous whole-block transfer a documented
  simplification; this is the first place where that simplification
  has a *visible* consequence for real IBM software rather than only
  for cycle counts.

**THE REMAINING CHECKS, if it ever matters again:****Until one of those is done, `boot_plan.md` M1 item 8 is blocked**,
and it is the item the plan calls cheapest. Recorded rather than
implemented, because an unsourced guess here does not fail loudly —
it hangs, and a hang in an IPL path is exactly the failure that is
hardest to attribute later.

**AND A NOTE ON THE CONTRACT ITSELF.** `tape_unit_contract.md` is
excellent and this does not change that; its 38 rules are mostly
quoted and cited. But it was written by an agent, this project
committed it today, and rule 31 blends a quotation and an inference
into one sentence without marking the seam. **When a derived document
states a rule, the citation needs to cover the whole rule, not its
first clause.** Worth a pass over the other 37 before they are built
on.

## 5p. THE MACHINE BOOTS FROM A TAPE IMAGE — `boot_plan.md` M1 reached

2026-10-17. `decks/ipl_boot.strap` + `gen_ipl_tb.py` +
`run_ipl_test.sh`, in `run_tests.sh` (394 -> 395 run lines).

```
PASS ipl_program_executed   = 0x9a400000000000
PASS ipl_loaded_entry_word  = 0x102400009a4301
PASS ipl_loaded_second_word = 0x10831000106800
PASS cycles = 237 (bound 300)
PASS PC (half-word address) = 131
```

**NOTHING WAS TRANSCRIBED TO GET HERE**, which was the whole argument
for this milestone order. Three instructions written by hand,
assembled by this repo, wrapped by `mktape.py`'s own
`pack_control_word`, and read off the simulated tape by the sequence
RefMan printed p.126 specifies. **Core storage starts at zero** —
`gen_tb.generate(ipl=True)` suppresses the program-word load rule
entirely, so pre-loading cannot be hiding a broken read.

**CHAINING NEEDED NO CHANGE, and that is the finding.** `iplStart()`
plants the fixed control word (data address 4, chain 1, count 1,
refill 4) and reads ONE word; the count exhausts; the chaining built
on 2026-10-16 refills from location 4, which now holds the word just
read off the tape; that word is a control word naming where the
program goes and how long it is; the rest loads under it. The
hand-off that reads like a special mechanism in p.126 **is** chaining,
which is why the manual can describe IPL in five short steps.

**THE FAILING RUN WAS WORTH MORE THAN THE PASSING ONE.**
`ipl_program_executed` first came back `0x9a400000000000` against an
expected `1234` — and that was the test's error, not the model's.
`0x9a400000000000 >> 40 = 39488 = 1234 x 32`: STRAP's bare operand in
`LVI,$X1,1234` is a **half-word address**, and an index word's value
field (IBM bits 0-23) holds a **bit** address. Every other check
passed on that run, including both loaded-word checks and the halt
PC, which is what identified the IPL path as already working. The
three checks were built to separate exactly those failure modes and
they did.

### WHAT M1 DOES *NOT* YET HAVE

- **The tape image is still the 16-word `Vector`**, though the
  *interface* is no longer limited to it — see §5q. A file- or
  SD-backed source is `boot_plan.md` M0 steps 1 and 4. **Neither was
  needed to prove the path**, which is why they come after.
- **The channel signal is folded into `iplStart()`**, honest for one
  unit at selection address 0 (p.126 allows loading only from such a
  unit) and open for the multi-unit case.
- **The PC departure stands**: p.126 says the entry address is *not*
  placed in the instruction counter and this model puts it there.
  Unobservable while the first instruction is `BD`, which the same
  page requires.
- **237 clocks is recorded, not validated.** No source gives an IPL
  duration; the bound is a regression guard, not a timing claim.

## 5q. THE TAPE INDEX IS 24 BITS, AND CAPACITY COMES FROM THE SOURCE

2026-10-17, `boot_plan.md` M0 step 2. io_tape 39/39 and the IPL boot
5/5 at the same 237 clocks, so this is behaviour-preserving.

**THE OBVIOUS MOVE DOES NOT WORK, and that is why this is shaped the
way it is.** Raising `TapeWords` from 16 would widen the derived
index for free — and it would break
`decks/io_tape.strap`, which reaches End Exception by
running a 20-word transfer off the end of a 16-word tape.
`gen_tape_tb.py`'s `CCWJ`/`CCWP` expectations literally encode "16 of
20 words transferred". **Sixteen is load-bearing for that test.**

So the image size and the address width were decoupled instead:

| | before | after |
|---|---|---|
| `TapeIndex` | `TLog#(TapeWords)` = 4 bits | **`Bit#(24)`**, 16.7M words |
| `TapePos` | 5 bits | **`Bit#(25)`** |
| `IoXfer.devIdx` | `Bit#(6)` | **`Bit#(25)`** |
| tape capacity | `valueOf(TapeWords)` in `StretchCore` | **`ioDev.tapeCapacity()`** |

**The capacity change is the one that matters.** The End Exception
test — *"the unit runs out of material"*, RefMan p.121 — was reading
a typedef, which silently assumed the register-backed implementation.
A file- or SD-backed source holds a reel and has to be able to say
so. `mkTapeSourceVector` reports 16 and nothing observable moves.

Two notes for whoever adds the next source:

- **`truncate(i)` inside a `Vector` index is a bsc type error**
  (T0035, "Bit vector of unknown size"): indexing accepts any width
  so there is nothing to infer from. The narrow index has to be a
  named, explicitly typed binding. Cost one build to learn.
- **`readReq`/`write`/`peek` guard the range and return zero past the
  end.** The caller gates on `capacity()`, so this is unreachable —
  but a 24-bit address into a 16-entry `Vector` aliases silently if
  that contract is ever broken, and a zero is much easier to notice.

The reader and printer are untouched: still fixed-size `Vector`s in
`StretchIO`, still truncating `devIdx` to `DeviceIndex` unchanged.

## 5r. `ka_ul1`'s TAPE WRITE ROUTINE CORROBORATES THREE COMMITTED THINGS

Read 2026-10-17: `docs/ka_ul1_load_and_tape_write_util.pdf` PDF p.17,
headed `@@@TAPE WRITE`, 29 rows with printed machine code. This is
IBM's own program for writing an IPL tape, and it independently
confirms three things this project had committed on weaker evidence.

**1. `mktape.py`'s LAYOUT IS IBM's.** The routine does, in order:

```
ST%BU,END                @TAPE WRITE CW.
LV,$X3,END
ST%BU,0%$X3              @IPL CW.
L%BU,32,B5,32
ST%BU,1.0%$X3            @IPL BD.
...
W%SEOP,0%$X1,END         @WRITE IPL TAPE.
```

`LV,$X3,END` loads the *value field* of the control word just stored
at `END` — i.e. its data word address — so `$X3` points at the buffer
the `W` will transmit. Into that buffer it puts the **IPL control
word at offset 0** and the **IPL `BD` at offset 1.0, one word later.**

That is exactly `strap/mktape.py`: word 0 of the image is a control
word, word 1 is the program, and the program starts with `BD`.
Derived here from RefMan p.126 and MCP's p.2; now confirmed against
the utility that actually wrote these tapes.

**2. ONE `W`, NO PREAMBLE.** `W%SEOP,0%$X1,END` writes the whole
thing against one control word. No tape mark, no label, no header
record — which is what `ka_ul1` was cited for in `boot_plan.md` and
is now visible in the code rather than taken from a summary.

**3. A THIRD WITNESS FOR THE SEOP POLL, and it is bit-exact.** The
routine polls three times, after the `LOC`, the `W` and the `UNLOAD`:

```
CCW,0%$X1,LDRCCW              0.00 81 000164.21 00   at 000565.40
BB,LDRCCW&.24,$-1.0      164.30 80 000565.74 02   at 000566.40
```

`$-1.0` is one word back — the `CCW`. So: copy the control word,
branch on bit 24 back to the copy, repeat. This assembler, given
`BB, LDRCCW+.24, $-1.0` with `LDRCCW = (8)164.0` at `(8)566.40`,
emits **`000164.30 80` and `000565.74 02`** — character for
character.

§5o settled the clearing rule on MCP's single loop plus p.121's
"temporarily". This is a second program, by a different author, on a
different printer, using the same idiom three times in twenty rows.
**The bit must clear at completion or none of these loops terminate.**

**4. AND `UNLOAD` IS OCTAL 137 VERBATIM.** `UNLOAD%SEOP,0%$X1`
prints `000137.15 00` — right effective address `000137`. Confirms
`strap_asm.py` is right not to apply the `>>6` word-address
conversion to `CTL`'s second field, which `archival_inventory.md`
already recorded from this file and which is now re-read directly.

### NOT TRANSCRIBED YET, and why

The 29 rows use VFL and connective forms this corpus has little of —
`L%BU,6,6,MNREG&.12,45`, `&%BU`, `-I%BU`, `&I%BU`, `ST%BU`,
`LOC%SEOP`, `W%SEOP`, `UNLOAD%SEOP` — and the control word is
*computed* at run time from `LIC`/`MIC` rather than assembled. That
is a real transcription with real syntax risk, and it is
`boot_plan.md` M2 rather than a side errand. What is recorded here is
only what was read first-hand and checked.

## 5s. THE TAPE COMES OFF A FILE NOW — 19 words, past the 16-word ceiling

2026-10-17, `boot_plan.md` M0 step 1. `bsv/StretchTapeSourceFile.bsv`
+ `bsv/host_tape.c`, selected in `StretchIO.bsv` behind
`` `ifdef HOST_TAPE ``.

```
host_tape: mounted /tmp/stretch_ipl_big.tape, 19 words
PASS ipl_file_program_executed    PASS ipl_file_second_store
PASS ipl_file_loaded_entry_word   PASS ipl_file_past_16_words = 0x1fffff
PASS cycles = 285 (bound 1200)    PASS PC = 133
```

**WHY A SECOND BOOT PROGRAM.** `ipl_boot.strap` is four words and
proves the *sequence*; it cannot prove the *scale*, because a path
that silently truncated at sixteen words would pass it unchanged.
`ipl_boot_big.strap` assembles to a 19-word image with `MARKER` as
its last word, so **a truncating path fails on `MARKER` and nowhere
else** — the program would still run, both stores would still land,
the entry word would still match. That one check is the ceiling.

**AND THE SCALE IS THE POINT.** MCP's IPL bootstrap is 369 words
(printed p.2's control word: count `0o560` = 368, plus the control
word). Sixteen is not within a factor of twenty of it, so M3 was
unattemptable until this existed. It is now.

### TWO DECISIONS THAT WOULD HAVE BITTEN

- **`` `ifdef `` rather than a module parameter.** `import "BDPI"`
  has no Verilog back end. bsc *will* emit a `.v` for a module using
  one — as VPI wrappers — and yosys then fails with
  `Can't resolve function name '\$imported_host_tape_read_word'`.
  A runtime or parameter choice cannot keep the BDPI package off a
  bitstream path; guarding the *import* can.
- **A separate `-bdir`, and this is the quiet one.** The two builds
  differ only by a `-D`, and bsc's `.bo` files carry no record of it.
  A `StretchIO.bo` built without `HOST_TAPE` is silently wrong for a
  build with it, and the symptom is **a tape that reads zeros, not a
  compile error.** `run_ipl_file_test.sh` uses
  `build-hosttape`/`simbuild-hosttape` for exactly that reason.

**AN OBSOLETE NOTE RETIRED.** `StretchIO.bsv`'s header has said since
it was written that bsc's `$fopen`/`$fgetc` are Actions and so force
pre-loaded `Vector`s. True of those primitives, irrelevant here: a
BDPI function whose result type is **not** Action may be called in a
value context from inside a rule. The idiom is the user's own, from
`~/src/alto-bluespec/src/Disk.bsv:18-23`.

**IN `run_tests.sh` as of 2026-10-17** (395 -> 396), added only after
the full suite finished reading the file — `sh` reads a script by
byte offset and editing it mid-run is the hazard `AGENTS.md` names
explicitly.

## 5t. MCP's SPACED SYMBOL NAMES ARE BLANKS STRAP IGNORES — M3 needs no assembler change for them

Checked 2026-10-17, before starting M3's transcription, because it
looked like the biggest blocker and turned out not to be one.

**THE WORRY.** MCP's listing prints names with embedded blanks —
`X IPL BS`, `X BS END`, `XW SR`, `X CL IND`, `X S ROOF` — and a
symbol containing a space is not something `strap_asm.py` accepts.
If those were real, M3 would be blocked on assembler work before a
single row could be transcribed.

**THE EVIDENCE IS ARITHMETIC, not a quotation.** C22-6531 printed
p.10 (PDF 11; this document's offset is printed + 1):

> "A symbol is any sequence of **six or fewer** alphabetic and
> numeric characters conforming to the following conditions:
> 1. It contains only alphameric characters.
> 2. Its first character is specifically alphabetic."

Fifteen spaced names taken from MCP's pp.2-3 and p.14, with blanks
removed: `XIPLBS` `XBSEND` `XBEGIN` `XWSR` `XCLIND` `XCLSTO`
`XVERFY` `XSROOF` `XLOOP` `XIPLK` `XERRAD` `XERROR` `XWIND`
`XBUFER` `XPROSA`.

**All fifteen are legal. Eight are exactly six characters — the
maximum.** As printed, every one of the fifteen exceeds six and would
be illegal. A name space used right up to its limit, with the
overflow all being blanks, is not a coincidence.

**So STRAP ignores embedded blanks in symbols, and the transcription
writes `XIPLBS`.** Recorded as an INFERENCE: p.10 states the length
and character rules and does **not** say blanks are ignored. What
makes it safe to act on is that the alternative — spaces being
significant — contradicts the stated six-character rule fifteen times
out of fifteen, and that `listing_oracle.py` will catch it anyway,
since a wrong symbol gives a wrong address and the printed machine
code will not match.

**M3 IS THEREFORE NOT BLOCKED ON THIS.** The remaining STRAP-II gaps
from `mcp_tape_manufacture.md` §4 stand — `TAIL` with multi-level
scoping, `CW(CR)`/`CW(CDSC)`, `XW`/`VF`, the `(A*)`/`(CC*)`/`(IQS*)`
DD prefixes — and those are real. This one is not among them.

## 5u. FULL SUITE GREEN AT 395/395, AND ONE M3 ASSEMBLER GAP CLOSED

**2026-10-17: 395 of 395 sections, 0 `FAIL` lines, 0 bsc errors,
"All regression tests passed."** This is the first full-suite run
since 2026-10-16's and it validates everything between: the
request/response tape source, chaining and its test, the SEOP status
bit, the IPL mechanism, the 24-bit widening, the interval timer and
time clock, the COMPOOL, and `mktape.py`.

Section count checked against `grep -c '^run '`, not taken from the
summary line — this file's own trap about a splice that silently
removed 3,266 lines and still reported 40 sections passing.

### STRAP-II LISTING CONTROL, parsed and discarded

`strap_asm.py` gains `LISTING_CONTROL`: `PUNFUL`, `PUNORG`, `PUNID`,
`PRNS`, `PRNID`, `RESEQ`, `SEM`. These control the printout and the
punched cards — no storage, no symbol, no location-counter movement —
so discarding them cannot change an assembled bit. **MCP's printed
p.2 opens with five of them before its first instruction**, so its
pages would not parse at all without this.

Regression: **246 of 246 programs still assemble, and 186 of 186
listing oracles still pass.** The oracles are the real check, since
they compare assembled bits against IBM's own printed machine code.

**`TAIL` IS DELIBERATELY NOT IN THE SET.** MCP uses `TAIL,(2)G` and
it is multi-level symbol scoping, not listing control. Discarding it
would change which definition a symbol resolves to — **wrong
addresses that still assemble cleanly**, which is the exact failure
this project's method exists to catch. It stays an error until
implemented, and the source says so where someone would otherwise add
it to the list.

### WHAT M3 STILL WAITS ON — now a short, specific list

1. **`TAIL` scoping.** Real symbol-table work.
2. ~~`CW(CR)` / `CW(CDSC)`~~ **DONE — see §5v.**
3. **The `(A*)` / `(CC*)` / `(IQS*)` DD prefixes.**

`XW` and `VF` turned out to be implemented already, and §5t removed
the spaced-symbol worry. The gap is smaller than
`mcp_tape_manufacture.md` §4 estimated.

## 5v. `CW` IS IMPLEMENTED — the manual had it, and the flags were never an octal field

2026-10-17. §5u listed `CW(CR)`/`CW(CDSC)` as needing `C28-6129` and
declared it blocked. `C28-6129` is in `docs/`. Reading it took
minutes and settled everything.

**C28-6129 printed p.14 (PDF 18; this document runs printed + 4),
section 8:**

> `CW(OP), ADDRESS, COUNT, CHAIN ADDRESS`
> "The quantity represented by the symbol ADDRESS is compiled in the
> first 18 bits of the full word created. COUNT is compiled in bits
> 28-45 and CHAIN ADDRESS is compiled in 46-63."
> "In a control word the flag bits (bits 25-27) are the chain flag,
> the multiple flag and the skip flag, **in that order**."

plus a table of all eight secondary mnemonics with their three bits,
now `CW_SECONDARY` in `strap_asm.py` verbatim: `CR` `CCR` `CD`
`CDSC` `SCR` `SCCR` `SCD` `SCDSC`.

**THE FLAGS FIELD WAS NEVER AN OCTAL FIELD.** §5u could not map
`110` onto chain/multiple/skip because it read those three characters
as a nine-bit octal number. They are **three one-bit digits, one per
flag.** `110` is chain 1, multiple 1, skip 0 — exactly `CDSC` in the
manual's table. The thing that looked undecodable was a format
assumption, not a gap in the sources.

### AND A SILENT WRONG ANSWER THAT ONE ORACLE WOULD HAVE MISSED

The first implementation shifted the chain address `>> 6`
unconditionally, the way `XW`'s refill does. `CDSC` matched; `CR`
produced `000000` where the listing prints `000001`, with no error.

C22-6531 printed p.12 — **a page this project had already rendered,
for the A18 truncation rules** — states the rule:

> "Note: An **integer** in an 18-bit field counts full words or unit
> address, control operation, **control word address**, and so on."

So a bare integer is already in word units and goes in as written,
while a bit-address expression must be converted. **MCP uses both
forms for the same field within twelve pages**: `1` on printed p.2,
`$+1.0` on printed p.14. `_is_bit_address` in `strap_asm.py` now
decides per operand.

**Having two printed control words is what caught it.** Either one
alone passes under the wrong rule. That is the second time today a
wrong answer passed one oracle and failed another, and both times the
pair existed only because the listing prints its own expected result
beside the source.

Regression: **246 of 246 programs assemble, 186 of 186 oracles pass.**

### M3's REMAINING GAPS

1. **`TAIL`** — **specified now, see §5x, and it is suffix mangling
   rather than scoping. Likely inert for a single-program assembly.**
2. **The `(A*)` / `(CC*)` / `(IQS*)` DD prefixes** — **specified now,
   see §5w, and probably not a blocker for the bootstrap at all.**

## 5w. THE DD ENTRY-MODE PREFIXES ARE FULLY SPECIFIED, and probably not an M3 blocker

C28-6129 printed p.16 (PDF 20), read 2026-10-17.

**THE `*` IS A DELIMITER DECLARATION, which is the part that made the
syntax look strange:**

> "**The second character in the entry mode field is known as the
> end-of-statement character.** Its presence instructs STRAP to
> perform the desired conversion until this character is reached in
> the message. The end-of-statement character may be any legal card
> code character except `)`, `'` (8-4), `;` (11-0), and blank. **This
> character is not compiled.** Blanks that appear in the message are
> retained, and converted and stored correctly."

So `(A*)` is "A entry mode, message ends at `*`", and MCP's
`(A*)DD(BU,32,8),C911*` is the four-character message `C911`. The
manual's own example is `(AQ)DD(BU, 60, 6), DONT PANIC Q`.

**ALL FOUR MODES, from the same page:**

| mode | character set | converted to |
|---|---|---|
| `A` | standard IBM **BCD** | 6-bit IBM tape BCD; byte size 8 adds two leading zeros |
| `IQS` | 7030 console typewriter / Inquiry Station | **8-bit** binary equivalents |
| `P` | **ECS 120**, the 120-member extended set | 8-bit equivalents |
| `CC` | IBM **card code** | **12-bit** bytes, "each byte reflects the multiple punch actually read in the appropriate card column" |

That last one explains MCP's `(CC*)DD(BU,,12)` — byte size **12**,
which is card code exactly, and which p.16 says is legal here even
though "the byte size in a 7030 statement may range from 1 through 8
because the byte size field is restricted to 3 bits".

### WHY THIS PROBABLY DOES NOT BLOCK THE BOOTSTRAP

MCP's printed p.2 uses them exactly twice, on **lines 4 and 5**, and
`SLC,(8)40.0` — which sets where the bootstrap assembles — is on
**line 15**. So both uses sit *before* the location counter is
positioned, under `PUNFUL`/`PUNORG`/`PUNID`: they are the punched-card
header and identification images, not the IPL image the tape carries.
**Worth confirming against pp.3-13 before relying on it**, but if it
holds, M3's transcription can skip them.

### WHAT IMPLEMENTING THEM WOULD ACTUALLY COST

Four character-set tables — BCD, IQS 8-bit, ECS 120, card code
12-bit.

**CORRECTED 2026-10-17, and the guess here was wrong twice over.**
This paragraph used to say the TOC puts Appendix C at printed
pp.47-53, "which is almost certainly where they are". Printed
pp.47-53 *is* Appendix C, but Appendix C is **"SYMBOLIC DESCRIPTIONS
AND MNEMONICS FOR IBM 7030"** — an instruction-mnemonic appendix with
**no character table on any of its seven pages**. Nor is there one
anywhere else in C28-6129: Appendix A is STRAP-II mnemonics (printed
43-45), B the pseudo-operations (46), D the error messages (54-55),
and E exists only in the bound-in Technical Newsletter N28-1081,
whose twenty pages are errata. The hedge "almost certainly" was
carrying a page range that had been read only from a table of
contents.

**THE TABLES ARE IN THE REFERENCE MANUAL, printed p.166 = PDF 169**,
on a page headed **"Character Codes"**, read first-hand at 150 dpi.
Four grids, captioned below each: *49 Character Set*, *89 Character
Set*, *48 Character Set*, *120 Character Set*. **The manual prints no
numbers at all** — columns are labelled `BITS 0-1-2-3` (0000…0111)
and rows `BITS 4-5-6-7` (0000…1111), so a code is
`(column << 4) | row` and any octal is the reader's own.

Spot-checked against canonical IBM BCD in the 48-character grid:
`A` at column 0011 row 0001 = 0o61, `J` at 0010/0001 = 0o41, `S` at
0001/0010 = 0o22, `0` at 0000/1010 = 0o12. All four canonical.

**AND THE TRAILING `*` IS NOT PART OF THE MODE NAME.** C28-6129
printed p.16 says it outright:

> "The second character in the entry mode field is known as the
> end-of-statement character. Its presence instructs STRAP to perform
> the desired conversion until this character is reached in the
> message. The end-of-statement character may be any legal card code
> character except `)`, `'` (8-4), `;` (11-0), and blank. **This
> character is not compiled.**"

So `(A*)`, `(CC*)` and `(IQS*)` are modes A, CC and IQS each
terminated by `*`, and **`(IQSX)` is mode IQS terminated by `X`** —
nothing is missing from it. The implementation trap that follows:
an `(IQSX)` message cannot contain a literal `X`, and an `(A*)`
message cannot contain a literal `*`.

Two more from the same page: `(N)` is not an entry mode at all but
the floating-point *normalized* use mode; and byte size 12 is legal
**only in a `DD`** — "in a DD statement, the byte size of converted
characters may range from one through 12 … However, the byte size in
a 7030 statement may range from 1 through 8 because the byte size
field is restricted to 3 bits" — which is what makes MCP's
`(CC*)DD(BU,,12)` legal. C28-6129 printed p.24 says there are "only
two entry modes" of this kind, A and IQS; **the newsletter corrects
that to three**, adding CC.

**~~STILL MISSING: the 12-bit card code `(CC*)` uses.~~ FOUND,
2026-10-21, in the last of the three candidates this note listed.**
`C22-6678-1` **printed p.56 = PDF p.56, "APPENDIX F. CHARACTER
CODES"**, tabulates it directly: four columns, *Character | IQS | BCD
| Punches*, with the header "The following table lists the octal
codes, by character, for eight-bit IQS, six-bit BCD, and **the
corresponding column binary punches**."

The original note said what was wanted was "a documented bit order,
not a lookup table", and both halves are now in hand from two
different manuals — the bit order from Reference Manual printed p.138
("Column 1, Row 12 / Column 1, Row 11 / Column 1, Row 0 / to / Column
1, Row 9 / Column 2, Row 12"), the lookup table from Appendix F.
Together they give the 12-bit value for any character.

**AND THE DERIVATION IT REPLACED WAS WRONG IN THREE PLACES** — see
`strap/cards.py` and `tests/verify_c22_6678_appendix_f.py`. The grid
derivation agrees on 48 of 52 rows and misses exactly the punctuation
where the 7030's 48-character set and the conventional commercial
code disagree: `'` and `,` have each other's punches, `;` is 11-0 and
was not in the grid at all, and `:` has an IQS code with a **blank**
Punches column — no card representation. The derivation was justified
on the grounds that the card code "belongs to the CARD and the
keypunch, not to the computer", which was true of the letters and
digits and false of exactly the characters where it mattered.

**THE LESSON IS SHARPER THAN "NOBODY OPENED IT", because somebody
did.** `C22-6678-1` is one of the most-cited documents in this
project — `disk_subsystem.md` and `exchange_and_io.md` quote its
printed pp.6, 8, 9, 29, 32, 40 and 43, and `boot_plan.md` items A3
and A5 both rest on it. The file was opened repeatedly, over weeks,
and **its last appendix was never turned to** while a note three
thousand lines up this file listed it as an unchecked candidate for
exactly the thing that appendix contains.

So the rule is not "read the unread documents". It is **"a document
you have cited is not a document you have read"** — and when a note
says a fact is missing, the cheapest possible move is to check the
back of the manuals already in hand, appendix by appendix, before
deriving anything. Both searches that found something today found it
in files `docs/` already had.

**AND A PAGE-OFFSET CORRECTION FOR C28-6129**: its body is printed =
PDF − 4 (PDF 16 → printed 12, PDF 28 → printed 24) but its
appendices are printed = PDF − 3 (PDF 49 → printed 46, PDF 56 →
printed 53). A leaf is dropped somewhere in printed 25-42. The
Reference Manual is a consistent +3.

## 5x. `TAIL` IS SUFFIX MANGLING, NOT SCOPING — and probably inert for one program

C28-6129 printed p.37 (PDF 41), read 2026-10-17. This was the last
item on M3's gap list and the one called "the only one needing design
rather than transcription". **That description was wrong**, and it
came from a summary rather than the page.

> **TAIL, ANYSYMBOL**
> "Difficulty with multiply-defined symbols can arise when two
> programs, written by different people at different locations, are
> assembled together. By appending a unique programmer symbol **as a
> tail to every symbol** in his program, a programmer can be assured
> that each of his symbols will be uniquely defined, regardless of
> what other programs are assembled with his program."
>
> "The pseudo operation TAIL **appends the symbol that appears in its
> address field as a tail to every symbol in the statements that
> follow** the tail statement until another tail statement, or an
> untail statement, is given."

So it is **name mangling for cross-program link safety**, not lexical
scoping. `TAIL, (n)DOG` assigns a tail at level *n*; STRAP-II permits
**ten levels**, and 256 distinct tail symbols per program. MCP's
`TAIL,(2)G` sets tail `G` at level 2.

### THE CONSEQUENCE THAT MATTERS FOR M3

**If every symbol in a block gets the same suffix, a single-program
assembly is unchanged.** Definitions and references are mangled
alike, so `XIPLBS` becomes `XIPLBSG` everywhere and the object code
is bit-identical. Tailing only has an observable effect when
**separately-written programs are assembled together** — which is
exactly the problem the manual says it exists to solve.

MCP's `TAIL,(2)G` is on printed p.2 **line 10**, before any code
(`SLC,(8)40.0` is line 15), so the whole bootstrap sits inside one
tail block.

**THE CONDITION TO CHECK BEFORE RELYING ON THIS**, and it is the only
way it can bite: a reference *inside* the tailed block to a symbol
defined *outside* it would be mangled while its definition was not,
and would fail to resolve. For a self-contained bootstrap assembled
alone there is nothing outside. **Verify that pp.3-13 define every
symbol they use** before treating `TAIL` as inert.

### SO THE REMAINING WORK IS SMALLER THAN THE LIST SAID

Implementing `TAIL` properly is a name-mangling pass — append active
tails to the name field and to every symbol token in operand
expressions — and it is only *needed* for multi-program assembly,
which this project does not yet do. **It is not a prerequisite for
transcribing MCP's bootstrap.** When it is implemented, note that
none of the 246 existing programs use `TAIL`, so mangling only when a
tail is active cannot disturb them.

**THE PATTERN, THREE FOR THREE TODAY.** `CW`, the DD entry-mode
prefixes, and now `TAIL` were each recorded as blocked on a document
that was already in `docs/`. Each took minutes to settle and each
turned out smaller than its summary. **"This needs document X" is
only true once document X has been opened.**

## 5y. MCP's PAGE 2 IS TRANSCRIBED — 15 of 16 rows bit-exact, and the 16th is a real find

2026-10-17, `boot_plan.md` M3's first page.
`decks/mcp_bootstrap_p2.strap` +
`tests/verify_mcp_bootstrap_p2.py`. **The first page of IBM's
operating system in this corpus.**

**All six symbols the page defines land exactly where its LOCATION
column prints them** — `XIPLBS` 000041.00, `XVERFY` 000043.00,
`XBEGIN` 000043.40, `XLOOP` 000044.40, `XCLIND` 000046.40, `XCLSTO`
000050.40 — and **fifteen of the sixteen rows carrying machine code
match character for character**, including the IPL control word, the
`BD` the hardware starts at, the `XW` disk-control-word slot, and the
full-word `L(BU)`.

### THE ORACLE EARNED ITS KEEP TWICE BEFORE THE REAL FIND

- **`listing_oracle.render()` could not print an index or control
  word.** The listing uses four groups — `vvvvvv.vv+ fff cccccc
  rrrrrr` — where `render` saw four tokens and emitted two
  half-words. Now handled, and **one renderer serves both `XW` and
  `CW`**: `CW`'s ADDRESS is only 18 bits with the status bits zero
  beneath it, but an 18-bit address in bits 0-17 *is* `addr << 6`
  read as 24 bits, so printing bits 0-23 as word.bit gives the
  address and `.00` either way.
- **`CW`'s COUNT field needed the integer-vs-bit-address rule too**,
  which §5v applied only to the two address fields. p.2 writes
  `X BS END-X IPL BS`, a difference of two bit addresses needing
  conversion; p.14 writes the plain integer `513`. The count came
  out **eight times too large** — `0o56000` against `0o560` — and
  nothing else moved. **Third field, same rule, caught only because
  MCP writes it both ways.**

### THE ONE FAILURE, AND IT IS NOT A TYPO

**RESOLVED — THE PAGE IS 16/16 AND THE CAUSE WAS TWO GLYPHS.**

**First: `M+1`, digit one, not `M+I`.** At 600 dpi the character has
a digit's angled top flag and matches the `1` in `$+1.0` two rows
below, while the `I` in `IND` *on the same row* carries serifs. This
is `listing_typography.md`'s letter-I/digit-1 trap **in reverse** —
that file exists because this corpus kept misreading leading `I` as
`1`. Read as `M+I` the operand becomes an immediate datum, and
`encode_vfl_immediate` correctly left-justifies it per RefMan p.56
(`(2483 & 0x3F) << 18` = `0o630000`), which is exactly the wrong word
the first attempt produced. **The assembler was right; the reading
was wrong.**

**Second: the trailing byte is `B0`, not `80`.** It read as `80` at
200 dpi **and at 600 dpi**; only at **900 dpi** does the flat left
stem of the `B` separate from the bowls. With `B0` the row matches
exactly and the page is complete. Written up as
`docs/listing_typography.md` §11, because §2's "render at 600 dpi"
rule was followed here and was not sufficient.

**THE POCKET CARD WOULD HAVE CAUGHT IT WITHOUT RE-RENDERING, and it
was in `docs/` the whole time.** `X22-6533_7030_PocketCard.pdf` — the
very card `opcodes.py` cites — tabulates every operation code, and
gives **`M+1  Add One to Memory  abc101011`** together with the
modifier rule (`a=1` data unsigned, `b=0` same sign, `c=0` binary),
so `BU` yields the nine-bit field `100101011`. The misread `80`
decoded to `100101000`, and **no code on that card ends in `000`** —
every integer and radix entry ends in `1`. An opcode absent from the
card is a misread byte until proven otherwise.

That is the **fourth** time in two days a question was recorded as
blocked on a document already sitting in `docs/`.

**`verify_mcp_bootstrap_p2.py` IS NOW IN `run_tests.sh`** (396 ->
397), which it earned by passing rather than by being weakened. It
was held out while it failed, and the holding-out is what kept line
34 visible long enough to be solved.

## 5z. A CROP HELPER FOR THE REMAINING MCP PAGES

`strap/mcp_crop.sh`, 2026-10-17. Printed p.2 was transcribed by
working out the page geometry by hand, twice, and the second time
produced a misread hex byte that took three commits to run down.
Twelve pages remain in the bootstrap alone.

```
./mcp_crop.sh PRINTED_PAGE  loc|code|stmt  1|2|3  [DPI]
```

**It encodes three things learned the expensive way:**

- **900 dpi for the `code` column, 600 for the others.** The default
  switches on the column. `listing_typography.md` §11: the trailing
  hex byte read as `80` at 200 dpi **and at 600** where the page
  prints `B0`. The octal columns have no letters and do not need it.
- **PDF page = printed + 7 for the bootstrap**, applied
  automatically — and the script prints `CONFIRM the page's own
  'PAGE NUMBER' header matches`, because the offset is **not**
  constant across this listing (vol. 1 duplicates pp.1-2 and carries
  three blanks).
- **The column x-offsets are stated at 600 dpi and scaled**, with a
  comment saying so. The first version wrote 900-dpi numbers and
  scaled them as if they were 600-dpi, which silently rendered the
  *statement* column when asked for the *code* column — a wrong
  answer that looks like a right one, since both are columns of text.

### THE CHEAP CHECK THAT WOULD HAVE CAUGHT THE BYTE

Worth repeating here because it generalises past this page: **a
misread byte in the opcode position is an opcode that does not
exist.** `X22-6533_7030_PocketCard.pdf` is in `docs/` and tabulates
every operation code. The misread `80` decoded to `100101000`, and
no integer-arithmetic or radix-conversion entry on that card ends in
`000` — they all end in `1`. **Decode the opcode field and look it
up before re-rendering anything.**

## 6a. MCP's BOOTSTRAP USES AN INSTRUCTION THE MODEL CANNOT EXECUTE

Caught 2026-10-17 by the opcode coverage audit, on the first full
suite run after MCP's p.2 landed:

```
FAIL: M+1 now used -- remove from KNOWN_GAP.
```

**This is not bookkeeping.** `M+1` sits in the audit's
`UNIMPLEMENTED` set, whose header says *"the model reaches
`setOpInvalid` for these… Only five VFL integer arms exist (L, ST,
+, M+, K)"*. MCP's printed p.2 line 34 is
`M+1(BU,6),X CL IND+.19  -CLEAR NON MASKABLE INDIC`, bit-exact
against the listing and **the fourth instruction of IBM's operating
system**.

**So the model would set Operation Code Invalid four instructions
into the bootstrap.** `boot_plan.md` M3 wants to *run* this thing,
and this is the first hard evidence that transcribing it is not
sufficient — exactly the distinction the audit's `ENCODING_ONLY`
category was built to keep visible, now forced a fourth time and for
the first time by MCP rather than a diagnostic deck.

**FIXED THE SAME DAY.** `M+1` is now a sixth VFL integer arm beside
`L`, `ST`, `+`, `M+` and `K`. It **shares `M+`'s arm** rather than
cloning fifty lines: X22-6533 lists them adjacently (`M+ Add to
Memory abc001001`, `M+1 Add One to Memory abc101011`) and the
difference is only the addend — addressing, field handling, refill,
the DF class-3 signal and the DS protection check are identical, and
`M+`'s arm is already deck-verified. "One" is one unit of the field:
`fieldToSM` right-justifies the field in `mag`, so the addend is
`SM128{sign:0, mag:1}` with no offset shift, `offSh` existing only to
align the accumulator that `M+1` does not have.

`M+1` has therefore **left every category on the audit page**, the
way `EX` and `EXIC` did — arriving and leaving on the same day, which
makes the round trip the clearest illustration of what
`ENCODING_ONLY` is for. Pinning the encoding is what made the
execution gap visible.

### THE TEST IS BEHAVIOURAL, NOT A DECK ORACLE, AND IT CAUGHT ME

`decks/vfl_m_plus_one.strap`. MCP's rows pin `M+1`'s encoding
bit-exactly; they cannot pin its execution, because running the
bootstrap is the goal rather than a tool available now. So this is
hand-written against the pocket card's wording and is weaker than a
deck check — stated in the program header rather than left to be
assumed.

**Three of its four expectations were wrong on the first run, against
a model that was correct.** I had written them as though a VFL field
were right-justified in the word. It is not: **a field at bit address
A with length L occupies IBM bits A..A+L−1, `w[63-A : 64-A-L]`, so
the increment lands at `w[64-A-L]`.** Re-derived from that rule, all
four matched the model exactly.

**And the carry case was testing nothing.** `DD(BU,64),255` read as a
16-bit field at offset 0 reads `w[63:48]` — zero, because the 255
sits in the low bits *outside* the field. It incremented 0 to 1 and
passed for the wrong reason. Rebuilt as `DD(BU,16),255` so the field
actually contains the 255 and the carry out of the low byte is real.

That is the second test in two days that would have passed while
checking nothing — the other being the IPL harness, where
pre-loading core would have made every check pass against a dead
tape. Both were found by asking what a *broken* implementation would
produce.

**The signed case is deliberately untested.** `M+1` on a signed field
exercises the sign-byte strip and `smAdd`'s sign handling; MCP uses
`(BU,6)` and no source here states the signed interpretation.
Writing that test would mean inventing its expected value.

**AND EXPECT MORE.** Page 2 is one of thirteen. Every page
transcribed from here will re-run this audit, and each one may name
another arm. That is the audit working: a transcription that cannot
run is worth having and worth knowing about, and the category
distinguishes "pinned its encoding" from "the machine can execute
it" precisely so growth here is never mistaken for progress.

## 6b. MCP's PAGE 3 IS TRANSCRIBED — 38 of 39 rows, and the tape layout is settled

**2026-10-17.** `decks/mcp_bootstrap_p3.strap` and
`tests/verify_mcp_bootstrap_p3.py`, in the suite. Printed p.3 picks
up exactly where p.2 stops — p.2's last instruction is a half word at
`000052.00`, p.3's first is at `000052.40` — and all eighteen symbols
it defines land at its own printed LOCATION column.

**WHAT THE PAGE SETTLES, and it is not a detail.** Lines 32-52 are
headed SPACE OVER TAPE MARK and open with `SPFL(SEOP),0.0($15)`.
**The bootstrap record is followed by a tape mark**, and the
bootstrap spaces past it before touching anything else. `mktape.py`
writes no tape mark today; `boot_plan.md`'s image format has to grow
one, and the model has to be able to space over it.

The other two banners: FIND IPL CHANNEL NUMBER walks the channels
with `M+1(BU,19)` on the 19-bit field at the head of a `CCW`
instruction — the channel number sits at IBM bits 12-18 of a 24-bit
address (RefMan p.111), so bit 18 is its units digit and adding one
at the bottom of a 19-bit field **is** "ADVANCE CHANNEL" — starting
at `15.32` = 992 = 31 << 5, one below the basic exchange's first
channel. IO TEST is the status loop every I-O operation on the page
returns to: `SIC` / three indicator branches / `CCW` / `BB` on bit 24
(SEOP) / `CT0011` / `BRZ`.

**TWO ASSEMBLER ADDITIONS, both forced by the page:**

* **`SPFL`** — see item 5 above and `mcp_tape_manufacture.md`.
* **`REL` with no second operand.** RefMan p.111: RELEASE's second
  effective address is "not used; ignored". MCP writes it that way
  three times on pp.3-4 and the listing prints `000000` in the field.
  Requiring the operand would have made the historical source
  unassemblable.

**THE B/8 TRAP, A THIRD TIME, AND THE RULE THAT BEAT IT.** Line 10's
trailing byte reads `80` at 900 dpi and is `B0`. It was not caught by
looking harder: it was caught because `LVE`'s operation code is
`11011` at bits 23-27 (X22-6533 DIRECT INDEX ARITHMETIC), which
forces bits 24-27 to `1011`, so the nibble **had** to be `B` before
anyone looked. **Decode the opcode field, then look at the glyph** —
`listing_typography.md` 11 already said to re-render, and this says
what to re-render *for*.

**THE ONE ROW LEFT UNCHECKED** is line 6, `CCW,15.32,X IPL BS`: bits
24-27 print `0011` where X22-6533's INPUT-OUTPUT OPERATIONS format
puts the literal `1000`. The glyph was ruled out at 1800 dpi against
line 7's `80` in the same crop. It is the only I-O instruction found
so far whose channel operand is a plain literal rather than an
indexed `0($15)`; a sweep of printed pp.6-12 found **no other
unindexed I-O instruction at all**, so the deciding sample is still
of size one. `mcp_tape_manufacture.md` carries the full evidence.

**AND AN UNEXPLAINED LISTING MARKER**, now in
`listing_typography.md` 12: an asterisk printed after the LOCATION
value on a minority of rows, on every MCP page looked at. Eleven
first-hand instances, no shared property among the statements, and
the one surviving pattern — the line-pitch between marks grows with
the page's line count, as a mark at a fixed physical height on the
form would — does not survive comparing two pages of similar
density. It cannot move a bit, and all three of p.3's instances are
in the checked set, so transcription proceeds past it.

**Next: printed p.4**, FETCH PROSA (`RD(SEOP)`, the same status loop,
`T` to move the MCP IPL, `LVS`, `CM1111`), already rendered.

---

## 6c. MCP's PAGE 4, AND `LVS`'s ADDRESS FIELD IS NOT AN ADDRESS

**2026-10-17.** `decks/mcp_bootstrap_p4.strap` and
`tests/verify_mcp_bootstrap_p4.py`, in the suite: twelve symbols and
**all thirty-seven machine-code rows**. Printed p.4 is FETCH PROSA —
it reads one PROSA record against printed p.14's chained control-word
table, runs it through p.3's IO TEST loop, takes the record apart
with four `LX`/`SC` pairs, sums two of the counts with `LVS`, and
`T`s the MCP IPL down to `X BS END`. **The bootstrap copies the next
stage over itself**, which is why p.3's SPACE OVER TAPE MARK has to
run first. Then it releases the disk and branches to `X 10` on
printed p.15, MCP INITIALIZATION proper.

**TEN EXTERNALS, EVERY ONE FROM THE PAGE THAT DEFINES IT** — pp.2, 3,
5, 13, 14 and 15. A `SYN` taken from the row that *uses* a symbol
makes that row prove nothing, and this page references ten.

**THE PAGE PROVES THE BLANKS RULE IN IBM's OWN OUTPUT.** Line 6
writes `SIC,XERRAD`; line 8 writes `SIC,X ERR AD`. Both print
`000551.00 80`. Two spellings, one symbol — which until now was an
inference from C22-6531 p.10's six-character limit.

### `LVS` — the one instruction whose address field is a bit mask

**Reference Manual printed p.28 = PDF 31**, section "Multiple
Indexing", read at 300 dpi:

> "In multiple indexing, bits 0-15 of the address part of the
> instruction are used to indicate which index registers participate
> in the operation. When bit position n contains a one, the register
> Xn participates. When bit position n contains a zero, the register
> Xn does not participate. Bits 16-19 of the address part of the
> instruction are ignored."

> "The index field J contains the address of the index to which the
> operation LOAD VALUE WITH SUM applies. **No address modification is
> available for this operation**" — i.e. there is no `I` field, which
> is why this format's OP runs out to bit 31.

> "The address parts, bits 0-24, of the index registers which
> participate are added and replace bits 0-24 of the index word
> specified by J… If bits 0-15 of the address part of the instruction
> are all zero, the value field of the index register specified by J
> is cleared."

**THE MANUAL CONTRADICTS ITS OWN FIGURE.** The prose says bits
**16-19** are ignored. Bit 19 is the high bit of `J` in the diagram
printed four inches below it on the same page (`ADDRESS | J | OP.`,
boundaries 0, 19, 23, 31) and in X22-6533's IMMEDIATE INDEX
ARITHMETIC row. Diagram and pocket card agree against the sentence,
so **16-18** is implemented and the discrepancy is recorded in
`verify_lvs_encoding.py` rather than smoothed over. Both MCP rows
leave 16-18 zero, so nothing here turns on it.

**TWO ROWS PIN IT, NOT ONE**, and that is why
`verify_lvs_encoding.py` exists separately from the page verifiers:

```
printed p.4  line 23   000050.03 0B   LVS,$1,$12,$14       bits 12,14      -> 80
printed p.15 line 17   000150.23 0B   LVS,$9,$12,$11,$14   bits 11,12,14   -> 208
```

IBM bit *n* of a 19-bit field weighs 2^(18−n), so the assembled field
is the mask shifted left three. One row would pin the mask only at
the bits it happens to set; two with different sets pin position
against register number in five places, with `J` carrying the written
destination in both.

**AND THE ZERO/C CONFLATION, A NEW GLYPH TRAP FOR THIS SCAN.** The
byte is `0B` in both rows, and at 900 dpi it reads `CB` — this
listing prints digit zero with a visible gap at the right, so a
leading `0` looks like a `C`. The same p.4 row prints `000050.C3`
where the octal field *cannot* contain a C. **The arithmetic settles
it without the glyph**: with `CB` the operation field would be
`111001011`, which is no operation on the pocket card at all.
Together with p.3 line 10's `B0`-read-as-`80`, that is two reading
errors in two pages caught by decoding the opcode first.

**Also corrected:** `resuscitation_roadmap.md` listed `LVS` as "OCR
only — not image-verified". It now has two image-verified witnesses.

**Next: printed p.5**, the ERROR ROUTINE (`LF`, `M+MG`, `SVA`,
`BZXVZ`, `GONG(SEOP)`, `TI`, and a `CTL(SEOP),0.0($1),0.0` whose
comment calls it an "ILLEGAL IO CONTROL CODE" on purpose).

---

## 6d. `LF` IS A CONNECTIVE, AND THE ASSEMBLER ALREADY HAD IT

**2026-10-17.** Printed p.5 of MCP, the ERROR ROUTINE, opens its
address-breakup with

```
12* 000136.00   000551.00 80   025300.46 70   X1 ERR   LF(BU,21,3),X ERR AD,1
```

and `LF` is on X22-6533 page 4's VARIABLE FIELD LENGTH mnemonic list
("`LF  Load Field`") but **not** in page 2's INTEGER ARITHMETIC
opcode table. So it looked like a missing instruction.

**Decoding the word first, as `6b` says to, is what found it.** Split
by the integer-arithmetic format the word gives LENGTH 21 and BS 3,
matching the written `(BU,21,3)`, OFFSET 1 matching the written `,1`
— and then modifier bits `0, 0, 1` with operation `100111`. That is
wrong twice over: `BU` sets the first modifier bit to 1 and the third
to 0, and `100111` is no integer operation on the card. **The field
boundaries were right and the field MEANINGS were wrong.**

The Reference Manual's "Complete Operation and Modifier List",
printed p.168, splits the VFL instructions into three boxes —
INTEGER ARITHMETIC `ssbxxxxx1 iiii`, RADIX CONVERSION
`ssbxxxxx1iiii`, and **CONNECTIVE OPERATIONS `ccccxx111iiii`**. The
connective box has **no Classes and no Modifiers footer**, because
bits 51-54 are `cccc`, the connective function. Bits 51-59 of MCP's
word are `001100111`, which is the pocket card's `C` ("Connect",
`xxxx00111`) with `xxxx = 0011`.

**So `LF` is `C0011`, and `C0011` has been in this assembler all
along.** Assembled and compared:

```
C0011(BU,21,3), X ERR AD, 1   ->   000551.00 80 025300.46 70
MCP printed p.5 line 12       ->   000551.00 80 025300.46 70
```

And the semantics agree: the pocket card's CONNECTIVES table gives
function 3 the result bits `0 0 1 1` for operand combinations
`m a` = 00, 01, 10, 11, whose symbolic representation it prints as
**`m`** — the memory operand replaces the accumulator field, which is
what Load Field means. `C` sends the result to the accumulator.

**THIS IS THE "NEEDS DOCUMENT X" LESSON IN A NEW SHAPE.** Not a
document already in `docs/` this time, but an *instruction already in
the assembler under a different name*. The corollary to add: **before
implementing a mnemonic, decode one of its assembled words and look
for the bit pattern among the operations already encoded.**

`SF` (Store Field) is presumably the `CM` analogue and is
**deliberately not implemented** — no assembled `SF` has been found,
so its `cccc` would be a guess.

**Mode `P` remains unresolved.** Pocket card page 4 says the VFL
`dds` mode is "(B, BU, D, DU, P)", but RefMan printed p.56 spends all
three modifier bits on signed/unsigned, same/inverted sign and
decimal/binary, leaving no bit for a fifth mode, and
`7030_Opcode_List.pdf` lists every VFL operation under `(B)`, `(BU)`,
`(D)`, `(DU)` only. Recorded, not guessed.

**`docs/7030_Opcode_List.pdf` deserves more use** than it has had: 99
pages of *assembled words* for every operation in every mode, i.e. a
second encoding oracle independent of the diagnostic decks. It
settled this question in one page.

---

## 6e. PRINTED p.5's FIVE EXTERNALS, AND THE PDF OFFSET IS +7 FOR 113 PAGES

**2026-10-17**, found by a delegated sweep and reported with page
citations, for the printed p.5 transcription that comes next:

| symbol | defined at | printed page | the defining row |
|---|---|---|---|
| `X ERR IN` | `000245.00` | p.8 line 32 | `XW,X ERR DD,X E DD K+1.0,0` |
| `X MS CW1` | `000246.00` | p.8 line 34 | `CW,X ZEROS,3,X MSG CW(.25)1` |
| `X MSG CW` | `000247.00` | p.8 line 35 | `CW,0,10,0` |
| `X ERR CW` | `000253.00` | p.8 line 37 | `CW,0  - SLOT FOR COPIED CW` |
| `S YCOCH`  | `002156.00` | **p.37** line 25 | `VF,22.4  -THE CHANNEL NUMBER OF THE CONSOLE` |

Each was cross-checked against its own printed binary: `X ERR IN`'s
`000176` is `X ERR DD`'s location on p.7; `X MS CW1`'s `000247` is
`X MSG CW`'s; `X MSG CW`'s `000012` is octal for the `10` it writes;
`S YCOCH`'s `000026.04+` is octal 26 = 22 decimal, and the next row
is `S YPRCH VF,22.4 -THE CHANNEL NUMBER OF THE PRINTER`, which is
what makes the CO/PR in the two names legible rather than inferred.

**`S YCOCH` LOOKED LIKE A DIFFERENT DECK AND IS NOT — corrected
2026-10-17.** Printed p.37 is headed "`***** THE COMMUNICATION REGION
FOR MCP *****`", its banner reads `PUNID 11C11IPL` and its cards are
the `13000xxx` series, where the bootstrap pages read `PUNID
11E11BSP` and `11000xxx`. This was written up here, and in
`mcp_bootstrap_p5_p6.strap`, as "the first cross-deck reference this
project has had to resolve", with a nod to `TAIL`.

**Printed p.15 line 5 settles it the other way**, read first-hand at
600 dpi:

```
 5*                      PUNID,11C11IPL
 6*                      RESEQ
 7* 000621.00            SLC,X BS END
```

`PUNID` and `RESEQ` change the identification and sequence **punched
into the cards**; neither ends an assembly. So printed pp.3-15 and
pp.16 onward are **one STRAP assembly punching two decks** — which is
exactly why line 7 can `SLC` to a symbol defined on printed p.14, and
why p.5 can name one defined on p.37. **Nothing here needs `TAIL`.**

The same structure explains printed p.13's `X BUFER SYN,X IN END+
2000.0`: `X IN END` is defined on **printed p.98 line 36**, `SYN,$`
at `005466.00`, eighty-five pages later and still the same assembly.
And `2000.0` is **decimal** — `0o11406` − `0o5466` = 4870 − 2870 =
2000 exactly, where an octal reading would need `0o3720`.
Corroborated independently by printed p.15 line 15, `X IN
BE,X IN END-X IN` at `000621.00` with address field `004645`:
`0o621 + 0o4645 = 0o5466`.

**The general rule this turned up, which the oracle needs:** on a
`SYN` row the LOCATION column prints the **resolved symbol value**,
not the assembly location counter. That is why `X BUFER` prints
`011406.00+` on a page whose counter is running `000526`-`000551`.

**AND A PAGE-OFFSET RESULT WORTH KEEPING**, since the offsets differ
per document and this one was known only for pp.2-15: the MCP
listing's **+7 holds unbroken from printed p.1 (PDF 8) to printed
p.113 (PDF 120)**, established by reading the header band of every
PDF page in that range rather than by sampling. The LOCATION column
restarts at a new origin at printed pp.63 (`000000`), 105 (`000014`)
and 111 (`215050`), which is how a symbol's page can be found by
bisection on its octal address.

---

## 6f. MCP's PAGES 5 AND 6 — the ERROR ROUTINE, 53 of 53, first attempt

**2026-10-17.** `decks/mcp_bootstrap_p5_p6.strap` and
`tests/verify_mcp_bootstrap_p5_p6.py`, in the suite: fourteen labels
and **all fifty-three machine-code rows**, matched on the first run
of the draft.

**TWO PAGES IN ONE FILE, AND THE REASON IS EVIDENCE.** They are
mutually recursive — p.5 branches to `X 1B ERR` and `X 1D ERR`, which
p.6 defines, and p.6 branches to `X 1A ERR` and `X6 ERR`, which p.5
defines. Transcribed separately, each file would have to `SYN` the
other's labels **from the very rows being checked**, and a `SYN` is
an input to a check rather than a witness. Together, every label is
placed by the assembler from the instruction stream. p.6 is only
twelve lines long; p.5 ends at `000166.40` and p.6 begins at
`000167.40`.

**WHAT THE ROUTINE DOES.** Every `B,X ERROR` on printed pp.2–4 lands
here. It looks the failing address up in `X ERR DD` with a
`KV`/`BXE`/`CB+` loop (and halts on `BD,$` — "IPL CONTAMINATED" — if
the table runs out), builds a console message with `LF` and two
`M+MG`s, and then **hunts for a console**: if the communication
region holds no console channel, it walks all 32 channels of the
basic exchange from `(8)20.0`, issuing a **deliberately invalid
`CTL`** ("ILLEGAL IO CONTROL CODE") to find out which channels answer
at all, a `LOC` to find out which are tape, and a `GONG` to find the
console. Then it writes the message and rings the gong. `TI` puts
the error address in the CE console's lights.

**ONE NEW MNEMONIC, ONE THAT ONLY LOOKED NEW.** `GONG` went in to
`SPFL`'s two-source standard (§6e, and `exchange_and_io.md` now has
the console's table). `LF` is `C0011` and needed nothing — §6d.

**THE BLANKS RULE, DEMONSTRATED FOUR WAYS IN EIGHT ROWS.** The same
symbol is printed `X 1D ERR` (p.5 line 25), `X1DERR` (line 31),
`X 1D ERR` (line 34) and `X1D ERR` (p.6 line 12's NAME). Likewise
`X6 ERR` / `X6ERR` / `X 6 ERR`, and `X 1B ERR` / `X1B ERR`. Page 4
had already proved it with two spellings assembling identically;
these pages make it unmistakable.

**A SMALL FIND IN THE PAGE HEADERS.** p.6's banner carries a trailing
`LOCATION 000167` field — the location of its first row. It is **not
printed on every page**: rendered side by side, printed pp.3, 4, 5
and 7 leave it blank while p.6 shows `000167` and p.8 shows `000230`.
Usable for coarse bisection to find a symbol's page by octal address,
but the page you land on may be a blank one. What decides whether it
prints was not established.

### And the coverage ratchet fired: `LOCSEOP` is now encoded

`audit_opcode_coverage.py` failed the first run with
`FAIL: LOCSEOP now used -- remove from KNOWN_GAP`, which is the
audit doing exactly what it is for. `LOCSEOP` moved from
`UNIMPLEMENTED` to `ENCODING_ONLY`, the same round trip `M+1` made
on 2026-10-17 and `EX`/`EXIC` made before it.

**It matters more than a bookkeeping move.** The ERROR ROUTINE does
not know which channel the console is on, so it asks every channel
what it is: an invalid `CTL` to see which answer at all, then
`LOC(SEOP)` to see which are **tape**, then `GONG` to find the
console. So LOCATE is not an exotic instruction MCP happens to touch
— **it is how the operating system identifies a device** — and
`StretchExecute.bsv:3376` sets Operation Code Invalid on it,
explicitly. Item 5 above has had `LOC` on its list all along; this is
the listing witness it was missing.

**AND NOTE WHAT THAT AUDIT CANNOT SEE.** `SPFL` and `GONG` are not
opcodes — they assemble to `CTLSEOP` with control codes 077 and 177 —
so a CONTROL FUNCTION the model rejects never reaches
`audit_opcode_coverage.py` at all. The bootstrap already uses both.
The gap is real and that page is the wrong instrument for it;
`mcp_tape_manufacture.md` carries the control-function table.

**Next: printed pp.7 and 8, together**, and the reason is the same
one that joined pp.5 and 6.

I had written here that p.7 would be the page where C28-6129
Appendix C's character tables stop being optional. **Rendering it
shows that is wrong, and the correction is worth keeping.** A
delegated page sweep had characterised printed pp.6–12 collectively
as "`VF`, `DD(BU,…)`, `(IQS*)DD(BU,…)`, `SYN`, `CNOP`, `XW`, `CW`,
`DR`, `LR`" — accurate for the range and misleading for the page.
Printed p.7 is **fifty-five rows of nothing but `VF`**: it is
`X ERR DD`, the error table itself, a flat array of pairs

```
 2* 000176.00  000055.40+  X ERR DD  VF,X ERR 00+1.0
 3* 000176.40  000254.00+            VF,X MSG 00  -EKJ ON CCW OF IPL CW
 4* 000177.00  000060.40+            VF,X ERR 01+1.0
 5* 000177.40  000260.00+            VF,X MSG 01  -EKJ DETECTED IN IO TEST ROUTINE
```

— the address `X ERR AD` will hold, paired with the message to print
for it. (`+1.0` because `SIC` and its branch are one 64-bit
instruction, so the instruction after the pair is one word on.) **A
page characterised at the range level is not a page read.**

**p.7 needs p.8** because the table names error sites that p.3 and
p.4 label differently: `X ERR 06 + 1.0` resolves to `000106.00`, so
`X ERR 06` is `000105.00` — which printed p.4 line 6 labels
`X9 A 1`. The equivalence is on printed p.8, whose line 38 heads a
block "`-ERROR CODE ADDRESS EQIVALENCIES`" (the listing's own
spelling). So the two pages are one unit, exactly as pp.5 and 6
were.

**AND RENDERING p.8 REORDERS THE WORK AGAIN.** p.8 carries the rest
of the table (`X ERR 18`–`29`), the definitions `X ERR IN`,
`X MS CW1`, `X MSG CW`, `X LR`, `X ERR CW`, and then the
equivalences block:

```
39* 000057.40+   X ERR 01  SYN,X7 1
41* 000105.00+   X ERR 06  SYN,X9 A 1
42* 000630.00+   X ERR 11  SYN,X10 5
47* 001613.00+   X ERR 28  SYN,X323A
```

Nine of them, and only the first two name labels inside the pages
transcribed so far — `X7 1` is p.3 line 17 and `X9 A 1` is p.4 line
6, both at the printed addresses. The rest (`X IO AA`, `X10 5`,
`X13 5`, `X22 3`, `X23 4`, `X32 2`, `X323A`) live past the
bootstrap. **And every `VF` on both pages references an `X MSG nn`,
which is a label on the message text of printed pp.9–12.**

So the dependency runs the other way from how it looked:

> **character tables → printed pp.9–12 (the messages) → printed
> pp.7–8 (the table that points at them).**

### But rendering p.9 changes what "character tables" has to mean

**THE LISTING DOES NOT PRINT THE ASSEMBLED BYTES OF AN `(IQS*)DD`
ROW.** Printed p.9's BINARY OUTPUT column is blank on every message
line. A message is six rows and only three of them print anything:

```
 6* 000254.00+  +00000000  NULL   X MSG 00  SYN,$
 7* 000254.00              375              DD(BU,8),(2)1111 1101  -CONTROL CODE * CARRIAGE RETURN
 8* 000254.10              002              DD(BU,8),(2)00000010   -RED$
 9* 000254.20                               (IQS*)DD(BU,64,8),000000.0*  -SLOT FOR ERROR ADDRESS
10* 000255.20                               (IQS*)DD(BU,64,8), EKJ ON CCW OF IPL CW*
11* 000257.70              376              DD(BU,8),(2)1111 1110  -CONTROL CODE * END OF MESSAGE
```

**So rule 3 cannot check a single character code**, and no
transcription of these pages ever will. What it CAN check, and
checks tightly, is the LOCATION COUNTER — eight bits per character,
terminator not compiled:

* line 9 → line 10 is `000255.20 − 000254.20` = 64 bits = 8
  characters, and `000000.0` is eight characters.
* line 10 → line 11 is `000257.70 − 000255.20` = 168 bits = 21
  characters, and `" EKJ ON CCW OF IPL CW"` is twenty-one, counting
  the leading blank and not the `*`.

That is a real and fairly sharp check — it catches a dropped or
doubled character anywhere in thirty messages — but it is a check on
**counting**, not on the code table. The table itself rests on
Reference Manual printed p.166 alone, and **the transcription must
say so in as many words**, the way `mcp_bootstrap_p2.strap`'s
substitution (4) already does for one row.

A smaller thing the same rows need: `listing_oracle.render` has
print shapes for a 22-octal-digit word and an 11-digit half-word but
not for an **8-bit `DD`, which prints as three octal digits**
(`375`, `002`, `376`). Three lines of work, and the control-code
rows are a third of the checkable output on these pages.

Doing pp.7–8 first would mean SYN-ing thirty message labels out of
the rows being checked, which is the mistake pp.5-6 were merged to
avoid. **Printed pp.9–12 are the next unit**, and C28-6129 Appendix
C is on the critical path after all — just one step further out than
this note first said.

Two smaller things p.8 shows that the assembler has not met:
`DR(BU,64),(3)` (Data Reservation with an array dimension, §5w's
list) and a control-word operand written `X MSG CW(.25)1`, a
bit-field designation inside a `CW` field.

---

## 6g. MCP's PAGES 9-12 — the error messages, and a check that is honest about its limits

**2026-10-17.** `decks/mcp_bootstrap_p9_p12.strap` and
`tests/verify_mcp_bootstrap_p9_p12.py`, in the suite: **thirty-one
message blocks, thirty-six labels, one hundred and ten printed
rows.** Four pages in one file because the page breaks fall *inside*
messages — `X MS 05B`'s control code is the last row of p.9 and its
text the second row of p.10, and `X MSG 10` and `X MSG 17` are split
the same way.

### What a pass means, and what it does not

**THE LISTING PRINTS NOTHING IN THE BINARY OUTPUT COLUMN FOR AN
`(IQS*)DD` ROW.** So no character code is checked here and none can
be from this listing. `strap/charsets.py`'s IQS table rests on
Reference Manual printed p.166 alone.

**What is checked is the counting, thirty-one times.** A converted
`DD` steps the location counter eight bits per character with the
end-of-statement character not compiled, so the next printed location
is an exact statement about the message's length. Every text was
read off the page and then its length compared with the listing's own
address delta; all thirty-one agreed, as did the eight-character
width of all thirty-one address slots.

**That is what fixes the trailing blanks**, and nothing else would:
`" EKJ ON CCW OF IPL CW"` has none and `" CBJ DETECTED IN IO TEST
ROUTINE "` has one. A drum printer's output cannot be stared at hard
enough to settle that; the page's own arithmetic settles it.

**And the check is not vacuous**: injecting one extra character into
the first message moves `X MSG 01` from `000260.00` to `000261.00`
and the verifier fails. That was run.

### Four things the assembler learned, each forced by a row

* **Entry modes.** `(IQS*)DD(BU,64,8), TEXT*` is a parenthesised
  prefix *in front of* the op — nothing else in the grammar starts a
  statement with `(`. Its datum is **not split on commas** (MCP
  writes commas inside one, printed p.2 line 4) and blanks in it are
  characters, eight bits each. C28-6129 printed p.16: the last
  character of the prefix is the programmer's **end-of-statement
  character** and "is not compiled", so `(IQSX)` is mode IQS
  terminated by `X`, not a fifth mode.
* **`strap/charsets.py`** — the 48 and 89 Character Sets off
  Reference Manual printed p.166, transcribed twice independently
  (once delegated at 600 dpi, once here from the cell positions) and
  agreeing on all 49 entries of the 48 set and sixteen spot checks of
  the 89 set.
* **Blanks inside a radix literal are grouping**, not separators. The
  control codes are written `(2)1111 1101` and print as `375`.
* **`CNOP` pads to the next HALF word with zeros before laying down a
  NOP.** Printed p.9 line 39's eight-bit code ends at `000307.20` and
  line 40's NOP prints at `000307.40` — the only filling that puts
  the NOP in the *second* half word. The zero fill itself is not
  printed anywhere, so it is an inference from the NOP's position and
  is labelled as one in the code.

`listing_oracle.render` also gained the **8-bit `DD` print shape**,
three octal digits, which is a third of the checkable output on these
pages.

### Two things the pages say about MCP itself

* **Five messages carry more than one label.** `X MSG 15`, `X MSG
  16`, `X MS 16A` and `X MS 16B` are four names for one text, and
  `X MSG 20`/`X MS 21A` and `X MSG 21`/`X MSG 23` are pairs. The
  listing is saying that several distinct failures print the same
  thing.
* **`X MSG 25` is deliberately not word-aligned**, at `000513.30`.
  Everywhere else the deck writes end-of-message code, `CNOP`, then
  the next `SYN`; printed p.12 lines 42-44 write the `SYN` *before*
  the `CNOP`, so the label points at the trailing edge of the
  previous message. Writing it the usual way would have put it at
  `000514.00`.

**Next: printed p.13**, which carries `X MSG 27`, `28` and `29` at
its top and then BOOTSTRAP DEFINITIONS — and after that pp.7-8, the
error table, which can finally cite these thirty-six labels from the
pages that define them.

---

## 6h. MCP's PAGE 13 — the page the whole transcription has been SYN-ing

**2026-10-17.** `decks/mcp_bootstrap_p13.strap` and
`tests/verify_mcp_bootstrap_p13.py`, in the suite: eight symbols and
fourteen printed rows, all matching.

**This is the page printed p.2 borrowed from on the first day.**
`X S ROOF` and `XW SR` were `SYN`'d out of it by
`mcp_bootstrap_p2.strap`, and `X ERR AD` by pp.3 through 6. Here the
assembler places all three from the instruction stream, which is the
whole difference between an input to a check and a witness.

### `X IPL K` settles the two-number question, with the page's own arithmetic

`mcp_tape_manufacture.md` §2.1 flagged a reconciliation it could not
source: printed p.2's IPL control word counts `0o560` = **368**
words, and some other reasoning wanted **369**. Printed p.13 line 27
is

```
27* 000561.00+   -00000000   BU,40 ,10   X IPL K  SYN, 1.0 + X BS END - X IPLBS   - SIZE OF BOOTSTRAP
```

`0o561` = 369. So **both numbers are right and they mean different
things**: `X BS END - X IPL BS` is the record the tape holds, and
`X IPL K` is that plus one, the bootstrap *including its own control
word*. A verification has to say which it is counting, and now it
can cite a row rather than an inference.

### And a third instance of one bug class

**The `XW` COUNT field is in WORDS.** Line 35 writes the count as a
bare integer — `XW,0.0,29,XW IND` — and the listing prints `000035`.
Line 36 writes the same kind of number in `word.bit` form —
`XW,X IPLK+33.0,20.0` — and the listing prints `000024`. The
assembler shifted **neither**, so line 36 came out `0002400`, sixty-
four times too large.

C22-6531 printed p.12's rule (an integer in a word-counted field is
already in words; a bit address scales `>>6`) had been applied to
`XW`'s REFILL and to `CW`'s COUNT and **not to `XW`'s own COUNT**.
**No program in the corpus writes a dotted `XW` count**, which is
exactly why nothing caught it: the gap was invisible until a
historical listing wrote the field the other legal way. Same shape as
the `CW` count bug earlier the same day.

### Left for later

Line 38, `X BUFER SYN,X IN END+ 2000.0`, is **deliberately not
transcribed**. Its value is printed (`011406.00`) but `X IN END` is
defined on some other page, and `SYN`-ing it from this row's own
printed value would make the row prove nothing —
`mcp_bootstrap_p4.strap` already cites `X BUFER` at `011406.00` from
here. What is missing is the page that defines `X IN END`.

**Remaining for M3: printed p.14** (the forty-two chained PROSA
control words and `X BS END`), then **pp.7-8**, the error table,
which can now cite all thirty-nine message labels from the pages that
define them.

---

## 6i. MCP's PAGE 14 — the bootstrap's last page, and the symbol p.2 borrowed on day one

**2026-10-17.** `decks/mcp_bootstrap_p14.strap` and
`tests/verify_mcp_bootstrap_p14.py`, in the suite: **thirty-nine
chained control words, every one checked** in the four-group form the
listing prints, plus `X PROSA` and `X BS END`.

Each control word fetches one PROSA record of 513 words into
`X BUFER`, 512 words further along than the one before, chaining by
refilling from `$+1.0`. **Thirty-eight are `CW(CDSC)`** — C28-6129
printed p.14's "Count Disregarding Record, Skip and Chain", flags
`110` — **and the thirty-ninth is `CW(CR)`**, flags `000`, which is
what stops the channel.

**The count and the address check each other, thirty-nine times.**
The statements write `,513,` and the listing prints `001001` octal =
513; the last writes `,512,` and prints `001000`. The addresses step
`0o1000` words at a time — `011406`, `012406`, `013406` — against
operands written `0`, `512.`, `1024.`, so the decimal-to-octal
conversion is independently confirmed on every row.

**`X BS END` is what printed p.2's IPL control word counts to.**
p.2's `CW(CR)` counts `X BS END − X IPL BS` = `0o621 − 0o41` =
`0o560` = 368 words, and p.2's transcription has been `SYN`-ing
`X BS END` from here since the first day. Now the assembler places
it, and p.13's `X IPL K` counts one more. **All three numbers come
from rows rather than reasoning.**

### A typo that is IBM's, and what it proves

Line 22's comment reads **`-FETCH ONE PROSA REXORD`** — X, not C —
where thirty-eight others say RECORD. Verified at 600 dpi. It
compiles to nothing, and it is the proof that these thirty-nine
near-identical rows were **keyed by hand rather than generated**. A
page that looks formula-clean is worth one spot check for exactly
this reason: if it had been generated, a single transcription error
in my reading would have been indistinguishable from the pattern.

(Line 4 also writes `CW(CDSC),0` with no trailing period where every
other row writes `512.`, `1024.` and so on. Zero needs no units, so
the two spellings agree.)

---

## 6j. MCP's PAGES 7 AND 8 — the error table, and the bootstrap is transcribed

**2026-10-17.** `decks/mcp_bootstrap_p7_p8.strap` and
`tests/verify_mcp_bootstrap_p7_p8.py`, in the suite: **seventy-eight
`VF` half words and seven symbols, ninety checks.**

**ALL THIRTEEN PAGES OF MCP's IPL BOOTSTRAP ARE NOW TRANSCRIBED** —
printed pp.2 through 14, `docs/boot_plan.md` M3's transcription step.

`X ERR DD` is the index to everything else: one word per error code,
the first half holding the address of the site that failed and the
second the address of the message to print for it. Printed p.5's
`X ERR SH  KV,$1,0.0($2)` is the loop that scans it.

**The table checks its own length.** Printed p.8 line 31 defines
`X E DD K SYN,$-X ERR DD  -SIZE OF ERROR TABLE` and the listing
prints `000047.00+` — thirty-nine words, which is exactly what
seventy-eight half words occupy and exactly the number of distinct
error codes (00–29 plus 05A–05E, 16A–16C and 21A). The table's
extent was never assumed.

### The cross-check earned its keep on its first run

The thirty-nine message labels this page names are `SYN`'d here but
**placed** by `mcp_bootstrap_p9_p12.strap` and `_p13.strap` from
their own instruction streams. The verifier asserts the two agree
before checking a single row — and the first run failed:

```
FAIL MCP pp.7-8 XMSG25: this page SYNs bit 21204, pp.9-13 place it at bit 21208
```

The generator that wrote those `SYN`s had converted the **bit** part
of `000513.30` out of octal. Every other label ends `.00`, so one
symbol in thirty-nine was wrong and the page's own rows would still
have passed — the `VF` for `X MSG 25` would have been checked against
a value this file had itself invented. **Three statements now have to
coincide**: the page's printed `VF`, the `SYN`, and the other
program's placement.

### Three things the table says about MCP

* **Eight entries share five messages.** `000432.00` appears four
  times — `X MSG 15`, `X MSG 16`, `X MS 16A`, `X MS 16B` — under four
  different descriptive comments, and `000464.00` and `000501.00`
  twice each. The message block is otherwise strictly sequential, so
  three described messages have **no storage of their own**: several
  distinct failures deliberately print the same text.
* **The table is not in error-code order.** The code-10 pair sits
  between 05E and 06 and everything else is sequential. That rules
  out indexing by code and fits `X ERR IN` being a **search** word —
  `XW,X ERR DD,X E DD K+1.0,0` — scanned by p.5's `KV` loop rather
  than subscripted.
* **`X ERR 20` and `X ERR 21` are `BD,$`, not `SIC,X ERR AD`.** Every
  other error site stores its instruction counter so the routine can
  print where it failed; these two branch-disabled to themselves and
  halt. Their messages are "NO CONSOLE DEFINED" and "NO CONSOLE
  AVAILABLE" — **with no console there is nothing to print to, so
  there is nothing to store an address for.** The two corroborate
  each other.

### What the assembler learned, and one substitution

* **`DR`**, Data Reservation. It emits nothing — that is what a
  reservation is — and its width is checked by what follows: printed
  p.8's `X LR DR(BU,64),(3)` puts `X ERR CW` three words later.
* **A bare `CW` with no secondary is legal** and means all three
  flags zero, the same bits `CR` sets. Printed p.8 writes it twice
  and both print `000`. The assembler used to demand one of the eight
  secondaries, which would have made those historical rows
  unassemblable.
* **Line 34's `X MSG CW(.25)1` is a BIT DESIGNATION** — set bit 25,
  which is a control word's chain flag — and is written `CW(CCR)`
  here. C28-6129 printed p.14 defines `CCR` as chain 1, multiple 0,
  skip 0, the same three bits, and the checked row proves the
  substitution. Inventing the general semantics of bit designations
  from one row is what rule 4 forbids.

---

## 6k. MCP's BOOTSTRAP RUNS — and the three gaps it found were not the three predicted

**2026-10-18.** IBM's operating system executes end to end on this
model. `strap/mcp_image.py` merges the thirteen transcribed pages,
`mktape.py --cw-in-image --tape-mark` writes the tape, and
`run_mcp_boot.sh` boots it through `iplStart()`. In the suite.

### The method mattered more than any of the fixes

The plan was A: build one image; B: **run it and let the model say
what is missing**; C: fix what B finds, in that order. The
alternative — read the listing, list what looks unimplemented, build
that — would have produced this list: `SPFL`, tape marks, `LOC`,
`GONG`, the disk.

**What the model actually reported, in order, was:**

1. **Address Invalid was never raised on a store past installed
   core.** Printed p.2's core-sizing loop is
   `Z,0.0($15)` / `BADZ,$+1.0` / `CB+,$15,X CLSTO` — **no terminating
   count.** AD is the only thing that ends it. The model had AD for
   floating-point operands and nowhere else, so after twelve million
   steps index 15 had wrapped the 24-bit address field and was
   clearing from word 6 again.

   MCP needs the model to do something **no diagnostic deck in this
   corpus does: size core storage by running off the end of it.** 243
   transcribed programs and not one of them asks that question.

2. **`LVE`.** See §6l.

3. **`SPFL` and a tape mark.**

**`LOC` and `GONG` were never reached** — both are only in the ERROR
ROUTINE, and the bootstrap never errs. **The disk was never reached**
either: `FETCH PROSA` reads from the TAPE, takes End Exception at the
end of the reel, and printed p.4's `X DONE` handles that as END OF
PROSA FILE. Three of the five predicted blockers were off the path
entirely.

### The two checks that carry the claim

A program that stops quietly looks exactly like a program that
finishes. So:

* **Printed p.4 line 37**, `CM1111(BU,1),$0 +.25  -END OF PROSA
  FILE`, sets word 16 bit 25 — index register X0's flag bit — and
  **nothing earlier in all thirteen pages writes it.** It is on the
  late path, after FETCH PROSA and after `X DONE` has seen End
  Exception.
* **`X ERR AD` is zero.** Every error site on pp.3-6 does
  `SIC,X ERR AD` before branching to `X ERROR`, and the instruction
  counter is never zero inside the bootstrap. Zero means no error
  site ever ran.

And the indicator register holds `XCZ`, `XVZ`, `RZ` — **neither OP
nor AD.** The model refused nothing and addressed nothing it does not
have.

### MCP measured the machine

Printed p.2's sizing loop stored **word 98,304** in `X S ROOF`, which
is `StretchMemory`'s `InstalledWords`, six units — a typical Stretch,
which is what the user asked for at the start. IBM's own code
measured this simulated machine and got the right answer.

---

## 6l. `LVE` — the page was nine pages on, and already cited in the same file

`bsv/README.md` carried, for months, the reason `LVE` was
unimplemented:

> "p.20 describes it only as enabling 'indirect addressing' ... and
> this session could not find a page giving its exact bit-level
> behavior distinctly from `LV`'s"

**The page is printed p.29.** It gives the whole thing: which
instruction's effective address is taken, that the target's operation
is *not* executed, that the target's own `J` is ignored, where the
result goes, and the one-millisecond/`USA` bound on a chain.

**And `StretchExecute`'s own `SVA` arm already cited printed p.29**,
for "Address Insertion" — the section immediately below LVE's on the
same page. The source was not merely in `docs/`; it was quoted a few
hundred lines away in the same file, for the neighbouring
instruction.

This is the project's recurring lesson in its sharpest form yet.
*"This needs document X" is only true once document X has been
opened* — and the corollary now is: **when a feature's neighbour is
implemented, read the citation its neighbour already carries.**

**The address-width rule came free.** LVE and SVA need the identical
six-case table — jb_ax3a printed p.140's — in opposite directions,
and `StretchDecode.svaReplaceAddr` already had it, deck-verified and
swept over all 2^14 half-words. `decks/lve_indirect.strap`
exercises it in the LVE direction by pointing targets of three
different classes (24-, 19- and 18-bit address fields) at **one**
datum: all three must produce that datum's bit address, because
p.21 extends the short fields "with the necessary low-order zeros".
A width bug is off by 32× or 64×, not by a little.

**A chain is refused out loud.** p.29 makes a chained LVE an
iteration with a time bound; this E-box runs one instruction per step
with no inner loop, so a target that is itself an `LVE` sets OP
rather than being silently truncated to one level.

**And a test can encode the absence of a feature as its premise.**
`op_ad_indicators.strap` demonstrated "Operation Code Invalid works"
by issuing `LVE` — so implementing LVE broke it, correctly. It now
uses `RNX`, with a note that it will need swapping again every time
the model gains an arm.

---

## 6. Open questions — record, do not guess

**What is the `-ILLEGAL OP.` word doing in routine 1262's TEST 3A and
3B?** ASKED AND ANSWERED on 2026-09-24, within hours, and it is kept
here because *how* it closed is reusable.

**The answer: it is a higher-priority DECOY that protects AD.** Not a
probe, which is what it is in TEST 1CC. Three primary-source steps,
each verified first-hand at 300 dpi:

1. **The block runs DISABLED.** 1260's `I60S1` clear-indicators
   subroutine returns via `I60SX1 $BD,0` at 023041.00 (PDF p.85) —
   a BRANCH DISABLED whose address the caller's `SIC` plants. Printed
   p.41: `SIC` stores the instruction counter into bits 0-18 and
   *"Other bits of the half-word are not disturbed"*. Printed p.40:
   *"Branch Disabled (BD). This operation disables the interruption
   mechanism, and then performs the same operation as BRANCH."* No
   `BE` exists anywhere in `I60S1`.
2. **An execution operation interrupts anyway.** Printed p.50, verbatim:
   *"Second, at the completion, termination, or suppression of an
   execution operation, interruption is always permitted."* Its
   PROGRAMMING NOTE goes further and describes the deck's own follow-up
   test in advance: *"...it is caused only by the actuated indicator of
   highest priority whose mask bit is one... **Examination for other
   actuated indicators can be programmed into the correction
   routine.**"*
3. **The interrupt CONSUMES the indicator it vectors on.** Printed
   p.48, verbatim: *"a mechanism develops the number of the leftmost
   actuated indicator whose mask bit is one. **After this leftmost
   indicator has been turned off**, the developed number is added to
   the contents of the interruption address register."*

OP is 15, AD is 16. Without the word, the interruption would consume AD
and the `BADZ` would find it off — a spurious *"-AD NOT SET..."*. With
it, OP outranks AD, OP is consumed, and AD survives to be tested. The
deck exercises the p.50 rule independently at block `I6225` (p.93),
which is called with `BD`, never enables, and whose OK path is an
interruption taken while provably disabled.

**Two things worth carrying forward.**

*The named next step worked; the candidate list did not.* The earlier
version of this item listed three candidate resolutions and named the
two untranscribed pages that would decide it. Reading the named pages
settled it in one pass. **The answer was none of the three candidates.**
Candidates are a way of showing a question is tractable — not a menu
the answer comes from — and listing them risks anchoring the search on
a wrong frame. Name the *evidence* that would decide it, and go read it.

*Two readings of one word were both right.* 1CC uses the identical
word as a pure enable-state probe; 3A and 3B use it as a decoy. Nothing
was in conflict — what the word does depends on whether an execution
operation follows it. The instinct to treat the contradiction as "one
of these must be wrong" would have thrown away a correct reading.

Recorded in `decks/ax5b_162_test3b.strap` at length and
cross-referenced from `ax5b_162_test3a.strap`, where the row is now
marked LOAD-BEARING: it looks removable and is not.


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
`I42XW4`, refill field 9 = `$R`, in routine 1242 — is **defined and
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

**AND THE DECK'S OWN AUTHORS KNEW THE ZERO BOUNDARY WAS OPEN.**
Found 2026-09-24 and verified first-hand at 300 dpi, `jb_ax4b` PDF
p.98, routine 1244's constants:

```
I44XW1  XW,I44B1,0,0
I44XW2  XW,I44B2,0,0
I44XW3  XW,1.0,31,0
                        -IF 0 BECOMES ILLEGAL FOR RNX, USE THE
                        -FOLLOWING THREE INDEX WORDS TO REPLACE
                        -THOSE DIRECTLY ABOVE.
I44XWA  XW,I44B1A,0,0
I44XWB  XW,I44B2A,0,0
I44XWC  XW,0.0,32,0
```

As shipped the sweep starts at `1.0` with count 31 — 1 to 37 octal,
matching the routine header. A **spare triple sits beside it** starting
at `0.0` with count 32 and pointing at the "ADDRESS IS 0." entries of
both error tables, which exist and are otherwise unreachable. So the
people who wrote the test in 1961 did not know whether 0 was illegal
for `RNX` either, and shipped the patch rather than pick a side.

That is the best possible answer to "manual says 0-31, deck walks
1-31": **neither is wrong, and the gap is a hedge, not an error.**

**~~One boundary discrepancy to settle if `RNX` is implemented~~ —
the manual was self-consistent all along.**
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
  at `I6090` into the word-spaced table slots has not been traced. The
  table's *units* are settled — 64 full words, from `I60IT` at
  023201.00 to `I60DMP` at 023301.00 — with the reasoning in
  `run_tests.sh` §"The interruption mechanism".

Two conventions that are not questions and cost a session each when
forgotten: Reference Manual **PDF page = printed page + 3**, and
`ja_ua1_ssip` is cited by **PDF page** because its listing carries no
printed page numbers.

## THE BACK-MATTER MAP -- what is in the appendices of the manuals this project already cites, 2026-10-21

Written because two finds in one day came out of appendices of
documents `docs/` already had and this project already quoted. The
rule drawn was **"a document you have CITED is not a document you
have READ"**; this is the map that makes acting on it cheap. Offsets
below were each confirmed against a rendered page.

| document | appendix | printed | PDF | what it is |
|---|---|---|---|---|
| `22-6530-2` RefMan | *(unlettered, 7 sub-tables)* Instruction Formats | 163 | 166 | bit layouts of all 13 instruction formats + the index word |
| | List of Indicators | 164 | 167 | all 64 indicators: number, mnemonic, mask bit, class, reset rule |
| | Storage Assignment | 165 | 168 | special locations 0-31: name, length, bit address |
| | Character Codes | 166 | 169 | four 8-bit code charts (48/49/89/120 sets) |
| | Alphabetical Operation Codes | 167 | 170 | mnemonic → name |
| | **Complete Operation and Modifier List** | **168-169** | **171-172** | **binary opcode bit patterns per class + modifier bits** |
| | Powers of Two | 170 | 173 | 2^1-2^64 |
| | Index | 171-172 | 174-175 | subject index |
| `C28-6129` STRAP-II | A STRAP-II Mnemonics | 43-45 | 46-48 | every mnemonic: type, footnote, **Word No. + Bit Address** |
| | B Pseudo-Operations | 46 | 49 | ~70 pseudo-ops |
| | C Symbolic Descriptions | 47-53 | 50-56 | formal per-op semantics |
| | D Error Messages | 54-55 | 57-58 | numbered assembler errors 1-127 |
| | *(N28-1081 update, Apr 1963)* | — | 59-78 | new pseudo-ops, **relocatable card formats**, revised B/C/D |
| | *Appendix E is cited by the update and ABSENT from this scan* | | | |
| `C22-6729` STRAP-II SAG | A Formats | 189-194 | same | STRAP II's internal record layouts |
| | B Additional Instructions | 195-196 | same | superset pseudo-op list (adds IOD/REEL) |
| | C Coded Expressions | 197-201 | same | bit-prefix encoding spec |
| | D-F designations / terms / rules | 202-207 | same | glossary and coding rules |
| | G Binary Deck Composition | 208 | same | the actual card deck layout |
| | H Memory Map of STRAP II | 209 | same | core layout of its sections |
| `C22-6728` MCP SAG | **A Symbolic I-O Control Tables** | **246-260** | same | **channel/unit status (Fig 137-138), Unit Area, File Area, Symbolic I-O Location, Reel Pool -- every indicator named with its bit** |
| | B Flow Chart Standards | 261-262 | same | documentation convention |
| | C The Multiplier Register | 263 | same | `$MR` on K-2+: LMR/LFT 10010, STM 11110, `*+` 01110 |
| | D Connector Index | 264-266 | same | flow-chart navigation |
| | Index | 267-269 | same | subject index |
| `R23-9694` CE Vol 2 | **none** | | | no appendix and no index |
| `R23-9695` CE Vol 3 | A *(storage assignment)* | 118 | same | locations 0-31 **with a storage-class column M/I/T/K** -- finer than the RefMan's |
| | B Extended Character Set | 119 | same | character → binary / octal / hex |
| | C Symbolic Descriptions | 120-127 | same | duplicate of C28-6129 App C |
| | D CE Abbreviations | 128-134 | same | the decoder ring for the `ja_*`/`jb_*`/`ka_*` listings |
| `C22-6531` STRAP-1 | A Mnemonics | **56**-58 | 57-59 | type legend + `$` symbols with Word/Bit, then the operation list |
| | B Pseudo-Operations | 59 | 60 | |
| | C Symbolic Descriptions | 60-67 | 61-68 | duplicate, with handwritten corrections |
| | D Error Marks | 68 | 69 | listing error marks A-Z and their causes |

**DUPLICATES, so the same table is not counted three times.**
"Symbolic Descriptions and Mnemonics for IBM 7030" is the same table
in `C28-6129` App C, `R23-9695` App C and `C22-6531` App C; take
`C28-6129`'s. The mnemonic + Word/Bit-address table is `C28-6129`
App A and `C22-6531` App A. Storage assignment is `22-6530-2` p.165
and `R23-9695` p.118 -- **take `R23-9695`'s**, which adds the storage
class.

**INDEXES EXIST IN ONLY TWO OF THESE**: `22-6530-2` (printed 171-172)
and `C22-6728` (printed 267-269). That is worth knowing before
planning a search.

**THE RANKED WORKLIST**, highest value first, each one a thing this
project would otherwise derive:

1. ~~`22-6530-2` printed **168-169**~~ — **DONE THE SAME DAY.** The
   Complete Operation and Modifier List is now
   `tests/verify_refman_p168_opcodes.py`, checking all ten classes
   two-way: 24 VFL integer and radix, 29 floating point, 16 direct
   index, 16 immediate index, 6 unconditional branch, 5
   miscellaneous, 11 input-output, 3 connective, 16 index branching,
   8 transmit, plus the P-field indexing modes. **Every one agrees**,
   which closes `strap/README.md`'s "Next steps" item 2 — and against
   a better source than that item named.

   Three things worth keeping from it. **The check is on the
   TEMPLATES**: the page gives each code as a pattern over a named
   bit range (`ssbxxxxx1iiii`, `nssxxxxx10iiii`, `jjjj10000xxxx`) and
   `opcodes.py` stores a different slice of each, so the verifier
   applies the template's own rule — and the immediate-index rule
   *differs* from the other three, its x's being at the end with
   nothing trailing them. **Two values moved from a summary to the
   manual**: `CONNECTIVE_SUFFIX` and `IO_OP` were taken from the
   `X22-6533` pocket card, which is a summary of this very page. And
   **the P field is printed** — "INDEXING MODES FOR VARIABLE FIELD
   LENGTH OPERATIONS; Instruction bits 32-34", 000 direct, 100
   immediate, 001 `V+` … 111 `V-CR` — the field a whole session was
   spent deriving from the other end.
2. `C22-6728` printed **247-260** -- the rest of Appendix A. p.246 is
   done (see the section above); the Unit Area, File Area, Symbolic
   I-O Location and Reel Pool tables are not.
3. `C28-6129` PDF **59-78** -- the April 1963 newsletter's
   relocatable binary card formats, which bear on boot_plan A3.
4. `C22-6729` printed **208-209** -- STRAP II's binary deck
   composition and memory map.
5. `R23-9695` printed **128-134** -- the CE abbreviation glossary,
   which would make three unused diagnostic oracles readable.
6. `C22-6728` printed **263** -- `$MR`, a K-1/K-2 model difference
   that affects decoding.

**NOT SWEPT**: `C22-6728-1`, the later revision, whose back matter may
differ from the base revision's.

## >>> THE CHANNEL AND UNIT STATUS TABLES ARE PRINTED, AND EVERY BIT DERIVED FROM pp.17-18 IS NAMED ON THE PAGE <<< 2026-10-21

`C22-6728` **printed pp.246-260 = PDF pp.246-260, "APPENDIX A --
SYMBOLIC I-O CONTROL TABLES"**, Figures 137 and 138. Found by the
appendix sweep that the Appendix F lesson prompted, in a document
this project cites for its pp.215-217.

The opening paragraph is the prose description of the two pages that
now run:

> "The channel and unit status tables reflect the operational status
> of all I-O channels and units logically attached to the system.
> **The tables are constructed by the Initializer program at IPL time
> from IOCD cards defining the I-O configuration.** … The channel and
> unit status tables will exist in two distinct forms, depending upon
> whether a channel has a single logical or physical unit (Figure
> 137), or multi-units (Figure 138). … **An entry in these tables
> consists of one word.**"

"An entry consists of one word" is the thing `CB+`'s one-word step was
used to derive. Here it is stated.

**EVERY BIT POSITION DERIVED FROM THE LISTING IS A NAMED FIELD**, and
the names match the listing's own comments:

| bit | printed name | the row that writes it | its comment |
|---|---|---|---|
| 25 | **SCHAVL** | p.17 l.44 `CM0000(BU,1), .25($3)` | "CHANNEL AVAILABLE FLAG" |
| 27 | **SMULTI** | p.18 l.9 `CM1111(BU,1), .27($3)` | "MULTI BIT TO ON IN CST" |
| 29 | **SUNASG** | p.18 l.7 `CM0000(BU,1), .29($3)` | "MEANINGLESS ASSIGN BIT" |
| 0-26 | **SUNAA**, "Address of Unit Status Table" | p.18 l.5 `SV, $15, 0.0($3)` | "INSERT UNIT STATUS TABLE ADDRESS IN CST" |
| 52-55 | **SEQUIP** | p.17 l.54 `ST(BU,4), .52($3)` | "INSERT IN CST ENTRY" |
| 59-62 | **SUNITK** | p.18 l.30/l.37 at `.59($3)` | "UNIT COUNT IN CST" |

and in the UNIT status table entry, which `$15` walks:

| bit | printed name | the row | its comment |
|---|---|---|---|
| 27 | **SDISPO** | p.18 l.23 `.27($15)` | "TAPE DISPOSITION BIT ON" |
| 28 | **SUNAVL** | p.18 l.21 `.28($15)` | "UNIT AVAILABLE BIT ON" |
| 29 | **SUNASG** | p.18 l.22 `.29($15)` | "UNIT NOT ASSIGNED BIT ON" |
| 39 | **SSEL** | p.18 l.24 `.39($15)` | "SELECT STATUS ON" |

Ten for ten. `SDISPO` is *disposition*, `SSEL` is *select*, `SUNAVL`
is *unit available* — the 1963 comments and the 1963 field names are
the same words, and this project put them together from opposite
ends without having seen either page name the other.

**ONE AMBIGUITY, AND THE CODE RESOLVES IT.** Figure 138's tick labels
(49, 55, 59, 63) do not survive magnification well enough to fix the
right-hand edge of `SEQUIP` and `SUNITK`. MCP settles both. The
equipment code is stored by `ST(BU,4), .52` — four bits at 52 — so
`SEQUIP` is 52-55. And `SUNITK` **must be exactly 59-62**, because
p.18 line 30 sets a SINGLE bit at `.59` under the comment "UNIT COUNT
IN CST TO 8", and one bit at the left of a field means eight only if
the field is four bits wide. A five-bit field would make that row
write sixteen.

That is the project's standing principle running the other way for
once: usually the program is read to recover a structure whose page
is missing. Here the page exists, its drawing is ambiguous, and the
program disambiguates the drawing.

**WHAT IS STILL NOT CHECKED in Appendix A**: `SARCAD` (bits 32-48 of a
multi-unit entry), `SEMODE`, `SUNIT`, `STATI`, `SOWNER`, `SSETUP`,
`SSETDN`, `SVER`, `SCNSSG`, `SUNDENS`, `SELG`, `SMOUNT`, `SREW`,
`SIMNT`, `SRD`, `SWR`, `SSPACE`, `SCTL`, `SREL`, `SUNRES`, `SOVRES` —
and pp.247-260's Unit Area Table, File Area Table, Symbolic I-O
Location Table and Reel Pool Table. **pp.17-18 write ten of the
fields on p.246 and nothing else on it**, which is a useful measure
of how much of MCP's I/O bookkeeping the transcribed pages cover:
not much, and now there is a printed map of the rest.

## THE INDICATOR-BRANCH MNEMONIC'S LEADING `Z` MEANS "BRANCH IF OFF", 2026-10-21

`C22-6531` Appendix A footnote 2 gives the indicator-branch form as
**`B[Z]<name>[Z]`**, two optional `Z`s around the indicator name, and
the Reference Manual's INDICATOR BRANCHING block (printed p.169)
gives the two modifier bits as *leave indicator / set indicator to
zero* and *branch if off / branch if on*. **Which `Z` is which was
never written down here, and it was assumed backwards.**

It is the **leading** `Z` that means "branch if off". Three
instructions across two pages agree:

| | | |
|---|---|---|
| p.17 l.31 | `BZAE, X19` | takes the "NOT AN IOCD CARD" exit when the compare **failed** |
| p.19 l.25 | `BZAEZ, X ERROR` | takes "NOT AN IOD CARD EITHER" the same way |
| p.19 l.6 | `BZXH, X 18 4` | measured below |

**The measurement.** A `DK` card was run with the equipment table
ordered so that the matched entry left `$1`'s count at exactly six,
and line 4's `KCI,$1,6.0` therefore compared six against six —
equal, so `XH` **off**. A halt planted at `X18 4` caught the machine
there (PC 982), and a probe on word 17 read the count back as six.
So `BZXH` branched with `XH` off. Reading the grammar the other way
predicts no branch.

**This is not a claim about the encoding**, which is already proven:
`verify_mcp_bootstrap_p19.py` matches line 6's assembled word to the
listing bit-for-bit. It is about what the bits *mean*, and the
evidence is that MCP's own control flow only makes sense this way.

**IT CORRECTED A DERIVATION WRITTEN THE SAME DAY.** p.19 line 4
partitions the equipment table by the *position* of the matched entry
(see the p.19 section below), and the direction of that partition
depends entirely on this. With the grammar read backwards, disk and
console came out as entries **4 and beyond**; read correctly, they
are entries **1-3**. `gen_mcp_p17_tb.py`'s `EQUIPMENT_CODES` is
ordered on the corrected reading, and the `disk` mode reaching p.19's
body at all is what demonstrates it.

## >>> A MODEL BUG FOUND BY MCP AND FIXED: THE LOOK-AHEAD'S STORE-FETCH INTERLOCK DID NOT KNOW ABOUT "CONNECT TO MEMORY", 2026-10-21 <<<

**THE CAUSE.** `storeTarget()` in `bsv/StretchIBox.bsv` listed the
floating-point stores and the four VFL store codes and had **no case
for the connectives**, so `CONNECT TO MEMORY` — which writes storage —
was invisible to the look-ahead's level-to-level `storeAddr`
interlock. A younger level fetching the word a `CM` was about to
write took its copy **before** the write, and because `CM`'s store is
a read-modify-write that reuses the fetched word (`mHiWord` in the
`Conn` arm), the stale copy went straight back — undoing the `CM`
before it.

The connectives **are** `isEboxClass`, so they do get look-ahead
levels. That is what separates this from the `BB` case the `Conn`
arm's own comment describes: `BB` is not E-box class, `iboxHazard`
drains the whole look-ahead before it runs, and a `storeTarget()`
case for it would be dead code. For `CM` it was the missing case.

`decks/cm_adjacent_offsets.strap` is now the regression test, in the
suite, with the thirteen blocks below as its checks. **The injection
is the fix itself**: removing the `Connective` case puts D3 and DD
back to one bit each and leaves the other eleven passing — which is
what says the case is necessary and not merely sufficient.

**Where it came from.** Printed p.19 lines 9-11 write three single
bits into the channel status table entry in a row:

```
CM1111(BU,1),.61($3)      -SET UNIT COUNT TO TWO
CM1111(BU,1),.27($3)      -MULIT BIT ON IN CST
CM0000(BU,1),.29($3)      -MEANINGLESS ASG BIT OFF
```

Running a **disk** card through pp.17-19 left bit 27 set and **bit 61
lost**. Halts planted between the rows showed bit 61 present after
line 9 and gone after line 10.

**What was measured, outside MCP:**

| block | | result |
|---|---|---|
| D1 | `.61` then `.27` | both bits |
| D2 | `.27` then `.61` | both bits |
| **D3** | **`.29` then `.27`** | **`.29` LOST** |
| D4 | `.61` then `.62` | both bits |
| D5/D6 | each alone | correct |
| D7 | `.27` then `.29` | both bits |
| D8 | `.29` then `.31` | both bits |
| D9 | `.29`, NOP, `.27` | both bits |
| DA | `.61` then `.59` | both bits |
| DB | `.29` then `.3` | both bits |
| DC | NOP, then `.29` then `.27` | both bits |
| **DD** | **`.29` then `.27` again** | **`.29` LOST** |

**TWO THEORIES, BOTH KILLED BY THE DATA.** *"The write is eight bits
wide, not one"* fits D3 — a write at 27 covering 27-34 would take out
29 — and every row through D8. **DA kills it**: a write at 59
covering 59-66 would take out 61, and does not. *"The second write
reads a stale copy of the word"* fits D3 and D9. **D1, D7, D8, DA and
DB all kill it**: every one is a second write into a word the
instruction before it just changed, and every one keeps both bits.

**WHAT ACTUALLY DECIDES IT IS DC AGAINST DD.** Those two blocks are
**the same instruction pair on the same data**, one after the other,
differing only in what precedes them — and DC keeps both bits while
DD loses one. Two identical instructions on identical operands cannot
correctly give two different answers. **So there is state in the
model that should not be there.** That is as far as the evidence
goes; the mechanism is *not* identified, and is deliberately not
guessed at here. The offsets are not the variable either: `.29`→`.27`
fails while `.61`→`.59`, the same descent two bits apart in the other
half of the word, passes.

**WHY NOTHING CAUGHT IT BEFORE.** Printed p.18 writes the same kind
of pair at `.29` and `.27` and comes out right, because its first
write is `CM0000` — it *clears* bit 29, so losing that write and
re-clearing the bit are the same picture. Every other deck in the
corpus writes a count field **last**. p.19 is the first program here
that sets a high-offset bit and then goes on writing lower ones into
the same word.

**WHAT IT UNBLOCKED.** `gen_mcp_p17_tb.py`'s **`disk`** mode — a
`DK` card, the only card that reaches printed p.19's own body — now
passes and is in the suite. All four modes (none/units/units8/disk)
are green.

**AND THE OBVIOUS FOLLOW-UP WAS AUDITED RATHER THAN ASSUMED: `CM`
WAS THE ONLY GAP.** A missing case in a list invites the question
"what else is missing?", so the list was checked against what the
model actually implements:

* **VFL** — the `VflInt` arm implements `L`, `ST`, `+`/`+MG`,
  `M+`/`M+1`/`M+MG`, `K`/`KF` and `LCV`. Of those exactly four write
  storage, and `storeTarget` lists exactly those four
  (`001101`, `001001`, `101001`, `101011`). `SRD`, `LTRS`, `CV` and
  `DCV` are not implemented at all, so a case for them would be dead
  code today — but each will need one when it is built.
* **Floating point** — the arm's writes to the effective address are
  `ST`/`SRD`/`SLO`, `SRT`, and `M+`/`M+MG`, and `storeTarget` lists
  all six.
* **Connectives** — `CM` writes storage; `C` writes the accumulator
  and `CT` writes nothing, so only `CM` belongs, and only `CM` is
  added.
* **`BB` and `SIC`** write storage and are deliberately absent,
  because neither is `isEboxClass`: `iboxHazard` drains the whole
  look-ahead before they run, which is strictly stronger than the
  level-to-level interlock. The `Conn` arm's own comment already said
  this about `BB`.

**So the invariant to hold going forward is: every
`isEboxClass` instruction that writes general storage needs a
`storeTarget` case, and only those.** Worth checking whenever a new
storing operation is implemented — `SRD` and `CV`/`DCV` are the next
candidates.

**THE SHAPE OF THE SEARCH IS WORTH KEEPING**, because the two dead
theories were both *reasonable* and both took real evidence to kill,
and the thing that finally located the fault was not a theory at all.
DC against DD is the same instruction pair on the same data, run one
after the other, and they disagreed. That rules out **every**
explanation living inside the instruction — width, offset, byte
boundary, contraction, the arithmetic — in one step, without knowing
anything about the mechanism. The remaining candidates all had to be
state carried **between** instructions, and there is exactly one such
thing in the path: the word the look-ahead hands the E-box.

Build the pair that differs only in history before building the pair
that differs in operands.

## PRINTED p.19 IS TRANSCRIBED -- 46 rows, bit-exact, 2026-10-21

`decks/mcp_bootstrap_p19.strap` + `tests/verify_mcp_bootstrap_p19.py`.
The DISK/CONSOLE half of the IOCD processing — p.18 handles a TAPE
channel, which carries up to eight units; this page handles
everything else — plus the move of the status tables into upper
storage (lines 27-53).

**The page was opened to settle a prediction and it did.** Line 9 is
`CM1111(BU,1),.61($3)`, "SET UNIT COUNT TO TWO". See the prediction
section below.

**Both forward references into this page were recovered from
encodings and both are exact**: `X18` = `000740.40` off p.18 line 2's
branch-address field, `X19` = `000756.40` from p.17's indicator
encoding. The page begins at `000740.40` and its line 23 sits at
`000756.40`.

**`X IOD` begins where `X IOCD` ends.** Line 23 compares 36 bits —
three columns, `IOD` — against `001750.40`, and p.17 put `X IOCD` at
`001747.60` with a 48-bit length, which runs to `001750.40` exactly.
Adjacent literals, in the order `C22-6728` p.88 gives the control
cards: IOCD, IOD, MCPP.

**Two rows failed first and both were MY reading errors**, not
assembler ones. Line 6 is `BZXH`, not `BZXE` — Index High, not Index
Equal, one glyph. And line 4's hex byte is `0A`, not `CA`, which is
the fourth instance of `listing_typography.md` §13 and contributed a
new tell to it (§13a): at 1200 dpi that row's six-digit address field
prints as `COCCO6`, the same digit zero as three `C`-shapes and two
`O`-shapes **within one field**. A field that disagrees with itself
about a glyph announces which glyph is unstable, and that is visible
without decoding anything.

### p.19 IS IN THE RUNNING TESTBENCH — three pages, one program

Done the same day. The loop processes the card, runs out of IOCD
cards, reaches `X 19`, fails its `IOD` compare, and p.19 line 25's
`BZAEZ, X ERROR` fires: **PC 182 = 5824/32**, MCP's own error exit
instead of a planted stop. Both `X18` and `X19` came out of `exits`
in the same change, as they had to.

**>>> AND THE MERGE HAD A BUG THAT ONLY THE PC COULD SEE. <<<**
p.18's last instruction is a half word at `000740.00` and p.19's
first is the *other half of that same word*, `000740.40`. The
generator merged decks with `dict.update`, so p.19's word **replaced**
p.18's and deleted line 45's `B, X131`. A zero half-word is `BE` to
address zero — so the machine ran the entire card loop correctly,
produced every expected table entry, and then branched to 0.

**All three data checks passed. Only the PC said anything was
wrong.** That is the argument for checking the PC separately from the
values, and it is worth keeping because the failure mode is so quiet:
a fixture bug that destroys one instruction of a transcribed page,
*after* all the work the test measures has already been done
correctly. The merge now ORs and asserts the contributions are
disjoint, so two decks claiming the same bits fail loudly.

**WHAT p.19 IS STILL NOT EXERCISED ON: lines 2-22, its whole
disk/console body.** A `TP` card takes p.18's tape path and only
p.19's lines 23-25 run. A `DK` or `CN` card would reach them — and
p.19 line 4 is why that is not just a constant change:

```
X18 1   KCI,$1,6.0     -LOGICAL MULTI UNIT * DISK OR CONSOL
        BZXH,X 18 4
```

**It tests the remaining COUNT of p.17's equipment search, not the
equipment code.** p.17 line 48 sets that count to ten and the search
spends one per entry examined, so the count *is* the matched entry's
position in `X EQP T` — and `6.0` **partitions the table by
position**. The equipment table's ORDER therefore decides which
equipment is "logical multi unit", which is a real constraint on a
structure whose own page nobody has transcribed. The fixture's six
entries are invented, so a `DK` card's behaviour would be a fact
about the fixture, not about MCP. **This is the first thing to settle
before adding a disk mode**, and `C22-6728`'s index may have it —
"I-O ASSIGNMENT TABLES 65", "I-O CONTROL TABLES 10".

## >>> A FABRICATED QUOTATION, FOUND AND CORRECTED, 2026-10-21 <<<

`tests/run_tests.sh` said, of printed p.17's `X 19` exit:

> 'The page's own comment on that row is "X 19 IS THE NORMAL END".'

**The page says no such thing.** Printed p.17 line 31's comment is
`-NOT AN IOCD CARD`. "X 19 IS THE NORMAL END" was a heading **I**
wrote in `gen_mcp_p17_tb.py`'s own commentary, and writing the
section up turned my own paraphrase into a quotation attributed to a
1963 listing.

This is the worst error class this project can produce. Every other
quoted comment in `run_tests.sh` was checked against the page. This
one was invented, in a file whose entire purpose is citing primary
sources, on the same day as five separate wins that all depended on
quotations being trustworthy. **A reader has no way to tell the
invented quotation from the forty real ones.**

**HOW IT HAPPENED, because the mechanism is reusable and therefore
dangerous.** The generator's comment blocks are written in the same
voice as the listings they describe — capitals, terse, imperative —
so a heading of mine sitting three lines above a real quoted comment
reads exactly like one. When the section was written up, the heading
was lifted across a file boundary and acquired quotation marks on the
way.

**THE RULE THIS NEEDS**: a quotation from a listing gets quotation
marks only if it was copied from the rendered page in the same
sitting, or from a deck line that carries the listing's own `!`
comment. Anything recalled from this project's own prose is a
paraphrase and must read as one. Checking is cheap — `grep` the deck.

**AND IT WAS WRONG AS A FACT, WHICH IS HOW IT WAS CAUGHT.** Printed
p.19 line 23 is

```
X19   KF(BU,36),XIOD,12     -COMPARE AGAINST * IOD *
X ERR 19   SIC,X ERR AD
      BZAEZ,X ERROR         -NOT AN IOD CARD EITHER
```

Thirty-six bits is **three columns** — the characters `IOD`. So
`X 19` is not an end; it asks whether the card that failed the IOCD
test is an **IOD** card, which is exactly the order `C22-6728`
printed p.88 gives: "Three types of control cards are used: 1. I-O
Configuration Definitions (IOCD) 2. MCP IOD's (IOD) 3. MCP Parameters
(MCPP)." The claim was false twice over, and only the second
falsehood was checkable by running anything.

**ONE THING p.19 CONFIRMS IN PASSING, and it is the method working
as designed.** Both forward references into this page were recovered
from instruction encodings rather than read: `X18` = `000740.40`,
taken off p.18 line 2's branch-address field, and `X19` =
`000756.40`, "RECOVERED FROM THE INDICATOR ENCODING" on p.17. Printed
p.19 begins at **000740.40** and its line 23 sits at **000756.40**.
Both exact.

## A PREDICTION ABOUT PRINTED p.19, WRITTEN BEFORE READING IT, 2026-10-21

Figure 44's `X18` branch — the disk/console path — contains a box
reading **"SET UNIT COUNT TO TWO AND SET MULTI BIT ON, ASSIGN
CHANNEL"**. That row is a check on today's `SUNITK` derivation, and
it is checkable before the model runs anything, so the prediction
goes here first.

`SUNITK` was derived as **bits 59-62** because p.18 line 30 sets a
SINGLE bit at `.59` under the comment "UNIT COUNT IN CST TO 8", and
one bit at the left of a field means eight only if the field is four
bits wide.

**Two is `0b0010`, which is not a bit at a field's left edge.** So
p.19's row cannot be another `CM1111(BU,1), .59`. On the 59-62
reading it must write a single bit at **`.61`**.

* **If p.19 sets one bit at `.61`** — the derivation is confirmed
  from a second, independent direction, by a different page writing a
  different value into the same field.
* **If it writes something that only makes sense for a field at
  56-59** — then Figure 138's tick marks were read wrong this
  morning, and three commits' worth of comments go with it.

Recorded because the second outcome is the valuable one and it is
exactly the outcome a reader who already believes the first would
explain away.

(Note: 56-59 is *already* excluded by p.18 alone — a single bit at
`.59` in a 56-59 field is one, not eight. So the prediction's real
job is to catch a field this project has not considered at all.)

### >>> CONFIRMED, AT `.61`, AN HOUR LATER <<<

Printed p.19, read at 600 dpi:

```
        LCI,$15,2.0
        SV,$15,0.0($3)            -YES * ENTER UST A[DDRESS]
        CM1111(BU,1),.61($3)      -SET UNIT COUNT TO [TWO]
        CM1111(BU,1),.27($3)      -MULIT BIT ON
        CM0000(BU,1),.29($3)      -MEANINGLESS ASG B[IT]
```

**`CM1111(BU,1), .61($3)`**, commented "SET UNIT COUNT TO [TWO]". A
single bit at `.61` in a four-bit field at 59-62 is `0b0010` = **2**.

So `SUNITK` = bits 59-62 now rests on **two pages writing two
different values into the same field at two different offsets** —
p.18's `.59` meaning eight and p.19's `.61` meaning two — and no
other field width makes both true. `.59`→8 needs the field to start
at 59; `.61`→2 needs it to end at 62. That is a stronger result than
the figure could have given on its own, and it came from a drawing
whose tick marks were too coarse to read.

**THE REST OF THE BAND CORROBORATES FIGURE 44 ROW FOR ROW**, which
is the other half of what this was for:

```
        BZX?,X 18 4               (the "IS EQUIPMENT DISK OR CONSOLE"
                                   test -- glyph not yet settled)
        LCI,$15,2.0               "SET UNIT COUNT TO TWO"
        ...
X18 2   BZB,.25($3),X18 3         -IF CHANNEL AVAILABLE
        CM1111(BU,1),.28($15)     -NO * THEN UN[IT ...]
X18 3   CM1111(BU,1),.29($15)     -YES * UNIT S[TATUS] ASSIGNED
        CB+,$15,X18 2             -IF PROCESSED [TWO ...]
        B,X17 1                   -RETURN FOR N[EXT CARD]
X18 4   BZB,.25($3),X18 5         -IF CHANNEL A[VAILABLE]
        CM1111(BU,1),.28($3)      -SINGLE UNIT STAT[US] AVAILABLE
X18 5   CM1111(BU,1),.29($3)      -AND TO NOT A[SSIGNED]
```

`B, X17 1` is p.18's `X171` — so p.19 returns into p.18 exactly where
Figure 44 says it does, and **pp.17, 18 and 19 are one loop**. The
`.25` tests are `SCHAVL`, the `.28`/`.29` writes are `SUNAVL` and
`SUNASG`, and `X184`'s single-unit arm writes them into **`($3)`, the
CST entry itself** rather than `($15)` — which is Figure 137's
"Channel Status Table Entry for Single-Unit Channel", where the
channel and unit indicators share one word. The two figures and the
two code paths line up.

## >>> THE IOCD CARD'S COLUMN FORMAT IS PRINTED, AND EVERY DERIVATION WAS RIGHT <<< 2026-10-21

`C22-6728` **printed p.88 = PDF p.88**, "The Initialization Program /
Control Cards". Found through that document's own INDEX — "IOCD CARDS
... 88" — which the back-matter sweep had revealed exists two hours
earlier. The index also lists, on the same page, "INITIALIZATION
PROGRAM", "INITIALIZING PROGRAM CONTROL CARDS" and "I-O STATUS TABLE
SETUP".

> "The IOCD cards, which do not have to be in order of channel
> number, have the following fixed fields:
> **Cols. 10-13 — Card Type: contains the characters, IOCD.**
> **Cols. 14-15 — Channel Number: contains the decimal number of the
> channel.**
> **Cols. 16-17 — Equipment:** must contain one of the following
> codes: CN Console, DK Disk, PR Printer, PU Punch, TP Tape, RD
> Reader"

**EVERY DERIVATION CONFIRMED, INCLUDING THE ONE THAT WAS LABELLED AN
INFERENCE.** The keyword field is four columns at 10-13 and the
keyword *is* the literal string `IOCD` — written up this morning as
"a strong inference rather than a derivation", resting on the field
being four columns at the keyword position plus line 13's "-IF ZONE
BIT OF IOCD" comment. It is printed. The channel is two decimal
digits at 14-15, matching the two columns p.17 converts separately.
The equipment code is **two letters** at 16-17, of which line 46
reads the **second**.

**AND THE PAGE EXPLAINS WHY ONE COLUMN IS ENOUGH**, which no amount
of reading p.17 would have given: the six codes' second letters are
**N, K, R, U, P, D — all distinct**. MCP never needs the first
letter. That is why line 46 reads twelve bits and not twenty-four.

**THE FIXTURE NOW PUNCHES A REAL CARD.** `gen_mcp_p17_tb.py` builds
an eighty-column line — `B`, blanks, `IOCD`, `35`, `TP`, a blank
availability column, then one column per unit — and runs it through
`strap/cards.py`, the same path `decks/` take to the 7503. Nothing in
it knows a bit address any more. Even the unit columns are text: a
punch in row 12 is `+` and a punch in row 0 is `0`.

Two things fell out of punching it. The channel digits read correctly
through MCP's own Hollerith conversion — `3` in column 14 gives a
left-zeros count of 3, `5` in column 15 gives 5. And **the 16-bit
units window comes out `0x0409`, not `0x0400`**, because it overruns
into column 16's `T` — *and the count is still 5*, because those bits
fall to the RIGHT of the punch. That was this morning's explanation
for why a 16-bit window can read a 10-row digit; it is now measured
rather than argued.

**ONE CORRECTION TO SOMETHING THIS FILE SAID TODAY.** `C22-6728`
printed p.90, **Figure 44 "The Initialization Program - Chart 1"**,
is the flowchart of printed pp.17-18, with the same label names —
`X131` "IS THIS AN IOCD CARD", `X19`, `X18`, `X171`. Its decision box
**"IS EQUIPMENT TAPE" goes to `X18` on NO**. So bit 29 of an
equipment-table entry means **IS tape**, not "not tape" as recorded
this morning, and the path p.18 transcribes is the TAPE path. The
fixture's VALUE was right and its NAME was backwards.

**THAT ALSO EXPLAINS THE EIGHT.** p.18 line 4 sets the unit counter
to eight and the loop walks up to eight unit columns; Figure 44's
`X18` branch, for disk and console, instead says "SET UNIT COUNT TO
TWO". A tape channel carries many units, a disk channel two. So the
card has to be `TP` for p.18 to be the page under test, which is now
why the fixture says so rather than an arbitrary choice.

**AND FIGURE 44 IS A MAP OF THE UNTRANSCRIBED PAGE.** `X18` leads to
"IS EQUIPMENT DISK OR CONSOLE", then "INSERT UST ADDRESS IN CST",
"SET UNIT COUNT TO TWO AND SET MULTI BIT ON, ASSIGN CHANNEL", "IS
CHANNEL AVAILABLE", "WERE TWO LOGICAL UNITS PROCESSED", and `X184`'s
own availability test — **that is printed p.19 in outline**, before
anybody transcribes it. Worth having beside the listing when that
page is done.

## THE IOCD CARD IS A HOLLERITH CONTROL CARD -- C22-6728 corroborates the geometry from outside MCP, 2026-10-21

The card stride and the card's field map were both derived from
pp.17-18's own progressive increments. That makes them two
derivations from **one** source, which is exactly the situation where
this project has been wrong before. C22-6728 printed p.215-216 is a
second source and it agrees on both.

**"Since information on the master tape is written in COLUMN BINARY
CARD IMAGE..."** — printed p.215. A column-binary card image is 80
columns of 12 rows read as bits: **960 bits = fifteen 64-bit words =
p.18 line 43's `V+I, $13, 15.0`.** Same number from opposite ends.

**AND EVERY FIELD OFFSET LANDS ON A CARD COLUMN.** Printed p.216
shows MCP's control cards with a tag in column 1 and the operation
field **starting in column 10** — "B ␣ HED, operation, ttaaaaaa,
LOAD", and the library control cards are "punched starting in column
10". Divide p.17's offsets by twelve:

| field | bits | column | |
|---|---|---|---|
| card type | 0, len 8 | col 1 | the tag field |
| IOCD identifier | 108, len 48 | **cols 10-13** | four columns = four characters |
| channel tens | 158, len 7 | col 14, rows 0-6 | the digit rows |
| channel units | 170, len 16 | col 15, rows 0-9 | the digit rows |
| equipment letter | 192, len 12 | col 17 | one column = one character |
| channel available | 204, len 1 | col 18, row 12 | a zone punch |
| unit entries | 216, 228, … | cols 19, 20, … | one column each |

**The identifier starts at column 10 and is FOUR COLUMNS LONG — four
characters, `IOCD`.** Nothing in p.17 says "column"; the number 12
never appears on the page. The map was read off `1.44`, `.48+.2`,
`.12`, `.22`, `.24` and comes out column-aligned anyway.

**AND IT EXPLAINS A COMMENT THAT PREVIOUSLY ONLY MADE STRUCTURAL
SENSE.** p.17 line 13 is `BB, 1.44($4)`, commented **"-IF ZONE BIT OF
IOCD"**. Bit 108 is column 10 row 12 — the zone row — and column 10
holds the first character of `IOCD`. The hunt finds a card by testing
the zone punch of a letter, and the letter is the `I`.

**WHY THIS MATTERS BEYOND BEING TIDY.** `gen_mcp_p17_tb.py`'s header
draws a hard line between DERIVED and INVENTED, and the INVENTED side
— the card's contents, X IOCD's pattern, the equipment table's
entries — is now carrying three test sections. This moves the card's
GEOMETRY across that line. The contents are still invented; the shape
they sit in is not.

**STILL OPEN: the IOD card's own printed column assignment.**
pp.215-217 are the UPDATE-30 writeup and do not carry it. Neither
revision of C22-6728 has a text layer, so finding it means working
from the table of contents and the index.

## pp.17 AND 18 RUN AS ONE PROGRAM -- the card LOOP, 2026-10-21

`tests/gen_mcp_p17_tb.py` now assembles **both** transcribed pages and
runs them against a synthetic IOCD card. p.18 starts at `(8)713.0`,
contiguous with p.17's last row at `000712.00`, and its last
instruction is `B, X131` -- back into p.17 line 26. They were always
one program. The run exits at `X 19`, the row whose own comment is
"X 19 IS THE NORMAL END": the loop ran out of cards.

**THE CARD STRIDE IS A PUNCHED CARD.** p.18 line 43 is `V+I, $13,
15.0`. Fifteen 64-bit words = 960 bits = 80 columns x 12 rows, one
IBM card as a bit image with nothing left over. The card's internal
field map was derived from p.17's increments; this is the number that
says where a card STOPS, and it is the first hard constraint on what
the IOD cards on the system tape have to look like.

**THE 29TH BIT OF AN EQUIPMENT ENTRY IS A TAPE FLAG, NOT A SPARE.**
p.17 lines 46-54 gave the entry as 24 bits of Hollerith letter + a
4-bit code + "1 spare". p.18 line 2 is `BZB, -.1($1), X18`, commented
"-TAPE EQUIPMENT TYPE ENTRY". `X18` is `(8)740.40` -- the empty low
half of p.18's last word, the first instruction of **untranscribed
p.19**. So p.19 handles tape units, and the second program to read a
structure has named the field the first one could only call spare.
Same principle as the PROSA dictionary's shape from printed p.4: the
code that reads a structure is a primary source for it.

**THE CST ENTRY IS NOW DERIVED ONE PRINTED LINE AT A TIME**, and the
generator reads as that list rather than as a hex constant:

| line | instruction | effect on the entry |
|---|---|---|
| p.17 l.22 | preset | bit 25 not available, bit 29 not assigned |
| p.17 l.44 | `CM0000(BU,1), .25($3)` | bit 25 off -- channel IS available |
| p.17 l.54 | `ST(BU,4)` | bits 52-55 = equipment code |
| p.18 l.5 | `SV, $15, 0.0($3)` | UST address into bits 0-23 |
| p.18 l.7 | `CM0000(BU,1), .29($3)` | "meaningless assign" bit off |
| p.18 l.9 | `CM1111(BU,1), .27($3)` | MULTI bit on |
| p.18 l.42 | `CM0000(BU,17), 0.0($3)` | X17 clears 17 bits of it again |

The last row needs its reason: p.18 line 32 compares `$15`'s count
against 8, line 4 had just SET it to 8, and this card carries no unit
entries -- so line 33's `BXE, X17` fires, the branch commented "NO
UNITS AT ALL ON MULTI CHANNEL". **A channel with no units gets no
unit status table, so MCP takes the table address back out of the
entry.** The third check in the testbench -- word 31, `$15`, still
holding the UST base and the 8 -- is the independent witness for
which way that branch went, because the entry's value depends on it.

**`SV` STORES THE VALUE *AND* ITS SIGN.** The first expectation put
the UST address one bit too low because I wrote the index value as a
single 25-bit field spanning bits 0-24. It is a 24-bit address at
bits 0-23 with the SIGN at bit 24. The measurement was off by exactly
2x, which is what a one-bit field-width error looks like and is worth
recognising on sight -- see the trap entry at the end of this file.

**TWO MEASURED INJECTIONS, both in the FIXTURE**, because
`decks/mcp_bootstrap_p18.strap` is checked bit-for-bit against the
listing and an injection into it would be testing a different page:

1. **Clear the tape flag** on the matched equipment entry. Observed
   PC 961 = 30752/32, the `X18` halt; the CST entry falls back to
   `0x400000600`; the UST counter word loses its 8. **That fallback
   value is exactly what this test asserted before p.18 was merged**,
   so the injection measures p.18's contribution as a difference.
2. **Remove the card's letter from the equipment table.** Observed PC
   182 = 5824/32 -- `X ERROR`, MCP's "WRONG EQUIPMENT CODE" exit --
   and the entry stops at `0x400000000`: available, no code, "not
   assigned" still standing, because p.18 never ran.

**AND THEN THE UNIT ARM WAS RUN THE SAME DAY**, as a second mode of
the same generator (`run_mcp_p17.sh StretchMcpP17UnitsTb units`).
**Every check passed on the first run, each predicted from the
listing before the simulator was built.**

**A UNIT IS A PUNCHED COLUMN**, and the increments say so twice over.
p.18 line 13 is `CT0011(V+I)(BU,12), .12($4)` — read twelve bits,
advance twelve — so a unit entry is twelve rows, one column. The card
stride confirms it from the other end: 80 × 12 = 960 = line 43's
fifteen words. Lines 16-17 test single ROWS of that column, ten and
twelve bits BACK from where the read left `$4`, and p.17's walk left
`$4` at card+216 — column 18. **A UST entry is one word**, derived
twice independently: X15 1/X15 2 write bits .27 .28 .29 .39 of
`($15)`, all inside one word, and `CB+` steps `$15` by "one in bit
position 17" = 64 bits.

**THE TWO UNITS ARE PUNCHED DIFFERENTLY ON PURPOSE.** The page's
comments read backwards against what X15 1 and X15 2 do: line 16 is
commented "-UNIT AVAILABLE" and branches to X15 2, which does NOT set
the bit the listing calls "UNIT AVAILABLE BIT ON". Punching both
units alike would measure nothing about that. Unit 1 takes the X15 2
route, unit 2 the X15 1 route, and the two UST words come out
differing in exactly bit 28 — the routing is a measurement, not a
reading of the comments. Same shape as the tens/units split that
caught the progressive-indexing misread.

**THIS IS THE RUN THAT EXERCISES THE UNSIGNED SUBTRACT.** Lines 34-37
are `LFI(BU,18), 8.0` / `-(BU,18), $15+.28` / `ST(BU,4), .59($3)`.
Two units leave the counter at 6 and the CST count field comes out 2.
`-(BU,18)` is the operation Figure 12 on printed p.61 caught this
week — every unsigned subtract was being done as an addition — and
the no-units mode *cannot* reach it, because `BXE, X17` jumps over
it. The two modes together are what make that repair tested by MCP
and not only by IBM's own worked example.

**`8.0` IS EIGHT, NOT 512.** The immediate assembles into the 24-bit
address field as `000010.00` (the deck header records it), and an
18-bit operand from that field's bits 0-17 is the WORD number:
512 >> 6 = 8. `$15+.28` has the same shape — word 31 bit 28, and
eighteen bits from there is exactly the count field. Worth pinning
rather than assuming: 512 would have given 512−6 = 506, whose low
four bits are 10, a number small and plausible enough to pass a
glance. **And the count field is bits 59-62**, from the pair of rows
that write it: line 37 stores FOUR bits at offset .59, line 30 sets
ONE bit at the same offset and is commented "UNIT COUNT IN CST TO 8",
and one bit at the left of a four-bit field IS eight.

**THE INJECTION IS p.18's OWN "IOCD PUNCHED INCORRECTLY"**, and it is
the first injection that reaches `X ERROR` from INSIDE p.18. Punch a
unit column on a row that is neither of the two the page tests; both
BBs miss and line 19's `SIC, XERRAD` / line 20's `B, XERROR` fire.
Observed PC 182 = 5824/32, UST entirely untouched, counter still 8.
(The equipment-table injection also halts at 182, but via p.17's
lookup, so it only proves p.18 was never entered — a reachability
control, not a test of p.18's logic.)

**AND IT CORROBORATED `SIC`'s FIELD RULE FROM MCP.** `X ERR AD` came
back `0x0074eaaaaaaaaaaa` over `0xAAAA...` fill — nineteen bits of
`000723.40` at the left, the rest undisturbed. Reference Manual
printed pp.41-42 has three clauses: the counter goes "in bits 0-18 of
the half-word", "other bits of the half-word are not disturbed", and
the stored value "always address[es] the instruction whose location is
next higher in storage than the branch instruction to which SIC is
prefixed". `XERR18` is at `000722.40`, its inner `B, XERROR` is the
right half at `000723.00`, and `000723.40` is `X15 1`. **All three
clauses in one word, measured from a 1963 program's error exit rather
than from a deck written to test it** — and it confirms in passing
that the assembler pairs `SIC` with the following branch into one
full word, which is how the listing's two source lines become one.

**AND THE EIGHT-UNIT ARM WAS CLOSED TOO, the same day: EVERY BRANCH
OF PRINTED p.18 HAS NOW BEEN EXECUTED.** A third mode, `units8`,
punches eight columns, so `CB+` runs the counter out, stops branching,
and falls into line 30's `CM1111(BU,1), .59($3)` — "UNIT COUNT IN CST
TO 8" — instead of lines 32-37's subtract.

**THE TWO ARMS WRITE THE SAME FIELD AND THE VALUE CANNOT TELL THEM
APART**: the subtract would give 8 − 0 = 8, exactly what line 30's
single bit gives. Worth stating plainly, because it is why the first
version of this test was **vacuous twice over**. Punching exactly
eight columns leaves two things that could have ended the loop — the
counter running out, or the ninth column being blank and line 14's
BRZ taking it — and nothing in the run separates them. So columns 9
and 10 are punched too, on row +0 so a loop that ran on would write a
UST word with bit 28 SET: visibly different from the eight before it
rather than merely present. "The ninth column was never read" is then
a measurement, and it is the only thing in either units run that
separates the two arms. **The cycle count is identical with and
without the extra punches — 20176 either way** — which is the same
fact from the other side.

**THE INJECTION BLANKS THE EIGHTH COLUMN**, so seven units are
punched and the BRZ, not the counter, ends the list. All three
observations moved together: the CST count field read **7**
(`0x...60e` not `0x...610`) — a value only the subtract can produce,
since line 30 can only write 8 — `$15` came out value +7 words with
counter remainder **1** rather than 0, and UST entry 7 was empty.
That is the pair of arms separated by measurement.

**A GENERAL LESSON ABOUT TERMINATION CHECKS**, worth the space
because this one nearly shipped vacuous: *"the structure past the
last element is untouched"* proves nothing when the input also ends
there. Two mechanisms can stop a loop — the data running out and the
counter running out — and a fixture that exhausts both at once
measures neither. Put data PAST the point the counter should stop at,
and make it data that would be distinguishable if it were consumed.


## `M+MG` IS BUILT, AND `OP` IS OUT OF THE INDICATOR WORD AGAIN -- 2026-10-19

ADD MAGNITUDE TO MEMORY, the VFL form (`abc101001`), is the seventh
arm of `StretchExecute`'s VFL integer case. Reference Manual printed
p.62 defines it in two sentences and Figure 13 on the same page
tabulates every sign combination; `decks/m_plus_mg.strap` transcribes
two of the table's rows and takes the other two cases from MCP's own
unsigned use, with **two measured injections** that land on different
checks (a real accumulator sign instead of a forced positive one puts
95 in T2; storing the sum unconditionally puts 512 in T3).

**NOT THE FLOATING-POINT `M+MG`** of printed pp.88-89, which has its
own opcode and its own thirty-two-sub-test deck from `jb_af1c` routine
F206B. Same mnemonic, different instruction, and the FP one has been
built for a long time.

### What found it

The console. MCP's error routine prints its diagnosis on the
operator's console and folds the failing instruction's address into
the message with two `M+MG(BU)` adds (printed p.5 lines 15 and 17).
With the operation refused, **the sentence came out right and the
address came out as the message's own placeholder, "000000.0"** --
a wrong number inside a correct diagnostic, which is exactly the
failure an end-to-end boot test with no field-level check would pass.

`tests/audit_opcode_coverage.py` could not see it and still cannot:
it compares what the assembler can EMIT against what some deck USES,
and says nothing about what the model EXECUTES. `+MG`, the
to-accumulator form, is still in that blind spot.

### One correction to an operation that already worked

Printed p.57's "Sign Control" settles where the negative sign modifier
(bit 52) lands, for the whole class rather than one operation: "if the
result is placed in the accumulator, bit 52 determines the use of the
sign of the operand from storage; **if the result is placed in
storage, bit 52 determines the use of the accumulator sign**", with a
four-row table under "TO-MEMORY OPERATION" spelling out all four
combinations. The model had been applying it to the storage operand
for `M+`. Corrected.

**The correction is inert and the comment says so.** Nothing in the
suite can reach it, because the VFL path of `strap_asm.py` has no
spelling for the negative sign modifier at all -- see the next item.

## THE CONNECTIVES LEARN BYTE SIZE -- and a good inference gets killed, 2026-10-19

**HALF CLOSED.** The connectives now do printed p.75's byte-size
expansion, which is what `LF(BU,21,3)` needs and what the model never
had. The console message receives seven octal digits where it used
to receive a smear -- but each one is exactly DOUBLED, and the
obvious fix for that turned out to be refuted by fifty-six sections
of IBM's own floating-point diagnostic. See below; the remaining
fault is in the reading of MCP's four instructions, not in the
model.

It took two things, both on Reference Manual printed p.75.

### The connectives are not a flat bit field

> "The connective operations process data in eight-bit bytes. In
> these operations, the byte size specified in the instruction
> designates the number of bits used to represent each character or
> symbol in the storage field. **If the byte size of the storage
> operand is less than eight, each byte is converted into an
> eight-bit byte before processing by the addition of high-order
> zeros.** The accumulator operand is assumed to have a byte size of
> eight. ... **Consequently, the result bytes always have a byte size
> of eight.**"

and, facing it:

> "In contrast to the integer arithmetic operations, the accumulator
> operand has a definite length; it is composed of as many bytes as
> there are in the addressed storage field."

So `LF(BU,21,3)` is seven bytes and **fifty-six** bits of accumulator,
not twenty-one -- which is exactly what MCP's own comment on that line
says: `-BREAK ADDRESS INTO EIGHT BIT BYTES`. The error routine
spreads seven octal digits into seven character positions so that two
`M+MG` can add them into an IQS string without carrying between
digits. `CONNECT TO MEMORY` contracts back the same way, dropping the
high-order bits of each result byte.

`StretchVFL`'s `connExpand`/`connContract` and
`decks/connective_byte_size.strap` (six checks, two injections).

**BYTE SIZE EIGHT IS BIT-IDENTICAL TO WHAT CAME BEFORE**, and that is
not a hope -- the deck's T5 asserts it and the `bsEff` injection
leaves T5 passing while four other checks fail. Every connective test
already in the suite uses byte size 8 and none of them moved.

### The offset is BITS -- a hypothesis the suite killed

This is the part worth reading, because the inference was good and it
was still wrong.

The connective offset was built as a **byte** offset, rounded down,
on three strands that all pointed the same way:

1. **p.75 admits it**: "Any offset may be specified and *the field is
   processed in eight-bit bytes starting with the offset*."
2. **p.57 states the exact analogue for decimal**, as a property of
   the machine rather than of the programmer: "the offset is limited
   to these digit positions and hence to a multiple of four by
   ignoring the two low-order bits of the offset specified by the
   effective address of the second half-word." Sixteen eight-bit
   bytes, three low-order bits.
3. **IBM's own code only works that way.** MCP's `LF` carries offset
   **1**; the two `M+MG` that consume its result carry 8 and 0, which
   want the seven bytes byte-aligned. Measured on the bootstrap,
   both ways:

   | offset | digits the console receives |
   |---|---|
   | taken literally | 0, 0, 0, **12, 12, 4, 8** -- every digit doubled |
   | rounded down | 0, 0, 0, 6, 6, 2, 4 -- the address |

**FIFTY-SIX SECTIONS FAILED.** All of `jb_af1c` and the PAU gates,
because the floating-point diagnostic checks every single result with
`CT0110(BU,60),ROS,4` -- a connective at **offset 4** -- and that
comparison needs the four bits honoured. IBM's own diagnostic
outranks a three-strand reading of the manual, and it says the offset
is bits.

The model, the deck's T6 and `run_tests.sh` all now carry the
refutation rather than the hypothesis, so that nobody rebuilds it.
T6 asserts the doubling and its injection is the rounding -- the
plausible wrong answer kept as the injection, which is the right
place for it.

### So MCP's console address is doubled, and that is the open question

Not the model's. The four instructions are printed p.5 lines 12-17:

```
X1 ERR  LF(BU,21,3),X ERR AD,1        -BREAK ADDRESS INTO EIGHT BIT BYTES
        LV,$2,.32($2)                 -GET ADDRESS OF MESSAGE
        M+MG(BU,48,8),.8+.8($2),8     -SKIPPING OVER CONTROL CODES
        M+MG(BU,8,8),.8+.48+.8($2)    -FORM HALF WORD PORTION
```

Seven eight-bit result bytes with their right end at bit 1 sit at
accumulator bits 1-56; the offsets 8 and 0 want them at 0-55. One bit
out, every digit doubled. Something in the reading of those four
rows is still wrong, and the offset is no longer a candidate.

**TWO OF THE FOUR CANDIDATES ARE ALREADY DEAD**, eliminated by
argument rather than by running anything, so do not spend a session
on them:

* **Not the field decode.** `LF`'s printed second half-word
  `025300.46 70` decodes to length 21, byte size 3, offset 1 against
  the connective format diagram on p.75 (identical to the integer
  one: ADDRESS 0-23, `1000` 24-27, I 28-31, P 32-34, LENGTH 35-40,
  BS 41-43, OFFSET 44-50, CONN 51-54, OP 55-59, I 60-63), and all
  fifty-three machine-code rows of pp.5-6 already match bit-exactly.
  The offset really is 1.
* **Not `SIC`'s alignment in `X ERR AD`.** A different alignment
  would change WHICH three-bit groups become digits, i.e. it would
  print different digits. The fault is that every digit is exactly
  **doubled**, which is a one-bit left shift of the whole 56-bit
  result -- a placement fault, not a value fault.

**AND THERE IS NO LISTING ORACLE TO FIND.** Every connective in the
transcribed corpus uses byte size 8 except MCP's own `LF(BU,21,3)`
and the one `CM0101(BU,21,3)` in this project's own deck -- checked
by grepping all 258 decks. So the expansion rests on p.75 alone
(verbatim, which is enough) and the offset question cannot be
settled from `decks/`. If a listing oracle exists it is in a
diagnostic page nobody has transcribed yet; `jb_ax5b` routine 1246
("modifiers") is the first place to look.

Worth checking next, cheapest first:

* **The second `M+MG`'s target, which may be working as designed.**
  `.8+.48+.8` is 64 bits, which in a normal two-control-code message
  is byte 8 -- the `.` of the slot `000000.0`, not its last digit at
  byte 9. Printed p.11 confirms the slot is exactly eight characters
  (line 46 at `000440.10`, line 47 at `000441.10`, one word apart).
  But note what that produces in the ordinary case: `X ERR AD` holds
  "LOCATION OF ERROR +1.0", and for a WORD-aligned address the
  seventh octal digit is 0, so `.` + 0 is still `.` and the console
  prints `nnnnnn.0`. The seventh digit only damages the point when
  the failing instruction sits at a half word. **IBM may simply have
  accepted that**, in which case this instruction is not a fault at
  all and the doubling is the only thing left to explain.
* **The offsets are not a consistent family, and that is a clue.**
  If everything were simply shifted one bit, `LF`'s 1 would pair
  with `M+MG` offsets of 9 and 1. MCP has 1, 8 and 0 -- the two
  `M+MG` are byte-aligned and only the `LF` is not. Whatever the
  explanation is, it has to account for that asymmetry.
* **Or MCP is simply wrong here, for the second time in this
  routine.** It is the ERROR routine -- the least-exercised path in
  any system -- and it already contains one defect this project has
  confirmed from the listing, the `X MS 16C` message whose missing
  `RED` code puts the digits a byte late. A doubled address in a
  message nobody read carefully is the same kind of defect. **This
  is a hypothesis of last resort and must not be reached for
  early**: the first three bullets are cheaper and one of them being
  right would be much more useful. But it is on the list, because
  "IBM's code is correct" is an assumption, not evidence, and this
  file has already recorded one place it failed.

### And the message is still one byte out -- faithfully

`X MS 16C` has only a carriage return where every other message in
the table has `CR` then `RED` (printed p.11 lines 44-48; the slot
starts at `000440.10`, byte ONE). MCP's error routine skips two
control codes unconditionally (printed p.5 line 15's address field is
`000000.20`). So this one message gets its digits a byte late, over
the ".". **A real 7030 running this tape would have printed it the
same way**, and `tests/gen_mcp_boot_tb.py` now checks for exactly
that, every byte accounted for.

The detail below is kept because it is the part worth re-reading: the
reasoning that looked like two model bugs and turned out to be one
model bug, one reading error, and one bug of IBM's.

---

## `K` AND A NONZERO OFFSET -- noticed while building `KF`, not chased

Reference Manual printed p.65, COMPARE:

> "The contents of the accumulator **left of the specified offset**
> are algebraically compared with the addressed operand. **The bits
> to the right of the offset do not participate in the comparison.**"

The model does it the other way round: it shifts the OPERAND left by
the offset and compares against the whole accumulator
(`smCompare(acc, opndSh)`). The two agree whenever the accumulator's
low `offset` bits are zero, and differ otherwise -- if the high parts
are equal and the low bits are not, the manual says AE and the model
says AH.

**Not touched, deliberately.** `K` is exercised by several hundred
listing-verified sections, every one of which passes, so either they
all use offset 0 or they all have zero low bits; a change made blind
could only be justified by a deck that fails first. Writing that deck
is a half-hour and the fix is one line, but it wants its own commit
and its own injection rather than riding along with `KF`.

The same page also says "Neither the lost carry nor the partial field
indicator can be turned on by a comparison operation" -- worth
checking against the arm while you are there.

## WORD 7'S CONNECTIVE COUNTS ARE BUILT — 2026-10-20

> **CLOSED the same day it was found.** `boot_plan.md` A2a is done.
> `decks/connective_counts.strap` is in the suite with six checks and
> one injection.

### What it was, and why `LCV` alone was not enough

Closing A2 did not make MCP's printed p.17 run. Lines 32-36 convert
an IOCD card's channel number out of Hollerith:

```
X132    CT0011(V+I)(BU,7), .12($4)   -TEST TENS POSITION OF CHANNEL
        LCV(DU,8,4), $LZC+.3, 46     -CONVERT TO OCTAL NUMBER
X132AA  CT0011(V+I)(BU,16), .22($4)  -TEST UNITS POSITION
        +(BU,4), $LZC+.3, 46         -FORM CHANNEL NUMBER
```

`$LZC` is word 7 bit 17, **the left-zeros counter**. A Hollerith
digit is one punch among several rows, so CONNECT FOR TEST over the
column leaves *the digit itself* as that count, and the two reads of
`$LZC+.3` are how MCP gets the tens and units. The model did not
implement the counters, so the sequence converted nothing.

Printed p.75 gives both counters and their positions; p.76 gives the
field each is taken over — byte size eight for `C`/`CT`, the
contracted field for `CM` — and notes they are positioned to be used
as index values, which is exactly what MCP does. The all-zero case is
the one thing the page does not state and is labelled as an inference
in both the model and the deck.

### THE SCHEDULING TOOK TEN ATTEMPTS, and the answer is one sentence

**`writeWord` does not write word 7's counter fields at all.**

Routing the counters through `writeWord` makes *every* connective a
scheduling conflict, because a `CONNECT TO MEMORY` stores its result
through a **dynamic** address in the same arm and bsc cannot see that
the address is not 7. Nine arrangements each moved the conflict
rather than removing it, and they are worth listing so nobody walks
back into them:

1. a second `writeWord` in the connective arm — the register against
   itself;
2. a `mkCReg` plus a dedicated method — port-0 write against port-1
   read;
3. word 7 split into five fields so the counters have their own
   CRegs — port-0 write against port-1 write;
4. ports swapped to match the case-arm order — port-0 read against
   port-1 write;
5. reads moved to port 1 — a **combinational cycle**, `rl_prepare`'s
   condition depending on its own firing through a look-ahead level;
6. counts set before the store instead of after — same conflict;
7. the write threaded to a single call site after the case — same
   conflict, because `connectiveOp` is its own `actionvalue`
   function;
8. threaded out through `VflOutcome` and written by the caller —
   same conflict again;
9. an explicit `schedule (writeWord) SB (setConnectiveCounts)` —
   not a statement in this dialect — and then
   `(* conflict_free = ... *)`, which must attach to a declaration
   and has none to attach to at the end of a module.

**Giving each counter exactly ONE writer removed it.** The cost is a
documented simplification: a program storing to word 7 changes the
other fifty bits and leaves the counts alone. The manual makes
location 7 an ordinary addressable word, so this is a departure — but
it is the same one this model already makes for the indicator
register, where `writeWord(11)` is a no-op and the write is folded in
elsewhere, and nothing in the corpus stores to word 7. MCP reads it
and never writes it.

**The general lesson, which is not about word 7:** when two writers
to one piece of state cannot be scheduled, the fix is usually to
remove a writer, not to re-arrange the ports. Eight of the nine
attempts above were port arrangements.

## TWO CORRECTIONS TO THINGS THIS SESSION ITSELF CLAIMED, 2026-10-19

Both were caught by checking the repo rather than by a test, and both
are the same failure: announcing that a document supplies something
the project had already worked out.

### `C22-6728` p.215's 513-word record was NOT a new constraint

It was recorded here and in `boot_plan.md` as "a constraint on the
PROSA fixture that arrived after the fixture was built", and as
something `strap/prosa.py` "does not model".

**`decks/mcp_bootstrap_p14.strap` derived 513-and-512 from MCP's own
chained control words**, one-word header included, and
`strap/prosa.py`'s header already cites that derivation and explains
that the fixture is deliberately shorter than one chunk. What p.215
genuinely adds is an independent second witness plus three facts the
derivation could not give: two binary FILES (hence the tape mark
printed p.3 only implied), odd parity and high density, and that each
record is an image of a disk ARC — which ties the 513 to `arcWords =
512`. Three sources, one number. `mcp_tape_manufacture.md` §2.0 has
it in full.

### `D*N` is not an assembler gap

Reported as "the floating-point analogue of exactly what Figure 14
settled for VFL", on the grounds that `strap/opcodes.py` has `D+`,
`D+MG`, `D*` and `D/` but no `D*N`. It does not need one.
`strip_fp_sign`'s suffix loop handles `N`/`A`/`NA` for anything in
`FP_CODES`, and `D*N(N)` assembles today — verified, and it differs
from `D*` by exactly the invert bit. `D*A`, `D+N`, `LN` and `SRTN`
assemble too. **Nothing to build.**

The general rule both of these want: **before recording that a
document supplies something new, grep the repo for the number.** The
PROSA derivation was in two files, one of them the very fixture being
criticised.

## THE `N` SUFFIX IS BUILT -- the last item `M+MG` left open, 2026-10-19

> **CLOSED.** C22-6531 Appendix A footnote 4 gives VFL operations the
> suffixes **I** Immediate, **N** Negative, **NI** Negative Immediate,
> and that footnote was already transcribed in
> `docs/c22_6531_appendix_a.md` — the standing lesson once more.
>
> **The objection that blocked it was real and is now answered.** The
> item said a blanket "strip a trailing N" rule would capture `LN`, a
> real floating-point operation. That is true of a rule at the top of
> `classify_vfl_or_fp`, and the `-MG` rewrite was written there first
> and did exactly that, costing four sections of `jb_af1c`. The strip
> now happens **inside the VFL branch**, after the data description
> has already returned the floating-point modes `N` and `U`, so
> `LN(U,...)` never reaches it and `LN(BU,...)` is a real VFL LOAD
> with the negative sign modifier — which is what footnote 4 says it
> is.
>
> **Witnessed in use**, not merely described: Reference Manual printed
> p.64, Figure 14 writes `STN(B, 24, 8)` and `STN(BU, 16, 8)` — a VFL
> data description on a VFL operation. `decks/fig14_sign_modifiers.strap`
> runs the whole figure at IBM's own addresses and reproduces all four
> of its notes, with one injection.
>
> The model side had been built and right since the `M+MG` work
> (printed p.57's "Sign Control" table, TO-MEMORY column); it was
> inert only because nothing could spell the modifier. It can now.

## IBM'S WORKED EXAMPLES ARE AN UNDER-USED ORACLE -- two run, two finds

Not a diagnostic listing and not prose: a *Figure* in the Reference
Manual that states a problem, gives the statements, and says what
each one leaves behind. A diagnostic exercises the corners; a worked
example exercises the path the manual expects a programmer to take,
which is where a model's unexercised defaults live.

Two have been run and both found something:

* **Figure 12, printed p.61** ("put the larger of x and y in the
  accumulator") would not run: `-MG(BU,64,8)` computed x PLUS y.
  `fieldToSM` returned sign 0 for every unsigned field and dropped
  the negative sign modifier, so **every unsigned subtract in the
  model was an addition**. Nothing in 419 sections could have caught
  it — only one deck in the corpus spells an unsigned written-minus,
  on a page MCP has not reached.
* **Figure 14, printed p.64** (A−B, |A−B|, −|A−B|, Ā−B) settled the
  `N` suffix above, and caught its own transcriber: `L(BU,24,8)`
  against a page printing `L (B, 24, 8)`.

**THE SWEEP HAS BEEN DONE, 2026-10-19** — all 175 pages of the
Reference Manual, all 82 of `C22-6578`, all 135 of `R23-9694` (CE
Introductory Programming Vol. 2), rendered and looked at, because
none of the three has a list of illustrations. The census:

* **The Reference Manual has 49 numbered figures, of which 13 are
  programs**: 7, 8, 9, 10, 12, 14, 15, 17, 18, 19, 21, 28, 29, 31,
  33. Figures 12 and 14 are done. Figure 13 (p.62) and Figure 30
  (p.101) are tables, not programs. The other 34 are bit layouts,
  truth tables, timing diagrams and photographs.
* **`C22-6578` has 44 problems**, 1.1–1.9, 2.1–2.12, 3.1–3.10,
  4.1–4.13, plus appendices A1–A8. Nearly all are runnable.
* **`R23-9694` printed pp.35–134** carries worked blocks per
  instruction; pp.5–34 have none, and the chapter says so.
* **NEGATIVE, so nobody re-sweeps**: Reference Manual printed
  pp.105–170 (the Exchange, External Units, Disk and Appendix
  chapters) contain **zero** program examples, and `C22-6578`
  appendices A1, A2, A3, A7 and A8 contain no runnable code.

**AND A CORRECTION TO THIS FILE, which had recorded a feature
request as coverage.** The sentence here used to end "mined only for
Problems 2.1, 2.2 and 4.5". **4.5 was never mined.** There is no
`problem_4_5` deck — only `problem_2_1` and the three `problem_2_2`
methods exist. 4.5 appears solely in `resuscitation_roadmap.md` as
*evidence* that word 7's left-zeros/all-ones counts are used, and it
could not be a test today in any case: it is built on `$AOC`/`$LZC`,
which are unimplemented.

---

## HOW THE CONSOLE ADDRESS WAS WORKED OUT -- the record, 2026-10-19

Kept because the reasoning is the useful part. Three faults were
visible in one run and the first two attributions were wrong: what
looked like two model bugs was one model bug (the byte expansion),
one reading error of mine (the field placement), and one bug of
IBM's (`X MS 16C`'s missing RED code). The sections below are as
they were written while it was still open; the resolution is above.

### (b) `LF`'s BYTE SIZE -- does a connective expand bytes?

**This is the live one, and it is what stands between MCP and a
correct error message.**

Printed p.5 line 12 is `LF(BU,21,3), X ERR AD, 1` and its own comment
is `-BREAK ADDRESS INTO EIGHT BIT BYTES`. The field is **21 bits with
byte size 3** -- seven 3-bit bytes -- and the two `M+MG` that follow
read **48 and 8 bits with byte size 8**, which is seven 8-bit bytes.
Seven octal digits, seven IQS character positions, `nnnnnn.n`. For the
arithmetic to work byte-wise without carries the digits must each sit
in their own 8-bit byte (IQS "0" is 0x60, and 0x60+7 = 0x67 does not
carry), so **the connective must expand three-bit storage bytes into
eight-bit accumulator bytes**.

The model's accumulator is a flat bit vector and does no such thing.

Printed p.57 argues both ways for INTEGER operations -- "the entire
contents of the accumulator are treated basically as a unit", but "in
decimal operations, the accumulator is treated as 32 four-bit digit
positions", which is itself a byte-size-dependent reinterpretation.
`LF` is a **connective**, not an integer operation, so the deciding
source is the connective section.

**READ, 2026-10-19: printed p.75, under the heading "Byte Size", and
it says exactly what MCP's comment says.**

> "The connective operations process data in eight-bit bytes. In
> these operations, the byte size specified in the instruction
> designates the number of bits used to represent each character or
> symbol in the storage field. **If the byte size of the storage
> operand is less than eight, each byte is converted into an
> eight-bit byte before processing by the addition of high-order
> zeros.** The accumulator operand is assumed to have a byte size of
> eight. Any offset may be specified and the field is processed in
> eight-bit bytes starting with the offset. Each byte of the storage
> field, after conversion to eight-bit form if necessary, is combined
> with an eight-bit byte from the accumulator according to the
> specified connective. **Consequently, the result bytes always have
> a byte size of eight.** In CONNECT, these result bytes replace the
> accumulator field which participated in the operation."

and, on the facing column of p.75:

> "In contrast to the integer arithmetic operations, the accumulator
> operand has a definite length; it is composed of as many bytes as
> there are in the addressed storage field."

So `LF(BU,21,3)` is seven 3-bit storage bytes, each zero-extended to
eight bits, written as seven 8-bit accumulator bytes -- 56 bits of
accumulator from 21 bits of storage. That is the expansion, stated,
and the model does not do it.

The same page carries the reverse rule for CONNECT TO MEMORY (each
result byte is truncated to the storage byte size, high-order bits
dropped, "no indication is given if the bits which are dropped are
significant"), the short-last-byte rule, and the PF (Partial Field)
indicator for a storage field that runs off the left end of the
accumulator. Figure 20 on printed p.76 confirms connective 3 is `m`,
the memory bit -- so `LF` is a plain copy.

**ONE THING STILL DOES NOT ADD UP, and it should be settled before
building.** MCP writes `LF(BU,21,3), X ERR AD, 1` -- OFFSET 1. Seven
eight-bit result bytes at a right end of bit 1 occupy accumulator bits
1-56, but the two `M+MG` that consume them use offsets 8 and 0, which
want the bytes byte-aligned at bits 0-55. One bit out. Either the
offset means something here that p.56's "number of bits by which the
right end of the accumulator operand is offset" does not cover (the
decimal rule on p.57 ignores the low two bits of the offset; no such
rule is stated for connectives), or the message's own layout absorbs
it. The encoding is not in doubt -- all 53 machine-code rows of
pp.5-6 matched bit-exactly -- so this is a reading question, not a
transcription one. **Settle it by measuring: dump the console image
and the message table words around `$X2` and see where the bytes
actually want to go.**

### And the apparent second fault is not the model's -- it is MCP's

The first `M+MG`'s 48-bit field landed at bits 16-63 of the message
word rather than 8-55: the "." at byte 7 moved and byte 1 did not.
That looked like a placement bug. **It is not. Both halves were
checked against the printed listing and the model is faithful.**

* Printed p.5 line 15 is `M+MG(BU,48,8),.8+.8($2),8` and its binary
  output is `000000.20 82  060004.22 90`. The address field
  `000000.20` is **16 bits** -- two eight-bit control codes, which is
  what "SKIPPING OVER CONTROL CODES" means. Line 17 is
  `.8+.48+.8($2)` printing `000001.00`, i.e. 64 bits, byte 8.
* Printed p.11 lines 44-48 are `X MS 16C`, and they are:

  ```
  44*  000440.00+  +00000000  NULL  X MS 16C  SYN,$
  45*  000440.00        375    DD(BU,8),(2)1111 1101   -CONTROL CODE * CARRIAGE RETURN
  46*  000440.10               (IQS*)DD(BU,64,8),000000.0*  -SLOT FOR ERROR ADDRESS
  47*  000441.10               (IQS*)DD(BU,64,8), NO IOCD CARD DETECTED*
  48*  000443.70        376    DD(BU,8),(2)1111 1110   -CONTROL CODE * END OF MESSAGE
  ```

  **There is no RED code.** The address slot starts at `000440.10`
  -- bit 8, byte ONE -- where every other message in the table has
  `CR` then `RED` and starts its slot at byte TWO (`X MSG 17`, four
  lines further down, prints `000444.00`, `000444.10`, `000444.20`).

So for this one message the error routine writes the address one byte
late, over the "." and into the text. **A real 7030 running this tape
would have printed it the same way**, and the deck had already
transcribed the missing RED code correctly without anyone noticing
what it meant.

**BUT DO NOT CLOSE THIS AS "IBM'S BUG" YET**, because the second
`M+MG` does not fit that story. In a normal two-control-code message
the slot occupies bytes 2-9 as `0 0 0 0 0 0 . 0`, the first `M+MG`
covers bytes 2-7 (the six digits, correct), and the second targets
**byte 8 -- the "."**, not byte 9. So under the tidy reading the
seventh digit overwrites the decimal point in *every* message, which
makes the point decorative and the slot's trailing `0` dead. Under
the `X MS 16C` layout it is the other way round: the second `M+MG`
lands exactly on the last digit and the first is the one that is
late.

Two readings, each of which makes one of the two instructions right.
That is the shape of a misreading, not of a bug. The template string
`000000.0`, the two offsets `.8+.8` and `.8+.48+.8`, and the `LF`
offset of 1 all have to be made to agree at once.
**AND THE LENGTH CHECK COULD NOT HAVE CAUGHT IT EITHER WAY**, which
is worth writing down because §6g advertises that check as the thing
that fixes these pages. `X MS 16C` is 32 bytes without the RED code
and `CNOP` adds nothing to an already-aligned entry, so the next
label lands at `000444.00`; with a RED code it would be 33 bytes,
`CNOP` would pad to the half word and lay a NOP, and the next label
would land at... also a whole number of words away. The delta does
not discriminate here. The *printed row* does.

### What the fixed message should say, and the offset that does not add up

> **SUPERSEDED.** The target value below (`w3 = 0xfd60606066666274`)
> assumes the tidy layout -- slot at bytes 1-6 -- and that is the
> reading this section itself goes on to disprove. The checked value
> is `w3 = 0xfd60606060666676`, digits at bytes 2-7, in
> `tests/gen_mcp_boot_tb.py`. Do not re-derive from the number
> below; the offset question is answered at the top of this file.


`tests/gen_mcp_boot_tb.py` carries the derived target. X ERR AD is
869 = `000662.40`, so LF's 21 bits are 3476 = octal `0006624`, and
the seven digits are `0 0 0 6 6 2` then `4`. Written one byte late,
as MCP writes them, that is bytes 2-7 of the message word and byte 8:

    w3 = fd 60 | 60 60 60 66 66 62      <CR> 0 | 0 0 0 6 6 2
    w4 = 64 ...                          4 ...

i.e. `<CR>0000066 2 4...` on the console -- the leading `0` of the
slot untouched, the "." overwritten. **Verify against that, not
against the tidy `000662.4` the slot was drawn for.**

**ONE THING STILL DOES NOT ADD UP.** `LF(BU,21,3), X ERR AD, 1` has
OFFSET 1, confirmed by decoding its own printed second half-word
(`025300.46 70` gives length 21, byte size 3, offset 1). Seven
eight-bit result bytes with their right end at bit 1 sit at
accumulator bits 1-56, but the two `M+MG` that consume them use
offsets 8 and 0, which want the bytes at bits 0-55. One bit out, and
one bit out halves every digit. Printed p.57 states exactly this kind
of rounding for DECIMAL operations -- "the offset is limited to these
digit positions and hence to a multiple of four by ignoring the two
low-order bits of the offset" -- and an analogous rule for
connectives (ignore the low three bits, offset to a multiple of
eight) would make MCP's code work exactly as written. **No such rule
is stated on p.75 or p.76.** Find it, or find why it is not needed,
before implementing the expansion: two independent off-by-ones in
four instructions is much more likely to be a misreading than two
bugs.

The two console words that currently hold the wrong bytes are
**deliberately not checked**, because freezing the output of a bug
that is not yet explained would mean the fix changes the expectation
again with nothing to say the new value is right.

## MCP'S BOOTSTRAP IS NOW REFUSED NOTHING -- LVS and TRANSMIT both built

> **CLOSED 2026-10-19.** `LVS` is built: `StretchExecute`'s
> immediate-index arm has a `4'b1011` case, driven by
> `decks/lvs_multiple_indexing.strap` (five checks, one per rule on
> printed p.28). With it and the multi-word `TRANSMIT` of the day
> before, **"MCP'S OWN BOOTSTRAP RUNS" reports no OP bit at all** --
> the model refuses nothing MCP executes, which is the claim that
> file made for weeks while actually measuring a register an
> interrupt had just cleared.
>
> What remains in the indicator word is `RZ | XVZ | XF | AD`, all
> four attributed in `tests/gen_mcp_boot_tb.py`, and the AD is the
> **tape** being short rather than the model being wrong: no PROSA on
> it means the TRANSMIT's count comes back zero, which printed p.30
> calls "never valid", and the transmit stops at the top of installed
> core exactly as that page describes.
>
> **So the next thing is not an instruction.** It is a tape with
> PROSA on it -- `docs/boot_plan.md` M3+ item 6 -- because until MCP
> has something real to move, every later page is being exercised
> against zeros.
>
> The section below is kept as the record of how the two gaps were
> found, which is the part worth re-reading: an exact indicator
> assertion caught both, and the first attribution was wrong because
> fixing one left the bit standing.

## THE NEXT MCP BLOCKER IS **LVS** -- TRANSMIT was built the same day

> **CORRECTION, 2026-10-18, same day.** This section was written
> saying OP came from the TRANSMIT on printed p.4 line 28. That was
> true and INCOMPLETE: **two** instructions on that path are refused,
> and fixing the first left the bit standing.
>
> `TRANSMIT` is now built -- multi-word, forward, immediate or direct
> count, `decks/transmit_multiword.strap`, fifteen checks -- and MCP's
> boot still reports OP. The remaining source is **printed p.4 line
> 23**:
>
>     X9 A 4 ... LVS,$X1,$X12,$X14      -WORDS PRECEEDING MCP
>
> `StretchExecute`'s immediate-index arm still ends
> `default: ind = setOpInvalid(ind); // LVS: out of scope`, and a
> four-line scratch deck reproduces it on its own. The ASSEMBLER
> gained LVS earlier (the participation mask, shifted left three);
> the MODEL never did.
>
> **It matters more than it looks.** `$X1` is the index the TRANSMIT
> two rows later uses to find MCP inside the buffer -- "WORDS
> PRECEEDING MCP" -- so even with TRANSMIT built, the move would copy
> from the wrong place. Reference Manual printed p.28, "Multiple
> Indexing", is the source, and the ENCODING is already pinned:
> `tests/verify_lvs_encoding.py` is in the suite.
>
> **THE SPECIFICATION, READ FIRST-HAND** -- printed p.28 (PDF p.31),
> "Multiple Indexing" and "Load Value with Sum (LVS)", both complete
> on that one page:
>
> > "In multiple indexing, bits 0-15 of the address part of the
> > instruction are used to indicate which index registers
> > participate in the operation. When bit position n contains a one,
> > the register Xn participates. When bit position n contains a
> > zero, the register Xn does not participate. **Bits 16-19 of the
> > address part of the instruction are ignored.**"
>
> > "The index field J contains the address of the index to which the
> > operation LOAD VALUE WITH SUM applies. **No address modification
> > is available for this operation.**"
>
> > "The address parts, bits 0-24, of the index registers which
> > participate are added and replace bits 0-24 of the index word
> > specified by J. The addition is algebraic, taking into account
> > the sign, bit 24, of all quantities. **Bits 25-63 of the index
> > word specified by J remain unchanged.** If bits 0-15 of the
> > address part of the instruction are all zero, the value field of
> > the index register specified by J is cleared."
>
> > "The index flag and index result indicators are set according to
> > the new contents of the index register specified by J."
>
> So the whole operation is: take the mask from the instruction's own
> address bits 0-15, sign-magnitude-add the value-plus-sign of every
> participating Xn, write bits 0-24 of index J and **leave 25-63
> alone**, and fold the index result indicators -- which
> `setIndexResultIndicatorsF` and `smAdd` already do for every other
> index operation. No indexing of the instruction itself, no count,
> no refill.
>
> **ONE THING TO WATCH:** the prose says bits **16-19** are ignored
> and the figure on the same page draws ADDRESS as bits 0-18 with J
> at 19-22. The two disagree about bit 19 and this repo has already
> recorded the conflict once. The assembler resolves it by shifting
> the mask left three, and `tests/verify_lvs_encoding.py` is what
> says that reproduces real listings -- so follow the assembler, not
> either reading of the page, and say so in the code.
>
> The rest of this section is kept as written, because the TRANSMIT
> half of it is the record of what was built.

## THE NEXT MCP BLOCKER IS TRANSMIT, found 2026-10-18

**MCP's IPL is never moved.** Printed p.4 line 28 is

    X9 A 5   T,11,X BUFER($X1),X BS END      -MOVE MCP IPL

and `StretchExecute.bsv`'s Transmit arm executes exactly one shape --
a ONE-WORD IMMEDIATE-count forward transmit -- and sets Operation
Code Invalid on every other, "conservative by construction" in its
own comment. An eleven-word transmit is every other. So the
instruction that copies MCP proper into place is refused, every time,
and has been since the bootstrap first ran.

**HOW IT STAYED INVISIBLE, which is the part worth keeping.** The
"MCP'S OWN BOOTSTRAP RUNS" section asserted the indicator register
exactly, as a ratchet, and it read `0xA040` -- three ordinary result
indicators and a clean OP bit. That value was an ARTIFACT:

1. Printed p.4 line 29 is `REL(SEOP),0.0($X0)` -- RELEASE **DISK**,
   channel zero. With no disk installed the model rejected it with
   Unit Not Ready.
2. Line 30's `BUNRJ,X ERR 12` then branched to printed p.15's
   `X ERR 12`, which is OUTSIDE the loaded image.
3. The machine ran into zeros. A zero half-word is BRANCH ENABLED,
   which enables the interrupt system with UNRJ pending.
4. The interrupt was taken and **reset the indicator register**.

So the test was measuring the register after an interrupt had wiped
it. Giving channel 0 a disk removed step 1, and the first thing that
appeared was the OP bit that had been there all along.

**Localised by bisecting the step cap** (no OP at 3.5M steps with the
PC at 000051.40, OP at 4M) **and then reproduced in four lines**, so
this is measured. The scratch deck was `T,11,SRC($X1),DST`; it sets
OP on its own.

**THE SPECIFICATION, READ FIRST-HAND.** Reference Manual **printed
p.30** (PDF p.33), "Data Transmission" -- one page, complete, and it
makes the job smaller than it looks. Verbatim:

> "Up to 2^18 - 1 (262,143) full words may be transmitted in one
> operation."

> "Bits 55-57 of the data transmission instructions are used as
> modifiers... modifier bit 57. A zero specifies unidirectional
> transmission; a one specifies bidirectional... modifier bit 56. A
> zero specifies a direct count; a one specifies an immediate count...
> modifier bit 55. A zero specifies forward transmission; a one
> specifies backward transmission."

> "In direct count operations, the field J, bits 51-54, specifies an
> index register. The count field, bits 28-45, of the index word in
> this register is used as a full word count. A count field of zero
> is interpreted as 2^18. Since this many words cannot be transmitted
> without encountering an invalid address, such a count is never
> valid. It is not detected, however, until the data transmission
> actually encounters an invalid or protected address."

> **"The count field in the index register is not changed as a result
> of the operation, and the index result indicators are not affected.
> A zero J field refers to location 16, X0."**

> "In forward transmission, the sending and receiving addresses of
> each successive word transmitted are obtained by incrementing the
> previous addresses by one. The starting addresses specified in the
> instruction are therefore the addresses of the first word in each
> of the two storage areas."

> "Only 18 bits of each effective address are used."

**THAT BOLD PARAGRAPH IS THE WHOLE SAVING.** A multi-word TRANSMIT
does **not** count the index register down and does **not** touch the
index result indicators, so the FSM needs no write-back path and no
indicator fold -- it reads the count once and walks two addresses.
And `J = 0` is X0, not "no index": a direct count really does read
word 16.

**What building it means.** The model writes one word per rule, so it
needs a small FSM of the `ioPending` shape -- the machinery `rl_io`
already has, applied to a memory-to-memory copy: read the source
word, write it to the destination, increment both, decrement a local
remaining. `StretchExecute`'s Transmit arm currently never reads the
index register at all, which is why every direct count sets OP.

**Scope to leave out, deliberately:** backward transmission and SWAP.
MCP's p.4 line 28 is forward unidirectional with a direct count, and
the two-source interchange SWAP needs is a different shape. The arm's
existing refusal should stay for both, with the OP it already sets.

**It is on the critical path and the disk is not.** The disk is
built; MCP LOCATEs and WRITEs it. What MCP cannot do is move itself
into storage.

**BUILT, 2026-10-18.** `XmitXfer` in `StretchTypes.bsv`, the count
read in `StretchExecute`'s Transmit arm, and `rl_xmit` in
`StretchCore.bsv` -- rl_io's shape with the device taken out.
`decks/transmit_multiword.strap` pins all five of p.30's rules
including "a zero count field indicates the maximum count of 16 full
words" and the ascending per-word order (a block shifted DOWN by one,
which only survives if the words move in order).

**AND THE ADDRESS-INVALID CHECK IN rl_xmit IS LOAD-BEARING, which is
worth knowing before anyone simplifies it away.** MCP's own transmit
takes its count from a PROSA dictionary, and the test tape has no
PROSA on it, so the count field is zero -- which p.30 says means 2^18
and "is never valid". 2^18 words is the WHOLE 18-bit address space:
the first version of `rl_xmit`, without the check, wrapped and zeroed
every word of core. With it, the transmit stops at the top of
installed storage with AD, exactly as p.30 describes.

## Traps this project has paid for

* **A ONE-BIT FIELD-WIDTH ERROR ANNOUNCES ITSELF AS A FACTOR OF TWO.**
  2026-10-21, writing the index value as a 25-bit field at IBM bits
  0-24 instead of a 24-bit address at 0-23 plus a sign at 24. The
  measured word was exactly 2x the expectation in that field and
  correct everywhere else. Before hunting for an arithmetic bug, check
  whether the ratio is a power of two: 2^n says the field is n bits
  wide in one place and n bits narrower in the other, and the fix is
  in the field map, not the arithmetic. The earlier version of the
  same mistake cost longer because I back-computed the operand from
  the expectation instead of printing the symbol -- `S["XBUFER"]` was
  one `python3 -c` away and settled it immediately.

* **AND THE ORIGINAL RULE BIT AGAIN ON 2026-10-21, IN THE SESSION
  THAT HAD JUST QUOTED IT.** "Never edit `run_tests.sh` while a suite
  is reading it" is the oldest entry in this list, and it was broken
  by backgrounding a suite and then editing a section comment in the
  same file while it ran. The failure looks like nothing else:

      run_tests.sh: line 2252: rather: command not found

  `sh` resumed at a byte offset that the edit had moved, landed in
  the middle of a comment paragraph, and tried to execute the word
  that happened to start there. The run died at 895 lines with no
  verdict. **The giveaway is a "command not found" naming an ordinary
  English word**; `sh -n` afterwards reports the file is fine,
  because it is. Discard the run and start again — a shortened run is
  the good case, since the same accident can also skip sections and
  still print a pass.

  THE DISCIPLINE THAT ACTUALLY WORKS, since knowing the rule plainly
  is not enough: while a suite is in the background, edit `docs/`
  only. Everything else waits.

* **DO NOT EDIT `strap_asm.py` WHILE A SUITE IS RUNNING.** The rule
  everyone remembers is "never edit `run_tests.sh` while a suite is
  reading it" — `sh` reads the script by byte offset. The rule that
  bit on 2026-10-17 is the other half: `run_tests.sh` invokes
  `python3` *per section*, so a mid-run edit to a module leaves the
  sections before it tested against the old code and the sections
  after it against the new. The run does not fail; it produces a
  **verdict about no single version of the assembler.** The only
  honest response is to discard it and re-run, which is what was
  done. A suite's result is only as atomic as the tree it read.
* **A CWD-RELATIVE PATH IS A TIME BOMB, AND THE TREE MOVED TWICE.**
  `strap/mcp_crop.sh` resolved `docs/` against the working directory
  (2026-10-17); on 2026-10-18 the reorganisation into
  `strap/`+`decks/`+`tests/` broke `strap/mcp_image.py`,
  `tests/verify_mktape.py`, and both coverage audits the same way.
  Three of those four were found only by running every moved script;
  the audits were the instructive one, because a path failure there
  does not look like a path failure — `audit_opcode_coverage.py`
  globbed a directory that no longer existed, found zero decks, and
  reported **every operation in the machine** as "newly unused". A
  coverage audit that reads nothing reports total failure of coverage,
  which is indistinguishable from a real regression until you look at
  the glob. Resolve against `__file__` in anything that is not invoked
  from a known directory, and after any move, *run everything*, not
  the suite only: `run_tests.sh` covers 409 sections but not the tools
  beside it.
* **`run_tests.sh` does not `cd` to its own directory** — it computes
  `TESTS_DIR` and exports `PYTHONPATH` from it, but the verifiers open
  `../decks/NAME.strap`, so it works only when run from `tests/`.
  Adding `cd "$TESTS_DIR"` near the top is a one-line fix and is
  *deliberately not done yet*: the only safe moment to edit that file
  is when no suite is reading it, and it should be followed by a full
  re-run to prove the harness still finds everything.
* A bare `*` or `L` assembles as **VFL**, not floating point. Write
  `*(N)`, `L(N)`.
* Give any data section an explicit `SLC`: `DD` emits at the location
  counter, so growing code silently overruns its own constants.
* Compute octal addresses with a helper. Every one written by eye in
  this project has been wrong.
* **A MEASURED NULL IS STRONGER WITH A LIVENESS PROOF, and it costs one
  extra run.** Recording "0 rows moved, and here is the arithmetic
  reason" is this project's standard, and it is still one inference away
  from "the instrument works". The sharper form, first used 2026-09-25:
  patch the encoder, show the patched build moves a CONSTRUCTED case
  that the real data does not contain, then report that the real data
  moved nothing. For the `LX`/`SX` bit-18 mask that reads: under the
  patch `LX,$X1,I62SUB+.32` goes `024324.42` to `024324.02`, so the
  encoder demonstrably moved by exactly bit 18 — and no row in the block
  sees it, because every operand is word-aligned. **That distinguishes
  "my data cannot reach this" from "my patch did nothing" with
  evidence rather than with reasoning.**
* **A CONFIDENT NEGATIVE ABOUT SOMETHING THE USER SAID THEY HAVE IS
  EVIDENCE THAT YOU ARE LOOKING IN THE WRONG PLACE.** An agent was told
  the plan was to use "the Flute SDRAM driver". It fetched upstream
  Flute's complete 1,922-path file listing, matched every path against
  `sdram|dram|phy|ddr`, found only false positives, and concluded *"the
  authorized plan names a component that does not exist."* The method
  was sound and the subject was wrong: the driver is at
  `~/src/ulx3s-experiments/flute-ulx3s/src/Sdram_Controller.bsv`, 434
  lines, with a testbench and seven build directories. The same agent
  also declared `nextpnr-ecp5` "unrecoverable" from one dead binary in
  `/usr/local`, while four working builds sat in a sibling project.
  **When a search contradicts what the user told you they have, the
  prior should be that the search is aimed wrong — they know their own
  machine.** `find ~/src -name '*dram*'` costs three seconds. Hedge the
  negative, or widen the search, before writing "does not exist".
* **NEVER READ A FILE A BACKGROUND JOB IS STILL WRITING — a partial
  file answers your question wrongly and silently.** An agent OCR'd a
  297-page CE manual in the background, grepped the output while the
  job was still running, found nothing, and reported *"I OCR'd all 297
  pages and grepped it"* along with a "could not determine". **The file
  held 87 pages at the time.** Re-run against the complete file, the
  same grep found the whole answer — a verbatim four-step CPU-side IPL
  sequence the report had declared absent. The agent caught and
  reported this itself, which is the only reason it was caught at all.
  **A grep over a file that is still being written is not a measurement,
  and "I found nothing" is only evidence if the search space was
  complete.** Check the job finished — compare the page count you
  expected against the page count you got — before concluding from an
  absence. Note this is the same shape as the stale `__pycache__` trap:
  a tool reporting confidently on input that was not what you thought.
* **AN INJECTION THAT NEVER APPLIED LOOKS EXACTLY LIKE AN INJECTION
  THAT PROVED NOTHING — and this project's whole discrimination
  argument rests on injections.** An agent's `sed` pattern did not
  match `opcodes.py`'s spacing. Nothing was patched. The verify script
  then printed `ALL TESTS PASSED`, which reads as "this check does not
  discriminate on that field" — a *result*, and a publishable one,
  since this project deliberately records measured nulls. The two
  outcomes are indistinguishable from the output alone. **Confirm the
  patch LANDED before running: print the patched lines, or diff, and
  look.** A measured null is only a result if the thing being measured
  actually changed; otherwise it is a broken instrument reporting zero.
  Note this is worse than an ordinary silent failure, because the
  failure mode produces output that fits a category we consider
  valuable and write down.
* **AND THE AUTHOR OF THAT RULE THEN BROKE IT, which is the part worth
  keeping.** Two commits after writing "before handing out an item,
  check it against the code", I briefed an agent to transcribe routine
  1262 TEST 1B. The block was already committed, green, and wired into
  the suite as `verify_ax5b_162_test1b_listing.py` — **and I had listed
  that exact file in the brief**, under a hedge I invented out of
  nothing: "a DIFFERENT block despite the name — check what it covers."
  It checked. It was the same block, the same 76 rows, the same octal
  range. Sixth instance in three days. The failure was not ignorance —
  the file was in my hand — it was writing a hedge instead of running
  `grep`. **A hedge is not a check. If you find yourself writing "check
  whether X", check it before you send the message.** (The agent
  stopped and reported rather than building a duplicate, which is the
  behaviour the brief asked for and got.)
* **"THAT IS NOT TRANSCRIBED YET" IS A CLAIM, AND IT NEEDS A GREP.**
  Twice in one session I handed out work whose premise was that a block
  was untranscribed, and twice it already was. `I60S1` — the brief said
  it was missing; its HEAD had been committed for days
  (`ax5b_160s1_clr_inds.strap`, pp.83-84) and only the tail was open.
  TEST 7's comparison test at PDF p.71 — the brief named it as the
  target and quoted two of its rows as evidence it was untouched; the
  whole page was already in `ax5b_160105_compare.strap` and already
  green, *including those two rows*. Both times the agent caught it and
  redirected to the genuinely uncovered range, so nothing was wasted —
  but that was their care, not my planning, and a less careful one
  would have produced a second file over the same octal range. **Before
  writing a brief that says a block is new, grep the verify files for
  its octal addresses.** One command. The quoted-row case is the sharper
  lesson: I cited specific rows as proof of absence without searching
  for those rows.
* **A 2-UP SCAN MEANS "WHAT IS ON PDF PAGE N" HAS TWO ANSWERS**, and
  finding one of them looks exactly like finding the answer. A report
  cited "`jb_ax4b`'s routine index at PDF p.2". I rendered p.2, saw
  PURPOSE / PROGRAM INTRODUCTION / OPERATING PROCEDURE, and wrote a
  correction into `docs/archival_inventory.md` saying there is no index
  there. **The left half was printed p.1; the right half was printed
  p.2, §4 PROGRAM PHILOSOPHY, and it lists all eleven routines.** The
  original citation was right and my correction was wrong. Note the
  failure was not a wrong page number — I rendered the correct page and
  stopped once it had told me something. Cheap tell: a 2-up scan shows
  TWO printed page numbers, and both were visible in the render I was
  reading from. **Look at the whole render before concluding from it.**
* **BRANCH POLARITY IS A PER-CHECK PROPERTY, NOT A PER-BLOCK ONE, and
  this file has been telling agents otherwise.** Every recent brief
  said "both error shapes exist in these decks — determine which shape
  YOUR rows use", which invites reading one row and applying the answer
  to a whole block. `verify_ax5b_162_test1b_listing.py` is a standing
  counterexample that was already in the repo: **both shapes coexist
  inside one 76-row block, and `BZXVZ` plays opposite roles within it.**
  In the DIR IX and IMMED IX classes, `BZXVZ,$+2.0` SKIPS the
  `SIC,SEN`/`B,SERS` pair — branch is the OK path. In FLT PT and FULL
  WD VFL, and in the "did EX destroy the subject" check of all five
  classes, `SIC,SEN` comes FIRST and the branch goes TO `SERS` — branch
  is the error path. The original transcriber recorded this in that
  file's docstring ("BZXVZ PLAYS TWO OPPOSITE ROLES"); the
  generalisation never made it out of the file. **Decide polarity per
  check, from the rows around that check.**
* **PROSE IS NOT EXECUTABLE, so an inverted gloss can sit in a
  committed, fully-passing file indefinitely.**
  `decks/ax5b_160_test8b.strap` said a protection violation with the
  interruption system DISABLED "still sets the indicator, there is just
  no interruption". The opposite is true. `B<IND>` branches when the
  indicator is ON and `BZ<IND>` branches when it is OFF, so in these
  decks **the branch is the OK path and the fall-through is the
  `SIC,SEN`/`B,SERS` error pair** — and an error message names the
  ANOMALY, not the requirement. `-SX OUT OF BOUNDS SETS DS WHEN /
  -SYSTEM DISABLED.` is a complaint. Nothing caught it because the rows
  were bit-exact and always had been; the verifier checks encodings, not
  glosses. Worse, the wrong claim contradicted both the sibling file
  (`ax5b_160_test8c_disabled.strap`) and the code it described
  (`protViolates` ends `st.irqEnabled() && installed(a) && signalled`).
  **When a file's prose makes a behavioural claim, check it against the
  model and against its siblings — nothing else will.**
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
  error table, `B,I60B17($X3)`, indexed — so the halt address names
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
  outright), and "1260 needs SSIP's `I60S1` harness, reported at
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
* **A splice with an unverified end marker can delete most of a file
  and still exit 0.** Editing `run_tests.sh`'s IF section as
  `s[:i] + new + s[j:]`, with `j` found by searching for another
  section's name, removed **3266 lines** — the marker sat ~3000 lines
  later than assumed. The suite then ran **40 sections, all passing,
  `EXIT=0`**. Nothing in that output says "most of me is missing".
  What caught it was printing the SECTION COUNT beside the exit
  status, which is the habit the PASS-count trap above already
  prescribes — one commit after it was written down. **Assert the
  bounds of every slice before writing it**: check the first and last
  line of each piece, and that the pieces rejoin where you think. And
  when a suite's size can change, compare `grep -c '^run '` against
  the previous run, not just the exit code.
* **Inserting after a `run` line puts your comments in front of its
  comments.** The same edit anchored on a section's `run` line plus
  its `"PC=..."` line — but that section's explanatory block follows
  those two lines, so the new section landed BETWEEN a run line and
  its own commentary, and that commentary then read as though it
  belonged to the newcomer. A section here is `run` line + `PC` line +
  comment block; anchor on the whole of it, or on the blank line
  before the NEXT `run`.
* **"I copied the deliverable to the scratchpad" is a claim, and it
  needs an `ls`.** The disk study's hand-back said it had copied
  `disk_subsystem.md` to `scratchpad/out_disk/`. The directory existed
  and was **empty**; the file was only in the agent's worktree, which
  is deleted when the worktree is cleaned up. The report was otherwise
  excellent and entirely accurate about the documents — which is the
  point: an agent that is reliable about the thing it studied can
  still be wrong about what it did with the result, because the two
  claims are verified by different means and only the first one got
  checked. **Verify the artefact exists at the path before acting on
  the report, and copy from the worktree if it does not.**
* **A number quoted by an agent is unverified until a render shows
  it, and OCR is not a render.** The VFL correction rested on ten
  measured times from Perf. Char. Vol. 2 p.110. Re-reading the page
  confirmed every one — but only after a scare: `pdftotext` put
  `(D,64,4)` at 15.00 in one extraction and 15.01 in another, because
  the row's OCR runs the label into the first number
  (`10,64,4115.01`) and the column alignment is invented. Had the
  "correction" been published, it would have corrected a right answer
  to a wrong one. **Where a table's columns matter, the text layer
  decides nothing**; and the same page then yielded 24 rows where the
  agent had tabled 9, so re-reading was worth it twice over.
* **A build that has started code generation has not passed.** This
  session reported "it compiles through `StretchCore` cleanly" on the
  strength of seeing `code generation for mkStretchCore starts` with
  only the known benign `G0024` warnings. The build then failed:
  `(G0005) The assertion 'fire_when_enabled' failed`. Two things hid
  it. The shell exit code was **0**, because `run_tape_test.sh`'s
  `set -e` could not help when the failing `bsc` was the first of two
  commands in a pipeline whose tail succeeded. And the grep was for
  `Error|BUILD_RC`, run against a log that had not finished being
  written — the same "do not report on a file a background job is
  still writing" trap, turned on the session's own build. **Wait for
  the process to exit, then grep; and never read progress output as a
  result.**
* **A load average is not evidence about your own work.** Hours of
  this session were spent queueing suites behind a load threshold,
  renicing, and apologising for a saturated machine. The machine held
  **446 `qemu-system-x86_64` processes** from an unrelated project in
  `~/src`, agent jobs run at **nice 5** against their **nice 0**, and
  `renice -n 0` exits 0 while silently doing nothing for a non-root
  user on macOS. The queued full suite never ran. **Before pacing work
  around load, find out whose load it is** — one `pgrep -c` would have
  done it, and would have changed the plan for the whole session.
* **A FIFO inside a device module can silently disable the rule that
  calls it, and bsc will not warn.** Giving `mkTapeSourceVector` a
  plain `mkFIFOF` response queue compiled clean, linked clean, ran,
  and **exited 0 with thirty-five failed checks all reading zero**.
  `build/mkStretchCore.sched` named the cause in one line:

      Rule: rl_io
      Predicate: ioDev_tape_respQ.i_notFull &&
                 ioDev_tape_respQ.i_notEmpty && ...

  **bsc lifts a called method's implicit condition into the CALLING
  RULE's predicate, and it does so UNGUARDED — not per if/else arm.**
  `enq`'s `notFull` and `deq`'s `notEmpty` were both ANDed into
  `rl_io`, so on an empty queue the rule could never fire **for any
  device**: one FIFO in the tape turned off the whole I/O path. The
  reader and printer, which never touch the tape, failed too.
  `RWire`/`PulseWire` are `always_ready`, have no implicit condition,
  and leave the predicate clean — **which is the actual reason
  `StretchStorage` drives its operand channel with wires rather than a
  FIFO.** That reason is worth more than the idiom, and this file now
  says so where the next person will look.
  **The general rule: after adding any module whose methods have
  implicit conditions, read the caller's `Predicate:` line in the
  `.sched` dump.** It is generated on every build and it is the only
  place this shows up before the test does.
* **`(* fire_when_enabled *)` failing is YOUR assertion failing, not a
  design that cannot schedule.** G0005 on the first version of this
  same module sent the work down two dead ends — `mkLFIFOF` (G0033, a
  real combinational cycle) and `mkFIFOF` (the silent disable above) —
  before the original design came back unchanged except for deleting
  the two attributes. Three builds at ~40 minutes each under load.
  **A 20-line testbench with one rule in the same if/else shape as the
  caller reproduces every one of these scheduling errors in seconds.**
  Write the repro before the second attempt, not after the third.
