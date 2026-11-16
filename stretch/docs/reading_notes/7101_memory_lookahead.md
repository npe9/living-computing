> **STATUS: UNVERIFIED FINDING AID.** Written by a reading agent on 2026-11-15
> from page images. Nothing here may be cited as a source: every quote must be
> re-read in the ink (the page image) before it is relied on, as AGENTS.md
> requires. Passages the agent could not read confidently are listed at the end.

# Reading notes: R23-9732 (7101 CPU CE Reference Manual, Jan 63) -- memory timing and look-ahead

Source: `stretch/docs/R23-9732_Manual04_7101_CPU_Jan63.pdf` (297 PDF pages, no usable text layer).
Method: page IMAGES only. Procedure 1 read with the Read tool's PDF renderer and Fig 4.1.1-4
re-rendered with `pdftoppm -r 300 -gray`; look-ahead pages rendered `pdftoppm -r 150 -gray`
(plus 300-dpi crops where stated). `docs/ocr/` was used ONLY to find which PDF pages hold the
timer rows of Table 3.4.1. Nothing in the repository was modified.

## 0. Page numbering -- which numbers the audit uses

**The numbers in `source_audit.md` ("pp.273-279", "pp.95, 99-119") are PDF page numbers, not
printed ones.** This manual has no running printed page number: each page carries a section tag
(`M3-04-2`, `M3-04-3`, `M3-04-4`) and a printed `chapter-page` number that restarts per chapter.
(The audit's "PDF page == printed page" correction at its line 277 is about `C22-6678`, the MCP
guide, not this manual; `clock_unit.md` already cites this manual as "printed 1-4, PDF 275".)
All page numbers below are **PDF pages**, with the printed number in parentheses.

| PDF | printed | section tag | content |
|---|---|---|---|
| 272 | 1-1 | M3-04-4 | Procedure start: "ADJUSTMENT OF STORAGE BUS CONTROL AND CORE STORAGE TIMING" (dated 2/1/62) |
| 273-278 | 1-2 .. 1-7 | M3-04-4 | procedure steps, Tables 4.1.1, 4.1.2 |
| 279 | 1-8 | M3-04-4 | Figures 4.1.1-4.1.4 |
| 280 | 2-1 | M3-04-4 | next procedure (+12VDC power supply) -- not part of this |
| 92 | 2-1/2-2 (fold-out) | M3-04-3 "LA FLOW DIAGRAMS" | Fig 3.2.1 |
| 93-107 | 2-3 .. 2-17 | M3-04-3 | Figs 3.2.2 (2 sheets) .. 3.2.15 |
| 108-113 | fold-outs | M3-04-3 | Figs 3.2.16 .. 3.2.21 |
| 114-119 | .. | M3-04-3 | Figs 3.2.22 .. 3.2.27 |
| 175-178 | (section 3.4) | M3-04-3 | Table 3.4.1 sheets holding the LA timer triggers |

**Note: the procedure begins on PDF 272, one page before the audit's "273".** PDF 272-279 were all read.
The page header does not print the words "Procedure 1"; the title is the header text
"ADJUSTMENT OF STORAGE BUS CONTROL AND CORE STORAGE TIMING", section M3-04-4, pages 1-n
(i.e. the first procedure of section 4). PDF 273 step A.6 refers to a different
"Check Procedure 1 of this manual" (the Sample Pulse Alignment Check).

**"Table 3.4.1's 13 named timers" is a misdescription worth knowing about**: Table 3.4.1 is
"7101 CE CONSOLE INDICATORS" (every console light, by trigger ID, ALD page and console
coordinate). It gives **no duration and no purpose** for any timer; it lists the E/M/EE
TRIGGERS of each timer. Durations exist nowhere on the pages read (see Part B §B.3).

---

# PART A -- Memory timing: "Adjustment of Storage Bus Control and Core Storage Timing" (PDF 272-279)

## A.1 What the procedure is (verbatim)

PDF 272 (1-1):

> "This procedure describes how to check and adjust the timing between core storage units
> (CSU's) and the storage bus control of the 7101 Central Processor Unit, Serial No. 30,004
> and higher. The procedure sets test conditions for each CSU by executing store and fetch
> operations from the CPU, exchange, and disk synchronizer CE consoles and then checking and
> adjusting the fixed and/or tapped delays of the intercommunication lines between the core
> storage and storage bus control units."

> "The storage bus control and CSU timing relationship must be checked and adjusted whenever
> the CPU clock frequency is changed or CPU clock sample pulses are realigned."

Equipment: "Oscilloscope - Tektronix type 551 dual-beam, with type 53/54L, fast-rise,
calibrated preamplifiers."

**There is NO sentence anywhere in PDF 272-279 that defines "the memory cycle", states a
read-data-available time in ns/usec, or describes bus request / accept / return-address /
priority sequencing in words.** The procedure gives adjustment targets only. No "request",
"accept", "return address" or "priority" wording appears on these pages; the only "busy"
is the CSU **Busy trigger** (step B.5). Everything below is what IS printed.

## A.2 Every timing value printed

| # | signal | relation / reference | value | unit | page | verbatim |
|---|---|---|---|---|---|---|
| 1 | SM memory-select timing pulse | width | 200 | nanosec | PDF 273 (1-2) step B.2 | "Adjust SM memory-select timing pulse (measured at card socket pin 11A2H21F, logic 11.12.02.1) so it is 200 nanosec wide and occurs 150 nanosec after leading edge of an SP pulse (measured at card socket pin 11A2K24F, logic 11.12.02.1). The delay lines for these adjustments are on cards 11A2F24 and 11A2F23 (logic 11.12.02.1)." |
| 2 | SM memory-select timing pulse | delay after leading edge of an SP pulse | 150 | nanosec | PDF 273 step B.2 | (same sentence) |
| 3 | Busy trigger (logic 13.05.01) | on-time | 1800 | nanosec | PDF 274 (1-3) step B.5 | "Adjust Busy trigger reset delay line so that Busy trigger (logic 13.05.01) is on for 1800 nanosec. The delay line for this adjustment is on card 01B1B22 (logic 01.12.00.1) of the selected CSU." |
| 4 | data-out-gate pulse (CSU) | width | 290 | nanosec | PDF 275 (1-4) step C.3 | "Adjust data-out-gate pulse (measured at pin A of CSU card 01B1B10, logic 01.12.03.1) so it is 290 nanosec wide by varying delay line on card 01B1C13 (logic 01.12.03.1)." |
| 5 | data-out-gate pulse | not earlier than, after select-memory pulse | 1050 | nanosec (minimum) | PDF 275 step C.3 | "Check data-out-gate pulse (measured at card socket pin 01A1H24B, logic 01.13.00.1) to ensure that it does not occur earlier than 1050 nanosec after select-memory pulse (measured at card socket pin 01B1C06D, logic 01.12.00.1). If time difference is too short, increase delay by adjusting delay line on card 01B1C19 (logic 01.12.00.1)." |
| 6 | IMOB data at 1Y register and at look-ahead level 4 | brackets the **sixth** SP pulse after the SP pulse that initiated gate I | 6th pulse | SP pulses | PDF 275 step C.3 (unnumbered paragraph) | see A.4 |
| 7 | SEL 1Y pulse | brackets the **fifth and sixth** SP pulses after the gate-I SP pulse | 5th-6th | SP pulses | PDF 276 (1-5) step C.4 | see A.4 |
| 8 | SELECT 2Y pulse | brackets the **fifth and sixth** SP pulses | 5th-6th | SP pulses | PDF 276 step C.5 | see A.4 |
| 9 | MEM SEL LA (each of four) | brackets the **fifth** SP pulse | 5th | SP pulses | PDF 276 step C.7 | see A.4 |
| 10 | warm-up | 30 | minutes | PDF 272 A.1 | "Allow warmup period of 30 minutes for CSU's, CPU, exchange, disk synchronizer, and oscilloscope." (not a machine timing) |

**The SP pulse period is NOT printed on these pages.** `clock_unit.md` §5.2 derives 0.3 us
from other pages (Table 2.1.1 typing 11A2K24F as ABAB); these pages only number SP pulses 0-6.

**No memory read-write cycle time is printed.** The only "cycle-like" figure is item 3, the
Busy trigger's 1800 nanosec. The page does not say what the Busy trigger gates (that it is
"CSU busy to the bus control" is an inference from its name and ALD page 13.05.01, which is in
the 13.xx bus-control range, with its reset delay line physically in the CSU, 01B1B22).

## A.3 The sequences, as steps (verbatim adjustment targets)

### Store path (PDF 273-274, "B. Timing of Store Operations"; test instruction: Store Index (SX) to CSU A0 in both half-words of PANEL KEYS)

| order | signal | what is adjusted to what | page |
|---|---|---|---|
| 1 | SP pulse (11A2K24F, logic 11.12.02.1) | reference | 273 |
| 2 | SM memory-select timing pulse (11A2H21F, logic 11.12.02.1) | 200 ns wide, 150 ns after leading edge of an SP pulse | 273 B.2 |
| 3 | MEM SEL pulse | "Adjust MEM SEL pulse delay so changing memory address bus (MAB) information will be properly sampled into memory address register (MAR) of CSU A0 (logics 01.02.00.1 through 01.02.04.1). The delay line for this adjustment is on card 11A3J27 (logic 13.06.01.1)." | 274 B.3 |
| 4 | MEM RD out pulse [printed with an overbar on "MEM RD" at its second occurrence: "so M̅E̅M̅ ̅R̅D̅ out pulse will arrive"] | "Adjust MEM RD out pulse delay line (contained on card 11B1E21, logic 14.01.01.1) so MEM RD out pulse will arrive at readout trigger of CSU A0 (measured at pin 3 of card socket 01C1C13, logic 01.02.04.1) at same time that MAB information arrives at MAR (logics 01.02.00.1 through 01.02.04.1)." | 274 B.4 |
| 5 | Busy trigger | on for 1800 nanosec (reset delay line 01B1B22, in the selected CSU) | 274 B.5 |
| 6 | (repeat for other CSUs) | "Change address portion of Store Index (SX) instruction in 7101 CE console PANEL KEYS to specify next sequential CSU. Repeat steps 1 through 5 to adjust delay lines associated with MEM SEL pulse, MEM RD out pulse, and Busy trigger reset pulse for CSU's A1, B0, B1, B2, and B3. The location of the MEM SEL delay line card for each of these CSU's is shown in table 4.1.1." | 274 B.6 |
| 7 | data-in-gate pulse | "After above operations, adjust data-in-gate pulse delay lines (contained on CSU cards 01B1B18 and 01B1B16, logic 01.12.02.1) to sample selected index register data into memory data register (MDR) of each CSU (logics 01.18.04.1 through 01.18.07.1)." | 274 B.7 |

Note on B.4: the MEM RD out pulse is adjusted in the **store** section, i.e. a store also drives
the CSU "readout trigger" (consistent with a destructive-read clear-then-write cycle, but the
page does not say so).

**TABLE 4.1.1. MEMORY SELECT PULSE DELAY LINE CARD LOCATIONS** (PDF 274). CSU A0's is 11A3J27, logic 13.06.01.1 (from step B.3).

| Core Storage Unit | Delay Line Card Location | Logic Page |
|---|---|---|
| A1 | 11A3J24 | 13.06.02.1 |
| B0 | 11A3J26 | 13.06.01.1 |
| B1 | 11A3J25 | 13.06.01.1 |
| B2 | 11A3J23 | 13.06.02.1 |
| B3 | 11A3J22 | 13.06.02.1 |

**The CSU names are A0, A1, B0, B1, B2, B3 -- six units, a two-unit group "A" and a four-unit
group "B".** (Compare Buchholz's 4-way + 2-way interleave; the page does not say which group
is which address block.)

### Fetch path (PDF 275-278, "C. Timing of Fetch Operations"; test instruction: Load Index (LX) to CSU A0 in both half-words)

| order | signal | target | page |
|---|---|---|---|
| 1 | RA DCR STROBE pulse | "Adjust RA DCR STROBE pulse (measured at pin E of card socket 12B1J21, logic 17.05.02.1) so it samples RA parity bit (measured at pin E of card socket 12B1J22, logic 17.05.02.1). The delay line for this adjustment is on card 12B1K19 (logic 17.04.06.1)." | 275 C.2 |
| 2 | data-out-gate pulse | 290 ns wide; not earlier than 1050 ns after select-memory pulse | 275 C.3 |
| 3 | read/write trigger | "Simultaneously, check read/write trigger (measured at card socket pin 01D2J06B, logic 01.08.00.1) to ensure that it is changing state between X- or Y read/write timing pulses (measured at card socket pins 01D2K09B and 01D2K04G, logic 01.12.02.1). The delay line for adjusting the setting of this trigger is also on card 01B1C19 (logic 01.12.00.1)." | 275 C.3 |
| 4 | IMOB data at 1Y and at LA level 4 | brackets 6th SP pulse (A.4) | 275 |
| 5 | SEL 1Y pulse | brackets 5th and 6th SP pulses | 276 C.4 |
| 6 | SELECT 2Y pulse | brackets 5th and 6th SP pulses | 276 C.5 |
| 7 | MEM SEL LA 1-4 | each brackets 5th SP pulse (test: "a Load instruction (from CSU A0)") | 276 C.6-7 |
| 8 | data-in-gate into 1Y / LA 4 | check sampling of IMOB data | 277 C.8 |
| 9 | other CSUs | IMOB data "identical in width and relative position for all CSU's" | 277 C.9 |
| 10 | PANEL KEYS | made to coincide with CSU data, sync on RA-decoder-strobe | 277 C.10 |
| 11-12 | exchange fetch: SET BX-BFR pulse | samples BX MOB into BX buffer register | 277-278 C.11-12 |
| 13-14 | disk-synchronizer fetch: SEL HX pulse | samples HX MOB into word register | 278 C.13-14 |

"RA" is not expanded on these pages [uncertain: "return address"? -- consistent with Blosk's
3-bit return address and with "RA-decoder-strobe" selecting the destination register, but the
expansion is NOT printed here].

## A.4 The sentences that fix read-data time (verbatim)

PDF 275 (1-4), unnumbered paragraph after step C.3:

> "The IMOB data pulses measured at the 1Y register (logic 22.11.01.1) through 22.11.37.1) and
> at lookahead level 4 (logic 31.01.01.1 through 31.02.10.1) should bracket (overlap) the sixth
> SP pulse (measured at card socket pin 11A3B20F, logic 12.10.04.1) that is generated after the
> SP pulse which initiated the gate I pulse (measured at card socket pin 11A3B20G; refer to
> step 3). If above condition does not exist, adjust data-out-gate pulse timing by varying delay
> line on card 01A1F26 (logic 01.13.00.1). Adjust accurately even though pulse may have to be
> realigned after select pulses have been adjusted. (See fig. 4.1.1.)"

(The stray ")" after "22.11.01.1" is as printed. "gate I": printed as capital I; could be
"gate I" (roman one) or "gate 1" [uncertain]. The figures label it "GATE I".)

PDF 276 (1-5) step C.4:

> "Check timing of SEL 1Y pulse (measured at card socket pin 17A2C25U, logic 28.72.41.1) to
> ensure that pulse brackets (overlaps) fifth and sixth SP pulses (measured at card socket pin
> 17A2C25-3) that occur after SP pulse which initiated gate I pulse (measured at card socket
> pin 11A3B20G; refer to step 3). If above condition does not exist, adjust SEL 1Y pulse timing
> by varying delay line on card 12B1K15 (logic 17.06.01.1). (See fig. 4.1.2.)"

PDF 276 step C.5:

> "Check timing of SELECT 2Y pulse (measured at card socket pin 17A2C21U, logic 28.72.51.1) to
> ensure that pulse brackets (overlaps) fifth and sixth SP pulses (measured at card socket pin
> 17A2C21-3) that occur after SP pulse which initiated gate I pulse (measured at card socket
> pin 11A3B20G; refer to step 3). If above condition does not exist, adjust SEL 2Y pulse timing
> by varying delay line on card 12B1K16, logic 17.06.01.1. (See fig. 4.1.3.)"

PDF 276 step C.6-C.7:

> "Set CPU to test timing of the four MEM SEL LA pulses at 7101 CE console: a. Set a Load
> instruction (from CSU A0) into both half-words of PANEL KEYS. ..."

> "Check and adjust timing of the four MEM SEL LA level pulses by using signal measuring points
> and delay line location information listed in table 4.1.2. When checking one of these pulses,
> bypass other lookahead levels by means of LA disable switches on 7101 CE console. Adjust each
> MEM SEL LA pulse so it brackets (overlaps) fifth SP pulse that occurs after SP pulse which
> initiated gate I pulse (measured at card socket pin 11A3C13G; refer to step 3). (See fig.
> 4.1.4.)"

(Note the gate-I measuring pin is 11A3B20G in C.3-C.5 and **11A3C13G** in C.7, as printed.)

PDF 277 (1-6) steps C.8-C.9:

> "Use Load Index instruction test routine (refer to step 1) to check time at which data-in-gate
> pulse samples IMOB data into 1Y register. Next, use Load instruction test routine (refer to
> step 5 ) to check time at which data-in-gate pulse samples IMOB data into lookahead level 4
> (LA 4). If IMOB data is not being correctly sampled into 1Y register and/or LA level 4, refer
> to step 3 and vary timing of data-out-gate pulse so that both transfers are made correctly."

> "Repeat step 3 for each of the other CSU's to ensure that IMOB data at 1Y and LA 4 registers
> is identical in width and relative position for all CSU's. Also, repeat step 7 for each of the
> other CSU's to ensure that IMOB data will be correctly transferred into 1Y and LA 4 registers
> from all CSU's."

("refer to step 5" is as printed; the Load routine is actually step 6.)

**TABLE 4.1.2. MEMORY SELECT LA LEVEL PULSE DELAY LINE LOCATIONS** (PDF 277)

| Test Pulse | LA Pulse (measuring pt) | SP Pulse (measuring pt) | Logic Page | Delay Line Location | Delay Line Logic Page |
|---|---|---|---|---|---|
| MEM SEL LA 1 | 18A3A21B | 18A3A21C | 36.01.05.1 | 12B1K18 | 17.06.01.1 |
| MEM SEL LA 2 | 18A3A21-6 | 18A3A21-5 | 36.01.06.1 | 12B1K10 | 17.06.02.1 |
| MEM SEL LA 3 | 18A3C21B | 18A3C21C | 36.01.07.1 | 12B1K12 | 17.06.02.1 |
| MEM SEL LA 4 | 18A3C21-6 | 18A3C21-5 | 36.01.08.1 | 12B1K13 | 17.06.02.1 |

Other destinations (PDF 277-278):
- PANEL KEYS: "Using RA-decoder-strobe pulse (measured at card socket pin 12B1J25F, logic
  17.05.01.1) as a sync point, check time relationship between a pulse on a data line from CSU
  A0 and a pulse on a data line from PANEL KEYS. If these two pulses do not coincide, adjust
  PANEL KEYS delay line on card 11A2H16 (logic 18.05.01.1) so that the two data pulses coincide."
- Exchange: "Adjust SET BX-BFR pulse by varying delay line on card 12B1J13 (logic 17.06.03.1)
  so BUS SET BR pulse samples data on BX MOB to BX buffer register."
- Disk synchronizer: "Adjust SEL HX pulse by varying delay line on card 12B1J12 (logic
  17.06.03.1) so HX MOB-to-WDR pulse samples data on HX MOB into word register."

So the bus control (logic 17.06.xx delay lines) generates one **select pulse per destination**:
SEL 1Y, SEL 2Y, MEM SEL LA 1..4, SET BX-BFR, SEL HX -- eight, each with its own delay line.
[My observation, not a printed statement: that count of eight matches Buchholz's "eight
different channels".] There are three memory-out buses named: IMOB (to 1Y / LA levels),
BX MOB (exchange), HX MOB (disk synchronizer).

## A.5 Figures 4.1.1-4.1.4 (PDF 279, printed 1-8) -- waveform steps

All four are undimensioned sketches: no ns scale, no axis. Each shows `SP PULSES` as seven
positive pulses numbered 0-6 (about 50% duty as drawn), `GATE I`, and `IMOB DATA` drawn as a
NEGATIVE-going pulse. Positions below are my pixel measurements on a 300-dpi render, expressed
in SP periods from the leading edge of SP pulse 0 (measurement error about +-0.1 period).
**They are drawing geometry, not printed values; use only the "brackets Nth pulse" statements
as source facts.**

| figure | signal | rises/starts (SP periods after pulse-0 leading edge) | ends | dashed reference lines |
|---|---|---|---|---|
| 4.1.1 DATA-OUT GATE TIMING | GATE I | 0.0 (coincident with leading edge of SP 0, dashed line drawn) | ~1.0 (leading edge of SP 1) | -- |
| | IMOB DATA (low) | ~5.6 | ~6.7 | two dashed lines at the leading and trailing edges of SP pulse 6, both inside the IMOB low interval |
| 4.1.2 SELECT 1Y PULSE TIMING | GATE I | 0.0 | ~1.0 | |
| | SELECT 1Y (high) | ~4.6 | ~6.6 | dashed at leading edge of SP 5 and trailing edge of SP 6, both inside SELECT 1Y |
| | IMOB DATA (low) | ~5.7 | ~6.7 | |
| 4.1.3 SELECT 2Y PULSE TIMING | GATE I | 0.0 | ~1.0 | |
| | SELECT 2Y (high) | ~4.6 | ~6.6 | dashed at leading edge of SP 5 and trailing edge of SP 6 |
| | IMOB DATA (low) | ~5.5 | ~6.6 | |
| 4.1.4 MEM SEL LA PULSE TIMING | GATE I | 0.0 | ~1.0 | |
| | MEM SEL LA (high) | ~4.7 | ~5.7 | dashed at leading and trailing edges of SP 5, both inside MEM SEL LA |
| | IMOB DATA (low) | ~5.6 | ~6.6 | |

Observations on the drawings (mine):
- GATE I is drawn one full SP period wide (leading edge of pulse 0 to leading edge of pulse 1).
- **In Fig 4.1.4 MEM SEL LA is drawn ENDING at about the moment IMOB DATA begins** (MEM SEL LA
  ~4.7-5.7, IMOB ~5.6-6.6), whereas SELECT 1Y/2Y are drawn spanning the IMOB pulse. Yet the
  text (PDF 275) says IMOB data at LA level 4 brackets the SIXTH pulse, the same as at 1Y. So
  "MEM SEL LA at the 5th pulse" is NOT evidence that a look-ahead level receives its data one
  pulse earlier than 1Y; as drawn, MEM SEL LA precedes the data. What MEM SEL LA does (select
  the level / set a trigger vs. gate data) is not stated on these pages; Fig 3.2.2 (PDF 93)
  shows "MEM SEL LA 1" on the arrow into "SET LF E TRIGGER" under "DATA ON IMOB".
- What "gate I" is, and its relation to the requester's bus request, is not stated here.

## A.6 What Procedure 1 does NOT contain (negative findings, so nobody re-mines it for them)

- no 2.1 usec (or any) read-write cycle figure; no 1.6 usec read-out figure;
- no description of request/accept/return, priority among requesters, or how a busy CSU delays
  a requester; no mention of interleaving;
- no SP period; no A/B phase;
- no regeneration (write-back) timing other than "read/write trigger ... changing state
  between X- or Y read/write timing pulses";
- no difference between CSUs (every CSU is adjusted to the same targets).

The LA flow diagrams add three bus-related facts (see Part B): "INFORM BCU OF NEW IAUC LEVEL"
(Fig 3.2.1), "FETCH ACCEPTED AND NO COMPARE" / "MEM FETCH CNCLD" (Fig 3.2.1), "DATA ON IMOB"
+ "MEM SEL LA 1" setting the LF E trigger (Fig 3.2.2).

---

# PART B -- Look-ahead flow diagrams (PDF 92-119, section M3-04-3 "LA FLOW DIAGRAMS")

**There is no prose on any of these pages.** Every "quote" below is the text of a box, a
decision hexagon, or an arrow label. The diagrams are logic-condition flows (boxes =
actions/lines raised, hexagons = conditions, small numbers = ALD logic pages), not
cycle-by-cycle charts. A wide box "START xxx TIMER" has its outputs labelled with the timer
trigger condition under which each action happens (`E`, `M`, `E.M̅` (E and not M), `E+M`,
`EM`, `EE`...). Overbars are written here as `M̅` or "not-M".

Abbreviations as they appear (expansions are from Buchholz ch.15 / spec_lookahead.md unless
marked): IAUC = instruction-unit (address) counter; OCC = operand check counter; TBC = transfer
bus counter; ABC = arithmetic bus counter; SCC = store check counter; AES = [advance enable
sequence? -- printed once as "SET IAUC ADV EN SEQ" on Fig 3.2.1]; LDE = [uncertain: "level
decode enable"? not expanded on the pages]; LF / LC = level filled / level checked tags;
LAOP = look-ahead op code (two octal digits); LLP = lookahead load pulse (types 1, 2, 3);
DISC = level disconnected (CE "LA disable" switches); HSCLN = houseclean; IJ = [an indicator,
"SET IJ IND"; uncertain reading, could be "IJ" or "U"]; CNIDC = [indicator name, printed "SET
CNIDC IND"]; ICIB/ICOB = I-checker in/out bus; TOB = transfer out bus?; STAR = store address
register? [not expanded]; IMOB = I(nstruction-unit/internal) memory out bus [not expanded].

Connections are given as "X --label--> Y". Where I could not follow a line with confidence I
say so. ALD page numbers are given as read at 150 dpi; digits `3/8`, `5/6`, `1/7` are the
likely confusions.

## Fig 3.2.1 "IAUC LOAD ENABLE AND ADVANCE CONDITIONS" -- PDF 92 (2-1/2-2, fold-out, 2/1/62)

Already read by an earlier agent (spec_lookahead.md); seen here only at the Read tool's low
resolution, so this is an INVENTORY of boxes, not a verified connection list.

Entry "ADVANCE IAUC" -> "STEP IAUC TO NEW LEVEL" (38.01.01.1), with side actions "SET IAUC
ADV EN SEQ" (38.01.06.1) -> "RESET LOAD PULSE MEMORY" (38.01.10.1); "INFORM BCU OF NEW IAUC
LEVEL" (38.61.01.1); "RESET LC, NOOP, IJ AT NEW LEVEL" (36.02.03.1, 33.01.16.1, 36.07.03.1).
Decisions then: "DISC IAUC" (YES -> "RESET IAUC AES" 38.01.01.1 -> "DROP LOAD ENABLE LINES");
NO -> "RECOVERY NEEDED" -NO-> "LOAD STARTED" -NO (AES ON)-> the load-enable group:
"BOTH LAARS BUSY" (NO -> "TYPE 1 & 2 LOAD ENABLE" 38.02.02.1; YES -> "STORE BEING DONE" -YES->
"TYPE 3 LOAD ENABLE" 38.02.03.1). Then "LOAD STARTED" (YES, labelled "(LLP 1/2)") -> "RESET
IAUC AES"; "MEM FETCH CNCLD" (YES -> "SET IAUC AES" 38.01.06.1 and back to the load-enable
group; NO -> ) "LLP1" (YES -> connector A) / "LLP2" (YES -> connector B) / "(LLP3)" "LLP3 MOD"
/ "LAOP 33 ECC CHK LOAD" (YES -> "I CHKR ECC ERR" loop-on-YES; NO -> connector C) ; "FETCH
ACCEPTED AND NO COMPARE" -YES-> "SET IAUC LOAD PULSE MEMORY" (38.01.10.1) -> "IAUC AES OFF"
-YES-> "NEXT LEVEL IN SCC" ... Connectors A/B/D -> "NEXT LEVEL IN SCC" -NO-> "ANY DISC" -NO->
"RECOVERY NEEDED" -NO-> "TYPE 1 & 2 LOAD ENABLE" (38.02.02.1) / "BOTH LAARS BUSY" (YES ->
"STORE BEING DONE" -YES-> "TYPE 3 LOAD ENABLE" 38.02.03.1; NO -> TYPE 3 LOAD ENABLE);
connector C -> "NEXT LEVEL IN SCC" -NO-> "ANY DISC" -NO-> "RECOVERY NEEDED" -NO-> "BOTH LAARS
NOT BUSY" -YES-> "TYPE 3 LOAD ENABLE". Lower left (advance): "SCC AT NEXT LEVEL" (YES -> "ABC
THERE" -YES-> "TBC THERE" -NO-> "STORE REQUIRED" -NO-> "ABC ADVANCING" -YES-> ) ... "IAUC AES
OFF" -YES (38.01.08.1)-> "ADVANCE IAUC". Also: "NEXT LEVEL IN ABC", "STORE REQ.", "STORE DONE"
(YES, "(STORE DATA M)"), "BOTH LAARS 1&2 BUSY", "STORE BEING DONE".
**Relevant to the model: the IAUC may not advance into the level the SCC (store check counter)
is at unless the store there is done; and load enable distinguishes "TYPE 1 & 2" from "TYPE
3" loads by whether both LAARs are busy.**

## Fig 3.2.2 "LOOKAHEAD LOAD PULSES" sheets 1-2 -- PDF 93 (2-3), PDF 94 (2-4)

Seen at low resolution only (ALD numbers not legible at that size); box inventory.

Sheet 1, bar "LLP 1" feeds in parallel: "GI TAG BITS & OP CODE FIELD EXCEPT BIT 8"; decision
"LAOP 45 ?" (NO -> "GI OP CODE BIT 8"; YES -> "I CHKR PARITY ERROR ?" -YES-> "SET OP BIT 8");
"GI I BOX IND'S TO IND. FIELD"; "GI IC TO IC FIELD"; "I CHKR PARITY ERROR ?" -YES-> "PSEUDO
STORE OR RECOVERY LEVEL ?" (YES -> "SET CNIDC IND"; NO -> "SET IJ IND" and "SET NOOP TAG");
"GI ICOB TO DATA FIELD"; "SET LF & LC TAGS".
Bar "LLP 2" feeds: "GI TAG BITS & OP CODE FIELD"; "GI I BOX IND'S TO IND FIELD"; "GI IC TO IC
FIELD"; decision "IS LAAR COMPARE ENABLED ?" (YES -> "ADDRESS COMPARE ?" -NO-> ; NO -> ) "DATA
ON IMOB" -YES ("MEM SEL LA 1")-> "SET LF E TRIGGER" -> "SET LF TAG" and "GI IMOB INTO DATA
FIELD"; also from DATA ON IMOB: "BOUNDARY ALARM ?" -YES-> "SET OP OF DS IND" [uncertain text]
and "SET NOOP TAG"; "MEM CHK ALARM ?" -YES-> "SET IJ IND" and "SET NOOP TAG" [faint].
**So an LLP 1 load takes its data from the I checker out bus (ICOB) and sets BOTH LF and LC
(filled and checked) at once; an LLP 2 load is a memory fetch whose data arrives later on the
IMOB and sets only LF (the OCC must then check it, Fig 3.2.3).**
Sheet 2, bar "LLP 3": "GI TAG BITS AND OP CODE"; "GI I-BOX IND'S TO IND FIELD"; "GI IC TO IC
FIELD"; "I BOX WILL LOAD LAAR 1 OR 2"; decision "LAAR 1 BUSY" (NO -> "MOD TYPE 3" [YES ->
"FETCH ACCEPTED" -YES-> ; NO ->] "SET FROM 1 & LAAR 1 BUSY" 36.16.02.1, 38.53.01.1; YES ->
"MOD TYPE 3" [YES -> "FETCH ACCEPTED" -YES->; NO ->] "SET FROM 2 & LAAR 2 BUSY" 36.16.02.1,
38.53.01.1); "LAOP 33 ECC CHK LOAD" (YES -> "GI ICOB WITH ECC", "ECC ERROR" [NO -> "SET LF &
LC TAGS"; YES -> "LAOP 33 ECC CORRECT LOAD" -> "GI ICOB WITH ECC", "UNCORR ECC ERR" -YES->
"SET NOOP TAG"]; NO -> "MODIFIED TYPE 3" -NO-> "SET LF & LC TAGS", "I BOX STORE" -YES-> "GI
ICOB WITH ECC" (38.03.07.1), "I-PAR ERROR" -YES-> "SET IJ & NOOP").
**"SET FROM 1 & LAAR 1 BUSY" / "SET FROM 2 & LAAR 2 BUSY": the level's FROM tag records WHICH
of the two LAARs holds its store address; the I box loads the LAAR ("I BOX WILL LOAD LAAR 1 OR
2").**

## Fig 3.2.3 "OPERAND CHECK AND CORRECT PHASE OF INSTRUCTION PREPARATION" -- PDF 95 (2-5, 2/1/62)

Read at 150 dpi; clear.

1. Entry "ADVANCE OCC" -> side box "SET OCC AES" (38.11.06.1); -> "STEP OCC TO NEXT LEVEL" (38.11.01.1).
2. Decision "DISC OCC": YES -> left rail (to step 9). NO -> 3.
3. Decision "OPD CHK REQ": NO "(LC ON)" -> left rail (step 9). YES "(LF NOT LC" -> 4.
4. Decision "CHK STARTED": NO "(OCC AES ON)" -> 5. [YES exit not drawn with a label.]
5. Box "3RD PRIORITY CHKR REQUEST" (38.12.01.1) -> 6.
6. Decision "CHKR IN USE": YES -> loops back up to box 5. NO "(NO "0" REQ)" -> box "DROP "OK TO I CHK" LINE" (35.01.02.1) -> box "PREVENT I BOX CHKER CYCLES"; and NO also -> 7.
7. Decision "IS CHKR NEED BY LAST USER FOR CORR CYC": YES -> back to loop (box 5). NO "(NO SINGLE ECC ERR)" -> 8.
8. Wide box "START OPERAND CHECK TIMER" (35.05.01.1), four outputs:
   - `E` -> "GO DATA FIELD TO ICIB" (35.10.02.1)
   - `E.M̅` [printed "EM" with a bar over the M] -> "RESET OCC AES"; -> "DROP "NO 0 REQ" LINE TO HOLD I CHKR PRIORITY"; -> decision "PANEL KEYS OR INVALID ADDRESS": NO -> "SIGNAL I CHKR TO CHK ECC" (35.15.01.1); YES "(OCC INT FETCH TAG)" -> "SIGNAL I CHKR TO GENERATE PARITY" (35.15.01.1)
   - `M` -> "GI ICOB DATA PARITY RESIDUE" (35.10.01.1); -> decision "ECC ERROR" -> [exit label not printed; by layout the non-error exit] "SET LC TAG" (35.15.01.1)
   - `EM` -> decision "ECC ERROR": NO -> down to the common rail (step 9). YES -> wide box "START OPERAND CORRECT TIMER" (35.05.02.1), outputs:
       - `E` -> "CONTINUE GATING DATA TO ICIB" (35.10.02.1)
       - `EM` [bar not legible; uncertain whether E.M or E.M̅] -> "DROP "NO 0 REQ" LINE TO HOLD CHKR PRIOR"
       - `EM` -> "GI ICOB AGAIN"; -> "SET LC TAG"; -> decision "DBL ERR" -YES-> "SET IJ IND NOOP TAG" (33.01.16.1, 36.07.07.1)
       - a further line from the timer box returns to the common rail.
9. Common rail -> decision "IS IAUC IN THIS LEVEL": NO -> "ADVANCE OCC". [YES: no exit drawn = wait.]

**What it says for timing: an operand that arrived from memory (LF on, LC off) costs one
OPERAND CHECK TIMER pass (E then M triggers) through the I checker, plus one OPERAND CORRECT
TIMER pass if a single ECC error is found; the OCC waits for the checker if it is in use ("3RD
PRIORITY"), and the OCC cannot advance past the level the IAUC is in.** No time value printed.

## Fig 3.2.4 "BASIC TBC ADVANCE CONDITIONS" -- PDF 96 (2-6, 2/1/62)

(Previously read by the earlier agent; re-read here at Read-tool resolution, clear.)
"ADV" -> side "SET TBC AES"; -> "TBC AT NEW LEVEL" -> decision "DISC / HSC IN MODE / NOOP MODE
?": YES -> down the left rail -> "TBC SINGLE ADV. COND" -> "ADVANCE TBC IF NOT INTLKD BY OCC".
NO -> "EXECUTE IF REQUIRED" -> (a) "SPECIAL CASES" -> left rail; (b) "TBC MULTIPLE ADV. COND"
-> decision "TBC AES OFF ?" -YES-> "ADVANCE TBC IF NOT INTLKD BY OCC"; (c) decision chain "TBC
EXECUTED ?" (YES -> "RESET TBC AES"; NO ->) "ABC TRANS INDS ONLY ?" (YES -> "RESET TBC AES";
NO ->) "ABC INT FETCH ?" (YES -> "RESET TBC AES"; NO ->) "ABC STORE ACTION ?" (YES -> "RESET
TBC AES").

## Fig 3.2.5 "TBC SINGLE ADVANCE CONDITION" -- PDF 97 (2-7, 2/1/62)

Read at 150 dpi; text clear, some line routing dense. No ALD numbers on this figure.

1. "ADVANCE TBC" -> side boxes "RESET TBC LDE" and "SET TBC AES"; -> "STEP TBC TO NEXT LEVEL".
2. Decision "DISC": YES -> left rail (the advance rail, which ends at step 12). NO -> two parallel branches, 3 and 2a.
   2a. Decision "LF & LC ON" -YES-> box "SET TBC LDE".
3. Decision "HSCLN MODE": YES -> left rail. NO -> 4.
4. Decision "NOOP MODE": YES -> 5. NO -> decision "INST DECODED" -YES "LDE ON"-> 6.
5. (NOOP MODE = YES) Decision "LAST LEVEL": NO "IC OFF" -> left rail. YES -> decision "EXT STORE": NO -> decision "ABC ACTION COMPLETE OK" -YES "AND CKT 3C"-> left rail. YES -> decision "ALL PREVIOUS STORES" -YES, labelled "STAR BUSY AND NO STORE REQ", "AND CKT 3A" -> left rail.
6. (LDE ON) Decision "LAOP 45 OR 47": NO -> long line down and round to step 7's entry. YES -> decision "BRANCH RECOVERY IN PROG" -NO-> decision "LAOP 47": YES -> left rail. NO -> decision "SIC BRANCH": YES "(NO IC)" -> [joins the LAOP 47 YES line] left rail. NO -> decision "BR CONDITION MET": NO -> left rail. YES -> oval "ABC WILL CAUSE HSCLN MODE".
7. Decision chain, each YES -> left rail, each other exit -> next:
   "LAOP 17 EXT STO" -> "LAOP 23 EXT STO" -> "NOOP 13 NOT INT STO" [printed "NOOP 13"; possibly meant "LAOP 13" -- as printed] -> "LAOP 21" (YES labelled "ALWAYS EXT STO") -> "LAOP 04" -> "LAOP 33 INT" (YES -> decision "ABC ACTION TAKEN" -YES "A TIMER M"-> left rail) -> "LAOP 11 OR 63" (YES -> decision "BAC REC REQ" [as printed; uncertain whether "BAC" or "BRC"] -NO-> decision "ABC ACTION TAKEN" -YES "TFR IND E+M"-> left rail).
12. Left rail -> decision "TBC OCC INT CK" -NO-> "ADVANCE TBC".

**Reading: for these LAOP codes the TBC takes no transfer-bus action of its own and advances
as soon as the listed condition holds; a branch level (LAOP 45/47) whose condition is met does
NOT advance the TBC -- "ABC WILL CAUSE HSCLN MODE".** The TBC is interlocked behind the OCC
("TBC OCC INT CK").

## Fig 3.2.6 "TBC MULTIPLE ADVANCE CONDITION" -- PDF 98 (2-8, 2/1/62)

Read at 150 dpi; left-margin text partly cropped by the binding, bottom-left boxes faint.

1. "ADVANCE TBC" -> "RESET TBC LDE", "SET TBC AES"; -> "STEP TBC TO NEXT LEVEL".
2. Decision "LDE ON" -YES-> two branches: (i) the LAOP chain, step 3; (ii) far right down to decision "TBC ABC INTLK" (step 5).
3. LAOP chain (each "NOT INT" [= operand not internal?] exit goes on to the next decision):
   - "LAOP 20 OR 24" -YES-> box "T BUS TIMER" -> "RESET TBC AES"; a line labelled "I O RESPONSE" [left edge cropped: "I O / RESPONSE"] from the timer box -> left rail.
   - "LAOP 03, 07'15" [as printed; reads "03, 07 15", punctuation uncertain] -YES-> "T BUS TIMER" -`M`-> left rail; -> "RESET TBC AES".
   - "LAOP 05" -YES-> "T BUS TIMER" -`M`-> left rail; -> "RESET TBC AES".
   - "LAOP X1, 35, 75, 43" -YES-> "T BUS TIMER" -> outputs labelled "FP 1ST CYC" and "VFL 1ST CYC" -> left rail (the "FP 1ST CYC" line carries the note "IF NOT INT STO") and -> box "SET FST CYC MEM" -> "IF NOT INT STO" -> left rail; -> "RESET TBC AES".
   - "LAOP X2 NOT INT" -YES-> joins the same "T BUS TIMER" as X1/35/75/43.
   - "LAOP 55, 27" -YES-> a further box "T BUS TIMER" -> "RESET TBC AES"; and -> decision "BR SUCCESSOR BR UNSUCC" -YES-> left rail.
5. Decision "TBC ABC INTLK" -YES-> oval "ABC WILL RESET AES", and -> decision "INT FETCH": YES -> decision "LOOP 51" [as printed: "LOOP 51"; probably "LAOP 51" -- flagged] -NO-> left rail. NO -> decision "LAOP 41,23,17" -YES-> left rail; else -> decision "LAOP 00,40,02, 42,25,65," -YES-> left rail; else -> decision "LAOP 31,57,33, EXT" -YES-> left rail.
6. Left rail -> decision "TBC AES OFF" -YES-> decision "TBC OCC INTLK" -NO-> "ADVANCE TBC" [bottom text faint].

## Fig 3.2.7 "TBC I/O INSTRUCTIONS - OP 20 AND OP 24" -- PDF 99 (2-9, 2/1/62)

Read at 150 dpi; clear.

1. "ADVANCE" -> side "SET TBC AES" (38.21.03.1); -> "TBC AT NEW LEVEL".
2. Decision "IS LEVEL READY FOR TBC ACTION ?" -YES "TBC LDE ON"-> 3.
3. Decision "NOOP'D OR NOOP MODE ?" -NO-> 4 (ALD 38.22.03.1 printed at this arrow).
4. Decision "IO INSTR ?" -YES "OP X00"-> 5.
5. Decision "ABC-SCC INTLKD ?" -YES-> (a) decision "TBC-ABC INTLKD ?" -YES-> 6; (b) box "GO OP CODE BITS 1-4 LEVELS TO IO DECODER" (35.28.01.1) -> box "SIGNAL BX & DISC SYNC TO READ WRITE CONTROL LOCATE RELEASE OR CCW (AND) SEOP" (38.68.01.1).
6. Decision "PREVIOUS INSTR. PROPERLY EXECUTED ?" -YES "MAR MODE"-> 7.
7. Decision "TBC ACTION TAKEN YET ?" -NO "TBC AES ON"-> 8.
8. Wide box "START TRANSFER BUS TIMER" (38.25.01.1), outputs:
   - `E.M` [printed "E. M"; a bar over M is not visible here, cf. "E.M̅" on Figs 3.2.8/3.2.9 -- uncertain] -> "RESET TBC AES" (38.21.03.1)
   - `M` -> decision "BX OR DISC SYNC INSTR. ?": "BX / OP 20" -> "SELECT BX" (38.68.02.1); "DISC / OP 24" -> "SELECT DISC SYNC"
   - `E or M` -> "GO DATA FIELD LEVELS ON TO B" [as printed "ON TO B"; probably "ON TOB"] (35.16.01.1)
9. After select -> decision "HAS BX OR DISC ACCEPTED THE INSTR ?": YES -> (38.25.03.1) box "SET IO REACTION STORAGE TRIGGER". NO -> decision "REJECTED ?" -YES (38.25.02.1)-> same box.
10. "SET IO REACTION STORAGE TRIGGER" -> "RESET TB TIMER M" (38.25.02.1) -> "DROP SELECT SIGNAL" (38.68.02.1) -> "DROP ACCEPT OR REJECT SIGNAL"; and -> "SET IO BUFFER TRIGGER" (which, with a line labelled "RESET", feeds back to "SET IO REACTION STORAGE TRIGGER") -> "SET IO RESPONSE TRIGGER" -> "ADV. TBC IF NOT INTLKD BY OCC" -> "SET TBC AES" and "RESET TBC LDE" (38.22.15.1); "SET TBC AES" -> "RESET IO RESPONSE TRIGGER".

**The TB TIMER M trigger stays on until the exchange/disk accepts or rejects: the transfer-bus
timer is not a fixed duration here, it is held by a handshake.**

## Fig 3.2.8 "FIRST LEVEL OF SAU INSTRUCTIONS" -- PDF 100 (2-10, 2/1/62)

Read at 150 dpi; clear. Legend box "OP DECODE": "OP X1 38.22.07.1 / LAOP 35 OR 75 38.22.10.1 / LAOP 75 38.22.09.1 / LAOP 43 38.22.09.1".

1. "ADVANCE" -> "SET TBC AES" (38.21.03.1); -> "TBC AT NEW LEVEL".
2. Decision "IS LEVEL READY FOR TBC ACTION ?" -YES "TBC LDE ON"-> 3.
3. Decision "NOOP'D OR NOOP MODE ?" -NO-> 4.
4. Decision "35, 75 43, X1 ?" -YES-> two branches:
   a. Decision "LAOP ?" -YES-> decision "BB OR BI ?": "BB" -> box "SIGNAL SAU OF BB INSTR."; "BI" -> decision "INTRPT BI ?" -> [exits unlabelled] "SIGNAL SAU OF INTRPT BI INSTR" (38.23.05.1) / "SIGNAL SAU OF BI INSTR." (36.11.02.1).
   b. Decision "TBC ACTION TAKEN YET?" -NO "TBC AES ON"-> 5.
5. Wide box "START TRANSFER BUS TIMER" (38.25.01.1), outputs:
   - `E.M̅` -> "RESET TBC AES" (38.21.03.1); -> "SET VFL START TRIGGER" (38.23.05.1) -> "ENABLE SAU TO START PRE-EXECUTION" -> decision "HAS SAU ACCEPTED THE DATA ?" -YES ""SAU HSKPING""-> "RESET VFL START TRIGGER" (38.23.05.1); and -> "SET FIRST CYCLE MEM. TRIGGER" (38.24.01.1) -> "ADV TBC IF NOT INTLKD BY OCC" -> "SET TBC AES", "RESET TB TIMER M", "RESET TBC LDE" (38.22.15.1); "SET TBC AES" -> "RESET "FIRST CYCLE MEM" TRIG" (38.24.01.1).
   - `E + M` -> "GO DATA FIELD ON TOB"; -> "GO OP CODE & WBC TO SAU".

## Fig 3.2.9 "VFL OPERANDS LAOP 03, 05, AND 07" -- PDF 101 (2-11, 2/1/62)

Read at 150 dpi; clear. Legend "OP DECODE": "LAOP 05 38.22.07.1 / LAOP 03 38.22.11.1 / LAOP 07 38.22.11.1".

1. "ADVANCE" -> "SET TBC AES" (38.21.03.1); -> "TBC AT NEW LEVEL".
2. "IS LEVEL READY FOR TBC ACTION ?" -YES "TBC LDE ON"-> "NOOP'D OR NOOP MODE ?" -NO-> 3.
3. Decision "IS OPERAND IN LA DATA FIELD ?" -YES "INT TAG OFF"-> 4.
4. Decision "FIRST OR ONLY OPERAND": NO "07" -> directly to 6. YES "03 05" -> decision "TBC-ABC INTLKD ?" -YES-> decision "PREVIOUS INSTR. PROPERLY EXECUTED ?" -YES "MAR MODE"-> 6.
6. Decision "TBC ACTION TAKEN YET?" -NO "TBC AES ON"-> 7.
7. Wide box "START TRANSFER BUS TIMER" (38.25.01.1), outputs:
   - `E.M̅` -> "RESET TBC AES" (38.21.03.1); -> decision "FIRST OR ONLY OPERAND ?": YES "03 05" -> "GI TOB TO C REG" (35.17.01.1); NO -> "GI TOB TO D REG"; -> decision "LAST, OR ONLY OPERAND ?" -YES "05 07"-> "SET SAU GO TRIGGER" (38.23.04.1) -> "SIGNAL SAU TO STOP HSKPING & START EXECUTION" -> decision "HAS SAU STARTED EXECUTION ?" -YES ""SAU HSKPING" OVER"-> "RESET SAU GO TRIGGER" (38.23.04.1).
   - `M` -> "ADV TBC IF NOT INTLKD BY OCC" -> "RESET TBC LDE", "SET TBC AES", "RESET TB TIMER M".
   - `E + M` -> "GO DATA ON TOB".

**So LAOP 03 = first VFL operand word (to C register), 07 = second/last (to D register), 05 =
only operand (to C, and starts execution). A VFL operand crossing a word boundary is two
levels, each one transfer-bus-timer pass.**

## Fig 3.2.10 "VFL SPECIAL OPERAND LAOP 15" -- PDF 102 (2-12, 2/1/62)

Read at 150 dpi; clear.

1. "ADVANCE" -> "SET TBC AES" (38.21.03.1); -> "TBC AT NEW LEVEL".
2. "IS LEVEL READY FOR TBC ACTION ?" -YES "TBC LDE ON"-> "NOOP'D OR NOOP MODE ?" -NO-> decision "LAOP 15" (38.22.11.1) -YES-> 3.
3. Decision "IS OPERAND IN LA DATA FIELD ?" -> exit labelled "ALWAYS / INT TAG OFF" -> 4.
4. Decision "IS C REG EMPTY ?" -YES "VFL RDY FOR MCND"-> box "SET VFL WAIT FOR MULTIPLICAND TRIG." (38.24.03.1) -> (a) box "SEND A SIGNAL TO SAU TO BLOCK ITS MPYC ACTION" (38.23.05.1); (b) decision "TBC ACTION TAKEN YET ?" -NO "TBC AES ON"-> 5.
5. Wide box "START TRANSFER BUS TIMER" (38.25.01.1), outputs:
   - `E.M̅` -> "RESET TBC AES" (38.21.03.1); "GI TOB TO C REG" (35.17.01.1); "GI RESIDUE FROM TOB TO A CHKR" (38.23.03.1); "RESET "VFL WAIT FOR MCND" TRIGGER" (38.24.03.1) -> "REMOVE SAU MPYC BLOCK".
   - `E+M` -> "GO DATA ON TOB" (35.16.01.1).
   - `M` -> "ADV. TBC IF NOT INTLKD BY OCC" -> "RESET TBC LDE", "SET TBC AES", "RESET TB TIMER M".

## Fig 3.2.11 "FP INSTRUCTION LEVEL OPX2" -- PDF 103 (2-13, 2/1/62)

Read at 150 dpi; clear.

1. "ADVANCE" -> "SET TBC AES"; -> "TBC AT NEW LEVEL".
2. Decision "INST PREPARATION COMP" -YES "LF & LC ON"-> decision "DISC OR NOOPED" -NO-> decision "HSCLN OR NOOP MODE" -NO-> decision "OP X2" -YES-> two branches:
   a. Decision "LATE DECODE ENABLE ON" -YES-> box "GO OP CODE ON TOB" (35.28.01.1).
   b. Decision "IS OPERAND IN INT REG" -NO "INT TAG OFF"-> decision "TBC ACTION TAKEN" -NO "TBC AES ON"-> 3.
3. Wide box "STAPT T BUS TIMER" [sic, "STAPT"] (38.25.01.1), outputs:
   - `E.M̅` [printed "EM" with bar over M] -> "RESET TBC AES" (38.21.03.1); "GI TOB TO C REG" (38.23.01.1); "SIGNAL PAU & SAU TO START" (38.23.01.1) -> decision "HAS PAU STARTED YET" -"YES TO" [label as printed]-> box "SET 1ST CYC MEM TGR" (38.24.01.1) and on to 4.
   - `E + M` -> "GO DATA FIELD ON TOB" (35.16.01.1).
4. Decision "INT STORE" -NO-> (38.21.04.1) box "ADVANCE IF NOT INTERLOCKED BY OCC" -> "ADVANCE"; side box "RESET TBC ADE [as printed; elsewhere 'LDE'] / 1ST CYC MEM / T BUS M".

**For a floating-point (OP X2) level: the TBC needs LF & LC on, then ONE transfer-bus-timer
pass gates the operand to the C register and signals PAU & SAU to start; TBC advance waits on
"HAS PAU STARTED YET".**

## Fig 3.2.12 "TBC STORE GATE CONTROL" -- PDF 104 (2-14, 2/1/62). "LOGIC: 38.22.16.1"

(Previously read by the earlier agent; re-read at 150 dpi, clear.)

1. "TBC ADV" -> "STEP TBC TO NEXT LEVEL" -> decision "TBC AES ON" -YES-> decision "TBC LDE ON" -YES-> decision "EXT STORE" -YES "EXT STO & NOT INT STO TAGS"-> 2.
2. Decision "FROM 1": YES -> box "SET GT LAAR 1 NEXT" (caption below: "IN BCU"); and -> decision "LAOP 33 EXT OR 31" [YES -> "SET STO NEXT 1 TGR" -> oval "LOAD STORE REG FROM TOB NEXT" (caption "FOR LAAR 1"); NO -> "RESET STO NEXT 1 TGR" -> oval "LOAD STORE REG FROM ACOB NEXT" ("FOR LAAR 1")].
   NO -> decision "FROM 2" -YES-> box "SET GT LAAR 2 NEXT" ("IN BCU"); and -> decision "LAOP 33 EXT OR 31" [YES -> "SET STO NEXT 2 TGR" -> oval "LOAD STORE REG FROM TOB NEXT" ("FOR LAAR 2"); NO -> "RESET STO NEXT 2 TGR" -> oval "LOAD STORE REG FROM ACOB NEXT" ("FOR LAAR 2")].

**A store level names its LAAR by its FROM tag (FROM 1 / FROM 2). The store DATA comes from the
TOB (transfer out bus, i.e. the level's own data field) for LAOP 33 EXT or 31 -- I-box stores --
and from the ACOB (arithmetic/A-checker out bus) otherwise -- E-box stores. "IN BCU": the LAAR
gate-next trigger lives in the bus control unit.**

## Fig 3.2.13 "I BOX STORE TO INTERNAL ADDRESS, LAOP 33" -- PDF 105 (2-15, 2/1/62)

Read at 150 dpi; clear.

1. "ADVANCE" -> "SET TBC AES"; -> "TBC AT NEW LEVEL" -> "IS LEVEL READY FOR TBC ACTION ?" -YES "TBC LDE ON"-> decision "NOOP'D OR NOOP MODE" -NO-> decision "LAOP 33 ?" (38.22.10.1) -YES-> decision "LAAR AT INT ADDR ?" (38.32.05.1) -YES "INT STORE"-> decision "TBC-ABC INTLKD ?" -YES-> decision "PREVIOUS INSTR PROPERLY EXECUTED ?" -YES "MAR MODE"-> decision "TBC ACTION TAKEN YET ?" -NO "AES ON"-> 2.
2. Wide box "START TRANSFER BUS TIMER" (38.25.01.1), outputs:
   - `E.M̅` -> "RESET TBC AES"; -> "GI TOB TO C REG" (35.17.01.1).
   - `E+M` -> "GO DATA FIELD ON TOB" (35.16.01.1).
   - `M` -> into a dashed enclosure captioned "ABC ACTION": decision "ABC TR. IND TIMER M ?" -YES-> box "START A BUS TIMER TO COMPLETE THE STORE OP".

**An I-box store to an internal (register) address is carried as a level with LAOP 33; "LAAR AT
INT ADDR" decides internal vs external. Its data passes level data field -> TOB -> C register
on the transfer bus timer, then the ABC's arithmetic bus timer completes the store. It requires
"TBC-ABC INTLKD" and "PREVIOUS INSTR PROPERLY EXECUTED" (MAR MODE), i.e. it is done in order,
at the arithmetic end, NOT at I-box time.**

## Fig 3.2.14 "ABC ADVANCE" -- PDF 106 (2-16, 2/1/62)

Read at 150 dpi; text clear, routing dense -- the list of boxes and labels is reliable, a few
line destinations are marked uncertain. No ALD numbers on the figure.

1. "ADVANCE" -> "SET ABC AES"; -> "ABC AT NEW LEVEL".
2. Decision "DISC. ABC ?": YES -> decision "ABC TBC INTLKD ?" -NO-> down the far-left rail to box "ADVANCE ABC". NO -> two branches: 3 and 2n.
   2n. Decision "NOOP MODE" -YES-> (far right, down) to step 9.
3. Decision "LEVEL PREPARATION FINISHED ?" -YES "LF & LC ON"-> decision "HSCLN MODE ?": YES -> line labelled "HOUSECLEAN MODE / HSCLN TIMER M" to the left rail B (the "COND. ABC ADV. COND." rail), with box "RESET ABC AES" off it. NO -> 4.
4. Decision "PREVIOUS INSTR PROPERLY EXECUTED ?": NO "INTRUPT" -> box "HSCLN TIMER WILL SET. HSCLN MODE". YES "MAR MODE" -> box "TRANSFER INDICATORS" -> 5.
5. Decision "STORE LEVEL":
   - YES -> decision "EXT. STO.": YES -> line down to the label ""NO DELAY ABC ADV." / TRANS. IND. M" -> rail B. NO -> box "A BUS TIMER ACTION".
   - NO -> decision "INT FETCH": YES -> box "A BUS TIMER ACTION". NO -> decision "BR REQ.": NO -> ""NO DELAY ABC ADV." / TRANS. IND. M" -> rail B. YES -> box "IND TEST E WILL RESET BR REQMTS."
6. Box "A BUS TIMER ACTION" -> decision "STORE TO INT. REQ. ?": NO, labelled "NOT "COND GI INT REQ"" -> junction J. YES, labelled ""COND GI INT. REQ"" -> decision "STORE TO INDICATOR REQ ?": NO, labelled "NOT "LAAR DEC ADDR. 11"" -> junction J. YES "ADD 11" -> decision "LAOP 41 ?": YES, labelled "NOT "NO ABC DEC BIN STO LEVEL"" -> junction J. NO -> box "IND. REQ. TIMER ACTION" -> line labelled "IND. REQ. TIMER M" -> rail B.
7. Junction J -> line labelled "AND CKT 5E / A BUS TIMER M" -> rail B.
8. Rail B, labelled "COND. ABC ADV. COND." -> decision "ABC TBC INTLKD ?": NO, labelled "ABC ADV. COND." -> decision "ABC AES OFF ?" -YES-> "ADVANCE ABC". YES -> decision "LAOP 27 OR 55" [printed "2?̶ OR 55"; second digit of the first number is damaged -- "27" by comparison with Fig 3.2.6's "LAOP 55,27"; uncertain] -NO-> decision "TBC MULT. ADV" -YES-> joins the "ABC ADV. COND." line.
9. (NOOP MODE = YES) Decision "HSCLN MODE": YES -> down to the line that joins "ABC ADV. COND." [via the junction at the bottom]. NO -> decision "EXT STO TAGS": YES -> decision "PREV STORES DONE" -YES, labelled "STAR BUSY NO STO REQ."-> same line. NO -> decision "LAST LEVEL" -YES "IC"-> decision "ABC TBC INTLK" -YES-> decision "ABC DONE" -YES "TFR IND M"-> same line.

**Per-action structure (no numbers printed): the ABC's dwell at a level is one of
(i) TRANS. IND. M only ("NO DELAY ABC ADV.") for an external store or a non-store, non-internal-
fetch, non-branch level; (ii) A BUS TIMER M for an internal store or internal fetch; (iii) A BUS
TIMER then IND. REQ. TIMER M for a store to the indicator register (address 11) unless LAOP 41;
(iv) HSCLN TIMER M in houseclean mode.**

## Fig 3.2.15 "SETTING MAR MODE" -- PDF 107 (2-17, 2/1/62)

Read at 150 dpi; clear.

1. Box "MAR MODE OFF" -> decision "ARITH INSTR EXECUTED ?" (both exits drawn DASHED):
   - NO -> decision ""NOOP IND TEST M" ON ?" -YES-> (a) box "SIGNAL PAU TO SET "MSTR TEST CMPLT" TRIG" (38.23.01.1); (b) down to the line "COND INTRPT OR MAR TRIGS" (38.35.02.1).
   - YES -> decision ""LA NORMAL IND TEST M" ON ?" -YES-> (a) box "SIGNAL PAU OF LA TESTS COMPLETE" (38.23.01.1); (b) decision ""EXEC UNIT IND TEST M" ON ?" -YES-> (i) decision "A CHKR IND TEST M ON ?" -YES-> line "COND INTRPT OR MAR TRIGS" (38.35.02.1); (ii) decision "A CHK COMPLETED ?" -YES, labelled "CHK COMP IMMEDIATE" (38.35.02.1)-> decision "A CHKR ERROR ?" -NO, labelled ""-P NOT ALL OTHER TEST TRIGS"" [leading characters uncertain]-> boxes "RESET ALL IND TEST TRIGGERS" (38.35.01.1), "PREVENT SETTING "A CHKR IND TEST M" TRIG" (38.35.01.1), and decision "INTRPT ?" [NO -> "SET "MAR MODE" AND "MAR NEXT INSTRN" TRIGS" (38.35.04.1); YES -> "SET "INTRPT NEXT INSTRN" TRIGGER" (38.35.05.1)].
2. Line "COND INTRPT OR MAR TRIGS" -> "NEW SETTING MAR" -> box "RESET ALL IND TEST TRIGGERS" (38.35.05.1) and decision "INTRUPT ?" [NO -> "SET "MAR MODE" AND "MAR NEXT INSTRN" TRIGS" (38.35.04.1); YES -> "SET "INTRUPT NEXT INSTRN" TRIGGER" (38.35.05.1)].

"MAR MODE" is the condition every TBC/ABC chart labels "PREVIOUS INSTR. PROPERLY EXECUTED ? --
YES / MAR MODE": it is set after the previous instruction's indicator tests complete with no
interrupt. [MAR is not expanded on the page.]

## Figs 3.2.16-3.2.21: the ABC action charts (fold-outs)

Printed numbering jumps 2-17 (PDF 107) -> 2-19/2-20 (PDF 108): each fold-out carries two
printed numbers. These six are large, dense fold-outs read at 150 dpi full-page. **Box texts
and ALD numbers below are reliable; for the long cross-page lines I give only the connections
I could follow, and say where I could not.** A parent re-check should crop at >= 300 dpi.

Common skeleton of 3.2.16/3.2.17/3.2.18: one wide bar "TRANSFER INDICATOR TIMER" (38.38.01.1)
with four outputs labelled, left to right, `E.M̅`, `E.M`, `M`, `E+M`. On the right margin the
`E+M` branch and the "INT. FETCH" branch leave the page labelled "STORES" and "FETCHES",
bracketed "TO A BUS TIMER" (they continue on Figs 3.2.19-3.2.21).

## Fig 3.2.16 "FP ABC ACTIONS-TRANSFER INDICATOR TIMER" -- PDF 108 (2-19/2-20, 2/1/62)

Entry: "ABC AT NEW LEVEL" -> side box "GO IND FIELD LEVELS TO MAIN IND REG AND GO IC FIELD LEVELS TO IC RUFFER" [sic, "RUFFER" = BUFFER] (35.27.01.1); -> decision "DISC ABC" -NO-> decision "LEVEL PREPARATION FINISHED ?" -YES "LF & LC ON"-> decision "HSCLN MODE ?":
- NO -> decision "PREVIOUS INSTR. PROPERLY EXECUTED ?": YES "MAR MODE" -> decision "ABC ACTION YET ?" -NO "ABC AES ON"-> the bar "TRANSFER INDICATOR TIMER" (38.38.01.1). NO "INTRUPT" -> joins the HSCLN MODE = YES path.
- YES -> decision "ABC ACTION YET ?" -NO "ABC AES ON"-> off page right: "START HSCLN TIMER" (38.39.02.1).

Bar outputs:
- `E.M̅`: "RESET ABC AES" (38.31.03.1) [digits uncertain: printed looks like "38.81.03.1"; Figs 3.2.17/3.2.18 print 38.31.03.1]; "GI X̅R̅ INDS TO IND REG" (35.27.03.1) [overbar over "XR" as printed]; decision "LAST INSTR. LEVEL ?" -YES "IC ON"-> "GI IC FIELD TO IC BUFFER" (35.27.02.1) and "RESET MAR MODE" (38.35.04.1); decision "NOOP ABC ?" -YES-> "SET NOOP MODE" (38.34.01.1); then decision "EXT STO TAGS": YES -> box ""NO DELAY IND. TEST"" (38.32[...]) ; NO -> decision "STORE TYPE LEVEL": NO -> ""NO DELAY IND. TEST""; [other exit] -> box "WAIT FOR A BUS TIMER". ""NO DELAY IND. TEST"" -> "SET IND. TEST E" (38.38.03.1) -> decision "NOOP MODE ?": YES -> "SET LA NOOP IND. TEST M" (38.35.03.1) -> "SIGNAL PAU TO SET "MSTR TEST COMPLT"" (38.23.01.1). NO -> "SET NORMAL IND. TEST M" (38.35.01.1) -> "SIGNAL PAU OF LA TESTS COMPLETE" (38.23.01.1).
- `E.M`: decision "1st INSTR. LEVEL ?" -YES, labelled ""MAR NEXT INSTR" ON"-> "RESET "MAR NEXT INSTR" TRIGGER" (38.35.04.1), and decision "IS THIS THE INTRPT FREE INSTR ?" -YES "INTRPT IS DISABLED"-> "RESET "DISABLE INTRPT" TRIGGER" (38.39.05.1). Also from `E.M`: "RESET UNIPOLAR INDS" (35.27.07.1). Then decision "NOOP MODE ?": YES -> line labelled "NON-ARITHMETIC" -> (a) decision "ABC FROM TAG ON ?" -YES-> decision "STORE OR INT. FETCH ?" -YES "LAAR BUSY"-> "RESET LAAR BUSY TRIG" (38.53.03.1); (b) decision "LAST INSTR. LEVEL ?" -YES "IC ON"-> decision "LAOP 11" -NO-> "RESET "MSTR TEST COMPLT" TRIG. IN PAU" (38.23.02.1) -> "ALLOW PAU TO RE-MEMORIZE THE INTRPT. LINE". NO -> decision "INT. FETCH ?" -YES "INT. TAG ON (X2 FETCH)"-> off page "FETCHES".
- `M`: decision "EXT STO TAGS": YES -> "ADV. ABC IF NOT INTLKD BY TBC"; NO -> decision "STORE TYPE LEVEL" -NO-> "ADV. ABC IF NOT INTLKD BY TBC".
- `E+M`: decision "NOOP MODE ?" -NO-> off page "STORES".
Margin notes bottom right: "OP X2 FETCH OR STORE" / "LAOP 13 STORE".

**Forwarding/store bookkeeping visible here: at the ABC, a level whose FROM tag is on and which
is a store or internal fetch RESETS the "LAAR BUSY" trigger when in NOOP mode ("NON-ARITHMETIC"
path) -- i.e. a cancelled (no-op'd) store level releases its LAAR at the arithmetic bus
counter.**

## Fig 3.2.17 "VFL ABC ACTIONS-TRANSFER INDICATOR TIMER" -- PDF 109 (2-21/2-22, 2/1/62)

Bar "TRANSFER INDICATOR TIMER", outputs:
- `E.M̅`: "RESET ABC AES" (38.31.03.1); "GI X̅R̅ INDS TO IND REG" (35.27.03.1); decision "LAST INSTR. LEVEL ?" -YES "IC ON"-> "GI IC FIELD TO IC BUFFER" (35.27.02.1), "RESET MAR MODE" (38.35.04.1); decision "NOOP ABC ?" -YES-> "SET NOOP MODE" and decision "VFL STORE OR FETCH LEVEL ?" -YES "SAU EN MEM TRIG ON"-> decision "1ST NOOP OF THIS INSTR. ?" -YES "NO NOOP MODE"-> "SET "VFL INSTR REJECT" TRIGGER" (38.23.04.1) -> "SIGNAL SAU TO STOP HSKPING." (38.23.04.1). Then decision "NOOP'D OR NOOP MODE?": YES -> box ""NO DELAY IND TEST"" (38.32.09.1); NO -> decision "ABC STORE ACTION RQD ?" -NO-> ""NO DELAY IND TEST"". -> "SET IND TEST E" (38.38.03.1) -> decision "NOOP MODE ?": YES -> "SET LA NOOP IND TEST M" (38.35.03.1) -> "SIGNAL PAU TO SET "MSTR TEST COMPLET"" (38.23.01.1); NO -> "SET "NORMAL IND TEST" M" (38.35.01.1) -> "SIGNAL PAU OF LA TESTS COMPLT" (38.23.01.1).
- `E.M`: decision "1ST INSTR. LEVEL ?" -YES-> "RESET "MAR NEXT INSTR" TRIG" (38.35.04.1) and decision "IS THIS THE INTRPT FREE INSTR ?" -YES ""MAR NEXT INSTR" ON"-> "RESET "DISABLE INTRPT" TRIG" (38.39.05.1); "RESET UNIPOLAR INDS" (35.27.07.1); decision "NOOP MODE" -NO-> decision "1ST INSTR. LEVEL ?" -YES "X1 35 75 48" [as printed; "48" may be "43"]-> "SET "SAU EN MEM" TRIG" (38.34.02.1); decision "LAST INSTR LEVEL ?" -YES "IC ON"-> "RESET SAU EN MEM TRIG" (38.34.02.1); decision "NOOP NODE" [sic]: YES "NON ARITH" -> decision "ABC FROM TAG ON ?" -YES-> decision "STORE OR INT. FETCH ?" -YES "LAAR BUSY"-> "RESET LAAR BUSY TRIG" (38.53.03.1); and decision "LAST INSTR LEVEL ?" -YES "IC ON"-> decision "LAOP 11" -> "RESET "MSTR TEST CMPLT" TRIG IN PAU" (38.23.02.1) -> "ALLOW PAU TO RE-MEMORIZE THE INTRPT LINE". [other exit] -> decision "INT. FETCH ?" -YES "INT TAG ON"-> off page "FETCHES".
- `M`: decision "NOOP MODE ?": YES -> "ADV. ABC IF NOT INTLKD BY TBC" (38.31.05.1); NO -> decision "A BUS TIMER ACTION RQD ?" -NO-> same box.
- `E+M`: decision "NOOP MODE ?" -NO-> off page "STORES".
Legend (bottom right), verbatim:
```
OP    X1  INSTR
LAOP  05  FETCH (1 of 1)
 "    03  FETCH (1 of 2)
 "    07  FETCH (2 of 2)
 "    17  STORE (1ST)
 "    23  STORE (2ND)
 "    21  STORE (SPECIAL)
 "    15  FETCH (SPECIAL)
```
**This legend is the VFL level complement: one instruction level (OP X1) plus separate FETCH
levels (05 / 03+07) and separate STORE levels (17, 23, 21) -- a VFL store that crosses a word
boundary has two store levels.**

## Fig 3.2.18 "BRANCH ABC ACTIONS-TRANSFER INDICATOR TIMER" -- PDF 110 (2-23/2-24, 2/1/62)

The branch-recovery chart. Bar "TRANSFER INDICATOR TIMER", outputs `E.M̅`, `E.M`, `M`, `E+M`.

`E.M̅` column (left):
- "RESET ABC AES" (38.31.03.1); "GI X̅R̅ INDS TO IND. REQ" [sic "REQ"] (35.27.03.1).
- decision "LAOP 31,57 ?" -YES-> "RESET TBC AES" (38.01.03.1) [as read; could be 38.21.03.1 as on the TBC charts -- digit uncertain] -> "ADV. TBC IF NOT INTLKD BY OCC".
- decision "NOOP ABC ?" -YES-> "SET NOOP MODE" (38.34.01.1).
- decision "LAOP 31 ?" -YES-> "RESET LF TAG" (36.01.09.1).
- decision "LAOP 11" -YES-> decision "RECOVERY REQ" -YES-> down to the junction above "BR SUCC & NO COND INDS".
- decision "LAST INSTR. LEVEL ?" -YES "IC ON"-> line labelled "NOT SIC BIN RECOVERY LEVEL" -> "GI IC FIELD TO IC BUFFER" (35.27.02.1), "RESET MAR MODE" (38.35.04.1); -> decision "NOOP OR NOOP MODE" -NO-> decision "LAOP 45 ?" -YES-> junction above "BR SUCC & NO COND INDS".
- lower: decision "NOOP OR NOOP MODE": YES -> "NO DELAY IND. TEST" (38.32.09.1); NO -> decision "ABC STORE ACTION RQD. ?" -[exit toward left]-> "NO DELAY IND. TEST" -> "SET IND. TEST E" (38.38.03.1) -> (line right) "RESET RQST CYCLE STORE MEM TRIGGER" (38.24.02.1), "RESET BR SUCC AND COND IND TRIGGERS" (38.24.03.1), and on (long line along the bottom) to decision "NOOP MODE ?" [YES -> "SET LA NOOP IND TEST M" (38.35.03.1) -> "SIGNAL PAU TO SET "MSTR TEST COMPLT"" (38.23.01.1); NO -> "SET NORMAL IND TEST M" (38.35.01.1) -> "SIGNAL PAU TO LA TESTS COMPLT" (38.23.01.1)].
- decision "BR SUCC & NO COND INDS" -YES-> "RESET LF TAG" (36.01.09.1), "SET BR RECOVERY INHB LOAD TRIGGER", and a line up and right to box "SET "I BOX RQST HSCLN" TRIGGER" (38.39.05.1).
- "SET "I BOX RQST HSCLN" TRIGGER" -> bar "START I BOX HSCLN TIMER": `E` -> "RESET I BOX RQST HSCLN TRIGGER"; `M` -> "SET LA "HSCLN MODE" TRIGGER" (38.39.04.1) -> decision "IS LA EMPTY ?": YES -> "START LA HSCLN OVER TIMER" (38.39.01.1); [other exit] -> "RESET "I BOX HSCLN TIMER"" (38.0[?].07.1) [one digit illegible].

`E.M` column (centre):
- decision "1st INSTR. LEVEL ?" -"MAR NEXT INSTR"-> "RESET MAR NEXT INSTR TRIGGER" (38.35.04.1), and decision "LAOP 75 ?" -NO-> decision "IS THIS THE INTRPT FREE INSTR. ?" -"INTRPT DISABLED"-> "RESET "DISABLE INTRPT" TRIGGERS" (38.39.05.1).
- "RESET UNIPOLAR INDS" (35.27.07.1).
- decision "BR. RECOVERY ?" -YES "45, 47"-> decision "SUCC BRANCH ?": YES -> decision "COND INDS ?" [YES -> "GI SAU'S COND INDS TO IND REQ." (35.27.05.1) [sic "REQ"]; NO -> decision "GOOD RECOVERY LEVEL" -NO "47"-> "GI CNIDC TO MK IND." (35.27.03.1)]; NO -> long line down to decision "SIC BIN" -YES "IC OFF"-> "SIGNAL I BOX OF NO BRANCH".
- a second decision "SIC BIN" -YES "IC OFF"-> "SIGNAL I BOX OF BRANCH" (38.38.02.1) [which of the two SIC BIN hexagons hangs off the SUCC = YES path I could not trace with confidence; by the labels, successful branch -> "SIGNAL I BOX OF BRANCH", unsuccessful -> "SIGNAL I BOX OF NO BRANCH"].
- decision "NOOP MODE ?": YES "NON-ARITH INSTR." -> decision "LAST INSTR. LEVEL ?" -YES "ICON"-> "RESET "MSTR TEST COMPLT" TRIG IN PAU" (38.23.02.1) -> "ALLOW PAU TO RE-MEMORIZE THE INTRPT LINE"; and decision "ABC FROM TAG ON ?" -YES-> decision "STORE OR INT. FETCH ?" -YES "LAAR BUSY"-> "RESET LAAR BUSY" (38.53.03.1). NO -> decision "INT. FETCH ?" -YES "INT. TAG ON"-> off page "FETCHES".

`M` column: decision "NOOP MODE ?": YES -> "ADV. ABC IF NOT INTLKD BY TBC" (38.31.05.1); NO -> decision "A BUS TIMER ACTION RQD ?" -NO-> decision "BRANCH REC RQD ?": NO -> "ADV. ABC IF NOT INTLKD BY TBC"; YES -> "IND TEST E WILL RESET THE BR RQMNTS" (38.24.03.1).
`E+M` column: decision "NOOP MODE ?" -NO-> off page "STORES" ("TO A BUS TIMER").

**Branch recovery, as this chart shows it (sequence, no numbers):** the branch level (LAOP 45
or 47, "BR. RECOVERY") reaches the ABC; under the transfer indicator timer the ABC tests
"SUCC BRANCH"; a successful branch with no conditional indicators outstanding ("BR SUCC & NO
COND INDS") does "RESET LF TAG", "SET BR RECOVERY INHB LOAD TRIGGER", "SET "I BOX RQST HSCLN"
TRIGGER" -> "START I BOX HSCLN TIMER" (E: reset the request; M: "SET LA "HSCLN MODE" TRIGGER")
-> "IS LA EMPTY ?" -> "START LA HSCLN OVER TIMER"; and the I box is told "SIGNAL I BOX OF
BRANCH" / "SIGNAL I BOX OF NO BRANCH". "GOOD RECOVERY LEVEL" and "NOT SIC BIN RECOVERY LEVEL"
name the recovery levels that follow the branch level.

## Fig 3.2.19 "I BOX AND I/O ABC ACTIONS-TRANSFER INDICATOR TIMER" -- PDF 111 (2-25/2-26, 2/1/62)

The chart for I-box-originated levels: pseudo stores, real I-box stores, I-box internal
fetches, recovery levels. Densest page of the set; inventory reliable, routing partly not.

**Legend (bottom right), verbatim -- the LAOP code table for I-box / I-O levels:**
```
OP   20  IO BX
 "   24  "  DISC
LAOP 25  "  DUMMY NOT CCW
     65  "    "    CCW
     02  I BOX PSEUDO STORE
     33  "     REAL STORE
     51  "     INT. FETCH
     04  PX PSEUDO STORE
     06  "    "     "    NOOP'D
     63  INDICATOR ONLY
     00  TEST LEVEL
     11  RAC RCY (NOOP RCY REQ)
```
("PX" as printed [uncertain: could be "BX"]; "RAC RCY" as printed [uncertain: "BAC"/"RAC";
cf. "BAC REC REQ" on Fig 3.2.5 -- the same thing, one of the two readings is wrong].)

Bar "TRANSFER INDICATOR TIMER", outputs `E.M̅`, `E.M`, `M` (no `E+M` output drawn on this chart).

`E.M̅` column:
- "RESET ABC AES" (38.31.03.1).
- decision "LAOP 02,04,33,63 ?" -YES-> decision "NOOP'D OR NOOP MODE ?" -NO-> "GI XR INDS TO IND REQ." (35.27.04.1) [no overbar on XR here].
- decision "LAOP 02, 04" -YES-> decision "NOOP'D ?" -YES-> decision "02" -YES-> "RESET ABC LF TAG" (36.01.09.1); and decision "NOOP MODE ?" -YES-> "RESET ABC LF TAG".
- decision "LAOP 33 EXT. ?" -YES-> decision "NOOP'D OR NOOP MODE" -NO-> "RESET ABC LF TAG".
- decision "06" -YES-> "RESET ABC LF TAG".
- "GI X̅R̅ INDS TO IND REQ." (35.27.03.1) [overbar on XR].
- decision "LAOP 00,02,25, 63,65,33 EXT. ?" -YES-> decision "NOOP'D OR NOOP MODE ?" -NO-> "RESET TBC AES" (38.21.03.1) -> "ADV. TBC, IF NOT INTLKD BY OCC".
- decision "NOOP ABC" -YES-> "SET NOOP MODE" (38.34.01.1).
- decision "LAOP 11" -YES-> decision "NOOP RECOVERY REQ" -YES-> down to "SET "PSEUDO INTRPT INHIBIT LOAD" TRIGGER".
- decision "LAST INSTR. LEVEL ?" -YES "IC ON"-> "GI IC FIELD TO IC BUFFER" (35.27.02.1), "RESET MAR MODE" (38.35.04.1); decision "02,04,33,63 ?" -YES-> decision "NOOP'D OR NOOP MODE ?" -YES-> (to "SET "PSEUDO INTRPT INHIBIT LOAD" TRIGGER"); decision "06 ?" -YES-> same.
- box "SET "PSEUDO INTRPT INHIBIT LOAD" TRIGGER" (38.39.03.1) -> box "SET "I BOX RQST HSCLN" TRIGGER" (38.39.05.1), captioned "(I BOX)" -> bar "START I BOX HSCLN TIMER": `E` -> "RESET "I BOX RQST HSCLN" TRIGGER"; `M` -> "SET LA "HSCLN MODE" TRIGGER" (38.39.04.1) -> decision "IS LA EMPTY ?" -YES-> "START LA HSCLN OVER TIMER" (38.39.01.1).
- decision "NOOP'D OR NOOP MODE ?": YES -> "NO DELAY IND TEST" (38.32.09.1); NO -> decision "AEC STORE ACTION RQD. ?" [printed "AEC"; = ABC] -NO-> "NO DELAY IND TEST" -> "SET IND. TEST E" (38.38.03.1) -> "RESET "LAST CYCLE STORE" AND STORE INHIBIT TRIGGERS" (38.24.02.1); and -> decision "NOOP MODE ?": YES -> "SET LA NOOP IND TEST M" (38.35.03.1) -> "SIGNAL PAU TO SET "MSTR TEST COMPLT"" (38.23.01.1); NO -> decision "NON-ARITH INSTR. ?" [YES, labelled ""LA ONLY MAR NEXT""-> the LA NOOP IND TEST M box; NO -> "SET NORMAL IND. TEST M" (38.35.01.1) -> "SIGNAL PAU OF LA TESTS COMPLETE" (38.23.01.1)].

`E.M` column:
- decision "1st INSTR LEVEL" -YES ""MAR NEXT INSTR" ON"-> "RESET "MAR NEXT INSTR"" (38.35.04.1); decision "IS THIS THE INTRPT FREE INSTR ?" -YES "INTRPT IS DISABLED"-> "RESET "DISABLE INTRPT" TRIGGER" (38.39.05.1); "RESET UNIPOLAR IND'S" (35.27.07.1).
- decision "06 ?" -YES-> "GI CNIDC TO MK IND." (35.27.03.1).
- decision "INT FETCH ?" -YES "INT TAG ON"-> off page "FETCHES" ("TO A BUS TIMER").
- decision "33 EXT. ?" -YES-> decision "NOOP'D OR NOOP MODE" -NO-> decision "IN ECC ?" -NO-> "RESET "STORE CHK IND TEST M"" (38.35.02.1).
- decision "NOOP MODE ?": YES "NON ARITH" -> decision "ABC FROM TAG ON ?" -YES-> decision "STORE OR INT. FETCH ?" -YES "LAAR BUSY"-> decision "51" -> "RESET "LAAR BUSY"" (38.58.03.1) [as read; Figs 3.2.16-18 print 38.53.03.1 -- one of 53/58 is a misread] and "SET ABC NOOP TAG" (36.07.03.1) [which exit of "51" feeds which box not traceable; a "NO" label sits by the line to both]. NO -> decision "NON-ARITH INSTR. ?" -YES-> (joins NON ARITH). Then decision "LAST INSTR LEVEL ?" -YES "IC ON"-> "RESET "MSTR TEST COMPLT" TRIG IN PAU" (38.23.02.1) -> "ALLOW PAU TO RE-MEMORIZE THE INTRPT LINE".

`M` column:
- decision "NOOP MODE ?": YES -> decision "LAOP 51 ?" -NO-> "ADV. ABC IF NOT INTLKD BY TBC" (38.31.05.1). NO -> decision "INT FETCH ?" -NO-> decision "LAOP 33 INT. ?": NO -> "ADV. ABC IF NOT INTLKD BY TBC"; YES -> decision "ABC-TBC INTLKD ?" -YES-> decision "TB TIMER M ?" -YES-> off page "STORES" ("TO A BUS TIMER").

**Store handling for I-box levels, as shown:** an I-box pseudo store (02) or noop'd pseudo
store (06), an external real store (33 EXT), when reached by the ABC, gets "RESET ABC LF TAG"
(freeing the level "to signal for SCC action", cf. Fig 3.2.20's wording); an internal real
store (33 INT) waits for "ABC-TBC INTLKD" and "TB TIMER M" and then goes "TO A BUS TIMER"; an
internal fetch (51) goes to the A bus timer chart (Fig 3.2.20). A NOOP'D recovery level
(LAOP 11 with "NOOP RECOVERY REQ", or a noop'd 02/04/33/63/06 at the last instruction level)
sets ""PSEUDO INTRPT INHIBIT LOAD"" and starts the I BOX HSCLN TIMER -> LA "HSCLN MODE".

## Fig 3.2.20 "INTERNAL FETCH ABC ACTIONS-ARITHMETIC BUS TIMER" -- PDF 112 (2-27, 2/1/62)

Clear. (The printed number is 2-27 alone; the right half of the scan is blank.)

Legend (bottom left), verbatim:
```
OP   X2  FP  FETCH
LAOP 05  VFL  "   (1 OF 1)
 "   03   "   "   (1 OF 2)
 "   07   "   "   (2 OF 2)
 "   37  BI   "
 "   51  I BOX "
```

Entry "INT. FETCH" -> (38.33.01.1) wide bar "ARITH BUS TIMER", the bar itself is marked with
three trigger names along its top edge: `EE` (left), `E` (centre), `M` (right). Also from the
entry: decision "LAOP 37 ?" -YES-> box "SIGNAL IND. REQ TO RESET 0-19 ASYNCHRONOUS INDS,
IMMEDIATELY AFTER FETCHES" (35.27.04.1).
Bar outputs:
- `EE` -> "SEND "PASS DATA" SIGNAL TO A CHKR" (38.23.03.1); -> "GO INT. ADDRESS SPECIFIED BY LAAR ONTO ACIB" (35.24.04.1, .05.1, .06.1).
- `E.M̅` -> "RESET TRANS. IND. TIMER M" (38.38.02.1); "RESET TBC AES" (38.21.03.1); "ADV. TBC IF INTLKD WITH ABC IF NOT INTLKD BY OCC"; -> decision "LAAR AT ADD. 7 OR 11 ?": NO -> "SIGNAL A CHKR TO CHK PARITY"; YES -> "SIGNAL A CHKR NOT TO CHK PARITY" (38.23.03.1).
- `M` -> "ADV. ABC IF NOT INTLKD BY TBC" (38.31.05.1).
- `E.M` -> "RESET LAAR BUSY TRIGGER" (38.53.03.1); -> decision "LAOP 51 ?" -YES-> "RESET LF TAG TO SIGNAL FOR SCC ACTION" (36.01.09.1) and "GI ACOB INTO ABC LEVEL" (35.23.02.1); [not 51] -> decision "LAOP 07 ?": NO -> "GI ACOB TO C REG"; YES -> "GI ACOB TO D REG" (35.22.01.1). Also from `E.M`: decision "FP INSTR. ?": YES "X2" -> "SEND "START" SIGNALS TO SAU & PAU" (38.23.01.1). NO -> decision "LAST OPERAND ?" -YES "05 07 37"-> "SET "SAU GO" TRIGGER" (38.23.04.1) -> "SEND "GO" SIGNAL TO SAU" -> decision "SAU STARTED EXECUTION ?" -YES ""SAU HSKPING" OVER"-> "RESET "SAU GO" TRIGGER" (38.23.04.1); and -> decision "LAOP 37" -YES-> "RESET 0-19 SYNCHRONOUS IND'S IN IND. REQ." (35.27.04.1), "RESET SAU'S ERROR TRIGGER" (35.27.04.1).

**This is the forwarding-relevant chart.** An operand whose address is an INTERNAL register
(INT tag on) is NOT fetched at level-load time: the level carries the address in a LAAR, and
at the ABC the arithmetic bus timer does "GO INT. ADDRESS SPECIFIED BY LAAR ONTO ACIB" (EE),
then gates the result from the ACOB to the C or D register (or, for an I-box internal fetch
LAOP 51, "GI ACOB INTO ABC LEVEL" then "RESET LF TAG TO SIGNAL FOR SCC ACTION"), and "RESET
LAAR BUSY TRIGGER" (E.M). **The arithmetic bus timer has three triggers EE, E, M and the
actions are spread over EE, E.M̅, E.M, M** -- the only timer on these pages with more than two.

## Fig 3.2.21 "STORE ABC ACTIONS-ARITHMETIC BUS TIMER" -- PDF 113 (2-29/2-30, 2/1/62)

Read at 150 dpi full page, right-centre region re-read from a 300-dpi crop (that region's text
below is confirmed at 300 dpi). Left third of the scan is speckled.

Legend (bottom right), verbatim:
```
OP X2 - FP STORE
LAOP 13 - FP STORE
LAOP 17 - VFL (1ST)
LAOP 23 - VFL (2ND)
LAOP 21 - VFL (SPECIAL)
LAOP 41 - BI
LAOP 33 - I BOX REAL
```

Two entries:
- left: "TRANS IND TIMER / LAOP 33 INT" -> (38.33.01.1) the bar.
- right: "TRANS IND TIMER / E + M" -> decision "WHAT IS BEING STORED ?":
  - "C - D REG / 17, 23, 41" -> decision "IS STORE DATA READY ?" -YES, labelled ""LAST CYCLE STORE MEM" ON"-> the bar (at its `EE` mark).
  - "ACOB / X2, 13, 21" -> decision "IS STORE DATA READY ?" -YES, labelled ""LAST CYCLE STORE MEM" TRIG ON"-> (38.33.02.1) the bar; and -> decision "HAS A ZERO DIVISOR CANCELLED ANY REMAINDER THAT WAS TO BE STORED ?" -YES, labelled ""STORE INHIBIT MEM" TRIG ON"-> the same entry (38.33.02.1).
Bar "ARITH BUS TIMER" (marked `EE` and `M` along its length; entry ALDs 38.33.01.1 at the left end and 38.33.02.1 mid-bar -- i.e. the 33-INT / C-D-register path enters at EE, the ACOB path enters later, at 38.33.02.1 = the E trigger's page per Table 3.4.1). Outputs:

- `EE` -> "SEND "PASS DATA" SIGNAL TO A CHKR" (38.23.03.1); -> decision "WHERE IS DATA ?": "C REG / 17, 41, 33 INT" -> "GI C REG TO ACIB"; "D REG / 23" -> "GI D REG TO ACIB" (35.21.01.[1]).
- `E.M̅` -> "RESET "TRANS IND TIMER M"" (38.38.02.1); -> decision "LAST INSTR LEVEL ?" -YES "IC ON"-> "DELAY IND TEST" (38.32.09.1) -> "SET IND TEST E" (38.38.03.1) -> "RESET: BR SUCC COND IND'S LAST CYCLE STORE, STORE INHIBIT TRIGGERS" (38.24.02.1, 38.24.03.1); -> decision "NON-ARITH INSTR ?" [YES -> "SET LA NOOP IND TEST M" (38.35.03.1) -> "SIGNAL PAU TO SET "MSTR TEST COMPLETE" TRIG" (38.23.01.1); NO -> "SET NORMAL IND TEST M" (38.35.01.1) -> "SIGNAL PAU OF LA TESTS CMPLT" (38.23.01.1)]. Also `E.M̅` -> decision "C+D STORE OP ?" -YES "17 23 41 33 INT"-> "SIGNAL A CHKR TO CHK PARITY" (38.23.03.1); -> decision "33 INT": YES -> "SIGNAL A CHECKER NOT TO SET ITS CHK CMPLT TGR"; NO "17, 23, 41" -> "RESET TBC AES" (38.21.03.1) -> "ADV TBC IF INTLKD WITH ABC, AND NOT INTLKD BY OCC" (38.23.03.1); and decision "23 ?" -YES-> (joins the line to "SIGNAL A CHECKER NOT TO SET ITS CHK CMPLT TGR").
- `M` -> decision "GOOD INTERNAL STORE ?": NO -> "ADV ABC IF NOT INTLKD BY TBC" (38.31.05.1). YES -> decision "ADDR 11 ?": NO -> "ADV ABC IF NOT INTLKD BY TBC". YES -> decision "BI STORE ?" -YES "LAOP41"-> "ADV ABC IF NOT INTLKD BY TBC". Also `M` -> decision "33 INT ?" -YES-> decision "ARC TBC INTLKD ?" [printed "ARC"; = ABC] -YES-> "ADV TBC IF NOT INTLKD BY OCC".
- `E.M` -> decision "ACOB STORE OP ?" -YES "X2,13,21"-> decision "STORE DATA READY ?" -YES ""LAST CYCLE STORE MEM" ON"-> "SIGNAL A CHKR THAT ACOB DATA IS ACCEPTED" (38.23.03.1). And `E.M` -> decision "LAAR INT ?":
  - YES -> "RESET LAAR BUSY TRIG" (38.23.03.1) [as printed at 300 dpi; elsewhere this box carries 38.53.03.1 -- possibly a printing slip]; -> box **"GI ACOB TO LAAR ADDER IF NOT ADDR 1, 5, or 6" (35.25.01.1, .02.1, .03.1)** -> decision "ADDR 8 ?" -YES-> decision "FP STORE ?" -YES-> "GI ACOB POS. 60-63 TO SIGN BYTE REG POS 4-7" (35.25.02.1); -> decision "BI STORE ?" -[exit labelled "33 INT / X2 / 13 / 17 / 23"]-> decision "ADDR 11 ?" -YES-> decision "33 INT ?": YES -> bar "START IND REG TIMER"; NO -> decision "STORE DATA READY ?" -YES ""LAST CYCLE STORE MEM" ON"-> "START IND REG TIMER". "START IND REG TIMER" -> **"GI MODIFIED XR IND'S FROM IND REG TO THE UPDATED INDEX IND REG" (35.26.02.1)** and "ADV ABC IF NOT INTLKD BY TBC".
  - NO -> decision "STORE DATA READY ?" -YES-> "RESET ABC LF TAG" (36.01.09.1) and "GI ACOB INTO ABC DATA FIELD" (35.23.02.1).

**Store handling as this chart shows it (the central facts for the model):**
1. A store level's data is placed on the arithmetic checker in bus (ACIB) from the C or D
   register (VFL 17/41, I-box 33 INT from C; VFL second word 23 from D) or comes on the ACOB
   (FP X2/13, VFL special 21).
2. **Internal store ("LAAR INT" = YES): the data goes "ACOB TO LAAR ADDER" -- i.e. to the
   internal register addressed by the LAAR -- and the LAAR BUSY trigger is reset.** "IF NOT
   ADDR 1, 5, or 6" (those internal addresses are not written this way).
3. **External (memory) store ("LAAR INT" = NO): when "STORE DATA READY", "GI ACOB INTO ABC
   DATA FIELD" and "RESET ABC LF TAG".** The store data is written BACK INTO THE LOOK-AHEAD
   LEVEL's data field, and the LF tag is reset as the signal for the SCC (store check counter)
   to act on it (cf. Fig 3.2.20 "RESET LF TAG TO SIGNAL FOR SCC ACTION"). The memory store is
   then issued from the level by the SCC (Fig 3.2.25), not by the arithmetic unit.
4. A store to internal address 11 (the indicator register) additionally runs the IND REG
   TIMER, which gates "MODIFIED XR IND'S FROM IND REG TO THE UPDATED INDEX IND REG".

## Fig 3.2.22 "LA HOUSECLEAN TIMER" -- PDF 114 (2-31, 2/1/62)

(Previously read by the earlier agent; re-read at 150 dpi. Left-column boxes are faint.)

Bar "HSCLN TIMER" (38.39.02.1), outputs:
- `E.M̅` -> "GI CNIDC IND TO MK IND." (35.27.03.1); "RESET ABC AES" (38.31.03.1); decision "PSEUDO STORE ?" -YES-> "RESET ABC LF TAG" (36.01.09.1); decision "LA HSCLN MODE ?" -NO-> decision "HSCLN DUE TO "INTRUPT" ?" -YES, labelled ""INTERPT NEXT INSTR" ON"-> "RESET "INTRPT NEXT INSTR" TRIG" (38.35.05.1); "SET "INTRPT INHIBIT LOAD" TRIG" (38.39.03.1); "SET "DISABLE INTRPT" TRIG" (38.39.05.1) [faint]; "SET I BOX RQST HSCLN" TRIG" (38.39.05.1) [faint] -> bar "START I BOX HSCLN TIMER" captioned "(I BOX)", ALD "38.03.10.1" [faint, uncertain]: `E` -> "RESET "I BOX RQST HSCLN" TRIG" (38.39.05.1) [faint]; `M` -> decision "EXEC UNITS IDLE ?" -YES-> "SET LA HSCLN MODE TRIG" (38.39.04.1) and "RESET "EXEC UNITS IDLE" TRIG" (38.39.04.1); "SET LA HSCLN MODE TRIG" -> "RESET I BOX HSCLN TIMER" (38.02.07.1) and decision "LA EMPTY ?" -YES-> "START LA "HSCLN OVER" TIMER" (38.39.01.1).
- `E.M` -> "RESET LAAR BUSY TRIG" (38.53.03.1); decision "LA HSCLN MODE ?" -NO-> decision "SAU INSTR ?": YES "X1,35,43" -> "SET "VFL INSTR INTRPT" TRIG" (38.23.04.1) -> decision "SAU STARTED PRE-EXECUTION ?" -YES "HSKPING"-> "RESET "VFL INSTR INTRPT" TRIG" (38.23.04.1) and "SET "VFL INSTR REJECT" TRIG" (38.38.04.1) -> "SIGNAL SAU TO STOP HSKPING" (38.23.04.1) and decision "SAU IDLE ?" -YES ""VFL NOT OPERATING""-> "SET "EXECUTION UNITS IDLE" TRIG" (38.39.04.1). NO -> decision "PAU INSTR ?": YES "X2" -> dashed box "PAU DISCOVERS INTRPT COND" -> decision "PAU IDLE ?" -YES "PAU IDLE"-> "SET "EXECUTION UNITS IDLE" TRIG"; NO -> same box.
- `M` -> decision "HSCLN MODE ?" -YES-> "ADV ABC IF NOT INTLKD BY TBC" (38.31.05.1) -> "SET ABC AES" (38.31.03.1) -> "RESET HSCLN TIMER M" (38.39.02.1).

**Housecleaning as a sequence:** in houseclean mode the ABC steps through the remaining levels
one HSCLN TIMER pass per level (E.M̅: reset pseudo-store LF tags; E.M: "RESET LAAR BUSY TRIG";
M: advance ABC, re-arm), i.e. each level is discarded individually; entry to the mode waits for
"EXEC UNITS IDLE" (SAU told to stop housekeeping / PAU idle); it ends when "LA EMPTY" starts
the "HSCLN OVER" timer.

## Fig 3.2.23 "LA HOUSECLEAN OVER TIMER" -- PDF 115 (2-32, 2/1/62)

Read at 150 dpi; clear.

Bar "LA HSCLN OVER TIMER" (38.39.01.1), outputs:
- `E.M̅` -> "RESET CN, DF, & DS IND'S AT ALL LA LEVELS" (38.70.01.1); "RESET "MAR MODE" TRIG" (38.35.04.1); "RESET PAU'S "MSTR TEST CMPLT" TRIG" (38.02.06.1); "RESET "VFL START" TRIG" (38.23.05.1); "RESET PAU'S "FP ENABLE" TRIG" (38.02.06.1); "RESET LA HSCLN MODE TRIG" (38.39.04.1); "RESET: INTRPT, PSEUDO INTRPT, & BR. RECOVERY INHIBIT LOAD TRIGGERS" (38.39.03.1); then -> "SET LA "NOOP IND TEST M" TRIG" (38.35.03.1) -> decision "INTRPT ?": NO -> "SET "MAR MODE" AND "MAR NEXT INSTR." TRIGS" (38.35.04.1); YES -> "SET "INTRPT NEXT INSTR" TRIG" (38.35.05.1).
- `E.M` -> "GI IC BUFFER TO IC REG" (38.02.06.1); **"GI IND REG XR IND'S INTO UPDATED INDEX IND REG" (38.02.06.1)**; "SET PAU'S " WAIT " TRIG TO ALLOW IT TO RECEIVE NEW INSTR'S" (38.02.06.1); "GI BIT ADDR. OF LEFT-MOST (SET) IND INTO I BOX W REG" (38.02.06.1).
- `M` -> "SIGNAL I BOX OF HSCLN COMPLETE" (38.02.05.1) -> (dashed) box "I BOX ACKNOWLEDGES RECEIPT OF SIGNAL & RESETS THE HSCLN OVER TIMER" (38.03.08.1) -> (dashed) box, **verbatim: "IF THIS WAS A BR. RECOVERY HSCLN, I BOX WILL PLACE THE "BRANCH TO" ADDR IN THE IC REG. TRANSFER THE IC REG INTO THE IAUC IC FIELD, THEN GI THE (ABC) IC FIELD INTO THE IC BUFFER" (35.27.02.1)**.

**Recovery end: ONE "HSCLN OVER" timer pass (E.M̅, E.M, M) closes housecleaning: IC buffer ->
IC register, architected index indicators -> the I box's "updated" copy, inhibit-load triggers
reset, then the I box is signalled; the timer's M trigger is held until the I box acknowledges
(a handshake, not a fixed time).**

## Fig 3.2.24 "ABC ACTION ON BAC (LAOP 11)" -- PDF 116 (2-33, 2/1/62)

Read at 150 dpi; clear.

Header strip, "BAC LOOK AHEAD DATA FIELD" -- the data-field layout of a LAOP 11 level, verbatim
(bit numbers above, field names in the strip):
```
 0                 18   50                      55    59          61      62          IC
| BRANCH TO ADDRESS | X | SPECIFIED INDICATOR FIELD | X | I BOX BRANCHED BIT | X | RESET INDIC BIT | BRANCH IF ON BIT | ORIGINAL ICR |
```
(Bit labels printed: 0, 18, 50, 55, 59, 61, 62, IC. Box "GATE DATA FIELD BITS 54, 55, 59, 61, 62".)

1. "ABC AT NEW LEVEL" -> decision "LAOP 11" -YES-> (a) step 2; (b) long line round the right to step 5.
2. Decision "DOES SPECIFIED INDIC = BIT 62":
   - NO -> decision "DID I BOX BRANCH" -YES "(BIT 59)"-> box "TFR INDIC TIMER SET PSUDO IRPT RECOVERY" and box "BLOCK INDIC RESET"; and -> box 4.
   - YES -> decision "COND INDICATORS": YES -> [to "TFR INDIC TIMER SET PSUDO IRPT RECOVERY" / "BLOCK INDIC RESET" and box 4]. NO -> decision "DID I BOX BRANCH": NO -> box "TFR INDIC TIMER SET BRANCH RECOVERY" and box 4; YES "(BIT 59)" -> decision "INTERRUPT" -YES-> "TFR INDIC TIMER SET BRANCH RECOVERY" and box 4.
4. Box "DELAY ABC ADV, RESET MAR MODE & MSTR TEST COMP" with the note "RESET LF" beside it. (Four lines enter it.)
5. Decision "INDIC RESET BLOCKED ?" (a dashed line joins it to "BLOCK INDIC RESET") -NO-> decision "INDIC RESET SPECIFIED ?" -YES "(BIT 61)"-> decision "BIT 55": YES -> "RESET AE"; NO -> decision "BIT 54": NO -> "RESET AL"; YES -> "RESET AH".

**Branch-on-indicator recovery level ("BAC", LAOP 11): the I box has already guessed and acted
("I BOX BRANCHED BIT", bit 59); the level carries the branch-to address (bits 0-18), the
specified indicator, the "branch if on" sense (bit 62) and the ORIGINAL ICR. At the ABC the
real indicator is compared with bit 62: agreement with the I box's action -> no recovery;
disagreement -> "TFR INDIC TIMER SET BRANCH RECOVERY" / "PSUDO IRPT RECOVERY".** [The exact
pairing of YES/NO exits to the two recovery boxes is as drawn above; the logic reading
"mismatch -> recovery" is mine.]

## Fig 3.2.25 "SCC ADVANCE" -- PDF 117 (2-34, 2/1/62)

(Previously read by the earlier agent; re-read at 150 dpi. Small tags under hexagons: 2E, 2D, 2F, 2G.)

1. "ADV" -> "SET SCC AES" (38.51.03.1); -> "SCC AT NEW LEVEL" -> decision "DISC SCC ?": YES -> decision "SCC ABC INTLKD ?" (2E) -NO-> left rail (to "SCC SING ADV. COND."). NO -> 2.
2. Decision "LC ON ?" -YES-> decision "LF ON ?": YES -> the line labelled "SCC DEC ADV. COND" (38.51.05.1) (step 4). NO -> (a) box "SET SCC LDE TRIG" (38.52.07.1) -> "TO PAGE 2" [= Fig 3.2.26]; (b) decision "SCC LDE ON ?" -YES-> 3.
3. Decision "ILLEGAL PS STORE ?": YES, labelled "(38.52.06.1) / 42, 44, 46" -> "SCC DEC ADV. COND" line. NO -> decision "EXT STORE":
   - YES "BCU" -> line labelled **"STORE DATA TIMER M / 31, 33, 21, 13, 23, 17, X2"** -> junction K.
   - NO "I BOX" -> decision "INDEX STORE": YES "X REG" -> line labelled **"WRITE INDEX LA M / 02, 04, 06, 13, 17, 23, X2"** -> junction K. NO "Y REG" -> line labelled **"I TIMER NO INDEX TRANSFER M / 45, 51"** -> junction K.
   Junction K -> decision "SCC AES OFF ?" -YES-> decision "SCC ABC INTLKD ?" -NO-> (38.51.06.1) box "SCC MULT. ADV. COND.".
4. "SCC DEC ADV. COND" -> decision "SCC ABC INTLKD ?" (2D): NO -> left rail. YES -> decision "ABC TBC INTLKD ?": NO -> decision "ABC ADVANCING ?" (2F) -YES, labelled "ANTIC ABC ADV."-> left rail. YES -> decision "TBC OCC INTLK" -NO-> decision "ABC ADVANCING" -YES-> decision "TBC ADVANCING TCC" [as printed; "TCC" uncertain] (2G) -YES-> left rail.
5. Left rail -> (38.51.04.1) box "SCC SING ADV. COND."; with "SCC MULT. ADV. COND." -> (38.51.01.1) "ADV. SCC" -> "RESET LF TAG" (36.01.02.1), "SET SCC AES" (38.51.03.1), "RESET SCC LDE" (38.52.07.1).

**The SCC's dwell at a store level is one of three timers, by store destination:
external memory store = STORE DATA TIMER M; index-storage (X reg) store = WRITE INDEX (LA) M;
other I-box (Y reg) transfer, LAOP 45/51 = "I TIMER NO INDEX TRANSFER M". A level that is
LC-on and LF-on (nothing to store) passes straight through ("SCC DEC ADV. COND").**

## Fig 3.2.26 "SCC ACTIONS" -- PDF 118 (2-35, 2/1/62)

Read at 150 dpi; clear except two small labels.

1. "SCC AT NEW LEVEL" -> decision "SCC AES ON" -YES-> (a) decision "SEC LDE ON" [printed "SEC"; = SCC] -YES-> three parallel decisions:
   - "LAOP 51" -YES ("4D")-> box R.
   - "REAL STORE INST." -YES-> decision "LAAR DEC IX ADR" -YES ("4E")-> box R.
   - "HSCLN MODE" -YES-> decision "PS STORE OR BR RCY LEVEL" -YES ("4F")-> box R.
   Box R: "REQUEST 4TH PRORITY FOR I CHKR" [sic] (38.52.08.1) -> "DROP OK TO I CHK" (35.01.03.1) -> "PREVENT I BOX FROM STARTING A CHECK CYCLE"; and -> decision "IS CHKR IN USE" -NO "(NO "0" REQ)"-> decision "IS OP CHK NEEDED" -NO "NO "3" REQ"-> decision "IS CHKR REQ FOR A CORRECT CYCLE" -NO "NO SINGLE ERROR"-> box "START LA TO I TIMER" (35.06.01.1) [continues on Fig 3.2.27].
   (b) decision "IS STORE REG READY FOR LA DATA NEXT" -YES "(LA NEXT)"-> decision "IS TOB IN USE" -NO "(NO TBUS TIMER E+M)"-> decision "IS STAR BUSY": NO -> bar S. YES -> decision "STORE ACCEPTED YET" -YES, labelled "NO STORE MEM REQ" [middle word faint]-> bar S.
   Bar S: "STO DATA TIMER" (35.02.01.1) [as read; Table 3.4.1 gives 38.53.04.1 for the STORE DATA TIMER triggers -- digits here uncertain], outputs: `E.M̅` -> "RESET SCC AES", "RESET FROM TAG"; `E` -> decision "SCC AES ON" -YES-> "INFORM STORE REG" and "GO LA TO TOB"; `M` -> decision "SCC AES OFF" -YES-> "ADV SCC IF NOT INTLKD WITH ABC" (38.51.06.1).

**External store sequencing as shown: the level's data goes level -> TOB -> "STORE REG" under
the STO DATA TIMER, but only when the store register is ready for LA data ("LA NEXT", set up by
Fig 3.2.12), the TOB is free (no transfer-bus timer running), and the store address register
is not busy or the previous store has been accepted ("IS STAR BUSY" / "STORE ACCEPTED YET").
The memory store therefore happens AFTER the arithmetic unit has finished with the level, from
the look-ahead, one store at a time through one STAR.** The I-checker "4TH PRIORITY" request
is for stores/transfers INTO the I box (LAOP 51, a real store whose LAAR decodes an index
address, or in houseclean mode a pseudo-store / branch-recovery level).

## Fig 3.2.27 "SCC STORES TO I BOX" -- PDF 119 (2-36, 2/1/62)

Read at 150 dpi; clear. **The chart that answers the index-register question.**

Legend (top right), verbatim:
```
LAOP 51 I BOX FETCH
     13 ARITH STORE
     17 ARITH STORE
     23 ARITH STORE
     X2 ARITH STORE
     45 BR. RECOV
     02 PS STORES
     04 PS STORES
     06 PS STORES
```

1. Connector "A" -> bar "LA TO I TIMER E", outputs:
   - `E` -> "GO SCC DATA ON ICIB" (35.11.01.1); -> decision "STORE DATA FOR IX STORAGE ?": NO "45, 51" -> "GI ICOB TO Y REG"; YES "13, 17, 23 / X2, 02, 04 / 06" -> "GI ICOB TO X REG" (38.02.06.1).
   - `E.M̅` -> "RESET SCC AES" (38.51.03.1); "DROP "NO 0 REQ" LINE TO HOLD I CHKR PRIORITY" (35.01.01.1); "SIGNAL I CHKR TO CHK PARITY" (35.15.01.1); -> decision "STORE DATA FOR IX STORAGE ?" (35.06.02.1): NO "(Y REG) / 45, 51" -> bar T. YES "(X REG) / 13, 17, 23, X2 / 02, 04, 06" -> bar U.
2. Bar T "I TIMER NO TRANS INDEX M", outputs: `E.M` -> decision "45 or 51 ?": "51" -> "SIGNAL I BOX TO LOOK FOR I CHKR PARITY ERROR SIGNAL" (38.02.07.1); "45" -> "CONDITION THE SETTING OF MK IND ON I CHKR PARITY ERROR" (35.27.04.1). `M` -> "ADV. SCC IF NOT INTLKD BY ABC" (38.51.06.1).
3. Bar U "LA TO I TIMER INDEX TRANS. M", outputs:
   - `E.M` -> decision "PS STORE ?": NO "13, 17, 23, X2" -> "CONDITION THE SETTING OF MK IND ON I CHKR PARITY ERROR" (35.27.04.1). YES "02 04 06" -> "CONDITION THE SETTING OF MK IND ON I CHKR PARITY ERROR" (35.27.04.1) and box, **verbatim: "NULLIFY ANY OTHER STORE LEVELS THAT ARE ADDRESSED TO THIS SAME IX ADDRESS BY SETTING OP BIT 0." (35.31.03.1)**
   - `M` -> decision "PS STORE ?": NO -> **"GO LAAR BITS 13-17 TO I BOX (IX ADDR)" (35.29.01.1)**; YES -> **"GO OP CODE BITS 1-4 TO I BOX (IX ADDR)" (35.30.01.1)**. And `M` -> (35.33.01.1) the double bar "START CLEAR AND WRITE INDEX TIMERS" = "CLEAR INDEX TIMER" | "WRITE INDEX TIMER", outputs: `E` -> **"SIGNAL I BOX TO START THE INDEX STORAGE CLEAR/STORE OPERATION" (35.30.01.1)**; `E.M` [printed "E. M"; bar not visible] -> decision "PS STORE ?" -NO "13, 17, 23, X2"-> "RESET LAAR BUSY TRIG" (38.53.03.1) and "RESET FROM TAG H2" [as printed, "H2" uncertain] (36.16.01.1); `M` -> "ADVANCE SCC IF NOT INTLKD BY ABC" (38.51.06.1).

**What this says about index registers and pending levels (source facts, then my reading):**
- Fact: a store into index storage by an ARITHMETIC instruction (LAOP 13, 17, 23, X2 with a
  LAAR that decodes an index address) is NOT done when the E-box produces the result. It is
  done by the **SCC**, the LAST of the five counters, from the look-ahead level: level data ->
  ICIB -> I checker -> ICOB -> X register, index address from "LAAR BITS 13-17", then "SIGNAL I
  BOX TO START THE INDEX STORAGE CLEAR/STORE OPERATION", timed by the CLEAR INDEX and WRITE
  INDEX timers (cf. Buchholz/CE Fig 2.10.1: index storage clear-and-write 1.2 usec).
- Fact: **pseudo-store levels (LAOP 02, 04, 06, "PS STORES") carry an INDEX ADDRESS in "OP CODE
  BITS 1-4" and data destined for the X register / index storage**, and Fig 3.2.26 shows the
  SCC acts on a "PS STORE OR BR RCY LEVEL" only in "HSCLN MODE". I.e. a pseudo store is written
  back to index storage only during housecleaning (recovery); in normal running the ABC just
  resets its LF tag (Fig 3.2.19, 3.2.22).
- Fact: when a pseudo store is written back, "NULLIFY ANY OTHER STORE LEVELS THAT ARE ADDRESSED
  TO THIS SAME IX ADDRESS BY SETTING OP BIT 0."
- My reading (NOT printed): the I box modifies index registers itself, ahead of the arithmetic
  unit, and each such modification loads a pseudo-store level holding the OLD contents (this is
  Buchholz §15 / Perf. Char. p.3-22's "index-recovery" level); recovery restores the oldest
  saved value per index register and nullifies younger saves of the same register.
- **Nothing on PDF 92-119 says the I box WAITS to change an index register while levels are
  pending.** The mechanism shown is the opposite: change at once, save for recovery. The only
  waits shown are IAUC load-enable waits on "RECOVERY NEEDED", "NEXT LEVEL IN SCC", "BOTH LAARS
  BUSY" and "STORE BEING DONE" (Fig 3.2.1).
- **Whether a level holds the already-modified operand address:** no level on these pages has
  an operand-address field at all. The level layout used throughout is tag bits, op code (LAOP),
  I-box indicators, IC, and a DATA field. A memory operand is fetched at load time (LLP 2:
  "DATA ON IMOB" -> "GI IMOB INTO DATA FIELD") by a fetch the I box issued ("FETCH ACCEPTED AND
  NO COMPARE", "MEM FETCH CNCLD", Fig 3.2.1), so the effective address was formed by the I box
  BEFORE the level was loaded and the arithmetic unit never sees or re-forms it. Addresses
  survive only in the two LAARs, for stores and internal fetches ("I BOX WILL LOAD LAAR 1 OR
  2"; "SET FROM 1 & LAAR 1 BUSY"; "GO INT. ADDRESS SPECIFIED BY LAAR ONTO ACIB"). This is
  structural evidence, not a sentence; no page here states it in words.

---

## B.3 Table 3.4.1 "7101 CE CONSOLE INDICATORS" -- the look-ahead timer triggers

PDF 175 (printed 4-16), 176 (4-17), 177 (4-18), 178 (4-19); all dated 2/1/62; read at 150 dpi,
clear. Columns as printed: INDICATOR LOCATION | TRIGGER LOCATION (ALD PAGE) | DESCRIPTIVE TITLE
| SCAN CARD NO. | CARD COL. | CARD ROW (T TO B).

**The table gives NO duration and NO purpose for any timer** -- only the trigger's name, its
ALD page and where its light is. "Purpose" below is taken from the flow diagram that starts the
timer (Part B above), and is marked as such. "Duration" does not exist in this manual's pages
92-119 / 175-178.

| # | timer | trigger | indicator | ALD page | scan card / col / row | PDF | started in (figure) -- what it times |
|---|---|---|---|---|---|---|---|
| 1 | OPERAND CHECK TIMER | E | 2Q012 | 35.05.01.1 | 1 / 61 / 12 | 178 | Fig 3.2.3 -- OCC: level data through the I checker (ECC check), sets LC |
| | | M | 2Q013 | 35.05.01.1 | 1 / 61 / 11 | 178 | |
| 2 | OPERAND CORRECT TIMER | E | 2Q014 | 35.05.02.1 | 1 / 61 / 0 | 178 | Fig 3.2.3 -- second pass on a single ECC error |
| | | M | 2Q015 | 35.05.02.1 | 1 / 61 / 1 | 178 | |
| 3 | TRANSFER BUS TIMER | E | 2Q024 | 38.25.01.1 | 1 / 62 / 12 | 178 | Figs 3.2.6-3.2.11, 3.2.13 -- TBC: level data/op code onto TOB, to C/D register, start SAU/PAU, I/O select |
| | | M | 2Q025 | 38.25.02.1 | 1 / 62 / 11 | 178 | |
| 4 | TRANSFER INDICATOR TIMER | E | 2N002 | 38.38.01.1 | 1 / 62 / 2 | 176 | Figs 3.2.16-3.2.19 -- ABC: indicator field to indicator register, IC field to IC buffer, branch test |
| | | M | 2N003 | 38.38.02.1 | 1 / 62 / 3 | 176 | |
| 5 | ARITHMETIC BUS TIMER | EE | 2N004 | 38.33.01.1 | 1 / 62 / 4 | 176 | Figs 3.2.20, 3.2.21 -- ABC: internal fetch via LAAR; store data C/D/ACOB -> ACIB -> level or internal register |
| | | E | 2N005 | 38.33.02.1 | 1 / 62 / 5 | 176 | |
| | | M | 2N006 | 38.33.03.1 | 1 / 62 / 6 | 176 | |
| 6 | INDICATOR REGISTER TIMER | E | 2N007 | 35.26.01.1 | 1 / 62 / 7 | 176 | Figs 3.2.14, 3.2.21 ("IND. REQ. TIMER", "START IND REG TIMER") -- store to indicator register, address 11 |
| | | M | 2N008 | 35.26.01.1 | 1 / 62 / 8 | 176 | |
| 7 | HOUSECLEAN TIMER | E | 2N009 | 38.39.02.1 | 1 / 62 / 9 | 176 | Fig 3.2.22 -- one pass per level discarded in houseclean mode |
| | | M | 2N010 | 38.39.02.1 | 1 / 63 / 12 | 176 | |
| 8 | LA HOUSECLEAN OVER TIMER | E | 2N011 | 38.39.01.1 | 1 / 63 / 11 | 176 | Fig 3.2.23 -- end of housecleaning, hand back to I box |
| | | M | 2N012 | 38.39.01.1 | 1 / 63 / 0 | 176 | |
| 9 | LA INDICATOR TEST TIMER | E | 2N021 | 38.38.03.1 | 1 / 63 / 9 | 177 | Figs 3.2.16-19, 3.2.21 ("SET IND TEST E") |
| | LA NORMAL INDICATOR TEST TIMER | M | 2N022 | 38.35.01.1 | 1 / 64 / 12 | 177 | "SET NORMAL IND TEST M" |
| | LA NOOP INDICATOR TEST TIMER | M | 2N026 | 38.35.03.1 | 1 / 64 / 2 | 177 | "SET LA NOOP IND TEST M" |
| 10 | STORE DATA TIMER | E | 2L007 | 38.53.04.1 | 1 / 65 / 12 | 175 | Figs 3.2.25, 3.2.26 -- SCC: level data -> TOB -> store register (external memory store) |
| | | M | 2L008 | 38.53.04.1 | 1 / 65 / 11 | 175 | |
| 11 | LA TO INST UNIT TIMER ("LA-I E TGR") | E | 2L013 | 35.06.01.1 | 1 / 65 / 0 | 175 | Figs 3.2.26, 3.2.27 -- SCC: level data -> I checker -> X or Y register of the I box |
| | "LA TO I INDEX XFER M TGR - LA-I XS/F M TGR-" | M | 2L014 | 35.06.02.1 | 1 / 65 / 1 | 175 | Fig 3.2.27 "LA TO I TIMER INDEX TRANS. M" |
| | "LA TO NO INDEX XFER M TGR - LA-I M-NX TGR-" | M | 2L015 | 35.06.02.1 | 1 / 65 / 2 | 175 | Fig 3.2.27 "I TIMER NO TRANS INDEX M" |
| 12 | CLEAR INDEX TIMER | E | 2L016 | 35.33.01.1 | 1 / 65 / 3 | 175 | Fig 3.2.27 -- index storage clear/store started by the SCC |
| | | M | 2L017 | 35.33.01.1 | 1 / 65 / 4 | 175 | |
| 13 | WRITE INDEX TIMER | E | 2L018 | 35.33.01.1 | 1 / 65 / 5 | 175 | Fig 3.2.27 |
| | | M | 2L019 | 35.33.01.1 | 1 / 65 / 6 | 175 | |

Titles exactly as printed for the rows above: "OPERAND CHECK TIMER E TRIGGER", "OPERAND CHECK
TIMER M TRIGGER", "OPERAND CORRECT TIMER E TRIGGER", "OPERAND CORRECT TIMER M TRIGGER",
"TRANSFER BUS TIMER E TRIGGER", "TRANSFER BUS TIMER M TRIGGER", "TRANSFER INDICATOR TIMER E
TRIGGER", "TRANSFER INDICATOR TIMER M TRIGGER", "ARITHMETIC BUS TIMER EE TRIGGER", "ARITHMETIC
BUS TIMER E TRIGGER", "ARITHMETIC BUS TIMER M TRIGGER", "INDICATOR REGISTER TIMER E TRIGGER",
"INDICATOR REGISTER TIMER M TRIGGER", "HOUSECLEAN TIMER E TRIGGER", "HOUSECLEAN TIMER M
TRIGGER", "LA HOUSECLEAN OVER TIMER E TRIGGER", "LA HOUSECLEAN OVER TIMER M TRIGGER", "LA
INDICATOR TEST TIMER E TRIGGER", "LA NORMAL INDICATOR TEST TIMER M TRIGGER", "LA NOOP INDICATOR
TEST TIMER M TRIGGER", "STORE DATA TIMER E TRIGGER", "STORE DATA TIMER M TRIGGER", "LA TO INST
UNIT TIMER E TGR - LA-I E TGR-", "LA TO I INDEX XFER M TGR - LA-I XS/F M TGR-", "LA TO NO INDEX
XFER M TGR - LA-I M-NX TGR-", "CLEAR INDEX TIMER E TRIGGER", "CLEAR INDEX TIMER M TRIGGER",
"WRITE INDEX TIMER E TRIGGER", "WRITE INDEX TIMER M TRIGGER".

A fourteenth timer appears in the FIGURES but not on these four table sheets: **"I BOX HSCLN
TIMER"** (Figs 3.2.18, 3.2.19, 3.2.22; E and M outputs; ALDs read as 38.02.07.1 / 38.03.10.1
[uncertain]). It is an I-box trigger and will be elsewhere in Table 3.4.1 (not searched).

Other rows on the same sheets that bear on the model (all read from the image):

| indicator | ALD | title | PDF |
|---|---|---|---|
| 2L001 | 38.51.03.1 | SCC ADVANCE ENABLES SEQUENCE TRIGGER (**this expands "AES"**) | 175 |
| 2L002 | 38.52.07.1 | SCC LATE DECODE ENABLE TRIGGER (**this expands "LDE"**) | 175 |
| 2L006 | 38.62.02.1 | GATE OUT LAMIB TRIGGER | 175 |
| 2L025 | 38.53.01.1 | LAAR 1 BUSY TGR | 175 |
| 2L026 | 38.53.01.1 | LAAR 2 BUSY TGR | 175 |
| 2L032-2L035 | 38.01.04.1 / 38.11.04.1 / 38.21.02.1 / 38.31.02.1 | IAUC / OCC / TBC / ABC COUNTER POS 3 TRIGGER | 175 |
| 2L036 | 38.51.02.1 | SCC COUNTER POS 3 TRIGGER | 176 |
| 2N001 | 38.31.03.1 | ABC ADVANCE ENABLES SEQUENCE TRIGGER | 176 |
| 2N014 | 38.35.04.1 | ALLOW MAR FOR NEXT INSTRUCTION TRIGGER | 176 |
| 2N015 | 38.35.04.1 | **MODIFY ADDRESSABLE REGISTER MODE TRIGGER** (expands "MAR MODE") | 176 |
| 2N016 | 38.34.01.1 | NOOP MODE TRIGGER | 176 |
| 2N017 | 38.39.04.1 | LA HOUSECLEAN MODE TRIGGER | 177 |
| 2N018 | 38.35.05.1 | INTERRUPT NEXT INSTRUCTION TRIGGER | 177 |
| 2N019 | 38.39.05.1 | LA DISABLE INTERRUPT LINE TRIGGER | 177 |
| 2N020 | 38.23.04.1 | SAU INSTRUCTION INTERRUPT BUFFER TRIGGER | 177 |
| 2N023 | 38.35.01.1 | EXECUTION UNIT INDICATOR TEST M TRIGGER | 177 |
| 2N024 | 38.35.01.1 | ARITHMETIC CHECKER INDICATOR TEST TRIGGER | 177 |
| 2Q001 | 38.01.06.1 | IAUC ADVANCE ENABLES SEQUENCE TRIGGER | 177 |
| 2Q002 | 38.01.10.1 | LOAD PULSE MEMORY TRIGGER | 177 |
| 2Q004 | 38.39.03.1 | INTERRUPT INHIBITS LOAD TRIGGER | 178 |
| 2Q005 | 38.39.03.1 | PSEUDO-INTERRUPT INHIBITS LOAD TRIGGER | 178 |
| 2Q006 | 38.39.03.1 | BRANCH RECOVERY INHIBITS LOAD TRIGGER | 178 |
| 2Q011 | 38.11.06.1 | OCC ADVANCE ENABLES SEQUENCE TRIGGER | 178 |
| 2Q021 | 38.21.03.1 | TBC ADVANCE ENABLES SEQUENCE TRIGGER | 178 |
| 2Q023 | 38.22.15.1 | TBC LATE DECODE ENABLE TRIGGER | 178 |

Per-level rows (level 1 = 2Q0xx on PDF 178, level 2 = 2N0xx on PDF 177, level 3 = 2L0xx on PDF
176, level 4 = 2J0xx on PDF 175), i.e. **what a look-ahead level physically holds**, titles
verbatim from the level-1 sheet: "FROM BIT 1 - LEVEL 1" (36.16.02.1), "FROM BIT 2 - LEVEL 1"
(36.13.03.1), "LA LEVEL 1 OP CODE FIELD POS 00-09" (36.09.03.1 THROUGH 36.09.12.1), "PAR ON OP
CODE POS 1-4 FOR PS J ADDR ONLY" (36.09.13.1), "DISCONNECT TAG BIT LEVEL 1", "NOOP TAG BIT
LEVEL 1", "WORD BOUNDARY CROSSOVER TAG BIT LEVEL 1", "LOOKAHEAD OPERATION CODE TAG BIT LEVEL
1", "INSTRUCTION COUNTER VALID TAG BIT LEVEL 1", "INTERNAL FETCH TAG BIT LEVEL 1", "LEVEL
CHECKED TAG BIT LEVEL 1", "LEVEL FILLED M TAG BIT LEVEL 1", **"INDEX STORE TAG - LEVEL 1"
(36.09.19.1)**, "EXTERNAL STORE TAG - LEVEL 1" (36.09.14.1), "INTERNAL STORE TAG - LEVEL 1"
(36.09.15.1), fifteen indicators ("LA LEVEL 1 CONDITIONAL MACH CHK INDICATOR", "INSTRUCTION
REJECT", "OPERATION CODE INVALID", "ADDRESS INVALID", "DATA STORE", "DATA FETCH", "INSTRUCTION
FETCH", "INDEX FLAG", "INDEX COUNT ZERO", "INDEX VALUE BELOW ZERO", "INDEX VALUE ZERO", "INDEX
VALUE ABOVE ZERO", "INDEX LOW", "INDEX EQUAL", "INDEX HIGH"), "LA LEVEL 1 IC FIELD POS 00-16",
"... PARITY FOR BITS 00-16", "... POS 17", "... POS 18", "... PARITY FOR BITS 17-18", and (on
the next sheet) "LA LEVEL 1 OPERAND FIELD POS 00-75" (31.01.01.1 THROUGH 31.01.64.1, 31.02.01.1
THROUGH 31.02.10.1, 31.29.01.1 AND 31.29.02.1).

**"PAR ON OP CODE POS 1-4 FOR PS J ADDR ONLY" confirms Fig 3.2.27: in a pseudo-store (PS)
level the op-code field positions 1-4 hold the J (index register) address.** And **there is no
operand-ADDRESS field in a level** -- op code (10 positions), tags, FROM bits, indicators, IC
(19 bits + parity), operand DATA (positions 00-75 as printed).

## B.4 Summary of what the pages DO and DO NOT give for the questions asked

| question | what PDF 92-119 / 175-178 show | where |
|---|---|---|
| Level loading | Three load-pulse types. LLP 1: data from the I checker out bus, LF and LC set together. LLP 2: memory operand, data arrives later on IMOB ("MEM SEL LA n" sets the LF E trigger), LF only, then the OCC checks it. LLP 3: store-type levels, "I BOX WILL LOAD LAAR 1 OR 2", "SET FROM 1 & LAAR 1 BUSY" / "SET FROM 2 & LAAR 2 BUSY". Load enable: "TYPE 1 & 2 LOAD ENABLE" unless "BOTH LAARS BUSY"; "TYPE 3 LOAD ENABLE" needs a free LAAR or "STORE BEING DONE". | Figs 3.2.1, 3.2.2 |
| Operand fetch | Memory operand: fetched at load by the I box; "FETCH ACCEPTED AND NO COMPARE" sets the IAUC load pulse memory; "MEM FETCH CNCLD" re-arms. Internal-register operand: NOT fetched at load; fetched at the ABC by "GO INT. ADDRESS SPECIFIED BY LAAR ONTO ACIB". | Figs 3.2.1, 3.2.2, 3.2.20 |
| Forwarding (LAAR) | LLP 2: "IS LAAR COMPARE ENABLED ?" -> "ADDRESS COMPARE ?"; Fig 3.2.1 "FETCH ACCEPTED AND NO COMPARE". What happens ON a compare (the forwarding itself) is not drawn in a way I could read on PDF 93 at the resolution used; Fig 3.2.21's "GI ACOB INTO ABC DATA FIELD" (store data written into the store's own level) and Fig 3.2.20's "GI ACOB INTO ABC LEVEL" are the data paths a forward would use. [NOT ESTABLISHED from these pages: the compare-hit path.] | Figs 3.2.1, 3.2.2, 3.2.20, 3.2.21 |
| Store handling | Store address in LAAR 1 or 2 (FROM tag); data returned to the level's data field by the ABC, LF tag reset; the SCC then performs the store: external -> STORE DATA TIMER via TOB/store register/STAR; index storage -> LA-to-I timer + CLEAR/WRITE INDEX timers; other I-box register -> LA-to-I "no index transfer". | Figs 3.2.12, 3.2.21, 3.2.25-27 |
| I-box index arithmetic vs pending levels | No wait is shown. Pseudo-store levels (LAOP 02/04/06) hold a J address in op-code positions 1-4 plus data; written back to index storage by the SCC only in houseclean mode; "NULLIFY ANY OTHER STORE LEVELS THAT ARE ADDRESSED TO THIS SAME IX ADDRESS BY SETTING OP BIT 0." A per-level "INDEX STORE TAG" exists (Table 3.4.1); what the I box does with it is not on these pages. | Figs 3.2.19, 3.2.26, 3.2.27; Table 3.4.1 |
| Does a level hold the modified operand address? | A level has no address field; memory operands are fetched by the I box before/at load, so the address is formed (indexed) by the I box once and never re-formed. Structural, not stated in words. | Table 3.4.1 level rows; Figs 3.2.1, 3.2.2 |
| Branch recovery / housecleaning | Branch level LAOP 45/47 ("BR. RECOV"), BAC level LAOP 11 with data-field layout; ABC decides; "SET BR RECOVERY INHB LOAD TRIGGER", I BOX HSCLN TIMER, LA HSCLN MODE, one HSCLN TIMER pass per level, pseudo stores written back via SCC, "LA EMPTY" -> HSCLN OVER TIMER -> "SIGNAL I BOX OF HSCLN COMPLETE" -> I box places the "BRANCH TO" address in the IC register. | Figs 3.2.5, 3.2.18, 3.2.19, 3.2.22-24, 3.2.26-27 |
| Per-action cycle counts | **None printed.** Every action is under a named timer's E / M (/EE) trigger condition. Several timers are HELD by a handshake rather than fixed: TB TIMER M until the exchange/disk accepts or rejects (3.2.7), until the SAU accepts (3.2.8), until the PAU starts (3.2.11); HSCLN OVER until the I box acknowledges (3.2.23); STO DATA waits on STAR / "STORE ACCEPTED YET" (3.2.26). So even with a clock source the LA is not a fixed-count pipeline. The audit's caution stands: E, E.M̅, E.M, M, E+M are overlapping trigger STATES; do not count them as cycles. | all |

---

# PART C -- Where the current model differs

## C.a Memory / bus (`bsv/StretchMemory.bsv`, `bsv/StretchStorage.bsv`)

1. **Unit busy time.** `StretchMemory.bsv:60` `memCycleClocks = 7` ("2.1 us at 0.3 us per
   clock", header lines 4-5, 36-40, from Buchholz p.202). PDF 274 step B.5: "Busy trigger
   (logic 13.05.01) is on for 1800 nanosec" = 6 slots. The page does not say the Busy trigger
   IS the whole unavailable period (the CSU's own cycle may run past it), so this is a
   documented 6-vs-7 question, not a proven error. (`clock_unit.md` §7 item 3 already lists it.)
2. **Read latency and where it is counted from.** `StretchMemory.bsv:61` `memReadClocks = 5`
   ("~1.6 us read-out"), counted from the unit accepting the request, then one more clock in
   `mkMBCU.route` before `respReady`. PDF 275: IMOB data at 1Y **and at look-ahead level 4**
   brackets "the sixth SP pulse ... generated after the SP pulse which initiated the gate I
   pulse". So the printed reference point is the gate-I pulse and the count is six SP pulses,
   the same for 1Y and for an LA level. **`clock_unit.md` §5.2 / §7 item 3 ("LA at the 5th SP
   pulse and 1Y at the 5th-6th") should be read carefully: the 5th-pulse figure is the MEM SEL
   LA select pulse, not the data; the text puts LA-level data at the sixth pulse too, and Fig
   4.1.4 draws MEM SEL LA ending about where IMOB DATA begins.** The model's single latency for
   all destinations therefore AGREES with the page; a separate, earlier LA latency would not.
   What gate I is relative to the requester's request remains unknown.
3. **Minimum data-out time.** Data-out gate "does not occur earlier than 1050 nanosec after
   select-memory pulse", 290 ns wide (PDF 275) -- sub-slot values with no home in a rule-per-
   clock model (`microarchitecture_roadmap.md:228`); recorded, not a model change.
4. **Unit naming / grouping.** `StretchMemory.bsv:64-76` `unitOf`: units 0-3 = the four-way
   block (first 65,536 words), units 4-5 = the two-way block. PDF 274 names the CSUs **A0, A1,
   B0, B1, B2, B3** (Table 4.1.1 plus step B.3): a two-unit group and a four-unit group. Which
   group holds the low addresses is not on these pages; the letters suggest the two-unit group
   is "A". Worth checking against another source before trusting the model's order.
5. **Destinations / return channels.** `StretchMemory.bsv:78-84` `RetTag`: 0 = "operand
   channel", 1-2 = 1Y/2Y, 3-6 = LA levels 1-4 (seven tags). The procedure shows eight
   destination select pulses, each with its own delay line: SEL 1Y, SEL 2Y, MEM SEL LA 1-4, SET
   BX-BFR (exchange), SEL HX (disk synchronizer), plus PANEL KEYS as a data source; and three
   memory-out buses (IMOB, BX MOB, HX MOB). The model's tag 0 "operand channel" (used by
   execute()'s follow-up reads) has no counterpart; exchange and disk channels are absent
   (acknowledged in the header, lines 42-45).
6. **Bus priority order.** `StretchStorage.bsv:684-686` `order = {0,3,4,5,6,1,2}` and stores
   first (`:679`). Nothing in Procedure 1 confirms or contradicts a priority order; do not cite
   these pages for it.
7. **Where stores come from.** `StretchStorage.bsv:676-683`: a store queue fed by the
   execute path, drained to the bus ahead of reads. Figs 3.2.12/3.2.25/3.2.26: a memory store
   is issued from the look-ahead level by the SCC through the store register and a single STAR,
   gated by "IS STAR BUSY" / "STORE ACCEPTED YET", after the ABC has put the data back into the
   level. Also PDF 274 B.4: a store drives the CSU "readout trigger" at the time the address
   arrives (clear-then-write), and store data is sampled into the MDR by a separate
   data-in-gate (B.7).
8. **Read-then-wait-on-stores.** `StretchStorage.bsv:698-712`: every read waits for the store
   queue to empty ("the look-ahead's LAAR forwarding replaces this in stage 3"). The manual's
   mechanism is the LAAR compare at load (Fig 3.2.2 "IS LAAR COMPARE ENABLED ? / ADDRESS
   COMPARE ?", Fig 3.2.1 "FETCH ACCEPTED AND NO COMPARE"), with TWO LAARs.

## C.b Look-ahead (`bsv/StretchLookAhead.bsv`, `bsv/StretchTypes.bsv`, `bsv/StretchIBox.bsv`, `bsv/StretchCore.bsv`, `docs/microarchitecture_plan.md` §1a)

1. **What a level is.** `StretchTypes.bsv:707-748`: one whole `DecodedInstr` per level
   (`kind: Whole`), with `da`, `storeAddr`, `waitFor`. Manual: a level is a PART of an
   instruction identified by a two-digit LAOP code, with no address field. The `LaKind` enum
   (`StretchTypes.bsv:721-731`) can now be tied to printed codes (legends of Figs 3.2.17,
   3.2.19, 3.2.20, 3.2.21, 3.2.27):
   `LaOp` = OP X1 (VFL instr) / OP X2 (FP); `LaOpnd` = LAOP 05 (1 of 1), 03 (1 of 2), 07 (2 of
   2), 15 (special); `LaStore` = 17 (VFL 1st), 23 (VFL 2nd), 21 (VFL special), 13 (FP store),
   33 (I box real store), 41 (BI); `LaInt` = 51 (I box int. fetch), 37 (BI fetch) and any level
   with the INT tag; `LaIxRec` = 02 (I box pseudo store), 04 ("PX pseudo store"), 06 (noop'd
   pseudo store); `LaBRec` = 45 / 47 (branch recovery), 11 ("RAC RCY" / BAC); `LaNoop`/`LaTest`
   = 63 (indicator only), 00 (test level); I/O = OP 20 (BX), 24 (DISC), LAOP 25 / 65 (dummy).
2. **The level carries an address the model re-derives.** `microarchitecture_plan.md` §1a row
   "A look-ahead level carries the operand address the I-box computed during preparation ..."
   (line 83) and `StretchIBox.bsv:296-300` ("the real I-box computes the effective address
   during preparation and the level carries it"). The pages refine this: the level carries the
   operand DATA (memory operands) -- the I box issued the fetch itself -- and the ADDRESS lives
   only in LAAR 1/2 for stores and internal fetches. So the E-box never needs the address for a
   fetched operand at all; "carrying the address in the level" is the right fix for the model
   but the real structure is "carry the data; carry store addresses in the two LAARs".
3. **The I-box index-write stall.** `StretchIBox.bsv:314-325` `levelIndexedBy` /
   `levelIndexedByWord` and their uses at `:362-416`; commit 3204601. The pages show no such
   wait and a mechanism that makes it unnecessary (address formed at load; index change saved
   as a pseudo-store level, LAOP 02/04/06, written back only on recovery, Fig 3.2.27). The
   model's stall is a correctness device with no hardware counterpart, as its own comment says;
   these pages are the citation for that statement and for what replaces it.
4. **The new-level-waits-for-index-store stall.** `StretchCore.bsv:1439-1451`
   `indexStorePending` (a level indexed by Xj waits for a pending level that STORES into Xj).
   This one plausibly HAS a hardware counterpart: an arithmetic store into index storage is
   performed last, by the SCC (Fig 3.2.27, LAOP 13/17/23/X2 with "GO LAAR BITS 13-17 TO I BOX
   (IX ADDR)"), and each level has an "INDEX STORE TAG" (Table 3.4.1, 36.09.19.1). What the I
   box does while such a tag is up is NOT on the pages read -- look in the I-unit flow
   diagrams (Figs 3.1.x, e.g. PDF 91 Fig 3.1.27 has boxes "COND STORE WAIT" and "BLOCK ...")
   before changing this.
5. **One LAAR-equivalent per level vs two LAARs.** `StretchLookAhead.bsv:45-55` and
   `StretchTypes.bsv:744-747` (`storeAddr` per level, `waitFor` an earlier level). Manual: two
   LAARs, "LAAR 1 BUSY" / "LAAR 2 BUSY" triggers, FROM 1 / FROM 2 tags per level; a third
   store-type level cannot load until a LAAR frees ("BOTH LAARS BUSY" -> wait for "STORE BEING
   DONE", Fig 3.2.1). The model allows four simultaneous store-address-bearing levels.
6. **Five counters collapsed to head/tail.** `StretchLookAhead.bsv:60-62, 88-98`
   (`retireHead` frees the level when the E-box finishes). Manual: a level is free for reload
   only when the SCC has passed it (Fig 3.2.1 "NEXT LEVEL IN SCC" / "SCC AT NEXT LEVEL"); a
   store level stays occupied after execution until its memory or index store is done.
   (`microarchitecture_plan.md` §1a line 82 already says "collapsed".)
7. **Who issues operand fetches.** `StretchLookAhead.bsv:67-83` `collect()`: the look-ahead
   issues one fetch per clock for any valid level with a `da`. Manual: the I box issues the
   fetch as part of the LLP 2 load; the level only receives ("DATA ON IMOB", MEM SEL LA n).
   Internal-register operands are read at the ABC through the LAAR (Fig 3.2.20), not at load.
8. **Operand check.** No OCC stage in the model (`StretchMemory.bsv:45-47`: "No ECC modeling
   (the I checker's cycle is charged in the instruction unit, stage 2)"). Manual: every memory
   operand level makes one OPERAND CHECK TIMER pass through the shared I checker ("3RD PRIORITY
   CHKR REQUEST", waits if "CHKR IN USE") before the TBC may use it (LF & LC ON), Fig 3.2.3.
9. **Branch recovery.** `StretchCore.bsv:179-183, 1262, 1534-1542` (index/indicator snapshot
   `xSnap`, `la.cancelAll()`); `StretchLookAhead.bsv:100-105` `cancelAll` clears all four
   levels in one clock. Manual: level-by-level housecleaning (one HSCLN TIMER pass each),
   pseudo-store write-backs through the SCC and the CLEAR/WRITE INDEX timers, then HSCLN OVER
   with an I-box handshake (Figs 3.2.18, 3.2.22, 3.2.23, 3.2.27). `microarchitecture_plan.md`
   §1a lines 81 and 85 already record "by snapshot"; these pages give the real sequence.
10. **I-box-class instructions and the look-ahead.** `StretchLookAhead.bsv:50-55`: "an
    I-box-class instruction waits for the levels to drain before executing (no recovery levels
    yet)". Manual: I-box instructions load levels of their own (02, 04, 06, 33, 51, 63, 00, 11,
    45/47) and do not wait for a drain.
11. **Per-action times.** Any fixed count attached to an LA action in the model remains
    un-sourced: the pages give trigger structure only, and several timers are handshake-held
    (B.4). `docs/spec_lookahead.md`'s `[NOT IN THE SOURCES]` stands as to numbers.

---

# PART D -- Passages not read with confidence

Procedure 1 (PDF 272-279): none of the text; every value in A.2 is clear. Only the figure
geometry (A.5) is approximate by nature, and "gate I" vs "gate 1" is typographically ambiguous.

Look-ahead:
- **Fig 3.2.1 (PDF 92) and Fig 3.2.2 (PDF 93-94)**: seen only at the Read tool's default
  resolution. Box inventory given; connections and most ALD numbers NOT verified. In
  particular the LLP 2 "ADDRESS COMPARE" branch (the forwarding decision) and the boxes
  "SET OP OF DS IND" / right-hand "SET IJ IND / SET NOOP TAG" on PDF 93 are faint.
- "IJ" (as in "SET IJ IND", "RESET LC, NOOP, IJ"): could be "IJ" or "U"; not expanded.
- Fig 3.2.3: the bar over M on the second "EM" output of START OPERAND CORRECT TIMER.
- Fig 3.2.5: "NOOP 13 NOT INT STO" (possibly LAOP 13); "BAC REC REQ" (BAC/BRC/RAC).
- Fig 3.2.6: left-margin label "I O RESPONSE" (cropped); "LAOP 03, 07'15" punctuation; "LOOP
  51"; bottom-left boxes "TBC AES OFF" / "TBC OCC INTLK" / "ADVANCE TBC" faint.
- Fig 3.2.7: "E. M" on the first timer output (bar over M not visible); "ON TO B".
- Fig 3.2.14: "LAOP 2? OR 55" (read 27); several long line destinations in the lower right.
- Fig 3.2.16: ALD of "RESET ABC AES" (38.81.03.1 vs 38.31.03.1); ALD under ""NO DELAY IND.
  TEST"" ("38.32[...]").
- Fig 3.2.17: "X1 35 75 48" (48 or 43).
- Fig 3.2.18: which "SIC BIN" hexagon belongs to which branch outcome; ALD of "RESET TBC AES"
  (38.01.03.1 vs 38.21.03.1); ALD of "RESET "I BOX HSCLN TIMER"" ("38.0?.07.1"); several
  cross-page lines.
- Fig 3.2.19: routing around the "51" hexagon to "RESET "LAAR BUSY"" / "SET ABC NOOP TAG";
  ALD 38.58.03.1 vs 38.53.03.1; legend entries "PX PSEUDO STORE" and "RAC RCY".
- Fig 3.2.21: left third speckled; ALD "35.21.01.[1]"; "RESET LAAR BUSY TRIG" printed with
  38.23.03.1 (elsewhere 38.53.03.1).
- Fig 3.2.22: left-column boxes faint ("SET "DISABLE INTRPT" TRIG", "SET I BOX RQST HSCLN"
  TRIG", "RESET "I BOX RQST HSCLN" TRIG"); ALD "38.03.10.1" under START I BOX HSCLN TIMER.
- Fig 3.2.25: "TBC ADVANCING TCC"; small tags 2D/2E/2F/2G.
- Fig 3.2.26: ALD of STO DATA TIMER (read "35.02.01.1"; Table 3.4.1 says 38.53.04.1); label
  "NO STORE MEM REQ".
- Fig 3.2.27: "RESET FROM TAG H2".
- Flow-line routing in general on Figs 3.2.14 and 3.2.16-3.2.19: box texts are reliable, long
  connections are best-effort. Re-check at >= 300 dpi before building on a specific path.
