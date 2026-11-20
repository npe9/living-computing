# `hobbit/sem` — an independent one-instruction model of the ATT92010

`hobbit_sem.py` is the specification side of the repository's HRI
(Hobbit Retirement Interface) check.  HRI is the Hobbit analogue of
riscv-formal's RISC-V Formal Interface (RVFI): a fixed per-instruction
retirement record.  The check is a **per-instruction trace comparison**
against the Bluespec core — the two records are diffed field by field —
**not a formal proof**.

One call to `step(state, memory_reader)` computes the architectural
effect of **exactly one** instruction from an architectural pre-state.
There is no pipeline, no prefetch buffer and no decoded-instruction
cache; those belong to the core side of the check.  The model does carry
the Chapter 4 cycle account, because the record's trailing `cyc` field
is part of the HRI comparison.  The record the model returns is the
`HRI ...` line the Bluespec core must reproduce field for field.

The model was written from the printed *ATT92010 Hobbit Microprocessor
Programmer's Reference Manual* (January 1993) and from nothing in
`hobbit/bsv` or `hobbit/asm`.  It is deliberately a second, independent
statement of the semantics, not a translation of the core.

`p. 1-21` below means the manual's own printed folio, Chapter 1, page 21.
The scan's PDF page is printed + 8 for Chapter 1, + 58 for Chapter 3,
+ 110 for Chapter 4.

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
HRI pc=%04x insn=%04x%04x sp=%08x>%08x msp=%08x>%08x we=%d addr=%08x data=%08x mask=%02x trap=%d cyc=%d
```

All hex is lowercase.  `%04x` is a minimum width, so a PC beyond 0xFFFF
prints more than four digits.  `cyc` is decimal.  One HRI line is printed
per retired instruction and for the unimplemented-instruction `trap=1`
line.  A
`Refusal` (a fetch fault, an illegal encoding, an alignment fault, a
state limitation, or a legal instruction outside the subset) produces a
`REFUSED pc=... insn=... reason: ...` diagnostic on stderr and no HRI
line, and ends the run (convention C2); it is not compared as a
retirement.

## State

`State` is `pc`, `sp`, `msp`, `psw`, `memory` and a non-architectural
`timing` record (`retired`, `last_compare`, `last_flag_source`,
`prev_foldable`).  The cycle account is the only thing `timing` feeds; no
architectural result depends on it.

| Field | Meaning | Cite |
|---|---|---|
| `pc` | Address of the instruction to execute; bit 0 is the reserved zero bit and is ignored for fetch | p. 1-13, Table 1-7 p. 1-14, p. 1-4 |
| `sp` | Stack Pointer; inclusive lower bound of the stack cache | p. 1-5, Table 1-10 p. 1-17 |
| `msp` | Maximum Stack Pointer; exclusive upper bound of the stack cache | p. 1-5, Table 1-6 p. 1-13 |
| `psw` | Only bits 6 (V), 5 (C), 4 (F), 11 (E) and 9 (CSP selector) are used | Table 1-8 pp. 1-14..1-16 |
| `memory` | Sparse architectural memory, a dict of word address to 32-bit word | p. 1-4 |
| `isp` | Interrupt-stack pointer; quad-aligned, not associated with the stack cache | p. 1-12, Table 1-6 p. 1-13 |
| `vb` | Vector-table base; quad-aligned | Table 1-14 p. 1-20 |

`isp` and `vb` are architectural but have **no field in the fixed HRI
line**, which carries only `SP`/`MSP` and one word write.  They exist in
`State` because KCALL, KRET and CRET read or write them (pp. 3-15..3-16,
3-29, 3-30); the CLI defaults (`--isp 0x40`, `--vb 0x0`) are harness
values, since the PRM prints no reset ISP or VB.  For those three
instructions the state effect on ISP/PSW is real but not diffable; the
records still carry the observable `SP`/`MSP`/PC and primary write.

The CLI initialises `psw` to `0x00000200` (CSP = SP, bit 9 set).  The
manual's reset value `PSW = 0` selects the ISP as the current stack
pointer (p. 1-35), and this model does not execute instructions with
ISP as CSP (it can call and return through ISP, but not run on it).
The reference pre-state for the demo, and the state the checker should
use, is therefore the explicit `PSW = 0x00000200`.

The model raises `Refusal` (no HRI line) for a state with:

* `psw` bit 16 set (virtual addressing; there is no MMU here, p. 2-1);
* `psw` bit 9 clear at instruction entry (CSP is ISP).  KCALL, KRET and
  CRET themselves are modelled from a CSP = SP state; the manual's
  ISP-as-CSP execution mode for the other instructions is still outside
  the model (p. 1-12);
* `SP` or `MSP` not quad-word aligned, `MSP < SP`, or `MSP > SP+256`
  (p. 1-13);
* a stack whose 256-byte cache would cross the 32-bit address boundary.

`psw` bit 10 (execution level) is recorded and checked for KRET/CRET,
which are privileged (pp. 3-15, 3-30); every other modelled instruction
is available at either level.  `SHAD` is not in the state.  The manual
updates it on ENTER/RETURN/CRET/KCALL/KRET/popn (pp. 1-16, 1-17, 3-19,
3-38, 3-40), but no modelled instruction *reads* it; it is a restart
optimisation, not part of the one-instruction record.  `CONFIG` is fixed
at its reset value 0 (p. 1-36) -- no PC extension, and the cache-enable
bits are irrelevant to this subset -- except bit 16, kernel
little-endian, which is the state's `config_kl` (default clear).  `ISP` and `VB` are
present (see the state table); KCALL/KRET/CRET maintain ISP exactly as
printed, but the HRI line has no ISP or PSW field to show it.

## Memory, byte order and the stack cache

Memory is byte-addressable, 32-bit words.  The numbering of bytes within
a data word is selectable (p. 1-3): at user level by PSW bit 15 (UL), at
kernel level by CONFIG bit 16 (KL).  With the bit clear the data is
big-endian, address 0 in bits 31:24 (Figure 1-2, p. 1-4); with it set it
is little-endian, address 0 in bits 7:0 (Figure 1-3).  Only byte and
half-word operands can tell the difference; "text is always in
big-endian order" (p. 1-4 note), so the parcel at the even address is
bits 31:16 in either mode.  1st Edition Plan 9 runs with both bits set
(`sys/src/9/hobbit/machine.h:24,77`), and `tools/p9run.py` runs its
binaries that way.  A byte or half-word load extracts the
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
  copy the 16-byte flush/refill blocks.  Those copies are not
  architecturally observable in this abstraction because the
  backing-memory image already has every byte the cache holds.  Flush
  *timing* is still accounted for: ENTER's `cyc` counts the blocks the
  pp. 3-19/3-20 loop would move (see “Cycle accounting”).  The `SP`/`MSP`
  bounds and the `PSW.E` enter-guard result are architectural.
* it does not model cache hits, bus arbitration or bus-error/retry cycles;
  its A/D/Q parameters price only the accesses the printed Chapter 4 rows
  name.

The integer accumulator (PRM p. 1-7, Figure 1-4; p. 1-3) is **not a
register**: it is the word at `CSP + 4`.  The `[3]` forms write that
address, and the model records that write like any other.  `R4` in the
manual's examples is stack offset 4 (the word above the PC-save slot at
`CSP`), not a fifth register.

**Stack fields are measured in two different units, and mixing them up
silently addresses the wrong word.**  Printed p. 1-21 scales "five-bit
offset values … by four" and the ten-bit PC-relative jump/call values by
two; it scales nothing else.

| field | unit | example |
|---|---|---|
| one-parcel `stk5`, `istk5`, `wai5` | word index, `× 4` (p. 1-21) | `SHL3 $4,R12` → field 3 → `SP+12` |
| 3-parcel 16-bit `Roffset` (modes 0x4…0x7, 0x8…0xB, 0xD, 0xE) | **byte offset, unscaled** | `SHL R12,R8` → fields `0x000C`/`0x0008` → `SP+12`/`SP+8` |
| 5-parcel 32-bit field | byte offset | — |
| absolute (0x0…0x3, 0xC) | byte address | — |

Register names are byte offsets: `R12` is `SP+12`, `R8` is `SP+8`, which
is also why the 5-bit form of `R12` is 3.  Table 1-21's byte and
half-word stack-offset modes exist precisely because the 16-bit fields
address bytes; a word index there would make them unencodable.

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
| `ADDI` | 3p/5p `gen16/gen16`, `gen32/gen32` (`0x03`) | `hidden=dst; dst+=src; Acc=hidden`; C and V unchanged; two architectural stores (dst is the record's primary write) | p. 3-6 |
| `ANDI` | 3p/5p (`0x02`) | `hidden=dst; dst&=src; Acc=hidden`; C and V unchanged; two stores | p. 3-8 |
| `ORI` | 3p/5p (`0x01`) | `hidden=dst; dst|=src; Acc=hidden`; C and V unchanged; two stores | p. 3-37 |
| `MUL`, `MUL3` | 3p/5p (`0x26`, `0x36`) | `dst *= src` or `Acc = dst*src`; C on unsigned overflow, V on signed overflow of the destination | p. 3-34 |
| `DIV`, `DIV3` | 3p/5p (`0x27`, `0x37`) | `dst = dst/src` or `Acc = dst/src`, two's-complement truncation toward zero; V set only for `0x80000000/-1`, C unchanged; divide-by-zero is a refusal | p. 3-17 |
| `REM`, `REM3` | 3p/5p (`0x25`, `0x35`) | `dst = dst%src` or `Acc = dst%src`; remainder follows the dividend's sign; V always cleared, C unchanged; divide-by-zero is a refusal | p. 3-39 |
| `UDIV` | 3p/5p (`0x2F`) | `dst = dst/src` unsigned; C always cleared, V unchanged; divide-by-zero is a refusal | p. 3-48 |
| `UREM` | 3p/5p (`0x05`) | `dst = dst%src` unsigned; C always cleared, V unchanged; divide-by-zero is a refusal | p. 3-49 |
| `DQM` | 3p/5p (`0x07`), source word modes or constant, destination mode selects 2 or 4 words | copy two or four contiguous words; alignment 8 (double) or 16 (quad); the record's one write is the lowest-addressed destination word | p. 3-18 |
| `MOVA` | 1p `stk5,stk5` (`0x1D`); 3p/5p (`0x04`), source only `0xC/0xD/0xE`, destination any general mode | `dst = &src`; immediate source and register source/destination are illegal | p. 3-33 |
| `SHL3` | 1p `uimm5,stk5` (`0x1E`) | `Acc = dst << unsigned(src)`; zeros fill; only the low five bits of src select the count; the destination is unchanged; C/V/F unchanged | p. 3-41 |
| `SHR3` | 1p `uimm5,stk5` (`0x1F`) | `Acc = dst >> src` as an arithmetic shift, sign bit replicated; only the low five bits of src select the count; the destination is unchanged; C/V/F unchanged | p. 3-42 |
| `LDRAA` | 3p monadic `0x00/0xA`, `flow32` | `Acc = &dst`, the address calculated exactly as a JMP target | p. 3-31 |
| `TADD` | 3p/5p (`0x0C`) | tagged add: a nonzero tag sets F=1, leaves C/V and memory alone; otherwise C/V and F=V, and the sum is stored only when F=0 | p. 3-44 |
| `TSUB` | 3p/5p (`0x0D`) | tagged subtract with the same tag/overflow/store rules | p. 3-47 |
| `CLRE` | 1p niladic `0x0B/0x00A` | clear `PSW.E`; no memory write | p. 3-12 |
| `KCALL` | 1p `imm10`; 3p monadic `0x00/0x0`, `word32` | save src, return PC and PSW at `ISP-12/-8/-4`, `ISP-=16`, `PC=*(VB+0)`, `PSW &= 0xFFFF0000`; the record shows the first frame word | p. 3-29 |
| `KRET` | 1p niladic `0x0B/0x001` | `PC=*(ISP+8)`, `PSW=*(ISP+12)`, `ISP+=16`; privileged; no memory write | p. 3-30 |
| `CRET` | 1p niladic `0x0B/0x005` | `SP=*(ISP+0)`, CATCH to `*(ISP+4)`, restore MSP/PC/PSW, `ISP+=16`; privileged; no memory write | pp. 3-15, 3-16 |
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
* `flow32` (Table 1-23) for CALL/JMP/LDRAA and KCALL: absolute indirect
  `**$addr`, stack-offset indirect `*Roffset`, PC-relative label,
  absolute `*$addr`;
* `word32` (Table 3-2, p. 3-4) for CATCH/ENTER and KCALL;
* the DQM source restricted to the word modes `0xC/0xD/0xE` plus the
  immediate `0xF`, and the DQM destination modes `0x0/0x4/0x8`
  (double-word) or `0xC/0xD/0xE` (quad-word), as p. 3-18 requires.

The width of an operand comes from its mode: `0x0/1/4/5/8/9` are bytes,
`0x2/3/6/7/A/B` are half-words, `0xC/0xD/0xE` are words, and `0xF` is an
immediate.  A missing suffix in the manual's syntax means a signed word
(p. 1-28); the model applies sign extension for signed byte and
half-word loads and zero extension for unsigned ones, exactly as p. 1-3
and p. 1-28 describe.

A stack-offset-indirect operand (`0x8`-`0xB`, `0xE`) is the two-access
form of p. 1-27: "The word at this address is fetched and then used as
an address to obtain the data operand."  The word at `CSP + offset` is
the operand's address and the access is at that address with the mode's
width and sign; the record's `addr` is therefore the pointer's value,
never the stack slot that holds it.  The offset is an unscaled byte
offset and must be word-aligned (alignment fault `0x4`, p. 1-27), while
the pointed-to address must meet its own width's alignment (p. 1-4).
The core models the same two steps across EU_S1 (pointer word and the
other operand) and EU_S2 (the word the pointer names) on the stack
cache's two printed read ports; `docs/isa_inventory.md` §1.6.1 records
the sequencing and the off-chip operand-path gap.  One core limitation
is recorded there too: an instruction that needs a pointed-to word for
*both* operands is refused by the core (the second word would need a
third read port), while this model still executes it.

A three-parcel **monadic** instruction (KCALL, CALL, RETURN, JMP,
LDRAA, the four conditional jumps, CATCH, ENTER, POPN) carries one
32-bit operand in parcels 2 and 3, `((parcel2 << 16) | parcel3)`
(p. 1-23, and `stk32`/`word32` in Table 3-2, p. 3-4); a three-parcel
**dyadic** instruction
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
| `we` | 1 if this instruction performs the record's one architectural write, else 0.  For the multi-write instructions (ADDI/ANDI/ORI, DQM, KCALL) the line carries the **primary** write only; see choice 26 | p. 1-5 (cache appears as normal memory), p. 1-7 (accumulator) |
| `addr` | Word address of that write (`effective address & ~3`) | p. 1-4 |
| `data` | Bus word for the write: the stored byte(s) in their byte lanes (Figure 1-2 lanes for big-endian data, Figure 1-3 for little-endian) | p. 1-4 |
| `mask` | Byte marks of the write by lane: bit 3 = bits 31:24, bit 0 = bits 7:0 (the byte at `addr` and at `addr+3` for big-endian data, the reverse for little-endian); a word write is `0f` | p. 1-4 (byte stores), p. 1-5 |
| `trap` | 0 = retired; 1 = the unimplemented-instruction sequence (FLUSHD/FLUSHDCE, and every three- and five-parcel dyadic opcode Tables 1-18/1-20 print as "unimp", which is where an operating system's floating point lives) with the p. 1-39 store; a `Refusal` produces no line | see below |
| `cyc` | Occupancy in core clock cycles between this retirement and the previous one (for the first record, from the core's start); the Chapter 4 base under the p. 4-1 assumptions | Tables 4-32..4-36 pp. 4-3..4-5; “Cycle accounting” below |

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

## Cycle accounting

`cyc` is the instruction's occupancy in core clock cycles at retirement:
the cycles between the previous HRI record and this one, and for the
first record from the core's start to its retirement.  It is the
Chapter 4 base cost under the four assumptions printed on p. 4-1:

* instruction fetch accesses the instruction cache (the prefetch-buffer
  cache condition);
* only the stack-offset, immediate, register, absolute (for jumps and
  calls only) and PC-relative addressing modes are used;
* all stack-offset accesses are captured in the stack cache;
* no data hazards occur between instructions.

Consistently with those assumptions the model adds **no** delay from
Tables 4-37..4-40 (pp. 4-6..4-7): no IC-miss or empty-EU penalty, no
operand-access penalty, no data-type penalty and no miscellaneous delay.
The indirect-operand rows of Tables 4-38 and 4-40 are byte-identical in
print and the manual never says whether both apply, so neither is applied;
the model cannot double-count an indirect operand.

### Memory parameters (model choices)

p. 4-2 defines the symbols but prints no cycle values.  The model's
memory is a single-cycle 32-bit word store, so one word access is one
core cycle.  These are named parameters in `hobbit_sem.py`, never
inline constants:

| Parameter | Meaning (p. 4-2) | Value | Why this value |
|---|---|---|---|
| `A_CYC` | memory access time, single word | 1 | one 32-bit word per cycle in the model's BRAM; the same unit the HRI counts in |
| `D_CYC` | memory access time, double word | 2 | two 32-bit words on the single-cycle word store |
| `Q_CYC` | memory access time, quad word | 4 | four 32-bit words on the single-cycle word store |

These values are choices, not printed manual facts; the manual prints
only the symbols.  No row used by an implemented instruction contains
`N`; p. 4-2 defines it, but no Chapter 4 table charges for stack-cache
occupancy (`docs/timing_tables.md` §6.11).  `E` is not a free parameter:
it is computed per ENTER (below).

### Rows used by implemented instructions

| Instruction(s) | Printed cell | `cyc` | Source |
|---|---|---|---|
| `ADD`, `ADD3` (all forms) | 1 | 1 | Table 4-32, p. 4-3 |
| `MOV` (all forms) | 1 | 1 | Table 4-32, p. 4-3 |
| `SUB`, `SUB3` | 1 | 1 | Table 4-32, p. 4-3 |
| `CMPEQ`, `CMPGT`, `CMPHI` | `CMP` = 1 | 1 | Table 4-32, p. 4-3; the `CMP` row is the only timing the manual gives the three compares (p. 3-13) |
| `TESTC`, `TESTV` | 1 | 1 | Table 4-32, p. 4-3 |
| `ADDI`, `ANDI`, `ORI` | 2 | 2 | Table 4-32, p. 4-3 |
| `CLRE` | 1 | 1 | Table 4-32, p. 4-3 |
| `LDRAA` | 1 | 1 | Table 4-32, p. 4-3 |
| `MOVA` | 1 | 1 | Table 4-32, p. 4-3 |
| `TADD`, `TSUB` | 1 | 1 | Table 4-32, p. 4-3 |
| `MUL`, `MUL3` | `Min 3`, `Max 20` | 20 | Table 4-33, p. 4-4; data dependent and no formula is printed, so the model takes the printed maximum (`MUL_CYC`, choice 24) |
| `DIV`, `DIV3`, `REM`, `REM3`, `UDIV`, `UREM` | 38 | 38 | Table 4-33, p. 4-4 |
| `DQM` constant → SC double/quad | 3 / 5 | 3 / 5 | Table 4-34, p. 4-4 |
| `DQM` constant → M double/quad | `1 + D` / `1 + Q` | 3 / 5 | Table 4-34, p. 4-4 |
| `DQM` SC → SC double/quad | 4 / 8 | 4 / 8 | Table 4-34, p. 4-4 |
| `DQM` SC/M ↔ M/SC double | `2 + D` | 4 | Table 4-34, p. 4-4 |
| `DQM` SC/M ↔ M/SC quad | `4 + D` | 6 | Table 4-34, p. 4-4; a quad transfer printed with D, not Q |
| `DQM` M → M double | `2·D` | 4 | Table 4-34, p. 4-4 |
| `DQM` M → M quad | `8·S` | **refused** | Table 4-34, p. 4-4; `S` is not defined on p. 4-2 |
| `KCALL` | `8 + D + A` | 11 | Table 4-36, p. 4-5 |
| `KRET` | `10 + D` | 12 | Table 4-36, p. 4-5 |
| `CRET` | `11 + Q` | 15 | Table 4-36, p. 4-5 |
| `NOP` | 1 | 1 | Table 4-32, p. 4-3 |
| `CALL` (1p and 3p) | 1 | 1 | Table 4-32, p. 4-3 |
| `RETURN` | 2 | 2 | Table 4-32, p. 4-3; always indirect, no indirection delay (p. 4-3 note) |
| `POPN` | 2 | 2 | Table 4-32, p. 4-3 |
| `CATCH` | 1 | 1 | Table 4-36, p. 4-5; flat 1, no refill term is printed even though CATCH fills the cache (pp. 3-10..3-11) |
| `ENTER` | `1 + (Q·E)` | `1 + Q_CYC·E` | Table 4-36, p. 4-5; E per the pp. 3-19/3-20 flush loop |
| `JMP` folded | Min 0 | 0 | Table 4-32, p. 4-3; folded unconditional jump takes no time (p. 4-3 note) |
| `JMP` unfolded | Max 1 | 1 | Table 4-32, p. 4-3 |
| `JMPFN`, `JMPFY`, `JMPTN`, `JMPTY` | Table 4-35 rows | 0..3 | Table 4-35, p. 4-5 (below) |
| `FLUSHD`, `FLUSHDCE` (trap) | `Unimplemented opcode = 7 + A` | 8 | Table 4-36, p. 4-5; the sequence both take (pp. 3-22, 3-23) |

The code's `CHAPTER4` tuple still transcribes the `Exception` row
(`9 + D + A`, p. 4-5), which the model refuses because event processing
is outside it, and the `DQM M quad-word to M quad-word = 8·S` cell, which
has no encoded value because `S` is not defined on p. 4-2.  The one
MUL row keeps its printed `Min 3/Max 20` range in the tuple; the named
`MUL_CYC` choice supplies the single number the record needs.

### Conditional jumps (Table 4-35, p. 4-5)

The branch's static Y/N bit is the low bit of the opcode: `JMPFY` and
`JMPTY` predict taken, `JMPFN` and `JMPTN` predict not taken (Table 1-15,
p. 1-22; p. 3-28).  The model compares that with the direction the branch
actually took.

| Case | Printed row | `cyc` |
|---|---|---|
| correct prediction, folded | Correct prediction, folded | 0 |
| correct prediction, unfolded | Correct prediction, unfolded | 1 |
| wrong, compare is the previous record | Incorrect prediction, jump after compare | 3 |
| wrong, one record between compare and branch | Incorrect prediction, jump 2 instructions after compare | 2 |
| wrong, two records between | Incorrect prediction, jump 3 instructions after compare | 1 |
| wrong, three or more records between, unfolded | Incorrect prediction, unfolded, 4 or more instructions after compare | 1 |
| wrong, three or more records between, folded | Incorrect prediction, folded, 4 or more instructions after compare | 0 |

The first three wrong-prediction rows carry no folded/unfolded qualifier
in print, so they apply to both.  The distance is counted in HRI records
from the compare that last wrote PSW.F: 0 means the compare retired
immediately before the branch.  A folded branch still retires as its own
record (the contract), and the model counts it like any other instruction
when a later branch measures its distance; the manual does not define
whether a folded branch counts, and this is the reading consistent with
the retirement record.  In particular golden 005's taken `JMPTN` after
`CMPEQ` is folded but incorrectly predicted at distance 0, so it is 3,
not 0.

### Branch folding (p. 4-7)

A one-parcel branch folds into a previous **one- or three-parcel**
instruction unless the previous instruction is:

1. another jump of any kind;
2. a one-parcel instruction whose five-bit opcode is in `0x00..0x07`;
3. any three-parcel monadic instruction (opcode `0x00`).

In the modelled subset classes 1 and 2 overlap (CALL, the stack class,
JMP and the conditional jumps all have one-parcel opcodes in
`0x00..0x07`), and every three-/five-parcel control transfer is caught by
class 3.  A five-parcel previous instruction is not a fold target at all
because p. 4-7 limits the previous instruction to one or three parcels.
Only one-parcel branches fold: a three- or five-parcel `JMP` or
conditional jump is always unfolded and pays 1 (or its Table 4-35
penalty).  A folded unconditional `JMP` is 0 and an unfolded one is 1
(p. 4-3 note).

### ENTER's E term

Table 4-36 prints `1 + (Q·E)`.  p. 4-2 calls E “ENTER size” but never
states its unit, and the same table prices CATCH at a flat 1 even though
CATCH refills the cache in 16-byte blocks.  The model therefore uses the
only ENTER work pp. 3-19/3-20 actually describe: the number of 16-byte
blocks the flush loop moves, one `MSP -= 16` iteration each, rounded up
for a partial block and capped by the valid cache (SHAD = SP).

* Stack-offset ENTER flushes only the excess over `SCSIZE`: the loop runs
  while `MSP - target > SCSIZE`, so `E = ceil((MSP - target - 256)/16)`
  capped at `(MSP - SP)/16`.
* A non-stack-offset ENTER flushes the cache unconditionally: every valid
  block, `E = (MSP - SP)/16`.

Worked examples from the goldens: `ENTER R-32` with
`MSP - target = 0x180 - 0x0e0 = 0xa0 ≤ 256` moves no block, so E = 0 and
`cyc = 1`; `ENTER $0xC0` at `SP=0x100, MSP=0x180` moves
`(0x180 - 0x100)/16 = 8` blocks, so `cyc = 1 + 4·8 = 33` (golden 004).

### Where the manual is silent

An incorrectly predicted conditional jump whose PSW.F did not come from a
compare -- the reset value, `TESTC` and `TESTV` are the other flag
sources -- has **no** Table 4-35 row.  `step()` raises `Refusal` with
`unsupported:` and emits no HRI line rather than inventing a penalty.
A correctly predicted branch needs no compare distance and is priced
normally.  This is the only timing refusal; every other refusal is an
instruction, encoding or state the model already refused.

## Traps and refusals

There are two different outcomes, and the adjudication's convention C2
requires that they not be conflated.

**`trap=1` — the unimplemented-instruction sequence.**  `FLUSHD` and
`FLUSHDCE` take it (p. 3-22, p. 3-23; both are not implemented in
hardware), and so does every three- or five-parcel dyadic opcode that
Tables 1-18 and 1-20 print as "unimp" (pp. 1-24, 1-25: "The
unimplemented instruction sequence is performed"; p. 1-39: "There are no
tests performed on the addressing modes of unimplemented dyadic
instructions").  Those opcodes are the ones an operating system
emulates: 1e's floating point (`FMOV` 0x11, `FADD` 0x2b, ...,
`sys/src/cmd/zl/optab.c`) is there, with `fprt0.s`/`fpihobbit.c` as the
handler.  Until 2026-11-20 the model refused them; `tools/p9run.py`
found the first one 138 instructions into `za`.  The sequence is
(p. 1-39):

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

`demo.s` is a program at 0 with a subroutine at `0x046`.  It exercises
the simple base rows, `CATCH`/`RETURN`/`POPN`, a zero-flush `ENTER`,
the trap row, folded and unfolded unconditional jumps, and five of the
seven Table 4-35 rows (the two “4 or more instructions after compare”
rows are not reached).  A multi-block ENTER flush is golden 004's
`ENTER $0xC0`, `cyc=33`.  The reference pre-state
is `PC=0, SP=0x100, MSP=0x180, PSW=0x200, SHAD=0x100, CONFIG=0`.  The
listing comments give the hand encoding; `demo.trace` is the model
output, byte for byte.

| # | PC | Instruction | `cyc` | What the line shows and why | Cite |
|---|---|---|---|---|---|
| 1 | 0000 | `ENTER R-32` | 1 | `SP 0x100→0x0e0`; `MSP-target = 0xa0 ≤ 256`, so the flush loop moves 0 blocks, E=0, `1 + Q·0`; E is set; no write | pp. 3-19..3-21; Table 4-36 p. 4-5 |
| 2 | 0002 | `MOV $1,R4` | 1 | word write `0x0e4 ← 1`, mask `0f`; accumulator slot is CSP+4 | p. 3-32, p. 1-7; Table 4-32 |
| 3 | 0004 | `MOV R4,R8` | 1 | word write `0x0e8 ← 1` | p. 3-32; Table 4-32 |
| 4 | 0006 | `ADD $5,R8` | 1 | word write `0x0e8 ← 6`; C=V=0 (flags are state, not in the line) | p. 3-5; Table 4-32 |
| 5 | 0008 | `CALL 0x046` | 1 | return PC `0x00a` written at `*(CSP)=0x0e0`, mask `0f`; next PC 0x046 | p. 3-9; Table 4-32 |
| 6 | 0046 | `CATCH R192` | 1 | no write; `MSP 0x180→0x1a0` (two 16-byte blocks, target 0x0e0+0xc0) | pp. 3-10, 3-11; Table 4-36 (flat 1) |
| 7 | 0048 | `MOV $7,R12` | 1 | word write `0x0ec ← 7` | p. 3-32; Table 4-32 |
| 8 | 004a | `RETURN R0` | 2 | no write; `PC ← *(0x0e0)=0x00a`, SP unchanged; no indirection delay | p. 3-40; Table 4-32 note |
| 9 | 000a | `MOV R8,R4` | 1 | word write `0x0e4 ← 6` | p. 3-32; Table 4-32 |
| 10 | 000c | `SUB R8,R4` | 1 | 3-parcel; word write `0x0e4 ← 0`; C=V=0 | p. 3-43; Table 4-32 |
| 11 | 0012 | `POPN R32` | 2 | no write; `SP 0x0e0→0x100`; MSP stays 0x1a0 | p. 3-38; Table 4-32 |
| 12 | 0014 | `CMPEQ $1,R0` | 1 | 1 == 0 false, so F=0; no write | p. 3-13; Table 4-32 `CMP` row |
| 13 | 0016 | `JMPTN 0x04c` | 0 | F=0, not taken; prediction N is correct; folded into the previous 1-parcel CMPEQ | Table 4-35 |
| 14 | 0018 | `CMPEQ $1,R0` | 1 | F=0 again | p. 3-13; Table 4-32 |
| 15 | 001a | `JMPTY 0x020` | 3 | F=0, not taken; prediction Y is wrong; folded; compare is the previous record | Table 4-35 “jump after compare” |
| 16 | 001c | `JMPFN 0x020` | 2 | F=0, taken; prediction N is wrong; unfolded because the previous instruction is a jump; one record between compare and branch | Table 4-35 “2 instructions after compare”; p. 4-7 |
| 17 | 0020 | `NOP` | 1 | no write; the next JMP folds into it | p. 3-35; Table 4-32 |
| 18 | 0022 | `JMP 0x026` | 0 | folded into the preceding NOP | Table 4-32 note |
| 19 | 0026 | `POPN R0` | 2 | offset 0: SP unchanged; cannot receive a fold (opcode 0x02) | p. 3-38; p. 4-7 |
| 20 | 0028 | `JMP 0x02a` | 1 | unfolded: previous POPN is in the p. 4-7 `0x00..0x07` class | Table 4-32; p. 4-7 |
| 21 | 002a | `POPN R0` | 2 | offset 0: SP unchanged | p. 3-38; Table 4-32 |
| 22 | 002c | `JMPTN 0x04c` | 1 | F=0, not taken; prediction N correct; unfolded (previous POPN) | Table 4-35 |
| 23 | 002e | `.5 CMPEQ $0,R0` | 1 | 5-parcel compare, F=1; a five-parcel instruction cannot receive a fold | p. 3-13; Table 4-32; p. 4-7 |
| 24 | 0038 | `JMPTN 0x03c` | 3 | F=1, taken; prediction N wrong; unfolded; compare is the previous record | Table 4-35 “jump after compare” |
| 25 | 003c | `POPN R0` | 2 | offset 0: SP unchanged | p. 3-38; Table 4-32 |
| 26 | 003e | `JMPTN 0x042` | 1 | F=1, taken; prediction N wrong; unfolded; two records (0038, 003c) between compare and branch | Table 4-35 “3 instructions after compare” |
| 27 | 0042 | `NOP` | 1 | no write | p. 3-35; Table 4-32 |
| 28 | 0044 | `FLUSHD` | 8 | `trap=1`; the fixed unimplemented save writes PC `0x044` at `CSP=0x100`, mask `0f`; `7 + A = 8`; the model stops | p. 3-22, p. 1-39; Table 4-36 |

The one-parcel forms in the trace are `0bf8`, `7021`, `6022`, `50a2`,
`041f`, `6041`, `080b`, `4020`, `181b`, `1c03`, `1002`, `2c02`,
`0c02`, `0803`, `0c01`, `1810`, `1802`, `2c06`, `0831`, `70e3`, `0802`;
the 3-parcel `SUB` is `a0dd 0008 0004`, and the 5-parcel `CMPEQ` is
`dffd 0000 0000 0000 0000`.  `insn1` is `0000` for every one-parcel line
and the second parcel for the multi-parcel lines.

## Golden programs 001–013

The model was run on all thirteen images with `--sp 0x100 --msp 0x180`:

```sh
for n in 001 002 003 004 005 006 007 008 009 010 011 012 013; do
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
* The `cyc` column follows the rows above: 001 and 002 are all simple
  one-cycle instructions; 003 is `1,1,1,1,2,1`; 004 is `1,1,2,33,2,1`
  (the 33 is `ENTER $0xC0`, eight flushed blocks, `1 + 4·8`); 006 is
  `1,1,1,8` (the trap row).
* `005` runs end to end: `CMPEQ` sets F=1, `JMPTN` at `0x0004` is taken
  to `0x000a` with `cyc=3` — folded into the compare, but the N
  prediction is wrong and the compare is the immediately previous
  record (Table 4-35 “jump after compare”); `CMPGT $1,R0` leaves F=0
  (1 > 10 is false), the second `JMPTN` is correctly not taken and folded
  (`cyc=0`); and `ADD $2,R0` / `ADD3 $5,R0` write `0x000c` /
  `0x00000011` before the C1 stop at `0x0018`.

The new programs hand-derive instructions added in this milestone.
007–012 have no core comparison yet (the Bluespec core does not
implement MUL, DIV, ADDI, TADD, LDRAA, or the three-parcel MOVA), but
`tests/run_tests.sh` runs the model against each trace with
`hri_check.py`, and `tests/golden/check_golden.py` checks their format,
state continuity and per-line citation.  013 is the exception: the core
implements its four one-parcel row-11 forms, so `tests/run_tests.sh`
compares the core, the model and the hand-derived trace three ways.

* **007 `MUL`**: `MOV $7,R8; MUL $6,R8` gives `0x2a` with `cyc=20`
  (Table 4-33's printed maximum), C=V=0.
* **008 `DIV`**: `MOV $-7,R8; DIV $2,R8` gives `0xfffffffd` with
  `cyc=38`, the truncation-toward-zero reading of p. 3-17.
* **009 `ADDI`**: `MOV $5,R8; ADDI $3,R8` writes 8 to `0x108` and 5 to
  the accumulator `0x104`; the record carries the destination store
  (choice 26), `cyc=2`.
* **010 `TADD`**: an untagged `4+4` stores 8; a tagged `TADD $2,R8`
  sets F and performs no store.
* **011 `MOVA`**: `MOVA R16,R8` stores the address `SP+16 = 0x110`.
* **012 `LDRAA`**: `LDRAA *$0x100` puts `0x100` in the accumulator at
  `0x104`.
* **013 one-parcel row 11**: `MOV $-1,R12` stores `0xffffffff` at
  `0x10c`; `SHL3 $4,R12` writes `0xfffffff0` to the accumulator at
  `0x104` and leaves `0x10c` alone; `SHR3 $4,R12` shifts the same
  `0xffffffff` arithmetically back to `0xffffffff` (a logical shift would
  give `0x0fffffff`); `MOVA R16,R8` stores `SP+16 = 0x110` at `SP+8 =
  0x108`.  All four are Table 1-15 row 11 one-parcel forms (p. 1-22),
  the shifts follow pp. 3-41/3-42 and are one cycle each in Table 4-32
  (p. 4-3).  Unlike 007–012, 013 also runs on the Bluespec core, which
  implements these four opcodes.

## Refused constructs

The model has no plausible-guess fallback.  A **`Refusal`** is a legal
instruction the model does not implement, an illegal encoding, an
alignment fault, a fetch fault or a state limitation: `step()` raises
`Refusal`, the CLI prints a `REFUSED ... reason:` diagnostic on stderr,
emits no HRI line and stops.  `trap=1` is reserved for the
unimplemented-instruction sequence (`FLUSHD`/`FLUSHDCE`).  Refused:

* **Opcodes not in the table above.**  In one-parcel form: FLUSHI,
  FLUSHP, CPU, AND/AND3, and the unimp rows.  In 3-/5-parcel form:
  AND/AND3, OR/OR3, XOR/XOR3, SHL/SHL3, SHR/SHR3, USHR/USHR3,
  FLUSHPTE, FLUSHPBE, the five-parcel monadic opcode 0x00 (Table 1-20
  p. 1-25 makes it unimp), and every unimp opcode.  These are real
  instructions in the manual; the model simply states only the listed
  subset.  The logical AND/OR/XOR and the 3-/5-parcel shift forms remain
  outside the subset; the arithmetic, interlocked, tagged, move, DQM,
  kernel-call and five-parcel forms and the one-parcel `SHL3`/`SHR3`
  (pp. 3-41, 3-42) are implemented.
* **Divide by zero** (`DIV`, `DIV3`, `REM`, `REM3`, `UDIV`, `UREM`).
  pp. 3-17, 3-39, 3-48, 3-49 say it takes the zero-divide exception;
  the event sequence is outside a one-instruction architectural model,
  so `step()` raises `unsupported:` rather than inventing a trap line.
* **DQM's printed `8·S` cell.**  A quad-word memory-to-memory transfer
  selects Table 4-34's `8·S` row (p. 4-4), and `S` is not among the
  p. 4-2 abbreviations.  The model refuses that cell rather than
  substituting `Q`; every other DQM cell resolves.
* **DQM mode misuse.**  p. 3-18's description calls non-permitted
  addressing modes an alignment fault while its Notes call them an
  illegal instruction sequence.  The model follows the specific Notes
  (`illegal:`) and says so in choice 28.
* **MOVA's immediate source.**  p. 3-33's footnote allows "immediate as
  already noted" while its Notes make an immediate source (and a
  register source or destination) an illegal instruction.  The model
  follows the Notes (choice 29).
* **Privilege and interrupt-stack state.**  KRET and CRET at user level
  are a privilege violation (pp. 3-15, 3-30) and are refused.  KCALL,
  KRET and CRET also refuse an unaligned or too-low ISP (p. 1-12,
  Table 1-6 p. 1-13), and KCALL refuses an unaligned VB (Table 1-14
  p. 1-20).  CRET refuses a restored SP/MSP outside the p. 1-13
  `SP <= MSP <= SP+256` relation.
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
* **Timing row absent**: an incorrectly predicted conditional jump whose
  PSW.F did not come from a compare (reset, `TESTC`, `TESTV`) has no
  Table 4-35 row; `step()` refuses rather than inventing a penalty (see
  “Where the manual is silent”).
* **Events**: reset, interrupts, exceptions, trace, trapped-niladic
  delivery, unimplemented registers, bus errors, MMU translation and
  the vector table.  A divide-by-zero is refused at the dividing
  instruction (see above).  The p. 1-39 store is only for
  FLUSHD/FLUSHDCE; the other events are refusals, not HRI records.
* **The one-write record limit.**  ADDI/ANDI/ORI write both the
  destination and the accumulator (p. 3-6), DQM writes two or four
  words (p. 3-18) and KCALL writes a three-word frame (p. 3-29).  The
  fixed HRI line has one `we`/`addr`/`data`/`mask` slot, so it reports
  the primary write (destination, lowest destination word, or the
  `ISP-12` source word) and the remaining stores are applied to
  `state.memory` but not shown (choice 26).  Those instructions are
  therefore **not** comparable against a core until the record grows a
  block/multi-write form; the implemented core does not execute them.

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
19. **Memory parameters A, D and Q.**  p. 4-2 defines them as the
    single-, double- and quad-word access times but prints no values.
    This model chooses `A_CYC = 1`, `D_CYC = 2`, `Q_CYC = 4` because its
    memory is a single-cycle 32-bit word store.  The alternative (some
    bus latency from the data sheet or a board model) would change every
    cell that contains A/D/Q; the chosen values are named parameters,
    not inline numbers, and are model choices, not manual facts.
20. **ENTER's E term.**  Table 4-36 prints `1 + (Q·E)` and p. 4-2 calls
    E “ENTER size” without a unit.  This model reads E as the number of
    16-byte blocks the pp. 3-19/3-20 flush loop moves, rounded up for a
    partial block.  The alternative (frame size in quad-words) would
    charge for allocation that the pseudocode never performs and would
    price `ENTER R-32` at `1 + Q·2 = 9` instead of 1; the flush reading
    matches the only memory traffic the pages describe.
21. **Table 4-35's folded/unfolded qualifiers.**  Three of the seven
    wrong-prediction rows have no folded/unfolded qualifier.  This model
    applies them to both folded and unfolded branches, and splits only
    the “4 or more instructions after compare” row (unfolded 1, folded
    0).  A folded branch still counts as one retiring instruction when a
    later branch measures its distance to the compare; the manual does
    not state whether folding removes it from that count.
22. **No Chapter 4 delay tables.**  Under p. 4-1's four assumptions the
    model adds no Table 4-37..4-40 penalty.  The duplicated indirect
    rows of Tables 4-38 and 4-40 are not applied at all, since the
    manual does not say whether both apply to one access.  Fetch,
    operand-access, data-type and miscellaneous delays are therefore
    outside the model; the core may add them only if the trace contract
    changes.
23. **First-record `cyc`.**  The first HRI record reports the whole span
    from the core's start to its retirement.  With no overlap modelled,
    that is the instruction's own occupancy (`cyc` is 1 for a first
    one-cycle instruction, 8 for a first FLUSHD trap).
24. **MUL/MUL3's single `cyc`.**  Table 4-33 (p. 4-4) prints only
    `Min 3 / Max 20` and calls the time data dependent; no page prints
    the dependence.  The record must carry one number, so the model
    takes the printed maximum, `MUL_CYC = 20`.  This is a model choice
    like A/D/Q; the alternative (the minimum, or an invented
    operand-dependence formula) would change every MUL record.
25. **Two's-complement division rounding.**  p. 3-17 says only "Two's
    complement division is performed", p. 3-39 says REM is defined in
    terms of DIV, and p. 1-28 repeats that definition.  No page prints
    the rounding direction or the remainder sign.  This model uses the
    standard truncation toward zero (quotient sign = sign of the
    dividend XOR divisor; remainder sign = dividend sign): `-7/2 = -3`
    with remainder `-1`.  Floor division would give `-4` and `+1`.
26. **Instructions with more than one architectural write.**  ADDI,
    ANDI and ORI store the destination and the old destination in the
    accumulator (p. 3-6); DQM moves two or four words (p. 3-18); KCALL
    writes the `ISP-12/-8/-4` frame (p. 3-29).  The fixed HRI line has
    one write slot (adjudication C3), so the model reports the primary
    write (the destination for the interlocked forms, the
    lowest-addressed destination word for DQM, the `ISP-12` source word
    for KCALL) and applies every other store to `state.memory`.  A DQM
    block is read into a temporary before any destination word is
    written; the PRM does not define overlapping source and destination
    blocks, so that order is a model choice.  Extending the line to a
    block write is a contract change, not a semantic choice; until then
    those instructions are not core-diffable.
27. **ISP and VB defaults.**  ISP (pp. 1-12, 1-13) and VB (p. 1-20) are
    architectural but absent from the HRI line.  `State` carries them
    and the CLI defaults them to `0x40` and `0x0`; the PRM prints no
    reset values for either.  KRET/CRET/KCALL therefore change state
    the trace cannot show, and the records remain valid only for their
    observable `SP`/`MSP`/PC/write fields.
28. **DQM's wrong-mode fault.**  p. 3-18's description assigns an
    alignment fault (exception `0x4`) to non-permitted modes while its
    Notes assign an illegal instruction sequence (`0x3`) to the same
    misuse.  This model follows the more specific Notes and raises
    `illegal:`.  The alternative reading would make the same program an
    `alignment:` refusal.
29. **MOVA's immediate source.**  p. 3-33's footnote says the source
    must be a word mode "except for immediate as already noted", while
    its Notes say an immediate source — and a register source or
    destination — is an illegal instruction.  This model follows the
    Notes: only modes `0xC/0xD/0xE` are accepted for the source, and
    mode `0x7` is illegal on either side.
30. **UREM's note copy.**  p. 3-49's note reads "The PSW carry bit is
    always cleared by UDIY" on the UREM page; `UDIY` is a scan/typo for
    `UDIV` copied from p. 3-48.  This model applies the sentence to
    UREM: C cleared, V unchanged.  The alternative — treating the note
    as not applying to UREM — would leave C unchanged.
31. **LDRAA's encoding table.**  The printed table on p. 3-31 is present
    on the page image but dropped by `pdftotext`; OCR of the rendered
    page gives `length 6 | opcode 0x00 | subcode 0xA | LDRAA | flow32`,
    matching Table 1-19 (p. 1-24) and Plan 9 `zl/optab.c`.  This is a
    text-layer limitation, not a semantic ambiguity.

## What the model deliberately is not

It is not a pipeline model, a cache/fetch-delay model, a cycle-by-cycle
simulator, an MMU, an event processor, an assembler, a disassembler or a
second copy of the Bluespec core.  Its `cyc` is a retirement-spacing
account from the printed Chapter 4 base tables, not a simulation of the
EU, the prefetch buffer or the bus.  It knows one instruction at a time
and only the architectural state named above plus the non-architectural
`timing` record.  That is what makes it useful as the independent side of
the HRI comparison.
