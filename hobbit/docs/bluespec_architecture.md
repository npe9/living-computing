# Bluespec architecture of the Hobbit model, grounded in Flute

This note fixes *how* the Hobbit model is built in Bluespec: which modules
exist, what interfaces they expose, and where the boundaries sit. The
architectural reference is **Flute**, Bluespec Inc.'s RISC-V SoC, whose
structure — not its instruction set — is what this model follows.

## Credits

**Flute: a free and open-source RISC-V CPU and SoC.**
© 2021 Rishiyur S. Nikhil and Bluespec, Inc. Apache License 2.0
(`Flute/LICENSE` in the reference tree). Version v1.0, 2021-05-19
(`Flute/README.adoc`).

Reference tree used for this note:
`/Users/npe/src/ulx3s-experiments/flute-lx50`, local commit
`432ef19761f1a3dd6a635b89a95ce7efff743b79` (2026-11-19). It is a
read-only reference outside this repository: no Flute source is copied
into `hobbit/`. If that ever changes, the copied file keeps its Apache-2.0
header and is listed in `docs/README.md` as third-party code with its
origin and licence.

What is borrowed is **architectural convention and interface shape**:
stage modules with `enq`/`deq`/`out` interfaces, explicit stall signals,
a reset `Server`, an AXI4/AXI4-Lite boundary between core and fabric, a
separate near-memory subsystem (caches + MMU + arbiter), peripherals as
fabric slaves, and a board wrapper that owns clock and reset
(`Flute/src_Core/CPU/CPU_Stage1..3.bsv`, `CPU_IFC.bsv`,
`Near_Mem_VM_WB_L1/Near_Mem_IFC.bsv`, `src/ClockHacks.bsv`,
`src/ULX3S_Top.bsv`, `src_Testbench/Fabrics/`). What is not borrowed:
the RISC-V ISA, Flute's quantities, its pipeline depth, or any code.

## Why Flute, and not an ad-hoc structure

The owner's requirement is the 92010's *structure* and *cycle counts*.
Flute demonstrates the idiomatic BlueSpec way to get both: one module per
pipeline stage with a registered boundary, cheap explicit stall
handshakes instead of a single monolithic rule, and multi-cycle
datapath boxes behind request/response interfaces. That reproduces the
sibling AGENTS.md rule ("each pipeline stage is its own module … the
expensive datapath lives in multi-cycle, stateful box sub-modules").

## Flute convention → Hobbit block (Figure 1-1, printed p. 1-2)

| Figure 1-1 block | Flute counterpart | Hobbit module (target) |
|---|---|---|
| Prefetch buffer cache, `1024×3 bytes`, 3-way | `Near_Mem_VM_WB_L1/*Cache.bsv` (I-cache + adapter) | `mkHobbitPrefetch` |
| Prefetch/decode unit, 3-stage pipeline | `CPU/CPU_Stage1..3.bsv`, `CPU_StageF.bsv` | `mkHobbitPdu` split into `PDU_S1..S3` |
| Decoded instruction cache, `32×192 bits` | `CPU_DII_IMem.bsv` (decoded-instruction interface) | `mkHobbitDecodeStore` |
| Stack cache, `64×32×2 bits` | `RegFiles/` (multi-port register file) | `mkHobbitStackCache`, one read + one write per clock |
| Execution unit, 3-stage pipeline | `CPU/CPU_StageD.bsv`, `CPU_Stage3.bsv` | `mkHobbitExec` split into `EU_S1..S3` |
| MMU, `2×32 page TLB`, `2×1 seg NPSR` | `Near_Mem_VM_WB_L1/D_MMU_Cache.bsv`, `I_MMU_Cache.bsv` | not modelled yet (gate: plan.md step 5) |
| Bus face (HA/HD/BE/IOC/START/…) | `AXI4_Master_IFC`, `AXI4_Lite_Slave_IFC`, `src_Testbench/Fabrics/mkFabric_*.bsv` | `mkHobbitBusMaster` / `mkHobbitBusMemStub` / `mkHobbitBusMem` (`HobbitBus.bsv`); PRM Appendix A signals and protocol; `mkHobbitMemBus` is the core's existing word port over the bus |
| Interrupts, timers | `PLIC/PLIC*.bsv` | `mkHobbitTimers` (`HobbitTimers.bsv`): TIMER1/TIMER2 and their level-one requests; the event/interrupt sequence is still plan.md step 6 |
| JTAG | `src/JtagTap.bsv`, `JtaggDtm.bsv` | not modelled |
| Board clock/reset | `src/ClockHacks.bsv`, `src/ULX3S_Top.bsv` | `hobbit/fpga/HobbitUlx3sTop.v` + `mkHobbitUlx3s(rst_n)` |
| UART | `src/Uart_Pins.bsv`, `Uart_DMI_Bridge.bsv` | `mkUartTx`/`mkHriWriter` (self-contained, same boundary: a fabric-side device, not core logic) |

## Rules this note imposes on `hobbit/bsv`

1. **One module per stage**, with a named interface and a registered
   boundary: `enq`/`deq`/`out`, plus an explicit `set_full`-style stall
   where the stage can block. No stage logic inside `mkHobbitCore`'s
   wiring module.
2. **Stalls are signals, not side effects.** A stage that cannot accept
   work says so; the orchestrator wires the signals. (Flute:
   `CPU_Stage1_IFC.set_full`, `server_reset`.)
3. **Multi-cycle datapath is a box.** The stack cache already is one;
   the future MMU and any divider stay boxes with request/response
   interfaces, never combinational sprawl.
4. **The core has no board knowledge.** Clock, reset, UART and LEDs live
   in the board wrapper; the core sees a memory interface and a
   retirement interface (`hriValid`/`hri`) only — the HRI record is this
   machine's trace, the analogue of Flute's `g_pc_trace`/`trace_data_out`
   (`CPU_IFC.bsv`), not part of the datapath.
5. **Every structural claim cites a page** of the January 1993 manual, and
   every Flute-derived convention cites the file above. A convention that
   the manual contradicts is dropped, and the manual wins.
6. **Credits travel with the structure.** Any module whose structure
   follows Flute carries a one-line comment pointing here, and this file
   keeps the copyright, licence and reference-tree commit current.

## The A1 syscall shim's devices are the testbench's, not the machine's

`docs/plan9_syscalls.md` records the syscall contract; this note records
where the A1 shim's pieces live, so that no reader mistakes a harness for
a block of Figure 1-1.

**The machine's part, unchanged.**  A `KCALL` writes the frame
(`*(ISP-12)=src`, `*(ISP-8)=PC`, `*(ISP-4)=PSW`, `ISP -= 16`, PRM p. 3-29),
reads `*(VB+0)` and clears the low PSW half — all in `HobbitCore.bsv`,
and the HRI record of the KCALL shows the frame's first word as its one
architectural write.  The vector page itself is hardware: `HobbitEvents`
reads `VB+0`, `VB+4`, `VB+8`, `VB+12`, `VB+16+4*IL` (Table 1-14).

**The testbench's part.**  `bsv/P9BootTb.bsv` supplies, and nothing in
the core or the event box knows about:

| device | where it lives | what it is |
|---|---|---|
| vector-page contents | `core.eventMemWrite(VB, …)`, a method the core exposes for the MMU/event testbenches ("the machine never calls these") | the tests substitute a handler address for the kernel's `_vectors` word |
| the stub | `tools/p9shim.py` assembles it, the loader pokes it into `0x1000..0x101f` (the Exec header, below the text) | ordinary Hobbit parcels, fetched through the same prefetch window |
| the doorbell | `mem[ISP-12]`, polled and cleared by the testbench | the KCALL's own `src` word, i.e. architectural memory the hardware wrote |
| the result | `mem[RES]` then `mem[RDY]`, two words of the device page written by the testbench | the stub reads them as absolute operands — ordinary memory operands, fetched through the core's one memory read port |
| the interrupt stack top | `core.setIsp(0x0d00)` | the kernel's job in a real boot (`raml.s:16`) |
| the user PSW restore | `core.setPsw(savedPsw)` when the handler returns | what `KRET` would do; the model has no KRET |
| the file table, the console, `write`/`read`/`open`/`close` | the testbench and `tools/p9shim.py` | the kernel side the shim replaces |

**The rule this keeps.**  A testbench device may not add architectural
state: everything a shimmed run retires is a parcel the machine executed,
and the HRI stream is the same interface the smoke and golden tests use.
The only testbench writes that survive into the trace are the ones the
manual assigns to hardware (the frame, the PSW bits) or to the loader
and the kernel (memory and the vector page).  The host puts a *data*
value into the machine the way a kernel does, by writing memory: the
p. 1-5 off-chip operand path is in the core (`docs/conformance_1to1.md`
§1a), not in a harness device.

## The A2 host testbench, and who owns the memory read port (2026-11-20)

`bsv/P9HostTb.bsv` runs a 1st Edition Plan 9 process on the core with
the kernel's side *replayed* from the reference run
(`docs/plan9_syscalls.md`, last section).  Its pieces, by the same rule
as above:

| piece | where it lives | what it is |
|---|---|---|
| memory | `bsv/p9host.c` behind `mkP9HostMem`, an ordinary `HobbitMem` (one registered read, one write) | a sparse 32-bit store, so the process keeps its real addresses; two rules own it in a fixed order (`fetch`, then `commit`), because bsc cannot schedule C state |
| vector table | `core.eventMemWrite`, from the recording's boot memory | as for A1 |
| the two stubs | boot memory at 0x0c40, assembled by `asm/hobbit_asm.py` | ordinary parcels the machine executes |
| the kernel | `tools/p9run.py`, recorded; `p9host.c` checks the machine's id and arguments against the recording and returns the recorded result | the one kernel, replayed |
| KRET's PSW and ISP | `core.setPsw`, `core.setIsp`, once per system call | the model has no KRET |

Two structural rules came out of building it, and they are rules for the
core as much as for testbenches:

**The memory's read port has one owner.**  `HobbitMem` has a single
registered read address.  The stack-cache box used it for CATCH refills
and operand fetches, and the prefetch buffer used it for fills, each
from its own rule.  bsc composed the two rules with one `readReq`
*shadowing* the other (warning G0117) -- legal Bluespec, and wrong: the
loser read the winner's word.  The box now owns the port outright and
lends it through `MemPort` (`HobbitTypes.bsv`): a second user asks
(`req`) and is told a clock later whether the word on the port is its
own (`live`).  Priority: refill, operand, prefetch.

**A rule that fires every clock must not be scheduled against the
pipeline.**  A testbench rule that polls every clock and calls an Action
method of the core conflicts with the pipeline's rules, wins (it is the
"more urgent"), and starves them on every clock; bsc reports it as
G0010 and builds the frozen machine anyway.  The poll reads only and
signals through a wire.  The same hazard inside the core was the
operand-latch rule against `move2to3` with events on (G0009), fixed by
making `start`'s latch clear a toggle the latch rule reads.

## Simulators: Bluesim and Verilator (2026-11-23)

The model runs on two simulators, built from the same BSV:

| | Bluesim | Verilator |
|---|---|---|
| A2/A3 host testbench | `bsv/run_p9host.sh` (`sim_p9host`) | `bsv/run_p9host_vl.sh` (`sim_p9host_vl`, built by `bsv/build_p9host_vl.sh`) |
| golden testbenches | `bsv/run_golden.sh NNN` | `HOBBIT_SIM=verilator bsv/run_golden.sh NNN` |
| the whole A2/A3 list | `tests/run_p9host_tests.sh` | `P9HOST_SIM=verilator tests/run_p9host_tests.sh` |

`run_p9host_vl.sh` is `run_p9host.sh` with `P9HOST_SIM=verilator`: the
same arguments, environment (`P9CWD`, `P9HOST_KEEP_SIM`, `P9KCLOCKS`,
`P9UNMAPPED`), work directory, comparison and exit status.
`P9HOST_WORK` moves the work directory for either, so the two can run
side by side.  Toolchain: Verilator 5.052 (Homebrew), bsc 2026.01.

**Equivalence.**  On every run checked, the two simulators print the
same `core.log` byte for byte -- every HRI line with its `cyc`, every
`P9HOST` line, in the same order -- and write the same files (a scratch
script, 2026-11-23): echo, cat trap.c, za main9.s, za hello.s, zl, the
linked hello, and zc frexp.c (1,652,549 HRI lines).  `tests/run_tests.sh`
re-checks this on zc frexp.c after the Bluesim steps.  The goldens
001-006 and 013-021 print the same output on both and pass their
hand-derived traces on Verilator.

**Speed** (zc frexp.c: 12,016,397 clocks, 1,651,700 retirements; the
same recording on both; machine at load average ~180, 2026-11-23):

| | wall | CPU (user+sys) | retirements per CPU second | clocks per CPU second |
|---|---|---|---|---|
| Bluesim | 136.7 s | 46.8 s | 35,300 | 257,000 |
| Verilator | 36.4 s | 13.5 s | 122,000 | 890,000 |

About 3.5 times faster.  At that rate the 1e kernel's boot (~22.5M
instructions) is ~3 CPU minutes on Verilator and the kernel link (351M)
~50.  Building `sim_p9host_vl` takes ~30 s.  A third of Verilator's time
in the first measurement was `getenv` in `p9host.c`'s `init`, called on
every C call before its "already done" test; that is fixed, for Bluesim
too (the Bluesim figure above is with the fix).

**What the Verilog path needs, and why** (`bsv/build_p9host_vl.sh`):

1. *One module.*  bsc puts each module's C calls (`p9h_read`,
   `p9h_poll`, ...) and `$display`s in that module's own
   `always @(negedge CLK)` block, in schedule order *within* the block;
   the order *between* two blocks is the simulator's.  With
   `mkP9HostMem` synthesized separately, memory writes were lost (the
   memory's block called `p9h_write` before the testbench's block had
   computed the write enable).  `-D P9HOST_FLAT` drops that module's
   `(* synthesize *)` (`P9HostTb.bsv`), so every C call is in one block,
   in the order Bluesim runs them (poll, fetch, ..., commit).  Bluesim
   builds without the flag.  The rule for later testbenches: C state
   touched from two synthesized modules is not portable to Verilog;
   inline them.
2. *`--no-timing`.*  bsc follows each C call with `#0` and computes,
   inside the block, every value a later statement needs, so ignoring
   the `#0`s changes nothing.  Honouring them (`--timing`) did not work:
   Verilator then did not re-evaluate continuous assignments that read
   what the block wrote after a resumption (the stack cache's CATCH test
   saw a stale MSP comparison and a refill never started).  Found by
   comparing VCDs of Verilator, Bluesim and Icarus Verilog (bsc
   `-vsim iverilog`, which matched Bluesim's output byte for byte).
3. *`$finish` stops at once.*  Bluesim runs no rule after `$finish`;
   Verilator's default lets the rest of the block run (one extra HRI
   line) and prints `- file:line: Verilog $finish`, so `bsv/vl_main.cpp`
   defines `vl_finish` to flush and exit.
4. *Exit status.*  Verilog's `$finish(n)` is a diagnostic level, not a
   status.  `vl_main.cpp` wraps `p9h_poll` (`p9host.c` is compiled with
   `-Dp9h_poll=p9h_poll_c`, otherwise unchanged) and exits 0 exactly
   when P9HostTb.bsv's `ok` holds: exits reached and the recording
   fully served.
5. `bsc -verilog -use-dpi` emits the BDPI imports as `import "DPI-C"`;
   `Bit#(32)` is `int unsigned`, i.e. `p9host.c`'s `uint32_t`, so no
   signature changes.

Differences that remain, none visible in any output: register values
that are don't-cares in BSV can differ (the payload of an `Invalid`
`Maybe`, e.g. `sc_memLiveR`, reads `'hAAAAAAAA` in Bluesim and 0 in
Verilator).  The Verilator build keeps its own `-bdir`
(`build/verilator/`), because `.bo` files do not record `-D`.

