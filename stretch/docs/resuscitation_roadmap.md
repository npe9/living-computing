# Resuscitation roadmap: from this model to a 7030 you can boot and use

*Written 2026-10-16. Every section is complete. Sections §4.2, §4.4
and parts of §6 rest on a research pass over the cited pages rather
than on this author's own re-reading of the page image; they say so
where it matters, and §11 lists what remains unanswered.*

The owner's words, in two statements that must be read together:

> *"I want a typical stretch. I want to be able to resuscitate a real
> stretch."*
>
> *"I want a cycle accurate recreation that I can run on the ulx3s and
> run the MCP and other systems software."*

That is four goals, not one: **cycle accuracy**, **real hardware
(ULX3S)**, **MCP and other systems software**, and **a typical
six-memory-unit installation**. This document sizes each as its own
layer, says which can be pursued independently, says which must land
together, and ends with one ordered sequence in which every step
produces something checkable.

It is written to the repository's own rule (root `AGENTS.md`, "How work
is verified here", rule 4): **every claim about the real machine cites a
document and page; every claim about the model cites a file and line**;
every quantitative claim has a number behind it. §11 lists what the
documents in `docs/` do *not* answer, and names the document that
would.

**The headline, stated once so nothing later softens it.** **Four** of
the layers below are each larger than everything this project has
built so far — which is 28 active days and 376 commits (§0). The
Exchange with real devices (3–7 months), cycle accuracy of the
arithmetic units (3–6 months), the ULX3S (2–3 months) and MCP (2–4
months) are not extensions of the current model; they are four more
projects of its size or larger. The honest total is **years, not
months**, for all four goals together — and there is a first milestone
inside **weeks** that genuinely boots and runs a real 1961 program.
§10 separates those two facts rather than averaging them.

---

## Summary: the eight layers at a glance

| # | layer | state today | size | §0-calibrated |
|---|---|---|---|---|
| 1 | **ISA completeness** | 19 of 24 VFL op codes, decimal mode, 4 index ops, most Transmit forms unimplemented — and IBM's own benchmarks, Programming Examples and MCP use nearly all of them | **1–2 months** | 25–45 project-days |
| 2 | **Interruption & alarms** | largely built and deck-verified; the interval timer does not tick | **2–4 weeks** | 11–21 project-days |
| 3 | **The Exchange & real I/O** | 3 stub devices, word-granular, synchronous; the real thing is byte-serial, asynchronous, 32-channel, with its own storage | **3–7 months** | 75–150 project-days |
| 4 | **Bootstrap / IPL** | nothing; **but fully specified** (Ref. Man. printed p.126) | **3–5 weeks** | 15–25 project-days |
| 5 | **Software stack (MCP etc.)** | nothing runs; MCP's 451-page source listing is in `docs/`; MCP's stated minimum requires the disk | **+2–4 months after layer 3** | — |
| 6 | **The console** | nothing; most pieces have a home already | **1–2 weeks** | 5–10 project-days |
| 7 | **Cycle accuracy** | memory/I-box/look-ahead structural; **the E-box is a stopwatch in front of a one-cycle answer** | **3–6 months** | 75–150 project-days |
| 8 | **ULX3S hardware** | at zero; the repo has never run `bsc -verilog` | **2–3 months** | 40–75 project-days |

**First milestone that genuinely boots and runs a real 1961 program:
4–7 weeks** (§10.3). **All four of the owner's goals together: well
over a year.**

---

## 0. How the sizing in this document is calibrated

"Days", "weeks" and "months" here mean *this project's kind of day*,
which is unusually productive and should not be read as a person-day.
The unit is measured from the repository, not asserted:

| measure | value | how measured |
|---|---|---|
| commits touching `stretch/` | 376 | `git log --oneline -- stretch \| wc -l` |
| calendar span | 2026-08-24 → 2026-09-29 | first and last commit dates |
| **active days** (days with ≥1 commit) | **28** | `git log --format=%ad --date=short -- stretch \| sort \| uniq -c` |
| commits per active day | **13.4** | 376 / 28 |
| Bluespec source | **10,412 lines** | `wc -l bsv/*.bsv` |
| transcription verifiers | **182** | `ls tests/verify_*.py \| wc -l` |
| runnable STRAP programs | **240** | `ls decks \| wc -l` |

So **one "project-day" ≈ 13 commits**, and **the whole project to date
= 28 project-days**. Landmark features, measured the same way, give the
scale of a "layer":

| landmark | project-days | commits | evidence |
|---|---|---|---|
| Interruption + indicators + mask + address monitoring + boundary registers, with ~20 deck transcriptions | ~8 | ~90 | commits 2026-09-17 … 2026-09-25 |
| Floating point: 29 opcodes + ~120 `verify_fp_*` scripts | ~8 | ~140 | commits 2026-09-07 … 2026-09-15 |
| Microarchitecture stages 0–3 (memory units, MBCU, I-box 1Y/2Y, four-level look-ahead, branch guess) + the idiomatic-Bluespec rewrite | ~9 | ~180 | commits 2026-09-03 … 2026-09-11 |
| `EX` | 1 | ~5 | 2026-09-25 |
| `EXIC` | 1 | ~3 | 2026-09-29 |
| The whole simulated I/O subsystem as it stands | ~2–3 | ~25 | `StretchIO.bsv` is 342 lines of which 81 are code |

**Therefore, in this document:** *days* = 1–3 project-days; *a week* =
~5; *weeks* = 5–15; *a month* = ~22; *months* = 40–120; *a year* =
~250 project-days. When a layer is sized as "larger than the
interruption system", that means more than ~8 project-days and ~90
commits of work *of the same density* — which is itself a strong claim.

**The one caveat that keeps this honest.** 13.4 commits per active day
is measured on *incremental work against a standing regression suite*:
change a case arm, run `run_tests.sh`, commit. Layers with no such
suite behave differently — a `nextpnr-ecp5` run, an SDRAM bring-up on
real hardware, or the first byte-level Exchange model produce far
fewer commits per day of effort, because the feedback loop is
minutes-to-hours rather than seconds and because there is nothing to
regress against yet. **Estimates for layers 1, 2 and 7 (which extend
existing, tested structure) are the most defensible; estimates for
layers 3 and 8 (the Exchange and the FPGA, both at zero today) carry
the widest error bars and should be read as lower bounds.**

---

## 1. Where the model actually is

### 1.1 What is built

`bsv/README.md` line 68 states the current standard plainly: this
targets **"ISA-level correctness for a documented subset"**. That
sentence is the thing the owner's new goal supersedes, and it is quoted
here rather than quietly dropped.

Structurally the model is further along than that sentence implies —
the same README's opening paragraph (lines 3–20) records that stages
0–3 of `docs/microarchitecture_plan.md` and the idiomatic-Bluespec
rewrite have landed:

- **Memory.** `bsv/StretchMemory.bsv` line 60 — `typedef 98304
  InstalledWords; // 4 x 16K interleaved + 2 x 16K interleaved`: six
  units, BRAM-backed (`mkBRAM1Server`, line 104), with the memory bus
  control unit, interleave map, a 7-clock unit cycle and 5-clock
  read-out (`docs/microarchitecture_plan.md` §7 "Stage 1 — done").
- **Instruction unit.** `bsv/StretchIBox.bsv` — `mkInstrBuffers`, the
  1Y/2Y buffers and IC controls.
- **Look-ahead.** `bsv/StretchLookAhead.bsv` — four levels, in-order
  removal, fetch-ahead, branch guessing with wrong-way recovery.
- **Storage/CPU side.** `bsv/StretchStorage.bsv` — special words 0–31
  Reg-backed, store queue, one outstanding read, tagged bus channels.
- **E-box.** `bsv/StretchExecute.bsv` `mkEBox` — request/busy/result.
- **Timing.** `bsv/StretchTiming.bsv` (85 lines) — per-instruction
  clock budgets from IBM's Performance Characteristics tables.
- **Interruption system.** Built and deck-verified in part — see §3.
- **Simulated I/O.** `bsv/StretchIO.bsv` — 342 lines of which **81 are
  code**; three fixed stub devices (reader ch.32, printer ch.33, tape
  ch.34) with 32- and 16-word `Vector#(Reg#(Word64))` images. Its own
  header says it stands in for the Exchange. It is test scaffolding.

### 1.2 The one sentence that reframes everything about cycle accuracy

`docs/microarchitecture_plan.md` line 5771, in the audit against
Bluespec's own Piccolo core:

> | expensive datapath | `mkMBox` and `mkFPU` ARE `(* synthesize *)`,
> multi-cycle `rg_state` FSMs behind `Server` req/rsp | `fpAddDouble`
> etc. are plain combinational functions; multi-cycle-ness lives in
> TIMING as E-box budgets | **differs, by prior decision** |

**The arithmetic in this model is combinational, and its timing is
bookkeeping.** `StretchTiming.bsv` charges each instruction a scalar
number of clocks (`iboxCycles`, `eboxClocks`, `budgetClocks`), which
`StretchCore` burns down as `ebusy`. The memory system and the
instruction unit and the look-ahead *are* structural; the E-box is a
stopwatch in front of a one-cycle answer. That distinction is the
entire cycle-accuracy layer (§8) and the entire FPGA-feasibility
question (§7), and it is the single most important fact in this
document about the gap between where the model is and where the owner
wants it.

### 1.3 The evidence base — and a correction to how it is usually quoted

240 STRAP programs (`decks/`, all `.strap`), 182
`verify_*.py`, 389 `run` invocations across 57 numbered sections of
`tests/run_tests.sh` (6,143 lines), and six `CYCLES<=N` timing bounds
(lines 2035, 2046, 2055, 2070, 5900, 6033). A full run is ~207 s
(`AGENTS.md`, item 1).

**But the 182 verifiers do not run the model.** Audited directly:
every one of the 182 imports `strap_asm.assemble` and 180 import
`listing_oracle.check_rows`; **none imports `subprocess`, `gen_tb`, or
invokes `bsc`**. `strap/listing_oracle.py` says so in its own header
(lines 4–6): IBM's printed machine code *"checks bit placement of
every field **with no dependence on the Bluespec model at all**"*.
They are static assembler-vs-listing encoding checks — the strongest
oracle in the project for *encodings*, and no evidence at all about
*execution*.

**Execution evidence comes only from `run_tests.sh`'s 389 `run`
lines**, driving `gen_tb.py`-generated Bluesim testbenches with a
30,000-step default cap (`tests/gen_tb.py` line 20). That is still a
large and genuine regression oracle, but it is roughly half the size
the usual "182 verifiers" framing implies, and the distinction matters
for every milestone below. Concretely: `verify_ssip_sip17_listing.py`
and `verify_dcp_maintenance_compool.py` are **encoding-only**; no part
of SSIP or the DCP has ever executed on this model.

---

## 2. Layer 1 — ISA completeness

### 2.1 The real denominator, and why the ratchet undercounts

`tests/audit_opcode_coverage.py` reports today:

```
mnemonics STRAP can emit      : 116
used by at least one program  : 104
unused                        : 12
  unimplemented (sets OP)     : 12
  unimplemented but ENCODED by a transcription : 1  (RNX)
```

**That 116 is not the instruction set.** The script's own header says
so (`tests/audit_opcode_coverage.py` lines 30–33: *"it screens what the
ASSEMBLER can emit — an operation neither the assembler nor any program
knows about is invisible to it"*). Three whole classes of gap are
invisible to it because they are not separate mnemonics:

1. **Decimal mode is a modifier, not a mnemonic.** `ST(DU,16,8)` and
   `ST(BU,16,8)` are the same mnemonic; only the `c` bit differs. The
   audit sees `ST` as used and implemented.
2. **CONTROL function codes are operand values.** `CTL` is "used"; 2 of
   its documented function codes execute and the rest set OP
   (`bsv/StretchIO.bsv` lines 120–150).
3. **Transmit's forms are field values.** `T` is "used"; only
   forward/non-swap/immediate-count-of-one executes
   (`bsv/README.md` lines 243–250).

The 12 names the ratchet does list are: `CV DCV LCV LTRCV` (radix
conversion), `KE KF KFE KFR` (compare variants), `M+1`, `LTRS`, `LOC`,
`LOCSEOP` — plus `RNX` in the encoding-only category.

**And a fourth class the ratchet misses, which is the largest of all.**
Auditing `setOpInvalid` directly: there are 23 call sites, all in
`bsv/StretchExecute.bsv`, of which 12 are real unimplemented-function
gaps. The biggest is **one line**: `bsv/StretchExecute.bsv:2511`, the
`default` of `vflIntOp`'s `case (vi.code)`. That case implements five
arms — `L` (:2312), `ST` (:2347), `+` (:2394), `M+` (:2427), `K`
(:2478) — while `isVflIntCode` in `bsv/StretchDecode.bsv:126–150`
admits **24** codes. **Nineteen VFL operation codes collapse into that
one default**, and they include:

- **VFL multiply and divide**: `*`, `/`, `*+`, `LFT`, `LWF`, `SRD`,
  `+MG`, `M+MG` (`StretchDecode.bsv:132–150`). The README's "Executed"
  list is accurate about what is there; nothing states the size of
  what is not. **VFL binary multiply and divide are not implemented**,
  and they are PAU operations — so they belong to §8's stage 4d/4e
  along with floating-point divide, which is also absent.
- the four radix conversions and the seven compare/`M+1`/`LTRS` codes
  the ratchet does name.

So the honest statement of layer 1's size is not "12 unused
mnemonics". It is: **19 of 24 VFL operation codes, decimal mode
entirely, four index operations, most Transmit forms, `LOC`, and all
but two `CTL` function codes.**

**And the real denominator depends on the question.** Four numbers,
each counted from a named page rather than asserted:

| number | what it counts | source |
|---|---|---|
| **95** | mnemonics the pocket card names canonically, in its "ALPHABETICAL LIST OF MNEMONIC CODES" (48 + 47) | X22-6533, `docs/pcard-*.png` |
| **≥163** | mnemonic strings an assembler should accept (a floor — the bottom of pcard-4's left panel was lost at scan time) | X22-6533 |
| **141** | distinct mnemonics in STRAP-II's own operation table (160 rows, 19 listed twice as both VFL and FP) | `C22-6729` |
| **811 / 1,651** | architecturally distinct operations with the J-field collapsed / distinct assembled bit patterns | `7030_Opcode_List.pdf`, counted from two disjoint page sets that agreed |

The project's own 116 sits between 95 and 163 — it is neither the
canonical list nor the full accepted vocabulary.

**One correction to the brief's own premise, and it removes an item
from the list.** **`PF` is not an instruction.** It is **indicator
23, Partial Field** — pocket card INDICATOR LIST: *"PF m P,C Partial
Field"*, no. 23; `C22-6729` Appendix A printed p.43: `$ PF 2 Partial
Field 11 23`; Ref. Man. printed p.59: *"Partial Field (PF). … In
decimal operations to storage, the indicator is turned on if there is
any non-zero digit to the left of the highest order accumulator digit
that is taking part in the operation."* There is no `PF` opcode, no
`PF` mode letter, and no operand suffix. The task is *"raise this
condition"*, not *"decode this instruction"* — and it matters
operationally, because MCP's interrupt dispatcher has a real entry
for it (`BD,SIPT+23.`), so a model that raises PF spuriously would
dispatch MCP into that slot. (A related trap: `LF` and `SF` are
**pseudo-connectives** — `LF = C0011`, `SF = CM0101` — not
partial-field load/store; `LFT` is Load Factor.)

### 2.2 The question that matters: what does real software use?

**This is answered first-hand, and the answer is uncomfortable.**

*IBM 7030 Performance Characteristics, Volume 2* (March 8, 1961) is not
only timing tables. Its first 33 printed pages are **complete STRAP
source listings of IBM's own four benchmark programs** — the programs
IBM used to characterise the machine it had built:

| program | PDF pp. | printed pp. |
|---|---|---|
| GERB2 (matrix inversion) | 4–9 | 1–6 |
| MATRIX MULTIPLY (MXM16) | 10–17 | 7–14 |
| PRIME NUMBER (PRIMC) | 18–21 | 15–18 |
| MONTE CARLO | 22–36 | 19–33 |

*(`docs/7030_Performance_Characteristics_Vol2_Mar61.pdf`, 190 PDF
pages. Offset established first-hand on three pages: **PDF page =
printed page + 3**. The document has a partial OCR text layer, so every
line quoted below was re-read from a rendered page image per rule 4.)*

Scanning those four listings for the instructions this model refuses:

| instruction | occurrences in the four benchmarks | evidence | model status |
|---|---|---|---|
| `LVE` | **7** | 5 read from the page image at PDF p.12 | **implemented 2026-10-17** (one level; a chain sets OP). RefMan printed p.29, driven by `decks/lve_indirect.strap` and witnessed by MCP printed p.3 line 10 |
| `SVA` | **8** | 2 read from the image at PDF p.12 | **implemented** — this row said "partially (indicator fold only)" and was stale; `StretchExecute`'s `dixop_SVA` arm does the address replacement in full, width from `svaReplaceAddr` |
| `LCV` (radix conversion) | **6** | 3 read from the image at PDF p.33 | not implemented |
| `ST(DU,…)` decimal VFL | **7** | 4 read from the image at PDF p.33 | not implemented |
| `SWAP` with a **direct** count (`$X2`) | **2** | 1 read from the image at PDF p.5 | not implemented |
| `T`/`TI` with counts > 1 | among 23 `T`/`TI` | `TI,2` read at PDF p.12; `TI,9` at PDF p.33 | only immediate-count-of-one |
| `M+1` | 1 | OCR only (PDF p.23) — not image-verified | **implemented 2026-10-17** (`StretchExecute.bsv`, sharing `M+`'s arm; MCP printed p.2 line 34 is the bit-exact witness) |
| `LVS` | 1 | OCR only (PDF p.20) — not image-verified | **assembles 2026-10-17**; the model does not execute it. Two image-verified witnesses now exist, MCP printed p.4 line 23 and printed p.15 line 17, and RefMan printed p.28 specifies the mask |
| `CW(CDSC)` chained control words | 7 | OCR (PDF p.35); `CCW`/`BB` poll read at PDF p.33 | chaining decoded, ignored |
| `LOC` | **0** | — | not implemented |
| `CV`, `DCV`, `LTRCV`, `KE`, `KF`, `KFE`, `KFR`, `LTRS`, `PF`, `RNX` | **0** | — | not implemented |

*(Counts are from the OCR text layer; the rows marked "read from the
page image" were re-verified first-hand at 170 dpi per rule 4. The two
"OCR only" rows are the weaker evidence and are labelled as such.)*

Three verbatim extracts, each read from the page image:

**PDF p.12 = printed p.9** (MXM16's calling-sequence decode — `$15` is
the argument-list pointer, so `LVE` *is* the argument-fetch mechanism):

```
LVE3   LVE,$4,0($15)
       LRI,$4,$4                -$4 COMPLETE
       LVE,$5,2.0($15)
       LVE,$3,3.0($15)
       LVE,$14,4.0($15)
       LVE,$2,0.32($15)
       SVA,$3,LOOP1B+1.0        'LOOP1B+1.0
       SVA,$3,DUMMY+0.32
       TI,2,$4,$2
```

**PDF p.5 = printed p.2** (GERB2's pivot step):

```
       LX, $X2, CN4
       SWAP, $X2, A,DELTA+A ($X3)     'SWAP ROWS
```

— the count is *in `$X2`*, i.e. the direct-count form the model
explicitly refuses (`bsv/README.md` line 249: *"every other form … and
every direct count, whose register this arm does not read, sets OP and
no-ops"*).

**PDF p.33 = printed p.30** (Monte Carlo's print routine):

```
       LCV(BU, 64), BN
       ST(DU, 16,8), PRUF+11. -.16, 32
       ST(DU, 64, 8), PBUF+11
       ...
       W(SEOP), PRNT, CWD
       CCW, TAPE, CWB
       BB, CWB+.24, $-1.
       ...
       TI, 9, 7.,HOLD
```

**Corroborated independently in three other bodies of real code.** A
separate pass over `C22-6578` (IBM's Programming Examples), the
STRAP-II System Analysis Guide, and — most strongly — the 451-page
MCP source listing, whose negatives are corpus-wide rather than
sampled:

| feature | Programming Examples | STRAP-II's own code | MCP's own code | FORTRAN IV |
|---|---|---|---|---|
| **decimal VFL (`c=1`)** | **used** (Problem 2.8, end to end) | no | **used** (2 modules, 18 operand sites) | no |
| `CV` / `LCV` / `LTRCV` | `CV`, `LCV` used | no (parses with a binary Horner loop) | **used**: 3 / 9 / 4 sites | no |
| `KF` / `KFI` | **used heavily** | — | **used heavily** (68 lines) | no |
| `KE` / `KFE` | not seen | — | **not used** | no |
| `M+1` | not seen | — | **used ~35 sites** | no |
| `RNX` | simulated in Problem 1.8 | **used** (two index registers reserved for it, both passes) | decoder-table only | no |
| `LVE` | **used** (Problems 1.8, 2.2, 2.7) | not found in 46/211 pp | **used, ~44 pages** | no |
| `SVA` | **used** (Problem 2.7, paired with `LVE`) | not found | **used, ~92 pages** | no |
| `LVS` | **used** (Problem 1.6) | in manual examples | **used** (2 sites) | no |
| Transmit multi-word / direct count | **used** (counts 2, 3, 6) | **used** (runtime count) | **used** (counts to 16) | no |
| Transmit **backward** | **used** (`TBI`) | **used** (`MOVE` picks direction by overlap) | never | no |
| `SWAP` multi-word | **used** (counts 1, 3, 6, 8) | not found | **used** (40/451 pp) | no |
| `LOC` | not seen | no | **used — exactly once** | no |
| `CTL` | not seen | no | **used, 7 sites, always `CTL(SEOP)`** | no |
| **connective byte size ≠ 8** | **used** (sizes 0,1,2,4,5,7) | specified | **used** (sizes 0,1) | — |
| word 7's left-zeros / all-ones counts | **used** (Problem 4.5 is built on them) | — | **used** | — |

*(Denominators: Programming Examples 26 of 82 PDF pages read;
STRAP-II SAG 46 of 211; MCP **all 451**, so its "never" entries are
much the stronger evidence.)*

**FORTRAN IV uses no VFL at all** — `C22-6751` printed p.24: *"A
FORTRAN integer is actually represented internally as an
unnormalized floating point quantity, with a fixed exponent of 38₁₀.
This enables the floating point instruction set to be used…"*, and
its Appendix C listing contains no VFL instruction. So the one
language a casual user would reach for is the one piece of the
software stack this model is already closest to running.

**And one correction that *reduces* the estimate.** Ref. Man. printed
p.55: *"Decimal multiplication and division are not provided
directly in the machine, but their operation codes are provided."*
Decimal `*`, `/` and `*+` execute a LOAD TRANSIT AND SET plus a
two-bit tag and raise DTR — they are not decimal arithmetic at all.
So "decimal VFL" is a BCD carry rule, tens-complement, and a
re-parameterised byte converter, not a second multiplier. Its real
cost driver is the **missing binary VFL state it leans on**: the
transit register, the left-zeros and all-ones counts of word 7 as
writable architectural state, the BTR/DTR indicators, and `LTRS`
itself.

**The finding, stated plainly.** *The model's deferred list is very
nearly a list of what IBM's own application programs need.* Radix
conversion and decimal VFL are not exotic: they are **how a 7030 prints
a number**. `LVE` is not an obscure addressing curiosity: it is **how a
subroutine reads its arguments**. `SWAP` and multi-word `T` are **how a
matrix program moves a row**. Any claim that the subset is "the
instructions real software uses" is false, and this is the primary
source that falsifies it.

Note also the last three lines of the Monte Carlo extract: `CCW` copies
the control word and `BB, CWB+.24, $-1.` branches on a status bit in
it, looping until the operation completes. **That is the real I/O wait
loop**, and the model already supports exactly this shape
(`bsv/StretchIO.bsv` lines 185–195 document `CCW` as the only way a
program observes EOP here). It does *not* support the interrupt-driven
alternative — see §4.3.

### 2.3 Sizing layer 1

| item | primary source | model has it | size |
|---|---|---|---|
| **Decimal VFL (`c=1`)** | Ref. Man. printed pp.55–77 (VFL chapter; radix conversion sits inside it at pp.71–74) | no | **weeks, and less than feared.** There is **no decimal multiply or divide to build** — printed p.55: *"Decimal multiplication and division are not provided directly in the machine, but their operation codes are provided"* (they execute a LOAD TRANSIT AND SET plus a two-bit tag and raise DTR). What is left is a BCD carry rule, tens-complement, and a re-parameterised byte converter. **5–10 project-days** for that — *but* it depends on binary VFL state the model does not have: the **transit register** (word 15), word 7's **left-zeros and all-ones counts** as writable state, the **BTR/DTR** indicators, and **`LTRS`**. Add **3–5 project-days** for those, and note they are needed anyway (Programming Examples Problem 4.5 is built on the word-7 counts). |
| **Radix conversion `CV/DCV/LCV/LTRCV`** | Ref. Man.; pocket card | no | **days–a week**. Four opcodes, arithmetic-only, no new addressing. **3–5 project-days.** `LCV` is the one actually used. |
| **`LVE`** | Ref. Man. printed p.20; `docs/NEXT.md` records the search for a bit-level spec as *unresolved* | no | **days, once the spec is found; indefinite until then.** This is a *documentation* blocker, not an engineering one — see §10. The model's own README (lines 118–126) records that p.20 describes it only as "indirect addressing" with no distinct bit-level behaviour located. Perf. Char. Vol.2 gives timings for it (PDF text, "The instructions LVE and SVA were timed for all three sizes of…"), which bounds its cost but not its semantics. |
| **`SVA` (full)** | Ref. Man. | partial | **days.** Already folds into the indicator word; the general store path is the gap (`bsv/README.md` lines 380–400). **1–3 project-days.** |
| **`RNX`** | Ref. Man. printed p.27 + `jb_ax4b` routine 1244 (a complete 4-part test plan) | no (encoded only) | **days.** Fully specified *and* has a deck oracle. **2–3 project-days.** |
| **`LVS`** | pocket card | no | **days.** |
| **Transmit backward / `SWAP` / multi-word / direct count** | Ref. Man. printed pp.30–31 | no | **a week.** `bsv/README.md` "Next steps" item 3 says this needs `StretchCore`'s FSM to support an instruction that isn't done after one `step()`; the `pendingIdxWrite`/`ioPending` FSMs are templates. **4–8 project-days**, and it overlaps the multi-cycle E-box work of §8, which is the right time to do it. |
| **`LOC`** | Ref. Man. printed pp.110–111, 133 | no | **belongs to §4**, not here: `LOC` exists to navigate a channel→control→unit hierarchy the model does not have (`bsv/StretchIO.bsv` lines 62–75). Zero occurrences in the four benchmarks; MCP is the likely user. |
| **`CTL` function codes** | Ref. Man. printed pp.129–132 | 2 of them | **belongs to §4.** |
| **`KF`/`KFI`, `KFR`, `M+1`, `LTRS`** | pocket card; Ref. Man. printed pp.55–77 | no | **days each**, and three of them are *not* optional: `KF` is used heavily by both the Programming Examples and MCP (68 lines), `M+1` ~35 times in MCP, `LTRS` by decimal's own multiply/divide stubs. `KE`/`KFE` are the two the evidence says nobody uses. |
| **`PF`** | — | — | **not an instruction.** Indicator 23; see §2.1. The work is "raise the condition", inside whatever decimal-to-storage path exists. |
| **Connective byte sizes other than 8; word 7's left-zeros / all-ones counts** | Ref. Man. printed p.75 | no (`bsv/README.md` lines 141–152 record both as deliberate simplifications) | **days.** Both are *used*: the Programming Examples use connective byte sizes 0, 1, 2, 4, 5 and 7, MCP uses 0 and 1, and Problem 4.5 is built on the word-7 counts. These were reasonable simplifications for a subset and are not reasonable for a machine meant to run real software. |
| **VFL multiply / divide (`*`, `/`, `*+`, `LFT`, `LWF`, `SRD`, `+MG`, `M+MG`)** and **floating-point divide** | Ref. Man.; Perf. Char. Vol.1 Table 2 (printed pp.3-3..3-5) | no | **do NOT size this here.** These are parallel-arithmetic-unit operations, and `microarchitecture_plan.md` §6f already says why they were deferred: *"A combinational full-width divide unfolds hugely in bsc, and the real divide is iterative (~3.5 quotient bits per cycle) — it belongs in `mkArithmeticUnit`."* They are **§8 stages 4d and 4e**, counted there. Attempting them before the multi-cycle E-box refactor is the one sequencing mistake this plan most wants to avoid. |

**Layer 1 total: 25–45 project-days ≈ 1–2 months**, *excluding*
`LVE`'s unresolved specification, excluding `LOC`/`CTL` (which are
really Exchange work, §4), and excluding multiply/divide (which are
really arithmetic-unit work, §8). This layer is the *smallest* of the
eight, and it is still larger than the floating-point effort that took
eight project-days.

### 2.4 The assembler is ahead of the model, but not far enough

A useful asymmetry: `strap/opcodes.py` **already encodes** `LCV`
(line 50), `LTRCV` (51), `CV` (52), `DCV` (53), `RNX` (113), `LVE`
(114), `SVA` (115), `LVS` (comment at 139), the eight `TRANSMIT_CODES`
including `SWAP`/`SWAPI`/`SWAPB` (288–297), and the decimal modes
`D`/`DU` (`strap/strap_asm.py` MODE_BITS region, line ~385, with
`MODE_DEFAULT_BS` at 387). `strap_asm.py`'s own header (lines 111–113)
says it plainly: *"binary modes B/BU only; decimal D/DU encode but
StretchExecute.bsv flags them OP invalid"*.

**So IBM's benchmark listings can be assembled and bit-checked against
their printed machine code today** — the `verify_*_listing.py`
methodology works on them immediately, before any execution work. That
is a cheap, high-value first step (§10).

**What the assembler still lacks for them.** `strap_asm.py` implements
these pseudo-ops: `DD`, `VF`, `XW`, `END`, `SYN`, `SLC`, `CNOP`,
`NOP`, `SIC` (dispatch at lines 967–988 and 1305–1416). The Vol.2
benchmark listings additionally use `DR`, `DRZ`, `DDL`, `CW` (control
word, with flag sets like `CDSC`/`CD`/`CCR`), `SEM`, `ENTER`, `PUNID`
and `PRINID`. **Adding those is days**, and `CW` in particular would
retire the hack `tests/gen_io_tb.py` exists for (patching packed
control words into the image after assembly because `DD` cannot
resolve a label — `gen_io_tb.py` lines 4–8).

**The sequencing consequence, stated early because it shapes
everything:** the decimal and radix-conversion work (§2.3) is SAU
work, and multiply/divide is PAU work. Both are cheaper *after* §8's
step 4b (splitting `execute()` into a multi-cycle arithmetic-unit
module) than before it, because before it they go into a 1,179-line
combinational function (`bsv/StretchExecute.bsv:3448–4626`) that is
already 48% of the model's source. **Do `LVE`, `SVA`, `RNX`, `LVS`,
Transmit and the `CTL` codes early; hold decimal, radix conversion
and multiply/divide until after 4b.**

---

## 3. Layer 2 — the interruption and alarm system

### 3.1 What is built

This is the one layer that is largely done, and it is worth saying
precisely how done, because the rest of the roadmap leans on it.

| piece | file:line |
|---|---|
| Enable flip-flop | `bsv/StretchStorage.bsv:240` `Reg#(Bool) irqEn <- mkConfigReg(False);` (reset = disabled) |
| Mask register (word 12) | `bsv/StretchStorage.bsv:268` |
| Indicator register (word 11) | `bsv/StretchStorage.bsv:258` |
| Interruption address register (word 2) | `bsv/StretchStorage.bsv:247` |
| Boundary registers (word 3) | `bsv/StretchStorage.bsv:248` |
| **The whole priority decision, 14 lines** | `bsv/StretchStorage.bsv:303–316` `rule intDueCalc` — `pending = indicators & mask`, leftmost-set scan, `iar + n` |
| Taking the interruption | `bsv/StretchCore.bsv:551–588` `rule rl_interrupt`, armed by `armInterrupt` at `:319–323` |
| Storage protection / address monitoring | `bsv/StretchExecute.bsv:416–425` `protViolates`, gated `st.irqEnabled() && installed(a) && signalled` |
| DS / DF (incl. the mask-dependent half) | `bsv/StretchExecute.bsv:752`, `:859`, `:1138` |

Deck-verified in part: `docs/NEXT.md` §1 records bit-exact
transcriptions of `jb_ax5b` routine 1260's `TS`, `OP`/`AD` and `DS`
blocks, the indicator walk, both boundary-register halves and the
comparison driver, plus `I60S1`.

### 3.2 What is left, and which of it real software needs

| open item | source | does real software depend on it? |
|---|---|---|
| **Interval timer and time clock actually ticking** | Ref. Man. printed p.34; `docs/NEXT.md` §5 | **YES, decisively.** `bsv/StretchStorage.bsv:246` `intervalTimerAndClock` has exactly one reader (`:391`) and one writer (`:480`, a program store) and **nothing steps it**. `addrTimeClock` (`bsv/StretchTypes.bsv:52`) is an alias for the same word, so there is no time clock either. Every one of IBM's four benchmark programs times itself off it (Vol.2 PDF p.5 = printed p.2, `SC, $X2, 1.0 'INTERVAL TIMER RESET`). MCP schedules on it. And `BEW`'s wait cannot be tested without it (`docs/NEXT.md` §3). **This is the single highest-value open item in the whole roadmap relative to its cost**: `bsv/StretchCore.bsv:123` already has a free-running `Reg#(Bit#(32)) clk` incremented at `:329`. Wiring it to word 1 at 1 tick per 3,255 model clocks (Ref. Man. p.34: 1,024 pulses/s; 0.3 µs/clock) is **days, not weeks** — with the reload-rule hazard `NEXT.md` §5 documents at length, and routine 1258 as its deck oracle. |
| **Actuation priority** (Ref. Man. printed p.51: only the higher-priority indicator is actuated; `IF` outranks `AD`) | `docs/NEXT.md` §5a | **Probably not for a bootstrap or SSIP**; `NEXT.md` §5b states outright it *"has no deck oracle — implement it from the manual or not at all"*. MCP's interrupt dispatcher reads the indicator register after vectoring, so a wrongly-actuated second indicator could mislead it. **Days.** |
| **`AD` for a branch below 32** | `docs/NEXT.md` §1 | Diagnostics provoke it deliberately. **Days.** |
| **`USA`'s one-millisecond timeout** | Ref. Man. p.45 item 17; `docs/execution_operations.md`; Perf. Char. Vol.1 printed p.3-2 for the 0.3 µs cycle | **No**, except that `jb_ax5b` TEST 1D is its oracle and requires it jointly with the disabled-state exception. **Days**, and `NEXT.md` §5e has the whole design including why the obvious implementation fails. |
| **p.50's two disabled-state exceptions** (monitoring always in force during `EX`/`EXIC`; interruption always permitted at an execution operation's boundary) | Ref. Man. printed p.50 | **No for application code; yes for the decks.** `NEXT.md` §5e sizes them at ~20–30 and ~40–60 lines and names five untranscribed deck blocks. **Days.** Note `execOpInProgress`, the method `NEXT.md` proposes, **does not exist**: grep finds it only in `docs/NEXT.md:1732` and `docs/execution_operations.md:294`. |
| **`AD` is not raised by the storage layer at all** | Ref. Man. printed p.32 | **Yes, eventually.** `ind_AD` is set at exactly four places (`bsv/StretchExecute.bsv:3936`, `:4012`, `:4102`, `:4232`) and the only `!installed` check is the floating-point one at `:4231`. An out-of-range VFL, index, Transmit or I/O access reads 0 and sets nothing (`bsv/StretchMemory.bsv:186–189`, and the in-source admission at `:46–48`). A real loader that probes memory size would see no error. **Days–a week.** |
| **The look-ahead unwind** — an I-box instruction that overtook a pending level cannot be taken back | `bsv/StretchCore.bsv:300–318` | **No for software; yes for cycle accuracy.** This is §8 work, not §3. |
| **An E-box-class interruption instruction** | `bsv/StretchCore.bsv:637` ("not implemented", fails loud) | Probably **yes for MCP**, whose interrupt routine is not trivially I-box-only. **Days.** |

**Layer 2 total: 3–6 project-days for the timer, 8–15 for everything
else ≈ 2–4 weeks.** This is the cheapest layer with the highest
leverage, because the timer unblocks `BEW`'s wait, self-timing
benchmarks (§8's oracle), and MCP scheduling at once.

---

## 4. Layer 3 — the Exchange and real I/O

*(§4.1 and §4.3 verified first-hand from page images. §4.2 and §4.4
rest on a research pass over the same documents; quotes are
reproduced with their page citations and are marked where they were
not independently re-read.)*

### 4.1 What the Exchange is

Reference Manual **printed p.104 (PDF p.107)**, "IBM 7619 Exchange",
read first-hand, with Figure 34 "Exchange Components" on the same
page:

> *"The IBM 7619 Exchange directs information flow between
> input-output units and core storage. … It contains the common
> control facilities to be time-shared among the external units, thus
> keeping these units as simple as possible, yet maintaining fully
> overlapped operation. … **The only core storage cycles required
> during external operations are those needed to transfer the data to
> or from the final locations in core storage. These cycles are
> sandwiched between computing operations without interfering with the
> computer program** except for the slight delay involved in the
> actual core storage references."*

Structure, from Figure 34: a buffer register and address registers on
the core-storage side, error checking and correction, **Exchange
Storage (ES)** with its own address control, data-word shifting
(byte↔word assembly), control-word modification, and a **channel
scanner and switch** facing the external control units.

Capacity, same page, verbatim:

> *"The exchange provides up to 32 channels… These units are of the
> kind that operate serially one 8-bit byte at a time, and thus
> require eight bytes to transmit a full storage word of 64 bits. The
> channels are nine bits wide, accommodating an 8-bit byte and a
> parity bit… **a channel can achieve data rates of one byte every 16
> microseconds**, but higher rates can be accommodated. … **The
> minimum is eight.** This minimum can be augmented by additional
> channels in groups of eight up to 24 additional, or a total of 32
> channels. **Each exchange channel is connected to one control unit.**
> Most control units are designed to handle only one specific external
> unit… Other control units are capable of handling more than one
> input-output or external storage device"*

Figure 34 numbers the channels **32, 33, 34, 35 … 63** — which is why
`bsv/StretchIO.bsv:216–218` puts its three stubs at 32, 33, 34. The
model's channel *numbering* is right; everything behind it is not.

Two numbers worth putting side by side:

| | real 7619 | this model |
|---|---|---|
| transfer granularity | one 8-bit byte, 9 bits wide with parity | one 64-bit word |
| rate | one byte / 16 µs ⇒ **128 µs per 64-bit word** | one word per `step()` = **0.3 µs**, i.e. **~427× too fast** |
| overlap with the CPU | *"fully overlapped"*, core cycles *"sandwiched between computing operations"* | none: every other core rule is gated on `!isValid(ioPending)` (`bsv/StretchCore.bsv:245–324`) |
| channels | 8 minimum, up to 32, each to one control unit which may front several units | 3 fixed, one device each, no control-unit layer |
| buffering | Exchange Storage + buffer register + byte↔word shifting | none (which is why the WRITE "+2" rule is deliberately not reproduced — `bsv/StretchIO.bsv:165–180`) |

**That table is the Exchange layer.** It is not an extension of
`StretchIO.bsv`; it replaces it. A byte-serial, asynchronous,
32-channel, ES-buffered bus requester competing with the I-box and
look-ahead for memory cycles is a module on the scale of
`StretchMemory.bsv` + `StretchLookAhead.bsv` together, and it brings
with it the status state machine of §4.3 and the channel→control→unit
hierarchy that `LOC` exists to navigate.

Sized in §4.5. Two unread deck oracles exist for it —
`ka_ex1_bx-0.pdf` and `ka_ex1b_bx-0.pdf`, which
`docs/archival_inventory.md` records as needing *"the exchange as a
real bus requester"*.

### 4.2 What a *typical* installation had — IBM's own word for it is "average"

The single best sentence in `docs/`, and it is IBM's own.
**`A22-6552_physPlan_Jul61.pdf` printed p.6 (PDF p.6)**, repeated
identically in `A22-6552-1_physPlan_Feb63.pdf` printed p.6 (PDF p.7):

> *"An average 7030 system will consist of a central processing unit,
> exchange, power distribution unit, **six core storage units**, three
> tape controls, eight magnetic tape units, card reader, card reader
> control, printer, printer control, card punch, card punch control,
> console control, console, disk synchronizer, and a disk storage."*

Three columns, because no two delivered machines were alike:

| type | what it is | MCP **minimum** | physPlan **"average"** | model |
|---|---|---|---|---|
| **7101** | Central Processing Unit | 1 | 1 | ✔ |
| **7619** | Exchange | 1, minimum 8 channels | 1 | ✘ (3 stub channels) |
| **7302** | Core Storage, 16,384 words (Model I) | **3** units | **6** units | ✔ **exactly right** |
| **7803** | Power Distribution Unit | — | 1 | n/a |
| **7613** | Tape Control, up to eight 729 IVs, one active at a time | ≥1 | **3** | ✘ |
| **729 IV** | Magnetic Tape Unit | **≥4** | **8** | ✘ (1 stub) |
| **7503 / 7614** | Card Reader, 1000 cards/min, + its control | 1 | 1 | ✘ (stub) |
| **7553 / 7615** | Card Punch, 250 cards/min, + control | not required | 1 | ✘ |
| **1403-2 / 7616** | Printer, 600 lpm, + control | not required (off-line via 1401) | 1 | ✘ (stub) |
| **7152 / 7623** | Operator's Console + control | 1 | 1 | ✘ |
| **7612** | Disk Synchronizer | 1, *"with at least one disk unit"* | 1 | **✔ (boot minimum, 2026-10-18)** |
| **353** or **7303** | Disk Storage (type number disputed, §4.4) | ≥1 | 1 | **✔ (two arcs, no timing)** |
| **IBM 1401** | *off-line* satellite: card→tape, tape→print, tape→punch | **required by MCP** | — | ✘ |

MCP's minimum is stated outright —
`C22-6678-1_7030_MCP_Reference_Jun64.pdf` printed p.6: *"An IBM 1401
Data Processing System (Tape-Oriented), used for off-line operation. A
minimum of three IBM 7302 Core Storage units. An IBM 7612 Disk
Synchronizer **with at least one disk unit used to store system
programs and as auxiliary storage for the problem program**. An IBM
7619 Exchange with the minimum eight basic exchange channels."*

**The model's memory configuration is exactly the typical one, and it
is the only part that is.** Triply sourced: Perf. Char. Vol.1 printed
p.A-1 (*"six boxes of 16,384 extended words each (for the Los Alamos
configuration)"*, read first-hand), Buchholz printed p.202 (*"A
typical 7030 system may have six memory units… The first four units
share a block of 65,536 addresses… The next two units share a block of
32,768 addresses with two-way interleaving"* — which is exactly
`bsv/StretchMemory.bsv:67–71`'s interleave map), and
`LASL_Jun61Article.pdf` printed p.5 (*"98,304 'words' of 64 bits
each… not to mention eight extra bits per word"*).

**And LASL — a real installation — ran the *minimum* eight-channel
exchange**, not 32: `LASL_Jun61Article.pdf` printed p.4,
*"Communications in both directions between Stretch and the rest of
the world normally flow through **eight** electrical 'channels.'"*
That is a useful bound on what "typical" has to mean: **eight
channels, not thirty-two.**

### 4.3 How channel status reaches the CPU — read first-hand, and it is a state machine

Reference Manual **printed p.118 (PDF p.121)**, "Setting up of
Input-Output Indicators", verified first-hand at 160 dpi. This is the
single page that defines everything `bsv/StretchIO.bsv:185–197` says
is "NOT PROPAGATED", and it specifies considerably more than five
bits:

> *"When an operation concerning an external unit has been terminated
> and at least one of these five status bits in the control word is
> on, the exchange attempts to set up the corresponding indicator or
> indicators and thus cause an interruption of the program. **All of
> the status indicators for a particular channel are set up as a group
> at one time. At the same time, the address of the channel causing
> the interruption is entered into the channel address register.**"*

Two preconditions, both quoted verbatim:

> *"1. The five input-output status indicators (EPGK, UK, EE, EOP, and
> CS) in the indicator register have previously been reset to zero
> either by permitting an interruption to occur or by turning them off
> by means of a BRANCH ON INDICATOR instruction.
> 2. The interruption system is currently enabled."*

and the consequence of failing either:

> *"If either condition is not satisfied, the status bits remain set in
> the control word, and another attempt to turn on the indicators is
> made a short time later. **While the status bits are in the control
> word, further instructions for this channel are rejected by means of
> a channel busy reject.**"*

Three further rules the model has no counterpart for:

- **One channel at a time.** *"While interruptions due to one channel
  are being processed, the exchange holds up any other status reports
  due to the same or other channels."*
- **A priority scanner.** *"the order of interruption is determined by
  a scanner in the exchange. The channel that gets the highest
  priority is the one specified by the current position of the
  scanner… when an input-output instruction is issued, the scanner is
  set to the channel to which the instruction is addressed."*
- **The documented idiom that exploits it**: *"if, while still
  disabled, the program issues a COPY CONTROL WORD immediately
  followed by BRANCH ENABLED, the highest interruption priority is
  assigned to the channel to which the COPY CONTROL WORD is
  addressed."*

**What this means for the model.** `bsv/StretchIO.bsv`'s "NOT
PROPAGATED" note is honest but understates the gap: closing it is not
"set `ind_EOP`", it is a per-channel status-report state machine with
a reject interlock and a round-robin scanner. Hence A2's **1–2 weeks**
rather than days. Note, though, that the *polling* path a real
program uses — `CCW` the control word into storage, `BB` on its status
bit (Perf. Char. Vol.2 printed p.30, §2.2) — **works on this model
today**, because `CCW` is implemented and `BB` can test any bit in
storage. Indeed the manual says polling is the *only* option when
disabled, because the indicators never come on at all: printed p.119,
*"If a program interruption due to input-output status is not
desired, the system can stay disabled, and the status bits can be
obtained from the exchange by means of COPY CONTROL WORD. Thereafter,
the status bits in the control word can be reset by means of RELEASE
SEOP."* **So milestone A3 does not need this work.** It is needed the
moment anything wants to overlap I/O with computation — which is to
say the moment MCP appears. It is step **B1**.

### 4.4 The disk — present in the average system, and fully documented

**Yes, a typical 7030 had disk, and `docs/` specifies its programming
interface completely.** The Reference Manual has a chapter, "HIGH-SPEED
DISK SYSTEM", printed pp.157–162 (PDF pp.160–165), revised in the
August 1961 edition.

- **It is not an Exchange channel.** Printed p.157: the **IBM 7612
  Disk Synchronizer** *"provides the common control and data transfer
  paths for the disk system… Basically, the method of control is the
  same as that used in the exchange. However, the high rate of data
  transmission… causes some differences."* Buchholz printed p.20:
  *"a single-channel device designed specifically to handle the high
  data rate of the disks. The exchange and the disk synchronizer can
  operate independently and simultaneously at full speed."* It is a
  **separate memory-bus requester** — and `bsv/StretchMemory.bsv`'s
  MBCU currently has one requester (`microarchitecture_plan.md` §7
  Stage 1: *"Not yet modeled: the eight-channel priority
  arbitration"*).
- **Capacity and rate.** 2,097,152 (2²¹) words per unit; 4,096 arcs of
  512 words; one full word every **8 µs** = 125,000 words/s; arm
  positioning up to 265 ms; up to 32 disk units, one transferring at a
  time (printed pp.157–158).
- **It is programmed with the same five instructions**, with `LOC`
  carrying the **arc address** rather than a unit selection (printed
  p.160: *"positions 38-49 specify the arc address"*), and
  **`CTL` is invalid**: *"The CONTROL and CONTROL (SEOP) instructions
  have no meaning for disk storage and will set the EPGK indicator."*
- **Control-word differences:** *"No use is made of control word flag
  bits or refill field… Only the data word address field and word
  count field… are retained"* (printed p.158), and there is no
  per-channel control-word storage (printed p.161), so `CCW` during a
  transfer is rejected channel-busy.

*(Type-number conflict, recorded: both physical-planning manuals say
**IBM 353 Disk Storage** (printed p.6); `D22-6513` printed p.20 and
`R23-9702`'s block diagram say **IBM 7303**; the Reference Manual
names only the 7612 and "the storage unit". Not resolvable from
`docs/` — §11.)*

**The disk is therefore not a documentation gap. It is a work item**,
and MCP requires it (§6).

> **BUILT, 2026-10-18 — the boot minimum, not a faithful 353.**
> `bsv/StretchDiskSource.bsv` plus the arc address register, an
> arc-addressed `LOCATE`, `RD`/`W` streaming arcs, the short write's
> zero-filled tail, `CCW`, and the control word's flags and refill
> discarded. Nineteen checks in `decks/io_disk.strap`, in the suite.
> `docs/disk_subsystem.md` §9a is the record.
>
> **What is NOT built is the whole of §4.4's timing** — the
> three-point seek, the rotational distribution, 8 µs per word,
> automatic access elimination, the dual access mechanism — and the
> backing store is two arcs rather than 2²¹ words. A functionally
> correct program cannot see the difference; a cycle-accurate one is
> nothing but the difference. The ticks above mean layer 3's
> *functional* row, not layer 4's.
>
> **And building it moved the critical path somewhere else.** With a
> disk at channel 0, MCP's bootstrap stopped taking a spurious
> error exit — and an `OP` indicator appeared that an interrupt had
> been wiping. Printed p.4 line 28's eleven-word `TRANSMIT` is
> refused by the model, so **MCP's IPL is never moved**. The disk was
> never the gate; `TRANSMIT` is. `docs/NEXT.md` has it.

### 4.5 Sizing layer 3

| piece | size |
|---|---|
| **Chaining + multiple-block + skip**, properly (Figure 36's truth table, printed pp.108–109; the chaining-at-count-2 rule, printed p.125) | **1–2 weeks**, and the chaining half is a prerequisite for IPL (§5.4) |
| **B1: the status-report discipline** of §4.3 — group set-up, two preconditions, channel-busy reject, one-channel-at-a-time, the round-robin scanner, the destructive channel-address register (printed p.119: *"the effect of the register is the same as that of location 0"* after reading) | **1–2 weeks** |
| **The reject indicators** EKJ / UNRJ / CBJ as real, permanently-masked, interrupt-before-next-instruction conditions (printed p.112) | **days–1 week** |
| **Byte-serial, asynchronous transfer** with Exchange Storage, byte↔word assembly, the 10 µs exchange cycle (printed p.119), the 100,000 words/s ceiling (printed p.105), and genuine CPU overlap | **4–8 weeks.** This is the heart of it and it is a rewrite of `StretchIO.bsv` plus the `ioPending` FSM plus a second MBCU requester |
| **MBCU priority arbitration** — Buchholz printed pp.205–206: *"the exchange and disk synchronizer will get highest priority, followed by the CPU… the memory bus unit receives requests from and assigns priority to eight different channels"* | **1–2 weeks** |
| **`LOC` and the channel→control→unit hierarchy** (3-bit selection address, bits 47–49; up to 8 units per control; sticky per channel) | **1–2 weeks** |
| **Real devices**: 7503 card reader (960-bit column-binary card image = 15 words no-ECC / 13 ECC, 60 ms card cycle, one byte per 62 µs, the end-of-file-by-SIGNAL-key convention), 1403-2 printer, 7553 punch, 729 IV tape with its 14 CONTROL codes, 7152 console typewriter with its own data-byte function codes | **4–8 weeks** for the set |
| **The disk**: 7612 synchronizer as a second requester, arc addressing, `LOC`-as-seek | **3–6 weeks** |

**Layer 3 total: 15–30 weeks ≈ 75–150 project-days ≈ 3–7 months.**

**This layer is larger than everything this project has built so
far** — 28 project-days — by a factor of three to five, and it has no
regression suite behind it (§0's caveat), only two unread deck
oracles. **It is the single biggest piece of work in this document
after cycle accuracy, and the two are roughly the same size.**

---

## 5. Layer 4 — bootstrap: how a real 7030 comes up

**This layer is fully specified by the documents present.** §5.3 gives
IPL's exact hardware action, quoted from the page.

### 5.1 The operator sequence

`jb_ax4b_ibox-4.pdf` printed p.1 gives the console procedure for
running a diagnostic: *"Depress Master Reset / Depress Start Clock /
Depress IPL / Disable Interrupt and Time Clock / Enable Maintenance
Mode"*, with a binary deck in the card reader.

### 5.2 What IPL does, from the loader's own side — read first-hand

`docs/ka_ul1_load_and_tape_write_util.pdf` is the *Load and Tape Write
Utility*, KA UL1, October 13 1961 (18 PDF pages, printed pages 1–…;
PDF p.1 carries printed pp. title+1, PDF p.2 carries printed pp.2–3,
i.e. **two printed pages per PDF page**). Printed p.1, verbatim:

> *"The Loader and Tape Write program is designed to load any punid
> deck into any 7030 DPS. **It is a punful deck and is placed on the
> front of the punid deck to be loaded. This deck is then placed in
> the card reader and an IPL given to the card reader.**"*

**Three things follow, and they settle the bootstrap model:**

1. **IPL is given *to a device*** — "an IPL given to the card reader".
   The device is therefore selectable, not hardwired, and the console
   is where it is selected.
2. **The loader is an ordinary card deck placed in front of the
   program deck.** The hardware's job is only to get *enough* of that
   deck into core to start it; the deck does the rest. So the amount
   the hardware reads is small, and whatever it is, the loader deck's
   first card is written to fit it.
3. **The operator passes options to the loader in console switches,
   before pressing IPL, and the loader reads them out of storage.**
   Printed pp.1–2, verbatim: *"Two switch options are available to the
   operator and must be set prior to giving the IPL… **Switch 32** –
   If this switch is set to zero all of core, above the loader, and
   all special registers will be cleared… **Switch 37** – When set to
   a one, this switch will initiate the writing of the IPL tape…
   **Switches 12-17** are used for the channel selection and **21-23**
   are used for drive selection. **If channel 32 (40₈) and drive 0 are
   to be used, these bits may all be set to zero**… The loader program
   **fetches and saves the switch setting**."* And errors are reported
   back to the operator through a register he can read on the console:
   *"By corralating the number displayed in the **lower bounds
   register** with the following list, the operator can determine the
   type of error"* (codes 000100, 000101, 000102, 000103 …).

   **Switches are numbered 12–17, 21–23, 32, 37, 63** — IBM bit
   numbering over a 64-bit word — and **the program's own source
   calls them `MS`**. KA UL1 PDF p.5 (the listing's `PRNS` header
   block, read first-hand): *"CLEARING OF MEMORY IS BYPASSED IF **MS
   32** IS SET PRIOR TO IPLING IN THE LOADER"*, *"THIS OPTION CAN BE
   SELECTED BY SETTING **MS 37** TO EQUAL ONE"*, *"PLACE CHANNEL
   ADDRESS, IN OCTAL, IN **MS 12-17**"*, *"PLACE DRIVE NUMBER IN **MS
   21-23**"*, *"IF THE ABOVE BITS ARE ALL ZERO, CHANNEL 32 %40 OCTAL%
   AND DRIVE 0 WILL BE USED"*, *"AS SOON AS THE LOADER PROGRAM STARTS
   LOADING THE SUBJECT PROGRAM, ANY **MAINTENANCE SWITCHES** MAY BE
   CHANGED"*.

   **`MS` = Maintenance Switches, and the pocket card names special
   storage word 4 "Maintenance Bits, 0-63"** (X22-6533-1, transcribed
   at `docs/microarchitecture_plan.md` §A.10). That identification is
   a one-step inference, but a well-supported one: the numbering
   (0–63) matches, the name matches, and the loader *reads* them
   ("the loader program fetches and saves the switch setting"), which
   requires them to be program-visible storage. **The model already
   has word 4 as a plain read/write register with no semantics**
   (`bsv/StretchStorage.bsv:251`, read `:394`, written `:485`) — so
   the console's switch panel has a home in the model already; it
   needs a driver, not a new architectural concept. §11 records the
   remaining confirmation as a console-manual item.

5. **And KA UL1 is itself a transcription target.** PDF pp.5–18 are a
   STRAP source listing (PDF p.5 opens with the `PRNS` header comment
   block quoted above). That is **a complete, real card loader in
   ~14 pages** — far smaller than the DCP's 130 and smaller than
   SSIP's 46 — and it is the natural program for milestone A3 to run.
   `docs/archival_inventory.md` lists it only as *"needs tape I/O"*,
   which is true of its *tape-write* half; its *card-loader* half
   needs only the reader.

4. **Core layout.** Printed p.3: *"Any program employing the Loader
   and Tape Write program should not attempt to load any registers
   between 40.00₈ and 601.00₈"* (octal 40–601 = decimal words 32–385),
   and *"An origin card has a starting address lower than (8) 602.00.
   This program cannot be loaded."* So **the card loader occupies
   words 32–385 and loaded programs start at octal 602 (decimal 386)
   or above.** This is independently consistent with the memory map
   `docs/archival_inventory.md` attributes to
   `7030_SystemTestPrograms_Aug61.pdf` ("control/dispatch at 64-192,
   tape loader at (8)100-(8)777, all test programs run above (8)1000")
   — a different loader, a different map, the same architecture: a
   low-core resident loader, programs above it.

### 5.3 WHAT IPL ACTUALLY DOES — Reference Manual printed p.126, verbatim

**Found, and it is completely specified.** The *mechanism* is in the
**Exchange chapter** of the Reference Manual, printed pp.125–126 (PDF
pp.128–129), read first-hand at 160 dpi — not in the console manual,
which deliberately punts to it. This is the single most actionable
finding in this document.

**First, what pressing the key itself does.**
`R23-9713_7101_Maint_Console_1961.pdf` printed p.26, §4.4.2 "Pulse
Switches", entry *Initial Program Load (A14)*, verbatim and complete:

> *"The initial program load switches on the IBM 7152 Operator's
> Console, the exchange maintenance console, and the CPU maintenance
> console **all produce the same results**, as follows:
> 1. Execution of any program by the CPU is interrupted by
> terminating the instruction in execution at the time the switch is
> depressed. All storage locations and registers which were altered
> prior to the termination are not restored to a former or
> predetermined state.
> 2. The interruption system is temporarily disabled.
> 3. All input-output operations on the exchange are terminated.
> 4. All control words in the exchange are reset to zero.
> 5. **The exchange is set to interpret the next channel signal in a
> special way.**
> 6. The contents of the instruction counter buffer are transferred
> to the instruction counter register if the depression of IPC occurs
> in arithmetic mode."*

Item 5 is the whole mechanism in one sentence, and the console manual
says nothing further — no device, no address, no branch target. The
rest comes from the Exchange chapter.

Two consequences worth noting before the sequence: there are **three
IPL keys** (operator's console, exchange maintenance console, CPU
maintenance console) and they are equivalent; and the key is *"not an
integral logical part"* of the operator's console — *"If the system
does not contain an operator's console, it is provided in a separate
box, which may be placed at a convenient operating point"* (Ref. Man.
printed p.125).

> *"The first channel signal indication received after the depression
> of the INITIAL PROGRAM LOAD key from a unit accommodated by the
> exchange initiates the following sequence of events:*
>
> ***1.** The exchange automatically stores in the control word
> location for the channel responsible for the channel signal a fixed
> control word with the following contents:*
>
> | | |
> |---|---|
> | *Data word address* | *= 4* |
> | *Chain flag* | *= 1* |
> | *Multiple flag* | *= 0* |
> | *Skip flag* | *= 0* |
> | *Count* | *= 1* |
> | *Refill address* | *= 4* |
>
> ***2.** The exchange initiates a READ for the indicated channel,
> using the fixed control word.*
>
> ***3.** The first word read from the unit is stored in the special
> core storage location referred to by means of address 4. Since the
> fixed control word is then exhausted, its refill address causes the
> next control word to be fetched from location 4. Location 4 at this
> time should contain another control word specifying the address at
> which the word immediately following should be stored, and the
> number of words to be read from the unit. Reading then proceeds
> normally.*
>
> ***4.** If and when the READ operation is completed as specified by
> the control word or words without causing the exchange-program-check
> or unit-check indications, the exchange sends an **initial start
> signal** to the computer. … The EOP as well as the EE indications,
> however, are not turned on upon the completion of the operation.*
>
> ***5.** The computer, upon receipt of the initial-start signal,
> **fetches and executes the instruction in the location specified by
> the data word address field of the control word in core storage
> location 4.** The address of this instruction, however, is not
> placed in the instruction counter. Unless specified otherwise by
> this instruction, the interruption system after the completion of
> this instruction returns to the state it was in at the time the
> INITIAL PROGRAM LOAD key was depressed. This completes the initial
> program loading sequence."*

**In one sentence: IPL is a one-word chained READ whose single word
*is the next control word*, and then a single-instruction execute at
the address that control word names.** The medium's first word is a
control word, not code.

Five more rules from the same two pages, each load-bearing:

- **The trigger is a channel signal, not the key.** *"the initial
  program loading is started by a channel upon the depression of the
  SIGNAL or START key on any unit accommodated by that channel
  address."* Pressing START on a loaded card reader is what boots the
  machine; the IPL key only arms it. The card-reader CE manual agrees
  from the device side (`R23-9702`, printed p.68: *"This signal is
  used through the machine program to request a read operation or for
  the initial program load operation… the channel signal is
  automatically turned on for the initial run-in operation only."*)
- **Selection address 0 only.** *"a program can be loaded by the
  initial loading technique only from a unit having the selection
  address 0."*
- **The first instruction must be `BD`.** *"the first instruction of a
  program loaded by means of the initial program loading technique
  must be BRANCH DISABLED. This instruction replaces the contents of
  the instruction counter and insures that the system does not return
  to the enabled state."* Because step 5 does **not** set the
  instruction counter, the one executed instruction must branch, or
  control falls back to whatever the IC held when the key was pressed
  — which the manual says *"cannot be properly executed"*.
  *"If the BRANCH DISABLED is preceded by STORE INSTRUCTION COUNTER
  IF, the original contents of the instruction counter can be made
  available to the programmer"* — which is exactly the `SIC`+`BD`
  pair this model already executes.
- **Address 4 is special, and the Exchange is otherwise barred from
  0–31.** Printed p.108 (PDF p.111): *"The exchange has access to data
  and control words at any existing core storage address from 32 up.
  … **An exception is made during initial program loading, when
  storage address 4 is used in a special way without giving an error
  indication.**"*
- **Failure mode.** *"If the READ as described in 3 and 4 is not
  successful, the input-output unit comes to a stop. In order to
  restart initial program loading, the INITIAL PROGRAM LOAD key has to
  be pressed again."*
- **IPL also violates three architectural rules on purpose, which is
  what "a special interpretation" means.** Ref. Man. printed p.34
  says of the special registers: *"2. The special registers are not
  valid refill addresses for index or control words. 3. The control
  word for an input-output operation cannot be located in a special
  register. 4. Data cannot be transmitted to or from the special
  registers in an input-output operation."* IPL's synthesised control
  word (data address 4, refill 4) breaks all three. And printed p.108
  carves it out explicitly: *"An exception is made during initial
  program loading, when storage address 4 is used in a special way
  without giving an error indication."*

**There is no fixed entry address, and two real decks prove it.**
`ja_ua1_ssip.pdf`'s last line is `END,%8@100.` — octal 100, decimal
64. `ka_ex1_bx-0.pdf`'s deck opens with `CW(CD),START,END-START+1,,0`
annotated *"@IPL CONTROL WORD"*, assembled at a dummy location
outside the program, whose data-word-address field is **octal
100000** — exactly the listing address of its label `START`. Two
decks, two entry points three orders of magnitude apart. **The entry
point is whatever the deck's own control word says**, which is also
why the "control/dispatch at 64–192, tape loader at octal 100–777"
map of §5.2 item 4 is a *software convention* of the System Test
Programs suite and not a hardware fact. (Independently: Ref. Man.
printed p.33 — *"Instructions cannot be executed from storage
locations 0-31"*, which sets the floor that makes octal 100 a natural
convention.)

**Implementing this in the model is small and entirely specified** —
and the model's control-word layout is already bit-exact against
Figure 35 (`bsv/StretchTypes.bsv:204–219`: `dataAddr = w[63:46]` =
IBM 0–17, status 18–24, flags 25–27, `count = w[35:18]` = IBM 28–45,
`refill = w[17:0]` = IBM 46–63), so the fixed IPL control word is
directly expressible today. It is: a fixed `ControlWord` constant, one chained READ through the
existing `ioPending` FSM (chaining itself is the only piece not yet
built — `bsv/StretchIO.bsv` captures the chain flag and the FSM
ignores it), a write to special word 4, a re-read of word 4 as the
next control word, and a one-shot "execute the instruction at
`word4[0:17]` without stepping the IC", which is structurally the same
thing `rule rl_interrupt` already does with `intPC`
(`bsv/StretchCore.bsv:551–588`, `:99`). **Estimate: 3–5
project-days**, and `jb_ax4b` printed p.1's console procedure plus KA
UL1's deck give it two independent end-to-end oracles.

**The word-4 puzzle, now largely resolved.** Earlier in this
document's drafting it looked contradictory that address 4 is both
*"Maintenance Bits"* and IPL's control-word slot. **The Reference
Manual states both roles in one paragraph.** Printed **p.35 (PDF
p.38)**, heading "Maintenance Bits", read first-hand at 170 dpi,
verbatim and complete:

> *"The 64 bits of storage location 4 are reserved for maintenance
> purposes. **These bits are active only when the machine is in the
> maintenance mode. When it is not in this mode, they act like the
> bits of location 0.** After an initial program load, this location
> contains the first word read from the input unit. **This is the
> control word for the initial load.** Any store to location 4 causes
> it to contain a 0 with correct check bits."*

So word 4 is a deliberately dual-purpose location, and the IPL use is
documented, not accidental. The console manual's side agrees:
maintenance mode (switch F49) *"enables … the program controlled
references to storage address 04"*, and the 64 panel keys are *"a
data source for storage address 4 when in the test mode"*
(`R23-9713` printed p.19).

**What remains open is narrow**: the panel-key substitution is
described as applying to *program controlled* references, while IPL's
write to location 4 comes from the **exchange**. That reading makes
everything consistent, but no page in `docs/` says it in those words
— and every documented IPL procedure has maintenance mode *enabled*
during the read. §11 item 5 keeps it, now as a one-clause question
rather than an apparent contradiction.

*(The same page also confirms §3.2's timer facts: the time clock is
36 bits at location 1 bits 28-63, stepped by **the same 1024 c/s
oscillator** that updates the interval timer, *"The two clocks are
updated consecutively in the same time interval"*, full cycle about
777 days.)*

### 5.4 Sizing layer 4

Small, and that is the point. Given the answer to §5.3:

| piece | size |
|---|---|
| **Control-word chaining** in the transfer FSM. IPL *is* a chained read, so this is a prerequisite, not an optional Exchange feature. The chain flag is already captured in the control word and ignored by the FSM (`bsv/StretchIO.bsv` INSTRUCTIONS note; `bsv/StretchCore.bsv:377–466`). Rules at Ref. Man. printed pp.108–109 (Figure 36's multiple×chain table) and p.125 | **3–6 project-days — or 1–2 if scoped.** p.126's sequence needs exactly **one** refill, to a fixed address, with count 1 and the multiple flag off. Special-casing *that* path is a fraction of implementing Figure 36's full multiple × chain truth table, and the general case can wait for layer 3. **Take the narrow scope; it pulls A3 in by about a week.** |
| An `ipl(channel)` method on `StretchCore`: the fixed control word, the chained read, the write-and-reread of word 4, and the one-shot execute at `word4[0:17]` without stepping the IC | **3–5 project-days** |
| Master Reset / the power-on channel state | **1–2 project-days** (`bsv/StretchIO.bsv:281–285` already approximates Ref. Man. printed p.126's channel reset) |
| Console switches readable by a program | **1–2 project-days** (the register exists at `bsv/StretchStorage.bsv:251`), modulo the word-4 puzzle in §5.3 |
| A card reader big enough for a real deck | **see step 0b.** A card is **960 bits = 15 words** in no-ECC mode, 13 in ECC mode (Ref. Man. printed pp.138–140). `DeviceWords = 32` therefore holds **two cards**. A real loader deck is hundreds. **1 day if raising the typedef elaborates; weeks if it forces the BRAM treatment.** |
| Transcribe and run KA UL1's card loader | **1–2 weeks** (§5.2 item 5) |

**Layer 4 total: ~3–5 weeks**, and it is the cheapest layer in this
document relative to how much it changes the character of the thing.
It is what turns a testbench into a machine.

---

## 6. Layer 5 — the software stack

### 6.1 MCP requires the disk, and that is the headline

`C22-6678-1_7030_MCP_Reference_Jun64.pdf` printed p.6 states MCP's
minimum machine, and it includes, verbatim: *"An IBM 7612 Disk
Synchronizer **with at least one disk unit used to store system
programs and as auxiliary storage for the problem program**."* It
also requires an **IBM 1401 (Tape-Oriented) used for off-line
operation**, three 7302 core units, the eight basic Exchange channels,
a console, a card reader and at least four 729 IV tapes.

**There is no diskless mode, and the manual's own structure proves
it.** The same page gives five explicit "can operate without"
escapes — without the 1401, without the card reader, with one output
tape, without the input tapes, with one input tape — and **none of
them is "without disk"**. `C22-6728-1` printed p.10 says why: *"All
of MCP resides permanently on the Permanent Read Only Storage Area of
the disk (PROSA). Most of it also resides permanently in upper core
storage, the rest being called in from the disk as needed."* And
`C22-6678-1` printed p.49's IPL error codes include *"04 The disk
locate was unsuccessful"* and *"05 The disk write of PROSA was
unsuccessful"* — unrecoverable halts.

Note also what the minimum does **not** include: **no printer and no
card punch on the 7030 itself.** *"An IBM 1401 Data Processing System
(Tape-Oriented) will perform all peripheral operations… Card-to-Tape,
Tape-to-Printer, System Output, Tape-to-Punch, System Input"* (same
page). MCP spools.

**So "run MCP" entails, at minimum: the Exchange (layer 3), the disk
and its synchronizer as a second memory-bus requester (§4.4),
interrupt-driven I/O status (§4.3 / step B1), the interval timer and
time clock (§3.2), four tape units, a console typewriter, and a card
reader.** MCP cannot be reached by a shortcut through any one of
them. It is downstream of essentially all of layer 3.

Two further CPU dependencies worth naming, because they are
architectural rather than peripheral:

- **The interruption system is MCP's spine.** `C22-6728-1` printed
  p.12: *"MCP design is centered around the IBM 7030 interrupt
  system. All interrupts are taken by MCP. All major transfers of
  control and all I-O functions depend upon the interrupt system."*
  It keeps two 48-entry tables, the **SIT** (*"48 full word
  instructions of the form SIC,---; BD,---; one for each indicator 0
  through 47. **Indicator 14 is not used**"*) and the parallel
  **SIPT**. That is directly checkable against this model, which
  already implements `SIC` plus the embedded branch, the mask, and
  the leftmost-wins scan — and whose own `ssip_sip17_reset`
  transcription independently established that slot 14 is not an
  indicator.
- **The boundary registers are how MCP protects itself.**
  `J22-6559` printed p.3: *"MCP uses the information contained in a
  LIM card for storage assignment; at load time, **MCP loads A and B
  into the boundary registers**."* The model has these
  (`bsv/StretchStorage.bsv:248`, `bsv/StretchExecute.bsv:416–425`).
- **There is no hardware privileged mode** — MCP uses a software
  "system level" bit plus the boundary registers (`C22-6728-1`
  printed p.8). That is good news: nothing to add.
- **The interval timer is read and written through MCP's `$SIT`
  pseudo-op precisely because it is protected** — `C22-6678-1`
  printed p.28: *"The value of the interval timer occupies bit
  positions 0-18 of word 1 in the 7030 special registers… To simplify
  the problem of accessing the interval timer, **which is permanently
  protected**, MCP provides $SIT."* `$TIME` reads the **time clock**
  and edits it into characters. Both must tick (§3.2).

The good news is that the disk is **not** a documentation gap: the
Reference Manual's printed pp.157–162 specify its programming
interface completely (§4.4), and MCP's own machine I/O pseudo-ops
include "Locate Arc" with "Disk Initialization" and "Disk IPL"
procedures.

### 6.2 MCP's source listing is genuine STRAP with a machine-code column — verified

`docs/MCP_Mar63_001-249.pdf` + `docs/MCP_Mar63_250-445.pdf`, 451 PDF
pages. **This was checked first-hand** rather than taken from
`archival_inventory.md`, because the whole MCP estimate hangs on it.
Rendering PDF p.120 of the first file at 130 dpi gives:

```
TIME CLOCK 00054041  PUNID 11D11MCP  CARD ID DB000100 ...  PAGE NUMBER 113
LINE  LOCATION        BINARY OUTPUT      NAME   STATEMENT        LOCATION  215147
  1*  215147.00    216371.40 80                 SIC,WINTOR                DB000100
  2*  215147.40    216333.10 00                 B,W LODE      -           DB000101
  ...
 25*                                            CNOP                      DB000112
```

So: a **LINE** column, an **octal LOCATION** column, a **BINARY
OUTPUT** column carrying the assembled machine code in exactly the
form `strap/listing_oracle.py` already consumes, a NAME column, the
STRAP statement, and a card-ID sequence number. **PDF page = printed
page + 7** (PDF 120 = printed 113). The content on that page is the
interrupt table — twenty-four `SIC,WINTOR` / `B,W LODE` pairs — which
is exactly what `C22-6728-1` printed p.12 says the SIT is.

Scale, from the assembler's own trailer and index: **97 control
sections** (9 for the IPL program, 88 for MCP), indexed on PDF pp.1–2
with page numbers; **~20,228 source statements**; lower memory bound
octal 000040, upper octal 236543; `END,0` at octal 023233.76; and
**eight assembler diagnostics in the whole 20,000-line assembly**,
all on comment/definition lines. There is also a symbol
cross-reference in the trailer. One defect: **printed page 329 is
missing from the scan** (51 cards of section `TA JOB CONTROL
LOADER`).

**So MCP is a transcription target, not a reconstruction — and it is
a first-rate oracle for this project's assembler even before the
machine can boot it.** 20,228 statements with their assembled binary
is an order of magnitude more encoding evidence than the 182 verifier
scripts currently rest on.

Supporting documents: the System Analysis Guide (`C22-6728-1`, 280pp
— the SIT/SIPT structure, job control, the IPL/Restart section at
printed pp.95–106) and the Loader manual (`C28-6379-0`, 24pp).

**MCP's own IPL is a second-stage bootstrap on top of §5.3's
hardware one.** `C22-6728-1` printed p.96: *"**The first word on the
tape is a control word to read in the rest of the IPL bootstrap
record.** The tape unit on which this tape is mounted must be on a
unit dialed to zero."* — which is precisely the Reference Manual's
p.125 requirement, independently confirmed from the software side.
The bootstrap *"locates the channel with the master tape… reads as
many records from the master tape as core storage permits, and then
moves the initialization program… to its operating storage"*, then
loops tape→disk writing the whole PROSA image. Operator procedure,
`C22-6678-1` printed p.29: set the time in **console binary keys
0–23** and the date in **keys 32–55**, *"3. Press IPL key. 4. Press
Signal key on the adapter unit for the channel on which the master
system tape is mounted."* — a third independent confirmation that
the trigger is the device's SIGNAL key (§5.3) and that the console
has 64 binary keys (§7.2).

### 6.3 Is there a smaller useful target than MCP? Yes — four, ranked by size

| target | size | what it needs beyond today's model |
|---|---|---|
| **JA BP6A memory-pattern test** (`ja_bp6a_memory_patterns_test.pdf`, 6pp) | **≈58 words**, a 7-card PUNFUL deck | the card reader and multi-word `T`. Issues **no I/O instructions at all** once loaded. Caveat: *"This program operates continuously with no error indications. It relies on scoping to detect errors"* — you verify it by dumping memory, not by reading output |
| **KA UL1 card loader** (`ka_ul1_load_and_tape_write_util.pdf` PDF pp.5–18) | ~14 listing pages | IPL + chaining + the card reader. **Running it *is* the definition of "the machine boots"** — this is milestone A3 |
| **SSIP + one maintenance deck** (`ja_ua1_ssip.pdf` PDF pp.7–52) | **795 words** — `SLC,%8@1300.` to `END` at 002732.71, i.e. octal 1300→2732 | `SVA`; a console typewriter as a character sink (its I/O is `REL(SEOP)` / `W(SEOP)` / `CCW` on unit 19.32); and a device-ready status bit. **No tape, no printer, no punch, no disk.** |
| **MCP** | **~20,228 statements**, ~11,000 words resident | everything in §6.1 |

**A correction worth recording.** An earlier reading of this repo
sized SSIP from its `END,%8@100.` operand as ~1,434 words. That is
wrong: the operand names the *entry* convention, and SSIP's own
`SLC` is octal **1300**, so it is **795 words** — about half. It is
still not a shortcut to A3, for a different reason: **nothing of SSIP
has ever executed on this model.** `tests/verify_ssip_sip17_listing.py`
imports only `strap_asm` and `listing_oracle` and never touches
Bluesim (§1.3). And SSIP is *not standalone* either — its own writeup
(PDF p.4 = printed p.6) says *"The present SSIP (PUNFUL card loaded)
does not control the reading in the maintenance program. It therefore
must rely on the maintenance programmer to give control to the
SSIP."* The runnable unit is SSIP **plus** a maintenance deck.

SSIP's operating procedure is also the clearest statement anywhere of
what the console must do (PDF pp.3–4 = printed pp.4–5): *"1. Push
Master Reset button 2. Place Interrupt disable in the inactive
position. 3. Place Time Clock disable switch in the inactive
position. 4. Place maintenance switch in active position (Maintenance
Mode). 5. Place sense switches in the desired location… 6. Depress
IPL key (initial program load) on operators console. 7. Place SSIP
card deck in the card reader hopper… 8. Push the Start pushbutton on
the card reader."* Its sense switches are numbered up to **SSW 61**,
inside the PK-0…PK-63 range of §7.2.

**The Diagnostic Control Program is the fifth candidate and it is
bigger than it looked.** `ka_ua1_diagnostic_ctl_pgm.pdf`: origin
`SLC,%8@4000.0`, `END,F1` at **016500.40** — **5,441 words**, about
6.8× SSIP, and `docs/archival_inventory.md`'s "pp.19-152" understates
it (the listing runs to PDF p.154). It needs three tape
channels/drives, a line printer, a console typewriter, `LOC(SEOP)`,
multi-word `T`, and marginal-check voltage control that has no
analogue in a Bluespec model. It **replaces** SSIP rather than
running under it — its own printed p.1: *"It also contains helper
routines required by the diagnostic program for sense switch options
and output. Therefore, it is an integral part of each diagnostic
program."*

**And "a standalone STRAP-II assembly" is a contradiction.**
`C22-6729` printed p.7: *"Since the minimum IBM STRETCH compiling
system consists of the IBM 7030 Master Control Program (MCP) and
STRAP II, the system requirements for STRAP II are the same as those
of MCP."* `C28-6129` printed p.1: *"it must be run on a 7030 computer
with a minimum storage capacity of 24,576 words. If the 7030 being
used has a disk unit attached, STRAP-II will require three tape
drives… If there is no disk attached, seven tape drives must be
available."* So the **disk** is substitutable by four more tapes;
**MCP is not substitutable at all**. STRAP-II is *larger* than MCP as
a target, not smaller. (Note that 24,576 ÷ 3 = 8,192 confirms MCP's
three 7302s are **Model II** units.)

### 6.4 The order that follows

**JA BP6A (days, a sanity check that a 1961 deck executes at all) →
A3's KA UL1 card loader (the boot milestone) → SSIP + a maintenance
deck (the first program that *prints*) → the Exchange and real
devices (layer 3) → the disk → MCP.** There is no reordering that
gets MCP earlier, because MCP's own minimum configuration names the
pieces.

**Sizing layer 5: MCP is gated on layer 3's 3–7 months and then needs
its own transcription-and-debug effort on the order of 2–4 months.**
JA BP6A is days; A3 is weeks; SSIP is weeks after that.

---

## 7. Layer 6 — the console

### 7.1 There are two consoles, and the roadmap needs both for different reasons

This is the first thing to get straight, because the documents use the
word for two different machines:

- The **IBM 7152 Operator's Console** with its **7623 Console
  Control** is an *external unit on an Exchange channel* — a
  typewriter. It has its own CONTROL codes (Ref. Man. printed p.150:
  016/017 reserved light, 116 check light, **177 Sound Gong**) and
  its function keys (Blank/Erase, Tabulate, Backspace, Carriage
  Return, End) arrive as WRITE *data* bytes, not control codes
  (printed p.151). It belongs to **layer 3**, not here.
- The **7101 CPU Maintenance Console** is not on a channel at all. It
  is wired directly into the CPU's logic, and it is what the operator
  touches to start the machine. `R23-9713_7101_Maint_Console_1961.pdf`
  documents it.

The system block diagram at `R23-9713` PDF p.3 shows both, and shows
the maintenance console attached to the CPU through a **Scanner**,
beside the Instruction Unit / Instruction Checker / Look-ahead /
SAU / PAU — the only box in the diagram drawn in bold ("covered in
detail in this manual").

### 7.2 What the maintenance console exposes

Contents (`R23-9713` PDF p.4, the printed table of contents). **Page
offset note:** the appendices carry visible folios and run at offset
**0** (PDF p.44 = printed p.44, Appendix C; PDF p.46 = printed p.46,
Appendix E). The figure pages in §4 carry no folio, so the printed
numbers below come from the TOC, not from the page; Figures 4.2-1 and
4.3-1 are cited by **PDF page**.

| § | printed pp. | what |
|---|---|---|
| 2 | 7–13 | Physical description: **three panels** plus gate contents |
| 3 | 14–15 | Maintenance console logic |
| **4** | **16–28** | **Manual controls**: 4.1 Switch Types (16), 4.2 **Panel Keys** (19), 4.3 **Address Keys** (19), 4.4 **Control Switches** (19–28) |
| 5 | 29–31 | Format rollers |
| 6 | 32 | Computer scanner |
| 7 | 33–37 | Power circuits, power sequence and crank-up, marginal check, grounding |
| 8 | 38–41 | **Error injection and its use** |
| App. | 42–48 | Instruction formats, indicator list, storage assignment, operation-code lists, powers of two |

**The decisive page for this roadmap is Figure 4.2-1, "PANEL KEYS AND
PATTERN SWITCHES", `R23-9713` PDF p.21 = printed p.19, read
first-hand.** It shows **sixty-four panel keys, labelled PK-0 through
PK-63**, each a two-position toggle feeding the CPU logic through the
console tailgate, plus four **pattern switches** that preset them in
bulk — the figure's own note: *"BOTH SWITCHES UP, ALL ZEROS ON PANEL
KEY OUTPUT. BOTH SWITCHES DOWN, ALL ONES ON OUTPUT"*, with `SET .0`,
`SET 01`, `SET 101010…` and `SET 0101010…` legends.

**PK-0…PK-63 is exactly the numbering KA UL1 calls `MS 0…63`**
(§5.2), and **the chain from "panel key" to "sense switch" to
"storage word 4" is now sourced end to end, not inferred**:

1. `R23-9713` printed p.19 — the 64 panel keys are *"a data source
   for storage address 4 when in the test mode"*.
2. `R23-9713` printed p.19, Maintenance Mode (F49) — it *"enables …
   the program controlled references to storage address 04"*.
3. Ref. Man. printed p.35 — location 4 is the Maintenance Bits, 64
   bits, *"active only when the machine is in the maintenance mode"*
   (§5.3, read first-hand).
4. Programs call them interchangeably *maintenance keys*,
   *maintenance switches*, *maintenance bits*, *MS n*, and **sense
   switches**: `R23-9732` printed 7-2 (*"Set maintenance key 31… Since
   maintenance key 31 is set before the initial program load"*);
   `ka_ul1` (*"MS 32"*, *"MS 37"*); the System Test Programs selection
   chart (*"Set 1 of 32 Maint. Switches 0-31… Alter maintenance
   switch 63"*); and the whole diagnostic family runs under the
   **Sense Switch Interrogation Program**.

**So a program reads the console switches as an ordinary storage
reference to word 4** — no instruction, no channel. The model's
`bsv/StretchStorage.bsv:251` register is therefore the right home,
and the work is a driver plus the maintenance-mode gate.

The DCP even partitions the 64 bits (`ka_ua1` printed p.16, Table 5):
bits **48–62** reserved for the control program (49 restart, 50
abandon, 55 halt on error, 56–59 loop options, 60 loop on error),
bits **32–47** defined by whichever diagnostic is running, and bit
**63** *"Reserved for continue from halts"* — which is why every
writeup says "alter maintenance switch 63" to proceed.

**One consequence that matters for the model.** `R23-9713` printed
p.19: Maintenance Mode *"**disables the boundary compare
circuits**"*. Every documented diagnostic procedure enables
maintenance mode — so **storage protection is off while the
diagnostic decks run**, which is worth knowing before expecting
`protViolates` (`bsv/StretchExecute.bsv:416–425`) to fire during one.

Figure 4.3-1, PDF p.22, is the matching diagram for the **Address
Keys** — *"18 telephone-type switches used to enter the address into
the CPU during manual display and store operations"* (printed p.19).

The controls an operator actually uses, from §4.4 (printed pp.19–28):

| control | what it does |
|---|---|
| **Master Reset** (D14) | *"provides a control reset and an error reset to all units of the CPU and to the storage bus"* — and that single sentence is **all** the corpus says (§11 item 4) |
| **Computer Reset** (D18) / **Error Trigger Reset** (D16) | narrower resets |
| **Start Clock** (D20) / **Stop Clock** (D22) | distribute / withhold controlled clock pulses |
| **Program Start** (D24) / **Program Halt** (D26) | reset / set the program-halt trigger — *"stop the program in arithmetic mode and allow manual intervention"* |
| **Display** (A18) / **Consecutive Display** (A20) | address keys → register W → storage bus; the word appears in 1Y and X |
| **Store** (A22) / **Consecutive Store** (A24) | panel keys → storage at the address keys' address |
| **Enter Instruction** (A26) | panel keys → register 1Y, nothing else |
| **Single Operation** (B26) | *"allows one instruction to be executed… by allowing only one level of lookahead to be filled"* |
| **1 / 2 / 3 Pulse** (C20/C22/C24) | single clock pulses; the clock must be stopped first |
| **Maintenance Mode** (F49) | enables the pulse switches, word-4 references, error injection; **disables boundary compare** |
| **Disable Interrupt** (F51) / **Disable Time Clock Advance** (F50) | the two switches every diagnostic procedure sets |
| **Disable Lookahead 1–4** (F52–F55) | suppress look-ahead levels individually |
| **Repeat Instruction** (F56), **Error Stop** (F60), **Inhibit Scan** (F59), error injection (B20/B22), index-storage test (F61–F64, A16), scan/ring controls | CE fault-isolation apparatus |

The manual's own single-step recipe (printed p.28): *"1. Stop clock
(D22). 2. Set instruction into panel switches. 3. Enter instruction
(A26). 4. Single operation (B26). 5. 1 pulse, 2 pulse, or 3 pulse."*

And the **format rollers** (printed p.29) are a nice detail: two
mechanical rollers behind slots in panel 3, printing the bit layout
of every instruction format so a displayed register can be decoded by
eye — a 1961 answer to the same problem `strap/listing_oracle.py`
solves.

**How IPL is used as a debugging tool, which independently confirms
§5.3.** `ka_ua1` printed p.19, "Octal Hex Dump of Memory from the
Switches": *"In keys 0-18, (8) 4005. **Bit 27 (the skip flag) must be
set.** Keys 32-49 must contain the starting address of the area to be
dumped… The operator should then depress IPL, and press the signal
key. **This, in effect, will cause a branch to location (8) 4005.**"*
It works because the 7152's switches *"are always scanned to furnish
the first three input words when the console receives a READ
instruction"* (Ref. Man. printed p.149) — so IPL reads the binary
keys as its one word, that word is the control word, the skip flag
suppresses any data transfer, and the CPU executes at the control
word's data-word-address field. **A perfect miniature of the whole
IPL mechanism, using the switch bank as the medium.**

**Caution on this document's nature.** `R23-9713` is a *Customer
Engineering* manual: Figures 4.2-1 and 4.3-1 are **circuit** diagrams
(open wire, tailgate connectors, coax drape cable, twisted pair, slud
card, +30 V / −6 V levels), not a user's guide. It tells you what
exists and how it is wired, not an operator's procedure. The
operator's procedure comes from the diagnostic decks
(`jb_ax4b` printed p.1, §5.1).

### 7.3 What the model has: nothing

Audited by grep over `bsv/` and `strap/`: **zero** occurrences of
`console`; `switch` only in prose; `IPL` only in two comments saying
it does not exist (`bsv/StretchIO.bsv:287–288`, *"…for a simulated
system with no IPL"*); `reset` only as `// clocks since reset` — there
is **no `reset()` method on any interface**. `maintenanceBits` exists
as a plain register with no semantics
(`bsv/StretchStorage.bsv:251`, read `:394`, written `:485`).

The entire operator surface today is four methods on
`bsv/StretchCore.bsv:56–59` — `step()` (a clock enable, `:731`),
`halted()` (`:734`), `getPC()` (`:736`), `setPC()` (`:737`) — plus two
back-door interfaces for the testbench (`:60–62`). A program is loaded
by generated BSV calling `core.mem.writeWord` once per phase
(`tests/gen_tb.py:87`), and a run stops because an instruction
branched to itself (`bsv/StretchCore.bsv:504`, `done = (o.next ==
pc)`). **There is no HALT instruction and no stop switch.**

### 7.4 The minimum that makes a machine usable

Mapped onto what the manual shows, and onto an FPGA:

| function | real console | minimum model/FPGA equivalent |
|---|---|---|
| **Start the machine** | IPL key + SIGNAL/START on the device | `ipl(channel)` method (§5.3) + a board button |
| **Stop it** | Stop Clock | a `stop()`/`run()` gate on the existing `tick` PulseWire (`bsv/StretchCore.bsv:83`) |
| **Reset it** | Master Reset | a `masterReset()` method — does not exist |
| **Set options** | 64 panel keys + pattern switches | a 64-bit register the host can set, readable as word 4 — **the register already exists** |
| **See where it is** | indicator lights, format rollers | `getPC()` exists; LEDs or HDMI on the board |
| **Read out an answer** | Address Keys + display | `core.mem` back door exists; an operator path does not |
| **Single-step** | §4.4 Control Switches | `step()` is literally this already |

**Sizing layer 6: 1–2 weeks (5–10 project-days) for the functional
minimum**, because almost every piece has a home in the model
already; and **3–6 weeks more** for a console an operator would
recognise on an FPGA (an indicator panel, address keys, display/store)
— which is really §9's peripheral work, not an architectural layer.

**The honest framing:** the console is not a hard layer. It is the
*missing framing* around work that is otherwise done. Four methods and
a 64-bit register turn `StretchCore` from a testbench component into
something a person operates.

---

## 8. Layer 7 — cycle accuracy

### 8.1 What "cycle accurate" would mean here, and how far off we are

A machine cycle is **0.3 µs** — *Performance Characteristics Vol. 1*,
printed p.3-2 (PDF p.20): *"The times are listed (table 2) in terms of
the basic machine cycles, which is presently 0.3 microsecond."* So the
target clock is **3.333 MHz**.

Three of the four major units are already structural, and one is not:

| unit | model | structural or charged? |
|---|---|---|
| Memory + MBCU | `bsv/StretchMemory.bsv`: six units, interleave map, 7-clock unit cycle, 5-clock read-out, store queue | **structural** |
| I-box | `bsv/StretchIBox.bsv`: 1Y/2Y buffers, IC controls, two-clock I-checker delay | **structural**, with the Y→Z transfer, index fetch and WBC still "planned (2b/2c)" (`microarchitecture_plan.md` §1a) |
| Look-ahead | `bsv/StretchLookAhead.bsv`: four levels, in-order removal, fetch-ahead, branch guess + recovery | **structural**, with the five counters' separate interlocks collapsed into one and no operand forwarding |
| E-box (SAU + PAU) | `bsv/StretchExecute.bsv` + `StretchFP.bsv` + `StretchALU.bsv` + `StretchVFL.bsv`: pure combinational functions | **charged**: `bsv/StretchTiming.bsv` hands out a scalar clock budget which `StretchCore` burns as `ebusy` |

`docs/microarchitecture_plan.md` line 5771 states this as a deliberate
difference from Bluespec's Piccolo reference core, and §6e is the
written design for closing it: the serial arithmetic unit's two
16-of-128 / 8-of-16 byte-extraction switch matrices, the decimal
corrector, the parallel unit's 100-bit carry-propagate adder with
4-bit look-ahead, the multiply tree (four carry-save adders, 12
multiplier bits per cycle as four 3-bit groups), and divide by
table-selected multiples at ~3.5 quotient bits per cycle. **None of
that exists.** Divide is not implemented at all for exactly this
reason (`microarchitecture_plan.md` §6f: *"A combinational full-width
divide unfolds hugely in bsc, and the real divide is iterative"*).

### 8.2 THE ORACLE QUESTION — and the answer is better than expected

This project's discipline is that behaviour must be checkable against a
primary source or a deck. For cycle accuracy, four candidate oracles
exist in `docs/`, and they form a genuine ladder rather than a single
weak proxy.

**(a) *Performance Characteristics* Vol.2's measured instruction
timings — the strongest, and it is ~150 pages of data.**
`docs/7030_Performance_Characteristics_Vol2_Mar61.pdf` PDF pp.40–190
(printed pp.37–187) are measured timing tables, one or more pages per
operation. Verified first-hand at PDF p.43 = printed p.36, headed
*"FLOATING POINT D+ OPERATION. WITHOUT FORWARDING OF EXTERNAL AND I-BOX
OPERANDS"*, with columns `NO INDEXING` × {`INTERNAL OPERAND`,
`EXTERNAL OPERAND`, `I-BOX OPERAND`} and the same three under
`INDEXING`, and rows by sign modifier and operand singularity class
(`NORMALIZED`, `BOTH OPERANDS WITH XPFN`, `AC EXPNT N. MEM EXPNT
XPFN`, `AC WITH XPFP. MEM WITH XPFN`). Values are in microseconds to
**two decimal places** — 2.57, 1.80, 1.81, 2.41, 2.10 on that one
page. At 0.3 µs per cycle, **0.01 µs is 1/30 of a cycle**: the data
resolves individual cycles with an order of magnitude to spare.

How the numbers were produced is documented, which matters for how to
use them. PDF p.37 = printed p.34, verbatim:

> *"A subroutine (GENER) was written to handle the generation of a long
> sequence of instructions, the execution of that sequence, the
> calculation of execution time, and the conversion and printing of
> that time. … It picks up the instruction at A, determines if it is
> full or half word, determines if it is a branch type instruction,
> "ors" in both masks, stores the instruction, and reduces the count B.
> … This series is then reproduced until a thousand instructions are
> available after which a count branch (with an original count of 10)
> is inserted."*

**So these are steady-state throughput figures over a 1000-instruction
sequence run ten times, not isolated latencies.** That is exactly the
right shape for validating a pipelined, look-ahead machine — it
measures the overlap, which is the thing a per-instruction table
cannot. The document's own "Time Evaluation" section gives the
algebra for backing a single instruction's time out of a mixed
sequence and states the error bound — *"Each time measurement may
have an error on 0.01 µs"* (**OCR text layer, not re-read from the
page image**; the 0.01 µs resolution is independently confirmed by
the two-decimal values on the timing pages, which were image-read).
It also distinguishes **with and without
operand forwarding** — the exact feature `microarchitecture_plan.md`
lists as not modeled — which makes it a discriminating oracle for the
one look-ahead feature most likely to be got wrong.

**And GENER itself is a 7030 program.** It can be transcribed and run
*on the model*, and the model's own clock counter compared against
IBM's printed microseconds, instruction class by instruction class.
That is the same methodology as every `verify_*_listing.py` in this
repo, one level up.

**(b) Whole-program execution times for six real programs —
Vol.1 Table 10.** `docs/7030_Performance_Characteristics_Vol1_Mar61.pdf`
PDF p.51 = printed p.4-9, *"TABLE 10. EXECUTION FREQUENCY CHART FOR
STRETCH PROGRAMS"*: per-operation execution counts for six programs
(Fl. Pt., Pseudo j-level, Grid Param., A1, A1 Modified, A2) with, for
each, a total instruction count, an **Execution Time in ms** (5.98,
0.70, 5.57, 7.045, 7.0135, 7.07, 0.38, 0.309) and an **average time
per operation in µs** (3.5, 6.4, 2.7, 2.36, 3.3, 2.9, 2.4, 3.8).
Four of these programs' full source listings are in Vol.2 (§2.2). So
there is an end-to-end oracle: **assemble IBM's own benchmark, run it,
and compare the model's clock count at halt against IBM's measured
milliseconds.** The suite's `CYCLES<=N` mechanism
(`tests/run_tests.sh` lines 2020–2075) already does precisely this
shape of check against synthetic microbenchmarks; this replaces the
synthetic target with a historical measured one.

**(c) Vol.1 Appendix A Table A-2.** PDF pp.69–71, *"SUMMARY OF 7030
INSTRUCTION EXECUTION"* — per operation code: how many look-ahead
levels it takes, whether it needs the LAAR, whether it uses it if
free, the I-box operand fetch and the I-box/E-box execution split.
This is a **structural** specification, not a timing table: it is the
spec a structural look-ahead must satisfy, and it is the document that
would let the five collapsed interlock counters be separated
correctly. `microarchitecture_plan.md` does not currently cite it.

**(d) The existing `CYCLES<=N` bounds.** Six of them
(`tests/run_tests.sh` lines 2035, 2046, 2055, 2070, 5900, 6033). These
are **regression guards, not accuracy evidence** — the file's own
comment says *"Bounds carry ~10-25% slack; they catch timing
regressions and tighten as later stages add overlap."* They prevent
loss of fidelity already achieved; they cannot establish fidelity.

**(e) The memory diagnostics** — `ja_bp6a_memory_patterns_test.pdf`
(6pp), `ja_bm6a_unique_adr_test.pdf` (11pp), `ja_bb6b_worst_pat_test.pdf`
(20pp), all listed in `docs/archival_inventory.md` as not yet used.
These are *functional* memory tests. Whether any of them times itself
is unestablished (§10). What *is* established is that the benchmark
programs time themselves: Vol.2 PDF p.5 = printed p.2 carries
`SC, $X2, 1.0   'INTERVAL TIMER RESET`, and Vol.2's Monte Carlo
listing has `TIME`/`TIMEE` labels. **A self-timing program is a
cycle-accuracy oracle that needs no external comparison at all** — it
prints its own elapsed time, and the model either reproduces IBM's
printed figure or does not.

**Verdict on the oracle question.** There *is* an adequate oracle, and
it is Vol.2 plus Vol.1 Table 10 — roughly 150 pages of measured
microseconds at 1/30-cycle resolution, cross-classified by the exact
structural features (operand location, indexing, forwarding) that
distinguish a real pipelined implementation from a charged-time one,
plus eight whole-program measured execution times. **This is a
stronger oracle than most modern cycle-accurate models have.** It is
not yet *used*: `StretchTiming.bsv`'s header cites Vol.1's Tables 2–8
and Blosk's figures, and `microarchitecture_plan.md` §1a lists
*"Measured benchmark timings (GERB2 etc.) | Perf. Char. vol.2 |
**planned (5)**"*. The oracle exists and is unexploited; that is good
news for sizing, because the verification method does not have to be
invented.

**The honest caveat.** An oracle of per-instruction-class times and
whole-program totals validates *throughput*, not every internal
latch. A model could match every number in Vol.2 and still differ from
the 7101's gate-level behaviour in ways nothing in `docs/` can see.
The ceiling on verifiable fidelity is therefore: **cycle-accurate
throughput, per instruction class, under documented operand and
indexing conditions, plus whole-program totals** — and the CE manual
(`R23-9732`, 297pp of section-3 flow/block/timing charts) is the only
thing in `docs/` that goes below that, as a *structural* source with
no measured data to check an implementation against.

### 8.3 Sizing cycle accuracy

This is `microarchitecture_plan.md`'s own stages 4 and 5, plus the
stage-2c/3 items still listed "planned" in its §1a.

| piece | what it is | size |
|---|---|---|
| **4a** SAU per-byte timing wrapper + explicit C/D registers | wrap the existing whole-field `StretchVFL`/`StretchALU` arithmetic in a per-byte loop; add the operand register the hand-off needs | **1–2 weeks** (5–10 project-days) |
| **4b** split `execute()` into an arithmetic-unit module | `microarchitecture_plan.md` §6g calls this "the highest-value step": the structural prerequisite for 4c–4f *and* the fix for the suite's build time. It is a refactor of the single largest function in the codebase | **2–3 weeks** (10–15 project-days) |
| **4c** FP add/sub/compare with normalization timing | against Vol.1 Table 2 and Vol.2's per-operation pages | **1–2 weeks** |
| **4d** multiply (the carry-save tree, 12 bits/cycle) | | **1–2 weeks** |
| **4e** divide (table-selected multiples, ~3.5 bits/cycle) | not implemented at all today | **2–3 weeks** |
| **4f** decimal + radix conversion in the SAU | overlaps layer 1 §2.3 — do it here, not there | **2–3 weeks** |
| **2c/3 residue** | Y→Z transfer, index fetch, modification and WBC as explicit register stages; index storage destructive read and 2-cycle write; the five look-ahead counters' separate interlocks; **operand forwarding**; interrupt recovery/housecleaning; the look-ahead unwind that closes the I-box-overtook-a-level interrupt gap | **4–8 weeks**. Several of these are listed "planned" in §1a with CE-manual figure references; forwarding alone is a measured, discriminable feature in Vol.2 |
| **5** validate against Vol.2 and Vol.1 Table 10 | transcribe GENER; transcribe the four benchmark programs; build a timing-comparison harness alongside `listing_oracle.py` | **3–6 weeks**, and it cannot start until layer 1 is done, because the benchmarks use `LVE`, `SVA`, `SWAP`, multi-word `T`, `LCV` and decimal VFL (§2.2) |

**Layer 7 total: 15–30 weeks of project-days, i.e. 75–150
project-days ≈ 3–6 months.** For comparison, everything built so far
is 28 project-days. **Cycle accuracy alone is three to five times the
entire project to date**, and that is with the memory system, the
instruction unit and the look-ahead already structural. If they were
not, it would be worse.

### 8.4 Can cycle accuracy be pursued independently?

**Yes, and it should be, with one exception.**

- **Independent of MCP.** Nothing MCP does requires the E-box to be
  structural rather than charged — see §6.
- **Independent of the Exchange**, except that real device timing is
  itself a cycle-accuracy question nobody has sized (the Exchange
  transfers *bytes*, asynchronously, while the CPU runs —
  `bsv/StretchIO.bsv` header, quoting Ref. Man. printed p.104).
- **NOT independent of layer 1.** The validation step (5) needs
  `LVE`, `SVA`, `SWAP`, multi-word `T`, `LCV` and decimal VFL, because
  those are what IBM's benchmarks are written in. You can build the
  SAU/PAU without them; you cannot *check* it without them.
- **NOT independent of the timer.** Self-timing programs need the
  interval timer to actually tick, which `docs/NEXT.md` §5 sizes and
  which nothing currently does.

---

## 9. Layer 8 — real hardware: the ULX3S

**Source note.** Everything in this section about the ULX3S board and
the Lattice ECP5 is **manufacturer data, not from `docs/`**, and is
labelled as such. Everything about the 7030 and about the model is
cited as usual. Nothing in this repository currently mentions FPGAs:
`grep -rniI 'ulx3s\|ecp5\|fpga\|yosys\|nextpnr' stretch/` returns only
occurrences of the word "synthesized" referring to bsc's
`(* synthesize *)` attribute. **This layer is at zero.**

### 9.1 The arithmetic, done once

| quantity | value | derivation |
|---|---|---|
| machine clock | **3.333 MHz** | 0.3 µs/cycle, Perf. Char. Vol.1 printed p.3-2 |
| ULX3S oscillator | 25 MHz (PLL-derivable) | board data — **7.5× headroom** |
| core storage, data bits | **6,291,456 bits** (768 KiB) | 98,304 words × 64 b; `bsv/StretchMemory.bsv` line 60 |
| core storage with ECC | **7,077,888 bits** (864 KiB) | 72 b/word — Perf. Char. Vol.1 printed p.A-1: *"Each extended word contains 64 information bits plus 8 error-check bits"* |
| ECP5-85F block RAM (EBR) | ~3,744 Kbit | Lattice data — **does not fit** |
| ULX3S SDRAM | 32 MiB, 16-bit bus | board data — **fits with 37× to spare** |
| memory bandwidth the six units need | **183 Mbit/s** | 6 words ÷ 2.1 µs × 64 b |
| SDRAM bandwidth at 100 MHz | **1,600 Mbit/s** | 16 b × 100 MHz — **8.7× headroom** |

**A useful corollary.** MCP's stated minimum is **three 7302 units**,
and three of them is **24,576 words** — not 49,152 — because the
minimum uses Model II units of 8,192 words (`C28-6129` printed p.1:
*"a minimum storage capacity of 24,576 words"*; the 7302 comes as
*"Model I – 16,384 words… Model II – 8,192 words"*, physPlan printed
p.6). **24,576 × 64 = 1.57 Mbit, which fits in block RAM on an
ECP5-45F (~1,944 Kbit) and comfortably on the -85F.** So there is a
real intermediate target: a *minimum-MCP* machine entirely in block
RAM, no SDRAM controller at all, before the typical six-unit machine
needs one. (The ULX3S ships as 12F/25F/45F/85F; the 3,744 Kbit figure
above is the **-85F only**, and on a -12F or -25F even this reduced
machine needs SDRAM.)

**Conclusion on memory:** a typical six-unit LASL machine does *not*
fit in the ECP5's block RAM and *does* fit comfortably in the board's
SDRAM, with enough bandwidth to serve all six interleaved units from
one controller. The 2.1 µs unit cycle is ~17× an SDRAM burst, so the
*real* memory's slowness, not the FPGA's, remains the bottleneck —
which is what cycle accuracy wants. This is a solvable problem with
numbers on its side, and it is the single most reassuring fact in
this section.

### 9.2 The real risk is area, and it is the same work as cycle accuracy

`bsv/StretchExecute.bsv`'s `execute()` is, per root `AGENTS.md`'s own
description of the pre-rewrite state, *"one ~1450-line combinational
`execute()` (the whole E-box)"*. The idiomatic rewrite moved it behind
`mkEBox`'s request/result interface but **did not make it
multi-cycle** — `microarchitecture_plan.md` line 5771 records that as
the one remaining difference from Piccolo. Combinationally that means:
a 128-bit sign-magnitude adder, a 96-bit pre-shift barrel shifter, a
post-normalisation shifter, a 48×48 (and 96×96 for `D*`) multiply, the
sixteen connectives, the VFL field extract/insert — all in parallel,
all muxed, in one cycle.

At 300 ns of clock period **timing closure is not the worry** (that is
a very long cycle for an ECP5). **Area is.** No measurement exists, so
no number is asserted here; what *is* assertable is that the
remediation is already specified: `microarchitecture_plan.md` §6g step
**4b** — split `execute()` into a multi-cycle arithmetic-unit module
with a shared datapath. That step is listed there as the
cycle-accuracy prerequisite. **It is simultaneously the FPGA area
fix.** One piece of work serves two of the owner's four goals, and
that is the most important structural insight in this document after
§1.2.

### 9.3 Toolchain, which has never been run here

Today `bsv/build.sh` and `bsv/run_tb.sh` target **Bluesim only**. The
path to a bitstream is `bsc -verilog` → `yosys` → `nextpnr-ecp5` →
`ecppack`. Known work, none of it done:

1. **bsc Verilog back end.** Primitives (`RegFile`, `BRAM1Port`,
   `FIFO`) come from bsc's Verilog library and must be included;
   `mkBRAM1Server`'s emitted module must be inferred as block RAM (or
   replaced by an SDRAM-backed module).
2. **Strip simulation-only constructs** from the synthesised path.
   Helpfully, `(* synthesize *)` is already on `mkStretchCore`
   (`bsv/StretchCore.bsv` line 65) and on nothing else that matters,
   and every `$display` lives in testbenches — so the boundary is
   already in the right place.
3. **Replace `StretchStorage`/`StretchMemory`'s BRAM with an SDRAM
   controller** behind the same MBCU interface. The interface is
   already request/response with a `responseReady` handshake, which
   is exactly what an SDRAM controller wants.
4. **Re-home the peripherals.** The board has no card reader. A
   plausible mapping, none of it specified anywhere yet: SD card as
   card reader *and* tape (both are sequential block devices to the
   Exchange), UART or HDMI+USB-keyboard as the console typewriter,
   the board's LEDs/buttons/DIP switches as a minimal console
   indicator panel, HDMI for a full console replica (§7).
5. **A clock-rate decision.** Running at a true 3.333 MHz makes the
   machine historically faithful and makes `CYCLES` counts directly
   comparable to Vol.2's microseconds. Running faster makes it usable.
   Both should be build options; the timing oracle requires the first.

### 9.4 Sizing layer 8

| piece | size |
|---|---|
| First `bsc -verilog` → yosys → nextpnr-ecp5 run of `mkStretchCore`, even if it does not fit | **1 week** (3–5 project-days) — **and it gates layer 7.** See below. |
| SDRAM-backed memory behind the MBCU interface | **2–4 weeks** |
| Area reduction via §8's step 4b (counted in layer 7, not twice here) | — |
| Peripherals: SD-card reader/tape, UART console, LED/switch panel | **3–6 weeks**, and it depends on §4 (the Exchange) being real |
| Board bring-up, clocking, bitstream, debug without a simulator | **2–4 weeks** |

**Layer 8 total: 8–15 weeks ≈ 40–75 project-days ≈ 2–3 months**,
*assuming* layer 7's 4b refactor has already made the design fit.

**The ordering claim, which is the most actionable thing in this
section: run `bsc -verilog` → `yosys` → `nextpnr-ecp5` on
`mkStretchCore` in the FIRST week of the whole roadmap, before any
other layer-8 work and before layer 7 starts.** It costs 3–5
project-days, it needs nothing else to be built, and its output is a
single number — the LUT count against the ECP5's ~84k. That number
decides whether §8's step 4b (splitting the 1,179-line combinational
`execute()` into a multi-cycle arithmetic unit) is an *optional*
refactor that improves cycle accuracy, or a *forced* prerequisite with
a hard deadline. Every other sizing decision in layers 7 and 8 hangs
on it, and it is the cheapest piece of information in this document to
acquire.

### 9.5 Which goals can be pursued independently

| | needs cycle accuracy? | needs the FPGA? | needs MCP? |
|---|---|---|---|
| **Cycle accuracy** | — | no (validate in Bluesim against Vol.2) | no |
| **ULX3S** | no, *except* that the 4b refactor is probably forced by area | — | no |
| **MCP** | **no** — see §6 | no | — |
| **"Boot and run a real program"** | no | no | **no** — SSIP/DCP, not MCP |

**The three goals are separable.** The one hard coupling is that the
multi-cycle arithmetic-unit refactor (§8 step 4b) is on the critical
path of *both* cycle accuracy and the FPGA, so it should be scheduled
once and early. The one soft coupling is that cycle-accuracy
*validation* needs layer 1's instructions, because IBM's benchmarks
are written in them.

### 9.6 Which parts of MCP would notice charged time versus structural timing

The coordinator asked this directly, and the answer is narrower than
it sounds. **MCP can run on a charged-time model.** What MCP is
timing-sensitive to is not the E-box's internal structure but three
*architectural* facts, all of which live outside the arithmetic unit:

1. **The interval timer and time clock must advance at the documented
   rate** (Ref. Man. printed p.34: 1,024 pulses/s). An operating
   system that time-slices, times out a device, or stamps a job reads
   word 1. Today nothing steps it (§3.2). This is an *indicator- and
   storage-level* property: a charged-time model that ticks word 1
   once every 3,255 model clocks satisfies it exactly as well as a
   structural one would.
2. **I/O completion must be observable, and at a plausible moment.**
   Today a block transfer is synchronous and nothing else runs during
   it (`bsv/StretchCore.bsv:377–466`, with every other arm gated on
   `!isValid(ioPending)`). MCP's whole reason for existing is to run
   one job while another waits on tape. That is §4's gap, not §8's —
   it needs *asynchronous* I/O, which is a structural change to the
   Exchange, not to the E-box.
3. **Interruptions must be taken at an instruction boundary.** Already
   measured and fixed (`docs/NEXT.md` §3: the bracket program passes
   at zero instructions of slack since the `ebusy` term was removed
   from `armInterrupt`).

**What MCP would *not* notice**: whether a floating-point divide takes
its real ~3.5-quotient-bits-per-cycle number of clocks or a charged
scalar; whether operand forwarding happens; whether the five
look-ahead interlock counters are separate. Those change *how long*
things take, not *what happens*, and nothing in an operating system
branches on them.

**The consequence for planning: MCP does not have to wait for cycle
accuracy, and cycle accuracy does not have to wait for MCP.** They
share only the interval timer, which is cheap and which both need.

---

## 10. The sequence

### 10.1 The principle

Every step below ends with something that **runs and is checked
against a deck or a document**, in this project's two established
standards (`docs/NEXT.md` "The bar"): *transcription* (a listing row
checked bit-exactly) or *manual-derived* (hand-written from a primary
source, stated as the weaker standard). No step is a big-bang, and no
step leaves the suite red.

The steps are grouped into four tracks that can run in parallel once
step 0 is done, because §9.5 established that cycle accuracy, the
FPGA and MCP are separable.

### 10.2 Step 0 — the week that decides the rest (≈1 week)

Four cheap, independent measurements, each of which converts a guess
into a number. **Do all four before committing to anything else.**

| step | what to measure |
|---|---|
| **0a** | **Synthesise `mkStretchCore`.** `bsc -verilog` → `yosys` → `nextpnr-ecp5`. Output: a LUT count against the ECP5's ~84k. Decides whether §8 step 4b is an optional refactor or a forced prerequisite (§9.4). |
| **0b** | **Raise `DeviceWords`** (`bsv/StretchIO.bsv:204`, `typedef 32 DeviceWords`; the tape's is `typedef 16 TapeWords` at `:209`) to a real card-deck size and see whether bsc elaborates. A card is 15 words, so 32 holds **two cards**. `bsv/README.md` "Next steps" item 5 warns these `Vector#(…, Reg#(Word64))` device images have the same elaboration ceiling that sent bsc to 1.5 TB on a 256-word storage array. If it blows up, the reader needs the BRAM treatment and milestone A3 grows by weeks. **This is the single unverified assumption under the shortest path below.** |
| **0d** | **Open `ka_ex1_bx-0.pdf` and `ka_ex1b_bx-0.pdf`** (78 and 66 pages, the BX-0 exchange tests) far enough to say whether they are real STRAP listings. They are layer 3's only deck oracle and this project has never opened them — see §10.9, the biggest risk. |
| **0c** | **Assemble one IBM benchmark** from Perf. Char. Vol.2 and bit-check it against its printed machine code with `listing_oracle.py`. Needs the six missing pseudo-ops (§2.4) and nothing at all from the model. Output: proof that IBM's own application code can be reconstructed exactly, plus the first execution target that is neither a diagnostic nor a worked example. |

### 10.3 Track A — "the machine starts" (the shortest credible path)

**This is the track that first yields a machine that boots and runs a
real program, and it is deliberately NOT the typical six-unit
installation.**

| step | what lands | checked against | size |
|---|---|---|---|
| **A1** | **The interval timer and time clock tick.** Wire `bsv/StretchCore.bsv:123`'s free-running `clk` to `intervalTimerAndClock` (`bsv/StretchStorage.bsv:246`) at one tick per 3,255 model clocks, with p.34's reload rule. | Ref. Man. printed p.34; deck oracles `ax5b` I6071 (already transcribed) and routine 1258 (located, PDF pp.5–7, ~94 rows) | **days** |
| **A2** | **Control-word chaining, then IPL.** The fixed control word (data address 4, chain 1, count 1, refill 4), the chained read, and the one-shot execute at the address in word 4 — exactly as Ref. Man. printed p.126 specifies (§5.3). Chaining first, because IPL *is* a chained read. | Ref. Man. printed pp.108–109, 125–126; `jb_ax4b` printed p.1's console procedure | **1.5–2.5 weeks** |
| **A3** | **A real loader deck runs.** Transcribe **KA UL1's card-loader half** (`docs/ka_ul1_load_and_tape_write_util.pdf` PDF pp.5–18, a complete STRAP listing of a real 1961 card loader, §5.2 item 5), IPL it, and watch it load a second deck. Its wait loop is IBM's own `CCW`/`BB` idiom, which this model already supports (§4.3). | the listing's own printed machine code via `listing_oracle.py`, then execution | **1–2 weeks** |

**A3 is the first milestone that is honestly "a machine that boots and
runs a real program."** It is reachable in roughly **4–7 weeks** from
today, and it needs **none** of: the real Exchange, I/O status
reaching the indicator register, interrupt-driven I/O, MCP, the disk,
decimal arithmetic, multiply/divide, cycle accuracy, or an FPGA.
The one thing it *does* need that is unverified is step 0b.

**What A3 is and is not.** It is: one CPU, the typical memory
configuration, one card reader, one printer, a working interruption
system, an IPL button, and a real 1961 program loaded from a deck. It
is not a typical installation. The difference, named explicitly —

| | milestone A3 | a typical (LASL) 7030 |
|---|---|---|
| core | 98,304 words, already modelled | same (Perf. Char. Vol.1 printed p.A-1: *"six boxes of 16,384 extended words each (for the Los Alamos configuration)"*) — **this part is already typical** |
| I/O | 3 stub devices on 3 fixed channels | the 7619 Exchange with its full channel/control/unit hierarchy, plus a disk exchange (§4) |
| devices | reader, printer, tape images in registers | card reader, punch, printers, many tape units, disk, console typewriter (§4) |
| software | a bootstrap deck | MCP, STRAP-II, FORTRAN IV (§6) |
| timing | charged E-box budgets | cycle-accurate (§8) |
| substrate | Bluesim | ULX3S (§9) |

So **the memory configuration is already typical and nothing else
is.** That is a useful thing to know: the "typical six-unit machine"
part of the owner's request is the one part that is done.

**Why A3 and not SSIP.** An earlier reading of this repo pointed at
SSIP as the shortest path, because `verify_ssip_sip17_listing.py`
exists. It is not: that script is an encoding check that never runs
the model (§1.3), nothing of SSIP has ever executed, SSIP is 795
words that need `SVA` and a console typewriter, and SSIP is not even
self-starting — it relies on a separate maintenance-program deck to
give it control (§6.3). KA UL1's card loader needs only what IPL
already requires, and *is* a bootstrap by construction. **JA BP6A**
(≈58 words, 7 cards, card reader only) is an even cheaper checkpoint
underneath A3, worth running first purely to prove a 1961 deck
executes at all.

### 10.4 Track B — the Exchange and real I/O

**B1 is I/O status reaching the CPU** — the p.118 discipline of §4.3,
**1–2 weeks** — and it is the gate for every interrupt-driven program,
MCP included. It is *not* on A3's path, which is why it moved out of
Track A. See §4 for the rest of the track's contents and sizing. Each step is independently checkable: the two
`ka_ex1*_bx-0.pdf` exchange test decks are its deck oracle, and
`docs/archival_inventory.md` already records that they *"need the
exchange as a real bus requester"*.

### 10.5 Track C — cycle accuracy

| step | what lands | checked against |
|---|---|---|
| C1 | **§8 step 4b**: split `execute()` (`bsv/StretchExecute.bsv:3448–4626`, 1,179 lines) into a multi-cycle arithmetic-unit module | the existing 389-`run` suite, unchanged — this is a refactor |
| C2 | SAU per-byte timing; then decimal and radix conversion inside it (layer 1's deferred half) | Perf. Char. Vol.1 Table 3 (SAU equations, printed pp.3-7..3-9); Vol.2's per-operation pages |
| C3 | PAU: FP add/compare timing, then multiply, then divide; VFL multiply/divide alongside | Vol.1 Table 2; Vol.2 pp. per operation |
| C4 | The look-ahead residue: separate interlock counters, **operand forwarding**, Y→Z/index-fetch/WBC stages, look-ahead unwind on interruption | Vol.1 Appendix A Table A-2 (PDF pp.69–71) for structure; Vol.2's *with*-vs-*without*-forwarding columns for timing |
| C5 | **Transcribe GENER and the four benchmarks; compare the model's clock counts with IBM's printed microseconds** | Perf. Char. Vol.2 pp.40–190; Vol.1 Table 10's eight whole-program execution times |

C5 is the step that makes "cycle accurate" a measured claim rather
than an asserted one, and it is why §8.2 matters.

### 10.6 Track D — the ULX3S

0a first (§10.2). Then SDRAM behind the MBCU interface, then
peripherals re-homed (SD card, UART, LEDs/switches), then bring-up.
Depends on C1 if 0a says the design does not fit, and on Track B for
anything beyond a bare bring-up.

### 10.7 Track E — the software stack

See §6. Its first increment is **not** MCP — it is A3's KA UL1 card
loader, then SSIP and the diagnostic decks, then (after the disk)
MCP. MCP's own stated minimum configuration (§6.1) fixes that order.

### 10.8 The honest totals

| | from today |
|---|---|
| **A3 — "it boots and runs a real program"** | **4–7 weeks** |
| Layer 1 ISA completeness (less mult/div) | +1–1.5 months |
| Layer 2 interruption residue | +2–4 weeks (A1 is the first slice) |
| Layer 3 the Exchange | +3–7 months |
| Layer 5 MCP | +2–4 months, **after** layer 3 |
| Layer 7 cycle accuracy | +3–6 months |
| Layer 8 ULX3S | +2–3 months |

Serialised naively, all four goals are **well over a year** of this
project's kind of day. Run as the four parallel tracks above — which
§9.5 shows is legitimate — there are **two** critical paths of
comparable length, and they are the two the owner named:

- **To MCP:** Track B (the Exchange, 3–7 months) → the disk → MCP
  (2–4 months) = **5–11 months**, because MCP's own minimum
  configuration (§6.1) names the Exchange, the disk and
  interrupt-driven I/O.
- **To cycle accuracy on hardware:** Track C (3–6 months) → Track D's
  remainder (2–3 months) = **5–9 months**, with step 0a in week one
  deciding how much of Track C is forced rather than optional.

They overlap only in the interval timer. So: **A3 in 4–7 weeks; a
cycle-accurate Bluesim model validated against Perf. Char. Vol.2 in
roughly 6–9 months; MCP running in roughly 6–12 months; all of it on
a ULX3S perhaps 3 months after whichever of those lands last.**

### 10.9 The single biggest risk

**The Exchange.** Named once, because it is the one thing that could
turn "well over a year" into "indefinitely":

- It is **on the critical path to the goal the user named first** —
  MCP's own minimum configuration (§6.1) requires it, the disk behind
  it, and interrupt-driven status through it. Nothing routes around
  it.
- It is **3–7 months, larger than everything built so far** (§4.5),
  and it is a *replacement* of `bsv/StretchIO.bsv`, not an extension:
  byte-serial where the model is word-serial, asynchronous where the
  model is synchronous, a second memory-bus requester competing with
  the I-box and look-ahead, with a per-channel status state machine
  and a priority scanner (§4.3).
- And it has **the weakest oracle of any layer here**. Layer 1 has
  IBM's own benchmark listings, the Programming Examples and 451
  pages of MCP; layer 2 has `jb_ax5b`; layer 4 has p.126 plus two
  loader decks; layer 7 has 150 pages of measured microseconds. Layer
  3 has `ka_ex1_bx-0.pdf` / `ka_ex1b_bx-0.pdf` — **"BX-0, Basic
  Exchange Parallel Maintenance Program"**, which *is* a real STRAP
  listing (its pages carry a listing-address column) and which this
  project has still never opened. But its own writeup calls it
  *"exclusively a manually operated test, since it is independent of
  the CPU"* (printed p.2), so how much of it can serve as a
  *program-level* oracle on this model is unknown. Meanwhile **no
  7619 Exchange CE manual exists in `docs/` or on bitsavers**
  (§11 items 7–8), so the Exchange's internals — scanner ordering,
  Exchange Storage addressing, the byte handshake — have no
  structural source at all.

**The cheapest mitigation is step 0d: open the two BX-0 decks before
committing to layer 3.** Establish how much of a manually-operated
exchange test can be driven from a program. If the answer is "little",
the honest conclusion is that the Exchange will be built
manual-derived and will be the least trustworthy part of the machine
— and that is worth knowing in week one, alongside step 0's three
other measurements.

*(Runners-up, for completeness: step 0b — whether the card reader's
`Vector`-of-`Reg` images can grow to a real deck without an
elaboration blow-up — and ECP5 area. Each blocks exactly one track;
the Exchange blocks the goal.)*

### 10.10 Read the totals as a lower bound

**Read these as a lower bound, not a forecast.** Three of these layers
— the Exchange, cycle accuracy, and the FPGA — are each larger than
the entire 28 project-days of work that produced the model as it
stands, and two of them have no regression suite to work against
(§0's caveat). The one thing this roadmap can promise with confidence
is the first milestone, because every piece of it is specified to the
page.

---

## 11. What the documents present do not answer

*(Partial — items are added as research lands. Each names the document
that would close it.)*

1. **`LVE`'s exact bit-level behaviour.** Ref. Man. printed p.20
   describes it only as enabling "indirect addressing"; this project
   searched for a page distinguishing it from `LV` and did not find
   one (`bsv/README.md` lines 118–126, `strap/README.md`'s Problem 2.2
   Method 3). *Needed:* `R23-9732_Manual04_7101_CPU_Jan63.pdf`
   (7101 CPU CE manual, 297pp) section 3's I-unit flow charts, or
   `TR00.722_Stretch_I-Unit_Design_Mar60.pdf` — **neither has been
   searched for this** (`docs/NEXT.md` §6 says so of the related
   refill question). Perf. Char. Vol.2 gives `LVE`'s *timings* for
   all three operand sizes, which bounds its cost but not its
   semantics. **This is a documentation blocker on an instruction
   IBM's own matrix-multiply benchmark uses seven times.**
2. **Whether `refillLegal`'s 1–15 gate applies to refills other than
   `R`/`RCZ`.** `docs/NEXT.md` §6 states the case fully and names
   `R23-9732` and `TR00.722` as the untouched places to look.
3. **Whether any memory or timing diagnostic deck measures its own
   elapsed time.** `ja_bp6a`, `ja_bm6a`, `ja_bb6b` are listed in
   `docs/archival_inventory.md` as never read for this purpose.
   *Needed:* read them; they are 6, 11 and 20 pages.
4. **What Master Reset actually clears.** The *power-on* state is
   documented — Ref. Man. printed p.53: *"1. The instruction counter
   and registers 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, and 12 contain
   random bits not necessarily with proper parity. 2. The
   interruption system is disabled. 3. All control units are restored
   to their initial power-on status."* — as is the IPL-time channel
   reset (printed pp.125–126). **Master Reset is not.** The entire
   corpus says one sentence: *"This switch provides a control reset
   and an error reset to all units of the CPU and to the storage
   bus"* (`R23-9713` printed p.25). Nothing says whether it clears
   the indicator register, the mask, or the instruction counter.
   *Needed:* **`R23-9698` and `R23-9699`, CE Manual of Instruction,
   7030 Instruction Unit, Volumes I and II** — named by `R23-9713`
   printed p.16 as the source for *"sequence diagrams of the manual
   controls"*. **Neither is in `docs/`.** `R23-9732` was searched in
   full and does not define it; it is a preventive-maintenance
   manual that only mentions Master Reset as a step inside check
   procedures.
5. **MOSTLY RESOLVED — see §5.3.** Ref. Man. printed p.35 states both
   of word 4's roles in one paragraph, so there is no contradiction:
   the maintenance bits are *"active only when the machine is in the
   maintenance mode"*, and *"After an initial program load, this
   location contains the first word read from the input unit. This is
   the control word for the initial load."* **What is left is one
   clause:** the console manual scopes the panel-key substitution to
   *"the **program controlled** references to storage address 04"*
   (`R23-9713` printed p.19), while IPL's write comes from the
   exchange — a reading that makes everything consistent but that no
   page states outright, with every documented IPL procedure running
   in maintenance mode. *Needed to close it:* the **7619 Exchange CE
   manual** (absent, see item 8). Note also that `R23-9713` Appendix
   C marks word 4 with neither a `P` nor a read-only flag, unlike
   words 1–3 and 5, so it is freely readable and writable — and it
   shows the **transit register (word 15)** and **word 7's
   left-zeros / all-ones counts (bits 17-23, 44-50)** that §2.3
   identifies as decimal VFL's real prerequisites.
6. **The disk storage unit's machine-type number.** Both physical
   planning manuals (`A22-6552` and `A22-6552-1`, printed p.6) say
   **IBM 353**; `D22-6513` printed p.20 and `R23-9702`'s system block
   diagram say **IBM 7303**; the Reference Manual (printed p.157)
   gives no type number at all. *Needed:* a 7612/353 CE manual or an
   IBM systems-reference bill of materials; neither is in `docs/`,
   and `docs/archival_inventory.md` records that all 52 PDFs of
   bitsavers' `ibm/7030/` are already here.
7. **Whether `LOC` to a single-device control unit is legal.**
   `R23-9702` printed p.31: *"The locate instruction, however, is
   invalid to the card reader because only one card reader is
   assigned to each reader control unit"* — versus the Reference
   Manual printed p.120, which states `LOC`'s semantics with no device
   exclusion and says it is accepted even when the unit is not ready.
   *Needed:* a **7619 Exchange CE manual**, which `docs/` does not
   contain (it has CE manuals for the 7503/7614, the 7101 CPU and the
   maintenance console, but none for the Exchange itself). This is
   the most consequential missing document for layer 3.
8. **Exchange internals**: scanner ordering, Exchange Storage
   addressing, the per-channel control-word store's layout (the
   Reference Manual says control words live *"in the exchange"*,
   printed p.117, but never gives an address or a register count),
   and the byte-response handshake from the Exchange side. The
   Reference Manual describes behaviour, not mechanism. *Needed:* a
   **7619 Exchange CE Manual of Instruction**, whose form number
   appears in no cross-reference found and which is **not in `docs/`
   and not on bitsavers**. `ka_ex1_bx-0.pdf` / `ka_ex1b_bx-0.pdf` are
   *not* that manual — they are the BX-0 maintenance **program**, a
   real STRAP listing but a manually-operated one, still unopened by
   this project (step 0d).
   Related and unresolved: whether the Exchange writes the stepped
   data-word-address back into location 4 as the deck loads. Step 5
   branches to *"the data word address field of the control word in
   core storage location 4"*, and BX-0's deck is consistent with that
   field being **unchanged** (its value is the address of `START`),
   but no page states the write-back behaviour for the IPL case.
   Also unexplained: BX-0's first instruction is `NOP`, where Ref.
   Man. printed p.126 says it *"must be BRANCH DISABLED"*.
9. **How FORTRAN IV's FORMAT conversion is implemented.**
   `C22-6751` localises it inside *"the Input-Output Control
   Subroutine (actually a whole family of library subroutines)"* and
   never names an instruction; `CV`/`LCV`/`DCV` appear nowhere in its
   37 pages. *Needed:* the FORTRAN library source, which is **not in
   `docs/`** and is not known to survive. (It matters less than it
   looks: MCP demonstrably uses `CV`/`LCV`/`LTRCV` for its own
   message formatting, so radix conversion must work regardless.)
10. **Whether decimal mode faults on an invalid digit code
   (1010–1111).** The Reference Manual's complete Indicator List has
   no invalid-digit indicator, so it cannot fault — but the *result*
   is unspecified for arithmetic. The Programming Examples state only
   the *load* case. *Needed:* the CE logic manuals.
11. **What an operating system uses chaining for, beyond IPL.** The MCP
   Reference abstracts control words away behind pseudo-ops (printed
   p.6: *"the necessary control words, mode, density, interrupts,
   etc., are handled by MCP"*). *Needed:* the MCP System Analysis
   Guide's I/O section or the `MCP_Mar63_*.pdf` listings — both in
   `docs/`, so this is a reading gap, not a holdings gap.


---

## ADDENDUM 2026-10-16 — the CPU side of IPL, from a second manual

The IPL answer above came from the Reference Manual's Exchange chapter
and describes what the **Exchange** does. `R23-9732` (7101 CPU CE
manual) gives the **CPU side**, which this document lacked entirely.
Printed **5-6** (PDF 193), verbatim:

> *"When depressed, the INITIAL PROGRAM LOAD pushbutton will cause the
> following sequence: a. A program halt operation will be executed to
> terminate the execution of the stored program. b. A master reset
> operation will be executed to reset all of the control and error
> triggers in the CPU. c. A start clock operation will be executed to
> reinitiate the generation of controlled clock pulses. d. An initial
> program-load-start pulse will be sent to the Exchange. This pulse
> will: 1. Reset the Exchange circuits to terminate all I/O
> operations. 2. Reset all control words in the Exchange to zero.
> 3. Reset all I/O devices to an initial power-on status. 4. Set the
> Exchange circuits so that the channel signal will be interpreted in
> a special way."*

**IPL is not atomic — it is an internally sequenced four-step
operation, and step (c) means IPL STARTS THE CLOCK ITSELF.** That also
explains why `jb_ax4b`'s operating procedure lists *"Depress Master
Reset / Depress Start Clock / Depress IPL"*: the first two are
belt-and-braces, not prerequisites.

The same manual confirms the Exchange's simulated control word word
for word, and settles a question this document left open — printed
**5-7**: *"**Note** — Data word address 4 refers to a special core
storage location which is used only during initial program load
operations."*

And it states the `BRANCH DISABLED` requirement more explicitly than
the Reference Manual does, printed **5-7**: *"this instruction, which
is the first instruction of the stored program, **must be a Branch
Disabled instruction to the address of the second instruction.** As a
result of this requirement, the second instruction of the newly
stored program is actually the first instruction of the desired
program."*

### A contradiction to be aware of, not resolved

`R23-9732` printed 5-6 says the operator must press **CHANNEL SIGNAL
first, then INITIAL PROGRAM LOAD.** That contradicts five other
sources in this corpus — Reference Manual printed pp.125-126,
`jb_ax4b`, the System Test Programs, the DCP manual and `ka_ul1` — all
of which say IPL first, then the signal. **It also contradicts itself
two paragraphs later** (*"After the INITIAL PROGRAM LOAD pushbutton is
depressed, the selected channel signal will cause…"*).

**For the model, follow the Reference Manual ordering**: IPL arms, then
the channel signal fires. That is the only order consistent with *"set
the Exchange circuits so that the channel signal will be interpreted
in a special way"* — arming must precede the thing armed. Recorded as
an internal inconsistency in `R23-9732`, not as an open question.

Incidentally useful from the same page: a tape drive generates a
channel signal at the end of a rewind, so **a spurious channel signal
can steal the IPL.** Worth knowing when the tape subsystem exists.

### Also now sourced verbatim: SSIP's sense switches are the panel keys

Printed **6-2**: *"This program contains eight options which are
selected by **sense switches (PANEL KEYS)**"*, with a table assigning
bits 32-39 — 32 suppress error printout, 33 stop on error, 34 repeat
100 times, 35 repeat indefinitely, 36 print section identity, 37
repeat block, 38 start each test enabled, 39 spare. This replaces a
four-document inference chain with one parenthetical.
