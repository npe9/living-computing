# AT&T 92010 Hobbit reproduction plan

## Scope

Build a cycle-accounted ATT92010 core: parcel decoding and the
memory-to-memory execution model with the 64-register stack cache and
integer accumulator; the instruction supply path (3 Kbyte three-way
prefetch buffer cache, prefetch/decode unit, 32-entry decoded
instruction cache, static prediction and branch folding); the MMU with
paged and non-paged segment tables and split text/data TLBs; event
processing (reset, interrupts on the interrupt stack, exceptions,
unimplemented instructions, trapped niladics, tracing); the timers; and
the synchronous bus with byte marks, block transfers, retry and bus
error. The ATT2100 variant, the CRISP ancestor, the DSP3210 companions
and the BeBox/EO board hardware are outside the initial scope unless a
documented program or diagnostic needs them, and then only behind
documented interfaces.

## Evidence gates

1. Acquire checksummed AT&T manuals, data sheets, errata and assembler
   or toolchain documentation, and record every silicon and document
   revision. The initial corpus is the January 1993 Programmer's
   Reference Manual, the December 1992 Advance Data Sheet, the March
   1991 ATT2100 Hardware Specification, and the February 1992
   Microprocessor Report article. The Programmer's Reference Manual and
   the data sheet must be checked against each other page by page; the
   1991 specification documents an earlier part whose register set and
   floating-point status differ, and those differences stay revisioned
   facts, not reconciliations.
2. Inventory every parcel format, opcode and subcode, smode/dmode
   encoding, control-register bit, stack-cache and accumulator rule,
   segment and page table entry, event sequence, bus transaction and
   timing number. Every encoding and timing cites a printed page.
   Table 3-1 (printed pp. 3-1 to 3-2) lists 46 mnemonic entries,
   counting the accumulator (`[3]`) forms and the four conditional
   jumps as one entry each; that count is the coverage measure.
3. Obtain a bit-exact oracle, in three tiers that must stay
   distinguished. First, the manual's printed encoding tables
   (Tables 1-15 to 1-20, printed pp. 1-22 to 1-25) plus the assembler
   syntax printed with each instruction description and every control
   register; the assembler must reproduce those bit patterns and the
   disassembler the tables. Second, Bell Labs' own Plan 9 1st Edition
   Hobbit toolchain, vendored in `tools/plan9-1e` with the provenance
   and checksums in `tools/README.md`: `zl/optab.c` and `zl/asm.c` state
   the encodings in code, and `tools/check_optab.py` already checks
   them against Tables 1-18/1-20 (35 mnemonics, 0 mismatches) and the
   mnemonics against Table 3-1 (45 of 46 entries; `CLRE` absent). It is
   not AT&T Microelectronics' assembler, and the release ships no
   `outcode`, so it constrains encoding, not syntax. Third, an original
   AT&T toolchain or a Hobbit object file from the BeOS DR4 disk
   images preserved by the BeBox community, which would outrank both and
   remains the top acquisition target.
4. Turn Chapter 4's execution times (Tables 4-1 to 4-5, printed
   pp. 4-3 to 4-5), its delay tables (Tables 4-6 to 4-9, printed
   pp. 4-6 to 4-7), and the branch-folding rules
   (printed p. 4-7, including the three instruction classes a branch
   will not fold into) into an explicit timing table. Where the data
   sheet and the Programmer's Reference Manual give different clock
   and power points, keep both as named operating points.
5. Verify semantics the way riscv-formal verifies a RISC-V core, not by
   trusting the model's own tests. The core exposes the HRI (Hobbit
   Retirement Interface, the Hobbit counterpart of riscv-formal's RVFI)
   retirement record for every retired instruction — pc, the first two
   parcels, SP and MSP before and after, the architectural word write
   (stack-cache-resident writes included), and the trap flag — and an
   independent one-instruction model, written from the manual and never
   computes the same record in one step. The two are diffed field by
   field, so the *architectural state* comparison never depends on
   pipeline depth; the one timing field, `cyc`, is checked separately by
   gate 6. Hand-derived golden traces, also written from the manual,
   break ties when the two disagree. The exact line format and field
   meanings are fixed in `sem/README.md` and the checker.
   The one-instruction model is explicitly **not** a second opinion from
   the same author: it is kept independent of `bsv/` and `asm/`.

6. Be cycle-accurate, not fast. The owner's priority is the original's
   structure and cycle counts; wall-clock speed and FPGA Fmax are not
   goals. Every HRI record therefore carries `cyc`, the instruction's
   occupancy measured at retirement (a *correctly predicted* folded
   branch costs 0, p. 4-3; a compare-adjacent mispredicted one costs 3,
   Table 4-35 p. 4-5, and retires as its own record after the compare),
   and the core's cycle counts must equal what the printed Chapter 4
   tables state under their own p. 4-1 assumptions. The document prints
   no values for the memory terms A, D and Q (p. 4-2), so the model
   chooses A=1, D=2, Q=4 (one cycle per 32-bit word) and labels these as
   choices, never as manual facts; ENTER is 1 + Q·E with E the number of
   16-byte blocks the pp. 3-19/3-20 flush loop moves. Where the present
   structure cannot retire an instruction in the documented number of
   cycles, the structure is what gets fixed — the counter is never
   adjusted to make a test agree.

## Staged implementation

1. Implement a parcel-level assembler and disassembler: one-, three-
   and five-parcel forms, smode/dmode, the `[3]` accumulator forms,
   `%SHAD` and the control-register `CPU` escape, and all addressing
   modes. Test round-trip and bit-exact agreement with the printed
   encoding tables and with `tools/plan9-1e/sys/src/cmd/zl/optab.c`,
   plus malformed and truncated parcel streams.
2. Model the instruction supply as separate Bluespec modules — prefetch
   buffer cache, prefetch/decode unit, decoded instruction cache with
   next-PC and alternate-next-PC fields — and the execution unit as its
   own module, connected by a small orchestration rule. Static
   prediction and folding first (behaviour), then the Chapter 4
   timings. Unsupported parcels and niladics stop loudly.
3. Expose the HRI retirement record from step 2's core and add
   the independent one-instruction model (`sem/`) and the trace differ
   (`tests/hri_check.py`). Land the hand-derived golden traces with it
   and require three-way agreement — core, spec, golden — before any
   further instruction is added. An instruction is "implemented" only
   when all three agree on its record.
4. Implement the stack cache and integer accumulator as a stateful box:
   the SP/MSP circular buffer, quad-word flush and refill on ENTER,
   CATCH, RETURN and POPN, the CSP-is-ISP exception, and the
   documented stack-cache precautions (vector table, translation
   tables and text must not lie between SP and MSP).
5. Implement the MMU: 1,024 segments of 4 MB, paged segments of
   1,024-word pages, non-paged segments, mixed segment tables, split
   TLBs, FLUSHPTE and the translation faults.
   **Achieved 2026-11-19** (`bsv/HobbitMmu.bsv`, `run_mmu.sh` 41 PASS):
   both entry formats (Table 2-1/2-2), the PTE R/M writeback, the
   text/data TLBs, `FLUSHPTE` and STB-based flushes, and fetch/read/
   write faults as Table 1-26 ids 0x7/0x8/0x9. Named choices: round-robin
   replacement (the manual prints no policy) and a combinational walk
   (Table 2-4's penalties are bus timing, step 7).
6. Implement event processing in the documented priority order
   (printed p. 1-40): reset, interrupts, trace, instruction fetch
   faults, illegal instructions, unimplemented instructions and
   trapped niladics, unimplemented registers, alignment faults, bus
   errors, privilege violation, divide by zero — with PC and PSW saved
   on the interrupt stack at the documented addresses, and the PSW
   trace bits.
   **Achieved 2026-11-19** (`bsv/HobbitEvents.bsv`, `run_event.sh`
   41 PASS; core integration `run_core_mmu.sh` 12 PASS): the priority
   order is tested as an order, frames and vector offsets come from
   Table 1-14/1-26, and a translated fetch fault in the core raises the
   event with the recorded saved PC/PSW. Not yet wired: TBB branch
   tracing, and returning from an event (CRET/KCALL/KRET); event frames
   live in their own model memory rather than through the bus.
7. Implement the bus: synchronous one-cycle transactions, byte marks,
   double-word/quad-word block transfers, retry and bus-error
   handling, arbitration, the reset start address 0x0, and the
   big-endian/little-endian selection for user and kernel modes. Add
   the two timers.
   **Achieved 2026-11-19** (`bsv/HobbitBus.bsv`, `run_bus.sh` 76 PASS;
   `bsv/HobbitTimers.bsv`, `run_timer.sh` 31 PASS): the printed Appendix A
   pins and protocol, byte/half/word and block transfers with `BE`/`IOC`,
   `RETRY`, `BERR`, `HOLD`, the `BREQ`/`BGRANT`/`BGACK` handshake and
   both byte orders, with memory behind the bus through the existing
   `HobbitMem` word port. The manual prints `BGRANT`, not `RC`. Not
   modelled: automatic retry/resume, the RMW dead cycle, and loopback.
8. Only then add board-level models required by an original program:
   the dual-Hobbit BeBox prototypes with their DSP3210s, or the EO
   personal communicator support chips.
9. Run the core on real silicon. The ULX3S (Lattice ECP5 85F) is a
   modern host, not a replica of any historical machine: it exists to
   show that the same image, the same parcels and the same HRI records
   work outside Bluesim. `fpga/build.sh` runs bsc → yosys → nextpnr →
   ecppack; the program is `bsv/smoke.hex` embedded through the same
   generator the simulator uses; the eight LEDs show state and the FTDI
   UART streams the HRI lines at 115200 so a captured log can be diffed
   with `tests/hri_check.py`. Timing closure at 25 MHz is a number the
   report quotes from nextpnr, never an assumption.
   **First achieved 2026-11-19**: `TRELLIS_COMB 18,041/83,640 (21%)`,
   `TRELLIS_FF 5,066 (6%)`, `DP16KD 18/208`, 25.66 MHz at the 25 MHz
   target, `fpga/build/hobbit_ulx3s.bit` (593,803 bytes).
   **Second achieved 2026-11-19**: the UART path itself is now proven,
   not assumed. `bsv/BoardUartTb.bsv` mirrors the board top's datapath
   (image load, prefetch warm-up, start at SP = 0x100 / MSP = 0x180, the
   48-deep BRAM retirement queue, the HRI writer) and decodes its `txd`
   line as 8N1 at 217 clocks/bit, mid-bit. `bsv/run_board_tb.sh` runs
   that and the smoke test and requires the decoded text to equal the
   smoke's 41 HRI lines byte for byte: 41 lines, 5,042 characters,
   identical. It is in `tests/run_tests.sh`. What remains here is a
   capture from physical hardware (no board attached here), and the
   historical BeBox/EO board models.

## Formal verification (owner's question, 2026-11-19)

The functional plan above does **not** lead to formal proof by itself:
verification here is HRI trace comparison and hand-derived goldens, and
no proof harness exists in the tree. The formal track — instruction
equivalence against a mechanised sem contract, structural invariants,
MMU/event order, device contracts, and bounded boot reachability, with
bounds and artefacts recorded — is
[`docs/plan9_formal_plan.md`](docs/plan9_formal_plan.md), and every
boot-plan milestone must ship its formal harness with it.

## Booting Plan 9 1e (owner's direction, 2026-11-19)

**Get 1e booting and printing on the UART, then support every device the
1e Hobbit port drives.** The staged plan, its gates and the device
inventory are in [`docs/plan9_boot_plan.md`](docs/plan9_boot_plan.md);
the immediate work is A0 (run 1e user code to its first syscall), A1
(the syscall shim) and A2 (bootstrap `za`/`zl` on the model), after
which the kernel is assembled and linked from `sys/src/9/hobbit` and
booted (A3, A4).

## Definition of the first milestone

The architectural inventory covers Table 3-1 completely and every
parcel form; the assembler round-trips the manual's printed encodings
bit-exactly and the disassembler reproduces the encoding tables; and a
one-core Bluesim smoke test starts at 0x0, runs a stack-cache call,
return and CATCH sequence, executes a folded conditional branch both
taken and not taken, and traps an unimplemented parcel observably — and
the core's HRI retirement records for that run agree, field by field —
including `cyc`, so the state and the documented cycle counts agree
separately — with the independent one-instruction model and with a
hand-derived golden trace, and the same image runs on the ULX3S with its
HRI lines streamed over the UART. The full repository test suite remains
green.

## Proof of concept: a Plan 9 port (owner's direction, 2026-11-19)

The proof of concept for this machine is **a Plan 9 port, not a smoke
test**. The 1st Edition of Plan 9 — the last release with the Hobbit
port — shipped complete Hobbit binaries (`hobbit/bin/`: `za`, `zc`,
`zl`, `rc`, `echo`, `cat`, `ls`, `sam`, …), the Hobbit kernel sources
(`sys/src/9/hobbit/`, including `_vector0`, the syscall entry at
`_vectors+0x00`) and the Hobbit libc (`sys/src/libc/hobbit/main9.s`).
Those binaries are Bell Labs' own compiled user code for this chip.

The proof of concept is: **`echo` from `plan9-1e/hobbit/bin/` runs on
the model and prints its argument over the model's UART byte for byte,
and exits 0**, followed by one file-reading program (`cat` over a
one-file shim). The loader, the `_main` start-up convention and the
syscall vector come from the 1st Edition sources, cited by path and
line; the syscalls themselves are a host shim, not the kernel — booting
`sys/src/9/hobbit/` is the milestone after that. Stages, gates and
negative controls are in [`docs/plan9_port.md`](docs/plan9_port.md).

The Plan 9 way of working applies throughout: nothing is added to the
instruction set and nothing to the toolchain for the port's sake — what
is needed is hand-assembled in the assembler's own idiom (`TEXT`/`DATA`
and macros with the parcels spelled out) and linked by `zl`, which is
also this machine's encoder oracle.

Until the 1e material is vendored, its archive is pinned by
sha256 `8718e279aa35b10a9391f330976d31c177bad00de40e7f0f67232ffa54fb7d77`
(`plan9-1e.tar.bz2`), the same archive `tools/plan9-1e/` was taken from.
