# The timing oracle: `StretchTiming.bsv` measured against IBM's own figures

Status: survey and comparison, 2026-10-16. Read-only session; no model
file was changed. Every IBM figure below is cited by **printed** page.

This note answers one question: how far is the model's time model from
cycle accuracy, measured against IBM's measured numbers rather than
against itself. The short answer is in §4.

---

## 0. The sources, and the page-number map

Two documents, both in `stretch/docs/`:

- **Vol. 1** `7030_Performance_Characteristics_Vol1_Mar61.pdf`, 71 PDF
  pages. Section 3 "Execution Times" (printed 3-1 … 3-14) holds Tables
  2-9: the *analytic* E-box and I-box time equations. Section 4
  "Computational Performance" (printed 4-1 … 4-9) holds whole-program
  measured times and Table 10.
- **Vol. 2** `7030_Performance_Characteristics_Vol2_Mar61.pdf`, 189 PDF
  pages. Printed pp.1-33 are STRAP source listings of four programs.
  **Printed pp.34-186 are the measured per-operation timing tables** —
  this is the oracle, and it is what `docs/microarchitecture_plan.md`
  still lists as "planned (5)".

`StretchTiming.bsv`'s header cites Vol. 1's Tables 2-9 and Blosk. It
does not cite Vol. 2. **Vol. 1's tables are IBM's design equations;
Vol. 2's tables are IBM's measurements of the built machine.** Where
they disagree, `AGENTS.md`'s own rule ("the 1961 Performance
Characteristics (measured on the built machine) wins for timing")
points at Vol. 2 — and they do disagree, sometimes by 4×  (§3.6).

**PDF ↔ printed page offset drifts** in Vol. 2, because the preface
pages are lettered 34A-34D. Anchors measured this session:

| PDF page | printed page | offset |
|---|---|---|
| 6 | 3 | +3 |
| 37 | 34 | +3 |
| 73 | 66 | +7 |
| 83 | 76 | +7 |
| 105 | 98 | +7 |
| 109 | 102 | +7 |
| 112 | 105 | +7 |
| 117 | 110 | +7 |

Vol. 2's text layer is OCR of a line printer and is unusable for the
tables — columns interleave and digits corrupt. Every figure in this
note was read off a rendered page image (`pdftoppm -r 170`), not off
`pdftotext`.

---

## 1. What is actually in the oracle

### 1.1 Method (printed pp.34, 34A, 95)

A subroutine **GENER** builds a 1000-instruction sequence from a short
pattern, closes it with a count branch, runs it ten times, and scales
the elapsed interval-timer reading to microseconds per million
instructions (printed p.34). Printed p.100 states "Each time
measurement may have an error on 0.01 µs" — i.e. **1/30 of a 0.3 µs
machine cycle.**

Two methodological facts that govern how the numbers may be used:

1. **These are average instruction times in a steady-state homogeneous
   loop** (printed p.95: "The printed output is actually the average
   instruction times"), i.e. *throughput under look-ahead overlap*, not
   isolated latency. For a subject instruction embedded in a different
   background, p.95 gives the subtraction
   `t_A = (n+1)·t_AV − n·t_B`.
2. **Forwarding is a property of the page, not a column.** Page titles
   read "WITH FORWARDING OF EXTERNAL AND I-BOX OPERANDS" (p.66) or
   "NO FORWARDING" (p.110); p.34C records that non-forwarding cases
   cycled four consecutive addresses while forwarding cases reused one.

### 1.2 Layout

| printed pp. | content | cross-classification |
|---|---|---|
| 34, 34A-34D | GENER method; floating-point method and commentary | — |
| 35-94 | **Floating point**, one page per operation × condition | `NO INDEXING`/`INDEXING` × `INTERNAL`/`EXTERNAL`/`I-BOX OPERAND`; rows = data cases (`NORMALIZED 1.`, `BOTH OPERANDS WITH XPFN`, `AC EXPNT N. MEM EXPNT XPFN`, `AC WITH XPFP. MEM WITH XPFN`) × sign/normalisation (`(N)`, `NEG (N)`, `A(N)`, `NEG A(N)`, `(U)`, `NEG (U)`, `A(U)`, `NEG A(U)`) |
| 95-97 | **Environmental timing** — subject instruction in 1-8 unnormalised add/multiply backgrounds | background depth |
| 98-100 | **Transmit** | `EXTERNAL`/`INTERNAL`/`I-BOX` source × same destination; rows 1,3,5,7,9,11,13,15,50,100 words |
| 101-103 | **Index arithmetic** (the I-box instructions) | `EXTERNAL`/`INTERNAL`/`INDEX OPERAND`, each `DIRECT`/`EFFECTIVE`, plus `IMMEDIATE` |
| 104-105 | **Branches** | `NO INDEXING`/`BRANCH ADDRESS INDEX` × `SUCCES`/`UNSUCC` × `CONSEC`/`NONCON` |
| 106-186 | **VFL** | `NO INDEXING`/`INDEXING` × `EXTERNL OPERAND`/`EXTERNL WB XOVR`/`I-BOX OPERAND`/`INTERNL OPERAND`/`INTERNL WB XOVR`; rows = field specs `(BU,1,8)` … `(D,64,4)`; page titles add forwarding, direct/indirect addressing, offset, and instruction alignment |

`DIRECT`/`EFFECTIVE` means unindexed/indexed. Corroboration: the p.101
commentary says the instructions "were timed with external, internal
and index operands both with and without indexing of the operand
addresses", which is exactly two sub-columns per operand class; and
the `EFFECTIVE − DIRECT` difference is a uniform +0.60 µs = one I-box
control cycle.

### 1.3 How many data points

Counted, not estimated: **printed p.66 carries 192 filled cells**
(4 blocks × 8 rows × 6 columns). **Printed p.110 carries roughly 270**
(two blocks of 24 field-spec rows, 5-6 of 10 columns populated).
Printed p.102 carries about 120, p.105 about 80, p.100 about 60.

There are ~147 table pages (printed 35-94 floating point, 98-105
transmit/index/branch, 106-186 VFL). Scaling the counted sample gives
an **order of 2-3 × 10⁴ measured values**. This is a counted-sample
extrapolation, not a count; a real count would need every page read.

A prior agent's report that Vol. 2 is "purely benchmark program
listings with zero device data" is correct only of pp.1-33 and of I/O
device timing. The CPU timing tables are pp.34-186.

---

## 2. What the model charges

`bsv/StretchTiming.bsv`, 53 code lines. Two functions and a combiner:

```
budgetClocks(d, taken) = 2 * iboxCycles(d, taken) + eboxClocks(d)
```

**Unit discipline, which matters for every number below.** A "clock"
is 0.3 µs. The factor of 2 means `iboxCycles` is denominated in
**0.6 µs I-box control cycles**, while `eboxClocks` is denominated in
**0.3 µs clocks**. So the model's charge in microseconds is

```
  0.6 * iboxCycles   +   0.3 * eboxClocks
```

Sanity check against the code's own comment: `LX` returns 9, and the
comment says "4.8 + dec"; 9 × 0.6 = 5.4 = 4.8 + 0.6. Consistent.

Vol. 1 p.3-2 states its own unit explicitly: Table 2's times "are
listed … in terms of the basic machine cycles, which is presently 0.3
microsecond". So Table 2 cycles and `eboxClocks` share a unit.

Every value `iboxCycles` returns is a **constant selected by opcode**,
with exactly two exceptions: `CountBranch` branches on `taken`, and
`VflInt`/`Connective` add 1 cycle when an index field is non-zero.
`eboxClocks` is 0 for everything except `Fp` (flat 3) and
`VflInt`/`Connective` (`8 + 2·ceil(length/byte_size)`).

---

## 3. The comparison

Model µs = `0.6·iboxCycles + 0.3·eboxClocks`, computed from the source.
IBM µs = measured, Vol. 2, printed page cited. Δ = model − IBM;
**negative means the model is too fast.**

### 3.1 Index arithmetic — printed p.102

Columns below: `EXT D` = external operand direct, `EXT E` = external
effective (indexed), `INT D` = internal direct, `IDX D` = index operand
direct, `IMM` = immediate.

| Instruction | model cyc | model µs | EXT D | EXT E | INT D | IDX D | IMM | Δ vs EXT D |
|---|---|---|---|---|---|---|---|---|
| `LX` | 9 | 5.40 | 5.73 | 6.33 | 6.93 | 5.72 | — | **−0.33** |
| `LV` `LC` `LR` | 8 | 4.80 | 5.42 | 5.87 | 5.88 | 5.27 | 3.31 | **−0.62** |
| `SX` | 3 | 1.80 | 3.46 | 3.61 | 3.01 | 5.12 | — | **−1.66** |
| `SV` `SC` `SR` | 8 | 4.80 | 7.81 | 7.82 | 7.83 | 6.33 | — | **−3.01** |
| `V+` | 8 | 4.80 | 5.27 | 5.87 | 5.87 | 5.27 | 3.31 | **−0.47** |
| `V+C` | 8 | 4.80 | 5.27 | 5.87 | 5.87 | 5.87 | 3.92 | **−0.47** |
| `V+CR`, refill **not** taken | 15 | 9.00 | 5.27 | 5.88 | 5.88 | 5.88 | 3.92 | **+3.73** |
| `V+CR`, refill taken | 15 | 9.00 | 9.34 | 9.94 | 9.94 | 9.94 | 8.13 | **−0.34** |
| `KV` `KC` | 8 | 4.80 | 5.27 | 5.87 | 5.87 | 5.27 | 3.31 | **−0.47** |
| `LVI` `LCI` `LRI` `LVNI` `V±I` `C±I` `KVI` `KVNI` `KCI` | 5 | 3.00 | — | — | — | — | 3.31 | **−0.31** |
| `V+IC` `V−IC` | 6 | 3.60 | — | — | — | — | 3.92 | **−0.32** |
| `V±ICR`, refill **not** taken | 13 | 7.80 | — | — | — | — | 3.92 | **+3.88** |
| `V±ICR`, refill taken | 13 | 7.80 | — | — | — | — | 8.13 | **−0.33** |
| `R` | 14 | 8.40 | 11.42 | 11.43 | 10.83 | 7.68 | — | **−3.02** |
| `RCZ`, C ≠ 0 | 8 | 4.80 | 5.27 | 5.87 | 5.87 | 4.07 | — | **−0.47** |
| `RCZ`, refill taken | 8 | 4.80 | 11.42 | 11.43 | 10.83 | 7.68 | — | **−6.62** |
| `RNX` | 8 (DirIndex default) | 4.80 | 12.96 | 13.56 | — | — | — | **−8.16** |
| `EX`, `EXIC` | 14 (inherits `R`) | 8.40 | not measured in Vol. 2 | | | | | see §3.7 |
| `Z` | 3 | 1.80 | not measured in Vol. 2 | | | | | — |

Printed p.103 continues the same table with three more I-box
instructions. `LVE` (0b11011) and `SVA` (0b11101) are both in
`DIR_INDEX_CODES` (`strap/opcodes.py:114-115`) and so both take the
`DirIndex default: 8`:

| Instruction | model cyc | model µs | EXT D | EXT E | INT D | INT E | IDX D | IDX E | Δ vs EXT D |
|---|---|---|---|---|---|---|---|---|---|
| `LVE`, 18/19/24-bit address | 8 | 4.80 | 8.89 | 9.04 | 9.49 | 9.49 | 7.68 | 7.68 | **−4.09** |
| `SVA`, 18/19/24-bit address | 8 | 4.80 | 7.81 | 7.82 | 7.82 | 7.83 | 6.33 | 6.93 | **−3.01** |

`SVA` matches `SV`/`SC`/`SR` to 0.01 µs, as Vol. 1 Table 4 (p.3-11)
predicts — and inherits the same −3.01 error.

**`LVS` is a second iteration-count instruction**, and the model does
not read its count. Printed p.103 measures it against the number of
index registers summed:

| | CLEAR VF | 1 XR | 5 XR | 10 XR | 15 XR |
|---|---|---|---|---|---|
| J field **=** index operand | 6.48 | 6.48 | 13.71 | 22.75 | 31.78 |
| J field **≠** index operand | — | 8.29 | 15.52 | 24.55 | 31.78 (14 XR) |

The slope is (31.78 − 6.48)/14 = **1.807 µs per added register**,
confirming Vol. 1 Table 5's "LVS 5.4 µsec + dec / Additional 1.8 µsec
per ADD" (p.3-11). `LVS` is immediate-index code 0b1011
(`opcodes.py:139`), so `iboxCycles`'s `ImmIndex default: 5` charges
**3.00 µs** against a measured 6.48-31.78. (`LVS` is excluded from the
assembler — `strap_asm.py:103` — so it cannot currently be reached by
a test program either.)

**The two-row `V+CR` reading** (first row = refill not taken, second =
taken) is corroborated three ways, not assumed: p.101 says "Conditional
refill operations were tested for both conditions"; the first row is
numerically identical to `V+C` (5.27/5.87/5.87/6.48 vs
5.27/5.88/5.88/6.48); and Vol. 1 Table 5 (p.3-11) footnotes `V+IC`
with "Also V ± ICR where Count ≠ 0", i.e. a non-refilling `V±ICR`
costs what `V±IC` costs. Vol. 1 Table 8 (p.3-14) says the same for
branches: "CBR behaves like CB if Refill is not to be taken."

**The model drops every bracketed `LAAR` and `LAdr` term in Vol. 1's
own formulas and keeps only the scalar part.** This is not scattered
bad luck; it accounts for most of the large negative deltas above.
Vol. 1 Table 4 (p.3-11) gives `SX` as `1.2 + dec + LAAR` and
`SV`/`SC`/`SR` as `4.2 + dec + LAAR`; Table 6 (p.3-12) gives `R` as
`7.8 + dec + LAAR` and `Z` as `1.2 + dec + LAAR`; Table 4 gives `RNX`
as `9.0 + dec + LAdr + LAAR`. `iboxCycles` charges the leading number
plus `dec` in every case and nothing for the bracketed term.

Backing the omitted term out of the measurements:

| instruction | Vol. 1 scalar part | measured (EXT D) | implied `LAAR`/`LAdr` |
|---|---|---|---|
| `SX` | 1.80 | 3.46 | 1.66 |
| `SV` `SC` `SR` | 4.80 | 7.81 | 3.01 |
| `R` | 8.40 | 11.42 | 3.02 |
| `RNX` | 9.60 | 12.96 | 3.36 |
| Transmit, 1 wd (§3.3) | 8.40 | 14.47 | 6.07 |

The implied term is **not a constant** — it ranges from 1.66 to 6.07
µs across these five. That is the point. `LAAR` is a look-ahead
address-register acquisition and `LAdr` is a look-ahead drain; both
are memory-unit and look-ahead occupancy, so their cost depends on
machine state at the moment of issue, not on the opcode. IBM wrote
them as unevaluated symbols in the table precisely because they have
no scalar value. There is no constant to add.

**`RNX` is 0b11111 in `DIR_INDEX_CODES`** (`strap/opcodes.py:113`) and
therefore falls through `iboxCycles`'s `DirIndex` `default: 8`. Vol. 1
Table 4 gives it 9.0 + dec + LAdr + LAAR; it is measured at 12.96. The
model charges 4.80.

### 3.2 Branches — printed p.105

Page conditions: `BRANCHING CB BIND NO FORWARDING DIRECT ADDRESSING
INSTRUCTION AT FULL WORD ADDR`. `SUCCES`/`UNSUCC` for `CBR` means
refill taken / not taken (printed p.104).

| Instruction | model cyc | model µs | IBM succ | IBM unsucc | Δ succ | Δ unsucc |
|---|---|---|---|---|---|---|
| `CB` `CBZ` `CB±` `CBH` `CBZH` | 8 / 7 | 4.80 / 4.20 | 4.82 | 4.52 | **−0.02** | **−0.32** |
| `CBR` `CBR±` `CBRH` | 12 / 11 | 7.20 / 6.60 | 11.14 | 4.52 | **−3.94** | **+2.08** |
| `BXL` `BZXL` (I-box indicator) | 6 | 3.60 | 4.52 | 2.26 | **−0.92** | **+1.34** |
| `BAL` `BZAL` (arithmetic-result indicator) | 6 | 3.60 | 19.78 | 7.20 | **−16.18** | **−3.60** |

Branch-address indexing adds +0.30 for `CB`/`CBR`, +0.15/+0.60 for
`BXL`, +0.30/+0.01 for `BAL`.

Two things here are worth more than their size. `CB` taken is 4.80
against a measured 4.82 — the single best match in the whole
comparison, and the reason the scalar looked plausible. And `CBR`'s
error **changes sign between its own two arms**: the model is 3.94 µs
too fast when the refill happens and 2.08 µs too slow when it does
not. The model's spread between the two cases is 0.60 µs; the real
machine's is 6.62 µs.

`BranchInd` has no `taken` term at all — one constant covers four
measured values spanning 2.26 to 19.78 µs.

### 3.3 Transmit — printed p.100, external → external

| words | model µs | IBM µs | Δ |
|---|---|---|---|
| 1 | 4.20 | 14.47 | **−10.27** |
| 3 | 4.20 | 20.48 | −16.28 |
| 5 | 4.20 | 26.51 | −22.31 |
| 15 | 4.20 | 56.66 | −52.46 |
| 50 | 4.20 | 162.15 | −157.95 |
| 100 | 4.20 | 312.88 | **−308.68** |

Least squares over the ten measured lengths: **11.46 + 3.014·N µs**.
The 3.014 µs/word slope matches Vol. 1 Table 9's "Loop time 3.0 µsec"
for `T (EM-EM)` (p.3-14) to within the measurement error. The 11.46 µs
intercept is Table 9's `1.2 + dec + LA dr` setup plus 3.6 termination
= 8.4 µs **plus a look-ahead drain of ≈ 6.07 µs**, which printed p.98
names outright: "LA is emptied before the actual transmission of
information."

The model's `Transmit` returns 7 — its comment says "Blosk fig.9: 2
set-up + 5 per word (**one word here**)". The word count is a field of
the instruction; the model never reads it.

### 3.4 VFL — printed p.110 (`M+`, no forwarding, direct addressing, offset 0, instruction at full word address)

Model µs = `0.6·(6 + idx) + 0.3·(8 + 2·ceil(len/bs))`, i.e. for the
unindexed case `6.0 + 0.6·ceil(len/bs)`.

| field spec | model µs | EXTERNL | EXTERNL **WB XOVR** | I-BOX | Δ vs EXTERNL | Δ vs WB XOVR |
|---|---|---|---|---|---|---|
| `(BU,1,8)` | 6.60 | 6.63 | — | 10.88 | −0.03 | — |
| `(BU,8,8)` | 6.60 | 6.63 | 15.96 | 10.88 | −0.03 | **−9.36** |
| `(BU,16,8)` | 7.20 | 6.93 | 16.56 | 11.48 | +0.27 | −9.36 |
| `(BU,32,8)` | 8.40 | 7.84 | 17.76 | 12.69 | +0.56 | −9.36 |
| `(BU,48,8)` | 9.60 | 9.02 | 18.97 | 13.90 | +0.58 | −9.37 |
| `(BU,64,8)` | 10.80 | 9.61 | 19.57 | 14.51 | +1.19 | −8.77 |
| `(DU,64,4)` | 15.60 | 14.40 | 24.39 | 19.34 | +1.20 | −8.79 |
| `(D,64,4)` | 15.60 | 15.01 | 24.99 | 19.94 | +0.59 | −9.39 |
| `(B,64,1)` | **44.40** | 10.80 | 20.78 | 15.72 | **+33.60** | +23.62 |

For the byte-size-8 and -4 rows with an external operand, the model is
the best it is anywhere: within 1.2 µs over a 6.6-15.6 µs range. That
agreement is confined to one of the ten columns.

Two structural failures are visible on this one page:

- **Word-boundary crossing costs ~9.3 µs and the model charges zero.**
  `StretchVFL.bsv:53` already has `fieldCrosses` — the model *knows*
  when a field spans two words, and uses it only to raise OP-invalid on
  a crossing store. It is a correctness predicate with no timing term
  attached.
- **Byte size 1 is 4× wrong, in the opposite direction — and this one
  is a plain bug in the model, not a gap in the source.**
  `effByteSize(bs) = (bs == 0) ? 8 : bs` (`StretchVFL.bsv:43`), so
  `(B,64,1)` yields 64 SAU passes and a 44.40 µs charge against a
  measured 10.80.

On that second point the model and Vol. 1 are **not** in agreement,
and Vol. 1 is right. Vol. 1 Table 3 (p.3-7) gives `M+` as
`1.8 + .6(x/y) + .6`, and the variable list on **printed p.3-8**
defines

> `y`   8 in binary operations and byte size in decimal operations

So `y` is the SAU's *effective* byte size, which is 8 in binary mode
whatever the instruction declares — byte size is a decimal-arithmetic
and field-addressing parameter on the 7030, not a binary-arithmetic
one. `effByteSize` returns the declared field instead.

With `y` read correctly, Vol. 1's equation plus the model's own 3.6 µs
I-box charge reproduces the measurements closely, including the row
the model gets worst:

| field spec | `x/y` per p.3-8 | 3.6 + 1.8 + .6(x/y) + .6 | measured (EXTERNL) |
|---|---|---|---|
| `(BU,8,8)` | 8/8 = 1 | 6.60 | 6.63 |
| `(B,32,1)` | 32/8 = 4 | 8.40 | 8.42 |
| `(B,64,1)` | 64/8 = 8 | **10.80** | **10.80** |
| `(DU,64,4)` | 64/4 = 16 | 15.60 | 14.40 |

**The model's VFL timing formula already has the right shape** — it is
literally Table 3's equation, `2.4 + 0.6·(x/y)` µs — with one variable
read wrong. That makes the byte-size error a correction (§4), and
leaves the `WB XOVR` column as the only VFL *shape* problem.

The fix is not simply to change `effByteSize`: the same function feeds
`readField`/`writeField`, where the declared byte size genuinely
governs field addressing and decimal arithmetic. Timing needs its own
`y`.

Indexing also costs differently by class: on p.110 it is +0.29/+0.30
(one 0.3 µs clock), while the model charges +1 I-box cycle = +0.60; on
p.102 indexing really is +0.60.

### 3.5 Floating point — printed p.66, and Vol. 1 Table 2

**These are not comparable as a delta, and the note does not table them
as one.** Vol. 2's floating-point figures are average times in a
steady-state loop with look-ahead overlapping the E-box; the model's
`budgetClocks` is a serialized occupancy charged at dispatch and not
overlapped (`StretchTiming.bsv` header: "Without the look-ahead (stage
3) E-box time is not overlapped with the next preparation"). For the
index-arithmetic and branch tables the two nearly coincide, because
the I-box is the bottleneck and there is nothing to overlap; for
floating point they measure different things.

What p.66 does show is the **spread** the model has to cover. For
`+` with forwarding, `NORMALIZED 1.`:

| data case | internal | external | I-box | internal, indexed | external, indexed | I-box, indexed |
|---|---|---|---|---|---|---|
| `(N)` | 4.37 | 2.41 | 2.27 | 4.37 | 2.41 | 2.41 |
| `(U)` | 3.60 | 2.41 | 1.81 | 3.60 | 2.41 | 2.41 |
| `AC EXPNT N. MEM EXPNT XPFN` `(N)` | 3.90 | 2.41 | 1.81 | 3.90 | 2.41 | 2.41 |

The model charges one number (`2·2 + 3` = 7 clocks = 2.10 µs) for all
of them. Note that the *internal* operand is the slowest case, not the
fastest — p.34C explains it: the internal operand is the accumulator's
right half, so consecutive operations accumulate large exponent
differences and pre-shift.

The decisive floating-point finding is in `eboxClocks`, which returns
**3 for every `Fp` instruction**. Vol. 1 Table 2 (printed pp.3-3 to
3-5), in 0.3 µs cycles:

| instruction | pre-execution | execution | total | model |
|---|---|---|---|---|
| `L` `LWF` `LFT` `ST` | 2 | 1 | **3** | 3 |
| `DL` | 2 | 1 | 3 | 3 |
| `SRD` | 3 | 1 | 4 | 3 |
| `+` `+MG` `M+` `K` `KMG` `KR` `KMGR` | 4 | 1 | 5 | 3 |
| `SHF` | 4 | 1 | 5 | 3 |
| `E+` | 1 | 5 | 6 | 3 |
| `*` `D*` | 5 | 4 | 9 | 3 |
| `SLO` | 2 | 17 | 19 | 3 |
| `*+` | 3 | 17 | **20** | 3 |
| `/` `D/` `R/` | 2 | 2 + **data-dependent reduction loops** | — | 3 |
| `SRT` | 2 | 106 | **108** | 3 |

The model charges the *Load* figure to Store Root, which Table 2 puts
at 36× that. And divide's execution time is not a number in IBM's own
table — it is a loop count annotated "number of cycles is data
dependent".

### 3.6 Where the model is right, and why

Collecting the small deltas: the scalar is within 0.3-1.2 µs for
**I-box index arithmetic, external operand, unindexed, no refill
taken** (`LX` −0.33, `LV` −0.62, `V+` −0.47, `KV` −0.47, immediates
−0.31, `V+IC` −0.32, `CB` taken −0.02) and for **VFL with an external
operand, byte size 4 or 8, no word-boundary crossing** (−0.03 … +1.20).

That is exactly the scope of Vol. 1 Tables 4, 5 and 8 — the tables the
model was built from. The model is a faithful implementation of Vol. 1
§3, and Vol. 1 §3 describes one column of a ten-column measurement.

### 3.7 `EX` and `EXIC`

Confirmed by reading: `MISC_CODES` (`strap/opcodes.py:212-218`) is
`R` 0b000, `RCZ` 0b001, `EX` 0b010, `EXIC` 0b011, `Z` 0b100. The
model's misc arm is
`case (x.code) 3'b100: 3; 3'b001: 8; default: 14; endcase`, so **`EX`
and `EXIC` both land in `default: 14`, a value whose comment sources it
to `R`.**

Vol. 1 Table 6 (printed pp.3-12, 3-13) does not give `EX` a number. It
gives a six-term recipe:

1. decode time, plus
2. **always begins with a look-ahead drain**, plus
3. instruction fetch, from an **address-indexed table**: 4.8 µs at
   0.0/0.32, 6.0 at 1.0, 7.8 at 2.0-4.32, **11.2 at 5.0-11.32**, 7.8 at
   12.0, 5.4 at 13.0-14.32, 4.8 at 15.0, 4.2 at 16.0-30.32, 6.0 at
   31.0, 5.4 at 32.0-up, plus
4. **the decode and execution time of the executed instruction**, plus
5. always ends with a look-ahead drain, plus
6. 3.0 µs for the fetch of the next instruction.

`EXIC` adds a pseudo-instruction-counter fetch overlapped with the
drain and a stepping cost that differs by where the psIC lives.

The fetch term alone ranges over 4.2-11.2 µs by address. Term 4 is
unbounded: `EX` of a transmit of 100 words costs at least 312.88 µs.
A flat 8.40 µs is not an approximation of this.

The model already contains the mechanism this needs. `Sic` recurses:
`2 + iboxCycles(decodeHalfWord(x.inner), taken)`. `EX` is structurally
the same instruction-containing-an-instruction and gets a constant.

---

## 4. The verdict: REBUILD, with a bounded correction inside it

**The per-instruction scalar is the wrong shape. No assignment of
constants to `iboxCycles` reaches cycle accuracy.** The evidence is
arithmetic, not rhetorical:

**(a) For several instructions the measured spread across conditions
exceeds the entire quantity the model charges.** A constant cannot be
within a factor of two of both ends.

| instruction | measured low | measured high | ratio | model charges |
|---|---|---|---|---|
| Transmit, ext→ext (p.100) | 14.47 (1 wd) | 312.88 (100 wd) | 21.6× | 4.20 |
| `LVS` (p.103) | 6.48 (1 XR) | 31.78 (15 XR) | 4.9× | 3.00 |
| `BAL`/`BZAL` (p.105) | 7.20 unsucc | 19.78 succ | 2.7× | 3.60 |
| `M+ (BU,8,8)` (p.110) | 6.63 external | 15.96 external WB XOVR | 2.4× | 6.60 |
| `CBR` (p.105) | 4.52 unsucc | 11.14 succ | 2.5× | 7.20 / 6.60 |
| `RCZ` (p.102) | 4.07 index, C≠0 | 11.43 ext, refill | 2.8× | 4.80 |

**(b) `CBR`'s error changes sign between the instruction's own two
cases.** Model 7.20 against a measured 11.14 when the refill is taken;
model 6.60 against a measured 4.52 when it is not. A constant can be
wrong; a constant whose error inverts across the two arms of a single
instruction is the wrong *shape*. The model's own spread is 0.60 µs
against the machine's 6.62.

**(c) IBM's page titles are the schema, and the model has one axis of
it.** Printed p.110's title alone names four orthogonal conditions —
`NO FORWARDING`, `DIRECT ADDRESSING`, `OFFSET 0`, `INSTRUCTION AT FULL
WORD ADDRESS` — before the ten columns and 24 field-spec rows. The
measured time is

```
t = f(opcode, operand location, indexing, forwarding,
      word-boundary crossing, field spec, data case,
      instruction alignment, surrounding instruction stream)
```

`iboxCycles(DecodedInstr, Bool taken)` can see the opcode, one index
field, and one taken bit. Operand location, forwarding, word-boundary
crossing and the surrounding stream are not in its argument list, and
could not be: they are properties of the memory system and the
look-ahead, which is where the time actually goes.

**(d) IBM's own tables already say the time is not a scalar.** Vol. 1
§3's formulas carry unevaluated symbolic terms — `LAAR` (look-ahead
address register), `LAdr` (look-ahead drain), `LAMT` (look-ahead
empty) — which the model silently drops (§3.1). Backing them out of
the measurements gives 1.66, 3.01, 3.02, 3.36 and 6.07 µs for five
different instructions: they are machine-state occupancy, not
constants. IBM left them as symbols because they have no number.

**(e) The model charges a scalar where IBM's own table is a recipe.**
`EX`/`EXIC` (§3.7) is the proof: Vol. 1 Table 6 declines to give a
number and instead gives six terms, one of which is the embedded
instruction's own time. Nothing in `Bit#(16)` can carry that.

**The bounded correction inside the rebuild.** Three of the gaps *are*
wrong constants and are worth fixing now, independently, in hours —
because each collapses a distinction IBM's own prose calls out:

1. **`DirIndex default: 8` lumps `SV`/`SC`/`SR` (measured 7.81) with
   `LV`/`LC`/`LR` (5.42) and `V+`/`KV`/`KC` (5.27)**, a 2.54 µs spread
   inside one `default`. Printed p.101 states the cause in words: "In
   SX, no memory fetch is necessary. This is not true for SV, SC and
   SR. This explains the large difference in timing." The model
   collapsed a distinction the source narrates.
2. **`V+CR` (15) and `V±ICR` (13) charge the refill-taken cost
   unconditionally**, +3.7 and +3.9 µs on the common non-refilling
   path. `CountBranch` already takes a `taken` argument; `DirIndex`
   and `ImmIndex` do not, and the refill condition is known at the
   same point.
3. **`RNX` falls through `default: 8`** (4.80) against a measured
   12.96; **`EX`/`EXIC` inherit `R`'s 14**; `LVE` and `SVA` likewise
   fall through it (−4.09, −3.01).
4. **`effByteSize` makes the VFL E-box charge 4× too slow in binary
   mode** (§3.4): +33.60 µs on `(B,64,1)`. This is the largest single
   correctable error found, and the VFL formula's *shape* is already
   right — it is Vol. 1 Table 3's equation with one variable read
   wrong. Timing needs its own `y` (8 in binary, byte size in
   decimal); `effByteSize` itself must keep returning the declared
   field for `readField`/`writeField`.

Fixing those four raises the model's accuracy on the operations it
already covers well. None of them touches (a)-(e), and none should be
mistaken for progress toward cycle accuracy.

**What the right shape looks like**, and it is the shape
`AGENTS.md` already mandates for other reasons: time must be an
*emergent* property of modelled structure — memory-unit occupancy and
bank conflict, look-ahead level occupancy and drain, forwarding from
the LAAR, word-boundary crossing in the VFL byte loop, a multi-cycle
SAU/PAU with request/response — not a number charged at dispatch. The
idiomatic-Bluespec rewrite (`microarchitecture_plan.md` §1c), the
multi-cycle box modules, and cycle accuracy are the same work, as
`AGENTS.md` says. This survey is evidence for that claim rather than
against it: every one of the five large gaps above is a *structure* the
model does not have — a look-ahead drain (Transmit, `BAL`, `EX`), a
refill memory fetch (`CBR`, `V+CR`), a word-boundary crossing (VFL), an
instruction-field iteration count (Transmit's word count, `LVS`'s
register count), a data-dependent iteration count (divide, `SRT`), and
an embedded instruction (`EX`).

**Timeline consequence.** Chasing constants against Vol. 2 is weeks and
caps out around ±1 µs on one column of the oracle. Reaching the
oracle's other nine columns is the structural rebuild already planned.
Vol. 2 should become the *acceptance test* for that rebuild, not a
table to copy into `StretchTiming.bsv`.

---

## 5. Do the `CYCLES<=` bounds mean anything?

**They are good regression guards and zero-information accuracy
checks.** Two independent reasons, and both halves are true.

**They are all one-sided, and the model's dominant error is in the
unbounded direction.** All six are `CYCLES<=N`, so **no bound can ever
fail because the model got faster** — and too-fast is the direction of
every large gap in §3.1-§3.3. Counting the tabled deltas in those
three sections — 17 in §3.1's main table, 2 in its `LVE`/`SVA`
addendum, 8 in §3.2, 6 in §3.3, so 33 — **29 have the model too
fast**, several by 3-300 µs; the 4 positive ones are the two
unconditional-refill rows and `CBR`/`BXL` unsuccessful. (§3.4's VFL rows are
genuinely mixed, and the one large positive delta there is the
`effByteSize` bug.) A model that got arbitrarily faster would pass all
six bounds. They cannot catch the error that is actually there.

**They were calibrated against the model's own output, not against
IBM.** `strap/run_tests.sh` says so: "bound is deliberately tight at
300" after "Measured 291 at stage 2b"; "Bounds carry ~10-25% slack;
they catch timing regressions and tighten as later stages add overlap".

| benchmark | recorded measurement | bound | slack | source |
|---|---|---|---|---|
| `ibox_timing_cb.strap` | 291 | 300 | 3.1% | `run_tests.sh` ~2035 |
| `la_timing_loads.strap` | 113 | 140 | 23.9% | `run_tests.sh` ~2046 |
| `la_timing_loop.strap` | 807 | 900 | 11.5% | `run_tests.sh` ~2055 |
| `la_branch_guess.strap` | **none recorded** | 260 | unknown | `run_tests.sh` ~2070 |
| `problem_2_1.strap` | 113 (stage 2b) | 140 | 23.9% | `run_tests.sh` ~2025 history note |
| pp.43-51 span | 4006 (stage 2b) | 4400 | 9.8% | `run_tests.sh` ~6033 |

The prior session's observation about `la_timing_loads` is confirmed
from the file: the comment says "~115 clocks; the note here said
'measured 120' and the figure is 113". The note was stale and has been
annotated but not corrected; the bound of 140 sits 24% above the real
figure.

Note also that `problem_2_1` and `la_timing_loads` are both recorded at
113 with the same bound of 140. That may be coincidence or may be a
transcription of one into the other; it was not resolved this session
(§7).

**What would make them mean something:** two-sided bounds
(`CYCLES` in `[N_lo, N_hi]`) on benchmarks whose IBM figure is known.
Two already exist in principle — `ibox_timing_cb.strap` is ten taken
`CB`s, and p.105 measures a taken `CB` at 4.82 µs = 16.07 clocks;
`la_timing_loads.strap` is four full-word VFL loads, and p.110's
column structure covers them. Those two could be converted from
self-referential guards into oracle checks without any new
infrastructure.

---

## 6. Vol. 1 Table 10, and the end-to-end oracle

**Table 10 is not what the task description expects, and the real
end-to-end oracle is better.**

**Table 10** (printed p.4-9) is the "EXECUTION FREQUENCY CHART FOR
STRETCH PROGRAMS". Its eight columns are **AO, Pseudo j-level, A1,
Modified, A2, Grid Param, Elem. Functions 1st Form, 2nd Form** — the
weather-forecasting study and the elementary function test of Vol. 1
§4. It gives, per column, operation counts broken down by class
(floating point, VFL, indexing, branching, misc.), a grand total, an
`Execution Time (ms)` row (5.98, .7, 5.57, 7.045, 7.0135, 7.07, .38,
.309) and an `Aver. time (µs)/opn` row (3.5, 6.4, 2.7, 2.4, 2.36, 3.8,
3.3, 2.9). So it does carry eight whole-program measured times. But
**the source of those programs is not in Vol. 2.** Vol. 2 pp.1-33 are
GERB2, the matrix multiply, PRIMC and the Monte Carlo program.

Table 10 is still valuable, in a different way: op counts × classes ×
total time is a direct check on a *weighted average* instruction time.
If the model's class-average times were right, the model would
reproduce 2.36-6.4 µs/op on those mixes. It is a cheap sanity oracle
that needs no program source.

**The real end-to-end oracle is Vol. 1 §4's prose, which cross-
references Vol. 2 explicitly.** Printed p.4-1, under GERB2, the
"Program" heading reads, in full: "See Volume 2."

| program | Vol. 2 listing | Vol. 1 measured time | printed page |
|---|---|---|---|
| GERB2 matrix inversion (Hilbert, Jordan elimination) | pp.3-7 | 10×10 **0.02 s**; 20×20 **0.14 s**; 30×30 0.43 s; 40×40 0.99 s; 50×50 1.59 s; 60×60 3.23 s; 70×70 5.10 s; 80×80 7.55 s; 90×90 10.69 s; 100×100 14.61 s | 4-1 |
| MXM16 matrix multiplication | pp.8-14 | 25×25 0.20 s; 50×50 1.35 s; 75×75 4.74 s; 100×100 10.71 s; 125×125 21.44 s | 4-3 |
| PRIMC prime generation | pp.15-18 | 106.7 s (102.7 s for the `V+I` variant) | 4-4 |
| Monte Carlo | pp.19-33 | 33 s for 10,000 particles | 4-5 |

**This is a genuine end-to-end oracle: measured runtime on the built
machine for a program whose source is printed.** It is strictly
stronger than a per-instruction table, because it integrates every
overlap the per-instruction tables control away.

**Could it be run today?** Assessment, in order of what blocks it:

- **Scale looks tractable for the small cases.** At 0.3 µs/clock,
  GERB2 10×10 = 0.02 s ≈ 66,700 clocks and 20×20 = 0.14 s ≈ 467,000
  clocks; 100×100 (14.61 s) is ≈ 4.9 × 10⁷ clocks. **This model's
  Bluesim throughput was not measured this session** (see §7), so
  whether half a million clocks is minutes or hours here is unknown —
  but 20×20 is the right target on precision grounds regardless: two
  significant figures against 10×10's one, which makes 10×10 a ±25%
  oracle at best.
- **The instruction set is largely covered.** GERB2 uses `L ST LX LV
  SV SC SX SVA Z DL D* D/ SRD *+ LFT T SWAP CB CB+ CBZ BXL BZAH BXVZ
  BZXCZ BEW C+I V+I V-IC LCI` and the pseudo-ops `XW DR DD SYN SLC
  CNOP`. Checked against `strap/opcodes.py` (368 mnemonics): `L ST LX
  LV SV SC SX SVA Z DL D* D/ SRD *+ T SWAP CB CB+ CBZ BEW C+I V+I
  V-IC LCI` are all present by name; the apparent absences (`BZAH`,
  `BXVZ`, `BZXCZ`, `BXL`, `LFTN`, `LA`, `KA`) are indicator-branch and
  modifier-composed forms the assembler builds from a base mnemonic
  plus an indicator, not missing opcodes. And the hard arithmetic is
  implemented and regression-tested: `run_tests.sh` covers `D/` ("FP
  divide arithmetic (jb_af1c F217A on the model)", ~line 2860), `*+`
  ("FP multiply and add arithmetic (jb_af1c F216A on the model)", ~line
  2840), `D*` and `SRD`. `SRT` (Store Root) has no test and was not
  investigated.
- **The real blocker is transcription, and it is specific to this
  project's rules.** Vol. 2's listings are OCR'd STRAP **source** with
  **no machine-code column** — unlike `ja_ax1a`, `jb_ax5b` and the
  other diagnostics, which print IBM's assembled octal beside each
  line. `AGENTS.md` rule 3 ("transcribe the printed machine-code column
  too and check it with `stretch/strap/listing_oracle.py`") **cannot be
  applied to Vol. 2.** And the OCR is poor: the GERB2 page alone shows
  `PIUOT` for `PIVOT`, `SK1` and `SXl` for `SX1`, `9+1,0` for `B+1.0`,
  `CON!` for `CON1`, `X~O` for `XWO`, `{SX1)` for `(SX1)`. Every line
  would need hand-reading from the page image with no independent
  check. GERB2 is ~5 printed pages, so this is feasible — but it is
  the project's weakest verification posture, and it should be entered
  knowingly.
- **One substantive unknown:** whether Vol. 1's GERB2 times are pure
  compute. The kernel is self-contained (Hilbert matrix generated, no
  I/O in the inversion loop), and the listing's console/tape I/O is in
  the driver. Not confirmed from the text.

**Recommendation.** GERB2 20×20 against 0.14 s is the single highest-
value validation target in the project, and it should be used as the
acceptance test for the structural rebuild, not attempted against the
current scalar model — §3 predicts it would come out far too fast, and
would tell you nothing you do not already know from this note.

---

## 7. What I could not determine

1. **`la_branch_guess.strap`'s actual cycle count.** No figure is
   recorded in `run_tests.sh` and I did not run it. `uptime` at the
   start of this session was `load averages: 103.46 119.70 137.66` and
   at the end `148.25 138.05 135.66`, on a machine with 58 logged-in
   sessions. Cycle counts from Bluesim are deterministic and would not
   be corrupted by load, but a compile-and-run under load 148 was not
   a responsible use of the machine. Whether its bound of 260 is tight
   is therefore unknown.
2. **Whether `problem_2_1` and `la_timing_loads` both genuinely measure
   113**, or whether one figure was transcribed into the other's
   comment. Both are recorded at 113 with a bound of 140.
3. **An exact count of the measured data points.** §1.3 is a
   counted-sample extrapolation from two pages (192 and ~270 cells),
   not a count. A real figure needs all ~147 table pages read.
4. **Printed pp.35-94 in detail.** I read p.66 closely and sampled the
   OCR of the rest. The floating-point section's 60 pages were not
   systematically extracted, so §3.5 rests on one page plus Vol. 1
   Table 2.
5. **Printed pp.111-186 in detail.** Of the VFL section's ~77 pages I
   read p.110 closely. The per-page conditions (forwarding, offset,
   indirect addressing, half-word instruction alignment) vary across
   those pages in ways I did not enumerate.
6. **Printed pp.96-97 (environmental timing results).** I read the
   method on p.95 but not the result tables. These matter most for the
   look-ahead model, since they measure a subject instruction against
   1-8 deep backgrounds — i.e. they measure overlap directly.
7. **Whether Vol. 2's `TRANSMIT` on p.99 differs from p.100 by
   indexing or by forwarding.** The page carries no distinguishing
   title in the rendering; the 1-word external→external figures differ
   (13.84 vs 14.47) and the internal columns on p.99 are constant
   across word counts, which is odd and unexplained.
8. **`Z`, `NOP`, `B`, `BR`, `BD`, `BE`, `BEW` measured times.** The
   model charges 3, 3, 7, 9, 11, 7, 7 cycles for these. They are not
   on printed pp.102, 103 or 105 (all three read this session); they
   may be on a page I did not open. `B`, `BR`, `BD`, `BE`, `BEW` have
   Vol. 1 Table 7 figures (p.3-13) which the model matches by
   construction, but no measured check was found.
9. **Whether Vol. 1's GERB2 timings include I/O.** See §6.
10. **`SRT` (Store Root) implementation status in the model.** Vol. 1
    Table 2 gives it 108 cycles; `run_tests.sh` has no `SRT` test and I
    did not read `StretchFP.bsv` for it.
11. **Whether `A22-6552` / `R23-9732` (the CE manuals) carry a third,
    structural timing source** — in particular numbers for `LAAR` and
    `LAdr` as functions of machine state (§3.1), which Vol. 1 leaves
    as unevaluated symbols and Vol. 2 can only show the sum of. Not
    opened. (`R23-9732` section 3 is listed in
    `microarchitecture_plan.md` as holding flow, block and timing
    charts, so it is the first place to look.)
12. **This model's Bluesim throughput in clocks per wall-clock second.**
    Needed to size the GERB2 end-to-end run in §6, and not measured:
    the machine was at `load average 148` and no simulation was run.
