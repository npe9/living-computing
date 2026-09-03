# Stretch microarchitecture plan: from ISA model to the real machine

Written 2026-09-03 on the owner's instruction: *"make the microarchitecture
the same as the original stretch, this includes pipelining and the other
tricks they did."* This supersedes the founding scope statement in
`bsv/README.md` ("ISA-level correctness, not the famous pipelined
microarchitecture"). Everything the project built up to this point --
the STRAP assembler, the listing oracle, and above all the suite of
verbatim 1961 diagnostic programs -- becomes the correctness oracle for
the rewrite.

## 1. Scope: a cycle-accurate replica, every documented feature, and the folklore

**Target (owner's instruction, 2026-09-03): a cycle-accurate replica of
the IBM 7030 Stretch that corresponds to every documented feature and
to the folklore.** That means:

- *Cycle-accurate*: for any program, the model's clock count matches
  what the real machine's documented timing says -- IBM's Performance
  Characteristics tables and worked examples, Blosk's and the CE
  manual's timing charts, and vol.2's measured benchmarks are the
  oracles; a discrepancy is a bug in the model until a source shows
  the document was wrong.
- *Every documented feature*: everything the Reference Manual, the
  pocket card, Buchholz, Blosk, the CE manuals and the diagnostics
  describe the machine as doing -- the whole instruction set including
  what is unimplemented today (floating-point arithmetic, decimal VFL,
  radix conversion, EX/EXIC, LVE/SVA/RNX/LVS, bit branching, swap and
  backward transmit, all I/O and channel functions), the interrupt
  system with its mask and left-most-one priority, boundary
  protection, the interval timer and time clock, the maintenance
  console's manual controls and repeat mode, ECC and parity checking
  with their indicators, memory interleaving and the bus priorities,
  the look-ahead's forwarding, recovery and housecleaning, the
  I-box's branch guess and updated indicators, index storage's
  destructive read and two-cycle write, the two arithmetic units and
  their register sharing.
- *The folklore*: the behaviors the machine was known for, which the
  documents describe as consequences rather than features -- that
  successful branches empty the buffers and cost a refetch; that a
  store close to a fetch stalls or forwards; that consecutive stores
  fight over the single LAAR; that a VFL crossing a word boundary
  costs extra levels; that I-box instructions load recovery levels
  and can leave the E-box idle; that the machine appears sequential
  despite everything in flight; that it delivered less than the
  promised speed (the performance figures in Perf. Char. §2 and
  Buchholz §15.7 are part of the record, not embarrassment to hide).
  §1a below is the running inventory of both, each with its source
  and status, and grows whenever a source turns up something new.

The 7030 was built from ~170,000 transistors in current-mode logic with
ECC on every memory word and parity on every internal register. The
model reproduces the machine at the level its own designers described
it: the functional units, their registers and buses, the buffering
between them, the interlocks that keep out-of-sequence execution
invisible, branch guessing and recovery, and the cycle timing of each
unit. It does not reproduce gate-level logic or physical clock
distribution; the error-checking hardware is modeled as the pipeline
stages it occupied plus the indicators and interrupts it raised (the
"I checker" takes a cycle whether or not there is an error), with the
correction algorithms themselves modeled only insofar as a diagnostic
exercises them.

### 1a. Feature and folklore inventory (living)

Status: **done** = modeled and tested; **partial**; **planned** (stage
in parentheses); **open** = no stage assigned yet.

| Item | Source | Status |
|---|---|---|
| Six interleaved 16K-word 2.1 µs memory units, MBCU busy handling | Buchholz §14.1/14.3 | done (stage 1); 8-channel priority partial |
| Bus return tags per requester | Blosk p.19 | done for operand/1Y/2Y; LA levels planned (3) |
| 1Y/2Y instruction buffers, I-checker cycle, program-store compare | Blosk pp.10, 15, 21 | done (2a); compare is conservative |
| Successful branch empties the buffers and refetches | Perf. Char. p.3-17, Blosk p.35 | done (2a); overlap of the refetch inside CB's sequence planned (2b/3) |
| Per-class I-box instruction times (tables 4-8) | Perf. Char. §3 | done as budgets (2b) |
| FP/VFL preparation cycles; VFL SAU equation | Blosk figs 6-7; Perf. Char. tables 2-3 | done as budgets (2b); overlap with E-box planned (3/4) |
| Y-to-Z transfer, index fetch, modification, WBC as explicit register stages | Blosk pp.13-14, 31; CE figs 3.1.6-3.1.24 | planned (2b/2c) |
| Index storage destructive read, 2-cycle write, word 17 timer/clock | Blosk p.11 | planned (2c) |
| Updated indicator register; index-indicator branches resolved in the I-box | Blosk p.17 | planned (2c) |
| Arithmetic-conditional branch guessed not taken; wrong-way recovery | Buchholz §15.2; Perf. Char. p.3-23 | planned (2c/3) |
| Four look-ahead levels, five counters, tags, indicators, IC per level | Buchholz §15.3 | planned (3) |
| LAAR, forwarding, store-close-to-fetch cases (1)-(3) | Buchholz §15.4; Perf. Char. pp.3-20..21 | planned (3) |
| I-box instructions load index-recovery pseudo-store levels | Perf. Char. p.3-22; Blosk p.33 | planned (3) |
| Interrupt recovery / housecleaning | Buchholz §15.6; CE figs 3.2.22-23 | planned (3) |
| Serial and parallel arithmetic units, A/B and C/D registers | Buchholz §14.4 | planned (4) |
| Floating-point arithmetic (all ops), timing per table 2 and CE figs 3.8.x | Ref. Manual; CE 3.3.x/3.8.x | planned (4) |
| Decimal VFL, radix conversion, VFL multiply/divide | Ref. Manual; CE 3.11.x | open |
| EX/EXIC (with LA drains, table 6), LVE, SVA, RNX, LVS, bit branching, swap/backward transmit | Ref. Manual; Perf. Char. table 6 | open |
| Interrupt system: indicators, mask, left-most-one, the "free instruction" | Blosk pp.16-17; Buchholz ch.10 | open |
| Boundary registers and inside/outside alarms | Blosk p.20 | open |
| Interval timer and time clock stepping (1024/s) | Blosk p.6 | open |
| ECC/parity: check cycles, correction, indicators, I-checker conflicts | Blosk p.15; Perf. Char. p.3-19 | partial (check cycle only) |
| Exchange as a bus requester with real overlap; disk synchronizer | Buchholz ch.16 | open (I/O is a synchronous FSM today) |
| Maintenance console: start/stop, display/store, single step, repeat mode, index-storage test | Blosk p.6 | open |
| Measured benchmark timings (GERB2 etc.) | Perf. Char. vol.2 | planned (5) |

Concretely, "the same" means these things, each with a primary source:

| Aspect | Real machine | Source |
|---|---|---|
| Memory | 16,384-word units, 2.1 µs read-write cycle, each with its own addressing and data registers; typical system 6 units: 4 interleaved (consecutive addresses in different units) for data + 2 interleaved for instructions | Buchholz ch.14 §14.1 (p.202); Blosk fig.1 |
| Memory bus control unit (MBCU) | Arbitrates 8 requesters with priority exchange > disk > look-ahead > instruction unit; accepts one store/fetch per 0.3 µs; returns a word ~1.6 µs after request when the unit is free; holds requests for busy units; each request carries a 3-bit return address (which Y register or LA level) | Buchholz §14.3 (pp.205-206); Blosk p.19 |
| Instruction unit (I-box) | ICR (19 bits) with +2 adder giving n..n+3; two 64-bit instruction/data buffers 1Y, 2Y; index storage: 17-word × 73-bit core array (word 17 = timer/clock) with one data register XR; preparation/execution register ZR (64 bits + 3-bit P for progressive indexing); working register WR (19 bits); 24-bit index adder with in-buses A (IC, WR, XR, ZR, complementable) and B (Y registers, ZR); shared I checker; up to six instructions in progress | Blosk TR00.722 pp.7-15, fig.3 |
| I-box responsibilities | Fetches and checks every instruction; indexes (normal and progressive); pre-decodes; executes index arithmetic, branches, transmit and misc itself; initiates operand fetches for FP/VFL and loads them into look-ahead; monitors all addresses against the boundary registers; runs the interrupt mechanism; steps the timer/clock | Blosk pp.4-6, Appendix B |
| Branch guessing | Conditional branches on arithmetic results are assumed *not* taken; the I-box continues; index-indicator branches (CB family, B on XF/XVLZ/XVZ/XVGZ/XCZ/XL/XE/XH) are resolved in the I-box from an "updated indicator register" of eight triggers | Buchholz §14.3 p.207, §15.2 p.238; Blosk p.17; Perf. Char. vol.1 p.3-22 |
| Look-ahead (LA) | Four levels, each: op code, 8 tag bits (level filled, level checked, internal operand, IC valid, LA op code, word-boundary crossover, no-op, from), 15 indicators, instruction counter, 64-bit operand; five ring counters (instruction-unit, operand-check, transfer-bus, arithmetic-bus, store-check) advancing under interlocks; one look-ahead address register (LAAR) with forwarding; all stores to memory and internal registers performed by LA; index-recovery pseudo-store levels; recovery ("housecleaning") on interrupt or wrong-way branch | Buchholz ch.15 §15.3-15.6 (pp.238-247), figs 15.6-15.10 |
| Arithmetic unit (E-box) | Serial unit (VFL add/subtract, connectives, FP exponent) and parallel unit (FP fraction add/multiply/divide, VFL multiply/divide), sharing the 128-bit accumulator A/B and 128-bit operand register C/D; slave to LA (receives op + operand, signals termination, returns store results to LA); basic cycle 0.3 µs | Buchholz §14.4 (pp.208-216); Perf. Char. vol.1 ch.3 |
| Timing | E-box cycle 0.3 µs; I-box control cycle 0.5 µs as designed (Blosk p.23) and 0.6 µs as shipped (Perf. Char. p.3-17: "decoding time of I-box instructions is 0.6 µs", table entries in multiples of 0.6); FP preparation one instruction per 1.2 µs; VFL preparation 3.6 µs minimum loading two LA levels, +0.6 per extra level or indexing; per-instruction pre-execution/execution cycle counts | Perf. Char. vol.1 ch.3 tables 2-9; Blosk figs 6-10 |
| Clocks | Units asynchronous with respect to each other, synchronous within; one master oscillator | Buchholz §14.2 p.204; Blosk p.21 |

Sources are all in `docs/` (downloaded from bitsavers 2026-09-03; the
site refuses non-browser user agents): `Planning_A_Computer_System.pdf`
(Buchholz, 1962; ch.14 = PDF pp.227-250, ch.15 = PDF pp.253-272),
`TR00.722_Stretch_I-Unit_Design_Mar60.pdf` (Blosk), `TR00.03000.703_
StretchVM_59.pdf` (Cocke & Kolsky, the look-ahead simulation study),
`Bloch_EngrDesOfStretch_1959.pdf`, `7030_Performance_Characteristics_
Vol1_Mar61.pdf` and `_Vol2_` (vol.2 is benchmark listings with measured
times -- a timing validation set), `ADescriptionOfStretch_Dec59.pdf`,
and the CE manuals `R23-9732_Manual04_7101_CPU_Jan63.pdf` (section 3:
flow, block and timing charts) and `R23-9694/9695` (CE programming
introduction). Only Buchholz and the two Performance Characteristics
volumes have text layers; the rest are read as page images.

## 2. Where the current model stands

`bsv/` today is a single non-pipelined core (`StretchCore.step()`):
fetch, decode completely, execute one instruction to completion (with
multi-cycle bail/resume for BRAM reads, a two-step index write, and an
I/O transfer FSM), then the next. Storage is one BRAM behind a
request/response interface. There is no instruction buffering, no
overlap, no look-ahead, no separate arithmetic unit, no timing. It is
architecturally correct for everything the 20-block suite covers, and
that correctness is what the rewrite must preserve at every stage.

What carries over unchanged: `StretchDecode.bsv` (field extraction),
`StretchALU.bsv`/`StretchVFL.bsv` (arithmetic on operands already in
registers), the assembler, the testbench generator's checks, and the
programs. What is replaced: `StretchCore.bsv` and the control structure
of `StretchExecute.bsv`. What is added: the units in §3.

## 3. Target structure (Bluespec modules)

```
                    +----------------------------------------------+
  memory units      |  mkMemoryUnit x6  (16K words, 2.1 µs cycle)   |
                    +----------------------------------------------+
                                       ^ requests / data
                    +----------------------------------------------+
  bus               |  mkMBCU  priority arbiter, interleave map,   |
                    |          busy tracking, 3-bit return tags    |
                    +----------------------------------------------+
                        ^ fetch (I-box)      ^ store / fetch (LA)
   +--------------------+------+     +--------+--------------------+
   |  mkInstructionUnit         |     |  mkLookAhead                |
   |  ICR, 1Y/2Y, XS+XR, ZR+P,  | --> |  4 levels, 5 ring counters, |
   |  WR, IAU, I checker,       |     |  LAAR + forwarding, store   |
   |  updated indicator reg,    |     |  path, recovery             |
   |  tags, boundary compare    | <-- |                             |
   +----------------------------+     +-------------+---------------+
                                                    | transfer bus / arithmetic bus
                                      +-------------v---------------+
                                      |  mkArithmeticUnit           |
                                      |  serial (VFL/conn/exp) +    |
                                      |  parallel (FP fraction,     |
                                      |  mul/div); A/B, C/D regs    |
                                      +-----------------------------+
   +----------------------------+
   |  mkInterruptMechanism      |  indicator reg (64), mask (20),
   |                            |  left-most-one detect
   +----------------------------+
   +----------------------------+
   |  StretchIO (exchange) --   |  becomes an MBCU requester with
   |  existing simulated devices|  highest priority
   +----------------------------+
```

Cycle base: one Bluespec clock = one E-box cycle = 0.3 µs. Units that
are asynchronous in the real machine are modeled as separately-clocked
FSMs on that common base (I-box control stages advance every 2 clocks;
a memory unit is busy for 7 clocks; the MBCU accepts one request per
clock). A global cycle counter exposed to the testbench gives every run
a time, and per-unit trace output (`$display` under a flag) gives the
same view Blosk's figures 6-10 draw.

## 4. Stages, each ending green on the full suite

The order follows the data: memory first (everything else waits on it),
then the unit that drives everything (I-box), then the buffering between
I-box and E-box (look-ahead), then splitting execution. Each stage is a
separate commit series with the full `run_tests.sh` suite green before
the next begins; the suite checks only architectural results, so a
stage that changes timing but not results is exactly what "green"
should mean.

**Stage 0 -- observability.** Add the cycle counter, a `PC=`-style
`CYCLES<=` bound check to `gen_tb.py`, and a per-unit trace flag. No
behavior change. (Small; lets every later stage report its timing.)

**Stage 1 -- memory units and the MBCU.** Replace `StretchStorage`'s
single BRAM with six `mkMemoryUnit`s behind `mkMBCU`: interleave map
(4-way over the data block, 2-way over the instruction block, per
Buchholz §14.1), per-unit busy for 7 clocks, priority arbitration,
return tags, and the request/response latency the rest of the machine
sees (~5 clocks when free). The 0-31 special-register words stay
register-backed inside the CPU (they are, on the real machine: index
storage and internal transistor registers -- Blosk p.19). The existing
core keeps working with a longer, variable memory latency; its
bail/resume design already tolerates that.

**Stage 2 -- the instruction unit.** New `mkInstructionUnit` replacing
the core's fetch/decode/step loop: ICR with n..n+3 addressing; 1Y/2Y
buffers filled ahead by the IC controls; I checker stage; Y-to-Z
transfer with the half-word criss-cross that aligns full-word
instructions; index storage as a 17-entry array with its 1-cycle read
and 2-cycle write through XR; ZR/P/WR; the index adder; pre-decoding
and the tag triggers; execution of the I-box instruction classes
(Blosk Appendix B: index arithmetic, branches, transmit, misc, SIC);
the updated indicator register for I-box-resolved branches; the
not-taken guess for arithmetic-conditional branches. At this stage the
E-box-class instructions (VFL, FP, connectives, I/O) are still executed
in order by the old execute path fed from ZR, so the suite must stay
green while instruction fetch and I-box execution become real.
Timing target: Blosk fig.6 (FP preparation one per two I-box cycles),
fig.8 (CB in six cycles), Perf. Char. tables 4-9 for I-box instruction
times.

**Stage 3 -- the look-ahead.** `mkLookAhead` with four levels of the
exact register set (op code, 8 tags, 15 indicators, IC, operand), the
five ring counters with the interlocks of Buchholz figs 15.7-15.10,
the LAAR with forwarding and store-close-to-fetch handling (Perf. Char.
pp.3-20..3-21: prefetched-instruction invalidation, delayed operand,
forwarding), all stores routed through LA, index-recovery pseudo-store
levels for every I-box instruction, and recovery/housecleaning on
interrupt and on wrong-way branch (I-box IC and index registers
restored from LA, intervening operations cancelled). The old execute
path becomes the consumer of LA levels. This is the largest stage and
the one the suite's SIC/CB/branch programs exercise hardest: every
verbatim I-Box 1 group is a sequence of I-box branches interleaved
with LA-loaded operations, and the p.50-51 SIC groups in particular
store into instructions that have just been prefetched.

**Stage 4 -- the arithmetic unit.** Split execution into the serial
and parallel units with A/B and C/D, driven by LA's transfer-bus
counter and reporting termination to the arithmetic-bus counter;
pre-execution vs. execution cycle accounting per Perf. Char. table 2
(FP) and the VFL tables; VFL word-boundary-crossover operands
arriving in two LA levels. Floating-point arithmetic beyond L/ST
(unimplemented today) is added here, since the parallel unit's timing
is the reason the machine exists.

**Stage 5 -- timing validation.** Reproduce Perf. Char. vol.1 ch.4's
worked timing examples and vol.2's benchmark programs (STRAP source
with measured times) as tests with `CYCLES<=` bounds; compare Blosk's
figures 6-10 against the trace output cycle by cycle.

Deferred, in scope, after stage 5: the interrupt system as a whole
(indicator/mask/left-most-one, the "free instruction"), boundary
protection alarms, the timer/clock stepping through index storage word
17, the exchange as an MBCU requester with real overlap (the current
synchronous I/O FSM is a stage-1 compatibility path).

## 5. Oracles and how each stage is verified

1. **Architectural**: `strap/run_tests.sh` -- 20 blocks, ~600 listing
   rows, seven verbatim diagnostic programs with the deck's own pass/
   fail mechanisms. Green before every commit, as now.
2. **Discriminating checks for the microarchitecture**: programs whose
   *result* depends on the machine doing the trick correctly rather
   than merely fast -- store-into-prefetched-instruction (the SIC
   groups already do this; add Perf. Char.'s three "store close to
   fetch" sequences as programs), forwarding (`LOAD a; MULTIPLY a;
   MULTIPLY a` per Buchholz §15.4), wrong-way branch recovery with
   index registers modified by prefetched I-box instructions, and
   interrupt recovery once interrupts exist.
3. **Timing**: `CYCLES<=` bounds from Perf. Char. tables, Blosk's
   diagrams, and vol.2's measured benchmarks. Timing checks are
   separate from architectural checks so a timing regression cannot
   masquerade as a correctness failure or vice versa.
4. **Bug injection** stays the rule: every interlock gets a test that
   fails when the interlock is removed (e.g. remove the instruction-
   unit-counter/store-check interlock and watch a store be lost).

## 6. Known risks

- **bsc scheduling.** The single-rule `step()` design was chosen partly
  because bsc rejected same-rule combinations of storage and index
  writes (README "Toolchain" item 7). Six concurrently firing units
  with shared buses will need explicit arbitration modules and FIFOs/
  RWires rather than one big rule; expect to rediscover G0004
  conflicts early in stage 2 and design the buses as modules with
  single-writer methods from the start.
- **Fidelity vs. documentation gaps.** Blosk's report predates the
  shipped machine (0.5 µs vs 0.6 µs I-box cycle); where Buchholz,
  Blosk and Performance Characteristics disagree, the 1961
  Performance Characteristics (measured on the built machine) wins
  for timing and the CE manual (1963) wins for structure. Record each
  such choice in this document.
- **Elaboration size.** Four LA levels × 64-bit operands, two Y
  registers, a 17-word index array and six memory units are modest;
  the earlier Vector-of-Reg blowup came from a 256-entry register
  file with dozens of read ports, which none of these are.
- **Suite runtime.** A cycle-level model runs the same programs in more
  simulated cycles; the suite's ~10-minute wall time is dominated by
  bsc compilation, not simulation, so this should stay tolerable.

## 6a. Stage 2 design: the instruction unit

Written after reading Blosk TR00.722 in full and the CE manual's
section-3 figure index. The CE manual's I-unit flow diagrams are the
sequencer-level reference: figures 3.1.1-3.1.5 (IF 1Y / IF 2Y
sequencers, IC 1Y/2Y triggers, IWC1/IWC2, IC Adv and ICOR), 3.1.6-3.1.9
(Y-Z start trigger and the four YL/YR to ZL/ZR transfer sequencers),
3.1.10-3.1.21 (ZR/ZL Mod Req triggers and Mod sequencers, block/suspend
triggers, the ZL/ZR FP triggers 1-6), 3.1.22 (IHW = "instruction half-
word" triggers, 1-bit mod, FP Z ALT), 3.1.23 (WBC+DEC and XF+DEC
sequencers), 3.1.24-3.1.28 (WBC trigger, FW/FWS/FW-not-S triggers, ZL
DEC trigger). The LA's are 3.2.1-3.2.27 (IAUC load, LA load pulses,
operand check, TBC advance, SAU/VFL/FP levels, LAOP codes, ABC actions
and indicator timers, houseclean timers, SCC advance/actions/stores).
PAU data flow 3.3.x, FP timing 3.8.x, error conditions 3.7.x/3.9.x.

**Time base.** The I-box control cycle is two clocks (0.6 µs as
shipped, Perf. Char. p.3-17); sequencers advance on I-box cycles,
memory on clocks. A `phase` toggle in the unit selects the A/B pulse.

**Registers** (Blosk pp.7-15): `ICR` (19); `Y1`, `Y2` (64 + valid +
checked + word address + fetch-outstanding); index storage `XS`
(Vector of 16 words + word 17 timer/clock) with data register `XR`;
`Z` (64, with `P` 3 bits) and its two halves; `W` (19); the index
adder `IAU` as functions over bus-A/bus-B selections; the updated
indicator register `UIR` (XL XE XH XCZ XVLZ XVZ XVGZ XF). The I
checker is a one-cycle stage between a Y register's arrival and its
`checked` flag (no error paths yet).

**Control areas** (Blosk p.25-27), each an FSM stepping on I-box
cycles:
- *IC controls*: keep 1Y/2Y filled -- when a Y is empty and no fetch
  is outstanding for it, request the next instruction word (the ICR
  and adder give n..n+3) through the MBCU with that Y as return tag;
  on a taken branch or recovery, invalidate both and restart at the
  target. Interlocks: a store whose address compares equal to a
  prefetched word invalidates the Y registers (program store compare,
  Blosk p.21; Perf. Char. p.3-21 sequence (1)).
- *Preparation controls*: when Z is free and the next half-word (per
  ICR) is in a checked Y, transfer Y->Z (one cycle; a full-word
  instruction straddling 1Y/2Y needs both), fetch the index word (XF,
  one cycle, reading XS into XR) when I != 0, modify (MOD, one cycle
  through the IAU; progressive indexing takes its two-step form); for
  VFL, the word-boundary-crossover test (WBC) adds the length to the
  24-bit address and gates the second word's address into W. The ICR
  advances as Z is loaded.
- *Look-ahead load controls*: for FP/VFL/I-O (E-box class) the
  prepared instruction leaves Z for execution. **Stage-2 simplification:**
  there is no look-ahead yet, so the existing `execute()` runs the
  instruction to completion in order, performing its own operand
  fetches through the storage handshake; its cycle cost is therefore
  unoverlapped. Stage 3 replaces this with the four levels.
- *Instruction-execution controls*: I-box instructions (Blosk
  Appendix B: direct and immediate index arithmetic, unconditional
  branches, branch on indicator, branch on bit, count-and-branch
  family, SIC, transmit/swap, refill, execute, store zero) execute in
  the I-box. Their *semantics* come from the existing `execute()`
  arms (already verified by the suite); their *timing* comes from a
  per-class I-box cycle count taken from Blosk's figures 8-10 and
  Perf. Char. tables 4-8 (e.g. CB successful 4.2 µs + decode = 8 I-box
  cycles; LVI 2.4 µs + dec = 5; LX from external memory 4.8 µs + dec =
  9, of which the operand fetch's real memory time is charged as it
  happens). Index-storage stores take two cycles.
- *Branches*: unconditional and index-indicator branches (CB family;
  B on XF/XVLZ/XVZ/XVGZ/XCZ/XL/XE/XH) are resolved in the I-box from
  the UIR at preparation time and cost a Y refill. Branches on other
  indicators are guessed not taken: the I-box goes on fetching and
  preparing the fall-through path. **Stage-2 simplification:** since
  the guess cannot yet be undone for index registers (no pseudo-store
  recovery levels), the I-box does not *execute* an I-box instruction
  past an unresolved arithmetic-conditional branch; it prepares and
  waits. When the executor resolves the branch as taken, the prepared
  fall-through work is discarded and fetching restarts at the target
  (the wrong-way recovery cost of Perf. Char. p.3-23).

**Deliverables**: `bsv/StretchIBox.bsv` (new) replacing
`StretchCore.step()`'s fetch/decode loop; `StretchCore` becomes the
composition of I-box + executor + storage + I/O. Suite green. Timing
tests: Blosk fig.6 (four indexed FP loads prepared in eight I-box
cycles), fig.8 (CB in six), tables 4-8 spot checks, all as `CYCLES<=`
programs. Trace flag showing, per I-box cycle, the IC/Y/Z/XF/MOD
activity in the format of Blosk's diagrams.

## 6b. Stage 3a design: the look-ahead, first cut

Four levels in a ring (`LaLevel`: instruction, IC value, operand
address, operand, fetch-issued, wait-for). The instruction unit loads
an E-box-class instruction (VFL, connective, floating point) into the
tail level at preparation: if it fetches a memory operand, the
operand address is obtained by running `execute()` with no operand,
which bails out with the address of the first read it needs and no
side effects (the contract established in the BRAM migration) -- so
the address arithmetic lives in one place; instructions that fetch
nothing (immediate VFL, FP store) are loaded without a probe and run
only at removal. Levels issue their fetches ahead on their own bus
channels (tags 3-6, priority above the Y buffers); a level whose
operand address equals an earlier unretired level's waits for that
level to retire (store-then-load ordering, the LAAR's job -- Cocke &
Kolsky fig.6A's compare/forward, done conservatively for any earlier
level rather than only stores). The arithmetic unit removes the head
level when its operand is present, executing with the operand
pre-supplied; further reads (crossing words, refills) go through the
existing resume path. E-box time (`eboxClocks`) holds the next
removal, the I-box budget holds the next preparation, so preparation
and fetch-ahead overlap execution. Conservative rules of this cut,
to be relaxed in 3b/3c: an I-box-class instruction waits for the
levels to drain before executing (no index-recovery levels yet, so
nothing the I-box does can run ahead of an E-box store or a
progressive-indexing modification); a load waits while a
progressive-indexing instruction is in the levels; branches on
non-index indicators are I-box-class and therefore also wait, which
is Cocke & Kolsky's "hold up on every branch" option -- the
not-taken guess comes with recovery in 3b.

## 6c. Stage 3b design: I-box instructions running ahead

Perf. Char. p.3-17: "I-box operations usually do not involve the
E-box, and the I-box time can be covered largely by neighboring
floating point operations" -- the folklore item that index arithmetic
and count-and-branch hide behind arithmetic. In 3a every I-box-class
instruction waits for the levels to drain; 3b lets it execute while
levels are pending unless a hazard exists:

- *Memory it reads* (LX/LV/LC/LR/KV/KC/V+ family, R/RCZ and CBR's
  refill word, Transmit's source): wait if any unretired level's
  operand address is that word (an E-box store ahead in program order
  may not have happened yet -- Cocke & Kolsky fig.5's "does index
  address compare with an address in a virtual memory").
- *Memory it writes* (SX/SV/SC/SR, Z, SIC's store, Transmit's
  destination): wait if any unretired level's operand address is that
  word (a level ahead in program order must fetch the old value).
- *Arithmetic indicators* (branch on a non-index indicator): wait for
  the levels to drain -- this stays "hold up on every branch" until 3c
  adds the not-taken guess with recovery.
- *Index registers*: free -- pending E-box levels were indexed at
  preparation and only progressive indexing modifies an index register
  at execution, and a progressive-indexing level already blocks further
  loading (3a rule), so it also blocks I-box run-ahead until it retires.

The operand word of an I-box-class instruction is computed at
preparation with the same effective-address arithmetic execute() uses
(index value plus address; refill from the index word), the second
place that arithmetic appears, kept to the one-line cases; anything
not in the list above waits for a drain. Its time budget and Y-buffer
restart behave as before. No recovery levels are needed yet because
nothing the I-box does ahead can be wrong: no guessed branches, no
interrupts.

## 6d. Stage 3c design: the not-taken guess and wrong-way recovery

Buchholz §15.2 item 4 and Blosk p.28: "for a branch instruction
conditional on the result of arithmetic-unit operations, the
instruction unit proceeds as if the branch will fail"; Perf. Char.
p.3-23: "all changes in the index registers and/or index indicators due
to the advance processing by the I-box must now be undone ... The
correct instruction counter value is also shipped back to the I-box."

- A branch on a non-index indicator (Perf. Char. p.3-22: everything but
  XF/XVLZ/XVZ/XVGZ/XCZ/XL/XE/XH) is loaded into a look-ahead level as a
  *branch level* -- the real machine uses four levels (instruction,
  indicator fetch, store, recovery); the model charges their time and
  keeps one level -- with its target address computed at preparation.
  The instruction unit records the guess (a snapshot of the sixteen
  index words and the index indicators, standing for the recovery
  pseudo-store levels the machine would have loaded one at a time) and
  continues down the fall-through path. Only one guess is outstanding
  at a time; a second arithmetic branch waits.
- While a guess is unresolved the I-box executes index arithmetic and
  index branches ahead, as 3b allows, but stalls anything whose effect
  could not be undone by the snapshot: stores to memory (SX/SV/SC/SR,
  Z, SIC, Transmit -- on the real machine these become store levels
  that the store-check counter does not release before the branch
  level), unconditional branches and halts (so a halt is never reported
  under a wrong guess), and a second guess.
- When the arithmetic unit reaches the branch level, all earlier
  operations are complete, so the indicators are final: the branch
  executes with its normal semantics (test, optional clear). Guess
  right: retire the level. Guess wrong: cancel every younger level,
  restore the index registers and index indicators from the snapshot,
  set the instruction counter to the target, invalidate the Y buffers,
  and charge the recovery time (Blosk fig.10: the branch's own five
  cycles; plus the refetch).

Cost model: the branch level's four-level load is charged as the
branch's I-box time (6 cycles); a wrong guess adds a Y refill. The
interrupt system, when it arrives, uses the same recovery path
(Buchholz §15.6: "the interruption action is quite similar to branch
recovery except that in addition a new instruction has to be fetched").

## 7. Status

- **Stage 0 -- done** (2026-09-03): `CYCLES<=N` check in `gen_tb.py`;
  `stepCount` at halt is the clock count. Per-unit trace flag still
  to add.
- **Stage 1 -- done** (2026-09-03): `StretchMemory.bsv` (six units,
  interleave map, 7-clock cycle, 5-clock read-out, single-requester
  MBCU with nonexistent-address handling) and `StretchStorage.bsv`
  reworked as the bus client (in-order store queue of 8, one
  outstanding read, `responseReady`/`writeReady` handshake). Three
  stall guards in `StretchCore.step()`, and the generated and hand-
  written testbenches poll the handshake instead of assuming one-cycle
  latency. Full 20-block suite green unchanged; first cycle bounds
  recorded (Problem 2.1: 94 clocks; pp.43-51 span: 2714). Found on the
  way: Bluesim's BRAM is not zero-initialized (0xAA..), so tests must
  not rely on unwritten storage reading as zero -- the smoke test now
  halts on its own data word instead of on fall-through. Not yet
  modeled: the eight-channel priority arbitration (one requester so
  far), address-invalid indication for nonexistent addresses.

- **Stage 2a -- in test** (2026-09-03): tagged bus responses
  (`RetTag`: operand, 1Y, 2Y) in `StretchMemory.bsv`; three read
  channels with priority order stores > operand > 1Y > 2Y in
  `StretchStorage.bsv`, instruction fetches held while stores are
  queued (conservative program-store compare); `StretchCore.step()`
  now begins with the IC controls -- two `YReg` buffers filled ahead
  through their own channels, a two-clock I-checker delay, freeing
  behind the instruction counter, invalidation on a taken branch, on
  `setPC`, and on a store to a buffered word (`recentStore`), with
  in-flight fetches for invalidated buffers discarded on arrival --
  and prepares each instruction from the buffers (a full word may
  straddle 1Y/2Y). The old one-fetch-at-a-time FSM is gone. Two
  real findings from the suite on the way: (1) reads on the operand
  channel must still wait for queued stores (the first channel
  generalization dropped that and a testbench read a control word
  before its store reached memory); (2) a 16-word tape transfer
  streams stores faster than four interleaved 2.1 µs units absorb
  them and overflowed the 8-deep store queue -- the exchange now
  waits for queue space per word, and an instruction does not start
  while the queue is full (the LAAR-busy wait of Perf. Char. p.3-21
  in miniature). Cycle counts with prefetch overlap: Problem 2.1 94
  -> 54 clocks, the pp.43-51 span 2714 -> 2065.
- **Stage 2b -- done** (2026-09-03): per-class time budgets (§6a),
  `ibox_timing_cb.strap` (250 table clocks, measured 291).
- **Stage 3a -- done** (2026-09-03; full 21-block suite green, Problem
  2.1 113 -> 92 clocks, pp.43-51 span 4006 -> 3985, the CB loop
  unchanged at 291 since it holds no E-box work): the look-ahead of §6b, seven
  bus tags, level channels in `StretchStorage`, `LaLevel` in
  `StretchTypes`, the engine in `StretchCore.step()` (levels
  collected/issued at the top of every clock; removal and preparation
  as branches of the one instruction chain so at most one `execute()`
  runs per clock). Follow-up: the E-box busy wait and the resume wait
  had preempted preparation (four loads measured 162 clocks against
  ~115); fixed, 120 clocks, benchmark `la_timing_loads.strap`.
- **Stage 3b -- done** (2026-09-03; 23-block suite green): I-box-class instructions run
  ahead of pending levels under §6c's hazard checks (`iboxHazard`:
  operand-word compare against every level's address for the direct
  index ops, refills, Z, SIC's store and its embedded branch; drain
  for branches on arithmetic indicators and for everything else).
  Benchmark `la_timing_loop.strap`: L/+/ST/V+/CB x10 in 807 clocks
  vs ~1120 serialized. Caught by the suite: the halt (a branch to
  itself) is unconditional and hazard-free, so it executed ahead of
  pending stores and the run ended before they retired -- unconditional
  branches now drain the levels first (the machine's "BD empties the
  LA" behavior, Perf. Char. p.3-18).

## 8. Immediate next steps

1. Stage 2 per §6a: `StretchIBox.bsv`, starting with the IC controls
   and Y buffers (2a), then preparation and I-box execution timing
   (2b), then the not-taken guess and restart (2c).
2. Per-unit trace flag (stage 0 leftover), first used by 2a.
