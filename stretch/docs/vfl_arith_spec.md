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

## What is still missing

Nothing in the sourcing. What remains is the implementation, and a
deck built from Problem 2.12 to check it.
