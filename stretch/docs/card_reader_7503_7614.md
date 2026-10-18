# R23-9702 — IBM 7503 Card Reader / 7614 Card Reader Control, CE Manual of Instruction (1961)

Source: `docs/R23-9702_7503_Card_Rdr_7614_Rdr_Ctl_CE_1961.pdf`, 86 PDF pages,
scan with no text layer. Everything below was read visually from
pdftoppm renders (150 dpi for text, 300–1200 dpi crops for Figure 4.3-1).

Form number on the back cover (PDF 86): **R23-9702**. Preface (printed p.2):
"the IBM 7503 Card Reader and the IBM 7614 Card Reader Control of the 7030
System … based on the information available for the commercial 7030 System
as of October 17, 1960."

---

## 0. PAGE OFFSET — **PDF = printed + 0, end to end. No drift.**

`docs/archival_inventory.md` does not itself record an offset for this file;
`docs/exchange_and_io.md` line 22 does ("PDF = printed + 0 (PDF 5 renders
printed 5)"). Confirmed, and extended:

| PDF page | printed folio seen |
|---|---|
| 5 | 5 |
| 19 | 19 |
| 21 | 21 |
| 22 | (Figure 4.3-1, full-page figure, no folio) |
| 27 | 27 |
| 28 | (Figure 4.5-1, full-page figure, no folio) |
| 29 | 29 |
| 30 | 30 |
| 31 | 31 |
| 32 | 32 |
| 34 | (figures 5.1-1/5.1-2, no folio) |
| 36 | 36 |
| 37 | 37 |
| 48 | 48 |
| 62 | 62 |
| 64 | 64 |
| **84** | **84** ← last numbered text page (§9 Power Distribution Layout, which the TOC also puts at 84) |
| 85 | Figure 9-1 (fold-out schematic, no folio) |
| 86 | back cover (IBM colophon, "R23-9702", "Printed in U.S.A.") |

TOC on printed p.4 matches every section start I sampled (§4 = 19, §4.5 = 27,
§5.6 = 48, §6.4 = 62, §6.5 = 64, §9 = 84). The user's landmark holds: Figure
4.5-1 "Communication Lines" is on PDF 28. Note the figure page itself carries
no folio, so "printed p.28" for that figure is by position, not by a printed
number; the folio-bearing text pages on either side (27, 29) pin it exactly.

Roughly a third of the pages are full-page figures or photographs carrying
no folio (PDF 1, 3, 6, 22, 28, 34, 35, 85, 86 among those I rendered). They
are interleaved into the sequence without disturbing it: every folio I read
equalled its PDF page number, from 5 to 84.

---

## 1. HOW A CARD BECOMES WORDS

### The statement of the format

Printed p.21, §4.3 MACHINE LANGUAGE:

> "The data punched in the IBM card used with the 7030 System is in a binary
> form. Each card punch position is a possible data bit, with a punched hole
> representing the data bit. The card is capable of storing 960 bits (80 x 12)."

Printed p.19, §4.1:

> "A block of data (the data in one punched card) is transferred to the
> exchange in 120 eight-bit bytes with an associated parity bit for each
> data byte."

Printed p.19, §4.2: the three core buffers (check buffer A, check buffer B,
record buffer) "have a full data card capacity: 960 bits."

960 bits = 120 × 8 = 15 × 64. The "960-bit block = 15 words" recorded in
`docs/exchange_and_io.md` is therefore confirmed **for non-ECC mode**
(see §1(e) below for ECC mode, where it is *not* 15 words).

### (a) Bit order WITHIN one column — **12 first, 9 last**

Figure 4.3-1, "DATA BIT RELATION–CARD TO DATA WORD" (PDF p.22, between
printed 21 and 23). The figure draws an 80-column × 12-row card grid with
the first six columns filled in. Printed p.21 explains the notation:

> "Figure 4.3-1 shows the first six-card columns with the 72 data bit
> positions enumerated. The larger number represents the byte in which the
> data bit is sent to the exchange, and the small number represents the data
> bit position within each byte."

Transcribed at 600 dpi (large number = byte number 1–120, small number =
bit 0–7 within that byte). Card rows are printed down the left margin in the
order **12, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9** — i.e. physical top-to-bottom:

| card row | col 1 | col 2 | col 3 | col 4 | col 5 | col 6 |
|---|---|---|---|---|---|---|
| 12 | 1/0 | 2/4 | 4/0 | 5/4 | 7/0 | 8/4 |
| 11 | 1/1 | 2/5 | 4/1 | 5/5 | 7/1 | 8/5 |
| 0  | 1/2 | 2/6 | 4/2 | 5/6 | 7/2 | 8/6 |
| 1  | 1/3 | 2/7 | 4/3 | 5/7 | 7/3 | 8/7 |
| 2  | 1/4 | 3/0 | 4/4 | 6/0 | 7/4 | 9/0 |
| 3  | 1/5 | 3/1 | 4/5 | 6/1 | 7/5 | 9/1 |
| 4  | 1/6 | 3/2 | 4/6 | 6/2 | 7/6 | 9/2 |
| 5  | 1/7 | 3/3 | 4/7 | 6/3 | 7/7 | 9/3 |
| 6  | 2/0 | 3/4 | 5/0 | 6/4 | 8/0 | 9/4 |
| 7  | 2/1 | 3/5 | 5/1 | 6/5 | 8/1 | 9/5 |
| 8  | 2/2 | 3/6 | 5/2 | 6/6 | 8/2 | 9/6 |
| 9  | 2/3 | 3/7 | 5/3 | 6/7 | 8/3 | 9/7 |

Every cell was read at 600 dpi; the bottom row (card row 9) was re-cropped
separately to confirm col 1 = 2/3 and col 2 = 3/7. All 72 cells are legible
and the table is internally consistent (a strict run 1/0 … 9/7).

**Answer (a): the 12 row is first — IBM bit 0, the most significant bit of
the first byte. The order is 12, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, reading
straight down the card, with the 9 row last.** There is no reordering and no
zone/digit split in the transmitted data.

A column therefore straddles a byte boundary: column 1 supplies byte 1 bits
0–7 (rows 12,11,0,1,2,3,4,5) and byte 2 bits 0–3 (rows 6,7,8,9); column 2
supplies byte 2 bits 4–7 (rows 12,11,0,1) and byte 3 bits 0–7 (rows 2…9).
Two card columns = three bytes = 24 bits. Six card columns = nine bytes =
72 bits = one ECC-mode word (printed p.64: "six consecutive card columns
define one data word").

### (b) Order of COLUMNS within the 960 bits — **column 1 first**

From the same figure: card column 1 carries byte 1 (the first byte sent),
column 2 bytes 2–3, column 3 byte 4, … column 6 byte 9. Byte numbers ascend
monotonically with column number. There is no interleave, no
odd/even-column split, no reversal.

The hardware confirms it twice over:

- Printed p.36, §5.1.3: "Zone driver 1 and column driver 1 are turned on to
  read the first byte from the buffer. The functional operation to read out
  the second byte initiates a column driver advance and provides a column 2
  pulse … as the column drivers are advanced to column driver 12, the
  succeeding byte read-out operation will reset the column drivers to 1 and
  advance the zone drivers to 2. This operation continues until zone driver
  10 and column driver 12 coincide."
- Printed p.37 tabulates the resulting byte numbering (twelve "column"
  drivers × ten "zone" drivers = 120 byte positions; note these are
  *buffer read-out ring* names, not card columns and not card zone rows):

  | Zone | Column | Byte Number |
  |---|---|---|
  | 1 | 1–12 | 1–12 |
  | 2 | 1–12 | 13–24 |
  | 3 | 1–12 | 25–36 |
  | 4 | 1–12 | 37–48 |
  | 5 | 1–12 | 49–60 |
  | 6 | 1–12 | 61–72 |
  | 7 | 1–12 | 73–84 |
  | 8 | 1–12 | 85–96 |
  | 9 | 1–12 | 97–108 |
  | 10 | 1–12 | 108–120 |

  (The last row reads "108–120" in the original — an off-by-one typo in the
  manual; it must be 109–120. Verified at 150 dpi, the digits are clear.)

**Answer (b): card column 1 is first. Byte 1 = card column 1, rows 12…5;
byte 120 ends at card column 80, row 9. The transmission order is simply
column 1 → column 80, and within each column row 12 → row 9.**

Figure 4.3-1 only fills columns 1–6, so uniformity across all 80 columns
would be an inference from that figure alone — but two other statements pin
the far end of the card and close it:

- At 1.5 bytes per column, card column 79 must begin at byte
  1 + 78 × 1.5 = **118**.
- Printed p.37: zone 10 covers bytes 109–120, so the read-out combination
  (zone 10, column driver 10) is byte 108 + 10 = **118**.
- Printed p.64: ECC mode "conditions the turn-on of the early disconnect
  trigger at **column 10, zone 10** of buffer read-out (**card column 79**)."

p.37 and p.64 independently agree that byte 118 is the first byte of card
column 79, which is only true if the 1.5-bytes-per-column mapping holds
uniformly from column 1 to column 80. The ECC arithmetic agrees as well:
13 words × 6 columns = 78 columns exactly, 13 × 9 = 117 bytes, leaving
bytes 118–120 for the unused columns 79–80.

### (c) Read ROW BY ROW, buffered, transmitted COLUMN BY COLUMN

Printed p.21, the key sentence:

> "Although the card is read in rows (starting from the 9 row through the 12
> row), the data are transmitted in column to the exchange."

So the physical read is row-serial, 9 row first (card moves 9-edge-first),
and the column-order transmission is produced entirely by the core buffer's
read-in/read-out wiring. The mechanism (printed p.36, §5.1.2 / §5.1.3):

- **Read-in, 80 bits at a time.** "In essence, the buffer is an 80 x 12
  matrix and the coincidence of the vertical write current (brush winding)
  with the horizontal write current (row drivers) sets a particular core."
  Each of the 80 read brushes drives one brush winding (a vertical line);
  one of twelve **row drivers** is energised per card row, selecting the
  horizontal line. Twelve row pulses therefore load all 960 cores.
  Figure 4.5-1 shows the interface as "1st Read Brush (80)" and
  "2nd Read Brush (80)" — 80 wires per read station, confirming row-parallel
  / column-parallel sensing (printed p.30: "80 first-read and 80 second-read
  supply the read buffer with core write current during a card feed cycle").
- **Read-out, 8 bits at a time, in column order.** Printed p.36: "a unique
  read-out writing layout is required to transmit data from each buffer in
  eight bit bytes. The buffer read-out is controlled by ten zone drivers and
  twelve column drivers … 120 read-out combinations result."
- The row-driver → core-plane assignment is deliberately scrambled to make
  this work; printed p.36 gives the map and admits it:
  core plane 1←row driver 4, 2←8, 3←7, 4←6, 5←2, 6←12, 7←5, 8←9, 9←0 (sic —
  printed "0", presumably row driver 10), 10←1, 11←3, 12←11. "The apparent
  indiscriminate assignment of the row drivers to the core planes results
  from an expedient core array wiring format."
- Printed p.48, §5.6: "Twelve column and ten zone triggers … provide driver
  outputs that are combined to develop 120 read-out pulses."

**Answer (c): the card is read ROW BY ROW (80 bits per row, 9 row first,
through 12 row) into an 80 × 12 ferrite-core buffer; the buffer is then read
OUT in column order as 120 eight-bit bytes by a 12-way "column" ring crossed
with a 10-way "zone" ring. The transposition is done by the core-array
wiring, not by a shift register or a counter.**

Three buffers, all 960 bits: check buffer A, check buffer B (loaded from the
first read station), and the record buffer (loaded from the second read
station). On read-out both the record buffer and one check buffer are read
simultaneously and compared (printed p.19, p.21, p.37, p.62).

### (d) Byte size — **8-bit bytes, with a ninth parity line. Not 12.**

Printed p.19, §4.1:

> "Data bits are transmitted in groups of eight over eight parallel lines.
> One group of eight data bits is referred to as a byte of data. In
> addition, a ninth line, also parallel to the data bit lines, transmits a
> parity bit for data-checking purposes at the exchange."

Printed p.29: "Read: Eight lines transmit the data bytes to the exchange
during a read operation. Eight data bits are sent in parallel as a byte of
data." / "Read Parity: … Odd-parity checking is employed by all I-O devices
for data transmission."

**Answer (d): the 7614 presents a card as 120 eight-bit bytes + 120 odd
parity bits. The 12-bit column is NOT a unit on the interface — a column is
split across a byte boundary (1.5 bytes per column).** The "12-bit byte"
language in C28-6129 p.16 for STRAP's `(CC*)` mode is a *programmer's* view
of the 960-bit block, not a transfer unit on the channel; nothing in this CE
manual ever transmits 12 bits as a group.

This CE manual says nothing about the exchange's **byte weight** or **word
weight** for the reader (those come from the Reference Manual, as
`docs/exchange_and_io.md` §§ around line 1114 already records) — **not in
this manual**.

### (e) ECC mode — the one place "15 words" is wrong

Printed p.21 and printed p.64, §6.5:

> "When the cards are punched in ECC mode, six consecutive card columns
> define one data word. Nine eight-bit bytes are required to transfer this
> 72-bit data word. (The data word is composed of an eight-bit error
> checking and correction code and 64 data bits.) **The ECC card contains a
> maximum of 13 data words in card columns 1 to 78. Columns 79 and 80 are
> not used.**"

So: non-ECC card = 120 bytes = 15 × 64-bit words, exactly. ECC card = 13 ×
9 = 117 bytes of useful data in columns 1–78; columns 79–80 (3 bytes) are
discarded by an early disconnect — printed p.64: ECC mode "conditions the
turn-on of the early disconnect trigger at column 10, zone 10 of buffer
read-out (card column 79)".

The bottom band of Figure 4.3-1 ("DATA WORD") draws the 72 word-bit cells
with word data bit positions 0 … 63 left to right, preceded by eight ECC
cells; the NON ECC MODE row labels bytes 1–8 against data bits 0–7, 8–15,
…, 56–63, and the ECC MODE row labels byte 1 = the eight ECC bits and bytes
2–9 = data bits 0–63. The eight ECC cells are labelled (rotated, read at
1200 dpi) **C0, C1, C2, C4(?), C8(?), C16, C32, CT(?)** — the 4th, 5th and
8th labels are **unclear**; C0, C1, C2, C16 and C32 are legible.

---

## 2. THE CARD CODE — **NO. There is no card-code table in this manual.**

**Answer: no, and the manual says why.** Printed p.21, §4.3 MACHINE LANGUAGE:

> "The data punched in the IBM card used with the 7030 System is in a binary
> form. Each card punch position is a possible data bit, with a punched hole
> representing the data bit."

The 7503/7614 pair does **no character translation whatsoever**. It is a
pure binary, bit-per-punch-position column reader; a character→punch table
would be out of scope by design. Every table in the manual is a hardware
table (core plane ↔ row driver, zone/column ↔ byte number, control function
codes, timing pulse ↔ Systems page) — there is nothing resembling
"A = 12-1".

I scanned all 86 pages as 72-dpi contact sheets and then read, at full
resolution, every page that contained a table or a grid-like figure
(21, 22, 36, 37, 48, 52, 62, 64, 84). The only figure with a card-shaped
grid is Figure 4.3-1, and its cells hold byte/bit numbers, not characters.

**Consequence for the STRAP `(CC*)` question: the punch patterns are NOT
sourced from any 7030 document in this manual. They must come from the
general IBM card code.** (This CE manual does cite another manual for
mechanical maintenance — printed p.5: "IBM Customer Engineering Manual of
Instruction *88 Collator*, Form R25-4503 under the section titled Card
Feed" — but that is a card-feed mechanism reference, not a code table.)

---

## 3. THE CONTROL SIGNALS

### 3.1 Figure 4.5-1 "Communication Lines" (PDF p.28), Exchange ↔ 7614

**21 signal names** on the 7619 Exchange ↔ 7614 Card Reader Control
interface: 9 Exchange→7614 and 12 7614→Exchange. Names are given exactly as
lettered on the figure; where §4.5's prose uses a different wording, both
are given. Glosses are quoted from printed pp.27, 29, 30.

**Exchange → Card Reader Control** (§4.5.1, printed p.27–29) — 9 lines:

| Figure 4.5-1 name | §4.5.1 heading | Meaning |
|---|---|---|
| `Write (8)` | Write | "Eight write lines are used to send information to the reader control during a control operation … These lines feed an eight-bit byte to the line register." |
| `Write Parity` | Write Parity | "Permits a parity bit to accompany the eight bits transmitted … generated for odd parity data checking." |
| `Byte Response` | Byte Response | "Used to inform the reader control that the exchange has recognized and honored a service request … during a read operation, indicates that a byte of data has been accepted by the exchange and the successive byte may be transmitted." |
| `Read Instruction` | Read Instruction | "Initiates a read operation if the card reader is in a ready status and is not busy." |
| `Write Instruction` | Write Instruction | "Sends a write instruction signal to the reader control. However, a write instruction cannot be performed by the reader, and an exchange program check and an end-of-message are signalled to the exchange." |
| `Control Instruction` | Control Instruction | "Starts a control operation to perform some desired function at the card reader." |
| `Locate Instruction` | Locate Instruction | "Sends a locate signal to reader control. However, the locate operation cannot be performed … exchange program check and an end-of-message are signalled." |
| `Disconnect` | Disconnect | "Is initiated at the exchange when the end-of-message (EOM) trigger is turned on at the reader control. The disconnect line resets triggers in the reader control to divorce the card reader from the exchange control. The disconnect line may be activated from the exchange before the EOM trigger is turned on … defined as an early disconnect. This early disconnect blocks further data transfer … The reader control continues to read out the remaining data from the record buffer and a card feed cycle is initiated." |
| `-36 Volt` | −36 Volts | "Supplies −36v to the D level of the rotary deck switch on the CE test panel." |

**Card Reader Control → Exchange** (§4.5.2, printed p.29–30) — 12 lines:

| Figure 4.5-1 name | §4.5.2 heading | Meaning |
|---|---|---|
| `Read (8)` | Read | "Eight lines transmit the data bytes to the exchange during a read operation. Eight data bits are sent in parallel as a byte of data." |
| `Read Parity` | Read Parity | "Carries the parity bit sent with each data byte … Odd-parity checking is employed by all I-O devices for data transmission." |
| `Unit Check` | Unit Check | "Is the output of the unit check trigger in the reader control. It indicates that an uncorrectable data error has occurred in the current read operation. The Unit check status bit is set in the control word in the exchange at the end of the current block of data." |
| `Ready` | Ready | "Signifies that the card reader is loaded with cards and is in a status to accept a read or control instruction from the main program." |
| `Channel Signal` | Channel Signal | "Is active when the reader is initially placed in a ready status or when the signal key is depressed at the card reader. A channel signal status bit is set in the control word … may be interrogated by the program as a decision element." |
| `End Exception` | End Exception | "Is active when the card reader stacker is full or when the reader runs out of cards. The out-of-material light is illuminated at the card reader by an end exception condition. When the reader runs out of cards, the end exception indication is not given until the data of the last card have been transmitted …" |
| `Exch Prog Check` | **Exchange Program** (prose heading differs) | "Is activated when a write or locate instruction is programmed to the card reader, or when the control code during a control operation is invalid. An exchange program check status bit is set in the control word." |
| `Ecc` | Error Checking and Correcting (ECC) | "Is active when the reader control is in ECC mode." |
| `Eom` | End of Message | "Indicates that the current operation (read or control) is terminated and that the reader control is to be disconnected from the exchange channel. Any unusual condition which turns on the cancel trigger in the reader control will also initiate the end-of-message. The exchange responds with a disconnect signal …" |
| `Ser Req` | Service Request | "Indicates to the exchange that a byte of data is on line ready to be accepted during a data transfer (read) operation. During a control operation, this line signifies that the reader control is ready to accept control information." |
| `Cancel` | Cancel | "Indicates that an unusual condition is recognized at the card reader or control unit such as card feed failure or circuit failure." |
| `Block Channel` | Block Channel | "Carries a −36v back to the exchange to block the channel to which the reader control is connected while the CE test panel is in use." |

Context, printed p.27: "The reader control unit is connected to the exchange
by one of **32 possible exchange channels**."

### 3.2 Figure 4.5-1, 7614 ↔ 7503 (the machine-side interface)

**19 further names**, 8 toward the control and 11 toward the reader
(§4.5.3–§4.5.4, printed p.30–31). Listed for completeness; these are *not*
on the Exchange interface.

7503 → 7614 (8): `DC Ground`, `-48 Volt`, `Emitter (17) (Magnetic)`,
`Card Levers`, `Keys and Switches`, `Hayden Timer Delay`,
`1st Read Brush (80)`, `2nd Read Brush (80)`.

7614 → 7503 (11): `Hayden Timer Clutch`, `-12 V to Timer`,
`Card Feed Clutch`, `Ready`, `Start Motor HD 1`, `Stop Motor HD 2`,
`Feed Check Light`, `Out of Material`, `Reserved Light`, `Read Check`,
`Timer Bias`.

Figure-vs-prose name mismatches on this side: figure `Hayden Timer Delay` /
prose "Timer Delay"; figure `Hayden Timer Clutch` / prose "Time Clutch";
figure `-12 V to Timer` / prose "Time Clutch −12v"; figure `Ready` /
prose "Ready Light"; figure `Reserved Light` / prose "reserve light"
(the control-code table on printed p.62 spells it "Reserve light");
figure's four separate light lines (`Feed Check Light`, `Out of Material`,
`Reserved Light`, `Read Check`) are glossed collectively as "Panel Lights"
in the prose. `Ready` appears on both interfaces — they are different wires
(one a status line to the exchange, one a lamp line to the reader), so the
counts 21 and 19 do not double-count.

Prose detail, printed p.30: `Magnetic Emitter (17)` — "From each of the
magnetic emitter pick-up heads; supply the magnetic emitter pulses to the
reader control during a card feed cycle." `Card Lever` — "Permit the reader
control unit to sense the condition of the hopper contact, card lever 1,
card lever 2, and the stacker contact." `Keys and Switches` — "stacker
switch, unload key, start key, stop key, signal key, motor switch off or
on."

### 3.3 The control function codes (printed p.62, §6.4)

The one code table in the manual. "The control instruction executed by the
reader control permits any of five functions to be performed at the card
reader … only one eight-bit byte is required to define a control function."

| Name | bit 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | Write Parity Tgr | (octal) |
|---|---|---|---|---|---|---|---|---|---|---|
| Reserve light Off | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 016 |
| Reserve light On | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 017 |
| ECC mode On | 0 | 0 | 1 | 0 | 1 | 1 | 1 | 1 | 0 | 057 |
| ECC mode Off | 0 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 157 |
| Read check light On | 0 | 1 | 0 | 0 | 1 | 1 | 1 | 0 | 1 | 116 |

The transcription is self-checking: counting the ones in each row and adding
the Write Parity Tgr bit gives 3+0, 4+1, 5+0, 6+1, 4+1 — odd in every case,
which is exactly what p.64's "provided with a parity bit (if the function
code is even)" requires. That validates both the bit patterns and the parity
column.

(The octal column is mine, not the manual's. It reproduces exactly the five
codes `docs/exchange_and_io.md` already records from Reference Manual
p.139 — 016, 017, 057, 116, 157 — so the CE manual independently confirms
that list and additionally gives the bit patterns and the expected parity.)

"The reserve light on or off permits the programmer to signal that the card
reader is reserved (or not reserved) during a program run. The ECC mode On
or Off permits the programmer to alter from non-ECC mode to ECC mode and
back again when required. The read check light is a control function used to
indicate that a data error has occurred."

Printed p.64: "This function code is provided with a parity bit (if the
function code is even) and is checked at the reader control unit parity
circuit." Printed p.31/p.32: "when a control operation is in progress …
the function codes are examined for a valid bit structure. An invalid
control function code turns on the program check latch."

Five basic instructions apply to I-O devices (printed p.31): **RD, WR, LOC,
CTL, REL**. The reader can execute only RD and CTL.

### 3.4 Status and error conditions, and how each is signalled

*Provenance note: in the table below, the section/page pointers in
parentheses (§7.1, p.72 and the like) are taken from the contents list on
printed p.4 — I did not render §7's own pages. Every quoted sentence is
from a page I rendered and read: §4.7 on printed pp.31–32, §4.5 on pp.29–30,
§6.4 on p.62, §6.5 on p.64. §4.7 is a summary of §7 written by the same
manual, and it already covers every condition asked about.*

§4.7 CHECKING CIRCUITS (printed p.31–32) — "Five check circuits survey the
machine operation":

| Check | What it catches (printed p.31–32) | Signalled as |
|---|---|---|
| **Unit Check** (§7.1, p.72) | "ensures the validity of the data entering or leaving the reader control unit. During a control instruction operation, the control code … is parity-checked. Similarly, during a read operation the transmitted data are checked in a compare circuit" (record buffer vs check buffer). In ECC mode, "the unit check is turned on if two bit errors are detected within one word (72 bits)." | `Unit Check` line → Unit check status bit in the exchange control word, set "at the end of the current block of data". Does **not** interrupt data transmission. |
| **Driver Check** (§7.3, p.74) | "an operational check of the core buffer read-in and read-out drivers. The row core drivers, the column core drivers, the zone core drivers, and the pulse power supply … If (during a read-out operation) a check cone is not sensed, the driver check is indicated." | → cancel → `Cancel` + `Eom` → exchange returns `Disconnect`. |
| **Ring Check** (§7.2, p.74) | "verifies that the carry operation and the byte counter coincide at the 120th byte … An error is indicated if the byte counter is less than 120 when the carry signal is generated." | → cancel → `Cancel` + `Eom`. |
| **Feed Check** (§7.4, p.76) | "made during a card feed cycle. This check examines the card levers during the feed cycle to ensure satisfactory card operation." | → cancel → `Cancel` + `Eom`; **Feed Check light** at the reader. |
| **Program Check** (§7.5, p.76) | "monitors the program instructions directed to the card reader. Should a write or locate instruction be addressed to a card reader exchange channel, the program check latch is turned on … when a control operation is in progress … the function codes are examined for a valid bit structure. An invalid control function code turns on the program check latch." | `Exch Prog Check` line → **EPGK** indicator at the exchange; "the card reader operation is never started. The EPGK check indicator has the highest interrupt priority of the I-O check indicators." |

"Either driver check, ring check, or feed check initiate a cancel operation.
Should an error condition be detected by these checks, the cancel signal
turns on the end-of-message (EOM) trigger. The exchange responds with a
disconnect signal to terminate the operation immediately." (printed p.32)

Other conditions:

| Condition | How signalled |
|---|---|
| **Hopper empty / out of material** | `End Exception` to the exchange → End exception status bit in the control word; **Out-of-material light** at the reader. "When the reader runs out of cards, the end exception indication is not given until the data of the last card have been transmitted to the exchange." (p.29) §6.7 Out-of-Material Operation is printed p.66. |
| **Stacker full** | Same `End Exception` line — "Is active when the card reader stacker is full **or** when the reader runs out of cards" (p.29). Sensed by the stacker stop switch (p.5). |
| **Not ready** | `Ready` line inactive. A `Read Instruction` only starts an operation "if the card reader is in a ready status and is not busy" (p.27). |
| **Became ready / operator attention** | `Channel Signal` — "active when the reader is initially placed in a ready status or when the signal key is depressed at the card reader" (p.29). |
| **Read check (data error)** | `Unit Check` to the exchange; **Read Check light** at the reader, which is lit *by the program* via the "Read check light On" control code (116), not automatically (p.62). |
| **Feed failure / circuit failure** | `Cancel` — "an unusual condition is recognized at the card reader or control unit such as card feed failure or circuit failure" (p.30). |
| **Validity / double-punch error** | **Not in this manual.** No validity check, no double-punch/blank-column check exists in the 7503/7614 — consistent with §4.3's statement that every punch position is simply a data bit. The only data check is the first-brush-vs-second-brush compare (record buffer vs check buffer), plus ECC when enabled. |

Card-progress sensing, printed p.5 — five strap-type contacts used as card
levers: hopper contact (cards present in hopper), first card lever contact
(card at first read station), second card lever contact (card at second read
station), stacker card lever contact (card in the feed rolls), stacker stop
switch (full stacker).

Reader controls, printed p.16 (§3.4 Lights, Keys and Switches, read from the
contact sheet only — **not verified at full resolution**): Master Switch,
Power-On Switch, Power-Off Switch, Motor Switch, Start Key, Stop Key, Unload
Key, Signal Key; lights Power-On, Ready, Out of Material, Feed Check, Read
Check, Reserve.

---

## 4. Things this manual does NOT contain (asked, and answered "no")

- A character-to-punch-combination card code table — **not in this manual**
  (see §2 above; the manual affirmatively says the data are binary,
  bit-per-punch-position).
- Byte weight / word weight for the card reader on the exchange —
  **not in this manual**.
- Any validity, double-punch or blank-column check — **not in this manual**.
- The exchange-side control-word bit layout (which bit is "unit check",
  etc.) — the manual names the status bits but **does not number them**.

## 5. Unclear readings

- Figure 4.3-1, DATA WORD band, the eight ECC-bit cell labels: best reading
  **C0, C1, C2, C4, C8, C16, C32, CT**; the 4th, 5th and 8th are **unclear**
  even at 1200 dpi (hand-lettered and rotated 90°). C0, C1, C2, C16, C32
  are certain.
- Printed p.36 core-plane table, core plane 9 → row driver printed as
  **"0"**; with twelve row drivers and the other eleven accounted for
  (1,2,3,4,5,6,7,8,9,11,12) this must be **10**, but the printed glyph is a
  single "0". Reported as printed.
- Printed p.37 zone/byte table, zone 10 → "**108**–120"; must be 109–120.
  Reported as printed.
- Printed p.16 switch/light list was read from a 72-dpi contact sheet only.
