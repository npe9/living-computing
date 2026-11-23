# The I-box, the look-ahead and the memory timing, figure by figure: step 0.3

Written 2026-11-23 for `fidelity_plan.md` step 0.3. This is the **second
half of 0.3**; the arithmetic-unit half is `sau_pau_spec.md`. It covers:

- the I-unit flow diagrams behind milestone A8, R23-9732 Figs 3.1.6-3.1.24
  (the Y-to-Z transfer, index fetch, modification and WBC);
- the look-ahead (LA) flow diagrams, Figs 3.2.1-3.2.27, all of them;
- the memory timing, R23-9732 §4 Procedure 1;
- cross-checks against Perf. Char. Vol. 1 ch.3 Tables 4-8 and its timing
  prose, and against Blosk (TR00.722) Figs 6-10.

No model file was changed. Every reading is from a page image. OCR
(`docs/ocr/`) was used only to find pages.

## 0. How this was read, and what to trust

- **Renders.** Every page was rendered at 300 dpi grayscale (`pdftoppm -r 300
  -gray`), with 400-600 dpi re-renders for small labels, into a scratch
  directory, and read in tiles of 1350 px or less. A fold-out is 5100 × 3300
  px. The renders were deleted afterwards. Tile names (for example
  `t077_3100_2050`) give the crop origin in full-page pixels, so any reading
  can be re-cropped.
- **Who read what.**
  - **The author, first-hand:** Figs 3.2.12, 3.2.13, 3.2.14, 3.2.22-3.2.27 (PDF
    104-106, 114-119); §4 Procedure 1 (PDF 272-279), including Figs
    4.1.1-4.1.4; Table 3.4.1's STORE WAIT and recovery rows (PDF 183). These
    are the figures A6 and A9 build from.
  - **Six parallel readers**, whose transcriptions are Appendices A-F, nearly
    verbatim:
    - A: Figs 3.1.6-3.1.12 (PDF 68-74);
    - B: Figs 3.1.13 sheets 1-3 to 3.1.17 (PDF 75-81);
    - C: Figs 3.1.18-3.1.24 (PDF 82-88);
    - D: Figs 3.2.1-3.2.11 (PDF 92-103);
    - E: Figs 3.2.15-3.2.21 (PDF 107-113);
    - F: Perf. Char. Vol. 1 printed 3-10..3-24 (PDF 28-42), and Blosk
      TR00.722 Figs 6-10 with their prose.
  - **Spot-checks.** The author re-read at least one figure or tile from each
    reader against the image, and each agreed with its transcription:
    - A: Fig 3.1.6, the bottom-bus box "XS READ P (24.00.09.1)" hanging unconditionally off the phase-E line (PDF 68, tile `t068_1600_2200`);
    - B: Fig 3.1.13 sheet 3, the ZOAR / STORE WAIT / PROGRAM STORE COMPARE
      cluster (PDF 77, tile `t077_3100_2050`);
    - C: Fig 3.1.21, "NOT IC FETCH PRIORITY" and the unconditional "BLOCK
      TYPE 2 LD TO LA" (PDF 85, tile `t085_3050_1150`);
    - D: Fig 3.2.2 sheet 2, the LAAR 1/LAAR 2 assignment (PDF 94, whole page),
      and Fig 3.2.5 (PDF 97, whole page). Fig 3.2.4 (PDF 96) was also viewed;
    - E: Fig 3.2.19's LAOP legend (PDF 111, 400 dpi, tile `t111_5750_3250`);
    - F: Perf. Char. printed 3-21 (PDF 39), the LAAR and index-store
      paragraphs.
- **Markings.**
  - PRINTED: what the page says.
  - DERIVED: an interpretation.
  - ILLEGIBLE: given with its reason.
  - REUSED: a page already read in an earlier doc, re-read here and cited.

**The one result that shapes everything below: no I-unit or LA flow diagram
prints a time.** Each of the 49 sheets (Figs 3.1.6-3.1.24, 21 sheets; Figs
3.2.1-3.2.27, 28 sheets) was checked for a clock, a cycle number,
an A/B pulse or a duration. None has one. The only sequencing marks are the
phase names of the timers and sequencers (E, E·M, E·M̄, M, E+M). So the cycle
counts in this file come from Perf. Char. ch.3, Blosk's charts and §4
Procedure 1. They do not come from the flow diagrams. The flow diagrams give
the steps, the conditions and the interlocks.

## 1. Where the figures are: page map

R23-9732 section 3 is paginated by category: "1-n" for category 1, "I Unit
Flow Diagrams", and "2-n" for category 2, "LA Flow Diagrams". The category list
is Index 3-1 (PDF 51); the figure list is Index 3-2 (PDF 52-60). The fold-outs
carry paired printed numbers. Each caption and foot below was read from the
image (a low-dpi caption pass over PDF 61-119, then each page in full).

**Unlike category 8, the I-unit and LA pages are in order.** No fold-out holds
two figures and none is out of sequence. The rules:

- I-unit: Fig 3.1.n is PDF 62+n, for n = 1..12. Fig 3.1.13 takes three sheets
  (PDF 75, 76, 77). For n = 14..27, Fig 3.1.n is PDF 64+n.
- LA: Fig 3.2.1 is PDF 92, and Fig 3.2.2 has two sheets (PDF 93, 94). For n =
  3..27, Fig 3.2.n is PDF 92+n.

| fig | title (as printed) | PDF | printed | foot date | read by |
|---|---|---|---|---|---|
| 3.1.6 | Y-Z START TRIGGER AND YR-ZL TRANSFER SEQUENCER | 68 | 1-11/1-12 | 2/1/62 | A |
| 3.1.7 | YL-ZR TRANSFER SEQUENCER | 69 | 1-13/1-14 | 2/1/62 | A |
| 3.1.8 | YL-ZL TRANSFER SEQUENCER | 70 | 1-15/1-16 | 2/1/62 | A |
| 3.1.9 | YR-ZR TRANSFER SEQUENCER | 71 | 1-17/1-18 | 2/1/62 | A |
| 3.1.10 | ZR MOD REQ TRIGGER AND MOD ZR SEQUENCER | 72 | 1-19/1-20 | 2/1/62 | A |
| 3.1.11 | ZR BLOCK AND SUSPEND TRIGGERS | 73 | 1-21/1-22 | 2/1/62 | A |
| 3.1.12 | ZR FP 1 TRIGGER | 74 | 1-23/1-24 | 2/1/62 | A |
| 3.1.13 sh.1 | ZR FP TRIGGERS 2, 3, 4, AND 6 (SHEET 1 OF 3) | 75 | 1-25 | 2/1/62 | B |
| 3.1.13 sh.2 | (sheet 2 of 3) | 76 | 1-26 | 2/1/62 | B |
| 3.1.13 sh.3 | (sheet 3 of 3) | 77 | 1-27/1-28 | 2/1/62 | B; spot-checked |
| 3.1.14 | ZR IHW TRIGGER, IHW RDY TRIGGER, AND IHW EX ZR TRIGGER | 78 | 1-29/1-30 | 2/1/62 | B |
| 3.1.15 | ZL MOD REQ TRIGGER AND MOD ZL SEQUENCER | 79 | 1-31/1-32 | 2/1/62 | B |
| 3.1.16 | ZL BLOCK AND SUSPEND TRIGGERS | 80 | 1-33/1-34 | 2/1/62 | B |
| 3.1.17 | ZL DEC TRIGGER | 81 | 1-35/1-36 | 2/1/62 | B |
| 3.1.18 | ZL FL PT TRIGGER AND ZL FP 1 TRIGGER | 82 | 1-37/1-38 | 2/1/62 | C |
| 3.1.19 | ZL FP2 TRIGGER | 83 | 1-39/1-40 | 2/1/62 | C |
| 3.1.20 | ZL FP3 TRIGGER | 84 | 1-41/1-42 | 2/1/62 | C |
| 3.1.21 | ZL FP4 TRIGGER AND ZL FP6 TRIGGER | 85 | 1-43/1-44 | 2/1/62 | C; spot-checked |
| 3.1.22 | ZL IHW TRIGGER, ZR WAS IHW TRIGGER, 1 BIT MOD TRIGGER, AND FP Z ALT TRIGGER | 86 | 1-45/1-46 | 2/1/62 | C |
| 3.1.23 | WBC + DEC SEQUENCER AND XF + DEC SEQUENCER | 87 | 1-47/1-48 | 2/1/62 | C |
| 3.1.24 | WBC TRIGGER | 88 | 1-49/1-50 | 2/1/62 | C |
| 3.2.1 | IAUC LOAD ENABLE AND ADVANCE CONDITIONS | 92 | 2-1/2-2 | 2/1/62 | D (REUSED page) |
| 3.2.2 sh.1 | LOOKAHEAD LOAD PULSES (SHEET 1 OF 2) | 93 | 2-3 | 2/1/62 | D (REUSED page) |
| 3.2.2 sh.2 | (sheet 2 of 2) | 94 | 2-4 | 2/1/62 | D; spot-checked |
| 3.2.3 | OPERAND CHECK AND CORRECT PHASE OF INSTRUCTION PREPARATION | 95 | 2-5 | 2/1/62 | D |
| 3.2.4 | BASIC TBC ADVANCE CONDITIONS | 96 | 2-6 | 2/1/62 | D (REUSED page) |
| 3.2.5 | TBC SINGLE ADVANCE CONDITION | 97 | 2-7 | 2/1/62 | D; spot-checked |
| 3.2.6 | TBC MULTIPLE ADVANCE CONDITION | 98 | 2-8 | 2/1/62 | D |
| 3.2.7 | TBC I/O INSTRUCTIONS - OP 20 AND OP 24 | 99 | 2-9 | 2/1/62 | D |
| 3.2.8 | FIRST LEVEL OF SAU INSTRUCTIONS | 100 | 2-10 | 2/1/62 | D |
| 3.2.9 | VFL OPERANDS LAOP 03, 05, AND 07 | 101 | 2-11 | 2/1/62 | D |
| 3.2.10 | VFL SPECIAL OPERAND LAOP 15 | 102 | 2-12 | 2/1/62 | D |
| 3.2.11 | FP INSTRUCTION LEVEL OPX2 | 103 | 2-13 | 2/1/62 | D |
| 3.2.12 | TBC STORE GATE CONTROL | 104 | 2-14 | 2/1/62 | author (REUSED page) |
| 3.2.13 | I BOX STORE TO INTERNAL ADDRESS, LAOP 33 | 105 | **2-15** (the OCR's "2-19" is a misread) | 2/1/62 | author |
| 3.2.14 | ABC ADVANCE | 106 | 2-16 | 2/1/62 | author |
| 3.2.15 | SETTING MAR MODE | 107 | 2-17 | 2/1/62 | E |
| 3.2.16 | FP ABC ACTIONS-TRANSFER INDICATOR TIMER | 108 | 2-19/2-20 | 2/1/62 | E |
| 3.2.17 | VFL ABC ACTIONS-TRANSFER INDICATOR TIMER | 109 | 2-21/2-22 | 2/1/62 | E |
| 3.2.18 | BRANCH ABC ACTIONS-TRANSFER INDICATOR TIMER | 110 | 2-23/2-24 | 2/1/62 | E |
| 3.2.19 | I BOX AND I/O ABC ACTIONS-TRANSFER INDICATOR TIMER | 111 | 2-25/2-26 | 2/1/62 | E; spot-checked |
| 3.2.20 | INTERNAL FETCH ABC ACTIONS-ARITHMETIC BUS TIMER | 112 | 2-27 (right half blank; no 2-28 printed) | 2/1/62 | E |
| 3.2.21 | STORE ABC ACTIONS-ARITHMETIC BUS TIMER | 113 | 2-29/2-30 | 2/1/62 | E |
| 3.2.22 | LA HOUSECLEAN TIMER | 114 | 2-31 | 2/1/62 | author (REUSED page) |
| 3.2.23 | LA HOUSECLEAN OVER TIMER | 115 | 2-32 | 2/1/62 | author |
| 3.2.24 | ABC ACTION ON BAC (LAOP 11) | 116 | 2-33 | 2/1/62 | author |
| 3.2.25 | SCC ADVANCE | 117 | 2-34 | 2/1/62 | author (REUSED page) |
| 3.2.26 | SCC ACTIONS | 118 | 2-35 | 2/1/62 | author |
| 3.2.27 | SCC STORES TO I BOX | 119 | 2-36 | 2/1/62 | author |

Notes on the map:

- **Applicability.** Figs 3.1.14-3.1.20 and 3.1.22-3.1.24 print "CPU 7101 SER.
  NO. 30,004 AND HIGHER". So do Fig 3.1.6 and §4 Procedure 1. Fig 3.1.21 and
  the LA figures print no serial note. 30,004 and higher is the shipped
  machine's series. Stretch serial numbers are discussed in `NEXT.md`; this
  file does not resolve which serials the pages exclude.
- **Dates.** Index 3-2 dates Figs 3.2.16-3.2.21 "1/1/63" (OCR, PDF 54-55), but
  every LA sheet prints 2/1/62 at its foot. The foot is what was printed on
  the sheet. The same split was found for the PAU charts (`sau_pau_spec.md` §1).
- **Fig 3.2.20** is a landscape page whose right half is blank (reader E).
- **§4 Procedure 1** ("ADJUSTMENT OF STORAGE BUS CONTROL AND CORE STORAGE
  TIMING", manual M3-04-4) is **PDF 272-279, printed 1-1 to 1-8**. It starts on
  PDF 272, not 273. The figures are on PDF 279.
- **Table 3.4.1** (7101 CE console indicators) is section 4 printed 4-n. Its
  STORE WAIT row is on **PDF 183, printed 4-24**.
- **Perf. Char. Vol. 1:** printed p.n is PDF n+18 throughout ch.3 (3-11 = PDF
  29, 3-24 = PDF 42; reader F, and consistent with `sau_pau_spec.md` §1).
  **Tables 4-8 are on printed 3-11 to 3-14 (PDF 29-32)**, not on 3-16..3-24.
  Printed 3-15..3-24 (PDF 33-42) carry only the timing prose. Both ranges were
  read.
- **Blosk.** The brief's guess `ADescriptionOfStretch_Dec59.pdf` is not Blosk.
  Blosk is `TR00.722_Stretch_I-Unit_Design_Mar60.pdf` (as `atlas_oracle.md`
  and `clock_unit.md` already cite it). Printed p.n is PDF n+2. The figures are
  Fig 6 p.29/PDF 31, Fig 7 p.32/PDF 34, Fig 8 p.34/PDF 36, Fig 9 p.36/PDF 38
  and Fig 10 p.38/PDF 40.

## 2. The structure the figures agree on

Everything in this section is DERIVED from the figures cited, unless a quote
marks it PRINTED.

### 2.1 The I-box, stage by stage (Figs 3.1.6-3.1.24)

The flow diagrams draw the I-box as a set of triggers and sequencers. A
sequencer is a vertical bar with phase lines M, E·M and E (sometimes E·M̄); a
trigger is a TON/TOF box. In order of an instruction's progress:

1. **Y-to-Z transfer.** The Y-Z START TRIGGER (Fig 3.1.6, 28.26.11.1) starts one
   of four transfer sequencers: YR-ZL (3.1.6), YL-ZR (3.1.7), YL-ZL (3.1.8) and
   YR-ZR (3.1.9). 1Y and 2Y are the two instruction-word buffers. YL and YR are
   the left and right half-words; ZL and ZR are the two decode registers. The
   start is blocked while a modification is pending ("BLOCK Y - Z START TON",
   28.26.11.1, on ZL MOD R, phase M, Fig 3.1.6). It is also gated by "FPR BLOCK
   Y-Z" and by the I checker ("NOT CHKR SING ERR", "CHK M CORR").
2. **Index fetch, in the same phase as the transfer.** At phase E of the
   transfer sequencers, "XS READ P" (24.00.09.1) is drawn unconditionally (Figs
   3.1.6, 3.1.8). The index address goes straight from the Y register to the
   index address bus: "GT 1Y 28-30 TO XAB 1-3", "GT 1Y 31 TO XAB 4" (28.27.52.1)
   for a left half-word, and "GT 1Y 60-63 TO XAB 1-4" for a right one. **So the
   index word is read while the half-word moves Y to Z, before decode.** That
   agrees with Blosk Fig 6's "Y-Z transfer and index fetch" in one cycle
   (TR00.722 p.28, PDF 30, reader F).
3. **Modification.** A MOD REQ trigger per side (ZR: Fig 3.1.10; ZL: Fig 3.1.15)
   and a MOD sequencer (E, E·M, M phases) add the index value to the address.
   "Y - Z M MOD REQ" comes from the transfer sequencer (3.1.7, 3.1.15). "1 BIT
   MOD TRIGGER" (Fig 3.1.22) handles the one-bit index case ("GT 1Y 31 / 2Y 31
   TO XAB 4" with 1BIT MOD R, Fig 3.1.7).
4. **Decode.** ZL DEC TRIGGER (Fig 3.1.17) and the XF + DEC and WBC + DEC
   sequencers (Fig 3.1.23).
5. **Look-ahead load request.** The FP triggers ZR FP 1-6 (Figs 3.1.12, 3.1.13)
   and ZL FP 1-6 (Figs 3.1.18-3.1.21) raise the LA load requests FPL2E, FPL3E and
   FPL4E (left) and FPR2E-FPR4E (right). They do it as typed loads: "TYPE 1 LD
   TO LA", "TYPE 2 LD TO LA", "TYPE 3 LOAD TO LA" / "TYPE 3 LOAD TO BCU", and "T3LD
   TO BCU WAIT FOR ACCEPT" (28.21.74.1). The op code goes "GT ZLOC TO LAOC"
   (28.21.60.1), the address "Z 0-17 TO MAB", and the store tag "SET LA EXT / INT
   STORE TAG" (28.24.82.1).
6. **VFL word-boundary crossing (WBC).** The WBC + DEC sequencer (Fig 3.1.23)
   turns on the WBC test only for a non-immediate VFL instruction ("IMM~ • VFL"
   -> "COND WBC TGR TON", 28.22.02.1). The WORD BOUNDRY CROSSOVER trigger (Fig
   3.1.24) then requests the second word with "W 0-17 TO MAB" (28.21.61.1) under
   VFL 4 E and sets "SET LA WBC TAG" (36.06.01.1).
7. **Instruction half-words (IHW).** "IHW" is a half-word instruction waiting in
   one Z register for its pair (Figs 3.1.14, 3.1.22). IHW EX ZR TGR blocks
   decode and modification of ZL ("BLOCK ZL DEC TON", "BLOCK MOD ZL TON", Fig
   3.1.14).
8. **Block and suspend.** For each Z register, block triggers ("ZR/ZL BLOCK 1Y/2Y
   TGR", 28.42.41.1) and suspend triggers ("ZL SPND 1Y/2Y TGR", 28.42.42.1 /
   .43.1) stop the transfer from a Y register (Figs 3.1.11, 3.1.16). The suspend
   inputs are the IC-fetch side: "IWC2 • ICOR NE • 2Y RD BRU + BRC • NO CHKR SING
   ERR • SAR", and "BR Y-Z XFER TON ZL SPND 1Y". Fig 3.1.16 prints "BLOCK ESTAB(L)
   OF IC FTH PRIORITY (28.42.12.1)" under all four triggers. No TOF is drawn for
   any of them.

**STORE WAIT and I-unit recovery** sit in ALD group 28.42 with block and
suspend:

| ALD | what | where printed |
|---|---|---|
| 28.42.51.1 | "TON STORE WAIT TGR", tested by "ZOAR EQ 11 +12 + 16 - 31" | Figs 3.1.13 sh.2 and sh.3, 3.1.20 (with "BLOCK STORE WAIT TGR TOF"), 3.1.21 (prints "ZOAL") |
| 28.21.71.1 | "VFL 5 CL 2 COND STORE WAIT", tested by "W EQ 11 + 12 + 16 - 31" and "ZL 11 + 12 + 16 - 31" (28.11.55.1) | Fig 3.1.24 |
| 28.42.72.1 | "TON IRCY REQ TGR" (I-unit recovery request), on the STORE WAIT test and on "PROGRAM STORE COMPARE" | Figs 3.1.13 sh.3, 3.1.20, 3.1.21 |
| 28.42.71.1 | "TON PIRCY TGR", on "PROGRAM STORE COMPARE" | Figs 3.1.13 sh.2 and sh.3, 3.1.20, 3.1.21 |
| 28.42.81.1 | "ALLOW LARCY TON", on BE/BEW/BD/SIC-B* or EX + RN | Figs 3.1.6, 3.1.14 |
| 28.42.41-.43.1 | block / suspend triggers | Figs 3.1.7, 3.1.8, 3.1.11, 3.1.16 |
| 28.42.44.1 | "CND SPND INTLK TGR TON", "GEN I EX IN PROG + RCVR TO YR" | Fig 3.1.17 |

Table 3.4.1 (PDF 183, printed 4-24, read by the author) names two of them:
"3R014 28.42.51.1 STORE WAIT LA TO 16-31 OR 11&12" and "3R016 28.42.81.1
LOOKAHEAD RECOVERY MODE". **The console title says what STORE WAIT waits for:
a store by the look-ahead into index words 16-31 or into words 11 and 12.**
The "11 + 12 + 16 - 31" test reads ZOAR (the Z operand address register) for
FP and W or ZL for VFL, which is the address of the instruction being
prepared. **No figure draws what turns STORE WAIT off.** §2.4 gives the
closest evidence for what does.

### 2.2 The look-ahead: five counters over four levels

The CE figures confirm Buchholz §15.3's five counters and give each its own
advance flow:

| counter | advance flow | interlock as PRINTED | AES/LDE triggers |
|---|---|---|---|
| IAUC (instruction unit) | Fig 3.2.1 (PDF 92) | "SCC AT NEXT LEVEL" -> "ABC THERE" -> "TBC THERE" -> "STORE REQUIRED" -> "ABC ADVANCING"; also "NEXT LEVEL IN SCC", "NEXT LEVEL IN ABC", "STORE DONE (STORE DATA M)"; ends "IAUC AES OFF" | SET/RESET IAUC AES |
| OCC (operand check) | Fig 3.2.3 (PDF 95) | "IS IAUC IN THIS LEVEL" NO -> "ADVANCE OCC" | SET OCC AES (38.11.06.1) |
| TBC (transfer bus) | Figs 3.2.4-3.2.13 (PDF 96-105) | "ADVANCE TBC IF NOT INTLKD BY OCC" (3.2.4, 3.2.7-3.2.10); "TBC OCC INT CK" (3.2.5); "TBC OCC INTLK" (3.2.6); "ADVANCE IF NOT INTERLOCKED BY OCC" (3.2.11, 38.21.04.1) | SET/RESET TBC AES, TBC LDE |
| ABC (arithmetic bus) | Fig 3.2.14 (PDF 106); actions 3.2.15-3.2.24 | "ABC TBC INTLKD ?"; "ADV ABC IF NOT INTLKD BY TBC" (3.2.16, 3.2.22, 38.31.05.1) | SET/RESET ABC AES |
| SCC (store check) | Fig 3.2.25 (PDF 117); actions 3.2.26-3.2.27 | "SCC ABC INTLKD ?"; "ADV SCC IF NOT INTLKD WITH ABC" (3.2.26, 38.51.06.1); "ADVANCE SCC IF NOT INTLKD BY ABC" (3.2.27) | SET/RESET SCC AES, SCC LDE |

DERIVED: each counter advances to the next level ("STEP ... TO NEXT LEVEL",
"... AT NEW LEVEL") and sets its AES trigger (the CE trigger index calls it
"ADVANCE ENABLES SEQUENCE TRIGGER", `spec_lookahead.md` §2.1). The level's
action resets AES. The counter advances again when AES is off and its
predecessor does not interlock it. A counter that is DISC (disconnected; e.g.
"DISC IAUC", "DISC OCC", "DISC. ABC", "DISC SCC") skips the action.

**The interlock chain is anticipatory, not a plain "has not reached".** Fig
3.2.25 (SCC ADVANCE) lets the SCC advance onto the ABC's level if the ABC is
itself advancing ("ABC ADVANCING ?" YES, "ANTIC ABC ADV."). Behind that it
asks "ABC TBC INTLKD ?", then "TBC OCC INTLK", then "TBC ADVANCING TOC". The
TBC uses the same pattern (Fig 3.2.6: "TBC ABC INTLK -> ABC WILL RESET AES"),
and so does the IAUC (Fig 3.2.1: "ABC ADVANCING"). So the rule is: a counter
may move onto its predecessor's level in the same step in which the
predecessor leaves it. This bears on how many clocks a full pipe loses per
level.

**The ring order is IAUC -> OCC -> TBC -> ABC -> SCC -> (IAUC).** The IAUC
waits on the SCC (Fig 3.2.1 "SCC AT NEXT LEVEL"), as Buchholz says. Fig 3.2.1
adds that the IAUC may still load a level whose SCC has not finished, if the
SCC is there only for a store that is under way ("STORE BEING DONE", "STORE
DONE (STORE DATA M)").

**Load types and LAARs (Figs 3.2.1, 3.2.2).** The IAUC drives three load-enable
lines and three load pulses:

- TYPE 1 & 2 LOAD ENABLE -> LLP 1 (an I-box-supplied operand: "GI ICOB TO DATA
  FIELD") and LLP 2 (a memory operand: "GI IMOB INTO DATA FIELD", "MEM SEL LA 1");
- TYPE 3 LOAD ENABLE -> LLP 3 (a level that needs a LAAR).

TYPE 3 is enabled when "BOTH LAARS BUSY" is NO, or when it is YES and "STORE
BEING DONE" is YES (Fig 3.2.1). At LLP 3 (Fig 3.2.2 sheet 2, PDF 94,
spot-checked): "I BOX WILL LOAD LAAR 1 OR 2"; "LAAR 1 BUSY" NO -> "SET FROM 1 &
LAAR 1 BUSY"; YES -> "SET FROM 2 & LAAR 2 BUSY" (both 36.16.02.1, 38.53.01.1).
A "MOD TYPE 3" waits first for "FETCH ACCEPTED". **The LAAR assignment is
fixed-priority: LAAR 1 if it is free, else LAAR 2.** The level's FROM 1 / FROM
2 tag records which LAAR it owns. At TBC time the tag selects which LAAR gates
the store address to the bus control unit (Fig 3.2.12: "SET GT LAAR 1 NEXT IN
BCU" / "SET GT LAAR 2 NEXT IN BCU").

**Checker priority.** The I checker is shared between I-box and LA (Perf.
Char. printed 3-19; Blosk p.16). The figures print two of its priorities:

- the OCC's operand check asks "3RD PRIORITY CHKR REQUEST" (38.12.01.1, Fig
  3.2.3), then "DROP "OK TO I CHK" LINE" -> "PREVENT I BOX CHKER CYCLES";
- the SCC's I-box stores ask "REQUEST 4TH PRIORITY FOR I CHKR" (38.52.08.1, Fig
  3.2.26), then "DROP OK TO I CHK" -> "PREVENT I BOX FROM STARTING A CHECK
  CYCLE".

Priorities 1 and 2 are not printed on these pages. DERIVED: they are the I
box's instruction-word check and correct (Fig 3.1.6's "CHK M CORR" and the IWC
sequencers, Figs 3.1.1-3.1.4, not read here). See Gaps.

### 2.3 What a level is, by LAOP

The LA op code (LAOP) a level carries selects its flow at every counter. No
single page prints the code table. The table below is assembled from every
legend and hexagon on Figs 3.2.1-3.2.27. A "legend" is the key printed at a
figure's foot. Codes with an X (X1, X2) are op-class codes printed that way;
DERIVED: X stands for any first digit.

| LAOP | meaning, as PRINTED (figure, PDF) | class (DERIVED) |
|---|---|---|
| 00 | TEST LEVEL (3.2.19 legend, 111) | indicator test |
| 02 | I BOX PSEUDO STORE (3.2.19 legend, 111); "02 PS STORES" (3.2.27 legend, 119) | pseudo-store (index recovery) |
| 03 | VFL FETCH (1 OF 2) (3.2.17, 3.2.20 legends) | VFL first operand |
| 04 | PX PSEUDO STORE (3.2.19 legend); "04 PS STORES" (3.2.27) | pseudo-store |
| 05 | VFL FETCH (1 OF 1) (3.2.17, 3.2.20) | VFL only operand |
| 06 | PX PSEUDO STORE NOOP'D (3.2.19, ditto expanded); "06 PS STORES" (3.2.27) | pseudo-store, no-op'd |
| 07 | VFL FETCH (2 OF 2) (3.2.17, 3.2.20) | VFL second operand |
| 11 | "RAC RCY (NOOP RCY REQ)" (3.2.19 legend; "RAC" at 600 dpi, "BAC" not excluded); Fig 3.2.24's title is "ABC ACTION ON BAC (LAOP 11)" | branch-on-indicator recovery level |
| 13 | STORE / FP STORE (3.2.16, 3.2.21); "13 ARITH STORE" (3.2.27) | FP store |
| 15 | FETCH (SPECIAL) (3.2.17); the VFL multiplicand (3.2.10) | VFL special operand |
| 17 | STORE (1ST) / VFL (1ST) (3.2.17, 3.2.21); "17 ARITH STORE" (3.2.27) | VFL store, first word |
| 21 | STORE (SPECIAL) / VFL (SPECIAL) (3.2.17, 3.2.21); "LAOP 21 ALWAYS EXT STO" (3.2.5) | VFL special store |
| 23 | STORE (2ND) / VFL (2ND) (3.2.17, 3.2.21); "23 ARITH STORE" (3.2.27) | VFL store, second word (WBC) |
| 25 | IO DUMMY NOT CCW (3.2.19) | I/O |
| 27, 55 | "LAOP 27 OR 55" (3.2.14); "LAOP 55,27" -> "BR SUCCESSOR BR UNSUCC" (3.2.6) | branch levels that let TBC and ABC advance together (DERIVED) |
| 31 | "LAOP 33 EXT OR 31" (3.2.12, store from TOB); in "STORE DATA TIMER M 31, 33, 21, 13, 23, 17, X2" (3.2.25); "LAOP 31,57" (3.2.18) | store whose data comes from the level (DERIVED) |
| 33 | I BOX REAL STORE (3.2.19, 3.2.21); "LAOP 33 INT" (3.2.5, 3.2.13); "LAOP 33 ECC CHK LOAD" (3.2.1, 3.2.2) | I-box store, external or internal |
| 35, 43, 75, X1 | SAU instruction levels (3.2.6, 3.2.8 decode legend: X1 38.22.07.1, 35 OR 75 38.22.10.1, 75 and 43 38.22.09.1); "OP X1 INSTR" (3.2.17) | VFL instruction level |
| 37 | BI FETCH (3.2.20) | branch-on-bit fetch |
| 41 | BI (3.2.21 store legend); "LAOP 41" (3.2.14) | branch-on-bit store |
| 42, 44, 46 | "ILLEGAL PS STORE" (3.2.25) | illegal pseudo-store |
| 45 | "45 BR. RECOV" (3.2.27); "45, 47" on "BR. RECOVERY ?" (3.2.18) | branch recovery level |
| 47 | with 45 (3.2.5, 3.2.18) | branch recovery level (second kind) |
| 51 | I BOX INT. FETCH (3.2.19); "51 I BOX FETCH" (3.2.27); I BOX FETCH (3.2.20) | I-box internal fetch |
| 57 | "LAOP 31,57" (3.2.18), "31,57,33, EXT" (3.2.6) | not glossed |
| 63 | INDICATOR ONLY (3.2.19) | indicator-update level |
| 65 | IO DUMMY CCW (3.2.19) | I/O |
| OP 20, OP 24 | IO BX, IO DISC (3.2.7, 3.2.19) | I/O instruction |
| X2 | FETCH OR STORE (3.2.16); FP FETCH / FP STORE (3.2.20, 3.2.21); "X2 ARITH STORE" (3.2.27); "OPX2" FP instruction level (3.2.11) | FP level |

The full per-figure lists are in reader D's and reader E's LAOP tables
(Appendices D and E) and in §4's figure tables.

### 2.4 Stores, the LAAR, store wait and index storage

- **The I box stores through the look-ahead, in order.** Every index-register
  write made ahead by the I box is carried through the LA as a level. These are
  the pseudo-stores, LAOP 02/04/06 (Fig 3.2.19 legend: "I BOX PSEUDO STORE",
  "PX PSEUDO STORE"). The SCC writes them into index storage in program order
  (Fig 3.2.27). A real store into an index word (LAOP 13, 17, 23, X2) takes the
  same SCC path.
- **Index address of a store into index storage** (Fig 3.2.27, PDF 119, phase
  M of "LA TO I TIMER INDEX TRANS."):
  - pseudo-store: "GO OP CODE BITS 1-4 TO I BOX (IX ADDR)" (35.30.01.1);
  - arithmetic store: "GO LAAR BITS 13-17 TO I BOX (IX ADDR)" (35.29.01.1).

  Then "START CLEAR AND WRITE INDEX TIMERS" (35.33.01.1): CLEAR INDEX TIMER,
  then WRITE INDEX TIMER, "SIGNAL I BOX TO START THE INDEX STORAGE CLEAR/STORE
  OPERATION" (35.30.01.1). This is Blosk p.19's two-cycle index store ("one
  for resetting, and the other for writing", reader F).
- **A pseudo-store cancels later stores to the same index word.** PRINTED, Fig
  3.2.27: "NULLIFY ANY OTHER STORE LEVELS THAT ARE ADDRESSED TO THIS SAME IX
  ADDRESS BY SETTING OP BIT 0" (35.31.03.1), on the pseudo-store path only.
- **What releases STORE WAIT (DERIVED, closest evidence):**
  - Perf. Char. printed 3-21 (PDF 39, spot-checked): "A store into index
    storage is a time-consuming operation. Whenever such an instruction is
    decoded, since the next instruction may make use of the new index
    contents, the I-box does no further decoding until the new index contents
    arrives."
  - Blosk p.19 (PDF 21, reader F): "In the case of VFL and FL stores to index
    storage, the I unit loads the store type instruction into lookahead; then
    waits until the entire operation is completed, including the resultant
    store back to index storage."

  The event that completes it on the LA side is Fig 3.2.27's WRITE INDEX TIMER
  (35.33.01.1) for the store's level. **The model's release at the store's
  retirement (`microarchitecture_plan.md` §1a) agrees with both sentences**, if
  "retirement" means the index write, not the E-box result. No figure draws
  the TOF, so this stays DERIVED. For words 11 and 12 (not index storage) the
  analogous completion is the ABC's indicator-register store (Fig 3.2.21:
  "START IND REG TIMER", "ADDR 11 ?"). See Gaps.
- **The LAAR is freed** ("RESET LAAR BUSY TRIG", 38.53.03.1):
  - for an arithmetic store into index storage, by the SCC's write-index timer
    (3.2.27);
  - for an internal fetch or an internal store, at the ABC (3.2.16, 3.2.20,
    3.2.21: "LAAR INT ?" YES -> RESET LAAR BUSY TRIG);
  - for an external store, at the SCC ("STO DATA TIMER", 3.2.26). Perf. Char.
    printed 3-20 says the LAAR stays busy "until the proper operand is
    available, is fetched, checked, and accepted by the MBCU";
  - in housecleaning, by the HSCLN timer, E·M phase (3.2.22).
- **External store data path** (Figs 3.2.12, 3.2.26):
  - store data comes from the TOB (from the level) for LAOP 31 and 33-EXT
    ("SET STO NEXT n TGR" -> "LOAD STORE REG FROM TOB NEXT"), and from the ACOB
    (the E-box result bus) otherwise;
  - the SCC waits for "IS STORE REG READY FOR LA DATA NEXT", then "IS TOB IN
    USE" (NO: "NO TBUS TIMER E+M"), then "IS STAR BUSY" (NO), or "STORE
    ACCEPTED YET" ("NO STORE MEM REQ");
  - then "STO DATA TIMER" (35.02.01.1), phase E: "INFORM STORE REG", "GO LA TO
    TOB".
- **Internal (I-box) store, LAOP 33 to an internal address** (Fig 3.2.13): it
  goes over the transfer bus to the E-box C register ("GI TOB TO C REG",
  35.17.01.1), at TBC time, and only if "PREVIOUS INSTR PROPERLY EXECUTED"
  ("MAR MODE"). The ABC then completes it under its transfer-indicator timer
  and a bus timer ("START A BUS TIMER TO COMPLETE THE STORE OP"). It never goes
  to memory.
- **Store to the indicator register, address 11** (Fig 3.2.14): "STORE TO
  INDICATOR REQ ?" YES "ADD 11" -> "IND. REQ. TIMER ACTION", unless LAOP 41.
  Fig 3.2.21 then gates "GI MODIFIED XR IND'S FROM IND REG TO THE UPDATED INDEX
  IND REG" under "START IND REG TIMER". **A store to $IND updates the I box's
  updated-index-indicator register.**
- **In NOOP mode, stores drain in order.** A no-op'd level with external store
  tags is let through by the TBC only when "ALL PREVIOUS STORES" are done
  ("STAR BUSY AND NO STORE REQ", Fig 3.2.5), and by the ABC only on "PREV STORES
  DONE" (Fig 3.2.14). NOOP mode follows a wrong guess or an interruption.

### 2.5 Forwarding and the program-store compare

- **Store to fetch (Perf. Char. printed 3-21..3-22, PDF 39-40, reader F).** "The
  I-box comparison with the LAAR shows that the operand will be in the LA
  prior to its arrival at the memory. A forwarding mechanism is activated to
  make the store operand available to the fetch level. Further LA loading in
  the I-box is delayed until the forwarding is completed."
- **Fetch to fetch.** "Forwarding is available also for consecutive fetch of
  the same memory operand. Whenever a fetch-type instruction is decoded, the
  fetch address is gated into LAAR unless the latter is busy. This act does not
  make LAAR busy but can allow the forwarding on successive fetches."
- **In the CE figures**, the compare is drawn and the forward is not:
  - Fig 3.2.2 sheet 1 (PDF 93) has "IS LAAR COMPARE ENABLED ?" (36.16.07.1) ->
    "ADDRESS COMPARE ?". Only its NO exit is drawn ("DATA ON IMOB" -> SET LF E
    TRIGGER -> SET LF TAG, GI IMOB INTO DATA FIELD).
  - Fig 3.2.1 has "FETCH ACCEPTED AND NO COMPARE" before "SET IAUC LOAD PULSE
    MEMORY".

  The YES path, the forward itself, is on no page of category 2. See Gaps.
- **Program store compare (a store into a prefetched instruction).** Perf.
  Char. printed 3-21: "When such a store is decoded, I-box invalidates the
  prefetched instructions and waits until the correct information is
  available." Figs 3.1.13 sh.2-3, 3.1.20 and 3.1.21 draw it as "PROGRAM STORE
  COMPARE" -> "TON IRCY REQ TGR" (28.42.72.1) and "TON PIRCY TGR" (28.42.71.1),
  on the FP store paths (FPR4E, FPL4E, "FPL3E AND NO CANCEL").

### 2.6 Recovery: housecleaning, branch recovery, pseudo-interrupt recovery

- **Entering housecleaning** (Figs 3.2.14, 3.2.16, 3.2.22):
  - at the ABC, "PREVIOUS INSTR PROPERLY EXECUTED ?" NO ("INTRUPT") -> "HSCLN
    TIMER WILL SET. HSCLN MODE", or "START HSCLN TIMER" (38.39.02.1);
  - a wrong branch guess also reaches it: Fig 3.2.5's "BR CONDITION MET" YES ->
    "ABC WILL CAUSE HSCLN MODE"; Fig 3.2.18's "SET BR RECOVERY INHB LOAD
    TRIGGER", "SET "I BOX RQST HSCLN" TRIGGER".
- **The HSCLN timer runs once per level the ABC reaches** (Fig 3.2.22: its M
  phase is "ADV ABC IF NOT INTLKD BY TBC", "SET ABC AES", "RESET HSCLN TIMER
  M"). Per level:
  - E·M̄: "GI CNIDC IND TO MK IND", "RESET ABC AES", and "PSEUDO STORE ?" YES ->
    "RESET ABC LF TAG";
  - E·M: "RESET LAAR BUSY TRIG".

  So pseudo-store levels are kept for the SCC to write back, and every other
  level is dropped.
- **First level only:**
  - "SET "INTRPT INHIBIT LOAD" TRIG", "SET "DISABLE INTRPT" TRIG", "SET "I BOX
    RQST HSCLN" TRIG" -> "START I BOX HSCLN TIMER" (38.03.10.1);
  - the execution units are polled: SAU (LAOP X1, 35, 43; a VFL already in
    pre-execution gets "SET "VFL INSTR REJECT" TRIG" and "SIGNAL SAU TO STOP
    HSKPING") and PAU (X2, "PAU IDLE ?");
  - "EXEC UNITS IDLE" -> "SET LA HSCLN MODE TRIG". Then "LA EMPTY ?" -> "START
    LA "HSCLN OVER" TIMER" (38.39.01.1).
- **HSCLN OVER** (Fig 3.2.23, PDF 115), in phase order:
  - E·M̄: reset CN, DF, DS indicators at all levels, MAR MODE, the PAU's MSTR
    TEST CMPLT and FP ENABLE, VFL START, LA HSCLN MODE, and the "INTRPT, PSEUDO
    INTRPT, & BR. RECOVERY INHIBIT LOAD TRIGGERS"; set LA "NOOP IND TEST M";
    "INTRPT ?" NO -> "SET "MAR MODE" AND "MAR NEXT INSTR." TRIGS"; YES -> "SET
    "INTRPT NEXT INSTR" TRIG";
  - E·M: "GI IC BUFFER TO IC REG"; **"GI IND REG XR IND'S INTO UPDATED INDEX
    IND REG"**; "SET PAU'S "WAIT" TRIG"; "GI BIT ADDR. OF LEFT-MOST (SET) IND
    INTO I BOX W REG";
  - M: "SIGNAL I BOX OF HSCLN COMPLETE" (38.02.05.1). The I box acknowledges and
    resets the timer (38.03.08.1). "IF THIS WAS A BR. RECOVERY HSCLN, I BOX WILL
    PLACE THE "BRANCH TO" ADDR IN THE IC REG. TRANSFER THE IC REG INTO THE IAUC
    IC FIELD, THEN GI THE (ABC) IC FIELD INTO THE IC BUFFER" (35.27.02.1).
- **Index recovery is by levels, as Buchholz says:**
  - Buchholz (`spec_lookahead.md` §2.6): "The arithmetic-bus counter identifies
    each level, for which the instruction unit has previously modified an
    index word ... as a pseudo store level. The old contents of the index word
    are placed in the pseudo store level, and the store-check counter is
    responsible for storing this word in the index memory."
  - The CE pages draw exactly that: the HSCLN timer keeps PSEUDO STORE levels
    (3.2.22), the SCC writes them (3.2.27, "WRITE INDEX LA M 02, 04, 06 ...",
    3.2.25), and HSCLN OVER restores the updated-index indicators from the
    indicator register (3.2.23).
  - Pseudo-stores that are illegal are LAOP 42, 44, 46 (3.2.25).
- **Branch-on-indicator resolution (LAOP 11, Fig 3.2.24)**:
  - the level's data field holds "BRANCH TO ADDRESS" (0-18), the "SPECIFIED
    INDICATOR FIELD" (50-55), "I BOX BRANCHED BIT" (59), "RESET INDIC BIT" (61),
    "BRANCH IF ON BIT" (62) and the "ORIGINAL ICR";
  - the ABC compares the indicator with bit 62 and with the I box's guess
    (bit 59). It sets "TFR INDIC TIMER SET BRANCH RECOVERY" (wrong guess) or
    "TFR INDIC TIMER SET PSUDO IRPT RECOVERY", then "DELAY ABC ADV, RESET MAR
    MODE & MSTR TEST COMP" ("RESET LF");
  - the indicator is reset if specified (bit 61): "RESET AE / AH / AL" by bits
    54-55.

  The exact pairing of the YES/NO arrows into the two recovery boxes is drawn
  with crossing lines, so it is DERIVED (§4, Fig 3.2.24).

### 2.7 Memory (Procedure 1) and the bus

§5 has the tables. In short:

- a core storage unit's **Busy trigger is "on for 1800 nanosec"** (PDF 274);
- the data-out gate pulse is 290 ns wide, and comes **"not ... earlier than 1050
  nanosec after select-memory pulse"** (PDF 275);
- IMOB data at the 1Y register and at LA level 4 "should bracket (overlap) the
  **sixth SP pulse**" after the one that started gate I (Fig 4.1.1). SELECT
  1Y/2Y bracket the **fifth and sixth** (Figs 4.1.2, 4.1.3). MEM SEL LA
  brackets the **fifth** (Fig 4.1.4);
- **the procedure prints no bus priority order.** The order comes from Buchholz
  §14.3 printed pp.205-206 (`exchange_and_io.md` §4.1, `spec_lookahead.md`
  §4.3).

## 3. The I-unit figures, 3.1.6-3.1.24

One table per figure: trigger or sequencer, phases, the conditions that branch
it, and what it does. Every figure PRINTS NO TIME. The transcriptions, with
every box and ALD page, are Appendices A-C.

Common to all: the trigger or sequencer is named with its ALD page; phases
are as printed; "->" is a YES exit unless marked. Abbreviations as printed:
SAC, SBC (DERIVED: A-clock / B-clock sample terms), CD 1Y-ZL ("condition 1Y to
ZL"), XAB (index address bus), ABB / AOB (address bus in / out of the index
adder), MAB (memory address bus), ICIB (I-checker in bus), LAOC (LA op-code
field).

### Fig 3.1.6, Y-Z START TRIGGER AND YR-ZL TRANSFER SEQUENCER (PDF 68, 1-11/1-12, 2/1/62; reader A)

| step | condition (PRINTED) | action (PRINTED) |
|---|---|---|
| Y-Z START TON (28.26.11.1) | "(YL-ZR • R MOD)~ + (YR-ZL • R MOD)~ + (XF + DEC ZL MC)~ • SBC" | starts the transfer: COND YR-ZR / YL-ZR / YR-ZL TON CKT |
| YR-ZL sequencer TON (28.15.30.1) | "CHK M CORR • NOT CD Y RIGHT • FPR BLOCK Y-Z" and related | phases M, E·M, E |
| M | ZL MOD R | BLOCK Y - Z START TON; COND XOF 1 TON |
| M | NOT ZL MOD R • ZL FP CL • NOT IHW EX | INSTR PREP COMP ZL |
| M | IHW RDY - ZR and (BE + BEW + BD + SIC-B*) or EX + RN | ALLOW LARCY TON (28.42.81.1) |
| E·M | -- | GT AOB TO ZL |
| E | CD 1Y-ZL / CD 2Y-ZL (with 1BIT MOD L or not) | GT 1Y/2Y 60-63 TO XAB 1-4, or GT 1Y/2Y 63 TO XAB 4 |
| E | (bottom bus, unconditional) | **XS READ P (24.00.09.1)**; TOF Y-Z START TGR |
| E | FP CL 2YR • SBC • CD 2Y-ZL | COND ZL FP 1-4 SET • RESET CKTS |

### Fig 3.1.7, YL-ZR TRANSFER SEQUENCER (PDF 69, 1-13/1-14, 2/1/62; reader A)

| step | condition (PRINTED) | action (PRINTED) |
|---|---|---|
| TON (28.15.10.1) | NORMAL YL-ZR XFER + ANTIC YL-ZR XFER | phases M, E·M, E |
| M | ZR MOD T | BLOCK Y-Z START TGR TON; ZL + ZR PREP NOT BUSY |
| M | (ZR WAS IHW)~ | Y-Z M • MOD REQ (28.70.42.1) |
| M | ZR FP CL • NOT ZR MOD, FP Z ALT TGR OFF | FP RDY ZR (28.20.21.1) |
| E·M | -- | GT AOB TO ZR; GT AOB 32 TO ZR |
| E | MOD REQ decoded from 1YL / 2YL | TON ZR MOD R TGR / SET MOD R TGR (28.26.21.1) |
| E | (1BIT MOD R)~ • CD 1Y-ZR | GT 1Y 28-30 TO XAB 1-3; GT 1Y31 TO XAB 4 (28.27.52.1) |
| E | CD 1Y-ZR, ZR IHW BL IF | TON ZR BLOCK 1Y / 2Y TGR (28.42.41.1) |
| E | CD 1Y-ZR, UNCOND + BIT BR + IND BR 1YL | TON ZR SPND TGR (28.42.43.1); BR Y-Z XFER TON ZR SPND 1Y (28.42.42.1) |
| E | -- | INH NIDC SET IX FR XAC; TOF FPL 3M / FPL 4M / VFL 5M TGR |

### Fig 3.1.8, YL-ZL TRANSFER SEQUENCER (PDF 70, 1-15/1-16, 2/1/62; reader A)

| step | condition (PRINTED) | action (PRINTED) |
|---|---|---|
| TON (28.15.70.1) | S1 + S2 (Appendix A) | phases M, E·M, E |
| M | NOT MOD L RQ | COND WBC + DEC TON (28.15.80.1) |
| M | ZL MOD R | BLOCK GEN OF ZL + ZR PREP NOT BUSY; BLOCK XSF1 E TON (faded) |
| E·M | SAC • 2YL MOD DEC | SET MOD L TGR; COND ZL MOD R TGR (28.26.23.1) |
| E | -- | **XS READ P (24.00.09.1)**; HOLD DATA SELECT PREP |
| E | CD 1Y-ZL / CD 2Y-ZL | GT 1Y/2Y 28-30 TO XAB 1-3, 31 TO XAB 4; GT 1Y 0-17 ... TO ABB; INST PREP TON ZL BLOCK 1Y/2Y |

### Fig 3.1.9, YR-ZR TRANSFER SEQUENCER (PDF 71, 1-17/1-18, 2/1/62; reader A)

| step | condition (PRINTED) | action (PRINTED) |
|---|---|---|
| TON (28.15.60.1) | S1 + S2 | phases M, E·M, E |
| M | NOT ZR MOD F | COND YL - ZL TON CKT |
| M | ZR MOD R | BLOCK GEN OF ZL + ZR PREP NOT BUSY; "BLOCK YSFI E TON" (as printed) |
| E·M | -- | GT AOB TO ZR; GT AOB 32 / 18 / 19 TO ZR |
| E | CD 2Y - ZR | GT 2Y 63 TO XAB 4; TOF FW WBC TGR; TOF Y-Z START TGR; **XS READ P** |
| E | SBC • 2YR MOD DEC + 2YR IB MOD D • SBC | SET MOD R TGR (28.26.21.1) |
| E | 1YR 4 BIT I FLD + 1Y63 ZERO • CD 1Y-ZR | GT 1Y 60-62 TO XAB 1-3 |
| E | FULL WRD 1Y + FULL WRD 2Y | TON FULL WDS TGR (28.26.60.1) |

### Fig 3.1.10, ZR MOD REQ TRIGGER AND MOD ZR SEQUENCER (PDF 72, 1-19/1-20, 2/1/62; reader A)

| step | condition (PRINTED) | action (PRINTED) |
|---|---|---|
| ZR MOD REQ TON (28.26.21.1) | A + B + C + D (Appendix A) | ZR MOD REQ TGR on |
| ZR MOD REQ | YL-ZR M • SAC + SAC • YR-ZR M | TON MOD ZR SEQUENCER |
| ZR MOD REQ | YL-ZR M | BLOCK Y-Z START TGR TON (28.26.11.1) |
| ZR MOD REQ | (always) | BLOCK YL-ZL TON; BLOCK IHW RDY TON; BLOCK GEN OF PREV ZR PREP COMP; BLOCK IHW EX ZR TGR TON |
| M | -- | PREV ZR PREP COMP (28.44.25.1); COND YR-ZL TON CKT; TOF MOD ZR E TGR |
| M | ZR FP CL | COND MOD ZR M TGR TOF; INSTR PREP COMP ZR (28.27.32.1) |
| M | FW NOT S | COND WBC + DEC TON CKT (28.15.80.1) |
| E·M | -- | GT AOB 18 TO ZR (28.27.51.1) |
| E | -- | **X 0-23 TO ABB • X 24-27 TO ABB** (the index value into the adder); TON MOD ZR M TGR; HOLD DATA SELECT PREP |
| E | IHW YL + FW S + FW NOT S | Z 32-49 TO ABB 0-17 PREP; Z 50 TO ABB 18 |

DERIVED: the index word read at the transfer's phase E (XS READ P) is added
to the address at the MOD sequencer's phase E, and the sum returns at E·M
(GT AOB TO ZR). So modification is one sequencer pass after the transfer.

### Fig 3.1.11, ZR BLOCK AND SUSPEND TRIGGERS (PDF 73, 1-21/1-22, 2/1/62; reader A)

| trigger | TON (PRINTED) | actions (PRINTED) |
|---|---|---|
| ZR BLOCK 2Y (28.42.41.1) | SBC • INSTR PREP TON ZR BLOCK 2Y | block 2Y not busy; **block IC FTH priority** (28.42.12.1); block branch ckt IF2Y TON (28.41.31.1) |
| ZR SPND 2Y (28.42.43.1) | S2-T1 + S2-T2 + S2-T3 | 18 blocks of the IF2Y instruction fetch (fetch request, return, ICR/ICA to MAB, ICADV, IWC2); IF2Y M -> COND ICADV E2 TON (28.41.41.1) |
| ZR BLOCK 1Y (28.42.41.1) | SBC • INSTR PREP TON ZR BLOCK 1Y | the same, for 1Y |
| ZR SPND 1Y (28.42.42.1) | TON SUSPEND TGR • SBC + BR Y-Z YFER TON ZR SPND 1Y • SBC | 13 blocks of the IF1Y fetch |

The mirror of Fig 3.1.16. Reader A lists as printed but unclear: "IWCI E",
"ICOA NE", "BRU", "IF1YE" on the 2Y bus, "IL FTH", "F02Y" and "YFER".

### Fig 3.1.12, ZR FP 1 TRIGGER (PDF 74, 1-23/1-24, 2/1/62; reader A)

| condition (PRINTED) | action (PRINTED) |
|---|---|
| (FP CL 1YL • CD 1Y-ZR • FWS + HW) + (FWS + HW • CD 2Y-ZR • FP CL 2YL), then YL-ZR E | TON ZR FL PT TGR; BLOCK FP Z ALT TGR TON |
| SET ZR FP1 + T2 | ZR FP1 TGR on (28.26.50.1) |
| FP1 | BLOCK WBC + DEC TON |
| SAC • ZRXS • ZR INSTR PREP COMP • ZR + ZL PREP NOT BUSY • XOF1 NM | TON XOF1 (28.12.11.1), the index operand fetch (Table 3.4.1 3H006 "INDEX OPERAND FETCH 1 MEMORY TGR") |
| ZR EQ 1 • ZR INSTR PREP COMP XOF1 E | XOF1 TC FTH (24.00.09.1) |
| ZR 1 + 2 + 3 • IRPT ENBLD ... GT FPR IND TO LA | SET LA DF (33.01.02.1); DF SET LANOP |
| SAC • XOF 1M • LA EN T1 + 2 • CHKR EN T1 • NOT CHKR SING ERR • ZR INSTR PREP COMP | TON FPR 4 (28.14.41.1) |
| FPR 3E | Z 32-49 TO MAB; GT ZROC TO LAOC (28.21.60.1) |
| FPR 3 E • NO CANCEL • FPR 3 M • ZR 4 MNT MD | PANEL KEY REQUEST |
| ZR XS LTH, FPR 4E • M | TYPE 1 LD TO LA (28.21.72.1) |
| FPR 4E • ZR ADDR 8 LTH | SET LA EXT / INT STORE TAG (28.24.82.1) |
| ZR INT LTH, FPR4E / • SBC / • M | SET LA INT FETCH (36.03.02.1); TYPE 3LD TO LA; TYPE 3LD TO BCU (28.21.74.1) |

DERIVED: an FP operand in index storage (ZR XS) goes to the LA as a TYPE 1
load, with the I box's data. An external operand is a TYPE 2 load, fetched
from memory into the level. An internal-address operand is a TYPE 3 load,
which takes a LAAR and goes to the bus control unit (BCU). That is Perf. Char.
p.3-20's "its fetch uses the store mechanism".

### Fig 3.1.13, ZR FP TRIGGERS 2, 3, 4 AND 6, sheets 1-3 (PDF 75-77, 1-25 / 1-26 / 1-27/1-28, 2/1/62; reader B, sheet 3 spot-checked)

No sequencer bar on any sheet. Phases appear only inside conditions (FPR4E,
FPR4E·M, SBC).

| sheet | condition (PRINTED) | action (PRINTED) |
|---|---|---|
| 1 | "SET 7R FP 2" or the 1Y21-25 decode • COND FP CL R | TON ZR FP 2 TGR (28.26.51.1) |
| 1 | INSTR PREP COMP ZL • FP Z ALT TGR OFF, no checker request | COND IWC1 / IWC2 TON CKT |
| 1 | BLOCK FP RDY • ZR INSTR PREP COMPL • ~CANCEL FPL3E, then SAC • FPL 3NE • I CHKR EN • NOT CHKR SING ERR • LA EN T 1 & 2 | TON FPR 4 (28.14.41.1) |
| 1 | FPR 4E • SBC, or FPR 4E • FPR 4M | FPR 4 E • M TYPE 1 LD (28.21.72.1) |
| 2 | 1Y NOT 23 • 1Y 24 • 1Y25 • COND FP CLR, or SET ZR FP 3 | TON ZR FP 3 TGR |
| 2 | FPR 4E | Z32-49 TO MAB; TYPE 3LD TO BCU / TO LA (28.21.74.1) |
| 2, 3 | FPR4E -> "ZOAR EQ 11 +12 + 16 - 31" (28.42.51.1) | **TON STORE WAIT TGR** (28.42.51.1); **TON IRCY REQ TGR** (28.42.72.1) |
| 2, 3 | FPR4E -> PROGRAM STORE COMPARE | TON IRCY REQ TGR (28.42.72.1); TON PIRCY TGR (28.42.71.1) |
| 3 | FPR3E AND NO CANCEL -> PROGRAM STORE COMPARE. ACCEPT OR COMPARE | TON IRCY REQ TGR |
| 3 | ZR EXT LTH • ZR INSTR PREP COMPLETE • ~FPDD ~M • LAAR 1 BUSY (28.10.11.1) | COND FPDD E TGR |
| 2, 3 | ZR EXT / INT LTH • FPR 4E | SET LA EXT / INT STORE TAG (36.09.14.1 / .15.1); T3 LD TO BCU WAIT FOR ACCEPT (28.21.74.1) |

**The prior reading of sheet 3 is confirmed** (`microarchitecture_plan.md` §1a
row "STORE WAIT and I-unit recovery"). It adds the two PROGRAM STORE COMPARE
branches. Sheet 3 is printed upright, not rotated.

### Fig 3.1.14, ZR IHW / IHW RDY / IHW EX ZR TRIGGERS (PDF 78, 1-29/1-30, 2/1/62; reader B)

| trigger | condition (PRINTED) | action (PRINTED) |
|---|---|---|
| IHW RDY ZR TGR | NOT ZR MOD • SAC • YL-ZR M • ZR IHW AND ZL MT | TON |
| ZR IHW TGR (28.26.61.1) | ZL MT; SAC • MOD ZR M | COND / TON IHW RDY and IHW EX ZR |
| IHW EX ZR TGR (28.26.11.1) | SET IHW EX TGR; NOT ZR MOD • SAC | unconditional: BLOCK XF+ DEC TON; BLOCK GEN OF INSTR PREP COMP ZL; BLOCK MOD ZL TON; BLOCK ZL DEC TON |
| (recovery) | EX + RN; BE + BEW + BD + SIC-BE-BEW-BD (28.89.32.1) | ALLOW LARCY TON (28.42.81.1) |
| (index) | -- | COND XSF3 TON CKT (28.71.11.1) |

### Fig 3.1.15, ZL MOD REQ TRIGGER AND MOD ZL SEQUENCER (PDF 79, 1-31/1-32, 2/1/62; reader B)

| step | condition (PRINTED) | action (PRINTED) |
|---|---|---|
| MOD REQ TON (28.26.23.1) | one of five decodes (SET MOD L TGR; SBC • IYL MOD DEC • YL-ZLE; ...) | TON ZL MODIFY REQUIRED TGR |
| MOD REQ (always) | -- | BLOCK WBC+DEC TON, BLOCK XF+DEC TON, BLOCK YL-ZR / YR-ZR TON, BLOCK ZR WAS IHW TOF, BLOCK GEN OF INSTR PREP COMPL ZL, COND MOD ZL TON |
| MOD REQ | ZR WAS IHW | Y - Z M MOD REQ (28.70.42.1) |
| sequencer TON (28.15.40.1) | e.g. "OK TO MOD ZL • YR-ZL M • NOT CHKR SING ERR • NOT IHW-EX T • FW NOT ST • SAC • ZL MOD REQ"; "SAC • NO LA CHKR REQ • ..." | MODIFY ZL SEQUENCER on |
| E | -- | TON MOD ZL M TGR WITH NEXT SBC; X 0-23 / 24-27 TO ABA; SET IDC ON IAUC ERR; RST ZL TAGS |
| E·M | various | GT AOB 18 / 24 / 19 TO ZL |
| M | ZL IHW T • ZR MT | IHW RDY E1 / E2 |

The E, E·M and M lines meet one continuous trunk, so the phase split is
DERIVED (reader B). "NO LA CHKR REQ" in the TON: **modification waits for the
I checker to be free of an LA request.**

### Fig 3.1.16, ZL BLOCK AND SUSPEND TRIGGERS (PDF 80, 1-33/1-34, 2/1/62; reader B)

| trigger | TON (PRINTED) | actions (PRINTED, unconditional) |
|---|---|---|
| ZL BLOCK 1Y TGR (28.42.41.1) | INSTR PREP TON ZL BLOCK 1Y • SBC | BLOCK GEN OF 1Y NOT BUSY (and ANTIC); **BLOCK ESTAB OF IC FTH PRIORITY** (28.42.12.1) |
| ZL BLOCK 2Y TGR (28.42.41.1) | INSTR PREP ZL BLOCK 2Y • SBC | the same for 2Y; BLOCK BR CKT IF2Y TON |
| ZL SPND 1Y TGR (28.42.42.1) | IWC2 • ICOR NE • 2Y RD BRU + BRC • NO CHKR SING ERR • SAR; or SBC • BR Y-Z XFER TON ZL SPND 1Y; or E1 TON SPND TGRS • SBC | BLOCK GEN OF IF1Y FTH REQ / ONE TO MAB 15 / GT ICA 0-16 TO MAB / PNL KEY REQ; BLOCK IF1Y TOF; COND IF2Y ANTIC TON CKT |
| ZL SPND 2Y TGR (28.42.43.1) | similar inputs | similar, for 2Y |

No TOF is drawn for any of the four. DERIVED: block holds the transfer from
a Y buffer; suspend holds the instruction fetch into that buffer, e.g. while
a branch's target is fetched.

### Fig 3.1.17, ZL DEC TRIGGER (PDF 81, 1-35/1-36, 2/1/62; reader B)

| step | condition (PRINTED) | action (PRINTED) |
|---|---|---|
| upper bus | -- | I EX USE ZL ... CONT CKTS; BLOCK ZL DEC TOF TGR TOF; BLOCK DEC ZR / USE ZR / I EX USE ZR (28.60.11.1) |
| upper bus | ZL IHW • SBC • I EX GOING | TOF MOD ZL M TGR |
| error column | ZLNA ON + ZLXA ON + ZLSA ON | ZL BR ADR INVLD (28.51.07.1) |
| error column | SET ZL IDC ON I PAR ERR; COND IDC FR UNCOR ERR; LA PAR ERR; **XS ADR CKK • SET ZLIDC ON XAC**; MEM CKK | TON ZLIDC (28.51.03.1) |
| Z18 | -- | CND SPND INTLK TGR TON (28.42.44.1); GEN I EX IN PROG + RCVR TO YR |
| -- | -- | SET LAAD (28.25.20.1); decoders Z17-Z31 |

"BLK DEC" YES is drawn into the decode bus, which may be a drafting error
(reader B).

### Fig 3.1.18, ZL FL PT TRIGGER AND ZL FP 1 TRIGGER (PDF 82, 1-37/1-38, 2/1/62; reader C)

| condition (PRINTED) | action (PRINTED) |
|---|---|
| NOT IHW E • NOT ZL MOD R • YR-ZL M, then FP Z ALT TGR ON | FP RDY ZL TO LA CONT COMMON COM CKTS (28.20.21.1); COND FP INCOMPL TGR TON CKT (28.42.53.1) |
| FPL 3 E TGR ON (28.13.32.1) | GT ZLOC TO LAOC; Z 0-17 TO MAB (28.21.60.1) |
| ZL INT LTH, FPL 4 E TGR ON | Z 0-17 TO MAB; SET LA INT FTH (36.03.02.1) |
| FPL 4 E TGR ON • SBC; FPL 4 M•E TGR ON | TYPE 3 LD TO LA; TYPE 3 LD TO BCU (28.21.74.1) |
| ZL XS LTH -> FPL 4 E • M; FPL 4 E • SBC | TYPE 1 LD TO LA (38.03.01.1) |
| ZL ADDR 8 LTH • FPR 4E | SET LA INT / EXT STORE TAG (28.24.82.1) |

### Fig 3.1.19, ZL FP2 TRIGGER (PDF 83, 1-39/1-40, 2/1/62; printed upright; reader C)

| condition (PRINTED) | action (PRINTED) |
|---|---|
| NOT IHWE • NOT ZL MOD R • YR - ZL M; FP Z ALT TGR ON | FP RDY ZL TO LA CONT COMMON COM CKTS |
| SBC • FPL 4 E TGR ON; FPL 4 E TGR ON • FPL 4 M TGR ON | TYPE 1 LD TO LA (28.21.72.1) |
| Z 24 -> IF INHBT OP • GT FPL IND TO LA | OP SET LANOP (28.25.40.1) |

### Fig 3.1.20, ZL FP3 TRIGGER (PDF 84, 1-41/1-42, 2/1/62; reader C)

| condition (PRINTED) | action (PRINTED) |
|---|---|
| FPL 4 E TGR ON (28.13.43.1) -> "ZOAR EQ 11 + 12 + 16 - 31" (28.42.51.1) | **TON STORE WAIT TGR** (28.42.51.1); **BLOCK STORE WAIT TGR TOF** (28.42.51.1); TON I RCY REQ TGR (28.42.72.1) |
| FPL 4 E TGR ON -> PROGRAM STORE COMPARE (28.42.71.1) | TON PIRCY TGR |
| FPL 4 E TGR ON -> PROGRAM STORE COMPARE (28.42.72.1) | TON I RCY REQ TGR |
| FPL 4 E • FPL 4 M; FPL 4 E • SBC | L T3 LD E • M TO LA (38.03.01.1); L T3 LD E • M TO BCU (15.01.01.1) |
| ZL EXT / INT LTH • FPL 4E | SET LA EXT / INT STORE TAG (28.24.82.1) |

"BLOCK STORE WAIT TGR TOF" is the only box on any sheet that touches STORE
WAIT's turn-off. It blocks the TOF while the condition holds; it does not
say what turns it off.

### Fig 3.1.21, ZL FP4 TRIGGER AND ZL FP6 TRIGGER (PDF 85, 1-43/1-44, 2/1/62; upright, different lettering, no serial note; reader C, spot-checked)

| condition (PRINTED) | action (PRINTED) |
|---|---|
| "NOT IC FETCH PRIORITY" (28.20.23.1) | COND FPL2E TON (28.13.21.1). No NO exit drawn |
| (unconditional, off the same column line, below the hexagon) | BLOCK TYPE 2 LD TO LA (28.13.33.1) |
| (unconditional, column A of the "ZL FP4 OR ZL FP6" bus) | a second COND FPL2E TON (28.13.21.1) |
| FPL3E | ZO-17 TO MAB; GT ZLOC TO LAOC (28.21.60.1) |
| FPL4E | Z0-17 TO MAB; SET ADR 13 ON MAB; BLOCK XFER OF ZLOC TO LAOC; SET LAOC 6, 8 & 9; SET LAOP TAG |
| FPL3E AND NO CANCEL • SBC / • FPL3M | TYPE 3 LOAD TO LA; T3LD TO BCU WAIT FOR ACCEPT (28.21.74.1); MODIFIED TYPE 3 LOAD TO LA (28.21.75.1) |
| FPL4E -> "ZOAL EQ 11+12+16-31" (28.42.51.1; "ZOAL" as printed here) | TON STORE WAIT TGR; TON 1RCY REQ TGR |
| FPL4E -> PROGRAM STORE COMPARE (28.42.71.1) | TON PIRCY TGR; TON 1RCY REQ TGR |
| FPL3E AND NO CANCEL -> PROGRAM STORE COMPARE . ACCEPT OR COMPARE | TON IRCY REQ TGR |

### Fig 3.1.22, ZL IHW, ZR WAS IHW, 1 BIT MOD AND FP Z ALT TRIGGERS (PDF 86, 1-45/1-46, 2/1/62; reader C)

| trigger | condition (PRINTED) | action (PRINTED) |
|---|---|---|
| FP Z ALT | INSTR PREP COMP ZL / ZR | FP RDY ZL / FP RDY ZR (28.20.21.1); COND FP INCOMP TON CKT (28.42.53.1) |
| FP Z ALT TON term | SBC • ZR FP CL • TOF FP RDY R • ZL EXT PREP • FPL 3E • ZL FP T (28.27.37.1) | -- |
| ZL IHW, ZR WAS IHW, 1 BIT MOD | Appendix C | -- |

DERIVED: FP Z ALT alternates the two Z registers' FP instructions into the LA.

### Fig 3.1.23, WBC + DEC SEQUENCER AND XF + DEC SEQUENCER (PDF 87, 1-47/1-48, 2/1/62; reader C)

| sequencer / phase | condition (PRINTED) | action (PRINTED) |
|---|---|---|
| WBC + DEC, E | (unconditional) | GT AOB 0-17 + P 0-17 TO W (28.02.01.1) |
| WBC + DEC, E | Z 35•36•37•38•39•40 ZERO (25.04.01.1) -> SUM 18•19•20•21 TO MEM AREA DEC (28.14.02.1) | WORD BNDRY CROSSOVER (28.22.02.1); IC - W - Z ABA; IC - Z ABA P1 |
| WBC + DEC, E·M | "IMM~ • VFL" (28.15.81.1) | **COND WBC TGR TON** (28.22.02.1) |
| WBC + DEC, E·M | "VFL • IMM~" (28.15.81.1) | GT AOB 19 TO ZL (28.27.50.1) |
| XF + DEC, E and M | Appendix C | -- |

The prior reading is confirmed (`atlas_oracle.md` "Indexed immediates").
Reader C adds that the E-line WORD BNDRY CROSSOVER test has no IMM or VFL
gate drawn.

### Fig 3.1.24, WBC TRIGGER (PDF 88, 1-49/1-50, 2/1/62; reader C)

| condition (PRINTED) | action (PRINTED) |
|---|---|
| SAR WBC TEST E o M o WRD BNDRY X OVER (28.22.02.1) | TON WORD BOUNDRY CROSSOVER TGR |
| VFL CL 2 + VFL CL 3 + VFL CL 4 • WBC~ • VFL CL 2~ (28.22.10.1) -> VFL 4 TYPE 3 + VFL 4 TYPE 2 (28.22.50.1) -> VFL 4 E ON (28.11.42.1) | W 0-17 TO MAB (28.21.61.1) |
| VFL 4 E (28.24.25.1) | SET LOAC POS 8 (36.09.11.1); BLOCK SET OF LAOC POS 6 |
| GT ZROC TO LOAC (28.24.80.1) | SET LA WBC TAG (36.06.01.1) |
| "W EQ 11 + 12 + 16 - 31" -> VFL CL 2 • VFL 5E (28.11.55.1) | **VFL 5 CL 2 COND STORE WAIT** (28.21.71.1) |
| "ZL 11 + 12 + 16 - 31" -> VFL C2 • VFL 5E (28.11.55.1) | VFL 5 CL 2 COND STORE WAIT |
| W EQ INT (28.22.20.1) | COND VFL 4 T3 (28.22.21.1) |
| -- | BLOCK GEN ZL EXT / INT NOT WBC (28.22.20.1) |

No IC FETCH PRIORITY test and no recovery request on this sheet.

## 4. The LA figures, 3.2.1-3.2.27

There is one table per figure. Each reader's full box-by-box transcription is in
Appendices D and E. The author's own readings (Figs 3.2.12-3.2.14 and
3.2.22-3.2.27) appear here in full. No figure prints a time.

### Fig 3.2.1, IAUC LOAD ENABLE AND ADVANCE CONDITIONS (PDF 92, printed 2-1/2-2, 2/1/62; reader D)

| step | condition(s) (PRINTED) | action(s) (PRINTED) | ALD | notes |
|---|---|---|---|---|
| on advance | — | SET IAUC ADV EN SEQ; RESET LOAD PULSE MEMORY; RESET LC, NOOP, IJ AT NEW LEVEL; STEP IAUC TO NEW LEVEL; INFORM BCU OF NEW IAUC LEVEL | 38.01.06.1; 38.01.10.1; 36.02.03.1, 33.01.16.1, 36.07.03.1; 38.01.01.1; 38.61.01.1 | |
| disc | DISC IAUC YES | RESET IAUC AES; DROP LOAD ENABLE LINES | 38.01.01.1 | disconnected level skipped |
| enable | DISC IAUC NO, RECOVERY NEEDED NO, LOAD STARTED NO (AES ON) | TYPE 1 & 2 LOAD ENABLE | 38.02.02.1 | |
| enable 3 | BOTH LAARS BUSY NO, or BOTH LAARS BUSY YES and STORE BEING DONE YES | TYPE 3 LOAD ENABLE | 38.02.03.1 | [KEY] LAAR gate |
| load | LOAD STARTED YES (LLP 1/2) | RESET IAUC AES | 38.01.01.1 | |
| cancel | MEM FETCH CNCLD YES | SET IAUC AES; re-test BOTH LAARS BUSY | 38.01.06.1 | [KEY] fetch cancelled |
| pulses | LLP1 / LLP2 / LLP3 MOD / LAOP 33 ECC CHK LOAD & I CHKR ECC ERR NO / FETCH ACCEPTED AND NO COMPARE | SET IAUC LOAD PULSE MEMORY | 38.01.10.1 | |
| advance | SCC AT NEXT LEVEL NO; or SCC AT NEXT LEVEL YES & ABC THERE & TBC THERE NO & STORE REQUIRED NO & ABC ADVANCING; or NEXT LEVEL IN ABC NO & (STORE REQ. NO or STORE DONE YES (STORE DATA M)); and then IAUC AES OFF YES | ADVANCE IAUC | 38.01.08.1 | interlock IAUC vs SCC/ABC |

Interlocks (the reader's list):

- IAUC vs SCC: "SCC AT NEXT LEVEL"; "NEXT LEVEL IN SCC".
- IAUC vs ABC: "ABC THERE", "ABC ADVANCING", "NEXT LEVEL IN ABC".
- IAUC vs TBC: "TBC THERE".
- IAUC self: "IAUC AES OFF" before ADVANCE IAUC.

### Fig 3.2.2 sheet 1, LOOKAHEAD LOAD PULSES (SHEET 1 OF 2) (PDF 93, printed 2-3, 2/1/62; reader D)

| step | condition (PRINTED) | action (PRINTED) | ALD | notes |
|---|---|---|---|---|
| LLP 1 | — | GI TAG BITS & OP CODE FIELD EXCEPT BIT 8; GI I BOX IND'S TO IND. FIELD; GI IC TO IC FIELD; GI ICOB TO DATA FIELD; SET LF & LC TAGS | 36.10.01.1; 35.09.01.1; 35.09.01.1; 35.02.01.1; 36.01.10.1 | I-box-supplied operand |
| LLP 1 | LAOP 45 NO | GI OP CODE BIT 8 | 36.09.01.1 | |
| LLP 1 | LAOP 45 YES & I CHKR PARITY ERROR | SET OP BIT 8 | 36.09.02.1 | |
| LLP 1 | I CHKR PARITY ERROR & PSEUDO STORE OR RECOVERY LEVEL | SET CNIDC IND | 38.03.05.1 | [KEY] |
| LLP 1 | I CHKR PARITY ERROR & not pseudo-store/recovery | SET IJ IND; SET NOOP TAG | 33.01.16.1; 35.09.04.1 | [KEY] |
| LLP 2 | — | GI TAG BITS & OP CODE FIELD; GI I BOX IND'S TO IND FIELD; GI IC TO IC FIELD | faint | memory operand |
| LLP 2 | LAAR compare not enabled, or ADDRESS COMPARE NO; DATA ON IMOB YES (MEM SEL LA 1) | SET LF E TRIGGER -> SET LF TAG, GI IMOB INTO DATA FIELD | see table | [KEY] |
| LLP 2 | BOUNDARY ALARM | SET DF OR DS IND; SET NOOP TAG | 35.09.02.1, 35.09.04.1; 35.09.02.1 | |
| LLP 2 | MEM CHK ALARM | SET IJ IND; SET [?] NOOP TAG | ILLEGIBLE | |

Interlocks (the reader's list):

None between counters on this sheet.

### Fig 3.2.2 sheet 2, LOOKAHEAD LOAD PULSES (SHEET 2 OF 2) (PDF 94, printed 2-4, 2/1/62; reader D; spot-checked)

| step | condition (PRINTED) | action (PRINTED) | ALD | notes |
|---|---|---|---|---|
| LLP 3 | — | GI TAG BITS AND OP CODE; GI I-BOX IND'S TO IND FIELD; GI IC TO IC FIELD; I BOX WILL LOAD LAAR 1 OR 2 | 36.10.01.1, 36.09.01.1; 35.09.01.1; 35.09.01.1 | |
| LLP 3 | LAAR 1 BUSY NO & (MOD TYPE 3 NO, or MOD TYPE 3 YES & FETCH ACCEPTED) | SET FROM 1 & LAAR 1 BUSY | 36.16.02.1, 38.53.01.1 | [KEY] LAAR 1 chosen first |
| LLP 3 | LAAR 1 BUSY YES & (same) | SET FROM 2 & LAAR 2 BUSY | 36.16.02.1, 38.53.01.1 | [KEY] |
| LLP 3 | LAOP 33 ECC CHK LOAD | GI ICOB WITH ECC | — | |
| LLP 3 | ECC ERROR NO | SET LF & LC TAGS | 36.02.02.1, 36.01.10.1 | |
| LLP 3 | ECC ERROR YES | LAOP 33 ECC CORRECT LOAD -> SET LF & LC TAGS; GI ICOB WITH ECC; (UNCORR ECC ERR -> SET NOOP TAG) | faint | |
| LLP 3 | LAOP 33 NO, MODIFIED TYPE 3 NO | SET LF & LC TAGS | 36.02.02.1, 36.01.10.1 | |
| LLP 3 | I BOX STORE | GI ICOB WITH ECC; (I-PAR ERROR -> SET IJ & NOOP) | 38.03.07.1 | |

Interlocks (the reader's list):

None between counters.

### Fig 3.2.3, OPERAND CHECK AND CORRECT PHASE OF INSTRUCTION PREPARATION (PDF 95, printed 2-5, 2/1/62; reader D)

| step / phase | condition (PRINTED) | action (PRINTED) | ALD | notes |
|---|---|---|---|---|
| advance | — | SET OCC AES; STEP OCC TO NEXT LEVEL | 38.11.06.1; 38.11.01.1 | |
| skip | DISC OCC YES, or OPD CHK REQ NO (LC ON) | to advance test | | |
| request | OPD CHK REQ YES (LF NOT LC), CHK STARTED NO (OCC AES ON) | 3RD PRIORITY CHKR REQUEST | 38.12.01.1 | [KEY] checker priority |
| wait | CHKR IN USE YES, or IS CHKR NEED BY LAST USER FOR CORR CYC YES | loop to 3RD PRIORITY CHKR REQUEST | | [KEY] |
| grant | CHKR IN USE NO (NO "0" REQ) | DROP "OK TO I CHK" LINE; PREVENT I BOX CHKER CYCLES | 35.01.02.1 | [KEY] OCC blocks I-box checker use |
| check E | — | GO DATA FIELD TO ICIB | 35.10.02.1 | |
| check EM̄ | — | RESET OCC AES; DROP "NO 0 REQ" LINE TO HOLD I CHKR PRIORITY | | |
| check EM̄ | PANEL KEYS OR INVALID ADDRESS NO / YES (OCC INT FETCH TAG) | SIGNAL I CHKR TO CHK ECC / SIGNAL I CHKR TO GENERATE PARITY | 35.15.01.1 | |
| check M | — | GI ICOB DATA PARITY RESIDUE | 35.10.01.1 | |
| check M | ECC ERROR | SET LC TAG | 35.15.01.1 | |
| check EM | ECC ERROR NO | to advance test | | |
| correct | ECC ERROR YES | START OPERAND CORRECT TIMER; CONTINUE GATING DATA TO ICIB | 35.05.02.1; 35.10.02.1 | |
| correct EM | — | DROP "NO 0 REQ" LINE TO HOLD CHKR PRIOR | | |
| correct (right line) | — | GI ICOB AGAIN; SET LC TAG | | |
| correct | DBL ERR YES | SET IJ IND NOOP TAG | 33.01.16.1, 36.07.07.1 | |
| advance test | IS IAUC IN THIS LEVEL NO | ADVANCE OCC | | **OCC interlocked by IAUC** |

Interlocks (the reader's list):

- OCC vs IAUC: "IS IAUC IN THIS LEVEL" NO -> ADVANCE OCC.

### Fig 3.2.4, BASIC TBC ADVANCE CONDITIONS (PDF 96, printed 2-6, 2/1/62; reader D)

| step | condition (PRINTED) | action (PRINTED) | notes |
|---|---|---|---|
| advance | — | SET TBC AES; TBC AT NEW LEVEL | |
| bypass | DISC / HSC IN MODE / NOOP MODE YES | TBC SINGLE ADV. COND | [KEY] housecleaning bypass |
| normal | NO | EXECUTE IF REQUIRED | |
| AES reset | TBC EXECUTED / ABC TRANS INDS ONLY / ABC TNT FETCH / ABC STORE ACTION | RESET TBC AES (4 boxes) | |
| advance | single path, or TBC AES OFF YES | ADVANCE TBC IF NOT INTLKD BY OCC | interlock |

Interlocks (the reader's list):

- TBC vs OCC: "ADVANCE TBC IF NOT INTLKD BY OCC".
- TBC waits on ABC actions: "ABC TRANS INDS ONLY", "ABC TNT FETCH", "ABC STORE ACTION" reset TBC AES.

### Fig 3.2.5, TBC SINGLE ADVANCE CONDITION (PDF 97, printed 2-7, 2/1/62; reader D; spot-checked)

| step | condition (PRINTED) | action (PRINTED) | notes |
|---|---|---|---|
| advance | — | RESET TBC LDE; SET TBC AES; STEP TBC TO NEXT LEVEL | |
| LDE | DISC NO & LF & LC ON | SET TBC LDE | |
| bypass | DISC / HSCLN MODE | to TBC OCC INT CK | [KEY] houseclean |
| noop | NOOP MODE & LAST LEVEL NO (IC OFF) | to bus | |
| noop store | NOOP MODE, LAST LEVEL, EXT STORE NO, ABC ACTION COMPLETE OK (AND CKT 3C) | to bus | |
| noop store | NOOP MODE, LAST LEVEL, EXT STORE YES, ALL PREVIOUS STORES (STAR BUSY AND NO STORE REQ; AND CKT 3A) | to bus | [KEY] |
| branch | LAOP 45 OR 47 & not BRANCH RECOVERY IN PROG & (LAOP 47, or SIC BRANCH (NO IC), or BR CONDITION MET NO) | to bus | [KEY] |
| branch taken | BR CONDITION MET YES | ABC WILL CAUSE HSCLN MODE | [KEY] wrong-way recovery via houseclean |
| store ops | LAOP 17 EXT STO / 23 EXT STO / NOOP 13 NOT INT STO / LAOP 21 ALWAYS EXT STO / LAOP 04 | to bus | |
| int | LAOP 33 INT & ABC ACTION TAKEN (A TIMER M) | to bus | |
| | LAOP 11 OR 63 & BAC REC REQ NO & ABC ACTION TAKEN (TFR IND E+M) | to bus | |
| advance | TBC OCC INT CK NO | ADVANCE TBC | interlock |

Interlocks (the reader's list):

- TBC vs OCC: "TBC OCC INT CK" NO -> ADVANCE TBC.
- TBC vs ABC: "ABC ACTION COMPLETE OK", "ABC ACTION TAKEN" (x2).

### Fig 3.2.6, TBC MULTIPLE ADVANCE CONDITION (PDF 98, printed 2-8, 2/1/62; reader D)

| step | condition (PRINTED) | action (PRINTED) | notes |
|---|---|---|---|
| advance | — | RESET TBC LDE; SET TBC AES; STEP TBC TO NEXT LEVEL | |
| I/O | LDE ON, LAOP 20 OR 24 | T BUS TIMER; RESET TBC AES; I/O RESPONSE -> bus | |
| VFL operand | LAOP 03, 07'15 (NOT INT chain) | T BUS TIMER; RESET TBC AES; M -> bus | |
| VFL | LAOP 05 | T BUS TIMER; RESET TBC AES; M -> bus | |
| SAU/PAU first | LAOP X1, 35, 75, 43 or LAOP X2 NOT INT | T BUS TIMER; RESET TBC AES; FP 1ST CYC / VFL 1ST CYC; SET FST CYC MEM; IF NOT INT STO -> bus | |
| branch | LAOP 55, 27 | T BUS TIMER; RESET TBC AES; BR SUCCESSOR BR UNSUCC -> bus | [KEY] |
| ABC wait | TBC ABC INTLK YES | ABC WILL RESET AES | [KEY] |
| | INT FETCH YES & LOOP 51 NO | -> bus | |
| | INT FETCH NO & (LAOP 41,23,17 / 00,40,02,42,25,65 / 31,57,33, EXT) | -> bus | |
| advance | TBC AES OFF YES & TBC OCC INTLK NO | ADVANCE TBC | interlock |

Interlocks (the reader's list):

- TBC vs ABC: "TBC ABC INTLK".
- TBC vs OCC: "TBC OCC INTLK" NO -> ADVANCE TBC.
- TBC self: "TBC AES OFF".

### Fig 3.2.7, TBC I/O INSTRUCTIONS - OP 20 AND OP 24 (PDF 99, printed 2-9, 2/1/62; reader D)

| step / phase | condition (PRINTED) | action (PRINTED) | ALD | notes |
|---|---|---|---|---|
| advance | — | SET TBC AES; TBC AT NEW LEVEL | 38.21.03.1 | |
| gate | IS LEVEL READY (TBC LDE ON); NOOP'D/NOOP MODE NO; IO INSTR (OP X00) | — | 38.22.03.1 | |
| gate | ABC-SCC INTLKD YES | GO OP CODE BITS 1-4 LEVELS TO IO DECODER; SIGNAL BX & DISC SYNC TO READ/WRITE/CONTROL/LOCATE/RELEASE OR CCW (AND) SEOP | 35.28.01.1; 38.68.01.1 | [KEY] I/O waits for pipe drain (DERIVED) |
| gate | TBC-ABC INTLKD YES; PREVIOUS INSTR. PROPERLY EXECUTED YES (MAR MODE); TBC ACTION TAKEN YET NO (TBC AES ON) | START TRANSFER BUS TIMER | 38.25.01.1 | |
| E. M | — | RESET TBC AES | 38.21.03.1 | |
| M | BX / OP 20; DISC / OP 24 | SELECT BX; SELECT DISC SYNC | 38.68.02.1 | |
| E or M | — | GO DATA FIELD LEVELS ON TO B | 35.16.01.1 | |
| reaction | HAS BX OR DISC ACCEPTED YES, or REJECTED YES | SET IO REACTION STORAGE TRIGGER | 38.25.03.1 / 38.25.02.1 | |
| reaction | — | RESET TB TIMER M; DROP SELECT SIGNAL; DROP ACCEPT OR REJECT SIGNAL | 38.25.02.1; 38.68.02.1 | |
| response | — | SET IO BUFFER TRIGGER (RESET); SET IO RESPONSE TRIGGER | | |
| advance | — | ADV. TBC IF NOT INTLKD BY OCC; SET TBC AES; RESET TBC LDE; RESET IO RESPONSE TRIGGER | 38.22.15.1 | interlock |

Interlocks (the reader's list):

- ABC vs SCC: "ABC-SCC INTLKD". TBC vs ABC: "TBC-ABC INTLKD". TBC vs OCC: "ADV. TBC IF NOT INTLKD BY OCC".

### Fig 3.2.8, FIRST LEVEL OF SAU INSTRUCTIONS (PDF 100, printed 2-10, 2/1/62; reader D)

| step / phase | condition (PRINTED) | action (PRINTED) | ALD | notes |
|---|---|---|---|---|
| advance | — | SET TBC AES; TBC AT NEW LEVEL | 38.21.03.1 | |
| select | LEVEL READY (TBC LDE ON); not NOOP; 35, 75 43, X1 | — | 38.22.07.1/10.1/09.1 | |
| branch-type | LAOP ? YES, BB OR BI, INTRPT BI | SIGNAL SAU OF INTRPT BI INSTR / OF BI INSTR. / OF BB INSTR. | 38.23.05.1; 36.11.02.1 | DERIVED: BB/BI = branch-on-bit / branch-on-indicator |
| start | TBC ACTION TAKEN YET NO (TBC AES ON) | START TRANSFER BUS TIMER | 38.25.01.1 | |
| E.M̄ | — | RESET TBC AES; SET VFL START TRIGGER; ENABLE SAU TO START PRE-EXECUTION | 38.21.03.1; 38.23.05.1 | |
| E + M | — | GO DATA FIELD ON TOB; GO OP CODE & WBC TO SAU | | |
| handshake | HAS SAU ACCEPTED THE DATA YES ("SAU HSKPING") | RESET VFL START TRIGGER; SET FIRST CYCLE MEM. TRIGGER | 38.23.05.1; 38.24.01.1 | |
| advance | — | ADV TBC IF NOT INTLKD BY OCC; SET TBC AES; RESET TB TIMER M; RESET TBC LDE; RESET "FIRST CYCLE MEM" TRIG | 38.22.15.1; 38.24.01.1 | interlock |

Interlocks (the reader's list):

TBC vs OCC: "ADV TBC IF NOT INTLKD BY OCC". (No ABC/SCC interlock test on this sheet.)

### Fig 3.2.9, VFL OPERANDS LAOP 03, 05, AND 07 (PDF 101, printed 2-11, 2/1/62; reader D)

| step / phase | condition (PRINTED) | action (PRINTED) | ALD | notes |
|---|---|---|---|---|
| advance | — | SET TBC AES; TBC AT NEW LEVEL | 38.21.03.1 | |
| gate | LEVEL READY (TBC LDE ON); NOOP'D NO; OPERAND IN LA DATA FIELD (INT TAG OFF) | — | | |
| gate (03, 05) | TBC-ABC INTLKD YES; PREVIOUS INSTR. PROPERLY EXECUTED YES (MAR MODE) | — | | first VFL operand waits for ABC |
| start | TBC ACTION TAKEN YET NO (TBC AES ON) | START TRANSFER BUS TIMER | 38.25.01.1 | |
| E.M̄ | — | RESET TBC AES | 38.21.03.1 | |
| E.M̄ | FIRST OR ONLY (03, 05) / NO | GI TOB TO C REG / GI TOB TO D REG | 35.17.01.1 | |
| E.M̄ | LAST, OR ONLY (05, 07) | SET SAU GO TRIGGER; SIGNAL SAU TO STOP HSKPING & START EXECUTION | 38.23.04.1 | |
| | HAS SAU STARTED EXECUTION YES ("SAU HSKPING" OVER) | RESET SAU GO TRIGGER | 38.23.04.1 | |
| M | — | ADV TBC IF NOT INTLKD BY OCC; RESET TBC LDE; SET TBC AES; RESET TB TIMER M | | interlock |
| E + M | — | GO DATA ON TOB | | |

Interlocks (the reader's list):

TBC vs ABC: "TBC- ABC INTLKD ?" (first/only operand only). TBC vs OCC: "ADV TBC IF NOT INTLKD BY OCC".

### Fig 3.2.10, VFL SPECIAL OPERAND LAOP 15 (PDF 102, printed 2-12, 2/1/62; reader D)

| step / phase | condition (PRINTED) | action (PRINTED) | ALD | notes |
|---|---|---|---|---|
| advance | — | SET TBC AES; TBC AT NEW LEVEL | 38.21.03.1 | |
| gate | LEVEL READY; NOOP'D NO; LAOP 15; OPERAND IN LA DATA FIELD (ALWAYS / INT TAG OFF); IS C REG EMPTY YES (VFL RDY FOR MCND) | SET VFL WAIT FOR MULTIPLICAND TRIG.; SEND A SIGNAL TO SAU TO BLOCK ITS MPYC ACTION | 38.22.11.1; 38.24.03.1; 38.23.05.1 | |
| start | TBC ACTION TAKEN YET NO (TBC AES ON) | START TRANSFER BUS TIMER | 38.25.01.1 | |
| E.M̄ | — | RESET TBC AES; GI TOB TO C REG; GI RESIDUE FROM TOB TO A CHKR; RESET "VFL WAIT FOR MCND" TRIGGER; REMOVE SAU MPYC BLOCK | 38.21.03.1; 35.17.01.1; 38.23.03.1; 38.24.03.1 | |
| E + M | — | GO DATA ON TOB | 35.16.01.1 | |
| M | — | ADV. TBC IF NOT INTLKD BY OCC; RESET TBC LDE; SET TBC AES; RESET TB TIMER M | | interlock |

Interlocks (the reader's list):

TBC vs OCC: "ADV. TBC IF NOT INTLKD BY OCC". No ABC interlock test on this sheet.

### Fig 3.2.11, FP INSTRUCTION LEVEL OPX2 (PDF 103, printed 2-13, 2/1/62; reader D)

| step / phase | condition (PRINTED) | action (PRINTED) | ALD | notes |
|---|---|---|---|---|
| advance | — | SET TBC AES; TBC AT NEW LEVEL | | |
| gate | INST PREPARATION COMP YES (LF & LC ON); DISC OR NOOPED NO; HSCLN OR NOOP MODE NO; OP X2 YES | — | | [KEY] HSCLN |
| decode | LATE DECODE ENABLE ON YES | GO OP CODE ON TOB | 35.28.01.1 | |
| start | IS OPERAND IN INT REG NO (INT TAG OFF); TBC ACTION TAKEN NO (TBC AES ON) | STAPT T BUS TIMER | 38.25.01.1 | |
| EM̄ | — | RESET TBC AES; GI TOB TO C REG; SIGNAL PAU & SAU TO START | 38.21.03.1; 38.23.01.1; 38.23.01.1 | |
| E + M | — | GO DATA FIELD ON TOB | 35.16.01.1 | |
| start ack | HAS PAU STARTED YET YES | SET 1ST CYC MEM TGR | 38.24.01.1 | |
| advance | INT STORE NO | ADVANCE IF NOT INTERLOCKED BY OCC; RESET TBC ADE, 1ST CYC MEM, T BUS M | 38.21.04.1 | interlock |

Interlocks (the reader's list):

TBC vs OCC: "ADVANCE IF NOT INTERLOCKED BY OCC" (38.21.04.1). No ABC interlock test on this sheet.

### Fig. 3.2.12, TBC STORE GATE CONTROL -- PDF 104, printed 2-14, 2/1/62. Read first-hand (REUSED page, re-read)

Logic: 38.22.16.1 (printed once, for the page). PRINTS NO TIME.

| # | box (PRINTED) | exits (PRINTED) |
|---|---|---|
| 1 | entry "TBC ADV" -> STEP TBC TO NEXT LEVEL | |
| 2 | hex TBC AES ON | YES -> 3 |
| 3 | hex TBC LDE ON | YES -> 4 |
| 4 | hex EXT STORE | YES, line labelled "EXT STO & NOT INT STO TAGS" -> 5 |
| 5 | hex FROM 1 | YES -> SET GT LAAR 1 NEXT "IN BCU", and -> 7a; NO -> 6 |
| 6 | hex FROM 2 | YES -> SET GT LAAR 2 NEXT "IN BCU", and -> 7b |
| 7a | hex LAOP 33 EXT OR 31 | YES -> SET STO NEXT 1 TGR -> LOAD STORE REG FROM TOB NEXT "FOR LAAR 1"; NO -> RESET STO NEXT 1 TGR -> LOAD STORE REG FROM ACOB NEXT "FOR LAAR 1" |
| 7b | hex LAOP 33 EXT OR 31 | YES -> SET STO NEXT 2 TGR -> LOAD STORE REG FROM TOB NEXT "FOR LAAR 2"; NO -> RESET STO NEXT 2 TGR -> LOAD STORE REG FROM ACOB NEXT "FOR LAAR 2" |

NO exits of 2, 3, 4 and 6 are not drawn. DERIVED: the store data comes from
the transfer bus (TOB, i.e. from the look-ahead level itself) for LAOP 31 and
33-external, and from the E-box result bus (ACOB) for every other external
store. Two LAARs ("LAAR 1", "LAAR 2"), and "FROM 1/2" tag bits select which
one gates the address to the bus control unit (BCU). Agrees with
`spec_lookahead.md` §1.4.

### Fig. 3.2.13, I BOX STORE TO INTERNAL ADDRESS, LAOP 33 -- PDF 105, printed 2-15 (OCR "2-19" is a misread), 2/1/62. First-hand

PRINTS NO TIME (beyond the names of timers and their E / M phases).

| # | box (PRINTED) | ALD | exits (PRINTED) |
|---|---|---|---|
| 1 | ADVANCE -> SET TBC AES; TBC AT NEW LEVEL | | |
| 2 | hex IS LEVEL READY FOR TBC ACTION ? | | YES ("TBC LDE ON") -> 3 |
| 3 | hex NOOP'D OR NOOP MODE | | exit to 4 labelled "NO" (the NO label sits on the entry line; DERIVED: not noop'd -> 4) |
| 4 | hex LAOP 33 ? | 38.22.10.1 | YES -> 5 |
| 5 | hex LAAR AT INT ADDR ? | 38.32.05.1 | YES ("INT STORE") -> 6 |
| 6 | hex TBC-ABC INTLKD ? | | YES -> 7 (as printed; DERIVED: probably "not interlocked" in sense, the label may be the drafting convention for "condition satisfied") |
| 7 | hex PREVIOUS INSTR PROPERLY EXECUTED ? | | YES ("MAR MODE") -> 8 |
| 8 | hex TBC ACTION TAKEN YET ? | | NO ("AES ON") -> 9 |
| 9 | START TRANSFER BUS TIMER | 38.25.01.1 | phase E·M̄ -> RESET TBC AES; GI TOB TO C REG (35.17.01.1). Phase E+M -> GO DATA FIELD ON TOB (35.16.01.1). Phase M -> dashed box "ABC ACTION": hex ABC TR. IND TIMER M ? YES -> START A BUS TIMER TO COMPLETE THE STORE OP |

DERIVED: an I-box store to an internal address (LAOP 33 with LAAR at an
internal address) is done over the transfer bus into the E-box's C register,
only when the previous instruction was properly executed ("MAR MODE"), and
completed under the ABC's transfer-indicator timer and an arithmetic-bus
timer. It is never sent to memory.

### Fig. 3.2.14, ABC ADVANCE -- PDF 106, printed 2-16, 2/1/62. First-hand

PRINTS NO TIME.

| # | box (PRINTED) | exits (PRINTED) |
|---|---|---|
| 1 | ADVANCE -> SET ABC AES; ABC AT NEW LEVEL | |
| 2 | hex DISC. ABC ? | YES -> hex ABC TBC INTLKD ? (NO -> ADVANCE ABC); NO -> 3 and -> NOOP MODE branch (11) |
| 3 | hex LEVEL PREPARATION FINISHED ? | YES ("LF & LC ON") -> 4 |
| 4 | hex HSCLN MODE ? | YES ("HOUSECLEAN MODE", "HSCLN TIMER M") -> RESET ABC AES, and to the advance bus; NO -> 5 |
| 5 | hex PREVIOUS INSTR PROPERLY EXECUTED ? | YES ("MAR MODE") -> TRANSFER INDICATORS -> 6; NO ("INTRUPT") -> HSCLN TIMER WILL SET. HSCLN MODE |
| 6 | hex STORE LEVEL | YES -> hex EXT. STO. (YES -> A BUS TIMER ACTION; NO -> BR. REQ hex); NO -> hex INT FETCH (YES -> A BUS TIMER ACTION; NO -> hex BR. REQ.) |
| 7 | hex BR. REQ. | NO -> "NO DELAY ABC ADV." / "TRANS. IND. M" to the advance bus; YES -> IND TEST E WILL RESET BR REQMTS. |
| 8 | A BUS TIMER ACTION -> hex STORE TO INT. REQ. ? | NO -> NOT "COND GI INT REQ" -> "AND CKT 5E / A BUS TIMER M" to advance bus; YES ("COND GI INT. REQ") -> 9 |
| 9 | hex STORE TO INDICATOR REQ ? | NO -> NOT "LAAR DEC ADDR. 11" -> advance bus; YES ("ADD 11") -> 10 |
| 10 | hex LAOP 41 ? | YES -> NOT "NO ABC DEC BIN STO LEVEL" -> advance bus; NO -> IND. REQ. TIMER ACTION ("IND. REQ. TIMER M" to advance bus) |
| 11 | hex NOOP MODE | YES -> hex HSCLN MODE (YES -> to ABC DONE line; NO -> hex EXT STO TAGS) |
| 12 | hex EXT STO TAGS | YES -> hex PREV STORES DONE (YES: "STAR BUSY NO STO REQ." -> ABC DONE line); NO -> hex LAST LEVEL (YES "IC" -> hex ABC TBC INTLK (YES -> hex ABC DONE)) |
| 13 | hex ABC DONE | YES ("TFR IND M") -> advance bus |
| 14 | advance bus "COND. ABC ADV. COND." -> hex ABC TBC INTLKD ? | NO ("ABC ADV. COND.") -> hex ABC AES OFF ? YES -> ADVANCE ABC; YES -> hex LAOP 27 OR 55 (second digit of "27" carries a stray stroke) NO -> hex TBC MULT. ADV YES -> back to the ABC-TBC test |

DERIVED: the ABC enters a level only when its preparation is finished (LF and
LC tags). In NOOP mode (a level after a mispredicted branch or an
interruption) a level with external-store tags waits for "PREV STORES DONE"
("STAR BUSY" = store address register busy, "NO STO REQ."). Store to the
indicator register (address 11, "LAAR DEC ADDR. 11") goes through the
indicator-request timer, except LAOP 41. ABC may not pass TBC (ABC TBC
INTLKD), except under LAOP 27/55 and TBC multiple advance.

### Fig 3.2.15, SETTING MAR MODE (PDF 107, printed 2-17, 2/1/62; reader E)

| step | condition(s) (PRINTED) | action(s) (PRINTED) | ALD page | notes |
|---|---|---|---|---|
| 0 | -- | MAR MODE OFF | -- | entry |
| 1 | ARITH INSTR EXECUTED ? NO; "NOOP IND TEST M" ON ? YES | SIGNAL PAU TO SET "MSTR TEST CMPLT" TRIG; -> COND INTRPT OR MAR TRIGS | 38.23.01.1; 38.35.02.1 | dashed NO line |
| 2 | ARITH INSTR EXECUTED ? YES; "LA NORMAL IND TEST M" ON ? YES | SIGNAL PAU OF LA TESTS COMPLETE | 38.23.01.1 | dashed YES line |
| 3 | + "EXEC UNIT IND TEST M" ON ? YES; A CHKR IND TEST M ON ? YES | -> COND INTRPT OR MAR TRIGS | 38.35.02.1 | |
| 4 | COND INTRPT OR MAR TRIGS (NEW SETTING MAR) | RESET ALL IND TEST TRIGGERS | 38.35.05.1 | |
| 5 | INTRUPT ? NO | SET "MAR MODE" AND "MAR NEXT INSTRN" TRIGS | 38.35.04.1 | |
| 6 | INTRUPT ? YES | SET "INTRUPT NEXT INSTRN" TRIGGER | 38.35.05.1 | |
| 7 | "EXEC UNIT IND TEST M" ON ? YES; A CHK COMPLETED ? YES (CHK COMP IMMEDIATE) ; A CHKR ERROR ? NO ("-P NOT ALL OTHER TEST TRIGS") | RESET ALL IND TEST TRIGGERS; PREVENT SETTING "A CHKR IND TEST M" TRIG | 38.35.02.1; 38.35.01.1; 38.35.01.1 | |
| 8 | INTRPT ? NO | SET "MAR MODE" AND "MAR NEXT INSTRN" TRIGS | 38.35.04.1 | |
| 9 | INTRPT ? YES | SET "INTRPT NEXT INSTRN" TRIGGER | 38.35.05.1 | |

### Fig 3.2.16, FP ABC ACTIONS-TRANSFER INDICATOR TIMER (PDF 108, printed 2-19/2-20, 2/1/62; reader E)

| step / phase | condition(s) (PRINTED) | action(s) (PRINTED) | ALD | notes |
|---|---|---|---|---|
| entry | ABC AT NEW LEVEL | GO IND FIELD LEVELS TO MAIN IND REG AND GO IC FIELD LEVELS TO IC RUFFER | 35.27.01.1 | unconditional on ABC reaching new level |
| entry | DISC ABC NO; LEVEL PREPARATION FINISHED YES (LF & LC ON); HSCLN MODE NO; PREVIOUS INSTR. PROPERLY EXECUTED YES (MAR MODE); ABC ACTION YET NO (ABC AES ON) | start TRANSFER INDICATOR TIMER | 38.38.01.1 (DERIVED) | |
| entry | HSCLN MODE YES, or PREVIOUS INSTR. PROPERLY EXECUTED NO (INTRUPT); ABC ACTION YET NO (ABC AES ON) | START HSCLN TIMER | 38.39.02.1 | **[KEY]** |
| E.M̄ | -- | RESET ABC AES | 38.81.03.1 | |
| E.M̄ | -- | GI X̄R̄ INDS TO IND REG | 35.27.03.1 | |
| E.M̄ | NOOP ABC YES | SET NOOP MODE | 38.34.01.1 | **[KEY]** |
| E.M̄ | LAST INSTR. LEVEL YES (IC ON) | GI IC FIELD TO IC BUFFER; RESET MAR MODE | 35.27.02.1; 38.35.04.1 | |
| E.M̄ | then EXT STO TAGS YES, or STORE TYPE LEVEL NO | "NO DELAY IND. TEST"; SET IND. TEST E | 38.32; 38.38.03.1 | |
| E.M̄ | EXT STO TAGS NO and STORE TYPE LEVEL (other exit) | WAIT FOR A BUS TIMER | -- | |
| E.M̄ | NOOP MODE YES | SET LA NOOP IND. TEST M; SIGNAL PAU TO SET "MSTR TEST COMPLT" | 38.35.03.1; 38.23.01.1 | |
| E.M̄ | NOOP MODE NO | SET NORMAL IND. TEST M; SIGNAL PAU OF LA TESTS COMPLETE | 38.35.01.1; 38.23.01.1 | |
| E.M | 1st INSTR. LEVEL YES ("MAR NEXT INSTR" ON) | RESET "MAR NEXT INSTR" TRIGGER | 38.35.04.1 | |
| E.M | + IS THIS THE INTRPT FREE INSTR YES (INTRPT IS DISABLED) | RESET "DISABLE INTRPT" TRIGGER | 38.39.05.1 | |
| E.M | -- | RESET UNIPOLAR INDS | 35.27.07.1 | |
| E.M | NOOP MODE NO; INT. FETCH YES (INT. TAG ON (X2 FETCH)) | -> FETCHES (TO A BUS TIMER) | -- | |
| E.M | NOOP MODE YES (NON-ARITHMETIC); ABC FROM TAG ON YES; STORE OR INT. FETCH YES (LAAR BUSY) | RESET LAAR BUSY TRIG | 38.53.03.1 | **[KEY]** |
| E.M | NOOP MODE YES (NON-ARITHMETIC); LAST INSTR. LEVEL YES (IC ON); LAOP 11 NO | RESET "MSTR TEST COMPLT" TRIG. IN PAU; ALLOW PAU TO RE-MEMORIZE THE INTRPT. LINE | 38.23.02.1; -- | |
| M | EXT STO TAGS YES, or STORE TYPE LEVEL NO | ADV. ABC IF NOT INTLKD BY TBC | -- | **[KEY]** counter interlock |
| E + M | NOOP MODE NO | -> STORES (TO A BUS TIMER) | -- | |

### Fig 3.2.17, VFL ABC ACTIONS-TRANSFER INDICATOR TIMER (PDF 109, printed 2-21/2-22, 2/1/62; reader E)

| phase | condition(s) (PRINTED) | action(s) (PRINTED) | ALD | notes |
|---|---|---|---|---|
| E.M̄ | -- | RESET ABC AES | 38.31.03.1 | 38.81.03.1 on Fig 3.2.16 |
| E.M̄ | -- | GI X̄R̄ INDS TO IND REG | 35.27.03.1 | |
| E.M̄ | NOOP ABC ? YES | SET NOOP MODE | -- | **[KEY]** |
| E.M̄ | NOOP ABC YES; VFL STORE OR FETCH LEVEL ? YES (SAU EN MEM TRIG ON); 1ST NOOP OF THIS INSTR. ? YES (NO NOOP MODE) | SET "VFL INSTR REJECT" TRIGGER; SIGNAL SAU TO STOP HSKPING. | 38.23.04.1; 38.23.04.1 | **[KEY]** |
| E.M̄ | LAST INSTR. LEVEL ? YES (IC ON) | GI IC FIELD TO IC BUFFER; RESET MAR MODE | 35.27.02.1; 38.35.04.1 | |
| E.M̄ | NOOP'D OR NOOP MODE? YES, or ABC STORE ACTION RQD ? NO | "NO DELAY IND TEST"; SET IND TEST E | 38.32.09.1; 38.38.03.1 | |
| E.M̄ | NOOP MODE ? YES | SET LA NOOP IND TEST M; SIGNAL PAU TO SET "MSTR TEST COMPLET" | 38.35.03.1; 38.23.01.1 | |
| E.M̄ | NOOP MODE ? NO | SET "NORMAL IND TEST" M; SIGNAL PAU OF LA TESTS COMPLT | 38.35.01.1; 38.23.01.1 | |
| E.M | 1ST INSTR. LEVEL ? YES | RESET "MAR NEXT INSTR" TRIG | 38.35.04.1 | |
| E.M | + IS THIS THE INTRPT FREE INSTR ? YES ("MAR NEXT INSTR" ON) | RESET "DISABLE INTRPT" TRIG | 38.39.05.1 | |
| E.M | -- | RESET UNIPOLAR INDS | 35.27.07.1 | |
| E.M | NOOP MODE NO; 1ST INSTR. LEVEL ? YES (X1 35 75 48) | SET "SAU EN MEM" TRIG | 38.34.02.1 | |
| E.M | LAST INSTR LEVEL ? YES (IC ON) | RESET SAU EN MEM TRIG | 38.34.02.1 | |
| E.M | NOOP NODE YES (NON ARITH); ABC FROM TAG ON ? YES; STORE OR INT. FETCH ? YES (LAAR BUSY) | RESET LAAR BUSY TRIG | 38.53.03.1 | **[KEY]** |
| E.M | NOOP NODE YES (NON ARITH); LAST INSTR LEVEL ? YES (IC ON); LAOP 11 (unlabelled exit) | RESET "MSTR TEST CMPLT" TRIG IN PAU; ALLOW PAU TO RE-MEMORIZE THE INTRPT LINE | 38.23.02.1; -- | |
| E.M | NOOP NODE (other exit); INT. FETCH ? YES (INT TAG ON) | -> FETCHES (TO A BUS TIMER) | -- | |
| M | NOOP MODE ? YES, or A BUS TIMER ACTION RQD ? NO | ADV. ABC IF NOT INTLKD BY TBC | 38.31.05.1 | **[KEY]** interlock |
| E + M | NOOP MODE ? NO | -> STORES (TO A BUS TIMER) | -- | |

### Fig 3.2.18, BRANCH ABC ACTIONS-TRANSFER INDICATOR TIMER (PDF 110, printed 2-23/2-24, 2/1/62; reader E)

| phase | condition(s) (PRINTED) | action(s) (PRINTED) | ALD | notes |
|---|---|---|---|---|
| E.M̄ | -- | RESET ABC AES; GI X̄R̄ INDS TO IND. REQ | 38.31.03.1; 35.27.03.1 | |
| E.M̄ | LAOP 31,57 ? YES | RESET TBC AES; ADV. TBC IF NOT INTLKD BY OCC | 38.01.03.1; -- | **[KEY]** interlock |
| E.M̄ | NOOP ABC ? YES | SET NOOP MODE | 38.34.01.1 | |
| E.M̄ | LAOP 31 ? YES | RESET LF TAG | 36.01.09.1 | |
| E.M̄ | LAOP 11 YES; RECOVERY REQ YES | RESET MAR MODE; RESET "MSTR TEST COMPLT" TRIG IN PAU (-> ALLOW PAU TO RE-MEMORIZE THE INTRPT LINE); -> BR SUCC & NO COND INDS | 38.35.04.1; 38.23.02.1 | **[KEY]** recovery |
| E.M̄ | LAST INSTR. LEVEL ? YES (IC ON) | GI IC FIELD TO IC BUFFER; RESET MAR MODE | 35.27.02.1; 38.35.04.1 | |
| E.M̄ | NOT SIC BIN RECOVERY LEVEL; NOOP OR NOOP MODE NO; LAOP 45 ? YES | -> BR SUCC & NO COND INDS | -- | |
| E.M̄ | NOOP OR NOOP MODE YES, or ABC STORE ACTION RQD. ? (left exit) | NO DELAY IND. TEST; SET IND. TEST E | 38.32.09.1; 38.38.03.1 | |
| E.M̄ | after SET IND. TEST E | RESET RQST CYCLE STORE MEM TRIGGER; RESET BR SUCC AND COND IND TRIGGERS | 38.24.02.1; 38.24.03.1 | |
| E.M̄ | BR SUCC & NO COND INDS YES | RESET LF TAG; SET BR RECOVERY INHB LOAD TRIGGER; SET "I BOX RQST HSCLN" TRIGGER | 36.01.09.1; --; 38.39.05.1 | **[KEY]** |
| I BOX HSCLN TIMER E | -- | RESET I BOX RQST HSCLN TRIGGER | -- | **[KEY]** |
| I BOX HSCLN TIMER M | -- | SET LA "HSCLN MODE" TRIGGER | 38.39.04.1 | **[KEY]** |
| I BOX HSCLN TIMER M | IS LA EMPTY ? YES | START LA HSCLN OVER TIMER | 38.39.01.1 | **[KEY]** |
| I BOX HSCLN TIMER M | IS LA EMPTY ? (other exit) | RESET "I BOX HSCLN TIMER" | 38.0.07.1 | **[KEY]** |
| E.M̄ (end) | NOOP MODE ? YES | SET LA NOOP IND TEST M; SIGNAL PAU TO SET "MSTR TEST COMPLT" | 38.35.03.1; 38.23.01.1 | |
| E.M̄ (end) | NOOP MODE ? NO | SET NORMAL IND TEST M; SIGNAL PAU TO LA TESTS COMPLT | 38.35.01.1; 38.23.01.1 | |
| E.M | 1st INSTR.LEVEL ? (MAR NEXT INSTR) | RESET MAR NEXT INSTR TRIGGER | 38.35.04.1 | |
| E.M | LAOP 75 ? NO; IS THIS THEINTRPT FREE INSTR. ? (INTRPT DISABLED) | RESET "DISABLE INTRPT" TRIGGERS | 38.39.05.1 | |
| E.M | -- | RESET UNIPOLAR INDS | 35.27.07.1 | |
| E.M | BR. RECOVERY ? YES (45, 47); SUCC BRANCH ? YES; COND INDS ? YES | GI SAU'S COND INDS TO IND REQ.; -> SIC BIN (left) | 35.27.05.1 | **[KEY]** |
| E.M | BR. RECOVERY YES; SUCC BRANCH ? NO (or COND INDS YES); SIC BIN YES (IC OFF) | SIGNAL I BOX OF NO BRANCH | 38.38.02.1 (placement ambiguous) | **[KEY]** |
| E.M | COND INDS ? NO; GOOD RECOVERY LEVEL NO (47) | GI CNIDC TO MK IND. | 35.27.03.1 | |
| E.M | COND INDS ? NO; SIC BIN (right) YES (IC OFF) | SIGNAL I BOX OF BRANCH | 38.38.02.1 (placement ambiguous) | **[KEY]** |
| E.M | NOOP MODE ? YES | GI CNIDC TO MK IND. | 35.27.03.1 | |
| E.M | NOOP MODE YES (NON-ARITH INSTR.); LAST INSTR. LEVEL ? YES (ICON) | RESET "MSTR TEST COMPLT" TRIG IN PAU; ALLOW PAU TO RE-MEMORIZE THE INTRPT LINE | 38.23.02.1 | |
| E.M | NOOP MODE YES; ABC FROM TAG ON ? YES; STORE OR INT. FETCH ? YES (LAAR BUSY) | RESET LAAR BUSY | 38.53.03.1 | **[KEY]** |
| E.M | NOOP MODE ? NO; INT. FETCH ? YES (INT. TAG ON) | -> FETCHES (TO A BUS TIMER) | -- | |
| M | NOOP MODE ? NO; A BUS TIMER ACTION RQD ? NO; BRANCH REC RQD ? YES | IND TEST E WILL RESET THE BR RQMNTS | 38.24.03.1 | |
| M | NOOP MODE ? YES, or BRANCH REC RQD ? NO | ADV. ABC IF NOT INTLKD BY TBC | 38.31.05.1 | **[KEY]** interlock |
| E + M | NOOP MODE ? NO | -> STORES (TO A BUS TIMER) | -- | |

### Fig 3.2.19, I BOX AND I/O ABC ACTIONS-TRANSFER INDICATOR TIMER (PDF 111, printed 2-25/2-26, 2/1/62; reader E; spot-checked)

| phase | condition(s) (PRINTED) | action(s) (PRINTED) | ALD | notes |
|---|---|---|---|---|
| E.M̄ | -- | RESET ABC AES | 38.31.03.1 | |
| E.M̄ | LAOP 02,04,33,63 ? YES; NOOP'D OR NOOP MODE ? NO | GI XR INDS TO IND REQ. | 35.27.04.1 | |
| E.M̄ | LAOP 02,04 YES and (NOOP'D ? YES and 02 YES, or NOOP MODE ? YES); or LAOP 33 EXT. ? YES and NOOP'D OR NOOP MODE NO; or 06 YES | RESET ABC LF TAG | 36.01.09.1 | **[KEY]** pseudo store |
| E.M̄ | -- | GI X̄R̄ INDS TO IND REQ. | 35.27.03.1 | |
| E.M̄ | LAOP 00,02,25,63,65,33 EXT. ? YES; NOOP'D OR NOOP MODE ? NO | RESET TBC AES; ADV. TBC, IF NOT INTLKD BY OCC | 38.21.03.1; -- | **[KEY]** interlock |
| E.M̄ | NOOP ABC YES | SET NOOP MODE | 38.34.01.1 | |
| E.M̄ | LAOP 11 YES; NOOP RECOVERY REQ YES | SET "PSEUDO INTRPT INHIBIT LOAD" TRIGGER; SET "I BOX RQST HSCLN" TRIGGER | 38.39.03.1; 38.39.05.1 | **[KEY]** |
| E.M̄ | LAST INSTR. LEVEL ? YES (IC ON); 02,04,33,63 ? YES; NOOP'D OR NOOP MODE ? YES | same as above | 38.39.03.1; 38.39.05.1 | **[KEY]** |
| E.M̄ | LAST INSTR. LEVEL YES; 06 ? YES | same as above | | **[KEY]** |
| E.M̄ | LAST INSTR. LEVEL YES | GI IC FIELD TO IC BUFFER; RESET MAR MODE | 35.27.02.1; 38.35.04.1 | |
| I BOX HSCLN TIMER E | -- | RESET "I BOX RQST HSCLN" TRIGGER | -- | |
| I BOX HSCLN TIMER M | -- | SET LA "HSCLN MODE" TRIGGER | 38.39.04.1 | |
| I BOX HSCLN TIMER M | IS LA EMPTY ? YES | START LA HSCLN OVER TIMER | 38.39.01.1 | |
| E.M̄ | NOOP'D OR NOOP MODE ? YES, or AEC STORE ACTION RQD. ? NO | NO DELAY IND TEST; SET IND. TEST E; RESET "LAST CYCLE STORE" AND STORE INHIBIT TRIGGERS | 38.32.09.1; 38.38.03.1; 38.24.02.1 | **[KEY]** |
| E.M̄ | NOOP MODE ? YES, or NON-ARITH INSTR. ? YES ("LA ONLY MAR NEXT") | SET LA NOOP IND TEST M; SIGNAL PAU TO SET "MSTR TEST COMPLT" | 38.35.03.1; 38.23.01.1 | |
| E.M̄ | NOOP MODE NO; NON-ARITH INSTR. ? NO | SET NORMAL IND. TEST M; SIGNAL PAU OF LA TESTS COMPLETE | 38.35.01.1; 38.23.01.1 | |
| E.M | 1st INSTR LEVEL YES ("MAR NEXT INSTR" ON) | RESET "MAR NEXT INSTR" | 38.35.04.1 | |
| E.M | IS THIS THE INTRPT FREE INSTR ? YES (INTRPT IS DISABLED) | RESET "DISABLE INTRPT" TRIGGER | 38.39.05.1 | |
| E.M | -- | RESET UNIPOLAR IND'S | 35.27.07.1 | |
| E.M | 06 ? YES | GI CNIDC TO MK IND. | 35.27.03.1 | |
| E.M | INT FETCH ? YES (INT TAG ON) | -> FETCHES | -- | |
| E.M | 33 EXT. ? YES; NOOP'D OR NOOP MODE NO; IN ECC ? NO | RESET "STORE CHK IND TEST M" | 38.35.02.1 | |
| E.M | NOOP MODE ? YES (NON ARITH); ABC FROM TAG ON ? YES; STORE OR INT. FETCH ? YES (LAAR BUSY); .51 NO | RESET "LAAR BUSY"; SET ABC NOOP TAG | 38.58.03.1; 36.07.03.1 | **[KEY]** |
| E.M | (NOOP MODE YES or NON-ARITH INSTR. ? YES); LAST INSTR LEVEL ? YES (IC ON) | RESET "MSTR TEST COMPLT" TRIG IN PAU; ALLOW PAU TO RE-MEMORIZE THE INTRPT LINE | 38.23.02.1; -- | |
| M | NOOP MODE ? YES and LAOP 51 ? NO; or NOOP MODE NO, INT FETCH ? NO, LAOP 33 INT. ? NO | ADV. ABC IF NOT INTLKD BY TBC | 38.31.05.1 | **[KEY]** interlock |
| M | NOOP MODE NO; INT FETCH NO; LAOP 33 INT. ? YES; ABC- TBC INTLKD ? YES; TB TIMER M ? YES | -> STORES (TO A BUS TIMER) | -- | **[KEY]** interlock |

### Fig 3.2.20, INTERNAL FETCH ABC ACTIONS-ARITHMETIC BUS TIMER (PDF 112, printed 2-27, 2/1/62; reader E)

| phase | condition(s) (PRINTED) | action(s) (PRINTED) | ALD | notes |
|---|---|---|---|---|
| entry | LAOP 37 ? YES | SIGNAL IND. REQ TO RESET 0-19 ASYNCHRONOUS INDS, IMMEDIATELY AFTER FETCHES | 35.27.04.1 | |
| EE | -- | SEND "PASS DATA" SIGNAL TO A CHKR | 38.23.03.1 | |
| EE | -- | GO INT. ADDRESS SPECIFIED BY LAAR ONTO ACIB | 35.24.04.1, .05.1, .06.1 | **[KEY]** LAAR |
| E.M̄ | -- | RESET TRANS. IND. TIMER M | 38.38.02.1 | |
| E.M̄ | -- | RESET TBC AES | 38.21.03.1 | |
| E.M̄ | -- | ADV. TBC IF INTLKD WITH ABC IF NOT INTLKD BY OCC | -- | **[KEY]** interlock |
| E.M̄ | LAAR AT ADD. 7 OR 11 ? NO | SIGNAL A CHKR TO CHK PARITY | 38.23.03.1 | **[KEY]** |
| E.M̄ | LAAR AT ADD. 7 OR 11 ? YES | SIGNAL A CHKR NOT TO CHK PARITY | 38.23.03.1 | **[KEY]** |
| M | -- | ADV. ABC IF NOT INTLKD BY TBC | 38.31.05.1 | **[KEY]** interlock |
| E.M | -- | RESET LAAR BUSY TRIGGER | 38.53.03.1 | **[KEY]** |
| E.M | LAOP 51 ? YES | RESET LF TAG TO SIGNAL FOR SCC ACTION; GI ACOB INTO ABC LEVEL | 36.01.09.1; 35.23.02.1 | **[KEY]** SCC |
| E.M | LAOP 07 ? NO | GI ACOB TO C REG | 35.22.01.1 (shared) | |
| E.M | LAOP 07 ? YES | GI ACOB TO D REG | 35.22.01.1 (shared) | |
| E.M | FP INSTR. ? YES (X2) | SEND "START" SIGNALS TO SAU & PAU | 38.23.01.1 | |
| E.M | FP INSTR. ? NO; LAST OPERAND ? YES (05 07 37) | SET "SAU GO" TRIGGER; SEND "GO" SIGNAL TO SAU | 38.23.04.1; -- | |
| E.M | SAU STARTED EXECUTION ? YES ("SAU HSKPING" OVER) | RESET "SAU GO" TRIGGER | 38.23.04.1 | |
| E.M | LAST OPERAND YES; LAOP 37 YES | RESET 0-19 SYNCHRONOUS IND'S IN IND. REQ.; RESET SAU'S ERROR TRIGGER | 35.27.04.1; 35.27.04.1 | |

### Fig 3.2.21, STORE ABC ACTIONS-ARITHMETIC BUS TIMER (PDF 113, printed 2-29/2-30, 2/1/62; reader E)

| phase | condition(s) (PRINTED) | action(s) (PRINTED) | ALD | notes |
|---|---|---|---|---|
| entry | WHAT IS BEING STORED ? C - D REG (17, 23, 41); IS STORE DATA READY ? YES ("LAST CYCLE STORE MEM" ON) | start ARITH BUS TIMER at EE | -- | **[KEY]** LAST CYCLE STORE |
| entry | ACOB (X2, 13, 21); IS STORE DATA READY ? YES ("LAST CYCLE STORE MEM" TRIG ON) | start ARITH BUS TIMER | 38.33.02.1 | **[KEY]** |
| entry | ACOB; HAS A ZERO DIVISOR CANCELLED ANY REMAINDER THAT WAS TO BE STORED ? YES ("STORE INHIBIT MEM" TRIG ON) | start ARITH BUS TIMER | 38.33.02.1 | **[KEY]** store inhibit |
| entry | TRANS IND TIMER LAOP 33 INT | start ARITH BUS TIMER | 38.33.01.1 | |
| EE | -- | SEND "PASS DATA" SIGNAL TO A CHKR | 38.23.03.1 | |
| EE | WHERE IS DATA ? C REG (17, 41, 33 INT) | GI C REG TO ACIB | 35.21.01.1 (shared) | |
| EE | WHERE IS DATA ? D REG (23) | GI D REG TO ACIB | 35.21.01.1 (shared) | |
| E.M̄ | -- | RESET "TRANS IND TIMER M" | 38.38.02.1 | |
| E.M̄ | LAST INSTR LEVEL ? YES (IC ON) | DELAY IND TEST; SET IND TEST E; RESET: BR SUCC COND IND'S LAST CYCLE STORE, STORE INHIBIT TRIGGERS | 38.32.09.1; 38.38.03.1; 38.24.02.1, 38.24.03.1 | **[KEY]** |
| E.M̄ | NON-ARITH INSTR ? YES | SET LA NOOP IND TEST M; SIGNAL PAU TO SET "MSTR TEST COMPLETE" TRIG | 38.35.03.1; 38.23.01.1 | |
| E.M̄ | NON-ARITH INSTR ? NO | SET NORMAL IND TEST M; SIGNAL PAU OF LA TESTS CMPLT | 38.35.01.1; 38.23.01.1 | |
| E.M̄ | C+D STORE OP ? YES (17 23 41 33 INT) | SIGNAL A CHKR TO CHK PARITY | 38.23.03.1 | |
| E.M̄ | 33 INT YES, or (33 INT NO (17, 23, 41) and 23 ? YES) | SIGNAL A CHECKER NOT TO SET ITS CHK CMPLT TGR | -- | |
| E.M̄ | 33 INT NO (17, 23, 41) | RESET TBC AES; ADV TBC IF INTLKD WITH ABC, AND NOT INTLKD BY OCC | 38.21.03.1; 38.23.03.1 | **[KEY]** interlock |
| M | GOOD INTERNAL STORE ? NO; or ADDR 11 ? NO; or BI STORE ? YES (LAOP41) | ADV ABC IF NOT INTLKD BY TBC | 38.31.05.1 | **[KEY]** interlock |
| M | 33 INT ? YES; ARC TBC INTLKD ? YES | ADV TBC IF NOT INTLKD BY OCC | -- | **[KEY]** interlock |
| E.M | ACOB STORE OP ? YES (X2,13,21); STORE DATA READY ? YES ("LAST CYCLE STORE MEM" ON) | SIGNAL A CHKR THAT ACOB DATA IS ACCEPTED | 38.23.03.1 | |
| E.M | LAAR INT ? YES | RESET LAAR BUSY TRIG; GI ACOB TO LAAR ADDER IF NOT ADDR 1, 5, or 6 | 38.23.03.1; 35.25.01.1/.02.1/.03.1 | **[KEY]** |
| E.M | ADDR 8 ? YES; FP STORE ? YES | GI ACOB POS 60-63 TO SIGN BYTE REG POS 4-7 | 35.25.02.1 | |
| E.M | LAAR INT YES; BI STORE ? (exit 33 INT X2 13 17 23); ADDR 11 ? YES; 33 INT ? YES, or 33 INT NO and STORE DATA READY ? YES ("LAST CYCLE STORE MEM" ON) | START IND REG TIMER -> GI MODIFIED XR IND'S FROM IND REG TO THE UPDATED INDEX IND REG; ADV ABC IF NOT INTLKD BY TBC | 35.26.02.1; -- | **[KEY]** UPDATED INDEX |
| E.M | LAAR INT ? NO; STORE DATA READY ? YES | RESET ABC LF TAG; GI ACOB INTO ABC DATA FIELD | 36.01.09.1; 35.23.02.1 | **[KEY]** |

### Fig. 3.2.22, LA HOUSECLEAN TIMER -- PDF 114, printed 2-31, 2/1/62. REUSED page (spec_lookahead.md §2.6), re-read in full

Timer "HSCLN TIMER" (38.39.02.1), phases E·M̄, E·M, M. PRINTS NO TIME.

| phase | condition (PRINTED) | action (PRINTED) | ALD |
|---|---|---|---|
| E·M̄ | -- | GI CNIDC IND TO MK IND. | 35.27.03.1 |
| E·M̄ | -- | RESET ABC AES | 38.31.03.1 |
| E·M̄ | hex PSEUDO STORE ? YES | RESET ABC LF TAG | 36.01.09.1 |
| E·M̄ | hex LA HSCLN MODE ? NO -> hex HSCLN DUE TO "INTRUPT" ? YES ("INTERPT NEXT INSTR" ON) | RESET "INTRPT NEXT INSTR" TRIG (38.35.05.1); SET "INTRPT INHIBIT LOAD" TRIG (38.39.03.1); SET "DISABLE INTRPT" TRIG (38.39.05.1) | |
| E·M̄ | (continuing) | SET "I BOX RQST HSCLN" TRIG (38.39.05.1) -> START I BOX HSCLN TIMER "(I BOX)" (38.03.10.1) | |
| I-box HSCLN timer E | -- | RESET "I BOX RQST HSCLN" TRIG | 38.39.05.1 |
| I-box HSCLN timer M | hex EXEC UNITS IDLE ? YES | RESET "EXEC UNITS IDLE" TRIG (38.39.04.1); SET LA HSCLN MODE TRIG (38.39.04.1); RESET I BOX HSCLN TIMER (38.02.07.1); hex LA EMPTY ? YES -> START LA "HSCLN OVER" TIMER (38.39.01.1) | |
| E·M | -- | RESET LAAR BUSY TRIG | 38.53.03.1 |
| E·M | hex LA HSCLN MODE ? NO -> hex SAU INSTR ? YES ("X1,35,43") | SET "VFL INSTR INTRPT" TRIG (38.23.04.1); hex SAU STARTED PRE-EXECUTION ? YES ("HSKPING") -> SET "VFL INSTR REJECT" TRIG (38.38.04.1) -> SIGNAL SAU TO STOP HSKPING (38.23.04.1) and hex SAU IDLE ? YES ("VFL NOT OPERATING") -> SET "EXECUTION UNITS IDLE" TRIG (38.39.04.1); NO -> RESET "VFL INSTR INTRPT" TRIG (38.23.04.1) | |
| E·M | SAU INSTR NO -> hex PAU INSTR ? YES ("X2") | dashed box PAU DISCOVERS INTRPT COND -> hex PAU IDLE ? YES ("PAU IDLE") -> SET "EXECUTION UNITS IDLE" TRIG; PAU INSTR NO -> SET "EXECUTION UNITS IDLE" TRIG | |
| M | hex HSCLN MODE ? YES | ADV ABC IF NOT INTLKD BY TBC (38.31.05.1); SET ABC AES (38.31.03.1); RESET HSCLN TIMER M (38.39.02.1) | |

DERIVED: housecleaning is per level, under the ABC: each level the ABC reaches
in HSCLN mode is stepped past; a pseudo-store level has its LF tag reset; the
LAAR busy trigger is reset. Before the LA enters HSCLN mode the I box's own
housecleaning timer runs and both execution units must be idle (the SAU is
told to stop housekeeping; a VFL instruction already in pre-execution is
rejected). When the LA is empty the "HSCLN OVER" timer starts (Fig 3.2.23).

### Fig. 3.2.23, LA HOUSECLEAN OVER TIMER -- PDF 115, printed 2-32, 2/1/62. First-hand

Timer "LA ... HSCLN OVER TIMER" (38.39.01.1). PRINTS NO TIME.

| phase | action (PRINTED) | ALD |
|---|---|---|
| E·M̄ | RESET CN, DF, & DS IND'S AT ALL LA LEVELS | 38.70.01.1 |
| E·M̄ | RESET "MAR MODE" TRIG | 38.35.04.1 |
| E·M̄ | RESET PAU'S "MSTR TEST CMPLT" TRIG | 38.02.06.1 |
| E·M̄ | RESET "VFL START" TRIG | 38.23.05.1 |
| E·M̄ | RESET PAU'S "FP ENABLE" TRIG | 38.02.06.1 |
| E·M̄ | RESET LA HSCLN MODE TRIG | 38.39.04.1 |
| E·M̄ | RESET: INTRPT, PSEUDO INTRPT, & BR. RECOVERY INHIBIT LOAD TRIGGERS | 38.39.03.1 |
| E·M̄ (end) | SET LA "NOOP IND TEST M" TRIG (38.35.03.1); hex INTRPT ? NO -> SET "MAR MODE" AND "MAR NEXT INSTR." TRIGS (38.35.04.1); YES -> SET "INTRPT NEXT INSTR" TRIG (38.35.05.1) | |
| E·M | GI IC BUFFER TO IC REG | 38.02.06.1 |
| E·M | **GI IND REG XR IND'S INTO UPDATED INDEX IND REG** | 38.02.06.1 |
| E·M | SET PAU'S "WAIT" TRIG TO ALLOW IT TO RECEIVE NEW INSTR'S | 38.02.06.1 |
| E·M | GI BIT ADDR. OF LEFT-MOST (SET) IND INTO I BOX W REG | 38.02.06.1 |
| M | SIGNAL I BOX OF HSCLN COMPLETE | 38.02.05.1 |
| M (dashed) | I BOX ACKNOWLEDGES RECEIPT OF SIGNAL & RESETS THE HSCLN OVER TIMER | 38.03.08.1 |
| M (dashed) | IF THIS WAS A BR. RECOVERY HSCLN, I BOX WILL PLACE THE "BRANCH TO" ADDR IN THE IC REG. TRANSFER THE IC REG INTO THE IAUC IC FIELD, [dashed rule] THEN GI THE (ABC) IC FIELD INTO THE IC BUFFER | 35.27.02.1 |

[KEY] Index recovery at the end of housecleaning: the indicator register's XR
indicators are gated into the I box's UPDATED INDEX IND REG, i.e. the
updated-index indicators are restored from the architected state.

### Fig. 3.2.24, ABC ACTION ON BAC (LAOP 11) -- PDF 116, printed 2-33, 2/1/62. First-hand

Head: "BAC LOOK AHEAD DATA FIELD": bits 0-18 BRANCH TO ADDRESS | X | 50-55
SPECIFIED INDICATOR FIELD | X | 59 I BOX BRANCHED BIT | X | 61 RESET INDIC BIT
| 62 BRANCH IF ON BIT | IC: ORIGINAL ICR. Box "GATE DATA FIELD BITS 54, 55,
59, 61, 62". PRINTS NO TIME.

| # | condition (PRINTED) | exits / actions (PRINTED) |
|---|---|---|
| 1 | ABC AT NEW LEVEL -> hex LAOP 11 | YES -> 2, and (long line) -> 6 |
| 2 | hex DOES SPECIFIED INDIC = BIT 62 | NO -> 3; YES -> 4 |
| 3 | hex DID I BOX BRANCH (BIT 59) | YES -> TFR INDIC TIMER SET PSUDO IRPT RECOVERY; (NO path) -> DELAY ABC ADV... |
| 4 | hex COND INDICATORS | YES -> TFR INDIC TIMER SET PSUDO IRPT RECOVERY and BLOCK INDIC RESET; NO -> 5 |
| 5 | hex DID I BOX BRANCH (BIT 59) | YES -> hex INTERRUPT (YES -> TFR INDIC TIMER SET BRANCH RECOVERY); NO -> TFR INDIC TIMER SET BRANCH RECOVERY |
| all | -> DELAY ABC ADV, RESET MAR MODE & MSTR TEST COMP ("RESET LF") | |
| 6 | hex INDIC RESET BLOCKED ? (dashed from BLOCK INDIC RESET) | NO -> hex INDIC RESET SPECIFIED ? YES (BIT 61) -> hex BIT 55 (YES -> RESET AE; NO -> hex BIT 54: YES RESET AH, NO RESET AL) |

DERIVED: the I box guesses a branch-on-indicator; the ABC resolves it when
the level's indicators are known. Wrong guess (indicator state ≠ the I box's
guess, bit 59) -> "BRANCH RECOVERY"; right guess -> "PSUDO IRPT RECOVERY"
(pseudo-interrupt recovery). Note the exact pairing of YES/NO arrows into the
two recovery boxes at nodes 3-5 is drawn with crossing lines; the pairing
above is as traced, DERIVED.

### Fig. 3.2.25, SCC ADVANCE -- PDF 117, printed 2-34, 2/1/62. REUSED page, re-read in full

PRINTS NO TIME. Codes "2D", "2E", "2F", "2G" printed under hexagons are logic-grid refs.

| # | condition (PRINTED) | exits / actions (PRINTED) |
|---|---|---|
| 1 | ADV -> SET SCC AES (38.51.03.1); SCC AT NEW LEVEL | |
| 2 | hex DISC SCC ? | YES -> hex SCC ABC INTLKD ? (2E) NO -> single-advance bus; NO -> 3 |
| 3 | hex LC ON ? | YES -> hex LF ON ? |
| 4 | hex LF ON ? | YES -> "SCC DEC ADV. COND" (38.51.05.1) bus; NO -> hex SCC LDE ON ? and SET SCC LDE TRIG (38.52.07.1) "TO PAGE 2" |
| 5 | hex SCC LDE ON ? YES -> hex ILLEGAL PS STORE ? | YES -> "(38.52.06.1) 42, 44, 46" -> SCC DEC ADV. COND bus; NO -> 6 |
| 6 | hex EXT STORE | YES ("BCU") -> "STORE DATA TIMER M  31, 33, 21, 13, 23, 17, X2" -> 8; NO ("I BOX") -> 7 |
| 7 | hex INDEX STORE | YES ("X REG") -> "WRITE INDEX LA M  02, 04, 06, 13, 17, 23, X2" -> 8; NO ("Y REG") -> "I TIMER NO INDEX TRANSFER M  45, 51" -> 8 |
| 8 | hex SCC AES OFF ? | YES -> hex SCC ABC INTLKD ? NO -> SCC MULT. ADV. COND. (38.51.06.1) |
| 9 | SCC DEC ADV. COND bus -> hex SCC ABC INTLKD ? (2D) | NO -> single-advance bus; YES -> hex ABC TBC INTLKD ? |
| 10 | hex ABC TBC INTLKD ? | NO -> hex ABC ADVANCING ? (2F) YES ("ANTIC ABC ADV.") -> single-advance bus; YES -> hex TBC OCC INTLK (NO -> hex ABC ADVANCING YES -> hex TBC ADVANCING TOC (2G) YES -> single-advance bus) |
| 11 | SCC SING ADV. COND. (38.51.04.1) / SCC MULT. ADV. COND. (38.51.06.1) -> ADV. SCC (38.51.01.1) | RESET LF TAG (36.01.02.1); SET SCC AES (38.51.03.1); RESET SCC LDE (38.52.07.1) |

[KEY] LAOP classes on the SCC: external store to the BCU = 31, 33, 21, 13,
23, 17, X2; I-box store into index storage (X reg) = 02, 04, 06, 13, 17,
23, X2; I-box non-index (Y reg) = 45, 51; illegal pseudo-store = 42, 44, 46.
[KEY] SCC may catch up with ABC only when ABC is itself advancing ("ANTIC ABC
ADV."); same chain for ABC-TBC and TBC-OCC. This is the anticipatory
interlock chain SCC <= ABC <= TBC <= OCC.

### Fig. 3.2.26, SCC ACTIONS -- PDF 118, printed 2-35, 2/1/62. First-hand

PRINTS NO TIME.

| # | condition (PRINTED) | exits / actions (PRINTED) |
|---|---|---|
| 1 | SCC AT NEW LEVEL -> hex SCC AES ON | YES -> 2 and -> 6 |
| 2 | hex SEC LDE ON (as printed; DERIVED "SCC") | YES -> three tests in parallel: 3a, 3b, 3c |
| 3a | hex LAOP 51 | YES -> "4D" -> REQUEST 4TH PRIORITY FOR I CHKR (38.52.08.1) |
| 3b | hex REAL STORE INST. | YES -> hex LAAR DEC IX ADR YES -> "4E" -> REQUEST 4TH PRIORITY FOR I CHKR |
| 3c | hex HSCLN MODE | YES -> hex PS STORE OR BR RCY LEVEL YES -> "4F" -> REQUEST 4TH PRIORITY FOR I CHKR |
| 4 | REQUEST 4TH PRIORITY FOR I CHKR | -> DROP OK TO I CHK (35.01.03.1) -> PREVENT I BOX FROM STARTING A CHECK CYCLE; and -> hex IS CHKR IN USE NO ("NO "0" REQ") -> hex IS OP CHK NEEDED NO ("NO "3" REQ") -> hex IS CHKR REQ FOR A CORRECT CYCLE NO ("NO SINGLE ERROR") -> START LA TO I TIMER (35.06.01.1) |
| 6 | hex IS STORE REG READY FOR LA DATA NEXT | YES ("LA NEXT") -> hex IS TOB IN USE NO ("NO TBUS TIMER E+M") -> hex IS STAR BUSY (NO -> 7; YES -> hex STORE ACCEPTED YET YES ("NO STORE MEM REQ") -> 7) |
| 7 | STO DATA TIMER (35.02.01.1) | ĒM̄ (as printed "EM̄"): RESET SCC AES; RESET FROM TAG. E: hex SCC AES ON YES -> INFORM STORE REG; GO LA TO TOB. M: hex SCC AES OFF YES -> ADV SCC IF NOT INTLKD WITH ABC (38.51.06.1) |

[KEY] I-box stores (index-register stores, pseudo-stores, branch recovery
and the I-box fetch, LAOP 51) go through the I-box CHECKER at 4th priority
("REQUEST 4TH PRIORITY FOR I CHKR"), then the LA TO I timer (Fig 3.2.27).
External stores wait for the store register ("STORE REG READY FOR LA DATA
NEXT"), the transfer bus (TOB) and STAR (store address register) not busy or
the previous store accepted, then the STO DATA TIMER puts the level on the TOB.

### Fig. 3.2.27, SCC STORES TO I BOX -- PDF 119, printed 2-36, 2/1/62. First-hand

Legend (PRINTED, top right): LAOP 51 I BOX FETCH; 13 ARITH STORE; 17 ARITH
STORE; 23 ARITH STORE; X2 ARITH STORE; 45 BR. RECOV; 02 PS STORES; 04 PS
STORES; 06 PS STORES. PRINTS NO TIME.

| timer / phase | condition (PRINTED) | action (PRINTED) | ALD |
|---|---|---|---|
| LA TO I TIMER E (entry "A") | -- | GO SCC DATA ON ICIB | 35.11.01.1 |
| E | hex STORE DATA FOR IX STORAGE ? NO (45, 51) | GI ICOB TO Y REG | 38.02.06.1 |
| E | YES (13, 17, 23, X2, 02, 04, 06) | GI ICOB TO X REG | |
| E·M̄ | -- | RESET SCC AES (38.51.03.1); DROP "NO 0 REQ" LINE TO HOLD I CHKR PRIORITY (35.01.01.1); SIGNAL I CHKR TO CHK PARITY (35.15.01.1) | |
| E·M̄ | hex STORE DATA FOR IX STORAGE ? (35.06.02.1) NO "(Y REG) 45, 51" | -> I TIMER NO TRANS INDEX M | |
| | YES "(X REG) 13, 17, 23, X2, 02, 04, 06" | -> LA TO I TIMER INDEX TRANS. M | |
| I TIMER NO TRANS INDEX M, E·M | hex 45 or 51 ? 51 -> SIGNAL I BOX TO LOOK FOR I CHKR PARITY ERROR SIGNAL (38.02.07.1); 45 -> CONDITION THE SETTING OF MK IND ON I CHKR PARITY ERROR (35.27.04.1) | | |
| I TIMER NO TRANS INDEX M, M | -- | ADV. SCC IF NOT INTLKD BY ABC | 38.51.06.1 |
| LA TO I TIMER INDEX TRANS. M, E·M | hex PS STORE ? NO (13, 17, 23, X2) | CONDITION THE SETTING OF MK IND ON I CHKR PARITY ERROR | 35.27.04.1 |
| E·M | YES (02, 04, 06) | CONDITION THE SETTING OF MK IND ON I CHKR PARITY ERROR (35.27.04.1); **NULLIFY ANY OTHER STORE LEVELS THAT ARE ADDRESSED TO THIS SAME IX ADDRESS BY SETTING OP BIT 0** (35.31.03.1) | |
| M | hex PS STORE ? NO | GO LAAR BITS 13-17 TO I BOX (IX ADDR) | 35.29.01.1 |
| M | YES | GO OP CODE BITS 1-4 TO I BOX (IX ADDR) | 35.30.01.1 |
| M | -- | START CLEAR AND WRITE INDEX TIMERS (35.33.01.1): CLEAR INDEX TIMER | WRITE INDEX TIMER | |
| clear/write, E | -- | SIGNAL I BOX TO START THE INDEX STORAGE CLEAR/STORE OPERATION | 35.30.01.1 |
| write, M | -- | ADVANCE SCC IF NOT INTLKD BY ABC | 38.51.06.1 |
| write, E·M | hex PS STORE ? NO (13, 17, 23, X2) | RESET LAAR BUSY TRIG (38.53.03.1); RESET FROM TAG H2 (36.16.01.1) | |

[KEY] Pseudo-store (PS STORE, LAOP 02/04/06): the I box's index-register
writes are carried through the look-ahead as levels and written into index
storage by the SCC, in program order. The index address of a pseudo-store
is in the level's op-code bits 1-4; of an arithmetic store to an index word
(13, 17, 23, X2), LAAR bits 13-17. A pseudo-store nullifies any other store
level addressed to the same index word (OP BIT 0). An arithmetic store frees
the LAAR (RESET LAAR BUSY TRIG); a pseudo-store does not use it.

## 5. Memory timing: R23-9732 §4 Procedure 1

M3-04-4, "ADJUSTMENT OF STORAGE BUS CONTROL AND CORE STORAGE TIMING",
printed 1-1 to 1-8, PDF 272-279, every page dated 2/1/62, "7101 Central
Processor Unit, Serial No. 30,004 and higher" (printed 1-1). Read by the author
from the page images at 300 dpi.

The procedure is an adjustment procedure. It gives the timing relations the
CE sets with an oscilloscope. It is not a cycle chart. Its purpose, as printed
on 1-1: "check and adjust the timing between core storage units (CSU's) and the
storage bus control ... by executing store and fetch operations from the CPU,
exchange, and disk synchronizer CE consoles". The "Check Procedure 1" that it
calls on printed 1-2 (step A.6) is a different procedure, the Sample Pulse
Alignment Check in M3-04-2.

### 5.1 Every timing it prints

| step | printed | PDF | what is set (PRINTED) | time (PRINTED) | in clocks (DERIVED, SP = 0.3 µs) |
|---|---|---|---|---|---|
| B.2 | 1-2 | 273 | "SM memory-select timing pulse ... 200 nanosec wide and occurs 150 nanosec after leading edge of an SP pulse" | 200 ns wide, +150 ns | inside one clock |
| B.3 | 1-3 | 274 | MEM SEL pulse delay "so changing memory address bus (MAB) information will be properly sampled into memory address register (MAR) of CSU A0" | none | -- |
| B.4 | 1-3 | 274 | "MEM RD out pulse will arrive at readout trigger of CSU A0 ... at same time that MAB information arrives at MAR" | none | -- |
| B.5 | 1-3 | 274 | "Busy trigger (logic 13.05.01) is on for 1800 nanosec" | **1800 ns** | **6** |
| B.6 | 1-3 | 274 | repeat B.1-B.5 for "CSU's A1, B0, B1, B2, and B3" (Table 4.1.1) | -- | six CSUs: A0, A1, B0-B3 |
| B.7 | 1-3 | 274 | data-in-gate delay lines "to sample selected index register data into memory data register (MDR) of each CSU" | none | -- |
| C.3 | 1-4 | 275 | "data-out-gate pulse ... 290 nanosec wide"; "does not occur earlier than 1050 nanosec after select-memory pulse" | **290 ns; ≥ 1050 ns** | ≥ 3.5 |
| C.3 (cont.) | 1-4 | 275 | "The IMOB data pulses measured at the 1Y register ... and at lookahead level 4 ... should bracket (overlap) the sixth SP pulse ... that is generated after the SP pulse which initiated the gate I pulse" (Fig 4.1.1) | **6th SP pulse** | data at clock 6 after gate I |
| C.4 | 1-5 | 276 | "SEL 1Y pulse ... brackets (overlaps) fifth and sixth SP pulses ... after SP pulse which initiated gate I pulse" (Fig 4.1.2) | 5th and 6th | 5-6 |
| C.5 | 1-5 | 276 | "SELECT 2Y pulse" the same (Fig 4.1.3) | 5th and 6th | 5-6 |
| C.7 | 1-5 | 276 | "Adjust each MEM SEL LA pulse so it brackets (overlaps) fifth SP pulse that occurs after SP pulse which initiated gate I pulse" (Fig 4.1.4); "bypass other lookahead levels by means of LA disable switches" | **5th** | 5 |
| C.8-C.9 | 1-6 | 277 | the data-in-gate samples IMOB into 1Y and into LA 4; "IMOB data at 1Y and LA 4 registers is identical in width and relative position for all CSU's" | none | -- |
| C.11-C.12 | 1-6, 1-7 | 277-278 | exchange fetch from CSU A0; "SET BX-BFR pulse ... so BUS SET BR pulse samples data on BX MOB to BX buffer register" | none | -- |
| C.13-C.14 | 1-7 | 278 | disk synchronizer fetch; "SEL HX pulse ... so HX MOB-to-WDR pulse samples data on HX MOB into word register" | none | -- |

Figs 4.1.1-4.1.4 (PDF 279, printed 1-8) draw SP pulses numbered 0-6 with gate I
on pulse 0. IMOB DATA is low across pulse 6 (4.1.1). SELECT 1Y and SELECT 2Y are
high from just before 5 to just after 6. MEM SEL LA is high across 5 only, and
the IMOB data under it falls just after 5 (4.1.4). The figures carry no time
scale.

**Table 4.1.1, MEMORY SELECT PULSE DELAY LINE CARD LOCATIONS (PDF 274):**

| CSU | delay line card | logic page |
|---|---|---|
| A1 | 11A3J24 | 13.06.02.1 |
| B0 | 11A3J26 | 13.06.01.1 |
| B1 | 11A3J25 | 13.06.01.1 |
| B2 | 11A3J23 | 13.06.02.1 |
| B3 | 11A3J22 | 13.06.02.1 |

(A0's is step B.3's card 11A3J27, logic 13.06.01.1.)

**Table 4.1.2, MEMORY SELECT LA LEVEL PULSE DELAY LINE LOCATIONS (PDF 277):**

| test pulse | LA pulse | SP pulse | logic page | delay line | logic page |
|---|---|---|---|---|---|
| MEM SEL LA 1 | 18A3A21B | 18A3A21C | 36.01.05.1 | 12B1K18 | 17.06.01.1 |
| MEM SEL LA 2 | 18A3A21-6 | 18A3A21-5 | 36.01.06.1 | 12B1K10 | 17.06.02.1 |
| MEM SEL LA 3 | 18A3C21B | 18A3C21C | 36.01.07.1 | 12B1K12 | 17.06.02.1 |
| MEM SEL LA 4 | 18A3C21-6 | 18A3C21-5 | 36.01.08.1 | 12B1K13 | 17.06.02.1 |

There is one MEM SEL LA pulse per LA level, each with its own delay line. The
memory returns a word straight into the level that asked for it, as Blosk
p.19 says ("a three bit return address ... which Y register in this I unit, or
which of the four lookahead levels is to receive the word"). Fig 3.2.2 sheet 1
draws the same return ("MEM SEL LA 1", "GI IMOB INTO DATA FIELD").

### 5.2 What this gives, and does not give

- **Busy time per unit.** 1800 ns = 6 clocks of 0.3 µs. It is a
  console-adjusted trigger length, the time the bus control treats the CSU as
  busy. Other sources give a different number:
  - Buchholz prints "a read-write cycle time of 2.1 microseconds" (`Planning_A_
    Computer_System` OCR, PDF 42; also PDF 28: "computer timing dictates a
    slightly longer cycle of 2.1 usec"). That is 7 clocks.
  - Perf. Char. printed 3-15 (PDF 33): "a readout time of 1 µs and a recycle
    time of 2.2 µs".

  The model uses 7 (`StretchMemory.bsv` `memCycleClocks = 7`, "2.1 us").
- **Read latency, DERIVED.** Data reaches an LA level at the 5th SP pulse after
  gate I, and the 1Y/2Y register at the 5th-6th. With SP = 0.3 µs
  (`clock_unit.md` §5.2 derives this from printed 1-2, Table 2.1.1 and Vol. 3
  p.128) that is 1.5 to 1.8 µs. It brackets Buchholz printed p.206's "1.6 usec"
  return. The model uses one latency, `memReadClocks = 5`, for both.
  - What gate I is relative to the bus request is not printed. Gate I is
    DERIVED to be the gate that sends the address onto the bus. So the count
    may start one clock after the request.
- **Bus priority: not in this procedure.** It names the three requesters it
  tests (CPU, exchange, disk synchronizer), each with its own MOB: IMOB for the
  CPU, "BX MOB" for the exchange, "HX MOB" for the disk synchronizer. It prints
  no order among them. The order is Buchholz §14.3 printed pp.205-206
  (`exchange_and_io.md` §4.1):
  - exchange and disk synchronizer first;
  - then the CPU's look-ahead operand fetches;
  - then instruction fetches.

  The I-box flow diagrams add one priority line of the CPU's own: "NOT IC FETCH
  PRIORITY" (Fig 3.1.21) gates an FP left-half load. "BLOCK ESTAB OF IC FTH
  PRIORITY" (Fig 3.1.16) withholds the instruction-fetch priority while a Y
  buffer is blocked. Neither says which side wins over the bus.
- **Cycle stealing.** Nothing here times it. The exchange and disk
  synchronizer reach the same CSUs through the same bus control (steps C.11-
  C.14), which is consistent with stealing a memory cycle. The cost of each
  steal is in `exchange_and_io.md` §4.

## 6. Cross-checks: Perf. Char. Vol. 1 Tables 4-8 and Blosk

The flow diagrams print no times (§0), so the cross-check compares
**structure**: which steps exist, their order, and what waits on what. Times
come only from the two other sources. Reader F's full transcriptions, all five
tables and every timing sentence, are Appendix F.

### 6.1 Perf. Char. Vol. 1 ch.3 (3/8/61), Tables 4-8 and prose

Tables 4-8 are on printed 3-11 to 3-14 (PDF 29-32). Each entry is a time "+
dec", where the table's footnote prints "dec = decade" (DERIVED: the decode
time). Other terms are "+ LAAR" and "+ LAdr" (look-ahead drain). Apart from one
entry, **every entry is a multiple of 0.6 µs**, the I-box decode time of
printed 3-18. The exception is Table 6's EX fetch "11.2 µsec", which is not a
multiple; `clock_unit.md` §5.1 also notes it.

| Perf. Char. statement (PRINTED) | page | flow diagrams | agrees? |
|---|---|---|---|
| "The decoding time of I-box instructions is 0.6 µs"; "each indexing operation requires 0.6 µs" | 3-18 | a transfer sequencer and a MOD sequencer are separate (Figs 3.1.6-3.1.10, 3.1.15). The index read (XS READ P) is at the transfer's phase E | yes in structure: indexing is its own sequencer, decode overlaps |
| FP "decoding rate is one instruction per 1.2 µs" | 3-17 | FP triggers 1-4 per side, alternated by FP Z ALT (Figs 3.1.12-3.1.13, 3.1.18-3.1.22) | consistent: two Z registers, one FP per two I-box steps (DERIVED) |
| VFL minimum 3.6 µs "which includes the loading of two LA levels"; +0.6 per extra level or index | 3-18 | VFL loader 1-5 triggers (Table 3.4.1 3H001-3H005; Fig 3.1.24 "VFL 4 E", "VFL 5E"); Fig 3.2.9 LAOP 03/05/07 operand levels | consistent; the loaders are not drawn as figures in 3.1.6-3.1.24 |
| "The I-Checker is shared between the I-box and LA. It processes information in 0.6 µs"; a conflict delays "0.3 to 0.6 µs" | 3-19 | OCC 3rd priority, SCC 4th priority checker requests (Figs 3.2.3, 3.2.26); MOD ZL waits for "NO LA CHKR REQ" (Fig 3.1.15) | yes |
| "since there is only one LAAR, if the latter is busy ... a wait must..." | 3-21 | **two LAARs** (Figs 3.2.1, 3.2.2 sh.2, 3.2.12) | **no**: Perf. Char. (3/8/61) describes a one-LAAR machine; the CE pages (2/1/62) draw two. Already a TIE-BREAK in `spec_lookahead.md` §1.4 |
| a store into index storage stops decoding "until the new index contents arrives" | 3-21 | STORE WAIT on 11, 12, 16-31 (§2.1); SCC index write (Fig 3.2.27) | yes; the release is not drawn |
| forwarding store to fetch, case (3); "further LA loading in the I-box is delayed until the forwarding is completed" | 3-22 | LAAR compare (Fig 3.2.2 sh.1), "FETCH ACCEPTED AND NO COMPARE" (Fig 3.2.1) | compare yes; forward not drawn |
| "It takes 0.9 to 1.2 µs to process an LA level corresponding to I-box instructions. This time cannot be overlapped by concurrent E-box action" | 3-22..3-23 | I-box levels go through the ABC's transfer-indicator timer (Fig 3.2.19, LAOP 00, 02, 04, 06, 33, 51, 63) | consistent: the ABC, which serves the E-box, handles them. DERIVED: 0.9-1.2 µs is 3-4 clocks of TFR INDIC timer and ABC advance |
| a conditional branch the I-box cannot decide uses four LA levels: "three levels not unlike those for a VFL connect-to-memory instruction plus a branch recovery level ... For Bind, two of these four levels involve the LAAR" | 3-24 | LAOP 37 BI FETCH, 41 BI store, 45/47 BR RECOV, 27/55 branch levels (§2.3) | yes |
| recovery "requires shipment of index register information back to the I-box. The correct instruction counter value is also shipped back" | 3-24 | SCC writes pseudo-stores into index storage (Fig 3.2.27); HSCLN OVER: "GI IC BUFFER TO IC REG", branch-to address into the IC (Fig 3.2.23) | yes |
| "Bind for XF, XVLZ, XVZ, XVGZ, XCZ, XL, XE, XH" executed entirely in the I-box | 3-23 | updated-index indicators (Table 3.4.1 3G015-3G018, 3H015-3H018: "UPDATED INDEX REGISTER N38 INDEX FLAG" ... "N54 INDEX VALUE GT 0"; PDF 179, read by the author); HSCLN OVER reloads them | yes: eight updated-index indicators, N38 and N48-N54 |

Tables 4-8 themselves need the I-box stages before they can be checked
row by row. They are the A8 exit oracle (with the Vol. 2 atlas pages).
`spec_lookahead.md` §3.1 already shows that Blosk's 0.5 µs cycles, rescaled to
0.6, reproduce several of them.

### 6.2 Blosk, TR00.722 (Mar 1960), Figs 6-10

Blosk designs to a 0.5 µs I-unit cycle ("one machine cycle of approximately
500 mµs", p.11). The shipped machine runs at 0.6 (`clock_unit.md` §4.3).

| Blosk chart | cycles PRINTED | time at 0.5 / at 0.6 (DERIVED) | flow-diagram counterpart |
|---|---|---|---|
| Fig 6 FP instruction preparation (p.29, PDF 31) | "8 CYCLES" for 4 FP instructions | 4.0 / 4.8 µs; 1 FP per 1.2 µs at 0.6 = Perf. Char. 3-17 | Y-Z transfer + index fetch in one cycle (Fig 3.1.6 XS READ P at phase E); MOD; FP triggers; TYPE 2/3 load |
| Fig 7 VFL instruction preparation (p.32, PDF 34) | "8 CYCLES" | 4.0 / 4.8 µs | VFL loaders, WBC + DEC (Fig 3.1.23), WBC trigger (Fig 3.1.24) |
| Fig 8 Count and branch (p.34, PDF 36) | "6 CYCLES" | 3.0 / 3.6 µs; Perf. Char. Table 8 CB unsuccessful 3.6 + dec | not in 3.1.6-3.1.24 (I-box execution figures) |
| Fig 9 Transmit (p.36, PDF 38) | "SET UP 2 CYCLES", "WORD 1 5 CYCLES" | set-up 1.0 / 1.2 µs; 2.5 / 3.0 µs per word | not in these figures |
| Fig 10 Branch on indicator (p.38, PDF 40) | "5 CYCLES" | 2.5 / 3.0 µs | LAOP 11 level, ABC action on BAC (Fig 3.2.24) |

**Blosk prose that the CE figures confirm:**

- **Index storage** (p.11): "read-out time of approximately 200 mµs"; store in
  two cycles, "one for resetting, and the other for writing" (p.19). The CE
  equivalent is Fig 3.2.27's CLEAR INDEX TIMER then WRITE INDEX TIMER.
  - The seventeenth XS word holds the interval timer and the time clock.
- **Updated Indicator Register** (p.17): "eight triggers in the I unit which
  contain the status of the index register value, count, and refill fields up
  to the last instruction executed by the I unit" (XL, XE, XH, XCZ, XVLZ, XVZ,
  XVGZ, XF). The CE equivalents:
  - Table 3.4.1's eight "UPDATED INDEX REGISTER" indicators (PDF 179);
  - Fig 3.2.21's "GI MODIFIED XR IND'S FROM IND REG TO THE UPDATED INDEX IND
    REG" on a store to $IND;
  - Fig 3.2.23's reload of the register after housecleaning.
- **The I checker is time-shared** between the I unit and the look-ahead
  under "a fast priority system" (p.16). The CE prints the OCC's and SCC's
  priorities as 3rd and 4th.
- **The "guess" external fetch** (p.19). In rapid FP preparation the fetch is
  started before the memory-area decode is done, and is cancelled if the
  address is internal. In the CE: "BLOCK TYPE 2 LD TO LA", "CANCEL FPL3E" and
  "FPL3E AND NO CANCEL" (Figs 3.1.13, 3.1.21). DERIVED: the CANCEL path is the
  guess undone.
- **Every external fetch carries "a three bit return address"** that names the
  Y register or one of four LA levels (p.19). In the CE: MEM SEL LA 1-4 and SEL
  1Y/2Y (§5).
- **VFL and FP stores to index storage**: "the I unit ... waits until the
  entire operation is completed, including the resultant store back to index
  storage" (p.19-20). This is STORE WAIT (§2.4).

## 7. What A6 can build from: stores, the LAAR, forwarding

- **Two LAARs, assigned LAAR 1 first.**
  - Fig 3.2.2 sheet 2 (PDF 94): at LLP 3, "LAAR 1 BUSY" NO -> "SET FROM 1 &
    LAAR 1 BUSY"; YES -> "SET FROM 2 & LAAR 2 BUSY".
  - Fig 3.2.1 (PDF 92): the type-3 load is disabled while "BOTH LAARS BUSY",
    unless "STORE BEING DONE".
  - Fig 3.2.12 (PDF 104): the level's FROM bit gates its LAAR to the BCU at
    TBC time.

  The model has one LAAR, used by FP levels only (`StretchCore.bsv`
  `laarFreeAt`, `laarRetire`). Perf. Char. p.3-21's "only one LAAR" is the
  3/8/61 machine. Which to build is still `spec_lookahead.md` §6.2 item 9's
  choice. This file makes the two-LAAR rule fully sourced.
- **What takes a LAAR.** A TYPE 3 load:
  - FP stores, external and internal (Figs 3.1.12, 3.1.13 sh.2, 3.1.18, 3.1.20);
  - FP internal-address fetches ("ZR INT LTH" -> TYPE 3LD, "SET LA INT FETCH",
    Figs 3.1.12, 3.1.18);
  - VFL stores, through VFL loader 4 ("COND VFL 4 T3", "VFL 4 TYPE 3", Fig
    3.1.24).

  `NEXT.md`'s "LAAR for every store level, not only FP" is drawn for VFL by
  Fig 3.1.24. VFL loader 4's own flow is not among Figs 3.1.6-3.1.24 (see
  Gaps).
- **When it is freed, by path:**
  - an internal fetch or store at the ABC (Figs 3.2.16, 3.2.20, 3.2.21 "LAAR
    INT ?" -> RESET LAAR BUSY TRIG);
  - an external store at the SCC's STO DATA TIMER (Fig 3.2.26);
  - an arithmetic store into index storage at the SCC's write-index timer
    (Fig 3.2.27);
  - every level in housecleaning (Fig 3.2.22).

  The model frees it at the store level's removal plus a fitted remainder
  (`laarStorePost`). The figures say external stores free it at the SCC, which
  is after the ABC: the remainder is the SCC's wait for the store register, the
  TOB and the STAR (Fig 3.2.26).
- **Store data source.** TOB (from the level) for LAOP 31 and 33-EXT, the
  ACOB (the E-box result) for every other store (Fig 3.2.12). An I-box store
  carries its operand in the level. An arithmetic store waits for the E-box.
- **Store order and NOOP mode.** A no-op'd level with an external store waits
  for "ALL PREVIOUS STORES" (Fig 3.2.5) and "PREV STORES DONE" (Fig 3.2.14).
- **Forwarding.** The compare is drawn ("IS LAAR COMPARE ENABLED ?" ->
  "ADDRESS COMPARE ?", Fig 3.2.2 sh.1; "FETCH ACCEPTED AND NO COMPARE", Fig
  3.2.1). The forward is not (Gaps). Build it from Perf. Char. p.3-22 cases
  (2) and (3) and the fetch-to-fetch sentence, as `spec_lookahead.md` §2 does.
- **I-box store levels.** Every I-box instruction's level (LAOP 00, 02, 04,
  06, 33, 51, 63) goes through the ABC's transfer-indicator timer (Fig 3.2.19).
  An internal store (LAOP 33 INT) goes over the TOB to the E-box C register
  (Fig 3.2.13). That matches p.3-22's 0.9-1.2 µs "cannot be overlapped".
- **Exit-relevant.** The WB XOVR path is the WBC trigger (Fig 3.1.24):
  - the second word's address is "W 0-17 TO MAB" at VFL 4 E;
  - the level gets "SET LA WBC TAG";
  - LAOP 23 is "STORE (2ND)" (Fig 3.2.21).

  A crossing store is two LA levels (17 then 23, or 03 then 07 for fetches).

## 8. What A8 can build from: I-box stages, index storage, the updated-indicator register, the five counters

- **Stages, in the order the sequencers run:**
  1. Y-Z start;
  2. one of four transfer sequencers (YR-ZL, YL-ZR, YL-ZL, YR-ZR), each M,
     E·M, E. At E it does the index-storage read, "XS READ P", with the index
     address gated from the Y register;
  3. the MOD sequencer (E: X to the adder; E·M: sum to Z);
  4. decode (ZL DEC; XF + DEC; WBC + DEC);
  5. the FP or VFL loader triggers, which make TYPE 1/2/3 loads.

  Blocks and suspends (Figs 3.1.11, 3.1.16) hold a Y buffer and its fetch.
  IHW triggers pair half-words (Figs 3.1.14, 3.1.22).
- **Index storage.** It is read during the transfer (Fig 3.1.6). It is written
  by the SCC with CLEAR then WRITE timers (Fig 3.2.27), Blosk's two cycles. A
  store into words 11, 12 or 16-31 sets STORE WAIT (§2.1); the closest
  release is §2.4.
- **The updated-indicator register.**
  - Eight indicators (Table 3.4.1 3G015-3G018, 3H015-3H018, PDF 179; Blosk
    p.17's list).
  - Reloaded from the indicator register after housecleaning (Fig 3.2.23) and
    on a store to $IND (Fig 3.2.21).
  - Branches on them are resolved in the I-box (Perf. Char. p.3-23).
  - The figures that set them during preparation are not in 3.1.6-3.1.24
    (Gaps).
- **The five counters.** §2.2's table:
  - each counter has its own AES/LDE triggers and its own interlock with its
    predecessor;
  - a counter may move onto its predecessor's level while the predecessor is
    advancing ("ANTIC ABC ADV.", "TBC ADVANCING", "ABC ADVANCING");
  - the IAUC is interlocked by the SCC one level ahead.

  The model's head/tail must become five pointers to reproduce:
  - the OCC (check and correct) step, with its 3rd-priority checker request;
  - the TBC (store-gate) step;
  - the SCC step, with its 4th-priority checker request and the store
    register, TOB and STAR waits.
- **Checker priority.** OCC 3rd, SCC 4th. The MOD ZL sequencer waits for "NO
  LA CHKR REQ" (Fig 3.1.15). The 1st and 2nd priorities are not printed here.
- **No times.** Every A8 timing must come from Perf. Char. Tables 4-8, Blosk
  Figs 6-10 (at 0.6 µs a cycle) and the atlas pages, as the plan says.

## 9. What A9 can build from: recovery by levels

- **The pseudo-store level.** LAOP 02 (I BOX PSEUDO STORE), 04 (PX PSEUDO
  STORE) and 06 (no-op'd). Its index address is in op-code bits 1-4. It
  cancels later stores to the same index word by setting their op bit 0 (Fig
  3.2.27). The SCC writes it in order (Fig 3.2.25: "WRITE INDEX LA M 02, 04, 06
  ..."). LAOP 42, 44, 46 are "ILLEGAL PS STORE".
- **Housecleaning, per level** (Fig 3.2.22):
  - the ABC walks every level with the HSCLN timer;
  - it drops each level's LF tag except a pseudo-store's;
  - it frees the LAAR;
  - it copies the CNIDC indicator to the mask indicator.

  Then HSCLN OVER (Fig 3.2.23):
  - it resets the CN, DF and DS indicators, MAR MODE and the inhibit
    triggers;
  - it reloads IC from the IC buffer;
  - it reloads the updated-index indicators from the indicator register;
  - for a branch recovery, the I box puts the branch-to address in IC.
- **Entering it:**
  - an interruption ("PREVIOUS INSTR PROPERLY EXECUTED ?" NO -> HSCLN TIMER,
    Figs 3.2.14, 3.2.16);
  - a wrong branch guess (TBC "BR CONDITION MET" -> "ABC WILL CAUSE HSCLN
    MODE", Fig 3.2.5; "I BOX RQST HSCLN", Fig 3.2.18);
  - BAC (LAOP 11): "BRANCH RECOVERY" or "PSUDO IRPT RECOVERY" (Fig 3.2.24).

  The I-unit side has LARCY (LOOKAHEAD RECOVERY MODE, 3R016, 28.42.81.1),
  allowed for BE, BEW, BD, SIC-B* and EX + RN (Figs 3.1.6, 3.1.14). It also
  has PIRCY / IRCY for a program store compare (Figs 3.1.13, 3.1.20, 3.1.21).
- **The time housecleaning takes is not printed.** Fig 3.2.22's timer runs
  once per level, and Fig 3.2.23's runs once. Their phases are E·M̄, E·M and
  M, which DERIVED is one timer cycle each: so one cycle per LA level plus
  one, plus the wait for the execution units to go idle. No page gives a
  number (Gaps). Record this as the A9 plan asks.
- **The not-taken SIC's empty store level** fits LAOP 41/37 ("BI" fetch and
  store) and Perf. Char. p.3-24's "there is always a store type level,
  whether the programmer specifies a change of the tested bit or not".

## 10. What A11 can build from: memory, priority, cycle stealing

- **Busy per unit: 1800 ns, 6 clocks** (printed 1-3, PDF 274). There are six
  CSUs on the procedure's machine (A0, A1, B0-B3).
- **Read return.** The 5th SP pulse after gate I for an LA level (Fig 4.1.4),
  and the 5th-6th for 1Y/2Y (Figs 4.1.2-4.1.3). DERIVED: 1.5-1.8 µs, which
  brackets Buchholz's 1.6.
- **Each LA level has its own memory-select line** (MEM SEL LA 1-4, Table
  4.1.2). The word goes straight into the level.
- **The three requesters** each have their own MOB: CPU (IMOB), exchange (BX
  MOB) and disk synchronizer (HX MOB). They share the CSUs (steps C.11-C.14).
- **Priority order: not in this procedure.** Use Buchholz §14.3 as
  `exchange_and_io.md` §4.1 already does. The I-box side adds "IC FETCH
  PRIORITY" (Figs 3.1.16, 3.1.21) as an internal CPU arbitration between
  instruction fetch and operand loads.

## 11. Gaps, with the searches made

1. **No flow diagram prints a time.** Searched: every sheet of Figs 3.1.6-
   3.1.24 and 3.2.1-3.2.27 (49 sheets), by six readers and the author. Each
   reader's "TIME" section is "none printed".
2. **STORE WAIT's release is not drawn.** Searched:
   - Figs 3.1.6-3.1.24 for "STORE WAIT" (turn-ons on 3.1.13 sh.2 and sh.3,
     3.1.20, 3.1.21, 3.1.24; "BLOCK STORE WAIT TGR TOF" on 3.1.20 only; no
     TOF);
   - Figs 3.2.1-3.2.27 (no STORE WAIT box);
   - Table 3.4.1 (title only, PDF 183);
   - the OCR of the whole manual for "STORE WAIT" (the same hits only).

   The closest evidence is in §2.4.
3. **The forward itself is not drawn.** Fig 3.2.2 sheet 1's "ADDRESS COMPARE"
   YES exit is absent (reader D, checked at 450 dpi). No other LA figure has a
   compare box. Searched the category-2 OCR for "COMPARE" and "FORWARD": only
   PROGRAM STORE COMPARE (category 1) and "NO COMPARE" (Fig 3.2.1).
4. **The duration of housecleaning.** No time on Figs 3.2.22-3.2.23. Perf.
   Char. pp.3-23..3-24 describe recovery with no number. Blosk p.33 was not
   re-read here.
5. **Bus priority order.** Not in §4 Procedure 1 (PDF 272-279, every step
   read). Not in Figs 3.1.x or 3.2.x, which have only "IC FETCH PRIORITY" lines.
   Buchholz §14.3 is the source. Exchange against disk synchronizer is not
   ordered on any CE page read here.
6. **I checker priorities 1 and 2.** Only 3rd (OCC) and 4th (SCC) are printed
   (Figs 3.2.3, 3.2.26). The I-unit checker figures (3.1.1-3.1.5, IWC) were
   not in this task's range.
7. **VFL loaders and the I-box execution figures.**
   - Figs 3.1.25-3.1.27 (PDF 89-91) and the VFL loader 1-5 flows are outside
     3.1.6-3.1.24.
   - CB, transmit and the updated-indicator updates during preparation are
     not drawn in the range read.
   - The I-unit category's later figures, and category 3.3 onward, were not
     searched.
8. **What gate I is**, relative to the CPU's bus request (§5.2). It is not
   defined in Procedure 1.
9. **Illegible items.** Each is listed in its reader's "Could not read"
   section (Appendices A-E). None changes a structural reading above:
   - the bar over "2" in Fig 3.1.13 sh.2's "ZR 1+~2+3";
   - several ALD digits on Figs 3.1.10, 3.1.12 and 3.2.2 sh.1;
   - Fig 3.2.19's LAOP 11 gloss, "RAC" against "BAC";
   - the crossing YES/NO lines into the two recovery boxes on Fig 3.2.24
     (DERIVED pairing).

## 12. Contradictions with the model or the docs

1. **The page numbers in the plan are PDF pages.**
   - `fidelity_plan.md` step 0.3 and `source_audit.md` G5 items 5-6 call the
     ranges "printed pp.95 and 99-119" and "pp.273-279". These are PDF pages.
     The LA figures are printed 2-5 and 2-9..2-36. The procedure is printed
     1-1..1-8 and starts on PDF 272, not 273.
   - The brief for this task placed Perf. Char. Tables 4-8 at 3-16..3-24; they
     are on 3-11..3-14 (PDF 29-32).
   - It named `ADescriptionOfStretch_Dec59.pdf` as Blosk; Blosk is TR00.722.
2. **The LAAR assignment is not round-robin.** `spec_lookahead.md` line 209
   says "allocated round-robin", and §6.2 item 4 says the assignment rule is
   "[NOT IN THE SOURCES]". Fig 3.2.2 sheet 2 (PDF 94, printed 2-4) prints the
   rule: LAAR 1 if not busy, else LAAR 2.
3. **`spec_lookahead.md` detail errors:**
   - its FROM-bit ALD is 36.13.03.1; PDF 94 prints 36.16.02.1;
   - "five alternative completions" on Fig 3.2.4; PDF 96 shows four;
   - SAU LAOP "X1, 35, 43"; Figs 3.2.6 and 3.2.8 print "X1, 35, 75, 43";
   - "ADV ABC IF NOT INTLKD BY TBC" is cited to PDF 113; it is on PDF 114
     (Fig 3.2.22).
4. **One LAAR (Perf. Char. printed 3-21, PDF 39) against two (CE Figs 3.2.1,
   3.2.2, 3.2.12).** This is known, and recorded as a TIE-BREAK in
   `spec_lookahead.md` §1.4. The model has one, for FP only
   (`microarchitecture_plan.md` §1a row "One LAAR").
5. **Fig 3.1.21's "BLOCK TYPE 2 LD TO LA" is unconditional.**
   `atlas_oracle.md` line 1812 reads FPL2E as "only under 'NOT IC FETCH
   PRIORITY', and otherwise 'BLOCK TYPE 2 LD TO LA'". On PDF 85 (printed
   1-43/1-44, tile `t085_3050_1150`, re-read by the author) the block box
   hangs off the column line below the hexagon, and no NO exit is drawn. The
   reading "otherwise" is an interpretation.
   - `microarchitecture_plan.md` line 74's "FPL2E only under 'NOT IC FETCH
     PRIORITY'" is contradicted by reader C's reading of the same sheet. That
     reading has a second "COND FPL2E TON" (28.13.21.1), unconditional, on
     column A of the "ZL FP4 OR ZL FP6" bus. The author's spot-check tile did
     not cover column A, so this point rests on reader C alone.
6. **STORE WAIT citations:**
   - `microarchitecture_plan.md` line 85 cites Fig 3.1.24 for the recovery
     request. Fig 3.1.24 (PDF 88) has no IRCY/PIRCY box. The request is on
     3.1.13 sh.2-3, 3.1.20 and 3.1.21. On 3.1.24 the wording is an action box,
     "VFL 5 CL 2 COND STORE WAIT", not a hexagon test.
   - `NEXT.md` line 931 says Fig 3.1.24's hexagon "tests 'W', the word
     address". The sheet has two hexagons, "W EQ 11 + 12 + 16 - 31" and "ZL 11
     + 12 + 16 - 31", feeding the same box.
   - `StretchIBox.bsv`'s STORE WAIT note says the pages draw no release and
     that "no box takes it as a condition". Fig 3.1.20 does have "BLOCK STORE
     WAIT TGR TOF". That box blocks the TOF while the test holds, and is still
     not a release.
7. **The memory cycle.** The model's `memCycleClocks = 7` (2.1 µs) matches
   Buchholz's printed 2.1 µs (PDF 28, 42). It does not match the CE manual's
   Busy trigger, "on for 1800 nanosec" = 6 clocks (printed 1-3, PDF 274), or
   Perf. Char.'s "recycle time of 2.2 µs" (printed 3-15, PDF 33).
   - `memReadClocks = 5` is one number. The CE prints the 5th SP pulse for an
     LA level (Fig 4.1.4) and the 5th-6th for 1Y/2Y (Figs 4.1.2-4.1.3).
   - Perf. Char. 3-15 prints readout 1 µs.
   - `clock_unit.md` §5.2 gap 3 records part of this.
8. **Dates.** Index 3-2 lists Figs 3.2.16-3.2.21 as 1/1/63. Every sheet's foot
   prints 2/1/62.
9. **LAOP 11's name.** Fig 3.2.19's legend glosses it "RAC RCY (NOOP RCY REQ)"
   (as read at 600 dpi). Fig 3.2.24's caption is "ABC ACTION ON BAC (LAOP 11)".
   One of the two is DERIVED to be a misprint or a poor reproduction.
10. **Perf. Char. Table 6's "11.2 µsec"** (EX fetch, printed 3-12) is the only
    Tables 4-8 entry that is not a multiple of 0.6 µs. This is already noted in
    `clock_unit.md`.
11. **Fig 3.1.17's "BLK DEC" YES exit** is drawn into the lower decode bus.
    It does not feed the three "BLOCK ... ZR" boxes, which hang
    unconditionally. That is a probable drafting error in the source (reader
    B), and is not a doc contradiction.

## Appendices: the readers' transcriptions

Each appendix is the reader's file as it was handed back. The headings are
moved down three levels, and nothing else is changed. Every reader rendered
and read the page images. The markings (PRINTED, DERIVED, [KEY], could not
read) are the readers' own. Where §§2-6 differ from an appendix, the section
is the author's re-reading and takes precedence.

### Appendix A. Figs 3.1.6-3.1.12 (reader A)

#### Figure 3.1.6 — Y-Z START TRIGGER AND YR-ZL TRANSFER SEQUENCER

- Caption PRINTED: "FIGURE 3.1.6. Y-Z START TRIGGER AND YR-ZL TRANSFER SEQUENCER"
- PDF page 68 (R23-9732_Manual04_7101_CPU_Jan63.pdf), landscape fold-out, box text rotated 90 deg.
- Header PRINTED: "M3-04-3   I UNIT FLOW DIAGRAMS"
- Foot PRINTED: date "2/1/62", page "1-11/1-12"
- Applicability PRINTED: "CPU 7101 SER. NO. 30,004 AND HIGHER"
- Read from 300 dpi renders (rotated tiles), bar/zoom checks at 600 dpi.

Notation: `¯(X)` = X is printed with an overbar (negation). Where a bar sits between two text
lines, it cannot be told from the image whether it underlines line n or overbars line n+1; such
cases are noted "bar between lines". `•` = printed AND dot, `+` = printed OR. All box text is
PRINTED unless marked DERIVED.

##### 1. Boxes

###### 1a. Y-Z START TGR (left part of sheet)

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| A1 | hexagon | ¯(YL-ZR • R MOD) + ¯(YR-ZL • R MOD) + ¯(XF + DEC ZL MC) • SBC | (28.26.11.1) |
| A2 | trigger bar | Y-Z START TGR | (28.26.11.1) |
| A3 | rect | COND YR-ZR TON CKT | (28.15.60.1) |
| A4 | hexagon | CHK M CORR • CD Y LEFT • ZL IHW | printed "(28.5.10.1)" [sic; DERIVED probably 28.15.10.1, the box below] |
| A5 | rect | COND YL-ZR TON CKT | (28.15.10.1) |
| A6 | hexagon | CHK M CORR • NOT CD Y RIGHT • FPR BLOCK Y-Z | (28.15.30.1) |
| A7 | rect | COND YR-ZL TON CKT | (28.15.30.1) |

Flow: A1 YES -> "TON" -> A2. A2 output node feeds A3 (unconditional), A4 (YES -> A5), A6 (YES -> A7).
No NO exits are drawn.

###### 1b. YR-ZL TRANSFER SEQUENCER TON conditions (top left)

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| B1 | hexagon | ACC + COM • CD Y RIGHT • ¯(FPR BLOCK Y-Z) • CHK M COR NOT E • YL-ZR NOT MOD R + Y-Z START + ¯(MOD ZR NOT M) • ZL MT ON ACC • FW NOTS + HW • SAC • NOT CHKR SING ERR | (28.15.30.1) |
| B2 | hexagon | SAC • ZL MT • ¯(FPR BLOCK Y-Z) • CD YR • CHK M COR NOT E • YL-ZR NOT MOD R + Y-Z START + ¯(MOD ZR NOT M) • FW NOT S + HW • NOT CHKR SING ERR | (28.15.30.1) |
| B3 | sequencer bar | YR-ZL TRANSFER SEQUENCER | (28.15.30.1) |

B1 YES and B2 YES join (OR) -> "TON" -> B3. Bars: in B1 and B2 the bar over "FPR BLOCK Y-Z" is
clear; a bar is drawn between "...Y-Z START +" and "MOD ZR NOT M" (bar between lines; read as an
overbar on "MOD ZR NOT M"). Line breaks in B1 as printed: "ACC + COM • CD Y / RIGHT • FPR BLOCK Y-Z • /
CHK M COR NOT E • YL- / ZR NOT MOD R + Y-Z START + / MOD ZR NOT M • ZL MT ON / ACC • FW NOTS + HW • SAC • /
NOT CHKR SING ERR". Line breaks in B2: "SAC • ZL MT • FPR / BLOCK Y-Z • CD YR • / CHK M COR NOT E • /
YL-ZR NOT MOD / R + Y-Z START + / MOD ZR NOT M • FW / NOT S + HW • NOT / CHKR SING ERR".

###### 1c. Phase M of YR-ZL TRANSFER SEQUENCER

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| M1 | rect | TOF YR - ZL E TGR | (28.15.30.1) |
| M2 | rect | COND MOD ZL TGR TON | (28.15.40.1) |
| M3 | hexagon | IHW RDY - ZR | (28.15.32.1) |
| M4 | hexagon | ZL IHW • ¯(BLOK XF + DEC) • NOT IHW EX | (28.15.50.1) |
| M5 | hexagon | NOT I EX IN PROGRESS | (28.15.50.1) |
| M6 | rect | COND XF + DEC ZL TON CKT | (28.15.50.1) |
| M7 | hexagon | NOT ZL MOD R • FW NOT ST + PROG IX (bars: a bar runs under "NOT ZL MOD"/over "R • FW NOT ST", and a bar between "R • FW NOT ST +" and "PROG IX"; negation scope not resolvable) | (28.15.32.1) |
| M8 | rect | COND YL-ZR TON | (28.15.10.1) |
| M9 | rect | COND YR-ZR TON | (28.15.60.1) |
| M10 | hexagon | NOT ZL MOD R • ZL FP CL • NOT IHW EX | (28.15.32.1) |
| M11 | rect | INSTR PREP COMP ZL | (28.27.32.1) |
| M12 | hexagon | ZL MOD R | (28.15.32.1) |
| M13 | rect | BLOCK Y - Z START TON | (28.26.11.1) |
| M14 | rect | COND XOF 1 TON | (28.12.11.1) |

M4: bar over "BLOK" (line 1) and over "XF + DEC" (line 2): read as one overbarred signal "BLOK XF + DEC".
Chains: M4 YES -> M5 YES -> M6. M7 YES -> M8 and M9. M10 YES -> M11. M12 YES -> M13 and M14.

M3 (IHW RDY - ZR) YES drives a bus (DERIVED name "IHW-RDY bus", drawn just below the E·M line) carrying:

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| R1 | rect | COND INTRPT EN GEN CKTS | (28.70.84.1) |
| R2 | rect | COND ADD 1 TON | (28.75.71.1) |
| R3 | hexagon | BE + BEW + BD + SIC - B(L) - BEW - BD ("BL" printed with a small L) | (28.89.32.1) |
| R4 | hexagon | EX + RN | (28.89.37.1) |
| R5 | rect | ALLOW LARCY TON | (28.42.81.1) |
| R6 | hexagon | BD + SIC - BD | (28.70.84.1) |
| R7 | rect | PRE - DSAB | (37.51.03.1) |
| R8 | rect | BLOCK YR-ZL M TGR TOF | "28.15.30.1)" printed without opening parenthesis |
| R9 | rect | COND LOP 4 TON | (28.88.34.1) |
| R10 | rect | COND LOP 5 TON | (28.88.41.1) |
| R11 | rect | COND DEC 1 TON | (28.75.11.1) |
| R12 | rect | COND LAM 1 TON | (28.81.11.1) |
| R13 | rect | COND TON EMF 1 | (28.70.34.1) |
| R14 | rect | COND XSF3 TON | (28.71.11.1) |
| R15 | rect | COND TON 1 EXP TGR | (28.87.64.1) |
| R16 | rect | COND DEC 3 TON | (28.70.14.1) |
| R17 | rect | COND EMF5 TON | (28.70.21.1) |
| R18 | rect | COND DEC 4 TON | (28.79.14.1) |
| R19 | rect | COND ADD 3 TON | (28.75.51.1) |
| R20 | rect | (empty box, no text printed) | none |

R3 YES and R4 YES meet at a node -> R5 (OR). R6 YES -> R7. All others unconditional on the bus.

###### 1d. Phase E·M

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| EM1 | rect | GT AOB TO ZL | (28.15.41.1 • 28.15.71.1) |
| EM2 | rect | GT AOB TO ZL | (28.27.57.1) |

###### 1e. Phase E (boxes above the E line)

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| E1 | hexagon | YR-ZL M TGR OFF | none printed |
| E2 | rect | PREP RST X 0-63 | (28.86.57.1) |
| E3 | hexagon | ¯(FP RDY ZR) • SBC | (28.15.10.1) |
| E4 | rect | TOF YL-ZR M TGR | (28.15.10.1) |
| E5 | hexagon | FP CL 2YR • SBC • CD 2Y-ZL | (28.26.56.1) |
| E6 | rect | COND ZL FP 1-4 SET • RESET CKTS | (28.26.56.1) |

E1 YES, line labelled "E • M̄" (M with overbar) -> E2. E3 YES -> E4. E5 YES -> E6.

###### 1f. Phase E (hexagons below the E line, on the E line itself)

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| E7 | hexagon | CD 1Y-ZL • ¯(1BIT MOD L) | (28.15.31.1) |
| E8 | rect | GT 1Y 60-63 TO XAB 1-4 | (28.15.61.1) |
| E9 | hexagon | CD 2Y-ZL • 1BIT MOD L (no bar visible at 600 dpi) | (28.15.61.1) [as printed; neighbours print 28.15.31.1] |
| E10 | rect | GT 2Y 60-63 TO XAB 1-4 | (28.15.61.1) |
| E11 | hexagon | CD 1Y-ZL • 1BIT MOD L | (28.15.31.1) |
| E12 | rect | GT 1Y 63 TO XAB 4 | (28.15.61.1) |
| E13 | hexagon | CD 2Y-ZL • 1BIT MOD L | (28.15.31.1) |
| E14 | rect | GT 2Y 63 to XAB 4 | (28.15.61.1) |
| E15 | hexagon | CD 1Y-ZL | (28.15.31.1) |
| E16 | hexagon | CD 2Y-ZL | (28.15.31.1) |
| E17 | rect | COND ZL FP TON CKT | (28.26.63.1) |
| E18 | rect | GT 2Y+1Y TO ABB COND TAGS ZL | (28.26.10.1 28.27.30.1 28.27.40.1) |
| E19 | rect | GT 2YR+1YR TO ABB | none printed |

E7 YES -> E8; E9 YES -> E10; E11 YES -> E12; E13 YES -> E14. E15 and E16 hang from one common stub
on the E line; E15 YES and E16 YES join (OR) -> E17, E18, E19.
DERIVED: E7/E8 vs E11/E12 = without 1-bit modification all four index-address bits 60-63 are gated to
XAB 1-4; with 1-bit modification only bit 63 goes to XAB 4. E9 prints no overbar although it is
paired with E10 (60-63) as E7 is; possibly a dropped bar. Flagged, not corrected.

###### 1g. Phase E — vertical E branch (from E line down the left side) and its two buses

From the E line a vertical runs down; on it hangs:

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| F1 | hexagon | FW NOT S • 1Y + 2Y • SBC | (28.26.60.1) |

F1 YES drives a bus ("FW NOT S bus", DERIVED name) carrying:

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| F2 | rect | TON FW NOT • S TGR | (28.26.60.1) |
| F3 | hexagon | 1Y26 • ¯(1Y 27) | (28.26.20.1) |
| F4 | rect | 1YLD FP TO SAD-LID DCDR | (28.62.11.1) |
| F5 | rect | COND ZR FP TGR TON | (28.26.62.1) |
| F6 | rect | COND ZR FPI TGR TON | (28.26.62.1) |
| F7 | rect | COND FP CL RESET LINES | (28.36.51.1) |
| F8 | rect | BLOCK ZR IHW TON | (28.26.61.1) |
| F9 | rect | BLOCK TOF OF FPR CL 1 • 2 • 3 • 4 | (28.26.58.1) |
| F10 | rect | FWS + HW TO Y DCD IHW CKTS | (28.26.61.1) |
| F11 | rect | FWS + HW TO Y DCD FP CKTS | (28.26.62.1) |
| F12 | rect | BLOCK ZR FP TGR TON | (28.26.62.1) |
| F13 | rect | BLOCK SETTING OF ZR FP 1 | (28.26.50.1) |
| F14 | rect | BLOCK RESET OF ZR FP 1 | (28.26.50.1) |
| F15 | rect | BLOCK ZR FP 2 TON | (28. 26.51.1) |
| F16 | rect | BLOCK RESET OF ZR FP 2 | (28.26.51.1) |
| F17 | rect | BLOCK ZR FP 3 TON | (28.26.51.1) |
| F18 | rect | BLOCK RESET ZR FP 3 | (28.26.51.1) |
| F19 | rect | BLOCK ZR FP 4 TON | (28.26.51.1) |
| F20 | rect | BLOCK ZR FP 4 RESET | (28.26.51.1) |
| F21 | rect | 2Y LD FP TO SAD - LID DCDR | (28.62.13.1) |
| F22 | hexagon | CD 2Y-ZR • FW S + HW • ¯(FW ST 2Y) | (28.26.61.1) |
| F23 | rect | COND ZR IHW TON | (28.26.61.1) |
| F24 | hexagon | YL-ZRE • CD 2Y-ZR • SBC | (28.26.58.1) |
| F25 | rect | TOF FPR CL 1 • 2 • 3 • 4 TGRS | (28.26.58.1) |
| F26 | rect | BLOCK ZR FP6 RESET | (28.26.51.1) |
| F27 | rect | BLOCK ZR FP6 TON | (28.26.51.1) |

F3 YES -> F4..F11 (eight boxes). F22 YES -> F23. F24 YES -> F25. F26 and F27 are drawn far below,
reached by long verticals from the F1 bus that cross the bottom bus without junction dots.
"FPI" in F6: printed "FPI" (DERIVED probably FP1).

The same E vertical continues down to a bottom bus ("bottom E bus", DERIVED name) carrying,
left to right:

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| G1 | rect | TOF ZLNA • ZLXA • ZLSA TGRS | (28.51.08.1) |
| G2 | rect | RESET ZL ADDR 8 TGR (below the bus) | (28.27.57.1) |
| G3 | rect | TOF CD YR-Z | (28.26.10.1) |
| G4 | rect | XS READ P | (24.00.09.1) |
| G5 | rect | COND ZR • ZL IHW TGRS TON CKTS | (28.26.61.1) |
| G6 | rect | COND ZL DEC TGR TON CKT | (28.27.30.1) |
| G7 | rect | COND ZR WAS IHW TGR TON CKT | (28.15.51.1) |
| G8 | rect | COND MOD ZR TOF CKT | (28.15.20.1) |
| G9 | rect | COND 1 BIT MOD TON CKT | (28.26.23.1) |
| G10 | rect | COND ZL MOD TON CKT | (28.26.23.1) |
| G11 | rect | COND ZL FP CL TGRS TON CKTS | (28.26.56.1) |
| G12 | rect | COND MOD L TGR TON CKT | (28.26.27.1) |
| G13 | rect | ¯(INH NIDC SET) ¯(IDC CR XAC) (both lines overbarred) | (28.86.55.1) |
| G14 | rect | COND ZL IDC TON • TOF CKTS | (28.51.03.1) |
| G15 | rect | COND ZLAD TON • TOF CKTS | (28.51.04.1) |
| G16 | rect | COND ZLIF TON • TOF CKTS | (28.51.05.1) |
| G17 | rect | TOF FP 3 M | (28.13.31.1) |
| G18 | rect | TOF FP 4 M | (28.13.41.1) |
| G19 | rect | TOF VFL 5 M | (28.11.51.1) |
| G20 | rect | COND ZDS • ZDF TOF CKTS | (28.51.06.1) |
| G21 | rect | TOF BROK TOR | (28.71.40.1) |
| G22 | hexagon | HW CL 1Y • CD 1Y - ZL • SBC (stray specks after first "•") | (28.26.58.1) |
| G23 | hexagon | HW CL 2Y • CD 2 Y-ZL • SBC | (28.26.58.1) |
| G24 | rect | TOF 1P C 1•2• 3•4•6 TGRS (printed "1P C"; DERIVED possibly "FP C") | (28.26.58.1) |
| G25 | rect | HOLD DATA SELECT PREP | (28.96.43.1) |
| G26 | rect | TOF Y-Z START TGR | (28.26.11.1) |
| G27 | rect | TOF FW WBC TGRS | (28.22.02.1) |

G22 YES and G23 YES join (OR) -> G24.

##### 2. Structure

- **Y-Z START TGR (28.26.11.1)**: TON = A1 YES. No TOF drawn on this sheet's trigger bar; the TOF is
  box G26 "TOF Y-Z START TGR" at YR-ZL phase E, and M13 "BLOCK Y - Z START TON" at phase M when ZL MOD R.
  Outputs: A3 unconditional; A4 -> A5; A6 -> A7. No phase lines.
- **YR-ZL TRANSFER SEQUENCER (28.15.30.1)**: vertical bar, TON = B1 + B2. Phase lines in order from the
  top: M, E • M, E. No TOF drawn into the bar; M1 "TOF YR - ZL E TGR" and R8 "BLOCK YR-ZL M TGR TOF"
  name its E and M triggers (DERIVED: E TGR and M TGR make up the sequencer).
  - M: M1, M2, M3 (-> IHW-RDY bus R1..R20), M4 chain, M7, M10, M12.
  - E • M: EM1, EM2.
  - E: E1..E6 above; E7..E19 below; vertical branch F1 (-> F2..F27) and bottom bus G1..G27.

##### 3. Step table

| phase | condition(s) PRINTED | action(s) PRINTED | ALD | notes |
|---|---|---|---|---|
| Y-Z START TON | ¯(YL-ZR • R MOD) + ¯(YR-ZL • R MOD) + ¯(XF + DEC ZL MC) • SBC | Y-Z START TGR on | 28.26.11.1 | |
| Y-Z START | — | COND YR-ZR TON CKT | 28.15.60.1 | |
| Y-Z START | CHK M CORR • CD Y LEFT • ZL IHW | COND YL-ZR TON CKT | 28.15.10.1 | hex ref printed 28.5.10.1 |
| Y-Z START | CHK M CORR • NOT CD Y RIGHT • FPR BLOCK Y-Z | COND YR-ZL TON CKT | 28.15.30.1 | |
| YR-ZL TON | B1 + B2 (see 1b) | YR-ZL TRANSFER SEQUENCER on | 28.15.30.1 | |
| M | — | TOF YR - ZL E TGR; COND MOD ZL TGR TON | 28.15.30.1; 28.15.40.1 | |
| M | ZL IHW • ¯(BLOK XF + DEC) • NOT IHW EX, then NOT I EX IN PROGRESS | COND XF + DEC ZL TON CKT | 28.15.50.1 | |
| M | NOT ZL MOD R • FW NOT ST + PROG IX (bars see M7) | COND YL-ZR TON; COND YR-ZR TON | 28.15.10.1; 28.15.60.1 | |
| M | NOT ZL MOD R • ZL FP CL • NOT IHW EX | INSTR PREP COMP ZL | 28.27.32.1 | |
| M | ZL MOD R | BLOCK Y - Z START TON; COND XOF 1 TON | 28.26.11.1; 28.12.11.1 | |
| M | IHW RDY - ZR | R1, R2, R8..R20 (COND ... TON list) | see 1c | |
| M | IHW RDY - ZR and (BE + BEW + BD + SIC - BL - BEW - BD or EX + RN) | ALLOW LARCY TON | 28.42.81.1 | |
| M | IHW RDY - ZR and BD + SIC - BD | PRE - DSAB | 37.51.03.1 | |
| E • M | — | GT AOB TO ZL (twice) | 28.15.41.1 • 28.15.71.1; 28.27.57.1 | |
| E | YR-ZL M TGR OFF (line "E • M̄") | PREP RST X 0-63 | 28.86.57.1 | |
| E | ¯(FP RDY ZR) • SBC | TOF YL-ZR M TGR | 28.15.10.1 | |
| E | FP CL 2YR • SBC • CD 2Y-ZL | COND ZL FP 1-4 SET • RESET CKTS | 28.26.56.1 | |
| E | CD 1Y-ZL • ¯(1BIT MOD L) | GT 1Y 60-63 TO XAB 1-4 | 28.15.61.1 | |
| E | CD 2Y-ZL • 1BIT MOD L (sic) | GT 2Y 60-63 TO XAB 1-4 | 28.15.61.1 | |
| E | CD 1Y-ZL • 1BIT MOD L | GT 1Y 63 TO XAB 4 | 28.15.61.1 | |
| E | CD 2Y-ZL • 1BIT MOD L | GT 2Y 63 to XAB 4 | 28.15.61.1 | |
| E | CD 1Y-ZL + CD 2Y-ZL | COND ZL FP TON CKT; GT 2Y+1Y TO ABB COND TAGS ZL; GT 2YR+1YR TO ABB | 28.26.63.1; ... | |
| E | FW NOT S • 1Y + 2Y • SBC | F2, F12..F21, F26, F27 | see 1g | |
| E | FW NOT S... and 1Y26 • ¯(1Y 27) | F4..F11 | see 1g | |
| E | FW NOT S... and CD 2Y-ZR • FW S + HW • ¯(FW ST 2Y) | COND ZR IHW TON | 28.26.61.1 | |
| E | FW NOT S... and YL-ZRE • CD 2Y-ZR • SBC | TOF FPR CL 1 • 2 • 3 • 4 TGRS | 28.26.58.1 | |
| E | — (bottom bus) | G1..G21, G25..G27 incl. XS READ P, TOF Y-Z START TGR | see 1g | |
| E | HW CL 1Y • CD 1Y - ZL • SBC + HW CL 2Y • CD 2 Y-ZL • SBC | TOF 1P C 1•2•3•4•6 TGRS | 28.26.58.1 | |

##### 4. Counters, timers, triggers, registers named

- Triggers: Y-Z START TGR; YR-ZL E TGR; YR-ZL M TGR; MOD ZL TGR; YL-ZR M TGR; FW NOT S TGR; ZR FP TGR;
  ZR FP1 ("FPI") TGR; ZR FP 1..4, FP6; FPR CL 1-4 TGRS; ZLNA, ZLXA, ZLSA TGRS; ZR, ZL IHW TGRS;
  ZL DEC TGR; ZR WAS IHW TGR; MOD ZR; MOD L TGR; ZL IDC; ZLAD; ZLIF; ZDS, ZDF; ZL FP CL TGRS;
  1 EXP TGR; FW WBC TGRS; ZL ADDR 8 TGR; 1P C 1,2,3,4,6 TGRS; XOF 1; LOP 4, LOP 5; DEC 1, 3, 4;
  LAM 1; EMF 1, EMF5; XSF3; ADD 1, ADD 3; LARCY; BROK TOR; FP 3 M, FP 4 M, VFL 5 M (TOF).
- Registers/data paths: Y (1Y, 2Y; YL, YR; 1YR, 2YR), ZL, ZR, AOB (GT AOB TO ZL), XAB (bits 1-4),
  ABB, X 0-63 (PREP RST X 0-63), SAD-LID DCDR (decoder), Y DCD, XS (XS READ P), DATA SELECT (HOLD DATA SELECT PREP).
- Counters: none named. Timers: none named. LAOP codes: none.

##### 5. TIME

PRINTS NO TIME. Only phase names (M, E • M, E, and the line label "E • M̄") appear; no clock, cycle,
A/B pulse or duration.

##### 6. [KEY] items

- **[KEY]** XS READ P (24.00.09.1) — at YR-ZL phase E, bottom bus, unconditional: the index-storage read
  is started from the YR-ZL transfer.
- **[KEY]** GT 1Y 60-63 TO XAB 1-4 / GT 2Y 60-63 TO XAB 1-4 / GT 1Y 63 TO XAB 4 / GT 2Y 63 to XAB 4
  (28.15.61.1), gated by CD 1Y-ZL / CD 2Y-ZL and 1BIT MOD L — the index address (I field bits 60-63) to
  the index address bus at E.
- **[KEY]** BLOCK Y - Z START TON (28.26.11.1) when ZL MOD R (28.15.32.1), phase M — Y-Z start blocked
  while ZL is awaiting index modification; also COND XOF 1 TON.
- **[KEY]** Y-Z START TON condition: "¯(YL-ZR • R MOD) + ¯(YR-ZL • R MOD) + ¯(XF + DEC ZL MC) • SBC" (28.26.11.1).
- **[KEY]** "FPR BLOCK Y-Z" in YR-ZL TON (B1, B2 overbarred) and in "CHK M CORR • NOT CD Y RIGHT • FPR BLOCK Y-Z"
  -> COND YR-ZL TON CKT: an FPR block of the Y-Z transfer.
- **[KEY]** "MOD ZR NOT M" (overbarred) and "YL-ZR NOT MOD R" in the YR-ZL TON conditions.
- **[KEY]** "BLOK XF + DEC" (overbarred) in ZL IHW • ¯(BLOK XF + DEC) • NOT IHW EX (28.15.50.1); "NOT I EX IN PROGRESS".
- **[KEY]** "NOT CHKR SING ERR" and "CHK M COR NOT E" / "CHK M CORR" in the TON conditions (checker single
  error / check-M correction gate the transfer).
- **[KEY]** BLOCK YR-ZL M TGR TOF (28.15.30.1) on IHW RDY - ZR.
- **[KEY]** ALLOW LARCY TON (28.42.81.1) on BE + BEW + BD + SIC - BL - BEW - BD (28.89.32.1) or EX + RN (28.89.37.1).
- **[KEY]** PRE - DSAB (37.51.03.1) on BD + SIC - BD (28.70.84.1).
- **[KEY]** BLOCK ZR IHW TON; BLOCK ZR FP TGR TON; BLOCK SETTING/RESET OF ZR FP 1..4, FP6; BLOCK TOF OF FPR CL 1•2•3•4 —
  the full-word-not-store (FW NOT S) block set at E.
- Not printed on this sheet: STORE WAIT, LA full, IAUC, LAAR, pseudo-store, houseclean, store-address compare,
  IC FETCH PRIORITY, "updated indicator", index recovery.

##### 7. Could not read / uncertain

- M7 negation scope (bars between lines).
- E9 missing overbar and ALD 28.15.61.1 (as printed; not corrected).
- A4 ALD printed "(28.5.10.1)".
- G24 "1P C" (clearly printed, meaning unknown).
- R3 "B L" (small L after B).
- E1 and E19 print no ALD reference. R20 is an empty box.

#### Figure 3.1.7 — YL-ZR TRANSFER SEQUENCER

- Caption PRINTED: "FIGURE 3.1.7. YL-ZR TRANSFER SEQUENCER"
- PDF page 69, landscape fold-out, box text rotated 90 deg.
- Header PRINTED: "M3-04-3   I UNIT FLOW DIAGRAMS"
- Foot PRINTED: "2/1/62", "1-13/1-14"
- Applicability PRINTED: "CPU 7101 SER. NO. 30,004 AND HIGHER"
- Read from 300 dpi rotated tiles; big hexagons and doubtful labels checked at 600 dpi.

Notation as in fig_3.1.6_s3.md: `¯(X)` = overbar printed over X; bars at line breaks are
ambiguous (underline of line n vs overbar of line n+1) and are stated as read.

##### 1. Boxes

###### 1a. Sequencer TON

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| S1 | hexagon | NORMAL YL-ZR XFER | (28.15.10.1) |
| S2 | hexagon | ANTIC YL-ZR XFER | (28.15.10.1) |
| S3 | sequencer bar | YL-ZR TRANSFER SEQUENCER | (28.15.10.1) |

S1 YES and S2 YES join (OR) -> "TON" -> S3. Phase lines from S3: M, E • M, E.

###### 1b. Phase M

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| M1 | hexagon | NOT ZR MOD | "(28.15.12.1" (no closing parenthesis) |
| M2 | rect | COND YR-ZL TON CKT | (28.15.30.1) |
| M3 | rect | COND IHW RDY ZR TGR TON CKT | (28.26.11.1) |
| M4 | rect | COND IHW EX ZR TGR TON CKT | (28.26.11.1) |
| M5 | hexagon | ZR FP CL • NOT ZR MOD | (28.15.12.1) |
| M6 | hexagon | FP Z ALT TGR OFF | (28.27.32.1) |
| M7 | rect | FP RDY ZR • FP RDY ZR IC | (28.20.21.1 • 28.44.28.1) |
| M8 | hexagon | FP Z ALT TGR OFF • FP CL 2 ZR | (28.27.32.1) |
| M9 | rect | COND INSTR CHK ENSLD CKT | (28.41.50.1) |
| M10 | rect | COND MOD ZR TON CKT | (28.15.20.1) |
| M11 | hexagon | NOT ZR MOD | (28.27.32.1) |
| M12 | rect | PREV ZR PREP COMPL | (28.44.25.1) |
| M13 | hexagon | ZR MOD T (printed "T", checked at 600 dpi; DERIVED probably "ZR MOD R") | (28.15.12.1) |
| M14 | rect | BLOCK Y-Z START TGR TON | (28.26.11.1) |
| M15 | rect | ZL + ZR PREP NOT BUSY | (28.20.21.1) |
| M16 | hexagon | ¯(ZR WAS IHW) | (28.15.71.1) |
| M17 | rect | Y-Z M • MOD REQ | (28.70.42.1) |
| M18 | rect | TOF YL-ZR E TGR | (28.15.10.1) |

Chains: M1 YES -> M2. M5 YES -> node -> M6 (YES -> M7) and M8 (YES -> M9). M11 YES -> M12.
M13 YES -> M14 and M15. M16 YES -> M17. M3, M4, M10, M18 unconditional.

###### 1c. Phase E • M

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| EM1 | rect | GT AOB TO ZR | (28.15.21.1 • 28.27.57.1) |
| EM2 | rect | GT AOB 32 to ZR | (28.27.51.1) |

###### 1d. Phase E — everything below

The E line runs down the left edge to a bottom bus; several verticals rise from the bottom bus
and a second horizontal bus (DERIVED name "mid E bus") runs across the middle of the sheet. All of
these are connected to E without any condition, so every box below is at phase E, gated only
by the hexagons named in its chain.

On the E line, left edge:

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| E1 | hexagon | FP CL 2YL • SBC • CD 2Y-ZR | (28.26.54.1) |
| E2 | rect | COND ZRFP 1•2•3•4•6 SET• RESET CKTS | (28.26.54.1) |
| E3 | rect | RESET ZR ADDR 8 TGR | (28.27.57.1) |

E1 YES -> E2. E3 unconditional.

Bottom bus, left part (unconditional):

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| E4 | rect | TON YL-ZR M TGR | (28.15.10.1) |
| E5 | rect | COND ZR IHW TON CKT | (28.26.61.1) |
| E6 | rect | COND ZR FL PT TGR TON CKT | (28.26.62.1) |
| E7 | rect | GENERATE SA PULSES | (24.00.09.1) |
| E8 | rect | HOLD DATA SELECT PREP | (28.96.43.1) |

First vertical (1Y side):

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| E9 | hexagon | CD 1Y-ZR | (28.15.11.1) |
| E10 | rect | GT 1YL TO ABB | (28.27.53.1) |
| E11 | hexagon | ZR IHW BL IF | (28.27.30.1) |
| E12 | rect | TON ZR BLOCK 1Y TGR | (28.42.41.1) |
| E13 | hexagon | UNCOND + BIT BR + IND BR 1YL | (28.27.31.1) |
| E14 | rect | TON ZR SPND TGR (stray mark over the R) | (28.42.43.1) |
| E15 | hexagon | SBC • DEC MOD REG FR 1YL • BIT BR DEC 1 • UNCOND + BIT BR CY 1 YL + YLD BRC • 1Y31 (no bars; "REG" as printed) | (28.26.21.1) |
| E16 | hexagon | SBC • ¯(IMM IX 1YL) + ¯(NOT FW NOTS) • 1Y31 + 1Y30 + 1Y28 + 1Y29 • DEC MOD REQ FR 1YL • ¯(BIT BR DEC 1) + ¯(UNCOND + BIT BR CL 1 YL) + ¯(1YLD BRC) | (28.26.21.1) |
| E17 | rect | TON ZR MOD R TGR | (28.26.21.1) |
| E18 | hexagon | ¯(1BIT MOD R) • CD 1Y-ZR • | (28.15.11.1) |
| E19 | rect | GT 1Y 28-30 TO XAB 1-3 | (28.27.52.1) |
| E20 | hexagon | 1 BIT MOD R • CD 1 Y-ZR | (28.15.11.1) |
| E21 | rect | GT 1Y31 TO XAB 4 | (28.27.52.1) |

Chains: E9 YES -> E10, then on -> E11 (YES -> E12) and -> E13 (YES -> E14) (E11 and E13 hang on
the continuation of E9's YES line, so they are gated by CD 1Y-ZR). E15 YES and E16 YES join (OR)
-> E17. E18 YES -> E19, line continues to E21; E20 YES joins that line above E21. (DERIVED: no
1-bit mod -> bits 28-30 to XAB 1-3 and bit 31 to XAB 4; 1-bit mod -> bit 31 only.)
E16 bars, 600 dpi: bar over "IMM IX 1YL"; a bar under "SBC • IMM IX 1YL +" spanning "NOT FW NOTS";
bar between line 3 and 4 spanning "BIT BR DEC 1"; bar between lines 4/5 over "UNCOND + BIT BR CL 1 YL";
bar between lines 5/6 over "1YLD BRC". No bars on "1Y31 + 1Y30 + 1Y28 + 1Y29".

Second vertical (2Y side):

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| E22 | hexagon | CD 2Y-ZR • NOT FP CL 2Y • SBC | (28.26.58.1) (smeared but legible) |
| E23 | rect | TOF FPR CL 1•2•3•4•6 TGR | (28.26.51.1) |
| E24 | hexagon | ¯(2YLD BRC • BIT BR) ¯(DEC.3) + ¯(UNCOND + BIT BR) ¯(CY 2YL) • DEC MOD REQ FR 2YL • ¯(2Y31) + ¯(2Y30) + ¯(2Y28) + ¯(2Y29) • ¯(IMM IX 2 YL) + NOT ¯(FW NOTS) • SBC | (28.26.25.1) |
| E25 | hexagon | 2Y31 • DEC MOD REQ FR 2YL • 2YLD BRC + BIT BR DEC 3 • UNCOND + BIT BR CL 2YL • SBC | (28.26.25.1) |
| E26 | rect | SET MOD R TGR | (28.26.21.1) |
| E27 | hexagon | ¯(1 BIT MOD R) • CD 2Y-ZR | "(28.15.10.1)" as read; under a smear |
| E28 | rect | GT 2Y 28-30 TO XAB 1-3 (mark over X) | (28.27.52.1) |
| E29 | hexagon | 1 BIT MOD R • CD 2Y - ZR | (28.15.11.1) |
| E30 | rect | GT 2Y 31 TO XAB 4 | (28.27.52.1) |
| E31 | hexagon | CD 1Y-ZR | (28.15.10.1) |
| E32 | rect | GT 1YL TO ABB COND TAGS ZR | (28.26.10.1 • 28.27.40.1) |

E22 YES -> E23. E24 YES and E25 YES join (OR) -> E26. E27 YES -> E28 -> continues to E30; E29
YES joins above E30. E31 YES -> E32. E24 bar layout, 600 dpi: line 1 "2YLD BRC • BIT BR" has one
continuous bar; line 2 bars over "DEC.3" and over "UNCOND + BIT BR"; line 3 bar over "CY 2YL";
line 4 bars over each of 2Y31, 2Y30, 2Y28; line 5 bars over "2Y29" and "IMM IX 2 YL"; line 6 bar
over "FW NOTS" (the "NOT" at the end of line 5 is not barred).

Third vertical / mid E bus (right half):

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| E33 | hexagon | CD 2Y-ZR | (28.15.11.1) |
| E34 | rect | GT 2YL TO ABB COND TAGS ZR | (28.26.10.1) (28.26.40.1) |
| E35 | hexagon | FP CL 1 YL • SBC • CD 1 Y - ZR | (28.26.50.1) |
| E36 | rect | COND FP CL R TON CKT | (28.26.51.1) |
| E37 | rect | COND ZR FP 1 TON CKTS | (28.26.50.1) |
| E38 | hexagon | NOT FP CL 1 Y • CD 1 Y -ZR • SBC | (28.26.58.1) |
| E39 | rect | TOF FPR CL 1•2•3•4•6 TGR | (28.26.51.1) |
| E40 | hexagon | SBC | (28.26.11.1) |
| E41 | rect | TOF Y-Z START TGR | (28.26.11.1) |
| E42 | hexagon | CD 1Y-ZR3 (printed so, with a stray mark before CD; 600 dpi) | (28.26.11.1) |
| E43 | rect | GT 1 YL TO ABB | (28.27.53.1) |
| E44 | hexagon | UNCOND + BIT BRC + IND BR 2YL | (28.27.31.1) |
| E45 | rect | BR Y-Z XFER TON ZR SPND 1Y | (28.42.42.1) |
| E46 | hexagon | ZR IHW BL IF | (28.27.30.1) |
| E47 | rect | TON ZR BLOCK 2Y TGR | (28.42.41.1) |

E33 YES -> E34. E35 YES -> E36, E37. E38 YES -> E39. E40 YES -> E41. E42 YES -> E43 then on to
E44 (YES -> E45) and E46 (YES -> E47) (mirror of the E9 chain).

Mid E bus (unconditional except where a hexagon is shown):

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| E48 | hexagon | YL-ZR NM | none printed |
| E49 | rect | PREP RST X 0-63 | (28.86.57.1) |
| E50 | hexagon | FW NOTS • SBC | (28.15.30.1) |
| E51 | rect | TOF YR-ZLM TGR | none printed |
| E52 | hexagon | FP MOD RDY | (28.15.40.1) |
| E53 | rect | TOF MOD ZL M TGR | (28.15.40.1) |
| E54 | rect | TOF FPL 3M TGR | (28.13.31.1) |
| E55 | rect | TOF FPL 4M TGR | (28.13.41.1) |
| E56 | rect | TOF VFL 5M TGR | (28.11.51.1) |
| E57 | rect | INH NIDC SET IX FR XAC (no bar visible) | none printed |
| E58 | rect | TOF ZR ICC TGR ("ICC" as printed) | (28.51.02.1) |
| E59 | rect | COND ZRAD TON • TOF CKTS | (28.51.04.1) |
| E60 | rect | COND ZRIF TON • TOF CKTS | (28.51.05.1) |
| E61 | rect | TOF ZDS • ZDF TGRS | (28.51.06.1) |

E48 YES on a line labelled "E • M̄" -> E49. E50 YES -> E51. E52 YES -> E53.

##### 2. Structure

- **YL-ZR TRANSFER SEQUENCER (28.15.10.1)**: TON = NORMAL YL-ZR XFER + ANTIC YL-ZR XFER. No TOF
  drawn into the bar; its triggers are named as "YL-ZR E TGR" (TOF at M, box M18) and
  "YL-ZR M TGR" (TON at E, box E4). Phase lines: M (M1..M18), E • M (EM1, EM2), E (E1..E61).

##### 3. Step table

| phase | condition(s) PRINTED | action(s) PRINTED | ALD | notes |
|---|---|---|---|---|
| TON | NORMAL YL-ZR XFER + ANTIC YL-ZR XFER | YL-ZR TRANSFER SEQUENCER on | 28.15.10.1 | |
| M | NOT ZR MOD | COND YR-ZL TON CKT | 28.15.30.1 | |
| M | — | COND IHW RDY ZR / IHW EX ZR TGR TON CKT | 28.26.11.1 | |
| M | ZR FP CL • NOT ZR MOD, then FP Z ALT TGR OFF | FP RDY ZR • FP RDY ZR IC | 28.20.21.1 • 28.44.28.1 | |
| M | ZR FP CL • NOT ZR MOD, then FP Z ALT TGR OFF • FP CL 2 ZR | COND INSTR CHK ENSLD CKT | 28.41.50.1 | |
| M | — | COND MOD ZR TON CKT | 28.15.20.1 | |
| M | NOT ZR MOD | PREV ZR PREP COMPL | 28.44.25.1 | |
| M | ZR MOD T | BLOCK Y-Z START TGR TON; ZL + ZR PREP NOT BUSY | 28.26.11.1; 28.20.21.1 | |
| M | ¯(ZR WAS IHW) | Y-Z M • MOD REQ | 28.70.42.1 | |
| M | — | TOF YL-ZR E TGR | 28.15.10.1 | |
| E • M | — | GT AOB TO ZR; GT AOB 32 to ZR | 28.15.21.1 • 28.27.57.1; 28.27.51.1 | |
| E | FP CL 2YL • SBC • CD 2Y-ZR | COND ZRFP 1•2•3•4•6 SET• RESET CKTS | 28.26.54.1 | |
| E | — | RESET ZR ADDR 8 TGR; TON YL-ZR M TGR; COND ZR IHW TON CKT; COND ZR FL PT TGR TON CKT; GENERATE SA PULSES; HOLD DATA SELECT PREP | see 1d | |
| E | CD 1Y-ZR | GT 1YL TO ABB | 28.27.53.1 | |
| E | CD 1Y-ZR, ZR IHW BL IF | TON ZR BLOCK 1Y TGR | 28.42.41.1 | |
| E | CD 1Y-ZR, UNCOND + BIT BR + IND BR 1YL | TON ZR SPND TGR | 28.42.43.1 | |
| E | E15 + E16 (MOD REQ from 1YL) | TON ZR MOD R TGR | 28.26.21.1 | |
| E | E24 + E25 (MOD REQ from 2YL) | SET MOD R TGR | 28.26.21.1 | |
| E | ¯(1BIT MOD R) • CD 1Y-ZR | GT 1Y 28-30 TO XAB 1-3 (and GT 1Y31 TO XAB 4) | 28.27.52.1 | |
| E | 1 BIT MOD R • CD 1 Y-ZR | GT 1Y31 TO XAB 4 | 28.27.52.1 | |
| E | same pair for 2Y | GT 2Y 28-30 TO XAB 1-3; GT 2Y 31 TO XAB 4 | 28.27.52.1 | |
| E | CD 2Y-ZR • NOT FP CL 2Y • SBC | TOF FPR CL 1•2•3•4•6 TGR | 28.26.51.1 | |
| E | CD 1Y-ZR | GT 1YL TO ABB COND TAGS ZR | 28.26.10.1 • 28.27.40.1 | |
| E | CD 2Y-ZR | GT 2YL TO ABB COND TAGS ZR | 28.26.10.1, 28.26.40.1 | |
| E | FP CL 1 YL • SBC • CD 1 Y - ZR | COND FP CL R TON CKT; COND ZR FP 1 TON CKTS | 28.26.51.1; 28.26.50.1 | |
| E | NOT FP CL 1 Y • CD 1 Y -ZR • SBC | TOF FPR CL 1•2•3•4•6 TGR | 28.26.51.1 | |
| E | SBC | TOF Y-Z START TGR | 28.26.11.1 | |
| E | CD 1Y-ZR3 | GT 1 YL TO ABB | 28.27.53.1 | |
| E | CD 1Y-ZR3, UNCOND + BIT BRC + IND BR 2YL | BR Y-Z XFER TON ZR SPND 1Y | 28.42.42.1 | |
| E | CD 1Y-ZR3, ZR IHW BL IF | TON ZR BLOCK 2Y TGR | 28.42.41.1 | |
| E | YL-ZR NM (line "E • M̄") | PREP RST X 0-63 | 28.86.57.1 | |
| E | FW NOTS • SBC | TOF YR-ZLM TGR | — | |
| E | FP MOD RDY | TOF MOD ZL M TGR | 28.15.40.1 | |
| E | — | TOF FPL 3M / FPL 4M / VFL 5M TGR; INH NIDC SET IX FR XAC; TOF ZR ICC TGR; COND ZRAD / ZRIF TON • TOF CKTS; TOF ZDS • ZDF TGRS | see 1d | |

##### 4. Counters, timers, triggers, registers named

- Triggers: YL-ZR E TGR, YL-ZR M TGR, YR-ZL M TGR ("YR-ZLM"), IHW RDY ZR TGR, IHW EX ZR TGR,
  FP Z ALT TGR, MOD ZR, ZR MOD R TGR, MOD R TGR, MOD ZL M TGR, Y-Z START TGR, ZR BLOCK 1Y TGR,
  ZR BLOCK 2Y TGR, ZR SPND TGR, ZR SPND 1Y, ZR ADDR 8 TGR, ZRFP 1,2,3,4,6, FPR CL 1-4,6 TGR, ZR FP 1,
  ZR FL PT TGR, ZR IHW, FPL 3M, FPL 4M, VFL 5M TGRS, ZR ICC TGR, ZRAD, ZRIF, ZDS, ZDF TGRS.
- Registers/paths: Y (1Y, 2Y, 1YL, 2YL; bits 28-31), ZR, ZL, AOB (to ZR; "AOB 32"), XAB 1-4, ABB,
  X 0-63, SA (GENERATE SA PULSES), DATA SELECT, XAC (INH NIDC SET IX FR XAC).
- Counters, timers, LAOP codes: none named.

##### 5. TIME

PRINTS NO TIME. Only phase names M, E • M, E and the line label "E • M̄".

##### 6. [KEY] items

- **[KEY]** "Y-Z M • MOD REQ (28.70.42.1)" on ¯(ZR WAS IHW) (28.15.71.1), phase M — the
  modification request raised from the Y-Z transfer.
- **[KEY]** TON ZR MOD R TGR (28.26.21.1) / SET MOD R TGR (28.26.21.1) on the "DEC MOD REQ FR 1YL /
  2YL" hexagons (E15, E16, E24, E25, quoted in full above): index-modification request decided from the
  Y halfword: immediate-index (IMM IX), bits 28-31 of the halfword, BIT BR DEC 1/3, UNCOND + BIT BR,
  YLD BRC, FW NOTS.
- **[KEY]** GT 1Y/2Y 28-30 TO XAB 1-3 and GT 1Y31 / 2Y 31 TO XAB 4 (28.27.52.1), with 1BIT MOD R —
  index address to XAB from the YL half.
- **[KEY]** BLOCK Y-Z START TGR TON (28.26.11.1) and ZL + ZR PREP NOT BUSY (28.20.21.1) on "ZR MOD T" (M).
- **[KEY]** TON ZR BLOCK 1Y TGR / TON ZR BLOCK 2Y TGR (28.42.41.1) on "ZR IHW BL IF" (28.27.30.1) —
  ZR block triggers.
- **[KEY]** TON ZR SPND TGR (28.42.43.1) on UNCOND + BIT BR + IND BR 1YL, and "BR Y-Z XFER TON ZR SPND 1Y"
  (28.42.42.1) on UNCOND + BIT BRC + IND BR 2YL — ZR suspend triggers for branches.
- **[KEY]** INH NIDC SET IX FR XAC (no ALD) at E.
- **[KEY]** PREV ZR PREP COMPL (28.44.25.1) on NOT ZR MOD (M).
- **[KEY]** COND INSTR CHK ENSLD CKT (28.41.50.1) on FP Z ALT TGR OFF • FP CL 2 ZR.
- Not printed: STORE WAIT, LA full, IAUC, LAAR, pseudo-store, houseclean, IC FETCH PRIORITY, updated
  indicator, index recovery.

##### 7. Could not read / uncertain

- M13 "ZR MOD T" (clear print; probably meant ZR MOD R).
- E42 "CD 1Y-ZR3" (clear print, stray mark; it heads a chain that gates "2YL"/"2Y" actions).
- E27 ALD under a smear, read "(28.15.10.1)".
- E58 "ICC" (probably IDC; not corrected).
- E16 vs E24: bars on the halfword bits appear on the 2Y hexagon but not the 1Y one; recorded as seen.
- Exact negation scope of bars that fall between lines (E16, E24).
- E48, E51, E57 print no ALD reference.

#### Figure 3.1.8 — YL-ZL TRANSFER SEQUENCER

- Caption PRINTED: "FIGURE 3.1.8. YL-ZL TRANSFER SEQUENCER"
- PDF page 70, landscape fold-out, box text rotated 90 deg.
- Header PRINTED: "M3-04-3   I UNIT FLOW DIAGRAMS"
- Foot PRINTED: "2/1/62", "1-15/1-16"
- Applicability PRINTED: "CPU 7101 SER. NO. 30,004 AND HIGHER"
- The sequencer bar itself is labelled "YL - ZL SEQUENCER (28.15.70.1)" (caption says TRANSFER SEQUENCER).
- Several boxes in the upper middle are faded; read at 600 dpi with contrast stretch.

Notation as in fig_3.1.6_s3.md.

##### 1. Boxes

###### 1a. TON

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| S1 | hexagon | FULL WD S • SAC • YR - ZR • NOT MOD R + MOD ZR M • ZL MT | (28.15.70.1) |
| S2 | hexagon | FULL WRD S • ACC + COMP • ZL MT ON ACC • YR - ZR • NOT MOD R + MOD Z R M • SAC | (28.15.70.1) |
| S3 | sequencer bar | YL - ZL SEQUENCER | (28.15.70.1) |

S1 YES and S2 YES join (OR) -> "TON" -> S3. Phase lines: M (top), E • M, E.

###### 1b. Phase M

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| M1 | rect | TOF YL - ZL E TGR | (28.15.70.1) |
| M2 | rect | COND MOD ZL TON CKT | (28.15.40.1) |
| M3 | hexagon | NOT MOD L RQ | (28.15.71.1) |
| M4 | rect | COND WBC + DEC TON | (28.15.80.1) |
| M5 | hexagon | ZL MOD R | (28.15.71.1) |
| M6 | rect | BLOCK GEN OF ZL + ZR PREP NOT BUSY | (28.20.21.1) |
| M7 | hexagon | ¯(ZR WAS IHW) (faded; bar faint) | (28.15.71.1) |
| M8 | rect | BLOCK XSF1 E TON (faded; "XSF1" partly legible, last char like "!"/"1") | (28.70.42.1) |

M3 YES -> M4. M5 YES -> node -> M6, and the line continues to M7; M7 YES -> M8 (so M8 is gated
by ZL MOD R and ¯(ZR WAS IHW)).

###### 1c. Phase E • M (boxes above the E • M line)

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| EM1 | rect | GT AOB TO ZL YL | (28.27.57.1) |
| EM2 | rect | GT AOB 32 TO ZL | (28.27.50.1) |
| EM3 | rect | GT AOB TO ZL LI ("LI" as printed, 600 dpi) | (28.15.41.1) |
| EM4 | rect | COND ZL IDC TON TO F CKTS ("TO F" as printed; DERIVED "TOF") | (28.51.03.1) |
| EM5 | rect | COND ZLAD TON • TOF CCTS | printed "(28.15.04.1)" [sic; fig 3.1.6 has 28.51.04.1] |
| EM6 | rect | COND ZL IF TON • TOF CKTS | (28.51.05.1) |
| EM7 | rect | COND ZDS • ZDF TOF CKTS | (28.51.06.1) |
| EM8 | rect | TOF BROK TGR | (28.71.40.1) |
| EM9 | rect | BLOCK GEN OF INH NIDC SET IDC FR XAC | (28.27.31.1) |
| EM10 | rect | Y-ZL + MOD ZR RST ZL TAGS | (28.51.06.1) |
| EM11 | rect | TOF VFL 5 M | (28.11.51.1) |
| EM12 | rect | TOF FPL 4 M | (28.13.41.1) |
| EM13 | rect | TOF FPL 3 M | (28.13.31.1) |
| EM14 | hexagon | SAC • 2YL MOD DEC (a fold line crosses the text) | (28.26.27.1) |
| EM15 | rect | SET MOD L TGR | (28.26.23.1) |
| EM16 | rect | COND ZL MOD R TGR | (28.26.23.1) |
| EM17 | rect | TON YR - ZR M TGR | (28.15.60.1) |
| EM18 | hexagon | SBC | (28.26.58.1) |
| EM19 | rect | TOF FPL CL 1• 2•3•4•6 | (28.26.52.1) |

EM14 YES -> EM15, EM16, EM17 and the same line runs on to the node where EM18 YES enters, then
-> EM19. As drawn EM19 is reached from EM18 (SBC); EM14's line also reaches that node.

###### 1d. Phase E — first E bus (boxes above it)

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| E1 | rect | COND MOD ZR M TOF | printed "'28.15.20.1)" (opening mark) |
| E2 | rect | HOLD DATA SELECT PREP | (28.96.43.1) |
| E3 | rect | XS READ P | (24.00.09.1) |
| E4 | hexagon | CD 1Y - ZL | (28.15.71.1) |
| E5 | rect | GT 1Y 0 - 17 TO ABB | (22.10.09.1) (overprinted) |
| E6 | rect | GT 1Y 18 TO ABB | (22.10.09.1) |
| E7 | rect | GT 1Y 19 - 23 TO ABB | (22.10.09.1) |
| E8 | rect | GT 1Y 24 - 27 TO ABB | (22.10.09.1) |
| E9 | rect | GT 1Y 28 - 31 TO ABB | (22.10.09.1) |
| E10 | rect | NO ADJ P 24 - 27 BYPS SIGN RES | (28.96.44.1) |

E4 YES -> E5..E10.

###### 1e. Phase E — second E bus (reached by a vertical from the first)

Below the bus:

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| E11 | rect | RESET ZL ADDR 8 TGR | (28.27.57.1) |
| E12 | rect | TOF ZLNA ZLXA ZL SA TGRS | (28.51.08.1) |

Above the bus:

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| E13 | rect | TON YL - ZL M TGR | (28.15.70.1) |
| E14 | hexagon | CD 1Y - ZL | (28.15.71.1) |
| E15 | rect | TON CD 2Y - ZR TGR | (28.26.10.1) |
| E16 | rect | GT 1Y 31 TO XAB 4 | (28.27.52.1) |
| E17 | rect | GT 1Y 28 - 30 TO XAB 1 -3 | (28.27.52.1) |
| E18 | rect | INST PREP TON ZL BLOCK 1Y | (28.43.41.1) [as printed; the 2Y box prints 28.42.41.1] |
| E19 | rect | 1Y - ZL E | (28.44.24.1) |
| E20 | hexagon | CD 2Y - ZL | (28.15.71.1) |
| E21 | rect | GT 2Y 31 TO XAB 4 | (28.27.52.1) |
| E22 | rect | GT 2Y 28 - 30 TO XAB 1 - 3 | (28.27.52.1) |
| E23 | rect | TOF CD 2Y - ZR TGR | (28.26.10.1) |
| E24 | rect | INST PREP TON ZL BLOCK 2Y | (28.42.41.1) |
| E25 | rect | 2Y - ZL | (28.44.24.1) |
| E26 | rect | GT 2Y 0 - 17 TO ABB | (22.10.11.1) |
| E27 | rect | GT 2Y 18 TO ABB | (22.10.11.1) |
| E28 | rect | GT 2Y 19 - 23 TO ABB | (22.10.11.1) |
| E29 | rect | GT 2Y 28 - 31 TO ABB | (22.10.11.1) |
| E30 | rect | GT 2Y 24 - 27 TO ABB | (22.10.11.1) |
| E31 | rect | NO ADJ P 24-27 BYDS SIGN RES ("BYDS" here, "BYPS" in E10) | (28.96.44.1) |

E14 YES -> E15..E19. E20 YES -> E21..E31. No 1-bit-modification test is drawn on this sheet:
both GT ..31 TO XAB 4 and GT ..28-30 TO XAB 1-3 hang directly on CD 1Y-ZL / CD 2Y-ZL.

##### 2. Structure

- **YL - ZL SEQUENCER (28.15.70.1)**: TON = S1 + S2. No TOF drawn into the bar; its triggers
  appear as "TOF YL - ZL E TGR" (M1, at M) and "TON YL - ZL M TGR" (E13, at E).
  - M: M1..M8. E • M: EM1..EM19. E: first E bus E1..E10, second E bus E11..E31.

##### 3. Step table

| phase | condition(s) PRINTED | action(s) PRINTED | ALD | notes |
|---|---|---|---|---|
| TON | S1 + S2 (see 1a) | YL - ZL SEQUENCER on | 28.15.70.1 | |
| M | — | TOF YL - ZL E TGR; COND MOD ZL TON CKT | 28.15.70.1; 28.15.40.1 | |
| M | NOT MOD L RQ | COND WBC + DEC TON | 28.15.80.1 | |
| M | ZL MOD R | BLOCK GEN OF ZL + ZR PREP NOT BUSY | 28.20.21.1 | |
| M | ZL MOD R, ¯(ZR WAS IHW) | BLOCK XSF1 E TON | 28.70.42.1 | faded |
| E • M | — | EM1..EM13 | see 1c | |
| E • M | SAC • 2YL MOD DEC | SET MOD L TGR; COND ZL MOD R TGR; TON YR - ZR M TGR | 28.26.23.1; 28.26.23.1; 28.15.60.1 | |
| E • M | SBC | TOF FPL CL 1•2•3•4•6 | 28.26.52.1 | |
| E | — | COND MOD ZR M TOF; HOLD DATA SELECT PREP; XS READ P | 28.15.20.1; 28.96.43.1; 24.00.09.1 | |
| E | CD 1Y - ZL | GT 1Y 0-17 / 18 / 19-23 / 24-27 / 28-31 TO ABB; NO ADJ P 24-27 BYPS SIGN RES | 22.10.09.1; 28.96.44.1 | |
| E | — | TON YL - ZL M TGR; RESET ZL ADDR 8 TGR; TOF ZLNA ZLXA ZL SA TGRS | 28.15.70.1; 28.27.57.1; 28.51.08.1 | |
| E | CD 1Y - ZL | TON CD 2Y - ZR TGR; GT 1Y 31 TO XAB 4; GT 1Y 28-30 TO XAB 1-3; INST PREP TON ZL BLOCK 1Y; 1Y - ZL E | see 1e | |
| E | CD 2Y - ZL | GT 2Y 31 TO XAB 4; GT 2Y 28-30 TO XAB 1-3; TOF CD 2Y - ZR TGR; INST PREP TON ZL BLOCK 2Y; 2Y - ZL; GT 2Y ... TO ABB (5 boxes); NO ADJ P 24-27 BYDS SIGN RES | see 1e | |

##### 4. Counters, timers, triggers, registers named

- Triggers: YL-ZL E TGR, YL-ZL M TGR, MOD ZL, MOD L (SET MOD L TGR), ZL MOD R TGR, YR-ZR M TGR,
  CD 2Y-ZR TGR, XSF1, ZL IDC, ZLAD, ZL IF, ZDS, ZDF, BROK TGR, VFL 5 M, FPL 4 M, FPL 3 M, FPL CL
  1,2,3,4,6, ZLNA, ZLXA, ZL SA TGRS, ZL ADDR 8 TGR, ZL BLOCK 1Y / 2Y, MOD ZR M.
- Registers/paths: Y (1Y, 2Y, YL; bits 0-17, 18, 19-23, 24-27, 28-31), ZL, ZR, AOB, ABB, XAB 1-4,
  XS (XS READ P), XAC, DATA SELECT, ZL TAGS.
- Counters, timers, LAOP codes: none.

##### 5. TIME

PRINTS NO TIME.

##### 6. [KEY] items

- **[KEY]** XS READ P (24.00.09.1) — at phase E, unconditional (index storage read).
- **[KEY]** GT 1Y/2Y 28 - 30 TO XAB 1 - 3 and GT 1Y/2Y 31 TO XAB 4 (28.27.52.1) on CD 1Y-ZL / CD 2Y-ZL.
- **[KEY]** BLOCK GEN OF ZL + ZR PREP NOT BUSY (28.20.21.1) on ZL MOD R (M).
- **[KEY]** BLOCK XSF1 E TON (28.70.42.1) on ZL MOD R • ¯(ZR WAS IHW) (M) (faded).
- **[KEY]** BLOCK GEN OF INH NIDC SET IDC FR XAC (28.27.31.1) at E • M.
- **[KEY]** INST PREP TON ZL BLOCK 1Y (28.43.41.1) / ZL BLOCK 2Y (28.42.41.1) at E.
- **[KEY]** SET MOD L TGR / COND ZL MOD R TGR (28.26.23.1) on SAC • 2YL MOD DEC (28.26.27.1).
- **[KEY]** Y-ZL + MOD ZR RST ZL TAGS (28.51.06.1) at E • M.
- Not printed: STORE WAIT, LA full, IAUC, LAAR, pseudo-store, houseclean, IC FETCH PRIORITY, updated
  indicator, index recovery.

##### 7. Could not read / uncertain

- M8 "BLOCK XSF1 E TON": faded; "XSF1" fourth character uncertain. The matching box on fig 3.1.9
  (same ALD 28.70.42.1) prints clearly "BLOCK YSFI E TON", so the first letter here may be Y.
- M7 overbar faint.
- EM3 "LI", EM4 "TO F", EM5 "CCTS" and its ALD 28.15.04.1: as printed.
- E18 ALD 28.43.41.1 vs E24 28.42.41.1: as printed.
- E10 "BYPS" vs E31 "BYDS": as printed.

#### Figure 3.1.9 — YR-ZR TRANSFER SEQUENCER

- Caption PRINTED: "FIGURE 3.1.9. YR-ZR TRANSFER SEQUENCER"
- PDF page 71, landscape fold-out, box text rotated 90 deg.
- Header PRINTED: "M3-04-3   I UNIT FLOW DIAGRAMS"
- Foot PRINTED: "2/1/62", "1-17/1-18"
- Applicability PRINTED: "CPU 7101 SER. NO. 30,004 AND HIGHER"
- Sequencer bar printed "YR - ZR SEQUENCER (28.15.60.1)".

Notation as in fig_3.1.6_s3.md.

##### 1. Boxes

###### 1a. TON (both hexagons read at 600 dpi)

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| S1 | hexagon | ¯(FW NOT S) • SAC • NOT CHKR SING ERR • ¯(CDY RIGHT) • ¯(ZL IHW) • INSTR WRD CHK COMP • FWS • ¯(FP BLOCK Y-Z) • MOD ZL M + YR - ZL NOT R MOD - ZR MT | (28.15.60.1) |
| S2 | hexagon | SAC • ¯(FW NOT S) • ¯(CD Y RIGHT) • ¯(ZL IHW) • INS WRD CHK COMP • FWS • FP BLOK Y-Z • ACC + COMP • ZR MT ON ACC • MOD ZL M + YR - ZL • NOT R MOD • NOT CHKR SING ERR | (28.15.60.1) |
| S3 | sequencer bar | YR - ZR SEQUENCER | (28.15.60.1) |

S1 YES and S2 YES join (OR) -> "TON" -> S3. S1 bars: a bar over "FW NOT S"; a short bar over the
word "NOT" at the end of line 1 (scope unclear: it sits over "NOT" of "NOT CHKR SING ERR"); bar over
"CDY" and a bar between lines 2/3 spanning "RIGHT • ZL IHW" (read as ¯(CDY RIGHT) • ¯(ZL IHW), as
S2 prints them unambiguously); bar between lines 4/5 over "FP BLOCK Y-Z". S2 prints no bar on
"FP BLOK Y-Z".

###### 1b. Phase M

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| M1 | rect | TOF YR - ZR M TGR | (28.15.60.1) |
| M2 | rect | COND MOD ZR TO N CKT ("TO N" as printed) | (28.15.20.1) |
| M3 | hexagon | NOT ZR MOD F ("F" as printed) | (28.15.61.1) |
| M4 | rect | COND YL - ZL TON CKT | (28.15.70.1) |
| M5 | hexagon | ZR MOD R | (28.15.61.1) |
| M6 | rect | BLOCK GEN OF ZL + ZR PREP NOT BUSY | (28.15.61.1) |
| M7 | hexagon | ZP WAS IHW ("ZP" as printed; no bar visible at 600 dpi) | (28.15.71.1) |
| M8 | rect | BLOCK YSFI E TON | (28.70.42.1) |

M3 YES -> M4. M5 YES -> M6 and on to M7; M7 YES -> M8. (Note: the same pair on fig 3.1.8 prints
¯(ZR WAS IHW) and a faded "BLOCK XSF1 E TON".)

###### 1c. Phase E • M

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| EM1 | rect | GT AOB TO ZR YR | (28.27.57.1) |
| EM2 | rect | GT AOB 32 to ZR | (28.27.51.1) |
| EM3 | rect | GT AOB 18 to ZR | (28.27.51.1) |
| EM4 | rect | GT AOB 19 to ZR | (28.27.51.1) |

###### 1d. Phase E — first E bus (boxes above it)

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| E1 | rect | COND ZRIDC TON • TOF CRT | (28.51.02.1) |
| E2 | rect | COND ZRAD TON • TOF CKT | (28.51.04.1) |
| E3 | rect | COND ZRIF TON • TOF CKT | (28.51.05.1) |
| E4 | rect | COND ZDS • ZDF TOF CKT | (28.51.06.1) |
| E5 | rect | TOF BROK TGR | (28.71.40.1) |
| E6 | hexagon | CD 1Y-ZR | (28.15.61.1) |
| E7 | rect | TOF CD 2Y-ZL TGR | (28.26.10.1) |
| E8 | rect | 1Y - ZR | (28.44.24.1) |
| E9 | rect | GT 1YR TO ABB | (28.27.55.1) |
| E10 | rect | COND BR TGR | (28.27.31.1) |

E6 YES -> E7, E8, E9, E10.

A vertical rises from the first E bus; on it:

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| E11 | hexagon | YR-ZR NM | none printed |
| E12 | rect | PREP RST X 0 - 63 | (28.86.57.1) |
| E13 | hexagon | CD 2Y - ZR | (28.15.51.1 ) |
| E14 | rect | GT 2Y 63 TO XAB 4 | (28.27.52.1) |
| E15 | rect | HOLD DATA PREP | (28.96.43.1) |
| E16 | rect | TOF FW WBC TGR | (28.22.92.1) |
| E17 | rect | TOF Y-Z START TGR | (28.26.11.1) |
| E18 | rect | XS READ P | (24.00.09.1) |
| E19 | hexagon | CD 2Y - ZR | (28.15.61.1) |
| E20 | rect | NO ADJ P 24 - 27 BYPS SIGN RES | (28.96.44.1) |
| E21 | rect | GT 2YR TO ABB | none printed |
| E22 | rect | COND BR TGR | (28.27.31.1) |
| E23 | rect | TOF 2Y - ZR TGR | (28.26.10.1) |
| E24 | rect | 2Y - ZR | (28.27.40.1) |

E11 YES, line labelled "E • M̄" -> E12. E13 YES -> E14..E18 (so XS READ P, TOF Y-Z START TGR,
TOF FW WBC TGR and HOLD DATA PREP are drawn under CD 2Y - ZR (28.15.51.1)). E19 YES -> E20..E24.

###### 1e. Phase E — bottom bus (from the E line)

Below the bus:

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| E25 | rect | RESET ZR ADDR 8 TGR | (28.27.57.1) |

Above the bus:

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| E26 | rect | TON YR - ZR M TGR | (28.15.60.1) |
| E27 | hexagon | SBC • 2YR MOD DEC | (28.26.25.1) |
| E28 | hexagon | 2YR IB MOD D • SBC ("IB" as printed) | (28.26.25.1) |
| E29 | rect | SET MOD R TGR | (28.26.21.1) |
| E30 | rect | COND ZR MOD R TGR | (28.26.21.1) |
| E31 | hexagon | 1YR 4 BIT I FLD + 1Y63 ZERO • CD 1Y-ZR | (28.15.61.1) |
| E32 | rect | GT 1Y 60 - 62 TO XAB 1 - 3 | (28.27.52.1) |
| E33 | hexagon | CD 1Y - ZR | (28.15.61.1) |
| E34 | rect | GT 1Y 63 TO XAB 4 | (28.27.52.1.) (sic, trailing dot) |
| E35 | hexagon | CD 2Y - ZR • 2YR 4 BIT I FLD + 2Y63 ZERO | (28.15.61.1) |
| E36 | rect | GT 2Y 60-62 TO XAB 1 - 3 | (28.27.52.1) |
| E37 | rect | GT 2Y 63 TO XAB 4 | (28.27.52.1) |
| E38 | hexagon | FULL WRD 1Y | (28.26.60.1) |
| E39 | hexagon | FULL WRD 2Y | (28.26.60.1) |
| E40 | rect | TON FULL WDS TGR | (28.26.60.1) |

E27 YES and E28 YES join (OR) -> E29. E30 unconditional. E31 YES -> E32, line continues to E34;
E33 YES joins it above E34. E35 YES -> E36, E37. E38 YES and E39 YES join (OR) -> E40.

A vertical rises from the bottom bus on the right to a bus carrying:

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| E41 | rect | Y-ZR + MOD ZR RST ZR TAGS | (28.51.07.1) |
| E42 | rect | TOF MOD ZL M | (28.15.40.1) |
| E43 | rect | BLOCK GEN OF INH NIDS SET IDC FR XAC ("NIDS" as printed) | (28.27.31.1) |
| E44 | rect | TOF VFL 5 M | (28.11.51.1) |
| E45 | rect | TOF FPR 4 M | (28.14.41.1) |
| E46 | rect | TOF FPR 3 M | (28.14.31.1) |
| E47 | hexagon | SBC | (28.26.58.1) |
| E48 | rect | TOF FPR - CLI TGR ("CLI" as printed) | (28.26.50.1) |
| E49 | rect | TOF FPR CL 2•3•4•6 TGRS, with a printed "*" at lower left of the box | (28.26.51.1) |

E47 YES -> E48, E49. No footnote for "*" found on the sheet.

##### 2. Structure

- **YR - ZR SEQUENCER (28.15.60.1)**: TON = S1 + S2. No TOF drawn into the bar; its triggers are
  named "TOF YR - ZR M TGR" (M1, at M) and "TON YR - ZR M TGR" (E26, at E).
  - M: M1..M8. E • M: EM1..EM4. E: E1..E49 (first E bus, rising vertical, bottom bus, right bus).

##### 3. Step table

| phase | condition(s) PRINTED | action(s) PRINTED | ALD | notes |
|---|---|---|---|---|
| TON | S1 + S2 | YR - ZR SEQUENCER on | 28.15.60.1 | |
| M | — | TOF YR - ZR M TGR; COND MOD ZR TO N CKT | 28.15.60.1; 28.15.20.1 | |
| M | NOT ZR MOD F | COND YL - ZL TON CKT | 28.15.70.1 | |
| M | ZR MOD R | BLOCK GEN OF ZL + ZR PREP NOT BUSY | 28.15.61.1 | |
| M | ZR MOD R, ZP WAS IHW | BLOCK YSFI E TON | 28.70.42.1 | |
| E • M | — | GT AOB TO ZR YR; GT AOB 32 / 18 / 19 to ZR | 28.27.57.1; 28.27.51.1 | |
| E | — | COND ZRIDC / ZRAD / ZRIF TON • TOF; COND ZDS • ZDF TOF CKT; TOF BROK TGR | 28.51.02-06.1; 28.71.40.1 | |
| E | CD 1Y-ZR | TOF CD 2Y-ZL TGR; 1Y - ZR; GT 1YR TO ABB; COND BR TGR | see 1d | |
| E | YR-ZR NM (line "E • M̄") | PREP RST X 0 - 63 | 28.86.57.1 | |
| E | CD 2Y - ZR (28.15.51.1) | GT 2Y 63 TO XAB 4; HOLD DATA PREP; TOF FW WBC TGR; TOF Y-Z START TGR; XS READ P | see 1d | |
| E | CD 2Y - ZR (28.15.61.1) | NO ADJ P 24-27 BYPS SIGN RES; GT 2YR TO ABB; COND BR TGR; TOF 2Y - ZR TGR; 2Y - ZR | see 1d | |
| E | — | TON YR - ZR M TGR; COND ZR MOD R TGR; RESET ZR ADDR 8 TGR | 28.15.60.1; 28.26.21.1; 28.27.57.1 | |
| E | SBC • 2YR MOD DEC + 2YR IB MOD D • SBC | SET MOD R TGR | 28.26.21.1 | |
| E | 1YR 4 BIT I FLD + 1Y63 ZERO • CD 1Y-ZR | GT 1Y 60 - 62 TO XAB 1 - 3 (and GT 1Y 63 TO XAB 4) | 28.27.52.1 | |
| E | CD 1Y - ZR | GT 1Y 63 TO XAB 4 | 28.27.52.1 | |
| E | CD 2Y - ZR • 2YR 4 BIT I FLD + 2Y63 ZERO | GT 2Y 60-62 TO XAB 1 - 3; GT 2Y 63 TO XAB 4 | 28.27.52.1 | |
| E | FULL WRD 1Y + FULL WRD 2Y | TON FULL WDS TGR | 28.26.60.1 | |
| E | — | E41..E46 | see 1e | |
| E | SBC | TOF FPR - CLI TGR; TOF FPR CL 2•3•4•6 TGRS | 28.26.50.1; 28.26.51.1 | |

##### 4. Counters, timers, triggers, registers named

- Triggers: YR-ZR M TGR, MOD ZR, ZR MOD R TGR, MOD R TGR, YSFI, ZRIDC, ZRAD, ZRIF, ZDS, ZDF,
  BROK TGR, CD 2Y-ZL TGR, 2Y-ZR TGR, BR TGR, FW WBC TGR, Y-Z START TGR, ZR ADDR 8 TGR, FULL WDS TGR,
  MOD ZL M, VFL 5 M, FPR 4 M, FPR 3 M, FPR-CL1 TGR, FPR CL 2,3,4,6 TGRS.
- Registers/paths: Y (1Y, 2Y, 1YR, 2YR; bits 24-27, 60-62, 63), ZR, ZL, AOB (to ZR; 18, 19, 32),
  ABB, XAB 1-4, X 0-63, XS (XS READ P), XAC, DATA (HOLD DATA PREP), ZR TAGS.
- Counters, timers, LAOP codes: none.

##### 5. TIME

PRINTS NO TIME.

##### 6. [KEY] items

- **[KEY]** XS READ P (24.00.09.1) at E, under CD 2Y - ZR (28.15.51.1) together with TOF Y-Z START TGR,
  HOLD DATA PREP, TOF FW WBC TGR and GT 2Y 63 TO XAB 4.
- **[KEY]** GT 1Y/2Y 60-62 TO XAB 1-3 on "1YR/2YR 4 BIT I FLD + 1Y63/2Y63 ZERO" and GT 1Y/2Y 63 TO XAB 4
  (28.27.52.1) — index address from the YR half (bits 60-63).
- **[KEY]** SET MOD R TGR (28.26.21.1) on SBC • 2YR MOD DEC + 2YR IB MOD D • SBC (28.26.25.1); COND ZR MOD R TGR.
- **[KEY]** BLOCK GEN OF ZL + ZR PREP NOT BUSY (28.15.61.1) on ZR MOD R; BLOCK YSFI E TON (28.70.42.1) on
  ZR MOD R and ZP WAS IHW (M).
- **[KEY]** BLOCK GEN OF INH NIDS SET IDC FR XAC (28.27.31.1) at E.
- **[KEY]** TON conditions carry NOT CHKR SING ERR, INSTR WRD CHK COMP, FP BLOCK Y-Z / FP BLOK Y-Z
  (barred in S1, unbarred in S2), ZR MT ON ACC.
- Not printed: STORE WAIT, LA full, IAUC, LAAR, pseudo-store, houseclean, IC FETCH PRIORITY, updated
  indicator, index recovery.

##### 7. Could not read / uncertain

- S1: scope of the bar over "NOT" at the end of line 1.
- As printed, meaning unclear: "TO N" (M2), "MOD F" (M3), "ZP" (M7), "YSFI" (M8), "IB" (E28),
  "4 BIT I FLD" (E31, E35), "CLI" (E48), "NIDS" (E43), the "*" in E49.
- E11, E21 print no ALD reference.

#### Figure 3.1.10 — ZR MOD REQ TRIGGER AND MOD ZR SEQUENCER

- Caption PRINTED: "FIGURE 3.1.10. ZR MOD REQ TRIGGER AND MOD ZR SEQUENCER"
- PDF page 72, landscape fold-out, box text rotated 90 deg.
- Header PRINTED: "M3-04-3   I UNIT FLOW DIAGRAMS"
- Foot PRINTED: "2/1/62", "1-19/1-20"
- Applicability PRINTED: "CPU 7101 SER. NO. 30,004 AND HIGHER"
- TON hexagons C and D and the ZR WAS IHW hexagon checked at 600 dpi.

Notation as in fig_3.1.6_s3.md.

##### 1. Boxes

###### 1a. ZR MOD REQ TGR — TON

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| A | hexagon | SET MOD REQ TGR | (28.26.21.1) |
| B | hexagon | SBC • 1YR MOD DEC • YR-ZRE | (28.26.21.1) |
| C | hexagon | SBC • YL-ZRE • 1Y31 • DEC MOD REQ FR 1YL • 1YL BRC • BIT BR DEC + UNCOND + BIT BR CL 1YL (no bars) | (28.26.21.1) |
| D | hexagon | SBC • YL-ZRE • ¯(1YLD BRC) • ¯(UNCOND + BIT BR CL 1YL) + ¯(BIT BR DEC) • DEC MOD REQ FR 1Y • ¯(1Y28) + ¯(1Y29) + ¯(1Y30) + ¯(1Y31) • ¯(IMM IX 1YL) + ¯(NOT FW NOT S) | printed "(28.62.21.1)" [sic; the other three print 28.26.21.1] |
| T | trigger bar | ZR MOD REQ TGR | (28.26.21.1) |

A, B, C, D YES all join (OR) -> "TON" -> T. Line breaks of D as printed: "SBC • YL-ZRE•1YLD / BRC • UNCOND + BIT /
BR CL 1YL + BIT BR DEC • / DEC MOD REQ FR 1Y • / 1Y28 + 1Y29 + 1Y30 + / 1Y31 • IMM IX 1YL + / NOT FW NOT S".
D bars: over "1YLD" (line 1) and over "BRC" and "UNCOND + BIT" (line 2); one bar over all of line 3
"BR CL 1YL + BIT BR DEC"; over each of 1Y28, 1Y29, 1Y30, 1Y31; over "IMM IX 1YL"; over "NOT FW NOT S".
Where the line-2/line-3 bars split between "BR CL 1YL" and "BIT BR DEC" is not certain.

###### 1b. Outputs of ZR MOD REQ TGR (one output bus, no phase lines)

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| R1 | hexagon | ¯(Y-Z START) • MOD ZR NOT M | (28.15.30.1) |
| R2 | rect | BLOCK YR-ZL TON | none printed |
| R3 | hexagon | YL-ZR M • SAC | none printed |
| R4 | hexagon | SAC • YR-ZR M | (28.15.20.1) |
| R5 | label on line | "TON MOD ZR SEQUENCER" | — |
| R6 | hexagon | YR-ZR M | (28.15.61.1) |
| R7 | hexagon | YL-ZR M | (28.15.12.1) |
| R8 | rect | BLOCK Y-Z START TGR TON | (28.26.11.1) |
| R9 | hexagon | ZR WAS IHW (no bar, no YES label printed; 600 dpi) | (28.15.71.1) |
| R10 | rect | Y-Z MOD REQ | (28.70.42.1) |
| R11 | rect | BLOCK YL-ZL TON | (28.15.70.1) |
| R12 | rect | BLOCK IHW RDY TON | (28.26.11.1) |
| R13 | rect | BLOCK GEN OF PREV ZR PREP COMP | (28.27.32.1) |
| R14 | rect | BLOCK IHW EX ZR TGR TON | (28.26.11.1) |

R1 YES -> R2. R3 YES and R4 YES join (OR) -> line labelled "TON MOD ZR SEQUENCER" -> the MOD ZR
SEQUENCER bar. R7 YES -> node R8, line continues; R6 YES joins it below R8; the joined line ->
R9 -> (exit, unlabelled) -> R10. R11..R14 unconditional at the foot of the bus.
(Compare fig 3.1.7, where "Y-Z M • MOD REQ (28.70.42.1)" hangs on ¯(ZR WAS IHW).)

###### 1c. MOD ZR SEQUENCER (28.15.20.1) — phase M

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| M1 | rect | PREV ZR PREP COMP | (28.44.25.1) |
| M2 | rect | COND YR-ZL TON CKT | (28.15.30.1) |
| M3 | hexagon | ZR IHW TGR ON | (28.26.61.1) |
| M4 | rect | COND IHW RDY ZR TON CKT • IHW EX ZR TON CKT | (28.26.11.1) |
| M5 | hexagon | SAC | (28.15.21.1) |
| M6 | rect | TON HW RDY TGR | (28.26.11.1) |
| M7 | rect | TON IHW EX TGR | (28.26.11.1) |
| M8 | hexagon | SAC • ZL MT ON ACC • ACC + COMP • FW S | (28.15.70.1) |
| M9 | rect | TON YL-ZL SEQUENCER | (28.15.70.1) |
| M10 | rect | BLOCK YR-ZL TON CKT | (28.15.30.1) |

A branch from the M line (drawn above it) carries:

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| M11 | rect | TOF MOD ZR E TGR | (28.15.20.1) |
| M12 | hexagon | FW NOT S | (28.15.21.1) |
| M13 | rect | COND WBC + DEC TON CKT | (28.15.80.1) |
| M14 | hexagon | ZR NOT FP CL • FW S + FW NOT S | (28.15.81.1) |
| M15 | rect | ANTIC FW TGR TON | (28.51.24.1) |
| M16 | hexagon | ZR FP CL | (28.51.24.1) |
| M17 | rect | COND MOD ZR M TGR TOF | (28.15.20.1) |
| M18 | rect | INSTR PREP COMP ZR | (28.27.32.1) |

M3 YES -> M4. M5 YES -> M6, M7. M8 YES -> M9, M10. M12 YES -> M13, and the line continues to M14;
M14 YES -> M15. M16 YES -> M17, M18.

###### 1d. Phase E • M

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| EM1 | rect | Y-ZR + MOD ZR COND ZR MA TAGS | (28.51.01.1) |
| EM2 | hexagon | YL FP | (28.15.21.1) |
| EM3 | rect | GT AOB 18 to ZR | (28.27.51.1) |
| EM4 | hexagon | IHW YL + FW S + FW NOT S | (28.15.21.1) |
| EM5 | rect | GT AOB 18 to ZR | (28.27.51.1) |
| EM6 | rect | GT AOB 19 to ZR | (28.27.51.1) |

EM3 hangs at the end of the E • M line, and EM2's YES enters the same node (as drawn, EM3 is not
isolated behind EM2). EM4 hangs on a vertical from the E • M line; EM4 YES -> EM5, EM6.

###### 1e. Phase E

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| E1 | rect | X 0-23 to ABB • X 24-27 to ABB | (28.96.01.1) |
| E2 | rect | RESET ZR ADDR 8 TGR | (28.27.57.1) |
| E3 | hexagon | SBC | (28.15.10.1) |
| E4 | rect | TOF YL-ZR M TGR | (28.15.10.1) |
| E5 | rect | TON MOD ZR M TGR | (28.15.20.1) |
| E6 | rect | HOLD DATA SELECT PREP | (28.96.45.1) |
| E7 | rect | Y-ZR M + MOD ZR RST ZR TAGS | (28.51.07.1) |
| E8 | hexagon | SBC | (28.15.60.1) |
| E9 | rect | TOF YR-ZR M TGR | (28.15.60.1) |
| E10 | hexagon | IHW YL + FW S + FW NOT S | (28.15.21.1) |
| E11 | rect | Z 50 to ABB 18 | (28.96.09.1) |
| E12 | rect | Z 32-49 to ABB 0-17 PREP | (28.96.09.1) |
| E13 | rect | Z 50 to ABB P2 ADJ PAR Z 50-55 | (28.96.08.1) |

E3 YES -> E4. E8 YES -> E9. E10 YES -> E11, E12, E13. Others unconditional.

##### 2. Structure

- **ZR MOD REQ TGR (28.26.21.1)**: TON = A + B + C + D. No TOF on this sheet. Its output bus
  carries R1..R14 with no phase lines; R3 + R4 turn on the MOD ZR SEQUENCER.
- **MOD ZR SEQUENCER (28.15.20.1)**: TON = (YL-ZR M • SAC) + (SAC • YR-ZR M) from the ZR MOD REQ
  TGR bus. Phase lines M, E • M, E. Its triggers are named "TOF MOD ZR E TGR" (M11, at M),
  "COND MOD ZR M TGR TOF" (M17, at M on ZR FP CL) and "TON MOD ZR M TGR" (E5, at E).

##### 3. Step table

| phase | condition(s) PRINTED | action(s) PRINTED | ALD | notes |
|---|---|---|---|---|
| ZR MOD REQ TON | A + B + C + D | ZR MOD REQ TGR on | 28.26.21.1 | |
| ZR MOD REQ | ¯(Y-Z START) • MOD ZR NOT M | BLOCK YR-ZL TON | — | |
| ZR MOD REQ | YL-ZR M • SAC + SAC • YR-ZR M | TON MOD ZR SEQUENCER | — | |
| ZR MOD REQ | YL-ZR M | BLOCK Y-Z START TGR TON | 28.26.11.1 | |
| ZR MOD REQ | (YL-ZR M + YR-ZR M), ZR WAS IHW | Y-Z MOD REQ | 28.70.42.1 | |
| ZR MOD REQ | — | BLOCK YL-ZL TON; BLOCK IHW RDY TON; BLOCK GEN OF PREV ZR PREP COMP; BLOCK IHW EX ZR TGR TON | see 1b | |
| M | — | PREV ZR PREP COMP; COND YR-ZL TON CKT; TOF MOD ZR E TGR | 28.44.25.1; 28.15.30.1; 28.15.20.1 | |
| M | ZR IHW TGR ON | COND IHW RDY ZR TON CKT • IHW EX ZR TON CKT | 28.26.11.1 | |
| M | SAC | TON HW RDY TGR; TON IHW EX TGR | 28.26.11.1 | |
| M | SAC • ZL MT ON ACC • ACC + COMP • FW S | TON YL-ZL SEQUENCER; BLOCK YR-ZL TON CKT | 28.15.70.1; 28.15.30.1 | |
| M | FW NOT S | COND WBC + DEC TON CKT | 28.15.80.1 | |
| M | FW NOT S, then ZR NOT FP CL • FW S + FW NOT S | ANTIC FW TGR TON | 28.51.24.1 | |
| M | ZR FP CL | COND MOD ZR M TGR TOF; INSTR PREP COMP ZR | 28.15.20.1; 28.27.32.1 | |
| E • M | — | Y-ZR + MOD ZR COND ZR MA TAGS; GT AOB 18 to ZR | 28.51.01.1; 28.27.51.1 | YL FP YES also enters |
| E • M | IHW YL + FW S + FW NOT S | GT AOB 18 to ZR; GT AOB 19 to ZR | 28.27.51.1 | |
| E | — | X 0-23 to ABB • X 24-27 to ABB; RESET ZR ADDR 8 TGR; TON MOD ZR M TGR; HOLD DATA SELECT PREP; Y-ZR M + MOD ZR RST ZR TAGS | see 1e | |
| E | SBC (28.15.10.1) | TOF YL-ZR M TGR | 28.15.10.1 | |
| E | SBC (28.15.60.1) | TOF YR-ZR M TGR | 28.15.60.1 | |
| E | IHW YL + FW S + FW NOT S | Z 50 to ABB 18; Z 32-49 to ABB 0-17 PREP; Z 50 to ABB P2 ADJ PAR Z 50-55 | 28.96.09.1; 28.96.08.1 | |

##### 4. Counters, timers, triggers, registers named

- Triggers: ZR MOD REQ TGR (SET MOD REQ TGR), MOD ZR E TGR, MOD ZR M TGR, ZR IHW TGR, HW RDY TGR,
  IHW EX TGR, ANTIC FW TGR, YL-ZR M TGR, YR-ZR M TGR, Y-Z START TGR, ZR ADDR 8 TGR; sequencers
  MOD ZR, YL-ZL (TON), YR-ZL (BLOCK).
- Registers/paths: X (bits 0-23, 24-27) to ABB, Z (bits 32-49, 50, 50-55) to ABB (0-17, 18, P2),
  AOB (18, 19) to ZR, ZR MA TAGS, ZR TAGS, Y (1Y bits 28-31, 1YL, 1YR), DATA SELECT.
- Counters, timers, LAOP codes: none.

##### 5. TIME

PRINTS NO TIME.

##### 6. [KEY] items

- **[KEY]** ZR MOD REQ TGR TON: the four hexagons A-D quoted above (index-modification request from
  1YL / 1YR: DEC MOD REQ FR 1YL, IMM IX 1YL, 1Y28-31, BIT BR DEC, UNCOND + BIT BR CL, 1YLD BRC, FW NOT S).
- **[KEY]** "X 0-23 to ABB • X 24-27 to ABB (28.96.01.1)" at MOD ZR phase E — the index word read out of
  X to the ABB (address modification adder input, DERIVED).
- **[KEY]** "Z 32-49 to ABB 0-17 PREP", "Z 50 to ABB 18", "Z 50 to ABB P2 ADJ PAR Z 50-55" on
  IHW YL + FW S + FW NOT S at E.
- **[KEY]** GT AOB 18 / 19 to ZR at E • M (modified address back to ZR).
- **[KEY]** Y-Z MOD REQ (28.70.42.1) on (YL-ZR M + YR-ZR M) • ZR WAS IHW.
- **[KEY]** BLOCK Y-Z START TGR TON (28.26.11.1) on YL-ZR M; BLOCK YR-ZL TON on ¯(Y-Z START) • MOD ZR NOT M;
  BLOCK YL-ZL TON, BLOCK IHW RDY TON, BLOCK GEN OF PREV ZR PREP COMP, BLOCK IHW EX ZR TGR TON on ZR MOD REQ TGR.
- **[KEY]** ANTIC FW TGR TON (28.51.24.1) on FW NOT S then ZR NOT FP CL • FW S + FW NOT S (M).
- Not printed: STORE WAIT, LA full, IAUC, LAAR, pseudo-store, houseclean, IC FETCH PRIORITY, updated
  indicator, index recovery, XS READ (no XS READ P on this sheet).

##### 7. Could not read / uncertain

- D: ALD printed 28.62.21.1; split of the line-2/3 bars.
- R2, R3 print no ALD reference. R9 has no YES label and no bar.
- EM2/EM3 junction as described.

#### Figure 3.1.11 — ZR BLOCK AND SUSPEND TRIGGERS

- Caption PRINTED: "FIGURE 3.1.11. ZR BLOCK AND SUSPEND TRIGGERS"
- PDF page 73, landscape fold-out, box text rotated 90 deg.
- Header PRINTED: "M3-04-3   I UNIT FLOW DIAGRAMS"
- Foot PRINTED: "2/1/62", "1-21/1-22"
- Applicability PRINTED: "CPU 7101 SER. NO. 30,004 AND HIGHER"
- Four triggers, each a horizontal-in-print bar with a TON line and one output bus; no phase lines.

Notation as in fig_3.1.6_s3.md. "above"/"below" = side of the output bus in page orientation.

##### 1. Boxes

###### 1a. ZR BLOCK 2Y TGR (28.42.41.1)

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| B2-T | hexagon | SBC • INSTR PREP TON ZR BLOCK 2Y | (28.42.41.1) |
| B2 | trigger bar | ZR BLOCK 2Y TGR | (28.42.41.1) |
| B2-1 | rect (below) | BLOCK GEN OF 2Y NOT BUSY | (28.42.12.1) |
| B2-2 | rect (above) | BLOCK GEN OF 2Y NOT BUSY ANTIC ON ACC | (28.42.12.1) |
| B2-3 | rect (below) | BLOCK ESTAB OF IC FTH PRIORITY | (28.42.12.1) |
| B2-4 | rect (above) | BLOCK BRANCH CKT IF2Y TON | (28.41.31.1) |
| B2-5 | rect (below) | BLOCK GEN OF 2Y NOT BUSY ANTIC | none printed |

B2-T YES -> "TON" -> B2. B2-1..B2-5 unconditional on the bus.

###### 1b. ZR SPND 2Y TGR (28.42.43.1)

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| S2-T1 | hexagon | SBC • BR Y-Z XFER TON ZR SPND 2 Y | (28.42.43.1) |
| S2-T2 | hexagon | E1 TON 2Y SPND TGR • SBC | (28.42.43.1) |
| S2-T3 | hexagon | SAR • IWCI E • NO CHKR SING ERR • 1YLD BRU + BRC • ¯(BLOK 1Y BR TON ZR SPND 2Y) • ICOA NE (600 dpi; bar between lines 3/4 across "BLOK 1Y BR TON ZR" and between lines 4/5 over "SPND 2Y") | (28.42.43.1) |
| S2 | trigger bar | ZR SPND 2Y TGR | (28.42.43.1) |
| S2-1 | rect (below) | BLOCK GEN OF IC FTH M • IC FTH MEM | (28.41.21.1) |
| S2-2 | rect (above) | BLOCK IF1YE TON ("IF1YE" as printed on the 2Y bus) | (28.41.21.1) |
| S2-3 | rect (below) | BLOCK ICADV E2 TON | (28.41.41.1) |
| S2-4 | rect (above) | BLOCK ESTAB OF IL FTH PRIORITY ("IL" as printed; DERIVED "IC") | (28.42.12.1) |
| S2-5 | rect (below) | BLOCK GEN OF IF2Y ONE TO MAB 15 | (28.41.32.1) |
| S2-6 | rect (above) | BLOCK IF2Y FTH REQ | (28.41.32.1) |
| S2-7 | rect (below) | BLOCK GEN OF IF2Y GT ICR 0-16 TO MAB | (28.41.32.1) |
| S2-8 | rect (above) | BLOCK IF2Y PNL KEY REQ | (28.41.32.1) |
| S2-9 | rect (below) | BLOCK GEN OF IF2Y GT ICA 0-16 TO MAB | (28.41.32.1) |
| S2-10 | rect (above) | BLOCK IF2Y TOF | (28.41.31.1) |
| S2-11 | rect (below) | BLOCK IF2Y IND TOF | (28.42.32.1) |
| S2-12 | rect (above) | BLOCK IC F02Y TON ("F02Y" as printed) | (28.41.33.1) |
| S2-13 | rect (below) | BLOCK GEN OF IF2Y RETURN ADR | (28.41.32.1) |
| S2-14 | rect (above) | BLOCK ICBC2Y TON | (28.41.33.1) |
| S2-15 | rect (below) | BLOCK GEN OF IC FTH M | (28.41.21.1) |
| S2-16 | rect (above) | BLOCK ICADV E1 TOF | (28.41.41.1) |
| S2-17 | rect (below) | BLOCK GEN OF IC FTH MEM | (28.41.21.1) |
| S2-18 | rect (above) | BLOCK IWC2 TON | (28.41.61.1) |
| S2-19 | hexagon (end of bus) | IF2Y M | (28.41.32.1) |
| S2-20 | rect | COND ICADV E2 TON | (28.41.41.1) |

S2-T1, S2-T2, S2-T3 YES join (OR) -> "TON" -> S2. S2-19 YES -> S2-20; all other boxes unconditional.

###### 1c. ZR BLOCK 1Y TGR (28.42.41.1)

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| B1-T | hexagon | SBC • INSTR PREP TON ZR BLOCK 1Y | none printed |
| B1 | trigger bar | ZR BLOCK 1Y TGR | (28.42.41.1) |
| B1-1 | rect (below) | BLOCK GEN OF 1Y NOT BUSY | (28.42.12.1) |
| B1-2 | rect (above) | BLOCK GEN OF 1Y NOT BUSY ANTIC ON ACC | (28.42.12.1) |
| B1-3 | rect (below) | BLOCK ESTAB OF IC FTH PRIORITY | (28.42.12.1) |
| B1-4 | rect (above) | BLOCK GEN OF I EX USE 1Y | (28.42.12.1) |
| B1-5 | rect (below) | BLOCK GEN OF 1Y NOT BUSY ANTIC | (28.42.12.1) |

B1-T YES -> "TON" -> B1.

###### 1d. ZR SPND TGR 1Y (28.42.42.1)

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| S1-T1 | hexagon | TON SUSPEND TGR • SBC | (28.42.42.1) |
| S1-T2 | hexagon | BR Y-Z YFER TON ZR SPND 1Y • SBC ("YFER" as printed) | (28.42.42.1) |
| S1 | trigger bar | ZR SPND TGR 1Y | (28.42.42.1) |
| S1-1 | rect (below) | BLOCK IF1Y TOF | "(28.41 21.1)" (dot missing) |
| S1-2 | rect (above) | BLOCK GT OF ICR 0-16 TO MAB | (28.41.22.1) |
| S1-3 | rect (below) | BLOCK IF1Y PNL KEY REQ | (28.41.22.1) |
| S1-4 | rect (above) | BLOCK GT OF ICA 0-16 TO MAB | (28.41.22.1) |
| S1-5 | rect (below) | BLOCK IF1Y FTH REQ | (28.41.22.1) |
| S1-6 | rect (above) | BLOCK GEN OF IF1Y RETURN ADR | (28.41.22.1) |
| S1-7 | rect (below) | BLOCK ICFO1Y TON | (28.41.23.1) |
| S1-8 | rect (above) | BLOCK IF1Y IND TOF | (28.41.22.1) |
| S1-9 | rect (below) | BLOCK ICBC1Y TON | (28.41.23.1) |
| S1-10 | rect (above) | COND IF2Y TON CKT | (28.41.22.1) |
| S1-11 | rect (below) | BLOCK IWC1 TON | (28.41.51.1) |
| S1-12 | rect (above) | BLOCK ESTAB OF IC FTH PRIORITY | (28.41.22.1) |
| S1-13 | rect (below, end) | BLOCK GEN OF IF1Y ONE TO MAB 15 | (28.41.22.1) |

S1-T1 YES and S1-T2 YES join (OR) -> "TON" -> S1.

##### 2. Structure

Four triggers, each TON from the hexagons listed, each with one unconditional output bus (except
S2-19). No TOF condition is drawn for any of the four on this sheet. No phase lines.

##### 3. Step table

| trigger | condition(s) PRINTED | action(s) PRINTED | ALD | notes |
|---|---|---|---|---|
| ZR BLOCK 2Y TON | SBC • INSTR PREP TON ZR BLOCK 2Y | ZR BLOCK 2Y TGR on | 28.42.41.1 | |
| ZR BLOCK 2Y on | — | B2-1..B2-5 (block 2Y not busy, block IC FTH priority, block branch ckt IF2Y TON) | 28.42.12.1; 28.41.31.1 | |
| ZR SPND 2Y TON | S2-T1 + S2-T2 + S2-T3 | ZR SPND 2Y TGR on | 28.42.43.1 | |
| ZR SPND 2Y on | — | S2-1..S2-18 (block IC fetch, IF2Y fetch/return/ICR/ICA to MAB, ICADV, IWC2...) | 28.41.x | |
| ZR SPND 2Y on | IF2Y M | COND ICADV E2 TON | 28.41.41.1 | |
| ZR BLOCK 1Y TON | SBC • INSTR PREP TON ZR BLOCK 1Y | ZR BLOCK 1Y TGR on | 28.42.41.1 | |
| ZR BLOCK 1Y on | — | B1-1..B1-5 | 28.42.12.1 | |
| ZR SPND 1Y TON | TON SUSPEND TGR • SBC + BR Y-Z YFER TON ZR SPND 1Y • SBC | ZR SPND TGR 1Y on | 28.42.42.1 | |
| ZR SPND 1Y on | — | S1-1..S1-13 | 28.41.2x.1; 28.41.51.1 | |

##### 4. Counters, timers, triggers, registers named

- Triggers: ZR BLOCK 2Y, ZR SPND 2Y, ZR BLOCK 1Y, ZR SPND 1Y (TGR), SUSPEND TGR, 2Y SPND TGR (E1 TON),
  IF1Y, IF1YE, IF2Y (IND, TOF), ICADV E1/E2, ICFO1Y / IC F02Y, ICBC1Y / ICBC2Y, IWC1, IWC2.
- Registers/paths: ICR 0-16 and ICA 0-16 to MAB, MAB 15 ("ONE TO MAB 15"), RETURN ADR, 1Y, 2Y.
- Counters, timers, LAOP codes: none.

##### 5. TIME

PRINTS NO TIME.

##### 6. [KEY] items (whole sheet is block/suspend)

- **[KEY]** "BLOCK ESTAB OF IC FTH PRIORITY" — on ZR BLOCK 2Y (28.42.12.1), ZR BLOCK 1Y (28.42.12.1),
  ZR SPND 1Y (28.41.22.1); "BLOCK ESTAB OF IL FTH PRIORITY" on ZR SPND 2Y (28.42.12.1). An instruction-
  counter fetch priority is blocked by each of the four triggers.
- **[KEY]** ZR BLOCK 2Y TGR TON: "SBC • INSTR PREP TON ZR BLOCK 2Y (28.42.41.1)"; ZR BLOCK 1Y TGR TON:
  "SBC • INSTR PREP TON ZR BLOCK 1Y".
- **[KEY]** ZR SPND 2Y TGR TON: "SBC • BR Y-Z XFER TON ZR SPND 2 Y" + "E1 TON 2Y SPND TGR • SBC" +
  "SAR • IWCI E • NO CHKR SING ERR • 1YLD BRU + BRC • ¯(BLOK 1Y BR TON ZR SPND 2Y) • ICOA NE" (28.42.43.1).
- **[KEY]** ZR SPND TGR 1Y TON: "TON SUSPEND TGR • SBC" + "BR Y-Z YFER TON ZR SPND 1Y • SBC" (28.42.42.1).
- **[KEY]** Block actions on the suspend buses: BLOCK GEN OF IC FTH M / IC FTH MEM, BLOCK IF1Y/IF2Y FTH REQ,
  BLOCK GT OF ICR / ICA 0-16 TO MAB, BLOCK GEN OF IF1Y/IF2Y ONE TO MAB 15, BLOCK IWC1 / IWC2 TON,
  BLOCK ICADV E1 TOF / E2 TON.
- **[KEY]** "BLOCK GEN OF 1Y/2Y NOT BUSY", "... NOT BUSY ANTIC", "... NOT BUSY ANTIC ON ACC", "BLOCK GEN OF I EX USE 1Y".
- Not printed: STORE WAIT, LA full, IAUC, LAAR, pseudo-store, houseclean, index recovery, updated indicator.

##### 7. Could not read / uncertain

- As printed, meaning unclear: "IWCI E", "ICOA NE", "BRU", "IF1YE" (on the 2Y bus), "IL FTH", "F02Y", "YFER".
- B1-T and B2-5 print no ALD reference; S1-1 ALD missing a dot.

#### Figure 3.1.12 — ZR FP 1 TRIGGER

- Caption PRINTED: "FIGURE 3.1.12. ZR FP 1 TRIGGER"
- PDF page 74, landscape fold-out. Unlike 3.1.6-3.1.11, the box text on this sheet is printed
  UPRIGHT (not rotated).
- Header PRINTED: "M3-04-3   I UNIT FLOW DIAGRAMS"
- Foot PRINTED: "2/1/62", "1-23/1-24"
- Applicability PRINTED: "CPU 7101 SER. NO. 30,004 AND HIGHER"
- Trigger box printed "ZR FP1 TGR (28.26.50.1)" ("FP1" printed with a serif I/1).
- The big TON hexagon was read at 600 dpi.

Notation as in fig_3.1.6_s3.md.

##### 1. Boxes

###### 1a. Top cluster: Z RIGHT FLOATING POINT TGR (separate from ZR FP1 TGR)

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| Z1 | hexagon | FP CL 1YL • CD 1Y-ZR • FWS + HW | (28.26.62.1) |
| Z2 | hexagon | FWS + HW • CD 2Y-ZR • FP CL 2YL | (28.26.62.1) |
| Z3 | hexagon | YL-ZR E | none printed |
| Z4 | label on line | "TON ZR FL PT TGR" | — |
| Z5 | trigger box | Z RIGHT FLOATING POINT TGR | (28.26.62.1) |
| Z6 | rect | BLOCK FP Z ALT TGR TON | (28.27.32.1) |
| Z7 | hexagon | MOD ZR E | (28.15.21.1) |
| Z8 | rect | Z 32-49 to ABB 0-17 PREP | (28.96.09.1) |
| Z9 | rect | HOT 1 TO ABB P2 | (28.96.41.1) |
| Z10 | hexagon | MOD ZR E • MOD ZR M | (28.15.21.1) |
| Z11 | rect | GT AOB 18 TO ZR | (28.27.51.1) |

Z1 YES and Z2 YES join (OR) onto a bus carrying Z3, Z7, Z10. Z3 YES -> line labelled "TON ZR FL PT
TGR" -> Z5 -> Z6. Z7 YES -> Z8, Z9. Z10 YES -> Z11.

###### 1b. ZR FP1 TGR — TON

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| T1 | hexagon | SET ZR FP1 | (28.26.54.1) |
| T2 | hexagon | FP CL 1Y • SBC • CD 1Y ZR • YL ZRE • ¯(1Y21) • 1Y23 • 1Y25 + ¯(1Y25) • ¯(1Y21) • ¯(1Y24) + ¯(1Y21) • 1Y23 • 1Y25 + 1Y22 • 1Y23 • 1Y25 – MULT AND ADD + ¯(1Y24) • ¯(1Y23) + 1Y21 • ¯(1Y22) • 1Y24 • ¯(1Y25) | (28.26.50.1) |
| T | trigger box | ZR FP1 TGR | (28.26.50.1) |

T1 YES and T2 YES join (OR) -> T. T2 line breaks as printed: "FP CL 1Y•SBC• / CD 1Y ZR•YL / ZRE•1Y21•1Y23• /
1Y25+1Y25•1Y21• / 1Y24+1Y21•1Y23• / 1Y25 + 1Y22•1Y23• / 1Y25 – MULT AND / ADD + 1Y24•1Y23 /
+ 1Y21•1Y22•1Y24• / 1Y25". Bars at 600 dpi: under "1Y ZR" on line 2 (= over "1Y21" on line 3); over
the second "1Y25" and the "1Y21" on line 4; under line 4's first "1Y25" (= over "1Y24" line 5); over
"1Y21" line 5; under "MULT AND" on line 7 (= over "1Y24 • 1Y23" line 8); over "1Y22" line 9; over
"1Y25" line 10. The operator before "MULT AND" prints as a dash ("–"), not clearly "+".

###### 1c. ZR FP1 TGR — output bus (one bus, no phase lines; seven drop columns, left to right)

Column 1:

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| C1-1 | rect | BLOCK WBC + DEC TON | (28.15.80.1) |
| C1-2 | hexagon | SAC • ZRXS • ZR INSTR PREP COMP • ZR + ZL PREP NOT BUSY • XOF1 NM | (28.12.11.1) |
| C1-3 | rect | TON XOF1 | (28.12.11.1) |
| C1-4 | hexagon | ZR EQ 1 • ZR INSTR PREP COMP XOF1 E | (28.12.11.1) |
| C1-5 | rect | XOF1 TC FTH | (24.00.09.1) |
| C1-6 | hexagon | ZR 1 + 2 + 3 • IRPT ENBLD | (28.23.70.1) |
| C1-7 | hexagon | ¯(FPR AD INHBT DF) • DS • ¯(IF INHBT DF) • GT FPR IND TO LA | (28.25.30.1) |
| C1-8 | rect | SET LA DF | (33.01.02.1) |
| C1-9 | hexagon | DF MASK EQ1 • INH SET NOP BIT 17 FR DF | (28.25.30.1) |
| C1-10 | rect | DF SET LANOP | (28.25.40.1) |
| C1-11 | hexagon | ZR INSTR PEP COMPLETE • ZR NOT EQ 1 • XOF 1E ("PEP" as printed) | none printed |
| C1-12 | rect | XOF 1 Z45-49 • P TO XAB | (28.86.56.1) |

C1-2 YES -> C1-3. C1-4 YES -> C1-5. C1-6 YES -> C1-7; C1-7 YES -> C1-8 and on to C1-9; C1-9 YES -> C1-10.
C1-11 YES -> C1-12.

Column 2:

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| C2-1 | hexagon | ¯(FPR AD INHBT DF) • DS • IRPT ENBLD • NOT ZR 16-31 • NOT ZR 0-15 | (28.23.61.1) |
| C2-2 | rect | PRE CND LA DF | (28.14.33.1) |
| C2-3 | hexagon | MDF EQ 1 | (28.23.61.1) |
| C2-4 | rect | PRE CND LANOP FR ALARM | (28.14.33.1) |
| C2-5 | hexagon | SAC • XOF 1M • LA EN T1 + 2 • CHKR EN T1 • NOT CHKR SING ERR • ZR INSTR PREP COMP | printed "28.14.41.1" (no parentheses) |
| C2-6 | rect | TON FPR 4 | (28.14.41.1) |

C2-1 YES -> C2-2 and on to C2-3; C2-3 YES -> C2-4. C2-5 YES -> C2-6.

Column 3:

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| C3-1 | hexagon | ZR ADDR 8 | (28.20.08.1) |
| C3-2 | rect | I CHK REQ | (28.27.32.1) |
| C3-3 | rect | BLOCK ZR XS LTH SIGNAL | (28.20.70.1) |
| C3-4 | hexagon | FPR 4E • ZR XS LTH1 | (28.14.42.1) |
| C3-5 | rect | X 0-63 TO XY ICIB | (28.21.61.1) |
| C3-6 | hexagon | FPR 3E | (28.14.32.1) |
| C3-7 | rect | Z 32-49 TO MAB | (28.21.60.1) |
| C3-8 | rect | GT ZROC TO LAOC | (28.21.60.1) |

C3-1 exit (no YES label printed) -> C3-2, C3-3. C3-4 YES -> C3-5. C3-6 YES -> C3-7, C3-8.

Column 4:

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| C4-1 | hexagon | ZR EXT LTH • ZR INSTR PREP COMP | (28.14.31.1) |
| C4-2 | rect | COND FPR3 TON CKT | (28.14.31.1) |
| C4-3 | hexagon | FPR 3 E • NO CANCEL • FPR 3 M • ZR 4 MNT MD | (28.14.33.1) |
| C4-4 | rect | PANEL KEY REQUEST | (28.21.71.1) |
| C4-5 | hexagon | FPR 3 NM | (28.23.50.1) |
| C4-6 | rect | COND FPR 3 TON CKT | (28.14.31.1) |
| C4-7 | hexagon | ZR ADDR 8 LTHD | (28.20.60.1) |
| C4-8 | rect | BLOCK ZR EXT AND ZR XS SIGNALS | (28.20.60.1) |

Each hexagon YES -> the rectangle below it.

Column 5:

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| C5-1 | hexagon | ZR XS LTH | (28.23.60.1) |
| C5-2 | hexagon | FPR 4E • M | (28.14.43.1) |
| C5-3 | rect | TYPE 1 LD TO LA | (28.21.72.1) |
| C5-4 | hexagon | FPR 4E • M | (28.14.42.1) |
| C5-5 | rect | I CHK PARITY | (28.21.75.1) |

C5-1 YES -> a vertical carrying C5-2 and C5-4 (both print the same condition text, different ALD).
C5-2 YES (exit on its left) -> C5-3. C5-4 YES -> C5-5.

Column 6:

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| C6-1 | hexagon | FPR 4E • ZR ADDR 8 LTH | (28.24.82.1) |
| C6-2 | rect | SET LA EXT STORE TAG | (28.24.82.1) |
| C6-3 | rect | SET LA INT STORE TAG | (28.24.82.1) |
| C6-4 | hexagon | FPR 4E • NM • ZR ADDR 8 LTH | (28.14.42.1) |
| C6-5 | rect | I GEN PARITY | (28.44.14.1) |

C6-1 YES -> C6-2, C6-3. C6-4 YES -> C6-5.

Column 7:

| # | shape | text (PRINTED) | ALD |
|---|---|---|---|
| C7-1 | hexagon | ZR INT LTH | (28.23.60.1) |
| C7-2 | rect | COND FPR4E TON | (28.14.41.1) |
| C7-3 | rect | Z32-49 TO MAB | (28.14.42.1) |
| C7-4 | hexagon | FPR4E | (28.24.81.1) |
| C7-5 | rect | SET LA INT FETCH | (36.03.02.1) |
| C7-6 | hexagon | FPR4E • SBC | (28.14.43.1) |
| C7-7 | rect | TYPE 3LD TO LA | (28.21.74.1) |
| C7-8 | hexagon | FPR4E • M | (28.14.43.1) |
| C7-9 | rect | TYPE 3LD TO BCU | (28.21.74.1) |

C7-1 YES (exit on its left) -> a vertical carrying C7-2, C7-3, C7-4, C7-6, C7-8. C7-4 YES -> C7-5.
C7-6 YES -> C7-7. C7-8 exit (no YES label printed) -> C7-9.

##### 2. Structure

- **Z RIGHT FLOATING POINT TGR (28.26.62.1)**: TON from YL-ZR E, gated by Z1 + Z2 (line label
  "TON ZR FL PT TGR"). Output: BLOCK FP Z ALT TGR TON.
- **ZR FP1 TGR (28.26.50.1)**: TON = SET ZR FP1 + T2. No TOF drawn. One output bus with seven
  columns; no phase lines (no E / M on this sheet).

##### 3. Step table

| step | condition(s) PRINTED | action(s) PRINTED | ALD | notes |
|---|---|---|---|---|
| Z bus | (FP CL 1YL • CD 1Y-ZR • FWS + HW) + (FWS + HW • CD 2Y-ZR • FP CL 2YL), then YL-ZR E | TON ZR FL PT TGR -> Z RIGHT FLOATING POINT TGR; BLOCK FP Z ALT TGR TON | 28.26.62.1; 28.27.32.1 | |
| Z bus | ... MOD ZR E | Z 32-49 to ABB 0-17 PREP; HOT 1 TO ABB P2 | 28.96.09.1; 28.96.41.1 | |
| Z bus | ... MOD ZR E • MOD ZR M | GT AOB 18 TO ZR | 28.27.51.1 | |
| TON | SET ZR FP1 + T2 | ZR FP1 TGR on | 28.26.50.1 | |
| FP1 | — | BLOCK WBC + DEC TON | 28.15.80.1 | |
| FP1 | SAC • ZRXS • ZR INSTR PREP COMP • ZR + ZL PREP NOT BUSY • XOF1 NM | TON XOF1 | 28.12.11.1 | |
| FP1 | ZR EQ 1 • ZR INSTR PREP COMP XOF1 E | XOF1 TC FTH | 24.00.09.1 | |
| FP1 | ZR 1 + 2 + 3 • IRPT ENBLD, then ¯(FPR AD INHBT DF) • DS • ¯(IF INHBT DF) • GT FPR IND TO LA | SET LA DF | 33.01.02.1 | |
| FP1 | ... and DF MASK EQ1 • INH SET NOP BIT 17 FR DF | DF SET LANOP | 28.25.40.1 | |
| FP1 | ZR INSTR PEP COMPLETE • ZR NOT EQ 1 • XOF 1E | XOF 1 Z45-49 • P TO XAB | 28.86.56.1 | |
| FP1 | ¯(FPR AD INHBT DF) • DS • IRPT ENBLD • NOT ZR 16-31 • NOT ZR 0-15 | PRE CND LA DF | 28.14.33.1 | |
| FP1 | ... and MDF EQ 1 | PRE CND LANOP FR ALARM | 28.14.33.1 | |
| FP1 | SAC • XOF 1M • LA EN T1 + 2 • CHKR EN T1 • NOT CHKR SING ERR • ZR INSTR PREP COMP | TON FPR 4 | 28.14.41.1 | |
| FP1 | ZR ADDR 8 | I CHK REQ; BLOCK ZR XS LTH SIGNAL | 28.27.32.1; 28.20.70.1 | |
| FP1 | FPR 4E • ZR XS LTH1 | X 0-63 TO XY ICIB | 28.21.61.1 | |
| FP1 | FPR 3E | Z 32-49 TO MAB; GT ZROC TO LAOC | 28.21.60.1 | |
| FP1 | ZR EXT LTH • ZR INSTR PREP COMP | COND FPR3 TON CKT | 28.14.31.1 | |
| FP1 | FPR 3 E • NO CANCEL • FPR 3 M • ZR 4 MNT MD | PANEL KEY REQUEST | 28.21.71.1 | |
| FP1 | FPR 3 NM | COND FPR 3 TON CKT | 28.14.31.1 | |
| FP1 | ZR ADDR 8 LTHD | BLOCK ZR EXT AND ZR XS SIGNALS | 28.20.60.1 | |
| FP1 | ZR XS LTH, FPR 4E • M (28.14.43.1) | TYPE 1 LD TO LA | 28.21.72.1 | |
| FP1 | ZR XS LTH, FPR 4E • M (28.14.42.1) | I CHK PARITY | 28.21.75.1 | |
| FP1 | FPR 4E • ZR ADDR 8 LTH | SET LA EXT STORE TAG; SET LA INT STORE TAG | 28.24.82.1 | |
| FP1 | FPR 4E • NM • ZR ADDR 8 LTH | I GEN PARITY | 28.44.14.1 | |
| FP1 | ZR INT LTH | COND FPR4E TON; Z32-49 TO MAB | 28.14.41.1; 28.14.42.1 | |
| FP1 | ZR INT LTH, FPR4E | SET LA INT FETCH | 36.03.02.1 | |
| FP1 | ZR INT LTH, FPR4E • SBC | TYPE 3LD TO LA | 28.21.74.1 | |
| FP1 | ZR INT LTH, FPR4E • M | TYPE 3LD TO BCU | 28.21.74.1 | |

##### 4. Counters, timers, triggers, registers named

- Triggers: ZR FP1 TGR, Z RIGHT FLOATING POINT TGR (ZR FL PT TGR), FP Z ALT TGR, XOF1 (NM, E, M),
  FPR 3 (E, M, NM), FPR 4 / FPR4E (E, M, NM), MOD ZR E / M, YL-ZR E, MDF, DF.
- Registers/paths: Z (32-49, 45-49) to ABB / MAB / XAB, X 0-63 to XY ICIB, ZROC to LAOC, ABB P2,
  AOB 18 to ZR, LA (DF, NOP bit 17, EXT STORE TAG, INT STORE TAG, INT FETCH), BCU, FPR IND.
- LA operation names: LANOP (PRE CND LANOP FR ALARM; DF SET LANOP), TYPE 1 LD, TYPE 3LD (to LA, to BCU).
- Counters, timers: none.

##### 5. TIME

PRINTS NO TIME. No phase lines, clocks or durations on this sheet.

##### 6. [KEY] items

- **[KEY]** "SET LA EXT STORE TAG (28.24.82.1)" and "SET LA INT STORE TAG (28.24.82.1)" on
  "FPR 4E • ZR ADDR 8 LTH" — store tags set in the look-ahead.
- **[KEY]** "SET LA INT FETCH (36.03.02.1)" on ZR INT LTH, FPR4E.
- **[KEY]** "TYPE 1 LD TO LA (28.21.72.1)" on ZR XS LTH, FPR 4E • M; "TYPE 3LD TO LA (28.21.74.1)" on
  ZR INT LTH, FPR4E • SBC; "TYPE 3LD TO BCU (28.21.74.1)" on ZR INT LTH, FPR4E • M.
- **[KEY]** "X 0-63 TO XY ICIB (28.21.61.1)" on FPR 4E • ZR XS LTH1 — index word X 0-63 out.
- **[KEY]** "BLOCK ZR XS LTH SIGNAL (28.20.70.1)" on ZR ADDR 8; "BLOCK ZR EXT AND ZR XS SIGNALS
  (28.20.60.1)" on ZR ADDR 8 LTHD.
- **[KEY]** "SET LA DF (33.01.02.1)", "DF SET LANOP (28.25.40.1)", "PRE CND LA DF", "PRE CND LANOP FR
  ALARM (28.14.33.1)", conditions "FPR AD INHBT DF", "IF INHBT DF", "DF MASK EQ1 • INH SET NOP BIT 17 FR DF",
  "MDF EQ 1", "IRPT ENBLD" — data-flag/interrupt conditions written into the look-ahead.
- **[KEY]** "SAC • XOF 1M • LA EN T1 + 2 • CHKR EN T1 • NOT CHKR SING ERR • ZR INSTR PREP COMP" -> TON FPR 4.
- **[KEY]** "PANEL KEY REQUEST (28.21.71.1)" on FPR 3 E • NO CANCEL • FPR 3 M • ZR 4 MNT MD.
- **[KEY]** "GT ZROC TO LAOC (28.21.60.1)" and "Z 32-49 TO MAB" on FPR 3E.
- **[KEY]** "XOF1 TC FTH (24.00.09.1)" (same ALD page as XS READ P on figs 3.1.6/3.1.8/3.1.9).
- Not printed: STORE WAIT, LA full, IAUC, LAAR, pseudo-store, houseclean, IC FETCH PRIORITY, updated
  indicator, index recovery.

##### 7. Could not read / uncertain

- T2: operator before "MULT AND" prints as "–"; bars at line breaks as described.
- "PEP" (C1-11, probably PREP), "TC FTH" (C1-5), "LTH1" (C3-4) as printed.
- C5-2 and C5-4 print identical condition text "FPR 4E • M" with different ALD pages.
- Z3, C1-11 print no ALD; C2-5 prints its ALD without parentheses. C3-1 and C7-8 exits have no YES label.

### Appendix B. Figs 3.1.13-3.1.17 (reader B)

#### Fig 3.1.13 sheet 1 of 3 -- ZR FP TRIGGERS 2, 3, 4, AND 6

- Caption (PRINTED): "FIGURE 3.1.13. ZR FP TRIGGERS 2, 3, 4, AND 6 (SHEET 1 OF 3)"
- PDF page 75; printed page "1-25"; issue date "2/1/62"; running head "M3-04-3   I UNIT FLOW DIAGRAMS".
- No "CPU 7101 SER. NO." note. Portrait-size drawing on the left half of a fold-out-width scan; text upright.
- Read from 600 dpi crops.

Notation: `~X` = overbar (NOT). `·` = AND, `+` = OR, as printed.

##### 1. Boxes (PRINTED)

###### Trigger: ZR FP 2 TGR (28.26.51.1)
TON from either (lines join at a merge arrow above "TON"):
- hexagon "SET 7R FP 2" (no ALD printed), YES. ("7R" as printed; DERIVED: ZR)
- hexagon "1Y21 · 1Y22 · ~1Y23 · 1Y24 · ~1Y25 + 1Y23 (1Y25 + ~1Y24) · 1Y21 · 1Y22 · COND FP CL R" (28.26.51.1), YES.
  Overbars read on line-2 "1Y23", line-3 "1Y25" and line-4 "1Y24". (A bar under line-1 "1Y21" is
  read as the overbar of line-2 "1Y23".) DERIVED: decodes the 1Y21-25 opcode bits to an FP class.
No TOF on this sheet.

###### Bus under ZR FP 2 TGR
Upper row:
| # | condition (YES exit) | action(s) |
|---|---|---|
| 1 | "INSTR PREP COMP ZL · FP Z ALT TGR OFF" (28.27.32.1) | -> condition 2 |
| 2 | "NO T2 CHKR REQ E· NO I CHKR REQ· NO T1 CHKR REQ· OK TO I CHK IC· NO I CHKR REQ E3" (28.41.50.1) | "COND IWC1 TON CKT" (28.41.51.1); "COND IWC2 TON CKT" (28.41.61.1) |
| 3 | "BLOCK FP RDY· ZR INSTR PREP COMPL· ~CANCEL FPL3E" (28.14.41.1) (overbar over "CANCEL FPL3E") | -> condition 4 |
| 4 | "SAC· FPL 3NE· I CHKR EN· NOT CHKR SING ERR· LA EN T 1 & 2" (28.14.41.1) | "TON FPR 4" (28.14.41.1) |

Lower row (second bus off the same TGR line):
| # | condition | action(s) |
|---|---|---|
| 5 | "FPR 4" (28.14.42.1) | "ICIB P POS 2-8 · Z 32-40 TO ICIB" (28.21.20.1) (28.21.61.1); "BLOCK GEN OF ERR PRECND LA AD" (28.38.70.1) |
| 6 | "FPR 4E · NM" (28.14.42.1) (small mark over the F, see Illegible) | "FPR 4 I CHK PARITY" (28.21.75.1) |
| 7 | "FPR 4 E · SBC" (28.14.43.1) | "FPR 4 E · M TYPE 1 LD" (28.21.72.1) |
| 8 | "FPR 4E · FPR 4M" (28.14.43.1) (small mark over the F) | same "FPR 4 E · M TYPE 1 LD" (28.21.72.1) (7 and 8 YES lines join) |

##### 2. Structure
No sequencer bar or E / E·M / M phase lines are drawn. Phase names appear only inside conditions:
FPL3E, FPL 3NE, FPR 4, FPR 4E, NM, FPR 4M, E3, T1/T2. ("FPL" here vs "FPR" elsewhere as printed.)

##### 3. Step table
| step | condition (PRINTED) | action (PRINTED) | ALD | notes |
|---|---|---|---|---|
| set FP2 | SET 7R FP 2, or the 1Y21-25 decode . COND FP CL R | TON ZR FP 2 TGR | 28.26.51.1 | |
| checker | INSTR PREP COMP ZL · FP Z ALT TGR OFF, then NO T2 CHKR REQ E · NO I CHKR REQ · NO T1 CHKR REQ · OK TO I CHK IC · NO I CHKR REQ E3 | COND IWC1 TON CKT; COND IWC2 TON CKT | 28.27.32.1, 28.41.50/51/61.1 | |
| start FPR4 | BLOCK FP RDY · ZR INSTR PREP COMPL · ~CANCEL FPL3E, then SAC · FPL 3NE · I CHKR EN · NOT CHKR SING ERR · LA EN T 1 & 2 | TON FPR 4 | 28.14.41.1 | |
| FPR4 | FPR 4 | ICIB P POS 2-8 · Z 32-40 TO ICIB; BLOCK GEN OF ERR PRECND LA AD | 28.14.42.1 | |
| FPR4E NM | FPR 4E · NM | FPR 4 I CHK PARITY | 28.21.75.1 | |
| FPR4E M | FPR 4 E · SBC, or FPR 4E · FPR 4M | FPR 4 E · M TYPE 1 LD | 28.21.72.1 | |

##### 4. Named items
- Triggers / sequencers: ZR FP 2 TGR, FP Z ALT TGR, FPR 4 (TON), FPL3E / FPL 3NE, IWC1, IWC2 (TON CKT).
- Registers: ZL, ZR, Z 32-40, ICIB (P POS 2-8), LA (EN T 1 & 2; PRECND LA AD), 1Y21-1Y25.
- Checker terms: T1 / T2 / I CHKR REQ, I CHKR REQ E3, OK TO I CHK IC, I CHKR EN, CHKR SING ERR.
- Others: SAC, SBC, BLOCK FP RDY, CANCEL, TYPE 1 LD.
- No counter, no timer, no LAOP code.

##### 5. TIME
PRINTS NO TIME.

##### 6. [KEY]
None of STORE WAIT, pseudo-store, recovery, houseclean, forwarding, LAAR, store-address compare, priority or block/suspend appears on this sheet.
(Closest: "BLOCK FP RDY" in condition 3 and "BLOCK GEN OF ERR PRECND LA AD" -- not the ZL BLOCK trigger.)

##### 7. Could not read / uncertain
- Conditions 6 and 8: a short mark above the "F" of "FPR 4E"; could be a partial overbar (NOT FPR 4E) or a print blemish. Not resolved.
- Top hexagon reads "SET 7R FP 2"; "7R" taken as printed (probably ZR). No ALD under it.
- Overbar placement in the 1Y decode hexagon is read as above; the line-1/line-2 bar could alternatively be an underline of "1Y21".

#### Fig 3.1.13 sheet 2 of 3 -- ZR FP TRIGGERS 2, 3, 4, AND 6

- Caption (PRINTED): "FIGURE 3.1.13. ZR FP TRIGGERS 2, 3, 4, AND 6 (SHEET 2 OF 3)"
- PDF page 76; printed page "1-26"; issue date "2/1/62"; running head "I UNIT FLOW DIAGRAMS   M3-04-3".
- No "CPU 7101 SER. NO." note. Portrait drawing on the left half of the scan; text upright. Read at 600 dpi (one label at 1200 dpi).

Notation: `~X` = overbar (NOT); `.` = AND, `+` = OR, as printed.

##### 1. Trigger: ZR FP 3 TGR
- Box "TON ZR FP 3 TGR" (28.26.51.1), fed by two lines from:
  - hexagon "1Y NOT 23. 1Y 24• 1Y25• COND FP CLR" (28.26.51.1)
  - hexagon "SET ZR FP 3" (28.26.51.1)
- No TOF on this sheet.

##### 2. Every box (PRINTED), by branch off the ZR FP 3 TGR bus

###### Left down-line
| # | condition (YES exit; YES label sometimes not printed) | action(s) |
|---|---|---|
| L0 | (unconditional) | "COND FPR4E TON" (28.14.41.1) |
| L1 | "FPR 4E" (28.14.42.1) | "Z32-49 TO MAB" (28.21.60.1) |
| L2 | "FPR4E.M" (28.14.43.1) | "TYPE 3LD TO BCU" (28.21.74.1) |
| L3 | "FPR 4E. SBC" (28.14.43.1) | "TYPE 3LD TO LA" (28.21.74.1) |
| L4 | "ZR 1+~2+3 - IRPT ENABLED" (28.23.70.1) (a bar over the "2", possibly over "1+2"; see Illegible) | "PRE CND LA DS" (28.25.20.1) |
| L5 | "ZR EQ1" (28.23.70.1) | "PRE CND LA AD" (28.25.20.1) |

###### Centre down-line
| # | condition | action(s) |
|---|---|---|
| C1 | "~FPR AD INHIB ~DF DS. IRPT ENABLED. NOT ZR 0-31" (28.23.61.1) (overbars over line 1 and over "DF DS") | "PRE CND LA DS" (28.14.33.1) |
| C2 | "ZR EXT LTH. FPR4E" (28.24.82.1) | "SET LA EXT STORE TAG" (36.09.14.1) |
| C3 | "ZR INT LTH. FPR 4E" (28.24.82.1) | "SET LA INT STORE TAG" (36.09.15.1) |

###### Right branch  **[KEY]**
| # | condition | action(s) |
|---|---|---|
| R0 | "FPR 4E" (28.14.43.1); YES exits LEFT and drops down a vertical line feeding R1-R3 | -- |
| R1 | "ZOAR EQ 11+12+16-31" (no ALD printed under it) | "TON STORE WAIT TGR" (28.42.51.1) (printed "TON STORE -WAIT TGR" with a stray dash); "TON IRCY REQ TGR" (28.42.72.1) |
| R2 | "PROGRAM STORE COMPARE" (28.42.72.1) | "TON IRCY REQ TGR" (28.42.72.1) |
| R3 | "PROGRAM STORE COMPARE" (28.42.71.1) | "TON PIRCY TRG" (28.42.71.1) (printed "TRG") |

##### 3. Structure / phases
No sequencer bar, no E / E.M / M phase lines. Phase names appear inside conditions only (FPR4E, FPR4E.M, M, SBC).

##### 4. Step table
| step | condition (PRINTED) | action (PRINTED) | ALD | notes |
|---|---|---|---|---|
| set FP3 | 1Y NOT 23. 1Y 24• 1Y25• COND FP CLR, or SET ZR FP 3 | TON ZR FP 3 TGR | 28.26.51.1 | |
| store-wait test | FPR 4E, then ZOAR EQ 11+12+16-31 | TON STORE WAIT TGR; TON IRCY REQ TGR | 28.14.43.1; 28.42.51.1; 28.42.72.1 | [KEY] |
| program store compare | FPR 4E, then PROGRAM STORE COMPARE | TON IRCY REQ TGR | 28.42.72.1 | [KEY] |
| program store compare | FPR 4E, then PROGRAM STORE COMPARE | TON PIRCY TRG | 28.42.71.1 | [KEY] |
| store tags | ZR EXT LTH. FPR4E / ZR INT LTH. FPR 4E | SET LA EXT / INT STORE TAG | 36.09.14.1 / 36.09.15.1 | |

##### 5. Named items
- Triggers: ZR FP 3 TGR, FPR4E (COND ... TON), STORE WAIT TGR, IRCY REQ TGR, PIRCY TRG/TGR.
- Registers / fields: ZR (EXT, INT, 0-31, 1+2+3, EQ1), ZOAR, Z32-49, MAB, LA (DS, AD, EXT/INT STORE TAG), BCU, 1Y23-1Y25.
- Others: SBC, IRPT ENABLED, FPR AD INHIB, TYPE 3 LD.
- No counter, timer or LAOP code.

##### 6. TIME
PRINTS NO TIME.

##### 7. [KEY] items (verbatim)
- "FPR 4E" (28.14.43.1) -> "ZOAR EQ 11+12+16-31" -> "TON STORE -WAIT TGR" (28.42.51.1), "TON IRCY REQ TGR" (28.42.72.1)
- "PROGRAM STORE COMPARE" (28.42.72.1) -> "TON IRCY REQ TGR" (28.42.72.1)
- "PROGRAM STORE COMPARE" (28.42.71.1) -> "TON PIRCY TRG" (28.42.71.1)
- "SET LA EXT STORE TAG" (36.09.14.1), "SET LA INT STORE TAG" (36.09.15.1), "TYPE 3LD TO BCU" (28.21.74.1)
- Nothing on this sheet turns STORE WAIT off; no XS read, no block/suspend, no IHW, no priority test.
- This sheet repeats, under ZR FP 3, the same FPR4E -> ZOAR / PROGRAM STORE COMPARE group as sheet 3 (ZR FP4). So the STORE WAIT test is drawn for at least the FP3 and FP4 trigger paths.

##### 8. Could not read / uncertain
- L4 "ZR 1+~2+3": a short bar sits over the "2" (1200 dpi); the "1" has a flat top serif. Whether this is an overbar (NOT 2) or a blemish is unresolved. Sheet 3's analogous box reads "ZR 1 + 2 + 3. 1RPT ENABLED" with no bar.
- R1 has no ALD number printed (sheet 3 gives 28.42.51.1 for the same box).

#### Fig 3.1.13 sheet 3 of 3 -- ZR FP TRIGGERS 2, 3, 4, AND 6

- Caption (PRINTED): "FIGURE 3.1.13. ZR FP TRIGGERS 2, 3, 4, AND 6 (SHEET 3 OF 3)"
- PDF page 77; printed page "1-27/1-28"; issue date "2/1/62"; running head "M3-04-3   I UNIT FLOW DIAGRAMS".
- No "CPU 7101 SER. NO." applicability note on the sheet.
- Orientation: box text on this sheet is UPRIGHT (not rotated) in the 300 dpi render.
- Read from 300 dpi tiles, overbars checked at 600 dpi.
- A vertical smear (scan defect) runs down near x~2500 px (300 dpi); it clips the left edge of the two
  "ZR INSTR PREP COMPL..." hexagons (see Illegible).

Notation: `~X` = X printed with an overbar (NOT). `.` = AND as printed, `+` = OR as printed.

##### 1. Triggers on this sheet (PRINTED)

###### ZR FP6 TGR (28.26.51.1)
- TON inputs (two lines merging into "TON" arrow):
  - hexagon "1YNOT22 . 1Y21.1Y23. 1Y24.1Y25. COND FP CLR" (28.26.51.1)
  - rectangle "SET ZR FP6 TGR" (28.26.51.1)
- No TOF shown on this sheet.

###### ZR FP4 TGR (28.26.51.1)
- TON inputs:
  - hexagon "~1Y21. ~1Y23 .1Y24-1Y NOT 25. COND FP CL" (28.26.51.1) (overbars over 1Y21 and over 1Y23, checked at 600 dpi)
  - rectangle "SET ZRFP4" (28.26.51.1)
- No TOF shown on this sheet.

###### Join box: rectangle "ZR FP4 OR ZR FP6" (28.23.50.1), exit labelled "YES"
- Fed by both the ZR FP6 bus (from the left) and the ZR FP4 bus (from the right).

##### 2. Every box, by branch (PRINTED; structure DERIVED from the drawn lines)

###### A. ZR FP6 TGR, left bus (column at far left)
| # | condition (hexagon, YES exit) | action(s) on YES |
|---|---|---|
| A1 | "FPR4E" (28.24.82.1) | "SET LA EXT STORE TAG" (28.24.82.1) |
| A2 | "FPR4E" (28.14.42.1) | "SET ADR 13 ON MAB" (28.21.10.1) |
| A3 | "ZR EXT LTH. ZR INSTR PREP COMPLETE. ~FPDD ~M .LAAR 1 BUSY" (28.10.11.1) | "COND FPDD E TGR" (28.10.11.1) |
| A4 | "1RPT ENABLED .ZR1 + 2 + 3" (28.23.70.1) | "CONDITION LA NOP FR DF" (28.25.30.1) |
| A4' | (rectangle, no input line drawn) "CONDITION LA DF TAG" (28.25.30.1) | its output line joins A4's YES line into "CONDITION LA NOP FR DF" (28.25.30.1) |
| A5 | "FPR3E AND NO CANCEL. SBC" (28.14.33.1) | "TYPE 3 LD TO LA" (28.21.74.1) |
| A6 | "FPR3E AND NO CANCEL. FPR3M" (28.14.33.1) | same "TYPE 3 LD TO LA" (28.21.74.1) (A5 and A6 YES lines join) |

###### B. ZR FP6 TGR, centre down-line
| # | condition | action(s) on YES |
|---|---|---|
| B1 | "ZR NE LTH" (28.23.60.1); YES exits left and feeds B2, B3 | -- |
| B2 | "FPR4E M" (28.14.43.1) | "TYPE 3 LOAD TO LA" (28.21.74.1); "T3 LD TC BCU WAIT FOR ACCEPT" (28.21.74.1) |
| B3 | "ZR INSTR PREP COMPLETE" (28.14.41.1) (on B1 YES path, below B2) | "COND FPR4E TON" (28.14.41.1) |

###### C. ZR FP6 TGR, right bus
| # | condition | action(s) on YES |
|---|---|---|
| C1 | "~FPR AD INHIB ~DF OR DS. NOT ZR 0-31. 1RPT ENABLED" (28.23.61.1) (both first lines overbarred, 600 dpi) | "PRE CND LA DF" (28.14.33.1); line continues to C2 |
| C2 | "MDF EQ 1" (28.23.61.1) | "FPR3 PRE CND LA NOP FR ALARM" (28.14.33.1) |

###### D. Under "ZR FP4 OR ZR FP6" YES (four sub-columns, left to right)
Sub-column D-a:
| # | condition | action(s) on YES |
|---|---|---|
| Da0 | (unconditional) | "COND XOF 1E TON" (28.12.11.1) |
| Da1 | "ZR ADR 8 LTH" (28.20.60.1) | "BLOCK ZR EXT AND ZR EXT" (28.20.60.1) |
| Da2 | "FPR 3 NM" (28.23.50.1) | "COND FPR 3 E TON" (28.14.31.1) |
| Da3 | "FPR3E" (printed "24.14.32.1"; probably 28.14.32.1 -- DERIVED) | "Z32-49 TO MAB" (28.21.60.1); "GATE ZROC TO LAOC" (28.21.60.1) |
| Da4 | "FPR3E AND NO CANCEL. ZR4 MNT MD. FPR3M" (28.14.33.1) | "PANEL KEY REQUEST" (28.14.33.1) |
| Da5 | "FPR3E" (28.24.82.1) | "SET LA EXT STORE TAG" (36.09.14.1) |

Sub-column D-b:
| # | condition | action(s) on YES |
|---|---|---|
| Db1 | "FPR3E AND NO CANCEL. SBC" (printed "21.14.33.1"; probably 28.14.33.1 -- DERIVED) | "MODIFIED TYPE 3 LD TO LA" (28.21.75.1) |
| Db2 | "FPR3E AND NO CANCEL. FPR3M" (28.14.33.1) | "XFER AND RESET NIDC" (28.21.73.1) |
| Db3 | "ZR ADDR 8" (28.20.08.1) | "I CHR REQ ZR" (28.27.32.1) |
| Db4 | "FPR4E" (28.24.80.1) | "SET LAOC 6, 8 & 9" (28.24.24.1 / 28.24.26.1); "SET LAOP TAG" (36.05.01.1) |
| Db5 | "ZR INSTR PREP COMPLETE. ZR NOT EQ1. XOF 1E" (28.12.12.1) | "Z45-49. P TO XAB" (28.86.56.1) |
| Db6 | "[ZR] INSTR PREP COMPL. [XO]F 1M+ ADR 8 LTH. [~]CHKR EN T1. LA EN T1+2 [A]ND CHKR SINGLE ERROR" (28.14.21.1) (bracketed chars under smear) | "TON FPR2E" (28.14.21.1) |
| Db7 | "[Z]R INSTR PREP COMPL [.] ZR INT LTH. [L]A EN T3. ~FPR3E LTH [.] SAC" (28.14.21.1) (overbar over "FPR3E LTH"; bracketed chars under smear) | same "TON FPR2E" (28.14.21.1) (Db6 and Db7 YES lines join) |

Sub-column D-c:
| # | condition | action(s) on YES |
|---|---|---|
| Dc0 | (unconditional) | "BLOCK TYPE 2 LOAD" (28.14.31.1) |
| Dc1 | "ZR ADR 8 .LTH. FPR 2 E . NM" (28.14.22.1) | "I GEN PARITY" (28.20.08.1) |
| Dc2 | "FPR4E" (28.14.42.1) | "BLOCK XFER OF ZROC TO LAOC" (28.21.60.1) |

Sub-column D-d:
| # | condition | action(s) on YES |
|---|---|---|
| Dd1 | "ZR ADR 8 LTH. FPR2E" (28.24.82.1) | "SET LA EXT STORE TAG" (28.24.82.1); "SET LA INT STORE TAG" (28.24.82.1) |
| Dd2 | "ZR INSTR PREP COMPLETE. ZREQ1 . XOF 1E" (28.12.12.1) | "XOF 1E TC FETCH" (24.00.09.1) |
| Dd3 | "FPR3E" (28.14.32.1) | "Z32-49 TO MAB" (28.14.32.1); "GT ZROC TO LAOC" (28.21.60.1) |

###### E. ZR FP4 TGR, main down-line (below the TGR)
| # | condition | action(s) on YES |
|---|---|---|
| E1 | "FPR3E AND NO CANCEL. FPR3M" (28.14.33.1) | "TYPE 3 LOAD TO LA" (28.21.74.1); "T3 LD TO BCU WAIT FOR ACCEPT" (28.21.74.1) |
| E2 | "FPR3E AND NO CANCEL . SBC" (28.14.33.1) | same two boxes as E1 (YES lines join) |
| E3 | "ZR EQ 1" (28.23.70.1) | "FPR PRE COND LA AD TO IND XFER CKTS" (28.25.20.1); "FPR AD INHIB DF AND DS" (28.23.70.1); "FPR PRE COND LA DS TO IND XFER CKTS" (28.25.20.1) |
| E4 | "ZR NE LTH" (28.23.60.1); YES goes up-right to bus G | -- |
| E5 | "FPR4E" (28.14.43.1) (parallel branch off the same down-line, left of E4); YES goes to bus H | -- |

###### F. ZR FP4 TGR, right bus (top right)
| # | condition | action(s) on YES |
|---|---|---|
| F1 | "ZR ADR 8 LTH + ZR INT LTH. FPR4E" (28.24.82.1) | "SET LA INT STORE TAG" (36.09.15.1) |
| F2 | (unconditional) | "BLOCK FPR3 COND LA DF" (28.14.33.1) |
| F3 | "FPR3E AND NO CANCEL" (28.14.33.1) -> F4 | |
| F4 | "PROGRAM STORE COMPARE. ACCEPT OR COMPARE" (28.42.72.1) | "TON 1RCY REQ TGR" (28.42.72.1) **[KEY]** |
| F5 | "ZR 1 + 2 + 3. 1RPT ENABLED" (28.23.70.1) | "PRE CND LA DS" (28.25.20.1) |
| F6 | "1RPT ENABLED .NOT ZRO-15" (28.23.61.1) | "FPR3 PRE COND LA DS" (28.23.61.1); "FPR3 PRE COND LA NOP FR ALARM" (28.23.61.1) |

###### G. Bus fed by E4 "ZR NE LTH" YES
| # | condition | action(s) on YES |
|---|---|---|
| G1 | "FPR4E" (28.14.42.1) | "Z32-49 TO MAB" (28.21.60.1) |
| G2 | "ZR INSTR PREP COMPLETE" (28.14.41.1) | "COND FPR4E TON" (28.14.41.1) |
| G3 | "FPR4 E . M" (28.14.43.1) | "TYPE 3 LOAD TO LA" (28.21.74.1); "T3 LD TO BCU WAIT FOR ACCEPT" (28.21.74.1) |
| G4 | "FPR4E . SBC" (28.14.43.1) | joins G3's YES line (same two actions) |

###### H. Bus fed by E5 "FPR4E" (28.14.43.1) YES  **[KEY]**
| # | condition | action(s) on YES |
|---|---|---|
| H1 | "ZOAR EQ 11 +12 + 16 - 31" (28.42.51.1) | "TON STORE WAIT TGR" (28.42.51.1); "TON IRCY REQ TGR" (28.42.72.1) |
| H2 | "PROGRAM STORE COMPARE" (28.42.72.1) | "TON IRCY REQ TGR" (28.42.72.1) |
| H3 | "PROGRAM STORE COMPARE" (28.42.71.1) | "TON PIRCY TGR" (28.42.71.1) |

(The recovery trigger is printed "IRCY" in H1/H2 and "1RCY" in F4 -- the same glyph ambiguity of
"I"/"1" seen in "1RPT"; DERIVED: all are the I-unit recovery request trigger, 28.42.72.1.)

##### 3. Phases
This sheet draws no sequencer bar and no E / E.M / M phase lines. Phase-like terms appear only inside
conditions as trigger names: FPR2E, FPR3E, FPR3M, FPR 3 NM, FPR 2 E . NM, FPR4E, FPR4E M, FPR4 E . M, FPDD M.
(DERIVED: FPRnE/M/NM = FP register-n sequencer E / M / not-M phases, drawn on sheets 1-2.)

##### 4. Step table (compact; full lists in section 2)
| step | condition (PRINTED) | action (PRINTED) | ALD | notes |
|---|---|---|---|---|
| ZR FP6 on | 1YNOT22 . 1Y21.1Y23. 1Y24.1Y25. COND FP CLR, or SET ZR FP6 TGR | TON ZR FP6 TGR | 28.26.51.1 | |
| ZR FP4 on | ~1Y21. ~1Y23 .1Y24-1Y NOT 25. COND FP CL, or SET ZRFP4 | TON ZR FP4 TGR | 28.26.51.1 | |
| FP4 or FP6 | ZR FP4 OR ZR FP6 | branches D | 28.23.50.1 | |
| FP4, FPR4E | FPR4E -> ZOAR EQ 11 +12 + 16 - 31 | TON STORE WAIT TGR; TON IRCY REQ TGR | 28.14.43.1 / 28.42.51.1 / 28.42.72.1 | [KEY] |
| FP4, FPR4E | FPR4E -> PROGRAM STORE COMPARE | TON IRCY REQ TGR | 28.42.72.1 | [KEY] |
| FP4, FPR4E | FPR4E -> PROGRAM STORE COMPARE | TON PIRCY TGR | 28.42.71.1 | [KEY] |
| FP4 | FPR3E AND NO CANCEL -> PROGRAM STORE COMPARE. ACCEPT OR COMPARE | TON 1RCY REQ TGR | 28.14.33.1 / 28.42.72.1 | [KEY] |
| FP6 | ZR EXT LTH. ZR INSTR PREP COMPLETE. ~FPDD ~M .LAAR 1 BUSY | COND FPDD E TGR | 28.10.11.1 | [KEY] LAAR 1 |

##### 5. Counters, timers, triggers, registers, codes named
- Triggers: ZR FP6 TGR, ZR FP4 TGR, STORE WAIT TGR, IRCY / 1RCY REQ TGR, PIRCY TGR, FPDD E TGR,
  FPR2E (TON), FPR4E (COND ... TON), FPR 3 E (COND ... TON), XOF 1E (COND ... TON).
- Registers / fields: ZR (ZR 0-31, ZR0-15, ZR1+2+3, ZR4 MNT MD, ZR EXT, ZR INT, ZR ADR 8 / ZR ADDR 8, ZROC),
  ZOAR, Z32-49, Z45-49, MAB, XAB, LA / LAOC (6, 8 & 9) / LAOP tag, LA EXT / INT STORE TAG, LA DF / DS / NOP FR DF / NOP FR ALARM,
  LAAR 1, NIDC, MDF, 1Y21..1Y25, P.
- Others: SBC, SAC, CHKR EN T1, LA EN T1+2, LA EN T3, CHKR SINGLE ERROR, 1RPT ENABLED, BCU (T3 LD TO BCU WAIT FOR ACCEPT),
  PANEL KEY REQUEST, I CHR REQ ZR, I GEN PARITY, TYPE 2 / TYPE 3 LOAD.
- No counter (IAUC, OCC, TBC, ABC, SCC) and no timer is named.

##### 6. TIME
PRINTS NO TIME. No clock, cycle count, A/B pulse or duration appears on the sheet.

##### 7. [KEY] items, verbatim
- "FPR4E" (28.14.43.1) -> "ZOAR EQ 11 +12 + 16 - 31" (28.42.51.1) YES -> "TON STORE WAIT TGR" (28.42.51.1) and "TON IRCY REQ TGR" (28.42.72.1)
- "FPR4E" (28.14.43.1) -> "PROGRAM STORE COMPARE" (28.42.72.1) YES -> "TON IRCY REQ TGR" (28.42.72.1)
- "FPR4E" (28.14.43.1) -> "PROGRAM STORE COMPARE" (28.42.71.1) YES -> "TON PIRCY TGR" (28.42.71.1)
- "FPR3E AND NO CANCEL" (28.14.33.1) -> "PROGRAM STORE COMPARE. ACCEPT OR COMPARE" (28.42.72.1) YES -> "TON 1RCY REQ TGR" (28.42.72.1)
- "ZR EXT LTH. ZR INSTR PREP COMPLETE. ~FPDD ~M .LAAR 1 BUSY" (28.10.11.1) -> "COND FPDD E TGR" (28.10.11.1)
- Store tags: "SET LA EXT STORE TAG" (28.24.82.1, 36.09.14.1), "SET LA INT STORE TAG" (28.24.82.1, 36.09.15.1)
- "T3 LD TO BCU WAIT FOR ACCEPT" (28.21.74.1) (also printed "T3 LD TC BCU WAIT FOR ACCEPT" once)
- NOT on this sheet: anything that turns OFF / releases STORE WAIT; any XS (index storage) read or
  updated-indicator condition; any block/suspend trigger; any IHW handling; any explicit priority test;
  any pseudo-store, forwarding, houseclean, LAAR-2.

###### Agreement with the repo's prior reading (microarchitecture_plan.md rows 84-85)
AGREE in substance, with refinements:
1. The sheet prints "ZOAR EQ 11 +12 + 16 - 31" (28.42.51.1) -> "TON STORE WAIT TGR" + "TON IRCY REQ TGR".
   It is gated by "FPR4E" (28.14.43.1) on the ZR FP4 TGR path, not by a generic "store" test. ZOAR is
   (DERIVED) the Z operand-address register -- the instruction's own address -- so "keyed on the store's
   own address" holds only if FPR4E on ZR FP4 is the store preparation; the sheet itself never says "store"
   in that branch.
2. There are TWO further recovery sources on the same FPR4E bus that the prior reading does not mention:
   "PROGRAM STORE COMPARE" (28.42.72.1) -> "TON IRCY REQ TGR" and "PROGRAM STORE COMPARE" (28.42.71.1) ->
   "TON PIRCY TGR"; and on the FP4 right bus "FPR3E AND NO CANCEL" -> "PROGRAM STORE COMPARE. ACCEPT OR
   COMPARE" -> "TON 1RCY REQ TGR".
3. Confirmed: the sheet does not show what turns STORE WAIT off, nor any time for the recovery.

##### 8. Could not read / uncertain
- Db6, Db7: first 1-2 characters of each line under the scan smear (bracketed above).
- Db6 ALD "28.14.21.1" and Db7 ALD "28.14.21.1": last digits partly faint, read as .1.
- Da3 ALD printed "24.14.32.1" and Db1 ALD printed "21.14.33.1": read as printed; probably misprints of 28.x.
- A4' "CONDITION LA DF TAG": no input line visible; its role is uncertain.

#### Fig 3.1.14 -- ZR IHW TRIGGER, IHW RDY TRIGGER, AND IHW EX ZR TRIGGER

- Caption (PRINTED): "FIGURE 3.1.14. ZR IHW TRIGGER, IHW RDY TRIGGER, AND IHW EX ZR TRIGGER"
- PDF page 78; printed page "1-29/1-30"; issue date "2/1/62"; running head "M3-04-3   I UNIT FLOW DIAGRAMS".
- Applicability note (PRINTED, near the caption, rotated with the drawing): "CPU 7101 SER. NO. 30,004 AND HIGHER".
- Box text rotated 90 degrees; read from tiles rotated upright (300 dpi). In the upright view the
  branches below run "down"; on the page they run left-to-right.
- ALD numbers here are printed INSIDE the boxes.

Notation: `•` = AND as printed, `+` = OR, `-` as printed (DERIVED: often AND in these labels).

##### 1. IHW RDY ZR TGR (28.26.11.1)
TON (lines join at a dot labelled "TON") from:
- hexagon "NOT ZR MOD • SAC • YL-ZR M • ZR IHW AND ZL MT (28.26.11.1)", YES
- hexagon "SET HW RDY T (28.26.11.1)", YES   ("T" as printed; DERIVED: TGR)
No TOF drawn.

Under IHW RDY ZR TGR:
| # | condition | action(s) |
|---|---|---|
| R0 | (unconditional) | "BLOCK YR-ZL M TGR TOF (28.15.30.1)" |
| R1 | "YR - ZL E" (no ALD), YES | "RST MOD REQ TGR (28.26.21.1)" |
| R2 | "YR-XL M (28.15.32.1)" (exit unlabelled) | a long list, each box on the same line (all on R2's exit): |
|    | | "BLOCK YR-ZL M TGR TOF (28.15.30.1)" |
|    | | "COND LOP 4 TON CKT (28.88.34.1)" |
|    | | "COND LOP 5 TON CKT (28.88.34.1)" |
|    | | "COND LAMI TON CKT (28.81.11.1)" |
|    | | "COND EN-DIS TON CKT (28.70.54.1)" |
|    | | "COND DEC I TON CKT (28.75.11.1)" |
|    | | "COND EMFI TON CKT (28.70.34.1)" |
|    | | "COND XSF3 TON CKT (28.71.11.1)" |
|    | | "COND EMF5 TON CKT (28.70.21.1)" |
|    | | "COND DEC 3 TON CKT (28.70.14.1)" |
|    | | "COND DEC 4 TON CKT (28.79.14.1)" |
|    | | "NOT PRE DSAB (37.51.03.1)" |
|    | | "COND ADD 3 TON CKT (28.75.51.1)" |
|    | | "COND ADD I TON CKT (28.75.71.1)" |
|    | | hexagon "EX + RN (28.89.32.1)" YES -> "ALLOW LARCY TON (28.42.81.1)" |
|    | | hexagon "SAC (28.87.64.1)" YES -> "TON I EXP TGR (28.87.64.1)" |
|    | | hexagon "BE + BEW + BD + SIC-BE-BEW-BD (28.89.32.1)" YES -> "ALLOW LARCY TON (28.42.81.1)" |

("DEC I", "EMFI", "ADD I": the last glyph may be "1"; printed as a thin I/1.)

##### 2. ZR IHW TGR (28.26.61.1)
No TON/TOF inputs drawn on this sheet. Under it:
| # | condition | action(s) |
|---|---|---|
| H1 | "ZL MT (28.26.61.1)", YES | "COND IHW RDY ZR TGR TON CKT (28.26.11.1)"; "COND IHW EX ZR TGR TON CKT (28.26.11.1)" |
| H2 | "SAC • MOD ZR M" (no ALD), YES | "TON IHW RDY TGR (28.26.11.1)"; "TON IHW EX ZR TGR (28.26.11.1)" |

##### 3. IHW EX ZR TGR (28.26.11.1)
TON from:
- hexagon "SET IHW EX TGR (28.26.11.1)", YES
- hexagon "NOT ZR MOD • SAC (28.26.11.1)", YES
No TOF drawn.

Under IHW EX ZR TGR:
| # | condition | action(s) |
|---|---|---|
| X0 | (unconditional) | "BLOCK XF+ DEC TON (28.15.50.1)"; "BLOCK GEN OF INSTR PREP COMP ZL (28.15.32.1)"; "BLOCK MOD ZL TON (28.15.40.1)"; "BLOCK ZL DEC TON (28.27.30.1)" |
| X1 | "NOT ZL MOD • XF + DEC ZL (28.15.51.1)", YES -> X2 | |
| X2 | "ZR INSTR COMP (28.15.51.1)", YES | "IHW RDY ZL (28.15.41.1)" |

##### 4. Structure / phases
No sequencer bar, no E / E.M / M phase lines. Phase-like terms in conditions: YR-ZL E, YR-ZL M, YR-XL M, MOD ZR M, YL-ZR M.

##### 5. Step table
| step | condition (PRINTED) | action (PRINTED) | ALD | notes |
|---|---|---|---|---|
| IHW RDY on | NOT ZR MOD • SAC • YL-ZR M • ZR IHW AND ZL MT, or SET HW RDY T | TON IHW RDY ZR TGR | 28.26.11.1 | IHW |
| IHW RDY | (always) | BLOCK YR-ZL M TGR TOF | 28.15.30.1 | |
| IHW RDY | YR - ZL E | RST MOD REQ TGR | 28.26.21.1 | |
| IHW RDY | YR-XL M | COND LOP 4/5, LAMI, EN-DIS, DEC I/3/4, EMFI, EMF5, XSF3, ADD 3/I TON CKT; NOT PRE DSAB | various | [KEY] XSF3 |
| IHW RDY . YR-XL M | EX + RN, or BE + BEW + BD + SIC-BE-BEW-BD | ALLOW LARCY TON | 28.42.81.1 | [KEY] recovery |
| IHW RDY . YR-XL M | SAC | TON I EXP TGR | 28.87.64.1 | |
| ZR IHW | ZL MT | COND IHW RDY ZR TGR TON CKT; COND IHW EX ZR TGR TON CKT | 28.26.11.1 | |
| ZR IHW | SAC • MOD ZR M | TON IHW RDY TGR; TON IHW EX ZR TGR | 28.26.11.1 | |
| IHW EX on | SET IHW EX TGR, or NOT ZR MOD • SAC | TON IHW EX ZR TGR | 28.26.11.1 | |
| IHW EX | (always) | BLOCK XF+ DEC TON; BLOCK GEN OF INSTR PREP COMP ZL; BLOCK MOD ZL TON; BLOCK ZL DEC TON | 28.15.50.1, 28.15.32.1, 28.15.40.1, 28.27.30.1 | [KEY] blocks ZL |
| IHW EX | NOT ZL MOD • XF + DEC ZL, then ZR INSTR COMP | IHW RDY ZL | 28.15.41.1 | |

##### 6. Named items
- Triggers: IHW RDY ZR TGR, ZR IHW TGR, IHW EX ZR TGR, IHW RDY TGR, YR-ZL M TGR, MOD REQ TGR, I EXP TGR, LARCY (ALLOW ... TON).
- TON circuits conditioned: LOP 4, LOP 5, LAMI, EN-DIS, DEC I, EMFI, XSF3, EMF5, DEC 3, DEC 4, ADD 3, ADD I.
- Registers: YL, YR, ZL, ZR, XL. Others: SAC, MOD, XF, DEC, EX, RN, BE, BEW, BD, SIC, PRE DSAB.
- No counter, timer or LAOP code.

##### 7. TIME
PRINTS NO TIME.

##### 8. [KEY] items (verbatim)
- IHW (instruction half-word) handling: whole figure. "NOT ZR MOD • SAC • YL-ZR M • ZR IHW AND ZL MT" -> TON "IHW RDY ZR TGR"; "IHW RDY ZL (28.15.41.1)".
- Recovery: "EX + RN (28.89.32.1)" -> "ALLOW LARCY TON (28.42.81.1)"; "BE + BEW + BD + SIC-BE-BEW-BD (28.89.32.1)" -> "ALLOW LARCY TON (28.42.81.1)". (DERIVED: LARCY is on the same 28.42 recovery pages as IRCY/PIRCY.)
- Block (not the ZL BLOCK trigger itself): "BLOCK GEN OF INSTR PREP COMP ZL", "BLOCK MOD ZL TON", "BLOCK ZL DEC TON", "BLOCK XF+ DEC TON", "BLOCK YR-ZL M TGR TOF".
- "COND XSF3 TON CKT (28.71.11.1)" (DERIVED: an XS-related step; the sheet does not expand it).
- Nothing about STORE WAIT, priority, forwarding, houseclean, LAAR.

##### 9. Could not read / uncertain
- Hexagons "YR - ZL E" and "SAC • MOD ZR M": no ALD printed.
- "SET HW RDY T": last character "T" as printed.
- Exit label of "YR-XL M" is not printed.

#### Fig 3.1.15 -- ZL MOD REQ TRIGGER AND MOD ZL SEQUENCER

- Caption (PRINTED): "FIGURE 3.1.15. ZL MOD REQ TRIGGER AND MOD ZL SEQUENCER"
- PDF page 79; printed page "1-31/1-32"; issue date "2/1/62"; running head "M3-04-3   I UNIT FLOW DIAGRAMS".
- Applicability note (PRINTED): "CPU 7101 SER. NO. 30,004 AND HIGHER".
- Text rotated 90 degrees; read from the page rotated upright (300 dpi). ALD numbers are inside the boxes.

Notation: `•` / `o` = AND dot as printed (the dot sometimes prints hollow), `+` = OR, `~X` = overbar.
Several labels carry bars that sit BETWEEN lines (an underline of one line or an overbar of the next);
they are recorded as "[bar: ...]" rather than resolved.

##### 1. ZL MODIFY REQUIRED TGR (28.26.23.1)
TON (line labelled "TON ZL MOD R") from five hexagons, all YES:
1. "SET MOD L TGR (28.26.23.1)"
2. "SBC • IYL MOD DEC • YL - ZLE (28.26.23.1)"
3. "~IMM IX 1YR + FULL WD SC • 1Y61 + 1Y60 + 1Y62 + 1Y63 • DEC MOD REQ FR 1YR • UNCOND + BIT BR CL 1YR + BIT BR DEC • 1YRD • SBC • YR ZLE (28.26.23.1)"
   [bar: overbar over "IMM IX 1YR"; bars under "DEC MOD", under "REQ FR 1YR" and "UNCOND", under "BIT" and "1YR" -- possibly overbars of the following line's words]
4. "SBC • YR - ZLE • IY63 • DEC MOD REQ FR 1 YR • 1 YR BRC + UNCOND + BIT BR CL • BIT BR DEC 2 (28.26.23.1)"
5. "NL IB MOD D • YL-ZLE • SBC (28.26.23.1)"
No TOF drawn for this trigger (but see "TON 1 BIT MOD TGR" below).

Under ZL MODIFY REQUIRED TGR (no condition on the first two lines; DERIVED: active while the trigger is on):
| # | condition | action(s) |
|---|---|---|
| Q0a | (unconditional) | "BLOCK WBC + DEC TON (28.15.80.1)"; "BLOCK ZR WAS IHW TOF (28.15.51.1)"; "BLOCK XF + DEC TON (28.15.50.1)"; "COND MOD ZL TON (28.15.40.1)" |
| Q0b | (unconditional) | "BLOCK YL-ZR TON (28.15.10.1)"; "BLOCK YR-ZR TON (28.15.60.1)"; "COND MOD ZL TON (28.15.40.1)"; "BLOCK GEN OF INSTR PREP COMPL ZL (28.15.32.1)" |
| Q1 | "SAC (28.15.50.1)", YES | "TON XF + DEC (28.15.50.1)" |
| Q2 | "YR - ZL M (28.15.32.1)", YES | "TON Y- Z START (28.26.11.1)"; "ZL + ZR PREP NOT BUSY (28. 20.21.1)"; then on to Q4 |
| Q3 | "YL - ZL M (28.15.71.1)", YES | joins the line into Q4 |
| Q4 | "ZR WAS IHW (28.15.71.1)", YES | "Y - Z M MOD REQ (28.70.42.1)" |

##### 2. MODIFY ZL SEQUENCER (28.15.40.1)
TON (line labelled "TON MOD ZL") from five hexagons, all YES:
1. "OK TO MOD ZL • YR-ZL M • NOT CHKR SING ERR • NOT IHW-EX T • FW NOT ST • SAC • ZL MOD REQ (28.15.40.1)"
2. "SAC • NO LA CHKR REQ • NOT CHKR SING ERR • OK TO MOD ZL • XF + DEC ZL MC • FW NOT ST (28.15.40.1)"
3. "YL - ZLM • SAC • ZL MOD REQ (28.15.40.1)"
4. "NOT FW NOT S • ZR WAS IHW • NOT IHW EXC • YR - ZL M • SAC • ZL MOD (28.15.40.1)" [bars under "NOT FW NOT S •" and "ZR WAS IHW"]
5. "SAC • NOT FW NOT S • XF + DEC ZL M • ZL MOD R (28.15.40.1)"

Phase lines PRINTED at the sequencer: "E", "E • M", "M". They meet one continuous line on the drawing,
each with a junction dot, so the split below is DERIVED from where each line enters the trunk.

###### Phase E (left/lower trunk)
| # | condition | action(s) |
|---|---|---|
| E0 | (unconditional) | "TON MOD ZL M TGR WITH NEXT SBC (28.15.40.1)"; "COND XF + DEC ZL M TON CKT (28.15.50.1)" |
| E1 | "ZL FP CL • ~FW NOT ST + PROG ~IX (28.15.41.1)" [bars under "ZL FP CL" and "NOT ST + PROG"; overbars on "FW" and "IX"], YES | "Z 0-17 ABB PREP (28.96.03.1)" |
| E2 | "ZL FP CL (28.15.41.1)", YES | "HOT 1 TO ABB P2 (28.96.41.1)" |
| E3 | "ZL IHWT • FW ON BDS + PROG IX (28.15.41.1)" [bars under "ZL IHWT •" and "FW ON BDS"], YES | "Z 0-17 ABB PREP (28.96.03.1)"; "Z 18 ABB PREP (28.96.03.1)"; "Z 18 TO ABB P2 - ADJ PAR Z 18 - 23 (28.96.07.1)" |
| E4 | "FWS + NOTS o FW ON BDS + PROG IX (28.15.41.1)" [bars under "FWS + NOTS o", "FW ON BDS", "PROG IX"], YES | "Z 0-17 ABB PREP (28.96.03.1)"; "Z 18 ABB PREP (28.96.03.1)"; "Z 19-23 ABB PREP (28.96.07.1)" |
| E5 | "SBC (28.15.30.1)", YES | "TOF YR - ZL M TGR (28.15.30.1)" |
| E6 | "SBC (28.15.70.1)", YES | "TOF YL - ZL M TGR (28.15.70.1)" |
| E7 | (unconditional, on a second vertical) | "X 0-23 TO ABA • X 24-27 TO ABA (28.96.01.1)"; "SET IDC ON IAUC ERR (28.51.01.1)"; "RESET ZL ADDR 8 TGR (28.27.57.1)"; "Y - Z L + MOD ZL • RST ZL TAGS (28.51.08.1)"; "HOLD DATA SELECT (27.09.07.1)" |
| E8 | "SBC (28.26.23.1)", YES | "TON 1 BIT MOD TGR (28.26.23.1)" |
| E9 | "PX • FW NOT ST • XF + DEC ZLM + (28.15.42.1)", YES | "PREP GT Z0 - 23 TO ICIB (28.79.65.1)"; "COND IDC FR I PAR ERR PREP (28.99.03.1)"; "TON PX YL TGR (28.78.34.1)"; "PREP SET ONE TO ICIB PAR (28.21.20.1)"; then E10-E12 |
| E10 | "MOD ZL M • CD 2Y - ZL (28.15.42.1)", YES | "P COND ICOB TO 2Y 0-63 (28.44.16.1)" |
| E11 | "MOD ZL M o CD IY - ZL (28.15.42.I)", YES | "P COND ICOB TO 1Y 0 - 63 (28.44.16.1)" |
| E12 | "~MOD ZL (28.15.42.1)" (overbar), YES | "IP CHK PAR (28.98.07.1)"; "I CHK E • NM P (38.03.03.1)" |

###### Phase E • M
| # | condition | action(s) |
|---|---|---|
| EM0 | (unconditional) | "Y - Z + MOD ZL CND ZL MA TAGS (28.51.01.1)" |
| EM1 | "MOD ZLM • ZL FP CL (28.15.41.1)", YES | "GT AOB 18 TO ZL (28.27.50.1)" |
| EM2 | "FWS + NOTS • MOD ZL M (28.15.41.1)", YES | "GT AOB 24 TO ZL (28.27.50.1)" |
| EM3 | "ZL IHW • MOD ZL M (28.15.41.1)", YES | "GT AOB 24 TO ZL"; "GT AOB 18 TO ZL (28.27.50.1)"; "GT AOB I9 TO ZL (28.27.50.I)" |

###### Phase M
| # | condition | action(s) |
|---|---|---|
| M0 | (unconditional) | "BLOCK GEN OF I CHK E • NM P • I CHK PAR (28.15.42.1)"; "COND YR - ZR TON CKT (28.15.60.1)"; "COND YL - ZR TON CKT (28.15.50.1)" |
| M1 | "CD 1Y - ZL • FW NOT S (28.15.42.1)", YES | "COND ICOB TO 1Y 0-63 (28.44.16.1)" |
| M2 | "CD 2Y - ZL • FW NOT S (28.15.42.1)", YES | "COND ICOB TO 2Y 0 - 63 (28.44.16.1)" |
| M3 | "ZL IHW T • ZR MT (28.15.41.1)", YES | "IHW RDY E1 (28.67.17.1)"; "IHW RDY E2 (28.64.14.1)" |

##### 3. Step table (summary)
| step / phase | condition (PRINTED) | action (PRINTED) | ALD | notes |
|---|---|---|---|---|
| MOD REQ on | one of 5 hexagons (SET MOD L TGR; SBC • IYL MOD DEC • YL - ZLE; 1Y60-63 decode...; SBC • YR - ZLE • IY63...; NL IB MOD D • YL-ZLE • SBC) | TON ZL MODIFY REQUIRED TGR | 28.26.23.1 | |
| MOD REQ | (always) | BLOCK WBC+DEC TON, BLOCK ZR WAS IHW TOF, BLOCK XF+DEC TON, BLOCK YL-ZR TON, BLOCK YR-ZR TON, BLOCK GEN OF INSTR PREP COMPL ZL, COND MOD ZL TON | 28.15.x | [KEY] block |
| MOD REQ | YR - ZL M | TON Y- Z START; ZL + ZR PREP NOT BUSY | 28.26.11.1; 28.20.21.1 | |
| MOD REQ | ZR WAS IHW | Y - Z M MOD REQ | 28.70.42.1 | IHW |
| SEQ on | 5 TON hexagons incl. "NOT CHKR SING ERR", "NO LA CHKR REQ", "OK TO MOD ZL" | TON MOD ZL (MODIFY ZL SEQUENCER) | 28.15.40.1 | |
| E | (always) | TON MOD ZL M TGR WITH NEXT SBC; X 0-23/24-27 TO ABA; SET IDC ON IAUC ERR; RESET ZL ADDR 8 TGR; RST ZL TAGS; HOLD DATA SELECT | various | IAUC named |
| E | PX • FW NOT ST • XF + DEC ZLM + | PREP GT Z0-23 TO ICIB; TON PX YL TGR; ... | 28.15.42.1 | |
| E•M | various | GT AOB 18 / 24 / 19 TO ZL | 28.27.50.1 | |
| M | ZL IHW T • ZR MT | IHW RDY E1; IHW RDY E2 | 28.67.17.1; 28.64.14.1 | IHW |

##### 4. Named items
- Sequencer: MODIFY ZL SEQUENCER (phases E, E • M, M).
- Triggers: ZL MODIFY REQUIRED TGR, MOD L TGR, MOD ZL M TGR, YR-ZL M TGR, YL-ZL M TGR, 1 BIT MOD TGR, PX YL TGR, ZL ADDR 8 TGR, IHW-EX T, Y-Z START.
- Counter: IAUC ("SET IDC ON IAUC ERR"). No other counter; no timer.
- Registers / buses: YL, YR, ZL, ZR, 1Y, 2Y, 1YR, X 0-27, Z 0-23, ABA, ABB (P2), AOB, ICIB, ICOB, IDC.
- Others: SBC, SAC, FW, FWS, ST, S, PROG IX, IMM IX, CHKR SING ERR, LA CHKR REQ, BIT BR, UNCOND, BRC, WBC, XF, DEC, PX.

##### 5. TIME
PRINTS NO TIME. (Only "WITH NEXT SBC" in "TON MOD ZL M TGR WITH NEXT SBC" refers to a clock-like event; no cycle count is printed.)

##### 6. [KEY] items (verbatim)
- Block: "BLOCK GEN OF INSTR PREP COMPL ZL (28.15.32.1)", "BLOCK ZR WAS IHW TOF (28.15.51.1)", "BLOCK XF + DEC TON", "BLOCK WBC + DEC TON", "BLOCK YL-ZR TON", "BLOCK YR-ZR TON", "BLOCK GEN OF I CHK E • NM P • I CHK PAR".
- IHW: "ZR WAS IHW (28.15.71.1)" -> "Y - Z M MOD REQ"; "ZL IHW T • ZR MT" -> "IHW RDY E1", "IHW RDY E2"; "NOT IHW-EX T", "NOT IHW EXC" in the sequencer TON conditions.
- Index/modify (DERIVED relevance to XS): "X 0-23 TO ABA • X 24-27 TO ABA (28.96.01.1)", "PROG IX", "IMM IX 1YR".
- No STORE WAIT, recovery, priority, LAAR, forwarding or houseclean on this sheet.

##### 7. Could not read / uncertain
- Bar placements in the hexagons marked [bar: ...]: overbar vs underline unresolved at 300 dpi.
- "GT AOB I9 TO ZL (28.27.50.I)": the "I9" is probably "19".
- E/E•M/M split: the three phase lines join one continuous drawn line; the assignment above is DERIVED from junction positions.

#### Fig 3.1.16 -- ZL BLOCK AND SUSPEND TRIGGERS

- Caption (PRINTED): "FIGURE 3.1.16. ZL BLOCK AND SUSPEND TRIGGERS"
- PDF page 80; printed page "1-33/1-34"; issue date "2/1/62"; running head "M3-04-3   I UNIT FLOW DIAGRAMS".
- Applicability note (PRINTED): "CPU 7101 SER. NO. 30,004 AND HIGHER".
- Text rotated 90 degrees; read from the page rotated upright (300 dpi). ALD numbers inside the boxes.
- The fold line of the fold-out crosses two boxes ("BLOCK ESTAB OF IC FTH PRIORITY" under SPND 1Y, "BLOCK ICBC1Y TON", "BLOCK GEN OF IF2Y GT ICA 0-16 TO MAB"): it looks like a strike-through but is the fold.

Notation: `•` / `o` = AND as printed, `+` = OR.

All four triggers are drawn the same way: TON from hexagon(s), then a trunk with unconditional
rectangles on both sides (DERIVED: everything a set trigger blocks). No TOF is drawn for any of them;
no sequencer, no phase lines.

##### 1. ZL BLOCK 1Y TGR (28.42.41.1)
TON from: hexagon "INSTR PREP TON ZL BLOCK 1Y • SBC (28.42.41.1)", YES.
Actions (unconditional):
- "BLOCK GEN OF 1Y NOT BUSY (28.42.12.1)"
- "BLOCK GEN OF 1Y NOT BUSY ANTIC ON ACC (28.42.12.1)"
- "BLOCK ESTABL OF IC FTH PRIORITY (28.42.12.1)"  **[KEY]**
- "BLOCK GEN OF I EX USE 1Y (28.42.12.1)"
- "BLOCK GEN OF IY NOT BUSY ANTIC (28.42.12.1)" ("IY" as printed; DERIVED 1Y)

##### 2. ZL BLOCK 2Y TGR (28.42.41.1)
TON from: hexagon "INSTR PREP ZL BLOCK 2Y • SBC (28.42.41.1)", YES.
Actions (unconditional):
- "BLOCK GEN OF 2Y NOT BUSY (28.42.12.1)"
- "BLOCK GEN OF 2Y NOT BUSY ANTIC (28.42.12.1)"
- "BLOCK ESTAB OF IC FTH PRIORITY (28.42.12.1)"  **[KEY]**
- "BLOCK GEN OF 2Y NOT BUSY ANTIC ON ACC (28.42.12.1)"
- "BLOCK BR CKT IF2Y TON (28.41.31.1)"

##### 3. ZL SPND 1Y TGR (28.42.42.1)
TON from three hexagons (all YES):
- "IWC2 • ICOR NE • 2Y RD BRU + BRC • NO CHKR SING ERR • SAR (28.42.42.1)"
- "SBC • BR Y-Z XFER TON ZL SPND 1Y (28.42.42.1)"
- "E1 TON SPND TGRS • SBC (28.42.42.1)"
Actions (unconditional):
- "BLOCK GEN OF IF1Y ONE TO MAB 15 (28.41.22.1)"
- "BLOCK GEN OF IF1Y FTH REQ (28.41.22.1)"
- "BLOCK GEN OF IF1Y GT ICA O-16 TO MAB (28.41.22.1)"
- "BLOCK GEN OF IF1Y PNL KEY REQ (28.41.22.1)"
- "BLOCK GEN OF IF1Y GT ICA O-16 TO MAB (28.41.22.1)" (printed twice, the second with a slashed zero "Θ-16")
- "BLOCK IF1Y TOF (28.41.21.1)"
- "COND IF2Y ANTIC TON CKT (28.41.31.1)"
- "BLOCK ICOF 1Y TON (28.41.23.1)"
- "BLOCK ESTAB OF IC FTH PRIORITY (28.42.12.1)"  **[KEY]**
- "BLOCK ICBC1Y TON (28.41.23.1)"
- "BLOCK IF1Y IND TOF (28.41.22.1)"
- "BLOCK IWC1 TON (28.41.51.1)"
- "BLOCK GEN OF IF1Y RETURN ADR (28.41.22.1)"

##### 4. ZL SPND 2Y TGR (28.42.43.1)
TON from three hexagons (all YES):
- "IWCIE • ICOR NE o 1YRD BRU + BRC • NO CHKR SING ERR • SAR (28.42.43.1)" ("IWCIE" as printed; DERIVED IWC1E or IWC1 E)
- "SBC • BR Y-Z XFER TON ZL SPND 2Y (28.42.43.1)"
- "E1 TON 2Y SPND TGR • SBC (28.42.42.1)"
Actions (unconditional):
- "BLOCK GEN OF IC FTH M • IC FTH MEM (28.41.21.1)"
- "BLOCK ESTAB OF IC FTH PRIORITY (28.42.12.1)"  **[KEY]**
- "BLOCK ICADV E2 TON (28.41.41.1)"
- "BLOCK IF2Y FTH REQ (28.41.32.1)"
- "BLOCK GEN OF IF2Y ONE TO MAB 15 (28.41.32.1)"
- "BLOCK IF2Y PNL KEY REQ (28.41.32.1)"
- "BLOCK GEN OF IF2Y GT ICR 0-16 TO MAB (28.41.32.1)"
- "BLOCK IF2Y TOF (28.41.31.1)"
- "BLOCK GEN OF IF2Y GT ICA 0-16 TO MAB (28.41.32.1)"
- "BLOCK ICFO2Y TON (28.41.33.1)"
- "BLOCK IF2Y IND TOF (28.42.32.1)"
- "BLOCK ICBC2Y TON (28.41.33.1)"
- "BLOCK GEN OF IF2Y RETURN ADR (28.41.32.1)"
- "BLOCK ICADV E1 TOF (28.41.41.1)"
- "BLOCK IF1Y E TON (28.41.21.1)"
- "BLOCK IWC2 TON (28.41.61.1)"
Then the trunk ends in hexagon "IF2Y M (28.41.32.1)", YES -> "COND ICADY E2 TON (28.41.41.1)" ("ICADY" as printed; DERIVED ICADV).

##### 5. Step table
| trigger | TON condition (PRINTED) | actions (PRINTED, summary) | ALD | notes |
|---|---|---|---|---|
| ZL BLOCK 1Y TGR | INSTR PREP TON ZL BLOCK 1Y • SBC | BLOCK GEN OF 1Y NOT BUSY (+ANTIC, +ANTIC ON ACC); BLOCK ESTABL OF IC FTH PRIORITY; BLOCK GEN OF I EX USE 1Y | 28.42.41.1 / 28.42.12.1 | [KEY] block, priority |
| ZL BLOCK 2Y TGR | INSTR PREP ZL BLOCK 2Y • SBC | same for 2Y; BLOCK BR CKT IF2Y TON | 28.42.41.1 / 28.42.12.1 / 28.41.31.1 | [KEY] |
| ZL SPND 1Y TGR | IWC2 • ICOR NE • 2Y RD BRU + BRC • NO CHKR SING ERR • SAR; or SBC • BR Y-Z XFER TON ZL SPND 1Y; or E1 TON SPND TGRS • SBC | blocks IF1Y fetch generation (FTH REQ, ICA/MAB, RETURN ADR, IND TOF, TOF), ICOF 1Y, ICBC1Y, IWC1; BLOCK ESTAB OF IC FTH PRIORITY; COND IF2Y ANTIC TON CKT | 28.42.42.1 | [KEY] suspend |
| ZL SPND 2Y TGR | IWCIE • ICOR NE o 1YRD BRU + BRC • NO CHKR SING ERR • SAR; or SBC • BR Y-Z XFER TON ZL SPND 2Y; or E1 TON 2Y SPND TGR • SBC | blocks IF2Y fetch generation, IC FTH M / MEM, ICADV E1/E2, ICFO2Y, ICBC2Y, IF1Y E TON, IWC2; BLOCK ESTAB OF IC FTH PRIORITY; IF2Y M -> COND ICADY E2 TON | 28.42.43.1 | [KEY] suspend |

##### 6. Named items
- Triggers: ZL BLOCK 1Y TGR, ZL BLOCK 2Y TGR, ZL SPND 1Y TGR, ZL SPND 2Y TGR, IF1Y, IF2Y (and IF1Y E, IF2Y M, IF2Y ANTIC), ICOF 1Y, ICFO2Y, ICBC1Y, ICBC2Y, ICADV E1/E2, IWC1, IWC2, IWCIE.
- Registers / addresses: 1Y, 2Y, IC, ICA, ICR, MAB (bit 15), ICOR.
- Others: SBC, SAR, BRU, BRC, BR Y-Z XFER, CHKR SING ERR, PNL KEY REQ, RETURN ADR.
- No counter, no timer, no LAOP code.

##### 7. TIME
PRINTS NO TIME.

##### 8. [KEY] items (verbatim)
- Priority: "BLOCK ESTABL OF IC FTH PRIORITY (28.42.12.1)" under ZL BLOCK 1Y TGR; "BLOCK ESTAB OF IC FTH PRIORITY (28.42.12.1)" under ZL BLOCK 2Y TGR, ZL SPND 1Y TGR and ZL SPND 2Y TGR.
- Block: "INSTR PREP TON ZL BLOCK 1Y • SBC" -> "ZL BLOCK 1Y TGR"; "INSTR PREP ZL BLOCK 2Y • SBC" -> "ZL BLOCK 2Y TGR".
- Suspend: "ZL SPND 1Y TGR" (28.42.42.1) and "ZL SPND 2Y TGR" (28.42.43.1) with the TON conditions above.
- These are on ALD page group 28.42 -- the same group as STORE WAIT (28.42.51.1) and the recovery triggers (28.42.71/72/81.1) -- but this sheet shows no link to STORE WAIT, and no TOF for any block/suspend trigger.
- No STORE WAIT, recovery, LAAR, forwarding or houseclean on this sheet.

##### 9. Could not read / uncertain
- "IWCIE" (first SPND 2Y hexagon) and "ICADY" are read as printed.
- Boxes crossed by the fold line remain legible.

#### Fig 3.1.17 -- ZL DEC TRIGGER

- Caption (PRINTED): "FIGURE 3.1.17. ZL DEC TRIGGER"
- PDF page 81; printed page "1-35/1-36"; issue date "2/1/62"; running head "M3-04-3   I UNIT FLOW DIAGRAMS".
- Applicability note (PRINTED): "CPU 7101 SER. NO. 30,004 AND HIGHER".
- Text rotated 90 degrees; read from the page rotated upright (300 dpi). ALD numbers inside the boxes.
- The fold line crosses several boxes (ZEDEC 19 TO I BOX, ZEDEC 23 TO BR, ZEDEC 26 TO CL, ZEDEC 21 TO MIGC, ZEDEC 24 TO C, ZEDEC 28 TO IMMIX, TON ZLIDC); it is not a strike-through.

Notation: `•` = AND, `+` = OR, `~X` = overbar, as printed.

##### 1. ZL DECODE (DEC) TGR (28.27.30.1)
TON from:
- hexagon "IEX COMP RST • SAC • ZL IHW (28.27.30.1)", YES
- hexagon "YR IHW • SBC • NOT IHW EX F • YR-ZL E (28.27.30.1)", YES
TOF: none drawn as an input; but see "BLOCK ZL DEC TOF TGR TOF (28.27.30.1)" below and "TOF ZL IHW TGR".
No sequencer bar or phase lines on this sheet.

##### 2. Upper bus (directly under the trigger)
| # | condition | action(s) |
|---|---|---|
| U0 | (unconditional, left) | "I EX USE ZL TO FR 17 LFT + RHT HLFZ CONT CKTS (28.67.12.1)"; "BLOCK ZL DEC TOF TGR TOF (28.27.30.1)" |
| U1 | "SBC • I EX COMP RST (28.26.61.1)", YES | "TOF ZL IHW TGR (28.26.61.1)" |
| U2 | "ZL IHW • SBC • I EX GOING (28.15.40.1)", YES | "TOF MOD ZL M TGR (28.15.40.1)" |
| U3 | "BLK DEC (28.60.11.1)", YES | its YES line drops to the lower decode bus (as drawn, see note) |
| U4 | (unconditional, right) | "BLOCK DEC ZR (28.60.11.1)"; "BLOCK USE ZR (28.60.11.1)"; "BLOCK I EX USE ZR (28.60.11.1)" |

Note (DERIVED / uncertain): as drawn, the BLK DEC YES line joins the lower bus with a junction dot,
and the three "BLOCK ... ZR" boxes hang unconditionally off the upper bus. One would expect BLK DEC YES
to feed the "BLOCK ... ZR" boxes; the drawing is transcribed as it stands.

##### 3. Lower bus -- ZL control / error column
| # | condition | action(s) |
|---|---|---|
| L1 | "OLLIE• BAC (28.79.23.1)", YES (exit drawn on the left) | "END EX ZL (28.79.63.1)"; "GT Z 0-18 TO ICIB 0-23 (28.79.65.1)" |
| L2 | "ZLNA ON + ZLXA ON + ZLSA ON (28.51.08.1)", YES | "ZL BR ADR INVLD (28.51.07.1)" |
| L3 | "RLLI E ON (28.79.53.1)", YES | "GT Z 0-23 TO ICIB 0-23 (28.79.65.1)" |
| L4 | "BI + BB • RLLI E ON (28.79.53.1)", YES | "END EX ZL (28.79.63.1)" |
| L5 | "OLLIE ON (28.79.23.1)", YES | "GT Z 19-24 CK (25.03.02.1)"; "Z 28-31 TO ICIB 60-63 (28.79.65.1)" |
| L6 | "SAC • SET ZL IDC ON I PAR ERR (28.51.03.1)", YES | -> "TON ZLIDC (28.51.03.1)" |
| L7 | "COND IDC FR UNCOR ERR • SAC (28.51.03.1)", YES | -> "TON ZLIDC" |
| L8 | "LA PAR ERR• SET ZL IDC ON LA PAR ERR • SAR (28.51.03.1)", YES | -> "TON ZLIDC" |
| L9 | "XS ADR CKK • SET ZLIDC ON XAC (28.51.03.1)", YES  **[KEY]** | -> "TON ZLIDC" |
| L10 | "SET ZLIDC + ZRIDC ON MC • SBC • MEM CKK (28.51.03.1)", YES | -> "TON ZLIDC (28.51.03.1)" (L6-L10 YES lines join) |
| L11 | (unconditional) | "USE ZL + ZR TO BR INSTR DEC CKTS (28.61.70.1)" |
| L12 | (unconditional) | "USE ZL TO ZOA MEM AREA DEC (28.61.76.1 - 28.61.78.1)" |

##### 4. Lower bus -- ZL bit decode (each hexagon "Z nn" YES -> its boxes)
| hexagon | boxes on YES |
|---|---|
| "Z17 (28.60.13.1)" | "GEN NOT OA 17 (28.67.13.1)" |
| "Z18 (28.60.13.1)" | "CND SPND INTLK TGR TON (28.42.44.1)" **[KEY]**; "GEN I EX IN PROG + RCVR TO YR (28.42.44.1)" **[KEY]**; "GEN OA 18 (28.67.13.1)" |
| "Z19 (28.60.13.1)" | "ZEDEC 19 TO MIGC CL DCDING (28.61.21.1)"; "ZEDEC 19 TO I BOX IND DCDING CKTS (28.52.10.1)"; "ZEDEC 19 TO BR INSTR DCDING CKTS (28.61.70.1)" |
| "Z 20 (28.16.13.1)" (sic) | "ZEDEC 20 TO MIGC CL DEC CKTS (28.61.21.1)"; "ZEDEC 20 TO I BOX IND DEC CKTS (28.52.10.1)"; "ZEDEC 20 TO BR INSTR DEC CKTS (28.61.70.1)" |
| "Z 21 (28.60.13.1)" | "ZEDEC 21 TO MIGC CL DEC CKTS (28.61.21.1)"; "ZEDEC 21 TO I BOX IND DEC CKTS (28.52.10.1)"; "ZEDEC 21 TO BR INSTR DEC CKTS (28.61.70.1)" |
| "Z 22 (28.60.13.1)" | "ZEDEC 22 TO BR INSTR DEC CKTS (28.61.70.1)"; "ZEDEC 22 TO I BOX IND DEC CKTS (28.52.10.1)"; "ZEDEC 22 TO CL DEC CKTS (28.61.11.1)" |
| "Z 23 (28.60.13.1)" | "ZEDEC 23 TO DIRECT IX INSTR DEC (28.61.42.1 - 28.61.44.1)"; "ZEDEC 23 TO CL DEC CKTS (28.61.11.1)"; "ZEDEC 23 TO I BOX IND DEC CKTS (28.52.10.1)"; "ZEDEC 23 TO BR INSTR DEC CKTS (28.61.70.1)"; "ZEDEC 23 TO INSTR EX FUN GEN (28.61.75.1)" |
| "Z 24 (28.60.13.1)" | "ZEDEC 24 TO BR INSTR DEC CKTS (28.61.70.1)"; "ZEDEC 24 TO INSTR EX FUN GEN (28.61.75.1)"; "ZEDEC 24 TO I BOX IND DEC CKTS (28.52.10.1)"; "ZEDEC 24 TO DIRECT IX INSTR DEC CKTS (28.61.41.1 - 28.61.44.1)"; "ZEDEC 24 TO C DEC CKTS (28.61.11.1)"; "ZEDEC 24 TO TMT • SWAP DEC CKTS (28.61.12.1)" |
| "Z 25 (28.60.13.1)" | "ZEDEC TO DIRECT IX INSTR DEC CKTS (28.61.41.1 - 28.61.44.1)" (no "25" printed); "ZEDEC 25 TO BR INSTR DEC CKTS (28.61.70.1)"; "ZEDEC 25 TO CL DEC CKTS (28.61.11.1)"; "ZEDEC 25 TO TMT • SWAP DEC CKTS (28.61.12.1)"; "ZEDEC 25 TO BR INSTR FUN GEN (28.61.71.1)" |
| "Z 26 (28.60.14.1)" | "ZEDEC 26 TO DIRECT IX INSTR DEC CKTS (28.61.41.1 - 28.61.44.1)"; "ZEDEC 26 TO CL DEC CKTS (28.61.11.1)"; "ZEDEC 26 TO BR INSTR DEC CKTS (28.26.70.1)" (sic); "ZEDEC 26 TO BR INSTR FUN GEN (28.61.11.1)" (sic) |
| "Z 27 (28.60.14.1)" | "ZEDEC 27 TO BR INSTR FUN GEN (28.61.71.1)"; "ZEDEC 27 TO CL DEC CKTS (28.61.11.1)"; "ZEDEC 27 TO BR INSTR DEC CKTS (28.61.70.1)" |
| "Z 28 (28.60.14.1)" | "ZEDEC 28 TO IMMIX INSTR DEC CKTS (28.61.31.1- 28.61.33.1)"; "ZEDEC 28 TO INSTR EX FUN GEN (28.61.74.1)"; "ZEDEC 28 TO BR INSTR DEC CKTS (28.61.70.1)"; "ZEDEC 28 TO BR INSTR DEC FUN GEN (28.61.71.1)" |
| "Z 29 (28.60.14.1)" | "ZEDEC 29 TO IMM IX INSTR DEC CKTS (28.61.31.1 - 28.61.34.1)"; "ZEDEC 29 TO 1ST LEVEL OF IMM CKT (28.61.36.1)"; "ZEDEC 29 TO BR INSTR DEC FUN GEN (28.61.71.1)"; "ZEDEC 29 TO INSTR EX FUN GEN (28.61.74.1)" |
| (unconditional, after Z 29) | "COND ZLIF TON CKT (28.15.05.1)" |
| "Z 30 (28.60.14.1)" | "ZEDEC 30 TO IMM IX INSTR DEC CKT (28.61.31.1 - 28.61.34.1)"; "ZEDEC 30 TO I BOX IND TSTR CKT (28.52.11.1)" |
| "Z 31 (28.60.14.1)" | "ZEDEC 31 TO IMM IX INSTR DEC CKT (28.61.31.1 - 28.61.34.1)" |

##### 5. Bottom row (lower bus)
| # | condition | action(s) |
|---|---|---|
| B1 | "SET IDC ON IAUC ERR • ~INH IAUC ~ERR TO IDC (28.51.01.1)" (overbar over "INH IAUC" and "ERR TO IDC"), YES | "SET ZLIDC ON IAUC ERR (28.51.03.1)" |
| B2 | "SBC • SET ZRAD + ZLAD (28.51.04.1)", YES | "TON ZLAD (28.51.04.1)" |
| B3 | "ZLAD ON (28.51.04.1)", YES | "ZLAD + ZRAD NOOP (28.61.75.1)"; then hexagon "GI IEI TO LA (28.51.04.1)" YES -> "SET LAAD (28.25.20.1)" |
| B4 | "SBC • EXT EXID RST Z IDC (28.51.02.1)", YES | "RESET ZRIRC (28.51.02.1)" |
| B5 | "ZLIDC ON (28.51.03.1)", YES -> hexagon "GT IET TO LA (28.51.02.1)," YES | "IDC TO LA IJ (28.25.10.1)" |
| B6 | "Z18 (28.60.15.1)", YES | "Z18 + Z50 TO MEM AREA DEC CKTS (28.61.77.1)" |

##### 6. Step table (summary)
| step | condition (PRINTED) | action (PRINTED) | ALD | notes |
|---|---|---|---|---|
| DEC on | IEX COMP RST • SAC • ZL IHW; or YR IHW • SBC • NOT IHW EX F • YR-ZL E | TON ZL DECODE (DEC) TGR | 28.27.30.1 | IHW |
| DEC | (always) | I EX USE ZL TO FR 17 ...; BLOCK ZL DEC TOF TGR TOF; BLOCK DEC ZR; BLOCK USE ZR; BLOCK I EX USE ZR | 28.67.12.1, 28.27.30.1, 28.60.11.1 | [KEY] block |
| DEC | Z18 | CND SPND INTLK TGR TON; GEN I EX IN PROG + RCVR TO YR; GEN OA 18 | 28.42.44.1, 28.67.13.1 | [KEY] suspend interlock, recover |
| DEC | XS ADR CKK • SET ZLIDC ON XAC (or 4 other error conditions) | TON ZLIDC | 28.51.03.1 | [KEY] XS |
| DEC | Z17..Z31 bits | ZEDEC nn to branch / I-box indicator / CL / MIGC / direct-IX / IMM-IX / TMT-SWAP / EX FUN GEN decoders | 28.60.x, 28.61.x, 28.52.x | |
| DEC | ZLAD ON then GI IEI TO LA | ZLAD + ZRAD NOOP; SET LAAD | 28.61.75.1, 28.25.20.1 | [KEY] LA |
| DEC | ZLIDC ON then GT IET TO LA | IDC TO LA IJ | 28.25.10.1 | |

##### 7. Named items
- Triggers: ZL DECODE (DEC) TGR, ZL IHW TGR (TOF), MOD ZL M TGR (TOF), SPND INTLK TGR (CND ... TON), ZLIDC, ZRIDC, ZLAD, ZRAD, ZLIF, RLLI E, OLLIE, ZLNA/ZLXA/ZLSA, ZRIRC.
- Counter: IAUC ("SET IDC ON IAUC ERR", "INH IAUC ERR TO IDC"). No timer.
- Registers / fields: ZL, ZR, Z 0-31, Z50, ZOA, ICIB (0-23, 60-63), YR, LA (LAAD, LA IJ), XS (XS ADR CKK), XAC, IDC.
- Others: SAC, SAR, SBC, BAC, BI, BB, MC, MEM CKK, LA PAR ERR, I PAR ERR, UNCOR ERR, IEX / I EX, OA 17/18, MIGC, TMT, SWAP.

##### 8. TIME
PRINTS NO TIME.

##### 9. [KEY] items (verbatim)
- XS: "XS ADR CKK • SET ZLIDC ON XAC (28.51.03.1)" -> "TON ZLIDC (28.51.03.1)". (DERIVED: an index-storage address check sets the ZL instruction-decode-check indicator; no XS READ and no "updated" indicator condition appears.)
- Suspend interlock / recovery: "Z18 (28.60.13.1)" -> "CND SPND INTLK TGR TON (28.42.44.1)" and "GEN I EX IN PROG + RCVR TO YR (28.42.44.1)" (same 28.42 ALD group as STORE WAIT 28.42.51.1 and IRCY 28.42.72.1).
- Block: "BLK DEC (28.60.11.1)"; "BLOCK DEC ZR", "BLOCK USE ZR", "BLOCK I EX USE ZR" (28.60.11.1); "BLOCK ZL DEC TOF TGR TOF (28.27.30.1)".
- LA: "SET LAAD (28.25.20.1)", "IDC TO LA IJ (28.25.10.1)", "GI IEI TO LA", "GT IET TO LA".
- IHW: "IEX COMP RST • SAC • ZL IHW", "YR IHW • SBC • NOT IHW EX F • YR-ZL E", "TOF ZL IHW TGR".
- No STORE WAIT, no priority test, no LAAR, forwarding or houseclean.

##### 10. Could not read / uncertain
- U3 wiring (BLK DEC YES into the decode bus) is transcribed as drawn; may be a drafting artifact.
- ALD "(28.16.13.1)" on Z 20 and "(28.26.70.1)" / "(28.61.11.1)" on two Z 26 boxes are read as printed (probably misprints of 28.60.13.1 / 28.61.70.1 / 28.61.71.1).
- "GI IEI TO LA" vs "GT IET TO LA": the first reads "GI IEI"; possibly "GT IEI".
- Z19 hexagon: YES label not printed.

### Appendix C. Figs 3.1.18-3.1.24 (reader C)

#### Figure 3.1.18 — ZL FL PT TRIGGER AND ZL FP 1 TRIGGER

- PDF page 82; printed page **1-37/1-38**; issue date at foot **2/1/62**; header "M3-04-3  I UNIT FLOW DIAGRAMS".
- Applicability note PRINTED (lower right of left half): "CPU 7101 SER. NO. 30,004 AND HIGHER".
- Read from 300 dpi render rotated upright, with 450 dpi zooms of the large hexagons. Box text is rotated 90 deg on the page.
- Notation: `X~` = X with an overbar (PRINTED overbar). "•" = AND dot as printed.

##### 1. Boxes (PRINTED), in diagram order

###### Entry / ZL FL PT TGR
- HEX: "CD 1Y-ZL • NOT HW CL 1Y • YR-ZL + CD 2Y-ZL • YR-ZL 2Y • NO HW CL 2Y (28.26.62.1)" — exit (no YES label printed) -> rect below. (The "1" glyphs print as "I"; read as 1Y, DERIVED.)
- RECT: "ZL FL PT TGR (28.26.62.1)" (the trigger; DERIVED: turned on by the hexagon above).
- Off the ZL FL PT TGR output (three actions in parallel):
  - RECT: "COND FP Z ALT TGR TON (28.27.32.1)"
  - RECT: "TOF ZR WAS IHW TGR (28.15.51.1)"
  - RECT: "COND XF + DEC ZL TON CKT (28.15.50.1)"
- HEX: "1Y53~ • 1Y55 • 1Y57 + 1Y53~ • 1Y56~ • 1Y57~ + 1Y54~ • 1Y56~ • 1Y57~ + 1Y53 • 1Y54~ • 1Y56 • 1Y57~ + 1Y55~ • 1Y56~ + MULT AND ADD + 1Y54~ • 1Y55 • 1Y57~ • FPCL1YR • SBC • CD1Y ZL • YR - ZLE (28.26.52.1)" — YES -> "TON".
- HEX: "SET ZL FPI (28.26.52.1)" — YES -> joins the same TON line (DERIVED: OR'd with the hex above).
- Label "TON" -> RECT: "ZL FPI TGR (28.26.52.1)" (PRINTED "FPI"; this is the ZL FP 1 trigger of the title).

###### Off the ZL FP1 TGR output bus — left column (each hexagon's YES exit only; no NO exits printed)
1. HEX "NOT IHW E • NOT ZL MOD R • YR-ZL M (28.15.32.1)" YES -> HEX "FP Z ALT TGR ON (28.27.32.1)" YES ->
   - RECT "FP RDY ZL TO LA CONT COMMON COM CKTS (28.20.21.1)"
   - RECT "COND FP INCOMPL TGR TON CKT (28.42.53.1)"
2. HEX "MOD ZL E • FW NOT ST + PROG IX (28.15.41.1)" (overbar over "FW NOT ST +" and "PROG IX"; extent of the bar DERIVED) YES -> RECT "Z 0 - 17 ABB PREP (28.96.03.1)"
3. HEX "MOD ZL E (28.15.41.1)" YES -> RECT "HOT 1 TO ABB P2 (28.96.41.1)"
4. HEX "MOD ZL E • MOD ZL M (28.15.41.1)" YES -> RECT "GT AOB 18 TO ZL (28.27.50.1)"
5. HEX "MOD ZL M (28.15.41.1)" YES -> RECT "INSTR PREP COMPL ZL (28.27.32.1)"; RECT "BLOCK MOD ZLM TGR TOF (28.15.40.1)"
6. HEX "FPL 3 M~ • ALLOW LAST LD (28.23.00.1)" YES -> RECT "COND FPL 3 TON CKT (28.13.31.1)"

###### Off the bus — middle-left column
1. HEX "FPL 3 E TGR ON (28.13.32.1)" YES -> RECT "GT ZLOC TO LAOC (28.21.60.1)"; RECT "Z 0 - 17 TO MAB (28.21.60.1)" (the YES line runs up to GT ZLOC and down to Z 0-17 TO MAB)
2. HEX "FPL 4 E • ZL XS LTH • (28.13.42.1)" (trailing "•" as printed) YES -> RECT "X 0 - 63 TO XY ICIB (28.21.61.1)"
3. HEX "ZL INST PREP COMP • ZL EQ 1 • XOF1 E TGR ON (28.12.12.1)" YES -> RECT "XOF1 TC FTH (24.00.09.1)"
4. HEX "ZL INST PREP COMP • ZL NOT EQ 1 • XOF1 E TGR ON (28.12.12.1)" YES -> RECT "XOF1 A Z 13 - 17 • P TO XAB (28.86.56.1)"
5. HEX "ZL INT LTH (28.23.10.1)" YES -> RECT "COND FPL 4 TON CKT (28.13.41.1)"; and YES also feeds a horizontal bus carrying:
   - HEX "FPL 4 E TGR ON (28.13.42.1)" YES -> RECT "Z 0 - 17 TO MAB (28.21.60.1)"
   - HEX "ZL INST PREP COMP • ZL INT FPL CL 1+3+4+6 (28.13.41.1)" YES -> RECT "COND FPL 4 TON CKT (28.13.41.1)"
   - HEX "FPL 4 E TGR ON (28.24.81.1)" YES -> RECT "SET LA INT FTH (36.03.02.1)"
   - HEX "FPL 4 E TGR ON • SBC (28.13.43.1)" YES -> and HEX "FPL 4 M•E TGR ON (28.13.43.1)" YES -> (joined) RECT "TYPE 3 LD TO LA (28.21.74.1)"; RECT "TYPE 3 LD TO BCU (28.21.74.1)"
6. HEX "ZL XS LTH" (NO ALD reference printed) -> bus carrying:
   - HEX "FPL 4 E • M" (NO ALD printed) -> RECT "I CHKR CYC E • M (38.03.03.1)"; RECT "I CHK PAR (34.08.11.1)"
   - HEX "FPL 4 E • M (28.13.43.1)" and HEX "FPL 4 E • SBC (28.13.43.1)" -> (joined) RECT "TYPE 1 LD TO LA (38.03.01.1)"
   (No YES labels printed on these three hexagons or on ZL XS LTH.)

###### Off the bus — middle-right column
1. HEX "FPL AD INNIB DF + DS - NOT ZL 0 - 15 • NOT ZL 16 - 31 • IRPT ENBLD (28.23.11.1)" — a bar is printed between line 1 and line 2: it is either an underline of "FPL AD INNIB" or an overbar on "DF + DS" (ambiguous; overbar on "FPL AD INNIB" is also printed). YES -> RECT "FPL 3 PRECND LA DF (28.13.33.1)" and -> HEX "DF MASK ONE (28.23.11.1)" YES -> RECT "FPL 3 PRECND LA NOP FR ALARM (28.13.33.1)"
2. HEX "FPL 3 • NO CANCEL • FPL 3 M • MNT MD ZL (28.13.33.1)" YES -> RECT "FPL 3 PNL KEY REQ (28.21.71.1)"

###### Off the bus — right column (a vertical line from the top of the sheet down)
1. HEX "ZL ADDR 8 (28.20.08.1)" YES -> RECT "I CHK REQ (28.27.32.1)"; RECT "BLOCK ZL XS LTH SIG (28.20.41.1)"
2. HEX "ZL ADDR 8 LTH • FPL 4E • NM (28.13.42.1)" YES -> RECT "I GEN PARITY (28.44.14.1)"
3. HEX "ZL ADDR 8 LTH • FPR 4E (28.24.82.1)" YES -> RECT "SET LA INT STORE TAG (28.24.82.1)"; RECT "SET LA EXT STORE TAG (28.24.82.1)"
4. HEX "IRPT EN • ZL 1 + 2 + 3 (28.23.20.1)" YES -> RECT "COND LA DF GEN CKTS (28.25.30.1)"
5. RECT "COND XOF1 E TON CKT (28.12.11.1)" (unconditional off the line)
6. RECT "COND FPL 3 TON CKT (28.13.31.1)" (unconditional)
7. RECT "COND FPL 4 TON CKT (28.13.41.1)" (unconditional)
8. HEX "ZL ADDR 8 LTH (28.20.30.1)" YES -> RECT "BLOCK ZL EXT OR ZLXS SIGNALS (28.20.30.1)"

##### 2. Structure
- This sheet has NO E / E.M / M phase-line sequencer bar. It is a two-trigger tree: ZL FL PT TGR (TON on the "CD 1Y-ZL ..." hexagon, 28.26.62.1) and ZL FP1 TGR (TON on the 1Y53..1Y57 decode hexagon OR "SET ZL FPI", 28.26.52.1). Everything else hangs off the ZL FP1 TGR output as condition -> action pairs.
- TOF of ZL FL PT TGR / ZL FP1 TGR: NOT PRINTED on this sheet. The only TOF printed is "TOF ZR WAS IHW TGR" and "BLOCK MOD ZLM TGR TOF".
- Phase-qualified conditions appear inside hexagon text: "FPL 3 E", "FPL 3 M", "FPL 3 M~", "FPL 4 E", "FPL 4 M•E", "FPL 4 E • M", "MOD ZL E", "MOD ZL M", "IHW E", "XOF1 E".

##### 3. Step table
| step | condition (PRINTED) | action (PRINTED) | ALD | notes |
|---|---|---|---|---|
| ZL FL PT TON | CD 1Y-ZL • NOT HW CL 1Y • YR-ZL + CD 2Y-ZL • YR-ZL 2Y • NO HW CL 2Y | ZL FL PT TGR | 28.26.62.1 | |
| ZL FL PT on | — | COND FP Z ALT TGR TON; TOF ZR WAS IHW TGR; COND XF + DEC ZL TON CKT | 28.27.32.1; 28.15.51.1; 28.15.50.1 | |
| ZL FP1 TON | 1Y53..57 decode + MULT AND ADD + ... • FPCL1YR • SBC • CD1Y ZL • YR - ZLE; or SET ZL FPI | ZL FPI TGR | 28.26.52.1 | |
| FP1 | NOT IHW E • NOT ZL MOD R • YR-ZL M, then FP Z ALT TGR ON | FP RDY ZL TO LA CONT COMMON COM CKTS; COND FP INCOMPL TGR TON CKT | 28.20.21.1; 28.42.53.1 | **[KEY]** ZL -> LA transfer |
| FP1 | MOD ZL E • (FW NOT ST + PROG IX)~ | Z 0-17 ABB PREP | 28.96.03.1 | |
| FP1 | MOD ZL E | HOT 1 TO ABB P2 | 28.96.41.1 | |
| FP1 | MOD ZL E • MOD ZL M | GT AOB 18 TO ZL | 28.27.50.1 | |
| FP1 | MOD ZL M | INSTR PREP COMPL ZL; BLOCK MOD ZLM TGR TOF | 28.27.32.1; 28.15.40.1 | |
| FP1 | FPL 3 M~ • ALLOW LAST LD | COND FPL 3 TON CKT | 28.13.31.1 | |
| FP1 | FPL 3 E TGR ON | GT ZLOC TO LAOC; Z 0-17 TO MAB | 28.21.60.1 | **[KEY]** op code ZL -> LA |
| FP1 | FPL 4 E • ZL XS LTH • | X 0-63 TO XY ICIB | 28.21.61.1 | |
| FP1 | ZL INST PREP COMP • ZL EQ 1 • XOF1 E TGR ON | XOF1 TC FTH | 24.00.09.1 | |
| FP1 | ZL INST PREP COMP • ZL NOT EQ 1 • XOF1 E TGR ON | XOF1 A Z 13-17 • P TO XAB | 28.86.56.1 | |
| FP1 | ZL INT LTH | COND FPL 4 TON CKT, then the FPL 4 sub-bus | 28.23.10.1 / 28.13.41.1 | |
| ZL INT LTH | FPL 4 E TGR ON | Z 0-17 TO MAB | 28.13.42.1 / 28.21.60.1 | **[KEY]** FP load fetch address |
| ZL INT LTH | ZL INST PREP COMP • ZL INT FPL CL 1+3+4+6 | COND FPL 4 TON CKT | 28.13.41.1 | |
| ZL INT LTH | FPL 4 E TGR ON | SET LA INT FTH | 28.24.81.1 / 36.03.02.1 | **[KEY]** |
| ZL INT LTH | FPL 4 E TGR ON • SBC; FPL 4 M•E TGR ON | TYPE 3 LD TO LA; TYPE 3 LD TO BCU | 28.13.43.1 / 28.21.74.1 | **[KEY]** |
| FP1 | ZL XS LTH -> FPL 4 E • M | I CHKR CYC E • M; I CHK PAR | —; 38.03.03.1; 34.08.11.1 | no ALD on the two hexes |
| FP1 | ZL XS LTH -> FPL 4 E • M; FPL 4 E • SBC | TYPE 1 LD TO LA | 28.13.43.1 / 38.03.01.1 | **[KEY]** |
| FP1 | FPL AD INNIB / DF+DS - NOT ZL 0-15 • NOT ZL 16-31 • IRPT ENBLD | FPL 3 PRECND LA DF; (DF MASK ONE) FPL 3 PRECND LA NOP FR ALARM | 28.23.11.1 / 28.13.33.1 | |
| FP1 | FPL 3 • NO CANCEL • FPL 3 M • MNT MD ZL | FPL 3 PNL KEY REQ | 28.13.33.1 / 28.21.71.1 | |
| FP1 | ZL ADDR 8 | I CHK REQ; BLOCK ZL XS LTH SIG | 28.20.08.1; 28.27.32.1; 28.20.41.1 | |
| FP1 | ZL ADDR 8 LTH • FPL 4E • NM | I GEN PARITY | 28.13.42.1 / 28.44.14.1 | |
| FP1 | ZL ADDR 8 LTH • FPR 4E | SET LA INT STORE TAG; SET LA EXT STORE TAG | 28.24.82.1 | **[KEY]** store tag into LA |
| FP1 | IRPT EN • ZL 1 + 2 + 3 | COND LA DF GEN CKTS | 28.23.20.1 / 28.25.30.1 | |
| FP1 | (none) | COND XOF1 E TON CKT; COND FPL 3 TON CKT; COND FPL 4 TON CKT | 28.12.11.1; 28.13.31.1; 28.13.41.1 | |
| FP1 | ZL ADDR 8 LTH | BLOCK ZL EXT OR ZLXS SIGNALS | 28.20.30.1 | |

##### 4. Named counters / timers / triggers / registers
- Triggers: ZL FL PT TGR, ZL FPI (FP1) TGR, FP Z ALT TGR, ZR WAS IHW TGR, FP INCOMPL TGR, MOD ZLM TGR, FPL 3 E TGR, FPL 4 E TGR, FPL 4 M•E TGR, XOF1 E TGR.
- Levels/sequencers named: FPL 3, FPL 4 (FP look-ahead levels, DERIVED), XOF1, MOD ZL (E, M, R).
- Registers/buses: ZL, ZR, YR, 1Y53..1Y57, 2Y, Z 0-17, Z 13-17, X 0-63, XY, ICIB, MAB, XAB, ABB (P2), AOB 18, ZLOC, LAOC, LA, BCU.
- Counters: none named. Timers: none named.

##### 5. TIME
PRINTS NO TIME (no clock, cycle count, A/B pulse or duration on the sheet).

##### 6. [KEY] items (verbatim)
- **[KEY]** "FP RDY ZL TO LA CONT COMMON COM CKTS (28.20.21.1)" under "FP Z ALT TGR ON" — FP instruction ZL -> look-ahead transfer.
- **[KEY]** "GT ZLOC TO LAOC (28.21.60.1)" with "Z 0 - 17 TO MAB (28.21.60.1)" under "FPL 3 E TGR ON (28.13.32.1)".
- **[KEY]** "SET LA INT STORE TAG (28.24.82.1)", "SET LA EXT STORE TAG (28.24.82.1)" under "ZL ADDR 8 LTH • FPR 4E (28.24.82.1)".
- **[KEY]** "SET LA INT FTH (36.03.02.1)" under "FPL 4 E TGR ON (28.24.81.1)".
- **[KEY]** "TYPE 3 LD TO LA (28.21.74.1)", "TYPE 3 LD TO BCU (28.21.74.1)" under "FPL 4 E TGR ON • SBC" / "FPL 4 M•E TGR ON (28.13.43.1)"; "TYPE 1 LD TO LA (38.03.01.1)" under "FPL 4 E • M" / "FPL 4 E • SBC".
- No STORE WAIT, pseudo-store, recovery, houseclean, LAAR, store-address compare, IC FETCH PRIORITY or block/suspend text on this sheet (only "BLOCK ZL XS LTH SIG", "BLOCK ZL EXT OR ZLXS SIGNALS", "BLOCK MOD ZLM TGR TOF").

##### 7. Not read / uncertain
- The bar between "FPL AD INNIB" and "DF + DS" (28.23.11.1 hexagon): underline vs overbar ambiguous. Fig 3.1.20 prints the same 28.23.11.1 term as "FPL AD~ INHBT DF~ + DS~", so the DERIVED reading here is NOT(FPL AD INHIB DF + DS) • NOT ZL 0-15 • NOT ZL 16-31 • IRPT ENBLD.
- Extent of the overbar in "MOD ZL E • FW NOT ST + PROG IX": spans the two lines after "MOD ZL E •"; exact extent DERIVED.
- "ZL XS LTH" and the first "FPL 4 E • M" hexagons print no ALD reference (not illegible: absent).

#### Figure 3.1.19 — ZL FP2 TRIGGER

- PDF page 83; printed page **1-39/1-40**; issue date **2/1/62**; header "M3-04-3  I UNIT FLOW DIAGRAMS".
- Applicability PRINTED: "CPU 7101 SER. NO. 30,004 AND HIGHER".
- Unlike its neighbours this sheet is printed UPRIGHT (box text horizontal on the page). Read at 300 dpi; decode hexagon and the BLOCK FP RDY hexagon at 450 dpi.
- Notation: `X~` = overbar printed over X.

##### 1. Boxes (PRINTED)

###### Entry
- HEX "SET ZL FP 2 (28.26.53.1)" YES -> TON line.
- HEX "1Y53 • 1Y54 • 1Y55 (1Y56~ • 1Y57~) + 1Y53 • 1Y54 • 1Y55~ • 1Y56 • 1Y57 • COND FP CL (28.26.53.1)" YES -> TON line. (Bars over 1Y56 and 1Y57 inside the parentheses, and over the second 1Y55; exact bar extent inside the parentheses DERIVED.)
- "TON" -> RECT "ZL FP 2 TGR (28.26.53.1)".

###### Left column off the ZL FP 2 TGR bus (YES exits only)
1. HEX "NOT IHWE • NOT ZL MOD R • YR - ZL M (28.15.32.1)" YES -> HEX "FP Z ALT TGR ON (28.27.32.1)" -> RECT "FP RDY ZL TO LA CONT COMMON COM CKTS (28.20.21.1)"; RECT "COND FP INCOMPL TGR TON CKTS (28.42.53.1)" (no YES label on the FP Z ALT TGR ON exit).
2. HEX "MOD ZL E • FW NOT ST + PROG IX (28.15.41.1)" (overbar over "FW NOT ST +" and "PROG IX") YES -> RECT "Z 0 - 17 ABB PREP (28.96.03.1)"
3. HEX "MOD ZL E (28.15.41.1)" YES -> RECT "HOT 1 TO ABB P 2 (28.96.41.1)"
4. HEX "MOD ZLE • MOD ZL M (28.15.41.1)" YES -> RECT "GT AOB 18 TO ZL (28.27.50.1)"
5. HEX "MOD ZL M (28.15.41.1)" YES -> RECT "INSTR PREP COMPL ZL (28.27.32.1)"; RECT "BLOCK MOD ZL M TGR TOF (28.15.40.1)" (printed "TOR TOF"? the glyph reads "TOR" — DERIVED: "TGR", a print defect)

###### Centre
- HEX "INSTR PREP COMPL ZL • FP Z ALT ON (28.27.32.1)" — **NO** exit (printed "NO") -> HEX "NO I CHKR REQ • NO T2 CHKR REQ • NO T1 CHKR REQ • OK TO I CHK IC • NO I CHKR REQ 3 (28.41.50.1)" -> (no YES label printed) RECT "COND IWC1 TON CKTS (28.41.51.1)"; RECT "COND IWC2 TON CKTS (28.41.61.1)". The YES exit of the INSTR PREP COMPL hexagon is not drawn.
- HEX "BLOCK FP RDY / CANCEL FPR3E • ZL INSTR PREP COMPL (28.27.32.1)" — a bar is printed between "BLOCK FP RDY" and "CANCEL FPR3E"; the upper bar coincides with the hexagon edge. Read as overbar on "CANCEL FPR3E" (and possibly on "BLOCK FP RDY"); ambiguous. Exit (no YES label) -> RECT "COND FPL 4 TON CKT (28.13.41.1)".
- Bus carrying:
  - HEX "SBC • FPL 4 E TGR ON (28.13.43.1)" YES, and HEX "FPL 4 E TGR ON • FPL 4 M TGR ON (28.13.43.1)" YES -> (joined) RECT "TYPE 1 LD TO LA (28.21.72.1)"
  - HEX "ZL NOT ADR 8 • FPL4E • NM (28.13.42.1)" -> RECT "I CHK PARITY (28.98.07.1)"

###### Right column
1. HEX "FPL 4 E TGR ON (28.13.42.1)" -> RECT "1 TO ICIB P POS 3 - 8 (28.21.20.1)"; RECT "Z 0 - 23 TO ICIB (28.21.61.1)"
2. HEX "FPL 4 E • FPL 4 NM (28.13.42.1)" -> RECT "I CHKR CYC E • NM (38.03.03.1)"; RECT "I CHKR PAR (34.08.11.1)"
3. RECT "BLOCK GEN OF PRE CND LA AD • FPL AD INHBT DF + DS (28.23.20.1)" (unconditional off the line)
4. HEX "Z 24 (28.23.00.1)" YES -> HEX "IF INHBT OP • GT FPL IND TO LA (28.25.01.1)" YES -> RECT "OP SET LANOP (28.25.40.1)"

##### 2. Structure
- No E / E.M / M sequencer bar. Single trigger ZL FP 2 TGR, TON by "SET ZL FP 2" OR the 1Y53..1Y57 • COND FP CL decode (both 28.26.53.1). No TOF of ZL FP 2 TGR printed.
- The only NO exit on the sheet is on "INSTR PREP COMPL ZL • FP Z ALT ON".

##### 3. Step table
| step | condition (PRINTED) | action (PRINTED) | ALD | notes |
|---|---|---|---|---|
| TON | SET ZL FP 2; or 1Y53•1Y54•1Y55(1Y56~•1Y57~) + 1Y53•1Y54•1Y55~•1Y56•1Y57 • COND FP CL | ZL FP 2 TGR | 28.26.53.1 | |
| FP2 | NOT IHWE • NOT ZL MOD R • YR - ZL M; FP Z ALT TGR ON | FP RDY ZL TO LA CONT COMMON COM CKTS; COND FP INCOMPL TGR TON CKTS | 28.15.32.1 / 28.27.32.1 / 28.20.21.1 / 28.42.53.1 | **[KEY]** ZL->LA |
| FP2 | MOD ZL E • (FW NOT ST + PROG IX)~ | Z 0-17 ABB PREP | 28.96.03.1 | |
| FP2 | MOD ZL E | HOT 1 TO ABB P 2 | 28.96.41.1 | |
| FP2 | MOD ZLE • MOD ZL M | GT AOB 18 TO ZL | 28.27.50.1 | |
| FP2 | MOD ZL M | INSTR PREP COMPL ZL; BLOCK MOD ZL M TGR TOF | 28.27.32.1; 28.15.40.1 | |
| FP2 | NOT (INSTR PREP COMPL ZL • FP Z ALT ON), then NO I CHKR REQ • NO T2 CHKR REQ • NO T1 CHKR REQ • OK TO I CHK IC • NO I CHKR REQ 3 | COND IWC1 TON CKTS; COND IWC2 TON CKTS | 28.41.50.1; 28.41.51.1; 28.41.61.1 | |
| FP2 | BLOCK FP RDY / CANCEL FPR3E~ • ZL INSTR PREP COMPL | COND FPL 4 TON CKT | 28.27.32.1 / 28.13.41.1 | |
| FP2 | SBC • FPL 4 E TGR ON; FPL 4 E TGR ON • FPL 4 M TGR ON | TYPE 1 LD TO LA | 28.13.43.1 / 28.21.72.1 | **[KEY]** |
| FP2 | ZL NOT ADR 8 • FPL4E • NM | I CHK PARITY | 28.13.42.1 / 28.98.07.1 | |
| FP2 | FPL 4 E TGR ON | 1 TO ICIB P POS 3-8; Z 0-23 TO ICIB | 28.13.42.1 / 28.21.20.1 / 28.21.61.1 | |
| FP2 | FPL 4 E • FPL 4 NM | I CHKR CYC E • NM; I CHKR PAR | 28.13.42.1 / 38.03.03.1 / 34.08.11.1 | |
| FP2 | (none) | BLOCK GEN OF PRE CND LA AD • FPL AD INHBT DF + DS | 28.23.20.1 | |
| FP2 | Z 24; IF INHBT OP • GT FPL IND TO LA | OP SET LANOP | 28.23.00.1 / 28.25.01.1 / 28.25.40.1 | **[KEY]** LANOP |

##### 4. Named items
- Triggers: ZL FP 2 TGR, FP Z ALT TGR, FP INCOMPL TGR, MOD ZL M TGR, FPL 4 E TGR, FPL 4 M TGR, IWC1, IWC2 (DERIVED: triggers, "COND IWCn TON CKTS").
- Registers/buses: ZL, YR, 1Y53..1Y57, Z 0-17, Z 0-23, Z 24, ICIB, ABB (P 2), AOB 18, LA. LAOP code: LANOP ("OP SET LANOP").
- Check requests: I CHKR REQ, T1 CHKR REQ, T2 CHKR REQ, I CHKR REQ 3, I CHKR CYC, I CHKR PAR, I CHK PARITY.
- No counters or timers named.

##### 5. TIME
PRINTS NO TIME.

##### 6. [KEY] items (verbatim)
- **[KEY]** "FP RDY ZL TO LA CONT COMMON COM CKTS (28.20.21.1)".
- **[KEY]** "TYPE 1 LD TO LA (28.21.72.1)" under "SBC • FPL 4 E TGR ON" / "FPL 4 E TGR ON • FPL 4 M TGR ON (28.13.43.1)".
- **[KEY]** "Z 24 (28.23.00.1)" -> "IF INHBT OP • GT FPL IND TO LA (28.25.01.1)" -> "OP SET LANOP (28.25.40.1)".
- No STORE WAIT, recovery, houseclean, LAAR, store compare, IC FETCH PRIORITY text.

##### 7. Not read / uncertain
- Bar placement in the "BLOCK FP RDY / CANCEL FPR3E" hexagon (28.27.32.1): which line(s) carry the overbar is ambiguous.
- "BLOCK MOD ZL M TOR TOF": third word prints as "TOR"; read as TGR (DERIVED).
- Bar extent inside "(1Y56 • 1Y57)" (28.26.53.1).

#### Figure 3.1.20 — ZL FP3 TRIGGER

- PDF page 84; printed page **1-41/1-42**; issue date **2/1/62**; header "M3-04-3  I UNIT FLOW DIAGRAMS".
- Applicability PRINTED: "CPU 7101 SER. NO. 30,004 AND HIGHER".
- Landscape fold-out, box text rotated 90 deg; read upright at 300 dpi, labels checked at 450 dpi.
- Notation: `X~` = overbar printed over X.

##### 1. Boxes (PRINTED)

###### Entry
- HEX "SET ZL FP 3 (28.26.53.1)" YES -> TON line.
- HEX "1Y53 • 1Y54 • 1Y55 • 1Y56 1Y57~ + 1Y55~ • 1Y56 • 1Y57 • COND FPCL (28.26.53.1)" YES -> TON line.
- "TON" -> RECT "ZL FP 3 TGR (28.26.53.1)".

###### Right of the trigger (off the line just below ZL FP 3 TGR)
- HEX "ZL EQ 1 (28.23.20.1)" YES -> RECT "PRE COND LA AD (28.25.20.1)"
- HEX "FPL 4 E TGR ON (28.13.43.1)" YES -> a vertical line carrying:
  - HEX "PROGRAM STORE COMPARE (28.42.71.1)" YES -> RECT "TON PIRCY TGR (28.42.71.1)"  **[KEY]**
  - HEX "PROGRAM STORE COMPARE (28.42.72.1)" YES -> RECT "TON I RCY REQ TGR (28.42.72.1)"  **[KEY]**
  - HEX "ZOAR EQ 11 + 12 + 16 - 31 (28.42.51.1)" YES -> RECT "TON STORE WAIT TGR (28.42.51.1)"; RECT "BLOCK STORE WAIT TGR TOF (28.42.51.1)"; RECT "TON I RCY REQ TGR (28.42.72.1)"  **[KEY]**
  - HEX "ZL EQ 1' (28.23.20.1)" (a tick after the "1"; print speck or prime — the other hexagon reads plain "ZL EQ 1") YES -> a vertical line carrying, unconditionally:
    - RECT "BLOCK GEN OF FPL 1 COND DF + DS (28.13.12.1)"
    - RECT "BLOCK GEN OF FPL 3 COND LA DF (28.13.33.1)"
    - RECT "BLOCK SETTING OF LA DS (28.25.20.1)"
    - RECT "BLOCK GEN OF DS SET LANOP (28.25.20.1)"
    - RECT "BLOCK GEN OF SET LA DF (28.25.30.1)"
    - RECT "BLOCK GEN OF DF SET LANOP (28.25.30.1)"
    - RECT "BLOCK GEN OF FPL 3 PRECND LA DF (28.23.11.1)"
    - RECT "BLOCK GEN OF FPL 3 PRECND LANOP FR ALARM (28.23.11.1)"
    - RECT "BLOCK GEN OF FPL 4 PRECND LA DS NOP (28.23.11.1)"
    - and HEX "IF INHBT AD~ • GT FPL IND TO LA (28.25.20.1)" (bar over "IF INHBT AD") YES -> RECT "SET LA AD (33.01.05.1)"; and -> HEX "INHBT SET NOP BIT FR AD + DF~ (28.25.20.1)" (bars over both lines) YES -> RECT "AD SET LANOP (28.25.40.1)"

###### Left column off the ZL FP 3 TGR bus
1. HEX "NOT IHW E • NOT ZL MOD R • YR - ZL M (28.15.32.1)" YES -> HEX "FP Z ALT TGR ON (28.27.32.1)" YES -> RECT "FP RDY ZL TO LA CONT COMMON COM CKTS (28.20.21.1)"; RECT "COND FP INCOMPL TGR TON CKTS (28.42.53.1)"
2. HEX "MOD ZLE • FW~ NOT~ ST~ + PROG IX~ (28.15.41.1)" YES -> RECT "Z 0 - 17 ABB PREP (28.96.03.1)"
3. HEX "MOD ZLE (28.15.41.1)" YES -> RECT "HOT 1 TO ABB P 2 (28.96.41.1)"
4. HEX "MOD ZL E • MOD ZL M (28.15.41.1)" YES -> RECT "GT AOB 18 TO ZL (28.27.50.1)"
5. HEX "MOD ZL M (28.15.41.1)" YES -> RECT "INSTR PREP COMPL ZL (28.27.32.1)"; RECT "BLOCK MOD ZL M TGR TOF (28.15.40.1)"

###### Second column off the bus
1. HEX "ZL INSTR PREP COMPL • (28.13.41.1)" (trailing "•" as printed) YES -> RECT "COND FPL 4 TON CKT (28.13.41.1)"
2. HEX "FPL 4 E TGR ON (28.13.42.1)" YES -> RECT "Z 0 - 17 TO MAB (28.21.60.1)"
3. HEX "FDL 4 E • FPL 4 M (28.13.43.1)" (PRINTED "FDL"; read FPL, DERIVED) YES, and HEX "FPL 4 E • SBC (28.13.43.1)" YES -> (joined) RECT "L T3 LD E • M TO LA (38.03.01.1)"; RECT "L T3 LD E • M TO BCU (15.01.01.1)"
4. HEX "FPL 2 M + ZOAL INT FPL CL 3 + 1 • ZL INSTR PREP COMPL (28.13.41.1)" YES -> RECT "COND FPL 4 TON CKT (28.13.41.1)"

###### Bottom bus
- HEX "ZL EXT LTH • FPL 4E (28.24.82.1)" YES -> RECT "SET LA EXT STORE TAG (28.24.82.1)"
- HEX "ZL INT LTH • FPL 4E (28.24.82.1)" YES -> RECT "SET LA INT STORE TAG (28.24.82.1)"
- HEX "IRPT ENBLD • NOT ZL 16 - 31 • NOT ZL 0 - 15 • FPL AD~ INHBT DF~ + DS~ (28.23.11.1)" (bars over "FPL AD", "INHBT DF" and "+ DS": DERIVED reading NOT(FPL AD INHBT DF + DS)) YES -> HEX "FPL 4 E • FPL 4 M (28.13.43.1)" YES -> RECT "COND LA DS FR ALARM (38.03.06.1)"
- HEX "ZL 1 + 2 + 3 IRPT ENBLD (28.23.20.1)" YES -> HEX "IF INHBT DS • GT FPL IND TO LA • FPL AD INHBT DF + DS (28.25.20.1)" YES -> RECT "SET LA DS (33.01.03.1)"; RECT "DS SET LANOP (28.25.40.1)"

##### 2. Structure
- No E / E.M / M sequencer bar. One trigger: ZL FP 3 TGR, TON by "SET ZL FP 3" OR the decode hexagon (28.26.53.1). No TOF for ZL FP 3 TGR printed.
- The store-wait / recovery logic is nested under "FPL 4 E TGR ON (28.13.43.1)", i.e. it is evaluated when the FP look-ahead load reaches FPL 4 E (DERIVED).

##### 3. Step table
| step | condition (PRINTED) | action (PRINTED) | ALD | notes |
|---|---|---|---|---|
| TON | SET ZL FP 3; or 1Y53•1Y54•1Y55•1Y56 1Y57~ + 1Y55~•1Y56•1Y57 • COND FPCL | ZL FP 3 TGR | 28.26.53.1 | |
| FP3 | ZL EQ 1 | PRE COND LA AD | 28.23.20.1 / 28.25.20.1 | |
| FP3 | FPL 4 E TGR ON; PROGRAM STORE COMPARE | TON PIRCY TGR | 28.13.43.1 / 28.42.71.1 | **[KEY]** |
| FP3 | FPL 4 E TGR ON; PROGRAM STORE COMPARE | TON I RCY REQ TGR | 28.42.72.1 | **[KEY]** I-unit recovery request |
| FP3 | FPL 4 E TGR ON; ZOAR EQ 11 + 12 + 16 - 31 | TON STORE WAIT TGR; BLOCK STORE WAIT TGR TOF; TON I RCY REQ TGR | 28.42.51.1; 28.42.51.1; 28.42.72.1 | **[KEY]** |
| FP3 | FPL 4 E TGR ON; ZL EQ 1' | nine BLOCK GEN ... boxes (see list) | 28.13.12.1 ... 28.23.11.1 | |
| FP3 | ... ZL EQ 1'; IF INHBT AD~ • GT FPL IND TO LA | SET LA AD | 28.25.20.1 / 33.01.05.1 | |
| FP3 | ... ; INHBT SET NOP BIT FR AD + DF~ | AD SET LANOP | 28.25.20.1 / 28.25.40.1 | LANOP |
| FP3 | NOT IHW E • NOT ZL MOD R • YR - ZL M; FP Z ALT TGR ON | FP RDY ZL TO LA CONT COMMON COM CKTS; COND FP INCOMPL TGR TON CKTS | 28.20.21.1; 28.42.53.1 | **[KEY]** |
| FP3 | MOD ZLE • (FW NOT ST + PROG IX)~ | Z 0-17 ABB PREP | 28.96.03.1 | |
| FP3 | MOD ZLE | HOT 1 TO ABB P 2 | 28.96.41.1 | |
| FP3 | MOD ZL E • MOD ZL M | GT AOB 18 TO ZL | 28.27.50.1 | |
| FP3 | MOD ZL M | INSTR PREP COMPL ZL; BLOCK MOD ZL M TGR TOF | 28.27.32.1; 28.15.40.1 | |
| FP3 | ZL INSTR PREP COMPL • | COND FPL 4 TON CKT | 28.13.41.1 | |
| FP3 | FPL 4 E TGR ON | Z 0-17 TO MAB | 28.13.42.1 / 28.21.60.1 | FP load address to MAB |
| FP3 | FDL[FPL] 4 E • FPL 4 M; FPL 4 E • SBC | L T3 LD E • M TO LA; L T3 LD E • M TO BCU | 28.13.43.1 / 38.03.01.1 / 15.01.01.1 | **[KEY]** |
| FP3 | FPL 2 M + ZOAL INT FPL CL 3 + 1 • ZL INSTR PREP COMPL | COND FPL 4 TON CKT | 28.13.41.1 | |
| FP3 | ZL EXT LTH • FPL 4E | SET LA EXT STORE TAG | 28.24.82.1 | **[KEY]** |
| FP3 | ZL INT LTH • FPL 4E | SET LA INT STORE TAG | 28.24.82.1 | **[KEY]** |
| FP3 | IRPT ENBLD • NOT ZL 16-31 • NOT ZL 0-15 • (FPL AD INHBT DF + DS)~; FPL 4 E • FPL 4 M | COND LA DS FR ALARM | 28.23.11.1 / 28.13.43.1 / 38.03.06.1 | |
| FP3 | ZL 1 + 2 + 3 IRPT ENBLD; IF INHBT DS • GT FPL IND TO LA • FPL AD INHBT DF + DS | SET LA DS; DS SET LANOP | 28.23.20.1 / 28.25.20.1 / 33.01.03.1 / 28.25.40.1 | |

##### 4. Named items
- Triggers: ZL FP 3 TGR, PIRCY TGR, I RCY REQ TGR, STORE WAIT TGR, FP Z ALT TGR, FP INCOMPL TGR, MOD ZL M TGR, FPL 4 E TGR.
- Registers/addresses: ZL, YR, 1Y53..1Y57, ZOAR (operand address register, compared to 11, 12, 16-31), ZOAL, Z 0-17, MAB, ABB (P 2), AOB 18, LA, BCU.
- LAOP codes: LANOP ("AD SET LANOP", "DS SET LANOP", "SET LANOP" blocks); LA indicators AD, DS, DF.
- FP look-ahead levels/phases: FPL 1, FPL 2 M, FPL 3, FPL 4 E, FPL 4 M.
- No counters, no timers.

##### 5. TIME
PRINTS NO TIME.

##### 6. [KEY] items (verbatim)
- **[KEY]** "PROGRAM STORE COMPARE (28.42.71.1)" YES -> "TON PIRCY TGR (28.42.71.1)" (under "FPL 4 E TGR ON (28.13.43.1)").
- **[KEY]** "PROGRAM STORE COMPARE (28.42.72.1)" YES -> "TON I RCY REQ TGR (28.42.72.1)".
- **[KEY]** "ZOAR EQ 11 + 12 + 16 - 31 (28.42.51.1)" YES -> "TON STORE WAIT TGR (28.42.51.1)", "BLOCK STORE WAIT TGR TOF (28.42.51.1)", "TON I RCY REQ TGR (28.42.72.1)".
- **[KEY]** "SET LA EXT STORE TAG (28.24.82.1)" under "ZL EXT LTH • FPL 4E"; "SET LA INT STORE TAG (28.24.82.1)" under "ZL INT LTH • FPL 4E".
- **[KEY]** "FP RDY ZL TO LA CONT COMMON COM CKTS (28.20.21.1)"; "L T3 LD E • M TO LA (38.03.01.1)", "L T3 LD E • M TO BCU (15.01.01.1)".
- What RELEASES store wait is NOT on this sheet: it only turns STORE WAIT TGR on and blocks its TOF.
- No LAAR, houseclean, IC FETCH PRIORITY, pseudo-store or forwarding text.

##### 7. Prior-claim check
- Prior claim "3.1.20 shows STORE WAIT": **AGREE** — PRINTED "TON STORE WAIT TGR (28.42.51.1)" and "BLOCK STORE WAIT TGR TOF (28.42.51.1)" under hexagon "ZOAR EQ 11 + 12 + 16 - 31 (28.42.51.1)", itself under "FPL 4 E TGR ON (28.13.43.1)". (Same word list 11, 12, 16-31 as claimed for 3.1.24.)

##### 8. Not read / uncertain
- "ZL EQ 1'": the tick after the 1 is either a speck or a printed prime.
- "TON PIRCY TGR": printed as one word "PIRCY" (likely P[rogram] I RCY, DERIVED); legible, not expanded.
- Bar extents in the IRPT ENBLD hexagon (28.23.11.1) and "INHBT SET NOP BIT FR AD + DF".

#### Figure 3.1.21 — ZL FP4 TRIGGER AND ZL FP6 TRIGGER

- PDF page 85; printed page **1-43/1-44**; issue date **2/1/62**; header "M3-04-3  I UNIT FLOW DIAGRAMS".
- No "CPU 7101 SER. NO." applicability note found on this sheet.
- This sheet is printed UPRIGHT (not rotated) and in a different (typewriter-style) lettering from its neighbours: "." is the AND dot, flow lines carry ARROWHEADS, and each ALD page is printed UNDER the box WITHOUT parentheses. ALDs below are quoted as printed.
- Notation: `X~` = overbar printed over X.

##### 1. Boxes (PRINTED)

###### Entry, ZL FP4
- RECT "SET ZL FP 4" 28.26.53.1 -> TON line.
- HEX "1Y53~ . 1Y55~ . 1Y56 . 1Y57~ . COND FP CL" 28.26.53.1 -> TON line.
- "TON" -> RECT "ZL FP4 TGR" 28.26.53.1.

###### Entry, ZL FP6
- HEX "1Y53 . 1Y NOT 54 . 1Y55 . 1Y56 . 1Y57 . COND FP CL" 28.26.53.1 -> TON line.
- RECT "SET ZL FP6" 28.26.53.1 -> TON line.
- "TON" -> RECT "ZL FP6 TGR" (no ALD printed under it).

###### Common
- RECT "ZL FP4 OR ZL FP6" 28.23.00.1 — entered from the ZL FP4 TGR bus (from the left) and from the ZL FP6 TGR bus (from the right).

###### ZL FP4 TGR bus — left column
1. HEX "ZL1 + 2 + 3 . IRPT ENABLED" 28.23.20.1 YES -> RECT "PRE CND LA DS" 28.25.20.1
2. HEX "ZL EQ 1" 28.23.20.1 YES -> RECT "PRE COND LA AD" 28.25.20.1
3. HEX "IRPT ENABLED . NOT ZL0-15" 28.23.11.1 YES -> RECT "PRE CND LA DS" 28.13.33.1; RECT "PRE CND LA NOP FR ALARM" 28.13.33.1
4. HEX "ZL INT + ZL ADR 8 . FPL4E" 28.24.82.1 YES -> RECT "SET LA INT STORE TAG" 28.24.82.1
5. HEX "ZL NE LTHD" 28.23.10.1 YES -> line carrying:
   - RECT "COND FPL4E TON" 28.13.41.1 (unconditional)
   - HEX "FPL4E . M" 28.13.43.1 YES and HEX "FPL4E . SBC" 28.13.43.1 YES -> (joined) RECT "TYPE 3 LOAD TO LA" 28.21.74.1; RECT "TYPE 3 LOAD TO BCU" 28.21.74.1
   - HEX "FPL4E" 28.13.42.1 YES -> RECT "Z0-17 TO MAB" 28.21.60.1

###### ZL FP4 TGR bus — second column
1. RECT "BLOCK CND LA DF" 28.13.33.1 (unconditional)
2. HEX "FPL3E AND NO CANCEL . SBC" 28.13.33.1 YES and HEX "FPL3E AND NO CANCEL . FPL3M" 28.13.33.1 YES -> (joined) RECT "TYPE 3 LOAD TO LA" 28.21.74.1; RECT "T3LD TO BCU WAIT FOR ACCEPT" 28.21.74.1  **[KEY]**
3. HEX "FPL3NM . ALLOW LAST LOAD" 28.23.00.1 YES -> RECT "COND FPL 3E TON" 28.13.31.1
4. HEX "FPL4E" (no ALD printed) YES -> line carrying:
   - HEX "ZOAL EQ 11+12+16-31" 28.42.51.1 YES -> RECT "TON STORE WAIT TGR" 28.42.51.1; RECT "TON 1RCY REQ TGR" 28.42.72.1  **[KEY]** (PRINTED "ZOAL" here; Fig 3.1.20 prints "ZOAR" for the same 28.42.51.1 test — both checked at 450 dpi)
   - HEX "PROGRAM STORE COMPARE" 28.42.71.1 YES -> RECT "TON PIRCY TGR" 28.42.71.1; RECT "TON 1RCY REQ TGR" 28.42.72.1  **[KEY]**
   (No "BLOCK STORE WAIT TGR TOF" box on this sheet, unlike 3.1.20.)

###### ZL FP4 TGR bus — third column (feeds also "ZL FP4 OR ZL FP6")
- HEX "FPL3E AND NO CANCEL" 28.13.33.1 YES (exit drawn on the LEFT) -> HEX "PROGRAM STORE COMPARE . ACCEPT OR COMPARE" 28.42.72.1 YES -> RECT "TON IRCY REQ TGR" 28.42.72.1  **[KEY]**

###### "ZL FP4 OR ZL FP6" bus — column A
1. HEX "FPL3E AND NO CANCEL" 28.24.82.1 YES -> RECT "SET LA EXT STORE TAG" 28.24.82.1
2. HEX "FPL4E" 28.24.80.1 YES -> RECT "SET LAOC 6, 8, & 9" 28.24.24.1 / 28.24.26.1; RECT "SET LAOP TAG" 36.05.01.1
3. RECT "COND FPL2E TON" 28.13.21.1 (UNCONDITIONAL: arrow straight from the column-A line)
4. HEX "FPL3E AND NO CANCEL . SBC" 28.13.33.1 YES -> RECT "MODIFIED TYPE 3 LOAD TO LA" 28.21.75.1
5. HEX "FPL3E AND NO CANCEL . FPL3M" 28.13.33.1 YES -> RECT "XFER & RESET NIDC" 28.21.73.1; RECT "MODIFIED TYPE 3 LOAD TO LA" 28.21.75.1
6. HEX "ZL ADR 8" 28.20.08.1 YES -> RECT "I CHKR REQ" 28.27.32.1; RECT "BLOCK ZL XS LTH SIGNAL" 28.20.41.1
7. RECT "COND XOF 1 E TON" 28.12.11.1 (unconditional)
8. (line continues) HEX "ZR INSTR PREP COMPLETE . ZR EQ1 . XOF1E" 28.12.12.1 YES -> RECT "XOF 1TC FETCH" 24.00.09.1

###### "ZL FP4 OR ZL FP6" bus — column B
1. HEX "ZL ADR 8 LTH . FPR2E" 28.24.82.1 YES -> RECT "SET LA EXT STORE TAG" 36.09.14.1; RECT "SET LA INT STORE TAG" 36.09.15.1
2. HEX "ZL ADDR 8 LTH . FPL2 E . NM" 28.13.22.1 YES -> RECT "I GEN PARITY" 28.44.14.1
3. HEX "NOT IC FETCH PRIORITY" 28.20.23.1 YES -> RECT "COND FPL2E TON" 28.13.21.1  **[KEY]** (no NO exit drawn)
4. RECT "BLOCK TYPE 2 LD TO LA" 28.13.33.1 (UNCONDITIONAL: arrow straight from the column-B line, below the hexagon; not on a NO exit)  **[KEY]**
5. HEX "FPL3E" 28.13.32.1 YES -> RECT "ZO-17 TO MAB" 28.21.60.1; RECT "GT ZLOC TO LAOC" 28.21.60.1  **[KEY]**
6. (line continues down and right to column C)

###### Column C (continuation of column B)
1. HEX "FPL3E AND NO CANCEL . FPL3M . MNT MD ZL4" 28.13.33.1 YES -> RECT "PANEL KEY REQUEST" 28.21.71.1
2. HEX "ZL ADR 8 LTH" 28.20.30.1 YES -> RECT "BLOCK ZL EXT OR ZL XS SIGNALS" 28.20.30.1
3. HEX "FPL4E" 28.13.42.1 YES -> RECT "BLOCK XFER OF ZLOC TO LAOC" 28.13.42.1  **[KEY]**
4. HEX "ZR INSTR PREP COMPLETE . ZR NOT EQ1 . XOF 1E" 28.12.12.1 YES -> RECT "Z13-17 . P TO XAB" 28.86.56.1

###### ZL FP6 TGR bus (and the line back to "ZL FP4 OR ZL FP6")
- HEX "ZL NE LTHD" 28.23.10.1 YES (exit on the LEFT) -> RECT "COND FPL4E TON" 28.14.41.1; HEX "FPL4E . M" 28.13.43.1 YES and HEX "FPL4E . SBC" 28.13.43.1 YES -> RECT "TYPE 3 LOAD TO LA" 28.21.74.1; RECT "TYPE 3 LOAD TO BCU" 28.21.74.1
- HEX "FPL4E" 28.24.82.1 YES -> RECT "SET LA EXT STORE TAG" 36.09.14.1
- HEX "IRPT ENABLED . ZL1 + 2 + 3" 28.23.20.1 YES -> RECT "COND LA DF" 28.25.30.1; RECT "COND LA NOP FROM DF" 28.25.30.1
- Straight down the ZL FP6 TGR line:
  1. RECT "COND FPDDE TON" 28.10.11.1 (unconditional)
  2. HEX "FPL3E AND NO. CANCEL. FPL3M" 28.13.33.1 YES and HEX "FPL3E AND NO CANCEL. SBC" 28.13.33.1 YES -> RECT "TYPE 3 LOAD TO LA" 28.21.74.1
  3. HEX "FPL4E" 28.13.42.1 YES -> RECT "SET ADR 13 ON MAB" 28.21.10.1
  4. HEX "FPL ADINHIB DF~ / DS~ . IRPT ENABLED . NOT ZL0-31" 28.23.11.1 (bars over line 1 and over "DS") YES -> RECT "PRE COND LA DF" 28.13.33.1; and -> HEX "DF MASK ONE" 28.23.11.1 YES -> RECT "PRE COND LA NOP FR ALARM" 28.13.33.1

##### 2. Structure
- No E / E.M / M sequencer bar. Two triggers: ZL FP4 TGR (TON: "SET ZL FP 4" or the 1Y53~.1Y55~.1Y56.1Y57~.COND FP CL decode) and ZL FP6 TGR (TON: "SET ZL FP6" or 1Y53.1Y NOT 54.1Y55.1Y56.1Y57.COND FP CL). Both feed the common block "ZL FP4 OR ZL FP6" 28.23.00.1. No TOF printed for either trigger.

##### 3. Step table
| step | condition (PRINTED) | action (PRINTED) | ALD | notes |
|---|---|---|---|---|
| FP4 TON | SET ZL FP 4; or 1Y53~.1Y55~.1Y56.1Y57~.COND FP CL | ZL FP4 TGR | 28.26.53.1 | |
| FP6 TON | SET ZL FP6; or 1Y53.1Y NOT 54.1Y55.1Y56.1Y57.COND FP CL | ZL FP6 TGR | 28.26.53.1 | |
| FP4 | ZL1+2+3 . IRPT ENABLED | PRE CND LA DS | 28.23.20.1 / 28.25.20.1 | |
| FP4 | ZL EQ 1 | PRE COND LA AD | 28.23.20.1 / 28.25.20.1 | |
| FP4 | IRPT ENABLED . NOT ZL0-15 | PRE CND LA DS; PRE CND LA NOP FR ALARM | 28.23.11.1 / 28.13.33.1 | |
| FP4 | ZL INT + ZL ADR 8 . FPL4E | SET LA INT STORE TAG | 28.24.82.1 | **[KEY]** |
| FP4 | ZL NE LTHD | COND FPL4E TON; (FPL4E.M / FPL4E.SBC) TYPE 3 LOAD TO LA, TYPE 3 LOAD TO BCU; (FPL4E) Z0-17 TO MAB | 28.23.10.1 ... | **[KEY]** FP load request |
| FP4 | — | BLOCK CND LA DF | 28.13.33.1 | |
| FP4 | FPL3E AND NO CANCEL . SBC / . FPL3M | TYPE 3 LOAD TO LA; T3LD TO BCU WAIT FOR ACCEPT | 28.13.33.1 / 28.21.74.1 | **[KEY]** |
| FP4 | FPL3NM . ALLOW LAST LOAD | COND FPL 3E TON | 28.23.00.1 / 28.13.31.1 | |
| FP4 | FPL4E; ZOAL EQ 11+12+16-31 | TON STORE WAIT TGR; TON 1RCY REQ TGR | 28.42.51.1; 28.42.72.1 | **[KEY]** |
| FP4 | FPL4E; PROGRAM STORE COMPARE | TON PIRCY TGR; TON 1RCY REQ TGR | 28.42.71.1; 28.42.72.1 | **[KEY]** |
| FP4 | FPL3E AND NO CANCEL; PROGRAM STORE COMPARE . ACCEPT OR COMPARE | TON IRCY REQ TGR | 28.13.33.1 / 28.42.72.1 | **[KEY]** |
| FP4/6 | FPL3E AND NO CANCEL | SET LA EXT STORE TAG | 28.24.82.1 | **[KEY]** |
| FP4/6 | FPL4E | SET LAOC 6, 8, & 9; SET LAOP TAG | 28.24.80.1 / 28.24.24.1, 28.24.26.1 / 36.05.01.1 | **[KEY]** |
| FP4/6 | — | COND FPL2E TON | 28.13.21.1 | unconditional, column A |
| FP4/6 | FPL3E AND NO CANCEL . SBC | MODIFIED TYPE 3 LOAD TO LA | 28.21.75.1 | |
| FP4/6 | FPL3E AND NO CANCEL . FPL3M | XFER & RESET NIDC; MODIFIED TYPE 3 LOAD TO LA | 28.21.73.1; 28.21.75.1 | |
| FP4/6 | ZL ADR 8 | I CHKR REQ; BLOCK ZL XS LTH SIGNAL | 28.20.08.1 / 28.27.32.1 / 28.20.41.1 | |
| FP4/6 | — | COND XOF 1 E TON | 28.12.11.1 | |
| FP4/6 | ZR INSTR PREP COMPLETE . ZR EQ1 . XOF1E | XOF 1TC FETCH | 28.12.12.1 / 24.00.09.1 | |
| FP4/6 | ZL ADR 8 LTH . FPR2E | SET LA EXT STORE TAG; SET LA INT STORE TAG | 28.24.82.1 / 36.09.14.1 / 36.09.15.1 | **[KEY]** |
| FP4/6 | ZL ADDR 8 LTH . FPL2 E . NM | I GEN PARITY | 28.13.22.1 / 28.44.14.1 | |
| FP4/6 | NOT IC FETCH PRIORITY | COND FPL2E TON | 28.20.23.1 / 28.13.21.1 | **[KEY]** |
| FP4/6 | — | BLOCK TYPE 2 LD TO LA | 28.13.33.1 | **[KEY]** unconditional |
| FP4/6 | FPL3E | ZO-17 TO MAB; GT ZLOC TO LAOC | 28.13.32.1 / 28.21.60.1 | **[KEY]** |
| FP4/6 | FPL3E AND NO CANCEL . FPL3M . MNT MD ZL4 | PANEL KEY REQUEST | 28.13.33.1 / 28.21.71.1 | |
| FP4/6 | ZL ADR 8 LTH | BLOCK ZL EXT OR ZL XS SIGNALS | 28.20.30.1 | |
| FP4/6 | FPL4E | BLOCK XFER OF ZLOC TO LAOC | 28.13.42.1 | **[KEY]** |
| FP4/6 | ZR INSTR PREP COMPLETE . ZR NOT EQ1 . XOF 1E | Z13-17 . P TO XAB | 28.12.12.1 / 28.86.56.1 | |
| FP6 | ZL NE LTHD | COND FPL4E TON; TYPE 3 LOAD TO LA / BCU | 28.23.10.1 / 28.14.41.1 / 28.21.74.1 | |
| FP6 | FPL4E | SET LA EXT STORE TAG | 28.24.82.1 / 36.09.14.1 | |
| FP6 | IRPT ENABLED . ZL1 + 2 + 3 | COND LA DF; COND LA NOP FROM DF | 28.23.20.1 / 28.25.30.1 | |
| FP6 | — | COND FPDDE TON | 28.10.11.1 | |
| FP6 | FPL3E AND NO. CANCEL. FPL3M; FPL3E AND NO CANCEL. SBC | TYPE 3 LOAD TO LA | 28.13.33.1 / 28.21.74.1 | |
| FP6 | FPL4E | SET ADR 13 ON MAB | 28.13.42.1 / 28.21.10.1 | |
| FP6 | (FPL ADINHIB DF DS)~ . IRPT ENABLED . NOT ZL0-31; DF MASK ONE | PRE COND LA DF; PRE COND LA NOP FR ALARM | 28.23.11.1 / 28.13.33.1 | |

##### 4. Named items
- Triggers: ZL FP4 TGR, ZL FP6 TGR, STORE WAIT TGR, 1RCY REQ TGR / IRCY REQ TGR, PIRCY TGR, FPL2E, FPL3E, FPL4E (TON), FPDDE, XOF 1 E.
- Registers/addresses: ZL (ZL0-15, ZL0-31, ZL1+2+3), ZR, ZOAL, Z0-17, ZO-17, Z13-17.P, MAB (ADR 13 ON MAB), XAB, ZLOC, LAOC (6, 8, & 9), LAOP TAG, LA EXT/INT STORE TAG, NIDC, BCU.
- LA indicators/codes: LA DS, LA AD, LA DF, LA NOP (FR ALARM, FROM DF).
- No counters, no timers.

##### 5. TIME
PRINTS NO TIME.

##### 6. [KEY] items (verbatim)
- **[KEY]** "NOT IC FETCH PRIORITY" 28.20.23.1 YES -> "COND FPL2E TON" 28.13.21.1; directly below, on the same line, unconditional: "BLOCK TYPE 2 LD TO LA" 28.13.33.1.
- **[KEY]** "COND FPL2E TON" 28.13.21.1 also appears UNCONDITIONALLY on column A of the "ZL FP4 OR ZL FP6" bus.
- **[KEY]** "ZOAL EQ 11+12+16-31" 28.42.51.1 YES -> "TON STORE WAIT TGR" 28.42.51.1, "TON 1RCY REQ TGR" 28.42.72.1.
- **[KEY]** "PROGRAM STORE COMPARE" 28.42.71.1 YES -> "TON PIRCY TGR" 28.42.71.1, "TON 1RCY REQ TGR" 28.42.72.1.
- **[KEY]** "PROGRAM STORE COMPARE . ACCEPT OR COMPARE" 28.42.72.1 YES -> "TON IRCY REQ TGR" 28.42.72.1 (under "FPL3E AND NO CANCEL" 28.13.33.1).
- **[KEY]** "T3LD TO BCU WAIT FOR ACCEPT" 28.21.74.1.
- **[KEY]** "SET LAOC 6, 8, & 9", "SET LAOP TAG"; "GT ZLOC TO LAOC"; "BLOCK XFER OF ZLOC TO LAOC"; SET LA EXT/INT STORE TAG (28.24.82.1, 36.09.14.1, 36.09.15.1).
- Nothing on what releases STORE WAIT; no LAAR, houseclean, pseudo-store text.

##### 7. Prior-claim check
- Prior claim "3.1.21 turns on FPL2E only under 'NOT IC FETCH PRIORITY', else 'BLOCK TYPE 2 LD TO LA'": **DISAGREE (in part)**. AGREE that "NOT IC FETCH PRIORITY" (28.20.23.1) YES -> "COND FPL2E TON" (28.13.21.1). But (a) "BLOCK TYPE 2 LD TO LA" (28.13.33.1) is NOT drawn on a NO exit — the hexagon has no NO exit; the BLOCK box hangs unconditionally off the same column line, below the hexagon; and (b) "COND FPL2E TON" (28.13.21.1) also hangs unconditionally off column A of the "ZL FP4 OR ZL FP6" bus, so the sheet does not say FPL2E is turned on "only" under NOT IC FETCH PRIORITY. (Whether the ALD gates these differently is not shown here.)

##### 8. Not read / uncertain
- "FPL4E" hexagon above "ZOAL EQ" prints no ALD (absent, not illegible).
- "ZL FP6 TGR" prints no ALD.
- "1Y53 . 1Y NOT 54 . ..." — printed with "NOT" between "1Y" and "54" (line break); read as NOT 1Y54 (DERIVED).
- "1RCY" vs "IRCY": the sheet prints both "TON 1RCY REQ TGR" (twice) and "TON IRCY REQ TGR" (once) for the same ALD 28.42.72.1; the lettering does not distinguish 1/I reliably.

#### Figure 3.1.22 — ZL IHW TRIGGER, ZR WAS IHW TRIGGER, 1 BIT MOD TRIGGER, AND FP Z ALT TRIGGER

- PDF page 86; printed page **1-45/1-46**; issue date **2/1/62**; header "M3-04-3  I UNIT FLOW DIAGRAMS".
- Applicability PRINTED: "CPU 7101 SER. NO. 30,004 AND HIGHER" (printed twice: left half and right half).
- Landscape fold-out, box text rotated; read upright at 300 dpi, top hexagon at 450 dpi.
- Notation: `X~` = overbar printed over X.

##### 1. Boxes (PRINTED)

###### A. ZL IHW TGR
- HEX "SBC • CD 1Y-ZL • HW CL 1Y • FW NOT S 1Y~ + CD 2Y-ZL • HW CL 2Y • FW NOT S 2Y • YR-ZL E (28.26.61.1)" — bars: over "FW NOT" / "S 1Y" (one negated term "FW NOT S 1Y"), and a short bar under "-ZL •" on line 1 whose meaning (underline vs overbar of "HW CL 1Y") is ambiguous. YES -> "TON" -> RECT "ZL IHW TGR (28.26.61.1)".
- Off the ZL IHW TGR bus:
  - Left column:
    1. HEX "ZR MT (28.15.41.1)" (no YES label) -> RECT "ZR INSTR COMP (28.15.51.1)"; and -> HEX "MOD ZL M (28.15.41.1)" (no YES label) -> line to RECT "IHW RDY E1 (28.67.17.1)", RECT "IHW RDY E2 (28.64.14.1)"
    2. HEX "XF + DEC ZL M • NOT ZL MOD (28.15.51.1)" (no YES label) -> HEX "ZR INSTR COMP (28.15.51.1)" (no YES label) -> same line to "IHW RDY E1" / "IHW RDY E2" (DERIVED: the MOD ZL M and ZR INSTR COMP exits join one line)
  - Second column:
    1. HEX "MOD ZL E • FW NOT S + PROG IX~ (28.15.41.1)" (bar over "FW NOT S +" and "PROG IX") (no YES label) -> RECT "Z 0-17 ABB PREP (28.96.03.1)"; RECT "Z 18 TO ABB P2 TO ADJ PAR OF Z 18 -23 (28.96.07.1)"; RECT "Z 18 ABB PREP (28.96.03.1)"
    2. HEX "MOD ZL E • MOD ZL M (28.15.41.1)" YES -> RECT "GT AOB 18 TO ZL (28.27.50.1)"; RECT "GT AOB 19 TO ZL (28.27.50.1)"
  - Third column:
    1. RECT "COND ZL DEC TON CKT (28.27.30.1)" (unconditional)
    2. HEX "BLOK XF + DEC~ • YR-ZL M • NOT IHW EX (28.15.50.1)" (bar over "BLOK XF + DEC"; PRINTED "BLOK") YES -> HEX "NOT I EX IN PROGRESS (28.15.50.1)" YES -> both:
       - HEX "SAC • NOT MOD L REQ (28.15.50.1)" YES
       - HEX "ZR WAS IHW • SAC (28.15.50.1)" YES
       -> (joined) RECT "TON XF + DEC ZL SEQ (28.15.50.1)"
    3. RECT "COND MOD ZL M TOF (28.15.40.1)" (unconditional, bottom of the column line)
  - Right column:
    1. HEX "CHK M COR • CD Y LEFT • Y-Z START + MOD ZL M + YR - ZL M • NOT MOD R (28.15.10.1)" YES -> RECT "COND YL-ZR TON CKT (28.15.10.1)"
    2. HEX "CD Y RIGHT • INST WD CHK COMP~ (28.15.60.1)" (bars over all three lines) YES -> RECT "COND YR-ZR TON CKT (28.15.60.1)"

###### B. ZR WAS IHW TGR
- HEX "YR-ZLE • IHW EX ZR TGR ON • SBC (28.15.51.1)" (the AND dots print as open circles) YES -> RECT "ZR WAS IHW TGR (28.15.51.1)" (no "TON" label printed here).
- Off it, unconditionally: RECT "BLOCK GEN OF OK TO MOD ZL (28.15.51.1)"; RECT "BLOCK MOD ZL E TON (28.15.40.1)"; RECT "BLOCK GEN OF Y-Z M • MOD REQ (28.15.71.1)"; RECT "COND XI + DEC SEQ TON (28.15.50.1)" (PRINTED "XI"; likely "XF", DERIVED).

###### C. 1 BIT MOD TGR
- HEX "SBC • MOD ZL E TGR ON (28.26.23.1)" YES -> RECT "1 BIT MOD TGR (28.26.23.1)".
- Off it: RECT "BLOCK GTING OF Z 28-30 TO XAB 1-3 (28.15.51.1)"; RECT "BLOCK GEN OF XS READ P (28.15.51.1)"; RECT "BLOCK GTING OF Z 31 TO XAB 4 (28.15.51.1)"; and HEX "XF + DEC ZL E (28.15.51.1)" YES -> RECT "GT Z 31 TO XAB 4 (28.27.52.1)"; RECT "XS READ P (24.00.09.1)"

###### D. FP Z ALT TGR
- Three hexagons, YES exits joined -> "TON" -> RECT "FP Z ALT TGR (28.27.32.1)":
  - HEX "ZR EXT • ZR FP CL • NOT ZR FP CL • ZL FP CL • SBC (28.27.32.1)" (PRINTED as such, "ZR FP CL • NOT ZR FP CL" across a line break)
  - HEX "NOT ZR FP TGR • ZL FP TGR • SBC (28.27.32.1)"
  - HEX "SBC • ZR FP CL • TOF FP RDY R • ZL EXT PREP • FPL 3E • ZL FP T (28.27.37.1)"
- Off FP Z ALT TGR:
  1. HEX "INSTR PREP COMP ZL (28.27.32.1)" YES -> RECT "FP RDY ZL (28.20.21.1)"; RECT "COND FP INCOMP TON CKT (28.42.53.1)"
  2. HEX "INST PREP COMP ZL • FP CL 2 ZL (28.27.32.1)" YES and HEX "INSTR PREP COMP ZR • FP CL 2 ZR (28.27.32.1)" YES -> (joined) RECT "BLOCK GEN OF INST CHK ENBLD (28.41.50.1)"
  3. HEX "INSTR PREP COMP ZR (28.27.32.1)" YES -> RECT "FP RDY ZR (28.20.21.1)"; RECT "COND FP INCOMP TON CKT (28.42.53.1)"

##### 2. Structure
- No E / E.M / M sequencer bar. Four independent triggers, each with a TON condition and actions hung off its output:
  - ZL IHW TGR — TON 28.26.61.1 hexagon (label "TON" printed). TOF not printed.
  - ZR WAS IHW TGR — set by "YR-ZLE • IHW EX ZR TGR ON • SBC". TOF not printed here (Fig 3.1.18 prints "TOF ZR WAS IHW TGR (28.15.51.1)" off ZL FL PT TGR).
  - 1 BIT MOD TGR — set by "SBC • MOD ZL E TGR ON". TOF not printed.
  - FP Z ALT TGR — TON (label printed) by the OR of three hexagons. TOF not printed (Fig 3.1.18 prints "COND FP Z ALT TGR TON (28.27.32.1)").

##### 3. Step table
| step | condition (PRINTED) | action (PRINTED) | ALD | notes |
|---|---|---|---|---|
| IHW TON | SBC • CD 1Y-ZL • HW CL 1Y • (FW NOT S 1Y)~ + CD 2Y-ZL • HW CL 2Y • FW NOT S 2Y • YR-ZL E | ZL IHW TGR | 28.26.61.1 | IHW = instruction half-word (DERIVED) |
| IHW | ZR MT | ZR INSTR COMP; MOD ZL M -> IHW RDY E1, IHW RDY E2 | 28.15.41.1 / 28.15.51.1 / 28.67.17.1 / 28.64.14.1 | |
| IHW | XF + DEC ZL M • NOT ZL MOD; ZR INSTR COMP | IHW RDY E1; IHW RDY E2 | 28.15.51.1 | |
| IHW | MOD ZL E • (FW NOT S + PROG IX)~ | Z 0-17 ABB PREP; Z 18 TO ABB P2 TO ADJ PAR OF Z 18-23; Z 18 ABB PREP | 28.96.03.1; 28.96.07.1 | |
| IHW | MOD ZL E • MOD ZL M | GT AOB 18 TO ZL; GT AOB 19 TO ZL | 28.27.50.1 | |
| IHW | — | COND ZL DEC TON CKT | 28.27.30.1 | |
| IHW | (BLOK XF + DEC)~ • YR-ZL M • NOT IHW EX; NOT I EX IN PROGRESS; SAC • NOT MOD L REQ or ZR WAS IHW • SAC | TON XF + DEC ZL SEQ | 28.15.50.1 | |
| IHW | — | COND MOD ZL M TOF | 28.15.40.1 | |
| IHW | CHK M COR • CD Y LEFT • Y-Z START + MOD ZL M + YR - ZL M • NOT MOD R | COND YL-ZR TON CKT | 28.15.10.1 | |
| IHW | (CD Y RIGHT • INST WD CHK COMP)~ | COND YR-ZR TON CKT | 28.15.60.1 | |
| ZR WAS IHW | YR-ZLE • IHW EX ZR TGR ON • SBC | ZR WAS IHW TGR; BLOCK GEN OF OK TO MOD ZL; BLOCK MOD ZL E TON; BLOCK GEN OF Y-Z M • MOD REQ; COND XI + DEC SEQ TON | 28.15.51.1; 28.15.40.1; 28.15.71.1; 28.15.50.1 | |
| 1 BIT MOD | SBC • MOD ZL E TGR ON | 1 BIT MOD TGR; BLOCK GTING OF Z 28-30 TO XAB 1-3; BLOCK GEN OF XS READ P; BLOCK GTING OF Z 31 TO XAB 4 | 28.26.23.1; 28.15.51.1 | |
| 1 BIT MOD | XF + DEC ZL E | GT Z 31 TO XAB 4; XS READ P | 28.15.51.1 / 28.27.52.1 / 24.00.09.1 | |
| FP Z ALT TON | ZR EXT • ZR FP CL • NOT ZR FP CL • ZL FP CL • SBC; or NOT ZR FP TGR • ZL FP TGR • SBC; or SBC • ZR FP CL • TOF FP RDY R • ZL EXT PREP • FPL 3E • ZL FP T | FP Z ALT TGR | 28.27.32.1 / 28.27.37.1 | |
| FP Z ALT | INSTR PREP COMP ZL | FP RDY ZL; COND FP INCOMP TON CKT | 28.20.21.1; 28.42.53.1 | **[KEY]** |
| FP Z ALT | INST PREP COMP ZL • FP CL 2 ZL or INSTR PREP COMP ZR • FP CL 2 ZR | BLOCK GEN OF INST CHK ENBLD | 28.41.50.1 | |
| FP Z ALT | INSTR PREP COMP ZR | FP RDY ZR; COND FP INCOMP TON CKT | 28.20.21.1; 28.42.53.1 | **[KEY]** |

##### 4. Named items
- Triggers: ZL IHW TGR, ZR WAS IHW TGR, 1 BIT MOD TGR, FP Z ALT TGR, MOD ZL E TGR, IHW EX ZR TGR, ZR FP TGR, ZL FP TGR, FP INCOMP (TGR), XF + DEC ZL SEQ (sequencer, TON only), XI[XF] + DEC SEQ.
- Registers: ZL, ZR, YL, YR, 1Y, 2Y, Z 0-17, Z 18, Z 18-23, Z 28-30, Z 31, XAB 1-3, XAB 4, ABB (P2), AOB 18, AOB 19, XS.
- No counters, no timers.

##### 5. TIME
PRINTS NO TIME.

##### 6. [KEY] items (verbatim)
- **[KEY]** "FP RDY ZL (28.20.21.1)" / "FP RDY ZR (28.20.21.1)" with "COND FP INCOMP TON CKT (28.42.53.1)" under "INSTR PREP COMP ZL" / "INSTR PREP COMP ZR" (FP instruction ready to go to look-ahead, DERIVED).
- **[KEY]** "SBC • ZR FP CL • TOF FP RDY R • ZL EXT PREP • FPL 3E • ZL FP T (28.27.37.1)" (FP Z ALT TON term naming TOF of FP RDY R and FPL 3E).
- No STORE WAIT, recovery, houseclean, LAAR, store compare, IC FETCH PRIORITY text.

##### 7. Not read / uncertain
- Short bar under "-ZL •" in the ZL IHW TON hexagon (28.26.61.1): underline vs overbar of "HW CL 1Y" ambiguous.
- "COND XI + DEC SEQ TON (28.15.50.1)": "XI" as printed; the sheet elsewhere says "XF + DEC".
- No YES labels printed on "ZR MT", "MOD ZL M", "XF + DEC ZL M • NOT ZL MOD", "ZR INSTR COMP" (hex) and the "MOD ZL E • FW NOT S + PROG IX" hexagon.

#### Figure 3.1.23 — WBC + DEC SEQUENCER AND XF + DEC SEQUENCER

- PDF page 87; printed page **1-47/1-48**; issue date **2/1/62**; header "M3-04-3  I UNIT FLOW DIAGRAMS".
- Applicability PRINTED: "CPU 7101 SER. NO. 30,004 AND HIGHER".
- Landscape fold-out, box text rotated; read upright at 300 dpi; the TON hexagon and both IMM/VFL hexagons checked at 450 dpi.
- Notation: `X~` = overbar printed over X.

##### 1. WBC + DEC SEQUENCER (upper half)

- HEX "SAC • ZR NOT FPCL • MOD ZR • FW NOT S + FW COMP + YL - ZL • NOT MOD L + MOD ZL • FWS • FW S + FW NOT S (28.15.80.1)" YES -> "TON" -> sequencer bar "WBC + DEC SEQUENCER (28.15.80.1)" with three phase lines labelled **E**, **E•M**, **M**.

###### Phase line E (left)
Unconditional actions, first column:
1. RECT "TON WBC + DEC M TGR (28.15.80.1)" (last digit partly lost: "(28.15.80.?)"; DERIVED .1)
2. RECT "GT Z TO ABB (28.27.53.1)"
3. RECT "Z0-17 ABB PREP (28.15.41.1)"
4. RECT "Z 18 ABB PREP (28.15.41.1)"
5. RECT "Z 19 - 23 ABB PREP (28.15.41.1)"
6. RECT "HOLD DATA SELECT PREP (28.96.43.1)"
7. RECT "COND TON • TOF WNA • WXA • WSA TGRS (28.51.09.1)"

Unconditional actions, second column:
8. RECT "TOF YL - ZL M TGR (28.15.70.1)"
9. RECT "TOF YR-ZL M TGR (28.15.30.1)"
10. RECT "TOF YL-ZR M TGR (28.15.10.1)"
11. RECT "TOF FULL WRD S TGR (28.26.60.1)"
12. RECT "TOF FULL WRD NOT S TGR (28.26.60.1)"
13. RECT "TOF MOD ZR M TGR (28.15.20.1)"
14. RECT "GT AOB 0-17 + P 0-17 TO W (28.02.01.1)"

Conditions on E:
15. HEX "Z 35 • 36 • 37 • 38 • 39 • 40 ZERO (25.04.01.1)" YES -> RECT "IC - W - Z ABA (27.02.06.1)"; RECT "IC - Z ABA P1 (27.05.01.1)"; and -> HEX "SUM 18 • 19 • 20 • 21 TO MEM AREA DEC (28.14.02.1)" YES -> RECT "WORD BNDRY CROSSOVER (28.22.02.1)"  **[KEY] WBC**
16. HEX "SBC" (no ALD) YES -> RECT "TOF MOD ZL M TGR (28.15.40.1)"

###### Phase line E•M (printed "E•M")
1. HEX "IMM~ • VFL (28.15.81.1)" YES -> RECT "COND WBC TGR TON (28.22.02.1)"  **[KEY] WBC**
2. HEX "VFL • IMM~ (28.15.81.1)" YES -> RECT "GT AOB 19 TO ZL (28.27.50.1)"

###### Phase line M (right)
1. RECT "COND VFL 1 TON CKT (28.11.11.1)" (unconditional)
2. HEX "VFL + IO (28.11.11.1)" YES -> RECT "BLOCK GEN OF NO I CHKR REQ L (28.20.21.1)"
3. RECT "FW RDY E1 (28.67.17.1)" (unconditional)
4. RECT "FW RDY E2 (28.75.72.1)" (unconditional)

##### 2. XF + DEC SEQUENCER (lower half)

- Three hexagons, YES exits joined -> "TON" -> sequencer bar "XF + DEC SEQUENCER (28.15.50.1)" with phase lines **E** and **M** (no E•M line):
  - HEX "BLOK XF + DEC~ • ZL IHW • YR-ZL M • NOT IHW EX • NOT I EX IN PROG • SAC • NOT MOD L RQ (28.15.50.1)" YES
  - HEX "SAC • ZR WAS IHW • BLOK XF + DEC~ • ZL IHW • YR-ZL M • NOT IHW EX • NOT I EX IN PROG (28.15.50.1)" (no YES label)
  - HEX "ZL MOD REQ • SAC • NOT IHW EX • ZR WAS IHW~ • BLOK XF + DEC~ • ZL FP + LH FW (28.15.50.1)" (bars over "ZR WAS IHW" and over "BLOK XF + DEC"; extent DERIVED; no YES label)

###### Phase line E
1. RECT "TON XF + DEC M TGR (28.15.50.1)"
2. RECT "COND YR-ZL M TGR TOF (28.15.30.1)"
3. HEX "NOT 1 BIT MOD RQD (28.15.51.1)" YES -> RECT "GT Z 28-30 TO XAB 1-3 (28.27.52.1)"
4. HEX "1 BIT MOD R T (28.15.51.1)" YES -> RECT "GT Z 31 TO XAB 4 (28.27.52.1)"; RECT "XS READ P (24.00.09.1)"; RECT "BLOCK GEN OF INH NIDC SET IDC FR XAC (28.27.31.1)"; RECT "TOF ZR WAS IHW TGR (28.15.51.1)"
5. HEX "XF + DEC M TGR OFF (28.15.50.1)" — exit labelled "YES" and "E • M~" (PRINTED "E o M" with bar over M) -> RECT "PREP RST X 0-63 (28.86.57.1)"

###### Phase line M
1. RECT "COND MOD ZL E TON CKT (28.15.40.1)"
2. RECT "TOF XF + DEC E TGR (28.15.50.1)"
3. RECT "BLOCK Y-Z START TON (28.26.11.1)"
4. HEX "FW NOT ST • PX Y • MOD ZL E (28.15.42.1)" (no YES label) -> RECT "PREP GT Z 0-23 TO ICIB (28.79.65.1)"; RECT "COND IDC FR I PAR ERR PREP (28.99.03.1)"; RECT "TON PX YL TGR (28.78.34.1)"; RECT "PREP SET ONE TO ICIB PAR (28.21.20.1)"; and -> HEX "MOD ZL M~ (28.15.42.1)" YES -> RECT "IP CHK PAR (28.98.07.1)"; RECT "I CHK E • NM (38.03.03.1)"
5. HEX "ZL IHW T • NOT ZL MOD (28.15.51.1)" YES -> HEX "ZR INSTR COMP (28.15.51.1)" YES -> RECT "IHW RDY E1 (28.67.17.1)"; RECT "IHW RDY E2 (28.64.14.1)"
6. HEX "FW NOT ST (28.15.40.1)" (no YES label) -> RECT "COND MOD ZL TON CKT (28.15.40.1)"

##### 3. Step table
| step / phase | condition (PRINTED) | action (PRINTED) | ALD | notes |
|---|---|---|---|---|
| WBC TON | SAC • ZR NOT FPCL • MOD ZR • FW NOT S + FW COMP + YL - ZL • NOT MOD L + MOD ZL • FWS • FW S + FW NOT S | WBC + DEC SEQUENCER | 28.15.80.1 | |
| WBC E | — | TON WBC + DEC M TGR; GT Z TO ABB; Z0-17 / Z 18 / Z 19-23 ABB PREP; HOLD DATA SELECT PREP; COND TON • TOF WNA • WXA • WSA TGRS | 28.15.80.1; 28.27.53.1; 28.15.41.1; 28.96.43.1; 28.51.09.1 | |
| WBC E | — | TOF YL-ZL M TGR; TOF YR-ZL M TGR; TOF YL-ZR M TGR; TOF FULL WRD S TGR; TOF FULL WRD NOT S TGR; TOF MOD ZR M TGR; GT AOB 0-17 + P 0-17 TO W | 28.15.70.1; 28.15.30.1; 28.15.10.1; 28.26.60.1; 28.15.20.1; 28.02.01.1 | |
| WBC E | Z 35•36•37•38•39•40 ZERO | IC - W - Z ABA; IC - Z ABA P1 | 25.04.01.1 / 27.02.06.1 / 27.05.01.1 | |
| WBC E | Z 35..40 ZERO, then SUM 18•19•20•21 TO MEM AREA DEC | WORD BNDRY CROSSOVER | 28.14.02.1 / 28.22.02.1 | **[KEY]** |
| WBC E | SBC | TOF MOD ZL M TGR | 28.15.40.1 | |
| WBC E•M | IMM~ • VFL | COND WBC TGR TON | 28.15.81.1 / 28.22.02.1 | **[KEY]** |
| WBC E•M | VFL • IMM~ | GT AOB 19 TO ZL | 28.15.81.1 / 28.27.50.1 | |
| WBC M | — | COND VFL 1 TON CKT; FW RDY E1; FW RDY E2 | 28.11.11.1; 28.67.17.1; 28.75.72.1 | |
| WBC M | VFL + IO | BLOCK GEN OF NO I CHKR REQ L | 28.11.11.1 / 28.20.21.1 | |
| XF TON | three hexagons (see §2) | XF + DEC SEQUENCER | 28.15.50.1 | |
| XF E | — | TON XF + DEC M TGR; COND YR-ZL M TGR TOF | 28.15.50.1; 28.15.30.1 | |
| XF E | NOT 1 BIT MOD RQD | GT Z 28-30 TO XAB 1-3 | 28.15.51.1 / 28.27.52.1 | |
| XF E | 1 BIT MOD R T | GT Z 31 TO XAB 4; XS READ P; BLOCK GEN OF INH NIDC SET IDC FR XAC; TOF ZR WAS IHW TGR | 28.27.52.1; 24.00.09.1; 28.27.31.1; 28.15.51.1 | |
| XF E | XF + DEC M TGR OFF (exit "YES", "E • M~") | PREP RST X 0-63 | 28.15.50.1 / 28.86.57.1 | |
| XF M | — | COND MOD ZL E TON CKT; TOF XF + DEC E TGR; BLOCK Y-Z START TON | 28.15.40.1; 28.15.50.1; 28.26.11.1 | |
| XF M | FW NOT ST • PX Y • MOD ZL E | PREP GT Z 0-23 TO ICIB; COND IDC FR I PAR ERR PREP; TON PX YL TGR; PREP SET ONE TO ICIB PAR | 28.15.42.1; 28.79.65.1; 28.99.03.1; 28.78.34.1; 28.21.20.1 | |
| XF M | ... MOD ZL M~ | IP CHK PAR; I CHK E • NM | 28.15.42.1; 28.98.07.1; 38.03.03.1 | |
| XF M | ZL IHW T • NOT ZL MOD; ZR INSTR COMP | IHW RDY E1; IHW RDY E2 | 28.15.51.1; 28.67.17.1; 28.64.14.1 | |
| XF M | FW NOT ST | COND MOD ZL TON CKT | 28.15.40.1 | |

##### 4. Named items
- Sequencers: WBC + DEC SEQUENCER (phases E, E•M, M); XF + DEC SEQUENCER (phases E, M). Per-phase triggers named: WBC + DEC M TGR (TON on E), XF + DEC M TGR (TON on E), XF + DEC E TGR (TOF on M).
- Other triggers: WBC TGR (COND ... TON), YL-ZL M, YR-ZL M, YL-ZR M, FULL WRD S, FULL WRD NOT S, MOD ZR M, MOD ZL M, MOD ZL E, ZR WAS IHW, PX YL, WNA / WXA / WSA TGRS, VFL 1, IDC.
- Registers/buses: Z (Z 0-17, 18, 19-23, 28-30, 31, 35-40), ZL, ZR, YL, YR, W ("GT AOB 0-17 + P 0-17 TO W"), ABB, AOB 0-17, AOB 19, ABA ("IC - W - Z ABA", "IC - Z ABA P1"), XAB 1-3, XAB 4, X 0-63, XS, ICIB, NIDC, IDC, XAC, "SUM 18•19•20•21" (MEM AREA DEC), IC.
- No counters (IAUC, OCC, ...) or timers named.

##### 5. TIME
PRINTS NO TIME (the E / E•M / M phase labels are the only sequencing marks).

##### 6. [KEY] items (verbatim)
- **[KEY]** WBC: "IMM~ • VFL (28.15.81.1)" YES -> "COND WBC TGR TON (28.22.02.1)", on the E•M line of the WBC + DEC SEQUENCER.
- **[KEY]** WBC: "Z 35 • 36 • 37 • 38 • 39 • 40 ZERO (25.04.01.1)" -> "SUM 18 • 19 • 20 • 21 TO MEM AREA DEC (28.14.02.1)" YES -> "WORD BNDRY CROSSOVER (28.22.02.1)", on the E line.
- **[KEY]** "GT AOB 0-17 + P 0-17 TO W (28.02.01.1)" (unconditional on E).
- No STORE WAIT, I-unit recovery, houseclean, LAAR, store compare, IC FETCH PRIORITY text.

##### 7. Prior-claim check
- Prior claim "3.1.23 turns the word-boundary test on only under IMM-bar . VFL ('COND WBC TGR TON'), 'GT AOB 19 TO ZL'": **AGREE, with one addition**. PRINTED: "IMM~ • VFL (28.15.81.1)" YES -> "COND WBC TGR TON (28.22.02.1)" and a SEPARATE hexagon "VFL • IMM~ (28.15.81.1)" YES -> "GT AOB 19 TO ZL (28.27.50.1)", both on the E•M line. The bars over IMM are confirmed at 450 dpi. Addition: the same sheet's E line also produces "WORD BNDRY CROSSOVER (28.22.02.1)" under "Z 35..40 ZERO" -> "SUM 18 • 19 • 20 • 21 TO MEM AREA DEC (28.14.02.1)" — not gated by IMM/VFL on the drawing.

##### 8. Not read / uncertain
- "TON WBC + DEC M TGR (28.15.80.?)": last digit of the ALD smeared; DERIVED ".1".
- Bar extents in the third XF + DEC TON hexagon ("ZR WAS IHW", "BLOK XF + DEC").
- "1 BIT MOD R T": printed with a gap ("R  T"); no bar visible.
- The "VFL + IO" YES exit runs off the right edge region but its connection to "BLOCK GEN OF NO I CHKR REQ L" is visible in the overview.

#### Figure 3.1.24 — WBC TRIGGER

- PDF page 88; printed page **1-49/1-50**; issue date **2/1/62**; header "M3-04-3  I UNIT FLOW DIAGRAMS".
- Applicability PRINTED: "CPU 7101 SER. NO. 30,004 AND HIGHER".
- Landscape fold-out, box text rotated; read upright at 300 dpi; eight labels re-read at 450 dpi.
- Notation: `X~` = overbar printed over X. "o" = AND printed as an open circle.

##### 1. Boxes (PRINTED)

###### Entry
- HEX "SAR WBC TEST E o M o WRD BNDRY X OVER (28.22.02.1)" YES -> "TON" -> RECT "WORD BOUNDRY CROSSOVER TGR (28.22.02.1)" (PRINTED "BOUNDRY").
  (DERIVED: "E o M" = the E•M phase of the WBC + DEC sequencer of Fig 3.1.23, where "IMM~ • VFL" gives "COND WBC TGR TON (28.22.02.1)".)

###### Column 1 — unconditional BLOCKs off the trigger bus
1. RECT "BLOCK GEN COND VFL 4T (28.22.20.1)"
2. RECT "BLOCK GEN VFL 5T (28.22.20.1)"
3. RECT "BLOCK GEN ZL EXT NOT WBC (28.22.20.1)"
4. RECT "BLOCK GEN ZL INT NOT WBC (28.22.20.1)"
5. RECT "BLOCK GEN COND VFL 4 T3" (no ALD printed)
6. RECT "BLOCK GEN VFL CL 1 DIR COND LA IF TAG (28.22.20.1)"
7. RECT "BLOCK GEN VFL 5 T3 (28.22.20.1)"
8. RECT "BLOCK GEN COND VFL 5 T3 (28.22.20.1)"
9. RECT "BLOCK GEN OF 3 LEVEL INSTR (28.22.10.1)"
10. RECT "BLOCK SET OF LAOC POS 6 (36.09.09.1)"
11. RECT "BLOCK GEN OF VFL 5 T3 CL 1 + 2 • WBC (28.22.10.1)"
12. HEX "VFL CL 2 + VFL CL 3 + VFL CL 4 • WBC~ • VFL CL 2~ (28.22.10.1)" (bars over WBC and the last VFL CL 2; a further bar sits under "CL 3 + VFL" above "CL 4" — extent ambiguous) YES -> line carrying:
    - HEX "VFL 4 TYPE 3 + VFL 4 TYPE 2 (28.22.50.1)" YES -> HEX "VFL 4 E ON (28.11.42.1)" YES -> RECT "W 0-17 TO MAB (28.21.61.1)"  **[KEY]**
    - HEX "CYC PREC VFL 4 COMP (28.12.12.1)" YES -> HEX "VFL • W + ZL EQ 1 • XOF1 E (28.12.12.1)" YES -> RECT "W 13-17 • P TO XAB (28.86.56.1)"
    - HEX "VFL 1 M TGR ON (28.11.12.1)" YES -> RECT "VFL 1 COND VFL 3 (28.11.22.1)"
    - RECT "COND VFL 4 TYPE 2 + 3 (28.11.42.1)" (unconditional, end of line)

###### Column 2
1. HEX "VFL CL 5 • IO~ • VFL + IO OP CODE INV~ (28.22.10.1)" (bars over both lines and "INV") YES -> RECT "BLOCK GEN OF VFL 1 COND VFL 5 (28.11.12.1)"
2. HEX "VFL 4 E (28.24.25.1)" YES -> RECT "SET LOAC POS 8 (36.09.11.1)"  **[KEY]**
3. HEX "GT ZROC TO LOAC (28.24.80.1)" (drawn as a hexagon) YES -> RECT "SET LA WBC TAG (36.06.01.1)"  **[KEY]**
4. HEX "W EQ 11 + 12 + 16 - 31 (28.11.55.1)" YES -> HEX "VFL CL 2 • VFL 5E (28.11.55.1)" YES -> RECT "VFL 5 CL 2 COND STORE WAIT (28.21.71.1)"  **[KEY]**
5. HEX "W EQ XS (28.22.20.1)" YES -> RECT "COND VFL 4 T (28.22.21.1)"; and -> HEX "VFL CL 1 • DIR (28.22.20.1)" YES -> RECT "VFL 5 TYPE 1B (28.22.40.1 • 28.11.52.1 • 28.12.11.1)"
6. HEX "W EXIST NON EXIST (28.22.20.1)" YES -> RECT "COND VFL 4 T2 (28.22.21.1)"; and -> HEX "VFL CL 1 • DIR (28.22.20.1)" (the word "DIR" is crossed by the fold line and reads "DI2"; DERIVED DIR) YES -> RECT "VFL 5 T2 (28.22.20.1)"
7. HEX "W EQ INT (28.22.20.1)" YES -> RECT "COND VFL 4 T3 (28.22.21.1)"; and -> HEX "VFL CL 1 • DIR (28.22.20.1)" YES -> RECT "VFL CL 1 DIR COND LA IF TAG (28.24.48.1)"; RECT "VFL 5 TY 3 (28.22.20.1)"

###### Column 3
1. HEX "W NON EXIST (28.20.50.1)" YES -> three hexagons:
   - HEX "COND VFL 3 T2 (28.22.50.1)" YES -> RECT "VFL 3 T2 • MNT MODE + NON EXIST (28.24.81.1)"
   - HEX "VFL 4 T2 (28.22.50.1)" YES -> RECT "VFL 4 T2 MNT MODE + NON EXIST (28.24.81.1)"
   - HEX "VFL 5 T2 (28.20.50.1)" YES -> RECT "VFL 5 T2 • MNT MODE + NON EXIST (28.24.81.1)"
2. HEX "CYL PREC VFL 5 COMP (28.12.12.1)" (PRINTED "CYL"; column 1 prints "CYC") YES -> RECT "BLOCK GTING OF Z 13-17 • P TO XAB (28.86.56.1)"; and -> HEX "VFL o W + ZL EQ 1 • XOF1 (28.12.12.1)" (a dot/tick precedes "VFL") YES -> RECT "W 13 - 17 • P TO XAB (28.86.56.1)"
3. HEX "W NON EXIST (28.22.60.1)" YES -> HEX "Z 59 • Z FW~ • VFL CL 5~ • IMM (28.22.60.1)" (a bar under "Z" / over "FW", and a bar over "VFL CL 5"; extents ambiguous) YES -> joins item 4's actions
4. HEX "W EQ 1 • VFL CL 2 (28.22.60.1)" YES -> RECT "VFL AD INHIB (28.22.60.1)"; RECT "VFL COND SET LAAD (28.22.60.1)"
5. HEX "ZL 11 + 12 + 16 - 31 (28.11.55.1)" YES -> HEX "VFL C2 • VFL 5E (28.11.55.1)" YES -> RECT "VFL 5 CL 2 COND STORE WAIT (28.21.71.1)"  **[KEY]**
6. HEX "VFL CL 1 (28.22.10.1)" YES -> RECT "3 LEVEL INSTR (28.11.12.1)"
7. HEX "W EQ 1 + 2 + 3 (28.22.70.1)" YES -> HEX "VFL CL 2 • IRPT ENBLD (28.22.70.1)" YES -> RECT "VFL COND SET LA DS (28" (ALD cut short as printed: only "(28"); and -> HEX "VFL CL 1 + VFL CL 3 + VFL CL 4 • IRPT ENBLD (28.22.70.1)" YES -> RECT "VFL COND SET LA DF (28.25.30.1)"

##### 2. Structure
- No E / E.M / M sequencer bar on this sheet. One trigger: WORD BOUNDRY CROSSOVER TGR (28.22.02.1), TON by "SAR WBC TEST E o M o WRD BNDRY X OVER". No TOF printed.
- The VFL look-ahead level/class names (VFL 1, VFL 3, VFL 4, VFL 5, VFL CL 1..5, types T, T2, T3, TYPE 1B, 2, 3) are the VFL analogue of the FPL levels on 3.1.18-3.1.21 (DERIVED).

##### 3. Step table
| step | condition (PRINTED) | action (PRINTED) | ALD | notes |
|---|---|---|---|---|
| TON | SAR WBC TEST E o M o WRD BNDRY X OVER | WORD BOUNDRY CROSSOVER TGR | 28.22.02.1 | **[KEY]** WBC |
| WBC | — | 11 BLOCK boxes (column 1) incl. BLOCK GEN ZL EXT NOT WBC, BLOCK GEN ZL INT NOT WBC, BLOCK SET OF LAOC POS 6, BLOCK GEN OF VFL 5 T3 CL 1 + 2 • WBC | 28.22.20.1 / 28.22.10.1 / 36.09.09.1 | |
| WBC | VFL CL 2 + VFL CL 3 + VFL CL 4 • WBC~ • VFL CL 2~; VFL 4 TYPE 3 + VFL 4 TYPE 2; VFL 4 E ON | W 0-17 TO MAB | 28.22.10.1 / 28.22.50.1 / 28.11.42.1 / 28.21.61.1 | **[KEY]** |
| WBC | ... ; CYC PREC VFL 4 COMP; VFL • W + ZL EQ 1 • XOF1 E | W 13-17 • P TO XAB | 28.12.12.1 / 28.86.56.1 | |
| WBC | ... ; VFL 1 M TGR ON | VFL 1 COND VFL 3 | 28.11.12.1 / 28.11.22.1 | |
| WBC | ... | COND VFL 4 TYPE 2 + 3 | 28.11.42.1 | |
| WBC | (VFL CL 5 • IO • VFL + IO OP CODE INV)~ | BLOCK GEN OF VFL 1 COND VFL 5 | 28.22.10.1 / 28.11.12.1 | |
| WBC | VFL 4 E | SET LOAC POS 8 | 28.24.25.1 / 36.09.11.1 | **[KEY]** |
| WBC | GT ZROC TO LOAC | SET LA WBC TAG | 28.24.80.1 / 36.06.01.1 | **[KEY]** |
| WBC | W EQ 11 + 12 + 16 - 31; VFL CL 2 • VFL 5E | VFL 5 CL 2 COND STORE WAIT | 28.11.55.1 / 28.21.71.1 | **[KEY]** |
| WBC | W EQ XS | COND VFL 4 T; (VFL CL 1 • DIR) VFL 5 TYPE 1B | 28.22.20.1 / 28.22.21.1 / 28.22.40.1, 28.11.52.1, 28.12.11.1 | |
| WBC | W EXIST NON EXIST | COND VFL 4 T2; (VFL CL 1 • DIR) VFL 5 T2 | 28.22.20.1 / 28.22.21.1 | |
| WBC | W EQ INT | COND VFL 4 T3; (VFL CL 1 • DIR) VFL CL 1 DIR COND LA IF TAG, VFL 5 TY 3 | 28.22.20.1 / 28.22.21.1 / 28.24.48.1 | |
| WBC | W NON EXIST; COND VFL 3 T2 / VFL 4 T2 / VFL 5 T2 | VFL n T2 (•) MNT MODE + NON EXIST | 28.20.50.1 / 28.22.50.1 / 28.24.81.1 | |
| WBC | CYL PREC VFL 5 COMP | BLOCK GTING OF Z 13-17 • P TO XAB; (VFL o W + ZL EQ 1 • XOF1) W 13-17 • P TO XAB | 28.12.12.1 / 28.86.56.1 | |
| WBC | W NON EXIST; Z 59 • Z FW~ • VFL CL 5~ • IMM — or W EQ 1 • VFL CL 2 | VFL AD INHIB; VFL COND SET LAAD | 28.22.60.1 | |
| WBC | ZL 11 + 12 + 16 - 31; VFL C2 • VFL 5E | VFL 5 CL 2 COND STORE WAIT | 28.11.55.1 / 28.21.71.1 | **[KEY]** |
| WBC | VFL CL 1 | 3 LEVEL INSTR | 28.22.10.1 / 28.11.12.1 | |
| WBC | W EQ 1 + 2 + 3; VFL CL 2 • IRPT ENBLD | VFL COND SET LA DS | 28.22.70.1 / "(28" | ALD truncated |
| WBC | W EQ 1 + 2 + 3; VFL CL 1 + VFL CL 3 + VFL CL 4 • IRPT ENBLD | VFL COND SET LA DF | 28.22.70.1 / 28.25.30.1 | |

##### 4. Named items
- Triggers: WORD BOUNDRY CROSSOVER TGR, VFL 1 M TGR, (WBC TGR via 3.1.23).
- VFL levels/types: VFL 1, VFL 3 T2, VFL 4 (E, E ON, T, T2, T3, TYPE 2, TYPE 3), VFL 5 (E, T, T2, T3, TY 3, TYPE 1B, CL 2), VFL CL 1-5.
- Registers/addresses: W (W 0-17, W 13-17, W EQ 1/1+2+3/11+12+16-31/INT/XS, W EXIST/NON EXIST), ZL (ZL 11+12+16-31, ZL EXT, ZL INT), Z 13-17, Z 59, Z FW, MAB, XAB, ZROC, LOAC (POS 6, POS 8), LA WBC TAG, LA IF TAG, LAAD, LA DS, LA DF, XOF1.
- No counters, no timers.

##### 5. TIME
PRINTS NO TIME (apart from "E o M" inside the TON condition, a phase name, not a time).

##### 6. [KEY] items (verbatim)
- **[KEY]** "SAR WBC TEST E o M o WRD BNDRY X OVER (28.22.02.1)" -> TON "WORD BOUNDRY CROSSOVER TGR (28.22.02.1)".
- **[KEY]** "W EQ 11 + 12 + 16 - 31 (28.11.55.1)" -> "VFL CL 2 • VFL 5E (28.11.55.1)" -> "VFL 5 CL 2 COND STORE WAIT (28.21.71.1)".
- **[KEY]** "ZL 11 + 12 + 16 - 31 (28.11.55.1)" -> "VFL C2 • VFL 5E (28.11.55.1)" -> "VFL 5 CL 2 COND STORE WAIT (28.21.71.1)".
- **[KEY]** "VFL 4 E ON (28.11.42.1)" -> "W 0-17 TO MAB (28.21.61.1)".
- **[KEY]** "GT ZROC TO LOAC (28.24.80.1)" -> "SET LA WBC TAG (36.06.01.1)"; "VFL 4 E (28.24.25.1)" -> "SET LOAC POS 8 (36.09.11.1)"; "BLOCK SET OF LAOC POS 6 (36.09.09.1)".
- **[KEY]** "BLOCK GEN ZL EXT NOT WBC (28.22.20.1)", "BLOCK GEN ZL INT NOT WBC (28.22.20.1)".
- No STORE WAIT release, recovery, houseclean, LAAR, store compare or IC FETCH PRIORITY text.

##### 7. Prior-claim check
- "3.1.24 has 'VFL 4 E ON (28.11.42.1)' -> 'W 0-17 TO MAB (28.21.61.1)'": **AGREE** (exact text and ALDs; nested under "VFL CL 2 + VFL CL 3 + VFL CL 4 • WBC~ • VFL CL 2~ (28.22.10.1)" then "VFL 4 TYPE 3 + VFL 4 TYPE 2 (28.22.50.1)").
- "tests 'W EQ INT'": **AGREE** — "W EQ INT (28.22.20.1)" YES -> "COND VFL 4 T3 (28.22.21.1)", then "VFL CL 1 • DIR" -> "VFL CL 1 DIR COND LA IF TAG (28.24.48.1)", "VFL 5 TY 3 (28.22.20.1)".
- "its STORE WAIT hexagon names words 11, 12 and 16-31": **AGREE in substance, one correction** — STORE WAIT is not in a hexagon: it is the action rectangle "VFL 5 CL 2 COND STORE WAIT (28.21.71.1)". The word list is in two hexagons, "W EQ 11 + 12 + 16 - 31 (28.11.55.1)" and "ZL 11 + 12 + 16 - 31 (28.11.55.1)", each gated further by "VFL CL 2 • VFL 5E" / "VFL C2 • VFL 5E".

##### 8. Not read / uncertain
- "VFL COND SET LA DS (28" — the ALD reference is printed incomplete ("(28" only).
- "BLOCK GEN COND VFL 4 T3" prints no ALD.
- "VFL CL 1 • DIR" above "VFL 5 T2": the fold line crosses "DIR" (reads "DI2").
- Bar extents in "Z 59 • Z FW • VFL CL 5 • IMM" and "VFL CL 2 + VFL CL 3 + VFL CL 4 • WBC • VFL CL 2".
- "CYL PREC" (col 3) vs "CYC PREC" (col 1) as printed.
- TON hexagon prints "SAR WBC" (checked at 450 dpi); neighbouring sheets use "SAC" — possibly SAC, kept as PRINTED "SAR".

### Appendix D. Figs 3.2.1-3.2.11 and LAOP table (reader D)

#### Fig 3.2.1 — "IAUC LOAD ENABLE AND ADVANCE CONDITIONS"

- PDF page 92 (landscape fold-out, 5100x3300 at 300 dpi; text upright, not rotated)
- Header: "M3-04-3" / "LA FLOW DIAGRAMS"
- Printed page number at foot: **2-1/2-2**; issue date at foot: **2/1/62**
- No "CPU 7101 SER. NO." applicability note on the sheet.
- Read from 300-dpi tiles t092_*.png (1200x1100 crops), plus junction zooms.

Shapes: rectangles = actions; hexagons = conditions. No E/M sequencer bar on this sheet.
Lettered connectors (A), (B), (C), (D) are circles on lines (on-page connectors).

##### 1. Boxes, verbatim (PRINTED), with ALD page

###### Entry / step section (top left)
| # | shape | text (PRINTED) | ALD (PRINTED) |
|---|---|---|---|
| 1 | entry label | ADVANCE IAUC | — |
| 2 | rect | STEP IAUC TO NEW LEVEL | 38.01.01.1 |
| 3 | rect | INFORM BCU OF NEW IAUC LEVEL | 38.61.01.1 |
| 4 | rect | SET IAUC ADV EN SEQ | 38.01.06.1 |
| 5 | rect | RESET LOAD PULSE MEMORY | 38.01.10.1 |
| 6 | rect | RESET LC, NOOP, IJ AT NEW LEVEL | 36.02.03.1, 33.01.16.1, 36.07.03.1 |
| 7 | hex | DISC IAUC | YES / NO |
| 8 | hex | RECOVERY NEEDED | NO exit drawn (YES not drawn) |
| 9 | hex | LOAD STARTED (upper-left one) | NO exit, annotated "(AES ON)" |
| 10 | rect | RESET IAUC AES | 38.01.01.1 (printed beside the arrow below it) |
| 11 | rect | DROP LOAD ENABLE LINES | — |

###### Load-enable section (top right)
| # | shape | text | ALD / exits |
|---|---|---|---|
| 12 | rect | TYPE 1 & 2 LOAD ENABLE | 38.02.02.1 |
| 13 | rect | TYPE 3 LOAD ENABLE | 38.02.03.1 |
| 14 | hex | BOTH LAARS BUSY | YES / NO |
| 15 | hex | STORE BEING DONE | YES (only exit drawn) |
| 16 | hex | LOAD STARTED (right one) | YES, annotated "(LLP 1/2)"; NO not drawn |
| 17 | hex | MEM FETCH CNCLD | YES / NO |
| 18 | rect | SET IAUC AES | 38.01.06.1 |

###### Load-pulse decode section (middle)
| # | shape | text | exits |
|---|---|---|---|
| 19 | hex | LLP1 | YES / NO |
| 20 | hex | LLP2 | YES / NO (NO line annotated "(LLP3)") |
| 21 | hex | LLP3 MOD | YES / NO |
| 22 | hex | LAOP 33 ECC CHK LOAD | YES / NO |
| 23 | hex | I CHKR ECC ERR | YES (loops back to its own input) / NO |
| 24 | hex | FETCH ACCEPTED AND NO COMPARE | YES (only exit drawn) |
| 25 | rect | SET IAUC LOAD PULSE MEMORY | 38.01.10.1 |
| 26 | junction label | (bus feeding the advance test) | 38.01.09.1 |

###### Advance test (bottom left)
| # | shape | text | exits |
|---|---|---|---|
| 27 | hex | SCC AT NEXT LEVEL | YES / NO |
| 28 | hex | ABC THERE | YES (only exit drawn) |
| 29 | hex | TBC THERE | NO (only exit drawn) |
| 30 | hex | STORE REQUIRED | NO (only exit drawn) |
| 31 | hex | ABC ADVANCING | YES (only exit drawn) |
| 32 | hex | NEXT LEVEL IN ABC (left one) | NO (only exit drawn) |
| 33 | hex | STORE REQ. | YES / NO |
| 34 | hex | STORE DONE | YES, annotated "(STORE DATA M)" |
| 35 | hex | IAUC AES OFF (bottom) | YES -> ADVANCE IAUC, ref 38.01.08.1 |
| 36 | exit label | ADVANCE IAUC | 38.01.08.1 |

###### Load-enable decision chains after load pulse memory (bottom middle/right)
| # | shape | text | exits |
|---|---|---|---|
| 37 | hex | IAUC AES OFF (middle) | YES (only exit drawn) |
| 38 | hex | NEXT LEVEL IN SCC (chain 1, middle) | YES / NO (NO -> connector (D)) |
| 39 | hex | ANY DISC (chain 1) | NO |
| 40 | hex | RECOVERY NEEDED (chain 1) | NO |
| 41 | hex | BOTH LAARS 1&2 BUSY | NO |
| 42 | hex | NEXT LEVEL IN ABC (chain 1) | NO |
| 43 | hex | STORE BEING DONE (chain 1) | YES |
| 44 | hex | NEXT LEVEL IN SCC (chain 2, fed by (A),(B),(D)) | NO |
| 45 | hex | ANY DISC (chain 2) | NO |
| 46 | hex | RECOVERY NEEDED (chain 2) | NO |
| 47 | hex | BOTH LAARS BUSY (chain 2) | YES / NO |
| 48 | hex | STORE BEING DONE (chain 2) | YES |
| 49 | hex | NEXT LEVEL IN SCC (chain 3, fed by (C)) | NO |
| 50 | hex | ANY DISC (chain 3) | NO |
| 51 | hex | RECOVERY NEEDED (chain 3) | NO |
| 52 | hex | BOTH LAARS NOT BUSY | YES |
| 53 | rect | TYPE 1 & 2 LOAD ENABLE (lower) | 38.02.02.1 |
| 54 | rect | TYPE 3 LOAD ENABLE (lower) | 38.02.03.1 |

##### 2. Structure / routing (DERIVED from line tracing; arrowheads checked at full res)

**Entry.** ADVANCE IAUC -> [SET IAUC ADV EN SEQ -> RESET LOAD PULSE MEMORY] and
[RESET LC, NOOP, IJ AT NEW LEVEL] and STEP IAUC TO NEW LEVEL -> INFORM BCU OF NEW IAUC LEVEL,
-> DISC IAUC?
- DISC IAUC YES -> RESET IAUC AES -> DROP LOAD ENABLE LINES; the same YES line also runs down the
  far-left vertical to the 38.01.09.1 bus (the advance test).
- DISC IAUC NO -> RECOVERY NEEDED? NO -> LOAD STARTED? NO (AES ON) -> TYPE 1 & 2 LOAD ENABLE,
  and (via the top line, arrowed rightwards) -> BOTH LAARS BUSY?.
  - BOTH LAARS BUSY NO -> TYPE 3 LOAD ENABLE. YES -> STORE BEING DONE? YES -> TYPE 3 LOAD ENABLE.
- TYPE 1&2 / TYPE 3 LOAD ENABLE -> merge -> LOAD STARTED? YES (LLP 1/2) -> RESET IAUC AES
  (line runs left to that box) and -> MEM FETCH CNCLD?
  - MEM FETCH CNCLD YES -> SET IAUC AES (38.01.06.1) and loops up the right edge back into
    BOTH LAARS BUSY? (merge arrow at the top junction).
  - MEM FETCH CNCLD NO -> LLP1?
- LLP1 YES -> connector (A) -> NEXT LEVEL IN SCC (chain 2); also -> SET IAUC LOAD PULSE MEMORY
  and -> 38.01.09.1 bus.  LLP1 NO -> LLP2?
- LLP2 YES -> FETCH ACCEPTED AND NO COMPARE? and -> connector (B) -> NEXT LEVEL IN SCC (chain 2).
  LLP2 NO "(LLP3)" -> LLP3 MOD?
- LLP3 MOD YES -> FETCH ACCEPTED AND NO COMPARE?, and also onto the LAOP-33-NO bus.
  LLP3 MOD NO -> LAOP 33 ECC CHK LOAD?
- LAOP 33 ECC CHK LOAD YES -> I CHKR ECC ERR? (YES loops back to its own input = wait while
  error; NO -> SET IAUC LOAD PULSE MEMORY).
  LAOP 33 NO -> 38.01.09.1 bus, -> SET IAUC LOAD PULSE MEMORY, and -> connector (C) ->
  NEXT LEVEL IN SCC (chain 3).
- FETCH ACCEPTED AND NO COMPARE YES -> SET IAUC LOAD PULSE MEMORY.
- SET IAUC LOAD PULSE MEMORY -> 38.01.09.1 bus and -> IAUC AES OFF? (middle)
  - YES -> NEXT LEVEL IN SCC (chain 1): YES -> ANY DISC (chain 1) and -> NEXT LEVEL IN ABC (left,
    advance-section); NO -> connector (D) -> joins chain 2 below NEXT LEVEL IN SCC (into ANY DISC).

**Chain 1** ANY DISC NO -> RECOVERY NEEDED NO -> BOTH LAARS 1&2 BUSY NO -> NEXT LEVEL IN ABC NO ->
STORE BEING DONE YES -> TYPE 1 & 2 LOAD ENABLE (arrow up into it) and -> TYPE 3 LOAD ENABLE.
**Chain 2** ANY DISC NO -> RECOVERY NEEDED NO -> TYPE 1 & 2 LOAD ENABLE and -> BOTH LAARS BUSY?
(YES -> STORE BEING DONE YES -> TYPE 3; NO -> TYPE 3).
**Chain 3** NEXT LEVEL IN SCC NO -> ANY DISC NO -> RECOVERY NEEDED NO -> TYPE 1 & 2 LOAD ENABLE
and -> BOTH LAARS NOT BUSY? YES -> TYPE 3 LOAD ENABLE.

**Advance test (38.01.09.1 bus)** -> SCC AT NEXT LEVEL?
- NO -> straight down to the advance junction.
- YES -> ABC THERE? YES -> TBC THERE? NO -> STORE REQUIRED? NO -> ABC ADVANCING? YES -> junction.
- Also into the junction: NEXT LEVEL IN ABC (left, fed from chain-1's NEXT LEVEL IN SCC YES)
  NO -> STORE REQ.? NO -> junction; YES -> STORE DONE? YES (STORE DATA M) -> junction.
- Junction -> IAUC AES OFF? YES -> ADVANCE IAUC (38.01.08.1).

##### 3. Step table
| step | condition(s) (PRINTED) | action(s) (PRINTED) | ALD | notes |
|---|---|---|---|---|
| on advance | — | SET IAUC ADV EN SEQ; RESET LOAD PULSE MEMORY; RESET LC, NOOP, IJ AT NEW LEVEL; STEP IAUC TO NEW LEVEL; INFORM BCU OF NEW IAUC LEVEL | 38.01.06.1; 38.01.10.1; 36.02.03.1, 33.01.16.1, 36.07.03.1; 38.01.01.1; 38.61.01.1 | |
| disc | DISC IAUC YES | RESET IAUC AES; DROP LOAD ENABLE LINES | 38.01.01.1 | disconnected level skipped |
| enable | DISC IAUC NO, RECOVERY NEEDED NO, LOAD STARTED NO (AES ON) | TYPE 1 & 2 LOAD ENABLE | 38.02.02.1 | |
| enable 3 | BOTH LAARS BUSY NO, or BOTH LAARS BUSY YES and STORE BEING DONE YES | TYPE 3 LOAD ENABLE | 38.02.03.1 | [KEY] LAAR gate |
| load | LOAD STARTED YES (LLP 1/2) | RESET IAUC AES | 38.01.01.1 | |
| cancel | MEM FETCH CNCLD YES | SET IAUC AES; re-test BOTH LAARS BUSY | 38.01.06.1 | [KEY] fetch cancelled |
| pulses | LLP1 / LLP2 / LLP3 MOD / LAOP 33 ECC CHK LOAD & I CHKR ECC ERR NO / FETCH ACCEPTED AND NO COMPARE | SET IAUC LOAD PULSE MEMORY | 38.01.10.1 | |
| advance | SCC AT NEXT LEVEL NO; or SCC AT NEXT LEVEL YES & ABC THERE & TBC THERE NO & STORE REQUIRED NO & ABC ADVANCING; or NEXT LEVEL IN ABC NO & (STORE REQ. NO or STORE DONE YES (STORE DATA M)); and then IAUC AES OFF YES | ADVANCE IAUC | 38.01.08.1 | interlock IAUC vs SCC/ABC |

##### 4. Counters, timers, triggers, registers, LAOPs named
- Counters: IAUC, SCC, ABC, TBC (OCC not named on this sheet).
- Triggers/sequences: IAUC ADV EN SEQ, IAUC AES, LOAD PULSE MEMORY, IAUC LOAD PULSE MEMORY.
- Tags reset at new level: LC, NOOP, IJ (IJ is an indicator, ALD 33.01.16.1).
- Pulses: LLP1, LLP2, LLP3 (LLP3 MOD), "LLP 1/2".
- LAARs: "BOTH LAARS BUSY", "BOTH LAARS 1&2 BUSY", "BOTH LAARS NOT BUSY".
- Timer: "STORE DATA M" (annotation on STORE DONE YES).
- LAOP: **33** ("LAOP 33 ECC CHK LOAD").
- Load-enable classes: TYPE 1 & 2, TYPE 3.

##### 5. TIME
PRINTS NO TIME. (The only timing-flavoured token is the trigger name "STORE DATA M".)

##### 6. [KEY] items, verbatim
- [KEY] "BOTH LAARS BUSY" (twice), "BOTH LAARS 1&2 BUSY", "BOTH LAARS NOT BUSY" — LAAR occupancy gates TYPE 3 LOAD ENABLE.
- [KEY] "STORE BEING DONE" (three boxes) — a busy LAAR is acceptable if its store is in progress.
- [KEY] "STORE REQ." / "STORE REQUIRED" / "STORE DONE (STORE DATA M)" — gate IAUC advance onto an SCC level.
- [KEY] "SCC AT NEXT LEVEL", "NEXT LEVEL IN SCC", "NEXT LEVEL IN ABC", "ABC THERE", "TBC THERE", "ABC ADVANCING" — the IAUC advance interlock.
- [KEY] "RECOVERY NEEDED" (four boxes) — I-unit recovery blocks load enables.
- [KEY] "MEM FETCH CNCLD" -> "SET IAUC AES"; "FETCH ACCEPTED AND NO COMPARE" (address compare tied to fetch acceptance).

##### 7. Interlocks between counters (PRINTED condition names)
- IAUC vs SCC: "SCC AT NEXT LEVEL"; "NEXT LEVEL IN SCC".
- IAUC vs ABC: "ABC THERE", "ABC ADVANCING", "NEXT LEVEL IN ABC".
- IAUC vs TBC: "TBC THERE".
- IAUC self: "IAUC AES OFF" before ADVANCE IAUC.

##### 8. Could not read / uncertain
- All box text legible. Missing exits (not drawn, not illegible): RECOVERY NEEDED YES, LOAD STARTED YES (left) / NO (right), STORE BEING DONE NO, ABC THERE NO, TBC THERE YES, STORE REQUIRED YES, ABC ADVANCING NO, IAUC AES OFF NO, etc.
- DERIVED uncertainty: direction of flow on the top line between TYPE 1 & 2 and the BOTH LAARS BUSY junction is inferred from the arrowheads (rightward arrow before the junction, leftward arrow from the MEM-FETCH-CNCLD loop).

##### 9. Comparison with spec_lookahead.md (read-only)
- §0 (lists PDF 92 as read): AGREE on title, header, date 2/1/62.
- §1.4 "BOTH LAARS BUSY / BOTH LAARS 1&2 BUSY / BOTH LAARS NOT BUSY": AGREE, all three printed.
- §2.1 "SCC AT NEXT LEVEL; if yes ... ABC THERE -> TBC THERE -> STORE REQUIRED -> ABC ADVANCING": AGREE.
  REFINEMENT (not a contradiction): the sheet also lets the IAUC advance via NEXT LEVEL IN ABC NO -> STORE REQ. NO,
  or STORE REQ. YES -> STORE DONE (STORE DATA M); and requires IAUC AES OFF on every path. §2.1's one-line rule
  "IAUC may not advance onto the level the SCC still occupies" is coarser than the printed test
  (the IAUC may move onto an SCC-held level when ABC is there, TBC is not, no store is required and ABC is advancing).
- §2.1 "Each counter also carries an AES trigger ... counter advances when AES is off": AGREE for IAUC (IAUC AES OFF -> ADVANCE IAUC).

#### Fig 3.2.2 — "LOOKAHEAD LOAD PULSES (SHEET 1 OF 2)"

- PDF page 93 (portrait). Header "M3-04-3" / "LA FLOW DIAGRAMS".
- Printed page at foot: **2-3**; issue date at foot: **2/1/62**. No serial-number note.
- Read at 450 dpi (h93_*.png) and 600 dpi (x93*.png). The scan is badly faded in the LLP 2 lower half; many ALD refs are degraded ("3c" = 36 with the 6 broken).

Structure: two horizontal pulse bars, "LLP 1" and "LLP 2", each fanning out to boxes. No E/M sequencer.

##### 1. Boxes (PRINTED unless marked)

###### LLP 1 bar
| box | shape | text | ALD |
|---|---|---|---|
| a | rect | GI TAG BITS & OP CODE FIELD EXCEPT BIT 8 | 36.10.01.1 (printed "3c.10.01.1", 6 degraded) |
| b | hex | LAOP 45 ? | YES / NO |
| c | rect (LAOP 45 NO) | GI OP CODE BIT 8 | 36.09.01.1 ("3c.09.01.1") |
| d | hex (LAOP 45 YES) | I CHKR PARITY ERROR ? | YES only |
| e | rect (d YES) | SET OP BIT 8 | 36.09.02.1 ("3c.09.02.1") |
| f | rect | GI I BOX IND'S TO IND. FIELD | 35.09.01.1 |
| g | rect | GI IC TO IC FIELD | 35.09.01.1 |
| h | rect | GI ICOB TO DATA FIELD | 35.02.01.1 |
| i | hex | I CHKR PARITY ERROR ? (second) | YES only |
| j | hex (i YES) | PSEUDO STORE OR RECOVERY LEVEL ? | YES / NO |
| k | rect (j YES) | SET CNIDC IND | 38.03.05.1 |
| l | rect (j NO) | SET IJ IND | 33.01.16.1 |
| m | rect (j NO) | SET NOOP TAG | 35.09.04.1 (first digits faint) |
| n | rect | SET LF & LC TAGS | 36.01.10.1 |

###### LLP 2 bar
| box | shape | text | ALD |
|---|---|---|---|
| o | rect | GI TAG BITS & OP CODE FIELD | ILLEGIBLE: two refs, faded; read as "3c.1?.0?.?" / "3c.09.0?.?" (DERIVED 36.10.0x.1 / 36.09.0x.1) |
| p | rect | G[I] I BOX IND'S TO IND FIELD | "35.09.01.1" (faint) ; "I" after G ILLEGIBLE (faded) |
| q | rect | GI IC TO IC FIELD | 35.09.01.1 |
| r | hex | IS LAAR COMPARE ENABLED ? | YES / NO; ALD 36.16.07.1 under the hexagon |
| s | hex (r YES) | ADDRESS COMPARE ? | NO only (no YES exit drawn) |
| t | hex (r NO, s NO) | DATA ON IMOB | YES only |
| u | rect (t YES, line labelled "MEM SEL LA 1") | SET LF E TRIGGER | "3c.01.05.1" (DERIVED 36.01.05.1, faint) |
| v | rect (u) | SET LF TAG | "3?.01.01.1" ILLEGIBLE: faint |
| w | rect (u) | GI IMOB INTO DATA FIELD | "35.32.01.1"? faint (DERIVED; middle digits uncertain) |
| x | hex (t YES) | BOUNDARY ALARM ? | YES only |
| y | rect (x YES) | SET DF OR DS IND | 35.09.02.1, 35.09.04.1 |
| z | rect (x YES) | SET NOOP TAG | 35.09.02.1 |
| aa | hex (t YES) | MEM CHK ALARM ? | YES only |
| bb | rect (aa YES) | SET IJ IND | ILLEGIBLE: faded, reads "3?.0?.1?.1" (DERIVED 33.01.16.1 by analogy, not printed-legible) |
| cc | rect (aa YES) | SET [?] NOOP TAG | ILLEGIBLE: second word of first line and ref faded ("SET  \\  NOOP T.G"); ref unreadable |

##### 2. Structure (DERIVED)
- LLP 1: fans out to a, b, f, g, (h & i), n in parallel. b: LAOP 45 NO -> c; YES -> d (YES -> e).
  i (I CHKR PARITY ERROR) YES -> j: YES -> k (SET CNIDC IND); NO -> l (SET IJ IND) and m (SET NOOP TAG).
- LLP 2: fans out to o, p, q, r. r NO -> t; r YES -> s; s NO -> t. t YES -> u ("MEM SEL LA 1") -> v and w;
  t YES also -> x and aa. x YES -> y and z. aa YES -> bb and cc.

##### 3. Step table
| step | condition (PRINTED) | action (PRINTED) | ALD | notes |
|---|---|---|---|---|
| LLP 1 | — | GI TAG BITS & OP CODE FIELD EXCEPT BIT 8; GI I BOX IND'S TO IND. FIELD; GI IC TO IC FIELD; GI ICOB TO DATA FIELD; SET LF & LC TAGS | 36.10.01.1; 35.09.01.1; 35.09.01.1; 35.02.01.1; 36.01.10.1 | I-box-supplied operand |
| LLP 1 | LAOP 45 NO | GI OP CODE BIT 8 | 36.09.01.1 | |
| LLP 1 | LAOP 45 YES & I CHKR PARITY ERROR | SET OP BIT 8 | 36.09.02.1 | |
| LLP 1 | I CHKR PARITY ERROR & PSEUDO STORE OR RECOVERY LEVEL | SET CNIDC IND | 38.03.05.1 | [KEY] |
| LLP 1 | I CHKR PARITY ERROR & not pseudo-store/recovery | SET IJ IND; SET NOOP TAG | 33.01.16.1; 35.09.04.1 | [KEY] |
| LLP 2 | — | GI TAG BITS & OP CODE FIELD; GI I BOX IND'S TO IND FIELD; GI IC TO IC FIELD | faint | memory operand |
| LLP 2 | LAAR compare not enabled, or ADDRESS COMPARE NO; DATA ON IMOB YES (MEM SEL LA 1) | SET LF E TRIGGER -> SET LF TAG, GI IMOB INTO DATA FIELD | see table | [KEY] |
| LLP 2 | BOUNDARY ALARM | SET DF OR DS IND; SET NOOP TAG | 35.09.02.1, 35.09.04.1; 35.09.02.1 | |
| LLP 2 | MEM CHK ALARM | SET IJ IND; SET [?] NOOP TAG | ILLEGIBLE | |

##### 4. Named items
- Pulses: LLP 1, LLP 2. Tags: OP CODE BIT 8 (OP BIT 8), LF, LC, NOOP, LF E TRIGGER. Indicators: CNIDC IND, IJ IND, DF OR DS IND.
- Buses/registers: ICOB, IMOB, IC field, IND field, DATA field. LAAR (compare). "MEM SEL LA 1".
- LAOP: **45**.
- No counters named.

##### 5. TIME
PRINTS NO TIME.

##### 6. [KEY] verbatim
- [KEY] "PSEUDO STORE OR RECOVERY LEVEL ?" -> YES "SET CNIDC IND" (38.03.05.1); NO "SET IJ IND" + "SET NOOP TAG".
- [KEY] "IS LAAR COMPARE ENABLED ?" (36.16.07.1) -> "ADDRESS COMPARE ?" (NO -> DATA ON IMOB). The YES exit of ADDRESS COMPARE is NOT drawn on this sheet (checked at 450 dpi): what happens on a compare (forwarding / wait) is not shown here.
- [KEY] "MEM SEL LA 1" (label on the line into SET LF E TRIGGER).

##### 7. Interlocks
None between counters on this sheet.

##### 8. Could not read
- LLP 2 refs under GI TAG BITS & OP CODE FIELD (two lines), SET LF E TRIGGER, SET LF TAG, GI IMOB INTO DATA FIELD: faded; partially read only.
- SET IJ IND (under MEM CHK ALARM): ref faded. Box "SET ? NOOP TAG" (under MEM CHK ALARM): one token after SET and the ref ILLEGIBLE (faded).

##### 9. Comparison with spec_lookahead.md
- §0 lists PDF 93 as read: AGREE (sheet 1 of 2, LLP 1 and LLP 2).
- §2.3 table/para: "IS LAAR COMPARE ENABLED?" (logic 36.16.07.1) feeding "ADDRESS COMPARE?" feeding "DATA ON IMOB": AGREE; the "no-compare path going on to set LF E trigger -> set LF tag + gate IMOB into data field": AGREE.
- §2.7: "LLP 1 checks I CHKR PARITY ERROR? -> PSEUDO STORE OR RECOVERY LEVEL? Yes -> SET CNIDC IND / No -> SET IJ IND + SET NOOP TAG": AGREE. "LLP 2 checks BOUNDARY ALARM? -> SET DF OR DS IND + SET NOOP TAG": AGREE. "MEM CHK ALARM? -> SET IJ IND + SET NOOP TAG": AGREE in structure; the second box's wording and both refs are too faded to confirm from this scan.
- §3.7 "names LLP 1, LLP 2, LLP 3 as discrete pulses": this sheet names LLP 1 and LLP 2 only; LLP 3 is on sheet 2 (PDF 94). Minor.

#### Fig 3.2.2 — "LOOKAHEAD LOAD PULSES (SHEET 2 OF 2)"

- PDF page 94 (portrait). Header "LA FLOW DIAGRAMS" / "M3-04-3".
- Printed page at foot: **2-4**; issue date: **2/1/62**. No serial-number note.
- Read at 450 dpi (h94_*.png) and 600 dpi. Lower-left and lower-middle refs faded.

Structure: one pulse bar "LLP 3" fanning out. No E/M sequencer.

##### 1. Boxes
| box | shape | text (PRINTED) | ALD / exits |
|---|---|---|---|
| a | rect | GI TAG BITS AND OP CODE | 36.10.01.1, 36.09.01.1 |
| b | rect | GI I-BOX IND'S TO IND FIELD | 35.09.01.1 |
| c | rect | GI IC TO IC FIELD | 35.09.01.1 |
| d | rect | I BOX WILL LOAD LAAR 1 OR 2 | (no ref) |
| e | hex | LAAR 1 BUSY | YES / NO |
| f | hex (e NO) | MOD TYPE 3 | YES / NO |
| g | hex (f YES) | FETCH ACCEPTED | YES |
| h | rect (f NO, g YES) | SET FROM 1 & LAAR 1 BUSY | 36.16.02.1, 38.53.01.1 |
| i | hex (e YES) | MOD TYPE 3 | YES / NO |
| j | hex (i YES) | FETCH ACCEPTED | YES |
| k | rect (i NO, j YES) | SET FROM 2 & LAAR 2 BUSY | 36.16.02.1, 38.53.01.1 |
| l | hex | LAOP 33 ECC CHK LOAD | YES / NO |
| m | rect (l YES) | GI ICOB WITH ECC | (no ref) |
| n | hex (l YES) | ECC ERROR | YES / NO |
| o | hex-like (n YES) | LAOP 33 ECC CORRECT LOAD | (second "3" degraded; read 33) — single exit |
| p | rect | SET LF & LC TAGS | 36.02.02.1, 36.01.10.1 |
| q | rect (o) | GI ICOB WITH ECC (lower left) | "3?.0?.07.1" ILLEGIBLE-partial (DERIVED 38.03.07.1) |
| r | hex (o) | UNCORR ECC ERR | YES |
| s | rect (r YES) | SET NOOP TAG | "3?.0?.?2.1" ILLEGIBLE-partial (DERIVED 36.07.02.1) |
| t | hex (l NO) | MODIFIED TYPE 3 | NO (YES not drawn) |
| u | hex (t NO) | I BOX STORE | YES |
| v | hex (u YES) | I-PAR ERROR | YES |
| w | rect (v YES) | SET IJ & NOOP | "3?.01.16.1", "3?.09.04.1" faint (DERIVED 33.01.16.1 / 35.09.04.1) |
| x | rect (u YES) | GI ICOB WITH ECC | 38.03.07.1 |

##### 2. Structure (DERIVED)
LLP 3 fans out to a, b, c, d, e and l.
- e LAAR 1 BUSY NO -> f MOD TYPE 3: NO -> h; YES -> g FETCH ACCEPTED YES -> h (SET FROM 1 & LAAR 1 BUSY).
- e LAAR 1 BUSY YES -> i MOD TYPE 3: NO -> k; YES -> j FETCH ACCEPTED YES -> k (SET FROM 2 & LAAR 2 BUSY).
- l LAOP 33 ECC CHK LOAD YES -> m (GI ICOB WITH ECC) and n ECC ERROR: NO -> p; YES -> o (LAOP 33 ECC CORRECT LOAD) -> p, q, r. r UNCORR ECC ERR YES -> s SET NOOP TAG.
- l NO -> t MODIFIED TYPE 3 NO -> p (SET LF & LC TAGS) and u I BOX STORE: YES -> v I-PAR ERROR YES -> w; and -> x.

##### 3. Step table
| step | condition (PRINTED) | action (PRINTED) | ALD | notes |
|---|---|---|---|---|
| LLP 3 | — | GI TAG BITS AND OP CODE; GI I-BOX IND'S TO IND FIELD; GI IC TO IC FIELD; I BOX WILL LOAD LAAR 1 OR 2 | 36.10.01.1, 36.09.01.1; 35.09.01.1; 35.09.01.1 | |
| LLP 3 | LAAR 1 BUSY NO & (MOD TYPE 3 NO, or MOD TYPE 3 YES & FETCH ACCEPTED) | SET FROM 1 & LAAR 1 BUSY | 36.16.02.1, 38.53.01.1 | [KEY] LAAR 1 chosen first |
| LLP 3 | LAAR 1 BUSY YES & (same) | SET FROM 2 & LAAR 2 BUSY | 36.16.02.1, 38.53.01.1 | [KEY] |
| LLP 3 | LAOP 33 ECC CHK LOAD | GI ICOB WITH ECC | — | |
| LLP 3 | ECC ERROR NO | SET LF & LC TAGS | 36.02.02.1, 36.01.10.1 | |
| LLP 3 | ECC ERROR YES | LAOP 33 ECC CORRECT LOAD -> SET LF & LC TAGS; GI ICOB WITH ECC; (UNCORR ECC ERR -> SET NOOP TAG) | faint | |
| LLP 3 | LAOP 33 NO, MODIFIED TYPE 3 NO | SET LF & LC TAGS | 36.02.02.1, 36.01.10.1 | |
| LLP 3 | I BOX STORE | GI ICOB WITH ECC; (I-PAR ERROR -> SET IJ & NOOP) | 38.03.07.1 | |

##### 4. Named items
- Pulse LLP 3. LAAR 1, LAAR 2, LAAR 1 BUSY, LAAR 2 BUSY (38.53.01.1), FROM 1 / FROM 2 tags (36.16.02.1 printed under BOTH boxes).
- Tags: LF, LC, NOOP, IJ. Buses: ICOB, IC field, IND field.
- LAOP: **33** (twice: "LAOP 33 ECC CHK LOAD", "LAOP 33 ECC CORRECT LOAD").
- Classes: MOD TYPE 3, MODIFIED TYPE 3, I BOX STORE.

##### 5. TIME
PRINTS NO TIME.

##### 6. [KEY] verbatim
- [KEY] **LAAR assignment rule**: "I BOX WILL LOAD LAAR 1 OR 2"; "LAAR 1 BUSY" NO -> "SET FROM 1 & LAAR 1 BUSY"; YES -> "SET FROM 2 & LAAR 2 BUSY". i.e. LAAR 1 if free, else LAAR 2 (DERIVED reading of the printed routing; verified at 450 dpi).
- [KEY] "MOD TYPE 3" -> "FETCH ACCEPTED" gates the SET FROM/LAAR BUSY for modified type-3 loads.
- [KEY] "I BOX STORE" -> "GI ICOB WITH ECC" (38.03.07.1): I-box store operand converted to ECC on loading.

##### 7. Interlocks
None between counters.

##### 8. Could not read
- Refs under lower-left GI ICOB WITH ECC, SET NOOP TAG, SET IJ & NOOP: faded, digits 3/5/6/8 not distinguishable (values given above are DERIVED).
- "LAOP 33 ECC CORRECT LOAD": the second digit is broken; read as 3 at 300 dpi.

##### 9. Comparison with spec_lookahead.md
- §0 says PDF 94 was "rendered but not read". §1.4: "CE PDF 94 (LA load pulses sheet 2) routes 'LAAR 1 OR 2'": AGREE ("I BOX WILL LOAD LAAR 1 OR 2").
- **DISAGREE with §6.2 item 4** ("What is [NOT IN THE SOURCES] is the assignment rule — which LAAR the I-box claims when both are free ... Round-robin is a modelling choice") and with §1.4's "allocated round-robin ('LAAR n NEXT')": PDF 94 prints the assignment: LAAR 1 BUSY? NO -> SET FROM 1 & LAAR 1 BUSY; YES -> SET FROM 2 & LAAR 2 BUSY. That is fixed priority to LAAR 1, not round-robin.
- §1.3 table gives FROM BIT 2 at logic page 36.13.03.1; PDF 94 prints **36.16.02.1** under both SET FROM 1 and SET FROM 2 boxes. Reported as printed; the trigger-index page may differ from the flow-chart page.

#### Fig 3.2.3 — "OPERAND CHECK AND CORRECT PHASE OF INSTRUCTION PREPARATION"

- PDF page 95 (portrait). Header "M3-04-3" / "LA FLOW DIAGRAMS".
- Printed page at foot: **2-5**; issue date: **2/1/62**. No serial-number note.
- Read at 300 dpi tiles (t95_*.png) and 600-dpi crops of the timer phase labels. Crisp scan.

##### 1. Boxes (PRINTED)
| box | shape | text | ALD / exits |
|---|---|---|---|
| a | entry | ADVANCE OCC | |
| b | rect | SET OCC AES | 38.11.06.1 |
| c | rect | STEP OCC TO NEXT LEVEL ("NFXT" misprint) | 38.11.01.1 |
| d | hex | DISC OCC | YES / NO |
| e | hex | OPD CHK REQ | NO "(LC ON)" / YES "(LF NOT LC" |
| f | hex | CHK STARTED | NO "(OCC AES ON)" (YES not drawn) |
| g | rect | 3RD PRIORITY CHKR REQUEST | 38.12.01.1 |
| h | hex | CHKR IN USE | NO "(NO "0" REQ)" / YES (loops back to g) |
| i | rect | DROP "OK TO I CHK" LINE | 35.01.02.1 |
| j | rect | PREVENT I BOX CHKER CYCLES | — |
| k | hex | IS CHKR NEED BY LAST USER FOR CORR CYC | NO "(NO SINGLE ECC ERR)" / YES (loops back to g) |
| l | timer bar | START OPERAND CHECK TIMER | 35.05.01.1; phase lines **E**, **EM̄** (overbar on M, clear at 600 dpi), **M**, **EM** |
| m | rect (E) | GO DATA FIELD TO ICIB ("FIELC" misprint) | 35.10.02.1 |
| n | rect (EM̄) | RESET OCC AES | — |
| o | rect (EM̄) | DROP "NO 0 REQ" LINE TO HOLD I CHKR PRIORITY | — |
| p | hex (EM̄) | PANEL KEYS OR INVALID ADDRESS | NO / YES "(OCC INT FETCH TAG)" |
| q | rect (p NO) | SIGNAL I CHKR TO CHK ECC | 35.15.01.1 |
| r | rect (p YES) | SIGNAL I CHKR TO GENERATE PARITY | 35.15.01.1 |
| s | rect (M) | GI ICOB DATA PARITY RESIDUE | 35.10.01.1 |
| t | hex (M) | ECC ERROR | single unlabelled exit to u |
| u | rect | SET LC TAG | 35.15.01.1 |
| v | hex (EM) | ECC ERROR | NO / YES |
| w | timer bar | START OPERAND CORRECT TIMER | 35.05.02.1; phase lines **E**, **EM** (overbar on M possible but not certain at 600 dpi), **EM**, plus one unlabelled line at right |
| x | rect (v YES, and E) | CONTINUE GATING DATA TO ICIB | 35.10.02.1 |
| y | rect (first EM) | DROP "NO 0 REQ" LINE TO HOLD CHKR PRIOR | — |
| z | rect (right line) | GI ICOB AGAIN | — |
| aa | rect (right line) | SET LC TAG | — |
| bb | hex (right line) | DBL ERR | YES |
| cc | rect (bb YES) | SET IJ IND NOOP TAG | 33.01.16.1, 36.07.07.1 |
| dd | hex | IS IAUC IN THIS LEVEL | NO -> ADVANCE OCC |

##### 2. Structure
Sequencers: two timers drawn as horizontal bars with labelled phase drops.
- **START OPERAND CHECK TIMER** (35.05.01.1). TON: IS CHKR NEED BY LAST USER FOR CORR CYC NO "(NO SINGLE ECC ERR)". Phases: E -> GO DATA FIELD TO ICIB; EM̄ -> RESET OCC AES, DROP "NO 0 REQ" LINE TO HOLD I CHKR PRIORITY, PANEL KEYS OR INVALID ADDRESS?; M -> GI ICOB DATA PARITY RESIDUE, ECC ERROR? -> SET LC TAG; EM -> ECC ERROR? (NO -> advance bus; YES -> correct timer).
- **START OPERAND CORRECT TIMER** (35.05.02.1). TON: ECC ERROR YES (EM phase of check timer). Phases: E -> CONTINUE GATING DATA TO ICIB; EM -> DROP "NO 0 REQ" LINE TO HOLD CHKR PRIOR; EM (third line) -> advance bus (DERIVED: label sits right of this line); unlabelled rightmost line -> GI ICOB AGAIN, SET LC TAG, DBL ERR? (YES -> SET IJ IND NOOP TAG).
- TOF conditions: not printed.
- Advance bus collects: DISC OCC YES; OPD CHK REQ NO (LC ON); ECC ERROR (EM) NO; the correct timer's EM line. Bus -> IS IAUC IN THIS LEVEL? NO -> ADVANCE OCC.

##### 3. Step table
| step / phase | condition (PRINTED) | action (PRINTED) | ALD | notes |
|---|---|---|---|---|
| advance | — | SET OCC AES; STEP OCC TO NEXT LEVEL | 38.11.06.1; 38.11.01.1 | |
| skip | DISC OCC YES, or OPD CHK REQ NO (LC ON) | to advance test | | |
| request | OPD CHK REQ YES (LF NOT LC), CHK STARTED NO (OCC AES ON) | 3RD PRIORITY CHKR REQUEST | 38.12.01.1 | [KEY] checker priority |
| wait | CHKR IN USE YES, or IS CHKR NEED BY LAST USER FOR CORR CYC YES | loop to 3RD PRIORITY CHKR REQUEST | | [KEY] |
| grant | CHKR IN USE NO (NO "0" REQ) | DROP "OK TO I CHK" LINE; PREVENT I BOX CHKER CYCLES | 35.01.02.1 | [KEY] OCC blocks I-box checker use |
| check E | — | GO DATA FIELD TO ICIB | 35.10.02.1 | |
| check EM̄ | — | RESET OCC AES; DROP "NO 0 REQ" LINE TO HOLD I CHKR PRIORITY | | |
| check EM̄ | PANEL KEYS OR INVALID ADDRESS NO / YES (OCC INT FETCH TAG) | SIGNAL I CHKR TO CHK ECC / SIGNAL I CHKR TO GENERATE PARITY | 35.15.01.1 | |
| check M | — | GI ICOB DATA PARITY RESIDUE | 35.10.01.1 | |
| check M | ECC ERROR | SET LC TAG | 35.15.01.1 | |
| check EM | ECC ERROR NO | to advance test | | |
| correct | ECC ERROR YES | START OPERAND CORRECT TIMER; CONTINUE GATING DATA TO ICIB | 35.05.02.1; 35.10.02.1 | |
| correct EM | — | DROP "NO 0 REQ" LINE TO HOLD CHKR PRIOR | | |
| correct (right line) | — | GI ICOB AGAIN; SET LC TAG | | |
| correct | DBL ERR YES | SET IJ IND NOOP TAG | 33.01.16.1, 36.07.07.1 | |
| advance test | IS IAUC IN THIS LEVEL NO | ADVANCE OCC | | **OCC interlocked by IAUC** |

##### 4. Named items
- Counters: OCC, IAUC. Triggers: OCC AES. Timers: OPERAND CHECK TIMER, OPERAND CORRECT TIMER.
- Lines: "OK TO I CHK", "NO 0 REQ" ("NO "0" REQ"). Checker: I CHKR / CHKR, 3RD PRIORITY CHKR REQUEST.
- Buses/registers: ICIB, ICOB, DATA FIELD. Tags: LC, LF, OCC INT FETCH TAG, NOOP. Indicator: IJ.
- No LAOP codes.

##### 5. TIME
Prints phase names only (E, EM̄, M, EM on the check timer; E, EM, EM on the correct timer). No durations, no cycle counts, no A/B pulses.

##### 6. [KEY] verbatim
- [KEY] "3RD PRIORITY CHKR REQUEST" (38.12.01.1); "CHKR IN USE" loop; "IS CHKR NEED BY LAST USER FOR CORR CYC" — OCC is third priority on the shared I-checker.
- [KEY] "DROP "OK TO I CHK" LINE" -> "PREVENT I BOX CHKER CYCLES".
- [KEY] "DROP "NO 0 REQ" LINE TO HOLD I CHKR PRIORITY" / "...TO HOLD CHKR PRIOR".

##### 7. Interlocks
- OCC vs IAUC: "IS IAUC IN THIS LEVEL" NO -> ADVANCE OCC.

##### 8. Could not read
- Whether the first EM line of the correct timer carries an overbar (EM̄) — uncertain at 600 dpi.
- Ownership of the correct timer's third "EM" label between two adjacent lines is DERIVED.

#### Fig 3.2.4 — "BASIC TBC ADVANCE CONDITIONS"

- PDF page 96 (portrait). Header "LA FLOW DIAGRAMS" / "M3-04-3".
- Printed page at foot: **2-6**; issue date: **2/1/62**. No serial-number note.
- Read at 300 dpi (t96_*.png) and 600 dpi (HSC label). **No ALD page references are printed anywhere on this sheet.**

##### 1. Boxes (PRINTED)
| box | shape | text | exits |
|---|---|---|---|
| a | entry | ADV | |
| b | rect | SET TBC AES | |
| c | rect | TBC AT NEW LEVEL | |
| d | hex | DISC / HSC IN MODE / NOOP MODE ? | YES / NO |
| e | rect | EXECUTE IF REQUIRED | |
| f | rect | SPECIAL CASES | |
| g | hex | TBC EXECUTED ? | YES / NO |
| h | rect | RESET TBC AES (g YES) | |
| i | hex | ABC TRANS INDS ONLY ? | YES / NO |
| j | rect | RESET TBC AES (i YES) | |
| k | hex | ABC TNT FETCH ? (printed "TNT"; DERIVED: INT) | YES / NO |
| l | rect | RESET TBC AES (k YES) | |
| m | hex | ABC STORE ACTION ? | YES (NO not drawn) |
| n | rect | RESET TBC AES (m YES) | |
| o | rect | TBC SINGLE ADV. COND | |
| p | rect | TBC MULTIPLE ADV. COND | |
| q | hex | TBC AES OFF ? | YES |
| r | rect | ADVANCE TBC IF NOT INTLKD BY OCC | |

##### 2. Structure (DERIVED)
ADV -> SET TBC AES; -> TBC AT NEW LEVEL -> d.
- d YES -> (left vertical) TBC SINGLE ADV. COND -> ADVANCE TBC IF NOT INTLKD BY OCC.
- d NO -> EXECUTE IF REQUIRED -> (i) SPECIAL CASES -> joins the single-advance vertical; (ii) TBC MULTIPLE ADV. COND -> TBC AES OFF? YES -> ADVANCE TBC IF NOT INTLKD BY OCC; (iii) the chain g -> i -> k -> m, each YES -> RESET TBC AES, each NO -> next test.
- The single-advance path does NOT pass through TBC AES OFF; the multiple-advance path does.

##### 3. Step table
| step | condition (PRINTED) | action (PRINTED) | notes |
|---|---|---|---|
| advance | — | SET TBC AES; TBC AT NEW LEVEL | |
| bypass | DISC / HSC IN MODE / NOOP MODE YES | TBC SINGLE ADV. COND | [KEY] housecleaning bypass |
| normal | NO | EXECUTE IF REQUIRED | |
| AES reset | TBC EXECUTED / ABC TRANS INDS ONLY / ABC TNT FETCH / ABC STORE ACTION | RESET TBC AES (4 boxes) | |
| advance | single path, or TBC AES OFF YES | ADVANCE TBC IF NOT INTLKD BY OCC | interlock |

##### 4. Named items
Counters TBC, ABC, OCC. Trigger TBC AES. Modes: DISC, "HSC IN MODE" (DERIVED: housecleaning mode; printed "HSC IN", not "HSCLN"), NOOP MODE. No LAOP codes. No registers.

##### 5. TIME
PRINTS NO TIME.

##### 6. [KEY] verbatim
- [KEY] "DISC HSC IN MODE NOOP MODE ?" (housecleaning mode sends TBC down the single-advance path).

##### 7. Interlocks
- TBC vs OCC: "ADVANCE TBC IF NOT INTLKD BY OCC".
- TBC waits on ABC actions: "ABC TRANS INDS ONLY", "ABC TNT FETCH", "ABC STORE ACTION" reset TBC AES.

##### 8. Could not read
Nothing illegible. "TNT" is printed as such (misprint for INT, DERIVED).

##### 9. Comparison with spec_lookahead.md
- §2.1 "CE manual PDF 96 (Fig 3.2.4), terminal box, verbatim: ADVANCE TBC IF NOT INTLKD BY OCC": AGREE.
- §2.1 "'SET TBC AES' on arrival, then 'RESET TBC AES' on each of five alternative completions (TBC EXECUTED / ABC TRANS INDS ONLY / ABC INT FETCH / ABC STORE ACTION)": **DISAGREE on the count** — there are **four** RESET TBC AES boxes / completions, matching the four the spec itself lists; "five" is wrong. Also the third is printed "ABC TNT FETCH" (spec silently corrects to INT).
- §2.1 "then TBC AES OFF? -> ADVANCE TBC IF NOT INTLKD BY OCC": AGREE for the multiple-advance path; the spec omits that the single-advance path (DISC / HSC IN MODE / NOOP MODE, SPECIAL CASES) reaches the ADVANCE box without the AES-OFF test.
- §3.7 "Fig 3.2.4 (PDF 96) gives TBC advance conditions and no times": AGREE.

#### Fig 3.2.5 — "TBC SINGLE ADVANCE CONDITION"

- PDF page 97 (portrait). Header "M3-04-3" / "LA FLOW DIAGRAMS".
- Printed page at foot: **2-7**; issue date: **2/1/62**. No serial-number note.
- Read at 300 dpi (t97_*.png) and 600-dpi crops of the LAOP labels. **No ALD page references printed.**

##### 1. Boxes (PRINTED)
| box | shape | text | exits |
|---|---|---|---|
| a | entry | ADVANCE TBC | |
| b | rect | RESET TBC LDE | |
| c | rect | SET TBC AES | |
| d | rect | STEP TBC TO NEXT LEVEL | |
| e | hex | DISC | YES / NO |
| f | hex | HSCLN MODE | YES / NO |
| g | hex | LF & LC ON | YES |
| h | rect | SET TBC LDE | |
| i | hex | NOOP MODE | YES / NO |
| j | hex | LAST LEVEL | NO "IC OFF" / YES |
| k | hex | EXT STORE | NO / YES |
| l | hex | ABC ACTION COMPLETE OK | YES, annotated "AND CKT 3C" |
| m | hex | ALL PREVIOUS STORES | YES, annotated "STAR BUSY AND NO STORE REQ" and "AND CKT 3A" |
| n | hex | INST DECODED | YES "LDE ON" |
| o | hex | LAOP 45 OR 47 | YES / NO |
| p | hex | BRANCH RECOVERY IN PROG | NO |
| q | hex | LAOP 47 | YES / NO |
| r | hex | SIC BRANCH | YES "(NO IC)" / NO |
| s | hex | BR CONDITION MET | NO / YES |
| t | oval (terminal) | ABC WILL CAUSE HSCLN MODE | |
| u | hex | LAOP 17 EXT STO | YES / (unlabelled right exit) |
| v | hex | LAOP 23 EXT STO | YES / (unlabelled) |
| w | hex | NOOP 13 NOT INT STO (printed "NOOP", not "LAOP"; confirmed at 600 dpi) | YES / (unlabelled) |
| x | hex | LAOP 21 | YES "ALWAYS EXT STO" / (unlabelled) |
| y | hex | LAOP 04 | YES / (unlabelled) |
| z | hex | LAOP 33 INT | YES / (unlabelled) |
| aa | hex | ABC ACTION TAKEN (upper) | YES "A TIMER M" |
| bb | hex | LAOP 11 OR 63 | YES |
| cc | hex | BAC REC REQ (printed "BAC"; DERIVED possibly "BR" / branch-recovery; not resolved) | NO |
| dd | hex | ABC ACTION TAKEN (lower) | YES "TFR IND E+M" |
| ee | hex | TBC OCC INT CK | NO -> ADVANCE TBC |

##### 2. Structure (DERIVED)
ADVANCE TBC -> RESET TBC LDE, SET TBC AES, STEP TBC TO NEXT LEVEL -> DISC?
All "go" exits land on a left-hand vertical bus that ends in TBC OCC INT CK? NO -> ADVANCE TBC.
- DISC YES -> bus. DISC NO -> HSCLN MODE? and -> LF & LC ON? (YES -> SET TBC LDE).
- HSCLN MODE YES -> bus; NO -> NOOP MODE?
- NOOP MODE YES -> LAST LEVEL? NO (IC OFF) -> bus; YES -> EXT STORE? NO -> ABC ACTION COMPLETE OK YES (AND CKT 3C) -> bus; YES -> ALL PREVIOUS STORES YES (STAR BUSY AND NO STORE REQ / AND CKT 3A) -> bus.
- NOOP MODE NO -> INST DECODED YES (LDE ON) -> LAOP 45 OR 47?
  - YES -> BRANCH RECOVERY IN PROG NO -> LAOP 47? YES -> bus; NO -> SIC BRANCH? YES (NO IC) -> bus; NO -> BR CONDITION MET? NO -> bus; YES -> ABC WILL CAUSE HSCLN MODE (terminal).
  - NO -> LAOP 17 EXT STO? YES -> bus; else LAOP 23 EXT STO? YES -> bus; else NOOP 13 NOT INT STO? YES -> bus; else LAOP 21 YES (ALWAYS EXT STO) -> bus; else LAOP 04 YES -> bus; else LAOP 33 INT? YES -> ABC ACTION TAKEN YES (A TIMER M) -> bus; else LAOP 11 OR 63? YES -> BAC REC REQ NO -> ABC ACTION TAKEN YES (TFR IND E+M) -> bus.

##### 3. Step table
| step | condition (PRINTED) | action (PRINTED) | notes |
|---|---|---|---|
| advance | — | RESET TBC LDE; SET TBC AES; STEP TBC TO NEXT LEVEL | |
| LDE | DISC NO & LF & LC ON | SET TBC LDE | |
| bypass | DISC / HSCLN MODE | to TBC OCC INT CK | [KEY] houseclean |
| noop | NOOP MODE & LAST LEVEL NO (IC OFF) | to bus | |
| noop store | NOOP MODE, LAST LEVEL, EXT STORE NO, ABC ACTION COMPLETE OK (AND CKT 3C) | to bus | |
| noop store | NOOP MODE, LAST LEVEL, EXT STORE YES, ALL PREVIOUS STORES (STAR BUSY AND NO STORE REQ; AND CKT 3A) | to bus | [KEY] |
| branch | LAOP 45 OR 47 & not BRANCH RECOVERY IN PROG & (LAOP 47, or SIC BRANCH (NO IC), or BR CONDITION MET NO) | to bus | [KEY] |
| branch taken | BR CONDITION MET YES | ABC WILL CAUSE HSCLN MODE | [KEY] wrong-way recovery via houseclean |
| store ops | LAOP 17 EXT STO / 23 EXT STO / NOOP 13 NOT INT STO / LAOP 21 ALWAYS EXT STO / LAOP 04 | to bus | |
| int | LAOP 33 INT & ABC ACTION TAKEN (A TIMER M) | to bus | |
| | LAOP 11 OR 63 & BAC REC REQ NO & ABC ACTION TAKEN (TFR IND E+M) | to bus | |
| advance | TBC OCC INT CK NO | ADVANCE TBC | interlock |

##### 4. Named items
- Counters: TBC, ABC, OCC. Triggers: TBC LDE, TBC AES. Modes: HSCLN MODE, NOOP MODE. Tags: LF, LC, IC. "STAR" (DERIVED: store address register) BUSY.
- Timers: "A TIMER M", "TFR IND E+M" (transfer-indicator timer phase).
- Circuits: "AND CKT 3C", "AND CKT 3A".
- LAOP codes: 45, 47, 17 (EXT STO), 23 (EXT STO), 13 (printed "NOOP 13 NOT INT STO"), 21 (ALWAYS EXT STO), 04, 33 (INT), 11, 63.

##### 5. TIME
PRINTS NO TIME (only trigger-phase names "A TIMER M", "TFR IND E+M").

##### 6. [KEY] verbatim
- [KEY] "HSCLN MODE" (bypass), "ABC WILL CAUSE HSCLN MODE" (after "BR CONDITION MET" YES).
- [KEY] "BRANCH RECOVERY IN PROG", "SIC BRANCH (NO IC)".
- [KEY] "ALL PREVIOUS STORES" / "STAR BUSY AND NO STORE REQ" / "AND CKT 3A".
- [KEY] "LAOP 21 ... ALWAYS EXT STO"; "NOOP 13 NOT INT STO"; "LAOP 33 INT".

##### 7. Interlocks
- TBC vs OCC: "TBC OCC INT CK" NO -> ADVANCE TBC.
- TBC vs ABC: "ABC ACTION COMPLETE OK", "ABC ACTION TAKEN" (x2).

##### 8. Could not read
Nothing illegible. Uncertain meanings (DERIVED only): "BAC REC REQ", "STAR", "NOOP 13" (likely LAOP 13 misprinted as NOOP, or a no-op'd level with LAOP 13 — kept verbatim).

#### Fig 3.2.6 — "TBC MULTIPLE ADVANCE CONDITION"

- PDF page 98 (portrait). Header "LA FLOW DIAGRAMS" / "M3-04-3".
- Printed page at foot: **2-8**; issue date: **2/1/62**. No serial-number note.
- Read at 450 dpi (h98_*.png) and 600-dpi crops of the LAOP labels. Bottom-left boxes faded. **No ALD page references printed.**

##### 1. Boxes (PRINTED)
| box | shape | text | exits |
|---|---|---|---|
| a | entry | ADVANCE TBC | |
| b | rect | RESET TBC LDE | |
| c | rect | SET TBC AES | |
| d | rect | STEP TBC TO NEXT LEVEL | |
| e | hex | LDE ON | YES (NO not drawn) |
| f | hex | LAOP 20 OR 24 | YES / "NOT INT" |
| g | rect | T BUS TIMER (#1, f YES) | out-lines: "I/O RESPONSE" (to bus; "I/O" faded, reads "I C") and one to h |
| h | rect | RESET TBC AES | |
| i | hex | LAOP 03, 07'15 (printed with an apostrophe; DERIVED 03, 07, 15) | YES / "NOT INT" |
| j | rect | T BUS TIMER (#2, i YES) | out-lines "M" (to bus) and one to k |
| k | rect | RESET TBC AES | |
| l | hex | LAOP 05 | YES / "NOT INT" |
| m | rect | T BUS TIMER (#3, l YES) | "M" (to bus) and one to n |
| n | rect | RESET TBC AES | |
| o | hex | LAOP X1, 35, 75, 43 | YES / (unlabelled) |
| p | hex | LAOP X2 NOT INT | YES / (unlabelled) |
| q | rect | T BUS TIMER (#4, o YES or p YES) | out-lines "FP 1ST CYC", "VFL 1ST CYC", and one to r |
| r | rect | RESET TBC AES | |
| s | rect | SET FST CYC MEM | out-line "IF NOT INT STO" to bus |
| t | hex | LAOP 55, 27 | YES |
| u | rect | T BUS TIMER (#5, t YES) | -> r |
| v | hex | BR SUCCESSOR BR UNSUCC | YES |
| w | hex | TBC ABC INTLK | YES |
| x | oval (terminal) | ABC WILL RESET AES | |
| y | hex | INT FETCH | YES / NO |
| z | hex | LOOP 51 (printed "LOOP", confirmed at 600 dpi; DERIVED LAOP 51) | NO |
| aa | hex | LAOP 41, 23, 17 | YES / (unlabelled) |
| bb | hex | LAOP 00, 40, 02, 42, 25, 65, (trailing comma printed; "02" first digit 0 not D) | YES / (unlabelled) |
| cc | hex | LAOP 31, 57, 33, EXT | YES |
| dd | hex | TBC AES OFF | YES (faded) |
| ee | hex | TBC OCC INTLK (faded: "TBC OCC INTLK") | NO -> ADVANCE TBC (faded) |

##### 2. Structure (DERIVED)
ADVANCE TBC -> RESET TBC LDE, SET TBC AES, STEP TBC TO NEXT LEVEL -> LDE ON?
LDE ON YES -> (1) the LAOP decode chain f -> i -> l -> o -> p -> t (each NOT INT / unlabelled exit to the next) and (2) a long line to TBC ABC INTLK?
All "go" exits land on a left vertical bus ending in TBC AES OFF? YES -> TBC OCC INTLK? NO -> ADVANCE TBC.
- LAOP 20 OR 24 YES -> T BUS TIMER -> RESET TBC AES; "I/O RESPONSE" -> bus.
- LAOP 03, 07, 15 YES -> T BUS TIMER -> RESET TBC AES; M -> bus.
- LAOP 05 YES -> T BUS TIMER -> RESET TBC AES; M -> bus.
- LAOP X1, 35, 75, 43 YES, or LAOP X2 NOT INT YES -> T BUS TIMER -> RESET TBC AES; FP 1ST CYC -> bus ("IF NOT INT STO") and -> SET FST CYC MEM; VFL 1ST CYC -> bus and -> SET FST CYC MEM; SET FST CYC MEM -> "IF NOT INT STO" -> bus.
- LAOP 55, 27 YES -> T BUS TIMER -> RESET TBC AES, and -> BR SUCCESSOR BR UNSUCC? YES -> bus.
- TBC ABC INTLK YES -> ABC WILL RESET AES (terminal) and -> INT FETCH?: YES -> LOOP 51? NO -> bus; NO -> LAOP 41,23,17? YES -> bus; else LAOP 00,40,02,42,25,65? YES -> bus; else LAOP 31,57,33, EXT? YES -> bus.

##### 3. Step table
| step | condition (PRINTED) | action (PRINTED) | notes |
|---|---|---|---|
| advance | — | RESET TBC LDE; SET TBC AES; STEP TBC TO NEXT LEVEL | |
| I/O | LDE ON, LAOP 20 OR 24 | T BUS TIMER; RESET TBC AES; I/O RESPONSE -> bus | |
| VFL operand | LAOP 03, 07'15 (NOT INT chain) | T BUS TIMER; RESET TBC AES; M -> bus | |
| VFL | LAOP 05 | T BUS TIMER; RESET TBC AES; M -> bus | |
| SAU/PAU first | LAOP X1, 35, 75, 43 or LAOP X2 NOT INT | T BUS TIMER; RESET TBC AES; FP 1ST CYC / VFL 1ST CYC; SET FST CYC MEM; IF NOT INT STO -> bus | |
| branch | LAOP 55, 27 | T BUS TIMER; RESET TBC AES; BR SUCCESSOR BR UNSUCC -> bus | [KEY] |
| ABC wait | TBC ABC INTLK YES | ABC WILL RESET AES | [KEY] |
| | INT FETCH YES & LOOP 51 NO | -> bus | |
| | INT FETCH NO & (LAOP 41,23,17 / 00,40,02,42,25,65 / 31,57,33, EXT) | -> bus | |
| advance | TBC AES OFF YES & TBC OCC INTLK NO | ADVANCE TBC | interlock |

##### 4. Named items
- Counters TBC, ABC, OCC. Triggers TBC LDE, TBC AES, FST CYC MEM. Timer: T BUS TIMER (five instances), phase "M".
- Lines/labels: I/O RESPONSE, FP 1ST CYC, VFL 1ST CYC, IF NOT INT STO, NOT INT, INT FETCH.
- LAOP codes: 20, 24, 03, 07, 15, 05, X1, 35, 75, 43, X2, 55, 27, 51 (as "LOOP 51"), 41, 23, 17, 00, 40, 02, 42, 25, 65, 31, 57, 33.

##### 5. TIME
PRINTS NO TIME (phase label "M" on timer out-lines; "1ST CYC" names only).

##### 6. [KEY] verbatim
- [KEY] "TBC ABC INTLK" -> "ABC WILL RESET AES".
- [KEY] "BR SUCCESSOR BR UNSUCC".
- [KEY] "IF NOT INT STO" (twice).

##### 7. Interlocks
- TBC vs ABC: "TBC ABC INTLK".
- TBC vs OCC: "TBC OCC INTLK" NO -> ADVANCE TBC.
- TBC self: "TBC AES OFF".

##### 8. Could not read
- "I/O RESPONSE": "I/O" faded (reads "I C"); RESPONSE clear.
- Bottom TBC AES OFF / TBC OCC INTLK / ADVANCE TBC: faded but readable at 450 dpi.
- Unlabelled exits on o, p, aa, bb (right side): drawn without YES/NO.

#### Fig 3.2.7 — "TBC I/O INSTRUCTIONS - OP 20 AND OP 24"

- PDF page 99 (portrait). Header "M3-04-3" / "LA FLOW DIAGRAMS".
- Printed page at foot: **2-9**; issue date: **2/1/62**. No serial-number note.
- Read at 300 dpi (t99_*.png) and 600 dpi (timer labels). Clean scan.

##### 1. Boxes (PRINTED)
| box | shape | text | ALD / exits |
|---|---|---|---|
| a | entry | ADVANCE | |
| b | rect | SET TBC AES | 38.21.03.1 |
| c | rect | TBC AT NEW LEVEL | |
| d | hex | IS LEVEL READY FOR TBC ACTION ? | YES "TBC LDE ON" |
| e | hex | NOOP'D OR NOOP MODE ? | NO |
| f | hex | IO INSTR ? | YES "OP X00"; ref 38.22.03.1 on the input arrow |
| g | hex | ABC-SCC INTLKD ? | YES |
| h | hex | TBC-ABC INTLKD ? | YES |
| i | hex | PREVIOUS INSTR. PROPERLY EXECUTED ? | YES "MAR MODE" |
| j | hex | TBC ACTION TAKEN YET ? | NO "TBC AES ON" |
| k | timer bar | START TRANSFER BUS TIMER | 38.25.01.1; phase lines "E. M" (no overbar at 600 dpi), "M", "E or M" |
| l | rect (E. M) | RESET TBC AES | 38.21.03.1 |
| m | hex (M) | BX OR DISC SYNC INSTR. ? | "BX / OP 20" / "DISC / OP 24" |
| n | rect | SELECT BX | 38.68.02.1 |
| o | rect | SELECT DISC SYNC | |
| p | rect (E or M) | GO DATA FIELD LEVELS ON TO B (DERIVED: "ONTO B[us]") | 35.16.01.1 |
| q | rect (g YES) | GO OP CODE BITS 1-4 LEVELS TO IO DECODER | 35.28.01.1 ("35" first digit smeared) |
| r | rect | SIGNAL BX & DISC SYNC TO READ WRITE CONTROL LOCATE RELEASE OR CCW (AND) SEOP | 38.68.01.1 |
| s | hex | HAS BX OR DISC ACCEPTED THE INSTR ? | NO / YES |
| t | hex | REJECTED ? | YES |
| u | rect | SET IO REACTION STORAGE TRIGGER | 38.25.02.1 (on t-YES input), 38.25.03.1 (on s-YES input) |
| v | rect | RESET TB TIMER M | 38.25.02.1 |
| w | rect | DROP SELECT SIGNAL | 38.68.02.1 |
| x | rect | DROP ACCEPT OR REJECT SIGNAL | |
| y | rect | SET IO BUFFER TRIGGER | out-line "RESET" |
| z | rect | SET IO RESPONSE TRIGGER | |
| aa | rect | ADV. TBC IF NOT INTLKD BY OCC | |
| bb | rect | SET TBC AES | |
| cc | rect | RESET TBC LDE | 38.22.15.1 |
| dd | rect | RESET IO RESPONSE TRIGGER | |

##### 2. Structure (DERIVED)
ADVANCE -> SET TBC AES; TBC AT NEW LEVEL -> IS LEVEL READY FOR TBC ACTION? YES (TBC LDE ON) -> NOOP'D OR NOOP MODE? NO -> IO INSTR? YES (OP X00) -> ABC-SCC INTLKD? YES -> (i) GO OP CODE BITS 1-4 LEVELS TO IO DECODER -> SIGNAL BX & DISC SYNC ...; (ii) TBC-ABC INTLKD? YES -> PREVIOUS INSTR. PROPERLY EXECUTED? YES (MAR MODE) -> TBC ACTION TAKEN YET? NO (TBC AES ON) -> START TRANSFER BUS TIMER.
Timer phases: E. M -> RESET TBC AES; M -> BX OR DISC SYNC INSTR? (BX/OP 20 -> SELECT BX; DISC/OP 24 -> SELECT DISC SYNC) -> merge -> HAS BX OR DISC ACCEPTED THE INSTR? (YES -> SET IO REACTION STORAGE TRIGGER; NO -> REJECTED? YES -> SET IO REACTION STORAGE TRIGGER); E or M -> GO DATA FIELD LEVELS ON TO B.
SET IO REACTION STORAGE TRIGGER -> RESET TB TIMER M -> DROP SELECT SIGNAL -> DROP ACCEPT OR REJECT SIGNAL; and -> SET IO BUFFER TRIGGER -> (RESET line loops back up into SET IO REACTION STORAGE TRIGGER and SET IO BUFFER TRIGGER) -> SET IO RESPONSE TRIGGER -> ADV. TBC IF NOT INTLKD BY OCC -> SET TBC AES (-> RESET IO RESPONSE TRIGGER) and RESET TBC LDE.
Sequencer: START TRANSFER BUS TIMER (38.25.01.1). TON: TBC ACTION TAKEN YET NO (TBC AES ON). TOF: "RESET TB TIMER M" after the I/O reaction storage trigger sets.

##### 3. Step table
| step / phase | condition (PRINTED) | action (PRINTED) | ALD | notes |
|---|---|---|---|---|
| advance | — | SET TBC AES; TBC AT NEW LEVEL | 38.21.03.1 | |
| gate | IS LEVEL READY (TBC LDE ON); NOOP'D/NOOP MODE NO; IO INSTR (OP X00) | — | 38.22.03.1 | |
| gate | ABC-SCC INTLKD YES | GO OP CODE BITS 1-4 LEVELS TO IO DECODER; SIGNAL BX & DISC SYNC TO READ/WRITE/CONTROL/LOCATE/RELEASE OR CCW (AND) SEOP | 35.28.01.1; 38.68.01.1 | [KEY] I/O waits for pipe drain (DERIVED) |
| gate | TBC-ABC INTLKD YES; PREVIOUS INSTR. PROPERLY EXECUTED YES (MAR MODE); TBC ACTION TAKEN YET NO (TBC AES ON) | START TRANSFER BUS TIMER | 38.25.01.1 | |
| E. M | — | RESET TBC AES | 38.21.03.1 | |
| M | BX / OP 20; DISC / OP 24 | SELECT BX; SELECT DISC SYNC | 38.68.02.1 | |
| E or M | — | GO DATA FIELD LEVELS ON TO B | 35.16.01.1 | |
| reaction | HAS BX OR DISC ACCEPTED YES, or REJECTED YES | SET IO REACTION STORAGE TRIGGER | 38.25.03.1 / 38.25.02.1 | |
| reaction | — | RESET TB TIMER M; DROP SELECT SIGNAL; DROP ACCEPT OR REJECT SIGNAL | 38.25.02.1; 38.68.02.1 | |
| response | — | SET IO BUFFER TRIGGER (RESET); SET IO RESPONSE TRIGGER | | |
| advance | — | ADV. TBC IF NOT INTLKD BY OCC; SET TBC AES; RESET TBC LDE; RESET IO RESPONSE TRIGGER | 38.22.15.1 | interlock |

##### 4. Named items
- Counters TBC, ABC, SCC, OCC. Triggers TBC AES, TBC LDE, IO REACTION STORAGE, IO BUFFER, IO RESPONSE. Timer: TRANSFER BUS TIMER / TB TIMER M.
- Units: BX (DERIVED: basic exchange), DISC SYNC (disk synchronizer). Bus "B". IO DECODER.
- Op codes (I/O, printed as OP, not LAOP): OP 20 (BX), OP 24 (DISC), OP X00.
- I/O orders: READ, WRITE, CONTROL, LOCATE, RELEASE, CCW, SEOP (printed "SEOP"; second character slightly smeared).
- Mode: MAR MODE.

##### 5. TIME
Phase names only ("E. M", "M", "E or M", "TB TIMER M"). PRINTS NO durations.

##### 6. [KEY] verbatim
- [KEY] "ABC-SCC INTLKD ?" YES and "TBC-ABC INTLKD ?" YES and "PREVIOUS INSTR. PROPERLY EXECUTED ?" YES "MAR MODE" before an I/O instruction is started.

##### 7. Interlocks
- ABC vs SCC: "ABC-SCC INTLKD". TBC vs ABC: "TBC-ABC INTLKD". TBC vs OCC: "ADV. TBC IF NOT INTLKD BY OCC".

##### 8. Could not read
Nothing illegible. "35.28.01.1" first two digits smeared (reads "35"). "SEOP" read verbatim.

#### Fig 3.2.8 — "FIRST LEVEL OF SAU INSTRUCTIONS"

- PDF page 100 (portrait). Header "LA FLOW DIAGRAMS" / "M3-04-3".
- Printed page at foot: **2-10**; issue date: **2/1/62**. No serial-number note.
- Read at 300 dpi (t100_*.png) and 600 dpi ("LAOP ?" box).

##### 1. Boxes (PRINTED)
| box | shape | text | ALD / exits |
|---|---|---|---|
| a | entry | ADVANCE | |
| b | rect | SET TBC AES | 38.21.03.1 |
| c | rect | TBC AT NEW LEVEL | |
| d | hex | IS LEVEL READY FOR TBC ACTION ? | YES "TBC LDE ON" |
| e | hex | NOOP'D OR NOOP MODE ? | NO |
| f | hex | 35, 75 43, X1 ? | YES |
| g | box (legend) | OP DECODE: "OP X1 38.22.07.1 / LAOP 35 OR 75 38.22.10.1 / LAOP 75 38.22.09.1 / LAOP 43 38.22.09.1" | |
| h | hex | LAOP ? (no code printed; confirmed blank at 600 dpi) | YES |
| i | hex | BB OR BI ? | "BI" / "BB" |
| j | hex | INTRPT BI ? | two unlabelled exits (left, right) |
| k | rect | SIGNAL SAU OF INTRPT BI INSTR | 38.23.05.1 |
| l | rect | SIGNAL SAU OF BI INSTR. | 36.11.02.1 |
| m | rect | SIGNAL SAU OF BB INSTR. | |
| n | hex | TBC ACTION TAKEN YET? | NO "TBC AES ON" |
| o | timer bar | START TRANSFER BUS TIMER | 38.25.01.1; phase lines "E.M̄" (overbar on M) and "E + M" |
| p | rect (E.M̄) | RESET TBC AES | 38.21.03.1 |
| q | rect (E.M̄) | SET VFL START TRIGGER | 38.23.05.1 |
| r | rect (E + M) | GO DATA FIELD ON TOB | |
| s | rect (E + M) | GO OP CODE & WBC TO SAU | |
| t | rect | ENABLE SAU TO START PRE-EXECUTION | |
| u | hex | HAS SAU ACCEPTED THE DATA ? | YES ""SAU HSKPING"" |
| v | rect | RESET VFL START TRIGGER | 38.23.05.1 |
| w | rect | SET FIRST CYCLE MEM. TRIGGER | 38.24.01.1 |
| x | rect | ADV TBC IF NOT INTLKD BY OCC | |
| y | rect | SET TBC AES | |
| z | rect | RESET TB TIMER M | |
| aa | rect | RESET TBC LDE | 38.22.15.1 |
| bb | rect | RESET "FIRST CYCLE MEM" TRIG | 38.24.01.1 |

##### 2. Structure (DERIVED)
ADVANCE -> SET TBC AES; TBC AT NEW LEVEL -> IS LEVEL READY? YES (TBC LDE ON) -> NOOP'D OR NOOP MODE? NO -> 35, 75 43, X1? YES -> (i) LAOP ? YES -> BB OR BI? (BI -> INTRPT BI? -> SIGNAL SAU OF INTRPT BI INSTR / SIGNAL SAU OF BI INSTR.; BB -> SIGNAL SAU OF BB INSTR.); (ii) TBC ACTION TAKEN YET? NO (TBC AES ON) -> START TRANSFER BUS TIMER.
Timer: E.M̄ -> RESET TBC AES and SET VFL START TRIGGER -> ENABLE SAU TO START PRE-EXECUTION -> HAS SAU ACCEPTED THE DATA? YES ("SAU HSKPING") -> RESET VFL START TRIGGER and SET FIRST CYCLE MEM. TRIGGER -> ADV TBC IF NOT INTLKD BY OCC -> SET TBC AES (-> RESET "FIRST CYCLE MEM" TRIG), RESET TB TIMER M, RESET TBC LDE. E + M -> GO DATA FIELD ON TOB, GO OP CODE & WBC TO SAU.
Sequencer: START TRANSFER BUS TIMER (38.25.01.1). TON: TBC ACTION TAKEN YET NO. TOF: RESET TB TIMER M after advance.

##### 3. Step table
| step / phase | condition (PRINTED) | action (PRINTED) | ALD | notes |
|---|---|---|---|---|
| advance | — | SET TBC AES; TBC AT NEW LEVEL | 38.21.03.1 | |
| select | LEVEL READY (TBC LDE ON); not NOOP; 35, 75 43, X1 | — | 38.22.07.1/10.1/09.1 | |
| branch-type | LAOP ? YES, BB OR BI, INTRPT BI | SIGNAL SAU OF INTRPT BI INSTR / OF BI INSTR. / OF BB INSTR. | 38.23.05.1; 36.11.02.1 | DERIVED: BB/BI = branch-on-bit / branch-on-indicator |
| start | TBC ACTION TAKEN YET NO (TBC AES ON) | START TRANSFER BUS TIMER | 38.25.01.1 | |
| E.M̄ | — | RESET TBC AES; SET VFL START TRIGGER; ENABLE SAU TO START PRE-EXECUTION | 38.21.03.1; 38.23.05.1 | |
| E + M | — | GO DATA FIELD ON TOB; GO OP CODE & WBC TO SAU | | |
| handshake | HAS SAU ACCEPTED THE DATA YES ("SAU HSKPING") | RESET VFL START TRIGGER; SET FIRST CYCLE MEM. TRIGGER | 38.23.05.1; 38.24.01.1 | |
| advance | — | ADV TBC IF NOT INTLKD BY OCC; SET TBC AES; RESET TB TIMER M; RESET TBC LDE; RESET "FIRST CYCLE MEM" TRIG | 38.22.15.1; 38.24.01.1 | interlock |

##### 4. Named items
- Counters TBC, OCC. Triggers TBC AES, TBC LDE, VFL START, FIRST CYCLE MEM. Timer TRANSFER BUS TIMER / TB TIMER M.
- Units/regs: SAU, TOB, WBC (DERIVED: word boundary crossover). Handshake "SAU HSKPING".
- Codes: OP X1; LAOP 35, 75, 43; BB, BI, INTRPT BI.

##### 5. TIME
Phase names only (E.M̄, E + M, TB TIMER M). PRINTS NO durations.

##### 6. [KEY] verbatim
None of the listed [KEY] topics appear (no store/LAAR/houseclean/recovery text).

##### 7. Interlocks
TBC vs OCC: "ADV TBC IF NOT INTLKD BY OCC". (No ABC/SCC interlock test on this sheet.)

##### 8. Could not read
Nothing illegible. "LAOP ?" carries no code (blank, not faded). INTRPT BI exits carry no YES/NO labels (DERIVED: left = yes -> INTRPT BI, right = no -> BI).

#### Fig 3.2.9 — "VFL OPERANDS LAOP 03, 05, AND 07"

- PDF page 101 (portrait). Header "M3-04-3" / "LA FLOW DIAGRAMS".
- Printed page at foot: **2-11**; issue date: **2/1/62**. No serial-number note.
- Read at 300 dpi (t101_*.png).

##### 1. Boxes (PRINTED)
| box | shape | text | ALD / exits |
|---|---|---|---|
| a | entry | ADVANCE | |
| b | rect | SET TBC AES | 38.21.03.1 |
| c | rect | TBC AT NEW LEVEL | |
| d | hex | IS LEVEL READY FOR TBC ACTION ? | YES "TBC LDE ON" |
| e | hex | NOOP'D OR NOOP MODE ? | NO |
| f | box (legend) | OP DECODE: "LAOP 05 38.22.07.1 / LAOP 03 38.22.11.1 / LAOP 07 38.22.11.1" | |
| g | hex | IS OPERAND IN LA DATA FIELD ? | YES "INT TAG OFF" |
| h | hex | FIRST OR ONLY OPERAND | NO "07" / YES "03 05" |
| i | hex | TBC- ABC INTLKD ? | YES |
| j | hex | PREVIOUS INSTR. PROPERLY EXECUTED ? | YES "MAR MODE" |
| k | hex | TBC ACTION TAKEN YET? | NO "TBC AES ON" |
| l | timer bar | START TRANSFER BUS TIMER | 38.25.01.1; phase lines "E. M̄", "M", "E + M" |
| m | rect (E.M̄) | RESET TBC AES | 38.21.03.1 |
| n | hex (E.M̄) | FIRST OR ONLY OPERAND ? | YES "03 05" / NO |
| o | rect | GI TOB TO C REG | 35.17.01.1 |
| p | rect | GI TOB TO D REG | |
| q | hex (E.M̄) | LAST, OR ONLY. OPERAND ? | YES "05 07" |
| r | rect | SET SAU GO TRIGGER | 38.23.04.1 |
| s | rect | SIGNAL SAU TO STOP HSKPING & START EXECUTION | |
| t | hex | HAS SAU STARTED EXECUTION ? | YES ""SAU HSKPING" OVER" |
| u | rect | RESET SAU GO TRIGGER | 38.23.04.1 |
| v | rect (E + M) | GO DATA ON TOB | |
| w | rect (M) | ADV TBC IF NOT INTLKD BY OCC | |
| x | rect | RESET TBC LDE | |
| y | rect | SET TBC AES | |
| z | rect | RESET TB TIMER M | |

##### 2. Structure (DERIVED)
ADVANCE -> SET TBC AES; TBC AT NEW LEVEL -> IS LEVEL READY? YES (TBC LDE ON) -> NOOP'D? NO -> IS OPERAND IN LA DATA FIELD? YES (INT TAG OFF) -> FIRST OR ONLY OPERAND?
- NO (07) -> straight to TBC ACTION TAKEN YET?
- YES (03, 05) -> TBC-ABC INTLKD? YES -> PREVIOUS INSTR. PROPERLY EXECUTED? YES (MAR MODE) -> TBC ACTION TAKEN YET?
TBC ACTION TAKEN YET NO (TBC AES ON) -> START TRANSFER BUS TIMER.
- E. M̄ -> RESET TBC AES; FIRST OR ONLY OPERAND? (YES 03/05 -> GI TOB TO C REG; NO -> GI TOB TO D REG); LAST, OR ONLY. OPERAND? YES (05/07) -> SET SAU GO TRIGGER -> SIGNAL SAU TO STOP HSKPING & START EXECUTION -> HAS SAU STARTED EXECUTION? YES ("SAU HSKPING" OVER) -> RESET SAU GO TRIGGER.
- M -> ADV TBC IF NOT INTLKD BY OCC -> RESET TBC LDE, SET TBC AES, RESET TB TIMER M.
- E + M -> GO DATA ON TOB.
DERIVED from the YES labels: LAOP 03 = first operand of two; LAOP 05 = only operand (first AND last); LAOP 07 = second/last operand.

##### 3. Step table
| step / phase | condition (PRINTED) | action (PRINTED) | ALD | notes |
|---|---|---|---|---|
| advance | — | SET TBC AES; TBC AT NEW LEVEL | 38.21.03.1 | |
| gate | LEVEL READY (TBC LDE ON); NOOP'D NO; OPERAND IN LA DATA FIELD (INT TAG OFF) | — | | |
| gate (03, 05) | TBC-ABC INTLKD YES; PREVIOUS INSTR. PROPERLY EXECUTED YES (MAR MODE) | — | | first VFL operand waits for ABC |
| start | TBC ACTION TAKEN YET NO (TBC AES ON) | START TRANSFER BUS TIMER | 38.25.01.1 | |
| E.M̄ | — | RESET TBC AES | 38.21.03.1 | |
| E.M̄ | FIRST OR ONLY (03, 05) / NO | GI TOB TO C REG / GI TOB TO D REG | 35.17.01.1 | |
| E.M̄ | LAST, OR ONLY (05, 07) | SET SAU GO TRIGGER; SIGNAL SAU TO STOP HSKPING & START EXECUTION | 38.23.04.1 | |
| | HAS SAU STARTED EXECUTION YES ("SAU HSKPING" OVER) | RESET SAU GO TRIGGER | 38.23.04.1 | |
| M | — | ADV TBC IF NOT INTLKD BY OCC; RESET TBC LDE; SET TBC AES; RESET TB TIMER M | | interlock |
| E + M | — | GO DATA ON TOB | | |

##### 4. Named items
Counters TBC, ABC, OCC. Triggers TBC AES, TBC LDE, SAU GO. Timer TRANSFER BUS TIMER / TB TIMER M. Regs/buses: TOB, C REG, D REG, LA DATA FIELD. Tag: INT TAG. Mode: MAR MODE. LAOP 03, 05, 07.

##### 5. TIME
Phase names only (E. M̄, M, E + M). PRINTS NO durations.

##### 6. [KEY] verbatim
- [KEY] "IS OPERAND IN LA DATA FIELD ?" YES "INT TAG OFF" (operand present in the level vs internal register).

##### 7. Interlocks
TBC vs ABC: "TBC- ABC INTLKD ?" (first/only operand only). TBC vs OCC: "ADV TBC IF NOT INTLKD BY OCC".

##### 8. Could not read
Nothing illegible. Missing exits not drawn: IS OPERAND IN LA DATA FIELD NO, TBC-ABC INTLKD NO, LAST OR ONLY NO, etc.

#### Fig 3.2.10 — "VFL SPECIAL OPERAND LAOP 15"

- PDF page 102 (portrait). Header "LA FLOW DIAGRAMS" / "M3-04-3".
- Printed page at foot: **2-12**; issue date: **2/1/62**. No serial-number note.
- Read at 300 dpi (t102_*.png).

##### 1. Boxes (PRINTED)
| box | shape | text | ALD / exits |
|---|---|---|---|
| a | entry | ADVANCE | |
| b | rect | SET TBC AES | 38.21.03.1 |
| c | rect | TBC AT NEW LEVEL | |
| d | hex | IS LEVEL READY FOR TBC ACTION ? | YES "TBC LDE ON" |
| e | hex | NOOP'D OR NOOP MODE ? | NO |
| f | hex | LAOP 15 | YES; ref 38.22.11.1 printed beside it |
| g | hex | IS OPERAND IN LA DATA FIELD ? | exit labelled "ALWAYS" above and "INT TAG OFF" below |
| h | hex | IS C REG EMPTY ? | YES "VFL RDY FOR MCND" |
| i | rect | SET VFL WAIT FOR MULTIPLICAND TRIG. | 38.24.03.1 |
| j | rect | SEND A SIGNAL TO SAU TO BLOCK ITS MPYC ACTION | 38.23.05.1 |
| k | hex | TBC ACTION TAKEN YET ? | NO "TBC AES ON" |
| l | timer bar | START TRANSFER BUS TIMER | 38.25.01.1; phase lines "E. M̄", "E + M", "M" |
| m | rect (E.M̄) | RESET TBC AES | 38.21.03.1 |
| n | rect (E.M̄) | GI TOB TO C REG | 35.17.01.1 |
| o | rect (E.M̄) | GI RESIDUE FROM TOB TO A CHKR | 38.23.03.1 |
| p | rect (E.M̄) | RESET "VFL WAIT FOR MCND" TRIGGER | 38.24.03.1 |
| q | rect | REMOVE SAU MPYC BLOCK | |
| r | rect (E + M) | GO DATA ON TOB | 35.16.01.1 |
| s | rect (M) | ADV. TBC IF NOT INTLKD BY OCC | |
| t | rect | RESET TBC LDE | |
| u | rect | SET TBC AES | |
| v | rect | RESET TB TIMER M | |

##### 2. Structure (DERIVED)
ADVANCE -> SET TBC AES; TBC AT NEW LEVEL -> IS LEVEL READY? YES (TBC LDE ON) -> NOOP'D? NO -> LAOP 15? YES -> IS OPERAND IN LA DATA FIELD? (ALWAYS / INT TAG OFF) -> IS C REG EMPTY? YES (VFL RDY FOR MCND) -> SET VFL WAIT FOR MULTIPLICAND TRIG. -> SEND A SIGNAL TO SAU TO BLOCK ITS MPYC ACTION, and -> TBC ACTION TAKEN YET? NO (TBC AES ON) -> START TRANSFER BUS TIMER.
E.M̄ -> RESET TBC AES; GI TOB TO C REG; GI RESIDUE FROM TOB TO A CHKR; RESET "VFL WAIT FOR MCND" TRIGGER -> REMOVE SAU MPYC BLOCK. E + M -> GO DATA ON TOB. M -> ADV. TBC IF NOT INTLKD BY OCC -> RESET TBC LDE, SET TBC AES, RESET TB TIMER M.
DERIVED: LAOP 15 carries the VFL multiplicand ("MCND") into the C register while the SAU's multiply ("MPYC") action is blocked.

##### 3. Step table
| step / phase | condition (PRINTED) | action (PRINTED) | ALD | notes |
|---|---|---|---|---|
| advance | — | SET TBC AES; TBC AT NEW LEVEL | 38.21.03.1 | |
| gate | LEVEL READY; NOOP'D NO; LAOP 15; OPERAND IN LA DATA FIELD (ALWAYS / INT TAG OFF); IS C REG EMPTY YES (VFL RDY FOR MCND) | SET VFL WAIT FOR MULTIPLICAND TRIG.; SEND A SIGNAL TO SAU TO BLOCK ITS MPYC ACTION | 38.22.11.1; 38.24.03.1; 38.23.05.1 | |
| start | TBC ACTION TAKEN YET NO (TBC AES ON) | START TRANSFER BUS TIMER | 38.25.01.1 | |
| E.M̄ | — | RESET TBC AES; GI TOB TO C REG; GI RESIDUE FROM TOB TO A CHKR; RESET "VFL WAIT FOR MCND" TRIGGER; REMOVE SAU MPYC BLOCK | 38.21.03.1; 35.17.01.1; 38.23.03.1; 38.24.03.1 | |
| E + M | — | GO DATA ON TOB | 35.16.01.1 | |
| M | — | ADV. TBC IF NOT INTLKD BY OCC; RESET TBC LDE; SET TBC AES; RESET TB TIMER M | | interlock |

##### 4. Named items
Counters TBC, OCC. Triggers TBC AES, TBC LDE, VFL WAIT FOR MULTIPLICAND (VFL WAIT FOR MCND). Timer TRANSFER BUS TIMER / TB TIMER M. Regs: C REG, TOB, A CHKR, LA DATA FIELD. Tag INT TAG. LAOP 15.

##### 5. TIME
Phase names only. PRINTS NO durations.

##### 6. [KEY] verbatim
None of the listed [KEY] topics; "IS OPERAND IN LA DATA FIELD ? ALWAYS / INT TAG OFF" noted.

##### 7. Interlocks
TBC vs OCC: "ADV. TBC IF NOT INTLKD BY OCC". No ABC interlock test on this sheet.

##### 8. Could not read
Nothing illegible.

#### Fig 3.2.11 — "FP INSTRUCTION LEVEL OPX2"

- PDF page 103 (portrait). Header "M3-04-3" / "LA FLOW DIAGRAMS".
- Printed page at foot: **2-13**; issue date: **2/1/62**. No serial-number note.
- Read at 300 dpi (t103_*.png).

##### 1. Boxes (PRINTED)
| box | shape | text | ALD / exits |
|---|---|---|---|
| a | entry | ADVANCE | |
| b | rect | SET TBC AES | (no ref) |
| c | rect | TBC AT NEW LEVEL | |
| d | hex | INST PREPARATION COMP | YES "LF & LC ON" |
| e | hex | DISC OR NOOPED | NO |
| f | hex | HSCLN OR NOOP MODE | NO |
| g | hex | OP X2 | YES |
| h | hex | IS OPERAND IN INT REG | NO "INT TAG OFF" |
| i | hex | LATE DECODE ENABLE ON | YES |
| j | rect | GO OP CODE ON TOB | 35.28.01.1 |
| k | hex | TBC ACTION TAKEN | NO "TBC AES ON" |
| l | timer bar | STAPT T BUS TIMER (misprint for START) | 38.25.01.1; phase lines "EM̄" and "E + M" |
| m | rect (EM̄) | RESET TBC AES | 38.21.03.1 |
| n | rect (EM̄) | GI TOB TO C REG | 38.23.01.1 |
| o | rect (EM̄) | SIGNAL PAU & SAU TO START | 38.23.01.1 |
| p | rect (E + M) | GO DATA FIELD ON TOB | 35.16.01.1 |
| q | hex | HAS PAU STARTED YET | "YES TO" |
| r | rect | SET 1ST CYC MEM TGR | 38.24.01.1 |
| s | hex | INT STORE | NO |
| t | rect | ADVANCE IF NOT INTERLOCKED BY OCC | 38.21.04.1 |
| u | rect | RESET TBC ADE 1ST CYC MEM T BUS M ("ADE" printed; DERIVED: LDE) | |
| v | exit | ADVANCE | |

##### 2. Structure (DERIVED)
ADVANCE -> SET TBC AES; TBC AT NEW LEVEL -> INST PREPARATION COMP? YES (LF & LC ON) -> DISC OR NOOPED? NO -> HSCLN OR NOOP MODE? NO -> OP X2? YES -> (i) IS OPERAND IN INT REG? NO (INT TAG OFF) -> TBC ACTION TAKEN? NO (TBC AES ON) -> STAPT T BUS TIMER; (ii) LATE DECODE ENABLE ON? YES -> GO OP CODE ON TOB.
Timer: EM̄ -> RESET TBC AES; GI TOB TO C REG; SIGNAL PAU & SAU TO START -> HAS PAU STARTED YET? YES -> SET 1ST CYC MEM TGR and (bypass) -> INT STORE? NO -> ADVANCE IF NOT INTERLOCKED BY OCC -> RESET TBC ADE / 1ST CYC MEM / T BUS M; -> ADVANCE. E + M -> GO DATA FIELD ON TOB.

##### 3. Step table
| step / phase | condition (PRINTED) | action (PRINTED) | ALD | notes |
|---|---|---|---|---|
| advance | — | SET TBC AES; TBC AT NEW LEVEL | | |
| gate | INST PREPARATION COMP YES (LF & LC ON); DISC OR NOOPED NO; HSCLN OR NOOP MODE NO; OP X2 YES | — | | [KEY] HSCLN |
| decode | LATE DECODE ENABLE ON YES | GO OP CODE ON TOB | 35.28.01.1 | |
| start | IS OPERAND IN INT REG NO (INT TAG OFF); TBC ACTION TAKEN NO (TBC AES ON) | STAPT T BUS TIMER | 38.25.01.1 | |
| EM̄ | — | RESET TBC AES; GI TOB TO C REG; SIGNAL PAU & SAU TO START | 38.21.03.1; 38.23.01.1; 38.23.01.1 | |
| E + M | — | GO DATA FIELD ON TOB | 35.16.01.1 | |
| start ack | HAS PAU STARTED YET YES | SET 1ST CYC MEM TGR | 38.24.01.1 | |
| advance | INT STORE NO | ADVANCE IF NOT INTERLOCKED BY OCC; RESET TBC ADE, 1ST CYC MEM, T BUS M | 38.21.04.1 | interlock |

##### 4. Named items
Counters TBC, OCC. Triggers TBC AES, TBC "ADE" (LDE), 1ST CYC MEM TGR, LATE DECODE ENABLE. Timer T BUS TIMER / T BUS M. Units PAU, SAU. Regs TOB, C REG, INT REG. Tags LF, LC, INT TAG. Modes HSCLN, NOOP. Code: OP X2.

##### 5. TIME
Phase names only (EM̄, E + M, T BUS M). PRINTS NO durations.

##### 6. [KEY] verbatim
- [KEY] "HSCLN OR NOOP MODE" (NO path continues).
- [KEY] "INT STORE" NO -> advance (internal-store FP results take a different exit, not drawn).

##### 7. Interlocks
TBC vs OCC: "ADVANCE IF NOT INTERLOCKED BY OCC" (38.21.04.1). No ABC interlock test on this sheet.

##### 8. Could not read
Nothing illegible. Misprints kept verbatim: "STAPT", "TBC ADE". "38.21.03.1" under RESET TBC AES has a smudged first digit.

#### LAOP / OP codes seen on CE manual R23-9732 PDF 92-103 (Figs 3.2.1-3.2.11)

The codes are exactly as printed: the prefix (LAOP / OP / NOOP / LOOP) is kept, and so is the qualifier.
There is one row per code per figure. "meaning as printed" is the box text or the exit/legend text that goes with the code.
DERIVED notes are in brackets.

| LAOP | meaning as printed | figure | PDF |
|---|---|---|---|
| 33 | "LAOP 33 ECC CHK LOAD" (YES -> I CHKR ECC ERR wait loop before SET IAUC LOAD PULSE MEMORY) | 3.2.1 | 92 |
| 45 | "LAOP 45 ?" on LLP 1: NO -> GI OP CODE BIT 8; YES -> I CHKR PARITY ERROR -> SET OP BIT 8 | 3.2.2 s1 | 93 |
| 33 | "LAOP 33 ECC CHK LOAD" on LLP 3: YES -> GI ICOB WITH ECC, ECC ERROR test | 3.2.2 s2 | 94 |
| 33 | "LAOP 33 ECC CORRECT LOAD" (ECC ERROR YES path) [second digit degraded] | 3.2.2 s2 | 94 |
| 45 OR 47 | "LAOP 45 OR 47" -> BRANCH RECOVERY IN PROG test [branch levels] | 3.2.5 | 97 |
| 47 | "LAOP 47" YES -> advance bus (inside the 45/47 branch path) | 3.2.5 | 97 |
| 17 | "LAOP 17 EXT STO" YES -> advance bus | 3.2.5 | 97 |
| 23 | "LAOP 23 EXT STO" YES -> advance bus | 3.2.5 | 97 |
| 13 | "NOOP 13 NOT INT STO" (printed NOOP, not LAOP) YES -> advance bus | 3.2.5 | 97 |
| 21 | "LAOP 21" YES "ALWAYS EXT STO" -> advance bus | 3.2.5 | 97 |
| 04 | "LAOP 04" YES -> advance bus | 3.2.5 | 97 |
| 33 | "LAOP 33 INT" YES -> ABC ACTION TAKEN ("A TIMER M") | 3.2.5 | 97 |
| 11 OR 63 | "LAOP 11 OR 63" YES -> BAC REC REQ NO -> ABC ACTION TAKEN ("TFR IND E+M") | 3.2.5 | 97 |
| 20 OR 24 | "LAOP 20 OR 24" YES -> T BUS TIMER, "I/O RESPONSE" | 3.2.6 | 98 |
| 03, 07, 15 | "LAOP 03, 07'15" (apostrophe printed) YES -> T BUS TIMER, "M" | 3.2.6 | 98 |
| 05 | "LAOP 05" YES -> T BUS TIMER, "M" | 3.2.6 | 98 |
| X1, 35, 75, 43 | "LAOP X1, 35, 75, 43" YES -> T BUS TIMER: "FP 1ST CYC" / "VFL 1ST CYC", SET FST CYC MEM | 3.2.6 | 98 |
| X2 | "LAOP X2 NOT INT" YES -> same T BUS TIMER as X1,35,75,43 | 3.2.6 | 98 |
| 55, 27 | "LAOP 55,27" YES -> T BUS TIMER, BR SUCCESSOR BR UNSUCC | 3.2.6 | 98 |
| 51 | "LOOP 51" (printed LOOP; [LAOP 51]) INT FETCH YES -> LOOP 51 NO -> advance bus | 3.2.6 | 98 |
| 41, 23, 17 | "LAOP 41,23,17" YES -> advance bus (INT FETCH NO path) | 3.2.6 | 98 |
| 00, 40, 02, 42, 25, 65 | "LAOP 00,40,02, 42,25,65," (trailing comma printed) YES -> advance bus | 3.2.6 | 98 |
| 31, 57, 33 | "LAOP 31,57,33, EXT" YES -> advance bus | 3.2.6 | 98 |
| OP 20 | "BX / OP 20" -> SELECT BX (38.68.02.1); title "TBC I/O INSTRUCTIONS - OP 20 AND OP 24" | 3.2.7 | 99 |
| OP 24 | "DISC / OP 24" -> SELECT DISC SYNC | 3.2.7 | 99 |
| OP X00 | "IO INSTR ?" YES "OP X00" | 3.2.7 | 99 |
| 35, 75, 43, X1 | "35, 75 43, X1 ?" YES -> SAU first-level path | 3.2.8 | 100 |
| OP X1 | OP DECODE legend: "OP X1 38.22.07.1" | 3.2.8 | 100 |
| 35 OR 75 | OP DECODE legend: "LAOP 35 OR 75 38.22.10.1" | 3.2.8 | 100 |
| 75 | OP DECODE legend: "LAOP 75 38.22.09.1" | 3.2.8 | 100 |
| 43 | OP DECODE legend: "LAOP 43 38.22.09.1" | 3.2.8 | 100 |
| (blank) | "LAOP ?" (no code printed) YES -> "BB OR BI ?" | 3.2.8 | 100 |
| 03 | OP DECODE "LAOP 03 38.22.11.1"; "FIRST OR ONLY OPERAND" YES "03 05" -> GI TOB TO C REG [first operand] | 3.2.9 | 101 |
| 05 | OP DECODE "LAOP 05 38.22.07.1"; FIRST OR ONLY YES "03 05" and LAST, OR ONLY YES "05 07" [only operand] | 3.2.9 | 101 |
| 07 | OP DECODE "LAOP 07 38.22.11.1"; FIRST OR ONLY NO "07" (-> GI TOB TO D REG), LAST, OR ONLY YES "05 07" -> SET SAU GO TRIGGER [last operand] | 3.2.9 | 101 |
| 15 | "LAOP 15" (38.22.11.1) -> IS C REG EMPTY / VFL RDY FOR MCND -> SET VFL WAIT FOR MULTIPLICAND TRIG.; title "VFL SPECIAL OPERAND LAOP 15" | 3.2.10 | 102 |
| OP X2 | "OP X2" YES -> FP instruction level; SIGNAL PAU & SAU TO START; title "FP INSTRUCTION LEVEL OPX2" | 3.2.11 | 103 |

The pages carry no LAOP decode table, only the fragments above. The OP DECODE legends on PDF 100 and 101 give an ALD page for each decoder:
- 38.22.07.1 decodes OP X1 and LAOP 05.
- 38.22.09.1 decodes LAOP 75 and 43.
- 38.22.10.1 decodes LAOP 35 OR 75.
- 38.22.11.1 decodes LAOP 03, 07 and 15.

### Appendix E. Figs 3.2.15-3.2.21 and LAOP table (reader E)

#### Figure 3.2.15 SETTING MAR MODE

- Title as printed: "FIGURE 3.2.15. SETTING MAR MODE"
- PDF page 107 (portrait, rendered 300 dpi gray)
- Header: "M3-04-3" (left), "LA FLOW DIAGRAMS" (right)
- Printed page at foot: 2-17 (printed as "2-1'7", a damaged 7)
- Issue date at foot: 2/1/62
- No "CPU 7101 SER. NO." applicability note on this page.

##### 1. Boxes (PRINTED, verbatim; ALD page under each box as printed)

Rectangles (actions / states):
- A1 "MAR MODE OFF" (entry box; no ALD ref)
- A2 "SIGNAL PAU OF LA TESTS COMPLETE" (38.23.01.1)
- A3 "SIGNAL PAU TO SET "MSTR TEST CMPLT" TRIG" (38.23.01.1)
- A4 "RESET ALL IND TEST TRIGGERS" (38.35.05.1) -- on the left (NEW SETTING MAR) branch
- A5 "RESET ALL IND TEST TRIGGERS" (38.35.01.1) -- on the right ("-P NOT ALL OTHER TEST TRIGS") branch
- A6 "PREVENT SETTING "A CHKR IND TEST M" TRIG" (38.35.01.1)
- A7 "SET "MAR MODE" AND "MAR NEXT INSTRN" TRIGS" (38.35.04.1) -- left branch
- A8 "SET "INTRUPT NEXT INSTRN" TRIGGER" (38.35.05.1) -- left branch (spelled INTRUPT here)
- A9 "SET "MAR .MODE" AND "MAR NEXT INSTRN" TRIGS" (38.35.04.1) -- right branch (stray dot before MODE is a print artifact)
- A10 "SET "INTRPT NEXT INSTRN" TRIGGER" (38.35.05.1) -- right branch (spelled INTRPT here)

Hexagons (conditions):
- C1 "ARITH INSTR EXECUTED ?" -- NO (dashed line) -> C2; YES (dashed line) -> C3
- C2 ""NOOP IND TEST M" ON ?" -- YES -> line that branches left to A3 and continues down to the "COND INTRPT OR MAR TRIGS" junction. NO exit: none drawn.
- C3 ""LA NORMAL IND TEST M" ON ?" -- YES -> right to A2, and down to C4. NO exit: none drawn.
- C4 ""EXEC UNIT IND TEST M" ON ?" -- YES -> down to C5 and right to C6. NO exit: none drawn.
- C5 "A CHKR IND TEST M ON ?" -- YES -> left into the "COND INTRPT OR MAR TRIGS" line. NO exit: none drawn.
- C6 "A CHK COMPLETED ?" -- YES -> (labelled "CHK COMP IMMEDIATE 38.35.02.1") down to C7. NO exit: none drawn.
- C7 "A CHKR ERROR ?" -- NO -> left; that line is labelled ""-P NOT ALL OTHER TEST TRIGS"" and feeds A5 and A6; from the same junction a line goes down to C9. YES exit: none drawn.
- C8 (left) "INTRUPT ?" -- NO -> A7; YES -> A8
- C9 (right) "INTRPT ?" -- NO -> A9; YES -> A10

Line labels (PRINTED):
- "COND INTRPT OR MAR TRIGS 38.35.02.1" -- the horizontal line collecting C2-YES and C5-YES, running left then down.
- "NEW SETTING MAR" -- on the left vertical; branches right to A4 and continues down to C8.
- "CHK COMP IMMEDIATE 38.35.02.1" -- on C6 YES exit.
- ""-P NOT ALL OTHER TEST TRIGS"" -- on the C7 NO line.

##### 2. Structure

No sequencer bar is drawn on this page; it is a decision tree. DERIVED reading:
- Entry: MAR mode off. After an instruction, if it was NOT an arithmetic instruction and the "NOOP IND TEST M" trigger is on, the LA signals the PAU to set "MSTR TEST CMPLT" and goes to the "COND INTRPT OR MAR TRIGS" path.
- If it WAS an arithmetic instruction and "LA NORMAL IND TEST M" is on, the LA signals the PAU that LA tests are complete; then if "EXEC UNIT IND TEST M" is on, either (a) "A CHKR IND TEST M" on -> COND INTRPT OR MAR TRIGS path, or (b) A check completed (CHK COMP IMMEDIATE) and no A-checker error -> reset all IND test triggers, prevent setting "A CHKR IND TEST M", then INTRPT? decision.
- On the COND INTRPT OR MAR TRIGS path (NEW SETTING MAR): reset all IND test triggers, then INTRUPT? NO -> set MAR MODE and MAR NEXT INSTRN; YES -> set INTRUPT NEXT INSTRN.
- (DERIVED) "MAR" here appears to be the indicator/interrupt-test "mode" (test triggers per instruction class), not the memory address register -- the page does not expand it.

##### 3. Step table

| step | condition(s) (PRINTED) | action(s) (PRINTED) | ALD page | notes |
|---|---|---|---|---|
| 0 | -- | MAR MODE OFF | -- | entry |
| 1 | ARITH INSTR EXECUTED ? NO; "NOOP IND TEST M" ON ? YES | SIGNAL PAU TO SET "MSTR TEST CMPLT" TRIG; -> COND INTRPT OR MAR TRIGS | 38.23.01.1; 38.35.02.1 | dashed NO line |
| 2 | ARITH INSTR EXECUTED ? YES; "LA NORMAL IND TEST M" ON ? YES | SIGNAL PAU OF LA TESTS COMPLETE | 38.23.01.1 | dashed YES line |
| 3 | + "EXEC UNIT IND TEST M" ON ? YES; A CHKR IND TEST M ON ? YES | -> COND INTRPT OR MAR TRIGS | 38.35.02.1 | |
| 4 | COND INTRPT OR MAR TRIGS (NEW SETTING MAR) | RESET ALL IND TEST TRIGGERS | 38.35.05.1 | |
| 5 | INTRUPT ? NO | SET "MAR MODE" AND "MAR NEXT INSTRN" TRIGS | 38.35.04.1 | |
| 6 | INTRUPT ? YES | SET "INTRUPT NEXT INSTRN" TRIGGER | 38.35.05.1 | |
| 7 | "EXEC UNIT IND TEST M" ON ? YES; A CHK COMPLETED ? YES (CHK COMP IMMEDIATE) ; A CHKR ERROR ? NO ("-P NOT ALL OTHER TEST TRIGS") | RESET ALL IND TEST TRIGGERS; PREVENT SETTING "A CHKR IND TEST M" TRIG | 38.35.02.1; 38.35.01.1; 38.35.01.1 | |
| 8 | INTRPT ? NO | SET "MAR MODE" AND "MAR NEXT INSTRN" TRIGS | 38.35.04.1 | |
| 9 | INTRPT ? YES | SET "INTRPT NEXT INSTRN" TRIGGER | 38.35.05.1 | |

##### 4. Counters, timers, triggers, registers, LAOP named

- Counters: none named (no IAUC/OCC/TBC/ABC/SCC on this page).
- Timers: none named.
- Triggers: "NOOP IND TEST M", "LA NORMAL IND TEST M", "EXEC UNIT IND TEST M", "A CHKR IND TEST M", "MSTR TEST CMPLT" (in PAU), "MAR MODE", "MAR NEXT INSTRN", "INTRUPT/INTRPT NEXT INSTRN", "ALL IND TEST TRIGGERS", "ALL OTHER TEST TRIGS".
- Units: PAU, LA (in "LA TESTS"), A CHKR / A CHK (A checker).
- Registers: none named. LAOP codes: none.

##### 5. TIME

PRINTS NO TIME.

##### 6. [KEY] items

- **[KEY]** NOOP: ""NOOP IND TEST M" ON ?" (C2, on the not-arithmetic-instruction branch) -> "SIGNAL PAU TO SET "MSTR TEST CMPLT" TRIG" (38.23.01.1).
- **[KEY]** "SIGNAL PAU OF LA TESTS COMPLETE" (38.23.01.1) -- LA-to-PAU handshake when "LA NORMAL IND TEST M" is on for an executed arithmetic instruction.
- **[KEY]** MAR MODE: "SET "MAR MODE" AND "MAR NEXT INSTRN" TRIGS" (38.35.04.1) when not INTRPT; "SET "INTRPT NEXT INSTRN" TRIGGER" (38.35.05.1) when INTRPT.
- **[KEY]** "PREVENT SETTING "A CHKR IND TEST M" TRIG" (38.35.01.1) after "CHK COMP IMMEDIATE" with no A CHKR ERROR.

##### 7. Could not read / not drawn

- Everything legible. The NO exits of C2, C3, C4, C5, C6 and the YES exit of C7 are not drawn on the page (not illegible: absent).

#### Figure 3.2.16 FP ABC ACTIONS-TRANSFER INDICATOR TIMER

- Title as printed: "FIGURE 3.2.16. FP ABC ACTIONS-TRANSFER INDICATOR TIMER"
- PDF page 108 (landscape fold-out, rendered 300 dpi gray, read in 1100 px tiles)
- Header: "M3-04-3" / "LA FLOW DIAGRAMS"
- Printed page at foot: 2-19/2-20
- Issue date at foot: 2/1/62
- No "CPU 7101 SER. NO." applicability note.
- A vertical fold/scan line crosses the sheet at about x=3830 px; it clips "INT. FETCH", "STORE TYPE LEVEL" and "LAST INSTR. LEVEL" but all are readable.

##### 1. Boxes (PRINTED, verbatim; ALD page in parentheses)

Pre-timer (entry) part:
- R1 "ABC AT NEW LEVEL" (entry; no ALD)
- R2 "GO IND FIELD LEVELS TO MAIN IND REG AND GO IC FIELD LEVELS TO IC RUFFER" (35.27.01.1) -- "RUFFER" as printed (DERIVED: BUFFER). Fed directly from R1, in parallel with H1.
- H1 "DISC ABC" -- NO -> H2. YES: not drawn.
- H2 "LEVEL PREPARATION FINISHED ?" -- YES (line label "LF & LC ON") -> H3. NO: not drawn.
- H3 "HSCLN MODE ?" -- NO -> H4; YES -> joins the H4-NO line into H6.
- H4 "PREVIOUS INSTR. PROPERLY EXECUTED ?" -- YES (line label "MAR MODE") -> H5; NO (line label "INTRUPT") -> H6.
- H5 "ABC ACTION YET ?" (left) -- NO (line label "ABC AES ON") -> into the TRANSFER INDICATOR TIMER bar. YES: not drawn.
- H6 "ABC ACTION YET ?" (right) -- NO (line label "ABC AES ON") -> off-page arrow "START HSCLN TIMER" (38.39.02.1). YES: not drawn.
- "38.38.01.1" printed just above the left part of the timer bar, below-left of H6 (DERIVED: ALD of the TRANSFER INDICATOR TIMER).
- Timer bar (horizontal): "TRANSFER INDICATOR TIMER". Phase lines drop from it, left to right: "E.M̄" (M with overbar), "E.M", "M", "E + M".

Phase E.M̄ (left column):
- R3 "RESET ABC AES" (38.81.03.1)
- R4 "GI X̄R̄ INDS TO IND REG" (35.27.03.1) -- overbar over "XR" as printed (DERIVED: XR-bar, i.e. the non-index-register indicators)
- H7 "LAST INSTR. LEVEL ?" -- YES (line label "IC ON") -> R5, R6, then H9. NO: not drawn.
- R5 "GI IC FIELD TO IC BUFFER" (35.27.02.1)
- R6 "RESET MAR MODE" (38.35.04.1)
- H8 "NOOP ABC ?" -- hung off the E.M̄ line ahead of H7; YES -> R7. NO: not drawn.
- R7 "SET NOOP MODE" (38.34.01.1)
- H9 "EXT STO TAGS" (no "?") -- YES -> R8; NO -> H10.
- H10 "STORE TYPE LEVEL" (no "?") -- NO -> R8; other exit (unlabelled, down) -> R9.
- R9 "WAIT FOR A BUS TIMER" (no ALD)
- R8 ""NO DELAY IND. TEST"" (38.32) -- printed with quotes, ALD "38.32" only.
- R10 "SET IND. TEST E" (38.38.03.1)
- H11 "NOOP MODE ?" -- YES -> R11; NO -> R13.
- R11 "SET LA NOOP IND. TEST M" (38.35.03.1) -> R12 "SIGNAL PAU TO SET "MSTR TEST COMPLT"" (38.23.01.1)
- R13 "SET NORMAL IND. TEST M" (38.35.01.1) -> R14 "SIGNAL PAU OF LA TESTS COMPLETE" (38.23.01.1)

Phase E.M (centre column):
- H12 "1st INSTR. LEVEL ?" -- YES (line label ""MAR NEXT INSTR" ON") -> R15 and H13. NO: not drawn.
- R15 "RESET "MAR NEXT INSTR" TRIGGER" (38.35.04.1)
- H13 "IS THIS THE INTRPT FREE INSTR ?" -- YES (line label "INTRPT IS DISABLED") -> R16. NO: not drawn.
- R16 "RESET "DISABLE INTRPT" TRIGGER" (38.39.05.1)
- R17 "RESET UNIPOLAR INDS" (35.27.07.1)
- H14 "NOOP MODE ?" -- YES -> line labelled "NON-ARITHMETIC" -> H15 and H17; NO -> H16.
- H16 "INT. FETCH ?" -- YES (line label "INT. TAG ON (X2 FETCH)") -> off-page arrow "FETCHES" (under the heading "TO A BUS TIMER"). NO: not drawn.
- H15 "ABC FROM TAG ON ?" -- YES -> H18. NO: not drawn.
- H18 "STORE OR INT. FETCH ?" -- YES (line label "LAAR BUSY") -> R18. NO: not drawn.
- R18 "RESET LAAR BUSY TRIG" (38.53.03.1)
- H17 "LAST INSTR. LEVEL ?" -- YES (line label "IC ON") -> H19. NO: not drawn.
- H19 "LAOP 11" (no "?") -- NO -> R19. YES: not drawn.
- R19 "RESET "MSTR TEST COMPLT" TRIG. IN PAU" (38.23.02.1) -> R20 "ALLOW PAU TO RE-MEMORIZE THE INTRPT. LINE" (no ALD)

Phase M:
- H20 "EXT STO TAGS" (no "?") -- YES -> R21; NO -> H21.
- H21 "STORE TYPE LEVEL" (no "?") -- NO -> R21. Other exit: not drawn.
- R21 "ADV. ABC IF NOT INTLKD BY TBC" (no ALD)

Phase E + M:
- H22 "NOOP MODE ?" -- NO -> off-page arrow "STORES" (under "TO A BUS TIMER"). YES: not drawn.

Legend / free text (PRINTED, bottom right, two separate lines):
- "OP X2 FETCH OR STORE"
- "LAOP 13 STORE"
- (DERIVED, uncertain) the two lines may gloss the "LAOP 11" hexagon and the STORES/FETCHES exits; the page does not print "LAOP 11 =". Not asserted.

Right margin text: "TO A BUS TIMER" (heading over the "STORES" and "FETCHES" exits).

##### 2. Structure

Sequencer: TRANSFER INDICATOR TIMER (horizontal bar; DERIVED ALD 38.38.01.1).
- TON: from "ABC AT NEW LEVEL", DISC ABC NO, LEVEL PREPARATION FINISHED (LF & LC ON), not HSCLN MODE, PREVIOUS INSTR. PROPERLY EXECUTED (MAR MODE), ABC ACTION YET? NO ("ABC AES ON").
- Alternate entry: HSCLN MODE YES, or previous instruction not properly executed (INTRUPT) -> ABC ACTION YET? NO (ABC AES ON) -> START HSCLN TIMER (38.39.02.1) instead of the transfer indicator timer.
- TOF: not printed.
- Phase lines: E.M̄, E.M, M, E + M (as printed).

##### 3. Step table

| step / phase | condition(s) (PRINTED) | action(s) (PRINTED) | ALD | notes |
|---|---|---|---|---|
| entry | ABC AT NEW LEVEL | GO IND FIELD LEVELS TO MAIN IND REG AND GO IC FIELD LEVELS TO IC RUFFER | 35.27.01.1 | unconditional on ABC reaching new level |
| entry | DISC ABC NO; LEVEL PREPARATION FINISHED YES (LF & LC ON); HSCLN MODE NO; PREVIOUS INSTR. PROPERLY EXECUTED YES (MAR MODE); ABC ACTION YET NO (ABC AES ON) | start TRANSFER INDICATOR TIMER | 38.38.01.1 (DERIVED) | |
| entry | HSCLN MODE YES, or PREVIOUS INSTR. PROPERLY EXECUTED NO (INTRUPT); ABC ACTION YET NO (ABC AES ON) | START HSCLN TIMER | 38.39.02.1 | **[KEY]** |
| E.M̄ | -- | RESET ABC AES | 38.81.03.1 | |
| E.M̄ | -- | GI X̄R̄ INDS TO IND REG | 35.27.03.1 | |
| E.M̄ | NOOP ABC YES | SET NOOP MODE | 38.34.01.1 | **[KEY]** |
| E.M̄ | LAST INSTR. LEVEL YES (IC ON) | GI IC FIELD TO IC BUFFER; RESET MAR MODE | 35.27.02.1; 38.35.04.1 | |
| E.M̄ | then EXT STO TAGS YES, or STORE TYPE LEVEL NO | "NO DELAY IND. TEST"; SET IND. TEST E | 38.32; 38.38.03.1 | |
| E.M̄ | EXT STO TAGS NO and STORE TYPE LEVEL (other exit) | WAIT FOR A BUS TIMER | -- | |
| E.M̄ | NOOP MODE YES | SET LA NOOP IND. TEST M; SIGNAL PAU TO SET "MSTR TEST COMPLT" | 38.35.03.1; 38.23.01.1 | |
| E.M̄ | NOOP MODE NO | SET NORMAL IND. TEST M; SIGNAL PAU OF LA TESTS COMPLETE | 38.35.01.1; 38.23.01.1 | |
| E.M | 1st INSTR. LEVEL YES ("MAR NEXT INSTR" ON) | RESET "MAR NEXT INSTR" TRIGGER | 38.35.04.1 | |
| E.M | + IS THIS THE INTRPT FREE INSTR YES (INTRPT IS DISABLED) | RESET "DISABLE INTRPT" TRIGGER | 38.39.05.1 | |
| E.M | -- | RESET UNIPOLAR INDS | 35.27.07.1 | |
| E.M | NOOP MODE NO; INT. FETCH YES (INT. TAG ON (X2 FETCH)) | -> FETCHES (TO A BUS TIMER) | -- | |
| E.M | NOOP MODE YES (NON-ARITHMETIC); ABC FROM TAG ON YES; STORE OR INT. FETCH YES (LAAR BUSY) | RESET LAAR BUSY TRIG | 38.53.03.1 | **[KEY]** |
| E.M | NOOP MODE YES (NON-ARITHMETIC); LAST INSTR. LEVEL YES (IC ON); LAOP 11 NO | RESET "MSTR TEST COMPLT" TRIG. IN PAU; ALLOW PAU TO RE-MEMORIZE THE INTRPT. LINE | 38.23.02.1; -- | |
| M | EXT STO TAGS YES, or STORE TYPE LEVEL NO | ADV. ABC IF NOT INTLKD BY TBC | -- | **[KEY]** counter interlock |
| E + M | NOOP MODE NO | -> STORES (TO A BUS TIMER) | -- | |

##### 4. Counters, timers, triggers, registers, LAOP

- Counters: ABC, TBC ("ADV. ABC IF NOT INTLKD BY TBC"). "DISC ABC" (DERIVED: ABC discontinued/disconnected).
- Timers: TRANSFER INDICATOR TIMER; HSCLN TIMER ("START HSCLN TIMER"); A BUS TIMER ("WAIT FOR A BUS TIMER", "TO A BUS TIMER").
- Triggers/modes: ABC AES; LF, LC ("LF & LC ON"); HSCLN MODE; MAR MODE; "MAR NEXT INSTR"; "DISABLE INTRPT"; NOOP MODE; NOOP ABC; LA NOOP IND. TEST M; NORMAL IND. TEST M; IND. TEST E; "MSTR TEST COMPLT" (PAU); LAAR BUSY TRIG; INT. TAG; EXT STO TAGS; IC (IC ON); ABC FROM TAG.
- Registers: MAIN IND REG / IND REG; IC BUFFER (IC RUFFER); LAAR (via LAAR BUSY); IND field, IC field, XR INDS, UNIPOLAR INDS.
- LAOP: "LAOP 11" (hexagon), "LAOP 13 STORE" (legend). "OP X2 FETCH OR STORE" (legend).

##### 5. TIME

PRINTS NO TIME. The phase lines E.M̄, E.M, M, E + M are timer phases; no clock, pulse or cycle count is printed.

##### 6. [KEY] items

- **[KEY]** NOOP: "NOOP ABC ?" YES -> "SET NOOP MODE" (38.34.01.1); "NOOP MODE ?" YES -> "SET LA NOOP IND. TEST M" (38.35.03.1) -> "SIGNAL PAU TO SET "MSTR TEST COMPLT"" (38.23.01.1); NO -> "SET NORMAL IND. TEST M" (38.35.01.1) -> "SIGNAL PAU OF LA TESTS COMPLETE" (38.23.01.1).
- **[KEY]** NOOP MODE YES path labelled "NON-ARITHMETIC".
- **[KEY]** LAST INSTR: "LAST INSTR. LEVEL ?" YES "IC ON" -> "GI IC FIELD TO IC BUFFER" (35.27.02.1), "RESET MAR MODE" (38.35.04.1); second instance -> "LAOP 11" NO -> "RESET "MSTR TEST COMPLT" TRIG. IN PAU" (38.23.02.1) -> "ALLOW PAU TO RE-MEMORIZE THE INTRPT. LINE".
- **[KEY]** Houseclean: "HSCLN MODE ?"; "PREVIOUS INSTR. PROPERLY EXECUTED ?" NO "INTRUPT"; "ABC ACTION YET ?" NO "ABC AES ON" -> "START HSCLN TIMER" (38.39.02.1).
- **[KEY]** MAR MODE: "PREVIOUS INSTR. PROPERLY EXECUTED ?" YES "MAR MODE"; "RESET MAR MODE" (38.35.04.1); "1st INSTR. LEVEL ?" YES ""MAR NEXT INSTR" ON" -> "RESET "MAR NEXT INSTR" TRIGGER" (38.35.04.1); "IS THIS THE INTRPT FREE INSTR ?" YES "INTRPT IS DISABLED" -> "RESET "DISABLE INTRPT" TRIGGER" (38.39.05.1).
- **[KEY]** LAAR BUSY: "ABC FROM TAG ON ?" YES -> "STORE OR INT. FETCH ?" YES "LAAR BUSY" -> "RESET LAAR BUSY TRIG" (38.53.03.1).
- **[KEY]** Counter interlock: "ADV. ABC IF NOT INTLKD BY TBC" (after EXT STO TAGS YES or STORE TYPE LEVEL NO, phase M).
- **[KEY]** Store wait on the A bus: "EXT STO TAGS" NO -> "STORE TYPE LEVEL" -> "WAIT FOR A BUS TIMER"; "NOOP MODE ?" NO -> "STORES" (TO A BUS TIMER).
- **[KEY]** "INT. FETCH ?" YES "INT. TAG ON (X2 FETCH)" -> "FETCHES".
- **[KEY]** Legend: "OP X2 FETCH OR STORE"; "LAOP 13 STORE".

##### 7. Could not read / not drawn

- Nothing illegible. Many exits are not drawn (listed per box above as "not drawn").
- "RUFFER" is printed (typo for BUFFER).
- Placement of "38.38.01.1" (timer bar vs H6) is DERIVED.

#### Figure 3.2.17 VFL ABC ACTIONS-TRANSFER INDICATOR TIMER

- Title as printed: "FIGURE 3.2.17. VFL ABC ACTIONS-TRANSFER INDICATOR TIMER"
- PDF page 109 (landscape fold-out; 300 dpi tiles, one 400 dpi check)
- Header: "M3-04-3" / "LA FLOW DIAGRAMS"
- Printed page at foot: 2-21/2-22
- Issue date at foot: 2/1/62
- No "CPU 7101 SER. NO." applicability note.
- This page has NO entry part: it starts at the TRANSFER INDICATOR TIMER bar (the ABC-at-new-level entry is on Fig 3.2.16). A fold line at x~3830 px clips "A BUS TIMER ACTION RQD", "INT. FETCH", "LAOP 11", "RESET "MSTR TEST CMPLT" TRIG IN PAU"; all still readable.

##### 1. Boxes (PRINTED, verbatim; ALD page in parentheses)

Timer bar (horizontal, across top): "TRANSFER INDICATOR TIMER". Phase lines, left to right: "E. M̄" (overbar on M), "E. M", "M", "E + M". No ALD printed for the bar.

Phase E. M̄:
- R1 "RESET ABC AES" (38.31.03.1)  -- NOTE: Fig 3.2.16 prints 38.81.03.1 for the same box.
- R2 "GI X̄R̄ INDS TO IND REG" (35.27.03.1) -- overbar over XR.
- H1 "NOOP ABC ?" -- hung off the E.M̄ line beside R2; YES -> R3 and on down to H2. NO: not drawn.
- R3 "SET NOOP MODE" (no ALD printed on this page)
- H2 "VFL STORE OR FETCH LEVEL ?" -- YES (line label "SAU EN MEM TRIG ON") -> H3. NO: not drawn.
- H3 "1ST NOOP OF THIS INSTR. ?" -- YES (line label "NO NOOP MODE") -> R4. NO: not drawn.
- R4 "SET "VFL INSTR REJECT" TRIGGER" (38.23.04.1) -> R5 "SIGNAL SAU TO STOP HSKPING." (38.23.04.1)
- H4 "LAST INSTR. LEVEL ?" -- YES (line label "IC ON") -> R6, R7, then H5. NO: not drawn.
- R6 "GI IC FIELD TO IC BUFFER" (35.27.02.1)
- R7 "RESET MAR MODE" (38.35.04.1)
- H5 "NOOP'D OR NOOP MODE?" -- YES -> R8; NO -> H6.
- H6 "ABC STORE ACTION RQD ?" -- NO -> R8. YES: not drawn.
- R8 ""NO DELAY IND TEST"" (38.32.09.1)
- R9 "SET IND TEST E" (38.38.03.1)
- H7 "NOOP MODE ?" -- YES -> R10; NO -> R12.
- R10 "SET LA NOOP IND TEST M" (38.35.03.1) -> R11 "SIGNAL PAU TO SET "MSTR TEST COMPLET"" (38.23.01.1)
- R12 "SET "NORMAL IND TEST" M" (38.35.01.1) -> R13 "SIGNAL PAU OF LA TESTS COMPLT" (38.23.01.1)

Phase E. M:
- H8 "1ST INSTR. LEVEL ?" -- YES -> R14 and H9. NO: not drawn.
- R14 "RESET "MAR NEXT INSTR" TRIG" (38.35.04.1)
- H9 "IS THIS THE INTRPT FREE INSTR ?" -- YES (line label ""MAR NEXT INSTR" ON") -> R15. NO: not drawn.  (Fig 3.2.16 labels the same exit "INTRPT IS DISABLED".)
- R15 "RESET "DISABLE INTRPT" TRIG" (38.39.05.1)
- R16 "RESET UNIPOLAR INDS" (35.27.07.1)
- H10 "NOOP MODE" (no "?") -- NO -> H11. YES: not drawn.
- H11 "1ST INSTR. LEVEL ?" -- YES (line label, stacked vertically: "X1 / 35 / 75 / 48") -> R17. NO: not drawn.
- R17 "SET "SAU EN MEM" TRIG" (38.34.02.1)
- H12 "LAST INSTR LEVEL ?" -- YES (line label "IC ON") -> R18. NO: not drawn.
- R18 "RESET SAU EN MEM TRIG" (38.34.02.1)
- H13 "NOOP NODE" (printed "NODE", DERIVED: MODE; no "?") -- YES -> line labelled "NON ARITH" -> H14 and H16; other exit (right, unlabelled) -> H15.
- H15 "INT. FETCH ?" -- YES (line label "INT TAG ON") -> off-page arrow "FETCHES". NO: not drawn.
- H14 "ABC FROM TAG ON ?" -- YES -> H17. NO: not drawn.
- H17 "STORE OR INT. FETCH ?" -- YES (line label "LAAR BUSY") -> R19. NO: not drawn.
- R19 "RESET LAAR BUSY TRIG" (38.53.03.1)
- H16 "LAST INSTR LEVEL ?" -- YES (line label "IC ON") -> H18. NO: not drawn.
- H18 "LAOP 11" -- one exit (left, UNLABELLED on this page; Fig 3.2.16 labels it NO) -> R20.
- R20 "RESET "MSTR TEST CMPLT" TRIG IN PAU" (38.23.02.1) -> R21 "ALLOW PAU TO RE-MEMORIZE THE INTRPT LINE" (no ALD)

Phase M:
- H19 "NOOP MODE ?" -- YES -> R22; NO -> H20.
- H20 "A BUS TIMER ACTION RQD ?" -- NO -> R22. YES: not drawn.
- R22 "ADV. ABC IF NOT INTLKD BY TBC" (38.31.05.1)

Phase E + M:
- H21 "NOOP MODE ?" -- NO -> off-page arrow "STORES". YES: not drawn.

Right margin: a brace spanning "STORES" and "FETCHES" with "TO A BUS TIMER".

Legend (PRINTED, bottom right, verbatim, ditto marks as printed):
```
OP    X1  INSTR
LAOP  05  FETCH (1 of 1)
  "   03  FETCH (1 of 2)
  "   07  FETCH (2 of 2)
  "   17  STORE (1ST)
  "   23  STORE (2ND)
  "   21  STORE (SPECIAL)
  "   15  FETCH (SPECIAL)
```

##### 2. Structure

Sequencer: TRANSFER INDICATOR TIMER (TON/TOF not printed on this page; DERIVED: same entry as Fig 3.2.16). Phases E.M̄, E.M, M, E + M.
VFL-specific differences from Fig 3.2.16 (DERIVED by comparison): the SAU EN MEM trigger (set at 1st instruction level when not NOOP, line labelled X1/35/75/48; reset at last instruction level); the VFL reject path (VFL STORE OR FETCH LEVEL with SAU EN MEM TRIG ON, 1st NOOP of this instruction -> SET "VFL INSTR REJECT" TRIGGER, SIGNAL SAU TO STOP HSKPING.); "NOOP'D OR NOOP MODE?" and "ABC STORE ACTION RQD ?" replace EXT STO TAGS / STORE TYPE LEVEL; phase M tests "A BUS TIMER ACTION RQD ?" instead of EXT STO TAGS.

##### 3. Step table

| phase | condition(s) (PRINTED) | action(s) (PRINTED) | ALD | notes |
|---|---|---|---|---|
| E.M̄ | -- | RESET ABC AES | 38.31.03.1 | 38.81.03.1 on Fig 3.2.16 |
| E.M̄ | -- | GI X̄R̄ INDS TO IND REG | 35.27.03.1 | |
| E.M̄ | NOOP ABC ? YES | SET NOOP MODE | -- | **[KEY]** |
| E.M̄ | NOOP ABC YES; VFL STORE OR FETCH LEVEL ? YES (SAU EN MEM TRIG ON); 1ST NOOP OF THIS INSTR. ? YES (NO NOOP MODE) | SET "VFL INSTR REJECT" TRIGGER; SIGNAL SAU TO STOP HSKPING. | 38.23.04.1; 38.23.04.1 | **[KEY]** |
| E.M̄ | LAST INSTR. LEVEL ? YES (IC ON) | GI IC FIELD TO IC BUFFER; RESET MAR MODE | 35.27.02.1; 38.35.04.1 | |
| E.M̄ | NOOP'D OR NOOP MODE? YES, or ABC STORE ACTION RQD ? NO | "NO DELAY IND TEST"; SET IND TEST E | 38.32.09.1; 38.38.03.1 | |
| E.M̄ | NOOP MODE ? YES | SET LA NOOP IND TEST M; SIGNAL PAU TO SET "MSTR TEST COMPLET" | 38.35.03.1; 38.23.01.1 | |
| E.M̄ | NOOP MODE ? NO | SET "NORMAL IND TEST" M; SIGNAL PAU OF LA TESTS COMPLT | 38.35.01.1; 38.23.01.1 | |
| E.M | 1ST INSTR. LEVEL ? YES | RESET "MAR NEXT INSTR" TRIG | 38.35.04.1 | |
| E.M | + IS THIS THE INTRPT FREE INSTR ? YES ("MAR NEXT INSTR" ON) | RESET "DISABLE INTRPT" TRIG | 38.39.05.1 | |
| E.M | -- | RESET UNIPOLAR INDS | 35.27.07.1 | |
| E.M | NOOP MODE NO; 1ST INSTR. LEVEL ? YES (X1 35 75 48) | SET "SAU EN MEM" TRIG | 38.34.02.1 | |
| E.M | LAST INSTR LEVEL ? YES (IC ON) | RESET SAU EN MEM TRIG | 38.34.02.1 | |
| E.M | NOOP NODE YES (NON ARITH); ABC FROM TAG ON ? YES; STORE OR INT. FETCH ? YES (LAAR BUSY) | RESET LAAR BUSY TRIG | 38.53.03.1 | **[KEY]** |
| E.M | NOOP NODE YES (NON ARITH); LAST INSTR LEVEL ? YES (IC ON); LAOP 11 (unlabelled exit) | RESET "MSTR TEST CMPLT" TRIG IN PAU; ALLOW PAU TO RE-MEMORIZE THE INTRPT LINE | 38.23.02.1; -- | |
| E.M | NOOP NODE (other exit); INT. FETCH ? YES (INT TAG ON) | -> FETCHES (TO A BUS TIMER) | -- | |
| M | NOOP MODE ? YES, or A BUS TIMER ACTION RQD ? NO | ADV. ABC IF NOT INTLKD BY TBC | 38.31.05.1 | **[KEY]** interlock |
| E + M | NOOP MODE ? NO | -> STORES (TO A BUS TIMER) | -- | |

##### 4. Counters, timers, triggers, registers, LAOP

- Counters: ABC, TBC.
- Timers: TRANSFER INDICATOR TIMER; A BUS TIMER.
- Triggers/modes: ABC AES; NOOP ABC; NOOP MODE; NOOP'D; SAU EN MEM TRIG; "VFL INSTR REJECT" TRIGGER; MAR MODE; "MAR NEXT INSTR"; "DISABLE INTRPT"; IND TEST E; LA NOOP IND TEST M; "NORMAL IND TEST" M; "MSTR TEST COMPLET"/"MSTR TEST CMPLT" (PAU); LAAR BUSY TRIG; INT TAG; IC ON; ABC FROM TAG.
- Units: SAU, PAU.
- Registers: IND REG; IC BUFFER; LAAR (LAAR BUSY); XR INDS; UNIPOLAR INDS.
- LAOP: "LAOP 11" (hexagon); legend LAOP 05, 03, 07, 17, 23, 21, 15; "OP X1 INSTR". Line label "X1 35 75 48".

##### 5. TIME

PRINTS NO TIME.

##### 6. [KEY] items

- **[KEY]** NOOP: "NOOP ABC ?" YES -> "SET NOOP MODE"; "NOOP'D OR NOOP MODE?"; "NOOP MODE ?" YES -> "SET LA NOOP IND TEST M" (38.35.03.1) -> "SIGNAL PAU TO SET "MSTR TEST COMPLET"" (38.23.01.1); "NOOP NODE" YES "NON ARITH".
- **[KEY]** "VFL STORE OR FETCH LEVEL ?" YES "SAU EN MEM TRIG ON" -> "1ST NOOP OF THIS INSTR. ?" YES "NO NOOP MODE" -> "SET "VFL INSTR REJECT" TRIGGER" (38.23.04.1) -> "SIGNAL SAU TO STOP HSKPING." (38.23.04.1).
- **[KEY]** "SET "SAU EN MEM" TRIG" (38.34.02.1) at "1ST INSTR. LEVEL ?" YES "X1 35 75 48"; "RESET SAU EN MEM TRIG" (38.34.02.1) at "LAST INSTR LEVEL ?" YES "IC ON".
- **[KEY]** LAST INSTR: "LAST INSTR. LEVEL ?" YES "IC ON" -> "GI IC FIELD TO IC BUFFER", "RESET MAR MODE"; "LAOP 11" -> "RESET "MSTR TEST CMPLT" TRIG IN PAU" (38.23.02.1) -> "ALLOW PAU TO RE-MEMORIZE THE INTRPT LINE".
- **[KEY]** MAR MODE: "RESET MAR MODE" (38.35.04.1); "RESET "MAR NEXT INSTR" TRIG" (38.35.04.1); "IS THIS THE INTRPT FREE INSTR ?" YES ""MAR NEXT INSTR" ON" -> "RESET "DISABLE INTRPT" TRIG" (38.39.05.1).
- **[KEY]** LAAR BUSY: "ABC FROM TAG ON ?" YES -> "STORE OR INT. FETCH ?" YES "LAAR BUSY" -> "RESET LAAR BUSY TRIG" (38.53.03.1).
- **[KEY]** Interlock: "ADV. ABC IF NOT INTLKD BY TBC" (38.31.05.1), after "NOOP MODE ?" YES or "A BUS TIMER ACTION RQD ?" NO.
- **[KEY]** "ABC STORE ACTION RQD ?" NO -> "NO DELAY IND TEST" (38.32.09.1).
- **[KEY]** Legend: OP X1 INSTR; LAOP 05 FETCH (1 of 1); 03 FETCH (1 of 2); 07 FETCH (2 of 2); 17 STORE (1ST); 23 STORE (2ND); 21 STORE (SPECIAL); 15 FETCH (SPECIAL).

##### 7. Could not read / not drawn

- Nothing illegible. Many exits not drawn (see each box).
- "NOOP NODE" is printed so (typo). "COMPLET" / "COMPLT" / "CMPLT" spellings as printed.
- R3 "SET NOOP MODE" has no ALD on this page (Fig 3.2.16: 38.34.01.1).
- The meaning of the stacked line label "X1 35 75 48" is not printed (DERIVED guess: operation codes for which SAU EN MEM is set; not asserted).

#### Figure 3.2.18 BRANCH ABC ACTIONS-TRANSFER INDICATOR TIMER

- Title as printed: "FIGURE 3.2.18. BRANCH ABC ACTIONS- TRANSFER INDICATOR TIMER" (a stray mark before FIGURE and after 3.2.18)
- PDF page 110 (landscape fold-out; 300 dpi tiles, 400 dpi checks of the centre and bottom)
- Header: "M3-04-3" / "LA FLOW DIAGRAMS"
- Printed page at foot: 2-23/2-24
- Issue date at foot: 2/1/62
- No "CPU 7101 SER. NO." applicability note.
- A fold line at x~3830 px (300 dpi) crosses "SET LA "HSCLN MODE" TRIGGER", "SET NORMAL IND TEST M", "SIGNAL PAU TO LA TESTS COMPLT", the right "SIC BIN" and its ALD; all still readable.
- No LAOP legend on this page.

##### 1. Boxes (PRINTED, verbatim; ALD in parentheses)

Timer bar (horizontal, top): "TRANSFER INDICATOR TIMER". Phase lines left to right: "E. M̄", "E.M", "M", "E + M". No ALD on the bar.

###### Phase E. M̄ (left)
- R1 "RESET ABC AES" (38.31.03.1)
- R2 "GI X̄R̄ INDS TO IND. REQ" (35.27.03.1) -- "REQ" as printed (DERIVED: REG); overbar over XR.
- Fork below R2 into three: H1, H2, and the main line.
- H1 "LAOP 31,57 ?" -- YES -> R3. NO: not drawn.
- R3 "RESET TBC AES" (38.01.03.1) -> R4 "ADV. TBC IF NOT INTLKD BY OCC" (no ALD)
- H2 "NOOP ABC ?" -- YES -> R5. NO: not drawn.
- R5 "SET NOOP MODE" (38.34.01.1)
- Main line forks again (right branch) to H3 and H4:
  - H3 "LAOP 31 ?" -- YES -> R6 "RESET LF TAG" (36.01.09.1). NO: not drawn.
  - H4 "LAOP 11" -- YES -> H5. NO: not drawn.
  - H5 "RECOVERY REQ" (no "?") -- YES -> junction J1 (see below). NO: not drawn.
- H6 "LAST INSTR. LEVEL ?" -- YES (line label "IC ON") -> left column. NO: not drawn.
  - Line label on the branch just below: "NOT SIC BIN RECOVERY LEVEL" -- this branch goes right to H7.
  - R7 "GI IC FIELD TO IC BUFFER" (35.27.02.1)
  - R8 "RESET MAR MODE" (38.35.04.1) -- also entered from the right by a line from J1.
  - H8 "NOOP OR NOOP MODE" (lower; no "?") -- YES -> R9; NO -> H9.
  - H9 "ABC STORE ACTION RQD. ?" -- left exit (unlabelled) -> R9. Other exit: not drawn.
  - R9 "NO DELAY IND. TEST" (38.32.09.1)
  - R10 "SET IND. TEST E" (38.38.03.1) -> (a) right to R11 "RESET RQST CYCLE STORE MEM TRIGGER" (38.24.02.1) and R12 "RESET BR SUCC AND COND IND TRIGGERS" (38.24.03.1); (b) a long line round the bottom of the sheet to H20 (NOOP MODE ?).
- H7 "NOOP OR NOOP MODE" (upper; no "?") -- NO -> H10. YES: not drawn.
- H10 "LAOP 45 ?" -- YES -> joins J1's vertical below J1, into H11. NO: not drawn.
- J1 (junction under H5): RECOVERY REQ YES enters; from it (i) a line left to R8 "RESET MAR MODE"; (ii) a line right/up that rises to the top of the sheet and runs right to R30 "RESET "MSTR TEST COMPLT" TRIG IN PAU"; (iii) down to H11.
- H11 "BR SUCC & NO COND INDS" (no "?") -- YES -> R13 "RESET LF TAG" (36.01.09.1), R14 "SET BR RECOVERY INHB LOAD TRIGGER" (no ALD), then on to R15. NO: not drawn.
- R15 "SET "I BOX RQST HSCLN" TRIGGER" (38.39.05.1)
- Bar "START I BOX HSCLN TIMER" (a small horizontal sequencer bar) with phase lines "E" and "M":
  - E -> R16 "RESET I BOX RQST HSCLN TRIGGER" (no ALD)
  - M -> R17 "SET LA "HSCLN MODE" TRIGGER" (38.39.04.1) -> H12
- H12 "IS LA EMPTY ?" -- YES -> R18 "START LA HSCLN OVER TIMER" (38.39.01.1); other exit (right, unlabelled) -> R19 "RESET "I BOX HSCLN TIMER"" (38.0.07.1 -- printed so, one digit group short).
- H20 "NOOP MODE ?" (bottom, reached from R10) -- YES -> R20 "SET LA NOOP IND TEST M" (38.35.03.1) -> R21 "SIGNAL PAU TO SET "MSTR TEST COMPLT"" (38.23.01.1); NO -> R22 "SET NORMAL IND TEST M" (38.35.01.1) -> R23 "SIGNAL PAU TO LA TESTS COMPLT" (38.23.01.1).

###### Phase E.M (centre)
- H13 "1st INSTR.LEVEL ?" -- left exit (labelled "MAR NEXT INSTR", no YES printed) -> R24 "RESET MAR NEXT INSTR TRIGGER" (38.35.04.1) and H14.
- H14 "LAOP 75 ?" -- NO -> H15. YES: not drawn.
- H15 "IS THIS THEINTRPT FREE INSTR. ?" (run-together "THEINTRPT" as printed) -- exit labelled "INTRPT DISABLED" (no YES) -> R25 "RESET "DISABLE INTRPT" TRIGGERS" (38.39.05.1).
- R26 "RESET UNIPOLAR INDS" (35.27.07.1)
- Main line forks: right to H21 (NOOP MODE ?) and down to H16.
- H16 "BR. RECOVERY ?" -- YES (line label "45, 47") -> H17. NO: not drawn.
- H17 "SUCC BRANCH ?" -- YES -> H18; NO -> left vertical V1 down to H22 (left SIC BIN).
- H18 "COND INDS ?" -- YES -> R27 "GI SAU'S COND INDS TO IND REQ." (35.27.05.1) and left into V1; NO -> line to H19 and on round to H23 (right SIC BIN).
- H19 "GOOD RECOVERY LEVEL" (no "?") -- NO (label "47") -> R28. YES: not drawn.
- R28 "GI CNIDC TO MK IND." (35.27.03.1) -- also fed by H21 YES.
- H22 "SIC BIN" (left) -- YES (line label "IC OFF") -> R29 "SIGNAL I BOX OF NO BRANCH".
- H23 "SIC BIN" (right) -- YES (line label "IC OFF") -> R31 "SIGNAL I BOX OF BRANCH".
- "38.38.02.1" is printed between R29 and R31, under R29's right corner (which box it belongs to is ambiguous).
- H21 "NOOP MODE ?" (centre right) -- YES -> down to R28; branch labelled "NON-ARITH INSTR." -> H24; branch -> H25. NO -> H26.
- H26 "INT. FETCH ?" -- YES (line label "INT. TAG ON") -> off-page "FETCHES".
- H24 "LAST INSTR. LEVEL ?" -- YES (line label "ICON" as printed) -> R30.
- R30 "RESET "MSTR TEST COMPLT" TRIG IN PAU" (38.23.02.1) -> R32 "ALLOW PAU TO RE-MEMORIZE THE INTRPT LINE" (no ALD). Also entered from J1 (RECOVERY REQ YES) by the long top line.
- H25 "ABC FROM TAG ON ?" -- YES -> H27 "STORE OR INT. FETCH ?" -- YES (line label "LAAR BUSY") -> R33 "RESET LAAR BUSY" (38.53.03.1).

###### Phase M
- H28 "NOOP MODE ?" -- YES -> R35; NO -> H29.
- H29 "A BUS TIMER ACTION RQD ?" -- NO -> H30. YES: not drawn.
- H30 "BRANCH REC RQD ?" -- YES -> R34 "IND TEST E WILL RESET THE BR RQMNTS" (38.24.03.1); NO -> R35.
- R35 "ADV. ABC IF NOT INTLKD BY TBC" (38.31.05.1)

###### Phase E + M
- H31 "NOOP MODE ?" -- NO -> off-page "STORES".

Right margin: brace over "STORES" and "FETCHES", "TO A BUS TIMER".

##### 2. Structure

- Main sequencer: TRANSFER INDICATOR TIMER (phases E.M̄, E.M, M, E + M). TON/TOF not printed here.
- Second sequencer: "START I BOX HSCLN TIMER" bar with phases E and M. TON: "SET "I BOX RQST HSCLN" TRIGGER" after "BR SUCC & NO COND INDS" (branch successful, no conditional indicators). TOF: not printed. Its M phase sets LA "HSCLN MODE" and then, if the LA is empty, starts the LA HSCLN OVER TIMER; otherwise resets the I BOX HSCLN TIMER.
- (DERIVED) This page is the branch-recovery path: a successful branch that the LA had not followed (BR RECOVERY with LAOP 45, 47) makes the I-box request a houseclean of the look-ahead.

##### 3. Step table

| phase | condition(s) (PRINTED) | action(s) (PRINTED) | ALD | notes |
|---|---|---|---|---|
| E.M̄ | -- | RESET ABC AES; GI X̄R̄ INDS TO IND. REQ | 38.31.03.1; 35.27.03.1 | |
| E.M̄ | LAOP 31,57 ? YES | RESET TBC AES; ADV. TBC IF NOT INTLKD BY OCC | 38.01.03.1; -- | **[KEY]** interlock |
| E.M̄ | NOOP ABC ? YES | SET NOOP MODE | 38.34.01.1 | |
| E.M̄ | LAOP 31 ? YES | RESET LF TAG | 36.01.09.1 | |
| E.M̄ | LAOP 11 YES; RECOVERY REQ YES | RESET MAR MODE; RESET "MSTR TEST COMPLT" TRIG IN PAU (-> ALLOW PAU TO RE-MEMORIZE THE INTRPT LINE); -> BR SUCC & NO COND INDS | 38.35.04.1; 38.23.02.1 | **[KEY]** recovery |
| E.M̄ | LAST INSTR. LEVEL ? YES (IC ON) | GI IC FIELD TO IC BUFFER; RESET MAR MODE | 35.27.02.1; 38.35.04.1 | |
| E.M̄ | NOT SIC BIN RECOVERY LEVEL; NOOP OR NOOP MODE NO; LAOP 45 ? YES | -> BR SUCC & NO COND INDS | -- | |
| E.M̄ | NOOP OR NOOP MODE YES, or ABC STORE ACTION RQD. ? (left exit) | NO DELAY IND. TEST; SET IND. TEST E | 38.32.09.1; 38.38.03.1 | |
| E.M̄ | after SET IND. TEST E | RESET RQST CYCLE STORE MEM TRIGGER; RESET BR SUCC AND COND IND TRIGGERS | 38.24.02.1; 38.24.03.1 | |
| E.M̄ | BR SUCC & NO COND INDS YES | RESET LF TAG; SET BR RECOVERY INHB LOAD TRIGGER; SET "I BOX RQST HSCLN" TRIGGER | 36.01.09.1; --; 38.39.05.1 | **[KEY]** |
| I BOX HSCLN TIMER E | -- | RESET I BOX RQST HSCLN TRIGGER | -- | **[KEY]** |
| I BOX HSCLN TIMER M | -- | SET LA "HSCLN MODE" TRIGGER | 38.39.04.1 | **[KEY]** |
| I BOX HSCLN TIMER M | IS LA EMPTY ? YES | START LA HSCLN OVER TIMER | 38.39.01.1 | **[KEY]** |
| I BOX HSCLN TIMER M | IS LA EMPTY ? (other exit) | RESET "I BOX HSCLN TIMER" | 38.0.07.1 | **[KEY]** |
| E.M̄ (end) | NOOP MODE ? YES | SET LA NOOP IND TEST M; SIGNAL PAU TO SET "MSTR TEST COMPLT" | 38.35.03.1; 38.23.01.1 | |
| E.M̄ (end) | NOOP MODE ? NO | SET NORMAL IND TEST M; SIGNAL PAU TO LA TESTS COMPLT | 38.35.01.1; 38.23.01.1 | |
| E.M | 1st INSTR.LEVEL ? (MAR NEXT INSTR) | RESET MAR NEXT INSTR TRIGGER | 38.35.04.1 | |
| E.M | LAOP 75 ? NO; IS THIS THEINTRPT FREE INSTR. ? (INTRPT DISABLED) | RESET "DISABLE INTRPT" TRIGGERS | 38.39.05.1 | |
| E.M | -- | RESET UNIPOLAR INDS | 35.27.07.1 | |
| E.M | BR. RECOVERY ? YES (45, 47); SUCC BRANCH ? YES; COND INDS ? YES | GI SAU'S COND INDS TO IND REQ.; -> SIC BIN (left) | 35.27.05.1 | **[KEY]** |
| E.M | BR. RECOVERY YES; SUCC BRANCH ? NO (or COND INDS YES); SIC BIN YES (IC OFF) | SIGNAL I BOX OF NO BRANCH | 38.38.02.1 (placement ambiguous) | **[KEY]** |
| E.M | COND INDS ? NO; GOOD RECOVERY LEVEL NO (47) | GI CNIDC TO MK IND. | 35.27.03.1 | |
| E.M | COND INDS ? NO; SIC BIN (right) YES (IC OFF) | SIGNAL I BOX OF BRANCH | 38.38.02.1 (placement ambiguous) | **[KEY]** |
| E.M | NOOP MODE ? YES | GI CNIDC TO MK IND. | 35.27.03.1 | |
| E.M | NOOP MODE YES (NON-ARITH INSTR.); LAST INSTR. LEVEL ? YES (ICON) | RESET "MSTR TEST COMPLT" TRIG IN PAU; ALLOW PAU TO RE-MEMORIZE THE INTRPT LINE | 38.23.02.1 | |
| E.M | NOOP MODE YES; ABC FROM TAG ON ? YES; STORE OR INT. FETCH ? YES (LAAR BUSY) | RESET LAAR BUSY | 38.53.03.1 | **[KEY]** |
| E.M | NOOP MODE ? NO; INT. FETCH ? YES (INT. TAG ON) | -> FETCHES (TO A BUS TIMER) | -- | |
| M | NOOP MODE ? NO; A BUS TIMER ACTION RQD ? NO; BRANCH REC RQD ? YES | IND TEST E WILL RESET THE BR RQMNTS | 38.24.03.1 | |
| M | NOOP MODE ? YES, or BRANCH REC RQD ? NO | ADV. ABC IF NOT INTLKD BY TBC | 38.31.05.1 | **[KEY]** interlock |
| E + M | NOOP MODE ? NO | -> STORES (TO A BUS TIMER) | -- | |

##### 4. Counters, timers, triggers, registers, LAOP

- Counters: ABC, TBC, OCC ("ADV. TBC IF NOT INTLKD BY OCC"; "ADV. ABC IF NOT INTLKD BY TBC").
- Timers: TRANSFER INDICATOR TIMER; I BOX HSCLN TIMER ("START I BOX HSCLN TIMER", phases E, M; "RESET "I BOX HSCLN TIMER""); LA HSCLN OVER TIMER; A BUS TIMER.
- Triggers/modes: ABC AES; TBC AES; NOOP ABC; NOOP MODE; LF TAG; MAR MODE; MAR NEXT INSTR; "DISABLE INTRPT"; IND TEST E; LA NOOP IND TEST M; NORMAL IND TEST M; "MSTR TEST COMPLT" (PAU); RQST CYCLE STORE MEM TRIGGER; BR SUCC and COND IND TRIGGERS; BR RECOVERY INHB LOAD TRIGGER; "I BOX RQST HSCLN" TRIGGER; LA "HSCLN MODE" TRIGGER; LAAR BUSY; INT. TAG; IC ON / IC OFF; SIC BIN; BR. RECOVERY; RECOVERY REQ; BRANCH REC RQD.
- Registers: IND REQ (sic, IND REG); IC BUFFER; MK IND.; SAU's COND INDS; CNIDC (not expanded); XR INDS; UNIPOLAR INDS; LAAR.
- LAOP codes in conditions: 31,57; 31; 11; 45; 75; line label "45, 47"; "47".

##### 5. TIME

PRINTS NO TIME. Phase letters only (E.M̄, E.M, M, E + M on the transfer indicator timer; E, M on the I BOX HSCLN TIMER).

##### 6. [KEY] items

- **[KEY]** Branch recovery / houseclean: "BR. RECOVERY ?" YES "45, 47" -> "SUCC BRANCH ?" -> "COND INDS ?" -> "GOOD RECOVERY LEVEL" NO "47" -> "GI CNIDC TO MK IND." (35.27.03.1); "SIC BIN" YES "IC OFF" -> "SIGNAL I BOX OF NO BRANCH" / "SIGNAL I BOX OF BRANCH" (38.38.02.1).
- **[KEY]** "LAOP 11" YES -> "RECOVERY REQ" YES -> "RESET MAR MODE", "RESET "MSTR TEST COMPLT" TRIG IN PAU", and "BR SUCC & NO COND INDS".
- **[KEY]** "NOT SIC BIN RECOVERY LEVEL" (line label) -> "NOOP OR NOOP MODE" NO -> "LAOP 45 ?" YES.
- **[KEY]** "BR SUCC & NO COND INDS" YES -> "RESET LF TAG" (36.01.09.1), "SET BR RECOVERY INHB LOAD TRIGGER", "SET "I BOX RQST HSCLN" TRIGGER" (38.39.05.1) -> "START I BOX HSCLN TIMER": E "RESET I BOX RQST HSCLN TRIGGER"; M "SET LA "HSCLN MODE" TRIGGER" (38.39.04.1) -> "IS LA EMPTY ?" YES "START LA HSCLN OVER TIMER" (38.39.01.1); other "RESET "I BOX HSCLN TIMER"" (38.0.07.1).
- **[KEY]** "RESET RQST CYCLE STORE MEM TRIGGER" (38.24.02.1); "RESET BR SUCC AND COND IND TRIGGERS" (38.24.03.1); "IND TEST E WILL RESET THE BR RQMNTS" (38.24.03.1) under "BRANCH REC RQD ?" YES.
- **[KEY]** Interlocks: "ADV. TBC IF NOT INTLKD BY OCC" (after "LAOP 31,57 ?" YES, "RESET TBC AES" 38.01.03.1); "ADV. ABC IF NOT INTLKD BY TBC" (38.31.05.1).
- **[KEY]** LAAR BUSY: "STORE OR INT. FETCH ?" YES "LAAR BUSY" -> "RESET LAAR BUSY" (38.53.03.1).
- **[KEY]** NOOP: "NOOP ABC ?" YES "SET NOOP MODE" (38.34.01.1); "NOOP MODE ?" YES "SET LA NOOP IND TEST M" (38.35.03.1); "NON-ARITH INSTR."
- **[KEY]** LAST INSTR: "LAST INSTR. LEVEL ?" YES "IC ON" / "ICON".

##### 7. Could not read / ambiguities

- Nothing illegible.
- ALD print variants vs sister pages: RESET TBC AES is 38.01.03.1 here, 38.21.03.1 on Figs 3.2.19-3.2.21.
- "38.38.02.1": placed between "SIGNAL I BOX OF NO BRANCH" and "SIGNAL I BOX OF BRANCH"; ownership ambiguous.
- "38.0.07.1" printed with only three groups (likely a misprint).
- "CNIDC" printed as such (DERIVED: possibly a misprint; not expanded).
- Exit flows at J1 are read from arrowheads; the RECOVERY REQ YES -> RESET MAR MODE and -> RESET "MSTR TEST COMPLT" connections are DERIVED from line tracing (no labels on those lines).
- Many exits not drawn (listed per box).

#### Figure 3.2.19 I BOX AND I/O ABC ACTIONS-TRANSFER INDICATOR TIMER

- Title as printed: "FIGURE 3.2.19. I BOX AND I/O ABC ACTIONS-TRANSFER INDICATOR TIMER"
- PDF page 111 (landscape fold-out; 300 dpi tiles, 400 dpi and 600 dpi checks)
- Header: "M3-04-3" / "LA FLOW DIAGRAMS"
- Printed page at foot: 2-25/2-26
- Issue date at foot: 2/1/62 (first digit clipped by the fold line, reads "2/1/62")
- No "CPU 7101 SER. NO." applicability note.
- Fold line at x~3830 px (300 dpi) crosses LAOP 51 ?, NOOP MODE ? (E.M), RESET "LAAR BUSY", SET ABC NOOP TAG; all readable.

##### 1. Boxes (PRINTED, verbatim; ALD in parentheses)

Timer bar: "TRANSFER INDICATOR TIMER". Phase lines: "E.M̄", "E.M", "M". (No "E + M" phase line on this page.)

###### Phase E.M̄
- R1 "RESET ABC AES" (38.31.03.1)
- H1 "LAOP 02,04,33,63 ?" -- YES -> H2. NO: not drawn.
- H2 "NOOP'D OR NOOP MODE ?" -- NO -> R2 "GI XR INDS TO IND REQ." (35.27.04.1) (no overbar on XR here). YES: not drawn.
- H3 "LAOP 02,04" (no "?") -- YES -> H4 and H5. NO: not drawn.
- H4 "NOOP'D ?" -- YES -> H6. NO: not drawn.
- H6 "02" -- YES -> R3.
- H5 "NOOP MODE ?" -- YES -> R3.
- H7 "LAOP 33 EXT. ?" -- YES -> H8.
- H8 "NOOP'D OR NOOP MODE" (no "?") -- NO -> R3.
- H9 "06" -- YES -> R3.
- R3 "RESET ABC LF TAG" (36.01.09.1)
- R4 "GI X̄R̄ INDS TO IND REQ." (35.27.03.1) (overbar on XR)
- H10 "LAOP 00,02,25, 63,65,33 EXT. ?" -- YES -> H11.
- H11 "NOOP'D OR NOOP MODE ?" -- NO -> R5 "RESET TBC AES" (38.21.03.1) -> R6 "ADV. TBC, IF NOT INTLKD BY OCC" (no ALD).
- H12 "NOOP ABC" (no "?") -- YES -> R7 "SET NOOP MODE" (38.34.01.1).
- H13 "LAOP 11" -- YES -> H14 "NOOP RECOVERY REQ" -- YES -> J1 (vertical into R12).
- H15 "LAST INSTR. LEVEL ?" -- YES (line label "IC ON") -> (a) right to H16; (b) down the left column: R8 "GI IC FIELD TO IC BUFFER" (35.27.02.1), with a branch right to H17; R9 "RESET MAR MODE" (38.35.04.1); then H18.
- H16 "02,04,33,63 ?" -- YES -> H19 "NOOP'D OR NOOP MODE ?" -- YES -> J1.
- H17 "06 ?" -- YES -> J1.
- J1 -> R12 "SET "PSEUDO INTRPT INHIBIT LOAD" TRIGGER" (38.39.03.1); from J1 a line also runs right to R13.
- R13 "SET "I BOX RQST HSCLN" TRIGGER" (38.39.05.1) -- line label "(I BOX)" beside its exit -> bar "START I BOX HSCLN TIMER", phases "E" and "M":
  - E -> R14 "RESET "I BOX RQST HSCLN" TRIGGER" (no ALD)
  - M -> R15 "SET LA "HSCLN MODE" TRIGGER" (38.39.04.1) -> H20 "IS LA EMPTY ?" -- YES -> R16 "START LA HSCLN OVER TIMER" (38.39.01.1). Other exit: not drawn.
- H18 "NOOP'D OR NOOP MODE ?" -- YES -> R17; NO -> H21.
- H21 "AEC STORE ACTION RQD. ?" ("AEC" as printed; DERIVED: ABC) -- NO -> R17. YES: not drawn.
- R17 "NO DELAY IND TEST" (38.32.09.1) -> R18 "SET IND. TEST E" (38.38.03.1) -> R19 "RESET "LAST CYCLE STORE" AND STORE INHIBIT TRIGGERS" (38.24.02.1), and -> H22.
- H22 "NOOP MODE ?" -- YES -> R20; NO -> H23.
- H23 "NON-ARITH INSTR. ?" -- YES (line label ""LA ONLY MAR NEXT"") -> R20; NO -> R22.
- R20 "SET LA NOOP IND TEST M" (38.35.03.1) -> R21 "SIGNAL PAU TO SET "MSTR TEST COMPLT"" (38.23.01.1)
- R22 "SET NORMAL IND. TEST M" (38.35.01.1) -> R23 "SIGNAL PAU OF LA TESTS COMPLETE" (38.23.01.1)

###### Phase E.M
- H24 "1st INSTR LEVEL" (no "?") -- YES (line label ""MAR NEXT INSTR" ON") -> R24 "RESET "MAR NEXT INSTR"" (38.35.04.1) and H25.
- H25 "IS THIS THE INTRPT FREE INSTR ?" -- YES (line label "INTRPT IS DISABLED") -> R25 "RESET "DISABLE INTRPT" TRIGGER" (38.39.05.1).
- R26 "RESET UNIPOLAR IND'S" (35.27.07.1)
- Fork: H26 "06 ?" -- YES -> R27 "GI CNIDC TO MK IND." (35.27.03.1). H27 "INT FETCH ?" -- YES (line label "INT TAG ON") -> off-page "FETCHES".
- Fork: H28 "33 EXT. ?" -- YES -> H29 "NOOP'D OR NOOP MODE" -- NO -> H30 "IN ECC ?" (printed "IN   ECC ?") -- NO -> R28 "RESET "STORE CHK IND TEST M"" (38.35.02.1).
- H31 "NOOP MODE ?" -- YES -> line labelled "NON ARITH" -> H32 and H34; NO -> H33.
- H33 "NON-ARITH INSTR. ?" -- YES -> joins the NON ARITH line into H34.
- H32 "ABC FROM TAG ON ?" -- YES -> H35 "STORE OR INT. FETCH ?" -- YES (line label "LAAR BUSY") -> H36 ".51" (printed with a leading dot) -- NO -> R29 "RESET "LAAR BUSY"" (38.58.03.1) and R30 "SET ABC NOOP TAG" (36.07.03.1).
- H34 "LAST INSTR LEVEL ?" -- YES (line label "IC ON") -> R31 "RESET "MSTR TEST COMPLT" TRIG IN PAU" (38.23.02.1) -> R32 "ALLOW PAU TO RE-MEMORIZE THE INTRPT LINE" (no ALD).

###### Phase M
- H37 "NOOP MODE ?" -- YES -> H38; NO -> H39.
- H38 "LAOP 51 ?" -- NO -> R33.
- H39 "INT FETCH ?" -- NO -> H40. YES: not drawn.
- H40 "LAOP 33 INT. ?" -- NO -> R33; YES -> H41.
- R33 "ADV. ABC IF NOT INTLKD BY TBC" (38.31.05.1)
- H41 "ABC- TBC INTLKD ?" -- YES -> H42.
- H42 "TB TIMER M ?" -- YES -> off-page "STORES". Text under it: "TO A BUS TIMER".

###### Legend (PRINTED, bottom right, verbatim; ditto marks as printed; read at 600 dpi)
```
   OP 20 IO BX
    "  24  "  DISC
LAOP 25  "  DUMMY NOT CCW
     65  "      "     CCW
     02  I BOX PSEUDO STORE
     33    "    REAL STORE
     51    "    INT. FETCH
     04  PX PSEUDO STORE
     06   "     "        "   NOOP'D
     63  INDICATOR ONLY
     00  TEST LEVEL
     11  RAC RCY (NOOP RCY REQ)
```
Note: the first word of the last line reads "RAC" at 600 dpi (first letter has the shape of R, matching the R of "RCY"); a reading "BAC" cannot be excluded on print quality alone. "OP" heads 20 and (ditto) 24; "LAOP" heads 25 and the rest.

##### 2. Structure

- Sequencer: TRANSFER INDICATOR TIMER, phases E.M̄, E.M, M (no E + M on this page; stores go out from phase M via "TB TIMER M ?" instead).
- Second sequencer: "START I BOX HSCLN TIMER" (phases E, M), TON by "SET "I BOX RQST HSCLN" TRIGGER" (38.39.05.1), reached from J1 (NOOP RECOVERY REQ YES; or last-instruction-level LAOP 02,04,33,63 NOOP'D-or-NOOP-MODE; or LAOP 06). TOF not printed.
- (DERIVED) Per legend: LAOP 02 = I-box pseudo store, 33 = I-box real store, 51 = I-box internal fetch, 04 = PX pseudo store, 06 = PX pseudo store NOOP'D, 63 = indicator only, 00 = test level, 11 = recovery (NOOP recovery request).

##### 3. Step table

| phase | condition(s) (PRINTED) | action(s) (PRINTED) | ALD | notes |
|---|---|---|---|---|
| E.M̄ | -- | RESET ABC AES | 38.31.03.1 | |
| E.M̄ | LAOP 02,04,33,63 ? YES; NOOP'D OR NOOP MODE ? NO | GI XR INDS TO IND REQ. | 35.27.04.1 | |
| E.M̄ | LAOP 02,04 YES and (NOOP'D ? YES and 02 YES, or NOOP MODE ? YES); or LAOP 33 EXT. ? YES and NOOP'D OR NOOP MODE NO; or 06 YES | RESET ABC LF TAG | 36.01.09.1 | **[KEY]** pseudo store |
| E.M̄ | -- | GI X̄R̄ INDS TO IND REQ. | 35.27.03.1 | |
| E.M̄ | LAOP 00,02,25,63,65,33 EXT. ? YES; NOOP'D OR NOOP MODE ? NO | RESET TBC AES; ADV. TBC, IF NOT INTLKD BY OCC | 38.21.03.1; -- | **[KEY]** interlock |
| E.M̄ | NOOP ABC YES | SET NOOP MODE | 38.34.01.1 | |
| E.M̄ | LAOP 11 YES; NOOP RECOVERY REQ YES | SET "PSEUDO INTRPT INHIBIT LOAD" TRIGGER; SET "I BOX RQST HSCLN" TRIGGER | 38.39.03.1; 38.39.05.1 | **[KEY]** |
| E.M̄ | LAST INSTR. LEVEL ? YES (IC ON); 02,04,33,63 ? YES; NOOP'D OR NOOP MODE ? YES | same as above | 38.39.03.1; 38.39.05.1 | **[KEY]** |
| E.M̄ | LAST INSTR. LEVEL YES; 06 ? YES | same as above | | **[KEY]** |
| E.M̄ | LAST INSTR. LEVEL YES | GI IC FIELD TO IC BUFFER; RESET MAR MODE | 35.27.02.1; 38.35.04.1 | |
| I BOX HSCLN TIMER E | -- | RESET "I BOX RQST HSCLN" TRIGGER | -- | |
| I BOX HSCLN TIMER M | -- | SET LA "HSCLN MODE" TRIGGER | 38.39.04.1 | |
| I BOX HSCLN TIMER M | IS LA EMPTY ? YES | START LA HSCLN OVER TIMER | 38.39.01.1 | |
| E.M̄ | NOOP'D OR NOOP MODE ? YES, or AEC STORE ACTION RQD. ? NO | NO DELAY IND TEST; SET IND. TEST E; RESET "LAST CYCLE STORE" AND STORE INHIBIT TRIGGERS | 38.32.09.1; 38.38.03.1; 38.24.02.1 | **[KEY]** |
| E.M̄ | NOOP MODE ? YES, or NON-ARITH INSTR. ? YES ("LA ONLY MAR NEXT") | SET LA NOOP IND TEST M; SIGNAL PAU TO SET "MSTR TEST COMPLT" | 38.35.03.1; 38.23.01.1 | |
| E.M̄ | NOOP MODE NO; NON-ARITH INSTR. ? NO | SET NORMAL IND. TEST M; SIGNAL PAU OF LA TESTS COMPLETE | 38.35.01.1; 38.23.01.1 | |
| E.M | 1st INSTR LEVEL YES ("MAR NEXT INSTR" ON) | RESET "MAR NEXT INSTR" | 38.35.04.1 | |
| E.M | IS THIS THE INTRPT FREE INSTR ? YES (INTRPT IS DISABLED) | RESET "DISABLE INTRPT" TRIGGER | 38.39.05.1 | |
| E.M | -- | RESET UNIPOLAR IND'S | 35.27.07.1 | |
| E.M | 06 ? YES | GI CNIDC TO MK IND. | 35.27.03.1 | |
| E.M | INT FETCH ? YES (INT TAG ON) | -> FETCHES | -- | |
| E.M | 33 EXT. ? YES; NOOP'D OR NOOP MODE NO; IN ECC ? NO | RESET "STORE CHK IND TEST M" | 38.35.02.1 | |
| E.M | NOOP MODE ? YES (NON ARITH); ABC FROM TAG ON ? YES; STORE OR INT. FETCH ? YES (LAAR BUSY); .51 NO | RESET "LAAR BUSY"; SET ABC NOOP TAG | 38.58.03.1; 36.07.03.1 | **[KEY]** |
| E.M | (NOOP MODE YES or NON-ARITH INSTR. ? YES); LAST INSTR LEVEL ? YES (IC ON) | RESET "MSTR TEST COMPLT" TRIG IN PAU; ALLOW PAU TO RE-MEMORIZE THE INTRPT LINE | 38.23.02.1; -- | |
| M | NOOP MODE ? YES and LAOP 51 ? NO; or NOOP MODE NO, INT FETCH ? NO, LAOP 33 INT. ? NO | ADV. ABC IF NOT INTLKD BY TBC | 38.31.05.1 | **[KEY]** interlock |
| M | NOOP MODE NO; INT FETCH NO; LAOP 33 INT. ? YES; ABC- TBC INTLKD ? YES; TB TIMER M ? YES | -> STORES (TO A BUS TIMER) | -- | **[KEY]** interlock |

##### 4. Counters, timers, triggers, registers, LAOP

- Counters: ABC, TBC, OCC ("ADV. TBC, IF NOT INTLKD BY OCC"; "ADV. ABC IF NOT INTLKD BY TBC"; "ABC- TBC INTLKD ?").
- Timers: TRANSFER INDICATOR TIMER; I BOX HSCLN TIMER (phases E, M); LA HSCLN OVER TIMER; TB TIMER (phase M tested: "TB TIMER M ?"); A BUS TIMER.
- Triggers/modes: ABC AES; TBC AES; ABC LF TAG; NOOP'D; NOOP MODE; NOOP ABC; ABC NOOP TAG; NOOP RECOVERY REQ; "PSEUDO INTRPT INHIBIT LOAD"; "I BOX RQST HSCLN"; LA "HSCLN MODE"; "LAST CYCLE STORE" and STORE INHIBIT TRIGGERS; MAR MODE; "MAR NEXT INSTR"; "DISABLE INTRPT"; IND. TEST E; LA NOOP IND TEST M; NORMAL IND. TEST M; "MSTR TEST COMPLT" (PAU); "STORE CHK IND TEST M"; "LAAR BUSY"; INT TAG; IC ON; IN ECC; "LA ONLY MAR NEXT".
- Registers: IND REQ (sic, IND REG); IC BUFFER; MK IND.; CNIDC; XR INDS; UNIPOLAR IND'S; LAAR.
- LAOP codes in boxes: 02,04,33,63; 02,04; 02; 33 EXT.; 06; 00,02,25,63,65,33 EXT.; 11; 51; 33 INT.; .51. Legend: OP 20, 24; LAOP 25, 65, 02, 33, 51, 04, 06, 63, 00, 11.

##### 5. TIME

PRINTS NO TIME. Phase letters only; "TB TIMER M ?" names a phase of the TB timer, not a time.

##### 6. [KEY] items

- **[KEY]** PSEUDO vs REAL STORE (legend): "02 I BOX PSEUDO STORE", "33 " REAL STORE", "04 PX PSEUDO STORE", "06 " " " NOOP'D", "51 " INT. FETCH".
- **[KEY]** "SET "PSEUDO INTRPT INHIBIT LOAD" TRIGGER" (38.39.03.1) and "SET "I BOX RQST HSCLN" TRIGGER" (38.39.05.1) on "LAOP 11" YES -> "NOOP RECOVERY REQ" YES, or at last instruction level for "02,04,33,63 ?" with "NOOP'D OR NOOP MODE ?" YES, or "06 ?" YES.
- **[KEY]** Houseclean: "(I BOX)" "START I BOX HSCLN TIMER" E: "RESET "I BOX RQST HSCLN" TRIGGER"; M: "SET LA "HSCLN MODE" TRIGGER" (38.39.04.1) -> "IS LA EMPTY ?" YES -> "START LA HSCLN OVER TIMER" (38.39.01.1).
- **[KEY]** "RESET "LAST CYCLE STORE" AND STORE INHIBIT TRIGGERS" (38.24.02.1) after "SET IND. TEST E".
- **[KEY]** ""LA ONLY MAR NEXT"" (YES exit of "NON-ARITH INSTR. ?") -> "SET LA NOOP IND TEST M".
- **[KEY]** LAAR BUSY: "STORE OR INT. FETCH ?" YES "LAAR BUSY" -> ".51" NO -> "RESET "LAAR BUSY"" (38.58.03.1) and "SET ABC NOOP TAG" (36.07.03.1).
- **[KEY]** Interlocks: "ADV. TBC, IF NOT INTLKD BY OCC"; "ADV. ABC IF NOT INTLKD BY TBC" (38.31.05.1); "ABC- TBC INTLKD ?" YES -> "TB TIMER M ?" YES -> "STORES".
- **[KEY]** "IN ECC ?" NO -> "RESET "STORE CHK IND TEST M"" (38.35.02.1).
- **[KEY]** Legend line "11 RAC RCY (NOOP RCY REQ)" (recovery request).

##### 7. Could not read / ambiguities

- Nothing illegible.
- Legend "RAC" vs "BAC": reads RAC; noted above.
- ".51" is printed with a leading dot (may be a speck).
- "AEC STORE ACTION RQD." printed AEC.
- ALD 38.58.03.1 for RESET "LAAR BUSY" here, versus 38.53.03.1 on Figs 3.2.16-3.2.18; first digit partly under the fold line, read as 38.58.03.1.
- ALD 38.21.03.1 for RESET TBC AES here, versus 38.01.03.1 on Fig 3.2.18.
- IS LA EMPTY ? other exit not drawn here (Fig 3.2.18 draws it to RESET "I BOX HSCLN TIMER").

#### Figure 3.2.20 INTERNAL FETCH ABC ACTIONS-ARITHMETIC BUS TIMER

- Title as printed: "FIGURE 3.2.20. INTERNAL FETCH ABC ACTIONS-ARITHMETIC BUS TIMER"
- PDF page 112. The scan is a landscape fold-out frame, but the printed page occupies only the LEFT half; the right half is blank. Read at 400 dpi.
- Header: "M3-04-3" / "LA FLOW DIAGRAMS"
- Printed page at foot: 2-27 (single page; no 2-28 printed)
- Issue date at foot: 2/1/62
- No "CPU 7101 SER. NO." applicability note.

##### 1. Boxes (PRINTED, verbatim; ALD in parentheses)

Entry: off-page connector "INT. FETCH" (drawn with a wavy-tailed arrow) -> forks to H1 and to the timer bar.

- H1 "LAOP 37 ?" -- YES -> R1 "SIGNAL IND. REQ TO RESET 0-19 ASYNCHRONOUS INDS, IMMEDIATELY AFTER FETCHES" (35.27.04.1). NO: not drawn.
- Timer bar "ARITH BUS TIMER" (38.33.01.1, printed just above the bar at the entry arrow). Inside the bar are printed the phase marks "EE" (left end), "E" (centre), "M" (right end). Phase lines dropping from it, left to right: "EE", "E.M̄" (overbar on M), "M", "E.M".

Phase EE:
- R2 "SEND "PASS DATA" SIGNAL TO A CHKR" (38.23.03.1)
- R3 "GO INT. ADDRESS SPECIFIED BY LAAR ONTO ACIB" (35.24.04.1 / .05.1 / .06.1 -- printed as three stacked refs)

Phase E.M̄:
- R4 "RESET TRANS. IND. TIMER M" (38.38.02.1)
- R5 "RESET TBC AES" (38.21.03.1)
- R6 "ADV. TBC IF INTLKD WITH ABC IF NOT INTLKD BY OCC" (no ALD)
- H2 "LAAR AT ADD. 7 OR 11 ?" -- NO -> R7 "SIGNAL A CHKR TO CHK PARITY"; YES -> R8 "SIGNAL A CHKR NOT TO CHK PARITY". One ALD "38.23.03.1" printed between/under R7 and R8.

Phase M:
- R9 "ADV. ABC IF NOT INTLKD BY TBC" (38.31.05.1)

Phase E.M:
- R10 "RESET LAAR BUSY TRIGGER" (38.53.03.1)
- H3 "LAOP 51 ?" -- YES -> R11 "RESET LF TAG TO SIGNAL FOR SCC ACTION" (36.01.09.1) and R12 "GI ACOB INTO ABC LEVEL" (35.23.02.1). NO: not drawn.
- H4 "LAOP 07 ?" (fed from the E.M line ahead of H3) -- NO -> R13 "GI ACOB TO C REG"; YES -> R14 "GI ACOB TO D REG". One ALD "35.22.01.1" printed between R13 and R14.
- Branch at the top of E.M -> H5 "FP INSTR. ?" -- YES (line label "X2") -> R15 "SEND "START" SIGNALS TO SAU & PAU" (38.23.01.1); NO -> H6.
- H6 "LAST OPERAND ?" -- YES (line label, stacked: "05 / 07 / 37") -> R16 and (right, down) H8. NO: not drawn.
- R16 "SET "SAU GO" TRIGGER" (38.23.04.1) -> R17 "SEND "GO" SIGNAL TO SAU" (no ALD) -> H7.
- H7 "SAU STARTED EXECUTION ?" -- YES (line label ""SAU HSKPING" OVER") -> R18 "RESET "SAU GO" TRIGGER" (38.23.04.1).
- H8 "LAOP 37" (no "?") -- YES -> R19 "RESET 0-19 SYNCHRONOUS IND'S IN IND. REQ." (35.27.04.1) and R20 "RESET SAU'S ERROR TRIGGER" (35.27.04.1).

Legend (PRINTED, bottom left, verbatim; ditto marks as printed):
```
  OP  X2  FP   FETCH
LAOP  05  VFL   "    (1 OF 1)
  "   03   "    "    (1 OF 2)
  "   07   "    "    (2 OF 2)
  "   37  BI    "
  "   51  I BOX "
```

##### 2. Structure

- Sequencer: ARITH BUS TIMER (38.33.01.1). TON: "INT. FETCH" (off-page entry; DERIVED: the FETCHES exit of Figs 3.2.16-3.2.19). TOF: not printed. Phases: EE, E.M̄, M, E.M.
- (DERIVED) For an internal (operand) fetch the ABC, at the arithmetic bus timer: EE gates the internal address from the LAAR onto the ACIB and tells the A checker to pass the data; E.M̄ resets the transfer indicator timer M and advances TBC; M advances ABC; E.M resets LAAR BUSY and steers the ACOB data (ACOB not expanded on the page) to the C or D register (VFL), or to the ABC level (I-box LAOP 51), and starts SAU & PAU (FP) or SAU (VFL last operand).

##### 3. Step table

| phase | condition(s) (PRINTED) | action(s) (PRINTED) | ALD | notes |
|---|---|---|---|---|
| entry | LAOP 37 ? YES | SIGNAL IND. REQ TO RESET 0-19 ASYNCHRONOUS INDS, IMMEDIATELY AFTER FETCHES | 35.27.04.1 | |
| EE | -- | SEND "PASS DATA" SIGNAL TO A CHKR | 38.23.03.1 | |
| EE | -- | GO INT. ADDRESS SPECIFIED BY LAAR ONTO ACIB | 35.24.04.1, .05.1, .06.1 | **[KEY]** LAAR |
| E.M̄ | -- | RESET TRANS. IND. TIMER M | 38.38.02.1 | |
| E.M̄ | -- | RESET TBC AES | 38.21.03.1 | |
| E.M̄ | -- | ADV. TBC IF INTLKD WITH ABC IF NOT INTLKD BY OCC | -- | **[KEY]** interlock |
| E.M̄ | LAAR AT ADD. 7 OR 11 ? NO | SIGNAL A CHKR TO CHK PARITY | 38.23.03.1 | **[KEY]** |
| E.M̄ | LAAR AT ADD. 7 OR 11 ? YES | SIGNAL A CHKR NOT TO CHK PARITY | 38.23.03.1 | **[KEY]** |
| M | -- | ADV. ABC IF NOT INTLKD BY TBC | 38.31.05.1 | **[KEY]** interlock |
| E.M | -- | RESET LAAR BUSY TRIGGER | 38.53.03.1 | **[KEY]** |
| E.M | LAOP 51 ? YES | RESET LF TAG TO SIGNAL FOR SCC ACTION; GI ACOB INTO ABC LEVEL | 36.01.09.1; 35.23.02.1 | **[KEY]** SCC |
| E.M | LAOP 07 ? NO | GI ACOB TO C REG | 35.22.01.1 (shared) | |
| E.M | LAOP 07 ? YES | GI ACOB TO D REG | 35.22.01.1 (shared) | |
| E.M | FP INSTR. ? YES (X2) | SEND "START" SIGNALS TO SAU & PAU | 38.23.01.1 | |
| E.M | FP INSTR. ? NO; LAST OPERAND ? YES (05 07 37) | SET "SAU GO" TRIGGER; SEND "GO" SIGNAL TO SAU | 38.23.04.1; -- | |
| E.M | SAU STARTED EXECUTION ? YES ("SAU HSKPING" OVER) | RESET "SAU GO" TRIGGER | 38.23.04.1 | |
| E.M | LAST OPERAND YES; LAOP 37 YES | RESET 0-19 SYNCHRONOUS IND'S IN IND. REQ.; RESET SAU'S ERROR TRIGGER | 35.27.04.1; 35.27.04.1 | |

##### 4. Counters, timers, triggers, registers, LAOP

- Counters: ABC, TBC, OCC, SCC ("SIGNAL FOR SCC ACTION").
- Timers: ARITH BUS TIMER (38.33.01.1); TRANS. IND. TIMER M (reset).
- Triggers: TBC AES; LAAR BUSY TRIGGER; LF TAG; "SAU GO" TRIGGER; SAU'S ERROR TRIGGER; "SAU HSKPING".
- Registers/buses: LAAR; ACIB; ACOB; C REG; D REG; ABC LEVEL; IND. REQ (sic); A CHKR.
- Indicators: 0-19 ASYNCHRONOUS INDS; 0-19 SYNCHRONOUS IND'S.
- Units: SAU, PAU, A CHKR.
- LAOP codes: 37, 51, 07; line labels "X2", "05 07 37"; legend OP X2, LAOP 05, 03, 07, 37, 51.

##### 5. TIME

PRINTS NO TIME. Phase letters only (EE, E.M̄, M, E.M; bar marks EE, E, M).

##### 6. [KEY] items

- **[KEY]** "GO INT. ADDRESS SPECIFIED BY LAAR ONTO ACIB" (35.24.04.1 .05.1 .06.1), phase EE.
- **[KEY]** "LAAR AT ADD. 7 OR 11 ?" NO -> "SIGNAL A CHKR TO CHK PARITY"; YES -> "SIGNAL A CHKR NOT TO CHK PARITY" (38.23.03.1).
- **[KEY]** "RESET LAAR BUSY TRIGGER" (38.53.03.1), phase E.M.
- **[KEY]** Interlocks: "ADV. TBC IF INTLKD WITH ABC IF NOT INTLKD BY OCC"; "ADV. ABC IF NOT INTLKD BY TBC" (38.31.05.1).
- **[KEY]** "RESET LF TAG TO SIGNAL FOR SCC ACTION" (36.01.09.1) for "LAOP 51 ?" YES (I-box internal fetch), with "GI ACOB INTO ABC LEVEL" (35.23.02.1).
- **[KEY]** "SIGNAL IND. REQ TO RESET 0-19 ASYNCHRONOUS INDS, IMMEDIATELY AFTER FETCHES" (35.27.04.1) for "LAOP 37 ?" YES.
- **[KEY]** Legend: OP X2 FP FETCH; LAOP 05 VFL FETCH (1 OF 1); 03 VFL FETCH (1 OF 2); 07 VFL FETCH (2 OF 2); 37 BI FETCH; 51 I BOX FETCH.
- No forwarding of store data to a fetch is printed on this page.

##### 7. Could not read / ambiguities

- Nothing illegible.
- Shared ALD refs: "38.23.03.1" under R7/R8, "35.22.01.1" under R13/R14 (one ref printed for each pair).
- Right half of the PDF page is blank; there is no 2-28 content on PDF 112.

#### Figure 3.2.21 STORE ABC ACTIONS-ARITHMETIC BUS TIMER

- Title as printed: "FIGURE 3.2.21. STORE ABC ACTIONS- ARITHMETIC BUS TIMER"
- PDF page 113 (landscape fold-out; faint print; read at 400 dpi with contrast stretch, entry label checked at 600 dpi)
- Header: "M3-04-3" / "LA FLOW DIAGRAMS"
- Printed page at foot: 2-29/2-30
- Issue date at foot: 2/1/62
- No "CPU 7101 SER. NO." applicability note.
- Fold line at x~5100 px (400 dpi) crosses "WHAT IS BEING STORED", "ARC TBC INTLKD", "33 INT ?", "START IND REG TIMER"; all readable.

##### 1. Boxes (PRINTED, verbatim; ALD in parentheses)

###### Entries and timer bar
- Entry A (left): off-page connector "TRANS IND TIMER LAOP 33 INT" -> enters the left end of the bar at "38.33.01.1".
- Entry B (top centre): off-page connector "TRANS IND TIMER E + M" (the "+" is faint; read at 600 dpi) -> H1.
- H1 "WHAT IS BEING STORED ?" -- left exit labelled "C - D REG / 17, 23, 41" -> H2; right exit labelled "ACOB / X2, 13, 21" -> H3 and H4.
- H2 "IS STORE DATA READY ?" (left) -- YES (line label ""LAST CYCLE STORE MEM" ON") -> enters the bar at the mark "EE".
- H3 "IS STORE DATA READY ?" (right) -- YES (line label ""LAST CYCLE STORE MEM" TRIG ON") -> enters the bar at "38.33.02.1".
- H4 "HAS A ZERO DIVISOR CANCELLED ANY REMAINDER THAT WAS TO BE STORED ?" -- YES (line label ""STORE INHIBIT MEM" TRIG ON") -> joins the H3 line into the bar at 38.33.02.1.
- Timer bar "ARITH BUS TIMER". Marks printed inside the bar: "EE" (centre-left, where H2 enters), "M" (right). ALD refs at the entry points: 38.33.01.1 (left end), 38.33.02.1 (H3/H4 entry).
- Phase lines below the bar, left to right: "EE", "E.M̄", "M", "E.M".

###### Phase EE
- R1 "SEND "PASS DATA" SIGNAL TO A CHKR" (38.23.03.1)
- H5 "WHERE IS DATA ?" -- left exit "C REG / 17, 41, 33 INT" -> R2 "GI C REG TO ACIB"; right exit "D REG / 23" -> R3 "GI D REG TO ACIB". Shared ALD "35.21.01.1" (last digit faint) printed between R2 and R3.

###### Phase E.M̄
- R4 "RESET "TRANS IND TIMER M"" (38.38.02.1)
- Fork to H6 and H7:
- H6 "LAST INSTR LEVEL ?" -- YES (line label "IC ON") -> R5. NO: not drawn.
- R5 "DELAY IND TEST" (38.32.09.1) -- NOTE: "DELAY", not "NO DELAY" as on Figs 3.2.16-3.2.19.
- R6 "SET IND TEST E" (38.38.03.1) -> R7 and H8.
- R7 "RESET: BR SUCC COND IND'S LAST CYCLE STORE, STORE INHIBIT TRIGGERS" (38.24.02.1, 38.24.03.1)
- H8 "NON-ARITH INSTR ?" -- YES -> R8 "SET LA NOOP IND TEST M" (38.35.03.1) -> R9 "SIGNAL PAU TO SET "MSTR TEST COMPLETE" TRIG" (38.23.01.1); NO -> R10 "SET NORMAL IND TEST M" (38.35.01.1) -> R11 "SIGNAL PAU OF LA TESTS CMPLT" (38.23.01.1).
- H7 "C+D STORE OP ?" (printed "C+D STORE OP ,") -- YES (line label, stacked "17 / 23 / 41 / 33 INT") -> R12 and H9.
- R12 "SIGNAL A CHKR TO CHK PARITY" (38.23.03.1)
- H9 "33 INT" (no "?") -- YES -> R13; NO (line label "17, 23, 41") -> H10 and R14.
- H10 "23 ?" -- YES -> R13. NO: not drawn.
- R13 "SIGNAL A CHECKER NOT TO SET ITS CHK CMPLT TGR" (no ALD)
- R14 "RESET TBC AES" (38.21.03.1) -> R15 "ADV TBC IF INTLKD WITH ABC, AND NOT INTLKD BY OCC" (38.23.03.1 printed under it)

###### Phase M
- H11 "GOOD INTERNAL STORE ?" -- NO -> R16; YES -> H12.
- H12 "ADDR 11 ?" -- NO -> R16; YES -> H13.
- H13 "BI STORE ?" -- YES (line label "LAOP41") -> R16. NO: not drawn.
- R16 "ADV ABC IF NOT INTLKD BY TBC" (38.31.05.1)
- H14 "33 INT ?" -- YES -> H15 "ARC TBC INTLKD ?" ("ARC" as printed; DERIVED: ABC) -- YES -> R17 "ADV TBC IF NOT INTLKD BY OCC" (no ALD).

###### Phase E.M
- H16 "ACOB STORE OP ?" -- YES (line label "X2,13,21") -> H17 "STORE DATA READY ?" -- YES (line label ""LAST CYCLE STORE MEM" ON") -> R18 "SIGNAL A CHKR THAT ACOB DATA IS ACCEPTED" (38.23.03.1).
- H18 "LAAR INT ?" -- YES -> line runs left: R19 "RESET LAAR BUSY TRIG" (38.23.03.1); H19 "BI STORE ?"; and into R20.
  - R20 "GI ACOB TO LAAR ADDER IF NOT ADDR 1, 5, or 6" (35.25.01.1 / .02.1 / .03.1) -> H20 "ADDR 8 ?" -- YES -> H21 "FP STORE ?" -- YES -> R21 "GI ACOB POS 60-63 TO SIGN BYTE REG POS 4-7" (35.25.02.1) (printed "GIACOEPOS 60-63"; DERIVED: GI ACOB POS).
  - H19 "BI STORE ?" -- exit (unlabelled as YES/NO; line label stacked "33 INT / X2 / 13 / 17 / 23") -> H22 "ADDR 11 ?" -- YES -> H23 "33 INT ?" -- YES -> R22; NO -> H24 "STORE DATA READY ?" -- YES (line label ""LAST CYCLE STORE MEM" ON") -> R22.
  - R22 "START IND REG TIMER" (bar; no phase labels printed on its two output lines) -> R23 "GI MODIFIED XR IND'S FROM IND REG TO THE UPDATED INDEX IND REG" (35.26.02.1) and R24 "ADV ABC IF NOT INTLKD BY TBC" (no ALD).
- H18 "LAAR INT ?" -- NO -> H25 "STORE DATA READY ?" -- YES -> R25 "RESET ABC LF TAG" (36.01.09.1) and R26 "GI ACOB INTO ABC DATA FIELD" (35.23.02.1).

###### Legend (PRINTED, bottom right, verbatim)
```
  OP X2 - FP STORE
LAOP 13 - FP STORE
LAOP 17 - VFL (1ST)
LAOP 23 - VFL (2ND)
LAOP 21 - VFL (SPECIAL)
LAOP 41 - BI
LAOP 33 - I BOX REAL
```
(The "I" of "I BOX REAL" prints as a dotted lower-case i, a type defect.)

##### 2. Structure

- Sequencer: ARITH BUS TIMER. TON: (a) "TRANS IND TIMER LAOP 33 INT" at 38.33.01.1; (b) from "TRANS IND TIMER E + M" via "WHAT IS BEING STORED ?": C-D REG stores (17, 23, 41) enter at EE when the store data is ready ("LAST CYCLE STORE MEM" ON); ACOB stores (X2, 13, 21) enter at 38.33.02.1 when the store data is ready ("LAST CYCLE STORE MEM" TRIG ON) or when a zero divisor cancelled the remainder ("STORE INHIBIT MEM" TRIG ON). TOF: not printed. Phases: EE, E.M̄, M, E.M.
- Second sequencer: "START IND REG TIMER" (E.M phase, I-box real store LAOP 33 INT at ADDR 11, or a store at ADDR 11 whose data is ready). Phases not labelled.
- (DERIVED) The "E + M" connector matches the "STORES" exits of Figs 3.2.16-3.2.18 (taken from the E + M line of the transfer indicator timer); "LAOP 33 INT" matches Fig 3.2.19's phase-M exit to STORES via "TB TIMER M ?".

##### 3. Step table

| phase | condition(s) (PRINTED) | action(s) (PRINTED) | ALD | notes |
|---|---|---|---|---|
| entry | WHAT IS BEING STORED ? C - D REG (17, 23, 41); IS STORE DATA READY ? YES ("LAST CYCLE STORE MEM" ON) | start ARITH BUS TIMER at EE | -- | **[KEY]** LAST CYCLE STORE |
| entry | ACOB (X2, 13, 21); IS STORE DATA READY ? YES ("LAST CYCLE STORE MEM" TRIG ON) | start ARITH BUS TIMER | 38.33.02.1 | **[KEY]** |
| entry | ACOB; HAS A ZERO DIVISOR CANCELLED ANY REMAINDER THAT WAS TO BE STORED ? YES ("STORE INHIBIT MEM" TRIG ON) | start ARITH BUS TIMER | 38.33.02.1 | **[KEY]** store inhibit |
| entry | TRANS IND TIMER LAOP 33 INT | start ARITH BUS TIMER | 38.33.01.1 | |
| EE | -- | SEND "PASS DATA" SIGNAL TO A CHKR | 38.23.03.1 | |
| EE | WHERE IS DATA ? C REG (17, 41, 33 INT) | GI C REG TO ACIB | 35.21.01.1 (shared) | |
| EE | WHERE IS DATA ? D REG (23) | GI D REG TO ACIB | 35.21.01.1 (shared) | |
| E.M̄ | -- | RESET "TRANS IND TIMER M" | 38.38.02.1 | |
| E.M̄ | LAST INSTR LEVEL ? YES (IC ON) | DELAY IND TEST; SET IND TEST E; RESET: BR SUCC COND IND'S LAST CYCLE STORE, STORE INHIBIT TRIGGERS | 38.32.09.1; 38.38.03.1; 38.24.02.1, 38.24.03.1 | **[KEY]** |
| E.M̄ | NON-ARITH INSTR ? YES | SET LA NOOP IND TEST M; SIGNAL PAU TO SET "MSTR TEST COMPLETE" TRIG | 38.35.03.1; 38.23.01.1 | |
| E.M̄ | NON-ARITH INSTR ? NO | SET NORMAL IND TEST M; SIGNAL PAU OF LA TESTS CMPLT | 38.35.01.1; 38.23.01.1 | |
| E.M̄ | C+D STORE OP ? YES (17 23 41 33 INT) | SIGNAL A CHKR TO CHK PARITY | 38.23.03.1 | |
| E.M̄ | 33 INT YES, or (33 INT NO (17, 23, 41) and 23 ? YES) | SIGNAL A CHECKER NOT TO SET ITS CHK CMPLT TGR | -- | |
| E.M̄ | 33 INT NO (17, 23, 41) | RESET TBC AES; ADV TBC IF INTLKD WITH ABC, AND NOT INTLKD BY OCC | 38.21.03.1; 38.23.03.1 | **[KEY]** interlock |
| M | GOOD INTERNAL STORE ? NO; or ADDR 11 ? NO; or BI STORE ? YES (LAOP41) | ADV ABC IF NOT INTLKD BY TBC | 38.31.05.1 | **[KEY]** interlock |
| M | 33 INT ? YES; ARC TBC INTLKD ? YES | ADV TBC IF NOT INTLKD BY OCC | -- | **[KEY]** interlock |
| E.M | ACOB STORE OP ? YES (X2,13,21); STORE DATA READY ? YES ("LAST CYCLE STORE MEM" ON) | SIGNAL A CHKR THAT ACOB DATA IS ACCEPTED | 38.23.03.1 | |
| E.M | LAAR INT ? YES | RESET LAAR BUSY TRIG; GI ACOB TO LAAR ADDER IF NOT ADDR 1, 5, or 6 | 38.23.03.1; 35.25.01.1/.02.1/.03.1 | **[KEY]** |
| E.M | ADDR 8 ? YES; FP STORE ? YES | GI ACOB POS 60-63 TO SIGN BYTE REG POS 4-7 | 35.25.02.1 | |
| E.M | LAAR INT YES; BI STORE ? (exit 33 INT X2 13 17 23); ADDR 11 ? YES; 33 INT ? YES, or 33 INT NO and STORE DATA READY ? YES ("LAST CYCLE STORE MEM" ON) | START IND REG TIMER -> GI MODIFIED XR IND'S FROM IND REG TO THE UPDATED INDEX IND REG; ADV ABC IF NOT INTLKD BY TBC | 35.26.02.1; -- | **[KEY]** UPDATED INDEX |
| E.M | LAAR INT ? NO; STORE DATA READY ? YES | RESET ABC LF TAG; GI ACOB INTO ABC DATA FIELD | 36.01.09.1; 35.23.02.1 | **[KEY]** |

##### 4. Counters, timers, triggers, registers, LAOP

- Counters: ABC, TBC, OCC.
- Timers: ARITH BUS TIMER (38.33.01.1 / 38.33.02.1); TRANS IND TIMER (entries "LAOP 33 INT", "E + M"; "RESET "TRANS IND TIMER M""); IND REG TIMER ("START IND REG TIMER").
- Triggers: "LAST CYCLE STORE MEM" TRIG; "STORE INHIBIT MEM" TRIG; BR SUCC, COND IND'S, LAST CYCLE STORE, STORE INHIBIT TRIGGERS; IND TEST E; LA NOOP IND TEST M; NORMAL IND TEST M; "MSTR TEST COMPLETE" (PAU); A CHECKER CHK CMPLT TGR; TBC AES; LAAR BUSY TRIG; ABC LF TAG.
- Registers/buses: C REG; D REG; ACIB; ACOB; LAAR; LAAR ADDER; SIGN BYTE REG; IND REG; UPDATED INDEX IND REG; ABC DATA FIELD; XR IND'S.
- LAOP/OP codes: 17, 23, 41, X2, 13, 21, 33 INT, 23, LAOP41, ADDR 1, 5, 6, 8, 11 (addresses); legend OP X2, LAOP 13, 17, 23, 21, 41, 33.

##### 5. TIME

PRINTS NO TIME. Phase letters only.

##### 6. [KEY] items

- **[KEY]** "IS STORE DATA READY ?" YES ""LAST CYCLE STORE MEM" ON" / ""LAST CYCLE STORE MEM" TRIG ON" -- the arithmetic-bus timer for a store starts only when store data is ready.
- **[KEY]** "HAS A ZERO DIVISOR CANCELLED ANY REMAINDER THAT WAS TO BE STORED ?" YES ""STORE INHIBIT MEM" TRIG ON".
- **[KEY]** "RESET: BR SUCC COND IND'S LAST CYCLE STORE, STORE INHIBIT TRIGGERS" (38.24.02.1, 38.24.03.1).
- **[KEY]** "DELAY IND TEST" (38.32.09.1) at last instruction level on a store (contrast "NO DELAY IND TEST" on the transfer-indicator pages).
- **[KEY]** LAAR: "LAAR INT ?" YES -> "RESET LAAR BUSY TRIG" (38.23.03.1), "GI ACOB TO LAAR ADDER IF NOT ADDR 1, 5, or 6" (35.25.01.1 .02.1 .03.1).
- **[KEY]** UPDATED INDEX: "START IND REG TIMER" -> "GI MODIFIED XR IND'S FROM IND REG TO THE UPDATED INDEX IND REG" (35.26.02.1).
- **[KEY]** "LAAR INT ?" NO -> "STORE DATA READY ?" YES -> "RESET ABC LF TAG" (36.01.09.1), "GI ACOB INTO ABC DATA FIELD" (35.23.02.1). (DERIVED: store data held in the ABC level's data field; the page does not print any transfer of that data to a later fetch.)
- **[KEY]** Interlocks: "ADV ABC IF NOT INTLKD BY TBC" (38.31.05.1, and again after START IND REG TIMER); "ADV TBC IF NOT INTLKD BY OCC" after "ARC TBC INTLKD ?" YES; "ADV TBC IF INTLKD WITH ABC, AND NOT INTLKD BY OCC" (38.23.03.1).
- **[KEY]** "SIGNAL A CHECKER NOT TO SET ITS CHK CMPLT TGR"; "SIGNAL A CHKR THAT ACOB DATA IS ACCEPTED" (38.23.03.1).
- **[KEY]** Legend: OP X2 - FP STORE; LAOP 13 - FP STORE; 17 - VFL (1ST); 23 - VFL (2ND); 21 - VFL (SPECIAL); 41 - BI; 33 - I BOX REAL.
- No store-to-fetch forwarding is printed on this page.

##### 7. Could not read / ambiguities

- 35.21.01.1: last digit faint (shared ref under GI C REG / GI D REG TO ACIB).
- "GIACOEPOS 60-63": printed so (letters run together; the B of ACOB looks like E).
- "C+D STORE OP ," -- "+" faint, stray comma.
- "ARC TBC INTLKD ?" printed ARC.
- H19 "BI STORE ?" exit is not labelled YES or NO; it carries the stacked label "33 INT X2 13 17 23" (DERIVED: the not-BI path).
- Many exits not drawn (H6 NO, H10 NO, H13 NO, H14 NO, H15 NO, H16 NO, H17 NO, H21 NO, H22 NO, H24 NO, H25 NO, H20 NO).
- ALD "38.23.03.1" printed under RESET LAAR BUSY TRIG here (38.53.03.1 on Figs 3.2.16-3.2.18, 3.2.20).

#### LAOP legend table, Figs 3.2.15-3.2.21 (R23-9732, PDF 107-113)

Meanings are PRINTED, from the legends at the foot of each figure, with ditto marks expanded (expansion is DERIVED; the raw legend is in each fig file). "OP" rows are printed with "OP", not "LAOP". Fig 3.2.15 (PDF 107) and Fig 3.2.18 (PDF 110) print no legend.

| LAOP | meaning as printed | figure | PDF |
|---|---|---|---|
| OP X2 | FETCH OR STORE | 3.2.16 | 108 |
| 13 | STORE | 3.2.16 | 108 |
| OP X1 | INSTR | 3.2.17 | 109 |
| 05 | FETCH (1 of 1) | 3.2.17 | 109 |
| 03 | FETCH (1 of 2) | 3.2.17 | 109 |
| 07 | FETCH (2 of 2) | 3.2.17 | 109 |
| 17 | STORE (1ST) | 3.2.17 | 109 |
| 23 | STORE (2ND) | 3.2.17 | 109 |
| 21 | STORE (SPECIAL) | 3.2.17 | 109 |
| 15 | FETCH (SPECIAL) | 3.2.17 | 109 |
| OP 20 | IO BX | 3.2.19 | 111 |
| OP 24 | " DISC (ditto = IO DISC) | 3.2.19 | 111 |
| 25 | " DUMMY NOT CCW (ditto = IO DUMMY NOT CCW) | 3.2.19 | 111 |
| 65 | " " CCW (ditto = IO DUMMY CCW) | 3.2.19 | 111 |
| 02 | I BOX PSEUDO STORE | 3.2.19 | 111 |
| 33 | " REAL STORE (ditto = I BOX REAL STORE) | 3.2.19 | 111 |
| 51 | " INT. FETCH (ditto = I BOX INT. FETCH) | 3.2.19 | 111 |
| 04 | PX PSEUDO STORE | 3.2.19 | 111 |
| 06 | " " " NOOP'D (ditto = PX PSEUDO STORE NOOP'D) | 3.2.19 | 111 |
| 63 | INDICATOR ONLY | 3.2.19 | 111 |
| 00 | TEST LEVEL | 3.2.19 | 111 |
| 11 | RAC RCY (NOOP RCY REQ) -- first word reads "RAC" at 600 dpi; "BAC" not excluded | 3.2.19 | 111 |
| OP X2 | FP FETCH | 3.2.20 | 112 |
| 05 | VFL " (1 OF 1) (ditto = VFL FETCH (1 OF 1)) | 3.2.20 | 112 |
| 03 | " " (1 OF 2) (= VFL FETCH (1 OF 2)) | 3.2.20 | 112 |
| 07 | " " (2 OF 2) (= VFL FETCH (2 OF 2)) | 3.2.20 | 112 |
| 37 | BI " (= BI FETCH) | 3.2.20 | 112 |
| 51 | I BOX " (= I BOX FETCH) | 3.2.20 | 112 |
| OP X2 | FP STORE | 3.2.21 | 113 |
| 13 | FP STORE | 3.2.21 | 113 |
| 17 | VFL (1ST) | 3.2.21 | 113 |
| 23 | VFL (2ND) | 3.2.21 | 113 |
| 21 | VFL (SPECIAL) | 3.2.21 | 113 |
| 41 | BI | 3.2.21 | 113 |
| 33 | I BOX REAL (printed with a dotted lower-case "i") | 3.2.21 | 113 |

##### Codes used in conditions/line labels but given NO legend meaning on these pages

| LAOP (as printed) | where | figure | PDF |
|---|---|---|---|
| LAOP 11 (hexagon) | after LAST INSTR. LEVEL YES; NO -> RESET "MSTR TEST COMPLT" TRIG. IN PAU | 3.2.16, 3.2.17 | 108, 109 |
| X1 / 35 / 75 / 48 (stacked line label) | 1ST INSTR. LEVEL ? YES -> SET "SAU EN MEM" TRIG | 3.2.17 | 109 |
| LAOP 31,57 ? | YES -> RESET TBC AES, ADV. TBC IF NOT INTLKD BY OCC | 3.2.18 | 110 |
| LAOP 31 ? | YES -> RESET LF TAG | 3.2.18 | 110 |
| LAOP 11 | YES -> RECOVERY REQ | 3.2.18 | 110 |
| LAOP 45 ? | YES -> BR SUCC & NO COND INDS | 3.2.18 | 110 |
| LAOP 75 ? | NO -> IS THIS THEINTRPT FREE INSTR. ? | 3.2.18 | 110 |
| 45, 47 (line label) | BR. RECOVERY ? YES | 3.2.18 | 110 |
| 47 (line label) | GOOD RECOVERY LEVEL NO | 3.2.18 | 110 |
| LAOP 02,04,33,63 ?; LAOP 02,04; 02; LAOP 33 EXT. ?; 06; LAOP 00,02,25,63,65,33 EXT. ?; 02,04,33,63 ?; 06 ?; 33 EXT. ?; .51; LAOP 51 ?; LAOP 33 INT. ? | condition hexagons | 3.2.19 | 111 |
| LAOP 37 ?; LAOP 51 ?; LAOP 07 ?; LAOP 37; "05 07 37" (line label); "X2" (line label) | condition hexagons / labels | 3.2.20 | 112 |
| "17, 23, 41" / "X2, 13, 21" / "17, 41, 33 INT" / "23" / "17 23 41 33 INT" / "LAOP41" / "33 INT X2 13 17 23"; 33 INT; 23 ?; 33 INT ? | line labels / hexagons | 3.2.21 | 113 |

Notes (DERIVED, for the reader): LAOP 11 is glossed only on Fig 3.2.19 ("RAC RCY (NOOP RCY REQ)"), and on Fig 3.2.18 it leads to "RECOVERY REQ", on Fig 3.2.19 to "NOOP RECOVERY REQ". LAOP 31, 45, 47, 57, 75 (branch page) have no legend on PDF 107-113. The X1/X2 "OP" rows are instruction-class codes, not LAOPs.

### Appendix F. Perf. Char. Vol. 1 Tables 4-8 and prose; Blosk TR00.722 (reader F)

#### 7030 Performance Characteristics, Vol. 1 (3/8/61), ch. 3: Tables 4-8 and I-box/LA/memory timing prose

Source: `stretch/docs/7030_Performance_Characteristics_Vol1_Mar61.pdf` (71 PDF pages).
Every value below was read from 300-dpi page images (tiles <= 1350 px), not OCR.
Markings: **PRINTED** = exactly as on the page; **DERIVED** = my note; **ILLEGIBLE** = could not read.
Unless marked otherwise, everything here is PRINTED. Typography: the page prints "µsec" in the tables and "µs" in prose; the
instruction mnemonics in the tables are italic on the page.

##### Page map (PRINTED folio at bottom right; date "3/8/61" at bottom left)

| Printed page | PDF page | Content |
|---|---|---|
| 3-10 | 28 | end of Table 3 glossary; heading "Timing of I-Box Instructions" + one-sentence intro |
| 3-11 | 29 | Table 4 (Direct Index), Table 5 (Immediate Index) |
| 3-12 | 30 | Table 6 (Miscellaneous Instructions) |
| 3-13 | 31 | Table 6 (cont'd), Table 7 (Unconditional Branch) |
| 3-14 | 32 | Table 8 (Index Branches), Table 9 (Transmit Instructions) |
| 3-15 | 33 | Table 9 (cont'd), "Analysis and Interpretation..." / "Machine Organization" (memory readout/recycle) |
| 3-16 | 34 | Machine organization cont'd (up to ten instructions in flight) |
| 3-17 | 35 | Effect of Memory Interleaving; Overlapping of Decoding |
| 3-18 | 36 | VFL decoding times; I-box decoding 0.6 µs; Look-Ahead Levels |
| 3-19 | 37 | LAAR demand; The I-Checker (0.6 µs) |
| 3-20 | 38 | The LAAR, Stores and Internal Operand Fetches |
| 3-21 | 39 | single LAAR wait; index-storage store stall; Store Close to Fetch |
| 3-22 | 40 | store/fetch conflicts (2),(3); forwarding; I-box Instructions 1-2 |
| 3-23 | 41 | I-box Instructions 2-7 (0.9-1.2 µs per LA level); Recovery Action |
| 3-24 | 42 | Recovery Action cont'd |

DERIVED: the caller's estimate "3-16 ~ PDF 34" is right, but Tables 4-8 are NOT on 3-16..3-24; they are on 3-11..3-14
(PDF 29-32). Printed 3-16..3-24 hold only the timing prose, transcribed in section 2.
DERIVED: the pdftotext layer reads the 3-16 date as "2/8/61"; the image reads "3/8/61".

---

##### 1. Tables

###### Lead-in (p. 3-10, PDF 28), PRINTED

> Timing of I-Box Instructions
>
> The following tables list the I-box times for decoding for execu-tion of I-box instruction.

###### TABLE 4. I-BOX TIMES – DIRECT INDEX (p. 3-11, PDF 29)

| Instruction | Address in EM | Address in XS | Address in IR |
|---|---|---|---|
| LX | 4.8 µsec + dec | 4.8 µsec + dec | 4.2 µsec + dec + LAdr |
| LV, LC, LR | 4.2 µsec + dec | 4.2 µsec + dec | 3.6 µsec + dec + LAdr |
| SX | 1.2 µsec + dec + LAAR | 4.2 µsec + dec | 1.2 µsec + dec + LAAR |
| SV, SC, SR | 4.2 µsec + dec + LAAR | 5.4 µsec + dec | 3.6 µsec + dec + LAdr + LAAR (printed on two lines: "3.6 µsec + dec + LAdr" / "+ LAAR") |
| SV, SC, SR to TC | (blank) | 6.0 µsec + dec + LAdr | (blank) |
| V + | 4.2 µsec + dec | 4.2 µsec + dec | 3.6 µsec + dec + LAdr |
| V + C | 4.2 µsec + dec | 4.8 µsec + dec | 4.2 µsec + dec + LAdr |
| V + CR (EM) | 8.4 µsec + dec | 9.0 µsec + dec | 8.4 µsec + dec + LAdr |
| V + CR (XS) | 7.2 µsec + dec | 7.8 µsec + dec | 7.2 µsec + dec + LAdr |
| KV, KC | 4.2 µsec + dec | 4.2 µsec + dec | 3.6 µsec + dec + LAdr |
| RNX | 9.0 µsec + dec + LAdr + LAAR (two lines: "9.0 µsec + dec + LAdr" / "+ LAAR") | (blank) | (blank) |
| LVE | 7.8 µsec + dec | 6.6 µsec + dec | 6.6 µsec + dec + LAdr |
| LVE as object INSN of LVE | Additional 4.8 µsec | Additional 3.6 µsec | Additional 3.0 µsec + LAdr (4.2 if LAMT) |
| SVA | 4.2 µsec + dec + LAAR | 5.4 µsec + dec | 3.6 µsec + dec + LAdr + LAAR |
| SVA to TC | (blank) | 6.0 µsec + dec + LAdr | (blank) |

Footnote block inside the table frame, PRINTED:

> ABBREVIATIONS: dec = decade
> LAAR = Look-ahead address register
> LAdr = Look-ahead drain
> LAMT = Look-ahead empty
> TC = Time clock

Notes: the column header is printed "Address in IR" (the "IR" is in a slightly different face, read as IR = internal register;
OCR renders it "m"). "dec = decade" is PRINTED; DERIVED: it is presumably the decoding time, but the page defines it only as "decade".
In the "SV, SC, SR to TC" and "SVA to TC" rows the single entry sits under the "Address in XS" column.

###### TABLE 5. I-BOX TIMES– IMMEDIATE INDEX (p. 3-11, PDF 29)

| Instruction | Basic Time | Variations |
|---|---|---|
| LVI, LCI, LRI, LVNI | 2.4 µsec + dec | |
| V + I, V - I | 2.4 µsec + dec | |
| V + IC, V - IC | 3.0 µsec + dec | Also V ± ICR where Count ≠ 0 |
| V + ICR, V - ICR | 7.2 µsec + dec | 1.2 µsec less if Refill from X5 |
| C + I, C - I | 2.4 µsec + dec | |
| KVI, KVNI, KCI | 2.4 µsec + dec | |
| LVS | 5.4 µsec + dec | Additional 1.8 µsec per ADD |

Note: "X5" is PRINTED as such (digit 5, not S); DERIVED: almost certainly means XS (index storage).

###### TABLE 6. I-BOX TIMES – MISCELLANEOUS INSTRUCTIONS (p. 3-12, PDF 30; cont'd p. 3-13, PDF 31)

| Instruction | Address in EM | Address in XS | Address in IR |
|---|---|---|---|
| R (from EM) | 7.8 µsec + dec + LAAR | 7.2 µsec + dec | 6.6 µsec + dec + LAAR + LAdr |
| R (from XS) | 5.4 µsec + dec + LAAR | 5.4 µsec + dec | 4.2 µsec + dec + LAAR + LAdr |
| RCZ (C ≠ 0) | 4.2 µsec + dec | 3.0 µsec + dec | 3.0 µsec + dec + LAdr |
| Z | 1.2 µsec + dec + LAAR | 3.6 µsec + dec | 1.2 µsec + dec + LAAR |

EX (spans the three address columns), PRINTED:

> 1. Decode time, plus
> 2. Always begins with Look-ahead drain, plus
> 3. Instruction fetch time as follows:
>
> | Address | Time |
> |---|---|
> | 0.0, 0.32 | 4.8 µsec |
> | 1.0, 1.32 | 6.0 µsec |
> | 2.0, 2.32 | 7.8 µsec |
> | 3.0, 3.32 | 7.8 µsec |
> | 4.0, 4.32 | 7.8 µsec |
> | 5.0 → 11.32 | 11.2 µsec |
> | 12.0, 12.32 | 7.8 µsec |
> | 13.0 → 14.32 | 5.4 µsec |
> | 15.0, 15.32 | 4.8 µsec |
> | 16.0 → 30.32 | 4.2 µsec |
> | 31.0, 31.32 | 6.0 µsec |
> | 32.0 → up | 5.4 µsec |
>
> 4. Add decode and execution time for given instruction
> 5. Always ends with LA drain, plus
> 6. Add 3.0 µsec for fetch of next instruction

(The arrows "→" are PRINTED as arrows; "Address" and "Time" are underlined headings.)

TABLE 6 (cont'd), p. 3-13, PDF 31. EXIC, PRINTED (spelling "psuedo" is the page's):

> 1. Decode time, plus
> 2. Always begins with a Look-ahead drain
>    a) 4.2 µsec to fetch the psuedo-instruction counter are overlapped with the Look-ahead drain if the ps IC is in EM.
>    b) 3.0 µsec to fetch the psuedo-instruction counter are overlapped with the Look-ahead drain if the ps IC is in XS.
> 3. Instruction fetch time = 6.0 µsec
> 4. Stepping of psuedo-instruction counter
>    a) Add LAAR time if psIC in EM
>    b) Add .6 µsec time if psIC in XS
> 5. Add decode and execution time for given instructions
> 6. Always ends with LA drain, plus
> 7. Add 3.0 µsec for fetch of next instruction

###### TABLE 7. I-BOX TIMES – UNCONDITIONAL BRANCH (p. 3-13, PDF 31)

| Instruction | Basic Time | SIC to EM | SIC to XS |
|---|---|---|---|
| B | 3.6 µsec + dec | 4.8 µsec + dec + LAAR | 4.2 µsec + dec |
| BR | 4.8 µsec + dec | 6.0 µsec + dec + LAAR | 5.4 µsec + dec |
| BE | 3.6 µsec + dec + LAdr (if previously disabled) | 4.8 µsec + dec + LAAR + LAdr (if previously dis-abled) | 4.2 µsec + dec + LAdr (if pre-viously disabled) |
| BEW | Setup time as above on BE (spans the row) | | |
| NOP | 1.2 µsec + dec | Same as Basic | Same as Basic |
| BD | 4.8 µsec + dec + 2 LA drains | 6.0 µsec + dec + 2 LA drains | 5.4 µsec + dec + 2 LA drains |

No footnote.

###### TABLE 8. I-BOX TIMES – INDEX BRANCHES (p. 3-14, PDF 32)

| Instruction | Basic Time | SIC to EM | SIC to XS |
|---|---|---|---|
| CB (Successful) | 4.2 µsec + dec | 6.6 µsec + dec + LAAR | 7.2 µsec + dec |
| CB (Unsuccessful) | 3.6 µsec + dec | 3.6 µsec + dec | 3.6 µsec + dec |
| CBR (EM) (Succ) | 6.6 µsec + dec | 9.0 µsec + dec + LAAR | 9.6 µsec + dec |
| CBR (XS) (Succ) | 6.0 µsec + dec | 8.4 µsec + dec + LAAR | 9.0 µsec + dec |
| CBR (EM) (Unsucc) | 6.0 µsec + dec | 6.0 µsec + dec | 6.0 µsec + dec |
| CBR (XS) (Unsucc) | 5.4 µsec + dec | 5.4 µsec + dec | 5.4 µsec + dec |

Footnote, PRINTED:

> NOTE: CBR behaves like CB if Refill is not to be taken.
> Ex: CBR, branch on count ≠ zero

(In the CBR (EM)(Succ) / SIC to EM cell the second "+" is slightly smudged; reads "9.0 µsec + dec + LAAR".)

Not requested but adjacent: TABLE 9. I-BOX TIMES - TRANSMIT INSTRUCTIONS is on p. 3-14 (PDF 32) and cont'd p. 3-15 (PDF 33);
columns Setup time / Loop time / Termination time (units printed "usec"); not transcribed here.

DERIVED observations (not printed): every Table 4-8 time is a multiple of 0.6 µs (the I-box decode time, p. 3-18) except
the EX fetch entry "11.2 µsec" (5.0 → 11.32), which is not a multiple of 0.6 (11.4 would be); possibly a typo for 11.4, not
verifiable from this page.

---

##### 2. Running prose stating I-box / look-ahead / memory timing (verbatim, PRINTED)

**p. 3-15 (PDF 33), Machine Organization:**
> For example, a 7030 box has a readout time of 1 µs and a recycle time of 2.2 µs, yet in the 7030 system information can be obtained at the rate of one word every 0.3 µs.

DERIVED: this document prints memory readout (access) 1 µs and recycle (cycle) 2.2 µs. A standalone `grep '2\.1'` over
the whole pdftotext layer and over `stretch/docs/ocr/7030_Performance_Characteristics_Vol1_Mar61.txt` returns no hit,
so "2.1 µs" is not printed in Vol. 1 as far as both text layers show.

Also relevant, outside the requested range (p. 3-2, PDF 20, read from the image), PRINTED:
> The times are listed (table 2) in terms of the basic machine cycles, which is presently 0.3 microsecond.

(That is the E-box/floating-point machine cycle used in Tables 2-3. DERIVED: the I-box times of Tables 4-8 are all
multiples of 0.6 µs = 2 x 0.3 µs.)

**p. 3-16 (PDF 34):**
> Within the CPU this local autonomy means that temporary delays up to several µs in one unit can be tolerated without slowing down the entire pipe line. Extensive buffering of information is needed to absorb such temporary delays, and within the 7030 CPU at any given time up to ten instructions can be in various stages of processing. Within wide limits, the times for instruction processing is not the sum of: Instruction fetch, instruction error check, decoding, operand fetch, oper-and error check, and execution but is the maximum of these times aver-aged over several instructions.

> The E-box times of the instructions listed in the previous section are the times realizable if the LA levels (which are buffers to the E-box) can always supply needed information to the E-box.

**p. 3-17 (PDF 35), Effect of Memory Interleaving:**
> With the instruction buffers 1Y, 2Y (capable of housing four half-word instructions), in the I-box, and the four LA levels, the advantage of memory interleaving is fully exploited.

> The demand of the E-box on LA is usually no higher than one word per 1.5 µs (sequence of floating adds) and on the average, the memory is not a factor. In terms of the four-level look-ahead, the requirement is satisfied if any four E-box demands are fulfilled in 6 µs. The memory interleave scheme allows four words every 2.2 µs (four box interleaving) or four words every 4.4 µs (two box interleaving).

> In actual computations, with the instructions occupying the two lower memory boxes and data occupying the four upper memory boxes, memory conflict is not expected to be an important factor, even if the I/O units are in full operation.

**p. 3-17 (PDF 35), Overlapping of Decoding:**
> The I-box decoding, address indexing, and operand request continues as long as instructions are available and as long as LA levels are avail-able for loading. For a sequence of floating point instructions the decoding rate is one instruction per 1.2 µs. With few exceptions, this is faster than the execution rate. Thus the decoding time for average floating point se-quences is completely overlapped by concurrent E-box execution time. In other words, floating point instructions are E-box limited. Address index-ing has no measurable effect on the timing of floating point instructions.

**p. 3-18 (PDF 36):**
> VFL instruction decoding is much more complicated. The minimum time is 3.6 µs which includes the loading of two LA levels. Each addition level requires an additional 0.6 µs, and each indexing operation requires 0.6 µs. Of course, there may be further slow down in the decoding process if the LA levels are not available for loading, or if the second half of the instruction is not available when needed.

(Page sets "µs,andeach" without spaces; "addition level" is the page's wording.)

> The decoding time of I-box instructions is 0.6 µs. Since these in-structions are executed in the I-box, the decoding time has been included in the execution times. The processing time of I-box instructions can be largely overlapped by concurrent E-box action, since their E-box time is only 1.2 µs.

> Whenever a branch instruction is successfully executed, the pre-fetched instructions in 1Y, 2Y must be replaced by new instructions. The latter have to be checked prior to use, and the decoding of the next instruc-tion will be delayed. This delay has been taken into account in the timing given. Again, concurrent E-box action can overlap much of this.

Look-Ahead Levels (p. 3-18):
> The following instructions empty the LA completely: T, TI, SWAP, SWAP I, RNX, BD.

> All I-box instructions load LA levels for index register recovery or for indicator register updating. These levels are not useful to the E-box and have the effect of reducing the number of LA levels.

> VFL data with word boundary crossover represent inefficient use of LA levels.

**p. 3-19 (PDF 37):**
> Frequent demands on LAAR (such as in consecutive STORE instruc-tions) and prolonged decoding delays in the I-box in general often lead to a half-empty look-ahead.

> When the number of effective LA levels are reduced, the E-box may become idle. The I-box processing time can then no longer be absorbed.

The I-Checker:
> The I-Checker is shared between the I-box and LA. It processes in-formation in 0.6 µs and is used for the following functions:
> 1. Instruction word error check with concurrent ECC to I-parity conversion.
> 2. I-box data error check with concurrent ECC to I-parity conver-sion.
> 3. Passage of data and VFL operation code from I-box to LA, with concurrent I-parity to LA-parity conversion.
> 4. E-box fetch operand error check and check code conversion.
> 5. Store operand error check and check code conversion.
> 6. As part of data path between LA and I-box during, say, branch recovery.
> 7. As part of I-box internal data path.
> 8. As part of LA internal data path.

> When an I-Checker conflict occurs, the processing of one piece of data may have to be delayed by 0.3 to 0.6 µs.

**p. 3-20 (PDF 38), The LAAR, Stores and Internal Operand Fetches:**
> All "to-memory" operations involving the main memory from the 7030 CPU are prepared by the I-box and accomplished by the look-ahead. I/O stores are, however, performed directly between the MBCU and ex-change units.

> The look-ahead address register (LAAR) is created for the purpose of containing the store address. LA levels are made available for the store operand.

> In the case of I-box store type instructions (SX, SV, SC, SR, SVA, R, RXZ, T, SWAP, etc.) the store operands are already available during I-box processing time and can be converted to ECC check bits during shipment to LA, simplifying the store action in LA. In practically all other cases the store operand will not be available during I-box proc-essing. In any case, the LAAR will remain "busy" from the time of look-ahead loading until the proper operand is available, is fetched, checked, and accepted by the MBCU.

> In an instruction, the address may refer to the main memory, in-dex register storage, or an internal register. The I-box, upon decoding an instruction whose fetch operand is an internal register, uses the LAAR to store the internal operand address. This is because the needed operand is not available during the decoding stage, and the mechanism for internal operand fetch already exists for the handling of store instruc-tions. Unlike a standard store, no memory bus request is needed, and the LAAR is freed sooner.

> (By an internal operand address is meant address 3, or an address between 5 and 12 inclusive. $Z, $IA, $MB, and $RM, $FT and $TR are *bona fide* main memory locations. $IT , $TC and $O through $15 are in index storage.)

(The "$" is printed as a struck S; "$IA" could be "$1A" in the image, the glyph after $ is ambiguous between I and 1; "$O" could be "$0".)

**p. 3-21 (PDF 39):**
> Since there is only one LAAR, if the latter is busy whenever the I-box decodes an instruction requiring LAAR, a wait must occur until the LAAR is free for reloading. Therefore, LAAR-requiring instructions should preferably be reasonably far apart, ideally with three or more time consuming instructions in between to ensure smooth I-box decoding. Measurements on consecutive floating-point-to-memory operations (ST, MT, LFT, etc.) do not therefore yield realistic timing information.

> A store into index storage is a time-consuming operation. When-ever such an instruction is decoded, since the next instruction may make use of the new index contents, the I-box does no further decoding until the new index contents arrives.

Store Close to Fetch:
> Whenever I-box requests a memory fetch, a comparison is made with the contents of LAAR to avoid logical conflicts. In all cases, logi-cal conflicts will not produce wrong results, although some delays are to be expected.

> One such conflict is a store into a location corresponding to a pre-fetched instruction, such as in the sequence:
>
>     A    ST (u),  A +. 0.32
>          * + (n), 1000. ($5)                    (1)
>
> The second instruction, having been previously fetched into 1 Y or 2 Y, clearly cannot have the correct information until the store is complete. When such a store is decoded, I-box invalidates the prefetched instructions and waits until the correct information is available.

(OCR read "$15" in (1); the image shows "($5)". "A +. 0.32" has a small mark between + and 0.32 that may be a period or a smudge.)

**p. 3-22 (PDF 40):**
> Another conflict is a store into a nearby I-box operand address:
>
>     ST (u),      1003. ($12)
>     V +, $15, 1003. ($12)                       (2)
>
> The execution of the second instruction is delayed until the correct operand arrives.
>
> A third such conflict is a store into a nearby E-box operand address:
>
>     ST (n),   1007.
>     * (n) ,   1007.                             (3)
>
> The I-box comparison with the LAAR shows that the operand will be in the LA prior to its arrival at the memory. A forwarding mechanism is activated to make the store operand available to the fetch level. Further LA loading in the I-box is delayed until the forwarding is completed.

> Forwarding is available also for consecutive fetch of the same mem-ory operand. Whenever a fetch-type instruction is decoded, the fetch ad-dress is gated into LAAR unless the latter is busy. This act does not make LAAR busy but can allow the forwarding on successive fetches.

I-box Instructions:
> 1. Some I-box instructions require the emptying of the LA. Con-current E-box operations would not be possible.
> 2. Each I-box instruction results in one (sometimes more) level of LA being loaded. This is done to enable the convenient up-dating of certain indicators and to allow interruption action (if needed) to take place in step with other interruptions. The loaded level may be an index recovery level containing the old [p. 3-23] contents of an index register to enable the restoration in case of unexpected interruptions. It takes 0.9 to 1.2 µs to process an LA level corresponding to I-box instructions. This time cannot be overlapped by concurrent E-box action.

**p. 3-23 (PDF 41):**
> 3. The E-box overlapping cannot be effective unless I-box instruc-tions are well dispersed.
> 4. I-box operand fetches are made when the instruction is decoded. There is no look-ahead buffering to reduce the effective fetch time. I-box immediate instructions, not requiring memory ac-cess, are therefore faster than the "direct index arithmetic in-structions".
> 5. Some I-box instructions require more than one memory refer-ence.
> 6. All successful branch instructions require the fetch of new instructions. The instructions previously buffered into 1Y and 2Y are invalidated.
> 7. The treatment of some conditional branches requires extensive E-box action and will be discussed in the next section. The fol-lowing branches, however, involve conditions known to the I-box and are executed entirely within the I-box:
>    CB and variants
>    Bind for XF, XVLZ, XVZ, XVGZ, XCZ, XL, XE, XH.

Recovery Action:
> The I-box is usually ahead by several instructions during a machine run of the E-box. There are certain situations, however, which may force the I-box to refer to the same instruction as the E-box:
> 1. "Wrong branch" recovery, the I-box having made a wrong assumption about the path to be chosen on conditional branch.
> 2. Interruption.

**p. 3-24 (PDF 42):**
> These cases may require the I-box to move backwards in time to be in step with the E-box. All changes in the index registers and/or index indicators due to the advance processing by the I-box must now be undone.

> For conditional branches where the condition is unknown to the I-box, the latter assumes the branch to be unsuccessful (to avoid unnec-essary invalidation of 1 Y, 2 Y contents) and processes ahead. Steps are taken, however, to perform the actual test and to facilitate the alterna-tive path to be taken. Altogether four LA levels are used for each such branch instruction: three levels not unlike those for a VFL connect-to-memory instruction plus a branch recovery level. It is noted that there is always a store type level, whether the programmer specifies a change of the tested bit or not. For Bind, two of these four levels involve the LAAR.

> When the I-box guess proved correct, no particular action is taken aside from setting of the tested bit. If, however, the guess proved incor-rect by E-box arithmetic, the I-box has already processed ahead, and re-covery action has to be taken to ensure the logical integrity of the pro-gram. The re-setting of the I-box to the previous state of ten requires shipment of index register information back to the I-box. The correct instruction counter value is also shipped back to the I-box.

("state of ten" is PRINTED; DERIVED: a typesetting split of "state often".)

> The interruption action is quite similar to branch recovery except that in addition a new instruction has to be fetched and executed.

###### Not found in these pages
DERIVED: chapter 3 pp. 3-10..3-24 print no explicit "I-box cycle = 0.6 µs" sentence; the closest PRINTED statements are
"The decoding time of I-box instructions is 0.6 µs" and "each indexing operation requires 0.6 µs" (p. 3-18) and the
I-Checker's 0.6 µs (p. 3-19). No "2.1 µs" memory cycle is printed; the memory figures are readout 1 µs, recycle 2.2 µs
(p. 3-15) and four words per 2.2 µs / 4.4 µs interleaved (p. 3-17). The basic machine cycle is 0.3 µs (p. 3-2).
Compare (DERIVED): Blosk TR 00.722 (Mar 1960) designs to a 0.5 µs I-unit cycle and "2 µs memory"; this Mar 1961
document's I-box times are multiples of 0.6 µs.

#### Blosk, "Stretch I-Unit Design", TR 00.722 (Mar 1960): cycle charts (Figs 6-10) and timing prose

Source: `stretch/docs/TR00.722_Stretch_I-Unit_Design_Mar60.pdf` (50 PDF pages, no text layer).
Everything here was read from 300-dpi page images (tiles <= 1350 px); the OCR file was used only to find pages.
Markings: **PRINTED** = as on the page; **DERIVED** = my reconstruction/inference; **ILLEGIBLE** = not readable.

##### Page map

Printed page = PDF page - 2 throughout the range checked (folio centred at page bottom; on the landscape figure
pages the folio is printed rotated in the left margin).

| Printed | PDF | Content |
|---|---|---|
| 11 | 13 | Index Storage (XS and XR): 200 mµs read-out, 500 mµs machine cycle, 2-cycle XS store |
| 12 | 14 | XR register (no timing) |
| 13 | 15 | Preparation-Execution Register (ZR) (no timing) |
| 14 | 16 | Working Register (WR), start of Index Adder Unit (no timing) |
| 16 | 18 | I checker time-shared, priority system |
| 17 | 19 | interrupt priority 0-63; Updated Indicator Register |
| 19 | 21 | "guess" external memory; fetch/store routing; index stores 2 cycles |
| 20 | 22 | VFL/FL stores to XS: I unit waits; internal-register fetch/store via lookahead |
| 21 | 23 | Program Store Compare; forwarding |
| 22 | 24 | circuit delay 10-20 mµs per block |
| 23 | 25 | E/M trigger cycle definition; 500 mµs control cycle; 4 Mc clock, 250 mµs period |
| 25 | 27 | IC controls |
| 26 | 28 | Lookahead load controls (VFL 2-5 steps; FP sequencers; guess main memory) |
| 28 | 30 | Floating Point Instruction Preparation (Fig 6 text) |
| 29 | 31 | **FIGURE 6. FP INSTRUCTION PREPARATION** (landscape) |
| 30 | 32 | Fig 6 text cont'd; VFL Instruction Preparation begins |
| 31 | 33 | Fig 7 text |
| 32 | 34 | **FIGURE 7. VFL INSTRUCTION PREPARATION** (landscape) |
| 33 | 35 | Fig 7 text end; Count and Branch Execution (Fig 8 text) |
| 34 | 36 | **FIGURE 8. COUNT AND BRANCH EXECUTION** (landscape) |
| 35 | 37 | Fig 8 text end; Transmit Execution (Fig 9 text) |
| 36 | 38 | **FIGURE 9. TRANSMIT EXECUTION** (landscape) |
| 37 | 39 | Fig 9 text end; Conditional Branch Operation (Fig 10 text) |
| 38 | 40 | **FIGURE 10. BRANCH ON INDICATOR EXECUTION** (portrait) |
| 39 | 41 | Fig 10 text end |

DERIVED: the requested "printed pp. 13-14" (PDF 15-16) describe the ZR and WR and contain no time, cycle count,
priority or indicator rule. The XS timing the brief seems to want is on printed p. 11 (= PDF 13; the OCR file's
"PDF page 13" marker matches). I transcribed the timing sentences from printed pp. 11, 16-26 as well (section 2).

---

##### 1. The charts

###### How the cycle columns were assigned (DERIVED, applies to all five figures)
The charts print **no cycle numbers and no grid**. Each row is a set of horizontal bars with tick marks; every bar
is an integer number of equal tick-to-tick spans, and the IAU row of each chart is a continuous run of ticks. I
measured the tick pitch in the 300-dpi image (Fig 6: 150 px; Fig 7: 106.5 px; Fig 8: 150 px; Fig 9: 116.5 px;
Fig 10: 150 px), took the left end of the earliest bar as the start of cycle 1, and assigned each bar to the
column(s) it spans. All bar ends fell within about +/-8 px of the computed boundaries. Cycle numbers "c1..cN" are
therefore DERIVED; the labels in the cells are PRINTED. The brace spans ("8 CYCLES" etc.) are PRINTED and bounded by
long vertical dashed lines, whose positions I give as column boundaries.

Glyph note (PRINTED vs read): the lettering prints the register names "1Y", "2Y" with a "1" that is drawn like
an "I" ("IY", "IYL", "IYR"); the text pages print "1Y", "1YR". I write 1Y. "->" stands for the printed arrow.
"IF" = instruction fetch, "OF" = operand fetch, "XF" = index fetch (DERIVED from the prose).

Row names are PRINTED as: MAB, I CHKR, IAU, XS, LALD (Fig 10: "LA LD"), LA #1..#4, LA->E, EXEC., MISC.
No chart row is labelled IC, Y, Z, MAB-address, or "index adder" as such: the index adder appears as row "IAU".

###### Cycle length (applies to all figures)
- PRINTED in Fig 6 itself: "4 FP INSTUCTIONS / 4.0 µS." [sic], "8 CYCLES", "FP RATE = 1 / 1.0 µS".
  DERIVED: 8 cycles = 4.0 µs, so 1 chart cycle = 0.5 µs.
- PRINTED in the prose: "one FP instruction every two cycles (one microsecond)" (p. 28); "eight cycles or 4.0
  microseconds" (p. 33); "six cycles equal to 3.0 microseconds", "ten cycles or 5.0 microseconds" (p. 35);
  "five cycles or 2.5 microseconds", "two cycles or 1.0 microseconds" (p. 37); "five cycles or 2.5 microseconds" (p. 39);
  "one machine cycle of approximately 500 mµs" (p. 11); "a control cycle should take approximately 500 mµs" (p. 23).
- Figs 7-10 print no time unit, only cycle counts.

---

###### FIGURE 6. FP INSTRUCTION PREPARATION (printed p. 29, PDF 31)

PRINTED annotations: "ASSUMPTION ; EACH FP INST. INDEXED"; asterisk "*" above the MAB bar in c12;
brace "4 FP INSTUCTIONS / 4.0 µS." / "<- 8 CYCLES ->" / "FP RATE = 1 / 1.0 µS" between vertical dashed lines at the
start of c8 and the start of c16.

Chart extent: c1..c16 (16 cycles drawn; FP3, FP4, E1 and the IAU row run off the right edge of c16, FP3/FP4 drawn
with a wavy end mark).

| Cycle | MAB | I CHKR | IAU | XS | LALD | LA #1 | LA #2 | LA #3 | LA #4 | LA->E | EXEC. |
|---|---|---|---|---|---|---|---|---|---|---|---|
| c1 | IF->1Y | | | | | | | | | | |
| c2 | IF->2Y | | | | | | | | | | |
| c3 | | | | | | | | | | | |
| c4 | | | | | | | | | | | |
| c5 | | 1Y->1Y (CHK+DEC) | | | | | | | | | |
| c6 | | 2Y->2Y (CHK+DEC) | 1YL->ZR | XF/1YL | | | | | | | |
| c7 | | | MOD ZR | | | | | | | | |
| c8 | IF->1Y | | 1YR->ZL | XF/1YR | ZR->LA (solid) | | | | | | |
| c9 | OF->LA1 | | MOD ZL | | (dashed continuation of ZR->LA) | | | | | | |
| c10 | OF->LA2 | | 2YL->ZR | XF/2YL | ZL->LA | FP1 | | | | | |
| c11 | | | MOD ZL [sic, see note] | | | FP1 | FP2 | | | | |
| c12 * | IF->2Y | 1Y->1Y | 2YR->ZL | XF/2YR | ZR->LA (solid) | FP1 | FP2 | | | | |
| c13 | OF->LA3 | | MOD ZL | | (dashed continuation) | FP1 | FP2 | | | | |
| c14 | OF->LA4 | | 1YL->ZR | XF/1YL | ZL->LA | | FP2 | FP3 | | LA1->E | |
| c15 | | | MOD ZR | | | | FP2 | FP3 | FP4 | | E1 |
| c16 | IF->1Y | 2Y->2Y | 1YR->ZL | XF/1YR | ZR->LA | | | FP3 -> | FP4 -> | | E1 -> |

Dashed diagonal lines (PRINTED) connect each MAB instruction fetch to its I CHKR check: c1->c5, c2->c6, c8->c12,
c12->c16. DERIVED: instruction-fetch-to-check latency = 4 cycles (fetch in cycle n, check in n+4) every time.

Notes:
- PRINTED label in c11 is "MOD ZL" (verified at 2x zoom: "2YL->ZR MOD ZL 2YR->ZL"); by the pattern (2YL went to ZR
  in c10) it would be MOD ZR. Reproduced as printed.
- LALD bars: each "ZR->LA" bar is solid for one cycle then dashed for the next, ending at the tick where "ZL->LA"
  starts. DERIVED: the dashed cycle is the held-up operand fetch described on p. 30 ("The lookahead load cycle holds up
  its fetch during this cycle and completes it with the load operation on the following cycle").
- The asterisked cycle c12 matches the p. 30 sentence: instruction fetch to 2Y, check on 1Y, 2YR transfer to Z,
  index fetch, attempted LA load, all in one cycle.
- Steady state (DERIVED): c8..c15 (8 cycles) contains 4 LA loads (ZR->LA c8, ZL->LA c10, ZR->LA c12, ZL->LA c14),
  i.e. one FP instruction per 2 cycles = 1.0 µs, as printed.

###### FIGURE 7. VFL INSTRUCTION PREPARATION (printed p. 32, PDF 34)

PRINTED annotations: "ASSUMPTIONS ; 1. VFL INST. ACROSS MEM. WO. BOUNDS  2. NORMAL INDEX BOTH HALVES.
3. TWO OPNDS. REQD."; brace "<- 8 CYCLES ->" between vertical dashed lines at the start of c8 and the start of c16.
No time unit printed on the figure.

Chart extent: c1..c16 (16 cycles; LA #3, LA #4 bars run to the right edge).

| Cycle | MAB | I CHKR | IAU | XS | LALD | LA #1 | LA #2 | LA #3 | LA #4 | LA->E | EXEC. |
|---|---|---|---|---|---|---|---|---|---|---|---|
| c1 | IF->1Y | | | | | | | | | | |
| c2 | IF->2Y | | | | | | | | | | |
| c3-c4 | | | | | | | | | | | |
| c5 | | 1Y->1Y (CHK+DEC) | | | | | | | | | |
| c6 | | 2Y->2Y (CHK+DEC) | 1YL->ZR | XF/1YL | | | | | | | |
| c7 | | | MOD ZR | | | | | | | | |
| c8 | IF->1Y | | 1YR->ZL | XF/1YR | ZR->LA (solid) | | | | | | |
| c9 | OF->LA1 | | MOD ZL | | (dashed continuation) | | | | | | |
| c10 | | | 2YL->ZR | XF/2YL | | FP1 | | | | | |
| c11 | | | MOD ZR | | | FP1 | | | | | |
| c12 | | 1Y->1Y | WBC | | | FP1 | | | | | |
| c13 | | | | | LALD2 | FP1 | | | | | |
| c14 | OF->LA3 | | | | LALD3 | | VFL1 | | | LA1-E (printed with a dash) | |
| c15 | OF->LA4 | | | | LALD4 | | VFL1 | VFL1 | | | E1 |
| c16 | IF->2Y | | 2YR->ZL | XF/2YR | | | VFL1 | VFL1 -> | VFL1 -> | | E1 |

Dashed fetch-to-check lines: c1->c5, c2->c6, c8->c12 (4-cycle latency again, DERIVED).
Notes: no OF->LA2 is printed (DERIVED: LALD2 is the instruction level, which per p. 31 carries no operand fetch).
E1 bar has end ticks at c15 start and c16 end. "WBC" = word boundary crossover test (p. 31).
DERIVED: the 8-cycle brace (c8..c15) is the VFL preparation; p. 33 says "eight cycles or 4.0 microseconds".

###### FIGURE 8. COUNT AND BRANCH EXECUTION (printed p. 34, PDF 36)

PRINTED annotation: brace "<- 6 CYCLES ->" between vertical lines at the start of c3 and the start of c9.
Rows printed: MAB, I CHKR, IAU, XS, LALD, MISC. (no LA #n / EXEC rows). Chart extent: c1..c12 (12 cycles).

| Cycle | MAB | I CHKR | IAU | XS | LALD | MISC. |
|---|---|---|---|---|---|---|
| c1 | OF->LA | | 1YL->ZR | XF/1YL | ZL->LA | |
| c2 | | | MOD ZR | | | DEC |
| c3 | | | | XF/ZJ (Z with subscript J) | | |
| c4 | IF/Z->Y | | | | X->LA | |
| c5 | | | COUNT | | | |
| c6 | | | ADV/DIM | | | |
| c7 | | | Z->ICR | CL/ZJ | | |
| c8 | IF->2Y | 1Y->1Y | | ST/ZJ | IC->LA, and below it INDS->LA | |
| c9 | | | 1YL->ZR | XF/1YL (printed "XF/-1YL" with a stray mark) | | |
| c10 | | | MOD ZR | | | |
| c11 | IF->1Y | | 1YR->ZL | XF/1YR | ZR->LA (solid) | |
| c12 | | 2Y->2Y | MOD ZL | | (dashed continuation) | |

Dashed fetch-to-check lines: c4 (IF/Z->Y) -> c8 (1Y->1Y); c8 (IF->2Y) -> c12 (2Y->2Y). DERIVED: 4-cycle latency.
DERIVED: the 6-cycle brace is c3..c8 (index fetch through ST/ZJ + IC/INDS->LA); p. 35 prints "six cycles equal to
3.0 microseconds". DERIVED: the next FP load ZR->LA occupies c11 (solid) and c12 (dashed continuation), so c9..c12
is the "four cycles later" of p. 35, and c3..c12 = 6 + 4 = 10 cycles is its "ten cycles or 5.0 microseconds".

###### FIGURE 9. TRANSMIT EXECUTION (printed p. 36, PDF 38)

PRINTED annotations: "SET UP" / "<- 2 CYCLES ->" (vertical lines at start of c5 and start of c7);
"WORD 1" / "<- 5 CYCLES ->" (start of c7 to start of c12); "WORD 2" (c12..c16, no brace); "WORD n" with a dashed
arrow "- - - ->" in the IAU row after c16. Rows: MAB, I CHKR, IAU, XS, LALD, MISC.
Chart extent: c1..c16 drawn, plus the "WORD n" arrow.

| Cycle | MAB | I CHKR | IAU | XS | LALD | MISC. |
|---|---|---|---|---|---|---|
| c1 | | | 1YL->ZL | XF/1YL | | |
| c2 | | | MOD ZL | | | |
| c3 | | | 1YR->ZR | XF/1YR | | |
| c4 | | | MOD ZR | | | DEC |
| c5 | | | | XF/ZJ | | |
| c6 | | | XC->WR (X with subscript C) | | | |
| c7 | F/ZOAL | | | | | |
| c8 | | | ZOAL±1 | | | |
| c9 | | | W-1 | | | |
| c10 | | | | | | TEST / W=0 (printed above and below the bar) |
| c11 | ZOAR->LA (see note) | Y->CHKR | | | Y->LA, below it OP->LA | |
| c12 | F/ZOAL (see note) | | ZOAR±1 | | | |
| c13 | | | ZOAL±1 | | | |
| c14 | | | W-1 | | | |
| c15 | | | | | | TEST / W=0 |
| c16 | ZOAR->LA | Y->CHKR | | | Y->LA, below it "OP-LA" (dash, no arrowhead) | |
| after | | | WORD n - - -> | | | |

Note: in MAB the labels "ZOAR->LA F/ZOAL" sit over ONE two-cycle bar (c11..c12) with no middle tick (checked at
2.5x zoom). The split ZOAR->LA = c11, F/ZOAL = c12 is DERIVED (label order; and the word-2 check Y->CHKR at c16 is
then 4 cycles after F/ZOAL, matching the c7 -> c11 latency of word 1, which is drawn as a dashed line).
Note: c1 is "1YL->ZL" and c3 "1YR->ZR" (left to left, right to right), unlike the FP charts' criss-cross.
DERIVED: the loop is 5 cycles per word (c7..c11, c12..c16); p. 37 prints "one word per five cycles or 2.5
microseconds" and "initial set-up time took two cycles or 1.0 microseconds".

###### FIGURE 10. BRANCH ON INDICATOR EXECUTION (printed p. 38, PDF 40)

PRINTED annotation: brace "<- 5 CYCLES ->" between vertical lines at the start of c3 and the start of c8.
Rows: MAB, I CHKR, I AU, XS, LA LD, MISC.. Chart extent: c1..c10 (10 cycles).

| Cycle | MAB | I CHKR | IAU | XS | LA LD | MISC. |
|---|---|---|---|---|---|---|
| c1 | OF->LA | | 1YL—ZR (printed with a dash, no arrowhead) | XF/1YL | ZL->LA | |
| c2 | | | MOD ZR | | | DEC (above bar) / BIN (below bar) |
| c3 | ZOA->MAB (Z with subscript OA), "TEST" printed below the bar | | | | | |
| c4 | | Z->LA | | | OP->LA | |
| c5 | | | | | F->LA | |
| c6 | | | | | ST->LA | |
| c7 | | ZOA->LA | | | BR->LA | |
| c8 | IF->1Y | | 1YR->ZL | XF/1YR | | |
| c9 | | | MOD ZL | | | |
| c10 | | | 2YL->ZR | | ZL->LA | |

DERIVED: the 5-cycle brace is c3..c7 (test fetch + four LA levels: OP, F(etch), ST(ore), BR(anch recovery)); p. 39
prints "five cycles or 2.5 microseconds". The p. 39 text calls this "a continuation of the FP preparation in Figure 5"
(PRINTED; DERIVED: almost certainly means Figure 6, since Figure 5 is the control-stage timing diagram).

###### Cycle counts, summary

| Figure | Chart span drawn (DERIVED) | Printed brace | Printed time |
|---|---|---|---|
| 6 FP preparation | 16 cycles | 8 CYCLES (4 FP instructions) | 4.0 µs; FP rate 1 / 1.0 µs |
| 7 VFL preparation | 16 cycles | 8 CYCLES | (text p. 33: 4.0 µs) |
| 8 Count and branch | 12 cycles | 6 CYCLES | (text p. 35: 3.0 µs; 10 cycles / 5.0 µs to first new FP in LA) |
| 9 Transmit | 16 cycles + "WORD n" | SET UP 2 CYCLES; WORD 1 5 CYCLES | (text p. 37: 2.5 µs/word, set-up 1.0 µs) |
| 10 Branch on indicator | 10 cycles | 5 CYCLES | (text p. 39: 2.5 µs) |

---

##### 2. Prose: every sentence giving a time, cycle count, index-storage rule, updated-indicator rule, priority rule or
##### look-ahead loading/counter rule (verbatim, PRINTED)

Typography: the report prints "mµs" for millimicroseconds (ns). Hyphenation at line ends is shown as on the page
("in-dex") only where it is a split word; otherwise joined.

**p. 11 (PDF 13), Index Storage (XS and XR):**
> The index storage (XS) was actually designed with 17 words of 73 bits each. The seventeenth word contains the interval timer and the elapsed time clock for rapid access and for advancing of these values. It is a two dimensional array (17 x 73) and has a read-out time of approximately 200 mµs. Total access time including address gating, transmission, and decoding takes up one machine cycle of approximately 500 mµs. To store the contents of the XR into XS requires two cycles. The first one destructively reads the selected word, thereby resetting it to zeros; the second cycle writes the XR contents into the selected row of cores. The index address is checked prior to decoding. The XR is checked during the following logical operation for which the index word was fetched.

**p. 12 (PDF 14), XR register** (image read for the bottom third only; rest OCR-located, no times in it):
> There are three d-c detector circuits connected to the XR. These circuits provide the following indications:
>
> | X value less 0 | X count equal 1 |
> | X value equal 0 | X count equal 0 |
> | X value greater 0 | X refill equal all 1's |
>
> These are used to set indicators or modify execution controls for various operations.

**pp. 13-14 (PDF 15-16):** no sentence in these categories (ZR and WR register descriptions; IAU description starts at
the bottom of p. 14 with no timing).

**p. 16 (PDF 18), I checker:**
> ...that one I checker unit could be time-shared between the I unit and look-ahead, provided a fast priority system could be designed to guarantee little loss in performance. This was done, and the result is a single I checker with separate in-busses from the I unit and lookahead, OR'd at the input to the checker.
> This bus feeds the four lookahead levels first and then the XR and the 2Y registers.

(The sentence begins on p. 15, not read. OCR read "ZY registers"; the image shows "2Y registers".)

**p. 17 (PDF 19), interrupt priority and Updated Indicator Register:**
> Priority is established from left to right (0 - 63) and the match with highest priority blocks the remaining ones from being effective.
> Once an interrupt is signalled, the left-most one detect logic is allowed time to establish priority.
> There are eight triggers in the I unit which contain the status of the index register value, count, and refill fields up to the last instruction executed by the I unit. These indicators differ from the status of the corresponding main indicator register triggers by the effect of the instructions which were processed by the I unit and which are still in lookahead, awaiting to be processed by the VFL or FP units. Hence, the term updated indicators. This UIR is used to test for conditional branches on these indicators.

Listing (PRINTED): 1. Index low - XL; 2. Index equal - XE; 3. Index high - XH; 4. Index count zero - XCZ;
5. Index value less than zero - XVLZ; 6. Index value zero - XVZ; 7. Index value greater than zero - XVGZ;
8. Index flag - XF.

**p. 19 (PDF 21):**
> In some cases where there was insufficient time to decode, notably in rapid FP instruction preparation, a "guess" is made that the operand address refers to external memory and the required fetch initiated. The memory area decoding is completed before the fetch is actually executed. This operation can either permit the fetch to be completed or cancel it. If cancelled, the proper fetch is initiated to the correct memory area on the following cycle. Since most operand addresses refer to external memory, this "guess" should save a decode cycle in the majority of cases. In the cases where the "guess" is incorrect, no time is lost since the decode time was required anyway.
> All external memory fetches are executed by the I unit and involve sending an 18 bit word address and a three bit return address to the bus control unit. The return address indicates which Y register in this I unit, or which of the four lookahead levels is to receive the word on return. All stores to external memory are done by lookahead. The I unit loads the store address into the lookahead address register and a store type operation code into the op code field. The operand may be loaded at the same time, in case of an I unit instruction, or may be loaded later as a result of a VFL or FP arithmetic operation.
> All index word fetches are done by the I unit whether for I unit operations or for VFL and FP operands. ... Index stores can be made by either the I unit or the lookahead unit. The operation is similar to the fetch except that two cycles are required, one for resetting, and the other for writing the contents of the XR into the selected row of cores.

**p. 20 (PDF 22):**
> In the case of VFL and FL stores to index storage, the I unit loads the store type instruction into lookahead; then waits until the entire operation is completed, including the resultant store back to index storage.

(Sentence starts at the foot of p. 19. "FL" is PRINTED; DERIVED: probably "FP".)

> Internal transistor register fetches and stores are made by lookahead on the arithmetic checker bus. The fetches and stores are set up by the I unit in loading a lookahead level with the address and properly coding the operation code field. If the fetch is for the I unit, lookahead will first transfer the contents of the register to the lookahead level on the arithmetic checker bus, and then relay it on to one of the Y registers via the I checker bus. If it is a VFL or an FP operand fetch, it is left in the lookahead level for later transfer to arithmetic operand register. The I unit stores to internal registers by loading the word into the lookahead level along with the address and operation code.

> The compare has to be executed rapidly to insure that the proper indication and action can be taken during the same cycle that the fetch or store transfer to lookahead is occurring, and the particular memory address is on the MAB.
> The comparison is made 18 bits parallel in five logical levels and indicates whether the contents of MAB is inside the bounds or outside.

**p. 21 (PDF 23), Program Store Compare:**
> Whenever a store is loaded into lookahead this comparison is made. If an equal condition results it indicates that the contents of that location have been fetched already and loaded into the I unit. A recovery is always made under these conditions.
> This does not solve the problem entirely. Since lookahead has four levels, all subsequent fetches have to be compared against the store address, once it is loaded into lookahead. If an instruction fetch or an I unit operand fetch compares equal, the fetch is held up until the store is completed. If an I unit operand fetch for lookahead compares equal with the store address, appropriate controls are effected. These initiate a "forwarding" operation of the store operand to the designated fetch level, without first requiring a store to memory. This comparison is done in another compare circuit between the memory address-bus and the store address register in lookahead. None of these comparisons cause recoveries of the I unit.

**p. 22 (PDF 24):**
> High speed, direct coupled, drift transistor current mode circuits were used throughout the design with an estimated delay of 10 to 20 millimicroseconds per logic block.

**p. 23 (PDF 25), control stage and cycle:**
> The E trigger is turned on by an A clock pulse. Its outputs control the output gating of the data paths, the turn-off of the previous M stage and -- at the next B pulse -- the turn-on of its own. When the M trigger comes on, it causes the turn-off of the E trigger, and the turn-on of the next E trigger at the following A pulse. The entire cycle, then, is defined as the time from the rise of the A pulse, which turns it on, to its completion which turns it off. This is twice the period of the clock, since A and B pulses arrive alternately from the master clock in a symmetrical sequence.
> Control overlap is accomplished by selecting and turning on control stages simultaneously with the result in-gating of the previous cycle.
> The control paths and data paths were all designed for a maximum of twenty-four logical levels. This included the cabling between frames, which was estimated at 15 feet of coax equivalent to the delay through one logic block.
> Assuming a maximum delay of 20 mµs per block means that a control cycle should take approximately 500 mµs, allowing 20 mµs for clock distribution skew. This means further that the master clock should operate at a frequency of four Mc and supply a symmetrical waveform, 125 mµs up and 125 mµs down, with a period of 250 mµs. The precise operating times will not be established until the system is completely assembled and tested.

**p. 25 (PDF 27), IC Controls:**
> The instruction counter controls consist of eight control stages for sequencing the fetching of instructions to the Y registers, checking-correcting them through the I checker, and advancing the IC register. There are thirteen supervisory control storage triggers to condition the sequences as to whether a fetch is in progress (outstanding), 1Y or 2Y is empty, ZL or ZR is empty, a branch to 1Y or 2Y is required, or a recovery is required. ... There are eight block-and-suspend triggers for instantaneously interrupting the normal IC operation to allow the I unit instruction execution controls use of the Y registers.

**p. 26 (PDF 28), Lookahead Load Controls:**
> The lookahead load controls consist of fourteen sequencers which regulate the loading of all I/O, VFL, and FP instructions into lookahead.
> Five of these deal solely with the loading of VFL instructions and are in the form of a five stage execution timer. Every VFL load begins with the first stage and may then step to any one of the remaining four, so that every VFL instruction requires anywhere from two to five steps. Each sequencer loads a different lookahead level so that a VFL instruction may occupy two to five levels. If an operand address refers to an index address, the sequence is broken in order to fetch the index from a common index fetch sequencer, and control is returned to the VFL load sequencers.
> There are two complete sets of four FP load sequencers for each half of the ZR.
> It was necessary to "guess" that the operand address referred to main memory, and begin the fetch immediately. If the guess is wrong, then the fetch is blocked and the next cycle is controlled by another sequencer which fetches the operand from the correct memory. The majority of FP instructions will require only one control step where the operand is fetched from main memory at the same time that the instruction is loaded into the single lookahead level.

**p. 28 (PDF 30), Floating Point Instruction Preparation:**
> It was decided to assume that the branch would not be successful, and if the assumption proves to be incorrect, then a recovery is made.
> A timing diagram showing the preparation of continuous FP instructions is shown in Figure 6. The preparation includes the fetching of instruction words from 2 µs memory, the ECC checking/correcting of the instruction, the Y to Z transfer and index fetch, the address modification, and finally the operand fetch and lookahead load. It can be seen how successive instruction fetches, preparations, and lookahead loads are overlapped to achieve a performance goal of one FP instruction every two cycles (one microsecond). Each instruction is assumed to require indexing. Otherwise instantaneous rates would achieve one FP instruction every half microsecond; the average rate, however, would still remain at one per microsecond. This is because the maximum rate of instruction fetches is balanced with the maximum indexing rate and the lookahead rates.
> Figure 6 starts out by assuming a start-up operation (either program start or recovery operation) where two rapid successive fetches are made by the IC

**p. 30 (PDF 32):**
> to the Y registers. When the words are received from memory they are immediately checked, and here we are assuming no errors so an extra correct cycle is not required. During the check cycle the ECC is converted to parity and the preparation controls pre-decode the type of instruction. In this case each word contains two FP instructions. The next cycle is the transfer from the left half of 1Y to the right half of Z. ... During this transfer, any addressed index word is fetched into the XR. Assuming that each instruction is to be indexed, the next cycle is the actual address modification. Here the index value in X is added through the index adder to the operand address in ZR. These last two cycles tied up the IAU so the next instruction in 1YR waited. The first instruction is now ready for loading into lookahead and fetching the operand. Since the IAU is not busy, we can also transfer the next instruction to Z and fetch its index word. So both operations are attempted. Since the 1Y register is now being emptied, the IC will try to fetch the next instruction word (IC + 3) into it. This conflicts with the operand fetch of the lookahead load cycle. Since IC controls have priority, the IC fetch is made simultaneously with the 1YR transfer to Z and the index fetch. The lookahead load cycle holds up its fetch during this cycle and completes it with the load operation on the following cycle, overlapped with the modification of the second instruction. This early instruction fetch guarantees that the 1Y register will be filled and checked by the time the 2Y register is emptied. In this manner the flow of instructions can be maintained. The degree of simultaneity in the I unit is best illustrated by the asterisked cycle which shows an instruction fetch to 2Y, a check cycle on 1Y, a 2 YR transfer to Z, an index fetch, and an attempted lookahead load, all occurring at the same time.
> The degree of overlap in the computer is best shown by the last cycle, which shows the execution of the first instruction E1, three of the four lookahead levels filled with instructions 2 and 3, instruction 4 being loaded into look-ahead and its operand being fetched, and instruction 5 being transferred from Y to Z and its index being fetched.

("(IC + 3)" is PRINTED as such.)

**p. 31 (PDF 33), VFL Instruction Preparation:**
> Before proceeding into the modification cycle, however, we must determine whether normal or progressive indexing is called for. This information is contained in the right half of the instruction, and is not available until the 2Y register has been filled, checked, and pre-decoded. In Figure 7, this is completed by the end of the 1YR to ZL transfer, so no wait is required. Assuming normal indexing, the next cycle is the modification cycle for the left half.
> After normal modification of the left half, the right half is transferred from 2YL to ZR and its index fetch executed. The next cycle then modifies the right half of the instruction.
> The word boundary cross-over test (WBC) is done by adding, in the index adder, the length field to the full 24 bit operand address field. If a carry into position 17 of the operand address field occurs, then the instruction operand does, in fact, cross memory word boundaries.
> This completes the preparation, and all that is left is to load the instruction into lookahead and fetch the operands. In this case three cycles are required. The first loads the instruction into one lookahead level. Since the data field is used for part of the instruction, no operand fetch can accompany this level. The next two cycles are for fetching the two operands of the instruction into two more levels of lookahead. The number of cycles required to load VFL type instructions varies from two to five, depending on whether the instruction [p. 33] requires one or two operands, whether it is a fetch or a store to memory instruction, and whether any special registers are implied in addition to the operand address.

**p. 33 (PDF 35):**
> It can be seen from Figure 7 that the VFL instruction in this case took eight cycles or 4.0 microseconds to prepare and load lookahead, as compared to two cycles or 1.0 microsecond for a normal FP. If the instruction had no indexing specified and only one operand memory word was required, the operation would have taken only five cycles or 2.5 microseconds.
> In the example, it is assumed that the instruction requires indexing, and therefore it is possible to overlap the operation decoding with the modification cycle. Otherwise it would have been necessary to take a separate decode cycle. ... The first cycle is a fetch of the index word whose count field will determine whether the branch is successful or not. In the next cycle, the fetch of the branch address instruction is initiated, and at the same time the count field of the index word in the XR is decoded for a XC = 1 condition. If this condition for branching exists, the fetch is completed; if the condition does not exist, the fetch is blocked. ... The instruction fetch is overlapped with the loading of the index word, before modification, into lookahead. This is referred to as a pseudo-store level, and is only used in recovery operations where the index registers have to restore to some previous level as a result of an interrupt or no-op condition. The next cycle then is the actual counting down through the index adder of the count field of the index word in the XR. After this, the value field can be advanced or diminished by one or one-half, if called for by the instruction. This is also effected through the index adder. At the same time, the advanced IC value (address of the instructions following the CB) is loaded into the same lookahead level as the pseudo-store. This is done because the next cycle destroys the IC contents by transferring into it the branch address from Z. If a no-op of this instruction is required, the I unit can continue on in the program. After the advance or diminish cycle, the updated index word is returned to XS. This is [p. 35]

**p. 35 (PDF 37):**
> done by a clear cycle for resetting the word during the same cycle that transfers the branch address into the IC. It is followed by a store cycle which sets the contents of the XR into the previously reset word in the array. To complete the operation, all indicators associated with this instruction and the new IC value are loaded into lookahead to be tested later in proper instruction sequence for an interrupt. If a condition occurred which would no-op the instruction, then the new IC field is not loaded, only the indicators and a no-op tag. This would cause any branching already done to be cancelled by a recovery operation later.
> Since the branch instruction was fetched early in the operation, the new instruction word has arrived and has been checked by the time the CB instruction is completely executed. The normal instruction preparation is restarted immediately and, in this case, the next FP instruction is loaded into lookahead four cycles later.
> The entire execution of the instruction took six cycles equal to 3.0 microseconds, and is overlapped with the operand fetch and execution of instruction 1. Another way of saying this is that it took ten cycles or 5.0 microseconds from the completion of one instruction in the program to branch to another program location, and to prepare and load the first new FP instruction into lookahead.
> As in the case of the count and branch instruction, the operation decoding is done in parallel with the indexing of the right half of the instruction, if called for. After decoding, the first cycle fetches the index word that contains the count of the number of words to be transmitted. Then the count field [p. 37]

**p. 37 (PDF 39):**
> is transferred through the index adder from the XR to the WR, where the counting and the test for W = 0 is performed. ... The left operand address (from) is used to fetch the first word into a Y register. Then, the from address is stepped (+1 or -1) through the index adder. The next cycle subtracts one from the count field in the WR and puts it back in W. A d-c detect circuit indicates in the following cycle whether the count went to zero. By then the fetched word has been received in the Y register and is immediately loaded into lookahead through the I checker, completing the ECC check. The ECC code is left with the word instead of converting it to parity, since lookahead will immediately attempt to store it to memory. When loading the word into lookahead, the "to" operand address in the ZR is gated to the memory address-bus (MAB). This, in turn, goes to the "effective address register for storing" in lookahead. So by the end of the cycle the level contains the word to be transmitted, the store memory address, as well as sufficient operation and indicator tags to tell lookahead what to do with them.
> After loading the store level, the "to" address in ZR is stepped (+1 or -1) and the operation is repeated for the next word. The loop continues until the count goes to zero. When this happens, the instruction execution is complete and a final lookahead level is loaded with the advanced IC value and any final indicators.
> It can be seen, from this example, that the rate of transmission is one word per five cycles or 2.5 microseconds. The initial set-up time took two cycles or 1.0 microseconds. This is only one of nine different variations of this instruction which can occur due to the combinations of the three different types of memory addresses in each of the two addresses. They all require a different sequence for execution, and therefore their transmission rates vary.
> The instruction is a branch on indicator, where the indicator specified is not an index result indicator. If it were, we would not have to guess but could test for the branch in the I unit's updated [p. 39]

**p. 39 (PDF 41):**
> indicator register. However, in this case the test cannot be made until all preceding instructions in lookahead have been executed and their indicators set. Rather than wait the I unit tests the instruction for certain indicator conditions and then loads it into lookahead. ... The I unit continues in the program, assuming that in the majority of cases the branch is unsuccessful.
> Once decoded, the actual execution sequence begins with a test fetch cycle. This is not an actual fetch, it merely places the branch address on the MAB for boundary compare purposes and the setting of possible indicators. Having determined whether the branch address is legitimate or not, the instruction is then loaded into lookahead.
> The loading is done in four steps and occupies four levels. The first is the instruction level with the operation codes and indicator address field, which tell the VFL unit what operation is required. The second cycle is the fetch level for fetching the indicator register to the lookahead level as the operand. The third level is a store to memory operand level with the store address of the indicator register. ... The fourth and final level is the recovery level which contains the branch address, the IC value, and various operation and indicator tags. This is in case the branch test proves successful and a branch recovery operation is required. If that happens, the branch address is returned to the IC and all intervening operations are cancelled.
> In the example, the branch is assumed unsuccessful and the I unit continues with the preparation of the following instruction (I6). It can be seen that the actual execution of the instruction took five cycles or 2.5 microseconds.

---

##### 3. Illegible / uncertain
- No cell in Figs 6-10 is illegible. Uncertain readings: Fig 6 c11 "MOD ZL" (printed, probably should be ZR);
  Fig 8 c9 "XF/-1YL" stray mark; Fig 9 MAB two labels on one unticked 2-cycle bar (split DERIVED).
- Cycle numbering (c1..cN) is DERIVED from tick pitch; the figures print no cycle numbers.
- p. 16 I-checker sentence begins on p. 15, which was not read.
