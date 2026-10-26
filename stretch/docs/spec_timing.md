<!-- PROVENANCE -- read before citing anything below. -->

> ## HOW THIS FILE WAS MADE
>
> Written 2026-10-25 by a **delegated agent** told to render and READ
> every page it quotes rather than trust `docs/ocr/`. It is research,
> not transcription, and the committing session has NOT checked it
> line by line.
>
> **Rule 4 still binds**: nothing here may be built into `bsv/` or a
> deck without opening the cited page first. These files say WHICH
> page and WHAT IT SAYS; the page is still the source.
>
> **Re-verified by the committing session: nothing yet.** The claims
> worth checking first are the transcribed timing tables, because
> `bsv/StretchTiming.bsv` already encodes numbers from the same
> tables and this file states which it confirms and which it
> corrects. A corrected timing number must be read at the ink before
> it is believed.

---

# IBM 7030 Performance Characteristics (March 8, 1961) — a citable timing spec

Source documents, both in `docs/`:

* `7030_Performance_Characteristics_Vol1_Mar61.pdf` — 71 PDF pages.
* `7030_Performance_Characteristics_Vol2_Mar61.pdf` — 189 PDF pages.

**Everything numeric below was read off a 300-dpi render of the page named,
with the `Read` tool, not off the OCR text.** The OCR (`docs/ocr/*.txt`) was
used only to find pages. Where a digit could not be resolved it is written
`[?]` — grep for that marker. Where the manual does not say something, this
file says "the manual is silent on X" rather than inferring.

## Page-number offsets (verified from printed footers, not computed)

| Document | printed | PDF | verified on |
|---|---|---|---|
| Vol. 1 ch. 3 | `3-N` | `N + 18` | footer `3-3` on PDF 21; `3-10` on PDF 28; `3-15` on PDF 33 |
| Vol. 1 ch. 4 | `4-N` | `N + 42` | see §3 (footer read there) |
| Vol. 2 | plain `N` | `N + 7` | see §3/§4 |

Citations below are written `[Table 2, printed p.3-3, PDF 21]`.

## Pages actually rendered and read in this pass

Rendered with `pdftoppm -r 300 -png` (or finer, with `-x -y -W -H` crops where
noted) and read as images.

**Volume 1 (29 pages):** 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
32, 33, 34, 35, 36, 43, 44, 45, 46, 47, 48, 49, 50, 51. Page 51 (Table 10) was
additionally cropped and re-rendered at 400 dpi (the floating-point block) and
500 dpi (the branching/totals block) to settle the three arithmetic defects in
§3.1.

**Volume 2 (12 pages):** 4, 18, 37, 105, 106, 108, 109, 111, 112, 113, 115,
117, 140. Page 109 was cropped and re-rendered at 500 dpi twice (the
EXTERNAL/INTERNAL columns, then the INDEX/IMMEDIATE columns); page 117's
`INVERT SIGN OF INSTRUCTION` block likewise at 500 dpi; page 140's heading at
400 dpi.

**Everything else cited by page number in this file** — in particular the
atlas page index in §3.4 and the `CM`/`CT` page numbers in §5.2 — comes from
the OCR page-separator headings and is explicitly labelled as a finding aid,
not as a reading.

---

# 1. The instruction timing tables

## 1.1 TABLE 2. FLOATING POINT INSTRUCTION TIMES

Printed pp. 3-3, 3-4, 3-5 = **PDF 21, 22, 23**. Column headings, verbatim:

> `Instruction` | `Pre-execution` | `Execution`

The two columns are defined on printed p. 3-1/3-2 (PDF 19/20), quoted in §2.
The unit is the machine cycle of 0.3 µs (§2).

### PDF 21 (printed 3-3)

| Instruction | Pre-execution | Execution |
|---|---|---|
| `+ (Add)`, `+MG (Add to Mag.)`, `M+ (Add to Mem.)`, `M+MG (Add Mag to Mem.)`, `K (Compare)`, `KMG (Compare Mag.)`, `KR (Compare for Range)`, `KMGR (Compare Mag. for Range)` | 4 cycles (pre shift ≤ 3) / 1 cycle for each Additional pre-shift of 4 | 1 cycle (norm ≤ 6) / 2 cycles for each additional norm. of 6 / 2 cycles if recomplement is necessary – note 1 / 2 cycles if forced zero occurs as result of "mag." operation. |
| `D+ (Add Double)`, `D+MG (Add Double to Mag.)`, `F+ (Add Fraction)` | Same as Add Class | Same as Add class plus 1 cycle if immediate next instruction is floating point |
| `L (Load)`, `LWF (Load with Flag)`, `LFT (Load Factor)`, `ST (Store)` | 2 cycles | 1 cycle (norm ≤ 6) / 2 cycles for each additional norm. of 6 |
| `DL (Load Double)`, `DLWF (Load Double with Flag)` | 2 cycles | 1 cycle (norm ≤ 6) / 2 cycles for each additional norm of 6 / 1 cycle if immediate next instruction is floating point |
| `SRD (Store Rounded)` | 3 cycles | 1 cycle (norm ≤ 6) / 2 cycles for each additional norm of 6 |
| `SLØ (Store Low Order)` | 2 cycles | 17 cycles – unnormalized / 15 cycles if normalized and there are no leading zeros in intermediate fraction / 2 cycles for each norm. of 6 or less |

### PDF 22 (printed 3-4)

| Instruction | Pre-execution | Execution |
|---|---|---|
| `SHF (Shift Fraction)` | "Applies to both left and right shift" — 4 cycles (shift ≤ 3) / 1 cycle for each additional shift of 4 | 1 cycle / 1 cycle if immediate next operation is floating point |
| `E+ (Add Exponent)`, `E+I (Add Immed. to Exp.)` – note 2 | 1 cycle | 5 cycles (norm ≤ 6) / 2 cycles for each additional norm. of 6 / 1 cycle if immediate next operation is floating point |
| `* (Multiply)` | 5 cycles | 4 cycles (norm. ≤ 6) / 2 cycles for each additional norm. of 6 |
| `D* (Multiply Double)` | 5 cycles | 4 cycles (norm ≤ 6) / 2 cycles for each additional norm. of 6 / 1 cycle if immediate next operation is floating point |
| `*+ (Multiply and Add)` | 3 cycles; cannot enter execution cycles until Factor is available | 17 cycles (pre shift ≤ 3 and norm ≤ 6) / 1 cycle for each additional pre-shift of 4 / 2 cycles for each additional norm. of 6 / 2 cycles if recomplement is necessary – note 1 / 1 cycle if immediate next operation is floating point |
| `R/ (Reciprocal Divide)` | 2 cycles | 2 cycles plus all pre-execution and execution cycles of Divide |

### PDF 23 (printed 3-5)

| Instruction | Pre-execution | Execution |
|---|---|---|
| `/ (Divide)` | 2 cycles (divisor shift ≤ 6) / 2 cycles for each additional divisor shift of 6 | 2 cycles (dividend shift ≤ 6) / 2 cycles for each additional dividend shift of 6 or total of 3 cycles if dividend is all zero / 2 cycles for initial reduction loop if dividend is normalized / 3 cycles for initial dividend pass if dividend has leading zeros. / 2 cycles for each additional reduction loop (number of cycles is data dependent). / 2 cycles if final remainder has to be complemented / 1 cycle - all |
| `/` (zero divisor) | If zero divisor 3 cycles pre-execution and | 2 cycles execution instead of previous |
| `D/ (Divide Double)` | Same as *Divide* | Same as *Divide* plus 6 cycles (remainder norm ≤ 6) / 2 cycles for each additional remainder norm. of 6 |
| `SRT (Store Root)` | 2 cycles | 106 cycles (norm. ≤ 6) / 1 cycle if operation began with a "B" pulse / 2 cycles for each additional norm of 6 |

### Notes 1 and 2 [printed p. 3-6, PDF 24], verbatim

> NOTE 1 – When fraction signs are unlike, the operand which is pre-shifted
> will be complemented. Recomplementing will only occur if the complemented
> (following pre-shift) fraction is larger in magnitude than unshifted
> fraction. / If fraction signs are alike no complementing occurs.

> NOTE 2 – <u>Add Exponent</u> and <u>Add Immediate to Exponent</u> will most
> likely be changed in the near future to three pre-execution and three
> execution cycles.

**Note 2 is a live warning for the model**: the E+ / E+I numbers in Table 2
are explicitly provisional.

## 1.2 TABLE 3. EQUATIONS FOR SAU INSTRUCTIONS

Printed pp. 3-7, 3-8, 3-9 = **PDF 25, 26, 27**. Column headings, verbatim:

> `Operation Code` | `Pre-execution Time` | `Execution Time` | `Termination Time` | `Full Word Total` | `Comments`

Headings defined on printed p. 3-6 (PDF 24), verbatim:

> * Operation Code - instruction abbreviations.
> * Pre-execution Time - time required to decode operation and set up controls.
> * Execution Time - time required to perform the instructed function.
> * Termination Time - time required to set indicators and clear unit.
> * Full Word Total - a computed time in microseconds for the operations using
>   unsigned full word operands which produce no arithmetic carries.
> * Comments - variations or additions to the execution time equations.

And, the sentence the model currently does **not** implement:

> All equations were developed for unsigned operations. Signed operations can
> be computed by adding .6 microseconds to the pre-execution time. An
> additional .6 microseconds must be added if the result of the operation
> requires complementing. The following operations require no additional time
> when signed: *SRD, C, CM, CT, CV, DCV, LCV (D-B), LTRCV (D-B), LTRS, LFT*.

All times in the table are in microseconds.

### PDF 25 (printed 3-7)

| Operation Code | Pre-exec | Execution | Termination | Full Word Total | Comments |
|---|---|---|---|---|---|
| `+` | 1.8 | .6(x/y + z) | .6 | 7.2 us | Unlike signs CD > AB, add .6(OS/r + x/y + Z + 1) to the execution time. |
| `+MG` | 1.8 | .6(x/y + z) | .6 | 7.2 us | Unlike signs CD > AB, add .6 to the execution time. |
| `L` | 1.8 | .6(x/y) | .6 | 7.2 us | |
| `LWF` | 1.8 | .6(x/y) | .6 | 7.2 us | |
| `M+` | 1.8 | .6(x/y) | .6 | 7.2 us | Unlike signs AB > CD, add .6(x/y + 1) to the execution time. |
| `M+MG` | 1.8 | .6(x/y) | .6 | 7.2 us | Unlike signs AB > CD, add .6(x/y + 1) to the execution time. |
| `M+1` | 1.8 | .6(c + 1) | .6 | 3.0 us | Unlike signs, execution time = .6(x/y) when true result or .6(2x/y + 1) when complement result. |
| `ST` | 1.8 | .6(x/y) | .6 | 7.2 us | |
| `SRD` | 3.0 | .6(x/y) | .6 | 8.4 us | No additional time required when operation is signed. |
| `K` | 1.8 | .6(x/y + w/r) | .6 | 7.2 us | |
| `KF` | 1.8 | .6(x/y) | .6 | 7.2 us | |
| `KE` | 1.8 | .6(x/y + w/r) | .6 | 7.2 us | |
| `KFE` | 1.8 | .6(x/y) | .6 | 7.2 us | |

### PDF 26 (printed 3-8)

| Operation Code | Pre-exec | Execution | Termination | Full Word Total | Comments |
|---|---|---|---|---|---|
| `KR` | 1.8 | .6(x/y + w/r) | .6 | 7.2 us | |
| `KFR` | 1.8 | .6(x/y) | .6 | 7.2 us | |
| `C` | 1.8 | .6(x/y) | .6 | 7.2 us | |
| `CM` | 1.8 | .6(x/y) | .6 | 7.2 us | |
| `CT` | 1.8 | .6(x/y) | .6 | 7.2 us | |
| `LTRS` | 2.4 | .6(v/y + 3) | .6 | 9.6 | If the effective FL is greater than 48 bits, add .6(t/8 – 1) to the execution time. |
| `LFT` | 2.4 | .6(v/y) + 3 | .6 | 9.6 | If the effective FL is greater than 48 bits, then add .6(t/8 – 1) to the execution time. |
| `B – D  LCV` | 2.4 | .6(x + u/8 + 1) | .6 | 45.3 | |
| `D – B  LCV` | 2.4 | .6(x/y + t/4 + u/8 + 4) | .6 | 14.7 | |
| `B – D  LTRCV` | 2.4 | .6(x + 3) | .6 | 29.4 | If the converted field length is greater than 48 bits, add .6(FLc/8 – 1) to the execution time. |
| `D – B  LTRCV` | 2.4 | .6(x/y + 16) | .6 | 21.6 | If the field length to be converted after all zone bits have been removed is greater than 48 bits, add .6(t/8 – 1) to the execution time. |
| `B – D  CV` | 2.4 | .6(s + u/8 + 1) | .6 | 37.2 | |

Note the parenthesisation difference between `LTRS` `.6(v/y + 3)` and `LFT`
`.6(v/y) + 3` — that is how the page prints them; both give Full Word Total
9.6, so **`LFT`'s printed form is internally inconsistent with its own Full
Word Total and `LTRS`'s is not**. Treat `LFT` as `.6(v/y + 3)` and record the
discrepancy rather than the render being misread: the `+ 3` sits clearly
outside the closing parenthesis on the page.

### PDF 27 (printed 3-9)

| Operation Code | Pre-exec | Execution | Termination | Full Word Total | Comments |
|---|---|---|---|---|---|
| `B – D  DCV` | 2.4 | .6(s + u/8 + 1) | .6 | 63.0 | |
| `D – B  CV` | 2.4 | .6(s/4 + 1) | .6 | 10.8 | |
| `D – B  DCV` | 2.4 | .6(s/4 + 2) | .6 | 18.6 | |
| `*` | 6.0 | 3.9 | .6 | 10.5 | |
| `*+` | 7.8 | 3.0 + *Add* exec. time | .6 | 18.6 | |
| `/` | 5.4 | Q | .6 | 24.0 | Q = .6( DR L"O"/6 + (DDL or DRL)/8 + A + (97 – DRL)/8 + 1 ) ; A = 1. Zero DD – (DDL – DRL)/6  2. Leading zero's –(1 + #L"O"/6 + (DDL – DRL – #L"O")/4)  3. Complement Result. –Add 1 to A2. |

### Glossary of Terms [printed p. 3-10, PDF 28], verbatim and complete

| Symbol | Definition |
|---|---|
| DD | Dividend |
| DR | Divisor |
| DDL | Dividend length |
| DRL | Divisor length |
| L "0" | Leading zero's |
| #L "0" | Number of leading zero's |
| DDL or DRL | Dividend or divisor length which ever is greater |
| OS | Offset |
| FL | Field length |
| BS | Byte size |
| B - D | Binary to decimal |
| D - B | Decimal to binary |
| R | 8 in Binary - 4 in decimal |
| S | Accumulator field specified by the offset minus all leading zero's |
| T | Field length less all zone bits |
| U | Result field |
| V | 96 in binary - 92 in decimal |
| W | The number of accumulator significant bits greater than the field length |
| X | Field length in unsigned operations - field length minus the byte size in signed operations |
| Y | 8 in binary operations and byte size in decimal operations |
| Z | One for a carry out of the last x/y byte plus one for a carry out of each succeeding 8 bit byte in binary or 4 bit byte in decimal |
| C | The number of times a carry results from an 8 bit byte in binary or a 4 bit byte in decimal |

Immediately below the glossary, printed p. 3-10 introduces Tables 4–9:

> Timing of I-Box Instructions / The following tables list the I-box times for
> decoding for execution of I-box instruction.

## 1.3 TABLE 4. I-BOX TIMES – DIRECT INDEX  [printed p. 3-11, PDF 29]

Column headings, verbatim:

> `Instruction` | `Address in EM` | `Address in XS` | `Address in IR`

| Instruction | Address in EM | Address in XS | Address in IR |
|---|---|---|---|
| `LX` | 4.8 µsec + dec | 4.8 µsec + dec | 4.2 µsec + dec + LAdr |
| `LV, LC, LR` | 4.2 µsec + dec | 4.2 µsec + dec | 3.6 µsec + dec + LAdr |
| `SX` | 1.2 µsec + dec + LAAR | 4.2 µsec + dec | 1.2 µsec + dec + LAAR |
| `SV, SC, SR` | 4.2 µsec + dec + LAAR | 5.4 µsec + dec | 3.6 µsec + dec + LAdr + LAAR |
| `SV, SC, SR to TC` | — | 6.0 µsec + dec + LAdr | — |
| `V+` | 4.2 µsec + dec | 4.2 µsec + dec | 3.6 µsec + dec + LAdr |
| `V+C` | 4.2 µsec + dec | 4.8 µsec + dec | 4.2 µsec + dec + LAdr |
| `V+CR (EM)` | 8.4 µsec + dec | 9.0 µsec + dec | 8.4 µsec + dec + LAdr |
| `V+CR (XS)` | 7.2 µsec + dec | 7.8 µsec + dec | 7.2 µsec + dec + LAdr |
| `KV, KC` | 4.2 µsec + dec | 4.2 µsec + dec | 3.6 µsec + dec + LAdr |
| `RNX` | 9.0 µsec + dec + LAdr + LAAR | — | — |
| `LVE` | 7.8 µsec + dec | 6.6 µsec + dec | 6.6 µsec + dec + LAdr |
| `LVE as object INSN of LVE` | Additional 4.8 µsec | Additional 3.6 µsec | Additional 3.0 µsec + LAdr (4.2 if LAMT) |
| `SVA` | 4.2 µsec + dec + LAAR | 5.4 µsec + dec | 3.6 µsec + dec + LAdr + LAAR |
| `SVA to TC` | — | 6.0 µsec + dec + LAdr | — |

> ABBREVIATIONS: dec = decade / LAAR = Look-ahead address register /
> LAdr = Look-ahead drain / LAMT = Look-ahead empty / TC = Time clock

**The manual prints `dec = decade`, not "decode".** Tables 4–8 are introduced
as "the I-box times for *decoding* for execution", so "decade" is plainly the
*decode* step's time, but **the manual is silent on the numeric value of
`dec`** anywhere in chapter 3. The project's assumption `dec = 0.6 µs`
(StretchTiming.bsv) is **not sourced from these two volumes** — see §5.

## 1.4 TABLE 5. I-BOX TIMES – IMMEDIATE INDEX  [printed p. 3-11, PDF 29]

Column headings, verbatim: `Instruction` | `Basic Time` | `Variations`

| Instruction | Basic Time | Variations |
|---|---|---|
| `LVI, LCI, LRI, LVNI` | 2.4 µsec + dec | |
| `V+I, V-I` | 2.4 µsec + dec | |
| `V+IC, V-IC` | 3.0 µsec + dec | Also V ± ICR where Count ≠ 0 |
| `V+ICR, V-ICR` | 7.2 µsec + dec | 1.2 µsec less if Refill from X5 |
| `C+I, C-I` | 2.4 µsec + dec | |
| `KVI, KVNI, KCI` | 2.4 µsec + dec | |
| `LVS` | 5.4 µsec + dec | Additional 1.8 µsec per ADD |

## 1.5 TABLE 6. I-BOX TIMES – MISCELLANEOUS INSTRUCTIONS  [printed pp. 3-12 / 3-13, PDF 30 / 31]

Column headings, verbatim: `Instruction` | `Address in EM` | `Address in XS` | `Address in IR`

| Instruction | Address in EM | Address in XS | Address in IR |
|---|---|---|---|
| `R (from EM)` | 7.8 µsec + dec + LAAR | 7.2 µsec + dec | 6.6 µsec + dec + LAAR + LAdr |
| `R (from XS)` | 5.4 µsec + dec + LAAR | 5.4 µsec + dec | 4.2 µsec + dec + LAAR + LAdr |
| `RCZ (C ≠ 0)` | 4.2 µsec + dec | 3.0 µsec + dec | 3.0 µsec + dec + LAdr |
| `Z` | 1.2 µsec + dec + LAAR | 3.6 µsec + dec | 1.2 µsec + dec + LAAR |

`EX` is given as a recipe, not a number:

> 1. Decode time, plus
> 2. Always begins with Look-ahead drain, plus
> 3. Instruction fetch time as follows:

| Address | Time |
|---|---|
| 0.0, 0.32 | 4.8 µsec |
| 1.0, 1.32 | 6.0 µsec |
| 2.0, 2.32 | 7.8 µsec |
| 3.0, 3.32 | 7.8 µsec |
| 4.0, 4.32 | 7.8 µsec |
| 5.0 → 11.32 | 11.2 µsec |
| 12.0, 12.32 | 7.8 µsec |
| 13.0 → 14.32 | 5.4 µsec |
| 15.0, 15.32 | 4.8 µsec |
| 16.0 → 30.32 | 4.2 µsec |
| 31.0, 31.32 | 6.0 µsec |
| 32.0 → up | 5.4 µsec |

> 4. Add decode and execution time for given instruction
> 5. Always ends with LA drain, plus
> 6. Add 3.0 µsec for fetch of next instruction

(These addresses are the special registers 0–31 and then general storage;
`11.2 µsec` for 5.0 → 11.32 is the one entry whose first digit sits against
the column rule — it is legible as **11.2**, and it is the only two-digit
value in the column.)

`EXIC` [printed p. 3-13, PDF 31], verbatim:

> 1. Decode time, plus
> 2. Always begins with a Look-ahead drain
>    a) 4.2 µsec to fetch the psuedo-instruction counter are overlapped with
>       the Look-ahead drain if the ps IC is in EM.
>    b) 3.0 µsec to fetch the psuedo-instruction counter are overlapped with
>       the Look-ahead drain if the ps IC is in XS.
> 3. Instruction fetch time = 6.0 µsec
> 4. Stepping of psuedo-instruction counter
>    a) Add LAAR time if psIC in EM
>    b) Add .6 µsec time if psIC in XS
> 5. Add decode and execution time for given instructions
> 6. Always ends with LA drain, plus
> 7. Add 3.0 µsec for fetch of next instruction

## 1.6 TABLE 7. I-BOX TIMES – UNCONDITIONAL BRANCH  [printed p. 3-13, PDF 31]

Column headings, verbatim: `Instruction` | `Basic Time` | `SIC to EM` | `SIC to XS`

| Instruction | Basic Time | SIC to EM | SIC to XS |
|---|---|---|---|
| `B` | 3.6 µsec + dec | 4.8 µsec + dec + LAAR | 4.2 µsec + dec |
| `BR` | 4.8 µsec + dec | 6.0 µsec + dec + LAAR | 5.4 µsec + dec |
| `BE` | 3.6 µsec + dec + LAdr (if previously disabled) | 4.8 µsec + dec + LAAR + LAdr (if previously disabled) | 4.2 µsec + dec + LAdr (if previously disabled) |
| `BEW` | Setup time as above on BE | | |
| `NOP` | 1.2 µsec + dec | Same as Basic | Same as Basic |
| `BD` | 4.8 µsec + dec + 2 LA drains | 6.0 µsec + dec + 2 LA drains | 5.4 µsec + dec + 2 LA drains |

## 1.7 TABLE 8. I-BOX TIMES – INDEX BRANCHES  [printed p. 3-14, PDF 32]

Column headings, verbatim: `Instruction` | `Basic Time` | `SIC to EM` | `SIC to XS`

| Instruction | Basic Time | SIC to EM | SIC to XS |
|---|---|---|---|
| `CB (Successful)` | 4.2 µsec + dec | 6.6 µsec + dec + LAAR | 7.2 µsec + dec |
| `CB (Unsuccessful)` | 3.6 µsec + dec | 3.6 µsec + dec | 3.6 µsec + dec |
| `CBR (EM) (Succ)` | 6.6 µsec + dec | 9.0 µsec + dec + LAAR | 9.6 µsec + dec |
| `CBR (XS) (Succ)` | 6.0 µsec + dec | 8.4 µsec + dec + LAAR | 9.0 µsec + dec |
| `CBR (EM) (Unsucc)` | 6.0 µsec + dec | 6.0 µsec + dec | 6.0 µsec + dec |
| `CBR (XS) (Unsucc)` | 5.4 µsec + dec | 5.4 µsec + dec | 5.4 µsec + dec |

> NOTE: CBR behaves like CB if Refill is not to be taken. / Ex: CBR, branch on
> count ≠ zero

## 1.8 TABLE 9. I-BOX TIMES - TRANSMIT INSTRUCTIONS  [printed pp. 3-14 / 3-15, PDF 32 / 33]

Column headings, verbatim: `Instruction` | `Setup time` | `Loop time` | `Termination time`

Transmit (`T`), PDF 32:

| Instruction | Setup time | Loop time | Termination time |
|---|---|---|---|
| `T (EM → EM)` | 1.2 usec + dec + LA dr | 3.0 usec | 3.6 usec |
| `T (EM → XS)` | 1.2 usec + dec + LA dr | 4.2 usec | .6 usec |
| `T (XS → EM)` | 1.2 usec + dec + LA dr | 3.0 usec | 3.6 usec |
| `T (XS → XS)` | 1.2 usec + dec + LA dr | 4.2 usec | .6 usec |
| `T (IR → EM)` | 1.2 usec + dec + LA dr | 7.2 usec | 3.6 usec |
| `T (IR → XS)` | 1.2 usec + dec + LA dr | 7.2 usec | .6 usec |

> Note: Transmit to EM and IR identical in time.

Swap (`S`), PDF 33:

| Instruction | Setup time | Loop time | Termination time |
|---|---|---|---|
| `S (EM → EM)` | 1.2 usec + dec + LA dr | 6.0 usec | 1.8 usec |
| `S (EM → XS)` | 1.2 usec + dec + LA dr | 6.6 usec | 1.8 usec |
| `S (EM → IR)` | 1.2 usec + dec + LA dr | 9.6 usec | 1.8 usec |
| `S (XS → EM)` | 1.2 usec + dec + LA dr | 6.0 usec | 1.8 usec |
| `S (XS → XS)` | 1.2 usec + dec + LA dr | 7.2 usec | 1.8 usec |
| `S (XS → IR)` | 1.2 usec + dec + LA dr | 10.8 usec | 1.8 usec |
| `S (IR → EM)` | 1.2 usec + dec + LA dr | 9.6 usec | 1.8 usec |
| `S (IR → XS)` | 1.2 usec + dec + LA dr | 10.2 usec | 1.8 usec |
| `S (IR → IR)` | 1.2 usec + dec + LA dr | 15.0 usec | 1.8 usec |

> Note: The immediate/direct and the forward/backward options do not affect
> the timing of either transmit or swap.

**The manual is silent on what "Loop time" is per: per word, per pair of
words, or for the whole loop.** The column is called "Loop time" and nothing
on either page quantifies the loop count. Vol. 2 printed pp. 98–100 (PDF 105–107)
carries measured transmit sequences and is the place to settle it; see §3.5.

---

# 2. The machine's clock and cycle structure, as the manual states it

Everything in this section is a quotation. Nothing here is inferred.

## 2.1 The basic machine cycle

[printed p. 3-2, PDF 20, last line of the section introducing Table 2]

> The times are listed (table 2) in terms of the basic machine cycles, which
> is presently 0.3 microsecond.

Note the word **presently**: the figure is given as the current value of a
machine still being built, not as a constant of the architecture.

## 2.2 What "pre-execution" and "execution" mean

[printed pp. 3-1 / 3-2, PDF 19 / 20]

> Following is a summary of "raw" floating point execution. The times are
> predicated upon the availability of data and instructions when needed; that
> is, the times given are the maximum speed at which the floating point unit
> may operate. If some memory access (look-ahead, I-box, etc.) factors enter
> such that data and instructions are not available when the floating point
> unit is able to accept them (or requires them), the extra delay thus caused
> is added to the times below.

> ● Pre-Execution — That part of the instruction which may be executed before
> any modification of an addressable register occurs. Floating point
> instructions are begun as soon as data paths are free and the instruction
> and initial addressed operand is made available. This time will overlap
> checking of a previous instruction, indicator setting, interrupt testing,
> memory storage, etc. These cases may lead to a condition such that the
> operation should never have been started (interrupt occurs as result of
> previous instructions). In such a case the pre-execution is terminated and
> no addressable registers would be modified. (As far as programmer is
> concerned pre-execution never occurred.)

> Execution — The part of the instruction which follows the initial
> modification of an addressable register up to the point when the next
> floating point instruction may begin.

That last sentence is the **issue-to-issue** definition the model needs: a
floating point instruction's "execution" cycles are exactly the interval
before the next floating point instruction may begin.

## 2.3 Decoding rates — the I-box's own clock, such as the manual gives it

[printed p. 3-17, PDF 35, under the heading "Overlapping of Decoding"]

> The I-box decoding, address indexing, and operand request continues as long
> as instructions are available and as long as LA levels are available for
> loading. For a sequence of floating point instructions the decoding rate is
> one instruction per 1.2 µs. With few exceptions, this is faster than the
> execution rate. Thus the decoding time for average floating point sequences
> is completely overlapped by concurrent E-box execution time. In other words,
> floating point instructions are E-box limited. Address indexing has no
> measurable effect on the timing of floating point instructions.

[printed p. 3-18, PDF 36 — the three sentences that source three different
model constants]

> *VFL* instruction decoding is much more complicated. The minimum time is
> 3.6 µs which includes the loading of two LA levels. Each addition[al] level
> requires an additional 0.6 µs, and each indexing operation requires 0.6 µs.
> Of course, there may be further slow down in the decoding process if the LA
> levels are not available for loading, or if the second half of the
> instruction is not available when needed.

> The decoding time of I-box instructions is 0.6 µs. Since these instructions
> are executed in the I-box, the decoding time has been included in the
> execution times. The processing time of I-box instructions can be largely
> overlapped by concurrent E-box action, since their E-box time is only 1.2 µs.

> Whenever a branch instruction is successfully executed, the pre-fetched
> instructions in 1Y, 2Y must be replaced by new instructions. The latter have
> to be checked prior to use, and the decoding of the next instruction will be
> delayed. This delay has been taken into account in the timing given. Again,
> concurrent E-box action can overlap much of this.

**This page, printed 3-18 (PDF 36), is where `dec = 0.6 µs` actually comes
from.** Tables 4–8 only abbreviate `dec = decade` and never give its value;
p.3-18 gives "The decoding time of I-box instructions is 0.6 µs" and says it
is what the "+ dec" in those tables stands for. The project's plan and
`StretchTiming.bsv` both attribute the 0.6 µs and the VFL 3.6 + 0.6/level to
"p.3-17" — **the citation is off by one page; the numbers are right.**

**There is no statement anywhere in Volume 1 or Volume 2 that the I-box
control cycle is two machine clocks (0.6 µs).** What the manual gives is a
set of *rates* and *decode times* that are all multiples of 0.6 µs. The model
may keep its two-clock control cycle, but it must be recorded as an inference
from the granularity of these tables, not as a quotation. See §5.

## 2.4 Memory

[printed p. 3-15, PDF 33, under "Machine Organization"]

> For example, a 7030 box has a readout time of 1 µs and a recycle time of
> 2.2 µs, yet in the 7030 system information can be obtained at the rate of
> one word every 0.3 µs.

[printed p. 3-17, PDF 35, under "Effect of Memory Interleaving"]

> With the instruction buffers 1Y, 2Y (capable of housing four half-word
> instructions), in the I-box, and the four LA levels, the advantage of memory
> interleaving is fully exploited.

> The demand of the E-box on LA is usually no higher than one word per 1.5 µs
> (sequence of floating adds) and on the average, the memory is not a factor.
> In terms of the four-level look-ahead, the requirement is satisfied if any
> four E-box demands are fulfilled in 6 µs. The memory interleave scheme
> allows four words every 2.2 µs (four box interleaving) or four words every
> 4.4 µs (two box interleaving).

> In actual computations, with the instructions occupying the two lower memory
> boxes and data occupying the four upper memory boxes, memory conflict is not
> expected to be an important factor, even if the I/O units are in full
> operation. Delays due to repeated demands of the same memory box are
> expected to be quite infrequent.

Note: **2.2 µs recycle, 1 µs readout**. The project's plan (`A.7 Memory`)
records "2.1 µs read-write cycle" from Buchholz; Performance Characteristics
says 2.2. Both can be true of different machines/dates, but the number the
*timing* tables were computed against is the 2.2 µs on this page.

## 2.5 How many instructions are in flight

[printed p. 3-16, PDF 34]

> Each major unit is responsible for processing at top speed as long as there
> is data to process. ... Within the CPU this local autonomy means that
> temporary delays up to several µs in one unit can be tolerated without
> slowing down the entire pipe line. Extensive buffering of information is
> needed to absorb such temporary delays, and within the 7030 CPU at any given
> time up to ten instructions can be in various stages of processing. Within
> wide limits, the times for instruction processing is not the sum of:
> Instruction fetch, instruction error check, decoding, operand fetch, operand
> error check, and execution but is the maximum of these times averaged over
> several instructions.

> The E-box times of the instructions listed in the previous section are the
> times realizable if the LA levels (which are buffers to the E-box) can
> always supply needed information to the E-box. The machine organization is
> such that this is usually the case.

(The plan's `A.6` says "Up to six instructions in progress", from Blosk.
This page says **ten**. Both are sourced; they count different things — Blosk
counts I-box stages, this counts the whole CPU including the four LA levels.)

[printed p. 3-18, PDF 36, "Look-Ahead Levels"]

> The following instructions empty the LA completely: *T, TI, SWAP, SWAP I,
> RNX, BD*.

> All I-box instructions load LA levels for index register recovery or for
> indicator register updating. These levels are not useful to the E-box and
> have the effect of reducing the number of LA levels.

> *VFL* data with word boundary crossover represent inefficient use of LA
> levels.

---

# 3. THE ORACLES

## 3.0 Volume 2's two page-number sequences — read this before citing it

Volume 2 does **not** have one page-number offset. Two sequences, both read
from printed footers/headers:

| Section | PDF pages | printed | offset | verified on |
|---|---|---|---|---|
| Benchmark program listings | 4 – 36 | 1 – 33 | PDF = printed + 3 | PRIMC listing head "15" on PDF 18 |
| Instruction timing atlas | 37 – 189 | 34 – 186 | PDF = printed + 3 for the prose head, **+ 7 for the landscape tables** | PREFACE "34" on PDF 37; "COMMENTARY ON VFL" **108** on PDF 115; "VFL INSTRUCTION M+" **110** on PDF 117; "I-BOX INSTRUCTIONS" **102** on PDF 109 |

So the prose pages of the atlas and its landscape tables are numbered on two
different runs. **Always cite Volume 2 by PDF page**; the printed number is
recorded beside it where it was read.

## 3.1 TABLE 10. EXECUTION FREQUENCY CHART FOR STRETCH PROGRAMS  [printed p. 4-9, PDF 51]

Column headings, verbatim (two header rows):

> `Operation` | `A0` | `Pseudo j-level` | `A1` | `Modified` | `A2` | `Grid Param.` | `Elem. Functions 1st Form` | `2nd Form`

(The heading prints **A0** with a zero; the prose on printed pp. 4-6/4-7
writes **AO** with a letter O for the same column. Same column.)

Row groups are `Fl. Pt.`, `VFL`, `Indexing`, `Branching`, `Miscell.`, each
with a `Total` line, then `Grand Total`, `Execution Time (ms)`,
`Aver. time (µs)/opn`.

### Floating point

| Operation | A0 | Pseudo j-level | A1 | Modified | A2 | Grid Param. | Elem. 1st | Elem. 2nd |
|---|---|---|---|---|---|---|---|---|
| LFT | 144 | | | | | 39 | | |
| L | 257 | 1 | 437 | 633 | 651 | 243 | 7 | 7 |
| ST | 261 | 1 | 465 | 659 | 677 | 202 | 15 | 15 |
| + | 250 | | 394 | 581 | 581 | 195 | 28 | 28 |
| * | 220 | | 434 | 637 | 637 | 187 | 26 | 26 |
| / | 88 | | 42 | 51 | 51 | 42 | 2 | 2 |
| *+ | 144 | | | | | 39 | | |
| D* | | | | | | | 2 | |
| K | | | | | | 45 | 2 | 2 |
| SHF | | | | | | | 2 | |
| E+ | | | | | | 69 | 4 | 4 |
| SRT | | | | | | 4 | | |
| **Total** | **1364** | **2** | **1772** | **2561** | **2597** | **1065** | **88** | **84** |

### VFL

| Operation | A0 | Pseudo j-level | A1 | Modified | A2 | Grid Param. | Elem. 1st | Elem. 2nd |
|---|---|---|---|---|---|---|---|---|
| L | 10 | 8 | 10 | 9 | 9 | 128 | 4 | 2 |
| ST | 2 | | 2 | 1 | 1 | 93 | 6 | 2 |
| + | 20 | 18 | 20 | 19 | 19 | 20 | | |
| CM | 66 | 66 | 70 | 71 | 71 | 9 | | |
| * | | | | | | 8 | | |
| LFT | | | | | | 4 | | |
| *+ | | | | | | 4 | | |
| -MG | | | | | | 4 | | |
| M+1 | | | | | | 37 | | |
| K | | | | | | 64 | | |
| **Total** | **98** | **92** | **102** | **100** | **100** | **371** | **10** | **4** |

### Indexing

| Operation | A0 | Pseudo j-level | A1 | Modified | A2 | Grid Param. | Elem. 1st | Elem. 2nd |
|---|---|---|---|---|---|---|---|---|
| LZ,LV,LC,SV | 13 | 9 | 13 | 11 | 11 | 6 | | |
| V+ | 60 | | 60 | 78 | 78 | 117 | | |
| CB | 15 | 1 | 15 | 20 | 20 | 13 | | |
| KCI | 12 | | 12 | 18 | 18 | | | |
| **Total** | **100** | **10** | **100** | **127** | **127** | **136** | **0** | **0** |

### Branching

| Operation | A0 | Pseudo j-level | A1 | Modified | A2 | Grid Param. | Elem. 1st | Elem. 2nd |
|---|---|---|---|---|---|---|---|---|
| B,BD,BEW | 77 | 5 | 68 | 91 | 91 | 6 | 8 | 10 |
| BIND | 18 | | 18 | 27 | 27 | 274 | 3 | 3 |
| BB | 2 | | 2 | 1 | 1 | 1 | | |
| **Total** | **97** | **5** | **88** | **119** | **119** | **280** | **11** | **13** |

### Miscellaneous, totals and times

| | A0 | Pseudo j-level | A1 | Modified | A2 | Grid Param. | Elem. 1st | Elem. 2nd |
|---|---|---|---|---|---|---|---|---|
| `Z,TI` Total | 52 | | 28 | 38 | 29 | 31 | 1 | 1 |
| **Grand Total** | **1711** | **109** | **2090** | **2945** | **2972** | **1883** | **114** | **106** |
| **Execution Time (ms)** | **5.98** | **.7** | **5.57** | **7.045** | **7.0135** | **7.07** | **.38** | **.309** |
| **Aver. time (µs)/opn** | **3.5** | **6.4** | **2.7** | **2.4** | **2.36** | **3.8** | **3.3** | **2.9** |

**Three arithmetic defects in the printed table, all verified at 500 dpi on a
cropped render, not inferred from a bad OCR:**

1. Grid Param. Branching: `6 + 274 + 1 = 281`, but the printed `Total` is
   **280**, and the printed `Grand Total` 1883 is consistent with 280
   (1065 + 371 + 136 + 280 + 31 = 1883). So one of the three branching
   entries is one too large, or the Total is one too small; the page does not
   say which.
2. Elem. Functions 1st Form `Grand Total` is **114**, but the five printed
   section totals sum to 88 + 10 + 0 + 11 + 1 = **110**.
3. Elem. Functions 2nd Form `Grand Total` is **106**, but 84 + 4 + 0 + 13 + 1
   = **102**. Both Elem. columns are short by exactly 4 — consistent with one
   missing row of 4 operations in each, not with a typo in the total.

Every other column's section totals and grand total check exactly. Record
these as *defects of the source*, not as reading errors, and do not assert a
model against the three bad cells.

Consistency check that the table passes: `Execution Time / Grand Total` gives
`Aver. time/opn` to the printed precision in every column
(5.98 ms / 1711 = 3.49 µs → 3.5; 7.0135 ms / 2972 = 2.360 → 2.36;
.38 ms / 114 = 3.33 → 3.3; .309/106 = 2.92 → 2.9 — note the last two use the
*defective* grand totals, so IBM's own average was computed from 114/106).

## 3.2 The benchmarks, one by one

### GERB2 — matrix inversion  [printed pp. 4-1/4-2, PDF 43/44]

* **Problem** (verbatim): "The inversion of Hilbert matrix segments of
  increasing size, using Jordan's elimination method. In each case the
  determinant of the matrix is evaluated as a by-product."
* **Problem size / published time** [printed p. 4-1, PDF 43]:

  | size | time |
  |---|---|
  | 10 x 10 matrix | 0.02 seconds |
  | 20 x 20 matrix | 0.14 seconds |
  | 30 x 30 matrix | 0.43 seconds |
  | 40 x 40 matrix | 0.99 seconds |
  | 50 x 50 matrix | 1.89 seconds |
  | 60 x 60 matrix | 3.23 seconds |
  | 70 x 70 matrix | 5.10 seconds |
  | 80 x 80 matrix | 7.55 seconds |
  | 90 x 90 matrix | 10.69 seconds |
  | 100 x 100 matrix | 14.61 seconds |

* **Operation mix**: Table 10 has **no GERB2 column**. The manual is silent on
  GERB2's operation mix.
* **Source**: Volume 2, **PDF 4 – 8** (printed 1 – 5), headed "LISTING OF
  GERB2 PROGRAM", first line `PUNID, GERBERIC`, last line `END, START`.
* **Instructions it needs** that the model does not have. Read off the first
  page of the listing itself (V2 printed p. 1, PDF 4): `DL` (load double),
  `D/` (divide double), `SRD`, `SVA`, `T` (transmit), `C+I` / `C-I`, `CB+`.
  Plus `*+`, which Vol. 1 printed p. 4-1 names: "The present program uses the
  relatively slow *+ (*multiply and add*) instruction to obtain 96-bit
  intermediate fraction accuracy". Against plan §A.9's "Open" list that is
  **all of double precision, `*+`, `/`, `SRD`**.
  It generates its own matrix — the listing's second line is the comment
  `-A (I,J) = 1/(I+J-1)-` — so it needs no input deck.
* **Runnable oracle today?** **No.** The very first floating-point arithmetic
  in the listing is `DL, ONE` / `D/, TEMP` — double-precision divide, which
  the model does not execute at all. Vol. 1 also says a double-precision
  variant GERB3 exists [printed p. 4-2, PDF 44].

### MXM16 — matrix multiplication  [printed p. 4-3, PDF 45]

* **Problem** (verbatim): "Multiplication of two nxn matrices."
* **Problem size / published time**:

  | size | time |
  |---|---|
  | 25 x 25 matrices | 0.20 seconds |
  | 50 x 50 matrices | 1.35 seconds |
  | 75 x 75 matrices | 4.74 seconds |
  | 100 x 100 matrices | 10.71 seconds |
  | 125 x 125 matrices | 21.44 seconds |

* **Conditions** (verbatim): "Assume n = 17 k+m. A 'major' inner loop is
  traversed k times, then a short inner loop is traversed m times, for each
  vector multiplication." / "The matrix elements used for the test are all
  equal to normalized floating point 1.0 and are placed in the upper memory
  (32768.0 and beyond)."
* **A second published number**, for a *different* program: "A simple version
  (taken directly from the 7030 programming example book) requires 15.5
  seconds for 100 x 100 matrices. The timing cost was traceable to the use of
  the more accurate but relatively slow LFT; *+ sequence and the fact that two
  adjacent I-box instructions are executed for each traversal of the inner
  loop." That simple version is in `docs/C22-6578_7030_Programming_Examples_
  Apr61.pdf` and is a *second*, independent oracle for the same problem.
* **Operation mix**: Table 10 has **no MXM16 column**. Silent.
* **Source**: Volume 2, **PDF 10 – 16** (printed 7 – 13), headed "LISTING OF
  MATRIX MULTIPLY PROGRAM", with a test driver; ends `END, BEGIN`.
* **Runnable oracle today?** **Not yet.** The data is self-generated (all
  1.0), so no input deck is needed, and the kernel is `L / * / + / ST` plus
  index arithmetic — all modelled. But the listing calls `GENER` and a test
  harness, is 7 pages, and the "major inner loop" is unrolled 17 ways. This
  is the **best candidate of the five** once `*` with its Table 2 execution
  cycles is trusted, and the right unit of work is one 25 x 25 run at
  0.20 s = 200,000 µs ≈ 666,667 model clocks.

### PRIMC — prime number generation  [printed p. 4-4, PDF 46]

* **Problem** (verbatim): "To generate prime numbers by the sieve of
  Eratosthenes, using VFL arithmetic and automatic program interruption."
* **Problem size**: "In a very large memory segment (octal 17740.40 through
  octal 272777.63), consecutive bits represent consecutive odd integers." /
  "The largest prime is (52,307,665)₈, or about 11 million."
* **Published time**: "Timing — 106.7 Seconds", and "A slight change in the
  inner loop (replacing the progressive indexing by ordinary indexing and
  adding a V + I instruction) leads to 102.7 seconds."
* **The manual's own warning** (verbatim): "It is to be noted that 2/3 of the
  program consists of an interruption table."
* **Operation mix**: Table 10 has **no PRIMC column**. Silent.
* **Source**: Volume 2, **PDF 18 – 21** (printed 15 – 18), headed "LISTING OF
  PRIME NUMBER PROGRAM PRIMC"; ends `END, PRIMC`.
* **Runnable oracle today?** **No, and it is the worst candidate of the five
  despite being the shortest.** Its listing opens
  `'THIS VERSION USES BOUNDARY CONTROL FEATURE OF THE 7030`, its first 2/3 is
  literally a table of `SIC, SICK` / `BEW, $` pairs (the interrupt vector),
  and its loop exit is "When the prescribed upper memory boundary is exceeded,
  an interruption causes exit from the loop." The model has no interrupt
  system. The program cannot terminate without one.

### A Monte Carlo program  [printed pp. 4-5/4-6, PDF 47/48]

* **Problem**: particles through a right-angle bent pipe; "The physics and
  method of solution of the problem is described by Davis, *Journal of Applied
  Physics*, 1960."
* **Published time** (verbatim): "10,000 particles were run and the measured
  time was 33 seconds. This is to be contrasted with a known 709 run of 5000
  particles in 10 minutes."
* **The disqualifier, printed on the same page**: "For the machine run 20
  cards had to be loaded and 36 numbers were printed on line."
* **Operation mix**: Table 10 has no Monte Carlo column. Silent.
* **Source**: Volume 2, **PDF 22 – 36** (printed 19 – 33), headed "LISTING OF
  MONTE CARLO PROGRAM"; ends `END, START`. The listing contains `CCW, PRNT,
  CWB` and `CW(CDSC), PBUF, 12, $+1.` — card reader and printer channel words.
* **Runnable oracle today?** **No.** It needs a card reader with the right 20
  cards (which the manuals do not print), a printer, a random number source,
  and `SRT`/`/`. 15 pages of source.

### Weather forecasting study  [printed pp. 4-6 .. 4-8, PDF 48 – 50]

This is the only benchmark Table 10 actually breaks down, and it is the only
one with **no source in Volume 2**. (Checked mechanically: the five
`LISTING OF ...` headings in Volume 2 are GERB2, matrix multiply, PRIMC and
Monte Carlo. There is no weather listing, and Vol. 1 never says "See
Volume 2" for it.)

Inner-loop times, verbatim [printed p. 4-6, PDF 48 and p. 4-7, PDF 49]:

> 1. First form (AO, see below), lower memory: 6.4 ms.
> 2. Pseudo j-level (see below), lower memory: .7 ms.
> 3. AO, upper memory: 6.13 ms.
> 4. AO, lower (instructions) & upper (data) memory: 5.98 ms.
> 5. Second form (A1, see below), lower (instructions) and upper (data) memory: 5.57 ms.
> 6. A1 Modified (see below), lower (instructions) and upper (data) memory: 7.045 ms.
> 7. Third form (A2, see below), lower (instructions) and upper (data) memory: 7.0135 ms.

> The above times for runs 1, 3, 4, 5 are for one pseudo j-level, two
> i-levels, and three k-levels per i-level. The time for run No. 2 is for one
> pseudo-j-level only, and the times for runs Nos. 6 and 7 are for greatly
> reduced pseudo-j-level, one i-level, and nine k-levels.

> AO: Coding prior to any changes for timing improvement.
> A1: Same as AO except for coding changes to improve timing with respect to
> accumulate multiply, division, add to memory, separation of indexing
> instructions, loop entry, CNOP, one-word transmits, and associated minor
> changes.
> A2: Same as A1 Modified except for additional coding changes to improve
> timing with respect to spacing of store instructions, and
> more-than-one-word transmits.

> Grid Parameters ... Using N = 3, lower memory: 7.07 ms

> Elementary Function Test — ln(eˣ) is compared against x, then a polynomial
> evaluation of e^(ln x) is compared against x. The evaluations are based on
> 8-decimal accuracy subroutines, employing polynomial methods. The program
> uses lower memory exclusively.

> In the following chart, certain similar operations have been grouped
> together (e.g., / and R/; V+, V-, V+I, V-I; +, M+ under Fl. Pt.). Also, the
> time given for AO is that for the more favorable memory arrangement (i.e.,
> instructions in lower, data in upper).

Note what that last sentence does to Table 10: the `A0` column's 5.98 ms is
**run 4**, not run 1's 6.4 ms. And it tells you Table 10's operation *names*
are **buckets**, not opcodes: the `Fl. Pt. +` count includes `M+`, the
`Indexing V+` count includes `V-`, `V+I` and `V-I`, and the `Fl. Pt. /` count
includes `R/`. A per-instruction check against Table 10 is therefore not
possible without un-bucketing.

**Runnable oracle today?** **No — there is no source.** Table 10's weather
columns are the richest operation mixes in either volume, but with no listing
they can only be used as a *statistical* check: feed the model the mix and see
whether Σ(count × modelled time) lands near the published ms. That check is
worth doing — see §4.3 — but it is not an execution oracle.

## 3.3 Which of the five are runnable oracles for a STRAP-executing model

| Benchmark | Source in Vol. 2 | Self-contained data | Needs I/O | Needs interrupts | Needs unimplemented ops | Verdict |
|---|---|---|---|---|---|---|
| GERB2 | PDF 4–8 | yes (Hilbert, generated) | no | no | `DL`, `D/`, `*+`, `SRD`, `SVA`, `T` | **No** — all of double precision away |
| MXM16 | PDF 10–16 | yes (all 1.0) | no | no | `LFT` in the "simple version" only | **Closest to runnable** |
| PRIMC | PDF 18–21 | yes | no | **yes — it cannot exit without one** | boundary control | **No** |
| Monte Carlo | PDF 22–36 | **no — 20 cards** | **yes (reader + printer)** | no | `SRT`, `/` | **No** |
| Weather | **none** | n/a | n/a | n/a | n/a | **No source at all** |

## 3.4 The oracle the two volumes actually deliver: Volume 2's instruction timing atlas

**This, not the five benchmarks, is the executable oracle in these volumes.**
PDF 37 – 189 is a per-instruction, per-condition measured timing atlas: about
150 landscape pages, one instruction per page, each with up to ten columns of
operand placement x indexing and up to 48 rows of data description.

### What produced the numbers — quote it before using one

[PREFACE, printed p. 34, PDF 37]

> The following are representative times of 7030 instructions. They will be
> updated when more information becomes available.

> INSTRUCTION SEQUENCE GENERATION AND TIMING / A subroutine (GENER) was
> written to handle the generation of a long sequence of instructions, the
> execution of that sequence, the calculation of execution time, and the
> conversion and printing of that time.

> It picks up the instruction at A, determines if it is full or half word,
> determines if it is a branch type instruction, "ors" in both masks, stores
> the instruction, and reduces the count B. It then updates A by a full or
> half word and cycles till the count B is zero. This series is then
> reproduced until a thousand instructions are available after which a count
> branch (with an original count of 10) is inserted.

**So every number in the atlas is a per-instruction THROUGHPUT, measured over
a thousand-instruction straight-line sequence run ten times, not an isolated
instruction's latency.** It therefore already contains the look-ahead overlap,
the I-box decode overlap and the memory interleave. A model without a
look-ahead cannot match it; a model with one should.

### What the columns mean  [VFL TIMING, printed p. 106, PDF 113]

> The page heading gives the name of the instruction and conditions under
> which it was tested. Each line represents a variation in operand data
> definition, as shown in the left-hand column. Each column of figures
> represents a variation of operand placement; external memory, external with
> word boundary crossover, I-box, internal (accumulator), and internal with
> word boundary crossover. The columns are then repeated for the case of
> operand indexing. Here the effective address was modified by an index
> register containing zero.

> A standard operand (444 .......4)₁₆ was used for both binary and decimal
> type operations. For data-signed operations this would be interpreted as
> +(44444 ....4)₁₆. Exceptions ... For add (+) the accumulator was initially a
> low order +1, and the memory operand +(444 ...4)₁₆. This provided for
> continual recomplementation where the sign of the instruction was inverted
> (subtract). For add to memory (n+) the accumulator was initially
> +(444 ....4)₁₆ and the memory operand +1, again to provide for
> recomplementation. For multiply (*), multiply and add (*+) and divide (/)
> the accumulator and factor registers initially contained the standard
> operand and the memory operand was +1. ... Finally, for convert (CV) and
> convert double (DCV) the accumulator was originally +1 at offset 20.

> There are some cases where a number enclosed in asterisks was printed
> instead of a time in microseconds. These numbers show that an indicator has
> come on during the execution which would invalidate the results. The bit
> position of this indicator bit is displayed. Specifically, *01* shows an
> instruction check reject.

[COMMENTARY ON VFL INSTRUCTIONS, printed p. 108, PDF 115]

> 1. All VFL instructions require an operation code LA level.
> 2. All VFL "to memory" operations require memory fetches.
> 3. The number of LA data levels are doubled whenever word boundary
>    crossover is present.
> 4. VFL stores with word boundary crossover involves a "sequential store"
>    situation. The second store level cannot be loaded into LA until the LAAR
>    is no longer busy processing the first store level.
> 5. The word "forwarding" is being used in the same context as for floating
>    point instructions, meaning identical operand address. Actual fetch-type
>    forwarding action is possible only for consecutive fetch-type VFL
>    instructions with no word boundary crossover. "Store-close-to-fetch"
>    forwarding is present for consecutive "to memory" VFL instructions with
>    no word boundary crossover.
> 6. The error marks on divide instructions (pp. 127, 154, 177) are due the
>    use of a zero divider.

[COMMENTARY ON INDEX ARITHMETIC INSTRUCTIONS, printed p. 101, PDF 108]

> These were timed with external, internal and index operands both with and
> without indexing of the operand addresses.

> The external operands refer to the two lowest memory boxes. The internal
> operands refer to locations 7.0, 8.0 and 9.0.

> Conditional refill operations were tested for both conditions.

> In the LVS instruction the answer is placed in the location of one of the
> summands.

> The instructions LVE and SVA were timed for all three sizes of the address
> field: 18, 19, and 24 bits.

> In SX, no memory fetch is necessary. This is not true for SV, SC and SR.
> This explains the large difference in timing.

> All successful refill action requires memory fetches. All direct index
> arithmetic instruction except SX require memory fetches. No memory fetch is
> required for immediate index arithmetic.

> Concurrent E-box activity can overlap much of the I-box time. This is, of
> course, not possible if the LA is empty. The RNX instruction requires the
> draining of LA.

### Atlas page index (read off the OCR page separators, then spot-verified)

| PDF | Contents |
|---|---|
| 37 | PREFACE; GENER method |
| 38–39 | GENER's branch handling and panel |
| 40–41 | FLOATING POINT TIMING — method, and the page index for the FP pages |
| 42–72 | Floating point, **without** forwarding: `+ D+ K KMG +MG D+MG ST SLO SRD SRT * D* / D/ R/ *+ KR KMGR F+ E+ DL LWF DL DLWF LFT M+ M+MG` |
| 73–101 | The same floating point set, **with** forwarding |
| 102–104 | ENVIRONMENTAL TIMING — method and the FP environmental test |
| 105 | COMMENTARY ON TRANSMIT INSTRUCTION |
| 106–107 | TRANSMIT tables (EM/INTERNAL/I-BOX × EM/INTERNAL/I-BOX) |
| 108 | COMMENTARY ON INDEX ARITHMETIC INSTRUCTIONS (printed 101) |
| **109** | **I-BOX INSTRUCTIONS** (printed 102) — transcribed in §4.2 |
| 110 | `LVS` with J field equal / not equal to index operand |
| 111 | BRANCH INSTRUCTIONS commentary |
| 112 | BRANCHING `CB`, `BIND`, no forwarding, direct addressing |
| 113–115 | VFL TIMING method and COMMENTARY ON VFL INSTRUCTIONS |
| 116–142 | VFL, **no forwarding**, one instruction per page |
| 143–169 | VFL, **forwarding**, one instruction per page |
| 170–189 | VFL **immediate**, one instruction per page |

This index is derived from the OCR page headings and was spot-verified on
PDF 37, 108, 109, 113, 115 and 117. Treat the ranges as a finding aid; verify
the exact page before citing a number from one.

## 3.5 Worked example of the atlas as an oracle: VFL `M+`  [printed p. 110, PDF 117]

This is the page `StretchTiming.bsv` already cites for its x/y correction, so
it is the natural regression target. Heading, verbatim:

> `VFL INSTRUCTION  M+`  `NO FORWARDING`  `DIRECT ADDRESSING`  `OFFSET 0`
> `INSTRUCTION AT FULL WORD ADDRESS`

Column group headings, verbatim: `NO INDEXING` and `INDEXING`, each over
`EXTERNL OPERAND`, `EXTERNL WB XOVR`, `I-BOX OPERAND`, `INTERNL OPERAND`,
`INTERNL WB XOVR`. (The INTERNL columns are blank on this page.) Row labels
are data descriptions `(mode, field length, byte size)`. A second block
repeats every row under `INVERT SIGN OF INSTRUCTION`. `PF` appears in the
right margin of four rows.

First block, read at 300 dpi off PDF 117 (microseconds):

| (mode,FL,BS) | ext. operand | ext. WB XOVR | I-box operand | idx ext. operand | idx ext. WB XOVR | idx I-box operand |
|---|---|---|---|---|---|---|
| (BU,1,8) | 6.63 | | 10.88 | 6.92 | | 11.48 |
| (BU,8,8) | 6.63 | 15.96 | 10.88 | 6.92 | 15.97 | 11.48 |
| (BU,16,8) | 6.93 | 16.56 | 11.48 | 7.23 | 16.57 | 12.09 |
| (BU,32,8) | 7.84 | 17.76 | 12.69 | 7.84 | 17.77 | 13.30 |
| (BU,48,8) | 9.02 | 18.97 | 13.90 | 9.03 | 18.98 | 14.51 |
| (BU,64,8) | 9.61 | 19.57 | 14.51 | 9.62 | 19.58 | 15.11 |
| (B,1,1) | 6.63 | | 10.88 | 6.93 | | 11.48 |
| (B,8,1) | 6.93 | 16.56 | 11.48 | 7.23 | 16.57 | 12.09 |
| (B,16,1) | 7.23 | 17.16 | 12.09 | 7.53 | 17.17 | 12.69 |
| (B,32,1) | 8.42 | 18.36 | 13.29 | 8.44 | 18.38 | 13.90 |
| (B,48,1) | 9.61 | 19.57 | 14.51 | 9.62 | 19.58 | 15.11 |
| (B,64,1) | 10.80 | 20.78 | 15.72 | 10.81 | 20.79 | 16.32 |
| (DU,4,4) | 6.63 | | 10.88 | 6.92 | | 11.48 |
| (DU,8,4) | 6.93 | 16.56 | 11.48 | 7.23 | 16.57 | 12.09 |
| (DU,16,4) | 7.84 | 17.77 | 12.69 | 7.84 | 17.77 | 13.29 |
| (DU,32,4) | 10.21 | 20.17 | 15.11 | 10.22 | 20.18 | 15.72 |
| (DU,48,4) | 12.60 | 22.58 | 17.53 | 12.60 | 22.59 | 18.13 |
| (DU,64,4) | 14.40 | 24.39 | 19.34 | 14.40 | 24.40 | 19.94 |
| (D,4,4) | 6.63 | | 10.88 | 6.93 | | 11.48 |
| (D,8,4) | 6.93 | 16.56 | 11.48 | 7.23 | 16.57 | 12.09 |
| (D,16,4) | 7.84 | 17.76 | 12.69 | 7.84 | 17.77 | 13.29 |
| (D,32,4) | 10.21 | 20.17 | 15.11 | 10.22 | 20.19 | 15.72 |
| (D,48,4) | 12.60 | 22.58 | 17.53 | 12.60 | 22.59 | 18.13 |
| (D,64,4) | 15.01 | 24.99 | 19.94 | 15.00 | 25.00 | 20.55 |

(The `INVERT SIGN OF INSTRUCTION` block is on the same page and is
transcribed into the machine-readable file in §4.)

**What this says about the model.** `StretchTiming.budgetClocks` for a
`VflInt M+` is `2 × (6 + idx) + (8 + 2 × ceil(x/y))` clocks at 0.3 µs, i.e.
3.6 µs preparation + 2.4 µs (pre-execution + termination) + 0.6 µs per byte.
For `(BU,64,8)` that is 10.8 µs against a published 9.61; for `(BU,8,8)` it is
6.6 against 6.63; for `(BU,1,8)` 6.6 against 6.63. The model is **exact at one
byte and increasingly slow as the field grows**, which is what you expect from
charging the SAU's per-byte time *serially* when the real machine overlaps the
tail of one instruction's execution with the next one's preparation. That gap
is the look-ahead, and it is the §5 item the Stage-3 work has to close.
Indexing costs the real machine **0.29–0.30 µs**, i.e. one *clock*, not the
0.6 µs (one I-box cycle) the model charges — but p.3-18 says plainly "each
indexing operation requires 0.6 µs", so the throughput figure and the decode
figure disagree and **the manual does not reconcile them**.

## 3.6 Two more measured pages that settle open model constants

### V2 BRANCHING  [printed p. 105, PDF 112]

Heading, verbatim: `BRANCHING CB BIND   NO FORWARDING   DIRECT ADDRESSING
INSTRUCTION AT FULL WORD ADDR`. Column groups `NO INDEXING` and
`BRANCH ADDRESS INDEX`, each over `SUCCES CONSEC`, `UNSUCC CONSEC`,
`SUCCES NONCON`, `UNSUCC NONCON`.

Conditions [printed p. 104, PDF 111], verbatim:

> "Consecutive" means that each instruction called for a branch to the next
> instructions. "Non-consecutive" means that the branch was to a location from
> one to four instructions from the one being executed.

> For CBR type, the "success" refers to a successful refill in which the
> register is refilled with its original contents. A one was in the count
> field. For an unsuccessful CBR the branch was unsuccessful and thus no
> refill. The original count in the count field in this case was greater than
> 10,000.

> The right-most four columns of data involved indexed addresses.

| Instruction | succ consec | unsucc consec | succ noncon | unsucc noncon | ix succ consec | ix unsucc consec | ix succ noncon | ix unsucc noncon |
|---|---|---|---|---|---|---|---|---|
| CB  CBZ | 4.82 | 4.52 | 4.82 | 4.52 | 5.12 | 5.12 | 5.12 | 5.12 |
| CB+ CBZ+ | 4.82 | 4.52 | 4.82 | 4.52 | 5.12 | 5.12 | 5.12 | 5.12 |
| CB- CBZ- | 4.82 | 4.52 | 4.82 | 4.52 | 5.12 | 5.12 | 5.12 | 5.12 |
| CBH CBZH | 4.82 | 4.52 | 4.82 | 4.52 | 5.12 | 5.12 | 5.12 | 5.12 |
| CBR | 11.14 | 4.52 | 11.14 | 4.52 | 11.44 | 5.12 | 11.44 | 5.12 |
| CBR+ | 11.14 | 4.52 | 11.14 | 4.52 | 11.44 | 5.12 | 11.44 | 5.12 |
| CBR- | 11.14 | 4.52 | 11.14 | 4.52 | 11.44 | 5.12 | 11.44 | 5.12 |
| CBRH | 11.14 | 4.52 | 11.14 | 4.52 | 11.44 | 5.12 | 11.44 | 5.12 |
| **BIND, I-BOX IND:** `BXL BZXL` | 4.52 | 2.26 | 4.52 | 2.26 | 4.67 | 2.86 | 4.67 | 2.86 |
| **BIND, ARITH RESULT IND:** `BAL BZAL` | 19.78 | 7.20 | 19.78 | 7.20 | 20.08 | 7.21 | 20.08 | 7.21 |

**This is the page that quantifies the not-taken guess.** A branch on an
*index* indicator — resolved in the I-box, which is exactly the set the plan
§6d calls "resolved in the I-box from the UIR" — costs 4.52 µs taken and
2.26 µs untaken. A branch on an *arithmetic result* indicator costs **19.78 µs
taken and 7.20 µs untaken**. The 12.58 µs difference is the measured price of
the guess being wrong. `StretchTiming.bsv` charges a flat 3.6 µs
(`tagged BranchInd .*: return 6`) for *both kinds*.

CB's measured 4.82 µs against Table 8's 4.2 + dec = 4.8 is a 0.02 µs
agreement. CBR's measured 11.14 against Table 8's CBR(EM) 6.6 + dec = 7.2 is
not — the atlas's CBR "success" is a refill *from external memory with the
LA involved*, and Table 8's is the I-box time only.

### V2 TRANSMIT  [printed p. 99, PDF 106], and what it settles about Table 9

Conditions [printed p. 98, PDF 105], verbatim:

> The transmit instructions were timed with the external operands in the two
> lowest memory boxes and the internal operands in locations 4.0 through 9.0.
> The index operands were in $2 through $14 (18.0 through 30.0).

> LA is emptied before the actual transmission of information.

Rows are word counts. Columns verbatim: `EXTERNAL TO EXTERNAL`,
`EXTERNAL TO INTERNAL`, `EXTERNAL TO I-BOX`, `INTERNAL TO INTERNAL`,
`INTERNAL TO EXTERNAL`, `INTERNAL TO I-BOX`, `I-BOX TO I-BOX`,
`I-BOX TO EXTERNAL`, `I-BOX TO INTERNAL`.

| words | ext→ext | ext→int | ext→I-box | int→int | int→ext | int→I-box | I-box→I-box | I-box→ext | I-box→int |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 13.84 | 13.85 | 13.28 | 14.47 | 14.47 | 13.28 | 13.28 | 13.85 | 13.85 |
| 3 | 19.89 | 19.90 | 21.69 | 14.47 | 14.47 | 13.28 | 13.28 | 13.85 | 13.85 |
| 5 | 25.94 | 25.94 | 30.16 | 14.46 | 14.47 | 13.28 | 13.28 | 13.85 | 13.85 |
| 7 | 31.97 | | 38.58 | | | | 13.27 | 13.85 | |
| 9 | 37.99 | | 47.00 | | | | 13.27 | 13.85 | |
| 11 | 43.99 | | 55.46 | | | | 13.27 | 13.85 | |
| 13 | 50.04 | | 63.87 | | | | | 13.85 | |
| 15 | 56.07 | | | | | | | | |

**This settles — by arithmetic, not by quotation — what Table 9's "Loop time"
covers.** The ext→ext column rises 13.84, 19.89, 25.94, 31.97, 37.99, 43.99,
50.04, 56.07 over 1, 3, 5, 7, 9, 11, 13, 15 words: a slope of 6.04 µs per two
words, i.e. **3.02 µs per word**, against Table 9's 3.0 µs `T (EM → EM)` loop
time. So the loop time is per word. The manual itself remains silent; this is
an inference from the slope and is labelled as one.

(The index-storage and I-box columns are flat at ~13.3–13.85 regardless of
word count, which is what you expect of a register-to-register transmit whose
cost is dominated by the LA drain p.98 describes.)

---

# 4. THE EXECUTABLE ARTIFACT

## 4.1 Why not a transcribed benchmark

**No benchmark printed in these two volumes is worth transcribing into a deck
today, and §3.3 gives the reason for each.** In summary: PRIMC is the shortest
(4 pages) but its loop *exit is an interrupt* and two-thirds of its listing is
an interrupt vector; Monte Carlo needs twenty punched cards whose contents are
printed nowhere; GERB2's inner loop is `DL` / `D/` — double-precision divide —
and it also wants `*+`, `SRD`, `SVA` and `T`; the weather program
has no listing at all; and MXM16, the best candidate, is a seven-page
GENER-driven harness whose smallest published point (25 x 25 in 0.20 s) is
666,667 model clocks of simulation. Transcribing seven pages of STRAP by hand,
off a 1961 scan, to produce one number that the model would fail anyway for
want of a look-ahead, is not the best use of this source.

So this deliverable takes the task's stated alternative: **a machine-readable
per-instruction timing table**, plus one small constructed deck.

## 4.2 `perf_char_timing.py` — the machine-readable table

In this directory. It is an importable Python module (it imports clean; see
the smoke test at the end of this section) with every number above, each
carrying its own `src` string naming the PDF page. Contents:

| Name | What |
|---|---|
| `CLOCK_US`, `DEC_US`, `FP_DECODE_RATE_US`, `VFL_DECODE_*`, `IBOX_EBOX_TIME_US`, `MEMORY_*`, `INTERLEAVE_*` | §2's quoted constants |
| `TABLE2`, `TABLE2_NOTE1`, `TABLE2_NOTE2` | Table 2, as structured pre/exec cycle counts with their conditions and extras as strings |
| `TABLE3`, `TABLE3_GLOSSARY`, `TABLE3_SIGNED_RULE` | Table 3's 32 rows, its glossary verbatim, and the signed-operation rule |
| `TABLE4` … `TABLE9_SWAP` | the I-box tables, in µs *before* `dec`, with the symbolic `LAAR`/`LAdr`/`LAMT` addends kept as strings |
| `TABLE6_EX_FETCH_US`, `TABLE6_EX_RECIPE`, `TABLE6_EXIC_RECIPE` | `EX` and `EXIC`, which are recipes rather than numbers |
| `TABLE10`, `TABLE10_GRAND_TOTAL`, `TABLE10_EXEC_TIME_MS`, `TABLE10_AVG_US_PER_OP`, `TABLE10_DEFECTS`, `TABLE10_BUCKETS` | the Execution Frequency Chart and its three arithmetic defects |
| `BENCHMARKS` | the five programs: published times, sizes, source page ranges, and a `blockers` list |
| `V2_IBOX`, `V2_VFL_MPLUS`, `V2_VFL_MPLUS_INVERT_SIGN`, `V2_VFL_C0011`, `V2_BRANCH`, `V2_TRANSMIT` | Volume 2's **measured** atlas pages, with `V2_METHOD` and `V2_CAVEAT` beside them |
| `check_connective_byte_count()` | the §5.2 C5 check, runnable: `python3 perf_char_timing.py` |
| `stretch_timing_ibox_us`, `stretch_timing_sau_us` | the two formulae `StretchTiming.bsv` implements, in Python, so a test can diff |

A future test asserts instruction by instruction, e.g.

```python
import perf_char_timing as pc
assert pc.TABLE8["CB (Successful)"][0][0] + pc.DEC_US == 4.8   # model: 8 I-box cycles
assert pc.V2_BRANCH["BAL BZAL"][0] == 19.78                    # model: 3.6 -- WRONG
ok, n, outliers = pc.check_connective_byte_count()
assert (ok, n) == (34, 35)                                     # model: right shape
```

Run in this session:

```
$ python3 perf_char_timing.py
connective byte count: 34/35 rows at a constant 2.40 us offset
  outlier: (('BU', 32, 1), 32, 25.200000000000003, 13.2, 12.0)
```

Smoke test run in this session:

```
$ python3 -c "import perf_char_timing as m; print(len(m.V2_VFL_MPLUS), len(m.V2_IBOX), len(m.V2_BRANCH))"
24 26 10
```

## 4.3 `vfl_mplus_sau_timing.strap` — one constructed deck

In this directory. A sixteen-deep straight-line body of
`M+(BU,8,8), OPND, 0` inside a count-branch loop, in the style of
`decks/ibox_timing_cb.strap`. Its header carries the full derivation. The
number it is against:

> **Volume 2 printed p. 110, PDF 117, `VFL INSTRUCTION M+`, row `(BU,8,8)`,
> column `NO INDEXING / EXTERNL OPERAND`: 6.63 µs per instruction.**

and the model's own budget for that instruction is
`3.6 µs (VFL decode, p.3-18) + 1.8 + 0.6 × 1 + 0.6 µs (Table 3's M+) = 6.6 µs
= 22 clocks`. 6.6 against 6.63 — this is the one data description where the
model's serial budget and IBM's measured throughput agree, which is what makes
it a regression test rather than a wish. The deck's suggested `CYCLES<=` bound
is 4150 clocks; the derivation is in the deck's own header so a future change
to `dec`, to the VFL preparation or to the SAU byte count moves the number
visibly.

**It is labelled in the file as a constructed deck, not a transcription.**
Nothing in either volume prints this program.

---

# 5. AUDIT OF `bsv/StretchTiming.bsv` AGAINST THESE TWO VOLUMES

The file's own comment says its numbers come from "the Performance
Characteristics tables 4-8 ... table 2's E-box cycles ... table 3's SAU
equation". Here is every number in it, checked.

## 5.1 CONFIRMED — the number is right and the page says so

| `StretchTiming` | value | means | source |
|---|---|---|---|
| one clock = 0.3 µs (in `oscPulseDenom`'s comment) | 0.3 µs | basic machine cycle | **confirmed verbatim**, printed p.3-2, PDF 20 |
| `DirIndex 5'b00001` (LX) | 9 cycles = 5.4 µs | 4.8 + dec | Table 4, PDF 29 |
| `DirIndex 5'b10001` (SX) | 3 = 1.8 µs | 1.2 + dec | Table 4 (the `+ LAAR` is dropped; no number exists for it) |
| `DirIndex 5'b01111` (V+CR) | 15 = 9.0 µs | 8.4 + dec | Table 4, **the `V+CR (EM)` row** |
| `DirIndex default` | 8 = 4.8 µs | 4.2 + dec | Table 4: LV/LC/LR, SV/SC/SR, V+, V+C, KV/KC all 4.2 in the EM column |
| `ImmIndex 0110/1110` (V±IC) | 6 = 3.6 µs | 3.0 + dec | Table 5, PDF 29 |
| `ImmIndex 0111/1111` (V±ICR) | 13 = 7.8 µs | 7.2 + dec | Table 5 |
| `ImmIndex default` | 5 = 3.0 µs | 2.4 + dec | Table 5: LVI/LCI/LRI/LVNI, V±I, C±I, KVI/KVNI/KCI |
| `CountBranch refill==1` | 12 / 11 = 7.2 / 6.6 µs | 6.6 / 6.0 + dec | Table 8, **the CBR (EM) rows**, PDF 32 |
| `CountBranch refill==0` | 8 / 7 = 4.8 / 4.2 µs | 4.2 / 3.6 + dec | Table 8, CB Successful / Unsuccessful. Independently confirmed by V2 PDF 112's measured 4.82 / 4.52 |
| `BranchOrMisc misc 3'b100` (Z) | 3 = 1.8 µs | 1.2 + dec | Table 6 EM, PDF 30 |
| `BranchOrMisc misc 3'b001` (RCZ) | 8 = 4.8 µs | 4.2 + dec | Table 6 EM, `RCZ (C ≠ 0)` |
| `BranchOrMisc misc default` (R) | 14 = 8.4 µs | 7.8 + dec | Table 6, **`R (from EM)` EM column** |
| `BranchOrMisc 3'b110` (NOP) | 3 = 1.8 µs | 1.2 + dec | Table 7, PDF 31 |
| `BranchOrMisc 3'b011` (BR) | 9 = 5.4 µs | 4.8 + dec | Table 7 |
| `BranchOrMisc default` (B/BE/BEW) | 7 = 4.2 µs | 3.6 + dec | Table 7 |
| `Fp` preparation | 2 cycles = 1.2 µs | FP decode rate | printed p.3-17, PDF 35 — **better sourced than the file's "Blosk fig.6"** |
| `VflInt` / `Connective` | 6 + (indexed ? 1 : 0) cycles = 3.6 + 0.6 µs | VFL decode minimum + per indexing operation | printed **p.3-18**, PDF 36 — the file and the plan both cite p.3-17; the sentence is on p.3-18 |
| `eboxClocks VflInt` shape | 8 + 2·bytes clocks = 2.4 + 0.6·bytes µs | pre 1.8 + .6(x/y) + term .6 | Table 3, PDF 25 |
| `x` and `y` in `eboxClocks` | field length (or minus byte size if signed); 8 in binary, byte size in decimal | | **confirmed verbatim** against the Glossary of Terms, printed p.3-10, PDF 28 |
| `dec` = 0.6 µs everywhere | 0.6 µs | | printed **p.3-18**, PDF 36, "The decoding time of I-box instructions is 0.6 microsecond". Tables 4-8 themselves only say `dec = decade` |

## 5.2 CORRECTED — the number or the comment is wrong

**C1. `eboxClocks` returns a flat `3` for every floating point instruction.**
The arm reads `tagged Fp .*: return 3;` with the comment
`// preparation; E-box cycles added below` — a comment copy-pasted from
`iboxCycles`, where there *is* no "below". Table 2 gives distinct
pre-execution + execution cycles per instruction:

| instruction | Table 2 pre + exec (minimum) | model |
|---|---|---|
| `L`, `LWF`, `LFT`, `ST` | 2 + 1 = **3** | 3 ✓ |
| `+`, `+MG`, `M+`, `M+MG`, `K`, `KMG`, `KR`, `KMGR` | 4 + 1 = **5** | 3 ✗ |
| `SRD` | 3 + 1 = **4** | 3 ✗ |
| `SHF` | 4 + 1 = **5** | 3 ✗ |
| `E+`, `E+I` | 1 + 5 = **6** (and Note 2 says this will become 3 + 3) | 3 ✗ |
| `*` | 5 + 4 = **9** | 3 ✗ |
| `*+` | 3 + 17 = **20** | 3 ✗ |
| `SLØ` | 2 + 15 = **17** (normalized) or 2 + 17 = 19 | 3 ✗ |
| `/` | 2 + 2 = **4** plus data-dependent reduction loops | 3 ✗ |
| `SRT` | 2 + 106 = **108** | 3 ✗ |

**So every FP E-box time in the model except the load/store class is a
placeholder**, and the error is largest exactly where the benchmarks spend
their time: Table 10's A0 column has 220 `*` and 88 `/` out of 1364 FP
operations. This is the single biggest correction the two volumes produce.

**C2. `tagged BranchInd .*: return 6;` charges 3.6 µs for every
branch-on-indicator, taken or not, index or arithmetic.** V2 printed p.105,
PDF 112, measures four distinct numbers: index-indicator branch **4.52 µs
taken / 2.26 µs not taken**; arithmetic-indicator branch **19.78 µs taken /
7.20 µs not taken**. The file's comment cites "Blosk fig.10: decode + 5
execution cycles" — that is not from these volumes, and these volumes
contradict it.

**C3. `tagged Sic .x: return 2 + iboxCycles(...)` charges a flat +1.2 µs for
SIC.** Table 7 (PDF 31) does give +1.2 for `B` (3.6 → 4.8), `BR` (4.8 → 6.0),
`BD` (4.8 → 6.0) and `BE` in the `SIC to EM` column. But the same table gives
`NOP`: "Same as Basic", i.e. **+0**; and Table 8 (PDF 32) gives `CB
(Successful)` 4.2 → **6.6**, i.e. **+2.4**, `CBR (EM) (Succ)` 6.6 → 9.0,
**+2.4**, while `CB (Unsuccessful)` and both `CBR ... (Unsucc)` rows are
unchanged, **+0**. So the flat +1.2 is right for Table 7's branches and wrong
for NOP and for every Table 8 row.

**C4. `tagged Transmit .*: return 7;` (4.2 µs) is low by at least half.**
Table 9 (PDF 32) gives `T (EM → EM)` setup 1.2 + dec + LA dr, loop 3.0,
termination 3.6 — **8.4 µs + one LA drain for a single word**, before the LA
drain is costed at all. V2 PDF 106 measures a one-word external-to-external
transmit at **13.84 µs**. The file's comment cites "Blosk fig.9: 2 set-up + 5
per word"; Table 9 and the V2 measurement both say otherwise, and the V2
column's 3.02 µs-per-word slope confirms Table 9's loop time is per word.

**C5. The `Connective` comment is factually wrong on two counts — but its
ARITHMETIC IS RIGHT, and this source proves it to within 0.01 us.**

The comment says Table 3's "instruction list ... does not include them" and
"Vol. 2 has no connective page either: its 66 instruction headers are all VFL
arithmetic". *Both of those claims are false:*

* Table 3 prints `C`, `CM` and `CT` on printed p. 3-8 (PDF 26), each with
  pre-execution 1.8, execution `.6(x/y)`, termination .6, Full Word Total
  7.2 us — the same row shape as `L` and `ST`.
* Volume 2 **does** have connective pages. `VFL INSTRUCTION C(0011)` is
  printed p. 133, **PDF 140**, read and transcribed below. Its OCR'd
  neighbours PDF 141 and 142 head `CM(0101)` and `CT(0111)`, and the set
  recurs in the forwarding run (PDF ~167–169) and the immediate run
  (PDF ~188–189) — **those four page numbers are from the OCR headings, a
  finding aid, and were not rendered; only PDF 140 was read.**
* The signed-operation rule on printed p. 3-6 (PDF 24) names `C, CM, CT`
  explicitly among the operations that "require no additional time when
  signed".

So p.3-10's `x` and `y` *do* have a referent for the connectives, and the
obvious reading of the glossary — a connective has no sign modifier and no
decimal mode, so `y` should take its binary branch and be **8** — says the
model's use of the DECLARED byte size is wrong.

**That obvious reading is wrong, and PDF 140 settles it against the glossary.**
`VFL INSTRUCTION C(0011)  NO FORWARDING  DIRECT ADDRESSING  OFFSET 0
INSTRUCTION AT FULL WORD ADDRESS` varies the byte size at fixed field length,
which is exactly the experiment the question needs, and the times *change with
byte size*: `(BU,8,1)` 8.40, `(BU,8,2)` 6.00, `(BU,8,3)` 5.40, `(BU,8,8)`
4.20. If `y` were 8 these four would be equal. They are not.

Taking the model's own formula — VFL decode 3.6 (p.3-18) + Table 3's
1.8 pre + 0.6 term + 0.6 per byte, with `bytes = ceil(field length / DECLARED
byte size)` — against the page's `EXTERNL OPERAND / NO INDEXING` column:

| (BU,FL,BS) | bytes | model µs | measured µs | model − measured |
|---|---|---|---|---|
| (BU,8,1) | 8 | 10.80 | 8.40 | **2.40** |
| (BU,8,2) | 4 | 8.40 | 6.00 | **2.40** |
| (BU,8,3) | 3 | 7.80 | 5.40 | **2.40** |
| (BU,8,4..7) | 2 | 7.20 | 4.80 | **2.40** |
| (BU,8,8) | 1 | 6.60 | 4.20 | **2.40** |
| (BU,16,1) | 16 | 15.60 | 13.20 | **2.40** |
| (BU,16,3) | 6 | 9.60 | 7.20 | **2.40** |
| (BU,16,5) | 4 | 8.40 | 6.00 | **2.40** |
| (BU,32,1) | 32 | 25.20 | 13.20 | 12.00 ← the only outlier |
| (BU,32,3) | 11 | 12.60 | 10.20 | **2.40** |
| (BU,32,7) | 5 | 9.00 | 6.60 | **2.40** |
| (BU,48,3) | 16 | 15.60 | 13.20 | **2.40** |
| (BU,48,5) | 10 | 12.00 | 9.60 | **2.40** |
| (BU,64,5) | 13 | 13.80 | 11.40 | **2.40** |
| (BU,64,7) | 10 | 12.00 | 9.60 | **2.40** |
| (BU,64,8) | 8 | 10.80 | 8.40 | **2.40** |

**Thirty-four of the page's thirty-five rows give `model − measured` = exactly
2.40 µs.** (The full check is reproducible from `perf_char_timing.py`'s
`V2_VFL_C0011`.) A constant offset across eleven distinct byte counts from 1
to 16 is not a coincidence: `ceil(field length / declared byte size)` is the
right byte count for a connective, `StretchTiming.bsv` already has it, and
**the comment that calls it "unsourced" and defers it to `docs/NEXT.md` 5g
should now say it is confirmed on this page.** The glossary's `y` is a rule
for the *arithmetic* operations Table 3 was written around; the connectives
take the declared byte size, and the measurement says so.

Two further findings fall straight out of the same page:

1. **The model over-charges a connective by exactly 2.40 µs = 8 clocks,
   uniformly.** Not a shape error — a constant. That 2.4 µs is the
   preparation the real machine overlaps with the previous instruction's
   execution, i.e. it is precisely the look-ahead credit, and it is the same
   2.4 µs as Table 3's `pre-execution + termination` for this class. A
   stage-3 model that overlaps preparation with execution should close this
   gap to zero on all 34 rows at once, which makes this page the single best
   regression target in either volume for the look-ahead work.

2. **The SAU byte count is capped at 16.** `(BU,32,1)` needs 32 bytes and is
   measured at 13.20 µs — identical to `(BU,32,2)`, `(BU,48,3)` and
   `(BU,64,4)`, all of which need exactly 16. And the page *omits* every
   combination that would need more than 16: there is no `(BU,48,1)` (48
   bytes), no `(BU,48,2)` (24), no `(BU,64,1)`, `(BU,64,2)` or `(BU,64,3)`.
   Sixteen is the width of the SAU's first byte-extraction switch matrix
   (Buchholz fig. 14.6, plan §A.5: "16-of-128 then 8-of-16 switch matrices").
   The manual never states the cap; it is visible only as this hole in the
   table and this one flat row, and it is recorded here as an inference.
   `StretchTiming.bsv` does not cap, and for `(BU,32,1)` it is therefore
   12.00 µs — forty clocks — too slow.

**C6. Citation corrections (the numbers are right, the page is not).** The
VFL "3.6 µs min + 0.6 per level or index" and "dec = 0.6 µs" are both on
printed **p.3-18 (PDF 36)**, not p.3-17 (PDF 35) as `StretchTiming.bsv` and
`docs/microarchitecture_plan.md` §A.6 both say. p.3-17 is the *floating point*
decoding rate (1.2 µs) and memory interleaving. Likewise the plan's §A.7
"2.1 µs read-write cycle" should read **2.2 µs recycle, 1.0 µs readout**
when citing Performance Characteristics (printed p.3-15, PDF 33); and §A.6's
"Up to six instructions in progress" is Blosk's number — this manual says
"up to ten instructions can be in various stages of processing" (printed
p.3-16, PDF 34).

## 5.3 NOT FOUND in either volume

* **`tagged IoOp .*: return 6;`** — neither volume gives an I-box time for any
  I/O instruction. Tables 4–9 cover direct index, immediate index,
  miscellaneous, unconditional branch, index branch and transmit; there is no
  I/O table, and Volume 2's atlas has no I/O page.
* **`default: return 3;`** (the catch-all in `iboxCycles`) — not sourced, by
  construction.
* **`BD`'s "+2 LA drains" costed at 1 I-box cycle each** (`11` rather than
  `9`). Table 7 says `BD` is "4.8 µsec + dec + 2 LA drains" and **the manual
  never gives a number for an LA drain**, here or anywhere. The same is true
  of `LAAR` and `LAMT`, which Tables 4, 6 and 7 add symbolically in fourteen
  places. The model's implicit 0.6 µs per drain is an invention.
* **The I-box control cycle = 2 clocks = 0.6 µs.** Neither volume states it.
  Every I-box number in Tables 4–8 is a multiple of 0.6 µs and p.3-18's decode
  time is 0.6 µs, so the inference is strongly supported — but it is an
  inference, and `StretchTiming.bsv`'s comment "one I-box control cycle = 2
  clocks = 0.6 us as shipped, Perf. Char. p.3-17" attributes it to a page that
  does not say it.
* **The `z` term in Table 3's `+` and `+MG`** (`.6(x/y + z)`), the `w/r` term
  in `K`, `KE` and `KR`, the `+0.6 µs` pre-execution for signed operations,
  the `+0.6 µs` for a complementing result, and every one of Table 3's
  unlike-sign Comments. The model implements none of them. They are *in* the
  source — this is a gap in the model, not in the manual.
* **Per-operation pre-execution times in Table 3 other than 1.8.** `SRD` is
  3.0; `LTRS`, `LFT` and all four convert families are 2.4; `*` is 6.0; `*+`
  is 7.8; `/` is 5.4. The model charges 1.8 to every VFL instruction.

---

# 6. GAP LIST — what cycle accuracy needs that these two volumes do NOT contain

1. **No clock-by-clock sequencer behaviour.** Every number in both volumes is
   an *instruction-level* time: a pre-execution/execution cycle count, a µs
   figure, or a measured throughput. Neither volume shows what happens on a
   given clock. For that the project already has the right sources — the CE
   manuals' I-unit flow diagrams (`docs/jb_ax*_ibox-*.pdf`, figures 3.1.x and
   3.2.x, indexed in plan §6a) and Blosk TR00.722. Performance Characteristics
   is a *budget* document, not a *sequencer* document.
2. **No value for `LAAR`, `LAdr` (look-ahead drain) or `LAMT`.** They appear
   as symbolic addends fourteen times in Tables 4, 6 and 7 and in every row of
   Table 9, and are never quantified. A model cannot charge `BD`, `SX`, `Z`,
   `R`, `RNX`, `EX`, `EXIC` or any transmit correctly without them.
3. **No statement of the I-box control cycle.** See §5.3.
4. **No memory-conflict model.** Printed p.3-17 says only that "memory
   conflict is not expected to be an important factor" and that "Delays due to
   repeated demands of the same memory box are expected to be quite
   infrequent". There is no bus-priority table, no MBCU queueing rule, no
   per-requester latency. (Buchholz §14.3 has those; this manual does not.)
5. **No look-ahead state machine.** The volumes give its *effects* — four
   levels, "the requirement is satisfied if any four E-box demands are
   fulfilled in 6 µs", "the following instructions empty the LA completely:
   T, TI, SWAP, SWAP I, RNX, BD", "All I-box instructions load LA levels for
   index register recovery or for indicator register updating" — but no ring
   counters, no interlocks, no forwarding timing. The forwarding/no-forwarding
   *pairs* of atlas pages (PDF 42–72 vs 73–101, 116–142 vs 143–169) give the
   measured *difference* forwarding makes, instruction by instruction, which
   is the best empirical handle these volumes offer on it.
6. **No interrupt timing.** PRIMC is described as using "automatic program
   interruption" and its 106.7 s is the only interrupt-dependent number
   published, with no breakdown. The manual is silent on interrupt latency,
   on recovery cost, and on the housecleaning sequence.
7. **No I/O timing at all.** No channel times, no device times, no exchange
   priority. Monte Carlo's 33 s includes "20 cards had to be loaded and 36
   numbers were printed on line" with no breakdown.
8. **No weather program source**, so the richest operation mixes in Table 10
   cannot be reproduced.
9. **The numbers are a 1961 model's output, not hardware measurements.**
   Volume 2's PREFACE: "The following are representative times of 7030
   instructions. They will be updated when more information becomes
   available", and the method is a simulator subroutine, `GENER`. Volume 1
   printed p.3-2 says the clock is "presently 0.3 microsecond"; Table 2's
   Note 2 says `E+`/`E+I` "will most likely be changed in the near future".
   **A model that matched these numbers exactly would be matching IBM's March
   1961 projection, not the shipped 7030.** Where the two volumes disagree
   with the CE manuals or with Buchholz, that is the reason, and the CE
   manuals are the later and more authoritative source for the machine as
   built.
10. **Three cells of Table 10 do not add up** (§3.1), so the Execution
    Frequency Chart cannot be used as a self-checking oracle without deciding
    which of its printed numbers to believe.
11. **Table 10's rows are buckets, not opcodes** (printed p.4-8, PDF 50: "/
    and R/; V+, V-, V+I, V-I; +, M+ under Fl. Pt."), so a per-instruction
    assertion against it is not possible without un-bucketing it by hand
    against a source listing that, for the weather program, does not exist.
12. **The SAU's 16-byte limit is never stated.** §5.2 C5 shows it is real —
    the connective page caps at 16 bytes and omits every row that would
    exceed it — but neither volume says so in words, and a model that takes
    its byte count from Table 3's `.6(x/y)` without a cap will be forty
    clocks slow on `(BU,32,1)` and worse on the combinations the page
    declines to print.
13. **Indexing costs 0.6 µs in the decode budget (printed p.3-18) and
    0.29–0.30 µs in the measured throughput (PDF 117's INDEXING columns
    against its NO INDEXING columns).** The two volumes do not reconcile
    these, and the manual is silent on why.
