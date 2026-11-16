> **STATUS: UNVERIFIED FINDING AID.** Written by reading agents on 2026-11-16
> from page images of R23-9732 (7101), PDF 63-91. Nothing here may be cited
> as a source: every quote must be re-read in the ink before it is relied on,
> as AGENTS.md requires. Load-bearing boxes on PDF 52-53, 77, 84, 88 and
> 91 (upper half) were re-read by the agent at 200 dpi; the rest is single-read.

# Reading notes: R23-9732 (7101 CPU CE Reference Manual, Jan 63) -- I UNIT FLOW DIAGRAMS, Figs 3.1.x

Source: `stretch/docs/R23-9732_Manual04_7101_CPU_Jan63.pdf`. Page IMAGES only, rendered with `pdftoppm -r 200 -gray`,
rotated upright, cut into tiles under ~1900 px, with 300-700% crops wherever there was doubt. `docs/ocr/` was used
only to locate pages, never as a source of text. Nothing in the repository was modified.
Companion: `notes_7101_memory_lookahead.md` (Part B: LA flow diagrams, Figs 3.2.x, PDF 92-119).

Method note: five readers transcribed the 29 pages in parallel from the same tiles. Their full transcriptions are
Appendices A-E below, unedited. **The coordinator re-read the load-bearing boxes against the page images**, as follows:
PDF 52-53 (list of illustrations); PDF 63 (seen once whole, rotated and resampled: box texts consistent with App. A,
overbars NOT checked); PDF 77 at 200 dpi crop (ZOAR EQ / STORE WAIT / IRCY / PROGRAM STORE COMPARE / SET LA EXT-INT
STORE TAG cluster); PDF 84 at 200 dpi (the same cluster, Fig 3.1.20); PDF 85 at ~110 dpi whole page (ZOAL EQ cluster:
box texts and ALDs legible, overbars not checked); PDF 88 at 200 dpi (W EQ 11 + 12 + 16 - 31 -> VFL 5 CL 2 COND STORE
WAIT); PDF 91 upper half at 200 dpi (FULL WORD TGR, ZEDEC 25 ... -> COND LOP 3 TON / GT ZR J FLD TO LA ON LOP 3 /
ZXAB TO LAOC, BR + SIC-BR, BI+SIC-BI, COND STORE WAIT). PDF 76 and everything else are single-read. Everything else in the appendices is single-read and is
for a second reader to check. Each appendix ends with its reader's "Not read with confidence" list.

Notation (all appendices): `~X` = overbar printed over X; `•` = AND dot as printed; hex = hexagon (condition);
box = rectangle (action); numbers in parentheses are ALD logic pages. TON / TOF = turn on / turn off, as printed.

---------------------------------------------------------------------------------------------------------------

## 1. Where the section is, and every figure

Section M3-04-3 "I UNIT FLOW DIAGRAMS": **first page PDF 63, last page PDF 91** (PDF 92 begins "LA FLOW DIAGRAMS").
Running head on every page: "M3-04-3" / "I UNIT FLOW DIAGRAMS". All pages are printed sideways and are read rotated.
Nearly every page carries "CPU 7101 / SER. NO. 30,004 / AND HIGHER" (exceptions: Fig 3.1.13 sheets 1-3 and Fig 3.1.21,
where no note was seen).

The list of illustrations (Index 3-2, PDF 52-53; all issue dates 1/1/63 there) names 3.1.1-3.1.28. Captions below
are **as printed on the figure pages**. Where the index title differs, it is noted.

| Fig | Caption as printed on the page | PDF | printed tag | date |
|---|---|---|---|---|
| 3.1.1 | IF 1Y SEQUENCER | 63 | 1-1/1-2 | 2/1/62 |
| 3.1.2 | IC 1Y TRIGGERS AND IWC1 SEQUENCER | 64 | 1-3/1-4 | 2/1/62 |
| 3.1.3 | IF 2Y SEQUENCER | 65 | 1-5/1-6 | 2/1/62 |
| 3.1.4 | IC 2Y TRIGGERS AND IWC2 SEQUENCER | 66 | 1-7/1-8 | 2/1/62 |
| 3.1.5 | IC ADV SEQUENCER AND ICOR SEQUENCER | 67 | 1-9/1-10 | 2/1/62 |
| 3.1.6 | Y-Z START TRIGGER AND YR-ZL TRANSFER SEQUENCER | 68 | 1-11/1-12 | 2/1/62 |
| 3.1.7 | YL-ZR TRANSFER SEQUENCER | 69 | 1-13/1-14 | 2/1/62 |
| 3.1.8 | YL-ZL TRANSFER SEQUENCER | 70 | 1-15/1-16 | 2/1/62 |
| 3.1.9 | YR-ZR TRANSFER SEQUENCER (see App. B) | 71 | 1-17/1-18 (see App. B) | 2/1/62 |
| 3.1.10 | ZR MOD REQ TRIGGER AND MOD ZR SEQUENCER | 72 | 1-19/1-20 | 2/1/62 |
| 3.1.11 | ZR BLOCK AND SUSPEND TRIGGERS | 73 | 1-21/1-22 | 2/1/62 |
| 3.1.12 | ZR FP 1 TRIGGER | 74 | 1-23/1-24 | [2?]/1/62 |
| 3.1.13 | ZR FP TRIGGERS 2, 3, 4, AND 6 (SHEET 1 OF 3) | 75 | 1-25 | 2/1/62 |
| 3.1.13 | ... (SHEET 2 OF 3) | 76 | 1-26 | 2/1/62 |
| 3.1.13 | ... (SHEET 3 OF 3) | 77 | 1-27/1-28 | 2/1/62 |
| 3.1.14 | ZR IHW TRIGGER, IHW RDY TRIGGER, AND IHW EX ZR TRIGGER | 78 | 1-29/1-30 | 2/1/62 |
| 3.1.15 | ZL MOD REQ TRIGGER AND MOD ZL SEQUENCER | 79 | 1-31/1-32 | 2/1/62 |
| 3.1.16 | ZL BLOCK AND SUSPEND TRIGGERS | 80 | 1-33/1-34 | 2/1/62 |
| 3.1.17 | ZL DEC TRIGGER (index: "ZL Dec Trigger ON") | 81 | 1-35/1-36 | 2/1/62 |
| 3.1.18 | ZL FL PT TRIGGER AND ZL FP 1 TRIGGER | 82 | 1-37/1-38 | 2/1/62 |
| 3.1.19 | ZL FP2 TRIGGER | 83 | 1-39/1-40 | 2/1/62 |
| 3.1.20 | ZL FP3 TRIGGER | 84 | 1-41/1-42 | 2/1/62 |
| 3.1.21 | ZL FP4 TRIGGER AND ZL FP6 TRIGGER | 85 | 1-43/1-44 | 2/1/62 |
| 3.1.22 | ZL IHW TRIGGER, ZR WAS IHW TRIGGER, 1 BIT MOD TRIGGER, AND FP Z ALT TRIGGER | 86 | 1-45/1-46 | 2/1/62 |
| 3.1.23 | WBC + DEC SEQUENCER AND XF + DEC SEQUENCER | 87 | 1-47/1-48 | 2/1/62 |
| 3.1.24 | WBC TRIGGER (the bar on the page reads "WORD BOUNDRY CROSSOVER TGR (28.22.02.1)") | 88 | 1-49/1-50 | 2/1/62 |
| 3.1.25 | FW NOT S TRIGGER | 89 | 1-51/1-52 | 2/1/62 |
| 3.1.26 | FWS TRIGGER | 90 | 1-53/1-54 | 2/1/62 |
| 3.1.27 | FW TRIGGER | 91 | 1-55/1-56 | **1/1/63** |
| 3.1.28 | (index: "ZL DEC Trigger OFF") | **not found** | | |

**Fig 3.1.28 is listed in Index 3-2 (PDF 53) but no page in PDF 63-91 carries it**; PDF 92 is Fig 3.2.1. Either it was
never issued in this copy or it was lost in scanning. Only "COND ZL DEC TON CKT (28.27.30.1)" (Fig 3.1.22) mentions
ZL DEC on the remaining pages.

**Timing material:** none. No page in 63-91 prints a duration, a cycle count or a timer value. These are trigger
turn-on / turn-off condition charts. The sequencer bars have outputs labelled `E`, `E•M` / `EM`, `M` (and once
`E • ~M`), and those are overlapping trigger states, not cycles. Section 3.8 has FP *timing* figures (3.8.1-3.8.20,
"(TIMING)") for the E-box. They are outside this task and were not read here. The OCR of the remaining
list-of-illustrations pages (PDF 54-60) is too degraded to use even as a locator, and those pages were not read as
images. So an I-unit or index timing chart elsewhere in the manual is NOT ruled out. The OCR's figure captions found
none outside 3.8 (FP) and 3.11 (VFL).

Vocabulary as it appears (expansions are NOT printed on these pages; any gloss here is mine and marked so):
1Y / 2Y = the two instruction buffer registers. YL / YR = left / right half of a Y word. ZL / ZR = the two
instruction-preparation (Z) registers, left / right half-word [my gloss]. IF1Y / IF2Y = instruction fetch to 1Y / 2Y.
IC = instruction counter. ICA / ICR = [IC address / IC return?]. MOD = address modification (indexing) [my gloss].
XF = index fetch [my gloss]. XAB = index address bus [my gloss]. XS = index storage [my gloss]. XAC = [index
adder?]. FPL n / FPR n = FP look-ahead load step n, left / right [my gloss]. LAOC / LAOP = look-ahead op code
(field / tag). SBC, SAC, SAR, SABR = [not expanded on these pages].

---------------------------------------------------------------------------------------------------------------

## 2. Synthesis by question (printed text quoted; my reading marked "MY READING")

### 2.1 Instruction fetch into 1Y/2Y and the program-store compare

- Fig 3.1.1 (PDF 63, verified): turn-on hexes of "INSTRUCTION FETCH 1Y SEQUENCER (28.41.21.1)" are
  "NORMAL FETCH ANTICIPATED ON ACCEPT", "ANTICIPATED NORMAL FETCH", "NORMAL FETCH", "RECOVERY OPERATION"
  (all 28.41.21.1). On the EM output: hex "NORMAL FETCH ~SUSPENDED (28.41.22.1)" -> "IF1Y FETCH REQ TO BCU (28.44.11.1)".
  Then hex "ACCEPT OR COMPARE PRESENT (28.41.23.1)" -> "TURN ON ICFO1Y TGR (28.41.23.1)". Then "REPEAT INSTR + MAB EQ
  AD 1" -> "TURN ON ICBC1Y TGR". The address source on the E output is "GATE ICA 0-16 TO MAB" (NORMAL ADVANCE)
  or "GATE ICR 0-16 TO MAB" (RECOVERY • ~REPEAT • ~SUSPEND), both (21.03.01.1), or "GENERATE ADR 4 (28.21.10.1)"
  (REPEAT INSTR • ~SUSPEND). The overbars on PDF 63 are as Appendix A gives them.
- The M output ends instruction fetch with hex "SABR • ~SUSPEND ~(IF1Y LTH) • ACCEPT OR COMPARE" -> "TURN OFF IF1Y E TGR".
  "COMPARE" here is the BCU's address compare, i.e. the fetch is satisfied by a pending store. MY READING; the page
  does not expand it.
- From the EM output, the hex "IF1Y E o M LTH + IF2Y E o M LTH (28.41.21.1)" fans out to "TO LA LD SEQ VFL2..VFL5,
  FPL4, FPL3, FPR4, FPR3, FPDD" and "TO FLLI TON CKT". The look-ahead load sequences are conditioned on the
  instruction-fetch latches.
- **Program-store compare** (a store into the instruction stream) appears on the store-preparation side, not on the
  fetch side. It is drawn identically on ZR (Fig 3.1.13 sh.3, PDF 77, verified) and ZL (Fig 3.1.20, PDF 84, verified;
  Fig 3.1.21, PDF 85):
  hex "PROGRAM STORE COMPARE" (28.42.71.1) --YES--> "TON PIRCY TGR" (28.42.71.1);
  hex "PROGRAM STORE COMPARE" (28.42.72.1) --YES--> "TON IRCY REQ TGR" (28.42.72.1).
  Under "FPR3E AND NO CANCEL" (28.14.33.1) there is also hex "PROGRAM STORE COMPARE. ACCEPT OR COMPARE" (28.42.72.1)
  --YES--> "TON IRCY REQ TGR" (28.42.72.1) (PDF 77, verified). ["PIRCY" prints as one word; P I RCY not decided.]

### 2.2 Index fetch, address modification, and when the effective address is formed

- **Index fetch**: Fig 3.1.23 "XF + DEC SEQUENCER (28.15.50.1)" (PDF 87, App. E). On the E output:
  "NOT 1 BIT MOD RQD" -> "GT Z 28-30 TO XAB 1-3 (28.27.52.1)"; "1 BIT MOD R T" -> "GT Z 31 TO XAB 4 (28.27.52.1)",
  "XS READ P (24.00.09.1)", "BLOCK GEN OF INH NIDC SET IDC FR XAC (28.27.31.1)". Also "XF + DEC M TGR OFF" with
  "E • ~M" -> "PREP RST X 0-63 (28.86.57.1)". The same "GT 1Y/2Y 28-30 TO XAB 1-3" / "GT 1Y/2Y 31 TO XAB 4" /
  "XS READ P" boxes appear in the Y->Z transfer sequencers (Figs 3.1.6-3.1.8, App. B). There the index address is
  gated straight from the Y register during the Y->Z transfer, and full-word forms use "GT 1Y 60-63 TO XAB 1-4"
  (Fig 3.1.6).
- **All three XF + DEC turn-on hexes require "~(BLOK XF + DEC)"** (28.15.50.1). "BLOCK XF + DEC TON (28.15.50.1)" is
  an output of Figs 3.1.14 and 3.1.15 (App. C). Nothing on PDF 63-91 shows a look-ahead-level or index-store
  condition setting it. Its setters are the IHW / MOD ZL triggers drawn there.
- **Address modification** (the "MOD" sequencers): Fig 3.1.10 "MOD ZR SEQUENCER (28.15.20.1)" (PDF 72) and Fig 3.1.15
  "MOD ZL SEQUENCER" (PDF 79). Their E outputs gate the index word and the Z address into the adder: "X 0-23 to ABB
  • X 24-27 to ABB (28.96.01.1)", "Z 32-49 to ABB 0-17 PREP", "Z 0 - 17 ABB PREP", "HOT 1 TO ABB P 2". The E•M output
  returns the sum: "GT AOB 18 to ZR (28.27.51.1)", "GT AOB 19 to ZR". "ABB"/"AOB" are the adder's in/out buses
  [my gloss]. The M output gives "PREV ZR PREP COMP (28.44.25.1)", "INSTR PREP COMP ZR (28.27.32.1)".
- **Order relative to loading a level.** The FP load triggers (ZR/ZL FP 1-6, Figs 3.1.12-3.1.13, 3.1.18-3.1.21) are
  gated by "ZR/ZL INSTR PREP COMPL(ETE)". Fig 3.1.20 has "ZL INSTR PREP COMPL• (28.13.41.1)" -> "COND FPL 4 TON CKT",
  and the operand address goes to memory from the prepared Z register: "Z 0 - 17 TO MAB (28.21.60.1)" under
  "FPL 4 E TGR ON", and "Z32-49 TO MAB" on ZR. "INSTR PREP COMPL" is produced at the M output of MOD ZR / MOD ZL.
  **MY READING:** the effective address is formed by MOD Z before the level-load steps (FPL/FPR 3-4, "TYPE 3 LOAD TO
  LA", "T3 LD TO BCU WAIT FOR ACCEPT"), which send the already-modified Z address to MAB/BCU. This agrees with the LA
  pages (no address field in a level). It is a structural inference; no box states it.

### 2.3 A store INTO an index word (or word 11 / 12) by an instruction being loaded: STORE WAIT + I RECOVERY

**The central finding.** It is drawn three times for FP stores and twice for VFL stores. The coordinator verified it
in the ink on PDF 77, 84 and 88.

- FP, right half-word (Fig 3.1.13 sheet 3, PDF 77, verified):
  hex "ZOAR EQ 11 +12 + 16 - 31" (28.42.51.1) --YES--> "TON STORE WAIT TGR" (28.42.51.1) and "TON IRCY REQ TGR"
  (28.42.72.1). It sits on the line that also carries the two "PROGRAM STORE COMPARE" hexes. Per App. C that line
  is the YES of "FPR4E" (28.14.43.1). (Sheet 2, PDF 76, has the same hex with no ALD number printed.)
- FP, left half-word (Fig 3.1.20, PDF 84, verified):
  hex "FPL 4 E TGR ON (28.13.43.1)" --YES--> a bus carrying "PROGRAM STORE COMPARE (28.42.71.1)" -> "TON PIRCY TGR";
  "PROGRAM STORE COMPARE (28.42.72.1)" -> "TON I RCY REQ TGR"; and
  **hex "ZOAR EQ 11 + 12 + 16 - 31 (28.42.51.1)" --YES--> "TON STORE WAIT TGR (28.42.51.1)", "BLOCK STORE WAIT TGR
  TOF (28.42.51.1)", "TON I RCY REQ TGR (28.42.72.1)"**.
  Fig 3.1.21 (PDF 85, App. D, not re-verified) prints the same with "ZOAL EQ 11+12+16-31" and without the BLOCK ... TOF box.
- VFL (Fig 3.1.24 WBC TRIGGER, PDF 88, verified):
  hex "W EQ 11 + 12 + 16 - 31 (28.11.55.1)" --YES--> hex "VFL CL 2 • VFL 5E (28.11.55.1)" --YES--> box
  "VFL 5 CL 2 COND STORE WAIT (28.21.71.1)". App. E reads a second copy on the same page as "ZL 11 + 12 + 16 - 31" ->
  "VFL C2 • VFL 5E" -> "VFL 5 CL 2 COND STORE WAIT". Fig 3.1.27 (PDF 91, verified in the upper half) has
  "VFL 5 (28.11.55.1)" --YES--> "COND STORE WAIT (28.21.71.1)".
- What the condition tests (MY READING): "ZOAR/ZOAL" = a Z operand address; "W" = the register used for VFL addresses.
  A left/right reading of the R/L is NOT safe: Fig 3.1.20, a ZL figure, prints "ZOAR" (PDF 84, verified), while Fig
  3.1.21 prints "ZOAL" (PDF 85, verified at low resolution). The equality is with **word 11, word 12, or words 16-31**. By the 7030 address
  map those are the indicator register (11), the mask register (12) and the sixteen index registers (16-31). The page
  does not name them. The ALD 28.42.51.1 is the same for the hex and both STORE WAIT boxes.
- **The printed fact is narrow:** the turn-on of STORE WAIT TGR and I RCY REQ TGR depends on the instruction's own
  address and on the load step (FPL/FPR 4 E, VFL 5E / VFL CL 2). No box compares it with a later instruction's index
  field. MY READING (that FPL/FPR 4 and VFL class 2 are the store steps is itself inference from "SET LA EXT/INT
  STORE TAG" sitting on the same steps): when the I box prepares a
  STORE (FP store at the FPL/FPR 4 step, VFL class 2 at the VFL 5 step) whose address is an index register (or
  11/12), it turns on STORE WAIT and requests an I-unit recovery ("TON I RCY REQ TGR").
  MY READING, consistent with Fig 3.2.27 on the LA pages ("STORE DATA FOR IX STORAGE ?" -> SCC -> "SIGNAL I BOX TO START
  THE INDEX STORAGE CLEAR/STORE OPERATION"): the I box stops preparing, the store goes down the look-ahead and is
  written to index storage by the SCC, and the I unit then recovers (re-prepares from the instruction after the
  store) with the new index value.
  **What resets STORE WAIT TGR, and exactly what it blocks, is NOT on PDF 63-91.** No box anywhere in Figs 3.1.1-3.1.27
  takes "STORE WAIT" as a condition, and none of the IF/IC sequencer hexes names it. Its turn-off and effect are on
  ALD 28.42.51.1. "I RCY" is likewise only turned on here.
  The two "SUSPEND" trigger figures (3.1.11, 3.1.16) are gated by branch/IC conditions ("BR Y-Z XFER TON ZR SPND",
  "TON SUSPEND TGR • SBC"), not by STORE WAIT.
- **"INDEX STORE TAG" does not appear on PDF 63-91.** The store tags the I box sets are "SET LA EXT STORE TAG" and "SET
  LA INT STORE TAG" (36.09.14.1 / 36.09.15.1 / 28.24.82.1). Their gates are "ZR/ZL EXT LTH • FPR/FPL 4E" and
  "ZR/ZL INT LTH • FPR/FPL 4E", plus "ZL INT + ZL ADR 8 • FPL4E" and "ZR ADR 8 LTH • FPR2E" variants (PDF 77 and 84
  verified for the EXT/INT pair). So an index-word store is an INT (internal-address) store level, plus the STORE WAIT
  / I RCY REQ above. The LA-side "INDEX STORE TAG" (Table 3.4.1, 36.09.19.1) is set elsewhere.
- **The words "pseudo store", "PS", LAOP 02/04/06 and "index recovery" appear nowhere on PDF 63-91. But Fig 3.1.27
  (PDF 91, verified) has the I box putting an index (J) address into a look-ahead op code:**
  hex "ZEDEC 25 • ZEDEC ~26 • ~27 • 28 (28.61.71.1)" --YES--> "COND LOP 3 TON (28.88.21.1)", "COND ICLI TON
  (28.84.11.1)", "BLOCK LAOC 9 ON LOP 3 (28.88.26.1)", "GT ZR J FLD TO LA ON LOP 3 (28.88.25.1)", and hex "LOP 3 • USE
  ZL (28.88.25.1)" --YES--> "GT Z 18 - 23 TO XAB (28.95.11.1)", "ZXAB TO LAOC (28.97.03.1)". The same figure has
  "BB SIG TO SLLI STORE LEVEL LALD OUT CKTS (28.79.43.1)", "COND XSFI TON CKT (28.70.41.1)" / "TOF CKT (28.70.43.1)"
  and "BLOCK LOP 4 TON"; Fig 3.1.14 has "COND LOP 4 / 5 TON CKT", "COND XSF3 TON CKT (28.71.11.1)" and "COND EMF1/EMF5,
  DEC 3/4, ADD 1/3 TON CKT".
  **MY READING:** "LOP n" are I-box execution steps of an instruction, and "XSF n" / "EMF n" / "ADD n" / "DEC n" are
  further I-box execution sequencers (index store/fetch, ...). They are only *conditioned* here; their own charts are
  not in Figs 3.1.x. The LA pages say a pseudo-store level carries "OP CODE BITS 1-4 ... (IX ADDR)" (Fig 3.2.27), so
  "GT ZR J FLD TO LA ON LOP 3" / "ZXAB TO LAOC" is very likely the I-box end of loading that level. Which instructions
  ZEDEC 25•~26•~27•28 decodes is not printed. Fig 3.1.17's ZEDEC boxes route 23, 24, 26 (and one unnumbered) "TO
  DIRECT IX INSTR DEC CKTS" (App. D, single-read). So whether this is the pseudo-store path of the direct-index
  instructions is a strong lead, not a reading. The execution sequencers' own flows (LOP 3-5, XSF, EMF, ADD) are
  **not in this section**.

### 2.4 Branches in the I box

- Fig 3.1.27 (PDF 91, verified): hex "BR + SIC-BR (28.61.72.1)" --YES--> hex "LAMIE • LARCY MD (28.81.15.1)" --YES-->
  "HOT 1 TO ABA 17 (28.96.41.1)". Hex "BI+SIC-BI (28.61.72.1)" --YES--> hex "E BOX IND (28.61.72.1)" --YES--> hex
  "~ZLXA • BROK (28.61.73.1)" -> "BLOCK SET OF LAOC 8 (28.97.04.1)"; and "~(E BOX IND) • ~BROK" -> "SET LAOC 0,5 ON
  LOP 3 (28.88.25.1)".
  The overbar readings are App. E's; I did not re-check the bars. **MY READING:** "E BOX IND" separates branches on an
  indicator the E box sets (these go to the look-ahead as a branch level, LAOC 8 ...) from indicators the I box owns.
  This matches the model's arithmetic-indicator vs index-indicator split. The page prints no word "guess".
- Fig 3.1.14 (PDF 78, App. C): hex "EX + RN (28.89.32.1)" --YES--> "ALLOW LARCY TON (28.42.81.1)"; hex "BE + BEW + BD +
  SIC-BE-BEW-BD (28.89.32.1)" --YES--> "ALLOW LARCY TON (28.42.81.1)". "LARCY" = look-ahead recovery [my gloss]. So
  EXECUTE, RN, and the enabling/disabling branches BE, BEW and BD (and their SIC forms) are the instructions that allow
  a look-ahead recovery.
- Figs 3.1.10, 3.1.6-3.1.8, 3.1.15 MOD-request hexes carry branch-decode terms ("BRC • UNCOND + BIT", "BR CL IYL + BIT
  BR DEC", "IYLD BRU + BRC"). Figs 3.1.11 / 3.1.16 suspend fetch on "BR Y-Z XFER TON ZR SPND IY • SBC" (PDF 73). That
  hex's ZR SPND TGR output is a column of "BLOCK IF1Y ..." / "BLOCK GT OF ICR 0-16 TO MAB" / "BLOCK GEN OF IF1Y
  RETURN ADR" boxes. MY READING: on a branch's Y->Z transfer the I box suspends the sequential instruction fetch.
- Fig 3.1.27 (PDF 91, verified) also has the branch level's IC: hex "RLL I E • M TGRS ON (28.79.54.1)" --YES--> "GT IC
  FLD (28.79.64.1)"; hex "RLL I E • M TGRS ON (28.79.53.1)" --YES--> "GT ICA 17 • 18 TO LA"; on the BI path "COND RLLI
  TON (28.79.52.1)", "BLOCK LA IC TAG SET (28.79.53.1)"; also "RLLI E • USE ZR/ZL" -> "END EX ZR/ZL (28.79.63.1)".
  MY READING: the instruction counter is gated into the look-ahead level ("LA IC TAG"), which is where the LA side's
  "BR. RECOV" level gets its return address. "RLLI" is not expanded on the page.
- **Housecleaning / recovery from the I-box side** appears only as the turn-on "RECOVERY OPERATION" of IF 1Y and
  "GATE ICR 0-16 TO MAB" under "RECOVERY • ~REPEAT • ~SUSPEND" (Fig 3.1.1). No HSCLN box is on PDF 63-91.

### 2.5 Updated indicator register

Nothing on PDF 63-91 shows an "updated indicator register" as such. Word 11 appears only in the store-wait compare
(§2.3). "SET LA AD", "SET LA DS", "SET LA DF", "...LANOP" (Figs 3.1.20-3.1.21) are look-ahead level tags set at
preparation for the address-, data-store- and data-fetch-related alarms [my gloss]. They are not an indicator copy.
**Not found.**

### 2.6 Cycle counts / timer durations

None printed (see §1).

---------------------------------------------------------------------------------------------------------------

## 3. Comparison with the model (line numbers taken 2026-11-16 in this worktree)

Files: `stretch/bsv/StretchIBox.bsv`, `stretch/bsv/StretchCore.bsv`, `stretch/bsv/StretchTiming.bsv`.

M1. **The model waits for an index-word store only when the new level is indexed by that register. The 7101 turns on
    STORE WAIT TGR and I RCY REQ TGR for every such store-step instruction whose address is 11, 12 or 16-31, whatever
    follows** (printed). That the trigger stalls the I box is my reading of its name; its effect is not drawn. `StretchCore.bsv:1446-1451` (`indexStorePending`): a new E-box
    level waits only if a pending level's `storeAddr` is word 16+j AND `usesIndex(di, j)`. The diagrams turn on STORE
    WAIT TGR and I RCY REQ at preparation of ANY FP store (FPL/FPR 4) or VFL class-2 store (VFL 5) to ZOA/W = 11, 12,
    16-31 (PDF 77, 84, 85, 88). The trigger keys on the store's address alone, with no test against the next
    instruction's index field. MY READING: the hardware therefore waits (and recovers) more broadly, also for
    stores to the indicator (11) and mask (12) words. The model has no counterpart for a store to 11/12. The model does cover E-box reads of
    words 7-15 through `eboxRegister` in the `waitFor` logic, `StretchCore.bsv:1513-1521`, and
    `iboxHazard`'s `eboxRegister(ea)` for I-box operands.
    Caveat: what releases STORE WAIT, and whether it stalls only preparation or also fetch, is not on these pages. A
    measured stall length cannot come from here.

M2. **Possible gap: an I-box instruction that reads Xj after a pending E-box store to word 16+j.** `iboxHazard`
    (`StretchIBox.bsv:338-420`): the ImmIndex arm (`:365-368`) and the CountBranch arm (`:369-372`) test
    `progressiveWrites` and `levelIndexedBy`. Neither tests a pending level whose `storeAddr` is 16+j. The DirIndex
    arm (`:342-364`) tests `levelHolds(lv, ea)`, which is the OPERAND word, not register J.
    In the 7101 the store sets STORE WAIT at its own preparation, so no later instruction can be prepared against the
    stale register. A sequence such as "ST(BU,64),$X9-word" then "V+I,$9,1" looks unprotected in the model, unless
    `StretchStorage`'s index-word write path orders it some other way. **I did not test this; it is a lead, not a
    finding.**

M3. **`levelIndexedBy` / `levelIndexedByWord` (StretchIBox.bsv:314-325, used at :362-363, :368, :372, :384, :397, :416).**
    The I box writing Xj waits while a pending level is indexed by Xj. **No such wait is shown on PDF 63-91**, but the I-box index-write execution flows
    are not in this section either (§2.3), so this is "not shown", not "absent": the XF +
    DEC and MOD sequencers have no condition on look-ahead levels, and their only block is "~(BLOK XF + DEC)", set by the
    IHW/MOD ZL triggers.
    The diagrams form the effective address in MOD Z before the level is loaded and send it to MAB/BCU from Z (§2.2).
    Structural inference: a later index change could not move an already-loaded level's operand, which points
    to the wait having no hardware counterpart. That agrees with the model's own comment at StretchIBox.bsv:297-300 and with the LA notes C.b.3. The I-box-side
    pseudo-store mechanism that makes the change recoverable is not drawn in this section (§2.3).

M4. **`progressiveWrites` (StretchIBox.bsv:260-273) and `progressivePending` (StretchCore.bsv:1414-1416, used at :1451,
    :1537).** Nothing on PDF 63-91 mentions progressive indexing, so no diagram backs or contradicts these waits.
    Progressive indexing writes an index register from an E-box (VFL) level, so §2.3's STORE WAIT is the nearest drawn
    mechanism. The VFL store-wait compare tests W, the operand address, not the progressive index's J. **Not shown on
    these pages.**

M5. **Branch guess (StretchCore.bsv:1530-1545).** The model loads a branch level for an arithmetic-indicator branch,
    snapshots `xSnap`/`indSnap`, sets `guessPending`, and allows one guess at a time.
    Fig 3.1.27 shows the I box splitting BI on "E BOX IND" and setting LAOC codes for the level. That supports
    "E-box-indicator branches become a look-ahead level". The snapshot, the "one at a time" limit and "not taken" are
    not drawn here. The recovery side is "ALLOW LARCY TON" for EX, RN, BE, BEW, BD, SIC-B* (Fig 3.1.14), plus IF 1Y's
    "RECOVERY OPERATION" / "GATE ICR 0-16 TO MAB". **A snapshot of index registers is not shown on these pages**; On the LA
    pages recovery restores them from pseudo-store levels instead.

M6. **`iboxCycles` (StretchTiming.bsv:76-100) and `ibusy <= 2 * iboxCycles(di, False)` (StretchCore.bsv:1528).** These
    PDF pages give no numbers to check them against. They neither confirm nor contradict any count. The constants keep
    their existing (Blosk / Perf. Char.) citations.

M7. **Unconditional-branch drain (`iboxHazard` BranchOrMisc arm, StretchIBox.bsv:374-380).** Fig 3.1.14 lists BE, BEW
    and BD with EX and RN as the "ALLOW LARCY" instructions. That is consistent with these instructions disturbing the
    look-ahead, but it does not show a drain. **No wait is drawn on these pages for this case.**

---------------------------------------------------------------------------------------------------------------

## 4. Passages not read with confidence (summary; full lists end each appendix)

- Overbars inside multi-line hexagons throughout. A rule between two text lines is assigned to the line below by
  convention. The big MOD-request turn-on hexes (Figs 3.1.6-3.1.10, 3.1.15) and all "~(BLOK XF + DEC)" readings except
  the left XF hex depend on this.
- "1Y" vs "IY", "I" vs "1" in IRCY/1RCY/PIRCY/P1RCY, XOF1/XOFI, IWC1/IWCI. "PIRCY" is one printed word; its
  meaning is not decided.
- Fig 3.1.21 (PDF 85): "ZOAL" vs Fig 3.1.20's "ZOAR". Both were read at zoom by App. D's reader, and the coordinator
  re-checked p84 ("ZOAR"). Not re-checked on p85.
- Fig 3.1.20 hex "[FDL? / FPL] 4 E • FPL 4 M" on the page fold, PDF 84.
- Fig 3.1.17 (PDF 81): the second line of "ZEDEC 19 TO I BOX [...]" is obliterated by the fold.
- Connections across tile boundaries on PDF 85, 87, 91 are best-effort, and a "connection not followed" note marks
  each such place.

---------------------------------------------------------------------------------------------------------------

# APPENDIX A -- reader transcription

# Part a: PDF pages 63-67 (Figs 3.1.1 - 3.1.5), R23-9732 I UNIT FLOW DIAGRAMS

Conventions: `~X` = overbar printed over X; `•` = printed AND-dot; hex = hexagon (condition); box = rectangle (action).
"rail" = the vertical line leaving the sequencer bar at the named output. A "dot" is a printed junction dot.

---------------------------------------------------------------------------------------------------
## FIGURE 3.1.1. IF 1Y SEQUENCER   (PDF page 63)

Header (margin strings as printed):
- Caption: "FIGURE 3.1.1. IF 1Y SEQUENCER"
- Page tag: "1-1/1-2"
- Date: "2/1/62"
- Other margin strings: "M3-04-3" ; "I UNIT FLOW DIAGRAMS"
- Applicability note (printed inside the drawing area): "CPU 7101 / SER. NO. 30,004 / AND HIGHER"

### Turn-on conditions (hexagons above the bar)
Four hexes, each with a YES exit; the four YES lines join one horizontal line (junction dots) which drops
into the bar through a line labelled "TURN ON IF1Y".
- hex: NORMAL FETCH / ANTICIPATED ON / ACCEPT (28.41.21.1) --YES-->
- hex: ANTICIPATED / NORMAL FETCH (28.41.21.1) --YES-->
- hex: NORMAL FETCH (28.41.21.1) --YES-->
- hex: RECOVERY / OPERATION (28.41.21.1) --YES-->
    --> line label "TURN ON IF1Y" -->

### Bar
INSTRUCTION FETCH 1Y SEQUENCER (28.41.21.1)
Outputs printed under the bar, left to right: E , EM , M

### Output E (leftmost rail, runs the full height of the figure)
Boxes hung directly on the E rail (each by a junction dot, boxes to the left of the rail):
- box: TURN OFF IF2Y / MI TGR (28.41.31.1)        [uncertain: "MI" may be "M1"; reads as letter I]
- box: TURN OFF IC ADV / M TGR (28.41.41.1)
- box: TURN OFF 1Y MT / TGR (28.42.11.1)
- box: TURN OFF RST 1 / M TGR (28.41.11.1)
From the same junction dot as TURN OFF RST 1 M TGR a line goes right to:
- hex: IF1Y M / TGR OFF   (no ALD number printed)
    exit labelled "YES" with "E • ~M" printed directly under the YES (overbar over M)
    --YES--> a vertical distribution line with junction dots, feeding (left column | middle column):
        - box: BLOCK IF1Y E / TURN ON (28.41.23.1)
        - box: BLOCK ICFO2Y / TURN ON (28.41.23.1)
        - box: BLOCK IF2Y E / TURN OFF (28.41.31.1)
        - box: BLOCK ICBC2Y / TURN ON (28.41.33.1)
        - box: BLOCK ICADV E1 / TURN OFF • E2 TURN / ON (28.41.41.1)
        - box: BLOCK ICADV E1 / TURN ON (28.41.41.1)      [ALD number crossed by a scan line; read 28.41.41.1]
        - box: BLOCK IF1Y ANTIC / NORMAL FETCH / TURN ON (28.41.21.1)
        - box: BLOCK IF1Y E / TURN OFF (28.41.21.1)       [a stray mark crosses "OFF" and the ALD number; read TURN OFF (28.41.21.1)]
      the same YES line continues right (from the dot at the hex exit) to a second vertical line feeding (right column):
        - box: BLOCK FLLI / TURN OFF (28.79.32.1)
        - box: BLOCK FLLI / TURN ON (28.79.32.1)
        - box: BLOCK SLLI / TURN ON (28.79.42.1)          [ALD number crossed by a scan line; read 28.79.42.1]
        - box: BLOCK ZL-ZR MT / COA TGRS / TURN OFF (28.42.62.1)
Further down the E rail, a junction dot, line right and down into the top of:
- hex: SUSPEND / OPERATION (28.41.22.1)
    --NO--> (exit on the LEFT side of the hex, labelled NO; junction dot)
        - box: ESTABLISH IC / FETCH PRIORITY (28.42.12.1)
        - box: GATE 1Y RETURN / ADDRESS (28.44.13.1)
At the bottom the E rail turns right into a horizontal line feeding the tops of five hexes (junction dots):
- hex: SUSPENSION / TGRS OFF • / SBC PRESENT (28.41.21.1)
    --YES--> box: TURN ON IF1Y / M TGR (28.41.21.1)
- hex: REPEAT INSTR • / ~SUSPEND (28.41.22.1)       [a rule is printed between "REPEAT INSTR •" and "SUSPEND"; read as overbar on SUSPEND]
    --YES--> box: GENERATE ADR / 4 (28.21.10.1)
- hex: RECOVERY • / ~REPEAT • / ~SUSPEND (28.41.22.1)
        [three text rows; a rule is printed between RECOVERY and REPEAT (spanning "REPEAT"), and a rule between
         REPEAT and SUSPEND (spanning "REPEAT •"/"SUSPEND"). Read as overbars on REPEAT and on SUSPEND; no rule above
         RECOVERY (checked at 600%). Whether each rule is an overbar on the row below is the usual convention, not certain.]
    --YES--> box: GATE ICR 0-16 / TO MAB (21.03.01.1)
- hex: NORMAL / ADVANCE (28.41.22.1)
    --YES--> box: GATE ICA 0-16 / TO MAB (21.03.01.1)
- hex: 1Y BEING / EMPTIED (28.42.11.1)
    --YES--> box: BLOCK 1Y MT / TGR TURN ON (28.42.11.1)

### Output EM (second rail)
The EM rail ends at a junction dot from which a horizontal line runs right; three hexes hang from it:
- hex: NORMAL FETCH / ~SUSPENDED (28.41.22.1)       [a rule is printed between the two rows; read as overbar on SUSPENDED]
    --YES--> (junction dot) box: IF1Y FETCH REQ / TO BCU (28.44.11.1)
    --YES--> the same YES line continues down and right to the top (junction dot) of:
        - hex: ACCEPT OR / COMPARE / PRESENT (28.41.23.1)
            --YES--> (junction dot) box: TURN ON / ICFO1Y TGR (28.41.23.1)
            --YES--> (line continues right, junction dot, down into the top of)
                - hex: REPEAT INSTR / + MAB EQ / AD 1 (28.41.23.1)
                    --YES--> box: TURN ON / ICBC1Y TGR (28.41.23.1)
- hex: REPEAT INSTR   (no ALD number printed)
    --YES--> box: MAKE A PANEL / KEY REQ (28.41.31.1)
- hex: IF1Y E o M / LTH + IF2Y / E o M LTH (28.41.21.1)
        [the operator between E and M is printed as a small open "o", unlike the solid "•" used elsewhere;
         no overbar seen on either M]
    --YES--> a vertical bus (junction dots) to ten off-figure lines, top to bottom:
        - TO FLLI TON CKT (28.79.32.1)
        - TO LA LD SEQ VFL2 (28.11.21.1)
        - TO LA LD SEQ VFL3 (28.11.31.1)
        - TO LA LD SEQ VFL4 (28.11.41.1)
        - TO LA LD SEQ VFL5 (28.11.51.1)
        - TO LA LD SEQ FPL4 (28.13.14.1)
        - TO LA LD SEQ FPL3 (28.13.31.1)
        - TO LA LD SEQ FPR4 (28.14.41.1)
        - TO LA LD SEQ FPR3 (28.14.13.1)
        - TO LA LD SEQ FPDD (28.10.11.1)

### Output M (third rail)
Junction dot just under the bar; two branches:
- hex: SABR • ~SUSPEND / ~(IF1Y LTH) • ACCEPT / OR COMPARE (28.41.21.1)
        [overbar over SUSPEND in row 1; a rule over "IF1Y LTH" in row 2 (does not extend over "• ACCEPT")]
    --YES--> box: TURN OFF IF1Y / E TGR (28.41.21.1)
- hex: IF1Y NE LTH • / ~(OPN FETCH REQ) / ~LTH (28.41.22.1)
        [a rule between row 1 and row 2 spanning "OPN FETCH REQ", and a short rule over "LTH" in row 3;
         best reading IF1Y NE LTH • ~(OPN FETCH REQ LTH)]
    --YES--> (down into the top of)
        - hex: 2Y NOT BUSY / ANTIC • NO CHRK / SINGLE ERR • SBC (28.41.31.1)
              [uncertain: "CHRK" - last letter runs into the hexagon border; could be CHK / CHRK / CHKR (Figs 3.1.2, 3.1.4 print CHKR)]
            --YES--> box: TURN ON / IF2Y (28.41.31.1)

### Noted (verbatim quotes)
- hex "RECOVERY OPERATION (28.41.21.1)" (turn-on condition)
- hex "SABR • ~SUSPEND ~(IF1Y LTH) • ACCEPT OR COMPARE (28.41.21.1)"
- hex "NORMAL FETCH ~SUSPENDED (28.41.22.1)"
- hex "ACCEPT OR COMPARE PRESENT (28.41.23.1)"
- hex "SUSPEND OPERATION (28.41.22.1)" (NO exit)
- hex "SUSPENSION TGRS OFF • SBC PRESENT (28.41.21.1)"
- hex "REPEAT INSTR • ~SUSPEND (28.41.22.1)"
- hex "RECOVERY • ~REPEAT • ~SUSPEND (28.41.22.1)"
- box "BLOCK IF1Y E TURN ON (28.41.23.1)"
- box "BLOCK ICFO2Y TURN ON (28.41.23.1)"
- box "BLOCK IF2Y E TURN OFF (28.41.31.1)"
- box "BLOCK ICBC2Y TURN ON (28.41.33.1)"
- box "BLOCK ICADV E1 TURN OFF • E2 TURN ON (28.41.41.1)"
- box "BLOCK ICADV E1 TURN ON (28.41.41.1)"
- box "BLOCK IF1Y ANTIC NORMAL FETCH TURN ON (28.41.21.1)"
- box "BLOCK IF1Y E TURN OFF (28.41.21.1)"
- box "BLOCK FLLI TURN OFF (28.79.32.1)"
- box "BLOCK FLLI TURN ON (28.79.32.1)"
- box "BLOCK SLLI TURN ON (28.79.42.1)"
- box "BLOCK ZL-ZR MT COA TGRS TURN OFF (28.42.62.1)"
- box "BLOCK 1Y MT TGR TURN ON (28.42.11.1)"
- lines "TO FLLI TON CKT (28.79.32.1)", "TO LA LD SEQ VFL2 (28.11.21.1)", "TO LA LD SEQ VFL3 (28.11.31.1)",
  "TO LA LD SEQ VFL4 (28.11.41.1)", "TO LA LD SEQ VFL5 (28.11.51.1)", "TO LA LD SEQ FPL4 (28.13.14.1)",
  "TO LA LD SEQ FPL3 (28.13.31.1)", "TO LA LD SEQ FPR4 (28.14.41.1)", "TO LA LD SEQ FPR3 (28.14.13.1)",
  "TO LA LD SEQ FPDD (28.10.11.1)"
- No printed time or count on this figure (other than "GENERATE ADR 4 (28.21.10.1)", "GATE ICR 0-16 TO MAB (21.03.01.1)",
  "GATE ICA 0-16 TO MAB (21.03.01.1)").

### Uncertain on this figure
- "MI TGR" vs "M1 TGR" in TURN OFF IF2Y MI TGR (28.41.31.1).
- Overbar extents in hex RECOVERY • / REPEAT • / SUSPEND (28.41.22.1).
- Overbar extents in hex IF1Y NE LTH • / OPN FETCH REQ / LTH (28.41.22.1).
- "NO CHRK" in hex 2Y NOT BUSY ... (28.41.31.1).
- "E o M" (open circle) in hex IF1Y E o M LTH + IF2Y E o M LTH (28.41.21.1): whether it is the AND-dot.
- ALD numbers crossed by the scan line: BLOCK ICADV E1 TURN ON (28.41.41.1), BLOCK SLLI TURN ON (28.79.42.1),
  BLOCK ICADV E1 TURN OFF • E2 TURN ON (28.41.41.1).

---------------------------------------------------------------------------------------------------
## FIGURE 3.1.2. IC 1Y TRIGGERS AND IWC1 SEQUENCER   (PDF page 64)

Header (margin strings as printed):
- Caption: "FIGURE 3.1.2. IC 1Y TRIGGERS AND IWC1 / SEQUENCER"
- Page tag: "1-3/1-4"
- Date: "2/1/62"
- Other margin strings: "M3-04-3" ; "I UNIT FLOW DIAGRAMS"
- Applicability note: "CPU 7101 / SER. NO. 30,004 / AND HIGHER"
- Printed note beside the drawing: "THIS FLOW DIAGRAM SHOWS: / ICFO 1Y TGR / ICBC 1Y TGR / ICRN 1Y TGR / IWC 1 SEQUENCER"

The page holds four bars: ICFO to 1Y TGR, ICRN to 1Y TGR, IWC 1 sequencer (left column, chained top to bottom),
and ICBC 1Y TGR (right column).

### Bar 1: INSTRUCTION COUNTER FETCH OUTSTANDING / (ICFO) TO 1Y TGR (28.41.23.1)
No turn-on hexagon drawn above it on this page. No output letter printed. One line leaves the bottom of the bar;
junction dots on it feed:
- box (left): BLOCK IF1Y / RECOVERY TON (28.41.21.1)
  same dot, line right and down into the top of:
    - hex: ~(RST1 M) • ~RST / ~(CHK CTLS) • SABR / o IC SELECT 1Y (28.41.23.1)
          [row 1: a rule over "RST1 M" and a separate rule over "RST"; a rule between row 1 and row 2 spanning
           "CHK CTLS" (so possibly ~(RST CHK CTLS) continued across the line break); the operator starting row 3 is
           printed as a small open "o", not the solid dot. "RST1" could be read "RSTI".]
        --YES--> line down the right side, then left, labelled "TURN ON ICRN1Y", into the top of Bar 2.
- box (left): BLOCK IF2Y / TURN ON (28.41.31.1)
- box (left): BLOCK LAM1 E / TURN ON (28.81.11.1)      [first group reads "28" with a slightly broken 8]
  box (right, same dot): BLOCK EMF3 / TON (28.80.11.1)
- box (left): BLOCK EMF5 / TURN ON (28.70.21.1)
  box (right, same dot): BLOCK IRF3 / TON (28.80.31.1)
- box (left): BLOCK XSF4 / TURN ON (28.80.24.1)   (end of the line; reached through a further junction dot)
  from that junction dot a line goes down and left to:
    - box (far left): BLOCK CHK 8 / TON (28.71.21.1)

### Bar 2: INSTRUCTION COUNTER RETURN (ICRN) TO 1Y TGR / (28.41.23.1)
Turn-on: the YES of the hex above, via the line labelled "TURN ON ICRN1Y".
No output letter printed. One line leaves the bottom; junction dots:
- first dot, line left and down into the top of:
    - hex: IC SELECT / 1Y (28.41.23.1)
        exit on the right side; NO "YES"/"NO" label printed on this exit
        --> box: COND I MOB / TO 1Y (28.44.15.1)
- second dot, line left and down to (no hexagon):
    - box: BLOCK ICWA / TURN ON (28.41.50.1)
- line continues down into the top of:
    - hex: INSTR CHK EN / • ICWA OFF • ~CHKR / ~(SINGLE ERR) • SAC • / ~(SUSPEND IF1Y LTH) (28.41.51.1)
          [rules as printed: a rule over "CHKR" at the end of row 2; a rule between rows 2 and 3 lying under
           "• ICWA OFF" / over "SINGLE ERR" (so possibly ~(CHKR SINGLE ERR) across the line break); a rule between rows 3
           and 4 spanning the whole of "SUSPEND IF1Y LTH". uncertain whether the last rule covers SUSPEND only,
           or SUSPEND IF1Y LTH.]
        --YES--> line labelled "TURN ON / 1Y IWC1 / SEQUENCER" into the top of Bar 3.

### Bar 3: INSTRUCTION WORD CHECK (IWC) 1 SEQUENCER / (28.41.51.1)
Outputs printed under the bar: E (left) , M (right)

Output E (rail down the left; boxes to the left of the rail, each on a junction dot, top to bottom):
- box: COND 1Y IDC / TURN ON CKTS (28.42.33.1)
  same dot, line right and down into the top of:
    - hex: ~(ICOR E • NM) • / IWC1 M TGR OFF   (no ALD number printed)
          [a long rule over "ICOR E • NM"; there may be a second, shorter rule directly over "NM" beneath it.
           uncertain: ~(ICOR E • NM) or ~(ICOR E • ~NM)?]
        --YES--> box: GATE ICOB / TO 1Y (28.44.16.1)
- box: TURN OFF ICRN1Y / WITH NEXT SABR (28.41.23.1)
- box: TURN OFF ICBC1Y / WITH NEXT SAC (28.41.23.1)
- box: COND SUSPEND / TURN ON CKT (28.42.43.1)
  same dot, line right and down into the top of:
    - hex: IWC1 M / TGR OFF (28.41.51.1)
        exit labelled "YES" with "E • ~M" printed under it (overbar over M)
        --YES--> box: I CHE E o NM TC (38.03.03.1)
              [operator between E and NM printed as a small open "o". Letters read as "I CHE ... TC";
               uncertain: I CHK? / IC? - Figs 3.1.4 and 3.1.5 print "I CHK E • ~M IC" / "I CHECK E NOT M IC" for 38.03.03.1.
               top edge of this box lies on a scan line.]
- box: COND ICOR TURN / ON CKT (28.41.71.1)       [ALD number sits on a scan line; read 28.41.71.1]
- box: TURN ON IWCA / WITH NEXT SBC (28.41.50.1)
- box: IWC1 ECC CHK (28.44.14.1)
- box: TO PARITY / GENERATION CTL / CKT (28.41.51.1)
  same dot, line right and down into the top of:
    - hex: REPEAT INSTR / + ~(IWC1 GEN PAR) (28.41.51.1)      [rule over "IWC1 GEN PAR", not over the "+"]
        --YES--> (right) box: GATE 1Y TO / ICIB (22.10.07.1)   [enters the box's left side]
        --NO-->  (left exit) line down, then right, then down to a junction dot feeding the left sides of:
            - box: BLOCK GATING OF / 1Y 0-18 TO ICIB (22.10.02.1)
            - box: BLOCK GATING OF / 1Y 19-63 TO ICIB (22.10.07.1)
- the E rail ends by turning right and down into the top of:
    - hex: SBC / PRESENT (28.41.51.1)
        --YES--> box: TURN ON IWC1 / M TGR (28.41.51.1)

Output M (rail down the right):
- junction dot: box (left): COND IC FTCH / PRIORITY CKTS (28.42.12.1)
  same dot, line right and down into the top of:
    - hex: ICOR SEQUENCER / OFF (28.41.61.1)      [a small mark after "OFF" - looks like a stray comma/period]
        --YES--> box: INSTR WORD CHK / COMPLETE TO Y-Z / XFER CKTS (28.15.60.1)
- rail continues down into the top of:
    - hex: NO CHKR / SINGLE ERR (28.41.51.1)      [crossed by a scan line between "SINGLE ERR" and the ALD number;
                                                   no overbar identified - the line there is the scan line]
        --YES--> box: TURN OFF IWC1 / E TGR (28.41.51.1)

### Bar 4 (right column): INSTRUCTION COUNTER BLOCK CHECK (ICBC) 1Y / TGR (28.41.23.1)
No turn-on hexagon drawn above it on this page. No output letter printed. One line leaves the bottom:
- junction dot: box (left): BLOCK ICW1 / ECC CHK (28.44.14.1)     [printed "ICW1" (letters in that order), not "IWC1"]
  same dot, line right and down into the top of:
    - hex: IWC1 E TGR / ON • IWC1 M TGR / OFF (28.41.51.1)
        --YES--> box: GENERATE / PARITY (34.08.11.1)
- line continues down into the top of:
    - hex: REPEAT / INSTR (28.41.51.1)
        --NO--> (left exit) long line down the page to the RIGHT sides of (junction dot at the first):
            - box: BLOCK GATING OF / 1Y 0-18 TO ICIB (22.10.02.1)
            - box: BLOCK GATING OF / 1Y 19-63 TO ICIB (22.10.07.1)
        --YES--> (right exit) down into the top of:
            - hex: IWC1 E TGR / ON (28.41.51.1)
                --YES--> long line down the right side of the page, then left into the RIGHT side of
                    - box: GATE 1Y TO / ICIB (22.10.07.1)
                  (this line crosses the NO line above without a junction dot)
  So the three ICIB boxes (GATE 1Y TO ICIB; BLOCK GATING OF 1Y 0-18 TO ICIB; BLOCK GATING OF 1Y 19-63 TO ICIB) are each
  drawn once and each is reached from both the IWC1 E branch (left side) and the ICBC 1Y branch (right side).

### Noted (verbatim quotes)
- box "BLOCK IF1Y RECOVERY TON (28.41.21.1)"
- box "BLOCK IF2Y TURN ON (28.41.31.1)"
- box "BLOCK LAM1 E TURN ON (28.81.11.1)"
- box "BLOCK EMF3 TON (28.80.11.1)"
- box "BLOCK EMF5 TURN ON (28.70.21.1)"
- box "BLOCK IRF3 TON (28.80.31.1)"
- box "BLOCK XSF4 TURN ON (28.80.24.1)"
- box "BLOCK CHK 8 TON (28.71.21.1)"
- box "BLOCK ICWA TURN ON (28.41.50.1)"
- box "BLOCK ICW1 ECC CHK (28.44.14.1)"
- box "BLOCK GATING OF 1Y 0-18 TO ICIB (22.10.02.1)"
- box "BLOCK GATING OF 1Y 19-63 TO ICIB (22.10.07.1)"
- hex "INSTR CHK EN • ICWA OFF • CHKR SINGLE ERR • SAC • SUSPEND IF1Y LTH (28.41.51.1)" (overbars as discussed above)
- box "COND SUSPEND TURN ON CKT (28.42.43.1)"
- box "COND 1Y IDC TURN ON CKTS (28.42.33.1)"
- box "COND I MOB TO 1Y (28.44.15.1)"
- box "INSTR WORD CHK COMPLETE TO Y-Z XFER CKTS (28.15.60.1)"
- hex "~(RST1 M) • ~RST ~(CHK CTLS) • SABR o IC SELECT 1Y (28.41.23.1)"
- No printed time or count (bit ranges only: "1Y 0-18", "1Y 19-63").

### Uncertain on this figure
- Overbar extents in hex RST1 M • RST / CHK CTLS • SABR / o IC SELECT 1Y (28.41.23.1); the open "o" operator.
- Overbar extents in hex INSTR CHK EN / • ICWA OFF • CHKR / SINGLE ERR • SAC • / SUSPEND IF1Y LTH (28.41.51.1).
- Overbar(s) in hex ICOR E • NM • / IWC1 M TGR OFF (one long rule, possibly a second over NM).
- "I CHE E o NM TC (38.03.03.1)": the open "o"; "CHE".
- NO CHKR / SINGLE ERR (28.41.51.1): scan line prevents ruling an overbar in or out.
- Exit of hex IC SELECT 1Y (28.41.23.1) carries no YES/NO label.
- COND ICOR TURN ON CKT (28.41.71.1): ALD number on a scan line.

---------------------------------------------------------------------------------------------------
## FIGURE 3.1.3. IF 2Y SEQUENCER   (PDF page 65)

Header (margin strings as printed):
- Caption: "FIGURE 3.1.3. IF 2Y SEQUENCER"
- Page tag: "1-5/1-6"
- Date: "2/1/62"
- Other margin strings: "M3-04-3" ; "I UNIT FLOW DIAGRAMS"
- Applicability note: "CPU 7101 / SER. NO. 30,004 / AND HIGHER"

### Turn-on conditions (hexagons above the bar)
Five hexes, each YES; the YES lines join one horizontal line (junction dots) which drops into the bar through a
line labelled "TURN ON IF2Y".
- hex: NORMAL FETCH / ANTICIPATED ON / ACCEPT (28.41.31.1) --YES-->
- hex: NORMAL FETCH (28.41.31.1) --YES-->
- hex: RECOVERY / OPERATION (28.41.31.1) --YES-->
- hex: BRANCH TO / EVEN ADR / INSTR (28.41.31.1) --YES-->
- hex: NORMAL / ANTICIPATED / FETCH (28.41.31.1) --YES-->
    --> line label "TURN ON IF2Y" -->

### Bar
INSTRUCTION FETCH TO 2Y SEQUENCER (28.41.31.1)
Outputs printed under the bar: E (far left) , M1 (next to E) , M2 (far right)

### Output M2
- box: TURN ON LA / LAST LD SEQS (28.41.31.1)     (direct; no hexagon)

### Output E (leftmost rail, full height)
Boxes hung directly on the E rail (junction dots, boxes left of the rail):
- box: TURN OFF 2YMT / TGR (28.42.11.1)
- box: TURN OFF EVEN / BR TGR (28.42.21.1)
- box: TURN OFF IF1Y / M TGR (28.41.21.1)
- box: TURN OFF RST1 / M TGR (28.41.11.1)
Next junction dot on the E rail, line right and down into the top of:
- hex: IF2Y M / TGR OFF   (no ALD number printed)
    exit labelled "YES" with "E • ~M" printed under it (overbar over M)
    --YES--> vertical distribution line with junction dots, feeding (left column | middle column):
        - box: BLOCK IF1Y / TURN ON (28.41.23.1)
        - box: BLOCK ICFO2Y / TURN ON (28.41.33.1)
        - box: BLOCK IF2Y / TURN OFF (28.41.31.1)
        - box: BLOCK ICBC2Y / TURN ON (28.41.33.1)
        - box: BLOCK ICADV / E1 TOF • E2 TON (28.41.41.1)
        - box: BLOCK ICADV / E1 TURN ON (28.41.41.1)
        - box: BLOCK IF1Y / ANTIC NORMAL / FETCH TON (28.41.21.1)     [row 2 crossed by a scan line]
        - box: BLOCK IF1Y / E TURN OFF   (no ALD number printed in this box; row 1 crossed by a scan line)
      the same YES line continues right from the dot at the hex exit to a second vertical line feeding (right column):
        - box: BLOCK FLLI / TURN OFF (28.79.32.1)
        - box: BLOCK FLLI / TURN ON (28.79.32.1)
        - box: BLOCK SLLI / TURN ON (28.79.42.1)
        - box: BLOCK ZL-ZR / MT COA TGRS / TURN OFF (28.42.62.1)     [row 2 crossed by a scan line]
Next junction dot on the E rail, horizontal line right feeding the tops of two hexes:
- hex: SUSPEND / OPERATION (28.41.32.1)
    --NO--> (left exit) line down with junction dots feeding (left | right of the line):
        - box: GATE 2Y RETURN / ADDRESS (28.44.13.1)
        - box: ESTABLISH IC / FETCH PRIORITY (28.20.23.1)
              [digits confirmed on a 600% crop; as printed. Fig 3.1.1 prints (28.42.12.1) for ESTABLISH IC FETCH PRIORITY.]
        - box: BLOCK ICADV / E1 TGR TURN / OFF (28.41.41.1)      [a small mark between "E1" and "TGR", like a hyphen]
        - box: COND IF1Y / ANTICIPATED NORMAL / FETCH TURN ON CKT (28.41.21.1)
- hex: END IC / SUSPENSION • IF / 2Y FETCH REQ LTH (28.41.31.1)
        [rules as printed (600% crop): one above "END IC"; one between rows 1 and 2 (under "END IC", over
         "SUSPENSION"); one between rows 2 and 3 on the left (under "SUSPENSION", over "2Y FETCH"); one over
         "REQ LTH" in row 3; and "IF" at the end of row 2 carries a mark that looks like an overbar/strike.
         Negation structure NOT resolved. Candidate: ~(END IC SUSPENSION) • ~(IF 2Y FETCH REQ LTH)?]
    --YES--> (junction dot)
        - box: TURN ON IF2Y / M1 TGR WITH / NEXT SBC (28.41.31.1)
        - line continues right and down into the top of:
          hex: ~RCY + ~ICADV / E (28.41.31.1)        [separate rules over "RCY" and over "ICADV"; "E" alone on row 2]
            --YES--> box: TURN ON IF2Y / M2 TGR (28.41.31.1)
At the bottom the E rail turns right into a horizontal line feeding the tops of five hexes (junction dots):
- hex: REPEAT INSTR • / ~SUSPEND (28.41.32.1)        [rule between the rows, under "REPEAT INST" / over "SUSPEND"]
    --YES--> box: GENERATE ADR 4 (28.21.10.1)
- hex: RECOVERY / • ~REPEAT • / ~SUSPEND (28.41.32.1)
        [rule between RECOVERY and "• REPEAT •", and rule between "• REPEAT •" and SUSPEND; none above RECOVERY]
    --YES--> box: GATE ICR 0-16 / TO MAB (21.03.01.1)     [the E of GATE is broken, looks like "GATL"]
- hex: NORMAL / ADVANCE (28.41.32.1)
    --YES--> box: GATE ICA 0-16 / TO MAB (21.03.01.1)
- hex: 2Y BEING EMPTIED (28.42.11.1)
        [a free-standing horizontal rule is printed inside the hexagon above the text, roughly over "BEING EMP";
         uncertain: overbar ~(2Y BEING EMPTIED)? or a drafting artefact]
    --YES--> box: BLOCK TURN ON / OF 2YMT TGR (28.42.11.1)
- hex: END IC / SUSPENSION • / SBC   (no ALD number printed)
    --YES--> box: TURN OFF IF2Y / M1 • M2 TGRS (28.41.31.1)

### Output M1 (second rail)
Junction dot just under the bar; a horizontal line runs right from it feeding the tops of three hexes:
- hex: ZRMT COA LTH • / ACC + COMP • SAC • ~RCY / ~(PROG HLT) • ICADV M / OFF • CARRY OUT OF / ICR 17 (28.41.41.1)
        [rule over "RCY" at the end of row 2; rule between rows 2 and 3 spanning "PROG HLT" (it lies under
         "ACC + COMP"). A small stray mark precedes "ICR 17".]
    --YES--> joins (junction dot) the YES of the next hex -->
- hex: CARRY OUT OF / ICR 17 • ~RCY • / ~(PROG HLT) • SAC • / ICADV M OFF o / ZRMT COA CTH (28.41.41.1)
        [rule over "RCY" (it lies under "UT OF" of row 1); rule between rows 2 and 3 spanning "PROG HLT" (it lies
         under "ICR 17 • R"). The operator ending row 4 is a small open "o". Last row reads "CTH" (C, not L) -
         uncertain: CTH / LTH?]
    --YES--> (both hexes) box: TURN ON ICADV / E1 TGR (28.41.41.1)
- hex: IF2Y E TGR ON / • ~RST1 + ~RST2 • / ~SUSPEND (28.41.32.1)
        [short rules under "2Y" and under "GR O" of row 1 = over "RST1" and over "RST2"; rule between rows 2 and 3
         under "• RST1 +" = over "SUSPEND"]
    exit labelled "YES" with "E • M" printed under it (no overbar seen on this M)
    --YES--> line down to a junction dot on a horizontal line, which feeds:
        - (left end, junction dot) box: SET NIDC ON / IC 0-16 ERR (28.51.11.1)
                                   box: FETCH REQ (12.09.01.1)
        - hex: REPEAT + MAB / EQAD 2 • ACC + / COMP • ~SUSPEND (28.41.33.1)   [rule under "ACC +" = over "SUSPEND"]
            --YES--> box: TURN ON ICBC / 2Y TGR (28.33.41.1)
                     [ALD number printed "28.33.41.1" - as printed; compare 28.41.33.1 on its neighbours]
        - (junction dot) hex: ACC + COMP • / SABR • ~SUSPEND (28.41.33.1)     [rule under "COMP •" = over "SUSPEND"]
            --YES--> box: TURN ON ICFO / 2Y TGR (28.41.33.1)
        - right end of the horizontal line turns down the right side of the figure; junction dot, line left into the top of:
          hex: SAR • ACC + / COMP • ICADV / M TGR ON (28.41.41.1)
            --YES--> box: TURN OFF ICADV / E1 TGR (28.41.41.1)
        - the right-side line continues down, then left into the top of:
          hex: ACC + COMP • / SAC • RCY / COND (28.41.41.1)
            --YES--> box: TURN ON ICADV / E2 TGR (28.41.41.1)
Further down the M1 rail, junction dot, line right and down into the top of:
- hex: ~SUSPEND / ~IF2Y (28.41.31.1)
        [a rule above "SUSPEND" and a shorter rule between the rows above "IF2Y". A scan smear crosses the bottom
         of this hexagon.]
    --YES--> line right and down into the top of:
        - hex: IF2Y  E / LTH (28.41.32.1)       [gap printed between "IF2Y" and "E"]
            --NO--> (left exit; "NE • M" printed under the NO; a small mark above the N or E - uncertain whether
                     it is an overbar) down into the top of:
                - hex: RCY COND / TON ICADV / E2 • SAC (28.41.41.1)
                    --YES--> box: TURN ON / ICADV E 2 (28.41.41.1)
            --YES--> (right exit; "E o M" printed under the YES, open "o") long line down to a vertical bus
                     (junction dots) of ten off-figure lines, top to bottom:
                - TO FLLI TON CKT (28.79.32.1)
                - TO LA LD SEQ VFL2 (28.11.21.1)
                - TO LA LD SEQ VFL3 (28.11.31.1)
                - TO LA LD SEQ VFL4 (28.11.41.1)
                - TO LA LD SEQ VFL5 (28.11.51.1)
                - TO LA LD SEQ FPL4 (28.13.41.1)      [as printed here; Fig 3.1.1 prints 28.13.14.1 for the same line]
                - TO LA LD SEQ FPL3 (28.13.31.1)
                - TO LA LD SEQ FPR4 (28.14.41.1)      [struck through by a scan line; read 28.14.41.1]
                - TO LA LD SEQ FPR3 (28.14.13.1)
                - TO LA LD SEQ FPDD (28.10.11.1)
The M1 rail ends by turning right and down into the top of:
- hex: ACC + COMP • / SABR • SUSPEND / IF2Y LTH (28.41.31.1)
        [a short rule sits over "COMP" exactly where the entry line meets the hexagon border - uncertain whether it is
         an overbar on COMP or part of the border; no rule seen over SUSPEND or IF2Y LTH]
    exit on the right side, NO "YES" label printed
    --> box: TURN OFF IF2Y / E TGR (28.41.31.1)

### Noted (verbatim quotes)
- hex "RECOVERY OPERATION (28.41.31.1)" ; hex "BRANCH TO EVEN ADR INSTR (28.41.31.1)" (turn-on conditions)
- box "TURN ON LA LAST LD SEQS (28.41.31.1)" (M2)
- box "TURN OFF EVEN BR TGR (28.42.21.1)"
- hex "ZRMT COA LTH • ACC + COMP • SAC • ~RCY ~(PROG HLT) • ICADV M OFF • CARRY OUT OF ICR 17 (28.41.41.1)"
- hex "CARRY OUT OF ICR 17 • ~RCY • ~(PROG HLT) • SAC • ICADV M OFF o ZRMT COA CTH (28.41.41.1)"
- hex "IF2Y E TGR ON • ~RST1 + ~RST2 • ~SUSPEND (28.41.32.1)"
- hex "REPEAT + MAB EQAD 2 • ACC + COMP • ~SUSPEND (28.41.33.1)"
- hex "ACC + COMP • SABR • ~SUSPEND (28.41.33.1)"
- hex "~SUSPEND ~IF2Y (28.41.31.1)"
- hex "ACC + COMP • SABR • SUSPEND IF2Y LTH (28.41.31.1)"
- hex "RCY COND TON ICADV E2 • SAC (28.41.41.1)"
- hex "ACC + COMP • SAC • RCY COND (28.41.41.1)"
- hex "SUSPEND OPERATION (28.41.32.1)" (NO exit)
- hex "END IC SUSPENSION • IF 2Y FETCH REQ LTH (28.41.31.1)" (overbars unresolved)
- hex "~RCY + ~ICADV E (28.41.31.1)"
- hex "REPEAT INSTR • ~SUSPEND (28.41.32.1)" ; hex "RECOVERY • ~REPEAT • ~SUSPEND (28.41.32.1)" ; hex "END IC SUSPENSION • SBC"
- box "SET NIDC ON IC 0-16 ERR (28.51.11.1)"
- boxes "BLOCK IF1Y TURN ON (28.41.23.1)", "BLOCK ICFO2Y TURN ON (28.41.33.1)", "BLOCK IF2Y TURN OFF (28.41.31.1)",
  "BLOCK ICBC2Y TURN ON (28.41.33.1)", "BLOCK ICADV E1 TOF • E2 TON (28.41.41.1)", "BLOCK ICADV E1 TURN ON (28.41.41.1)",
  "BLOCK IF1Y ANTIC NORMAL FETCH TON (28.41.21.1)", "BLOCK IF1Y E TURN OFF", "BLOCK FLLI TURN OFF (28.79.32.1)",
  "BLOCK FLLI TURN ON (28.79.32.1)", "BLOCK SLLI TURN ON (28.79.42.1)", "BLOCK ZL-ZR MT COA TGRS TURN OFF (28.42.62.1)",
  "BLOCK ICADV E1 TGR TURN OFF (28.41.41.1)", "BLOCK TURN ON OF 2YMT TGR (28.42.11.1)"
- lines "TO FLLI TON CKT (28.79.32.1)" and the nine "TO LA LD SEQ ..." lines listed above
- box "TURN ON IF2Y M1 TGR WITH NEXT SBC (28.41.31.1)"
- No printed time or count.

### Uncertain on this figure
- Overbar structure of hex END IC / SUSPENSION • IF / 2Y FETCH REQ LTH (28.41.31.1).
- Rule above the text in hex 2Y BEING EMPTIED (28.42.11.1).
- Possible overbar on COMP in hex ACC + COMP • / SABR • SUSPEND / IF2Y LTH (28.41.31.1); its exit has no YES label.
- "CTH" in ZRMT COA CTH (second M1 hex); the open "o" before it.
- "NE • M" label on the NO exit of IF2Y E LTH (possible overbar); "E o M" on its YES exit; "E • M" on IF2Y E TGR ON.
- TURN ON ICBC 2Y TGR (28.33.41.1): number as printed looks transposed relative to neighbours; digits themselves read clearly.
- TO LA LD SEQ FPR4 (28.14.41.1): under a scan line.
- BLOCK IF1Y E TURN OFF: no ALD number visible (a scan line crosses the box; the number may be absent rather than hidden).

---------------------------------------------------------------------------------------------------
## FIGURE 3.1.4. IC 2Y TRIGGERS AND IWC2 SEQUENCER   (PDF page 66)

Header (margin strings as printed):
- Caption: "FIGURE 3.1.4. IC 2Y TRIGGERS AND / IWC2 SEQUENCER"
- Page tag: "1-7/1-8"
- Date: "2/1/62"
- Other margin strings: "M3-04-3" ; "I UNIT FLOW DIAGRAMS"
- Applicability note: "CPU 7101 / SER. NO. 30,004 / AND HIGHER"
- Printed note beside the drawing: "THIS FLOW DIAGRAM SHOWS: / ICFO 2Y TGR / ICBC 2Y TGR / ICRN 2Y TGR / IWC 2 SEQUENCER"

Four bars: ICFO to 2Y TGR (top left), ICBC 2Y TGR (top right), ICRN to 2Y TGR (middle), IWC 2 sequencer (below it).

### Bar 1: INSTRUCTION COUNTER FETCH OUTSTANDING TO 2Y / TGR (28.41.33.1)
No turn-on hexagon drawn above it. No output letter printed. One line leaves the bottom; junction dots feed
(boxes to the left of the line, top to bottom):
- box: BLOCK IF1Y TON (28.41.21.1)
  the same dot's horizontal line continues right:
    - junction dot, down into the top of
      hex: RST1 NM (28.41.50.1)
        --YES--> box: BLOCK IWCA / TON (28.41.50.1)
    - line continues right, then down into the top of
      hex: IC SELECT / 2Y • SABR • / ~(RST1 M) o ~RST / ~(CHK CTLS) (28.41.33.1)
            [rules: between rows 2 and 3 on the left (under "2Y • SA", over "RST1 M"); a short one at the right end of
             row 2 (under the trailing "•", over "RST"); between rows 3 and 4 over "CHK CTLS". The operator between
             "RST1 M" and "RST" is a small open "o". Possibly ~(RST CHK CTLS) across the line break.]
        --YES--> long line down labelled "TON ICRN 2Y" into the top of Bar 3.
- box: BLOCK IF2Y E / RECOVERY TON (28.41.31.1)
- box: BLOCK EMF 5 / TON (28.70.21.1)
- box: BLOCK XSF4 / TON (28.80.24.1)        [last digit slightly damaged; read .1]
- box: BLOCK LAM 1E / TON (28.81.11.1)
- box: BLOCK EMF3 / TON (28.80.11.1)
- box: BLOCK IRF3 / TON (28.80.31.1)        (end of the line)

### Bar 2 (top right): INSTRUCTION COUNTER BLOCK CHECK 2Y / TGR (28.41.33.1)
No turn-on hexagon drawn above it. No output letter printed. One line leaves the bottom:
- junction dot: box (left): BLOCK IWC2 / ECC CHK (28.41.61.1)
- line continues down into the top of:
    - hex: IWC2 E / TGR ON (28.41.61.1)
        --YES--> box: GEN IWC2 / PAR (28.44.16.1)

### Bar 3: INSTRUCTION COUNTER RETURN TO 2Y (28.41.33.1) / TGR
(text as printed: the ALD number follows "2Y" on row 1 and "TGR" is on row 2)
Turn-on: YES of the IC SELECT 2Y • SABR ... hex above, via the line labelled "TON ICRN 2Y".
No output letter printed. One line leaves the bottom, runs left; it feeds two hexes:
- (junction dot) hex: SAC • ~SUSPEND / ~2Y • NO CHKR SING / ERR • INSTR CHK EN • / ALLOW 2Y INSTR / CHK (28.41.61.1)
        [a rule over "SUSPEND" in row 1; a short rule between rows 1 and 2 over "2Y" (it lies under "SA" of SAC).
         Possibly ~(SUSPEND 2Y) across the line break. No rule seen over CHKR.]
    --YES--> line labelled "TON IWC2" into the top of Bar 4.
- (end of line) hex: IC SELECT 2Y (28.41.33.1)
    --YES--> box: COND IMOB / TO 2Y (28.44.15.1)

### Bar 4: INSTRUCTION WORD CHECK 2 SEQUENCER / (28.41.61.1)
Outputs printed under the bar, left to right: E , E • M , M

Output E • M:
- box: GATE ICOB TO / 2Y (28.44.16.1)       (direct, no hexagon; last digit slightly damaged, read .1; box bottom on a scan line)

Output E (rail; boxes to the left, each on a junction dot, top to bottom):
- box: GATE 2Y 0-63 / TO ICIB / (22.10.21.1) / (22.10.08.1)       [two ALD numbers printed in this box]
- box: TOF ICBC2Y / TGR (28.41.33.1)
- box: TOF ICRN2Y TGR (28.41.33.1)
- box: TOF IWCA TGR (28.41.50.1)
- box: COND TON 2YIDC (28.42.33.1)
- box: COND SPND TON (28.42.42.1)
  from this same junction dot a horizontal line runs right, feeding the tops of three hexes:
    - (junction dot) hex: IWC2 GEN / PAR (ICBC2Y / TGR ON) (28.41.61.1)        [parentheses around "ICBC2Y TGR ON" are printed]
        --YES--> box: GEN PAR IWC2 (34.08.11.1)
    - (junction dot) hex: IWC2 M TGR / OFF • ~BLOCK / ~(IWC2 ECC CHK) (28.41.61.1)
            [rule between rows 1 and 2 on the right (under "M TGR", over "BLOCK"); rule between rows 2 and 3 over the whole
             of "IWC2 ECC CHK". Possibly IWC2 M TGR OFF • ~(BLOCK IWC2 ECC CHK).]
        exit labelled "YES" with "E • ~M" under it (overbar over M)
        --YES--> box: I CHK ECC (34.08.11.1)
    - (end of line) hex: IWC2 M / TGR OFF (28.41.61.1)
        --YES--> box: I CHK E • ~M IC (38.03.03.1)        [overbar over M inside the box text]
- box: COND ICOR TON / CKT (28.41.71.1)       (end of the E rail)

Output M (rail on the right):
- junction dot just below the bar; a line runs right and then down the right side to (no hexagon):
    - (junction dot) box: COND IC FETCH / PRIORITY CKTS (28.42.12.1)
    - box: INSTR WRD CHK / COMPLETE TO Y-Z / XFER CKTS (28.15.60.1)
- rail continues down into the top of:
    - hex: NO CHKR SING / ERR • SAC (28.41.61.1)       [hexagon bottom edge on a scan line]
        --YES--> box: TOF IWC2 E / TGR (28.41.61.1)

### Noted (verbatim quotes)
- box "BLOCK IF1Y TON (28.41.21.1)" ; box "BLOCK IF2Y E RECOVERY TON (28.41.31.1)" ; box "BLOCK EMF 5 TON (28.70.21.1)" ;
  box "BLOCK XSF4 TON (28.80.24.1)" ; box "BLOCK LAM 1E TON (28.81.11.1)" ; box "BLOCK EMF3 TON (28.80.11.1)" ;
  box "BLOCK IRF3 TON (28.80.31.1)" ; box "BLOCK IWCA TON (28.41.50.1)" ; box "BLOCK IWC2 ECC CHK (28.41.61.1)"
- hex "SAC • ~SUSPEND ~2Y • NO CHKR SING ERR • INSTR CHK EN • ALLOW 2Y INSTR CHK (28.41.61.1)"
- hex "IWC2 M TGR OFF • ~BLOCK ~(IWC2 ECC CHK) (28.41.61.1)"
- box "COND SPND TON (28.42.42.1)" ; box "COND TON 2YIDC (28.42.33.1)" ; box "COND IMOB TO 2Y (28.44.15.1)"
- box "INSTR WRD CHK COMPLETE TO Y-Z XFER CKTS (28.15.60.1)"
- hex "IC SELECT 2Y • SABR • ~(RST1 M) o ~RST ~(CHK CTLS) (28.41.33.1)" ; hex "RST1 NM (28.41.50.1)"
- No printed time or count (bit range only: "GATE 2Y 0-63 TO ICIB").

### Uncertain on this figure
- Overbar extents in hex IC SELECT / 2Y • SABR • / RST1 M o RST / CHK CTLS (28.41.33.1); the open "o".
- Overbar extents in hex SAC • SUSPEND / 2Y • NO CHKR SING / ERR ... (28.41.61.1).
- Overbar extents in hex IWC2 M TGR / OFF • BLOCK / IWC2 ECC CHK (28.41.61.1).
- Last digit of BLOCK XSF4 TON (28.80.24.1) and of GATE ICOB TO 2Y (28.44.16.1) (damaged "1").

---------------------------------------------------------------------------------------------------
## FIGURE 3.1.5. IC ADV SEQUENCER AND ICOR SEQUENCER   (PDF page 67)

Header (margin strings as printed):
- Caption: "FIGURE 3.1.5. IC ADV SEQUENCER AND / ICOR SEQUENCER"
- Page tag: "1-9/1-10"
- Date: "2/1/62"
- Other margin strings: "M3-04-3" ; "I UNIT FLOW DIAGRAMS"
- Applicability note: "CPU 7101 / SER. NO. 30,004 / AND HIGHER"

Two bars on the page: ICADV sequencer (top) and ICOR sequencer (bottom). They are not connected to each other by any line.

### Bar 1: INSTRUCTION COUNTER ADVANCE (ICADV) / SEQUENCER (28.41.41.1)
No turn-on hexagon drawn above it on this page.
Outputs printed under the bar, left to right: E1 , E2 , M

Output E2 (rail; boxes to the LEFT of the rail, between the E1 and E2 rails; no hexagons):
- (junction dot) box: TOF ODD BR TGR (28.42.21.1)
- (junction dot) box: TOF RCY GT CTL (28.42.21.1)
- (end of rail)  box: TON ICADV M / TGR (28.41.41.1)

Output E1 (rail):
- junction dot; a line goes left and down, feeding (no hexagon):
    - (junction dot) box: BLOCK IF2Y M2 / TON (28.41.31.1)
    - (end of line)  box: TON ICADV M / TGR (28.41.41.1)
      [this is a second, separately drawn "TON ICADV M TGR (28.41.41.1)" box - the other one is on E2]
- the E1 rail continues down into the top of:
    - hex: ~(RST1 + RST 2)E • / ICADV E 1 LTH (28.41.41.1)
          [one rule over "RST1 + RST 2"; uncertain whether it also covers the trailing "E". Printed with a space:
           "RST 2E".]
        --YES--> (junction dot) box: GI ICA 0-16 / TO ICR 0-16 (21.02.01.1)
                     [first word printed "GI" - possibly "GT" with a broken T; the hyphen in the first "0-16" is
                      damaged and looks like a small mark]
                 (end of line)  box: BLOCK IC LOCAL / ERR TGRS TON (21.04.07.1)

Output M (rail):
- junction dot; a line goes right and down into the top of:
    - hex: ~(SUSPEND IF2Y) / ~LTH • ~(IF2YE LTH) • / SAR (28.41.41.1)
          [rules as printed: one above the whole of "SUSPEND IF2Y" (row 1); one between rows 1 and 2 on the left
           (under "SU", over "LTH"); one between rows 1 and 2 on the right (under "ND IF2Y", over "IF2YE LTH").
           Possibly ~(SUSPEND IF2Y LTH) • ~(IF2YE LTH) • SAR. "SAR" printed with a gap ("SA R").]
        --YES--> line down to a junction dot at the right side of
            box: TOF ICADV E1 / TGR (28.41.41.1)       (only this box is on the YES line)
- the M rail continues down (boxes hung on it by junction dots, no hexagon):
    - (junction dot) box (left): BLOCK JCADV E1 / TGR TON (28.41.41.1)
          [printed "JCADV" - first letter looks like J; probably a damaged I. Recorded as printed.]
    - (junction dot, end of rail) box (left): TOF ICADV E2 / TGR (28.41.41.1)
                                  box (right): COND IF1Y E / TGR TON CKTS (28.41.21.1)
          [printed "IFIY" - the 1 looks like I; second group of the ALD number has a weak "1": 28.41.21.1]

### Bar 2: INSTRUCTION WORD CORRECT (ICOR) SEQUENCER / (28.41.71.1)
Turn-on condition (hexagon above the bar):
- hex: SAC•IWC 1+ / IWC 2 E LTH• / CHKR SING ERR (28.41.71.1)      [no overbar seen]
    --YES--> into the top of the bar (no label on the line)
Outputs printed under the bar, left to right: E , E • ~M , E • M , M
  ("E • ~M": overbar over M. "E • M": the dot is printed as a ring/dot, no overbar on M.)

Output M:
- box: TOF ICOR E / TGR WITH NEXT / SBC (28.41.71.1)       (direct; row 2 struck by a scan line)

Output E • M:
- box: I LAST HALF / CORR CYCLE (34.08.31.1)       (direct; a stray mark sits over the "3" of ".31."; row 1/2 on a scan line)

Output E • ~M (rail):
- (junction dot) box (left): I CHECK E NOT / M IC (38.03.03.1)       (row 1 on a scan line)
- rail ends at a junction dot on a short horizontal line feeding the tops of two hexes:
    - hex: IWC2E•NM (28.41.61.1)
        --YES--> box: GT ICOB / TO 2Y (28.44.16.1)
    - hex: IWC1E•NM (28.41.51.1)
        exit on the right; NO "YES" label printed on this exit
        --> box: GT ICOB / TO 1Y (28.44.16.1)

Output E (rail; boxes to the left of the rail on junction dots, top to bottom):
- box: TON ICOR M / TGR WITH NEXT / SBC (28.41.71.1)       (row 2 struck by a scan line)
- box: BLOCK GENERATION / OF 2Y NOT BUSY (28.42.12.1)
- box: BLOCK / ESTABLISHMENT OF / IC FTCH PRIORITY (28.42.12.1)
- box: BLOCK GENERATION / OF 2Y NOT BUSY / ANTIC ON ACCEPT (28.42.12.1)
  from this same junction dot a horizontal line runs right; three vertical drops hang from it:
    - first drop (junction dot on the horizontal line), boxes to its LEFT:
        - (junction dot) box: BLOCK GENERATION / OF 1Y NOT BUSY / ANTIC (28.42.12.1)
        - (end)          box: BLOCK GENERATION / OF 1Y NOT BUSY / ANTIC ON ACCEPT (28.42.12.1
                              [closing parenthesis not printed / cut by the box border]
    - second drop (junction dot), boxes to its LEFT:
        - (junction dot) box: BLOCK 1Y SUSPEND / TGRS TON (28.42.42.1)
        - (end)          box: BLOCK 2Y SUSPEND / TGRS TON (28.42.43.1)
    - third drop (end of the horizontal line), boxes to its LEFT:
        - (junction dot) box: BLOCK INITIATION / OF Y-Z XFER (28.15.60.1)
        - (end)          box: COND 1Y • 2Y / IDC TON CKTS (28.41.71.1)       [the dot between 1Y and 2Y is a ring-dot]
- box: BLOCK GENERATION / OF 2Y NOT BUSY / ANTIC (28.42.12.1)
- box: BLOCK GENERATION / OF 1Y NOT BUSY (28.41.21.1)       (end of the E rail)

### Noted (verbatim quotes)
- box "TOF ODD BR TGR (28.42.21.1)" ; box "TOF RCY GT CTL (28.42.21.1)"
- box "BLOCK IF2Y M2 TON (28.41.31.1)" ; box "BLOCK IC LOCAL ERR TGRS TON (21.04.07.1)" ; box "BLOCK JCADV E1 TGR TON (28.41.41.1)"
- hex "~(RST1 + RST 2)E • ICADV E 1 LTH (28.41.41.1)"
- hex "~(SUSPEND IF2Y) ~LTH • ~(IF2YE LTH) • SAR (28.41.41.1)"
- box "GI ICA 0-16 TO ICR 0-16 (21.02.01.1)"
- box "BLOCK GENERATION OF 2Y NOT BUSY (28.42.12.1)" ; box "BLOCK ESTABLISHMENT OF IC FTCH PRIORITY (28.42.12.1)" ;
  box "BLOCK GENERATION OF 2Y NOT BUSY ANTIC ON ACCEPT (28.42.12.1)" ; box "BLOCK GENERATION OF 2Y NOT BUSY ANTIC (28.42.12.1)" ;
  box "BLOCK GENERATION OF 1Y NOT BUSY (28.41.21.1)" ; box "BLOCK GENERATION OF 1Y NOT BUSY ANTIC (28.42.12.1)" ;
  box "BLOCK GENERATION OF 1Y NOT BUSY ANTIC ON ACCEPT (28.42.12.1" ; box "BLOCK 1Y SUSPEND TGRS TON (28.42.42.1)" ;
  box "BLOCK 2Y SUSPEND TGRS TON (28.42.43.1)" ; box "BLOCK INITIATION OF Y-Z XFER (28.15.60.1)"
- box "COND 1Y • 2Y IDC TON CKTS (28.41.71.1)" ; box "COND IF1Y E TGR TON CKTS (28.41.21.1)"
- box "I LAST HALF CORR CYCLE (34.08.31.1)" ; box "I CHECK E NOT M IC (38.03.03.1)"
- No printed time or count (bit ranges only: "ICA 0-16", "ICR 0-16").

### Uncertain on this figure
- Overbar extent in hex RST1 + RST 2E • / ICADV E 1 LTH (28.41.41.1).
- Overbar structure in hex SUSPEND IF2Y / LTH • IF2YE LTH • / SAR (28.41.41.1).
- "GI" vs "GT" in GI ICA 0-16 TO ICR 0-16 (21.02.01.1).
- "JCADV" vs "ICADV" in BLOCK JCADV E1 TGR TON (28.41.41.1).
- I LAST HALF CORR CYCLE (34.08.31.1): the "3" of ".31." has a stray mark over it (3 vs 8 not fully excluded).
- Exit of hex IWC1E•NM (28.41.51.1) has no YES/NO label.

===================================================================================================
## Not read with confidence (consolidated, all five figures)

General: wherever a horizontal rule sits between two text rows of a hexagon it has been read as an overbar on the
row BELOW it; the horizontal extent given is what was measured on 300-600% crops, but for multi-row hexagons the
logical grouping is not certain. Small open "o" operators have been transcribed as "o", not normalised to "•".
None of the pages carries a printed time or count.

Fig 3.1.1 (p63)
- box TURN OFF IF2Y MI TGR (28.41.31.1): "MI" vs "M1".
- hex IF1Y NE LTH • / OPN FETCH REQ / LTH (28.41.22.1): overbar extent (over OPN FETCH REQ and over LTH).
- hex SABR • SUSPEND / IF1Y LTH • ACCEPT / OR COMPARE (28.41.21.1): overbars read over SUSPEND and over IF1Y LTH.
- hex RECOVERY • / REPEAT • / SUSPEND (28.41.22.1): overbars read over REPEAT and over SUSPEND.
- hex 2Y NOT BUSY / ANTIC • NO CHRK / SINGLE ERR • SBC (28.41.31.1): "CHRK" runs into the border.
- hex IF1Y E o M / LTH + IF2Y / E o M LTH (28.41.21.1): open "o" operator.
- scan-line-crossed ALD numbers: BLOCK ICADV E1 TURN ON (28.41.41.1); BLOCK SLLI TURN ON (28.79.42.1);
  BLOCK ICADV E1 TURN OFF • E2 TURN ON (28.41.41.1).
- line TO LA LD SEQ FPL4 (28.13.14.1) here vs (28.13.41.1) in Fig 3.1.3 - both transcribed as printed.
- cross-figure differences in ALD numbers, each transcribed as printed and each read clearly:
  ESTABLISH IC FETCH PRIORITY (28.42.12.1) in Fig 3.1.1 vs (28.20.23.1) in Fig 3.1.3;
  BLOCK ICFO2Y TURN ON (28.41.23.1) in Fig 3.1.1 vs (28.41.33.1) in Fig 3.1.3.

Fig 3.1.2 (p64)
- hex RST1 M • RST / CHK CTLS • SABR / o IC SELECT 1Y (28.41.23.1): overbar extents; open "o".
- hex INSTR CHK EN / • ICWA OFF • CHKR / SINGLE ERR • SAC • / SUSPEND IF1Y LTH (28.41.51.1): overbar extents.
- hex ICOR E • NM • / IWC1 M TGR OFF (no ALD): one long overbar, possibly a second over NM.
- box I CHE E o NM TC (38.03.03.1): "CHE", open "o", "TC" (compare "I CHK E • ~M IC (38.03.03.1)" in Fig 3.1.4).
- hex NO CHKR / SINGLE ERR (28.41.51.1): scan line; overbar cannot be ruled in or out.
- hex IC SELECT 1Y (28.41.23.1): exit unlabelled.
- box COND ICOR TURN ON CKT (28.41.71.1): number on a scan line.
- box BLOCK ICW1 ECC CHK (28.44.14.1): "ICW1" as printed.

Fig 3.1.3 (p65)
- hex END IC / SUSPENSION • IF / 2Y FETCH REQ LTH (28.41.31.1): overbar structure not resolved.
- hex 2Y BEING EMPTIED (28.42.11.1): free-standing rule above the text.
- hex ACC + COMP • / SABR • SUSPEND / IF2Y LTH (28.41.31.1): possible overbar on COMP; exit unlabelled.
- hex CARRY OUT OF / ICR 17 • RCY • / PROG HLT • SAC • / ICADV M OFF o / ZRMT COA CTH (28.41.41.1): "CTH"; open "o"; overbar extents.
- hex ZRMT COA LTH • / ACC + COMP • SAC • RCY / PROG HLT • ICADV M / OFF • CARRY OUT OF / ICR 17 (28.41.41.1): overbar extents.
- hex IF2Y E TGR ON / • RST1 + RST2 • / SUSPEND (28.41.32.1): overbars read over RST1, RST2 (separately) and SUSPEND.
- hex SUSPEND / IF2Y (28.41.31.1): overbars read over both rows; scan smear.
- exit labels: "NE • M" (NO of IF2Y E LTH; possible overbar), "E o M" (its YES), "E • M" (YES of IF2Y E TGR ON).
- box TURN ON ICBC 2Y TGR (28.33.41.1): as printed.
- line TO LA LD SEQ FPR4 (28.14.41.1): struck by a scan line.
- box BLOCK IF1Y E TURN OFF: no ALD number seen.

Fig 3.1.4 (p66)
- hex IC SELECT / 2Y • SABR • / RST1 M o RST / CHK CTLS (28.41.33.1): overbar extents; open "o".
- hex SAC • SUSPEND / 2Y • NO CHKR SING / ERR • INSTR CHK EN • / ALLOW 2Y INSTR / CHK (28.41.61.1): overbars read over SUSPEND and 2Y.
- hex IWC2 M TGR / OFF • BLOCK / IWC2 ECC CHK (28.41.61.1): overbars read over BLOCK and IWC2 ECC CHK.
- damaged final "1" in BLOCK XSF4 TON (28.80.24.1) and GATE ICOB TO 2Y (28.44.16.1).

Fig 3.1.5 (p67)
- hex RST1 + RST 2E • / ICADV E 1 LTH (28.41.41.1): overbar extent.
- hex SUSPEND IF2Y / LTH • IF2YE LTH • / SAR (28.41.41.1): overbar structure.
- box GI ICA 0-16 TO ICR 0-16 (21.02.01.1): "GI"/"GT"; damaged hyphen.
- box BLOCK JCADV E1 TGR TON (28.41.41.1): "JCADV"/"ICADV".
- box I LAST HALF CORR CYCLE (34.08.31.1): mark over the "3".
- hex IWC1E•NM (28.41.51.1): exit unlabelled.

Pages/tiles not finished: none (f63-T/B through f67-T/B all transcribed).

# APPENDIX B -- reader transcription

# part_b — I UNIT FLOW DIAGRAMS, PDF pages 68-73 (reader "b")

Reading notes that apply to every page in this part:
- The pre-cut tiles fNN-T/B are 1870 px wide but the upright page r-NN.png is 2200 px wide; the tiles cut off
  a strip on the right (and the margin text). I therefore read each page from the tiles PLUS my own crops of
  r-NN.png (iu/tiles/zoom-b-NN-*.png).
- `~X` = overbar printed over X. "no YES label" means the hexagon's exit line is drawn but no YES/NO is printed.
- "dot" = a printed junction dot. Where lines meet at a corner with no dot I say so.

---------------------------------------------------------------------------------------------------------

## FIGURE 3.1.10.  ZR MOD REQ TRIGGER AND MOD ZR SEQUENCER   (PDF page 72)

- Caption as printed (two lines): "FIGURE 3.1.10.  ZR MOD REQ TRIGGER" / "AND MOD ZR SEQUENCER"
- Page tag: 1-19/1-20        Date: 2/1/62
- Heading: "I UNIT FLOW DIAGRAMS"      Manual tag: "M3-04-3"
- Applicability note: "CPU 7101 / SER. NO. 30,004 / AND HIGHER"

### Boxes and connections

Turn-on conditions (four hexagons in a row above the trigger; each has a YES exit; the four YES lines join one
horizontal line, which drops through a line labelled "TON" into the top of the trigger box):

  hex T1 (leftmost), 7 text lines + ALD, with overbars as printed:
        SBC • YL-ZRE•~IYLD
        ~(BRC • UNCOND + BIT)
        ~(BR CL IYL + BIT BR DEC) •
        DEC MOD REQ FR IY •
        ~IY28 + ~IY29 + ~IY30 +
        ~IY31 • ~(IMM IX IYL) +
        ~(NOT FW NOT S)
        (28.62.21.1)
      Overbar detail (read at 500%): line 1 has a bar over "IYLD" only. A full-width bar is printed above
      line 2, spanning "BRC • UNCOND + BIT". A full-width bar is printed above line 3, spanning
      "BR CL IYL + BIT BR DEC" (not over the trailing •). Whether these are one overbar continuing from IYLD
      through "...BIT BR DEC" across the line breaks, or separate bars, cannot be told from the print.
      Line 4 has no bar. Line 5: separate bars over IY28, IY29, IY30. Line 6: bar over IY31, separate bar over
      "IMM IX IYL". Line 7: a bar above "NOT FW NOT S" (spans the whole phrase).
      ALD number is printed 28.62.21.1 (the other three turn-on hexagons and the trigger print 28.26.21.1).
      --YES--> TON line
  hex T2:  SBC • YL-ZRE • IY31 • / DEC MOD REQ FR IYL • / IYL BRC • BIT BR DEC + / UNCOND + BIT BR CL / IYL (28.26.21.1)
      (no overbars seen)   --YES--> TON line
  hex T3:  SBC • IYR MOD / DEC • YR-ZRE (28.26.21.1)      --YES--> TON line
  hex T4:  SET MOD / REQ TGR (28.26.21.1)                 --YES--> TON line

  --TON--> box (trigger): ZR MOD REQ TGR (28.26.21.1)

Output of ZR MOD REQ TGR: one line down from the box to a horizontal bus (dot). The bus feeds, left to right:

  (a) left end of bus, down a vertical with a dot at each box (unconditional):
        box: BLOCK YL-ZL TON (28.15.70.1)
        box: BLOCK IHW RDY TON (28.26.11.1)
        box: BLOCK GEN OF / PREV ZR PREP COMP (28.27.32.1)
        box: BLOCK IHW EX / ZR TGR TON (28.26.11.1)
  (b) hex: YL-ZR M (28.15.12.1)  --YES--> line down, on which (dot) hangs
        box: BLOCK Y-Z / START TGR TON (28.26.11.1)
        and which continues down (second dot, see (c)) into the top of
        hex: ZR WAS IHW (28.15.71.1)  --right exit, no YES label--> box: Y-Z MOD REQ (28.70.42.1)
  (c) hex: YR-ZR M (28.15.61.1)  --YES--> line down then left, joining (dot) the YES line of (b) between the
        BLOCK Y-Z START TGR TON box and the ZR WAS IHW hexagon. (So as drawn the YES lines of YL-ZR M and
        YR-ZR M are one net carrying BLOCK Y-Z START TGR TON and ZR WAS IHW.)
  (d) hex: SAC • YR-ZR M (28.15.20.1)  --YES--\
  (e) hex: YL-ZR M • / SAC   (no ALD number printed)  --YES--/  the two YES lines join (dot) and run down a
        line labelled "TON MOD ZR SEQUENCER" into the top of the MOD ZR SEQUENCER bar
  (f) hex (right end of bus): ~(Y-Z START) • / MOD ZR NOT M (28.15.30.1)   [overbar over "Y-Z START" only]
        --YES--> box: BLOCK YR-ZL TON   (no ALD number printed in this box)

Bar (sequencer): MOD ZR SEQUENCER (28.15.20.1)      outputs labelled, left to right:  E    E•M    M

  E output (vertical line down from the bar):
    first dot -> horizontal bus running left, feeding:
        left vertical (dots), unconditional:
            box: TON MOD ZR / M TGR (28.15.20.1)
            box: HOLD DATA / SELECT PREP (28.96.45.1)
            box: Y-ZR M + MOD / ZR RST ZR TAGS (28.51.07.1)
        hex: SBC (28.15.10.1)  --YES--> box: TOF YL-ZR / M TGR (28.15.10.1)
        box: RESET ZR / ADDR  8 TGR (28.27.57.1)     [character between ADDR and TGR read as "8"; uncertain: 8 / B?]
    second dot (lower on the E line) -> horizontal bus running left, feeding:
        hex: IHW YL + / FW S + FW / NOT S (28.15.21.1)  --YES--> vertical with dots:
            box: Z 50 to ABB 18 (28.96.09.1)
            box: Z 32-49 to / ABB 0-17 PREP (28.96.09.1)
            box: Z 50 to ABB P2 / ADJ PAR Z 50-55 (28.96.08.1)
        hex: SBC (28.15.60.1)  --right exit, no YES label--> box: TOF YR-ZR / M TGR (28.15.60.1)
    E line then ends (below the second dot) at
        box: X 0-23 to ABB / • X 24-27 to ABB (28.96.01.1)      (unconditional)

  E•M output (vertical line down from the bar; drawn in line with the "TON MOD ZR SEQUENCER" line entering the
  top of the bar):
        dot -> box: Y-ZR + MOD ZR / COND ZR MA TAGS (28.51.01.1)      (unconditional)
        dot -> horizontal bus running left, feeding:
            hex: IHW YL + FW S + / FW NOT S (28.15.21.1)  --YES--> vertical with dot:
                box: GT AOB 18 to ZR (28.27.51.1)
                box: GT AOB 19 to ZR (28.27.51.1)
            hex: YL FP (28.15.21.1)   top joined to this bus (dot). Its right-hand vertex is joined by a short
                line to a dot on the E•M vertical line itself (no YES label).
        the E•M vertical line then ends at
            box: GT AOB 18 to ZR (28.27.51.1)     (a second box with this same text)
        [connection not followed with confidence: as drawn, the YL FP hexagon's exit lands on the E•M line just
         above the point where that line ends at this second GT AOB 18 to ZR box; the print does not show
         whether that box is gated by YL FP or is an unconditional E•M action.]

  M output (vertical line down from the bar):
    first dot -> horizontal bus running right to a second vertical (the "right column", below)
    on the M vertical itself, in order downward:
        dot -> box: PREV ZR PREP / COMP (28.44.25.1)
        dot -> box: COND YR-ZL TON CKT (28.15.30.1)
        branch right (corner, no dot) -> top of
            hex: ZR IHW TGR ON (28.26.61.1)  --YES--> vertical with dot:
                box: COND IHW RDY / ZR TON CKT • IHW / EX ZR TON CKT (28.26.11.1)
              [this YES vertical continues below the box and ends in a corner (no dot) on the horizontal line
               of the next item; a scan fold line runs along that same horizontal. Connection not followed
               with confidence.]
        dot -> horizontal line (dot at the top of the next hexagon) ->
            hex: SAC (28.15.21.1)  --YES--> vertical with dot:
                box: TON HW RDY TGR (28.26.11.1)        [printed "HW", not "IHW"]
                box: TON IHW EX TGR (28.26.11.1)
        bottom end of the M vertical, turning right -> top of
            hex: SAC • ZL MT ON / ACC • ACC + COMP • / FW S (28.15.70.1)     (no overbar; a small stray mark
                 follows "ON") --right exit, no YES label--> vertical with dot:
                box: TON YL-ZL / SEQUENCER (28.15.70.1)
                box: BLOCK YR-ZL / TON CKT (28.15.30.1)
    right column (second vertical fed from the first M dot), in order downward:
        dot -> box: TOF MOD ZR / E TGR (28.15.20.1)
        dot -> hex: FW NOT S (28.15.21.1)  --YES--> vertical with dot:
                box: COND WBC + / DEC TON CKT (28.15.80.1)
                the same YES vertical continues down past that box, turns left and enters the top of
                hex: ZR NOT FP CL • / FW S + FW NOT S (28.15.81.1)   [ALD struck through by the scan fold line;
                     uncertain: first group 28 / 29?, and 81 / 61?]
                     --YES--> box: ANTIC FW / TGR TON (28.51.24.1)
        bottom end of the right column, turning right -> top of
            hex: ZR FP CL (28.51.24.1)  --YES--> vertical with dot:
                box: COND MOD ZR / M TGR TOF (28.15.20.1)
                box: INSTR PREP / COMP ZR (28.27.32.1)

### Noted (Fig 3.1.10)
- "SBC • YL-ZRE•~IYLD ~(BRC • UNCOND + BIT) ~(BR CL IYL + BIT BR DEC) • DEC MOD REQ FR IY • ~IY28 + ~IY29 + ~IY30 + ~IY31 • ~(IMM IX IYL) + ~(NOT FW NOT S)" (28.62.21.1)   [MOD, BR, IX]
- "SBC • YL-ZRE • IY31 • DEC MOD REQ FR IYL • IYL BRC • BIT BR DEC + UNCOND + BIT BR CL IYL" (28.26.21.1)
- "SBC • IYR MOD DEC • YR-ZRE" (28.26.21.1)
- "SET MOD REQ TGR" (28.26.21.1)
- "ZR MOD REQ TGR" (28.26.21.1)
- "BLOCK YL-ZL TON" (28.15.70.1)
- "BLOCK IHW RDY TON" (28.26.11.1)
- "BLOCK GEN OF PREV ZR PREP COMP" (28.27.32.1)
- "BLOCK IHW EX ZR TGR TON" (28.26.11.1)
- "BLOCK Y-Z START TGR TON" (28.26.11.1)
- "Y-Z MOD REQ" (28.70.42.1)
- "~(Y-Z START) • MOD ZR NOT M" (28.15.30.1)
- "BLOCK YR-ZL TON" (no ALD number printed)
- "TON MOD ZR SEQUENCER" (line label); "MOD ZR SEQUENCER" (28.15.20.1)
- "TON MOD ZR M TGR" (28.15.20.1)
- "Y-ZR M + MOD ZR RST ZR TAGS" (28.51.07.1)
- "X 0-23 to ABB • X 24-27 to ABB" (28.96.01.1)
- "Y-ZR + MOD ZR COND ZR MA TAGS" (28.51.01.1)
- "TOF MOD ZR E TGR" (28.15.20.1)
- "COND MOD ZR M TGR TOF" (28.15.20.1)
- "BLOCK YR-ZL TON CKT" (28.15.30.1)
- "SAC • ZL MT ON ACC • ACC + COMP • FW S" (28.15.70.1)   [COMP]
- "PREV ZR PREP COMP" (28.44.25.1); "INSTR PREP COMP ZR" (28.27.32.1)   [COMP]
- No printed time or count on this page.

---------------------------------------------------------------------------------------------------------

## FIGURE 3.1.11.  ZR BLOCK AND SUSPEND TRIGGERS   (PDF page 73)

- Caption as printed (two lines): "FIGURE 3.1.11.  ZR BLOCK AND" / "SUSPEND TRIGGERS"
- Page tag: 1-21/1-22        Date: 2/1/62
- Heading: "I UNIT FLOW DIAGRAMS"      Manual tag: "M3-04-3"
- Applicability note: "CPU 7101 / SER. NO. 30,004 / AND HIGHER"

Glyph note for this page: the lettering has a digit "1" with a flag (as in the ALD numbers, "IF1Y", "ICBC1Y",
"IWC1", "BLOK 1Y") and a plain vertical stroke for the letter "I". In the left-hand groups the name printed
where the right-hand groups print "2Y" is a plain stroke + Y; I transcribe it "IY" as printed
[uncertain: IY / 1Y?]. Read at 600%.

The page holds four separate trigger groups, none connected to another. Every action box hangs on a single
vertical line dropping from the middle of its trigger bar (boxes left and right of the line, dots at the
junctions); all are unconditional outputs of the trigger except where a hexagon is listed.

### Group 1 (upper left)

  hex: SBC • INSTR / PREP TON / ZR BLOCK IY      (no ALD number printed in this hexagon)
      --YES--> line labelled TON -->
  bar: ZR BLOCK IY TGR (28.42.41.1)
      left of the output line, top to bottom:
          box: BLOCK GEN OF / IY NOT BUSY (28.42.12.1)
          box: BLOCK ESTAB OF / IC FTH PRIORITY (28.42.12.1)
          box: BLOCK GEN OF IY / NOT BUSY ANTIC (28.42.12.1)      (line ends here)
      right of the output line, top to bottom:
          box: BLOCK GEN OF IY NOT / BUSY ANTIC ON ACC (28.42.12.1)
          box: BLOCK GEN OF I / EX USE IY (28.42.12.1)

### Group 2 (upper right)

  hex: SBC • INSTR / PREP TON ZR / BLOCK  2Y (28.42.41.1)
      --YES--> line labelled TON -->
  bar: ZR BLOCK 2Y TGR (28.42.41.1)
      left, top to bottom:
          box: BLOCK GEN OF 2Y / NOT BUSY (28.42.12.1)
          box: BLOCK ESTAB OF / IC FTH PRIORITY (28.42.12.1)
          box: BLOCK GEN OF 2Y / NOT BUSY ANTIC      (no ALD number printed in this box)   (line ends here)
      right, top to bottom:
          box: BLOCK GEN OF 2Y NOT / BUSY ANTIC ON ACC (28.42.12.1)
          box: BLOCK BRANCH / CKT IF2Y TON (28.41.31.1)

### Group 3 (lower left)

  Turn-on conditions (two hexagons; YES lines join at a dot, then a line labelled TON):
      hex: TON SUSPEND / TGR • SBC (28.42.42.1)                      --YES-->
      hex: BR Y-Z YFER / TON ZR SPND / IY • SBC (28.42.42.1)         --YES-->
           [first line's last word is printed "YFER" as far as I can read it; uncertain: YFER / XFER?
            (the matching hexagon in Group 4 clearly prints "XFER")]
  bar: ZR SPND TGR IY (28.42.42.1)
      left, top to bottom:
          box: BLOCK IF1Y  TOF (28.41 21.1)        [no dot printed between 41 and 21]
          box: BLOCK IF1Y PNL / KEY REQ (28.41.22.1)
          box: BLOCK IF1Y / FTH REQ (28.41.22.1)
          box: BLOCK ICFO1Y / TON (28.41.23.1)     [uncertain: letter O / digit 0 in "ICFO1Y"]
          box: BLOCK ICBC1Y / TON (28.41.23.1)
          box: BLOCK IWC1 / TON (28.41.51.1)
          box: BLOCK GEN OF IF1Y / ONE TO MAB 15 (28.41.22.1)       (line ends here)
      right, top to bottom:
          box: BLOCK GT OF ICR / 0-16 TO MAB (28.41.22.1)
          box: BLOCK GT OF ICA / 0-16 TO MAB (28.41.22.1)
          box: BLOCK GEN OF / IF1Y RETURN ADR (28.41.22.1)
          box: BLOCK IF1Y / IND TOF (28.41.22.1)
          box: COND IF2Y / TON CKT (28.41.22.1)
          box: BLOCK ESTAB OF / IC  FTH PRIORITY (28.41.22.1)
      [in "IF1Y" throughout this group the third character is read as the digit 1; uncertain: IF1Y / IFIY?]

### Group 4 (lower right)

  Turn-on conditions (three hexagons; the three YES lines join one horizontal line, dot, then a line labelled TON):
      hex (leftmost), 5 text lines + ALD, overbars as printed:
            SAR • IWCI E • NO
            CHKR SING ERR •
            IYLD BRU + BRC •
            ~(BLOK 1Y BR TON ZR)
            ~(SPND 2Y) • ICOA NE
            (28.42.43.1)
          Overbar detail (read at 700%): a bar is printed above the whole of line 4 "BLOK 1Y BR TON ZR" and a
          bar above "SPND 2Y" on line 5 (not over "• ICOA NE"). I read these as one overbar continued across the
          line break, but the print cannot distinguish that from two separate bars. No bars on lines 1-3.
          [uncertain: "IWCI E" could be "IWC1 E" (last character before E is a plain stroke);
           "ICOA NE" -- third character O / 0 not distinguishable; text runs into the hexagon's right edge and
           may be clipped after "NE".]
          --YES-->
      hex: SBC • BR Y-Z / XFER TON ZR / SPND 2 Y (28.42.43.1)        --YES-->
      hex: E1 TON 2Y / SPND TGR • / SBC (28.42.43.1)                 --YES-->
  bar: ZR SPND 2Y TGR (28.42.43.1)
      left, top to bottom:
          box: BLOCK GEN OF IC / FTH M • IC FTH MEM (28.41.21.1)
          box: BLOCK ICADV E2 TON (28.41.41.1)
          box: BLOCK GEN OF IF2Y / ONE TO MAB 15 (28.41.32.1)
          box: BLOCK GEN OF IF2Y / GT ICR 0-16 TO MAB (28.41.32.1)
          box: BLOCK GEN OF IF2Y / GT ICA 0-16 TO MAB (28.41.32.1)
          box: BLOCK IF2Y IND / TOF (28.42.32.1)        [printed 28.42.32.1 -- second group "42", unlike its neighbours' "41"]
          box: BLOCK GEN OF IF2Y / RETURN ADR (28.41.32.1)
          box: BLOCK GEN OF / IC FTH M (28.41.21.1)
          box: BLOCK GEN OF / IC FTH MEM (28.41.21.1)
      right, top to bottom:
          box: BLOCK IF1YE / TON (28.41.21.1)
          box: BLOCK ESTAB OF / IL FTH PRIORITY (28.42.12.1)     [printed "IL" as I read it at 500%; uncertain: IL / IC?]
          box: BLOCK IF2Y FTH REQ (28.41.32.1)
          box: BLOCK IF2Y PNL / KEY REQ (28.41.32.1)
          box: BLOCK IF2Y TOF (28.41.31.1)
          box: BLOCK IC F02Y / TON (28.41.33.1)                  [uncertain: 0 / O in "F02Y"; printed with a space after IC]
          box: BLOCK ICBC2Y TON (28.41.33.1)
          box: BLOCK ICADV E1 TOF (28.41.41.1)
          box: BLOCK IWC2 TON (28.41.61.1)
      the output line then ends in the top of
          hex: IF2Y M (28.41.32.1)  --YES--> box: COND ICADV / E2 TON (28.41.41.1)

### Noted (Fig 3.1.11)
- "SBC • INSTR PREP TON ZR BLOCK IY" (no ALD printed); "ZR BLOCK IY TGR" (28.42.41.1)
- "BLOCK GEN OF IY NOT BUSY" (28.42.12.1); "BLOCK ESTAB OF IC FTH PRIORITY" (28.42.12.1); "BLOCK GEN OF IY NOT BUSY ANTIC" (28.42.12.1); "BLOCK GEN OF IY NOT BUSY ANTIC ON ACC" (28.42.12.1); "BLOCK GEN OF I EX USE IY" (28.42.12.1)
- "SBC • INSTR PREP TON ZR BLOCK  2Y" (28.42.41.1); "ZR BLOCK 2Y TGR" (28.42.41.1)
- "BLOCK GEN OF 2Y NOT BUSY" (28.42.12.1); "BLOCK ESTAB OF IC FTH PRIORITY" (28.42.12.1); "BLOCK GEN OF 2Y NOT BUSY ANTIC" (no ALD printed); "BLOCK GEN OF 2Y NOT BUSY ANTIC ON ACC" (28.42.12.1); "BLOCK BRANCH CKT IF2Y TON" (28.41.31.1)
- "TON SUSPEND TGR • SBC" (28.42.42.1)
- "BR Y-Z YFER TON ZR SPND IY • SBC" (28.42.42.1)
- "ZR SPND TGR IY" (28.42.42.1)
- every box under ZR SPND TGR IY except "COND IF2Y TON CKT" begins BLOCK (list above); those naming IND / RETURN ADR / MAB:
  "BLOCK IF1Y IND TOF" (28.41.22.1); "BLOCK GEN OF IF1Y RETURN ADR" (28.41.22.1); "BLOCK GT OF ICR 0-16 TO MAB" (28.41.22.1); "BLOCK GT OF ICA 0-16 TO MAB" (28.41.22.1); "BLOCK GEN OF IF1Y ONE TO MAB 15" (28.41.22.1)
- "SAR • IWCI E • NO CHKR SING ERR • IYLD BRU + BRC • ~(BLOK 1Y BR TON ZR) ~(SPND 2Y) • ICOA NE" (28.42.43.1)
- "SBC • BR Y-Z XFER TON ZR SPND 2 Y" (28.42.43.1)
- "E1 TON 2Y SPND TGR • SBC" (28.42.43.1)
- "ZR SPND 2Y TGR" (28.42.43.1)
- every box under ZR SPND 2Y TGR begins BLOCK (list above); those naming IND / RETURN ADR / MAB:
  "BLOCK IF2Y IND TOF" (28.42.32.1); "BLOCK GEN OF IF2Y RETURN ADR" (28.41.32.1); "BLOCK GEN OF IF2Y ONE TO MAB 15" (28.41.32.1); "BLOCK GEN OF IF2Y GT ICR 0-16 TO MAB" (28.41.32.1); "BLOCK GEN OF IF2Y GT ICA 0-16 TO MAB" (28.41.32.1)
- No printed time or count on this page.

---------------------------------------------------------------------------------------------------------

## FIGURE 3.1.6.  Y-Z START TRIGGER AND YR-ZL TRANSFER SEQUENCER   (PDF page 68)

- Caption as printed (two lines): "FIGURE 3.1.6.  Y-Z START TRIGGER AND" / "YR-ZL TRANSFER SEQUENCER"
- Page tag: 1-11/1-12        Date: 2/1/62
- Heading: "I UNIT FLOW DIAGRAMS"      Manual tag: "M3-04-3"
- Applicability note: "CPU 7101 / SER. NO. 30,004 / AND HIGHER"

Read from a 3x4 grid of 240% crops of r-68.png plus 500% crops of every multi-line hexagon.
On this page the digit 1 is drawn with a flag, so "1Y" / "2Y" / "1BIT" are read as digits.

### Part 1: Y-Z START TGR (upper left; not connected by any line to the sequencer part)

  Turn-on condition:
    hex:  ~(YL-ZR • R MOD)
          + ~(YR-ZL • R MOD) +
          ~(XF + DEC ZL MC) •
          SBC
          (28.26.11.1)
        Overbars as printed (500%): line 1, a bar over the whole of "YL-ZR • R MOD"; line 2, a bar over
        "YR-ZL • R MOD" (not over the leading "+" or the trailing "+"); line 3, a bar over "XF + DEC ZL MC"
        (not over the trailing •). "SBC" has no bar.
        --YES--> line labelled TON -->
  bar: Y-Z START TGR (28.26.11.1)
    output line down to a dot, from which:
      left:  box: COND YR-ZR / TON CKT (28.15.60.1)                 (unconditional)
      down:  hex: CHK M CORR • / CD Y LEFT • ZL / IHW (28.5.10.1)   [ALD printed "28.5.10.1" -- only three groups'
                   worth of digits before the .1; as printed]
                 --YES--> box: COND YL-ZR / TON CKT (28.15.10.1)
      right: hex: CHK M CORR • / NOT CD Y RIGHT • / FPR BLOCK Y-Z (28.15.30.1)     (no overbars)
                 --YES--> box: COND YR-ZL / TON CKT (28.15.30.1)

### Part 2: YR-ZL TRANSFER SEQUENCER

  Turn-on conditions (two hexagons at upper right, one above the other; their YES lines join at a dot on one
  vertical line, which runs down, then left, then down a line labelled TON into the top of the bar):

    hex R1 (upper):
          ACC + COM • CD Y
          RIGHT • ~(FPR BLOCK Y-Z) •
          CHK M COR NOT E • YL-
          ZR NOT MOD R + Y-Z START +
          ~(MOD ZR NOT M) • ZL MT ON
          ACC • FW NOTS + HW • SAC •
          NOT CHKR SING ERR
          (28.15.30.1)
        Overbars as printed: line 2, a bar over "FPR BLOCK Y-Z" (it may run on over the trailing •);
        line 5, a bar over "MOD ZR NOT M". No other bars. "NOTS" is printed without a space. The dot after
        "NOT E" on line 3 is printed as a small open ring.
    hex R2 (lower):
          SAC • ZL MT • ~FPR
          ~(BLOCK Y)-Z • CD YR •
          CHK M COR NOT E •
          YL-ZR NOT MOD
          R + Y-Z START +
          ~(MOD ZR NOT M) • FW
          NOT S + HW • NOT
          CHKR SING ERR
          (28.15.30.1)
        Overbars as printed: line 1, a short bar over "FPR" (it touches the hexagon's top edge;
        [uncertain: bar present / part of the border?]); line 2, a bar over about "BLOCK Y" (it stops before
        "-Z"); I take these as one overbar over "FPR BLOCK Y-Z" broken across the line, as in hex R1, but that is
        an inference. Line 6, a bar over "MOD ZR NOT M". No other bars.

  bar: YR-ZL TRANSFER SEQUENCER (28.15.30.1)        outputs labelled, left to right:  E    E•M    M

  ---- E output (long vertical line down from the bar) ----
  First dot on the E line: a horizontal bus running LEFT to the far-left vertical ("column A"), with a dot over
  the FW NOT S hexagon (head of "column B"); and a short branch RIGHT (corner) to the YR-ZL M TGR OFF hexagon.

    Branch right:
      hex: YR-ZL M TGR / OFF      (no ALD number printed)
          --YES--> line down, with the label "E • ~M" printed beside it (overbar over the M) -->
          box: PREP RST / X  0-63 (28.86.57.1)

    Column A (far-left vertical; every box on its right joined by a dot; unconditional E actions), top to bottom:
          box: TOF ZLNA • ZLXA • / ZLSA TGRS (28.51.08.1)
              -- at this same dot a line runs LEFT to the margin box:
              box: RESET ZL / ADDR 8 TGR (28.27.57.1)        [uncertain: 8 / B in "ADDR 8 TGR"]
          box: TOF CD YR-Z (28.26.10.1)
          box: XS READ P (24.00.09.1)                       [prefix printed 24, not 28]
          box: COND  ZR • ZL  IHW / TGRS TON CKTS (28.26.61.1)
          box: COND ZL DEC / TGR TON CKT (28.27.30.1)
          box: COND ZR WAS / IHW TGR TON CKT (28.15.51.1)
          box: COND MOD ZR / TOF CKT (28.15.20.1)
          box: COND 1 BIT MOD / TON CKT (28.26.23.1)
          box: COND ZL MOD / TON CKT (28.26.23.1)
          box: COND ZL FP CL / TGRS TON CKTS (28.26.56.1)
          box: COND MOD L / TGR TON CKT (28.26.27.1)
          box: ~(INH NIDC SET) / ~(IDC CR XAC) (28.86.55.1)     [a bar is printed over each of the two text lines]
          box: COND ZL IDC / TON • TOF CKTS (28.51.03.1)
          box: COND ZLAD TON • / TOF CKTS (28.51.04.1)
          box: COND ZLIF TON• / TOF CKTS (28.51.05.1)
          box: TOF FP 3 M (28.13.31.1)
          box: TOF FP 4 M (28.13.41.1)
          box: TOF VFL 5 M (28.11.51.1)
          dot -> long line right to box: COND ZDS • ZDF / TOF CKTS (28.51.06.1)   (this box is drawn over in the
                 column-B area, below the end of column B; unconditional, fed from column A)
          box: TOF BROK TOR (28.71.40.1)
          dot -> hex: HW CL 1Y • / CD 1Y - ZL • / SBC (28.26.58.1)     --YES--\
          dot -> hex: HW CL 2Y • / CD 2 Y-ZL • / SBC (28.26.58.1)      --YES--/ the two YES lines join (dot) ->
                 box: TOF 1P C 1•2• / 3•4•6 TGRS (28.26.58.1)
                      [first line read at 500% as "TOF 1P C 1•2•"; uncertain: "1P C" may be a damaged "FP CL";
                       second line "3•4•6" as printed (the last digit is 6, not 5)]
          box: HOLD DATA / SELECT PREP (28.96.43.1)
          box: TOF Y-Z / START TGR (28.26.11.1)
          box: TOF FW WBC / TGRS (28.22.02.1)                (column A ends here)

    Two margin boxes at the far left, outside column A. Each has a long horizontal line running right, which
    CROSSES column A with NO dot and ends in a large dot on the column-B vertical:
          box: BLOCK ZR / FP6 RESET / 28.26.51.1      (ALD printed without parentheses)
               -- its line meets column B between "TON FW NOT • S TGR" and "BLOCK ZR FP TGR TON"
          box: BLOCK ZR / FP6 TON (28.26.51.1)
               -- its line meets column B between "BLOCK RESET OF ZR FP 1" and "BLOCK ZR FP 2 TON"
          (so as drawn these two boxes are on the column-B net, i.e. gated by the FW NOT S hexagon)

    Column B (second vertical from the left):
      hex: FW NOT S / 1Y + 2Y • SBC (28.26.60.1)    (fed from the E bus by a dot above it)
          --YES--> dot heading the column-B vertical; boxes on its LEFT joined by dots, top to bottom:
          box: TON FW NOT • / S TGR (28.26.60.1)
          (dot: line from margin box BLOCK ZR FP6 RESET)
          box: BLOCK ZR FP / TGR TON (28.26.62.1)
          box: BLOCK SETTING / OF ZR FP 1 (28.26.50.1)
          box: BLOCK RESET OF / ZR FP 1 (28.26.50.1)
          (dot: line from margin box BLOCK ZR FP6 TON)
          box: BLOCK ZR FP / 2 TON (28. 26.51.1)
          box: BLOCK RESET OF / ZR FP 2 (28.26.51.1)
          box: BLOCK ZR FP / 3 TON (28.26.51.1)
          box: BLOCK RESET / ZR FP 3 (28.26.51.1)
          box: BLOCK ZR / FP 4 TON (28.26.51.1)
          box: BLOCK ZR FP / 4 RESET (28.26.51.1)
          box: 2Y LD FP TO / SAD - LID DCDR (28.62.13.1)
          dot -> hex: CD 2Y-ZR • / FW S + HW • / ~(FW ST 2Y) (28.26.61.1)    [bar over the whole third line]
                    --YES--> box: COND ZR IHW TON (28.26.61.1)
          end of column B (corner) -> hex: YL-ZRE • CD / 2Y-ZR • SBC (28.26.58.1)
                    --YES--> box: TOF FPR CL / 1 • 2 • 3 • 4 TGRS (28.26.58.1)

    Column C (third vertical). The YES line of the FW NOT S hexagon also continues RIGHT from the column-B dot
    and drops into the top of:
      hex: 1Y26 • ~(1Y 27) (28.26.20.1)     [bar printed over "1Y 27"; it looks like one bar with a thin spot
                                              between "1Y" and "27" -- uncertain: one bar / two bars]
          --YES--> column-C vertical; boxes on its LEFT joined by dots, top to bottom:
          box: 1YLD FP TO / SAD-LID DCDR (28.62.11.1)
          box: COND ZR FP / TGR TON (28.26.62.1)
          box: COND ZR FPI / TGR TON (28.26.62.1)           ["FPI" as printed; uncertain: FPI / FP1]
          box: COND FP CL / RESET LINES (28.36.51.1)        [second group printed "36"; read at 500%]
          box: BLOCK ZR / IHW TON (28.26.61.1)
          box: BLOCK TOF OF / FPR CL 1 • 2 • 3 • 4 (28.26.58.1)
          box: FWS + HW TO Y / DCD IHW CKTS (28.26.61.1)
          box: FWS + HW TO / Y DCD FP CKTS (28.26.62.1)     (column C ends here)
      (So column C is in series behind the FW NOT S hexagon: FW NOT S --YES--> 1Y26 • ~(1Y 27) --YES--> these.)

    Further down the E line itself, each from a dot on the E line:
      dot -> hex: ~(FP RDY ZR) • / SBC (28.15.10.1)      [bar over "FP RDY ZR"]
                --YES--> box: TOF YL-ZR / M TGR (28.15.10.1)
      dot -> hex: FP  CL  2YR • / SBC • CD 2Y-ZL (28.26.56.1)
                --YES--> box: COND ZL FP 1-4 / SET • RESET CKTS (28.26.56.1)
      dot -> hex: CD 1Y-ZL • / ~(1BIT MOD L) (28.15.31.1)     [bar over "1BIT MOD L"]
                --YES--> box: GT 1Y 60-63 / TO XAB 1-4 (28.15.61.1)
      dot -> hex: CD 2Y-ZL • / 1BIT MOD L (28.15.61.1)        [NO bar printed over "1BIT MOD L" in this hexagon
                                                                (500%); ALD printed 28.15.61.1, unlike the 28.15.31.1
                                                                of the other three]
                --YES--> box: GT 2Y 60-63 TO / XAB 1-4 (28.15.61.1)
      dot -> hex: CD 1Y-ZL • / 1BIT MOD L (28.15.31.1)        (no bar)
                --YES--> box: GT 1Y 63 TO XAB 4 (28.15.61.1)
      dot -> hex: CD 2Y-ZL • / 1BIT MOD L (28.15.31.1)        (no bar)
                --YES--> box: GT 2Y 63 to XAB 4 (28.15.61.1)
      bottom end of the E line: turns left along a horizontal that feeds two hexagons
            hex: CD 1Y-ZL (28.15.31.1)      (dot on the horizontal above it)   --YES--\
            hex: CD 2Y-ZL (28.15.31.1       (closing parenthesis not printed)  --YES--/ YES lines join (dot) ->
            vertical with dots:
                box: COND ZL FP / TON CKT (28.26.63.1)
                box: GT 2Y+1Y TO ABB / COND TAGS ZL / (28.26.10.1 / 28.27.30.1  28.27.40.1)    [three ALD numbers in one parenthesis]
                box: GT 2YR+1YR / TO ABB           (no ALD number printed)

  ---- E•M output (vertical line down from the bar) ----
          dot -> box: GT AOB TO ZL / (28.15.41.1 • / 28.15.71.1)       [two ALD numbers joined by •]
          end -> box: GT AOB TO ZL (28.27.57.1)
      (nothing else hangs on the E•M line)

  ---- M output (vertical line down from the bar) ----
      on the M vertical, in order downward:
          dot -> box: TOF YR - ZL E / TGR (28.15.30.1)
          dot -> box: COND MOD ZL / TGR TON (28.15.40.1)
          dot -> hex: ZL  IHW • ~BLOK / ~(XF + DEC) • NOT / IHW EX (28.15.50.1)
                    [overbars as printed: a bar over "BLOK" at the end of line 1; a bar over the start of line 2
                     covering "XF +" and reaching about half-way over "DEC". Presumably one overbar over
                     "BLOK XF + DEC" broken across the line -- uncertain. No bar over "NOT IHW EX".]
                    --YES--> line down into the top of
                    hex: NOT I EX / IN PROGRESS (28.15.50.1)
                        --YES--> box: COND XF + DEC / ZL TON CKT (28. 15.50.1)
          dot -> line LEFT then down into
                 hex: IHW RDY - ZR (28.15.32.1)
                    --YES--> line down, then left, to a vertical bus ("bus H") with a dot at every item.
                    Boxes on the LEFT of bus H, top to bottom:
                        box: BLOCK YR-ZL / M  TGR TOF / 28.15.30.1)        (opening parenthesis not printed)
                        box: COND LOP 4 TON (28.88.34.1)
                        box: COND LOP 5 TON (28.88.41.1)
                        box: COND DEC 1 TON (28.75.11.1)
                        box: COND LAM 1 TON (28.81.11.1)
                        box: COND TON EMF 1 (28.70.34.1)
                        box: COND XSF3 TON (28.71.11.1)
                        box: COND TON 1 EXP TGR (28.87.64.1)
                        box: COND DEC 3 TON (28.70.14.1)
                        box: COND EMF5 TON (28.70.21.1)
                        box: COND DEC 4 TON (28.79.14.1)
                        box: COND ADD 3 TON (28.75.51.1)        [a scan fold line runs through the top text line of this box]
                        box: (EMPTY -- a box is drawn with no text in it)        (bus H ends here)
                    Items on the RIGHT of bus H, top to bottom:
                        box: COND INTRPT / EN GEN CKTS (28.70.84.1)        (same dot as BLOCK YR-ZL M TGR TOF)
                        box: COND ADD 1 TON (28.75.71.1)                    (same dot as COND LOP 4 TON)
                        from the dot at COND LOP 5 TON:
                            hex: BE + BEW + BD / + SIC - BE - BEW - BD (28.89.32.1)
                                 [second line: the term after "SIC -" is badly printed; read "BE"; uncertain: BE / BL?]
                                 --YES--\
                        from the dot at COND LAM 1 TON:
                            hex: EX + RN (28.89.37.1)   --YES--/ the two YES lines join (dot) ->
                            box: ALLOW LARCY TON (28.42.81.1)
                        from the dot at COND TON 1 EXP TGR:
                            hex: BD + SIC - BD (28.70.84.1)
                                 --YES--> box: PRE - DSAB (37.51.03.1)       [prefix printed 37]
          dot -> hex: NOT ZL MOD / R • FW ~(NOT ST) + / ~(PROG IX) (28.15.32.1)
                    [overbars as printed: on line 2 a bar starting over the end of "FW" and covering "NOT ST";
                     above line 3 a bar covering "PROG IX" and running on a little past it. No bar on line 1.
                     uncertain where the line-2 bar starts (over "FW NOT ST" or only "NOT ST").]
                    --YES--> vertical with dot:
                        box: COND YL-ZR TON (28.15.10.1)
                        box: COND YR-ZR TON (28.15.60.1)
          dot -> hex: NOT ZL MOD / R •  ZL FP CL • NOT / IHW EX (28.15.32.1)      (no overbars)
                    --YES--> box: INSTR PREP / COMP ZL (28.27.32.1)
          bottom end of the M line (corner) ->
                 hex: ZL MOD R (28.15.32.1)
                    --YES--> vertical with dot:
                        box: BLOCK Y - Z / START TON (28.26.11.1)
                        box: COND XOF 1 TON (28.12.11.1)

### Noted (Fig 3.1.6)
- "~(YL-ZR • R MOD) + ~(YR-ZL • R MOD) + ~(XF + DEC ZL MC) • SBC" (28.26.11.1)    [MOD, XF]
- "CHK M CORR • NOT CD Y RIGHT • FPR BLOCK Y-Z" (28.15.30.1)
- "ACC + COM • CD Y RIGHT • ~(FPR BLOCK Y-Z) • CHK M COR NOT E • YL-ZR NOT MOD R + Y-Z START + ~(MOD ZR NOT M) • ZL MT ON ACC • FW NOTS + HW • SAC • NOT CHKR SING ERR" (28.15.30.1)
- "SAC • ZL MT • ~FPR ~(BLOCK Y)-Z • CD YR • CHK M COR NOT E • YL-ZR NOT MOD R + Y-Z START + ~(MOD ZR NOT M) • FW NOT S + HW • NOT CHKR SING ERR" (28.15.30.1)
- "RESET ZL ADDR 8 TGR" (28.27.57.1)
- "BLOCK ZR FP6 RESET 28.26.51.1"; "BLOCK ZR FP6 TON" (28.26.51.1)
- "XS READ P" (24.00.09.1)
- "COND MOD ZR TOF CKT" (28.15.20.1); "COND 1 BIT MOD TON CKT" (28.26.23.1); "COND ZL MOD TON CKT" (28.26.23.1); "COND MOD L TGR TON CKT" (28.26.27.1)
- "~(INH NIDC SET) ~(IDC CR XAC)" (28.86.55.1)      [XAC]
- "COND ZL IDC TON • TOF CKTS" (28.51.03.1)
- "TOF BROK TOR" (28.71.40.1)
- "BLOCK ZR FP TGR TON" (28.26.62.1); "BLOCK SETTING OF ZR FP 1" (28.26.50.1); "BLOCK RESET OF ZR FP 1" (28.26.50.1); "BLOCK ZR FP 2 TON" (28. 26.51.1); "BLOCK RESET OF ZR FP 2" (28.26.51.1); "BLOCK ZR FP 3 TON" (28.26.51.1); "BLOCK RESET ZR FP 3" (28.26.51.1); "BLOCK ZR FP 4 TON" (28.26.51.1); "BLOCK ZR FP 4 RESET" (28.26.51.1)
- "BLOCK ZR IHW TON" (28.26.61.1); "BLOCK TOF OF FPR CL 1 • 2 • 3 • 4" (28.26.58.1)
- "CD 1Y-ZL • ~(1BIT MOD L)" (28.15.31.1) -> "GT 1Y 60-63 TO XAB 1-4" (28.15.61.1)      [MOD, XAB]
- "CD 2Y-ZL • 1BIT MOD L" (28.15.61.1) -> "GT 2Y 60-63 TO XAB 1-4" (28.15.61.1)
- "CD 1Y-ZL • 1BIT MOD L" (28.15.31.1) -> "GT 1Y 63 TO XAB 4" (28.15.61.1)
- "CD 2Y-ZL • 1BIT MOD L" (28.15.31.1) -> "GT 2Y 63 to XAB 4" (28.15.61.1)
- "PREP RST X  0-63" (28.86.57.1), on the line labelled "E • ~M"
- "COND MOD ZL TGR TON" (28.15.40.1)
- "ZL  IHW • ~BLOK ~(XF + DEC) • NOT IHW EX" (28.15.50.1); "COND XF + DEC ZL TON CKT" (28. 15.50.1)      [XF]
- "BLOCK YR-ZL M  TGR TOF 28.15.30.1)"
- "COND LOP 4 TON" (28.88.34.1); "COND LOP 5 TON" (28.88.41.1)      [LOP]
- "BE + BEW + BD + SIC - BE - BEW - BD" (28.89.32.1); "BD + SIC - BD" (28.70.84.1)      [SIC]
- "NOT ZL MOD R • FW ~(NOT ST) + ~(PROG IX)" (28.15.32.1)      [MOD, IX]
- "NOT ZL MOD R •  ZL FP CL • NOT IHW EX" (28.15.32.1); "ZL MOD R" (28.15.32.1)
- "INSTR PREP COMP ZL" (28.27.32.1)
- "BLOCK Y - Z START TON" (28.26.11.1); "COND XOF 1 TON" (28.12.11.1)
- "COND INTRPT EN GEN CKTS" (28.70.84.1)
- No printed time or count on this page.

---------------------------------------------------------------------------------------------------------

## FIGURE 3.1.7.  YL-ZR TRANSFER SEQUENCER   (PDF page 69)

- Caption as printed (two lines): "FIGURE 3.1.7.  YL-ZR TRANSFER" / "SEQUENCER"
- Page tag: 1-13/1-14        Date: 2/1/62
- Heading: "I UNIT FLOW DIAGRAMS"      Manual tag: "M3-04-3"
- Applicability note: "CPU 7101 / SER. NO. 30,004 / AND HIGHER"

Read from a 3x5 grid of 240% crops of r-69.png plus 400-500% crops of the multi-line hexagons.
Digit 1 has a flag on this page ("1Y", "1YL", "1BIT" read as digits) except where noted.
In several ALD pairs the separator between two numbers is printed as a small open ring; written `o` here.

### Turn-on conditions

  hex (upper left):  ANTIC YL- / ZR XFER (28.15.10.1)      --YES--\
  hex (upper right): NORMAL YL-ZR / XFER (28.15.10.1)      --YES--/ the two YES lines join (dot) -> line labelled TON ->

  bar: YL-ZR TRANSFER  SEQUENCER (28.15.10.1)        outputs labelled, left to right:  E    E•M    M

### E output
The E line drops from the bar and turns LEFT along a horizontal bus ("bus 1") that ends at the top of the far-left
vertical ("column A"). Column A runs the whole height of the figure; three more horizontal buses (2, 3, 4) leave
it to the right at dots.

  On bus 1:
      dot -> hex: FP CL 2YL • / SBC • CD 2Y-ZR (28.26.54.1)
                --YES--> box: COND ZRFP 1• / 2•3•4•6 SET• / RESET CKTS (28.26.54.1)
      dot -> line down, then right, to box: RESET ZR ADDR / 8 TGR (28.27.57.1)     [uncertain: 8 / B]   (unconditional)

  Column A, top to bottom (boxes on its right, dots):
      box: TON YL-ZR M / TGR (28.15.10.1)
      box: COND ZR IHW / TON CKT (28.26.61.1)
      box: COND ZR FL PT / TGR TON CKT (28.26.62.1)
      box: GENERATE SA / PULSES (24.00.09.1)             [prefix printed 24]
      box: HOLD DATA / SELECT PREP (28.96.43.1)
      dot -> BUS 2 (see below)
      dot -> hex: 1 BIT MOD R • / CD 1 Y-ZR (28.15.11.1)       (no overbar)
                --YES--> joins the vertical described under bus 2 item (a)
      dot -> BUS 3 (see below)
      dot -> hex: 1 BIT MOD R • / CD 2Y - ZR (28.15.11.1)      (no overbar)
                --YES--> joins (dot) the vertical described under bus 3 item (a)
      dot -> hex: CD 1Y-ZR (28.15.10.1)
                --YES--> box: GT 1YL TO ABB / COND TAGS ZR / (28.26.10.1 o 28.27.40.1)
      dot -> BUS 4 (see below)
      bottom end of column A (corner) ->
             hex: FP CL 1 YL • / SBC • CD 1 Y - ZR (28.26.50.1)
                --YES--> vertical with dot:
                    box: COND FP CL / R TON CKT (28.26.51.1)
                    box: COND ZR FP 1 / TON CKTS (28.26.50.1)

  BUS 2 (leaves column A below HOLD DATA SELECT PREP), left to right:
      (a) dot -> hex: ~(1BIT MOD R) • / CD 1Y-ZR • (28.15.11.1)       [bar over "1BIT MOD R"; a • is printed after ZR]
                --YES--> a vertical line on which, in order downward:
                    (dot)  box: GT 1Y 28-30 TO / XAB 1-3 (28.27.52.1)
                    (T-junction, NO dot) the YES line of the column-A hexagon "1 BIT MOD R • CD 1 Y-ZR" comes in
                    (corner, end)  box: GT 1Y31 TO / XAB 4 (28.27.52.1)
                [As drawn the vertical is one unbroken line from the first hexagon's YES, past the first box,
                 to the second box; the print does not separate "which hexagon gates which box". Connection
                 not followed beyond that.]
      (b) dot -> line down, then right, into the top of
            hex M2:   SBC • ~(IMM IX 1YL) +
                      ~(NOT FW NOTS) • 1Y31 + 1Y30
                      + 1Y28 + 1Y29 • DEC MOD
                      REQ FR 1YL • ~(BIT BR DEC 1 +)
                      ~(UNCOND + BIT BR CL 1 YL) +
                      ~(1YLD BRC) (28.26.21.1)
                Overbars as printed (500%): L1 a bar over "IMM IX 1YL"; L2 a bar over "NOT FW NOTS" only (1Y31,
                1Y30 have no bars); L3 no bars (1Y28, 1Y29 unbarred); L4 a bar starting over "BIT" and running
                over "BIT BR DEC 1 +" to the end of the line; L5 a bar over "UNCOND + BIT BR CL 1 YL" (it stops
                before the final "+"); L6 a bar over "1YLD BRC". The L4/L5/L6 bars are probably one overbar
                continued across the line breaks -- cannot be told from the print.
                --YES--\
      (c) dot -> hex M1:  SBC • DEC MOD / REG FR 1YL • BIT BR / DEC 1 • UNCOND + BIT BR / CY 1 YL + YLD BRC •1Y31 / (28.26.21.1)
                (no overbars; second line is printed "REG FR", not "REQ FR")
                --YES--/ YES lines of M1 and M2 join (dot) ->
                    box: TON ZR MOD R / TGR (28.26.21.1)
      (d) right-hand end of bus 2 (corner) ->
            hex: CD 1Y-ZR (28.15.11.1)
                --YES--> vertical: (dot) box: GT 1YL TO ABB (28.27.53.1)
                         then the line turns left along a short horizontal which feeds
                         (dot) hex: ZR IHW BL / IF (28.27.30.1)
                                  --YES--> box: TON ZR BLOCK 1Y / TGR (28.42.41.1)
                         (corner, far end) hex: UNCOND + BIT / BR + IND BR IYL (28.27.31.1)
                                  [last word: first character is a plain stroke, "IYL"; uncertain: IYL / 1YL]
                                  --YES--> box: TON ZR SPND TGR (28.42.43.1)

  BUS 3 (leaves column A below the "GT 1Y31 TO XAB 4" box), left to right:
      (a) hex: ~(1 BIT MOD R •) / CD 2Y-ZR (28.15.10.1)       [bar over "1 BIT MOD R •"; ALD partly under a dark
                scan smear, read 28.15.10.1; uncertain last-but-one group 10 / 11]
                This hexagon sits directly under bus 3 but NO line is drawn from the bus (or from anything else)
                to its top -- its input is not drawn.
                --YES--> vertical: (dot) box: GT 2Y 28-30 TO / XAB 1-3 (28.27.52.1)
                                   (dot) YES line of the column-A hexagon "1 BIT MOD R • CD 2Y - ZR" comes in
                                   (corner, end) box: GT 2Y 31 TO / XAB 4 (28.27.52.1)
                [same single-line drawing as bus 2 item (a); here the lower junction has a dot]
      (b) dot -> a vertical dropping from bus 3 ("column B"); bus 3 itself continues right to (c)
      (c) right-hand end of bus 3 (corner) ->
            hex: CD 2Y-ZR • NOT / FP  CL  2Y • SBC (28.26.58.1)     [ALD partly under the scan smear]
                --YES--> box: TOF FPR CL / 1•2•3•4•6 TGR (28.26.51.1)
      Column B, downward:
          dot -> a horizontal running right ("bus 3b"):
              dot -> hex N1:   ~(2YLD BRC • BIT BR)
                               ~(DEC.3) + ~(UNCOND + BIT BR)
                               ~(CY 2YL) • DEC MOD REQ FR
                               2YL • ~2Y31 + ~2Y30 + ~2Y28 +
                               ~2Y29 • ~(IMM IX 2 YL) + NOT
                               ~(FW NOTS) • SBC
                               (28.26.25.1)
                      Overbars as printed (500%): L1 a bar over the whole line; L2 a bar over "DEC.3" and a
                      separate bar over "UNCOND + BIT BR" (the "+" between them is unbarred); L3 a bar over
                      "CY 2YL"; L4 separate bars over 2Y31, 2Y30, 2Y28; L5 a bar over 2Y29 and a separate bar
                      over "IMM IX 2 YL" ("+ NOT" unbarred); L6 a bar over "FW NOTS". A dot-like mark is printed
                      between "DEC" and "3" on L2.
                      --YES--\
              dot -> a vertical dropping from bus 3b ("column C"); bus 3b continues right (corner) to
                     hex: YL-ZR NM       (no ALD number printed)
                         --right exit, no YES label; the label "E o ~M" (overbar over M) is printed beside the
                           exit line--> box: PREP RST X 0-63 (28.86.57.1)
              column C ends (corner) at
                     hex: FW NOTS  • / SBC (28.15.30.1)
                         --YES--> box: TOF YR-ZLM TGR        (no ALD number printed)
          bottom end of column B (corner) ->
              hex N2:  2Y31 • DEC MOD REQ / FR 2YL • 2YLD BRC + BIT / BR DEC 3 • UNCOND + BIT / BR CL 2YL • SBC / (28.26.25.1)
                      (no overbars)
                      --YES--/ YES lines of N1 and N2 join (dot) ->
                         box: SET MOD R TGR (28.26.21.1)

  BUS 4 (leaves column A below the "GT 1YL TO ABB COND TAGS ZR" box), left to right:
      dot -> hex: CD 2Y-ZR (28.15.11.1)
                --YES--> box: GT 2YL  TO ABB / COND TAGS ZR / (28.26.10.1) (28.26.40.1)
                         [two separately parenthesised ALD numbers; a scan fold line runs through "COND TAGS ZR"]
      dot -> a vertical dropping from bus 4 ("column D")
      dot -> hex: NOT FP CL 1 Y • / CD 1 Y -ZR • SBC (28.26.58.1)
                --YES--> box: TOF FPR CL / 1•2•3•4•6 TGR (28.26.51.1)      [fold line through the ALD; uncertain: 51]
      dot -> a vertical dropping from bus 4 ("column E")
      right-hand end of bus 4 (corner) ->
            hex: FP MOD RDY (28.15.40.1)
                --YES--> box: TOF MOD ZL M TGR (28.15.40.1)       [fold line through the ALD; uncertain: 15.40]
      Column D, downward:
          dot -> hex: SBC (28.26.11.1)
                    --YES--> box: TOF Y-Z START TGR (28.26.11.1)
          end (corner) -> hex: CD 1Y-ZR3 (28.26.11.1)
                    [text as printed: a stray tick, then "CD 1Y-ZR3"; uncertain what the trailing "3" is]
                    --YES--> vertical: (dot) box: GT 1 YL TO ABB (28.27.53.1)
                             then left along a horizontal feeding
                             (dot) hex: UNCOND + BIT / BRC + IND BR 2YL (28.27.31.1)
                                      --YES--> box: BR Y-Z XFER TON / ZR SPND 1Y (28.42.42.1)
                             (corner, far end) hex: ZR IHW / BL  IF (28.27.30.1)
                                      --YES--> box: TON ZR BLOCK / 2Y TGR (28.42.41.1)
      Column E, downward (boxes on its right, dots; unconditional):
          box: TOF FPL 3M TGR (28.13.31.1)
          box: TOF FPL 4M TGR (28.13.41.1)
          box: TOF VFL 5M TGR (28.11.51.1)
          box: INH NIDC SET / IX FR XAC          (no ALD number printed; no overbars in this box)
          box: TOF ZR ICC TGR (28.51.02.1)
          box: COND ZRAD TON • / TOF CKTS (28.51.04.1)
          box: COND ZRIF TON • / TOF CKTS (28.51.05.1)
          box: TOF ZDS • ZDF TGRS (28.51.06.1)        (column E ends here)

### E•M output (vertical line down from the bar)
          dot -> box: GT AOB TO ZR / (28.15.21.1 o 28.27.57.1)
          end -> box: GT AOB 32 to ZR (28.27.51.1)

### M output (vertical line down from the bar), in order downward
          dot -> hex: NOT ZR MOD (28.15.12.1         (closing parenthesis not printed)
                    --YES--> box: COND YR-ZL TON CKT (28.15.30.1)
          dot -> box: COND IHW RDY ZR / TGR TON CKT (28.26.11.1)
          dot -> box: COND IHW EX ZR / TGR TON CKT (28.26.11.1)
          dot -> hex: ZR FP CL • / NOT ZR MOD (28.15.12.1)
                    --YES--> dot, from which two hexagons are fed:
                        hex: FP Z ALT / TGR OFF (28.27.32.1)
                            --YES--> box: FP RDY ZR • FP / RDY ZR IC / (28.20.21.1 o 28.44.28.1)
                        hex: FP Z ALT TGR OFF • / FP CL 2 ZR (28.27.32.1)
                            --YES--> box: COND INSTR CHK / ENSLD CKT (28.41.50.1)
          dot -> box: COND MOD ZR TON / CKT (28.15.20.1)
          dot -> hex: NOT ZR MOD (28.27.32.1)
                    --YES--> box: PREV ZR PREP / COMPL (28.44.25.1)
          dot -> hex: ZR MOD T (28.15.12.1)
                    --YES--> vertical with dot:
                        box: BLOCK Y-Z START / TGR TON (28.26.11.1)
                        box: ZL + ZR PREP NOT / BUSY (28.20.21.1)
          dot -> hex: ~(ZR WAS IHW) (28.15.71.1)        [bar over "ZR WAS IHW"]
                    --YES--> box: Y-Z M • MOD / REQ (28.70.42.1)
          bottom end of the M line (corner) -> box: TOF YL-ZR E TGR (28.15.10.1)

### Noted (Fig 3.1.7)
- "~(1BIT MOD R) • CD 1Y-ZR •" (28.15.11.1); "GT 1Y 28-30 TO XAB 1-3" (28.27.52.1)      [MOD, XAB]
- "1 BIT MOD R • CD 1 Y-ZR" (28.15.11.1); "GT 1Y31 TO XAB 4" (28.27.52.1)
- "~(1 BIT MOD R •) CD 2Y-ZR" (28.15.10.1); "GT 2Y 28-30 TO XAB 1-3" (28.27.52.1)
- "1 BIT MOD R • CD 2Y - ZR" (28.15.11.1); "GT 2Y 31 TO XAB 4" (28.27.52.1)
- "SBC • DEC MOD REG FR 1YL • BIT BR DEC 1 • UNCOND + BIT BR CY 1 YL + YLD BRC •1Y31" (28.26.21.1)      [MOD, BR]
- "SBC • ~(IMM IX 1YL) + ~(NOT FW NOTS) • 1Y31 + 1Y30 + 1Y28 + 1Y29 • DEC MOD REQ FR 1YL • ~(BIT BR DEC 1 +) ~(UNCOND + BIT BR CL 1 YL) + ~(1YLD BRC)" (28.26.21.1)      [IX, MOD, BR]
- "TON ZR MOD R TGR" (28.26.21.1)
- "~(2YLD BRC • BIT BR) ~(DEC.3) + ~(UNCOND + BIT BR) ~(CY 2YL) • DEC MOD REQ FR 2YL • ~2Y31 + ~2Y30 + ~2Y28 + ~2Y29 • ~(IMM IX 2 YL) + NOT ~(FW NOTS) • SBC" (28.26.25.1)      [IX, MOD, BR]
- "2Y31 • DEC MOD REQ FR 2YL • 2YLD BRC + BIT BR DEC 3 • UNCOND + BIT BR CL 2YL • SBC" (28.26.25.1)
- "SET MOD R TGR" (28.26.21.1)
- "UNCOND + BIT BR + IND BR IYL" (28.27.31.1) -> "TON ZR SPND TGR" (28.42.43.1)      [BR, IND, SUSPEND]
- "ZR IHW BL IF" (28.27.30.1) -> "TON ZR BLOCK 1Y TGR" (28.42.41.1)      [BLOCK ZR]
- "UNCOND + BIT BRC + IND BR 2YL" (28.27.31.1) -> "BR Y-Z XFER TON ZR SPND 1Y" (28.42.42.1)
- "ZR IHW BL  IF" (28.27.30.1) -> "TON ZR BLOCK 2Y TGR" (28.42.41.1)
- "YL-ZR NM" (no ALD), exit labelled "E o ~M" -> "PREP RST X 0-63" (28.86.57.1)
- "INH NIDC SET IX FR XAC" (no ALD printed)      [IX, XAC]
- "RESET ZR ADDR 8 TGR" (28.27.57.1)
- "GENERATE SA PULSES" (24.00.09.1)
- "NOT ZR MOD" (28.15.12.1; "ZR FP CL • NOT ZR MOD" (28.15.12.1); "COND MOD ZR TON CKT" (28.15.20.1); "NOT ZR MOD" (28.27.32.1); "ZR MOD T" (28.15.12.1)
- "FP MOD RDY" (28.15.40.1); "TOF MOD ZL M TGR" (28.15.40.1)
- "BLOCK Y-Z START TGR TON" (28.26.11.1); "ZL + ZR PREP NOT BUSY" (28.20.21.1)
- "~(ZR WAS IHW)" (28.15.71.1) -> "Y-Z M • MOD REQ" (28.70.42.1)
- "PREV ZR PREP COMPL" (28.44.25.1); "FP RDY ZR • FP RDY ZR IC" (28.20.21.1 o 28.44.28.1); "COND INSTR CHK ENSLD CKT" (28.41.50.1)
- No printed time or count on this page.

---------------------------------------------------------------------------------------------------------

## FIGURE 3.1.8.  YL-ZL TRANSFER SEQUENCER   (PDF page 70)

- Caption as printed (two lines): "FIGURE 3.1.8.  YL-ZL TRANSFER" / "SEQUENCER"
- Page tag: 1-15/1-16        Date: 2/1/62
- Heading: "I UNIT FLOW DIAGRAMS"      Manual tag: "M3-04-3"
- Applicability note: "CPU 7101 / SER. NO. 30,004 / AND HIGHER"
- Note: the caption says "YL-ZL TRANSFER SEQUENCER"; the bar inside the figure is lettered "YL - ZL SEQUENCER".

Read from a 3x4 grid of 240% crops of r-70.png plus 500% crops of the doubtful boxes. The right-hand column
of this page is faintly printed. On this page the "1Y" names are printed with a plain stroke ("IY"); I write
"IY" as printed [uncertain throughout: IY / 1Y]. No overbars were found on this page except over ZR WAS IHW.

### Turn-on conditions

  hex (upper left):  FULL WRD S • ACC + / COMP • ZL MT ON ACC • / YR - ZR • NOT MOD R + / MOD Z R M • SAC / (28.15.70.1)     --YES--\
  hex (upper right): FULL WD S • SAC • / YR - ZR • NOT MOD / R + MOD ZR M • ZL / MT / (28.15.70.1)                              --YES--/
      the two YES lines join (dot) -> line labelled TON ->

  bar: YL - ZL SEQUENCER (28.15.70.1)        outputs labelled, left to right:  E    E•M    M

### E output
The E line drops from the bar and turns LEFT along a horizontal. The horizontal meets the top of a vertical
("column B") at a T-junction with no dot, and ends (corner) at the top of the far-left vertical ("column A").

  Column A, downward:
      dot -> box on the LEFT (margin):  RESET ZL / ADDR 8 TGR (28.27.57.1)      [uncertain: 8 / B]
             box on the right:          TON YL - ZL M / TGR (28.15.70.1)
      dot -> hex: CD IY - ZL (28.15.71.1)
                --YES--> vertical with dots:
                    box: TON CD 2Y - ZR / TGR (28.26.10.1)
                    box: GT IY 31 TO / XAB 4 (28.27.52.1)
                    box: GT IY 28 - 30 / TO XAB 1 -3 (28.27.52.1)
                    box: INST PREP TON / ZL BLOCK IY (28.43.41.1)     [second group read "43" at 500%; heavy, slightly
                                                                         smeared print; uncertain: 43 / 42]
                    box: IY - ZL E (28.44.24.1)                        (line ends here)
      dot -> box on the LEFT (margin):  TOF ZLNA / ZLXA  ZL / SA TGRS (28.51.08.1)
      bottom end of column A (corner) ->
             hex: CD 2Y - ZL (28.15.71.1)
                --YES--> vertical with dots:
                    box: GT 2Y 31 TO / XAB 4 (28.27.52.1)
                    box: GT 2Y 28 - 30 / TO XAB 1 - 3 (28.27.52.1)
                    box: TOF CD 2Y - ZR TGR (28.26.10.1)
                    box: INST PREP TON / ZL BLOCK 2Y (28.42.41.1)
                    box: 2Y - ZL (28.44.24.1)
                    box: GT 2Y 0 - 17 TO ABB (22.10.11.1)             [fold line through the ALD]
                    box: GT 2Y 18 TO / ABB (22.10.11.1)
                    box: GT 2Y 19 - 23 / TO ABB (22.10.11.1)
                    box: GT 2Y 28 - 31 / TO ABB (22.10.11.1)          (printed in this order: 28-31 before 24-27)
                    box: GT 2Y 24 - 27 / TO ABB (22.10.11.1)
                    box: NO ADJ P 24-27 / BYDS SIGN RES (28.96.44.1)  ["BYDS" as printed here; the matching box
                                                                         under CD IY - ZL prints "BYPS"]   (line ends here)

  Column B, downward (boxes on its right, dots; unconditional):
      box: COND MOD ZR / M TOF / (28.15.20.1)          [opening parenthesis printed as a small tick]
      box: HOLD DATA / SELECT PREP (28.96.43.1)
      box: XS READ P (24.00.09.1)                       [prefix printed 24]
      bottom end of column B (corner) ->
             hex: CD IY - ZL (28.15.71.1)
                --YES--> vertical with dots:
                    box: GT IY 0 - 17 / TO ABB / (22.10.09.1)        [lines 2 and 3 are printed on top of each other]
                    box: GT IY 18 TO ABB (22.10.09.1)
                    box: GT IY 19 - 23 / TO ABB (22.10.09.1)
                    box: GT IY 24 - 27 / TO ABB (22.10.09.1)
                    box: GT IY 28 - 31 / TO ABB (22.10.09.1)
                    box: NO ADJ P 24 - 27 / BYPS SIGN RES (28.96.44.1)       (line ends here)

### E•M output (long vertical straight down from the bar; boxes on its right, dots; unconditional unless a hexagon is listed)
      box: GT AOB TO / ZL YL (28.27.57.1)
      box: GT AOB 32 TO ZL (28.27.50.1)
      box: GT AOB TO ZL LI (28.15.41.1)                 [last word faint; read "LI"; uncertain: LI / L1 / LH]
      box: COND ZL IDC / TON TO F  CKTS (28.51.03.1)    [second line as printed, with a gap after F; probably a
                                                          damaged "TON • TOF CKTS" -- uncertain]
      box: COND ZLAD TON / • TOF CCTS (28.15.04.1)      ["CCTS" and "28.15.04.1" as printed (read at 500%); the
                                                          neighbouring boxes use 28.51.0x.1 -- uncertain 15 / 51]
      box: COND ZL IF / TON • TOF CKTS (28.51.05.1)
      box: COND ZDS • ZDF / TOF CKTS (28.51.06.1)       [faint]
      box: TOF BROK TGR (28.71.40.1)                    [faint]
      box: BLOCK GEN OF INH / NIDC SET IDC FR XAC (28.27.31.1)
      box: Y-ZL + MOD ZR / RST ZL TAGS (28.51.06.1)     [the "+" is nearly gone; uncertain: + ]
      box: TOF VFL 5 M (28.11.51.1)
      box: TOF FPL 4  M (28.13.41.1)
      box: TOF FPL 3 M (28.13.31.1)
      dot -> hex: SAC o 2YL MOD DEC (28.26.27.1)        [a scan fold line runs through the text line; the separator
                                                          after SAC prints as a small ring; uncertain: "2YL"]
                --YES--> vertical with dots:
                    box: SET MOD L TGR (28.26.23.1)
                    box: COND ZL MOD / R TGR (28.26.23.1)
                    box: TON YR - ZR / M TGR (28.15.60.1)
                    (dot: the exit line of the SBC hexagon below comes in here)
                    box: TOF FPL CL / 1• 2•3•4•6 (28.26.52.1)        (line ends here)
      bottom end of the E•M line (corner) ->
             hex: SBC (28.26.58.1)
                --right exit, no YES label--> joins (dot) the YES vertical of the SAC hexagon, between
                  "TON YR - ZR M TGR" and "TOF FPL CL 1•2•3•4•6"
                [As drawn the SAC-hexagon YES line and the SBC-hexagon exit are one net; presumably SBC gates only
                 TOF FPL CL, but the print does not show that. Connection not followed beyond what is drawn.]

### M output (the M line leaves the bar, runs right, then down)
      dot -> box: TOF YL - ZL / E TGR (28.15.70.1)
      dot -> box: COND MOD ZL / TON CKT (28.15.40.1)
      dot -> hex: NOT MOD L RQ (28.15.71.1)
                --YES--> box: COND  WBC + / DEC TON (28.15.80.1)
      bottom end of the M line (corner) ->
             hex: ZL MOD R (28.15.71.1)
                --YES--> vertical: (dot) box: BLOCK GEN OF ZL + ZR / PREP NOT BUSY (28.20.21.1)
                         the same line continues down into the top of
                         hex: ~(ZR WAS IHW) (28.15.71.1)       [faint; a bar is visible over "ZR WAS IHW";
                                                                 ALD read 28.15.71.1, uncertain]
                             --YES--> box: BLOCK XSF[illegible] / E TON / (28.70.42.1)
                                      [very faint, read with gamma-darkened 500% crop: first line "BLOCK XSF" plus
                                       one or two unreadable characters; ALD third group uncertain: 42 / 47?]

### Noted (Fig 3.1.8)
- "FULL WRD S • ACC + COMP • ZL MT ON ACC • YR - ZR • NOT MOD R + MOD Z R M • SAC" (28.15.70.1)      [MOD, COMP]
- "FULL WD S • SAC • YR - ZR • NOT MOD R + MOD ZR M • ZL MT" (28.15.70.1)
- "RESET ZL ADDR 8 TGR" (28.27.57.1)
- "COND MOD ZR M TOF" (28.15.20.1)
- "XS READ P" (24.00.09.1)
- "GT IY 31 TO XAB 4" (28.27.52.1); "GT IY 28 - 30 TO XAB 1 -3" (28.27.52.1); "GT 2Y 31 TO XAB 4" (28.27.52.1); "GT 2Y 28 - 30 TO XAB 1 - 3" (28.27.52.1)      [XAB]
- "INST PREP TON ZL BLOCK IY" (28.43.41.1); "INST PREP TON ZL BLOCK 2Y" (28.42.41.1)      [BLOCK ZL]
- "COND ZL IDC TON TO F  CKTS" (28.51.03.1)
- "BLOCK GEN OF INH NIDC SET IDC FR XAC" (28.27.31.1)      [XAC]
- "Y-ZL + MOD ZR RST ZL TAGS" (28.51.06.1)
- "TOF BROK TGR" (28.71.40.1)
- "SAC o 2YL MOD DEC" (28.26.27.1); "SET MOD L TGR" (28.26.23.1); "COND ZL MOD R TGR" (28.26.23.1)
- "COND MOD ZL TON CKT" (28.15.40.1); "NOT MOD L RQ" (28.15.71.1); "ZL MOD R" (28.15.71.1)
- "BLOCK GEN OF ZL + ZR PREP NOT BUSY" (28.20.21.1)
- "~(ZR WAS IHW)" (28.15.71.1) -> "BLOCK XSF[illegible] E TON" (28.70.42.1)
- "NO ADJ P 24 - 27 BYPS SIGN RES" (28.96.44.1); "NO ADJ P 24-27 BYDS SIGN RES" (28.96.44.1)
- No printed time or count on this page.


---------------------------------------------------------------------------------------------------------

## FIGURE 3.1.9.  YR-ZR TRANSFER SEQUENCER   (PDF page 71)

- Caption as printed (two lines): "FIGURE 3.1.9.  YR-ZR TRANSFER" / "SEQUENCER"
- Page tag: 1-17/1-18        Date: 2/1/62
- Heading: "I UNIT FLOW DIAGRAMS"      Manual tag: "M3-04-3"
- Applicability note: "CPU 7101 / SER. NO. 30,004 / AND HIGHER"
- The bar inside the figure is lettered "YR - ZR SEQUENCER".

Read from a 3x5 grid of 240% crops of r-71.png (zoom-b-71-g00..g42). On this page "1Y" is printed with a
plain stroke in some boxes ("IY") and as "1Y" in others; I write each as printed [uncertain throughout: IY / 1Y].

### Turn-on conditions

  hex 1: SAC • ~(FW NOT S) • ~(CD Y / RIGHT) • ~(ZL IHW) • INS / WRD CHK COMP • FWS • / FP BLOK Y-Z • ACC + /
         COMP • ZR MT ON ACC • / MOD ZL M + YR - ZL • / NOT R MOD • NOT CHKR / SING ERR (28.15.60.1)
         [bars: over FW NOT S; over "CD Y" continuing over "RIGHT" on the next line; over ZL IHW.]      --YES--\
  hex 2: ~(FW NOT S) • SAC • NOT / CHKR SING ERR • ~(CDY / RIGHT) • ~(ZL IHW) • INSTR / ~(WRD CHK COMP) • FWS • /
         ~(FP BLOCK Y-Z) • MOD / ZL M + YR - ZL NOT R / MOD - ZR MT (28.15.60.1)
         [bars: over FW NOT S; over "CDY" into "RIGHT"; over ZL IHW; over WRD CHK COMP (this may be the
          continuation of a bar from the line above) [uncertain]; over FP BLOCK Y-Z.]                       --YES--/
      the two YES lines meet (dot) -> line labelled TON ->

  bar: YR - ZR SEQUENCER (28.15.60.1)        outputs labelled, left to right:  E    E•M    M

### E output
The E line drops from the bar and runs left along a horizontal. That horizontal meets the top of a vertical
("column B") at a dot and ends at the top of the far-left vertical ("column A").

  Column A, downward:
      dot -> box on the LEFT (margin):  RESET ZR / ADDR 8 TGR (28.27.57.1)      [uncertain: 8 / B]
             box on the right:          TON YR - ZR / M TGR (28.15.60.1)
      dot -> hex: SBC • 2YR / MOD DEC (28.26.25.1)      --YES--\
      dot -> hex: 2YR IB MOD / D • SBC (28.26.25.1)     --YES--/  [as printed: "IB"]
                the two YES lines join -> box: SET MOD R TGR (28.26.21.1)
      dot -> box: COND ZR MOD / R TGR (28.26.21.1)
      dot -> hex: 1YR 4 BIT I FLD / + 1Y63 ZERO • / CD 1Y-ZR (28.15.61.1)
                --YES--> vertical:
                    (dot) box: GT IY 60 - 62 / TO XAB 1 - 3 (28.27.52.1)
                    (dot) the YES line of the next hex joins here:
                          hex: CD IY - ZR (28.15.61.1), fed from the next column-A dot
                    line ends at box: GT IY 63 TO / XAB 4 (28.27.52.1.)     [the trailing dot is printed]
      dot -> hex: CD 2Y - ZR • / 2YR 4 BIT I / FLD + 2Y63 ZERO (28.15.61.1)
                --YES--> vertical:
                    (dot) box: GT 2Y 60-62 / TO XAB 1 - 3 (28.27.52.1)
                    line ends at box: GT 2Y 63 TO / XAB 4 (28.27.52.1)
      dot -> hex: FULL WRD IY (28.26.60.1)      --YES--\
      dot -> hex: FULL WRD 2Y (28.26.60.1)      --YES--/ (dot) the two YES lines join and end at
                box: TON FULL WDS TGR (28.26.60.1)
      the bottom of column A turns right (corner) into a horizontal bus ("bottom bus", below).

  Column B, downward (boxes on its right; each one a dot on the vertical unless a hexagon is listed):
      box: COND ZRIDC / TON o TOF CRT (28.51.02.1)      [as printed: "CRT"; the "o" is a small circle]
      box: COND ZRAD / TON o TOF CKT (28.51.04.1)
      box: COND ZRIF TON • / TOF CKT (28.51.05.1)
      box: COND ZDS • ZDF / TOF CKT (28.51.06.1)
      box: TOF BROK TGR (28.71.40.1)
      dot -> hex: CD 1Y-ZR (28.15.61.1)
                --YES--> vertical with dots:
                    box: TOF CD 2Y-ZL / TGR (28.26.10.1)
                    box (on the right): 1Y - ZR (28.44.24.1)
                    box: GT 1YR TO ABB (28.27.55.1)
                    line ends at box: COND BR TGR (28.27.31.1)
      the bottom of column B turns right (corner) into a horizontal, which feeds three hexagons by dots:
          hex: CD 2Y - ZR (28.15.61.1)
                --YES--> vertical with dots:
                    box: NO ADJ P 24 - 27 / BYPS SIGN RES (28.96.44.1)
                    box: GT 2YR TO ABB          [no ALD number printed]
                    box: COND BR TGR (28.27.31.1)
                    box: TOF 2Y - ZR TGR (28.26.10.1)
                    line ends at box: 2Y - ZR (28.27.40.1)
          hex: CD 2Y - ZR (28.15.51.1 )            [as printed: "51", with a space before ")"; the hexagon to
                                                    its left reads 28.15.61.1]
                --YES--> vertical with dots:
                    box: GT 2Y 63 TO / XAB 4 (28.27.52.1)
                    box: HOLD DATA PREP (28.96.43.1)
                    box: TOF FW WBC TGR (28.22.92.1)
                    box: TOF Y-Z START / TGR (28.26.11.1)
                    line ends at box: XS READ P (24.00.09.1)
          (end of the horizontal, corner) hex: YR-ZR NM          [no ALD number printed]
                --YES--, the exit line labelled "E • ~M" --> box: PREP RST / X 0 - 63 (28.86.57.1)

  Bottom bus (from the bottom of column A), left to right:
      dot -> hex: SBC (28.26.58.1)
                --YES--> vertical:
                    (dot) box: TOF FPR - CLI TGR (28.26.50.1)
                    line ends at box: TOF FPR CL 2•3•4•6 / TGRS / * (28.26.51.1)
                    [an asterisk is printed at the lower left of this box; no footnote for it was found on the page]
      dot -> vertical with dots (boxes on the right):
                box: Y-ZR + MOD ZR / RST ZR TAGS (28.51.07.1)
                box: TOF MOD ZL M (28.15.40.1)
                box: BLOCK GEN OF INH / NIDS SET IDC FR XAC (28.27.31.1)
                box: TOF VFL 5 M (28.11.51.1)
                box: TOF FPR 4 M (28.14.41.1)
                line ends at box: TOF FPR 3 M (28.14.31.1)

### E•M output (vertical down from the bar; all boxes on dots)
      box: GT AOB TO ZR YR (28.27.57.1)
      box: GT AOB 32 to ZR (28.27.51.1)        [lower-case "to" as printed in these three boxes]
      box: GT AOB 18 to ZR (28.27.51.1)
      line ends at box: GT AOB 19 to ZR (28.27.51.1)

### M output
      dot -> box: TOF YR - ZR / M TGR (28.15.60.1)
      dot -> box: COND MOD / ZR TO N CKT (28.15.20.1)      [as printed: "TO N"]
      dot -> hex: NOT ZR MOD F (28.15.61.1)
                --YES--> box: COND YL - ZL / TON CKT (28.15.70.1)
      bottom end of the M line (corner) ->
             hex: ZR MOD R (28.15.61.1)
                --YES--> vertical: (dot) box: BLOCK GEN OF ZL / + ZR PREP NOT / BUSY (28.15.61.1)
                         the same line continues down into
                hex: ZP WAS IHW (28.15.71.1)      [as printed: "ZP"; no overbar visible (compare Fig 3.1.8,
                                                   which has ~(ZR WAS IHW)); uncertain]
                    --YES--> box: BLOCK YSFI / E TON (28.70.42.1)

### Noted (Fig 3.1.9)
- "... • NOT R MOD • NOT CHKR SING ERR" and "... MOD ZL M + YR - ZL NOT R MOD - ZR MT" (both 28.15.60.1)      [MOD, CHKR]
- "FP BLOK Y-Z" (hex 1) and "~(FP BLOCK Y-Z)" (hex 2), both 28.15.60.1      [BLOK / BLOCK spelt both ways]
- "SBC • 2YR MOD DEC" (28.26.25.1); "2YR IB MOD D • SBC" (28.26.25.1); "SET MOD R TGR" (28.26.21.1);
  "COND ZR MOD R TGR" (28.26.21.1)      [MOD]
- "GT IY 60 - 62 TO XAB 1 - 3"; "GT IY 63 TO XAB 4"; "GT 2Y 60-62 TO XAB 1 - 3"; "GT 2Y 63 TO XAB 4" (all 28.27.52.1)      [XAB]
- "COND BR TGR" (28.27.31.1), twice      [BR]
- "TOF BROK TGR" (28.71.40.1)
- "GT 1YR TO ABB" (28.27.55.1); "GT 2YR TO ABB" (no ALD)
- "COND ZRIDC TON o TOF CRT" (28.51.02.1)
- "BLOCK GEN OF INH NIDS SET IDC FR XAC" (28.27.31.1)      [BLOCK, XAC]
- "Y-ZR + MOD ZR RST ZR TAGS" (28.51.07.1); "TOF MOD ZL M" (28.15.40.1)      [MOD]
- "YR-ZR NM" exit labelled "E • ~M" -> "PREP RST X 0 - 63" (28.86.57.1)
- "COND MOD ZR TO N CKT" (28.15.20.1); "NOT ZR MOD F" (28.15.61.1); "ZR MOD R" (28.15.61.1)      [MOD]
- "BLOCK GEN OF ZL + ZR PREP NOT BUSY" (28.15.61.1)      [BLOCK; Fig 3.1.8's box of the same name reads 28.20.21.1]
- "ZP WAS IHW" (28.15.71.1) -> "BLOCK YSFI E TON" (28.70.42.1)      [BLOCK]
- "HOLD DATA PREP" (28.96.43.1); "XS READ P" (24.00.09.1)
- No printed time or count on this page.

---------------------------------------------------------------------------------------------------------

## Not read with confidence (all of part b)

p72, Fig 3.1.10:
- Turn-on hex T1: whether the overbars carry on across the line breaks, i.e. how far each ~( ) reaches.
- "ADDR 8" vs "ADDR B" in the RESET ... ADDR 8 TGR box.
- The ALD 28.15.81.1, which the fold line runs through.
- Whether YL FP gates the second "GT AOB 18" box.
- Where the YES line of "ZR IHW TGR ON" ends.
- The exits of "ZR WAS IHW" and "SBC", which are drawn but have no YES label.

p73, Fig 3.1.11:
- IY vs 1Y; YFER vs XFER; IWCI vs IWC1; ICOA (O vs 0); ICFO1Y; IF1Y; IL vs IC; F02Y.
- The ALD "28.41 21.1", printed with a space where a dot belongs; and 28.42.32.1.

p68, Fig 3.1.6:
- The extent of the overbars on R2 FPR and BLOCK Y.
- "1P C"; FPI; the ALD 28.36.51.1.
- Hex "CD 2Y-ZL", which has no bar, and its ALD 28.15.61.1.
- BE vs BL.
- How far the bar over the "NOT ZL MOD" hexagon reaches.
- The bar over ZL IHW BLOK.
- An empty box.
- ADDR 8 vs B.

p69, Fig 3.1.7:
- The input to "~(1 BIT MOD R •) CD 2Y-ZR" is not drawn (connection not followed), and its ALD sits in a smear.
- IYL vs 1YL; "1Y-ZR3"; REG vs REQ.
- Whether the overbars continue across line breaks.
- The fold line runs through 28.26.51.1 and 28.15.40.1.
- The shared verticals in bus 2/3, item (a).

p70, Fig 3.1.8:
- IY vs 1Y throughout.
- The ALD 28.43.41.1 (43 or 42).
- "TON TO F".
- 28.15.04.1 and "CCTS".
- "LI".
- The "+" in "Y-ZL + MOD ZR".
- "2YL" in the SAC hexagon.
- Whether the SBC exit joins the SAC net.
- The faint "~(ZR WAS IHW)" and its ALD.
- "BLOCK XSF[illegible]", whose ALD is 28.70.42.1 or 28.70.47.1.

p71, Fig 3.1.9:
- "ZP WAS IHW": the ZP spelling, and whether it has an overbar.
- "TO N" in COND MOD ZR TO N CKT.
- "CRT" in COND ZRIDC.
- "2YR IB MOD D".
- The ALD 28.15.51.1 on the second CD 2Y - ZR hexagon.
- In hex 2, whether the bar over WRD CHK COMP continues the bar from the line above.
- IY vs 1Y.
- ADDR 8 vs B.
- The asterisk in TOF FPR CL 2•3•4•6 TGRS has no footnote that I could find.
- "BLOCK YSFI" (YSFI vs XSFI, compared with Fig 3.1.8).

# APPENDIX C -- reader transcription

# part_c: PDF pages 74-79 (Figs 3.1.12 - 3.1.15)

Conventions: `~X` = overbar on X; `•` = AND-dot; `+` as printed. "(no ALD)" = no number printed in the box.
"YES" is written only where the word is printed at the hexagon exit. Line-by-line breaks inside a box are
shown with ` / ` where the break could matter.
General 1/I caveat: this typeface prints digit 1 and letter I almost identically ("XOF1"/"XOFI", "FP1"/"FPI",
"T1"/"TI"); I write what the glyph most resembles and do not claim to distinguish them.

---------------------------------------------------------------------------------------------------
## FIGURE 3.1.12. ZR FP 1 TRIGGER
PDF page 74 (landscape; tiles f74-L/M/R). Page head: "M3-04-3   I UNIT FLOW DIAGRAMS".
Printed page tag: "1-23/1-24". Printed date: "[uncertain: 2?]/1/62" (first digit partly hidden by a scan line).
Applicability note: "CPU 7101 / SER. NO. 30,004 / AND HIGHER".

### Top group (above the trigger)
Two hexagons whose YES exits join one horizontal line:
- hex `FP CL IYL • / CD IY-ZR • FWS / + HW (28.26.62.1)` --YES-->
- hex `FWS + HW • / CD 2Y-ZR • / FP CL 2YL (28.26.62.1)` --YES-->
  (both YES lines drop to one horizontal line; from that line, by dots, hang the three hexagons below)
  - hex `YL-ZR E` (no ALD) --YES--> (line label, not boxed: `TON ZR / FL PT / TGR`)
      -> box/bar `Z RIGHT FLOATING POINT / TGR (28.26.62.1)`
      -> (same line continues down to) box `BLOCK FP Z / ALT TGR TON (28.27.32.1)`
  - hex `MOD ZR E (28.15.21.1)` --YES-->
      - box `Z 32-49 to ABB / 0-17 PREP (28.96.09.1)`   ("to" is printed lower-case)
      - box `HOT 1 TO ABB P2 (28.96.41.1)`
  - hex `MOD ZR E • / MOD ZR M (28.15.21.1)` --YES-->
      - box `GT AOB 18 / TO ZR (28.27.51.1)`

### Turn-on conditions of ZR FP1 TGR
- hex `SET ZR FP1 (28.26.54.1)` --YES-->  (joins at a dot above the trigger box)
- hex (large, 10 text lines; YES exit on its LEFT side), text line by line:
    `FP CL 1Y•SBC•`
    `CD 1Y ZR•YL`
    `ZRE•~1Y21•1Y23•`
    `1Y25+~1Y25•~1Y21•`
    `~1Y24+~1Y21•1Y23•`
    `1Y25 + 1Y22•1Y23•`
    `1Y25 + MULT AND`
    `ADD + ~1Y24•~1Y23`
    `+ 1Y21•~1Y22•1Y24•`
    `~1Y25`
    `(28.26.50.1)`
  --YES-->
  (Overbars as I see them: line 3 over the first "1Y21" only; line 4 over the second "1Y25" and over "1Y21";
   line 5 over "1Y24" and over "1Y21"; line 8 over "1Y24" and over "1Y23"; line 9 over "1Y22"; line 10 over "1Y25".
   Several of the `+` signs print as a blurred "+"/"÷"/"-"; all taken as `+`.)

=> box (the trigger) `ZR FPI TGR (28.26.50.1)`

### Outputs of ZR FP1 TGR (one horizontal bus under the trigger; branches listed left to right)

A. Leftmost vertical line (runs down the left of the page; items hang off it by dots):
  - box `BLOCK WBC + / DEC TON (28.15.80.1)`  (direct, no hexagon)
  - hex `SAC • ZRXS • ZR / INSTR PREP COMP • / ZR + ZL PREP NOT / BUSY • XOFI NM (28.12.11.1)` --YES-->
      - box `TON XOFI (28.12.11.1)`
  - hex `ZR EQ 1 • ZR / INSTR PREP COMP / XOF1 E (28.12.11.1)` --YES-->
      (no `•` is printed between "COMP" and "XOF1 E")
      - box `XOFI TC FTH (24.00.09.1)`
  - hex `ZR 1 + 2 + 3 • / IRPT ENBLD (28.23.70.1)` --YES-->
      - hex `~(FPR AD INHBT DF) / • DS • ~(IF INHBT / DF) • GT FPR IND / TO LA (28.25.30.1)` --YES-->
          (overbars: over the whole of "FPR AD INHBT DF"; over "IF INHBT" and over the "DF" that starts the next line)
          - box `SET LA DF (33.01.02.1)`
          - hex `DF MASK EQI • / INH SET NOP BIT / 17 FR DF (28.25.30.1)` --YES-->
              - box `DF SET LANOP (28.25.40.1)`
  - hex `ZR INSTR / PEP COMPLETE• / ZR NOT EQ 1• / XOF 1E` (no ALD; "PEP" is as printed) --YES-->
      - box `XOF 1 Z45-49 / •P TO XAB (28.86.56.1)`

B. Next vertical (dot on bus), runs down then right to:
  - hex `SAC • XOF 1M • / LA EN TI +2 • / CHKR EN TI • / NOT CHKR SING ERR• / ZR INSTR PREP COMP / 28.14.41.1` --YES-->
      (the ALD number is printed without parentheses in this hexagon)
      - box `TON FPR 4 (28.14.41.1)`

C. Next (dot on bus):
  - hex `~(FPR AD INHBT DF) • / DS • IRPT ENBLD / • NOT ZR 16-31 • / NOT ZR 0-15 (28.23.61.1)` --YES-->
      (overbar over "FPR AD INHBT DF" only)
      - box `PRE CND LA DF (28.14.33.1)`
      - hex `MDF EQ 1 (28.23.61.1)` --YES-->
          - box `PRE CND LANOP / FR ALARM (28.14.33.1)`

D. Next vertical (dot on bus, just right of the trigger's own line), runs down:
  - hex `FPR 4E • / ZR XS LTHI (28.14.42.1)` --YES-->
      - box `X 0-63 TO XY / ICIB (28.21.61.1)`
  - hex `FPR 3E (28.14.32.1)` --YES-->
      - box `Z 32-49 TO / MAB (28.21.60.1)`
      - box `GT ZROC / TO LAOC (28.21.60.1)`

E. Next (drop from bus):
  - hex `ZR ADDR 8 (28.20.08.1)` --(exit line on right, no YES printed)-->
      - box `I CHK REQ (28.27.32.1)`
      - box `BLOCK ZR / XS LTH SIGNAL (28.20.70.1)`

F. Next vertical (dot on bus), items hang off it by dots:
  - hex `ZR EXT LTH • / ZR INSTR PREP / COMP (28.14.31.1)` --YES-->
      - box `COND FPR3 / TON CKT (28.14.31.1)`
  - hex `FPR 3 E • NO / CANCEL • FPR / 3 M • ZR 4 MNT / MD (28.14.33.1)` --YES-->
      - box `PANEL KEY / REQUEST (28.21.71.1)`
  - hex `FPR 3 NM (28.23.50.1)` --YES-->
      - box `COND FPR 3 / TON CKT (28.14.31.1)`
  - hex `ZR ADDR / 8 LTHD (28.20.60.1)` --YES-->
      - box `BLOCK ZR / EXT AND ZR XS / SIGNALS (28.20.60.1)`

G. Next (dot on bus):
  - hex `ZR XS LTH (28.23.60.1)` --YES--> (line down the right side, feeding two hexagons from above)
      - hex `FPR 4E•M (28.14.43.1)` --YES (exit on left)-->
          - box `TYPE 1 LD / TO LA (28.21.72.1)`
      - hex `FPR 4E•M (28.14.42.1)` --YES (exit on left)-->
          - box `I CHK / PARITY (28.21.75.1)`
      (no overbar seen on either "FPR 4E•M"; the two differ only in ALD number, .43 vs .42)

H. Next vertical (dot on bus, a second dot just below it):
  - hex `FPR 4E•ZR / ADDR 8 LTH (28.24.82.1)` --YES-->
      - box `SET LA EXT / STORE TAG (28.24.82.1)`
      - box `SET LA INT / STORE TAG (28.24.82.1)`
  - (same vertical continues down to) hex `FPR 4E•NM • / ZR ADDR 8 LTH (28.14.42.1)` --YES-->
      - box `I GEN / PARITY (28.44.14.1)`

I. Rightmost (end of bus):
  - hex `ZR INT LTH (28.23.60.1)` --YES (exit on left)--> vertical line with, in order:
      - box `COND FPR4E / TON (28.14.41.1)`
      - box `Z32-49 TO / MAB (28.14.42.1)`
      - hex `FPR4E (28.24.81.1)` --YES--> box `SET LA INT / FETCH (36.03.02.1)`
      - hex `FPR4E•SBC (28.14.43.1)` --YES--> box `TYPE 3LD / TO LA (28.21.74.1)`
      - hex `FPR4E•M (28.14.43.1)` --(no YES printed)--> box `TYPE 3LD / TO BCU (28.21.74.1)`

### Noted (Fig 3.1.12)
- `MOD ZR E (28.15.21.1)`; `MOD ZR E • MOD ZR M (28.15.21.1)`
- `BLOCK FP Z ALT TGR TON (28.27.32.1)`
- `BLOCK WBC + DEC TON (28.15.80.1)`
- `SAC • ZRXS • ZR INSTR PREP COMP • ZR + ZL PREP NOT BUSY • XOFI NM (28.12.11.1)`; `TON XOFI (28.12.11.1)`
- `ZR EQ 1 • ZR INSTR PREP COMP XOF1 E (28.12.11.1)`; `XOFI TC FTH (24.00.09.1)`
- `ZR INSTR PEP COMPLETE• ZR NOT EQ 1• XOF 1E`; `XOF 1 Z45-49 •P TO XAB (28.86.56.1)`
- `SAC • XOF 1M • LA EN TI +2 • CHKR EN TI • NOT CHKR SING ERR• ZR INSTR PREP COMP 28.14.41.1`
- `~(FPR AD INHBT DF) • DS • ~(IF INHBT DF) • GT FPR IND TO LA (28.25.30.1)`
- `DF MASK EQI • INH SET NOP BIT 17 FR DF (28.25.30.1)`; `DF SET LANOP (28.25.40.1)`
- `PRE CND LANOP FR ALARM (28.14.33.1)`
- `X 0-63 TO XY ICIB (28.21.61.1)`
- `GT ZROC TO LAOC (28.21.60.1)`
- `BLOCK ZR XS LTH SIGNAL (28.20.70.1)`; `BLOCK ZR EXT AND ZR XS SIGNALS (28.20.60.1)`
- `SET LA EXT STORE TAG (28.24.82.1)`; `SET LA INT STORE TAG (28.24.82.1)` -- both gated by `FPR 4E•ZR ADDR 8 LTH (28.24.82.1)`
- `TYPE 1 LD TO LA (28.21.72.1)` -- gated by `ZR XS LTH (28.23.60.1)` then `FPR 4E•M (28.14.43.1)`
- `TYPE 3LD TO LA (28.21.74.1)` -- gated by `ZR INT LTH (28.23.60.1)` then `FPR4E•SBC (28.14.43.1)`
- `TYPE 3LD TO BCU (28.21.74.1)` -- gated by `ZR INT LTH (28.23.60.1)` then `FPR4E•M (28.14.43.1)`
- `SET LA INT FETCH (36.03.02.1)`

---------------------------------------------------------------------------------------------------
## FIGURE 3.1.13. ZR FP TRIGGERS 2, 3, 4, AND 6 (SHEET 1 OF 3)
PDF page 75 (landscape; tiles f75-L/M; f75-R is blank). Page head: "M3-04-3   I UNIT FLOW DIAGRAMS".
Printed page tag: "1-25". Printed date: "2/1/62". No applicability note printed on this sheet.
On this sheet the ALD numbers are printed BELOW each box/hexagon, the AND-dot is a small `·` (written `•` here),
and lines carry arrowheads.

### Turn-on conditions of ZR FP 2 TGR
- hex, text line by line:
    `1Y21 • 1Y22 •`
    `~1Y23 • 1Y24 •`
    `~1Y25 + 1Y23`
    `(1Y25 + ~1Y24) •`
    `1Y21 • 1Y22 •`
    `COND FP CL R`
    `(28.26.51.1)`
  --YES-->
  (overbars seen: over "1Y23" on line 2, over "1Y25" on line 3, over "1Y24" inside the parentheses on line 4; none on lines 1 and 5)
- hex `SET 7R FP 2` (no ALD; the first letter of "7R" prints like a 7 -- [uncertain: ZR?]) --YES-->
  (both YES lines meet; arrow down labelled `TON`)

=> box (the trigger) `ZR FP 2 TGR` `(28.26.51.1)`

### Outputs of ZR FP 2 TGR (arrow down to an upper bus; the bus's left end also runs down the left margin to a lower bus)

Upper bus:
- hex `INSTR PREP COMP / ZL • FP Z ALT TGR OFF` `(28.27.32.1)` --YES-->
    - hex `NO T2 CHKR REQ / E• NO I CHKR REQ• / NO T1 CHKR REQ• / OK TO I CHK IC• / NO I CHKR REQ E3` `(28.41.50.1)` --YES-->
        - box `COND IWC1 TON CKT` `(28.41.51.1)`
        - box `COND IWC2 TON CKT` `(28.41.61.1)`
- hex `BLOCK FP RDY• / ZR INSTR PREP / COMPL•~(CANCEL FPL3E)` `(28.14.41.1)` --YES-->
    (overbar over "CANCEL FPL3E" only)
    - hex `SAC•FPL 3NE• I / CHKR EN• NOT CHKR / SING ERR• LA EN T / 1 & 2` `(28.14.41.1)` --YES-->
        - box `TON FPR 4` `(28.14.41.1)`

Lower bus (left to right):
- hex `FPR 4` `(28.14.42.1)` --YES-->
    - box `ICIB P POS 2-8 • / Z 32-40 TO ICIB` `(28.21.20.1)` `(28.21.61.1)`   (two ALD numbers printed under this box)
    - box `BLOCK GEN OF ERR / PRECND LA AD` `(28.38.70.1)`
- hex `FPR 4E • NM` `(28.14.42.1)` --YES-->
    (a small tick is printed at the top-left of the "F"; [uncertain: stub of an overbar, or a blemish])
    - box `FPR 4 I CHK / PARITY` `(28.21.75.1)`
- hex `FPR 4 E • SBC` `(28.14.43.1)` --YES--> (joins the next hexagon's YES line)
- hex `FPR 4E • FPR 4M` `(28.14.43.1)` --YES-->
    (same small tick at the top-left of the first "F"; [uncertain as above])
    - (both YES lines feed) box `FPR 4 E•M / TYPE 1 LD` `(28.21.72.1)`

### Noted (Fig 3.1.13 sheet 1)
- `BLOCK FP RDY• ZR INSTR PREP COMPL•~(CANCEL FPL3E) (28.14.41.1)`
- `SAC•FPL 3NE• I CHKR EN• NOT CHKR SING ERR• LA EN T 1 & 2 (28.14.41.1)`
- `INSTR PREP COMP ZL • FP Z ALT TGR OFF (28.27.32.1)`
- `BLOCK GEN OF ERR PRECND LA AD (28.38.70.1)`
- `FPR 4 E•M TYPE 1 LD (28.21.72.1)` -- fed by YES of `FPR 4 E • SBC (28.14.43.1)` and YES of `FPR 4E • FPR 4M (28.14.43.1)`
- `ICIB P POS 2-8 • Z 32-40 TO ICIB (28.21.20.1) (28.21.61.1)`

---------------------------------------------------------------------------------------------------
## FIGURE 3.1.13. ZR FP TRIGGERS 2, 3, 4, AND 6 (SHEET 2 OF 3)
PDF page 76 (landscape; tiles f76-L/M; f76-R is blank). Page head: "I UNIT FLOW DIAGRAMS   M3-04-3".
Printed page tag: "1-26". Printed date: "2/1/62". No applicability note printed on this sheet.
On this sheet the ALD numbers are printed BELOW each box/hexagon and WITHOUT parentheses; the AND-dot is printed
as a baseline period `.` in most hexagons (I keep `.` where a period is printed and `•` where a raised dot is printed).
The letter "F" of "FPR" in this sheet's lettering carries a small extra tick in nearly every occurrence, including
inside plain action boxes ("COND FPR4E TON"); I take it as a lettering artefact, not an overbar.

### Turn-on conditions of ZR FP 3 TGR
- hex `1Y NOT 23. / 1Y 24•1Y25• / COND FP CLR` `28.26.51.1` --(no YES printed; arrow)-->
- hex `SET ZR / FP 3` `28.26.51.1` --(no YES printed; exit on its left; arrow)-->

=> box `TON ZR / FP 3 TGR` `28.26.51.1`

### Outputs (arrow down from the box to a horizontal bus; three groups)

LEFT group -- the bus's left end turns down into a vertical line on the far left; items hang off it, top to bottom:
- box `COND FPR4E / TON` `28.14.41.1`   (direct from the bus, no hexagon)
- hex `FPR 4E` `28.14.42.1` --(no YES printed)--> box `Z32-49 TO / MAB` `28.21.60.1`
- hex `FPR4E.M` `28.14.43.1` --(no YES printed)--> box `TYPE 3LD / TO BCU` `28.21.74.1`
- hex `FPR 4E. / SBC` `28.14.43.1` --(no YES printed)--> box `TYPE 3LD / TO LA` `28.21.74.1`
- hex `ZR 1+2+3 / . IRPT / ENABLED` `28.23.70.1` --YES--> box `PRE CND / LA DS` `28.25.20.1`
    (there are small marks above "1+2" in "ZR 1+2+3"; [uncertain: overbar over "2", or blemish])
- hex `ZR EQ1` `28.23.70.1` --YES--> box `PRE CND / LA AD` `28.25.20.1`

MIDDLE group -- from the bus, plus a second vertical line that drops from the bus just left of this column:
- hex `~(FPR AD INHIB / DF) DS. IRPT / ENABLED. NOT / ZR 0-31` `28.23.61.1` --YES--> box `PRE CND / LA DS` `28.14.33.1`
    (overbar over the whole first line "FPR AD INHIB"; a second bar over the start of line 2 covering "DF" and
     [uncertain: possibly also "DS"] -- the bar ends about under the "S" of "DS")
- hex `ZR EXT / LTH. FPR4E` `28.24.82.1` --YES--> box `SET LA EXT / STORE TAG` `36.09.14.1`
- hex `ZR INT / LTH. FPR 4E` `28.24.82.1` --YES--> box `SET LA INT / STORE TAG` `36.09.15.1`

RIGHT group -- the bus's right end arrows down into:
- hex `FPR 4E` `28.14.43.1` --YES (exit on its LEFT)--> a vertical line running down, feeding in order:
    - hex `ZOAR EQ / 11+12+16-31` (no ALD printed under it) --YES-->
        - box `TON STORE / WAIT TGR` `28.42.51.1`
        - box `TON IRCY / REQ TGR` `28.42.72.1`
    - hex `PROGRAM / STORE / COMPARE` `28.42.72.1` --YES-->
        - box `TON IRCY / REQ TGR` `28.42.72.1`
    - hex `PROGRAM / STORE / COMPARE` `28.42.71.1` --YES-->
        - box `TON PIRCY / TRG` `28.42.71.1`    ("TRG" as printed; "PIRCY" as printed, the "I" is heavy/smudged)

### Noted (Fig 3.1.13 sheet 2)
- `TON STORE WAIT TGR 28.42.51.1` -- gated by `FPR 4E 28.14.43.1` YES, then `ZOAR EQ 11+12+16-31` YES
- `TON IRCY REQ TGR 28.42.72.1` (first) -- same gating as TON STORE WAIT TGR (same YES line)
- `PROGRAM STORE COMPARE 28.42.72.1` --YES--> `TON IRCY REQ TGR 28.42.72.1` (second), under `FPR 4E 28.14.43.1` YES
- `PROGRAM STORE COMPARE 28.42.71.1` --YES--> `TON PIRCY TRG 28.42.71.1`, under `FPR 4E 28.14.43.1` YES
- `SET LA EXT STORE TAG 36.09.14.1` -- gated by `ZR EXT LTH. FPR4E 28.24.82.1`
- `SET LA INT STORE TAG 36.09.15.1` -- gated by `ZR INT LTH. FPR 4E 28.24.82.1`
- `TYPE 3LD TO BCU 28.21.74.1` -- gated by `FPR4E.M 28.14.43.1`
- `TYPE 3LD TO LA 28.21.74.1` -- gated by `FPR 4E. SBC 28.14.43.1`
- `~(FPR AD INHIB DF) DS. IRPT ENABLED. NOT ZR 0-31 28.23.61.1`
- `ZR 1+2+3 . IRPT ENABLED 28.23.70.1`

---------------------------------------------------------------------------------------------------
## FIGURE 3.1.13. ZR FP TRIGGERS 2, 3, 4, AND 6 (SHEET 3 OF 3)
PDF page 77 (landscape; tiles f77-L/M/R). Page head: "M3-04-3   I UNIT FLOW DIAGRAMS".
Printed page tag: "1-27/1-28". Printed date: "2/1/62". No applicability note printed on this sheet.
Conventions on this sheet: ALD numbers printed BELOW each box/hexagon, WITHOUT parentheses; AND is a baseline
period `.` (kept as printed); lines carry arrowheads. "(no YES)" = the word is not printed at that exit.
The sheet holds THREE things: ZR FP6 TGR (left), a box "ZR FP4 OR ZR FP6" (centre), ZR FP4 TGR (right).

### (1) ZR FP6 TGR
Turn-on:
- hex `1YNOT22 . / 1Y21.1Y23. / 1Y24.1Y25. / COND FP CLR` `28.26.51.1` --(no YES)-->
- box `SET / ZR FP6 / TGR` `28.26.51.1` -->
  (the two lines meet; arrow down labelled `TON`)
=> box `ZR FP6 TGR` `28.26.51.1`

Outputs. An arrow drops from the trigger to a horizontal bus. The bus runs left to a vertical line down the far
left ("FP6 left column"), and right to the box `ZR FP4 OR ZR FP6` (arrowhead into that box's left side).

(1a) From the bus, directly:
- hex `FPR4E` `28.24.82.1` --YES--> box `SET LA / EXT STORE / TAG` `28.24.82.1`
- hex `~(FPR AD INHIB / DF OR DS). NOT / ZR 0-31. IRPT / ENABLED` `28.23.61.1` --YES-->
    (overbar over the whole first line "FPR AD INHIB"; second bar over the start of line 2, covering "DF OR D"
     and [uncertain: whether it reaches the "S" of "DS"])
    - box `PRE CND / LA DF` `28.14.33.1`
    - hex `MDF / EQ 1` `28.23.61.1` --YES (exit on its left)--> box `FPR3 PRE / CND LA NOP / FR ALARM` `28.14.33.1`

(1b) FP6 left column (vertical line down the far left), top to bottom:
- hex `FPR4E` `28.14.42.1` --YES--> box `SET ADR / 13 ON / MAB` `28.21.10.1`
- hex `ZR EXT LTH. / ZR INSTR PREP / COMPLETE. ~(FPDD / M) . LAAR 1 BUSY` `28.10.11.1` --YES-->
    (overbar over "FPDD" at the end of line 3 and over the "M" that starts line 4; NO overbar seen over "LAAR 1 BUSY";
     there is a stray dot after the "M" then a period before "LAAR")
    - box `COND FPDD / E TGR` `28.10.11.1`
- hex `IRPT ENABLED / .ZR1 + 2 + 3` `28.23.70.1` --YES--> arrow down onto a horizontal line that joins the two boxes:
    - box `CONDITION / LA DF TAG` `28.25.30.1`  (line leaves its right side, no arrowhead at this box)
    - box `CONDITION / LA NOP / FR DF` `28.25.30.1`  (arrowhead into its left side)
    [connection note: I cannot tell whether the YES line gates both boxes or only passes through the first to the second]
- hex `FPR3E / AND NO / CANCEL. / SBC` `28.14.33.1` --YES--> (line down the right)
- hex `FPR3E / AND NO / CANCEL. / FPR3M` `28.14.33.1` --YES--> (joins the same line)
    - (both feed) box `TYPE 3 LD / TO LA / 28.21.74.1`   (ALD printed inside the box's bottom edge)

(1c) A vertical line straight down from the ZR FP6 TGR / bus junction:
- hex `ZR NE / LTH` `28.23.60.1` --YES (exit on its LEFT)--> vertical line down, feeding:
    - hex `FPR4E / M` `28.14.43.1` --YES-->
        - box `TYPE 3 / LOAD TO LA` `28.21.74.1`
        - box `T3 LD TO / BCU WAIT / FOR ACCEPT` `28.21.74.1`
    - hex `ZR INSTR / PREP / .COMPLETE` `28.14.41.1` --YES--> box `COND FPR4E / TON` `28.14.41.1`
        (a small mark precedes "COMPLETE"; [uncertain: a period or a blemish])

### (2) Box `ZR FP4 / OR / ZR FP6` `28.23.50.1`
Inputs as drawn: the ZR FP6 bus enters its left side (arrowhead into the box). A line leaves its right side and
runs to the junction under ZR FP4 TGR (an open arrowhead at that junction end points rightward, toward the junction;
none at the box). Its bottom exit is labelled `YES`, arrow down to a sub-bus. Three columns hang from the sub-bus.

(2a) OR column A (sub-bus's left end turns down), top to bottom:
- box `COND / XOF 1E / TON` `28.12.11.1`  (direct)
- hex `ZR ADR 8 / LTH` `28.20.60.1` (ALD printed inside the hexagon) --YES--> box `BLOCK ZR / EXT AND / ZR EXT` `28.20.60.1`
- hex `FPR 3 / .NM` `28.23.50.1` --YES--> box `COND FPR 3 / E TON` `28.14.31.1`
- hex `FPR3E` `24.14.32.1` (printed inside the hexagon; first group reads "24" -- [uncertain: 24? 28?]) --YES-->
    - box `Z32-49 TO / MAB` `28.21.60.1`
    - box `GATE ZROC / TO LAOC` `28.21.60.1`
- hex `FPR3E AND / NO CANCEL. / ZR4 MNT MD. / FPR3M` `28.14.33.1` --YES--> box `PANEL / KEY / REQUEST` `28.14.33.1`
- hex `FPR3E` `28.24.82.1` --YES--> box `SET LA / EXT STORE / TAG` `36.09.14.1`  (this box is drawn to the LEFT, below the FP6 area)

(2b) OR column B (vertical line straight down under the box), top to bottom:
- hex `FPR3E / AND NO / CANCEL. / SBC` `21.14.33.1` (first group reads "21" -- [uncertain: 21? 28?]) --YES-->
    box `MODIFIED / TYPE 3 LD / TO LA` `28.21.75.1`  ([uncertain: the "21" group is broken: 28.21.75.1?])
- hex `FPR3E / AND NO / CANCEL. / FPR3M` `28.14.33.1` --YES--> box `XFER AND / RESET NIDC` `28.21.73.1`
- hex `ZR / . ADDR 8` `28.20.08.1` --YES--> box `I CHR REQ / ZR` `28.27.32.1`   ("CHR" as printed)
- hex `FPR4E` `28.24.80.1` --YES--> arrow down onto a horizontal line with arrowheads into both:
    - box `SET LAOC / 6, 8 & 9` `28.24.24.1` `28.24.26.1`  (two ALD numbers printed under it)
    - box `SET / LAOP / TAG` `36.05.01.1`  ([uncertain: partly under a scan streak: 36.05.01.1?])
- hex `ZR INSTR / PREP COMPLETE. / ZR NOT EQ1. / XOF 1E` `28.12.12.1` --YES--> box `Z45-49. / P TO XAB` `28.86.56.1`
- (line right, up, right, down into) hex `[ZR] INSTR PREP COMPL. / [XOF] 1M+ ADR 8 LTH. / [uncertain: I?][.] CHKR EN T1. LA EN T1+2 / [.] NO CHKR SINGLE ERROR` `28.14.21.1` --YES-->
    (the hexagon's left edge is under a dark scan streak; bracketed starts of each line are partly hidden)
    - joins the next hexagon's YES line
- (bottom end of the column, line right, down into) hex `[.?]ZR INSTR PREP COMPL / . ZR INT LTH. / [L]A EN T3. ~(FPR3E LTH) / . SAC` `28.14.21.1` --YES-->
    (overbar over "FPR3E LTH"; left edge under the same streak; ALD's last digits faint: [uncertain: 28.14.21.1])
    - (both YES lines feed) box `TON / FPR2E` `28.14.21.1`

(2c) OR column C (sub-bus's right end turns down), top to bottom:
- box `BLOCK / TYPE 2 / LOAD` `28.14.31.1`  (direct; ALD faint: [uncertain: 28.14.31.1])
- hex `ZR ADR 8 / . LTH. FPR 2 / E . NM` `28.14.22.1` --YES--> box `I GEN / PARITY` `28.20.08.1` ([uncertain: 28.20.08.1; digits faint])
- hex `FPR4E` `28.14.42.1` --YES--> box `BLOCK XFER / OF ZROC / TO LAOC` `28.21.60.1`
- (branch: line right, UP, right, down into) hex `ZR ADR 8 / LTH. FPR2E` `28.24.82.1` --YES-->
    - box `SET LA EXT / STORE TAG` `28.24.82.1`
    - box `SET LA INT / STORE TAG` `28.24.82.1`
- (branch right, down into) hex `ZR INSTR / PREP COMPLETE. / ZREQ1 / .XOF 1E` `28.12.12.1` --YES--> box `XOF 1E / TC FETCH` `24.00.09.1`
- (column's bottom end: right, down, right, down into) hex `FPR3E` `28.14.32.1` --YES-->
    - box `Z32-49 / TO MAB` `28.14.32.1`
    - box `GT ZROC / TO LAOC` `28.21.60.1`

### (3) ZR FP4 TGR
Turn-on:
- hex `~1Y21. ~1Y23 / .1Y24-1Y NOT / 25. COND FP CL` `28.26.51.1` --(no YES)-->
    (overbars over "1Y21" and over "1Y23"; the mark between "1Y24" and "1Y NOT" prints as a short dash;
     the last word is cut by the hexagon edge after "CL" -- [uncertain: CLR])
- box `SET / ZRFP4` `28.26.51.1` -->
  (meet; arrow down labelled `TON`)
=> box `ZR FP4 TGR` `28.26.51.1`

Outputs. Arrow down to a junction on a horizontal bus (the line from box (2) arrives at this junction from the left).

(3a) From the bus, left to right:
- hex `FPR3E / AND NO / CANCEL. / FPR3M` `28.14.33.1` --YES--> (line down the right; see (3b) first item)
- a vertical line dropping from the bus ("FP4 second column"), feeding in order:
    - box `BLOCK FPR3 / COND LA DF` `28.14.33.1`  (direct)
    - hex `FPR3E / AND NO / CANCEL` `28.14.33.1` --YES--> hex `PROGRAM / STORE COMPARE. / ACCEPT OR / COMPARE` `28.42.72.1`
          --YES (exit on its left)--> box `TON IRCY / REQ TGR` `28.42.72.1`
    - (column's bottom end: right, UP, right, down into) hex `IRPT ENABLED / .NOT / ZRO-15` `28.23.61.1` --YES-->
        - box `FPR3 PRE / COND LA DS` `28.23.61.1`
        - box `FPR3 PRE / COND LA NOP / FR ALARM` `28.23.61.1`
- hex `ZR ADR 8 / LTH + ZR / INT LTH. / FPR4E` `28.24.82.1` --YES--> box `SET LA / INT STORE / TAG` `36.09.15.1`
- (bus's right end) hex `ZR 1 + 2 + 3. / IRPT / ENABLED` `28.23.70.1` --YES--> box `PRE CND / LA DS` `28.25.20.1`

(3b) Vertical line straight down under ZR FP4 TGR, top to bottom:
- hex `FPR3E / AND NO / CANCEL / . SBC` `28.14.33.1` --YES--> (joins the YES line of the FPR3M hexagon in (3a))
    - (both feed) box `TYPE 3 / LOAD TO LA` `28.21.74.1`
    - (both feed) box `T3 LD TO / BCU WAIT / FOR ACCEPT` `28.21.74.1`
- hex `ZR EQ 1` `28.23.70.1` --YES-->
    - box `FPR PRE COND / LA AD TO IND / XFER CKTS` `28.25.20.1`
    - box `FPR AD / INHIB DF AND / DS` `28.23.70.1`
    - box `FPR PRE COND / LA DS TO IND / XFER CKTS` `28.25.20.1`
- (branch left, down into) hex `FPR4E` `28.14.43.1` --YES--> line right, UP, then a horizontal bus feeding:
    - hex `ZOAR EQ 11 / +12 + 16 - 31` `28.42.51.1` --YES-->
        - box `TON STORE / WAIT TGR` `28.42.51.1`
        - box `TON IRCY / REQ TGR` `28.42.72.1`
    - hex `PROGRAM / STORE / COMPARE` `28.42.72.1` --YES--> box `TON IRCY / REQ TGR` `28.42.72.1`
    - hex `PROGRAM / STORE / COMPARE` `28.42.71.1` --YES--> box `TON PIRCY / TGR` `28.42.71.1`
- (column's end) hex `ZR NE / LTH` `28.23.60.1` --YES--> line right, UP, then a horizontal bus feeding:
    - hex `FPR4E` `28.14.42.1` --YES (exit on its left)--> box `Z32-49 / TO MAB` `28.21.60.1`
    - hex `ZR INSTR / PREP COMPLETE` `28.14.41.1` --YES--> box `COND / FPR4E / TON` `28.14.41.1`
    - hex `FPR4 / E . M` `28.14.43.1` --YES--> (meets the next hexagon's exit line)
    - hex `FPR4E. / SBC` `28.14.43.1` --(no YES; exit on its left)-->
        - (both feed) box `TYPE 3 / LOAD TO LA` `28.21.74.1`
        - (both feed) box `T3 LD TO / BCU WAIT / FOR ACCEPT` `28.21.74.1`

### Noted (Fig 3.1.13 sheet 3)
STORE TAG:
- FP6: `FPR4E 28.24.82.1` --YES--> `SET LA EXT STORE TAG 28.24.82.1`
- FP4 OR FP6: `FPR3E 28.24.82.1` --YES--> `SET LA EXT STORE TAG 36.09.14.1`
- FP4 OR FP6: `ZR ADR 8 LTH. FPR2E 28.24.82.1` --YES--> `SET LA EXT STORE TAG 28.24.82.1` and `SET LA INT STORE TAG 28.24.82.1`
- FP4: `ZR ADR 8 LTH + ZR INT LTH. FPR4E 28.24.82.1` --YES--> `SET LA INT STORE TAG 36.09.15.1`
STORE WAIT / RCY / COMPARE:
- FP4: `FPR4E 28.14.43.1` YES, then `ZOAR EQ 11 +12 + 16 - 31 28.42.51.1` YES --> `TON STORE WAIT TGR 28.42.51.1`, `TON IRCY REQ TGR 28.42.72.1`
- FP4: `FPR4E 28.14.43.1` YES, then `PROGRAM STORE COMPARE 28.42.72.1` YES --> `TON IRCY REQ TGR 28.42.72.1`
- FP4: `FPR4E 28.14.43.1` YES, then `PROGRAM STORE COMPARE 28.42.71.1` YES --> `TON PIRCY TGR 28.42.71.1`
- FP4: `FPR3E AND NO CANCEL 28.14.33.1` YES, then `PROGRAM STORE COMPARE. ACCEPT OR COMPARE 28.42.72.1` YES --> `TON IRCY REQ TGR 28.42.72.1`
LAAR:
- FP6: `ZR EXT LTH. ZR INSTR PREP COMPLETE. ~(FPDD M) . LAAR 1 BUSY 28.10.11.1` --YES--> `COND FPDD E TGR 28.10.11.1`
TYPE n LD / WAIT:
- `TYPE 3 LD TO LA 28.21.74.1` (FP6; from `FPR3E AND NO CANCEL. SBC` and `FPR3E AND NO CANCEL. FPR3M`, both 28.14.33.1)
- `TYPE 3 LOAD TO LA 28.21.74.1`, `T3 LD TO BCU WAIT FOR ACCEPT 28.21.74.1` (three occurrences: FP6 under `ZR NE LTH`/`FPR4E M`;
  FP4 under `FPR3E AND NO CANCEL. FPR3M` + `FPR3E AND NO CANCEL . SBC`; FP4 under `ZR NE LTH`/`FPR4 E . M` + `FPR4E. SBC`)
- `MODIFIED TYPE 3 LD TO LA 28.21.75.1`; `BLOCK TYPE 2 LOAD 28.14.31.1`
BLOCK / LAOC / LAOP / NOP / IND / XAB / XOF:
- `BLOCK ZR EXT AND ZR EXT 28.20.60.1`; `BLOCK XFER OF ZROC TO LAOC 28.21.60.1`; `BLOCK FPR3 COND LA DF 28.14.33.1`
- `GATE ZROC TO LAOC 28.21.60.1`; `GT ZROC TO LAOC 28.21.60.1`; `SET LAOC 6, 8 & 9 28.24.24.1 28.24.26.1`; `SET LAOP TAG 36.05.01.1`
- `CONDITION LA NOP FR DF 28.25.30.1`; `FPR3 PRE CND LA NOP FR ALARM 28.14.33.1`; `FPR3 PRE COND LA NOP FR ALARM 28.23.61.1`
- `FPR PRE COND LA AD TO IND XFER CKTS 28.25.20.1`; `FPR PRE COND LA DS TO IND XFER CKTS 28.25.20.1`; `FPR AD INHIB DF AND DS 28.23.70.1`
- `Z45-49. P TO XAB 28.86.56.1`; `COND XOF 1E TON 28.12.11.1`; `XOF 1E TC FETCH 24.00.09.1`
- `ZR INSTR PREP COMPLETE. ZR NOT EQ1. XOF 1E 28.12.12.1`; `ZR INSTR PREP COMPLETE. ZREQ1 .XOF 1E 28.12.12.1`
- `[ZR] INSTR PREP COMPL. [XOF] 1M+ ADR 8 LTH. [I?] CHKR EN T1. LA EN T1+2 . NO CHKR SINGLE ERROR 28.14.21.1`
- `ZR INSTR PREP COMPL . ZR INT LTH. LA EN T3. ~(FPR3E LTH) . SAC 28.14.21.1`
- `XFER AND RESET NIDC 28.21.73.1`

---------------------------------------------------------------------------------------------------
## FIGURE 3.1.14. ZR IHW TRIGGER, IHW RDY TRIGGER, AND IHW EX ZR TRIGGER
PDF page 78 (tiles f78-T/B; diagram upright, caption and margins printed sideways). Page head: "M3-04-3   I UNIT FLOW DIAGRAMS".
Printed page tag: "1-29/1-30". Printed date: "2/1/62" (first digit touches a scan line).
Applicability note: "CPU 7101 / SER. NO. 30,004 / AND HIGHER".
ALD numbers are inside the boxes, in parentheses. Three separate groups on the page.

### (1) ZR IHW TGR
(no turn-on hexagons are drawn above it)
box `ZR IHW TGR (28.26.61.1)` --> dot, branching to two hexagons:
- hex `ZL MT (28.26.61.1)` --YES-->
    - box `COND IHW RDY / ZR TGR TON CKT (28.26.11.1)`
    - box `COND IHW EX / ZR TGR TON CKT (28.26.11.1)`
- hex `SAC • MOD / ZR M` (no ALD) --YES-->
    - box `TON IHW RDY / TGR (28.26.11.1)`
    - box `TON IHW EX / ZR TGR (28.26.11.1)`

### (2) IHW EX ZR TGR
Turn-on:
- hex `SET IHW / EX TGR (28.26.11.1)` --YES-->
- hex `NOT ZR / MOD • SAC (28.26.11.1)` --YES-->
  (meet at a dot; line down labelled `TON`)
=> box `IHW EX ZR TGR (28.26.11.1)`
Outputs (one vertical line down, with dots):
- box `BLOCK XF+ / DEC TON (28.15.50.1)`   (left of first dot)
- box `BLOCK GEN OF / INSTR PREP COMP / ZL (28.15.32.1)`   (right of first dot)
- box `BLOCK MOD / ZL TON (28.15.40.1)`   (left of second dot)
- box `BLOCK ZL / DEC TON (28.27.30.1)`   (right of second dot)
- hex `NOT ZL MOD • / XF + DEC ZL (28.15.51.1)` --YES-->
    - hex `ZR INSTR COMP (28.15.51.1)` --YES-->
        - box `IHW RDY ZL (28.15.41.1)`

### (3) IHW RDY ZR TGR
Turn-on:
- hex `NOT ZR MOD • SAC • / YL-ZR M • ZR IHW / AND ZL MT (28.26.11.1)` --YES-->
- hex `SET HW RDY T (28.26.11.1)` --YES-->     ("HW", not "IHW", as printed)
  (meet at a dot; line down labelled `TON`)
=> box `IHW RDY ZR TGR (28.26.11.1)`
Outputs (vertical line down to a dot, then three ways):
- (left of the dot) box `BLOCK YR-ZL / M TGR TOF (28.15.30.1)`
- (continuing down, then left) hex `YR - ZL E` (no ALD) --YES-->
    - box `RST MOD / REQ TGR (28.26.21.1)`
- (right of the dot) hex `YR-XL M (28.15.32.1)` ("XL" as printed) --(exit on its right, no YES printed)--> a long vertical line
  down the right side of the page, with a dot at each of the following, top to bottom:
    - box `BLOCK YR-ZL / M TGR TOF (28.15.30.1)`
    - box `COND LOP 4 / TON CKT (28.88.34.1)`
    - box `COND LOP 5 / TON CKT (28.88.34.1)`
    - box `COND LAMI / TON CKT (28.81.11.1)`
    - box `COND EN-DIS / TON CKT (28.70.54.1)`
    - box `COND DEC I / TON CKT (28.75.11.1)`
    - box `COND EMFI / TON CKT (28.70.34.1)`
    - box `COND XSF3 / TON CKT (28.71.11.1)`
    - box `COND EMF5 / TON CKT (28.70.21.1)`
    - box `COND DEC 3 / TON CKT (28.70.14.1)`
    - box `COND DEC 4 / TON CKT (28.79.14.1)`
    - box `NOT PRE DSAB (37.51.03.1)`
    - box `COND ADD 3 / TON CKT (28.75.51.1)`
    - box `COND ADD I / TON CKT (28.75.71.1)`
    - hex `EX + RN (28.89.32.1)` --YES--> box `ALLOW LARCY TON (28.42.81.1)`
    - hex `SAC (28.87.64.1)` --YES--> box `TON I EXP TGR (28.87.64.1)`
    - (end of the line) hex `BE + BEW + / BD + SIC-BE- / BEW-BD (28.89.32.1)` --YES--> box `ALLOW LARCY / TON (28.42.81.1)`

### Noted (Fig 3.1.14)
- `SAC • MOD ZR M`; `NOT ZR MOD • SAC (28.26.11.1)`; `NOT ZR MOD • SAC • YL-ZR M • ZR IHW AND ZL MT (28.26.11.1)`
- `BLOCK XF+ DEC TON (28.15.50.1)`; `BLOCK MOD ZL TON (28.15.40.1)`; `BLOCK ZL DEC TON (28.27.30.1)`;
  `BLOCK GEN OF INSTR PREP COMP ZL (28.15.32.1)`; `BLOCK YR-ZL M TGR TOF (28.15.30.1)` (twice)
- `NOT ZL MOD • XF + DEC ZL (28.15.51.1)`
- `RST MOD REQ TGR (28.26.21.1)`
- `COND LOP 4 TON CKT (28.88.34.1)`; `COND LOP 5 TON CKT (28.88.34.1)`; `COND LAMI TON CKT (28.81.11.1)`
- `COND XSF3 TON CKT (28.71.11.1)`
- `EX + RN (28.89.32.1)` --YES--> `ALLOW LARCY TON (28.42.81.1)`
- `BE + BEW + BD + SIC-BE-BEW-BD (28.89.32.1)` --YES--> `ALLOW LARCY TON (28.42.81.1)`
- `TON I EXP TGR (28.87.64.1)`

---------------------------------------------------------------------------------------------------
## FIGURE 3.1.15. ZL MOD REQ TRIGGER AND MOD ZL SEQUENCER
PDF page 79 (tiles f79-T/B; diagram upright, caption and margins printed sideways). Page head: "M3-04-3   I UNIT FLOW DIAGRAMS".
Printed page tag: "1-31/1-32". Printed date: "2/1/62".
Applicability note: "CPU 7101 / SER. NO. 30,004 / AND HIGHER".
ALD numbers are inside the boxes, in parentheses.

IMPORTANT reading caveat for this page: several hexagons carry horizontal rules BETWEEN their text lines. Where a rule
sits clearly above a word with a gap I write `~`. Where a rule sits tight under the upper line (so it could be an
underline of the upper words or an overbar of the lower words) I do NOT convert it to `~`; I describe it instead.

### (A) ZL MODIFY REQUIRED TGR
Turn-on (five hexagons; all YES lines join one horizontal line; the drop to the trigger is labelled `TON ZL MOD R`):
1. hex `SET MOD L / TGR (28.26.23.1)` --YES-->
2. hex `SBC • 1YL MOD / DEC • YL - ZLE (28.26.23.1)` --YES-->
3. hex, line by line:
     `~(IMM IX 1YR) + FULL`
     `WD SC•1Y61 + 1Y60 +`
     `1Y62 + 1Y63•DEC MOD`
     `REQ FR 1YR•UNCOND +`
     `BIT BR CL 1YR + BIT BR`
     `DEC• 1YRD•SBC•YR ZLE`
     `(28.26.23.1)`
   --YES-->
   (rules: a clear overbar above "IMM IX 1YR" on line 1. Further rules sit tight UNDER these words: "DEC MOD" (line 3);
    "REQ FR 1YR" and, separately, "UNCOND" (line 4); "BIT" and, separately, the second "1YR" (line 5). They touch the
    bottoms of those words and are far from the tops of the words below, so they read as underlines;
    [uncertain: whether any of them is meant as an overbar of the text beneath].)
4. hex `SBC • YR-ZLE • 1Y63 • / DEC MOD REQ FR 1 YR / • 1 YR BRC + UNCOND + / BIT BR CL • BIT BR DEC 2 (28.26.23.1)` --YES-->
5. hex `NL IB MOD / D • YL-ZLE • / SBC (28.26.23.1)` --YES-->
=> box `ZL MODIFY REQUIRED TGR (28.26.23.1)`

Outputs (line down to a dot on a horizontal bus; from left to right):
- far-left vertical line, with a dot at each:
    - box `BLOCK WBC + DEC TON (28.15.80.1)`
    - box `BLOCK ZR WAS IHW TOF (28.15.51.1)`
    - box `BLOCK XF + DEC TON (28.15.50.1)`
    - box `COND MOD ZL TON (28.15.40.1)`
- second vertical line, with a dot at each:
    - box `BLOCK YL-ZR TON (28.15.10.1)`
    - box `BLOCK YR-ZR TON (28.15.60.1)`
    - box `COND MOD ZL TON (28.15.40.1)`   (left of the last dot)
    - box `BLOCK GEN OF / INSTR PREP COMPL ZL (28.15.32.1)`   (right of the same dot)
- hex `SAC (28.15.50.1)` --YES--> box `TON XF + DEC (28.15.50.1)`
- hex `YR - ZL M (28.15.32.1)` --YES--> vertical line with dots:
    - box `TON Y- Z START (28.26.11.1)`
    - box `ZL + ZR PREP / NOT BUSY (28. 20.21.1)`
    - (dot where the YES line of the `YL - ZL M` hexagon below joins) then down into:
    - hex `ZR WAS IHW (28.15.71.1)` --YES--> box `Y - Z M MOD REQ (28.70.42.1)`
- hex `YL - ZL M (28.15.71.1)` --YES--> line down and left, joining the dot just above `ZR WAS IHW`
    (so `ZR WAS IHW` is fed by the YES lines of both `YR - ZL M` and `YL - ZL M`)

### (B) MODIFY ZL SEQUENCER
Turn-on (five hexagons; all YES lines join one horizontal line; the drop is labelled `TON MOD ZL`):
1. hex `OK TO MOD ZL • YR-ZL / M • NOT CHKR SING / ERR • NOT IHW-EX T • / FW NOT ST • SAC • ZL / MOD REQ (28.15.40.1)` --YES-->
2. hex `SAC • NO LA CHKR / REQ • NOT CHKR SING / ERR • OK TO MOD ZL • / XF + DEC ZL MC • FW / NOT ST (28.15.40.1)` --YES-->
3. hex `YL - ZLM • / SAC • ZL MOD / REQ (28.15.40.1)` --YES-->
4. hex `NOT FW NOT S • / ZR WAS IHW • NOT / IHW EXC • YR - ZL / M • SAC • ZL MOD (28.15.40.1)` --YES-->
     (one rule lies between line 1 and line 2; it starts at the left margin and is exactly as long as "ZR WAS IHW";
      [uncertain: overbar of "ZR WAS IHW" (i.e. `~(ZR WAS IHW)`), or underline of "NOT FW NOT"])
5. hex `SAC • NOT FW / NOT S • XF + DEC / ZL M • ZL MOD / R (28.15.40.1)` --YES-->
=> bar `MODIFY ZL SEQUENCER (28.15.40.1)` with three exits on its lower edge labelled `E`, `E•M`, `M`.

Connection caveat: the three exits each end in a dot on ONE continuous horizontal line (no gap visible between the
E dot, the E•M dot and the M dot at 450% enlargement). That line runs left to the "left vertical" below and right to
the "right vertical" below; the E•M exit also continues straight down. I therefore list the three groups by position
(left = under/left of `E`; centre = straight down from `E•M`; right = right of `M`) and do not claim the line is split.

(B1) LEFT group -- the horizontal line runs left, then turns down as a long vertical line to the bottom of the page.
Hung on that vertical, top to bottom:
- dot: (left) box `TON MOD ZL M TGR / WITH NEXT SBC (28.15.40.1)`;
       (right, from the same dot) line to hex `PX • FW NOT ST • / XF + DEC ZLM + (28.15.42.1)` --YES--> vertical line with dots:
           (the hexagon text ends with a trailing `+` as printed)
           - box `PREP GT Z0 - 23 / TO ICIB (28.79.65.1)`   ([uncertain: last digit of "23": 23? 28?])
           - box `COND IDC FR / I PAR ERR PREP (28.99.03.1)`
           - box `TON PX YL TGR (28.78.34.1)`
           - box `PREP SET ONE / TO ICIB PAR (28.21.20.1)`
           - (bottom dot) horizontal line feeding three hexagons:
               - hex `MOD ZL M • CD / 2Y - ZL (28.15.42.1)` --YES--> box `P COND ICOB / TO 2Y 0-63 (28.44.16.1)`
               - hex `MOD ZL M • CD / 1Y - ZL (28.15.42.1)` --YES--> box `P COND ICOB / TO 1Y 0 - 63 (28.44.16.1)`
               - hex `~(MOD ZL) (28.15.42.1)` --YES-->     (clear overbar above "MOD ZL")
                   - box `IP CHK PAR (28.98.07.1)`
                   - box `I CHK E • NM P (38.03.03.1)`
- dot: hex `ZL FP CL • ~FW / NOT ST + PROG / IX (28.15.41.1)` --YES--> box `Z 0-17 ABB PREP (28.96.03.1)`
       (rules: a clear overbar above "FW" on line 1. Between lines 1 and 2: one rule under "ZL FP CL" / above "NOT ST",
        and a separate rule under "FW" / above "PROG". A short rule above "IX" on line 3 (it also underlies the "+" of line 2).
        [uncertain: which of these are overbars of the lower text -- possible reading `~(NOT ST) + ~PROG ~IX`; not asserted])
- dot: hex `ZL FP CL (28.15.41.1)` --YES--> box `HOT 1 TO ABB P2 (28.96.41.1)`
- dot: hex `ZL IHWT • / FW ON BDS + / PROG IX (28.15.41.1)` --YES-->
       (rules: one between line 1 and line 2, about the length of "FW ON BDS"/"ZL IHWT •"; one between line 2 and line 3,
        about the length of "PROG IX"/"FW ON B". [uncertain: overbars of "FW ON BDS" and of "PROG IX", or underlines])
       - box `Z 0-17 ABB PREP (28.96.03.1)`
       - box `Z 18 ABB PREP (28.96.03.1)`
       - box `Z 18 TO ABB P2 - / ADJ PAR Z 18 - 23 (28.96.07.1)`
- dot with a horizontal line running both ways:
    - (left) hex `FWS + NOTS • / FW ON BDS + / PROG IX (28.15.41.1)` --YES-->
        (same two rules as the previous hexagon, between lines 1/2 and 2/3; same uncertainty)
        - box `Z 0-17 ABB PREP (28.96.03.1)`
        - box `Z 18 ABB PREP (28.96.03.1)`
        - box `Z 19-23 ABB PREP (28.96.07.1)`
    - (right) hex `SBC (28.15.70.1)` --YES--> box `TOF YL - ZL M TGR (28.15.70.1)`
    - (further right, a dot) a second vertical line down, with dots:
        - box `X 0-23 TO ABA• / X 24-27 TO ABA (28.96.01.1)`
        - box `SET IDC ON / IAUC ERR (28.51.01.1)`
        - box `RESET ZL / ADDR 8 TGR (28.27.57.1)`   (on the right of the line)
        - box `Y - Z L + MOD ZL • / RST ZL TAGS (28.51.08.1)`
        - box `HOLD DATA / SELECT (27.09.07.1)`   (end of that line)
    - (right end of the horizontal line) hex `SBC (28.26.23.1)` --YES--> box `TON 1 BIT / MOD TGR (28.26.23.1)`
- dot: box `COND XF + DEC / ZL M TON CKT (28.15.50.1)`
- (bottom end of the long vertical) hex `SBC (28.15.30.1)` --YES--> box `TOF YR - ZL M TGR (28.15.30.1)`
       (the ALD number in this last box is printed overlapping the text line above it)

(B2) CENTRE group -- straight down from the `E•M` dot:
- dot: box `Y - Z + MOD ZL CND / ZL MA TAGS (28.51.01.1)`   (to the left of the line)
- dot, then a horizontal line feeding three hexagons:
    - hex `MOD ZLM • / ZL FP CL (28.15.41.1)` --YES--> box `GT AOB 18 TO ZL (28.27.50.1)`
    - hex `FWS + NOTS • / MOD ZL M (28.15.41.1)` --YES--> (line down to a dot beside) box `GT AOB 24 TO ZL (28.27.50.1)`;
          from that dot a horizontal line continues right to a dot on the next hexagon's YES line
    - hex `ZL IHW • MOD / ZL M (28.15.41.1)` --YES--> vertical line with dots:
          - (dot joined to the `GT AOB 24 TO ZL` line just described)
          - box `GT AOB 18 TO ZL (28.27.50.1)`
          - box `GT AOB 19 TO ZL (28.27.50.1)`
      (as drawn, `GT AOB 24 TO ZL` is tied to the YES lines of both `FWS + NOTS • MOD ZL M` and `ZL IHW • MOD ZL M`,
       and so are the lower `GT AOB 18`/`GT AOB 19` boxes; I cannot separate them)

(B3) RIGHT group -- the horizontal line runs right, then turns down as a vertical line with dots, top to bottom:
- box `BLOCK GEN OF I / CHK E • NM P • I CHK / PAR (28.15.42.1)`
- box `COND YR - ZR / TON CKT (28.15.60.1)`
- box `COND YL - ZR / TON CKT (28.15.50.1)`
- hex `CD 1Y - ZL • / FW NOT S (28.15.42.1)` --YES--> box `COND ICOB TO 1Y / 0-63 (28.44.16.1)`
- hex `CD 2Y - ZL• / FW NOT S (28.15.42.1)` --YES--> box `COND ICOB TO 2Y / 0 - 63 (28.44.16.1)`
- (end) hex `ZL IHW T • / ZR MT (28.15.41.1)` --YES-->
    - box `IHW RDY E1 (28.67.17.1)`
    - box `IHW RDY E2 (28.64.14.1)`

### Noted (Fig 3.1.15)
- Turn-on label `TON ZL MOD R`; `ZL MODIFY REQUIRED TGR (28.26.23.1)`; `SET MOD L TGR (28.26.23.1)`
- `SBC • 1YL MOD DEC • YL - ZLE (28.26.23.1)`
- `~(IMM IX 1YR) + FULL WD SC•1Y61 + 1Y60 + 1Y62 + 1Y63•DEC MOD REQ FR 1YR•UNCOND + BIT BR CL 1YR + BIT BR DEC• 1YRD•SBC•YR ZLE (28.26.23.1)` (rules as described above)
- `SBC • YR-ZLE • 1Y63 • DEC MOD REQ FR 1 YR • 1 YR BRC + UNCOND + BIT BR CL • BIT BR DEC 2 (28.26.23.1)`
- `NL IB MOD D • YL-ZLE • SBC (28.26.23.1)`
- `BLOCK WBC + DEC TON (28.15.80.1)`; `BLOCK ZR WAS IHW TOF (28.15.51.1)`; `BLOCK XF + DEC TON (28.15.50.1)`;
  `BLOCK YL-ZR TON (28.15.10.1)`; `BLOCK YR-ZR TON (28.15.60.1)`; `BLOCK GEN OF INSTR PREP COMPL ZL (28.15.32.1)`;
  `BLOCK GEN OF I CHK E • NM P • I CHK PAR (28.15.42.1)`
- `COND MOD ZL TON (28.15.40.1)` (twice); `TON XF + DEC (28.15.50.1)`; `Y - Z M MOD REQ (28.70.42.1)`
- `ZL + ZR PREP NOT BUSY (28. 20.21.1)`
- Turn-on label `TON MOD ZL`; `MODIFY ZL SEQUENCER (28.15.40.1)`; all five of its turn-on hexagons (quoted in (B) above; each
  contains `ZL MOD`/`MOD ZL`/`XF + DEC`)
- `TON MOD ZL M TGR WITH NEXT SBC (28.15.40.1)`
- `PX • FW NOT ST • XF + DEC ZLM + (28.15.42.1)`; `TON PX YL TGR (28.78.34.1)`
- `ZL FP CL • ~FW NOT ST + PROG IX (28.15.41.1)`; `ZL IHWT • FW ON BDS + PROG IX (28.15.41.1)`; `FWS + NOTS • FW ON BDS + PROG IX (28.15.41.1)`
- `COND IDC FR I PAR ERR PREP (28.99.03.1)`; `SET IDC ON IAUC ERR (28.51.01.1)`
- `MOD ZL M • CD 2Y - ZL (28.15.42.1)`; `MOD ZL M • CD 1Y - ZL (28.15.42.1)`; `~(MOD ZL) (28.15.42.1)`
- `Y - Z + MOD ZL CND ZL MA TAGS (28.51.01.1)`; `Y - Z L + MOD ZL • RST ZL TAGS (28.51.08.1)`
- `MOD ZLM • ZL FP CL (28.15.41.1)`; `FWS + NOTS • MOD ZL M (28.15.41.1)`; `ZL IHW • MOD ZL M (28.15.41.1)`
- `X 0-23 TO ABA• X 24-27 TO ABA (28.96.01.1)`
- `COND XF + DEC ZL M TON CKT (28.15.50.1)`; `TON 1 BIT MOD TGR (28.26.23.1)`
- `TOF YL - ZL M TGR (28.15.70.1)`; `TOF YR - ZL M TGR (28.15.30.1)`
- `HOLD DATA SELECT (27.09.07.1)`

===================================================================================================
# Not read with confidence

Fig 3.1.12 (p74)
- Printed date: first digit sits on a scan line ("2/1/62" assumed from the other sheets).
- Large turn-on hexagon of ZR FP1 TGR (28.26.50.1): placement of the six overbars (given line by line in the text) and the
  operators, several of which print as a blurred "+" / "÷" / "-".
- `LA EN TI +2` and `CHKR EN TI` in the hexagon `SAC • XOF 1M • ...` : "TI" vs "T1" not distinguishable; this hexagon's ALD
  "28.14.41.1" is printed without parentheses.
- 1 vs I throughout ("XOFI"/"XOF1", "ZR FPI TGR", "FP CL IYL", "CD IY-ZR", "DF MASK EQI").
- Top group: I list the three hexagons `YL-ZR E`, `MOD ZR E`, `MOD ZR E • MOD ZR M` as hanging from the line that joins the two
  `FP CL nYL` hexagons' YES exits; that is how the dots are drawn, but no arrowheads show direction.

Fig 3.1.13 sheet 1 (p75)
- `SET 7R FP 2` -- first letter prints as "7" (ZR?). No ALD printed for it.
- Small tick on the "F" of `FPR 4E • NM` and of `FPR 4E • FPR 4M` (overbar stub vs lettering artefact; sheet 2 shows the same
  tick on "FPR" inside plain action boxes, which argues for artefact).
- `(28.38.70.1)` under `BLOCK GEN OF ERR PRECND LA AD` -- 3/8 digits small.

Fig 3.1.13 sheet 2 (p76)
- Hexagon `~(FPR AD INHIB DF) DS. IRPT ENABLED. NOT ZR 0-31`: extent of the second-line bar (over "DF" only, or "DF DS").
- `ZR 1+2+3 . IRPT ENABLED`: marks above "1+2".
- `ZOAR EQ 11+12+16-31` has no ALD number printed (sheet 3's copy has 28.42.51.1).
- `TON PIRCY TRG` -- "PIRCY" smudged; "TRG" as printed (sheet 3 prints "TON PIRCY TGR").
- No "YES" is printed at the exits of `FPR 4E (28.14.42.1)`, `FPR4E.M`, `FPR 4E. SBC`, nor at the two turn-on hexagons.

Fig 3.1.13 sheet 3 (p77)
- Hexagon `~(FPR AD INHIB DF OR DS). NOT ZR 0-31. IRPT ENABLED`: extent of the second-line bar.
- Hexagon `ZR EXT LTH. ZR INSTR PREP COMPLETE. ~(FPDD M) . LAAR 1 BUSY (28.10.11.1)`: I see bars over "FPDD" and "M" only; the
  hexagon is tiny and the text touches its border, so a bar over "LAAR 1 BUSY" cannot be absolutely excluded.
- `CONDITION LA DF TAG` / `CONDITION LA NOP FR DF`: whether the `IRPT ENABLED .ZR1 + 2 + 3` YES line gates both.
- ALD first groups that print oddly: `FPR3E 24.14.32.1`; `FPR3E AND NO CANCEL. SBC 21.14.33.1`; `MODIFIED TYPE 3 LD TO LA 28.21.75.1`;
  `BLOCK TYPE 2 LOAD 28.14.31.1`; `I GEN PARITY 28.20.08.1`; `SET LAOP TAG 36.05.01.1`.
- The two hexagons feeding `TON FPR2E` (both 28.14.21.1): left edges under a scan streak -- "[ZR] INSTR PREP COMPL.",
  "[XOF] 1M+ ADR 8 LTH.", "[I?] CHKR EN T1. LA EN T1+2", "NO CHKR SINGLE ERROR"; and "ZR INSTR PREP COMPL / . ZR INT LTH. /
  [L]A EN T3. ~(FPR3E LTH) / . SAC".
- Direction of the line between box `ZR FP4 OR ZR FP6` and the ZR FP4 TGR junction (arrowhead only at the junction end).
- FP4 turn-on hexagon: "1Y24-1Y NOT 25" (dash vs period) and the cut-off last word "CL[R]".
- `I CHR REQ ZR` ("CHR" as printed).
- `ZR INSTR PREP .COMPLETE` (FP6): mark before "COMPLETE".

Fig 3.1.14 (p78)
- `YR-XL M (28.15.32.1)` as printed ("XL"); no YES printed at its exit.
- `SET HW RDY T` as printed.
- `SAC • MOD ZR M` and `YR - ZL E` have no ALD numbers.
- 1 vs I in `COND DEC I`, `COND ADD I`, `COND EMFI`, `COND LAMI`, `TON I EXP TGR`.

Fig 3.1.15 (p79)
- All horizontal rules inside hexagons other than the clear overbars over "IMM IX 1YR", "FW" (in `ZL FP CL • ~FW ...`) and
  "MOD ZL": hexagon A3 (under "DEC MOD", "REQ FR 1YR", "UNCOND", "BIT", "1YR"); hexagon B4 (between "NOT FW NOT S •" and
  "ZR WAS IHW"); `ZL FP CL • ~FW / NOT ST + PROG / IX`; `ZL IHWT • / FW ON BDS + / PROG IX`; `FWS + NOTS • / FW ON BDS + / PROG IX`.
- Which sequencer exit (E / E•M / M) owns the left and right groups: all three exits land on one unbroken horizontal line.
- `GT AOB 24 TO ZL` and the lower `GT AOB 18 TO ZL` / `GT AOB 19 TO ZL`: shared between two YES lines as drawn.
- `PREP GT Z0 - 23 TO ICIB` (last digit); `GT AOB 19 TO ZL` (prints "I9").
- `SBC • 1YL MOD DEC • YL - ZLE`: "1YL" could be "IYL".

Pages/tiles not finished: none (all of pp 74-79 covered; f75-R and f76-R are blank tiles).

# APPENDIX D -- reader transcription

# part_d — R23-9732 I UNIT FLOW DIAGRAMS, PDF pages 84, 85, 80, 82, 83, 81

Conventions: `~X` = overbar on X; `•` = AND dot; hex = hexagon (condition); box = rectangle (action).
"bus" = a drawn line with junction dots from which several hexes/boxes hang. Order of writing: 84, 85, 80, 82, 83, 81.
The "zoom-d-*" crops cited in the headers were temporary enlargements (200-300%) cut from the tiles / r-NN / p-0NN images; they have since been deleted.

Cross-figure differences in the STORE WAIT / STORE COMPARE gating, all AS PRINTED and each read at zoom (not slips):
- Fig 3.1.20 prints hex `ZOAR EQ 11 + 12 + 16 - 31 (28.42.51.1)`; Fig 3.1.21 prints hex `ZOAL EQ 11+12+16-31` 28.42.51.1.
- box `BLOCK STORE WAIT TGR TOF (28.42.51.1)` appears only in Fig 3.1.20; Fig 3.1.21 has `TON STORE WAIT TGR` and `TON 1RCY REQ TGR` under ZOAL EQ, no BLOCK box.
- Fig 3.1.20 prints a second hex `PROGRAM STORE COMPARE (28.42.72.1)` under FPL 4 E TGR ON; Fig 3.1.21 prints hex
  `PROGRAM STORE COMPARE .ACCEPT OR COMPARE` 28.42.72.1 under `FPL3E AND NO CANCEL` 28.13.33.1 instead; both lead to TON I RCY REQ TGR 28.42.72.1.
- `PROGRAM STORE COMPARE (28.42.71.1)` -> `TON PIRCY TGR (28.42.71.1)` is the same in both (3.1.21 adds `TON 1RCY REQ TGR` 28.42.72.1 on the same YES line).

---

## FIGURE 3.1.20. ZL FP3 TRIGGER — PDF page 84

- Caption as printed: "FIGURE 3.1.20. ZL FP3 TRIGGER"
- Page tag: 1-41/1-42. Date: 2/1/62. Margin: "M3-04-3", "I UNIT FLOW DIAGRAMS".
- Applicability note: "CPU 7101 SER. NO. 30,004 AND HIGHER"
- Tiles read: f84-T, f84-B, plus zooms zoom-d-84-*.

### Turn-on
- hex `SET ZL FP 3 (28.26.53.1)` --YES--+
- hex (3 text lines + ALD):
      `1Y53•1Y54•1Y55•1Y56`
      `~1Y57 + ~1Y55•1Y56•1Y57`
      `•COND FPCL`
      `(28.26.53.1)`  --YES--+
  (overbars seen: over the first "1Y57" at the start of line 2 and over "1Y55" in line 2; none seen in line 1.
   The leading character of each term reads "1Y"; it could be "IY" — the glyph is the same as digit 1.)
- both YES lines join at one dot --`TON`--> box/bar `ZL FP 3 TGR (28.26.53.1)`

### Outputs of ZL FP 3 TGR
One line leaves the bottom of the bar to a junction dot on a horizontal bus. From that bus (left to right):
far-left vertical bus (A), drop to hex "NOT IHW E...", vertical bus (B), drop to hex "ZL INSTR PREP COMPL•",
drop (centre) to hex "FPL 4 E TGR ON (28.13.43.1)", and a line up-and-right to hex "ZL EQ 1".
No E / EM / M output labels are printed on this bar.

- hex `ZL EQ 1 (28.23.20.1)` --YES--> box `PRE COND LA AD (28.25.20.1)`

#### Left column (first hex from the top bus; the rest hang from far-left vertical bus A by junction dots)
- hex `NOT IHW E • NOT ZL MOD R • YR - ZL M (28.15.32.1)` --YES-->
    - hex `FP Z ALT TGR ON (28.27.32.1)` --YES-->
        - box `FP RDY ZL TO LA CONT COMMON COM CKTS (28.20.21.1)`
        - box `COND FP INCOMPL TGR TON CKTS (28.42.53.1)`
- hex `MOD ZLE • ~FW ~NOT / ~ST + ~(PROG IX) (28.15.41.1)` --YES-->
  (printed on two lines: "MOD ZLE • FW NOT" / "ST + PROG IX"; separate overbar segments over FW, over NOT, over ST,
   and one over PROG IX; no overbar over MOD ZLE)
    - box `Z 0 - 17 ABB PREP (28.96.03.1)`
- hex `MOD ZLE (28.15.41.1)` --YES-->
    - box `HOT 1 TO ABB P 2 (28.96.41.1)`
- hex `MOD ZL E • MOD ZL M (28.15.41.1)` --YES-->
    - box `GT AOB 18 TO ZL (28.27.50.1)`
- hex `MOD ZL M (28.15.41.1)` --YES-->
    - box `INSTR PREP COMPL ZL (28.27.32.1)`   (a scan line runs through "INSTR PREP")
    - box `BLOCK MOD ZL M TGR TOF (28.15.40.1)`

#### Second column (first hex from the top bus; the rest hang from vertical bus B by junction dots)
- hex `ZL INSTR PREP COMPL• (28.13.41.1)` --YES-->   (a "•" is printed after COMPL with nothing following it)
    - box `COND FPL 4 TON CKT (28.13.41.1)`
- hex `FPL 4 E TGR ON (28.13.42.1)` --YES-->
    - box `Z 0 - 17 TO MAB (28.21.60.1)`
- hex `[uncertain: FPL 4 E? prints like "FDL 4 E"] • FPL 4 M (28.13.43.1)` --YES--> line X
  (this hex lies on the page fold; the top of its text is damaged, so any overbar over these terms could not be seen)
- hex `FPL 4 E • SBC (28.13.43.1)` --YES--> joins line X at a junction dot
    - line X (carrying the YES of both hexes above, as drawn) goes to:
        - box `L T3 LD E • M TO LA (38.03.01.1)`
        - box `L T3 LD E • M TO BCU (15.01.01.1)`
- hex `FPL 2 M + ZOAL INT FPL CL 3 + 1• ZL INSTR PREP COMPL (28.13.41.1)` --YES-->
  (printed lines: "FPL 2 M + ZOAL" / "INT FPL CL 3 + 1•" / "ZL INSTR PREP" / "COMPL")
    - box `COND FPL 4 TON CKT (28.13.41.1)`

#### Centre: FPL 4 E TGR ON
- hex `FPL 4 E TGR ON (28.13.43.1)` --YES--> junction dot; from it a vertical bus C (down) and a line right to hex "ZL EQ 1" (second one)
    - bus C:
        - hex `PROGRAM STORE COMPARE (28.42.71.1)` --YES-->
            - box `TON PIRCY TGR (28.42.71.1)`   [uncertain: "PIRCY" as one word; could be "P I RCY"]
        - hex `PROGRAM STORE COMPARE (28.42.72.1)` --YES-->
            - box `TON I RCY REQ TGR (28.42.72.1)`
        - hex `ZOAR EQ 11 + 12 + 16 - 31 (28.42.51.1)` --YES-->
            - box `TON STORE WAIT TGR (28.42.51.1)`
            - box `BLOCK STORE WAIT TGR TOF (28.42.51.1)`
            - box `TON I RCY REQ TGR (28.42.72.1)`
    - hex `ZL EQ 1 (28.23.20.1)` (a stray mark after the "1") --YES--> junction dot; from it vertical bus D (down) and a line right to hex "IF INHBT AD..."
        - bus D (nine boxes, each joined to the bus on its right side):
            - box `BLOCK GEN OF FPL 1 COND DF + DS (28.13.12.1)`
            - box `BLOCK GEN OF FPL 3 COND LA DF (28.13.33.1)`
            - box `BLOCK SETTING OF LA DS (28.25.20.1)`
            - box `BLOCK GEN OF DS SET LANOP (28.25.20.1)`
            - box `BLOCK GEN OF SET LA DF (28.25.30.1)`
            - box `BLOCK GEN OF DF SET LANOP (28.25.30.1)`
            - box `BLOCK GEN OF FPL 3 PRECND LA DF ( 28.23.11.1 )`
            - box `BLOCK GEN OF FPL 3 PRECND LANOP FR ALARM (28.23.11.1)`
            - box `BLOCK GEN OF FPL 4 PRECND LA DS NOP (28.23.11.1)`
        - hex `~(IF INHBT AD) • GT FPL IND TO LA (28.25.20.1)` --YES-->
          (overbar over "IF INHBT AD" only)
            - box `SET LA AD (33.01.05.1)`
            - the same YES line continues from the junction dot at SET LA AD down to the top of:
              hex `~(INHBT SET NOP) / ~(BIT FR AD + DF) (28.25.20.1)` --YES-->
              (two text lines, an overbar over each whole line)
                - box `AD SET LANOP (28.25.40.1)`

#### Bottom (far-left vertical bus A runs to the bottom and turns right into a horizontal bus E)
- from bus E, a vertical riser (junction dot) feeding two hexes:
    - hex `ZL EXT LTH •FPL 4E (28.24.82.1)` --YES--> box `SET LA EXT STORE TAG (28.24.82.1)`
      (a scan line runs through "•FPL 4E" and "STORE TAG"; both still legible)
    - hex `ZL INT LTH • FPL 4E (28.24.82.1)` --YES--> box `SET LA INT STORE TAG (28.24.82.1)`
- from bus E (junction dot):
    - hex `IRPT ENBLD • NOT ZL 16 - 31 • NOT ZL 0 - 15 • ~(FPL AD) ~(INHBT DF) ~(+ DS) (28.23.11.1)` --YES-->
      (printed lines: "IRPT ENBLD •" / "NOT ZL 16 - 31 •" / "NOT ZL 0 - 15 •" / "FPL AD INHBT DF" / "+ DS";
       overbar segments over "FPL AD", over "INHBT DF" and over "+ DS"; none over the first three lines)
        - hex `FPL 4 E • FPL 4 M (28.13.43.1)` --YES-->
            - box `COND LA DS FR ALARM (38.03.06.1)`
- from the right end of bus E:
    - hex `ZL 1 + 2 + 3 IRPT ENBLD (28.23.20.1)` --YES-->
        - hex `IF INHBT DS • GT FPL IND TO LA • FPL AD INHBT DF + DS (28.25.20.1)` --YES-->
          (printed lines: "IF INHBT DS •" / "GT FPL IND TO" / "LA • FPL AD" / "INHBT DF + DS"; NO overbar seen on any line of this hex)
            - box `SET LA DS (33.01.03.1)`
            - box `DS SET LANOP (28.25.40.1)`

### Noted (Fig 3.1.20)
- `SET LA EXT STORE TAG (28.24.82.1)` — gated by hex `ZL EXT LTH •FPL 4E (28.24.82.1)`
- `SET LA INT STORE TAG (28.24.82.1)` — gated by hex `ZL INT LTH • FPL 4E (28.24.82.1)`
- `PROGRAM STORE COMPARE (28.42.71.1)` -> `TON PIRCY TGR (28.42.71.1)`
- `PROGRAM STORE COMPARE (28.42.72.1)` -> `TON I RCY REQ TGR (28.42.72.1)`
- `ZOAR EQ 11 + 12 + 16 - 31 (28.42.51.1)` -> `TON STORE WAIT TGR (28.42.51.1)`, `BLOCK STORE WAIT TGR TOF (28.42.51.1)`, `TON I RCY REQ TGR (28.42.72.1)`
- `MOD ZLE • ~FW ~NOT ~ST + ~(PROG IX) (28.15.41.1)`; `MOD ZLE (28.15.41.1)`; `MOD ZL E • MOD ZL M (28.15.41.1)`; `MOD ZL M (28.15.41.1)`; `NOT IHW E • NOT ZL MOD R • YR - ZL M (28.15.32.1)`
- `BLOCK MOD ZL M TGR TOF (28.15.40.1)`
- `PRE COND LA AD (28.25.20.1)`; `SET LA AD (33.01.05.1)`; `AD SET LANOP (28.25.40.1)`; `SET LA DS (33.01.03.1)`; `DS SET LANOP (28.25.40.1)`; `COND LA DS FR ALARM (38.03.06.1)`
- `L T3 LD E • M TO LA (38.03.01.1)`; `L T3 LD E • M TO BCU (15.01.01.1)`; `FP RDY ZL TO LA CONT COMMON COM CKTS (28.20.21.1)`
- `~(IF INHBT AD) • GT FPL IND TO LA (28.25.20.1)`; `IF INHBT DS • GT FPL IND TO LA • FPL AD INHBT DF + DS (28.25.20.1)`; `~(INHBT SET NOP) ~(BIT FR AD + DF) (28.25.20.1)`
- `IRPT ENBLD • NOT ZL 16 - 31 • NOT ZL 0 - 15 • ~(FPL AD) ~(INHBT DF) ~(+ DS) (28.23.11.1)`; `ZL 1 + 2 + 3 IRPT ENBLD (28.23.20.1)`
- `BLOCK GEN OF FPL 1 COND DF + DS (28.13.12.1)`; `BLOCK GEN OF FPL 3 COND LA DF (28.13.33.1)`; `BLOCK SETTING OF LA DS (28.25.20.1)`; `BLOCK GEN OF DS SET LANOP (28.25.20.1)`; `BLOCK GEN OF SET LA DF (28.25.30.1)`; `BLOCK GEN OF DF SET LANOP (28.25.30.1)`; `BLOCK GEN OF FPL 3 PRECND LA DF ( 28.23.11.1 )`; `BLOCK GEN OF FPL 3 PRECND LANOP FR ALARM (28.23.11.1)`; `BLOCK GEN OF FPL 4 PRECND LA DS NOP (28.23.11.1)` — all nine gated by the second hex `ZL EQ 1 (28.23.20.1)` after `FPL 4 E TGR ON (28.13.43.1)`
- No printed times or counts on this page.

---

## FIGURE 3.1.21. ZL FP4 TRIGGER AND ZL FP6 TRIGGER — PDF page 85 (landscape)

- Caption as printed: "FIGURE 3.1.21. ZL FP4 TRIGGER AND" / "ZL FP6 TRIGGER"
- Page tag: 1-43/1-44. Date: 2/1/62. Margin: "M3-04-3", "I UNIT FLOW DIAGRAMS".
- Applicability note: none seen on the page.
- Tiles read: f85-L, f85-M, f85-R, plus zooms zoom-d-85-1..10.
- Drawing style differs from Fig 3.1.20: the ALD number is printed BELOW each box/hex without parentheses,
  the AND is printed as a period "." (transcribed here as printed, "."), and lines carry arrowheads.
  No E / EM / M output labels are printed on either trigger box.

### A. ZL FP4 TGR — turn-on
- box `SET ZL FP 4` 28.26.53.1 --+
- hex `~1Y53. ~1Y55 / .1Y56. ~1Y57 / .COND FP CL` 28.26.53.1 --+
  (three text lines; overbars seen over "1Y53", over "1Y55" and over "1Y57"; none over "1Y56". "1Y" may be "IY".)
- the two lines meet (arrowheads) --`TON`--> box `ZL FP4 TGR` 28.26.53.1

### A. ZL FP4 TGR — outputs
The output line leaves the bottom of ZL FP4 TGR. Immediately below it a horizontal line runs LEFT to the
left column (A1) and RIGHT to the "ZL FP4 OR ZL FP6" area (A3). The line also continues straight down as the main column (A2).

#### A1. left column (vertical bus, arrowheads downward)
- hex `ZL1 + 2 + 3 . IRPT ENABLED` 28.23.20.1 --YES--> box `PRE CND LA DS` 28.25.20.1
- hex `ZL EQ 1` 28.23.20.1 --YES--> box `PRE COND LA AD` 28.25.20.1
- hex `IRPT ENABLED .NOT ZL0-15` 28.23.11.1 --YES-->
    - box `PRE CND LA DS` 28.13.33.1
    - box `PRE CND LA NOP FR ALARM` 28.13.33.1
- hex `ZL INT + ZL ADR 8.FPL4E` 28.24.82.1 --YES--> box `SET LA INT STORE TAG` 28.24.82.1
  (printed lines: "ZL INT +" / "ZL ADR" / "8.FPL4E")
- the bus ends in the top of hex `ZL NE LTHD` 28.23.10.1 --YES--> (line to the right), from which:
    - box `COND FPL4E TON` 28.13.41.1  (straight on, no further condition)
    - hex `FPL4E.M` 28.13.43.1 --YES--> line X1
    - hex `FPL4E . SBC` 28.13.43.1 --YES--> joins line X1 (arrowhead into it)
        - line X1 goes to: box `TYPE 3 LOAD TO LA` 28.21.74.1 ; box `TYPE 3 LOAD TO BCU` 28.21.74.1
    - hex `FPL4E` 28.13.42.1 --YES--> box `Z0-17 TO MAB` 28.21.60.1

#### A2. main column under ZL FP4 TGR (vertical bus, arrowheads downward)
- box `BLOCK CND LA DF` 28.13.33.1  (direct, no hex)
- hex `FPL3E AND NO CANCEL. SBC` 28.13.33.1 --YES--> line X2
- hex `FPL3E AND NO CANCEL. FPL3M` 28.13.33.1 --YES--> joins line X2 (arrowhead into it)
    - line X2 goes to:
        - box `TYPE 3 LOAD TO LA` 28.21.74.1
        - box `T3LD TO BCU WAIT FOR ACCEPT` 28.21.74.1   (two lines: "T3LD TO BCU" / "WAIT FOR ACCEPT")
- hex `FPL3NM .ALLOW LAST LOAD` 28.23.00.1 --YES--> box `COND FPL 3E TON` 28.13.31.1
- the bus ends in the top of hex `FPL4E` (NO ALD number printed under this hex) --YES--> line that splits to:
    - hex `ZOAL EQ 11+12+16-31` 28.42.51.1 --YES-->
        - box `TON STORE WAIT TGR` 28.42.51.1
        - box `TON 1RCY REQ TGR` 28.42.72.1   (prints "1RCY", i.e. I RCY with no space)
    - hex `PROGRAM STORE COMPARE` 28.42.71.1 --YES-->
        - box `TON P1RCY TGR` 28.42.71.1   (prints "PIRCY"/"P1RCY" as one word)
        - box `TON 1RCY REQ TGR` 28.42.72.1

#### A3. to the right of ZL FP4 TGR
The horizontal line from the ZL FP4 TGR output runs right to a vertical; that vertical goes UP into the left side
of box "ZL FP4 OR ZL FP6" (section C) and DOWN into:
- hex `FPL3E AND NO CANCEL` 28.13.33.1 --YES (exit on the LEFT side)-->
    - hex `PROGRAM STORE COMPARE .ACCEPT OR COMPARE` 28.42.72.1 --YES-->
      (printed lines: "PROGRAM" / "STORE COMPARE" / ".ACCEPT OR" / "COMPARE")
        - box `TON IRCY REQ TGR` 28.42.72.1

### B. ZL FP6 TGR — turn-on
- box `SET ZL FP6` 28.26.53.1 --+
- hex `1Y53.1Y NOT / 54.1Y55.1Y56. / 1Y57.COND / FP CL` 28.26.53.1 --+
  (four text lines exactly as broken; no overbars seen; the word NOT is printed between "1Y" and "54")
- the two lines meet (arrowheads) --`TON`--> box `ZL FP6 TGR` (no ALD number printed under this box)

### B. ZL FP6 TGR — outputs
Output line leaves the bottom of ZL FP6 TGR. Just below, a horizontal line crosses it: to the RIGHT it feeds the hex
"IRPT ENABLED .ZL1 + 2 + 3"; to the LEFT it feeds (arrowhead) hex "FPL4E" 28.24.82.1, and continues left, then up,
then left along the top of the page, feeding hex "ZL NE LTHD" (second one) and ending (arrowhead) in the RIGHT side of
box "ZL FP4 OR ZL FP6" (section C). The line also continues straight down as the FP6 main column.

#### B1. right of the cross line
- hex `IRPT ENABLED .ZL1 + 2 + 3` 28.23.20.1 --YES-->
    - box `COND LA DF` 28.25.30.1
    - box `COND LA NOP FROM DF` 28.25.30.1

#### B2. FP6 main column (vertical bus, arrowheads downward)
- box `COND FPDDE TON` 28.10.11.1  (direct, no hex) [uncertain: "FPDDE" — letters read F P D D E]
- hex `FPL3E AND NO. CANCEL. FPL3M` 28.13.33.1 --YES--> line X3   (a period is printed after "NO" in this hex)
- hex `FPL3E AND NO CANCEL. SBC` 28.13.33.1 --YES--> joins line X3 (arrowhead into it)
    - line X3 goes to: box `TYPE 3 LOAD TO LA` 28.21.74.1
- hex `FPL4E` 28.13.42.1 --YES--> box `SET ADR 13 ON MAB` 28.21.10.1
- the bus ends in the top of hex `~(FPL ADINHIB DF) / ~DS. IRPT / ENABLED. NOT / ZL0-31` 28.23.11.1 --YES-->
  (four text lines; an overbar over the whole first line "FPL ADINHIB DF" and an overbar over "DS" on the second line;
   none over the rest)
    - box `PRE COND LA DF` 28.13.33.1
    - hex `DF MASK ONE` 28.23.11.1 --YES (exit on the LEFT side)--> box `PRE COND LA NOP FR ALARM` 28.13.33.1

#### B3. left of the cross line
- hex `FPL4E` 28.24.82.1 --YES--> box `SET LA EXT STORE TAG` 36.09.14.1
- hex `ZL NE LTHD` 28.23.10.1 --YES (exit on the LEFT side)--> vertical bus:
    - box `COND FPL4E TON` 28.14.41.1   (printed 28.14.41.1 here; the corresponding box in A1 is printed 28.13.41.1)
    - hex `FPL4E.M` 28.13.43.1 --YES--> line X4
    - hex `FPL4E. SBC` 28.13.43.1 --YES--> joins line X4 (arrowhead into it)
        - line X4 goes to: box `TYPE 3 LOAD TO LA` 28.21.74.1 ; box `TYPE 3 LOAD TO BCU` 28.21.74.1
  (the page fold runs through the right edge of these hexes/boxes; text still legible)

### C. box `ZL FP4 OR ZL FP6` 28.23.00.1
Inputs: from the left, the ZL FP4 TGR output line (A3); from the right, the ZL FP6 TGR output line (B).
Output: bottom of the box to a horizontal bus feeding two vertical columns C1 (left) and C2 (right).

#### C1. left column (arrowheads downward)
- hex `FPL3E AND NO CANCEL` 28.24.82.1 --YES--> box `SET LA EXT STORE TAG` 28.24.82.1
- hex `FPL4E` 28.24.80.1 --YES-->
    - box `SET LAOC 6, 8, & 9` with TWO numbers printed below: 28.24.24.1 and 28.24.26.1
    - box `SET LAOP TAG` 36.05.01.1
- box `COND FPL2E TON` 28.13.21.1  (direct, no hex)
- hex `FPL3E AND NO CANCEL. SBC` 28.13.33.1 --YES--> box `MODIFIED TYPE 3 LOAD TO LA` 28.21.75.1
- hex `FPL3E AND NO CANCEL. FPL3M` 28.13.33.1 --YES-->
    - box `XFER & RESET NIDC` 28.21.73.1
    - box `MODIFIED TYPE 3 LOAD TO LA` 28.21.75.1
- hex `ZL ADR 8` 28.20.08.1 --YES-->
    - box `I CHKR REQ` 28.27.32.1
    - box `BLOCK ZL XS LTH SIGNAL` 28.20.41.1
- box `COND XOF I E TON` 28.12.11.1  (direct, no hex)
- the column then runs along the bottom, right, and up into the top of:
  hex `ZR INSTR PREP COMPLETE .ZR EQ1. XOF1E` 28.12.12.1 --YES--> box `XOF 1 TC FETCH` 24.00.09.1
  (printed lines: "ZR INSTR" / "PREP COMPLETE" / ".ZR EQ1." / "XOF1E"; "XOF1E" prints crowded, like "XOFIE")
  ("XOF 1 TC FETCH": [uncertain: "1 TC" could be "I TC"]; its number reads 24.00.09.1)

#### C2. right column (arrowheads downward)
- hex `ZL ADR 8 LTH .FPR2E` 28.24.82.1 --YES-->   [uncertain: ".FPR2E" — third letter reads R, not L]
    - box `SET LA EXT STORE TAG` 36.09.14.1
    - box `SET LA INT STORE TAG` 36.09.15.1
- hex `ZL ADDR 8 LTH .FPL2 E.NM` 28.13.22.1 --YES--> box `I GEN PARITY` 28.44.14.1
  (printed lines: "ZL ADDR" / "8 LTH" / ".FPL2" / "E.NM")
- hex `NOT IC FETCH PRIORITY` 28.20.23.1 --YES--> box `COND FPL2E TON` 28.13.21.1
- box `BLOCK TYPE 2 LD TO LA` 28.13.33.1  (direct, no hex)
- hex `FPL3E` 28.13.32.1 --YES-->
    - box `ZO-17 TO MAB` 28.21.60.1   (prints letter-like "O" after Z)
    - box `GT ZLOC TO LAOC` 28.21.60.1   (first two digits of the number overprinted/smudged: [uncertain: 28?])
- the column then runs down, right, and up into a further vertical bus C3:

#### C3. continuation bus (right-hand part of the page, left of the FP6 area)
- hex `FPL3E AND NO CANCEL. FPL3M. MNT MD ZL4` 28.13.33.1 --YES--> box `PANEL KEY REQUEST` 28.21.71.1
  (printed lines: "FPL3E AND" / "NO CANCEL." / "FPL3M. MNT" / "MD ZL4"; the page fold line runs through the right
   edge of this hex and through the last digit of both ALD numbers — [uncertain: final ".1" of each])
- hex `ZL ADR 8 LTH` 28.20.30.1 --YES--> box `BLOCK ZL EXT OR ZL XS SIGNALS` 28.20.30.1
  (fold line through the last digit of both numbers — [uncertain: final ".1"])
- hex `FPL4E` 28.13.42.1 --YES--> box `BLOCK XFER OF ZLOC TO LAOC` 28.13.42.1
- the bus then runs along the bottom, right, and up into the top of:
  hex `ZR INSTR PREP COMPLETE .ZR NOT EQ1 .XOF 1E` 28.12.12.1 --YES--> box `Z13-17.P TO XAB` 28.86.56.1
  ([uncertain: 28.86.56.1 — second group could be 86 or 96])

### Noted (Fig 3.1.21)
- `SET LA INT STORE TAG` 28.24.82.1 — gated by `ZL INT + ZL ADR 8.FPL4E` 28.24.82.1 (under ZL FP4 TGR)
- `SET LA EXT STORE TAG` 36.09.14.1 — gated by `FPL4E` 28.24.82.1 (under ZL FP6 TGR)
- `SET LA EXT STORE TAG` 28.24.82.1 — gated by `FPL3E AND NO CANCEL` 28.24.82.1 (under ZL FP4 OR ZL FP6)
- `SET LA EXT STORE TAG` 36.09.14.1 and `SET LA INT STORE TAG` 36.09.15.1 — gated by `ZL ADR 8 LTH .FPR2E` 28.24.82.1 (under ZL FP4 OR ZL FP6)
- `TON STORE WAIT TGR` 28.42.51.1 and `TON 1RCY REQ TGR` 28.42.72.1 — gated by `ZOAL EQ 11+12+16-31` 28.42.51.1, itself after `FPL4E` YES (under ZL FP4 TGR)
- `PROGRAM STORE COMPARE` 28.42.71.1 -> `TON P1RCY TGR` 28.42.71.1, `TON 1RCY REQ TGR` 28.42.72.1 (after `FPL4E` YES, under ZL FP4 TGR)
- `FPL3E AND NO CANCEL` 28.13.33.1 -> `PROGRAM STORE COMPARE .ACCEPT OR COMPARE` 28.42.72.1 -> `TON IRCY REQ TGR` 28.42.72.1
- `T3LD TO BCU WAIT FOR ACCEPT` 28.21.74.1 — on the joined YES line of `FPL3E AND NO CANCEL. SBC` 28.13.33.1 and `FPL3E AND NO CANCEL. FPL3M` 28.13.33.1 (under ZL FP4 TGR)
- `BLOCK CND LA DF` 28.13.33.1; `BLOCK TYPE 2 LD TO LA` 28.13.33.1; `BLOCK ZL XS LTH SIGNAL` 28.20.41.1; `BLOCK ZL EXT OR ZL XS SIGNALS` 28.20.30.1; `BLOCK XFER OF ZLOC TO LAOC` 28.13.42.1
- `SET LAOC 6, 8, & 9` 28.24.24.1 / 28.24.26.1; `SET LAOP TAG` 36.05.01.1; `GT ZLOC TO LAOC` 28.21.60.1
- `COND LA NOP FROM DF` 28.25.30.1; `PRE CND LA NOP FR ALARM` 28.13.33.1; `PRE COND LA NOP FR ALARM` 28.13.33.1
- `COND XOF I E TON` 28.12.11.1; `ZR INSTR PREP COMPLETE .ZR EQ1. XOF1E` 28.12.12.1; `XOF 1 TC FETCH` 24.00.09.1; `ZR INSTR PREP COMPLETE .ZR NOT EQ1 .XOF 1E` 28.12.12.1; `Z13-17.P TO XAB` 28.86.56.1
- `MODIFIED TYPE 3 LOAD TO LA` 28.21.75.1 (twice); `TYPE 3 LOAD TO LA` 28.21.74.1 (four times); `TYPE 3 LOAD TO BCU` 28.21.74.1 (twice)
- `IRPT ENABLED .NOT ZL0-15` 28.23.11.1; `ZL1 + 2 + 3 . IRPT ENABLED` 28.23.20.1; `IRPT ENABLED .ZL1 + 2 + 3` 28.23.20.1; `~(FPL ADINHIB DF) ~DS. IRPT ENABLED. NOT ZL0-31` 28.23.11.1
- `NOT IC FETCH PRIORITY` 28.20.23.1; `XFER & RESET NIDC` 28.21.73.1; `PANEL KEY REQUEST` 28.21.71.1; `FPL3NM .ALLOW LAST LOAD` 28.23.00.1
- No printed times or counts on this page.

---

## FIGURE 3.1.16. ZL BLOCK AND SUSPEND TRIGGERS — PDF page 80

- Caption as printed: "FIGURE 3.1.16. ZL BLOCK AND" / "SUSPEND TRIGGERS"
- Page tag: 1-33/1-34. Date: 2/1/62. Margin: "M3-04-3", "I UNIT FLOW DIAGRAMS".
- Applicability note: "CPU 7101 SER. NO. 30,004 AND HIGHER"
- Tiles read: f80-T, f80-B, plus zooms zoom-d-80-*.
- Four separate triggers on the page. No E / EM / M output labels are printed on any of them; each trigger's
  output is one vertical bus with action boxes attached left and right at junction dots. No condition hexes
  below the triggers except the last one under ZL SPND 2Y TGR.

### 1. ZL BLOCK 1Y TGR (upper left)
- hex `INSTR PREP TON ZL BLOCK 1Y • SBC (28.42.41.1)` --YES--`TON`--> box `ZL BLOCK 1Y TGR (28.42.41.1)`
- output bus:
    - (left)  box `BLOCK GEN OF 1Y NOT BUSY (28.42.12.1)`
    - (right) box `BLOCK GEN OF 1Y NOT BUSY ANTIC ON ACC (28.42.12.1)`
    - (left)  box `BLOCK ESTABL OF IC FTH PRIORITY (28.42.12.1)`
    - (right) box `BLOCK GEN OF I EX USE 1Y (28.42.12.1)`
    - (left, at the end of the bus) box `BLOCK GEN OF IY NOT BUSY ANTIC (28.42.12.1)`  (prints "IY" here, "1Y" in the others)

### 2. ZL BLOCK 2Y TGR (upper right)
- hex `INSTR PREP ZL BLOCK 2Y • SBC (28.42.41.1)` --YES--`TON`--> box `ZL BLOCK 2Y TGR (28.42.41.1)`
  (this hex has no word "TON" inside it, unlike the 1Y one)
- output bus:
    - (left)  box `BLOCK GEN OF 2Y NOT BUSY (28.42.12.1)`
    - (right) box `BLOCK GEN OF 2Y NOT BUSY ANTIC (28.42.12.1)`
    - (left)  box `BLOCK ESTAB OF IC FTH PRIORITY (28.42.12.1)`
    - (right) box `BLOCK GEN OF 2Y NOT BUSY ANTIC ON ACC (28.42.12.1)`
    - (right, at the end of the bus) box `BLOCK BR CKT IF2Y TON (28.41.31.1)`

### 3. ZL SPND 1Y TGR (lower left)
Turn-on: three hexes whose YES lines join one horizontal line (junction dots) --`TON`--> box `ZL SPND 1Y TGR (28.42.42.1)`
- hex `IWC2 • ICOR NE • 2Y RD BRU + BRC • NO CHKR SING ERR • SAR (28.42.42.1)`
  (printed lines: "IWC2 • ICOR" / "NE • 2Y RD BRU +" / "BRC • NO CHKR SING" / "ERR • SAR"; no overbars seen, but the
   first line touches the hex's top border, so an overbar there could not be excluded)
- hex `SBC • BR Y-Z XFER TON ZL SPND 1Y (28.42.42.1)`
- hex `E1 TON SPND TGRS • SBC (28.42.42.1)`
Output bus (pairs listed top to bottom, left box / right box):
- box `BLOCK GEN OF IF1Y ONE TO MAB 15 (28.41.22.1)` / box `BLOCK GEN OF IF1Y FTH REQ (28.41.22.1)`
- box `BLOCK GEN OF IF1Y GT ICA O-16 TO MAB (28.41.22.1)` / box `BLOCK GEN OF IF1Y PNL KEY REQ (28.41.22.1)`
- box `BLOCK GEN OF IF1Y GT ICA O-16 TO MAB (28.41.22.1)` / box `BLOCK IF1Y TOF (28.41.21.1)`
  (this left box prints the same text as the one above it — both read "ICA"; in this one the "O" of "O-16" has a dot
   in its centre. [uncertain: one of the two may be intended as ICR — on the 2Y side the corresponding pair is ICR / ICA —
   but both print as ICA])
- box `COND IF2Y ANTIC TON CKT (28.41.31.1)` / box `BLOCK ICOF 1Y TON (28.41.23.1)`
- box `BLOCK ESTAB OF IC FTH PRIORITY (28.42.12.1)` / box `BLOCK ICBC1Y TON (28.41.23.1)`
  (a scan/fold line strikes through the first text line of both boxes: "BLOCK ESTAB OF IC" and "BLOCK ICBC1Y" —
   [uncertain: ICBC1Y], read through the line)
- box `BLOCK IF1Y IND TOF (28.41.22.1)` / box `BLOCK IWC1 TON (28.41.51.1)`
- box `BLOCK GEN OF IF1Y RETURN ADR (28.41.22.1)` (left, at the end of the bus; no right partner)

### 4. ZL SPND 2Y TGR (lower right)
Turn-on: three hexes whose YES lines join one horizontal line --`TON`--> box `ZL SPND 2Y TGR (28.42.43.1)`
- hex `IWCIE • ICOR NE o 1YRD BRU + BRC • NO CHKR SING ERR • SAR (28.42.43.1)`
  (printed lines: "IWCIE • ICOR" / "NE o 1YRD BRU" / "+ BRC • NO CHKR" / "SING ERR • SAR"; "IWCIE" [uncertain: IWC1E];
   the dot after NE is printed hollow; no overbars seen, first line touches the top border as above)
- hex `SBC • BR Y-Z XFER TON ZL SPND 2Y (28.42.43.1)`
- hex `E1 TON 2Y SPND TGR • SBC (28.42.42.1)`   (number printed 28.42.42.1, not .43)
Output bus (pairs top to bottom, left box / right box):
- box `BLOCK GEN OF IC FTH M • IC FTH MEM (28.41.21.1)` / box `BLOCK ESTAB OF IC FTH PRIORITY (28.42.12.1)`
- box `BLOCK ICADV E2 TON (28.41.41.1)` / box `BLOCK IF2Y FTH REQ (28.41.32.1)`
- box `BLOCK GEN OF IF2Y ONE TO MAB 15 (28.41.32.1)` / box `BLOCK IF2Y PNL KEY REQ (28.41.32.1)`
- box `BLOCK GEN OF IF2Y GT ICR 0-16 TO MAB (28.41.32.1)` / box `BLOCK IF2Y TOF (28.41.31.1)`
- box `BLOCK GEN OF IF2Y GT ICA 0-16 TO MAB (28.41.32.1)` / box `BLOCK ICFO2Y TON (28.41.33.1)`
  (scan/fold line strikes through "BLOCK GEN OF IF2Y"; "ICFO2Y" as printed — the 1Y counterpart prints "ICOF 1Y")
- box `BLOCK IF2Y IND TOF (28.42.32.1)` / box `BLOCK ICBC2Y TON (28.41.33.1)`
  (28.42.32.1 re-read at 200%: prints 42 clearly; the neighbouring IF2Y boxes are 28.41.32.1 — as printed)
- box `BLOCK GEN OF IF2Y RETURN ADR (28.41.32.1)` / box `BLOCK ICADV E1 TOF (28.41.41.1)`
- box `BLOCK IF1Y E TON (28.41.21.1)` / box `BLOCK IWC2 TON (28.41.61.1)`
- the bus ends in the top of hex `IF2Y M (28.41.32.1)` --YES--> box `COND ICADY E2 TON (28.41.41.1)`
  ("ICADY" re-read at 300%: prints Y clearly; the boxes above print "ICADV" — as printed)

### Noted (Fig 3.1.16)
- ZL BLOCK 1Y TGR: `BLOCK GEN OF 1Y NOT BUSY (28.42.12.1)`; `BLOCK GEN OF 1Y NOT BUSY ANTIC ON ACC (28.42.12.1)`; `BLOCK ESTABL OF IC FTH PRIORITY (28.42.12.1)`; `BLOCK GEN OF I EX USE 1Y (28.42.12.1)`; `BLOCK GEN OF IY NOT BUSY ANTIC (28.42.12.1)`
- ZL BLOCK 2Y TGR: `BLOCK GEN OF 2Y NOT BUSY (28.42.12.1)`; `BLOCK GEN OF 2Y NOT BUSY ANTIC (28.42.12.1)`; `BLOCK ESTAB OF IC FTH PRIORITY (28.42.12.1)`; `BLOCK GEN OF 2Y NOT BUSY ANTIC ON ACC (28.42.12.1)`
- ZL SPND 1Y TGR: `BLOCK GEN OF IF1Y ONE TO MAB 15 (28.41.22.1)`; `BLOCK GEN OF IF1Y FTH REQ (28.41.22.1)`; `BLOCK GEN OF IF1Y GT ICA O-16 TO MAB (28.41.22.1)` (twice); `BLOCK GEN OF IF1Y PNL KEY REQ (28.41.22.1)`; `BLOCK IF1Y TOF (28.41.21.1)`; `BLOCK ICOF 1Y TON (28.41.23.1)`; `BLOCK ESTAB OF IC FTH PRIORITY (28.42.12.1)`; `BLOCK ICBC1Y TON (28.41.23.1)`; `BLOCK IWC1 TON (28.41.51.1)`; `BLOCK GEN OF IF1Y RETURN ADR (28.41.22.1)`
- ZL SPND 2Y TGR: `BLOCK GEN OF IC FTH M • IC FTH MEM (28.41.21.1)`; `BLOCK ESTAB OF IC FTH PRIORITY (28.42.12.1)`; `BLOCK ICADV E2 TON (28.41.41.1)`; `BLOCK IF2Y FTH REQ (28.41.32.1)`; `BLOCK GEN OF IF2Y ONE TO MAB 15 (28.41.32.1)`; `BLOCK IF2Y PNL KEY REQ (28.41.32.1)`; `BLOCK GEN OF IF2Y GT ICR 0-16 TO MAB (28.41.32.1)`; `BLOCK IF2Y TOF (28.41.31.1)`; `BLOCK GEN OF IF2Y GT ICA 0-16 TO MAB (28.41.32.1)`; `BLOCK ICFO2Y TON (28.41.33.1)`; `BLOCK ICBC2Y TON (28.41.33.1)`; `BLOCK GEN OF IF2Y RETURN ADR (28.41.32.1)`; `BLOCK ICADV E1 TOF (28.41.41.1)`; `BLOCK IF1Y E TON (28.41.21.1)`; `BLOCK IWC2 TON (28.41.61.1)`
- `ZL SPND 1Y TGR (28.42.42.1)`, `ZL SPND 2Y TGR (28.42.43.1)` and their turn-on hexes:
  `IWC2 • ICOR NE • 2Y RD BRU + BRC • NO CHKR SING ERR • SAR (28.42.42.1)`; `SBC • BR Y-Z XFER TON ZL SPND 1Y (28.42.42.1)`;
  `E1 TON SPND TGRS • SBC (28.42.42.1)`; `IWCIE • ICOR NE o 1YRD BRU + BRC • NO CHKR SING ERR • SAR (28.42.43.1)`;
  `SBC • BR Y-Z XFER TON ZL SPND 2Y (28.42.43.1)`; `E1 TON 2Y SPND TGR • SBC (28.42.42.1)`
- `ZL BLOCK 1Y TGR (28.42.41.1)` <- `INSTR PREP TON ZL BLOCK 1Y • SBC (28.42.41.1)`; `ZL BLOCK 2Y TGR (28.42.41.1)` <- `INSTR PREP ZL BLOCK 2Y • SBC (28.42.41.1)`
- `BLOCK BR CKT IF2Y TON (28.41.31.1)`
- `BLOCK IF1Y IND TOF (28.41.22.1)`; `BLOCK IF2Y IND TOF (28.42.32.1)`
- No STORE TAG / STORE WAIT / COMPARE / WAIT FOR ACCEPT box appears on this page. No printed times or counts.

---

## FIGURE 3.1.18. ZL FL PT TRIGGER AND ZL FP 1 TRIGGER — PDF page 82

- Caption as printed: "FIGURE 3.1.18. ZL FL PT TRIGGER AND" / "ZL FP 1 TRIGGER"
- Page tag: 1-37/1-38. Date: 2/1/62 (both read from the left margin of r-82.png; the tiles cut them off). Margin: "M3-04-3", "I UNIT FLOW DIAGRAMS" (checked on r-82.png).
- Applicability note: "CPU 7101 SER. NO. 30,004 AND HIGHER"
- Tiles read: f82-T, f82-B, plus zooms zoom-d-82-*.
- No E / EM / M output labels are printed on either trigger box.

### A. ZL FL PT TGR
- hex `CD IY-ZL•NOT HW CL IY • YR-ZL + CD 2Y-ZL • YR-ZL 2Y • NO HW CL 2Y (28.26.62.1)`
  (printed lines: "CD IY-ZL•NOT" / "HW CL IY • YR-ZL +" / "CD 2Y-ZL • YR-ZL 2Y •" / "NO HW CL 2Y"; no overbars seen;
   no YES and no TON label is printed on its exit line)
  --> box `ZL FL PT TGR (28.26.62.1)`
- output (one junction dot below the box, three boxes hang from it):
    - box `COND FP Z ALT TGR TON (28.27.32.1)`
    - box `TOF ZR WAS IHW TGR (28.15.51.1)`
    - box `COND XF + DEC ZL TON CKT (28.15.50.1)`

### B. ZL FPI TGR — turn-on   (the box and the SET hex print "FPI"; the caption prints "FP 1")
- hex `SET ZL FPI (28.26.52.1)` --YES--+
- large hex, nine text lines + ALD, --YES--+ :
      `~1Y53•1Y55•1Y57 +`
      `~1Y53•~1Y56•~1Y57 +`
      `~1Y54•~1Y56•~1Y57 +`
      `1Y53•~1Y54•1Y56•`
      `~1Y57 + ~1Y55•~1Y56 +`
      `MULT AND ADD +`
      `~1Y54•1Y55•~1Y57`
      `•FPCL1YR•SBC•CD1Y`
      `ZL•YR - ZLE`
      `(28.26.52.1)`
  [uncertain: the overbars in this hex. The lines are set so tightly that a bar could belong to the term below it or be
   read as an underline of the term above. Best reading is as written above (a bar directly over each term marked `~`).
   In addition a short bar is printed directly above the word "MULT" in line 6 — [uncertain: overbar on MULT, or stray].
   "1Y" may be "IY" throughout.]
- both YES lines join at a dot --`TON`--> box `ZL FPI TGR (28.26.52.1)`

### B. ZL FPI TGR — outputs
One line from the bottom of the box to a junction dot on a long horizontal bus. From that bus, left to right:
far-left vertical bus (L), drop to hex "NOT IHW E...", vertical bus (M), drop to hex "FPL 3 E TGR ON", vertical line (N),
drop to hex "FPL AD INNIB...", vertical bus (P) which runs both UP and DOWN from the horizontal bus, and at the right end
a drop to hex "IRPT EN • ZL 1 + 2 + 3".

#### B1. left column (first hex from the horizontal bus; the rest hang from bus L)
- hex `NOT IHW E • NOT ZL MOD R • YR-ZL M (28.15.32.1)` --YES-->
    - hex `FP Z ALT TGR ON (28.27.32.1)` --YES-->
        - box `FP RDY ZL TO LA CONT COMMON COM CKTS (28.20.21.1)`
        - box `COND FP INCOMPL TGR TON CKT (28.42.53.1)`
- hex `MOD ZL E • ~(FW NOT ST) + ~(PROG IX) (28.15.41.1)` --YES--> box `Z 0 - 17 ABB PREP (28.96.03.1)`
  (printed lines: "MOD ZL E •" / "FW NOT ST +" / "PROG IX"; one continuous overbar over "FW NOT ST" and one over "PROG IX";
   compare Fig 3.1.20 where the bar over the same words is printed in separate segments)
- hex `MOD ZL E (28.15.41.1)` --YES--> box `HOT I TO ABB P2 (28.96.41.1)`   ("HOT I": [uncertain: I or 1])
- hex `MOD ZL E • MOD ZL M (28.15.41.1)` --YES--> box `GT AOB 18 TO ZL (28.27.50.1)`   (scan line through "ZL M")
- hex `MOD ZL M (28.15.41.1)` --YES-->
    - box `INSTR PREP COMPL ZL (28.27.32.1)`
    - box `BLOCK MOD ZLM TGR TOF (28.15.40.1)`
- hex `FPL 3 ~M • ALLOW LAST LD (28.23.00.1)` --YES--> box `COND FPL 3 TON CKT (28.13.31.1)`
  (overbar over the "M" only)

#### B2. second column (first hex from the horizontal bus; the rest hang from bus M)
- hex `FPL 3 E TGR ON (28.13.32.1)` --YES--> junction dot, to:
    - box `Z 0 - 17 TO MAB (28.21.60.1)`
    - box `GT ZLOC TO LAOC (28.21.60.1)`  (drawn ABOVE the horizontal bus, to the left of ZL FPI TGR; its line comes down to this YES dot)
- hex `FPL 4 E • ZL XS LTH • (28.13.42.1)` --YES--> box `X 0 - 63 TO XY ICIB (28.21.61.1)`
  (a "•" is printed after LTH with nothing following; "ICIB": [uncertain: ICIB / ICIR])
- hex `ZL INST PREP COMP • ZL EQ I • XOFI E TGR ON (28.12.12.1)` --YES--> box `XOFI TC FTH (24.00.09.1)`
  ("EQ I", "XOFI": I or 1, as printed they look like I)
- hex `ZL INST PREP COMP • ZL NOT EQ 1 • XOF1 E TGR ON (28.12.12.1)` --(exit line, no YES label seen)-->
    - box `XOFI A Z 13 - 17 • P TO XAB (28.86.56.1)`
- hex `ZL INT LTH (28.23.10.1)` --YES--> junction dot, to:
    - box `COND FPL 4 TON CKT (28.13.41.1)`  (directly below the hex)
    - a horizontal bus to the right with junction dots, feeding:
        - hex `FPL 4 E TGR ON (28.13.42.1)` --YES--> box `Z 0 - 17 TO MAB (28.21.60.1)`
        - hex `ZL INST PREP COMP • ZL INT FPL CL 1+3+4+6 (28.13.41.1)` --YES--> box `COND FPL 4 TON CKT (28.13.41.1)`
        - hex `FPL 4 E TGR ON (28.24.81.1)` --YES--> box `SET LA INT FTH (36.03.02.1)`
        - hex `FPL 4 E TGR ON • SBC (28.13.43.1)` --YES--> line Y
        - hex `FPL 4 M•E TGR ON (28.13.43.1)` --YES--> joins line Y at a junction dot
            - line Y goes to: box `TYPE 3 LD TO LA (28.21.74.1)` ; box `TYPE 3 LD TO BCU (28.21.74.1)`
- hex `ZL XS LTH` (NO ALD number printed in it; no YES label on its exit) --> horizontal bus with junction dots, feeding:
    - hex `FPL 4 E • M` (NO ALD number printed) --(no YES label)-->
        - box `I CHKR CYC E • M (38.03.03.1)`
        - box `I CHK PAR (34.08.11.1)`
    - hex `FPL 4 E • M (28.13.43.1)` --(no YES label)--> line W
    - hex `FPL 4 E • SBC (28.13.43.1)` --(no YES label)--> joins line W at a junction dot
        - line W goes to: box `TYPE 1 LD TO LA (38.03.01.1)`

#### B3. centre
- hex `~(FPL AD INNIB) / ~(DF + DS) - NOT ZL / 0 - 15 • NOT ZL 16 - 31. / • IRPT ENBLD (28.23.11.1)` --YES-->
  (overbar over the whole first line "FPL AD INNIB" — printed INNIB — and over "DF + DS" on the second line; a "-" (dash,
   not a dot) is printed between "DF + DS" and "NOT ZL")
    - box `FPL 3 PRECND LA DF (28.13.33.1)`
    - hex `DF MASK ONE (28.23.11.1)` --YES--> box `FPL 3 PRECND LA NOP FR ALARM (28.13.33.1)`
- vertical line N (from the horizontal bus) runs down and right to:
    - hex `FPL 3 • NO CANCEL • FPL 3 M • MNT MD ZL (28.13.33.1)` --YES--> box `FPL 3 PNL KEY REQ (28.21.71.1)`

#### B4. bus P, part ABOVE the horizontal bus (upper right of the page)
- at the top: hex `ZL ADDR 8 (28.20.08.1)` --YES-->
    - box `I CHK REQ (28.27.32.1)`
    - box `BLOCK ZL XS LTH SIG (28.20.41.1)`
- from a junction dot on P, a branch right with a junction dot:
    - hex `ZL ADDR 8 LTH•FPL 4E•NM (28.13.42.1)` --YES--> box `I GEN PARITY (28.44.14.1)`
      (printed lines: "ZL ADDR" / "8 LTH•FPL" / "4E•NM")
    - hex `ZL ADDR 8 LTH•FPR 4E (28.24.82.1)` --YES-->     ("FPR" as printed, third letter R)
        - box `SET LA INT STORE TAG (28.24.82.1)`
        - box `SET LA EXT STORE TAG (28.24.82.1)`

#### B5. bus P, part BELOW the horizontal bus
- box `COND XOFI E TON CKT (28.12.11.1)`  (direct)
- box `COND FPL 3 TON CKT (28.13.31.1)`  (direct)
- box `COND FPL 4 TON CKT (28.13.41.1)`  (direct)
- bus ends in hex `ZL ADDR 8 LTH (28.20.30.1)` --YES--> box `BLOCK ZL EXT OR ZLXS SIGNALS (28.20.30.1)`

#### B6. right end of the horizontal bus
- hex `IRPT EN • ZL 1 + 2 + 3 (28.23.20.1)` --YES--> box `COND LA DF GEN CKTS (28.25.30.1)`

### Noted (Fig 3.1.18)
- `SET LA INT STORE TAG (28.24.82.1)` and `SET LA EXT STORE TAG (28.24.82.1)` — both gated by hex `ZL ADDR 8 LTH•FPR 4E (28.24.82.1)`
- `SET LA INT FTH (36.03.02.1)` — gated by `FPL 4 E TGR ON (28.24.81.1)` after `ZL INT LTH (28.23.10.1)`
- `BLOCK ZL XS LTH SIG (28.20.41.1)`; `BLOCK ZL EXT OR ZLXS SIGNALS (28.20.30.1)`; `BLOCK MOD ZLM TGR TOF (28.15.40.1)`
- `COND XF + DEC ZL TON CKT (28.15.50.1)`; `COND XOFI E TON CKT (28.12.11.1)`; `XOFI TC FTH (24.00.09.1)`; `XOFI A Z 13 - 17 • P TO XAB (28.86.56.1)`; `X 0 - 63 TO XY ICIB (28.21.61.1)`
- `ZL INST PREP COMP • ZL EQ I • XOFI E TGR ON (28.12.12.1)`; `ZL INST PREP COMP • ZL NOT EQ 1 • XOF1 E TGR ON (28.12.12.1)`
- `MOD ZL E • ~(FW NOT ST) + ~(PROG IX) (28.15.41.1)`; `MOD ZL E (28.15.41.1)`; `MOD ZL E • MOD ZL M (28.15.41.1)`; `MOD ZL M (28.15.41.1)`; `NOT IHW E • NOT ZL MOD R • YR-ZL M (28.15.32.1)`
- `GT ZLOC TO LAOC (28.21.60.1)`; `FP RDY ZL TO LA CONT COMMON COM CKTS (28.20.21.1)`; `TYPE 3 LD TO LA (28.21.74.1)`; `TYPE 3 LD TO BCU (28.21.74.1)`; `TYPE 1 LD TO LA (38.03.01.1)`
- `FPL 3 PRECND LA DF (28.13.33.1)`; `FPL 3 PRECND LA NOP FR ALARM (28.13.33.1)`; `COND LA DF GEN CKTS (28.25.30.1)`
- `~(FPL AD INNIB) ~(DF + DS) - NOT ZL 0 - 15 • NOT ZL 16 - 31. • IRPT ENBLD (28.23.11.1)`; `IRPT EN • ZL 1 + 2 + 3 (28.23.20.1)`
- `FPL 3 ~M • ALLOW LAST LD (28.23.00.1)`; `MULT AND ADD` (inside the FP1 turn-on hex)
- No STORE WAIT / STORE COMPARE / WAIT FOR ACCEPT box on this page. No printed times or counts.

---

## FIGURE 3.1.19. ZL FP2 TRIGGER — PDF page 83 (landscape)

- Caption as printed: "FIGURE 3.1.19. ZL FP2 TRIGGER"
- Page tag: 1-39/1-40. Date: 2/1/62. Margin: "M3-04-3", "I UNIT FLOW DIAGRAMS".
- Applicability note: "CPU 7101 SER. NO. 30,004 AND HIGHER"
- Tiles read: f83-L (blank — no drawing on it), f83-M, f83-R, plus zooms zoom-d-83-*.
- No E / EM / M output labels are printed on the trigger box.

### Turn-on
- hex `SET ZL FP 2 (28.26.53.1)` --YES--+
- hex, four text lines + ALD, --YES--+ :
      `1Y53•1Y54•1Y55`
      `(~1Y56•1Y57) + 1Y53•`
      `1Y54•~1Y55•1Y56•1Y57`
      `•COND FP CL`
      `(28.26.53.1)`
  [uncertain: overbars. A bar is printed over "(1Y56" at the start of line 2 — it may be meant to span the whole
   parenthesis "(1Y56•1Y57)"; and a bar lies between "1Y57)" of line 2 and "1Y55" of line 3, read here as an overbar on
   "1Y55" in line 3. No bar seen on line 1. "1Y" may be "IY".]
- both YES lines join at a dot --`TON`--> box `ZL FP 2 TGR (28.26.53.1)`

### Outputs of ZL FP 2 TGR
One line from the bottom of the box to a junction dot on a horizontal bus. From the bus: to the LEFT a long line to the
left column (far-left vertical bus S, plus a drop to hex "NOT IHWE..."); straight DOWN into hex "INSTR PREP COMPL ZL • FP Z ALT ON";
a junction dot to the right of centre starting vertical bus Q; and at the right end a drop to hex "FPL 4 E TGR ON".

#### 1. left column (first hex from the horizontal bus; the rest hang from bus S by junction dots)
- hex `NOT IHWE • NOT ZL MOD R • YR - ZL M (28.15.32.1)` --YES-->
    - hex `FP Z ALT TGR ON (28.27.32.1)` --(no YES label seen)-->
        - box `FP RDY ZL TO LA CONT COMMON COM CKTS (28.20.21.1)`
        - box `COND FP INCOMPL TGR TON CKTS (28.42.53.1)`
- hex `MOD ZL E • ~(FW NOT ST) + ~(PROG IX) (28.15.41.1)` --YES--> box `Z 0 - 17 ABB PREP (28.96.03.1)`
  (one overbar over "FW NOT ST", one over "PROG IX")
- hex `MOD ZL E (28.15.41.1)` --YES--> box `HOT 1 TO ABB P 2 (28.96.41.1)`
- hex `MOD ZLE • MOD ZL M (28.15.41.1)` --YES--> box `GT AOB 18 TO ZL (28.27.50.1)`
- hex `MOD ZL M (28.15.41.1)` --YES-->
    - box `INSTR PREP COMPL ZL (28.27.32.1)`
    - box `BLOCK MOD ZL M TOR TOF (28.15.40.1)`   (re-read at 300%: prints "TOR" clearly; the same box in Figs 3.1.18/3.1.20 reads "TGR TOF" — as printed)

#### 2. centre
- hex `INSTR PREP COMPL ZL • FP Z ALT ON (28.27.32.1)` --NO (exit on the LEFT side; this is the only exit drawn)-->
    - hex `NO I CHKR REQ • NO T2 CHKR REQ • NO T1 CHKR REQ • OK TO I CHK IC • NO I CHKR REQ 3 (28.41.50.1)` --(no YES label)-->
      (five text lines, one term per line as separated by the dots)
        - box `COND IWCI TON CKTS (28.41.51.1)`   ("IWCI": [uncertain: IWC1])
        - box `COND IWC2 TON CKTS (28.41.61.1)`
      (the page fold line runs through the right edge of this hex and these two boxes; text legible)

#### 3. right end of the horizontal bus
- hex `FPL 4 E TGR ON (28.13.42.1)` --(no YES label)-->
    - box `1 TO ICIB P POS 3 - 8 (28.21.20.1)`   (two text lines "1 TO ICIB" / "P POS 3 - 8"; a stray bar is printed under "P POS")
    - box `Z 0 - 23 TO ICIB (28.21.61.1)`

#### 4. vertical bus Q (junction dots, top to bottom)
- first junction: a branch left and a branch right
    - (left) hex `~(BLOCK FP RDY) / ~(CANCEL FPR3E)• / ZL INSTR PREP COMPL (28.27.32.1)` --(no YES label)--> box `COND FPL 4 TON CKT (28.13.41.1)`
      [uncertain: overbars. A bar is clearly printed between line 1 "BLOCK FP RDY" and line 2 "CANCEL FPR3E" (read as the
       overbar of CANCEL FPR3E); line 1 sits against the hex's top border and appears to have its own bar as well.
       "FPR3E" as printed, third letter R.]
    - (right) hex `FPL 4 E • FPL 4 NM (28.13.42.1)` --(no YES label)-->
        - box `I CHKR CYC E • NM (38.03.03.1)`
        - box `I CHKR PAR (34.08.11.1)`
- second junction: a horizontal bus running LEFT with junction dots:
    - hex `FPL 4 E TGR ON • FPL 4 M TGR ON (28.13.43.1)` --YES--> line V
    - hex `SBC • FPL 4 E TGR ON (28.13.43.1)` --YES--> joins line V at a junction dot
        - line V goes to: box `TYPE 1 LD TO LA (28.21.72.1)`
    - the left end of this bus turns down and back right into the top of:
      hex `ZL NOT ADR 8•FPL4E•NM (28.13.42.1)` --(no YES label)--> box `I CHK PARITY (28.98.07.1)`
      ([uncertain: 28.98.07.1 — second group 98 or 96])
- third junction: box `BLOCK GEN OF PRE CND LA AD • FPL AD INHBT DF + DS (28.23.20.1)`  (direct, no hex; no overbar seen in it)
- bus Q ends in the top of hex `Z 24 (28.23.00.1)` --YES-->
    - hex `IF INHBT OP • GT FPL IND TO LA (28.25.01.1)` --YES--> box `OP SET LANOP (28.25.40.1)`
      (no overbar seen over "IF INHBT OP" here; the corresponding hex in Fig 3.1.20 has one over "IF INHBT AD")

### Noted (Fig 3.1.19)
- `BLOCK GEN OF PRE CND LA AD • FPL AD INHBT DF + DS (28.23.20.1)`; `BLOCK MOD ZL M TOR TOF (28.15.40.1)`
- `~(BLOCK FP RDY) ~(CANCEL FPR3E)• ZL INSTR PREP COMPL (28.27.32.1)` (a hex, not an action box)
- `MOD ZL E • ~(FW NOT ST) + ~(PROG IX) (28.15.41.1)`; `MOD ZL E (28.15.41.1)`; `MOD ZLE • MOD ZL M (28.15.41.1)`; `MOD ZL M (28.15.41.1)`; `NOT IHWE • NOT ZL MOD R • YR - ZL M (28.15.32.1)`
- `IF INHBT OP • GT FPL IND TO LA (28.25.01.1)`; `OP SET LANOP (28.25.40.1)`; `Z 24 (28.23.00.1)`
- `FP RDY ZL TO LA CONT COMMON COM CKTS (28.20.21.1)`; `TYPE 1 LD TO LA (28.21.72.1)`
- `COND IWCI TON CKTS (28.41.51.1)`; `COND IWC2 TON CKTS (28.41.61.1)`; `1 TO ICIB P POS 3 - 8 (28.21.20.1)`; `Z 0 - 23 TO ICIB (28.21.61.1)`
- No STORE TAG / STORE WAIT / STORE COMPARE / WAIT FOR ACCEPT box on this page. No printed times or counts.

---

## FIGURE 3.1.17. ZL DEC TRIGGER — PDF page 81

- Caption as printed: "FIGURE 3.1.17. ZL DEC TRIGGER"   (the brief's expected title was "ZL Dec Trigger ON"; the printed caption has no "ON")
- Page tag: 1-35/1-36. Date: 2/1/62. Margin: "M3-04-3", "I UNIT FLOW DIAGRAMS".
- Applicability note: "CPU 7101 SER. NO. 30,004 AND HIGHER"
- Tiles read: f81-T, f81-B, plus zooms zoom-d-81-1..6 (whole page at 165%).
- No E / EM / M output labels on the trigger box. Many of the "Z nn" hexes have no YES label printed on their exit
  line; where a YES is printed it is shown.

### Turn-on
- hex `IEX COMP RST • SAC • ZL IHW (28.27.30.1)` --YES--+
- hex `YR IHW • SBC • NOT IHW EX F • YR-ZL E (28.27.30.1)` --YES--+
  (printed lines: "YR IHW •" / "SBC • NOT IHW" / "EX F • YR-ZL  E")
- both join at a dot --`TON`--> box `ZL DECODE (DEC) TGR (28.27.30.1)`

### Upper bus (directly under the trigger; junction dots left to right)
- left end, direct (no hex):
    - box `I EX USE ZL TO FR 17 LFT + RHT HLFZ CONT CKTS (28.67.12.1)`
    - box `BLOCK ZL DEC TOF TGR TOF (28.27.30.1)`
- hex `SBC • I EX COMP RST (28.26.61.1)` --YES--> box `TOF ZL IHW TGR (28.26.61.1)`
- hex `ZL IHW • SBC • I EX GOING (28.15.40.1)` --YES--> box `TOF MOD ZL M TGR (28.15.40.1)`
- hex `BLK DEC (28.60.11.1)` --YES--> a line that runs down to a junction dot on the LOWER bus (this is the only line
  drawn from the upper part of the figure to the lower bus) and continues down as column 5 below
- right end, direct (no hex):
    - box `BLOCK DEC ZR (28.60.11.1)`
    - box `BLOCK USE ZR (28.60.11.1)`
    - box `BLOCK I EX USE ZR (28.60.11.1)`

### Lower bus (fed, as drawn, from the YES of hex BLK DEC) — columns left to right

#### Column 0 (far left)
- hex `OLLIE• BAC (28.79.23.1)` --YES (exit on the LEFT side)-->
    - box `END EX ZL (28.79.63.1)`
    - box `GT Z 0-18 TO ICIB 0-23 (28.79.65.1)`

#### Column 1 (vertical bus; first hex from the lower bus directly)
- hex `ZLNA ON + ZLXA ON + ZLSA ON (28.51.08.1)` --YES--> box `ZL BR ADR INVLD (28.51.07.1)`
- hex `RLLI E ON (28.79.53.1)` --YES--> box `GT Z 0-23 TO ICIB 0-23 (28.79.65.1)`
- hex `BI + BB • RLLI E ON (28.79.53.1)` --YES--> box `END EX ZL (28.79.63.1)`
  ("BI + BB" prints heavy/filled-in: [uncertain: BI + BB])
- hex `OLLIE ON (28.79.23.1)` --YES-->
    - box `GT Z 19-24 CK (25.03.02.1)`
    - box `Z 28-31 TO ICIB 60-63 (28.79.65.1)`
- five hexes whose YES lines all join one vertical line (junction dots), which ends at box `TON ZLIDC (28.51.03.1)`:
    - hex `SAC • SET ZL IDC ON I PAR ERR (28.51.03.1)`
    - hex `COND IDC FR UNCOR ERR • SAC (28.51.03.1)`
    - hex `LA PAR ERR• SET ZL IDC ON LA PAR ERR • SAR (28.51.03.1)`
    - hex `XS ADR CKK • SET ZLIDC ON XAC (28.51.03.1)`
    - hex `SET ZLIDC + ZRIDC ON MC • SBC • MEM CKK (28.51.03.1)`
- direct (no hex): box `USE ZL + ZR TO BR INSTR DEC CKTS (28.61.70.1)`
- direct (no hex): box `USE ZL TO ZOA MEM AREA DEC (28.61.76.1 - 28.61.78.1)`
- the column-1 bus then turns right along the bottom of the page as a horizontal bus with six hexes:
    - hex `SET IDC ON IAUC ERR • ~(INH IAUC ERR TO IDC) (28.51.01.1)` --YES--> box `SET ZLIDC ON IAUC ERR (28.51.03.1)`
      (printed lines: "SET IDC ON" / "IAUC ERR • INH IAUC" / "ERR TO IDC"; overbar over "INH IAUC" on line 2 and over
       "ERR TO IDC" on line 3)
    - hex `SBC • SET ZRAD + ZLAD (28.51.04.1)` --YES--> box `TON ZLAD (28.51.04.1)`
    - hex `ZLAD ON (28.51.04.1)` --YES-->
        - box `ZLAD + ZRAD NOOP (28.61.75.1)`
        - hex `GI IEI TO LA (28.51.04.1)` --(no YES label)--> box `SET LAAD (28.25.20.1)`
          ([uncertain: "GI IEI" — prints G I  I E I; the similar hex to the right prints "GT IET"])
    - hex `SBC • EXT EXID RST Z IDC (28.51.02.1)` --YES--> box `RESET ZRIRC (28.51.02.1)`   ("ZRIRC" as printed)
    - hex `ZLIDC ON (28.51.03.1)` --YES-->
        - hex `GT IET TO LA (28.51.02.1)` --(no YES label)--> box `IDC TO LA IJ (28.25.10.1)`
    - hex `Z18 (28.60.15.1)` --YES--> box `Z18 + Z50 TO MEM AREA DEC CKTS (28.61.77.1)`

#### Column 2
- hex `Z17 (28.60.13.1)` --> box `GEN NOT OA 17 (28.67.13.1)`
- hex `Z18 (28.60.13.1)` -->
    - box `CND SPND INTLK TGR TON (28.42.44.1)`
    - box `GEN I EX IN PROG + RCVR TO YR (28.42.44.1)`
    - box `GEN OA 18 (28.67.13.1)`
- hex `Z19 (28.60.13.1)` -->
    - box `ZEDEC 19 TO MIGC CL DCDING (28.61.21.1)`
    - box `ZEDEC 19 TO I BOX [illegible second line — obliterated by the page fold; shape consistent with "IND DCDING CKTS"] (28.52.10.1)`
    - box `ZEDEC 19 TO BR INSTR DCDING CKTS (28.61.70.1)`
- hex `Z 20 (28.16.13.1)` -->      (prints 28.16.13.1; every other Z hex in this column prints 28.60.13.1)
    - box `ZEDEC 20 TO MIGC CL DEC CKTS (28.61.21.1)`
    - box `ZEDEC 20 TO I BOX IND DEC CKTS (28.52.10.1)`
    - box `ZEDEC 20 TO BR INSTR DEC CKTS (28.61.70.1)`
- hex `Z 21 (28.60.13.1)` -->
    - box `ZEDEC 21 TO MIGC CL DEC CKTS (28.61.21.1)`   (scan line through the ALD number: [uncertain: 28.61.21.1])
    - box `ZEDEC 21 TO I BOX IND DEC CKTS (28.52.10.1)`
    - box `ZEDEC 21 TO BR INSTR DEC CKTS (28.61.70.1)`

#### Column 3
- hex `Z 22 (28.60.13.1)` --YES-->
    - box `ZEDEC 22 TO BR INSTR DEC CKTS (28.61.70.1)`
    - box `ZEDEC 22 TO 1 BOX IND DEC CKTS (28.52.10.1)`   (prints "1 BOX" here, "I BOX" elsewhere)
    - box `ZEDEC 22 TO CL DEC CKTS (28.61.11.1)`
- hex `Z 23 (28.60.13.1)` --YES-->
    - box `ZEDEC 23 TO DIRECT IX INSTR DEC (28.61.42.1 - 28.61.44.1)`   (prints 28.61.42.1 as the first number; no "CKTS")
    - box `ZEDEC 23 TO CL DEC CKTS (28.61.11.1)`
    - box `ZEDEC 23 TO I BOX IND DEC CKTS (28.52.10.1)`
    - box `ZEDEC 23 TO BR INSTR DEC CKTS (28.61.70.1)`   (fold line through "ZEDEC 23 TO BR")
    - box `ZEDEC 23 TO INSTR EX FUN GEN (28.61.75.1)`
- hex `Z 24 (28.60.13.1)` -->
    - box `ZEDEC 24 TO BR INSTR DEC CKTS (28.61.70.1)`
    - box `ZEDEC 24 TO INSTR EX FUN GEN (28.61.75.1)`
    - box `ZEDEC 24 TO I BOX IND DEC CKTS (28.52.10.1)`
    - box `ZEDEC 24 TO DIRECT IX INSTR DEC CKTS (28.61.41.1 - 28.61.44.1)`
    - box `ZEDEC 24 TO C DEC CKTS (28.61.11.1)`   (prints "C", not "CL"; scan line through the number: [uncertain: 28.61.11.1])
    - box `ZEDEC 24 TO TMT • SWAP DEC CKTS (28.61.12.1)`

#### Column 4
- hex `Z 25 (28.60.13.1)` --YES-->
    - box `ZEDEC TO DIRECT IX INSTR DEC CKTS (28.61.41.1 - 28.61.44.1)`   (no "25" printed after ZEDEC in this box)
    - box `ZEDEC 25 TO BR INSTR DEC CKTS (28.61.70.1)`
    - box `ZEDEC 25 TO CL DEC CKTS (28.61.11.1)`
    - box `ZEDEC 25 TO TMT • SWAP DEC CKTS (28.61.12.1)`
    - box `ZEDEC 25 TO BR INSTR FUN GEN (28.61.71.1)`
- hex `Z 26 (28.60.14.1)` -->
    - box `ZEDEC 26 TO DIRECT IX INSTR DEC CKTS (28.61.41.1 - 28.61.44.1)`
    - box `ZEDEC 26 TO CL DEC CKTS (28.61.11.1)`   (fold line through "ZEDEC 26")
    - box `ZEDEC 26 TO BR INSTR DEC CKTS (28.26.70.1)`   (prints 28.26.70.1; the same box for other Z values prints 28.61.70.1)
    - box `ZEDEC 26 TO BR INSTR FUN GEN (28.61.11.1)`   (prints 28.61.11.1; the same box for Z 25 / Z 27 prints 28.61.71.1)
- hex `Z 27 (28.60.14.1)` -->
    - box `ZEDEC 27 TO BR INSTR FUN GEN (28.61.71.1)`
    - box `ZEDEC 27 TO CL DEC CKTS (28.61.11.1)`   (number faint: [uncertain: 28.61.11.1])
    - box `ZEDEC 27 TO BR INSTR DEC CKTS (28.61.70.1)`
- hex `Z 28 (28.60.14.1)` --> (two boxes left of the line, two right)
    - box `ZEDEC 28 TO IMMIX INSTR DEC CKTS (28.61.31.1- 28.61.33.1)`   (fold line through the first text line; second number prints .33, where Z 29/30/31 print .34)
    - box `ZEDEC 28 TO INSTR EX FUN GEN (28.61.74.1)`
    - box `ZEDEC 28 TO BR INSTR DEC CKTS (28.61.70.1)`
    - box `ZEDEC 28 TO BR INSTR DEC FUN GEN (28.61.71.1)`

#### Column 5 (the BLK DEC YES line continuing downward)
- hex `Z 29 (28.60.14.1)` -->
    - box `ZEDEC 29 TO IMM IX INSTR DEC CKTS (28.61.31.1 - 28.61.34.1)`
    - box `ZEDEC 29 TO 1ST LEVEL OF IMM CKT (28.61.36.1)`
    - box `ZEDEC 29 TO BR INSTR DEC FUN GEN (28.61.71.1)`
    - box `ZEDEC 29 TO INSTR EX FUN GEN (28.61.74.1)`
- direct (no hex): box `COND ZLIF TON CKT (28.15.05.1)`
- hex `Z 30 (28.60.14.1)` -->
    - box `ZEDEC 30 TO IMM IX INSTR DEC CKT (28.61.31.1 - 28.61.34.1)`
    - box `ZEDEC 30 TO I BOX IND TSTR CKT (28.52.11.1)`
- hex `Z 31 (28.60.14.1)` --YES-->
    - box `ZEDEC 31 TO IMM IX INSTR DEC CKT (28.61.31.1 - 28.61.34.1)`

### Noted (Fig 3.1.17)
- `BLOCK ZL DEC TOF TGR TOF (28.27.30.1)`; `BLOCK DEC ZR (28.60.11.1)`; `BLOCK USE ZR (28.60.11.1)`; `BLOCK I EX USE ZR (28.60.11.1)`; hex `BLK DEC (28.60.11.1)`
- `TOF MOD ZL M TGR (28.15.40.1)` <- `ZL IHW • SBC • I EX GOING (28.15.40.1)`
- `CND SPND INTLK TGR TON (28.42.44.1)`; `GEN I EX IN PROG + RCVR TO YR (28.42.44.1)`
- `ZL BR ADR INVLD (28.51.07.1)`; `USE ZL + ZR TO BR INSTR DEC CKTS (28.61.70.1)`; every `ZEDEC nn TO BR INSTR DEC CKTS` / `... BR INSTR FUN GEN` / `... BR INSTR DEC FUN GEN` box listed above
- every `ZEDEC nn TO DIRECT IX INSTR DEC CKTS`, `... IMM IX INSTR DEC CKT(S)`, `... IMMIX INSTR DEC CKTS`, `... I BOX IND DEC CKTS`, `ZEDEC 30 TO I BOX IND TSTR CKT (28.52.11.1)` box listed above
- `XS ADR CKK • SET ZLIDC ON XAC (28.51.03.1)`
- `RLLI E ON (28.79.53.1)`; `BI + BB • RLLI E ON (28.79.53.1)`; `OLLIE• BAC (28.79.23.1)`; `OLLIE ON (28.79.23.1)`; `END EX ZL (28.79.63.1)` (twice)
- (the ZEDEC boxes are quoted in full, with numbers, in the column lists above and are not repeated here)
- IDC boxes/hexes: `SAC • SET ZL IDC ON I PAR ERR (28.51.03.1)`; `COND IDC FR UNCOR ERR • SAC (28.51.03.1)`; `LA PAR ERR• SET ZL IDC ON LA PAR ERR • SAR (28.51.03.1)`; `SET ZLIDC + ZRIDC ON MC • SBC • MEM CKK (28.51.03.1)`; `TON ZLIDC (28.51.03.1)`; `SET IDC ON IAUC ERR • ~(INH IAUC ERR TO IDC) (28.51.01.1)`; `SET ZLIDC ON IAUC ERR (28.51.03.1)`; `SBC • EXT EXID RST Z IDC (28.51.02.1)`; `ZLIDC ON (28.51.03.1)`; `IDC TO LA IJ (28.25.10.1)`
- `ZLAD + ZRAD NOOP (28.61.75.1)`; `GI IEI TO LA (28.51.04.1)`; `GT IET TO LA (28.51.02.1)`; `SET LAAD (28.25.20.1)`
- No STORE TAG / STORE WAIT / STORE COMPARE / WAIT FOR ACCEPT box on this page. No printed times or counts.

---

## Not read with confidence

All six figures were completed (3.1.16, 3.1.17, 3.1.18, 3.1.19, 3.1.20, 3.1.21). Specific doubts:

General
- "1Y" vs "IY" in every 1Y53..1Y57 term (Figs 3.1.18-3.1.21): the leading glyph is identical to the digit 1 used elsewhere; transcribed "1Y".
- "I" vs "1" in XOFI / XOF1 / XOF 1E / EQ I / EQ1 / HOT I / HOT 1 / IWCI / IWCIE / "1 BOX" / "1RCY": transcribed as each instance looks; none is certain.
- Where two hex YES lines join one line that then feeds boxes (lines X, X1-X4, Y, W, V), the drawing does not say whether the
  join is OR or a series AND; transcribed as drawn only.

Fig 3.1.20 (p84)
- Turn-on hex `1Y53•1Y54•1Y55•1Y56 / ~1Y57 + ~1Y55•1Y56•1Y57 / •COND FPCL`: overbar placement (two bars seen, at start of line 2 and over 1Y55 in line 2).
- hex on the page fold `[FPL/FDL] 4 E • FPL 4 M (28.13.43.1)`: first word and any overbar.
- hex `MOD ZLE • ~FW ~NOT / ~ST + ~(PROG IX)`: whether the bar segments over FW, NOT, ST are one intended bar.
- hex `IRPT ENBLD ... ~(FPL AD) ~(INHBT DF) ~(+ DS)`: whether the three bar segments are one bar over "FPL AD INHBT DF + DS".
- hex `IF INHBT DS • GT FPL IND TO LA • FPL AD INHBT DF + DS (28.25.20.1)`: no overbar seen (its sibling `~(IF INHBT AD)...` has one).
- box `TON PIRCY TGR (28.42.71.1)`: prints "PIRCY" as one word at zoom (meaning P I RCY not decided).
- Bus D's nine BLOCK boxes, both PROGRAM STORE COMPARE hexes, the ZOAR hex and its three boxes were re-read at 200-220%: no change, no overbars.
- hexes `ZL INSTR PREP COMPL• (28.13.41.1)` and `FPL 2 M + ZOAL INT FPL CL 3 + 1• ZL INSTR PREP COMPL`: dangling/embedded "•" and grouping.

Fig 3.1.21 (p85)
- FP4 turn-on hex `~1Y53. ~1Y55 / .1Y56. ~1Y57 / .COND FP CL`: overbars (three seen).
- FP6 turn-on hex `1Y53.1Y NOT / 54.1Y55.1Y56. / 1Y57.COND / FP CL`: the "1Y NOT 54" wording as printed.
- hex `ZL ADR 8 LTH .FPR2E` 28.24.82.1: "FPR2E" (R vs L).
- box `COND FPDDE TON` 28.10.11.1: "FPDDE".
- box `XOF 1 TC FETCH` 24.00.09.1: "1 TC" vs "I TC"; hex `... XOF1E` crowded.
- box `GT ZLOC TO LAOC` 28.21.60.1 (C2): leading "28" smudged.
- C3 ALD numbers under the page fold: 28.13.33.1, 28.21.71.1, 28.20.30.1 (x2) — final digit partly hidden.
- box `Z13-17.P TO XAB` 28.86.56.1: 86 vs 96.
- box `ZO-17 TO MAB`: O vs 0.
- `COND FPL4E TON` 28.14.41.1 (FP6 side) vs 28.13.41.1 (FP4 side): both as printed; possible printed inconsistency, not a misreading as far as I can tell.
- hex `~(FPL ADINHIB DF) / ~DS. IRPT / ENABLED. NOT / ZL0-31`: extent of the two overbars.
- Which of ZL FP4 TGR / ZL FP6 TGR feeds which side of box "ZL FP4 OR ZL FP6" was followed with care, but the long lines cross tile
  boundaries (f85-M/R); the FP6 "ZL NE LTHD" branch is tapped from the FP6 line only, as drawn.

Fig 3.1.16 (p80)
- Suspend hexes `IWC2 • ICOR NE • 2Y RD BRU + BRC • NO CHKR SING ERR • SAR` and `IWCIE • ICOR NE o 1YRD BRU + BRC • NO CHKR SING ERR • SAR`:
  first lines touch the hex border (possible hidden overbar); "IWCIE"; hollow dot after NE; grouping of + and • not indicated.
- Two boxes both reading `BLOCK GEN OF IF1Y GT ICA O-16 TO MAB (28.41.22.1)` (one may be ICR).
- box `BLOCK ICBC1Y TON (28.41.23.1)` (struck by scan line); `BLOCK ICOF 1Y TON` vs `BLOCK ICFO2Y TON` spelling as printed.
- (resolved at zoom, as printed, likely printing inconsistencies: `BLOCK IF2Y IND TOF (28.42.32.1)`; `COND ICADY E2 TON (28.41.41.1)`.)
- The upper half (ZL BLOCK 1Y/2Y TGR and their ten boxes) and the ZL SPND 2Y column were re-read at 200%: no change, no overbars.

Fig 3.1.18 (p82)
- FP1 turn-on hex (nine lines): all overbar assignments, and the short bar above "MULT".
- box `X 0 - 63 TO XY ICIB (28.21.61.1)`: "ICIB".
- hexes `ZL XS LTH` and first `FPL 4 E • M`: no ALD number printed (confirmed absent, not illegible).
- hex `~(FPL AD INNIB) / ~(DF + DS) - NOT ZL / 0 - 15 • NOT ZL 16 - 31. / • IRPT ENBLD`: bar extents; "-" between DS and NOT.
- hex `ZL ADDR 8 LTH•FPR 4E (28.24.82.1)`: "FPR".

Fig 3.1.19 (p83)
- Turn-on hex `1Y53•1Y54•1Y55 / (~1Y56•1Y57) + 1Y53• / 1Y54•~1Y55•1Y56•1Y57 / •COND FP CL`: overbar extents.
- hex `~(BLOCK FP RDY) / ~(CANCEL FPR3E)• / ZL INSTR PREP COMPL`: whether line 1 has its own overbar; "FPR3E".
- (resolved at zoom, as printed: `BLOCK MOD ZL M TOR TOF (28.15.40.1)`.)
- box `I CHK PARITY (28.98.07.1)`: 98 vs 96.
- box `COND IWCI TON CKTS`: IWCI vs IWC1.
- hex `IF INHBT OP • GT FPL IND TO LA (28.25.01.1)`: no overbar seen.
- hex `Z 24 (28.23.00.1)`: text is just "Z 24" as far as I can see.

Fig 3.1.17 (p81)
- box `ZEDEC 19 TO I BOX [second line obliterated by fold] (28.52.10.1)`.
- hex `BI + BB • RLLI E ON (28.79.53.1)`: "BI + BB".
- hex `GI IEI TO LA (28.51.04.1)` vs `GT IET TO LA (28.51.02.1)`.
- ALD numbers struck by the scan line: `ZEDEC 21 TO MIGC CL DEC CKTS (28.61.21.1)`, `ZEDEC 24 TO C DEC CKTS (28.61.11.1)`, `TON ZLIDC (28.51.03.1)`; faint: `ZEDEC 27 TO CL DEC CKTS (28.61.11.1)`.
- As-printed oddities that I read clearly but which look like printing inconsistencies: `Z 20 (28.16.13.1)`; `ZEDEC 26 TO BR INSTR DEC CKTS (28.26.70.1)`;
  `ZEDEC 26 TO BR INSTR FUN GEN (28.61.11.1)`; `ZEDEC TO DIRECT IX INSTR DEC CKTS` (no 25); `ZEDEC 23 TO DIRECT IX INSTR DEC (28.61.42.1 - ...)`.
- That the whole lower bus hangs only from the YES line of hex `BLK DEC (28.60.11.1)`: followed on tile and zoom; reported as drawn.
- hex `SET IDC ON IAUC ERR • ~(INH IAUC ERR TO IDC)`: overbar extent.

# APPENDIX E -- reader transcription

# part_e — R23-9732 I UNIT FLOW DIAGRAMS, PDF pages 86-91 (Figs 3.1.22 - 3.1.27)

Conventions: `~X` = drawn overbar over X; the printed word NOT is kept as NOT. `•` = AND dot.
"no label printed" = the exit line of a hexagon carries no YES/NO text on the page.
Order written: 87, 91, 89, 90, 88, 86.

---

## FIGURE 3.1.23. WBC + DEC SEQUENCER AND XF + DEC SEQUENCER

- PDF page 87. Caption as printed (two lines): "FIGURE 3.1.23. WBC + DEC SEQUENCER AND / XF + DEC SEQUENCER"
- Page tag: 1-47/1-48. Date: 2/1/62. Running heads: "M3-04-3", "I UNIT FLOW DIAGRAMS".
- Applicability note printed: "CPU 7101 / SER. NO. 30,004 / AND HIGHER"

### A. WBC + DEC SEQUENCER (upper half of page)

Turn-on condition (hexagon above the bar, exit labelled YES, line labelled TON into the bar):

    hex: SAC • ZR NOT FPCL •
         MOD ZR • FW NOT S + FW
         COMP + YL - ZL • NOT
         MOD L + MOD ZL • FWS •
         FW S + FW NOT S
         (28.15.80.1)
      --YES--> TON --> bar

(no overbars seen in this hexagon; line breaks as printed; no grouping printed)

Bar: WBC + DEC SEQUENCER (28.15.80.1)      outputs printed under the bar: E , E•M , M

Output E (one line running left along the page with three drops; all unconditional unless under a hexagon):

    first drop (leftmost column):
      TON WBC + DEC M TGR (28.15.80.[uncertain: 1? last digit smudged])
      GT Z TO ABB (28.27.53.1)
      Z0-17 ABB PREP (28.15.41.1)
      Z 18 ABB PREP (28.15.41.1)
      Z 19 - 23 ABB PREP (28.15.41.1)
      HOLD DATA SELECT PREP (28.96.43.1)
      COND TON • TOF WNA • WXA • WSA TGRS (28.51.09.1)
    second drop (second column):
      TOF YL - ZL M TGR (28.15.70.1)
      TOF YR-ZL M TGR (28.15.30.1)
      TOF YL-ZR M TGR (28.15.10.1)
      TOF FULL WRD S TGR (28.26.60.1)
      TOF FULL WRD NOT S TGR (28.26.60.1)
      TOF MOD ZR M TGR (28.15.20.1)
      GT AOB 0-17 + P 0-17 TO W (28.02.01.1)
    third drop:
      hex: SBC   (no ALD number printed in the hexagon)
        --YES--> TOF MOD ZL M TGR (28.15.40.1)
    directly under the E output:
      hex: Z 35 • 36 • 37 • 38 • 39 • 40 ZERO (25.04.01.1)
        --YES--> IC - W - Z ABA (27.02.06.1)
        --YES--> IC - Z ABA P1 (27.05.01.1)
        --YES (same line continues down into)--> hex: SUM 18 • 19 • 20 • 21 TO MEM AREA DEC (28.14.02.1)
                    --YES--> WORD BNDRY CROSSOVER (28.22.02.1)

Output E•M:

      hex: ~IMM • VFL (28.15.81.1)          (overbar over IMM only)
        --YES--> COND WBC TGR TON (28.22.02.1)   [uncertain: third group "02" is smudged; 28.22.02.1?]
      hex: VFL • ~IMM (28.15.81.1)          (overbar over IMM only)
        --YES--> GT AOB 19 TO ZL (28.27.50.1)

   (Both hexagons print the bar over IMM; they differ only in word order as printed.)

Output M:

      COND VFL 1 TON CKT (28.11.11.1)
      hex: VFL + IO (28.11.11.1)
        --YES--> BLOCK GEN OF NO I CHKR REQ L (28.20.21.1)
      FW RDY E1 (28.67.17.1)
      FW RDY E2 (28.75.72.1)

### B. XF + DEC SEQUENCER (lower half of page)

Three turn-on hexagons side by side above the bar; their exit lines join on one horizontal line that enters the bar
through a line labelled TON. Only the left hexagon's exit has YES printed; the middle and right exits have no label printed.

    hex (left):   ~(BLOK XF + DEC) • ZL
                  IHW • YR-ZL M • NOT
                  IHW EX • NOT I EX
                  IN PROG • SAC • NOT
                  MOD L RQ
                  (28.15.50.1)
        bar extent seen: one bar over "BLOK XF + DEC" on line 1.
        --YES--> TON

    hex (middle): SAC • ZR WAS IHW
                  ~(• BLOK XF + DEC) • ZL
                  IHW • YR-ZL M • NOT
                  IHW EX • NOT I EX
                  IN PROG
                  (28.15.50.1)
        bar extent seen: one rule between line 1 and line 2, spanning from the leading "•" of line 2 to the end of "DEC"
        (the rule is the length of "• BLOK XF + DEC" and a little shorter than line 1's text "SAC • ZR WAS IHW").
        Read as an overbar on "• BLOK XF + DEC"; it could be taken for an underline of line 1.
        --(no label printed)--> TON

    hex (right):  ZL MOD REQ • SAC •
                  NOT IHW EX • ZR
                  WAS IHW • ~(BLOK XF
                  + DEC) • ZL [uncertain: FP? / EP?] + LH
                  FW
                  (28.15.50.1)
        bar extent seen: two rule segments. One lies between lines 2 and 3 at the right, under "• ZR" and over "BLOK XF".
        The other lies between lines 3 and 4 at the left, under "WAS IHW" and over "+ DEC". Read as one overbar
        ~(BLOK XF + DEC) continued across the line break (consistent with the other two hexagons), NOT as bars on
        "ZR" or "WAS IHW" -- but the rules sit between text lines, so see "Not read with confidence".
        A stray tick mark is printed after the "•" that ends line 1 ("SAC •'").
        --(no label printed)--> TON

Bar: XF + DEC SEQUENCER (28.15.50.1)      outputs printed under the bar: E , M      (no E•M output is drawn on this bar)

Output E (line running to the left margin, then down the left side):

      TON XF + DEC M TGR (28.15.50.1)
      COND YR-ZL M TGR TOF (28.15.30.1)
      hex: NOT 1 BIT MOD RQD (28.15.51.1)
        --YES--> GT Z 28-30 TO XAB 1-3 (28.27.52.1)
      hex: 1 BIT MOD R T (28.15.51.1)        [printed with a gap between "R" and "T": "R  T"; a letter may be missing in the print]
        --YES--> GT Z 31 TO XAB 4 (28.27.52.1)
        --YES--> XS READ P (24.00.09.1)
        --YES--> BLOCK GEN OF INH NIDC SET IDC FR XAC (28.27.31.1)
        --YES--> TOF ZR WAS IHW TGR (28.15.51.1)
      hex: XF + DEC M TGR OFF (28.15.50.1)
        --YES , with "E • ~M" printed beside the exit just below the YES (bar over M)-->
                 PREP RST X 0-63 (28.86.57.1)

Output M (line straight down from the bar):

      COND MOD ZL E TON CKT (28.15.40.1)
      TOF XF + DEC E TGR (28.15.50.1)
      (from the same junction as the TOF XF + DEC E TGR box, a line runs LEFT to:)
      hex: FW NOT ST • PX Y • MOD ZL E (28.15.42.1)
        --(no label printed)--> PREP GT Z 0-23 TO ICIB (28.79.65.1)
        --(no label printed)--> COND IDC FR I PAR ERR PREP ([uncertain: 28? prints like 23].99.03.1)
        --(no label printed)--> TON PX YL TGR (28.78.34.1)
        --(no label printed)--> PREP SET ONE TO ICIB PAR (28.21.20.1)
        --(same line continues down into)--> hex: ~(MOD ZL M) (28.15.42.1)      (one bar over all of "MOD ZL M")
                    --YES--> IP CHK PAR (28.98.07.1)
                    --YES--> I CHK E • NM ([uncertain: prints 38; 28?].03.03.1)
      BLOCK Y-Z START TON (28.26.11.1)
      hex: ZL IHW T • NOT ZL MOD (28.15.51.1)
        --YES--> hex: ZR INSTR COMP (28.15.51.1)
                    --YES--> IHW RDY E1 ([uncertain: 28.67.17.1? a fold line runs through the number])
                    --YES--> IHW RDY E2 (28.64.14.1)
      hex: FW NOT ST (28.15.40.1)
        --(no label printed)--> COND MOD ZL TON CKT (28.15.40.1)

### Noted (Fig 3.1.23)

- "XF + DEC SEQUENCER (28.15.50.1)"
- "~(BLOK XF + DEC) • ZL IHW • YR-ZL M • NOT IHW EX • NOT I EX IN PROG • SAC • NOT MOD L RQ (28.15.50.1)"
- "SAC • ZR WAS IHW ~(• BLOK XF + DEC) • ZL IHW • YR-ZL M • NOT IHW EX • NOT I EX IN PROG (28.15.50.1)"
- "ZL MOD REQ • SAC • NOT IHW EX • ZR WAS IHW • ~(BLOK XF + DEC) • ZL FP[?] + LH FW (28.15.50.1)"
- "TON XF + DEC M TGR (28.15.50.1)"; "TOF XF + DEC E TGR (28.15.50.1)"; "XF + DEC M TGR OFF (28.15.50.1)" with "E • ~M"
- "PREP RST X 0-63 (28.86.57.1)"
- "NOT 1 BIT MOD RQD (28.15.51.1)"; "1 BIT MOD R T (28.15.51.1)"
- "GT Z 28-30 TO XAB 1-3 (28.27.52.1)"; "GT Z 31 TO XAB 4 (28.27.52.1)"
- "XS READ P (24.00.09.1)"
- "BLOCK GEN OF INH NIDC SET IDC FR XAC (28.27.31.1)"
- "TOF ZR WAS IHW TGR (28.15.51.1)"
- "COND MOD ZL E TON CKT (28.15.40.1)"; "COND MOD ZL TON CKT (28.15.40.1)"; "TOF MOD ZL M TGR (28.15.40.1)"; "TOF MOD ZR M TGR (28.15.20.1)"
- "FW NOT ST • PX Y • MOD ZL E (28.15.42.1)"; "~(MOD ZL M) (28.15.42.1)"; "ZL IHW T • NOT ZL MOD (28.15.51.1)"
- "COND IDC FR I PAR ERR PREP (2[8/3].99.03.1)"
- "BLOCK Y-Z START TON (28.26.11.1)"; "BLOCK GEN OF NO I CHKR REQ L (28.20.21.1)"
- "IHW RDY E1 (28.67.17.1?)"; "IHW RDY E2 (28.64.14.1)"; "ZR INSTR COMP (28.15.51.1)"
- WBC turn-on hexagon (contains MOD ZR, FW COMP, MOD L, MOD ZL): "SAC • ZR NOT FPCL • MOD ZR • FW NOT S + FW COMP + YL - ZL • NOT MOD L + MOD ZL • FWS • FW S + FW NOT S (28.15.80.1)"

### Not read with confidence (Fig 3.1.23)

- Overbar extents in the middle and right XF + DEC turn-on hexagons (rules sit between text lines; described above).
- Right XF hexagon: "ZL FP + LH" -- the letter before P is broken (F or E); stray tick after "SAC •".
- "1 BIT MOD R T" -- gap in print between R and T.
- "ZL IHW T •" -- transcribed as printed (single letter T).
- ALD digits: TON WBC + DEC M TGR (28.15.80.?); COND WBC TGR TON (28.22.02.1); COND IDC FR I PAR ERR PREP (28 vs 23); I CHK E • NM (38 vs 28); IHW RDY E1 (fold line).
- VFL + IO hexagon: its YES line is broken in the print for a short stretch before reaching BLOCK GEN OF NO I CHKR REQ L (connection assumed from position).
- Whether the hexagons with no printed label are YES exits is not stated on the page.


---

## FIGURE 3.1.27. FW TRIGGER

- PDF page 91. Caption as printed: "FIGURE 3.1.27. FW TRIGGER"
- Page tag: 1-55/1-56. Date: 1/1/63 (note: this page is dated differently from pages 86-89, which are 2/1/62).
  Running heads: "M3-04-3", "I UNIT FLOW DIAGRAMS".
- Applicability note printed: "CPU 7101 / SER. NO. 30,004 / AND HIGHER"
- Read from my own 200% tiles of iu/r-91.png (tiles/zoom-e-91-1L..4R) plus 300-400% crops of every hexagon carrying bars.
- Overbar convention on this page: bars over individual bit numbers are frequent. When a barred term is on the second
  line of a hexagon the bar prints as a rule under the first line; I have assigned each such rule to the term directly
  beneath it (lengths match in every case checked). "Z ~52" = bar over the digits only; "~(Z 53)" = bar over "Z 53".

### Turn-on and bar

    hex: WBC + DEC E TGR ON (28.15.80.1)
      --YES--> TON --> bar
    Bar: FULL WORD TGR (28.22.02.1)        (no E / M output labels are printed under this bar; one line leaves its bottom)

The single output line meets a long horizontal line with five drops, left to right:
  [A] hex ZEDEC ~22 ...      [B] an unconditional trunk      [C] hex ZEDEC 25 ...      [D/E] hex Z 55 ...      [F/G] hex Z59

### [A] leftmost drop

    hex: ZEDEC ~22 • ~23 •
         ~24 • ~25 • ~26 • ~27 •
         19 • 20 • 21
         (28.61.70.1)
      --YES--> a vertical line ("A-bus") carrying, top to bottom:
        BB SIG TO SLLI STORE LEVEL LALD OUT CKTS (28.79.43.1)
        COND XSFI TON CKT (28.70.41.1)
        COND XSFI TOF CKT (28.70.43.1)
        COND ZLAD + ZRAD • ZDS • ZDF TON CKTS (28.79.15.1)
        COND DEC 4 TON; (28.79.14.1)             [a stray mark like ";" follows TON]
        hex: ZL ADR NOT IR + XS (28.61.74.1)
          --YES--> COND FLLI TON (28.79.32.1)
        hex: RLL I E • M TGRS ON (28.79.54.1)      [uncertain: "RLL I E" -- the character after RLL is a plain stroke: I or 1]
          --YES--> GT IC FLD (28.79.64.1)
        hex: RLL I E • M TGRS ON (28.79.53.1)      [same text as the hexagon above; only the ALD number differs]
          --YES--> GT ICA 17 • 18 TO LA            (no ALD number printed in this box; text runs to the box edge)
        hex: RLLI E • USE ZR (28.79.53.1)
          --YES--> END EX ZR (28.79.63.1)
        hex: RLLI E • USE ZL (28.79.53.1)
          --YES--> END EX ZL (28.79.63.1)
        hex: DEC 4 E • USE ZL + FW TGR ON (28.79.15.1)
          --YES--> TOF ZL BLOK - SPND TGRS (28.99.51.1)
        hex: DEC 4E • USE ZR (28.79.15.1)
          --YES--> TOF ZR BLOK- SPND TGRS (28.99.51.1)
        junction dot; from it a horizontal line ("A-low line") runs right across the page -- see below
        the A-bus then turns left and ends in the top of:
        hex: ZOAL IR (28.61.74.1)
          --YES--> a new vertical line (verified at 400%: it is NOT joined to the A-bus above it) carrying:
            COND FLLI TOF (28.79.31.1)
            junction dot, then a horizontal line with three hexagons:
            hex: FLLI E TGR ON (28.79.33.1)
              --YES--> SET LA INT TAG (28.79.61.1)
            hex: FLLI E TGR ON • SBC (28.79.34.1)
              --(no label printed)--> LA LD E • M (38.03.01.1)       [prints 38]
              --(no label printed)--> SET LAAR E2 (15.01.01.1)
            hex: FLLI E • M TGRS ON (28.79.34.1)
              --YES--> its line runs down and then left to the junction dot at the SET LAAR E2 (15.01.01.1) box,
                       where it joins the exit line of "FLLI E TGR ON • SBC" (that line also has a dot at LA LD E • M above).

    A-low line (from the junction dot on the A-bus, i.e. still under the ZEDEC ~22... YES), left to right:
        hex: ZLXA (28.61.74.1)
          --NO  (printed, left side)--> hex: FLLI E TGR ON (28.79.33.1)
                                           --YES--> GT Z 0 - 17 TO MAB (28.79.64.1)
          --YES (printed, right side)--> hex: FLLI E • M TGRS ON (28.79.34.1)
                                           --YES--> COND IR FR I PAR ERR (28.79.62.1)
        hex: ~ZLNA • ZL ADR
             ~(IR+XS) • IRPT ENBLD
             (28.61.74.1)                       (bar over ZLNA; separate bar over "IR+XS")
          --YES--> hex: ZEDC ~28 • ZEDC ~29 (28.61.74.1)        (bars over the digits 28 and 29)
                     --YES (printed, left side)--> junction dot, two branches:
                           hex: FLLIE • M TGR ON • DF MASK ON • (28.79.32.1)     [text ends with a "•" as printed]
                             --YES--> COND LANOP FR ALARM (28.79.64.1)
                           hex: FLLIE E • M TGR ON (28.79.33.1)
                             --YES--> COND LA DF FR ALARM (28.79.62.1)
                     --NO (printed, right side)--> hex: FLLIE E • M TGR ON (28.79.34.1)
                             --YES--> COND LA DS NOP FR ALARM (28.79.64.1)
        hex: RLLI M • SAC (28.89.21.1)
          --YES--> SET FNS2 E (28.89.24.1 • 28.89.25.1)
        BLOCK TC SELECT EI GEN (28.86.55.1)
        COND I EXP TON CKT (28.87.64.1)

### [B] unconditional trunk (second drop; boxes attach directly to it)

        BLOCK XCL 4 TON (28.86.41.1)
        BLOCK BR INSTR FUN GEN CKT OP (28.61.72.1)
        PREP TO TOF BLOK- SPND TGRS (28.61.72.1)
        BLOCK LOP 4 TON (28.88.34.1)
        hex: BR + SIC-BR (28.61.72.1)
          --YES--> hex: LAMIE • LARCY MD (28.81.15.1)
                     --YES--> HOT 1 TO ABA 17 (28.96.41.1)
        hex: BI+SIC-BI (28.61.72.1)
          --YES--> a vertical line ("BI-bus") carrying, top to bottom:
            hex: E BOX IND (28.61.72.1)
              --YES--> hex: ~ZLXA • BROK (28.61.73.1)          (bar over ZLXA only)
                         --YES--> BLOCK SET OF LAOC 8 (28.97.04.1)
                         --YES (same line continues down into)--> hex: LOP 3 (28.88.25.1)
                                    --(no label printed)--> SET LAOC 5,6 (28.97.04.1)
                                    --(no label printed)--> SET LAOC WBC (28.97.06.1)
            hex: ~(E BOX IND) • ~BROK (28.61.72.1)             (bar over "E BOX IND"; separate bar over BROK)
              --YES--> SET LAOC 0,5 ON LOP 3 (28.88.25.1)
            COND EMF5 TON (28.70.21.1)
            hex: NOT EX MODE 28.22.02.1                        (ALD number printed without parentheses)
              --YES--> LAST XFER FW 21.04.06.1                 (ALD number printed without parentheses)
            COND RLLI TON (28.79.52.1)
            BLOCK LA IC TAG SET (28.79.53.1)                   (BI-bus ends here)
        hex: CNT1 E • COND 2 BLOK - SPND TGRS TOF (28.75.35.1)
          --YES--> TOF ZL BLOK- SPND TGRS (28.42.41.1)
        COND ROTC • Z 13 - 17 TO XAB GEN CKT (28.70.45.1)        (this box is printed heavier than its neighbours)
        COND ZL BLOK- SPND TGRS TOF (28.79.15.1 • 28.86.25.1 • 28.82.26.1)
        hex: LOP 3 • NOT BEW + SIC BEW (28.88.27.1)
          --YES--> line runs down to a junction dot on the YES exit of the next hexagon, then on to END EX FR ZL
        hex: IF INHBT • LOP 4 (28.88.35.1)
          --YES--> (junction dot with the line from the hexagon above) --> END EX FR ZL (28.99.54.1)
        (trunk ends in the top of:)
        hex: NOT BD + BEW + SIC-BD-BEW • LOP 5 (28.88.45.1)
          --YES--> TOF ZL BLOK- SPND TGRS (28.99.51.1)

   "SET LAOC 5,6" and "SET LAOC 0,5": the separator prints as a low dot/comma (could be "5.6" / "0.5").

### [C] third drop

    hex: ZEDEC 25 •
         ZEDEC ~26 • ~27 • 28
         (28.61.71.1)                    (bars over 26 and 27 only; 25 and 28 unbarred)
      --YES--> COND LOP 3 TON (28.88.21.1)
      --YES--> COND ICLI TON (28.84.11.1)
      --YES--> BLOCK LAOC 9 ON LOP 3 (28.88.26.1)
      --YES--> GT ZR J FLD TO LA ON LOP 3 (28.88.25.1)
      --YES (same line continues down into)--> hex: LOP 3 • USE ZL (28.88.25.1)
                 --YES--> GT Z 18 - 23 TO XAB (28.95.11.1)
                 --YES--> ZXAB TO LAOC (28.97.03.1)

### [D/E] fourth drop

    hex: Z 55 • ~58 • ~56 •
         ~57 • ~59
         (28.22.80.1)
      --YES--> a vertical line ("Z55-bus"). Items are attached on both sides of it. In top-to-bottom order of their junctions:
        (right) COND VFL 1E TON 28.11.11.1                        (ALD number printed without parentheses)
        (left)  hex: CYC PRE YFL 5 COMP (28.20.21.1)              [prints "YFL"; uncertain: VFL?]
                  --YES--> COND INSTR CHK ENBLD GEN CKTS (28.41.50.1)
        (right) hex: Z ~52 • Z ~53 • Z ~54 • Z 51 (28.22.80.1)    (bars over the digits 52, 53, 54)
                  --YES--> a vertical line carrying:
                    hex: VFL 5 (28.24.20.1)
                      --YES--> SET LAOC POS O (36.09.03.1)        [last character is O or 0]
                    hex: VFL 5 (28.11.55.1)
                      --YES--> COND STORE WAIT (28.21.71.1)
                    (line continues down into:)
                    hex: ZR 0 - 31 + ZR NON EXIST (28.22.80.1)
                      --YES--> line runs down to a junction dot on the YES exit of "~(Z 51) • ~(Z 52) • ~(Z 53)" below,
                               then on to COND SET LA AD (28.25.20.1)
        (left)  hex: VFL 5E TGR ON (28.11.52.1)
                  --YES--> VFL 5 1 TO ICIB 3 - 8 (28.21.20.1)
                  --YES--> Z 0 - 23 TO Z ICIB (28.21.61.1)
        (left, directly on the bus through a short stub with two dots)
                COND VFL 5 TI (28.11.51.1)
                COND VFL 5 I CHK PAR GEN CKT (28.11.53.1)
                COND TI LD GEN CKTS (28.11.54.1)
        (left)  hex: VFL I ON (28.11.12.1)
                  --YES--> VFL I E I TO ICIB P POS 2,6 (28.21.20.1)
                  --YES--> VFL I Z 12 - 18 TO Z ICIB 32 - 38 (25.03.01.1)
        (right) hex: ~(Z 51) • ~(Z 52) • ~(Z 53) (28.22.80.1)     (three separate bars, each over "Z nn")
                  --YES--> (junction dot with the line from "ZR 0 - 31 + ZR NON EXIST") --> COND SET LA AD (28.25.20.1)
        (right) hex: ~(Z 12 LD) • ~(Z 13 LD) (28.22.80.1)
                  --YES--> hex: IO • GT ZROC TO LAOC (28.24.25.1)
                             --YES--> SET LAOC POS 7              (no ALD number printed in this box)
        (left)  junction feeding two hexagons:
                hex: Z 53 • Z 51 (28.22.80.1)
                  --YES--> line runs down past a junction dot on the YES exit of the next hexagon and a junction dot
                           at BLOCK OP SET LANOP GEN (28.25.10.1); below that box the line continues and ENDS ON
                           (touches, no dot) the horizontal line that runs from the Z55-bus to the VFL I M ON hexagon.
                hex: Z 51 • ~(Z 53) •
                     Z 52 • ~(Z 54)
                     (28.22.80.1)
                  --YES--> (junction dot on the line above) --> BLOCK OP SET LANOP GEN (28.25.10.1)
        (right) hex: MCP PROTECT
                     IRPT ENABLED
                     + Z51 • Z53
                     + Z51 • ~(Z53) • Z52 • ~(Z54)
                     (28.22.80.1)
                  --YES--> VFL + 1-0 OP CODE INVALID 28.22.80.1   (ALD number printed without parentheses)
        (left)  hex: VFL I M ON (28.11.12.1)
                  --YES--> VFL I COND VFL 5 (28.11.42.1)
        (left)  COND VFL I TON (28.11.11.1)
        (left)  SET LAOC POS 5 (36.09.08.1)                       (Z55-bus ends here)

### [F/G] fifth (rightmost) drop

    hex: Z59                              (no ALD number printed)
      --YES--> a vertical line ("Z59-bus") and, continuing right from the same exit, the top of hex Z56 (see [G]).
      On the Z59-bus, top to bottom:
        COND VFLI TON (28.11.11.1)
        hex: VFL I E TGR ON (28.11.12.1)
          --YES--> Z 50 • P5O TC Z ICIB 18 • P2 (28.79.63.1)      [prints "P5O TC"; uncertain: P50 TO?]
        hex: VFL I E TGR ON • ~IMM (28.11.12.1)                   (bar over IMM)
          --YES--> 1 TO ICIB P POS 5 (28.21.20.1)
          --YES--> Z 18 - 23 TO Z ICIB 50 - 55 (28.79.65.1)
        hex: XOFIE • W + ZL NOT
             EQ I Z VFL CL 2 • CYC
             PREC VFL 3 COMP +
             VFL 3 + 4 WBC • CYC
             PREC VFL 4 COMP +
             WBC 4 • CYC PREC
             VFL 5 COMP
             (28.12.12.1)                                          (no bars; line breaks as printed)
          --YES--> W 13 - 17 • P TO XAB (28.86.56.1)
        hex: WBC • W NON
             EXIST + ZOAL •
             NON EXIST •
             ~VFL5 • ~IMM
             (28.22.60.1)                                          (bar over VFL5; separate bar over IMM)
          --YES--> COND SET LAAD (28.25.20.1)
        hex: W + ZL NOT EQ 1
             E • VFL CL 2 + CYC
             PREC VFL COMP •
             VFL 3 + 4 WBC + CYC
             PREC VFL 4 COMP •
             WBC 4 + CYC PREC
             VFL 5 COMP
             (28.12.12.1)                                          (no bars; line 3 reads "PREC VFL COMP" with no digit)
          --YES--> Z 13 - 17 • P TO XAB (28.86.56.1)
        (bus ends in the top of:)
        hex: W + ZL EQI • (28.12.12.1)                             [text ends with a "•" as printed]
          --YES--> hex: XOF I E (28.12.12.1)
                     --YES--> XOFI TC FTH (24.00.09.1)             [a blot sits on the second group: 24.00.09.1?]

### [G] under Z59 YES

    hex: Z56 28.22.02.1                   (ALD number printed without parentheses)
      --YES--> a vertical line ("Z56-bus") carrying:
        hex: Z 55 • ~58 • ~53 • ~57 • Z 53 + 54 + 57 (28.22.03.1)      (third term re-checked at 800%: reads 53, barred)
          --YES--> VFL CL 3 (28.22.03.1)
        hex: Z 53 + 54 + 57 • 55 • ~58 (28.22.03.1)
          --YES--> VFL CL I (28.22.03.1)                           [last character a plain stroke: I or 1]
        hex: IMM • Z 54 + 57 + ~58 • 55 (28.22.03.1)               (IMM unbarred here)
          --YES--> VFL OP CODE INVD (28.22.03.1)
        hex: Z 54 + 57 + ~58 • Z 55 • ~IMM (28.22.03.1)
          --YES--> VFL CL 2 (28.22.03.1)
        hex: Z 57 • 55 • 58 (28.22.03.1)                           (no bars)
          --YES--> VFL OP CODE INVD (28.22.03.1)
        hex: Z 55 • 58 • ~57 (28.22.03.1)
          --YES--> VFL CL 5 (28.22.03.1)
        hex: ~(Z 55) • Z 58 • ~54 • ~57 (28.22.03.1)
          --YES--> VFL CL 3 MULTICND (28.22.03.1)
        (bus ends in the top of:)
        hex: Z 54 • 55 • ~53 • ~57 • ~58 (28.22.03.1)
          --YES--> VFL CL 4 (28.22.03.1)
          --YES (same line continues down into)--> hex: ~(Z 53) (28.22.03.1)
                     --YES--> MULTIPLICAND (28.22.03.1)
      --(second, unlabelled exit from the LEFT point of the Z56 hexagon; a line runs down the whole page to:)-->
        hex: Z 55 + 57 • + ~(54 • 58) (28.22.03.1)                 (one bar spanning "54 • 58"; the "• +" is as printed)
          --YES--> VFL CL 1 (28.22.03.1)

    Isolated hexagon (between MULTIPLICAND and the bottom hexagon): NO input line is drawn to it.
        hex: Z 54 • 58 • ~55 • ~57 (28.22.03.1)
          --YES--> VFL CL 3 TRANSIT ADR (28.22.03.1)

### Noted (Fig 3.1.27)

- "BB SIG TO SLLI STORE LEVEL LALD OUT CKTS (28.79.43.1)"
- "COND XSFI TON CKT (28.70.41.1)"; "COND XSFI TOF CKT (28.70.43.1)"
- "ZL ADR NOT IR + XS (28.61.74.1)"; "~ZLNA • ZL ADR ~(IR+XS) • IRPT ENBLD (28.61.74.1)"; "ZOAL IR (28.61.74.1)"
- "COND IR FR I PAR ERR (28.79.62.1)"
- "BLOCK XCL 4 TON (28.86.41.1)"
- "BLOCK BR INSTR FUN GEN CKT OP (28.61.72.1)"; "BR + SIC-BR (28.61.72.1)"; "BI+SIC-BI (28.61.72.1)"
- "PREP TO TOF BLOK- SPND TGRS (28.61.72.1)"; "CNT1 E • COND 2 BLOK - SPND TGRS TOF (28.75.35.1)";
  "TOF ZL BLOK- SPND TGRS (28.42.41.1)"; "COND ZL BLOK- SPND TGRS TOF (28.79.15.1 • 28.86.25.1 • 28.82.26.1)";
  "TOF ZL BLOK - SPND TGRS (28.99.51.1)" (two boxes: under DEC 4 E • USE ZL + FW TGR ON, under NOT BD + BEW + SIC-BD-BEW • LOP 5);
  "TOF ZR BLOK- SPND TGRS (28.99.51.1)"
- "BLOCK LOP 4 TON (28.88.34.1)"; "COND LOP 3 TON (28.88.21.1)"; "BLOCK LAOC 9 ON LOP 3 (28.88.26.1)";
  "GT ZR J FLD TO LA ON LOP 3 (28.88.25.1)"; "LOP 3 • USE ZL (28.88.25.1)"; "LOP 3 (28.88.25.1)";
  "LOP 3 • NOT BEW + SIC BEW (28.88.27.1)"; "IF INHBT • LOP 4 (28.88.35.1)"; "NOT BD + BEW + SIC-BD-BEW • LOP 5 (28.88.45.1)"
- "GT Z 18 - 23 TO XAB (28.95.11.1)"; "ZXAB TO LAOC (28.97.03.1)"; "COND ROTC • Z 13 - 17 TO XAB GEN CKT (28.70.45.1)";
  "W 13 - 17 • P TO XAB (28.86.56.1)"; "Z 13 - 17 • P TO XAB (28.86.56.1)"
- "BLOCK SET OF LAOC 8 (28.97.04.1)"; "SET LAOC 5,6 (28.97.04.1)"; "SET LAOC WBC (28.97.06.1)"; "SET LAOC 0,5 ON LOP 3 (28.88.25.1)";
  "SET LAOC POS O (36.09.03.1)"; "SET LAOC POS 7"; "SET LAOC POS 5 (36.09.08.1)"; "IO • GT ZROC TO LAOC (28.24.25.1)"
- "E BOX IND (28.61.72.1)"; "~(E BOX IND) • ~BROK (28.61.72.1)"; "~ZLXA • BROK (28.61.73.1)"; "ZLXA (28.61.74.1)"
- "HOT 1 TO ABA 17 (28.96.41.1)"; "LAMIE • LARCY MD (28.81.15.1)"
- "COND STORE WAIT (28.21.71.1)" (under VFL 5 (28.11.55.1), under Z ~52 • Z ~53 • Z ~54 • Z 51, under Z 55 • ~58 • ~56 • ~57 • ~59)
- "COND SET LA AD (28.25.20.1)"; "COND SET LAAD (28.25.20.1)"; "SET LA INT TAG (28.79.61.1)"; "BLOCK LA IC TAG SET (28.79.53.1)"
- "LA LD E • M (38.03.01.1)"; "SET LAAR E2 (15.01.01.1)"
- "BLOCK OP SET LANOP GEN (28.25.10.1)"; "COND LANOP FR ALARM (28.79.64.1)"; "COND LA DS NOP FR ALARM (28.79.64.1)"; "COND LA DF FR ALARM (28.79.62.1)"
- "GT IC FLD (28.79.64.1)"; "GT ICA 17 • 18 TO LA"; "GT Z 0 - 17 TO MAB (28.79.64.1)"; "END EX ZR (28.79.63.1)"; "END EX ZL (28.79.63.1)"; "END EX FR ZL (28.99.54.1)"
- "COND FLLI TON (28.79.32.1)"; "COND FLLI TOF (28.79.31.1)"; "COND RLLI TON (28.79.52.1)"; "RLLI M • SAC (28.89.21.1)"; "SET FNS2 E (28.89.24.1 • 28.89.25.1)"
- "MCP PROTECT IRPT ENABLED + Z51 • Z53 + Z51 • ~(Z53) • Z52 • ~(Z54) (28.22.80.1)"; "VFL + 1-0 OP CODE INVALID 28.22.80.1"
- "COND I EXP TON CKT (28.87.64.1)"; "BLOCK TC SELECT EI GEN (28.86.55.1)"; "XOFI TC FTH (24.00.09.1)"; "XOF I E (28.12.12.1)"
- "LAST XFER FW 21.04.06.1"; "NOT EX MODE 28.22.02.1"; "COND EMF5 TON (28.70.21.1)"
- "WBC • W NON EXIST + ZOAL • NON EXIST • ~VFL5 • ~IMM (28.22.60.1)"; "ZR 0 - 31 + ZR NON EXIST (28.22.80.1)"
- "COND INSTR CHK ENBLD GEN CKTS (28.41.50.1)"

### Not read with confidence (Fig 3.1.27)

- Z56-bus first hexagon: third term reads "~53" at 800% (so the hexagon as printed contains both ~53 and Z 53); flagged because it looks self-contradictory, not because the digit is unclear.
- "RLL I E • M TGRS ON" (two hexagons, 28.79.54.1 and 28.79.53.1): I vs 1 not distinguishable; same for "VFL I ...", "VFL CL I", "W + ZL EQI", "EQ I Z", "NOT EQ 1 E", "VFL 5 1 TO ICIB 3 - 8", "COND VFLI TON" vs "COND VFL I TON", "COND VFL 1E TON".
- "CYC PRE YFL 5 COMP" (prints Y); "Z 50 • P5O TC Z ICIB 18 • P2" (O/0 and C/O); "SET LAOC POS O".
- "SET LAOC 5,6" / "SET LAOC 0,5" / "P POS 2,6": comma or period.
- Junction under BLOCK OP SET LANOP GEN: the Z 53 • Z 51 YES line runs on to touch (no dot) the bus-to-VFL I M ON horizontal. Whether that is an intended connection is not determinable from the page.
- Hexagon "Z 54 • 58 • ~55 • ~57" -> VFL CL 3 TRANSIT ADR has no input line drawn.
- Bar assignment for rules that print between two text lines (all hexagons with two-line bit lists): assigned to the lower line's term; lengths agree, but a second reader should confirm "ZEDEC 25" (unbarred) and "Z 55" (unbarred) in particular.
- "Z 55 + 57 • + ~(54 • 58)": bar read as spanning "54 • 58"; it could be two touching bars.
- XOFI TC FTH ALD number has a blot on "00".
- Exit labels: LOP 3 (28.88.25.1) and FLLI E TGR ON • SBC (28.79.34.1) have no YES printed; the left exit of Z56 has no label printed.

---

## FIGURE 3.1.25. FW NOT S TRIGGER

- PDF page 89. Caption as printed: "FIGURE 3.1.25. FW NOT S TRIGGER"
- Page tag: 1-51/1-52. Date: 2/1/62. Running heads: "M3-04-3", "I UNIT FLOW DIAGRAMS".
- Applicability note printed: "CPU 7101 / SER. NO. 30,004 / AND HIGHER"

### Turn-on and bar

Two turn-on hexagons side by side; both exits are labelled YES and join on one line that enters the bar through "TON":

    hex (left):  SBC • FW NOTS
                 IY • YR-ZL E FW
                 (28.26.60.1)                 ["NOTS" printed as one word; "IY" first character a plain stroke: I or 1]
      --YES--> TON
    hex (right): YR-ZL E FW • FW
                 NOT S 2Y • SBC
                 (28.26.60.1)
      --YES--> TON

    Bar: FW NOT S TGR (28.26.60.1)       (no E / M output labels printed; one line leaves its bottom)

The output line meets a horizontal line with eight drops. Left to right:

### (1) far-left vertical line ("L-bus")

        hex: MOD ZR E (28.15.21.1)
          --YES--> Z 50 TO ABB P2 ADJ PAR Z 50-55 (28.96.08.1)
          --YES--> Z 32 TO 49 TO ABB 0 - 17 PREP (28.96.09.1)        [number smudged; 28.96.09.1?]
          --YES--> Z 50 TO ABB 18 PREP (28.96.09.1)
        hex: MOD ZR E • MOD ZR M (28.15.21.1)
          --YES--> GT AOB 18 TO ZR (28.27.51.1)
          --YES--> GT AOB 19 TO ZR (28.27.51.1)
        hex: XF + DEC ZL M (28.15.40.1)
          --YES--> COND MOD ZL TON CKT (28.15.40.1)
        hex: YL-ZR E • SBC (28.15.30.1)
          --YES--> TOF YR-ZL M TGR (28.15.30.1)
        hex: MOD ZR M (28.15.21.1)
          --YES--> [rectangle] MOD ZR • FW NOT S (28.15.80.1)
        (L-bus ends in the top of:)
        hex: MOD ZL E •
             PX Y • XF+DEC
             ZL M
             (28.15.42.1)
          --YES--> PREP GT Z 0 - 23 TO ICIB (28.79.65.1)
          --YES--> COND IDC FR I PAR ERR PREP (28.99.03.1)
          --YES--> TON PXYL TGR (28.78.34.1)
          --YES--> PREP SET ONE TO ICIB PAR (28.21.20.1)             ["ONE" prints broken, like "ONI"]
          --YES (same exit, horizontal line to the right)--> three hexagons:
              hex: MOD ZL M • CD 2Y-ZL (28.15.42.1)
                --YES--> COND ICOB TO 2Y 0 - 63 (28.44.16.1)         [a speck sits between "28" and "44"]
              hex: MOD ZL M • CD IY-ZL (28.15.42.1)
                --YES--> COND ICOB TO IY 0 - 63                       (no ALD number printed in this box)
              hex: ~(MOD ZL M) (28.15.42.1)                           (one bar over "MOD ZL M")
                --YES--> IP CHK PAR (28.98.07.1)
                --YES--> I CHK E • NM P (38.03.03.1)                  [prints 38; the "•" prints as a small open dot]

### (2)

        hex: NOT ZR MOD • YL-ZR M (28.15.12.1)
          --YES--> COND WBC + DEC TON CKT (28.15.80.1)
          --YES (same line continues down into)--> hex: ZR NOT FP CL • FW ST + FW NOT S (28.15.80.1)
                     --YES--> FW DEC RDY (28.51.24.1)

### (3) vertical line ("M-bus")

        hex: MOD ZL E • MOD ZL M (28.15.41.1)
          --YES--> GT AOB 18 TO ZL (28.27.50.1)
          --YES--> GT AOB 19 TO ZL (28.27.50.1)
          --YES--> GT AOB 24 TO ZL (28.27.50.1)                      [number smudged; 28.27.50.1?]
        hex: FW NOT FP CL •
             MOD ZR • FW NOT
             S+ FW CMP + YL-ZL•
             NOT MOD L + MOD
             ZL • FWS
             (28.15.80.1)                                             (no bars; print damaged on "FW NOT" of line 1 and "FW" of line 3)
          --YES--> FW DEC RDY (28.51.24.1)
        COND WBC + DEC TON CKT (28.15.80.1)
        COND YL-ZR TON CKT (28.15.10.1)
        (M-bus ends in the top of:)
        hex: IY29 + IY28 + IY30
             + IY31 • DEC MOD
             REQ FR IYL • ~IYLD
             ~BRC • ~UNCOND +
             ~(BIT BRCL IYL) + BIT
             BR ~(DEC I)
             (28.26.21.1)
            bars seen at 600%: over "IYLD"; over "BRC"; over "UNCOND"; one bar over "BIT BRCL IYL"; one bar over "DEC I".
            ("IY.." / "IYL" / "DEC I": first/last character a plain stroke, I or 1.)
          --YES--> COND ZR MOD R TON CKT (28.26.21.1)
          --YES--> COND ZL MOD R TON CKT (28.26.23.1)                 [a fold line runs through the first text line of this box]

### (4)

        hex: MOD ZL E • ~FW
             ~(ON BDS) + ~PROG ~IX
             (28.15.41.1)
            bars seen at 600%: over "FW" (line 1); one bar over "ON BDS"; a bar over "PROG"; a separate short bar over "IX".
          --YES--> Z 0 - 17 ABB PREP (28.96.03.1)
          --YES--> Z 18 ABB PREP (28.96.03.1)
          --YES--> Z 19 - 23 ABB PREP (28.96.07.1)

### (5) vertical line ("N-bus")

        hex: PROG IX (28.15.32.1)
          --YES--> BLOCK COND YL- ZR TON CKT (28.15.10.1)
          --YES--> BLOCK COND YR- ZR TON CKT (28.15.60.1)
        hex: XF + DEC ZL M (28.15.40.1)
          --YES--> COND MOD ZL TON CKT (28.15.40.1)
        COND XF + DEC TON CKT (28.15.50.1)
        BLOCK MOD ZL TON CKT (28.15.40.1)                             (N-bus ends here)

### (6) directly under the bar

        hex: 2Y29 + 2Y28 + 2Y30
             + 2Y31 • DEC MOD
             REQ FR 2YL • ~2YLD
             ~BRC • ~(BIT BR) ~(DEC 3)
             + ~(UNCOND + BIT)
             ~(BR CL 2YL)
             (28.26.25.1)
            bars seen at 600%: over "2YLD"; over "BRC"; one over "BIT BR"; one over "DEC 3"; one long bar over
            "UNCOND + BIT" (line 5, starting after the leading "+"); one bar over "BR CL 2YL" (line 6).
          --YES--> COND MOD L TON CKT (28.26.27.1)
          --YES--> COND MOD R TON CKT (28.26.25.1)

### (7) vertical line ("P-bus")

        hex: SBC • NOT MOD
             L REQ • I EX
             CMPL RST.
             (28.15.51.1)
          --YES--> TOF ZR WAS IHW TGR (28.15.51.1)
        BLOCK YR-ZR TON CKT (28.15.60.1)                              (P-bus ends here)

### (8) rightmost

        hex: PROG IY (28.15.41.1)
          --(no label printed)--> BLOCK Z 0 - 17 ABB PREP (28.15.41.1)
          --(no label printed)--> BLOCK Z 18 ABB PREP (28.15.41.1)
          --(no label printed)--> BLOCK Z18 TO ABB P2 ADJ PAR Z 18 - 23 (28.15.41.1)
          --(no label printed)--> BLOCK Z 19 - 23 ABB PREP (28.15.41.1)

### Noted (Fig 3.1.25)

- "MOD ZL E • ~FW ~(ON BDS) + ~PROG ~IX (28.15.41.1)"; "PROG IX (28.15.32.1)"; "PROG IY (28.15.41.1)"
- "XF + DEC ZL M (28.15.40.1)" (twice) -> "COND MOD ZL TON CKT (28.15.40.1)" (twice); "COND XF + DEC TON CKT (28.15.50.1)"; "BLOCK MOD ZL TON CKT (28.15.40.1)"
- "MOD ZL E • PX Y • XF+DEC ZL M (28.15.42.1)"; "MOD ZL M • CD 2Y-ZL (28.15.42.1)"; "MOD ZL M • CD IY-ZL (28.15.42.1)"; "~(MOD ZL M) (28.15.42.1)"; "MOD ZL E • MOD ZL M (28.15.41.1)"
- "MOD ZR E (28.15.21.1)"; "MOD ZR E • MOD ZR M (28.15.21.1)"; "MOD ZR M (28.15.21.1)"; "MOD ZR • FW NOT S (28.15.80.1)"; "NOT ZR MOD • YL-ZR M (28.15.12.1)"
- "2Y29 + 2Y28 + 2Y30 + 2Y31 • DEC MOD REQ FR 2YL • ~2YLD ~BRC • ~(BIT BR) ~(DEC 3) + ~(UNCOND + BIT) ~(BR CL 2YL) (28.26.25.1)"
- "IY29 + IY28 + IY30 + IY31 • DEC MOD REQ FR IYL • ~IYLD ~BRC • ~UNCOND + ~(BIT BRCL IYL) + BIT BR ~(DEC I) (28.26.21.1)"
- "COND MOD L TON CKT (28.26.27.1)"; "COND MOD R TON CKT (28.26.25.1)"; "COND ZR MOD R TON CKT (28.26.21.1)"; "COND ZL MOD R TON CKT (28.26.23.1)"
- "SBC • NOT MOD L REQ • I EX CMPL RST. (28.15.51.1)"; "TOF ZR WAS IHW TGR (28.15.51.1)"
- "FW NOT FP CL • MOD ZR • FW NOT S+ FW CMP + YL-ZL• NOT MOD L + MOD ZL • FWS (28.15.80.1)"
- "COND IDC FR I PAR ERR PREP (28.99.03.1)"
- "BLOCK COND YL- ZR TON CKT (28.15.10.1)"; "BLOCK COND YR- ZR TON CKT (28.15.60.1)"; "BLOCK YR-ZR TON CKT (28.15.60.1)"
- "BLOCK Z 0 - 17 ABB PREP (28.15.41.1)"; "BLOCK Z 18 ABB PREP (28.15.41.1)"; "BLOCK Z18 TO ABB P2 ADJ PAR Z 18 - 23 (28.15.41.1)"; "BLOCK Z 19 - 23 ABB PREP (28.15.41.1)"

### Not read with confidence (Fig 3.1.25)

- Grouping of the bars in the two long branch hexagons (2Y... 28.26.25.1 and IY... 28.26.21.1) and in "MOD ZL E • ~FW ~(ON BDS) + ~PROG ~IX": each bar segment is reported as seen; segments on adjacent lines may be one logical bar continued across the line break.
- I vs 1 throughout ("IY", "IY29", "IYL", "DEC I", "I EX", "CD IY-ZL").
- Smudged ALD numbers: Z 32 TO 49 TO ABB 0 - 17 PREP (28.96.09.1); GT AOB 24 TO ZL (28.27.50.1); COND ICOB TO 2Y 0 - 63 (28.44.16.1).
- I CHK E • NM P: leading "38" as printed (28?).
- PROG IY exit has no YES printed.

---

## FIGURE 3.1.26. FWS TRIGGER

- PDF page 90 (landscape; the left ~45% of the sheet is blank, so tile f90-L is empty). Read from my own 200% tiles of iu/p-090.png.
- Caption as printed: "FIGURE 3.1.26. FWS TRIGGER"
- Page tag: 1-53/1-54. Date: 2/1/62. Running heads: "M3-04-3", "I UNIT FLOW DIAGRAMS".
- Applicability note printed: "CPU 7101 / SER. NO. 30,004 / AND HIGHER"
- A vertical fold/crease line runs through the sheet (through the right end of the bar, the IY61 hexagon's YES exit,
  ZR NOT FP CL and FW DEC RDY); it is not a drawn line.

### Turn-on and bar

    hex (left):  FULL WORD IY •
                 YR - ZRE FW
                 (28.26.60.1)
      --YES--> TON
    hex (right): YR - ZRE FW •
                 FULL WORD 2Y
                 (28.26.60.1)
      --YES--> TON
    (both YES lines join on one line that enters the bar through "TON")

    Bar: FULL WORD S TGR (28.26.60.1)      (the caption calls it FWS TRIGGER; no E / M output labels printed)

The output line meets a horizontal line with six drops. Left to right:

### (1) far-left vertical line

        COND WBC + DEC ZE TON CKT (28.15.80.1)           [printed "COND WBC + DEC / ZE TON CKT"]
        hex: MOD ZL E •
             ~(FW ON BDS) +
             ~(PROG IY)
             (28.15.41.1)
            bars seen at 500%: one bar over "FW ON BDS"; one bar over "PROG IY".
          --YES--> Z 0 - 17 ABB PREP (28.96.03.1)
          --YES--> Z 18 ABB PREP (28.96.03.1)
          --YES--> Z 19 - 23 ABB PREP (28.96.07.1)
        hex: MOD ZL E • MOD ZL M (28.15.41.1)
          --YES--> GT AOB 18 TO ZL (28.27.50.1)
          --YES--> GT AOB 19 TO ZL (28.27.50.1)
          --YES--> GT AOB 24 TO ZL (28.27.50.1)
        (line ends in the top of:)
        hex: PROG IX (28.15.41.1)
          --YES--> a horizontal line with three hexagons:
              hex: ZL FP CL • MOD ZLE                    (no ALD number printed in this hexagon)
                --YES--> Z 0 - 17 ABB PREP (28.96.03.1)
              hex: MOD ZLE • ZL IHW (28.15.41.1)
                --YES--> Z 18 TO ABB P2 ADJ PAR Z 18 - 23 (28.96.07.1)
                --YES--> Z 18 ABB PREP (28.96.03.1)       [a speck sits between "96" and "03"]
                --YES--> Z 0 - 17 ABB PREP (28.96.03.1)
              hex: FW S + NOT S• MOD ZL E (28.15.41.1)
                --YES--> Z 0 - 17 ABB PREP (28.96.03.1)
                --YES--> Z 18 ABB PREP (28.96.03.1)
                --YES--> Z 19 - 23 ABB PREP (28.96.07.1)

### (2) second vertical line

        hex: MOD ZRE • MOD ZR M (28.15.21.1)
          --YES--> GT AOB 18 TO ZR (28.27.51.1)
          --YES--> GT AOB 19 TO ZR (28.27.51.1)
        COND YL-ZL TON CKT (28.15.70.1)                   (line ends here)

### (3)

        hex: MOD ZR E (28.15.21.1)
          --YES--> Z 50 TO ABB P2 ADJ PAR Z 50 - 55 (28.96.08.1)
          --YES--> Z 32 - 49 ABB 0 - 17 PREP (28.96.09.1)
          --YES--> Z 50 TO ABB 18 PREP (28.96.09.1)

### (4) a vertical line that runs down, turns right, and ends in the top of:

        hex: MOD ZL M (28.15.41.1)
          --YES--> hex: ZR NOT FP CL • FW S + FW NOT S (28.15.80.1)
                     --YES--> FW DEC RDY (28.51.24.1)       [crease through the first characters; "FW" and "(28" partly hidden]

### (5) just right of the bar's output

        hex: IY61 + IY60 +
             IY62 + IY63 •
             DEC MOD REQ
             FR IYR • ~IYRD
             ~BRC • ~UNCOND
             ~(+ BIT BR CL IYR) +
             ~(BIT BR DEC) 2
             (28.26.23.1)
            bars seen at 500%: over "IYRD"; over "BRC"; over "UNCOND"; one long bar over line 6 from its leading "+"
            to the end of "IYR"; one bar over line 7 covering "BIT BR DEC" and stopping short of the "2".
          --YES--> COND ZL MOD R TON CKT (28.26.23.1)
          --YES--> COND ZR MOD R TON CKT (28.26.21.1)

### (6) rightmost

        hex: 2Y61 + 2Y60 + 2Y62
             + 2Y63 • DEC MOD
             REQ FR 2Y • ~2YRD
             ~BRC • ~(UNCND + BIT)
             ~(BR CL 2YR) + ~(BIT BR)
             ~DEC Z
             (28.26.27.1)
            bars seen at 500%: over "2YRD"; over "BRC"; one long bar over "UNCND + BIT"; one bar over "BR CL 2YR";
            one bar over "BIT BR"; one bar over "DEC" (not over the following character).
            The last character of line 6 prints as "Z" [uncertain: Z? or 2 -- the matching IY hexagon has "DEC 2"].
          --YES--> junction dot, two hexagons:
              hex: YR-ZLE • SBC (28.26.27.1)
                --YES--> SET MOD L TGR (28.26.23.1)
              hex: YR-ZRE • SBC (28.26.25.1)
                --YES--> SET MOD R TGR (28.26.25.1)

### Noted (Fig 3.1.26)

- "MOD ZL E • ~(FW ON BDS) + ~(PROG IY) (28.15.41.1)"; "PROG IX (28.15.41.1)"
- "IY61 + IY60 + IY62 + IY63 • DEC MOD REQ FR IYR • ~IYRD ~BRC • ~UNCOND ~(+ BIT BR CL IYR) + ~(BIT BR DEC) 2 (28.26.23.1)"
- "2Y61 + 2Y60 + 2Y62 + 2Y63 • DEC MOD REQ FR 2Y • ~2YRD ~BRC • ~(UNCND + BIT) ~(BR CL 2YR) + ~(BIT BR) ~DEC Z (28.26.27.1)"
- "COND ZL MOD R TON CKT (28.26.23.1)"; "COND ZR MOD R TON CKT (28.26.21.1)"; "SET MOD L TGR (28.26.23.1)"; "SET MOD R TGR (28.26.25.1)"
- "MOD ZL E • MOD ZL M (28.15.41.1)"; "MOD ZL M (28.15.41.1)"; "MOD ZLE • ZL IHW (28.15.41.1)"; "ZL FP CL • MOD ZLE"; "FW S + NOT S• MOD ZL E (28.15.41.1)"
- "MOD ZR E (28.15.21.1)"; "MOD ZRE • MOD ZR M (28.15.21.1)"
- "COND WBC + DEC ZE TON CKT (28.15.80.1)"

### Not read with confidence (Fig 3.1.26)

- Bar grouping in the IY61 / 2Y61 hexagons (segments reported as seen; adjacent-line segments may be one logical bar).
- "DEC Z" vs "DEC 2" in the 2Y61 hexagon.
- I vs 1 ("IY", "IY61", "IYR", "IYRD"); "PROG IX" here prints with a blotted first letter (IX read).
- "COND WBC + DEC ZE TON CKT": "ZE" as printed.
- FW DEC RDY number partly under the crease: (28.51.24.1) read.

---

## FIGURE 3.1.24. WBC TRIGGER

- PDF page 88. Caption as printed: "FIGURE 3.1.24. WBC TRIGGER"
- Page tag: 1-49/1-50. Date: 2/1/62. Running heads: "M3-04-3", "I UNIT FLOW DIAGRAMS" (same layout as the other pages; read on the page thumbnail, not re-zoomed).
- Applicability note printed: "CPU 7101 / SER. NO. 30,004 / AND HIGHER"

### Turn-on and bar

    hex: SAR WBC
         TEST E • M • WRD
         BNDRY X OVER
         (28.22.02.1)                   [the two "•" in line 2 print as small open dots]
      --YES--> TON --> bar
    Bar: WORD BOUNDRY CROSSOVER TGR (28.22.02.1)     (spelled BOUNDRY as printed; no E / M output labels printed)

The output line meets a horizontal line with five drops. Left to right: bus A, bus B, a hexagon, bus C (directly under the bar), a hexagon.

### Bus A (far-left vertical line; boxes attach directly)

        BLOCK GEN COND VFL 4T (28.22.20.1)
        BLOCK GEN VFL 5T (28.22.20.1)
        BLOCK GEN ZL EXT NOT WBC (28.22.20.1)
        BLOCK GEN ZL INT NOT WBC (28.22.20.1)
        BLOCK GEN COND VFL 4 T3                        (no ALD number printed in this box)
        BLOCK GEN VFL CL 1 DIR COND LA IF TAG (28.22.20.1)
        BLOCK GEN VFL 5 T3 (28.22.20.1)
        BLOCK GEN COND VFL 5 T3 (28.22.20.1)
        BLOCK GEN OF 3 LEVEL INSTR (28.22.10.1)
        BLOCK SET OF LAOC POS 6 (36.09.09.1)           [a speck sits in the number; a smear band crosses the page just below this box]
        BLOCK GEN OF VFL 5 T3 CL 1 + 2 • WBC (28.22.10.1)
        (bus A ends in the top of:)
        hex: VFL CL 2 +
             VFL CL 3 + VFL
             CL 4 • ~WBC •
             ~(VFL CL 2)
             (28.22.10.1)
            bars seen at 400%: over "WBC" (line 3); one bar over "VFL CL 2" (line 4). The last letter of line 2 prints like "VFI".
          --YES--> a vertical line carrying:
            hex: VFL 4 TYPE 3 + VFL 4 TYPE 2 (28.22.50.1)
              --YES--> hex: VFL 4 E ON (28.11.42.1)
                         --YES--> W 0-17 TO MAB (28.21.61.1)
            hex: CYC PREC VFL 4 COMP (28.12.12.1)
              --YES--> hex: VFL • W + ZL
                            EQ 1 • XOFI
                            E
                            (28.12.12.1)
                         --YES--> W 13-17 • P TO XAB (28.86.56.1)
            hex: VFL I M TGR ON (28.11.12.1)                [I or 1]
              --YES--> VFL 1 COND VFL 3 (28.11.22.1)
            COND VFL 4 TYPE 2 + 3 (28.11.42.1)              (line ends here)

### Bus B (second vertical line; each junction feeds a hexagon)

        hex: VFL 4 E (28.24.25.1)
          --YES--> SET LOAC POS 8 (36.09.11.1)              [prints "LOAC"]
        hex: GT ZROC TO LOAC (28.24.80.1)                   [prints "LOAC"]
          --YES--> SET LA WBC TAG (36.06.01.1)
        hex: W EQ 11 + 12 + 16 - 31 (28.11.55.1)
          --YES--> hex: VFL CL 2 • VFL 5E (28.11.55.1)
                     --YES--> VFL 5 CL 2 COND STORE WAIT (28.21.71.1)
        hex: W EQ XS (28.22.20.1)
          --YES--> COND VFL 4 T (28.22.21.1)
          --YES (same line continues down into)--> hex: VFL CL 1 • DIR (28.22.20.1)
                     --YES--> VFL 5 TYPE 1B (28.22.40.1 • 28.11.52.1 • 28.12.11.1)     [text crowds the box border; last number 28.12.11.1?]
        hex: W EXIST NON EXIST (28.22.20.1)
          --YES--> COND VFL 4 T2 (28.22.21.1)
          --YES (same line continues down into)--> hex: VFL [uncertain: C1 1? = CL 1] • [uncertain: DI2? = DIR; a fold line runs through this word] (28.22.20.1)
                     --YES--> VFL 5 T2 (28.22.20.1)
        (bus B ends in the top of:)
        hex: W EQ INT (28.22.20.1)
          --YES--> COND VFL 4 T3 (28.22.21.1)
          --YES (same line continues down into)--> hex: VFL CL 1 • DIR (28.22.20.1)
                     --YES--> VFL CL 1 DIR COND LA IF TAG (28.24.48.1)
                     --YES--> VFL 5 TY 3 (28.22.20.1)

### Third drop

        hex: ~(VFL CL 5 • IO)
             ~(• VFL + IO OP CODE)
             ~INV
             (28.22.10.1)
            bars seen at 400%: a rule above line 1 from its start to about the end of "IO"; a rule above line 2 across its
            whole width; a short bar over "INV". (Probably one bar over the whole expression continued over three lines;
            reported as seen.)
          --YES--> BLOCK GEN OF VFL 1 COND VFL 5 (28.11.12.1)

### Bus C (vertical line directly under the bar)

        hex: CYL PREC VFL 5 COMP (28.12.12.1)                [prints "CYL"]
          --YES--> junction dot, two branches:
                BLOCK GTING OF Z 13-17 • P TO XAB (28.86.56.1)
                hex: VFL • W +
                     ZL EQ 1 • XOFI
                     (28.12.12.1)                             [first "•" prints as a small open dot]
                  --YES--> W 13 - 17 • P TO XAB (28.86.56.1)
        hex: W NON EXIST (28.22.60.1)
          --YES--> hex: Z 59 • Z
                        FW • ~(VFL CL
                        5) • IMM
                        (28.22.60.1)
                      bars seen at 400%: one bar over "VFL CL" (line 2) and a short bar over "5" (line 3); IMM unbarred.
                     --YES--> line runs down and left to the junction dot at the VFL AD INHIB box (see next hexagon)
        hex: W EQ 1 • VFL CL 2 (28.22.60.1)
          --YES--> VFL AD INHIB (28.22.60.1)        (junction dot here; the Z 59 ... YES line joins at this dot)
          --YES--> VFL COND SET LAAD (28.22.60.1)
        hex: ZL 11 + 12 + 16 - 31 (28.11.55.1)
          --YES--> hex: VFL C2 • VFL 5E (28.11.55.1)          [prints "C2"]
                     --YES--> VFL 5 CL 2 COND STORE WAIT (28.21.71.1)
        hex: VFL CL 1 (28.22.10.1)
          --YES--> 3 LEVEL INSTR (28.11.12.1)
        (bus C ends in the top of:)
        hex: W EQ 1 + 2 + 3 (28.22.70.1)                      [a fold line runs through line 1]
          --YES--> junction dot, two hexagons:
              hex: VFL CL 2 • IRPT ENBLD (28.22.70.1)
                --YES--> VFL COND SET LA DS (28 [number not completed in the print: only "(28" is printed])
              hex: VFL CL 1 + VFL CL 3 + VFL CL 4 • IRPT ENBLD (28.22.70.1)
                --YES--> VFL COND SET LA DF (28.25.30.1)

### Fifth (rightmost) drop

        hex: W NON EXIST (28.20.50.1)                         [uncertain: second group 20 or 22]
          --YES--> a horizontal line with three hexagons:
              hex: COND VFL 3 T2 (28.22.50.1)
                --YES--> VFL 3 T2 • MNT MODE + NON EXIST (28.24.81.1)
              hex: VFL 4 T2 (28.22.50.1)
                --YES--> VFL 4 T2 MNT MODE + NON EXIST (28.24.81.1)        (no "•" printed in this box)
              hex: VFL 5 T2 (28.20.50.1)                      [uncertain: second group 20 or 22]
                --YES--> VFL 5 T2 • MNT MODE + NON EXIST (28.24.81.1)

### Noted (Fig 3.1.24)

- "VFL 5 CL 2 COND STORE WAIT (28.21.71.1)" -- two boxes: under "W EQ 11 + 12 + 16 - 31 (28.11.55.1)" -> "VFL CL 2 • VFL 5E (28.11.55.1)", and under "ZL 11 + 12 + 16 - 31 (28.11.55.1)" -> "VFL C2 • VFL 5E (28.11.55.1)"
- "W EQ XS (28.22.20.1)"; "W EQ INT (28.22.20.1)"; "BLOCK GEN ZL EXT NOT WBC (28.22.20.1)"; "BLOCK GEN ZL INT NOT WBC (28.22.20.1)"
- "W 13-17 • P TO XAB (28.86.56.1)" (two boxes); "BLOCK GTING OF Z 13-17 • P TO XAB (28.86.56.1)"
- "VFL • W + ZL EQ 1 • XOFI E (28.12.12.1)"; "VFL • W + ZL EQ 1 • XOFI (28.12.12.1)"
- "BLOCK SET OF LAOC POS 6 (36.09.09.1)"; "SET LOAC POS 8 (36.09.11.1)"; "GT ZROC TO LOAC (28.24.80.1)"; "SET LA WBC TAG (36.06.01.1)"
- "BLOCK GEN VFL CL 1 DIR COND LA IF TAG (28.22.20.1)"; "VFL CL 1 DIR COND LA IF TAG (28.24.48.1)"
- "VFL COND SET LAAD (28.22.60.1)"; "VFL COND SET LA DS (28"; "VFL COND SET LA DF (28.25.30.1)"; "VFL AD INHIB (28.22.60.1)"
- "VFL CL 2 • IRPT ENBLD (28.22.70.1)"; "VFL CL 1 + VFL CL 3 + VFL CL 4 • IRPT ENBLD (28.22.70.1)"
- "W 0-17 TO MAB (28.21.61.1)"
- All "BLOCK ..." boxes of bus A (listed above).

### Not read with confidence (Fig 3.1.24)

- Bar extents in "~(VFL CL 5 • IO) ~(• VFL + IO OP CODE) ~INV" and in "Z 59 • Z FW • ~(VFL CL 5) • IMM".
- "VFL C1 1 • DI2" (fold line; likely the same text as the two "VFL CL 1 • DIR" hexagons, but printed/damaged differently).
- "W NON EXIST (28.20.50.1)" and "VFL 5 T2 (28.20.50.1)": 20 vs 22.
- VFL 5 TYPE 1B triple number: last number partly on the box border.
- VFL COND SET LA DS: ALD number incomplete on the page.
- 1 vs I in "VFL I M TGR ON", "VFL 1 COND VFL 3", "EQ 1".

---

## FIGURE 3.1.22. ZL IHW TRIGGER, ZR WAS IHW TRIGGER, 1 BIT MOD TRIGGER, AND FP Z ALT TRIGGER

- PDF page 86. Caption as printed (three lines): "FIGURE 3.1.22. ZL IHW TRIGGER, ZR WAS / IHW TRIGGER, 1 BIT MOD / TRIGGER, AND FP Z ALT TRIGGER"
- Page tag: 1-45/1-46. Date: 2/1/62. Running heads: "M3-04-3", "I UNIT FLOW DIAGRAMS".
- Applicability note printed: "CPU 7101 / SER. NO. 30,004 / AND HIGHER"
- Four separate trigger bars on the page.

### A. ZL IHW TGR (top of page)

    hex: SBC • CD 1Y-ZL •
         HW CL 1Y • ~(FW NOT
         S 1Y) + CD 2Y-ZL • HW
         CL 2Y • FW NOT S 2Y •
         YR-ZL E
         (28.26.61.1)
        bars seen at 400%: one bar over "FW NOT" at the end of line 2 and one bar over "S 1Y" at the start of line 3
        (read as one bar ~(FW NOT S 1Y) continued across the line break). "FW NOT S 2Y" on line 4 has NO bar.
      --YES--> TON --> bar
    Bar: ZL IHW TGR (28.26.61.1)          (no E / M output labels printed)

The output line meets a horizontal line with seven drops. Left to right:

    (1) far-left line, runs down and then right into the top of:
        hex: XF + DEC
             ZL M • NOT
             ZL MOD
             (28.15.51.1)
          --(no label printed)--> hex: ZR INSTR COMP (28.15.51.1)
                     --(no label printed)--> its exit meets, at a junction dot, the vertical line coming down from the
                                             "MOD ZL M" hexagon of drop (2); that line carries:
                                               IHW RDY E1 (28.67.17.1)
                                               IHW RDY E2 (28.64.14.1)
    (2) hex: ZR MT (28.15.41.1)
          --(no label printed)--> [rectangle] ZR INSTR COMP (28.15.51.1)
          --(no label printed; same line continues down into)--> hex: MOD ZL M (28.15.41.1)
                     --(no label printed)--> vertical line: junction dot with the exit of hex "ZR INSTR COMP" (drop 1),
                                             then IHW RDY E1 (28.67.17.1), then IHW RDY E2 (28.64.14.1)
    (3) a vertical line that runs down, turns right, and ends in the top of:
        hex: MOD ZL E • MOD ZL M (28.15.41.1)
          --YES--> GT AOB 18 TO ZL (28.27.50.1)
          --YES--> GT AOB 19 TO ZL (28.27.50.1)
    (4) hex: MOD ZL E •
             ~(FW NOT S +)
             ~(PROG IX)
             (28.15.41.1)
            bars seen at 400%: one rule above line 2 across its full width including the trailing "+"; one bar over "PROG IX".
          --(no label printed)--> Z 0-17 ABB PREP (28.96.03.1)
          --(no label printed)--> Z 18 TO ABB P2 TO ADJ PAR OF Z 18 -23 (28.96.07.1)
          --(no label printed)--> Z 18 ABB PREP (28.96.03.1)
    (5) a vertical line (just left of the bar's own output) carrying:
        COND ZL DEC TON CKT (28.27.30.1)
        hex: ~(BLOK XF + DEC)
             • YR-ZL M • NOT
             IHW EX
             (28.15.50.1)                          (one bar over "BLOK XF + DEC")
          --YES--> hex: NOT I EX IN PROGRESS (28.15.50.1)
                     --YES--> junction dot, two hexagons:
                         hex: SAC • NOT MOD L REQ (28.15.50.1)
                           --YES--> (junction dot) --> TON XF + DEC ZL SEQ (28.15.50.1)
                         hex: ZR WAS IHW • SAC (28.15.50.1)
                           --YES--> line runs down and left to the same junction dot --> TON XF + DEC ZL SEQ (28.15.50.1)
        COND MOD ZL M TOF (28.15.40.1)             (line ends here)
    (6) a vertical line that runs down, turns right, and ends in the top of:
        hex: ~(CD Y RIGHT •)
             ~(INST WD CHK)
             ~COMP
             (28.15.60.1)
            bars seen at 400%: a rule over each of the three text lines (line 1 including its trailing "•"; line 2 full
            width; "COMP"). Probably one bar over the whole expression; reported as seen.
          --YES--> COND YR-ZR TON CKT (28.15.60.1)
    (7) hex: CHK M COR • CD
             Y LEFT • Y-Z START
             + MOD ZL M + YR -
             ZL M • NOT MOD
             R (28.15.10.1)                        (no bars)
          --YES--> COND YL-ZR TON CKT (28.15.10.1)

### B. ZR WAS IHW TGR (middle left)

    hex: YR-ZLE • IHW
         EX ZR TGR ON •
         SBC
         (28.15.51.1)                              [both "•" print as small open dots]
      --YES--> bar                                 (no "TON" printed on this line)
    Bar: ZR WAS IHW TGR (28.15.51.1)
      one output line down the middle with two junction dots; a box on each side of each dot:
        BLOCK GEN OF OK TO MOD ZL (28.15.51.1)      |   BLOCK MOD ZL E TON (28.15.40.1)
        BLOCK GEN OF Y-Z M • MOD REQ (28.15.71.1)   |   COND [prints "XI"; uncertain: XF?] + DEC SEQ TON (28.15.50.1)

### C. 1 BIT MOD TGR (middle right)

    hex: SBC • MOD
         ZL E TGR
         ON
         (28.26.23.1)
      --YES--> bar                                 (no "TON" printed on this line)
    Bar: 1 BIT MOD TGR (28.26.23.1)
      one output line down:
        BLOCK GTING OF Z 28-30 TO XAB 1-3 (28.15.51.1)
        (from the same junction dot, a line runs right to:)
        hex: XF + DEC ZL E (28.15.51.1)
          --YES--> GT Z 31 TO XAB 4 (28.27.52.1)
          --YES--> XS READ P (24.00.09.1)           [a fold line runs through the number]
        BLOCK GEN OF XS READ P (28.15.51.1)
        BLOCK GTING OF Z 31 TO XAB 4 (28.15.51.1)

### D. FP Z ALT TGR (bottom)

    Three turn-on hexagons side by side, each exit labelled YES; the three join on one line entering the bar through "TON":
    hex (left):   ZR EXT • ZR FP
                  CL • NOT ZR FP CL
                  • ZL FP CL • SBC
                  (28.27.32.1)
    hex (middle): NOT ZR FP TGR •
                  ZL FP TGR •
                  SBC
                  (28.27.32.1)
    hex (right):  SBC • ZR FP CL •
                  TOF FP RDY R • ZL
                  EXT PREP • FPL
                  3E • ZL FP T
                  (28.27.37.1)                       [uncertain: last group 37 vs 32 -- prints 37]

    Bar: FP Z ALT TGR (28.27.32.1)
      output line to a horizontal line whose two ENDS drop into the outer two hexagons:
        hex: INSTR PREP COMP ZL (28.27.32.1)
          --YES--> FP RDY ZL (28.20.21.1)
          --YES--> COND FP INCOMP TON CKT (28.42.53.1)
        hex: INSTR PREP COMP ZR (28.27.32.1)
          --YES--> FP RDY ZR (28.20.21.1)
          --YES--> COND FP INCOMP TON CKT (28.42.53.1)
      Two more hexagons stand between them. NO input line is drawn from the horizontal line to either of them:
        hex: INST PREP COMP ZL • FP CL 2 ZL (28.27.32.1)          [prints "INST" without R]
          --YES--> (junction dot) --> BLOCK GEN OF INST CHK ENBLD (28.41.50.1)
        hex: INSTR PREP COMP ZR • FP CL 2 ZR (28.27.32.1)
          --YES--> line runs down and left to the same junction dot --> BLOCK GEN OF INST CHK ENBLD (28.41.50.1)

### Noted (Fig 3.1.22)

- "~(BLOK XF + DEC) • YR-ZL M • NOT IHW EX (28.15.50.1)"; "NOT I EX IN PROGRESS (28.15.50.1)"; "SAC • NOT MOD L REQ (28.15.50.1)"; "ZR WAS IHW • SAC (28.15.50.1)"; "TON XF + DEC ZL SEQ (28.15.50.1)"
- "XF + DEC ZL M • NOT ZL MOD (28.15.51.1)"; "XF + DEC ZL E (28.15.51.1)"; "COND XI + DEC SEQ TON (28.15.50.1)"
- "BLOCK GTING OF Z 28-30 TO XAB 1-3 (28.15.51.1)"; "BLOCK GTING OF Z 31 TO XAB 4 (28.15.51.1)"; "GT Z 31 TO XAB 4 (28.27.52.1)"
- "BLOCK GEN OF XS READ P (28.15.51.1)"; "XS READ P (24.00.09.1)"
- "BLOCK GEN OF OK TO MOD ZL (28.15.51.1)"; "BLOCK MOD ZL E TON (28.15.40.1)"; "BLOCK GEN OF Y-Z M • MOD REQ (28.15.71.1)"; "COND MOD ZL M TOF (28.15.40.1)"
- "MOD ZL E • ~(FW NOT S +) ~(PROG IX) (28.15.41.1)"; "MOD ZL E • MOD ZL M (28.15.41.1)"; "MOD ZL M (28.15.41.1)"; "SBC • MOD ZL E TGR ON (28.26.23.1)"; "1 BIT MOD TGR (28.26.23.1)"
- "CHK M COR • CD Y LEFT • Y-Z START + MOD ZL M + YR - ZL M • NOT MOD R (28.15.10.1)"
- "ZR INSTR COMP (28.15.51.1)" (once as a rectangle, once as a hexagon); "IHW RDY E1 (28.67.17.1)"; "IHW RDY E2 (28.64.14.1)"
- "COND ZL DEC TON CKT (28.27.30.1)"
- "BLOCK GEN OF INST CHK ENBLD (28.41.50.1)"; "COND FP INCOMP TON CKT (28.42.53.1)"

### Not read with confidence (Fig 3.1.22)

- Bar extents in the ZL IHW turn-on hexagon, in "MOD ZL E • ~(FW NOT S +) ~(PROG IX)" and in "~(CD Y RIGHT •) ~(INST WD CHK) ~COMP".
- Exits with no YES printed: ZR MT, MOD ZL M, XF + DEC ZL M • NOT ZL MOD, ZR INSTR COMP (hexagon), MOD ZL E • ~(FW NOT S +) ~(PROG IX).
- "COND XI + DEC SEQ TON": XI vs XF.
- Right FP turn-on hexagon ALD number (28.27.37.1 vs .32.).
- The two middle hexagons under FP Z ALT TGR have no drawn input.
- 1 vs I in "CD 1Y-ZL", "HW CL 1Y", "S 1Y", "NOT I EX".

---

## Fig 3.1.28 "ZL DEC Trigger OFF"

Not present on PDF pages 86-91. The six printed captions on these pages are 3.1.22 (p86), 3.1.23 (p87), 3.1.24 (p88),
3.1.25 (p89), 3.1.26 (p90), 3.1.27 (p91); no page carries a second caption, and no trigger bar named "ZL DEC" appears.
The only "ZL DEC" text on these pages is the action box "COND ZL DEC TON CKT (28.27.30.1)" under ZL IHW TGR on p86.

---

## Not read with confidence -- consolidated list (all figures in this file)

Fig 3.1.23 (p87)
- XF + DEC turn-on hexagons, middle and right: overbar extent (rules sit between text lines; read as ~(BLOK XF + DEC) in all three).
- Right XF hexagon "ZL FP + LH FW": letter before P broken (F/E); stray tick after "SAC •".
- "1 BIT MOD R T" (gap in print); "ZL IHW T •".
- ALD digits: TON WBC + DEC M TGR (28.15.80.?); COND WBC TGR TON (28.22.02.1); COND IDC FR I PAR ERR PREP (28/23); I CHK E • NM (38/28); IHW RDY E1 (fold).
- VFL + IO YES line broken in print before BLOCK GEN OF NO I CHKR REQ L.
Fig 3.1.27 (p91)
- Z56-bus first hexagon: third term reads ~53 at 800%, alongside an unbarred "Z 53" in the same hexagon (as printed).
- I vs 1 in RLL I E, VFL I ..., VFL CL I, EQ I Z, EQI, VFL 5 1 TO ICIB.
- "CYC PRE YFL 5 COMP"; "Z 50 • P5O TC Z ICIB 18 • P2"; "SET LAOC POS O"; commas/periods in "5,6", "0,5", "2,6".
- Whether the Z 53 • Z 51 YES line is meant to connect to the bus-to-VFL I M ON line (touches, no dot).
- Hexagon "Z 54 • 58 • ~55 • ~57" (VFL CL 3 TRANSIT ADR) has no input line.
- Bar assignment for rules between two text lines; "Z 55 + 57 • + ~(54 • 58)" bar span.
- XOFI TC FTH number blot; unlabelled exits of LOP 3 (28.88.25.1), FLLI E TGR ON • SBC, and the left exit of Z56.
Fig 3.1.25 (p89)
- Bar grouping in the 2Y29... and IY29... hexagons and in "MOD ZL E • ~FW ~(ON BDS) + ~PROG ~IX".
- Smudged numbers: (28.96.09.1) on Z 32 TO 49..., (28.27.50.1) on GT AOB 24 TO ZL, (28.44.16.1) on COND ICOB TO 2Y 0 - 63; "38" on I CHK E • NM P.
- PROG IY exit unlabelled; I vs 1.
Fig 3.1.26 (p90)
- Bar grouping in IY61... / 2Y61... hexagons; "DEC Z" vs "DEC 2"; "ZE" in COND WBC + DEC ZE TON CKT; FW DEC RDY number under crease.
Fig 3.1.24 (p88)
- Bar extents in "~(VFL CL 5 • IO) ~(• VFL + IO OP CODE) ~INV" and "Z 59 • Z FW • ~(VFL CL 5) • IMM".
- "VFL C1 1 • DI2" (fold); (28.20.50.1) twice (20/22); VFL 5 TYPE 1B last number; VFL COND SET LA DS number incomplete in print.
Fig 3.1.22 (p86)
- Bar extents in the ZL IHW turn-on hexagon, "MOD ZL E • ~(FW NOT S +) ~(PROG IX)", "~(CD Y RIGHT •) ~(INST WD CHK) ~COMP".
- Unlabelled exits (ZR MT, MOD ZL M, XF + DEC ZL M • NOT ZL MOD, ZR INSTR COMP hexagon, MOD ZL E...).
- "COND XI + DEC SEQ TON"; (28.27.37.1); two FP hexagons with no drawn input.

Coverage: all six pages (86-91) were transcribed in full; no tile was left unread. Running heads on p88/p89 were read at
thumbnail scale only. Page 91 connections were traced on 200% tiles; the densest junctions were re-checked at 400%.
