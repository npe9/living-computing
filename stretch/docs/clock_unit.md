# The clock unit: G1.0

Written 2026-11-08 for `docs/source_audit.md` goal G1.0. No model file was
changed. Every number below was read from a page image (`pdftoppm -r 110
-gray`, higher where stated), not from `docs/ocr/`. Pages are given as printed
page and PDF page. CE manual pages also carry their section tag (M3-04-n).

## 1. The answer

**The three units are one clock with three names. Inside the CPU:**

| name | value | what it physically is |
|---|---|---|
| "basic machine cycle" (Perf. Char.), one trigger cycle (CE manual), one model clock | **0.3 µs** | one A-or-B pulse slot, one FP CLOCK period |
| "clock cycle" (Buchholz p.209), I-box control cycle, SAU byte cycle | **0.6 µs** | A to next A, two slots |
| master oscillator frequency as shipped | **about 3.33 Mc, inferred, not printed** | see §6 |

"One phase", the audit's factor of two, resolves to **one A-or-B pulse = 0.3 µs,
and an A+B pair = 0.6 µs**.

**The model's clock already means the right thing: one clock = one pulse slot =
0.3 µs.** No budget needs rescaling. What the model lacks is the *phase* of the
slot, and that is cheap and mostly unneeded today (§7).

**Confidence.** High for the CPU's 0.3/0.6 structure: four independent routes
agree (§4). The exact period is only known as nominal: the frequency was
adjustable and no page read gives it as a number (§6). Bloch's denial is true of
the machine as a whole: memory, Exchange, disk and the timer are not on this grid
(§5).

## 2. What earlier work had settled

Nothing had settled it, but the parts were present.

* `execution_operations.md` §1.2, `spec_timing.md`, `timing_oracle.md` and
  `perf_char_timing.py` cite 0.3 µs correctly to Perf. Char. p.3-2.
* `microarchitecture_plan.md` §3 asserts "one clock = one E-box cycle = 0.3 µs"
  and I-box stages every 2 clocks. `NEXT.md:1560` correctly records that the
  ratio was stated by no source it had read. §4 supplies the source.
* `ebox_roadmap.md:829` found "300 nanoseconds" on the CE manual's Fig 3.8.15.
  `ebox_roadmap.md:843` then refused to connect STORE ROOT's A PULSES to its time
  because no ratio was known. §4.4 supplies the ratio.
* `web_references.md:47` holds a secondary source's 600 ns as an open
  discrepancy. It is the A-to-A interval, not a discrepancy.

## 3. Pre-registration

Written to a scratch file before the table was built. **It was not blind.** I had
already read Blosk p.23; CE Figs 2.8.1, 2.10.1, 3.8.2, 3.8.9, 3.8.10, 3.8.15
sheet 3 and 4.1.1-4; Table 2.1.1's first sheet; Perf. Char. pp.3-2 and 3-5; and
Buchholz p.209. The remaining tables had not been tabulated.

**The numeric test is one-sided.** It can reject a unit that is too large or
incommensurate. It can never reject a divisor of the true unit, since 0.15 and
0.1 pass whenever 0.3 passes. And times are printed to 0.1 µs, so 0.1 passes
nearly everything by typography alone. Only the physical drawings can reject a
smaller unit.

| outcome | claim | prediction | if true |
|---|---|---|---|
| O1 | 0.3 = one A-or-B slot, 0.6 = A+B | CPU times all multiples of 0.3; odd multiples exist (FP); I-box and SAU tables even; A-to-A 600 ns | model clock correct |
| O2 | 0.3 = A+B pair, slot = 0.15 | SAC period 300 ns; "+1 cycle if began with B" would have to be half a cycle | model clock is two slots; needs doubling |
| O3 | 0.6 fundamental | no odd multiples of 0.3 anywhere | model clock is half a real cycle |
| O4 | Blosk's 0.25/0.5 survived into the shipped machine | printed times multiples of 0.25 | every budget mis-scaled |
| O5 | no common unit inside the CPU | CPU tables off every grid | G1.0 becomes per-unit |
| O6 | O1 inside the CPU, other units on separate clocks | Exchange, disk, timer off the 0.3 grid | single clock right for the CPU only |

**Result: O1 and O6 together. O2, O3, O4, O5 rejected.** One printed number,
Table 6's 11.2 µs, matches no outcome (§5.1).

## 4. The physical evidence: four routes

### 4.1 The drawn clock (rejects O2)

CE manual M3-04-2, **Fig 2.10.1, printed 10-3, PDF 47**, dated 1/1/63: `SAC 1`
with a dimension line **"600 NSEC"** from one rise to the next and a pulse width
**"150"**, and `SBC 2` interleaved. CE Vol. 3 Appendix D, printed p.132 (PDF 132):
SAC is "Sample A Controlled Pulses", SBC "Sample B Controlled Pulses".

Re-derived by measuring the figure, since a labelled dimension can be a nominal.
At 300 dpi the figure's printed scale, 1/16" = 50 ns, gives 18.75 px per 50 ns.

| interval | px | ns by printed scale |
|---|---|---|
| A rise to A rise (three) | 226.5, 229, 229.5 | 604, 611, 612 |
| A rise to following B rise, 2nd and 3rd pairs | 115, 112.5 | 307, 300 |
| A rise to following B rise, **1st pair** | 94 | **251** |
| A width, B width | 57-61 | 152-163 |

The first B pulse is drawn early. The other two pairs are the 300 ns that
symmetry predicts, and Blosk p.23 calls the waveform symmetrical. This is a
drawing, so A-to-A 600 is the firm number and A-to-B 300 is the measured
inference. Fig 2.8.1's "DELAYED SBC 250 NSEC" (printed 8-3, PDF 43) is a delayed
pulse measured from a read request, not an A-to-B figure.

Fig 2.8.1 and Fig 2.10.1 also draw a 600 ns read request and a 1200 ns write
address in index storage, matching Buchholz printed p.19 (PDF 44): index memory
read 0.6 µs, clear-and-write 1.2 µs.

The console agrees that A and B are single consecutive pulses: "1 PULSE ...
either an A or a B pulse", "2 PULSE ... either A and B or B and A", "3 PULSE ...
either ABA or BAB" (M3-04-3 printed 5-9, PDF 196).

### 4.2 One cycle is one pulse (rejects O2 and O3)

Perf. Char. Vol. 1 **Table 2, printed 3-5, PDF 23**, STORE ROOT execution: **"1
cycle if operation began with a 'B' pulse."** A B-start penalty of a whole cycle
means the wait for the next A is one cycle, so a cycle is one slot. Under O2 this
would be half a cycle.

Table 2 (printed 3-3 to 3-5, PDF 21-23) has odd counts throughout: 1, 3, 5, 15,
17 cycles. A sequence of floating adds is 4 + 1 = 5 cycles, and printed 3-17 (PDF
35) independently says one word per **1.5 µs**, which is 5 × 0.3 and is not on
the 0.6 grid. That rejects O3.

Printed 3-2 (PDF 20): "the basic machine cycles, which is presently 0.3
microsecond." CE M3-04-3 **Fig 3.8.15 sheet 3, Note 2, printed 8-19, PDF 241**:
turning TC on with END OP "shortens the operation by 300 nanoseconds", and TC
occupies one FP CLOCK period on that chart. So FP CLOCK's numbered periods (8-2,
8-8, PDF 226, 232) are 0.3 µs each and ring triggers step every slot.

### 4.3 The A+B pair is the control cycle

Blosk TR00.722 **printed p.23, PDF 25**, as designed: an E trigger turns on at an
A pulse, its M trigger at the next B, and the entire cycle "is twice the period of
the clock, since A and B pulses arrive alternately from the master clock in a
symmetrical sequence"; "a control cycle should take approximately 500 mµs", "four
Mc ... with a period of 250 mµs".

This is the source for "one I-box control cycle = 2 clocks". Its shipped value:
every I-box entry on pp.3-11 to 3-14 is a multiple of 0.6 bar one (§5.1), decode
is 0.6 µs (printed 3-18, PDF 36), and Blosk's index storage cycle "approximately
500 mµs" (printed p.11, PDF 13) shipped as Buchholz's 0.6 µs (printed p.19). So
design to shipped scaled 250 to 300 ns and 500 to 600 ns, ratio preserved.

Same structure in the serial unit: Buchholz **printed p.209, PDF 234**, one byte
pair handled "in one clock cycle of 0.6 µsec"; Table 3 charges .6 per byte
(printed 3-7, PDF 25).

### 4.4 STORE ROOT closes the sum (second route, and it undoes a hold)

CE M3-04-3 **Fig 3.8.10, printed 8-9 and 8-10, PDF 233-234.** Sheet 1's left panel
runs on FP CLOCK, its right panel on **A PULSES**: one A pulse per F REG LATCH
pulse, one root bit per pulse, SCR set to 96 and counting 96, 94, 92 ... 0.
Perf. Char. Table 2 gives 2 + 106 = 108 cycles (printed 3-5).

`ebox_roadmap.md:843` calls A PULSES "a separate and faster waveform" with no
known ratio. They are drawn tighter, but the two panels are not to one scale, and
§4.1 now gives the ratio: A to A is two cycles.

| reading of A period | 48 root bits | rest to reach 108 |
|---|---|---|
| **2 cycles (0.6 µs)** | 96 | **12** |
| 1 cycle (0.3 µs) | 48 | 60 |

What the chart draws for those 12, counted by hand:

| item | cycles |
|---|---|
| sheet 1 left: T0, T3, T4 | 3 |
| sheet 2: TX, T4, T3, TC/T4 | 4 |
| two more A periods: SU SSQ, and the unnumbered first F REG LATCH | 4 |
| "B TIMED SCR=0" hand-back to PAU control: A to B | 1 |
| **total** | **12** |

So the chart sums to exactly 108. **Treat the exact closure as suggestive**: I
chose which items count, knowing the target. The firm result is the gap: 12
against 60, with 7 charted FP periods. It also explains the "B" row: the SAU runs
on A pulses, so entry from a B slot waits one slot, which is Table 2's +1.

The memory path gives a further route (§5.2): under 0.6 or 0.15 the SP pulse
count contradicts printed read times.

## 5. The table

Whole-multiple test. A cell reads "all", or passes/total. Inputs are printed
figures, and n counts the distinct values in that class, not table cells. FP Table
2 is omitted because it is printed in cycles, not µs, so testing it would be
circular.

| class | source (printed page) | n | 0.6 | 0.5 | **0.3** | 0.25 | 0.2 | 0.15 | 0.1 |
|---|---|---|---|---|---|---|---|---|---|
| Table 3 pre, term, fixed | Perf 3-7 to 3-9 | 9 | 8/9 | 3/9 | **all** | 3/9 | 8/9 | all | all |
| Table 3 full-word totals | Perf 3-7 to 3-9 | 15 | 12/15 | 4/15 | **all** | 4/15 | 12/15 | all | all |
| Table 4 direct index | Perf 3-11 | 12 | all | 3/12 | **all** | 3/12 | all | all | all |
| Table 5 immediate | Perf 3-11 | 6 | all | 1/6 | **all** | 1/6 | all | all | all |
| Table 6 misc, less 11.2 | Perf 3-12, 3-13 | 11 | all | 2/11 | **all** | 2/11 | all | all | all |
| **Table 6, 5.0 → 11.32** | Perf 3-12 | 1 | 0/1 | 0/1 | **0/1** | 0/1 | all | 0/1 | all |
| Table 7 branch | Perf 3-13 | 6 | all | 1/6 | **all** | 1/6 | all | all | all |
| Table 8 index branch | Perf 3-14 | 9 | all | 2/9 | **all** | 2/9 | all | all | all |
| Table 9 transmit | Perf 3-14 | 6 | all | 1/6 | **all** | 1/6 | all | all | all |
| decode rates 1.2, 3.6, .6 | Perf 3-17, 3-18 | 3 | all | 0/3 | **all** | 0/3 | all | all | all |
| FP add demand 1.5 | Perf 3-17 | 1 | 0/1 | all | **all** | all | 0/1 | all | all |
| drawn 600, 1200 ns | CE 8-3, 10-3 | 2 | all | 0/2 | **all** | 0/2 | all | all | all |
| Note 2, 300 ns | CE 8-19 | 1 | 0/1 | 0/1 | **all** | 0/1 | 0/1 | all | all |
| index memory .6, 1.2 | Buchholz 19 | 2 | all | 0/2 | **all** | 0/2 | all | all | all |
| bus rate .3 | Buchholz 206 | 1 | 0/1 | 0/1 | **all** | 0/1 | 0/1 | all | all |
| SAU clock cycle .6 | Buchholz 209 | 1 | all | 0/1 | **all** | 0/1 | all | all | all |
| CSU Busy 1800 ns | CE 1-3 (M3-04-4) | 1 | all | 0/1 | **all** | 0/1 | all | all | all |
| memory cycle 2.1 | Buchholz 202 | 1 | 0/1 | 0/1 | **all** | 0/1 | 0/1 | all | all |
| memory read 1.6 | Buchholz 206; Bloch 58 | 1 | 0/1 | 0/1 | **0/1** | 0/1 | all | 0/1 | all |
| interleave 2.2, 4.4 | Perf 3-17 | 2 | 0/2 | 0/2 | **0/2** | 0/2 | all | 0/2 | all |
| data-out gate ≥ 1050 ns | CE 1-4 (M3-04-4) | 1 | 0/1 | 0/1 | **0/1** | 0/1 | 0/1 | all | 0/1 |
| Exchange 1.0 cycle | Perf A-6 | 1 | 0/1 | all | **0/1** | all | all | 0/1 | all |
| Exchange pulse 0.1 | Perf A-6 | 1 | 0/1 | 0/1 | **0/1** | 0/1 | 0/1 | 0/1 | all |
| Exchange 10, disk 8 µs | Perf A-6 | 2 | 0/2 | all | **0/2** | all | all | 0/2 | all |
| timer 976.5625 µs | Ref. Man. 34 (PDF 37) | 1 | 0/1 | 0/1 | **0/1** | 0/1 | 0/1 | 0/1 | 0/1 |

Reading it: 0.25 and 0.5 fail almost all CPU rows (O4 rejected). 0.6 and 0.2 fail
on 3.9, 1.5, the bus rate and Note 2 (O3 rejected; 0.2 also on the CPU). 0.3 is
the largest unit passing every CPU row but one. 0.15 and 0.1 pass by the
one-sidedness of §3, so the table cannot reject them. §4.1 and §5.2 reject 0.15. 0.1
appears in print only as the Exchange's own pulse.

### 5.1 Entries needing a note

* **11.2 µs, Table 6's EX fetch time for addresses 5.0 → 11.32, printed 3-12, PDF
  30.** Re-read at 300 dpi: it is 11.2. 37⅓ × 0.3. It matches none of the
  pre-registered outcomes. Every other entry in Tables 4-9 is on the 0.6 grid, so
  it looks like a printing or arithmetic error, with 10.8 and 11.4 the nearest
  grid values. Nothing printed confirms that, and I have not corrected it.
* **14.7 and 45.3, Table 3 full-word totals (printed 3-8).** Odd multiples of 0.3,
  but they are computed from equations with t/4 and u/8 terms; the column heading's
  gloss on printed 3-6 calls the total "a computed time". Not clock counts.
* **3.9 and 10.5, printed 3-9.** VFL multiply: execution 3.9 = 13 cycles, total 6.0
  + 3.9 + .6 = 10.5. These are legitimately odd, consistent with the parallel unit
  stepping per slot.

### 5.2 Memory is off the grid, and sampled onto it

Buchholz printed p.202 (PDF 227): each memory unit "has its own clock". So 1.6 and
2.2 being off-grid is expected rather than a failure. The CPU then samples the
result on its own pulses. CE M3-04-4, printed 1-4, 1-5, 1-8, PDF 275, 276, 279:

* IMOB data at 1Y and at LA level 4 "should bracket (overlap) the sixth SP pulse"
  after the one that initiated gate I (Fig 4.1.1, pulses numbered 0-6).
* SEL 1Y and SEL 2Y bracket the fifth and sixth SP pulses (Figs 4.1.2, 4.1.3).
* MEM SEL LA brackets the fifth (Fig 4.1.4).

SP is 0.3 µs by this chain: printed 1-2 (PDF 273) locates the SP pulse at
11A2K24F; Table 2.1.1 (M3-04-2, printed 1-3, PDF 18) types that point **ABAB**; Vol. 3
printed p.128 expands ABAB as "Free Running AB Pulses". The same table has an
"ABAB -180" type, and printed 1-2 places the memory-select pulse 150 ns after SP's
leading edge, which is half of 300.

**Test, re-derived a second way:** five and six pulses should bracket the printed
read time.

| SP period | 5th to 6th pulse | against printed 1.6 µs, and ≥1050 ns data-out | |
|---|---|---|---|
| 0.6 | 3.0 to 3.6 µs | twice the printed read | rejected |
| **0.3** | **1.5 to 1.8 µs** | **brackets 1.6** | **fits** |
| 0.15 | 0.75 to 0.9 µs | data earlier than the 1050 ns data-out floor | rejected |

The caveat is that gate I's relation to the bus request is not worked out here.

### 5.3 Reconciling the sources

* **Bloch printed p.58, PDF 11 (Dec 1959):** "There is no such thing, since the
  individual units of the computer operate asynchronously. However, each unit has a
  clock which has a cycle anywhere between 200 and 300 millimicroseconds." He is
  right as to the system, and 200-300 is the *slot*, not the A+B pair. It brackets
  Kolsky's 1959 notes, Blosk's design and the shipped machine.
* **Kolsky, "Timing in Sigma", 27 Feb 1959, handwritten, `chm/102635057.pdf` p.1,
  attribution per the catalogue:** I-box 0.4, look-ahead 0.2, memory bus 0.2 µs, "all
  in synchronism"; VFL cycle 0.45 "not in synchronism"; floating point "no cycle as
  such". An earlier design, cited only as history: same 2:1 I-box ratio, on a 0.2
  slot. The "not in synchronism" VFL explains why the denial was fair in 1959.
  By shipment the SAU charges a 0.6 multiple and runs on A pulses (§4.4).
* **Johnson, printed p.4, PDF 10:** "no arbitrary machine cycle to which the timing
  of various tasks is subservient", and also "considerable use of a master clock and
  of the synchronous circuit mode". Procedural asynchronism over a common clock.
* **Buchholz printed p.204, PDF 229:** units "each one controlled by its own clock
  system, which in turn is synchronized by a master oscillator". True of the CPU's
  units. It sits awkwardly with the Exchange's 1.0 µs, which is not a multiple of 0.3.
  No page read says how the two relate, so `exchange_and_io.md`'s open item 2 stays
  open.

## 6. What the evidence does not settle

* **The exact period.** Perf. Char. p.3-2 says "presently"; CE M3-04-4 printed 1-1
  (PDF 272) requires re-adjustment "whenever the CPU clock frequency is changed", and
  AXXB (printed 5-9) slows controlled pulses to a third. So 300 ns is nominal.
  Alignment tolerance is ± 10 ns (printed 1-1 of M3-04-2, PDF 15), and that is
  alignment, not period. The October 1962 letter at PDF 17 says machines vary
  slightly in timing, about a delay value. `oscPulseDenom`'s exact 78125/24 is
  therefore more exact than its input; it is a sound divider on a nominal number.
* **The oscillator frequency as a number. Scope of this negative:** no page read in
  the ink gives it, and a regex sweep of the OCR of R23-9732, R23-9695, Perf. Char.
  Vol. 1, the Reference Manual, Buchholz and Blosk for Mc/megacycle/frequency found
  none for the 7030 as shipped. That is an OCR sweep, not 297 page images. The ALD
  pages for the clock (11.04.xx, 11.07.xx, 11.12.xx, per Table 2.1.1) would hold it
  and are not in the corpus as far as I found. The CHM collection was not swept;
  only `102635057` was read.
* **Whether A or B comes first at reset.** Index entries for START SYNC A/B and B
  NEXT clock triggers exist (OCR of PDF 169, finding aid only, not read in the ink).
* **Look-ahead counts.** The unit is settled, the count is not. One E or M trigger
  time is 0.3 and an E+M stage 0.6 for a control stage per Blosk p.23. Whether the
  thirteen LA timers' columns are sequential is still the question the audit left;
  this document does not license "two triggers = two cycles" for them.

## 7. What the model's clock is today, and what would change

**Today.** `rl_clock` steps `clk` once per Bluespec clock (`StretchCore.bsv:537`).
`budgetClocks = 2 * iboxCycles + eboxClocks` (`StretchTiming.bsv:267`): I-box tables
in 0.6 units, doubled; FP and SAU in 0.3 units. `memCycleClocks = 7`, `memReadClocks
= 5`, bus one request per clock (`StretchMemory.bsv`). The header comments and
`run_tests.sh:9132` state 0.3 µs. Of the CYCLES checks, `run_tests.sh:8624` has a
real unit in it (3334 clocks = 1 ms); `145`, `142` and `421` are tripwires with no
printed figure. All of them are correctly denominated.

**The unit: nothing changes.**

**Gaps this finding names, none blocking, none done here:**

1. **No phase.** Nothing in the model knows A from B. `clk[0]` would carry it; which
   parity is A is free (§6). The only printed consequence in Tables 2-9 is STORE
   ROOT's +1 (all of printed 3-3 to 3-14 read for this): `eboxClocks` charges a flat
   108, the A-start case.
2. **Stage alignment, inference only.** Blosk p.23 starts control stages on A. After
   an odd-length FP operation the model may dispatch on an odd `clk`. A faithful I-box
   might wait one slot. No page prints a figure for this, so it should wait for M2 and
   a Vol. 2 atlas comparison rather than be charged on inference.
3. **M3 questions, not unit questions.** CSU Busy is 1800 ns, 6 slots (CE 1-3), against
   Buchholz's 2.1 µs cycle (7) and Perf. Char.'s four words per 2.2 µs (printed 3-17).
   The model uses 7. And the model has one read latency, 5, where the CE manual has LA
   at the 5th SP pulse and 1Y at the 5th-6th.
4. **Off-grid units.** If Exchange or disk are ever timed, they need rational dividers
   like the oscillator's: 1.0 µs = 10/3 clocks, 8 µs = 80/3. `StretchIO.bsv` today moves
   one word per core clock and claims no such timing.

**Docs that should change when someone is next in them** (not edited, per this task's
scope):

* `StretchTiming.bsv:17`, `microarchitecture_plan.md` §3: "2 clocks" now has a source,
  Blosk printed p.23 plus CE printed 10-3.
* `NEXT.md:1560`: answered, as above.
* `ebox_roadmap.md:843, 859`: A PULSES are not faster than FP CLOCK. A to A is 2 cycles.
* `exchange_and_io.md:1533-1537`: the digit is legible, **1.0**, and the page is printed
  **A-6** (PDF 65). This file and `disk_subsystem.md` cite p.A-5 for the same paragraph;
  check each before changing it.
* `source_audit.md` G1.0 and `web_references.md:47`: close, pointing here.
* `microarchitecture_roadmap.md:228` is unaffected: sub-cycle delays still have nowhere
  to live in a rule firing.
