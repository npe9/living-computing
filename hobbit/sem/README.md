# `hobbit/sem` — an independent one-instruction model of the ATT92010

`hobbit_sem.py` is the specification side of the repository's HRI
(Hobbit Retirement Interface) check.  HRI is the Hobbit analogue of
riscv-formal's RISC-V Formal Interface (RVFI): a fixed per-instruction
retirement record.  The check is a **per-instruction trace comparison**
against the Bluespec core — the two records are diffed field by field —
**not a formal proof**.

One call to `step(state, memory_reader)` computes the architectural
effect of **exactly one** instruction from an architectural pre-state.
There is no pipeline, no prefetch buffer, no decoded-instruction cache,
no branch folding, no cache-fill timing and no cycle count: those belong
to the core side of the check.  The record the model returns is the
`HRI ...` line the Bluespec core must reproduce field for field.

The model was written from the printed *ATT92010 Hobbit Microprocessor
Programmer's Reference Manual* (January 1993) and from nothing in
`hobbit/bsv` or `hobbit/asm`.  It is deliberately a second, independent
statement of the semantics, not a translation of the core.

`p. 1-21` below means the manual's own printed folio, Chapter 1, page 21.
The scan's PDF page is printed + 8 for Chapter 1, + 58 for Chapter 3.

## Running it

```sh
python3 hobbit/sem/hobbit_sem.py --image hobbit/sem/demo.s \
    --sp 0x100 --msp 0x180
```

`demo.s` is both the listing and the image; the loader ignores everything
from a `#` onward.  `demo.trace` is the exact output of the command
above.  `--max-steps N` bounds a program that does not stop (default
10000).  `--stop-at-image-end` is on by default: the run stops when the
next PC equals the image length in bytes, without executing the zero
words past the end (adjudication convention C1; `--no-stop-at-image-end`
turns it off).  Execution also stops on the unimplemented-instruction
`trap=1` line, or on a `Refusal`, which is reported on stderr with no
HRI line (convention C2).

### Image format

Text, one 32-bit word per line, eight hex digits, ascending addresses
starting at 0.  The parcel at an even address is in bits 31:16 and the
parcel at the following odd address in bits 15:0 (big-endian, PRM
Figure 1-2, p. 1-4).  Entry is at 0.  A missing instruction word is a
fetch fault and therefore a `Refusal` (no HRI line); a data read from an
address the image does not contain reads 0 (a modelling choice, since
the PRM does not define the value of uninitialised memory).

### Fixed output line

```
HRI pc=%04x insn=%04x%04x sp=%08x>%08x msp=%08x>%08x we=%d addr=%08x data=%08x mask=%02x trap=%d
```

All hex is lowercase.  `%04x` is a minimum width, so a PC beyond 0xFFFF
prints more than four digits.  One HRI line is printed per retired
instruction and for the unimplemented-instruction `trap=1` line.  A
`Refusal` (a fetch fault, an illegal encoding, an alignment fault, a
state limitation, or a legal instruction outside the subset) produces a
`REFUSED pc=... insn=... reason: ...` diagnostic on stderr and no HRI
line, and ends the run (convention C2); it is not compared as a
retirement.

## State

`State` is `pc`, `sp`, `msp`, `psw` and `memory`.

| Field | Meaning | Cite |
|---|---|---|
| `pc` | Address of the instruction to execute; bit 0 is the reserved zero bit and is ignored for fetch | p. 1-13, Table 1-7 p. 1-14, p. 1-4 |
| `sp` | Stack Pointer; inclusive lower bound of the stack cache | p. 1-5, Table 1-10 p. 1-17 |
| `msp` | Maximum Stack Pointer; exclusive upper bound of the stack cache | p. 1-5, Table 1-6 p. 1-13 |
| `psw` | Only bits 6 (V), 5 (C), 4 (F), 11 (E) and 9 (CSP selector) are used | Table 1-8 pp. 1-14..1-16 |
| `memory` | Sparse architectural memory, a dict of word address to 32-bit word | p. 1-4 |

The CLI initialises `psw` to `0x00000200` (CSP = SP, bit 9 set).  The
manual's reset value `PSW = 0` selects the ISP as the current stack
pointer (p. 1-35), which this model cannot represent — it has no
interrupt stack.  The reference pre-state for the demo, and the state
the checker should use, is therefore the explicit `PSW = 0x00000200`.

The model raises `Refusal` (no HRI line) for a state with:

* `psw` bit 16 set (virtual addressing; there is no MMU here, p. 2-1);
* `psw` bit 15 set (user little-endian data; this model is big-endian
  only, p. 1-4);
* `psw` bit 9 clear (CSP is ISP; the interrupt stack is out of scope,
  p. 1-12);
* `SP` or `MSP` not quad-word aligned, `MSP < SP`, or `MSP > SP+256`
  (p. 1-13);
* a stack whose 256-byte cache would cross the 32-bit address boundary.

`psw` bit 10 (execution level) is recorded but not used: every
instruction in the modelled subset is unprivileged.  `SHAD` is not in
the state.  The manual updates it on ENTER/RETURN/CRET/KCALL/KRET/popn
(pp. 1-16, 1-17, 3-19, 3-38, 3-40), but no modelled instruction *reads*
it; it is a restart optimisation, not part of the one-instruction record.
`CONFIG` is fixed at its reset value 0 (p. 1-36): big-endian, no PC
extension, and the cache-enable bits are irrelevant to this subset.

## Memory, byte order and the stack cache

Memory is byte-addressable, 32-bit words, big-endian: address 0 is bits
31:24 (Figure 1-2, p. 1-4).  A byte or half-word load extracts the
addressed bytes; a byte or half-word store is a read-modify-write of the
surrounding word with byte marks.  Word operands must be 4-byte aligned,
half-word operands 2-byte aligned, or the model raises an alignment
exception (p. 1-4).  Instruction fetch ignores bit 0 of the address
(p. 1-4).

The stack cache is 64 words (256 bytes), with `SP` the inclusive lower
bound and `MSP` the exclusive upper bound (p. 1-5).  The model keeps the
`SP`/`MSP` bookkeeping exactly where the manual makes it architectural
(ENTER, CATCH, POPN, RETURN; pp. 1-6, 1-7, 3-10..3-11, 3-19..3-21,
3-38, 3-40) and treats the cache as an ordinary-memory region:

* every architectural write, including a write into `[SP, MSP)`, is
  recorded in `mem_we`/`mem_addr`/`mem_wdata`/`mem_wmask` and is visible
  to the next instruction;
* the model is therefore write-through.  It does **not** represent
  which words are duplicated in the 64 cache registers, and does not
  model the 16-byte flush/refill copies.  Those copies are not
  architecturally observable in this abstraction because the
  backing-memory image already has every byte the cache holds.  Flush
  *timing*, quad-word boundaries and the number of blocks moved are
  abstracted; the `SP`/`MSP` bounds and the `PSW.E` enter-guard result
  are not.
* it does not model memory latency, cache hits or bus cycles.

The integer accumulator (PRM p. 1-7, Figure 1-4; p. 1-3) is **not a
register**: it is the word at `CSP + 4`.  The `[3]` forms write that
address, and the model records that write like any other.  `R4` in the
manual's examples is stack offset 4 (the word above the PC-save slot at
`CSP`), not a fifth register.

## Instructions modelled

The model covers exactly these mnemonics and forms.  Anything else is a
`Refusal` (no HRI line; see “Refused constructs”), except `FLUSHD` and
`FLUSHDCE`, whose unimplemented-instruction sequence is the `trap=1`
line.

| Instruction | Forms implemented | Operation | Cite |
|---|---|---|---|
| `ADD` | 1p `imm5,stk5`; 1p `stk5,stk5`; 3p/5p `gen16/gen32` | `dst += src`; C on unsigned carry, V on signed overflow, both cleared otherwise | p. 3-5; pp. 1-29..1-30 |
| `ADD3` | 1p `wai5,stk5`; 1p `imm5,stk5`; 1p `stk5,stk5`; 3p/5p | `Acc = dst + src`; same flags | p. 3-5 |
| `SUB` | 3p/5p `gen16/gen32` | `dst -= src`; C on unsigned borrow, V on signed overflow | p. 3-43 |
| `SUB3` | 3p/5p | `Acc = dst - src`; same flags | p. 3-43 |
| `MOV` | 1p `wai5,stk5`, `imm5,stk5`, `stk5,stk5`, `istk5,stk5`, `stk5,istk5`, `istk5,istk5`; 3p/5p `gen16/gen32` | `dst = src` | p. 3-32 |
| `CMPEQ` | 1p `imm5,stk5` (`0x10`), 1p `stk5,stk5` (`0x13`); 3p/5p `gen16/gen32` (`0x1F`) | `PSW.F = (src1 == src2)`; src1 is the source field, src2 the destination field; no memory write | p. 3-13 |
| `CMPGT` | 1p `stk5,stk5` (`0x11`), 1p `imm5,stk5` (`0x12`); 3p/5p `gen16/gen32` (`0x1D`) | `PSW.F = signed(src1 > src2)`; no memory write | p. 3-13 |
| `CMPHI` | 3p/5p `gen16/gen32` (`0x1E`) | `PSW.F = unsigned(src1 > src2)`; no memory write | p. 3-13 |
| `TESTC` | 1p niladic `0x0B/0x009` | `PSW.F = PSW.C`, then `PSW.C = 0`; no memory write | p. 3-45 |
| `TESTV` | 1p niladic `0x0B/0x008` | `PSW.F = PSW.V`, then `PSW.V = 0`; no memory write | p. 3-46 |
| `CALL` | 1p `pcrel10`; 3p `flow32` | `*(CSP) = next PC; PC = target` | p. 3-9 |
| `CATCH` | 1p `stk8`; 3p `word32` | fill the cache upward to the operand's target MSP in 16-byte blocks, capped at `SP+256`; no-op when CSP = ISP | pp. 3-10, 3-11 |
| `ENTER` | 1p `stk8`; 3p `word32` | allocate a frame: stack-offset form moves CSP and flushes only the excess above 256 bytes; the other modes replace CSP and empty the cache; sets/clears the E bit | pp. 3-19..3-21 |
| `POPN` | 1p `stk8`; 3p `stk32` | `CSP += src`; `MSP = SP` if the new SP exceeds it; stack-offset mode only, non-negative | p. 3-38 |
| `RETURN` | 1p `stk8`; 3p `stk32` | `PC = *(CSP + src)`, then `CSP += src` (low 4 offset bits ignored for the SP update); MSP as POPN | p. 3-40 |
| `JMP` | 1p `pcrel10`; 3p `flow32` | `PC = &dst` (target) | p. 3-28 |
| `JMPFN`, `JMPFY`, `JMPTN`, `JMPTY` | 1p `pcrel10`; 3p `abs32` (label or absolute only) | T jumps when F=1; F jumps when F=0; Y/N is the static prediction bit and does not change the state | p. 3-28, p. 1-33 |
| `NOP` | 1p niladic `0x0B/0x002` | no operation | p. 3-35 |
| accumulator | implicit destination of every `[3]` form | word at `CSP + 4` | p. 1-7 |

Operand modes implemented (Tables 1-21..1-24, pp. 1-25..1-27):

* all sixteen general modes `0x0`..`0xF`: absolute byte/unsigned byte/
  half-word/unsigned half-word/word, stack-offset byte/UB/H/UH/word,
  stack-offset-indirect byte/UB/H/UH/word, and immediate;
* the one-parcel forms `imm5`, `wai5`, `stk5`, `istk5`, `stk8`;
* `flow32` (Table 1-23) for CALL/JMP: absolute indirect `**$addr`,
  stack-offset indirect `*Roffset`, PC-relative label, absolute `*$addr`;
* `word32` (Table 3-2, p. 3-4) for CATCH/ENTER.

The width of an operand comes from its mode: `0x0/1/4/5/8/9` are bytes,
`0x2/3/6/7/A/B` are half-words, `0xC/0xD/0xE` are words, and `0xF` is an
immediate.  A missing suffix in the manual's syntax means a signed word
(p. 1-28); the model applies sign extension for signed byte and
half-word loads and zero extension for unsigned ones, exactly as p. 1-3
and p. 1-28 describe.

A three-parcel **monadic** instruction (CALL, RETURN, JMP, the four
conditional jumps, CATCH, ENTER, POPN) carries one 32-bit operand in
parcels 2 and 3, `((parcel2 << 16) | parcel3)` (p. 1-23, and `stk32` /
`word32` in Table 3-2, p. 3-4); a three-parcel **dyadic** instruction
carries a 16-bit source in parcel 2 and a 16-bit destination in parcel 3
(p. 1-23).  This model follows the monadic 32-bit rule (the earlier
16-bit reading was the 003/004 defect); the fixed HRI line still shows
only parcels 0 and 1.

### Control flow and the PC

`pc` in the record is the address of the instruction being executed
(p. 1-13), not the next address.  A 1-parcel `pcrel10` field is
sign-extended and multiplied by two (p. 1-21, p. 1-27).  A 16- or
32-bit `Label` field is sign-extended but **not** scaled; p. 1-21 says
only the 10-bit PC-relative fields are multiplied by two.  The target is
`pc + offset`.  A CALL saves `pc + 2` or `pc + 6` for the implemented
one- and three-parcel forms at `*(CSP)` and branches to the target.  A RETURN
reads the new PC from `*(CSP + src)` and then advances the SP; it ignores
the low four bits of the offset when adjusting SP, so `RETURN R20`
reads the PC from `SP+20` but adds only 16 to SP (p. 3-40).  A jump or a
returned PC whose bit 0 is set is fetched with bit 0 ignored (p. 1-4).

## The HRI record

| Field | Definition | Cite |
|---|---|---|
| `pc` | Address of the retiring instruction, or of the unimplemented opcode; bit 0 cleared | p. 1-13, Table 1-7 p. 1-14 |
| `insn0` | First parcel (the first four hex digits of the `insn` field) | p. 1-21, Tables 1-15..1-20 pp. 1-22..1-25 |
| `insn1` | Second parcel (the second four hex digits); 0 for a one-parcel instruction.  A three-parcel monadic operand is the 32-bit `((parcel2 << 16) \| parcel3)` (p. 1-23); the fixed line shows only the first two parcels, so that third parcel is not in `insn` | p. 1-21, p. 1-23, pp. 1-22..1-25 |
| `sp_before` | `SP` before the instruction | p. 1-5, Table 1-10 p. 1-17 |
| `sp_after` | `SP` after the instruction (equal before/after for non-stack instructions) | pp. 3-19..3-21, 3-38, 3-40 |
| `msp_before` | `MSP` before the instruction | p. 1-5, Table 1-6 p. 1-13 |
| `msp_after` | `MSP` after the instruction (CATCH/ENTER/POPN/RETURN change it) | pp. 3-10, 3-19, 3-38, 3-40 |
| `we` | 1 if this instruction performs the one architectural write in the record, else 0 | p. 1-5 (cache appears as normal memory), p. 1-7 (accumulator) |
| `addr` | Word address of that write (`effective address & ~3`) | p. 1-4 |
| `data` | Big-endian bus word for the write: the stored byte(s) in their byte lanes | p. 1-4, Figure 1-2 |
| `mask` | Byte marks of the write, bit 3 = byte at `addr` (bits 31:24), bit 0 = byte at `addr+3` (bits 7:0); a word write is `0f` | p. 1-4 (byte stores), p. 1-5 |
| `trap` | 0 = retired; 1 = the unimplemented-instruction sequence (FLUSHD/FLUSHDCE) with the p. 1-39 store; a `Refusal` produces no line | see below |

The mask convention is fixed here so the model and the core can be
diffed.  It is the big-endian bus convention, not an effective-address
field: for a byte store of `0x11` to address `0x104` the record is
`addr=00000104 data=11000000 mask=08`; for a half-word store of `0x1122`
to `0x106` it is `addr=00000104 data=00001122 mask=03`; a word store of
`0x11223344` to `0x104` is `addr=00000104 data=11223344 mask=0f`.
`step()` returns the same `data` and `mask` as the record, and the core's
HRI record must normalise its bus write the same way.  The alternative
convention — `addr` = the effective byte address and `data` right-aligned
— is not used.

### Traps and refusals

There are two different outcomes, and the adjudication's convention C2
requires that they not be conflated.

**`trap=1` — the unimplemented-instruction sequence.**  Only `FLUSHD`
and `FLUSHDCE` take it (p. 3-22, p. 3-23; both are not implemented in
hardware).  The sequence is (p. 1-39):

```
*(CSP) = PC of the unimplemented opcode;  PC = *(VB+12)
```

The one-instruction model reports the store as the instruction's one
architectural write — `we=1, addr=CSP (before the sequence),
data=PC of the opcode, mask=0x0f` — and stops after that HRI line.  `pc`
stays the opcode's own address (p. 1-13), and `sp`/`msp` are unchanged.
The `VB+12` fetch and the handler are outside a one-instruction model.
The demo's last line and the `006` golden are this case.

**`Refusal` — everything else.**  A fetch fault, an illegal encoding,
an alignment fault, a state limitation, or a legal instruction the model
does not implement is **not** a `trap=1` line.  `step()` raises
`Refusal`; the CLI prints

```
REFUSED pc=%04x insn=%04x%04x reason: <reason>
```

on stderr, emits no HRI line, and stops.  The checker aligns the
remaining records by PC (C4) and does not count the missing record as a
field mismatch; the refusal is outside the comparison, not an
architectural result.  In particular, the remaining legal-but-unmodelled
mnemonics are refusals, not traps, and the
unimplemented-instruction store must never be reused for a fetch fault
(p. 1-38's three-word frame is a different sequence) or a model
limitation.

Reason prefixes: `unsupported:` for a legal opcode/mode the model does
not implement (including CPU/register and exception-processor
constructs), `illegal:` for an encoding the manual calls illegal,
`alignment:` for p. 1-4 alignment faults, `fetch-fault:` for an absent
instruction word, and `unpredictable:` for a state the manual calls
unpredictable (e.g. `MSP < SP`).  `trap=1` and `Refusal` both print a
reason on stderr and exit 0 from the CLI.

## The demo, line by line

`demo.s` is a straight-line program at 0, with a subroutine at 0x020.
The reference pre-state is `PC=0, SP=0x100, MSP=0x180, PSW=0x200,
SHAD=0x100, CONFIG=0`.  The listing comments give the hand encoding;
`demo.trace` is the model output.

| # | PC | Instruction | What the line shows and why | Cite |
|---|---|---|---|---|
| 1 | 0000 | `ENTER R-32` | `SP 0x100→0x0e0`; `MSP 0x180→0x180` because `MSP-target = 0xa0 ≤ 256`, so no flush and E=1; no write | pp. 3-19..3-21, p. 1-15 |
| 2 | 0002 | `MOV $1,R4` | word write `0x0e4 ← 1`, mask `0f`; accumulator slot is CSP+4 | p. 3-32, p. 1-7 |
| 3 | 0004 | `MOV R4,R8` | word write `0x0e8 ← 1` | p. 3-32 |
| 4 | 0006 | `ADD $5,R8` | word write `0x0e8 ← 6`; C=V=0 (the flags are state, not in the line) | p. 3-5, pp. 1-29..1-30 |
| 5 | 0008 | `CALL 0x020` | return PC `0x00a` written at `*(CSP)=0x0e0`, mask `0f`; next PC 0x020 | p. 3-9 |
| 6 | 0020 | `CATCH R192` | no write; `MSP 0x180→0x1a0` (two 16-byte blocks, target 0x0e0+0xc0) | pp. 3-10, 3-11 |
| 7 | 0022 | `MOV $7,R12` | word write `0x0ec ← 7` | p. 3-32 |
| 8 | 0024 | `RETURN R0` | no write; `PC ← *(0x0e0)=0x00a`, SP unchanged (offset 0) | p. 3-40 |
| 9 | 000a | `MOV R8,R4` | word write `0x0e4 ← 6` | p. 3-32 |
| 10 | 000c | `SUB R8,R4` | 3-parcel; word write `0x0e4 ← 0`; C=V=0 | p. 3-43 |
| 11 | 0012 | `POPN R32` | no write; `SP 0x0e0→0x100`; MSP stays 0x1a0 because the new SP is below it | p. 3-38 |
| 12 | 0014 | `JMPTY 0x01c` | no write; F=0 so the T jump is not taken; next PC 0x016 | p. 3-28 |
| 13 | 0016 | `JMPFN 0x01c` | no write; F=0 so the F jump is taken; next PC 0x01c | p. 3-28 |
| 14 | 001c | `NOP` | no write; next PC 0x01e | p. 3-35 |
| 15 | 001e | `FLUSHD` | `trap=1`; the fixed unimplemented save writes PC `0x01e` at `CSP=0x100`, mask `0f`; the model stops | p. 3-22, p. 1-39 |

The one-parcel forms in the trace are `0bf8`, `7021`, `6022`, `50a2`,
`040c`, `6041`, `080b`, `1c04`, `1003`, `2c02`, `2c06`, `0831`, `70e3`,
`0802`; the 3-parcel `SUB` is `a0dd 0008 0004`.  `insn1` is `0000` for
every one-parcel line and the second parcel for the 3-parcel line.

## Golden programs 001–006

The model was run on the six images with `--sp 0x100 --msp 0x180`
after the adjudicated fixes:

```sh
for n in 001 002 003 004 005 006; do
  python3 sem/hobbit_sem.py --image tests/golden/$n.hex --sp 0x100 --msp 0x180
done
```

* **All six** — `001`, `002`, `003`, `004`, `005` and `006` — are
  byte-identical to the current `tests/golden/NNN.trace`.  This covers
  the `stk5`-scaled addresses, the 32-bit three-parcel
  `RETURN`/`ENTER`/`POPN` operands, the C1 image-end stop, the
  `CMPEQ`/`CMPGT`/`CMPHI` flag results (signed vs unsigned, no memory
  write), and the `006` FLUSHD trap storing the opcode's own PC
  (`0x0006`).
* `005` runs end to end: `CMPEQ` sets F=1, `JMPTN` at `0x0004` is taken
  to `0x000a`, `CMPGT $1,R0` leaves F=0 (1 > 10 is false), the second
  `JMPTN` is not taken, and `ADD $2,R0` / `ADD3 $5,R0` write `0x000c` /
  `0x00000011` before the C1 stop at `0x0018`.

## Refused constructs

The model has no plausible-guess fallback.  A **`Refusal`** is a legal
instruction the model does not implement, an illegal encoding, an
alignment fault, a fetch fault or a state limitation: `step()` raises
`Refusal`, the CLI prints a `REFUSED ... reason:` diagnostic on stderr,
emits no HRI line and stops.  `trap=1` is reserved for the
unimplemented-instruction sequence (`FLUSHD`/`FLUSHDCE`).  Refused:

* **Opcodes not in the table above.**  In one-parcel form: KCALL
  (`0x00`), KRET, CRET, FLUSHI, FLUSHP, CLRE, CPU, AND/AND3,
  MOVA, SHL3/SHR3, and the unimp rows.  In 3-/5-parcel form: ORI,
  ANDI, ADDI, MOVA, UREM, DQM, TADD, TSUB,
  OR/AND/XOR/REM/MUL/DIV (and their `3` forms), SHR/USHR/SHL/UDIV,
  all `3` shift forms, KCALL, LDRAA, FLUSHPTE, FLUSHPBE, and every
  unimp opcode.  These are real instructions in the manual; the model
  simply states only the listed subset.
* **Hardware-unimplemented instructions**: FLUSHD (`0x0B/0x006`) and
  FLUSHDCE (monadic `0x00/0xD`) are the only `trap=1` lines (p. 3-22,
  p. 3-23, p. 1-39); they are not refusals in the sense above.
* **CPU register escape** (`CPU`, niladic `0x0B/0x000`, and Table 1-22
  mode `0x7`).  Control registers (MSP/ISP/SP/CONFIG/PSW/SHAD/VB/STB/
  FAULT/ID/TIMER1/TIMER2) are not modelled, nor is the CPU's "following
  instruction is part of the CPU instruction" property (pp. 1-26,
  1-27, 3-14).
* **Unmodelled modes**: the register mode `0x7`; a 5-parcel monadic
  opcode 0x00 (Table 1-20 p. 1-25 makes it unimp); a conditional jump
  with an indirect mode (p. 3-28); RETURN/POPN with a non-stack-offset
  mode or a negative offset; ENTER with a non-negative stack offset;
  CATCH/ENTER with a non-`word32` mode; a store to an immediate operand
  (a `MOV`/`ADD`/`SUB` destination is written, so an immediate there is
  illegal; `ADD3`/`SUB3` only read their destination, so an immediate
  there is accepted and used as a constant).
* **State** the model cannot represent: virtual addressing, user
  little-endian data, CSP = ISP, unaligned or out-of-range SP/MSP, a
  stack cache crossing 2^32.
* **Events**: reset, interrupts, exceptions, trace, trapped-niladic
  delivery, unimplemented registers, divide-by-zero, privilege
  violations, bus errors, MMU translation and the vector table.  The
  p. 1-39 store is only for FLUSHD/FLUSHDCE; the other events are
  refusals, not HRI records.

An illegal encoding (e.g. a destination immediate, or an unaligned word
access) is a `Refusal` with `illegal:`/`alignment:` rather than being
silently canonicalised.  In particular, an unaligned word or half-word
operand is never rounded down.

## Choices where the manual is ambiguous

These are marked as choices, with both readings.  Where the core and
this model ever disagree, the README is the tie-breaker for the checker.

1. **PC-relative scaling of 16-/32-bit Labels.**  p. 1-21 scales the
   10-bit CALL/JMP offsets by two and says nothing about 16-/32-bit
   Label fields; p. 1-23 only says the 16-bit fields are sign-extended
   in offset modes; p. 1-27 says the offset is added to the
   instruction's address.  This model uses the byte offset as it stands
   (no scaling) and scales only the 10-bit field.  The other reading is
   that a Label is also parcel-scaled (×2).
2. **ENTER's E bit.**  p. 1-15 says the enter guard is set only by an
   ENTER that caused no stack-cache flush; p. 3-19 says it is set on
   successful completion.  This model follows p. 1-15: E=1 only when no
   flush occurred.  For the non-stack-offset ENTER, which the
   pseudocode says flushes unconditionally, it clears E.
3. **ENTER's one-parcel offset.**  p. 3-20 says the 8-bit field is
   *left padded with ones*, not sign-extended.  This model one-fills:
   field `0x00` → -4096, field `0xFE` → -32, field `0xFF` → -16.  The
   other reading (ordinary 8-bit sign extension) would make field 0 a
   zero offset, which contradicts the stated range -16..-4096.
4. **ENTER's MSP.**  For the stack-offset form the model uses
   `MSP = min(old MSP, target+256)`, because the p. 3-19 pseudocode
   flushes only until the cache is at most 256 bytes and never grows
   MSP.  The model also checks that the new SP does not exceed MSP
   (p. 3-21).  For the non-stack-offset forms it sets `SP = MSP =
   target` (p. 3-19 prose, "the stack cache is set empty").
5. **CATCH's target.**  The p. 3-10 pseudocode uses `CSP + src` as the
   fill bound for every addressing mode, while the prose on the same
   page defines, per mode, a target MSP (stack offset → `SP+offset`,
   immediate → the value, indirect/absolute → the fetched word).  This
   model uses the prose target, rounds a non-multiple target up to the
   next 16 (p. 3-11), and caps the fill at `SP+256`.  It does not fill
   downward when the target is already below MSP.
6. **RETURN/POPN offset low bits.**  p. 3-40 explicitly ignores the low
   four bits of the RETURN offset when adjusting SP.  The POPN page
   (p. 3-38) does not repeat this, but the SP's bits 3:0 are reserved
   (Table 1-10 p. 1-17), so this model masks the new POPN SP to 16 bytes
   as well.  With the one-parcel forms the point is moot: their offset
   is always a multiple of 16.
7. **Stack-cache hit relation.**  p. 1-5 displays `SP <= ADDR < MSP`;
   the prose on p. 1-12 says "greater than, or equal to, the SP and
   less than the MSP", but the displayed relation on the same page is
   the strict `SP < ADDR < MSP`.  Because the model does not represent
   cache contents, the discrepancy is not observable; the SP/MSP
   bookkeeping follows p. 1-5 and the p. 1-13 `SP <= MSP <= SP+256`
   bound.
8. **`insn1` and multi-parcel operands.**  The fixed record has two
   parcel slots.  This model prints 0 for the second slot when the
   instruction is one parcel, and the first two parcels for a
   three-/five-parcel instruction.  A three-parcel *monadic* operand is
   the 32-bit `((parcel2 << 16) | parcel3)` (p. 1-23); its second
   parcel is the `insn1` field and its third parcel is not representable
   in the fixed line.  The alternative — always printing the two parcels
   physically following the PC — would make a one-parcel line show the
   next instruction's first parcel; that is not used.
9. **`ADD`'s operation line.**  p. 3-5 prints `ADD: dst += dst`, but
   the description ("source operand is added to the destination") and
   p. 1-28's `ADD a,b ; add a to b` give `dst += src`.  The model uses
   the description.
10. **Trap records and refusals.**  The adjudication's convention C2
    reserves `trap=1` for the unimplemented-instruction sequence
    (`FLUSHD`/`FLUSHDCE`): one store, `*(CSP) = PC`, reported as
    `we=1`, `mask=0f`, with PC/SP/MSP at their pre-state values and no
    `VB+12` fetch.  A legal instruction the model does not implement,
    an illegal encoding, an alignment fault or a fetch fault is a
    `Refusal` with no HRI line; the checker aligns by PC (C4) and does
    not count the missing record as a field mismatch.  The trap store
    is never reused for a fetch fault or a model limitation.
11. **Byte masks.**  The record uses the big-endian bus convention
    (bit 3 = the byte at the word address, bits 31:24) with a word
    address.  The alternative — effective byte address plus a
    right-aligned value — is not used; the core must adopt this
    convention for the diff.
12. **16-bit absolute addresses.**  p. 1-23 lets CONFIG bit 17 copy
    PC bits 31:29 into a 16-bit absolute address.  This model fixes
    CONFIG at its reset value 0, so absolute addresses are
    zero-extended.  The PC-extension reading is not modelled.
13. **Accumulator location.**  The model takes p. 1-7 literally: the
    accumulator is the word at `CSP+4`, not a separate register.  A
    `MOV` to stack offset 4 is therefore a normal stack write that can
    alias the accumulator for a later `[3]` instruction; no special
    casing is applied.
14. **Uninitialised memory.**  Reads of memory the image does not
    contain return 0.  The PRM does not define a value; the demo is
    built so no architectural result depends on an unwritten word.
15. **Overlapping operands.**  The manual does not define an order when
    a source and destination address the same word, or when an indirect
    pointer aliases another operand.  For a 3-/5-parcel `MOV`/`ADD`/`SUB`
    the model resolves the source addressing mode, then the destination
    addressing mode, then loads the source value and the destination
    value; the 1-parcel `MOV istk5,istk5` resolves its destination
    pointer before its source pointer.  These are implementation orders,
    not architectural claims; the demo avoids aliasing.
16. **`CLRE` and the E bit.**  CLRE is not in the modelled subset, so
    the only writer of E in this model is ENTER.  This is a scope
    statement, not a claim that CLRE is optional in the architecture.
17. **`psw` initial value.**  The manual's reset (`PSW = 0`, p. 1-35)
    selects ISP as CSP; this model's CLI uses `0x200` (SP as CSP)
    because it has no ISP.  The reference pre-state in the parent
    checker is the same `0x200`; the trace's SP/MSP lines are only
    meaningful under that starting PSW.
18. **CSP = ISP.**  The model refuses it with `unsupported:` rather
    than guessing an interrupt-stack address.  The manual makes CATCH a
    no-op and ENTER/POPN/RETURN skip MSP updates in that mode
    (pp. 3-10, 3-38, 3-40); none of that is modelled.

## What the model deliberately is not

It is not a timing model, a pipeline model, a cache model, an MMU, an
event processor, an assembler, a disassembler or a second copy of the
Bluespec core.  It knows one instruction at a time and only the
architectural state named above.  That is what makes it useful as the
independent side of the HRI comparison.
