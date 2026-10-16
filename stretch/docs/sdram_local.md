# The SDRAM back end, re-assessed against the driver that exists on this machine

Status: **a correction to `stretch/docs/fpga_feasibility.md` §3.2 and a
re-derivation of §3.1 and §3.3.** Nothing here is committed to the repo and no
repo file was edited.

Every clock count below is counted from an FSM in a file on this machine, with
the file and line quoted. Every nanosecond figure is a clock count times a
stated clock period. Where a number would have to be estimated it is in §9,
"What could not be determined", instead.

**Machine load during this work: `11:04 up 28 days, 58 users, load averages:
138.00 130.71 148.18`, and `11:10 ... 107.85 122.37 139.32`.** On 16 cores that
is 7–9× oversubscribed. **No `bsc` run, no synthesis and no timing measurement
was attempted**, because nothing timed on this machine today would mean
anything. Every number here is derived from source text, which is load-immune.
That is a deliberate choice, not a gap: the quantities that decide this question
are clock counts in an FSM, and those are read, not measured.

---

## 1. What the previous assessment got wrong, and why

§3.2 of `fpga_feasibility.md` says:

> **`bluespec/Flute` has no SDRAM driver, and this was checked exhaustively
> rather than by looking in the likely place.** … So "pull in Flute's SDRAM
> driver" names a component that does not exist, and the plan needs re-pointing.

The *method* was sound — a complete 1,922-path tree listing, matched against
`sdram|sdr|dram|phy|ddr`, is a real check. The *subject* was wrong. It checked
`github.com/bluespec/Flute`. The driver is in a local fork:

```
/Users/npe/src/ulx3s-experiments/flute-ulx3s/src/Sdram_Controller.bsv   (434 lines)
```

This is the recurring failure mode worth naming, because it will recur: **an
exhaustive search of the wrong corpus returns a confident negative.** The
sentence "the authorized plan names a component that does not exist" was not
hedged, and it should have been — a negative about a *user's plan* is evidence
that the searcher and the planner are looking at different trees, and the cheap
next step was to search this filesystem. Three lines of `find ~/src -name
'*dram*'` would have turned it up.

The same root cause invalidates two more of that note's conclusions, in §10 below.

---

## 2. The controller, read in full

`mkSdram_Controller #(Integer clk_hz)`, a 19-state FSM. The states
(`Sdram_Controller.bsv:53-64`):

```
ST_PWR_WAIT, ST_PRE_ALL(_WAIT), ST_INIT_REF1(_WAIT), ST_INIT_REF2(_WAIT),
ST_MRS(_WAIT),                                            -- power-up only
ST_IDLE, ST_ACT, ST_RCD_WAIT, ST_RD, ST_RD_CAP, ST_GAP,
ST_WR, ST_WR_DATA, ST_WR_END, ST_REF, ST_REF_WAIT
```

### 2.1 What it is designed for: 25 MHz, and only 25 MHz

The file header (line 14) says the timing constants are "in 12.5 MHz clock
cycles (80 ns)". **That header is stale.** The live design point is 25 MHz:

- `src/Top.v:36` — `wire sys_clk = CLK;` with `CLK` the 25 MHz board clock on
  pin G2, and the comment at `Top.v:4`: "The board clock is 25 MHz and the
  design closes timing at 25 MHz on the 85F (26.99 MHz worst seed-1 path after
  the Stage2 BYPASS_RD fix), so the system clock is the raw board clock."
- `src/ULX3S_Top.bsv:88` — `Integer sys_clk_hz = 25_000_000;` passed at line 98
  to `mkSdram_Controller (sys_clk_hz)`.
- `test/Sdram_Tb.bsv` — `mkSdram_Controller (25_000_000)`.
- `ULX3S_Top.bsv:20` carries the same stale "divided by 2 => 12.5 MHz" comment.

So two comments in two files describe a 12.5 MHz system that no longer exists.
The number that matters is 25 MHz, and it is the number in the artifacts.

### 2.2 `clk_hz` scales exactly one thing

```bsv
Integer t_powerup = clk_hz / 5000;    // 200 us      (line 98, inside the module)

Integer t_init_gap  = 2;   Integer t_rcd       = 1;    // module-level, line 45-49
Integer t_cas_first = 3;   Integer t_rfc       = 2;
Integer refresh_div = 98;
Bit #(13) mode_reg_value = 13'h0023;                   // line 43: CL2, BL8, sequential
```

`t_powerup` is the only `clk_hz`-derived quantity in the file. **Every other
timing constant is a module-level `Integer` — a raw clock count that does not
scale.** This answers the brief's question directly: `refresh_div = 98` is a
hardcoded assumption, not a scaling rule. It is 7.84 µs at 12.5 MHz, 3.92 µs at
25 MHz (2× too frequent — wasteful, harmless), 0.98 µs at 100 MHz (8× too
frequent).

Over-refreshing is safe. **Under-waiting is not**, and three constants
under-wait as soon as the clock rises. Taking the header's own ns assertions
(line 15: "tRCD 1 (>=18 ns), CL 2, tRFC 2 (>=66 ns), tRP/tMRD 2") as the
requirement:

| constant | wait states | 25 MHz | 50 MHz | 100 MHz | 166.67 MHz | requirement |
|---|---|---|---|---|---|---|
| `t_rcd = 1` | 2 | 80 ns ✓ | 40 ns ✓ | 20 ns ~ | **12 ns ✗** | ≥ 18 ns |
| `t_rfc = 2` | 3 | 120 ns ✓ | **60 ns ✗** | **30 ns ✗** | **18 ns ✗** | ≥ 66 ns |
| `refresh_div = 98` | — | 3.92 µs ✓ | 1.96 µs ✓ | 0.98 µs ✓ | 0.59 µs ✓ | ≤ 7.8 µs (over-refresh safe) |
| CL2 in `mode_reg_value` | — | ✓ | ✓ | ✓ | **✗, needs CL3** | part rating |
| tRP after auto-precharge | 2 (implicit, §2.5) | 80 ns ✓ | 40 ns ✓ | 20 ns ~ | **12 ns ✗** | ≥ 18 ns |

So the controller is **datasheet-legal as written only at 25 MHz and below**
(and at 50 MHz after one constant change). This is not a surprise to its author:
`~/src/ulx3s-experiments/HANDOFF.md:653-656` lists as the next milestone "50 MHz
via EHXPLLL PLL + registered I/D-cache RAM responses … + **SDRAM ns-derived
timings**", and line 768 requires "SDRAM ns-timing re-derivation" before any
clock change. The project has already identified exactly this work. Nobody has
done it.

### 2.3 Clock count for a 256-bit read

Each state rule fires once per clock; each `*_WAIT` state costs `N+1` clocks
because the rule tests `rg_wait == 0` *before* exiting (`if (rg_wait == 0)
rg_state <= …; else rg_wait <= rg_wait - 1;`).

| state | clocks | source |
|---|---|---|
| `ST_IDLE` — latch request from `f_reqs` | 1 | `rl_idle`, :247 |
| `ST_ACT` — issue ACTIVATE, set `rg_wait = t_rcd = 1` | 1 | `rl_act`, :274 |
| `ST_RCD_WAIT` | `t_rcd + 1` = **2** | `rl_rcd_wait`, :284 |
| `ST_RD` — issue READ, `rg_wait = t_cas_first = 3`, `rg_beat = 0` | 1 | `rl_rd`, :294 |
| `ST_RD_CAP` — 3 wait clocks, then 8 beat-capture clocks | `3 + 8` = **11** | `rl_rd_cap`, :308 |
| `ST_GAP` — tCCD | 1 | `rl_gap_rd`, :341 |
| `ST_RD` — second burst, auto-precharge (`A10` set when `rg_phase`) | 1 | :300 |
| `ST_RD_CAP` — 3 + 8, last clock enqueues `f_rsps` | **11** | :311-322 |
| | **29 clocks** | |

The 8 capture clocks per burst: the `rg_wait == 0` branch captures beat 0 and
sets `rg_beat <= 1`; beats 1–6 are six more clocks; the `rg_beat == 7` clock
captures beat 7 and either moves to `ST_GAP` (first burst) or assembles
`v[15] = rg_dq_in` and enqueues the 256-bit response (second burst).

The FSM returns to `ST_IDLE` on the 29th clock, so **29 clocks is also the
back-to-back period**, not just the latency.

A write is **23 clocks** by the same count: `ST_WR` (1) + `ST_WR_DATA` (7) +
`ST_WR_END` (1) per burst, twice, plus IDLE/ACT/RCD_WAIT/GAP — there is no CAS
latency on the write path (`rl_wr` drives beat 0 with the WRITE command, zero
write latency, line 350).

### 2.4 There is no "row open" case. Every request pays the full ACTIVATE.

The brief asks for the cost "with the row open" versus "with a row change".
**That distinction does not exist in this controller**, and the header says so
(lines 10-12):

> A 256-bit request is two BL8 bursts (burst 0 at col, burst 1 at col+8), with
> auto-precharge, so all banks are closed between requests and refresh can be
> inserted at request boundaries.

`rl_rd` sets `A10` (`| 13'h0400`) on the second burst only, so the row stays
open *across the two bursts of one request* and is closed at the end of it. The
cost is therefore **uniformly 29 clocks for every read, regardless of
locality** — no best case to exploit, and no row-conflict penalty to fear. That
is a deliberate simplicity-for-correctness trade (it is what makes "refresh at
request boundaries" sound), and it is the single largest piece of performance
left on the table: an open-row policy could serve 32 consecutive granules from
one ACTIVATE. Noted as an improvement path, not assumed in any number below.

### 2.5 Refresh

`rl_refresh_tick` (:222) counts down from 98 **every clock, unconditionally**,
and restarts at 98 the moment it reaches 1 — whether or not a refresh was
serviced. `rl_idle` (:250) checks `rg_ref_cnt <= 1` *before* dequeuing a
request, so refresh wins at every request boundary. Cost:

`ST_REF` (1) + `ST_REF_WAIT` (`t_rfc + 1` = 3) = **4 clocks every 98**.

Two consequences, both good:

- **Steady-state overhead is 4/94 = 4.26%** of useful time, at *any* clock
  frequency *as built*, because both numbers are clock counts — amortized
  transaction period = 29 × 1.0426 = **30.2 clocks** at 25 MHz. Rescaling
  `refresh_div` to a true 7.8 µs at a higher clock (§5) drops this to ~1%: the
  refresh then costs more clocks but happens proportionally far less often.
  Either way refresh is a non-issue.
- **Jitter is bounded by one transaction.** A refresh whose counter expires
  mid-transaction waits at most 28 clocks for the next `ST_IDLE`. Since the
  counter has already restarted, refreshes stay ~98 clocks apart *on average*,
  which is what tREFI requires. The design is correct here and the comment at
  :218-220 says exactly why.

The implicit tRP: after the second burst's auto-precharge, the next ACTIVATE is
at least `ST_IDLE` (1) + `ST_ACT` (1) = 2 clocks later, plus the ~3-clock
capture-pipeline offset between the device driving a beat and the controller
seeing it. There is **no explicit tRP wait state**; the margin is incidental.
Fine at 25–50 MHz, marginal at 100, insufficient at 166.67.

### 2.6 One unresolved discrepancy, bounded

`Sdram_Controller.bsv:47` — `Integer t_cas_first = 3;   // IOB reg + BSV input
reg pipeline (sim-validated)`.

`src/Top.v:63-66` — "The BSV controller's own input register adds the second
stage; **keep t_cas_first=2** to match the original timing chain."

One of these is stale. `git log -S"t_cas_first"` shows a single commit
(`3050c27`) touching both, so history does not arbitrate. **I take 3 as
authoritative, because it is the value in the file that produced
`build/ulx3s_top.bit` (dated today, 10:00).** The effect is bounded: `±1` clock
per burst, `±2` per transaction, **29 ± 2 clocks = ±7%**. It does not change any
verdict below, and every margin stated is computed at 29.

### 2.7 What "sim-validated" does and does not cover

`test/Sdram_Tb.bsv` (284 lines) checks "initialization, read/write data
alignment, auto-precharge, refresh interaction, and byte masking, using a
64-granule scoreboard". `sim/strict_bram/sdram_model.v` is a behavioral
W9825G6KH-6. But its own header is explicit:

> **NOT modeled: refresh decay, tRCD/tRP/tRFC enforcement**, DQM on the read
> path, self-refresh, CKE power-down.

So the timing constants are validated for **FSM correctness and data integrity,
not for datasheet legality.** The simulation would pass with `t_rcd = 0`. This
matters for AGENTS.md's standard: the only *physical* validation of these
constants is the 25 MHz hardware run, and `HANDOFF.md:824` records a DMI
system-bus scan of all 2 MB of SDRAM in use on the bench. That is real and it is
strong — at 25 MHz. It says nothing about 50, 100 or 166 MHz.

### 2.8 Byte-enables: a 64-bit store costs no read-modify-write

`rl_wr`/`rl_wr_data` derive `rg_dqm` per beat from `rg_req_byteen`
(32 bits, one per byte of the 256-bit granule, lines 367 and 383). A single
64-bit Stretch word is written by setting 8 of the 32 byteen bits: **a 23-clock
granule write, no read-modify-write, no granule fetch first.** This is
load-bearing for §4 and §5 — it is why the write path is simple and why a
granule cache can write through in place. It also means stores never need a read
before them, which the non-bursting alternative in §6 cannot say.

---

## 3. The Stretch side, counted from the model

### 3.1 The deadline is 1,200 ns, not 1,500 ns

`StretchMemory.bsv`'s `mkMemoryUnit` (`rule tick`, :125-141):

```bsv
busy    <= fromInteger(memCycleClocks);   // 7
readDue <= wr ? 0 : fromInteger(memReadClocks);   // 5
...
if (readDue == 1) dataOut <= tagged Valid raw;
```

A request at model clock 0 sets `readDue = 5`. Clocks 1–4 decrement it to 1. At
clock 5, `readDue == 1`, so `dataOut <= tagged Valid raw` — **sampling `raw` as
it stood at the start of clock 5, i.e. whatever was written at the end of clock
4.**

So the data must be in the holding register **4 model clocks = 1,200 ns** after
the request, not 5 / 1,500 ns. The previous note used 1,500. **The model's own
counter gives 1,200, and that 20% is spent before any analysis starts.**

### 3.2 The required rate is one word per 400 ns, not 350 ns

Also from `rule tick`: `busy` is set to 7 on the request clock and decremented
**only in the `else` branch** (no request). Clock 0 sets `busy = 7`; clocks 1–7
walk it 7→1; at clock 8 `busy == 0` and `free()` is true. **The unit's period is
8 model clocks = 2,400 ns, not 7 / 2,100 ns.** The model is off by one against
its own header's "busy for 7 clocks per access (2.1 µs)" — a pre-existing,
unrelated discrepancy, noted in §9 as something for the owner, not something to
fix here.

Six units at one request per 8 clocks = 6 per 2,400 ns = **one per 400 ns**.

Confirmed on the other side: `StretchStorage.bsv:332-363`, `rule memCtl`,
declares `Bool busUsed = False` *local to one rule execution* and every
`mbcu.put` call site is guarded by `!busUsed`. So **at most one `mbcu.put` per
model clock** — one request per 300 ns. The sustained constraint is the tighter
of the two: `min(1 per 300 ns, 6 per 2,400 ns)` = **one 64-bit word per 400 ns**.

The brief's 350 ns is the figure from `memCycleClocks = 7`. 400 ns is what the
counter does. Both are given in the tables; the margins are computed against
both.

### 3.3 Where "six at once" comes from and why it is not the constraint

`mkMBCU`'s `rule route` (:175) collects *every* unit presenting data this clock
into its tag's slot, so six responses can land in one model clock. But they
cannot have been *requested* in one model clock, because `putW` is a single
`RWire`. Six requests take at least six model clocks (1,800 ns) to arrive. Any
queueing analysis must use that arrival schedule, or it overstates the burst by
a factor of six. The previous note got this right and it is the most important
thing in its §3.1.

---

## 4. The clock-domain crossing is half the latency budget

This is the term the previous note omitted, and it decides the answer.

A generic `SyncFIFOIfc` response crossing from the SDRAM domain to the 3.333 MHz
core domain costs about **two destination-clock edges = 600 ns** of the 1,200 ns
budget. The request crossing the other way costs two *fast* clock edges, which
is negligible. So with independent clocks the SDRAM gets **560 ns**, and a
single 29-clock transaction plus a worst-case refresh (33 clocks) needs 660 ns
at 50 MHz. **50 MHz fails on the crossing alone, before any queueing.**

**The fix is a design requirement, and it should be written into the plan:
derive the core clock from the SDRAM clock by integer division in the same PLL,
and cross with a clock-enable strobe rather than a metastability synchronizer.**
One machine cycle is 300 ns, so:

| SDRAM clock | ÷ | core clock | exactly 300 ns? |
|---|---|---|---|
| 25 MHz | 7.5 | — | **no** |
| 50 MHz | 15 | 3.3333 MHz | **yes** |
| 100 MHz | 30 | 3.3333 MHz | **yes** |
| 166.67 MHz | 50 | 3.3333 MHz | **yes** |

Bluespec's `Clocks` package supplies this: `mkClockDivider(N)` yields the
divided clock plus a `clockReady` boolean, and a fast→slow data crossing
gated by `clockReady` is the documented safe pattern — the clocks are
phase-locked by construction, so there is no metastability to synchronize. Cost:
one fast clock in each direction, **40 ns at 50 MHz, 20 ns at 100 MHz.**

Two things follow, and the second is the best news in this document:

1. **25 MHz is off the table for a second, independent reason.** 25 ÷ 7.5 is not
   an integer, so a 25 MHz SDRAM clock forces a genuine asynchronous crossing
   and its 600 ns. It already failed on throughput (§5); this is why no amount
   of cleverness rescues it.
2. **The core clock becomes an enable the interposer can withhold.** See §7 —
   this converts the entire latency question from a correctness problem into a
   performance problem.

Budget after the crossing: **1,200 ns − 2 SDRAM clocks** ≈ 1,160 ns at 50 MHz,
1,180 ns at 100 MHz.

---

## 5. The corrected arithmetic

Two bounds, because the burst's value depends entirely on whether the four words
of a granule are wanted. §6 shows that for the access patterns this machine
actually generates they are, but that is an argument from expected behaviour, so
both bounds are given and the recommendation rests on the pessimistic one.

- **Reuse bound** (all four words of each granule are used): 4 Stretch words per
  transaction.
- **Scattered bound** (one useful word per transaction): 1 word per transaction.
  This is the previous note's implicit assumption, and it is why its conclusion
  was what it was.

Constants are re-derived to datasheet legality per §2.2 at each clock, which
*lengthens* the transaction — this is counted, not waved away. `refresh_div` is
rescaled to a true 7.8 µs at each clock (a one-constant change, strictly
beneficial: it is the difference between 4.3% and 1.0% refresh overhead):

| SDRAM clock | constant changes needed | read | write | refresh | `refresh_div` | refresh overhead |
|---|---|---|---|---|---|---|
| 25 MHz | none | 29 clk | 23 clk | 4 clk | 98 (as built) | 4.3% |
| 50 MHz | `t_rfc` 2→3 | 29 clk | 23 clk | 5 clk | 390 | 1.3% |
| 100 MHz | `t_rcd` 1→2, `t_rfc` 2→6, explicit tRP state (+2) | 32 clk | 26 clk | 8 clk | 780 | 1.0% |
| 166.67 MHz | `t_rcd`→3, `t_rfc`→10, CL2→CL3 in `mode_reg_value`, `t_cas_first` 3→4, tRP state | 36 clk | 28 clk | 12 clk | 1300 | 0.9% |

### 5.1 Throughput — required: one word per 400 ns (brief's figure: 350 ns)

| SDRAM clock | per-word, reuse bound | margin (400 / 350) | per-word, scattered bound | margin (400 / 350) |
|---|---|---|---|---|
| 12.5 MHz | 605 ns | **0.66× / 0.58× ✗** | 2,419 ns | **0.17× / 0.14× ✗** |
| 25 MHz | 302 ns | 1.32× / 1.16× ~ | 1,209 ns | **0.33× / 0.29× ✗** |
| 50 MHz | 147 ns | **2.7× / 2.4× ✓** | 588 ns | **0.68× / 0.60× ✗** |
| 100 MHz | 81 ns | **5.0× / 4.3× ✓** | 323 ns | 1.24× / 1.08× ~ |
| 166.67 MHz | 55 ns | **7.3× / 6.4× ✓** | 218 ns | **1.83× / 1.61× ✓** |

### 5.2 Latency — budget: 1,200 ns minus the crossing (§4)

Budget is 1,200 ns less the crossing cost: **600 ns** at 12.5/25 MHz (no integer
divide to 300 ns, so a genuine asynchronous crossing), **2 SDRAM clocks** at
50/100/166.67 MHz (phase-locked divider).

Worst case for the reuse bound is one transaction plus a refresh. Worst case for
the scattered bound is the sixth of six requests arriving 300 ns apart:
`finish_k = max(arrival_k, finish_{k-1}) + S`, so `lat_6 = 6S − 1,500 ns`, plus
one refresh, plus **one** store ahead of it (stores win in `memCtl`, §3.2 /
§2.8).

Why exactly one store and not four — `f_reqs` is `mkSizedFIFOF(4)` and nothing in
the controller bounds write-ahead: because `memCtl` issues a read only under
`!busUsed && !issued && !storeQ.notEmpty` (`StretchStorage.bsv:359`), so a read
is never issued while any store is queued. Stores and reads therefore cannot
deeply interleave at the controller's input. **This is a constraint the scheduler
must preserve, listed alongside §7.2's unconditional-drain rule: write-ahead
depth into `f_reqs` must be bounded at 1 whenever any read slot is pending.**
Without that bound the one-write term here is an assumption rather than a bound,
and four queued writes would add 3 × 260 ns at 100 MHz — enough to break the
scattered-bound latency margin.

| SDRAM clock | budget | reuse bound | scattered bound | verdict |
|---|---|---|---|---|
| 12.5 MHz | 600 ns | 2,640 ns **✗** | 14,580 ns **✗** | fails both |
| 25 MHz | 600 ns | 1,320 ns **✗** | 6,540 ns **✗** | fails both |
| 50 MHz | 1,160 ns | 680 ns ✓ **1.7×** | 2,540 ns **✗** | reuse only |
| 100 MHz | 1,180 ns | 400 ns ✓ **3.0×** | 760 ns ✓ **1.55×** | **passes both** |
| 166.67 MHz | 1,188 ns | 288 ns ✓ **4.1×** | 456 ns ✓ **2.6×** | **passes both** |

### 5.3 The verdict

- **12.5 MHz and 25 MHz: not feasible.** 25 MHz — the clock at which this
  controller is hardware-validated — fails throughput by 3× on the scattered
  bound and fails latency on *both* bounds, and cannot divide to 300 ns. **The
  one configuration we have physical evidence for is the one that does not
  work.** That is the most uncomfortable finding here and it should not be
  buried: going to SDRAM means leaving the validated operating point.
- **50 MHz: feasible on the reuse bound (2.7× throughput, 1.7× latency), not on
  the scattered bound** (0.68× throughput, 2,540 ns against a 1,160 ns budget).
  One constant change (`t_rfc` 2→3). This is a real improvement on the previous
  note, which ruled 50 MHz out entirely — the bursting is worth 4× and it moves
  50 MHz from "not sustainable" to "sustainable if the granules are reused".
- **100 MHz: feasible on both bounds** — 5.0×/1.24× throughput, 3.0×/1.55×
  latency. Three constant changes plus an explicit tRP state. The scattered-bound
  margins are **thin, and should be called thin**: 1.24× throughput means a
  sustained fully-scattered read stream has 24% headroom and nothing more. But
  they are margins on a *bound*, not on an expectation. **This is the lowest
  clock at which the window is met for any access pattern with no stall at
  all.**
- **166.67 MHz: comfortable on both** (7.3×/1.83× throughput, 4.1×/2.6× latency),
  at the cost of a CL3 mode-register change, five constant changes, and the
  least-validated electrical margin. This is where to go if 100 MHz's 1.24×
  turns out to be uncomfortable in practice.

**Recommendation: 100 MHz, ÷30 to a 3.3333 MHz core clock from one `EHXPLLL`.**

And the recommendation should be stated in the right currency, because §7.3's
stall mechanism changes what "fails" means. **Once the core clock can be gated, a
missed window is not incorrectness — it is wall-clock dilation, counted by
`stall_cycles`.** So:

| SDRAM clock | correctness | worst-case wall-clock dilation |
|---|---|---|
| 50 MHz | **correct** | ~1.0× on the reuse bound; **1.47×** (588/400) on a sustained fully-scattered read stream |
| 100 MHz | **correct** | **1.0× — zero dilation on any access pattern** |
| 166.67 MHz | **correct** | 1.0×, with 1.83× spare |

That is a stronger claim than "provable versus not", and it is what §7.3 earns:
**50 MHz is not wrong, it is slow in a measured way.** Choose 100 MHz because it
is the cheapest clock with *zero* dilation on every access pattern, so the
machine runs at literal 7030 speed unconditionally and `stall_cycles == 0` is a
regression assertion rather than a budget. Choose 50 MHz if the PLL or the
timing-closure risk of (b) in §7.1 makes it attractive, accept up to 1.47×
dilation in the worst case, and let the counter report it. Both are defensible;
only 25 MHz is not.

Note what this does *not* change: the previous note's **"a 25 MHz core clock is
not feasible with this memory system"** stands, and is now overdetermined. At a
25 MHz *core* clock the budget is 160 ns and the required rate one word per
48 ns; the reuse bound at 166.67 MHz is 59 ns per word. Still no.

---

## 6. Does the 256-bit granularity interact with the interleave?

**It is a gift, and a sharper one than "four words happen to arrive together".
Under the right address map the granule number *is* the unit index, and the
interleave is precisely the pattern that makes the burst pay.**

From `StretchMemory.bsv:68-79`:

```bsv
function Bit#(3) unitOf(WordAddr a);
  if (a < 65536) return {1'b0, a[1:0]};        // 4-way
  else return {2'b10, a[0]};                   // 2-way
endfunction
function UnitIndex indexOf(WordAddr a);
  if (a < 65536) return a[15:2];
  else begin Bit#(18) rel = a - 65536; return rel[14:1]; end
endfunction
```

Lay SDRAM out so that **one 256-bit granule holds four consecutive Stretch word
addresses**: granule `g` = words `4g … 4g+3`. Then:

**4-way region (words 0–65,535, units 0–3).** Granule `g` holds words `4g`,
`4g+1`, `4g+2`, `4g+3`. Their units are `a[1:0]` = 0, 1, 2, 3 — all four, each
once. Their indices are `a[15:2]` = `g`, `g`, `g`, `g` — **all the same, and
equal to `g`.** So:

> **Granule `g` is exactly {unit 0, unit 1, unit 2, unit 3} at index `g`.**
> One 256-bit read answers all four units' index-`g` request simultaneously.
> The reverse map is `g = index`, slot = unit. No arithmetic at all.

**2-way region (words 65,536–98,303, units 4–5).** Granule `g` holds words
`4g…4g+3`; units are `4 + a[0]` = 4, 5, 4, 5 and indices
`rel[14:1]` = `2g−32768` twice then `2g−32767` twice. So:

> **Granule `g` is {unit 4, unit 5} × {index `2g−32768`, index `2g−32767`}** —
> both units, at the current index *and the next one*. The reverse map is
> `g = 16384 + (index >> 1)`, slot = `{index[0], unit[0]}`.

Both maps are pure bit-slicing plus one constant. **The interposer's address
arithmetic is a wiring change, not a datapath.**

**Why this is a gift rather than a coincidence.** Buchholz's reason for the
interleave, quoted in `StretchMemory.bsv:9-12`, is that "four consecutive word
addresses lie in four different memory units … to achieve a high degree of
overlap". The *purpose* of the interleave is that a sequential access stream
spreads across units. A sequential stream is exactly what fills a granule. So
the two mechanisms are aligned by construction: **the access pattern the
interleave exists to accelerate is the access pattern that makes a 256-bit burst
fully useful.** The instruction fetch walking consecutive words, and the
four-level look-ahead prefetching consecutive operands, both hit units 0,1,2,3 at
the same index — one granule.

**The naive map is the problem, and it is the one the previous note proposed.**
§3.3 of `fpga_feasibility.md` says "The address map is trivial: `unit × 16384 +
index` words". Under that map a 256-bit granule holds four consecutive *indices
within one unit*, which is Stretch words `16j+u`, `16j+4+u`, `16j+8+u`,
`16j+12+u` — four words **stride 4 apart in one unit**. A sequential program
touches one of them and discards three. **That map throws the entire benefit of
the burst away and puts you on the scattered bound**, where (§5) 50 MHz fails and
100 MHz is marginal. The granularity question therefore has a real answer with a
real consequence: **interleave-aligned map → reuse bound; unit-major map →
scattered bound.** Same hardware, 4× apart.

**What converts the gift into something closer to a guarantee: a granule cache.**
The reuse bound as stated requires the four units' index-`g` requests to be
*simultaneous*. They are not quite — they arrive one model clock apart (§3.3),
and different return tags walk different streams (operand, 1Y, 2Y, four
look-ahead levels — seven channels, `NumTags = 7`). A small granule cache fixes
both:

- **8 entries × 256 bits = 2 Kbit** — one `DP16KD`, or plain registers.
- Each entry serves four consecutive addresses of one stream, so **one fetch per
  four accesses per stream** for any set of ≤ 8 sequential streams. Seven tags
  plus a store stream is eight.
- A store writes through in place (byteen, §2.8) and needs no invalidate-and-
  refetch — the 64-bit word is written to SDRAM *and* patched into the cached
  granule, which is exact because the granule is a cache of words, not of bytes.
- Truly random access still falls to the scattered bound. The cache raises the
  *expected* case; it does not raise the *bound*. Hence §5's recommendation
  rests on 100 MHz, where the bound itself passes.

**One residual hazard worth stating.** Four units sharing one granule means a
fetch answers four `mkMemoryUnit` instances from one transaction. Those units'
`readDue` counters are independent and were started on different model clocks, so
the granule must be *held* until the latest of the four deadlines, and each
unit's slot delivered on its own clock. That is a 4-bit pending mask per cache
entry, not a new mechanism — but it is the reason the response path needs
storage per unit and not a single shared register.

---

## 7. The interposer, and what happens when the promise is broken

Building on §3.3 of the previous note, which is sound and which I keep.

### 7.1 Shape

**Keep `mkMemoryUnit` as it is, minus the `BRAM1Port`.** It already models an
independently busy unit — `busy`, `readDue`, `tagReg`, `free()`, `dataReady()` —
and six instances keep six independent busy counters, so neither `mkMBCU`'s
priority vector nor `mkStretchStorage`'s seven channels change. The `drain` rule
(`raw <= v` from the BRAM response) is the single seam: `raw` is instead loaded
from the interposer's per-unit response slot.

**The shared scheduler, in the SDRAM clock domain:**

- **Six request slots**, one per unit, each holding `{valid, index, write, data,
  granule, slot}`. Written from the core domain on the clock the unit's
  `request` method fires; the unit's own `busy` counter already guarantees at
  most one outstanding request per slot, so there is nothing to size.
- **An 8-entry granule cache** (§6), tag = granule number, each entry with a
  4-bit mask of units awaiting a slot of it.
- **A round-robin arbiter** over the six slots, choosing the next granule to
  fetch and coalescing every pending slot that maps to the same granule. Writes
  first, matching `memCtl`'s store priority (§3.2); a write is 23 clocks and
  needs no fetch (§2.8).
- **Six response registers**, one per unit, each `{valid, Word64}`, cleared when
  the unit's request is taken and set when its slot arrives.
- **One `mkSdram_Controller` instance** connected by `mkConnection` to
  `mem_server`, which is a `MemoryServer#(addr, 256)` from the standard `Memory`
  package — a `Get`/`Put` pair. No adapter is needed on that side at all.

**The crossing**, per §4: `mkClockDivider(30)` from the 100 MHz PLL output gives
the 3.3333 MHz core clock and a `clockReady` strobe. Requests and responses cross
as plain registers gated by `clockReady`. Phase-locked by construction, so no
synchronizer and no 600 ns.

**One correction to make before building this, because it is easy to get wrong:
`clockReady` is an *output* of `ClockDividerIfc`.** The divider free-runs and its
edge cannot be withheld, so §7.3's stall is **not** implementable by
"not asserting `clockReady`". The construct that does implement it is
**`mkGatedClock`**, with the gate driven by `clockReady && all_responses_ready`
and the core instantiated `clocked_by` the gated clock; bsc emits a
`CLK_GATE_*` port for it, as `flute-ulx3s/src/Top.v` already demonstrates by
wiring `.CLK_GATE_jtag_tclk_out()`. Naming it exposes a fork that should be
decided deliberately rather than assumed:

| | **(a) divided 3.33 MHz core clock, gated** | **(b) single 100 MHz domain, core on a 1-in-30 clock-enable** |
|---|---|---|
| CDC | 2 SDRAM clocks (§4) | **none at all** — §4's 20 ns disappears |
| stall mechanism | gate a *derived* clock → a real ECP5 clock gate (`DCCA`) | **free** — withhold the enable; `synth_ecp5` maps it to the CE pin every `TRELLIS_FF` already has |
| timing closure | trivial: 300 ns per path, the previous note's argument survives intact | **every combinational path in `mkStretchCore` must close at 10 ns** |
| risk | the gated derived clock is synthesizable but unverified here | `Top.v:4` records the Flute SoC on this same 85F plateauing near 28 MHz — weak but real evidence against a large BSV design closing at 100 MHz on this part |

**(b) is the cheaper and cleaner mechanism and the one whose feasibility is
least established.** (a) is the safe default and keeps the timing-closure
argument that made the 3.333 MHz core clock attractive in the first place.
Recommend starting with (a); (b) is worth a single synthesis experiment once the
machine is quiet, because if the core closes at 100 MHz it removes the clock
domain crossing from the design entirely. Either way this is in §10 as
unmeasured.

### 7.2 A hard constraint the controller imposes: drain `f_rsps` unconditionally

`f_rsps` is `mkSizedFIFOF(2)` (line 130) and `rl_rd_cap` enqueues into it. **If
it is full, `rl_rd_cap` cannot fire — and the SDRAM device free-runs, so burst
beats are lost, not delayed.** Flute never reaches this: one outstanding request,
drained immediately. A six-unit interposer can.

So: **the scheduler must dequeue `f_rsps` into its own storage on every clock a
response is present, unconditionally, never gated on a consumer being ready.**
That is a structural requirement on the scheduler, not a tuning choice, and it is
the kind of thing that works in simulation for a long time before it doesn't.

### 7.3 When the promise is broken

There are two distinct failures and they need different answers. The previous
note's instinct — "a visible overrun counter, not a silent stall … a status bit a
test can read, in the spirit of the model's 'fail loud, never silently'
convention" — is right, and §4's clock-enable crossing makes it concrete and
much better than a counter alone.

**Failure 1: the response misses the 1,200 ns window.** As the model stands this
is *silent data corruption*, not a stall: at model clock 5, `dataOut <= tagged
Valid raw` latches whatever `raw` holds, which is the previous read's value. No
rule is blocked, no condition is false, the program continues with a wrong word.
This is the worst possible failure mode for this project and it must be made
impossible by construction, not detected after the fact.

**It can be, and cheaply: withhold the core clock.** Because the core clock is
derived from the SDRAM clock by integer division (§4), the scheduler can gate it
— `mkGatedClock` with the gate `clockReady && all_responses_ready`, per §7.1's
correction — so that no core clock edge occurs on a cycle when any unit with
`readDue == 1` has an invalid response register. Consequences:

- **Correctness is absolute.** The core cannot advance into the clock that would
  latch a stale `raw`. There is no window to miss, because the window stretches.
- **Cycle accuracy is preserved exactly where it matters.** Every `CYCLES<=`
  bound in the regression suite counts *model clocks*, and model clocks are
  enable pulses. Stalling inserts no model clock. The suite's bounds stay
  literally true. Only wall-clock time dilates.
- **The dilation is countable.** `rg_stall_cycles` — one counter of withheld
  enables — is the exact number of machine cycles of wall-clock time the SDRAM
  cost beyond the model. A test asserts it is zero; a benchmark reads it as a
  figure of merit. This is strictly more informative than an overrun bit,
  because zero means "the timing model was literally true on this run" and
  nonzero means "it was true in model clocks and dilated by exactly N".
- **It replaces a proof with a measurement, in the safe direction.** §5's latency
  analysis stops being a correctness argument and becomes a performance
  prediction, checkable against the counter. That is the right way round: the
  thing that would otherwise need proving before first silicon is instead
  self-reporting.

One cost, stated plainly: a global enable stall is global. One late unit stalls
all six and the E-box. That is *less* accurate than per-unit backpressure would
be, but per-unit backpressure means changing `mkMemoryUnit`'s `busy`/`readDue`
contract, which is the thing the brief and the previous note both want kept
intact. The counter makes the inaccuracy visible and bounded, which is the trade
the project's conventions prefer.

**Failure 2: scheduler storage full when a response arrives** (§7.2), or a
request arriving for a slot already valid. These are *internal invariant
violations* — they mean the scheduler is miscounting, not that the SDRAM is slow.
They get their own sticky status bit each, set and never cleared, readable
alongside the stall counter, plus `$display` under a simulation guard. Distinct
from failure 1 because the response is "there is a bug in the interposer", not
"memory was slow". Conflating them into one counter would hide a logic error
behind a performance number.

**Three status outputs, then**, all readable through the UART observer path the
previous note's §3.5 describes:

| output | meaning | test assertion |
|---|---|---|
| `stall_cycles` (32-bit) | machine cycles of wall-clock dilation | `== 0` ideally; any value is correct |
| `rsp_overrun` (sticky bit) | `f_rsps` or scheduler storage was full | `== 0`, always; nonzero is a bug |
| `slot_conflict` (sticky bit) | request to an already-valid slot | `== 0`, always; nonzero is a bug |

### 7.4 Capacity and address map

98,304 words × 8 bytes = 786,432 bytes = **24,576 granules of 32 bytes**, i.e.
2.3% of the 32 MB part. Granule numbers 0–24,575 need 15 bits; the controller
decodes `bank = r[6:5]`, `row = r[19:7]`, `col base = {r[4:0], 4'b0}`
(lines 88-92), so the installed store occupies rows 0–191 across all four banks,
well inside the 20 bits used and the 13-bit row field. The map is §6's: `g =
index` in the 4-way region, `g = 16384 + (index >> 1)` in the 2-way region.

---

## 8. The two controllers, side by side

| | **local `flute-ulx3s/src/Sdram_Controller.bsv`** | **`sangwoojun/ulx3s_bsv/src/Sdram.bsv`** |
|---|---|---|
| lines | 434 | 313 |
| transfer unit | **256 bits** — two BL8 bursts | **16 bits** — one half-word per `req` |
| bursting | **yes**, BL8 ×2, mode register `13'h0023` | **no** |
| clocks per 64-bit word | 29/4 = **7.25** (reuse) … 29 (scattered) | **~27** with the row open, ~32 on conflict |
| row policy | auto-precharge every request; **no open-row case** (§2.4) | **open-row tracking per bank** (`open_bank`, `open_rows`) |
| interface | **`MemoryServer#(addr, 256)`** from the standard `Memory` package — a `Get`/`Put` pair, `mkConnection`-able as-is | bare methods `req(addr, data, write)` / `readResp()` — needs a wrapper |
| byte masking | **32-bit byteen → per-beat DQM**; 64-bit store needs no RMW (§2.8) | 2-bit `sdram_dqm` exposed; per-request only |
| clock domains | **single-clock**; no `Clock` parameter. CDC is the integrator's job | takes `Clock sdram_clk`; **CDC already built** |
| timing constants | hardcoded clock counts, legal at ≤ 25 MHz; 50/100/166 need re-derivation (§2.2) | `rf_cycles = clock_mhz * 78 / 10` — **refresh scales**; `delay_tRP/tRCD/tRC/CL` hardcoded |
| clock-phase work | done — `ODDRX1F` forwarding + `useioff` IOB capture in `Top.v`, with the byte-skew bug found and fixed | **not done** — line 8: `// TODO clock either needs to be shifted, or commands need to be held for longer` |
| validation | **running on a ULX3S-85F at 25 MHz**, booting an RV32IMAC SoC; 2 MB DMI scan (`HANDOFF.md:824`); bitstream dated today; `Sdram_Tb.bsv` + behavioral W9825G6KH model | no evidence of a hardware run found |
| pin interface | 13 `a` / 2 `ba` / 2 `dqm` / 16 `dq_out` + `dq_in` + `dq_oe` (split, no `Inout`) | 13 / 2 / 2 / `Inout#(Bit#(16))` |
| comes with | `constraints/ulx3s_85f.lpf`, `src/Top.v`, a `yosys`/`nextpnr`/`ecppack` Makefile, `openFPGALoader` targets, `scripts/loader.py`, a UART-DMI debug bridge | `PLL.bsv`, `Uart.bsv`, `Top.bsv`, `ulx3s_bsv.lpf`, `Mult18x18D.bsv` |
| glue to `mkMemoryUnit` | 6 slots + 8-entry granule cache + arbiter + CDC + bit-slice address map (§7.1) | 6 slots + arbiter + 64↔4×16 packer; CDC free; no granule logic |

### Which, and why

**Recommendation: the local Flute controller.** Four reasons, in descending
weight:

1. **It is the only one with physical evidence behind it.** It is on a bench,
   today, serving a CPU out of this exact chip on this exact board, with the
   hard part already debugged — `Top.v:58-66` records that fabric routing skew
   between `DQ[15:8]` and `DQ[7:0]` clocked one byte a cycle late on some
   placements, read back as "byte1↔byte3 swaps within each 32-bit word", and
   fixed it by forcing the pad register with `(* useioff = 1 *)`. That is a bug
   nobody finds in simulation, it would have cost days, and it is the exact class
   of problem `sangwoojun`'s line-8 TODO is still carrying. The previous note
   called that TODO "an honest caveat"; it is the whole risk.
2. **The interface is already the right shape.** `MemoryServer#(addr, 256)` is a
   standard `ClientServer` pair; the scheduler connects with `mkConnection` and
   no adapter. `sangwoojun`'s bare `req`/`readResp` needs a wrapper written and
   tested first.
3. **It bursts, and §6 shows the interleave hands it four useful words per
   transaction.** That is the 4× that moves 50 MHz from impossible to
   conditional and gives 100 MHz a 5.0× throughput margin instead of 1.24×.
4. **The whole board flow comes with it** — `.lpf`, `Top.v`, synth/pnr/pack
   Makefile rules, a programmer target, a host loader, and a UART-DMI bridge that
   is a ready-made answer to the previous note's §3.5 readback problem. The
   previous note identified `ulx3s_bsv` as "the whole bring-up kit … the single
   highest-leverage thing to read before starting". **That sentence is now wrong
   for a better reason than it was wrong before: a more complete kit, already
   working, is on this filesystem.**

**Judged on the merits, as the brief asks: `sangwoojun` does not win on
integration.** Its two genuine advantages are real and worth taking:

- **Its CDC is built and the Flute one's is not.** But §4 argues the interposer
  should *not* use a generic asynchronous crossing anyway — the phase-locked
  divider is both cheaper in latency (40 ns vs 600 ns) and the mechanism that
  makes §7.3's stall possible. `sangwoojun`'s built-in CDC solves a problem the
  right design does not have.
- **Its refresh interval scales with `clock_mhz`** where Flute's `refresh_div` is
  hardcoded — a genuinely better pattern, and the one to copy when re-deriving
  Flute's constants for 100 MHz (§2.2). Its other delays are hardcoded too, so
  the advantage is partial.

Its **open-row tracking** is architecturally nicer than Flute's blanket
auto-precharge and is the clearest thing to borrow *later* — but it cannot
overcome not bursting. Per 64-bit word, open-row `sangwoojun` costs ~24–27 clocks
against Flute's 7.25 in the reuse case: **Flute is 3.3–3.7× ahead even where
`sangwoojun` is at its best.**

Worth stating against my own recommendation: **`sangwoojun` would win if the
access pattern were truly random and the clock had to stay at 25 MHz.** At that
clock Flute fails everything (§5.3) while open-row `sangwoojun` at 25 MHz costs
24 clocks = 960 ns per word — which also fails the 400 ns requirement. So the
tie-break never arises: neither controller works at 25 MHz, and above it Flute
wins on every axis that is measured here.

---

## 9. Two more corrections from the same root cause

Both are in scope because they share the cause — assessed against upstream
rather than this filesystem — and both remove items from the previous note's
critical path. Kept short.

**`nextpnr-ecp5` is not "non-functional, unrecoverable".** `fpga_feasibility.md`
§2.6 and effort item 2 ("Revive `nextpnr-ecp5`: … 0.5–2 days, yes — nothing
routes without it") are true of `/usr/local/bin/nextpnr-ecp5`, which I confirmed
still fails on a missing `libboost_python38-mt.dylib`. But a working one is built
on this machine:

```
/Users/npe/src/ulx3s-experiments/bluespec-ulx3s/toolchain/nextpnr-build/nextpnr-ecp5
  → "nextpnr-ecp5" -- Next Generation Place and Route (Version eb4f15c)
/Users/npe/src/ulx3s-experiments/bluespec-ulx3s/toolchain/prjtrellis-install/bin/ecppack
  → Project Trellis ecppack Version 65fe191
```

and `flute-ulx3s/Makefile:13-14` already points at both. **Effort item 2 is 0
days, not 0.5–2, and it is not on the critical path.** Proof it runs end to end:
`flute-ulx3s/build/ulx3s_top.bit` is 1,107,757 bytes dated **today, 10:00**, from
an 89 MB `ulx3s_top.json`.

**"The whole FPGA flow is new work" is wrong** (§3.5: "There is no `.lpf`, no
board top-level, no PLL, and no `yosys`/`nextpnr`/`ecppack` rule anywhere"). True
of `stretch/`; false of this machine. `flute-ulx3s` has
`constraints/ulx3s_85f.lpf` with every SDRAM pin located (`sdram_clk` F19,
`sdram_cke` F20, `sdram_a[0..12]` M20…G19, `sdram_dq[0..15]` J16…, matching
`Top.v`'s comments and the board), `src/Top.v` as the board wrapper, and Makefile
targets `compile → synth → bitstream → program → run`. **The flow is a template
to adapt, not a thing to write.** What is genuinely missing is the `EHXPLLL`
instance — `Top.v` uses the raw 25 MHz clock and needs a PLL for §4's ÷30 — and
`sangwoojun/ulx3s_bsv/src/PLL.bsv` remains the right thing to borrow for exactly
that one piece.

---

## 10. What could not be determined

1. **The W9825G6KH-6 datasheet is not on this machine.** Every ns requirement
   used above (tRCD ≥ 18, tRFC ≥ 66, tRP/tMRD, CL2 vs CL3 ratings) is **the
   controller header's own assertion at `Sdram_Controller.bsv:15`, not a
   datasheet citation.** All the 50/100/166.67 MHz constants in §5 are
   re-derivations from that assertion and are **unverified against the part**.
   Before any clock change, get the datasheet and re-derive; this is precisely
   the "SDRAM ns-timing re-derivation" `HANDOFF.md:768` gates on.
2. **Nothing above 25 MHz is validated for this driver, electrically or
   functionally.** The 25 MHz bench run is the only physical evidence. §5
   recommends 100 MHz on arithmetic alone.
3. **`ulx3s-bitstreams/memtest-32MB-190MHz-85f.bit` is evidence about the board
   and the chip, not about this driver.** It shows the physical SDRAM, the PCB
   routing and the ECP5 I/O can run a *different* (EMARD) controller at 190 MHz,
   which makes 100 MHz electrically plausible. It is not a measurement of
   `Sdram_Controller.bsv` and must not be quoted as one.
4. **`t_cas_first`: 3 (BSV) vs 2 (`Top.v` comment)** — §2.6. Unresolved; bounded
   at ±2 clocks per transaction (±7%); every margin above computed at 29.
5. **Granule-cache hit rate is unknown**, so §6's reuse bound is an expectation,
   not a bound. It is measurable cheaply: instrument `mkMBCU`'s `route` in
   Bluesim over the existing 389-section corpus and histogram
   `(unit, index) → granule` reuse within a 4-model-clock window. **That one
   measurement decides 50 MHz vs 100 MHz** and needs no hardware. It is the
   highest-value next step and it was not run here (load 138).
6. **The scheduler's own Fmax is unmeasured.** Under §7.1 option (a) it is the
   only new logic on a 100 MHz path — at a 3.3333 MHz core clock nothing in
   `mkStretchCore` is. `Top.v:4`'s near-28 MHz plateau is about Flute's
   pipeline, not about a six-slot arbiter and an 8-entry cache, so it is not
   evidence either way.
7. **The stall mechanism of §7.3 requires `mkGatedClock` on the core domain, and
   neither of its two forms is measured** (§7.1): whether a gated *derived*
   clock closes on ECP5 through a `DCCA` cell (option a), or whether
   `mkStretchCore` closes at 10 ns so the core can run as a clock-enable in a
   single 100 MHz domain with no CDC at all (option b). Option (b) is the better
   design if it closes, and `Top.v:4`'s record of the Flute SoC plateauing near
   28 MHz on this part is the only evidence either way — weak, and about a
   different design. **One synthesis run on a quiet machine decides it**, and it
   is the second-highest-value measurement after item 5.
8. **`mkMemoryUnit`'s `busy` period is 8 model clocks, not the 7 its header
   claims** (§3.2) — an off-by-one in the model, pre-existing and unrelated to
   SDRAM. It makes the required rate 400 ns rather than 350 ns, i.e. it *helps*.
   Flagged for the owner; not touched.
9. **No `bsc` elaboration, synthesis or simulation was run**, by choice, at load
   138/107 (§0). Everything here is source-derived. The three things that would
   most change these numbers — item 5's reuse histogram, item 1's datasheet, and
   a 50/100 MHz bench run — all need a quiet machine or a bench.

---

## 11. Summary

- **The local driver fits.** It bursts BL8 ×2 for 256 bits per transaction =
  four Stretch words, at a uniform 29 clocks with no row-conflict case, ~1–4%
  refresh overhead, and byte-enables that make a 64-bit store a 23-clock write
  with no read-modify-write.
- **At 100 MHz it meets both the throughput requirement (one word per 400 ns)
  and the latency window (1,200 ns, tightened from the previous note's 1,500) for
  every access pattern** — 5.0× and 3.0× margins on the optimistic bound, a thin
  but real 1.24× and 1.55× on the pessimistic one. 166.67 MHz is comfortable
  (1.83×/2.6× even scattered). 50 MHz works only if granules are reused.
  **25 MHz, the only hardware-validated clock, does not work at all.**
- **The interleave is a gift, under one specific address map**: granule =
  4 consecutive Stretch words makes the granule number *equal* the unit index in
  the 4-way region, so one 256-bit read answers units 0–3 at index `g` at once —
  and the access pattern the interleave exists to accelerate is the one that
  fills a granule. The unit-major map the previous note proposed discards 3 of
  every 4 words and costs 4×.
- **The crossing must be a phase-locked divider, not a `SyncFIFO`** — 40 ns
  instead of 600 ns out of 1,200 — and that same choice makes the core clock an
  enable, so **a broken promise stalls the core by a counted number of machine
  cycles instead of silently latching stale data.** `CYCLES<=` bounds stay
  exactly true; only wall-clock time dilates, by a readable amount.
- **Correct the plan's naming**: not upstream Flute (no driver), not
  `ulx3s_bsv` (does not burst, no hardware evidence, TODO on clock phase) —
  **`~/src/ulx3s-experiments/flute-ulx3s/src/Sdram_Controller.bsv`**, with
  `PLL.bsv` borrowed from `ulx3s_bsv` and its scaling-refresh pattern copied
  when the constants are re-derived.
