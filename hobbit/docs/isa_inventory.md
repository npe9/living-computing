# ATT92010 Hobbit architectural inventory

Primary source: AT&T Microelectronics, *ATT92010 Hobbit Microprocessor
Programmer's Reference Manual*, January 1993
(`docs/ATT92010_Hobbit_Programmers_Reference_Jan93.pdf`). Every claim
below cites the manual's own printed folio. `p. 1-22` means Chapter 1,
printed page 22; the scan's PDF page is `printed + 8` for Chapter 1,
`+ 48` for Chapter 2, `+ 58` for Chapter 3, `+ 110` for Chapter 4,
`+ 119` for Appendix A and `+ 126` for Appendix B. Table numbers are the
manual's (`T1-15`, `T2-1`, …).

Nothing here is taken from the 1991 ATT2100 specification, the data
sheet, or the Plan 9 toolchain except where an "evidence status" entry
says so explicitly. Where the manual is silent, this inventory records
the silence rather than supplying an encoding.

**Coverage summary:** Table 3-1 (printed pp. 3-1 to 3-2) has **46
mnemonic entries**, expanding to **60 assembled spellings** (11 `[3]`
entries each add one spelling; `JMP(F/N)(Y/N)` expands to four). Of the
46, **44 are implemented in hardware** (CRET and KRET implemented but
privileged), and **2 are reserved-unimplemented** (FLUSHD, FLUSHDCE,
which take the unimplemented-instruction sequence). No Table 3-1
mnemonic uses the trapped-niladic vector.

## 1. Instruction forms

### 1.1 Parcel lengths and prefixes

Instructions are built from two-byte parcels and are one, three or five
parcels long (2, 6 or 10 bytes) — p. 1-21. The length prefix is:

| Parcels | Bytes | Prefix (first parcel, high bits) | Cite |
|---|---|---|---|
| 1 | 2 | bit 15 = `0`; bit 14 is opcode[4], not part of a length code | p. 1-21, p. 1-22 |
| 3 | 6 | bits 15:14 = `10` | p. 1-23 |
| 5 | 10 | bits 15:14 = `11` | p. 1-24 |

The manual states the one-parcel rule as "a zero (0) in the most
significant bit distinguishes all one-parcel instruction formats"
(p. 1-21) and prints the field diagrams tabulated below (p. 1-21).
Five-parcel is the general form that can encode two complete 32-bit
addresses; one- and three-parcel forms are compact encodings of it
(p. 1-21). Instructions have at most two operand-addressing fields
(p. 1-21).

### 1.2 One-parcel field layout

The one-parcel form has four subforms, selected by bits 14:10 (p. 1-21,
Table 1-15 p. 1-22, Table 1-16 p. 1-22, Table 1-17 p. 1-22):

| Subform | Bit 15 | Bits 14:10 | Bits 9:0 | Cite |
|---|---|---|---|---|
| Niladic (no operand) | `0` | `0x0B` (`01011`) | 10-bit subcode | p. 1-21, T1-17 p. 1-22 |
| Monadic (one operand) | `0` | 5-bit opcode | 10-bit source (`pcrel10` or `imm10`) | p. 1-21, T1-15 p. 1-22 |
| Stack class | `0` | `0x02` | bits 9:2 = 8-bit stack offset / 16; bits 1:0 = subcode | p. 1-21, T1-16 p. 1-22 |
| Dyadic (two operands) | `0` | 5-bit opcode | bits 9:5 = source, bits 4:0 = destination | p. 1-21, T1-15 p. 1-22 |

Consequences that the field layout makes exact:

* The 5-bit one-parcel opcode is split 1 + 4 across bits 14 and 13:10;
  bits 14:10 therefore read as the documented `opcode[4:3]` row and
  `opcode[2:0]` column of Table 1-15 (p. 1-22). Example: ADD is opcode
  `0x14` = `10100`, i.e. bit 14 = 1 and bits 13:10 = `0100`; the
  Chapter 3 encoding table prints `0x14` (p. 3-5).
* The niladic opcode is the fixed 5-bit value `0x0B`; its 10-bit
  subcode occupies bits 9:0. CLRE is therefore `0x0B`/subcode `0x0A`
  (p. 3-12, T1-17 p. 1-22). The 10-bit subcode field is also what
  p. 1-40 means when it says "one-parcel niladic with an opcode in the
  range `0x200` through `0x3FF`": that is the trap row
  `subcode[9:3] = 1xxxxxx` of Table 1-17 (p. 1-22), not bits 14:10.
* The stack class fixes bits 14:10 to `0x02`; ENTER is subcode 0,
  CATCH 1, RETURN 2, POPN 3 in bits 1:0 (T1-16 p. 1-22, pp. 3-19,
  3-10, 3-40, 3-38).
* The monadic 10-bit source is sign-extended and multiplied by 2 for
  the PC-relative CALL/JMP forms (p. 1-21, p. 1-22); KCALL's `imm10`
  is zero-extended and multiplied by 4 (p. 3-29).

### 1.3 Three-parcel field layout

Three-parcel instructions begin `10` (p. 1-23). First parcel:

| Form | Bits 15:14 | Bits 13:8 | Bits 7:4 | Bits 3:0 | Parcels 2–3 | Cite |
|---|---|---|---|---|---|---|
| Monadic | `10` | opcode[5:0] = `0x00` | operand addressing mode (labelled SMODE) | subcode (4 bits) | operand-hi, operand-lo | p. 1-23, T1-19 p. 1-24 |
| Dyadic | `10` | opcode[5:0] | smode | dmode | source[15:0], destination[15:0] | p. 1-23, T1-18 p. 1-24 |

The monadic subcode is the low nibble (bits 3:0); this is confirmed by
the Chapter 3 encodings (`0x00`/`0x8` CATCH, `0x00`/`0x9` ENTER,
`0x00`/`0xA` LDRAA, `0x00`/`0xB` FLUSHPTE, `0x00`/`0xC` FLUSHPBE,
`0x00`/`0xD` FLUSHDCE, `0x00`/`0xF` POPN, pp. 3-11, 3-20, 3-31,
3-27, 3-26, 3-23, 3-38) and by Table 1-19's row values 0/1 crossed
with its `subcode[2:0]` columns (p. 1-24). The operand addressing mode
in bits 7:4 is encoded like smode: Table 1-21's codes for
CATCH/ENTER/POPN/RETURN and the FLUSH monadics (p. 1-25), Table
1-23's codes for CALL/JMP/LDRAA (p. 1-26).

The 16-bit source and destination fields are sign-extended when used in
immediate or offset modes; used as absolute addresses, their upper 16
bits come from CONFIG bit 17 (PC extension) as described on p. 1-23.

### 1.4 Five-parcel field layout

Five-parcel instructions begin `11`; parcel 1 is opcode[5:0] in bits
13:8, smode in 7:4, dmode in 3:0; parcels 2–3 are source-hi/source-lo
and parcels 4–5 are destination-hi/destination-lo (p. 1-24, T1-20
p. 1-25).

### 1.5 smode/dmode encodings

General 4-bit operand mode, Table 1-21 p. 1-25:

| Code | Mode | Meaning |
|---|---|---|
| `0x0` | `*$addr:B` | byte absolute |
| `0x1` | `*$addr:UB` | unsigned byte absolute |
| `0x2` | `*$addr:H` | half-word absolute |
| `0x3` | `*$addr:UH` | unsigned half-word absolute |
| `0x4` | `Roffset:B` | byte stack offset |
| `0x5` | `Roffset:UB` | unsigned byte stack offset |
| `0x6` | `Roffset:H` | half-word stack offset |
| `0x7` | `Roffset:UH` | unsigned half-word stack offset |
| `0x8` | `*Roffset:B` | byte stack offset indirect |
| `0x9` | `*Roffset:UB` | unsigned byte stack offset indirect |
| `0xA` | `*Roffset:H` | half-word stack offset indirect |
| `0xB` | `*Roffset:UH` | unsigned half-word stack offset indirect |
| `0xC` | `*$addr:W` | word absolute |
| `0xD` | `Roffset:W` | word stack offset |
| `0xE` | `*Roffset:W` | word stack offset indirect |
| `0xF` | `$data` | immediate |

CPU-prefixed instruction modes, Table 1-22 p. 1-26: `0x7` = register,
`0xC` = word absolute, `0xD` = word stack offset, `0xE` = word stack
offset indirect, `0xF` = immediate. The table prints only these five
codes; the CPU description says all word-sized modes remain the same
while mode `0x7` becomes the register mode (p. 3-14).

CALL/JMP modes, Table 1-23 p. 1-26: `0xC` = absolute indirect
(`**$addr`), `0xD` = stack offset indirect (`*Roffset`), `0xE` = label
(program-counter relative), `0xF` = absolute (`*$addr`). Conditional
jumps may not use the indirect modes (p. 3-28).

Register numbers for the CPU escape, Table 1-24 p. 1-26:
`0x1` MSP, `0x2` ISP, `0x3` SP, `0x4` CONFIG, `0x5` PSW, `0x6` SHAD,
`0x7` VB, `0x8` STB, `0x9` FAULT, `0xA` ID, `0xB` TIMER1, `0xC`
TIMER2; `0x0` and `0xD`–`0xF` are unimplemented (the `0x0` case is
stated on p. 1-27, the `0xD`–`0xF` case in T1-24).

### 1.6 Field width, extension and scaling

| Field | Width | Rule | Cite |
|---|---|---|---|
| 5-bit immediate (`imm5`, `uimm5`, `wai5`) | 5 | `imm5` sign-extended; `uimm5` unsigned; `wai5` unsigned and word-aligned (multiplied by 4) | p. 1-21, p. 1-22 |
| 5-bit stack offset (`stk5`) | 5 | zero-extended, then multiplied by 4 | p. 1-21, p. 1-22 |
| 5-bit indirect stack offset (`istk5`) | 5 | zero-extended, then multiplied by 4; offset must be word-aligned or alignment fault `0x4` | p. 1-22, p. 1-27 |
| 10-bit CALL/JMP PC offset (`pcrel10`) | 10 | sign-extended, then multiplied by 2 | p. 1-21, p. 1-22 |
| 10-bit KCALL immediate (`imm10`) | 10 | zero-extended, then multiplied by 4 | p. 1-21, p. 3-29 |
| 8-bit stack offset (`stk8`) | 8 | zero-extended, then multiplied by 16; ENTER's is one-filled, then multiplied by 16 | p. 1-21, pp. 3-11, 3-20, 3-38, 3-40 |
| 16-bit source/destination | 16 | sign-extended in immediate/offset modes; absolute upper half via CONFIG PC-extension bit | p. 1-23 |
| 32-bit source/destination | 32 | full 32-bit value | p. 1-24 |

#### 1.6.1 Stack-offset-indirect resolution and the two read ports

All sixteen general codes of Table 1-21 are modelled. A
stack-offset-indirect operand (`0x8`-`0xB`, `0xE`) is two accesses
(p. 1-27): the pointer word at `CSP + offset`, fetched with the other
operand in the execution unit's first stage on the stack cache's two
printed read ports (Figure 1-1, p. 1-2, prints `64x32x2`), and then the
one word the pointer names, fetched in the second stage on one port.
The two stages never read in the same clock — the hand-off into EU_S2
needs an empty input slot and EU_S2's step needs a full one — so the
box keeps exactly two read ports and the instruction keeps its
Table 4-32 occupancy (1 cycle for `MOV`, p. 4-3). The offset's
word-alignment rule and the pointed-to address's width-alignment rule
(pp. 1-27, 1-4) are the exception `0x4` alignment fault (Table 1-26,
p. 1-38).

Until 2026-11-20 the decoder refused an instruction that needs a
pointed-to word for *both* operands (both fields indirect and both read
as values, e.g. `ADD *R4,*R8`, or an indirect byte/half store with an
indirect source), on the argument that it would need a third cache
port.  It does not: the two pointer words are EU_S1's reads and the two
pointed-to words are EU_S2's, a clock later, on the same two ports
(`HobbitCore.bsv` `readPointed2`; golden 019).  1st Edition Plan 9
executes the form within 300 instructions (`CMPEQ *R24.UB, *R28.UB`).
`MOV` with a word destination (including the one-parcel `MOV.II`) needs
only the source's word — a word store has no old word to merge (p. 1-4)
— and `MOVA` uses its source as an address (p. 3-33), so both fit the
printed ports.

`mkHobbitStackCache` keeps the printed `64x32x2` as a declared shape,
not a `RegFile`: bsc's `mkRegFile*` caps statically reachable read
ports at five and counts call sites, so the two EU stages plus the
testbench probe exceed it even though they never read in the same
clock. The array is a `Vector#(64, Reg#(Word))`; reads are
combinational muxes and the one write per retirement is unchanged. The
cost is LUTs (`docs/area_analysis.md` measured 12,107 LUT4 for this
shape against 132 LUT4 for a `RegFile`), not ports.

A word outside `[SP, MSP)` is memory (p. 1-5: such addresses are
"normal memory"; p. 1-27 sends a negative stack offset off-chip), and the
model reads it from memory: the absolute modes `0x0`-`0x3`/`0xC`, a
stack offset outside the window and a pointer's target are fetched
through the stack-cache box's one registered memory read port before the
instruction leaves EU_S1, one clock per word
(`docs/conformance_1to1.md` §1a).  Until 2026-11-19 such a word read as
zero; golden `016` pins the five cases, and the pointed-to word still
reaches EU_S2 on one port — EU_S1 supplies it only when it is not in the
cache.

### 1.7 Width suffixes

The PRM prints the operand suffixes on p. 1-28:

| Suffix | Printed meaning | Cite |
|---|---|---|
| `:B` | signed byte | p. 1-28 |
| `:UB` | unsigned byte | p. 1-28 |
| `:H` | half-word (not printed in the p. 1-28 list; defined by the mode table) | Table 1-21 p. 1-25 |
| `:UH` | *printed* "signed half-word" | p. 1-28 |
| `:W` | word | p. 1-28 |

A missing suffix implies signed word operands (p. 1-28). The printed
list is defective (see §7): Table 1-21 p. 1-25 defines both `:H`
(half-word) and `:UH` (unsigned half-word), and the six integer data
types are signed/unsigned byte, half-word and word (p. 1-3). The
inventory therefore records the mode table as authoritative and the
p. 1-28 list as an erratum.

### 1.8 Accumulator (`[3]`) rule

`ADD[3]` denotes both `ADD` and `ADD3`; `JMP(F/N)(Y/N)` denotes
`JMPFY`, `JMPFN`, `JMPTY`, `JMPTN` (p. 3-1). A trailing `3` on a
dyadic instruction means the 32-bit result is stored in the
accumulator instead of the destination operand, making it a
"two-and-a-half-operand" instruction (p. 3-1, p. 1-3, p. 1-28). The
accumulator is named `R4` in that notation (p. 3-1, p. 1-28).

The accumulator is **not a hardware register**: it is the word in
memory at `CSP + 4`, above the word addressed by the current stack
pointer, where CSP is SP or ISP according to PSW bit 9 (p. 1-7,
Figure 1-4). It normally lives in the stack cache but may be off-chip
when `SP = MSP` or when CSP is the ISP (p. 1-7). The PC-save slot for
CALL and for the unimplemented-instruction exception is at `CSP`
itself (p. 1-7, p. 1-31); `R4`, the stack offset 4, is therefore the
first data word above the save slot.

### 1.9 Registers, `%SHAD` and the `CPU` escape

There are no programmer-visible general registers (p. 1-1). Internal
registers are reached by the `CPU` niladic prefix, which is not
executed by itself but rewrites the address-mode interpretation of the
instruction that follows: mode `0x7` becomes the register mode while
the word modes `0xC`–`0xF` keep their meaning (p. 1-27, p. 3-14,
T1-22 p. 1-26). The register number is the low 4 bits of the operand
field; higher operand bits are ignored and should be zero (p. 1-27,
p. 3-14). At most one register may be read per instruction; reading
register `0x0` or `0xD`–`0xF` raises the unimplemented-register
exception (ID `0x6`), reads are allowed in user mode, and a register
write in user mode raises the privilege-violation exception (ID `0x5`)
(p. 1-27).

The PRM's own examples name control registers with a `%` prefix:
`MOV %SP, %SHAD` and `MOV %ISP, %SHAD` (p. 1-15), and
`MOV $new, %SHAD`, `ADD $16, %SHAD` (p. 3-3). The examples the manual
prints use the `%name` form and never show the literal `CPU` mnemonic,
so the assembled spelling of the escape (whether `CPU` is written
explicitly or implied by a `%name` operand) is not stated. `R4`, `R8`, `R20` etc. in the examples
are stack offsets in words, not registers: `RETURN R4` fetches the new
PC from stack offset 4 (p. 3-40), and `MUL $0x7F,R4:B` addresses a
byte at stack offset 4 (p. 3-3).

## 2. Instruction inventory: all 46 Table 3-1 entries

Status legend: **HW** = implemented in hardware; **HW-P** =
implemented, privileged (privilege-violation exception ID `0x5` at
user level); **UNIMP** = not implemented in hardware, the
unimplemented-instruction sequence is taken (PC of the opcode saved at
CSP, PC ← `*(VB+12)`, p. 1-39); **TRAP** = trapped niladic via
`*(VB+8)` (p. 1-40). No row below is a TRAP; that vector is selected
only by niladic subcodes `0x200`–`0x3FF` (T1-17 p. 1-22, p. 1-40).

Encoding columns use `1p`/`3p`/`5p` for one/three/five parcels and the
manual's operand abbreviations: `imm5`, `uimm5`, `wai5`, `stk5`,
`istk5`, `stk8`, `stk32`, `gen16`, `gen32`, `word32`, `flow32`,
`abs32`, `pcrel10`, `imm10` (definitions: Table 3-2 p. 3-4; field
rules §1.6). Every row cites its printed encodings page; table pages
are cited where they add the opcode/subcode source.

| # | Mnemonic (spellings) | Parcels | Opcode / subcode and page | Operand modes | Semantics | Status |
|---|---|---|---|---|---|---|
| 1 | ADD[3] (ADD, ADD3) | 1, 3, 5 | 1p: ADD `0x14` imm5,stk5; ADD3 `0x15` imm5,stk5; ADD `0x16` stk5,stk5; ADD3 `0x17` stk5,stk5 (T1-15 p. 1-22); 3p/5p: ADD `0x23`, ADD3 `0x33` (T1-18 p. 1-24, T1-20 p. 1-25); encodings p. 3-5 | imm5/stk5, stk5/stk5, gen16/gen16, gen32/gen32 | `dst += src` (ADD) or `Acc = dst + src` (ADD3); C set on unsigned overflow, V on signed overflow, else both cleared (p. 3-5) | HW |
| 2 | ADDI | 3, 5 | `0x03` gen16,gen16 / gen32,gen32 (T1-18 p. 1-24, T1-20 p. 1-25); encodings p. 3-6 | gen16/gen16, gen32/gen32 | Interlocked fetch-add-store to dst; original dst saved in Acc; C and V unaffected; not restartable if the Acc store faults (p. 3-6) | HW |
| 3 | AND[3] (AND, AND3) | 1, 3, 5 | 1p: AND3 `0x0E` imm5,stk5; AND `0x0F` stk5,stk5 (T1-15 p. 1-22); 3p/5p: AND `0x22`, AND3 `0x32` (T1-18 p. 1-24, T1-20 p. 1-25); encodings p. 3-7 | imm5/stk5, stk5/stk5, gen16/gen16, gen32/gen32 | Bitwise AND; result to dst (AND) or Acc (AND3) (p. 3-7) | HW |
| 4 | ANDI | 3, 5 | `0x02` gen16,gen16 / gen32,gen32 (T1-18 p. 1-24, T1-20 p. 1-25); encodings p. 3-8 | gen16/gen16, gen32/gen32 | Interlocked bitwise AND into dst; original dst saved to Acc; C/V handling is not stated on the page (p. 3-8) | HW |
| 5 | CALL | 1, 3 | 1p: `0x01` pcrel10 (T1-15 p. 1-22); 3p: `0x00`/sub `0x1` flow32 (T1-19 p. 1-24); encodings p. 3-9 | pcrel10, flow32 | Store next PC at `*(CSP)` (the R0 slot), then PC ← src; the target-PC fetch fault saves the target PC (p. 3-9, p. 1-34) | HW |
| 6 | CATCH | 1, 3 | 1p: `0x02`/sub `0x1` stk8 (T1-16 p. 1-22); 3p: `0x00`/sub `0x8` word32 (T1-19 p. 1-24); encodings pp. 3-10, 3-11 | stk8, word32 | If CSP = SP, refill stack cache in 16-byte blocks from MSP until `MSP >= CSP+src` or the cache is full; no-op if CSP = ISP (p. 3-10) | HW |
| 7 | CLRE | 1 | `0x0B`/sub `0x0A` (T1-17 p. 1-22); encodings p. 3-12 | none | Clear the PSW enter-guard bit (p. 3-12) | HW |
| 8 | CMPEQ | 1, 3, 5 | 1p: `0x10` imm5,stk5 and `0x13` stk5,stk5 (T1-15 p. 1-22); 3p/5p: `0x1F` (T1-18 p. 1-24, T1-20 p. 1-25); encodings p. 3-13 | imm5/stk5, stk5/stk5, gen16/gen16, gen32/gen32 | `PSW.F = (src1 == src2)`; operands are source field = src1, destination field = src2 (p. 3-13) | HW |
| 9 | CMPGT | 1, 3, 5 | 1p: `0x11` stk5,stk5 and `0x12` imm5,stk5 (T1-15 p. 1-22); 3p/5p: `0x1D` (T1-18 p. 1-24, T1-20 p. 1-25); encodings p. 3-13 | stk5/stk5, imm5/stk5, gen16/gen16, gen32/gen32 | `PSW.F = signed(src1 > src2)` (p. 3-13) | HW |
| 10 | CMPHI | 3, 5 | `0x1E` gen16/gen16, gen32/gen32 (T1-18 p. 1-24, T1-20 p. 1-25); encodings p. 3-13 | gen16/gen16, gen32/gen32 | `PSW.F = unsigned(src1 > src2)` (p. 3-13) | HW |
| 11 | CPU | 1 | `0x0B`/sub `0x0` (T1-17 p. 1-22); encodings p. 3-14 | none | Escape prefix that changes the next instruction's addressing so mode `0x7` selects an internal register (p. 3-14) | HW |
| 12 | CRET | 1 | `0x0B`/sub `0x5` (T1-17 p. 1-22); encodings p. 3-15 | none | Context return from kernel: load SP from `*(ISP+0)`, unconditional CATCH to `*(ISP+4)`, restore MSP, PC ← `*(ISP+8)`, PSW ← `*(ISP+12)`, `ISP += 16`; untraceable (pp. 3-15, 3-16) | HW-P |
| 13 | DIV[3] (DIV, DIV3) | 3, 5 | `0x27` DIV, `0x37` DIV3 (T1-18 p. 1-24, T1-20 p. 1-25); encodings p. 3-17 | gen16/gen16, gen32/gen32 | `dst = dst / src` two's-complement (DIV) or `Acc = dst / src` (DIV3); divide-by-zero exception; `0x80000000 / -1` sets V and returns `0x80000000`, C unchanged (p. 3-17) | HW |
| 14 | DQM | 3, 5 | `0x07` (T1-18 p. 1-24, T1-20 p. 1-25); encodings p. 3-18 | word modes with size selected by dst mode: dst `0x0`/`0x4`/`0x8` = double-word, dst `0xC`/`0xD`/`0xE` = quad-word; src `0xF` replicates the constant; dst `0xF` illegal; the description and Notes disagree on the fault for other modes (see §7) (p. 3-18) | Move two or four contiguous words src → dst; double-word must be 8-byte aligned, quad-word 16-byte aligned, else alignment exception (p. 3-18) | HW |
| 15 | ENTER | 1, 3 | 1p: `0x02`/sub `0x0` stk8 (T1-16 p. 1-22); 3p: `0x00`/sub `0x9` word32 (T1-19 p. 1-24); encodings pp. 3-19, 3-20 | stk8, word32 | Allocate a stack frame: stack-offset mode adjusts CSP by the offset, other modes replace CSP; flushes stack cache only when CSP = SP, in 16-byte blocks; sets PSW.E on successful completion (pp. 3-19, 3-20, 3-21) | HW |
| 16 | FLUSHD | 1 | `0x0B`/sub `0x6` (T1-17 p. 1-22); encodings p. 3-22 | none | "Flush data cache"; there is no data cache, so the unimplemented-instruction sequence is taken (p. 3-22) | UNIMP |
| 17 | FLUSHDCE | 3 | `0x00`/sub `0x0D` word32 (T1-19 p. 1-24); encodings p. 3-23 | word32 | "Flush a data-cache entry"; no data cache, so the unimplemented-instruction sequence is taken (p. 3-23) | UNIMP |
| 18 | FLUSHI | 1 | `0x0B`/sub `0x3` (T1-17 p. 1-22); encodings p. 3-24 | none | Flush the decoded instruction cache (all entries invalid) (p. 3-24) | HW |
| 19 | FLUSHP | 1 | `0x0B`/sub `0x4` (T1-17 p. 1-22); encodings p. 3-25 | none | Flush the prefetch buffer cache (all entries invalid) (p. 3-25) | HW |
| 20 | FLUSHPBE | 3 | `0x00`/sub `0x0C` word32 (T1-19 p. 1-24); encodings p. 3-26 | word32 | Mark the quad-word at src invalid in the PFB; no other cache affected (p. 3-26) | HW |
| 21 | FLUSHPTE | 3 | `0x00`/sub `0x0B` word32 (T1-19 p. 1-24); encodings p. 3-27 | word32 (normally a stack-offset-indirect address moved into the stack cache) | If a page-table entry for src exists in either TLB, invalidate it; invalidate both nonpaged segment registers (p. 3-27, p. 2-8) | HW |
| 22 | JMP | 1, 3 | 1p: `0x03` pcrel10 (T1-15 p. 1-22); 3p: `0x00`/sub `0x3` flow32 (T1-19 p. 1-24); encodings p. 3-28 | pcrel10, flow32 | Unconditional PC ← address of dst (p. 3-28) | HW |
| 23 | JMP(F/N)(Y/N) (JMPFY, JMPFN, JMPTY, JMPTN) | 1, 3 | 1p: JMPFN `0x04`, JMPFY `0x05`, JMPTN `0x06`, JMPTY `0x07`, all pcrel10 (T1-15 p. 1-22); 3p: `0x00`/sub `0x4`–`0x7` abs32 (T1-19 p. 1-24); encodings p. 3-28 | pcrel10, abs32; indirect modes illegal | JMPT jumps if `PSW.F = 1`, JMPF if `PSW.F = 0`; trailing Y/N is the static prediction (Y = likely taken) (p. 3-28, p. 1-33) | HW |
| 24 | KCALL | 1, 3 | 1p: `0x00` imm10 (T1-15 p. 1-22); 3p: `0x00`/sub `0x0` word32 (T1-19 p. 1-24); encodings p. 3-29 | imm10 (×4, 0–4092), word32 | Kernel call: push src, return PC and PSW as a quad-word event frame on the interrupt stack, `ISP -= 16`, PC ← `*(VB+0)`, low 16 PSW bits cleared (p. 3-29) | HW |
| 25 | KRET | 1 | `0x0B`/sub `0x1` (T1-17 p. 1-22); encodings p. 3-30 | none | Kernel return: PC ← `*(ISP+8)`, PSW ← `*(ISP+12)`, `ISP += 16`; privileged and untraceable (p. 3-30) | HW-P |
| 26 | LDRAA | 3 | `0x00`/sub `0x0A` flow32 (T1-19 p. 1-24); encodings p. 3-31 (the printed table is present; pdftotext drops it — see §7) | flow32 | `Acc = &dst`; the address is computed exactly as a JMP target (p. 3-31) | HW |
| 27 | MOV | 1, 3, 5 | 1p: `0x0A` wai5,stk5; `0x18` stk5,stk5; `0x19` istk5,stk5; `0x1A` stk5,istk5; `0x1B` istk5,istk5; `0x1C` imm5,stk5 (T1-15 p. 1-22); 3p/5p: `0x06` (T1-18 p. 1-24, T1-20 p. 1-25); encodings p. 3-32 | wai5, imm5, stk5, istk5, gen16/gen16, gen32/gen32 | `dst = src` (p. 3-32) | HW |
| 28 | MOVA | 1, 3, 5 | 1p: `0x1D` stk5,stk5 (T1-15 p. 1-22); 3p/5p: `0x04` (T1-18 p. 1-24, T1-20 p. 1-25); encodings p. 3-33 | stk5/stk5, gen16\*/gen16, gen32\*/gen32 (\*source must be a word mode; immediate is disputed — see §7); the Notes also make a register source or destination illegal | `dst = &src`; if dst is byte/half-word the address is truncated or sign-extended (p. 3-33) | HW |
| 29 | MUL[3] (MUL, MUL3) | 3, 5 | `0x26` MUL, `0x36` MUL3 (T1-18 p. 1-24, T1-20 p. 1-25); encodings p. 3-34 | gen16/gen16, gen32/gen32 | Multiply src by dst, product to dst (MUL) or Acc (MUL3); C on unsigned overflow, V on signed overflow (p. 3-34) | HW |
| 30 | NOP | 1 | `0x0B`/sub `0x2` (T1-17 p. 1-22); encodings p. 3-35 | none | No operation (p. 3-35) | HW |
| 31 | OR[3] (OR, OR3) | 3, 5 | `0x21` OR, `0x31` OR3 (T1-18 p. 1-24, T1-20 p. 1-25); encodings p. 3-36 | gen16/gen16, gen32/gen32 | Bitwise OR; result to dst or Acc (p. 3-36) | HW |
| 32 | ORI | 3, 5 | `0x01` (T1-18 p. 1-24, T1-20 p. 1-25); encodings p. 3-37 | gen16/gen16, gen32/gen32 | Interlocked bitwise OR into dst; original dst saved to Acc; C/V handling is not stated on the page (p. 3-37) | HW |
| 33 | POPN | 1, 3 | 1p: `0x02`/sub `0x3` stk8 (T1-16 p. 1-22); 3p: `0x00`/sub `0x0F` stk32 (T1-19 p. 1-24); encodings p. 3-38 | stk8, stk32; only stack-offset mode legal, nonnegative | `SHAD = CSP = CSP + src`; if CSP = SP and the new value exceeds MSP, MSP is set to the new value; MSP not updated when CSP = ISP (p. 3-38) | HW |
| 34 | RETURN | 1, 3 | 1p: `0x02`/sub `0x2` stk8 (T1-16 p. 1-22); 3p: `0x00`/sub `0x2` stk32 (T1-19 p. 1-24); encodings p. 3-40 | stk8, stk32; only stack-offset mode legal, nonnegative | New PC ← `*(CSP+src)`, then `SHAD = CSP = CSP + src`; MSP updated as for POPN; low 4 bits of the offset ignored when adjusting SP (p. 3-40) | HW |
| 35 | REM[3] (REM, REM3) | 3, 5 | `0x25` REM, `0x35` REM3 (T1-18 p. 1-24, T1-20 p. 1-25); encodings p. 3-39 | gen16/gen16, gen32/gen32 | Remainder of signed dst/src to dst or Acc; V always cleared, C unchanged; divide-by-zero exception (p. 3-39) | HW |
| 36 | SHL[3] (SHL, SHL3) | 1, 3, 5 | 1p: SHL3 `0x1E` uimm5,stk5 (T1-15 p. 1-22); 3p/5p: SHL `0x2E`, SHL3 `0x3E` (T1-18 p. 1-24, T1-20 p. 1-25); encodings p. 3-41 | uimm5/stk5, gen16/gen16, gen32/gen32 | `dst <<= unsigned(src)`; only the low 5 bits of src are used; zeros fill; SHL3 leaves dst unchanged and writes Acc (p. 3-41) | HW |
| 37 | SHR[3] (SHR, SHR3) | 1, 3, 5 | 1p: SHR3 `0x1F` uimm5,stk5 (T1-15 p. 1-22); 3p/5p: SHR `0x2C`, SHR3 `0x3C` (T1-18 p. 1-24, T1-20 p. 1-25); encodings p. 3-42 | uimm5/stk5, gen16/gen16, gen32/gen32 | Arithmetic right shift, sign bit replicated; low 5 bits of src select the count; SHR3 leaves dst unchanged and writes Acc (p. 3-42) | HW |
| 38 | SUB[3] (SUB, SUB3) | 3, 5 | `0x20` SUB, `0x30` SUB3 (T1-18 p. 1-24, T1-20 p. 1-25); encodings p. 3-43 | gen16/gen16, gen32/gen32 | `dst -= src` (SUB) or `Acc = dst - src` (SUB3); C on unsigned borrow/overflow, V on signed overflow (p. 3-43) | HW |
| 39 | TADD | 3, 5 | `0x0C` (T1-18 p. 1-24, T1-20 p. 1-25); encodings p. 3-44 | gen16/gen16, gen32/gen32 | Tagged add: if either low 2 bits is nonzero, F = 1 and no store; else add and set F = V, storing only when F = 0 (p. 3-44) | HW |
| 40 | TESTC | 1 | `0x0B`/sub `0x9` (T1-17 p. 1-22); encodings p. 3-45 | none | `PSW.F = PSW.C`, then `PSW.C = 0` (p. 3-45) | HW |
| 41 | TESTV | 1 | `0x0B`/sub `0x8` (T1-17 p. 1-22); encodings p. 3-46 (printed table present; pdftotext drops it — see §7) | none | `PSW.F = PSW.V`, then `PSW.V = 0` (p. 3-46) | HW |
| 42 | TSUB | 3, 5 | `0x0D` (T1-18 p. 1-24, T1-20 p. 1-25); encodings p. 3-47 | gen16/gen16, gen32/gen32 | Tagged subtract with the same tag/overflow rules as TADD (p. 3-47) | HW |
| 43 | UDIV | 3, 5 | `0x2F` (T1-18 p. 1-24, T1-20 p. 1-25); encodings p. 3-48 | gen16/gen16, gen32/gen32 | Unsigned dst/src to dst; divide-by-zero exception; C always cleared, V unchanged (p. 3-48) | HW |
| 44 | UREM | 3, 5 | `0x05` (T1-18 p. 1-24, T1-20 p. 1-25); encodings p. 3-49 | gen16/gen16, gen32/gen32 | Unsigned remainder to dst; divide-by-zero exception; C always cleared, V unchanged (p. 3-49) | HW |
| 45 | USHR[3] (USHR, USHR3) | 3, 5 | `0x2D` USHR, `0x3D` USHR3 (T1-18 p. 1-24, T1-20 p. 1-25); encodings p. 3-50 | gen16/gen16, gen32/gen32 | Logical right shift, zeros fill; low 5 bits of src select the count; USHR3 leaves dst unchanged and writes Acc (p. 3-50) | HW |
| 46 | XOR[3] (XOR, XOR3) | 3, 5 | `0x24` XOR, `0x34` XOR3 (T1-18 p. 1-24, T1-20 p. 1-25); encodings p. 3-51 | gen16/gen16, gen32/gen32 | Bitwise exclusive OR; result to dst or Acc (p. 3-51) | HW |

Summary: **46 rows**, 60 spellings, 44 HW (including CRET and KRET,
which are HW-P), 2 UNIMP (FLUSHD, FLUSHDCE), 0 TRAP.

## 3. Control registers

Table 1-1 (p. 1-8) lists 13 control registers. The CPU-escape register
numbers are from Table 1-24 (p. 1-26). PC has no CPU-escape number; it
is manipulated only by control-flow instructions and is read by LDRAA
(p. 1-13).

| Register | CPU # | Bit fields | Notes | Cite |
|---|---|---|---|---|
| CONFIG | `0x4` | 31:25 Timer2 config; 24:22 Timer1 config; 21 prefetch mode; 20 prefetch-buffer enable; 19 instruction-cache enable; 18 stack-cache enable; 17 PC extension; 16 kernel little-endian; 15:0 reserved (=0) | Reset to 0; all caches disabled, timer interrupts off, demand prefetch after reset (p. 1-36) | T1-2 pp. 1-9, 1-10 |
| FAULT | `0x9` | 31:0 fault address | Holds the 32-bit operand-aligned virtual address for exception IDs `0x8` and `0x9` | pp. 1-10, 1-11; p. 1-39 |
| ID (JTAG) | `0xA` | 31:28 version; 27:12 part code; 11:0 manufacturer | Read-only (writes are no-ops); part code 0, manufacturer `0x3B`, version 0 or 1 by mask | pp. 1-11 |
| ISP | `0x2` | 31:4 quad-aligned interrupt stack pointer; 3:0 reserved | Not associated with the stack cache; must always be valid | pp. 1-12, 1-20 |
| MSP | `0x1` | 31:4 quad-aligned maximum stack pointer; 3:0 reserved | Must satisfy `SP <= MSP <= SP+256`; implicit updates by CATCH/CRET/ENTER/POPN/RETURN | p. 1-13 |
| PC | — | 31:1 program counter; bit 0 reserved | Always even (parcel-aligned); cannot be directly manipulated by a general instruction; read by LDRAA and changed only by CALL/CRET/JMP/KCALL/KRET/RETURN | pp. 1-13, 1-14 |
| PSW | `0x5` | 16 V/P addressing; 15 user little-endian; 14:12 interrupt priority level; 11 enter guard; 10 execution level; 9 current stack pointer; 8 trace basic block; 7 trace instruction; 6 overflow (V); 5 carry (C); 4 flag (F); 3:0 reserved | Reset to 0; event sequences alter only the low 16 bits | T1-8 pp. 1-14 to 1-16 |
| SHAD | `0x6` | 31:4 quad-aligned CSP shadow; 3:0 reserved | Copy of CSP maintained for instruction restart; updated by CRET/ENTER/KCALL/KRET/RETURN and any CSP change | pp. 1-16, 1-17 |
| SP | `0x3` | 31:4 quad-aligned user stack pointer; 3:0 reserved | Stack grows downward toward 0; SP as the direct destination of a CPU-prefixed instruction also writes MSP | pp. 1-17, 1-13 |
| STB | `0x8` | 31:12 page-aligned segment table base; 11 cache bit; 10:0 reserved | A write flushes all TLB and NPSR entries (PFB/IC/SC are not flushed) | p. 1-18 |
| TIMER1 | `0xB` | 31:0 count value | Configured by CONFIG 24:22 | p. 1-19 |
| TIMER2 | `0xC` | 31:0 count value | Configured by CONFIG 31:25 | p. 1-19 |
| VB | `0x7` | 31:4 quad-aligned vector table base; 3:0 reserved | Vector table must always be available; a faulted vector access resets the part | p. 1-20 |

CONFIG timer fields (p. 1-9): Timer2 bit 31 enables its interrupt
(level 1); bit 30 = 1 restricts it to kernel mode; bits 29:25 select
the counted event: `00000` clock cycles, `00001` completed
instructions (folded branches not counted), `11111` do not increment
(low-power). Timer1 bit 24 enables its interrupt (level 1; external
level 1 has priority over Timer1, and external level 1 and Timer1 have
priority over Timer2); bit 23 = kernel-only; bit 22 selects cycles (0)
or completed instructions (1). CONFIG bit 21: 0 = demand prefetching
(no off-chip prefetch), 1 = aggressive prefetching. Bit 17 PC
extension: 0 = zero-extend 16-bit absolute addresses; 1 = copy bits
31:29 from the PC and zero bits 28:16 (pp. 1-9, 1-10, 1-23). Bit 16:
0 = big-endian data in kernel mode, 1 = little-endian data (p. 1-10).
Bit 18/19/20 enable the stack cache/instruction cache/prefetch buffer
without flushing or altering them (p. 1-10).

PSW details (T1-8 pp. 1-14 to 1-16): bit 16, 0 = physical addressing
and NCACHE asserted, 1 = virtual; bit 15 user little-endian; bits
14:12 interrupt priority level (an interrupt is accepted when its
level is below IPL; IPL = 7 enables all, IPL = 0 allows only level 0);
bit 11 enter guard, set by an ENTER that caused no flush, cleared by
CLRE; bit 10, 0 = kernel, 1 = user; bit 9, 0 = ISP is CSP, 1 = SP is
CSP (changing it by a direct PSW write requires the SHAD update
described on p. 1-15/1-17); bit 8 basic-block trace; bit 7 instruction
trace (if both trace bits are set, instruction trace wins); bit 6 V;
bit 5 C; bit 4 F. The exception/interrupt sequences save the low 16
bits and force `PSW &= 0xFFFF0000` (pp. 1-37, 1-38).

## 4. Stack cache and integer accumulator

### 4.1 Organization

The stack cache is 64 four-byte registers (256 bytes) organized as a
circular buffer maintained by two 28-bit quad-word addresses, MSP and
SP (p. 1-5). MSP is the address above the highest cached data; SP
delimits the lowest cached data (p. 1-5). It is byte-addressable and
appears as normal memory to all virtual addresses (p. 1-5). Address
hits are a range check: p. 1-5 displays `SP <= ADDR < MSP`, and
p. 1-12's prose says "greater than, or equal to, the SP" but its
displayed relation is the strict `SP < address < MSP` — see §7. MSP
must satisfy `SP <= MSP <= SP + 256`, or stack-cache accesses are
unpredictable (p. 1-13). When SP is the
direct destination of a CPU-prefixed instruction, MSP is written with
the same value, defining an empty cache (p. 1-13).

Hardware, not the compiler, allocates these registers; the machine has
no programmer-visible general registers (p. 1-5). The top 64 words of
the stack are therefore on-chip for most frames (p. 1-6).

### 4.2 Maintenance by CALL / CATCH / CRET / ENTER / POPN / RETURN

Six instructions maintain the stack cache (p. 1-6):

| Instruction | Stack-cache action | Cite |
|---|---|---|
| CALL | Moves the return address to the top of the stack (`*(CSP)`) and branches; the PC slot is the cache word at CSP | p. 1-6, p. 3-9 |
| CATCH | Fills the cache to the depth named by its operand, in 16-byte quad-word blocks, by copying memory to `stack_cache[MSP]` while `MSP < CSP+src` and `MSP-SP < 256` (the pseudocode's condition; the prose defines the target MSP per addressing mode — §7); rounds a non-16-multiple operand up to the next 16; no-op when CSP = ISP | pp. 3-10, 3-11, p. 1-7 |
| CRET | Loads a new SP from `*(ISP+0)`, discards the current cache contents, performs an unconditional CATCH to the fetched MSP, then restores MSP/PC/PSW | p. 3-15 |
| ENTER | Allocates a new frame. If the new frame is < 256 bytes, flushes only `frame size minus free entries`; if >= 256 bytes, flushes all valid entries and keeps only the part of the new frame nearest SP. Stack-offset mode flushes only as much as necessary; other source modes flush unconditionally and force `SHAD = MSP = SP = target`. Flushing is in quad-word (16-byte) transfers | pp. 1-6, 3-19, 3-20 |
| POPN | `SHAD = CSP = CSP + src`; if CSP = SP and the new value exceeds MSP, `MSP = SP` (the new value) | p. 3-38 |
| RETURN | Fetches the new PC from `*(CSP + src)`, then advances `SHAD = CSP = CSP + src` and updates MSP exactly as POPN does | p. 3-40 |

Additional constraints:

* ENTER's stack-offset form may be used only with negative offsets;
  positive offsets (including `ENTER R0`) take the illegal-instruction
  sequence. The 6-byte ENTER with a stack-offset source requires
  `|offset| > SCSIZE` and `offset <= 0` (p. 3-21).
* CATCH requires `MSP >= SP`, otherwise operation is unpredictable
  (p. 3-11).
* RETURN and POPN allow only stack-offset mode; negative offsets are
  illegal (pp. 3-38, 3-40). RETURN may read a new PC from a word
  offset that is not a multiple of 16, but the low 4 bits are ignored
  when adjusting SP (p. 3-40).
* ENTER's 1-parcel offset is one-filled before scaling, giving a range
  of -16 to -4096 in quad-aligned decrements (p. 3-20); CATCH, POPN
  and RETURN zero-extend their 1-parcel offset and scale by 16, giving
  0 to 4080 (pp. 3-11, 3-38, 3-40).
* A page-table invalidation (FLUSHPTE) must be followed by two
  instructions before an ENTER into that page (p. 3-3).

### 4.3 CSP = ISP caveat

When the PSW CSP bit selects the ISP, the stack cache is out of the
picture: CATCH is a no-op (p. 3-10); ENTER performs no stack-cache
traffic and does not update MSP (p. 3-20); POPN and RETURN do not
update MSP (pp. 3-38, 3-40). The conceptual "any address between SP
and MSP is cached" model is violated while CSP = ISP, but there is no
problem as long as the SP-based stack cache and the ISP-based interrupt
stack do not overlap (p. 1-8). The ISP itself is not associated with
the stack cache (p. 1-12).

### 4.4 Addresses forbidden between SP and MSP

The following addresses must not lie between SP and MSP (p. 1-8):

* the vector table defined by VB;
* the MMU address-translation tables;
* any text address.

### 4.5 Integer accumulator

The integer accumulator is not a hardware register. It is the word in
memory above the word addressed by CSP, i.e. `CSP + 4`; CSP is SP or
ISP according to PSW bit 9 (p. 1-7, Figure 1-4). It normally resides
on-chip in the stack cache, but may be off-chip when `SP = MSP` or
`CSP = ISP` (p. 1-7). The word at CSP is the PC save area for CALL and
for the unimplemented-instruction exception (p. 1-7, pp. 1-31, 1-39).
Instructions whose mnemonic ends in `3` write this word with the full
32-bit result (p. 1-28, p. 1-3); the interlocked ADDI, ANDI and ORI
also save the old destination there (pp. 3-6, 3-8, 3-37).

## 5. Memory management unit

### 5.1 Organization and address mapping

The 32-bit virtual address space is 1,024 segments of 4 MB each, 4 MB
aligned (p. 2-1). Two translation methods exist (p. 2-1):

* **Paged segments** divide a segment into 1,024-word pages; each page
  is 4 KB (1,024 words) and can map anywhere in the 32-bit physical
  space (pp. 2-1, 2-4).
* **Nonpaged segments** provide a variable-size contiguous segment
  (p. 2-1).

Address translation is enabled by PSW bit 16 = 1 (p. 2-1). The MMU has
two 32-entry fully associative TLBs, one for text and one for data, plus
one text micro-TLB holding the last prefetch translation, plus two
nonpaged segment registers (NPSRs), one text and one data (p. 2-1).
A TLB/NPSR miss walks the in-memory tables (p. 2-1).

Virtual-address fields (Figures 2-1 and 2-2, p. 2-2):

| Mapping | Segment | Page | Offset | Cite |
|---|---|---|---|---|
| Paged | VA 31:22 (10 bits) | VA 21:12 (10 bits) | VA 11:0 | p. 2-2 |
| Nonpaged | VA 31:22 (10 bits) | — | VA 21:0 | p. 2-2 |

Physical address = page-frame base (from the PTE) concatenated with the
12-bit page offset, or segment base (from the STE) concatenated with the
22-bit segment offset (pp. 2-4, 2-6). All map tables are 4,096 bytes
(one page frame), and all addresses inside a map table are physical, so
translation is not recursive (p. 2-3).

### 5.2 Segment table

The segment table has 1,024 4-byte entries in one 4 KB page frame; STB
holds its base (p. 2-4). A segment-table entry's address is formed by
concatenating STB bits 31:12 with VA bits 31:22 (p. 2-4). The segment
bit (bit 3) selects paged or nonpaged format, so one table may mix both
(pp. 2-5, 2-6).

**Paged segment table entry** (Table 2-1 p. 2-5):

| Bits | Field |
|---|---|
| 31:12 | page table base address (physical) |
| 11 | cache: 1 deasserts NCACHE when fetching page-table entries |
| 10:4 | reserved |
| 3 | segment = 0 for paged |
| 2:1 | reserved |
| 0 | valid |

**Nonpaged segment table entry** (Table 2-2 pp. 2-5, 2-6):

| Bits | Field |
|---|---|
| 31:22 | segment base address (physical) |
| 21:12 | segment bound: `0x0` = 4,096 bytes through `0x3FF` = 4 MB, in 4,096-byte increments |
| 11 | cache: 0 asserts NCACHE for this segment (text still cached in the decoded instruction cache); no effect on the stack cache |
| 10:4 | reserved |
| 3 | segment = 1 for nonpaged |
| 2 | user: 1 permits access at user level (all valid segments are kernel-accessible) |
| 1 | writable: 1 permits writes (all valid segments are readable) |
| 0 | valid |

### 5.3 Page table entry

A page-table entry's address concatenates the segment entry's upper 20
bits with VA bits 21:12 (the page number) (p. 2-6). Table 2-3 (p. 2-7):

| Bits | Field |
|---|---|
| 31:12 | page frame base address (physical) |
| 11 | cache: 0 asserts NCACHE for the page; no effect on the stack cache |
| 10:5 | reserved |
| 4 | modified (M): set on a write; subsequent writes do not re-read the memory copy; a software change requires FLUSHPTE |
| 3 | referenced (R): set on first reference; a software change requires FLUSHPTE |
| 2 | user: 1 permits user-level access |
| 1 | writable: 1 permits writes |
| 0 | valid |

The MMU sets R and M automatically; software must clear them when
needed (p. 2-7). NCACHE is asserted during PTE fetch, cleared when R
and M are current, and held asserted while a modified PTE is written
back (p. 2-8).

### 5.4 TLB maintenance and translation faults

Reset and any write to STB flush all TLB and NPSR entries (pp. 2-8,
1-18). FLUSHPTE invalidates the TLB/NPSR entry for its effective
address; it is **not privileged**, so a user process may flush any or
all entries, which can cost performance but not correctness because
the in-memory tables remain authoritative (p. 2-8, p. 3-27).
FLUSHPTE's normal operand is a stack-offset-indirect address moved
into the stack cache (p. 3-27).

Translation faults (p. 2-3): fetch fault (no mapping or kernel-only
page in user mode for text; only on demand fetches), read fault (same
for a data read; can be ignored after a mispredicted branch), write
fault (no page, kernel-only page in user mode, or a write to a
read-only page). Exception IDs are Table 1-26 (p. 1-38) and the
priority list is §6.4. MMU walk penalties are Table 2-4 (p. 2-9); they
are outside this inventory's instruction-encoding scope.

## 6. Event processing

### 6.1 Reset

Reset is entered on the external reset pin or on a memory fault while
reading/writing the interrupt stack or the vector table during event
processing (p. 1-35). The sequence is: disable interrupts; flush PFB
and IC; set SHAD to 0 or to PSW depending on the reset type (the
pseudocode's `if reset` branch is not labelled — see §7); `PSW = 0`;
`CONFIG = 0`; `PC = 0`; enable NMI (p. 1-35).
PSW = 0 selects kernel mode, physical addressing, tracing off,
interrupts inhibited, and ISP as CSP (p. 1-35). CONFIG = 0 disables all
on-chip caches, disables timer interrupts and selects demand
prefetching (p. 1-36). Execution starts at physical address 0
(p. 1-36). After a reset-pin reset, SP and MSP are undefined and the
caches must not be enabled until they are assigned, or the stack-cache
range check is meaningless (p. 1-36).

### 6.2 Interrupt

An interrupt is requested on IL[2:0] or by a Timer1/Timer2 overflow
with interrupts enabled (p. 1-36). Levels: `000` NMI, `001` level 1,
`010` level 2, `011` level 3, `100` level 4, `101` level 5, `110`
level 6, `111` no interrupt (Table 1-25 p. 1-36). A request is serviced
when its level is less than PSW IPL; IPL = 7 accepts levels 0–6, IPL =
0 inhibits 1–6 and accepts only level 0 (NMI) (p. 1-36). Level 0 is
edge-sensitive and must be deasserted for two cycles before another
interrupt is recognized (p. 1-37). IL must be stable for at least two
cycles (p. 1-37).

Interrupt sequence (p. 1-37): disable interrupts; if CSP = ISP then
`ISP = SHAD` else `SP = SHAD`; `*(ISP-8) = PC`;
`*(ISP-4) = PSW`; `ISP -= 16`; `SHAD = ISP`;
`PC = *(VB + 16 + 4*level)`; `PSW &= 0xFFFF0000`; enable NMI. The event
frame is the same as KCALL's, so KRET returns from an interrupt
(p. 1-37). Interruptible instructions are CATCH, ENTER, MUL[3],
DIV[3], REM[3], UDIV, UREM and the CATCH portion of CRET; the saved PC
is the interrupted instruction's address and CATCH/ENTER/CRET's CATCH
portion resume rather than restart (p. 1-37).

### 6.3 Exceptions and unimplemented instructions

Exception identifiers, Table 1-26 p. 1-38:

| Code | Exception |
|---|---|
| `0x1` | integer zero-divide |
| `0x2` | trace |
| `0x3` | illegal instruction |
| `0x4` | alignment fault |
| `0x5` | privilege violation |
| `0x6` | unimplemented register |
| `0x7` | fetch fault |
| `0x8` | data read fault |
| `0x9` | data write fault |
| `0xA` | memory access I/O bus fault |
| `0xB` | MMU table walk bus fault |

Exception sequence (p. 1-38): disable interrupts; `ISP`/`SP` update as
for an interrupt; `*(ISP-12) = exception ID`; `*(ISP-8) = PC`;
`*(ISP-4) = PSW`; `ISP -= 16`; `SHAD = ISP`; `PC = *(VB+4)`;
`PSW &= 0xFFFF0000`; enable NMI. For IDs `0x8`/`0x9`, the faulting
32-bit operand-aligned virtual address is saved in FAULT (p. 1-39).
For a data-write bus error the saved PC is the instruction at the
bottom of the execution pipeline, not necessarily the faulting store
(p. 1-39).

Unimplemented instruction (p. 1-39): the PC of the unimplemented
opcode is saved at `*(CSP)`, then `PC = *(VB+12)`. An unimplemented monadic with a
non-word mode (< `0xC`), an unimplemented instruction after CPU with an
illegal mode or mode combination, and a RETURN with a negative operand
are illegal instructions (ID `0x3`) instead (p. 1-39). Trapped niladic
(p. 1-40): same save, but `PC = *(VB+8)`, selected by a one-parcel
niladic whose 10-bit subcode is `0x200`–`0x3FF` (p. 1-40, T1-17
p. 1-22).

### 6.4 Event processing priority

The documented priority, highest first (p. 1-40):

1. Reset
2. Interrupts
3. Trace
4. Instruction fetch faults
5. Illegal instructions
6. Unimplemented instructions / trapped niladic
7. Unimplemented registers
8. Alignment faults
9. Data read and write and read bus-error faults
10. Privilege violation
11. Divide by zero

Reset and interrupts occur independently of instruction execution; the
others are associated with a particular instruction (p. 1-40). Vector
table offsets: `VB+0` KCALL PC, `VB+4` exception PC, `VB+8` niladic
traps, `VB+12` unimplemented instruction, `VB+16` NMI, `VB+20`–`VB+40`
interrupt levels 1–6, `VB+44` Timer1, `VB+48` Timer2, `VB+52` FP
exception (Table 1-14 p. 1-20).

## 7. Evidence status, counts and ambiguities

### 7.1 Transcribed from printed tables

The following are direct transcriptions of printed tables, not
inferences from prose: Table 1-1 (control-register list, p. 1-8);
Tables 1-2 and 1-3 (CONFIG, FAULT, pp. 1-9 to 1-11); Tables 1-4 to
1-14 (ID, ISP, MSP, PC, PSW, SHAD, SP, STB, TIMER1, TIMER2, VB,
pp. 1-11 to 1-20); Tables 1-15 to 1-20 (one-, three- and five-parcel
encodings and one-parcel subcodes, pp. 1-22 to 1-25); Tables 1-21 to
1-24 (operand modes and register numbers, pp. 1-25 to 1-26); Table 1-25
(interrupt levels, p. 1-36); Table 1-26 (exception IDs, p. 1-38);
Table 2-1 and Table 2-2 (segment entries, pp. 2-5 to 2-6); Table 2-3
(page entry, p. 2-7); Table 2-4 (MMU performance, p. 2-9); Table 3-1
(mnemonic list, pp. 3-1 to 3-2); and every instruction's printed
"Encodings" block in Chapter 3. Table 3-2 (operand abbreviations,
p. 3-4) is used only to expand the abbreviations in the encoding
columns; its OCR is mangled and it is not reproduced here.

The 46-row instruction table is the union of Table 3-1's entries and
the per-instruction encodings. Counts: 46 entries, 60 spellings
(11 `[3]` entries expand to two spellings and `JMP(F/N)(Y/N)` to
four), 44 implemented, 2 unimplemented. Independent corroboration (not
used for any claim above): `tools/check_optab.py` reports the Plan 9
`zl` `genop` byte equal to the printed opcode[5:0] for 35 mnemonics
with 0 mismatches, and 45 of the 46 Table 3-1 entries present in
`zl/optab.c` (CLRE absent). That is a statement about the Plan 9
toolchain, not about the chip.

### 7.2 Derived from prose (not a printed table)

These entries are paraphrases of prose and are marked as such in the
body: stack-cache organization and hit rule (p. 1-5) and maintenance
rules (pp. 1-6, 1-7); ENTER/CATCH flush and refill policies (pp. 1-6,
3-10, 3-11, 3-19, 3-20); the forbidden SP–MSP address ranges (p. 1-8);
the integer-accumulator definition (p. 1-7); the reset, interrupt,
exception, unimplemented-instruction, trapped-niladic sequences
(pp. 1-35 to 1-40); the event priority list (p. 1-40); and the MMU
translation-fault descriptions (p. 2-3). No numeric encoding or bit
field above was inferred from prose alone.

### 7.3 OCR and printed-page ambiguities

1. **Stack-cache lower bound (printed inconsistency).** p. 1-5 displays
   `SP <= ADDR < MSP` (inclusive lower bound), and p. 1-12's prose says
   an address "greater than, or equal to, the SP and less than the
   MSP" hits the cache, but p. 1-12's displayed relation printed
   directly below that prose is the strict `SP < address < MSP`. Two
   statements support an inclusive lower bound and one does not; the
   strict display on p. 1-12 is the outlier.
2. **Width-suffix list is defective (printed).** p. 1-28 prints
   ":UH — signed half-word" and omits ":H", although Table 1-21
   (p. 1-25) defines both `:H` and `:UH`, and p. 1-3 defines six
   signed/unsigned byte/half-word/word types. This inventory uses
   Table 1-21's modes and treats p. 1-28 as an erratum.
3. **Undefined `:L` suffix (printed).** p. 3-3's pipeline example prints
   `MOV R4:B, R8:L`; no `:L` appears in the p. 1-28 suffix list or in
   Table 1-21. Unresolved.
4. **Table 1-19 row header (printed).** The table is headed
   `subcode[9:3]` yet has only two rows, 0 and 1. The three-parcel
   monadic layout (p. 1-23) puts a 4-bit subcode in bits 3:0 and the
   operand mode in bits 7:4, so the row selector is subcode[3] and the
   effective subcode is `row<<3 | column`. The Chapter 3 encodings and
   Plan 9's encoder both use this 4-bit value.
5. **MOVA immediate source (printed conflict).** p. 3-33's footnote
   says the source must be a word mode "except for immediate as
   already noted", while the Notes on the same page say an immediate
   source (as well as a register source or destination) causes an
   illegal instruction exception. The Notes are specific; the footnote
   is ambiguous. A bit-exact implementation must choose, and this
   inventory does not silently resolve it.
6. **ADD operation line.** p. 3-5 prints `ADD: dst += dst`; the
   description ("source operand is added to the destination") implies
   `dst += src`. Printed typo.
7. **XOR classification.** Table 3-1 (p. 3-2) lists XOR[3] with type
   "Shift"; p. 3-51 defines it as bitwise logical exclusive OR. Printed
   classification typo.
8. **USHR format line.** p. 3-50 prints `Format: SHR[3] src, dst` on
   the USHR page; the mnemonics are USHR/USHR3 (Table 3-1 p. 3-2,
   encodings p. 3-50). Printed typo.
9. **Timer2 description.** p. 1-19's Table 1-13 (Timer2) says the bits
   "contain the count value for Timer1". Printed copy-paste typo.
10. **`pdftotext` drops printed encoding tables.** The LDRAA encoding
    table (p. 3-31: `6 0x00 0xA LDRAA flow32`) and the TESTV encoding
    table (p. 3-46: `2 0x0B 0x8 TESTV`) are present on the scanned
    pages but absent from `pdftotext -layout` output. Both were read
    from the page images and cross-checked against Table 1-19 p. 1-24
    and Table 1-17 p. 1-22.
11. **`pdftotext` misreads mnemonics and opcodes.** Table 1-17's
    FLUSHD is OCR'd as "FLUSHC" (page image shows FLUSHD); the VB
    vector offsets `+20`, `+36`, `+48` are dropped on p. 1-20 (page
    image confirms them); `OR3 0x31` and `SHL3 0x3E` appear as
    `OX31.`/`OX3E`; ADDI's page header is "ADDl"; DQM often OCRs as
    "DOM"; and the `*`/`**` prefixes of the Table 1-21/1-23 mode
    strings OCR as bullets. None of these change the encodings
    recorded above. (The `subcode[9:3]` header of Table 1-19 is
    printed, not an OCR error; see item 4.)
12. **Trapped-niladic wording.** p. 1-40 says "one-parcel niladic with
    an opcode in the range 0x200 through 0x3FF". The first parcel's
    bits 14:10 are fixed at `0x0B`; the range refers to the 10-bit
    subcode, matching Table 1-17's `subcode[9:3] = 1xxxxxx` trap row
    (p. 1-22). The wording is ambiguous if read as a parcel opcode.
13. **Interrupt-acceptance wording.** p. 1-15 says interrupts are
    accepted when the request level "is less than interrupt priority
    level or equal to 0"; p. 1-36 states the rule as "less than the IPL
    field" and explains IPL 0/7. The p. 1-15 phrasing is ambiguous; the
    p. 1-36 rule is used above.
14. **Malformed or inconsistent pseudocode.** CATCH's operation
    pseudocode (p. 3-10) uses `CSP + src` as the fill bound for every
    addressing mode even though the description on the same page
    defines the target MSP differently for stack-offset, immediate,
    stack-offset-indirect and absolute sources. ENTER's pseudocode
    (p. 3-19) is also indented/garbled in the printed page. Their prose
    descriptions (pp. 3-10, 3-20) and the per-instruction Notes are the
    authoritative statements used here.
15. **`%`-register syntax versus `CPU`.** The manual prints
    `MOV $new, %SHAD` (p. 3-3) and `MOV %SP, %SHAD` (p. 1-15) but no
    example containing the literal `CPU` prefix, and it does not state
    whether a `%name` operand implies the escape. Table 1-22 (p. 1-26)
    and the CPU description (p. 3-14) give the mechanism but not the
    assembled spelling.
16. **DQM's wrong-mode fault (printed conflict).** p. 3-18's
    description says addressing modes outside the permitted word
    source/special destination set "result in an alignment fault",
    while the Notes on the same page say those modes "cause an illegal
    instruction sequence to occur". The two statements assign different
    exception IDs (`0x4` vs `0x3`) to the same misuse.
17. **Reset SHAD branch (printed ambiguity).** p. 1-35's sequence
    tests `if reset` to choose `SHAD = 0` versus `SHAD = PSW` but never
    labels which reset type (`HRESET` pin versus memory-fault reset)
    selects which branch. The accompanying prose only says SHAD is set
    to one or the other "depending on the reset type".
