<!-- PROVENANCE, and read it before citing anything below. -->

> ## HOW THIS FILE WAS MADE, AND WHAT THAT IS WORTH
>
> Written on 2026-10-25 by a **delegated agent** working in parallel
> with two others, each told to render and READ the pages it quotes
> rather than trust `docs/ocr/`. It is research, not transcription,
> and it has NOT been checked line by line by the session that
> committed it.
>
> **What was independently re-verified before commit** is listed at
> the end of this banner. Everything else carries the agent's word
> and its page citation, which is exactly as much as a page citation
> is worth: go and look.
>
> **Rule 4 still binds.** No encoding or semantic in this file may be
> built into `bsv/` or a deck without opening the cited page first.
> These files exist to say WHICH page, and to stop the next session
> re-reading six manuals to find it. They are a finding aid with
> citations, one level above `docs/ocr/`, and a level below a
> transcribed deck.

> **Re-verified by the committing session, both by measurement:**
> (1) `DD(D,8,4),12` assembles to `0x0C`, binary twelve -- the `DD`
> emitter ignores the data description's mode, so this file is right
> that `strap_asm.py` builds no BCD, and `docs/vfl_arith_spec.md`
> was wrong to say it did; (2) the sign-byte table on Reference
> Manual **printed p.36** was rendered and read, and it does put `S`
> at register position 4 in every row -- so `raw[bsz - 1]` in
> `StretchExecute.bsv` reads a ZONE bit as the sign for byte sizes
> 5-8, and `min(bsz,4)-1` is correct. The other bug it reports --
> `LCV` not clearing the sign byte register's low four bits -- is
> NOT yet re-verified.

---

# Decimal in this model, and `CV` / `DCV` / `LTRCV`

Written 2026-10-25 against a RUNNING test suite, so nothing under
`bsv/`, `tests/`, `decks/` or `strap/` was touched. Everything below
is read-only evidence plus a design.

Page convention, as the task set it and as I used it:
Reference Manual `22-6530-2` printed N = PDF N+3;
CE manual `R23-9694` printed N = PDF N+1.
**Every manual quotation below was read off a 200-dpi render of the
page named, not off `docs/ocr/`.** The renders are in this scratchpad
(`rm20-020.png`, `rm40-040.png`, `rm60-060.png`, `rm61-061.png`,
`rmc74..77-0xx.png`, `rmL71-071.png`, `ce101-101.png`).

`docs/vfl_arith_spec.md`'s section "AND THE SAME TWO NUMBERS RUN
THROUGH THE WHOLE RADIX-CONVERSION FAMILY" is taken as given and not
re-derived. This document builds on it and fills the gaps it names. It
adds three things that document does not have: Reference Manual printed
p.74's own statement of why the offsets are 68 and 20 (which that
document derives instead from the CE manual), Figure 19 on the same
page — a complete IBM worked program using all four conversions — and
two defects in the already-shipped `LCV` arm.

---

## 0. THE GATE QUESTION: what does this model need in order to do decimal at all?

**Much less than the phrase "add decimal arithmetic" suggests, and the
answer is five items, of which two already exist.**

The reason is structural and worth stating before the evidence: on the
7030 a decimal number is not a different *kind* of machine quantity.
It is the same bits, read four at a time.

1. **In storage: nothing new.** A decimal field is an ordinary
   bit-addressed VFL field. `extractFieldBits` /
   `insertFieldBits` in `bsv/StretchVFL.bsv` already fetch and
   deposit it. What changes is only the *interpretation* of the bits
   once fetched.

2. **In the accumulator: nothing new.** Reference Manual printed p.57:
   "In decimal operations, the accumulator is treated as 32 four-bit
   digit positions." The accumulator in this model is
   `SM128 { sign; mag }` (`bsv/StretchALU.bsv` l.49, `accToSM`), and
   `mag` is literally the 128 bits of words 8 and 9. 32 x 4 = 128.
   **`SM128.mag` IS the decimal accumulator already** — it just has to
   be read as a digit string instead of as a binary integer by the
   arms that are in decimal mode. No second register, no tagged union,
   no change to `readAcc`/`writeAcc`/`packAcc`.

3. **The accumulator sign byte register: already modelled, already
   right.** `bsv/StretchFP.bsv` ll.78-81 put the sign at BSV bit 59
   (IBM bit 4) and the flags T/U/V at BSV 58:56 (IBM 5-7), with the
   zone bits IBM 0-3 above. That is exactly what the CE manual's
   table (printed p.100, below) requires, for every byte size.

4. **Two pure digit functions.** `bcdToBinary` **already exists** —
   `bsv/StretchALU.bsv` l.159, written for `LCV` — and is correct for
   byte sizes 1..8 including the "converted to byte size four"
   truncation. Its inverse, **`binaryToBcd` does not exist** and is
   the single genuinely new piece of arithmetic this whole subject
   needs.

5. **One line of offset masking.** Printed p.57: in decimal the offset
   is "limited to these digit positions and hence to a multiple of
   four by ignoring the two low-order bits of the offset specified by
   the effective address of the second half-word." So
   `offSh_dec = offSh & ~7'b11`.

That is the whole gate. **The model needs an inverse of a function it
already has, and a two-bit mask.** It does not need a new storage
format, a new accumulator, a new sign convention, or an assembler
change.

### Where the model refuses today

`bsv/StretchExecute.bsv` ll.2245-2253, inside `vflIntOp`:

```
      Bool radixConv = (vi.code == 6'b000011);
      if (vi.m.decimal == 1 && !radixConv)
        ind = setOpInvalid(ind);
```

One `if`. Decimal-moded VFL integer arithmetic sets OP (indicator 15)
and no-ops; `LCV` (`000011`) is the sole exemption, because for a
radix conversion bit 53 is *which way to convert*, not *do decimal
arithmetic*. The header at l.16 and l.2186 and `strap/strap_asm.py`
l.122 all say the same thing in prose.

**Note the shape of the gate: it is an exemption list, not a
rewrite.** Adding `011011` (CV), `111011` (DCV) and `100011` (LTRCV)
to `radixConv` is literally the whole change to the guard. The three
arms then do their own work. Nothing else in the file has to learn
about decimal for `CV`/`DCV`/`LTRCV` to work.

---

## 1. THE DECIMAL REPRESENTATION

### 1a. Digits — Reference Manual printed p.17 (PDF 20), "Operand Designation"

> "In decimal integer arithmetic, the digits 0 through 9 are
> represented by the ten four-bit binary integers 0000 through 1001.
> To these four bits, extra high-order bits (zone bits) may be added
> to permit alphameric representation. A maximum of four zone bits can
> be used, which makes the decimal character size, or byte size, a
> maximum of eight bits. Decimal arithmetic makes use of variable
> length fields. For unsigned data, the entire field is treated as a
> group of numeric bytes. All bytes have the same byte size, with a
> possible exception of the high-order byte. For signed data, the
> low-order byte is interpreted as a sign byte. The sign byte has the
> same size as the numeric bytes."

and, the sentence that makes item 0.2 above a fact rather than a
convenience:

> "Decimal information placed in the accumulator always has byte size
> 4. The zone bits of decimal bytes do not enter the accumulator or
> the accumulator sign byte register. The zone bits of the sign byte
> register may be used to set the zone bits of decimal bytes in
> storage."

Figure 4 on the same page is the worked picture: a 30-bit signed
decimal field at byte size 6 holding `0 9 4 2 -` — four numeric bytes
of six bits plus a six-bit sign byte.

### 1b. Byte size and radix — Reference Manual printed p.58 (PDF 61), "Radix and Byte Size"

The dense one. Verbatim, the parts that are code:

> "Bit 53 of the instruction, the *radix* modifier, specifies the type
> of arithmetic to be performed, the interpretation of the byte size
> field in the instruction, and the byte size of the accumulator
> operand. Binary arithmetic is specified if the bit is zero; decimal
> arithmetic is specified if the bit is one."

> "If decimal arithmetic is specified, the byte size of the
> instruction defines the length of each byte in the storage field
> including the sign byte if the data are signed. Decimal digits are
> represented in four-bit binary-coded decimal form and, therefore,
> can be stored in compact form. ... Decimal arithmetic can be
> performed on data of any byte size. **If the byte size is greater
> than four, only the four low-order bits of each byte take part in
> the operation. The remaining bits of each byte are ignored.** If a
> byte size less than four is specified in a decimal operation, normal
> decimal results may not be produced if two operands are involved
> whose effective signs are unlike, owing to the complementing
> procedure used. **When complementation is not involved, each byte of
> the storage operand is converted to a four-bit byte for processing
> by the addition of high-order zeros.** The byte size of the
> accumulator operand is assumed to be four in all decimal
> operations. The accumulator is always composed of integral 4-bit
> bytes regardless of the byte size or field length of the storage
> operand."

> "Since the field lengths are not constrained to be multiples of the
> byte size, the high-order byte of the memory operand may have an
> effective byte size less than that specified in the operation. The
> high-order byte is processed according to its effective byte size
> rather than the byte size specified in the operation."

The CE manual's 6.21.6 (printed p.100, PDF 101) repeats this almost
word for word; it is the same text, not an independent one. Its value
is the *table* in 1c.

For the model: `bcdToBinary(digitsRaw, numBits, bsEff)` already
implements every clause of that paragraph — per-byte masking to the
low four bits for `bsEff > 4`, zero-extension for `bsEff < 4`, and a
short high-order byte when `numBits` is not a multiple of `bsEff`. See
the loop at `bsv/StretchALU.bsv` ll.158-178. Nothing in 1b is
unbuilt.

### 1c. The sign — CE manual `R23-9694` printed p.100 (PDF 101)

**This is the one piece of the representation the Reference Manual
only describes in prose and the CE manual tabulates.** Printed p.100,
immediately above section 6.21.6:

```
  Byte Size    Sign Byte      Position in Sign Byte Register
                                      0 1 2 3 4 5 6 7
      1           S                   0 0 0 0 S 0 0 0
      2           ST                  0 0 0 0 S T 0 0
      3           STU                 0 0 0 0 S T U 0
      4           STUV                0 0 0 0 S T U V
      5           ZSTUV               0 0 0 Z S T U V
      6           ZZSTUV              0 0 Z Z S T U V
      7           ZZZSTUV             0 Z Z Z S T U V
      8           ZZZZSTUV            Z Z Z Z S T U V
```

> "Here S is the sign bit, T, U, and V are data flag bits, and the
> bits marked Z are zone bits. The sign and flag bits may be placed in
> or obtained from the 8-bit accumulator sign byte register. **The
> sign byte is positioned in such a way that the sign bit always
> occupies position 4 in the register.** Zone bits in the sign byte of
> a signed storage operand do not replace the zone bit positions in
> the sign byte register as an inherent part of any operation."

Reference Manual printed p.57 says the same from the other side: "If
the field is signed, the rightmost byte is the sign byte. The size of
the sign byte is specified by the byte size. The sign of the
accumulator operand is contained in the fifth bit position from the
left in the accumulator sign byte register."

**So: the sign byte is the RIGHTMOST byte of the field, it is INSIDE
the declared field length** (printed p.56), and **within that byte the
sign bit is the leftmost NON-ZONE bit.** In a right-justified field of
width `bsz`:

```
  sign bit index = min(bsz, 4) - 1
```

— `bsz-1` for byte sizes 1,2,3,4 and **3** for byte sizes 5,6,7,8,
because the extra width is zone bits stacked above S, not below it.

> **FINDING — the model has this wrong for byte sizes above four.**
> `bsv/StretchExecute.bsv` l.3101, inside the built `LCV` arm:
>
> ```
> Bit#(1) rawSign = !signed_ ? 0 : raw[bsz - 1];
> ```
>
> For `bsz` in 1..4 that is right. For `bsz` 5..8 it reads the
> **topmost zone bit** as the sign. Figure 4 on printed p.17 is
> precisely that case (signed decimal, byte size 6), and so is the
> Reference Manual's own `LCV(D,30,6)` in Figure 19 (printed p.74).
> Nothing in the suite can catch it: every `LCV` MCP writes is
> **unsigned** (`DU`/`BU`), so `signed_` is false and the expression
> is never evaluated. Flagged, not fixed — the suite is running.

### 1d. Invalid digit codes — THE MANUAL IS SILENT, AND THAT SILENCE IS LOAD-BEARING

I looked for a "ZD"-style invalid-digit check and **there is none**.

* The indicator list on printed p.46 (PDF 49) has `ZD` at bit 24 and
  it is **Zero Divisor**, defined on printed p.46 as "The divisor or
  divisor fraction is zero" — nothing to do with digits.
* The complete VFL indicator set — PF, LC, DF, TF/UF/VF, MOP, BTR,
  DTR, RLZ/RZ/RGZ/RN, AL/AE/AH — contains no digit-validity member,
  on printed p.46 or in any operation's INDICATORS paragraph I read.
* Printed p.58 says what happens to the bits it does not want, and it
  is always *ignore*, never *check*: "only the four low-order bits of
  each byte take part in the operation. The remaining bits of each
  byte are ignored"; and for a decimal result written back into a
  narrower storage byte, "Higher order bits in each result byte are
  dropped, and **no indication is given if these positions contain
  one-bits.**"

**So the 7030 does not validate decimal digits.** A byte whose low
four bits are `1010`..`1111` is simply fed to the adder. Printed p.58
says only what goes wrong, and it is wrongness without a flag: "If a
byte size less than four is specified in a decimal operation, normal
decimal results may not be produced..."

For the model this is a simplification and should be written down as a
deliberate one: `bcdToBinary` currently computes `digit * 10^k` for
`digit` up to 15, which is *a* behaviour for an invalid digit but not
a sourced one. **Where the manual is silent the model should be
silent too**, and the honest thing is a comment saying the hardware's
treatment of `1010`..`1111` is unknown, not an invented check. (The
CE manual's adder description, `R23-9694` printed pp.100-101, may
settle it; I did not chase it, because no deck in the corpus produces
an invalid digit.)

### 1e. Data flags and zone bits — printed p.57 (PDF 60)

> "All integer arithmetic operations that obtain data flag bits from
> storage place these bits into the indicator register. LOAD WITH FLAG
> also places the flag bits into the three rightmost bits of the
> accumulator sign byte register. The only other integer arithmetic
> operation that affects the data flag positions of the sign byte
> register as an inherent part of its operation is LOAD, which sets
> these three bit positions to zero."

and printed p.58:

> "Operations that place a signed result in storage, with the
> exception of STORE and STORE ROUNDED, do not alter the original flag
> bits or zone bits of the storage operand sign byte. STORE and STORE
> ROUNDED replace the data flag and zone bits in the sign byte and the
> zone bits in decimal bytes with the contents of the corresponding
> bit positions in the accumulator sign byte register."

That last clause is the only place the **zone** bits of a decimal
field are ever *written*, and it is `ST`/`SRD` only. Everything else
ignores them. For `CV`/`DCV`/`LTRCV` zone bits never arise: all three
produce byte-size-four output.

---

## 2. HOW BIG A JOB IS IT? — every other operation that would need decimal

I checked each VFL integer operation's own `Radix.` paragraph in the
Reference Manual. `strap/opcodes.py` ll.29-53 defines **24** VFL
integer / radix-conversion codes. **Every one of the 24 carries the
radix modifier** (bit 53) and the manual gives each one a `Radix.`
clause. But they do not all cost the same, and three of them cost
almost nothing. The count that matters:

### Class A — real decimal arithmetic: a BCD adder. **11 operations.**

| op | code | built? | printed page of its `Radix.` clause |
|---|---|---|---|
| `+` (ADD) | `000001` | **yes** | p.60 |
| `+MG` (Add to Magnitude) | `100001` | **yes** | p.61 ("as in ADD") |
| `M+` (Add to Memory) | `001001` | **yes** | p.61 |
| `M+MG` (Add Magnitude to Memory) | `101001` | **yes** | p.62 ("as in ADD TO MEMORY") |
| `M+1` (Add One to Memory) | `101011` | **yes** | p.63 ("as in ADD TO MEMORY") |
| `K` (Compare) | `010001` | **yes** | p.65 ("as in ADD") |
| `KF` (Compare Field) | `110001` | **yes** | p.65 |
| `KE` / `KFE` / `KR` / `KFR` | `010011`/`110011`/`010101`/`110101` | no | pp.65-67 ("as in ADD") |

(Eleven codes: `+`, `+MG`, `M+`, `M+MG`, `M+1`, `K`, `KF`, `KE`,
`KFE`, `KR`, `KFR`.)

The governing sentence is printed p.60's ADD: the radix modifier
"determines the properties of the adder, and controls complementation
and recomplementation when the effective operand signs are unlike. In
decimal arithmetic, four-bit bytes are used, only the four low-order
bits of each byte in the addressed operand participate in the
operation, and **a carry occurs from one byte to the next when a sum
byte exceeds 9.**"

That is the expensive item in the whole subject: a 32-digit BCD
add/subtract with decimal carry, decimal complementation and decimal
recomplementation, replacing `smAdd` (`bsv/StretchALU.bsv` l.61) in
decimal mode.

**Seven of these eleven codes are already built in binary**, in four
shared arms of `vflIntOp`: `000001`/`100001` (`+`, `+MG`) at
`StretchExecute.bsv` l.2538, `001001`/`101011`/`101001` (`M+`, `M+1`,
`M+MG`) at l.2750, and `010001`/`110001` (`K`, `KF`) at l.2918. Each
of those four arms would grow a decimal path through the same new
adder. **Four codes are unbuilt entirely**: `KE`, `KFE`, `KR`, `KFR`.

### Class B — decimal byte *placement*, no adder. **4 operations.**

| op | code | built? | what decimal changes |
|---|---|---|---|
| `L` (Load) | `000101` | **yes** | accumulator in 4-bit bytes; zone bits dropped (p.61) |
| `LWF` (Load with Flag) | `100101` | no | same, plus flags into ASBR 5-7 |
| `ST` (Store) | `001101` | **yes** | printed p.63: each 4-bit accumulator byte replaces the four low-order bits of each storage byte; high-order bits of a wider byte replaced from the ASBR zone bits |
| `SRD` (Store Rounded) | `101101` | no | printed p.64: "a four-bit byte with value five is added to the four-bit byte immediately to the right of the offset ... Carries are propagated as in any decimal addition" |

`SRD` needs a decimal increment but not a general adder.

### Class C — decimal is a TRAP, not arithmetic. **3 operations, and this is the surprise.**

Reference Manual printed p.68 (PDF 71), MULTIPLY:

> "If decimal is specified, this operation has the same action as LOAD
> TRANSIT AND SET, except that the two high-order bits of the left
> zeros counter are set to zeros."

and its PROGRAMMING NOTE:

> "A decimal MULTIPLY instruction can be used to produce an automatic
> entry to a subroutine, where the desired decimal multiplication may
> be performed..."

`*+` (printed p.69) and `/` (printed p.70) say the same: "It also
determines whether a binary division is performed or whether instead
the action is like that of a decimal LOAD TRANSIT AND SET." The same
page tabulates the discriminator the interrupt handler reads out of
the left-zeros counter:

```
  MULTIPLY             00
  DIVIDE               01
  MULTIPLY AND ADD     10
  LOAD TRANSIT AND SET 11
```

**So decimal `*`, `*+` and `/` are not decimal arithmetic at all.**
They load the transit register, set `DTR` (Decimal Transit), set two
bits of the left-zeros counter, and interrupt. On this machine decimal
multiply and divide were always software. Implementing them is
implementing `LTRS`, once.

### Class D — the radix conversions themselves. **4 operations.**

`LCV` (built, one direction), `LTRCV`, `CV`, `DCV`. Specified in
section 4 below. These need `binaryToBcd` and nothing else.

### Class E — `LTRS` and `LFT`. **2 operations.**

`LTRS` (printed p.68) needs only the BTR/DTR distinction — the radix
bit picks which indicator is turned on, and the transit register
itself is a bit pattern either way. `LFT` (Load Factor, printed p.69)
is "as in ADD" and clears the factor register with a four-bit sign
byte.

### The count

```
  24 VFL integer/conversion codes carry the radix modifier
   -  4 radix conversions                   (section 4; need binaryToBcd)
   -  3 that TRAP instead                   (*, *+, /  -> LTRS + DTR)
   -  2 that need only an indicator/register (LTRS, LFT)
   -  4 that need byte placement only       (L, LWF, ST, SRD)
  = 11 that need a real BCD adder           (+, +MG, M+, M+MG, M+1,
                                             K, KF, KE, KFE, KR, KFR)
```

**Of those 11 codes, SEVEN are already built in binary** — `+`, `+MG`,
`M+`, `M+MG`, `M+1`, `K`, `KF`, occupying four shared arms — and each
of the four arms would need a decimal branch through the same new
adder. Four codes (`KE`, `KFE`, `KR`, `KFR`) are unbuilt entirely.
**The connectives need nothing**: printed p.17, "The
accumulator byte size is always eight for connect operations. The
accumulator sign byte register is not used as part of the accumulator
in these operations." They carry no radix modifier.

---

## 3. WHAT THE ASSEMBLER ALREADY HAS — and it is NOT what the task supposed

> **`strap/strap_asm.py` does NOT build BCD constants. Measured, not
> inferred.**

### 3a. What `(IQS*)DD` actually is

`strap/charsets.py` is a **character-code** table, not a numeric BCD
table. Its header says so (ll.80-90): `IQS` is "the 89 Character Set"
of the console typewriter, reached via C28-6129 printed p.16's "the
set appropriate to the 7030 console typewriter, or Inquiry Station",
and Reference Manual printed p.166's grid. In that set
`'0' = 0o140 = 0x60` (`charsets.py` l.236) — not `0000`.

The other entry mode, `A`, *is* described by C28-6129 as "6-bit IBM
tape BCD", but that is **character** BCD: `charsets.py` l.125 has
`'0': 0o012`, i.e. the digit zero is `001010`, which is not the BCD
numeric zero the arithmetic wants. `charsets.py`'s own header already
warns that "internal BCD and 7-track tape BCD differ in a position or
two".

So the `(IQS*)DD` rows on printed pp.9-12 of the MCP listing are
**console message text**, and they share nothing with decimal
arithmetic but the three letters.

### 3b. What a `DD` with a decimal data description does

`strap/strap_asm.py` ll.2454-2468 is the whole numeric `DD` emitter:
it evaluates the field with `parse_dd_literal` (l.3229) and calls
`image.deposit(pos, length, value)`. **`length` comes from the dds;
the dds's MODE is never consulted.** `MODE_BITS` (l.3084) is read only
by the *instruction* encoder, for bits 51 and 53 of an instruction
word.

Measured, with the assembler as it stands:

```
X       DD(D,8,4),12        ->  byte 0x0C
Y       DD(DU,8,4),12       ->  byte 0x0C
Z       DD(BU,8),12         ->  byte 0x0C
```

All three deposit binary twelve. A decimal data description produces
no BCD.

### 3c. Can the `bsv/` side reuse it? — yes, by a different route

**A packed-BCD constant is writable today with no assembler change**,
using the radix-literal prefix `parse_dd_literal` already honours
(`strap_asm.py` l.3225, `_DD_RADIX_LITERAL`). Measured:

```
X       DD(DU,8,4),(16)12        ->  0x12
Y       DD(DU,24,4),(16)123456   ->  0x123456
```

i.e. **write the BCD digits as a hexadecimal literal.** Hex is
nibble-per-digit, which is exactly byte-size-four packed BCD, and for
a byte size other than four the deck can write `(2)` binary with the
grouping blanks the parser already allows (that idiom is sourced at
`strap_asm.py` l.3220 from MCP printed p.9's `(2)1111 1101`).

**So the answer to "can bsv/ reuse the same representation" is: there
is no assembler-side decimal representation to reuse, and none is
needed.** A `decks/vfl_convert.strap` can state its BCD operands as
`(16)` literals, and that is both honest about what the assembler does
and bit-exact. Changing `DD` to interpret a `D`/`DU` mode as "these
digits are BCD" would be a plausible future improvement **and a
breaking one** — it would silently change the meaning of any existing
`DD(D,...)` row — and no primary source I read states that STRAP does
it. **Do not add it on inference.**

---

## 4. IMPLEMENTABLE SEMANTICS FOR `CV`, `DCV`, `LTRCV`

All three verified on printed pp.72-74 (PDF 75-77). The quotations in
`docs/vfl_arith_spec.md` are accurate; what follows adds the parts
that document leaves out and resolves the ambiguities that would stop
someone coding.

### 4.0 Shared, all four radix conversions — printed p.72

**Direction.** Bit 53 "specifies the radix of the operand to be
converted, and hence also whether binary-to-decimal or
decimal-to-binary conversion is to be performed. If this bit is zero,
the original field is binary; if this bit is one, the original field
is decimal."

**Decimal side is always byte size four.** "Byte size four is assumed
in the accumulator conversion operation." Combined with printed p.73's
`LCV` clause — the decimal result is produced "in byte size four", and
a decimal *source* is converted "to byte size four" before conversion.

**Sign modifiers.** "In all cases these modifiers apply to the
original field before conversion and specify how its sign is to be
modified during the conversion. All possible values may be obtained
for the sign of the result." Printed p.73's `CV` spells out the
two-step rule that the other three inherit:

> *Unsigned.* "If the unsigned modifier is zero, the accumulator sign
> is taken as-is before the negative sign modifier is applied. If the
> modifier is one, the accumulator sign is taken as positive before
> the negative sign modifier is applied."
> *Negative Sign.* "If the negative sign modifier is zero, the
> accumulator sign is taken as-is after modification by the unsigned
> modifier. If the negative sign modifier is one, the accumulator sign
> after modification by the unsigned modifier is inverted."

In code: `sgn = (unsign ? 0 : srcSign) ^ invert`. **This is the rule
the built `LCV` arm already uses** (`StretchExecute.bsv` ll.3102-3104)
— confirmed, not changed.

**Indicators, shared (printed p.72):**

* *Partial Field (PF)* — permanent, sticky until it interrupts or is
  explicitly zeroed. "turned on if a radix conversion operation does
  not use all of the operand data provided." Per-operation conditions
  below.
* *Data Flags (TF, UF, VF)* — "In a radix conversion operation **using
  a storage operand**, these indicators are set according to the data
  flag bits, if any, of the storage operand. Any operation that
  normally affects these indicators will turn them off if the unsigned
  modifier is designated in the operation. **These indicators are not
  affected by CONVERT or CONVERT DOUBLE.**"
* *To-Memory Operation (MOP)* — "turned off by all radix conversion
  operations." Unconditional, all four.
* *Arithmetic Result (RLZ, RZ, RGZ, RN)* — "set according to the final
  result of the radix conversion operation" (for `LTRCV`, printed
  p.73 is explicit that "final result" means **in the transit
  register**).

> **GAP IN THE EXISTING MODEL, found while checking this.** The built
> `LCV` arm sets `MOP` and `PF` and the arithmetic results, but never
> touches `TF`/`UF`/`VF`. Printed p.72 requires them set from the
> storage operand's flag bits, and *turned off* when the unsigned
> modifier is given. Every `LCV` MCP writes is unsigned, so the
> required behaviour is "turn TF/UF/VF off" and the model leaves them
> alone. Not fixed here (suite running); it belongs with the `CV`
> work, which shares the rule.

> **SECOND GAP.** Printed p.72's `LCV`: "**The four low-order bits of
> the sign byte register are cleared.** The sign bit in the sign byte
> register is set according to the sign of the data as affected by the
> sign modifiers." The model's `writeAcc`
> (`StretchExecute.bsv` l.677) *preserves* the old flags via
> `sbFlags(sb)`. That is correct for `CV`/`DCV` — printed p.73: "all
> other positions of the sign byte register remain unchanged" — and
> **wrong for `LCV`**, which must zero IBM bits 5-7 as well as setting
> bit 4. `CV`/`DCV` can use `writeAcc` unchanged; `LCV` needs its own
> sign-byte write. The difference between the two ops is exactly one
> sentence on two facing columns, and it is easy to miss.

### 4.1 `CV` — Convert, opcode 27 = `6'b011011`

Printed p.73, verbatim and complete:

> "A field from the accumulator is converted as an integer from binary
> to decimal or from decimal to binary depending on the setting of the
> radix modifier. If the original field is binary, it is obtained at an
> implied offset of 68 and its length is 48 numeric bits. The decimal
> result is loaded into the cleared accumulator at the specified
> offset. If the original field is decimal, it is obtained at the
> specified offset. The binary result, which can be a maximum of 48
> significant bits, is loaded into the cleared accumulator at offset
> 68. The sign modifiers operate on the sign bit in the sign byte
> register; all other positions of the sign byte register remain
> unchanged."

> *Radix.* "If binary is specified, the 48-bit accumulator field at
> offset 68 is converted from binary to decimal. **Higher-order bits
> (positions 0-11 of the accumulator) are ignored and lost. No
> indication of this loss is retained.** The decimal result in byte
> size four is placed into the accumulator at the specified offset. If
> decimal is specified, the accumulator field at the specified offset
> is converted from decimal to binary. The binary result is placed
> into the accumulator at offset 68. The original decimal field is
> assumed to be byte size four."

**Implementable statement.**

Let `off` be the instruction's seven-bit offset, taken **as written,
in bits** — and note it is NOT masked to a multiple of four here.
Printed p.57's masking rule is stated for *decimal arithmetic
operations*; printed pp.72-74 never restate it for the conversions,
and MCP's own `CV(BU),$L,16` and `CV(BU,18),0.0,-32` both use
multiples of four anyway, so **the corpus cannot distinguish the two
readings.** Say so in the code and pick literal, which is what the
page says and what the project already settled for connectives.

```
  direction = (bit 53 == 0) ? BIN_TO_DEC : DEC_TO_BIN

  BIN_TO_DEC:
    src       = acc.mag[115:68]            // 48 bits at offset 68
                                           // acc.mag[127:116] = IBM 0..11
                                           // are DROPPED SILENTLY, no PF
    srcSign   = acc.sign
    sgn       = (unsign ? 0 : srcSign) ^ invert
    digits    = binaryToBcd(src)           // up to 15 digits, 60 bits
    acc.mag   = 0;  acc.mag |= digits << off
    acc.sign  = sgn
    ASBR flags and zone bits: UNCHANGED
    PF  if any nonzero digit of `digits` would land at or above
        bit 128, i.e. if (off + 4*significantDigits) > 128
    MOP = 0
    TF/UF/VF: UNCHANGED (no storage operand)
    RLZ/RZ/RGZ/RN from (sgn, digits == 0)

  DEC_TO_BIN:
    srcDigits = acc.mag >> off             // byte size four, 32 digits max
    srcSign   = acc.sign
    sgn       = (unsign ? 0 : srcSign) ^ invert
    val       = bcdToBinary(srcDigits, 128 - off, 4)
    acc.mag   = 0;  acc.mag |= (val & ((1<<48)-1)) << 68
    acc.sign  = sgn
    ASBR flags and zone bits: UNCHANGED
    PF  if val >= 2^48   ("the low-order 48 bits of the result are
                          placed in the accumulator. Any higher-order
                          bits are lost.")
    MOP = 0
    RLZ/RZ/RGZ/RN from (sgn, val == 0)
```

**Clearing.** "loaded into the **cleared** accumulator" is the whole
accumulator, all 128 bits, not just the result field. `docs/
vfl_arith_spec.md` already proves this from MCP printed p.24 line 23
(the binary seconds are saved to memory before the `CV` precisely
because the `CV` destroys them) and the reasoning is correct. Note
`LOAD` behaves identically — printed p.57, "LOAD clears the entire
accumulator regardless of the offset specified" — so this is the
house rule, not a `CV` peculiarity.

**Address, length and byte size are ignored.** Printed p.74's
PROGRAMMING NOTES: "The effective address of the first half-word, the
byte size field, and the length field are not normally used by either
the CONVERT or the CONVERT DOUBLE operations and are ignored."
**But**: "If progressive indexing is specified, the specified index
register will be modified as specified by the progressing indexing
code in the normal manner." So `CV`/`DCV` take **no storage read** and
still run the progressive-index block.

> **EVIDENCE MARKER: this clause is written to the page, not to a
> listing, and nothing in the corpus can check it.** None of MCP's
> four conversion sites uses progressive indexing — printed p.24 line
> 28's `0.24($1)` is ordinary indexing (P=0), and both `CV`s are
> unindexed. Mark it in the code the way `strap/charsets.py` marks its
> low-half arm: built from the manual, unexercised. In `vflIntOp` that means: do
not set `needsRead`, do not touch `vflReadsUsed`, leave
`vflWriteArmHandled` false, and let the shared trailing block at
l.3157 do the index update. **`vflNeedsRefill` with no own read is the
easy path** — `vflReadsUsed` is 0, so the refill can use prefetch slot
0 and nothing collides.

**Where the 68 comes from, and why it is not arbitrary.** Printed
p.74: "The fixed offsets used in the accumulator conversion operations
are designed to facilitate conversion between binary floating point
and decimal formats. Thus, the 48-bit binary field at offset 68 used
in CONVERT corresponds to the fraction field of a single-precision
floating point number; and the 96-bit binary field at offset 20 used
in CONVERT DOUBLE corresponds to the fraction field of a
double-precision floating point number. This 96-bit field also
corresponds to the result field of a binary integer MULTIPLY
instruction." `docs/vfl_arith_spec.md` derived this from the CE manual
and from `127-59`/`127-107`; **the Reference Manual says it outright
on printed p.74**, which that document does not cite. Worth adding
there.

### 4.2 `DCV` — Convert Double, opcode 59 = `6'b111011`

Printed p.74, verbatim:

> "A field from the accumulator is converted as an integer from binary
> to decimal or from decimal to binary depending on the setting of the
> radix modifier. If the original field is binary, it is obtained at an
> implied offset of 20 and its length is 96 numeric bits. **However, no
> more than 80 significant bits can be converted without causing a
> partial field condition.** The decimal result, which can be a maximum
> of 24 significant digits, is loaded into the cleared accumulator at
> the specified offset. If the original field is decimal, it is
> obtained at the specified offset. The binary result, which can be a
> maximum of 96 significant bits, is loaded into the cleared
> accumulator at offset 20. The sign modifiers operate on the sign bit
> in the sign byte register; all other positions of the sign byte
> register remain unchanged."

> *Radix.* "...Higher-order bits (positions 0-11 of the accumulator)
> are ignored and lost. No indication of this loss is retained. The
> decimal result in byte size four is placed into the accumulator at
> the specified offset. ... The binary result is placed into the
> cleared accumulator at offset 20. The original decimal field is
> assumed to be byte size four."

**`DCV` is `CV` with two constants changed and one extra PF clause.**

```
  BIN_TO_DEC:  src = acc.mag[115:20]       // 96 bits at offset 20
               result = binaryToBcd(src), up to 24 digits = 96 bits
  DEC_TO_BIN:  val placed at offset 20, 96 bits wide

  PF: "This indicator is actuated if the converted field exceeds 96
      significant bits in either type of conversion. The 96 low-order
      bits of the result are obtained, and higher-order bits are lost.
      The indicator is also actuated in a binary-to-decimal conversion
      if significant bits of the decimal result extend beyond the left
      end of the accumulator when this field is loaded into the
      accumulator at the specified offset. Since a maximum of 24
      decimal digits can be produced, no more than 80 significant bits
      can be converted without causing a partial field condition."
```

**The "80" resolves a real ambiguity and should be implemented
literally.** 2^80 ≈ 1.209e24, so an 80-bit binary number needs at most
25 decimal digits and a 24-digit result caps out at 10^24 - 1 < 2^80.
The manual does not say *which* of the two PF clauses fires for an
81-bit operand; it says both numbers and leaves the mechanism
implicit. The implementable reading, and the one consistent with
"the converted field exceeds 96 significant bits": **PF if the binary
source has more than 96 significant bits, OR if the decimal result
needs more than 24 digits, OR if the result placed at `off` runs past
the accumulator's left end.** Note the last clause is `off`-dependent
and the other two are not.

* *MOP; RLZ/RZ/RGZ/RN* — "set as in ADD."
* *TF/UF/VF* — not affected (printed p.72, `CV`/`DCV` exemption).

### 4.3 `LTRCV` — Load Transit Converted, opcode 35 = `6'b100011`

Printed p.73, verbatim:

> "The addressed storage field is converted as an integer from decimal
> to binary or from binary to decimal depending on the setting of the
> radix modifier. The transit register, storage location 15, is
> cleared. **The four low-order bits of the transit register form a
> sign byte in which the leftmost bit is the sign of the addressed
> storage operand as modified by the negative sign modifier. The
> remaining three bits of the sign byte are zero.** The converted field
> is placed in the transit register positioned to the left of the
> four-bit sign byte. **The accumulator is not altered by this
> operation, and the offset field of the instruction is ignored.**"

> *Modifiers.* "Unsigned; Negative Sign; Radix. These modifiers operate
> as in LOAD CONVERTED."

> *Indicators.* "*Partial Field (PF).* This indicator is actuated if
> the result in a binary-to-decimal conversion exceeds 15 significant
> decimal digits or if the result of a decimal to binary conversion
> exceeds 48 significant bits. In the former case the result is placed
> in the transit register up to its left end. In the latter case, only
> the 48 low-order bits of the result are placed in the transit
> register. This indicator is also actuated if the storage field
> specified in a decimal-to-binary conversion exceeds 15 decimal
> digits. Meaningless results are then obtained. *Data Flags (TF, UF,
> VF); To-Memory Operation (MOP).* These indicators are set as in ADD.
> *Arithmetic Result (RLZ, RZ, RGZ, RN).* These indicators are set
> according to the final result in the transit register."

**Implementable statement.** The transit register is word 15,
64 bits. Using the model's IBM-bit convention (`bsv/StretchStorage.bsv`
l.399, `transit`; BSV bit 63 = IBM bit 0):

```
  storage field: effective address, field length, byte size, immediate
    addressing -- "in the same manner as in integer arithmetic"
    (printed p.72, Field Definition). Same fetch as the built LCV arm.

  signed (unsign == 0): sign byte is the RIGHTMOST byte, width bsz,
    inside len_.  numeric part = raw >> bsz, numBits = len_ - bsz
    srcSign = raw[min(bsz,4) - 1]          // SEE 1c -- not raw[bsz-1]
  unsigned: numeric part = raw, numBits = len_, srcSign = 0

  sgn = (unsign ? 0 : srcSign) ^ invert
        -- printed p.73 says "as modified by the negative sign
           modifier"; the unsigned step is inherited from LCV, which
           the MODIFIERS line defers to.

  decimal source (bit 53 == 1):  val = bcdToBinary(numeric, numBits, bsz)
                                 payload = val, width 48 max
  binary  source (bit 53 == 0):  digits = binaryToBcd(numeric)
                                 payload = digits, 4 bits each, 15 max

  transit = 0
  transit[IBM 60]    = sgn          // leftmost bit of the 4-bit sign byte
  transit[IBM 61:63] = 0
  transit[IBM 0:59]  = payload, RIGHT-JUSTIFIED against IBM bit 60
                       (i.e. payload's low-order end sits at IBM 59)

  PF if (binary source   and significantDigits(payload) > 15)
     or (decimal source  and val >= 2^48)
     or (decimal source  and digitCount(storage field) > 15)
  MOP = 0
  TF/UF/VF from the storage operand's flag bits; turned OFF if unsign
  RLZ/RZ/RGZ/RN from the final transit register contents
```

**"Positioned to the left of the four-bit sign byte" means
right-justified against IBM bit 60, not left-justified at IBM bit 0.**
`docs/vfl_arith_spec.md` already proves this from MCP printed p.24
lines 26-27: `LTRCV(BU,6),$RM+.54` followed by
`C0011(BU,8),$TR+.52,8` reading IBM bits 52-59 — the two digits
immediately above the sign byte. That reasoning is sound and is the
decisive evidence; the manual's phrase alone is ambiguous.

**Only 60 numeric bits fit**, which is why the PF thresholds are 15
digits (60 bits) and 48 bits. The analogous sentence is spelled out
for `LTRS` on printed p.68 — "Since the low-order four bits of the
transit register are used as a sign byte, only 60 numeric bits can be
loaded into it" — and `LTRCV` inherits the geometry.

**The offset is ignored but the index register is not.** Printed p.73
says the offset field is ignored. It says nothing about progressive
indexing for `LTRCV`; by the Field Definition clause on printed p.72
("in the same manner as in integer arithmetic") the ordinary
progressive-index machinery applies, and MCP writes offset 0 on both
of its `LTRCV`s, which cannot distinguish the readings.

### 4.4 What `binaryToBcd` has to be

One function, mirroring `bcdToBinary`:

```
  function Tuple2#(Bit#(128), Bit#(7)) binaryToBcd(Bit#(128) v);
    // returns (packed byte-size-four digits, significant digit count)
```

Repeated division by ten, or the standard shift-and-add-3
double-dabble. For `DCV` it must handle 96 bits in and 24 digits out;
for `CV`, 48 bits in and 15 digits out; for `LTRCV`, 60 bits of room.
A single 128-bit-in / 32-digit-out version covers all three and the
callers mask. `bcdToBinary`'s fixed 16-iteration unrolled loop is the
shape to copy.

> **OPEN QUESTION, NOT SETTLED: what this costs in gates on the
> ULX3S.** Double-dabble over 96 bits is ~96 shift stages each with up
> to 24 conditional add-3s; a divide-by-ten chain is ~32 deep. Either
> is larger than anything `bcdToBinary` does (it is 16 multiply-adds
> by constants). The project already carries the floating divide and
> square-root arms, so the *logic* estimate in section 6 stands
> regardless — but **the area does not follow from that and I did not
> measure it.** Whoever builds this should synthesise the function
> alone before committing to a shape.

**This is the ONLY new arithmetic in the entire subject.**

---

## 5. `CV` / `DCV` / `LTRCV` / `LCV` ELSEWHERE IN THE CORPUS

```
grep -nE "\bCV\(|\bDCV\(|\bLTRCV\(|\bLCV\(" decks/*.strap
```

Every hit, with the MCP printed page it transcribes.

> **Scope warning, and it matters.** `decks/*.strap` covers the ~80
> MCP pages this project has transcribed, not MCP's 445. "Nowhere in
> the decks" is not "nowhere in MCP". I therefore also swept the OCR
> finding aid over all 445 printed pages — `docs/ocr/listing_index.py
> grep`, which `docs/ocr/README.md` explicitly blesses for "which
> page, and roughly which line" and explicitly forbids as a citation.
> Results are in 5c; they are page-locations, not readings.

**`CV` — three live instructions, two printed pages.**

| file:line | instruction | MCP printed page / line |
|---|---|---|
| `decks/mcp_bootstrap_p24.strap:113` | `CV(BU), $L, 16` | p.24 line 25 — convert hours |
| `decks/mcp_bootstrap_p78.strap:141` | `CV(BU,18), 0.0, -32` | p.78 line 12 (card reads `$CV`) |
| `decks/mcp_bootstrap_p78.strap:19,53,199` | the same row, in that deck's comments and its verification block | p.78 line 12 |

**`LTRCV` — two live instructions, one page.**

| file:line | instruction | MCP printed page / line |
|---|---|---|
| `decks/mcp_bootstrap_p24.strap:115` | `LTRCV(BU,6), $RM+.54` | p.24 line 26 — convert minutes |
| `decks/mcp_bootstrap_p24.strap:118` | `LTRCV(BU,6), 0.24($1)` | p.24 line 28 — convert seconds |

**`LCV` — built, and used on five printed pages.**

| file:line | instruction | MCP printed page / line |
|---|---|---|
| `decks/mcp_bootstrap_p17.strap:137` | `LCV(DU,8,4), $LZC+.3, 46` | p.17 line 34 |
| `decks/mcp_p17_card.strap:97` | same | p.17 line 34 |
| `decks/mcp_p17_channel_number.strap:8,96` | same | p.17 line 34 |
| `decks/connective_counts.strap:36` | same, quoted in a comment | p.17 line 34 |
| `decks/mcp_bootstrap_p23.strap:144` | `LCV(DU,8), XLRIN+1.24, 46` | p.23 line 49 — convert channel number |
| `decks/mcp_bootstrap_p30.strap:66` | `LCV(DU,8,4), XLRIN+1.36` | p.30 line 13 — convert number |
| `decks/mcp_bootstrap_p32.strap:64` | **`LCV(BU,18), $13`** | p.32 line 6 — "CONVERT CHANNEL TO DECIMAL" |
| `decks/mcp_bootstrap_p32.strap:113` | **`LCV(BU,18), $14`** | p.32 line 41 — "CONVERT TO DECIMAL" |
| `decks/load_converted.strap:35,88,92,96,100,103` | the `LCV` test deck, not MCP | — |

### 5a. >>> THE THING THIS GREP ACTUALLY FOUND <<<

**MCP printed p.32 lines 6 and 41 are `LCV(BU,18)` — BINARY source,
i.e. binary-to-decimal — and the model's built `LCV` arm refuses
exactly that direction.** `StretchExecute.bsv` ll.3086-3089:

```
              if (vi.m.decimal == 0) begin
                // Binary to decimal: see the scope note above.
                ind = setOpInvalid(ind);
```

with the scope note at l.3064 saying "ONLY DECIMAL-TO-BINARY IS
BUILT... nothing in the corpus calls for it."

**Something in the corpus does call for it, in two places**: MCP
printed p.32 lines 6 and 41.

### 5b. EXECUTED vs. MERELY TRANSCRIBED — I checked, and the distinction is real

**`decks/mcp_bootstrap_p32.strap` is never executed by this model.**
`tests/run_tests.sh` l.4327 runs `verify_mcp_bootstrap_p32.py`, which
is an assemble-and-compare-to-the-printed-binary check
(`listing_oracle.check_rows`), and **no Bluespec testbench reads that
deck** — `grep -rl mcp_bootstrap_p32 tests/ bsv/` returns only
`run_tests.sh` and the verifier itself. The same is true of
`mcp_bootstrap_p78.strap`.

So the honest statement, in two parts:

* **LIVE, in the running boot.** `docs/vfl_arith_spec.md` places the
  boot's current first refusal at `001213.00` and shows it moving to
  `001217.00` once `/` is built — `001217.00` is MCP printed p.24
  line 25, the `CV(BU)`. The boot therefore reaches, in order:
  `CV(BU),$L,16` then `LTRCV(BU,6),$RM+.54` then
  `LTRCV(BU,6),0.24($1)`. **All three are binary-to-decimal.** The
  already-built `LCV(DU,8,4)` on printed p.17 is decimal-to-binary
  and already runs.
* **LATENT, in verified-but-unexecuted decks.** MCP printed p.32
  lines 6 and 41 (`LCV(BU,18)`) and printed p.78 line 12
  (`CV(BU,18),0.0,-32`) are bit-exact against the listing and would
  hit `setOpInvalid` the moment anything executes them.

**So: every conversion instruction that stands between this model and
the next step of the MCP boot runs binary-to-decimal, the direction
that does not exist.** `binaryToBcd` is not a nicety needed by `CV`
alone; it is the only thing all three live sites have in common, and
building it also retires the `setOpInvalid` sitting inside the
already-shipped `LCV` arm.

### 5c. The OCR sweep over all 445 printed pages — a finding aid, not a citation

`python3 docs/ocr/listing_index.py grep ...` from the repository root
(printed = PDF-7 in volume one, PDF+249 in volume two):

| mnemonic | printed pages with an OCR hit |
|---|---|
| `DCV` | **none, in 445 pages** |
| `CV` (bare) | p.24, p.78 — exactly the two the decks already have |
| `LTRCV` | p.24, **p.300, p.340, p.356** |
| `LCV` | 29 OCR hits, far more pages than the 5 transcribed |

The three `LTRCV` sites beyond the transcribed corpus, as OCR renders
them (**unverified ink — page-finders only**):

```
  p.300   LTRCV(BU,6),0.20($1)
  p.340   LTRCV(DU,84),$R4+0.55   -CONVERT BIT ADDR TO $TR
  p.356   LTRCV(BU,18,8),$C       -N IN DEC TC TRANSIT REG
```

Two things follow and neither needs the ink confirmed. **`DCV` is
genuinely unused by MCP** — a zero across 445 pages is the one
OCR result that a glyph error cannot manufacture, and it means `DCV`
has no oracle in this corpus at all, only Reference Manual Figure 19.
And **`LTRCV` is used in both directions elsewhere in MCP** (`DU` on
p.340 is decimal-to-binary), so an `LTRCV` built for only one
direction would be a future refusal, exactly as `LCV` is today.

### 5d. And the Reference Manual ships an oracle for most of it

Printed p.74, Figure 19, "Radix Conversion" — a complete worked
program with IBM's own notes:

```
  NAME   STATEMENT                      NOTES
         LCV  (D, 30, 6), 1900.0, 8
         LTRCV(D, 30, 6), 1900.30, 0      1
         *    (B, 64, 4), $TR, 8          2
         DCV  (B, 0, 8), 0, 0             3
         ST   (D, 54, 6), 2000.0, 0

  1. Converts multiplier and places it in transit register.
  2. The offset of the LCV and the * instruction should be the same.
     A byte size of four is used in * because of the four-bit sign
     byte in the transit register.
  3. DCV is used instead of CV because of the offset of 20 produced
     by the * instruction.
```

"Given two four-digit signed decimal integers (byte size six) in
locations 1900 and 1900.30, form the eight-digit product and store it
in location 2000."

**But it does NOT run end-to-end inside the three-operation scope, and
that must be said plainly before anyone writes the deck.** Of its five
instructions:

| # | instruction | runnable with CV/DCV/LTRCV built? |
|---|---|---|
| 1 | `LCV(D,30,6),1900.0,8` | yes — but **signed decimal at byte size six**, i.e. exactly the `bsz > 4` sign-bit case section 1c shows the model gets wrong. Fix 1c first and this line becomes the regression test for it. |
| 2 | `LTRCV(D,30,6),1900.30,0` | yes — decimal-to-binary into the transit register |
| 3 | `*(B,64,4),$TR,8` | yes — binary `*` is already built (arm `011001`) |
| 4 | `DCV(B,0,8),0,0` | yes — binary-to-decimal from offset 20 |
| 5 | `ST(D,54,6),2000.0,0` | **NO.** A decimal `ST` is Class B, unbuilt: printed p.63's byte-replacement and ASBR-zone-bit rules. |

So the usable form of this oracle is **the first four instructions,
checked against the accumulator and transit register directly** rather
than against the word stored at location 2000. That still exercises
every one of `CV`'s siblings and IBM states the intermediate shapes in
its own notes. The fifth line waits for decimal `STORE`.

With that caveat it is still a better oracle than anything that could
be invented, and it comes with its own expected answer. The three
`*`-family oracles in `docs/vfl_arith_spec.md` came from `C22-6578`;
this one is in the Reference Manual itself and that document does not
mention it.

---

## 6. ESTIMATE OF SIZE — honest

**Adding `CV`, `DCV` and `LTRCV`: a ONE-ARM JOB, three times over,
plus one new function. Call it one working session.**

Justification, item by item:

* The representation question — the one the task calls the gate — is
  **already answered by the existing code**. `SM128.mag` is the
  128-bit accumulator and printed p.57 says the decimal accumulator is
  those same 128 bits as 32 digits. No new type, no new register, no
  change to `readAcc`/`writeAcc`/`packAcc`/`accToSM`.
* `bcdToBinary` exists and is correct. `binaryToBcd` is ~25 lines of
  the same shape.
* The guard is one boolean: `radixConv` grows from one opcode to four.
* `CV` and `DCV` take **no storage operand at all**, which removes the
  prefetch/bail-out/crossing-field machinery that is the bulk of every
  other VFL arm. They are each maybe 60 lines, mostly comment.
* `LTRCV` reuses the built `LCV` arm's fetch verbatim and differs only
  in destination and sign-byte placement.
* The oracles already exist: MCP printed p.24 (eleven lines, fully
  decoded in `docs/vfl_arith_spec.md`, and the one the running boot
  actually reaches), MCP printed p.78 line 12, and Reference Manual
  Figure 19 with its own stated answer — minus its fifth instruction,
  which is a decimal `STORE` and out of scope (see 5d).

The one item inside this estimate that is **asserted rather than
measured** is `binaryToBcd`'s gate count on the ULX3S; see the open
question in 4.4. It does not move the "one working session" figure for
the logic, but it could move the synthesis.

**Adding decimal ARITHMETIC: a STRUCTURAL CHANGE, and a different
project.** The eleven Class-A operations need a 32-digit BCD adder
with decimal carry, decimal complementation and recomplementation
(printed p.60), replacing `smAdd` in decimal mode for seven arms that
are already built and tested in binary. That is a change to the heart
of the VFL dispatch, not a new arm beside it, and it risks every
binary regression in the suite. `*`, `*+` and `/` are cheap only
because they *do not do decimal* — they trap.

**The honest ordering**, which the grep in section 5 settles:

1. `binaryToBcd`. One function, no arm. **All three of the live boot
   blockers need it and nothing else does.** It simultaneously retires
   the `setOpInvalid` sitting inside the already-shipped `LCV` arm,
   which MCP printed p.32 hits twice (latent — that deck is verified
   but never executed; see 5b).
2. `CV`. No storage operand. The boot's first stop after `/`, at
   `001217.00`; MCP printed p.78 line 12 is a second, latent site.
3. `LTRCV`. `LCV`'s fetch, a different destination. Two live sites on
   printed p.24; three more elsewhere in MCP by OCR (5c), one of them
   decimal-to-binary, so **build both directions**.
4. `DCV`. `CV` with 20/96 for 68/48. **Zero uses in all 445 printed
   pages of MCP** (5c); its only oracle anywhere is Figure 19.
5. The two `LCV` defects in section 1c and 4.0 — the `bsz > 4` sign
   bit, and the uncleared ASBR flags — fixed with `CV`, since they are
   the same two sentences on the same two pages. Figure 19's first
   instruction is the regression test for the first of them.

**Everything else decimal stays refused**, and the comment at
`StretchExecute.bsv` l.2186 should then say what section 2 found: that
what remains is eleven operations needing a BCD adder, three that trap
to software instead, and two that need an indicator.
