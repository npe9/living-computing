# AT&T 92010 Hobbit (1993)

The AT&T 92010 Hobbit, the second-generation implementation of Bell
Laboratories' CRISP (C-language Reduced Instruction Set Processor)
architecture, is a 32-bit memory-to-memory microprocessor with no
programmer-visible general registers. The top of the stack lives in a
64-register, 256-byte on-chip stack cache that the hardware allocates
as the stack grows, so operands are named by stack offsets or memory
addresses and the compiler does no register allocation. Instructions
are built from 16-bit parcels and encode in one, three or five parcels
(2, 6 or 10 bytes); the one-parcel form is restricted to the 32 opcode
and addressing-mode combinations that frequency analysis of compiled
UNIX C source found most common. A static prediction bit per
conditional jump and branch folding — the branch target is stored in
the next-address field of the preceding decoded instruction — remove
the branch penalty.

The chip integrates a 3 Kbyte three-way set-associative prefetch buffer
cache, a 32-entry decoded-instruction cache, dual 32-entry TLBs for text
and data, and an MMU with paged and non-paged segments; it consumes
250 mW at 3.3 V and 20 MHz and runs from 5 V at 30 MHz, in a 132-pin
PQFP on 0.9 µm double-level-metal CMOS. It was built for pen-based
"personal communicators": Apple paid AT&T to develop the low-power
second-generation CRISP for the Newton and then shipped the Newton on
ARM instead, EO chose the Hobbit for its personal communicators, and
Be, Inc.'s original BeBox was a dual-Hobbit machine with three DSP
chips until AT&T cancelled the Hobbit line and Be moved to PowerPC.
This directory fixes the ATT92010 as the target; the earlier ATT2100
hardware specification (March 1991) and the CRISP ancestor are related
machines whose differences must remain explicit.

## Status

| piece | where | evidence |
|---|---|---|
| parcel assembler + disassembler | `asm/` | 18 unittest checks, bit-exact against Tables 1-15…1-20, cross-checked with Plan 9's encoder |
| architectural inventory | `docs/isa_inventory.md` | all 46 Table 3-1 entries, each with a printed-page cite |
| Chapter 4 timing table | `docs/timing.csv`, `docs/timing_tables.md` | 46/46 spellings covered; `tools/check_timing.py` |
| one-instruction semantics model | `sem/` | written from the PRM, independent of `bsv/` and `asm/`; now also MUL/MUL3, DIV/DIV3, REM/REM3, UDIV, UREM, ADDI/ANDI/ORI, TADD/TSUB, DQM, MOVA, LDRAA, CLRE, KCALL/KRET/CRET and the five-parcel forms, with 27 unit tests (`tests/test_sem_extended.py`) and explicit refusals where the manual is silent (divide by zero, DQM's `8·S` cell) |
| Bluesim core | `bsv/` | 30-check smoke test (behaviour + cycles), `run_smoke.sh`; PDU → decoded-instruction store → EU, stack cache as a stateful box |
| Verilator build | `bsv/run_p9host_vl.sh`, `HOBBIT_SIM=verilator bsv/run_golden.sh` | same HRI output as Bluesim byte for byte (cyc included) on the A2/A3 runs and the goldens; ~3.5× faster (`docs/bluespec_architecture.md`, "Simulators") |
| cycle accuracy | `cyc` in every HRI record | Tables 4-32…4-36 under the p. 4-1 assumptions; A/D/Q are named model choices, not printed values |
| hand-derived golden programs | `tests/golden/` | twelve programs, 56 retirement records, each line and each cycle figure justified by a printed page; 001–006 run on the core and the model, 007–012 on the model only (the core does not yet implement those instructions) |
| HRI retirement interface and differ | `bsv/`, `sem/`, `tests/hri_check.py` | the Hobbit counterpart of riscv-formal's RVFI (RVFI itself means *RISC-V* Formal Interface) |
| UART HRI stream | `bsv/HobbitUart.bsv` | 9-check testbench, byte-exact variable-length lines at 115200 |
| ULX3S target (ECP5 85F)|`fpga/`|bitstream produced: 22,034/83,640 `TRELLIS_COMB` (26%), 5,074 FF (6%), 645,118 bytes; clock domain 34.64 MHz (PASS at 25 MHz), asynchronous input to clock 29.95 ns; same `smoke.hex`, HRI lines over the UART|
| MMU|`bsv/HobbitMmu.bsv`|1,024 × 4 MB segments, paged/nonpaged/mixed tables, 2 × 32-entry TLBs, 2 NPSRs, R/M writeback, `FLUSHPTE`; `run_mmu.sh` 41 PASS|
| event processing|`bsv/HobbitEvents.bsv`|the p. 1-40 priority order, interrupt stack frames, the VB vector offsets; `run_event.sh` 41 PASS|
| core + MMU + events|`bsv/HobbitCore.bsv`, `mkHobbitCoreMmu`|a translated fetch fault raises the event sequence with the printed vector; `run_core_mmu.sh` 12 PASS|
| synchronous bus | `bsv/HobbitBus.bsv` | PRM Appendix A: `START`/`DTACK` one-clock transactions, `BE[3:0]`, double/quad block transfers, `IOC[1:0]`, `RETRY`, `BERR`, `HOLD`, `BREQ`/`BGRANT`/`BGACK`, `NCACHE`, `LOCK`; memory sits behind the bus; 76-check `run_bus.sh` |
| TIMER1/TIMER2 | `bsv/HobbitTimers.bsv` | p. 1-19 counters, CONFIG[31:22] event/enable fields, level-one overflow interrupts, CPU-escape reads 0xB/0xC; 31-check `run_timer.sh` |
| board UART end to end | `bsv/BoardUartTb.bsv`, `bsv/run_board_tb.sh` | the board datapath's `txd` decoded as 8N1 at 217 clocks/bit yields the smoke's 41 HRI lines byte for byte (5,042 characters) |

The goal for this machine is **full functional completeness and
provability** (`docs/plan9_formal_plan.md`): every documented feature
implemented and every claim proved for all executions, so the core's
remaining refusals are defects to be closed, not a design stance. What it
models today: the memory-to-memory ALU, the stack cache, the control
transfers, the MMU, the event sequence, the synchronous bus and the
timers. The one structural gap left from the printed
Figure 1-1 is the 3 Kbyte three-way prefetch buffer: a 64-word
direct-mapped window stands in (see `plan.md`). The board bitstream runs
`mkHobbitCore` with translation and events off, so the MMU and event
boxes are exercised in Bluesim rather than on the ECP5.

Every instruction the core claims to implement is checked three ways by
`tests/run_tests.sh`: the core's HRI record, the independent
one-instruction model's record, and a hand-derived golden trace must all
agree field by field — and the `cyc` field makes the documented cycle
count part of that agreement.

See [`plan.md`](plan.md) for the evidence gates and staged model.
The primary-source acquisition manifest is [`docs/README.md`](docs/README.md).
Plan 9's 1st Edition Hobbit toolchain is vendored, with its checks and
its limits, under [`tools/`](tools/README.md). The architectural
inventory — every Table 3-1 mnemonic, every parcel form, the control
registers, the stack cache, the MMU and the event priority, each with a
printed-page citation — is [`docs/isa_inventory.md`](docs/isa_inventory.md).

Architecture conventions follow **Flute**, Bluespec Inc.'s RISC-V SoC
(© 2021 Rishiyur S. Nikhil and Bluespec, Inc., Apache-2.0) — structure and
interface shape only, no Flute code; see
[`docs/bluespec_architecture.md`](docs/bluespec_architecture.md) for the
mapping, the credits and the reference-tree commit.

Sources: AT&T Microelectronics, *ATT92010 Hobbit Microprocessor
Programmer's Reference Manual* (January 1993); *ATT92010 Hobbit
Microprocessor Advance Data Sheet* (December 1992); AT&T, *ATT2100
Microprocessor Hardware Specification*, release 1.7.2 (31 March 1991);
M. Slater, "AT&T Sampling Low-Power 'Hobbit' Processor", *Microprocessor
Report* 6:2 (12 February 1992); S. Horowitz, "'Our' Toy Story", *Be
Newsletter* 3 (20 December 1995).
