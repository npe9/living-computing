# What to do next, and why

A standing work queue for the Stretch model, ordered by dependency.
Written so the next session starts from a decision rather than a
survey.

**This file is the plan, not the record.** The record of *how* each
piece was built lives in `docs/microarchitecture_plan.md`, in the
section comments of `tests/run_tests.sh`, and in commit messages.
When an item here is finished it shrinks to a pointer; it does not
accumulate.

## WHERE THIS STANDS, 2026-10-25 — read this first

**The frontier is `T PICA` at 004604.00, and printed p.78 is the
blocker.** The MCP image holds printed pp.15-77 gapless (60 decks,
467 stand-ins checked against their definitions, 276 agreeing SYNs,
32 symbols still external), and
the boot run executes MCP's ASSIGN routine end to end: it saves its
indexes, walks the channel status table for a machine-configuration
change (p.72), sorts the multi-unit count table and runs the MULTI
UNIT SCAN (p.73), takes the reject path (p.74's `T AREJX` into p.75),
clears the reel slot and the assigned and mount bits, and **dispatches
through p.75's exit table at `T L` — *NOT OVERLAP JOB NOT ASSIGNED* —
to `T PICA`**, which is not yet transcribed. `boot_plan.md` A21
carries the detail.

**The one unexplained refusal** is still the OP trail's single
`operation invalid` at half-word 1304 = 001214.00, printed p.24's
time conversion, raised once after 6.01 million steps. It is proven
NOT to be the crossing store (that is built and tested). An exact
locator in `StretchCore` is the tool that will name it.

### The older orientation, 2026-10-21

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
4. ~~Printed pp.20-26~~ **— all seven done, bit-exact (17, 28, 50,
   54, 44, 32 and 26 rows). Printed p.27 onward** is the
   continuation.

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

## THE MCP IMAGE THE BOOT MOVES IS NOW PRINTED pp.15-36 -- 727 words, where it was 80, 2026-10-22

`strap/prosa.py`'s PROSA record carried printed pp.15-18. It now
carries pp.15-36, because all twenty-two pages are transcribed and
they form **one run from 000621.00 to 002147 with no gap** — each
page starting on the word the one before it ended on or the next.

**And the merge checks all twenty-two against each other.**
`mcp_image.merge()` refuses a symbol defined twice and requires every
`SYN` stand-in to equal the value the page that *places* that symbol
gives it. Across pp.15-36 that is **253 symbols, 45 of them external
to the whole range** — so the image is also the largest cross-page
consistency check in the project, and it runs every time the tape is
built.

### Three things broke, and all three were invisible at eighty words

**1. The tape had to be written in chunks.** printed p.14's control
words have a COUNT of 513 and a STRIDE of 512, so consecutive records
**overlap by one word** — the one-word header `C22-6728` printed
p.215 describes. The fixture wrote its record flat, which is correct
for anything shorter than one chunk and wrong for anything longer:
the second control word read tape word 513 into buffer offset 512 and
shifted everything after the first chunk down by one.

**The fixture said so exactly, which is what `BODY_TAG` is for.**
Every filler word carries its own buffer offset, so the failure read
`mcp_moved_last = 0x5a5a0000000002df` — offset 735 where 734 was
wanted. An off-by-one with its own size written in it.
`prosa.tape_words()` emits the chunked form now.

**2. The image has two holes and they are reservations.** printed
p.21's two `DR(BU),(3)` leave 001034-001041 and printed p.36's
`DR(BU),(100)` leaves 002000-002143. `prosa.py` used to refuse *any*
hole, on the grounds that a missing word reads as zero and a zero
half word is BRANCH ENABLED to location zero. That reasoning is right
and the fix was not to relax it: **`AssembledProgram` now records
every `DR`'s range**, and `mcp_ipl_image()` requires the set of
missing words to be *exactly* the set of reserved ones. A
transcription that loses a word still fails, and it fails naming the
word.

**3. "The word after the last one is still zero" had to go**, because
MCP now runs far enough to write it. `S MCP` is 002150.00 — exactly
one word past the image's last at 002147 — and printed p.15 line 21
is `T,$0,X BUFER($9),S MCP -MOVE COMM REGION`. What replaces it is
stronger: printed p.15 line 17's `LVS,$9,$12,$11,$14` sums **three**
dictionary counts, 3 + 727 + 5 = 735, and the new check requires
`S MCP` to hold the fixture word tagged 735, so a wrong sum fails
with the offset MCP actually computed.

**And "a word from the middle" had to be computed.** Index 363, the
plain midpoint of 727, lands inside printed p.24's `DRZ(BU),100` — a
hundred words of deliberate zeros. An expected value of zero over a
region that was zero *before* the move proves nothing.

## "X ICD" IS "X IOD", AND THE DATUM IS WHAT SAID SO, 2026-10-22

printed p.35 line 10's name field reads **`X ICD`** at 900 dpi, and
its comment reads `-ICD IN HOLLERITH`. The deck copied both. **The
datum says IOD.**

`0o400120104040` is the three card columns of `I`, `O`, `D` punched
through `strap/cards.py` — i.e. through `C22-6678-1` printed p.56's
Appendix F. Three things agree against the glyph:

* **The datum itself**, decoded through a different manual.
* **printed p.19 line 23**, `KF(BU,36),X IOD,12 -COMPARE AGAINST *
  IOD *`, which SYNs 001750.40 — exactly where p.35 puts it.
* **The same printed row**, which renders its own `DD(BU,36)` as
  `CD(BU,36)`. §13 with an `O` in place of a zero, in the same six
  glyphs.

**The rename is not cosmetic.** `mcp_image.merge()` links a symbol
one page *places* to every page that SYNs it. While this one was
called `X ICD`, printed p.19's `X IOD` had no definition anywhere and
was carried as an external; it is checked now, and the image's
external count fell from 45 to 44.

**And the check that caught it is in the suite**: all three
card-type literals — `X MCPP`, `X IOCD`, `X IOD` — are now asserted
to be the punched characters. A fourth manual would be needed to
disagree.

### §13 now has an O as well as a zero

`listing_typography.md` §13 was "digit zero read as `C`" and §13b
added "a `C` that is a real `C`". This is the third shape: **a
letter `O` read as `C`**, in a NAME field, where no octal column and
no opcode can rule it out. What ruled it out was the datum the name
labels — which is a tell worth stating on its own: *when a name
labels data, decode the data before trusting the name.*

## >>> THE "HALVED OFFSET" IS A SEVEN-BIT FIELD, AND BIT 18 IS ITS LOW BIT — 2026-10-25 <<<

For dozens of transcribed pages the printed second group's low octal
has been **half the offset the statement writes**: `,46` printing
`027`, `,32` printing `020`, `,40` printing `024`. It has been
checked against the listing every time and never explained, and the
explanation was one odd number away.

printed p.78 line 14 is the odd number:

```
LFI(BU,2),3,5    ->   402002.46 70
LFI(BU,2),3,13   ->   402006.46 70
```

Five halved is two and a half. The missing half is **bit 18 of the
second group**:

> **The VFL offset is SEVEN bits: bits 12-17 of the second group
> hold `offset >> 1`, and bit 18 holds `offset & 1`.** The printed
> `.bb` pair begins at bit 18, so an odd offset shows up as `.46`
> where an even one shows `.06`.

That is C28-6129 printed p.3's format 7 read back off the machine:
`OP(dds), A₂₄(I), OF₇(I')`. **`OF₇` — seven bits — is written in the
manual, and this is the listing agreeing with it.**

Checked across three pages, odd and even, positive and negative:

```
row                             offset   hi    b18
p.73 line 10  LF(BU,32),...,32      32   020    0
p.73 line 25  L,T UNITK,46          46   027    0
p.78 line 13  LF(BU,12,4),$L+.20,1   1   000    1
p.78 line 14  LFI(BU,2),3,5          5   002    1
p.78 line 15  LFI(BU,2),3,13        13   006    1
p.78 line  9  L,T ABSCH,-60        -60   042    0
p.78 line 12  CV(BU,18),0.0,-32     -32   060    0
```

Seven for seven, with the negatives in seven-bit two's complement
(−60 → 68 → `042`, low bit 0).

> **An unexplained regularity is a bug report you have not filed
> yet.** "The offset prints halved" was tolerated because every row
> still checked bit-for-bit — the assembler had the rule right
> without anyone writing down why. It took one odd offset to turn a
> curiosity into a field width, and the field width was in the
> manual the whole time. *When a derived quantity is consistently
> off by a factor, look for the bit that fell off the end.*

## >>> PRINTED p.77 IS `T SCRIB`, AND p.47's LINKAGE FORMAT IS USED FOR REAL — 2026-10-25 <<<

Thirty-two compiled rows of forty-one lines, all bit-exact on the
first assembly. Seven measured injections, one of which survives and
says something true.

### Four of p.75's ten exits come here

Line 6 is 004461.00 = `T SCRIB`, and **four** of the dispatch table's
exits are `B,T SCRIB`:

```
T D  -NOT OVERLAP FULLY ASSIGNED
T F  -OK -- ALL I/O REQ HAVE BEEN PROCESSED
T G  -OK -- NO MORE UNITS AVAIL FOR ASSIGN
T K  -OK -- NOT OVERLAP JOB FULLY ASSIGNED
```

Four ways for ASSIGN to finish, one place to go afterwards, and this
page — *SCAN THE PP REF TABLE FOR NEW ASSIGNMENTS* — is what happens
there.

### printed p.47 documented a call; this page makes it

p.47 compiles **nothing**. It is THE DECODE PROGRAM LINKAGE FORMAT
written out as a worked example, and it has been sitting in the
image as a documentation page since 2026-10-23. Lines 17-24 here are
that call in live code:

```
        SX,$15,T PSAV          save the caller's index
        LVI,$15,T P6A          point $15 at the parameter block
        BD,S A8IQS             and enter the routine
T P6A   VF,T P5IN              -FWA IN
        CF,8                   -N
        VF,T P5OUT             -FWA OUT
T IPLB1 BE,$+.32               -MODIFIED BY IPL
        LF(BU,64,8),T P5OUT    -GET THE CONVERTED WORD
```

`VF, CF, VF` — first word address in, count, first word address out
— is p.47's block field for field, and `$15` is the linkage register
printed p.59's LINKAGE FORMAT page names. **The documentation page
and the call site are thirty pages apart and they agree exactly.**
*That is what a transcribed corpus buys that a transcribed page does
not.*

**And `BD,S A8IQS` is a branch, not a halt.** p.75 has five `BD,$`
rows that stop the machine only because the target is the
instruction's own address. Here the same operation — branch
*disabled* — enters a subroutine with interruptions off. The
injection that makes it a plain `B` moves the J field 0001 → 0100
and nothing else.

### >>> An `E` read as an `L`, and the glyph is the last witness <<<

Line 23 prints `BL,$+.32` at 1800 dpi: a vertical stroke and a bottom
bar, no top bar, no middle bar. It is **`BE`**.

1. **`BL` is not a mnemonic.** The unconditional branch family is
   `B`, `BD`, `BE`, `BEW`, `BR`, `NOP` and nothing else. A reading
   that produces a mnemonic no source lists is a reading to doubt.
2. **`BE,$+.32` at 004474.00 produces `004474.40 00`** — the printed
   row exactly. Nothing else does.
3. **The twin says so.** printed p.78 line 40 is `T IPLB2 BE,$+.32`,
   same operation, same J field 0000, same comment *MODIFIED BY
   IPL*, printed cleanly.

> So the stroke-dropping artifact is **about ink, not about
> character class**. A drum that drops a zero's left stroke drops an
> `E`'s bars too. §13 spent six sub-sections on digits because
> digits are where the octal column could catch it; the mechanism
> never cared. `listing_typography.md` §13i.

`T IPLB1` was already a stand-in at 004474.00 and this page places
it. Its comment says **the IPL modifies that row** — a branch the
loader patches — which is why a `BE` to the next half word has a
name at all.

### The injection that survived

`$+.32` → `$+.40` changes nothing. A branch address is nineteen bits
— word plus half-word selector — so **every offset from 32 to 63
bits names the same target**. The deck could have written `.32`,
`.40` or `.50` and the listing could not tell them apart; `.32` is
what the card says. *Recorded, because a survival that explains the
encoding is worth as much as a failure that confirms it.*

## >>> PRINTED p.76 IS A DATA PAGE, AND THE COUNTING IS THE WHOLE CHECK — 2026-10-25 <<<

Thirty-seven lines, thirty compiled, and **only seven print any
machine code at all**. It is the print sub-routine's message store:
the buffers the assignment printer fills in, three hexadecimal
constants, five SYN cards, four one-bit flags and three index words.

### Seventeen labels, seventeen locations, first assembly

The listing prints no binary for character data — as it prints none
for p.41's `(AX)` masks or pp.9-12's `(IQS*)` messages — so **no
character code is checked or can be**. What is checked is the
counting, and on a page that is almost all character data the
counting *is* the page: seventeen labels, each landing on its printed
location, and **one wrong character anywhere shifts every label after
it**. The injection that drops a single blank from line 9 produces
**eleven failures**, each exactly eight bits early.

**And the advance is the datum's character count, not the declared
item length.** Line 16 is `(IQS*)DD(BU,36,8), UNIT *` — six
characters — and advances forty-eight bits. Line 14 declares 64 and
advances 96 for twelve characters; line 15 declares 24 and advances
24 for three. The injection that changes 36 to 48 **survives**, which
is how that is recorded.

Four of its labels were already stand-ins and all four agree:
`T BUFB1`, `T MESSY` (p.74 line 55's `LVI`), `T SBHDI`, and `YSCRBT`
(p.75 line 37's `BBZ` — and that stand-in gives the *bit*, 03). The
external count went 35 → **31**, predicted exactly.

### >>> A hex literal is the one field where the C/zero rule has no internal answer <<<

`listing_typography.md` §13e turns on octal having no `C`.
**Hexadecimal does**, so the field cannot rule it out — and this page
has three such literals. Line 11 prints

```
DD(BU),(16) C C 0 F 9 D B 6 8 B C D 9 1 9 1
```

with **three open-C shapes and one closed zero among its four
zeros**. Its compiled datum prints `0000174733321303310621`, which is
`000F9DB68B0D9191`: all four are zeros.

> **Nothing in the statement could have said so.** The compiled value
> is the only authority for a hex literal's `C`, and it is printed in
> octal three columns to the left. The injection that takes the C's
> literally prints `14` where the listing prints `00` — 1100 in the
> top four bits — so the discriminator is loud once you look for it.

### The artifact alternates with the COLUMN, not with the digit

Line 19 is `(16)8993151193000000` and prints its six trailing zeros

```
C 0 C 0 C 0
```

and printed p.74 line 10's `CM0000` prints `C M O C O C` — **the same
alternation in the opposite phase**. That is the mechanism showing
through: the drum drops the stroke on alternate columns, so a run of
identical zeros necessarily comes out in two shapes.

> **Which kills the last defence of a single-glyph reading.** "It
> looked like a C at 1800 dpi" is worth nothing on its own, because
> the shape is a fact about where the character sits, not about what
> it is. Read the run, read the field, read the compiled value — in
> that order.

Line 18 was misread a third way, and neither rule would have caught
it: its sixth hex digit was read `0` and is `D`. The compiled octal
said so before the render confirmed it.

### The trail does not move, and the step count does

004604.00 is still `T PICA` — p.76 is data the run never executes, so
nothing was re-measured and all 36 boot checks passed unchanged. But
the step count rose 22,046,898 → **22,047,265**, because the IPL
TRANSMIT moves the whole image and the image is thirty words longer.
*A page that adds no instructions still costs the bootstrap something
to load, and the step counter is where it shows.*

## >>> PRINTED p.75 IS THE DISPATCH TABLE, AND MCP USES IT — 2026-10-25 <<<

Fifty compiled rows of fifty-three lines — the first short page in
this run — with **no boxed heading at all**. All fifty assembled on
the first try except two, both of which are recorded below. Six
measured injections.

### The run dispatches, and the exit it takes has a comment

The trail moved **4578 → 4872 = 004604.00**, and p.75 line 50 names
that address:

```
T L   B,T PICA    -NOT OVERLAP JOB NOT ASSIGNED
```

MCP walks the reject path — clearing the reel slot, the assigned
bits, the mount bits — counts `T IXA` down through line 36's
`CB+,T IXA,T AREJ1`, falls out at line 40's `B,T L`, and dispatches.
703 steps. **The dispatch table is not a table the run passes over;
it is a table the run uses, and the exit it chooses is labelled with
the condition it means.**

`T PICA` is next, and p.75's own deck already carries its address.
**It is printed p.80 line 4** (MCP_Mar63 PDF p.87, whose location
column reads 004604.00 at its first compiled line) — so printed
pp.76, 77, 78 and 79 lie between, and the merge needs all four before
p.80 can join. *The run's next step is four pages of reading away,
and it has already told us which four.*

### Nine labels were already in the image, and all nine agree

`T AREJ`, `T D`, `T F`, `T H`, `T I`, `T K`, `T M`, `T N`, `T P` —
every one carried as a stand-in by printed pp.66-74, every one
landing on the address its stand-in gives.

**`T M` and `T N` are the pair that made this page worth doing
first.** p.72 line 31 is `BZB,T UNASG(T IXF),T M` and p.73 line 32 is
`BZB,T UNASG(T IXG),T N` — *the same test on different index
registers* — and their two targets are the two halves of one word,
004422. A page that resolves a pair like that is worth more than its
own fifty rows.

**And the external count predicted it.** 39 − 9 placed + 5 new = 35,
and the merge printed 35. Yesterday that number caught a wrong
diagnosis by landing on 39 where I said 40; today it confirms a
right one. *Predict it before you build.*

### Five deliberate halts in ten lines

Lines 44-53 are a dispatch table of ten exits and nothing else:

```
T D  B,T SCRIB   -NOT OVERLAP FULLY ASSIGNED
T F  B,T SCRIB   -OK -- ALL I/O REQ HAVE BEEN PROCESSED
T G  B,T SCRIB   -OK -- NO MORE UNITS AVAIL FOR ASSIGN
T H  BD,$        -ASSIGN BIT ON - SING UNIT CHAN
T I  BD,$        -ASSIGN BIT ON - MULTI UNIT CHAN
T K  B,T SCRIB   -OK -- NOT OVERLAP JOB FULLY ASSIGNED
T L  B,T PICA    -NOT OVERLAP JOB NOT ASSIGNED
T M  BD,$        -MACH CONF CH. ASSIGN BIT ON - SING
T N  BD,$        -MACH CONF CH. ASSIGN BIT ON - MULTI
T P  BD,$        -ERROR MCP IS OUT OF PHASE
```

The corpus had **three** `BD,$` halts in total (printed p.6 line 1,
printed p.52 line 55, printed p.74 line 39). This page adds five, and
each carries the impossible condition it stands for. Four of the five
are *the assign bit is already on* — a state ASSIGN has just
convinced itself it ruled out. **This is 1963's assertion failure**,
and it is written the only way the machine allows: stop, with the
address in the instruction counter naming which assumption broke.

### A seventh written minus, and the strongest §13d row yet

Line 7 is `-(BU,18),T CHSXW,46` with the familiar `.30`. The count
was **one** three days ago.

And line 30, `V+I,T X1,0.0`, prints its octal field at 1800 dpi as

```
C 0 0 C C C 0 . 2 5     C 5
```

— six digits of a field that **is** zero, four of which dropped their
left stroke. Octal has no C, so all six are zeros, and the byte's
leading glyph has the same open shape in the same row: `05`, which
p.73 line 45's `V+I` (`000000.45 05`) says independently.

### The two rows the deck got wrong, out of fifty

That byte was one. The other was **`T P1BA`'s stand-in, read `.40`
where the branch's own bit 18 says `.00`** — I derived the address
from the code and then mis-split the `.bb` pair.

> **A stand-in derived from a branch must use the branch's bit 18.**
> The branch target's low bits and the J field share one printed
> octal pair, and reading it as an address when it is half condition
> code puts the symbol half a word away — where it will assemble
> cleanly and fail only when the defining page arrives.

### The four pages between here and `T PICA`, all read

`T PICA` is printed p.80 line 4. pp.76-79 lie between, the merge
needs all four, and all four are now read. What each one costs:

**printed p.76** — 004423.40-004460.00, 37 lines. *A PRINT
SUB-ROUTINE THAT WILL PRINT ASSIGNMENTS*: character data in `(IQSX)`
entry mode (`(IQSX)DD(BU,64,8)`) plus radix-16 datums
(`DD(BU),(16)C00F9DB68BCD9191`). `charsets.ENTRY_MODES` already has
`(IQSX)`, so this should need no assembler work. **It defines
`T MESSY` at 004451.00 and `YSCRBT` at 004455.03** — p.74's and
p.75's forward stand-ins, confirmed by name and by bit.

**printed p.77** — **LANDED**, 32/32 rows, seven injections, image
at 60 pages and 32 externals (predicted exactly). `T SCRIB`, four
of p.75's dispatch exits, and printed p.47's linkage format used for
real.

**printed p.78** — 004511.00-004554.40, 56 lines, *CONVERT THE
CHANNEL FIELDS*. **BLOCKED ON A PRIMARY SOURCE, and the search so
far has come up empty.** Lines 9-12 carry a syntax no page in this
corpus has used:

```
T P5A1  $L,T ABSCH(T XB),-60
        $-(BU,18),T CHSXW,-60
        $SF(BU,18),T IPL+1,-60
        $CV(BU,18),0.0,-32
```

a `$` PREFIX ON THE OPERATION, with **negative offsets**. Confirmed
at 1200 dpi: the `$` really is the first character of the operation
field, on four consecutive rows and nowhere else on the page.

**Where it is NOT documented**, as of 2026-10-25:

* **C28-6129 printed pp.3-4** lists *all twelve* STRAP-II symbolic
  instruction formats, from `OP, A` outward. None has a prefix on
  the operation. Format 7 (VFL) is `OP(dds), A₂₄(I), OF₇(I')` — and
  that **`OF₇` is a seven-bit offset field, which is where the
  negative offsets come from**; `-60` compiles to `042` in the
  printed second group, two's complement of −30 at the half-bit
  scale the field uses. So the minus signs are explained and the
  `$` is not.
* The **April 1963 bulletin** (N28-1081, bound in at PDF 59-79)
  itemises additions to Appendix C's mnemonics — including
  `M+N1`/`M−N1`, the negative of printed p.73's `M+1` — and lists no
  prefix.
* `docs/c22_6531_appendix_a.md`'s eight footnotes are the mnemonic
  grammar and are all about **suffixes**; its only `$` rule is "this
  mnemonic is a system symbol, it must be prefixed by `$` whenever
  used", which is about operands such as `$L` and `$R`.

**And the bits say the prefix does nothing.** printed p.77 line 33
is `L,T ABSCH(T XB),46` compiling `000000.56 83  022027.20 50`, and
p.78 line 9 is `$L,T ABSCH(T XB),-60` compiling
`000000.56 83  022042.20 50`. Identical but for the offset field.

> **That is exactly the situation Rule 4 exists for.** The temptation
> is to write `L` for `$L`, get fifty bit-exact rows, and move on —
> and the deck would then assert, silently and without evidence,
> that the prefix means nothing. It might mean something STRAP
> records elsewhere (a listing control, a relocation flag, a
> programmer's convention the assembler ignores) and the one thing
> that is certain is that **this listing cannot tell us which**.
> p.78 waits for a source.

**Also checked and empty**, same day: C22-6729 (the STRAP-II System
Analysis Guide) **Appendix B — "Additional Instructions and
Pseudo-Ops Accepted by STRAP II"** (printed p.195), which is the
complete list and does confirm `CNOP`, `SLC`, `SYN`, `DD`, `VF`,
`CF`, `XW`, `DR`, `DRZ` and names `IOD` and `REEL` as *MCP
Instructions*; and its **Appendix D — "Symbolic Designations"**
(p.202), which turns out to be STRAP II's own internal naming
convention, not user syntax.

**A coprocessor lead was followed and DOES NOT fit.** C22-6729
printed p.180, *Including a Coprocessor Subroutine with STRAP II*,
says Pass 1 enters a coprocessor on six conditions, and condition 5
is "an illegal operation code (detected by `MAIN`)". That is a real
mechanism by which an operation no manual lists could appear in a
STRAP II listing — **but it cannot be this one.** An illegal
operation code is an ERROR condition; STRAP II would have flagged
the row. p.78's four rows compiled to correct, sensible machine code
with no error indication. **Whatever `$` is, STRAP II understood
it.** Recorded so the next session does not spend the morning there.

### >>> AND THE PREFIX CONTRIBUTES NOTHING TO THE BITS: FOUR FOR FOUR <<<

Assembled in the scratchpad from the UNPREFIXED mnemonic and checked
against the printed rows:

```
line  9  L, T ABSCH(T XB), -60     000000.56 83  022042.20 50  PASS
line 10  -(BU,18), T CHSXW, -60    002152.00 80  022042.30 10  PASS
line 11  SF(BU,18), T IPL+1, -60   003266.01 80  022042.12 F0  PASS
line 12  CV(BU,18), 0.0, -32       000000.00 80  022060.21 B0  PASS
```

**All four, with no prefix anywhere.** Two operation classes (VFL
arithmetic, connective, convert), four different second-group bytes
— 50, 10, F0, B0 — and one of them is a written minus with its `.30`
sign modifier. One row matching could be luck; four rows across
three encodings is a measurement.

> So the deck can be written with the base mnemonics and will be
> bit-exact, **provided the header, the verifier and `run_tests.sh`
> all say loudly that the card reads `$L` and the deck writes `L`,
> and why.** That is not inferring an instruction's meaning from
> listing usage — it is declining to represent a character that
> cannot be explained, with the evidence for why it is safe stated
> in full. If the meaning turns up later, the decks name every row
> that would need revisiting.

The encoding check that fell out of it, free: `CV` is VFL operation
27 = 0b11011, so its byte is `0xB0` (low four bits 1011) and bit 23
carries the 16 — printing `.21`. `M+1` is 43 = 0b101011, same byte,
bit 22 carrying the 32 — printing `.22`. printed p.73's `M+1` and
this page's `CV` share a byte and are told apart by one bit, which
is the third instance of that shape after `*`/`M+` on printed p.72.

Still unread in the manuals: C28-6129's section on the offset field
and its pseudo-operation chapter.

**printed p.79** — 004555.40-004603.40, 39 lines.

Then **printed p.80 line 4 is 004604.00**, and the run moves again.

## >>> PRINTED p.74 IS `T AREJX`, AND THE TRAIL MOVES BY TWO HALF WORDS — 2026-10-25 <<<

Forty-five compiled rows of fifty-six lines, under one boxed heading.
All forty-five passed on the first assembly. Five measured
injections, one of which fails three rows.

### The trail moved by exactly the length of what landed

4576 → **4578**. 004360.00 is `T AREJX`, printed p.74's line 55; its
two half words — `LVI,T X1,T MESSY` and `SV,T X1,0.0(T IXE)` — ran,
and the PC trail advanced **two half words and no more**, to
004361.00, for 424 more steps.

**004361.00 is printed p.75 line 1**, `T AREJ R,T IXA -RELOAD IX`.
The run is now stopping one page at a time, and each stop names its
own next transcription.

> *The stop address is a transcription target, not a symptom.* Before
> p.74, the trail sat on 004360.00 and I wrote that the run must be
> walking off the end of p.73 through zeros. **It was not.** p.66
> line 16 (`BB,T RJECT(T IXE),T AREJX` — *IF PP WAS REJECTED*) and
> p.71 line 47 (`BXF,T AREJX` — *NOT OVERLAP ASSIGNED*) both branch
> to 004360.0 and both have carried it as a stand-in since they
> landed. The run was taking a branch two transcribed pages print.
> **When a stop address is unexplained, grep the decks for it before
> inventing a mechanism** — it took one `grep -l` to find that two
> pages already named it.

### Three indicator bits, and two rows account for all three

`mcp_indicators_word11` went `0x200A448` → `0x9448`: XVZ out, XVGZ
in, XF out. An `LVI` of 004451.0 into an index leaves that index
**greater** than zero (XVZ→XVGZ), and the `SV` that follows clears
XF. Two instructions, three bits, and every one of them is what those
two instructions do. Re-measured, not retired.

### Every symbol was already placed, and every value was derived first

Eighteen stand-ins, and the image held every one before this deck was
written. What makes that worth saying is the **order**: each value
came out of *this page's* machine code and was only then looked up.

* the index fields gave `T IXD` = $7, `T IXE` = $3, `T IXI` = $5;
* the second groups gave the field lengths 8 (`T UNCT`), 3
  (`T ABSUN`), 18 (`T ABSCH`);
* the `.bb` pairs gave the offsets — `.34`→28, `.07`→7, `.56`→46,
  `.47`→39, `.44`→36, `.22`→18, `.46`→38, `.02`→2, `.01`→1.

All eighteen agreed with printed pp.61-64. **A page that only
confirms is still worth the morning**: it is eighteen independent
checks of four earlier pages, run by the merge on every build.

And the external count fell 41 → **39** rather than 40, which is one
more confirmation than I predicted: `T A10` and `T C10` stopped being
external, `T MESSY` joined — and so did `T AREJX` leave, because
pp.66 and 71 had been carrying it all along.

### A sixth written minus and a third deliberate halt

Line 32 is `-,T ABSUN(T IXI),46` — *COMPUTE THE RELATIVE UNIT NUMBER*
— compiling `003027.30 10`, the familiar `.30`. Line 39 is `BD,$` at
004345.00, branch disabled to its own address, commented *MCP OR
MACHINE ERROR*: the third deliberate stop this project has
transcribed, after printed p.6 line 1 and printed p.52 line 55.

### Three bytes the assembler disputed, and the ink agreed three times

```
line 36   read C7, is 07    its own octal field prints 00CC02 (13d)
line 38   read 00, is 0C    closed oval + open curve in ONE byte
line 47   read C2, is 02    closed oval at 1800 dpi
```

Each was re-rendered **before** it was adopted, which is the order
this project requires. That the ink agreed with the assembler three
times running is a calibration fact about *the corpus* — this drum
drops zero strokes often — and not a licence to skip the render. Line
38 is the sharpest: two adjacent glyphs inside one byte, one closed
and one open, which cannot both be zeros and cannot both be C's.

## >>> PRINTED p.73 SORTS THE TABLE, AND THE RUN LEAVES THE RANGE — 2026-10-25 <<<

Forty-one compiled rows of fifty-six lines, under **four boxed
headings** — more than any page of the ASSIGN program so far. All
forty-one passed on the first assembly, which has now happened on
enough pages that the interesting part of a page is no longer
whether it compiles.

**The run moved from 004263.00 to 004360.00.** 004263.00 was this
page's own first word, so the run had been stopping *on* it; it now
executes the page and stops on the next address it cannot reach.

**And that address has a name: 004360.00 is `T AREJX`.** printed
p.66 line 16 (`BB,T RJECT(T IXE),T AREJX` — *IF PP WAS REJECTED*) and
printed p.71 line 47 (`BXF,T AREJX` — *NOT OVERLAP ASSIGNED*) both
branch there and have carried it as a stand-in since they landed. The
run is not walking off the end of p.73 into zeros; it is taking a
branch two earlier pages print, into a page that is not in the image
yet. *The stop address is a transcription target, not a symptom.*

**The step count did NOT move** — 22,045,771 against p.72's 22.04
million — and that is informative rather than disappointing. p.72
cost sixteen million steps because line 51 count-branches over the
whole channel status table. p.73's loops are over the MULTI-UNIT
count table, which this fixture's machine barely fills, so the page
runs almost for free. *A page that adds no steps is not a page that
did nothing; it is a page whose loops this fixture does not fill.*

### `M+1` — an operation the assembler had and no page had used

Line 55 is `M+1,T CHCNT(T IXH)`, add one to memory, compiling
`004000.22 B0`. p.72 line 26's plain `M+` compiles `010000.20 90`.
The two bytes differ, and so does the second group's `.bb`, and the
arithmetic is exact:

> **A VFL operation's low four bits are the printed byte's high
> nibble; its high bits are bits 22 and 23 of the second group,
> worth 32 and 16.**

`M+1` is operation 43 = `0b101011` → byte `0xB0`, bit 22 set, so
`.22`. `M+` is 9 → `0x90`, `.20`. `*` is 25 → `0x90`, bit 23, `.21`
— which is the pair printed p.72 already showed, now explained
rather than observed. Four bits plus two is six, so the model covers
0-63 and `opcodes.VFL_INT_CODES` tops out at 61: **the whole table,
not just the three rows that prompted it, and no change to the
assembler.**

### The index field is the authority for an index NAME

Line 2 read `LVI,T IXF,T CHCUC` at 600 dpi. Its code is
`003661.05 01`, whose bits 19-22 are `0010` = `$2` = **`T IXH`**. At
1200 dpi the glyph is an H. **F and H are the hardest pair in the
statement column at this size**, and eight rows on this page turn on
it, including the two `CBH`s that name the sort's inner and outer
loops apart (`004267.24 C8` against `004265.04 C8`) — the two rows
whose statements are otherwise identical.

*Read the index field before trusting an index name.* That is the
same shape as "decode the data before trusting the name that labels
it" (printed p.71), and this is the second column it applies to.

### A false count the byte checks could not have caught

The deck's first header said **FOUR LISTING MARKS: lines 32, 33, 36
and 54**. It is TWO, lines 25 and 44.

The four were read off the **right edge of the code crop**: at 900
dpi `-x 4200 -W 3000` ends at 7200 and the statement column begins
at 6150, so the leading `T` of `T A9F`, `T A9FA`, `T A9G` and `T C9`
— exactly the four *labelled* lines in that range — bled in. A
listing mark is a bare `*` **after the location**, and the location
column has two.

> **A crop that overlaps the next column invents a feature in the
> one you are reading.** Nothing in the forty-one row checks could
> have found this, because the claim was about ink and not about
> bits. The guard is to know where each column's x-range ENDS, not
> only where it starts.

### What p.73 says about the C/zero rule

One page, all three readings, and the column decides each:

* line 33 `004306.C3 C1` → `004306.03 01`, both C's zeros (a §13d
  per-row artifact), confirmed by p.72 line 32's twin `T A9BA
  LVI,T X1BR,T B9` = `004246.03 01`;
* line 35 `C04322.74 CO` → `004322.74 C0` and line 42
  `C04246.34 C2` → `004246.34 C2`, where the **location's** leading
  C is a zero and the **byte's** C is real — p.72's own `BZRZ` (C0)
  and `BRZ` (C2) say so.

`listing_typography.md` §13e now carries the pair as its worked
example. **Do not generalise a row's verdict to the row below it;
generalise the column rule instead.**

### >>> AND READING p.74's FIRST PAGE RENAMED TWO SYMBOLS <<<

p.73's forward branch and p.72's were transcribed `BZRZ,T C1C` and
`BZRZ,T A1C`, and at 1800 dpi both final glyphs really are open
curves. **printed p.74 DEFINES both addresses** — 004320.00 at its
line 6 and 004322.40 at its line 10 — and names them `T A10` and
`T C10`, with the zero closed. They are the generation after `T A9`,
`T B9`, `T C9`, and p.74 goes on to define `T A10A`, `T B10A`,
`T B10`, `T B10B`, `T A11`, `T A11A`, `T A11B` and `T B11C`.
`A1C` would have been the only name of its kind.

**And p.74 proves the shape in one token.** Its line 10 statement is
`CM0000`, whose code `001000.00 F0` puts zero in the connective
field — and at 1800 dpi it prints **`CMOCOC`**: the same digit, four
times, twice closed and twice open, in one word of one impression.
`listing_typography.md` §13g now carries it as the section's
evidence.

> **A NAME IN A REFERENCE CANNOT BE CHECKED; A NAME IN ITS
> DEFINITION CAN.** A `SYN` stand-in assembles to the right bits
> whatever it is called, so no bit check in this project could have
> caught either name. Only the page that PLACES the symbol can.
> Both decks and both verifiers are renamed here; no bit changed.

### The indicator word moved, and it was re-measured, not retired

`mcp_indicators_word11` went `0x9544` → `0x200A448`: out go AE, MOP
and XVGZ, in come AL, XF and XVZ. XF and XVZ are what the `CBH` pair
on lines 16 and 18 leave behind and AL is what the `KF` on line 11
that decides each swap leaves. **A check that moves because the run
went further is still measuring something** — retirement was right
for `mcp_end_of_prosa_bit_X0`, whose quantity stopped being
meaningful, and is wrong here.

## >>> PRINTED p.72 IS `T A9`, AND THE RUN MOVES AGAIN — 2026-10-25 <<<

Forty-nine compiled rows, the densest page of the ASSIGN program.
48 of 49 bit-exact on the first run.

**Line 4 is the address the boot has been stopping on since p.65
landed.** p.65 line 9 is `BZXVZ,T A9` commented *"-IF A MACH CNF
CHANGE"*, and this page's heading three lines above line 4 reads
**"MACHINE CONFIGURATION CHANGE / ADJUST THE NECESSARY TABLES"**. So
the fixture's machine does report one, and MCP now walks the channel
status table adjusting it.

**The step count is the tell: 6.05 million before this page, 22.04
million after.** Line 51 is `CB+,T IXF,T A9A`, a count-branch over
the whole table, and line 12 loops the machine-configuration count
table as well. The trail is now **004263.00 — printed p.73's first
word**.

### A multiply, the first in this corpus

Line 19 is `*(BU,24),T COMBO,40` — the operation is a **bare
asterisk**, and no page read before this one spells a multiply at
all. It compiles `030024.21 90`; line 26's `M+,T DISK(T IXG)`
compiles `010000.20 90`. **The same opcode byte**, told apart by bit
23 of the second group — the same shape the written minus has.

### And a fifth written minus, two lines below it

Line 20 is `-(BU,24),T 2COMB,20` with the familiar `.30`. **This
pair is the sharpest instance yet**, because each operand is the
*other half of one constant*:

```
p.63 line 21  T COMBO  VF,T TYBC+T MACBC+T REQBC
p.63 line 22  T 2COMB  VF,T TYBC+T MACBC
```

Multiply by the three-field width, subtract the two-field width — a
computation in which a wrong sign produces a different table offset
**in silence**. That is precisely what the 2026-10-19 unsigned-
subtract fix was protecting, and until p.69 there was one row in the
corpus to protect.

### A sixth `DD`-label dds — and the first from an entry-mode DD

Line 26's bare `M+,T DISK(T IXG)` takes length **eight** from
`T DISK`, which p.64 line 6 defines as `(8)DD(BU,8),1,1,0` — an
*octal entry-mode* DD. pp.66, 67 and 69 found this shape on plain
`DD(BU,1),0` labels; it carries identically here. **That was the one
row of forty-nine the deck got wrong first**, which is how the case
was found.

### Two immediates that prove their own field position

`KFI(BU,4),2` compiles `100000.00` and `KFI(BU,4),5` compiles
`240000.00` — the value times 2^14, left-justified in the eighteen-
bit address field. Their comments read *"-LOOK FOR CONSOLE"* and
*"-LOOK FOR A PRINTER"*, equipment codes 2 and 5 — which is **p.64's
REQUEST VALIDITY CHECK TABLE read back**, three pages after it was
transcribed.

### Where the range stands

```
merged 55 pages, 425 stand-ins checked against their definitions,
203 SYNs that agree with another page's SYN, 40 symbols external
```

printed pp.15-72 are in the image, gapless. **printed p.73 is next**
and the run names it: 004263.00.

## PRINTED p.71 — the range closes on `T ASIGN`'s forward branch, 2026-10-24

Thirty-six compiled rows, **all bit-exact on the first run**.

**Line 52 ends at 004215.00**, which is printed p.72 line 4 — and
004215.00 is `T A9`, the address p.65 line 9 branches to and the
boot run's PC trail has named since p.65 landed. **printed pp.15-71
are now contiguous in the image**, and the run stops at exactly the
first word p.72 would provide.

It also places five stand-ins: `T A5S` (p.68) and `T A8`, `T B8C`,
`T B8Z`, `T B8` (all p.66).

### Statements with no operation

Lines 1 and 2 print `,DFREE` and `,9.` — a comma and a field,
nothing before it. They are the **parameter block of p.70 line 56's
`B,DMCP`**, straddling the page break; that row's comment reads
*"-THEN UNLOAD WITH - SFREE -"*. A null operation compiles a half
word and both rows print one. `9.` is nine **words**, and the
injection that drops the dot reads `000000.11` for `000011.00` —
nine moving from the word field to the bit field, visible in both
halves of the printed pair.

### >>> Line 26 is a §13d row, and the octal field decides it <<<

At 1800 dpi the row prints `C0C024.02 C0`. The **six-digit octal
field contains two of those `C` glyphs** — and octal has no `C`, so
the drum dropped the left stroke on *every* zero in this row. That
is §13d's per-ROW artifact. The opcode byte's first glyph has the
same shape, so the row is `000024.02 00`, which p.66 line 4's
`R,T X1` (`000032.02 00`) says independently.

**That is the opposite call from p.66 line 5 three pages ago**,
where a `C` in a hex byte *was* a `C` (`4C`, not `40`). The
difference is that this row's octal field is contaminated and that
one's was not. §13e's rule — *"the hex byte is where a `C` is
ambiguous, the OCTAL pair is where it cannot be"* — made both
decisions, in opposite directions, within three pages.

### Where this leaves the arc

```
merged 54 pages, 412 stand-ins checked against their definitions,
189 SYNs that agree with another page's SYN, 37 symbols external
```

The external count has fallen from 42 to 37 over pp.68-71. The boot
run is unchanged at 004215.00 because `T A9`'s code is p.72's, so
**printed p.72 is the next page** and it is the one that moves the
run again.

## PRINTED p.70 — the written-minus count goes from two to four, 2026-10-24

Thirty-eight compiled rows, **all bit-exact on the first run**. It
places three stand-ins from two earlier pages: `T A3F1` (p.68),
`T A5A` and `T A5MA` (p.69).

### >>> A recorded fact was wrong, and this page corrected it <<<

The project's memory said *"only one deck in the corpus spells an
unsigned written-minus at all, MCP printed p.18 line 35"*. p.69 line
48 made it two. **Lines 37 and 40 here make it four**:

```
line 37  -(BU,18),T CHSXW,46
line 40  - (BU,4),T IXJ+0.42,46      (a space after the minus)
```

And the modifier is visible in both, against a plain row two lines
away each time:

```
line 36  ST,T ABSCH(T IXA),46    022027.20 D0
line 37  -(BU,18),T CHSXW,46     022027.30 10
line 39  L,T UNITK(T X3),46      004027.20 50
line 40  - (BU,4),T IXJ+0.42,46  004027.30 10
```

**Three rows across two pages now rest on that one bit**, and all
three would have compiled an *addition* before the 2026-10-19 fix —
which was itself found by typing in RefMan p.61's Figure 12 rather
than by any test. The memory has been corrected.

### p.69's weakest derivation is confirmed

`STATI = 0.26`, dds `(BU,1)`, was read off **one row** on p.69 — the
only symbol on that page not named `T something`, and therefore the
one with no corroboration. Line 45 here is `BB,STATI(T IXJ),T A5LC`
compiling `000000.32 86`, and 0o32 is 26.

### Two mnemonics new to the corpus

Line 12's `CBH` (byte `C8`) and line 19's `BBN` (byte `0A`), both
written as printed and reproduced by the assembler.

### Where the range stands

```
merged 53 pages, 398 stand-ins checked against their definitions,
177 SYNs that agree with another page's SYN, 40 symbols external
```

printed pp.15-70 are in the image, gapless, and the external count
has started *falling* — 42 after p.68, 40 now — because these pages
define more than they borrow. **printed p.71 is the last page**
before `T A9` (p.72 line 4) is reachable.

## PRINTED p.69 — the second written minus in the corpus, 2026-10-24

Forty-five compiled rows, **all bit-exact on the first run**. It
places p.68's last two forward references: line 2 is `T A3CB`
(004064.40), line 5 is `T C3Z` (004065.00).

### >>> A bare written minus, and it is only the second ever seen <<<

Line 48 is `-,T ABSUN(T IXM),46` — the **operation** is a single
minus sign.

The only other instance in the whole corpus is MCP printed p.18 line
35, and **that is the row that found a real model bug**: `fieldToSM`
returned sign 0 for every unsigned field and dropped the negative
sign modifier, so *every unsigned subtract in the model was an
addition*. It was found on 2026-10-19 by typing in RefMan p.61's
Figure 12.

**The listing shows the modifier, one bit wide:**

```
line 47  L,T UNITK(T X1),46   004027.20 50
line 48  -,T ABSUN(T IXM),46  003027.30 10
```

The second group's `.20` becomes `.30`. That is RefMan p.57's
"Unsigned, use −" and p.60's *"whether the sign of the storage
operand is taken as-is or is inverted"*. The injection that turns
the minus into a plus reads exactly `003027.20`, so **this row would
have been silently wrong before that fix** — and it is the only
check on it outside the deck written for it.

### Three more `DD`-label dds

Lines 8/18 (`CM0000,T INDZ`), 23 (`LF,T ONE`) and 26
(`CM1111,T INDC`) are bare and compile length one; p.61 lines 21, 25
and 28 define all three with `DD(BU,1)`. pp.66 and 67 each found one
such symbol — this page has three, so the shape is confirmed on
**five symbols across three pages**.

### One symbol that is not a `T` name

Line 24 is `KF,STATI(T IXJ)` compiling `000000.32 86 001000.23 10` —
a one-bit field at 0.26. Every other table offset on these pages is
`T something`; this one is not, which suggests a table declared
outside the ASSIGN program. Carried as a stand-in at 0.26 with
`(BU,1)`, both read off that row alone.

### Where the range stands

```
merged 52 pages, 381 stand-ins checked against their definitions,
159 SYNs that agree with another page's SYN, 42 symbols external
```

printed pp.15-69 are in the image, gapless. **pp.70 and 71 are all
that remain** before `T A9` (p.72 line 4) is reachable. p.69's `T B3`
at 004127.0 is p.70's line 5.

## PRINTED p.68 — twin blocks that check each other, 2026-10-24

Forty-one compiled rows, **all bit-exact on the first run**. It
places three of p.67's four forward references: line 7 is `T B7`
(004034.00), line 12 is `T A7D` (004035.00), line 30 is `T A3`
(004046.00). The fourth, `T C3Z`, is one word past the page and
belongs to p.69.

### >>> Two eight-line blocks that differ only in their index <<<

Lines 1-8 and lines 16-23 are the **same unit-availability test
written twice** — once on `T X3`, once on `T IXJ`:

```
line  1  000000.34 82  004034.34 02   BB,T UNAVL(T X3),T B7
line 16  000000.34 86  004045.34 02   BB,T UNAVL(T IXJ),T C7
```

**The binary differs in one nibble per row** — the index in the
opcode byte, `82` against `86`, which is `$2` against `$6`. Every
other field is identical: `T UNAVL` 0.34, `T UNASG` 0.35, `T UNRES`
0.76, the same `CT0011(BU,2)`, the same `BZB` on `T MODE`.

**That is a transcription check the page provides itself.** A
misread digit in either block disagrees with the other. The
injections show both halves: moving `T UNRES` fails **four** rows,
two in each block; moving `T IXJ` fails **six**, all in the second.
One symbol common to both, one that separates them.

This is a different kind of self-check from the ones this project
has relied on so far — those come from a *reference* agreeing with
its target's own location. This one comes from the program being
written twice.

### `$R+.32` is an expression on a system symbol

Line 38's `KC,T X3,$R+.32` compiles `000011.45 90`. `$R` is word 9
(`000011` octal) and `.45` has **bit 18 set**, the half-word
selector, so the operand is word 9's *second* half — which is where
line 37's `LC,T IXJ,$R` put the count being compared. The injection
reads `000011.05`.

### Where the range stands

```
merged 51 pages, 371 stand-ins checked against their definitions,
135 SYNs that agree with another page's SYN, 42 symbols external
```

printed pp.15-68 are in the image, gapless. **pp.69, 70 and 71
remain** before `T A9` (p.72 line 4) is reachable; p.68's own
forward references name part of what is on them — `T A3CB`
004064.40, `T C3Z` 004065.0, `T A3F1` 004132.0, `T A5A` 004137.0,
`T A5S` 004167.40.

## PRINTED p.67 — the assignment attempts, and a dds rule confirmed on a second kind of symbol, 2026-10-24

Thirty-eight compiled rows, **all bit-exact on the first run**. It
places both of p.66's forward references: line 5 is `T A2E` at
003775.00, line 50 is `T A7` at 004020.40.

### `T CTACH` and `T CTSCH` are the two halves of one word

p.61 lines 13-14 declare them `SYN(BU,18),T CTEMP+0.0` and
`SYN(BU,7),T CTEMP+0.25` — the **absolute** channel number and the
**symbolic** one, eighteen bits and seven, packed in one temp word.
Line 32 here is `L,T CTACH,46` compiling `003265.00`; line 25 is
`KF,T CTSCH` compiling `003265.31`. Declared six pages back, spent
here, and the bit offsets match to the digit (0o31 = 25).

### A second independent instance of a dds carried by a `DD` label

Line 41's `CM1111,T INDB` is bare and compiles `001000` — length
one — and p.61 line 24 made `T INDB` with `DD(BU,1),0`, not a SYN.
p.66 showed this with `T MODE` and `T INDD`; p.67 confirms it on a
different symbol, and its injection fails the row.

**Nine bare VFL statements on the page, and every dds comes from a
page already transcribed**: p.61's `T CTACH` (18), `T CTSCH` (7) and
`T INDB` (1); p.62's `T RLSYM` (7) and `T TYPE` (4); p.63's
`T EQUIP` (4) and `T UNITK` (4).

### Where the range stands

```
merged 50 pages, 361 stand-ins checked against their definitions,
120 SYNs that agree with another page's SYN, 41 symbols external
```

printed pp.15-67 are in the image, gapless. The trail stays at
004215.00 (`T A9`, p.72 line 4) — the run branches straight there
from p.65 line 9 and does not enter pp.66-67 yet. **pp.68-71 are what
remain**, four dense code pages; p.67's own forward references name
part of what is on them (`T A3` 004046.0, `T B7` 004034.0, `T A7D`
004035.0, `T C3Z` 004065.0).

## PRINTED p.66 — and a `C` misread as a ZERO, the mirror of §13, 2026-10-24

Forty-four compiled rows; forty-three bit-exact on the first run.
The page picks up exactly where p.65 left off — p.65's last line
branches to `T C1` and its line 37 to `T A2`, and lines 3 and 19 here
*are* those two labels, at 003733.40 and 003743.40.

**Line 1 is a halt, the fourth transcribed**: `BD,$` commented
*"-ILLEGAL REQUEST - MCP ERROR"*. The other three (p.6 line 1, p.54
line 55, p.55 line 12) are all table overflows; this one is not.

### Three bare VFL statements take their dds from a `DD` label

Lines 22, 39 and 44 are `CM0000,T INDD`, `CM0000,T MODE` and
`CM1111,T MODE` — all bare, all compiling `001000`, length one.
**Neither symbol is a SYN**: p.61 lines 22 and 26 define them with
`DD(BU,1),0`.

So C22-6531 printed p.31's dds sentence is about the **symbol**, not
about the card that made it. Every earlier confirmation of that rule
on this project has been against a SYN card; this page is where the
other kind shows.

### >>> The one row that was wrong reverses the direction of §13 <<<

Line 5's opcode byte was transcribed `40` and is `4C`.

**Every earlier instance of that pair is a ZERO taken for a `C`** —
§13 and its four sub-cases, going back to the MCP scan's own glyph
trap. **This is a `C` taken for a ZERO**, and it is the first.

Three things settle it, none of them the assembler:

1. At **1800 dpi** the glyph is an open curve with a clear gap,
   against the *closed ovals* of the three zeros in the same row's
   `003726`. 900 dpi was not enough — the same resolution that failed
   on p.55 line 40's `B0`.
2. The corpus prints `CBR` as `4C` in two rows transcribed long
   before this page (002252.00, 002272.40).
3. Plain `CB+` prints `48`. `48` is `01001000`, `4C` is `01001100` —
   one bit, which is what the `R` adds.

**Why it matters beyond the row.** §13 trains a reflex — *a `C` in a
hex byte is probably a zero* — which is right most of the time and
wrong here. A reflex applied in only one direction will eventually
turn a correct `C` into a wrong `0` with nothing to catch it, because
the octal fields cannot see a hex byte. The practice that catches it
is symmetric and was already written down for p.55: **when the
assembler and a hex byte disagree, re-render that byte at 1800 dpi
and grep the corpus for the mnemonic.** Recorded as
`listing_typography.md` §13f.

### Two expressions worth the note

Line 35's `T LAST+1.0(T IXA)` compiles `000001.22` — `T LAST` is
0.18 (0o22) and one *word* on is 1.18, so the word part and the bit
part move independently and the printed pair shows both.

Line 36's `T IOREQ-1` compiles `003372.51`. `T IOREQ` is 003373.0 and
the `-1` is **one bit**, landing at 003372.63; LVI's address field is
nineteen bits — eighteen of word and one of half word, as p.55 line
40 established — so it holds 003372 with the half-word bit set. The
injection changes *both* the word and that bit.

### Where the range stands

```
merged 49 pages, 347 stand-ins checked against their definitions,
107 SYNs that agree with another page's SYN, 39 symbols external
```

The trail is unchanged at 004215.00 (`T A9`), because the run
branches straight from p.65 line 9 and does not enter p.66's code
yet. **`T A9` is printed p.72 line 4**, found by bisection, so
pp.67-71 are what stand between the run and it — five dense code
pages of roughly forty rows each.

## >>> MCP EXECUTES ITS ASSIGN ROUTINE — printed pp.63, 64 and 65, 2026-10-24 <<<

**71 rows, all bit-exact on the first run**, and the ASSIGN program
is in the image from printed p.59 through p.65.

**The run goes past `T ASIGN`.** The PC trail had ended at
003701.00 from the moment p.58 landed; p.65 line 6 *is* that
address:

```
T ASIGN  SWAPI,12,$1,T ASAVE   -SAVE INDEXES
         000021.00 80  003274.30 E0
```

Every field checks against a page already transcribed: `000021` is
word 0o21 = 16+1 = `$1`; `003274` is `T ASAVE`, p.61 line 52's
`DRZ(BU,64),(15)`; and `.30` → bits 19-22 = 0110 = **twelve**.
Twelve index registers into a fifteen-word save area. Line 7 then
reads the caller's `XW` through `$15` — exactly what p.59's LINKAGE
FORMAT page says the caller plants. **The documentation page and the
code page agree.**

The trail is now **004215.00 = `T A9`**, p.65 line 9's forward
branch on a machine-configuration change, on printed p.66 or after.

### `(8)` is an octal entry mode, and one row is the whole proof

p.64's lines 6, 9, 12, 15, 18, 21, 24 and 27 are each
`(8)DD(BU,8),n,m,0` — **one statement compiling three 8-bit bytes**,
printed on three rows at three consecutive addresses.

Seven of the eight cannot tell the radix: their type codes are 1
through 7. **Line 27 can.** It is `(8)DD(BU,8),10,0,0`, commented
`-SAME AS ABOVE - TAPE`, and prints `010`. Tape's equipment code is
eight; ten octal is eight, ten decimal would print `012`. The
injection reads exactly that `012`.

**The assembler gained two things**: a numeric entry mode now takes
the ordinary field parse rather than the converted-datum one (it is
a radix, not a character set — C22-6531 defines `(R)` and
`eval_expr` has always honoured it on a *value*), and
`parse_statement_text` stopped discarding the entry on that path.

### The dds rule now checks from both ends

Seven bare VFL statements on p.65 take their dds from symbols this
project *derived* before p.62 was read. Line 27 is
`L,T UNCT(T IXE),46` with nothing written, compiling `010027.20 50`
— 010000/512 = 8 — from `T UNCT`'s own `SYN(BU,8)`. Likewise line 46
(`T RCAD`, 8), line 51 (`T TYPE`, 4) and line 52 (`T TYAD`, 8).

So the page that **declares** each symbol and the page that
**spends** it bare are both transcribed, and the bits agree. A dds
that was an inference three commits ago is now pinned from both
sides.

### Two more things the listing showed rather than argued

**An XW's value field is signed.** p.64 line 38 is
`T RCHSC XW,-T CHCUC-32.0,0,0` and prints `003721.00-` where every
XW transcribed before it printed `+`.

**A CNOP has two cases and these pages show both.** p.64 line 5 had
to pad and prints `000000.30 00`; p.65 line 5 was already rounded —
p.64's `DRZ` ends exactly at 003701.00 — and compiles **nothing at
all**, no location and no binary.

### A check retired for drifting, the second one

`mcp_end_of_prosa_bit_X0` read word 16, `$X0`, at the end of the run
and asserted the measured core size. That was a fact about a
**mid-run state**, true only while the run stopped before anything
reused the register. With p.65 in the image, MCP's ASSIGN path runs
and `$X0` ends holding what that path left.

**Nothing is lost**: `mcp_x_s_roof`, `mcp_comm_size_fixture_and_listing_agree`
and `mcp_placed_at_dest_first` cover the same fact from storage the
program wrote *on purpose*, and all three pass on the run that broke
this one. The precedent is `mcp_qsav_last_after_swap`, retired
2026-10-23. **Pin a check to storage the program wrote deliberately,
not to a register it happened to leave alone** — because the whole
point of this project is that the run keeps going further.

### Where the range stands

```
merged 48 pages, 335 stand-ins checked against their definitions,
88 SYNs that agree with another page's SYN, 35 symbols external
```

printed pp.15-65 are in the image, gapless, with p.47, p.59 and p.60
named as the three that compile nothing. **Printed p.66 onward is
next, and the run names its own target: `T A9` at 004215.00.**

## PRINTED pp.61 AND 62 — and p.62 confirms eleven derivations from four earlier pages, 2026-10-24

Thirty-two rows and seventy symbols between them, **all bit-exact on
the first run.**

`p.61` is the ASSIGN program's constants and index names; `p.62` is
its three tables and their SYN cards.

### >>> p.62 is the declaration page for what pp.55-58 had to infer <<<

Those four pages were transcribed before this one was read. Each
needed symbols it could only derive — from a length field's
arithmetic, from an octal pair in a location, or from a row that
wrote no dds at all. p.62 carries IBM's own SYN cards:

| derived on | p.62's card |
|---|---|
| `T UNCT` (BU,8) 0.28 — pp.54, 58 | line 10 `SYN(BU,08),0.28` |
| `T RJECT` 0.37 — p.58 | line 12 `SYN(BU,1),0.37` |
| **`T LPPEN` (BU,1) 0.39 — p.58** | **line 14 `SYN(BU,1),0.39`** |
| `T LREFN` (BU,12) 0.40 — p.56 | line 15 `SYN(BU,12),0.40` |
| `T IODCT` (BU,12) 0.52 — p.56 | line 16 `SYN(BU,12),0.52` |
| `T RLSYM` 0.11 — p.55 | line 35 `SYN(BU,7),0.11` |
| `T LAST` 0.18 — pp.57, 58 | line 36 `SYN(BU,1),0.18` |
| `T FREEL` 0.28 — p.56 | line 38 `SYN(BU,18),0.28` |
| `T TYPE` (BU,4) 0.03 — pp.54, 55 | line 33 `SYN(BU,4),0.03` |
| `T IOREQ` 003373.0 — pp.57, 58 | line 28, its own location |
| `T UIORQ` 003514.0 — p.57 | line 41, its own location |

**Eleven for eleven.** The `(BU,1)` on `T LPPEN` is worth naming
twice: p.58 lines 31 and 35 write `CM0000,T LPPEN(L XPP)` with no dds
on the statement, so the length could *only* come from the symbol,
and the deck gave it `SYN(BU,1)` on that reasoning alone. Line 14 is
that card.

**And `T FREEL` and `T UNCT` are both 0.28 because they are in
different tables.** p.56's deck recorded that as *"a coincidence
worth not re-deriving later"*. `T UNCT` is in the PP REFERENCE
TABLE's SYN block (lines 9-17); `T FREEL` is in the I/O REQUEST
TABLE's (lines 30-39). The page shows it rather than arguing it.

### p.61's one XW predicted two addresses on p.62

p.61 line 19 is `T SAV XW,T PREFT,T PPC,T PPREF` compiling
`003317.00+ 000 000024 003314`. p.62 line 6 defines `T PREFT` at
003317.00 and line 3 defines `T PPREF` at 003314.00. Both to the bit,
from a row on the page before — and the count group `000024` = 20 is
p.60's `T PPC SYN,20`, which p.60 itself prints with `NULL` because a
SYN compiles nothing.

### `(.39)1` places a value at a bit, and `T LPPEN` is bit .39

p.62 line 21 is `XW,0(.39)1`, commented *"-NECESSARY FOR LAST ENTRY
BIT"*, compiling `000000.00+ 000 000100 000000`. An XW's third group
is its 18-bit count field at bits 28-45, so bit .39 is offset eleven
within it and a 1 there is 2^6 = 0o100. Line 14 says what bit .39 is:
`T LPPEN ... -LAST ENTRY BIT`. The XW and the SYN card agree about
which bit, and each comment names the same thing. Moving it to
`(.38)1` prints `000200` — the encoding is legible because the octal
doubles.

### One assembler gap, forced by this page

**`dr_count` evaluated its dimension against an EMPTY symbol table**,
so only a literal could resolve. That was enough while every `DR`
this project had read was `DR(BU,64),(3)` or `DRZ(BU),100`. p.62 has
six rows of `DRZ(BU,64),(T PPC)` and the like — the counts are p.60's
six SYN cards — and line 42 is `T UIOC-1`, an **expression** in a
symbol. `dr_count` now takes the symbol table.

That `-1` is load-bearing in four places: its injection moves
`T FSTRE` and `T UFRE`, changes line 43's VF from `000000.40+` to
`000000.00+`, and changes line 47's CNOP from `000000.30 00` to
`000000.00 00` because it no longer has to pad.

### Where the range stands

pp.61 and 62 are **not in the image yet** — pp.63, 64 and 65 are
still unread and `prosa.py` wants it gapless. p.62 ends at 003647.00
(line 51's `DRZ(BU,64),T UFRC`, 20 words from 003623.00), so p.63
starts there. `T ASIGN` is p.65 line 6.

## THE ASSIGN PROGRAM — printed pp.59-65 surveyed, and two of them are free, 2026-10-24

The boot run's trail now points at `T ASIGN` (003701.00), and
`decks/mcp_bootstrap_p27.strap` line 60 is `X241 B,T ASIGN`, so it is
a genuine branch target despite the `T` prefix. **Printed p.65 line 6
is 003701.00** — the bisection landed on the nose. Reaching it means
pp.59-65, because `prosa.py` wants the range gapless.

**Surveyed before transcribing, and the survey changes the estimate.**

### printed p.59 and p.60 COMPILE NOTHING — they are p.47's shape

`p.59` has 26 lines of which only line 1 (`003264.40 * SLC,$`)
touches the counter. It is the section heading — *"I/O ASSIGNMENT
--- ASSIGN ---"* — plus **THE ASSIGN PROGRAM LINKAGE FORMAT**,
written out as a worked call exactly as p.47 does for DECODE:

```
         LVI,$15,Y
         B,T ASIGN
Y        XW,A,B,,C
         BEW,$            RETURN LOCATION

LET A = STATUS OF MACHINE
    ZERO = NO MACHINE CONF. CHANGE
    NOT ZERO = MACHINE CONF. CHANGE
LET B = EXIT DISPOSITION
LET C = MODE
    ZERO = OVERLAP MODE
    NOT ZERO = NOT OVERLAP MODE
```

That is the convention `X241` on printed p.27 uses, and it says what
the caller must plant: a four-field `XW` and a `BEW,$` to come back
to.

`p.60` is *"SYN CARDS FOR THE LENGTHS OF THE THREE TABLES"* — six
integer SYNs, and **the BINARY OUTPUT column prints `NULL` on every
one**, which is the listing saying no word was compiled:

```
line  6  +00000024  NULL  T PPC   SYN,20
line  7  +00000120  NULL  T IOC   SYN,80
line  8  +00000062  NULL  T FRC   SYN,50   -THE FIRST REEL TABLE LENGHT
line 10  +00000002  NULL  T UPPC  SYN,2    -NOT OVERLAP PP REF TABLE LENGTH
line 11  +00000024  NULL  T UIOC  SYN,20   -NOT OVERLAP I/O REQ TABLE LENGTH
line 12  +00000024  NULL  T UFRC  SYN,20   -NOT OVERLAPFIRST REEL TABLE LENGHT
```

The location column prints the resolved value in octal with a
leading `+` and it checks: 20 = 0o24, 80 = 0o120, 50 = 0o62, 2 = 0o2.
**These are INTEGER SYNs** — no dot — which is the classification
printed p.48 forced `strap_asm` to get right (`sym_int`).

**So both go in `NO_DECK_PAGES` beside p.47.** That is two of the
seven pages for free, and it is the first time a *second* kind of
no-deck page has turned up: p.47 and p.59 are documentation, p.60 is
declarations the listing itself marks `NULL`.

### And p.60's lengths are visible in p.62's addresses

p.62's location column jumps by exactly those counts: line 7
(003320.00) to line 8 (003344.00) is 0o24 = **20** = `T PPC`; line 28
(003373.00) to line 29 (003513.00) is 0o120 = **80** = `T IOC`; line
48 (003541.00) to line 51 (003623.00) is 0o62 = **50** = `T FRC`. So
p.62 is where the three tables are reserved, and p.60's SYN cards are
what size them. Those are `DR`-shaped holes, which is the ONE kind of
hole `prosa.py` accepts — and it will want them declared as `DR`s,
not left implicit.

### What is left, and in what order

* **p.61** — 56 lines, about 20 compiled, the rest SYNs: the ASSIGN
  program's symbol declarations, including its index-register names
  (lines 31-47 resolve to 000021-000032, which are words 17-26, i.e.
  `$1`-`$10`).
* **p.62** — the three tables and their not-overlap counterparts.
* **pp.63, 64** — not yet surveyed.
* **p.65** — `T ASIGN` is its line 6.

## PRINTED pp.55, 56 AND 57 — the gap closes and the image reaches p.58, 2026-10-24

**123 rows, 122 of them bit-exact on the first run.** `prosa.py` is
why these three exist: p.58 was transcribed first and could not join
the image, because the record then had a hole at 003106-003236 and
that check refused it. Rather than weaken the check, the pages behind
the hole were read.

```
printed p.55  44 lines, all 44 compile   003105.40 - 003147.00
printed p.56  56 lines, 41 compile       003147.40 - 003205.40
printed p.57  38 lines, all 38 compile   003206.00 - 003237.00
```

**pp.54-58 are now contiguous to the bit.** Each page's last
instruction ends exactly on the next page's first printed location —
p.54 line 56 → p.55 line 1, p.55 line 44 → p.56 line 5, p.56 line 56
→ p.57 line 1, p.57 line 38 → p.58 line 5 — and `prosa.py` rechecks
the whole range on every build.

### What they are

`p.55` is the CHANNEL SYMBOL TABLE SEARCH: an IOD card's channel name
looked up, entered if absent, the unit slot pointed at it. Its line
12 is a HALT — `BD,$` commented *"-INTERNAL CHANNEL TABLE EXCEEDED"*
— the third deliberate stop transcribed, after p.6 line 1 and p.54
line 55. All three are table overflows.

`p.56` is THE REEL CARD ROUTINE, the FINAL ROUTINE and the sort's
entry, in three boxed sections the listing names itself. Every branch
off the page lands on one already transcribed: `L ERROR`, `L NORM`
and `L ERR4` on p.58, `L FIN3` and `L SKIP` on p.57.

`p.57` is the IOREQ SEARCH AND SORT, and **its last seven lines are
p.58's error tail to the bit** — p.57 lines 32-35 and 37 equal p.58
lines 31, 33, 34, 35 and 38, differing only in line 36's branch
target. The normal path and the error path do the same housekeeping
and differ in where they go.

### The one row that was wrong, and 900 dpi is what got it wrong

p.55 line 40's opcode byte was transcribed `80` and is `B0`.
`listing_typography.md` §11 already names this pair — *"B and 8 are
the only pair in 0-9A-F that differ mainly in one vertical stroke,
and that stroke is the first thing a worn drum printer loses"* — and
the memory records p.3 line 10 as the instance that cost three
commits. **The standing practice is "900 dpi for hex", and 900 dpi
got this one wrong too.**

At **1800 dpi** it is not close: the glyph has a straight vertical
left stroke with two bowls hung off it, which is a B; an 8 is two
closed round bowls with no straight edge. And the corpus settles it
without the assembler — five rows already transcribed from earlier
pages print `V+` as `B0` (000702.00, 001167.40, 001540.40, 001622.00,
001623.00).

**The practice this adds:** when the assembler and a hex byte
disagree, re-render *that byte* at 1800 dpi and grep the corpus for
the mnemonic. Two cheap checks, neither of which is "believe the
model" — the listing is the oracle, and a disagreement is a prompt to
look again, not an answer.

### The dds rule demonstrated on one operand across two pages

p.55 line 18 is `K(BU,48),L BLANK` → `060000.21 10`.
p.56 line 11 is `K,L BLANK` → `060600.21 10`.

Same symbol, same operation, one page apart, and the only difference
is whether the dds was written. The `0600` is the BYTE SIZE, which
p.54 carries as `SYN(BU,48,6)` and derived by measuring a blank count
in pixels. The injection bites on the bare row only.

**And the length field is arithmetic**: the second group's leading
octal is the field length × 512 — `010000` = 8, `014000` = 12,
`022000` = 18, `060000` = 48. That is how p.56's `T IODCT` and
`T LREFN` were given `SYN(BU,12)` from rows that write no dds at all,
the same way p.58 forced `T LPPEN`'s.

### What the image and the run say now

```
merged 43 pages, 313 stand-ins checked against their definitions,
55 SYNs that agree with another page's SYN, 33 symbols external
```
(was 39 pages, 265, 25 and 39 before p.58.)

**The run goes through `L NORM` instead of stopping at it.** Nine
swaps execute where five did — including `L NORM`'s own `SWAPI,8` at
half-word 3391, twice, and p.58 line 38's `SWAPI,3` at 3388. The
trail is now **half-word 3970 = 003701.00**, which
`decks/mcp_bootstrap_p27.strap` carries as `T ASIGN SYN,(8)3701.0` —
a stand-in for a page still unread, around printed p.65. `X ERR AD`
is still zero: no error site runs.

### What is next

**Printed p.59 onward.** p.59 line 1 is `003264.40 * SLC,$` followed
by `PRND`, so the page boundary is already confirmed. The run's own
trail names where it wants to go: whatever defines `T ASIGN` at
003701. The same location-column bisection that found p.58 will find
it — about 0o50 words a page, so 003701 is roughly printed p.65, and
the pages between are what the next `prosa.py` refusal will ask for.

## PRINTED p.58 IS TRANSCRIBED — the page the boot run was stopping at, 2026-10-24

THE DISPATCHER'S TWO RETURNS. Thirty-two compiled rows out of
forty-two lines (5-6 and 12-41), bit-exact. The run had been ending
by branching into zeroed storage at 003237.40 — printed p.54's
`L NORM SYN,(8)3237.40` — and **line 5 is that symbol**.

### It was found by bisecting the location column, not by reading code

MCP's listing is in address order, so the LOCATION column alone
answers "which page defines this?". Three renders at 600 dpi:

```
printed p.55  line 6 = 003112.40 ... line 21 = 003125.40
printed p.57  line 6 = 003212.00 ... line 21 = 003223.40
printed p.57  line 38 003237.00   003237.50 00        B,L NORM
printed p.58  line  5 003237.40   002571.00 80  000023.20 E0   L NORM  SWAPI,8,L TY,L IODX
```

p.57's **last** compiled line is a branch to the very next half
word. About 0o50 words a page is the rate; the column restarting at
printed pp.63, 105 and 111 is the only thing that can break the
bisection.

### What the page is

Two exits from one dispatcher, named by the listing's own comments:
`L NORM` (003237.40) is "-SWAP 8 INDICES." then "-DISPATCHER NORMAL
RETURN."; `L ERROR` (003241.00) heads the ERROR RETURN ROUTINE, which
zeroes this program's IOREQ and FREEL slots, sets the reject bit,
steps the PPREF index and ends at "-DISPATCHER ERROR RETURN."

**Both return through `$15` and they differ by a half word** — line 6
is `B,2.0($15)`, line 41 is `B,1.32($15)`. The caller plants a
two-word linkage and the callee picks the arm, which is the same
convention printed p.43 line 54 uses to return from `S CA6`. And
**lines 5 and 39 are the same instruction to the bit**
(`SWAPI,8,L TY,L IODX` → `002571.00 80 000023.20 E0`): the error path
rejoins the normal path's index restore, then takes the other return.

### Sixteen stand-ins re-derived from this page's own binary, all sixteen agreeing

Each had been given a value by an earlier deck from a different page.
Each was re-derived here from p.58's printed binary alone — an index
number out of an opcode byte's low nibble, a bit offset out of a
location's octal pair — before the existing values were looked at.
`L TY`, `L IODX`, `L XPP`, `L XIO`, `L XFR`, `L XNT`, `L WORKX`,
`L FINB`, `L OVBIT`, `L SAVEY`, `L SAVEZ`, `L NOSAV`, `T UNCT`,
`T LPPEN`, `L NORM`, `L ERROR`.

**The sharpest is `L XNT`.** Line 23 is `SC,L XNT,L XNT` and pins it
twice in one row: the address is `000031` = word 0o31 = 16+9, and the
J field `.23` = 010011 has bits 19-22 = 1001. Two independent fields
of the same printed half-word giving 9.

Five symbols are new and derived here: `L SAVE` (8)2602.0 — lines 13
and 36 are the save and the restore of one index at the same address,
differing only in bit 23 — plus `T IOREQ`, `T LAST`, `T RJECT` and
`LASTPP`.

### Thirty of thirty-two were bit-exact first try; the other two are the finding

Lines 31 and 35 failed with `000000` where the listing prints
`001000` in the second group — the **field length**.

**This page is the first that writes the operation BARE.** printed
p.53 and printed p.57 only ever write
`CM1111(BU,1),T LPPEN(L XPP)`, with the dds on the statement, so
`T LPPEN`'s own dds never had to exist. Lines 31 and 35 are
`CM0000,T LPPEN(L XPP)` and `CM1111,T LPPEN(L XPP)` with nothing on
the statement, and a bare VFL statement takes its operand symbol's
dds — C22-6531 printed p.31 again, the same sentence that has now
cost four separate corrections.

So `T LPPEN` is `SYN(BU,1)`, and **the listing is what says so**: line
30's `CM1111(BU,1),T RJECT(L XPP)` and line 35's bare
`CM1111,T LPPEN(L XPP)` print the same second group, `001000.36 F0`.
`decks/mcp_bootstrap_p53.strap` got the same change in the same
commit — `merge` treats two identical SYNs as a confirmation and two
that disagree as a hard failure, so the pair has to move together.

### `.22` means three different things on this page

Lines 19, 20, 24, 25 and 29 all print `.22` in their first address
group, and it is not the same field:

* line 19 `LX,L XNT,0.0(L WORKX)` — the **J field** (1001 = 9), with
  the modifying index in the opcode byte (`1A` → 10).
* line 20 `BZB,T LAST(L WORKX)` — a **bit address**, 0o22 = 18.
* lines 24, 25, 29 `Z,0.0(index)` — **constant**. All three print
  `000000.22` and differ only in the opcode byte (09, 0A, 04), so the
  index is carried there.

The first reading tried to make `.22` an index field and could not:
two rows naming different index registers print the same `.22`.

### Four injections, all caught

`L SAVE` +1 → 2 FAIL (lines 13, 36); `T LPPEN` loses its dds → 2 FAIL
(lines 31, 35); `T LAST` 0.18→0.17 → 1 FAIL (line 20); `L IODX`
$3→$2 → 2 FAIL (lines 5, 39, the page's two SWAPIs).

### >>> AND IT IS NOT IN THE IMAGE YET, WHICH IS THE NEXT JOB <<<

Adding p.58 to `mcp_image.MCP_IPL_PAGES` makes `prosa.py` refuse the
record, correctly:

```
prosa.py: printed pp.15-36 do not account for every word.
  words MISSING with no reservation: 003106 ... 003236
```

That hole is **printed pp.55, 56 and 57**, which have code on them
and have not been read. `prosa.py` allows exactly one kind of hole —
a reservation **proved by a `DR` in the listing**, storage the
program means to leave as the loader found it — and three unread
pages are not that. Declaring them reserved would be precisely the
lie that check exists to catch.

**So pp.55-57 are the next three transcriptions**, and when they land
the range becomes `range(15, 59)` and p.58 joins with them. Until
then p.58 stands on its own verifier, which needs no image. The run
still stops at 003237.40 — the page is transcribed, not yet loaded.

What is already legible of p.57: `L SEARE`, `L SEARG`, `L SKIP`,
`L FIN3`, and an IOREQ search loop whose line 22 is
`SWAPI,1,0.0(L WORKX),0.0(L IODX)  -SWAP IOREQ`.

## >>> MCP ACCEPTS ITS IOD CARD. SIXTY-FOUR IS NOT A MULTIPLE OF SIX, 2026-10-24 <<<

**The model was refusing a store IBM's operating system depends on,
and the cost was ten characters out of eighty.**

### What was measured, in the order it was measured

The question carried in since commit `c6e3e60` was why MCP rejects the
IOD card. Four probe runs had established that UNCODE *was* handed the
fixture's card and that the card is correctly punched — columns 1
(`12-2` = `B`), 10 (`12-9` = `I`), 11 (`11-6` = `O`), 12 (`12-4` =
`D`). So the next thing to read was what the conversion produced.

Printed p.38 lines 11-20 are two call blocks. The first hands `S CA6`
the card's address, `CF,80` — **eighty columns**, printed as `000120`
and reproduced bit-exactly by `decks/mcp_bootstrap_p38.strap` — and
`Y UCBF1` (002327.00) to convert into. The second hands `S BRK8`
`Y UCBF1+.54` and 53 characters, into `Y UCBF2` (002337.00).

`Y UCBF1` word 0 read `0xc800000000000390`, with words 1-7 zero. As
ten 6-bit characters that is `0o62`, eight zeros, `0o71` — **`B`,
eight blanks, `I`** — and bits 60-63, the top of character eleven,
are zero. **Exactly ten characters out of eighty**, and the card has
`IOD`.

### Why ten, and the self-check that makes it mean the word boundary

Printed p.43 is the converter and its loop is explicit: line 19's
`CT0011(V+I)(BU,3)` and line 23's `LF(V+I)(BU,9)` read **twelve bits**
— one card column, twelve rows — line 49's
`ST(V+I)(BU,6,6),.6($5)` stores **six**, and line 52's `CB,$4,Q P`
counts the eighty down. Ten passes × 6 bits = 60 bits. **Character
ten lands at bits 60-65 of a 64-bit word and straddles the
boundary.**

**The input side proves it is the boundary and not the glyph.** Twelve
bits per column straddles too — column 6's nine-bit `LF` sits at bits
63-71 — so if crossing *loads* were also refused, `$4` would have
stuck at column 6 and character 9 would be a blank. It is `0o71`,
`I`, read from column 10. Crossing loads worked. The store was the
sole governor, and ten is arithmetic, not coincidence.

### The mechanism, found in the code and not guessed

`bsv/StretchExecute.bsv`'s ST arm read
`if (immediate || fieldCrosses(ea, len_)) setOpInvalid`. And the
refusal cost more than the one character: `vflOk = False` also gates
the progressive-index advance (line 2956), so **`$5` stayed at bit 60
and the remaining seventy characters were refused at the same
place.** That is why words 1-7 were zero rather than holding the rest
of the card.

So `Y UCBF2` held `I` and blanks; printed p.38 line 26's
`K(BU,48),Y TYPMK($13)` compared it against `Y IOD MK`
(`0xe66d000000000000`, measured); line 28's `BZAEZ,Y MKEAR` was
taken; and MCP left through printed p.25 line 44's
`B,X 223  -NOT IOD OR REEL CARD`.

**It was never a documented restriction.** `StretchExecute.bsv`'s own
header recorded it as the one-write-per-rule toolchain limit, in the
same breath as "Transmit moves only one word" — which was the same
limit, and was lifted the same way in October. Rule 4 wants a primary
source for a semantic, and **printed p.43 line 49 is one**: IBM's
operating system stores a crossing VFL field in its card converter.

### How it is built

`StretchStorage.writeWordTail` writes a **register** where
`writeWord` writes a **wire**, so the ST arm can call both in one
`execute()` without the G0004 conflict a second `writeWord` would be;
`memCtl` drains the register into the store queue on the following
clock, ahead of anything newer, and holds reads off while it waits.
`insertFieldBitsPair` in `StretchVFL.bsv` does the 128-bit insert and
cuts it at the word boundary — the write-side mirror of
`extractFieldBits`. `StretchCore`'s `busyXfer` gains
`st.storeTailPending()`, so nothing is armed for the one clock the
tail waits. **`StretchCore`'s FSM was not touched**, which the old
`bsv/README.md` item 3 predicted it would have to be.

### What it changed, and the three checks were written first

`tests/gen_mcp_boot_tb.py`'s `mcp_ucbf1_0`, `mcp_ucbf1_1` and
`mcp_ucbf2_0` were computed in Python from `strap/iocd.card_text`
**before the arm existed**, and failed in the exact way a stuck
output pointer fails. They now read `0xc800000000000399`,
`0xb400000000000000` and `0xe66d000000000000` — and the third is not
a prediction from the card but the value **measured at `Y IOD MK`**,
so the check says the type field MCP reads out of the card is
bit-for-bit the mark MCP tests it with.

Then the run went further and four checks moved. Re-measured, not
re-predicted:

* **`mcp_x_err_ad` is zero** — and for the opposite reason to the
  first time it was zero. Not "no error site ran because MCP stopped
  dead", but **MCP does not take the error exit at all.**
* **`mcp_indicators_word11` is `0x1248`** — `AL`, `RZ`, `XH`,
  `XVGZ`. **OP is out of the word again.**
* **The PC is 0 and the trail is 3391.** MCP goes on into printed
  p.54's TAPE IOD ROUTINE and branches to `L NORM`, which p.54 line
  87 compiles as `SYN,(8)3237.40` — a stand-in for a symbol on a page
  not yet transcribed. 003237.40 holds zeros, and a zero half-word is
  BRANCH ENABLED to 0.0.
* **Five swaps now execute where one did.** Half-words 2649 (printed
  p.43's `Q FIN`), 2429 and 2436 (002276 and 002302 — printed p.40's
  `Y REELC`, the two swaps on a card's path), 3006 and 3013.

`gen_tb.py` gained `pc_trail_check` for this: when a run ends by
branching into zeros the PC is 0 for every such run, so the **trail**
is the datum, and a `$display` is not a check.

### A negative result worth the line

**The OP refusal at half-word 1304 (001214.00, printed p.24's time
conversion) is NOT the crossing-field store.** Building the store
would have cleared it if it were; `op_trail` still reports exactly
one rise, still at that address. That open question stays open and is
one hypothesis narrower. An exact locator in `StretchCore` remains
the right tool for it, not another probe.

### Two injections, and one of them survived

**Caught:** drop `st.writeWordTail(w0 + 1, tpl_2(np))` and
`mcp_ucbf1_0` still PASSES — the head word is written — while
`mcp_ucbf1_1` fails at `0x3400000000000000` against
`0xb400000000000000`. The two missing bits are exactly character
ten's low two: `D`, wholly inside the tail word, still lands through
its own non-crossing store, so **only the straddling character is
lost**. Four more checks fail with it and the run returns to MCP's
error exit at half-word 239.

**Survived:** remove `st.storeTailPending()` from `busyXfer` and both
the new deck — including its deliberately back-to-back block — and
the whole boot run stay green, with no `LOST` message. The collision
is unreachable at this pipeline's latency: two stores cannot be one
clock apart. **It is kept anyway**, because without it the tail's
correctness rests on a timing property nothing states, and the
failure mode is a word dropped in silence. Recorded here because a
guard no test can reach is exactly what a later reader would
otherwise assume was tested.

**AND "UNREACHABLE" IS A CLAIM ABOUT *THIS* PIPELINE.** The ordering
is MCP first, then cycle accuracy, and the cycle-accurate rebuild
(`5g`, `microarchitecture_plan.md`) changes exactly the latency that
makes the collision unreachable — a multi-cycle E-box retiring two
stores closer together is the whole point of it. **So the guard is
load-bearing for the rebuild rather than for today**, and
`StretchStorage`'s `$display` is the thing that will say so. Put this
on the rebuild's list: when the E-box becomes multi-cycle, re-run the
`busyXfer` injection against `decks/vfl_crossing_store.strap` block 2
and expect it to be caught.

**One more thing the rebuild inherits:** `recentStore()` reports the
head's address for one clock and the tail's for the next, and the
look-ahead's interlock compares one `storeAddr` per level. A level
loaded on the head's clock that fetches the TAIL word sees no
hazard — a two-clock window where the head write's own is one.
`decks/store_close_to_fetch.strap` and `store_then_execute.strap` are
the sections that would show it.

### And the deck corrected itself — `LVI`'s address field is 19 bits

`decks/vfl_crossing_store.strap` (twelve checks, every expectation
derived in Python from Reference Manual printed p.21 and p.31 before
the arm existed, every target starting as all ones) set up its
progressive block with `LVI,$X2,TE+.60` and the stores landed at bits
32 and 38.

**`LVI`'s address field is eighteen bits of word and ONE of half
word.** A bit offset of 60 is not expressible in it and became 32.
Printed p.43 proves it on one page: line 33's `LVI,$3,5.0` compiles
as `000005.07 01` and line 38's `LVI,$3,5.32` as `000005.47 01` —
differing **in bit 18 alone**, with `$3` in bits 19-22 and the flag
in bit 23 unchanged. Both rows are checked bit-exactly by
`verify_mcp_bootstrap_p43.py`.

**And IBM never asks for a finer one.** Every `LVI` in the converter
uses `.0` or `.32` — lines 33, 38, 42, 44. A full 24-bit bit address
comes from a **data word**, which is exactly why printed p.38 line 15
is `VF,Y UCBF1` and printed p.43 line 15 reads it with
`LV,$5,1.0($15)`. The deck uses that idiom now.

**The assembler rounded silently, and no diagnostic was added.**
Nothing this project has read says whether real STRAP diagnosed an
operand its address field cannot hold, and rule 4 forbids inventing
one. **Open item:** if a source turns up, `eval_addr_field` is where
the check would go. Until then this paragraph is the warning.

### What this unblocks: `L NORM` is printed p.58 line 5, and it was found by bisection

The run stops at a symbol whose page had not been transcribed, which
is the cleanest possible signal for which page is next — and the
LOCATION column answers it without reading a word of code. MCP's
listing is in address order, so **bisect on the octal address**
(the practice note in memory; the column restarts at printed pp.63,
105 and 111, which is the only thing that can break it).

Rendering the location column alone, at 600 dpi, three pages:

```
printed p.55  line 6 = 003112.40 ... line 21 = 003125.40
printed p.57  line 6 = 003212.00 ... line 21 = 003223.40
```

About 0o50 words a page, so 003237 is on p.57 or just past it. It is
just past it, and the way it ends is the useful part:

```
printed p.57  line 38  003237.00   003237.50 00        B,L NORM
printed p.58  line  5  003237.40   002571.00 80  000023.20 E0   L NORM  SWAPI,8,L...
printed p.58  line  6  003240.40   000002.10 0F        B,2.0($15)
```

**`L NORM` is the first compiled line of printed p.58**, and p.57's
last line is a branch to the very next half-word. It is a NORMAL
RETURN: restore eight index registers with a `SWAPI,8` and return
through `$15`, which is the same linkage printed p.43 line 53's
`Q FIN  SWAPI,6,Q SAV,$1` uses one routine down. `decks/`'s p.54
`SYN,(8)3237.40` for it is confirmed exactly.

**PRINTED p.58 IS THE NEXT PAGE.** Its neighbourhood is already
legible: p.57 carries `L SEARE`, `L SEARG`, `L SKIP`, `L FIN3` and an
IOREQ search loop (`SWAPI,1,0.0(L WORKX),0.0(L IODX)  -SWAP IOREQ`),
and p.58 opens into `L ERROR` at 003241.00 with `L ERRA` at
003245.40. So the model is about to need whatever those swaps and
`CB+` loops do — and **both swaps visible on these two pages are
`SWAPI`** (p.57 line 22 and p.58 line 5), which is built. Backward
`SWAP` is the one thing still refused, and neither page asks for it.

`boot_plan.md` A3's remaining piece — getting IOD/REEL/MCPP cards
onto the system tape the way the real system did — is unchanged by
this, but the card it would deliver is now one MCP accepts.

## THE `$4` GAP IS CLOSED, AND A MECHANISM CLAIM IS CORRECTED, 2026-10-24

Four boot runs with temporary probes, no code changed. The probes are
removed again; what they measured is here.

### UNCODE *was* handed the fixture's IOD card

The gap flagged since commit `c6e3e60` — "that printed p.25 line
32's `$4` really does point at the area the fixture punches into" —
is closed. Reading the sixteen index registers at the end of the run:

```
$4  value 005601.00      $7  value 005601.00
$14 value 001435.00      $15 value 005603.00
```

`0o5601` is **the terminator IOD card's slot**: `strap/prosa.py`
punches six cards fifteen words apart from `X IN END` = `0o5466`, and
the sixth is at `0o5466 + 5×15 = 0o5601`. `$14` is `X 222A`
(001435.00), which printed p.25 line 35 loads. And `$15` is
`2.0($7)`, which is exactly what printed p.40 line 39's
`LVE,$15,2.0($14)` computes by chaining through line 43's
`,2.0($7)`.

A sweep of the whole card region confirms the card is there and
intact: six images fifteen words apart, the terminator's first word
`0x8800000000000000` — bits 0-11 are `100010000000`, **the exact
pattern printed p.38 line 7 tests for**.

### A mechanism claim from commit 869d4a0 was wrong

That commit said *"printed p.40 line 40 is `Y UER`'s `Z,0.0($15)` —
UNCODE's error exit zeroes that slot"*, with "that slot" meaning
`X 222A`. **It zeroes the BREAK-DOWN TABLE, not `X 222A`**: `$15` is
`2.0($7)` = 005603.00, not the parameter word. `X 222A` reads zero
because nothing ever wrote it, which is a weaker fact than the
commit claimed.

**The conclusion survives on better evidence.** `Y JCCER` and `Y UER`
both return through `2.32($14)`, and they differ in what they leave
at `0.0($15)`: JCCER writes fifteen words (`T,15,Y UCBF2,0.0($15)`),
UER writes a zero. The break-down table at 005603 **and the five
words after it** are all zero, so UER ran and JCCER did not.

### And the break-down output is not where printed p.25 line 43 points

That is the new open question. `S BRK8` demonstrably runs — the PC
trail reached it and p.44's tables changed the run — but 005603
onward is empty, so its output went somewhere else. Either the OUT
parameter it is given is not `2.0($7)`, or the breakdown produced
nothing.

### The likely reason the card is rejected, stated as a hypothesis

`C22-6728` printed p.88 says IOD cards *"perform the same function
for MCP as they do for the problem program"* — i.e. they are
**job-control cards**, and printed p.52's dispatch compares a
**broken-down field**, not a fixed column. The fixture's terminator
card carries `IOD` in **columns 10-13**, the IOCD layout, because
that is what printed p.19's IOCD-scan terminator test reads — in
Hollerith, before any conversion.

**So the same card may be right for p.19 and wrong for UNCODE.** If
`S BRK8` splits on commas and the card has none, the first field is
whatever precedes column 10 — blanks — and no type mark matches.

*This is a hypothesis with a mechanism, not a measurement.* What
would settle it is finding where the break-down output goes, which
is the question above.

### >>> AND IT WAS WRONG, 2026-10-24. BOTH HALVES. <<<

Kept above rather than deleted, because it was wrong in a way worth
being able to find again: it was a mechanism argued from two
documents, and it named the card when the fault was in the model.

**The card never needed commas.** Printed p.38 line 18 is
`VF,Y UCBF1+.54` — bit 54, character ten, **column 10**, exactly
where `C22-6728` printed p.88 puts the card type. The break-down
starts where the fixture already punches. Field splitting was never
in play.

**And "where does the break-down output go" dissolves.** It goes to
`Y UCBF2` (002337.00), exactly where printed p.38 line 20 puts it,
and `mcp_ucbf2_0` now reads it. 005603 was only ever going to be
filled by `Y JCCER`'s `T,15,Y UCBF2,0.0($15)`, and JCCER never ran —
because the type field it compares was one character long. The empty
table was a *consequence* of the rejection, not a clue to it.

**The rejection was the model's.** See the section above this one.

## PRINTED p.54 — A THIRD `$`, AND A dds CHECKED FROM THREE PAGES AWAY, 2026-10-24

The DISK-TRACK CHECK ROUTINE and the TAPE IOD ROUTINE, forty-eight
rows. **Two more of printed p.53's stand-ins land**: `L CODE` at
003042.00 and `L IODTP` at 003077.00.

### A third `$` in front of an operation, and three is a pattern

Line 15 is `$SF(BU,4),.48(L XNT)` and it compiles as a plain `SF`.
printed p.43 line 6 was `$B,Q GO$A`; printed p.53 line 14 was
`$TI,1,-1.0(L IODX),1.0(L XPP)`. **Three instances in three source
decks, every one inert**, and all three on operations whose compiled
row is ordinary. C28-6129 printed p.37 accounts for a `$` on an
*operand* and says nothing about one on an *operation*.

> Still recorded rather than guessed at — but three is a pattern:
> **whatever the `$` marks, it is not in the object program.**

### printed p.51's `L BLANK` dds travels here, which is a third witness

Line 32 is a bare `KF,L BLANK` and prints **060600** — length 48,
byte size 6. p.51 line 34 declares `L BLANK (AY)DD(BU,48,6)`, and its
eight characters of blanks were settled by measuring the `Y`
terminator's column **in pixels**, with the declared dds as the only
other witness.

This row is a third, and a different kind: the dds is not merely
*declared* on p.51, it is **used** here, three pages on, by a row
whose own printed length depends on it. A wrong dds on p.51 makes
this row wrong too.

### An integer-classified symbol in a bit-address field

Line 41's `BZB1,L ZBIT(L XNT),L NORM` prints `000000.77 89` — 0o77 is
63, which printed p.50 line 40 puts in the **integer** column with
the location at zero. C22-6531 printed p.11: an integer "adds into
the low-order position of the field". The classification built for
p.48 and shown by p.50 is now exercised by p.54.

### And a prediction in an injection note was wrong

Changing `L BLANK`'s stand-in to `(BU,48,8)` was predicted to print
`061000` and prints **060000**: a byte size of eight does not fit a
three-bit field and goes in as **zero** (C28-6129 printed p.16, "byte
size is treated modulo 8"). The note now says what happened.

## PRINTED p.53 — TWO DERIVED STAND-INS CONFIRMED AND A FLAG LOWERED, 2026-10-23

Fifty-one rows: the end of the initialization routine and the **IOD
CARD ROUTINE**.

### Both of printed p.52's derived stand-ins land

`L OOPN` at 002775.40 and `L IODRN` at 003021.40 — and both were read
off p.52 from **one octal digit**. `BXVZZ,L OOPN+1.` prints
`002776.71` and `BAEZ,L IODRN` prints `003021.76`; bit 18 is set in
each, which puts the target on the `.40` half word. Transcribing them
as `.00` was p.52's first draft and three rows failed. This page says
the corrected reading was right.

### And a flag printed p.48 raised comes down the way it said it would

Line 28 is `CM0000(BU,9),L IOSCR,0.0  -SET IODSQ COUNTER TO 1.`
p.48 line 46 defines that symbol at 002601.40 as `DRZ(BU,9),(1)`, and
its deck recorded that the name came off a row where the drum had
lost several glyphs — `L ICSCR ... -ICDSQ COLNTER` — with **no
compiled bit depending on the spelling**, and said the next page to
reference it would decide.

At 900 dpi line 28 reads `L IOSCR` and the dds `(BU,9)` matches.

> **It came down by a reference, not by a better look at the
> definition.** That is the second time in two pages: `L CVBIT` →
> `L OVBIT` went the same way. A name field has no internal check; a
> use of it does.

### A second `$` in front of an operation, and it is still inert

Line 14 is `$TI,1,-1.0(L IODX),1.0(L XPP)  -STORE PP ID` and the row
compiles as a plain `TI` — `777777.00 83 / 000001.02 A4`. printed
p.43 line 6's `$B,Q GO$A` was the first. Two instances, two source
decks, both inert; C28-6129 printed p.37 accounts for a `$` on an
**operand** and says nothing about one on an **operation**. Still
recorded rather than guessed at, but the pattern is worth naming:
whatever the `$` marks, it is not in the object program.

### A dds travels through a SYN twice more

Lines 37-41 are four bare operations with no data description
written — `M+1,T IODCT(L XPP)`, `L,L IREF(L IODX),0.0`,
`K,T LREFN(L XPP)`, `ST,T LREFN(L XPP)` — and every one prints a
length of **014000, twelve**. And the listing distinguishes a *field*
symbol from an *address*, which is printed p.50's lesson in use: all
three are **bit offsets inside a table entry** (0.52, 0.52, 0.40),
with the index register supplying the entry.

## PRINTED p.52 — THE DECODE PROGRAM ITSELF, 2026-10-23

Forty-five rows of code. **Line 7 is `L DECOD` at 002737.00 — the
entry printed p.47's linkage format names — and it opens with an
eight-word `SWAPI`**, the largest in the corpus and the tenth caller.
p.47's worked call passes A (the break-down area) and B (the mode),
and lines 8 and 9 read exactly those two.

**The IOD/REEL dispatch is four characters wide**: lines 19-25 load
twenty-four bits of the card, compare against `L IOD` and `L REEL`,
branch to `L IODRN` or `L REELR`, and otherwise flag 9 and go to
`L ERROR`. Four BCD characters, so the comparison reads `IOD ` and
`REEL` and no more.

### A dds travels through a SYN across a page boundary

Lines 36 and 37 are bare connectives with no data description
written, and they differ only in a property carried from four pages
away:

```
line 36   CM0000,L INFAD    prints 001000.00 F0   -- length ONE
line 37   CM0000,L COUNT    prints 007000.00 F0   -- length SEVEN
```

`L INFAD` is p.48 line 52's `DD(BU,1),0` and `L COUNT` its line 49's
`DRZ(BU,7),(1)`. C22-6531 p.31 is the rule, printed p.45 is where
`strap_asm` learned it, and this is where it crosses a page.

### This page is §13d at its thickest — and two rows are not the artifact

The drum prints digit zero as C across whole rows here: line 24
prints its own location as `CCCC11.37` and line 35 its operand as
`C.O`, so the rows announce themselves. Five bytes were settled by
**decode plus a row already checked elsewhere in the corpus** —
`C2`→`02` (LCI's high nibble is zero; p.43 line 33's LVI prints
`000005.07 01`), `FC`→`F0`, and `CA`/`C0`/`C8`→`0A`/`00`/`08` (p.40
line 40's `Z,0.0($15)` prints `000000.22 0F`).

**But lines 21 and 23 print `003021.76 C6` and `003147.76 C6` and
both Cs are real** — p.43 line 43's `BAE,Q CK` prints `002447.76 C2`
and is checked. What mattered on those rows is the **octal pair,
which cannot hold a C**: `0o76` has bit 18 **set**, so `L IODRN` and
`L REELR` are at `.40`, not `.00`.

> Reading them as `.00` was this deck's first draft and three rows
> failed. **The same page taught both halves of §13 in one pass: a C
> that is a zero, and a C that is a C, told apart by which column it
> sits in.**

## PRINTED p.51 — AND A BLANK COUNT MEASURED IN PIXELS, 2026-10-23

TYPE SYMBOLS AND CODES, nine of them, plus the IOD AND REEL
COMPARISONS. **`L DISK` lands at 002723.00 and that is printed p.48's
last stand-in** — p.48 line 18 is `L XTYPE XW,L DISK,9,$`, a refilling
index word over **nine** entries, and this page has exactly nine type
symbols. The count and the table are three pages apart and they
agree.

### The trailing blank counts were measured, not eyeballed

Every type datum is `(AY)DD(BU,60,6),NAME<blanks>Y`, sixty bits, and
the addresses prove the sixty: each entry's four-bit code sits at
`.74` and the next entry at the next word. **How many blanks** is a
different question, and the usual answer — squint at it — is the one
`listing_typography.md` exists to replace.

So the statement column was rendered at 600 dpi and the **ink runs
read off numerically**. One character pitch is ~61 px in that crop,
and every `Y` terminator in the nine type rows sits at x = 1818-1868:
the same card column, so every datum is ten characters. The same
measurement settles the three rows no address can:

| row | Y at | characters |
|---|---|---|
| `L IOD` (line 30) | 1818 | ten — `IOD` + 7 blanks |
| `L REEL` (line 32) | 1819 | ten — `REEL` + 6 |
| `L BLANK` (line 34) | **1701** | **eight** — two pitches earlier |

`L BLANK`'s eight has a second witness: its own dds is `(BU,48,6)`
and 8 × 6 is 48, where `L IOD`'s and `L REEL`'s declared 64 is *not*
10 × 6. Neither witness is conclusive alone — a converted DD's size
is characters times byte size and the declared length "plays no part"
— but they agree.

> **A column position is a measurement when it is read in pixels and
> a guess when it is read by eye.** The method is the same one
> §13 uses for a glyph; it had not been pointed at a *count* before.

**`L IOD`'s and `L REEL`'s lengths are pinned by nothing else** —
lines 31 and 33 are CNOPs that round sixty bits to sixty-four, so
nine or ten characters leave the next row where it is. printed p.52's
first compiled word, 002737.00, bounds `L BLANK` only to 33-64 bits.
The code that compares against them will settle it and is not
transcribed yet.

### And printed p.52 opens with the entry p.47 named

`L DECOD  SWAPI,8,L TY,L IODX  -SAVE INDEXES` at **002737.00** — the
DECODE program's entry, opening with an **eight-word SWAP**, which is
a tenth caller and the largest yet.

**It also corrected a name on printed p.48.** p.52 line 11 is
`BB1,L OVBIT,L OVER` and its binary carries **002601.62** — p.48 line
50, which this project had transcribed as `L CVBIT`. A second print
of the same symbol three pages on, in a listing whose drum turns
digit zeros into Cs: that is `listing_typography.md` §13c's rule in
its cheapest form, because **a name field has no internal check and a
reference to it does**. The comment on the row said so too —
"-OVERLAPPED JOB", and OVBIT is the OVerlap BIT. No compiled bit
moved; what would have broken is the **image**, silently, the first
time p.52 joined it and `L OVBIT` resolved to nothing.

*`L IOSCR` on p.48 line 46 is still flagged for the same reason and
is still unreferenced. The next page that names it decides it.*

### And the IOD/REEL dispatch is four characters wide

p.52 lines 19-25 are the card-type test: `L(BU,24),1.0(L IODX)` then
`K(BU,24),L IOD,0.0` / `BAEZ,L IODRN`, then the same against
`L REEL`, then `LCI,$15,9.0  -NEITHER -- ERROR FLAG` and
`B,L ERROR`. **Twenty-four bits is four BCD characters**, so the
comparison reads `IOD ` and `REEL` and no more — which does not pin
p.51's data lengths but does say what a card's type field has to
contain and where: word 1 of the area `L IODX` points at.

## PRINTED p.50 — AND THE LISTING HAD BEEN PRINTING THE ANSWER ALL ALONG, 2026-10-23

Thirty-one printed rows: a count table of the bytes 1 through 31, and
the INTERNAL DECODE TABLES. **Three of printed p.48's stand-ins land**
— `L SYMU` 002620.00, `L SYMC` 002660.00, `L NTPU` 002700.00 — and
each one's SIZE is what puts the next where p.48 said it would be, so
this page checks p.48's arithmetic as much as its own. The merge now
reports **222 stand-ins checked and 35 external**, from 219 and 38.

### The listing prints a symbol's classification

Lines 37 and 40 are both one-bit SYNs and their values go in
**different columns**:

```
line 37  000000.61+                L RLBIT  SYN(BU,1),0.49
line 40  000000.00+  +00000077     L ZBIT   SYN(BU,1),63
```

A **bit address** goes in the LOCATION column (0o61 is 49); an
**integer** goes in the INTEGER column (0o77 is 63) with the location
left at zero. That is C22-6531 printed p.31's *"its bit address or
INTEGER CLASSIFICATION"* **shown rather than stated** — the same
distinction printed p.48 had just cost an assembler fix to learn,
when a count SYNned to 80 was scaled as a bit address and came out as
one.

> **The listing had been printing the answer all along, in a column
> this project had no reason to read until a bug made one.** Worth
> remembering next time a property seems undecidable from the page:
> the symbol-table columns carry more than the value.

### And the injection that matters is in the merge, not the verifier

Line 36's `(32) -> (31)` gives two failures in p.50's own verifier
and the useful one somewhere else entirely: `mcp_image` dies with
*"LNTPU: printed p.48 SYNs bit 94208, printed p.50 places it at bit
94144"*. One page's reservation size against another page's stand-in
— a claim no single verifier can see, and the reason the merge is a
program rather than a shell pipeline.

## PRINTED p.49, EIGHT LINES, AND THREE SPELLINGS OF ONE THING, 2026-10-23

The shortest page this project has transcribed, and it finishes the
storage block printed p.48 opened: four index words, a self-refilling
clear word, a four-word count table and one more index word,
002602-002613.

**It starts at 002602.00 and that is a rounding, not a new origin.**
printed p.48's last datum is line 52's **one-bit**
`L INFAD DD(BU,1),0` at 002601.73, ending at 002601.74, and an `XW`
rounds to the next full word. **There is no `SLC` on this page at
all** — the location counter carries over, which is what a single
STRAP assembly looks like when the listing's page break falls
mid-deck.

**Three spellings of a null value field on one page.** Lines 1 and 4
are a bare `XW`, lines 2 and 3 `XW,0`, line 8 `XW,` — and all five
compile the same all-zero index word (C22-6531 printed p.7: "A null
field is always compiled as a zero"). *That the listing uses all
three within eight lines is the best evidence this project has that
they are interchangeable*, and all five rows are checked.

**And the page states one number twice**, which makes its two
injections each other's mirror: line 5's self-refilling
`XW,L RLCT,4,$` carries count four and line 6's `DRZ(BU,64),(4)`
reserves four words.

* count `4 -> 5` — 1 FAIL, line 5's row, no symbol moves.
* `(4) -> (5)` — 1 FAIL, `LAST PP`'s **symbol** check, and **not**
  line 8's row: the fifth reserved word is zero and an all-zero index
  word is exactly what that row expects.

**Predicted 2 and observed 1**, and the gap is worth the sentence: *a
row check pinned to an ADDRESS cannot see a symbol move into or out
of it when the storage either side is identical.* The symbol check is
what catches it, which is why every page here carries both.

## PRINTED pp.47-48, AND A GUESS THAT HAD BEEN WRONG SINCE THE FIRST XW, 2026-10-23

**printed p.47 compiles nothing.** Twenty-three lines; the only
non-comment is line 1's `SLC,$` at 002556.67, where printed p.46's
`Q BLNK` ends to the bit. The rest is **THE DECODE PROGRAM LINKAGE
FORMAT** written out as a worked call — `boot_plan.md` A17 has it —
so `L DECOD` is handed the area `S BRK8` filled, a mode, and a
disposition list. `mcp_image.py` names p.47 in `NO_DECK_PAGES`
because a gap in that range would otherwise look like a page someone
forgot.

**printed p.48 is that program's storage**: ten self-refilling index
words, a swap area of eight more, eight index-register SYNs and a
block of counters, 002557-002601. The boot's trail stays at 239 and
every check passes.

**But the step count moves, and it is not a simple function of the
image size.** p.48 adds nineteen words and costs **+1,033** clocks;
printed p.49 adds ten more and costs **−692**. "That is the extra
tape words being read" fits the first and not the second, so the step
count is **not a tape-length meter** and this file should stop
treating a move in it as self-explaining. It moved for p.44's tables
(+240, and that one WAS traced), for the SWAP (+82, counted in
`rl_xmit` itself), and now twice more without an account. *What the
step count is a meter for is open; the trail and the checks are what
the boot is judged on.*

### A second, independent witness for VF = 25 bits

Line 44 is `L NO6  VF,.06` at 002601.00 and line 45 is at
**002601.31** — bit 25 — and eight more rows chain off it without a
byte boundary: `.31 .40 .51 .52 .53 .62 .63 .73`. Every one is
printed and every one is checked. printed p.46 forced that correction
and this page, which had no part in it, confirms it.

### AND IT FOUND A GUESS THAT HAD BEEN WRONG SINCE THE FIRST XW

An eighteen-bit field reads an **integer** as a count of words and a
**bit address** as a bit count to divide by 64 (C22-6531 printed
p.12). `strap_asm` decided which by looking at the **text**: anything
with a letter in it was an address. Lines 9-14 write their counts as
SYMBOLS — `XW,T IOREQ,T IOC,$` prints count 000120, eighty, and
`T IOC` is `SYN,80` — so **eighty came out as one**. Six rows wrong.

What made it visible is that the same page writes `32-2` as a literal
two rows later and gets it right.

**The rule is the same sentence the last two pages needed.** C22-6531
printed p.31: *"data properties (dds) associated with Y and its bit
address or INTEGER CLASSIFICATION are transferred to A."* `SymTab`
now carries `sym_int` beside `sys_alias` and `sym_dds` — **three
things one sentence transfers, found one page at a time**, and each
time the assembler had been guessing at what the sentence states.

### It moved two entries in the file that exists to record exactly this

`verify_c22_6578_a4_addresses.py` keeps a `KNOWN_GAP` list and fails
if a gap starts passing. Both halves happened at once:

* **`M.M` left the list.** With `M` no longer scaled it comes to 10
  half-words and so does `5.5`.
* **`.M` joined it, and that is the more useful half.** It used to
  pass **by accident**: `.M` tokenizes as `0 + M`, and `M` scaled as
  a bit count came to 0 — which is also what `0.5` comes to in a
  half-word field, because bit 5 is inside half-word 0. *Two
  different wrongs cancelling.*

Point notation on a symbolized integer is **still not implemented**.
What changed is which pairs happen to agree, and the list now says
so.

### A check was removed for drifting

`mcp_qsav_last_after_swap` lasted one commit. Its count field was
1106; adding p.48 made it 1125 — **exactly nineteen more, the number
of words p.48 adds to the image**. So `$6`'s count tracks the image
SIZE, and the check would have to be re-measured on every page and
would say nothing new each time. `Q SAV+0`'s count does not move and
one word is enough to say the swap ran.

*This project has been bitten by a drifting check before — two
comm-region checks that walked onto MCP's own working storage as the
image grew. A ratchet nobody can predict is a ratchet nobody reads.*

### And the card types are documented after all

`C22-6728` printed p.88: *"Three types of control cards are used:
1. I-O Configuration Definitions (IOCD) 2. MCP IOD's (IOD) 3. MCP
Parameters (MCPP)."* **MCPP's fields are given** — cols. 10-13
`MCPP`, cols. 14-17 a mode of `OFFLINE`/`ONLINE`/`BYPASS` — and the
IOD card's are not, because an IOD *"perform[s] the same function for
MCP as [it does] for the problem program"*. printed p.25 line 51's
comment names the same three: *"TEST 12 ZONE OF THIRD LETTER IN IOD,
REEL OR MCPP TYPE FIELD"*, and the 12-zone test is what ends the
loop: `D` and `E` carry it, `P` does not.

**So the fixture needs at least one IOD or REEL card, then an MCPP.**
The first call to UNCODE is unconditional, so the first card after
the IOCDs cannot be the MCPP. And `Y REELC` executes two `SWAPI`s,
which is why SWAP came first.

## FORWARD SWAP IS BUILT, AND IT WAS A DEPENDENCY RATHER THAN A WISH, 2026-10-23

`SWAP` had been a documented absence for weeks, then a documented
absence with a caller, then "a survival with an expiry date". The
expiry date arrived, and not because the count of callers grew:
**printed p.40's `Y REELC` — the REEL-card handler — executes two
`SWAPI`s**, so the moment the fixture punches the IOD and REEL cards
printed p.25 expects, the refusal stops being a note and becomes a
halt.

**THE ORDERING THAT FOLLOWS FROM THAT, worth writing down before it is
rediscovered:** an **IOD** card can be the fixture's first card
without `SWAP`; a **REEL** card cannot. `Y IODC` (printed p.40 lines
14-22) does not swap.

### What was built, and the one asymmetry worth naming

Reference Manual printed p.30: "...**at the same time**, the full
words of the area which starts at the right effective address are
transmitted to the area which starts at the left effective address."

An exchange needs **two reads and two writes per word** and this model
has one of each per rule, so a swapped word takes **three clocks** in
`rl_xmit`: read the sender, read the receiver and write the sender's
value into it, then write the receiver's old value back. **Both reads
happen before either write**, which is the whole of "at the same
time".

*The asymmetry with Transmit:* Transmit's first word is moved in the
execute arm and the rest by `rl_xmit`; **a swap moves no word in the
execute arm at all**, because the arm has one write. Keeping the swap
branch out of the prefetch path entirely is what stops that from
becoming a half-folded arm.

### Two injections, and the second is the argument for the overlap block

* **Write before read** — phase 0 made to write the receiving word as
  soon as the sender is in hand. Fails blocks 1, 2, 3 *and* 4: every
  sending word comes back unchanged, which is IBM's own failure
  message, "SWAP FAILS TO ALTER ORIGINAL WD / AND THEREFORE ACTS LIKE
  TRANSMIT".
* **Reverse word order** — the execute arm made to start at the last
  word of each area and step down. **Passes every disjoint block and
  fails only block 4**, which comes back `3 1 2` where the manual
  gives `2 3 1`.

The second is the one that justifies block 4's existence: blocks 1 and
3 are one word and block 2 is three *disjoint* words, and **nothing
but an overlap can see the order**. Both failing values were
hand-computed before the injections were run.

### And block 1 is IBM's own test, finally executed

`jb_ax4b` routine 1246 TEST 2C has been transcribed since the I-Box 4
work and checked **only for its encoding** — `run_tests.sh` said so in
as many words: "its ENCODING is pinned by
`decks/ax4b_1246_transmit_swap.strap`; its EXECUTION is not tested by
anything and this says so." Block 1 is that test with the branch logic
replaced by a storage check, because this harness can read storage and
the diagnostic could not.

*A transcription that has only ever been encoding-checked is a test
waiting to be run.* There are more of them.

### AND THE FIRST THING IT MEASURED WAS A RETRACTION

The boot run was expected to be unchanged — `op_trail` had said the
one `OP` raise in the whole run was at 001214.00, in printed p.24's
time conversion, and a control run reproduced it. **The step count
moved by 82**, so something did change, and rather than theorise
`StretchCore` was made to announce every swap that starts. The boot
prints exactly one line:

```
StretchCore: SWAP started at half-word 2649, 6 words
```

2649 is word 0o2454 half 1 — **002454.40, printed p.43 line 53's
`Q FIN  SWAPI,6,Q SAV,$1  -RESTORE INDEXES`** — and six words is that
row's count. **MCP executes one SWAP and this project said three
times that it executed none.**

**What misled it was an indicator trail that can only see a
TRANSITION.** `op_trail` counts RISING edges of `OP`; the refusal at
002454.40 was raised while `OP` was already high from 001214.00, so
there was no edge to count. The anomaly was even recorded at the time
— "one edge each does not by itself account for two different
endings" — and filed as an open question instead of being treated as
the answer.

> **A trail that can only see a transition cannot answer "did this
> ever happen".** The fix was not a better trail: it was making the
> thing announce itself at the point it occurs, which cannot be
> missed and costs one `$display` on an event that is rare by
> construction.

**AND THE WHOLE OF THE 82 IS THE ARM, counted rather than
estimated.** `rl_xmit` now reports what it spent — `SWAP finished, 82
clocks in rl_xmit` — and the boot's step count moved by **exactly
82**. So MCP's execution after `Q FIN` takes the same number of
clocks whether `$1`-`$6` were restored or not; nothing downstream
changed. (Six words at ~13.7 clocks each: each of the two reads per
word waits on `responseReady`, which is memory latency, not the
exchange.)

**And the one swap is now observable in storage, not just in a
`$display`.** Two boot checks read `Q SAV`, which the SWAP exchanges
with `$1`-`$6`: `Q SAV+0` is `0x00000000001C0000` (count 7) and
`Q SAV+5` is `0x0001200011480000` (value 000004.40, count 2122 =
0o4112, a character counter — which is what `$6` is doing in printed
p.43 line 46's `LVE,$6,Q FLD($3)`). **These are the loop's registers,
not the `TI`'s**, and a future regression that silently refused SWAP
again would leave the `TI`'s values standing and fail them.

**The arm does not trip the core's own anomaly warning**, which was
worth checking rather than assuming: the `swap_scope` run prints
**zero** "E-box instruction at N executed at preparation
(classification mismatch)" lines, and the MCP boot prints **73 both
before and after the build — the identical set, none of them at the
swap's address**. Those 73 are a pre-existing observation about other
instructions and are an open item, not a consequence of this work.

The three retracted claims are struck where they stand, in
`decks/mcp_bootstrap_p43.strap`, `decks/mcp_bootstrap_p46.strap` and
`run_tests.sh`'s p.45 section, rather than quietly edited.

### Backward swap is still refused, and the reason is narrower now

`SWAPB` and `SWAPBI` are **card-only** — named on pocket card
X22-6533 and written by no deck in this corpus. Building them would be
manual-derived with no oracle; `rl_xmit`'s sign handling would carry
them unchanged the day one turns up. `bsv/README.md`'s scope list says
this, and carries the caution its own former entry earned: **a scope
list is a measurement with a date on it.**

## THE TABLES ARRIVE, AND FOUR ASSEMBLER CORRECTIONS COME WITH THEM, 2026-10-23

printed p.46 defines **every one of printed p.45's fourteen
stand-ins** and not one of them moves. Three are index registers
(`QX INN SYN,$1` and its two fellows, lines 22-24), one is the integer
6, ten are addresses. The two `dds` p.45 had to write by hand are
printed here as `(A*)DD(BU,Q KSIZ,Q KSIZ)` — `(BU,6,6)`, which is
exactly what p.45's bare `KF,Q CMA` prints as `006600`.

**And `SWAP` now has nine documented callers**: two on printed p.40,
one on p.43, three on p.45, three here. ~~The run still executes none
of them.~~ **RETRACTED the same day** — it executes exactly one, printed
p.43 line 53's, and the retraction is at the top of this file.

### The run halves and the answer does not change

p.46 is not just more code — it is the DATA the breakdown routine runs
on, and until now that data was **zero**. `boot_plan.md` A15 has the
list; the short version is that `S BRK8` had been comparing every
input character against a `Q CMA` of 0, which is the BCD **blank**.

**12,847,130 steps to 6,036,053**, and the error is the same one at
the same address. That was the prediction worth getting wrong: the
missing tables were a plausible cause of printed p.25 line 44's "NOT
IOD OR REEL CARD" and they are **not** the cause.

**So the next place to look is the card, or where the routine is
pointed at it.** `strap/iocd.py` punches an **IOCD** card; printed
p.25 line 41's parameter word says "EXPECT IOD AND REEL CARDS"; lines
32-36 compute the area from `$4` and pass `$7`. In that order.

### WHICH EXIT UNCODE TOOK, measured — and a check that was removed for being green for nothing

printed p.25 line 39's `X 222A  XW,0` is the slot UNCODE writes its
answer into, "FOR TOE, FIELD COUNT, IO REF NUMBER", and line 35's
`LVI,$14,X 222A` is what points the routine at it. A boot check was
added on that word and the run was read: **it is zero.**

printed p.40 line 40 is `Y UER`'s `Z, 0.0($15)` — UNCODE's error exit
**zeroes that slot** and then returns to `2.32($14)`, which with
`$14` = X 222A is 001437.40, printed p.25 line 44's `B,X 223  -NOT
IOD OR REEL CARD`. The success exit, `Y JCCER` on p.40 lines 35-36,
writes the slot instead. So the rejection is **UNCODE's own `Y UER`**,
not something downstream of it, and the question narrows to which of
the five branches reaches `Y UER` — printed p.38 lines 8, 36, 38 and
41, and p.40 line 32's `BZXE,Y UER`.

**THE CHECK WAS THEN REMOVED, deliberately.** The slot is assembled
zero and `Y UER` zeroes it, so a green there is consistent with "the
error exit ran" AND with "nothing ran at all" — an all-zero fixture
cannot test an all-zero result, which is the same lesson the console
switch register cost earlier in the same week. It cannot be fixed by
preloading either: the bootstrap MOVES the whole image into place, so
a marker written before the run is overwritten, and a marker in the
tape image would mean the tape no longer matches the deck. The
measurement is recorded here instead of being enshrined as a test
that proves nothing.

*What WOULD be discriminating is `Y UX SAV` on printed p.40, which
both exits write with `TI,3,Y UX SAV,$11` before they part. Zero there
means UNCODE never ran; a value means it did. That is the check to
add when the next question needs it.*

### AND THE BRANCH IS LINE 41, WHICH MEANS MCP IS RIGHT AND THE FIXTURE IS WRONG

Five branches reach `Y UER`. Four can be ruled out and the fifth is
the one printed p.25 line 44 names.

* **printed p.38 line 8**, `BZAEZ,Y UER  -IF NOT A B GIVE ERROR
  RETURN`, is UNCODE's FIRST test: lines 6-7 load twelve bits of the
  card and compare them against `(2)100010000000`. **It passed**, and
  that is measured rather than argued: line 12 is `BD,S CA6`, the
  boot run's PC trail reached `S CA6`, and the step count responds to
  printed p.44's tables. A card that failed line 8 would never have
  got there.
* **lines 36 and 38** are inside `Y MKEAR`'s disposition tests, and
  **line 41 is its fall-through**: line 39 is
  `K(BU,48),Y RELMK  -TEST FOR REEL CARD`, line 40 branches to
  `Y REELC` if it matches, and line 41 is `B,Y UER` when it does not.
  "Not an IOD, not a LIM, not a REEL" is exactly the sentence printed
  p.25 line 44 writes as `-NOT IOD OR REEL CARD`.

**And the card the fixture punches is an IOCD card.**
`strap/iocd.py`'s `CLASS_COLUMN = "B"` is why line 8 passes — every
MCP control card carries a class character and this one is a B — and
`CARD_TYPE` is `IOCD`, which is none of IOD, LIM or REEL.

> **So MCP is behaving correctly and so is the model.** printed p.25
> line 41's parameter word says "EXPECT IOD AND REEL CARDS", the boot
> hands it a class-B card whose type is IOCD, and MCP says so. The
> bug is in the FIXTURE, not in either program.

**What that makes the next task** is `boot_plan.md` A3's remaining
piece, stated more precisely than before: the PROSA record needs the
cards this call expects — IOD and REEL — not only the IOCD cards
printed p.17 wanted. One gap is still open in the chain and should be
closed rather than assumed: that printed p.25 line 32's `$4` really
does point at the area the fixture punches into.

### FOUR ASSEMBLER CORRECTIONS, and one of them had a note predicting it

* **`VF` is twenty-five bits.** C22-6531 printed p.18 says "THE
  LOCATION COUNTER STANDS AT BIT 25 at the end of the operation", and
  `strap_asm.py` carried that quote while returning a whole half word
  anyway, because *"Nothing in the corpus distinguishes the two any
  other way."* **Lines 29 and 30 do**: `Q SKIP VF,.16` is at
  002556.00 and the very next row is at **002556.31** — bit 25. The
  ALIGNMENT stays `HALF`, which is the whole trick: p.18 rounds the
  counter up *before* compiling the value, so a run of VFs still
  measures in half words and only a following pseudo-operation that
  does not round sees bit 25. `(HALF, HALF)` breaks this page;
  `(0, 25)` broke seventeen verifiers; `(HALF, 25)` is both at once.
* **A null operation aligns to a half word.** It returned alignment 0,
  invisible until the above: printed p.25 lines 41-42 are a `VF,4.0`
  and a `,0.0($7)` on consecutive rows, and the half word would have
  started at bit 25 and overlapped the VF. The assembler caught it as
  "two statements deposited overlapping bits" rather than quietly
  producing a wrong word.
* **A constant `SYN` is resolved before the location walk.** Lines 30
  and 32 write `(BU,Q KSIZ,Q KSIZ)` and line 33, three rows below,
  defines it. C22-6531 printed p.31 allows the forward reference
  outright: a SYN's operand need only be "fully defined (although this
  may possibly mean as late as pass 3 of Strap-1)".
* **A data symbol carries its `dds`** — the other end of the same p.31
  sentence printed p.45 needed.

### And the first of those found a missing line in another deck

printed p.8 line 31 is `X E DD K  SYN,$-X ERR DD` and prints
000047.00, a whole word, which a 25-bit VF would make 000046.71.
**Line 30 of that page is a `CNOP`** and `mcp_bootstrap_p7_p8.strap`
had omitted it — invisible while VF claimed a half word, and the first
thing to fail when it stopped.

*That is the second time this month a correction to the assembler has
paid for itself by finding a transcription error nothing else could
see.* It is an argument for making the assembler right rather than
making it permissive: a permissive assembler cannot find anything.

### Two things the injections said, and one of them was a survival

**The step count's cause is measured, not inferred.** Four of the
corrections above change how the assembler lays storage out, so "the
run halved because p.46's tables arrived" needed checking rather than
asserting. pp.15-45 were built under the **old** assembler and the
**new** one and diffed word by word: **867 words, zero differences.**
The step change is p.46's by construction.

**`Q BLNK`'s length survived every check on its own page**, which is
the printed p.44 line 25 shape one page later. It is the last datum
here, `Q CMA` is held from above by `QCOUNT`'s 002556.37 but `Q BLNK`
has no successor, and the content cannot discriminate either — a
blank is `0o00` and so is a second blank. Giving it two passed every
row, every symbol and the image build. **What pins it is the next
page:** printed p.47 line 1 is `SLC,$` at **002556.67**, bit 55, and
`Q BLNK`'s 002556.61 is bit 49 — 49 + 6 = 55 to the bit. The same
shape as printed p.42's last datum ending exactly on `S CA6`.

*Three pages running, the thing that pins a page's last datum has
been the next page's opening address.* That is worth doing on purpose
from now on rather than discovering each time.

### The merge learned that two identical SYNs are not a duplicate

`_STANDIN` only recognises the `(8)NNN.NN` form, because that is what
a page writes when it reads an address off its own binary. p.45 has to
write `QX INN SYN,$1` and `Q KSIZ SYN,6` because that is what those
symbols *are*, and p.46 defines them with the identical text. When the
two values **agree** the stand-in has been checked, which is all the
cross-check exists to do; a disagreement, and any collision involving
a location-counter symbol, is still a hard failure. The merge now
reports "4 SYNs that agree with another page's SYN".

## MCP RUNS THE WHOLE UNCODE PATH AND REJECTS THE CARD, 2026-10-23

printed p.45 is THE BREAKDOWN ROUTINE, its line 10 is `S BRK8` at
002502.00 — the address the PC trail had been stopping at, on a zero
word — and the page is **signed**: lines 6-7 read "-SBRK8, 6 BIT BCD
VERSION, 16 BITS BETWEEN FIELDS.   **LARRY LEVY**", the first author's
name transcribed out of this listing.

With it in the image the run goes **more than twice as far**:
6,028,291 steps to 12,847,130, ending at half-word 239 = **000167.40**
= printed p.6 line 1's `BD,$  -LOOP`. `boot_plan.md` A14 has the
chain; in one line, MCP ran UNCODE, decided the card was **NOT an IOD
or REEL card**, and said so through its own error routine.

### THE NEXT THING TO DO, and it is now a question with a shape

**Why is the card rejected?** The fixture punches an **IOCD** card
and printed p.25 line 41's parameter word says "EXPECT IOD AND REEL
CARDS". Before chasing the conversion, establish whether this path
should be reached with this fixture at all. Three places to look, in
order:

1. **printed p.25 lines 32-36**, the call. `X 22` computes the base
   of the area "CONTAINING IOD AND REEL CARDS" from `$4`. If `$4` is
   wrong the routine is looking at the wrong storage.
2. **The card itself.** `strap/iocd.py` punches it; printed p.46's
   `Q CMA` and `Q BLNK` are what `S BRK8` splits on, so a card with
   no commas breaks into one field.
3. **printed p.46**, which is not transcribed. It holds the rest of
   `S BRK8` and the table `Q CMA`/`Q BLNK`/`Q COUNT`/`Q SKIP` live
   in, and it is the next page either way.

### TWO THINGS A `SYN` HAS TO CARRY, and this page needed both

C22-6531 printed p.31: "**THE MEANING OF SYN IS ALWAYS ONE OF EXACT
SUBSTITUTION** ... data properties (dds) associated with Y and its bit
address or integer classification are transferred to A."

* **A register SYN stays a register.** printed p.46 lines 22-24 are
  `QX INN SYN,$1`, `QX OUT SYN,$2`, `QX CF9 SYN,$3`, and p.45 uses
  them as a J field (line 10) *and* as an index (line 19). `$1` was
  already context-dependent in `strap_asm` — register 1 in an I or J
  field, bit address 000021.00 in an address field — and storing a
  SYN's **value** loses that: 000021.00 in four bits is 0. `SymTab`
  now keeps the substitution. **Line 19 prints 81 and the old
  assembler gave 80.**
* **A dds travels too.** Lines 20 and 22 are `KF,Q CMA` and
  `KF,Q BLNK` with no data description written, and both print
  006600 — length 6, byte size 6. `strap_asm` had been **accepting a
  dds on a SYN and silently dropping it**, which is the
  wrong-output-no-error shape this project keeps finding. It now
  keeps it, and `inherited_dds()` is where.

*The second one is worth the note it got in `strap_asm.py`: the fix
was not "implement a missing feature", it was "stop accepting input
you then ignore."*

### The SWAP refusal survives, and this time it is measured

p.45 lines 47-49 are three `SWAPI`s under `Q 2BIG`, the
oversized-field path. `tests/gen_tb.py` gained an opt-in **`op_trail`**
that latches the PC the first time the OP indicator rises. It says OP
is raised **once**, at half-word 1304 = **001214.00**, after six
million steps — and a **control run with p.45 taken back out of the
image** raises it at the same address. So no `SWAP` executed, and that
is a result rather than a reading. Six documented callers now: two on
printed p.40, one on p.43, three here.

### TWO THINGS THE SAME TRAIL OPENED

1. **What is refused at 001214.00?** It is in printed p.24's TIME
   CONVERSION and it has been in every run since p.24 joined the
   image, invisible, because MCP's interruption system clears the bit.
   The candidates are on four consecutive rows — line 21's
   `/I(BU,6),60,-60`, line 22's `C0011(BU,6),$RM+.54`, line 25's
   `CV(BU),$L,16`, line 26's `LTRCV(BU,6),$RM+.54` — and `bsv/README`
   lists `CV`/`DCV`/`LCV`/`LTRCV` and `KE`/`KF`/`KFE`/`KFR` as
   decoded-but-not-executed. **The PC the trail reports is a LOCATOR
   AND NOT A PROOF**: this model has a look-ahead, so `getPC()` can be
   running ahead of the operation that set the bit. A one-instruction
   deck per candidate, run on the model with a `BB,$OP` after it,
   looked like it would settle this in minutes.

   **IT WAS TRIED ON 2026-10-23 AND IT DID NOT**, which is worth the
   paragraph so the next attempt starts further on. A scratch deck
   ran `/I(BU,6),60,-60`, `C0011(BU,6)`, `CV(BU),$L,16`,
   `LTRCV(BU,6)` and `KF(BU,6,6)` in sequence on the model and
   finished with **word 11 = `0x44` — `AE|RZ`, OP CLEAR**. So on a
   bare program none of the five refuses, which is at odds with
   `bsv/README`'s "decoded but not executed" list naming `CV`,
   `LTRCV` and `KF`.

   **Do not act on that yet.** A second version of the same deck,
   snapshotting word 11 with `L(BU,64),(8)11.0` / `ST` between the
   candidates, returned nonsense — the FIRST snapshot, taken before
   any candidate ran, came back `0x0104500000000000` and every later
   one came back zero — so **reading word 11 from inside a program is
   not trustworthy here**, and the single end-of-run read that gave
   `0x44` inherits that doubt. The model also prints "E-box
   instruction at N executed at preparation (classification
   mismatch)" for several of these rows, which is its own signal that
   they take an odd path. The deck was deleted rather than kept as a
   test it cannot support.

   **What to build instead is an exact locator, not another probe.**
   `StretchCore` already has the E-box's instruction address in hand
   where it prints that warning; latching it in a register and
   exposing it read-only would let `op_trail` report the address of
   the operation that set OP instead of the instruction unit's
   counter — one run instead of a probe per candidate.
2. **The edge count does not account for both endings.** The p.45 run
   reports one edge and ends with OP **set**; the control reports one
   edge at the same address and ends with OP **clear**. One edge each
   cannot be both. Either a clear and a re-set fall between two
   samples, or `mem.readIndicators()` and the word 11 the checks read
   are not the same thing. Recorded in `gen_tb.py` rather than
   guessed at; the **address** is what the trail is trusted for, and
   the control reproduces it exactly.

### Three boot checks moved, and each now names something

`mcp_x_err_ad` said "no error site ever ran" and now holds
**001441.40**, printed p.25 line 48's `X 224`; `mcp_indicators_word11`
moved to `OP|XVGZ|XE|RGZ|AH`; `pc_check` moved from 0 to **239**,
MCP's deliberate error stop rather than a branch into zeros. Ratchets
with reasons: any *other* error site, and any return to zero, fails
them.

## PRINTED p.44, AND THE STEP COUNT IS THE MEASUREMENT, 2026-10-23

printed p.44 is THE CHARACTER LOCATOR TABLES and THE TABLES, and it
defines **all four** of the stand-ins printed p.43 had to `SYN`:
`Q FLD` 002456.00, `Q` 002465.00, `Q SAV` 002472.00, `Q TB`
002500.00. Not one moves. Its last datum ends at **002501.71**, which
`boot_plan.md` A9 had recorded as printed p.45's opening address
before this page was rendered.

### The prediction was written down before the log was read

p.44 is **data**: no entry point, no executable row, and p.43's loop
branches on `$LZC` and the `KFI` punch tests, none of which touch
`Q`. So the PC trail should **not** move, and it does not — still
2692, `S BRK8`, whose body is on printed p.45. `mcp_indicators_word11`
should *possibly* move, because `Q FLD` and `Q` used to be past the
end of the image and the `LVE` chain was reading zeros; it does not,
because `RZ` was already set.

**What moves is the step count: 6,028,051 → 6,028,291.** Two hundred
and forty more steps to reach the same address. That delta is the
only thing in the run that says the tables are *live* — and it is a
measurement, not a reading, because nothing else was added to the
image.

### The second `CNOP` absorbed an injection, and that is why there is an extra check

Three injections were run against the new verifier and the third
survived everything the listing can pin:

* line 15 `,.66($2)` → `,.72($2)` — 1 FAIL, 002463.40.
* line 21's data one character short — 1 FAIL, 002470.44, the colon's
  address, which is what pins the three rows above it.
* **line 25's data one character short — ALL twenty-two rows and all
  four symbols passed.** Line 27's `CNOP` rounds the location counter
  to the next word and absorbs it.

So lines 21-23 are pinned by the colon row and **line 25 was pinned
by nothing on the page**. What pins it is the two printed tables read
together: `Q FLD`'s thirteen entries 0 through 72, and `Q TB`'s
0/78/156/234, which is thirteen six-bit characters apiece. The test
now checks the thirteenth character of every zone, and the same
injection gives one FAIL at `Q+234+72`.

*The lesson is an old one in a new shape: a rounding pseudo-operation
between a datum and the next checked address is a place where errors
go to hide.* `CNOP` was already known to be alignment-dependent
(jb_ax5b p.80 against p.82); what was new is that the same property
makes it an **error sink** for anything compiled just before it.

### `UNTAIL`, and MCP's tailing is two levels deep

Line 35 is `UNTAIL,(1)`. C28-6129 printed p.37 gives the level
syntax, `TAIL, (n)DOG`, with `(1)` the default, and printed p.38:

> "An untail statement will untail all levels up to and including the
> level specified in the address field."

So printed p.2 line 10's `TAIL,(2)G` covers the whole program at
**level 2**, p.43 line 9's `TAIL,A` opens **level 1** over these two
pages, and p.44 line 35 closes level 1 and leaves G standing. Nothing
before had shown the second level in use. `UNTAIL` joins `TAIL` in
`LISTING_CONTROL` for the same reason — tails mangle definitions and
references alike.

**And the condition that would make discarding them wrong is now
CHECKED, in both directions, rather than asserted.** Outward: no
other MCP deck names any of the thirteen symbols the level-1 block
defines. Inward: printed p.43's four `SYN` stand-ins are exactly the
four symbols p.44 defines, and neither of the two names p.43 defines
before its `TAIL` (`S CA6`, `S CA8`) is referenced after it. A fourth
injection — a fifth, unreferenced `SYN` on p.43, which moves no
compiled row — gives 1 FAIL in the inward check and nothing else.

### One standard stated rather than left as a hole

The listing prints **no binary** for lines 21, 22, 23 and 25, so no
character code on the page is transcription-checked and none can be.
The codes are **manual-derived**: `strap/charsets.py`'s `A` table is
the 48 Character Set from RefMan printed p.166. The grid they come
out as is its own evidence — `0o6x` for the 12 zone, `0o4x` for the
11, `0o2x` for the zero zone, `0o0x` for none — and the same
structure settles the one typography question the page raises without
a re-render: the tenth character of each row is that row's lone-zone
punch (`+`, `-`, blank), so the zero zone's is the **digit** zero,
and `JKLMNOPQR` has a **letter** O.

## MCP RUNS S CA6, AND CALLS S BRK8, 2026-10-23

printed p.43 line 5 is

```
002422.00   000011.22 00    S CA6   Z,$R   -SET UP FOR A-6 CONVERSION
```

**That is the address printed p.38 predicted five pages earlier, the
address printed p.42's last datum ends on to the bit, and the
address the boot run's PC trail has been stopping at since p.38
joined the image.**

With p.43 in the image MCP executes it, and the trail moves:

```
PC TRAIL: last non-zero half-word address 2692, after 6028051 steps
```

2692 half-words is **002502.00** — `S BRK8`, printed p.38 line 17's
"BREAK CARD INTO FIELDS", predicted at that address by the same page
that predicted `S CA6`. It is printed p.45 line 10.

So MCP has now converted a system card from Hollerith to BCD and
called the routine that breaks it into fields.

### `TAIL` appears, and §5x predicted it would be inert

Line 9 is `TAIL,A`. The project's memory has said since 2026-10-17
that *"Nothing in MCP needs `TAIL`"* — derived when only pp.3-15
were transcribed, and now false.

**But §5x's analysis holds, and that is the point.** C28-6129
printed p.37 makes `TAIL` name mangling for cross-program link
safety, not lexical scoping: definitions and references are mangled
alike, so a single-program assembly is bit-identical with or without
it. §5x wrote that down **before any page using `TAIL` had been
opened**. This page is the first test of it and all forty-three rows
match.

**The deck writes `TAIL, A` as printed and the *assembler* discards
it** — which is the other way round from how this first landed.
`strap_asm.py`'s `LISTING_CONTROL` carried a paragraph saying `TAIL`
could *not* be discarded, resting on
`docs/mcp_tape_manufacture.md` §4's *"multi-level scoping, this
needs real symbol-table scoping"* — **a summary that printed p.37
superseded three days later, in a different file, without this one
being updated**. That paragraph is now replaced by the page itself,
by the condition under which discarding *would* be wrong, and by the
point at which it stops being true (the first multi-program
assembly). Keeping the line in the deck makes the page a literal
transcription and leaves something for that assembly to find.

**And line 6 is exactly the case §5x said to watch for** — a
reference from *outside* the tail block to a symbol defined *inside*
it:

```
002422.40   002424.10 00    $B,Q GO$A
```

C28-6129 printed p.37: *"When tailing is used, the last two
characters of the basic symbol are used for a special character that
indicates tailing is being used and a character to represent the
tail symbol."* So `Q GO$A` **is** the mangled name, spelled out by
hand because from outside the block the plain name would not
resolve. With no mangling at all, reference and definition match for
the same reason they would have matched mangled.

**The `$` in front of the `B` is not explained**, and is recorded
rather than guessed at. p.37 accounts for the `$A` and says nothing
about a `$` on an *operation*. It is in the statement column, not
the name column — checked at 600 dpi against `S CA8` and
`LI(BU,24)` on the row below. The compiled row is a plain branch,
and lines 34 and 50 print the same shape with no `$`.

### A second SWAP, with its matched TRANSMIT on the same page again

Line 53 is `Q FIN  SWAPI,6,Q SAV,$1  -RESTORE INDEXES` — **six**
words, where printed p.40's two were three — and line 10 is its
matched `TI,6,$1,Q SAV  -SAVE THE INDICES`, the same six words the
other way, `A0` against `E0`.

~~**`OP` is still clear, so no SWAP executed** — that is the
measurement, and it is all of it.~~ **RETRACTED 2026-10-23: THIS ROW
IS THE ONE SWAP MCP EXECUTES.** When forward SWAP was built,
`StretchCore` began announcing each swap that starts and the boot
printed exactly one line — `SWAP started at half-word 2649, 6 words`
— which is 002454.40, this row, with this row's count. See the entry
at the top of this file.

Two callers now, in two routines, in the identical save-and-restore
shape.

### Two checks had drifted onto MCP's own working storage

`mcp_comm_region_last_word` and `mcp_comm_region_one_past_is_zero`
sat at `MCP_IPL_AT + IPL_WORDS + COMM_REGION_WORDS`, which assumed
the comm region lands immediately after the image — true while the
image ended at 002147 and p.37's region began at 002150. Seven pages
later `IPL_WORDS` is 925 and that expression points at **002473**,
which is inside the `Q SAV` this very page saves its index registers
into.

The old comment had predicted it: *"if the image grows by a page
this check moves with it and stops being about S MCP — which is the
right failure."* The failure was right.

**The move's extent is now pinned from both sides at addresses that
do not move:**

- **002165** is the last word the fourteen-word move covers, and
  reads **zero**. The image puts p.37's `S TODAY` there, so a move
  one word short leaves a non-zero datum standing.
- **002166** is one past, and it is **printed p.38 line 4's
  `Y UNCOD`** — the TRANSMIT MCP branches to. A move one word long
  destroys it.

Both were zero in the old formulation; one is now a specific
instruction word. Strictly stronger, and neither drifts.

## THE PAGES CLOSE ON S CA6, 2026-10-23

printed p.38 line 12 is `BD,S CA6` and its binary put `S CA6` at
**002422.00** — a prediction made four pages before anything near
that address was opened, and the address the boot run's PC trail has
been stopping at ever since.

**Printed p.42's last datum ends there to the bit.** Its final row is
21 characters of IQS data starting at 002417.30, and 21 × 8 bits
lands on 002422.00 exactly; the assembler's highest compiled word is
`0o2421`, the one before it.

That checks the whole character-count chain at once. Lines 32-38
print no binary except two radix-2 bytes, so no character code is
checked or can be — but every string's **length** is pinned by the
address of the row after it, and the last one is pinned by a symbol
a different deck predicted:

| line | at | datum | chars | next |
|---|---|---|---|---|
| 32 | 002412.00 | `/1234567890=` | 12 | 002413.40 |
| 34 | 002413.50 | `/// /STUVWXYZ` | 13 | 002415.20 |
| 36 | 002415.30 | `,(///-JKLMNOPQR` | 15 | 002417.20 |
| 37 | 002417.20 | `/` | 1 | 002417.30 |
| 38 | 002417.30 | `$*///+ABCDEFGHI/.)///` | 21 | **002422.00** |

### Printed p.41: fourteen predictions on one page

pp.38, 39 and 40 between them SYN'd forty-three symbols they did not
define. p.41 defines **fourteen** of them — `Y NORR`, `Y IDX12`,
`Y UCX12`, `Y UX SAV`, `Y UCBF1`, `Y UCBF2`, `Y UTOE`, `Y GOMK`,
`Y TYPMK`, `Y REL MK`, `Y COMMK`, `Y CNGMK`, `Y BLWD4`, `Y UPDAT` —
every one where those pages said.

**`Y UTOE` could not have been guessed.** p.40 line 20 is
`LF(BU,60,6),Y UTOE`, whose VFL left half prints `002334.64`, a *bit*
address; line 37 of p.41 is `Y UTOE  SYN,Y UCBF1+.372`, a **decimal**
bit offset from a symbol three rows above. 002327.00 plus 372 bits is
002334.64 exactly. Two pages, two notations, one bit.

**The three reservations are checked by what follows them**, not by
their printed size — printed p.24's verifier established that a
`DR`/`DRZ` row prints a size and not a word. Here `002324+3` is
`Y UCBF1`, `002327+8` is `Y UCBF2`, `002337+13` is `Y GOMK`, and all
three of those are themselves earlier pages' predictions. **A wrong
reservation size moves a prediction.**

**The ten masks are eight characters each and the column says so.**
48 bits at byte size 6 is eight characters, every mask blank-padded
to exactly eight, and the proof is column alignment at 600 dpi —
every end-of-statement `X` in one column. **Line 32 is the control**:
`COMPILGOX` puts its X one position *earlier*, because `COMPILGO` is
eight characters and leaves no room for a blank. A datum of any
other length would have moved its X.

### §13 at its thickest, and the decode beat the re-render

p.42 line 24 reads **`C00CC1.5C  CF`** at 200 dpi. At 900 dpi every
one of those glyphs is a digit zero: `000001.50  0F`.

**The decode settles it without the re-render**, which is the rule
this project keeps relearning. printed p.40 lines 37 and 41 are the
same instruction shape — `B,2.32($14)` — and print `000002.50 0E`.
A branch through an index gives 0 in the high nibble and the index
in the low one, so `CF` is not an operation this machine has.

### Two substitutions on p.42, both checked rather than asserted

- **The radix moves from the statement to the operand.** The listing
  writes `(2)DD(BU,8,8),00101010`; the deck writes
  `DD(BU,8,8), (2)00101010`, the form every other deck uses. Both
  rows are in the checked set — `0o52` is `00101010`, `0o165` is
  `01110101` — so the substitution is verified.
- **Line 37's byte size loses a trailing period**, `8.` → `8`,
  because this assembler evaluates a trailing period as `WORD.BIT`
  and 8 words is 512. The addresses prove the size is eight either
  way: line 38 sits eight bits later, and line 38's own length is
  what lands on `S CA6`. printed p.39 line 19's `CF,53.` takes the
  same period and compiles 53, because a count field is evaluated in
  the other context. **The ambiguity is this assembler's, not the
  listing's**, and it is written down rather than worked around.

### And p.42 makes no predictions at all

Every symbol it mentions it also defines — the first page since
printed p.37 for which that is true. **The image is now contiguous
from 000621 to 002421**, and printed p.43, which holds `S CA6`
itself, is the next page and the one the run has been waiting for.

## MCP EXECUTES A SWAP, 2026-10-23

printed p.40 lines 24 and 28:

```
002276.40   000033.00 80   002324.06 E0   SWAPI,3,$11,Y UX SAV
002302.00   000033.00 80   002324.06 E0   SWAPI,3,$11,Y UX SAV
```

`bsv/README.md` has said since 2026-09-22 that SWAP *"is a different
datapath and **nothing in the corpus executes one**"*.
`decks/transmit_multiword.strap` says it, `StretchExecute.bsv`'s own
arm says it, and `run_tests.sh` records a surviving injection
(**T3**) whose whole justification is that sentence. **All four are
now false**, and the instruction is three words from the UNCODE
subroutine's normal exit.

### The page carries its own control

**Line 33 is `TI,3,Y UX SAV,$11`** — the *same three words going the
other way* — and it prints a trailing **`A0`** where the two SWAPs
print **`E0`**. Sub-op 010 against 110, the one bit X22-6533's
TRANSMIT box uses to tell them apart, on two rows of one page. There
is no reading of this that makes the SWAPs transmits.

### And what it is for makes it believable

Lines 23-29 are the **REEL card's handler**. It swaps three index
registers out to `Y UX SAV`, does its work, and swaps the same three
back. A two-way interchange is exactly what *"save these and restore
the old ones"* wants, and it is why a SWAP and not a TRANSMIT is
written here. Lines 33 and 38 are the one-way version, on the exit
paths that do not need the old values back.

**SWAP is now an unbuilt arm with a documented caller** — the shape
backward transmission was in on 2026-10-22, when the same kind of
sentence ("MCP needs neither") died the same way. The boot run does
**not** reach printed p.40 yet, because `S CA6` on printed p.43 comes
first, so the refusal still stands and T3 still survives. **It is a
survival with an expiry date**, and the record says so rather than
being quietly edited.

### Five more predictions land, three of them on bit 18

| symbol | address | predicted by | defined on p.40 |
|---|---|---|---|
| `Y IODC` | 002266.40 | p.38 line 34, `.50` | line 14 |
| `Y REELC` | 002276.00 | p.38 line 40, `.36` | line 23 |
| `Y JCCER` | 002303.40 | p.38 line 35, `.72` | line 30 |
| `Y UER` | 002311.00 | p.38 lines 8/36/38/41 | line 38 |
| `Y UCLLC` | 002262.00 | p.39 line 56, `.32` | line 5 |

**The half-word selector has now been checked on five separate
symbols by three separate pages**, each transcribed before the page
that defines it. `Y IODC`, `Y JCCER` and `Y UCLLC` would all have
been half a word wrong without bit 18.

### A TRANSMIT's count register is written without its `$`

Line 36's listing is `T,$15,Y UCBF2,0.0($15)` and the deck writes
`T, 15, ...`, which is printed p.4 line 28's convention. Reference
Manual printed p.30: the direct count comes from *"the field J, bits
51-54"*, so that `$15` is a **four-bit register number**, not an
address — as an address it would be word `0o37` and the assembler
refuses it in those words. **Line 33's `TI,3,Y UX SAV,$11` keeps its
`$11`**, because there the index register *is* the transmit's source
address and the count is the immediate 3. Same page, both readings,
and the binary distinguishes them.

## PRINTED p.39, AND p.38's PREDICTIONS START LANDING, 2026-10-23

printed p.38 used fourteen symbols it did not define and SYN'd each
from its own binary output. **Three of them are defined on the very
next page**, at exactly the addresses p.38 said:

| symbol | address | p.38's row | p.39's row |
|---|---|---|---|
| `Y JCBC` | 002213.00 | line 30, `BXEZ,Y JCBC` | line 4 |
| `Y TCPGO` | 002214.40 | line 31, `BXLZ,Y TCPGO` | line 7 |
| `Y LIMC` | 002246.00 | line 33, `BXEZ,Y LIMC` | line 44 |

**`Y TCPGO` is the sharpest of the three.** p.38 line 31 prints
`002214.72 46`, and `.72` has **bit 18 set** — the half-word
selector — so the address is `002214.40` and not `002214.00`. Line
7 here is `002214.40`. A reading that ignored bit 18 would have been
half a word wrong, and would have been caught by a page transcribed
afterwards.

p.39 confirms six more by *using* them: `S ROOF` (p.37), `Y USB8C`
(p.38), `Y NLST` and `Y NOPUN` (p.36, both at 001775.40), and p.38's
predictions `Y UER` and `Y UCBF2`.

### `SF` is a connective wearing another name

Line 52 is `SF(BU,18,3),$12` and the assembler refused it. The
printed word is

```
002254.00   000034.00 80   022300.12 F0
```

The trailing `F0` is **CM**, Connect to Memory (C prints `70`, CT
`77`), and `.12`'s bits 19-22 are the connective **function: 0101**.
`CM0011` renders `.06` and does not match; `CM0101` renders `.12`
and does.

**And the pair makes sense as a pair**, which is what makes it more
than a fitted constant. `LF` was already known to be `C0011`. A
connective's four bits are a **truth table over (accumulator bit,
memory bit)**, so `0011` and `0101` are the two *operand-selecting*
functions — LOAD FIELD takes the memory operand into the accumulator
with `C`, STORE FIELD takes the accumulator operand into memory with
`CM`. Lines 51 and 52 are adjacent rows doing exactly that.

**Three injections**, through `tests/inject.py`, and each wrong
candidate fails in a *different field* — which is how the check
shows it pins both halves of the derivation: `CM0011` (LF's
function) misses in the function field, `C0101` misses in the
C-versus-CM byte, `CM1010` misses in the function field the other
way.

The same lesson `LF` taught: **before implementing a mnemonic,
decode one of its assembled words and look for that bit pattern
among the operations already encoded.** No tally is kept here on
purpose — `LF`, the `LFI` suffix fix and this one are the same
lesson in three different shapes, and counting them invites the
ordinal to go stale.

### Three rows needed a second look, and the deck was right about all three

Each is a reading fault this project already has a name for:

- **line 25** — its LOCATION is `002231.40`, which a 200 dpi read
  made `002231.00`. **The tell was arithmetic, not typography**:
  line 24 is a full-word VFL instruction, so line 25 cannot be half
  a word after it. (A full word at an *odd* half word is normal
  here; p.38 line 6 does it too.)
- **line 43** — the code column prints `002313.5C  C0` and **both
  of those glyphs are digit zeros**: `002313.50 00`. The octal field
  proves it — `.5C` cannot be octal — and the hex byte follows,
  because the two glyphs are the same shape. `listing_typography.md`
  §13, with §13a's self-disagreeing field one level up: the row
  above prints `001000.00 F0` with round zeros.
- **line 55** — the binary is `.70 90`, not `.70 50`. A 200 dpi read
  made the 9 a 5, which decoded to `LC` where the statement column
  says `KV` in crisp 900 dpi glyphs. **600 dpi for octal and 900 for
  hex is the rule and 200 dpi is not evidence**; the two columns
  never actually disagreed.

### The run is unchanged, deliberately

MCP calls `S CA6` before it reaches any of p.39's entry points, and
`S CA6` is on printed p.43. p.39 is one of the four pages the image
needs in order to stay **contiguous** before p.43 can be added.
Three to go: pp.40, 41, 42.

## MCP IS RUNNING THE UNCODE SUBROUTINE, 2026-10-23

printed p.38 line 4 is

```
002166.00  000033.00 80  002324.06 A0   Y UNCOD  TI,3,$11,Y UX SAV
```

**002166.00 is the address printed p.37 line 45 calls `S PRIME` and
the PC trail said MCP branched to.** The PRIME ROUTINE and the
UNCODE SUBROUTINE are the same entry, which neither page says on its
own — p.37 names the address, p.38 names the code, and only putting
them together names the thing.

With p.38 in the image the boot run executes it: the class-column
test on lines 6-8 **passes** — the card really does carry a `B` in
the column `C22-6728` printed p.88 names — and the PC trail moves to

```
PC TRAIL: last non-zero half-word address 2596, after 6002202 steps
```

2596 half-words is **002422.00**, which is `S CA6`, the routine line
12 calls to convert the card to six-bit BCD.

### A page that is mostly predictions

Thirty-six rows with binary output, bit-exact on the first run.
Nineteen symbol locations — and **fourteen of them are symbols the
page does not define**, every one at an address later than anything
transcribed (002213 through 002502, where the page itself ends at
002213.00). Each is SYN'd from this page's own binary output:

| | | |
|---|---|---|
| `Y UX SAV` 002324.00 | `Y UCBF2` 002337.00 | `Y JCCER` 002303.40 |
| `Y UER` 002311.00 | `Y JCBC` 002213.00 | `Y REELC` 002276.00 |
| `S CA6` 002422.00 | `Y TCPGO` 002214.40 | `Y REL MK` 002360.00 |
| `Y UCBF1` 002327.00 | `Y LIMC` 002246.00 | `Y TYPMK` 002355.00 |
| `S BRK8` 002502.00 | `Y IODC` 002266.40 | |

**Reading them needed the half-word BIT layout, not just the
octal.** A half-word prints `wwwwww.bb XX` and the `.bb` pair is
bits 18-23: bit 18 the **half-word selector**, bits 19-22 the J
field, bit 23 the first bit of the operation code. So line 30's
`.32` and line 40's `.36` are bit 18 **clear** — the first half
word, `.00` — while line 31's `.72`, line 34's `.50` and line 35's
`.72` are bit 18 **set**, which is `.40`. Three of the fourteen
would have been half a word wrong without it.

`Y UER` appears in **four** rows (8, 36, 38, 41) with three
different operation codes and agrees in all of them.

### Lines 13-15 and 18-20 are arguments, not instructions

`LVI,$15,$+1.0` plants the return address in `$15` and
`BD,<routine>` goes; the half-words **after** the branch are the
call's parameters, and the routine steps over them on the way back.
That is why two `VF`/`CF`/`VF` triples sit between branches. A
transcription that read them as code would still assemble, which is
why their addresses are checked as well as their contents.

`CF` compiles a bare eighteen-bit count — line 14's `CF,80` prints
`000120`, which is eighty, the number of columns on a card.

### The next five pages, and why they have to be five

`S CA6` is at 002422.00. Printed p.42 runs 002365.60 to 002417.30
and printed p.45 opens at 002501.71, so **`S CA6` is on printed
p.43** and `S BRK8` at 002502.00 is printed p.45 line 10.

`strap/prosa.py`'s `mcp_ipl_image()` requires the image to be
**contiguous** — "a hole would silently become a zero word in the
record, and a zero half-word is BRANCH ENABLED to location zero" —
so printed pp.39, 40, 41 and 42 have to be transcribed before p.43
can help. Five pages, in order, each one extending the run.

## MCP FINISHED ITS INITIALIZATION, 2026-10-23

It did not get lost. The run that ended at "PC 0" ended at
**002166.00**, and printed p.37 line 45 names that address
`S PRIME  SYN,$  - SAVED ADDRESS FOR PRIME ROUTINE`, with line 31
nine rows above it reading
`S PR IN  VF,S PRIME  -ENTRY TO PRIME ROUTINE`.

MCP's IPL initialization **ran printed pp.15 through 36 without
entering a single error site** — `X ERR AD` is zero — filled its
communication region, and branched to the next phase.

### The probe that turned "PC 0" into a sentence

A halt reports the PC it stopped at, and that is enough while a
program stops somewhere it meant to. It stops being enough the
moment one branches into storage that holds zeros: a zero half-word
is `BE, 0.0`, so **every such run reports PC 0 and they all look
alike**. `gen_tb.py` gained an opt-in `pc_trail` that keeps the last
NON-zero program counter, which is the branch's destination.

```
PC TRAIL: last non-zero half-word address 2284, after 6002413 steps
```

2284 half-words is 002166.00. **It earned its keep on its first
run**, and the cost is one `$display` on the tests that ask for it.

### printed p.37 is transcribed — and it is a different source deck

Its card sequence restarts at **13000001** where p.36's ended at
`11C11xxx`, and the banner reads `******* THE COMMUNICATION REGION
FOR MCP *******`. **The LOCATION counter does not restart**: p.36's
last datum is `X ABN` at 002146.74, thirty-six bits, which runs into
002147, and p.37 opens with a `CNOP` at 002147.40. Forty-six rows,
twenty-three with binary output, **bit-exact on the first run**.

### TWENTY-ONE EXTERNALS BECAME DEFINITIONS

`strap/mcp_image.py`'s `merge()` carried **44** names used across
printed pp.15-36 with no definition on any transcribed page, each
held up by one page's stand-in `SYN`. This one page defines
twenty-one of them:

| | | |
|---|---|---|
| `S MCP` 002150.00 | `S MAXRN` 002155.40 | `S IF DMP` 002161.00 |
| `S COM SZ` 002150.40 | `S YCOCH` 002156.00 | `S REJ JB` 002161.40 |
| `S COM RG` 002151.00 | `S YPRCH` 002156.40 | `S ROOF` 002162.00 |
| `S XCHAN` 002152.00 | `S DKMCP` 002157.00 | `S MARK` 002162.40 |
| `S BAMCP` 002153.00 | `S SYRFT` 002157.40 | `S IA` 002163.00 |
| `S R TAPE` 002153.40 | `S PR IN` 002160.00 | |
| `S W TAPE` 002154.00 | `S PR OUT` 002160.40 | |
| `S READ R` 002154.40 | `S BA PP` 002155.00 | |

**Every one of those addresses was decoded out of an instruction on
one of NINE earlier pages**, before this page was opened. The merge
now checks each stand-in against a definition instead of against
itself: **externals 44 → 23**, and the number of stand-ins actually
checked against a definition rose accordingly — they all agree. The pp.7-8/pp.9-13 cross-check in its strongest form
so far.

### A FIXTURE NUMBER THAT WAS DERIVED, CORRECTED BY THE DOCUMENT

`strap/prosa.py` had `COMM_REGION_WORDS = 15`, from a lower bound it
argued for at length: the smallest region containing every
comm-region symbol pp.15-36 mention, 002150.00 through 002166.00
inclusive, "twenty-two symbols in fifteen words". Line 9 of p.37 is

```
002150.40  000016.00+   S COM SZ  VF,S END CM-S MCP
                        -SIZE OF COMMUNICATION REGION
```

and `0o16` is **fourteen**. The symbol the derivation had at
002166.00 is `Y UNCOD`, and lines 44-45 put `S END CM` and `S PRIME`
there — the END of the region, and the address MCP branches to.

**A LOWER BOUND FROM USAGE CANNOT SEE WHICH SIDE OF THE BOUNDARY THE
LAST SYMBOL IS ON**, and that is the generalisable part: an address
used as a BRANCH TARGET and an address used as a TABLE SLOT look
identical from the instruction that mentions them. Every symbol the
derivation found was real and every address was right. The size had
to come from the program's own arithmetic, and line 9 is that
arithmetic.

### AN OMITTED BYTE SIZE IS EIGHT, and the assembler used to refuse it

Lines 42 and 43 are `(AX)DD(BU),03/15/63X` and
`(AX)DD(BU),  /  /63X` — **no byte size in the dds at all** — and
the listing puts them one word apart. C28-6129 printed p.16:

> "the byte size in a 7030 statement may range from 1 through 8
> because the byte size field is **restricted to 3 bits** in length.
> Therefore, **byte size is treated modulo 8** by STRAP."

A three-bit field cannot hold 8, so 8 is written as 0 — and
C22-6531 printed p.7 makes a null field compile as a zero, which
reaches the same place. **This is the 7030's standing idiom, not a
special case**: printed p.30 reads a zero immediate TRANSMIT count
as sixteen and a zero control-word count as 2¹⁸ by the identical
argument.

The two rows print no binary, as pp.9-12's `(IQS*)` messages do not,
so no character code is checked. What *is* checked is the counting —
and the counting is what found the rule. Line 43's blanks were
counted by **column alignment** against line 42 at 900 dpi: its two
slashes sit under line 42's two slashes, so `"  /  /63"` has two
blanks per gap and not three.

(The expected values the boot test computes are a free second
witness for the character set: `0x0A03110105110603` is `03/15/63`
and `0x0000110000110603` is `  /  /63` in six-bit BCD with the two
leading zeros p.16 describes.)

### WHAT THE RUN SAYS ABOUT THE REGION, AND WHAT IS STILL OPEN

Adding p.37 to the image moved two boot checks onto words MCP
rewrites. **The image does arrive** — `002150`'s LOW half still
holds p.37 line 9's `S COM SZ` (`0x38000`) at the end of the run,
while MCP writes `S MCP` into the HIGH half of the same word
(printed p.20 line 11, `SV,$10,S MCP`). One word with both halves of
the story in it, and it is a check now.

The pair moved down to 002146 and 002147, which are also the two
words that **straddle the join between the two source decks** —
p.36's thirty-six-bit `X ABN` runs into 002147 and p.37's `CNOP`
sits in it. One word, two decks, right only if both are.

**ALL EIGHT ARE EXPLAINED, AND THE EXPLANATION IS printed p.15
lines 20-21:**

```
X101  LC, $0, X BUFER+.32($9)     -GET SIZE OF COMM REGION
      T, $0, X BUFER($9), S MCP   -MOVE COMM REGION
```

A direct-count TRANSMIT whose count MCP **loads out of the record**,
so the fixture's comm-region block — a descriptor and thirteen zeros
— is written over the real one. **002150 through 002165 inclusive IS
fourteen words** (`0o2165 - 0o2150 + 1 = 0o16`), so the move covers
the whole region including `S DATE` and `S TODAY`. MCP then writes
002152, 002155, 002156, 002157 and 002162 over the zeros, and
002150's high half last of all.

**I HAD THIS "STILL OPEN" FOR AN HOUR ON AN OCTAL SLIP** — I read
fourteen words from 002150 as ending at 002163 rather than 002165,
which left two words apparently unaccounted for and sent me looking
for a second writer that does not exist. **MEASURED, not re-derived:**
rebuilding with a two-word block moved the boundary exactly two words
and every other word came back holding the image's value —
002164 reading `0x0A03110105110603` and 002165 `0x0000110000110603`,
IBM's `03/15/63` and `  /  /63`. A probe that moves the boundary
beats re-checking the arithmetic that put it in the wrong place.

**AND THE FIXTURE'S DESCRIPTOR AND IBM'S OWN `S COM SZ` NOW AGREE
BIT FOR BIT**, which is worth more than either on its own. `LC`
reads a half-word's bits 31:14 (`StretchExecute.bsv`'s `dixop_LC`:
`count: h[31:14]`); `prosa.py`'s `comm_descriptor` puts
`size_words << 14`, which is those bits; and p.37 line 9's
`S COM SZ` compiles to `0x00038000`, whose bits 31:14 are **14**.
The fixture's invented field and the document's compiled word are
the same thirty-two bits — so a check on 002150 after the run is a
cross-check between them, not a measurement of the move.

**I NEARLY SHIPPED THAT AS "THE IMAGE ARRIVES ANYWAY".** 002150's
low half is unchanged at the end of the run, and the obvious reading
is that the comm move did not reach it. It did; it wrote the same
bits. Fourth unmeasured structural claim of this phase, caught
before the commit this time, by doing the two-minute read of `LC`
against `index_word` that the reading demanded.

### TRIED AND REVERTED: the comm block built out of printed p.37

The obvious next step is to stop inventing the block at all. p.37
**is** the communication region, so the fourteen words the record
carries could be p.37's own, with the single field the fixture must
supply — `S MCP`, "SLOT FOR BASE ADDRESS OF MCP", which p.37
compiles as zero because the address is not known until the tape is
generated. Fourteen invented words down to one invented field.

**It works and the run is unchanged** (same PC trail, same step
count to the digit), and `S DATE` and `S TODAY` end the run holding
IBM's dates instead of zeros. **It was reverted anyway**, for two
reasons worth writing down:

1. `mcp_console_channel_in_comm_region` moves from
   `0x0004600000000000` to `0x0004640000000400` — which is expected
   in kind, because the region now STARTS at p.37's `VF,22.4` in
   both channel slots instead of zero and MCP writes over a
   different residue, but "expected in kind" is not a measurement.
2. `mcp_comm_region_last_word` reads zero where the fixture now
   expects `S TODAY`, and I cannot yet say why.

**The fixture's whole comm-block concept is an inference** from
printed p.15 lines 17-21 — that the PROSA record carries a copy of
the region at the offset the three-register `LVS` computes. Nothing
read so far states it. Replacing invented contents inside an
inferred structure is not obviously progress, and it perturbs two
measured values. The change is described here so it can be made
deliberately rather than discovered again.

## MCP TYPES A MESSAGE TO ITS OPERATOR, 2026-10-22

```
<CR><RED> DATE OF IPL TAPE <CR>00 MONTH 00 DAY  <CR><EOM>
```

Five words, out of printed pp.21-24's date routine, on the console
MCP found in the channel status table it relocated itself, on a
machine it configured from cards it read off a tape.

The date reads 00/00 because the fixture's tape has no date on it.
printed p.21 lines 17-20 build the digits with
`M+MG(BU,4),X MONTH+.3,24` and three more like it, **adding** into
the literal `00 MONTH ` / `00 DAY  ` that lines 37-38 assemble; what
they add comes from `X VERFY`, which printed p.2 line 27 declares as
`DD(BU,32,8),0 -SLOT FOR DATE OF SOURCE TAPE`. `strap/prosa.py`
writes no tape label, so the slot is zero and zero is what gets
added. What the message proves is the **path**: relocation, console
hunt, and WRITE.

### TRANSMIT BACKWARD is built, and a page of MCP is why

`decks/transmit_multiword.strap` used to say *"NOT TESTED HERE,
deliberately: backward transmission and SWAP ... **MCP needs
neither**."* printed p.19 line 41 is `TB,3,0.0($11),0.0($13) -MOVE
BIASED CTS`, and with the IOCD deck on the tape the boot run reaches
it.

**The spec is one sign.** Reference Manual printed p.30:

> "In **forward** transmission, the sending and receiving addresses
> of each successive word transmitted are obtained by
> **incrementing** the previous addresses by one. The starting
> addresses specified in the instruction are therefore the addresses
> of the **first** word in each of the two storage areas.
>
> In **backward** transmission ... by **decrementing** the previous
> addresses by one. The starting addresses ... are therefore the
> addresses of the **last** word in each of the two storage areas."

So the instruction's own addresses are the starting pair either way
and only the step changes sign. The change is three lines: `XmitXfer`
carries the direction, `rl_xmit` decrements when it is set, and the
Transmit arm stops refusing it. **SWAP still sets OP** — a two-way
interchange is a different datapath and nothing in the corpus
executes one.

The deck now tests both directions against the case each is
*required* for, which the same page names: *"When the receiving area
overlaps the upper end of the sending area, backward transmission
must be used; if the receiving area overlaps the lower end, forward
must be used."*

**Four injections.** T1 and T2 are caught with distinct failure
sets — T2's extra two are the tell, because an ascending run from
`BWS2` never writes the words below it. **T3, accepting SWAP as
well, SURVIVES and must** (**until 2026-10-23 — printed p.40 lines
24 and 28 are `SWAPI,3,$11,Y UX SAV`; see that page's section
above**): no deck executed a SWAP, so nothing could
see the difference. Its *encoding* is pinned by
`decks/ax4b_1246_transmit_swap.strap`; its *execution* is not tested
by anything, and the record now says so.

**T4 had to be WRITTEN, not re-run.** `decks/transmit_scope.strap`'s
block 6 flipped from asserting a refusal to asserting the move, so
its old injection — "remove the backward check" — became
meaningless: the check is gone. The replacement is its inverse,
restoring `t.backward == 1 ||` in the Transmit arm, and it is caught
at a named address: the run hangs on block 6's `BOP,$` at
**`004111.40`** (half-word 4243), `DST6` reads zero, and the step cap
reports "reached without halting". **A flipped assertion needs a
flipped injection**; re-running the old one would have reported a
survival and meant nothing.

That flip also moved the deck's `PASS` back one half-word, 4246 to
4245, because `BZOP,$ / BOPZ,$+.32` became a single `BOP,$` — so the
run's PC check is load-bearing in that file and not decoration.

### The deck's alignment pad failed loudly, in a recognisable shape

The pad was `NOP, 0` — exactly one half-word, and therefore correct
only while the instruction run above it has **odd parity**. The new
steps added two words and a half, parity flipped, and every `DD`
below came out **half a word low**: the first check read
`0x1800A0000000` where it wanted `0xA000000000000001`, which is two
adjacent words seen through a 32-bit shift. It is `CNOP` now, which
rounds to the next full word whatever the parity is.

### Next: THE STATUS BIT AND THE SILENT CONSOLE ARE ONE GATE

The run ends with `X ERR AD` holding printed p.3's `X ERR 05` — one
row below `X7 3 BRZ,0.0 -SUCCESSFUL` — which printed p.7 line 12's
error table maps to `X MSG 05`, **"UNSUCCESSFUL COMPLETION"**. The
test is printed p.3 lines 26-28: `BB,X IPL BS+.24` spins while the
SEOP status bit is set, then `CT0011(BU,5),X IPL BS+.19` tests
control-word bits **19-23** — EPGK, UK, EE, EOP, CS — and `BRZ,0.0`
returns only if all five are off.

**IT IS NOT THE WRITE. IT IS THE READ THAT FOLLOWS IT, AND THE MODEL
PREDICTED IT IN ITS OWN SOURCE.** printed p.21 line 24, the
instruction `X7 3`'s `BRZ` returns to after the date message, is
`B,X IO`, and `X IO` is printed p.22 line 5:

```
XIO     RD(SEOP),0.0($15),X DCW 2    -GET IPL OPTIONS
```

with `X DCW 2 = CW,X LR IN,3,0` — **a three-word READ from the
console**. `StretchExecute.bsv`'s `wrongUnit` guard excludes the
console from `RD`'s legal units and sets `cw.epgk = 1; cw.eop = 1`.
**EPGK is control-word bit 19 and EOP is bit 22** — both inside the
five bits `CT0011` tests. So p.22 line 5 program-checks, p.3's shared
I/O test finds it, and the run ends in `X ERROR` at printed p.6 line
1's `BD,$`, half-word 239.

**I HAD THIS WRONG TWICE BEFORE READING THE ARM.** First I looked for
a bit the console WRITE leaves behind — it leaves none, and the
message came out right. Then I guessed the READ "falls through to the
card reader's image", which is what `StretchCore.bsv`'s device `else`
would do if the transfer ever started; it never starts, because
`execute()` refuses it two stages earlier. **The arm was commented
for this exact day:**

> "THE CONSOLE IS WRITE-ONLY HERE, AND THAT IS A KNOWN DEVIATION
> rather than a modelling choice… Nothing on the path that runs today
> reads them, so the three-word switch image is not built and a READ
> here program-checks instead. **When the IPL needs the switches this
> is the line to change**, and the capacity in StretchCore's `rl_io`
> is 3."

That is the second time in this phase a check's own comment named the
next failure before it happened; the Address Invalid one was the
first. A deviation recorded where the code is beats a deviation
recorded in a plan.

### What to build: the console's three switch words

Reference Manual **printed p.150** (PDF 153), the console's whole
specification, read first-hand:

> "A READ instruction received by the console **with the keyboard not
> enabled** is automatically terminated when the **three words
> scanned from the switches** have been sent to the exchange."

and, at the head of the same page, "The console has a byte weight of
zero and a word weight of **3**." The word weight *is* the three
switch words, and MCP's count of three is that word weight exactly.
`C22-6678-1` printed p.29 says what the operator sets in them: the
time and date, in binary keys 0-23 and 32-55.

**ZERO IS THE RIGHT DEFAULT AND MCP SAYS SO.** printed p.22 line 12
is `KFI(BU,24),0,40 -NO TIME ENTERED` followed by `BAE,X V NO TM`:
all-zero switches *are* the documented "the operator entered nothing"
case, so a zeroed register is a real configuration and not a stub.

**AND THE ENTER KEY IS A CHANNEL SIGNAL**, which is the other half of
MCP's console protocol and explains printed p.23. Line 39 is
`BZB,X IPL BS+.23,X IO A` — spin while control-word bit 23 (CS) is
off — and p.150 says *"Enter. Depression of this key enables the
keyboard and generates a **channel-signal** indication."* That loop
is MCP waiting for a human. With zero switches the run never reaches
it: printed p.23 line 30's `BZB,X LR IN+.29` takes the other branch.

**Two more status rules from the same page**, for whoever builds it:
the ERASE key "terminates the READ operation with an end-exception
indication", and during a WRITE the same key "immediately terminates
the WRITE operation with an end-exception indication" — "in both
cases the end-exception is accompanied by end-of-operation **unless
the multiple block flag in the control word is on**." Neither is
reachable without an operator, so neither needs building first.

**MEASURED, AND EVERY FIELD CORROBORATES.** printed p.3 line 23 is
`X7 1 CCW  CCW,0($15),X IPL BS`, so `X IPL BS` holds MCP's own copy
of the control word as of the failing I/O TEST — no new model
plumbing needed. The boot testbench now checks it, and it reads

```
0x008A920000000000
```

which decodes, field by field, to the whole story:

| field | value | why |
|---|---|---|
| data word address | `0o1052` | `X DATE 1 + X DATE K`, one past the date message — the chained WRITE ran to its end. `X DATE K` is printed p.21 line 42's `SYN,$-X DATE 1`, **five words**, which is how many console words this test checks. It lands on `X IO` because printed p.22 opens with `SLC,(8)1052.0` right after the message. |
| 18 unit ready | 0 | |
| **19 exchange program check** | **1** | the console READ |
| 20 unit check | 0 | |
| 21 end exception | 0 | |
| **22 end of operation** | **1** | set alongside EPGK: the operation never started |
| 23 channel signal | 0 | no operator |
| 24 suppress end of op | 0 | cleared at the WRITE's completion |
| chain / count / refill | 0 / 0 / 0 | printed p.21 line 30's `X DCW 1  CW,X DATE 1,X DATE K,0` is exhausted |

**Bits 19 and 22 are exactly the pair `wrongUnit` sets, and nothing
else is on.** The WRITE before it finished cleanly — the model says
so in the same word that reports the failure.

**This was derived from the model's source first and measured
second, and that order mattered**: the two readings before it were
derived and wrong. The check is written as an expression over
`X DATE 1`, `X DATE K` and the two bit numbers, not as the constant,
so it cannot drift from the thing it describes.

**ITS INJECTION IS THE HALF-FIX.** Permit the console on `RD` — add
`&& !consoleCh` to `wrongUnit`'s RD arm, one token — without
building the switch register. Four checks fail: the control word
becomes `0x0087C00000000000` (dataAddr `0o1037` = `X LR IN` + 3,
every status bit off), `X ERR AD` goes to zero, `PC` reads 0 against
239 and the indicator register `0x1324` against `0x9424`.

> **CORRECTION, SAME DAY, AND IT MATTERS.** I wrote here and in
> commit `a945d53` that the half-fix is *worse* than the refusal,
> because the read "succeeded out of the card reader's image". The
> mechanism is right — `StretchCore.bsv`'s device arm only knows it
> is a console on the WRITE side — but the conclusion was not
> measured. When the switch register was actually built, **the run
> produced byte-for-byte the same four values.** The card reader's
> image in this fixture is all zeros and so is the switch register,
> so nothing could tell them apart. The four checks were measuring
> "MCP now gets past the read", not "the card reader served it".
>
> That is the third unmeasured structural claim in this one phase,
> after the two above, and it is the one that got into a commit
> message. **The injection, not the reasoning, is the claim.**

**AND THE THREE WORDS HAVE A DOCUMENTED LAYOUT**, which makes the
register a real device and not a zero-filled placeholder.
`C22-6678-1` printed p.29 = PDF 29, "INITIALIZING THE SYSTEM", step
2: *"Set up the time in binary keys 0-23, and the date in binary keys
32-55."* Its table:

| Console binary key latched on | Option |
|---|---|
| **0–23** | Time |
| **32–55** | Date |
| 28 | Suppress Messages |
| 29 | I/O Status Report |
| 30 | Rejected Job Count Report |
| 31 | Abnormal MCP Mode Report |

**The binary keys are the FIRST of the three words, and MCP's own
code proves the bit numbering independently.** printed p.22 line 11
is `L(BU,64),X LR IN` — one word — and printed p.23 line 30 is
`BZB,X LR IN+.29,X20B  - IF I/O STATUS REPORT DESIRED`: bit 29 of
the first word is binary key 29, which p.29's table calls I/O Status
Report. Two documents that do not cite each other, agreeing bit for
bit.

So a testbench that sets word 0 to a real date would make printed
p.21's message print a real one, and `X VERFY` is *not* the only
source — printed p.22 lines 9-24 validate the switch digits and
printed p.23 line 15 loads `X VDATE`. That is the first thing to try
once the register exists.

## THE SWITCHES ARE BUILT, AND MCP RAN OFF THE END OF THE
## TRANSCRIPTION, 2026-10-22

Four pieces, not the one the guard looked like:

1. a three-word switch register in `StretchIO.bsv` (`switchImg`),
   zero at power-on, with `consoleSwitchWord`/`setConsoleSwitchWord`
   beside `consolePos`;
2. `rl_io`'s device arm splitting on `DevConsole` for READ as it
   already did for WRITE — scanning, not consuming, so nothing
   advances — and a **capacity of 3** on that direction only;
3. **the `devIdx` origin**, which is the piece I missed and the model
   caught in one word. A console WRITE starts at `consolePos`; a
   console READ must start at **zero**, because the switches have no
   position. Left at `consolePos` — 8 after the date message — the
   read began past a capacity of 3 and `rl_io`'s "runs out of
   material" arm fired before a single word moved. The control word
   came back `0x00870400000C0000`: **End Exception on, data word
   address still `X LR IN`, count still 3.** A transfer that moved
   nothing and said exactly why;
4. `wrongUnit` dropping the console from the RD exclusion, last.

### MCP used them, and said so in BCD

`X LR IN`'s first word reads **`0xAAAAAA00AAAAAA00`** at the end of
the run: nibble `1010` six times across **bits 0-23** and six more
across **bits 32-55**, and nothing in between or after. Those are
`C22-6678-1` printed p.29's Time and Date key fields exactly, and the
nibble is MCP's own — printed p.24 line 13 is
`X VZER  LFI(BU,4),(2)1010,46  - BCD ZERO`, under the banner *"replace
a blank character with a BCD zero"*. The whole path is legible in one
word: switches read (all zero), printed p.22 line 12's
`KFI(BU,24),0,40  -NO TIME ENTERED` taken, blank-to-BCD-zero run over
both fields p.29 names.

### AN ALL-ZERO FIXTURE CANNOT TEST AN ALL-ZERO REGISTER

The first injection written against the new check — serve the console
READ out of the card reader's image again, which is what the model
did before — **SURVIVED**. Both images are zero; there is nothing to
see. The fix is that the testbench now *sets* switch words 1 and 2 to
markers (`0x5A5A…`, `0xA5A5…`), which MCP reads into `X LR IN+1` and
`X LR IN+2` and then never touches, because those are p.29's NUMERIC
switches and only the I/O-status-report path reads them. Re-run, the
injection is caught in its own two checks.

**Word 0 stays zero deliberately**: all-zero *is* p.22's "no time
entered", and taking that branch is what exercises p.24's BCD-zero
routine. An operator who sets nothing is a real operator.

### WHERE IT STOPS NOW: PC 0, AND THAT IS A SENTENCE

No error site runs — `X ERR AD` is **zero** — and the run ends with
the program counter at **0**. That is not a mystery and not a crash:
`UNCOND_BRANCH_CODES["BE"]` is `0b000` and the address field is zero,
so **`BE, 0.0` assembles to all zeros** (checked with the assembler)
and all zeros disassemble to it. MCP has branched into storage this
project has not transcribed, where every word is a branch to location
zero and location zero is another one — which the model reports as
"the last instruction branched to itself".

**MCP ran off the end of the transcription.** Printed p.36 is the
last page in the image; the next source deck begins at printed p.37,
"THE COMMUNICATION REGION FOR MCP", card sequence 13000001. **That is
the next transcription**, and `pc_check=0` is what will notice when it
lands.

### How far it got, measured

The communication region is populated at the end of the run:

| symbol | value | what it is |
|---|---|---|
| `S YCOCH` | `0x0004600000000000` | **35** in bits 0-18. MCP learned it from the IOCD cards on the tape, and the value is confirmed independently of any decoding: printed p.21 line 5 is `LV,$15,S YCOCH  -GET CONSOLE CHANNEL` and every console WRITE addresses `0.0($15)` — **the date message printed, so `$15` is the console.** |
| `S YPRCH` | same | **OPEN, and flagged rather than explained.** The printer channel slot holds the same 35, but `strap/prosa.py`'s IOCD deck puts the printer on channel **33**, and printed p.25 lines 22-24 store a *difference* (`SX,$10,$R` / `-(BU,19),S XCHAN,45` / `ST(BU,19),S YPRCH`), not a channel address. Whether 35 is that difference coming out right, the "IF NO PRINTER" path at line 26 leaving something behind, or a real bug is **not established** — only the two values being equal is measured. |
| `S MARK`, `S MCP`, `S XCHAN`, `S MAXRN`, `S DKMCP`, `S SYRFT` | non-zero | filled during printed pp.25-36 |
| `S PRIN`, `S PROUT`, `S READR`, `S RTAPE`, `S WTAPE`, `S IA`, `S REJJB`, `S BAMCP`, `S COMRG` | zero | not reached, or no device for them |

and the indicator register moved from `0x9424` to `0x1324` — `XCZ`
and `XE` out, `MOP` and `XH` in, all five result indicators of
whatever ran last. **`OP` is still clear**, which is the bit that
check is for: eleven pages further on, the model still refuses
nothing MCP executes.

### Also found while reading for this, and worth fixing on the way

**The refill arm adopts a chained control word verbatim.**
`StretchCore.bsv`'s `ioRefillIssued` branch does
`ioDev.writeChanCW(x.ch, n)` with `n` unpacked straight out of core
storage, where bits 18-24 are zero — so **a chained SEOP operation
clears its own SEOP status bit the moment it refills**, and the date
message *is* a chain (`X DCW` chains to `X DCW 1`).

**THIS IS NOT AN INFERENCE, AND I NEARLY FILED IT AS ONE.** I was
about to flag it the way `tape_unit_contract.md` item 31 flags the
SEOP clear, on the grounds that printed p.123's "ignored" does not
say what the exchange does with its own copy. **Reference Manual
printed p.107 says, in the paragraph introducing Figure 35's status
field:**

> "Bits 18 to 24, Status Bits. When obtaining a control word from
> core storage, the exchange **ignores these bits and treats them as
> if they were zero**. **Inside the exchange, however, these same bit
> positions are used to retain the status bits which indicate the
> status of the unit.**"

*Retain* — the exchange's own status is kept in those positions, and
a fetched word's zeros are not copied over it. The refill arm is
simply wrong. Nothing observable depends on it today (the poll exits
early and then finds zeros), which is exactly why it should be fixed
before something does. **The page was two clicks away the whole
time** — see the half-read note above; this is the same page Figure
35 was transcribed from.

The same page settles a second thing, against MCP's own prose. printed
p.3 line 47's comment reads `-YES*TEST FOR UK` on a branch testing
bit **19**, and p.107 is explicit: *"19-22. Exchange Program Check,
Unit Check, End Exception, End of Operation"* and *"23. Channel
Signal"*. So 19 is EPGK, 20 is UK, and the listing's comment is loose
prose. `docs/exchange_and_io.md` §3.2's table was right. p.107 also
confirms the field `CT0011(BU,5)` at `.19` covers: *"Bits 19 through
23 have corresponding indicators in the indicator register"* — MCP
tests exactly the set the manual groups.

## ONE IOD CARD, AND MCP RUNS ELEVEN PAGES FURTHER -- the next gate is TRANSMIT BACKWARD, 2026-10-22

With an IOD card terminating the deck, the boot run reaches
**printed p.20 line 18, `XERR 20 BD,$ -YES *ERROR* NO CONSOLE`** —
IBM's own stop — with **`X ERR AD` zero** and **nothing printed on
the console**. Every error site in MCP does `SIC,X ERR AD` first and
the instruction counter is never zero inside the program, so zero
means *no error site ran at all*.

### The terminator's format came out of the comparison, not a document

printed p.17 line 31's `BZAE` sends a card that is not an IOCD to
`X19`; printed p.19 line 23 asks whether it is an IOD instead; only
line 25 is an error. So **one IOD card ends the scan.**

Its type field is **three columns, left-justified**, and that is
settled by the compare rather than by `C22-6728`. p.17 line 27 loads
48 bits of the type field and line 30 compares all of them against
`X IOCD`; p.19 line 23 is `KF(BU,36),X IOD,12` — 36 bits with an
**offset of twelve**. Reference Manual printed p.65:

> "The contents of the accumulator **left of the specified offset**
> are algebraically compared with the addressed operand. The bits to
> the right of the offset do not participate."

Twelve bits is one card column, so the compare is columns 10-12 and
column 13 is ignored. The two literals agree: `X IOCD` is 48 bits at
001747.60, `X IOD` is 36 at 001750.40, and 001747.60 + 48 = 001750.40.

**Nothing else is punched on it.** p.19 does not read an IOD card's
other fields — after the compare succeeds it goes straight to moving
the unit status table — so punching anything there would invent a
format the pages do not state.

## >>> THE NEXT GATE IS A MISSING INSTRUCTION: TRANSMIT BACKWARD <<<

printed p.19 line 41 is

```
TB,3,0.0($11),0.0($13)    -MOVE BIASED CTS
```

and `StretchExecute.bsv`'s Transmit arm refuses it outright:

```
if (t.backward == 1 || t.swap == 1)
  ind = setOpInvalid(ind);
```

**Reference Manual printed p.30 specifies it** — *"modifier bit 55.
A zero specifies forward transmission; a one specifies backward"* —
so this is an unbuilt arm, not an unknown. `OP` in the boot test's
indicator check is that refusal.

**And it is on the critical path.** Without the move the channel
status table is never relocated, so p.20's walk looks for a console
in a table that was not brought along. The console *is* declared —
`prosa.py` punches a CN card for channel 35, where
`bsv/StretchIO.bsv` puts it — so the halt is MCP being **right about
the machine the model presents**.

Build the backward arm next. `SWAP` is refused by the same line and
is a different datapath; backward alone is what p.19 needs.

### One witness had to be retired

`S MCP` held the descriptor the comm-region move delivered, and
printed p.20 line 11's `SV,$10,S MCP -SET BASE OF MCP IN COM REG`
now runs and overwrites it. The move's extent is still pinned by
`X0`'s count (fifteen, the size `LC` read out of the descriptor) and
by `one_past_is_zero`; the descriptor's arrival by
`mcp_placed_at_dest_first`, which p.15 line 24 delivers to an address
nothing overwrites.

## MCP READS ITS CONFIGURATION IN THE REAL BOOT, AND PRINTS A DIAGNOSIS ON THE CONSOLE, 2026-10-22

```
<CR><RED>000760|0 INCORRECT CARD TYPE <EOM>
```

That is MCP, running on the model, off a tape, having read five IOCD
cards describing this machine, reached a sixth group that is zeros,
and said what is wrong with the deck. **000760 is printed p.19 line
25's own address** — `BZAEZ,X ERROR -NOT AN IOD CARD EITHER` — and it
is the same number `mcp_x_err_ad` checks, because the error routine
prints `X ERR AD` in octal. The register and the console agree. The
message came out of printed pp.7-8's error table, which maps a
failing address to a message and had never been exercised on more
than one entry.

The run before this said "NO IOCD DETECTED".

### The cards' address was not a choice, and the listing said so

printed p.17 line 8 points `$4` at `X IN END` and line 12 tests
fourteen words from there; printed p.13 line 38 reserves what follows
as `SLOTS LEFT FOR IOCD + IODS`. The cards are not read from a
7503 — `C22-6678-1` printed p.29's operator procedure mounts the
master system *tape* and no deck — so they arrive in the PROSA record.

**How they get from the buffer to `X IN END` was already in the
listing**: printed p.15 line 24, `T,$10,X BUFER($9),0.0($8) -PLACE
MCP IN STORAGE`. Put the cards at the *end* of that block and they
land at the end of where MCP is placed — which is what `X IN END`
*is*. So MCP's destination stopped being free:

```
MCP_DEST_WORD = X IN END - MCP_BODY_WORDS
```

### Two fixture lessons, both about inert-looking data

**1. Channel 35 is the console in this model, and the first deck
called it a tape.** MCP processed the card, preset all sixty-four CST
entries to not-available, marked 35 as tape — and then its error
routine found no console and **wrote nothing at all**, where the run
before it, with no cards whatever, had printed a message. *A
configuration that lies about the machine makes MCP correct about the
wrong machine, and the symptom is silence.* The deck now describes
the five channels `bsv/StretchIO.bsv` actually presents.

**2. The comm region's filler was not inert.** printed p.5 line 19 is
`LV,$X1,S YCOCH -GET CONSOLE CHANNEL SLOT CONTENT` and line 20
`BZXVZ,X2AERR -IF CHANNEL NUMBER PRESENT`: a **non-zero** `S YCOCH`
sends the error routine straight to `GONG` on whatever channel it
read instead of walking the exchange. `S YCOCH` is `S MCP` + 6 words,
inside the fifteen the fixture was filling with tagged words — so MCP
believed in a console on a channel made of `0x5A5A`. The region
arrives zeroed now except its descriptor.

### One check was measuring nothing

`mcp_x15_word31` asserted that `$15` still held `LVE`'s result from
printed p.3. printed p.17 lines 18-20 load it with the UST base and
printed p.19 advances it per unit, so the check only measured how far
the run got. It is replaced by `S LR BU`, the communication-region
word printed p.19 line 27 *saves* that pointer into — still zero,
because the run stops two rows earlier, which is itself a statement
about where it stops.

### Next: an IOD card

`C22-6728` printed p.88 lists three control-card types — **IOCD, IOD,
MCPP** — and the deck has only the first kind. printed p.19 line 23's
`KF(BU,36),X IOD,12` is what wants the second, and what the page does
after that compare succeeds is the body of p.19 that has never run.

`strap/iocd.py` is one card builder with two users now; the
testbench's inline version was proved byte-identical for all four of
its modes before it was replaced.

## THE COMM REGION IS BUILT, AND ADDRESS INVALID IS GONE FROM THE BOOT RUN, 2026-10-22

The section below was written as "what the fixture needs next". It
was built the same day, and the thing worth recording is that **the
indicator check's own comment predicted it**:

> AD is READ, not measured... the count is arbitrary and the
> transmit runs until it leaves installed core... **A fixture
> artifact; it goes away when the record is real.**

It went away. `strap/prosa.py` now carries a comm-region descriptor,
printed p.15 line 20's `LC` loads **fifteen** instead of zero, line
21 moves fifteen words and stops, line 24 places MCP's twelve at the
address `LVE` pulled out of the descriptor, and **Address Invalid is
no longer raised anywhere in the run.**

**The size is not a choice.** Every communication-region symbol the
twenty-two transcribed pages name runs from `S MCP` at 002150.00 to
`Y UNCOD` at 002166.00 — 0o17 = **fifteen words**, twenty-two symbols,
mostly two to a word. Fourteen would cut `Y UNCOD` off; sixteen would
be unreferenced.

**And the bit-32 field is not a guess either.** printed p.34 line 29
is `LC,$14,S COMSZ -GET SIZE OF MCP COMMUNIZIATION REGION`, and
`S COMSZ` is **002150.40 — bit 32 of `S MCP`'s word**. After the move
the descriptor *is* `S MCP`'s word, so the field printed p.15 reads
out of the **buffer** and the field printed p.34 reads out of the
**comm region** are the same field, read by the same instruction. The
fixture did not invent the layout; it put the size where the program
already looks.

Four new checks pin it: the region's last word, one past it still
zero, MCP's first and last placed words, and one past *those* still
zero. Two existing expectations gained fixture bits, both derived —
`X0`'s count is now the region's size, and `S ROOF`'s word keeps its
buffer-offset tag in the forty bits `SR` does not write, so a region
that arrived from the wrong place fails with the offset in hand.

Still chosen: where MCP is placed (002200.00, the next round word
above the region), the MCP SIZE of twelve the dictionary already
carried, and the contents of the fourteen words after the descriptor.

### [the derivation, as written before it was built]

## >>> WHAT THE FIXTURE NEEDS NEXT: A COMM REGION, and printed p.15 gives its shape <<<

```
X10   LVS,$9,$12,$11,$14         -COMPUTE NUMBER OF WORDS PRECEEDING
      LVE,$8,X BUFER($9)         - GET (MCP)
X101  LC,$0,X BUFER+.32($9)      -GET SIZE OF COMM REGION
      T,$0,X BUFER($9),S MCP     -MOVE COMM REGION
      T,$10,X BUFER($9),0.0($8)  -PLACE MCP IN STORAGE
```

Buffer offset `$9` — 735, just past the IPL image — is a
**descriptor**: bits 0-23 are the address MCP is to be placed at
(`LVE` loads it into `$8`) and the 18-bit field at bit 32 is the
**size of the comm region** (`LC` loads it into `$0`'s count).

The fixture's filler word sits there instead, and its bits 32-49 are
zero — which Reference Manual printed p.30 says is a direct count of
**2^18**. So the comm-region move copies until it runs off the record
into the zeros above it. That is why four filler words appear at
`S MCP` and everything past them is zero: **the move is not wrong,
the descriptor is missing.**

Build it from those five rows, the way the dictionary was built from
printed p.4 lines 19-27 — derived shape, chosen contents, and say
which is which.

## A SWEEP FOR CLAIMS THE LAST TEN PAGES SUPERSEDED -- eight of them, in six files, 2026-10-22

Transcribing pp.27-36 and replacing the invented equipment table
moved the ground under claims written days earlier. **None of them
was marked, and three sat directly under paragraphs that contradict
them.** This is the failure mode this file already names — *a
correction that retracts the REASON for a claim can leave the claim
standing* — at a larger scale: here the correction was a new page,
not a new argument, and nothing went looking for what it had
invalidated.

Each is now marked where it stands rather than deleted, because what
moved is the interesting part.

### The boot-test section carried three dead paragraphs

`run_tests.sh`'s "MCP'S OWN BOOTSTRAP RUNS" has a list headed *"WHAT
THE MACHINE NOW DOES, in order"*. Underneath it sat three paragraphs
describing earlier states as current:

| claim | measured 2026-10-22 |
|---|---|
| "THIS TAPE HAS NO PROSA — 369 bootstrap words and a mark" | the run prints `host_tape: mounted /tmp/mcp.tape, 462 words`, and four checks verify the moved image |
| "stops at 000124.40, printed p.4 line 32's `CB,0,$`… A HARNESS LIMIT" | stops at **PC 239 = 000167.40 = printed p.6 line 1, `BD,$`**, IBM's own halt |
| "hands off to printed p.15… which is not transcribed" | p.15 and everything through p.36 is transcribed; the hand-off lands on real instructions |

### Two injections had to be re-measured, and one had to change shape

The p.18 fixture injections were recorded with values that the
printed equipment table moved. Re-run against
`StretchMcpP17UnitsTb`:

* **Clear the MULTI flag** (p.35's bit 28, which p.18 line 2 reaches
  as "-TAPE EQUIPMENT TYPE ENTRY") — the CST entry falls back to
  `0x400000800`, not `0x400000600`; the UST pointer/count word loses
  its count.
* **Remove the card's letter from the table** — this now makes the
  *fixture* refuse to build the card (`KeyError: 'TP'` out of
  `equipment_code()`), which is a better failure but tests the
  fixture rather than the machine. Punching `TQ` on the card instead
  reproduces the original result exactly: `0x400000000`, and p.18
  never runs.

**And the PC in those notes was meaningless.** They recorded "PC 961,
the X18 halt" and "PC 182, X ERROR". There is no X18 halt — p.19 is
in `DECKS`, so X18 is a real row — and `X ERROR` is the only planted
exit, which **a passing run also reaches**: the card loop runs out,
the next buffer word matches neither IOCD nor IOD, and p.19 line 25
sends it there. PC 182 is what every mode and every injection
reports. Only the data checks discriminate.

### "Untranscribed" was the wrong word four times, and once it always had been

`gen_mcp_p17_tb.py` said `X ERROR` "is still on an untranscribed page
— printed p.5 line 5". **Printed p.5 has been transcribed since
2026-10-17.** What is true is that it is not in *this testbench's*
`DECKS`, which assembles 17, 18 and 19 — and only that is a reason to
plant a halt. The distinction is worth keeping: one phrase means
"nobody has read this page", the other means "this fixture does not
load it".

### One prediction was satisfied and nobody went back to say so

`verify_mcp_bootstrap_p23.py` predicted that `X VTIME` (001242.02)
and `X VDATE` (001242.70) would turn out to be in the same word
region "on a page nobody has transcribed yet — which is a prediction
that page will have to satisfy". **It is printed p.24, transcribed
the next day, and it satisfies it exactly**, by character count:

```
X VCLOK  (A*)DD(BU,,6),COMD,CLOCK,*   001241.00, 11 chars = 66 bits
X VTIME  (A*)DD(BU,,6),00,00,00,*     001242.02,  9 chars = 54 bits
X VDATE  (A*)DD(BU,,6),00/00/00*      001242.70,  8 chars = 48 bits
```

The heading also said "0o70 BITS PAST", which was a misreading of
`X VDATE`'s own bit offset; the distance is 0o66 bits and it is the
nine characters of `"00,00,00,"`.

### What to do about it

**When a page lands, grep for what it supersedes.** The cheap
searches are the page's own symbol names, the words "untranscribed"
and "nobody has transcribed", and any hexadecimal expectation that a
fixture computes rather than states. Two of the eight above would
have been caught by grepping `0x400000600` alone.

## EVERY PAGE OF MCP's LISTING FROM PRINTED p.2 THROUGH p.36 IS NOW TRANSCRIBED -- and the injection harness was lying, 2026-10-22

`decks/mcp_bootstrap_p36.strap` closes the range `boot_plan.md`'s
M3+ opened as *"$IPLD, printed pp.15-36 — 22 pages, 3 sampled"*.
Twenty-six rows and twenty symbol locations on p.36, bit-exact, and
with it there is no untranscribed page left between p.2 and p.36.

### p.36 is where a dozen earlier derivations get paid

Nothing in the deck states an address except the `SLC` at the top.
Every symbol below is the running total of what precedes it — a
thirty-five character `(IQS*)` message, a seven character `(IQSX)`
one, a hundred-word `DR`, a one-bit flag — and every one of them
matches an address an earlier page had already compiled into an
instruction:

```
X BYPAS  001757.00   printed p.33 line 47
X ON LIN 001761.00   printed p.33 line 21
X OF LIN 001763.00   printed p.33 line 45
X RDR MG 001765.00   printed p.32 line 46
X RDR CR 001771.50   printed p.32 lines 42-43
X MSG    001773.00   printed p.27 line 23
X MSG CR 001774.00   printed p.27 line 24
X BOUND  001777.00   printed p.33 line 51
X MSG BK 002000.00   printed pp.27, 32 and 34
X ON OV  002144.00   printed p.31 line 12
X OF OV  002145.00   printed p.31 line 14
X BYPS   002146.00   printed p.31 line 16
S LR BU  002155.00   printed pp.28 and 30
```

**The assembler gained one thing: a bare `VF`.** Line 31 is
`Y NLST  VF`, no operand at all, printing `000000.00+`. `C22-6531`
printed p.7 ("a null field is always compiled as a zero") and
`C28-6129` printed p.4 ("missing fields are compiled by STRAP-II as
if they contained zeros **and were added at the end of the
statement**") both say so; the second is the sentence that covers an
operand left off entirely rather than written as a bare comma. Both
shapes are now checked — `VF` parses to no fields, `VF,` to one
empty field, and only the page writes the first.

**Three entry modes on one page**: `(A*)` at byte size 6, `(IQS*)`
at 8, and `(IQSX)` — terminated by `X` because the datum `MCPIPL*`
*contains* an asterisk. `C28-6129` printed p.16 makes the terminator
the programmer's choice, and this page is why.

## >>> THE INJECTION HARNESS PRODUCED TWO FALSE "SURVIVED" REPORTS, and both faults fail in the dangerous direction <<<

This project's convention is that every claim gets a measured
injection and that a SURVIVING injection is reported as surviving,
because it says something true. That convention is only as good as
the harness, and on 2026-10-22 the harness lied twice within an
hour. **Both faults make a test look stronger than it is.**

**1. A stale `.pyc`.** A one-character mutation leaves the file the
*same size*, and restoring it can land in the same second, so
CPython's `(mtime, size)` staleness check reuses bytecode compiled
from the **injected** source — or from the *previous* injection's.
A verifier then passes against code that is not on disk. This one
surfaced as a bare `VF` compiling 1 when the source plainly said
`['0']`, and cost a confused half hour before `eval_expr` was traced
and printed `'1'`.

**2. A non-unique anchor.** `if not stmt.fields or not
stmt.fields[0].strip():` occurs **eight times** in `strap_asm.py`,
once per pseudo-operation with a null-field check. A
`str.replace(old, new, 1)` against it patched the *first* — a
different pseudo-operation entirely — so the injection was never
applied and was reported as surviving.

`tests/inject.py` is the hardened harness: it clears `__pycache__`
between steps, runs with `-B` and `PYTHONDONTWRITEBYTECODE`, and
**refuses an anchor that does not occur exactly once**.

**Every injection result already recorded was re-run through it.**
The eight on the parenthetical integer entry mode reproduce exactly,
including I3 and I8, whose survival is genuine and explained where
they are reported; every one of their anchors was confirmed to occur
exactly once. Nothing in the record had to be withdrawn — but
nothing in the record *would have been* withdrawn either, which is
the point.

## THE EQUIPMENT TABLE IS PRINTED, ON p.35, AND THE TESTBENCH NO LONGER INVENTS IT -- pp.34 and 35, 2026-10-22

Seventy-three rows and twenty symbol locations, bit-exact, in
`tests/verify_mcp_bootstrap_p34.py` and `_p35.py`. The bootstrap is
now continuous and bit-exact from printed **p.26 through p.35**.

### X EQP T

`tests/gen_mcp_p17_tb.py` has synthesised the equipment table since
the testbench was written — an invented order with one known code,
and the largest invented object in that file. It is printed p.35,
`X EQP T` at 001752.00, nine entries of `DD(BU,24) + DD(BU,4) +
DD(BU,1)`:

```
entry  column  letter       code  multi   the page's own comment
    0  000000  (none)          0      0   -NO EQUIPMENT
    1  002200  K  (11-2)       1      0   -DISK * DK
    2  002020  N  (11-5)       2      0   -CONSOLE *CN
    3  004040  D  (12-4)       3      0   -READER * RD
    4  001040  U  (0-4)        4      0   -PUNCH *PU
    5  002001  R  (11-9)       5      0   -PRINTER * PR
    6  000000  (none)          0      0   -UNUSED
    7  000000  (none)          0      0   -UNUSED
    8  002004  P  (11-7)      10      1   -TAPE MULTI * TP
```

**The 24-bit field is a card column, and two independently
transcribed documents agree about all six.** The verifier compares
each entry against `strap/cards.py`'s `column_bits`, which came from
`C22-6678-1` printed p.56's Appendix F — a different manual,
transcribed for a different reason. K is 11-2, N is 11-5, D is 12-4,
U is 0-4, R is 11-9, P is 11-7, in both.

**The second letter alone identifies the unit.** This repository had
already noticed that `C22-6728` p.88's CN/DK/PR/PU/TP/RD have second
letters N, K, R, U, P, D, all distinct. *This table is why that
matters*: MCP never looks at the first letter.

**Two codes were already known from the programs that use them, and
both agree** — console = 2 (printed p.20 line 14), printer = 5
(printed p.25 line 17). Two derivations twenty pages apart, checked
against the table they came from.

### Two claims in the testbench were corrected, and one was vindicated

* **Vindicated.** The order had been argued from printed p.19 line
  4's `KCI,$1,6.0` / `BZXH`: the count is 10 − k after matching the
  k-th entry, the single-unit arm is taken when k >= 4, therefore
  "entries 1-3 are the DISK OR CONSOL ones". The printed first three
  are **NO EQUIPMENT, DK, CN**, and the fourth is RD, the first
  single-unit device. The derivation was right; it could not see the
  zero entry at the head.
* **Corrected.** The 29th bit was called "IS TAPE", argued from
  `C22-6728` p.90's Figure 44 and p.18 line 2's comment. The
  **polarity was right**; the name was not. p.35 comments every zero
  entry `-SINGLE UNIT CHANNEL` and the single set entry `-MULTI UNIT
  CHANNEL`. The field is the channel's unit multiplicity; tape is
  the only multi-unit equipment, which is why no behaviour could
  distinguish the two readings.

All four p.17 testbench modes (none / `units` / `units8` / `disk`)
pass with the printed table.

### The oracle learned that a printed width is not a printed digit count

`listing_oracle.render` guessed a DD's width from how many octal
digits the listing printed (3 → 8 bits, 6 → 18, 11 → 32, 22 → 64).
**Three octal digits is 7, 8 or 9 bits**, and p.35 puts `DD(BU,24)`,
`DD(BU,4)` and `DD(BU,1)` adjacent, so a guess would have silently
read the next datum's bits. `render` now takes an explicit `width`
and `check_rows` accepts a fourth element per row; every row on p.35
passes one. The old guesses stay for the callers that predate this.

### printed p.34

Every row, forty-one of them. **The first input-output instructions
in the initialization** — everything since p.17 had been
table-walking:

```
W(SEOP),0.0($15),X MSG W      000000.00 8F 001724.13 00
LOC(SEOP),0.0($15),0.0        000000.00 8F 000000.17 00
```

and a **third `(.25)1`**, on line 19, one commit after the mode was
built. The page also writes register fields both ways — `LC,$1,…`
and `SV,1,…`, `LV,$15,…` and `LX,14,…` — which settles that the `$`
is the programmer's hand, the same answer printed p.32's `TI,$10`
gave.

**The next page is printed p.36**, whose first printed row is a
`CNOP` at **001756.40** — p.35's last datum is a one-bit `DD` at
001756.04, so the counter stands at 001756.05 and the CNOP rounds it
up. p.36's `X BYPAS` (001757.00) and `X ON LIN` (001761.00) are two
more addresses printed p.33 compiled before that page was opened.

## PRINTED pp.32 AND 33 ARE TRANSCRIBED -- and p.32 measures a page transcribed five pages ago, 2026-10-22

Eighty-one rows and twenty-four symbol locations, bit-exact, in
`tests/verify_mcp_bootstrap_p32.py` and `_p33.py`. **No assembler
work for either**, which makes it five pages in six.

**p.32** finishes the message-deletion passes and builds the message
that tells the operator which channel the spool reader is on.

**THE REAL CHECK IS THAT IT REACHES BACK.** Lines 24, 44 and 48 all
address `X24 A2+.32`. `X24A2` is printed **p.27** line 21,
transcribed from that page's own location column three commits ago
as 001473.00; these rows print 001473.40. Line 22's `B,X33 1A`
reaches back one page to printed p.31 line 35. Neither address was
read off p.32 — both are `SYN`'d from the pages that define them —
so the rows *measure* the earlier transcriptions instead of
repeating them.

**`TI,$10` is a COUNT, not a register**, and the page proves it
against its own binary: line 46 is `TI,$10,X RDR MG,0.0($14)`, the
Reference Manual's printed p.30 says an immediate-count transmit
takes "the full word count ... by instruction bits 51-54", and the
printed second half word `000000.24 AE` has `1010` in bits 19-22.
Ten. Contrast printed p.29 line 38's `T,$11`, which **is** a
register — same `$`, same evidence, opposite answer, because the
opcode nibble differs (A immediate, 2 direct).

**p.33** unassigns the spool reader in offline overlapped mode and
primes the System Command routine three ways. Every row on the page,
forty-five of them.

* **Eleven null-operation rows** — `, S COMD`, `, 4.0`, `, 0.0($14)`
  — the parameter list each `BD,0.0($12)` branches into. The form
  the assembler gained for printed p.25; `C28-6129` printed p.6
  specifies it and all eleven print exactly that.
* **X36 is an address three earlier pages already compiled**: p.30
  line 24, p.31 line 24 and p.32 line 51 all branch to it, all
  transcribed first, all producing 001661.74, and this page opens at
  001661.40.

### One open grammar question, parked rather than guessed

p.33 line 33 is `BZB1,X VSWCH.19,X37 4A` and the deck writes
`XVSWCH+.19`. The printed address 001672.23 is `XVSWCH` (001672.00)
plus nineteen bits, so for **this row** the two spellings are the
same address, and that is measured. What is *not* settled is whether
STRAP-II accepts `SYMBOL.bits` as an implicit sum at all:
`C28-6129` printed p.8 defines a STRAP bit address as "two integers
separated by a period", and every symbolic offset in that manual
uses a `+` (`SAM+4`, printed p.30). **One row is not a grammar.** If
a later page writes it again, read Section II before touching the
expression parser.

**The MCP bootstrap is now continuous and bit-exact from printed
p.26 through p.33.** The next page is printed p.34, whose first
row is at **001713.40** -- p.33's last instruction is a full-word
BRANCH ON BIT at 001712.40, so the two meet exactly.

## PRINTED p.31 IS TRANSCRIBED -- every row on the page, and the assembler found a second real C, 2026-10-22

Thirty-five rows and thirteen symbol locations, bit-exact, in
`tests/verify_mcp_bootstrap_p31.py`. Reading the installation's
operating mode off the MCPP card, and the bypass-mode walk that
turns six status bits off along the spool tape's UAT/CST/UST chain.

**No assembler work, for the fourth page in five.** The one form the
page introduces, PROGRESSIVE INDEXING, has been in the assembler
since the I-Box decks:

```
line 6  CT0000(V+I)(BU,8),+1.44($4)  -> 000001.54 84 110000.01 70
line 7  L(V+I)(BU,48),.48($4)        -> 000000.60 84 160000.20 50
```

C28-6129 printed p.4 writes the format as `OP1(OP2)(dds), A24(I),
OF7(I')`, so the instruction that reads a field of the card also
advances `$4` past it and the card is walked with no separate
increment.

**A second real `C`, and again the assembler found it.** Line 24's
trailing byte was transcribed `00` off the 600 dpi render; the
assembler compiled `0C`, the 900 dpi render says `0C`, and the
structure says so without any render: `BZB1` differs from `BZB`
exactly in bits 28-31, where "and set the bit to one" lives, and
line 32's plain `BZB` prints `00` in the same column eight rows
later. Fourth row in two days where the glyph decided nothing and
the field decided it — see `listing_typography.md` §13b.

Reached by branch from p.30 twice (`BZB,X LR IN+.31,X 32` and
`BAH,X32` both compile X32 = 001601.00) and contiguous with it as
well, since p.30's last data byte ends at 001600.70.

**The MCP bootstrap is now continuous and bit-exact from printed
p.26 through p.31.** The next page is printed p.32 at 001632.40.

## PRINTED pp.27, 28 AND 29 ARE TRANSCRIBED -- three pages, no assembler work, and a glyph rule that needed a counter-instance, 2026-10-22

Eighty-four printed rows and thirty-three symbol locations, all
bit-exact, in `tests/verify_mcp_bootstrap_p27.py`, `_p28.py` and
`_p29.py`. The bootstrap's MCP-relocation phase is now continuous
from p.26's "TO DECODE" through p.29's last TRANSMIT.

**THE ASSEMBLER NEEDED NOTHING FOR ANY OF THE THREE.** The nine
pages before them each wanted a pseudo-operation, a field width or
an encoding; these three wanted none. The two forms that looked new
were already right:

* **p.27's `XW` with a negative value AND a flag digit**, which the
  corpus had not shown together. `XW,-1,0,0,4` prints
  `000000.01- 100` and `XW,-1.0,0,0,6` prints `000001.00- 110` --
  the same magnitude written two ways, six places apart in the
  value field, with the flag digit untouched beside the sign.
* **p.28's VFL arithmetic**, the first in the MCP:
  `L(BU,18),S MARK,46`, `-(BU,18),S LR BU,46`, `LC,$11,$R`. Twenty-
  nine rows, all right the first time.

### The half-word layout is PRINTED, and eleven addresses rest on it

p.28 names eleven external symbols and the page never gives their
addresses -- they are decoded out of the printed half words. The
rule that makes that possible had been reverse-engineered from
matching rows; it is **printed in the Reference Manual on printed
p.19 (PDF 22)**, a page the manual's own index does not point at,
reached from the CONTENTS line "Index Format ... 19":

> Figure 6's second diagram:  `| ADDRESS | J | OP. | I |`
>
> "A half word operand is implied by most branch, index
> modification, and transmit operations. This group of operations
> has an address part of **19 bits**. The 18 high-order bits address
> full words. **The low-order bit addresses the first or second half
> of the full word.**"

So bit 18 is the half-word selector, `J` follows at 19-22, and the
operation part runs to bit 27. `LC,$12,S MAX RN` prints `.70` =
`111000`: half 1, register `1100` = `$12` -- which puts `S MAX RN`
at 002155.40 and not 002155.00.

The same sentence settles the VFL rows **by exclusion**: integer
arithmetic and connectives "ha[ve] an address part of 24 bits", so
`L(BU,18),S MARK,46` carries no J and no half-selector and its
printed 002162.40 is a plain bit address.

### Four cross-page checks, in both directions

p.28 was transcribed before p.29 was opened, and three of its branch
encodings fixed three addresses that p.29's location column then
stated outright. One branch on p.29 closes the loop backwards:

```
p.28 l.51  BXVZ,X30 4      001537.71 42   ->  X30 4  001537.40
p.28 l.48  BAL,X31         001547.36 42   ->  X31    001547.00
p.28 l.43  CBZ+,$12,X31 2  001551.71 4A   ->  X31 2  001551.40
p.29 l.35  B,X29           001525.50 00   ->  X29    001525.40
```

All four were decoded with the p.19 rule, so the four agreements are
also four tests of the rule.

### §13 needed a counter-instance, and the assembler supplied it

`docs/listing_typography.md` §13 -- "a `C` in this scan is a digit
zero" -- had four instances behind it and was about to acquire a
fifth and sixth from p.27 lines 5 and 36, which print `C1` for `01`.
**Lines 23 and 24 of the same page print `AC`, and the `C` is
real**: it is the index register `$12` of `0.0($12)`. Line 21, the
`TI` two rows above with no index, prints `A0`.

The first draft of the verifier read both `AC` rows as `A0` and the
assembler refused them. The rule is therefore **not** "a `C` in a
trailing byte is a zero" but:

> an octal column cannot hold a `C`; an index or operation field
> can. The glyph is evidence only *after* the field it sits in has
> been decoded.

Written up as §13b. A transcription habit that has been right four
times is exactly the one that stops being checked.

### The row that looked like a blocker and was not

p.29 line 38 is `T,$11,0.0($13),0.0($14)` -- a direct-count TRANSMIT
whose count register is written with a `$`. The assembler refused
it, and the right answer was **not** to teach it the spelling: every
TRANSMIT in `decks/` already writes the register as a bare digit
with the listing's own spelling in a comment beside it (see
`decks/ax4b_1246_memories.strap`'s `T, 1, I46D4, $X3  ! listing
"T,$X1,I46D4,$X3"`). Adding `$n` for one page would have left the
corpus with two spellings for one field and no record of which page
used which. **If `$n` is ever wanted, it is a migrate-everything
change on its own, not folded into a page.**

What the row did produce is a source. Reference Manual **printed
p.30 (PDF 33)**, "Data Transmission" -- a section the index does not
list either -- states the whole instruction in prose: modifier bits
55 (backward), 56 (immediate count) and 57 (bidirectional), which
this project had **only from the pocket card**; and

> "In direct count operations, the field J, bits 51-54, **specifies
> an index register**. The count field, bits 28-45, of the index
> word in this register is used as a full word count. A count field
> of zero is interpreted as 2^18... A zero J field refers to
> location 16, X0."
>
> "In immediate count operations, the full word count is specified
> by instruction bits 51-54. **A zero count field indicates the
> maximum count of 16 full words.**"

**`docs/boot_plan.md` had already been citing this page** for one
clause -- *"never valid"* -- while `docs/archival_inventory.md` went
on calling the layout card-only. Fifth instance of *a document you
have cited is not a document you have read*, and the first where the
citation was this project's own.

Two of its rules are unimplemented and now have numbers attached: an
immediate count of 0 means **sixteen**, a direct count of 0 means
**2^18**, and the Bluespec Transmit arm moves exactly one word.

### printed p.30 IS TRANSCRIBED TOO, and it needed the one feature this project had refused

Twenty-three rows and nine symbol locations, bit-exact, in
`tests/verify_mcp_bootstrap_p30.py`. "MCP TYPE REQUEST REPORT" and
"MCP MODE REPORT". It starts at 001553.40, picking up from p.29's
last full word, and wanted `CW`, `CNOP` and alphabetic
`DD(BU,64,8)`, all of which the assembler had. **The one thing it
did not have was line 27's syntax:**

```
X MO CW   CW,X ZEROS,3,X MO CW1(.25)1   ->  001037.00+ 100 000003 001574
```

The flag group prints `100`, the chain flag, and the statement
carries no `CW(CCR)` secondary -- so `(.25)1` is setting bit 25
directly. `C28-6129` printed p.14, the CW section, documents only
the eight secondary mnemonics and says nothing about it.

**IT IS PRINTED, IN FULL, AND IT WAS FOUND BEFORE ANYTHING WAS
WRITTEN.** `C28-6129` Section II, **printed pp.25-26 (PDF 29-30)**,
heading "Field Entry Mode":

> "A final STRAP entry mode that is used as a field entry mode is
> the **parenthetical integer entry mode**. This mode permits any
> integer or pattern of bits to be stored in any bit position of an
> instruction or pseudo operation that produces binary output. The
> general format for this entry mode is:
>
>       (.n)A(n+1)
>
> The symbol `.n` represents the **bit address of the rightmost bit
> of the field** into which the integer or bit pattern is to be
> entered. The integer A(n+1) is formed as an unsigned field, **n+1
> bits in length** (because of the 7030 custom of addressing bits
> starting with zero), and inserted into the leftmost n+1 bits of
> the addressed instruction or data entry field by means of a
> **logical OR** type operation. Logical OR is used so that the
> parenthetical entry may be combined with the existing contents of
> the particular field addressed or with other parenthetical
> entries."

and the rules that go with it, all on those two pages:

* **Where `.n` counts from.** *"In the case of an instruction, the
  position of the entry is determined by counting bits from the
  beginning of the instruction, starting with bit zero, no matter in
  which subfield of the instruction the integer entry may be
  written."* In a `DD`'s D field it is relative to **that field**
  instead, counted from the previous comma forward.
* **Where it may be written.** *"The parenthetical entry must follow
  all other information in the field in which it does appear."*
  `+(BU), DATA(.23)4, 20` and `+(BU), DATA, 20(.23)4` compile the
  same word.
* **Bounds.** `.n` must be <= 31 in a half-word instruction and <=
  63 in a full word; at most 24 significant bits convert; the
  expression is evaluated **modulo 2^(n+1)** and is unsigned, so a
  negative is compiled as its complement re 2^(n+1).
* **Not everywhere.** *"This entry mode must appear in a statement
  that compiles space in storage. Therefore, this mode cannot be
  used in pseudo operations that give instructions to the compiler
  but result in no binary output (SCL, DDI, END, etc.)."*
* **Radix inside the parentheses.** `(.32, 8)` or `(8, .32)` both
  mean "octal, rightmost bit 32"; *"all numbers that appear within
  parentheses are interpreted by STRAP as decimal numbers"* unless a
  radix is given there or is already in force.
* **Consecutive entries are legal and OR together**, which is the
  whole point of using OR -- `L(BU), INFO(.50,8)17-JOE+(10)4203(4,
  .22)-33303(.60)1030` is the manual's own example.

So p.30 line 27's `X MO CW1(.25)1` ORs a 1 into bit 25 of the full
word the `CW` compiles -- the chain flag -- which is exactly the
`100` the listing prints, and it is the general mechanism the
programmer reached for instead of writing `CW(CCR)`.

**This is a real assembler feature and it is specified, not
guessed.** It is also the first construct in this corpus that
modifies a word *after* the field that names it, so it cannot be
folded into expression evaluation: it needs a post-pass over the
emitted half word or full word. Build it with the bounds and the
modulo rule, not just the common case.

**AND IT IS NOT NEW -- IT WAS DEFERRED ONCE, CORRECTLY.**
`decks/mcp_bootstrap_p7_p8.strap` carries "substitution (a)":

> LINE 34's `CW,X ZEROS,3,X MSG CW(.25)1` IS WRITTEN `CW(CCR), X
> ZEROS,3,X MSG CW`. The `(.25)1` is a bit designation -- set bit 25
> of the generated word to one... **This assembler does not implement
> bit designations, and inventing their general semantics from one
> row is what AGENTS.md rule 4 forbids.**

That was the right call and it bought the project four months of not
having a guessed feature. The same construct now has a printed
general specification, so p.8 line 34 can be made VERBATIM and the
substitution retired. **Retire it in the same change that builds the
feature**, so the one row that was worked around becomes the second
witness for the thing that replaced the workaround.

Note what the two rows have in common: both are `CW` with
`(.25)1`, twenty-two printed pages apart, both setting the chain
flag, and `CW(CCR)` sets the identical three bits. So the MCP's
programmer had both spellings and used both.

**BUILT THE SAME DAY, AND BOTH ROWS ARE VERBATIM NOW.**
`decks/parenthetical_entry.strap` and
`tests/verify_parenthetical_entry.py` carry the mode;
`decks/mcp_bootstrap_p7_p8.strap`'s substitution (a) is retired, and
the equality it *asserted* -- that `CW(CCR),…` and `CW,…(.25)1`
compile the same word -- is check C6.

**Measured before the splitter was switched on:** its regular
expression was run over every statement field of every deck,
**24,073 fields, zero matches**, so the mode cannot reach a row that
was not written for it.

**Eight injections, and the two that SURVIVED are the interesting
ones:**

* **I3, deleting the modulo-2^(n+1) mask, survives** -- and that is
  not a hole in the test. `Image.or_into` extracts each chunk with
  `(value >> k) & ((1 << take) - 1)`, so the truncation is
  structural; the explicit mask is a *second copy* of it. It is kept
  because it is where the manual's sentence belongs, but it is
  documentation, not a mechanism, and no test can tell the two
  apart. Say so rather than counting it as covered.
* **I8, not reversing the entries back into source order, survives
  and must** -- OR is commutative, which is exactly the property the
  manual chose OR for. `reverse()` only decides which entry an error
  message names first.

The other six are caught; `run_tests.sh` has each one's measured
failure. Two of them (I5, I7) are caught by `Image.deposit`'s
overlap guard rather than by a check -- a misplaced entry lands on
the *next* statement's half word -- which is worth knowing, because
it means the guard is doing double duty here.

**A vacuous check caught in the first draft:** C4 was written
`20(.23)4(.21)1`, two entries into the SAME bit (4 = 100 puts a one
at bit 21), so it would have passed with either entry dropped. It is
`(.20)1` now, and the deck says why.

## PRINTED p.26 IS TRANSCRIBED -- and a too-wide field was only visible where a narrower one followed, 2026-10-22

Twenty-six rows and ten symbol locations, bit-exact. "TO DECODE":
each broken-out IOD and REEL table is handed to the decode routine
with a four-word linkage parameter block.

**The assembler gained `CF` and `RF`**, and this time the manual was
read *before* anything was written. C22-6531 printed p.19 gives
`CF` "COUNT FIELD" as an 18-bit integer in positions 0-17, `RF` as
the same with Refill substituted, and printed p.18 gives `VF` as a
24-bit-plus-sign quantity in positions 0-24. The same page states the
widths again as data descriptions: `XW` `(BU)`, `VF` `(B,25)`,
`CF`/`RF` `(BU,18)`.

**>>> AND THAT CORRECTED `VF`'s DEPOSIT, WHICH HAD BEEN WRONG SINCE
IT WAS WRITTEN. <<<** `VF` wrote a whole half word — claiming bits
25-31 it does not own. **Nothing ever noticed**, because every
statement that can follow a `VF` rounds up to a half word anyway. A
`CF` after a `VF` is the first case in the corpus where the
difference is visible, and it showed as an **overlap**, not as a
wrong value.

> **A field that is too wide is only detectable where something
> narrower follows it.**

**AND THE SIZE QUESTION WENT THE OTHER WAY, which is the better
half of the story.** The manual says the counter "stands at bit 25
at the end of the operation", so I made `statement_size` return 25 —
and **the full suite caught it**: pp.7-8 line 31 is
`X E DD K SYN,$-X ERR DD`, measuring a table built entirely of `VF`s,
and the listing prints `000047.00` — thirty-nine words exactly, on a
half-word boundary. At bit 25 `$` would be `000046.71`, and line 32's
`XW`, which uses `X E DD K+1.0` as its **count**, printed `000047`
where the listing prints `000050`.

So *"stands at bit 25"* describes where the counter sits **for a
following field** and is **not what `$` reports**: a `SYN` sees the
rounded location. Nothing else in the corpus distinguishes the two —
p.26 can't, since its `CF` sits on a boundary either way — so the
manual and the listing are both satisfied by a **half-word size with
a 25-bit deposit**.

**The pattern worth keeping**: the manual's sentence was about one
thing (where a following field starts) and I applied it to another
(what `$` reads). The listing is the oracle for which of those a
1960 assembler actually did, and a page transcribed weeks ago was
the thing that knew.

## PRINTED p.25 IS TRANSCRIBED -- the block was a four-bit constant, and it was printed, 2026-10-22

Thirty-two rows and fourteen symbol locations, bit-exact. The page
was blocked for one construct, written up here as *"two rows is not
enough to fix a four-bit constant"* — which was the right call on the
evidence then, and wrong about the evidence available.

**>>> THE PRINTER'S EQUIPMENT CODE IS OCTAL 5. <<<** Line 17 is
`LFI(BU,4),(8)5`, "ENTER PRINTER EQUIPMENT CODE", compared against
`.52($10)` — the `SEQUIP` field. With p.20's console = 2, **two** of
`X EQP T`'s values are now known from the programs that use them.

### The null operation field, and where both halves of it are printed

Lines 42-43 are `,0.0($7)` and `,2.0($7)` — statements with **no
operation**, written as nothing but the comma.

**The syntax** — `C22-6531` printed p.7: *"A major field may be null,
even though other non-null fields follow it. Such is the case if
nothing but the comma denoting the field termination is written"*,
and *"a null field is always compiled as a zero."*

**The encoding** — `22-6530-2` printed p.163, "Instruction Formats",
draws INTEGER, CONNECTIVE, INPUT-OUTPUT, TRANSMIT, SIC BRANCH and
BRANCH ON BIT with an **identical first half**:

```
ADDRESS (0-23) │ 1000 (24-27) │ I (28-31) │ …rest from bit 32
```

Six diagrams, one shape. The `1000` is a **literal of the full-word
forms** — not a VFL marker, not the operation's own bits. No
half-word format on that page has it, because they pack their
operation into bits 18/19-31 instead. So a null operation lays down
exactly the half the programmer wrote and nothing after bit 31.

**AND THE PAGE CORROBORATES IT FROM INSIDE ITSELF.** Line 51's
`BB,2.04($7),X22 2` is a *real* branch on bit — a full-word format —
and its first half prints `000002.04 87`: same address shape, same
`1000`, same index 7, from an instruction that is not a null
operation at all.

### The lesson, which is the one this file keeps writing down

The constant was never a fit waiting for more instances. **It was
printed, in six diagrams, in a file `docs/` has had all along** — the
Reference Manual's own appendix, which the back-matter sweep had
already catalogued as "bit-layout diagram of all 13 instruction
formats with bit-position rulers" without anyone opening it for this.

"A document you have cited is not a document you have read" has now
been paid for four times in two days: `C22-6678-1`'s Appendix F, the
opcode list at `22-6530-2` pp.168-169, `C22-6531`'s Appendix A
opening page, and this. **The back-matter map in this file exists
precisely so the fifth time is cheap — use it before concluding that
evidence is unavailable.**

**A SIXTH, 2026-10-22, AND IT IS A NEW SHAPE: HALF-READ, NOT
UNREAD.** `docs/exchange_and_io.md` quotes Reference Manual printed
p.150 at length — the console's four CONTROL codes, the gong's
timing, the pluggable-exit jack — and introduces it as *"the
console's whole specification"*. The LEFT COLUMN of that page says
what a console READ does: *"terminated when the three words scanned
from the switches have been sent to the exchange"*, and the ENTER key
"generates a channel-signal indication". Both are things MCP's
printed pp.22-23 use and the model does not have. The quotation was
right, the page number was right, and the half of the page nobody
needed yet went unread for a month. **The corollary: a page is read
when you know what is on all of it, not when you have the sentence
you came for.**

**AND IT HAPPENED TWICE ON THE SAME DAY, IN THE SAME FILE.** §3.2 of
that document transcribes Figure 35 from printed p.107 field by
field, and then sources its three "properties the model does not
honour" from printed p.123. p.107's own prose beside the figure says
*"Inside the exchange, however, these same bit positions are used to
retain the status bits which indicate the status of the unit"* —
which is the sentence that turns `StretchCore.bsv`'s refill bug from
an inference into a fact, and it sat eight lines from a figure this
project had already read twice. **A figure is not a page either.**

## PRINTED p.24 IS TRANSCRIBED -- and it settles p.23's prediction, 2026-10-21

Forty-four rows and nineteen symbol locations, all bit-exact on the
first run.

**>>> THE PREDICTION HOLDS. <<<** p.22 line 35 loads an immediate
`X VTIME` = `001242.02` and p.23 line 15 loads `X VDATE` =
`001242.70`, so the two constants had to sit `0o70` bits apart in one
word region. Lines 50 and 51 **define** them, at `001242.02` and
`001242.70` exactly — and the prediction was committed before this
page was opened.

**FOUR MORE FORWARD REFERENCES LAND**: `X VZER` at `001204.40`,
`X VZER 1` at `001207.00`, `X VNOTM` at `001211.40` and `X VTDER` at
`001225.40` were all SYN'd on pp.22-23 from those pages' own binary
output, and this page defines every one at the address read off an
instruction.

**THE ASSEMBLER GAINED `DRZ`.** Line 52 is `X VSTOR DRZ(BU),100`,
printing `000144.00` — `0o144` is a hundred, so it reserves a hundred
**words** and the printed value is the size, as `DR`'s is. The pair
`DR`/`DRZ` is "Data Reservation, with and without zeroing"; only
`DR` existed here. The `Z` is not cosmetic: a `DR` region is *absent*
from the image `strap/mcp_image.py` builds, a `DRZ` region is a
hundred zero words.

**AND THE LABEL FAMILY IS `X IO n`, NOT `X IC n` — §13a again.** This
page's own name column prints `X IC 3`, `X IC 4`, `X IC 5` and then
`X IO 6` for four labels of **one** family, and its operands read
`X IO 1` and `X IO6` at 600 dpi. A column that disagrees with itself
about a glyph is naming the unstable one. pp.21-23's decks were
renamed to match; the bits were never affected, only the names, and
all three still pass.

**AND THE OPCODE RATCHET FIRED**, which is the first time this
session that a page changed the coverage picture rather than just
adding rows. `CV` and `LTRCV` were in the audit's `UNIMPLEMENTED`
set — "expected to be *unused*" — and p.24's time conversion uses
both:

```
CV(BU),$L,16              -CONVERT HOURS TO DECIMAL
LTRCV(BU,6),$RM+.54       - CONVERT MINUTES TO DECIMAL
LTRCV(BU,6),0.24($1)      -CONVERT SECONDS
```

They moved to `ENCODING_ONLY`, the same move `KF` and `LCV` made when
p.17 first used them. **The model still refuses both** — they reach
`setOpInvalid` — so building them is what would let the time
conversion actually run. That is now the most concrete "make a
transcribed page executable" item on the list.

**LINE 44's CNOP IS IN THE CHECKED TABLE** and the page's other three
are not: it is the one that had to **pad**, and it prints
`000000.30 00`, a NOP half word. That is the difference between a
`CNOP` that rounds and a `CNOP` already rounded, visible in the
listing itself.

## PRINTED p.23 IS TRANSCRIBED -- and the 19-bit branch field cost something, 2026-10-21

Fifty-four rows, all bit-exact. The IPL **date** constant's
validation — the same shape p.22 used for the time — and then the
**I/O status report loop**.

**THE MONTH AND DAY LIMITS ARE PRINTED IN HEXADECIMAL**, `(16)13` and
`(16)32`, and that is not an arbitrary radix. The characters being
compared are a **pair of BCD digits packed one per nibble**, so
`0x13` *is* the digit pair 1,3 and `0x32` *is* 3,2. The comparison is
on the digits, and hexadecimal is the only radix in which the
constant looks like the number it bounds. p.22 does the same with
`(16)24` and `(16)60`.

**FOUR PAGES NOW SHARE `X LR IN`**: p.21 reserved it with
`DR(BU),(3)`, p.22 read the operator's reply into it, and this page
reads the date half and then the channel number out of it at `+1.24`.

**>>> THREE FORWARD REFERENCES WERE GUESSED `.40` AND ARE `.00`, and
the verifier caught all three on the first run. <<<** The
branch-address field is **nineteen bits** and bit 18 — the top bit of
the printed `.bb` group — is the half-word selector: `001207.36` has
it **clear** and means the *left* half of `001207`, while `001225.76`
has it **set** and means the right half of `001225`. p.21 documented
the field; this is the page where not actually using it cost
something. **Defaulting an unknown forward reference to `.40` is a
coin flip — read the bit.**

**AND A PREDICTION FOR A PAGE NOT YET READ**: p.22 line 35's
immediate is `X VTIME` = `001242.02` and line 15 here is `X VDATE` =
`001242.70`, so the two constants sit `0o70` bits apart in one word
region. Whatever page defines them has to put them there.

## PRINTED p.22 IS TRANSCRIBED -- and it found an assembler gap, 2026-10-21

Fifty rows, all bit-exact. **"OPERATOR STATUS REPORT FOR IO"**: it
*reads* the IPL options the operator typed and validates them — six
characters of IPL time, each tested for being a valid digit and then
in **pairs** against `(16)24` and `(16)60`, hours under twenty-four
and minutes and seconds under sixty, then the same digit validation
over the IPL date.

**THREE PAGES SHARE ONE BUFFER.** Line 5 reads into `X LR IN`, which
p.21 line 26 **reserved** with `DR(BU),(3)`, using `X D CW 2`, which
p.21 line 31 **built**. And p.21 line 24's `B,XIC` is what branches
here: `X IC` at `001052.00` was recovered from that branch's own
encoding before this page was opened.

**>>> THE PAGE FOUND AN ASSEMBLER GAP. <<<** Lines 20, 23 and 26 are
`KFI(BU,8),(16)24` and `KFI(BU,8),(16)60` — a **radix-sixteen literal
in an immediate operand**. `tokenize_expr` capped the `(R)` radix at
**ten**, so the page would not assemble at all, while
`parse_dd_value` had always accepted any radix: the same literal was
legal as *data* and illegal as an *operand*. The cap is now sixteen,
and the digits A-F are matched only after a prefix has introduced
them, so a bare identifier can never be read as hexadecimal.

**What makes the fix evidence rather than a guess**: the two rows
print `110000.00 80 410000.23 10` and `300000.00 80 410000.23 10`,
whose address fields are `0x24` and `0x60` left-justified in the
24-bit field. Had the prefix meant anything else those words would
not match — and 271 other decks assemble unchanged, which is the
other half of the check.

**AND THE C/D CONFUSION BIT AGAIN**, harmlessly this time because the
two columns were read at different resolutions. Every `ST(BU,4)(V+I)`
row ends `D0`; at 150 dpi six of them looked like `C0`. The statement
column was read at 600 dpi and the code column at 900, so a misread
in one could not cancel a misread in the other — which is the reason
for reading them separately rather than from one render.

## PRINTED p.21 IS TRANSCRIBED -- the console date message, 2026-10-21

Twenty-eight rows plus fourteen symbol locations, all bit-exact on
the first run. **"MCP SOURCE TAPE VERIFICATION"**: it prints the IPL
tape's date on the console so the operator can see which system he
has just loaded. It takes the console channel out of the
communication region — which p.20 put there, so the two pages join.

**THE MESSAGE IS PATCHED IN PLACE**, which is why the digits are
*added* rather than stored. Lines 37-38 are
`(IQS*)DD(BU,64,8),00 MONTH *` and `,00 DAY  *` — the text carries
zeros as **placeholders**, and lines 17-20 `M+MG` four-bit digits
into them. That is also why the leading-zero suppression **clears** a
digit instead of skipping it: a cleared placeholder prints as a
blank. pp.9-12 use the same trick for an error address.

**THREE ROW KINDS ARE DELIBERATELY ABSENT from the checked table**,
each for a reason that is itself a fact about the listing: the
`(IQS*)DD` rows print *nothing* in the binary column (so no character
code is checked because none is printed — their text *lengths* are
pinned instead by the locations of everything after them); the `DR`
rows print the reserved **size**, not a stored word; and line 42's
`SYN` prints its **value**, a symbol definition rather than storage.

**A CROSS-PAGE CONFIRMATION FELL OUT.**
`decks/mcp_bootstrap_p7_p8.strap` already carried
`XZEROS SYN,(8)1037.00` with the comment *'printed p.21 line 28,
"X ZEROS DR(BU),(3)"'* — a forward reference written when p.21 was
unread. p.21 defines `X ZEROS` at `001037.00`.

**AND THE BRANCH-ADDRESS FIELD IS NINETEEN BITS, WHICH THE PRINTED
FORM HIDES.** Line 23's output is `000057.50 00`. The `.50` group is
instruction bits 18-23 and **bit 18 is the half-word selector**, so
`101000` means word `000057`, *right* half — location `000057.40`.
Read as a plain bit offset, `0o50` is 40 decimal, which is not a
half-word boundary at all and would have looked like a misprint.
Worth remembering for every branch row on every future page.

## PRINTED p.20 IS TRANSCRIBED -- and it names an equipment code, 2026-10-21

Seventeen rows, all bit-exact on the first run. Short: the
communication-region entries (`S X CHAN`, `S MCP`, `S Y CO CH`) and
the **search for the console channel in the CST**.

**>>> THE CONSOLE'S EQUIPMENT CODE IS OCTAL 2. <<<** Line 14 is
`LFI(BU,4),(8)2`, commented "-ENTER CONSOLE EQUIPMENT CODE", and line
15 compares that four-bit value against `.52($10)`. `X EQP T` — which
maps a card's equipment letter to a four-bit code — is on a page
nobody has transcribed, and this is the **first of its values to be
known**, from the program that uses it rather than from a table.
`gen_mcp_p17_tb.py` now carries it as the one real code among
invented ones.

**AND IT CONFIRMS `SEQUIP` FROM A THIRD PAGE.** `C22-6728` printed
p.246 names bits 52-55 `SEQUIP`; p.17 line 54 *writes* four bits at
`.52`; this page *reads* four bits at `.52` and calls it "the
equipment field". Three independent sources, one field.

**`S MCP` IS CROSS-CHECKED BETWEEN TWO PAGES**: line 11 puts it at
`002150.00`, and p.19 line 43's `LV,$10,SMCP` assembles to
`002150.24 30` — the same address recovered from a different page's
binary output.

**TWO NEW ERROR EXITS**, `X ERR 20` ("NO CONSOLE") and `X ERR 21`
("CONSOLE NOT AVAILABLE"), both `BD,$` — branch disabled to self, a
deliberate stop. That is `boot_plan.md` A4's point in MCP's own code:
a machine with no console has nowhere to report that it has no
console, so it stops.

**NOT RUN YET.** Like p.19's lines 27-53, this page needs context the
testbench does not set up — `$3`/`$R` carry the CST size from p.19's
table move, and the communication region is at `002150`-`002156`,
addresses no transcribed page populates. Transcription and execution
are separate milestones here, as they have been throughout.

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

> **BOTH RE-MEASURED 2026-10-22, and the two paragraphs above are
> wrong in three places.** Two things moved under them: printed p.19
> joined `DECKS`, and the equipment table stopped being invented.
> `tests/run_tests.sh` carries the full re-measurement; the short
> form is
>
> * **there is no `X18` halt** — p.19 is transcribed, so X18 is a
>   real row, and `X ERROR` is the only planted exit. The NORMAL run
>   ends there too, so **PC 182 is what every one of these runs
>   reports** and the PC says nothing about which path was taken.
>   The data checks do.
> * **the fallback is `0x400000800`** — the 6 was the fixture's
>   invented equipment code and printed p.35 gives TAPE octal 10.
> * **injection 2 had to change shape.** Deleting the table's letter
>   now makes the FIXTURE refuse to build the card (`KeyError:
>   'TP'`), which is a better failure but tests the fixture rather
>   than the machine. Punching `TQ` on the card instead leaves the
>   table alone and reproduces the old result exactly:
>   `0x400000000`, and p.18 never runs.

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
