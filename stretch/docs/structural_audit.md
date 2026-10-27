# What the real 7101 has, and what this model has

**The target, stated by the user on 2026-10-26: a STRUCTURALLY
FAITHFUL REGISTER-TRANSFER MODEL.** Not gate-level — the corpus
cannot support that and Bluespec could not express it (see the end of
this file). This is the gap list between the two.

## Where the hardware inventory comes from

`R23-9732_Manual04_7101_CPU_Jan63` carries a **trigger index**: every
flip-flop in the CPU, with a logic-page reference, a name carrying
its BIT POSITIONS, and a physical frame/gate/panel location.

```
2B055  25.01.07.1  Z REGISTER POS 24-27      1 33 12-1
2B059  25.01.09.1  Z REGISTER PARITY 24-27   1 36 5
2L025              LAAR 1 BUSY TGR
```

**963 distinct trigger IDs, 561 named items, 122 figures.** Grouping
the index by name and unioning the bit ranges gives the machine's
register complement and each register's width. That is what the table
below is built from; the method is a dozen lines of regex over
`docs/ocr/`, and it is reproducible.

> The OCR is a FINDING AID (`docs/ocr/README.md`). Every row below
> should be confirmed against the rendered page before it is built
> from — the index renders `Z` as `%` in places, which is the same
> glyph trap `listing_typography.md` documents for the MCP scan.

## The audit

Of the 27 hardware items carrying two or more triggers:

### PRESENT — the architectural registers, what the programmer sees

| hardware | triggers | bits | model |
| --- | --- | --- | --- |
| `IND REG` | 51 | — | `indicators`, word 11 |
| `UPPER BOUNDARY REGISTER` | 8 | 0-17 | `boundaryReg` |
| `INSTRUCTION COUNTER REGISTER` | 4 | 0-18 | `StretchCore`'s `pc` |
| `MASK REGISTER` | 4 | 20-47 | `mask`, word 12 |
| `LOWER BOUNDARY REGISTER` | 3 | 32-47 | `boundaryReg` |
| `UNIT ADDRESS REGISTER` | 3 | 12-23 | `channelAddress`, word 5 |

**`INSTRUCTION COUNTER REGISTER` at bits 0-18 is a nineteen-bit
field**, which is exactly what the Reference Manual says `SIC` stores
— "the instruction counter contents to be stored in bits 0-18". The
hardware index and the programming manual agree without being
consulted for each other.

### ABSENT — the microarchitectural registers, what an RTL model needs

| hardware | triggers | bits |
| --- | --- | --- |
| `Z REGISTER` | 17 | 0-63 |
| `X REGISTER` | 14 | 18-63 |
| `B REGISTER` | 9 | 0-63 |
| `C REGISTER` | 8 | 0-63 |
| `D REGISTER` | 8 | 0-63 |
| `ADDER OUTPUT` | 8 | **3-102** |
| `A REGISTER` | 6 | 8-63 |
| `Z% REGISTER` | 3 | 50-63 |
| `INSTRUCTION COUNTER BUFFER` | 3 | 0-16 |
| `EXECUTE REGISTER` | 2 | 21-25 |
| `LOAD GEOMETRIC ADDRESS REGISTER` | 2 | 0-3 |
| `CD RESIDUE REGISTER`, `RESIDUE OF AB REGISTER` | 5 | 12-63 |
| `OCC COUNTER`, `TBC COUNTER` | 4 | — |
| `PAR ON OP CODE` | 2 | 1-4 |
| **`LA LEVEL *`** | **46** | across **41** named fields |

## What the gap actually is

**The model is architecturally complete and microarchitecturally
empty.** Every register the programmer can name is there; none of the
machine's internal working registers is. The model computes an
instruction's RESULT directly and charges it a time budget, where the
machine moves operands through `A`/`B`/`C`/`D`/`X`/`Z` and an adder.

Three consequences worth stating plainly:

1. **`ADDER OUTPUT` spans bits 3-102.** That is a hundred-bit path,
   wider than a word and narrower than the accumulator — the shape of
   the PAU's double-precision field (12-107) seen from the adder's
   end. See `docs/vfl_arith_spec.md` on why `*` deposits at offset 20.
2. **A residue-checking tree exists** (`CD RESIDUE`, `RESIDUE OF AB`,
   `GENERATED RESIDUE FIRST/SECOND LEVEL`, per-register `PARITY`
   triggers). The machine checks its own arithmetic continuously. The
   model has no error-detection hardware at all, and the indicators
   it would drive — `EE`, `CS`, the data flags — are the ones
   `StretchIO.bsv` already records as not propagated.
3. **The look-ahead is 46 triggers across 41 named fields** and is
   the single largest absent structure. `docs/spec_lookahead.md` has
   its design; `bsv/StretchTiming.bsv` says in its own comment that
   without it "E-box time is not overlapped with the next
   preparation".

## Why not gate level

`R23-9732` references **1,993** logic pages and reproduces roughly
**285** lines of their content — waveform figures with signal names,
card locations and sub-cycle delays:

```
24.00.08.1   SAMPLE BIT DRIVERS   14B1E27B
             CHOPPED AND DELAYED 175 NSEC
24.00.09.1   GEN WORD WRITE       14B1F 186
             DELAYED SB           150 NSEC
```

The ALD set itself is a separate document nobody here has. And those
delays — 580, 175, 150 nanoseconds — are **sub-cycle**: the machine
clock is 300 ns. Bluespec is an RTL language in which a rule firing
IS a clock edge, so intra-cycle gate delay has nowhere to live in it.
Gate fidelity is netlist and SPICE territory, would not synthesise
onto a ULX3S any better, and would not run MCP any more correctly.

**So the ceiling is "cycle-accurate against IBM's own published
measurements", and the corpus supports that completely.** The
connective timing path already reproduces Vol. 2 PDF 140 at 17 rows
of 17 to 0.01 us.
