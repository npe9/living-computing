# Cycle-accurate and block-level-accurate: the sources, the gaps, the plan

The owner's direction (2026-11-24): once the full system works, make the
model **cycle-accurate and block-level accurate**. This document is the
plan, written before the work starts, so that it can begin when the core
reaches rc's prompt. It changes no behaviour of the core or of the
reference model. What it adds is a read-only tool,
`tools/cyc_classify.py`, with its test `tests/test_cyc_classify.py`, and
this text.

"Cycle-accurate" is used here in two strengths, and the plan keeps them
apart:

* **cyc-accurate.** Every HRI record's `cyc` equals the printed Chapter 4
  occupancy of that instruction in that context: its base time, plus the
  delays the printed tables permit, with the memory symbols resolved by
  named parameters. Today `cyc` is the base time only, under the p. 4-1
  assumptions.
* **clock-accurate.** The number of clocks between two retirements, and
  so the total run time, equals what the part would take with a stated
  board (memory wait states, devices). This includes everything charged
  *outside* `cyc` today: prefetch fills, memory operands, stack-cache
  traffic, table walks and bus contention.

Printed pages are the January 1993 Programmer's Reference Manual (PRM)
unless another document is named. "DS" is the December 1992 Advance Data
Sheet, whose PDF page equals its printed page. "2100" is the March 1991
ATT2100 Hardware Specification; printed 3-N is its PDF page 102+N, and
5-N is PDF 110+N. "MPR" is Microprocessor Report 6:2. Every number cited
below was read from the rendered page image, not from the OCR layer.

## 1. Sources

### 1.1 The documents

| source | timing content | where |
|---|---|---|
| PRM Chapter 4 | Tables 4-32…4-40: base times and delays; the p. 4-1 assumptions; p. 4-2 symbols (IC, PDU, A, D, Q, M, N, SC, E, EU); §4.2's delay prose (p. 4-5: fetch delays "may be extended" if the EU is using I/O; p. 4-6: data hazards and "internal contention for I/O"); §4.3's folding rule (p. 4-7) | pp. 4-1…4-7; transcribed in `docs/timing.csv`, discussed in `docs/timing_tables.md` |
| PRM §1.9 | "call, allocate, deallocate, and return … can be as little as four clock cycles" | p. 1-31 |
| PRM §1.10 | aggressive prefetch "in quad-word pieces consisting of two double-word I/O requests"; prefetch follows predicted and non-indirect branches and stops at indirect ones; demand fetch on a mispredicted or indirect branch; a demand request lets the PDU's I/O in progress complete first | p. 1-32 |
| PRM §1.10.1–1.10.2 | the PDU prefetches down the predicted path "without any discontinuity"; "The pipeline runs more efficiently if three instructions, which do not reference off-chip memory, are sandwiched between the compare instructions and the jump" | p. 1-33 |
| **PRM §2.6, Table 2-4** | **Address Translation Performance**: text micro-TLB hit 0; micro-TLB miss with TLB/NPSR hit 1; nonpaged walk A + 1 (text) or A + 3 (data); paged walk 2A + 3, or 3A + 3 when R (or M) must be written back. "These performance numbers do not include the time required to access the actual item." "An A represents the I/O delay for a single word access." | p. 2-9. **Not in `timing.csv`** before this plan |
| PRM §2.1 | the micro-TLB "contains the last translation used by the prefetch unit and provides zero-cycle address translation. If the micro-TLB misses, one cycle is required for update if the address translation hits in the text TLB or text NPSR"; a TLB/NPSR miss walks the tables in hardware | p. 2-1 |
| PRM Appendix A | the bus: A.1 arbitration (the new master owns the bus the cycle after BGRANT; the arbiter inserts a dead cycle), A.3 transactions (START begins, DTACK ends; "Text reads are always double-word transfers"; loopback after a read), A.3.3 RMW (a dead cycle after it), A.3.4 block transfers ("a series of single-word bus transfers"), A.4 retry and error. Figures A-2 (read) and A-3 (write) | pp. A-1…A-8. The text calls the read figure "Figure A-1"; the caption reads "Figure A-2" |
| PRM Appendix B | two 1× clocks in quadrature (CLK23, CLK34), four internal phases per clock; period 50–100 ns at 3.3 V, 33.2–50 ns at 5 V; setup, hold and valid times | pp. B-5…B-9 |
| DS p. 1 | "Single-cycle instruction execution for most instructions"; "Peak rate of better than one cycle per instruction"; "Operand bypass mechanism that reduces off-chip reads"; 250 mW at 3.3 V, 20 MHz; 900 mW at 5.0 V, 30 MHz | p. 1 |
| DS p. 26 | Prefetching Strategy, the p. 1-32 text **plus the demand mode**: "The I/O request is made for a double word … Demand fetching is the default mode after reset". Branch folding: "for selected single-parcel instructions or a three-parcel instruction, A, if the following instruction, B, is a jump, the next-PC field for the instruction A is the (predicted) target of the instruction B" | p. 26 |
| DS p. 27 | "if a jump is folded into the previous instruction, the trace will occur after the jump … all jumps must be encoded as three-parcel and, hence, will not be folded" | p. 27 |
| DS pp. 28–31 | IL[2:0] held for two cycles before an interrupt is recognised; CATCH, ENTER, MUL, DIV, REM, UDIV and UREM are interruptible; ENTER's two flush cases; "usually no entries need to be restored and CATCH takes only one clock cycle" | pp. 28, 31 |
| DS pp. 32–33 | CONFIG: the PB/IC/SC enables and the prefetch mode; TIMER1/TIMER2 count clock cycles or "completed instructions (folded branches are not counted)"; after a CONFIG write the NOPs needed vary with "the number of wait-states being used by I/O transactions" (no count printed) | pp. 32–33 |
| DS pp. 49–54 | the Appendix A bus text again, with Figures 28 (read), 29 (write) and 30 (RMW, with and without retry). There is no transaction-type table: IOC[1:0] is a count of words remaining, and D/T separates text from data | pp. 49–54 |
| DS pp. 61–67 | Tables 47–53: the clock, synchronous input, output, relinquish, DTRI and BREQ/BGACK timings. Edge relationships only, no clock counts | pp. 61–67 |
| 2100 Chapter 3 | Tables 3-1…3-10: **the same tables as PRM Chapter 4, cell for cell, with one exception.** The SC/M quad-word DQM row is printed **4 + Q** (2100 p. 3-3; PRM p. 4-4 prints 4 + D). `8 * S` is printed in the 2100 too. A 2100-only footnote: "Data type delays only occur for signed multi-cycle instructions". The 2100 calls the fetch delays "best case" and says I/O contention "cannot be accurately predicted" (p. 3-4) | 2100 pp. 3-1…3-5 |
| 2100 Table 6-1 | the same translation costs as PRM Table 2-4 | 2100 p. 6-6 |
| 2100 Chapter 5 | "One clock period synchronous bus transactions", "A one cycle minimum access synchronous I/O protocol" (pp. 5-1, 1-1). Its own figures draw a wait state in the examples | 2100 pp. 1-1, 5-1, 5-12…5-15 |
| 2100 §2.15 | pipeline considerations: two instructions between a C/V setter and a CPU read of the PSW; ENTER after a page invalidation; the untruncated byte/half result; SHAD after ENTER/RETURN needs two NOPs; the only stage name printed is "RR" (p. 2-39) | 2100 pp. 2-39, 2-87 |
| MPR | CRISP's buffer was 512 bytes and Hobbit's is 3 KB three-way; the decoded cache is 32 × 192 bits in both; two next-address fields; "Most instructions execute in a single clock cycle"; 20 MHz at 3.3 V. There is no CPI, Dhrystone, penalty or bus figure for the Hobbit | MPR pp. 7–8 |

None of these documents prints any of the following:

* a value, in clocks, for A, D or Q;
* a definition of S;
* the unit of E;
* a wait-state count;
* a prefetch-buffer line size or replacement policy;
* a TLB replacement policy;
* the decoded-cache fill policy;
* a stack-cache refill cost (CATCH is a flat 1);
* MUL's data dependence;
* the stage in which a branch resolves.

### 1.2 The 1st Edition release

`/tmp/p9/plan9-1e.tar.bz2` was **not on disk** on 2026-11-24 (`/tmp/p9`
holds only `plan9-1e/hobbit` and `tree`). The kernel sources read here
are the copies vendored from that tarball in
`tools/plan9-1e/sys/src/9/hobbit/`; `docs/plan9_port.md` gives the
tarball's sha256. What they say about timing:

| item | where | what it says |
|---|---|---|
| `delay(ms)` | `clock.c:12-19` | spins `1000*ROUNDUP(eeprom.clock,2)/2` laps per millisecond, with `eeprom.clock` in MHz (`io.h:147`). So **the author assumed 2 clocks per lap.** In `s9term` the lap is at 0x8002f72c: `CMPGT` (three-parcel 0x1d, `9ddf`), `ADD` (one-parcel 0x14, `53e5`), and `JMPTY 0x8002f72c` (`1ffc`) folded into the ADD. Under Chapter 4 that is 1 + 1 + 0 = **2**, from Table 4-32 for CMP and ADD and from Table 4-35's "correct prediction, folded". This is an independent, period witness to the fold and to single-cycle CMP and ADD. The loop's last lap mispredicts with the compare two instructions back, which is class 2 in §2.1 below. |
| `mdelay` | `deviic.c:55-62` | `count*25` laps with no CPU-clock term. A crude wait, not a timing claim |
| `scsi.c:167` | | `ms *= ROUNDUP(eeprom.clock,2)/2`, the same 2-clock assumption per lap |
| `HZ 25` | `mem.h:21` | the kernel expects 25 ticks a second from the Quart counter. `clockinit` programs `Crystal/(2*16*HZ)` (`deveia.c:528-541`, Crystal 3.6864 MHz). `docs/p9boot.md` records that the shipped image loads 0xFFFF instead |
| `CONFIG` | `raml.s:14`, `roml.s:16` | `PM|PE|IE|SE|PX|KL`: **aggressive prefetch**, with the prefetch buffer, IC and stack cache enabled. This is the mode the 1e kernel runs in, and not the reset default (DS p. 26: demand) |
| `IOACK`, `IONAK` | `io.h:1-2` | two device windows, `IOBASE + x` and `IOBASE + 0x08000000 + x`. The names suggest the board acknowledges (DTACK) one window itself and leaves the other to the device. Nothing in the release says so. This is the only board bus-timing hint, and it is **no source** |
| TIMER1/TIMER2 | `machine.h:30-36` | the CONFIG bits are named, but 1e never enables a counter. Nothing in 1e reads cycles |

No file in the release describes the board's memory, its wait states or
its DTACK logic.

## 2. The gaps, measured

### 2.1 The `cyc` differences between the reference model and the core

`tools/cyc_classify.py ref.hri core.log [--all]` pairs the two traces as
`tools/p9trace_cmp.py` does. It describes every conditional jump from the
reference stream alone (host parcel count, p. 4-7 foldability,
prediction, outcome, compare distance), gives each disagreement a cause,
and exits 1 if any disagreement is unexplained. Runs on 2026-11-24
(Verilator, this branch):

| run | records | conditional jumps | `cyc` differs |
|---|---:|---:|---:|
| `za main9.s` | 125,572 | 20,146 | 462 |
| `zc frexp.c` | 1,651,700 | 238,194 | 8,571 |

| class | ref | core | za | zc | cause |
|---|---:|---:|---:|---:|---|
| 1 | 1 | 0 | 224 | 6,816 | **the core folds a branch into a five-parcel instruction** |
| 2 | 2 | 3 | 161 | 1,298 | a folded, mispredicted branch whose compare is two instructions back |
| 3 | 1 | 3 | 77 | 441 | the same with the compare three instructions back |
| 4 | 1 | 3 | 0 | 16 | an unfolded mispredict that is the first instruction after a trap's return |

**Class 1: the reference is right.**

* The core folds into a five-parcel host because `maybeFold`
  (`HobbitDecode.bsv`) folds any one-parcel branch found at `p[plen]`.
  The six-parcel decode window reaches past a five-parcel host, and
  nothing checks `plen`.
* PRM p. 4-7 says a one-parcel branch folds "into a previous one- or
  three-parcel instruction". DS p. 26 likewise names only "selected
  single-parcel instructions or a three-parcel instruction".
* So a jump after a five-parcel instruction is unfolded, and costs 1 when
  correctly predicted (Table 4-35).
* This is visible beyond `cyc`. A TIMER counting "completed instructions
  (folded branches are not counted)" (DS pp. 32–33) would count these
  jumps on the part and not on the core.

**Classes 2 and 3: the core is wrong, and the reference has the plain
reading.**

* The core prices every mispredicted folded branch at a flat 3:
  `pendFold <= tagged Valid (foldRecord(o, foldMispredicted(o) ? 3 : 0))`
  in `HobbitCore.bsv`. It resolves a folded branch only when its host
  reaches EU_S3.
* Table 4-35 (p. 4-5) prints 3, 2 and 1 for a jump 1, 2 and 3
  instructions after its compare, with no folded/unfolded qualifier. It
  also prints a folded "4 or more" row of **0**. So the part resolves a
  folded branch *earlier* than an unfolded one, never later.
* The reference reads the unqualified rows as covering folded branches
  too (`_conditional_jump_cycles`).
* `docs/timing_tables.md` §6 and §7 item 9 instead say that no folded
  incorrect row is printed for 1–3 instructions. Read strictly, that
  means *no* printed value at all. **The two documents contradict each
  other.** The plan adopts the reference's reading as the only one that
  gives these cases a number, and asks for it to be recorded as a reading
  (milestone C1).
* Under either reading the core's 3 at distances 2 and 3 has no printed
  row.

The joint table (`--all`) shows the rule rather than only its
exceptions. Every folded mispredict at distance 0 agrees at 3 (za 7,337,
zc 116,861). Every one at distance 1 or 2 differs. Every correctly
predicted folded branch agrees at 0.

**Class 4: a harness artefact with no printed row.**

* The jump follows an unimplemented-instruction trap: 1e's floating point
  (`d9f5…`), emulated by the kernel. Its PSW.F is the kernel's, not a
  CMP's.
* The core charges 3 because `mkHobbitEuS1.redirect` resets `sinceCmp`
  to 0 at every redirect.
* The reference charges 1 because it indexes Table 4-35 by the last CMP
  it saw, six records back. It does this because the A2 host harness
  hides the handler.
* Table 4-35 has no row for a flag that did not come from a compare. On
  the real machine the handler's KRET restores the PSW. The underlying
  core defect is real, though: after a redirect, the compare distance is
  not 0.

**Latent classes, not yet observed** (read from the code; za and zc reach
neither):

* (a) A folded mispredict four or more instructions after its compare.
  The core gives 3; Table 4-35 prints 0.
* (b) A mispredicted branch folded into a five-parcel *compare*. The core
  resolves it in EU_S2 as `foldMis` and charges 3. The reference counts
  it as unfolded at distance 0 and charges 3. They agree only by
  coincidence (za 289, zc 23,198, the `nofold host5 dist0` rows).
* (c) A compare that is squashed. `sinceCmp` counts issued, not retired,
  compares.

### 2.2 A, D, Q and S: what the data sheet can pin

**Nothing in the data sheet pins a value.** It prints no instruction
timing at all. Its bus figures are examples in which the *slave* chooses
when DTACK arrives (DS p. 6: DTACK "is asserted and deasserted by the
slave device"), so they describe a board, not the part. What the sources
do pin is the **shape** of the terms:

* **A** is "the I/O delay for a single word access" (PRM p. 2-9). It is
  a bus quantity set by the board's DTACK. In Figures A-2/A-3 and DS
  28–30, a single-word transfer runs from its START cycle to its DTACK
  cycle: **3 clocks** drawn (START in 4, DTACK in 6).
  * No figure draws START and DTACK in one clock.
  * The 2100 claims "one clock period" transactions (2100 p. 5-1), but
    its own figures draw two clocks or more.
  * The model's A = 1 is therefore faster than anything drawn.
* **D and Q** are each "a series of single-word bus transfers" (p. A-6),
  one START per word (DS p. 10, IOC). So the shape is **D = 2A, Q = 4A**,
  as the model has it, if every word waits the same. The drawn block
  transfers do *not* wait the same: the first word takes 3 clocks and
  the second 2 (Figure A-2, cycles 11–13 and 14–15).
* **`5 + 2D` and `8 + 2D`** (Table 4-37). PRM p. 1-32 and DS p. 26 say a
  prefetch quad-word is "two double-word I/O requests". PRM p. A-4 says
  "Text reads are always double-word transfers". So a quad-word text
  fill costs **2D**, not Q, which explains `timing_tables.md` §7 item 6's
  first half. Why two quad words also cost 2D stays unexplained.
* **SC/M quad-word DQM, `4 + D`.** The 2100 prints this cell **4 + Q**
  (2100 p. 3-3, image-checked). That supports the reading that the PRM's
  `4 + D` is a misprint (`timing_tables.md` §7 item 4). The PRM is still
  the document for the 92010, so the cell stays printed-as-is, with the
  2100's value as evidence.
* **S** is undefined in both manuals. `S_CYC = A_CYC` stays a choice.

**What can be pinned instead.** With a board choice of `w` wait states
per word, START-to-DTACK is `2 + w` clocks if DTACK can come in the cycle
after START, as the second beats are drawn. That gives A = 2 + w,
D = 2A, Q = 4A. Whether the bus overlaps the next START with the
previous DTACK is not drawn anywhere.

**`HobbitBus.bsv`'s header is wrong about this.** It says "Figure A-3,
printed p. A-5, shows START in consecutive bus cycles 14 and 15", and
uses that to justify A = 1. The figure, re-read at 300 dpi, has START
low in cycles **4, 11 and 14** only, and DTACK across the 6|7, 13|14 and
15|16 boundaries. A = 1 is therefore a model choice with no figure
behind it. The comment should say so. It is **not edited here**, because
`bsv/` is in flight; see milestone C0.

### 2.3 What is charged outside `cyc`, measured

| run | Σ `cyc`, reference | Σ `cyc`, core (paired records) | stub records (`cyc`) | core clocks | clocks / Σ `cyc` |
|---|---:|---:|---:|---:|---:|
| `za main9.s` | 148,896 | 148,987 | 145 (708) | 607,746 | 4.1 |
| `zc frexp.c` | 2,244,136 | 2,227,760 | 844 (4,233) | 12,019,025 | 5.4 |

On these runs, three quarters or more of the core's clocks are outside
`cyc`:

* prefetch fills: the boot window and demand fills, one 64-bit line per
  three clocks in the boot fill;
* memory-operand fetches: one word a clock, A = 1;
* stack-cache refills, during which nothing issues behind a CATCH;
* operand-forwarding stalls;
* the host stub's wait for the replayed kernel, which is host time, not
  machine time.

No document prices the core's particular mix. Chapter 4 prices the same
events as delays:

* Table 4-37: an IC miss is 3 if the instruction is in the prefetch
  buffer, else 5 + D, 5 + 2D or 8 + 2D; EU pipeline empty is 2.
* Tables 4-38/4-40: an operand in memory is 1 + A; a destination in
  memory is A.
* Table 2-4: translation.

The p. 4-1 assumptions are exactly the conditions under which these are
all zero. The first job of the cycle work (milestone C2) is therefore to
**attribute** each core clock to a table row or to the harness.

### 2.4 Stack cache, MMU, decoded cache, prefetch buffer

| mechanism | documented | a choice |
|---|---|---|
| ENTER flush | 1 + Q·E (Table 4-36); flushed in quad words (pp. 3-19/3-20; DS p. 31's two cases) | E's unit (the model reads it as 16-byte blocks); Q |
| CATCH refill | CATCH = 1 (Table 4-36); "usually no entries need to be restored and CATCH takes only one clock cycle" (DS p. 31); fills in 16-byte blocks (p. 3-10) | the cost when entries *are* restored: no table prices it. The core lets the refill run in the background and holds issue behind CATCH, outside `cyc` |
| CRET's CATCH portion | 11 + Q (Table 4-36) | the fill cost, as for CATCH |
| N (valid entries) | defined, never used (p. 4-2) | — |
| TLB miss / walk | **Table 2-4, p. 2-9**: 0 / 1 / A + 1 / A + 3 / 2A + 3 / 3A + 3; the micro-TLB (p. 2-1) | TLB replacement (the core uses round-robin, `HobbitMmu.bsv`); the micro-TLB is not modelled; the core's walk is combinational and uncharged (`HobbitMmu.bsv` header); the reference has no TLB |
| decoded instruction cache | 32 entries × 192 bits, direct-mapped (DS p. 1); an IC miss with the instruction in the prefetch buffer costs 3 (Table 4-37) | the index function; when the PDU fills it (how far ahead, along which path) |
| prefetch buffer | 3 KB three-way (p. 1-1; DS p. 1); quad-word pieces as two double-word requests; the aggressive and demand modes and what stops them (p. 1-32, DS p. 26); a 64-bit path to the PDU (DS p. 3) | the line size (the core: 64-bit lines, set = addr[9:3]); replacement (the core: an invalid way first, else one rotating victim pointer); fill order and priority against the EU (the core: refill, then operand, then prefetch) |
| bus contention | "I/O contention occurs when the EU wants to make an external memory access while the PDU is in the middle of an access" (p. 4-6); a demand request lets the PDU's I/O complete first (p. 1-32) | its cost: the 2100 says it "cannot be accurately predicted" (2100 p. 3-4) |
| data hazards | "a previous instruction tries to write to a memory location that overlaps the location being read" (p. 4-6) | its cost: none printed |
| MUL | 3…20, data dependent (Table 4-33) | the dependence (both models take 20) |
| interrupt latency | IL held two cycles (DS p. 28); the interruptible instructions | the rest |

## 3. Block-level accuracy

No board documentation exists in the release or in the corpus: no
schematic, no memory timing, no DTACK logic. So "block-level accurate"
can honestly mean two different things, and the plan claims only the
first.

**(1) The CPU's documented blocks, each matching documented behaviour per
clock.** The blocks are Figure 1-1's (DS p. 3): PDU, decoded-instruction
cache, EU stages, stack cache, MMU/TLB and the bus unit. Each has a
boundary the model already draws as a module (`docs/conformance_1to1.md`
§1). The block is accurate when its *externally visible events* happen on
the documented clock: issue, resolve, squash, fill request, bus START,
TLB update. Where a page prints a number, the block reproduces it. Where
no page does, the block implements a named choice, and the choice is one
switch in one place.

**(2) Board devices.** These are the SONIC (DP83932), the Quart (68C94),
the WD33C93, the IIC/EEPROM, the LCD and the memory. They have their own
vendors' data sheets but no board-level timing. Their *functional*
behaviour is pinned by the kernel and by those data sheets
(`docs/p9boot.md`). Their *timing* is board choices: DTACK latency per
window (`IOACK`/`IONAK`), the Quart's counter period, the memory's wait
states. They are parameters of a board model, never claims.

**Oracle per block:**

| block | what is checkable | oracle |
|---|---|---|
| EU base times | Tables 4-32…4-36 per instruction | **printed table**: `timing.csv` with `check_timing.py`, and the hand-derived goldens' `cyc` column |
| branch folding / prediction | p. 4-7 rule, Table 4-35 | **printed table**, plus a **hand-derived golden per class** with a per-cycle trace (which stage the branch resolves in, which slots are squashed) |
| PDU + decoded cache | Table 4-37 rows; p. 1-32 prefetch order; CPU-prefix 1 | **hand-derived goldens** that force each Table 4-37 row (a cold IC with the line in the PFB; a line not in the PFB; an instruction straddling quad words), with the PFB/IC policy choices stated |
| prefetch buffer | organisation, fill sizes, mode | **documented choice** for replacement and line size, plus a **twin** check that the fill sequence on the bus matches p. 1-32 (quad = two double-word text reads, D/T low) |
| stack cache | ENTER 1 + Q·E; CATCH 1; refill in 16-byte blocks | **printed table** for the instruction; **documented choice** for the refill's clocks, plus the twin |
| MMU | Table 2-4, p. 2-1's micro-TLB | **printed table**; **choice** for replacement; goldens on the MMU core that force each row |
| bus unit | Figures A-2/A-3, DS 28–30: the order of START, IOC count, DTACK, loopback, the dead cycle after RMW, arbitration | **printed waveforms** transcribed cycle by cycle into `run_bus.sh` checks. Clock counts that depend on the slave are a **board choice** |
| timers | count clocks or completed instructions (folded not counted) | the core's own clock count and fold count, against the **twin**. This is architecturally visible, so it is the strongest check that `cyc` and folding are right |
| board devices | — | **documented choices** (a board file), never claims |

### 3.1 The reference model needs a cycle-level twin

**Decision: yes.** `hobbit_sem` is a one-instruction model, and its `cyc`
is the base time under the p. 4-1 assumptions. It cannot say how many
clocks the boot takes, and it should not grow a pipeline: its
independence from the core is its value. Yet clock accuracy on long runs
needs an independent number for every record, not just a statement that
both models agree on the base time. Three things show the need:

* the zc run's 9.8 million clocks that `cyc` does not see;
* the boot's interrupts, which land by model time (the reference paces
  the Quart by Σ `cyc` at 20 MHz, `tools/p9boot.py` CHOICES `clock`);
* the fact that a cycle-accurate core will deliver interrupts by its own
  clock, not by record number.

**Sketch: `sem/hobbit_timing.py`, an independent timing model fed by the
HRI stream.**

* **Inputs.**
  * The reference's HRI records: pc, insn, sp/msp, write and trap.
  * The memory image, read only to decode the parcels at each record's pc
    and its fold partner.
  * A *board* file holding the choices: wait states per address window,
    A/D/Q derived from them, CONFIG.PM, and the cache-enable bits.
  * The policy choices: PFB replacement, IC index, TLB replacement, MUL.
* **State it keeps.**
  * Its own PFB tags (3 × 128 sets) and decoded-cache tags (32
    direct-mapped).
  * The micro-TLB and the two 32-entry TLBs (System only).
  * Compare distance in *retired* instructions.
  * Fold state by the p. 4-7 rule applied to the *static* predecessor
    (pc + length), not the dynamic one.
  * Stack-cache occupancy, from the records' sp/msp.
* **Outputs, per record.**
  * The base `cyc`.
  * The list of delay rows charged, with ids from `timing.csv` plus a new
    Table 2-4 block.
  * The clocks to retirement.
  * A running total.
* **Contract.** The twin imports nothing from `sem/hobbit_sem.py`'s
  timing (`_conditional_jump_cycles`, `_retirement_cycles`), from
  `bsv/`, or from `tools/cyc_classify.py`. It is written from the pages,
  as `hobbit_sem` was, so that three independent numbers exist for every
  record:
  * the reference's base `cyc`;
  * the twin's base `cyc` and delays;
  * the core's `cyc` and its clocks to retirement.

  The core already prints total clocks (`P9HOST EXIT … clocks`). Per
  record, it would need an optional retirement-clock line beside the HRI
  line. That is behind a flag so the HRI format does not change.
* **Cost.** About one dictionary lookup per record, so the 22.5-million
  record boot is minutes in Python, and it can run on recorded traces
  offline.

The twin adjudicates the way `docs/sem_adjudication.md` adjudicates
values. A disagreement goes to the page. If the page is silent, it goes
to a named choice, and the choice lives in the board or policy file.

## 4. The staged plan

The suite stays green at every step: `tests/run_tests.sh`, and
`tests/run_p9host_tests.sh` for the long runs. Each step is its own
commit, keeps the Flute-shaped structure (`docs/bluespec_architecture.md`
rules 1–3: stage modules, stalls as signals, multi-cycle datapath in
boxes), and changes `cyc` only where its gate says so. The milestones
start when the core reaches rc's prompt, except C0 and C1, which are
paper and tooling.

| # | milestone | change | gate (runnable) |
|---|---|---|---|
| **C0** | sources (this commit) | the plan; `tools/cyc_classify.py`; the inventory | `python3 tests/test_cyc_classify.py`; `cyc_classify.py` exits 0 on za and zc, with every difference in a named class |
| C1 | decide the readings | record in `timing_tables.md` §6/§7: (i) the unqualified Table 4-35 rows cover folded branches (the reference's reading), or the alternative; (ii) Table 2-4 as a new block of `timing.csv` (13 rows, p. 2-9); (iii) the 2100's 4 + Q beside `t434_scm_qw_msc_qw`; (iv) A = 1 restated as a choice, with the HobbitBus header corrected when `bsv/` is free | `check_timing.py` accepts the new rows with the printed count (13) for Table 2-4; one injected defect per new rule, recorded in its docstring |
| C2 | the twin, base times only | `sem/hobbit_timing.py` with the p. 4-1 assumptions: base `cyc` from the pages, folding by the static rule, compare distance by retirement | on the goldens, the twin's `cyc` equals the hand-derived column; on za and zc, the twin equals the *reference* on every record. A twin/reference disagreement goes to the page and is classified with `cyc_classify` |
| C3 | the core's folding and resolution | (a) `maybeFold` does not fold into a five-parcel host (class 1); (b) a folded branch resolves by compare distance, in the stage the unfolded one would, so it pays 3/2/1/0 (classes 2, 3, latent a); (c) `sinceCmp` counts retired compares and is not reset by a redirect (class 4, latent c). Each is a structural change to the PDU/EU_S1 stage modules, not a `cyc` patch | one hand-derived golden per class, with an injection table; `cyc_classify.py` on za and zc reports **0** differences; `test_cyc_classify` keeps its synthetic classes |
| C4 | the kernel's `cyc` | run `run_p9kern.sh` with `cyc` compared (the reference's `System.untimed` mnemonics listed first: those are the cells Chapter 4 does not print, e.g. CPU-escape forms); a choice per untimed cell | `p9kcmp`/`p9trace_cmp --cyc` on the 300,000-record boot sample: every record agrees, or falls in a class `cyc_classify` names |
| C5 | attribute the clocks outside `cyc` | the core prints, behind a flag, each retirement's clock and the reason for each idle clock (fill, operand, refill, stub); a reader totals them by Table 4-37/4-38/2-4 row | the attributions sum to `P9HOST EXIT` clocks exactly, on za and zc |
| C6 | the bus is the one source of A | the core's memory traffic goes through `mkHobbitBusMaster` with a board slave whose DTACK latency is a parameter (the board file); A, D and Q follow from it (D = 2 transfers, Q = 4, text = double-word); Figures A-2/A-3 transcribed as cycle-by-cycle bus goldens | `run_bus.sh` reproduces the printed waveforms (START/IOC/DTACK/loopback columns) at `w = 1` (the drawn first word); the suite green at `w = 0` (today's numbers) |
| C7 | PDU timing | CONFIG.PM: aggressive (quad = two double-word text reads, following predicted and non-indirect branches, stopping at indirect ones) and demand (a double word, decode until miss) (p. 1-32, DS p. 26); Table 4-37 charged into `cyc` once the run leaves the p. 4-1 assumptions (a mode switch, so the goldens keep the assumption) | one golden per Table 4-37 row; twin = core per record on za with the delays on |
| C8 | EU operand and stack-cache timing | Tables 4-38/4-39 (the 4-40 duplication: charge once, a stated reading); ENTER's Q·E from the bus; CATCH refill clocks as a choice; data hazards and I/O contention as choices (the 2100 calls them unpredictable) | twin = core on za and zc per record; total clocks equal |
| C9 | MMU timing | Table 2-4 on the core: the micro-TLB, the TLB-hit update cycle, walks as bus reads with LOCK (DS p. 48) | one golden per Table 2-4 row on the MMU core; the boot sample's walks counted by the twin and by the core |
| C10 | board devices in time | the core delivers interrupts by its own clock (Quart counter, SONIC, SCSI) instead of replaying them by record number (`docs/p9boot.md`, choice 3) | the boot to rc's prompt on the core, with the twin's clock total and the core's equal, and the same console |

Ordering. C3 is the first behaviour change, and it is small. C5 comes
before C6–C9 because every later gate needs the attribution. C6 comes
before C7–C9 because A must come from the bus before anything charges
it.

### 4.1 What this does to the FPGA build (`fpga/`, ULX3S)

* **C3** adds one length check in the PDU and moves folded-branch
  resolution earlier, using the comparator EU_S1 already has. No new
  arrays. LUT change: small. Timing: the EU_S1 branch path is already the
  unfolded one.
* **C5's** clock and reason trace is simulation-only (`$display` behind a
  flag). It is not in the board build.
* **C6** is where the board diverges from the model. ULX3S memory is
  SDRAM, whose latency is not a fixed DTACK. Two ways to stay
  cycle-accurate:
  * keep program memory in BRAM, as the board build does now (one
    registered read), so that w is a counter;
  * or run the core on a clock enable: the board's clock ticks, the
    model's clock advances only when its bus would, and `cyc`/clocks are
    model clocks, not board clocks.

  The second is the general answer, and it costs one enable on every
  register. bsc's `mkGatedClock`, or a `Bool` guard on the
  orchestrator's rules, is the Bluespec way.
* **C7** needs the 3 KB prefetch buffer as BRAM. `docs/area_analysis.md`
  measures the current register array at 41,052 LUT4, which does not
  fit. That conversion is needed for the board regardless of this plan.
* **C9** needs the MMU on the board, which today runs `mkHobbitCore` with
  translation off. That adds the two 32-entry TLBs, about 2 × 32 × ~60
  FF, and they should be LUT RAM.
* The twin is host-side only. The board's UART HRI stream feeds it
  unchanged.

## 5. Corrections this plan records, not yet applied

* `bsv/HobbitBus.bsv` header: Figure A-3 does not show START in
  consecutive cycles. START is in 4, 11 and 14 (p. A-5, re-read at
  300 dpi). A = 1 is a choice.
* `docs/timing_tables.md` §7 item 4: the 2100 prints this cell 4 + Q
  (2100 p. 3-3).
* `docs/timing_tables.md` §7 item 6: the 2D in 5 + 2D is p. 1-32's "two
  double-word I/O requests" for a quad-word piece.
* `docs/timing_tables.md` §7 item 12: the data sheet has no cycle table,
  as it says. It does, however, have the demand/aggressive prefetch text
  (p. 26), the fold-host sentence (p. 26), the three-parcel-jumps-never-
  fold sentence (p. 27), the CATCH sentence (p. 31) and the TIMER
  events (pp. 32–33).
* `docs/timing.csv`: Table 2-4 (p. 2-9) is a printed timing table that
  is not yet transcribed.
* `docs/timing_tables.md` §6/§7 item 9 against `sem/hobbit_sem.py`'s
  `_conditional_jump_cycles` docstring: they read the unqualified Table
  4-35 rows differently.
