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
| the release | `core.setPsw(savedPsw \| PSW_F)` | `PSW.F` is the one host-writable bit the machine reads (`JMPFN`) |
| the interrupt stack top | `core.setIsp(0x0d00)` | the kernel's job in a real boot (`raml.s:16`) |
| the user PSW restore | `core.setPsw(savedPsw)` when the handler returns | what `KRET` would do; the model has no KRET |
| the file table, the console, `write`/`read`/`open`/`close` | the testbench and `tools/p9shim.py` | the kernel side the shim replaces |

**The rule this keeps.**  A testbench device may not add architectural
state: everything a shimmed run retires is a parcel the machine executed,
and the HRI stream is the same interface the smoke and golden tests use.
The only testbench writes that survive into the trace are the ones the
manual assigns to hardware (the frame, the PSW bits) or to the loader
(memory and the vector page).  If a future milestone needs the host to
put a *data* value into the machine, that is the p. 1-5 off-chip operand
path (`docs/isa_inventory.md` §1.6), a core change, not a harness
device — and it must be made in `HobbitStackCache`/`HobbitCore`, with the
HRI record extended to show it.
