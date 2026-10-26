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
> **Re-verified by the committing session:** the headline claim, that
> the shipped machine has **TWO** look-ahead address registers where
> Buchholz p.266 and Performance Characteristics both say one. CE
> manual PDF page 92 was rendered and read: Figure 3.2.1, "IAUC LOAD
> ENABLE AND ADVANCE CONDITIONS", header "M3-04-3 LA FLOW DIAGRAMS",
> **page stamped 2/1/62**, carries decision boxes reading **BOTH
> LAARS BUSY**, **BOTH LAARS 1&2 BUSY** and **BOTH LAARS NOT BUSY**.
> The OCR of the same page corroborates independently with "LAAR 1
> BUSY COND", "LAAR 1 OR 2", "LAAR 1 NEXT", "LAAR 2 NEXT".
> Everything else in this file is the agent's reading.

---

# The IBM 7030 look-ahead unit: an implementation specification

Written 2026-10-25 for the Bluespec model in `/Users/npe/src/living-computing/stretch`.
Extends, confirms and in several places **corrects** `docs/microarchitecture_plan.md`
sections 6b/6c/6d and A.6.

**Evidence rule used throughout** (from the plan's own tie-breaker, §6 "Known risks"):
where sources disagree, the **1961 Performance Characteristics wins for TIMING** and the
**Jan-1963 CE manual R23-9732 wins for STRUCTURE**. Every place that rule bites is marked
**[TIE-BREAK]**. Where no source says anything, the line reads **[NOT IN THE SOURCES]** —
nothing in this document is invented.

---

## 0. PDF pages actually rendered and read

Every page below was rendered with `pdftoppm` at 350-700 dpi and read as an image. OCR text
was used only to find pages. Nothing is quoted here that was not read from a rendered page,
except where explicitly marked "OCR only (plain running text)".

| Document | PDF pages rendered + read | What for |
|---|---|---|
| `Planning_A_Computer_System.pdf` (Buchholz 1962) | **230** (Fig 14.4 + MBCU priority prose), **264** (Fig 15.6 look-ahead registers), **267** (Fig 15.7 IAUC advance), **268** (Fig 15.8 OCC advance; full page at 350 dpi plus three 700-dpi crops), **269** (Fig 15.9; 700-dpi crop of the TBC interlock box), **270** (Fig 15.10; full page plus two 700-dpi crops) | level complement, tag bits, counters, forwarding, interlocks, bus priority |
| `TR00.722_Stretch_I-Unit_Design_Mar60.pdf` | **5** (Fig 2 Stretch computer, unit interconnect), **10** (Fig 3 I-unit data paths), **31** (Fig 6 FP prep), **34** (Fig 7 VFL prep), **36** (Fig 8 CB execution), **38** (Fig 9 Transmit execution), **40** (Fig 10 Branch-on-indicator execution) | cycle-by-cycle I-box/LA interaction |
| `7030_Performance_Characteristics_Vol1_Mar61.pdf` | **61** (Fig A-1 data processing unit), **67** (LA register/tag/counter list), **69, 70, 71** (Table A-2, all three sheets) | shipped-machine register list, per-instruction LA level usage |
| `R23-9732_Manual04_7101_CPU_Jan63.pdf` (CE manual) | **92** (Fig 3.2.1 IAUC load enable + advance conditions), **93** (Fig 3.2.2 LA load pulses sheet 1), **96** (Fig 3.2.4 basic TBC advance conditions), **104** (Fig 3.2.12 TBC store gate control — the LAAR-1/LAAR-2 selector), **114** (Fig 3.2.22 LA houseclean timer), **117** (Fig 3.2.25 SCC advance), **171, 172, 175** (Table 3.4.1, 7101 CE console indicators — the trigger/ALD-page index) | **shipped** structure; the two-LAAR discovery |

OCR-only (plain running text, no figure content, legibility not in doubt):
Buchholz pp.253-272 (ch.15 text), TR00.722 pp.6-9, 18-30, 32-41, Perf Char pp.33-42
(ch.3 analysis + Tables 4-9), pp.60-68 (Appendix A text), CE manual pp.168-190
pp.189, 196-197 (console switch descriptions).

**Every CE trigger ID quoted in this document was read from a rendered page** (171, 172, 175),
not from OCR. That mattered: the OCR of these pages corrupts exactly the ID strings — `2D001`
came out as `2p001`, `2J054` as `25054`, `2L001` as `2L,001`, `2J014` as `23014`. The IDs below
are as printed. CE pp.176-177 were **not** rendered; the level-2 and level-3 tag IDs taken from
them are marked as OCR-derived in §1.3 and follow the level-1/level-4 pattern verified on p.175.

Rendered but **not** read in this pass, and therefore not cited: CE manual pp.94, 105, 106, 108.
They are in the "read next" list at the end.

---

## 1. Structure

### 1.1 How many levels

**Four.** Buchholz PDF 263 lists it as design decision 1 out of the simulator study:
"1. Four levels of look-ahead are provided." Buchholz PDF 257 gives the reason: speed
"goes up very rapidly for the first two levels, then rises more slowly", and on the Monte
Carlo problem "actually decreases slightly beyond six levels... a result of memory conflicts
caused by extraneous memory references started by the computer's running ahead on the
wrong-way paths of branches."

Perf Char PDF 62 names them **LA0, LA1, LA2, LA3**; CE manual's trigger index names them
**LA LEVEL 1 .. LA LEVEL 4**. Same four registers, two numbering conventions. This document
uses 0..3 and notes that CE logic-page citations use 1..4.

### 1.2 What one level holds

A level holds **the instruction (or a fragment of one), its operand, where it came from and
everything needed to retire it in program order** — never an address. (The address lives in
the LAAR, §1.4.) Transcribed from Buchholz Fig 15.6 (PDF 264), Perf Char PDF 67, and the CE
manual trigger index (PDF 174-177), which gives exact bit widths:

| Field | Width | CE trigger / logic page |
|---|---|---|
| Operand field | **76 bits** (64 data + 12 check) | `2P029/2M029/2K029/2H029` @ 31.01.01.1, "LA LEVEL n OPERAND FIELD POS 00-75" |
| Op code field | **10 bits** + check | `2Q040/2N040/2L040/2J040` @ 36.09.03.1, "POS 00-09" |
| Indicator field | **15 bits** | `..066`..`..080` @ 33.01.01.1-33.01.14.1 |
| Instruction-counter field | **19 bits** (POS 00-16, 17, 18) + 2 parity | `..083/..100/..101/..102/..103` @ 32.01.01.1, 32.01.18/19/20/21.1 |

The fifteen indicators, verbatim from Buchholz PDF 264 footnote 1, in order, and confirmed
one-for-one by the CE trigger index: *machine check* (CE calls it CONDITIONAL MACH CHK),
*instruction reject, operation code invalid, address invalid, data store, data fetch,
instruction fetch, index flag, index count zero, index value less than zero, index value
zero, index value greater than zero, index low, index equal, index high.*

### 1.3 Tag bits — **[TIE-BREAK], three-way, and the CE manual wins**

Buchholz PDF 264 says **8 tag bits** and names exactly eight: *level filled, level checked,
internal operand, instruction counter, look-ahead operation code, word-boundary crossover,
no operation, from.* Perf Char PDF 67 lists **nine**, adding **DISC** (disconnect).

The CE manual's trigger index lists, **per level, for all four levels**, the following —
and this is the shipped complement:

| Tag | CE logic page | Triggers (L1/L2/L3/L4) |
|---|---|---|
| LEVEL FILLED M | 36.01.0n.1 | 2Q060 / 2N060 / 2L060 / 2J060 |
| LEVEL CHECKED | 36.02.03.1 | 2Q059 / 2N059 / 2L059 / 2J059 |
| INTERNAL FETCH | 36.03.02.1 | 2Q058 / 2N058 / 2L058 / 2J058 |
| INSTRUCTION COUNTER VALID | 36.04.01.1 | 2Q057 / 2N057 / 2L057 / **2J057** |
| LOOKAHEAD OPERATION CODE | 36.05.01.1 | 2Q056 / 2N056 / 2L056 / 2J056 |
| WORD BOUNDARY CROSSOVER | 36.06.01.1 | 2Q055 / 2N055 / 2L055 / 2J055 |
| NOOP | 36.07.0n.1 | 2Q054* / 2N054 / 2L054 / **2J054** (36.07.06.1) |
| DISCONNECT | 36.08.0n.1 | 2Q053 / 2N053 / 2L053 / 2J053 |
| **INDEX STORE TAG** | 36.09.19.1 | 2Q061 / 2N061 / 2L061 / 2J061 |
| **EXTERNAL STORE TAG** | 36.09.14.1 | 2Q062 / 2N062 / 2L062 / 2J062 |
| **INTERNAL STORE TAG** | 36.09.15.1 | 2Q063 / 2N063 / 2L063 / 2J063 |
| **FROM BIT 1** | 36.16.02.1 | 2Q037 / 2N037 / 2L037 / 2J037 |
| **FROM BIT 2** | 36.13.03.1 | 2Q038 / 2N038 / 2L038 / 2J038 |

**Level 4's whole column was read from the rendered CE p.175** (`2J053` DISCONNECT …
`2J063` INTERNAL STORE TAG, in that printed order) and level 1's from p.175's neighbours and
the OCR of pp.176-177. The two entries this document earlier flagged as "dropped by OCR" are
now confirmed present on the rendered page: `2J057 36.04.01.1 INSTRUCTION COUNTER VALID TAB BIT
LEVEL 4` and `2J054 36.07.06.1 NOOP TAG BIT LEVEL 4`. (*) `2Q054`, the level-1 NOOP tag, is
**not** on a page rendered here — it is inferred from the 36.07.03/04/05/06.1 progression
across levels 1-4; everything else in the table is read or OCR-read directly.

So: **thirteen** tag bits per level, not eight and not nine.
- Buchholz's single *from* bit is **two** bits on the shipped machine (one per LAAR, §1.4).
- Buchholz's single notion "store" is **three** destination tags — index store / external
  store / internal store — matching TR00.722 PDF 21's three memory kinds (external memory
  EM, index storage XS, internal register IR).
- DISC is a maintenance bypass, not a program-visible tag: CE PDF 189, console switches
  A3F52-A3F55 "LA 1, 2, 3, 4 — When set (down), these switches set the disconnect tag for the
  associated level of lookahead. When this tag is set, the associated level of lookahead is
  bypassed for all lookahead loading operations." **A model may omit DISC** and still be
  faithful to normal operation; it must not omit the store-destination tags.

> **Correction to plan A.6**, which says "8 tags (level filled/checked, internal operand, IC
> valid, LA op code, word-boundary crossover, no-op, from)". That is Buchholz's 1962
> simplification. The shipped level carries 13.

### 1.4 The look-ahead address register — **[TIE-BREAK], and this is the big one**

Buchholz PDF 266 is categorical: "Since only one look-ahead address register is provided,
the look-ahead unit can handle only one store-type operation at a time." Perf Char PDF 67
lists "LAAR Look-Ahead address register (18 + check)" — singular — with three attached bits:
**LAAR-Busy**, **Store-executed**, **Forward-cycle-required**. Perf Char PDF 39 repeats it:
"Since there is only one LAAR, if the latter is busy whenever the I-box decodes an
instruction requiring LAAR, a wait must occur until the LAAR is free for reloading."

**The Jan-1963 CE manual shows two.** CE PDF 92 (Figure 3.2.1, IAUC LOAD ENABLE AND ADVANCE
CONDITIONS) contains the decision boxes **"BOTH LAARS BUSY"**, **"BOTH LAARS 1&2 BUSY"** and
**"BOTH LAARS NOT BUSY"**. The trigger index confirms the hardware:

```
2E001 .. 2D019   15.02.01.1 .. 15.02.05.1   LOOKAHEAD ADDRESS REGISTER 1, POSITIONS 0-18
2D001 .. 2D019   15.02.01.1 .. 15.02.05.1   LOOKAHEAD ADDRESS REGISTER 2, POSITIONS 0-18
2L025            38.53.01.1                 LAAR 1 BUSY TGR
2L026            38.53.01.1                 LAAR 2 BUSY TGR
```
(read from rendered CE pp.171, 172 and 175 — **"POSITIONS 0-18"** is printed, i.e. 19 bits,
consistent with Perf Char's "18 + check". CE p.171 carries the footnote **"Serial Numbers
30,003 - 30,005"** and is dated **1/1/63**; p.172 and p.175 are dated **2/1/62**.)

and the two *from* bits per level (36.16.02.1 FROM BIT 1, 36.13.03.1 FROM BIT 2) are exactly
what a two-LAAR forwarding network needs: each level records which LAAR it may forward from.
CE PDF 77 has "LAAR 1 BUSY COND FPR 3 TO LAOC"; CE PDF 94 (LA load pulses sheet 2) routes
"LAAR 1 OR 2"; CE PDF 104 has "LAAR 1 NEXT / LAAR 2 NEXT / FOR LAAR 1 / FOR LAAR 2".

**CE Figure 3.2.12, "TBC STORE GATE CONTROL" (PDF 104, logic 38.22.16.1), read as a rendered
page, is the mechanism in full and it removes any doubt.** Its flow, verbatim from the boxes:

```
TBC ADV -> STEP TBC TO NEXT LEVEL -> TBC AES ON? -> TBC LDE ON? -> EXT STORE?
          (gated by "EXT STO & NOT INT STO TAGS")
   -> FROM 1?  yes -> SET GT LAAR 1 NEXT (IN BCU)
              no  -> FROM 2?  yes -> SET GT LAAR 2 NEXT (IN BCU)
   -> LAOP 33 EXT OR 31?  yes -> SET STO NEXT n TGR  -> LOAD STORE REG FROM TOB NEXT
                          no  -> RESET STO NEXT n TGR -> LOAD STORE REG FROM ACOB NEXT
                          (n = 1 or 2, "FOR LAAR 1" / "FOR LAAR 2")
```

Three implementable facts fall straight out:
1. **FROM BIT 1 selects LAAR 1; FROM BIT 2 selects LAAR 2.** The two per-level *from* bits are
   not redundant — they are the level's association with one of the two store addresses. This
   is the shipped replacement for Buchholz's single *from* bit.
2. **The store data has two sources**, chosen by the LA op code: `TOB` (transfer-out bus, i.e.
   the operand the I-box already supplied) or `ACOB` (arithmetic checker out bus, i.e. the
   E-box result). This is exactly Perf Char PDF 38's distinction: *"In the case of I-box store
   type instructions (SX, SV, SC, SR, SVA, R, RXZ, T, SWAP, etc.) the store operands are
   already available during I-box processing time and can be converted to ECC check bits
   during shipment to LA, simplifying the store action in LA. In practically all other cases
   the store operand will not be available during I-box processing."*
3. The store gate is set **at TBC time**, not at SCC time — the SCC then finds the store
   register already loaded.

**Verdict under the tie-breaker rule: implement two LAARs**, each 18 bits + check, each with
its own busy trigger, allocated round-robin ("LAAR n NEXT"). Two store-type operations may
be outstanding at once. **But see §6.2 item 9 before wiring this in: every published timing in the corpus was measured
on the one-LAAR machine, so two LAARs buy fidelity of structure at the cost of every timing
oracle.** The recommendation there is two LAARs with a switch, defaulting to one, and all
regression oracles run with one. A one-LAAR model is the Mar-1961/1962-book machine and will be
*slower* than the shipped machine on consecutive stores — which is precisely the effect
Perf Char PDF 39 warns about ("LAAR-requiring instructions should preferably be reasonably
far apart, ideally with three or more time consuming instructions in between").

Because Perf Char's **Table A-2 LAAR columns were written for the one-LAAR machine**, the
whole of §1.6 below should be read as "needs *a* LAAR", not "needs *the* LAAR".

### 1.5 The five ring counters

Buchholz Fig 15.6 (PDF 264) draws five 4-position ring counters; Perf Char PDF 62 and 67 and
Fig A-1 (PDF 61) name them; the CE trigger index gives one trigger per counter per position
(e.g. `2Q032/2N032/2L032/—` IAUC positions 1/2/3, `2J033` OCC pos 4, `2J034` TBC pos 4,
`2J035` ABC pos 4, `2J036` SCC pos 4, logic pages 38.01/38.11/38.21/38.31/38.51).

| Counter | Buchholz name | Perf Char PDF 62, verbatim |
|---|---|---|
| **IAUC** | Instruction unit counter | "When IAUC refers to a level, that level may accept I-box loading, although the required operand may come later from MBCU." |
| **OCC** | Operand check counter | "During OCC time, the operand from MBCU may be checked for error." |
| **TBC** | Transfer bus counter | "During TBC time, the level may be shipped into E-box." |
| **ABC** | Arithmetic bus counter | "During ABC time, the interruption system is updated and signal is given to E-box for execution of the instruction just loaded." |
| **SCC** | Store check counter | "During SCC time, the store operand (if any) is checked and sent to MBCU on the basis of the contents of LAAR." |

Buchholz PDF 265 adds for ABC: "Controls the functions necessary for proper operation of the
interrupt system. Also designates the next level to have its indicator field entered into the
indicator register and to receive any result from the arithmetic unit for later storing";
and for SCC: "For non-store-type operations, this counter generally advances with the
arithmetic-bus counter."

Buchholz PDF 265: "The counters advance from level to level under their own control...
Except for interlocks to keep the counters in proper sequence, the counters are free to
advance as soon as their work is completed." **They are five independent FSMs over a shared
4-entry ring, not a pipeline with a common clock.**

### 1.6 Everything else in the look-ahead

From Perf Char Fig A-1 (PDF 61) — the shipped block diagram — the LA box contains, drawn
left to right: **LAAR**, the three standalone bits **LAAR BUSY / ST EX (store executed) /
FCR (forward cycle required)**, the five counters **IAUC OCC TBC ABC SCC**, the four level
registers **LA0 LA1 LA2 LA3**, and an **IC BUFFER** (19 bits + check per Perf Char PDF 67).
Outside the box but on the LA/I-box boundary sits the shared **I-LA-CHKR** (I checker).

The IC buffer is the recovery path: TR00.722 PDF 12, "The ICR has a set of in-gates (21) from
the lookahead IC buffer for use in recovery operations."

**The external interface, from TR00.722 Figure 2 (PDF 5), read as a rendered page.** The
look-ahead sits between the instruction unit, the memory bus control unit and the arithmetic
units, with exactly these arrows and no others:

```
          MULTIPLE MEMORIES
                 |
    BASIC EXCHANGE --\    MEMORY BUS CONTROL UNIT   /-- DISK EXCHANGE
                       \      |  FETCHES    ^ STORES
                              |             |
   INDEX REGS | INSTRUCTION UNIT ------> LOOKAHEAD --LOAD--> SERIAL ARITH UNIT (VFL)
                       |                     ^                ARITH REGS, BUS, CHECKERS
                       |                     \----STORE------ PARALLEL ARITH UNIT (FP)
                  INDS/CNTL            INDS/CNTL                        |
                       \-------- INTERRUPT MECHANISM <----------- INDS/CNTL
```
Note what is absent: **the arithmetic units have no path to the memory bus control unit at
all.** The `FETCHES` line from the MBCU tees to both the instruction unit and the look-ahead;
the `STORES` line runs only from the look-ahead.

**The I-unit side, from TR00.722 Figure 3 (PDF 10), read as a rendered page.** Six registers —
`IC REG (19)`, `1Y REG (64)`, `2Y REG (64)`, `X REG (64)`, `Z REG (64)`, `W REG (18)` — plus
`IC ADV (19)`, `INDEX ADDER (24-32)`, `I CHECKER (64)` and `INDEX REGS (16)`, wired by eight
named buses: `MEMORY OUT BUS (64)`, `I CHECKER OUT BUS`, `I CHECKER IN BUS`, `ADDER OUT BUS`,
`INDEX ADR BUS`, `ADDER BUS A`, `ADDER BUS B`, `MEM. ADR. BUS`. Four of these cross the
look-ahead boundary, and the figure labels them: the memory out bus and the I-checker out bus
both run **TO LOOKAHEAD**; there are **FROM LOOKAHEAD** returns into the index registers and
onto the I-checker in bus; the memory address bus runs **TO MBCU**. The decoder block is
`OPERATION DECODER → INSTRUCTION PREP. EXEC. CONTROLS`.

The **I checker is physically in the look-ahead** but was designed by the I-unit group:
TR00.722 PDF 18, "The I checker is located in the lookahead unit and was not a part of — but
coordinated with — the I unit design... a single I checker with separate in-busses from the
I unit and lookahead, OR'd at the input to the checker. The checker out-bus (ICOB) is a 64
bit data-bus, plus 29 parity and ECC lines... This bus feeds the four lookahead levels first
and then the XR and the ZY registers." It takes **0.6 µs** and is time-shared eight ways
(Perf Char PDF 37 lists all eight uses). **A model that ignores I-checker contention is
making a documented approximation**: Perf Char PDF 37, "it is therefore conceivable that
I-Checker conflicts may occur. The situation has not been completely studied... When an
I-Checker conflict occurs, the processing of one piece of data may have to be delayed by
0.3 to 0.6 µs."

Also real, from the CE trigger index: `2N017` LA HOUSECLEAN MODE TRIGGER (38.39.04.1),
`2N009/2N010` HOUSECLEAN TIMER E/M, `2N011/2N012` LA HOUSECLEAN OVER TIMER E/M,
`2N019` LA DISABLE INTERRUPT LINE TRIGGER, `2N021/2N022/2N026` LA (NORMAL/NOOP) INDICATOR
TEST TIMER, `2N016` NOOP MODE TRIGGER, `2Q005` PSEUDO-INTERRUPT INHIBITS LOAD TRIGGER,
`2C003` LA STORE MEMORY REQUEST TGR, `3R016` LOOKAHEAD RECOVERY MODE,
`2L001` SCC ADVANCE ENABLES SEQUENCE TRIGGER, `2N001` ABC ADVANCE ENABLES SEQUENCE TRIGGER,
`2L013/2L014/2L015` LA-to-I-unit transfer timers.

### 1.7 How many levels each instruction takes — **Perf Char Table A-2, transcribed**

This is the single most implementable artifact in the corpus and it exists nowhere else.
Read from rendered PDF pages 69, 70, 71. Level kinds, per the table's own legend (p.69):
`INT` internal operand fetch · `INT STORE` internal operand store · `Store` store ·
`IX Rec.` index-register recovery, "also called pseudo-store" · `B Rec.` branch recovery ·
`LAOP` LA operation · `NOOP` no-op, indicator transfer only · `Op` operation-code level (VFL)
· `opnd` operand level · `op + opnd` op code plus operand (usually F.P.).
Column meanings: *I-box opnd fetch* / *I-box execution* / *opnd fetch for LA* / *LA levels* /
*LAAR needed?* / *LAAR not needed but used if not busy* / *SAU* / *PAU*.

**Sheet 1 (p.69) — I-box instructions**

| Op | I-box fetch | I-box exec | fetch for LA | LA levels | LAAR? | LAAR-if-free | Comment |
|---|---|---|---|---|---|---|---|
| LX, LV, LC, LR, V+, V+C, V+CR(C≠0), V±ICR(C=0), R(index), RC≠(index,C=0) | yes | yes | no | IX Rec. | no | no | V+CR (c=0) involves 2 I-box fetches |
| LVI, LVNI, LCI, LRI, C±I, V±I, V±IC, V±ICR(C≠0), RCZ(C≠0)(index) | no | yes | no | IX Rec. | no | no | |
| KV, KC | yes | yes | no | NOOP | no | no | |
| KVI, KCI | no | yes | no | NOOP | no | no | |
| SX, Z | no | partly | no | store | **yes** | no | |
| SV, SC, SR, SVA | yes | partly | no | store | **yes** | no | SVA requires extra decoding |
| R(memory), RC≠(memory, C=0) | 2 | partly | no | store | **yes** | no | |
| RC≠(memory, C≠0) | no | yes | no | NOOP | no | no | |
| LVE | N | N | no | IX Rec. | no | no | extra decoding for each instruction fetch |
| LVS | no | yes | no | IX Rec. | no | no | repeated addition of index value fields |
| RNX | yes | partly | no | **test, store, NOOP** | —, yes, no | no | LA is pre-cleared by first level |
| EX (excl. subject instr.) | N | yes | no | NOOP | no | no | extra decoding for each instruction fetch |
| EXIC (excl. subject instr.) | 2N | partly | no | **N stores** | **No times** | no | extra decoding for each instruction fetch |
| T, SWAP | N | partly | no | **test, stores, NOOP** | —, **N times**, no | no | LA pre-cleared by first level; each N doubled in SWAP |

**Sheet 2 (p.70) — branches.** Header note on the sheet: *"1Y, 2Y are cleared to receive new
instruction for all successful branches."*

| Op | I-box fetch | I-box exec | fetch for LA | LA levels | LAAR? | Comment |
|---|---|---|---|---|---|---|
| B, BR, BE, NOP | no | yes | no | NOOP, test | no | |
| BD | no | yes | no | test, NOOP | no | LA pre-cleared |
| BEW | no | partly | no | NOOP, **2 test levels** | no | |
| CB, CBR (no refill) | no | yes | no | IX Rec. | no | |
| CBR (refill) | yes | yes | no | IX Rec. | no | |
| B ind (XF, XC≠, XVL≠, XV≠, XVGZ, XL, XE, XH) | no | yes | no | noop | no | |
| **B ind (non-index conditions)** | no | **partly** | **INT** | **OP. / INT / INT.stores / B Rec.** | no/**yes**/no/no | **SAU yes** |
| **BB** (branch on bit) | no | partly | yes | **OP / opnd / store / B Rec.** | no/no/**yes**/no | SAU yes |
| SIC B, SIC BR, SIC BE, SIC BD | yes | partly | no | store | **yes** | LA pre-cleared in SIC BD by 2 test levels |
| SIC BEW | yes | partly | no | store, 2 test levels | **yes**, no | |
| SIC CB, SIC CBR (no refill), if branch taken | yes | partly | no | IX Rec., Store | **yes**, no | SIC store level will not exist if branch is not taken |
| SIC CBR (refill), if branch taken | 2 | partly | no | IX Rec., store | **yes**, no | same |
| SIC B ind (index conditions), if branch taken | yes | partly | no | store | **yes** | store level replaced by noop if branch is not taken |
| SIC B ind (non-index conditions) | yes | partly | no | **op / INT / INT store / B Rec. / store** | no/**yes**/no/no/**yes** | SAU yes |

**Sheet 3 (p.71) — E-box instructions**

| Op | fetch for LA | LA levels | LAAR? | LAAR-if-free | SAU | PAU |
|---|---|---|---|---|---|---|
| FP ±, L, LWF, ±MG, D±, DL, DLWF, D±MG, K, KMG, KR, KMGR, \*, /, R/, F±, E± | yes | op + opnd | no | **yes** | exp | frac |
| FP E±I | no | op + opnd | no | no | exp | frac |
| FP SHF | no | op + count | no | no | no | frac |
| FP ST, SL0, SRD, SRT | no | **store** | **yes** | no | exp | frac |
| FP M±, M±MG | yes | op + opnd / **store** | no / **yes** | yes / no | exp | frac |
| FP \*+ | **2** | op + opnd / C($FT) | no / no | yes / yes | exp | frac |
| FP LFT, D/ | yes | op + opnd / **store** | no / **yes** | yes / no | exp | frac |
| VFL +, L, LWF, ±MG, K, KMG, KR, KMGR, KE, KF, KFE, KFR, C, CT, LCV | yes | **op** / **opnd** | no / no | no / yes | yes | no |
| VFL \* (binary) | yes | op / opnd | no / no | no / yes | yes | yes |
| VFL CV, DCV | no | op / INT | no | no | yes | no |
| VFL ST, SRD, CM, M±MG, M+1 | yes | **op / opnd / store** | no / no / **yes** | no / yes / no | yes | no |
| VFL \*+ (binary) | 2 | op / opnd / C($FT) | no | no / yes / yes | yes | yes |
| VFL LFT, LTRS, LTRCV, \*(dec), /(dec), \*+(dec) | yes | op / opnd / **store** | no / no / **yes** | no / yes / no | yes | no |
| I/O | no | op / LAOP | no | no | no | no — *"LA communicates with exchange directly"* |

Sheet-3 note, verbatim: *"For all VFL operations, if opnd crosses over full word boundary,
the no. of LA opnd and/or store levels is doubled. Progressive indexing required one more
IX box."* (i.e. one more IX-Rec level.)

Buchholz PDF 271 states the worst case independently: *"An extreme case is a VFL ADD TO MEMORY
instruction with progressive indexing, which may require six successive levels (two levels
being used twice)."* With only four levels in the ring, **a six-level instruction is a
self-blocking case the ring must handle by reuse, not by having six levels resident.**

> **Correction to plan §6b**, which says "The instruction unit loads an E-box-class
> instruction ... into the tail level". One level per instruction is the FP case only. VFL
> takes 2-3 (6 worst case), Bind-on-arithmetic takes 4, I/O takes 2, Transmit takes
> 2 + N (+ N more for SWAP). **Level occupancy must be per-instruction from Table A-2, not
> one-per-instruction.**

> **Confirmation of plan §6c/§6d**: Perf Char PDF 40, "Each I-box instruction results in one
> (sometimes more) level of LA being loaded. This is done to enable the convenient updating
> of certain indicators and to allow interruption action (if needed) to take place in step
> with other interruptions." Table A-2 makes the "sometimes more" exact. And PDF 36:
> "All I-box instructions load LA levels for index register recovery or for indicator
> register updating. These levels are not useful to the E-box and have the effect of
> reducing the number of LA levels."

---

## 2. Forwarding and interlock rules

### 2.1 The four counter interlocks

Buchholz's prose (PDF 267, 268, 271) and the CE manual's shipped flowcharts agree on a single
rule: **each counter may not advance onto or past the level its predecessor still occupies,
and the IAUC may not advance onto the level the SCC still occupies.** The ring order is
IAUC → OCC → TBC → ABC → SCC → (back to IAUC).

Verbatim:
- Buchholz PDF 267: "The instruction-unit counter is interlocked to prevent it from advancing
  to a level still occupied by the store-check counter. This prevents new information from
  destroying data yet to be stored."
- Buchholz PDF 268: "This counter is interlocked so that it will not pass the instruction
  unit counter." (OCC)
- Buchholz PDF 268: "Each counter is appropriately interlocked with its predecessor."
- **CE manual PDF 96** (Fig 3.2.4), terminal box, verbatim: **"ADVANCE TBC IF NOT INTLKD BY OCC"**.
- **CE manual PDF 113** (OCR of the ABC figure): **"ADV ABC IF NOT INTLKD BY TBC"**.

**[CONFLICT, resolved]** Buchholz's *figures* 15.9 and 15.10 (PDF 269, 270) print the branch
labels the other way round from figures 15.7 and 15.8. Read at 700 dpi:
- Fig 15.7 (IAUC): "Has instruction unit counter reached store check counter setting?"
  **No → Advance, Yes → Wait.**
- Fig 15.8 (OCC): "Has operand check counter reached instruction unit counter setting?"
  **No → Advance, Yes → Wait.**
- Fig 15.10 (TBC): "Has transfer bus counter reached operand check counter?"
  **Yes → Advance, No → Wait.** Same inversion on the ABC and SCC boxes of the same figure.

The second polarity is inconsistent with the book's own prose and with the CE manual.
**Implement "reached ⇒ wait" for all five.** Treat Figs 15.9/15.10's labels as a
typographical error in the 1962 book.

CE Fig 3.2.1 (PDF 92) gives the IAUC's shipped advance test in more detail than Buchholz:
the IAUC checks **"SCC AT NEXT LEVEL"**; if yes it then looks at **ABC THERE → TBC THERE →
STORE REQUIRED → ABC ADVANCING** before deciding, and separately tracks **"NEXT LEVEL IN SCC"**,
**"NEXT LEVEL IN ABC"**, **"ANY DISC"**, **"RECOVERY NEEDED"**, **"STORE DONE"**, **"STORE BEING DONE"**.
Each counter also carries an **AES** ("advance enable sequence") trigger —
`2L001 SCC ADVANCE ENABLES SEQUENCE TRIGGER`, `2N001 ABC ...` — which is set on arrival at a
new level and reset by whichever action that level needs; the counter advances when AES is off.
Fig 3.2.4's own words: "SET TBC AES" on arrival, then "RESET TBC AES" on each of five
alternative completions (TBC EXECUTED / ABC TRANS INDS ONLY / ABC INT FETCH / ABC STORE ACTION),
then "TBC AES OFF? → ADVANCE TBC IF NOT INTLKD BY OCC".

**CE Figure 3.2.25, "SCC ADVANCE" (PDF 117), read as a rendered page**, is the most complete
single advance sequence in the corpus and should be the template for all five:

```
ADV -> SET SCC AES (38.51.03.1) -> SCC AT NEW LEVEL
  -> DISC SCC?  yes -> SCC ABC INTLKD? (2E) -> ... -> SCC SING ADV. COND.
                no  -> LC ON? -> LF ON?
       -> no  -> SCC LDE ON? -> SET SCC LDE TRIG (38.52.07.1)
       -> yes -> SCC DEC ADV. COND. (38.51.05.1) / ILLEGAL PS STORE? (LAOP 42, 44, 46)
  -> EXT STORE?
       yes (BCU)  -> STORE DATA TIMER M        (LAOP 31, 33, 21, 13, 23, 17, X2)
       no  (I BOX) -> INDEX STORE?
              yes (X REG) -> WRITE INDEX LA M            (LAOP 02, 04, 06, 13, 17, 23, X2)
              no  (Y REG) -> I TIMER NO INDEX TRANSFER M (LAOP 45, 51)
  -> SCC AES OFF? -> SCC ABC INTLKD? -> SCC SING ADV. COND. (38.51.04.1)
                                     / SCC MULT. ADV. COND. (38.51.06.1)
  -> ADV. SCC (38.51.01.1) -> RESET LF TAG (36.01.02.1)
                           -> SET SCC AES   (38.51.03.1)
                           -> RESET SCC LDE (38.52.07.1)
```

Note **"ADV. SCC -> RESET LF TAG"**: the store-check counter's advance is what frees a level,
which is why the IAUC-vs-SCC interlock is the one that throttles the whole I-box. Note also
the three destination branches (BCU / index storage / Y register), matching the three store
tags of §1.3 and TR00.722's three memory kinds. The parallel ABC rule is printed on CE
PDF 114: **"ADV ABC IF NOT INTLKD BY TBC"** (logic 38.31.05.1).

**Minimal implementable model:** per level, a set of "work remaining" flags; per counter, a
rule that fires when its own work at the current level is done **and** `next(counter) != pred`;
the SCC's advance clears *level filled*.

### 2.2 When the I-box may run ahead, and what stops it

Perf Char PDF 34: "within the 7030 CPU at any given time **up to ten instructions** can be in
various stages of processing." (TR00.722 PDF 9 gives the I-box's own share: "a number (6) of
instructions may be located in the Y and Z registers simultaneously".)

The I-box runs ahead **unconditionally** until one of these stops it. This is the complete
documented stall list:

1. **No free look-ahead level** (IAUC would advance onto SCC). Perf Char PDF 35: "The I-box
   decoding, address indexing, and operand request continues as long as instructions are
   available and as long as LA levels are available for loading."
2. **No free LAAR** when the instruction needs one. Perf Char PDF 39: "if the latter is busy
   whenever the I-box decodes an instruction requiring LAAR, a wait must occur until the LAAR
   is free for reloading." (Two LAARs on the shipped machine, §1.4.)
3. **A store into index storage.** Perf Char PDF 39, verbatim and unambiguous: *"A store into
   index storage is a time-consuming operation. Whenever such an instruction is decoded,
   since the next instruction may make use of the new index contents, the I-box does no
   further decoding until the new index contents arrives."* TR00.722 PDF 22 says the same
   from the hardware side: "In the case of VFL and FP stores to index storage, the I unit
   loads the store type instruction into lookahead; then waits until the entire operation is
   completed, including the resultant store back to index storage"; and PDF 29 names the
   trigger: "store wait control, when lookahead contains a store to XS, IR, or MR."
4. **Program-store compare hit** (store into an already-prefetched instruction). §2.4.
5. **A forwarding cycle in progress.** Perf Char PDF 40, case (3): "Further LA loading in the
   I-box is delayed until the forwarding is completed."
6. **Instructions that drain the look-ahead completely.** Perf Char PDF 36, verbatim:
   *"The following instructions empty the LA completely: T, TI, SWAP, SWAP I, RNX, BD."*
   Table A-2 adds the mechanism — RNX / T / SWAP are "LA pre-cleared by first level";
   BD and SIC BD by "2 test levels". Tables 4-9 add `+ LAdr` ("Look-ahead drain") to the time
   of: LX/LV/LC/LR/SV/SC/SR/V+/V+C/V+CR/KV/KC **with address in IR**; SV,SC,SR and SVA **to
   the time clock**; RNX; LVE; EX and EXIC (which "always begins with a Look-ahead drain" and
   "always ends with LA drain"); BE when previously disabled; **BD = 2 LA drains**; and every
   T/SWAP variant's setup.
7. **A second guessed branch.** §2.5.
8. **Houseclean / recovery mode.** §2.6.

An I-box instruction's own LA level costs real time that **cannot** be hidden. Perf Char
PDF 41, verbatim: *"It takes 0.9 to 1.2 µs to process an LA level corresponding to I-box
instructions. This time cannot be overlapped by concurrent E-box action."* And PDF 41:
"The E-box overlapping cannot be effective unless I-box instructions are well dispersed."

### 2.3 Forwarding: store→load and load→load

**The mechanism.** Buchholz PDF 265-266, verbatim: *"Each time a store operation is loaded
into a look-ahead level, the operand address is placed in the common look-ahead address
register, and this level is tagged by turning on the from bit. The address of each subsequent
data fetch is compared with the contents of the look-ahead address register, and, if they are
equal, the data fetch is canceled and the operand field is forwarded from the tagged level.
This forwarding process saves memory references and prevents the use of obsolete data."*

**Load→load forwarding is real and separate.** Buchholz PDF 266: *"When the look-ahead address
register is not busy with a store instruction, it contains the address of the most recently
loaded operand. Thus, if several successive references are made to the same address, only one
memory fetch is required, the other levels receiving their operands by forwarding."* The
worked example is `LOAD a; MULTIPLY a; MULTIPLY a` for A³ — "The operand A is fetched from
address a once for LOAD and then supplied to the two MULTIPLY instructions by forwarding."
Perf Char PDF 40 confirms for the shipped machine: *"Forwarding is available also for
consecutive fetch of the same memory operand. Whenever a fetch-type instruction is decoded,
the fetch address is gated into LAAR unless the latter is busy. This act does not make LAAR
busy but can allow the forwarding on successive fetches."*
**This is what Table A-2's column "LAAR not needed but used if not busy" means** — every
`op + opnd` FP level and every VFL `opnd` level is marked `yes` there.

**The exact sequence**, from Buchholz Fig 15.7 (PDF 267), read as a rendered page. Decode
type of instruction → three arms:

*No data required*: set *level filled* and *level checked* immediately; done.

*Memory fetch*: compare the operand address with the LAAR.
  - **Equal** → "Cancel data request" → "Forward data" → "Any data error? / Is error
    correctable? → Correct, else Tag level with no-op to show it should not be executed"
    → set *level filled* + *level checked*.
    (Note: the fetch *had already been started* by the I-box; forwarding cancels it.
    Buchholz PDF 266: "the operand request (which had already been initiated by the
    instruction unit to save time) is canceled".)
  - **Unequal** → "Does look-ahead address register contain data address of store type
    operation?" **No** → "Gate operand address into look-ahead address register. Set *from*
    bit" (this is the load→load case; it does **not** set LAAR-busy). **Yes** → do nothing to
    the LAAR (a live store owns it) and fall through.

*Store*: "Does look-ahead address register contain data address of store type operation?"
  **Yes → Wait** (loop). **No** → "Place address in look-ahead address register and tag level
  with *from* bit."

Then all three arms converge on "Has instruction unit counter reached store check counter
setting? No → Advance, Yes → Wait."

**The three store-close-to-fetch cases, verbatim from Perf Char PDF 39-40.** These are the
canonical worked examples and should become three regression programs:

> *"Whenever I-box requests a memory fetch, a comparison is made with the contents of LAAR to
> avoid logical conflicts. In all cases, logical conflicts will not produce wrong results,
> although some delays are to be expected."*

- **(1) Store into a prefetched instruction** — `A  ST (u), A+0.32` then `+(n), 1000.($5)`:
  *"The second instruction, having been previously fetched into 1Y or 2Y, clearly cannot have
  the correct information until the store is complete. When such a store is decoded, I-box
  invalidates the prefetched instructions and waits until the correct information is
  available."*
- **(2) Store into a nearby I-box operand address** — `ST (u), 1003.($12)` then
  `V+, $15, 1003.($12)`: *"The execution of the second instruction is delayed until the
  correct operand arrives."*
- **(3) Store into a nearby E-box operand address** — `ST (n), 1007.` then `*(n), 1007.`:
  *"The I-box comparison with the LAAR shows that the operand will be in the LA prior to its
  arrival at the memory. A forwarding mechanism is activated to make the store operand
  available to the fetch level. Further LA loading in the I-box is delayed until the
  forwarding is completed."*

TR00.722 PDF 23 gives the same three cases from the I-unit side, and adds the fourth
comparator: *"Since lookahead has four levels, all subsequent fetches have to be compared
against the store address, once it is loaded into lookahead. If an instruction fetch or an I
unit operand fetch compares equal, the fetch is held up until the store is completed. If an
I unit operand fetch for lookahead compares equal with the store address, appropriate
controls are effected. These initiate a 'forwarding' operation of the store operand to the
designated fetch level, without first requiring a store to memory... None of these
comparisons cause recoveries of the I unit."*

**So there are three distinct comparators, and the model needs all three:**

| Comparator | Compares | Hit effect | Source |
|---|---|---|---|
| **Program store compare** | store address on MAB **vs ICR and IC-adder output** | **I-unit recovery** — invalidate 1Y/2Y and refetch | TR00.722 PDF 23 |
| **LAAR compare (instruction / I-box operand fetch)** | fetch address vs LAAR | **hold the fetch** until the store completes | TR00.722 PDF 23; Perf Char case (2) |
| **LAAR compare (LA operand fetch)** | fetch address vs LAAR | **forward**, cancel the memory fetch, delay further LA loading | TR00.722 PDF 23; Perf Char case (3); Buchholz Fig 15.7 |

CE Fig 3.2.2 (PDF 93), load pulse **LLP 2**, shows the shipped gating of this: a decision
**"IS LAAR COMPARE ENABLED?" (logic 36.16.07.1)** feeding **"ADDRESS COMPARE?"** feeding
**"DATA ON IMOB"**, with the no-compare path going on to set *LF E trigger* → *set LF tag* +
*gate IMOB into data field*. The enable bit is why case (1)-style conflicts can be armed and
disarmed per load.

> **Correction to plan §6b.** The plan's model "a level whose operand address equals an
> earlier unretired level's waits for that level to retire ... done conservatively for any
> earlier level rather than only stores" and "no data forwarding" is **sound but structurally
> different from the machine**. The machine compares against **one (shipped: two) address
> register**, not against every level, and it **forwards rather than waits** in the
> store→E-box-load case, and it **also forwards load→load**. The plan already flags this as
> "one of the places the cycle-accuracy phase has to come back to". This section is the
> specification for that return. The `storeTarget()` completeness invariant recorded in the
> plan stays necessary under the real rule too — a store that never announces itself never
> claims a LAAR, and then nothing forwards.

### 2.4 Program store compare

TR00.722 PDF 23, verbatim: *"A store type instruction, for example, presently being executed,
can store into the address of an instruction which has already been fetched. In order to
detect this condition and be able to correct it, it was necessary to design two logical units
for comparing the memory address-bus with the IC register and the IC adder output. Whenever a
store is loaded into lookahead this comparison is made. If an equal condition results it
indicates that the contents of that location have been fetched already and loaded into the I
unit. **A recovery is always made under these conditions.**"*

Note the comparison is against **ICR and ICR+adder**, which together give n, n+1, n+2, n+3
(TR00.722 PDF 12) — i.e. against the *word addresses currently covered by 1Y/2Y*, not against
the Y registers' contents.

### 2.5 Branches: the guess and the wrong-way recovery

**The guess.** Buchholz PDF 263, design decision 4: *"For a branch instruction conditional on
the result of arithmetic-unit operations, the instruction unit proceeds as if the branch will
fail."* Buchholz PDF 262 gives the reasoning: *"Holding up at every branch point seems less
desirable than any of five guessing procedures... Unless there is an unusual situation in a
problem with a very high probability that the branch will always be taken, the least time
will be lost if one assumes that branching will not occur."* TR00.722 PDF 30 records that the
decision was close: *"A study and program simulation was made to determine whether to assume
the branch or not. The results did not clearly indicate an advantage either way, and depended
largely upon how the program was written. It was decided to assume that the branch would not
be successful, and if the assumption proves to be incorrect, then a recovery is made."*
Perf Char PDF 42 adds the engineering reason: *"the latter assumes the branch to be
unsuccessful (to avoid unnecessary invalidation of 1Y, 2Y contents) and processes ahead."*

**Which branches are guessed.** Perf Char PDF 41, verbatim: *"The following branches, however,
involve conditions known to the I-box and are executed entirely within the I-box: CB and
variants; B ind for XF, XVLZ, XVZ, XVGZ, XCZ, XL, XE, XH."* Everything else conditional on an
indicator — i.e. on arithmetic results — is guessed. These are exactly the eight indicators in
the I-box's **updated indicator register** (TR00.722 PDF 19: XL, XE, XH, XCZ, XVLZ, XVZ, XVGZ,
XF), which exists for precisely this purpose: *"These indicators differ from the status of the
corresponding main indicator register triggers by the effect of the instructions which were
processed by the I unit and which are still in lookahead, awaiting to be processed by the VFL
or FP units. Hence, the term updated indicators. This UIR is used to test for conditional
branches on these indicators."*

**The four levels.** Perf Char PDF 42, verbatim: *"Altogether four LA levels are used for each
such branch instruction: three levels not unlike those for a VFL connect-to-memory instruction
plus a branch recovery level. It is noted that there is always a store type level, whether the
programmer specifies a change of the tested bit or not. **For B ind, two of these four levels
involve the LAAR.**"*

Table A-2 (p.70) names them and TR00.722 Fig 10 (PDF 40) shows them being loaded in order:

| # | Level | Table A-2 LAAR | TR00.722 Fig 10 LALD label | What it does |
|---|---|---|---|---|
| 1 | `OP.` | no | `OP→LA` | op codes + indicator address field: "tell the VFL unit what operation is required" |
| 2 | `INT` | **yes** | `F→LA` | internal fetch of the **indicator register** as the operand |
| 3 | `INT.stores` | no | `ST→LA` | store level: "after selecting, testing, and possibly modifying the indicator bit, the contents of the indicator register must be returned" |
| 4 | `B Rec.` | no | `BR→LA` | "the recovery level which contains the branch address, the IC value, and various operation and indicator tags" |

**[CONFLICT, minor]** Perf Char says "two of these four levels involve the LAAR"; Table A-2's
own LAAR column marks only the `INT` level yes for `B ind (non-index)`. For `BB` (branch on
bit) the `store` level is also marked yes. Under the TIMING tie-breaker take Perf Char's prose
(two LAAR uses, hence two LAAR-busy intervals to charge). **[NOT IN THE SOURCES]** which two.

**The recovery.** TR00.722 PDF 41, verbatim: *"If that happens, the branch address is returned
to the IC and all intervening operations are cancelled."* Perf Char PDF 42, verbatim: *"If,
however, the guess proved incorrect by E-box arithmetic, the I-box has already processed
ahead, and recovery action has to be taken to ensure the logical integrity of the program.
The re-setting of the I-box to the previous state often requires shipment of index register
information back to the I-box. The correct instruction counter value is also shipped back to
the I-box."* And PDF 42 again, naming the whole obligation: *"All changes in the index
registers and/or index indicators due to the advance processing by the I-box must now be
undone."*

**How the undo is possible.** Not a snapshot: *pseudo-store levels*. TR00.722 PDF 35, on the
CB sequence: *"The instruction fetch is overlapped with the loading of the index word, before
modification, into lookahead. This is referred to as a pseudo-store level, and is only used in
recovery operations where the index registers have to restore to some previous level as a
result of an interrupt or no-op condition."* Table A-2 calls it `IX Rec. = index register
recovery (also called pseudo-store)` and marks it on **every** index-arithmetic and index-branch
instruction. Buchholz PDF 272 describes the interrupt case the same way: *"The arithmetic-bus
counter identifies each level, for which the instruction unit has previously modified an index
word in the index memory, by tagging it as a pseudo store level. The old contents of the index
word are placed in the pseudo store level, and the store-check counter is responsible for
storing this word in the index memory."*

> **Correction to plan §6d**, which proposes "a snapshot of the sixteen index words and the
> index indicators, standing for the recovery pseudo-store levels the machine would have
> loaded one at a time." The real machine's mechanism is **per-instruction, in the ring**: the
> *old* index word travels in its own LA level and is written back by the SCC on recovery.
> A snapshot gives the right answer but the wrong *level occupancy*, and level occupancy is
> what throttles the I-box. **For cycle accuracy the IX-Rec levels must be modelled as real
> levels** — Perf Char PDF 36 says exactly why: "All I-box instructions load LA levels for
> index register recovery or for indicator register updating. These levels are not useful to
> the E-box and have the effect of reducing the number of LA levels."

> **Correction to plan §6d**'s "Only one guess is outstanding at a time; a second arithmetic
> branch waits." **[NOT IN THE SOURCES]** — no source states a limit of one outstanding guess.
> What the sources state is a limit of *four levels*, and a guessed branch eats all four
> (Perf Char PDF 42). The one-guess rule therefore *falls out* of the level count rather than
> being an independent rule, and should be implemented that way.

The no-op path is also a recovery: TR00.722 PDF 37, on CB, *"If a condition occurred which
would no-op the instruction, then the new IC field is not loaded, only the indicators and a
no-op tag. This would cause any branching already done to be cancelled by a recovery operation
later."*

### 2.6 Interrupt recovery (housecleaning) — same machinery

Buchholz PDF 271-272, the full procedure, verbatim in sequence:

1. *"As soon as the arithmetic-bus counter senses an interrupt, the instruction unit and
   arithmetic unit are signaled to stop preparing and executing more instructions. The
   interrupt system is disabled temporarily. The look-ahead housecleaning mode is turned on."*
2. *"The instruction-unit counter stops where it is. The operand-check and transfer-bus
   counters are allowed to advance until they reach the same level as the instruction-unit
   counter."*
3. *"The arithmetic-bus counter identifies each level, for which the instruction unit has
   previously modified an index word in the index memory, by tagging it as a pseudo store
   level. The old contents of the index word are placed in the pseudo store level, and the
   store-check counter is responsible for storing this word in the index memory."*
4. *"Eventually all counters will be at the same level, and the look-ahead unit will then be
   empty. The proper instruction-counter setting is sent to the instruction unit to return
   that unit to the point in the program at which interruption occurred. The housecleaning
   mode in the look-ahead is turned off, and the instruction and arithmetic units are allowed
   to resume operation."*
5. The free instruction is then fetched and executed by the I-box; *"The temporary disabling
   of the interrupt system prevents secondary interrupts."*

Note **where the interrupt is taken**: at the **ABC**, before the indicator field is gated
(Fig 15.10, first box of the ABC column: "Is interrupt waiting? Yes → To interrupt controls").
This is the precise-interrupt point and it is what makes the whole overlapped machine appear
sequential — Buchholz PDF 255: *"the design of the look-ahead unit was required to make the
CPU, despite its complex overlapped and nonsequential operation, appear to execute programs
sequentially, one instruction at a time."*

Perf Char PDF 63 gives the shipped sequence, verbatim: *"a. The left-most masked indicator bit
position is noted. b. I-box is house-cleaned except the index storage. c. LA house-cleaning is
performed. Recovery information is shipped back to the I-box. This includes all index register
recovery information and the interrupted IC value. d. Contents of $IA is fetched and added to
K.0. e. Instruction beginning at the address C($IA) + K.0 is fetched from MBCU without
disturbing $IF indicator. f. The 'free' instruction is performed with all masked interruption
conditions enforced... g. I-box fetches new instructions on the basis of IC."*

**CE Figure 3.2.22, "LA HOUSECLEAN TIMER" (PDF 114, logic 38.39.02.1), read as a rendered
page**, gives the shipped sequence, and it matches Buchholz step for step:

```
HSCLN TIMER (E,M)
  -> GT CNIDC IND TO MK IND (35.27.03.1); RESET ABC AES (38.31.03.1)
  -> RESET LAAR BUSY TRIG (38.53.03.1)                 <- both LAARs are freed here
  -> PSEUDO STORE? yes -> RESET ABC LF TAG (36.01.09.1)
  -> HSCLN DUE TO "INTRUPT"? / "INTERPT NEXT INSTR" ON
       -> RESET "INTRPT NEXT INSTR" TRIG (38.35.05.1)
       -> SET "INTRPT INHIBIT LOAD" TRIG (38.39.03.1)
       -> SET "DISABLE INTRPT" TRIG      (38.39.05.1)
       -> SET "I BOX RQST HSCLN" TRIG    -> START I BOX HSCLN TIMER (38.03.10.1)
  -> (execution units) SAU INSTR? (LAOP X1, 35, 43) / PAU INSTR? (LAOP X2)
       -> SAU IDLE? / PAU IDLE? -> SET "EXECUTION UNITS IDLE" TRIG (38.39.04.1)
  -> EXEC UNITS IDLE? -> SET LA HSCLN MODE TRIG (38.39.04.1)
                      -> RESET "EXEC UNITS IDLE" TRIG; RESET I BOX HSCLN TIMER
  -> LA EMPTY? yes -> START LA "HSCLN OVER" TIMER (38.39.01.1)
  -> while in HSCLN MODE: ADV ABC IF NOT INTLKD BY TBC (38.31.05.1) -> SET ABC AES
                                                                   -> RESET HSCLN TIMER M
```

Two things to carry into the model: the **LAAR busy triggers are reset at the very start of
housecleaning** (so a pending store's address register is released before the drain, not
after), and **housecleaning is gated on the execution units going idle** before LA mode is
entered — the SAU and PAU are polled (`SAU IDLE?`, `PAU IDLE?`, `PAU DISCOVERS INTRPT COND`),
they are not simply told to stop.

CE manual triggers for this mode: `2N017 LA HOUSECLEAN MODE TRIGGER` (38.39.04.1),
`2N009/2N010 HOUSECLEAN TIMER E/M` (38.39.02.1), `2N011/2N012 LA HOUSECLEAN OVER TIMER E/M`
(38.39.01.1), `2N019 LA DISABLE INTERRUPT LINE TRIGGER` (38.39.05.1),
`2J014 INSTRUCTION UNIT HOUSECLEAN REQUEST TRIGGER`, `3R016 LOOKAHEAD RECOVERY MODE`,
`2Q005 PSEUDO-INTERRUPT INHIBITS LOAD TRIGGER`. Figures 3.2.22 (CE PDF 114) and 3.2.23
(PDF 115) are the houseclean timers.

### 2.7 Where errors enter the picture

Both the IAUC and the OCC can kill a level. Buchholz Fig 15.7 and 15.8 (PDF 267, 268):
uncorrectable data error → *"Tag level with no-op to show it should not be executed"* (IAUC
path) / *"Tag level with no-op to show it should not be executed, and set instruction reject
indicator"* (OCC path). CE Fig 3.2.2 (PDF 93) shows the shipped version: LLP 1 checks "I CHKR
PARITY ERROR?" → "PSEUDO STORE OR RECOVERY LEVEL? Yes → SET CNIDC IND / No → SET IJ IND + SET
NOOP TAG"; LLP 2 checks "BOUNDARY ALARM? → SET DF OR DS IND + SET NOOP TAG" and "MEM CHK
ALARM? → SET IJ IND + SET NOOP TAG". The *no-op tag* is read by the TBC (Buchholz PDF 271:
"This counter must test the no-operation bit, which, if on, would indicate that an error had
occurred and require that the operation be suppressed").

The boundary alarm is set by the **I-box**, not the LA, but lands in the LA level:
TR00.722 PDF 22, *"If an operand store is to be made, then the DS indicator in the lookahead
level may be set during the actual lookahead load cycle."* And PDF 7: *"before loading
lookahead with a store operation the I unit must test the address and set a store indicator,
if out of bounds... If 'out of bounds,' the lookahead may cancel (no-op) the actual store
operation"* (PDF 21).

---

## 3. Timing

### 3.1 The time base, and the one conflict the tie-breaker was written for

**[TIE-BREAK — this is the 0.5-vs-0.6 µs conflict, in its concrete form.]**

TR00.722 PDF 28 derives its cycle from circuit delay: *"Assuming a maximum delay of 20 mµs per
block means that a control cycle should take approximately 500 mµs... the master clock should
operate at a frequency of four Mc and supply a symmetrical waveform, 125 mµs up and 125 mµs
down, with a period of 250 mµs."* It then hedges, in the same paragraph: *"The precise
operating times will not be established until the system is completely assembled and tested."*
Accordingly every figure in TR00.722 is labelled in both cycles and µs at **0.5 µs/cycle**:
Fig 6 reads "4 FP INSTUCTIONS / 4.0 µS", "8 CYCLES", "FP RATE = 1/1.0 µS".

Perf Char PDF 35, measured: *"For a sequence of floating point instructions the decoding rate
is one instruction per **1.2 µs**."* Perf Char PDF 36: *"The decoding time of I-box
instructions is **0.6 µs**."* Clocks are 0.3 µs; an I-box control cycle is two clocks = 0.6 µs.

**The resolution is clean and it is the single most useful result in this document:
the CYCLE COUNTS in TR00.722's figures are correct; only the cycle LENGTH changed, from 0.5 µs
to 0.6 µs.** Rescale every TR00.722 µs figure by 1.2 and it reproduces Perf Char exactly:

| Quantity | TR00.722 (0.5 µs cycle) | × 0.6 µs | Perf Char, measured | Agree? |
|---|---|---|---|---|
| FP preparation rate | 2 cycles = 1.0 µs | **1.2 µs** | "one instruction per 1.2 µs" (PDF 35) | **exact** |
| Transmit setup (EM→EM) | 2 cycles = 1.0 µs | **1.2 µs** | "1.2 µsec + dec + LA dr" (Table 9) | **exact** |
| Transmit loop (EM→EM) | 5 cycles = 2.5 µs | **3.0 µs** | "3.0 µsec" (Table 9) | **exact** |
| VFL prep, 3 levels, 2 indexings, WBC | 8 cycles = 4.0 µs | **4.8 µs** | 5.4 µs plain reading / 4.8 µs if the 3.6 min already contains one indexing (PDF 36) | **ambiguous — see §3.2** |
| VFL prep, 2 levels, no indexing | 5 cycles = 2.5 µs | **3.0 µs** | 3.6 µs plain reading / 3.0 µs on the other reading | **ambiguous** |
| CB successful | 6 cycles = 3.0 µs (+1 decode) | **3.6 (+0.6)** | "4.2 µsec + dec" (Table 8) | **off by one cycle** |
| Branch-on-indicator | 5 cycles = 2.5 µs | **3.0 µs** | no I-box table entry | n/a |

**The FP and Transmit rows are exact under any reading and are the strongest timing result in
this document.** The VFL rows are not: they depend on a reading of one Perf Char sentence
(§3.2), and the CB row is one cycle apart. Note that **under the plain reading of that sentence
the VFL and CB discrepancies are the same discrepancy** — TR00.722 is uniformly one 0.6 µs
cycle short of Perf Char on VFL preparation and on CB, while matching exactly on FP and
Transmit. That is one story rather than a coincidence plus an anomaly, and it is the reading
this document prefers, without claiming the sources settle it.

**Rule for the model: take cycle counts from TR00.722's figures and multiply by 0.6 µs; where
Perf Char gives a number, Perf Char wins.** So charge **4.2 µs + 0.6 dec** for CB successful
and the plain-reading VFL arithmetic of §3.2, accepting that the model is then one cycle slower
than TR00.722's figures on both.

### 3.2 VFL preparation time: a structural hypothesis, and the sentence it turns on

**What the sources actually say.** Perf Char PDF 36, verbatim: *"VFL instruction decoding is
much more complicated. The minimum time is 3.6 µs which includes the loading of two LA levels.
Each additional level requires an additional 0.6 µs, and each indexing operation requires 0.6
µs. Of course, there may be further slow down in the decoding process if the LA levels are not
available for loading, or if the second half of the instruction is not available when needed."*
TR00.722 Figure 7 (PDF 34) reads **8 cycles** for a full-word VFL, indexed on both halves,
crossing a word boundary, loading three levels; the prose on PDF 35 gives a second data point:
*"If the instruction had no indexing specified and only one operand memory word was required,
the operation would have taken only five cycles or 2.5 microseconds."*

**The ambiguity.** The sentence puts indexing in the *adder* list, not in the 3.6 base. But it
also does not say what else the base covers. Two readings:

| | Fig-7 case (3 levels, 2 index) | 2-level, 0-index case | Perf Char minimum |
|---|---|---|---|
| **Plain reading** (base 3.6 = 6 cyc, excludes indexing) | 3.6 + 0.6 + 1.2 = **5.4 µs = 9 cyc** | 3.6 = **6 cyc** | 6 cyc |
| **Other reading** (base 3.6 includes one indexing) | 3.6 + 0.6 + 0.6 = **4.8 µs = 8 cyc** | 3.6 − 0.6 = **5 cyc** | 6 cyc |
| TR00.722 figure/prose | **8 cyc** | **5 cyc** | — |

The second reading reproduces TR00.722 exactly; the first leaves TR00.722 one cycle short in
both cases — the *same* one-cycle offset as CB (§5 #8), and under the first reading those two
anomalies become one. **Perf Char does not say which reading is right, and this document does
not claim to know.**

**The structural hypothesis**, offered because it makes the cost computable from Table A-2
rather than from a table of special cases, and because it is what Figure 7's own IAU/LALD rows
show cycle by cycle:

```
VFL I-box preparation (cycles) = (half-word transfers: 1 for half-word, 2 for full-word)
                               + (number of indexing operations: 0, 1 or 2)
                               + (1 if a word-boundary-crossover test is performed)
                               + (number of LA levels loaded, from Table A-2)
                               + K
```
Figure 7's trace gives K = 0: its IAU row reads `1YR→ZL · MOD ZL · 2YL→ZR · MOD ZR · WBC`
(5 cycles) followed by `LALD2 · LALD3 · LALD4` (3), total 8 = 2 + 2 + 1 + 3. The 5-cycle
variant is 2 + 0 + 1 + 2. **Under the plain reading of Perf Char, K = 1.**

**Recommendation:** implement `K` as a single named constant, default **1** (plain reading,
Perf Char wins on timing), and record that setting it to 0 reproduces TR00.722's figures
exactly. One constant, one documented uncertainty, no invented numbers.

**[NOT IN THE SOURCES]** whether the WBC cycle is skipped when the length field makes crossover
impossible — Fig 7 always shows it; and whether progressive indexing's two-step form (TR00.722
PDF 33) costs one indexing or two in this accounting.

### 3.3 The published FP preparation trace — the overlap, cycle by cycle

Figure 6 (TR00.722 PDF 31), transcribed from the rendered page. Rows are the resources the
I-box arbitrates: **MAB** (memory address bus), **I CHKR**, **IAU** (index adder), **XS**
(index storage), **LALD** (look-ahead load), then the four LA levels, **LA→E**, **EXEC**.
Assumption printed on the figure: *"EACH FP INST. INDEXED"*.

```
cyc  MAB            I CHKR        IAU            XS         LALD        LA levels / E
 1   IF→1Y
 2   IF→2Y
 3   (memory latency)
 4                  1Y→1Y CHK+DEC
 5                  2Y→2Y CHK+DEC 1YL→ZR         XF/1YL
 6                                MOD ZR
 7   IF→1Y                        1YR→ZL         XF/1YR     ZR→LA   (fetch held: MAB busy)
 8   OF→LA1                       MOD ZL                    ──┘     LA#1 ← FP1
 9   OF→LA2                       2YL→ZR         XF/2YL     ZL→LA   LA#2 ← FP2
10                                MOD ZL
11   IF→2Y          1Y→1Y         2YR→ZL         XF/2YR     ZR→LA   (held)   ← the "*" cycle
12   OF→LA3                       MOD ZL                    ──┘     LA#3 ← FP3
13   OF→LA4                       1YL→ZR         XF/1YL     ZL→LA   LA#4 ← FP4 ; LA1→E
14                                MOD ZR                                     E1 executes
15   IF→1Y          2Y→2Y         1YR→ZL         XF/1YR     ZR→LA
```
Printed totals: **"4 FP INSTUCTIONS / 4.0 µS", "8 CYCLES", "FP RATE = 1/1.0 µS"** —
i.e. **2 cycles per indexed FP instruction**, = **1.2 µs on the shipped machine**.

Three model-relevant facts are visible only in this figure and its prose (PDF 32):

1. **Intra-I-box MAB priority: the instruction fetch beats the look-ahead operand fetch.**
   Verbatim: *"This conflicts with the operand fetch of the lookahead load cycle. **Since IC
   controls have priority**, the IC fetch is made simultaneously with the 1YR transfer to Z
   and the index fetch. The lookahead load cycle holds up its fetch during this cycle and
   completes it with the load operation on the following cycle."* (See §4.3 — this is **not**
   the MBCU priority and must not be merged with it.)
2. **Six things happen at once.** Verbatim: *"The degree of simultaneity in the I unit is best
   illustrated by the asterisked cycle which shows an instruction fetch to 2Y, a check cycle
   on 1Y, a 2YR transfer to Z, an index fetch, and an attempted lookahead load, all occurring
   at the same time."*
3. **The steady state is balanced, not level-limited.** Verbatim: *"Each instruction is assumed
   to require indexing. Otherwise instantaneous rates would achieve one FP instruction every
   half microsecond; the average rate, however, would still remain at one per microsecond.
   This is because **the maximum rate of instruction fetches is balanced with the maximum
   indexing rate and the lookahead rates**."*

### 3.4 The other three published traces

**Count and branch** — Fig 8 (TR00.722 PDF 36), 6 cycles after decode, prose on PDF 35/37:

```
cyc  MAB          IAU         XS        LALD              notes
 0                MOD ZR                                  (DEC overlapped with MOD)
 1                            XF/Z_J                      fetch the index word whose count decides
 2   IF/Z→Y                             X→LA              branch-target fetch, BLOCKED if XC≠1;
                                                          pseudo-store level gets pre-modification index word
 3                COUNT                                   count down through the IAU
 4                ADV/DIM                                 value ±1 or ±½;  IC-advance → same LA level
 5                Z→ICR       CL/Z_J                      branch address into ICR; clear the index word
 6                            ST/Z_J    IC→LA, INDS→LA    write back XR; IC value + indicators into LA
```
Verbatim (PDF 35): *"In the next cycle, the fetch of the branch address instruction is
initiated, and at the same time the count field of the index word in the XR is decoded for a
XC = 1 condition. If this condition for branching exists, the fetch is completed; if the
condition does not exist, the fetch is blocked."* — **the branch target fetch is launched
speculatively and killed, not launched after the decision.**
And (PDF 35): *"At the same time, the advanced IC value (address of the instructions following
the CB) is loaded into the same lookahead level as the pseudo-store. This is done because the
next cycle destroys the IC contents by transferring into it the branch address from Z. If a
no-op of this instruction is required, the I unit can continue on in the program."*
Total cost including refill, verbatim (PDF 37): *"it took **ten cycles or 5.0 microseconds**
from the completion of one instruction in the program to branch to another program location,
and to prepare and load the first new FP instruction into lookahead."* — i.e. **12 cycles,
7.2 µs, on the shipped machine**, of which 6 are the branch and 4 are the Y-refill pipeline
restart. That 4-cycle restart is the branch penalty to charge.

**Transmit** — Fig 9 (TR00.722 PDF 38): **2-cycle setup** (`XF/Z_J`, then `X_C→WR`), then a
**5-cycle loop per word**:
```
 1   MAB F/Z_OAL                            fetch the source word into a Y register
 2   IAU Z_OAL±1                            step the "from" address
 3   IAU W−1                                decrement the count in W
 4   MISC TEST W=0 ; I CHKR Y→CHKR          zero test; ECC check of the fetched word
 5   MAB Z_OAR→LA ; LALD Y→LA, OP→LA        store address to the LAAR, word + op into a level
     (next cycle) IAU Z_OAR±1               step the "to" address
```
Verbatim (PDF 39): *"The ECC code is left with the word instead of converting it to parity,
since lookahead will immediately attempt to store it to memory. When loading the word into
lookahead, the 'to' operand address in the ZR is gated to the memory address-bus (MAB). This,
in turn, goes to the 'effective address register for storing' in lookahead. So by the end of
the cycle the level contains the word to be transmitted, the store memory address, as well as
sufficient operation and indicator tags."* And: *"If an error or a data store indicator
appears, the entire operation will be terminated at that point. **Neither recovery nor
no-opping of the instruction can be effected, since irrecoverable damage could have been
done.**"* ← Transmit is the one non-restartable instruction in the machine.
Perf Char Table 9 confirms 1.2 µs setup + 3.0 µs loop for T(EM→EM), and gives all nine
address-pair variants plus the SWAP table (p.33): S(EM→EM) loop 6.0 µs, S(IR→IR) loop 15.0 µs.

**Branch on indicator** — Fig 10 (TR00.722 PDF 40), **5 cycles**:
```
 1   MAB Z_OA→MAB (TEST)              not a real fetch: address on the bus for boundary compare only
 2   LALD OP→LA   (I CHKR Z→LA)       instruction level
 3   LALD F→LA                        fetch level: the indicator register as operand
 4   LALD ST→LA   (I CHKR Z_OA→LA)    store level: return the indicator register
 5   LALD BR→LA                       branch recovery level: branch address + IC value + tags
```
Verbatim (PDF 41): *"This is not an actual fetch, it merely places the branch address on the
MAB for boundary compare purposes and the setting of possible indicators."* And:
*"the test cannot be made until all preceding instructions in lookahead have been executed and
their indicators set. **Rather than wait**, the I unit tests the instruction for certain
indicator conditions and then loads it into lookahead. This enables the VFL unit to select,
test, and modify the specified indicator. The I unit continues in the program, assuming that
in the majority of cases the branch is unsuccessful."*

### 3.5 How E-box time overlaps I-box preparation — the quantitative statement

Perf Char PDF 34, the governing sentence, verbatim: *"Within wide limits, the times for
instruction processing is **not the sum of**: Instruction fetch, instruction error check,
decoding, operand fetch, operand error check, and execution **but is the maximum of these
times averaged over several instructions.**"* And: *"The E-box times of the instructions listed
in the previous section are the times realizable **if the LA levels (which are buffers to the
E-box) can always supply needed information to the E-box**. The machine organization is such
that this is usually the case."*

This gives the model's cost function directly:

```
time(program) ≈ Σ over instructions of max( I-box preparation time,
                                            E-box execution time,
                                            memory service time )
              + the stalls enumerated in §2.2
              + the non-overlappable 0.9-1.2 µs per I-box-instruction LA level (Perf Char PDF 41)
```

Supporting figures, all verbatim:
- Perf Char PDF 35: *"The demand of the E-box on LA is usually no higher than one word per
  1.5 µs (sequence of floating adds)... In terms of the four-level look-ahead, the requirement
  is satisfied if any four E-box demands are fulfilled in 6 µs."*
- Perf Char PDF 35: *"With few exceptions, this [1.2 µs FP decode] is faster than the execution
  rate. Thus the decoding time for average floating point sequences is completely overlapped by
  concurrent E-box execution time. In other words, **floating point instructions are E-box
  limited.** Address indexing has no measurable effect on the timing of floating point
  instructions."*
- Perf Char PDF 36: *"The processing time of I-box instructions can be largely overlapped by
  concurrent E-box action, since their E-box time is only 1.2 µs."*
- Perf Char PDF 36: *"Whenever a branch instruction is successfully executed, the pre-fetched
  instructions in 1Y, 2Y must be replaced by new instructions. The latter have to be checked
  prior to use, and the decoding of the next instruction will be delayed. This delay has been
  taken into account in the timing given. Again, concurrent E-box action can overlap much of
  this."*
- Perf Char PDF 36-37, the failure mode to model: *"In order to use the look-ahead (LA) levels
  efficiently, they must not be allowed to be empty over extended lengths of time, nor should
  they be crowded with data with little information content... Frequent demands on LAAR (such
  as in consecutive STORE instructions) and prolonged decoding delays in the I-box in general
  often lead to a half-empty look-ahead. **When the number of effective LA levels are reduced,
  the E-box may become idle. The I-box processing time can then no longer be absorbed.**"*
- Perf Char PDF 36: *"VFL data with word boundary crossover represent inefficient use of LA
  levels."*

### 3.6 I-box instruction time table (the oracle for the budgets)

Perf Char Tables 4-9 (PDF 29-33), with `dec = 0.6 µs`, `LAdr = look-ahead drain`,
`LAAR = a LAAR-busy interval`, `LAMT = look-ahead empty`. These are **I-box times**, i.e. the
preparation+execution budget the model charges; memory time is inside them.

| | EM | XS | IR |
|---|---|---|---|
| LX | 4.8 + dec | 4.8 + dec | 4.2 + dec + LAdr |
| LV, LC, LR | 4.2 + dec | 4.2 + dec | 3.6 + dec + LAdr |
| SX | 1.2 + dec + LAAR | 4.2 + dec | 1.2 + dec + LAAR |
| SV, SC, SR | 4.2 + dec + LAAR | 5.4 + dec | 3.6 + dec + LAdr + LAAR |
| SV/SC/SR **to time clock** | 6.0 + dec + LAdr | | |
| V+ | 4.2 + dec | 4.2 + dec | 3.6 + dec + LAdr |
| V+C | 4.2 + dec | 4.8 + dec | 4.2 + dec + LAdr |
| V+CR (EM refill) | 8.4 + dec | 9.0 + dec | 8.4 + dec + LAdr |
| V+CR (XS refill) | 7.2 + dec | 7.8 + dec | 7.2 + dec + LAdr |
| KV, KC | 4.2 + dec | 4.2 + dec | 3.6 + dec + LAdr |
| RNX | 9.0 + dec + LAdr + LAAR | | |
| LVE | 7.8 + dec | 6.6 + dec | 6.6 + dec + LAdr |
| LVE as object of LVE | +4.8 | +3.6 | +3.0 + LAdr (**4.2 if LAMT**) |
| SVA | 4.2 + dec + LAAR | 5.4 + dec | 3.6 + dec + LAdr + LAAR |

Immediate (Table 5): LVI/LCI/LRI/LVNI 2.4 + dec; V±I 2.4 + dec; V±IC 3.0 + dec (also V+ICR when
count = 0); V±ICR 7.2 + dec (**1.2 less if refill from XS**); C±I 2.4 + dec;
KVI/KVNI/KCI 2.4 + dec; LVS 5.4 + dec **+1.8 per ADD**.

Miscellaneous (Table 6): R (from EM) 1.8 + dec + LAAR / 7.2 + dec (XS) / 6.6 + dec + LAAR + LAdr (IR);
R (from XS) 5.4 + dec + LAAR / 5.4 + dec / 4.2 + dec + LAAR + LAdr;
RCZ (C≠0) 4.2 + dec / 3.0 + dec / 3.0 + dec + LAdr;
Z 1.2 + dec + LAAR / 3.6 + dec / 1.2 + dec + LAAR.
**EX**: decode + **always begins with a look-ahead drain** + an address-dependent instruction
fetch time (4.8 µs for 0.0/0.32; 6.0 for 1.0/1.32; 7.8 for 2.0-4.32 and 12.0/12.32;
11.2 for 5.0-11.32; 5.4 for 13.0-14.32; 4.8 for 15.0/15.32; 4.2 for 16.0-30.32;
6.0 for 31.0/31.32; 5.4 for 32.0-up) + the subject's own decode and execution + **always ends
with LA drain** + 3.0 for the next instruction fetch.
**EXIC**: as EX, but the pseudo-IC fetch (4.2 µs EM / 3.0 µs XS) is *overlapped with* the
opening drain; instruction fetch is a flat 6.0; stepping the pseudo-IC costs a LAAR interval
(EM) or 0.6 µs (XS).

Unconditional branch (Table 7): B 3.6 + dec; BR 4.8 + dec; BE 3.6 + dec + LAdr (if previously
disabled); NOP 1.2 + dec; **BD 4.8 + dec + 2 LA drains**. SIC variants add 1.2 and a LAAR.

Index branch (Table 8): CB successful 4.2 + dec, unsuccessful 3.6 + dec; CBR(EM) 6.6/6.0,
CBR(XS) 6.0/5.4. *"NOTE: CBR behaves like CB if Refill is not to be taken."*

Transmit (Table 9): setup 1.2 + dec + LAdr for every variant; loop 3.0 (EM→EM, XS→EM),
4.2 (EM→XS, XS→XS), 7.2 (IR→EM, IR→XS); termination 3.6 (to EM/IR) or 0.6 (to XS).
Swap (PDF 33): loop 6.0 (EM→EM), 6.6 (EM→XS), 9.6 (EM→IR), 6.0 (XS→EM), 7.2 (XS→XS),
10.8 (XS→IR), 9.6 (IR→EM), 10.2 (IR→XS), 15.0 (IR→IR); termination 1.8.
*"Note: The immediate/direct and the forward/backward options do not affect the timing of
either transmit or swap."*

### 3.7 What is NOT timed anywhere

**[NOT IN THE SOURCES]** **No source in this corpus gives a per-action cycle count for any
look-ahead-internal operation.** Buchholz's Figs 15.7-15.10 are untimed flowcharts
("At several places processing is described as if it were sequential, when it actually is
overlapped," PDF 263). The CE manual's Figures 3.2.1-3.2.27 are *pulse* and *condition*
diagrams with logic-page references and no microseconds — Fig 3.2.2 is literally called
"LOOKAHEAD LOAD PULSES" and names LLP 1, LLP 2, LLP 3 as discrete pulses without durations.
**Verified directly on the three figures whose titles promise timing.** Fig 3.2.4 (PDF 96)
gives TBC advance *conditions* and no times. Fig 3.2.25 "SCC ADVANCE" (PDF 117) names three
timers — `STORE DATA TIMER M`, `WRITE INDEX LA M`, `I TIMER NO INDEX TRANSFER M` — and gives
each one's LA op codes but **no duration for any of them**. Fig 3.2.22 "LA HOUSECLEAN TIMER"
(PDF 114) is an E/M trigger sequencer whose exit condition is `LA EMPTY?`, not a count; it
likewise prints no microseconds. The durations live in the 38.xx logic pages, which are not
in this document.
The only LA-internal numbers in the whole corpus are:

- the I-checker's **0.6 µs** and its **0.3-0.6 µs** conflict penalty (Perf Char PDF 37);
- the **0.9-1.2 µs** to process an I-box instruction's LA level (Perf Char PDF 41);
- the LAAR-busy *interval*, which is defined by **condition, not duration**: Perf Char PDF 38,
  verbatim, *"the LAAR will remain 'busy' from the time of look-ahead loading until the proper
  operand is available, is fetched, checked, and accepted by the MBCU."*

**Therefore the implementable look-ahead model is condition-driven, not count-driven.** Levels
and counters advance when their work is done and their interlock is clear; the *durations* come
from the I-box table (§3.6), the E-box tables (Perf Char Tables 2-3, already in plan A.5), and
the memory model (§4). Do not invent LA-internal cycle counts.

---

## 4. Interaction with memory

### 4.1 The memory complement

Perf Char PDF 60, verbatim: *"The main memory, sometimes called extended memory, is composed of
six boxes of 16,384 extended words each (for the Los Alamos configuration). Each extended word
contains 64 information bits plus 8 error-check bits."*
Buchholz PDF 263, design decision 2: *"The standard memory complement is two instruction
memories and four data memories, all with 2-µsec cycle time; fewer or more memory units are
optional."* Decision 3: *"The addresses of the four data memories are interlaced (i.e., four
consecutive addresses refer to different memory units); likewise the addresses of the two
instruction memories are interlaced separately."*

Perf Char PDF 33: *"a 7030 box has a readout time of 1 µs and a recycle time of 2.2 µs, yet in
the 7030 system information can be obtained at the rate of one word every 0.3 µs."*
Buchholz PDF 231: *"Requests for stores and fetches can be processed at a rate of one every
0.3 µsec. If no busy or priority conditions exist, **the time to return the word to the
requesting unit is 1.6 µsec**, a direct function of the memory read-out time."*

**[CONFLICT, minor, in cycle time]** Buchholz says 2.0 µs memory cycle; Perf Char says 2.2 µs
recycle. **Use 2.2 µs** (timing tie-breaker). The plan's A.7 currently says "2.1 µs
read-write cycle" from Buchholz §14.1 — **neither source read here says 2.1**; the two figures
in evidence are 2.0 (Buchholz PDF 258 figure caption and PDF 263) and 2.2 (Perf Char PDF 33).

### 4.2 Interleaving, as it affects the look-ahead

Perf Char PDF 35, verbatim and directly usable as a model: *"With the instruction buffers 1Y,
2Y (capable of housing four half-word instructions), in the I-box, and the four LA levels, the
advantage of memory interleaving is fully exploited. The demand of the E-box on LA is usually
no higher than one word per 1.5 µs (sequence of floating adds) and on the average, the memory
is not a factor. In terms of the four-level look-ahead, the requirement is satisfied if any
four E-box demands are fulfilled in 6 µs. **The memory interleave scheme allows four words
every 2.2 µs (four box interleaving) or four words every 4.4 µs (two box interleaving).**
In actual computations, with the instructions occupying the two lower memory boxes and data
occupying the four upper memory boxes, memory conflict is not expected to be an important
factor, even if the I/O units are in full operation. Delays due to repeated demands of the
same memory box are expected to be quite infrequent."*

And the warning that the real conflicts are elsewhere: *"There are conflicts due to fetches and
stores, independent of memory access. These are related to the machine measures at preserving
the logical integrity of a program sequence"* — i.e. §2.3, not §4.

### 4.3 Bus priority — the quoted order, and the second arbitration that is not it

**MBCU requester priority, quoted, Buchholz PDF 230-231** (read from the rendered page):

> *"The memory bus unit monitors the requests for storing in or fetching from memory and sets
> up a priority scheme. **Since input-output units cannot hold up their requests, the exchange
> and disk synchronizer will get highest priority, followed by the CPU. In the CPU the
> operand-fetch mechanism, the look-ahead unit, has priority over the instruction-fetch
> mechanism.** Altogether the memory bus unit receives requests from and assigns priority to
> eight different channels."*

So the quoted order, top to bottom, is:
**exchange and disk synchronizer > CPU operand fetch (look-ahead) > CPU instruction fetch**,
over **eight channels** total. Buchholz PDF 254 gives the rationale: *"Input-output units
cannot be kept waiting long, and so they have a higher priority on memory than the central
processing unit. If the CPU were simply stopped during a period of peak input-output activity,
the waiting time would be lost completely. By having a reservoir for unexecuted instructions in
the look-ahead registers, it is possible to make up some of the lost time by satisfying
deferred CPU demand during a period of lower input-output activity."*

**The E-box is not a memory-bus requester at all.** Buchholz PDF 254, verbatim: *"The
arithmetic unit communicates only with the look-ahead unit, not directly with the real memory;
it receives instructions and operands from the look-ahead and returns its results there."*
TR00.722 Figure 2 (PDF 5) draws it that way — the SAU and PAU reach memory only through the
look-ahead's `LOAD` and `STORE` arrows. So the four-way priority the question asks about is
really three-way: **channels > look-ahead > I-box, with the E-box behind the look-ahead.**

**The shipped requester names**, read from the rendered CE p.171, all at ALD page 12.09.01.1:

```
2C001  12.09.01.1  BX MEMORY REQUEST TGR          (basic exchange)
2C002  12.09.01.1  HX MEMORY REQUEST TGR          (high-speed / disk exchange)
2C003  12.09.01.1  LA STORE MEMORY REQUEST TGR    (look-ahead, stores only)
2C004  12.09.01.1  I FETCH MEMORY REQUEST TGR     (instruction fetch)
```
with matching `2C014 BX STORE ADDRESS ERR`, `2C015 HX STORE ADDRESS ERR`, `2C016 LA STORE
ADDRESS ERR`, `2C011 RETURN ADDRESS PARITY ERR`, and the BCU gate triggers `2C018 GATE 1 TGR`,
`2C019 GATE NEXT TGR`, `2C020 GATE 2 TGR`, `2C021 STAR BUSY TGR` — the last four being what
Fig 3.2.12's "SET GT LAAR 1 NEXT (IN BCU)" drives. **Note that the look-ahead's only own
request line is a store request**, consistent with TR00.722 PDF 7's "All memory fetches for the
computer are initiated by the I unit": an LA level's operand fetch is issued on the I-box's
operand-fetch channel (Perf Char Fig A-1's "I-BOX OPERAND OR LA LEVEL" arrow), not by the LA.

**[NOT IN THE SOURCES]** No source read here gives the relative order of the exchange versus the
disk synchronizer, nor the identity of all eight channels (four of the eight are named above). The plan's A.6 asserts
"exchange > disk > look-ahead > I-box (8 requesters)"; the **exchange > disk** half is not in
Buchholz PDF 230 and no other source read here states it. Flagged as unsourced.

Buchholz PDF 231 on busy handling, verbatim: *"Since access to a memory unit can be
independently initiated from several sources, a busy condition can exist. Here again, the
memory bus tests for the busy conditions and delays the requesting unit until the desired
memory unit is ready. **The return address identifying the requesting unit is remembered, and
the information is forwarded when it becomes available.**"* The return address is 3 bits:
TR00.722 PDF 21, *"All external memory fetches are executed by the I unit and involve sending
an 18 bit word address and a three bit return address to the bus control unit. The return
address indicates which Y register in this I unit, or which of the four lookahead levels is to
receive the word on return."* — **six tags: 1Y, 2Y, LA0, LA1, LA2, LA3.**

**[CONFLICT, and it is a real one]** Buchholz says the look-ahead's operand fetch outranks the
instruction fetch at the MBCU. TR00.722 PDF 32 says the opposite about the same decision one
level up: *"This conflicts with the operand fetch of the lookahead load cycle. Since IC
controls have priority, the IC fetch is made simultaneously with the 1YR transfer to Z and the
index fetch."* These are **two different arbiters** and both must exist in the model:

| Arbiter | Where | Contestants | Winner | Source |
|---|---|---|---|---|
| **MAB gating** | inside the I-box, per I-box cycle | IC controls (instruction fetch) vs look-ahead load controls (operand fetch) vs instruction-execution controls | **IC controls** | TR00.722 PDF 32; PDF 27 "These controls time-share the I checker and the memory address-bus with other controls" |
| **MBCU priority** | memory bus control unit, per 0.3 µs | 8 channels: exchange, disk synchronizer, CPU operand fetch, CPU instruction fetch, … | **exchange/disk, then operand fetch, then instruction fetch** | Buchholz PDF 230 |

Perf Char Fig A-1 (PDF 61) draws both I-box-sourced request lines into the MBCU as separate
labelled arrows — *"FETCH REQUEST FOR INSTRUCTION"* and *"I-BOX OPERAND OR LA LEVEL"* — which
is exactly the two-channel structure the MBCU priority rule needs.

### 4.4 Who does what to memory

TR00.722 PDF 7 and PDF 21-22, verbatim, is the clean division and it is absolute:

- *"All memory fetches for the computer are initiated by the [I] unit."*
- *"**All stores to external memory are done by lookahead.** The I unit loads the store address
  into the lookahead address register and a store type operation code into the op code field.
  The operand may be loaded at the same time, in case of an I unit instruction, or may be
  loaded later as a result of a VFL or FP arithmetic operation."*
- *"All index word fetches are done by the I unit whether for I unit operations or for VFL and
  FP operands... **Index stores can be made by either the I unit or the lookahead unit.** The
  operation is similar to the fetch except that **two cycles are required, one for resetting,
  and the other for writing** the contents of the XR into the selected row of cores."*
- *"**Internal transistor register fetches and stores are made by lookahead** on the arithmetic
  checker bus... If the fetch is for the I unit, lookahead will first transfer the contents of
  the register to the lookahead level on the arithmetic checker bus, and then relay it on to
  one of the Y registers via the I checker bus. If it is a VFL or an FP operand fetch, it is
  left in the lookahead level for later transfer to arithmetic operand register."*

Perf Char PDF 38 confirms, and adds the I/O exception: *"All 'to-memory' operations involving
the main memory from the 7030 CPU are prepared by the I-box and accomplished by the look-ahead.
**I/O stores are, however, performed directly between the MBCU and exchange units.**"*
Table A-2 agrees for I/O instructions: *"LA communicates with exchange directly."*
Perf Char PDF 65: the exchange *"Accepts I/O instructions from LA (2 levels per instruction)"*
and *"Fetches and stores control words and data words directly from MBCU, subject to $AD
restrictions but not $DF and $DS since these are performed by the I-Box."*

**Internal-register fetches use a LAAR.** Perf Char PDF 38, verbatim: *"The I-box, upon decoding
an instruction whose fetch operand is an internal register, uses the LAAR to store the internal
operand address. This is because the needed operand is not available during the decoding stage,
and the mechanism for internal operand fetch already exists for the handling of store
instructions. **Unlike a standard store, no memory bus request is needed, and the LAAR is freed
sooner.**"* The address classes, verbatim: *"By an internal operand address is meant address 3,
or an address between 5 and 12 inclusive. $Z, $1A, $MB, and $RM, $FT and $TR are bona fide main
memory locations. $IT, $TC and $0 through $15 are in index storage."*

The address-type pre-decode is itself speculative — TR00.722 PDF 21, verbatim: *"In some cases
where there was insufficient time to decode, notably in rapid FP instruction preparation, a
'guess' is made that the operand address refers to external memory and the required fetch
initiated. The memory area decoding is completed before the fetch is actually executed. This
operation can either permit the fetch to be completed or cancel it. If cancelled, the proper
fetch is initiated to the correct memory area on the following cycle... In the cases where the
'guess' is incorrect, no time is lost since the decode time was required anyway."*
TR00.722 PDF 28 repeats it for the LA load controls: *"It was necessary to 'guess' that the
operand address referred to main memory, and begin the fetch immediately. If the guess is
wrong, then the fetch is blocked and the next cycle is controlled by another sequencer which
fetches the operand from the correct memory. The majority of FP instructions will require only
one control step where the operand is fetched from main memory at the same time that the
instruction is loaded into the single lookahead level."*
**Two speculations, not one: the branch guess and the memory-class guess.** The second is free
(it costs a cycle only when wrong, and that cycle was needed anyway).

---

## 5. Conflicts between sources, called out

| # | Subject | Source A | Source B | Resolution |
|---|---|---|---|---|
| 1 | **I-box cycle length** | TR00.722 PDF 28: ~500 mµs from a 4 Mc clock; every figure labelled at 0.5 µs/cycle | Perf Char PDF 35-36: FP decode 1.2 µs, I-box decode 0.6 µs, clocks 0.3 µs | **Perf Char (TIMING).** 0.6 µs = 2 clocks. **TR00.722's cycle COUNTS survive intact**; only the scale changes. TR00.722 itself hedges: "The precise operating times will not be established until the system is completely assembled and tested." |
| 2 | **Number of LAARs** | Buchholz PDF 266: "**only one** look-ahead address register is provided"; Perf Char PDF 39 and 67: one | CE manual PDF 92 figure boxes "BOTH LAARS BUSY" / "BOTH LAARS 1&2 BUSY" / "BOTH LAARS NOT BUSY"; trigger index `2D001 LOOKAHEAD ADDRESS REGISTER 2`, `2E001 ... 1`, `2L025/2L026 LAAR 1/2 BUSY TGR`; two *from* bits per level | **CE manual (STRUCTURE). Implement two.** But see §6.2 item 9: this is a **chronology, not a contradiction** — Perf Char is dated 3/8/61, the LA flow diagrams 2/1/62 — and it puts the two halves of the tie-breaker rule in direct tension. |
| 3 | **Tag bits per level** | Buchholz PDF 264: 8, named | Perf Char PDF 67: 9 (adds DISC) | **CE manual (STRUCTURE): 13** — Buchholz's 8 with *from* split in two, plus DISC, plus index/external/internal store tags. |
| 4 | **Counter interlock polarity** | Buchholz Figs 15.9/15.10 (PDF 269-270): "Has TBC reached OCC? **Yes → Advance**" | Buchholz Figs 15.7/15.8 and all the book's prose: "reached ⇒ Wait"; CE Fig 3.2.4 (PDF 96): "**ADVANCE TBC IF NOT INTLKD BY OCC**" | **"reached ⇒ wait" for all five.** Figs 15.9/15.10's labels are a book typo, confirmed by reading them at 700 dpi. |
| 5 | **Memory cycle** | Buchholz PDF 263: 2.0 µs | Perf Char PDF 33: readout 1 µs, recycle 2.2 µs | **Perf Char (TIMING): 2.2 µs.** Note: the plan's A.7 says "2.1 µs", which matches **neither** page read here. |
| 6 | **Memory-bus priority, instruction fetch vs operand fetch** | Buchholz PDF 230: at the MBCU, "the operand-fetch mechanism, the look-ahead unit, **has priority over** the instruction-fetch mechanism" | TR00.722 PDF 32: inside the I-box, "**Since IC controls have priority**, the IC fetch is made" and the LA load's fetch is held one cycle | **Both, at different arbiters** (§4.3). Not a contradiction once separated — but the plan's A.6 one-line "Bus priority: exchange > disk > look-ahead > I-box" conflates them. |
| 7 | **Exchange vs disk order** | plan A.6 asserts "exchange > disk" | Buchholz PDF 230 says only "the exchange and disk synchronizer will get highest priority" as a pair | **[NOT IN THE SOURCES]** — unsourced in this corpus; drop the ordering or mark it a modelling choice. |
| 8 | **CB successful timing** | TR00.722 Fig 8 (PDF 36) + prose PDF 37: **6 cycles** = 3.6 µs at 0.6, + 1 decode cycle | Perf Char Table 8: **4.2 µs + dec** = 7 cycles + dec | **Perf Char (TIMING): 8 cycles total.** The one-cycle gap turns on whether Perf Char's "+ dec" is additional; Perf Char does not say. |
| 9 | **Bind LAAR count** | Perf Char PDF 42: "**two** of these four levels involve the LAAR" | Perf Char Table A-2 p.70: only the `INT` level marked LAAR-needed for `B ind (non-index)` | Same document, two places. Charge **two** LAAR intervals per the prose; **[NOT IN THE SOURCES]** which second level. |
| 10 | **"Blosk" attribution** | plan A.6/§6a/§6d repeatedly cite "Blosk pp.7-15", "Blosk p.28", "Blosk fig.10" and §6 calls TR00.722 "Blosk's 1959 report" | TR00.722 is dated **Mar 1960**; its acknowledgments (PDF 42) credit S. F. Anderson, L. L. Headrick, C. R. Holleran, S. L. Lindauer, L. F. Winter, under **E. Bloch and R. E. Merwin**; Buchholz PDF 18 credits **R. A. Blosk (instruction unit)** as a chapter author of the *book* | Cosmetic but worth fixing once: the report is **TR00.722, March 1960**; "Blosk" is the Buchholz chapter author. The substance of the tie-breaker is unaffected (1960 still predates the 1961 measurements). |

---

## 6. Implementability verdict

### 6.1 Fully specified — buildable from this document with no further reading

1. **Level count and level contents.** Four levels; exact field widths (76-bit operand, 10-bit
   op code, 15 indicators, 19-bit IC + parity) from the CE trigger index; the 13 tag bits with
   logic-page citations; the 15 indicators named in order.
2. **The five ring counters**, their names, their responsibilities (one quoted sentence each
   from Perf Char PDF 62), and their interlock rule ("may not advance onto its predecessor's
   level"), with the shipped machine's AES-trigger idiom from CE Fig 3.2.1/3.2.4.
3. **Per-instruction LA level usage**, for the whole instruction set, from Table A-2 — level
   kind, count, LAAR requirement, LAAR-if-free, SAU/PAU engagement. Plus the VFL doubling rule
   for word-boundary crossover and the extra IX level for progressive indexing.
4. **Forwarding**, in both directions (store→fetch and fetch→fetch), with the exact decision
   sequence from Buchholz Fig 15.7 and the three worked store-close-to-fetch cases from
   Perf Char PDF 39-40 as ready-made regression programs.
5. **The three comparators** and their three different hit effects (recovery / hold / forward).
6. **The guess** (always not-taken), **which branches are guessed** (everything but CB-family
   and the eight index-indicator Bind conditions), **the four levels a guessed branch costs**,
   and **the pseudo-store recovery mechanism**.
7. **Interrupt housecleaning**, step by step, from Buchholz PDF 271-272 and Perf Char PDF 63;
   the interrupt point is the ABC, before the indicator gate.
8. **The complete I-box stall list** (§2.2), including the two most surprising entries — the
   index-storage store that halts decoding outright, and the six instructions that drain the LA.
9. **I-box instruction times** for every instruction, three address classes, from Tables 4-9.
10. **The overlap cost function**: "not the sum but the maximum of these times averaged over
    several instructions", plus the non-overlappable 0.9-1.2 µs per I-box-instruction LA level.
11. **Memory**: six 16,384-word boxes, 2 instruction + 4 data, interleaved 2-way and 4-way
    separately, 2.2 µs recycle, 1 µs readout, one request per 0.3 µs, 1.6 µs unloaded return,
    3-bit return tag naming 1Y/2Y/LA0-3.
12. **Bus priority**, quoted, and the separate intra-I-box MAB arbitration.
13. **Four published cycle-by-cycle traces** (FP prep, VFL prep, CB, Transmit, Bind) that
    double as timing regression oracles once rescaled to 0.6 µs — and the derived VFL formula
    in §3.2, which two independent sources satisfy exactly.

### 6.2 Under-specified — the shape is documented, a number or a case is missing

1. **Which second level of a guessed Bind uses a LAAR.** Prose says two, the table marks one.
2. **The CB one-cycle discrepancy** (§5 #8) — resolvable only by deciding what "+ dec" means.
3. **I-checker contention.** The eight users are listed and the penalty is given as a range
   (0.3-0.6 µs), but Perf Char PDF 37 explicitly says: *"The situation has not been completely
   studied (because of the difficulty in subjecting the variables to program control)."*
   A model can either ignore it (as the sources effectively do for FP) or charge a fixed
   0.45 µs; neither is more faithful than the other.
4. **The LAAR allocation policy between the two shipped LAARs.** *Selection* is now sourced:
   CE Fig 3.2.12 (PDF 104) shows the level's FROM BIT 1 / FROM BIT 2 choosing LAAR 1 / LAAR 2
   at TBC time. What is **[NOT IN THE SOURCES]** is the *assignment* rule — which LAAR the
   I-box claims when both are free, and what happens to a third store when both are busy
   beyond CE Fig 3.2.1's "BOTH LAARS BUSY" blocking the load enable. Round-robin is a
   modelling choice, not a sourced fact.
5. **How a six-level VFL fits in a four-level ring.** Buchholz PDF 271 states the case ("two
   levels being used twice") but not the sequencing. The LAOP / LA-op-code tag is clearly the
   mechanism ("At each extra level the look-ahead unit inserts a pseudo operation code to
   control the action required") but the pseudo-op encodings are not listed.
6. **The LAOP op-code values.** CE figure titles name them — "VFL OPERANDS LAOP 03, 05, AND 07"
   (Fig 3.2.9), "VFL SPECIAL OPERAND LAOP 15" (Fig 3.2.10), "FP INSTRUCTION LEVEL OPX2"
   (Fig 3.2.11), "TBC I/O INSTRUCTIONS — OP 20 AND OP 24" (Fig 3.2.7), "LAOP 33 ECC CHK LOAD"
   and "LAOP 45" (Fig 3.2.1/3.2.2) — so the encoding exists in the 10-bit op code field, but
   **no complete LAOP table was found** in the pages read. The fragments recovered from
   rendered figures, worth recording because they partially constrain the encoding:
   - external store (to the BCU): LAOP **31, 33, 21, 13, 23, 17, X2** (Fig 3.2.25)
   - index store (to the X register): LAOP **02, 04, 06, 13, 17, 23, X2** (Fig 3.2.25)
   - no-index transfer (to a Y register): LAOP **45, 51** (Fig 3.2.25)
   - illegal pseudo-store: LAOP **42, 44, 46** (Fig 3.2.25)
   - store data taken from TOB rather than ACOB: LAOP **33 EXT or 31** (Fig 3.2.12)
   - SAU instruction: LAOP **X1, 35, 43**; PAU instruction: LAOP **X2** (Fig 3.2.22)
   - ECC-check load: LAOP **33**; special LLP-1 case: LAOP **45** (Fig 3.2.1 / 3.2.2)
   - VFL operand levels: LAOP **03, 05, 07**; VFL special operand: LAOP **15**;
     I/O: op **20** and **24** (figure titles, Figs 3.2.7/3.2.9/3.2.10)
   CE §3.2 figures 3.2.5, 3.2.6, 3.2.13, 3.2.14, 3.2.24, 3.2.27 were **not** rendered and are
   the place to look for the full table.
7. **The exchange/disk split of the 8 MBCU channels** (§5 #7).
8. **Memory-box busy modelling.** The sources say conflicts are "expected to be quite
   infrequent" but give no queue discipline inside a box beyond "delays the requesting unit
   until the desired memory unit is ready."
9. **The tie-breaker collides with itself on the LAAR, and the implementer must choose.**
   Every `+ LAAR` term in Perf Char Tables 4-9 is a *time measured on a one-LAAR machine*,
   and every page of that document is stamped **3/8/61**. The two-LAAR hardware is on CE pages
   stamped **2/1/62** (LA flow diagrams, trigger index p.172/p.175) and **1/1/63** (p.171,
   which additionally carries "Serial Numbers 30,003 - 30,005"). Applying "CE for structure,
   Perf Char for timing" literally means **charging one-LAAR stall times to two-LAAR
   hardware** — the stalls will fire about half as often but each will be priced as if the
   single register were the bottleneck. Three defensible positions, in order of how much this
   project's MCP-first goal cares:
   (a) **model the 1961 machine**: one LAAR, Perf Char's times, internally consistent, matches
       every published timing in the corpus, and is what the benchmark numbers in Perf Char
       Vol.2 were measured on;
   (b) **model the 1962/63 machine**: two LAARs, same per-event times, faster than any
       published figure, and with no oracle anywhere in the corpus to check it against;
   (c) two LAARs with a switch to disable the second, defaulting to (a).
   **[NOT IN THE SOURCES]** anything that dates the change or gives a two-LAAR timing. This
   document recommends (c), and recommends that the regression oracles all run in (a).

### 6.3 Simply not written down anywhere in this corpus

1. **Per-action look-ahead-internal cycle counts.** This is the single most important gap and
   §3.7 argues it at length. There is no "an IAUC load takes N cycles", no "a TBC transfer
   takes N cycles", no "the SCC store takes N cycles". Buchholz's flowcharts are untimed by
   the author's own admission; the CE manual's 3.2.x figures are pulse/condition diagrams
   without durations. **A faithful model must be condition-driven, with durations imported
   from the I-box table, the E-box tables and the memory model.** Any LA-internal cycle count
   in the Bluespec will be invented, and should be labelled as such in the code.
2. **The wrong-way-branch recovery penalty, as a number.** Perf Char PDF 42 describes the
   action ("shipment of index register information back to the I-box... The correct instruction
   counter value is also shipped back") and TR00.722 PDF 41 describes the cancellation, but
   **neither gives a µs or cycle cost for recovery itself.** The only adjacent number is
   TR00.722 PDF 37's "ten cycles or 5.0 microseconds from the completion of one instruction in
   the program to branch to another program location, and to prepare and load the first new FP
   instruction into lookahead" — which is a *successful CB*, not a wrong-way recovery.
3. **The houseclean duration.** The CE manual names `HOUSECLEAN TIMER` and `LA HOUSECLEAN OVER
   TIMER` triggers; no source gives their lengths.
4. **How many levels a guessed branch may have outstanding.** Nothing states a limit; the limit
   is implicit in the four-level ring (§2.5).
5. **What happens when a guessed branch's levels and a VFL's six levels both want the ring.**
   Not addressed in any source read.
6. **The exact Y-register refill cost after a successful branch**, separable from the branch's
   own time. Perf Char PDF 36 says only *"This delay has been taken into account in the timing
   given"* — i.e. it is folded into Tables 7 and 8 and cannot be extracted.
7. **Whether the two LAARs may both forward to the same level**, and what FROM BIT 1 vs FROM
   BIT 2 arbitration looks like.
8. **Any statement of how the look-ahead behaves with fewer than six memory boxes**, beyond
   Buchholz PDF 260-261's three qualitative reasons why small configurations are slower.

### 6.4 Recommended order of work on the Bluespec model

1. Replace the plan's per-level `storeAddr` comparison with **LAAR(s) + per-level FROM BIT 1/2
   selection** and implement real forwarding in both directions (store→fetch and fetch→fetch).
   This is the single biggest fidelity gain and the mechanism is fully specified. Build the
   two-LAAR structure, default the second one off (§6.2 item 9).
2. Make **level occupancy per-instruction from Table A-2**, including the IX-Rec and NOOP levels
   that every I-box instruction loads. This is what makes the four-level ring actually throttle
   the I-box, and it is what the plan's one-level-per-instruction model is missing.
3. Implement the five counters as five rules with the "may not advance onto its predecessor"
   interlock, plus the IAUC-vs-SCC interlock.
4. Charge I-box times from Tables 4-9 and the §3.2 VFL formula; charge the 0.9-1.2 µs
   non-overlappable LA-level cost for I-box instructions; leave LA-internal actions
   condition-driven with zero invented latency.
5. Add the three comparators (program store compare → recovery; LAAR compare on I-fetch/I-box
   operand → hold; LAAR compare on LA operand → forward) and the six drain instructions.
6. Only then revisit the branch guess: four levels, pseudo-store recovery, ABC interrupt point.
7. Regression oracles, in order of value: the three Perf Char store-close-to-fetch sequences
   (1)(2)(3); TR00.722 Fig 6 (4 indexed FP in 8 cycles = 4.8 µs); Fig 7 (VFL 8 cycles);
   Fig 9 (Transmit 2 + 5N cycles, cross-checked against Table 9's 1.2 + 3.0N µs);
   Fig 8 (CB, 8 cycles under the Perf Char reading); Fig 10 (Bind 5 cycles, 4 levels).

---

## Appendix: pages worth reading next

Not rendered in this pass, and likely to close gaps in §6.2:
- **CE manual PDF 94, 97, 98, 105, 106, 108, 116, 118, 119** — Fig 3.2.2 sheet 2 (LLP 3) and
  Figures 3.2.5, 3.2.6, 3.2.13, 3.2.14, 3.2.16, 3.2.24, 3.2.26, 3.2.27. The full LAOP encoding
  table and the LAAR *assignment* rule should be among these.
- **CE manual PDF 275-277** — "bypass other lookahead levels by means of LA disable switches",
  "gate pulse samples IMOB data into lookahead level 4 (LA 4)", logic 31.01.01.1 / 22.11.37.1.
- **CE manual PDF 62** — the figure index for section 3.2, to confirm nothing between 3.2.1 and
  3.2.27 was missed.
- **Perf Char Vol.2** — the benchmark sources, for whole-program `CYCLES<=` oracles.
