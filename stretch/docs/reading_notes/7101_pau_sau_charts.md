> **STATUS: UNVERIFIED FINDING AID.** Written by a reading agent on 2026-11-15
> from page images. Nothing here may be cited as a source: every quote must be
> re-read in the ink (the page image) before it is relied on, as AGENTS.md
> requires. Passages the agent could not read confidently are listed at the end.

# Reading notes: 7101 CPU CE manual, PAU/SAU timing charts (Figures 3.8.1 - 3.8.19)

Source: `stretch/docs/R23-9732_Manual04_7101_CPU_Jan63.pdf`, section M3-04-3,
running head "PAU TIMING CHARTS". Read from page images rendered with
`pdftoppm -gray` at 180-300 dpi and cropped; nothing below comes from OCR.

## 0. Conventions, and what "p.225" means

**Page numbering.** `source_audit.md`'s "pp.225-243" are **PDF page numbers**.
PDF 224 carries the printed footer "7-20" (Table 3.7.16) and PDF 225 carries
"8-1" (Figure 3.8.1). Printed numbering in this volume is section-local
(`8-n` inside M3-04-3), so no printed "225" exists in this range. I used PDF
pages throughout and give the printed footer beside each.
The "PDF page == printed page" statement in `source_audit.md` (line ~277) is
about the two editions of `C22-6728`, not this PDF. Audit 3's
"CORRECTION TO THIS FILE'S OWN METHOD" is about citation density, not about
page numbering; I found no page-numbering correction for R23-9732 in
`source_audit.md`.

**PDF -> printed map, read from the footers** (fold-outs carry double numbers):

| PDF | printed | figure(s) |
|---|---|---|
| 225 | 8-1 | 3.8.1 FP Load |
| 226 | 8-2 | 3.8.2 FP Add |
| 227 | 8-3 | 3.8.3 FP Add to Magnitude |
| 228 | 8-4 | 3.8.4 FP Compare |
| 229 | 8-5 | 3.8.5 FP Add to Fraction |
| 230 | 8-6 | 3.8.6 FP Shift Fraction |
| 231 | 8-7 | 3.8.7 FP Store AND 3.8.8 FP Store Rounded (one landscape page) |
| 232 | 8-8 | 3.8.9 FP Store Low Order |
| 233 | 8-9 | 3.8.10 Store Root sheet 1 (landscape) |
| 234 | 8-10 | 3.8.10 Store Root sheet 2 |
| 235 | 8-11 | 3.8.11 FP Multiply |
| 236 | 8-12 | 3.8.12 FP Load Multiplier Register |
| 237 | 8-13/8-14 | 3.8.13 FP Multiply and Add (fold-out) |
| 238 | 8-15 | 3.8.14 FP Store Multiplier Register |
| 239 | 8-16 | 3.8.15 FP Divide sheet 1 (Parts A, B) |
| 240 | 8-17/8-18 | 3.8.15 FP Divide sheet 2 (Parts C, D; chart drawn rotated 90 deg) |
| 241 | 8-19 (left) and 8-21 (right) | 3.8.15 FP Divide sheet 3 (Parts E, F, G; drawn rotated) and 3.8.17 FP Add to Exponent |
| 242 | 8-22 (left) and 8-20 (right) | 3.8.18 SAU Multiply / Multiply and Add, PAU section, and 3.8.16 FP Divide Double |
| 243 | 8-23 (dated 1/1/63) | 3.8.19 SAU Divide |
| 244 | 8-24 (dated 1/1/63) | 3.8.20 FP Reciprocal Divide -- a twentieth chart, one page past the stated range |
| 245 | 9-1 | Figure 3.9.1 IC ERROR: next section, not a timing chart |

Every footer in this table was read from the page image. Printed order is
scrambled against PDF order on PDF 241-242 (8-19/8-21, then 8-22/8-20), as
`ebox_roadmap.md` already warns. That file says 3.8.15 sheet 3 is the rotated
one; in fact BOTH sheet 2 (PDF 240) and sheet 3 (PDF 241 left) are drawn
rotated 90 degrees. It also lists PDF 232 with no printed number; it is 8-8.

**What the charts are.** They are waveform charts, not step lists: an `FP CLOCK`
square wave with numbered rising edges across the top, and below it one line per
ring trigger / control trigger / gate / latch-sample pulse, each drawn high
for the periods it is on, with its set condition printed in parentheses at its
rising edge.

**My row convention.** "Period n" = from the rising edge labelled n to the
rising edge labelled n+1 (one full high+low of FP CLOCK). "1st half" = the high
half of the period, "2nd half" = the low half. Edge positions were read against
the clock row by x-position in full-width crops; where a pulse edge fell
between clock edges I say "1st half"/"2nd half"/"mid", and those are the
places most worth re-checking.

**Clock phase.** **None of the FP CLOCK charts shows A/B phase.** Only
Fig 3.8.10 sheet 1 (right panel) draws `A PULSES`, and one line there is
labelled `B TIMED`. Every "phase" cell below is therefore "not shown" unless
stated. No chart prints a period in time units; the only time figure in the
range is NOTE 2 on 3.8.15 sheet 3 (quoted in sec. 15).

**"&" in IBM's lettering** is drawn as a script ampersand that looks like
"E"/"4"/"f" in places; I transcribe it as `&`. Overbars are written `NOT x`
or `x-bar`.

**Totals.** For each chart I give (a) the drawn example: number of FP CLOCK
periods from T0 through the period in which `END OP` is up, inclusive, and the
period in which the result latches (`LATCH ACOB`, `EXP LATCH`) follow; (b) the
straight-line case only when the chart's own loop conditions show what one
loop costs. The chart origin (period 0 = `START CTRL` -> `T0`) is NOT shown to
be the same origin as Perf. Char. Table 2's "pre-execution + execution"; that
alignment is not printed anywhere in these pages.

---

## 1. Figure 3.8.1 FLOATING-POINT LOAD (TIMING) -- PDF 225, printed 8-1, dated 2/1/62

Header, verbatim: "EXAMPLE SHOWS TWO NORMALIZATION SEQUENCES. LOAD WITH FLAG IS
THE SAME EXCEPT FLAG BITS ROUTED TO SIGN BYTE REGISTER ON LAST SAMPLE."

FP CLOCK edges numbered 0-6.

| period | ring triggers up (set condition) | rises / pulses in this period | falls at end of period |
|---|---|---|---|
| 0 | `T0` (START CTRL) | `SAMPLE TO C & EXECUTION REGS.` (START CTRL), 1st half only; `FIRST CYCLE TGR` (FCT) (START CTRL); `GATE 33` (FCT, LD); `EXPONENT ROUTING CONTROL TGR` (TP6) (FCT, LD) | T0 |
| 1 | `T3` (T0, LD) | `NORMALIZE EXPONENT TGR (NE)` (T0, LD); `GATE 61 & 63 (TGR)` (T0, LD); `WRITE EXPONENT A TGR` (T0, TO ACC) -- stays up to the right edge of the chart; `F REG LATCH & SAMPLE` (T0), 1st half | T3; FIRST CYCLE TGR; GATE 33 |
| 2 | `T4` (T3); `TC` (T3, NE) | `NORMALIZE MANTISSA TGR (NM)` (T3, NE); `GATE 21 & 22 (TGR)` (T3, NE); `SAMPLE TEST COMP`; `F REG LATCH & SAMPLE` (T3, NE), 1st half | T4; TC; SAMPLE TEST COMP; EXPONENT ROUTING CONTROL TGR |
| 3 | `T3` (T4, NOT END OP, NOT INT) | `EXP LATCH` (TC, NM); `EXP SAMPLE` (TC, NM) | T3; EXP LATCH; EXP SAMPLE |
| 4 | `T4` (T3); `TC` (T3, NE) | `END OP (TGR)` (T3, NE, SHIFT <= 6); `F REG LATCH & SAMPLE` (T3, NE), 1st half; `GATE 11 & 12` (END OP, TEST COMP) rises mid-period | T4; TC; END OP; NE; GATE 61 & 63; NM; GATE 21 & 22 |
| 5 | (none drawn) | `LATCH ACOB` (TC, END OP, NOT INT) -- stays up; A REG SAMPLE pulse (TO ACC, T0 [sic, printed "To"] END OP, NOT INT), 1st half; `EXP LATCH` and `EXP SAMPLE` (TC, END OP, NOT INT); GATE 11 & 12 falls mid-period | EXP LATCH; EXP SAMPLE |

Annotations: at the A REG sample, "A REG SAMPLE - SECOND SAMPLE WILL OCCUR IF
THIS IS A DOUBLE OPERATION (FROM A CHECKER)"; at the second EXP LATCH, "ALSO
USED AS INDICATOR LATCH"; at F REG LATCH & SAMPLE, "& (ALSO USED FOR SHIFT
REGISTER)". Bottom braces: `ADDER LOOP 1` (about period 0-1), `ADDER LOOP 2`
(periods 2-3), `EXPONENT LOOP 1` (periods 1-2), `EXPONENT LOOP 2` (periods
3-4, running into 5).

**Loop.** One normalization sequence = `T3` then `T4`+`TC` = 2 periods. It
repeats on `(T4, NOT END OP, NOT INT)`; it ends when `(T3, NE, SHIFT <= 6)`
sets END OP.
**Totals.** Drawn example (two normalization sequences): END OP in period 4,
i.e. 5 periods (0-4), result latches in period 5. Straight-line (one sequence,
shift <= 6), by the chart's own conditions: END OP in period 2, i.e. 3 periods
(0-2), latches in period 3. Each additional normalization sequence: +2 periods.
Dependence on operand: number of normalization sequences (shift > 6 repeats).

---

## 2. Figure 3.8.2 FLOATING-POINT ADD (TIMING) -- PDF 226, printed 8-2, dated 2/1/62

Header, verbatim: "EXAMPLE SHOWS A EXP. > C. C. EXP > A REPRESENTED BY DOTTED
LINES. EXPONENT DIFFERENCE AMOUNT = 11. NO NORMALIZATION."

FP CLOCK edges numbered 0-4 legibly; 5, 6, 7 are faint but the edges are drawn.
Printed under the clock: "PRE SHIFT >3" under period 3, "SHIFT CTR REG >4"
under period 4, "SHIFT CTR REG = 4" under period 5.

| period | ring triggers up (set condition) | rises / pulses | falls at end |
|---|---|---|---|
| 0 | `T0` (START CTRL) | `SAMPLE TOB TO C REG & EXECUTION REG` (START CTRL), 1st half; `FIRST CYCLE TGR` (START CTRL); `GATE A & C EXP TO SAU` (FCT & ADD) | T0 |
| 1 | `T1` (T0 & ADD); `TC` (T0 & ADD) | `PRE SHIFT AND ADD TGR` (T0 & ADD); `LPSE` (T0 & ADD) "(LATE PRE-SHIFT EXPONENT STATUS TGR)"; `GATE` (LPSE) "(GATE INITIAL PRE SHIFT AMOUNT TO SHIFT REGISTER)"; `GATE 3` (LPSE & EXP SUM +) "(C 12-59 TO F 2-49)"; dotted alternative `GATE 1` (LPSE & EXP SUM -) "(A 12-59 TO F 2-49)"; `WRITE EXPONENT A TGR` (T0 & TO ACC OPER) stays up; `EXPONENT ROUTING TGR (TP6)` and `MANTISSA ROUTING TGR`, each with two set labels "(SIGN - ADD)" [dotted] and "(SIGN + ADD)" [solid], stay up; `GATE 31` (NOT MANT ROUTE TGR) "(A [1]2-59 TO ADDER 2-49)" [first digit faint]; dotted `GATE 33` (MANT ROUTE TGR) "(C 12-59 TO ADDER 2-49)"; `F REG LATCH` RESET (T0), 1st half | T1; TC; FIRST CYCLE TGR; GATE A & C EXP TO SAU; LPSE; GATE; GATE 3 / GATE 1 |
| 2 | `T2` (T1 & PSA) | `NORMALIZE EXPONENT TGR` (TC & PSA); `GATE A EXPONENT TO SAU` (NE & NOT TP6); dotted `GATE C EXPONENT TO SAU` (NE [& or =] TP6) [operator uncertain]; `GATE 71 & 72` (T2 & PSA); `GATES 21 & 22 OR 23 (TGR)` (T1 & SIGN MIX T/C); shift-counter line (T2 IN T4 & PSA) "8 IN" "(GATE TO SHIFT COUNTER FROM SAU & ADDER)"; `EXP LATCH` (TC & PSA) | T2; EXP LATCH |
| 3 | `T4` (T2, PSA & SH > 3) | `F REG LATCH` SET (T2, PSA & SH > 3), 1st half; shift-counter line "4 IN"; GATE 71 & 72 continues, marked (T4 & SH>4) | -- |
| 4 | `T4` continues, marked "(SCR > 4)" | `F REG LATCH` SET (T4, PSA & CTR > 4), 1st half; shift-counter line "0 IN" | T4; GATE 71 & 72; shift-counter line |
| 5 | `T3` (T4 & SCR = 4) | `GATE 61 & 63 (TGR)` (T4, PSA & SH = 4) | T3; PRE SHIFT AND ADD TGR; GATE 31 / GATE 33 |
| 6 | `T4` (T3); `TC` (T3 & NE) | `NORM MANT (TGR)` (T3 & NE); `END OPR (TGR)` (T3, NE & SH <= 6); `SAMPLE TEST COMP (TGR)`; `F REG LATCH` SET (T3 & NE), 1st half; `GATE 11 & 12` (END OP, TEST COMP) in 2nd half | T4; TC; NE; GATE A/C EXPONENT TO SAU; GATES 21 & 22 OR 23; GATE 61 & 63; NORM MANT; END OPR; SAMPLE TEST COMP |
| 7 | (none drawn) | `EXP LATCH` (END OP); `EXP SAMPLE` (END OP, NOT INT); `LATCH FRACTION ON ACOB` (TC, TEST COMP, END OP & NOT INT); `SAMPLE TO A REG` (TC & TO ACC), 1st half | -- |

**Reading of the example.** Exponent difference 11 = initial pre-shift (gated
at LPSE in period 1; 3.8.3 and 3.8.4 call this amount "3"/"3 OR LESS") plus two
T4 periods of 4 ("8 IN" -> "4 IN" -> "0 IN"). The split 3+4+4 is my reading of
the "8 IN / 4 IN / 0 IN" labels; the chart does not print "3" on this page.
**Loop.** Pre-shift loop: `T4` held one period per shift of 4 while
(SCR > 4); exits to `T3` on (T4 & SCR = 4). Normalization loop not drawn here
("NO NORMALIZATION"), but END OPR's condition is (T3, NE & SH <= 6).
**Totals.** Drawn example: END OPR in period 6 = 7 periods (0-6); latches in
period 7. Straight-line (pre-shift <= 3, shift <= 6): not drawn on this page;
it is drawn on 3.8.4 (Compare, an add-class instruction) as 5 periods (0-4).
Per additional pre-shift of 4: +1 period (shown: periods 3 and 4).

---

## 3. Figure 3.8.3 FLOATING POINT-ADD TO MAGNITUDE (TIMING) -- PDF 227, printed 8-3, 2/1/62

Header, verbatim: "EXAMPLE SHOWS C EXP > A AND FORCED ZERO FRACTION."
FP CLOCK edges 0-7.

| period | ring triggers up (set condition) | rises / pulses | falls at end |
|---|---|---|---|
| 0 | `T0` (START CTRL) | "(SAMPLE TOB)" (START CTRL), 1st half; `FIRST CYCLE TGR`; `GATE EXPONENTS TO SAU` (FC[T] & ADD) [printed "(FC+ 4 ADD)"; uncertain] | T0 |
| 1 | `T1` (T0 & ADD); `TC` (T0 & ADD) | `PRE-SHIFT & ADD TGR` (T0 & ADD); `LPSE` (T0 & ADD); `GATE` (LPSE) "(GATE TO SHIFT REGISTER AMOUNT = 3)"; `GATE 1` (LPSE & EXP SUM -); `WRITE EXPONENT A TGR` (T0 & TO ACC OPER) stays up; `TPB TGR` [so printed; uncertain: TP6?] (EXP SIGN - & ADD); `MANTISSA ROUTING TGR` (EXP SIGN - & ADD) stays up; `GATE 33` (MANT ROUTE TGR & PSA); `F REG LATCH` RESET (T0), 1st half | T1; TC; FIRST CYCLE TGR; GATE EXPONENTS TO SAU; LPSE; GATE; GATE 1 |
| 2 | `T2` (T1 & PSA) | `NORMALIZE EXPONENT TGR` (TC & PSA); `GATE C EXP TO SAU` (NE & TP6); `GATE 71 & 72` (T2 & PSA); `GATES 21 & 22 OR 23` (T1 & SIGN MIX T/C); `EXP LATCH` (TC & PSA) | T2; GATE 71 & 72; EXP LATCH |
| 3 | `T3` (T2, PSA & SN=3) [so printed; probably SH = 3; uncertain] | `GATE 61 & 63` (T2 PSA & SHIFT = 3) | T3; PRE-SHIFT & ADD TGR; TPB TGR -- its fall annotated "(1 PERFORM AUGMENT TGR & TO ALL OPER)" [uncertain reading]; GATE 33; GATE C EXP TO SAU |
| 4 | `TC` (T3 & NE); `T4` (T3) | `GATE A EXP TO SAU` (NE & NOT TP6); `NORMALIZE MANTISSA TGR` (T3 & NE); `PERFORM AUGMENT (TGR)` (TP6, T3, NE, SIGNS UNLIKE, RESULT TGR); `F REG LATCH` SET (T3 & NE), 1st half | TC; T4; GATE 61 & 63 -- fall annotated "(PERFORM AUG & T4)" |
| 5 | `T3` (T4 - NOT END OP) | -- | T3; PERFORM AUGMENT |
| 6 | `TC` (T3 & NE); `T4` (T3) | `END OP (TGR)` (T3 PERFORM AUG); `F REG LATCH` RESET (T3 & NE), 1st half; `GATE 11 & 12` (END OP & TST COMP) in 2nd half | TC; T4; NE; GATE A EXP TO SAU; GATES 21 & 22 OR 23; NM; END OP |
| 7 | (none drawn) | `EXP LATCH` (END OP); `LATCH FRACTION ACOB`; (SAMPLE TO A REG), 1st half; both braced "0'S"; GATE 11 & 12 falls mid-period | -- |

Also printed: "EXPONENT SAMPLE (NONE)".
**Totals.** Drawn example (pre-shift amount = 3, then a forced-zero-fraction
"perform augment" second pass): END OP in period 6 = 7 periods (0-6); latch in
period 7. The second T3/T4 pass (periods 5-6) is the PERFORM AUGMENT pass, not
a normalization repeat. Straight-line for M+ without augment: not drawn here.

---

## 4. Figure 3.8.4 FLOATING-POINT COMPARE (TIMING) -- PDF 228, printed 8-4

Caption, verbatim: "FIGURE 3.8.4. FLOATING-POINT COMPARE (TIMING)". Dated
2/1/62. The clock row here is
labelled `CLOCK`, not `FP CLOCK`. Edges 0-5.

Header, verbatim: "ALL INSTRUCTIONS CHART DETAILS A EXP > C EXP BY 3 OR LESS.
CHART DEALS WITH COMPARE. (1) COMPARE FOR RANGE AFFECTS INDICATOR SETTING ONLY.
(2) COMPARE MAGNITUDE AFFECTS SIGN MOD ONLY. (3) COMPARE MAGNITUDE FOR RANGE,
(1) AND (2) ABOVE."
Footnote, verbatim: "NOTE: THE CHART SHOWS SEVERAL OPERATIONS OCCURRING AS A
RESULT OF DECODED ADD CLASS INSTRUCTIONS. COMPARE IS AN ADD CLASS INST. AND
THEREFORE USES MANY CONTROL LINES (USED ALSO FOR ADD)."

| period | ring triggers up (set condition) | rises / pulses | falls at end |
|---|---|---|---|
| 0 | `T0` (START CTRL) | `SAMPLE TOB TO C & EXECUTION REG.` 1st half; `FIRST CYCLE TGR`; `GATE A & C EXP TO SAU` (FCT & ADD) | T0 |
| 1 | `T1` (T0 & ADD); `TC` (T0 & ADD) | `PRE-SHIFT AND ADD TGR` (T0 & ADD); `LPSE` (T0 & ADD); `GATE` (LPSE) "(GATE SHIFT AMOUNT TO SHIFT REG)"; `GATE 3` (LPSE + SUM +) "(C 12-59 TO F 2-49)"; `EXPONENT ROUTING TGR (TP6)` and `MANTISSA ROUTING TGR`, set label "(SIGN + ADD)" with dotted alternative; `GATE 31` (PSA AND NOT MANTISSA ROUTE) "(A 12-59 TO ADDER 2-49)"; `F REG LATCH` RESET (T0), 1st half | T1; TC; FIRST CYCLE TGR; GATE A & C EXP TO SAU; LPSE; GATE; GATE 3 |
| 2 | `T2` (T1 & PSA) | `NORMALIZE EXPONENT TGR` (T0 & PSA) [so printed; other charts print TC & PSA; uncertain]; `GATE A EXP TO SAU` (NE & NOT TP6); `GATE 71 & 72` (T2 & PSA); `GATE 21 & 22 OR 23 (TGR)` (T1 & SIGN MIX T/C); `EXP LATCH` (TC & PSA) | T2; GATE 71 & 72; EXP LATCH |
| 3 | `T3` (T2, PSA & SH <= 3) | `GATE 61 & 63 (TGR)` (T2, PSA, & SH = 3) [printed "SH=3" here vs "SH <= 3" on the ring row] | T3; PRE-SHIFT AND ADD TGR; GATE 31 |
| 4 | `T4` (T3); `TC` (T3 & NE) | `NORM MANT (TGR)` (T3 & NE); `END OP (TGR)` (T3, NE, & SH <= 6); `SAMPLE TEST COMP (TGR)`; `F REG LATCH` SET (T3 & NE), 1st half; `GATE 11 & 12` (END OP & TEST COMP) in 2nd half | T4; TC; NE; GATE A EXP TO SAU; GATE 21 & 22 OR 23; GATE 61 & 63; NORM MANT; END OP; SAMPLE TEST COMP |
| 5 | (none drawn) | "(END OP) OP LATCH" [so printed; sits on the EXP LATCH row; uncertain whether "EXP LATCH"]; `LATCH FRACTION (ACOB)` (TC, END OP, NOT INT); `INDICATOR LATCH` (END OP T0 & NOT INT); "(IND SAMPLE)" pulse, 1st half, condition "(END OP, TC, NOT INT & DECODED K OR KMG OR DECODED KR OR KMGR AND AH ON)" | -- |

Also printed: "EXP SAMPLE (NONE)", "SAMPLE ACOB (NONE)".
**Totals.** END OP in period 4 = 5 periods (0-4); latches/indicator sample in
period 5. This is the straight-line add-class case (pre-shift <= 3, shift
<= 6). No loop drawn.

---

## 5. Figure 3.8.5 FLOATING-POINT ADD TO FRACTION (TIMING) -- PDF 229, printed 8-5

Header, verbatim: "EXAMPLE SHOWS 2 NORMALIZATION CYCLES. NOTE: NO EXPONENT ADD
OCCURS; THIS RESULTS IN A ZERO EXPONENT DIFFERENCE CAUSING A ZERO PRE-SHIFT."
Edges 0-7. Under the clock: "PRE-SHIFT <= 3" (period 3), "SHIFT > 6" (period
4), "SHIFT <= 6" (period 6).

| period | ring triggers up (set condition) | rises / pulses | falls at end |
|---|---|---|---|
| 0 | `T0` (START CTRL) | `SAMPLE TO C AND EXECUTION REGS` 1st half; `FIRST CYCLE TGR` | T0 |
| 1 | `T1` (T0, ADD); `TC` (T0, ADD) | `PRE-SHIFT & ADD TGR` (T0, ADD); `LPSE` (T0, ADD) "(LATE PRE SHIFT EXP STATUS TGR)"; `EXPONENT ROUTING CONTROL TGR (TP6)` and `MANTISSA ROUTING TGR` (EXPONENT SUM + ADD, FCT) [dotted set; lines run the whole chart]; `WRITE EXPONENT A TGR` (T0, TO ACC, NOT DIVIDE) stays up; `GATE 3` (LPSE EXP SUM +); `GATES 31 & 32` (NOT MANTISSA ROUTE, PSA, [OP?]) [last term illegible]; F REG LATCH pulse (T0), 1st half | T1; TC; FIRST CYCLE TGR; LPSE; GATE 3 |
| 2 | `T2` (T1, PSA) | `NORMALIZE EXPONENT TGR` (TC, PSA); `GATE A EXPONENT TO SAU` (NE, NOT TP6); `GATES 21 & 22 OR 23 (TGR)` (T1, PSA, SIGN MIX T/C); `EXP LATCH` (TC, PSA) | T2; EXP LATCH |
| 3 | `T3` (T2, PSH [so printed], SH <= 3) | `GATE 61 & 63 (TGR)` (T2 PSA, PRE-SH <= 3) | T3; PRE-SHIFT & ADD TGR; GATES 31 & 32 |
| 4 | `T4` (T3); `TC` (T3, NE) | `NORMALIZE MANTISSA TGR` (T3, NE); F REG LATCH pulse (T3, NE), 1st half | T4; TC |
| 5 | `T3` (T4, NM, NOT END OP) | `EXP LATCH` (TC NM); `EXP SAMPLE` (TC, NM, NOT INT) | T3; EXP LATCH; EXP SAMPLE |
| 6 | `T4` (T3); `TC` (T3, NE) | `SAMPLE TEST COMP`; `END OP` (T3, NE, SH <= 6); F REG LATCH pulse (T3, NE), 1st half "F REG LATCH ALSO SHIFT REG"; `GATE 11 & 12` (TEST COMP END OP) in 2nd half | T4; TC; NE; GATE A EXPONENT TO SAU; GATES 21 & 22 OR 23; GATE 61 & 63; NM; SAMPLE TEST COMP; END OP |
| 7 | (none drawn) | `LATCH DATA ACOB` (TC, TEST COMP, END OP, NOT INT); `SAMPLE TO A REG` (TC & TO ACC), 1st half; `EXP LATCH`, `EXP SAMPLE` (TC END OP, NOT INT) | -- |

Annotation: "NOTE: SECOND SAMPLE FOR DOUBLE PRECISION NUMBER IS UNDER CHECKER
CTRL".
**Loop.** Normalization cycle = T3 then T4+TC (2 periods), repeating on
(T4, NM, NOT END OP).
**Totals.** Drawn example (2 normalization cycles): END OP in period 6 = 7
periods; latches in period 7. One normalization cycle (shift <= 6): 5 periods
(0-4) by the chart's loop structure. +2 periods per extra normalization cycle.

---

## 6. Figure 3.8.6 FLOATING-POINT SHIFT FRACTION (TIMING) -- PDF 230, printed 8-6

Caption, verbatim: "FIGURE 3.8.6. FLOATING-POINT SHIFT FRACTION (TIMING)".
Header, verbatim: "EXAMPLE SHOWS WHERE SHIFT>3 BUT<12 EXPONENT SIGN +, SHIFT
LEFT. EXPONENT SIGN -, SHIFT RIGHT." Edges 0-7.

| period | ring triggers up (set condition) | rises / pulses | falls at end |
|---|---|---|---|
| 0 | `T0` (START CTRL) | "(SAMPLE TO C & EXECUTION REGISTERS)" 1st half; `FIRST CYCLE TGR`; `GATE C EXP TO SAU` (FCT, SHF); `EXPONENT ROUTING TGR (TP6)` (DECODED SHF) [dotted set, runs whole chart] | T0 |
| 1 | `T1` (T0, SHIFT); `TC` (T0, SHIFT) | `PRE SHIFT & ADD TGR` (T0, SH); `LPSE` (T0, SH) "(LATE PRE-SHIFT EXPONENT STATUS TGR)"; `GATE` (LPSE & SAU SIGN) "(GATE INITIAL SHIFT AMOUNT TO SHIFT REG RIGHT OR LEFT)"; `GATE 1 & 2` (LPSE, SHF); `WRITE EXPONENT A TGR` (T0 TO ACC NOT DIVIDE) stays up; "(PSA) (ALLOW SUBTRACTION OF SHIFT AMOUNT FROM SH CTR REG)"; F REG SAMPLE GATE pulse (T0) and SHIFT CONTROL REG SAMPLE GATE pulse (T0) "TO INITIAL SHIFT AMOUNT", 1st half | T1; TC; FIRST CYCLE TGR; GATE C EXP TO SAU; LPSE; GATE; GATE 1 & 2 |
| 2 | `T2` (T1, PSA) | `GATE` (T2, PSA) "(GATE REMAINING SHIFT AMOUNT TO SHIFT COUNTER REG)"; `NORMALIZE EXPONENT TGR` (TC, PSA); `GATE 21 & 22 (TGR)` (LPSE, SHF); `GATE 71 & 72` (T2, PSA); `GATE A EXP TO SAU ADDER` (NE, NOT TP6); `EXP LATCH` (TC, PSA) | T2; GATE (remaining shift); EXP LATCH |
| 3 | `T4` (T2, PSA, SH > 3) | SET SHIFT COUNTER REG (PSA T2) "TO 8" (SHIFT CTR REG SAMPLE GATE), 1st half; F REG SAMPLE GATE pulse (T2 SH>3 PSA); SHIFT CONTROL REG SAMPLE GATE pulse (T2 SH>3 PSA) "TO RIGHT OR LEFT 4"; GATE 71 & 72 continues, marked (T4 SHIFT CTR > 4) | -- |
| 4 | `T4` continues (T4, PSA, SH, CTR [op illegible; "≠ 4" or "> 4"] 4) | shift counter "(PSA T4) TO 4", 1st half; F REG SAMPLE GATE pulse (T4 PSA) | T4; GATE 71 & 72 |
| 5 | `T3` (T4, PSH [so printed], SH CTR = 4) | `GATE 61 & 63 (TGR)` (T4, PSA, SH CTR = 4); shift counter "(PSA T4) TO 0", 1st half; F REG SAMPLE GATE pulse (T4 PSA) | T3; PRE SHIFT & ADD TGR; "(ALLOW SUBTRACTION ...)" |
| 6 | `T4` (T3); `TC` (T3, NE) | `NORM MANT (TGR)` (T3, NE); `SAMPLE TEST COMP`; `END OP` (T3, NE, NORM, SH <= 6); F REG SAMPLE GATE (T3 NE); SHIFT CONTROL REG SAMPLE GATE (T3, NE) "NORMALLY USED FOR NORMALIZATION"; `GATE 11 & 12` (END OP, TEST COMP) in 2nd half | T4; TC; NE; GATE 21 & 22; GATE A EXP TO SAU ADDER; GATE 61 & 63; NORM MANT; END OP |
| 7 | (none drawn) | `LATCH ACOB` (TC, TEST COMP, END OP, NOT INT); `SAMPLE TO A REG` (TC, TO ACC), 1st half; `EXP LATCH`, `EXP SAMPLE` (END OP TC, NOT INT) | -- |

**Totals.** Drawn example (shift > 3 but < 12: counter 8 -> 4 -> 0, two T4
periods then T3): END OP in period 6 = 7 periods; latches in period 7. +1
period per shift of 4 (the T4 hold), as on 3.8.2. Shift <= 3 case: not drawn.

---

## 7. Figure 3.8.7 FLOATING-POINT STORE (TIMING) -- PDF 231 (left half), printed 8-7

Header, verbatim: "EXAMPLE SHOWS 2 NORMALIZATION CYCLES." Edges 0-6.

| period | ring triggers up (set condition) | rises / pulses | falls at end |
|---|---|---|---|
| 0 | `T0` (START CTRL) | "SAMPLE TO EXECUTION REG)" 1st half; `FIRST CYCLE TGR` (FCT); `GATE 31` (STORE, FCT) | T0 |
| 1 | `T3` (T0, ST) | `NORMALIZE EXPONENT TGR` (T0 STORE); `GATE 61 & 63 (TGR)` (T0 STORE); `WRITE EXPONENT C TGR` (T0, TO MEM); `F REG LATCH & SAMPLE` (T0), 1st half | T3; FIRST CYCLE TGR; GATE 31 |
| 2 | `T4` (T3); `TC` (T3, NE) | `NORMALIZE MANTISSA TGR` (T3, NE); `GATE 21 & 22 (TGRS)` (T3, NE); `SAMPLE TEST COMP`; F REG LATCH & SAMPLE (T3, NE), 1st half | T4; TC; SAMPLE TEST COMP |
| 3 | `T3` (T4 NOT END OP, NOT INT) | `EXPONENT ROUTING TGR (TP6)` rises, labelled "(T0 MEM NM, EXP SAMPLE)" [left of it a dotted "(STORE, FCT)" set]; stays up; `EXP LATCH` (TC, NM); `EXP SAMPLE` (TC, NM) | T3; WRITE EXPONENT C TGR; EXP LATCH; EXP SAMPLE |
| 4 | `T4` (T3); `TC` (T3, NE) | `END OP` (T3, NE, SHIFT <= 6); `WRITE EXPONENT D TGR` (END OP, TO MEM) stays up; F REG LATCH & SAMPLE (T3, NE), 1st half; `GATE 11 & 12` (END OP TEST COMP) in 2nd half | T4; TC; NE; GATE 61 & 63; NM; GATE 21 & 22; END OP |
| 5 | (none drawn) | `LATCH ACOB` (TC, END OP, NOT INT) stays up; `EXP LATCH`, `EXP SAMPLE` (TC, END OP, NOT INT) "ALSO USED AS AN INDICATOR LATCH" | -- |

Braces: ADDER LOOP 1 / ADDER LOOP 2, EXP LOOP 1 / EXP LOOP 2 (as on 3.8.1).
F REG LATCH & SAMPLE: "ALSO USED FOR SHIFT REGISTER".
**Totals.** Drawn (2 normalization cycles): END OP in period 4 = 5 periods;
latch in period 5. One normalization cycle: 3 periods (0-2). +2 per extra cycle.

## 8. Figure 3.8.8 FLOATING-POINT STORE ROUNDED (TIMING) -- PDF 231 (right half), printed 8-7

Header, verbatim: "EXAMPLE SHOWS NORMALIZATION SHIFT OF 6 OR LESS". Edges 0-3.

| period | ring triggers up (set condition) | rises / pulses | falls at end |
|---|---|---|---|
| 0 | `T0` (START CTRL) | `SAMPLE OPERATION BITS TO EXECUTION REGISTER` 1st half; `FIRST CYCLE TGR`; `GATES 31 & 32` (SRD & FCT); `GATE 61` (SRD & FCT) [the row is annotated "(61 & 63 TGRS)"; GATE 61 runs periods 0-2, a separate `GATE 63` box only period 2]; `SUPPRESS ADDER OUTPUT 50 & 51` (SRD & FCT); `ADD "1" TO POS 50` (SRD & FCT); `EXPONENT ROUTING TGR (TP6)` (STORE & FCT) [dotted] | T0 |
| 1 | `T3` (T0 & STORE) | `NORMALIZE EXPONENT TGR` (T0 & STORE); `WRITE EXP C TGR` (T0 & TO MEM); F REG SAMPLE pulse, 1st half | T3; FIRST CYCLE TGR; GATES 31 & 32; SUPPRESS ADDER OUTPUT; ADD "1"; WRITE EXP C TGR |
| 2 | `T4` (T3); `TC` (T3 & NE) | `GATE 63`; `WRITE EXP D TGR` (END OP & TO MEM); `NORM MANTISSA (TGR)` (T3 & NE); `GATE 21 & 22 (TGR)` (MANTISSA RESULT TRUE, T3 & NE); `SAMPLE TEST COMP`; `END OP (TGR)` (MANTISSA RESULT TRUE T3, NE & SH <= 6); F REG SAMPLE "SET" pulse, 1st half; `GATES 11 & 12` (END OP & TEST COMP) in 2nd half | T4; TC; NE; GATE 61/63; NORM MANTISSA; GATE 21 & 22; END OP |
| 3 | (none drawn) | `EXP LATCH` (END OP, TC, NOT INT); `EXP SAMPLE` (END OP); `LATCH FRACTION ON ACOB` (TC, TEST COMP, END OP, & NOT INT); `LATCH AND SAMPLE INDICATORS` pulse, 1st half | -- |

**Totals.** END OP in period 2 = 3 periods (0-2); latches in period 3. The
rounding add (`ADD "1" TO POS 50`, `SUPPRESS ADDER OUTPUT 50 & 51`) is drawn in
periods 0-1 under FCT, i.e. inside the same first adder pass, not as an extra
period. Extra normalization: not drawn (END OP condition is SH <= 6).

---

## 9. Figure 3.8.9 FLOATING-POINT STORE LOW ORDER (TIMING) -- PDF 232, printed 8-8

Header, verbatim: "EXAMPLE SHOWS ONE NORMALIZATION SHIFT."
Edges 0-7. **The FP CLOCK row and most level lines have a break mark between
edge 4 and edge 5**: an unstated number of periods is omitted there.

| period | ring triggers up (set condition) | rises / pulses | falls at end |
|---|---|---|---|
| 0 | `T0` (START CTRL) | `SAMPLE TO EXECUTION REGISTER` 1st half; `FIRST CYCLE TGR`; `GATE 32` (SLO FCT); `48 TO SH CTR ADDER` (SLO FCT); `SHIFT CONTROL A` (SLO) -- stays up to end of period 6 | T0 |
| 1 | `T3` (T0 & STORE) | `NORMALIZE EXPONENT TGR` (T0 & STORE); `GATE 61 & 63 (TGR)` (T0 & STORE); `WRITE EXPONENT C TGR` (T0 & TO MEM); "A EXP A INPUT / SHIFT AMOUNT C INPUT SAU" (NE & NOT TP6), up periods 1-2; "LATCH & SAMPLE F REG, SHIFT REG & SHIFT COUNTER REG" pulse (T0), 1st half | T3; FIRST CYCLE TGR; GATE 32; 48 TO SH CTR ADDER |
| 2 | `T4` (T3); `TC` (T3 & NE) | `NORMALIZE MANTISSA TGR` (T3 & NE); `GATE 21 & 22 (TGR)` (MANTISSA RESULT TRUE, T3 & NE); `SAMPLE TEST COMP (TGR)`; "GATE SHIFT COUNTER REG TO SHIFT COUNTER ADDER" (SLO & NM); latch/sample pulse (T3 NE), 1st half | T4; TC; SAMPLE TEST COMP |
| 3 | `T3` (T4 & NOT END OP) | `EXPONENT ROUTING TGR (TP6)` rises, labelled "(TO MEM & EXP SAMPLE)" [dotted "(STORE FCT)" set to its left], stays up; `EXP LATCH` (TC & NE) [so printed]; `EXP SAMPLE` (TC & NM); "C EXP C INPUT & SHIFT AMOUNT A INPUT SAU ADDER" (NE & TP6), stays up | T3; EXP LATCH; EXP SAMPLE |
| 4 | `T4` (T3); `TC` (T3 & NE) | latch/sample pulse (T3 NE), 1st half | (runs into the break) |
| -- break: unstated number of periods omitted -- | | | |
| 5 | `T3` (T4 & NOT END OP) | `EXP LATCH` (TC, NE); `EXP SAMPLE` (TC, NM) | T3; EXP LATCH; EXP SAMPLE; WRITE EXPONENT C TGR |
| 6 | `T4` (T3); `TC` (T3 & NE) | `END OP` (MANTISSA RESULT TRUE, T3, NE, SH <= 6); `WRITE EXP D (TGR)` (END OP TO MEM) stays up; latch/sample pulse (T3 NE), 1st half; `GATE 11 & 12` (END OP & TEST COMP) in 2nd half | T4; TC; NE; GATE 61 & 63; NM; GATE 21 & 22; END OP; SHIFT CONTROL A; GATE SHIFT COUNTER REG TO SHIFT COUNTER ADDER |
| 7 | (none drawn) | `LATCH ON ACOB` (TC, TEST COMP, END OP & NOT INT); `LATCH & SAMP IND` pulse 1st half; `EXP LATCH`, `EXP SAMPLE` (TC, END OP, NOT INT) | -- |

**Loop.** T3 then T4+TC (2 periods), repeating on (T4 & NOT END OP), counter
driven: "48 TO SH CTR ADDER" loads the count and "GATE SHIFT COUNTER REG TO
SHIFT COUNTER ADDER" runs while NM.
**Totals.** NOT SHOWN as a number: the clock row is broken. As drawn (and
numbered) the chart has END OP in period 6 = 7 periods, but that is a
typographic count across a break, not the operation's length. The number of
T3/T4 passes is not printed. (Inference, mine, not on the page: 48 at a shift
of 6 per pass would be 8 passes = 16 periods + T0 = 17, which equals Perf.
Char. Table 2's SLO execution figure of 17. Do not cite that as chart-shown.)
The header's "ONE NORMALIZATION SHIFT" presumably refers to the last pass
(period 5-6) after the break [uncertain].

(Footers confirmed after the table in sec. 0 was written: PDF 228 = "8-4",
caption "FIGURE 3.8.4. FLOATING-POINT COMPARE (TIMING)"; PDF 230 = "8-6",
caption "FIGURE 3.8.6. FLOATING-POINT SHIFT FRACTION (TIMING)"; PDF 232 =
"8-8"; PDF 234 = "8-10"; PDF 236 = "8-12". All dated 2/1/62.)

---

## 10. Figure 3.8.10 FLOATING-POINT STORE ROOT (TIMING), sheets 1 and 2

### Sheet 1 -- PDF 233 (landscape), printed 8-9, 2/1/62. Two panels on two different time bases.

**Left panel**, headed "INSTRUCTION DECODING AND INITIAL PREPARATION UNDER PAU
CONTROL". `FP CLOCK`, edges 0-3.

| period | ring triggers up | rises / pulses | falls at end |
|---|---|---|---|
| 0 | `T0` (START CTRL) | "SAMPLE (TO EXECUTION REGISTER)" 1st half; `FIRST CYCLE TGR` (START CTRL); `EXPONENT ROUTING TGR (TP6)` (SSQ FST) [dotted set; line runs off right with a break mark]; `GATE 31` (SSQ FST); `GATE 61` (SSQ FST); `DECODE FOR SHIFT OF ZERO OR R1` (SSQ FST & A REG BIT 10) | T0 |
| 1 | `T3` (T0 & SSQ FST) | `WRITE EXPONENT C TGR` (T0 & TO MEM) [runs off right with a break mark]; `F REG LATCH` "RESET" pulse (T0), 1st half | T3 |
| 2 | `T4` (T3) | `SAMPLE TEST COMP TGR`; `GATE 11 & 12` (TEST COMP, T4, SSQ FST) [drawn over about the same period; its exact half-period offset is uncertain]; `F REG LATCH` "SET" pulse, 1st half | T4; FIRST CYCLE TGR; GATE 31; GATE 61; DECODE FOR SHIFT...; SAMPLE TEST COMP |
| 3 | (none) | `SIGNAL SSQ TO VFL TGR` (T4 SSQ FST) "(TURN CONTROL OVER TO SAU)", one period; `LATCH ACOB` (T4 SSQ FST), with "(NOT INT)", one period, fall annotated "(SIGNAL SSQ TO VFL TGR)"; "GATE ACOB 12-59 TO C 12-59" (T4 SSQ FST), 1st half; `GATE 21 (TGR)` (T4 SSQ FST) [runs off right with a break mark] | -- |

Note FIRST CYCLE TGR is drawn THREE periods long here (0-2); on the other
charts it is two.

**Right panel**, headed "SQUARE ROOT DEVELOPMENT UNDER SAU CONTROL". Time base
is a row labelled `A PULSES` (15 pulses drawn, unnumbered, with break marks in
the rows below). **No FP CLOCK is drawn on this panel and no ratio between an
A-pulse period and an FP CLOCK period is printed on either sheet.** The two
panels are not drawn to a common scale (A pulses are drawn closer together);
that is a drawing fact, not a timing statement.

| A-pulse slot (my count, from the left) | what is drawn |
|---|---|
| 1 | `SU SSQ (TGR)` (SIGNAL SSQ TO VFL): up for one A period |
| 2 onward | `SSQ TGR` (SU SSQ) up, with a break mark, down around slot 10 as drawn; `PAU DO SSQ TGR` (SU SSQ) up, with a break mark, down at about slot 15; under it, same span, (PAU DO SSQ) "GATES 61, 21, 22 & 25, BLOCK ADDER POS. 50 & 51, & ONE TO ADDER POS. 50, 98, 99" |
| 2 onward, one pulse per A pulse | `ROUTE C TO F` pulses labelled "(C BITS) - (12-13) (14-15) (16-17) (56-57) (58-59) (60-61)" with a break between the 3rd and 4th; note "NOTE THIS IS REPRESENTING CHANGING DATA (NEW C POSITIONS)" |
| 2 onward, one pulse per A pulse | `F REG LATCH` pulses, labelled above "(C BITS) -> (12-13)(14-15)(16-17)(56-57)(58-59)(60-61)" and "(DEV ROOT BIT) -> 1 2 21 22 23 24 25 26 27 28 47 48", break marks after "2" and after "28"; over 24..48 a brace "(ZEROS TO F REG POS 100 & 101)" |
| -- | `RFL`: "SET RFL TO 47", then "RFL = 47 - 45 - 43 - 3 - 1 - 0" (break between 43 and 3) |
| after RFL = 0 | `EOC1` (RFL = 0) one A period; then `EOC2` (EOC1) one A period; and an (EOC1) pulse "(HANDLE EXPONENT FROM A REG & WRITE INTO C POS 0-11)" |
| -- | `SHIFT COUNTER REGISTER`: "SET SCR TO 96", then "SCR = 96 - 94 - 92 [break] 54 52 50 48 46 44 42 40 38 [break] 0", one value per A pulse |
| at SCR = 0 | pulse "B TIMED SCR=0" "(PAU RESUME CONTROL)" |
| -- | dotted rows "(ADDER OUTPUT POS 50 = 0) GATE 63 ... ETC." and "ADDER OUTPUT POS 50 = 1 GATE 72 ... ETC." (alternating per root bit) |

What this panel shows numerically: one root bit developed per A pulse, root
bits numbered 1..48; SCR set to 96 and stepping by 2 per A pulse to 0; RFL set
to 47 and stepping by 2 (47, 45, ... 1) then 0, i.e. C bits are routed in
pairs for the first 24 root bits and zeros after ("ZEROS TO F REG POS 100 &
101" over root bits 24-48). So **48 A-pulse periods** of development, plus 1
for SU SSQ before and the SCR=0 hand-back after. [The labels "(C BITS)" pair
list and the "(DEV ROOT BIT)" list are only loosely aligned under the breaks;
I could not confirm which C pair goes with which root-bit number.]

### Sheet 2 -- PDF 234, printed 8-10, 2/1/62

Headed "NORMALIZATION AND TERMINATION UNDER PAU CONTROL". `FP CLOCK`, five
periods drawn, **unnumbered**; I call them q0-q4.

| period | ring triggers up | rises / pulses | falls at end |
|---|---|---|---|
| q0 | `TX` (PAU RESUME SSQ) | (continuing from sheet 1: `EXPONENT ROUTING TGR (TP6)`, `WRITE EXPONENT C TGR`, `GATE 21`) | TX |
| q1 | `T4` (TX) | `NORMALIZE EXPONENT TGR` (TX); `GATES 11 & 12` (NE, NOT NM, SSQ); `SUPPRESS ADDER OUTPUT (59) (51)` [so printed; sheet 1 says 50 & 51; uncertain] (NE, NOT NM, SSQ); `GATE 61` (SSQ, NE NOT NM); `GATE C EXP TO SAU (FOR NORMALIZING)` (NE, TP6), annotated "NORMALIZE AMOUNT A INPUT" | T4 |
| q2 | `T3` (T4, SSQ OPER, NE, NOT NM) | -- | T3; WRITE EXPONENT C TGR; SUPPRESS ADDER OUTPUT; GATES 11 & 12 falls mid-q2 [approx.] |
| q3 | `T4` (T3); `TC` (T3 & NE) | `WRITE EXPONENT D TGR` (END OP, TO MEM); "61 & 63 (TGR)" (T3, SSQ) [GATE 61 row continues as 61 & 63]; `NORM MANTISSA (TGR)` (T3, NE); `END OP (TGR)` (MANTISSA RESULT TRUE, T3, NE, SH <= 6); `F REG LATCH` pulse (T3, NE), 1st half; `ACIB BUS LATCH LEVEL 1` rises; GATES 11 & 12 again "(END OP, NOT INT)" from 2nd half | T4; TC; NE; GATE 21; GATE 61 & 63; GATE C EXP TO SAU; NORM MANTISSA; END OP |
| q4 | (none) | `EXP LATCH`, `EXP SAMPLE`, `LATCH DATA ACOB` (each: TC, END OP, NOT INT); `ACIB BUS LATCH LEVEL 2` rises | -- |

**Totals for Store Root, as the charts give them.**
- PAU preparation: T0, T3, T4 = 3 FP periods, then 1 FP period of
  `SIGNAL SSQ TO VFL TGR` (shown).
- SAU development: SU SSQ (1 A period) + 48 root bits at one per A period
  (shown by SCR 96..0 step 2 and DEV ROOT BIT 1..48), then "B TIMED SCR=0".
- PAU termination: TX, T4, T3, T4/TC = 4 FP periods to END OP, latches in a 5th
  (shown for shift <= 6).
- **The A-pulse period in FP CLOCK periods: NOT SHOWN on these sheets.** The
  total in FP periods therefore cannot be computed from Fig 3.8.10 alone.
  (`clock_unit.md` sec. 4.1/4.4 takes A-to-A = 2 slots from Fig 2.10.1 and gets
  96 + 12 = 108, and itself calls the closure "suggestive". `ebox_roadmap.md`
  says A PULSES are "a separate and faster waveform"; the chart draws them
  closer together but prints no ratio and the panels share no scale. Neither
  claim is established by this figure.)

---

## 11. Figure 3.8.11 FLOATING-POINT MULTIPLY (TIMING) -- PDF 235, printed 8-11, 2/1/62

Header, verbatim: "SEQUENCE SHOWS NORMALIZATION SHIFT OF 6 OR LESS."
FP CLOCK edges 0-10.

| period | ring triggers up (set condition) | rises / pulses | falls at end |
|---|---|---|---|
| 0 | `T0` (START CTRL) | `SAMPLE TO C & EXECUTION REGS` 1st half; `1ST CYC TGR` (START CTRL) [drawn only one period long here]; `GATE 1` (MPY, FCT) "GATE A REG FRACTION TO F REG"; `GATE 36` (MPY, FCT)/(RIGHT 12 TGR) "ALLOW DEVELOPMENT OF 1 & 3 X MULTIPLE" | T0; 1ST CYC TGR; GATE 1 |
| 1 | `T1` (T0, MPY) | `MULTIPLY STATUS TGR` (MPY, FST); `SHIFT RIGHT 12 TGR (GATE 47)` (MPY, FST) "ALLOW FOR F REG SHIFT OF 12 POS 1-37 & 62-85"; `WRITE EXPONENT A TGR` (MPY, FST, T0) [stays up, break mark at right]; `1X MULTIPLICAND TGR` (MPY, FST) "ALLOW FOR OPENING OF 1X MCD COMP FROM MULTIPLICAND SET UNIT IF LOW ORDER BIT = 1"; `RESET S & T REG` (T1, MPY) [drawn about 1.5 periods; extent uncertain]; `GATE EXPONENTS TO SAU ADDER` (MPY STATUS TGR, RIGHT 12 TGR) | T1 |
| 2 | `MR1` (T1, MPY) | F REG LATCH & SAMPLE pulse #1 "(NOT T4 MPY STATUS TGR)", 1st half; G REG LATCH & SAMPLE pulse #1 "(SHIFT RIGHT 12 TGR NOT MC)", 1st half; S & T REG LATCH & SAMPLE DELAYED pulse #1 "(NOT T3, NOT T4, MPY STATUS 1)" -- drawn later in the period than the F/G pulse | MR1; 1X MULTIPLICAND TGR |
| 3 | `MR2` (MR1, NOT MR2) [row label printed "MR, 2"] | F, G pulses #2; delayed S&T pulse #2; (RIGHT 12 TGR, NOT 1X MCD TGR) "GATE S REG 49-61 TO F REG 1-12" / "GATE T REG 49-61 TO F REG 62-73" rises | -- |
| 4 | `MR2` continues; `MR1` again (MR2, NOT MR1) | F, G pulses #3; delayed S&T pulse #3 | MR1; MR2 |
| 5 | `MC` (MR2, MR1) [printed twice: "(MR2.MR1)" and "(MR1,MR2)"] | F, G pulses #4; delayed S&T pulse #4; `SAMPLE TEST COMP` | MC; SHIFT RIGHT 12 TGR; GATE 36; GATE EXPONENTS TO SAU ADDER; GATE S/T REG 49-61; SAMPLE TEST COMP |
| 6 | `T4` (MC, MPY) | `GATE 41, 42, 46 (TGR)` (MC, MPY, NOT INT); `GATE 22 TGR` (MC, MPY, NOT INT) "F REG 50-97 TO MAIN ADDER 50-97"; `NORMALIZE EXPONENT TGR` (MC, MPY, NOT INT); `GATE A EXP TO SAU ADDER` (NE, NOT TP6) "(FOR NORMALIZATION)"; `EXP LATCH & SAMPLE` (MC, MPY, NOT INT), one period; F REG pulse #5, 1st half; delayed S&T pulse #5 [5th S&T pulse: uncertain, 3.8.13 draws only four] | T4; EXP LATCH & SAMPLE |
| 7 | `T3` (T4, MPY) | `GATE 61 & 63 (TGR)` (T4, MPY STATUS TGR) | T3; MULTIPLY STATUS TGR; GATE 41, 42, 46 |
| 8 | `T4` (T3); `TC` (T3) | `GATE 21 (TGR)` (T3, NE, RESULT TRUE); `END OP (TGR)` (T3, NE, SHIFT <= 6); `NORM MANT (TGR)` (T3, NE); F REG pulse (T3, NE), 1st half; `GATE 11 & 12` (TEST COMP END OP) from 2nd half | T4; TC; GATE 22 TGR; NE; GATE A EXP TO SAU ADDER; GATE 61 & 63; GATE 21; END OP; NORM MANT |
| 9 | (none) | `LATCH DATA ACOB` (TC, TEST COMP, END OP, NOT INT); "(SAMPLE TO A REG)" (TC TO ACC), 1st half; `EXP LATCH & SAMPLE` (END OP, NOT INT) | -- |
| 10 | (none) | second A REG sample pulse, 1st half: "SECOND SAMPLE ORDER CHECKER CONTROL IF THIS IS DOUBLE OPER." | -- |

Side note printed at right of period 6-7: "GATE S AND T REGS (POS 2-61) TO MAIN
ADDER (POS 2-61) AND F REG (POS 1-36) TO ADDER (POS 62-97)". Beside the S&T
row: "(DELAYED TO ALLOW CSA LOOP TIME TO COMPLETE)".
Bottom braces: `CSA LOOPS` I, II, III, IV, each about one period long and
overlapping the next by half (I starts mid-period 2, IV ends mid-period 6),
then `MAIN ADDER LOOP` over periods 6-7.

**Loop.** The CSA loop is a fixed four-state count MR1 -> MR2 -> MR1.MR2 -> MC
(periods 2-5), each state with `SHIFT RIGHT 12`; no data-dependent exit is
drawn. 4 x 12 = 48. Then T4, T3 (main adder), then T4/TC with END OP.
**Totals.** END OP in period 8 = 9 periods (0-8) for normalization shift <= 6;
latches in period 9 (and a second A sample in 10 for a double operation). An
extra normalization pass is not drawn on this chart (the header restricts it
to shift <= 6); by 3.8.1's rule it would be T3 + T4/TC = +2, but that is not on
this page. No dependence on multiplier bits is shown.

---

## 12. Figure 3.8.12 FLOATING-POINT LOAD MULTIPLER [sic] REGISTER (TIMING) -- PDF 236, printed 8-12, 2/1/62

Different draughting style (typeset labels, circled clock numbers 0-5).
Header: "FLOATING POINT LOAD MULTIPLIER REG. LMR". Note, verbatim: "NOTE: THIS
EXAMPLE SHOWS TWO NORMALIZATION SEQUENCES". Under the clock: "SHIFT > 6"
(period 2), "SHIFT <= 6" (period 4). An `LA ENABLE` level is drawn over
period 0 (rises before edge 0, falls before edge 1).

| period | ring triggers up | rises / pulses | falls at end |
|---|---|---|---|
| 0 | `T0` (START CRTL [sic]) | "SAMPLE OP CODE TO EXEC REG AND TOB TO C REG" (START CTRL), 1st half; `FIRST CYCLE TGR (FCT)`; "GATE 33 - C 12-59 TO ADDER 2-49" (FCT, LMR); "TP-6 - EXPONENT ROUTING CONTROL" (FCT, LMR), stays up | T0 |
| 1 | `T3` (T0, LMR) | "GATE 61 AND 63 - ADDER 0-99 to F 0-89" [so printed] (T0, LMR); `NORM EXPONENT TGR (NE)` (T0, LMR); `WRITE EXP C` (T0, TO MEM); F REG LATCH & SAMPLE pulse (T0), 1st half | T3; FCT; GATE 33 |
| 2 | `T4` (T3); `TC` (T3, NE) | `NORM MANTISSA TGR (NM)` (T3, NE); "GATE 21 AND 22 - SHIFTER 0-99 TO ADDER 0-99" (T3, NE); `STC`; F REG pulse (T3, NE), 1st half | T4; TC; STC |
| 3 | `T3` (T4, NOT END OP, NOT INT) | `EXPONENT LATCH` (TC, NM); `EXPONENT SAMPLE` (TC, NM) | T3; WRITE EXP C; EXPONENT LATCH/SAMPLE |
| 4 | `T4` (T3); `TC` (T3, NE) | `END OP` (T3, NE SHIFT <= 6); `WRITE EXP "B"` (T3, NE, SHIFT <= 6); F REG pulse (T3, NE), 1st half; "GATES 11 and 12 - SHIFTER TO ACIB" (END OP, TEST COMP) from 2nd half | T4; TC; END OP; NE; GATE 61/63; NM; GATE 21/22 |
| 5 | (none) | `LATCH ACOB` (TC, END OP, NOT INT); `EXPONENT LATCH`, `EXPONENT SAMPLE` (TC, END OP, NOT INT); "SAMPLE ACIB TO D REG" pulse, 1st half; `A REG SAMPLE` (TO ACC, T0 [sic], END OP, NOT INT), 1st half | -- |

Braces: ADDER LOOP 1/2, EXPONENT LOOP 1/2.
**Totals.** Drawn (two normalization sequences): END OP in period 4 = 5
periods; latches in 5. One sequence: 3 periods (0-2). +2 per extra sequence.

---

## 13. Figure 3.8.13 FLOATING-POINT MULTIPLY AND ADD (TIMING) -- PDF 237 (fold-out), printed 8-13/8-14, 2/1/62

Circled clock edges 0-15. No header sentence. Label in the chart: "FLOATING
POINT MULTIPLY AND ADD". Solid lines are one case; dashed lines plus a braced
lower block are the other, per the note, verbatim: "IF ACCUMULATOR EXPONENT IS
SMALLER USE THIS TIMING ALONG WITH DOTTED LINES ABOVE".

### Solid-line case

| period | ring triggers up (set condition) | rises / pulses | falls at end |
|---|---|---|---|
| 0 | `T0` (START CTRL) | "SAMPLE OF CODE TO EXEC REG AND TOB TO C REG" (START CTRL), 1st half; `LA ENABLE` up from before edge 0, falls late in period 0; `FCT TGR` (START CTRL); "SET BAAB TO 112 = T0.MPYC" (T0, MPYC), about 1.3 periods; `LTH BAAB` (T0, MPYC), 2nd half; "GATE C REG TO F REG / GATE #3" (T0, MPYC); "GATE 37 = D REG TO MULTIPLE GENERATION CKTS = T0.MPYC - MPY ST", up to mid-period 8 | T0; FCT TGR; GATE #3 |
| 1 | `T1` (T0 MPYC, CM) | "GATE BEXP PLUS CEXP TO VFL ADDER" (1 XMCD, CM), until early period 3 [approx.]; `WRITE EXP C TGR` (T0, MPYC), periods 1-3; `RESET S AND T REGS` (T1, MPY ST), one period; `1X MCD TGR` (T0, MPYC), periods 1-2; `RIGHT 12 STATUS TGR` (T0, MPYC), periods 1-5; `MULTIPLY STATUS TGR` (T0, MPYC), periods 1-7; `CUMULATIVE MULTIPLY - CM TGR` (T0, MPYC), solid to end of period 9, dashed to end of period 12 | T1; RESET S AND T REGS |
| 2 | `MR1` (T1, MPY) | F REG LTH AND SAMPLE pulse #1 "(NOT T4, MPY ST)"; G REG LTH AND SAMPLE #1; "S REG AND T REG LTH AND SAMPLE" #1 "(SH RIGHT 12 ST, NOT MC)", drawn later in the period; "RESET BAAB TO 10" pulse (MR1, NOT MR2), 2nd half | MR1; 1X MCD TGR |
| 3 | `MR2` (NOT MR2, MR1) | F, G, S/T pulses #2; `EXPONENT LATCH` (CM, MR1, NOT MR2), one period; `EXPONENT SAMPLE` (CM, MR1, NOT MR2), shorter; an unnamed level on the FCT TGR row rises, set label "(COM [or CUM], NOT MR2, MPY ST)", solid to end of period 7, dashed on to about period 11 [name not printed; uncertain]; "GATE A EXP MINUS C EXP TO VFL ADDER" (CUM, FCT) rises early in period 3, solid to mid-period 8, dashed to mid-period 11 | WRITE EXP C TGR |
| 4 | `MR2` continues; `MR1` again (MR2, NOT MR1) | F, G, S/T pulses #3; `WRITE EXP A TGR` (MR2, NOT MR1, CM), stays up | MR1; MR2 |
| 5 | `MC` (MR1, MR2) | F, G, S/T pulses #4; "STC = MR1 MR2 MPY", one period | MC; RIGHT 12 STATUS TGR; STC |
| 6 | `T4` (NOT INT, MC) | F REG pulse #5 | T4 |
| 7 | `T3` (T4, MPY ST) | `PSA TGR` (T4, CM, EXP SUM PLUS), solid periods 7-9, dashed to end of 12 | T3; MULTIPLY STATUS TGR |
| 8 | `T2` (CUM, PSA)(T3, MPY ST) | "SAMPLE 1ST PRESHIFT TO SCR" (T3, CM, NOT CMPSE), 1st half; "GATE PRESHIFT AMT TO SHIFT COUNTER" (T2, PSA), one period; `NORM EXPONENT` (T3, CM, NOT CMPSE), solid periods 8-10; "GATES 31 AND 32 (A REG AND B REG TO ADDER)" [legend: "GATE 31 - NOT MANT ROUTING, PSA; GATE 32 - CM, PSA, NE"], solid to early period 10; "GATES 21 AND 22 OR GATE 23 (SHIFTER TO ADDER TRUE OR COM)" (T3, CM), solid to early period 10; "GATES 71 AND 72 (SHIFTER TO F REG)" (T2, PSA) [drawn dashed; solid extent uncertain]; F REG pulse, 1st half; `EXPONENT LATCH`, one period, set label printed after it "(MR3, MPYC + TC, NM)" | T2 |
| 9 | `T3` (T2, PSA, SH < 4) | -- | T3; CM TGR (solid); PSA TGR (solid) |
| 10 | `T4` (T3, NE); `TC` (T3, NE) | `NORM MANT` (T3, NE); `END OPN` (T3, NE, SH <= 6); F REG pulse (T3, NE), 1st half; "GATES 11 AND 12 (SHIFTER TO ACIB)" (END OP, TESTS COMP) from 2nd half | T4; TC; NORM EXPONENT; NORM MANT; END OPN |
| 11 | (none) | `EXPONENT LATCH`, `EXPONENT SAMPLE` (TC, NM); "(END OP) BUS LATCH I AND II" rises mid-period | -- |

### Dashed case (accumulator exponent smaller), lower braced block plus dashed lines

| period | ring triggers up (set condition) | other lines in the lower block |
|---|---|---|
| 7 | (as above) | `CMPSE TGR` rises, up periods 7-9; `TP6 TGR` (FCT, CM, T3) rises, up to about edge 14 |
| 8 | `TB` (MPY ST, CMPSE) | "GATES 11 AND 12 (SHIFTER TO ACIB) = TB.CMPSE.TESTS CMPT", 2nd half of 8 to 1st half of 9 |
| 9 | `TC` (T4, CM, EXP SUM MINUS)(TB) | "SAMPLE LEVEL II TO C REG" (TB, CMPSE), 1st half; "SAMPLE A REG AND B REG TO F REG" (TB, CMPSE), 1st half; `BUS LTH II` (TB, CMPSE), 2nd half of 9 to 1st half of 10; `BUS LTH I` (TB, CMPSE), 2nd half of 9 to mid-11; "PASS DATA 1ST LEVEL TO II ND LEVEL" (TC, CMPSE) [extent uncertain]; dashed "SAMPLE 1ST PRESHIFT TO SCR" alternative labelled (TB, CMPSE) |
| 10 | `MR3` (TC, CMPSE) | "SAMPLE BUS TO B REG" (TC, CMPSE), 1st half |
| 11 | `T2` (MR3, CM) | dashed "GATE PRESHIFT AMT TO SHIFT COUNTER"; dashed GATES 71 AND 72 |
| 12 | `T3` (T2, PSA, SH < 4) | -- |
| 13 | `T4` (T3, NE); a second unlabelled level (T3, NE) [presumably TC; label not printed] | dashed `NORM MANT` (T3, NE), dashed `END OPN` (T3, NE, SH <= 6), dashed F REG pulse (T3, NE); dashed GATES 11 AND 12 from 2nd half |
| 14 | -- | dashed EXPONENT LATCH / SAMPLE (TC, NM); dashed BUS LATCH I AND II |

**Totals.** Solid case (pre-shift < 4, norm shift <= 6): END OPN in period 10 =
11 periods (0-10); latches in 11. Dashed case (accumulator exponent smaller):
END OPN in period 13 = 14 periods (0-13), i.e. +3 (TB, TC, MR3). The
multiply spine (T0, T1, MR1, MR2, MR1.MR2, MC, T4, T3) is periods 0-7 as in
3.8.11; the add phase is T2, T3, T4/TC = 3 periods. No pre-shift T4 hold is
drawn here ((T2, PSA, SH<4) goes straight to T3). Data dependence shown: the
solid/dashed split only.

---

## 14. Figure 3.8.14 FLOATING-POINT STORE MULTIPLIER REGISTER (TIMING) -- PDF 238 (fold-out, chart on left third), printed 8-15, 2/1/62

Header, verbatim: "EXAMPLE SHOWS 2 NORMALIZATION CYCLES". Circled edges 0-6.

| period | ring triggers up | rises / pulses | falls at end |
|---|---|---|---|
| 0 | `T0` (START CTRL) | `LA ENABLE` (up from before edge 0 to late period 0); "(SAMPLE OP CODE TO EXEC REG AND TOB TO C REG)" 1st half; `FIRST CYCLE TGR` (FCT); "GATE 34, D12-59 TO ADDER 2-49" (STM, FCT), up to mid-period 2; "SET BAAB TO 112" (T0, STM), about 1.3 periods; `LTH BAAB` (T0, STM), 2nd half | T0 |
| 1 | `T3` (T0, STM) | `NORM EXPONENT TGR (NE)` (T0, STM); "GATE 61 AND 63 - ADDER 0-99 TO F 0-99" (T0, STM); "WRITE EXP INTO C REG" (T0, TO MEM); F REG LATCH & SAMPLE pulse (T0), 1st half "ALSO USED FOR SHIFT REG" | T3; FCT |
| 2 | `T4` (T3); `TC` (T3, NE) | "GATE 21 AND 22 - SHIFTER TO ADDER" (T3, NE); `NORM MANTISSA TGR (NM)` (T3, NE); `STC` (T3, STM, FCT); F REG pulse (T3, NE), 1st half; "RESET BAAB TO 10" pulse (T4, STM), 2nd half | T4; TC; STC |
| 3 | `T3` (T4, NOT END OP, NOT INT) | "TP6 EXP ROUTING CTRL" rises, labelled "(TO MEM, NM, EXP SAMPLE)" [dotted "(STM, FCT)" set to its left], stays up; `EXP LATCH` (TC, NM); `EXP SAMPLE` (TC, NM) | T3; WRITE EXP INTO C REG |
| 4 | `T4` (T3); `TC` (T3, NE) | `END OP` (T3, NE, SHIFT <= 6); "WRITE EXP INTO D REG" (END OP, TO MEM), stays up; F REG pulse (T3, NE), 1st half; "GATE 11 & 12 SHIFTER TO ACOB" (END OP, TEST COMP) from 2nd half | T4; TC; END OP; NE; GATE 61/63; (GATE 21/22 and NM fall slightly before the edge as drawn) |
| 5 | (none) | `LATCH ACOB` (TC, END OP, NOT INT); `EXP LATCH`, `EXP SAMPLE` (TC, END OP, NOT INT) "ALSO USED AS INDICATOR LATCH" | -- |

**Totals.** Drawn (2 normalization cycles): END OP in period 4 = 5 periods;
latches in 5. One cycle: 3 periods. +2 per extra cycle.

---

## 15. Figure 3.8.15 FLOATING-POINT DIVIDE (TIMING), three sheets

**Clock numbering on this figure starts at 1, not 0** (T0 is "period 1"), and
runs continuously across Parts A-D by edge number; Parts E, F, G are detours.

### Sheet 1 -- PDF 239, printed 8-16, 2/1/62. Parts A and B.

**Part A**, header verbatim: "DIVISOR PRE-NORMALIZATION EXAMPLE SHOWS TWO
NORMALIZATION LOOPS." At edge 4: "IF ZERO DIVISOR, GO TO PART E, SHEET 3".
Under the clock: "SHIFT > 6" (period 3), "SHIFT <= 6" (period 5). At edge 5:
"(START ROUTING DIVIDEND FOR NORMALIZATION SEE PART B)". Edges 1-7.

| period | ring triggers up | rises / pulses | falls at end |
|---|---|---|---|
| 1 | `T0` (START CTRL) | "SAMPLE TO C & EXECUTION REGS" 1st half; `FIRST CYCLE TGR`; `GATE 33` (FCT, DIV) "(C REG TO ADDER)" | T0 |
| 2 | `D3` (T0, DIV) | `DIVIDE NORMALIZE EXPONENT TGR (DNE)` (T0, DIV), continues into Part B; `EXPONENT ROUTING TGR (TP6)` (D3, DIV, FCT) [drawn rising at edge 2, label notwithstanding]; `GATE 61 & 63 (TGR)` (T0, DIV), continues; `GATE C EXPONENT TO SAU ADDER` (TP6, DNE, NOT DC) "(FOR NORMALIZATION UPDATING)"; `SHIFT CONTROL "A"` (DNE, DIV), continues; "SAMPLE TO F REG, SHIFT REG & COUNTER REG" pulse, 1st half | D3; FIRST CYCLE TGR; GATE 33 |
| 3 | `D4` (D3, DNE) | `DIVISOR STATUS TGR (DVSR)` (D3, DIV, FCT); `GATE 21 & 22 (TGR)` (D3, DIV, FCT, SH > 6); `WRITE EXPONENT C TGR` (D3, DIV, FCT); `GATE SHIFT COUNTER ADDER TO REG` (DVSR OR DVND OR DVDE), continues; `GATE SHIFT COUNTER REG TO ADDER` (NOT SDC), continues; `ADD SHIFT AMOUNT TO REGISTER` (DVSR); sample pulse, 1st half | D4 |
| 4 | `D3` (D4, NOT DVDE ZERO, DVSR) | `EXP LATCH & SAMPLE` (D4, DNE, NOT DC), one period | D3; GATE 21 & 22 |
| 5 | `D4` (D3, DNE) | `SAMPLE TEST COMP`; `GATE 11` (DVSR, DVND) "(FREQ TO A CHECKER)" [= F REG TO A CHECKER], periods 5-6; sample pulse, 1st half | D4; TP6; GATE C EXPONENT TO SAU ADDER; SAMPLE TEST COMP |
| 6 | `D3` (D4, DVND, NOT INT) | "SAMPLE ACOB TO C REG" (D4, DVSR, DVND), 1st half; `EXP LATCH & SAMPLE` (D4, DNE, NOT DC) | D3; DVSR; WRITE EXPONENT C TGR; ADD SHIFT AMOUNT TO REGISTER; GATE 11 |

**Part B**, header verbatim: "DIVIDEND PRE-NORMALIZATION EXAMPLE SHOWS 2
NORMALIZATION LOOPS." Edges 5-11 (overlapping Part A's 5-7). Under the clock:
"SHIFT > 6" (about period 6-7), "SHIFT <= 6" (period 8). Marked: at edge 8 "IF
DIVIDEND ZERO, GO TO PART F, SHEET 3"; at edge 9 "(START DIVIDE, SEE PART C,
SHEET 3)" [so printed; Part C is on sheet 2]; at edge 10 "IF DIVIDEND NOT
NORMALIZED, GO TO PART G, SHEET 3".

| period | ring triggers up | rises / pulses | falls at end |
|---|---|---|---|
| 5 | `D4` (D3, DNE) | `GATE SHIFT COUNTER REG TO ADDER` (redrawn rising); `DIVIDEND STATUS TGR (DVND)` (D3 DVSR SHIFT <= 6), periods 5-10; `GATE 31` (DVSR, DVND) "(A REG TO ADDER)", periods 5-6; dotted "(DVND, NOT DVDE, UNNORMALIZED) (GATE 32, ALSO IF DOUBLE OPERATION)" and dotted `SHIFT CONTROL "B"`, to edge 9 | D4; TP6 TGR |
| 6 | `D3` (D4, DVND NOT INT) | "GATE A EXP TO SAU ADDER FOR NORMALIZE UPDATING)" (DNE, NOT TP6), periods 6-10 | D3; GATE 31 |
| 7 | `D4` (D3, DNE) | `GATE 21 (TGR)` (D3, DVND), continues; `GATE 22 (TGR)` (D3, DVSR, DVND, SH > 6), periods 7-8; `WRITE EXPONENT A TGR` (D3, DVSR, DVND), continues; `SUB SHIFT AMOUNT FROM REG` (DVND, NOT DVSR, OR DVDE), continues; "SAMPLE TO F REG, SHIFT REG & COUNTER REG" pulse, 1st half | D4 |
| 8 | `D3` (D4, DVND NOT INT) | `EXP LATCH & SAMPLE`, one period | D3; GATE 61 & 63 (TGR); GATE 22 |
| 9 | `D4` (D3, DNE) | sample pulse, 1st half | D4 |
| 10 | `D3` (D4, DVND NOT INT) | `EXP LATCH & SAMPLE` | D3; DNE; DVND; GATE A EXP TO SAU ADDER; GATE SHIFT COUNTER REG TO ADDER |

### Sheet 2 -- PDF 240 (fold-out, chart drawn rotated 90 deg), printed 8-17/8-18, 2/1/62. Parts C and D.

Title in the chart: "Floating Point Divide, Reduction and Termination". Circled
edges 9-19, then a **break mark in the clock row** (with one unnumbered pulse on
each side of it), then 20, 21, 22, (23 unlabelled on Part C; labelled on Part
D), 24, 25. Edge numbers after the break are nominal.

Ring triggers (Part C): `D4` (D3, DNE) in period 9; `D3` (D4, DVND Not Int) in
period 10; `D4` (D3, DNE) in 11; then alternating `D3` (D4, DVDE) in 12, 14,
16, 18 and `D4` (D3, DVDE) in 13, 15, 17, 19 ... break ... `D4` 20, `D3` 21,
`D4` 22, `D3` 23, `D4` 24. `TC` "(D3, DC, Sh = 0 Not Double, Res True)" in
period 22; a dashed second `TC` in period 24, with "Not Both" between them.

| period(s) | braces (Part D) | lines rising / up |
|---|---|---|
| continuing from sheet 1 | -- | `Shift Control "A"`; `Gate Shift Counter Adder to Register`; `Gate 21 (Tgr)`; `Write Exponent A (Tgr)` (solid to about edge 14, dashed to 16); `Subtract Shift Amount from Counter Register` |
| 9-10 | "Trial Reduction Cycle" | `Divide Status Trigger (DVDE)` (D3, DVND, Sh <= 6) rises at 9 and stays; "One Times Comp Tgr (1x Comp)" rises at 9, with "Note: Trigger will reset here. However 1x Comp line will stay up due to (DVND, DVDE)" and a dashed alternative "(D4, 1x COMP, DVND, Shifter 2 output = 0) Note: This would occur if Dividend was not Normalized."; `Gate 35` ((DVND, 1x Comp)) period 9, dashed into 10; "Gate 36, Gate 72, Enable Multiple Decoding" (DVDE) rises at 9 and stays; `Gate 61` (DVDE) rises at 9 and stays |
| 11-12 | "Intermediate Reduction Cycle" #1 | `Second Divide Cycle Trigger (SDC)` (D3, DVND, DVDE), periods 11-12; "(SDC) Gate Shift Counter to LZC", 11-12; `Shift Control "B"` (DVDE, NOT DVND) rises at 11 and stays; dashed "Gate 47 to Shift Counter" (SDC, 1x Comp, F Register True) and "Gate 48 to Shift Counter" (SDC, 1x Comp, F Register Comp), 11-12; dashed pulse "Sample to ACC (60-107) If double operation (all zeros)" 1st half of 12; "Sample to F Register, Shift Register and Counter Register" pulse, 1st half of 11 |
| 13-14 | "Intermediate Reduction Cycle" #2 | `Divide Counter Trigger (DC)` (D3, SDC) rises at 13 and stays; `Tx Trigger` (D3, SDC), 13-14, dashed continuation "(D3, DC, NOT DNE)" 15-16; `Gate A Exponent to SAU Adder` (DC) rises at 13; `Gate Shift Counter Register to Adder` (NOT SDC) rises at 13; dashed `DNE` (D3, 1x Comp, SDC, F Register True, Sh Ctr = 0 or +) 13-14 "Allows for updating of the Dividend"; dashed "Add "1" to LZC" (DC, DNE and Shift Ctr Reg + or 0) and "Gate "1" to SAU Adder" (DC, DNE), 13-14; dashed "Gate Comp of 48 to SAU Adder" (TX, DC, NOT DNE) 13-14 then solid 15-16 "Used to Update Exponent for Remainder Exp, Does not Affect Divide"; sample pulse 1st half of 13 |
| 15-16 | "Intermediate Reduction Cycle" #3 | dashed `Write Exponent D (Tgr)` (DC, TX, NOT DNE) 14-15, solid 16-17 "Used For Divide Double Has no Effect on Divide"; `Gate & Invert C Exp to SAU Adder` (DC, NOT TX) dashed from 15, solid from 17; dashed "Exponent Latch and Sample (D3, DNE, DC)" in 15 "Update Exponent if Trial Reduction Cycle Result True."; dashed "Exponent Latch and Sample (D3, NOT DNE, TX, DC)" in 15 and 17 "Set Remainder Exp into D Reg, Does Not Affect Divide"; sample pulse 1st half of 15 |
| 17-18 | "Intermediate Reduction Cycle" #4 | `Write Exp A Trigger` (DC, NOT FD [uncertain], NOT TX) dashed from 16, solid from 18, stays; sample pulse 1st half of 17; brace "Exponent Subtraction" from 17 across the break |
| 19 - break | "Intermediate Reduction Cycle" (runs into the break) | sample pulse 1st half of 19 |
| 20-21 | "Last Reduction Cycle" | `Exp Latch and Sample` in 20; sample pulse 1st half of 20 |
| 22 | -- | `End Op` "(Result True, D3, DC)"; `Final Divide` "(Result True, Shift Ctr Adder Output = 0 D3, DC)"; `Gates 13, 14` (DF, DC); `TC`; sample pulse 1st half; dashed `Inhibit Quotient Sample` "Ctr = 0 (DC, Comp, Result) (Double, Shift Ctr Adder Output = 0)" over 22-23. At the end of 22 these all fall (solid): Shift Control "A", Gate Shift Counter Adder to Register, Gate 21, Subtract Shift Amount, DVDE, Gate 36/72, Shift Control "B", DC, Gate 61, Gate A Exponent to SAU Adder, Gate Shift Counter Register to Adder -- each with a dashed continuation to the end of 24 |
| 23 | -- | "(End Op) Exp Latch and Sample"; "(End Op) Latch ACOB"; "(End Op) Sample ACC 12-59", 1st half; "(End Op) Sample Indicators", 1st half; `Gate & Invert C Exp to SAU Adder` falls at 23 (dashed to 25) |
| 22-24 dashed | "Add Back 1x Divisor" | dashed End Op, Final Divide, Gates 13, 14 in period 24, dashed latches in 25 |

Notes, verbatim:
- "Number of Reduction or Dummy Cycles Depend Upon Number of Quotient Bits
  Developed per Step (Cycle)" (printed twice, at the break, in Part C and D).
- "Note: Any one or more of these intermediate reduction cycles could be a
  dummy cycle. That is if more than 6 quotient bits were developed on the
  previous reduction cycle this would be just a shift cycle."
- "Divider Determined by Multiple Selection Circuits" (brace over 11-20).
- "Update Dividend Exponent by "1" (If Trial Reduction did not Produce an
  Overdraw)"; "(Here if Trial Reduction Produced an Overdraw)" [dashed arrow
  13-15]; "(Here if Trial Reduction did not Produce Overdraw)" [dashed arrow
  15-17]; "(Has no Affect on Divide)".
- Boxed: "Subtract "48" from Dividend & Route to D Reg. Used as Remainder Exp
  on Divide Double."
- At "Add Back 1x Divisor": "Note: This is done if the last reduction cycle
  caused the result to be complement. This is represented by the dotted lines
  above and is done to allow the remainder to be in True form." [printed
  "complement-/ment" across a line break; confirmed on a 200-dpi crop]
- At edge 22: "If Double, go to Figure 3.8.16".

### Sheet 3 -- PDF 241 left half (chart drawn rotated 90 deg), printed 8-19, 2/1/62. Parts E, F, G.

**Part E "ZERO DIVISOR"**, circled edges 1-5.

| period | ring triggers up | rises / pulses | falls at end |
|---|---|---|---|
| 1 | `T0` | "SAMPLE OP CODE TO EXEC REG AND TOB TO C REG" 1st half; `FIRST CYCLE TRIGGER`; an unlabelled level (LA ENABLE on the sibling charts) falls mid-period | T0 |
| 2 | `D3` | "ONE" [so printed; presumably DNE; uncertain] rises | D3; FIRST CYCLE TRIGGER |
| 3 | `D4` | `DIVISOR TRIGGER` rises | D4; "ONE" |
| 4 | `TC` | `END OP`; `STC` | TC; END OP; STC; DIVISOR TRIGGER |
| 5 | -- | "SAMPLE ZERO DVSR IND" pulse, 1st half | -- |

Notes, verbatim: "NOTE 1: FLOATING POINT DIVIDE OR DIVIDE DOUBLE RECIPROCAL
DIVIDE IS TERMINATED IN THE SAME MANNER AFTER 2" [the sentence ends there as
printed]. "NOTE 2: THE TC TRIGGER IS NOW TURNED ON SIMULTANEOUSLY WITH THE END
OP TRIGGER. THIS ACTION SHORTENS THE OPERATION BY 300 NANOSECONDS".
**Total (zero divisor):** END OP in period 4 = 4 periods (T0, D3, D4, TC);
indicator sample in a 5th. NOTE 2 says this is one period (300 ns) shorter
than it used to be.

**Part F "ZERO DIVIDEND"**, edges 8-9: `D4` (D4, NOT DVSR, DVND, F=0) held for
period 8 (an extra D4), then `D3` at 9. An unnamed level rises at 8, annotated
"(TURNED OFF BY D3, DVSR, DVND)"; `ZERO DIVIDEND TGR (ZD)` (D4, DVND, DVSR, F=
REG = 0) rises at 8, "(TURNED OFF BY SDC)"; `SHIFT CONTROL "B"` (ZD, DVND, NOT
DVDE) rises at 8; `GATE 31` (DVSR, DVND) period 8 "(32 ALSO IF DOUBLE
OPERATION)"; "OTHER TGRS NOT AFFECTED"; "RETURN TO POINT 9 PART B, SHEET 1".
Note, verbatim: "NOTE: THIS CYCLE IN EFFECT RESTORES THE OPERATION TO THE START
OF DIVIDEND PRE-NORMALIZATION, THIS TIME WITH SHIFT CONTROL "A". THEREFORE THE
DIVIDEND WILL BE SHIFTED ONLY AS MUCH AS THE DIVISOR". Cost shown: +1 period.

**Part G "DIVIDEND NOT NORMALIZED"**, edges 10-11: `MR-3` (D4, 1X COMP, DVND,
HIGH BIT DIVIDEND = 0) for period 10, then `D3` at 11; "(1X COMP TGR)" and "1X
COMP GATE LINE DIVISOR GATING" fall at edge 10; "RETURN TO POINT 11 PART B,
SHEET 1". Note, verbatim: "THIS CYCLE ALLOWS HIGH ORDER DIVIDEND ZEROS TO BE
SKIPPED; THAT IS, DROPPING DIVISOR GATING LINE DOES NOT ALLOW FOR REDUCTION
CYCLES. QUOTIENT BITS FOR LEADING ZEROS WILL BE ZERO". Cost shown: +1 period
per pass through Part G.

**Totals for FP Divide.**
- Every loop on this figure is a D3/D4 pair = 2 periods: divisor
  pre-normalization loop, dividend pre-normalization loop, trial reduction
  cycle, each intermediate reduction (or dummy) cycle, last reduction cycle.
- Drawn example: T0 = period 1; two divisor loops (D3/D4 in 2-5); two dividend
  loops overlapping the divisor's tail (Part B edges 5-11, DVND up 5-10);
  trial reduction 9-10; intermediate cycles from 11; break; last reduction
  20-21; End Op and TC in 22; latches in 23. That is "22 periods" only by the
  nominal numbering across a broken axis.
- **Number of intermediate reduction cycles: NOT SHOWN** (broken axis, and the
  chart says it depends on quotient bits developed per step, set by the
  "Multiple Selection Circuits").
- Straight-line minimum: NOT SHOWN as a drawn case. How Parts A and B overlap
  when each needs only one loop is not drawn.
- +2 periods if the last reduction left a complement result ("Add Back 1x
  Divisor", dashed, 22-24). +1 for zero dividend (Part F). +1 per Part G pass.

---

## 16. Figure 3.8.16 FLOATING-POINT DIVIDE DOUBLE (TIMING) -- PDF 242 right half, printed 8-20, 2/1/62

Headers, verbatim: "BASICALLY SAME AS DIVIDE TO THIS POINT (SEE SHEET 2, FIGURE
3.8.15)" (arrow at edge 22); "SHOWS 2 REMAINDER NORMALIZATION LOOPS." Edges
22-30. Under the clock: "SHIFT > 6" (about 26-27), "SHIFT <= 6" (about 28-29).
Note, verbatim: "NOTE: IF THE REMAINDER IS COMPLEMENTED AT POINT 22 OF PART C,
SHEET 3 [so printed], FIGURE 3.8.15 IT IS RESTORED (22 TO 24) PART C BEFORE
COMING TO THIS POINT."

| period | ring triggers up (set condition) | rises / pulses | falls at end |
|---|---|---|---|
| 22 | `D4` (D3, DVDE) | `FINAL DIVIDE (FD)` (DC CTR=0 D3, RES TRUE), up 22-29; `GATE 13 & 14` (FD, DC), 22-24; "ROUTE 1X COMP DIVISOR TO ADDER", 22-23; F REG / SHIFT REG / SHIFT COUNTER REG latch & sample pulses, 1st half | D4 |
| 23 | `D3` (D4, DVDE) | -- | D3; GATE SHIFT CTR ADDER TO REG; SUBTRACT SHIFT AMOUNT FROM CTR REG; DVDE; GATE 36 & 72; SHIFT CONTROL "B"; GATE 61; ROUTE 1X COMP DIVISOR |
| 24 | `D4` (D3, DVDE); `TC` (D3, FD) | dashed "(RESULT TRUE) ROUTE A "1" TO INPUT 60 OF ACIB (BECOMES 49 QUOTIENT BIT)"; SHIFT REG and SHIFT COUNTER REG sample pulses, 1st half | D4; TC; DC; GATE A EXP TO SAU ADDER; GATE 13 & 14 |
| 25 | `MR3` (TC, DC DOUBLE) | "READ OUT BACD 64 TGR" (TC, DC, DOUBLE) "(ROUTES D EXP TO SAU ADDER)", 25-27; `NORMALIZE EXPONENT TGR` (TC, DC, DOUBLE), 25-29; `TP6 TGR` (MR3, FD), stays up; `SUPPRESS ADDER OUT POS 51` (FD [printed "FP"?], NOT DC, NOT NM), 25-26 "(THIS POSITION IS HIGH ORDER BIT OF QUOTIENT AND IS NOT WANTED ON REMAINDER NORMALIZATION LOOPS)"; `GATE 61` again "(NOT NM)(FD, NOT DC)", 25-26; `ACOB LATCH`; "SAMPLE ACC 12-63 (61-63 ALWAYS ZERO)", 1st half; "SAMPLE DIVIDE INDICATORS", 1st half; `EXP LATCH & SAMPLE`, one period | MR3; WRITE EXP A TGR; GATE & INVERT C EXP TO SAU ADDER |
| 26 | `T3` (MR3, FD) | `WRITE EXP C` (MR3, FD), 26-28 | T3 |
| 27 | `T4` (T3); `TC` (T3, NE) | `GATE 22 (TGR)` (T3, NE); `GATE 61 & 63 TGR` (T3, FD, NOT NM); `NORMALIZE MANTISSA TGR` (T3, NE) -- all 27-29; F REG and SHIFT REG pulses, 1st half | T4; TC; READ OUT BACD 64 TGR |
| 28 | `T3` (T4, NM) | `EXP LATCH & SAMPLE`, one period | T3; WRITE EXP C |
| 29 | `T4` (T3); `TC` (T3, NE) | `END OP` (T3, NE SH <= 6); `WRITE EXP D TGR` (END OP, FD); F REG and SHIFT REG pulses, 1st half; `GATE 11 & 12` (END OP) from 2nd half | T4; TC; END OP; FD; SHIFT CONTROL "A"; GATE 21; GATE SHIFT COUNTER REG TO ADDER; NE; GATE 22; GATE 61 & 63; NM |
| 30 | (none) | `ACOB LATCH`; "SAMPLE REMAINDER INDICATORS", 1st half; `EXP LATCH & SAMPLE` | -- |

Braces: "TRY FOR 49 QUOTIENT BIT (ADDER LOOP)" 22-25; "QUOTIENT FRACTION TO
ACC" 22-25; "QUOTIENT EXP TO ACC" to 25; "ADDER LOOP TO DETERMINE SHIFT AMOUNT"
25-27; "NORMALIZATION LOOP "1"" 27-29; "LOOP 2 FRACTION TO A CHECKER" from 29;
"UPDATE EXP LOOP "1"" about 27-28; "UPDATE EXP LOOP "2"" 28-30; "EXP TO
CHECKER". Long note, verbatim: "NOTE: WHEN THIS PORTION OF THE OPERATION IS
REACHED, THE REMAINDER RESULT (IN F REG) IS TRUE. THE 1X DIVISOR IS SUBTRACTED
WITH NO LATCH TO THE F REG. ( NO CHANGE TO ORIGINAL TRUE RESULT). IF THE ADDER
OUTPUT RESULT IS STILL TRUE A ONE IS ROUTED TO THE A CHECKER (AND EVENTUALLY TO
ACC) TO BECOME THE 49 QUOTIENT BIT((ACC POS 60)."

**Totals.** Relative to Divide (whose End Op is in nominal period 22): Divide
Double's END OP is in period 29 with two remainder normalization loops, i.e.
**+7 periods**; with one loop (shift <= 6), **+5** (22: D4, 23: D3, 24: D4/TC,
25: MR3, 26: T3, 27: T4/TC with END OP). +2 per extra remainder normalization
loop.

---

## 17. Figure 3.8.17 FLOATING-POINT ADD TO EXPONENT (TIMING) -- PDF 241 right half, printed 8-21, 2/1/62

Notes, verbatim: "NOTE: THIS EXAMPLE SHOWS TWO NORMALIZATION SEQUENCES"; "ADD
IMMEDIATE TO EXPONENT IS IDENTICAL E + I". Circled edges 0-8.

| period | ring triggers up (set condition) | rises / pulses | falls at end |
|---|---|---|---|
| 0 | `T0` (START CTRL) | `LA ENABLE` (up before edge 0, falls mid/late period 0); "SAMPLE OP CODE TO EXEC REG AND TOB TO C REG" 1st half; `FIRST CYCLE TRIGGER` (START CTRL) -- **up periods 0-4**; "GATE A & C EXPONENTS TO VFL ADDER" (ADD EXP, FCT, NOT NE, NOT A+C FLAG), to early period 4; "GATES 31 & 32 - AB 12-107 TO F2-97 = AEXP FCT" (FCT, ADD EXP), to just after edge 5 | T0 |
| 1 | `T1` (T0, ADD EXP) | "GATES 61 & 63 ADDER 0-99 TO F 0-99" (T0, ADD EXP), periods 1-7; `WRITE EXPONENT A` (T0, TO ACC), stays up; "F REG & SCR REG LATCH AND SAMPLE" pulse (T0), 1st half; "EXPONENT ROUTING CONTROL TRIGGER - TP6" drawn dashed-high through period 1 and falling early in period 2, label "(T1, ADD EXP, NOT INT)" | T1 |
| 2 | `T2` (T1, ADD EXP); `TC` (T1, ADD EXP) | -- | T2; TC |
| 3 | `MR 3` (T2, ADD EXP) | `STC` (T2, ADD EXP), one period | MR3; STC |
| 4 | `T3` (MR3, ADD EXP) | "EXPONENT LATCH AND SAMPLE" (MR3, ADD EXP), one period; `NORM EXPONENT TRIGGER` (MR3, ADD EXP), periods 4-7; "GATE A EXP TO VFL ADDER & NORM AMT TO C SIDE" (NE, NOT TP6), to just after edge 8 | T3; FIRST CYCLE TRIGGER |
| 5 | `T4` (T3); `TC` (T3, NE) | `NORM MANTISSA TRIGGER` (T3, NE), 5-7; "GATE 21 & 22 TRIGGERS - SHIFTER 0-99 TO ADDER 0-99" (T3, NE), 5-7; F REG & SCR pulse (T3, NE), 1st half | T4; TC |
| 6 | `T3` (T4, NM, NOT EO) | "EXPONENT LATCH AND SAMPLE" (TC, NOT INT) | T3 |
| 7 | `T4` (T3); `TC` (T3, NE) | `END OP` (T3, NE, SH <= 6); F REG & SCR pulse (T3, NE), 1st half; "GATE 11 & 12 - SHIFTER TO ACIB" (TEST COMP, END OP) from 2nd half | T4; TC; END OP; GATES 61 & 63; NE; NM; GATE 21 & 22 |
| 8 | (none) | "EXPONENT LATCH AND SAMPLE" (TC, NOT INT); "SAMPLE TO ACC - 12-59" pulse, 1st half; `LATCH ACOB` rises mid-period; then (in what would be period 9) "ARITH CHECKER SAMPLE TO ACC 60-107" [last digits faint] pulse | -- |

**Totals.** Drawn (two normalization sequences): END OP in period 7 = 8 periods
(0-7); latches in 8. One sequence (shift <= 6): 6 periods (0-5). +2 per extra
sequence. E+I: "IDENTICAL".

---

## 18. Figure 3.8.18 SAU MULTIPLY AND MULTIPLY AND ADD, PAU SECTION (TIMING) -- PDF 242 left half, printed 8-22, 2/1/62

Two fragments joined by break marks; FP clock rows unnumbered.

**Entry fragment** (three clock periods drawn, then a break):

| drawn period | up |
|---|---|
| e0 | "SIGNAL SSQ TO VFL TRIGGER" (PAU START VFL MPY), one period, with "NOTE: THIS TRIGGER IS USED BUT SINCE A PAU OPERATION IS NOT IN PROGRESS THE ONLY LINE UP WILL BE "SECOND CYCLE START VFL MPY""; from e0 on, each set by (PAU START VFL MPY): `MULTIPLY STATUS TGR (MPY ST)`, `ONE X MULTIPLICAND TGR`, `SHIFT RIGHT 12 TGR` |
| e1 | `MR 3` (SECOND CYCLE START VFL MPY) |
| e2 | `T1` (MR3, MPY ST) |
| e3 (at the break) | `MR1` (T1, MPY ST) begins |

Between the fragments, verbatim: "IDENTICAL TO FLOATING POINT MULTIPLY BETWEEN
THESE POINTS FOR BOTH SAU MULTIPLY AND MULTIPLY AND ADD".

**Exit fragment**, header verbatim: "SHIFT = 0 - (WILL ALWAYS BE ZERO ON SAU
MULTIPLY SINCE PAU EXECUTION REGISTER IS RESET)". `T3` ends at the first drawn
edge; then:
- "(MULTIPLY)": `TC` (T3) and `T4` (T3), one period; `END OP` (T3, NE), same
  period; `LATCH ACOB` (TC, END OP) from the next edge; "SAMPLE TO ACC 12-59"
  pulse, 1st half of the next period; `GATE 11 & 12` (END OP) 2nd half to 1st
  half. "NOTE: SAMPLE TO ACC 60-107 CONTROLLED BY A CHECKER, ALSO A CHECKER
  RETURNS CONTROL TO SAU."
- "MULTIPLY & ADD": `END OP` (T3, NE), same period; `LAST CYCLE` (TC, END OP)
  "SIGNAL SAU"; "SET IN RIGHT 8 SHIFT" (TC, END OP); "SAMPLE SHIFT CONTROL REG"
  (TC END OP SAU OPERATION), 1st half of the next period; "SAU RESUMES CONTROL
  (BEGINS ADDITION)" at that edge.

**Totals.** Shown on this page: 3 entry periods (signal, MR3, T1) and 1 exit
period (T4/TC/END OP). The middle is by reference to 3.8.11: MR1 through T3 =
periods 2-7 there = 6 periods. So the PAU section of an SAU multiply =
3 + 6 + 1 = **10 FP periods**, a splice the chart itself authorises ("IDENTICAL
... BETWEEN THESE POINTS"), no normalization loop ("SHIFT = 0 ... ALWAYS").
The SAU's own byte cycles before and after are not on this chart.

---

## 19. Figure 3.8.19 SAU DIVIDE (TIMING) -- PDF 243 (fold-out, chart on left half), printed 8-23, dated **1/1/63**

Two panels, clock rows unnumbered.

**"DIVISOR NORMALIZATION"** (four periods drawn, a-d, then a fifth edge):

| drawn period | ring | lines |
|---|---|---|
| a | `D4` (TURN ON VFL DIVISOR) (SIGNAL FROM SAU) | each set by (TURN ON VFL DIVISOR) and up a-d: `VFL DIVISOR TGR (VFL DVSR)`, `GATE 61 & 63 (TGR)`; `GATE 21 (TGR)` (continues past d); each set by (VFL DVSR) and up a-d: `SHIFT CONTROL "A"`, "ADD COUNTER REG & SHIFT AMOUNT", "GATE COUNTER ADDER TO REGISTER"; marker "CONTROL TO PAU" |
| b | `D3` (D4, VFL DVSR) | -- |
| c | `D4` (D3, BIT 2=0 VFL DVSR), with "SHIFT <= 6" printed beside it | "F. REG & SHIFT COUNTER REG LATCH & SAMPLE" pulse, 1st half |
| d | `D3` (D4, VFL DVSR) | "DIVISOR NORMALIZED" (D3, BIT 2=1) "SIGNAL TO SAU", one period |
| e | -- | latch & sample pulse, 1st half; marker "RETURN TO SAU" at the edge |

Braces: "LOOP TO ADDER TO DECODE LEADING ZEROS" (a-b), "NORMALIZATION LOOP"
(c-d). Below, unattached: a boxed level labelled "DIVIDEND" [its meaning is not
stated].

**"DIVIDE REDUCTION CYCLES"** (five periods, a break mark, two more periods):

| drawn period | ring | lines |
|---|---|---|
| a | `D4` (PAU START VFL DIVIDE) | each set by (PAU START VFL DIVIDE): `DIVIDE STATUS TGR (DVDE)` (up to the end), `1X COMP TGR` (a-b), `DIVIDEND STATUS TGR (DVND)` (a-b); set by (DVDE): "(GATES 36 & 72 & ENABLE MULTIPLE DECODING)", "GATE COUNTER ADDER TO REG & SUB SHIFT AMOUNT FROM CTR" (to the end); `GATE 21 (TGR)` continuing; marker "FROM SAU" |
| b | `D3` (D4, DVND NORMALIZED) | marker "IF DIVIDEND NOT NORMALIZED TAKE SAME ACTION AS FP" |
| c | `D4` (D3, DVDE) | `SHIFT CONTROL "A & B"` (DVDE, NOT DVND), to the end; "F REG, SHIFT REG, & COUNTER REG LATCH & SAMPLE" pulse, 1st half |
| d | `D3` (D4, DVDE) | -- |
| e | `D4` (D3, DVDE) | latch & sample pulse, 1st half |
| -- break -- | | |
| y | `D4` | latch & sample pulse, 1st half; `FINAL DVDE TGR` (D3, CTR=0, TRUE RESULT) rises -- drawn rising about mid-period y [position uncertain; may be meant at the next edge] |
| z | `D3` (D4, DVDE) | everything falls at the end; marker "RETURN CONTROL TO SAU" |

Printed: "REDUCTION CYCLES JUST LIKE FP".
**Totals.** Divisor normalization, PAU part: 4 periods for the drawn case
(decode loop + one normalization loop, shift <= 6); extra loops not drawn.
Reduction cycles: **NOT SHOWN** (broken axis; "JUST LIKE FP"). Each cycle is a
D4/D3 pair = 2 periods.

---

## 20. Figure 3.8.20 FLOATING POINT RECIPROCAL DIVIDE TIMING -- PDF 244, printed 8-24, dated **1/1/63**

**Outside the stated range (pp.225-243) and not in `ebox_roadmap.md`'s list of
"nineteen" charts: there are twenty.** PDF 245 is printed 9-1, "SIGMA ERRORS
THAT CAUSE A SCAN", Figure 3.9.1, so 3.8.20 is the last chart of the section.

FP CLOCK edges 0-7. At edge 6: "IDENTICAL TO DIVIDE (POINT 3) FROM THIS POINT
EXCEPT FOR *." At edge 7: "* ZERO DIVISOR SEE BELOW".

| period | ring triggers up (set condition) | rises / pulses | falls at end |
|---|---|---|---|
| 0 | `T0` (START CTRL) | "SAMPLE TO C & EXECUTION REG" 1st half; `FIRST CYCLE TGR (FCT)`, **up periods 0-3**; `GATE 33` (DIV I, FST, NOT ID) "(C REG TO ADDER)", 0-1; `GATE A EXP TO SAU ADDER` (DIV I, FCT, NOT ID), 0-1 | T0 |
| 1 | `MR1` (T0, FCT, DIV I) | `GATE 61 & 63 (TGR)` (DIV I, T0), continues; `WRITE EXP D TGR` (T0, DIV I), 1-2; F REG LATCH pulse, 1st half | MR1; GATE 33; GATE A EXP TO SAU ADDER |
| 2 | `MR2` (MR1, DIV I) | `INTERCHANGE DIVIDE TGR (ID)` (MR1, DIV I), 2-5; `SAMPLE TEST COMP`; `GATE 31` "(A REG TO ADDER)", 2-3; `GATE 11` (MR2, DIV I FCT) "(F REG TO CHECKER)", one period; `GATE C EXP TO SAU ADDER` (ID, NOT DNE), 2-3; "EXP LATCH & SAMPLE (MR1 DIV I)", one period; F REG LATCH pulse, 1st half | MR2; WRITE EXP D TGR; SAMPLE TEST COMP; GATE 11 |
| 3 | `MR3` (MR2, FCT, NOT INT, ID) | `LATCH ACOB` (MR2, NOT INT, DIV I, FCT); `WRITE EXP A TGR` (MR2, NOT INT, DIV I, FCT), 3-5 | MR3; FCT; GATE 31; GATE C EXP TO SAU ADDER |
| 4 | `T1` (MR3, ID) | "(SAMPE [sic] TO A REG)" (MR3, ID), 1st half; "DIVIDE NORMALIZE EXP TGR (ONE)" [so printed; DNE] rises, continues; `GATE 21 (TGR)` (MR3, ID), 4-5, then dashed with "SHIFT AMOUNT >6 / <=6"; `BA 64 TGR` (MR3.ID), 4-6 *; `GATE D EXP TO SAU ADDER` (BA64), 4-6 * "(FIRST NORM CYCLE)"; "EXP LATCH & SAMPLE" (MR3, ID), one period; F REG LATCH pulse, 1st half | T1 |
| 5 | `D3` (T1, ID) | `TP6 TGR` (D3, DIV I), continues | D3; ID; WRITE EXP A TGR; GATE 21 (solid) |
| 6 | "DT" [so printed; D4 by position] (D3, DNE) | `DIVISOR TGR (DVSR)` (D3, DIV TYPE), continues; `WRITE EXP C TGR` (D3, DIV TYPE), continues; F REG LATCH pulse, 1st half | D4; BA 64 TGR; GATE D EXP TO SAU ADDER |
| 7 | `D3` | "GATE C EXP TO SAU" (DNE, TP6, NOT 64); "EXP LATCH & SAMPLE" | -- |

Braces: "C FRACTION TO A REG" (0-4), "A EXP TO D REG" (0-2), "A FRACTION TO
ADDER & START DIVISOR NORMALIZATION" (2 onward), "C EXP TO A REG" (2-4), "D EXP
TO C 1ST NORMAL CYCLE" (4-7).

**"ZERO DIVISOR"** sub-chart (FP CLOCK marked *; three periods z0-z2):

| period | ring | lines |
|---|---|---|
| z0 | `TB` (D4 DVSR F=0) | `END OP TGR` (D4, DVSR, F=0), z0-z1; continuing and falling: DVSR (end z1), WRITE EXP C TGR (end z0), BA 64 TGR (end z1), GATE D EXP SAU ADDER (end z1); `GATE 11` (END OP, TEST COMP) from 2nd half of z0 to 1st half of z2 |
| z1 | `TC` (TB) | `WRITE EXP A TGR` (TB, DVSR) "(F REG TO CHECKER)" |
| z2 | -- | `LATCH ACOB` (END OP, NOT INT); "LATCH & SAMPLE EXP" (END OP, NOT INT), one period; "SAMPLE A REG" (END OP, NOT INT), 1st half; "SAMPLE ZERO DIVISOR INDICATOR" (TC, DVSR, NOT INT, END OP), 1st half |

**Totals.** Reciprocal Divide joins Divide at Divide's "point 3" (edge 3 of
3.8.15 sheet 1, where the first D4 rises) at its own edge 6. The two figures
number differently (3.8.20 from 0, 3.8.15 from 1), so count states, not edge
numbers: before the first D4, Reciprocal Divide has T0, MR1, MR2, MR3, T1, D3 =
6 periods; Divide has T0, D3 = 2 periods. **Reciprocal Divide = Divide + 4
periods.** (This rests on reading "(POINT 3)" as edge 3 of 3.8.15 sheet 1; the
ring triggers on both sides of the join, D3 then D4, match that reading.) Zero
divisor here: TB, TC = 2 periods with END OP up for both.

---

## 21. Summary of totals (periods of FP CLOCK from T0 through END OP inclusive)

| fig | operation | drawn example | straight-line case the chart supports | operand dependence shown |
|---|---|---|---|---|
| 3.8.1 | Load (L; LWF "the same") | 5 (2 norm. sequences) | 3 | +2 per extra normalization sequence |
| 3.8.2 | Add | 7 (exp. diff. 11, no norm.) | not on this page (see 3.8.4: 5) | +1 per extra pre-shift of 4 |
| 3.8.3 | Add to Magnitude | 7 (pre-shift 3, forced zero fraction/augment) | not shown | augment pass +2 |
| 3.8.4 | Compare (add class) | 5 | 5 | none drawn |
| 3.8.5 | Add to Fraction | 7 (2 norm. cycles) | 5 | +2 per extra norm. cycle |
| 3.8.6 | Shift Fraction | 7 (shift >3, <12) | not shown | +1 per shift of 4 |
| 3.8.7 | Store | 5 (2 norm. cycles) | 3 | +2 per extra norm. cycle |
| 3.8.8 | Store Rounded | 3 | 3 | none drawn |
| 3.8.9 | Store Low Order | axis broken | NOT SHOWN | counter-driven T3/T4 loop, 2 per pass |
| 3.8.10 | Store Root | 3 (+1 signal) FP periods, then 1 + 48 A-pulse periods, then 4 FP periods | same | none; A-pulse : FP ratio NOT SHOWN |
| 3.8.11 | Multiply | 9 | 9 | none (fixed 4 CSA loops) |
| 3.8.12 | Load Multiplier Reg (LMR) | 5 (2 norm. sequences) | 3 | +2 per extra sequence |
| 3.8.13 | Multiply and Add | 11 solid; 14 dashed (acc. exponent smaller) | 11 | +3 for the dashed case |
| 3.8.14 | Store Multiplier Reg (STM) | 5 (2 norm. cycles) | 3 | +2 per extra cycle |
| 3.8.15 | Divide | nominal 22 across a broken axis; zero divisor 4 | NOT SHOWN | every loop 2 periods; reduction count not shown; +2 add-back; +1 zero dividend; +1 Part G |
| 3.8.16 | Divide Double | Divide + 7 (2 remainder norm. loops) | Divide + 5 | +2 per extra remainder loop |
| 3.8.17 | Add to Exponent (E+, E+I) | 8 (2 norm. sequences) | 6 | +2 per extra sequence |
| 3.8.18 | SAU Multiply, PAU section | 10 (3 + 6 by reference to 3.8.11 + 1) | 10 | none |
| 3.8.19 | SAU Divide, PAU section | divisor norm. 4; reduction: axis broken | NOT SHOWN | 2 per loop |
| 3.8.20 | Reciprocal Divide | Divide + 4 | Divide + 4 | -- |

Observed regularity (mine, from the tables above, not printed anywhere): in
the single-result FP charts the result latches (`LATCH ACOB`, final `EXP
LATCH`) come up in the period AFTER the END OP period, so "periods through END
OP" + 1 is when the result is on the bus latch. Exceptions: 3.8.16 latches the
quotient at period 25, before END OP; 3.8.18's multiply-and-add path hands
back to the SAU with no latch drawn.

## 22. Verbatim text in these pages that defines a duration, a cycle length or a count

There is no body text in this section: pp. 225-244 are charts only. The only
statements of this kind are on the charts:

- PDF 241 (8-19), 3.8.15 sheet 3, NOTE 2: "THE TC TRIGGER IS NOW TURNED ON
  SIMULTANEOUSLY WITH THE END OP TRIGGER. THIS ACTION SHORTENS THE OPERATION BY
  300 NANOSECONDS". (One trigger period = 300 ns; the only time unit printed
  in the range.)
- PDF 240 (8-17/8-18): "Number of Reduction or Dummy Cycles Depend Upon Number
  of Quotient Bits Developed per Step (Cycle)"; "Any one or more of these
  intermediate reduction cycles could be a dummy cycle. That is if more than 6
  quotient bits were developed on the previous reduction cycle this would be
  just a shift cycle."
- PDF 235 (8-11): "SEQUENCE SHOWS NORMALIZATION SHIFT OF 6 OR LESS."; "ALLOW
  FOR F REG SHIFT OF 12 POS 1-37 & 62-85"; "(DELAYED TO ALLOW CSA LOOP TIME TO
  COMPLETE)".
- PDF 226 (8-2): "EXPONENT DIFFERENCE AMOUNT = 11. NO NORMALIZATION." with "PRE
  SHIFT >3", "SHIFT CTR REG >4", "SHIFT CTR REG = 4".
- PDF 233 (8-9): "SET SCR TO 96", "SCR = 96 - 94 - 92 ... 0", "SET RFL TO 47",
  "(DEV ROOT BIT) 1 2 ... 47 48", "B TIMED SCR=0".
- PDF 232 (8-8): "48 TO SH CTR ADDER".
- PDF 242 (8-22): "SHIFT = 0 - (WILL ALWAYS BE ZERO ON SAU MULTIPLY SINCE PAU
  EXECUTION REGISTER IS RESET)".
- The example headers quoted at the top of each section ("EXAMPLE SHOWS TWO
  NORMALIZATION SEQUENCES", etc.).

No chart states a cycle count for an operation in words.

## 23. Which model operations these charts time, and where they disagree with `eboxClocks`

`bsv/StretchTiming.bsv`: `budgetClocks = 2 * iboxCycles + eboxClocks`; for
`Fp`, `iboxCycles` = 2 and `eboxClocks` = Perf. Char. Vol. 1 Table 2
"pre-execution + execution" at the minimum (0.3 us units). **Caveat that
applies to every row:** the charts do not say that their period 0 (START CTRL
-> T0) is where Table 2's pre-execution count starts, so equality or
inequality below is between "chart periods T0..END OP" and "Table 2 pre+exec",
with the origin alignment NOT PRINTED.

The comparison also assumes one FP CLOCK period = one model clock = 0.3 us.
That is `clock_unit.md` sec. 4.2's conclusion, and NOTE 2 on 3.8.15 sheet 3
(one trigger period = "300 NANOSECONDS") is the in-range evidence for it.

**What the table itself shows about alignment (my observation, not printed):**
"periods T0 through END OP inclusive" equals Table 2's pre+exec minimum
exactly for L (3), ST (3), the add class via 3.8.4 (5), F+ (5), E+ (6), * (9),
and for R/ relative to Divide (+4). Seven agreements with one counting
convention is the best evidence available that the origins coincide. Against
that background the three residuals are real differences between the two
documents rather than origin noise: SRD (chart 3, Table 2 4), D/ (chart
Divide + 5, Table 2 Divide + 6), *+ (chart 11, Table 2 20). A possible source
of single-period differences is the engineering change recorded in NOTE 2 (TC
now simultaneous with END OP, one period shorter) if Table 2 predates it; that
is an inference, and it would not explain *+.

Model ops are assigned to charts by the model's own grouping in `eboxClocks`.
The charts name only their title operation: DL/DLWF, +MG/D+/D+MG, M+MG, KMG/
KR/KMGR and D* are NOT named on the charts I assign them to (3.8.1 says only
"LOAD WITH FLAG IS THE SAME"; 3.8.4's IND SAMPLE condition names K, KMG, KR,
KMGR; 3.8.11 mentions "IF THIS IS DOUBLE OPER.").

| model op (Fp code) | `eboxClocks` | chart, straight-line | chart | verdict |
|---|---|---|---|---|
| L (6), LWF (38), DL (70), DLWF (102) | 3 (2+1) | 3 | 3.8.1 | agree; chart adds +2 per extra normalization sequence, which the budget (a floor) does not charge |
| ST (14) | 3 | 3 | 3.8.7 | agree; same +2 rule |
| LFT (74) | 3 | 3 if LFT is the chart's "LOAD MULTIPLIER REG. LMR" | 3.8.12 | mapping uncertain: the chart says LMR, the model has no LMR; LFT = load factor is my guess, not sourced here |
| (none) | -- | 3 | 3.8.14 STM | no model op named STM in `eboxClocks`; mapping not established |
| SRD (46) | 4 (3+1) | **3** | 3.8.8 | **disagree by 1** (chart draws the rounding add inside the first adder pass, END OP in period 2) |
| +, +MG, D+, D+MG (2, 34, 66, 98) | 5 (4+1) | 5 (from 3.8.4, add class, pre-shift <= 3) | 3.8.2, 3.8.4 | agree; chart: +1 per extra pre-shift of 4 (drawn), norm. loop +2 |
| M+, M+MG (10, 42) | 5 | not shown; example with augment 7 | 3.8.3 | no straight-line case drawn; the augment pass (+2) is not in the budget |
| K, KMG, KR, KMGR (18, 50, 22, 54) | 5 | 5 | 3.8.4 | agree |
| F+ (82) | 5 | 5 | 3.8.5 | agree; +2 per extra normalization cycle |
| SHF (114) | 5 | not shown; example (shift 4..11) 7 | 3.8.6 | consistent with 5 + 1 per shift of 4, but the <= 3 case is not drawn |
| E+ (86), E+I (118) | 6 (1+5) | 6 | 3.8.17 | agree; "ADD IMMEDIATE TO EXPONENT IS IDENTICAL" |
| * (26), D* (90) | 9 (5+4) | 9 | 3.8.11 | agree. D* is not separately charted; 3.8.11 only notes a second A sample "IF THIS IS DOUBLE OPER." |
| *+ (58) | 20 (3+17) | **11** (solid), 14 (dashed) | 3.8.13 | **disagree: 20 vs 11/14.** `ebox_roadmap.md` already noted the axis (0-15) is shorter than 20. The chart's sequence is the 3.8.11 spine (8 periods) + T2, T3, T4. Whether Table 2's 17 includes something the chart does not draw (e.g. waiting on the factor) is not shown |
| SLO (78) | 19 (2+17) | NOT SHOWN (axis broken) | 3.8.9 | cannot compare. Chart shows a 48-count T3/T4 loop; see sec. 9 for an inference (17) that is mine, not the chart's |
| SRT (110) | 108 (2+106) | 3(+1) FP, 1+48 A periods, 4 FP | 3.8.10 | cannot compare without the A-pulse : FP-clock ratio, which this figure does not give |
| / (30) | 4 (2+2, floor) | NOT SHOWN | 3.8.15 | chart confirms every loop is 2 periods (Table 2's "2 cycles for each additional ..."); it does not give a minimum or the reduction count. Zero divisor: chart 4 periods (and NOTE 2 says that is 300 ns shorter than before), Table 2's zero-divisor rule (3+2 = 5, as quoted in `docs/ebox_roadmap.md`; I did not re-read Table 2) is one more -- consistent with Table 2 predating NOTE 2's change, but that is an inference |
| D/ (94) | 10 = Divide(4) + 6 | **Divide + 5** (one remainder loop); + 7 drawn (two loops) | 3.8.16 | **disagree by 1** against Table 2's "+6 (remainder norm <= 6)" |
| R/ (62) | 8 = Divide(4) + 4 | Divide + 4 | 3.8.20 | agree with Table 2's "2 + 2 plus all ... of Divide" (state count T0, MR1, MR2, MR3, T1, D3 vs T0, D3) |
| VFL `*` / `*+` (`VflInt`) | no separate budget: all `VflInt` codes get `8 + 2*bytes` | PAU section 10 periods | 3.8.18 | **the model has no multiply-specific VFL budget at all**; Perf. Char. Table 3 gives VFL multiply its own execution figure (3.9 us = 13 cycles per `clock_unit.md` sec. 5.1) |
| VFL `/` (`VflInt`) | same formula | NOT SHOWN (axis broken) | 3.8.19 | no divide-specific VFL budget in the model |
| Connectives | `2*bytes` | -- | none | not charted here (SAU only) |

Also relevant to `bsv/StretchPAU.bsv (was StretchDivBox.bsv)` (standalone, not instantiated): its
header leaves open whether one normalization pass is one cycle or two. On
3.8.15 sheets 1-2 and 3.8.19 every pass (divisor loop, dividend loop, trial,
intermediate, last reduction) is drawn as one `D3` period plus one `D4`
period, i.e. two FP CLOCK periods per pass. The box spends one clock per pass
and per reduction cycle.

## 24. Passages I could not read confidently (re-check these first)

1. 3.8.2 (PDF 226): clock edge numbers 5-7 faint; `GATE 31` note "(A [1]2-59 TO
   ADDER 2-49)"; operator in "(NE [&/=] TP6)"; the 3+4+4 split of the 11.
2. 3.8.3 (PDF 227): "TPB TGR" vs TP6; "(T2, PSA & SN=3)"; the annotation
   "(1 PERFORM AUGMENT TGR & TO ALL OPER)"; "(FC+ 4 ADD)".
3. 3.8.4 (PDF 228): "(T0 & PSA)" on NORMALIZE EXPONENT TGR; "OP LATCH".
4. 3.8.5 (PDF 229): third term of the GATES 31 & 32 condition.
5. 3.8.6 (PDF 230): the operator in "(T4, PSA, SH, CTR ? 4)".
6. 3.8.9 (PDF 232): how many periods the break omits; what "ONE NORMALIZATION
   SHIFT" refers to.
7. 3.8.10 sheet 1 (PDF 233): GATE 11 & 12's half-period position; alignment of
   C-bit pairs to root-bit numbers; where SSQ TGR and PAU DO SSQ TGR fall
   relative to RFL=0/SCR=0 (breaks in every row); sheet 2 "(59) (51)".
8. 3.8.11 (PDF 235): extent of `RESET S & T REG`; whether there are 4 or 5
   delayed S&T latch pulses; "1ST CYC TGR" drawn one period (others two).
9. 3.8.13 (PDF 237): the unnamed level on the FCT TGR row "(COM/CUM, NOT MR2,
   MPY ST)"; solid extent of GATES 71 AND 72; extent of "PASS DATA 1ST LEVEL
   TO II ND LEVEL"; the unlabelled (T3, NE) trigger in the lower block; exact
   mid-period fall points of the trapezoid-drawn gates.
10. 3.8.15 sheet 2 (PDF 240): "(DC, NOT FD, NOT TX)"; the set label of "One
    Times Comp Tgr" (partly smudged: "(D3, DVND, [DVDE-bar?])"); wording of the
    "Add Back 1x Divisor" note's right edge; exact solid/dashed change-over
    edges on the four dashed-then-solid rows.
11. 3.8.15 sheet 3 Part E (PDF 241): "ONE" (DNE?); NOTE 1's truncated ending.
12. 3.8.16 (PDF 242): "(FP, NOT DC, NOT NM)" vs FD; "UPDATE EXP LOOP "1"" start.
13. 3.8.17 (PDF 241): "ARITH CHECKER SAMPLE TO ACC 60-10?"; the TP6 row's
    dashed-high-then-low drawing.
14. 3.8.19 (PDF 243): where FINAL DVDE TGR rises; meaning of the boxed
    "DIVIDEND" level.
15. 3.8.20 (PDF 244): "DT" (D4?); the "+4 over Divide" figure rests on reading
    "(POINT 3)" as edge 3 of 3.8.15 sheet 1 (and on counting states, since the
    two figures number their clocks from 0 and from 1 respectively).
16. General: every "1st half / 2nd half / mid-period" placement was judged by
    eye against the clock row at 180-300 dpi and is the least certain class of
    statement here. Period-level placements of ring triggers and END OP were
    read against the numbered clock edges once per chart, and a second time,
    on a fresh higher-resolution crop, for the three charts behind the
    disagreements in sec. 23 (3.8.8 END OP in period 2; 3.8.13 END OPN solid
    in period 10 and dashed in period 13; 3.8.16 ring row 22-29 and END OP in
    29). Those three second readings matched the first.
