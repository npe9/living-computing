# Execution operations

> **CORRECTED 2026-09-29, by the transcription this note commissioned.**
> Three readings in here were wrong and are fixed in place:
> 1. **The header prints `1C`, not `IC`.** What read as a letter-I top
>    bar is the row's own DASHED RULE LINE — 59 px where the glyph
>    spans 24. The deck's letter `I` is a bare stroke with no serifs;
>    this glyph has a bottom serif, which no rule can forge. See
>    `listing_typography.md` §10.
> 2. **`TI,1,1000,$MASK` is `TI,1,I00O,$MASK`**, and it does not "turn
>    on the relevant mask bit" — `I00O` is the all-ones word, so it
>    turns on EVERY settable bit, 20-47. That asymmetry is the point:
>    1CA needs no mask setup because OP is indicator 15, inside the
>    permanently-masked 0-19 range, while 1CB must set the mask because
>    IF is 21, outside it.
> 3. **1CA is 12 rows, not 11** — §3.2's table omitted the
>    `I6218 BD,$+.32` header row that §3.1 quotes separately.
>
> Everything else in §3 bore out against the pages, including the 1CA
> mechanism. Transcription: `verify_ax5b_162_test1cab_listing.py`.
: `USA`'s number, p.50's two exceptions, and the deck that tests them

Research note, 2026-09-29.  Read-only: nothing in `bsv/` or `strap/` was
changed to produce it.  It settles the three things the `EX`
implementation of 2026-09-25 (`git log -1 e954152`) deliberately left
undone, and bounds what it cannot settle.

Every page citation below was rendered with `pdftoppm -r 300` (Reference
Manual, Performance Characteristics) or `-r 400` (the `jb_ax5b` listing)
and read from the PNG.  Reference Manual **PDF page = printed page + 3**.
The Performance Characteristics volumes are cited by their own printed
chapter-page (`3-2`, `3-11`, `3-12`) with the PDF page beside it.
`jb_ax5b`'s listing pages carry no printed numbers, so they are cited by
PDF page, as every `verify_ax5b_*.py` in `strap/` already does.

---

## 0. Two corrections to the premises this note was given

**(a) The "several hundred" parenthetical is on printed p.45, not p.52.**
It is part of item 17 itself.  Printed p.52 item 3 states the same
one-millisecond rule from the suppression side but carries a *different*
addition, quoted in §1.2 — and that addition is a behavioural fact for
`EXIC`, not a timing one.

**(b) `I60S1` returns DISABLED, and that was already known in this
repo.**  §3 needed "is the machine disabled when TEST 1C runs its `EX`?"
answered.  It is, and not by inference:
`strap/programs/ax5b_160s1_clr_inds.strap`'s header records the tail row
first-hand — *"the RETURN, `I60SX1 $BD,0` at 023041.00.  I60S1 returns
via a BRANCH DISABLED, so every block that calls `SIC,I60SX1 / B,I60S1`
runs DISABLED afterwards unless it enables for itself."*

---

## 1. QUESTION 1 — the `USA` timeout.  The number exists.

### 1.1 The two Reference Manual statements, verified first-hand

Printed **p.45** (PDF 48), *Instruction Exceptions*, item 17, verbatim:

> *17.  Unended Sequence of Addresses (USA).*  A LOAD VALUE EFFECTIVE,
> EXECUTE, or EXECUTE INDIRECT AND COUNT operation has been in progress
> for longer than one millisecond (several hundred indirect addressing
> cycles).  The operation is terminated wherever it may be and the
> program proceeds.  This indicator is the only means of breaking out of
> a loop that occurs as a result of a programming error in the use of
> execution operations or indirect addressing.  If interruption occurs,
> it takes place after execution of the causing instruction has been
> terminated.

Printed **p.52** (PDF 55), *Execution Suppressed*, item 3, verbatim:

> 3.  Indicates that the execution of EXECUTE, EXECUTE INDIRECT AND
> COUNT, or LOAD VALUE EFFECTIVE has exceeded one millisecond (the alert
> is USA).  Any pseudo-instruction counters referred to by EXIC
> instructions will have been stepped.

That second sentence is the one to carry forward into `EXIC`: a `USA`
termination does **not** roll the pseudo-instruction counters back.

### 1.2 The cycle time — a documented number, with its page

**IBM 7030 Performance Characteristics, Vol. 1 (March 1961), printed
page 3-2 (PDF page 20)**, closing the definition of pre-execution and
execution time:

> The times are listed (table 2) in terms of the basic machine cycles,
> which is presently 0.3 microsecond.

This is the number `bsv/StretchTiming.bsv`'s header already asserts
("one clock = 0.3 us; one I-box control cycle = 2 clocks = 0.6 us as
shipped") and `docs/microarchitecture_plan.md` already uses ("Cycle
base: one Bluespec clock = one E-box cycle = 0.3 µs").  It is now cited
to its page.

**Therefore one millisecond is 3333⅓ of this model's clocks** — 3333, or
3334 if rounded up.

### 1.3 The cross-check that closes the loop: "several hundred"

The manual's parenthetical is itself checkable against IBM's own timing
tables, and it checks out — for **LVE**, which is what "indirect
addressing cycles" names.  Performance Characteristics Vol. 1,
**Table 4, "I-BOX TIMES – DIRECT INDEX", printed page 3-11 (PDF 29)**,
read at 300 dpi:

| row | Address in EM | Address in XS | Address in IR |
|---|---|---|---|
| `LVE` | 7.8 µsec + dec | 6.6 µsec + dec | 6.6 µsec + dec + LAdr |
| `LVE as object INSN of LVE` | Additional 4.8 µsec | Additional 3.6 µsec | Additional 3.0 µsec + LAdr (4.2 if LAMT) |

One additional level of `LVE` chaining costs **4.8 / 3.6 / 3.0 µsec**.
In 1 ms that is **208 / 278 / 333 levels** — "several hundred indirect
addressing cycles", exactly, in all three memory cases.  In machine
cycles one indirect addressing level is 16 / 12 / 10 clocks.

The parenthetical is therefore **about `LVE`, not about `EX`**, and it
should not be quoted as an `EX` number.  Table 6, **"I-BOX TIMES –
MISCELLANEOUS INSTRUCTIONS", printed page 3-12 (PDF 30)**, gives `EX`
as a six-term recipe rather than a scalar:

> EX
> 1. Decode time, plus
> 2. Always begins with Look-ahead drain, plus
> 3. Instruction fetch time as follows:
> [address table: 0.0,0.32 → 4.8 µsec; 1.0,1.32 → 6.0; 2.0,2.32 → 7.8;
> 3.0,3.32 → 7.8; 4.0,4.32 → 7.8; 5.0–11.32 → 11.2; 12.0,12.32 → 7.8;
> 13.0–14.32 → 5.4; 15.0,15.32 → 4.8; 16.0–30.32 → 4.2; 31.0,31.32 →
> 6.0; **32.0–up → 5.4**]
> 4. Add decode and execution time for given instruction
> 5. Always ends with LA drain, plus
> 6. Add 3.0 µsec for fetch of next instruction

Two of the six terms ("look-ahead drain") are not scalars, so there is
**no single documented per-`EX`-level charge**.  There is a bound: for a
chain of `EX`s at addresses 32.0 and up, one level is decode (0.6) +
fetch (5.4) = 6.0 µsec plus a drain, so 1 ms is of order **110–160 `EX`
levels** — "over a hundred", not "several hundred".  Quote it as a
bound, not a number.

For completeness, Table 6 continued (printed p.3-13, PDF 31) gives
`EXIC` the same shape plus *"4.2 µsec to fetch the pseudo-instruction
counter … if the ps IC is in EM"* / *"3.0 µsec … if the ps IC is in XS"*,
overlapped with the drain, a flat *"Instruction fetch time = 6.0 µsec"*,
and the stepping cost (`LAAR` time in EM, `.6 µsec` in XS).

### 1.4 What the deck's 2049 bounds, and what it does not

Routine 1262 TEST 1D builds a chain of 2049 (see §3.4).  2049 levels at
6.0 µsec is ~12 ms — twelve times the threshold.  So **2049 bounds the
threshold only from above** (it must be under 2049 levels) and is
consistent with anything from ~110 to ~333.  It is a design margin, not
a measurement, and it does not pin the cycle time from the other side.
The premise that it might was worth testing; it does not hold.

### 1.5 THE FINDING THAT MATTERS: a 3333-clock timer would fail the deck

The model chains one `EX` level per Bluesim clock —
`StretchExecute.bsv`'s `mkEBox.resume()` replaces `held.di` with the
subject once per clock, and its own comment says so.  The whole `EX` is
charged **once, at dispatch**, from `StretchTiming.bsv`'s `iboxCycles`.

So a literal implementation — "count clocks since the execution
operation began, fire `USA` at 3333" — gives, for the deck's 2049-level
chain, 2049 clocks plus the dispatch budget.  **That is under 3333.
`USA` would never fire, and routine 1262 TEST 1D would fail.**  The
number alone is not enough; the number has to be spent at the documented
rate.

Two shapes work, and they are the same statement twice:

1. **Charge the documented per-level time.**  Make `resume()`'s subject
   swap cost the Table 6 recipe (6.0 µsec = 20 clocks for a subject at
   32.0 and up; 4.2 µsec + decode for 16.0–30.32) instead of one clock,
   and compare a per-operation clock counter against 3333.  This is also
   the cycle-accurate answer and is what `microarchitecture_plan.md`'s
   goal asks for; it will change `CYCLES<=` benchmarks only for programs
   that execute an `EX`.
2. **Count levels against a documented divisor.**  Keep one clock per
   level and fire at `1000 µs ÷ (per-level µs)` levels — 167 for the
   6.0 µsec `EX` case, 208/278/333 for the three `LVE` cases.  This is
   the manual's own framing ("several hundred indirect addressing
   cycles") and is cheaper, but it hard-codes a quotient the timing
   model would otherwise derive.

They agree on when `USA` fires.  (1) is the better fit for this project's
stated direction; (2) is defensible and much smaller.

### 1.6 A rule-4 gap found on the way, stated rather than left

`StretchTiming.bsv`'s `iboxCycles` gives `BranchOrMisc`-misc:

```
? (case (x.code) 3'b100: 3; 3'b001: 8; default: 14; endcase)   // Z / RCZ / R
```

`EX` is misc code `3'b010` (`StretchExecute.bsv` line 3783, "EX
(EXECUTE), Reference Manual printed p.50"), so **`EX` currently falls
into `default: 14`, a value sourced for `R`** (Table 6: `R (from EM)`
7.8 µsec + dec = 8.4 µsec = 14 I-box cycles), not for `EX`.  It lands
within the range Table 6 gives `EX`, so nothing is visibly wrong — but
it is not the `EX` number and AGENTS.md rule 4 wants it to be.  Fixing
it and implementing `USA` are naturally the same change.

### 1.7 Cost of building `USA`, if it is built

Small, once the shape above is chosen.  A per-execution-operation clock
(or level) counter belongs with `held` in `mkEBox` — started when
`start()` stashes an `EX` and cleared when `resume()` returns
`tagged Valid`, i.e. exactly the `HeldOp` lifetime.  On overflow:
set indicator `USA` (17), abandon the chain, and return the `EX`'s own
`next` so "the operation is terminated wherever it may be and the
program proceeds" (p.45).  Indicator 17 is inside the permanently-masked
range 0–19 (`StretchStorage.bsv`: `mask <= {20'hFFFFF, …}`), so no mask
test is needed — and see §2, because the interruption that must follow
is p.50's second exception, not ordinary interruption.

---

## 2. QUESTION 2 — p.50's two special exceptions.  A design.

### 2.1 The text, verified first-hand

Printed **p.50** (PDF 53), first paragraph, continuing from p.49's *"In
general, when the interruption system is dis-"*:

> abled, interruption cannot occur and address monitoring is suspended.
> In order that control may remain entirely with the main program during
> an execution operation, two special exceptions are made.  First,
> address monitoring is always in force during (1) EXECUTE and (2)
> EXECUTE INDIRECT AND COUNT, except for the address of the location of
> the *first level* pseudo-instruction counter.  Second, at the
> completion, termination, or suppression of an execution operation,
> interruption is always permitted.

And the Programming Note directly below it, which is what actually
bounds exception 2 and is easy to miss:

> When interruption occurs following an execution operation with the
> interruption system disabled, it is caused only by the actuated
> indicator of highest priority whose mask bit is one.  Further
> interruptions cannot occur until either the system is enabled or
> another execution operation is completed, terminated, or suppressed.
> Examination for other actuated indicators can be programmed into the
> correction routine.
>
> Any actuated indicator whose mask bit is on may cause interruption at
> the completion, termination, or suppression of an execution operation.

Three things follow that the one-sentence version does not say:

* exception 2 is **one interruption**, not "interruption enabled for a
  while";
* the mask still applies — exception 2 overrides `irqEn`, not the mask;
* the indicator may have been actuated **before** the execution
  operation started.  The deck relies on exactly that (§3.2).

### 2.2 Where the state lives

An "execution operation in progress" flag, and a one-shot "an execution
operation just retired" pulse.  Both belong in `mkEBox`, because
`mkEBox`'s `held` register already *is* the execution operation's
lifetime: `start()` stashes an `EX` into `held` and bails for the
subject word; `resume()` swaps the subject in one level per clock;
`held <= tagged Invalid` on the clock the operation completes.

* **In progress** — `Reg#(Bool) execOp`, set with `held` in `start()`
  when `exSubjectAddr` is `Valid`, cleared with `held` in `resume()`.
  Published from `mkEBox` and forwarded to `StretchStorage` (or read by
  the core and passed down; see 2.3).
* **Just retired** — `Reg#(Bool) execBoundary`, set on the clock
  `resume()` returns `tagged Valid`, cleared by `rl_interrupt`.  **It
  must be a register, not a wire.**  `intDueCalc` is latched one clock
  behind the indicator write (its own comment in `StretchStorage.bsv`
  says so), and `armInterrupt` additionally waits for
  `la.count()==0 && !ebox.busy() && ibusy == 0` to settle, so the
  boundary and the arming do not coincide in one clock.

### 2.3 Exception 1 — one term in one function, not thirty edits

`StretchExecute.bsv`:

```
function Bool protViolates(StretchStorage st, WordAddr a);
  ...
  return st.irqEnabled() && installed(a) && signalled;
endfunction
```

Every one of the ~30 call sites goes through this.  Exception 1 is:

```
  return (st.irqEnabled() || st.execOpInProgress()) && installed(a) && signalled;
```

and **no call site changes**.  That is the right granularity, because
"address monitoring is always in force" is about monitoring as a whole —
`DS`, `DF` *and* `IF` — which is exactly the set `protViolates` gates.
`dfSuppresses`, `ifViolates` and `ifSignal` all inherit it for free, and
they should: p.45 item 21's *"the fetch or branch did not take place and
the entire operation was suppressed"* is the behaviour TEST 1CB checks
(§3.3).

The alternative is to thread it through `ExSubject`, which `execute()`
already carries (`ex.under` is true from the first subject swap
onwards).  That is more "local" but needs `protViolates` to take an
extra argument at ~30 call sites, and it is **wrong at the edges**: the
monitoring must be in force for the `EX`'s *own* subject-location fetch
at level 1, where `ex.under` is still false (`mkEBox.resume()` computes
`ifViolates(st, sa[18:1])` outside `execute()` precisely for that
reason), and it must stay in force for the whole operation, not only
inside `execute()`.  **Take the `StretchStorage` method.**  One new
method, one changed line, zero call-site churn.

Cost: one `Reg#(Bool)` plumbed from `mkEBox` to `StretchStorage`.  The
plumbing is the only real work, and `StretchCore` already holds both
modules.

### 2.4 The "first level pseudo-instruction counter" carve-out costs nothing today

It is `EXIC`-only.  Plain `EX` has no pseudo-instruction counter, so
there is nothing to exempt, and the carve-out is **zero lines** until
`EXIC` lands.  When it does, it is one exemption term at the one place
`EXIC` reads its first-level pseudo-IC — the address named by bits 0-17
of the `EXIC`'s own effective address — and it applies only to the
*first* level: a second-level `EXIC`'s pseudo-IC is monitored.

**It is deferred only because `EXIC` is, and it acquires a deck oracle
the same day `EXIC` does.**  §3.5 shows TEST 2CB placing the first-level
pseudo-IC `I62PSI` *inside* the monitored region on purpose: an
exception-1 implementation without the exemption raises a spurious `IF`
there and 2CB fails.  Zero lines today, load-bearing and witnessed
tomorrow — not trivia.

Note `EX` already carries its own, different carve-out — p.50's *"An
effective address of EXECUTE that is below 32.00 … is not monitored by
the address monitoring mechanism; that is, indicator IF cannot be
actuated by these addresses"* — implemented as `ifViolates`' `a >= 32`
guard and tested by `strap/programs/ex_monitor.strap`.  The two are
different rules with different comparands and neither subsumes the
other, but they compose at the same call: a first-level `EXIC`
pseudo-IC below 32.00 is exempt twice over.

### 2.5 Exception 2 — the expensive half

`StretchStorage.bsv`'s `intDueCalc` returns `tagged Invalid` whenever
`!irqEn`, and `StretchCore.bsv`'s `armInterrupt` requires
`isValid(intDue)`.  So today **no interruption can be taken while
disabled, anywhere.**  Exception 2 needs both to change:

1. `intDueCalc` must publish the leftmost masked-and-actuated indicator
   *regardless* of `irqEn` — i.e. compute `found`/`n`/`eia` always, and
   let the consumer decide.  Cleanest as a second latched output
   (`intDuePending`, ungated) alongside the existing gated one, so the
   ordinary path is bit-for-bit unchanged.
2. `armInterrupt` gains `(isValid(intDue) || (execBoundary && isValid(intDuePending)))`.
3. `rl_interrupt` clears `execBoundary` as well as turning the indicator
   off.  That gives p.50's *"Further interruptions cannot occur until
   either the system is enabled or another execution operation is
   completed"* for free: one pulse, one interruption, highest-priority
   masked indicator.  This is a **different** guard from the existing
   `!isValid(intPC)`, which is about the in-flight interruption
   instruction, and both are needed.

Note what must *not* change: the interruption still requires the mask
bit (p.50's programming note is explicit), so `pending = indicators &
mask` stays.  And `irqEn` itself is untouched — the machine is still
disabled when the routine is entered, which is why the deck's landing
word `I62ITE` is a `BD` and why the interrupt routine can be a
disabled-state one.

### 2.6 Interaction with the interruption-timing change of 2026-09-25

`git log -1 41fe5fe` moved the interruption boundary from "the E-box's
charged budget has drained" to "the instruction is functionally
complete", by deleting `ebusy == 0` from `armInterrupt`.  Exception 2's
boundary is the **execution operation's** completion — and in this model
that is the same edge: `resume()` returning `tagged Valid` is what
retires the operation, and `armInterrupt`'s structural conditions
(`la.count()==0 && !ebox.busy() && ibusy==0`) are what the 2026-09-25
change left as the definition of "complete".  So exception 2 rides the
fixed boundary rather than needing a new one.  Without that fix,
`execBoundary` would have had to survive an unbounded `ebusy` drain and
the one-shot would have been much harder to get right.

One consequence worth writing down: `rl_interrupt`'s `ebusy <= eb;`
line — flagged in `docs/NEXT.md` §3 as necessary but untested — acquires
a second caller under exception 2 and is still untested by anything in
the suite.  The `CYCLES<=` benchmarks never enable the interruption
system; a disabled-state interruption would be the first thing that
could exercise it, and a `CYCLES<=` bound on a 1CA-shaped program would
be the discriminator.

### 2.7 Size estimate, honestly

* **Exception 1: small.**  One `Reg#(Bool)` in `mkEBox`, one new
  `StretchStorage` method, one changed line in `protViolates`, plus the
  wiring in `StretchCore`.  Call it 20–30 lines across three files, no
  interface reshaping, no change to `execute()`'s signature.  The ~30
  `protViolates` sites change behaviour *collectively* and none change
  textually.
* **Exception 2: medium.**  A second latched output in
  `StretchStorage`'s `intDueCalc`, a term in `armInterrupt`, a clear in
  `rl_interrupt`, and the `execBoundary` register and its plumbing.
  Perhaps 40–60 lines — but it touches the two predicates this project
  has already measured once and been surprised by, so the cost is in the
  regression run and the discriminating tests, not in the lines.  The
  E-box interface does **not** need reshaping: everything hangs off
  `held`'s existing lifetime.
* **The carve-out: zero, until `EXIC`.**

### 2.8 What could go wrong

* **`intDueCalc` ungated is a scheduling hazard.**  Its comment records
  that reading `indicators`/`mask`/`interruptionAddress` from a rule
  while the exported `writeWord` also writes them produced bsc `G0095`,
  and that `mkConfigReg` is what broke the loop.  A second output from
  the same rule is safe; a second *rule* would not be.  Add the output,
  not a rule.
* **The one-shot can be swallowed.**  If `execBoundary` is set on a
  clock when `armRecover`, `ioPending` or `pendingIdxWrite` is also
  valid, `armInterrupt` is false and the pulse must survive to the next
  clock.  A register cleared only by `rl_interrupt` does survive; a wire
  or a `mkDWire` would not.  This is the single most likely bug.
* **Exception 2 must not leak into the ordinary enabled path.**  If
  `execBoundary` is left set after an *enabled* execution operation, the
  next disabled instruction could interrupt.  Clearing it in
  `rl_interrupt` covers the taken case; it also needs clearing when the
  system is enabled and `intDue` fires normally, or simply on any
  `rl_interrupt` firing — which is what is proposed.
* **Exception 1 widens `DF`/`IF` suppression while disabled.**  A
  masked-on `DF` inside a subject instruction now suppresses where it
  previously did not.  That is correct per p.45 items 20/21, but it is a
  behaviour change reachable by existing programs that run `EX` with
  boundaries set, and `ex_monitor.strap` is the program most likely to
  move.
* **p.52's last paragraph is still not modelled**, and exception 1 makes
  it reachable: *"The occurrence of an alert of Class S during a
  transmission in TRANSMIT or SWAP or during the execution of a subject
  instruction of EXECUTE or EXECUTE INDIRECT AND COUNT may not cause
  full suppression of the instruction."*  Exception 1 is what makes such
  an alert happen while disabled.  Out of scope, but it moves from
  "unreachable" to "reachable and unimplemented".

---

## 3. QUESTION 3 — yes, the deck tests both, and it is a precise oracle

`docs/NEXT.md` §4a's block map puts TEST 1C at PDF pp.92-94, entry
`16218`, octal 023442.40-023551.00.  The map is right.  1CA and 1CB are
both on **PDF p.92**, entirely outside every transcribed range
(`verify_ax5b_162_test1cc_listing.py` starts at 023474.40; 1262's other
covered ranges are 023373-023442, 023705-024000, 023742-023767,
024136-024151, 024151-024171, 024172-024331).  **1CA, 1CB, 2CA and 2CB
are a genuine gap.**

### 3.1 The block header that sets the state

PDF p.92, first row of TEST 1C:

| label | source | comment | machine code | address |
|---|---|---|---|---|
| `16218` | `BD,$+.32` | `-TEST 1C, CHK MISC CNTRLS OF EX.` | `23443.04 00` | `023442.40` |

`BD` = BRANCH DISABLED.  **TEST 1C opens by disabling the interruption
system**, and the only subroutine it calls before the `EX` is `I60S1`,
which §0(b) establishes returns via `BD`.  No `BE` appears anywhere in
1CA or 1CB.  Every `EX` in TEST 1C runs with the system DISABLED.  (The
listing's comment column prints `1C` as `IC` throughout — the deck's own
typography, transcribed, not tidied.)

### 3.2 TEST 1CA — `023442.40`–`023450.00` — exception 2, directly

PDF p.92, verbatim (machine-code column as printed):

| source | comment | machine code | address |
|---|---|---|---|
| `SIC,160SX1` | `-TEST 1CA, ENABLE AFTER EX.` | `23041.00 80` | `023443.00` |
| `BD,160S1` | | `22741.04 00` | `023443.40` |
| `Z,$IND` | | `13.22 00` | `023444.00` |
| `LVI,$X1,I62INT` | | `24220.03 01` | `023444.40` |
| `SV,$X1,$IA` | | `2.03 30` | `023445.00` |
| `%8@DD%BU,32,8@,3740` | `-ILLEGAL OP CODE.` | `00000003740` | `023445.40` |
| `LVI,$X1,16219` | | `23450.43 01` | `023446.00` |
| `SVA,$X1,I62ITE` | | `24320.03 D0` | `023446.40` |
| `EX,$-.32` | | `23446.52 00` | `023447.00` |
| `SIC,SEN` | `-NO INT TAKEN ON EX` | `1310.00 80` | `023447.40` |
| `BD,SERS` | `-WHEN OP SET.` | `1304.04 00` | `023450.00` |

**How it works, and the point that took the longest to see.**  The
`-ILLEGAL OP CODE.` word at `023445.40` is not an operand and is not the
`EX`'s subject — it is **in the straight-line instruction stream** and is
executed on the way past.  Printed p.45 item 15: *"An instruction with
invalid operation code is executed as NO OPERATION"* and indicator `OP`
(15) is actuated.  `OP` is inside the permanently-masked range 0–19, but
the system is disabled, so **no interruption happens there** — which is
also why the deck can plant its vector *after* the illegal word rather
than before it.

Then `LVI`/`SVA` point the interrupt landing `I62ITE` at `16219` (the
start of 1CB), and `EX,$-.32` executes the harmless `SVA` at `023446.40`
as its subject.  The subject does nothing interesting on purpose: the
whole test is that **at the completion of the execution operation the
already-actuated `OP` must cause an interruption although the system is
disabled.**  Falling through to `SIC,SEN / BD,SERS` reports
`-NO INT TAKEN ON EX WHEN OP SET.`

**The harmless subject is deliberate, not an off-by-one.**  The machine
code `23446.52` puts the subject at `023446.40`, the `SVA` — not the
illegal word three half-words back.  2CA (§3.5) is built the same way
and reaches its subject through `I62PSI` → `I62SUB` ← `I62EXI`, where no
`$-n` off-by-one is even available; two blocks with the same shape is
design, not a shared typo.  The subject is chosen to do nothing so that
the only thing under test is the boundary.  (The pass condition would
not change either way.)

That is p.50's second special exception and the Programming Note's *"Any
actuated indicator whose mask bit is on may cause interruption at the
completion … of an execution operation"*, executable.  It tests the
**disabled-state override**, nothing else.  It does not test exception 1
at all.

`I62ITE` (not `I62ITE+.32`) means the landing is `024320.00`, which
`verify_ax5b_162_test1cc_listing.py` records as `I62ITE BD,$` — so 1CB
is entered still disabled.

### 3.3 TEST 1CB — `16219`, `023450.40`–`023460.00` — exception 1

| label | source | comment | machine code | address |
|---|---|---|---|---|
| `16219` | `LX,$X1,BIT57` | `-TEST 1CB, CHK ADR MONITOR.` | `24613.02 10` | `023450.40` |
| | `SX,$X1,3.0` | | `3.03 10` | `023451.00` |
| | `LVI,$X1,I62EX` | | `24322.03 01` | `023451.40` |
| | `SV,$X1,$UB` | | `3.03 30` | `023452.00` |
| | `LVI,$X1,16220` | | `23456.43 01` | `023452.40` |
| | `SVA,$X1,I62ITE` | | `24320.03 D0` | `023453.00` |
| | `Z,$X1` | | `21.22 00` | `023453.40` |
| | `TI,1,I00O,$MASK` | | `24503.00 80  000014.02 A0` | `023454.00` |
| | `EX,I62EXI` | | `24332.12 00` | `023455.00` |
| | `SIC,SEN` | `-NO INT TAKEN WHEN EX INST` | `1310.00 80` | `023455.40` |
| | `B,SERS` | `-ABOVE UB.` | `1304.10 00` | `023456.00` |
| `16220` | `LX,$X1,$X1` | | `21.02 10` | `023456.40` |
| | `SIC,SEN` | `-INSTRUCTION EXECUTED ABOVE UB WAS` | `1310.00 80` | `023457.00` |
| | `BZXVZ,SERS` | `-NOT NOPED.` | `1304.31 40` | `023457.40` |
| | `Z,3.0` | `-CLR BNDS REG.` | `3.22 00` | `023460.00` |

`BIT57` into word 3 sets the boundary-register control bit;
`SV,$X1,$UB` sets the upper boundary to `I62EX` (`024322`).  `I62EXI` is
at `024332.00` — **above the upper boundary, i.e. protected**.  `Z,$X1`
clears the index register the subject would write; `TI,1,I00O,$MASK`
turns on the relevant mask bit.  Then `EX,I62EXI` — an `EX` whose
subject lies in the protected area, **with the system disabled**.

Required behaviour: p.50 exception 1 keeps address monitoring in force,
so `IF` is actuated; p.45 item 21 (mask bit one) suppresses the subject
entirely; p.50 exception 2 permits the interruption, which lands at
`16220`.  `16220` then checks that the suppressed subject did **not**
write `$X1` — `-INSTRUCTION EXECUTED ABOVE UB WAS NOT NOPED.`  Falling
straight through instead reports `-NO INT TAKEN WHEN EX INST ABOVE UB.`

So 1CB tests **exception 1 as its subject and exception 2 as its
delivery mechanism**, plus the `IF`-mask suppression rule.  It is the
sharper of the two blocks and the one that would fail first.

### 3.4 TEST 1D — `16241`, `023551.40`– — the `USA` oracle, and a *third* exception-2 witness

PDF p.95.  The block loads a count from `USAWD`, then loops at `16242`
storing a chain of `EX`s through `16084A`, counts down with
`CB+,$X1,16242`, patches the chain's end, sets `$IA`, calls `I60S1`
(returns disabled), and then:

| label | source | comment | machine code | address |
|---|---|---|---|---|
| `16241` | `LX,$X1,USAWD` | `-TEST 1D, CHK EXE AND USA INDS.` | `23076.02 10` | `023551.40` |
| | `Z,$IND` | | `13.22 00` | `023561.00` |
| | `Z,$MASK` | | `14.22 00` | `023561.40` |
| | `LVI,$X1,16245` | | `23566.43 01` | `023562.00` |
| | `SVA,$X1,I62ITE` | | `24320.03 D0` | `023562.40` |
| | `EX,16084A` | | `17245.12 00` | `023563.00` |
| `16243` | `BUSA,16244` | | `23565.50 C2` | `023563.40` |
| | `SIC,SEN` | `-2049 SUCCESSIVE EXECUTES FAIL TO SET` | `1310.00 80` | `023564.00` |
| | `BD,SERS` | `-USA AND FAIL TO CAUSE INTERRUPT.` | `1304.04 00` | `023564.40` |
| | `B,$+1.32` | | `23566.50 00` | `023565.00` |
| `16244` | `SIC,SEN` | `-2049 SUCCESSIVE EXECUTES FAIL TO COUSE` | `1310.00 80` | `023565.40` |
| | `B,SERS` | `-INT BUT DO SET USA.` | `1304.10 00` | `023566.00` |

(`COUSE` is the deck's own typo, transcribed.)

Both straight-line paths are error reports: `16243` is reached when `USA`
did not come on, `16244` when it did but no interruption followed.  **The
only pass path is an interruption landing at `16245`.**  `Z,$MASK`
clears the settable mask so nothing but a permanently-masked indicator
can interrupt — and `USA` is indicator 17, inside the permanent 0–19
range.  The system is disabled (`I60S1` returned via `BD`, no `BE`
follows).

So TEST 1D requires **all three** of: `USA` firing on a 2049-level chain
(Q1), the termination proceeding, and p.50's exception 2 delivering the
interruption while disabled (Q2).  Neither piece can be validated by 1D
alone.  That is worth saying plainly: **1D is a second oracle for
exception 2, and the strongest single argument for doing Q1 and Q2 as
one change.**

### 3.5 The `EXIC` twins — TEST 2C, `16271`, PDF p.103

Identical in shape, at `024000.40`–`024016.40`:

| label | source | comment | machine code | address |
|---|---|---|---|---|
| `16271` | `BD,$+.32` | `-TEST 2C, CHK MISC CNTRLS OF EXIC.` | `24001.04 00` | `024000.40` |
| | `SIC,160SX1` | `-TEST 2CA, ENABLE AFTER EXIC.` | `23041.00 80` | `024001.00` |
| | `BD,160S1` | | `22741.04 00` | `024001.40` |
| | `LVI,$X1,I62INT` | | `24220.03 01` | `024002.00` |
| | `SV,$X1,$IA` | | `2.03 30` | `024002.40` |
| | `%8@DD%BU,32,8@,3740` | `-ILLEGAL OP CODE.` | `00000003740` | `024003.00` |
| | `LVI,$X1,16272` | | `24010.03 01` | `024003.40` |
| | `SVA,$X1,I62ITE` | | `24320.03 D0` | `024004.00` |
| | `LVI,$X1,I62SUB` | | `24324.03 01` | `024004.40` |
| | `SVA,$X1,I62PSI` | | `24323.03 D0` | `024005.00` |
| | `LX,$X1,I62EXI` | | `24332.02 10` | `024005.40` |
| | `SX,$X1,I62SUB` | | `24324.03 10` | `024006.00` |
| | `EXIC,I62PSI` | | `24323.16 00` | `024006.40` |
| | `SIC,SEN` | `-NO INT TAKEN ON EXIC` | `1310.00 80` | `024007.00` |
| | `BD,SERS` | `-WHEN OP WAS SET.` | `1304.04 00` | `024007.40` |
| `16272` | `LVI,$X1,I62SUB` | `-TEST 1CB, CHK ADR MONITOR.` | `24324.03 01` | `024010.00` |
| | `SVA,$X1,I62PSI` | | `24323.03 D0` | `024010.40` |
| | `LX,$X1,BIT57` | | `24613.02 10` | `024011.00` |
| | `SX,$X1,3.0` | | `3.03 10` | `024011.40` |
| | `LVI,$X1,I62PSI-1.0` | | `24322.03 01` | `024012.00` |
| | `SV,$X1,$UB` | | `3.03 30` | `024012.40` |
| | `LVI,$X1,16273` | | `24017.03 01` | `024013.00` |
| | `SVA,$X1,I62ITE` | | `24320.03 D0` | `024013.40` |
| | `Z,$X1` | | `21.22 00` | `024014.00` |
| | `TI,1,I00O,$MASK` | | `24503.00 80  000014.02 A0` | `024014.40` |
| | `EXIC,I62PSI` | | `24323.16 00` | `024015.40` |
| | `SIC,SEN` | `-NO INT TAKEN WHEN` | `1310.00 80` | `024016.00` |
| | `B,SERS` | `-EXIC INSTRUCT ABOVE UB.` | `1304.10 00` | `024016.40` |
| `16273` | `LX,$X1,$X1` | | `21.02 10` | `024017.00` |
| | `SIC,SEN` | `-EXIC INSTRUCT ABOVE UB` | `1310.00 80` | `024017.40` |
| | `BZXVZ,SERS` | `-WAS NOT NOPED.` | `1304.31 40` | `024020.00` |

2CA is 1CA with the subject reached through a pseudo-instruction
counter (`I62PSI` → `I62SUB`, loaded from `I62EXI`).

**2CB IS THE CARVE-OUT ORACLE, and sharply so.**  It sets the upper
boundary from `LVI,$X1,I62PSI-1.0`, whose machine code is `24322.03 01`
— the *same* `024322.00` that 1CB sets from `I62EX`.  The block's three
relevant addresses are therefore:

| | address | vs `upper = 024322.00` |
|---|---|---|
| upper boundary | `024322.00` | — |
| `I62PSI`, the **first-level pseudo-instruction counter** | `024323.00` | at/above → protected |
| `I62SUB`, the **subject instruction** | `024324.00` | at/above → protected |

(`protViolates` reads `inArea = (a >= lower) && (a < upper)` and, with
the control bit one, signals *outside* the area — which is what
`LX,$X1,BIT57 / SX,$X1,3.0` sets up, exactly as in 1CB.)

So **both** the subject and the pseudo-IC fall in the monitored region.
The subject must signal `IF`, be suppressed, and interrupt — that is
exception 1, as in 1CB.  The pseudo-IC must **not** signal, because
p.50 exempts *"the address of the location of the first level
pseudo-instruction counter"*.  An implementation of exception 1 that
omits the carve-out raises a spurious `IF` on the pseudo-IC fetch — a
higher-priority actuation than the one the block is looking for — and
2CB fails.  The carve-out is therefore not a detail; it has a deck
witness, in the direction that catches its omission.

The comment column again prints `2CB` as `ICB`.

(`16272`'s block also shows `EXIC,I62PSI` at `024015.40` with no row at
`024015.00` in the address column as printed — read at 400 dpi; the
`TI` above it is a full word at an odd half-word, which is the same
shape `ax5b_160s1_clr_inds.strap` records for `I60S1`'s fifteen `TI`s.)

### 3.6 What this changes about the standard

**It changes it from manual-only to deck-verified, and that is the most
important sentence in this note.**  Before: p.50's two exceptions were a
paragraph with no executable witness, and any implementation would have
been argued from the text.  Now there are four blocks and a fifth
consequence:

| block | PDF | octal | entry | tests |
|---|---|---|---|---|
| TEST 1CA | 92 | 023442.40-023450.00 | `16218` | exception 2 only, with `OP` actuated *before* the `EX` |
| TEST 1CB | 92 | 023450.40-023460.00 | `16219` | exception 1 (via `IF`), delivered by exception 2, plus `IF`-mask suppression |
| TEST 1D | 95 | 023551.40-023576.00 | `16241` | `USA` on a 2049-chain **and** exception 2 |
| TEST 2CA | 103 | 024000.40-024007.40 | `16271` | exception 2 for `EXIC` |
| TEST 2CB | 103 | 024010.00-024020.00 | `16272` | exception 1 for `EXIC`, incl. the first-level pseudo-IC carve-out |

The practical consequence: **1CA is the cheapest of the five to
transcribe and run** — eleven rows, one inline data word, one error
message, and it needs nothing from `EXIC`.  It should be the
discriminating test for exception 2, and it can be written *before* the
implementation in the way `ax5b_16071_ts.strap` was for the interval
timer.  1CB needs the boundary registers and the `IF` mask, both of
which the model already has.  Both need the `SERS`/`SEN` error harness
and `I62ITE`/`I62INT`, which `ax5b_162_test1cc.strap` already stands up.

---

## 4. What I could not settle

* **No single documented per-`EX`-level time exists.**  Table 6's recipe
  has two non-scalar terms ("always begins/ends with Look-ahead drain").
  The 0.3 µs cycle and the 1 ms threshold are documented; the divisor
  for `EX` is a bound (~110–160 levels/ms), not a number.  For `LVE` it
  *is* a number (4.8/3.6/3.0 µs → 208/278/333 levels/ms).
* **Why 2049.**  It is comfortably above any threshold the numbers
  support and is presumably 2048+1.  I found no statement of why, and
  `USAWD` (the count word, at `023076` per `LX,$X1,USAWD`) is outside
  every page I read.  Conjecture, flagged as such.
* **The exact contents of `I62EXI`, `I62SUB` and `I62PSI`.**
  `docs/NEXT.md` records `I62EXI LVI,$X1,%8@777777.40` at `024332.00`
  from PDF p.110; I did not re-verify it at 400 dpi, and I did not
  locate `I62SUB`/`I62PSI` in the constants area.  1CB's and 2CB's
  behaviour depends on `I62EXI` being an instruction that writes `$X1`
  (the `BZXVZ` check), which `LVI,$X1,…` satisfies.
* **Whether `EXE` (indicator 18) interacts with exception 2.**  TEST 1D
  is titled "CHK EXE AND USA INDS" and its second half (from `16245`,
  PDF p.95) tests `EXE` with another inline illegal-op word; I did not
  read past `16245`'s first rows.
* **The look-ahead drain cost.**  If `USA` is implemented as (1) in
  §1.5, the per-level charge needs the drain modelled or bounded.  The
  model's `iboxHazard` already drains for unconditional branches; what
  an `EX` costs in drain clocks here is not documented anywhere I found.
* **I did not run anything.**  No `bsc`, no `run_tests.sh`, no
  `run_program.sh`, no `mutation_score.py`.  Every behavioural claim
  about the model is read from source, not observed.

---

## 5. Sources, by page

| claim | source | printed page | PDF page |
|---|---|---|---|
| `USA` definition, "one millisecond (several hundred indirect addressing cycles)" | Reference Manual 22-6530-2 | 45 | 48 |
| `EXE` definition, "the subject operation was suppressed" | Reference Manual | 45 | 48 |
| `OP` "executed as NO OPERATION"; `IF` mask-one suppression | Reference Manual | 45 | 48 |
| Execution instructions; the `EXE` rule; IC never stepped for a subject | Reference Manual | 49 | 52 |
| p.50's two special exceptions and the Programming Note | Reference Manual | 50 | 53 |
| `EX`/`EXIC` operation spec; `EX`'s below-32.00 monitoring carve-out | Reference Manual | 50 | 53 |
| Execution Suppressed item 3; "pseudo-instruction counters … will have been stepped" | Reference Manual | 52 | 55 |
| Class S during a subject instruction "may not cause full suppression" | Reference Manual | 52 | 55 |
| **"basic machine cycles, which is presently 0.3 microsecond"** | Perf. Characteristics Vol.1, Mar 61 | 3-2 | 20 |
| Table 4: `LVE as object INSN of LVE` — additional 4.8 / 3.6 / 3.0 µsec | Perf. Characteristics Vol.1 | 3-11 | 29 |
| Table 6: `EX` six-term recipe and its fetch-time address table | Perf. Characteristics Vol.1 | 3-12 | 30 |
| Table 6 cont.: `EXIC` pseudo-IC fetch and stepping times | Perf. Characteristics Vol.1 | 3-13 | 31 |
| TEST 1C header, 1CA, 1CB | `jb_ax5b_ibox-5.pdf` | — | 92 |
| TEST 1D | `jb_ax5b_ibox-5.pdf` | — | 95 |
| TEST 2C header, 2CA, 2CB | `jb_ax5b_ibox-5.pdf` | — | 103 |
| `I60S1` returns via `BD` | `strap/programs/ax5b_160s1_clr_inds.strap` header (from `jb_ax5b` PDF p.85) | — | 85 |
