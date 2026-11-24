# The SoC core's area (fpga/README.md, "The SoC")

The privileged core (`mkHobbitSocCpu`, `bsv/HobbitSocCpu.bsv`) did not
fit the LFE5U-85F. At master 1317cddd it was 116,562 LUT-equivalents,
against the device's 83,640 (fpga/README.md "Area, Fmax and the clock").
The goal set for this work: at most 65,000 for the core, so that the
whole SoC places with room for the devices, which need about 20,000.
The constraint: the machine must not change. Every HRI record of the
co-simulated boot must be identical, `cyc` included, and so must the
core's clock count. These are re-implementations, not timing changes.

Result: **60,422 LUT-equivalents**, in eight milestones. Each was
checked on its own tree by the boot co-simulation, which gave the same
2,893,027 HRI lines byte for byte (`cmp` against the baseline run's) and
the same 9,920,333 core clocks.

Since then:
* Stack-cache copy C (milestone 4, below) brings it to 60,450, because
  the harnesses need it. The SoC drops it in synthesis.
* The byte-enable commit, which changes the device reads rather than the
  area (fpga/README.md "Byte enables and device reads"), measures 60,090.
  It is the one change that moves the core clock total: 9,920,614.

The milestone co-simulations for 4 to 8 ran before copy C. The C runs
that cover them are the m8 + C run (same HRI, 9,920,333 core clocks) and
the tip run.

## Method

* **Unit.** LUT-equivalents are LUT4 + 2 x CCU2C + 6 x TRELLIS_DPR16X4,
  the formula that reproduces nextpnr's "Total LUT4s" (fpga/README.md
  "Area"). PFUMX and L6MUX21 are free: they are muxes inside a slice.
* **Measurement.** `fpga/area_cpu.sh NAME [BSVDIR]` synthesises the core
  alone with yosys 0.51 `synth_ecp5` (abc9) and leaves the netlist in
  `fpga/build/area-NAME/cpu.json`. A milestone's numbers are from a
  frozen copy of `bsv/` at that milestone.
* **Attribution.** `tools/area_cones.py` labels every state element (a
  flip-flop, a block or LUT RAM, an output port) and walks the
  combinational netlist backwards. A cell that reaches one group is that
  group's. A cell that reaches several is "shared", which is where a
  lookup used by several stages lands. `--combos` splits shared logic by
  its exact set of groups.
* **Instance counts.** bsc inlines a value method at every call site
  with its own arguments, and yosys merges two copies only when their
  inputs are the same nets. So the number of distinct addresses a TLB
  lookup or a window read is evaluated on is the cost driver. That
  number can be read off the bsc Verilog: one 32-entry compare per TLB
  lookup, one 16-entry compare per window read.
* **Behaviour.** For each milestone:
  * `fpga/sim/run_soc.sh 2893000` printed MATCH;
  * `grep '^HRI' core.log | cmp - ref_soc.hri` was silent against the
    baseline's 2,893,027 lines;
  * the core clock count was 9,920,333;
  * the unit testbenches that cover the touched code passed (run_mmu,
    run_core_mmu, run_event, run_arith).

  The full regression suite ran on the final tree.

## Where it went (baseline)

`area_cones.py --depth 1` on the baseline netlist (LUT-eq):

| group | baseline | final |
|---|---:|---:|
| shared (several stages) | 58,534 | 25,942 |
| EU stage 2 (`core.s2`) | 14,830 | 9,265 |
| PDU (`core.pdu`) | 10,444 | 8,108 |
| prefetch store (`core.pf`) | 9,901 | 1,018 |
| MMU state (`core.mmu`) | 4,453 | 4,867 |
| stack cache (`core.sc`) | 2,721 | 1,048 |
| EU stage 3 (`core.s3`) | 2,484 | 2,486 |
| memory write port (`port.memWr`) | 2,337 | 925 |
| read address port (`port.rdAddr`) | 2,109 | 765 |
| decode store (`core.ic`) | 1,730 | 1,252 |
| event frame write (`port.evWr`) | 1,281 | -- |
| total | 116,562 | 60,422 |

Ablations of the baseline, each a measurement variant rather than a
design:

| variant | LUT-eq | change |
|---|---:|---:|
| baseline | 116,562 | |
| `notlb`: findTlb always misses | 89,166 | -27.4k |
| `nowin` (on M1): winRead returns 0 | 84,516 | -23.5k against M1 |
| `nosc`: the stack cache's read is a constant | 98,415 | -18.1k |
| `nodiv`: no divide | 116,396 | -0.2k |

The large shared item was the translation, replicated many times over.
A TLB lookup is a 32-entry compare plus a payload select. A table walk is
two reads of the adapter's 16-entry window, each a 16-entry compare plus
a 32-bit AND-OR. In the baseline both were evaluated at every call site
of `translate` and every walk probe. The step rule then re-translated
each of the four noted references twice more, once in `translateFn` and
once in `walk`, and `walkProbes` looked each up a third time.

`nodiv` saves almost nothing. Its divide cost had moved into the
multiplier's second product, which `nodiv` kept; milestone 1 shows the
real figure.

## The milestones

| # | change | LUT4 | CCU2C | DPR16X4 | FF | DP16KD | MULT18 | LUT-eq | saving |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| | baseline (master 1317cddd) | 98,806 | 4,288 | 1,530 | 12,002 | 9 | 11 | 116,562 | |
| 1 | one divider, one multiplier product | 92,538 | 3,125 | 1,530 | 12,002 | 9 | 4 | 107,968 | 8,594 |
| 2 | the core's arrays on the system clock | 88,362 | 3,125 | 8 | 11,997 | 45 | 4 | 94,660 | 13,308 |
| 3 | three prefetch lines on two translations | 85,093 | 3,099 | 8 | 11,997 | 45 | 4 | 91,339 | 3,321 |
| 4 | the stack cache in block RAM | 72,170 | 3,099 | 8 | 10,013 | 59 | 4 | 78,416 | 12,923 |
| 5 | the window read as an AND-OR | 68,503 | 3,097 | 8 | 10,013 | 59 | 4 | 74,745 | 3,671 |
| 6 | a note carries its translation | 65,708 | 3,076 | 8 | 10,013 | 59 | 4 | 71,908 | 2,837 |
| 7 | walk probes from the translation; event frame by page | 61,748 | 3,050 | 8 | 10,013 | 59 | 4 | 67,896 | 4,012 |
| 8 | the text note's own TLB; two event translations | 54,378 | 2,998 | 8 | 10,011 | 59 | 4 | 60,422 | 7,474 |

TLB lookups (distinct addresses in the Verilog, data + text) went from
12 + 6 at milestone 5 to 4 + 4 at milestone 8. Window reads went from
32 at milestone 6 to 18.

### 1. One divider, one multiplier product (`bsv/HobbitCore.bsv`)

DIV/REM was `divSigned`, a 64-bit signed division followed by a multiply
back, and UDIV/UREM was bsc's `/` and `%`. They are now one 32-step
restoring divider on the operands' magnitudes (`udivmod32`, `divUnit`),
with signs applied after. MUL took two 64 x 64 products, signed and
unsigned. It now takes the unsigned product and derives the signed one
by subtracting the two cross corrections (`mulArith`). This went from 11
MULT18X18D to 4.

The replaced forms stay in the file as references (`divSigned`,
`mulArithRef`). `bsv/HobbitArithTb.bsv` (`bsv/run_arith.sh`, in the
suite) compares both against them on 401,156 operand pairs. Its header
records both injections it was shown to catch.

### 2. The core's arrays on the system clock

The core runs on a gated clock, with about ten system clocks between two
core edges. The registers hold throughout, so a RegFile's read address
is stable for all of them. `fpga/sysram_filter.py` rewrites every bsc
`RegFile` in the generated Verilog into `HobbitSysRegFile`
(`fpga/rtl/hobbit_sysregfile.v`). That module has one block-RAM copy per
read port, written on the core clock and read into a register on SYSCLK
from the port's current address. The BSV is unchanged, and Bluesim keeps
RegFile semantics. The prefetch ways and the decode store left LUT RAM
(1,530 DPR16X4 to 8) for 36 DP16KD.

The adapter samples the probes only after the arrays have settled
(SETTLE in `rtl/hobbit_soc_mem.v`, default 1). `tools/sysram_depth.py`
bounds the settling from the netlist. On the final netlist the longest
chain of block-RAM reads into the probe port is 2 (a decode-store read
that addresses a stack-cache bank). No block-RAM read reaches the
probes from `rdData` or the window: depth 0, and 1 into any other port.
So the arrays depend on new state only after a core edge. From that edge
to the probe sample the adapter spends at least four system clocks
(S_WR, S_RD, S_SETTLE, S_PROBE), and SETTLE = 1 holds with margin in
simulation, where logic has no delay. The bound counts stages only. On
hardware the core's own paths are about 190 to 240 ns in the post-placement
estimate (nextpnr, 2026-11-24, unrouted), against the 40 ns that one
system clock gives at 25 MHz. A stage then needs about
ceil(t_stage / 40 ns) system clocks, roughly 5, so the hardware's
SETTLE has to be sized from routed timing, not from the stage count
alone. That is pending.

The co-simulation checks this every time, under `HOBBIT_SIM`, and any
failure stops the run:

| check | what it catches | injection, observed (300,000-record run) |
|---|---|---|
| SYSRAM STALE (`hobbit_sysregfile.v`) | a read port differs from a combinational read at a core edge | the read register clocked on CLK instead of SYSCLK: `SYSRAM STALE ...core_c_pf_way0 at system clock 5106`, 0 records, rc=1 |
| PROBE STALE (`hobbit_soc_mem.v`) | a valid RAM/ROM probe is missing from the window at a core edge | every probe counted as a hit in S_CHECK: `PROBE STALE at core clock 0: probe 21 00000000 not in the window`, rc=1 |
| WINDOW DUPLICATE (`hobbit_soc_mem.v`) | two valid window entries with one address (milestone 5's invariant) | a hit treated as a miss when the fill pointer is 3: `WINDOW DUPLICATE ... entries 2 and 3 both hold 80000000`, 2,245 records, rc=1 |
| EDGE STALE (`hobbit_soc_mem.v`) | two core edges in consecutive system clocks out of reset (the SYSRAM check skips only reset's) | none; no adapter path can produce it |

### 3. Three prefetch lines on two translations (`bsv/HobbitDecode.bsv`)

PDU_S1 looked up a0, a0 + 8 and a0 + 16, each with its own
`translate` and `faultAt`. A translation depends on va[31:12] alone and
passes va[11:0] through, so a0 + 8 takes a0's translation unless a0 is
the last line of its page, and then a0 + 16's. `lines3` does three
lookups on two translations.

### 4. The stack cache in block RAM (`bsv/HobbitStackCache.bsv`)

The 64-word cache was a `Vector` of registers, read combinationally at
five places. It is now six RegFiles: two banks, one per writer (the EU
and the refill), each in three copies with identical writes, because bsc
allows a RegFile five read call sites. Copy A serves `read` and the
flush, B `read2`, and C only `cacheWord`, the harnesses' view. A 64-bit
live-value table selects the bank. On the system clock (milestone 2)
they are block RAM. Copy C was added after the milestone runs: with only
two copies, `P9BootTb`'s three `cacheWord` calls overflowed copy B and
the suite's A1 run failed to compile. The SoC never reads C, so
synthesis drops it: 60,450 LUT-eq with it, against 60,422 without, and
the same 59 DP16KD. The boot co-simulation with it gave the same HRI,
byte for byte, and 9,920,333 core clocks.

### 5. The window read as an AND-OR (`bsv/HobbitSocCpu.bsv`)

The adapter enters an address only on a miss, so valid window entries
are unique. At most one matches, and an OR of the matching words equals
the priority select it replaces, at about half the logic. WINDOW
DUPLICATE checks that invariant.

### 6. A note carries its translation (`bsv/HobbitMmu.bsv`)

A noted reference's translation and walk are now computed in the noting
rule (`noteOf`), from the same clock's state `translate` reads, and
carried on the note wire. The step rule and `walkProbes` use them
instead of translating each note twice more. The stack cache calls
`mem.readReq` once with a chosen address instead of twice, because the
face translates its argument.

### 7. Walk probes from the translation; the event frame by page

* `walkProbe(r)` is built on `noteOf(r)`, the same expression as
  `translate(r)`, so a probe of a reference that a rule also translates
  shares that rule's logic.
* The text note is carried as the bare request and translated once on
  the wire. The prefetch's `noteFetch` has two callers that translate
  nothing themselves.
* The event unit's frame needs base - 4, base - 8 and base - 12. Base - 8
  is on base - 4's page unless base[11:0] < 8, and then on base - 12's.

### 8. The text note's own TLB; two event translations

* The text note's request always has isText set, so stating that keeps
  the data TLB out of its translation.
* The event unit's step makes at most two translations a clock, by state
  and class:
  * EVS_IDLE: base - 4 (or, for the unimplemented sequence, the CSP) and
    base - 12;
  * EVS_WRITE: the frame word;
  * EVS_VECTOR: the vector.

  `evX1` is muxed by state and `evX2` is base - 12's. `combProbes` asks
  for the walks of the same two requests.
* With these, the data TLB is looked up at 4 addresses (was 8) and the
  window read at 18 (was 27).

## Placement (2026-11-24)

`fpga/build_soc.sh 1` on the milestone 8 tree (core only, every device
forwarded) packs and places:
* 61,569 of 83,640 LUT4 (73%);
* TRELLIS_COMB 62,451 (74%).

It did not route in the time given:
* router1 still had 153k of 244k arcs left after two hours;
* router2 stayed at about 48k overused wires from iteration 5 to 9.

Both runs were stopped, so there is no bitstream. The post-placement
estimate is 4.24 MHz for the gated core clock and 5.17 MHz for the
system clock, with every path timed in one system clock. The core's paths
are multi-cycle by design. The SETTLE caveat above follows from that
estimate. The full SoC with its RTL devices is in fpga/README.md ("Area,
Fmax and the clock").
