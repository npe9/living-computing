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

> **Re-verified by the committing session: nothing yet.** Two claims
> are load-bearing and cheap to check: that
> `writeWord(addrLeftZerosCount)` deliberately skips the counter
> fields so `setConnectiveCounts` is the only write path, and that
> every `LFT`/`SRD`/`*+` hit in `decks/` is floating-point by
> `strap_asm.py`'s `if mode in ('N','U'): return 'FP'`.

---

# Five unimplemented VFL integer operations: LFT, LWF, SRD, *+, LTRS

Specification for the Bluespec arms, from the Reference Manual (22-6530-2),
the CE Manual Vol. II (R23-9694) and the pocket card (X22-6533).

Written 2026-10-25.  No file under `bsv/`, `tests/`, `decks/` or `strap/`
was created or modified in producing this.

---

## 0. Provenance and verification log

**Page-number conventions used throughout.**

| Document | printed page | PDF page |
|---|---|---|
| `docs/22-6530-2_7030RefMan.pdf` | N | N+3 |
| `docs/R23-9694_7030_CE_Intro_Pgmg_Vol2_1961.pdf` | N | N+1 |

**Pages RENDERED AND READ as PNG** (`pdftoppm -r 200 -png`).  Every verbatim
quote below comes from one of these; the OCR in `docs/ocr/` was used only to
find them.

| PDF page | printed page | what is on it | file read |
|---|---|---|---|
| RefMan 40 | 37 | Factor Register paragraph; sign-byte-register prose | `rm40-040.png` |
| RefMan 41 | 38 | Transit Register paragraph | `rm41-041.png` |
| RefMan 59 | 56 | VFL format, modifier bit positions, immediate rules | `rm59x-059.png` |
| RefMan 64 | 61 | LOAD, **LOAD WITH FLAG**, Figure 12 | `rm64-064.png` |
| RefMan 67 | 64 | **STORE ROUNDED** (entire operation) | `rm67-067.png` |
| RefMan 70 | 67 | **LOAD TRANSIT AND SET** (opening paragraph) | `rm70-070.png` |
| RefMan 71 | 68 | LTRS modifiers/indicators/notes; **MULTIPLY** | `rm71-071.png` |
| RefMan 72 | 69 | **LOAD FACTOR**; **MULTIPLY AND ADD** | `rm72-072.png` |
| CE 101 | 100 | byte-size → sign-byte-register table | `ce101-101.png` |
| CE 105 | 104 | LOAD + **LOAD WITH FLAG**, with op codes | `ce105-105.png` |
| CE 111 | 110 | **STORE ROUNDED**, with op code | `ce111-111.png` |
| CE 117 | 116 | **LOAD TRANSIT AND SET**, with op code | `ce117-117.png` |
| CE 118 | 117 | LTRS notes; **MULTIPLY**, with op code | `ce118-118.png` |
| CE 119 | 118 | Multiply indicators; **LOAD FACTOR**, with op code | `ce119-119.png` |
| CE 120 | 119 | LFT indicators/notes; **MULTIPLY AND ADD**, with op code | `ce120-120.png` |
| CE 123 | 122 | §6.21.28 Review of VFL Integer Arithmetic | `ce123-123.png` |
| CE 124 | 123 | Review points 4-6 | `ce124-124.png` |
| RefMan 170 | 167 | Appendix, "Alphabetical Listing of Operation Codes" | `rmapx-170.png` |
| Pocket card 2 | — | OPERATION CODES: INTEGER ARITHMETIC table + modifier key | `pcv-2.png` |

**Rendered but NOT read** (so nothing is quoted verbatim from them; their
OCR agrees with the verified RefMan text for the same material):
CE PDF 112 (printed 111, SRD continuation), CE PDF 121 (printed 120, *+
continuation), CE PDF 102 (printed 101), RefMan PDF 68 (printed 65).

---

## 1. Opcodes — every source that prints one

The CE manual prints a **five-bit** code.  The six-bit VFL integer code is
that five-bit code with a trailing `1` appended.  This is not an inference:
it is confirmed against two arms already in `bsv/StretchExecute.bsv`.

- CE printed p.104 prints `L` as `Operation Code: 00010`; the implemented
  LOAD arm is `6'b000101`.
- CE printed p.117 prints `*` as `Operation Code: 01100`; the implemented
  MULTIPLY arm is `6'b011001`.

| Op | CE (5-bit, printed p.) | Pocket card X22-6533 p.2 | 6-bit code | decimal |
|---|---|---|---|---|
| LFT  Load Factor          | `00101` (p.118) | `abc001011` | `6'b001011` | 11 |
| LWF  Load with Flag       | `10010` (p.104) | `abc100101` | `6'b100101` | 37 |
| SRD  Store Rounded        | `10110` (p.110) | `abc101101` | `6'b101101` | 45 |
| \*+  Multiply and Add     | `11100` (p.119) | `abc111001` | `6'b111001` | 57 |
| LTRS Load Transit and Set | `11110` (p.116) | `abc111101` | `6'b111101` | 61 |

The pocket-card column was **render-verified** on `pcv-2.png` (PDF page 2,
"OPERATION CODES / INTEGER ARITHMETIC"), not taken from OCR.  The same table
gives `*  Multiply  abc011001`, matching the implemented arm, and
`L  Load  abc000101`, matching the implemented LOAD arm.  Both sources agree
digit for digit with each other and with `strap/opcodes.py`'s `VFL_INT_CODES`.

**The Reference Manual nowhere prints a bit pattern for any of the five.**  Its
VFL chapter gives no code alongside the operation paragraphs, and its Appendix,
"Alphabetical Listing of Operation Codes" on printed p.167 (verified on
`rmapx-170.png`), is a two-column **mnemonic-and-name** list with no code
column — `LFT  Load Factor`, `SRD  Store Rounded`, `LWF  Load with Flag`,
`*+  Multiply and Add`, `LTRS  Load Transit and Set`, each listed twice where
a VFL and a floating-point operation share the mnemonic.  So the Reference
Manual is silent on numeric opcodes; the CE manual and the pocket card are the
only two sources that print one.

**Modifier bits.**  Pocket card p.2, verified on `pcv-2.png`:
"Instruction Modifiers = abc / a = 0, data signed; b = 0, same sign;
c = 0, binary operation; a = 1, data unsigned; b = 1, invert sign;
c = 1, decimal operation."  RefMan printed p.56 gives the bit positions
(verified on `rm59x-059.png`):

> "All integer arithmetic operations are subject to three *modifiers*
> specified in bit positions 51 through 53 of the instruction. One modifier,
> bit 51, designates whether the storage field is signed or not; another,
> bit 52, designates whether the sign of the unreplaced field is to be taken
> as-is or inverted; the third, bit 53, designates whether the operation is
> decimal or binary."

Same page: field length = bits 35-40, byte size = bits 41-43, offset = bits
44-50.  `vi.m.unsign`, `vi.m.invert`, `vi.m.decimal` in the model already
carry these.

**STRAP spellings** (needed to write decks).  CE printed p.122, verified:

> "In other operations the mnemonic is merely altered by the addition of the
> letter N. For example, the negative sign modifier is applied to a LOAD WITH
> FLAG by the mnemonic LWFN."

and

> "In MULTIPLY AND ADD, the negative sign modifier as well as the immediate
> modifier applies to the storage operand used in the multiplication. For this
> reason, the N and I symbols are inserted between the multiply symbol and the
> add symbol. Thus a MULTIPLY AND ADD (\*+) with a negative immediate
> multiplier is encoded in STRAP notation as \*NI+. In all other applicable
> operations the N and/or I symbols follow the basic mnemonic."

So: `LFT`/`LFTN`/`LFTI`/`LFTNI`, `LWF`/`LWFN`/`LWFI`/`LWFNI`,
`SRD`/`SRDN` (no immediate — see §4), `LTRS`/`LTRSN`/`LTRSI`/`LTRSNI`,
and `*+`/`*N+`/`*I+`/`*NI+`.  The RefMan appendix on printed p.167
(`rmapx-170.png`) lists exactly `*+`, `*A+`, `*I+`, `*N+`, `*NA+`, `*NI+` — the
`A` (absolute-sign) forms are **floating-point only**, since VFL has no absolute
sign modifier, so the four VFL forms are the ones above.
`strap/opcodes.py` already carries all five
six-bit codes in `VFL_INT_CODES`, and `strap_asm.py` already strips the
`I`/`N`/`NI` suffixes for any VFL mnemonic, so **the assembler side needs no
work**; only the Bluespec arms are missing.

---

## 2. LFT — Load Factor — `6'b001011` (11)

### 2.1 Operation paragraph, verbatim

Reference Manual, **printed p.69** (`rm72-072.png`):

> **Load Factor (LFT)**
>
> The factor register (FT) is cleared. A four-bit sign byte, in which the
> leftmost bit is the sign of the addressed storage operand as modified by the
> negative sign modifier, is placed in the four low-order bits of FT. The
> remaining three bits of this sign byte are zero. The numeric part of the
> addressed operand is positioned to the left of this sign byte in FT.

CE Manual §6.21.25, **printed p.118** (`ce119-119.png`) — note the added
condition "For a signed operation", which the Reference Manual does not have:

> The factor register (FT) is cleared to zeros. For a signed operation, a
> 4-bit byte, in which the leftmost bit is the sign of the addressed storage
> operand as modified by the negative sign modifier, is placed in the four
> low-order bits of FT. The remaining three bits of this sign byte are zero.
> The numeric part of the addressed operand is positioned to the left of this
> sign byte in FT.
>
> STRAP Notation: LFT (D, 64, 4), NAME .0, 0
> Operation Code: 00101
>
> The accumulator contents are not altered by this operation. The offset has
> no meaning and is ignored.

### 2.2 Modifiers

RefMan p.69 and CE p.118 agree exactly:

> Unsigned; Negative Sign; Radix. These modifiers operate as in ADD.

The radix modifier has **no further effect** on LFT.  Unlike `*`, `*+`, `/`
and `LTRS`, a decimal LFT is not redefined as a transit operation — neither
manual gives a decimal LFT any different behaviour.  (The model's global
decimal refusal still catches it; see §10.4.)

### 2.3 Indicators

RefMan p.69, verbatim:

> *Partial Field (PF).* Since the four low-order bits of FT are used as a sign
> byte, only 60 numeric bits can be loaded into FT. This indicator is turned on
> if the numeric part of the field loaded contains more than 60 significant
> bits. If this occurs, FT is loaded up to its left end. Higher-order bits are
> lost.
>
> *Data Flags (TF, UF, VF); To-Memory Operation (MOP).* These indicators are
> set as in ADD.
>
> *Arithmetic Result (RLZ, RZ, RGZ, RN).* These indicators are set according
> to the contents of the factor register when the operation is complete.

CE p.119 (`ce120-120.png`) is word-for-word the same for all three.

RefMan p.69 adds one rule the CE does not (see §8):

> The lost-carry indicator cannot be turned on by this operation.

MOP "as in ADD" means **off** — the model already does
`ind = setBit(ind, ind_MOP, 0)` for the to-accumulator class.

### 2.4 Registers read and written

- **Reads:** the addressed storage field (or immediate operand).  Does not
  read the accumulator.
- **Writes:** the FACTOR REGISTER only.  `addrFactor = 14`
  (`bsv/StretchTypes.bsv:68`), a full 64-bit register
  (`bsv/StretchStorage.bsv:398  Reg#(Word64) factor`).
  - IBM bits 0-59 = numeric part, right-justified so the low-order numeric
    bit lands in IBM bit 59 (model bits `[63:4]`).
  - IBM bit 60 = sign (model bit `[3]`).
  - IBM bits 61-63 = zero (model bits `[2:0]`).
- **Does not touch:** accumulator (p.69 "The accumulator contents are not
  affected by LOAD FACTOR"), accumulator sign byte register, transit register,
  either counter.
- **Offset:** ignored ("The offset has no meaning in this operation and is
  ignored", p.69).

RefMan printed p.37 (`rm40-040.png`), Factor Register:

> The operation MULTIPLY AND ADD obtains one of the factors in the
> multiplication from the factor register as an implied operand. The factor
> register is a 64-bit register in location 14.
>
> The factor register is loaded as an implied operand in the operation LOAD
> FACTOR.

and printed p.38 (`rm41-041.png`), continuing:

> In an integer operation, the four low-order bits of the factor register form
> a 4-bit sign byte in which the flag bits are zero. In a floating point
> operation, the factor has the same format as a floating point word in storage
> whose flag bits are zero. The factor register is not altered as the implied
> operand of any other operation.

**"the flag bits are zero"** is a hard rule: unlike LWF, LFT never places data
flag bits into FT.  FT's IBM bits 61-63 are always zero after LFT.

---

## 3. LWF — Load with Flag — `6'b100101` (37)

### 3.1 Operation paragraph, verbatim

Reference Manual, **printed p.61** (`rm64-064.png`):

> **Load with Flag (LWF)**
>
> The LOAD WITH FLAG operation is the same as LOAD except that if the addressed
> storage field includes data flag bits, these bits are placed in the
> accumulator sign byte register in addition to setting the data flag
> indicators.

CE §6.21.11, **printed p.104** (`ce105-105.png`), identical wording plus:

> STRAP Notation: LWF (D, 28, 4), NAME, 0
> Operation Code: 10010

LOAD itself, which LWF inherits, RefMan printed p.61, verbatim:

> The entire left and right halves of the accumulator and the four low-order
> bits of the accumulator sign byte register are cleared. The numeric part of
> the addressed operand is placed in the accumulator as specified by the
> offset. The sign bit in the sign byte register is set according to the sign
> of the data as affected by the sign modifiers. The zone bits of the
> accumulator sign byte are not altered.

CE p.104 says "the entire left and right halves of the accumulator (128 bits)"
— same thing, with the width spelled out.

### 3.2 Modifiers and indicators

Both manuals, identically:

> Unsigned; Negative Sign; Radix. These modifiers operate as in ADD.
>
> *Partial Field (PF); Data Flags (TF, UF, VF); To-Memory Operation (MOP);
> Arithmetic Result (RLZ, RZ, RGZ, RN).* These indicators are set as in ADD.

Programming note, RefMan p.61 and CE p.104 word for word:

> LOAD, LOAD WITH FLAG, and LOAD CONVERTED are the only variable-field-length
> data handling operations that affect the data flag bit positions in the
> accumulator sign byte register as an implied operand. All other operations of
> this type leave these positions unchanged. No operation changes the zone bit
> positions in the accumulator sign byte register as an implied operand.

### 3.3 The exact bits LWF writes

This is the whole of the difference from LOAD, so it needs the sign-byte
layout.  **Both** manuals carry the table; CE printed p.100 (`ce101-101.png`)
is the cleaner copy:

```
Byte Size   Sign Byte     Position in Sign Byte Register
                          0 1 2 3 4 5 6 7
    1       S             0 0 0 0 S 0 0 0
    2       ST            0 0 0 0 S T 0 0
    3       STU           0 0 0 0 S T U 0
    4       STUV          0 0 0 0 S T U V
    5       ZSTUV         0 0 0 Z S T U V
    6       ZZSTUV        0 0 Z Z S T U V
    7       ZZZSTUV       0 Z Z Z S T U V
    8       ZZZZSTUV      Z Z Z Z S T U V
```

> Here S is the sign bit, T, U, and V are data flag bits, and the bits marked Z
> are zone bits. The sign and flag bits may be placed in or obtained from the
> 8-bit accumulator sign byte register. The sign byte is positioned in such a
> way that the sign bit always occupies position 4 in the register.

(The RefMan's copy is on printed p.36-37; the OCR of it is mangled, so the CE
copy is quoted.  Prose on RefMan p.37, verified, agrees: "The sign byte is
positioned in such a way that the sign bit always occupies position 4 in the
register.")

So, in the model's bit numbering — `addrAccSignByte = 10`
(`bsv/StretchTypes.bsv:62`), IBM bits 0-7 = model bits `[63:56]`:

| IBM bit | model bit | meaning | LOAD | LWF |
|---|---|---|---|---|
| 0-3 | `[63:60]` | zone bits Z | unchanged | unchanged |
| 4 | `[59]` | sign S | set from data + sign modifiers | same |
| 5 | `[58]` | flag T | **cleared** | **copied from operand** |
| 6 | `[57]` | flag U | **cleared** | **copied from operand** |
| 7 | `[56]` | flag V | **cleared** | **copied from operand** |

"the four low-order bits of the accumulator sign byte register are cleared"
(LOAD, p.61) = IBM 4-7 = model `[59:56]`.  LWF clears them and then writes
S T U V back.

**How many flag bits actually get written depends on byte size.**  CE printed
p.123 (`ce124-124.png`), review point 5, verbatim:

> The flag bits of the sign byte register are set to zero during a LOAD. In
> LWF, the flag bits of the sign byte register are replaced by the appropriate
> flag bits of the storage word. In such cases the actual number of flag bits
> set is dependent on the specified byte size. The only other method of
> altering the flag positions of the sign byte register is by addressing them
> as a storage operand.

**The per-byte-size breakdown that follows is read off the p.100 table; neither
manual enumerates it.**  Read against the table: byte size 1 supplies S only
(T, U, V stay cleared);
byte size 2 supplies S and T; byte size 3 supplies S, T, U; byte size 4 or
more supplies S, T, U and V.  Byte sizes 5-8 supply zone bits too, and those
are **discarded** — p.61: "No operation changes the zone bit positions in the
accumulator sign byte register as an implied operand", and CE p.100: "Zone
bits in the sign byte of a signed storage operand do not replace the zone bit
positions in the sign byte register as an inherent part of any operation."

### 3.4 Registers read and written

- **Reads:** the addressed storage field (or immediate operand).
- **Writes:** `addrAccLeft` (8), `addrAccRight` (9) — both halves cleared then
  loaded at the offset — and `addrAccSignByte` (10) IBM bits 4-7
  (model `[59:56]`).  IBM bits 0-3 of word 10 are left alone.
- **Does not touch:** FT, TR, left-zeros counter, all-ones counter.

### 3.5 Relationship to the implemented L arm

LWF is `6'b000101`'s arm with the sign-byte write widened.  The model's
`writeAcc` (`bsv/StretchExecute.bsv:677`) already preserves bits it is not
told to change; the LWF arm needs an additional path to put T/U/V into
word 10 `[58:56]`.  **The model is already extracting those flag bits** — the
FP side does `ind = setBit(ind, ind_TF, opnd0.flags[2])` at
`bsv/StretchExecute.bsv:1482`, and the VFL data-flag indicator setting
("set as in ADD") must already derive them, so the values exist; LWF only has
to also store them.

---

## 4. SRD — Store Rounded — `6'b101101` (45)

### 4.1 Operation paragraph, verbatim

Reference Manual, **printed p.64** (`rm67-067.png`):

> **Store Rounded (SRD)**
>
> The field from the accumulator is rounded by adding to its magnitude one-half
> of the proper radix in the position to the right of the offset. Carries are
> propagated as in any addition in that radix. This rounded field replaces the
> addressed storage field. If a signed operation is specified, the contents of
> the accumulator sign byte register replace the rightmost byte of the storage
> field after the sign bit has been modified by the negative sign modifier. The
> contents of the accumulator and the sign byte register are not changed by
> this operation. The accumulator sign is ignored in the actual rounding
> process.

CE §6.21.16, **printed p.110** (`ce111-111.png`), is word-for-word identical
except that it writes "in the **digit** position to the right of the offset",
plus:

> STRAP Notation: SRD(DU,20,4), NAME .0, 108
> Operation Code: 10110

### 4.2 Modifiers

RefMan p.64, verbatim:

> *Unsigned; Negative Sign.* These modifiers operate as in STORE.
>
> *Radix.* This modifier acts in the same manner as in STORE, except that in
> addition it governs the rounding process. If a binary operation is specified,
> a binary one is added to the field from the accumulator in the bit position
> immediately to the right of the specified offset. Carries are propagated as
> in any binary addition. If a decimal operation is specified, a four-bit byte
> with value five is added to the four-bit byte immediately to the right of the
> offset in the field from the accumulator. Carries are propagated as in any
> decimal addition. This action is equivalent to adding the five one decimal
> position to the right of the offset.

STORE's own modifier rules, which SRD inherits (CE printed p.109-110, OCR;
the RefMan's copy is on printed p.63-64):

- *Unsigned*: determines whether the stored field is signed.  When signed, the
  accumulator sign byte register replaces the rightmost byte of the field; if
  byte size < 8, only part of the sign byte register is stored, the number of
  bits being the byte size.
- *Negative Sign*: the sign bit from the accumulator sign byte register is
  inverted before being placed in the storage field.  The register itself is
  unchanged.  **If the unsigned modifier is specified, the negative sign
  modifier has no effect on the field stored. However, the result indicators
  are set according to the modified accumulator sign, whether it is stored or
  not.**
- *Radix*: in binary, byte size refers only to the sign byte length and the
  data is stored in eight-bit bytes.

### 4.3 Indicators

RefMan p.64, verbatim:

> *Partial Field (PF); To-Memory Operation (MOP); Arithmetic Result (RLZ, RZ,
> RGZ, RN).* These indicators are set as in STORE.
>
> *Lost Carry (LC).* This indicator is turned on when the rounding process
> causes a carry to be propagated beyond the left end of the field stored.

CE p.111 (OCR, not render-verified) repeats both, identically.

STORE's PF rule, which SRD inherits (CE printed p.109, OCR):
"turned on in a binary STORE if there is any one bit in the accumulator to the
left of the last bit position stored."  STORE's MOP: **on**.  STORE's
arithmetic-result rule: "set according to the data field stored. The sign of
the accumulator, as modified by the negative sign modifier, affects the setting
whether it is stored or not."

LC is the one indicator SRD has that STORE does not: STORE's own note on
RefMan p.64 says "The lost carry indicator cannot be turned on by a STORE
operation."

### 4.4 Programming notes

RefMan p.64, verbatim:

> The STORE ROUNDED operation does not change the contents of the accumulator.
> This is convenient in those problems in which it is desirable to store part
> of the accumulator contents rounded while retaining full precision in the
> accumulator for further calculation. The accumulator contents can be rounded
> by using ADD TO MAGNITUDE with an immediate address of 1 or 5 with the proper
> offset. An unsigned STORE ROUNDED addressing the accumulator as the storage
> operand can also be used for this purpose.
>
> A STORE ROUNDED with zero offset specified is equivalent to a STORE.

### 4.5 Immediate addressing is forbidden, and the failure mode is specified

RefMan printed p.56 (`rm59x-059.png`), verbatim:

> Immediate addressing is, of course, not possible in operations whose result
> is placed in storage. If immediate addressing is specified in a to-memory
> operation, the operation is not performed and the operation code invalid (OP)
> indicator is turned on.

CE p.122 states the restriction without the failure mode: "All VFL, other than
store type, arithmetic operations may specify immediate addressing."

The implemented ST arm already does exactly this
(`bsv/StretchExecute.bsv:2461-2466`: `if (immediate || ...) ind = setOpInvalid(ind)`).
SRD must do the same.

### 4.6 Registers read and written

- **Reads:** accumulator (words 8 and 9) and accumulator sign byte register
  (word 10).  Neither is modified.
- **Writes:** the addressed storage field only.
- **Does not touch:** FT, TR, counters.
- **Arithmetic, concretely** (model terms): let `acc = readAcc(st)`,
  `offSh = vi.a.offset`.  Binary:
  `rounded = (acc.mag + (offSh == 0 ? 0 : (128'b1 << (offSh - 1)))) >> offSh`.
  Zero offset adds nothing, which is the manual's "equivalent to a STORE".
  The sign used for the stored sign byte is `acc.sign ^ vi.m.invert`, and
  `acc.sign` plays **no** part in the addition ("The accumulator sign is
  ignored in the actual rounding process").
- **LC condition:** the carry out of the stored field.  "Beyond the left end of
  the field stored" — i.e. out of the numeric width of the storage field, not
  out of the 128-bit accumulator.  Note this is distinct from PF: PF reports
  accumulator bits above the stored field that were *already* there; LC reports
  a bit that *the rounding produced*.  A field that is already all ones gives
  both; a field with high-order ones and no carry gives only PF.

---

## 5. \*+ — Multiply and Add — `6'b111001` (57)

### 5.1 Operation paragraph, verbatim

Reference Manual, **printed p.69** (`rm72-072.png`):

> **Multiply and Add (\*+)**
>
> If a binary operation is specified, the multiplicand field in the factor
> register (FT) is multiplied by the addressed storage operand. Neither
> multiplicand nor multiplier may exceed 48 significant numeric bits. The
> product is algebraically added to the accumulator contents as specified by
> the offset. If a decimal operation is specified, this operation has the same
> action as LOAD TRANSIT AND SET, except that the two high-order bits of the
> left zeros counter are set to 10.

CE §6.21.26, **printed p.119** (`ce120-120.png`), word for word the same, plus:

> STRAP Notation: \*+(BU, 48, 8), NAME .0, 64
> Operation Code: 11100

### 5.2 Modifiers

RefMan p.69 and CE p.119, identically:

> *Unsigned; Negative Sign.* These modifiers operate as in ADD.
>
> *Radix.* This modifier operates as in ADD. It also determines whether a
> binary multiplication and addition are performed or whether instead the
> action is like that of a decimal LOAD TRANSIT AND SET.

The sign modifiers apply to the **storage operand** (the multiplier), not to
FT and not to the accumulator — CE p.122, verbatim: "In MULTIPLY AND ADD, the
negative sign modifier as well as the immediate modifier applies to the storage
operand used in the multiplication."

### 5.3 Indicators

RefMan p.69, verbatim:

> *Lost Carry (LC).* In a binary operation, this indicator is set as in ADD.
> Lost carry cannot be turned on if decimal is specified.
>
> *Partial Field (PF).* This indicator is turned on in a binary operation if
> either the multiplicand or the multiplier exceeds 48 significant bits in
> length. In such a case, only the 48 low-order bits of the oversized operands
> are used in the operation. Partial field is also turned on in a binary
> operation if the offset is such that significant bits of the product attempt
> to combine with accumulator positions to the left of the left end of the
> accumulator. Such high-order bits of the product are lost. In a decimal
> operation, partial field is set as in LOAD TRANSIT AND SET.
>
> *Decimal Transit (DTR).* This indicator is turned on if decimal is specified.
>
> *Data Flags (TF, UF, VF); To-Memory Operation (MOP).* These indicators are
> set as in ADD.
>
> *Arithmetic Result (RLZ, RZ, RGZ, RN).* In a binary operation the above
> indicators are set as in ADD. In a decimal operation, they are set as in LOAD
> TRANSIT AND SET.

CE p.119-120 is identical except that its PF sentence reads "attempt to **add
with** accumulator positions" where the RefMan reads "attempt to **combine
with**".

**Two distinct PF causes**, both of which the arm must raise:
1. multiplicand (FT) or multiplier (storage operand) wider than 48 significant
   numeric bits — truncate to the low 48, lose the high bits;
2. the shifted 96-bit product overflowing the 128-bit accumulator at the left,
   i.e. `offSh + 96 > 128`, equivalently `offSh > 32` with a product wide
   enough to reach — the lost bits are discarded.

### 5.4 Programming notes

RefMan p.69, verbatim:

> At the completion of the operation, FT still contains the multiplicand and
> its sign. It is unchanged by the operation. The product that was formed
> during the operation is not available anywhere. To retain both the product
> and the cumulative sum, the instructions MULTIPLY and ADD TO MEMORY can be
> used.
>
> The LOAD FACTOR operation should normally precede MULTIPLY AND ADD. However,
> the loading of FT need not be done in the operation immediately preceding the
> MULTIPLY AND ADD operation.
>
> The offset specified has no effect upon the multiplication. The offset affects
> the addition of the product to the accumulator contents in the same manner
> that it affects ADD.

RefMan printed p.70 (OCR; same text appears in CE p.120, OCR), continuing:

> The arithmetic result indicators are set according to the entire contents of
> the accumulator when the operation is complete, and not according to the
> product.

### 5.5 Registers read and written

- **Reads:** `addrFactor` (14) as an *implied* operand — `st.readFactor()`
  already exists (`bsv/StretchStorage.bsv:868`) and the FP `*+` arm already
  uses it (`bsv/StretchExecute.bsv:2037`); the addressed storage field (or
  immediate operand) as the multiplier; the accumulator (8/9/10) as the addend.
- **Writes:** the accumulator (8, 9) and its sign (10 bit `[59]`), exactly as
  ADD does.
- **Does not write:** FT ("It is unchanged by the operation"), TR, counters —
  in a **binary** operation.  In a decimal operation it writes TR and both
  counters, like LTRS, with the left-zeros counter's two high bits set to `10`.
- **The product is not stored anywhere.**  Only the sum lands.

### 5.6 Relationship to `*` (implemented, `6'b011001`) — the actual data flow

The implemented MULTIPLY arm is at `bsv/StretchExecute.bsv:2647`.  Read against
`*+`, three differences and one shared uncertainty.

| | `*` (implemented) | `*+` (to write) |
|---|---|---|
| multiplicand | **accumulator field at the offset** (`acc.mag >> offSh`) | **FT**, independent of the offset |
| multiplier | addressed storage operand | addressed storage operand |
| product destination | **cleared accumulator at the constant offset 20** | **added** to the accumulator at the instruction's offset |
| offset's role | selects the accumulator operand; does **not** place the result | plays no part in the multiplication; places the product for the add |
| LC | not listed | set as in ADD |
| decimal | LTRS action, LZC high bits `00` | LTRS action, LZC high bits `10` |

The `*` arm's own comment already establishes that **"offset 20 is a constant,
not the instruction's offset"**, cross-checked against DCV's implied offset of
20 on printed p.70-71.  `*+` has no such constant: its product is shifted by
the instruction's own offset and added.

**Why LFT exists at all.**  RefMan p.69, LFT's programming note, verbatim:

> This operation is necessary to load the multiplicand of a subsequent MULTIPLY
> AND ADD. This instruction is not used to load either factor of a MULTIPLY.

That sentence is not an arbitrary restriction — it falls straight out of the
operand plumbing.  `*` takes **both** its factors from places LFT does not
write: one from the accumulator (via the offset) and one from storage.  FT is
not in `*`'s datapath at all, so loading FT before a `*` accomplishes nothing.
`*+` takes one factor from FT and the other from storage, and uses the
accumulator as the **accumulator** rather than as a factor — which is what lets
`LFT; *+; LFT; *+; ...` run a dot product without ever disturbing the running
sum.  RefMan p.56 names the pair in exactly those terms (`rm59x-059.png`):

> A variation on the multiply operation and a related auxiliary function are
> provided by
>     LFT     Load Factor
> and \*+     Multiply and Add.

**The loop, from IBM.**  Reference Manual Figure 8, printed p.27, is the
canonical `LFT`→`*+` accumulate:

```
LOOP    LFT(N), a0 ($X7)        3. Loads element of A in factor register.
        *+(N), b0 ($X8)         4. Multiplies by element of B, adds product
                                   to accumulator.
        V+ICR, $X8, p.0         5. ...
        CBR+, $X7, LOOP         6. ...
        ST(N), c0
```

*Caveat:* this figure's constant is `DD(U), 0E-600`, a floating-point datum, so
Figure 8 is a **floating-point** example.  It is cited here for the data-flow
shape, which is identical in VFL, not as a VFL encoding.  (Figure 8 was read
from OCR, not render-verified.)

**Sequence state.**  Nothing says FT must be loaded immediately before:
"the loading of FT need not be done in the operation immediately preceding the
MULTIPLY AND ADD operation" (p.69).  And CE p.119 adds the only rule about
*what* should be in it: "If a partial field indication is to be avoided, the
loaded factor must be less than 48 significant bits in length."

**Inherited open question.**  The `*` arm's comment already flags that the
signed product's sign "is stated nowhere in the corpus and exercised nowhere in
it", and that its algebraic `acc.sign ^ opnd.sign` is the conventional reading
of "Unsigned; Negative Sign. These modifiers operate as in ADD".  `*+` inherits
that question *and compounds it*: the product's sign then feeds an algebraic
add against the accumulator's sign.  Treat it as open, not settled.

---

## 6. LTRS — Load Transit and Set — `6'b111101` (61)

### 6.1 Operation paragraph, verbatim

Reference Manual, **printed p.67** (`rm70-070.png`):

> **Load Transit and Set (LTRS)**
>
> The transit register (location 15), the left zeros counter, and the all-ones
> counter are cleared. A four-bit sign byte, in which the leftmost bit is set
> to the sign of the addressed storage operand as modified by the negative sign
> modifier, is placed in the four low-order bits of the transit register. The
> remaining three bits of this sign byte are zero. The numeric part of the
> addressed operand is positioned immediately to the left of this sign byte in
> the transit register. The effective offset specified by the instruction is
> placed in the all-ones counter (bits 44-50 of location 7). The two high-order
> bits of the left zeros counter (bits 17-18 of location 7) are set to ones.

continuing on **printed p.68** (`rm71-071.png`):

> At the end of the operation, either the binary-transit or decimal-transit
> indicator is turned on, depending on the value of the radix modifier.

CE §6.21.23, **printed p.116** (`ce117-117.png`) — **more precise about the
bit positions**, and it conditions the sign byte on signedness:

> The transit register (location 15), the left-zeros counter and the all-ones
> counter are cleared to zero. If the operation is signed, the sign bit of the
> storage operand replaces bit 60 of the transit register (TR). Bit positions
> 60-63 of TR form a sign byte, with positions 61-63 remaining cleared. The
> remaining 60 bits of the TR (bits 0-59) are loaded with the numeric portion
> of the storage operand with the low-order bit replacing bit 59 of the TR. The
> effective offset, specified in the instruction, is placed in the all-ones
> counter. The two high-order bits of the left-zeros counter, bits 17 and 18 of
> location 7, are set to ones. At the completion of the operation, the binary
> transit (BTR) or the decimal transit (DTR) indicator is turned on. This is
> determined by the status of the radix modifier specified in the instruction.
>
> STRAP Notation: LTRS (D, 64, 4), NAME .4, 64
> Operation Code: 11110

### 6.2 Modifiers

RefMan p.68 and CE p.116, identically:

> *Unsigned; Negative Sign.* These modifiers operate as in ADD.
>
> *Radix.* This modifier operates as in ADD. In addition, it determines whether
> the binary transit (BTR) or decimal transit (DTR) indicator is turned on.

Note what the radix modifier does **not** do here: LTRS's behaviour is
otherwise identical in both radices.  LTRS is the only one of the five whose
binary form is fully defined and useful.

### 6.3 Indicators

RefMan p.68, verbatim:

> *Partial Field (PF).* Since the low-order four bits of the transit register
> are used as a sign byte, only 60 numeric bits can be loaded into it. This
> indicator is turned on if the numeric part of the field loaded contains more
> than 60 significant bits. If this occurs, the transit register is loaded up
> to its left end. Higher-order bits are lost.
>
> *Binary Transit (BTR); Decimal Transit (DTR).* One of these two indicators is
> turned on at the end of the operation, depending upon the value of the radix
> modifier bit.
>
> *Data Flags (TF, UF, VF); To-Memory Operation (MOP).* These indicators are
> set as in ADD.
>
> *Arithmetic Result (RLZ, RZ, RGZ, RN).* These indicators are set according to
> the contents of the transit register when the operation is complete.

CE p.116 is identical, plus one worked example sentence the RefMan omits:

> For example, this indicator may be turned on by loading a 64-bit unsigned
> number where a one bit is contained in any of the four high-order bit
> positions.

### 6.4 Programming notes

RefMan p.68, verbatim:

> Since the two indicators, binary transit and decimal transit, have lower
> priority than any other indicators capable of causing an interruption, the
> necessary steps to correct any errors detected during LOAD TRANSIT AND SET
> operation will be taken before entering the sequence associated with the BTR
> or DTR indicators.
>
> The primary purpose of this operation is to serve as an entry to an
> interpretive routine, for example, to a routine for an integer arithmetic
> square root operation. The effective offset, which has been placed in the
> all-ones counter, is available to the interpretive routine in the correct bit
> address to be directly transmitted to an index register and used to produce
> the desired effective offset.
>
> The offset field of the instruction may also be used to distinguish between
> one of 128 pseudo-operations. For this purpose it is at the correct bit
> address to be used directly in indexing to a table of half-word BRANCH
> instructions.
>
> The two high-order bits of the left zeros count may be used after an
> interruption caused by the DTR indicator to distinguish this operation from
> decimal MULTIPLY, DIVIDE, or MULTIPLY AND ADD, which may also turn on this
> indicator. These two bits are set as follows by the four operations:
>
>     MULTIPLY                00
>     DIVIDE                  01
>     MULTIPLY AND ADD        10
>     LOAD TRANSIT AND SET    11
>
> These bits are at the correct bit address to be used directly in indexing to
> a table of half-word BRANCH instructions.
>
> Note that, if the interruption mechanism is disabled or the BTR or DTR
> indicators are masked off, the contents of the left-zeros and all-ones
> counters may have been altered since these indicators were turned on.

CE p.117 (`ce118-118.png`) carries the same discriminator table verbatim.

### 6.5 Registers read and written

- **Reads:** the addressed storage field (or immediate operand).
- **Writes:**
  - `addrTransit = 15` (`bsv/StretchTypes.bsv:69`,
    `bsv/StretchStorage.bsv:399  Reg#(Word64) transit`).  Cleared, then:
    IBM 0-59 = numeric part right-justified at IBM 59 (model `[63:4]`),
    IBM 60 = sign (model `[3]`), IBM 61-63 = zero (model `[2:0]`).
  - the **ALL-ONES COUNTER**: `addrAllOnesCount = 7`, IBM bits 44-50
    (`bsv/StretchTypes.bsv:61`; model bits `[19:13]`, register `zocAoc`,
    `bsv/StretchStorage.bsv:377`).  Receives the 7-bit effective offset — the
    instruction's own offset field is also 7 bits (bits 44-50), so it drops in
    unshifted, which is the whole point of "at the correct bit address".
  - the **LEFT-ZEROS COUNTER**: `addrLeftZerosCount = 7`, IBM bits 17-23
    (`bsv/StretchTypes.bsv:60`; model bits `[46:40]`, register `zocLzc`).
    Cleared, then IBM bits 17-18 (the counter's **two high-order bits**) set
    to ones → the whole 7-bit field becomes `7'b1100000`.
- **Does not touch:** accumulator, accumulator sign byte register, FT.
- **Indicator writes:** BTR (bit 39) or DTR (bit 40) — `ind_BTR = 39`,
  `ind_DTR = 40` in `bsv/StretchTypes.bsv:435`.  Both are *permanent*
  indicators (CE printed p.102: the transit indicators "are permanent. If they
  are turned on by any operation, they will remain on until they are turned off
  either by causing an interruption or by being explicitly made zero").

### 6.6 The counter constants for all four operations

The two high-order bits of the left-zeros counter distinguish the four decimal
transit entries.  As a full 7-bit field written into `zocLzc` (the counter is
cleared first in every case):

| operation | LZC[17:18] | full 7-bit `zocLzc` value |
|---|---|---|
| `*`  decimal  | `00` | `7'b0000000` |
| `/`  decimal  | `01` | `7'b0100000` |
| `*+` decimal  | `10` | `7'b1000000` |
| `LTRS` (either radix) | `11` | `7'b1100000` |

---

## 7. CE-ONLY RULES

Rules the **CE manual states and the Reference Manual does not**.  Each was
checked against the RefMan text verified above before being listed here.

1. **LTRS's transit-register bit layout is given explicitly.**  CE printed
   p.116: "the sign bit of the storage operand replaces **bit 60** of the
   transit register (TR). Bit positions **60-63** of TR form a sign byte, with
   positions **61-63** remaining cleared. The remaining 60 bits of the TR
   (**bits 0-59**) are loaded with the numeric portion of the storage operand
   with the low-order bit replacing **bit 59** of the TR."  The RefMan only
   says the numeric part is "positioned immediately to the left of this sign
   byte", which does not by itself fix the right-justification.  **This is the
   implementable statement; use it.**

2. **LFT and LTRS condition the sign byte on a signed operation.**  CE p.118
   LFT: "**For a signed operation**, a 4-bit byte, in which the leftmost bit is
   the sign…".  CE p.116 LTRS: "**If the operation is signed**, the sign bit of
   the storage operand replaces bit 60…".  The RefMan places the sign byte
   unconditionally in both.  See §9 — this is a genuine divergence, not a
   clarification.

3. **The number of flag bits LWF writes depends on the byte size.**  CE printed
   p.123, review point 5: "In such cases the actual number of flag bits set is
   dependent on the specified byte size."  The RefMan's LWF paragraph says only
   "if the addressed storage field includes data flag bits, these bits are
   placed in…", leaving the count to be inferred from the sign-byte table.
   (The *table itself* is in both manuals, so the table is **not** CE-only.)

4. **The `*NI+` STRAP form and the rule behind it.**  CE p.122: the N and I
   modifiers of `*+` belong to the **multiplier** (the storage operand), and
   that is why STRAP writes them *inside* the mnemonic.  The RefMan does not
   discuss `*+`'s STRAP spelling at all.

5. **`*` is executed by the PAU, and that is why 48 and 20 are the numbers.**
   CE printed p.117: "The actual multiplication in this operation is performed
   by PAU. This restricts the operands to 48 significant bits each. Similarly,
   the result appears at offset 20 as this is the normal result field (12-107)
   for a double-precision PAU operation."  The RefMan states 48 and 20 as bare
   facts.  This is CE-only, it corroborates the reasoning already written into
   the implemented `*` arm, and it implies the same 48-bit ceiling on `*+`.

6. **LTRS as an installation-wide pseudo-instruction mechanism.**  CE printed
   p.117: "a binary LTRS with an offset of 200 may be defined, in a particular
   installation, as a cube root pseudo-instruction… once all the desired
   subroutines have been compiled in the determined format, all programs in a
   given installation may utilize them by using LTRS, with proper offsets, as
   pseudo-instructions."  The RefMan mentions "one of 128 pseudo-operations"
   but not the installation-convention framing.  Behaviourally inert, but it is
   what a **binary** LTRS is *for*, which matters when deciding how to test it.

7. **The all-ones counter's content is for loading an index word.**  CE p.117:
   "The effective offset, which has been placed in the all-ones counter, is
   available to the subroutine in the correct bit address to be directly loaded
   into an **index word**."  The RefMan says "transmitted to an index
   register".  Same rule, CE is more specific about the format.

8. **CE's LTRS PF example.**  "this indicator may be turned on by loading a
   64-bit unsigned number where a one bit is contained in any of the four
   high-order bit positions" (p.116) — a directly testable case the RefMan
   does not give.

9. **CE p.119 names the condition for avoiding `*+`'s PF.**  "If a partial
   field indication is to be avoided, the loaded factor must be less than 48
   significant bits in length."  The RefMan states the 48-bit limit but not
   this as advice about FT specifically.

**Checked and REJECTED as CE-only** (both manuals have them):

- "If zero offset is specified, the operation is performed as STORE" (CE p.111)
  — RefMan printed p.64 has "A STORE ROUNDED with zero offset specified is
  equivalent to a STORE."
- "The arithmetic result indicators are set according to the entire contents of
  the accumulator … and not according to the product" — RefMan printed p.70.
- The byte-size → sign-byte-register table — RefMan printed p.36-37.
- The `MULTIPLY 00 / DIVIDE 01 / MULTIPLY AND ADD 10 / LTRS 11` discriminator
  table — both, verbatim identical (RefMan p.68, CE p.117).

---

## 8. REFERENCE-MANUAL-ONLY RULES

Rules only the **Reference Manual** states.  Both are load-bearing.

1. **The all-ones counter's bit range.**  RefMan printed p.67: "The effective
   offset specified by the instruction is placed in the all-ones counter
   (**bits 44-50 of location 7**)."  CE p.116 names the counter but gives no
   bit range for it (it gives one only for the left-zeros counter's bits 17-18).
   `bsv/StretchTypes.bsv:61` already agrees: `addrAllOnesCount = 7; // bits 44-50`.

2. **LFT cannot set lost carry.**  RefMan printed p.69: "The lost-carry
   indicator cannot be turned on by this operation."  CE p.118-119 does not say
   so.  (CE *does* say it for `*+`: "Lost carry cannot be turned on if decimal
   is specified" — a different statement.)

3. **The failure mode for an immediate to-memory operation.**  RefMan printed
   p.56: "the operation is not performed and the operation code invalid (OP)
   indicator is turned on."  CE p.122 only says store-type operations may not
   specify immediate.  This is what tells the SRD arm to call `setOpInvalid`
   rather than, say, program-check.

4. **The interruption-priority note for LTRS.**  RefMan p.68: BTR and DTR "have
   lower priority than any other indicators capable of causing an interruption",
   so error correction happens first.  CE p.117 does not say it.

5. **The masked-off caveat.**  RefMan p.68: "if the interruption mechanism is
   disabled or the BTR or DTR indicators are masked off, the contents of the
   left-zeros and all-ones counters may have been altered since these
   indicators were turned on."  Not in CE.

---

## 9. Divergence between the two manuals — OPEN, do not resolve silently

For **LFT** and **LTRS**, the RefMan places the 4-bit sign byte
unconditionally; the CE conditions it on the operation being signed.

- RefMan p.69 (LFT): "A four-bit sign byte, in which the leftmost bit is the
  sign of the addressed storage operand **as modified by the negative sign
  modifier**, is placed in the four low-order bits of FT."
- CE p.118 (LFT): "**For a signed operation**, a 4-bit byte, in which the
  leftmost bit is the sign… is placed in the four low-order bits of FT."
- RefMan p.67 (LTRS): "A four-bit sign byte, in which the leftmost bit is set
  to the sign of the addressed storage operand as modified by the negative sign
  modifier, is placed…"
- CE p.116 (LTRS): "**If the operation is signed**, the sign bit of the storage
  operand replaces bit 60…"

**Where they differ observably.**  Both clear FT/TR first, so for plain
unsigned data the two readings agree (bit 60 = 0).  The *only* divergent case
is the **negative sign modifier applied to unsigned data** — `LFTN(BU,…)`,
`LTRSN(BU,…)`:

- Under the RefMan, the sign is "assumed positive, before applying the negative
  modifier" (ADD's rule, CE p.122), the modifier inverts it, and FT/TR bit 60
  ends up **1**.
- Under the CE, no sign byte is placed at all for an unsigned operation, and
  bit 60 stays **0**.

RefMan printed p.38's "the four low-order bits of the factor register form a
4-bit sign byte in which the flag bits are zero" does **not** break the tie:
it is a statement about FT's *format*, not about what LFT writes.

**The corpus exercises this nowhere.**  No deck and no MCP listing contains a
VFL `LFT`, `LFTN`, `LTRS` or `LTRSN` (§11).  Mark it as an open item in the arm
and pick one deliberately; do not let it pass as settled.

---

## 10. Model hooks that already exist

### 10.1 Addresses and bit ranges (`bsv/StretchTypes.bsv`)

```
WordAddr addrLeftZerosCount  = 7;   // bits 17-23     (line 60)
WordAddr addrAllOnesCount    = 7;   // bits 44-50     (line 61)
WordAddr addrAccLeft         = 8;
WordAddr addrAccRight        = 9;
WordAddr addrAccSignByte     = 10;  // bits 0-7
WordAddr addrRemainder       = 13;
WordAddr addrFactor          = 14;                    (line 68)
WordAddr addrTransit         = 15;                    (line 69)
```

Word 7's decomposition is in `bsv/StretchStorage.bsv:374-382`, with the
IBM↔model mapping spelled out there:

```
Reg#(Bit#(17)) zocHi   // IBM 0-16   = model [63:47]
Reg#(Bit#(7))  zocLzc  // IBM 17-23  = model [46:40]   LEFT-ZEROS COUNTER
Reg#(Bit#(20)) zocMid  // IBM 24-43  = model [39:20]
Reg#(Bit#(7))  zocAoc  // IBM 44-50  = model [19:13]   ALL-ONES COUNTER
Reg#(Bit#(13)) zocLo   // IBM 51-63  = model [12:0]
```

### 10.2 THE TRAP: you cannot write the counters with `writeWord`

`bsv/StretchStorage.bsv:781-787` deliberately drops the counter fields on a
store to word 7:

```bsv
addrLeftZerosCount: begin
               // The counter fields are deliberately NOT
               // written here -- see the registers' comment.
               zocHi  <= v[63:47];
               zocMid <= v[39:20];
               zocLo  <= v[12:0];
             end
```

The **only** path that writes them is
`st.setConnectiveCounts(Bit#(7) lzc, Bit#(7) aoc)`
(`bsv/StretchStorage.bsv:876`, declared at line 261), with
`st.setLeftZerosCount(Bit#(7))` (line 881) for the LZC alone.  Both take the
**full 7-bit field**, not a mask to OR in — so an LTRS arm passes
`setConnectiveCounts(7'b1100000, zeroExtend(vi.a.offset))`, not two bit-sets.

`setConnectiveCounts` exists because CONNECT TO MEMORY writes through a dynamic
address bsc cannot prove is not word 7; LTRS has exactly the same problem and
the method is already the right shape for it.  Callers of `setLeftZerosCount` today: `bsv/StretchExecute.bsv:1876, 1913, 1953`
(the floating-point divide arms).

### 10.3 FT and TR

`addrFactor` and `addrTransit` are plain 64-bit registers readable and writable
through the ordinary `readWord`/`writeWord` path
(`bsv/StretchStorage.bsv:679-680, 805-806`), plus a dedicated
`st.readFactor()` accessor (line 868).  The FP arms already use both:
`st.writeWord(addrFactor, fpToWord(v))` at `bsv/StretchExecute.bsv:1561`
(FP LFT) and `fpFromWord(st.readFactor())` at line 2037 (FP `*+`).  **No new
storage plumbing is needed for LFT or `*+`.**

### 10.4 The decimal refusal blocks half of this specification

`bsv/StretchExecute.bsv:2249-2253`:

```bsv
Bool radixConv = (vi.code == 6'b000011);
if (vi.m.decimal == 1 && !radixConv)
  ind = setOpInvalid(ind);
```

Every VFL integer code except LCV is refused outright when the radix modifier
is 1.  Consequences:

- **Decimal LTRS, decimal `*+`, and the decimal half of the already-shipped `*`
  are dead text under the current guard.**  All three reduce to the LTRS action,
  which the model does not implement at all.
- **All five operations are implementable in binary**, and binary is all the
  corpus exercises.
- Lifting the guard for LTRS specifically would mean implementing the LTRS
  action once and routing decimal `*`, `/` and `*+` into it with the three
  different LZC constants from §6.6.  That is the natural second step, not the
  first.

### 10.5 VFL integer codes currently implemented

From the `case (vi.code)` at `bsv/StretchExecute.bsv:2364`:
`000101` L, `001101` ST, `000001` +, `100001` +MG, `011001` \*,
`001001` M+, `101011` M+1, `101001` M+MG, `010001` K, `110001` KF,
`000011` LCV.  Everything else falls to the `default` arm at line 3122, which
prints `OP site = vflIntOp/unimplemented-code` and sets Operation Code Invalid.

---

## 11. MCP's actual usage of the five

The requested grep:

```
grep -nE "\bLFT\(|\bLWF\(|\bSRD\(|\*\+|\bLTRS\(" decks/*.strap
```

returns many hits.  **Every one of them is a FLOATING-POINT instruction, not a
VFL integer one.**  The mnemonics `LFT`, `LWF`, `SRD` and `*+` exist in both
the VFL integer set and the floating-point set (pocket card X22-6533 lists both
columns), and the disambiguator is the data-description mode letter.
`strap/strap_asm.py:1449-1451` is decisive:

```python
mode = dds_mods[0].split(',')[0].strip().upper()
if mode in ('N', 'U'):
    return 'FP', base_op, invert, immediate, p_progressive, dds_mods, None
```

`N`/`U` are the floating-point normalize modifiers, so `SRD(U)`, `SRD(N)`,
`LFT(U)`, `LFT(N)`, `LWF(U)`, `*+(U)`, `*+(N)` all assemble as FP.  A VFL
integer form would need mode `B`, `BU`, `D` or `DU`.

```
grep -nE "(LFT|LWF|SRD|LTRS)\s*\((B|D)" decks/*.strap   ->  no hits
grep -nE "\*N?I?\+" decks/*.strap                        ->  only *+(U) / *+(N) / *+A(U) / *+N(U) / *+NA(U), all FP
grep -n  "LTRS" decks/*.strap                            ->  no hits at all
```

Itemised:

| hit | file | disposition |
|---|---|---|
| `SRD(U)` / `SRD(N)` ×~20 | `decks/fp_arith_f210*.strap` | FP STORE ROUNDED (`fpop_SRD = 7'b0101110`), already implemented |
| `LFT(U)` / `LFT(N)` ×~8 | `decks/fp_arith_f215*.strap` | FP LOAD FACTOR (`fpop_LFT = 7'b1001010`), already implemented |
| `*+(U)`, `*+N(U)`, `*+A(U)`, `*+NA(U)`, `*+(N)` ×~30 | `decks/fp_arith_f216*.strap`, `f219d.strap` | FP MULTIPLY AND ADD (`fpop_STAR_PLUS = 7'b0111010`), already implemented |
| **`LWF(U), XBOUND`** | **`decks/mcp_bootstrap_p33.strap:129`** (MCP printed p.33, listing line 51, "GET MCP BOUNDS") | **FP** LOAD WITH FLAG (`fpop_LWF = 7'b0100110`): mode `U` → FP by the rule above.  This is the one hit in an MCP deck. |
| `LTRS` | — | **none anywhere** |

In MCP's own printed listing (`docs/ocr/MCP_Mar63_001-249.txt` lines 6685,
6821, 7395, 7515) the only occurrences are `LFT(U),STLR+1.0` and
`LFT(U),SLRPP+1.0` style, commented "-RESTORE $MR" — again mode `U`, i.e.
floating-point LFT used to restore a saved register.  The two apparent `*+`
hits in `docs/ocr/MCP_Mar63_250-445.txt` (lines 2002, 3262) are OCR noise in
column/flag markers, not instructions.

> **Conclusion: MCP uses none of the five VFL integer operations.  None of the
> five is needed for MCP.  `LTRS` appears nowhere in the corpus at all.**

---

## 12. Ranking by implementation difficulty

Ordered easiest first.  The discriminator that actually matters is whether the
arm needs a **storage write path** (hard: field insertion, word crossing,
protection, refill) or only register writes (easy).

**1. LWF (`6'b100101`) — easiest.**  It is the already-converted L arm
(`6'b000101`, the one arm using the prefetch/bail-out staging) with three more
bits written into word 10.  No new storage method, no new arithmetic, no new
indicator.  The only real work is deriving T/U/V from the operand's sign byte
at the right byte size — and the model already extracts data flag bits to set
TF/UF/VF.  Half a day.

**2. LFT (`6'b001011`).**  Also a load, but into FT instead of the accumulator,
and simpler than LWF in one way: no accumulator traffic at all, the offset is
ignored, and `st.writeWord(addrFactor, …)` is a path the FP LFT arm already
uses.  The only new logic is the PF-at-60-bits rule and "load up to the left
end, higher-order bits are lost".  Second **by code volume** — but the §9
signed/unsigned divergence has to be decided before the arm is written, and
that decision is a judgement call, not a transcription.  If you want to defer
that judgement, do `*+` (3) first and come back.

**3. `*+` (`6'b111001`).**  Substantial but entirely parallel to the shipped
`*` arm: same prefetch/bail-out shape, same 48-bit truncation and PF rule, same
96-bit product.  The new parts are (a) read FT instead of the accumulator for
the multiplicand, (b) shift the product by the instruction's offset instead of
the constant 20, (c) **add** to the accumulator with `smAdd` instead of
replacing it, (d) a second PF cause (product overflowing the accumulator's left
end), (e) LC "as in ADD".  All five are mechanical given the `+` and `*` arms
side by side.  Inherits `*`'s unresolved signed-product question.

**4. LTRS (`6'b111101`).**  Looks exotic, is not: `setConnectiveCounts` already
exists and is exactly the right shape, FT/TR are plain registers, and the
numeric load into TR is LFT's load with a different destination.  New: setting
BTR/DTR (`ind_BTR = 39`, `ind_DTR = 40`), which are *permanent* indicators —
they must not be cleared by a later instruction the way the arithmetic-result
indicators are.  The real cost is not the arm, it is that **binary LTRS's only
observable purpose is to raise BTR and park state for an interrupt handler**,
so testing it means exercising the interrupt path, and the decimal half (which
is what `*`, `/` and `*+` share with it) is unreachable behind the decimal
refusal.  Nothing in the corpus uses it.

**5. SRD (`6'b101101`) — hardest.**  It is the only one of the five that writes
storage, so it inherits all of the ST arm's machinery: field insertion,
word-crossing with two reads and two writes, per-word protection checks, the
refill interaction, and the `immediate → setOpInvalid` refusal.  On top of that
it adds a rounding add with its own carry-out detection for LC, and the LC/PF
distinction in §4.6 is a genuine modelling judgement rather than a transcription.
The honest estimate is "the ST arm again, plus a new indicator whose exact
trigger the manual states in one sentence".

**None of the five is needed for MCP** (§11).  If the goal is corpus coverage
rather than MCP, SRD and LFT are the two with existing *floating-point* twins
already exercised by the `fp_arith_f210*` and `fp_arith_f215*` decks, which
means a VFL counterpart deck would be straightforward to write by analogy —
and that, not MCP, is the argument for doing them.

---

## 13. Open items, collected

1. **§9**: LFT/LTRS sign byte on unsigned data with the negative modifier —
   RefMan and CE disagree; corpus is silent; pick deliberately.
2. **§5.6**: the signed product's sign in `*` is already flagged unverified in
   the shipped arm; `*+` inherits it and then feeds it to an algebraic add.
3. **§4.6**: SRD's LC is "a carry propagated beyond the left end of the field
   stored".  Whether "field" there means the full storage field or its numeric
   part (excluding the sign byte) is not stated.  Both manuals use the same
   wording; **the manuals are silent on this distinction.**
4. **§10.4**: decimal LTRS, decimal `*+` and decimal `*` are all the same
   unimplemented LTRS action behind the same refusal.  Implementing LTRS once
   unlocks all three; doing them separately would duplicate it three times.
5. **§3.3**: the byte-size → number-of-flag-bits breakdown for LWF is derived
   from the p.100 sign-byte table.  CE p.123 states only that the count
   "is dependent on the specified byte size"; **neither manual enumerates the
   cases.**
6. The manuals are silent on what `*+` does when FT has never been loaded —
   p.69 only says LFT "should normally precede" it.  FT simply holds whatever
   was last written to word 14, by LFT or by an explicit store.
