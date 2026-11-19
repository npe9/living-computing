# Adjudication — golden traces versus `hobbit/sem`

> Naming note: this document was written while the retirement record was
> called "RVFI" as a shorthand for the riscv-formal pattern. It is now the
> **HRI — Hobbit Retirement Interface** — because RVFI means *RISC-V*
> Formal Interface. The field set and every verdict are unchanged; quoted
> `RVFI ...` lines below are the same records with the old prefix.

Read-only adjudication of `hobbit/tests/golden/001.trace` … `006.trace`
against `hobbit/sem/hobbit_sem.py`, using the printed *ATT92010 Hobbit
Microprocessor Programmer's Reference Manual* (January 1993, PRM) as the
only authority. No file under `hobbit/sem/`, `hobbit/tests/` or
`hobbit/bsv/` was modified.

Page cites are the manual's printed folios. The PDF page is the printed
page + 8 in Chapter 1 and + 58 in Chapter 3. `T3-2` means the manual's
Table 3-2. Quotations are from the PDF text layer except p. 1-23 and
p. 3-40, whose OCR is unreliable and which were checked against the page
images; those two are marked "[page image]".

## How the diff was produced

The spec was run once per image, from `hobbit/`:

```sh
for n in 001 002 003 004 005 006; do
  python3 sem/hobbit_sem.py --image tests/golden/$n.hex --sp 0x100 --msp 0x180
done
```

Both sides were then parsed with the fixed-line regex (11 fields: `pc`,
`insn`, `sp0`, `sp1`, `msp0`, `msp1`, `we`, `addr`, `data`, `mask`,
`trap`) and compared field by field after pairing records by retirement
ordinal. A record with no counterpart is a divergence too. In `005` the
ordinal alignment becomes meaningless after the wrong branch decision, so
the tail was re-aligned by PC (the goldens' records at `0x0014` and
`0x0016` are the manual-correct terminal NOPs).

| program | image bytes | golden records | spec records | divergent records |
|---|---:|---:|---:|---:|
| 001 | 16 | 8 | 9 | 5 |
| 002 | 28 | 8 | 9 | 1 |
| 003 | 16 | 6 | 81 | 77 |
| 004 | 20 | 6 | 7 | 4 |
| 005 | 24 | 11 | 2 | 10 |
| 006 | 8 | 4 | 4 | 1 |
| **total** | | **43** | **112** | **98** |

Two counts are used below:

* a **divergent record** is one line on which the two outputs differ in
  at least one field, or that one side emits and the other does not —
  **98** in total;
* an **adjudicated divergence** is one disputed point, listed as one row
  of the tables; a single wrong reading that corrupts a run of records
  (above all `003`'s 76-record loop) is one point — **17** in total.

Every divergent record is covered by exactly one row, and the covered
record range is stated in the row. Only divergences are adjudicated:
common lines were checked against the same pages while reading, and none
needed a verdict.

## 001 — the 5-bit stack offset is scaled by four

`MOV $20, R0`; `MOV $8, R4`; `MOV R4, R8`; `ADD R0, R8`;
`ADD3 $5, R0`; `ADD3 R8, R0`; two NOPs.

The one-parcel encodings are `MOV wai5, stk5` (opcode `0x0A`, p. 3-32;
T1-15 p. 1-22) and `MOV stk5, stk5` (opcode `0x18`). The source field
`wai5` is "an unsigned constant … which is multiplied by 4
(word-aligned)" (T3-2 p. 3-4), and the destination field `stk5` is a
stack offset:

> "5-bit immediate fields are sign extended and 5-bit stack offset
> fields are zero extended." — p. 1-21

> "Five-bit offset values are multiplied by four before they are added
> to the stack pointer (SP)." — p. 1-22

> "stk5 … A Stack Offset mode with the offset number in the range 0
> through 124 and is divisible by four, (the operand size of word)."
> — T3-2 p. 3-4

> "Stack Offset — addressing develops the address of an operand by
> adding a constant offset in the instruction to the address of the
> current stack pointer (CSP)." — p. 1-27

So field value 4 means byte offset 16: `CSP+16 = 0x00000110`, not
`0x00000104`. The golden's own derivation says "`stk5`=4 (offset 16)"
and then writes the sum as `*(0x00000100+16) = *(0x00000104)` — an
arithmetic slip in the `.md`, not a different reading of the manual. The
rest of the golden's values are the cascade of that one wrong address.

| ID | golden / spec | pc | field | golden | spec | verdict | page and deciding text |
|---|---|---|---|---|---|---|---|
| I1 | G02 / S02 | 0002 | `addr` | 00000104 | 00000110 | **SPEC** | p. 1-22: "Five-bit offset values are multiplied by four before they are added to the stack pointer (SP)." |
| I2 | G03 / S03 | 0004 | `data` | 00000008 | 00000000 | **SPEC** | p. 3-32: "The value of the source operand is stored in the destination." `R4` is offset 4; `0x104` was never written, so the pre-state's zero memory is read. |
| I3 | G04 / S04 | 0006 | `data` | 0000001c | 00000014 | **SPEC** | p. 3-5: "The source operand is added to the destination operand and the sum is placed in either the destination (ADD)…" |
| I4 | G06 / S06 | 000a | `data` | 00000030 | 00000028 | **SPEC** | p. 3-5 (ADD3 `Acc = dst + src`), accumulator at `CSP+4` (p. 1-7, Figure 1-4; p. 1-28). |
| I5 | — / S09 | 0010 | record | absent | fetch-fault trap at `0x10` | **CONVENTION** | Convention C1; no manual sentence. Context only: a fetch fault is exception ID `0x7` with the p. 1-38 frame. |

I1 is the root. I2–I4 are consequences: with I1 corrected, `0x104` holds
0 until the first `ADD3`, so `MOV R4,R8` stores 0 at `0x108`, the `ADD`
gives `0x14`, and the second `ADD3` gives `0x14 + 0x14 = 0x28`. (The
`0` of I2 depends on the fixed pre-state's zero-filled memory and
`CONFIG = 0`, i.e. stack cache disabled, p. 1-36; that is a harness
convention shared by both sides, not a manual value. The accumulator
address `0x104` itself is manual: p. 1-7, "The integer accumulator is not
an actual hardware register. It is the word in memory above the word
addressed by the current stack pointer (CSP)", Figure 1-4 marks it
`CSP+4`.)

Corrected records (only the divergent fields change):

```text
I1  RVFI pc=0002 insn=28440000 sp=00000100>00000100 msp=00000180>00000180 we=1 addr=00000110 data=00000008 mask=0f trap=0
I2  RVFI pc=0004 insn=60220000 sp=00000100>00000100 msp=00000180>00000180 we=1 addr=00000108 data=00000000 mask=0f trap=0
I3  RVFI pc=0006 insn=58020000 sp=00000100>00000100 msp=00000180>00000180 we=1 addr=00000108 data=00000014 mask=0f trap=0
I4  RVFI pc=000a insn=5c400000 sp=00000100>00000100 msp=00000180>00000180 we=1 addr=00000104 data=00000028 mask=0f trap=0
I5  (no record; stop after G08, PC = 0x10 = image length)
```

S01, S05, S07 and S08 already equal the golden.

## 002 — image end is a harness boundary

`MOV`, three-parcel `ADD $100,R0`, three-parcel `SUB $112,R0`,
`MOV $20,R8`, three-parcel `SUB R0,R8`, three NOPs. Every field of the
eight common records agrees, including the `SUB` result
`0x0000006e - 0x00000070 = 0xfffffffe` (p. 3-43) and
`0x14 - (-2) = 0x16`.

| ID | golden / spec | pc | field | golden | spec | verdict | page and deciding text |
|---|---|---|---|---|---|---|---|
| I6 | — / S09 | 001c | record | absent | fetch-fault trap at `0x1c`, `we=1 addr=00000100 data=0000001c` | **CONVENTION** | Convention C1; no manual sentence. Context only: p. 1-40 lists instruction fetch faults as event 4, and p. 1-38 gives them exception ID `0x7` and a three-word frame. |

The last NOP is at `0x1a`, one parcel, so its end is `0x1c`, the image
length. Golden stop rule 2 ends the run there. The spec fetches `0x1c`
and applies its generic trap protocol. The extra line is not comparable
and, more strongly, its single `*(CSP)=PC` write is not the p. 1-38
fetch-fault sequence; the spec's generic save is the p. 1-39
unimplemented-instruction write applied to the wrong event. C1 removes
the line rather than scoring its fields.

Corrected record: none. Stop after G08.

## 003 — 3-parcel monadic operands are 32-bit; RETURN reads PC then moves CSP

`JMP 0xC`; `CALL 0x2` (saves return PC `0xE` at CSP); `ENTER R-16`;
`NOP`; `RETURN R16`; `NOP`.

The PRM's monadic three-parcel format is a 32-bit operand split across
parcels 2 and 3:

> "The notation *operand-lo* represents the low-order 16-bits and
> *operand-hi* represents the high-order 16-bits." — p. 1-23

The Monadic (One Operand) figure on the same page prints
`2nd PARCEL / OPERAND-HI` and `3rd PARCEL / OPERAND-LO` [page image],
and T3-2 p. 3-4 defines `stk32` as "A Stack Offset mode with the offset
any 32-bit number". `RETURN` is the monadic subcode `0x2` (T1-19 p. 1-24;
p. 3-40 encoding table), and its operand in `003` is therefore
`(0x0000 << 16) | 0x0010 = 0x00000010`, not `0x0000`.

The divergence is the operand, not the order. The PRM's Operation block
prints `PC = PC * (CSP + src)` — a print defect [page image] — but the
Description and Notes state the intended order unambiguously:

> "The src operand is fetched and used as the new PC value." — p. 3-40

> "RETURN can obtain a new PC for a word-aligned register offset that is
> not a multiple of 16; but when adjusting the SP, the lower 4 bits of
> the offset are ignored. … RETURN R20 obtains the new PC from R20, but
> the SP only increments 16." — p. 3-40

So `PC = *(CSP + 16) = *(0x100) = 0x0000000e`, then
`CSP = CSP + 16 = 0x00000100`; the new SP `0x100` does not exceed MSP
`0x180`. Golden does exactly this. The spec uses operand 0: it reads
`*(0xf0) = 0`, leaves SP at `0xf0`, and re-enters the JMP/CALL/ENTER loop.

| ID | golden / spec | pc | field | golden | spec | verdict | page and deciding text |
|---|---|---|---|---|---|---|---|
| I7 | G05 / S05 | 0006 | `sp` after; next PC | `0x100`; next PC `0x000e` | `0xf0`; next PC `0x0000` | **GOLDEN** | p. 1-23 operand-HI/LO; p. 3-40 "The src operand is fetched and used as the new PC value" and "SHAD = CSP = CSP + src". |
| I8 | G06 / S06–S81 | 000e vs 0000… | `pc`, `insn`, `sp` before/after | `000e`, `2c020000`, `0x100` | `0000`, `0c060000`, `0xf0`; then 75 more records | **GOLDEN** | Same two pages: with the 32-bit operand the RETURN lands on the NOP at `0x000e`, which "No operation is performed" (p. 3-35), and the image ends at `0x10`. |

I8 covers 76 records: S06 re-executes the JMP at `0x0000`; S07–S80 are
the repeating JMP/CALL/ENTER/NOP/RETURN loop as SP walks down by `0x10`
per iteration and, once the 256-byte window is exceeded, MSP is flushed
down (p. 3-19); S81 is a wild-PC
fetch-fault (`pc=c060bfc`) after `RETURN` reads the image's first word at
`0x00000000`. All of it is the single operand error of I7.

Corrected records:

```text
I7  RVFI pc=0006 insn=80d20000 sp=000000f0>00000100 msp=00000180>00000180 we=0 addr=00000000 data=00000000 mask=00 trap=0
I8  RVFI pc=000e insn=2c020000 sp=00000100>00000100 msp=00000180>00000180 we=0 addr=00000000 data=00000000 mask=00 trap=0
    (then stop: PC = 0x10 = image length)
```

G01–G04 already equal S01–S04.

## 004 — the same 32-bit monadic operand, now for ENTER and POPN

`MOV $16,R0`; one-parcel `ENTER R-32`; one-parcel `POPN R32`;
three-parcel `ENTER $0xC0`; three-parcel `POPN $16`; `NOP`.

The first three records agree (MOV, ENTER R-32, POPN R32): ENTER R-32
moves SP `0x100 → 0xe0` without a flush (`0x180 - 0xe0 = 0xa0 ≤ SCSIZE`),
and POPN R32 moves it
`0xe0 → 0x100`, below MSP `0x180` (p. 3-19, p. 3-38). The two
three-parcel operands are `0x000000c0` and `0x00000010`; the spec reads
only the high parcel (`0x0000`) of each, so its targets are 0.

For the ENTER:

> "SHAD = MSP = SP = target" — p. 3-19 pseudocode, non-stack-offset
> branch

> "If the source operand is defined with an immediate mode ($data), the
> immediate value is used as the target value (MSP = data) and the stack
> cache is set empty at the completion of ENTER." — p. 3-20

An empty cache means MSP = SP (p. 1-5: MSP is "the address above the
highest address of the data that is currently kept in the stack cache
registers"). With the correct operand 0xC0, both SP and MSP become
`0x000000c0`.

For the POPN:

> "SHAD = CSP = CSP + src" and "if ((CSP = SP) && (CSP > MSP)) MSP = SP"
> — p. 3-38

> "If the CSP is SP, and the new SP value exceeds the MSP, the MSP is
> also updated to the new value." — p. 3-38 Description

With SP = MSP = `0xc0` and src = 16, SP becomes `0xd0` and, because the
new SP exceeds MSP, MSP becomes `0xd0` too.

| ID | golden / spec | pc | field | golden | spec | verdict | page and deciding text |
|---|---|---|---|---|---|---|---|
| I9 | G04 / S04 | 0006 | `sp` after, `msp` after | 000000c0, 000000c0 | 00000000, 00000000 | **GOLDEN** | p. 1-23 operand-HI/LO; p. 3-19 "SHAD = MSP = SP = target"; p. 3-20 "the immediate value is used as the target value (MSP = data)". |
| I10 | G05 / S05 | 000c | `sp` before/after, `msp` before/after | c0→d0, c0→d0 | 0→0, 0→0 | **GOLDEN** | p. 3-38 "SHAD = CSP = CSP + src" and "the new SP value exceeds the MSP, the MSP is also updated". |
| I11 | G06 / S06 | 0012 | `sp` before/after, `msp` before/after | d0→d0, d0→d0 | 0→0, 0→0 | **GOLDEN** | Same p. 3-38 state; the NOP itself is p. 3-35, "No operation is performed." |
| I12 | — / S07 | 0014 | record | absent | fetch-fault trap at `0x14` | **CONVENTION** | Convention C1; no manual sentence. Context only: p. 1-38 exception ID `0x7` and its three-word frame. |

I10 and I11 are the cascade of I9. (S07's `addr=0` is also a cascade: the
spec's CSP is 0 because of I9; even after fixing I9 the record would
remain a C1 case.)

Corrected records:

```text
I9   RVFI pc=0006 insn=80f90000 sp=00000100>000000c0 msp=00000180>000000c0 we=0 addr=00000000 data=00000000 mask=00 trap=0
I10  RVFI pc=000c insn=80df0000 sp=000000c0>000000d0 msp=000000c0>000000d0 we=0 addr=00000000 data=00000000 mask=00 trap=0
I11  RVFI pc=0012 insn=2c020000 sp=000000d0>000000d0 msp=000000d0>000000d0 we=0 addr=00000000 data=00000000 mask=00 trap=0
I12  (no record; stop after G06, PC = 0x14 = image length)
```

G01–G03 already equal S01–S03. PSW.E is not a field of the fixed line, so
the ENTER guard bit is outside this comparison (p. 3-19 sets it; T1-8
p. 1-15 conditions it on "an ENTER instruction that does not result in
any stack cache flush").

## 005 — the spec refuses CMPEQ, and the golden reverses JMPTN

`MOV $10,R0`; `CMPEQ $10,R0`; `JMPTN 0x14`; `ADD $1,R0`; `JMPTY 0xC`;
`ADD $1,R0`; `ADD3 $5,R0`; `NOP`; `ADD $2,R0`; `NOP`; `NOP`; `NOP`.

Two separate errors make this the only program where both sides lose.

**CMPEQ is a legal instruction, not a trap.** p. 3-13 encodes it as
`2 0x10 CMPEQ imm5, stk5` and says:

> "The program status word (PSW) flag bit is set to 1 if the comparison
> between the two source operands is true." — p. 3-13

> "src1 is specified in the source operand field. src2 is specified in
> the destination operand field." — p. 3-13 Notes

`10 == *(CSP+0) = 10`, so `PSW.F := 1`; there is no memory write and no
trap. The spec's `trap=1`, `we=1`, `data=2` line is its generic refusal
protocol, not an architectural result.

**JMPTN with F=1 is taken.** The `N` is a prediction, not a condition:

> "JMPT: if (PSW.F) PC = &dst" — p. 3-28 Operation

> "The jump instructions cause the address of the destination operand to
> become the new PC value … if the PSW flag bit is 1 (JMPT)…" — p. 3-28

> "The Y or N at the end of the conditional jump instruction is the
> prediction of the branch (Y=jump, N=continue)." — p. 1-33

The `pcrel10` field is 8, and "The 10-bit PC-relative offsets in the JMP
and CALL instructions are multiplied by 2" (p. 1-22), so the target is
`0x0004 + 2*8 = 0x0014`. The golden's own `005.md` quotes p. 3-28 and
then says "F is 1 … this branch is **not taken**", which contradicts the
sentence it quotes. The golden's fall-through path is therefore not a
legal execution; its records at `0x0006`–`0x0012` cannot retire. (ADD
sets C and V, not F, p. 3-5, so the later JMPTY would be taken if it were
reached; it is not.)

| ID | golden / spec | pc | field | golden | spec | verdict | page and deciding text |
|---|---|---|---|---|---|---|---|
| I13 | G02 / S02 | 0002 | `we`, `addr`, `data`, `mask`, `trap` | 0, 0, 0, 00, 0 | 1, 00000100, 00000002, 0f, 1 | **GOLDEN** | p. 3-13: "The program status word (PSW) flag bit is set to 1 if the comparison between the two source operands is true." |
| I14 | G03 / — | 0004 | successor PC (not printed) | `0x0006` | no record | **BOTH WRONG** | p. 3-28 "JMPT: if (PSW.F) PC = &dst"; p. 1-33 the N is only a prediction; p. 1-22 the target is `0x0014`. |
| I15 | G04–G09 / — | 0006, 0008, 000c, 000e, 0010, 0012 | six records | six retiring records | no records | **BOTH WRONG** | Same p. 3-28 / p. 1-33 rule: once JMPTN is taken, none of these instructions is on the execution path. |
| I16 | G10–G11 / — | 0014, 0016 | two records | NOP, NOP; `we=0` | no records | **GOLDEN** | p. 3-28 taken target `0x0014`; p. 3-35 "No operation is performed." |

I14's printed fields (no write, SP/MSP unchanged) happen to equal the
manual-correct JMPTN record; the verdict concerns its successor, which
the fixed line does not print. I15 covers the six instructions the golden
executes only because of I14: `ADD` at `0x6`, `JMPTY` at `0x8`, `ADD3` at
`0xc`, NOPs at `0xe`/`0x12`, and `ADD` at `0x10`. I16 is the two-record
terminal NOP sequence the manual does reach; the spec never gets there
because it stopped at I13.

Corrected trace:

```text
RVFI pc=0000 insn=71400000 sp=00000100>00000100 msp=00000180>00000180 we=1 addr=00000100 data=0000000a mask=0f trap=0
RVFI pc=0002 insn=41400000 sp=00000100>00000100 msp=00000180>00000180 we=0 addr=00000000 data=00000000 mask=00 trap=0
RVFI pc=0004 insn=18080000 sp=00000100>00000100 msp=00000180>00000180 we=0 addr=00000000 data=00000000 mask=00 trap=0
RVFI pc=0014 insn=2c020000 sp=00000100>00000100 msp=00000180>00000180 we=0 addr=00000000 data=00000000 mask=00 trap=0
RVFI pc=0016 insn=2c020000 sp=00000100>00000100 msp=00000180>00000180 we=0 addr=00000000 data=00000000 mask=00 trap=0
```

Stop after the last line: PC = `0x18` = image length.

## 006 — the unimplemented-instruction sequence saves the opcode's own PC

`NOP`; `MOV $6,R0`; `NOP`; `FLUSHD` (`0x2c06`, niladic `0x0B`/`0x006`).

> "Since there is no data cache, FLUSHD is not implemented in hardware.
> An unimplemented instruction sequence is taken." — p. 3-22

> "The sequence is: `*(CSP) = PC of unimplemented opcode`;
> `PC = *(VB+12)`" — p. 1-39

The opcode's PC is the address of its own parcel, `0x0006`:

> "The program counter (PC) addresses the instruction currently being
> executed. Instructions are aligned on parcel (half-word) boundaries.
> Since parcels are composed of 2 bytes, the PC is always a multiple of
> two and the low-order bit is always 0." — p. 1-13

`0x0006` is the parcel carrying `0x2c06`; `0x0004` is the preceding NOP's
parcel and is not the PC of the unimplemented opcode. The golden's own
record prints `pc=0006`, and its `.md` calls `0x0006` "the following
parcel" — but it is the instruction's own address, not a following one.
The spec's `6` is the manual value; the golden's `4` is wrong.

| ID | golden / spec | pc | field | golden | spec | verdict | page and deciding text |
|---|---|---|---|---|---|---|---|
| I17 | G04 / S04 | 0006 | `data` | 00000004 | 00000006 | **SPEC** | p. 1-39 "`*(CSP) = PC of unimplemented opcode`" with p. 1-13 "The program counter (PC) addresses the instruction currently being executed." |

Corrected record:

```text
I17  RVFI pc=0006 insn=2c060000 sp=00000100>00000100 msp=00000180>00000180 we=1 addr=00000100 data=00000006 mask=0f trap=1
```

G01–G03 already equal S01–S03. The single write, its address (`CSP =
0x100`) and `mask=0f` are correct in both: p. 1-39's sequence performs
one store, and `trap=1` marks it.

## Conventions both sides must adopt

These are comparison conventions, not manual facts. They remove the
uncomparable records without changing any instruction's semantics.

**C1 — stop rule.** A run retires exactly the instructions whose last
parcel lies inside the loaded image and then stops; equivalently, stop
when the next PC equals the image length, and emit no record for the
fetch that would follow. The PRM has no "end of program" instruction;
an instruction fetch fault is a different event (exception ID `0x7`,
p. 1-38, and item 4 of p. 1-40), not a program terminator. Adopting C1
removes S09 of `001`, S09 of `002` and S07 of `004` from the comparison
and leaves the other 95 divergent records.

**C2 — trap line and trap write.** A `trap=1` record is emitted only for
an instruction that takes the unimplemented-instruction sequence, and its
one architectural write is `*(CSP) = PC of unimplemented opcode` (p.
1-39), reported as `we=1`, `addr=CSP`, `mask=0f`. For `006` the value is
`0x0006`. That write must not be reused for a fetch fault (p. 1-38's
three-word frame at `ISP-12/-8/-4` is a different sequence and does not
fit the one-write line) or for a model limitation. A legal instruction
the model does not implement (CMPEQ in `005`) is not a trap at all:
report it as a refusal outside the comparison, not as `trap=1`.

**C3 — one-write record encoding.** `we=0`, `addr=0`, `data=0`,
`mask=00` when the instruction performs no architectural store; `we=1`
with a `0f` word mask and the stored word when it performs exactly one;
`sp`/`msp` are the instruction's before/after values; `insn` is the first
two parcels (`0000` as the second for a one-parcel instruction); `pc` is
the first parcel's address. This is the fixed line, not a manual fact.

**C4 — alignment after a refusal.** When one side stops or refuses and
the other continues, align the remaining records by PC, not by ordinal,
and do not count a missing record as a field mismatch. This is how the
`005` table is built; ordinal alignment is used only while both sides are
still retiring the same instruction sequence.

A manual rule that is *not* a convention and that both sides must
implement: a three-parcel monadic operand (opcode `0x00`) is 32 bits,
`(parcel2 << 16) | parcel3` (p. 1-23; T3-2 p. 3-4), and its width is 32
even though the instruction is only three parcels long. The spec's
three-parcel dyadic handling (16-bit source in parcel 2, 16-bit
destination in parcel 3) is correct; only the monadic reconstruction is
wrong, which is what I7–I11 record.

## Verdict summary

**Verdict: 17 adjudicated divergences — SPEC 5, GOLDEN 7, BOTH WRONG 2,
CONVENTION 3 — covering 98 divergent records, at record level SPEC 5,
GOLDEN 83, BOTH WRONG 7, CONVENTION 3 (001 5, 002 1, 003 77, 004 4,
005 10, 006 1).**
