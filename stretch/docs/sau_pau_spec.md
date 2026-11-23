# The serial and parallel arithmetic units, cycle by cycle: step 0.3

Written 2026-11-23 for `fidelity_plan.md` step 0.3. It covers only the
**arithmetic-unit half** of 0.3: the PAU timing charts (CE §3.8), the SAU
flow diagrams (CE §3.11), Buchholz §14.4, and Perf. Char. Vol. 1 Tables
2-3 as a cross-check. The LA flow diagrams (pp.95, 99-119) and the memory
timing (§4 Procedure 1) are the other half of 0.3 and are **not** here.
No model file was changed.

It exists so that A3 (`mkSAU`) and A4 (`mkPAU`) build from cycle tables
rather than fitted budgets. Every reading is from a page image, never
from OCR alone. OCR (`docs/ocr/`) was used only to find pages.

## 0. How this was read, and what to trust

- **Renders.** Every page was rendered at 300 dpi grayscale (`pdftoppm
  -r 300 -gray`) into a scratch directory and read in tiles of 1350 px or
  less. A fold-out is 5100 × 3300 px. The renders were deleted
  afterwards. Tile names in the appendices (for example `t242_2550_100`
  or `c258_2500_1150`) encode the crop origin in full-page pixels, so any
  reading can be re-cropped.
- **Who read what.**
  - §4's figures were read first-hand by the author: 3.8.15 sheets
    1 and 3, the end of sheet 2, 3.8.16, 3.8.18, 3.11.1, 3.11.8, 3.11.10,
    Buchholz pp.208-216 and Perf. Char. pp.3-3 to 3-10.
  - The other figures were transcribed by five parallel readers (A-E). Their
    transcriptions are Appendices A-E, essentially verbatim.
  - At least one tile of each reader's work was re-read by the author.
    Each agreed with the transcription: 3.8.1's clock and T0/T3 rows;
    3.8.20's preamble; 3.11.4's "CONVERT DEC TO BIN SIGNAL TO PAU" loop;
    3.11.11's "NO WRITE IN AFTER EOC2" note; and for reader B the whole
    of 3.8.9 (PDF 232), re-rendered at 300 dpi after the first commit.
    B's other charts (3.8.10-3.8.14) were not spot-checked.
- **Markings.**
  - PRINTED: what the page says.
  - COUNTED: periods counted off the drawing.
  - DERIVED: an interpretation.
  - ILLEGIBLE: given with its reason.
- **What a chart period is.** One FP CLOCK period is one trigger cycle,
  0.3 µs, and one model clock. This follows `clock_unit.md` §1 and §4.2
  and is re-confirmed here: 3.8.15 sheet 3 NOTE 2 says moving TC under
  END OP "SHORTENS THE OPERATION BY 300 NANOSECONDS".
- **The SAU byte cycle.** Buchholz p.209 gives one byte pair in "one
  clock cycle of 0.6 µsec", which is 2 model clocks. Perf. Char. Table 3
  charges .6 µs per byte. No SAU flow diagram prints any time.

**Counting convention for the cross-checks (DERIVED, tested).** A chart
starts at period 0 (T0), or 1 on the divide sheets, and its length is
counted through the period in which END OP is on. That count is what
Table 2's pre-execution plus execution cycles measure. The LATCH
ACOB/EXP LATCH period after END OP is not counted.

The convention reproduces Table 2 exactly for Load, Store, Compare, Add
to Fraction, FP Multiply and Add to Exponent (§3). That agreement is
the evidence for it.

## 1. Where the figures are: page map and offsets

**There is no single PDF-to-printed offset.** Section 3 is paginated by
category, as section-relative "8-n" and "11-n", and the fold-outs
scramble the printed order. The figure list is Index 3-2 at PDF 52-60;
category list Index 3-1 is at PDF 51. Category 8 is "PAU Timing Charts"
and category 11 is "SAU Flow Diagrams".

**PAU timing charts, category 8, PDF 225-244.** There are **twenty**
figures, not nineteen. Index 3-2 (PDF 58, read at the image) lists
**3.8.20 "Floating Point Reciprocal Divide Timing", 1/1/63**.

| fig | title (as printed) | PDF | printed | issue (foot) | read by |
|---|---|---|---|---|---|
| 3.8.1 | Floating-Point Load | 225 | 8-1 | 2/1/62 | A |
| 3.8.2 | Floating-Point Add | 226 | 8-2 | 2/1/62 | A |
| 3.8.3 | Floating Point-Add to Magnitude | 227 | 8-3 | 2/1/62 | A |
| 3.8.4 | Floating-Point Compare | 228 | 8-4 | 2/1/62 | A |
| 3.8.5 | Floating-Point Add to Fraction | 229 | 8-5 | 2/1/62 | A |
| 3.8.6 | Floating-Point Shift Fraction | 230 | 8-6 | 2/1/62 | A |
| 3.8.7 / 3.8.8 | Store / Store Rounded | 231 (landscape) | 8-7 (both) | 2/1/62 | A |
| 3.8.9 | Store Low Order | 232 | **8-8** (was "—" in `ebox_roadmap.md`) | 2/1/62 | B |
| 3.8.10 | Store Root, sheets 1-2 | 233 (landscape), 234 | 8-9, 8-10 | 2/1/62 | B |
| 3.8.11 | Floating-Point Multiply | 235 | 8-11 | 2/1/62 | B |
| 3.8.12 | Load Multiplier Register | 236 | 8-12 | 2/1/62 | B |
| 3.8.13 | Multiply and Add | 237 | 8-13/8-14 | 2/1/62 | B |
| 3.8.14 | Store Multiplier Register | 238 | 8-15 | 2/1/62 | B |
| 3.8.15 | FP Divide, sheet 1 | 239 | 8-16 | 2/1/62 | author |
| 3.8.15 | sheet 2 | 240 (rotated) | 8-17/8-18 | 2/1/62 | reused, end only re-read |
| 3.8.15 | sheet 3 | 241 left (rotated) | 8-19 | 2/1/62 | author |
| 3.8.17 | Add to Exponent | 241 right | 8-21 | 2/1/62 | C |
| 3.8.18 | SAU Multiply and Multiply and Add, PAU Section | 242 left | 8-22 | 2/1/62 | author |
| 3.8.16 | Divide Double | 242 right | 8-20 | 2/1/62 | author |
| 3.8.19 | SAU Divide | 243 | 8-23 | — | reused, not re-read |
| **3.8.20** | **Reciprocal Divide** | **244** | **8-24** | **1/1/63** | C |

The issue dates in the foot and in Index 3-2 differ for some charts.
3.8.2-3.8.9, 3.8.13 and 3.8.18 are 1/1/63 in the index and 2/1/62 at
the foot. The foot is what was printed on the sheet.

**SAU flow diagrams, category 11, PDF 255-268.** Fourteen figures, all
1/1/63. Each is one fold-out with paired printed numbers:
PDF = 255 + (k − 1)/2 for printed page 11-k/11-(k+1).

| fig | title | PDF | printed | read by |
|---|---|---|---|---|
| 3.11.1 | Binary Multiply | 255 | 11-1/11-2 | author |
| 3.11.2 | VFL Add 1 to Memory | 256 | 11-3/11-4 | D |
| 3.11.3 | VFL Load Transit and Set, Decimal Multiply, Decimal Multiply and Add, Decimal Divide, or Load Factor | 257 | 11-5/11-6 | D |
| 3.11.4 | VFL Load Converted Decimal to Binary | 258 | 11-7/11-8 | D |
| 3.11.5 | VFL Load Transit Converted Binary to Decimal | 259 | 11-9/11-10 | D |
| 3.11.6 | VFL Load Transit Converted Decimal to Binary | 260 | 11-11/11-12 | D |
| 3.11.7 | VFL Load Converted Binary to Decimal | 261 | 11-13/11-14 | D |
| 3.11.8 | Binary Divide | 262 | 11-15/11-16 | author |
| 3.11.9 | VFL Add, Add to Magnitude, Load, or Load with Flags | 263 | 11-17/11-18 | E |
| 3.11.10 | Binary Multiply and Add | 264 | 11-19/11-20 | author |
| 3.11.11 | VFL Add to Memory, Add Magnitude to Memory, Store or Store Rounded | 265 | 11-21/11-22 | E |
| 3.11.12 | VFL ("VLF" as printed) Compare Instructions | 266 | 11-23/11-24 | C |
| 3.11.13 | Binary Convert and Binary Convert Double | 267 | 11-25/11-26 | C |
| 3.11.14 | Decimal Convert and Decimal Convert Double | 268 | 11-27/11-28 | C |

**Between them, PDF 245-252** are category 9, "Sigma Errors That Cause
a Scan" (Figs 3.9.1-3.9.9; 3.9.9 SAU Error is PDF 252, printed
9-15/9-16). Category 10 (test equipment) follows.

**The serial unit's charts are flow diagrams, not timing charts.**
Category 11 is the SAU's only per-operation material. Not one of its 14
figures prints a clock, an A/B pulse, a cycle number or a time
(confirmed on every sheet by its reader). There is **no SAU timing-chart
category** in Index 3-1. The two SAU charts that do carry timing are
3.8.18 and 3.8.19, and they show the PAU's side of the SAU's multiply
and divide. **No figure anywhere in Index 3-2 covers the logical
connectives.** See Gaps.

**Buchholz** (`Planning_A_Computer_System.pdf`): printed p.n is PDF
n + 25 for pp.208-216 (p.208 = PDF 233, p.216 = PDF 241).

**Perf. Char. Vol. 1:**
- Table 2 is printed 3-3 to 3-5, PDF 21-23.
- Its notes and the Table 3 preamble are on 3-6, PDF 24.
- Table 3 is printed 3-7 to 3-9, PDF 25-27 (landscape).
- The glossary is on 3-10, PDF 28.

## 2. The structure the sources agree on

1. **Two units, one register file.** Buchholz p.208 (PDF 233), read at
   the image:
   > "The arithmetic unit consists of a parallel unit for floating-point
   > operations and a serial unit for variable-field-length operations.
   > The two units use the same arithmetic registers, namely a
   > double-length accumulator of 128 bits (the left part being called
   > register A and the right part register B), and a double-length
   > operand register of 128 bits (C and D)."

   Register spans printed on the charts:
   - A 12-59, C 12-59 (3.8.x);
   - ACC 12-59 and ACC 12-107 (with "60-107 controlled by A checker");
   - AB 12-107;
   - F up to F1-F101 (3.11.x), with "F2-49" for single, F2-97 double,
     and the digit inlet F98-101;
   - D0-D63 (3.11.3).
2. **Who does what.** Buchholz p.208:
   > "Operations on the floating-point fraction and also
   > variable-field-length binary multiply and divide operations are
   > performed by the parallel unit. Floating-point exponent operations,
   > variable-field-length (binary or decimal) add operations, and
   > logical-connective operations are executed by the serial unit. The
   > square-root operation and the binary-decimal conversion algorithm
   > are executed in unison by both units."

   p.216 (PDF 241):
   > "In floating-point multiply and divide operations, the arithmetic on
   > the fractions is performed by the parallel arithmetic unit ...
   > while the serial arithmetic unit is executing the exponent
   > arithmetic."

   The CE charts show every one of these:
   - FP exponent work goes through "GATE A EXP TO SAU ADDER" and "C EXP
     TO SAU" on 3.8.1-3.8.16. 3.8.13 and 3.8.17 call the same adder the
     "VFL ADDER".
   - VFL `*` and `/` run in the PAU (3.11.1, 3.11.8, 3.8.18, 3.8.19).
   - Store Root's right panel is headed "SQUARE ROOT DEVELOPMENT UNDER SAU
     CONTROL" (3.8.10 sheet 1, Appendix B).
   - The conversions send each digit or bit to the PAU: "CONVERT DEC TO
     BIN SIGNAL TO PAU" and "CONVERT BIN TO DEC SIGNAL TO PAU"
     (3.11.4-3.11.7, 3.11.13, 3.11.14).
3. **The serial unit's datapath.** Buchholz Fig. 14.6 (p.209, PDF 234),
   read at the image:
   - Each of AB and CD feeds a "Switch matrix (16 of 128)", then a
     "Switch matrix (8 of 16)".
   - The 8 bits go through a "T-C switch (8 bits)", with a "By-pass (8
     bits)" for undisturbed bits.
   - Both sides meet at a common "Binary adder" and "Logic unit".
   - The adder output passes a "T-C switch" or a "Decimal corrector", then
     a "Switch matrix 16→16", into the "AB write-in matrix" or "CD
     write-in matrix".

   Text, p.208-209:
   > "A two-level switch matrix is used to extract 8 adjacent bits from
   > any of 128 possible register positions, together with a by-pass for
   > 8 bits which are to remain undisturbed. True-complement (inversion)
   > circuits, both before and after the adder, take care of
   > subtraction. A decimal-correction circuit is switched into the data
   > path when decimal addition or subtraction is specified." ... "A
   > single pair of bytes is extracted, arithmetic or logic performed,
   > and the result returned to the registers in one clock cycle of 0.6
   > µsec. Longer fields are processed by repeatedly stepping the
   > counters that control the switch matrixes. The operations are
   > checked by parity checks on the switch matrixes and by use of
   > duplicate arithmetic and logic units."

   The duplicate units are visible in Fig. 3.9.9, SAU Error (PDF 252, read
   at 200 dpi): "COMPARE LU 1 BITS 0-8 WITH LU 2 BITS 0-8", "COMPARE LU 1
   BITS 9-16 WITH LU 2 BITS 9-16".

   The counters that step are named on every 3.11 sheet:
   - BAAB, the bit address in AB;
   - BACD, the bit address in CD;
   - RFL, the remaining field length;
   - SC/SCTR, the shift counter;
   - with end tests EOC1/EOC2 (end of count), EOA1/EOA2 (end of
     accumulator), EHOM1/EHOM2, and CD CUTOFF / AB CUTOFF.
4. **The parallel unit's datapath.** Buchholz Fig. 14.7 (p.210, PDF 235),
   read at the image:
   - "A,B registers" and "C,D registers" go through a "True-complement
     switch" into a "Carry propagate adder 100 bits".
   - A "Parallel unit register" and a "Shifter" sit beside them.
   - Four "MCD ×3 bits of MPR" multiple generators feed CSA 1 and CSA 2.
     CSA 1 and CSA 2 feed CSA 3, then CSA 4, into a "Sum register" and a
     "Carry register" that loop back.
   - Text, p.210:
     - "the shifter and adder extend to 96 bits";
     - "a delay time of 0.15 µsec for 96-bit additions";
     - "The shifter is capable of shifting up to four positions to the
       right and up to six positions to the left at one time ... For
       longer shifts the operation is repeated automatically";
     - "12 bits of the multiplier are handled in one cycle".
   - Text, p.211: "Since no propagation of carries is required in the four
     cycles when multiplicand multiples are added, this operation is fast."

   The "four right / six left" shifter is the source of two things.
   - Table 2's "1 cycle for each additional pre-shift of 4" is a
     right-shift loop, drawn on 3.8.2 and 3.8.6 as the shift counter
     stepping "TO 8 / TO 4 / TO 0".
   - Every chart's "(T3, NE, SH≤6) END OP" is a left-shift
     (normalization) loop of two periods a pass.
5. **The divide law** (Buchholz pp.213-216, PDF 238-241, re-read at the
   image this session).
   - One of three divisor multiples, 1, 3/4 and 3/2, is chosen per add
     cycle by Fig. 14.11. The new remainder is normalized. Fig. 14.12
     gives the quotient bits. Its rule (1): "Use only as many quotient
     bits ... as the number of shifts needed to normalize the new partial
     remainder"; its rule (3): "If more than six shifts are needed, take
     additional shift cycles".
   - p.216: "The scheme always permits at least two shifts after each add
     cycle. As many as six shifts can be carried out in the same cycle
     as one addition; if more shifts are needed, extra cycles are used
     without addition."
   - Fig. 14.13: "On the average, 3.5 quotient bits are generated each
     cycle."
   - **The Fig. 14.11 cell boundaries were re-read at 2× zoom.** In this
     reading the row labels sit inside cells. The table is:
     - remainder 100: 3/4 for divisor ≥10101, else 1;
     - remainder 101: 3/4 for ≥11001, 3/2 for ≤10001, else 1;
     - remainder 110: 3/4 for ≥11110, 3/2 for ≤10100, else 1;
     - remainder 111: 3/2 for ≤10111, else 1.
   - **This agrees with `divMultiple` in `StretchDivBox.bsv`**. (A first
     read at overview scale was one row off on columns 101 and 110 and
     was corrected at the zoom.)
   - The CE chart's "dummy cycle if more than 6 quotient bits were
     developed" (3.8.15 sheet 2) is the same law, so **the divide's
     bits-per-cycle IS in the sources**. `ebox_roadmap.md`'s
     "[NOT IN THE SOURCES]" (lines 645 and 859) is stale; the bsv header
     already records this, dated 2026-11-17.

## 3. The PAU charts against Perf. Char. Table 2

**How the columns are counted.**
- "Chart" counts periods from T0 through the END OP period, from the
  per-figure tables.
- "Table 2" is pre-execution plus execution cycles, read at the image
  (PDF 21-23), and evaluated for the example the chart's own note says
  it draws.
- The Table is dated 3/8/61. The charts are 2/1/62 or 1/1/63.

**Common to every chart (DERIVED).**
- After END OP, one period carries LATCH ACOB, EXP LATCH / EXP SAMPLE
  and the A REG sample, into the next instruction's time.
- GATE 11 & 12 runs from the second half of the END OP period to the
  first half of the next.

| fig | op | example drawn (printed note) | END OP in period | chart count | Table 2 for that example | verdict |
|---|---|---|---|---|---|---|
| 3.8.1 | L | "TWO NORMALIZATION SEQUENCES" | 4 (of 0-6) | 5 | 2 + 1 + 2 = 5 | agrees |
| 3.8.2 | + | "A EXP > C, exp diff 11", no norm | 6 | 7 | 4 + 2 (pre-shift 11 = 3 + 4 + 4) + 1 = 7 | agrees |
| 3.8.3 | +MG | "C EXP> A AND FORCED ZERO FRACTION", shift 3 | 6 | 7 | 4 + 1 + 2 (forced zero) = 7 | agrees |
| 3.8.4 | K | A exp > C exp by ≤3 | 4 | 5 | 4 + 1 = 5 | agrees |
| 3.8.5 | F+ | zero pre-shift, 2 norms | 6 | 7 | 4 + 1 + 2 = 7 | agrees |
| 3.8.6 | SHF | "SHIFT>3 BUT<12", two T4 periods drawn | 6 | 7 | 4 + 2 + 1 = 7 for shift 8-11 | agrees (for 8-11) |
| 3.8.7 | ST | 2 norms | 4 | 5 | 2 + 1 + 2 = 5 | agrees |
| 3.8.8 | SRD | norm ≤6 | 2 | **3** | 3 + 1 = **4** | **disagrees by 1, chart shorter** |
| 3.8.9 | SLØ | "ONE NORMALIZATION SHIFT"; **break mark** between clocks 4 and 5 | 6 as numbered | **not countable** (break elides periods) | 2 + 15 or 17 (+2) = 17-21 | **consistent** (DERIVED); see note (a) |
| 3.8.10 | SRT | sheet 1: PAU 0-3 on FP CLOCK; root on A PULSES (SCR 96 by 2) | — | not countable alone | 2 + 106 = 108 | reused: `clock_unit.md` §4.4 closes 108 with A = 2 periods |
| 3.8.11 | * | "NORMALIZATION SHIFT OF 6 OR LESS" | 8 | 9 | 5 + 4 = 9 | agrees |
| 3.8.12 | LMR | 2 norms | 4 | 5 | not in Table 2 | not comparable (same shape as L) |
| 3.8.13 | *+ | one norm pass; main and alternative path | 10 / 13 | 11 / 14 | 3 + 17 = 20 | **disagrees**; see note (b) |
| 3.8.14 | SMR | 2 norms | 4 | 5 | not in Table 2 | not comparable (same shape as ST) |
| 3.8.15 sh.3 E | / zero divisor | — | 4 (of 1-5) | 4 | "3 cycles pre-execution and 2 cycles execution" = 5 | **disagrees by 1, explained by the chart**: NOTE 2, "THE TC TRIGGER IS NOW TURNED ON SIMULTANEOUSLY WITH THE END OP TRIGGER. THIS ACTION SHORTENS THE OPERATION BY 300 NANOSECONDS" |
| 3.8.15 sh.2 | / (true final remainder) | — | 22 | — | data-dependent | END OP at 22; with a complemented remainder 24 (+2 = Table 2's "2 cycles if final remainder has to be complemented") |
| 3.8.16 | D/ | "2 REMAINDER NORMALIZATION LOOPS" | 29 (vs / at 22) | / + 7 | / + 6 + 2 = / + 8 | **disagrees by 1, chart shorter**; one pass: / + 5 against / + 6 |
| 3.8.17 | E+ / E+I | "TWO NORMALIZATION SEQUENCES" | 7 (of 0-8) | 8 | 1 + 5 + 2 = 8 | agrees |
| 3.8.20 | R/ | preamble then "IDENTICAL TO DIVIDE (POINT 3) FROM THIS POINT" | — | / + 4 (DERIVED: R/ periods 0-5 replace /'s periods 1-2) | "2 cycles" + "2 cycles plus all ... of Divide" = / + 4 | agrees |

**Notes to the table.**
- **The three one-period disagreements all run the same way:** the
  chart is shorter than the 1961 Table (SRD, D/, zero-divisor `/`). One
  of them is explained on the chart itself: zero-divisor `/` is NOTE 2's
  300 ns change. DERIVED, unproven: the 1962 charts record a shortened
  end-of-operation that the 1961 Table predates. **Nothing printed says
  the same change applies to SRD or D/.**
- **(a) SLØ** (Store Low Order). Table 2 charges 17 cycles unnormalized
  and 15 if normalized, plus pre-execution. The 3.8.9 chart numbers its
  clocks 0-7 consecutively, but **a break mark (a pair of wavy strokes)
  crosses the FP CLOCK row between 4 and 5 and every row below it**:
  the ring triggers, EXP LATCH/SAMPLE, the shift-register pulses, SHIFT
  CONTROL A and the SAU rows. This was re-read at 300 dpi (PDF 232).
  - So the numbering does not count the periods, and the chart's length
    is not countable.
  - DERIVED: the elided part is the T3,T4 shift loop. In period 0 the
    chart loads "48 TO SH CTR ADDER" (SLØ FCT). Shifting 48 places at
    six a T3,T4 pass is 8 passes = 16 periods, which with T0 and the
    END OP period lands at Table 2's 15-17. The drawn T3 at 1 and 3 and
    the T3 at 5 after the break are passes of that loop. The printed "ONE
    NORMALIZATION SHIFT" then refers to the normalization after the
    48-place shift.
  - So **3.8.9 does not contradict Table 2**, and Table 2 stands for
    SLØ. The model charges 2 + 17 (`ebox_roadmap.md`).
- **(b) `*+`** (3.8.13). 0-10 main path, 0-13 alternative. Table 2 says
  3 + 17, and the Table's "cannot enter execution cycles until Factor is
  available" suggests the two count from different origins.
  - `ebox_roadmap.md` already flagged this.
  - The chart reuses 3.8.11's multiply ring (MR1, MR2, MC, T4, T3) with
    "RIGHT 12 STATUS TGR". It enters the add at 8 through T2 "(CUM,
    PSA)" or TB "(MPY ST, CMPSE)".
  - It prints no CSA-loop rows (Appendix B).
  - Still open; the fidelity plan's `*+` residual (mean −1.64, down to
    −28) is the place to test it.

## 4. Figures read first-hand for this spec

The other figures' per-period tables and flows are in Appendices A-E.
### Fig. 3.8.15 sheet 1 of 3, FLOATING-POINT DIVIDE (TIMING) -- PDF 239, printed 8-16, 2/1/62

Read this session at 300 dpi (tiles t239_*). The roadmap listed it as
unread. Two parts on one sheet.

**Part A, divisor pre-normalization, FP CLOCK 1-7.** Page head: "IF ZERO
DIVISOR, GO TO PART E, SHEET 3" (arrow to 4); "DIVISOR PRE-NORMALIZATION
EXAMPLE SHOWS TWO NORMALIZATION LOOPS."

| FP CLOCK | rising, with printed condition | what moves |
|---|---|---|
| 1 | (START CTRL) T0; (START CTRL) SAMPLE TO C & EXECUTION REGS; (START CTRL) FIRST CYCLE TGR; (FCT, DIV) GATE 33 "(C REG TO ADDER)" | operand to C and execution registers; C to adder |
| 2 | (T0,DIV) D3; (T0,DIV) DIVIDE NORMALIZE EXPONENT TGR (DNE); (D3,DIV,FCT) EXPONENT ROUTING TGR (TP6); (T0,DIV) GATE 61 & 63 (TGR); (TP6,DNE,DC-bar) GATE C EXPONENT TO SAU ADDER; (DNE,DIV) SHIFT CONTROL "A" | C exponent to the SAU adder |
| 3 | (D3,DNE) D4; (D3,DIV,FCT) DIVISOR STATUS TGR (DVSR); (D3,DIV,FCT,SH>6) GATE 21 & 22 (TGR); (D3,DIV,FCT) WRITE EXPONENT C TGR; (DVSR OR DVND OR DVDE) GATE SHIFT COUNTER ADDER TO REG; (NOT SDC) GATE SHIFT COUNTER REG TO ADDER; (DVSR) ADD SHIFT AMOUNT TO REGISTER. "SHIFT >6" printed over 3. | divisor shifted, shift amount added to the counter |
| 4 | (D4, DVDE-bar, ZERO, DVSR) D3; (D4,DNE,NOT DC) EXP LATCH & SAMPLE | |
| 5 | (D3,DNE) D4; "SHIFT <= 6" printed over 5; (DVSR,DVND) GATE 11 "(FREQ TO A CHECKER)"; SAMPLE TEST COMP; SAMPLE TO F REG, SHIFT REG & COUNTER REG; "(START ROUTING DIVIDEND FOR NORMALIZATION SEE PART B)" | divisor fraction to F |
| 6 | (D4, DVND NOT INT) D3; (D4,DVSR,DVND) SAMPLE ACOB TO C REG; (D4,DNE NOT DC) EXP LATCH & SAMPLE | ACOB to C |
| 7 | D4 (continues into Part B) | |

**Part B, dividend pre-normalization, FP CLOCK 5-11.** "DIVIDEND
PRE-NORMALIZATION EXAMPLE SHOWS 2 NORMALIZATION LOOPS." D3/D4 alternate
each period: (D3,DNE) D4 at 5, 7, 9; (D4,DVND NOT INT) D3 at 6, 8, 10.
"SHIFT>6" over 6-7, "SHIFT<=6" over 8-9. Lanes: (DNE); GATE 61 & 63 (TGR)
to 9; SHIFT CONTROL "A"; GATE SHIFT COUNTER ADDER TO REG; GATE SHIFT
COUNTER REG TO ADDER; (D3 DVSR SHIFT<=6) DIVIDEND STATUS TGR (DVND);
(DVSR, DVND) GATE 31 "(A REG TO ADDER)"; (DVND, DVDE-bar, UNNORMALIZED)
"(GATE 32, ALSO IF DOUBLE OPERATION)"; SHIFT CONTROL "B" (dashed);
TP6 TGR (5-6); (DNE, TP6-bar) GATE A EXP TO SAU ADDER FOR NORMALIZE
UPDATING; (D3,DVND) GATE 21 (TGR); (D3,DVSR,DVND,SH>6) GATE 22 (TGR);
(D3,DVSR,DVND) WRITE EXPONENT A TGR; (DVND, DVSR-bar, OR DVDE) SUB SHIFT
AMOUNT FROM REG; EXP LATCH & SAMPLE (8-9, 10-11); SAMPLE TO F REG, SHIFT
REG & COUNTER REG (6-7, 9-10). Exits: at 8 "IF DIVIDEND ZERO, GO TO PART
F, SHEET 3"; at 9-10 "(START DIVIDE, SEE PART C, SHEET 3)"; at 10 "IF
DIVIDEND NOT NORMALIZED, GO TO PART G, SHEET 3".

**Branch structure.** One normalization pass is a D3,D4 pair: two FP
CLOCK periods per shift of six (both parts show "SHIFT >6" on the first
pair and "SHIFT <=6" on the second). That is Table 2's "2 cycles for each
additional divisor (dividend) shift of 6" drawn (agrees).

**Points.** The "POINT 9" and "POINT 11" that sheet 3 returns to are the
circled FP CLOCK numbers 9 and 11 of Part B, not separately named points.

**A printed cross-reference error.** Part B says "START DIVIDE, SEE PART
C, SHEET 3", and 3.8.16's note says "POINT 22 OF PART C, SHEET 3". Part
C is on SHEET 2 (PDF 240, labelled "PART C" with "Floating Point Divide,
Reduction and Termination"); sheet 3 holds Parts E, F, G only. 3.8.16's
own page head says "(SEE SHEET 2, FIGURE 3.8.15)", which is right.

### Fig. 3.8.15 sheet 2 of 3 -- PDF 240, printed 8-17/8-18, 2/1/62: REUSED, not re-transcribed

Per the brief, the roadmap's reading ("Step 6 groundwork", the trial /
intermediate / last reduction cycles, "Number of Reduction or Dummy
Cycles Depend Upon Number of Quotient Bits Developed per Step (Cycle)")
is reused, and `StretchDivBox.bsv`'s header already quotes it further.
Only the end of the sheet was read this session, to fix the D/ branch
point (tiles t240c, t240d, sheet rotated 90°):

- Periods 9-25. Part C (upper) and Part D (lower, "PART D'").
- At 20: "(D3, DC, Sh=0 Not Double, Res True)" TC at 22; "Not Both" TC
  dashed at 24.
- At 22: "If Double, go to Figure 3.8.16" (twice, Part C and Part D).
- Part D, 20-22: "Last Reduction Cycle", entered on "Ctr = 0 (DC, Comp,
  Result) (Double, Shift Ctr Adder Output = 0) Result True, D3, DC".
- At 22: (End Op) END OP; (End Op) Latch ACOB (22.5-24); (End Op) Sample
  ACC 12-59; (End Op) Sample Indicators; Inhibit Quotient Sample
  (dashed); Final Divide; (DF, DC) Gates 13, 14.
- Dashed alternative 24-25: End Op, Final Divide, Gates 13,14, "Add Back
  1x Divisor"; note "This is done if the last reduction cycle caused the
  result to be complemented. This is represented by the dotted lines above
  and is done to allow the remainder to be in true form."

So `/` with a true final remainder ends END OP at period 22. With a
complemented remainder it ends at 24: +2, which is Table 2's "2 cycles if
final remainder has to be complemented" (agrees).

No per-cycle table of periods 9-21 is given here. That is a GAP (below).

### Fig. 3.8.15 sheet 3 of 3 -- PDF 241 left (rotated 90°), printed 8-19, 2/1/62

Read this session (rotated render, overview at 1600 px; labels legible at
that size).

**Part E, ZERO DIVISOR, FP CLOCK 1-5.** T0 (1); D3 (2); D4 (3); TC (4);
SAMPLE OP CODE TO EXEC REG AND TØB TO C REG (1); FIRST CYCLE TRIGGER
(1-2); ONE (2-4); DIVISOR TRIGGER (3-4); END OP (4); SAMPLE ZERO DVSR IND
(4.5-5); STC (4). Five periods, END OP in the fourth.
- NOTE 1: "FLOATING POINT DIVIDE OR DIVIDE DOUBLE RECIPROCAL DIVIDE IS
  TERMINATED IN THE SAME MANNER AFTER 2".
- NOTE 2: "THE TC TRIGGER IS NOW TURNED ON SIMULTANEOUSLY WITH THE END OP
  TRIGGER. THIS ACTION SHORTENS THE OPERATION BY 300 NANOSECONDS".
- Table 2 (PDF 23): "If zero divisor 3 cycles pre-execution and 2 cycles
  execution instead of previous" = 5. Chart: END OP in period 4, STC and
  the indicator sample in 4-5. AGREES if the indicator sample in 5 is
  counted; NOT COMPARABLE to better than one period otherwise.

**Part F, ZERO DIVIDEND, FP CLOCK 8-9.** (D4, DVSR-bar, DVND, F=0) D4;
D3 at 9; (D4, DVND, DVSR, F-REG=0) ZERO DIVIDEND TGR (ZD) "(TURNED OFF BY
SDC)"; (ZD, DVND, DVDE-bar) SHIFT CONTROL "B"; (DVSR,DVND) GATE 31 "(32
ALSO IF DOUBLE OPERATION)"; "OTHER TGRS NOT AFFECTED"; "RETURN TO POINT 9
PART B, SHEET 1". NOTE: "THIS CYCLE IN EFFECT RESTORES THE OPERATION TO
THE START OF DIVIDEND PRE-NORMALIZATION, THIS TIME WITH SHIFT CONTROL
"A". THEREFORE THE DIVIDEND WILL BE SHIFTED ONLY AS MUCH AS THE DIVISOR".
One extra period.

**Part G, DIVIDEND NOT NORMALIZED, FP CLOCK 10-11.** D4 → MR-3 (10);
(D4, 1X COMP, DVND, HIGH BIT DIVIDEND = 0) "(1X COMP TGR)"; "1X COMP GATE
LINE DIVISOR GATING"; D3 (11); "RETURN TO POINT 11 PART B, SHEET 1".
Note: "THIS CYCLE ALLOWS HIGH ORDER DIVIDEND ZEROS TO BE SKIPPED; THAT
IS, DROPPING DIVISOR GATING LINE DOES NOT ALLOW FOR REDUCTION CYCLES.
QUOTIENT BITS FOR LEADING ZEROS WILL BE ZERO". One extra period, then
rejoin.

### Fig. 3.8.16, FLOATING-POINT DIVIDE DOUBLE (TIMING) -- PDF 242 right half, printed 8-20, 2/1/62

Read this session at 300 dpi, tiles t242_2550_* and t242_3750_*.
Page head: "BASICALLY SAME AS DIVIDE TO THIS POINT (SEE SHEET 2, FIGURE
3.8.15)" (arrow to 22); "SHOWS 2 REMAINDER NORMALIZATION LOOPS."
NOTE (left): "IF THE REMAINDER IS COMPLEMENTED AT POINT 22 OF PART C,
SHEET 3, FIGURE 3.8.15 IT IS RESTORED (22 TO 24) PART C BEFORE COMING TO
THIS POINT."

Clock axis: FP CLOCK, circled 22-30.

| FP CLOCK | rising (printed condition) | lanes / transfers |
|---|---|---|
| 22 | (D3,DVDE) D4; (DC CTR=0 D3,RES TRUE) FINAL DIVIDE (FD); (FD,DC) GATE 13 & 14; ROUTE 1X COMP DIVISOR TO ADDER; continuing: SHIFT CONTROL "A", GATE SHIFT CTR ADDER TO REG (to 23), GATE 21 (TGR), SUBTRACT SHIFT AMOUNT FROM CTR REG (to 24), DVDE (to 24), GATE 36 & 72 (to 24), SHIFT CONTROL "B" (to 24), DC (to 25), GATE 61 (to 24, then (NM-bar)(FD,DC-bar) again from 25), GATE A EXP TO SAU ADDER (to 25), GATE SHIFT COUNTER REG TO ADDER, WRITE EXP A TGR (to 26), GATE & INVERT C EXP TO SAU ADDER (to 26) | 22-23: "TRY FOR 49 QUOTIENT BIT (ADDER LOOP)"; QUOTIENT FRACTION TO ACC (22-25); QUOTIENT EXP TO ACC (to 25) |
| 23 | (D4,DVDE) D3; (RESULT TRUE) ROUTE A "1" TO INPUT 60 OF AC1B "(BECOMES 49 QUOTIENT BIT)" (dashed, 23-25) | |
| 24 | (D3,DVDE) D4; (D3,FD) TC; (TC,DC DOUBLE) READ OUT BACD 64 TGR "(ROUTES D EXP TO SAU ADDER)"; (TC,DC,DOUBLE) NORMALIZE EXPONENT TGR | SHIFT COUNTER REG LATCH & SAMPLE (24); "ADDER LOOP TO DETERMINE SHIFT AMOUNT" (24-26) |
| 25 | (TC,DC DOUBLE) MR3; (MR3,FD) TP6 TGR; (FP, DC-bar, NM-bar) SUPPRESS ADDER OUT POS 51 "(THIS POSITION IS HIGH ORDER BIT OF QUOTIENT AND IS NOT WANTED ON REMAINDER NORMALIZATION LOOPS)"; ACOB LATCH; SAMPLE ACC 12-63 (61-63 ALWAYS ZERO); SAMPLE DIVIDE INDICATORS; EXP LATCH & SAMPLE (25-26) | quotient out through the ACOB |
| 26 | (MR3,FD) T3; (MR3,FD) WRITE EXP C (to 28) | F REG LATCH & SAMPLE, SHIFT REG LATCH & SAMPLE (26); NORMALIZATION LOOP "1" (26-28); UPDATE EXP LOOP "1" |
| 27 | (T3,NE) TC; (T3) T4; (T3,NE) GATE 22 (TGR); (T3,FD,NM-bar) GATE 61 & 63 TGR; (T3,NE) NORMALIZE MANTISSA TGR. "SHIFT >6" printed over 27 | |
| 28 | (T4,NM) T3 | F REG and SHIFT REG LATCH & SAMPLE (28); LOOP 2; UPDATE EXP LOOP "2" (28-30) |
| 29 | (T3,NE) TC; (T3) T4; (T3,NE SH<=6) END OP. "SHIFT <=6" printed over 29 | "FRACTION TO A CHECKER" (29-30) |
| 30 | (END OP,FD) WRITE EXP D TGR; (END OP) GATE 11 & 12; SAMPLE REMAINDER INDICATORS; ACOB LATCH | "EXP TO CHECKER" |

NOTE (right): "WHEN THIS PORTION OF THE OPERATION IS REACHED, THE
REMAINDER RESULT (IN F REG) IS TRUE. THE 1X DIVISOR IS SUBTRACTED WITH
NO LATCH TO THE F REG. (NO CHANGE TO ORIGINAL TRUE RESULT). IF THE ADDER
OUTPUT RESULT IS STILL TRUE A ONE IS ROUTED TO THE A CHECKER (AND
EVENTUALLY TO ACC) TO BECOME THE 49 QUOTIENT BIT((ACC POS 60)."

**Paths (COUNTED from the drawing).** The 49th-bit trial is two periods
(22-23), the exponent hand-over is two (24 TC, 25 MR3), and each
remainder normalization pass is a T3,T4 pair (26-27, 28-29), two periods
a shift of six, ending on (T3,NE SH<=6) END OP.
- One remainder pass (shift <=6): END OP in period 27.
- Two passes, as drawn: END OP in 29, the remainder's ACOB latch in 30.
- Each further pass: +2.

**Registers.** The quotient goes to ACC 12-63 through the ACOB at 25,
before the remainder work. The remainder fraction is in the F REG and
goes "TO A CHECKER"; its exponent is D's ("READ OUT BACD 64 TGR (ROUTES D
EXP TO SAU ADDER)"; sheet 2 Part D: "Subtract "48" from Dividend Exp &
Route to D Reg. Used as Remainder Exp on Divide Double"). The remainder
leaves by the ACOB latch at 30, the period after END OP. The chart does
not say where the ACOB goes next; Fig. 3.2.21 (PDF 113, cited in NEXT.md)
routes it to the store ABC.

### Fig. 3.8.18, SAU MULTIPLY AND MULTIPLY AND ADD, PAU SECTION (TIMING) -- PDF 242 left half, printed 8-22, 1/1/63

Read this session at 300 dpi, tiles t242a, t242b. No numbered clock: an
unnumbered waveform of three periods before, and three after, a central
section that is not drawn.

**Entry (three drawn periods, then the dashed line).**
- (PAU START VFL MPY) SIGNAL SSQ[?] TO VFL TRIGGER. "SSQ" partly
  ILLEGIBLE (smudged); "SIGNAL SSQL" is the best reading. NOTE: "THIS
  TRIGGER IS USED BUT SINCE A PAU OPERATION IS NOT IN PROGRESS THE ONLY
  LINE UP WILL BE "SECOND CYCLE START VFL MPY"".
- (PAU START VFL MPY) MULTIPLY STATUS TGR (MPY ST); ONE X MULTIPLICAND
  TGR; SHIFT RIGHT 12 TGR (all held through the dashed line).
- (SECOND CYCLE START VFL MPY) MR3 (periods 1-2); (MR3,MPY ST) T1
  (2-3); (T1,MPY ST) MR1 at the dashed line.
- Between the dashed lines: "IDENTICAL TO FLOATING POINT MULTIPLY BETWEEN
  THESE POINTS FOR BOTH SAU MULTIPLY AND MULTIPLY AND ADD".

**Exit, MULTIPLY.** "SHIFT = 0 - (WILL ALWAYS BE ZERO ON SAU MULTIPLY
SINCE PAU EXECUTION REGISTER IS RESET)". T3; (T3) TC; (T3) T4;
(T3,NE) END OP (one period); (TC,END OP) LATCH ACOB; SAMPLE TO ACC
12-59; (END OP) GATE 11 & 12. NOTE: "SAMPLE TO ACC 60-107 CONTROLLED BY A
CHECKER, ALSO A CHECKER RETURNS CONTROL TO SAU."

**Exit, MULTIPLY & ADD.** (T3,NE) END OP; (TC,END OP) LAST CYCLE "SIGNAL
SAU"; (TC,END OP) SET IN RIGHT; (TC END OP SAU OPERATION) 8 SHIFT SAMPLE
SHIFT CONTROL REG; "SAU RESUMES CONTROL (BEGINS ADDITION)".

**Counts (COUNTED).** Entry: MR3, T1 then MR1, about 2-3 FP periods
before the FP multiply's MR1. Exit: one period (T3/TC/T4 with END OP),
then the ACOB latch. The middle is 3.8.11 verbatim.

**What it settles.** VFL binary multiply runs on the FP multiply's
hardware and sequence, entered at MR1 ("IDENTICAL TO FLOATING POINT
MULTIPLY"), started by the SAU ("PAU START VFL MPY") and handed back to
it ("A CHECKER RETURNS CONTROL TO SAU"; "SAU RESUMES CONTROL"). See
"One multiplier or two" below.

### Fig. 3.8.19, SAU DIVIDE (TIMING) -- PDF 243, printed 8-23, 1/1/63: REUSED, not re-read

Per the brief. The roadmap's lines: "GATES 36 & 72 & ENABLE MULTIPLE
DECODING", "GATE COUNTER ADDER TO REG & SUB SHIFT AMOUNT FROM CTR", "(D3,
CTR=0, TRUE RESULT) -> FINAL DVDE TGR", "IF DIVIDEND NOT NORMALIZED TAKE
SAME ACTION AS FP", "REDUCTION CYCLES JUST LIKE FP". `StretchDivBox.bsv`
adds "(D3, BIT 2-0 SHIFT <= 6)" beside "NORMALIZATION LOOP". These are
extracts, not a cycle table (GAP below). What they settle for A3/A4: the
VFL divide's reduction is the FP divide's reduction ("JUST LIKE FP"),
which is the same hardware finding as 3.8.18.

### Fig. 3.11.1, BINARY MULTIPLY -- PDF 255, printed 11-1/11-2, 1/1/63

Read this session (overview and tiles t255a-c). Flow diagram. **Cycle
count NOT PRINTED.**

Entry: "DECODED VFL INST LA START SAU NOT OPER PAU NOT OPER" → TON VFL OP
56.16.00; TON H K 56.16.00; LOAD SAU EXEC REQ 55.10.

Housekeeping fan-out (one parallel group): RESET F REG 56.33.00; LOAD
SHIFT CTR TO 48 56.32.00; LOAD BAAB TO 05-bar 54.12.00; ◇BAER = 0: NO →
LOAD BACD TO BAER-1 54.21.01, YES → LOAD BACD TO 64-1 54.22.02; ◇SAB = NSM:
NO → TOF LIKE SIGNS, YES → TON LIKE SIGNS 56.15.01; SET SHIFT CTL TO R8
56.32.01; ◇LAGO → RESET SRCD 54.60.06; ◇SIGNED: NO → LOAD RFL TO FLER-8
54.32., YES → LOAD RFL TO FLER - BS 54.32. Then ◇LA GO: NO → back to the
fan-out; YES → TOF HK 56.16.00 and ◇SIGNED.

Signed branch: TON HSB 56.11.00 → READ OUT CD SIGN BYTE TO SRCO; REDUCE
BACD BY 8 54.22.02; REDUCE RFL BY 8 54.32.01; ◇SCD = 1: YES → INVERT LIKE
SIGNS TRIG 56.15.01; NO → TOF HSB 56.11.00. Both branches → TON MPY 1
56.12.00.

**MPY 1 loop (one byte a pass).** REDUCE BAAB BY 8 54.12.01; REDUCE BACD
BY 8 54.22.01; ACCUMULATE CD RESIDUE; REDUCE RFL BY 8 54.32.01; ◇BAAB
CARRY NO → TON EOA2 AB CUT OFF 54.18.01 56.21.21; ◇SC = 0: NO → ACC AB RES
WRITE IN AB, CD RES. 56.26.10; YES → EXAMINE OUTPUT OF CO FOR PF 56.51.20;
SC - 8 TO SCTR REG 56.31.10; SAU RES. TO INITIAL RES REG 56.41.10; XFER
BYTE FROM AB F2-9 FROM CD F50-57 56.31.20. Then ◇EOC1: NO → loop; YES →
◇SC = 0: NO → loop; YES → TON EOA2 AB CUT OFF; TOF MPY 1 TON MPY 2
56.12.00.

**MPY 2.** RESET AB 56.24.40; F50-97 TO ACKR TO C12-59 56.31.00;
◇LIKE SIGNS NO → TON SIGN BIT OF SRAB 56.25.02; PAU SRART [sic] UFL [sic]
MULT 56.34.00; → TOF MPY2 TON MPY3 56.12.00 → (WAIT FOR PAU TO MULT AND
XFER RESULT TO AB 12-107) ‖ DECONDITION UFL LATCH 54.60.01 → ◇END DPXFR
FROM ACKR: YES → TON SIR 56.11.16; TO FMPY3 56.11.16 → NORMAL SIR CYCLE.

**DERIVED.** The SAU's own work is operand assembly: the field is moved a
byte (8 bits) a pass from AB/CD into the F register (F2-9 from AB, F50-57
from CD) and counted down by 8 (BAAB, BACD, RFL, SC). The multiplication
is the PAU's ("PAU START", "WAIT FOR PAU TO MULT"). The product returns
to AB 12-107 through the A checker. The PAU half is Fig. 3.8.18.

### Fig. 3.11.8, BINARY DIVIDE -- PDF 262, printed 11-15/11-16, 1/1/63

Read this session (overview and tiles t262a-c). **Cycle count NOT
PRINTED.**

Same housekeeping entry as 3.11.1 (with "LOAD BAAB TO 47", "LOAD SHIFT
CTV TO 0"; ◇LA REJECT → TON RESET ONLY → GENERATE INST RESET PORTION OF
SIR AND END OP). Signed → TON HSB, then TON DIV 1 56.12.10.

**DIV 1 loop (divisor bytes).** ◇EOA1 YES → CHK CD BYTE FOR PF 56.51.20;
◇EOA2: NO → XFER CD BYTE TO F 2-9 56.31.20 → ACCUMULATE CD RESIDUE
56.26.10; REDUCE BAAB, BACD • RFL BY 8 54.12.- 54.22.02 54.32.01; ◇CD
CUTOFF: NO → WRITE CD RESIDUE INTO SAU CD RES REG 56.26.10; ◇EOA 2: NO →
LATCH SHIFTER AND CD INTO F 56.31.10 56.33.00 → REDUCE SHFT CTR BY 8. Then
◇EOC 1: NO → SET SHFT CTL TO R8 56.32.01, loop; YES → ◇EOC 2: YES → ◇F = 0:
YES → TON SIR, TON Z D 56.51.30, TOF DIV 1 (zero divisor); NO → ◇ANOTHER
NORM. CYCLE REQ. ... ; EOC2 NO → LOAD SHFT CTL TO R 0 56.32.01 → SIGNAL
PAU TO START NORM. (TON VFL DIVISOR) 56.32.01 → TON CD CUTOFF 56.21.21.
TOF DIV 1 TON DIV 2 56.12.10 with GATE F2-49 TO C12-59 56.31.00, SET SHIFT
CTL TO R8, "A" INPUT TO RFL-49, "B" INPUT TO RFL-1, "A" INPUT TO
BACD-97, "B" INPUT TO BACD-SHIFT CTR, RESET EOA2, RESET "F" REG, GATE
OS-bar TO BAAB.

**DIV 2-3 (dividend bytes, normalization).** TOF DIV 2 TON DIV 3
56.12.10; ◇EOC2, ◇EOA2, ◇EHOM2, ◇EHOM1, ◇"1" IN AB BYTE; XFER AB BYTE TO
F2-9 56.31.20; ACCUMULATE AB RESIDUE; TON PF ADD; XFER AB AND CD RESIDUE
TO A CKR 56.41.10; DECREASE RFL BY 8; INCREASE SHFT CTR BY 8; LATCH F REG
SHIFTED R8; DECREASE BAAB BY 8; ◇EHOM 2 / ◇SHFT CTR PLUS: YES → TOF EOC1
AND EOC2 54.38.03; SET R 0 IN SHFT CTL; **PAU START VFL DIVIDE 56.33.10**;
TOF DIV 3 TON DIV 4.

**DIV 4.** **PAU DO VFL DIVIDE 56.34.00** → ◇PAU FINISHED (self-loop: the
SAU waits) → SET SHFT CTL TO L1. (PAU, FD-VFL DIVISOR) 61.03.71; TOF DIV 4
TON DIV 5 56.12.10 → RESET AB REG; LATCH F REG SHIFTED L1; XFER BACD TO
SHFT CTR; SET R8 INTO SHFT CTL; KILL CDSM (HELD UP TIL SIR); GATE LS-bar
INTO SAB; GATE SAB INTO LIKE SIGN TRG; GATE OS-bar TO BAAB; TON PAU COUNT
TO ZERO 56.32.01; RESET EOA2; GATE F90-97 TO CD PRE OR 56.13.5; GATE
BACD-8 TO RFL.

**DIV 5-6 (quotient and remainder out, byte a pass).** TOF DIV 5 TON DIV
6; ◇EOC1, ◇EOC2, ◇CD CUTOFF; TON EOC2; TON CD CUTOFF; MASK BY RFL;
ACCUMULATE CD RESIDUE; REDUCE SHFT CTR BY SHFT CH (?); WRITE IN CD
RESIDUE; GATE F90-97 TO CD PRE OR; UPDATE RFL AND BAAB BY 8 OR RFL; LATCH
F REG SHIFTED R8; ◇SHFT CTR=0 → SET R1 INTO SHFT CTL; TOF DIV 6 TON SIR.

**SIR (termination).** GATE F50-97 TO A CKR TO STORE REG 56.31.00; GATE
LS TO A CKR TO STORE REG 56.31.00; XFER CD RESIDUE TO A CKR 56.41.10;
SIGNAL A CKR TO CHK RESIDUE 56.41.01; SET BAAB TO 10. 54.15.02; SET BACD
TO 10 54.25.02; SIR TO PAU AND LA 56.42.00; RESET CTL TRIGS IN SAU; GATE
INDS TO IND REG 56.52.04; **SIGNAL LA IF ZD 56.42.00 "CANCEL STORE TO
REMAINDER REG"**; TOF SIR 56.11.16.

**DERIVED.** As for multiply, the SAU assembles and normalizes the
operands a byte (8 bits) a pass and the PAU divides; the SAU waits on
"PAU FINISHED". The VFL remainder goes out through the A checker to the
STORE REG, and the look-ahead is told to cancel the store to the
remainder register on a zero divisor. VFL `/` therefore stores its
remainder through the look-ahead's store path, as Vol. 2 PDF 41 implies
for FP D/.

### Fig. 3.11.10, BINARY MULTIPLY AND ADD -- PDF 264, printed 11-19/11-20, 1/1/63

Read this session (overview and tiles t264a-c). **Cycle count NOT
PRINTED.**

Entry and housekeeping as 3.11.1 (LOAD BAAB WITH OS-bar; LOAD SHIFT CTR
TO 48; SET SHIFT CTL TO R8; ◇LA REJECT). TON MPYC 1 56.12.05: XFER BYTE
FROM CD TO F2-9 56.31.20; REDUCE BACD AND RFL BY 8; ACCUMULATE CD
RESIDUE; GATE INITIAL CD RESIDUE TO A CKR 56.41.10; ◇SC = 0: NO → LATCH
BYTE INTO F REG 56.31.10, REDUCE SHFT CTR BY 8, WRITE CD RES INTO SAU CD
RES REG; YES → CK FOR PF 56.51.20; ◇EOC1 / ◇EOC2 / ◇SC=0; **VFL READY FOR
MCND TO LA 56.42.00**; TON CD CUT OFF; ◇WAIT FOR MCND (loop); TOF MPCY 1;
◇REJECT.

Connector (A): LOAD BACD TO 63; TOF EOC 1•EOC2; TON MPYC2 56.12.05 → READ
OUT CD TO SIGN BYTE ARRANGER 54.60.01; ◇SIGN = 1 → INVERT LIKE SIGNS;
LOAD BACD TO 11; LOAD RFL TO 4. TOF MPYC2 TON MPYC3: loop READ OUT BYTE
FROM CD 56.21.12; REDUCE BACD • RFL BY 8 54.22.02; ENABLE CD PF CKR
56.51.20; ◇EOC1 → ◇EOC2 NO → loop. EOC2 YES → TOF MPYC3 TON MPYC4
56.12.05; TOF EOC1•EOC2; **PAU START MULTIPLY 56.34.00** → **PAU DO VFL
MPYC 56.12.05**; KILL CDSM 56.13.15 (THESE LEVELS UP WITH SIR); GATE
F90-97 TO CD PRE OR 56.13.15 → ◇LAST CYCLE MPYC: YES → TOF MPYC4 TON MPYC5
AND PL1 56.12.05 56.11.06. ◇LIKE SIGNS NO → TON CD COMP 56.21.21.

**The add (PL1/PL2 loop, one byte a pass).** BRING UP ADD TO AB LVLS
55.20.01 55.20.03; GATE BYTE FROM AB TRUE 56.21.22; ◇CD COMP: NO → GATE
BYTE FROM F TRUE, YES → GATE BYTE FROM F COMP; GATE SHIFTER TO F REG →
LATCH F REG → ACCUMULATE CD RESIDUE ON BYTE FROM F → UPDATE BAAB BY 8;
◇1ST CYCLE: YES (PL1 • PL2-bar) → ◇LIKE SIGNS NO → VFL CARRY TO ADDER
56.23.01 → TON PL2 56.11.06; PERFORM ADD • WRITE RESULT INTO AB AT BAAB.
◇F = 0: NO → loop. YES → ◇LIKE SIGNS: YES → ◇CARRY: YES → ◇EOA1 (NO →
loop; YES → TOF PL1•2, TON SIR); NO → TOF PL1•2 TON SIR. LIKE SIGNS NO →
◇CARRY: YES → TOF PL1•2 TON SIR; NO → ◇EHOM1 YES → TOF PL1•2 56.11.06 TON
SUR 56.11.10 → "SUR AND RECOMP IDENTICAL TO ADD."

NORMAL SIR CYCLE: LOAD BAAB BACD TO 10; GATE INDS TO REG; UPDATE AB RES IN
ACKR; XFER CD RESIDUE TO ACKR.

**DERIVED.** The product comes back in F and is added into AB a byte a
pass ("PERFORM ADD • WRITE RESULT INTO AB AT BAAB", until F = 0), with
carry propagation past the product (◇CARRY, ◇EOA1) and a recomplement
pass (SUR) "IDENTICAL TO ADD". So `*+` VFL = SAU operand assembly + PAU
multiply + an SAU add of the product. This matches Table 3's "*+ ... 3.0
+ Add exec. time" in shape.

## 5. The SAU flows against Perf. Char. Table 3

No SAU flow prints a time, so the check is of **shape**: do the loops on
the sheet match the terms of the Table 3 equation (PDF 25-28, read at
the image)? Table 3 counts .6 µs, which is 2 model clocks, per term
unit.

Glossary (PDF 28):
- x = field length (minus the byte size if signed);
- y = 8 in binary, the byte size in decimal;
- r = 8 in binary, 4 in decimal;
- w = accumulator significant bits beyond the field length;
- t = field length less zone bits;
- u = result field;
- s = accumulator field less leading zeros;
- v = 96 in binary, 92 in decimal;
- z = carries out of the last x/y byte plus one per succeeding byte.

| Table 3 entry | equation (exec) | flow | shape |
|---|---|---|---|
| `+`, `+MG`, `L`, `LWF` | .6(x/y + z); unlike signs CD > AB add .6(os/r + x/y + z + 1) | 3.11.9 | Agrees in shape. The loop steps "BAAB, BACD AND RFL BY 8" (binary) or "BAAB BY 4; RFL AND BACD BY BSER" (decimal): one pass per y bits, giving x/y. After EOC1 the carry tests continue a byte at a time while a carry propagates, giving z. The recomplement is a separate full AB pass from "BAAB TO 127", giving the os/r + ... + 1 term (DERIVED). |
| `M+`, `M+MG`, `ST`, `SRD` | .6(x/y); unlike signs AB > CD add .6(x/y + 1); SRD pre-execution 3.0 not 1.8 | 3.11.11 | Agrees in shape. The CD recomplement is a second pass. SRD's extra 1.2 µs pre-execution matches the separate single-byte RND cycle before the loop (DERIVED). "NO WRITE IN AFTER EOC2. CYCLES TAKEN FOR PF CK ONLY" means extra passes after the field. Table 3 has no term for them. **Open.** |
| `M+1` | .6(c + 1) | 3.11.2 | Agrees in shape (the add-1 loop exits early on "like signs and no carry", giving c) |
| `K`, `KE`, `KR` | .6(x/y + w/r) | 3.11.12 | Agrees in shape. "PERFORM ADD BUT NO WRITE IN" byte loop, then the accumulator beyond the field gives w/r. **Compare ends early** on some paths (3 of 9 paths to TON SIR bypass EOC1/EOC2; Appendix C, DERIVED from wire tracing). Table 3's equation has no early-exit term. |
| `LTRS`, `LFT` | .6(v/y + 3) | 3.11.3 | **Agrees exactly in the constant.** 3.11.3 loads the PAU shift counter "96" (binary) or "92" (decimal), matching v = 96 / 92 |
| `LCV D-B` | .6(x/y + t/4 + u/8 + 4) | 3.11.4 | **Agrees term by term.** CD-FLO loop: bytes in (x/y). AB-FHI loop: "GATE 4 BIT BYTE FROM AB TO F98-101" → "CONVERT DEC TO BIN SIGNAL TO PAU", one digit a pass (t/4). F-ABOS loop: 8 bits out a pass (u/8). |
| `LCV B-D` | .6(x + u/8 + 1) | 3.11.7 | Agrees term by term: CD-FHI one bit a pass, "TRANSFER 1 BIT BYTE FROM CD TO F98" (x); F-ABOS 8 bits out (u/8) |
| `LTRCV B-D` / `D-B` | .6(x + 3) / .6(x/y + 16) | 3.11.5 / 3.11.6 | Agrees in shape (one bit a pass / bytes in) |
| `CV B-D`, `DCV B-D` | .6(s + u/8 + 1) | 3.11.13 | Agrees: a bit loop ("GATE 1 BIT FROM AB TO F98", "CONVERT BIN TO DEC SIGNAL TO PAU") over s bits, then a byte loop out |
| `CV D-B`, `DCV D-B` | .6(s/4 + 1) / .6(s/4 + 2) | 3.11.14 | Agrees: a digit loop, 4 bits a pass. Double does two LA transfers (LA1, LA2): the +1 (DERIVED) |
| `*` | pre 6.0, exec 3.9 | 3.11.1 + 3.8.18 | **Not comparable.** The SAU's byte-assembly loop (MPY 1) is not split out. 3.9 µs = 13 clocks, against FP `*`'s 4 execution cycles. |
| `*+` | pre 7.8, exec 3.0 + add exec time | 3.11.10 | Agrees in shape: PAU multiply, then a product-into-AB add loop, "SUR AND RECOMP IDENTICAL TO ADD" |
| `/` | pre 5.4, Q = .6(DR L"0"/6 + (DDL or DRL)/8 + A + (97 − DRL)/8 + 1) | 3.11.8 + 3.8.19 | Agrees in shape: "/6" is the 6-place normalization, "/8" the byte loops in and out |
| `C`, `CM`, `CT` (connectives) | .6(x/y) | **none** | no flow diagram exists (Gaps) |

## 6. One multiplier or two (`NEXT.md` "ONE PARALLEL-UNIT MULTIPLIER, NOT TWO")

**ONE. The sources settle it, three ways independently.**
1. **Buchholz.** p.208: VFL binary multiply and divide "are performed by
   the parallel unit". Fig. 14.7 (p.210) draws one CSA tree (CSA 1-4),
   one sum register and one carry register, with four "MCD ×3 bits of
   MPR" inputs, and nothing else that multiplies.
2. **CE Fig. 3.8.18** (PDF 242 left, read first-hand):
   - The SAU starts the PAU ("(PAU START VFL MPY) MULTIPLY STATUS TGR (MPY
     ST)", "ONE X MULTIPLICAND TGR", "SHIFT RIGHT 12 TGR").
   - It enters at MR1. "IDENTICAL TO FLOATING POINT MULTIPLY BETWEEN THESE
     POINTS FOR BOTH SAU MULTIPLY AND MULTIPLY AND ADD".
   - It returns: "A CHECKER RETURNS CONTROL TO SAU"; for `*+`, "LAST CYCLE
     → SIGNAL SAU", "SAU RESUMES CONTROL (BEGINS ADDITION)".
   - "SHIFT = 0 - (WILL ALWAYS BE ZERO ON SAU MULTIPLY SINCE PAU EXECUTION
     REGISTER IS RESET)".
3. **CE Figs 3.11.1 and 3.11.10** (read first-hand):
   - The SAU only assembles the operand a byte a pass into F ("XFER BYTE
     FROM AB F2-9 FROM CD F50-57").
   - It then hands over: "PAU SRART [sic] UFL [sic] MULT 56.34.00"; "WAIT
     FOR PAU TO MULT AND XFER RESULT TO AB 12-107" (3.11.1); "PAU START
     MULTIPLY 56.34.00" → "PAU DO VFL MPYC" (3.11.10).

**The divider is shared the same way.** 3.11.8: "SIGNAL PAU TO START
NORM. (TON VFL DIVISOR)", "PAU START VFL DIVIDE 56.33.10", "PAU DO VFL
DIVIDE 56.34.00", then a "PAU FINISHED" wait loop. 3.8.19 (reused):
"REDUCTION CYCLES JUST LIKE FP". So `mkDivBox` is the same unit by the
CE manual too, not only by Buchholz p.208.

**What this means for the model (DERIVED).**
- `mkVflBox`'s multiplier and `mkFpBox`'s are one PAU.
- VFL `*` is SAU byte-assembly, then the FP multiply sequence from MR1
  (3.8.11's CSA loops I-IV and the main adder loop), with the exponent
  path skipped ("SHIFT = 0"), then the SAU again.
- A4's `mkPAU` should take the VFL request as a second request kind into
  the same sequencer. A3's `mkSAU` issues it and waits on the PAU's
  finish, as the flows draw.
- The merge stays behaviour-neutral while only one instruction is in the
  E-box, as NEXT.md says.

## 7. The length of D/ (`NEXT.md` "D/ AND THE LAAR")

**What the charts settle.**
- **D/ = `/` up to `/`'s END OP point (period 22 on 3.8.15 sheet 2), then
  3.8.16:**
  - the 49th-quotient-bit trial (22-23);
  - TC (24), MR3 (25);
  - one T3,T4 remainder-normalization pair per shift of six (26-27,
    28-29, ...);
  - END OP on (T3,NE SH≤6).
- **Counted:** `/` + 5 for one remainder pass, + 2 per further pass.
  Table 2 says `/` + 6 (+2). **The chart is one period shorter**, the
  same direction as SRD and zero-divisor `/` (§3).
- **The quotient leaves at period 25**, mid-operation: "ACOB LATCH",
  "SAMPLE ACC 12-63 (61-63 ALWAYS ZERO)", "SAMPLE DIVIDE INDICATORS".
  That is three periods after `/`'s END OP point and before the remainder
  work ends.
- **The remainder leaves by a second ACOB LATCH** at the period after END
  OP (30 in the example), with "SAMPLE REMAINDER INDICATORS".
  - Its fraction goes "TO A CHECKER" (29-30) and its exponent "TO
    CHECKER". The exponent was routed through D: "READ OUT BACD 64 TGR
    (ROUTES D EXP TO SAU ADDER)", and sheet 2's "Subtract "48" from
    Dividend Exp & Route to D Reg. Used as Remainder Exp on Divide
    Double".
  - So the remainder is ready for a store the period after END OP, like
    any other result. The chart shows **no extra wait** for a memory
    store.
  - The route from ACOB to the store ABC and the LAAR is Fig. 3.2.21's
    (cited in NEXT.md), not this chart's.

**What the charts do not settle.** Whether the Second Divide Cycle (SDC)
is a loop of its own, the open question behind NEXT.md's V3. Sheet 2 was
not re-transcribed here. Its SDC row ("(D3, DVND, DVDE) Second Divide
Cycle Trigger (SDC)" at 11, with "Gate 47 / Gate 48 to Shift Counter") is
drawn once at period 11 in the example, and the sheet gives no rule for
whether it repeats. **Still open.**

**Bearing on the decision.**
- The atlas's D/ − `/` = 7 clocks (NEXT.md) is the chart's two-pass
  figure (/ + 7), or Table 2's one-pass + 1. The atlas operands decide
  which, and they were not checked here.
- Under the chart, a D/ whose remainder needs one normalization pass is
  `/` + 5. A model charging Table 2's `/` + 6 is one long. It would then
  need one clock from somewhere else (the LAAR head gate) to match the
  atlas.
- So the chart **weakens** the case for "Table 2 + 1" accounting. It
  supports finding the 7 in the remainder normalization (two passes)
  instead.
- DERIVED. Test it before building: the atlas page's D/ operands give the
  remainder's leading-zero count, and with it the pass count.

## 8. Contradictions with what the model or the docs now claim

1. **`ebox_roadmap.md` says there are "nineteen" PAU charts (line 592).**
   There are twenty: Fig. 3.8.20, Reciprocal Divide, PDF 244, printed
   8-24, 1/1/63 (Index 3-2, PDF 58).
2. **`ebox_roadmap.md` lines 645 and 859, "[NOT IN THE SOURCES]" for
   divide bits-per-cycle.** Stale: Buchholz Figs 14.11-14.12 (pp.214-215,
   PDF 239-240) print the rule. `StretchDivBox.bsv` already uses it.
   `mkFpDivBox`'s `divBitsPerCycle = 6` and `coreDivBitsPerCycle = 24`
   remain marked INVENTED in the bsv, correctly.
3. **3.8.9's printed page** is 8-8 (PDF 232), not "—" (`ebox_roadmap.md`
   table).
4. **3.8.15's own cross-references** say "PART C, SHEET 3". Part C is on
   sheet 2 (PDF 240); sheet 3 holds Parts E-G. 3.8.16's page head ("SEE
   SHEET 2") is right. This matters to anyone navigating by the chart's
   own words.
5. **`NEXT.md` "ONE PARALLEL-UNIT MULTIPLIER, NOT TWO", "open".** The CE
   manual settles it as one (§6), and the divider too.
6. **`mkDecBox`'s `decDigitsPerCycle` (32 bits a clock)** and
   **`mkCvtBox`'s `cvtBitsPerCycle = 16`** are not the drawn rates.
   - The serial step is a byte pair per 0.6 µs (2 clocks).
   - Conversion is one digit (D→B) or one bit (B→D) a pass.
   - NEXT.md already calls the first CHOSEN, not sourced; this gives the
     drawn rate for both.
7. **D/ chart length** is `/` + 5 (+2 per further remainder pass), one
   less than Table 2's + 6 (+2) (§7). Whatever the model charges from
   Table 2 for D/ is one clock longer than the 1962 chart.
8. **SRD** is three chart periods against Table 2's four. **`*+`** is
   11 or 14 against 20. The model charges Table 2 for each
   (`ebox_roadmap.md`: `*+` 20). SLØ is *not* in this list: 3.8.9 has a
   break mark that elides the 48-place shift loop (§3 note a).
   - Not a model bug: Table 2 is a source.
   - But two sources disagree, and the model sides with the older one
     without saying so.

## 9. Appendices: the parallel readers' transcriptions

Appendices A-E are the four readers' working transcriptions, kept close
to verbatim. Each says how it was read.
- Tile file names refer to crops of the (deleted) 300 dpi renders, named
  by crop origin.
- In Appendix B, names like `237_r850_c3450` are 150% crops of page
  237 at row 850, column 3450.
- Their "period n" runs from rising edge n to rising edge n+1. Edges were
  placed by eye or by a small edge-measuring script, ±0.1 period.

The appendices are:
- Appendix A: Figs 3.8.1-3.8.8.
- Appendix B: 3.8.9-3.8.14.
- Appendix C: 3.8.17, 3.8.20, 3.11.12-3.11.14.
- Appendix D: 3.11.2-3.11.7.
- Appendix E: 3.11.9, 3.11.11.

### Appendix A

#### R23-9732 PAU timing charts, Figs 3.8.1 - 3.8.8 (transcriber A)

Method: 300 dpi page PNGs, cropped tiles 1300x1250 px read with the image viewer; no OCR.
Tiles are in [scratch, deleted]/tA/
(name tPPP_X_Y.png = PDF page PPP, crop origin X,Y in full-page pixels).
Period assignment is DERIVED by comparing the x position of each waveform edge with the
FP CLOCK rising edges. The pixel x values quoted are ESTIMATED BY EYE from tile offsets (not
measured programmatically) and are good to roughly +/-20 px; each period assignment was
cross-checked against the downscaled page overview (ovPPP.png), where edges line up visibly. "Period n" = from the rising edge
numbered n to the rising edge numbered n+1. "1st half"/"2nd half" = clock high/low half.
Glyph conventions (apply to all figures): the trigger names inside conditions are printed with a
small raised/subscript letter ("To", "Tc", "T1"...). They are transcribed T0, TC, T1. Where the same
"To" glyph is followed by ACC/MEM/STORE ("To ACC", "To MEM", "To STORE", "To END OP") it may be the
English word TO rather than trigger T0; the glyph does not decide it. Rows give the reading as it
looks; the TO/T0 question is flagged where it matters. The ampersand is a hand-lettered glyph like a
struck "f"/"E"; transcribed "&".
A/B pulses: no figure draws a separate A or B pulse line. The word "TOB" appears in "SAMPLE TOB ..."
(3.8.2, 3.8.3, 3.8.4); it is printed as one word (z227_sampletob.png shows the pulse label "( SAMPLE TOB)").
DERIVED/unverified: TOB may be a register or bus name (e.g. "transfer output bus"), or T0 + "B";
the print does not say. Flagged, not resolved.
Header on every page: "M3-04-3" (top left), "PAU TIMING CHARTS" (top right).

---------------------------------------------------------------------------------------------
#### Fig 3.8.1  FLOATING-POINT LOAD (TIMING)

- Title as printed: "FIGURE 3.8.1. FLOATING-POINT LOAD (TIMING)". No sheet number printed.
- PDF page 225; page foot "8-1"; date at foot "2/1/62".
- Tiles: t225_200_150.png, t225_1150_150.png, t225_200_1050.png, t225_1150_1050.png, t225_200_1950.png, t225_1150_1950.png

#### Printed note (top right, verbatim)
"EXAMPLE SHOWS TWO NORMALIZATION SEQUENCES.  LOAD WITH FLAG IS THE SAME EXCEPT FLAG BITS ROUTED TO SIGN BYTE REGISTER ON LAST SAMPLE."

#### Clock axis
"FP CLOCK": square wave, 7 numbered periods, numbered 0 1 2 3 4 5 6 (the "0" is faint, printed like ")" -- read as 0 from position). Rising edges at x ~578, 800, 1025, 1250, 1475, 1697, 1922; period ~225 px. No A/B pulses drawn. No other clock line.

#### Signals as drawn (condition in parentheses exactly as printed, then label; DERIVED period span)
| Line | Printed set condition | Label | On (DERIVED) | Printed reset / trailing label |
|---|---|---|---|---|
| T0 | (START CTRL) | T0 | period 0 | - |
| T3 #1 | (T0. LD) | T3 | period 1 | - |
| T3 #2 | (T4, NOT END OP. NOT INT) | T3 | period 3 | - |
| T4 #1 | (T3) | T4 | period 2 | - |
| T4 #2 | (T3) | T4 | period 4 | - |
| TC #1 | (T3,NE) | TC | period 2 | - |
| TC #2 | (T3, NE) | TC | period 4 | - |
| sample pulse | (START CTRL) | "SAMPLE TO C & EXECUTION REGS." | 1st half of period 0 | - |
| | (START CTRL) | FIRST CYCLE TGR | periods 0-1 | "(FCT)" written after the fall |
| | (FCT, LD) | GATE 33 | periods 0-1 | - |
| | (FCT, LD) | EXPONENT ROUTING CONTROL TGR | periods 0-2 | "(TP6)" written at the fall (reset) |
| | (T0, LD) | NORMALIZE EXPONENT TGR (NE) | periods 1-4 | - |
| | (T0, LD) | GATE 61 & 63  (TGR) | periods 1-4 | - |
| | (T0, TO ACC) | WRITE EXPONENT A TGR | period 1 onward, line continues past period 6 (no fall drawn) | - |
| | (T3, NE) | NORMALIZE MANTISSA TGR | periods 2-4 | "(NM)" after the fall |
| | (no condition printed) | SAMPLE TEST COMP | period 2 (full period) | - |
| | (T3, NE,SHIFT <=6) | END OP | period 4 | "(TGR)" after the fall |
| | (END OP, TEST COMP) | GATE 11 & 12 | 2nd half of period 4 through 1st half of period 5 | - |
| | (TC, END OP, NOT INT) | LATCH ACOB | period 5 onward, line continues past period 6 | - |
| | (T0 ACC, T0 END OP, NOT INT) [glyphs "To ACC", "To END OP"; see glyph note] | (unlabelled pulse; note "A REG SAMPLE-SECOND SAMPLE WILL OCCUR IF THIS IS A DOUBLE OPERATION(FROM A CHECKER)") | 1st half of period 5 | - |
| EXP LATCH #1 | (TC,NM) | EXP LATCH | period 3 | - |
| EXP LATCH #2 | (TC, END OP. NOT INT) | EXP LATCH | period 5 | note with arrow: "ALSO USED AS INDICATOR LATCH" |
| EXP SAMPLE #1 | (TC,NM) | EXP SAMPLE | period 3 | - |
| EXP SAMPLE #2 | (TC, END OP NOT INT) | EXP SAMPLE | period 5 | - |
| F REG LATCH & SAMPLE | (T0) | pulse | 1st half of period 1 | - |
| | (T3.NE) | pulse | 1st half of period 2 | - |
| | (T3.NE) | pulse | 1st half of period 4 | "& (ALSO USED FOR SHIFT REGISTER)" |

Note on "&": the manual's ampersand is a hand-lettered "&"-like glyph (looks like a struck "f"); transcribed as "&" ("SAMPLE TO C & EXECUTION REGS.", "GATE 61 & 63", "GATE 21 & 22", "GATE 11 & 12", "F REG LATCH & SAMPLE").

Note on conditions: the T-names inside parentheses are printed with a subscript-like letter ("To", "Tc"); read as T0, TC. "(T0 ACC, T0 END OP, NOT INT)" is printed "(To ACC, To END OP, NOT INT)" -- DERIVED reading "TO ACC, TO END OP" (i.e. the word TO, compare "(T0, TO ACC)" on the WRITE EXPONENT line, where the first is subscripted To and the second plainly "TO"). ILLEGIBLE-ish: whether the "To" in that line is T-sub-0 or the word "TO" cannot be decided from the glyphs (t225_1150_1050.png); the context "TO ACC" / "TO END OP" (operation types) suggests the word TO (DERIVED).

#### Loop brackets drawn under the chart (verbatim)
- "ADDER LOOP 1": arrow from left of period 0 (x~518) to start of period 2 (x~1030).
- "ADDER LOOP 2": from start of period 2 to start of period 4 (x~1490).
- "EXPONENT LOOP 1": from start of period 1 (x~810) to start of period 3 (x~1260).
- "EXPONENT LOOP 2": from start of period 3 to middle of period 5 (x~1805).
DERIVED: the exponent loop lags the adder loop by one FP clock period.

#### Cycle table (DERIVED from edge positions)
| Period | On / rising |
|---|---|
| 0 | (START CTRL) T0; (START CTRL) SAMPLE TO C & EXECUTION REGS. (1st half); (START CTRL) FIRST CYCLE TGR; (FCT, LD) GATE 33; (FCT, LD) EXPONENT ROUTING CONTROL TGR |
| 1 | (T0. LD) T3; FIRST CYCLE TGR, GATE 33, EXP ROUTING CTRL still on; (T0, LD) NORMALIZE EXPONENT TGR (NE) rises; (T0, LD) GATE 61 & 63 rises; (T0, TO ACC) WRITE EXPONENT A TGR rises; F REG LATCH & SAMPLE (T0) pulse, 1st half |
| 2 | (T3) T4; (T3,NE) TC; (T3, NE) NORMALIZE MANTISSA TGR rises; (T3, NE) GATE 21 & 22 rises; SAMPLE TEST COMP; F REG LATCH & SAMPLE (T3.NE) pulse 1st half; EXPONENT ROUTING CONTROL TGR falls at end (TP6) |
| 3 | (T4, NOT END OP. NOT INT) T3; (TC,NM) EXP LATCH; (TC,NM) EXP SAMPLE |
| 4 | (T3) T4; (T3, NE) TC; (T3, NE,SHIFT <=6) END OP; F REG LATCH & SAMPLE (T3.NE) pulse 1st half; (END OP, TEST COMP) GATE 11 & 12 rises mid-period; NE, GATE 61&63, NM, GATE 21&22 fall at end |
| 5 | (TC, END OP, NOT INT) LATCH ACOB rises (stays on); (T0 ACC, T0 END OP, NOT INT) A-reg sample pulse 1st half; (TC, END OP. NOT INT) EXP LATCH; (TC, END OP NOT INT) EXP SAMPLE; GATE 11 & 12 falls mid-period |
| 6 | clock only; WRITE EXPONENT A TGR and LATCH ACOB lines continue |

#### Branches
- NE (normalize exponent) gates T3->TC, NORMALIZE MANTISSA TGR, GATE 21 & 22, F REG sample.
- END OP condition: (T3, NE, SHIFT <=6) -- printed "SHIFT ≦6". DERIVED: a normalization pass that needs a shift of 6 or less ends the op; otherwise T4 -> T3 again "(T4, NOT END OP. NOT INT)" for another 2-period loop.
- INT (interrupt?) -- "NOT INT" qualifies the T3 repeat and LATCH ACOB / EXP LATCH. Meaning not printed.

#### Lengths
- COUNTED: T0 (1) + 2 normalization loops x 2 periods (T3,T4) = periods 0-4, plus end period 5 (LATCH ACOB, EXP LATCH/SAMPLE) => 6 FP clock periods (0-5) for the two-normalization example; clock drawn for 7 (0-6).
- COUNTED: each normalization loop (T3 then T4/TC) = 2 FP clock periods; adder loop = 2 periods; exponent loop = 2 periods, lagging by 1.
- PRINTED: no cycle count printed.

---------------------------------------------------------------------------------------------
#### Fig 3.8.2  FLOATING-POINT ADD (TIMING)

- Title as printed: "FIGURE 3.8.2. FLOATING-POINT ADD (TIMING)". No sheet number printed.
- PDF page 226; page foot "8-2" (bottom left); date "2/1/62" (bottom right). Header: "PAU TIMING CHARTS" (left), "M3-04-3" (right).
- Tiles: s226_100_300.png, s226_850_300.png, s226_1500_300.png, s226_100_1100.png, s226_850_1100.png, s226_1500_1100.png, s226_100_1900.png, s226_850_1900.png, s226_1500_1900.png; zooms z226_tc.png, z226_clk.png

#### Printed note (top right, verbatim)
"EXAMPLE SHOWS A EXP. > C. C. EXP > A REPRESENTED BY DOTTED LINES. EXPONENT DIFFERENCE AMOUNT = 11. NO NORMALIZATION."
(So dashed lines = the C EXP > A case; solid = A EXP > C.)

#### Clock axis
"FP CLOCK": 8 drawn periods. Numbers printed 0, 1, 2, 3, 4 legibly; above periods 5, 6, 7 there are only faint marks -- ILLEGIBLE (faded print; z226_clk.png). Rising edges x ~400, 610, 815, 1020, 1225, 1432, 1640, 1847; last fall ~1950; period ~207 px. No A/B pulses.
Annotations printed under the clock: under period 3 "PRE SHIFT >3"; under period 4 "SHIFT CTR REG >4"; under period 5 "SHIFT CTR REG = 4".
A vertical dashed line is drawn at the start of period 2 down through the whole chart (reference line, no label).

#### Ring triggers (left label "RING TRIGGERS")
| Printed condition | Trigger | On (DERIVED) |
|---|---|---|
| (START CTRL) | T0 | period 0 |
| (T0 & ADD) | T1 | period 1 |
| (?C & ADD) | TC | period 1 -- ILLEGIBLE in part: the leading "(T" and the subscript are faint (z226_tc.png, z226_tc2.png); the subscript looks like "C" but the same line in 3.8.3/3.8.4 reads "(T0 & ADD)". Undecidable between (TC & ADD) and (T0 & ADD) |
| (T1 & PSA) | T2 | period 2 |
| (T2, PSA & SH >3) | T4 | periods 3-4, with a dashed break at start of period 4 marked "(SCR >4)" with an arrow (T4 held/re-set because SCR >4) |
| (T4 & SCR = 4) | T3 | period 5 |
| (T3) | T4 | period 6 |
| (T3 & NE) | TC | period 6 |

#### Other lines (printed condition, label, trailing label; DERIVED span)
| Condition | Label | Span | Trailing text |
|---|---|---|---|
| (START CTRL) | SAMPLE TOB TO C REG & EXECUTION REG | 1st half period 0 | |
| (START CTRL) | FIRST CYCLE TGR | periods 0-1 | |
| (FCT & ADD) | GATE A & C EXP TO SAU | periods 0-1 | |
| (T0 & ADD) | PRE SHIFT AND ADD TGR | periods 1-5 | |
| (T0 & ADD) | LPSE | period 1 | (LATE PRE-SHIFT EXPONENT STATUS TGR) |
| (LPSE) | GATE | period 1 | (GATE INITIAL PRE SHIFT AMOUNT TO SHIFT REGISTER) |
| (LPSE & EXP SUM+) | GATE 3 | period 1 | (C 12-59 TO F 2-49) |
| (LPSE & EXP SUM-) dashed | GATE 1 | period 1 | (A 12-59 TO F 2-49) |
| (T0 & TO ACC OPER) | WRITE EXPONENT A TGR | period 1 to end of drawing | |
| (SIGN - ADD) dashed / (SIGN + ADD) solid | EXPONENT ROUTING TGR (TP6) | period 1 to end | |
| (SIGN - ADD) dashed / (SIGN + ADD) solid | MANTISSA ROUTING TGR | period 1 to end | |
| (NOT MANT ROUTE TGR) | GATE 31 | periods 1-5 | (A 12-59 TO ADDER 2-49) -- the "1" of 12 is faint, reads "(A ?2-59 TO ADDER 2-49)" |
| (MANT ROUTE TGR) dashed | GATE 33 | periods 1-5 | (C 12-59 TO ADDER 2-49) |
| (TC & PSA) | NORMALIZE EXPONENT TGR | periods 2-6 | |
| (NE & NOT TP6) | GATE A EXPONENT TO SAU | periods 2-6 | |
| (NE = TP6) dashed | GATE C EXPONENT TO SAU | periods 2-6 | the connective prints as "=" (possibly a poorly printed "&"; not decidable) |
| (T2 & PSA) | GATE 71 & 72 | periods 2-4, dashed break at start of period 3 marked "(T4 & SH>4)" with arrow | |
| (T1 & SIGN MIX T/C) | GATES 21 & 22 OR 23 | periods 2-6 | (TGR) |
| (T2 IN T4 & PSA) | (unlabelled level) | periods 2-4; ticks "8 IN" at start of period 2, "4 IN" at start of period 3, "0 IN" at start of period 4 | (GATE TO SHIFT COUNTER FROM SAU & ADDER) |
| (T4, PSA & SH=4) | GATE 61 & 63 | periods 5-6 | (TGR) |
| (T3 & NE) | NORM MANT | period 6 | (TGR) |
| (T3, NE & SH<=6) | END OPR | period 6 | (TGR)  [printed "SH≤6" with the ≤ small/superscript] |
| (none) | SAMPLE TEST COMP | period 6 | (TGR) |
| F REG LATCH line: (T0) | RESET | 1st half period 1 | |
| (T2, PSA & SH >3) | SET | 1st half period 3 | |
| (T4, PSA & CTR >4) | SET | 1st half period 4 | |
| (T3 & NE) | SET | 1st half period 6 | line label "F REG LATCH" |
| (TC & PSA) | EXP LATCH | period 2 | |
| (END OP) | EXP LATCH | period 7 | |
| (END OP, NOT INT) | EXP SAMPLE | period 7 | |
| (TC, TEST COMP, END OP & NOT INT) | LATCH FRACTION ON ACOB | period 7 onward | |
| (TC & TO ACC) | pulse | 1st half period 7 | SAMPLE TO A REG |
| END OP, TEST COMP)  [opening paren not printed] | GATE 11 & 12 | 2nd half of period 6 (ends at start of period 7) | |

#### Cycle table (DERIVED)
| Period | On / rising |
|---|---|
| 0 | T0; SAMPLE TOB TO C REG & EXECUTION REG (1st half); FIRST CYCLE TGR; GATE A & C EXP TO SAU |
| 1 | T1, TC; LPSE; GATE (initial pre-shift amount to shift register); GATE 3 (C 12-59 TO F 2-49) or GATE 1 (A 12-59 TO F 2-49); PRE SHIFT AND ADD TGR, WRITE EXPONENT A TGR, EXPONENT ROUTING TGR, MANTISSA ROUTING TGR, GATE 31 / GATE 33 rise; F REG LATCH RESET (1st half) |
| 2 | T2; NORMALIZE EXPONENT TGR, GATE A (or C) EXPONENT TO SAU, GATE 71 & 72, GATES 21 & 22 OR 23, shift-counter gate ("8 IN") rise; EXP LATCH (TC & PSA) |
| 3 | T4 (PRE SHIFT >3); F REG LATCH SET (T2, PSA & SH >3) 1st half; "4 IN"; GATE 71&72 re-set (T4 & SH>4) |
| 4 | T4 again (SCR >4) (SHIFT CTR REG >4); F REG LATCH SET (T4, PSA & CTR >4) 1st half; "0 IN"; GATE 71&72, shift-counter gate end |
| 5 | T3 (T4 & SCR = 4) (SHIFT CTR REG = 4); GATE 61 & 63 rises; PRE SHIFT AND ADD TGR, GATE 31/33 end |
| 6 | T4 (T3), TC (T3 & NE); NORM MANT; END OPR; SAMPLE TEST COMP; F REG LATCH SET (T3 & NE) 1st half; GATE 11 & 12 2nd half; NE, GATE A/C EXP TO SAU, GATES 21&22 OR 23, GATE 61&63 end |
| 7 | EXP LATCH (END OP); EXP SAMPLE; LATCH FRACTION ON ACOB rises; SAMPLE TO A REG (1st half) |

#### Branches
- Exponent compare: EXP SUM+ -> GATE 3 (C 12-59 TO F 2-49); EXP SUM- (dashed) -> GATE 1 (A 12-59 TO F 2-49).
- Sign/add: (SIGN + ADD) solid vs (SIGN - ADD) dashed set the EXPONENT ROUTING TGR (TP6) and MANTISSA ROUTING TGR; NOT MANT ROUTE TGR -> GATE 31 (A to adder), MANT ROUTE TGR -> GATE 33 (C to adder); NE & NOT TP6 -> GATE A EXPONENT TO SAU, NE = TP6 -> GATE C EXPONENT TO SAU.
- T1 & SIGN MIX T/C -> GATES 21 & 22 OR 23 (DERIVED: true/complement adder gating).
- Pre-shift: (T2, PSA & SH >3) -> T4 (pre-shift loop); "(SCR >4)" keeps T4 for another period; (T4 & SCR = 4) -> T3. GATE 61 & 63 on (T4, PSA & SH=4). Shift counter ticks 8 IN / 4 IN / 0 IN. DERIVED: with SH <=3 the T4 pre-shift loop is skipped (condition "SH >3" printed only for the drawn branch; the other path is not drawn).
- END OPR on (T3, NE & SH<=6); NORM MANT on (T3 & NE). The example has no normalization.

#### Lengths
- COUNTED: 8 FP clock periods (0-7) for exponent difference 11, no normalization; period 7 is the end period (EXP LATCH, EXP SAMPLE, LATCH FRACTION ON ACOB, SAMPLE TO A REG).
- COUNTED: pre-shift loop T4 occupies periods 3 and 4 (2 periods) for the difference of 11 (8 IN, 4 IN, 0 IN).
- PRINTED: no cycle count printed.
- Mentions the SAU explicitly: "GATE A & C EXP TO SAU", "GATE A EXPONENT TO SAU", "GATE C EXPONENT TO SAU", "(GATE TO SHIFT COUNTER FROM SAU & ADDER)". Register field widths printed: A 12-59, C 12-59, F 2-49, ADDER 2-49.

---------------------------------------------------------------------------------------------
#### Fig 3.8.3  FLOATING POINT-ADD TO MAGNITUDE (TIMING)

- Title as printed: "FIGURE 3.8.3. FLOATING POINT-ADD TO MAGNITUDE (TIMING)" (hyphen placed after POINT as printed). No sheet number.
- PDF page 227; page foot "8-3" (bottom right); date "2/1/62" (bottom left). Header "M3-04-3" left, "PAU TIMING CHARTS" right.
- Tiles: s227_100_300.png, s227_850_300.png, s227_1500_300.png, s227_100_1100.png, s227_850_1100.png, s227_1500_1100.png, s227_100_1900.png, s227_850_1900.png, s227_1500_1900.png

#### Printed note (verbatim)
"EXAMPLE SHOWS C EXP> A AND FORCED ZERO FRACTION."

#### Clock axis
"FP CLOCK": 8 periods, numbered 0 1 2 3 4 5 6 7 (all legible). Rising edges x ~470, 677, 885, 1092, 1300, 1505, 1712, 1920; last fall ~2020. No A/B pulses. Vertical dashed reference line at start of period 2.

#### Glyph note
In this figure the conjunction in several conditions is printed as a "4"-like glyph: "(FC+4 ADD)", "(T0 4 ADD)", "(T0 4 TO ACC OPER)". Transcribed verbatim. DERIVED: these are the same "&" as elsewhere, i.e. (FCT & ADD), (T0 & ADD), (T0 & TO ACC OPER) -- compare the same lines in Fig 3.8.2. Not certain; the printed text is as given.

#### Ring triggers ("RING TRIGGERS")
| Printed condition | Trigger | On (DERIVED) |
|---|---|---|
| (START CTRL) | T0 | period 0 |
| (T0 & ADD) | T1 | period 1 |
| (T0 & ADD) | TC | period 1 |
| (T1 & PSA) | T2 | period 2 |
| (T2, PSA & SN ? 3) | T3 | period 3  ["SN" as printed; DERIVED likely SH. The relation glyph is a single small solid square/dot (z227_sn3.png): ILLEGIBLE between "=" and "≤"] |
| (T3) | T4 | period 4 |
| (T3 & NE) | TC | period 4 |
| (T4- NOT END OP) | T3 | period 5 |
| (T3) | T4 | period 6 |
| (T3 & NE) | TC | period 6 |

#### Other lines
| Condition | Label | Span (DERIVED) | Trailing text |
|---|---|---|---|
| (START CTRL) | pulse | 1st half period 0 | ( SAMPLE TOB) |
| (START CTRL) | FIRST CYCLE TGR | periods 0-1 | |
| (FC+4 ADD) | GATE EXPONENTS TO SAU | periods 0-1 | |
| (T0 4 ADD) | PRE-SHIFT & ADD TGR | periods 1-3 | |
| (T0 4 ADD) | LPSE | period 1 | |
| (LPSE) | GATE | period 1 | (GATE TO SHIFT REGISTER AMOUNT = 3) |
| (LPSE & EXP SUM-) | GATE 1 | period 1 | |
| (T0 4 TO ACC OPER) | WRITE EXPONENT A TGR | period 1 to end of drawing | |
| (EXP SIGN- & ADD) | TPB TGR | periods 1-3 | reset arrow: "(? PERFORM AUGMENT TGR & TO ALL OPER)" -- a short vertical stroke follows "(": ILLEGIBLE whether it is a character ("1"/"I") or a blot (z227_tpb.png). "ALL" is faint but reads ALL, not ACC (z227_allop.png). "TPB TGR" is clearly B, not 6 (z227_tpb.png) |
| (EXP SIGN- & ADD) | MANTISSA ROUTING TGR | period 1 to end | |
| (MANT ROUTE TGR & PSA) | GATE 33 | periods 1-3 | |
| (TC & PSA) | NORMALIZE EXPONENT TGR | periods 2-6 | |
| (NE & TP6) | GATE C EXP TO SAU | periods 2-3 | |
| (NE & NOT TP6) | GATE A EXP TO SAU | periods 4-6 | |
| (T2 & PSA) | GATE 71 & 72 | period 2 | |
| (T1 & SIGN MIX T/C) | GATES 21 & 22 OR 23 | periods 2-6 | |
| (T2 PSA & SHIFT ? 3) [relation glyph a small solid dot, ILLEGIBLE "=" vs "≤"; z227_shift3.png] | GATE 61 & 63 | periods 3-4 | reset arrow "(PERFORM AUG & T4)" |
| (T3 & NE) | NORMALIZE MANTISSA TGR | periods 4-6 | |
| (TP6, T3, NE, SIGNS UNLIKE, RESULT TGR) | PERFORM AUGMENT | periods 4-5 | (TGR) |
| (T3 PERFORM AUG) | END OP | period 6 | (TGR) |
| (END OP & TST COMP) | GATE 11 & 12 | 2nd half period 6 through 1st half period 7 | |
| F REG LATCH line: (T0) | RESET | 1st half period 1 | |
| (T3 & NE) | SET | 1st half period 4 | |
| (T3 & NE) | RESET | 1st half period 6 | line label "F REG LATCH" |
| (TC & PSA) | EXP LATCH | period 2 | |
| (END OP) | EXP LATCH | period 7 | |
| -- | "EXPONENT SAMPLE ( NONE)" (flat line, no pulse) | | |
| -- | LATCH FRACTION / ACOB | period 7 onward | brace "0'S" |
| -- | (SAMPLE TO A REG) pulse | 1st half period 7 | brace "0'S" (both ACOB and A REG get zeros) |

#### Cycle table (DERIVED)
| Period | On / rising |
|---|---|
| 0 | T0; (SAMPLE TOB) 1st half; FIRST CYCLE TGR; GATE EXPONENTS TO SAU |
| 1 | T1, TC; LPSE; GATE (shift register amount = 3); GATE 1; PRE-SHIFT & ADD TGR, WRITE EXPONENT A TGR, TPB TGR, MANTISSA ROUTING TGR, GATE 33 rise; F REG LATCH RESET 1st half |
| 2 | T2; NORMALIZE EXPONENT TGR, GATE C EXP TO SAU, GATES 21 & 22 OR 23 rise; GATE 71 & 72; EXP LATCH (TC & PSA) |
| 3 | T3 (T2, PSA & SN = 3); GATE 61 & 63 rises; PRE-SHIFT & ADD TGR, TPB TGR, GATE 33, GATE C EXP TO SAU end |
| 4 | T4, TC; NORMALIZE MANTISSA TGR, PERFORM AUGMENT, GATE A EXP TO SAU rise; F REG LATCH SET 1st half; GATE 61 & 63 ends (PERFORM AUG & T4) |
| 5 | T3 (T4- NOT END OP); PERFORM AUGMENT ends |
| 6 | T4, TC; END OP; F REG LATCH RESET 1st half; GATE 11 & 12 2nd half; NE, NORMALIZE MANTISSA, GATE A EXP TO SAU, GATES 21&22 OR 23 end |
| 7 | EXP LATCH (END OP); LATCH FRACTION ACOB (0'S); SAMPLE TO A REG (0'S) 1st half |

#### Branches
- EXP SUM- -> GATE 1; EXP SIGN- & ADD -> TPB TGR and MANTISSA ROUTING TGR; NE & TP6 -> GATE C EXP TO SAU, NE & NOT TP6 -> GATE A EXP TO SAU (switch at period 4).
- Shift of 3 drawn (pre-shift amount = 3 per "(GATE TO SHIFT REGISTER AMOUNT = 3)"; conditions "SN ? 3" / "SHIFT ? 3" have an illegible relation glyph): T2 -> T3 directly (no T4 pre-shift loop as in 3.8.2).
- PERFORM AUGMENT on (TP6, T3, NE, SIGNS UNLIKE, RESULT TGR); END OP on (T3 PERFORM AUG). Forced zero fraction: ACOB and A REG receive 0'S.
#### Lengths
- COUNTED: 8 FP clock periods (0-7), period 7 being the end/latch period.
- PRINTED: none.
- SAU mentioned: "GATE EXPONENTS TO SAU", "GATE C EXP TO SAU", "GATE A EXP TO SAU".

---------------------------------------------------------------------------------------------
#### Fig 3.8.4  FLOATING-POINT COMPARE (TIMING)

- Title as printed: "FIGURE 3.8.4. FLOATING-POINT COMPARE (TIMING)". No sheet number.
- PDF page 228; page foot "8-4" (bottom left); date "2/1/62" (bottom right). Header "PAU TIMING CHARTS" left, "M3-04-3" right.
- Tiles: s228_100_300.png, s228_850_300.png, s228_1500_300.png, s228_100_1100.png, s228_850_1100.png, s228_1500_1100.png, s228_100_1900.png, s228_850_1900.png, s228_1500_1900.png

#### Printed notes (verbatim)
Right margin: "ALL INSTRUCTIONS CHART DETAILS A EXP > C EXP BY 3 OR LESS. CHART DEALS WITH COMPARE. (1) COMPARE FOR RANGE AFFECTS INDICATOR SETTING ONLY. (2) COMPARE MAGNITUDE AFFECTS SIGN MOD ONLY. (3) COMPARE MAGNITUDE FOR RANGE. (1) AND (2) ABOVE."
Bottom left: "NOTE: THE CHART SHOWS SEVERAL OPERATIONS OCCURRING AS A RESULT OF DECODED ADD CLASS INSTRUCTIONS. COMPARE IS AN ADD CLASS INST. AND THEREFORE USES MANY CONTROL LINES (USED ALSO FOR ADD)."  [the closing ")" prints as ";" -- "ADD;."]

#### Clock axis
Labelled "CLOCK" (not "FP CLOCK"). 6 periods numbered 0 1 2 3 4 5 (the "4" carries an extra tick mark "4·"). Rising edges x ~585, 795, 1005, 1212, 1418, 1628; last fall ~1735. A vertical dashed line is drawn at the start of period 4 down the whole chart. No A/B pulses.

#### Ring triggers ("RING TRIGGERS")
| Printed condition | Trigger | On (DERIVED) |
|---|---|---|
| (START CTRL) | T0 | period 0 |
| (T0 & ADD) | T1 | period 1 |
| (T0 & ADD) | TC | period 1 |
| (T1 & PSA) | T2 | period 2 |
| (T2, PSA & SH <= 3) | T3 | period 3  [printed "SH ≤ 3"] |
| (T3) | T4 | period 4 |
| (T3 & NE) | TC | period 4 |

#### Other lines
| Condition | Label | Span (DERIVED) | Trailing text |
|---|---|---|---|
| (START CTRL) | pulse | 1st half period 0 | SAMPLE TOB TO C & EXECUTION REG. |
| (START CTRL) | FIRST CYCLE TGR | periods 0-1 | |
| (FCT & ADD) | GATE A & C EXP TO SAU | periods 0-1 | |
| (T0 & ADD) | PRE-SHIFT AND ADD TGR | periods 1-3 | |
| (T0 & ADD) | LPSE | period 1 | (LATE PRE-SHIFT EXPONENT STATUS TGR) |
| (LPSE) | GATE | period 1 | (GATE SHIFT AMOUNT TO SHIFT REG) |
| (LPSE + SUM +) | GATE 3 | period 1 | (C 12-59 TO F 2-49) |
| (SIGN + ADD) with a dashed box and arrow to the rise | EXPONENT ROUTING TGR (TP6) | period 1 to end | |
| (SIGN + ADD) with dashed box and arrow | MANTISSA ROUTING TGR | period 1 to end | |
| (PSA AND NOT MANTISSA ROUTE) | GATE 31 | periods 1-3 | (A 12-59 TO ADDER 2-49) |
| (T0 & PSA) | NORMALIZE EXPONENT TGR | periods 2-4 | (condition printed "To", not "Tc" as in 3.8.2/3.8.3) |
| (NE & NOT TP6) | GATE A EXP TO SAU | periods 2-4 | |
| (T2 & PSA) | GATE 71 & 72 | period 2 | |
| (T1 & SIGN MIX T/C) | GATE 21 & 22 OR 23 | periods 2-4 | (TGR) |
| (T2, PSA, & SH ? 3) [relation glyph a small solid dot, ILLEGIBLE "=" vs "≤"; z228_sh3.png. Compare the T3 line on this page which prints a clear "≤ 3"] | GATE 61 & 63 | periods 3-4 | (TGR) |
| (T3 & NE) | NORM MANT | period 4 | (TGR) |
| (T3, NE & SH <= 6) | END OP | period 4 | (TGR) [printed "SH≤6" with underlined ≤] |
| (none) | SAMPLE TEST COMP | period 4 | (TGR) |
| (END OP & TEST COMP) | GATE 11 & 12 | 2nd half period 4 through 1st half period 5 | |
| F REG LATCH line: T0 (no parentheses) | RESET | 1st half period 1 | |
| (T3 & NE) | SET | 1st half period 4 | label "F REG LATCH" |
| (TC & PSA) | EXP LATCH | period 2 | |
| (END OP) | OP LATCH | period 5 | printed "OP LATCH" (the parallel line in 3.8.2/3.8.3 reads "EXP LATCH"; verbatim here is "OP LATCH") |
| -- | "EXP SAMPLE (NONE)" flat line | | |
| (TC, END OP, NOT INT) | LATCH FRACTION (ACOB) | period 5 onward | |
| -- | "SAMPLE ACOB (NONE)" flat line | | |
| (END OP T0 & NOT INT) | INDICATOR LATCH | rises at period 5 (no fall drawn) | ["To" carries a dot/tick above] |
| (END OP, TC, NOT INT & DECODED K OR KMG OR DECODED KR OR KMGR AND AH ON) | pulse | 1st half period 5 | (IND SAMPLE) |

#### Cycle table (DERIVED)
| Period | On / rising |
|---|---|
| 0 | T0; SAMPLE TOB TO C & EXECUTION REG. (1st half); FIRST CYCLE TGR; GATE A & C EXP TO SAU |
| 1 | T1, TC; LPSE; GATE (shift amount to shift reg); GATE 3 (C 12-59 TO F 2-49); PRE-SHIFT AND ADD TGR, EXPONENT ROUTING TGR (TP6), MANTISSA ROUTING TGR, GATE 31 rise; F REG LATCH RESET 1st half |
| 2 | T2; NORMALIZE EXPONENT TGR, GATE A EXP TO SAU, GATE 21 & 22 OR 23 rise; GATE 71 & 72; EXP LATCH |
| 3 | T3 (T2, PSA & SH <= 3); GATE 61 & 63 rises |
| 4 | T4, TC; NORM MANT; END OP; SAMPLE TEST COMP; F REG LATCH SET 1st half; GATE 11 & 12 rises 2nd half |
| 5 | OP LATCH (END OP); LATCH FRACTION (ACOB) rises; INDICATOR LATCH rises; IND SAMPLE pulse 1st half; GATE 11 & 12 ends mid-period |

#### Branches
- SH <= 3 drawn (no pre-shift loop): T2 -> T3. Compare variants by note: range -> indicators only; magnitude -> sign mod only; magnitude for range -> both.
- IND SAMPLE only for decoded K or KMG or KR or KMGR with AH ON (DERIVED: compare op-code variants; AH = "A high"? meaning not printed).
- No exponent sample and no ACOB sample in compare ("(NONE)").

#### Lengths
- COUNTED: 6 periods (0-5) for A EXP > C EXP by 3 or less.
- PRINTED: none.
- SAU mentioned: "GATE A & C EXP TO SAU", "GATE A EXP TO SAU".

---------------------------------------------------------------------------------------------
#### Fig 3.8.5  FLOATING-POINT ADD TO FRACTION (TIMING)

- Title as printed: "FIGURE 3.8.5. FLOATING-POINT ADD TO FRACTION (TIMING)". No sheet number.
- PDF page 229; page foot "8-5" (bottom right); date "2/1/62" (bottom left). Header "M3-04-3" left, "PAU TIMING CHARTS" right.
- Tiles: s229_100_300.png, s229_850_300.png, s229_1500_300.png, s229_100_1100.png, s229_850_1100.png, s229_1500_1100.png, s229_100_1900.png, s229_850_1900.png, s229_1500_1900.png; zoom z229_clk.png

#### Printed note (verbatim)
"EXAMPLE SHOWS 2 NORMALIZATION CYCLES. NOTE: NO EXPONENT ADD OCCURS; THIS RESULTS IN A ZERO EXPONENT DIFFERENCE CAUSING A ZERO PRE-SHIFT."
Bottom right (arrow to the A REG sample pulse): "NOTE: SECOND SAMPLE FOR DOUBLE PRECISION. NUMBER IS UNDER CHECKER CTRL"  [printed "PRECISION.NUMBER IS" with no space]

#### Clock axis
"FP CLOCK": 8 periods numbered 0 1 2 3 4 5 6 7 (italic-style numerals, legible). Rising edges x ~468, 675, 880, 1090, 1297, 1503, 1710, 1918; last fall ~2020. The low half after period 5 prints broken/faint (z229_clk.png) -- DERIVED: print quality, not a drawn break. No A/B pulses.
Clock annotations: under period 3 "PRE-SHIFT ≤3"; under period 4 "SHIFT >6"; at the start of period 6, beside a vertical dashed line drawn down the chart, "SHIFT ≤6".

#### Ring triggers ("RING TRIGGERS")
| Printed condition | Trigger | On (DERIVED) |
|---|---|---|
| (START CTRL) | T0 | period 0 |
| (T0, ADD) | T1 | period 1 |
| (T0, ADD) | TC | period 1 |
| (T1, PSA) | T2 | period 2 |
| (T2, PSH, SH≤3) | T3 | period 3 ["PSH" as printed] |
| (T3) | T4 | period 4 |
| (T3, NE) | TC | period 4 |
| (T4 NM NOT END OP) | T3 | period 5 |
| (T3) | T4 | period 6 |
| (T3, NE) | TC | period 6 |

#### Other lines
| Condition | Label | Span (DERIVED) | Trailing |
|---|---|---|---|
| (START CTRL) | pulse | 1st half period 0 | SAMPLE TO C AND EXECUTION REGS |
| (START CTRL) | FIRST CYCLE TGR | periods 0-1 | |
| (T0, ADD) | PRE-SHIFT & ADD TGR | periods 1-3 | |
| (T0, ADD) | LPSE | period 1 | (LATE PRE SHIFT EXP STATUS TGR) |
| (EXPONENT SUM + ADD, FCT) -- "SUM + ADD FCT" drawn with a dashed over-box | EXPONENT ROUTING CONTROL TGR (TP6) | period 1 to end | |
| (EXPONENT SUM + ADD, FCT) -- same dashed over-box | MANTISSA ROUTING TGR | period 1 to end | |
| (T0, TO ACC, NOT DIVIDE) | WRITE EXPONENT A TGR | period 1 to end | |
| (LPSE EXP SUM +) | GATE 3 | period 1 | |
| (NOT MANTISSA ROUTE, PSA, DP) | GATES 31 & 32 | periods 1-3 | |
| (TC, PSA) | NORMALIZE EXPONENT TGR | periods 2-6 | |
| (NE, NOT TP6) | GATE A EXPONENT TO SAU | periods 2-6 | |
| (T1, PSA, SIGN MIX T/C) | GATES 21 & 22 OR 23 | periods 2-6 | (TGR) |
| (T2 PSA, PRE-SH ≤3) | GATE 61 & 63 | periods 3-6 | (TGR) |
| (T3, NE) | NORMALIZE MANTISSA TGR | periods 4-6 | |
| (none) | SAMPLE TEST COMP | period 6 | |
| (T3, NE, SH≤6) | END OP | period 6 | |
| (TEST COMP END OP) | GATE 11 & 12 | 2nd half period 6 through 1st half period 7 | |
| (TC, TEST COMP, END OP, NOT INT) | LATCH DATA ACOB | period 7 onward | |
| (TC & TO ACC) | SAMPLE TO A REG (pulse) | 1st half period 7 | note on DP second sample |
| F REG line: (T0) | pulse | 1st half period 1 | |
| (T3, NE) | pulse | 1st half period 4 | |
| (T3, NE) | pulse | 1st half period 6 | "F REG LATCH ALSO SHIFT REG" |
| (TC, PSA) | EXP LATCH | period 2 | |
| (TC NM) | EXP LATCH | period 5 | |
| (TC END OP, NOT INT) | EXP LATCH | period 7 | |
| (TC, NM, NOT INT) | EXP SAMPLE | period 5 | |
| (TC END OP, NOT INT) | EXP SAMPLE | period 7 | |

#### Cycle table (DERIVED)
| Period | On / rising |
|---|---|
| 0 | T0; SAMPLE TO C AND EXECUTION REGS (1st half); FIRST CYCLE TGR |
| 1 | T1, TC; LPSE; GATE 3; PRE-SHIFT & ADD TGR, EXPONENT ROUTING CONTROL TGR, MANTISSA ROUTING TGR, WRITE EXPONENT A TGR, GATES 31 & 32 rise; F REG pulse (T0) 1st half |
| 2 | T2; NORMALIZE EXPONENT TGR, GATE A EXPONENT TO SAU, GATES 21 & 22 OR 23 rise; EXP LATCH (TC, PSA) |
| 3 | T3 (PRE-SHIFT ≤3); GATE 61 & 63 rises; PRE-SHIFT & ADD TGR and GATES 31 & 32 end |
| 4 | T4, TC (SHIFT >6); NORMALIZE MANTISSA TGR rises; F REG pulse (T3, NE) 1st half |
| 5 | T3 (T4 NM NOT END OP); EXP LATCH (TC NM); EXP SAMPLE (TC, NM, NOT INT) |
| 6 | T4, TC (SHIFT ≤6); SAMPLE TEST COMP; END OP; F REG pulse 1st half; GATE 11 & 12 rises 2nd half; NE, GATE A EXP TO SAU, GATES 21&22 OR 23, GATE 61&63, NORMALIZE MANTISSA end |
| 7 | LATCH DATA ACOB rises; SAMPLE TO A REG 1st half; EXP LATCH, EXP SAMPLE (END OP) |

#### Branches
- Pre-shift <=3 (here zero): T2 -> T3 directly, GATE 61 & 63 on (T2 PSA, PRE-SH ≤3).
- Normalize: SHIFT >6 -> another loop (T4 NM NOT END OP -> T3); SHIFT ≤6 -> END OP (T3, NE, SH≤6).
- DP: GATES 31 & 32 condition includes DP; second A REG sample for double precision is under checker control (note).
- NOT DIVIDE on WRITE EXPONENT A TGR.

#### Lengths
- COUNTED: 8 periods (0-7) for zero pre-shift and 2 normalization cycles; each normalization cycle = 2 periods (T3, T4/TC).
- PRINTED: none.
- SAU mentioned: "GATE A EXPONENT TO SAU".

---------------------------------------------------------------------------------------------
#### Fig 3.8.6  FLOATING-POINT SHIFT FRACTION (TIMING)

- Title as printed: "FIGURE 3.8.6. FLOATING-POINT SHIFT FRACTION (TIMING)". No sheet number.
- PDF page 230; page foot "8-6" (bottom left); date "2/1/62" (bottom right). Header "PAU TIMING CHARTS" left, "M3-04-3" right (the "3" of M3 prints damaged).
- Tiles: s230_100_300.png, s230_850_300.png, s230_1500_300.png, s230_100_1100.png, s230_850_1100.png, s230_1500_1100.png, s230_100_1900.png, s230_850_1900.png, s230_1500_1900.png; zoom z230_t4.png

#### Printed note (verbatim)
"EXAMPLE SHOWS WHERE SHIFT>3 BUT<12 EXPONENT SIGN +, SHIFT LEFT. EXPONENT SIGN -, SHIFT RIGHT."
Annotations: "TO INITIAL SHIFT AMOUNT" (arrow to period-1 shift control reg sample), "TO RIGHT OR LEFT 4" (arrow to period-3 pulse), "NORMALLY USED FOR NORMALIZATION" (arrow to period-6 pulse).

#### Clock axis
"FP CLOCK": 8 periods numbered 0 1 2 3 4 5 6 7 (legible). Rising edges x ~440, 645, 853, 1062, 1268, 1475, 1682, 1890; last fall ~1995. Vertical dashed lines at start of period 2 and start of period 6. No A/B pulses.

#### Ring triggers (no "RING TRIGGERS" label on this page)
| Printed condition | Trigger | On (DERIVED) |
|---|---|---|
| (START CTRL) | T0 | period 0 |
| (T0, SHIFT) | T1 | period 1 |
| (T0, SHIFT) | TC | period 1 |
| (T1, PSA) | T2 | period 2 |
| (T2, PSA, SH > 3) | T4 | periods 3-4; at the start of period 4 a tick with an arrow from "(T4 .PSA , SH, CTR = 4 )" [the relation glyph is two short strokes, read "="; z230_t4.png. DERIVED: by analogy with 3.8.2's "(SCR >4)" one would expect ">4" here, but the print reads "= 4" -- flagged, not corrected] |
| (T4, PSH, SH CTR=4) | T3 | period 5 |
| (T3) | T4 | period 6 |
| (T3, NE) | TC | period 6 |

#### Other lines
| Condition | Label | Span (DERIVED) | Trailing |
|---|---|---|---|
| (START CTRL) | pulse | 1st half period 0 | (SAMPLE TO C & EXECUTION REGISTERS) |
| (START CTRL) | FIRST CYCLE TGR | periods 0-1 | |
| (FCT, SHF) | GATE C EXP TO SAU | periods 0-1 | |
| (DECODED SHF) -- "SHF" with a dashed overbar | EXPONENT ROUTING TGR (TP6) | from period 0 to end (level line, rise drawn at the label) | |
| (T0, SH) | PRE SHIFT & ADD TGR | periods 1-5 | |
| (T0, SH) | LPSE | period 1 | (LATE PRE-SHIFT EXPONENT STATUS TGR) |
| (LPSE & SAU SIGN) | GATE | period 1 | (GATE INITIAL SHIFT AMOUNT TO SHIFT REG RIGHT OR LEFT) |
| (LPSE, SHF) | GATE 1 & 2 | period 1 | |
| (T0 TO ACC NOT DIVIDE) | WRITE EXPONENT A TGR | period 1 to end | |
| (T2, PSA) | GATE | period 2 | (GATE REMAINING SHIFT AMOUNT TO SHIFT COUNTER REG) |
| (TC, PSA) | NORMALIZE EXPONENT TGR | periods 2-6 | |
| (LPSE, SHF) | GATE 21 & 22 | periods 2-6 | (TGR) |
| (T2, PSA) | GATE 71 & 72 | periods 2-4; tick marks at start of periods 3 and 4, both arrowed from "(T4 SHIFT CTR >4)" | |
| (NE, NOT TP6) | GATE A EXP TO SAU ADDER | periods 2-6 | ["SAU" prints with S like "6"] |
| (T4, PSA, SH CTR=4) | GATE 61 & 63 | periods 5-6 | (TGR) |
| (T3, NE) | NORM MANT | period 6 | (TGR) |
| (none) | SAMPLE TEST COMP | period 6 | |
| (T3, NE, NORM, SH≤6) | END OP | period 6 | |
| (END OP, TEST COMP) | GATE 11 & 12 | 2nd half period 6 through 1st half period 7 | |
| (TC, TEST COMP, END OP, NOT INT) | LATCH ACOB | period 7 onward | |
| (TC, TO ACC) | pulse | 1st half period 7 | SAMPLE TO A REG |
| (TC, PSA) | EXP LATCH | period 2 | |
| (END OP TC, NOT INT) | EXP LATCH | period 7 | |
| (END OP, TC, NOT INT) | EXP SAMPLE | period 7 | |
| (PSA) | (ALLOW SUBTRACTION OF SHIFT AMOUNT FROM SH CTR REG) | periods 1-5 | |
| SET SHIFT COUNTER REG (PSA T2) | pulse "TO 8" | 1st half period 3 | |
| (PSA T4) | pulse "TO 4" | 1st half period 4 | |
| (PSA T4) | pulse "TO 0" | 1st half period 5 | right label "SHIFT CTR REG SAMPLE GATE" |
| F REG SAMPLE GATE line: (T0) | pulse | 1st half period 1 | |
| (T2 SH>3 PSA) | pulse | 1st half period 3 | |
| (T4 PSA) | pulse | 1st half period 4 | |
| (T4 PSA) | pulse | 1st half period 5 | |
| (T3 NE) | pulse | 1st half period 6 | right label "F REG SAMPLE GATE" |
| SHIFT CONTROL REG SAMPLE GATE line: (T0) | pulse | 1st half period 1 | "TO INITIAL SHIFT AMOUNT" |
| (T2 SH>3 PSA) | pulse | 1st half period 3 | "TO RIGHT OR LEFT 4" |
| (T3, NE) | pulse | 1st half period 6 | "NORMALLY USED FOR NORMALIZATION"; right label "SHIFT CONTROL REG SAMPLE GATE" |

#### Cycle table (DERIVED)
| Period | On / rising |
|---|---|
| 0 | T0; SAMPLE TO C & EXECUTION REGISTERS (1st half); FIRST CYCLE TGR; GATE C EXP TO SAU; EXPONENT ROUTING TGR (TP6) |
| 1 | T1, TC; LPSE; GATE (initial shift amount to shift reg right or left); GATE 1 & 2; PRE SHIFT & ADD TGR, WRITE EXPONENT A TGR, ALLOW SUBTRACTION (PSA) rise; F REG SAMPLE GATE and SHIFT CONTROL REG SAMPLE GATE pulses (T0) 1st half |
| 2 | T2; GATE (remaining shift amount to shift counter reg); NORMALIZE EXPONENT TGR, GATE 21 & 22, GATE 71 & 72, GATE A EXP TO SAU ADDER rise; EXP LATCH (TC, PSA) |
| 3 | T4 (T2, PSA, SH > 3); SET SHIFT COUNTER REG "TO 8"; F REG SAMPLE GATE; SHIFT CONTROL REG SAMPLE GATE ("TO RIGHT OR LEFT 4") -- all 1st half |
| 4 | T4 again (tick, "(T4 .PSA , SH, CTR = 4 )" / "(T4 SHIFT CTR >4)"); "TO 4"; F REG SAMPLE GATE 1st half |
| 5 | T3 (T4, PSH, SH CTR=4); GATE 61 & 63 rises; "TO 0"; F REG SAMPLE GATE 1st half; PRE SHIFT & ADD TGR and ALLOW SUBTRACTION end |
| 6 | T4, TC; NORM MANT; SAMPLE TEST COMP; END OP; F REG SAMPLE GATE and SHIFT CONTROL REG SAMPLE GATE (T3, NE) 1st half; GATE 11 & 12 rises 2nd half; NE, GATE 21&22, GATE A EXP TO SAU ADDER, GATE 61&63 end |
| 7 | LATCH ACOB; SAMPLE TO A REG (1st half); EXP LATCH; EXP SAMPLE |

#### Branches
- SAU SIGN (exponent sign) chooses shift direction: + left, - right (note; "GATE INITIAL SHIFT AMOUNT TO SHIFT REG RIGHT OR LEFT").
- SH > 3 -> T4 shift loop (4 positions per T4 period, DERIVED from "TO RIGHT OR LEFT 4" and the 8/4/0 counter steps); SHIFT CTR >4 holds T4 and GATE 71 & 72; SH CTR=4 -> T3 and GATE 61 & 63.
- END OP on (T3, NE, NORM, SH≤6).

#### Lengths
- COUNTED: 8 periods (0-7) for a shift > 3 but < 12 with no extra normalization; the T4 shift loop occupies periods 3-4 (2 periods), then T3 in period 5.
- PRINTED: none.
- SAU mentioned: "GATE C EXP TO SAU", "SAU SIGN", "GATE A EXP TO SAU ADDER".

---------------------------------------------------------------------------------------------
#### PDF page 231 (landscape, two figures)
- The page image is stored landscape with the chart text upright; no rotation was needed for the figures. The page-margin furniture is rotated 90 degrees: left margin "2/1/62" (top) and "8-7" (bottom); right margin "M3-04-3" (top) and "PAU TIMING CHARTS".
- One page number for both figures: "8-7"; date "2/1/62".
- Tiles: s231_200_230.png, s231_900_230.png, s231_200_950.png, s231_900_950.png, s231_200_1650.png, s231_900_1650.png (Fig 3.8.7); s231_1700_230.png, s231_2300_230.png, s231_1700_950.png, s231_2300_950.png, s231_1700_1650.png, s231_2300_1650.png, zoom z231_t3.png (Fig 3.8.8).

#### Fig 3.8.7  FLOATING-POINT STORE (TIMING)

- Title as printed: "FIGURE 3.8.7. FLOATING-POINT STORE (TIMING)". No sheet number. PDF 231 left half; page "8-7"; "2/1/62".

#### Printed notes (verbatim)
"EXAMPLE SHOWS 2 NORMALIZATION CYCLES."
"ALSO USED AS AN INDICATOR LATCH" (arrow to second EXP LATCH); "ALSO USED FOR SHIFT REGISTER" (after F REG LATCH & SAMPLE line).

#### Clock axis
"FP CLOCK": 7 periods numbered 0 1 2 3 4 5 6. Rising edges x ~432, 618, 808, 995, 1182, 1370, 1555; last fall ~1650. No A/B pulses.

#### Lines (printed condition, label; DERIVED span)
| Condition | Label | Span | Trailing |
|---|---|---|---|
| (START CTRL) | T0 | period 0 | |
| (T0. ST) | T3 | period 1 | |
| (T4 NOT END OP, NOT INT) | T3 | period 3 | |
| (T3) | T4 | period 2 | |
| (T3) | T4 | period 4 | |
| (T3,NE) | TC | period 2 | |
| (T3,NE) | TC | period 4 | |
| (START CTRL) | pulse | 1st half period 0 | SAMPLE TO EXECUTION REG)  [closing paren only, as printed] |
| (START CTRL) | FIRST CYCLE TGR | periods 0-1 | (FCT) |
| (STORE,FCT) | GATE 31 | periods 0-1 | |
| (STORE,FCT̄) [overbar on the T of FCT, i.e. possibly NOT FCT -- DERIVED] followed by "(T0 MEM NM, EXP SAMPLE)" | EXPONENT ROUTING TGR (TP6) | rises at start of period 3, continues to end | DERIVED: the set event is "(T0 MEM NM, EXP SAMPLE)" (printed "To MEM" -- probably "TO MEM"); not certain |
| (T0 STORE) | NORMALIZE EXPONENT TGR | periods 1-4 | ["(To STORE)" -- DERIVED "TO STORE" or "T0 STORE"; glyph is the subscript-style "To"] |
| (TO STORE) | GATE 61 & 63 (TGR) | periods 1-4 | |
| (T0, TO MEM) | WRITE EXPONENT C TGR | periods 1-3 | |
| (T3,NE) | NORMALIZE MANTISSA TGR | periods 2-4 | |
| (T3, NE) | GATE 21 & 22 (TGRS) | periods 2-4 | |
| (none) | SAMPLE TEST COMP | period 2 | |
| (END OP, TO MEM) | WRITE EXPONENT D TGR | period 4 to end | |
| (T3,NE, SHIFT ≤ 6) | END OP | period 4 | |
| END OP TEST COMP [no parentheses] | GATE 11 & 12 | 2nd half period 4 through 1st half period 5 | |
| (TC, END OP, NOT INT) | LATCH ACOB | period 5 onward | |
| (TC,NM) | EXP LATCH | period 3 | |
| (TC END OP, NOT INT) | EXP LATCH | period 5 | "ALSO USED AS AN INDICATOR LATCH" |
| (TC,NM) | EXP SAMPLE | period 3 | |
| (TC END OP, NOT INT) | EXP SAMPLE | period 5 | |
| F REG LATCH & SAMPLE (T0) | pulse | 1st half period 1 | |
| (T3, NE) | pulse | 1st half period 2 | |
| (T3, NE) | pulse | 1st half period 4 | "ALSO USED FOR SHIFT REGISTER" |
| "ADDER LOOP 1" | arrow | from before period 0 (x~505) to start of period 2 | |
| "ADDER LOOP 2" | arrow | start of period 2 to start of period 4 | |
| "EXP LOOP 1" | arrow | start of period 1 to start of period 3 | |
| "EXP LOOP 2" | arrow | start of period 3 to start of period 5 (x~1365) | |

#### Cycle table (DERIVED)
| Period | On / rising |
|---|---|
| 0 | T0; SAMPLE TO EXECUTION REG (1st half); FIRST CYCLE TGR; GATE 31 |
| 1 | T3 (T0. ST); NORMALIZE EXPONENT TGR, GATE 61 & 63, WRITE EXPONENT C TGR rise; F REG LATCH & SAMPLE (T0) 1st half |
| 2 | T4, TC; NORMALIZE MANTISSA TGR, GATE 21 & 22 rise; SAMPLE TEST COMP; F REG (T3, NE) 1st half |
| 3 | T3 (T4 NOT END OP, NOT INT); EXP LATCH, EXP SAMPLE (TC,NM); EXPONENT ROUTING TGR (TP6) rises |
| 4 | T4, TC; END OP (T3,NE, SHIFT ≤ 6); WRITE EXPONENT D TGR rises; F REG (T3, NE) 1st half; GATE 11 & 12 rises 2nd half; WRITE EXPONENT C TGR ended at end of period 3; NE, GATE 61&63, NM, GATE 21&22 end at end of period 4 |
| 5 | LATCH ACOB; EXP LATCH, EXP SAMPLE (TC END OP, NOT INT); GATE 11 & 12 ends mid-period |
| 6 | clock only |

#### Branches
- (T3,NE, SHIFT ≤ 6) -> END OP; otherwise (T4 NOT END OP, NOT INT) -> T3 again (2-period normalization loop).
- TO MEM: WRITE EXPONENT C TGR during normalization, WRITE EXPONENT D TGR from END OP. DERIVED: C and D are exponent destinations (meaning not printed).

#### Lengths
- COUNTED: 6 periods (0-5) for 2 normalization cycles (clock drawn 7 periods, 0-6). Same shape as Fig 3.8.1 (FP LOAD).
- PRINTED: none.

---------------------------------------------------------------------------------------------
#### Fig 3.8.8  FLOATING-POINT STORE ROUNDED (TIMING)

- Title as printed: "FIGURE 3.8.8. FLOATING-POINT STORE ROUNDED (TIMING)" (two lines). No sheet number. PDF 231 right half; page "8-7"; "2/1/62".

#### Printed note (verbatim)
"EXAMPLE SHOWS NORMALIZATION SHIFT OF 6 OR LESS"

#### Clock axis
"FP CLOCK": 4 periods numbered 0 1 2 3. Rising edges x ~1988, 2178, 2365, 2552; last fall ~2645. No A/B pulses.

#### Lines
| Condition | Label | Span (DERIVED) | Trailing |
|---|---|---|---|
| (START CTRL) | T0 | period 0 | |
| (T0 & STORE) | T3 | period 1 | condition prints faint (z231_t3.png) but readable |
| (T3) | T4 | period 2 | ("RING TRIGGERS" label at left) |
| (T3 & NE) | TC | period 2 | |
| (START CTRL) | pulse | 1st half period 0 | SAMPLE OPERATION BITS TO EXECUTION REGISTER |
| (START CTRL) | FIRST CYCLE TGR | periods 0-1 | |
| (SRD & FCT) | GATES 31 & 32 | periods 0-1 | |
| (SRD & FCT) | GATE 61 | periods 0-2, a dashed tick at start of period 2 | |
| -- | "(61 & 63 TGRS)" with two arrows: one to the tick on GATE 61 at period 2, one to the rise of GATE 63 | | |
| -- | GATE 63 | period 2 | |
| (SRD & FCT) | SUPPRESS ADDER OUTPUT 50 & 51 | periods 0-1 | |
| (SRD & FCT) | ADD "1" TO POS 50 | periods 0-1 | |
| (STORE & FCT) -- dashed level | EXPONENT ROUTING TGR (TP6) | dashed from period 0 to end | |
| (T0 & STORE) | NORMALIZE EXPONENT TGR | periods 1-2 | |
| (T0 & TO MEM) | WRITE EXP C TGR | period 1 | |
| (END OP & TO MEM) | WRITE EXP D TGR | period 2 to end | |
| (T3 & NE) | NORM MANTISSA | period 2 | (TGR) |
| (MANTISSA RESULT TRUE, T3 & NE) | GATE 21 & 22 | period 2 (box aligned with NORM MANTISSA box above it; ov231.png, z231_g21.png) | (TGR) |
| (none) | SAMPLE TEST COMP | period 2 | |
| (MANTISSA RESULT TRUE T3, NE & SH ≤ 6) | END OP | period 2 | (TGR) |
| (END OP & TEST COMP) | GATES 11 & 12 | 2nd half period 2 through 1st half period 3 | |
| (END OP, TC, NOT INT) | EXP LATCH | period 3 | |
| (END OP) | EXP SAMPLE | period 3 | |
| F REG SAMPLE line (no condition printed) | pulse | 1st half period 1 | |
| | SET | 1st half period 2 | label "F REG SAMPLE" |
| (TC, TEST COMP, END OP, & NOT INT) | LATCH FRACTION ON ACOB | period 3 onward | |
| LATCH AND SAMPLE INDICATORS | pulse | 1st half period 3 | |

#### Cycle table (DERIVED)
| Period | On / rising |
|---|---|
| 0 | T0; SAMPLE OPERATION BITS TO EXECUTION REGISTER (1st half); FIRST CYCLE TGR; GATES 31 & 32; GATE 61; SUPPRESS ADDER OUTPUT 50 & 51; ADD "1" TO POS 50; EXPONENT ROUTING TGR (dashed) |
| 1 | T3; NORMALIZE EXPONENT TGR; WRITE EXP C TGR; F REG SAMPLE pulse 1st half |
| 2 | T4, TC; GATE 63 (61 & 63 TGRS); NORM MANTISSA; GATE 21 & 22; SAMPLE TEST COMP; END OP; WRITE EXP D TGR rises; F REG SAMPLE SET 1st half; GATES 11 & 12 rises 2nd half |
| 3 | EXP LATCH; EXP SAMPLE; LATCH FRACTION ON ACOB; LATCH AND SAMPLE INDICATORS (1st half) |

#### Branches
- SRD (DERIVED: store rounded) & FCT: in the first cycle the adder adds "1" to position 50 with adder output 50 & 51 suppressed (rounding).
- MANTISSA RESULT TRUE qualifies GATE 21 & 22 and END OP.
- Normalization shift ≤ 6 -> END OP in the first T3/T4 pass.

#### Lengths
- COUNTED: 4 periods (0-3) for normalization shift of 6 or less.
- PRINTED: none.
- Bit positions printed: "SUPPRESS ADDER OUTPUT 50 & 51", "ADD "1" TO POS 50".

---------------------------------------------------------------------------------------------
#### Summary (transcriber A)
| Fig | Op | Example drawn | Clock periods drawn | Op length COUNTED (periods, last = END/latch period) |
|---|---|---|---|---|
| 3.8.1 | FP LOAD | two normalization sequences | 7 (0-6) | 6 (0-5) |
| 3.8.2 | FP ADD | A EXP > C, exp diff 11, no normalization | 8 (0-7) | 8 (0-7) |
| 3.8.3 | FP ADD TO MAGNITUDE | C EXP > A, forced zero fraction | 8 (0-7) | 8 (0-7) |
| 3.8.4 | FP COMPARE | A EXP > C EXP by 3 or less | 6 (0-5) | 6 (0-5) |
| 3.8.5 | FP ADD TO FRACTION | zero pre-shift, 2 normalization cycles | 8 (0-7) | 8 (0-7) |
| 3.8.6 | FP SHIFT FRACTION | shift > 3 but < 12 | 8 (0-7) | 8 (0-7) |
| 3.8.7 | FP STORE | 2 normalization cycles | 7 (0-6) | 6 (0-5) |
| 3.8.8 | FP STORE ROUNDED | normalization shift <= 6 | 4 (0-3) | 4 (0-3) |
No figure prints a cycle count (PRINTED: none on all eight).
Common pattern (DERIVED): a trigger "set by (X)" turns on in the period after X; the END OP period is followed by one period with LATCH ACOB / EXP LATCH / EXP SAMPLE / A-REG sample; GATE 11 & 12 straddles that boundary (2nd half of END OP period, 1st half of next). Normalization loop = 2 periods (T3, T4/TC); pre-shift loop: T4 repeats while SCR/SHIFT CTR > 4, 4 positions per period.

#### ILLEGIBLE list (all figures)
- 3.8.2: clock numerals over periods 5, 6, 7 (faded marks only) -- z226_clk.png.
- 3.8.2: TC set condition "(?C & ADD)" -- TC vs T0 undecidable -- z226_tc.png, z226_tc2.png.
- 3.8.2: GATE C EXPONENT TO SAU condition prints "(NE = TP6)"; "=" may be a poor "&" -- s226_850_1100.png.
- 3.8.3: relation glyph in "(T2, PSA & SN ? 3)" and "(T2 PSA & SHIFT ? 3)" ("=" vs "≤") -- z227_sn3.png, z227_shift3.png.
- 3.8.3: stroke after "(" in "(? PERFORM AUGMENT TGR & TO ALL OPER)" -- z227_tpb.png.
- 3.8.4: relation glyph in "(T2, PSA, & SH ? 3)" -- z228_sh3.png.
- 3.8.1, 3.8.7: whether "To" before ACC / MEM / STORE / END OP is T0 or the word TO.
- 3.8.6: "(T4 .PSA , SH, CTR = 4 )" reads "=" though ">4" would be expected (flagged, not illegible) -- z230_t4.png.

### Appendix B

#### R23-9732 (7101 CPU CE manual) PAU timing charts, transcription set B

Transcribed from 300-dpi page images; tiles in
[scratch, deleted]/tB/
Conventions: labels quoted VERBATIM in capitals; "&" stands for the
printed ampersand-like "and" glyph (drawn as a script "f"/"&").
Timing positions were read by measuring x-coordinates of edges against
the numbered FP CLOCK rising edges in the full-resolution page (pixel
positions noted where useful); "period n" = the interval from clock
rise n to clock rise n+1. "h" = half period. DERIVED = my
interpretation; COUNTED = counted from the drawing; PRINTED = printed.

---

#### FIGURE 3.8.9. FLOATING-POINT STORE LOW ORDER (TIMING)

- Title as printed: "FIGURE 3.8.9. FLOATING-POINT STORE LOW ORDER (TIMING)"
- Sheet: single sheet (no sheet number printed).
- PDF page 232. Running head: "PAU TIMING CHARTS" (left), "M3-04-3" (right).
- Printed page number at foot: **8-8** (lower left). Issue date at foot: **2/1/62** (lower right). (tile 232foot.png)
- Printed NOTE (top right, above clock): "EXAMPLE SHOWS ONE NORMALIZATION SHIFT."
- Tiles: 232a.png (upper left), 232b.png (upper right), 232c.png (lower left), 232d.png (lower right), 232e.png / 232f.png (SAU rows zoom), 232foot.png.

#### Clock axis
FP CLOCK, drawn as square wave with rising edges numbered **0 1 2 3 4 | 5 6 7** (PRINTED numbers 0..7, first 0, last 7).
A break symbol ("){") is drawn on the FP CLOCK low half after period 4 (between 4 and 5) and on most long signals at the same place:
the loop between 4 and 5 is of indefinite length (DERIVED: one pass per normalization shift).
Full-res x of clock rises (approx.): 0=400, 1=605, 2=815, 3=1025, 4=1235, [break], 5=1440, 6=1650, 7=1860; last clock falls ~1960. One period ~ 210 px.
No A PULSES row on this chart.

#### RING TRIGGERS (rows labelled "RING TRIGGERS")
- "T0": "(START CTRL)" rises at 0, falls at 1 -> ON period 0.
- "T3": "(T0 & STORE)" rises at 1, ON period 1; falls at 2; re-rises at 3 with condition printed in the gap "(T4 & NOT END OP)" -> ON period 3; falls at 4; gap labelled "(T4 & NOT END OP)"; [break]; rises at 5 -> ON period 5; falls at 6.
- "T4": "(T3)" rises at 2 -> ON period 2; "(T3)" ON period 4 (through break, falls at 5); "(T3)" ON period 6, falls at 7.
- "TC" (printed "Tc"): "(T3 & NE)" ON period 2; "(T3 & NE)" ON period 4 (through break); "(T3 & NE)" ON period 6, falls at 7.
So ring sequence COUNTED: T0 | T3 | T4,Tc | T3 | T4,Tc | {break} | T3 | T4,Tc | end at 7.
(DERIVED) one T3/T4-TC pair = 2 FP CLOCK periods, loop condition "(T4 & NOT END OP)". See "Path length" for the conflict between this ink and the printed note.

#### Cycle table (COUNTED from edge positions)
| period | ON / rising (condition as printed) |
|---|---|
| 0 | T0 (START CTRL); "SAMPLE TO EXECUTION REGISTER" (START CTRL) pulse, first half of period 0 only; "FIRST CYCLE TGR" (START CTRL) rises, ON 0-1; "GATE 32" (SLO FCT) rises, ON 0-1; "48 TO SH CTR ADDER" (SLO FCT) rises, ON 0-1; "SHIFT CONTROL A" (SLO) rises at 0 (ON through 7); "(STORE FCT)" drawn as dashed line at 0 feeding EXPONENT ROUTING TGR |
| 1 | T3 (T0 & STORE); "NORMALIZE EXPONENT TGR" (T0 & STORE) rises; "GATE 61 & 63" (T0 & STORE) rises; "WRITE EXPONENT C TGR" (T0 & T0 MEM) rises; "LATCH & SAMPLE F REG, SHIFT REG & SHIFT COUNTER REG" row: (T0) pulse, first half of period 1; "A EXP A INPUT / SHIFT AMOUNT C INPUT } SAU" (NE & NOT TP6) rises, ON periods 1-2, falls at 3 |
| 2 | T4 (T3), TC (T3 & NE); "NORMALIZE MANTISSA TGR" (T3 & NE) rises; "GATE 21 & 22" (MANTISSA RESULT TRUE. T3 & NE) rises; "SAMPLE TEST COMP" rises, falls at 3 "(TGR)"; LATCH & SAMPLE row: (T3 NE) pulse, first half of period 2; "GATE SHIFT COUNTER REG TO SHIFT COUNTER ADDER" (SLO & NM) rises (ON through 7); FIRST CYCLE TGR, GATE 32, 48 TO SH CTR ADDER all fall at 2 (ON for periods 0-1) |
| 3 | T3 (T4 & NOT END OP); "EXPONENT ROUTING TGR (TP6)" (TO MEM & EXP SAMPLE) rises (no fall drawn; line runs to right edge past 7); "EXP LATCH" (TC & NE) ON period 3; "EXP SAMPLE" (TC & NM) ON period 3; "C EXP C INPUT & SHIFT AMOUNT A INPUT SAU ADDER" (NE & TP6) rises (no fall drawn; line runs to ~x=1935, i.e. into period 7) |
| 4 | T4 (T3), TC (T3 & NE); LATCH & SAMPLE row: (T3 NE) pulse, first half of period 4 |
| {break} | indefinite repetition |
| 5 | T3 (T4 & NOT END OP); "EXP LATCH" (TC, NE) ON period 5 (printed "(Tc, NE)" with break mark before it); "EXP SAMPLE" (TC, NM) ON period 5; END OP condition sampled here (DERIVED) |
| 6 | T4 (T3), TC (T3 & NE); "END OP" (MANTISSA RESULT TRUE, T3, NE, SH<=6) ON period 6 (falls at 7); "WRITE EXP D (TGR)" (END OP TO MEM) rises at 6 (line runs to right edge); "GATE 11 & 12" (END OP & TEST COMP) rises at 6.5, ON to ~7.5; LATCH & SAMPLE row: (T3 NE) pulse, first half of 6, labelled "LATCH & SAMPLE F REG, SHIFT REG & SHIFT COUNTER REG"; WRITE EXPONENT C TGR falls at 6 (ON 1-5) |
| 7 | "LATCH ON ACOB" (TC . TEST COMP. END OP & NOT INT) rises at 7; "LATCH & SAMP IND" pulse first half of 7 (unconditioned label "LATCH & SAMP IND"); "EXP LATCH" (TC, END OP NOT INT) ON period 7; "EXP SAMPLE" (TC, END OP NOT INT) ON period 7; NORMALIZE EXPONENT TGR, GATE 61 & 63 "(TGR)", NORMALIZE MANTISSA TGR, GATE 21 & 22 "(TGR)", SHIFT CONTROL A, GATE SHIFT COUNTER REG TO SHIFT COUNTER ADDER all fall at 7; T4/TC fall at 7 |

#### Branch conditions
- Normalization loop: T3 re-entered on "(T4 & NOT END OP)"; TC only "(T3 & NE)". Exit: "END OP" set by "(MANTISSA RESULT TRUE, T3, NE, SH<=6)" (printed "SH≤6").
- "NE" vs "NM" appear as separate conditions (EXP LATCH on "(TC & NE)", EXP SAMPLE on "(TC & NM)"); "(NE & NOT TP6)" vs "(NE & TP6)" select SAU inputs. Meanings of NE / NM / TP6 are not printed on THIS chart; but 3.8.12 and 3.8.14 print "NORM EXPONENT TGR (NE)" and "NORM MANTISSA TGR (NM)", and 3.8.12 prints "TP-6- EXPONENT ROUTING CONTROL" (DERIVED by cross-reference: NE/NM are the normalize-exponent / normalize-mantissa trigger states, not a normalized/unnormalized data test; TP6 = the exponent routing trigger). No explicit "normalized/unnormalized" branch is labelled; "MANTISSA RESULT TRUE" is a condition on GATE 21 & 22 and END OP. "(T0 & STORE)" / "(T0 & T0 MEM)" / "(TO MEM & EXP SAMPLE)" / "(END OP TO MEM)" select memory-store paths. "NOT INT" qualifies end latching.
- "TEST COMP": SAMPLE TEST COMP in period 2; GATE 11 & 12 on "(END OP & TEST COMP)".

#### Register transfers named
F REG, SHIFT REG, SHIFT COUNTER REG (latched/sampled on the "(T0)"/"(T3 NE)" pulses, periods 1,2,4,6); EXECUTION REGISTER (period 0); "SH CTR ADDER" ("48 TO SH CTR ADDER", periods 0-1); "SHIFT COUNTER ADDER" (periods 2-6); ACOB ("LATCH ON ACOB", period 7); exponent C and exponent D write tgrs; **SAU** ("A EXP A INPUT, SHIFT AMOUNT C INPUT } SAU", periods 1-2; "C EXP C INPUT & SHIFT AMOUNT A INPUT SAU ADDER" from 3). Gates 32, 61 & 63, 21 & 22, 11 & 12.

#### Path length
- CONFLICT between note and ink: the printed note says "EXAMPLE SHOWS ONE NORMALIZATION SHIFT.", but the ink draws T3 at 1, 3, [break], 5, i.e. at least three T3/T4-TC pairs (and the break means an indefinite number in between). Compare 3.8.12 and 3.8.14, where "TWO NORMALIZATION SEQUENCES / CYCLES" are drawn as exactly two T3/T4 pairs. I do not resolve the conflict; the T3/T4 pair should NOT be read as "one pass per shift".
- As drawn, excluding the break: clock 0..7 = 8 periods: T0 (0) + 3 pairs x 2 periods (1-6) + the end/latch period 7 (COUNTED). Generally T0 + 2n + 1 for n drawn pairs (DERIVED). END OP is ON in period 6; latch period 7.
- No count printed.

#### ILLEGIBLE
- None outright. The ampersand glyph is rendered as "&" throughout. "(T0 & T0 MEM)" on WRITE EXPONENT C TGR is as the ink reads (second "T0" drawn like "To"); 3.8.10 prints "(T0 & TO MEM)" for the same signal, so "TO MEM" (to memory) is the likely meaning (DERIVED; 232a.png). The precise falling edge of "A EXP A INPUT ... SAU" (x~1040 full-res, i.e. at 3) is from 232e.png.

---

#### FIGURE 3.8.10. FLOATING-POINT STORE ROOT (TIMING) (SHEET 1 OF 2)

- Title as printed: "FIGURE 3.8.10. FLOATING-POINT STORE ROOT (TIMING) (SHEET 1 OF 2)"
- PDF page 233. Page is landscape (3300x2550); the chart reads correctly in the file's NATIVE orientation (time left to right); the running head "M3-04-3" / "PAU TIMING CHARTS" and the foot run sideways along the short edges. No rotation was needed to read the chart (tiles cut from the native image, copied to tB/p233n.png).
- Printed page number at foot: **8-9**. Issue date at foot: **2/1/62**. (tile 233foot.png, cut from the -90-rotated copy tB/p233r.png)
- Tiles: 233L1.png, 233L2.png (left panel), 233R1.png, 233R2.png, 233R3.png, 233R4.png (right panel), 233z1.png (root-bit / RFL zoom), 233z2.png (SCR / adder-output zoom). Edge x-positions measured with a column-darkness script (tB/tools/edges.py (copy of [scratch, deleted]/tools/edges.py)) on p233n.png.

The sheet has TWO panels with two different time axes.

#### Left panel: "INSTRUCTION DECODING AND INITIAL PREPARATION UNDER PAU CONTROL" (printed heading)
Clock axis: FP CLOCK, rising edges numbered **0 1 2 3** (PRINTED); rises at full-res x = 481, 650, 819, 990; last fall 1076; period ~170 px. Period 3 is drawn only as the hand-over to the SAU.

| period | ON / rising (condition as printed) |
|---|---|
| 0 | "T0" (START CTRL); "SAMPLE" (START CTRL) pulse, first half of 0, annotated "(TO EXECUTION REGISTER)"; "FIRST CYCLE TGR" (START CTRL) rises, ON 0-2; "EXPONENT ROUTING TGR (TP6)" (SSQ FST) rises (line runs off the panel right with a break mark, no fall); "GATE 31" (SSQ FST) ON 0-2; "GATE 61" (SSQ FST) ON 0-2; "DECODE FOR SHIFT OF ZERO OR R1" (SSQ FST & A REG BIT 10) ON 0-2 |
| 1 | "T3" (T0 & SSQ FST); "WRITE EXPONENT C TGR" (T0 & TO MEM) rises (runs off panel with break mark); F REG LATCH "RESET" (T0) pulse, first half of 1 |
| 2 | "T4" (T3); "SAMPLE TEST COMP TGR" ON period 2; "GATE 11 & 12" (TEST COMP, T4, SSQ FST) ON period 2; F REG LATCH "SET" pulse, first half of 2 |
| 3 | "SIGNAL SSQ TO VFL TGR" (T4 SSQ FST) ON period 3, annotated "(TURN CONTROL OVER TO SAU)"; under "(NOT INT)" two arrows: "LATCH ACOB" (T4 SSQ FST) ON period 3, its fall marked by an arrow labelled "(SIGNAL SSQ TO VFL TGR)"; and (T4 SSQ FST) half-period pulse, first half of 3, labelled "GATE ACOB 12-59 TO C 12-59"; "GATE 21 (TGR)" (T4 SSQ FST) rises at 3 (break mark, continues; falls on sheet 2). FIRST CYCLE TGR, GATE 31, GATE 61, DECODE ... fall at 3 |

Left panel length: **3 FP CLOCK periods (0,1,2) + hand-over period 3** (COUNTED).

#### Right panel: "SQUARE ROOT DEVELOPMENT UNDER SAU CONTROL" (printed heading)
Clock axis: **"A PULSES"** (not FP CLOCK), drawn as an unnumbered train of **15 pulses** (COUNTED by edge measurement: rises at x = 1596, 1683, 1767, ... 2791, spacing ~85 px). The A PULSES row itself has no break mark, although the rows below do. I index them A0..A14 (DERIVED numbering; nothing printed).

| A period | ON / rising (condition as printed) |
|---|---|
| A0 | "SU SSQ" (SIGNAL SSQ TO VFL) ON for A0, falls at A1 "(TGR)" |
| A1 | "SSQ TGR" (SU SSQ) rises; "PAU DO SSQ TGR" (SU SSQ) rises; "GATES 61, 21, 22 & 25, BLOCK ADDER POS. 50 & 51, & ONE TO ADDER POS. 50,98,99" (PAU DO SSQ) rises; "SET RFL TO 47" -> "RFL" rises; "SET SCR TO 96" -> "SHIFT COUNTER REGISTER" rises; ROUTE C TO F pulse #1 "(12-13)"; F REG LATCH pulse #1 in second half of A1, C BITS "(12-13)", "(DEV ROOT BIT)" arrow, no bit number |
| A2 | ROUTE C TO F "(14-15)"; F REG LATCH (2nd half) C BITS "(14-15)", DEV ROOT BIT "1" |
| A3 | ROUTE C TO F "(16-17)"; F REG LATCH "(16-17)", "2" |
| {break} | break marks on ROUTE C TO F, F REG LATCH, SSQ TGR, PAU DO SSQ TGR, GATES 61..., RFL, SCR |
| A4 | ROUTE C TO F "(56-57)"; F REG LATCH "(56-57)", "21" |
| A5 | ROUTE C TO F "(58-59)"; F REG LATCH "(58-59)", "22" |
| A6 | ROUTE C TO F "(60-61)" (last); F REG LATCH "(60-61)", "23"; RFL reaches "0" and falls at ~A6 + 0.4 (x 2141-2151, with a small down-arrow) |
| A6.5-A7.5 | "EOC1" (RFL=0), x ~2145-2225; "(EOC1)" pulse annotated "(HANDLE EXPONENT FROM A REG & WRITE INTO C POS 0-11)", x ~2150-2225 |
| A7 | "EOC2" (EOC1), x ~2192-2276 (lags EOC1 by about half an A period); F REG LATCH "24" (overbarred) |
| A8..A11 | F REG LATCH "25", "26", "27", "28" (all overbarred); SSQ TGR falls at A9 (x 2364) |
| {break} | second break, F REG LATCH only |
| A12, A13 | F REG LATCH "47", "48" (overbarred). Bracket over 24..48 printed "(ZEROS TO F REG POS 100 & 101)" |
| A13.5 | SHIFT COUNTER REGISTER falls at x 2744 (value "0") |
| A14 | "B TIMED SCR=O" pulse x 2744-2790, annotated "(PAU RESUME CONTROL)"; PAU DO SSQ TGR and GATES 61, 21, 22 & 25 ... fall at A14 (x 2791) |

Printed counter values:
- "RFL = 47 - 45 - 43 - 3 - 1 - 0" (break between 43 and 3). "SET RFL TO 47".
- "SCR = 96 - 94 - 92   54  52  50  48  46  44  42  40  38 ... 0" (break after 92 and before 0). "SET SCR TO 96".
- Per-step conditional gates (dashed boxes, one per step): "(ADDER OUTPUT POS 50 = 0)  GATE ... 63 ... ETC." and "ADDER OUTPUT POS 50 = 1  GATE ... 72 ... ETC." (233z2.png).

#### NOTES printed (sheet 1)
- "NOTE THIS IS REPRESENTING CHANGING DATA (NEW C POSITIONS)" (arrow to ROUTE C TO F row).
- "(ZEROS TO F REG POS 100 & 101)" over F REG LATCH pulses 24-48.
- "(TURN CONTROL OVER TO SAU)"; "(PAU RESUME CONTROL)"; "(HANDLE EXPONENT FROM A REG & WRITE INTO C POS 0-11)".

#### Loop terminations (sheet 1)
- ROUTE C TO F / RFL loop: RFL set to 47, steps by 2 per routing (47-45-43 ... 3-1-0); terminates on "(RFL=O)" -> EOC1 -> EOC2. DERIVED: 47,45,...,1 is 24 values, plus 0 = 25 states = 25 C-bit pairs (12-13)..(60-61); consistent.
- Root-development / SCR loop: SCR set to 96, printed decrementing by 2 per step (96-94-92 ... 38 ... 0); terminates on "B TIMED SCR=O" -> "(PAU RESUME CONTROL)". DERIVED: 96/2 = 48 steps, matching F REG LATCH root bits 1..48 (last printed "48").
- Neither loop count is data-dependent as printed (fixed presets 47 and 96). The per-step choice is data-dependent: GATE 63 vs GATE 72 on "ADDER OUTPUT POS 50 = 0 / = 1" (DERIVED: root-bit decision from the adder sign position).
- DERIVED oddity: by pair index, (56-57) would correspond to root bit 22, but the chart prints "21" under (56-57) and "23" under (60-61), then overbarred "24". Labels transcribed as printed; the break hides the intermediate pairs.

#### Panels A PULSES vs FP CLOCK
Left panel (PAU) timed by FP CLOCK 0-3 (drawn period ~170 px); right panel (SAU) timed by A PULSES, 15 drawn, drawn period ~85 px. The axes are separate drawings, not aligned and with no printed ratio between FP CLOCK and A PULSES (DERIVED: do not read the 2:1 drawn-width ratio as a timing ratio).

#### Path length, sheet 1
- PAU part: 3 FP CLOCK periods (0-2) + period 3 hand-over (COUNTED).
- SAU part as drawn: 15 A PULSES (COUNTED) with two breaks. DERIVED from printed labels (no count printed): 1 SU SSQ period (A0) + F REG LATCH pulses = 1 unnumbered (C bits 12-13, A1) + 48 numbered root bits 1..48 = 49 A periods after SU SSQ, i.e. 50 A periods in all; this matches SCR 96 stepping by 2 to 0 (48 steps) only if SCR starts stepping at the first numbered bit, which the drawing does not settle (SCR is set at A1).
- Hand-back: "B TIMED SCR=O" -> "(PAU RESUME CONTROL)" -> sheet 2 "TX (PAU RESUME SSQ)".

---

#### FIGURE 3.8.10. FLOATING-POINT STORE ROOT (TIMING) (SHEET 2 OF 2)

- Title as printed: "FIGURE 3.8.10. FLOATING-POINT STORE ROOT (TIMING) (SHEET 2 OF 2)"
- PDF page 234 (portrait). Running head "PAU TIMING CHARTS" left, "M3-04-3" right.
- Printed page number at foot: **8-10**. Issue date: **2/1/62**. (234foot.png)
- Printed panel heading: "NORMALIZATION AND TERMINATION UNDER PAU CONTROL".
- Tiles: 234a.png, 234b.png, 234c.png, 234d.png; edge positions measured on the page image.

Clock axis: FP CLOCK, **unnumbered**, 5 periods drawn (rises at x 346, 568, 793, 1017, 1241; last fall 1353; period ~224 px). Called P0..P4 here (DERIVED numbering). No A PULSES on this sheet. No break marks on this sheet.

| period | ON / rising (condition as printed) |
|---|---|
| P0 | "TX" (PAU RESUME SSQ) (printed "Tx"); EXPONENT ROUTING TGR (TP6), WRITE EXPONENT C TGR, GATE 21 enter from the left with arrowheads (continued from sheet 1) |
| P1 | "T4" (TX); "NORMALIZE EXPONENT TGR" (TX) rises, ON P1-P3; "GATES 11 & 12" (NE, NOT NM, SSQ) rises (ON to about mid-P4); "SUPPRESS ADDER OUTPUT (59) (51)" (NE, NOT NM, SSQ) ON P1-P2; "GATE 61" (SSQ, NE NOT NM) rises; "GATE C EXP TO SAU (FOR NORMALIZING)" (NE, TP6) rises, ON P1-P3, with pointer "NORMALIZE AMOUNT A INPUT" |
| P2 | "T3" (T4, SSQ OPER, NE, NOT NM) |
| P3 | "T4" (T3); "TC" (T3 & NE); WRITE EXPONENT C TGR falls; "WRITE EXPONENT D TGR" (END OP, TO MEM) rises (no fall drawn); "NORM MANTISSA" (T3, NE) ON P3, falls "(TGR)"; "END OP" (MANTISSA RESULT TRUE, T3, NE, SH<=6) ON P3, falls "(TGR)"; F REG LATCH (T3, NE) pulse, first half of P3; "61 & 63 (TGR)" segment of the GATE 61 line from P3, arrow from "(T3, SSQ)"; "11 & 12" segment of the GATES 11 & 12 line from mid-P3, arrow from "(END OP, NOT INT)"; "ACIB BUS LATCH LEVEL 1" rises (no fall) |
| P4 | "GATE 21" falls "(TGR)"; NORMALIZE EXPONENT TGR, GATE C EXP TO SAU, 61 & 63 (TGR) fall; "EXP LATCH" (TC, END OP, NOT INT) ON P4; "EXP SAMPLE" (TC, END OP, NOT INT) ON P4; "LATCH DATA ACOB" (TC, END OP NOT INT) rises (no fall); "ACIB BUS LATCH LEVEL 2" rises (no fall); GATES 11 & 12 falls about mid-P4 |

Branch conditions (sheet 2): T3 entered on "(T4, SSQ OPER, NE, NOT NM)"; TC on "(T3 & NE)"; END OP on "(MANTISSA RESULT TRUE, T3, NE, SH<=6)" (printed "SH≤6"); "NOT INT" qualifies the end latches; "NE, NOT NM" qualifies GATES 11 & 12, SUPPRESS ADDER OUTPUT, GATE 61; "(NE, TP6)" gates the C exponent to the SAU. Only one normalize pass (T3 at P2, T4/TC at P3) is drawn, with no loop break (COUNTED).

Register transfers named (sheet 2): C exponent to SAU (GATE C EXP TO SAU), F REG latch, adder output positions 59 and 51 suppressed, exponent written to C then D, ACOB (LATCH DATA ACOB), ACIB BUS LATCH LEVEL 1 and 2.

Path length sheet 2: **5 FP CLOCK periods (P0 TX .. P4 EXP LATCH)** (COUNTED, unnumbered).

Total Store Root as drawn (DERIVED): 3 PAU periods (+ hand-over) + SAU development (15 A pulses drawn; 48 SCR steps implied by printed 96 by 2) + 5 PAU periods.

ILLEGIBLE (3.8.10): none. Uncertain reading: "DECODE FOR SHIFT OF ZERO OR R1": the last glyph pair is "R" with a small "I"/"1" (tile 233L1.png).

---

#### FIGURE 3.8.11. FLOATING-POINT MULTIPLY (TIMING)

- Title as printed: "FIGURE 3.8.11. FLOATING-POINT MULTIPLY (TIMING)"
- Single sheet. PDF page 235. Running head "M3-04-3" left, "PAU TIMING CHARTS" right.
- Printed page number at foot: **8-11** (right). Issue date: **2/1/62** (left). (235foot.png)
- Printed NOTE (top right): "SEQUENCE SHOWS NORMALIZATION SHIFT OF 6 OR LESS."
- Tiles: 235a.png, 235b.png (top), 235c.png, 235d.png (middle), 235e.png, 235f.png (bottom), zooms 235z1.png (MR ring rows), 235z2.png (1X MULTIPLICAND / RESET S&T), 235z3.png (GATE A EXP row). Edge x-positions measured with tB/tools/edges.py (copy of [scratch, deleted]/tools/edges.py) and runs.py on the page image.

#### Clock axis
FP CLOCK with rising edges numbered **0 1 2 3 4 5 6 7 8 9 10** (PRINTED, first 0, last 10). Full-res rises at x = 395, 566, 738, 910, 1085, 1258, 1430, 1602, 1774, 1946, 2120; last fall 2206; period ~172 px. Dashed vertical reference lines are drawn at clock **3** and clock **8**. No break marks anywhere on this chart. No A PULSES row.

#### Ring triggers
| period | trigger (condition as printed) |
|---|---|
| 0 | "T0" (START CTRL) |
| 1 | "T1" (T0, MPY) |
| 2 | "MR1" (T1, MPY) |
| 3-4 | second MR row, rises at 3 on "(MR1, MR2-bar)" (printed "(MR1, MR̄2)"), ON 3-4, falls at 5; label printed "MR1, 2" or "MR, 2" with a small arrow from "(MR2.MR1)" (exact label: see ILLEGIBLE) |
| 4 | "MR1" again, on "(MR2, MR1-bar)" (printed "(MR2, M̄R̄1)"), ON 4, falls at 5 |
| 5 | "MC" (MR1,MR2) |
| 6 | "T4" (MC, MPY) |
| 7 | "T3" (T4, MPY) |
| 8 | "T4" (T3); "TC" (T3) |

#### Cycle table (COUNTED from measured edges)
| period | ON / rising (condition as printed) |
|---|---|
| 0 | T0; "SAMPLE TO C & EXECUTION REGS" (START CTRL), first half of 0; "1ST CYC TGR" (START CTRL), ON 0; "GATE 1" (MPY,FCT), ON 0, annotated "GATE A REG FRACTION TO F REG"; the "(MPY,FCT)" line labelled "(RIGHT 12 TGR)" ... "GATE 36" rises at 0, ON 0-5, annotated at its fall "ALLOW DEVELOPMENT OF 1 & 3 X MULTIPLE" |
| 1 | T1; "MULTIPLY STATUS TGR" (MPY, FST) rises, ON 1-7, falls at 8; "SHIFT RIGHT 12 TGR" ... "(GATE 47)" (MPY, FST) rises, ON 1-5, annotated at its fall "ALLOW FOR F REG SHIFT OF 12 POS 1-37 & 62-85"; "WRITE EXPONENT A TGR" (MPY, FST, T0) rises (runs to ~x 1970, i.e. into period 9, ending in a curl; no fall drawn); "1X MULTIPLICAND TGR" (MPY, FST) ON 1-2, annotated "ALLOW FOR OPENING OF 1X MCD COMP FROM MULTIPLICAND SET UNIT IF LOW ORDER BIT = 1"; "RESET S & T REG" (T1, MPY) rises at 1, falls at ~2.5 (x 570-827); "GATE EXPONENTS TO SAU ADDER" (MPY STATUS TGR, RIGHT 12 TGR) ON 1-5 |
| 2 | MR1; F REG LATCH & SAMPLE pulse (first half of 2); G REG LATCH & SAMPLE pulse (first half of 2); S & T REG LATCH & SAMPLE DELAYED pulse at ~2.4-2.9 (x 808-893); CSA LOOP "I" arrow starts ~2.4 (x 804) |
| 3 | MR row 2; "GATE S REG 49-61 TO F REG 1-12" / "GATE T REG 49-61 TO F REG 62-73" (RIGHT 12 TGR NOT 1X MCD TGR) rises, ON 3-5; F REG and G REG latch pulses (first half of 3); S & T delayed pulse ~3.4-3.9 (x 978-1065); CSA LOOP "II" starts at 3.0 (x 908); loop I ends ~3.4 (x 980) |
| 4 | MR1 (again) + MR row 2; F, G latch pulses (first half); S & T delayed pulse ~4.4-4.9 (x 1150-1238); CSA LOOP "III" starts at 4.0 (x 1080); loop II ends ~4.4 (x 1152) |
| 5 | MC; "SAMPLE TEST COMP" ON 5; F, G latch pulses (first half); S & T delayed pulse ~5.4-5.9 (x 1325-1408); CSA LOOP "IV" starts ~4.9 (x 1235); loop III ends ~5.4 (x 1324); G REG latch pulses end after period 5 (4 G pulses: 2,3,4,5) |
| 6 | T4 (MC, MPY); "GATE 41, 42, 46" (MC, MPY NOT INT) ON 6-7, falls "(TGR)"; "GATE 22 TGR" (MC, MPY NOT INT) ON 6-8, annotated "F REG 50-97 TO MAIN ADDER 50-97"; "NORMALIZE EXPONENT TGR" (MC.MPY, NOT INT) ON 6-8; "GATE A EXP TO. SAU ADDER" (NE, NOT TR6) ON 6-8, annotated "(FOR NORMALIZATION)"; "EXP LATCH & SAMPLE" (MC, MPY, NOT INT) ON 6; F REG latch pulse (first half of 6, the 5th and last of the run); S & T delayed pulse ~6.4-6.9 (x 1495-1581), annotated "(DELAYED TO ALLOW CSA LOOP TIME TO COMPLETE)"; CSA LOOP IV ends ~6.4 (x 1496); "MAIN ADDER LOOP" arrow starts at 6.0 (x 1423) |
| 7 | T3 (T4, MPY); "GATE 61 & 63" (T4, MPY STATUS TGR) rises, ON 7-8, falls "(TGR)" |
| 8 | T4 (T3), TC (T3); "GATE 21" (T3, NE, RESULT TRUE) ON 8 "(TGR)"; "END OP" (T3, NE, SHIFT <= 6) ON 8 "(TGR)" (printed "SHIFT ≤ 6"); "NORM MANT" (T3, NE) ON 8 "(TGR)"; F REG LATCH (T3, NE) pulse, first half of 8; MAIN ADDER LOOP arrow ends at the dashed line at 8 (x 1774); "GATE 11 & 12" (TEST COMP END OP) ON ~8.5-9.5 (x 1855-2030); MULTIPLY STATUS TGR falls at 8 |
| 9 | "LATCH DATA ACOB" (TC, TEST COMP, END OP, NOT INT) rises at 9 (no fall drawn); "(TC TO ACC)" pulse first half of 9, labelled "(SAMPLE TO A REG)"; "EXP LATCH & SAMPLE" (END OP, NOT INT) ON 9; GATE 22 TGR, NORMALIZE EXPONENT TGR, GATE A EXP TO SAU ADDER, GATE 61 & 63 fall at 9 |
| 10 | second "(SAMPLE TO A REG)" pulse, first half of 10, with arrowed note "SECOND SAMPLE ORDER CHECKER CONTROL IF THIS IS DOUBLE OPER." |

#### Printed annotations / NOTES (verbatim)
- "SEQUENCE SHOWS NORMALIZATION SHIFT OF 6 OR LESS."
- "GATE A REG FRACTION TO F REG"
- "ALLOW FOR F REG SHIFT OF 12 POS 1-37 & 62-85"
- "ALLOW FOR OPENING OF 1X MCD COMP FROM MULTIPLICAND SET UNIT IF LOW ORDER BIT = 1"
- "ALLOW DEVELOPMENT OF 1 & 3 X MULTIPLE"
- "GATE S AND T REGS (POS 2-61) TO MAIN ADDER (POS 2-61) AND F REG (POS 1-36) TO ADDER (POS 62-97)" (small type, right of the dashed line at 8, at the level of SAMPLE TEST COMP / GATE 41,42,46; no arrow)
- "F REG 50-97 TO MAIN ADDER 50-97"
- "(FOR NORMALIZATION)"
- "(DELAYED TO ALLOW CSA LOOP TIME TO COMPLETE)"
- "(SAMPLE TO A REG)"; "SECOND SAMPLE ORDER CHECKER CONTROL IF THIS IS DOUBLE OPER."

#### CSA loops and main adder loop (bottom of chart, rows "CSA LOOPS")
PRINTED: four CSA loops labelled **I, II, III, IV**, then **"MAIN ADDER LOOP"**. Measured arrow extents (full-res x, then in clock units):
- I: 804-980 = 2.37 -> 3.39
- II: 908-1152 = 2.98 -> 4.39
- III: 1080-1324 = 3.97 -> 5.39
- IV: 1235-1496 = 4.87 -> 6.38
- MAIN ADDER LOOP: 1423-1774 = 5.96 -> 8.00 (ends on the dashed line at 8)
COUNTED: each CSA loop arrow spans ~1.0-1.5 periods; a new loop starts about every period, so successive loops overlap (pipelined). Main adder loop = 2 FP CLOCK periods (6, 7).
DERIVED (measured coincidence): the right ends of loops I-IV (x 980, 1152, 1324, 1496) coincide with the rising edges of S & T delayed latch pulses 2-5 (x 978, 1150, 1325, 1495), and loop I starts at the rise of S & T pulse 1 (x 804 vs 808). Each CSA loop therefore runs from one S&T latch to the next (or from the F/G latch at k to the S&T latch at k+1.4). The 5th S&T pulse (6.4) closes loop IV; the main adder loop starts at 6.
- Bits per pass: NOT PRINTED as such. DERIVED from printed labels: 12 bits per pass ("SHIFT RIGHT 12 TGR", "SHIFT OF 12", "GATE S REG 49-61 TO F REG 1-12", "GATE T REG 49-61 TO F REG 62-73"), 4 passes x 12 = 48 multiplier bits; multiples 1x and 3x ("ALLOW DEVELOPMENT OF 1 & 3 X MULTIPLE").
- Loop count data-dependent? The CSA loop count is drawn as a fixed 4 with no break marks (COUNTED). The data-dependent parts are: "1X MULTIPLICAND TGR" / "IF LOW ORDER BIT = 1"; the normalization exit "END OP (T3, NE, SHIFT ≤ 6)" with the note that the sequence shows a shift of 6 or less (DERIVED: a longer shift would take more T3/T4 periods, not drawn); "RESULT TRUE" on GATE 21; "DOUBLE OPER" adding a second A-REG sample.

#### Branch conditions
NE / NOT TR6 (printed "TR6" here, not "TP6": 235z3.png); SHIFT ≤ 6; RESULT TRUE; NOT INT; TEST COMP; MR1/MR2 ring alternation ("(MR1, MR̄2)", "(MR2, M̄R̄1)", "(MR2.MR1)", "(MR1,MR2)"); "NOT 1X MCD TGR"; "NOT T4 MPY STATUS TGR" (F REG latch), "SHIFT RIGHT 12 TGR NOT MC" (G REG latch), "NOT T3, NOT T4, MPY STATUS 1" (S & T latch); DOUBLE OPER.

#### Register transfers named
A REG fraction -> F REG (period 0); C & execution regs (0); 1X MCD complement from MULTIPLICAND SET UNIT; S REG and T REG (reset at 1; latched 2.4..6.9, "DELAYED"); S REG 49-61 -> F REG 1-12 and T REG 49-61 -> F REG 62-73 (3-5); F REG latch/sample (2,3,4,5,6, and 8); G REG latch/sample (2,3,4,5); exponents -> SAU ADDER (1-5); A exponent -> SAU ADDER for normalization (6-8); F REG 50-97 -> MAIN ADDER 50-97 (6-8); S and T regs (2-61) -> main adder (2-61), F reg (1-36) -> adder (62-97); ACOB (LATCH DATA ACOB, 9); TC TO ACC sample to A REG (9, and 10 if double).

#### Path length
- **11 FP CLOCK periods, 0..10** (COUNTED; printed numbers 0-10) for normalization shift of 6 or less, double-precision sample in 10; END OP in 8; LATCH DATA ACOB at 9. If single operation, the last activity is in 9 (DERIVED).
- No total printed.

#### ILLEGIBLE / uncertain
- Second MR ring row label: printed as "MR" + subscript "1" + a comma/tick + "2" (235z1.png). Could be "MR1,2" or "MR2" with a stray mark. DERIVED: it is the MR2 trigger; its enabling condition "(MR1, MR̄2)" matches, and 3.8.13 draws the identical row (rises at 3, ON 3-4) labelled plainly "MR2".
- "TR6" vs "TP6" in "(NE, NOT TR6)": the ink reads "TR6" (235z3.png); every other chart in this set prints "TP6"/"TP-6" (DERIVED: probably TP6).
- "(GATE 47)": the "4" is broken in the ink, the "7" is clear (235z5.png). "GATE 36", "GATE 41, 42, 46", "GATE S REG 49-61 TO F REG 1-12", "GATE T REG 49-61 TO F REG 62-73", "SHIFT OF 12 POS 1-37 & 62-85" all confirmed at 200% (235z4.png, 235z6.png, 235z7.png, 235z8.png). Note 49-61 is 13 positions feeding 12-position fields 1-12 / 62-73 (as printed; not resolved).
---

#### FIGURE 3.8.12. FLOATING-POINT LOAD MULTIPLER REGISTER (TIMING)

- Title as printed (note the printed misspelling "MULTIPLER"): "FIGURE 3.8.12. FLOATING-POINT LOAD MULTIPLER REGISTER (TIMING)" (236title.png)
- Single sheet. PDF page 236. Running head "PAU TIMING CHARTS" left, "M3-04-3" right.
- Printed page number at foot: **8-12** (left). Issue date: **2/1/62** (right). (236foot.png)
- Chart caption top right: "FLOATING POINT LOAD MULTIPLIER REG.  LMR".
- Printed NOTE (bottom left): "NOTE: THIS EXAMPLE SHOWS TWO NORMALIZATION SEQUENCES" (236g.png).
- Drawing style differs from 3.8.9-3.8.11 (typeset lettering, circled clock numbers, dashed verticals at each clock rise; some signals drawn with slow ramps).
- Tiles (upscaled 140%): 236a.png, 236b.png (top), 236c.png, 236d.png (middle), 236e.png, 236f.png (bottom), 236g.png (loop arrows and NOTE). Position conversion: full-res x = tile x / 1.4 + 430 (a,c,e) or + 1150 (b,d,f).

#### Clock axis
Unlabelled clock waveform (top row) with circled numbers **0 1 2 3 4 5** (PRINTED) at the rising edges; full-res rises at x = 670, 861, 1049, 1239, 1427, 1617; period ~190 px; the waveform ends shortly after 5. Dashed verticals at 1, 2, 3, 4, at the fall of 4 (x ~1526, i.e. 4.5), and at 5. No A PULSES, no break marks.
Labels on the clock row: "SHIFT>6" between 1 and 2 (under the clock low of period 1); "SHIFT≤6" just after 4 (under period 4) (PRINTED).

#### Ring triggers
| period | trigger (condition as printed) |
|---|---|
| 0 | "TO" (START CRTL) [printed "CRTL" on this row] |
| 1 | "T3" (TO, LMR) |
| 2 | "T4" (T3); "TC" (T3, NE) |
| 3 | "T3" (T4, NOT END OP, NOT INT) |
| 4 | "T4" (T3); "TC" (T3, NE) |
| 5 | ring falls at 5 (no trigger after) |

#### Cycle table (COUNTED)
| period | ON / rising (condition as printed) |
|---|---|
| before 0 - 1 | "LA ENABLE": drawn as a slow ramp from a dashed line before 0 rising before 0, high through period 0, ramping down just before 1 |
| 0 | TO; "SAMPLE OP CODE TO EXEC REG AND TOB TO C REG" (START CTRL), first half of 0; "FIRST CYCLE TGR (FCT)" (START CTRL), ON 0-1, falls at 2; "GATE 33 - C 12-59 TO ADDER 2-49" (FCT, LMR), ramped rise at 0, ramped fall just after 2; "TP-6- EXPONENT ROUTING CONTROL" (FCT, LMR), ramped rise at 0, runs past 5 (no fall) |
| 1 | T3 (TO, LMR); "GATE 61 AND 63 - ADDER 0-99 to F 0-89" (TO, LMR) rises, ON 1-4; "NORM EXPONENT TGR (NE)" (TO, LMR) ON 1-4; "WRITE EXP C" (TO, TO MEM) ON 1-3, falls at 4; F REG LATCH & SAMPLE (TO) pulse, first half of 1; "SHIFT>6" (printed on clock row); EXPONENT LOOP 1 starts at 1 |
| 2 | T4 (T3), TC (T3, NE); "NORM MANTISSA TGR (NM)" (T3, NE) ON 2-4; "GATE 21 AND 22 - SHIFTER 0-99 TO ADDER 0-99" (T3, NE) ON 2-4; F REG LATCH & SAMPLE (T3, NE) pulse, first half of 2; "STC" ON 2, falls at 3; ADDER LOOP 1 (0->2) ends, ADDER LOOP 2 starts |
| 3 | T3 (T4, NOT END OP, NOT INT); "EXPONENT LATCH" (TC, NM) ON 3, falls at 4; "EXPONENT SAMPLE" (TC, NM) ON from 3 to ~3.8 (x 1250-1398); EXPONENT LOOP 1 (1->3) ends, EXPONENT LOOP 2 starts |
| 4 | T4 (T3), TC (T3, NE); "SHIFT≤6"; "END OP" (T3, NE SHIFT ≤ 6) ON 4, falls at 5; "WRITE EXP "B"" (T3, NE, SHIFT≤6) rises at 4 (runs to ~5.5, no fall drawn); F REG LATCH & SAMPLE (T3, NE) pulse, first half of 4; "GATES 11 and 12 - SHIFTER TO AC1B" (END OP, TEST COMP) ON 4.5-5.5; WRITE EXP C falls; ADDER LOOP 2 ends at 4 (x 1439) |
| 5 | "LATCH ACOB" (TC, END OP, NOT INT) rises (no fall); "EXPONENT LATCH" (TC, END OP, NOT INT) ON 5 (to ~6, x 1627-1819); "EXPONENT SAMPLE" (TC, END OP, NOT INT) ON 5 (to ~5.8, x 1627-1779); "SAMPLE ACIB TO D REG" pulse first half of 5; "A REG SAMPLE" (TO ACC,TO,END OP, NOT INT) pulse first half of 5; GATE 61 AND 63, NORM EXPONENT TGR, NORM MANTISSA TGR, GATE 21 AND 22, END OP, ring fall at 5; EXPONENT LOOP 2 ends ~5.5 (x 1723) |

#### Loops (PRINTED arrows, bottom; measured with tB/tools/runs.py)
- "ADDER LOOP 1": 0 -> 2 (x 675-1060). "ADDER LOOP 2": 2 -> 4 (x 1060-1439). Each = **2 FP clock periods** (COUNTED).
- "EXPONENT LOOP 1": 1 -> 3 (x 872-1250). "EXPONENT LOOP 2": 3 -> ~5.5 (x 1250-1723). (COUNTED)
- The exponent loop lags the adder loop by one period (DERIVED).

#### Branch conditions
- "SHIFT>6" -> loop again: T3 re-entered on "(T4, NOT END OP, NOT INT)" (period 3).
- "SHIFT≤6" -> "END OP" on "(T3, NE SHIFT ≤ 6)"; "WRITE EXP "B"" on "(T3, NE, SHIFT≤6)".
- "NE" gates TC, NORM MANTISSA TGR, GATE 21 AND 22, F REG latch; "NM" gates EXPONENT LATCH / SAMPLE in loop; "NOT INT", "TEST COMP", "TO MEM", "TO ACC" conditions as quoted. DERIVED: the number of normalization sequences is data-dependent (each pass handles up to 6 shifts; this example shows two).

#### Register transfers named
OP code -> EXEC REG, TOB -> C REG (0); C 12-59 -> ADDER 2-49 (GATE 33, 0-2); ADDER 0-99 -> F 0-89 (GATE 61 AND 63, 1-4); SHIFTER 0-99 -> ADDER 0-99 (GATE 21 AND 22, 2-4); F REG latch (1, 2, 4); exponent C written (1-3), exponent "B" written (from 4); SHIFTER -> AC1B (GATES 11 and 12, 4.5-5.5); ACOB latch (5); ACIB -> D REG (5); A REG sample (5).

#### Path length
- **6 FP clock periods, 0..5** (COUNTED; printed circled 0-5) for two normalization sequences; END OP in 4; final samples in first half of 5.
- DERIVED: one sequence would be 2 periods shorter (one adder loop = 2 periods); not printed.

#### ILLEGIBLE
None. Note "(START CRTL)" vs "(START CTRL)" spelling differs between rows as printed.
---

#### FIGURE 3.8.13. FLOATING-POINT MULTIPLY AND ADD (TIMING)

- Title as printed: "FIGURE 3.8.13. FLOATING-POINT MULTIPLY AND ADD (TIMING)" (two lines). Also a caption inside the chart, left of the lower section: "FLOATING POINT MULTIPLY AND ADD" over a double rule.
- Fold-out, single sheet. PDF page 237 (5100x3300). Left half of the fold-out is blank; the chart occupies x ~1950-4900. A vertical fold seam crosses the chart at x ~3819 (between clocks 9 and 10).
- Running head "M3-04-3" / "PAU TIMING CHARTS" (top right).
- Printed page number at foot: **8-13/8-14**. Issue date: **2/1/62**. (237foot.png)
- Tiles (native crops upscaled 150%; full-res x = tile x/1.5 + column offset, y = tile y/1.5 + row offset): 237_r200_c1950.png, 237_r200_c2700.png, 237_r200_c3450.png, 237_r200_c4150.png, 237_r850_c1950.png, 237_r850_c2700.png, 237_r850_c3450.png, 237_r850_c4150.png, 237_r1500_c1950.png, 237_r1500_c2700.png, 237_r1500_c3450.png, 237_r1500_c4150.png, 237_r2150_c1950.png, 237_r2150_c2700.png, 237_r2150_c3450.png, 237_r2150_c4150.png; zoom 237z5.png (TB/TC lower ring), 237z6.png; 237foot.png; 237left.png, 237lefthalf.png (blank left half). Latch-pulse edges measured with tB/tools/edges.py.

#### Clock axis
Unlabelled clock waveform with circled numbers **0 .. 15** (PRINTED, first 0, last 15) at the rising edges; full-res rises at x = 2150, 2320, 2488, 2660, 2832, 3004, 3173, 3345, 3517, 3685, 3856, 4028, 4198, 4369, 4542, 4710; period ~171 px; waveform ends ~4800. Dashed verticals at every clock rise (the one at 8 drawn heavier). No A PULSES, no break marks.

Two paths are drawn: SOLID lines = main path; DASHED lines plus the bracketed lower section = alternative path, per the printed note (bracket, centre left of lower section):
"IF ACCUMULATOR EXPONENT IS SMALLER USE THIS TIMING ALONG WITH DOTTED LINES ABOVE".

#### Ring triggers, main (solid) path
| period | trigger (condition as printed) |
|---|---|
| 0 | "TO" (START CTRL) |
| 1 | "T1" (TO MPYC, CM) |
| 2 | "MR1" (T1, MPY) |
| 3-4 | "MR2" (M̄R̄2̄, MR1) [printed with overbar over "MR2"], ON 3-4, falls at 5 |
| 4 | "MR1" again, on "(MR2, M̄R̄1̄)" |
| 5 | "MC" (MR1, MR2) |
| 6 | "T4" (ĪN̄T̄, MC) [overbar over INT] |
| 7 | "T3" (T4, MPY ST) |
| 8 | "T2" (CUM, PSA) / (T3, MPY ST) [two conditions stacked at the rise] |
| 9 | "T3" (T2, PSA, SH<4) [printed "SH<4"] |
| 10 | "TC" (T3, NE); "T4" (T3, NE) |
| 11 | ring falls at 11 |

#### Ring triggers, alternative path (lower bracketed section, solid ink, used with the dashed lines above)
| period | trigger (condition as printed) |
|---|---|
| 8 | "TB" (MPY ST, CMPSE) |
| 9 | "TC": two labels at its rise, "(T4, CM, EXP SUM MINUS)" with "(TB)" under it (237z5.png). AMBIGUITY: T4 is ON in period 6, not 8, so "(T4, CM, EXP SUM MINUS)" cannot be the condition of a rise at 9 in the same sense as "(TB)". It mirrors "(T4, CM, EXP SUM PLUS)" on PSA TGR (rises at 7), while "CMPSE TGR" rises at 7 with no condition printed. DERIVED, unconfirmed: "(T4, CM, EXP SUM MINUS)" is the set condition of CMPSE TGR and was lettered on the wrong row. |
| 10 | "MR3" (TC, CMPSE) |
| 11 | "T2" (MR3, CM) |
| 12 | "T3" (T2, PSA, SH<4) |
| 13 | "T4" (T3, NE); a second, unlabelled row (T3, NE) also ON 13 (DERIVED: TC) |
| 14 | ring falls at 14 |

#### Cycle table (COUNTED; S = solid main path, D = dashed alternative)
| period | ON / rising (condition as printed) |
|---|---|
| 0 | TO; "SAMPLE OF CODE TO EXEC REG AND TOB TO C REG" (START CTRL) first half of 0; "LA ENABLE" (ramp, high before 0, ramps down ~0.5); "FCT TGR" (START CTRL) ON 0; "SET BAAB TO 112 = TO•MPYC" (TO, MPYC) ramp rise ~0.2, ramp fall ~1.5; "LTH BAAB" (TO, MPYC) second half of 0; "GATE C REG TO F REG" / "GATE #3" (TO, MPYC) ON 0; "GATE 37 = D REG TO MULTIPLE GENERATION CKTS = TO•MPYC - MPY ST" ramp rise at 0, ramps down ~8.4-8.6 |
| 1 | T1; "GATE BEXP PLUS CEXP TO VFL ADDER" (1 XMCD, CM) rises, ramps down ~3.3; "WRITE EXP C TGR" (TO, MPYC) ON 1-3 (a dashed box is also drawn from 0 to 1 on this row, unlabelled); "RESET S AND T REGS" (T1, MPY ST) ON 1; "1X MCD TGR" (TO, MPYC) ON 1-2; "RIGHT 12 STATUS TGR" (TO, MPYC) ON 1-5; "MULTIPLY STATUS TGR" (TO, MPYC) ON 1-7; "CUMULATIVE MULTIPLY - CM TGR" (TO, MPYC) rises (S falls at 10; D continues to 13) |
| 2 | MR1; "F REG LTH AND SAMPLE" (T̄4̄, MPY ST) pulse first half of 2; "G REG LTH AND SAMPLE" first half of 2; "S REG AND T REG LTH AND SAMPLE" (SH RIGHT 12 ST, M̄C̄) pulse 2.2-2.7; "RESET BAAB TO 10" (MR1, M̄R̄2̄) second half of 2; arrow "NOT T4, MPY ST" spans 2 -> 8 over the F REG latch row |
| 3 | MR2; F, G latch (first half); S & T latch 3.2-3.7; "EXPONENT LATCH" (CM, MR1, M̄R̄2̄) ON 3; "EXPONENT SAMPLE" (CM, MR1, M̄R̄2̄) ON 3-~3.75; "GATE A EXP MINUS C EXP TO VFL ADDER" (CUM, FCT) ramp rise ~3.1-3.3 (S ramps down ~8.5; D to ~11.2); FCT TGR row: a second level rises at 3 on "(COM, M̄R̄2̄, MPY ST)" (no separate name printed) and falls at 8 (S) / ~11.3 ramp (D) |
| 4 | MR1 + MR2; F, G latch; S & T latch 4.2-4.7; "WRITE EXP A TGR" (MR2, M̄R̄1̄, CM) rises (S to ~11.5, then D to the right edge; no fall drawn) |
| 5 | MC; "STC = MR1 MR2 MPY" ON 5; F, G latch (G: last, 4 pulses 2-5); S & T latch 5.2-5.7 (last; 4 pulses) |
| 6 | T4 (ĪN̄T̄, MC); F REG latch (5th and last of the multiply run, 2-6); RIGHT 12 STATUS TGR falls at 6 |
| 7 | T3 (T4, MPY ST); "PSA TGR" (T4, CM, EXP SUM PLUS) rises (S falls at 10; D to 13); "CMPSE TGR" rises (falls at 10); "TP6 TGR" (FCT, CM, T3) ramp rise ~7.1 (ramps down ~14.1); annotation "GATE 31 - NOT MANT ROUTING, PSA / GATE 32 - CM, PSA, NE" printed between 5.5 and 8 |
| 8 | S: T2 (CUM, PSA)/(T3, MPY ST); "SAMPLE 1ST PRESHIFT TO SCR" (T3, CM, C̄M̄P̄S̄Ē) first half of 8; "GATE PRESHIFT AMT TO SHIFT COUNTER" (T2, PSA) ON 8; "NORM EXPONENT" (T3, CM, C̄M̄P̄S̄Ē) rises (S to 11, D to 14); "GATES 31 AND 32 (A REG AND B REG TO ADDER)" (... PSA) ramp rise (S ramps down ~10.3, D to 13); "GATES 21 AND 22 OR GATE 23 (SHIFTER TO ADDER TRUE OR COM)" (T3, CM) ramp rise (S ramps down ~10.4, D ~13.2); "GATES 71 AND 72 (SHIFTER TO F REG)" (T2, PSA) ramp rise, solid top ends ~9.3 (D: ramp rise at 11, ramp fall ~12.2); F REG latch first half of 8; "EXPONENT LATCH" ON 8; MULTIPLY STATUS TGR falls. D: TB (MPY ST, CMPSE) |
| 9 | S: T3 (T2, PSA, SH<4). D: TC (T4, CM, EXP SUM MINUS)/(TB); "(TB, CMPSE)" dashed pulse first half of 9 on the SAMPLE 1ST PRESHIFT row; "GATES 11 AND 12 (SHIFTER TO ACIB) = TB•CMPSE•TESTS CMPT" ~8.5-9.5; "SAMPLE LEVEL II TO C REG" (TB, CMPSE) 9-9.5; "SAMPLE A REG AND B REG TO F REG" (TB, CMPSE) 9-9.5; "BUS LTH II" (TB, CMPSE) 9.5-10.5; "BUS LTH I" (TB, CMPSE) 9.5-11.5; "PASS DATA IST LEVEL TO II ND LEVEL" (TC, CMPSE) 9.5-10.5 |
| 10 | S: TC (T3, NE), T4 (T3, NE); "NORM MANT" (T3, NE) ON 10; "END OPN" (T3, NE, SH≤6) ON 10; F REG latch (T3, NE) first half of 10; "GATES 11 AND 12 (SHIFTER TO ACIB)" (END OP, TESTS COMP) ~10.5-11.5; PSA TGR, CM TGR, CMPSE TGR fall. D: MR3 (TC, CMPSE); "SAMPLE BUS TO B REG" (TC, CMPSE) 10-10.5 |
| 11 | S: "EXPONENT LATCH" (MR3, MPYC - TC, NM) ON 11; "EXPONENT SAMPLE" (TC, NM) ON 11-11.75; "(END OP) BUS LATCH I AND II" rises ~11.5 (solid to ~12.9, no fall); NORM EXPONENT falls (S). D: T2 (MR3, CM); GATES 71 AND 72 (D) rise; GATE PRESHIFT AMT TO SHIFT COUNTER (D) ON 11 |
| 12 | D: T3 (T2, PSA, SH<4) |
| 13 | D: T4 (T3, NE), (T3, NE) row; NORM MANT (D, T3, NE) ON 13; END OPN (D, T3, NE, SH≤6) ON 13; F REG latch (D, T3, NE) first half of 13; GATES 11 AND 12 (D) ~13.5-14.5; PSA TGR (D), CM TGR (D), GATES 31 AND 32 (D) fall at 13 |
| 14 | D: EXPONENT LATCH / SAMPLE (TC, NM) ~14-14.75; BUS LATCH I AND II (D) rises ~14.5; NORM EXPONENT (D) falls; TP6 TGR ramps down ~14.1 |
| 15 | clock only (no signal activity drawn after ~14.75) |

#### Answers to the specific questions (3.8.13)
- CSA loops / passes: **no "CSA LOOPS" or "MAIN ADDER LOOP" rows on this chart** (unlike 3.8.11). The ring is the same as 3.8.11 (MR1 2, MR2 3-4, MR1 4, MC 5, T4 6, T3 7) and RIGHT 12 STATUS TGR is ON 1-5, F REG latch pulses 2-6 (5), G REG latch 2-5 (4) as on 3.8.11. BUT the S & T latch differs (COUNTED, measured):
  - 3.8.11: "S & T REG LATCH & SAMPLE DELAYED" (NOT T3, NOT T4, MPY STATUS 1): **5 pulses**, at k+0.4..k+0.9 for k = 2..6.
  - 3.8.13: "S REG AND T REG LTH AND SAMPLE" (SH RIGHT 12 ST, M̄C̄) [lead-in confirmed on the S&T row, 237_r1500_c1950.png]: **4 pulses**, at k+0.2..k+0.7 for k = 2..5 (x 2526-2611, 2695-2782, 2869-2957, 3040-3126).
  - On 3.8.11 the "SHIFT RIGHT 12 ... NOT MC" condition is on the G REG row instead.
  So the 3.8.13 multiply core is NOT drawn identically to 3.8.11. Bits per pass not printed (DERIVED from "RIGHT 12": 12).
- Where the add phase begins (DERIVED from the ink): at clock 7-8. "PSA TGR" (T4, CM, EXP SUM PLUS) and "CMPSE TGR" rise at 7; the ring leaves the multiply sequence at 8 with T2 "(CUM, PSA)" (main path) or TB "(MPY ST, CMPSE)" (alternative path); "GATES 31 AND 32 (A REG AND B REG TO ADDER)", "GATES 21 AND 22 OR GATE 23 (SHIFTER TO ADDER TRUE OR COM)", "SAMPLE 1ST PRESHIFT TO SCR", "GATE PRESHIFT AMT TO SHIFT COUNTER" start at 8.
- Branches: "EXP SUM PLUS" -> PSA path (solid); "EXP SUM MINUS" / CMPSE -> alternative ("IF ACCUMULATOR EXPONENT IS SMALLER ..."); "SH<4" gates T2 -> T3; "SH≤6" gates END OPN; "NE" gates TC/T4/NORM MANT; "NM" gates exponent latch/sample; "TRUE OR COM" choice on GATES 21 AND 22 OR GATE 23; "ĪN̄T̄" on T4 at 6; "TESTS COMP"/"TESTS CMPT".
- SAU: **not mentioned anywhere on 3.8.13** (all 16 grid tiles read, including 237_r2150_c1950.png, which holds only the left end of the bracket note and the double rule; the fold-out's left half is blank apart from binding marks, 237left.png and 237lefthalf.png). Exponent arithmetic is routed to the **"VFL ADDER"**: "GATE BEXP PLUS CEXP TO VFL ADDER" (1-~3.3) and "GATE A EXP MINUS C EXP TO VFL ADDER" (~3.1-8.5). No "VFL multiply" appears.
- Other registers named: BAAB ("SET BAAB TO 112", "LTH BAAB", "RESET BAAB TO 10"); D REG -> MULTIPLE GENERATION CKTS (GATE 37); C REG -> F REG (GATE #3); S, T, F, G REGs; SCR (preshift); SHIFT COUNTER; A REG, B REG -> ADDER; SHIFTER -> ADDER / F REG / ACIB; BUS LATCH I, II (LEVEL I/II), LEVEL II -> C REG, BUS -> B REG, A REG and B REG -> F REG; exponents B, C (write C), A (write A).

#### Path lengths
- Main (solid) path: ring 0..10, falls at 11; exponent latch 11, bus latch from ~11.5: **12 FP clock periods, 0..11** (COUNTED).
- Alternative path (accumulator exponent smaller): ring to 13, falls at 14; last activity ~14.75: **15 periods, 0..14** (COUNTED). The clock is drawn to 15.
- No total printed. Each path shows one normalize pass (END OPN on SH≤6); longer normalization is not drawn (DERIVED: data-dependent).

#### ILLEGIBLE / uncertain
- The second level on the FCT TGR row (rises at 3 on "(COM, M̄R̄2̄, MPY ST)") has no name printed (237_r200_c1950.png). "COM" (not "CM") as printed.
- The dashed box at 0-1 on the WRITE EXP C TGR row has no label (237_r850_c1950.png).
- GATES 71 AND 72 solid level: its top line ends at ~9.3 with no drawn falling edge (237_r850_c3450.png).
- "EXPONENT LATCH" second condition reads "(MR3, MPYC - TC, NM)"; the "-" is a short dash, possibly an OR mark (237_r1500_c3450.png).
---

#### FIGURE 3.8.14. FLOATING-POINT STORE MULTIPLIER REGISTER (TIMING)

- Title as printed: "FIGURE 3.8.14. FLOATING-POINT STORE MULTIPLIER REGISTER (TIMING)" (238title.png)
- Single sheet. PDF page 238 (5100x3300 fold-out format), but the chart and text occupy only the LEFT half; the right half is blank. Running head "M3-04-3" left, "PAU TIMING CHARTS" (centre of the sheet).
- Printed page number at foot: **8-15** (bottom, centre of sheet = right edge of the used half). Issue date: **2/1/62** (left). (238foot.png)
- Printed NOTE (top right of chart): "EXAMPLE SHOWS 2 NORMALIZATION CYCLES".
- Tiles (native crops upscaled 160%; full-res x = tile x/1.6 + offset): 238_r520_c330.png, 238_r520_c1050.png, 238_r1100_c330.png, 238_r1100_c1050.png, 238_r1700_c330.png, 238_r1700_c1050.png, 238_bottom.png.

#### Clock axis
"FP CLOCK" with circled numbers **0 1 2 3 4 5 6** (PRINTED); full-res rises at x ~560, 730, 900, 1072, 1242, 1414, 1586; period ~170 px; waveform ends ~1703. Dashed verticals at 0-5. No A PULSES, no breaks.

#### Ring triggers
| period | trigger (condition as printed) |
|---|---|
| 0 | "TO" (START CTRL) |
| 1 | "T3" (TO,STM) |
| 2 | "T 4" (T3) [condition glyph nearly illegible, reads "(i3)"]; "TC" (T3, NE) |
| 3 | "T3" (T4, NOT END OP, NOT INT) |
| 4 | "T4" (T3); "TC" (T3, NE) |
| 5 | ring falls at 5 |

#### Cycle table (COUNTED)
| period | ON / rising (condition as printed) |
|---|---|
| before 0 | "LA ENABLE" high from ~-0.25 to ~0.75; a dashed box on the TP6 row labelled "(STM, FCT)" from before 0 to ~0.25 |
| 0 | TO; "(SAMPLE OP CODE TO EXEC REG AND TOB TO C REG)" (START CTRL) first half of 0; "FIRST CYCLE TGR" (START CTRL) ON 0-1, falls at 2 "(FCT)"; "GATE 34, D12-59 TO ADDER 2-49" (STM, FCT) ON 0 to ~2.5; "SET BAAB TO 112" (TO, STM) ON 0 to ~1.25; "L TH BAAB" (TO,STM) second half of 0 |
| 1 | T3 (TO,STM); "NORM EXPONENT TGR (NE)" (TO, STM) ON 1-4; "GATE 61 AND 63- ADDER 0-99 TO F O-99" (TO, STM) ON 1-4; "WRITE EXP INTO C REG" (TO, TO MEM) ON 1-3; "F REG LATCH & SAMPLE" (TO) first half of 1; EXP LOOP 1 starts |
| 2 | T4 (T3), TC (T3, NE); "GATE 21 AND 22 - SHIFTER TO ADDER" (T3, NE) rises (ON to ~4.85); "NORM MANTISSA TGR (NM)" (T3,NE) rises (ON to ~4.85); "STC" (T3, STM, FCT) ON 2; F REG LATCH & SAMPLE (T3, NE) first half of 2; (T4, STM) pulse second half of 2 labelled "RESET BAAB TO 10"; ADDER LOOP 1 (0->2) ends, ADDER LOOP 2 starts |
| 3 | T3 (T4, NOT END OP, NOT INT); "TP6 EXP ROUTING CTRL" (TO MEM, NM, EXP SAMPLE) rises (runs to end, no fall); "EXP LATCH" (TC, NM) ON 3; "EXP SAMPLE" (TC, NM) ON 3 to ~3.75; EXP LOOP 1 (1->3) ends, EXP LOOP 2 starts |
| 4 | T4 (T3), TC (T3, NE); "END OP" (T3, NE, SHIFT ≤ 6) ON 4; "WRITE EXP INTO D REG" (END OP, TO MEM) rises (to ~6, no fall); F REG LATCH & SAMPLE (T3, NE) first half of 4, with note "F REG LATCH & SAMPLE } ALSO USED FOR SHIFT REG"; "GATE 11 & 12" (END OP, TEST COMP) ON 4.5-5.5 "SHIFTER TO ACOB"; WRITE EXP INTO C REG falls; ADDER LOOP 2 (2->4) ends |
| 5 | "LATCH ACOB" (TC,END OP,NOT INT) rises (no fall); "EXP LATCH" (TC, END OP, NOT INT) ON 5 to ~6, note "ALSO USED AS INDICATOR LATCH"; "EXP SAMPLE" (TC, END OP, NOT INT) ON 5 to ~5.75; NORM EXPONENT TGR, GATE 61 AND 63 fall at 5; EXP LOOP 2 (3->5) ends |
| 6 | clock only; WRITE EXP INTO D REG and LATCH ACOB lines run to ~6 |

#### Loops (PRINTED arrows)
"ADDER LOOP 1" 0->2, "ADDER LOOP 2" 2->4, "EXP LOOP 1" 1->3, "EXP LOOP 2" 3->5. Each loop = **2 FP clock periods** (COUNTED); exponent loop lags adder loop by one period. Same structure as 3.8.12.

#### Branch conditions
"(T4, NOT END OP, NOT INT)" -> another normalization cycle (T3 at 3); exit "END OP" on "(T3, NE, SHIFT ≤ 6)"; "NE" on TC / GATE 21 AND 22 / NORM MANTISSA / F REG latch; "NM" on EXP LATCH / SAMPLE in loop and TP6; "TO MEM" on write-exponent paths; "NOT INT"; "TEST COMP". DERIVED: normalization cycle count is data-dependent (example shows 2).

#### Register transfers named
OP CODE -> EXEC REG, TOB -> C REG (0); D12-59 -> ADDER 2-49 (GATE 34, 0-2.5); BAAB set to 112 (0), latched (0.5), reset to 10 (2.5); ADDER 0-99 -> F 0-99 (GATE 61 AND 63, 1-4); exponent into C REG (1-3); SHIFTER -> ADDER (GATE 21 AND 22, 2-4.85); F REG (also SHIFT REG) latch (1, 2, 4); exponent into D REG (4-); SHIFTER -> ACOB (GATE 11 & 12, 4.5-5.5); LATCH ACOB (5).

#### Path length
**6 FP clock periods, 0..5** with 2 normalization cycles (COUNTED); clock drawn to 6. No total printed.

#### ILLEGIBLE
- Condition on the first T4 rise (period 2): printed glyph reads "(i3)", almost certainly "(T3)" by analogy with the second rise "(T3)" (DERIVED) (238_r1100_c330.png, bottom).
- Note: this chart prints "F O-99" (letter O) for "F 0-99" in GATE 61 AND 63.
---

#### CROSS-FIGURE SUMMARY (set B)

Path-length convention used throughout: from the first numbered clock (T0 = 0) THROUGH the latch period after END OP (the period in which ACOB / EXP LATCH / A REG sample occur), counted inclusively.

| Figure | PDF | Page foot | Date | Clock | Drawn length (COUNTED) | END OP period | Loops |
|---|---|---|---|---|---|---|---|
| 3.8.9 FP Store Low Order | 232 | 8-8 | 2/1/62 | FP CLOCK 0-7, break after 4 | 8 (0..7); T0 + 2n + 1 | 6 | normalize T3/T4-TC pairs, 2 periods each; note says "one shift", ink shows >=3 pairs (conflict) |
| 3.8.10 FP Store Root sh.1 | 233 | 8-9 | 2/1/62 | PAU: FP CLOCK 0-3; SAU: 15 A PULSES drawn, 2 breaks | PAU 3 + hand-over; SAU ~50 A periods implied by labels (DERIVED) | n/a | RFL 47->0 by 2 (25 C-bit-pair routings), SCR 96->0 by 2 (48 root bits); fixed counts |
| 3.8.10 FP Store Root sh.2 | 234 | 8-10 | 2/1/62 | FP CLOCK unnumbered, 5 periods | 5 | P3 | one normalize pass drawn |
| 3.8.11 FP Multiply | 235 | 8-11 | 2/1/62 | FP CLOCK 0-10 | 11 (0..10; 10 only for "DOUBLE OPER") | 8 | CSA LOOPS I-IV (fixed 4, overlapping, ~1.4 periods each) + MAIN ADDER LOOP 6-8 (2 periods) |
| 3.8.12 FP Load Multiplier Reg | 236 | 8-12 | 2/1/62 | circled 0-5 | 6 (0..5) with 2 normalization sequences | 4 | ADDER LOOP 1,2 and EXPONENT LOOP 1,2, 2 periods each |
| 3.8.13 FP Multiply and Add | 237 | 8-13/8-14 | 2/1/62 | circled 0-15 | main 12 (0..11); "accumulator exponent smaller" path 15 (0..14) | 10 (main), 13 (alt) | no CSA rows; multiply ring as 3.8.11 but 4 S&T latches |
| 3.8.14 FP Store Multiplier Reg | 238 | 8-15 | 2/1/62 | circled 0-6 | 6 (0..5) with 2 normalization cycles | 4 | ADDER LOOP 1,2 / EXP LOOP 1,2, 2 periods each |

Answers to the "surprising" items, negatives included:
- SAU: named on 3.8.9 ("... SAU", "SAU ADDER" for the exponent / shift amount), 3.8.10 ("SQUARE ROOT DEVELOPMENT UNDER SAU CONTROL", "(TURN CONTROL OVER TO SAU)" paired with "SIGNAL SSQ TO VFL TGR", "(SIGNAL SSQ TO VFL)", "(PAU RESUME CONTROL)", "GATE C EXP TO SAU"), 3.8.11 ("GATE EXPONENTS TO SAU ADDER", "GATE A EXP TO. SAU ADDER"). NOT named on 3.8.12, 3.8.13, 3.8.14.
- VFL: 3.8.10 uses "VFL" for the SAU hand-off ("SIGNAL SSQ TO VFL TGR"). 3.8.13 routes the exponent arithmetic to a "VFL ADDER" ("GATE BEXP PLUS CEXP TO VFL ADDER", "GATE A EXP MINUS C EXP TO VFL ADDER") where 3.8.11 says "SAU ADDER" for the same job (DERIVED: SAU adder and VFL adder are the same unit under two names). **No "VFL multiply" appears on any of these charts.**
- Second multiplier: **none printed.** 3.8.13 has an extra ring trigger "MR3" (alt path, period 10) and the "GATE 37 = D REG TO MULTIPLE GENERATION CKTS" line, but no second multiplier is named.
- Register widths printed: ADDER 0-99, F 0-89 (3.8.12) / F 0-99 (3.8.14), SHIFTER 0-99, F REG POS 100 & 101 (3.8.10), ACOB 12-59 -> C 12-59, C 12-59 -> ADDER 2-49, D12-59 -> ADDER 2-49, S/T REG 49-61 -> F REG 1-12 / 62-73, S and T regs (2-61) -> main adder (2-61), F REG (1-36) -> adder (62-97), F REG 50-97 -> MAIN ADDER 50-97, F REG shift of 12 POS 1-37 & 62-85, C POS 0-11 (exponent), BAAB set to 112 / reset to 10, SCR 96, RFL 47, "48 TO SH CTR ADDER" (3.8.9).
- Data-dependent loop counts: normalization pass count everywhere (exit on SH≤6 / NOT END OP); preshift "SH<4" on 3.8.13; GATE 63 vs GATE 72 per root step on 3.8.10. NOT data-dependent as drawn: the 4 CSA loops of 3.8.11, the RFL (47) and SCR (96) counts of 3.8.10.

### Appendix C

#### Transcription C — R23-9732 (7101 CPU CE manual), PDF pp. 241 (right), 244, 266, 267, 268

Tiles are in [scratch, deleted]/tC/
Convention: a parenthesised condition printed just left of a rising edge is the condition that turns that line ON at that clock.
"Period n" = the interval starting at circled clock (n). Edge positions read from tiles by pixel column; anything inferred is marked DERIVED.

---------------------------------------------------------------------------------------------------

#### Fig 3.8.17 — "FIGURE 3.8.17. FLOATING-POINT ADD TO EXPONENT (TIMING)"

- PDF page 241, RIGHT half (left half = Fig 3.8.15 sheet 3, skipped). No sheet number printed (single sheet).
- Running head: "M3-04-3" (left) / "PAU TIMING CHARTS" (right).
- Foot: date "2/1/62" (left), page "8-21" (right). (tile a241_ft.png)
- Clock axis: circled numbers 0,1,2,3,4,5,6,7,8 above a square-wave clock; each circled number sits on a clock rising edge. First 0, last 8. No "FP CLOCK" label printed; the row is unlabelled. (a241_1.png, a241_2.png)
- Printed side note (left, mid-chart): "ADD IMMEDIATE TO EXPONENT IS IDENTICAL" and below it "E + I". (a241_3.png)
- NOTE (bottom left, verbatim): "NOTE: THIS EXAMPLE SHOWS TWO NORMALIZATION SEQUENCES" (a241_5.png)

#### Lines, top to bottom, verbatim, with ON/OFF positions

| # | Label (verbatim) | Enabling condition (verbatim) | ON | OFF | tile |
|---|---|---|---|---|---|
| 1 | LA ENABLE | (none printed) | already high at left edge before (0) | slow decay during period 0, low by ~3/4 of period 0 | a241_1 |
| 2a | TO (upper timing row) | (START CTRL) | (0) | (1) | a241_1 |
| 2b | T2 (upper row) | (T1, ADD EXP) printed in period 1 | (2) | (3) | a241_1 |
| 2c | T3 (upper row) | (MR3, ADD EXP) printed in period 3 | (4) | (5) | a241_2 |
| 2d | T3 (upper row, 2nd) | (T4, NM, EO-bar) — printed "(T4, NM, EO)" with an overbar on EO | (6) | (7) | a241_2 |
| 3a | T1 (lower timing row) | (TO, ADD EXP) | (1) | (2) | a241_1 |
| 3b | MR 3 | (T2, ADD EXP) | (3) | (4) | a241_1 |
| 3c | T4 | (T3) | (5) | (6) | a241_2 |
| 3d | T4 (2nd) | (T3) | (7) | (8) | a241_2 |
| 4 | END OP | (T3, NE, SH≤6) — "SH" followed by a ≤ glyph (≤ over-struck on =) and "6" | (7) | (8) | a241_2 |
| 5 | SAMPLE OP CODE TO EXEC REG AND TØB TO C REG | (START CTRL) | (0) | ~mid period 0 (short pulse) | a241_1 |
| 6 | FIRST CYCLE TRIGGER | (START CTRL) | (0) | (5) | a241_1, a241_2 |
| 7 | GATE A & C EXPONENTS TO VFL ADDER | (ADD EXP, FCT, NOT NE, NOT A+C FLAG) | (0), sloped rise | slow decay early in period 4 (DERIVED from pixel column) | a241_1, a241_2 |
| 8 | GATES 31 & 32 - AB 12-107 TO F2-97 = AEXP FCT | (FCT, ADD EXP) | (0), sloped rise | slow decay just after (5) | a241_1, a241_2 |
| 9 | F REG & SCR REG LATCH AND SAMPLE (T3, NE) | first pulse: (TO); later pulses: (T3, NE) printed in periods 4 and 6 | pulses at (1), (5), (7) | each ~half a period | a241_1, a241_7 |
| 10 | GATES 61 & 63 ADDER 0-99 TO F 0-99 | (TO, ADD EXP) | (1) | (8) | a241_1, a241_7 |
| 11 | WRITE EXPONENT A | (TO, TO ACC) | (1) | not shown (continues past (8) to right edge) | a241_1, a241_2 |
| 12 | EXPONENT ROUTING CONTROL TRIGGER - TP6 | (T1, ADD EXP, NOT INT) — the word "EXPONENT" above and ", NOT INT)" are UNDERLINED WITH DASHES | prior state shown DASHED (an upper dashed level under "EXPONENT" and a lower dashed level under the condition), then a curved FALL just after (2) to a solid LOW level that continues past (8). DERIVED reading: (T1, ADD EXP, NOT INT) turns TP6 OFF just after (2), whatever its prior state; this agrees with row 15, gated (NE, NOT TP6), rising at (4) | after (2) | a241_8 (zoom), a241_3 |
| 13 | EXPONENT LATCH AND SAMPLE | first: (MR3, ADD EXP); then "TC , NOT INT" (period 5) and "(TC, NOT INT)" (period 7) | (4), (6), (8) | each falls just before the next clock (≈ full period) | a241_4, a241_7 |
| 14 | NORM EXPONENT TRIGGER | (MR3, ADD EXP) | (4) | (8) | a241_4 |
| 15 | GATE A EXP TO VFL ADDER & NORM AMT TO C SIDE | (NE, NOT TP6) | (4), sloped rise | slow decay just after (8) | a241_4 |
| 16 | NORM MANTISSA TRIGGER | (T3, NE) | (5) | (8) | a241_4 |
| 17 | GATE 21 & 22 TRIGGERS- SHIFTER 0-99 TO ADDER 0-99 | (T3, NE) | (5) | (8) | a241_4, a241_6 |
| 18 | GATE 11 & 12 -SHIFTER TO ACIB | (TEST COMP, END OP) | ~mid period 7 | ~mid period 8 | a241_4, a241_6 |
| 19 | TC (line labelled "Tc") | first: (T1, ADD EXP); later (T3,NE) printed in period 4 and (T3, NE) in period 6 | (2), (5), (7) | (3), (6), (8) | a241_3, a241_4 |
| 20 | STC | (T2, ADD EXP) | (3) | (4) | a241_3, a241_4 |
| 21 | SAMPLE TO ACC - 12-59 | (none printed) | (8) | ~mid period 8 | a241_6 |
| 22 | LATCH ACOB | (none printed) | ~mid period 8 (as SAMPLE TO ACC falls) | continues to right edge | a241_6 |
| 23 | ARITH CHECKER SAMPLE TO ACC 60-107 | (none printed) | right of the last drawn clock: ≈ one period after (8), i.e. period "9" — no clock is drawn there (DERIVED from pixel column) | ~half period later | a241_6 |

"ARITH CHECKER SAMPLE TO ACC 60-107": the "107" is degraded ("6U-1o7" look); reading "60-107" is DERIVED by analogy with "AB 12-107" and "ACC - 12-59". (a241_6)

#### Cycle table (one row per period)

| Period | Timing level(s) | What is ON / rises |
|---|---|---|
| 0 | TO | LA ENABLE decays; SAMPLE OP CODE TO EXEC REG AND TØB TO C REG pulse (START CTRL); FIRST CYCLE TRIGGER on (START CTRL); GATE A & C EXPONENTS TO VFL ADDER (ADD EXP, FCT, NOT NE, NOT A+C FLAG); GATES 31 & 32 - AB 12-107 TO F2-97 = AEXP FCT (FCT, ADD EXP) |
| 1 | T1 | F REG & SCR REG LATCH AND SAMPLE pulse (TO); GATES 61 & 63 ADDER 0-99 TO F 0-99 on (TO, ADD EXP); WRITE EXPONENT A on (TO, TO ACC); EXPONENT ROUTING CONTROL TRIGGER - TP6 prior state dashed; (T1, ADD EXP, NOT INT) turns it OFF just after (2) (DERIVED, see row 12) |
| 2 | T2 | TC (T1, ADD EXP) |
| 3 | MR 3 | STC (T2, ADD EXP) |
| 4 | T3 | EXPONENT LATCH AND SAMPLE (MR3, ADD EXP); NORM EXPONENT TRIGGER (MR3, ADD EXP); GATE A EXP TO VFL ADDER & NORM AMT TO C SIDE (NE, NOT TP6); GATE A & C EXPONENTS decays |
| 5 | T4 [(T3)] | F REG & SCR REG LATCH AND SAMPLE pulse (T3, NE); NORM MANTISSA TRIGGER (T3, NE); GATE 21 & 22 TRIGGERS (T3, NE); TC (T3,NE); FIRST CYCLE TRIGGER off; GATES 31 & 32 decay |
| 6 | T3 [(T4, NM, EO-bar)] | EXPONENT LATCH AND SAMPLE (TC , NOT INT) |
| 7 | T4 [(T3)] | END OP (T3, NE, SH≤6); F REG & SCR REG LATCH AND SAMPLE pulse (T3, NE); TC (T3, NE); GATE 11 & 12 -SHIFTER TO ACIB (TEST COMP, END OP) from mid-period |
| 8 | — (all timing levels, END OP, NORM triggers, GATES 61&63, GATE 21&22, TC off at (8)) | EXPONENT LATCH AND SAMPLE (TC, NOT INT); SAMPLE TO ACC - 12-59; LATCH ACOB from mid-period; GATE 11&12 off mid-period |
| (9, undrawn) | — | ARITH CHECKER SAMPLE TO ACC 60-107 (DERIVED position) |

#### Path lengths
- PRINTED: none (no cycle count or ns figure printed).
- COUNTED: clocks (0)..(8) drawn. Fixed part TO,T1,T2,MR3 = periods 0-3 (4 periods). Each normalization sequence = one T3 + one T4 = 2 periods; this example shows two (periods 4-5 and 6-7), as the NOTE says. END OP is on in period 7 (the last T4), so TO..END OP = 8 periods; results gated to ACC in period 8 and the checker sample after it.
- DERIVED: the T3 -> T3 loop is re-entered under (T4, NM, EO-bar) and END OP comes under (T3, NE, SH≤6); with N normalization sequences the length would be 4 + 2N periods to END OP — not printed, inferred from the drawing only.
- No mention of a second multiplier, D register, or PAU doing SAU work. Uses the VFL adder for the exponent arithmetic ("GATE A & C EXPONENTS TO VFL ADDER", "GATE A EXP TO VFL ADDER & NORM AMT TO C SIDE").

---------------------------------------------------------------------------------------------------

#### Fig 3.8.20 — "FIGURE 3.8.20. FLOATING POINT RECIPROCAL DIVIDE TIMING"

- PDF page 244. Fold-out page (5100x3300) but ALL drawing is on the LEFT ~2200 px; the right half is blank (thresholded mean 0.99998 white over x>=2200). No sheet number printed (single sheet).
- Running head: "PAU TIMING CHARTS" (left) / "M3-04-3" (right).
- Foot: page "8-24" (left), date "1/1/63" (right) — note this is a later issue date than the 2/1/62 pages around it. (g244_foot.png, gL_2600.png)
- Clock axis: row labelled "FP CLOCK", numbered 0,1,2,3,4,5,6,7 (first 0, last 7), number over each rising edge; the clock wave stops about half a period after 7. A second, short "FP CLOCK" row (3 pulses, unnumbered, first edge marked "*") heads the ZERO DIVISOR sub-chart; I call its edges Z0, Z1, Z2, Z3 (my labels, not printed).
- Tiles: b244_*.png are raw; g244.png and gL_*/gR_* are copies with red guide lines I drew at the clock rising edges 0..7 (x = 430, 625, 822, 1018, 1218, 1413, 1610, 1808 in page pixels; checked against the printed clock in gL_200/gR_200). In the ZERO DIVISOR sub-chart the guides at x=430/625/822/1018 fall on its own edges Z0/Z1/Z2/Z3.
- Printed annotations (verbatim, gR_200): at clock 6 a dashed vertical line with "<-IDENTICAL TO DIVIDE (POINT 3) FROM THIS POINT EXCEPT FOR *." ; at clock 7 a dashed vertical line with "* ZERO DIVISOR SEE BELOW".
- Convention on this chart (DERIVED): for the timing-level rows, the printed condition names the level of the PREVIOUS period, e.g. "(TO,FCT,DIV I)" turns MR1 on at clock 1. For the gate/trigger rows, several conditions name the level of the period in which the line is ON (e.g. "(MR2,DIVI FCT)" GATE 11 rises at clock 2, during MR2). Edges below are as DRAWN; I have not re-interpreted them.

#### Main chart, lines top to bottom (verbatim)

| # | Label | Condition (verbatim) | ON | OFF | tile |
|---|---|---|---|---|---|
| 1 | TO | (START CTRL) | 0 | 1 | gL_200 |
| 2 | MRI (MR1) | (TO,FCT,DIV I) | 1 | 2 | gL_200 |
| 3 | MR2 | (MRI,DIV I) | 2 | 3 | gL_200 |
| 4 | MR3 | (MR2,FCT,NOT INT, ID) | 3 | 4 | gL_200 |
| 5 | T1 (printed "TI") | (MR3, ID) | 4 | 5 | gL_200, gR_200 |
| 6 | D3 (printed "D3", subscript 3) | (T1, ID) | 5 | 6, where the row steps DOWN; it steps up again at 7 labelled "D3" and ends in a squiggle (continues) | gR_200 |
| 7 | DT | (D3, DNE) | 6 | 7, ends in a squiggle | gR_200 |
| 8 | SAMPLE TO C & EXECUTION REG | (START CTRL) | 0 | ~mid period 0 | gL_200 |
| 9 | FIRST CYCLE TGR | (START CTRL); "(FCT)" printed near the falling end | 0 | 4 | gL_700 |
| 10 | GATE 33 ... "(C REG TO ADDER)" | (DIVI, FST, ID-bar) — printed "FST", not FCT; ID overbarred | 0 | 2 | gL_700 |
| 11 | GATE A EXP TO SAU ADDER | (DIVI; FCT, ID-bar) | 0 | 2 | gL_700 |
| 12 | GATE 61 & 63 (TGR) | (DIVI, TO) | 1 | not shown: runs past 7, ends in a squiggle (~x 1900) | gL_700, gR_700 |
| 13 | WRITE EXP D TGR | (TO, DIVI) | 1 | 3 | gL_700 |
| 14 | INTERCHANGE DIVIDE TGR ... "(ID)" | (MRI, DIV I) | 2 | 6 | gL_700, gR_700 |
| 15 | SAMPLE TEST COMP | (none printed) | 2 | 3 | gL_700 |
| 16 | GATE 31 ... "(A REG TO ADDER)" | (none printed) | 2 | 4 | gL_700, gR_700 |
| 17 | GATE 11 ... "(F REG TO CHECKER)" | (MR2,DIVI FCT) | 2 | 3 | gL_700 |
| 18 | GATE C EXP TO SAU ADDER | (ID, DNE-bar) | 2 | 4 | gL_700 |
| 19 | LATCH ACOB | (MR2, NOT INT, DIVI,FCT) — "DIVI,FCT" underlined | 3 | the line stops just before 4; no falling edge drawn | gL_1200, z244_acob |
| 20 | (pulse) "(SAMPE TO A REG)" [sic, "SAMPE"] | (MR3, ID) | 4 | ~mid period 4 | z244_acob |
| 21 | WRITE EXP A TGR | (MR2, NOT INT, DIV I, FCT) | 3 | 6 | gL_1200, z244_acob |
| 22 | DIVIDE NORMALIZE EXP TGR (ONE) | (none printed) | 4 | not shown: runs past 7 (~x 1890) | gR_1200, z244_shift |
| 23 | GATE 21 (TGR) | (MR3,ID) | 4 | 6, with "<-SHIFT AMOUNT <=6" at the fall; a DASHED continuation from 6 to 7 labelled ">6" | z244_shift |
| 24 | BA 64 TGR | (MR3.ID) | 4 | 7, falling edge marked "*" | gR_1200 |
| 25 | GATE D EXP TO SAU ADDER | (BA64) | 4 | 7, marked "*(FIRST NORM CYCLE)" | gR_1200, z244_shift |
| 26 | TP6 TGR | (D3,DIV I) | 5 | not shown: past 7, squiggle | gR_1200 |
| 27 | DIVISOR TGR (DVSR) | (D3,DIV TYPE) — "PE)" underlined | 6 | not shown: past 7, squiggle | gR_1200 |
| 28 | WRITE EXP C TGR | (D3, DIV TYPE) | 6 | not shown: past 7, squiggle | gR_1200, z244_gatec |
| 29 | GATE C EXP TO SAU | (DNE, TP6, NOT 64) — "64)" underlined | 7 | about clock "8" (one period later) — see ambiguity below | gR_1700, z244_gatec |
| 30 | EXP LATCH & SAMPLE | first: "(MRI DIV±)" — the glyph after DIV looks like ± over an underline; "DIV I" is my DERIVED reading. second: (MR3, ID) | 2, 4 | 3, 5 | gL_1700, z244_explatch |
| 31 | F REG LATCH | (none printed) | half-period pulses at 1, 2, 4, 6 | each ~mid period | gL_1700, gR_1700, z244_explatch |

"SHIFT AMOUNT <=6": the glyph between "AMOUNT" and "6" is a small <=-like mark printed over the T, read as <= by analogy with the ">6" printed just above it and Fig 3.8.17's "SH<=6" — DERIVED; the bare glyph is unclear (z244_shift.png).

Ambiguity, row 29/30 (z244_gatec.png): the pulse from 7 to about 8 is drawn on the same baseline as the EXP LATCH & SAMPLE row, directly under the "(DNE, TP6, NOT 64)" GATE C EXP TO SAU label, which has a short overline of its own starting at 7. From the drawing alone I cannot tell whether the 7 pulse belongs to GATE C EXP TO SAU or is a third EXP LATCH & SAMPLE pulse. Either way, something is gated at clock 7.

Register-transfer arrows (double-headed spans, gL_1700/gR_1700):
- "C FRACTION TO A REG": from about clock 0 to clock 4.
- "A EXP TO D REG": from about clock 0 to clock 2.
- "A FRACTION TO ADDER & START· DIVISOR NORMALIZATION": from clock 2 to past 7 (squiggle, ~x 1950).
- "C EXP TO A REG": from clock 2 to clock 4.
- "D EXP TO C 1ST NORMAL CYCLE": from late in period 3 (left arrowhead just before 4) to clock 7.
- A heavy rule from 0 to past 7 with "ZERO DIVISOR" printed under it: this is the heading of the sub-chart below.

#### Main chart, cycle table

| Period | Timing level | ON / rising |
|---|---|---|
| 0 | TO | SAMPLE TO C & EXECUTION REG pulse; FIRST CYCLE TGR; GATE 33 (C REG TO ADDER); GATE A EXP TO SAU ADDER; [C FRACTION TO A REG, A EXP TO D REG spans begin] |
| 1 | MR1 | GATE 61 & 63 (TGR) (DIVI, TO); WRITE EXP D TGR (TO, DIVI); F REG LATCH pulse |
| 2 | MR2 | INTERCHANGE DIVIDE TGR (MRI, DIV I); SAMPLE TEST COMP; GATE 31 (A REG TO ADDER); GATE 11 (F REG TO CHECKER) (MR2,DIVI FCT); GATE C EXP TO SAU ADDER (ID, DNE-bar); EXP LATCH & SAMPLE (MRI DIV I); F REG LATCH pulse; GATE 33 and GATE A EXP off; [A FRACTION TO ADDER & START DIVISOR NORMALIZATION, C EXP TO A REG begin; A EXP TO D REG ends] |
| 3 | MR3 | LATCH ACOB (MR2, NOT INT, DIVI,FCT); WRITE EXP A TGR (MR2, NOT INT, DIV I, FCT); WRITE EXP D TGR off |
| 4 | T1 | (SAMPE TO A REG) pulse (MR3, ID); DIVIDE NORMALIZE EXP TGR (ONE); GATE 21 (TGR) (MR3,ID); BA 64 TGR (MR3.ID); GATE D EXP TO SAU ADDER (BA64); EXP LATCH & SAMPLE (MR3, ID); F REG LATCH pulse; FIRST CYCLE TGR, GATE 31, GATE C EXP TO SAU ADDER off; [C FRACTION TO A REG and C EXP TO A REG end; D EXP TO C 1ST NORMAL CYCLE runs] |
| 5 | D3 | TP6 TGR (D3,DIV I) |
| 6 | DT (D3, DNE) | DIVISOR TGR (DVSR) (D3,DIV TYPE); WRITE EXP C TGR (D3, DIV TYPE); F REG LATCH pulse; INTERCHANGE DIVIDE TGR and WRITE EXP A TGR off; GATE 21 off if SHIFT AMOUNT <=6, else (dashed) stays on to 7 — "IDENTICAL TO DIVIDE (POINT 3) FROM THIS POINT EXCEPT FOR *." |
| 7 | D3 (continues, squiggle) | GATE C EXP TO SAU (DNE, TP6, NOT 64) [or EXP LATCH pulse, see ambiguity]; BA 64 TGR "*" and GATE D EXP TO SAU ADDER "*(FIRST NORM CYCLE)" off; "* ZERO DIVISOR SEE BELOW" |

#### ZERO DIVISOR sub-chart (gL_1700, gL_2200, gL_2600)
Starts at the "*" (clock 7 of the main chart, per "* ZERO DIVISOR SEE BELOW"). Own FP CLOCK, 3 pulses, edges Z0, Z1, Z2 (my labels; Z3 = where the 4th edge would be).

| Label | Condition (verbatim) | ON | OFF |
|---|---|---|---|
| TB | (D4 DVSR F=0) — printed "F•O"/"F=O" | Z0 | Z1 |
| TC | (TB) | Z1 | Z2 |
| DVSR | (squiggle: continues from main chart) | before Z0 | Z2 |
| WRITE EXP C TGR (printed "WRITE EXPC_TGR") | (squiggle: continues) | before Z0 | Z1 |
| BA 64 TGR | (squiggle: continues) | before Z0 | Z2 |
| GATE D EXP SAU ADDER | (squiggle: continues) | before Z0 | Z2 |
| END OP TGR | (D4,DVSR, F=O) | Z0 | Z2 |
| GATE 11 | (END OP, TEST COMP) | ~mid Z0 period | ~mid Z2 period |
| WRITE EXP A TGR "(F REG TO CHECKER)" | (TB, DVSR) — "R)" underlined | Z1 | top line runs to ~mid Z2 period; no falling edge drawn |
| LATCH ACOB | (END OP,NOT INT) — "INT)" underlined | Z2 | top line runs to just before Z3; no falling edge drawn |
| LATCH & SAMPLE EXP | (END OP NOT INT) — printed "(END OR NOT INT)", "OR" read as OP | Z2 | Z3 |
| SAMPLE A REG | (END OP, NOT INT) | Z2 | ~mid Z2 period |
| SAMPLE ZERO DIVISOR INDICATOR | (TC, DVSR, NOT INT, END OP) | Z2 | ~mid Z2 period |

The "(F REG TO CHECKER)" text sits at the end of the WRITE EXP A TGR line, but it probably belongs to GATE 11 as in the main chart. That attribution is DERIVED.

#### Path lengths
- PRINTED: no cycle count or ns figure.
- COUNTED: the reciprocal-divide preamble is periods 0-5 (TO, MR1, MR2, MR3, T1, D3) = 6 periods. At clock 6 it joins Divide "POINT 3" ("IDENTICAL TO DIVIDE (POINT 3) FROM THIS POINT EXCEPT FOR *"). The rest of the divide is not on this page; see Fig 3.8.15 (Divide). DERIVED (not verified): Fig 3.8.15 sheet 3, on the left half of PDF 241, prints "RETURN TO POINT 11, PART B, SHEET 1" and "RETURN TO POINT 9, PART B, SHEET 1" beside circled clock numbers. That suggests "POINT n" means circled clock n of the Divide chart. If so, Reciprocal Divide = Divide + 3 periods (clock 6 here ≡ Divide clock 3). I only saw this in the 241 overview; I did not transcribe that half.
- COUNTED, zero divisor sub-chart: TB in period Z0, TC in period Z1. END OP TGR is ON for periods Z0 and Z1 and falls at Z2. LATCH & SAMPLE EXP, SAMPLE A REG and SAMPLE ZERO DIVISOR INDICATOR are in period Z2. That is 3 sub-chart periods.
- The offset of Z0 from the main clock is NOT PRINTED on this sheet. TB's condition is "(D4 DVSR F=0)", but this chart has no D4 level (period 6 is DT, period 7 is D3). D4 belongs to the Divide chart (Fig 3.8.15), so a total from TO cannot be counted from this page.
- Conditional path: GATE 21 (shifter gate) lasts one period longer when SHIFT AMOUNT >6 (dashed), so the first normalization cycle depends on the shift amount (DERIVED from the dashed line).
- Units: the exponent arithmetic goes through the "SAU ADDER" ("GATE A EXP TO SAU ADDER", "GATE C EXP TO SAU ADDER", "GATE D EXP TO SAU ADDER", "GATE C EXP TO SAU"). Fig 3.8.17 instead says "VFL ADDER" for the same job. DERIVED (not printed): the PAU's exponent arithmetic appears to run on the serial (SAU/VFL) adder. A D register is named ("A EXP TO D REG", "WRITE EXP D TGR", "D EXP TO C 1ST NORMAL CYCLE", "GATE D EXP TO SAU ADDER"); on this chart it holds exponents only. No second multiplier is mentioned.

---------------------------------------------------------------------------------------------------

#### Fig 3.11.12 — "FIGURE 3.11.12. VLF COMPARE INSTRUCTIONS" [sic: "VLF", not "VFL"]

- PDF page 266, fold-out (5100x3300), two-page spread.
- Running head: "M3-04-3" / "SAU FLOW DIAGRAMS" (top right only).
- Foot: date "1/1/63", page "11-23/11-24". (z266_foot.png)
- FLOW DIAGRAM. **Cycle count NOT PRINTED.** No clock numbers, A/B pulses or timing anywhere on the page. ALD references are printed in the boxes as NN.NN.NN.
- Tiles: c266_X_Y.png (X,Y = page-pixel origin, 1200x1000); zooms z266_*.png.
- Notation: "(A)" and "(B)" are circled connectors. "→X" means the exit goes to X. A "bus" is a horizontal line with junction dots. Several decisions hang off one bus side by side; I read these as parallel tests in the same step (DERIVED: the drawing does not say).

#### Legend (bottom right, verbatim with overbars; z266_legend.png)
```
K   (Ā B C̄ D̄ Ē)
KF  (A B C̄ D̄ Ē)
KE  (Ā B C̄ D̄ E)
KFE (A B C̄ D̄ E)
KR  (Ā B C̄ D Ē)
KFR (A B C̄ D Ē)
```
Overbar extents were read at 3x zoom. The bars over C, D and E are separate short bars, or one long bar where adjacent letters are both barred. DERIVED pattern: A = F (field form), D = R (range), E = E (equal).

#### Part 1 — start-up (left page; c266_250_250, c266_1150_250, c266_250_1050)
Entry conditions printed at the top left: "DECODED VFL INST / SAU NOT OPER / PAU NOT OPER / LA START". These feed three parallel boxes:
- "SET VFL OP 56.16.00"
- "TON HK TRIG 56.16.00"
- "LOAD SAU EXEC REG 55.10.-.-"

TON HK TRIG drops onto a horizontal bus (an arrowhead on its left end marks the re-entry from the LA GO NO loop below). Five parallel tests hang from the bus:
1. ◇ "BAER = 0": NO → "LOAD BACD TO BAER-1 54.21.01"; YES → "LOAD BACD TO 64-1 54.21.02".
2. ◇ "BINARY": NO → "LOAD BAAB TO OS-bar ASSUME 2 LO ORDER 0'S" → "LOAD RFL TO FLER-BS 54.32.-.-". YES → "LOAD BAAB TO OS-bar" → ◇ "SIGNED": YES → "LOAD RFL TO FLER-BS 54.32.-.-" (the same box the decimal path enters); NO → "LOAD RFL TO FLER-8 54.32.-.-". (The OS in "TO OS" carries an overbar.)
3. ◇ "LA GO": YES → "RESET SCRD 54.60.06". No NO exit is drawn.
4. ◇ "KF ETC": NO → ◇ "SAB = NSM": NO → "TOF LIKE SIGNS 56.15.01"; YES → "TON LIKE SIGNS 56.15.01". KF ETC YES → ◇ "NSM = 0": NO → "TOF LIKE SIGNS 56.15.01"; YES → "TON LIKE SIGNS 56.15.01". TON LIKE SIGNS → ◇ "SIGNED": NO → "TON CD COMP 56.21.21"; YES → bus.
5. ◇ "LA REJECT": YES → "TON RESET ONLY 56.14.00", then a rounded note box: "RESET ONLY GENERATES INST RESET ONLY. SEE SIR OF LOAD."

Everything except branch 5 joins a lower bus, which feeds ◇ "LA GO":
- NO → a line runs back up the left edge to the top bus (arrowhead): a wait loop. It repeats the five tests until LA GO.
- YES → three parallel items: "TOF HK 56.16.00"; ◇ "RFL CARRY" with NO → "TON EOC 1 54.38.01" (no YES exit drawn); ◇ "SIGNED".
  - SIGNED NO → "TON PL1 56.11.06" → (A).
  - SIGNED YES → "TON HSB 56.11.00" → the sign-byte step below.

#### Part 2 — sign-byte step (HSB) (left page, lower half; c266_250_1050, c266_1150_1050, c266_250_1850, c266_1150_1850)
TON HSB feeds a bus with four parallel branches:
- "READ OUT CD SIGN BYTE AT BACD PUT INTO SRCD 54.60.06" → ◇ "SCD = 1": YES → "INVERT LIKE SIGNS TRIG 56.15.01"; NO → join. Then ◇ "LIKE SIGNS": YES → "TON CD COMP 56.21.21"; NO → bus.
- ◇ "BINARY": NO → "REDUCE RFL BY BSER 54.32.01"; YES → "REDUCE RFL BY 8 54.32.01". Then ◇ "RFL CARRY": YES → bus; NO → "TON EOC1 54.38.01" → bus.
- "REDUCE BACD BY BSER 54.22.02" (printed "54.22.Ø2"; the second digit is blotted) → bus.
- ◇ "EOC1": YES → "TON EOC2 54.38.03" and, in parallel, "TON CD CUTOFF 56.21.11" → bus. No NO exit is drawn.

The bus also feeds "TOF HSB 56.11.0" [sic: "56.11.0"] and ◇ "KF ETC":
- YES → ◇ "EOC1 ON BEFORE HSB": YES → (B); NO → "TON PL1 56.11.06" → (A).
- NO → "TON PL1 56.11.06" → (A).

#### Part 3 — per-byte loop, entered at (A) (right page, top; c266_2100_250, c266_3000_250, c266_3900_250, z266_pl)
(A) arrives at the top left of a bus. The re-entry line runs up the far left edge from the EOC1/EHOM1 NO exits below. Six parallel tests hang from the bus:
1. ◇ "EOA1": YES → "TON EOA2 54.18.01" and "TON AB CUT OFF 56.21.11". These two boxes do NOT connect to the lower bus; they end there. No NO exit is drawn.
2. ◇ "CD CUTOFF": YES → ◇ "CD COMP": YES → ◇ "BINARY": NO → "GATE 9'S TO ADDER 56.21.22"; YES → "GATE 1'S TO ADDER 56.21.22". CD COMP NO → "GATE 0'S TO ADDER 56.21.22".
3. CD CUTOFF NO → ◇ "CD COMP": YES → "GATE CD BYTE COMP TO ADDER 56.21.22"; NO → "GATE CD BYTE TRUE TO ADDER 56.21.22".
4. ◇ "AB CUTOFF": NO → "GATE AB BYTE TRUE TO ADDER 56.21.12"; YES → "GATE 0'S TO ADDER 56.21.12".
5. ◇ "1ST CYCLE" (the YES exit is also labelled "PL1 • PL2-bar"): NO → bus. YES → "TON PL2 56.11.06" and, in parallel, ◇ "LIKE SIGNS": YES → "ADDER CARRY IN 56.23.01" (no NO exit drawn).
6. ◇ "BINARY": YES → "UPDATE BACD BY 8. UPDATE BAAB BY 8 OR RFL. UPDATE RFL BY 8"; NO → "UPDATE BAAB BY 4. REDUCE RFL AND BACD BY BSER".

The lower bus feeds a hexagon "PERFORM ADD BUT NO WRITE IN". The (B) connector arrow joins just below the hexagon, so (B) skips the add. Next comes ◇ "KF ETC".

Per-byte stepping as printed: binary moves BACD by 8, BAAB by 8 or RFL, and RFL by 8. Decimal moves BAAB by 4 and reduces RFL and BACD by BSER. A cutoff (field exhausted) gates 0's, 1's or 9's instead of the byte. 9's is decimal and 1's is binary, both on the complement path (CD COMP).

#### Part 4 — after the add: loop control and result (right page, middle; c266_2100_1050, c266_3000_1050, c266_3900_1050)
KF ETC splits into two halves. Each half has a loop-control chain and a result chain, hung side by side from the same exit.

**KF ETC NO** (left; the exit runs left to a bus feeding two chains):
- Loop control: ◇ "EOC1": NO → back to (A). YES → ◇ "EHOM1": NO → back to (A); YES → "TOF PL1•2 TON SIR" (left box).
- Result chain: ◇ "LIKE SIGNS".
  - NO (unlike signs) → ◇ "NZRT ON".
    - YES → "TOF PL1•2 TON SIR" (left box) AND down to the bus into "AB GT CD OR CKT 56.52.01".
    - NO → ◇ "CARRY": YES → the same bus → "AB GT CD OR CKT"; NO → "AB = CD OR CKT 56.52.01" (left box).
  - YES (like signs) → ◇ "EHOM 1".
    - NO → ◇ "EOC2": NO → (A). YES → "TOF PL1• PL2 TON SIR" (centre box) AND "TON AB GT CD 56.52.01" → bus → "AB GT CD OR CKT".
    - YES → ◇ "CARRY".
      - NO → "TON AB LT CD 56.52.01" → "AB LT CD OR CKT 56.52.01", AND "TOF PL1• PL2 TON SIR" (centre).
      - YES → ◇ "EOC1": NO → back to (A). YES → "TON AB GT + E CD 56.52.01" AND "TOF PL1• PL2 TON SIR" (centre). TON AB GT + E CD then → ◇ "NZRT ON": NO → "AB = CD OR CKT" (left box); YES → "AB GT CD OR CKT".

**KF ETC YES** (right) → ◇ "LIKE SIGNS":
- NO (unlike signs) → two parallel chains:
  - ◇ "EOC1": NO → (A); YES → "TOF PL1• PL2 TON SIR" (centre).
  - ◇ "CARRY": YES → "AB GT CD OR CKT". NO → ◇ "NZRT ON": YES → "AB GT CD OR CKT"; NO → "AB = CD OR CKT" (centre box, printed "AB = CD OK CKT" in the overview; reads "AB = CD OR CKT 56.52.01" at full resolution) AND "TOF PL1• PL2 TON SIR" (centre).
- YES (like signs) → two parallel chains:
  - Loop control: ◇ "EOC1": YES → "TOF PL1•2 TON SIR" (right box). NO → ◇ "EHOM1": NO → (A). YES → ◇ "CARRY": YES → (A); NO → "TOF PL1•2 TON SIR" (right box).
  - Result chain: ◇ "CARRY".
    - YES → ◇ "NZRT ON": YES → "AB GT CD OR CKT"; NO → "AB = CD OR CKT" (centre).
    - NO → ◇ "NZRT ON": YES → "AB LT CD OR CKT"; NO → "AB = CD OR CKT" (centre).

Wiring note: the centre "TOF PL1• PL2 TON SIR" box has 5 entry lines and "AB GT CD OR CKT" has 5. I traced each line by pixel across tiles c266_2100_1050, c266_3000_1050 and c266_3900_1050. The tracing is mine (DERIVED from the drawing), and the tangle is dense, so this is the part of the page most worth a spot-check.

#### Part 5 — indicator setting (inside the SIR boundary box; c266_2100_1850, c266_3000_1850, c266_3900_1850)
- Both "AB = CD OR CKT" boxes → ◇ "K+ KE + KF + KFE": YES → "SAU SET AE 56.52.02"; NO, labelled "NO (KR + KFR)", → "SAU SET AH 56.52.02".
- "AB GT CD OR CKT 56.52.01" → ◇ "SAB PLUS": YES → "SAU SET AH 56.52.02" (the same box as above). NO → ◇ "KR + KFR": YES → "SAU SET AE"; NO → "SAU SET AL".
- "AB LT CD OR CKT 56.52.01" → ◇ "SAB PLUS": NO → "SAU SET AH". YES → ◇ "KR + KFR": YES → "SAU SET AE"; NO → "SAU SET AL".
- "S I R" labels a U-shaped collector line, not an enclosing box. It joins the outputs of the left and right "TOF PL1•2 TON SIR" boxes to the centre one's line at a junction, which then crosses the dashed line into Part 6. The SAU SET AE/AH/AL boxes are dead ends: no line leaves them.

#### Part 6 — below the dashed line: "NORMAL SIR CYCLE WITH THESE ADDITIONS" (c266_3000_1850, z266_kekfl)
- ◇ "KE&KFL" [verbatim; read at 3x zoom. By the legend it is probably KE & KFE, but it is printed "KFL"]:
  - YES → ◇ "AE ON IN IND REG": YES → "SAU SET COMP RSLT INDS TO LA 56.52.04". No NO exit is drawn.
  - NO → ◇ "KR + KFR": NO → "SAU SET COMP RSLT INDS TO LA 56.52.04". YES → ◇ "AH ON IN IND REG": YES → "SAU SET COMP RSLT INDS TO LA". No NO exit is drawn.

#### Answers to the specific questions (Fig 3.11.12)
- Cycle count: NOT PRINTED.
- Per-byte stepping: yes. Binary: "UPDATE BACD BY 8. UPDATE BAAB BY 8 OR RFL. UPDATE RFL BY 8". Decimal: "UPDATE BAAB BY 4. REDUCE RFL AND BACD BY BSER". In the sign step, "REDUCE RFL BY BSER" (decimal) or "REDUCE RFL BY 8" (binary) and "REDUCE BACD BY BSER".
- Counters: BAER, BACD, BAAB, RFL, FLER, BSER, SCD/SRCD; end flags EOC1, EOC2, EOA1, EOA2, EHOM1, HSB, PL1, PL2, NZRT.
- Decimal vs binary: the BINARY decisions in Parts 1, 2 and 3, and 9's vs 1's on cutoff with complement.
- Signs: SAB = NSM, NSM = 0, LIKE SIGNS trigger, "INVERT LIKE SIGNS TRIG" when SCD = 1, CD COMP (complement CD) on like signs, and "ADDER CARRY IN" on the first cycle with like signs.
- Recomplement: none printed. The compare never writes ("PERFORM ADD BUT NO WRITE IN").
- Early end on inequality: YES, as drawn (DERIVED from my wire tracing). There are nine entry lines into the three loop-ending boxes ("TOF PL1•2 TON SIR" left and right, "TOF PL1• PL2 TON SIR" centre):
  1. Left, KF ETC NO: EOC1 YES and EHOM1 YES. EOC-gated.
  2. Left, KF ETC NO, unlike signs: NZRT ON YES (also → AB GT CD OR CKT). **NOT gated by EOC1/EOC2.**
  3. Centre, KF ETC NO, like signs: EHOM 1 YES, CARRY YES, EOC1 YES (also → TON AB GT + E CD). EOC1-gated.
  4. Centre, KF ETC NO, like signs: EHOM 1 YES, CARRY NO (also → TON AB LT CD). **NOT gated by EOC1/EOC2.**
  5. Centre, KF ETC NO, like signs: EHOM 1 NO, EOC2 YES (also → TON AB GT CD). EOC2-gated.
  6. Centre, KF ETC YES, unlike signs: EOC1 YES. EOC1-gated.
  7. Centre, KF ETC YES, unlike signs: CARRY NO, NZRT ON NO (also → AB = CD OR CKT). **NOT gated by EOC1/EOC2.** Wiring re-checked at 2x zoom in z266_mid.png.
  8. Right, KF ETC YES, like signs: EOC1 YES. EOC1-gated.
  9. Right, KF ETC YES, like signs: EOC1 NO, EHOM1 YES, CARRY NO. Gated by EHOM1, not by EOC1/EOC2.
  Every exit not caught here returns to (A) for the next byte.
- Logical-connective branch: none on this page.
- No mention of a second multiplier, the PAU, or a D register.

---------------------------------------------------------------------------------------------------

#### Fig 3.11.13 — "FIGURE 3.11.13. BINARY CONVERT AND BINARY CONVERT DOUBLE"

- PDF page 267, fold-out. Left ~38% of the sheet is blank. The flow occupies two columns: x≈1980-3420 (left column) and x≈3600-4980 (right column).
- Running head: "M3-04-3" / "SAU FLOW DIAGRAMS".
- Foot: date "1/1/63", page "11-25/11-26". (e267_4.png)
- FLOW DIAGRAM. **Cycle count NOT PRINTED.** No clock numbers, A/B pulses or timing.
- Tiles: c267_X_Y.png, d267_a..e.png, e267_1..4.png, e267_r.png; zoom z267_nsm.png.

#### Left column (d267_a, d267_b, d267_c, c267_2100_250, c267_2100_1050)
Entry: "DECODED UFL INST" [sic: "UFL"], "LA START", "SAU NOT OPER", "PAU NOT OPER". These feed three parallel boxes:
- "TON UFL OP 56.16.00" [sic: "UFL"]
- "TON HK 56.16.00"
- "LOAD SAU EXEC REG 55.20."

TON HK feeds a bus (an arrowhead marks the re-entry from the LA GO NO loop). Parallel items on the bus:
- "LOAD BACD WITH BAER-1 54.21.01"
- "LOAD BAAB WITH OS-bar 54.11.01" (OS overbarred)
- "LOAD RFL WITH FLER-8 OR BYTE SIZE 54.32.-"
- "RESET AØ THRU A11 56.24.40"
- "RESET AB AND CD RESIDUE REGS 56.26.10"
- ◇ "LA GO": YES → "RESET SRCD 54.60.06" → back to the lower bus. No NO exit is drawn.
- ◇ "REJECT": YES → "TON RESET ONLY 56.14.00" → rounded box "GENERATE INST RESET PORTION OR SIR 56.14.10" [sic, "OR SIR"; Fig 3.11.14 prints "OF SIR"].

The lower bus feeds ◇ "LA GO":
- NO → loops back to the top bus (wait loop).
- YES → "TOF HK TON SU AB-FHI 56.16.00 56.13.10", which feeds a second bus with these parallel items:
  - "RESET F REG 56.33.00" → "SET L1 INTO SHFT CTL 56.32.01"
  - "LOAD BAAB WITH HOM ØØØ 54.15.02"
  - ◇ "CVAD": YES → "107 HOM ØØØ TO RFL"; NO → "59 HOM ØØØ TO RFL". Both boxes carry the ALD note "54.31.01 AND 54.32.01".
  - "TOF AB CUTOFF 56.21.11"
  - ◇ "SIGNED": NO → "GATE NSM TO SAB 56.25.02"; YES → "GATE NSM [glyph] SAB TO SAB 56.25.02". The glyph is ILLEGIBLE: a blotted symbol, possibly ⊻ or ∀ as an exclusive-OR sign (z267_nsm.png).
  - All of these join a bus → "TOF SUAB- FHI, TON, AB-FHI 56.13.10".

**Bit loop** (re-entry point just below "TOF SUAB-FHI ..."; the return line runs up the right side of the left column with two up-arrows). Parallel items:
- "INCREASE BAAB BY 1 54.12.01"
- "DECREASE RFL BY 1 54.32.01"
- "CONVERT BIN TO DEC SIGNAL TO PAU 56.31.20"
- ◇ "RFL CARRY": YES → three parallel boxes: "GATE 1 BIT FROM AB TO F98 56.31.20", "ACCUMULATE AB RESIDUE 56.26.10", and "ENABLE 1 BIT RESIDUE GEN 56.26.00 53.52.22". No NO exit is drawn.

All of these join a bus → ◇ "EOC1":
- NO → loop line → back to the bit-loop entry.
- YES → "RESET AB REG 56.24.40" → ◇ "EOC2":
  - NO → loop line → back to the bit-loop entry.
  - YES → "TOF AB-FHI TON SUF-ABOS 56.13.10 56.13.15". A line runs along the bottom and up the far right to the top of the right column.

#### Right column (e267_1, e267_2, e267_3, e267_r)
**First step.** The entry arrow comes in at the top. Parallel items:
- "LOAD BAAB WITH OS-barØØ 54.15.02" (OS overbarred, followed by "ØØ")
- "SET SFT CIL TO R8 56.32.01 56.33.10" [sic, "SFT CIL"; cf. "SHFT CTL" elsewhere]
- "KILL CDSM 56.13.15"
- "GATE F90-97 TO CD PREOR 56.13.15"
- "RESET AB REG 56.24.40"
- "IF F1 = 1 TON PF ADD 56.51.20"
- "TON AB CUTOFF 56.21.11"
- "TOF CD CUTOFF 56.21.21"
- "TOF E0C1 E0C2 54.38.03"
- "TOF CLOSE CD 56.21.31"

Callouts:
- "THESE LEVELS UP UNTIL SIR": two pointer lines, to KILL CDSM and to GATE F90-97 TO CD PREOR.
- "DISABLES BYTE SIZE GATING": points to TOF CLOSE CD.

Then ◇ "F2-97 = Ø":
- YES → "TOF SU F-ABOS TON SIR 56.11.16". No further exit is drawn.
- NO → "TOF SU F-ABOS TON F-ABOS 56.13.15" → byte loop.

**Byte loop** (re-entry arrow on its top bus, fed from the F = Ø NO exit). Parallel items:
- "GATE F90-97 TO ADDER VIA CD T/C 56.13.15" and "GATE TO ADDER FROM AB 56.21.12", both → ◇ "E0A2":
  - YES → "ENABLE CD PF CKR 56.51.20"
  - NO → "PERFORM ADD AND WRITE INTO AB"
- "LATCH F SHIFTED R8 56.33.00"
- "REDUCE BAAB BY 8 54.12.01"
- "ACCUMULATE CD RESIDUE 56.26.10"
- "DISABLE E0C1 TON DUE TO RFL CARRY 54.38.01"

All of these join a bus → ◇ "F = Ø":
- NO → back to the byte-loop top (loop).
- YES → "TOF F-ABOS TON SIR 56.11.16" → end step.

**End (SIR) step.** Parallel items:
- "UPDATE AB RES TO A CKR 56.41.01"
- "BAAB • BACD TO 10 54.15.02, 54.25.02"
- "INDS TO IND REG 56.52.04"
- "SIR SIG TO LA • PAU 56.42.00"
- "RESET CTL TRIGS 56.14.10"
- ◇ "CVAD": NO → "COMPARE AB AND CD RES IN SAU 56.26.10 59.06.04". YES → ◇ "PF": NO → "COMPARE AB AND CD RES IN SAU"; YES → line down to the bus (skips the compare).

All of these join a bus → "TOF SIR 56.16.00".

#### Answers (Fig 3.11.13)
- Cycle count: NOT PRINTED.
- Stepping:
  - The first loop steps ONE BIT per pass: "INCREASE BAAB BY 1", "DECREASE RFL BY 1", "GATE 1 BIT FROM AB TO F98".
  - The second loop steps ONE BYTE per pass: "REDUCE BAAB BY 8", "LATCH F SHIFTED R8".
  - DERIVED per-iteration box count: bit loop = 1 level of parallel boxes + EOC1 test; byte loop = 1 level + F = Ø test.
- Field-length counter: RFL is loaded with "107 HOM ØØØ" (CVAD YES) or "59 HOM ØØØ" (CVAD NO); these constants are printed. DERIVED: CVAD = the Double form; the constants suggest 108 vs 60 bit positions.
- Decimal/binary: "CONVERT BIN TO DEC SIGNAL TO PAU" — **the PAU is signalled during the SAU's binary convert.** "SIR SIG TO LA • PAU" also appears at the end.
- Signs: SIGNED → "GATE NSM TO SAB" vs "GATE NSM [?] SAB TO SAB".
- Checking: AB/CD residue accumulation, then "COMPARE AB AND CD RES IN SAU" (skipped when CVAD and PF).
- Recomplement: none.
- Logical connective: none.
- Second multiplier: none.
- D register: none.

---------------------------------------------------------------------------------------------------

#### Fig 3.11.14 — "FIGURE 3.11.14. DECIMAL CONVERT AND DECIMAL CONVERT DOUBLE"

- PDF page 268, fold-out.
- Running head: "M3-04-3" / "SAU FLOW DIAGRAMS".
- Foot: date "1/1/63", page "11-27/11-28". (f268_foot.png)
- FLOW DIAGRAM. **Cycle count NOT PRINTED.** No clock numbers, A/B pulses or timing.
- Tiles: f268_L1..L7.png (left column), f268_R1..R4.png (right column); zoom z268_nsm.png.

#### Left column
**Start-up** (f268_L1, f268_L2). Entry: "DECODED VFL INST", "LA START", "PAU NOT OPER, SAU NOT OPER". These feed three parallel boxes:
- "TON VFL OP 56.16.00"
- "TON HK 56.16.00"
- "LOAD SAU EXEC REG 55.20.-"

Then a bus (re-entry arrowhead at its left) with parallel items:
- "LOAD BACD WITH BAER-1 54.21.01"
- "LOAD BAAB WITH OS00-bar 54.11.01" (overbar over "OS00")
- "LOAD RFL WITH FLER- BSER 54.32.-"
- "RESET AB • CD RES REGS 56.26.10"
- ◇ "L A GO": YES → "RESET SRCD 54.60.06" → lower bus. No NO exit is drawn.
- ◇ "REJECT": YES → "TON RESET ONLY 56.14.00" → rounded box "GENERATE INST RESET PORTION OF SIR 56.14.10".

The lower bus feeds ◇ "L A GO":
- NO → back to the top bus (wait loop).
- YES → "TOF H K TON SU AB-FHI 56.16.00 56.13.10".

**Set-up step** (f268_L3, f268_L4). Parallel items on the bus:
- "RESET PAU F REG 56.33.00"
- "LOAD BAAB WITH HOM 011 54.15.01 54.15.02"
- '"A" INPUT TO RFL = OS00-bar' and '"B" INPUT TO RFL= HOM 011-bar' (overbars over "OS00" and "HOM 011"), both → "ADDER OUT INTO RFL"
- ◇ "SIGNED":
  - NO → "GATE NSM TO SRAB 56.25.02" [printed "SRAB"]
  - YES → "GATE NSM [glyph] SAB TO SAB 56.25.02". The glyph is ILLEGIBLE: a blotted symbol, the same mark as on Fig 3.11.13, possibly an exclusive-OR sign (z268_nsm.png).

All join a bus → "TOF SU AB-FHI TON AB-FHI 56.13.10".

**Digit loop** (f268_L5, f268_L6, f268_L7). The re-entry arrow is on the loop's top bus, fed by the return line on the far right. Parallel items:
- "CONVERT DEC TO BIN SIGNAL TO PAU 56.31.20"
- "INCREASE BAAB BY 4 54.12.01"
- "DECREASE RFL BY 4 54.32.01"
- "LATCH F REG 56.33.00"
- ◇ "RFL CARRY": YES → "GATE 4 BITS FROM AB TO F98-101 56.31.20" and "ACCUMULATE AB RESIDUE 56.26.10". No NO exit is drawn.
- ◇ "CVAD":
  - NO → ◇ "1 IN F2 - F49": YES → "TON PF ADD 56.51.20". No NO exit is drawn.
  - YES → ◇ "F1=1": YES → "TON PF ADD 56.51.20". No NO exit is drawn.

All join a bus → ◇ "EOC1":
- NO → loop line → back to the digit-loop top.
- YES → "RESET AB REG 56.24.40" → ◇ "EOC 2":
  - NO → loop line → back to the digit-loop top.
  - YES → (A).

#### Right column, from (A) (f268_R1, f268_R2, f268_R3, f268_R4)
1. ◇ "CVAD": NO → "SET SHFT CTL TO R1 56.33.10"; YES → "SET SHFT CTL TO R0 56.33.10". Both → "TOF AB-FHI TON F--AB+LA1 56.13.10 56.13.20".
2. That box feeds a bus with two parallel items:
   - ◇ "CVAD":
     - NO → "F50-97 (SHFTR 51-98) TO ACIB 12-59 56.31.00"
     - YES → "F2-97 TO ACIB 12-107 56.31.00"
     - Both → "ACOB 12-59 TO AB12-59 56.31.00".
   - "XFER AB RES TO A CKR 56.41.10", which rejoins below ACOB→AB.
3. ◇ "CVAD":
   - NO → "TOF F--AB+LA1 TON SIR 56.13.20 56.11.16".
   - YES → "TOF F--AB+LA1 TON F--AB+LA2 56.13.20" → "ACOB + 0 AB60 - 107" (no ALD printed) → "TOF F--AB+LA2 TON SIR 56.13.20 56.11.16".
4. **SIR step.** Parallel items:
   - "LOAD BAAB TO 10 54.15.02"
   - "LOAD BACD TO 10 54.25.02"
   - "RESET CTL TRIGS" (no ALD printed)
   - "SIR SIGNAL TO PAU • L A 56.42.00"
   - ◇ "PF ADD ON": YES → "TON PF IND 56.52.04" and "SUPPRESS RESIDUE CK 56.41.01". No NO exit is drawn.
   - "GATE INDS TO REG 56.41.01"
   - All join a bus → "TOF SIR 56.16.00".

#### Answers (Fig 3.11.14)
- Cycle count: NOT PRINTED.
- Stepping: ONE DECIMAL DIGIT (4 bits) per pass — "INCREASE BAAB BY 4", "DECREASE RFL BY 4", "GATE 4 BITS FROM AB TO F98-101". The loop ends on EOC1 then EOC2. DERIVED: one level of parallel boxes plus the EOC1 test per pass.
- **The PAU does the conversion arithmetic.** The SAU signals "CONVERT DEC TO BIN SIGNAL TO PAU" and feeds 4-bit digits into F98-101. At the end the result passes through the PAU adder path:
  - "F50-97 (SHFTR 51-98) TO ACIB 12-59" (single) or "F2-97 TO ACIB 12-107" (double)
  - "ACOB 12-59 TO AB12-59"
  - "ACOB + 0 AB60 - 107" (double only)
  - Register-length evidence: F 2-97 / F 50-97 into ACIB 12-59 or 12-107. The shifter path "SHFTR 51-98". AB 12-59 and AB 60-107. RFL initialised from the "A"/"B" adder inputs OS00-bar and HOM 011-bar.
- Double vs single: CVAD selects shift control R0 or R1, the F field (2-97 vs 50-97), one or two LA transfers (F--AB+LA1, then F--AB+LA2), and the "TON PF ADD" test, "1 IN F2 - F49" (CVAD NO) vs "F1=1" (CVAD YES). PF is not expanded anywhere on these pages.
- Signs: SIGNED → "GATE NSM TO SRAB" vs "GATE NSM [?] SAB TO SAB".
- Recomplement: none.
- Early end: none (the loop runs to EOC1/EOC2).
- Logical connective: none.
- Second multiplier: none.
- D register: none.

### Appendix D

#### R23-9732 (7101 CPU CE manual, Jan 1963) — SAU flow diagrams, Figs 3.11.2 – 3.11.7 (transcription set D)

Source: 300 dpi renders [scratch, deleted]/pdfNNN-NNN.png. Tiles in
[scratch, deleted]/tD/.
Tile naming: `tPPP_X_Y.png` = 1300x1200 crop at (X,Y) of PDF page PPP; `xPPP_*.png` = extra targeted crops.
Conventions: labels quoted VERBATIM in capitals; a printed overbar is written as a `-bar` suffix (e.g. `OS-bar`). ALD numbers are given in parentheses.
"Bus" = a horizontal line with several boxes hanging from it (parallel actions, joined by a lower line).
Anything that is my reading of the wiring rather than printed text is marked DERIVED.

---

#### Figure 3.11.2 — "FIGURE 3.11.2. VFL ADD 1 TO MEMORY"

- PDF page 256; page header "M3-04-3" / "SAU FLOW DIAGRAMS"; foot "1/1/63" (issue date) and "11-3/11-4".
- Tiles: t256_300_200, t256_1500_200, t256_300_1150, t256_300_2100, t256_1500_1150, t256_1500_2100,
  t256_2700_200, t256_2700_1150, t256_2700_2100, t256_3800_200, t256_3800_1150, t256_3800_2100, x256_a, x256_b.
- **Timing: cycle count NOT PRINTED.** No clock, A/B pulse or cycle number anywhere on the sheet. The only
  "timing" words are trigger names (PL 1, PL 2, "1ST CYCLE", HK, HSB, SUR, SIR, RECOMP, EOC 1/EOC 2).
- No NOTES block printed on this sheet.
- No PAU hand-off and no multiplier appear on this sheet.

#### A. Entry and set-up (t256_300_200, t256_1500_200, t256_300_1150)
Entry condition text (4 lines, no box): "DECODED VFL OP / SAU NOT OPER / PAU NOT OPER / LA START".
1. Three boxes in parallel: "SET VFL OP 56.16.00"; "TON HK 56.16.00"; "LOAD SAU EXEC REQ" (no ALD printed).
2. Set-up bus (all in parallel, joined below):
   - "TON AB CUT OFF 56.21.11"
   - diamond "BAER = 0": NO → "LOAD BACD TO BAER - 1 54.21.01"; YES → "LOAD BACD TO 64-1 54.21.01"
   - diamond "NSM = 1": NO → "TON LIKE SIGNS TRIG 56.15.01"; YES → "TOF LIKE SIGNS TRIG 56.15.01" →
     diamond "SIGNED": YES → join; NO → "TON AB COMP 56.21.11"
   - diamond "BINARY": YES → "LOAD BAAB TO OS-bar 54.12. -"; NO → "LOAD BAAB TO OS-bar 2 LO ORDER BITS= 0"
     (no ALD printed on the NO box)
   - diamond "SIGNED": YES → "LOAD RFL TO FLER-B.S. 54.32. -"; NO → diamond "BINARY": NO → same
     "LOAD RFL TO FLER-B.S." box; YES → "LOAD RFL TO FLER-8 54.32. -"
3. Join → diamond "LA GO": NO → line returns up to the set-up bus (the vertical from TON HK)
   — a WAIT LOOP until LA GO (DERIVED from the wiring). YES → three parallel items:
   - diamond "RFL CARRY": NO → "TON EOC 1 54.38.01". (Only the NO exit is drawn; no YES exit printed.)
   - "TOF HK 56.16.00"
   - diamond "SIGNED" (the main path).
4. "SIGNED": NO → long line to "TON PL 1 56.11.06" (section C). YES → section B.

#### B. Signed: sign-byte cycle (HSB) (t256_300_1150, t256_300_2100, t256_1500_1150)
5. "TON HSB 56.11.00" → parallel bus:
   - "READ OUT CD SIGN BYTE AT BACD PUT S & FLAGS IN SRCD 54.60.06" → diamond "SCD = 1":
     YES → "INVERT LIKE SIGNS TRIG 56.15.01"; NO → join → diamond "LIKE SIGNS": YES → join;
     NO → "TON AB COMP 56.21.11"
   - "REDUCE BACD BY BSER 54.22.02"
   - diamond "BINARY": NO → "REDUCE RFL BY BSER 54.32.01"; YES → "REDUCE RFL BY 8 54.32.01"
6. Join → "TOF HSB 56.11.00" (hangs off the line) and → diamond "EOC 1":
   - NO → joins the SIGNED-NO line → "TON PL 1" (section C).
   - YES → diamond "LIKE SIGNS": NO → "TON SUR 56.11. -" (ALD printed incomplete as "56.11. -");
     YES → "TON SIR 56.11.16" → line to "NORMAL SIR CYCLE" (section F).
   (i.e. a field that is only the sign byte ends here; DERIVED.)

#### C. Main add loop, PL 1 / PL 2 (t256_2700_200, t256_2700_1150, x256_b, x256_a)
7. "TON PL 1 56.11.06" → loop-entry bus (the loop returns to this bus, below the TON PL 1 box). In parallel:
   - diamond "AB CUT OFF": YES → diamond "AB COMP": YES → diamond "BINARY": NO → "GATE 9's TO ADDER FROM
     AB 56.21.12"; YES → "GATE 1's TO ADDER FROM AB 56.21.12" (neither box has an output line drawn).
     "AB COMP" NO → "GATE O'S TO ADDER FROM AB 56.21.12" → diamond "1ST CYCLE".
     (No NO exit is drawn on "AB CUT OFF".)
   - "GATE CD BYTE TRUE TO ADDER" (no ALD) → line down, joined by "1ST CYCLE" NO, to the add join.
   - diamond "BINARY": YES → "REDUCE RFL BACD BY 8"; NO → "REDUCE BACD & RFL BY BSER" (no ALDs) → join
     enters below the add box (see 9).
8. "1ST CYCLE": NO → join. YES, annotated "(PL1·PL2-bar)" → "TON PL 2 56.11.06" → join; and from the YES
   junction → diamond "LIKE SIGNS": NO → join; YES → "VFL ADDER CARRY IN 56.23.01" → join.
   DERIVED: the "1" of ADD 1 is injected as the adder carry-in on the first cycle (with 0's gated from AB),
   when signs are like. Not stated in words on the sheet.
9. Join → "PERFORM ADD WRITE IN TO CD 56.24.12" → joined by the BINARY/reduce branch → diamond "LIKE SIGNS":
   - NO → diamond "CARRY":
     - NO → diamond "EOC 1": NO → LOOP back to the PL 1 bus (7). YES → "TON SUR 56.11.10" and
       "TOF PL 1·2 56.11.06".
     - YES → diamond "EOC 1": NO → LOOP. YES → "TOF PL 1·2 56.11.06" and "TON SIR 56.11.16".
   - YES → diamond "CARRY":
     - NO → "TOF PL 1·2" and "TON SIR" (no EOC 1 test on this exit: like signs, no carry ends the
       operation early; DERIVED).
     - YES → diamond "EOC 1": NO → LOOP. YES → "TOF PL 1·2" and "TON SIR".
   LOOP: one pass per byte; exit = EOC 1 (or no-carry with like signs). Step size per pass:
   "BY 8" if BINARY, "BY BSER" (byte size) if decimal/not binary — so binary steps 8 bits per pass,
   otherwise one byte of BSER bits (DERIVED from the box labels).
   Boxes per iteration (DERIVED): about 3 serial levels (gate/reduce → PERFORM ADD WRITE → tests);
   no cycle count printed.
10. "TON SIR" → line to "NORMAL SIR CYCLE". "TON SUR 56.11.10" → bus D.

#### D. SUR (unlike signs, no carry at end: result must be recomplemented) (t256_1500_2100, t256_2700_2100, x256_a)
11. Bus (fed from both TON SUR boxes), in parallel:
   - "TOF EOC 1 EOC 2 54.38.03"
   - "LOAD BAAB TO 127 54.15.02"
   - "LOAD RFL TO FLER-8 OR FLER -B.S. 54.32. -"
   - "TOF AB COMP 56.21.11"
   - diamond "SIGNED": NO → "TON CD COMP 56.21.21"; YES → join
12. Join (DERIVED: joined via the wire under TOF EOC 1) → "TOF SUR 56.11.10" and diamond "SIGNED":
   NO → "TON RECOMP·PL 1 56.11.10 56.11.06" → long line to the PL 1 recomplement loop (section E2).
   YES → "TON RECOMP·HSB 56.11.00 56.11.00" → long line to "HSB·RECOMP" (section E1).

#### E1. HSB·RECOMP (sign-byte rewrite) (t256_3800_200)
Entry label printed on the line: "HSB·RECOMP". Parallel bus:
   - "READ OUT CD SIGN REG WRITE NOT SIGN INTO CDSIGN BYTE 56.25.03"
   - diamond "BINARY": NO → "REDUCE RFL BY BSER 54.32.01"; YES → "REDUCE RFL BY 8 54.32.01"
   - "REDUCE BACD BY BSER 54.22.02"
   - "TON CD COMP 56.21.21"
Join → "TOF HSB 56.11.00" (hangs off) and diamond "EOC 1": NO → "TON PL 1 56.11.06" → E2;
YES → "TON SIR 56.11.16" → NORMAL SIR CYCLE.

#### E2. Recomplement loop (PL 1, RECOMP) (t256_3800_200, t256_3800_1150, t256_3800_2100)
Entry: from E1's TON PL 1, from "TON RECOMP·PL 1", and from this loop's own EOC 1 NO. Parallel bus:
   - "READ OUT CD AT BACD COMP & PASS THRU ADDER" (no ALD) → diamond "1ST CYCLE": NO → join;
     YES "(PL 1·PL 2-bar)" → "TON PL 2 56.11.06" → join; and from the YES junction → diamond "LIKE SIGNS":
     NO → "REDUCE BACD & RFL BY BSER" (no ALD) → join; YES → "VFL CARRY TO ADDER 56.23.01" → join
   - diamond "BINARY": NO → "REDUCE BACD & RFL BY BSER 54.32.01"; YES → "REDUCE BACD & RFL BY 8 54.32.01"
Join → hexagon "WRITE RESULT INTO CD 56.24.12" → joined with the BINARY branch → diamond "EOC 1":
   YES → "TON SIR 56.11.16" and "TOF PL 1·2 56.11.06" → "NORMAL SIR CYCLE"; NO → LOOP to the bus.
   Loop exit condition: EOC 1. Per-pass step: 8 (binary) or BSER (DERIVED from labels).

#### F. Exit
"NORMAL SIR CYCLE" (box, t256_3800_2100) — fed by all TON SIR boxes.

#### Registers / counters named on 3.11.2
AB (operand/"A-B" byte gating), CD (memory word being modified; "CD BYTE", "CDSIGN BYTE", "CD COMP"),
BACD, BAAB, BAER, BSER (byte size), RFL, FLER, OS-bar, SRCD, SCD, NSM, ADDER ("VFL ADDER"),
"SIGN REG". Triggers: HK, HSB, PL 1, PL 2, SUR, SIR, RECOMP, EOC 1, EOC 2, AB CUT OFF, AB COMP, CD COMP,
LIKE SIGNS TRIG, LA GO, RFL CARRY.

---

#### Figure 3.11.3 — "FIGURE 3.11.3. VFL LOAD TRANSIT AND SET, DECIMAL MULTIPLY, DECIMAL MULTIPLY AND ADD, DECIMAL DIVIDE, OR LOAD FACTOR"

- PDF page 257; header "M3-04-3" / "SAU FLOW DIAGRAMS"; foot "1/1/63" and "11-5/11-6" (t257_3800_2100).
- On this sheet the ALD number is printed ABOVE each box (at its top-right corner), not inside it.
- Tiles: t257_300_200, t257_300_1150, t257_300_2100, x257_a, t257_1500_1150, t257_1500_2100,
  t257_2700_200, t257_2700_1150, t257_2700_2100, x257_b, x257_c, t257_3800_200, t257_3800_1150, t257_3800_2100.
- **Timing: cycle count NOT PRINTED.** No clock, A/B pulse or cycle count anywhere.
- No NOTES block printed.
- **PAU involvement is explicit on this sheet** (see "PAU" items below): the SAU loads the PAU shift counter,
  resets the PAU F register, shifts bytes into the PAU F register (R4 decimal / R8 binary), later unloads F
  8 bits at a time back through the SAU adder into CD, and finally sends "SI.R. SIGNAL TO PAU AND LA".
  **No multiplier, and no multiply step, is drawn** — although the title covers DECIMAL MULTIPLY / MULTIPLY AND ADD /
  DIVIDE, this sheet only loads the operand into the PAU F register and unloads it to the transit/AC (the SAU side);
  nothing is converted on it. DERIVED.
- **Printed discrepancies on this sheet (reported as drawn):** (i) the missing junction dot in step 3; (ii) the CD-FLO
  shift test in step 8 has the OPPOSITE polarity to its siblings: "SH CTR = 0?" YES → LATCH/shift, whereas "SC = 0" in
  this sheet's own SU F-CD loop (step 10), on 3.11.4 and on 3.11.6 is NO → LATCH/shift.

#### A. Entry and set-up (t257_300_200)
Entry text: "DECODED VFL INSTR / PAU. SAU NOT OPERATING / LA START".
1. Parallel: "TURN ON VFL-OP TRIGGER" (56.16.00); "TURN ON HOUSEKEEPING TRIGGER" (56.16.00);
   "LOAD SAU EXECUTION TRIGGER" (55.10.).
2. Bus (from HOUSEKEEPING), parallel:
   - "LOAD BACD REG WITH BAER -1" (54.22.)
   - "RESET CD SIGN BYTE REG" (54.60.06)
   - diamond "BINARY ?": YES → "LOAD BAAB REG WITH 05-bar" (54.12.00; overbar over "05") → diamond "SIGNED":
     NO → "LOAD RFL REG WITH FLER-8" (54.32); YES → "LOAD RFL REG WITH FLER-BSER" (54.32).
     BINARY NO → "LOAD BAAB REG WITH 0500-bar" (54.12.00 55.20.26; overbar over "0500") → joins into the
     "FLER-BSER" box line.
     Glyph check (z257_baab.png at 300%): the characters are printed as digits — narrow zero, flat-topped 5 — not as the
     round O and S of 3.11.2's "LOAD BAAB TO OS-bar" (z256_baab.png). DERIVED cross-reference, not a reading: the same box
     position on 3.11.2 reads "OS-bar" (binary) / "OS-bar 2 LO ORDER BITS= 0" (not binary), and on 3.11.4/3.11.5 reads
     "NOT OFFSET", so "05-bar"/"0500-bar" may be a drafting rendering of OS-bar (offset complement) rather than numeric
     constants. Treat them as unresolved.
   (No LA GO wait is drawn on this sheet, unlike 3.11.2.)
3. Join → diamond "SIGNED ?":
   - YES → "TURN OFF H.K. TURN ON HSB AND SUCD-FLO" (56.11.00 56.13.00) → B
   - NO → "TURN OFF HK TURN ON SU CD-FLO" (56.13.00) → vertical line straight down to "LOAD CONSTANT OF 59
     INTO BAAB" (see B). The line CROSSES the YES box's right-hand bus with NO junction dot drawn
     (x257_a). As drawn, therefore, the unsigned path skips the PAU shift-counter/LOAD FACTOR boxes, AND the signed
     path skips "LOAD CONSTANT OF 59 INTO BAAB" and "RESET PAU F REGISTER". 3.11.4 and 3.11.6 draw a junction dot at the
     same spot (both paths reach the PAU set-up), so this is probably a drafting omission (DERIVED). Reported as drawn.

#### B. Sign byte + PAU set-up (t257_300_1150, x257_a)
4. From the YES box, left bus (parallel):
   - "READ OUT CD SIGN BYTE AT BACD AND PLACE INTO SCD REG" (54.60.06)
   - "REDUCE BACD BY BSER" (54.22.02)
   - diamond "BINARY ?": NO → "REDUCE RFL BY BSER" (54.32.01); YES → "REDUCE RFL BY 8" (54.32.01)
5. From the YES box, right bus (parallel):
   - diamond "BINARY ?": YES → "LOAD CONSTANT OF 96 INTO PAU SHIFT CTR" (56.33.00) →
     "SET RIGHT 8 INTO SH CTL" (56.32.01 56.33.10). NO → "LOAD CONSTANT OF 92 INTO PAU SHIFT COUNTER"
     (56.32.00) → "SET R4 INTO SHIFT CONTROL" (56.32.01).
   - diamond "LOAD FACTOR": YES → join; NO → "GATE EX REG 12-18 34 TO AOC AND L2C REGS" (56.27.00).
6. Unsigned path: "LOAD CONSTANT OF 59 INTO BAAB" (54.15.01, 02) → "RESET PAU F REGISTER" (56.33.00) → join.
7. All join → "TURN OFF HSB. SU CD-FLO. TURN ON CD-FLO" (56.13.00).

#### C. CD-FLO loop: bytes of the memory operand into PAU F (t257_300_1150, t257_300_2100, t257_1500_1150, t257_1500_2100)
8. Loop bus (entered from 7; loop returns enter it with arrows), parallel:
   - diamond "END OF C": YES → diamond "EOC2 TGR ON": YES → "CUT OFF THE CD BYTE IN TR/CMP UNIT" (56.21.21) → join;
     "NO(EOC1)" → "MASK THE CD BYTE BY RFL" (56.21.32) → into the line below.
     "END OF C" NO → line down to diamond "EOA?"; the MASK box output is wired to that line and also down to
     "WRITE CD BYTE INTO F2-9" (56.31.20) → join. "EOA?": YES → "EXAMINE CD BYTE FOR P.F." (56.51.20) → join; NO → join.
     No arrowheads at this junction, so whether END-OF-C-NO also reaches WRITE CD BYTE is NOT shown; DERIVED that it does.
     On 3.11.6 the same junction carries arrowheads sending both END-OF-C-NO and MASK into EOA 2, with WRITE CD BYTE
     reached only below MASK — a conflict with the DERIVED reading here.
   - diamond "SH CTR = 0?": NO → join; YES → "LATCH F REG· SHFTD R4/R8" (56.31.10 56.33.00) [polarity as printed;
     opposite to the sibling SC = 0 tests, see header] →
     "REDUCE SH CTR BY SH CTL" (56.33.00) → "ACCUMULATE CD RESIDUE" (56.26.10) → join.
   - diamond "BINARY ?": NO → "REDUCE BACD BY BSER" (54.22.01) → "REDUCE RFL BY BSER" (54.32.01) →
     "REDUCE BAAB BY 4" (54.12.01). YES → "REDUCE BACD BY 8" (54.22.01) → "REDUCE RFL BY 8" (54.32.01) →
     "REDUCE BAAB BY 8" (54.12.01) → join.
9. Join → diamond "EOC1": NO → LOOP back to the bus (arrow). YES → diamond "EOA1 OR EOA2 ?":
   NO → LOOP back to the bus (arrow); YES → "TURN OFF CD- FLO. TURN ON SU F-CD" (56.13.05) → D.
   Per-pass step: one CD byte; F register latched shifted R4 (decimal: 4 bits/digit) or R8 (binary: 8 bits);
   BAAB reduced by 4 (decimal) or 8 (binary); BACD and RFL reduced by BSER (decimal) or 8 (binary). DERIVED
   from the labels. Loop exits: EOC1 then EOA1/EOA2.

#### D. SU F-CD loop: finish shifting F (x257_b, t257_2700_200)
10. Entry with arrow. Bus (parallel):
   - "SET BACD TC 127" (54.25.01; printed "TC", presumably TO) → "RESET CD REGISTER" (56.24.40)
   - "LOAD RFL REG WITH CONSTANT OF 60" (54.31.01) → "RESET EOC1 AND EOC2" (54.38.03)
   - "RESET EOA2" (54.18.01)
   - diamond "SC = 0": YES → join; NO → "LATCH F REG SHIFTED R4 OR R8" (56.31.10 56.33.00) →
     "REDUCE SHIFT BY 4 OR 8" (56.33.00) → join
11. Join → diamond "SH CTR = 0": NO → LOOP back to the bus entry (arrow); YES →
    "TURN OFF SU F-CD. TURN ON SC-D 127" (56.13.05). Loop exit: SH CTR = 0. DERIVED: this right-justifies the
    loaded number in F with shift-counter-driven 4- or 8-bit shifts.

#### E. SC-D 127: sign byte into D (t257_2700_200, t257_2700_1150)
12. Parallel:
   - "DEVELOP SIGN BYTE AS IN STORE, USE SCD AND NSM AS SIGN USE ZEROS AS FLAGS" (56.25.03 54.60.05) →
     "WRITE SIGN BYTE INTO D60 -63" (56.24.12)
   - "REDUCE RFL REG BY 8" (54.32.01) → "REDUCE BACD BY 4" (54.22.01)
   - "XFER CD RESIDUE TO A CHECKER" (56.26.10)
13. Join → diamond "ANY 1's IN F1-49 ?" — YES exit annotated "F>48":
   - YES → "SET SHIFT CONTROL TO R8" (56.32.01 56.33.10) → "TURN OFF SC-D 127. TURN ON F-CD" (56.13.05) → F.
   - NO → "SET SHIFT CONTROL TO R1" (56.33.10) → "TURN OFF SC- D127. TURN ON F--AB AND LA1" (56.13.20) → G.

#### F. F-CD loop: high part of F written to CD (D) 8 bits at a time (x257_c, t257_2700_1150, t257_2700_2100)
14. Bus (parallel):
   - "GATE F90-97 TO SAU ADDER VIA AB T/C" (56.13.05; the middle digit of "56.1?.05" is overstruck —
     reads 56.13.05; x257_c) and "GATE ZEROS TO ADDER FROM CD" (56.21.21) → join → diamond "END OF C":
     YES → diamond "EOC2": YES → join; NO → "MASK BY RFL" → into "PERFORM ADD AND WRITE INTO CD" (56.24.12).
     "END OF C" NO → "PERFORM ADD AND WRITE INTO CD" (56.24.12) → join.
   - "REDUCE BACD BY 8" (54.22.01) → "REDUCE RFL BY 8" (54.32.01) → join
   - "LATCH F REG SHIFTED R8" (56.31.10) → join
   - "ACCUMULATE AB RESIDUE" (56.26.10) → join (the loop-return arrow enters the bus at this box)
15. Join → diamond "F1 97 ZEROS": NO → LOOP back (arrow at ACCUMULATE AB RESIDUE). YES →
    "XFER D0-D63 TO ACIB." (56.41.10) and "TURN OFF F-CD TURN ON SI.R" (56.11.16) → join → long line to H.
    Loop exit condition: F bits 1-97 all zero (data-dependent). 8 bits per pass (F90-97, R8). DERIVED.

#### G. F--AB (number fits: no 1's in F1-49) (t257_3800_200)
16. Arrow entry. Parallel: "GATE F50-97 TO ACIB 12-59 VIA R1 SHIFT" (56.31.00) and "GATE D60-63 TO ACIB 60- 63"
    (56.41.10) → join → "LATCH A CHECKER BUS" (56.41.10); and "RESET CD RESIDUE REG" (56.26.10) →
    "TURN ON NZRT IF F = 0" (56.15.05). Join → "TURN OFF F--AB AND LA1. TURN ON SI.R" (56.11.16) → H.

#### H. End (t257_3800_1150)
17. Bus (entered by arrow from F's exit line and from G), parallel:
   - diamond "LOAD FACTOR": YES → join; NO → diamond "BIN": YES → "GATE BTR IND" (56.52.04); NO → "GATE DTR IND" → join
   - "SET BAAB TO 10" (54.15.02) → "RESET CONTROL TRIGGERS"
   - "SET BACD TO 10" (54.25.02) → "SI.R. SIGNAL TO PAU AND LA" (56.42.00)
   - "GATE INDS TO IND REG." (56.52.04) → "COMPARE A.B AND CD RESIDUES" (56.26.10 59.06.04)
18. Join → "TURN OFF SIR AND VFL OP TGRS" (56.16.00). End.

#### Registers / widths named on 3.11.3
PAU F register bits "F2-9", "F1-49", "F50-97", "F90-97", "F1 97" (so F is at least 97 bits wide as numbered here);
ACIB "12-59", "60- 63"; D "D0-D63", "D60-63"; PAU SHIFT CTR loaded with 96 (binary) or 92 (decimal); BAAB values
59, 10 (plus the unresolved "05-bar"/"0500-bar", see step 2); BACD constants 127, 10; RFL constant 60; "EX REG 12-18 34"; AOC, L2C REGS; SCD, NSM;
TR/CMP UNIT; A CHECKER; residues (CD RESIDUE, AB RESIDUE). Triggers: HSB, SUCD-FLO, SU CD-FLO, CD-FLO, SU F-CD,
SC-D 127, F-CD, F--AB, LA1, SI.R, NZRT, EOC1, EOC2, EOA, EOA1, EOA2, BTR / DTR IND.

---

#### Figure 3.11.4 — "FIGURE 3.11.4. VFL LOAD CONVERTED DECIMAL TO BINARY"

- PDF page 258; header "M3-04-3" / "SAU FLOW DIAGRAMS"; foot "1/1/63" and "11-7/11-8" (f258.png;
  read from the footer crop).
- ALD numbers printed above each box. Three columns, joined by long lines with arrowheads.
- Tiles: c258_850_250, c258_1500_250, c258_850_1150, c258_1500_1150, c258_850_2050, c258_1500_2050,
  c258_2500_250, c258_2500_1150, c258_2500_2050, c258_3600_250, c258_4000_250, c258_3600_1150, c258_4000_1150,
  c258_3600_2050, c258_4000_2050.
- **Timing: cycle count NOT PRINTED.** The only timing words: "LATCH F REG EACH CYCLE" (a box label, no number).
- No NOTES block printed.
- **PAU hand-off printed explicitly: "CONVERT DEC TO BIN SIGNAL TO PAU" (56.31.20)**, once per 4-bit digit, after
  "GATE 4 BIT BYTE FROM AB TO F98-101". The SAU feeds digits; the PAU does the conversion. No multiplier is named
  on the sheet (the x10 step is not drawn; DERIVED that it lives in the PAU).

#### A. Entry and set-up (c258_850_250, c258_1500_250)
Entry text: "DECODED VFL INSTRUCTION / LA START" | "SAU NOT OPERATING / PAU NOT OPERATING".
1. Parallel: "TURN ON VFL OP TRIGGER" (56.16.00); "TURN ON HOUSEKEEP TRIGGER" (56.16.00);
   "LOAD SAU EXECUTION REGISTER" (55.20.).
2. Bus (parallel):
   - "LOAD BACD REG WITH BAER - 1" (54.22.) → "RESET CD SIGN BYTE REG" (54.60.06)
   - "LOAD BAAB REG WITH NOT OFFSET" (54.12.00) → "LOAD SAB POS 4 WITH NEG SIGN MOD" (56.25.02)
   - "RESET AB REGISTER" (56.24.40) → "RESET AB & CD RESIDUES" (56.26.10)
   - "LOAD RFL REG WITH FLER-BSER" (56.32.)
   - "RESET SIGN OF AB REGISTER POS 5-7" (56.25.02)
3. Join → diamond "SIGNED ?":
   - YES → "TURN OFF HK TURN ON HSB AND SU CD-FLO" (56.11.00 56.13.00) → (a) left bus, and (b) a line that JOINS
     (junction dot drawn) the NO path's bus.
   - NO → "TURN OFF HK TURN ON SU CD-FLO" (56.13.00) → bus (b).
4. (a) Signed-only bus: "READ OUT CD SIGN BYTE AT BACD AND PLACE INTO SCD REG" (54.60.06) →
   "GATE SCD NEG SIGN MOD TO SIGN OF AB REG"; and "REDUCE BACD BY BSER" (54.22.02) → "REDUCE RFL BY BSER" (54.32.01).
   (b) PAU set-up bus: "LOAD CONSTANT OF 59 INTO BAAB REG" (54.15.01, 02) → "SET PAU SHIFT CONTROL TO RIGHT 4"
   (56.32.01); "LOAD CONSTANT OF 92 INTO PAU SHIFT COUNTER" (56.32.00) → "RESET PAU F REGISTER" (56.33.00).
5. All join → "TURN OFF HSB + SUCD-FLO TURN ON CD-FLO" (56.13.10).
   (No BINARY test anywhere on this sheet: the source field is decimal; every step is 4 bits.)

#### B. CD-FLO loop: decimal digits of the memory field into PAU F (c258_850_1150, c258_1500_1150, c258_850_2050, c258_1500_2050)
6. Loop bus (arrow), parallel:
   - diamond "END OF C1": YES → diamond "E0C2": YES → "CUT OFF THE CD BYTE IN TR/CMP UNIT" (56.21.21) → join;
     NO → "MASK CD BYTE BY RFL" (56.21.32) → junction with the END-OF-C1-NO line (no arrowheads; DERIVED that both reach WRITE) → "WRITE CD BYTE INTO F6-9" (56.31.20)
     → join, and → diamond "E0A2 ON": YES → "EXAMINE CD BYTE FOR P.F." (56.51.20) → join; NO → join.
   - "REDUCE BACD BY BSER" (54.22.01) → "REDUCE RFL BY BSR" (54.32.01; printed "BSR") → "REDUCE BAAB BY 4" (54.12.01)
   - diamond "SC = 0": YES → join; NO → "LATCH F SHIFTED RIGHT 4" (56.31.10 56.33.00) →
     "REDUCE SHIFT COUNTER BY 4" (56.33.00) → "ACCUMULATE CD RESIDUE" (56.26.10) → join
7. Join → diamond "E0C1": NO → LOOP (arrow). YES → diamond "SN CTR = 0" (printed "SN"; presumably the shift
   counter, not confirmed): NO → LOOP (joins the E0C1-NO return); YES → long line to C.
   Per pass: one CD byte; "WRITE CD BYTE INTO F6-9" = 4 bits into F; F latched shifted RIGHT 4; BAAB reduced by 4.
   Loop exit: E0C1 and SN CTR = 0. ("E0C"/"E0A" printed with a zero-like O; transcribed as printed.)

#### C. F--AB: F into the AB register via ACIB (c258_2500_250)
8. Arrow → "TURN OFF CD-FLO.TURN ON F--AB + LA1" (56.13.20) → parallel:
   - "GATE F2-97 TO ACIB 12-107" (56.31.00) → "ACOB 12-59 LATCHED INTO A12-59" (56.31.00)
   - "RESET E0C1 & E0C2 TGRS" (56.38.03) → "RESET E0A2 TGR" (54.18.01)
   - "SIGNAL ACK TO NOT CHECK RESIDUE" (56.41.10)
9. Join → "TURN OFF F--AB +LA1. TURN ON F--AB + LA2" (56.13.20) → "LATCH ACOB INTO AB60-107 (NO SAU ACTION)"
   (no ALD) → "TURN OFF F--AB +LA2. TURN ON SU AB-FHI" (56.13.10).
   DERIVED: the 96-bit F content goes to AB in two LA transfers (bits 12-59, then 60-107).

#### D. SU AB-FHI set-up (c258_2500_1150)
10. Parallel: "RESET PAU F REGISTER" (56.33.00); "LOAD BAAB WITH HOM 011" (54.15.01, 02);
    "GATE CONSTANT OF 107 AS A INPUT TO RFL" (54.31.01) and "GATE HOM 011-bar AS B INPUT TO REL ADDER" (54.32.01;
    overbar over "HOM 011") → join → "SET ADDER OUTPUT INTO RFL REG" (54.35.01).
11. Join → "TURN OFF SU AB-FHI TURN ON AB-FHI" (56.13.10).

#### E. AB-FHI loop: digit by digit into the PAU for conversion (c258_2500_1150, c258_2500_2050)
12. Loop bus (return arrow enters at the right), parallel:
    - "GATE 4 BIT BYTE FROM AB TO F98-101" (56.31.20) → "CONVERT DEC TO BIN SIGNAL TO PAU" (56.31.20)
    - "INCREASE BAAB BY 4" (54.12.01) → "DECREASE RFL BY 4" (54.32.01)
    - "LATCH F REG EACH CYCLE" (56.33.00) → "ACCUMULATE AB RESIDUE" (56.26.10)
13. Join → diamond "EOC2": NO → LOOP (arrow); YES → "TURN OFF AB-FHI TURN ON SU F-ABOS" (56.13.15) → long line to F.
    Per pass: 4 bits (one decimal digit), one PAU convert signal. Loop exit: EOC2. Boxes per iteration
    (DERIVED): 2 serial levels + the EOC2 test.

#### F. SU F-ABOS set-up and F-ABOS loop: binary result out of F into AB 8 bits at a time (c258_3600_250, c258_4000_250, c258_3600_1150, c258_4000_1150)
14. Arrow → bus (parallel):
    - "LOAD BAAB REG WITH NOT OFFSET" (54.12.00) → "RESET AB REGISTER" (56.24.40)
    - "RESET EOC1 AND EOC2 TRIGGERS" (54.38.03) → "SET SHIFT CONTROL TO RIGHT EIGHT" (56.32.01 56.33.10)
    - "TURN ON AB CUTOFF TRIGGER" (56.21.11) → "KILL CD SWITCH MATRIX OUTPUT" (56.13.15)
    - "GATE F90-97 TO CD SM" LEVEL — printed with quote marks round GATE ... SM (56.13.15) →
      "COMPARE AB AND CD RESIDUE REGISTERS" (56.26.10) → "RESET CD RESIDUE REGISTER" (56.26.10)
15. Join → diamond "F1-97 =ZEROS": YES → "TURN OFF SU F- ABOS. TURN ON SI.R" (56.11.15) → G.
    NO → "TURN OFF SU F-ABOS. TURN ON F-ABOS" (56.13.15) → loop bus (parallel):
    - "GATE F90-97 TO ADDER VIA CD TR/CMP" (56.13.15) and "GATE ZEROS TO ADDER FROM AB" (56.21.12) → join →
      diamond "END OF A": YES → "ENABLE CD PARTIAL FIELD CHECKER" (56.51.20); NO → "PERFORM ADD & WRITE INTO AB" (56.24.11)
    - "LATCH F REG SHIFTED RIGHT 8" (56.33.00) → "ACCUMULATE CD RESIDUE" (56.26.10)
    - "REDUCE BAAB BY 8" (54.12.01) (loop-return arrow enters here)
16. Join → diamond "F1-97 = 0": NO → LOOP (arrow); YES → "TURN OFF F-ABOS TURN ON SI.R" (56.11.15) → G.
    Per pass 8 bits (F90-97, shift right 8). Loop exit: F1-97 = 0 (data-dependent).

#### G. End (c258_3600_2050, c258_4000_2050)
17. Bus (also entered by arrow from the F1-97 =ZEROS YES path), parallel:
    - "UPDATE AB RESIDUE SIGNAL TO A CHECKER" (56.41.01) → "RESET CONTROL TRIGGERS"
    - "SET BAAB TO 10" (54.15.02) → "SI.R SIGNAL TO PAU & L.A." (56.42.00)
    - "SET BACD TO 10" (54.25.02) → "COMPARE AB & CD RES REGS" (59.06.04)
    - "GATE INDS TO IND REG" (56.52.04)
18. Join → "TURN OFF SI R & VFL OP TGRS" (56.16.00).

#### Registers / widths on 3.11.4
F bits "F6-9", "F2-97", "F98-101", "F90-97", "F1-97"; ACIB "12-107"; ACOB "12-59"; "A12-59"; "AB60-107";
PAU SHIFT COUNTER 92; BAAB 59, "HOM 011", 10, NOT OFFSET; RFL constant 107; "REL ADDER"; SAB POS 4; AB sign POS 5-7.

---

#### Figure 3.11.5 — "FIGURE 3.11.5. VFL LOAD TRANSIT CONVERTED BINARY TO DECIMAL"

- PDF page 259; header "M3-04-3" / "SAU FLOW DIAGRAMS"; foot "1/1/63" and "11-9/11-10" (c259_3700_2050).
- ALD numbers printed above each box. Three columns.
- Tiles: c259_950_250, c259_950_1150, c259_950_2050, c259_2350_250, c259_3000_250, c259_2350_1150,
  c259_3000_1150, c259_2350_2050, c259_3000_2050, c259_3700_250, c259_3700_1150, c259_3700_2050, z259_n2rt (zoom).
- **Timing: cycle count NOT PRINTED.** Only "LATCH F REG EACH CYCLE" (label, no number).
- No NOTES block printed.
- **PAU hand-off printed: "CONVERT BIN TO DECIMAL SIGNAL TO PAU" (56.31.20)**, once per pass of a loop that moves
  ONE BIT per pass: "TRANSFER 1 BIT BYTE FROM CD TO F98" (56.26.00), "INCREASE BACD BY 1", "DECREASE RFL BY 1",
  PAU shift control "LEFT 1". So binary-to-decimal conversion is fed to the PAU bit-serially, 1 bit per step
  (DERIVED from the labels; contrast 3.11.4, where decimal-to-binary is fed 4 bits per step). No multiplier named.

#### A. Entry and set-up (c259_950_250)
Entry text: "DECODED VFL INSTRUCTION / PAU. SAU NOT OPERATING / LA START".
1. Parallel: "TURN ON VFL OF TRIGGER" (56.16.00; printed "OF", presumably OP); "TURN ON HOUSEKEEPING TRIGGER"
   (56.16.00); "LOAD SAU EXECUTION REGISTER" (55.10.).
2. Bus (parallel): "LOAD BAAB TO NOT OFFSET" (54.12.00); "LOAD BACD TO BAER-1" (54.22.); "RESET CD SIGN BYTE REG"
   (54.60.06); diamond "SIGNED ?": YES → "LOAD RFL TO FLER - BSER" (54.32); NO → "LOAD RFL TO FLER-1" (54.32).
3. Join → diamond "SIGNED ?":
   - YES → "TURN OFF H.K. TURN ON HSB" (56.11.00) → parallel: "READ OUT CD SIGN BYTE AT BACD PLACE SIGN AND FLAGS
     INTO SCD REG." (54.60.06); "REDUCE BACD REG BY BSER" (54.22.02); "REDUCE RFL REG BY ONE" (54.32.01) → join →
     "TURN OFF HSB TURN ON SU CD-FHI" (56.13.10) → bus B.
   - NO → "TURN OFF HK TURN ON SUCD-FHI" (56.13.10) → long line joining bus B.

#### B. SU CD-FHI set-up (c259_950_1150)
4. Parallel: "REDUCE BACD BY RFL" (54.22.02); "RESET. PAU F REGISTER" (56.33.00); "SET SHIFT CONTROL TO LEFT 1"
   (56.32.01); "BLOCK TURN ON OF EOC2" (54.38.03).
5. Join → diamond "END OF C2 TGR ON?": NO → "TURN OFF SUCD-FHI TURN ON CD-FHI" (56.13.10) → C.
   YES → "TURN OFF SU CD-FHI. TURN ON SUF-CD" (56.13.05, read in z259_suf.png)
   → long line to D. (DERIVED: a field with no bits after the sign skips conversion.)

#### C. CD-FHI loop: one bit per pass into the PAU (c259_950_1150, c259_950_2050)
6. Loop bus, parallel:
   - diamond "EOC2 ?": NO → "TRANSFER 1 BIT BYTE FROM CD TO F98" (56.26.00) → "ACCUMULATE CD RESIDUE" (56.26.10) → join;
     YES → join (skips the transfer)
   - "CONVERT BIN TO DECIMAL SIGNAL TO PAU" (56.31.20) → "LATCH F REG EACH CYCLE" (56.33.00)
   - "INCREASE BACD BY 1" (54.22.01) → "DECREASE RFL BY 1" (54.32.01)
7. Join → diamond "EOC2": NO → LOOP; YES → "TURN OFF CD-FHI TURN ON SUF-CD" (56.13.05) → long line to D.
   Per pass: 1 bit. Loop exit: EOC2. Boxes per pass (DERIVED): 2 serial levels + the EOC2 test.

#### D. SUF-CD set-up (no loop on this sheet) (c259_2350_250, c259_3000_250)
8. Bus (parallel): "SET BACD LEG TO 127" (54.25.01; printed "LEG", presumably REG); "RESET CD REGISTER" (56.24.40);
   "SET RFL TO CONSTANT OF 60" (54.31.01); "RESET EOC1 AND EOC2" (54.38.03); "RESET EOA2" (54.18.01).
9. Join → "TURN OFF SUF-CD TURN ON SC-D127" (56.13.05). (Unlike 3.11.3 there is no SC = 0 / SH CTR shift loop here.)

#### E. SC-D127: sign byte into D (c259_2350_250)
10. Parallel: "DEVELOP SIGN BYTE AS IN STORE USING SCD AND NS MOD AS SIGN. USE ZEROS AS FLAG BITS" (56.25.03 54.60.05)
    → "WRITE SIGN BYTE INTO D 60-63" (56.24.12); "REDUCE BACD REG BY 4" (54.22.02) → "REDUCE RFL REG BY 8" (54.32.01);
    "TRANSFER CD RESIDUE TO ACKR" (56.26.10).
11. Join → diamond "ONE BIT IN F1-49 ?":
    - "YES F>48" → "SET SHIFT CONTROL TO RIGHT 8" (56.32.01 56.33.10) → "TURN OFF SC- D127. TURN ON F-CD" (56.13.05) → F.
    - "NO F>48-bar" (overbar over "F>48") → "SET SHIFT CONTROL TO R1" (56.33.10) → "TURN OFF SC-D127. TURN ON F--AB+LA1"
      (56.13.20) → G.

#### F. F-CD loop: result written to memory 8 bits per pass (c259_2350_1150, c259_3000_1150, c259_2350_2050, c259_3000_2050)
12. Bus, parallel:
    - "GATE F90- 97 TO SAU ADDER VIA AB T/C" (56.13.05) and "GATE ZEROS TO ADDER FROM CD" (56.21.21) → join →
      diamond "END OFC": YES → diamond "EOC2": YES → diamond "F = 0": YES → join; NO → "SET PARTIAL FIELD ADD" (56.51.20)
      → join. "EOC2" NO → "MASK BYTE FROM F BY RFL" → diamond "1 IN F90-93": YES → "SET PARTIAL FIELD ADD"; NO → join;
      and "MASK BYTE..." → "PERFORM ADD AND WRITE INTO CD" (56.24.12). "END OFC" NO → "PERFORM ADD AND WRITE INTO CD".
    - "REDUCE BACD BY 8" (54.22.01) → "REDUCE RFL BY 8" (54.32.01)
    - "LATCH F SHIFTED RIGHT 8" (56.31.10)
    - "ACCUMULATE AB RESIDUE" (56.26.10)
13. Join → diamond "F1-97 ALL ZEROS": NO → LOOP to the bus. YES → "TRANSFER D0-D63 TO AC1B0-63" (56.41.10) →
    "TURN OFF F-CD. TURN ON SI.R" (56.11.16) → line to H.
    Per pass 8 bits; loop exit F1-97 all zeros (data-dependent).

#### G. F--AB (c259_3700_250)
14. Parallel: "GATE F50-97 TO AC1B 12-59 VIA R1 SHIFT" (56.31.00) and "GATE D60-63 TO AC1B 60-63" (56.41.10) → join →
    "LATCH ACKR BUS" (56.41.10); "RESET CD RESIDUE REGISTER" (56.26.10) → "TURN ON N2RT IF F=0" (56.15.05) — a bar is
    printed above "F=0", between the two text lines (z259_n2rt): it may be an overbar (i.e. NOT F=0) or an underline of
    "RN" in TURN; ILLEGIBLE as to which (z259_n2rt.png). Compare 3.11.3, where "TURN ON NZRT IF F = 0" has no bar.
15. Join → "TURN OFF F--AB+LA1 TURN ON SI.R" (56.11.16) → H.

#### H. End (c259_3700_250, c259_3700_1150)
16. Bus (also entered from F's exit), parallel: "SET BAAB TO 10" (54.15.02) → "RESET CONTROL TGRS"; "SET BACD TO 10"
    (54.25.02) → "SIR SIGNAL TO PAU AND LA" (56.42.00); "GATE INDS TO IND REG" (56.52.04) → "COMPARE AC AND CD RES."
    (56.26.10, 59.06.04).
17. Join → "TURN OFF SIR AND VFL OP TGRS." (56.16.00).

#### Registers / widths on 3.11.5
F bits "F98", "F1-49", "F90-97", "F90-93", "F1-97", "F50-97"; D "D 60-63", "D0-D63"; AC1B "0-63", "12-59", "60-63"
(printed "AC1B"; elsewhere "ACIB"); ACKR; BACD constants 127, 10; RFL constant 60; PAU shift control LEFT 1 / RIGHT 8 / R1.

---

#### Figure 3.11.6 — "FIGURE 3.11.6. VFL LOAD TRANSIT CONVERTED DECIMAL TO BINARY"

- PDF page 260; header "M3-04-3" / "SAU FLOW DIAGRAMS"; foot "1/1/63" and "11-11/11-12" (f260.png).
- ALD numbers printed above (or beside) each box. Three columns.
- Tiles: c260_450_200, c260_1150_200, c260_450_1100, c260_1150_1100, c260_450_2000, c260_1150_2000, c260_2200_200,
  c260_2650_200, c260_2200_1100, c260_2650_1100, c260_2200_2000, c260_2650_2000, c260_3650_200, c260_3950_200,
  c260_3650_1100, c260_3950_1100, c260_3650_2000, c260_3950_2000, f260.
- **Timing: cycle count NOT PRINTED.** Only "LATCH F REG EACH CYCLE" (label).
- **Printed NOTE (verbatim, c260_2650_1100): "NOTE: F-CD & F--CD TWO DIFFERENT TRIGGERS"**
- **PAU hand-off printed: "CONVERT DEC TO BIN SIGNAL TO PAU" (56.31.20)** once per 4-bit step ("TRANSFER 4 BIT BYTE FROM
  C TO F99- 101", "INCREASE BACD BY 4", "DECREASE RFL BY 4"). No multiplier named.
- Structure (DERIVED): load the decimal memory field into PAU F (CD-FLO, as in 3.11.3/3.11.4) → write it as a transit
  word into D/C (F-CD) or via ACIB into C12-59 (F--CD) → read it back 4 bits at a time from C into F98-101 with a PAU
  "convert dec to bin" signal per digit (CD-FHI) → binary result out via ACIB/ACOB (F--AB + LA1).

#### A. Entry and set-up (c260_450_200, c260_1150_200)
Entry text: "DECODED VFL INSTR / LA START / PAU NOT OPERATING / SAU NOT OPERATING".
1. Parallel: "TURN ON VFL OP TRIGGER" (56.16.00); "TURN ON HOUSEKEEPING TRIGGER" (56.16.00); "LOAD SAU EXECUTION
   REGISTER" (55.10.).
2. Bus: "LOAD BACD TO BAER-1" (54.22.-); "LOAD RFL TO FLER BSER" (54.32.-); "LOAD BAAB TO 0500-bar" (54.12.-; overbar
   over "0500"); "RESET CD SIGN BYTE REGISTER" (54.60.06).
3. Join → diamond "SIGNED ?" (both exits drawn with arrowheads):
   - YES → "TURN OFF HOUSE KEEPING - TURN ON HSB AND SU CD-FLO" (56.11.00, 56.13.00) → (a) "READ OUT CD SIGN BYTE AT BACD
     AND PLACE INTO SIGN OF CD REG" (54.60.06); "REDUCE BACD BY BSER" (54.22.02) → "REDUCE RFL BY BSER" (54.32.01);
     and (b) a line joining (junction dot) the NO bus.
   - NO → "TURN OFF HK - TURN ON SU CD-FLO" (56.13.00) → bus (b): "LOAD CONSTANT DF59 INTO BAAB" (54.15.01,02; printed "DF59",
     presumably OF 59) → "SET PAU SHIFT CONTROL TO RIGHT 4" (56.32.01); "LOAD CONSTANT OF 92 INTO PAU SHIFT CTR" (56.13.00)
     → "RESET PAU F REGISTER" (56.33.00).
4. Join → "TURN OFF HSB SU CD-FLO TURN ON CD-FLO" (56.13.05).

#### B. CD-FLO loop: decimal field into PAU F, 4 bits per byte (c260_450_1100, c260_1150_1100, c260_450_2000, c260_1150_2000)
5. Loop bus (arrows), parallel:
   - diamond "END OF C?": YES → diamond "EOC 2 TGR ON?": YES → "CUT OFF THE CD BYTE IN TR/CMP UNIT" (56.21.21) → join;
     NO "(EOC 1)" → "MASK THE CD BYTE BY RFL" (56.21.32) → "WRITE CD BYTE INTO F6-9" (56.31.20) → join, and (arrow) →
     diamond "EOA 2 ?". "END OF C?" NO → (arrow) diamond "EOA 2 ?": YES → "EXAMINE CD BYTE FOR PARTIAL FIELD" (56.51.20);
     NO → join.
   - "REDUCE BACD BY BSER" (54.22.01) → "REDUCE RFL BY BSER" (54.32.01) → "REDUCE BAAB BY 4" (54.12.01)
   - diamond "SHIFT COUNTER =0": YES → join; NO → "LATCH F REG SHIFTED RIGHT 4" (56.31.10 56.33.00) → "REDUCE SIIFT
     COUNTER BY 4" (56.33.00; printed "SIIFT") → "ACCUMULATE CD RESIDUE" (56.26.10)
6. Join → diamond "EOC 1 ?": NO → LOOP (arrow). YES → diamond "EOA 1 OR EOA 2 ?": NO → LOOP (arrow); YES → long line to C.

#### C. SUF-CD: finish shifting (c260_2200_200, c260_2650_200)
7. Arrow → "TURN OFF CD-FLO TURN ON SUF-CD" (56.13.05) → loop bus (arrow): "SET BACD TO 127" (54.25.01) → "RESET CD
   REGISTER" (56.24.40); "LOAD RFL REG WITH CONSTANT OF 60" (54.31.01) → "RESET EOC 1 AND EOC 2" (54.38.03); "RESET EOA 2"
   (54.18.01); diamond "SC = 0": YES → join; NO → "LATCH F REG SHIFTED R 4" (56.31.10 56.33.00) → "REDUCE SH COUNTER BY 4"
   (56.33.00).
8. Join → diamond "SHIFT COUNTER= ZERO": NO → LOOP to the bus (arrow); YES → "TURN OFF SU F - CD TURN ON SC - D 127".

#### D. SC-D 127 (c260_2650_1100)
9. Parallel: "DEVELOP SIGN BYTE AS IN STORE USING SCD & NSM AS SIGN USE ZEROS AS FLAGS" (56.25.03 54.60.05) → "WRITE SIGN
   BYTE IN D6D -63" (56.24.12; printed "D6D", presumably D60); "SET CONSTANT OF 59 INTO BACD REG" (54.25.01) → "REDUCE RFL
   REG BY 8" (54.32.01); "TRANSFER CD RESIDUE TO A CKR" (56.26.10).
10. Join → diamond "ONE BITS IN F1- F49": "YES F>48" → "SET SHIFT CONTROL TO R8" (54.32.01, 56.33.10) → "TURN OFF SC-D127
    TURN ON F-CD" (56.13.05) → E. NO → "SET SHIFT CONTROL TO R1" (56.33.10) → "TURN OFF SC-D127 TURN ON F--CD" (56.13.20)
    → long line to F. (NOTE beside this box: "F-CD & F--CD TWO DIFFERENT TRIGGERS".)

#### E. F-CD loop: F written into CD 8 bits per pass (c260_2200_2000, c260_2650_2000)
11. Bus (loop-return arrow enters at ACCUMULATE AB RESIDUE), parallel:
    - "GATE F90-97 TO SAU ADDER VIA ABT/C" (56.13.05; the "05" is partly obscured by a scan streak in c260_2200_2000, reads
      56.13.05) and "GATE ZEROS TO ADDER FROM CD" (56.21.21) → join → diamond "END OF C": YES → diamond "EOC 2": YES → join;
      NO → "MASK BY RFL" → "PERFORM ADD AND WRITE INTO CD" (56.24.12). "END OF C" NO → "PERFORM ADD AND WRITE INTO CD".
    - "REDUCE BACD BY 8" (54.22.01) → "REDUCE RFL BY 8" (54.32.01)
    - "LATCH F REG SHIFTED RIGHT 8" (56.31.10)
    - "ACCUMULATE AB RESIDUE" (56.26.10)
12. Join → diamond "F1-97 ALL ZEROS": NO → LOOP (arrow). YES → "TURN OFF F CD TURN ON SU CD- F 1" (56.13.10; printed
    "SU CD- F 1"; the matching box in F reads "SU CD-FHI") → long line entering G's set-up bus (arrow at CONSTANT OF 03).
    Loop exit F1-97 all zeros (data-dependent); 8 bits per pass.

#### F. F--CD (number fits, no 1's in F1-49) (c260_3650_200)
13. Arrow → parallel: "XFER F50-97 TO ACIB 12-59 VIA R1 SHIFT" (56.31.00); "LATCH ACOB INTO C12-59" (56.31.00) → join →
    "TURN OFF F-- CD. TURN ON SU CD-FHI" (56.13.10) → G.

#### G. SU CD-FHI and CD-FHI loop: transit read back 4 bits per pass, PAU converts (c260_3650_200, c260_3950_200, c260_3650_1100, c260_3950_1100)
14. Bus (also entered by arrow from E): "CONSTANT OF 03 TO BACD" (54.25.01); "CONSTANT OF 56 TO RFL" (54.31.02); "RESET PAU F
    REGISTER" (56.33.00) → join → "TURN OFF SU CD - FHI TURN ON CD-FHI" (56.13.10).
15. Loop bus (return arrow enters at INCREASE BACD), parallel:
    - diamond "EOC 2": NO → "TRANSFER 4 BIT BYTE FROM C TO F99- 101" (56.31.20; printed "F99- 101") → "ACCUMULATE CD RESIDUE"
      (56.26.10) → join; YES → join
    - "CONVERT DEC TO BIN SIGNAL TO PAU" (56.31.20; DEC, BIN and PAU are underlined/barred in print — marks over the
      words; read as plain text) → "LATCH F REG EACH CYCLE" (56.33.00)
    - "INCREASE BACD BY 4" (54.22.01) → "DECREASE RFL BY 4" (54.32.01)
16. Join → diamond "EOC 2": NO → LOOP (arrow); YES → "SET SHIFT CONTROL TO R1" (56.33.10) — drawn joined by a horizontal line
    to "TURN OFF CD- FHI TURN ON F--AB + LA1" (56.13.20) → H.
    Per pass 4 bits (one decimal digit); loop exit EOC 2. Boxes per pass (DERIVED): 2 serial levels + test.

#### H. F--AB + LA1 and end (c260_3650_1100, c260_3950_1100, c260_3650_2000, c260_3950_2000)
17. Parallel: diamond "ONE IN F1-49": "YES F > 48" → "SET PF ADD TRIGGER" (56.51.20) → join; NO → join;
    "GATE F50-97 TO ACIB/2-59 VIA R1 SHIFT" (56.31.20; printed "/2-59", presumably 12-59); "GATE D60-63 TO ACIB 60-63"
    (56.41.10); "LATCH DATA ON ACOB" (56.41.10).
18. Join → "TURN OFF F-- AB + LA1 TURN ON SI.R" (56.11.15) → bus: "SET BAAB TO 10" (54.15.02) → "RESET CONTROL TRIGGERS";
    "SET BACD TO 10" (54.25.02) → "SIR SIGNAL TO PAU & LA" (56.42.00); "GATE INDS TO IND REG" (56.52.04); diamond "PARTIAL
    FIELD": YES → "SIGNAL ACKR TO NOT CHECK RESIDUE" (56.41.01); NO → join.
19. Join → "TURN OFF SIR & VFL OP TGRS" (56.16.00).

#### Registers / widths on 3.11.6
F "F6-9", "F1- F49", "F90-97", "F1-97", "F50-97", "F99- 101"; ACIB "12-59", "60-63"; "C12-59"; D "D6D -63"; ACOB; ACKR/A CKR;
PAU SHIFT CTR 92; BAAB 59, 10 (plus unresolved "0500-bar", cf. 3.11.3 step 2); BACD 127, 59, 03, 10; RFL 60, 56.

---

#### Figure 3.11.7 — "FIGURE 3.11.7. VFL LOAD CONVERTED BINARY TO DECIMAL"

- PDF page 261; header "M3-04-3" / "SAU FLOW DIAGRAMS"; title read in f261b.png; foot "1/1/63" and "11-13/11-14" (f261.png).
- ALD numbers printed above each box. Three columns joined by long arrowed lines.
- Tiles: c261_1350_250, c261_1900_250, c261_1350_1150, c261_1900_1150, c261_1350_2050, c261_1900_2050, c261_2700_250,
  c261_3150_250, c261_2700_1150, c261_3150_1150, c261_2700_2050, c261_3150_2050, c261_3950_1150, z261_note2, f261.
- **Timing: cycle count NOT PRINTED.** Only "LATCH F REG EACH CYCLE" (label).
- No NOTES block. One unconnected annotation is printed in the right half (z261_note2.png, at about x=4480,y=2420 of the
  page): "ABCD-bar E H-bar" (overbar over "ABCD", a letter E, overbar over "H"). Not attached to any box; meaning not
  stated. (A printed annotation box on the left — see step 5 — is the only other free text.)
- **PAU hand-off printed: "CONVERT BIN TO DEC SIG TO PAU" (56.31.20)** once per pass of a 1-bit loop ("TRANSFER 1 BIT BYTE
  FROM CD TO F98", "INCREASE BACD BY 1", "DECREASE RFL BY 1", PAU shift control "LEFT ONE"). Binary-to-decimal is fed to the
  PAU bit-serially (DERIVED, as in 3.11.5). No multiplier named.

#### A. Entry and set-up (c261_1350_250, c261_1900_250)
Entry text: "DECODED VFL INSTRUCTION / LA START / SAU NOT OPERATING / PAU NOT OPERATING".
1. Parallel: "TURN ON VFL OP TRIGGER" (56.16.00); "TURN ON HOUSE- KEEPING TRIGGER" (56.16.00); "LOAD SAU EXECUTION REGISTER"
   (55.20).
2. Bus: "LOAD BACD REG WITH BAER-1" (54.22) → "RESET CD SIGN BYTE REG" (54.60.06); "LOAD BAAB REG WITH 0500" (54.12.00
   55.20.26; no overbar visible here) → "LOAD SAB POS 4 TO NEG SIGN MOD" (56.25.02); "RESET AB REGISTER" (56.24.40) →
   "RESET AB AND CD RESIDUES" (56.26.10); diamond "SIGNED ?": YES → "LOAD RFL REG WITH FLER-BS" (54.32.); NO → "LOAD RFL REG
   WITH FLER-1"; "RESET SIGN AB REG POS 5-7" (56.25.02).
3. Join → diamond "SIGNED ?":
   - YES → "TURN OFF HK. TURN ON HSB" (56.11.00) → parallel: "READ OUT CD SIGN BYTE AT BACD & PLACE INTO SCD REGISTER"
     (54.60.06) → "GATE SCD ∀ NEG SIGN MOD TO SIGN OF AB REG" (56.25.02; the operator is printed as a "∀"-like glyph, a V
     with a crossbar — plausibly exclusive-OR, DERIVED); "REDUCE BACD BY BSER" (54.22.02); "REDUCE RFL BY 1" (54.32.01).
     Join → diamond "EOC1 ?": NO → "TURN OFF HSB TURN ON SU CD-FHI" (56.13.10) → bus B. YES → "TURN OFF HSB TURN ON SI.R"
     (56.11.15) → long line to the end bus F (a field that is only a sign byte ends here; DERIVED).
   - NO → "TURN OFF HK TURN ON SUCD-FHI" (56.13.10) → arrow into bus B.

#### B. SU CD-FHI set-up (c261_1350_2050, c261_1900_2050)
4. Parallel: "REDUCE BACD BY RFL" (54.22.02); "RESET PAU F REGISTER" (56.33.00); "SET SHIFT CONTROL TO LEFT ONE" (56.32.01);
   "BLOCK TURN ON OF EOC2" (54.38.03).
5. Printed annotation (rounded/tape-shaped box, dashed arrow pointing at "REDUCE BACD BY RFL"):
   **"BACD NOW ADDRESSES THE LEFT MOST BIT IN THE FIELD"** (verbatim).
6. Join → "TURN OFF SUCD- FHI. TURN ON CD-FHI" (56.13.10) → long line to C.

#### C. CD-FHI loop: one bit per pass into the PAU (c261_2700_250, c261_3150_250)
7. Loop bus (arrow), parallel:
   - diamond "EOC2": NO → "TRANSFER 1 BIT BYTE FROM CD TO F98" (56.26.00) → "ACCUMULATE CD RESIDUE IN AB RES ACCUMULATOR"
     (56.26.00 56.26.10) → join; YES → join
   - "CONVERT BIN TO DEC SIG TO PAU" (56.31.20) → "LATCH F REG EACH CYCLE" (56.33.00)
   - "INCREASE BACD BY 1" (54.22.01) → "DECREASE RFL BY 1" (54.32.01)
8. Join → diamond "EOC2": NO → LOOP (arrow); YES → "TURN OFF CD-FHI. TURN ON SU F-ABOS" (56.13.15) → D.
   Per pass 1 bit, left to right (BACD increases; step 5 note). Loop exit EOC2. Boxes per pass (DERIVED): 2 serial levels + test.

#### D. SU F-ABOS (c261_2700_1150, c261_3150_1150)
9. Parallel: "LOAD BAAB REG WITH 0500-bar" (54.12.00 55.20.26; overbar under/over "0500" — a bar is printed between "REG WITH"
   and "0500"; read as overbar) → "RESET AB REGISTER" (56.24.40); "TURN ON AB CUTOFF TRIGGER" (56.21.11) → "TURN OFF CLOSE CD
   TRIGGER" (56.21.31); "SET SHIFT CONTROL FOR RIGHT EIGHT" (56.32.01 56.33.10) → "RESET EOC1 & EOC2 TGRS" (54.38.03);
   "KILL CD SWITCH MATRIX OUTPUT" (56.13.15) → "GATE F90-97 TO CDSM LEVEL" (56.13.15).
10. Join → diamond "F1-97 =AH ZEROS" (printed "=AH", presumably ALL): YES → "TURN OFF SUF-ABOS TURN ON SI.R" (56.11.15) →
    arrow to F. NO → "TURN OFF SUF-ABOS. TURN ON F-ABOS" (56.13.15) → E.

#### E. F-ABOS loop: decimal result out of F into AB, 8 bits per pass (c261_2700_2050, c261_3150_2050)
11. Loop bus (arrow), parallel:
    - "GATE F90-97 TO ADDER VIA CD TRUE/COMP" (56.13.15) and "GATE ZEROS TO ADDER FROM AB" (56.21.12) → join → diamond
      "END OF A ?": YES → "ENABLE CD PARTIAL FIELD CHECKER" (56.51.20); NO → "PERFORM ADD & WRITE INTO AB" (56.24.11)
    - "LATCH F REG SHFTD RIGHT 8" (56.33.00)
    - "REDUCE BAAB BY 8" (54.12.01)
    - "ACCUMULATE CD RESIDUE" (56.26.10)
12. Join → diamond "F1- 97 =ZEROS": NO → LOOP (arrow); YES → "TURN OFF F-ABOS. TURN ON SI.R" (56.11.16) → arrow to F.
    Loop exit F1-97 zero (data-dependent); 8 bits per pass.

#### F. End (c261_3950_1150)
13. Bus (entered by arrows from: the EOC1-YES sign-only exit in A, the F1-97 =AH ZEROS YES exit, and E's exit), parallel:
    "UPDATE AB RESIDUE SIGNAL TO A CHECKER" (56.41.01) → "RESET CONTROL TRIGGERS"; "SET BAAB TO 10" (54.15.02) → "SI.R SIGNAL
    TO PAU & LOOK AHEAD" (56.42.00); "SET BACD TO 10" (54.25.02) → "COMPARE AB&CD RESIDUE REGISTERS" (56.26.10, 59.06.04);
    "GATE INDS TO IND REG" (56.52.04).
14. Join → "TURN OFF SI.R & VFL OP TRIGGERS" (56.16.00).

#### Registers / widths on 3.11.7
F "F98", "F90-97", "F1-97"; BAAB 10 (plus "0500" in A and "0500-bar" in D, unresolved, cf. 3.11.3 step 2); BACD 10; SAB POS 4; AB sign POS 5-7; CDSM ("CD SWITCH MATRIX");
AB RES ACCUMULATOR; PAU shift control LEFT ONE / RIGHT EIGHT.

---

#### Cross-figure summary (DERIVED unless quoted)

| Fig | PDF | Page | Timing printed | Main loops (exit condition; bits per pass) | PAU hand-off (verbatim) |
|---|---|---|---|---|---|
| 3.11.2 ADD 1 TO MEMORY | 256 | 11-3/11-4 | NOT PRINTED | PL1/PL2 add loop (EOC 1, or LIKE SIGNS & no CARRY; 8 binary / BSER decimal); recomplement loop (EOC 1); LA GO wait | none |
| 3.11.3 LOAD TRANSIT AND SET / DEC MPY / DEC MPY-ADD / DEC DIV / LOAD FACTOR | 257 | 11-5/11-6 | NOT PRINTED | CD-FLO (EOC1 then EOA1/EOA2; R4 decimal / R8 binary); SU F-CD (SH CTR = 0); F-CD (F1 97 ZEROS; 8) | "LOAD CONSTANT OF 96/92 INTO PAU SHIFT CTR", "RESET PAU F REGISTER", "SI.R. SIGNAL TO PAU AND LA" |
| 3.11.4 LOAD CONVERTED DEC TO BIN | 258 | 11-7/11-8 | NOT PRINTED | CD-FLO (E0C1 and SN CTR = 0; 4); AB-FHI (EOC2; 4); F-ABOS (F1-97 = 0; 8) | "CONVERT DEC TO BIN SIGNAL TO PAU", "SI.R SIGNAL TO PAU & L.A." |
| 3.11.5 LOAD TRANSIT CONV BIN TO DEC | 259 | 11-9/11-10 | NOT PRINTED | CD-FHI (EOC2; 1 bit); F-CD (F1-97 ALL ZEROS; 8) | "CONVERT BIN TO DECIMAL SIGNAL TO PAU", "SIR SIGNAL TO PAU AND LA" |
| 3.11.6 LOAD TRANSIT CONV DEC TO BIN | 260 | 11-11/11-12 | NOT PRINTED | CD-FLO (EOC 1 then EOA 1 OR EOA 2; 4); SUF-CD (SHIFT COUNTER= ZERO); F-CD (F1-97 ALL ZEROS; 8); CD-FHI (EOC 2; 4) | "CONVERT DEC TO BIN SIGNAL TO PAU", "SIR SIGNAL TO PAU & LA" |
| 3.11.7 LOAD CONV BIN TO DEC | 261 | 11-13/11-14 | NOT PRINTED | CD-FHI (EOC2; 1 bit); F-ABOS (F1-97 =ZEROS; 8) | "CONVERT BIN TO DEC SIG TO PAU", "SI.R SIGNAL TO PAU & LOOK AHEAD" |

- No sheet prints a cycle count, clock, A/B pulse or time. Every loop is described only by its trigger state (PL 1, CD-FLO,
  CD-FHI, F-CD, F-ABOS ...) and its exit test.
- Conversion asymmetry (from labels): decimal→binary feeds the PAU 4 bits (one digit) per step; binary→decimal feeds it
  1 bit per step. The arithmetic of the conversion (x10 / x2 accumulation) is not drawn on any SAU sheet — only the
  "CONVERT ... SIGNAL TO PAU" box. No multiplier is mentioned on any of the six sheets.
- Field-unload loops (F-CD, F-ABOS) terminate when F1-97 becomes all zeros — data-dependent length, not field-length-driven.
- The PAU F register is numbered at least F1-F101 on these sheets (F98-101 / F99-101 receive incoming digits; F90-97 is the
  outgoing byte).

### Appendix E

#### E — SAU flow diagrams, R23-9732 (7101 CPU CE manual), PDF 263 and PDF 265

Transcriber: agent tE. Source: 300 dpi renders [scratch, deleted]/pdf263-263.png, pdf265-265.png.
Tiles and zooms are in [scratch, deleted]/ (names given below; `a_X_Y.png` = PDF 263 crop at
origin X,Y; `b_X_Y.png` = PDF 265; `z263_*`, `z265_*` = enlarged zooms).

Conventions: text in CAPITALS in quotes or in boxes is VERBATIM as printed (line breaks
collapsed). Overbars are written as `-bar` or with a combining overline where unambiguous.
"•" is the printed AND dot. Anything marked DERIVED is my interpretation, not printed.
Numbers like 56.11.06 are the ALD page references printed in the boxes.

---------------------------------------------------------------------------------------------

#### FIGURE 3.11.9 (PDF 263)

- Title as printed: "FIGURE 3.11.9. VFL ADD, ADD TO MAGNITUDE, LOAD, OR LOAD WITH FLAGS"
- Running head: "M3-04-3" (left) and "SAU FLOW DIAGRAMS" (right)
- Foot: date "1/1/63", page "11-17/11-18" (fold-out). Title, date and page read from tile
  foot263.png; running head from head263.png.
- **Timing: cycle count NOT PRINTED.** No clock, A/B pulse, microsecond or cycle number appears
  anywhere on the page. The only "cycle" words are trigger/decision names: "FIRST CYCLE",
  "VFL LAST CYCLE TO PAU", "VFL LAST CYCLE NOT STORE OP TO PAU".
- No NOTES block is printed on this page. The only free text outside the flow is the opcode
  legend (lower right, tile `a_4050_2050.png`, zoom `z263_legend2.png`):

      VFL
      + (ABCDE)      overbar over all of A B C D E          -> A̅B̅C̅D̅E̅
      +MG (ABCDE)    overbar starts over B: A plain, B C D E barred -> A B̅C̅D̅E̅
      L (ABCDE)      overbar over A B, and a separate one over E   -> A̅B̅ C D E̅
      LWF (ABCDE)    overbar over (B?)C and over E. The left end of the first bar
                     sits over the right half of B, so whether B is barred is
                     ILLEGIBLE/ambiguous (z263_legend2.png). Reads as A B̅? C̅ D E̅.
  DERIVED: A..E are five operation-code bits decoded to select the four instructions this
  figure covers. I have not cross-checked them against the Reference Manual op-code table.

- Logical connectives: **NOT on this figure** (no connective / switch-matrix / logic box).
- Decimal correction: not drawn as a box; decimal appears only as the BINARY/BIN/DEC branches
  that pick byte size (4 vs 8 bits, 9's vs 1's fill, -4 vs -8). DERIVED.

#### Glossary of names as printed (no expansion is printed; expansions are NOT given)
AB, CD (SAU registers), BAAB, BACD (bit-address counters for AB and CD — DERIVED from
"UPDATE BAAB … BACD", "LOAD BAAB TO 127", "SET BAAB TO 10"), BAER, RFL, FLER, BSER, BS, SAB,
SRAB, SRAB4, SRAB 5-7, NSM, SCD, LS, LF, EOA1, EOA2, EOC1, EOC2, EHOM1, HK, HSB, PL1, PL2, ZAB,
SIR, SUR, RECOMP, AU, A (decision "AU + A", "A + AU"), LA (look-ahead), PAU.

#### Part 1 — Start (tile a_1550_380.png)
Entry conditions printed at the top (four lines, no box):
"PAU NOT OPER / VFL INST / LA START / SAU NOT OPER"

Three boxes in parallel off one line:
1. [SET VFL OP TRGR 56.16.00]
2. [SET HK TRIG 56.16.00]
3. [LOAD SAU EX REG 55.10.??] — the ALD number is overprinted/misregistered: "55.10." then
   ILLEGIBLE (z263_sauex.png; double-struck characters). (PDF 265's equivalent box reads
   "LOAD SAU EXEC REG 55.10.")

From under SET HK TRIG a junction feeds a horizontal bus, which also receives the
"LA GO = NO" loop-back (see Part 2). Six parallel branches hang from this bus
(all of them rejoin a common bus at the bottom of the section, orig y≈1350, except
LA REJECT):

**1a. BAER = 0** (ALD 55.10.16 printed under the diamond)
 - NO  -> [LOAD BACD TO BAER-1 54.21.01]
 - YES -> [LOAD BACD TO 64-1 54.22.02 54.21.01]

**1b. BINARY**
 - NO  -> [LOAD BAAB WITH O̅S̅ - 2 LO ORDER BITS FORCED TO Ø 54.11.1 55.20.26.1]
          (printed "OS" with an overbar; "Ø" is the slashed zero) -> drops straight to a
          junction on the SIGNED-YES line -> [LOAD RFL TO FLER-BS 54.32]
 - YES -> [LOAD BAAB WITH O̅S̅ 54.11.1] -> **SIGNED**
     - YES -> [LOAD RFL TO FLER-BS 54.32]
     - NO  -> [LOAD RFL TO FLER-8 54.32.]
 (As drawn: decimal always gets FLER-BS; FLER-8 only for unsigned binary. Same shape as Fig
 3.11.11 Part 1c.)

**1c. LA GO** — only YES drawn -> [RESET CD SIGN BYTE REG 54.60.06]

**1d. LA REJECT** — only YES drawn -> [TON RESET ONLY 56.14.00] -> a long line that does NOT join
the bottom bus; it runs right and down and enters [INST RESET 56.14.10] in the ending
section (Part 5). (Traced on a_1550_1200, a_2450_1200, a_2450_2050, z263_final.png.)

**1e. AU + A** (no YES/NO labels printed; single right exit) -> junction feeding three things
(z263_lagoleft.png, z263_au.png):
 - [RESET AB REG 56.24.40] -> bottom bus
 - **LA GO** — only YES drawn -> junction:
     - [GATE NSM INTO SRAB4 56.25.02] (no exit line drawn below this box)
     - DASHED line -> [GENERATE A SAMPLE TO SRAB 5-7 BUT INHIBIT R OUT OF FLAGS - RESET 5-7
       56.25.02] -> bottom bus
 - a line to [SET LIKE SIGNS 56.15.01.1]

**1f. AU** (z263_au.png)
 - YES -> **NSM = 0**
     - NO  -> [RESET LIKE SIGNS]
     - YES -> junction -> [SET LIKE SIGNS 56.15.01.1]
 - NO  -> **SAB = ER 29**
     - YES -> same junction -> [SET LIKE SIGNS 56.15.01.1]
     - NO  -> **AU + A**
         - YES -> [RESET LIKE SIGNS]
         - NO  -> [SET LIKE SIGNS 56.15.01.1]
 - [RESET LIKE SIGNS] (no ALD printed) -> **SIGNED**
     - YES -> bottom bus
     - NO  -> **A + AU**
         - YES -> [SET CD COMP 56.21.21] -> bottom bus
         - NO  -> bottom bus
 - [SET LIKE SIGNS] -> bottom bus

#### Part 2 — wait for look-ahead, then the sign-byte (HSB) cycle (a_1550_1200.png, z263_hsb.png)
Bottom bus -> **LA GO**
 - NO -> line right to the frame and back up to the top bus of Part 1 (re-test).
   DERIVED: a wait loop until look-ahead delivers the operand.
 - YES -> junction:
   - **RFL CARRY** — NO -> [TON EOC1 54.38.01]. YES exit not drawn.
   - **SIGNED**
     - YES -> [HKOFF HSB ON 56.11.00] -> HSB section below
     - NO  -> [HK OFF PL1 ON 56.11.06] -> line right into the left edge of the
       right-hand frame = entry to the per-byte loop (Part 3). DERIVED: unsigned
       operands skip the sign-byte cycle.

HSB section: [HKOFF HSB ON] -> junction feeding, in parallel:
 - [READ OUT CD SIGN BYTE A7 BACD PLACE SIGN AND FLAGS IN SEP REG 54.60.06]
   ("A7" is as printed; DERIVED: a misprint for "AT"). No exit line drawn below.
 - **AU + A**
   - YES -> **SCD = 1**
       - YES -> [INVERT LIKE SIGNS 56.15.01] -> join
       - NO  -> join
     join -> **LS COND MET**
       - NO  -> [SET CD COMP 56.21.21] -> bus
       - YES -> bus
   - NO -> junction:
       - **LF** — YES -> [GATE FLAGS TO SRAB 56.25.02] -> bus; NO -> bus
       - [HOLD LIKE SIGNS TRIG ON 56.15.01] (no exit line drawn)
 - **BINARY** (a_2450_1200.png)
   - NO  -> [REDUCE RFL BY BSER 54.32.01] (the word "BY" is struck over/garbled but legible)
   - YES -> [REDUCE RFL BY 8 54.32.01]
 - [REDUCE BACD BY BSER 54.22.02]
All -> bus -> **EOC1 ON**
 - YES -> [HSB OFF SIR ON 56.11.16] -> ending section (Part 5)
 - NO  -> [HSB OFF PL1 ON 56.11.06] -> line right into the right-hand frame = per-byte loop.

#### Part 3 — the per-byte add loop (right-hand frame; a_3250_380, a_4050_380, z263_cd.png)
The loop is entered along the frame's left edge (from HK OFF PL1 ON or HSB OFF PL1 ON) and
along the frame top reaches a bus that fans out to four parallel groups:

**3a. CD side: CD CUT OFF**
 - YES -> **CD COMP**
     - YES -> **BINARY**
         - NO  -> [GATE 9'S TO ADDER FROM CD]
         - YES -> [GATE 1'S TO ADDER FROM CD]
     - NO  -> [GATE Ø'S TO ADDER FROM CD 56.21.22]
 - NO  -> (ALD "56.21.22" printed at the corner) **CD COMP**
     - YES -> [GATE CD BYTE COMP TO ADDERS]
     - NO  -> [GATE CD BYTE TRUE TO ADDERS]

**3b. AB side: AB CUT OFF**
 - YES -> [GATE O'S TO ADDER FROM AB]
 - NO  -> [GATE AB TRUE TO ADDER]
 (DERIVED: AB is never complemented going into the adder; only CD is.)

**3c. EOA1** — only YES drawn -> both [TON EOA2 54.18.01] and [TON AB CUT OFF 56.21.11]

**3d. BINARY** (a_4050_380.png)
 - NO  -> [UPDATE BAAB BY 4; RFL AND BACD BY BSER]
 - YES -> **PARTIAL BYTE**
     - NO  -> [UPDATE BAAB, BACD AND RFL BY 8]
     - YES -> [UPDATE BAAB AND BACD BY RFL]

All four -> bus -> **PL1 • P̅L̅2̅** (printed "PL1•" over "PL2" with overbar)
 - NO  -> straight to PERFORM ADD
 - YES -> **LIKE SIGNS**
     - YES -> [SET PL2 TRIGGER 56.11.06]
     - NO  -> [HOT 1 TO SAU ADDER 56.23.01] -> [SET PL2 TRIGGER 56.11.06]
   -> PERFORM ADD
   (DERIVED: on the first PL1 cycle only, unlike signs inject the hot 1 that turns the
   ones'/nines' complement of CD into a two's/ten's complement; PL2 then marks "not first".)

[PERFORM ADD OF CD AND AB. WRITE RESULT INTO AB AT BAAB IF NOT EOA2]

-> **EOC1**
 - NO -> line right to the frame's right edge and up to the top bus = **LOOP: next byte**.
 - YES -> end-of-field tests (z263_eoc1.png):
   junction -> [TON EOC2•CDC/O 56.21.11 54.38.03] (no exit drawn) and **LIKE SIGNS**
   - LIKE SIGNS YES -> junction -> **CARRY** (second) and **EOA1** (second)
       - CARRY(2): NO exit joins the CARRY(1)-YES line (below); YES exit not drawn.
       - EOA1(2): YES -> joins the same line; NO (unlabeled right exit) -> junction -> frame
         right edge -> top bus = **LOOP again** (DERIVED: like signs, AB field not exhausted:
         keep going, propagating carry into the rest of AB with CD cut off).
   - LIKE SIGNS NO -> **CARRY** (first)
       - YES -> junction -> (with CARRY(2)-NO and EOA1(2)-YES) -> line right ->
         [PL1•2 OFF SIR ON 56.11.16] -> down the right frame edge -> ending section.
       - NO  -> **EHOM1**
           - NO  -> joins the EOA1(2)-NO line -> **LOOP again** via the frame.
           - YES -> **AU**
               - YES -> [PL1•2 OFF ZAB ON 56.11.10] -> [RESET AB 56.24.40] -> [TOF 2AB, TON SIR]
                 -> ending section. ("2AB" is printed with a clear numeral 2, z263_2ab.png,
                 while the box above reads "ZAB ON"; DERIVED: "2AB" is a misprint for ZAB.)
   PRECEDENCE NOT PRINTED: on the LIKE SIGNS = YES side, CARRY(2) and EOA1(2) hang off the same
   junction in parallel; CARRY(2)=NO leads to finish (SIR) while EOA1(2)=NO leads back into the
   loop. The diagram does not say which wins when both apply (and CARRY(2)=YES has no exit).
   Any order I give is DERIVED.
               - NO  -> [PL1•2 OFF SUR ON 56.11.10] -> **recomplement setup** (Part 4)
   DERIVED: unlike signs and no end carry = result is in complement form -> recomplement.
   With AU set (DERIVED: add-to-unsigned? the result field is zeroed instead) the AB field is
   reset rather than recomplemented. The expansion of AU is not printed.

#### Part 4 — recomplement setup and the recomplement pass (a_3250_1200, a_4050_1200, z263_eoa2.png, a_3250_2050, a_4050_2050)
[PL1•2 OFF SUR ON 56.11.10] -> junction, five things in parallel:
 - [LOAD BACD TO BAER-1 54.22--] -> [SET AB COMP 56.21.11] -> [TOF AB CUT OFF 56.21.11] -> join
 - **EOA2**
     - YES -> hexagon [RFL INPUT "A" GETS NOTHING INPUT "B" = -8. ADDER OUTPUT =120]
     - NO  -> [GATE B̅A̅A̅B̅ TO RFL INPUT "A" 54.31.01.1]
     -> [LOAD BAAB TO 127 54.15.02] -> join
 - **DEC** (ALD 54.32.01.1 printed between its outputs)
     - YES -> [RFL INPUT "B" = -4]
     - NO  -> [RFL INPUT "B" = -8]
     -> join
 - [INVERT SAB 56.25.02] -> [SET CD CUT OFF 56.21.21] -> join
 - [TOF EOC1, EOC2 54.38.03] (no exit drawn)
join -> [TOF SUR TON RECOMP AND PL1 56.11.10 56.11.06]
-> junction (loop return point) -> **FIRST CYCLE**
 - YES "(PL1•P̅L̅2̅)" -> [TON PL2 56.11.06] -> [HOT"1" TO ADDER 56.23.01] -> join
 - NO -> join
-> [READ OUT BYTE AT BAAB, COMP, PASS THRU ADDER WRT IN AT BAAB]
-> **BIN**
 - NO  -> [REDUCE BAAB AND RFL BY 4]
 - YES -> [REDUCE BAAB AND RFL BY 8]
-> **EOC1**
 - NO  -> line right and up to the junction above FIRST CYCLE = **RECOMPLEMENT LOOP, one byte
   per pass**
 - YES -> [TOF PL1•PL2 B, TON SIR] (printed "TOF PL1oPL2 / B, / TON SIR" — the AND dot is
   printed as a small open circle and "B," stands alone on the second line; meaning of "B"
   not printed; z263_plb.png) -> bottom line
   -> left -> ending section.
DERIVED: this is the second pass: a byte-serial two's/ten's complement of the AB result
(complement each byte, hot 1 on the first byte only), walking BAAB from the low-order end
(BAAB loaded to 127) downward by 4 (decimal) or 8 (binary) bits per step. It is a separate
loop from the add loop.

#### Part 5 — ending (a_1550_2050, a_2450_2050, z263_final.png)
Entries: [HSB OFF SIR ON] from Part 2, the right-frame bottom line (TOF 2AB, TON SIR / TOF
PL1•PL2 B, TON SIR) and [PL1•2 OFF SIR ON] from Part 3 all join one line, which fans out to
eight parallel boxes:
 - [SET FLAG INDS 56.52.04]
 - [SET ARITH RESULT IND 56.52.03]
 - (a line straight down to) [TOF SIR 56.11.16]
 - [VFL LAST CYCLE TO PAU 56.42.00]
 - [VFL SIR TO LA 56.42.00] (a faint speck above "IR" at 6x zoom, z263_sir.png, is not a
   clear overbar; read as plain SIR)
 - [VFL LAST CYCLE NOT STORE OP TO PAU 56.42.00]
 - [UPDATE AB RESIDUE TO A CKR 56.41.01]
 - [INST RESET 56.14.10] (also entered by TON RESET ONLY from LA REJECT, Part 1d)
[INST RESET] -> junction, in parallel:
 - **LA START** — YES -> [START NEXT INST 56.16.00]; NO -> [RESET VFL OP 56.16.00.1]
 - [RESET:] list box, verbatim:
       RECOMP        56.11.10
       AB CUTOFF     56.21.11
       AB COMP
       CD CUTOFF     56.21.21
       CD COMP
       CLOSE CD      56.21.31
       P BYTE        56.21.32
       NOT ZRT       56.15.05
       PF ADD        56.51.20
       ZERO DIV      56.51.30
       COMP RES INDS 56.52.01
       CARRY TRIG    56.23.03
       EOC1 EOC2     54.38.03
       MPYC5         56.12.05
 - [SET BAAB TO 10 54.15.01]
 - [SET BACD TO 10 54.25.01]
(LA START, the RESET: list, SET BAAB TO 10 and SET BACD TO 10 all hang off one line fed by the
bottom of [INST RESET]; z263_final.png.)

#### Fig 3.11.9 — summary of loops and per-step width
- Add loop (Part 3): one pass round the frame per byte. Byte width: binary = 8 bits
  ("UPDATE BAAB, BACD AND RFL BY 8") or a partial byte ("UPDATE BAAB AND BACD BY RFL");
  decimal = 4 bits for AB ("UPDATE BAAB BY 4") with BACD and RFL stepped by BSER (DERIVED:
  the CD byte size). Exit condition: EOC1 (DERIVED: end of the CD operand field), then
  LIKE SIGNS/CARRY/EOA1/EHOM1 decide: continue (carry propagation into the rest of AB),
  finish, or recomplement.
- DERIVED box count per add-loop iteration: 1 fan of 4 parallel gate/update groups ->
  PL1•PL2-bar test -> PERFORM ADD -> EOC1. No timing is printed, so no cycle count can be read.
- Recomplement loop (Part 4): one byte per pass, 4 (BIN=NO) or 8 (BIN=YES) bits; exit EOC1.
- Word boundary / second memory word: **not drawn on this figure.** No box mentions a
  second word, a fetch, or look-ahead beyond "LA GO", "LA REJECT", "LA START" and "VFL SIR TO
  LA". (DERIVED: BAAB/BACD are 7-bit bit addresses — "LOAD BAAB TO 127", "BACD TO 64-1" — so
  the two-word (128-bit) window is addressed directly; the manual does not say so here.)
- Result return: AB is written in place ("WRITE RESULT INTO AB AT BAAB IF NOT EOA2").
  Nothing on this figure stores to memory (Load/Add target the accumulator).

---------------------------------------------------------------------------------------------

#### FIGURE 3.11.11 (PDF 265)

- Title as printed: "FIGURE 3.11.11. VFL ADD TO MEMORY, ADD MAGNITUDE TO MEMORY, STORE OR
  STORE ROUNDED" ("STORE OR" set tight at the line end; tile foot265.png)
- Running head: "M3-04-3" / "SAU FLOW DIAGRAMS" (head265.png)
- Foot: date "1/1/63", page "11-21/11-22" (fold-out; foot265.png).
- **Timing: cycle count NOT PRINTED.** No clock, A/B pulse or cycle numbers. The only timing-
  related words are trigger/decision names ("1ST CYCLE", "TON PL1", "TON PL2", "TON SIR") and
  the printed note about extra cycles after EOC2 (see NOTE).
- **Printed NOTE (verbatim, b_4100_1000.png, z265_wr2.png), tied by asterisks to the boxes
  [TON EOC2 54.38.03]* and [TON CD CUTOFF 56.21.21]*:**
  "* NO WRITE IN AFTER EOC2. CYCLES TAKEN FOR PF CK ONLY."
- Opcode legend (lower right, z265_legend.png), poorly printed:
      M+ (ABCDE)      M+MG (ABCDE)      S (ABCDE)      SRD (ABCDE)
  Overbars visible: M+ and M+MG both show bars over (A,B) and over (D,E); S shows a bar over
  (A,B) and a fainter one over (D,E); SRD shows bars over B and over E. Since M+ and M+MG look
  identical, at least one bar is lost in printing: **overbar extents ILLEGIBLE** (z265_legend.png).
- Logical connectives: **NOT on this figure.**
- Decimal handling: branches "BINARY", "BIN", "DECIMAL", "BYTE 4", the box [ASSEMBLE ZONE BITS
  TO SATISFY BYTE SIZE 54.60.03 56.25.03], and ones/nines fill for a complemented cut-off AB.
  No separate decimal-correction box.
- Misprints, kept verbatim: "DECODED UFL INST", "SET UFL OP TRIG" (DERIVED: VFL); "AM+AYM"
  (DERIVED: AM+AUM); "GATE SAB* NSM TO CO SIGN BYTE" (DERIVED: CD); "BLOCK TON OR EOC2" (DERIVED:
  OF). Zooms: z265_ufl.png, z265_aym.png, z265_sab.png, z265_rsu.png.
- Physical damage: a vertical crease runs through orig x≈2565 from y≈2250 to the bottom, across
  [REDUCE RFL BY 8], [TOF HSB 56.11.00] and [TON PL1 56.11.06] in the recomplement-HSB column
  (b_1950_1850.png, b_2450_1850.png). Still legible; "BY" and the "H" of HSB partly obscured.

Role reversal vs Fig 3.11.9 (DERIVED from box text): here AB (accumulator) is the source that may
be complemented ("AB COMP ON", "GATE AB BYTE COMP TO ADDER") and CD (the memory operand) is the
destination ("WRITE RESULT INTO CD AT BACD"; the recomplement pass reads CD).

#### Part 1 — Start (b_250_180.png, b_1100_180.png, z265_aum.png)
Entry box: [DECODED UFL INST / SAU NOT OPER / PAU NOT OPER / LA START]
-> in parallel: [SET UFL OP TRIG 56.16.00], [SET HK TRIG 56.16.00], [LOAD SAU EXEC REG 55.10.]
[SET HK TRIG] -> bus, which fans out to:

**1a. BAER = 0** (labels "N"/"Y"): N -> [LOAD BACD TO BAER-1 54.21.01]; Y -> [LOAD BACD TO 64-1
  54.21.01]
**1b. L. A. REJECT** (diamond) — YES -> cylinder [TON RESET ONLY. THIS CYCLE GENERATES INST RESET
  PORTION OF SIR 56.14.00] (no exit drawn)
**1c. BINARY** (labels "N"/"Y")
 - N -> [LOAD BAAB WITH O̅S̅ 2 LO ORDER BITS = 0 54.11.1 55.20.26]
 - Y -> [LOAD BAAB WITH O̅S̅ 54.11.1] -> **SIGNED**
     - YES -> joins the N branch -> [LOAD RFL TO FLER - B. S. 54.32.]
     - NO  -> [LOAD RFL TO FLER-8 54.32]
**1d. S + SRND** (single unlabeled exit) -> [TON CD CUT OFF 56.21.21]
**1e. AM + AUM** — "NO (S + SRD)" -> [TON LIKE SIGNS 56.15.01]. YES exit not drawn.
**1f. AUM**
 - YES -> **NSM = 0**: YES -> [TON LIKE SIGNS 56.15.01]; NO -> [TOF LIKE SIGNS 56.15.01]
 - NO  -> **SAB=NSM**: YES -> [TON LIKE SIGNS]; NO -> **AM + AUM**: YES -> [TOF LIKE SIGNS];
   NO not drawn.
 - [TOF LIKE SIGNS] -> **SIGNED**: Y -> bus; NO -> **AM + AUM**: YES -> [TON AB COMP 56.21.11]
   -> bus; NO -> bus.
**1g.** The bus continues right and down to a second **L. A. REJECT** (drawn as a rectangle):
  YES -> rounded terminal [T ON RESET ONLY. GENERATES INST RESET PORTION OF SIR 56.14.00]
  (z265_rej.png).

All of 1a–1f -> bottom bus -> **L. A. GO**
 - NO -> line right, then an ARROW into the vertical line that runs up to the Part-1 bus
   (z265_rej.png). DERIVED: wait loop until look-ahead is ready (as in Fig 3.11.9).
 - YES -> junction -> **RFL CARRY** (NO -> [TON EOC1 54.38.01], no exit drawn; YES not drawn)
   and **SRD**.

#### Part 2 — STORE ROUNDED rounding cycle (b_250_1000, b_250_1850, z265_rsu.png)
**SRD**
 - YES -> [TOF HK TON RSU 56.11.00] -> **BINARY** (ALD 54.12.01 printed between the branches)
     - NO  -> [ADD 4 TO BAAB] -> [TOF RSU TON RND 56.11.00] -> junction R
     - YES -> [ADD 1 TO BAAB] -> **SIGNED**
         - NO  -> [BLOCK TON OR EOC2 DURING RND&RSU 56.11.01] -> junction R
         - YES -> [TON HSB 56.11.00] -> HSB bus (Part 3)
   junction R -> **BINARY**
     - YES -> [READ OUT 1 BIT BYTE FROM AB TO ADDER] -> [GATE HOT 1 TO ADDER] ->
              [SAVE ANY CARRY IN CARRY TRIG] -> [REDUCE BAAB BY 1]
     - NO  -> [READ OUT 4 BIT BYTE FROM AB TO ADDER] -> [GATE HOT 4 & 1 TO ADDER] ->
              [SAVE ANY CARRY IN CARRY TRIG] -> [REDUCE BAAB BY 4]
     -> [TOF RND 56.11.00] -> bottom line -> [TON PL1 56.11.06] -> per-byte frame (Part 4).
 - NO  -> **SIGNED**
     - YES -> [TOF HK TON HSB 56.11.00] -> HSB bus (Part 3)
     - NO  -> [TOF HK TON PL1 56.16.00 56.11.06] -> line right -> arrow into the per-byte frame.
DERIVED reading of rounding: BAAB is first moved one position BELOW the low-order end of the AB
field (ADD 1 = one bit for binary, ADD 4 = one 4-bit digit for decimal); one RND cycle reads that
single bit/digit and adds hot 1 (binary) or hot 4&1 = 5 (decimal), keeping only the carry; BAAB
is put back (REDUCE BY 1 / BY 4). The saved carry is injected on the store loop's byte(s) via
"CARRY ON" -> "SRND" -> "GATE CARRY IN TO ADDER" (Part 4). It is one single-byte pass, not a
full-field pass.
AS-DRAWN ASYMMETRY (not resolved by the figure):
 - Decimal path: ADD 4 TO BAAB -> [TOF RSU TON RND] -> round read. There is NO SIGNED test on this
   path, so as drawn signed decimal SRD never reaches the HSB (sign) cycle.
 - Binary path: ADD 1 TO BAAB -> SIGNED; it never passes the [TOF RSU TON RND] box. Unsigned binary
   joins junction R via [BLOCK TON OR EOC2 ...]; signed binary goes to [TON HSB] and the HSB bus,
   and how it then reaches the RND read is NOT drawn.
 Treat the SRD control as uncertain beyond what is listed.

#### Part 3 — sign-byte (HSB) cycle (b_250_1850, b_1100_1850, b_1100_2550)
HSB bus (fed by [TON HSB] and [TOF HK TON HSB]) fans out to:
 - **RFL CARRY** (second instance) — NO -> [TON EOC1 54.38.01] -> bottom line (to TON PL1)
 - [REDUCE BACD BY BSER 54.22.02] -> bus2
 - **EOC1.** — Y -> [TON EOC2 CD CUTOFF 54.38.03 56.21.21] -> bottom line (to TON PL1)
 - **BINARY**: NO -> [REDUCE RFL BY BSER]; YES -> [REDUCE RFL BY 8] -> bus2
 - **AM + AUM**
     - N "(S+SRD)" -> [TON LIKE SIGNS 56.15.01] -> bus2
     - YES -> **SCD= 1** (YES -> [INVERT LIKE SIGNS TRIG 56.15.01]; NO direct) -> **LIKE SIGNS**
         - YES -> join;  NO -> [TON AB COMP 56.21.11] -> join  -> bus2
 - [READ OUT CD SIGN BYTE AT BACD, PLACE SIGN AND FLAGS INTO SRCD 54.60.06] (no exit drawn)
 - **S+SRND** — Y -> both [GATE FLAGS & ZONE BITS TO SATISFY B.S. 54.60.03] and
   [GATE SAB* NSM TO CO SIGN BYTE 54.60.05] -> bus2
bus2 -> [TOF HSB 56.11.00] -> junction (also gets TOF RND, TON EOC1, TON EOC2 CD CUTOFF) ->
[TON PL1 56.11.06] -> long line right -> arrow up into the per-byte frame.

#### Part 4 — the per-byte loop (right frame; b_2450_180, b_3300_180, b_4100_180, b_2450_1000, z265_srnd.png, z265_wr1.png, z265_wr2.png)
Frame entry -> top bus -> four parallel groups:

**4a. AB side: AB COMP ON**
 - NO  -> **AB CUT OFF**: NO -> [GATE AB TRUE TO ADDER]; YES -> [GATE 0'S TO ADDER FROM AB]
 - YES -> **AB CUT OFF** (ALD 56.21.12 printed nearby)
     - NO  -> [GATE AB BYTE COMP TO ADDER]
     - YES -> **BIN**: YES -> [GATE ONES TO ADDER]; NO -> [GATE NINES TO ADDER]
**4b. CD side: CD CUT OFF** (ALD 56.21.22 between branches)
 - NO -> [GATE CD TRUE TO ADDER];  YES -> [GATE 0'S TO ADDER]
 (DERIVED: CD is never complemented in this loop; only AB is.)
**4c. EOA1** — YES -> [TON EOA2 54.18.01] and [TON AB CUTOFF 56.21.11]
**4d. BINARY**
 - NO  -> [UPDATE BAAB BY 4. REDUCE RFL & BACD BY BSER]
 - YES -> [UPDATE BAAB BY 8. REDUCE RFL BACD BY 8 OR RFL]

All -> bus -> **S+SRND**
 - YES (store, store rounded) -> **CARRY ON**
     - NO -> join S
     - YES -> **SRND**: NO -> join S; YES -> [GATE CARRY IN TO ADDER 56.23.01] -> both join S and
       **CARRY OUT OF ADDER** — NO -> **EOC2** — NO -> [TOF CARRY TRIG 56.23.03] (no exit drawn;
       the YES exits of both diamonds are not drawn)
     join S -> **DECIMAL**: NO -> bus; Y -> **BYTE 4**: N -> bus; Y -> [ASSEMBLE ZONE BITS TO
     SATISFY BYTE SIZE 54.60.03 56.25.03] -> bus -> to the EOC2 test below. No PERFORM ADD box on
     this branch.
 - "NO (AM + AUM)" (add to memory) -> **1ST CYCLE** "(PL1 · PL2)" (no overbar on PL2 here,
   z265_pl.png)
     - NO  -> straight to [PERFORM ADD]
     - YES -> **LIKE SIGNS**: YES -> join; NO -> [ADDER CARRY IN 56.23.01] -> join ->
       [TON PL2 56.11.06] -> [PERFORM ADD]
Both branches -> bus -> ARROW into **EOC2**
 - NO  -> [WRITE RESULT INTO CD AT BACD] -> **EOC1**
     - NO -> line right, ARROW up the frame's right edge to the top bus = **LOOP: next byte**
     - YES -> **EOC2**: YES -> junction W;  NO -> **EHOM**: YES -> junction W;
              NO -> [TON EOC2 54.38.03]* -> [TON CD CUTOFF 56.21.21]* -> up the frame edge =
              **LOOP again** (the asterisked NOTE: no write after EOC2, cycles for PF CK only).
 - YES -> [INHIBIT WRITE IN TO CD] -> junction W
junction W ->
 - **ADD TO CD** — YES -> **SUR** — NO -> [TOF PL1 PL2 (2G) 56.11.05]. (ADD TO CD NO and SUR YES
   not drawn.)
 - **LIKE SIGNS**
     - YES -> [TOF PL1· PL2. TON S.I.R. 56.11.16]
     - NO  -> **EHOM1**
         - NO  -> [TOF PL1· PL2. TON SUR 56.11.10]
         - YES -> **CARRY**: YES -> [TOF PL1· PL2. TON S.I.R. 56.11.16]; NO -> [TOF PL1· PL2.
           TON SUR 56.11.10]
[TOF PL1·PL2. TON S.I.R.] has NO exit line drawn (z265_mid.png). [TOF PL1·PL2. TON SUR] ->
recomplement setup (Part 5).
DERIVED/uncertain: after EOC1 the loop keeps cycling, with CD cut off and writes inhibited, until
EOC2 or EHOM — "cycles taken for PF CK only" — so the cycle count is set by the longer field, not
by the stored field. Unlike signs + no carry (or EHOM1 = NO) -> the CD result is in complement form
-> recomplement.

#### Part 5 — recomplement of CD (b_3300_1000, b_2450_1850, b_2450_2550, b_3300_1850, b_3300_2550, z265_recomp.png, z265_mid.png)
[TOF PL1·PL2. TON SUR 56.11.10] -> bus, parallel:
 - [LOAD BACD TO BAER-1 54.22.], [LOAD BAAB TO 127 54.15.02], [TON AB CUTOFF 56.21.11]
 - **SIGNED**: YES -> [LOAD RFL TO FLER-B.S.]; NO -> **BINARY**: NO -> [LOAD RFL TO FLER-B.S.];
   YES -> [LOAD RFL TO FLER-8] (ALD 54.32 between them)
 - **AUM**: YES -> [TON CD CUTOFF 56.21.21]; "NO (AM)" -> **SIGNED**: NO -> [TON CD COMP 56.21.21];
   unlabeled left exit -> bus
 - [TOF EOC1·EOC2 54.38.03] (no exit drawn)
-> [TOF SUR TON RECOMP 56.11.10] -> junction:
 - **SIGNED** — NO -> line down to the junction above [TON PL1] (skips HSB). (YES not drawn.)
 - **AM+AYM** — YES -> **SIGNED** — YES -> [T OF HSB 56.11.00] (printed "T OF HSB", with a
   space, z265_tofhsb.png; because the column ends with [TOF HSB], DERIVED: probably meant
   "TON HSB") -> parallel:
     - **BINARY**: YES -> [REDUCE RFL BY 8]; NO -> [REDUCE RFL BY BSER] (54.32.01)
     - [REDUCE BACD BY BSER 54.22.02]
     - **AM**: "(AUM) NO" -> bus; unlabeled right exit -> [READOUT SRCD FLAGS AND NOT S TO CD SIGN
       BYTE 56.25.03] and [TON CD COMP 56.21.21]
   -> [TOF HSB 56.11.00] -> junction -> [TON PL1 56.11.06] -> ARROW into **AM**
 - **AM**
     - "(AUM) NO", side label "ZERO CD" -> [READ OUT BYTE AT BACD. CD IS CUT OFF. WRITE ZEROS INTO
       CD.] -> bottom line of the loop (joins after 1ST CYCLE)
     - YES -> [READ OUT CD AT BACD. PUT INTO ADDER COMP.] -> junction above **1ST CYCLE**
 - **1ST CYCLE** "PL1 · P̅L̅2̅ YES" (overbar on PL2 printed here)
     - YES -> [CARRY TO ADDER 56.23.03] and [TON PL2 56.11.06] -> bottom line
     - NO  -> bottom line
   bottom line -> ARROW into **EOC1**
     - NO  -> outer line back to the junction above 1ST CYCLE = **RECOMPLEMENT LOOP**
     - YES -> [TON SIR 56.11.16] and [TON PL1· PL2 56.11.05]
As drawn, the loop return lands ABOVE 1ST CYCLE and BELOW the AM / READ OUT boxes: the per-byte
read-complement and its write-back are drawn once, outside the loop line, and no "write CD" box
is in the loop. DERIVED: the read/complement/write must repeat per byte; the drawing simplifies
it. Treat the loop body as uncertain.

#### Part 6 — ending (b_3300_1850, b_4100_1850)
[TON SIR 56.11.16] -> fan:
 [LOAD BAAB TO 10 54.15.01], [LOAD BACD TO 10 54.25.01], [SET INDS 56.52.04 56.52.03],
 [SIR TO LA & PAU 56.42.00], [RESET CTL TRIGS. (SEE ADD)], [TOF SIR 56.11.16]
("SEE ADD" — DERIVED: refers to the RESET: list on Fig 3.11.9.)

#### Fig 3.11.11 — summary
- Per-byte loop: one pass round the frame per byte; 8 bits (binary; or RFL for the last partial
  byte: "BY 8 OR RFL") or 4 bits for AB / BSER for CD and RFL (decimal). Exit test EOC1 after the
  CD write, then EOC2/EHOM.
- Store / Store Rounded skip PERFORM ADD: AB (true, complemented, or 0/1/9 fill) plus an optional
  rounding carry passes through the adder and is written into CD; decimal bytes larger than 4 bits
  get zone bits assembled.
- Rounding: a separate single-byte RND cycle before the loop (Part 2); carry saved in CARRY TRIG
  and gated into the adder in the loop.
- Unlike signs: AB is complemented (TON AB COMP); hot 1 = "ADDER CARRY IN" on 1ST CYCLE; at the
  end, unlike signs without carry -> second pass recomplementing CD (Part 5).
- Second memory word / word boundary: **not drawn.** No box names a word fetch or store; the only
  look-ahead items are L. A. GO, L. A. REJECT, LA START, "SIR TO LA & PAU".
- Result return to memory: "WRITE RESULT INTO CD AT BACD" per byte; "INHIBIT WRITE IN TO CD" after
  EOC2. The store of CD back to core is not drawn (DERIVED: look-ahead/memory bus, outside this
  figure).
- Timing: cycle count NOT PRINTED.


## 10. What A3 (`mkSAU`) can build from, figure by figure

**The byte step (all flows).**
- One pass = extract a byte pair at BAAB/BACD through the switch matrices
  (8 of 16 of 128), apply T-C as each flow's CD COMP / AB COMP decision
  says, add (or apply the logic unit, or the decimal corrector), and
  write into AB at BAAB or CD at BACD.
- Step BAAB / BACD / RFL by 8 (binary), by RFL (partial byte), or by
  BSER (decimal; BAAB by 4).
- **Rate: 0.6 µs = 2 model clocks a pass** (Buchholz p.209, PRINTED; Perf.
  Char. Table 3's .6 per byte). This is the rate `NEXT.md` "THE BINARY
  ADD'S BOX HOLD" says `decDigitsPerCycle` departs from.
- Tested at each pass: EOC1/EOC2 (end of field), EOA1/EOA2 (end of
  accumulator), CD CUTOFF / AB CUTOFF (fill 0s, 1s or 9s), EHOM1/EHOM2.

**Per figure:**
- **3.11.9 (+, +MG, L, LWF), Appendix E.**
  1. Start-up; wait on LA GO.
  2. If signed, an HSB sign-byte pass.
  3. The PL1/PL2 byte loop: first pass injects "HOT 1 TO SAU ADDER" on
     unlike signs; "PERFORM ADD OF CD AND AB. WRITE RESULT INTO AB AT
     BAAB IF NOT EOA2".
  4. After EOC1: carry-propagation passes while CARRY; EOA1; EHOM1; AU
     (zero AB).
  5. The recomplement: a separate pass over AB from "BAAB TO 127", one
     byte a pass. Not printed: the priority between two parallel end
     tests (Appendix E).
- **3.11.11 (M+, M+MG, ST, SRD), Appendix E.**
  - Roles swap: AB is complemented, and the result is written into CD at
    BACD.
  - ST/SRD skip the add.
  - SRD has a single-byte rounding pre-pass (ADD 1 binary / ADD 4 decimal
    TO BAAB, HOT 1 or HOT 4 & 1, CARRY TRIG).
  - Passes after EOC2 are taken "FOR PF CK ONLY" with the write
    inhibited.
  - The CD recomplement is a second pass, whose per-byte body is
    uncertain as drawn.
  - The word-boundary crossing is **not drawn** (Gaps).
- **3.11.2 (M+1), Appendix D.** The add-1 loop: first pass "GATE O'S TO
  ADDER FROM AB" plus carry-in; exits early on like signs with no carry.
  SUR → RECOMP·HSB / RECOMP·PL1 → recomplement loop.
- **3.11.12 (K family), Appendix C.** The byte loop with "PERFORM ADD BUT
  NO WRITE IN". Indicators AE/AH/AL; "SAU SET COMP RSLT INDS TO LA".
  Early exit on inequality (DERIVED from wire tracing, spot-check
  z266_mid before building on it).
- **3.11.3-3.11.7, 3.11.13, 3.11.14 (transit, LFT, conversions),
  Appendices C, D.**
  - Three-loop shape: bytes into PAU F (CD-FLO / CD-FHI); one digit (4
    bits) or one bit a pass into the PAU with a "CONVERT ... SIGNAL TO
    PAU"; results out of F 8 bits a pass (F-CD / F-ABOS) until F1-97 is
    zero (data-dependent).
  - Table 3's equations match these loops term by term (§5).
  - **Absorbs `mkCvtBox`.** `cvtBitsPerCycle = 16` is not the drawn rate:
    the drawn rate is one bit (B→D) or one digit (D→B) a pass.
- **3.11.1, 3.11.8, 3.11.10 (VFL *, /, *+), §4.** The SAU's half:
  - operand assembly into F a byte a pass;
  - "PAU START ...", then wait on the PAU;
  - unload (DIV 5-6) or add the product into AB (PL1/PL2).
- **3.8.x exponent lanes.** The SAU adder serves the PAU's exponent
  arithmetic in the same periods (every 3.8 chart). In a two-module
  build this is a port the PAU drives, not an SAU instruction.

**Missing for A3.**
- The clock count of the setup and end boxes. Every flow box is a level
  or a trigger, with no time. Table 3's constants (pre-execution 1.8 or
  2.4, termination .6) are the only source.
- The per-pass count is printed (0.6 µs).

## 11. What A4 (`mkPAU`) can build from, figure by figure

All figures are timing charts with numbered FP CLOCK periods, so each is
a per-clock table (Appendices A-C and §4).

**Shared primitives** (seen on every chart):
- **T0 start:** (START CTRL) T0, SAMPLE TO C & EXECUTION REGS, FIRST CYCLE
  TGR.
- **The right pre-shift loop:** T4 repeated while SHIFT CTR > 4, 4 places
  a period; 3.8.2, 3.8.6.
- **The left normalization loop:** T3, then T4/TC, two periods a pass of
  up to 6; exit "(T3, NE, SH≤6) END OP", else "(T4, NOT END OP, NOT INT)
  T3".
- **The end period:** LATCH ACOB, EXP LATCH, EXP SAMPLE, A REG sample.
  GATE 11 & 12 straddles it.
- **The exponent lane,** one period behind the adder lane through the SAU
  adder ("EXPONENT LOOP n" lags "ADDER LOOP n"; 3.8.1).

**Per figure:**
- **3.8.1 L, 3.8.7 ST, 3.8.12 LMR, 3.8.14 SMR:** T0, then normalization
  pairs. 2 + 1 + 2/norm; matches Table 2.
- **3.8.2 +, 3.8.3 +MG, 3.8.4 K, 3.8.5 F+:**
  - T0, T1, T2, the pre-shift loop, then normalization.
  - The PSA, PERFORM AUGMENT and TPB triggers carry the sign and
    recomplement cases.
  - "SN ? 3" and "SHIFT ? 3" relation glyphs are ILLEGIBLE on 3.8.3 and
    3.8.4; 3.8.2 prints "PRE SHIFT > 3".
- **3.8.6 SHF:** the shift-counter "TO 8 / TO 4 / TO 0" stepping.
  "(T4 .PSA , SH, CTR = 4)" is printed where "> 4" would be expected; it
  is recorded as printed.
- **3.8.8 SRD:** "ADD "1" TO POS 50", "SUPPRESS ADDER OUTPUT 50 & 51".
  Three periods against Table 2's four (§3).
- **3.8.9 SLØ:** T0 loads 48 into the shift-counter adder. Then a T3,T4
  shift loop runs, with a break mark eliding its middle. Then
  normalization and END OP. Build the loop from the shift counter, and
  take the total from Table 2 (§3 note a).
- **3.8.10 SRT:**
  - the PAU part is 0-3 on FP CLOCK;
  - the root development is "UNDER SAU CONTROL" on A PULSES: RFL 47 by 2
    (C bit pairs), SCR 96 by 2 (48 root bits), "B TIMED SCR=0" → "(PAU
    RESUME CONTROL)";
  - with `clock_unit.md` §4.4 (A period = 2 clocks) this sums to Table
    2's 108;
  - it belongs to both units, "in unison" (Buchholz p.208).
- **3.8.11 * (and D*):**
  - The MR1/MR2 ring, then CSA LOOPS I-IV (12 multiplier bits each,
    overlapped about one a period), then the MAIN ADDER LOOP (periods
    6-7), then normalization. END OP at 8.
  - 5 + 4 = 9 matches Table 2.
  - The CSA count is fixed at four; only normalization is data-dependent.
- **3.8.13 *+:** the multiply ring, then the add from period 8 by PSA (main
  path, END OPN at 10) or CMPSE (the alternative, "IF ACCUMULATOR
  EXPONENT IS SMALLER", END OPN at 13). It conflicts with Table 2's 20
  (§3 note b).
- **3.8.15 / (sheets 1-3) and 3.8.16 D/ (§4):**
  - Parts A/B: pre-normalization, D3/D4 pairs, two periods a shift of
    six.
  - Parts E/F/G: zero divisor 1-4; zero dividend returns to point 9;
    unnormalized dividend returns to point 11.
  - Part C/D: the trial, intermediate and last reduction cycles, with
    the multiple chosen by Buchholz Fig. 14.11 and the quotient bits by
    Fig. 14.12 (§2 item 5). END OP at 22; +2 for "Add Back 1x Divisor".
  - D/ continues per §7.
- **3.8.17 E+ / E+I:** T0, T1, T2, MR3, then normalization pairs. END OP
  at 7 for two sequences (4 + 2 per sequence, DERIVED). Matches Table 2.
- **3.8.18 / 3.8.19:** the VFL entry and exit to the multiply and divide
  sequences (§6).
- **3.8.20 R/:**
  - The preamble T0, MR1, MR2, MR3, T1, D3 (periods 0-5) interchanges
    the operands: "C FRACTION TO A REG", "A EXP TO D REG", "C EXP TO A
    REG", "A FRACTION TO ADDER".
  - Then "IDENTICAL TO DIVIDE (POINT 3) FROM THIS POINT". Matches Table
    2's `/` + 4.
  - A zero-divisor sub-chart has its own 3-pulse axis; its alignment is
    NOT PRINTED.

## 12. Gaps: not printed anywhere that was looked

| gap | where looked |
|---|---|
| **A logical-connective (C, CM, CT) flow or timing chart.** | Index 3-2 in full (PDF 52-60): no title names a connective. Category 11's 14 titles all name arithmetic, transit or convert. 3.11.9, 3.11.11 and 3.11.12 were read in full: no connective branch. Fig. 3.9.9 SAU Error (PDF 252, read at 200 dpi) has only the duplicate logic-unit check ("COMPARE LU 1 BITS 0-8 WITH LU 2 BITS 0-8"). An OCR sweep of R23-9732 for CONNECT / LOGIC / CONNECTIVE found only scan-card table entries, "SAU LOGICAL UNIT COMPARISON ERROR TRIGGER" and "PARTIAL FIELD CONNECT TRIGGER" (OCR of PDF 162-163, finding aid only, not read at the image). Figs 3.2.8-3.2.10 (the LA's VFL figures) were not re-read for this; `NEXT.md` records them as the transfer to the SAU. **Only Table 3's .6(x/y) and Buchholz p.208-209 ("logical-connective operations are executed by the serial unit"; Fig. 14.6's "Logic unit") describe them.** |
| **A decimal add or decimal-correction timing chart.** | Decimal appears in the flows only as BIN/DEC branches (4 vs 8 bits, nines vs ones fill, "ASSEMBLE ZONE BITS TO SATISFY BYTE SIZE"). Fig. 14.6 draws the "Decimal corrector". No decimal-correction box or time is on any sheet. |
| **Decimal multiply and divide.** | 3.11.3's title includes them. The flow only loads the operand into the PAU (shift counter 96/92) and unloads it. No multiply step is drawn, and no multiplier is named on any 3.11 sheet. Buchholz p.208: "Decimal multiplication and division are not built in" (1962 text). How the 1/1/63 machine executes them is **not printed** here. |
| **Any time on an SAU flow.** | All 14 sheets of category 11 (no clock, no A/B pulse, no cycle number). The only per-step time is Buchholz p.209's 0.6 µs and Table 3's .6. Setup and termination boxes are untimed except through Table 3's constants. |
| **The VFL field crossing a word boundary inside the SAU.** | Not drawn on 3.11.9 or 3.11.11. The look-ahead appears only as LA GO / LA REJECT / LA START / "SIR TO LA". BAAB/BACD loaded to 127 / 64-1 suggests a two-word, 128-bit window (DERIVED). The fetch of the second word is the LA flows' (Fig. 3.1.24, per NEXT.md), outside this spec. |
| **A per-cycle table for 3.8.15 sheet 2 (periods 9-21) and for 3.8.19.** | Reused from `ebox_roadmap.md` as extracts, per the brief. Neither has a period-by-period transcription here. Sheet 2's periods 20-25 were re-read (§4). |
| **Whether the SDC is a loop.** | 3.8.15 sheet 2 (re-read only at 20-25), 3.8.16, 3.8.20. Not settled (§7). |
| **`*+`'s 20 against 11/14.** | 3.8.13, Table 2. Unresolved (§3). (SLØ's apparent gap is the break mark on 3.8.9, §3 note a.) |
| **The 3.8.20 zero-divisor sub-chart's place on the main clock.** | 3.8.20 itself; its start condition names D4, which is not on the sheet. |
| **The opcode legends' overbars on 3.11.9 and 3.11.11.** | ILLEGIBLE: M+ and M+MG print identically, so a bar was lost in printing (Appendix E). |

