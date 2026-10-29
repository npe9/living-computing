# The E-box: from an interpreter in a rule to arithmetic hardware

**Direction set by the project owner, 2026-10-28.** The diagnosis, in
their words: *"the repository now has idiomatic rule-level
orchestration, but its execution semantics are still written like a
large software interpreter embedded inside a rule."*

And the sentence that reframes the whole timing effort:

> **"You aren't trying to emulate Stretch's timings, you are trying to
> REPRODUCE them."**
>
> **"Stalls etc should happen as actual stalls, not as faked rules."**

With one scope limit, also theirs: **cycle accuracy, not timing
accuracy.** A Bluespec rule firing is a clock edge, so sub-cycle delay
has nowhere to live — which is what `docs/microarchitecture_roadmap.md`
already says under "What stays out".

## What is already idiomatic and must be preserved

Stated by the owner, and worth writing down so a later refactor does
not undo it:

* `step()` is only a clock enable, and behaviour lives in rules.
  (Since 2026-10-28 there is no `step()` at all: the core owns a run
  latch. See that commit.)
* Instruction buffering, look-ahead, storage, memory and the E-box are
  modules with interfaces.
* Mutually exclusive rules express the core control transitions.
* `mkCReg` explicitly represents required same-cycle ordering.
* `DecodedInstr` is a tagged union with typed payloads.
* Memory uses request/response handshakes and return tags.
* Long memory-dependent execution goes through start/busy/resume.
* Off-pipe work — I/O, transmit, recovery, interrupts — has its own
  rules.

**It does not need FIFOs between every stage, and not every submodule
needs `(* synthesize *)`.** Combinational `out` methods with atomic
enq/deq handoff in one orchestration rule is normal Bluespec practice.

## The reference, and it is checked out locally

`~/src/Flute/src_Core/CPU/IntMulDiv.bsv` — read 2026-10-28, and it is
the shape the arithmetic should take:

```bluespec
typedef enum { Div_RDY, Div_START, Div_LOOP1, Div_LOOP2, Div_DONE } DivState
   deriving (Eq, Bits, FShow);

rule rl_loop1 (rg_state == Div_LOOP1);          // shift while it can
rule rl_loop2 (rg_state == Div_LOOP2);          // subtract while it can
method Bool result_valid = (rg_state == Div_DONE);
```

**No budget appears anywhere.** `rl_loop1` shifts while
`denom2 <= numer>>1`; `rl_loop2` subtracts while `numer >= denom`; the
cycle count is whatever the data required, and the consumer stalls
because `result_valid` is false.

`~/src/Piccolo` and `~/src/CHERI-Piccolo` are also present if a second
opinion on stage structure is wanted.

> **>>> WHY THIS IS THE KEY TO CYCLE ACCURACY AND NOT JUST TIDINESS.
> <<<** The Stretch timing tables are conditional on OPERAND VALUES:
> Table 2 adds cycles "for each additional pre-shift of 4", "for each
> additional norm. of 6", "if recomplement is necessary"; the divide
> loop is "data dependent"; Table 3's `M+` says "Unlike signs AB > CD,
> add .6(x/y + 1)". The roadmap's old plan was to feed the operands to
> `eboxClocks`. **If the box iterates, those numbers EMERGE instead** —
> they stop being a table to reproduce and become a consequence of the
> hardware.

## The recommended order (the owner's, verbatim in substance)

1. Introduce a pure `prepareExec` result and **eliminate the
   "call execution to discover the operand" protocol**. Today
   `rl_prepare` calls `ebox.exec` with no operands so that `execute()`
   "bails out" with `needsRead` — which makes execution serve as both a
   supposedly side-effect-free query and the operation that commits
   architectural effects. Every instruction arm must then do no
   irreversible work before noticing an operand is missing: a fragile
   contract.
2. Define typed `ExecRequest`, `ExecCompletion` and explicit commit
   records.
3. **Extract one genuinely iterative operation — divide is the best
   forcing case — into a request/response box.**
4. Generalise into `mkPAU` and `mkSAU`, the historical parallel and
   serial arithmetic machinery.
5. **Replace `ebusy` with actual response readiness** for boxed
   operations. Countdowns remain only where the machinery is not yet
   modelled.
6. Move decode/preparation fully into an I-box stage output bundle.
7. Split whole-instruction look-ahead entries into the historical
   operation / operand / store / recovery entries. (`LaKind` already
   admits this: every live entry is `Whole`.)
8. Add forwarding and accurate SAU/PAU overlap.

## Separate commit from calculation

Execution helpers currently call `st.writeWord`, `st.writeIndex`,
`st.setIndicatorBits` and the accumulator writes directly. Returning
effects as data instead — a single `ExecCompletion` applied by one
commit rule — buys a single architectural commit point, easier
suppression on alarms and protection violations, easier branch
recovery, less scheduler coupling, and boxes that can be tested without
instantiating storage.

**Not every write must go through one universal structure**, but
arithmetic should not mutate global architectural state halfway through
its own calculation.

## What NOT to do

Also the owner's, and these are the traps:

* Do not insert FIFOs between all stages.
* Do not mark every module `(* synthesize *)`.
* Do not pipeline combinational helpers merely to shorten files.
* Do not replace typed `DecodedInstr` variants with flat opcode records.
* Do not turn every pure arithmetic helper into a module.
* Do not split well-tested functions arbitrarily: **preserve the
  primary-source citations and the semantic seams.**

Pure functions are idiomatic for genuinely combinational bounded work.
Modules are warranted when the component owns state, consumes multiple
clocks, arbitrates a resource, or supports independent concurrency.

## The oracle for every step

The full suite — 5621 PASS / 0 FAIL as of 2026-10-28 — plus, for the
boxed operations, Volume 2's per-instruction atlas, which is throughput
measured on a machine WITH overlap. `docs/microarchitecture_roadmap.md`
M2 is where that becomes the oracle; the measured `VflInt` residual is
0.281 µs mean and 1.20 worst.

# Step 1, measured: the address is pure; the PROBE ANSWERS A SECOND QUESTION

`operandTarget(st, di)` was written as the pure analogue of
`storeTarget` (`bsv/StretchIBox.bsv`), and then run BESIDE the old
`ebox.exec`-with-no-operands probe across the whole suite, comparing
both answers and printing on mismatch.

## The positive result, and it is strong

**Across 5621 checks there was not one address disagreement.** Every
mismatch was `pure = Valid`, `probe = Invalid` — eight of them. There
were **zero** cases where both were Valid and differed, and **zero**
where the pure function said "no fetch" and the probe wanted one.

So: *wherever the probe asked for a fetch, `operandTarget` named the
same word.* The three-state `p` split matters and is handled — `p == 4`
no fetch, `p == 0` ordinary effective address, any other `p`
progressive, where the address comes from the index register.

## The blocker, which the measurement found and the plan did not

The eight mismatches are not address errors. They are the probe
answering a **different question**: not "which word does this
instruction want?" but "**will this instruction fetch anything at
all?**" — and that has at least four separate causes, named by the
sections the mismatches fell in:

| section | why the probe returned Invalid |
|---|---|
| `DF SUPPRESSED (p.32/p.45 class 1)` | `dfSuppresses` — DF masked on and the address protected |
| `Address Invalid (AD, no-op)` | the address is not installed, so the operation is a no-op |
| `OP and AD indicators (both polarities)` | Operation Code Invalid — the model has no arm |
| `CV and LTRCV` | same shape (DCV is unbuilt and sets OP) |
| `A VFL STORE ACROSS A WORD BOUNDARY` | the store path completes without the probe's fetch |

`dfSuppresses(st, a)` is already pure and `installed` is available, so
two of those are cheap. **The third is not**: "will `execute()` set OP?"
is a statement about WHICH ARMS EXIST, which is precisely the
interpreter shape this conversion is trying to remove. Enumerating it
in a predicate would duplicate the dispatch it is meant to replace.

> **>>> SO STEP 1 AND STEP 2 ARE COUPLED, AND THAT IS THE FINDING.
> <<<** The probe has two legitimate answers — "I need word A" and "I
> am already finished, with these indicators" — and `Maybe#(WordAddr)`
> can only carry the first, so the second is smuggled in as `Invalid`.
> **"Completes immediately" is a real outcome, not a bail-out**, and it
> cannot be removed until it is representable. That is exactly the
> typed dispatch union step 2 proposes:
>
> ```bluespec
> typedef union tagged {
>    ExecCompletion Complete;      // AD / OP / DF-suppressed, with indicators
>    OperandRequest NeedOperand;   // operandTarget's answer
>    SauRequest     StartSAU;
>    PauRequest     StartPAU;
> } ExecDispatch deriving (Bits);
> ```
>
> With that, `Complete` carries the indicator effects the no-op cases
> set, `NeedOperand` carries `operandTarget`'s address, and the
> impossible combinations a `Tuple5` currently permits stop being
> representable.

**Revised order for step 1:** land `operandTarget` as the proven pure
address source, then do step 2's typed result, and only then delete
`EBox.exec`. Deleting the probe first would mean inventing a predicate
for "does the model implement this", which is the wrong direction.

# Step 3, scoped: all eight "completes without fetching" causes, named

The step-1 measurement said eight instructions in the corpus are
classified as fetching and then complete without a read, and that the
third cause looked like "will `execute()` set OP?", which is a
statement about which arms exist. **Measured properly, it is not.** A
second instrumented run printed, for each of the eight, the address and
every candidate condition, then mapped each to its test section:

| cause | n | condition, and it is PURE |
|---|---|---|
| DF suppression | 3 | `dfSuppresses(st, addr)` — already a pure function |
| address not installed (AD) | 2 | `!installed(addr)` |
| **CV reads the accumulator** | 2 | not a completion at all: `fetchesOperand` OVER-REPORTS |
| **M+ crossing a word boundary** | 1 | `fieldCrosses(ea, len_)` — pure arithmetic |

One per class for DF (VflInt, Connective, Fp), which is a good sign the
three arms agree.

**The two surprises are the useful part.**

`CV`'s mismatches both had `addr = 8` — the ACCUMULATOR. printed p.73,
quoted at the arm: *"A field from the accumulator is converted as an
integer from binary to decimal..."*. CV has no storage operand, so
`fetchesOperand` returning True for it (because `v.a.p != 4`) is wrong,
and the probe was compensating. `LTRCV` is different — *"The addressed
STORAGE field is converted"* — so it genuinely fetches. The fix is to
NARROW `fetchesOperand`, not to add a completion clause.

`M+`'s was in `decks/vfl_crossing_store.strap`, whose own source says
what it expects:

```
        M+(BU,32,8), TF+.48
        BZOP, $                      ! hang if OP did NOT come on
```

`protViolates`'s comment already recorded why: a STORE may cross a word
boundary as of 2026-10-24, but *"the remaining one-word-each sites are
the ones that still cannot cross: M+ and the CM connective."*

**And reading the VflInt arm for this turned up two more pure OP causes
the corpus does not currently reach** — `vi.m.decimal == 1 && !radixConv`
and `isProgressive && vi.a.i1 == 0`. Both are conditions on the decoded
instruction. So the predicate is enumerable, with roughly six clauses,
and none of them requires knowing which arms exist.

> **>>> WHICH IS WHY THE NEXT STEP WAS NOT TO WRITE THAT PREDICATE.
> <<<** Every clause needs `ea` and `len_`, and a review of this file
> had just named the real problem: the effective address was being
> derived in THREE independently maintained places — `operandTarget`,
> `storeTarget`, and the arms of `execute()`. A predicate with its own
> derivation would have been a FOURTH.
>
> So `prepareExec` came first: one pure function, one `ea` per class,
> returning a `PreparedExec` record, with `operandTarget` and
> `storeTarget` reduced to projections out of it and `rl_prepare`
> calling it once for both. The completion prediction is then one more
> field on a record that already has the derivation, rather than a new
> copy of it.

**Order for the rest of step 3**, each with the same oracle — run it
beside the probe and require ZERO mismatches before deleting anything:

1. Narrow `fetchesOperand` to exclude CV. (Expect the two CV mismatches
   to disappear and nothing else to move.)
2. Add `completesWithoutFetch` to `PreparedExec`, with the six clauses
   above.
3. Only then delete `EBox.exec`. Note what that does and does not buy:
   preparation stops calling execution *speculatively*, but the
   completion's own effects still come from running `execute()` through
   the ordinary dispatch path. It removes a query that commits, not the
   interpreter.


# >>>>>> STEP 3 IS DONE: `EBox.exec` IS DELETED, 2026-10-29 <<<<<<

The preparation arm no longer calls execution to ask a question. Both of
the probe's answers are pure, and both were PROVEN against it across the
whole corpus before it was removed:

| answer | replacement | evidence |
|---|---|---|
| "I need word A" | `prep.operandAddr` | **0** address disagreements in 5621 checks |
| "I am already finished" | `prep.completesWithoutFetch` | **0** disagreements in 5621 checks |

`completesWithoutFetch`'s six causes, every one a pure condition and
every one found by measurement rather than by reading the arms and
hoping:

* the decimal refusal, `m.decimal == 1 && !radixConv`
* progressive indexing with index 0
* M+/M+1/M+MG, and the CM connective, crossing a word boundary —
  `fieldCrosses(ea, len_)`; a plain ST may cross as of 2026-10-24, these
  may not
* DF suppression, `dfSuppresses(st, w)`
* the address not installed (AD), `!installed(w)`

and separately, CV was removed from `fetchesOperand` altogether, because
printed p.73 says its operand is the ACCUMULATOR — that was never a
completion, it was a misclassification the probe had been papering over.

**An instruction that will finish without reading now gets a level with
no operand address, exactly like ST, and is dispatched through
`ebox.start()` in the ordinary way.** The inline completion path and its
"classification mismatch" message are gone: there is no longer a
classification to mismatch. That display was its own counter, and it
went 8 → 6 when CV was reclassified, exactly as predicted beforehand.

## What this does NOT buy, stated plainly

`execute()` is still a 6,800-line ActionValue that computes and commits
in one invocation, and the completion's effects still come from running
it through ordinary dispatch. **This removed a query that commits; it
did not remove the interpreter.** The remaining steps are unchanged:

5. an explicit arithmetic completion record,
6. **divide as the first genuinely iterative box** — the forcing case,
7. readiness rather than `ebusy` as its timing authority,
8. generalise into PAU/SAU,
9. preparation as a real stage-output bundle (`prepareExec` is its seed),
10. split the look-ahead's `Whole` levels into the historical pieces.

# A NEGATIVE RESULT WORTH THE SPACE: `completesWithoutFetch` IS INERT

The step-3 writeup ended with a caveat: zero prediction-vs-probe
mismatches proves agreement *everywhere the corpus reaches*, and two of
the six clauses -- the decimal refusal and progressive-indexing-with-X0
-- were reasoned from the arms rather than measured. Closing that
caveat produced three results, and the second one contradicts what the
first was supposed to show.

## 1. A census, and the two clauses really were unreached

A temporary `Bit#(8) whyMask` on `PreparedExec`, displayed on every
firing, over the whole suite:

| clause | firings |
|---|---|
| DF suppression | 3 |
| address not installed (AD) | 2 |
| M+/CM crossing a word boundary | 1 |
| **the decimal refusal** | **0** |
| **progressive indexing with X0** | **0** |

Six firings, matching the six remaining inline completions exactly.

## 2. >>> AND THE PROGRESSIVE-X0 REFUSAL IS PRINTED, NOT INFERRED <<<

It had been an **uncited** refusal in BOTH VFL arms. Reference Manual
printed **p.21** (PDF 24), read at the ink:

> *"In progressive indexing, the value field, bits 0-24 of the index
> specified by I, is used as the effective address. **IF PROGRESSIVE
> INDEXING WITH INDEX REGISTER X0 IS SPECIFIED, INDICATOR OP (OPERATION
> CODE INVALID) IS SET.**"*

Index field 0 means "no indexing" for ordinary addressing -- see
`effAddr24`'s `if (idx == 0) return raw` -- so progressive indexing has
no register to advance and the machine refuses it. The citation is now
at both arms and in the deck. **The model was right and simply never
said why.**

## 3. THE INJECTION I WROTE FOR THE DECKS SURVIVED

Both decks were written expecting to pin the two clauses, on the
reasoning that deleting a clause makes preparation issue an operand
fetch for an instruction that never reads it, and that the extra fetch
would move a zero-tolerance cycle window.

**It does not.** With both clauses deleted the counts are still exactly
145 and 142, and every value check still passes. So the claim was swept
properly rather than left as an impression:

> **A full-suite run with `completesWithoutFetch` hard-wired to `False`
> came back 5633 PASS / 0 FAIL.**

The field is **behaviourally inert on this corpus**. The look-ahead's
operand fetch overlaps, so issuing a pointless one costs nothing any
current check can see.

### What was done about it

The field is **kept**, and labelled at its declaration with exactly
that: no test distinguishes it, measured rather than suspected. It is
kept because the machine would not request an operand for an operation
it has already refused and the target is cycle accuracy -- but a field
nothing can observe is a liability if it is not advertised as one.

**What would pin it:** either a count of memory requests the testbench
can read, or M2's look-ahead overlap, at which point a pointless fetch
costs a clock and those two decks' windows move.

### And the decks keep their value, with the right claim attached

They pin the OP REFUSALS, which is worth having independently -- one
sourced to printed p.21, one labelled as a MODEL scope boundary, since
the real 7030 does perform decimal VFL arithmetic and this model
refuses it so an unbuilt operation is visible rather than silently
wrong. Their measured injection is the refusal itself: replace either
arm's test with `False` and all four checks fail, with
`refused_head` at word 272 showing the store LANDING
(`0xfffffffffffffff9`, `0xffffffffffff1234`) and the machine hanging on
its `BZOP, $` self-branch at half-word 392 or 391 until the step cap.

# Step 6 groundwork: the divide timing charts, MINED

`docs/source_audit.md`'s Audit 3 lists **"the PAU/SAU timing-chart
category (pp. 225-243), which does give numbered per-cycle charts"** as
genuinely unmined, and its goal table calls it *"the first real
per-cycle source"* for M1. This is not a new discovery; it is two of
those pages finally read.

**There are nineteen of them**, Figures 3.8.1-3.8.19, one per
arithmetic operation: Load, Add, Add to Magnitude, Compare, Add to
Fraction, Shift Fraction, Store, Store Rounded, Store Low Order, Store
Root (2 sheets), Multiply, Load/Store Multiplier Register, **Divide (3
sheets)**, Divide Double, SAU Multiply and Multiply-and-Add, and SAU
Divide. They are timing charts with named triggers and per-cycle
pulses, and they are legible at 300 dpi.

## Figure 3.8.19, SAU DIVIDE (TIMING) -- PDF 243, printed 8-23

Read at the ink. Two halves, DIVISOR NORMALIZATION and DIVIDE REDUCTION
CYCLES, with these lines among others:

* `GATES 36 & 72 & ENABLE MULTIPLE DECODING`
* `GATE COUNTER ADDER TO REG & SUB SHIFT AMOUNT FROM CTR`
* `(D3, CTR=0, TRUE RESULT)` -> `FINAL DVDE TGR`
* `IF DIVIDEND NOT NORMALIZED TAKE SAME ACTION AS FP`
* `REDUCTION CYCLES JUST LIKE FP`

**So the loop is counter-driven and terminates on CTR = 0**, each
reduction cycle subtracting a shift amount from the counter. That is
the FSM shape, and it is the thing Table 2's "2 cycles for each
additional reduction loop (number of cycles is data dependent)" is
counting.

## Figure 3.8.15 sheet 2 of 3, FLOATING-POINT DIVIDE -- PDF 240, printed 8-17/8-18

The phases are named: **Trial Reduction Cycle**, then **Intermediate
Reduction Cycle**s, then a **Last Reduction Cycle**. And twice, in the
chart's own words:

> **"Number of Reduction or Dummy Cycles Depend Upon Number of Quotient
> Bits Developed per Step (Cycle)"**

with a note that an intermediate cycle **"could be a dummy cycle ... if
more than 6 quotient bits were developed on the previous reduction
cycle"**, and an exponent-subtraction lane annotated

> **"Divider Determined by Multiple Selection Circuits"**

## >>> WHAT THIS ESTABLISHES, AND THE ONE THING IT DOES NOT <<<

**Established, and enough to build the FSM:** the divide is not 96
single-bit steps. It is a counter-driven loop of trial / intermediate /
last reduction cycles, developing a VARIABLE number of quotient bits
per cycle, with dummy cycles when a step runs ahead, terminating when
the shift counter reaches zero. `fpDivFrac` currently does all 96
restoring-division iterations combinationally in one clock, and
`eboxClocks` charges a flat 4 -- which its own comment calls a floor.

**NOT established:** how many quotient bits a given cycle develops.
The chart attributes it to the "Multiple Selection Circuits", which are
ALDs this volume does not reproduce. So the bits-per-cycle rule is
**[NOT IN THE SOURCES]** as things stand, and any FSM written today
must either derive its loop count from Table 2's aggregate rules --
which `tests/perf_char_timing.py` already carries, transcribed, with
"2 cycles for each additional reduction loop" among them -- or say in
its own comment that the per-cycle division is invented.

That is the decision to make before writing `mkDivBox`, and it should
be made deliberately rather than discovered halfway through. The
remaining seventeen charts are the same seam for the other operations.


# A COMMIT-HYGIENE RULE, PAID FOR TWICE

**`git add -A` run from `stretch/` stages the whole repository, not
`stretch/`.** Commit `23ca2d5`, whose subject is the divide box, also
contains fifteen files belonging to three unrelated machine projects --
`pim/`, `symbolics3600/`, `transputer/` -- plus a `README.md` change,
all of which were the owner's untracked work in progress. Nothing was
lost or altered, but unrelated work is mixed into a commit that claims
to be about one thing, and it was pushed before anyone noticed.

This is the SECOND time in one session. The first swept ten debug
probes into a commit, which is why `tests/verify_no_probes.py` exists
and runs first. **That check cannot see this one**: it scans committed
files under `stretch/`, and these are above it.

> **THE RULE: stage by path, never `-A`, and when the working directory
> is `stretch/` remember that the repository root is one level up.**
> `git add bsv/X.bsv tests/Y.sh docs/Z.md` costs one extra line and
> cannot reach into a sibling project.

Splitting the commit afterwards means rewriting pushed history, which
is a destructive operation and needs the owner's explicit say-so, so it
has deliberately NOT been done.

# >>>>>> THE ATLAS CANNOT CALIBRATE DIVIDE, AND IT SAYS SO ITSELF <<<<<<

The divide box's one invented number -- `divBitsPerCycle` -- was left
uncalibrated with "Perf. Char. Vol. 2's measured divide page" named as
the next step. **There is no usable measured divide page.** Vol. 2 says
so twice, in its own words.

**Vol. 2 PDF 41:**

> *"The present measurements for /, D/, and R/ do not give a realistic
> timing, since the latter is strongly data dependent. **The average
> divide time should be about 10 us.**"*

**Vol. 2 PDF 115**, in the notes to the VFL section:

> *"The error marks on divide instructions (pp. 127, 154, 177) are
> **due the use of a zero divider**."*

A zero divisor is precisely the case that SKIPS the reduction loop:
Vol. 1 Table 2's own `zero_divisor` entry -- transcribed in
`tests/perf_char_timing.py` -- is "3 cycles pre-execution and 2 cycles
execution INSTEAD OF previous", i.e. five cycles with no reduction
loops at all. So the three atlas pages measure the one input for which
the loop does not run.

## What this costs, and it is not only divide

`docs/microarchitecture_roadmap.md` M1 and M2 both name Vol. 2's
per-instruction atlas as THE oracle -- "this is where the atlas becomes
the oracle", with M2's correctness "measured by how much of the
residual it closes". **For divide that oracle is void**, and the
roadmap does not say so. The same question should be asked of every
other operation before its box is calibrated: Vol. 2's notes pages
(PDF 110-116) are where the authors flag which measurements are
unrepresentative, and they have not been read as a whole.

## What is left for divide, stated honestly

1. **Vol. 1 Table 2's data-dependent rules**, already transcribed:
   2 pre-execution cycles (+2 per additional divisor shift of 6), 2
   execution (+2 per additional dividend shift of 6, +2 for the initial
   reduction loop if the dividend is normalised, +3 for the initial
   dividend pass if it has leading zeros, **+2 for each additional
   reduction loop**, +2 if the final remainder needs complementing,
   +1 all). These are RULES, not a measured total, and they are the
   best divide oracle in the corpus.
2. **"about 10 us"**, which at the project's 0.3 us machine cycle is
   ~33 cycles -- a sanity bound, not a measurement, and explicitly an
   average over unknown data.

The box currently takes 18 cycles (1 trial + 16 reduction at 6 bits
per cycle + 1 last), i.e. ~5.4 us. That is the right order and about
half the stated average.

> **>>> AND TUNING `divBitsPerCycle` TO 3 SO THAT 33 CYCLES FALLS OUT
> WOULD BE EXACTLY THE MOVE THIS WORK EXISTS TO AVOID. <<<** It would
> be fitting an invented constant to a rough average so the total looks
> right -- emulating the timing, not reproducing it. The honest path is
> Table 2's RULES: derive the pre-shift, dividend-shift and
> normalisation counts from the operands, which `StretchFP` already
> computes to produce the answer, and let the loop count follow. The
> bits-per-cycle then stops being free: it is whatever makes the rule
> counts come out, and if no value does, that is a finding about the
> model rather than a number to pick.
