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
   from the core, computes the same record in one step. The two are
   diffed field by field, so pipeline depth, folding and cache timing
   never enter the check; hand-derived golden traces, also written from
   the manual, break ties when the two disagree. The exact line format
   and field meanings are fixed in `sem/README.md` and the checker.
   The one-instruction model is explicitly **not** a second opinion from
   the same author: it is kept independent of `bsv/` and `asm/`.

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
6. Implement event processing in the documented priority order
   (printed p. 1-40): reset, interrupts, trace, instruction fetch
   faults, illegal instructions, unimplemented instructions and
   trapped niladics, unimplemented registers, alignment faults, bus
   errors, privilege violation, divide by zero — with PC and PSW saved
   on the interrupt stack at the documented addresses, and the PSW
   trace bits.
7. Implement the bus: synchronous one-cycle transactions, byte marks,
   double-word/quad-word block transfers, retry and bus-error
   handling, arbitration, the reset start address 0x0, and the
   big-endian/little-endian selection for user and kernel modes. Add
   the two timers.
8. Only then add board-level models required by an original program:
   the dual-Hobbit BeBox prototypes with their DSP3210s, or the EO
   personal communicator support chips.

## Definition of the first milestone

The architectural inventory covers Table 3-1 completely and every
parcel form; the assembler round-trips the manual's printed encodings
bit-exactly and the disassembler reproduces the encoding tables; and a
one-core Bluesim smoke test starts at 0x0, runs a stack-cache call,
return and CATCH sequence, executes a folded conditional branch both
taken and not taken, and traps an unimplemented parcel observably — and
the core's HRI retirement records for that run agree, field by field,
with the independent one-instruction model and with a hand-derived
golden trace. The full repository test suite remains green.
