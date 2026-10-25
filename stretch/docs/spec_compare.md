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

> **Re-verified by the committing session: nothing yet.** The claim
> most worth checking first is that MCP uses none of `KE`/`KR`/`KFE`/
> `KFR` -- the `KR(` hits in `decks/` are floating-point sharing the
> mnemonic. That negative result is what took this whole family off
> the critical path, so it should be the first thing confirmed.

---

# VFL compare family: KE, KR, KFE, KFR — implementation spec

Written 2026-10-25 for `bsv/StretchExecute.bsv`. Nothing here was taken
from OCR text. Every quotation below was read off a rendered page with
the Read tool; the renders are listed in §0.

---

## 0. Pages rendered and read (the evidence base)

All renders went to this scratchpad at 200 dpi unless noted.

| File | PDF page | Printed page | What it carries |
|---|---|---|---|
| `docs/22-6530-2_7030RefMan.pdf` | 62 | **59** | MOP / data-flag definitions; the twenty-integer-operation classification table (`K KF KE KFE KR KFR` = "Indicators only / Add") |
| `docs/22-6530-2_7030RefMan.pdf` | 68 | **65** | COMPARE (K), COMPARE FIELD (KF), COMPARE IF EQUAL (KE) |
| `docs/22-6530-2_7030RefMan.pdf` | 69 | **66** | KE indicators + note, COMPARE FIELD IF EQUAL (KFE), COMPARE FOR RANGE (KR) |
| `docs/22-6530-2_7030RefMan.pdf` | 69 | **66** | re-rendered at **600 dpi** and cropped (`kr_crop.png`) to settle the KR gate sentence — see §6 |
| `docs/22-6530-2_7030RefMan.pdf` | 70 | **67** | Figure 16, Figures 17/18, COMPARE FIELD FOR RANGE (KFR) |
| `docs/22-6530-2_7030RefMan.pdf` | 94 | **91** | floating-point COMPARE FOR RANGE — the decisive cross-check |
| `docs/R23-9694_..._Vol2_1961.pdf` | 114 | **113** | CE 6.21.19 Compare if Equal |
| `docs/R23-9694_..._Vol2_1961.pdf` | 115 | **114** | CE 6.21.20 Compare Field if Equal |
| `docs/R23-9694_..._Vol2_1961.pdf` | 116 | **115** | CE 6.21.21 Compare for Range, 6.21.22 Compare Field for Range |
| `docs/R23-9694_..._Vol2_1961.pdf` | 117 | **116** | CE 6.21.22 indicators + note |
| `docs/X22-6533_7030_PocketCard.pdf` | 2 | — | INTEGER ARITHMETIC opcode table + modifier-bit legend |
| `docs/X22-6533_7030_PocketCard.pdf` | 4 | — | at **300 dpi**: the STRAP-mnemonic column, for the `(I, N, NI)` suffix sets |

Page-offset confirmations seen in the ink: RefMan PDF 68 carries the
running foot "Variable Field Length 65", PDF 69 carries "66 IBM 7030",
PDF 70 carries "Variable Field Length 67" (printed = PDF − 3). CE PDF
114/115/116/117 carry centred folios 113/114/115/116 (printed = PDF − 1).

---

## 1. Opcodes, every source that prints one

Ink-verified in all three columns.

| op | CE "Operation Code" (5 bits) | Pocket card | six-bit `vi.code` | decimal |
|---|---|---|---|---|
| K   | `01000` (CE p.111) | `abc010001` | `6'b010001` | 17 |
| KF  | `11000` (CE p.112) | `abc110001` | `6'b110001` | 49 |
| **KE**  | `01001` (CE p.113) | `abc010011` | `6'b010011` | **19** |
| **KFE** | `11001` (CE p.114) | `abc110011` | `6'b110011` | **51** |
| **KR**  | `01010` (CE p.115) | `abc010101` | `6'b010101` | **21** |
| **KFR** | `11010` (CE p.115) | `abc110101` | `6'b110101` | **53** |

The CE five-bit code is the six-bit code with the trailing `1` dropped,
exactly as predicted. All six agree.

Pocket card modifier legend, read off the same page, verbatim:

> `a = 0, data signed` `c = 0, binary operation` `b = 1, invert sign`
> `b = 0, same sign` `a = 1, data unsigned` `c = 1, decimal operation`

i.e. `abc` are the Unsigned / Negative-Sign / Radix modifier bits that
`vi.m.unsign`, `vi.m.invert` and the byte-size/radix handling already
carry for K and KF. **No new modifier decoding is needed.**

Bit structure worth exploiting in the arm: bit 5 of `vi.code` selects
the FIELD variant, and `vi.code[2:1]` selects the gate — `2'b00` = plain,
`2'b01` = if-equal, `2'b10` = for-range.

---

## 2. COMPARE IF EQUAL (KE) — opcode `6'b010011`

### 2.1 Operation paragraph, verbatim

Reference Manual, **printed p.65** (PDF 68), right column:

> **Compare if Equal (KE)**
>
> If the accumulator-equal indicator is off when this operation is
> interpreted, the comparison is not performed and the comparison
> result indicators are not changed. Otherwise, the operation is
> executed exactly as is COMPARE.

CE manual **printed p.113**, §6.21.19, verbatim:

> If the accumulator equal indicator is off when this operation is
> interpreted, the comparison is not performed and the comparison
> result indicators are not changed. Otherwise, the operation is
> executed exactly as in COMPARE.

(The two differ only in "as is" / "as in". They agree.)

### 2.2 Modifiers

RefMan p.65 and CE p.113, both verbatim:

> Unsigned; Negative Sign; Radix. These modifiers operate as in ADD.

Identical to K. Nothing new.

### 2.3 Indicators

RefMan **printed p.66** (PDF 69), left column, verbatim:

> **INDICATORS**
>
> *Data Flags (TF, UF, VF); To-Memory Operation (MOP).* These
> indicators are set as in COMPARE.
>
> *Comparison Result (AL, AE, AH).* These indicators are set as in
> COMPARE if the accumulator-equal indicator is on when the operation
> is initiated. If the accumulator-equal indicator is off, these
> indicators are not affected by the operation.

CE p.113 is word-for-word the same, with "memory" for "storage" in the
programming note.

Note the deliberate split: the data flags and MOP are stated flatly;
only AL/AE/AH are made conditional. See §6 for what that buys.

### 2.4 Programming note (RefMan p.66, CE p.113) — verbatim

> COMPARE IF EQUAL can be used with COMPARE to obtain a comparison of
> fields of more than 64 bits. A COMPARE operation is used to compare
> the high-order part of both fields. This is followed by one or more
> COMPARE IF EQUAL operations comparing the succeeding lower-order
> parts of the field. At the completion of the series of comparisons,
> the indicators will describe the relation of the entire accumulator
> field to the entire storage field. The same technique may also be
> used to compare fields that are split into several parts.

The worked pair (RefMan Figure 15, p.66; CE p.113–114) is:

```
        L  (DU, 60, 6), M, 0
        K  (DU, 60, 6), N, 0
        L  (DU, 30, 6), M+.60, 0
        KE (DU, 30, 6), N+.60, 0
```

CE p.114 adds the sentence the Reference Manual does not print:

> Notice, however, that the LOAD following the first comparison is
> executed regardless of the status of the comparison result indicators.

That is a statement about the *program*, not the machine: only the KE
is gated, the intervening LOAD always runs. Useful when writing the deck.

### 2.5 What it does — unambiguous

* **Accumulator: not changed.** Printed p.59 classifies KE under
  `RESULT ALTERS = Indicators only`, `ARITHMETIC ACTION = Add`.
  Neither operand is changed (inherited from COMPARE, p.65).
* **Gate:** AE at the start of the instruction.
* **AE on** → behave exactly as K: `AL = (acc < opnd)`, `AE = (acc == opnd)`,
  `AH = (acc > opnd)`, **all three written** (the ungated case *is*
  COMPARE, and COMPARE "always causes one and only one indicator to be
  turned on" — p.67).
* **AE off** → AL, AE and AH are all left exactly as they were.
* Arithmetic result indicators (RLZ/RZ/RGZ/RN), lost carry and partial
  field: never touched — p.65, "Neither the lost carry nor the partial
  field indicator can be turned on by a comparison operation."

---

## 3. COMPARE FIELD IF EQUAL (KFE) — opcode `6'b110011`

### 3.1 Operation paragraph, verbatim

Reference Manual, **printed p.66** (PDF 69), left column:

> **Compare Field if Equal (KFE)**
>
> If the accumulator-equal indicator is off when this operation is
> interpreted, the comparison is not performed and the comparison
> result indicators are not changed. Otherwise, the operation is
> executed exactly as is COMPARE FIELD.

CE **printed p.114**, §6.21.20, is identical word for word.

### 3.2 Modifiers

RefMan p.66, CE p.114: "Unsigned; Negative Sign; Radix. These modifiers
operate as in ADD." Same as KF.

### 3.3 Indicators

RefMan p.66, right column, verbatim:

> *Data Flags (TF, UF, VF); To-Memory Operation (MOP); Comparison
> Result (AL, AE, AH).* These indicators are set as in COMPARE IF EQUAL.

CE p.114 is identical.

### 3.4 Programming note (RefMan p.66, CE p.114) — verbatim

> COMPARE FIELD IF EQUAL can be used with COMPARE FIELD to obtain
> comparison of fields of more than 64 bits in the same way that
> COMPARE IF EQUAL is used with COMPARE.

### 3.5 What it does

Exactly KE's gate wrapped around KF's comparison. So, in addition to
§2.5:

* The accumulator side is the **bounded field**, length = storage field
  length **exclusive of the sign byte**, positioned by the offset.
* **The accumulator's real sign is not used; a positive sign is assumed**
  (p.65, COMPARE FIELD).
* No indication is given of a one-bit in the accumulator to the left of
  the field (p.65/p.66 programming note, quoted in full inside the
  existing arm).
* Accumulator unchanged (p.59: "Indicators only / Add").

---

## 4. COMPARE FOR RANGE (KR) — opcode `6'b010101`

### 4.1 Operation paragraph, verbatim

Reference Manual, **printed p.66** (PDF 69), right column. This is
transcribed from a 600 dpi crop (`kr_crop.png`); the word "performed" is
unambiguous in the ink and there is **no "not" before it**:

> **Compare for Range (KR)**
>
> If the accumulator-high indicator is off when this operation is
> interpreted, the comparison is performed and the comparison result
> indicators are not changed. Otherwise, the operation is identical to
> COMPARE except for the setting of the comparison result indicators.
> If the accumulator operand is equal to or higher than the storage
> operand, the accumulator-high indicator is left on. If the
> accumulator operand is less than the storage operand, the AE
> indicator is turned on, and AH is turned off.

CE manual, **printed p.115**, §6.21.21, verbatim — note the divergence
in the first sentence and in "turned on" vs "left on":

> If the accumulator high indicator is off when this operation is
> interpreted, the comparison is not performed and the comparison
> result indicators are not changed. Otherwise, the operation is
> identical to COMPARE with the exception of the setting of the
> comparison result indicators. If the accumulator operand is equal to
> or higher than the storage operand, the accumulator high indicator is
> turned on. If the accumulator operand is less than the storage
> operand, the accumulator equal indicator is turned on.

See §6 for the resolution of "is performed" vs "is not performed", and
§8 for why the "left on"/"turned on" difference is behaviourally empty.

### 4.2 Modifiers

RefMan p.66, CE p.115: "Unsigned; Negative Sign; Radix. These modifiers
operate as in ADD."

### 4.3 Indicators

RefMan **printed p.66**, right column, verbatim:

> *Data Flags (TF, UF, VF); To-Memory Operation (MOP).* Set as in COMPARE.
>
> *Accumulator Equal (AE).* Set if accumulator operand is algebraically
> less than storage operand.
>
> *Accumulator High (AH).* Remains on if accumulator operand is
> algebraically equal to or greater than storage operand. Set to zero
> when accumulator operand is algebraically less than storage operand.

**AL does not appear in the Reference Manual's list at all.** The CE
manual supplies it — see §7.

CE **printed p.115**, verbatim:

> *Accumulator Low (AL):* This indicator cannot be affected by this operation.
>
> *Accumulator Equal (AE):* This indicator is turned on if the
> accumulator operand is algebraically less than the memory operand.
>
> *Accumulator High (AH):* This indicator is turned on if the
> accumulator operand is algebraically equal to or greater than the
> storage operand.

### 4.4 Programming note (RefMan p.66–67) — verbatim

> COMPARE FOR RANGE can be used with COMPARE to determine whether a
> quantity falls within a given range. The range is defined by two
> bounds stored in storage and includes all values equal to or greater
> than the lower bound but less than the upper bound. The field to be
> tested is placed in the accumulator. A COMPARE is then performed,
> addressing the lower range bound, followed by a COMPARE FOR RANGE,
> addressing the upper bound. If AE indicator is on at completion, the
> tested field is within range. If AL indicator is on, the field is
> below range; if AH is on the field is above range (Figure 16).
>
> If a COMPARE FOR RANGE is executed with one or more AL, AE, or AH
> indicators on, more than one of these may be left on after execution
> of the COMPARE FOR RANGE. The COMPARE always causes one and only one
> indicator to be turned on. Therefore, if a COMPARE FOR RANGE follows
> a COMPARE, the above case never exists and indicators are set as
> described.

Figure 16 (p.67) draws it: below the lower bound → AL, between the
bounds → AE, at or above the upper bound → AH.

Figure 17 (p.67) is the worked example and is the natural first deck:

```
        L   (D, 44, 4), 1492.0, 0
        KI  (D, 20, 4), TEN3, 0
        KR  (D, 40, 4), TEN8, 0
        BZAE, OUT
        ST  (D, 40, 4), 1500.0, 0
OUT     ...
TEN3    DDI (D, 20, 4), 1000
TEN8    DD  (D, 40, 4), 100000001
```

### 4.5 Truth table for the K-then-KR idiom (derived, all four cases)

| accumulator vs bounds | after K (lower bound) | KR gate | after KR |
|---|---|---|---|
| acc < lower | AL on, AE off, AH off | AH off → gated | AL on → below range |
| acc = lower | AE on, AL off, AH off | AH off → gated | AE on → in range (lower bound included) |
| lower < acc < upper | AH on | AH on → runs; acc < upper | AE turned **on**, AH turned **off** → in range |
| acc ≥ upper | AH on | AH on → runs; acc ≥ upper | AH **left on**, AE untouched → above range |

Row 3 is why **AH must be cleared on the low branch**. If AH were left
on, rows 3 and 4 would both end with AH on and the idiom would not
distinguish "in range" from "above range" by AH at all.

(p.67's "more than one of these may be left on" does *not* by itself
prove the AH clear — it is satisfiable either way, e.g. AL+AE after a
low branch. The proof is the explicit sentence in §4.3: "*Accumulator
High (AH).* ... **Set to zero** when accumulator operand is algebraically
less than storage operand.")

### 4.6 What it does

* **Accumulator: not changed** (p.59, "Indicators only / Add").
* **Gate:** AH at the start of the instruction.
* **AH off** → AL, AE, AH all unchanged. (See §6 on whether the fetch
  still happens.)
* **AH on, acc ≥ storage** → AH stays on; **AE and AL are not written.**
* **AH on, acc < storage** → **AE := 1 and AH := 0**; AL is not written.
* **AL is never written by KR, in either branch.**
* The comparison itself (sign-magnitude, algebraic, −0 == +0, zero-extend
  on the left) is identical to K: p.66, "the operation is identical to
  COMPARE except for the setting of the comparison result indicators."

**AE is SET-ONLY, not set-or-cleared** — this is a deliberate reading and
§8 records it as the one genuinely open point. The manual's phrasing is
asymmetric on the page rendered: for AH it spells out both branches
("Remains on if ... **Set to zero** when ..."), for AE it gives only one
("**Set** if accumulator operand is algebraically less than storage
operand"). CE p.115 is one-sided in the same way ("turned on if"), and so
is the floating-point KR on p.91 ("**set to one** if the accumulator
operand is low"). When this manual means "and cleared otherwise", it says
so. So KR does not clear AE on the high branch.

---

## 5. COMPARE FIELD FOR RANGE (KFR) — opcode `6'b110101`

### 5.1 Operation paragraph, verbatim

Reference Manual, **printed p.67** (PDF 70), left column continuing into
the right column:

> **Compare Field for Range (KFR)**
>
> If the accumulator-high indicator is off when this operation is
> interpreted, the comparison is not performed and the comparison result
> indicators are not changed. Otherwise, the operation is identical to
> COMPARE FIELD with the exception of the setting of the comparison
> result indicators. If the accumulator operand is equal to or higher
> than the storage operand, the AH indicator is turned on. If the
> accumulator operand is less than the storage operand, the AE indicator
> is turned on.

CE **printed p.115**, §6.21.22, is word-for-word the same.

Note: here the Reference Manual *does* print "is not performed", unlike
its own KR paragraph on the facing page. §6 covers this.

### 5.2 Modifiers

RefMan p.67, CE p.115: "Unsigned; Negative Sign; Radix. These modifiers
operate as in ADD."

### 5.3 Indicators

RefMan **printed p.67**, right column, verbatim:

> *Data Flags (TF, UF, VF); To-Memory Operation (MOP); Comparison Result
> (AL, AE, AH).* These indicators are set as in COMPARE FOR RANGE.

CE **printed p.116** is word-for-word the same.

So KFR inherits KR's full indicator rule — including "AH set to zero when
the accumulator operand is algebraically less" (which KFR's own body text
omits) and "AL cannot be affected".

### 5.4 Programming note (RefMan p.67, CE p.116) — verbatim

> COMPARE FIELD FOR RANGE can be used with COMPARE FIELD to determine
> whether a quantity falls within a given range in the same manner that
> COMPARE FOR RANGE is used with COMPARE.

### 5.5 What it does

KR's gate and KR's indicator rule (§4.6 in full, AE set-only included),
wrapped around KF's field comparison: bounded accumulator field,
assumed-positive accumulator sign, no indication of high-order
accumulator one-bits. Accumulator unchanged (p.59, "Indicators only /
Add").

---

## 6. The "is performed" / "is not performed" divergence — NOT an erratum

RefMan p.66 says the gate-off KR performs the comparison and suppresses
only the indicator write. CE p.115 says it does not perform the
comparison. It is tempting to call the Reference Manual's sentence a
dropped "not". **It is not.** The same construction appears in a
different chapter of the same manual, for the floating-point KR, on
**printed p.91** (PDF 94), read off the ink:

> **Compare for Range (KR)**
>
> When the indicator accumulator high (AH) is on, a comparison will be
> performed between the operand in the left half of the accumulator and
> the operand specified by the effective address. **If the indicator
> accumulator high (AH) is off, the comparison is performed but the
> comparison indicators are not changed.**

and p.91 then states what that buys, verbatim:

> *Data Flags (TF, UF, VF).* These indicators are set according to the
> flag bits of the addressed operand **whether or not the comparison is
> performed**.
>
> *To-Memory Operation (MOP).* This indicator is set to zero **whether
> or not the comparison is performed**.

Two chapters, same wording, and a spelled-out consequence. The reading
is self-consistent: on a gate-off compare the operand **is still
fetched** and only the AL/AE/AH write is suppressed. The Reference
Manual's VFL KE/KFE/KFR paragraphs say "is not performed" as shorthand
for the same thing, which is why their INDICATORS sections still list
the data flags and MOP *unconditionally* and make only the comparison
result indicators conditional (§2.3).

**The only observable difference** between the two readings is whether
TF/UF/VF and MOP are affected when the gate is off.

**In this model the difference is currently unobservable**, and that is
worth stating so nobody relitigates it:

* VFL data flags are not implemented at all. `grep ind_TF bsv/` has one
  hit, `StretchExecute.bsv:1482`, inside the floating-point arm.
* The existing `K`/`KF` arm never writes MOP either — contrast the
  floating-point compare at `StretchExecute.bsv:1813`, which does
  `ind = setBit(ind, ind_MOP, 0)`. (RefMan printed p.59 is clear that it
  should be off: MOP "is turned on by all integer arithmetic operations
  in which the result is placed in the addressed storage location. All
  other integer arithmetic operations turn this indicator off." That is
  a pre-existing gap in the K arm, not something these four introduce.)

**Recommendation, and it matters for progressive indexing:** write the
arms so the operand fetch is performed unconditionally and only the
indicator write is gated. That is the p.91-consistent reading, it keeps
`vflReadsUsed` and the shared progressive-index/refill completion block
at `StretchExecute.bsv:3156` behaving exactly as they do for K and KF,
and it means a gated-off KE does not silently skip a progressive-index
advance or a data-fetch monitor. The manuals are silent on what a
gate-off VFL compare does to a progressive index; this choice is the one
that needs no new rule.

---

## 7. CE-ONLY RULES

This section is short, and the shortness is the finding. I checked each
candidate against the rendered Reference Manual page before listing it;
two rules that look CE-only in the OCR are in fact printed in both.

**Genuinely CE-only:**

1. **KR's effect on AL is stated.** CE printed p.115, verbatim:
   "*Accumulator Low (AL):* This indicator cannot be affected by this
   operation." The Reference Manual's KR INDICATORS section (p.66) simply
   **omits AL**, leaving it to inference. This is the one substantive
   CE-only rule in the family, and it confirms the inference. By
   KFR's "set as in COMPARE FOR RANGE" (p.67 / CE p.116) it carries to
   KFR as well.
2. **The five-bit printed operation codes** (§1) — the Reference Manual's
   operation paragraphs do not print opcodes at all; only the pocket card
   and the CE manual do. The two agree.
3. (Programming colour, not a machine rule.) CE p.114: "Notice, however,
   that the LOAD following the first comparison is executed regardless of
   the status of the comparison result indicators."

**Checked and NOT CE-only** — these are printed in the Reference Manual
too, at printed p.65, and I read them there:

* "The comparison is performed by making a subtraction and testing the
  result. A decimal digit with byte size less than four is handled as in
  any other subtraction." (RefMan p.65 programming note 4.)
* "Neither the lost carry nor the partial field indicator can be turned
  on by a comparison operation." (RefMan p.65.)
* The zero-extension rule, the ±0 collation rule, and "The arithmetic
  result indicators are not changed by a comparison operation."

**Where the CE manual is WEAKER than the Reference Manual** (worth
flagging because it is the opposite of the usual direction):

* CE p.115's KR body text says only "the accumulator equal indicator is
  turned on" on the low branch. It never says AH is turned off. The
  Reference Manual says it **twice** — in the body ("and AH is turned
  off") and in the indicator list ("Set to zero when accumulator operand
  is algebraically less than storage operand"). Follow the Reference
  Manual here; §4.5 shows the idiom only works that way.

---

## 8. Open points, stated rather than guessed

* **Does KR/KFR clear AE on the high branch?** §4.6 says no (set-only),
  on the strength of the manual's asymmetric phrasing — AH gets both
  branches spelled out, AE gets only "Set if ... less". Nothing read here
  states the high branch's effect on AE either way, so this is a reading,
  not a quotation. It **is** observable: enter with AE *and* AH both on,
  then KR with acc ≥ storage. Set-only leaves AE on; set-or-clear turns
  it off. §9.6 lists the three-instruction deck that would settle it.
  Note that the existing floating-point arm makes the *opposite* choice
  (`StretchExecute.bsv:1813`, `setBit(ind, ind_AE, pack(cmp < 0))`), and
  that choice is unproven — `jb_af1c` F202G never enters a high-branch KR
  with AE already on. Do not "fix" the VFL arm by copying it; that is the
  §9.3 trap displaced by one indicator.
* **"interpreted" vs "initiated".** The Reference Manual gates on the
  indicator "when this operation is **interpreted**" (body text) but
  describes the indicator write as conditional on the state "when the
  operation is **initiated**" (KE's INDICATORS section, p.66). It never
  defines the difference. On the real machine the I-unit runs ahead of
  the E-unit, so they could in principle differ. In this model they
  coincide — the gate is read from the live `ind` word at execute time,
  exactly as the floating-point KR arm already does
  (`StretchExecute.bsv:1822`, `ind[63 - ind_AH]`). Noting it rather than
  silently picking one.
* **"left on" vs "turned on" for KR's high branch.** RefMan says the AH
  indicator "is left on"; CE says it "is turned on". Behaviourally
  identical: AH is the gate, so it is necessarily already on whenever
  that branch is reached. Either implementation (write 1, or write
  nothing) gives the same state.
* **KFR's body text omits "AH is turned off"** where KR's includes it.
  KFR's INDICATORS section says "set as in COMPARE FOR RANGE", which
  pulls in KR's explicit "Set to zero when accumulator operand is
  algebraically less". Implement KFR's low branch the same as KR's.
* **Progressive indexing on a gated-off compare**: the manuals are
  silent. §6 recommends performing the fetch and the index completion
  unconditionally, which makes the question moot.
* **VFL data flags (TF/UF/VF) and MOP**: not modelled for VFL at all
  today. These four operations do not change that; see §6.

---

## 9. What must change in `bsv/StretchExecute.bsv`

### 9.1 Where things stand

* `StretchExecute.bsv:2918` — the arm `6'b010001, 6'b110001:` implements
  K and KF. It reads the operand (immediate, in-word, or word-crossing),
  builds `SM128 opnd = fieldToSM(...)`, builds the accumulator side two
  different ways depending on `fieldCmp`, calls `smCompare`, and ends with
  `ind = setAccCmpIndicatorsF(ind, c);` at line 3038.
* `6'b010011`, `6'b110011`, `6'b010101`, `6'b110101` currently fall to the
  VFL `default:` at line 3122, which prints
  `OP site = vflIntOp/unimplemented-code`, calls `setOpInvalid(ind)` and
  sets `vflOk = False`.

### 9.2 The headline: two of the four are trivial, two are not

**KE and KFE are a small variation on the existing arm.** The
comparison, the operand fetch, the field/offset handling and the
indicator write are all *identical* to K and KF. The only change is a
gate around the final `setAccCmpIndicatorsF` call. Add
`6'b010011, 6'b110011` to the existing case label, derive `fieldCmp` from
bit 5 rather than from the whole code — `Bool fieldCmp = (vi.code[5] == 1);`
replaces `Bool fieldCmp = (vi.code == 6'b110001);` — and gate the write
on `ind[63 - ind_AE]`. `setAccCmpIndicatorsF` is exactly right for
KE/KFE, because the ungated case *is* COMPARE and writes all three bits.

**KR and KFR are a different operation at the indicator write, and
`setAccCmpIndicatorsF` is WRONG for them.** That helper
(`StretchExecute.bsv:919`) unconditionally writes all three of AL, AE
and AH. KR/KFR must write AE and AH only, and only on the low branch.
They need a bespoke write:

```bsv
// KR/KFR, Ref. Manual printed p.66 (KR) and p.67 (KFR, "set as in
// COMPARE FOR RANGE").  AH is the input GATE, not a result.
//   low branch : AE := 1, AH := 0   ("the AE indicator is turned on,
//                                     and AH is turned off", p.66)
//   high branch: nothing is written (AH is already on; AE is SET-ONLY,
//                                    see spec_compare.md section 8)
// AL is never written -- CE manual printed p.115: "Accumulator Low
// (AL): This indicator cannot be affected by this operation."
if (ind[63 - ind_AH] == 1 && c == CmpLow) begin
  ind = setBit(ind, ind_AE, 1);
  ind = setBit(ind, ind_AH, 0);
end
```

### 9.3 DO NOT copy the floating-point KR arm

`StretchExecute.bsv:1810` (`fpop_K, fpop_KMG, fpop_KR, fpop_KMGR`) looks
like a ready-made template and is **wrong by one line for VFL**. Its
comment says, correctly for floating point:

> "when the gate AH is on, set AE to 'accumulator low' (acc < operand).
> AL and AH are NOT changed"

and the code writes only AE. That is right for the floating-point KR,
because printed **p.91 omits AH from the KR indicator list entirely**
(§6 quotes the whole list: Data Flags, MOP, AL, AE, PSH — no AH), and it
was verified against `decks/fp_compare_f202g.strap` / `jb_af1c` F202G11-18.

The **VFL** KR is specified differently on printed p.66, twice over:
"the AE indicator is turned on, **and AH is turned off**", and
"*Accumulator High (AH).* ... **Set to zero** when accumulator operand is
algebraically less than storage operand." §4.5 shows why the K-then-KR
idiom requires it. So the VFL arm must clear AH where the FP arm does
not. This is the single most likely bug in a naive port and it is
invisible to any test that only checks AE.

The FP arm also writes AE unconditionally within the gate
(`pack(cmp < 0)`), which clears AE on the high branch; §4.6 and §8 argue
the VFL op does not. Second reason not to copy it.

(Whether the real 7030's floating-point KR also clears AH, or preserves
AE, is not settled by any source read here; p.91 is simply silent and the
jb_af1c sub-tests never probe either. Out of scope — do not change the FP
arm.)

### 9.4 Suggested shape

```bsv
6'b010001, 6'b110001,   // K,  KF
6'b010011, 6'b110011,   // KE, KFE
6'b010101, 6'b110101:   // KR, KFR
begin
  Bool fieldCmp = (vi.code[5] == 1);          // bit 5 = FIELD variant
  Bit#(2) gate  = vi.code[2:1];               // 00 plain, 01 if-equal, 10 for-range
  ... existing fetch + opnd/acc construction, unchanged ...
  if (!isValid(needsRead)) begin
    ... existing smCompare -> Cmp3 c, unchanged ...
    case (gate)
      2'b00: ind = setAccCmpIndicatorsF(ind, c);          // K, KF
      2'b01: if (ind[63 - ind_AE] == 1)                   // KE, KFE
               ind = setAccCmpIndicatorsF(ind, c);
      2'b10: if (ind[63 - ind_AH] == 1 && c == CmpLow) begin   // KR, KFR
               ind = setBit(ind, ind_AE, 1);
               ind = setBit(ind, ind_AH, 0);
             end
      default: ind = setOpInvalid(ind);                   // unreachable
    endcase
  end
end
```

Indicator bit numbers, for reference: `StretchTypes.bsv:441` —
`ind_AL = 60`, `ind_AE = 61`, `ind_AH = 62`; read with `ind[63 - n]`.

The fetch, the `vflReadsUsed` bookkeeping, the data-fetch (DF)
signalling and the shared progressive-index completion at line 3156 all
stay outside the gate, which is both the p.91-consistent reading (§6) and
the choice that requires no new rule.

### 9.5 What does NOT change

* `smCompare` and `fieldToSM` are correct as they stand for all six ops —
  the comparison semantics are explicitly "identical to COMPARE" /
  "identical to COMPARE FIELD".
* Modifier decoding (`vi.m.unsign`, `vi.m.invert`, byte size / radix):
  unchanged, all six take exactly ADD's modifiers.
* Immediate addressing: all four take `I`. Pocket card page 4 (rendered
  at 300 dpi, read off the ink) lists, in its STRAP-mnemonic column:
  `K(I, N, NI)`, `KE(I, N, NI)`, `KF(I, N, NI)`, `KFE(I, N, NI)`,
  `KFR(I, N, NI)`, `KR(I, N, NI)` — i.e. each takes the Immediate,
  Negative-sign and Negative-Immediate suffixes. RefMan Figure 18 (p.67)
  uses `KEI (DU, 60, 4), 0, 0` for real. The existing `immediate` path in
  the K arm covers all of this for free.
* Accumulator: **none of the four ever writes it.** No `writeAcc` call
  belongs in any of these arms.

### 9.6 Suggested first decks

* `KE`: RefMan Figure 15 (p.66) verbatim — the four-instruction
  split-field compare, run twice with the high halves equal and unequal.
* `KR`, test A: RefMan Figure 17 (p.67) verbatim, driven through all four
  rows of §4.5's table. **Row 3 is the one that catches the AH-clear
  bug**: it is the only case where a correct KR must turn AH off, and a
  test that only checks AE will pass with the FP arm's logic.
* `KR`, test B (settles §8's open point, three instructions): `BB1 $AE`,
  `BB1 $AH`, load an accumulator value ≥ the storage operand, `KR`, then
  branch on AE. Set-only leaves AE on; set-or-clear turns it off. No
  source read here decides it, so write the deck before the arm.
* `KFE`/`KFR`: the same programs with the field variants and an
  accumulator carrying a one-bit to the left of the compared field, to
  pin "no indication is given ... if there is a one-bit in the
  accumulator to the left of the field".

---

## 10. Does MCP use any of these? NO.

Negative result, and it is clean.

```
$ grep -rnE "\b(KE|KR|KFE|KFR)I?\s*\(" decks/*.strap
decks/fp_arith_f219a.strap:231:        KR(N), FPK32
decks/fp_compare_f202g.strap:3:! the KR (Compare for Range) tests, run on the model. KR is the FP
decks/fp_compare_f202g.strap:85:        KR(U), FK34
decks/fp_compare_f202g.strap:90:        KR(U), FK34
decks/fp_compare_f202g.strap:95:        KR(U), FPK1
decks/fp_compare_f202g.strap:100:        KR(U), FPK1
decks/fp_compare_f202g.strap:105:        KR(U), FK25
decks/fp_compare_f202g.strap:110:        KR(U), FK25
decks/fp_compare_f202g.strap:115:        KR(U), FPK23
decks/fp_compare_f202g.strap:120:        KR(U), FPK23
```

(The grep carries `I?` so the immediate forms `KEI`, `KRI`, `KFEI`,
`KFRI` — which RefMan Figure 18 on p.67 actually uses — could not hide.
There are none. A second pass for a bare mnemonic followed by `,` found
the same ten lines and nothing else.)

**Every one of those hits is the FLOATING-POINT Compare for Range, not
the VFL one.** The 7030 reuses the mnemonic `KR` in both instruction
classes. The tell is the modifier list: `(U)` is the floating-point
*unnormalized* modifier and `(N)` the *negative-sign* modifier, and both
decks pair them with `L(U)` loads; a VFL `KR` would carry a field
descriptor like `KR(D, 40, 4), TEN8, 0`. `decks/fp_compare_f202g.strap`
says so in its own header, citing Reference Manual p.91 — the
floating-point page.

Searching the whole `decks/` tree, including all 71 transcribed
`mcp_bootstrap_p*.strap` pages:

**MCP uses none of KE, KR, KFE or KFR.** Nor does any other
non-floating-point deck in the repository. These four operations are
being implemented for coverage of the VFL instruction set, not to unblock
the MCP boot. Any deck that exercises them will have to be written from
the Reference Manual's own programming examples (§9.6) rather than lifted
from the listing.
