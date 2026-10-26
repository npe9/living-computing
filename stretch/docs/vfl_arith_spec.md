# VFL integer MULTIPLY and DIVIDE — the manual's own words

Everything below is quoted from Reference Manual `22-6530-2`,
**printed pp.68-70** (PDF 71-73), the "Variable Field Length"
chapter. It is written down here because the model does not
implement either operation and both are on MCP's path:

* **`/`** — MCP printed p.24 lines 21 and 24, the time conversion.
  Refused by the model, confirmed by the OP locator at 001213.00.
* **`*`** — MCP printed p.72 line 19, `*(BU,24),T COMBO,40
  -COMPUTE LOC WITHIN TABLE`. Refused, and the current best
  suspect for the `EXHAUSTED ALL CHANNELS` halt, because a
  suppressed multiply leaves a table offset at whatever the
  accumulator held.

> Quoted from the OCR in `docs/ocr/`, **spot-checked against the
> rendered page at 200 dpi** before being written here. The OCR is a
> finding aid (see `docs/ocr/README.md`); these sentences were read.

---

## Multiply (`*`) — printed p.68

> "If binary is specified, the product of the addressed operand and
> the accumulator field specified by the offset is placed into the
> **cleared accumulator at offset 20**. Neither operand may exceed
> **48 significant numeric bits**. If decimal is specified, this
> operation has the same action as LOAD TRANSIT AND SET, except that
> the two high-order bits of the left zeros counter are set to
> zeros."

**Indicators.** *Partial Field (PF)*: "turned on in a binary
operation if either operand exceeds 48 significant bits in length.
In such a case, only the 48 low-order bits of the oversized operand
are used in the operation. If the accumulator operand was oversized,
the higher-order bits are lost." *Decimal Transit (DTR)*: on if
decimal. *Data Flags (TF, UF, VF)* and *MOP*: as in ADD.
*Arithmetic Result (RLZ, RZ, RGZ, RN)*: in a binary operation, as in
ADD.

**Note the asymmetry that makes this easy to get wrong:** the result
lands at **offset 20**, a fixed position, *not* at the instruction's
offset. The instruction's offset selects the accumulator *operand*.

---

## Divide (`/`) — printed p.70

> "If a binary operation is specified, the entire accumulator
> contents **to the left of the offset** are divided by the addressed
> storage field. Accumulator positions to the right of the offset are
> ignored. At the completion of the operation, the quotient is placed
> in the **cleared accumulator at the specified offset**, and the
> remainder with sign is placed in the **remainder register (RM)**.
> Both dividend and divisor are treated as integers, and only the
> integral part of the quotient is developed. The length of the
> dividend to the left of the offset cannot exceed **96 significant
> bits**, and the divisor cannot exceed **48 significant numeric
> bits**. The sign of the quotient replaces the sign bit in the
> accumulator sign byte register. **Bits 60-63 of RM form a four-bit
> remainder sign byte with bit 60, the sign bit, set to the original
> accumulator sign. Bits 61-63 are set to zero. Bits 0-59 of RM are
> replaced by the integer remainder with the low-order remainder bit
> in bit position 59 of the remainder register.**"

**Indicators.** *PF*: on if more than 96 significant bits in the
accumulator to the left of the offset, or the divisor exceeds 48;
only the low-order 96 or 48 are used and higher-order dividend bits
"are lost in the operation". **`ZD` (Zero Divisor): "turned on if the
binary divisor is zero. The division is not attempted, and both the
accumulator and the remainder register remain unchanged."** *DTR*:
on if decimal. *Data flags*, *MOP*: as in ADD. *Arithmetic result*:
as in ADD — and the programming notes add that these "describe the
quotient, and not the remainder."

**Programming notes worth keeping:** "The rightmost digit of the
quotient is always found at the offset specified in the instruction.
The bits to the right of the offset are zero."


### And `R23-9694` printed pp.120-121 carries three divide rules the Reference Manual does not

Verified on the rendered page, not only in the OCR.

**1. A divisor that is not zero can still be a zero divisor.** Under
Zero Divisor:

> "This indicator is turned on if the binary divisor is zero. The
> division is not attempted, and both the accumulator and the
> remainder register remain unchanged. **If the divisor contains over
> 48 bits, but the low-order 48 bits are zero, both the PF and ZD
> indicators are turned on.**"

So the zero test is applied to the **truncated** divisor. A divisor of
exactly 2⁴⁸ has forty-nine significant bits and low-order forty-eight
zeros: PF *and* ZD, and nothing is written. Printed p.70 alone would
never produce that behaviour, and a model that tested the field as
written would pass every obvious test and be wrong exactly there.

**2. The quotient length is predictable, and the divisor is
normalized first.**

> "(Dividend length + 1) - Divisor length = Maximum quotient length
> ... To assure that the high-order bit of the divisor is a one, the
> divisor is **normalized as though it were a floating point
> fraction**. The normalization is performed in PAU prior to the
> actual division."

The normalization is a mechanism note, not a semantic one -- an
integer quotient does not depend on it -- but it is the direct
evidence for why a VFL integer divide inherits floating point's
operand limits, which the next sentence states outright:

> "**As in MULTIPLY, this operation is actually performed by PAU.**
> For this reason the operands are restricted to the fraction length
> acceptable in floating point operations."

96 and 48 are the double- and single-precision fraction lengths. The
same two numbers, from the same unit, as `*`.

**3. The quotient's position is restated so it cannot be confused
with multiply's.**

> "The rightmost bit of the quotient is always found at the offset
> specified in the instruction. The bits to the right of the offset
> are zero."

**And the opcode confirms again.** "Operation Code: 01110" with the
VFL integer codes' trailing 1 is `011101` = 29. "STRAP Notation:
`/(B, 52, 4), NAME .12, 20`".

---

## The free check that already exists in the corpus

MCP printed p.24 lines 21-22 are

```
/I(BU,6), 60, -60
C0011(BU,6), $RM+.54      -SECONDS IN RM IN BINARY
```

The manual says RM's integer remainder has **its low-order bit in
position 59**. MCP reads **six bits at offset 54 — positions 54-59**,
which is exactly the low-order six bits, and sixty seconds needs
exactly six bits.

> A page transcribed from a 1963 listing and a manual page never read
> beside it until 2026-10-25 **agree to the bit**. When `/` is built,
> printed p.24 stops being five lines the model declines and becomes
> a test of the implementation — the quotient feeds the next divide
> and the remainder feeds the console, so both must be right or the
> printed time is wrong.

## >>> AND IBM'S OWN WORKED EXAMPLES EXIST: `C22-6578`, Apr 61 <<<

The oracle problem is solved. `C22-6578` *Programming Examples* uses
both operations in complete programs, with the constants specified,
and **states the offset-20 rule independently of the Reference
Manual**.

### Problem 2.10, matrix element address — multiply

```
LOCATE  V-I, $1, 1.0          'p-1 generated
        L(BU, 18), 17.0       'S1
        *(BU, 18), ENN        'result has 20 offset
        ST(BU, 25), $3, 20-7  '(p-1)*N
        V+, $3, 18.0          '(p-1)*N+q
        V+, $3, VF
        L(BU, 64), 0($3)
        BEW, $
ENN     DD(BU, 18), N
VF      VF, MTRIX-1.0
```

> "(b) After a binary VFL multiply the answer is placed in the
> **cleared accumulator with offset 20**."

**Two independent sources now agree on the rule that is easiest to
get wrong.** The Reference Manual states it normatively; this states
it as a working programmer's note, in a different document, five
years apart in revision.

### Problem 2.12, matrix transposition — multiply AND divide

```
        LI(BU, 18), M
        *I(BU, 18), N
        -I(BU,18), 1, 20            'M*N-1
        ST(BU, 25), 20.0, 20-7
...
CYCLE   L(U), 18.0                  'location of old element
        *I(BU, 18), N, 128-18       'answer is at 20 offset
        /(BU, 18), 20.0, 20         'divide by M*N-1
        L(BU, 18), $RM+.60-.18,128-18   'location of new element
...
M       SYN, 20      'no. of rows
N       SYN, 5       'no. of columns
```

**This is a runnable oracle**: M and N are given, so every
intermediate is computable by hand, and it exercises the multiply,
the immediate form, the divide and the remainder read in one
sequence.

### And a third confirmation of how RM is read

`L(BU,18),$RM+.60-.18` reads **bits 42-59** — the low-order
eighteen bits of the remainder, whose low-order bit the manual puts
at position 59. MCP printed p.24 line 22 reads `$RM+.54` for six
bits — **bits 54-59**, the low-order six.

> The Reference Manual, IBM's programming examples, and MCP's own
> source all read the remainder the same way, from the bottom. Three
> documents, three decades of provenance apart in how this project
> acquired them, agreeing on a bit position.

---

## >>> AND THE CE MANUAL SAYS *WHY* OFFSET 20 <<<

`R23-9694` *Customer Engineering Intermediate Level Diagrams,
Introduction to Programming, Vol. 2*, 1961, **§6.21.24 Multiply,
printed p.117** (PDF 118; this manual's offset is +1) repeats the Reference Manual's two sentences verbatim and then adds
two the Reference Manual does not have:

> "The actual multiplication in this operation is performed by **PAU**.
> This restricts the operands to 48 significant bits each. Similarly,
> **the result appears at offset 20 as this is the normal result field
> (12-107) for a double-precision PAU operation**."

**The constant is not arbitrary and it is not a VFL decision at all.**
The 7030's floating-point unit produces a double-precision 96-bit
fraction in accumulator bits 12-107. A VFL multiply is dispatched to
that same unit, so its product lands where that unit always puts a
96-bit answer. Counting an offset from the accumulator's low-order
end, bit 107 is offset `127 - 107 = 20` and bit 12 is offset 115:

```
IBM bit:     12 ........................................ 107
offset:     115 ........................................  20
             ^ product MSB                   product LSB ^
```

Both numbers in the manual's "48 significant bits" and "offset 20"
are therefore the SAME fact stated twice: 48 x 48 = 96, and 96 bits
at offset 20 reach to offset 115, which is bit 12. The Reference
Manual's two constants are one hardware constraint. (They are also
stated outright on printed p.74 -- see the correction at the end of
this file.)

**This also decides the sign, which p.68 leaves unstated.** If the
VFL multiply is the PAU's multiply, the PAU's own sign rule applies,
and `R23-9694` **§6.20.13 Multiply, printed p.75** (PDF 76) -- the
FLOATING-POINT multiply, the other operation the PAU performs --
states it outright:

> "**The sign of the product replaces the accumulator sign in bit
> position 4 of the sign byte register.** ... The product sign is
> determined by **the rules of algebra**, using the accumulator sign
> and the effective sign of the addressed operand. The sign of the
> addressed operand is modified according to the specifications of the
> sign modifiers."

So the product's sign is `accumulator sign XOR effective storage
sign`, and it is WRITTEN, not left alone — which is the opposite of
`+MG` and `M+MG`, where printed pp.60-62 say the sign byte "is not
changed". The model's arm does the algebraic product for that reason
and cites this paragraph. No deck in the corpus exercises it: MCP's
own use (printed p.72) and IBM's examples (C22-6578 Problems 2.10 and
2.12) are all `(BU, ...)`, binary unsigned, both signs zero.

**And the opcode checks out independently.** §6.21.24 prints
"STRAP Notation: *(B, 48, 4), NAME .0, 64" and "Operation Code:
01100" -- note that the floating-point multiply on p.75 prints
"Operation Code: 00110" for the same mnemonic, so the two are
distinguished here as everywhere else by the data description.  The
VFL integer codes in the Reference Manual are six bits ending in 1,
and `011001` is 25 decimal, which is the
code the model decodes and the code `X22-6533`'s pocket card gives.
Three documents, one number.

> Read in the OCR and then **re-read on the rendered page** before
> being quoted here, per `docs/ocr/README.md`.

---

## >>> AND THE SAME TWO NUMBERS RUN THROUGH THE WHOLE RADIX-CONVERSION FAMILY <<<

Read on 2026-10-25 because `/` alone does not unblock MCP printed
p.24: the same eleven-line block uses `CV` and `LTRCV` two
instructions later, and both are also unimplemented.

### `CV` (Convert), Reference Manual printed p.73 (verified on the page)

> "A field from the accumulator is converted as an integer from
> binary to decimal or from decimal to binary depending on the
> setting of the radix modifier. If the original field is binary, it
> is obtained at an **implied offset of 68** and its length is **48
> numeric bits**. The decimal result is loaded into the cleared
> accumulator **at the specified offset**. If the original field is
> decimal, it is obtained at the specified offset. The binary result,
> which can be a maximum of 48 significant bits, is loaded into the
> cleared accumulator **at offset 68**. The sign modifiers operate on
> the sign bit in the sign byte register; **all other positions of the
> sign byte register remain unchanged**."

And under Radix: "Higher-order bits (positions 0-11 of the
accumulator) are ignored and lost. **No indication of this loss is
retained.**" -- a silent truncation, which is unusual enough in this
manual to be worth implementing deliberately.

### `DCV` (Convert Double), printed p.74

Same shape with the other pair of numbers: binary field "at an
implied offset of **20** and its length is **96** numeric bits", and
the binary result of a decimal conversion goes "into the cleared
accumulator at offset 20". No more than 80 significant bits convert
without a partial field condition; the decimal result is at most 24
digits.

### The four constants are two

| operation | implied field | IBM bits | PAU field |
|---|---|---|---|
| `CV` binary operand/result | offset **68**, 48 bits | 12-59 | single-precision fraction |
| `DCV` binary operand/result | offset **20**, 96 bits | 12-107 | double-precision fraction |
| `*` product | offset **20**, 96 bits | 12-107 | double-precision fraction |
| `/` quotient | the instruction's offset | -- | not PAU-fixed |

`127 - 59 = 68` and `127 - 107 = 20`. **Every implied offset in the
VFL arithmetic and conversion set is one end of one of the PAU's two
result fields**, which is what `R23-9694` printed p.117 says outright
for `*` and printed p.121 repeats for `/`. The Reference Manual
states four numbers that look arbitrary beside each operation;
there are two, they are the floating-point unit's, and printed p.74
says so -- see the correction at the end of this file.

> And printed p.71's aside finally parses: "`DCV` is used instead of
> `CV` because of the offset of 20." A multiply leaves a 96-bit
> product at 20, which is `DCV`'s field and not `CV`'s.

### `LTRCV` (Load Transit Converted), printed p.73

> "The addressed **storage** field is converted as an integer ... The
> transit register, **storage location 15**, is cleared. The four
> low-order bits of the transit register form a sign byte in which
> the leftmost bit is the sign of the addressed storage operand as
> modified by the negative sign modifier. The remaining three bits of
> the sign byte are zero. The converted field is placed in the
> transit register **positioned to the left of the four-bit sign
> byte**. **The accumulator is not altered by this operation, and the
> offset field of the instruction is ignored.**"

PF if a binary-to-decimal result exceeds 15 significant decimal
digits, or a decimal-to-binary result exceeds 48 significant bits
(low-order 48 kept), or the storage field exceeds 15 decimal digits.
Arithmetic result indicators are "set according to the final result
in the transit register" -- not the accumulator.

> `LTRCV` and `LCV` are the pair that differ only in destination:
> `R23-9694` printed p.129 tabulates all four, "LCV ... Storage ->
> Accumulator; LTRCV ... Storage -> Transit Register; CV ...
> Accumulator -> Accumulator; DCV ... Accumulator -> Accumulator".
> `LCV` is already built.

## >>> MCP PRINTED p.24 IS THE ORACLE AND IT CHECKS ALL OF THIS <<<

```
L(BU,26), $TC, -60           -GET TIME          line 19
/I(BU,6), 60, -60                               line 21
C0011(BU,6), $RM+.54         -SECONDS IN RM     line 22
CM0101(BU,6), 0.24($1)       -SAVE BINARY SECS  line 23
/I(BU,6), 60, -60            -COMPUTE HOUR AND  line 24
CV(BU), $L, 16               -CONVERT HOURS     line 25
LTRCV(BU,6), $RM+.54         -CONVERT MINUTES   line 26
C0011(BU,8), $TR+.52, 8                         line 27
LTRCV(BU,6), 0.24($1)        -CONVERT SECONDS   line 28
C0011(BU,8), $TR+.52                            line 29
```

**`-60` is a seven-bit two's complement offset, which is 68.** Line
19 puts the 26-bit clock at offset 68. Line 21 divides it there and
the quotient comes back at 68. Line 24 divides *that* and the hours
come back at 68. Line 25 is `CV`, **whose binary operand is at an
implied offset of 68 and nowhere else.**

> The offset MCP writes on four consecutive instructions is the one
> number at which `CV` will read. A 1963 operating system and a 1961
> manual agree through a chain of four instructions, and neither was
> consulted for the other when `-60` was transcribed off the scan.

**And lines 26-27 check `LTRCV` the same way.** `LTRCV` leaves a
four-bit sign byte in the transit register's bits 60-63 with the
converted digits to its left; MCP then reads `$TR+.52` for **eight
bits -- positions 52-59**, which is exactly the two byte-size-four
decimal digits immediately above that sign byte. Minutes and seconds
are at most 59: two digits, never three.

### Every offset in the block, decoded out of the printed columns

Not read off the STRAP statements -- taken from the BINARY OUTPUT
column that `tests/verify_mcp_bootstrap_p24.py` checks, by the
seven-bit rule of `listing_typography.md` (bits 12-17 of the second
group hold `offset >> 1`, bit 18 holds `offset & 1`):

```
line 19  L(BU,26),$TC,-60          offset = 68
line 21  /I(BU,6),60,-60           offset = 68
line 22  C0011(BU,6),$RM+.54       offset =  0
line 23  CM0101(BU,6),0.24($1)     offset =  0
line 24  /I(BU,6),60,-60           offset = 68
line 25  CV(BU),$L,16              offset = 16
line 26  LTRCV(BU,6),$RM+.54       offset =  0
line 27  C0011(BU,8),$TR+.52,8     offset =  8
line 28  LTRCV(BU,6),0.24($1)      offset =  0
line 29  C0011(BU,8),$TR+.52       offset =  0
line 30  ST(BU,24),XLRIN           offset =  0
```

**`-60` encodes as 68**, which is seven-bit two's complement and
which is CV's implied offset exactly.

**And the three result offsets are 16, 8 and 0** -- hours, minutes,
seconds -- each two byte-size-four BCD digits, assembled into the
low 24 bits of the accumulator and stored in one go by line 30's
`ST(BU,24)`. Six digits, HHMMSS. Nothing in the manual says a
conversion result is two digits wide; the program says it, and the
widths and offsets it chose only fit together if `CV` reads its
binary operand at 68 and `LTRCV` writes its digits immediately above
a four-bit sign byte.

**Lines 26 and 28 carry offset 0 and the manual says the offset is
ignored for `LTRCV`.** MCP writes the one value that cannot mislead.
That is a small confirmation, but it is the kind that cannot be
arranged after the fact.

> **And it explains line 23, which otherwise looks redundant.** Line
> 22 puts the binary seconds at accumulator offset 0 and line 23
> immediately saves them to memory. Why save what is already in the
> accumulator? **Because line 25's `CV` loads "into the CLEARED
> accumulator"** -- the seconds at offset 0 do not survive it. Line
> 28 reads them back out of memory to convert them. A model that
> implemented `CV` without the clearing would run this program
> correctly anyway and be wrong; a model that cleared only the
> result field would leave line 28 converting a value it had already
> converted.

**So p.24 needs three operations, not one:** `/`, `CV` and `LTRCV`.
Building `/` alone moves the first refusal from `001213.00` to
`001217.00` -- line 25, the `CV` -- because the second `/` at
`001216.00` will then also run.

---

## >>> AND THE REFERENCE MANUAL EXPLAINS IT TOO, ON PRINTED p.74. <<<
## A CORRECTION TO THIS FILE, 2026-10-25

Everything above about the PAU is right, and the framing around it
was wrong. This file said the Reference Manual "states four
unexplained numbers" and that only the CE manual says why. **It does
not.** Printed p.74, in the right-hand column beside Figure 19, two
pages after the MULTIPLY section that leaves them bare:

> "The fixed offsets used in the accumulator conversion operations
> are designed to facilitate conversion between binary floating point
> and decimal formats. Thus, the **48-bit binary field at offset 68**
> used in CONVERT corresponds to the fraction field of a
> **single-precision floating point number**; and the **96-bit binary
> field at offset 20** used in CONVERT DOUBLE corresponds to the
> fraction field of a **double-precision floating point number**.
> This 96-bit field also corresponds to **the result field of a
> binary integer MULTIPLY instruction**."

That is the entire unification -- 68/48 single, 20/96 double, and
multiply landing in the double field -- stated normatively, in the
manual this project reads first.

**What the CE manual actually adds** is the MECHANISM rather than the
correspondence: "the actual multiplication in this operation is
performed by PAU", which says these are not merely laid out to match
the floating-point format but computed by the floating-point unit.
That is still worth having, and it is still what decided the sign.
But the constants were explained in the Reference Manual all along.

> **THE LESSON IS THE ONE THIS PROJECT KEEPS PAYING FOR.** The claim
> "the Reference Manual never explains this" was made after reading
> the MULTIPLY section and the DIVIDE section and not the two pages
> between them. `docs/NEXT.md` already carries the rule in capitals
> -- **SWEEP THE BACK MATTER OF A MANUAL BEFORE DERIVING ANYTHING
> FROM IT; a document you have CITED is not a document you have
> READ** -- and it was broken within the same session that re-quoted
> it. A negative claim about a source ("X does not say Y") is a claim
> about every page of X, and costs a sweep to make honestly.

## What is still missing

Nothing in the sourcing.

**`*` is implemented** -- `bsv/StretchExecute.bsv`, arm `6'b011001`,
with `decks/vfl_multiply.strap` checking IBM's own 20 x 5 by both the
storage and the immediate form, the same 24 x 24 product from two
different instruction offsets landing in the same place, the PF
truncation keeping the LOW 48 bits, and the accumulator being cleared
below the product.

**`/` is not**, and neither are `CV` and `LTRCV`, which the same
eleven lines of MCP need. Sourcing for all three is above and
complete. What each one costs:

* **`/`** -- quotient at the instruction's offset (not a constant,
  unlike multiply), remainder into RM with its low-order bit at
  position 59 and a four-bit sign byte in bits 60-63, and `ZD` with
  its "the division is not attempted, and both the accumulator and
  the remainder register remain unchanged" rule plus the CE manual's
  truncated-divisor corollary. Problem 2.12 is an oracle for it, and
  so is MCP p.24. Arm drafted, deck drafted, fifteen checks.
* **`CV`** -- a binary/decimal integer conversion between accumulator
  fields, one end of it pinned at offset 68. The model has no
  decimal arithmetic at all yet, so this is the first operation that
  forces a byte-size-four BCD representation into existence. That is
  the real cost, not the arm.
* **`LTRCV`** -- the same conversion with the operand taken from
  STORAGE and the result left in the transit register, offset
  ignored. Once `CV`'s conversion exists this is a different
  destination and a four-bit sign byte.

**The decimal question looked like the gate and it is much smaller
than that.** Three claims I wrote here on 2026-10-25 were checked and
two were wrong:

* ~~"`strap_asm.py` already builds BCD constants (printed pp.9-12's
  `(IQS*)DD` rows)"~~ -- **FALSE.** Those rows are console CHARACTER
  text in the 89-character set, where `'0'` is `0x60`. The `DD`
  emitter never reads the data description's MODE at all:
  `DD(D,8,4),12` assembles to `0x0C`, binary twelve, not `0x12`.
  Measured, not reasoned. Packed BCD is still writable today, as a
  radix literal -- `DD(DU,24,4),(16)123456` gives `0x123456` -- so
  nothing needs adding to the assembler, and `DD` must NOT be taught
  to read `D` as BCD: it would silently change rows that already
  verify, and no source says STRAP does that.
* ~~"the first operations that must actually convert radix"~~ --
  **`LCV` is already built and already converts.** What it has never
  been asked for is the BINARY-TO-DECIMAL direction.
* The representation needs nothing new. Reference Manual printed
  p.57: "In decimal operations, the accumulator is treated as 32
  four-bit digit positions." 32 x 4 = 128, so `SM128.mag` IS the
  decimal accumulator. `bcdToBinary` exists in `StretchALU.bsv`.

**So the gate is one function: `binaryToBcd`.** All three live
blockers -- MCP printed p.24 lines 25, 26 and 28 -- convert binary to
decimal, and that is the only direction the model cannot do. The
refusal at `StretchExecute.bsv` is an exemption list with `LCV` in
it; the conversions join the list.
