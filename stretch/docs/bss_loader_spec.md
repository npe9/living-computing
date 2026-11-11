# The MCP loader and the BSS processor: a specification from the documents

Reconstruction-plan rows M-5 and L-1; road step E4 of
`programming_environment.md`. Nothing here is implemented. IBM's BSS
code is lost. This file fixes what the documents and the listing say,
marks what they do not say as **UNSPECIFIED**, and does not fill it in.

## 0. The short answer

**What MCP's listing holds.** The March 1963 listing holds the MCP
*loader* and the *resume load* program that drives it: type area
22LOADER, printed pp.320-334, with its data block on p.291. It takes
**15** card classes, not 18. Printed p.329 is missing from the scan.

**What it does not hold.** It holds no BSS processor, no link program,
no node table, and no code for K, A or Z cards. Its only BSS content
is the receiving side: it reads relocation tables that BSS has left in
storage.

**What this means for E4.** A first job does not need BSS. C22-6678-1
p.13 defines a non-BSS deck (JOB, TYPE GO, LIM, IOD, binary cards,
branch card), and origin, flow and branch cards run through code that
is transcribed. Section 7 lists what needs p.329.

**Is p.329 needed?** Only by P cards, by D cards (they share its
routine), by hex digits A-F, and by C cards that are continuations,
have ignored fields, or hold fewer than four half-words.

## 1. Sources and page offsets

"Printed p.N" is used throughout. Offsets were established by reading
page images.

| document | short name | PDF page vs printed page | evidence |
|---|---|---|---|
| C28-6379-0, Loader and BSS Processor | **C28** | PDF = printed | PDF 3 prints "3"; PDF 22 prints "22" |
| C22-6678-1, MCP Reference, June 1964 | **6678-1** | PDF = printed | PDF 13 prints "13"; PDF 53 prints "53" |
| C22-6728, MCP Systems Analysis Guide (base) | **6728-0** | PDF = printed | PDF 81 prints "81"; PDF 195 prints "195" |
| C22-6728-1, same, next edition | **6728-1** | PDF = printed | PDF 89 prints "89" |
| C22-6729, STRAP II Analysis Guide | **6729** | PDF = printed | PDF 183 prints "183" |
| C22-6751, FORTRAN IV, May 1963 | **6751** | PDF = printed | PDF 30 prints "30"; PDF 35 prints "35" |
| C28-6129, STRAP II | **6129** | printed = PDF − 4 | PDF 26 prints "22"; PDF 27 prints "23" |
| N22-0085, MCP update, May 1963 | **N22** | PDF n = "Page n of 12" | PDF 3, PDF 11 |
| MCP listing, volume 2 | **L** | printed = PDF + 249 to p.328; PDF + 250 from p.330 | deck headers p.320 (PDF 71), p.330 (PDF 80) |

**How the listing was read.** The listing was read from
`decks/mcp_bootstrap_p*.strap`, the transcriptions whose code columns
are checked against the print, not from fresh page images. Comments
quoted from the listing are the programmers' own. `L p.331 l.24` means
printed p.331, line 24. Readings of what the code does are mine, and
**no loader path has been run for this file**. Mark them "as read" and
test them when the loader first runs.

**The card-bit convention.** A card is 80 columns of 12 bits, column
major, in the 15-word buffer `YBCBU` (L p.274 l.19), called `ALDBF` by
the loader (L p.291 l.33). Column c, row r (0-11) is bit
`12(c−1)+r` of the buffer. The notation `c.r` is IBM's: "the first
number specifies the card column ... the second ... the row number ...
the row nearest the top of the card is row 0 and the row nearest the
bottom ... is row 11" (6129 p.22). The print's named rows map as
1.0=12, 1.1=11, 1.2=0, 1.3=1, ... 1.11=9: N22 p.3 gives the O punch as
(1.1, 1.8), which C28 p.4 gives as (11,6).

## 2. The two programs

"The IBM 7030 system loader consists of two programs: (1) the resume
load program of MCP, with the loader as a subroutine, and (2) the
Binary and Symbolic Subroutine (BSS) processor" (C28 p.3).

- **Non-FORTRAN environment.** BSS is not involved. Control goes
  straight to resume load, and storage for relocatable subprograms is
  set by control cards (C28 p.3).
- **FORTRAN environment.** BSS runs first as "a preprocessor to the
  MCP loader", assigns storage, fetches library routines, computes
  cross references, then gives control to resume load (C28 pp.3, 7).
- **BSS's two call forms.** BSS is the last link of the FORTRAN chain,
  or a single processor called by `B TYPE,GO,FORTRAN` (C28 p.7). The
  listing shows the second: job control rewrites a GO job's chain name
  FORTRAN into `BSS` ("INTERPRET GO, AS CMPILGO,.. AND FORTRAN AS BSS",
  L p.271 ll.43-50).
- **Author of the segmentation part.** The Naval Weapons Laboratory,
  Dahlgren (C28 p.2).

## 3. Card classes

Column 1 punches, from C28 p.4 and 6678-1 pp.13-14 (identical), with
the listing's table (`ATBL`, L p.331 ll.24-38, searched by `ATXW1
XW,ATBL,15,0`, l.49) alongside. The octal is the 12-bit column, 12-row
first.

| # | card | column 1 | `ATBL` octal | L entry (p.320 `ATYPE`) | 6728-0 p.81 | 6728-1 p.89 | N22 p.3 |
|---|---|---|---|---|---|---|---|
| 1 | Absolute origin | 7,8,9 | 0007 | p.321 l.1 `AXWORG` | yes | yes | not listed as new |
| 2 | Absolute flow | 7,9 | 0005 | `AFLOW` | yes | yes | not listed as new |
| 3 | Absolute branch | 6,7,9 | 0015 | `ABCARD` | yes | yes | not listed as new |
| 4 | Absolute correction (C) | 12,3 | 4100 | `AOCTAL` | yes | yes | not listed as new |
| 5 | Absolute patch (P) | 11,7 | 2004 | `APCARD` | yes | yes | not listed as new |
| 6 | Absolute dump (D) | 12,4 | 4040 | `ADCARD` | yes | yes | not listed as new |
| 7 | Relocatable data | 6,7,8,9 | 0017 | `AXRDAT`, `ARBDCD` | yes | yes | new |
| 8 | Relocatable instruction | 5,7,9 | 0025 | `AXWBIN`, `ARBNCD` | yes | yes | new |
| 9 | FORTRAN program | 5,6,7,9 | 0035 | `AFPCRD` | yes | yes | new |
| 10 | Common definition | 5,7,8,9 | 0027 | `AFPCRD` | yes | yes | new |
| 11 | FORTRAN branch | 5,6,7,8,9 | 0037 | `AFPCRD` | yes | yes | new |
| 12 | **Relocatable correction (K)** | 11,2 | **absent** | **none** | **no** | yes | no |
| 13 | **Relocatable patch (A)** | 12,1 | **absent** | **none** | **no** | yes | no |
| 14 | **Relocatable dump (Z)** | 0,9 | **absent** | **none** | **no** | yes | no |
| 15 | T | 0,3 | 1100 | `ATCARD` | yes | yes | not listed as new |
| 16 | Super T | 0,2,3 | 1300 | `ASUPRT` | yes | yes | not listed as new |
| 17 | Loader adjustment (O) | 11,6 | 2010 | `ALDADJ` | yes | yes | new |
| 18 | B | 12,2 | 4200 | `ANORMR` (ignored) | yes | yes | not listed as new |

**M-5 answered.** `ATBL` has 15 entries and `ATXW1` counts 15. K, A
and Z are not in it, and their codes (2200, 4400, 1001) occur in no
loader page. So a K, A or Z card takes `B,AERR3`, "ILLEGAL TYPE OF
CARD" (L p.322 l.34), in the March 1963 MCP. The listing is the loader
of 6728-0 (15 classes, `A...` labels), not of 6728-1 (18 classes,
`M...` labels such as `MLOADR`, `MKCARD`, `MZCARD`). None of those M
labels occurs in any deck.

Which list applies:

| source | date | classes |
|---|---|---|
| C22-6678-0, as quoted by N22 p.11 ("eight") | before May 1963 | 8 (edition not held) |
| N22 pp.3, 11 | May 1963 | 14 = 8 + 6 |
| L (`ATBL`); 6728-0 p.81 | March 1963 listing | 15 |
| C28 p.4; 6678-1 p.13; 6728-1 p.89 | 1964 | 18 |

N22's 14 is later in date than the listing's 15. See gap G1.

## 4. Card formats

### 4.1 Common fields

| columns | field | source |
|---|---|---|
| 1 | class punches | C28 p.4 |
| 2 | ID. "12 bits of the 36-bit 7030 time clock"; "Column 2 will be ignored by the loader" | 6129 p.22 |
| 3 | sequence number, 12-bit binary; first card 1, second 2 | 6129 p.22; L p.321 l.22 (`ALDBF.24`) |
| 4 | check sum, 12 bits; blank means not used | 6728-0 p.80; L p.322 ll.48-49 |
| 73-80 | identification, ignored by the loader | 6129 pp.22-23; C28 p.22 |

Listing support for column 2: a grep of every `ALDBF` reference in the
decks finds `.14` (the octal scan start, not column 2 as a field),
`.24`, `.36`, `.48`, `.49`, `.52`, `.60`, `.96`, `.108`, `.116`,
`.120`, `+13.32`, and no `.12`.

### 4.2 Absolute origin, column 1 = 7,8,9

C28 p.18; 6129 p.22. The bit-level form is 6129's; C28's diagram only
labels the columns.

| columns | field |
|---|---|
| 5.0 | 0 skip, 1 zero |
| 5.1 | 0 before loading, 1 after |
| 5.2-5.11 | primary bit count, 10 bits |
| 6-7 | origin, 24 bits (bit address) |
| 8-9 | secondary bit count, 24 bits: bits to skip or zero |
| 10.0-10.7 | not used |
| 10.8-71.11 | up to 736 information bits (23 half-words) |

Listing: `AXWORG XW,ALDBF.116` (L p.331 l.47) = 10.8. Control bits
tested at `ALDBF.48`, `.49` (L p.321 ll.29-30).

### 4.3 Absolute flow, column 1 = 7,9

C28 p.18; 6129 p.23. Columns 5.0-5.3 not used; **5.4-71.11 exactly 25
half-words** (800 bits). "All columns ... must be used. No primary bit
count is provided for." Loads immediately after the highest location
of the previous origin or flow card (C28 p.4). Listing: `AXWFLW
XW,ALDBF.52,12` is 12 full words, plus a 32-bit partial (`LFI(BU,6),
(8)400000.,48`), L p.323 ll.42-43.

### 4.4 Absolute branch, column 1 = 6,7,9

C28 p.18: column 5 unused, **columns 6-7 branch address**, columns
8-72 unused. Listing: `LF(BU,24),ALDBF.60`, L p.323 l.26. See C4 for
6129's different form.

### 4.5 Relocatable instruction, column 1 = 5,7,9

C28 p.19; 6729 p.188; 6751 p.33.

| columns | field |
|---|---|
| 5 | bit count of instructions, "excluding the relocation bits" (6729 p.188). Listing takes 10 bits (`SF(BU,10),$7.14,24`, L p.324 l.40) |
| 6-7 | origin relative to the subprogram |
| 8 | unused |
| 9.0-71.11 | instructions, then immediately the relocation bits (6729 p.188) |

"XW's, CF's, and RF's only (i.e., no DD's or DR's)" (6729 p.188).
Listing: `AXWBIN XW,ALDBF.96` = 9.0. The location of the relocation
bits is the start plus the bit count (L p.324 ll.41, 53).

Relocation bits, one set per half-word (C28 p.19; 6729 p.188; 6751
p.33). The dot notation in all three is not bit-for-bit, so the bit
positions below are from the code (L p.325 ll.5-33), as read:

| bits | meaning | width |
|---|---|---|
| `0` | no relocation | 1 |
| `1 x a 0` | a=0 first 18 bits (address), a=1 last 18 (refill); as lower address, relative to the subprogram origin | 4 |
| `1 x a 1 0` | same selection, as upper address, blank common | 5 |
| `1 x a 1 1 i` | same selection, as upper address, named common i | 5 + w |

- `x` is "reserved for later definition" (6729 p.188, an arrow to the
  second bit). The code does not test it.
- w is the width of i: `19 − LZC` of the 19-bit count of named commons
  (L p.324 ll.20-23), that is, the bit length of the count. 6751 p.33
  and C28 p.19: "length of i sub-field is determined by number of named
  commons". 6728-0 p.85 disagrees: see C2.
- Relocating adds 18 bits only: `+(BU,18),$2,14` left, `+(BU,18),$2`
  right (L p.325 ll.11, 16).
- A remainder of under 32 bits is relocated and loaded by `ARBCD7`,
  with a computed offset (L p.325 ll.43-53), so its left 18 bits are
  the leftmost of the partial field.

### 4.6 Relocatable data, column 1 = 6,7,8,9

C28 p.19; 6729 p.187; 6751 p.33.

| columns | field |
|---|---|
| 5.0, 5.1 | as origin card |
| 5.2-5.11 | bit count, 10 bits |
| 6-7 | origin relative to the loading base |
| 8-9 | secondary bit count, 24 bits (see C3) |
| 10 | loading base: 0 program data, 1 first named common, 2 second, ... |
| 11.0-71.11 (6729) or 11-72 (C28, 6751) | data. See C5 |

No relocation bits. Listing: `ARBDCD`, L p.326 ll.16-35, `AXRDAT
XW,ALDBF.120` = 11.0.

### 4.7 FORTRAN program, column 1 = 5,6,7,9

C28 p.18; 6729 p.188; 6751 p.33.

| columns | field |
|---|---|
| 5 | not used |
| 6.0-7.5 | program size, 18 bits |
| 7.6-8.11 | blank common size, 18 bits |
| 9.0-14.3 | first entry name, A8, 64 bits |
| 14.4-15.10 | entry address, 19 bits |
| 15.11 | not used |
| 16.0-22.11 | second entry, same pattern |
| ... to 65.0-71.11 | up to nine entries per card |

"Columns 6, 7, and 8 are blank on any subsequent continuation program
cards" (C28 p.18). Size: computed at assembly if STRAP generates the
card, all 1's if FORTRAN does (C28 p.7). An entry without a name gets
eight A8 blanks (6729 p.186). Produced by `PUNFPC,S,C` and `ENTER`
(6729 pp.183, 186; 6751 p.30). S is the number of full words, "the
highest location relative to zero used, plus 1"; C is full words of
blank common (6751 p.31).

### 4.8 Common definition, column 1 = 5,7,8,9

C28 p.19; 6729 p.187; 6751 p.33. Columns 5-8 not used; 9.0-14.3 A8
name; 14.4-15.9 size, 18 bits; 15.10-15.11 not used; 16.0-22.11 the
same; up to nine names per card, ending at 71.11; more cards in the
same format. Produced by `PUNCDC`, `COMBLOCK` (6729 p.186; 6751 p.31).
"It is vital that the original ordering of these cards ... be
preserved" (6751 p.30): the order numbers the commons.

### 4.9 FORTRAN branch, column 1 = 5,6,7,8,9

C28 p.19 and 6751 p.34: column 5 labelled BIT COUNT, 6-72 unused. 6729
p.187: "5.0-71.11 Not used". Produced by `FEND` (6729 p.183). The
loader takes no field from it (L p.324 l.12).

### 4.10 Octal cards: C, P, D

C28 p.21. Hollerith, not column binary.

| columns | C and P | D |
|---|---|---|
| 1 | C or P | D |
| 2-9 | origin, `xxxxxx.x` octal; blank means continuation | same |
| 10-11 | blank | blank |
| 12-23 | first half-word | lower limit |
| 24-27 | blank | blank |
| 28-39 | second half-word | upper limit |
| 40-43 | blank | blank |
| 44-55 | third half-word | format |
| 56-59 | blank | blank |
| 60-71 | fourth half-word | lower limit of second request |
| 72 | as drawn, unlabelled | as drawn, unlabelled |

- Half-word form: `xxxxxx.xx HH` (C28 p.21). Listing: 6 octal, point,
  2 octal, 1 column skipped, 2 hex (L p.328 ll.17-31), stride 16
  columns (two `AOPT24`, ll.16, 34).
- Decimal point: 12,3,8 (`(8)4102`, L p.327 l.46). A 1 punch added in
  the point column means ignore (`$R+.55`, l.47), for the whole card in
  the origin field, for one half-word in a half-word field. The loading
  address still steps, except for the last half-word on the card (C28
  p.4). C cards only: "IF P CARD DONT TEST FOR 1" (L p.327 l.45).
- Digit decoding: rows 0-7 for octal (`CT0011(BU,8)` from `.14`), rows
  0-9 for hex (`CT0011(BU,10)`), the value being the leading-zero
  count; blank is zero (L p.327 l.49; L p.328 ll.26-27, 41-44).
- A 12 punch on a hex digit goes to `AOCTH1` (L p.328 l.29), which is on
  p.329. A-F decoding is lost with that page.

Dump formats (C28 p.21): 0.0 / 0.40 octal-hex with / without panel;
1.0 / 1.40 floating point; 2.0 / 2.40 index word; 17.0 / 17.40 octal-hex
no mnemonics. Bit 24 of the format half-word: 0 no more requests, 1
more follow. A second request starts with its lower limit in column 60
and continues with upper limit and format in column 12 of a next D card
with columns 2-11 blank (C28 p.21).

### 4.11 Relocatable octal cards: K, A, Z (not in the listing)

C28 p.20. Column 1 K, A or Z.

| columns | field |
|---|---|
| 2-9 | origin `xxxxxx.x` octal |
| 10-11 | relocation of the origin: 00 subprogram, xx named common number, two-digit octal |
| 12-23 | first half-word or dump parameter |
| 24-27 | relocation of first |
| 28-39 | second |
| 40-43 | relocation of second |
| 44-55 | third |
| 56-59 | relocation of third |
| 60-72 | unused |

Relocation columns: `----` none; `P---` subprogram origin; `C---` common
origin; `P0--`, `P1--` left or right 18 bits relative to subprogram;
`C0--`, `C1--` left or right relative to common; `C0xx`, `C1xx` named
common xx, 00 meaning blank (C28 p.20). "Blanks in significant columns
will be considered to be 0's." The named-common number must be right
justified. Continuation: columns 2-11 blank. Named commons are numbered
in the order they appear within the subprogram. `P---` and `C---`
leave which 18 bits **UNSPECIFIED**.

### 4.12 Loader adjustment (O)

C28 p.21: column 1 O, columns 2-9 origin `xxxxxx.x` octal, 10-72 unused.
6729 p.188 calls it the "Special Origin Card", `xxxxxx.0` octal, "the
full word location". Listing reads 6 digits, 18 bits (`AOXW1 XW,ALDBF
.14,6`, `SF(BU,18),$3,46`; L p.323 l.46, L p.324 l.3). Produced by
`ORIGIN,N` (6729 p.183).

### 4.13 T, Super T, B

- **T**, column 1 T (0,3). Significant forms (C28 p.20):
  - **NODE**: columns 10-19 `NODE,XX,YY`. XX is this segment's two-digit
    number, YY the segment it attaches to, 00 for the primary.
  - **DEFINE**: columns 10-14 `DEF,C` with `COMNAM1,COMNAM2` following.
  - **DEFINE IMMEDIATE**: columns 10-14 `DEFI,` then the same.
  - All others: "columns 2-72 used for anything".
- **Super T**: S and T multi-punched in column 1; printed as ST; columns
  2-72 ignored (C28 p.20).
- **B**: control cards (JOB, TYPE, LIM, IOD, REEL). The loader ignores
  them (C28 p.6). BSS reacts to IOD and REEL only (C28 p.9).
- **SUBTYPE**: T card, columns 10 on, `SUBTYPE, deck description, list
  option, punch option` (6751 p.28). A FORTRAN-chain matter, not read by
  the loader.

### 4.14 Deck order

Within a subprogram, BSS requires "a rigid ordering" (C28 p.7): A, one
or more FORTRAN program cards; B, one or more common definition cards
(none unless common is defined); C, O card if present; D, one relocatable
instruction card with an index word whose count is the transfer-vector
length; E, one or more relocatable data cards holding the transfer vector
in A8; F, the subprogram (relocatable or absolute); G, correction, patch
or dump cards.

- If the count is zero, no transfer-vector data card is expected.
- K, A and Z apply only to the subprogram they follow, and may be
  intermixed, but "K cards should precede those A or Z cards at the same
  location".
- Continuations must immediately follow what they continue.
- A last FORTRAN branch card ends the deck; "The job may not be run in
  the absence of such a card" (C28 p.9).
- Every absolute subprogram must contain an O card or a T card to reset
  the sequence counter (C28 p.8).
- Data after a GO job is separated by a FORTRAN branch card (6751 p.29).

## 5. The MCP loader's algorithm

### 5.1 Calling sequence

6728-0 p.80 (`ALOADR`), 6728-1 p.88 (`MLOADR`); listing L p.332 ll.42-52:

```
LVI,$15,$+1.0 ; B,ALOADR
,FWA          first word (18-bit) address of the card
,L            lower limit; XF=1 means new job, initialize
,U            upper limit (protected); XF=1 means reset the
              sequence counter from column 3 of the first binary card
(error return)
VF,D          bits 0-11 sequence number of the card, or 0 for an
              octal card; bits 13-17 error code
(branch return)
VF,A          half-word branch address
(normal return)
```

"The loader does not save or restore index registers" (6728-0 p.80).

### 5.2 Per-card flow

From L pp.320-331; charts 6728-0 pp.83-86 (Figures 40-42).

1. New job, `.57($15)` set: clear indicators `ALL`; set `ATCRDI` if
   `.89($15)` set; store bounds; zero `ALDCTR`, `ASEQID`, `AHIWD` (L
   p.320 ll.11-21).
2. Compare column 1 with `ATBL`, branch through `ATYPE`. No match:
   error 3 (L p.322 ll.29-36).
3. By class:

| class | action | L |
|---|---|---|
| Origin | test origin in bounds; test last location in bounds; save first origin (`ALL.3`) as the default branch address; sequence; check sum; skip or zero first if `5.1`=0; load 64-bit words, then a partial word; skip or zero after if `5.1`=1 | p.321, p.322 ll.1-27 |
| Flow | error 8 if no origin saved; start at `ALDCTR`; then as origin, no skip or zero | p.323 ll.39-44 |
| Branch | in a BSS deck go to the card counter; else sequence, check sum; address nonzero: bounds, store as branch address; zero: error 8 if no origin saved; branch return | p.323 ll.20-37 |
| T | set `ATCRDI`: the next card's column 3 becomes the counter | p.323 ll.14-15 |
| Super T | set `ASTCRD`: no further sequence check | p.323 ll.17-18 |
| B | normal return | p.320 l.27 |
| O | BSS: ignored; else 6 octal digits, bounds, store in `ALDCTR`; also the default branch address if none saved | p.323 l.45 to p.324 l.11 |
| Relocatable instruction | check sum only; base `ALDCTR`, error 8 if zero; bounds; relocate and load half-words; relocate and load the remainder | p.324 ll.30-56, p.325, p.326 ll.1-14 |
| Relocatable data | base 0 uses `ALDCTR`, error 8 if zero; other bases error 4 if not BSS, else from the relocation table; sets `ALL.3`, `ATCRDI`, `ARBCDI`; enters origin path at `ALD8` | p.326 ll.16-35 |
| FORTRAN program, common def, FORTRAN branch | see 5.4 | p.324 ll.12-29 |
| C | set up; `AOCTLA`; origin, half-words | p.327 l.32 on, p.328 |
| P | `APCARD`. Opening on p.329, tail on p.330 | p.330 ll.1-19 |
| D | `ADCARD`: error 5 if `AHIWD`=0; dump calling sequence | p.330 ll.20-39 |

### 5.3 Check and sequence tests

**Sequence** (as read, L p.322 ll.38-46). If `ATCRDI` is on, clear it
and store column 3 as the counter. If `ASTCRD` is on, no test.
Otherwise column 3 less 1 must equal the counter, else error 2; the
counter then steps. Relocatable instruction cards take no sequence test
(`ARBNCD` calls only `ACHSM`, L p.324 ll.30-31), and relocatable data
cards set `ATCRDI` and so store column 3 without testing. This agrees
with "The sequence number on relocatable cards is not checked" (6728-0
p.80).

**Check sum.** C28, 6728-0, 6728-1 and 6729 name it and give no
algorithm in the pages read. As read in `ACHSM` (L p.322 l.48 to p.323
l.13):

- blank column 4: no check;
- add the 12-bit columns 1, 2, 3, then 5 through 71 (`ACXW3 XW,ALDBF,2`
  chained to `ACXW3A XW,ALDBF.48,67`);
- fold: low 12 bits + high 12 bits + the carry of that addition;
- compare with column 4, error 1 on mismatch.

Two things here need proof by execution. First, the chain continues
past column 3 only if `BXF` sees the first XW's flag at the moment of
refill: `ACXW3` carries flag `100`, `ACXW3A` `000`, and the listing's
remark says "SETS XF". Second, column 72 is outside the sum (see C5).

### 5.4 Relocation and the table the loader reads

**First FORTRAN program card** (`AFPCRD`, L p.324 ll.12-29). If
`KSILO+2.` does not hold `BSS`, error 4. Set `AFPCI`. The table is at
`KSILO+9.32`. Origin into `ALDCTR`. Compute w. Set the card count from
`SRCDCT`, or 0 for a library subprogram. Program cards after the first,
common definition and FORTRAN branch cards go straight to the counter.

**Card counting** (`ARNRM1`, L p.326 l.41). In a BSS deck every normal
return, including T and B cards, decrements the count. At zero:

1. Word 1 of the table is loaded as an index word: origin in value,
   `SRTVL` in count, `SRNXAD` in refill (L p.326 l.47).
2. If `SRTVL` is nonzero, transmit it from
   `table + 3.0 + SRCCT half-words` to **subprogram origin + 1.0**
   (L p.327 ll.2-4). This overwrites the A8 names the data cards loaded.
3. `SRNXAD` zero: take the branch address from `KSILO+10.`, branch
   return (ll.28-30).
4. Otherwise store it in `KSILO+9.32`; if bit .63 (library) set the type
   area to `LB` + the 36-bit name in word 0, read from word 0 of it with
   `AREAD1`; if not, set the type area to `ATWSTA` (`))))))))`, TWS) and
   position `AREADS` by `SRDKAD` (L p.327 ll.10-27).

A library subprogram has count 0, so the decrement never reaches zero;
it ends on `$FETCH`'s end return, which sets the count to 1 and enters
`ARNORM` (L p.334 ll.12-16; 6728-0 p.80).

**Disk geometry the loader assumes.** 15 words per card. TWS: 34 cards
per arc, then 2 words are skipped (`V+IC,13,15.`, `LCI,$13,34.0`,
`V+I,$13,2.0`, L p.332 ll.27-30; 6728-0 p.80). First card at relative
word `SRDKAD` + 2 as read (`AREADS XW,-13.,35,,7`). Library: `AREAD1
XW,-15.,0,,7`, contiguous from word 0, no arc gap as read.

**Relocation table** (6728-0 p.82 Figure 39; 6728-1 p.91 Figure 44;
C28 p.10 Figure 4; L as above):

| word | bits | name | meaning |
|---|---|---|---|
| 0 | 0-35 | `SRDKAD` | library (bit 63=1): 36-bit type-area name |
| 0 | 0-17 | `SRDKAD` | else: 18-bit relative FWA in TWS |
| 0 | 28-45 | `SRCDCT` | card count, not library |
| 0 | 63 | `SRLIB` | 1 library |
| 1 | 0-17 | `SRORG` | subprogram origin |
| 1 | 28-45 | `SRTVL` | transfer-vector length |
| 1 | 46-63 | `SRNXAD` | next table; zero ends |
| 2 | 0-18 | `SRCCT` | number of named commons |
| 2 | 32- | `SRCOMB` | origin of named common 1; each next common one half-word on (`table + 2.0 + i × .32`, L p.325 ll.25-31, L p.326 ll.23-25) |
| ... | | | more common origins, then transfer vector, actual branch instructions |

### 5.5 Resume load

L p.291 ll.45-51, pp.332-333; 6728-0 p.79 Figure 38.

1. `$RESLD` fetches the loader from disk (`YMPFCH`). 22LOADER overlays
   the buffer `YMPBUF` (L p.320 header note; p.319).
2. GO phase of a COMPILGO with `KSILO+2.` = `BSS`: `YARSL`. Lower limit
   from `KSILO+8.`, **upper limit = `KSILO+9.0`**, the base of blank
   common, "inhibiting loading into blank common" (C28 p.4); new-job bit
   set; enter `ARNRM5` with `KSILO+9.32` as next table (L p.333 ll.22-28).
3. Otherwise limits from `YLLSAV`, source from `SREADS`, or system input
   if the request was the `$SCR` form (L p.332 ll.7-11).
4. Initial entry, non-BSS: clear storage from (8)41 = 33.0 to the upper
   limit (`SBAPP`) (L p.332 ll.13-17; C28 p.4). BSS: not cleared (C28 p.4).
5. Read one card to `YBCBU` by `$SCR` or `$FETCH`; call `ALOADR`; repeat
   on normal return (L p.332 ll.19-52).
6. Branch return: restore source, put the address in `SICBU` and `$RET`
   (L p.332 l.53 to p.333 l.5).
7. Error return: print the reject, go to `$EOJ` on initial entry, else
   `$ABEOJ` (L p.333 ll.6-21; L p.334 ll.17-37).

User entry: `B,$MCP ; ,$RESLD` (C28 p.4). "Care should be taken" in an
I-O fix-up: it does nothing to alter a stacking mode (C28 p.4).

### 5.6 Patch and dump (C28 pp.4-6)

- **P**: replace the instruction at the origin by a branch (or branch;
  NOP, by its length) to the patch area, at the lowest location above all
  loaded. Place there: the replaced instruction, the card's half-words, a
  branch back to the next instruction. Continuation with no origin: up to
  four half-words following the highest in the patch area. The programmer
  may have to extend the upper limit.
- **D**: same displacement, then a call of the MCP dump routine, first
  and second half-words the limits, third the format, then a branch back.
- **K**: up to three half-words at the relocated origin. One above the
  subprogram's highest origin resets the patch area.
- **A**: as P, relocated, up to three half-words, each relocated by its
  columns. Patch area at the end of the subprogram. BSS extends the size;
  in non-FORTRAN "no space is provided".
- **Z**: as D, relocated, parameters relocated. "(or the named common,
  although it seems unlikely ...)".

Listing tail: `APCRND` stores the branch back and updates `AHIWD`,
`ALDTC` (L p.330 ll.11-19). Skeletons: `APBRCH`, `APNOP`, `ABDMP` (`B,DMCP
; ,DDUMP`), `ADFWA` (L p.331 ll.19-23).

## 6. The BSS processor (C28 pp.7-14; nothing in the listing)

### 6.1 Input and output

Input: disk if BSS is the last chain link, system input if it runs alone,
in which case it places subprograms on disk, "so that the MCP loader, in
both cases, finds the input on the disk" (C28 p.7).

Output, left in storage and the communication region (C28 p.9): the
relocation table at the base of blank common; the storage map printed;
library entries sorted so "library subprograms are loaded in the order in
which they appear on the disk".

### 6.2 Communication region (C28 p.12 Figure 7)

`KSILO` is 25 words (`K QUANT SYN,25`, `K SILO DR(BU,64),(K QUANT)` at
220451.00, L p.171 ll.42-43).

| word | 0-31 | 32-63 |
|---|---|---|
| 0-7 | defined by MCP | |
| 8 | problem program lower limit | upper limit |
| 9 | origin of blank common | address of relocation table |
| 10 | branch address | main entry point |
| 11 | address of node table | |
| 12-13 | link table mask | |
| 14-24 | defined by chain of processors | |

Word 2 holds the A6 name `BSSbbbbb` (6728-0 p.80); the listing compares
18 bits of it. Field widths: 18 bits each in words 8-9, 19 at 10.0
(6728-0 p.80).

### 6.3 The scan (C28 pp.7-9)

Per subprogram, by card class:

| card | BSS action |
|---|---|
| FORTRAN program | new first-table entry, pointers to the second and third tables, names and relative origins; `*MAIN*`'s origin to the communication region; the card also closes the previous subprogram's computed size; no entry points means a data subprogram; blank common size becomes the largest declared |
| Common definition | names and sizes into the second table; the largest size wins |
| O | allocate the next subprogram at that absolute origin; conflict with earlier storage is an error; later subprograms go higher |
| T | reset sequence counter, except DEFINE, DEFI, NODE |
| DEFINE | second name replaces the first in the second table; not before the definition card declaring it |
| DEFI | second name replaces the first within this subprogram only; may be new |
| NODE | job uses overlay |
| Relocatable instruction | scan for size; the first holds the index word in its first 64 bits |
| Relocatable data | scan for size; those right after the first instruction card hold the transfer vector, saved with a third-table entry per name |
| Absolute binary, C, P, D | ignored |
| K, A, Z | scan for size: K above the highest extends the subprogram to the origin; A and Z extend it for instructions or dump sequence |
| FORTRAN branch | end of deck |
| B | IOD and REEL reduce problem-program storage for IOD tables; others ignored |
| Super T | stop sequence checks for the job. Otherwise BSS verifies sequence numbers and check sums of all binary cards |

Up to 50 significant define cards (C28 p.22, message 9).

### 6.4 Intermediate tables (C28 p.8)

**First (Figure 1).**

| word | fields |
|---|---|
| 1 | 0-47 entry point name; 48-63 number of cards in subprogram |
| 2 | 0-18 absolute origin of entry point; 19-27 segment number; 28-45 storage occupied by subprogram; 46-63 pointer to third-table entry |
| 3 | 0-18 relative entry point; 25 library flag; 28-45 pointer to second-table entry; 46-63 disk address if not in library |

Absolute subprogram: the O card's origin goes in the first 19 bits of
word 2.

**Second (Figure 2).**

| word | fields |
|---|---|
| 1 | 0-47 common name |
| 2 | 0-17 absolute common origin; 25 block-data flag; 28-45 amount; 56-63 segment number |

**Third (Figure 3).**

| word | fields |
|---|---|
| 1 | 0-47 subprogram name; 56-63 segment number |
| 2 | 0-47 transfer-vector entry; later "replaced by a branch; NOP to the absolute transfer address" |
| 3 | 0-47 entry point name from first table; 48-49 legality marks; 56-63 transfer segment number |

### 6.5 Matching, allocation, output (C28 pp.7, 9)

1. Match every third-table name against first-table entry points. Not
   found: fetch from the FORTRAN library on disk and treat as input,
   adding table entries. Continue until all are linked.
2. Compute the upper limit for the job, the relocation-table size and
   the blank common origin. Store the origin in the communication region.
3. Subprogram origins: consecutive from **33.0**, in order encountered;
   library subprograms higher, in order of call. Unused storage may lie
   between the highest subprogram and the lowest common.
4. Blank common highest; named commons next below (C28 p.7).
5. Merge identical common names, reserving the largest.
6. Check overlap of common and program.
7. Build the table, one entry per subprogram, with the fields of section
   5.4; library entries carry the name, others the disk address and card
   count.
8. Store main entry address; sort library entries; print the map; pass
   control via MCP to the loader.

**An oracle.** Example 4's map (C28 p.17) satisfies these rules; I
checked the octal sums:

- Subprograms: `*MAIN*` 41 + 745 = `STEP` 1006; + 441 = `RANDM` 1447;
  + 7 = `POLY` 1456; + 346 = `DERIV` 2024; + 271 = `VALUE` 2315; + 134 =
  `FISIP*` 2451; + 7 = `IOCS*` 2460; + 3037 = `UST*` 5517. `SPTXT*`
  shares `IOCS*`'s origin, with size printed `E. P.`
- Commons, unnamed first then descending: 213713 (amount 14); `DIFF`
  213703 + 10 = 213713; `A` 213535 + 146 = 213703; `STE` 213527 + 6 =
  213535; `POL` 213363 + 144 = 213527.
- Columns: NAME, ORIGIN, REL. E. P., SIZE, LIB., SEG. NO.; and NAME,
  ORIGIN, AMOUNT, SEG. NO.

### 6.6 Segmentation (C28 pp.10-14; 6751 p.35)

**Model.**

- A segment is a group of subprograms behind a NODE card. The primary
  segment holds `*MAIN*`, FIOD, all library routines and the link
  subprogram, starts at 33.0, and stays in storage.
- No node card is needed for a single segment (6751 p.35).
- Limits: at most 8 in storage at once, at most 99 in all (C28 p.11; 6751
  p.35).
- FORTRAN subprograms must be compiled before node cards are inserted
  (6751 p.35; but see C11).

**Storage.**

- The relocation table must stay in storage (except the primary segment's
  entry) and goes above blank common.
- The node table goes immediately above it, to the top of available
  storage (C28 p.10).
- Named commons are below blank. A segment's common is reserved for the
  highest position in the tree reached by all groups referring to it.
- Block data goes with the segment holding that subprogram; referencing
  segments must be in its group and higher (C28 p.10).
- Commons of lower segments go higher in storage.

**Node table (Figure 5, C28 p.10).**

| word | fields |
|---|---|
| 1 | 0-17 beginning of common; 28-45 end of common |
| 2 | 0-17 beginning of program; 18-35 end of program; 40-47 segment number from NODE card; 48-63 attached segments |
| 3 | 0-63 attached segments |

The first 64 bits of each entry are not moved to upper storage (C28 p.13).

**Procedure.** After the input scan, if a NODE was seen (C28 pp.11-13):

*Expansion.* Trace each entry's chain, for example `08, 04, 02, 01, 00`.
Reaching 00 stores the available-storage lower limit, a second-table
entry for blank common's segment number, and the link table mask for the
primary. Bad attachment: error. Then the normal library scan.

| phase | work |
|---|---|
| 1 | Storage addresses of each segment's start and end; absolute entry origins. Start at the primary; scan the first table; store the next segment's start in the node table |
| 2 | Merge duplicate commons: larger size; match segments up the node table until an associated segment is found and store it; zero the eliminated entry's segment and leave a pointer. Errors: duplicate block data, block data in a foreign segment |
| 3 | End of blank common into the primary's node entry. Common origins by subtraction from the blank base; primary's lowered if necessary for its relocation table; repeat per node entry. Second scan completes the duplicates |
| 4 | Common start below the segment's highest program: error. Space for the primary's table |
| 5 | Transfer vectors. Within the segment or to a lower address: compute the actual address into the third table. To a higher address: a transfer to the link subprogram. Legality: either segment number must appear among the other's associated numbers, else illegal |
| 6 | Further legality, by marking each direction: a transfer to a lower segment is illegal if return cannot be made because another transfer would overlay the original |
| 7 | Compute the table base (not blank's base for this case); too-large check; fill entries; store the address |
| 8 | Compute the node table base and move it to the top, verifying the relocation table is below it |

Then reorder library entries and print the map.

**Worked examples.** Figure 6 (C28 p.11): 5 primary; `NODE,05,00`,
`NODE,02,04`; 10 and 11 start at one location; 5, 6, 8, 11 can be one
load. 6 to 4 is illegal. 11 to 8 is illegal only if 8 then transfers to
10 before returning. Figure 8 (C28 p.13): 1 to 4 and 4 to 1 may be legal;
3 to 4 and 2 to 3 are illegal.

**Not checked by BSS** (C28 p.11): overlay by a subprogram passed via
EXTERNAL; overlay of named commons.

### 6.7 The link program (C28 pp.13-14)

- BSS puts a branch to it in the transfer vector when the callee will
  occupy a higher position.
- First entry, after the primary is loaded and before execution: pick up
  the communication region with the mask, then go to the main entry.
- Later entries through the transfer vector, which carries, besides the
  branch, the absolute target and the target's segment number.
- In storage (mask bit on): go to the address. Otherwise search the node
  table entry for the segment, call the loader for each segment in that
  entry not yet loaded, then go to the address.

## 7. In the listing, and to be reconstructed

### 7.1 Present in L

| part | where |
|---|---|
| `$RESLD` entry, loader data block | p.291 |
| dispatch, `ATBL`, index words, skeletons | pp.320, 331 |
| origin, flow, skip, zero, partial word | pp.321-322 |
| sequence, check sum, T, Super T, branch, O | pp.322-324 |
| FORTRAN program card, relocation table read | pp.324, 326-327 |
| relocatable instruction and data | pp.324-326 |
| C card, D card, P tail, error returns | pp.327-328, 330-331 |
| resume load, `YARSL`, reject messages | pp.332-334 |
| BSS hooks elsewhere | p.271 (chain rewrite), p.389, p.397 (`YBSSID`, `YTSP`) |

Run on the model, 2026-11-11 (`tests/gen_loader_deck_tb.py`, in the
suite): the origin, flow, zero, partial-word and branch paths, the
sequence test and `ACHSM` load a six-card absolute deck strap/strap2
punched, through the calling sequence of p.332 lines 42-52, and core
equals STRAP II's image. Relocatable, FORTRAN, C, P and D cards have
not yet run.

### 7.2 Printed p.329: lost, inside the loader

Span 235112.00-235153.40, 34 words, serials TA000449-499. Labels fixed
by references from transcribed pages:

| label | address | what the referring page shows |
|---|---|---|
| `AOIGN3` | 235113.0 | end of the ignore scan |
| `AOIGN1` | 235114.40 | ignore a whole card |
| `AOCTH1` | 235116.0 | hex A-F |
| `AOCTL6` | 235122.40 | not a decimal point: continuation or end of card |
| `APCARD` | 235130.0 | P entry |
| `APCRD2` | 235135.0 | after a P card's origin |
| `APCRD4` | 235150.40 | P or D rejoin |

Also on it: the end of `AOIGN2` (p.328 ends mid-routine at `V+I,$3,.32`),
and whatever else fills the span. Text: 6728-0 p.85, chart p.86; C28
pp.4-5. Reconstruct, labelled, against those addresses.

**Paths that touch p.329:** P, D (via `APCRD4+1.`), hex A-F, ignored
corrections, and any C card reaching a decimal-point column that holds no
point, which includes every C card with fewer than four half-words (L p.327
l.48; 6728-0 p.85). **Paths that do not:** origin, flow, branch, T, Super T,
B, O, relocatable instruction and data, FORTRAN program, common definition,
FORTRAN branch, and a C card with an origin and four half-words of digits
0-9 (as read).

### 7.3 Absent from L, and later than it

K, A and Z (`MKCARD`, `MACARD`/`MZCARD`, 6728-1 p.94 Figure 47; pp.90-91),
the messages that name them, and 6728-1 p.89's "the rest of the PP memory
(i.e., blank common) is set to plus (+) infinity for non-segmented jobs",
which L's `YARSL` path does not do.

To add them means choosing a later MCP than the listing. See G2.

### 7.4 Absent from L entirely

| part | status |
|---|---|
| BSS processor: all of section 6 | external behaviour and table layouts only |
| Segmentation phases 1-8 | prose only |
| Link program | prose only |
| FIOD subprogram, FORTRAN library | not read here; not in L (grep of decks for `FIOD`: none) |

Sweep behind this table. `grep` over `decks/*.strap` for `SRORG`,
`SRNXAD`, `SRTVL`, `SRCOMB`, `SRCCT`, `SRDKAD`, `NODE TBL`, `LINK TABLE`,
`INTERMEDIATE`, `*MAIN*`, `FIOD` finds none. `NAMED COMMONS` and `T.V.`
hit only remarks in the loader itself (p.324 l.20, p.327 l.2). `TOO MANY`
hits only unrelated MCP pages (pp.107, 152). So: **no deck holds any BSS
processor code**, and the symbolic `SR...` names exist only in the guides;
the loader uses numeric offsets.

Also, no repo tool produces these cards: a grep of `strap/*.py` for
`PUNREL`, `PUNFPC`, `PUNCDC`, `COMBLOCK`, `FEND`, `ENTER` and `BSS` finds
nothing, and `strap_asm.py` has no match for "relocat".

## 8. Errors

### 8.1 Loader error codes

6728-0 p.80; L p.334 ll.43-50 in the same order; returned through
`AERRA` (with column 3) or `AERRB` (with 0), L p.330 l.41, L p.331 l.2.

| code | 6728-0 p.80 | L p.334 text | C28 p.22 and 6678-1 p.53 |
|---|---|---|---|
| 1 | Checksum error | CHECKSUM ERROR. | CHECK SUM ERROR |
| 2 | Sequence or ID error | SEQUENCE ERROR. | SEQUENCE ERROR |
| 3 | Illegal card type | ILLEGAL TYPE OF CARD. | ILLEGAL TYPE OF CARD |
| 4 | Illegal non-BSS function | ILLEGAL NON-BSS FUNCTION | same |
| 5 | Out of bounds | TRIED TO LOAD OUTSIDE LIMITS. | same |
| 6 | C or P card incorrectly punched, e.g., hex character not 0-9 or A-F | C OR P CARD INCORRECTLY PUNCHED | C, P, D, K, A, or Z CD PUNCH ERR |
| 7 | Blank location in first octal card | FIRST C CARD HAS NO ORIGIN. | NO ORIGIN ON FIRST C OR K CARD |
| 8 | First binary card not an origin card | NO ORIGIN IN FIRST CARD. | NO ORIGIN IN FIRST CARD |

Also: `-NO BRANCH CARD IN CURRENT DECK- JOB REJECTED.` and `-JOB CANNOT BE
RUN BECAUSE OF INPUT DIFFICULTIES.` (L p.334 ll.39-40, 51). Bit 60 of
`REJJOB` signals the second (6728-0 p.80; L p.332 l.54). Form, L:
`-LOAD. REJ. CD. xxxx ID yyyyyyyy reason`. Form, C28 p.22 and 6678-1 p.53:
`LOD. REJ. CD. XXXX ID YYYYYYYY` (reason) `LAST CORRECT CARD LOADED IS
SEQUENCE NO. XXXX ID YYYYYYYY`. A grep of all decks finds no `LAST
CORRECT`. Fields: XXXX column 3, YYYYYYYY columns 73-80 (C28 p.22; L p.334
l.28, `ALDBF+13.32`).

Text for "NO ORIGIN IN FIRST CARD": in an absolute deck, perhaps a first
flow card; a non-BSS relocatable deck without an O card also gives it (C28
p.22).

### 8.2 BSS messages (C28 pp.22-23)

Always:

1. JOB TERMINATED DUE TO SEQUENCE (OR CHECK SUM) ERROR. LAST CORRECT CARD
   IS SEQ. NO. X ID Y IN Z SUBPROGRAM.
2. JOB REJECTED - COMMON AND PROGRAM OVERLAP.
3. BSS TERMINATED JOB - PROGRAMMER ERROR, on the console only, with on the
   listing JOB TERMINATED - (reason), reason one of:
   - T.V. XX INCOMPLETE IN YY SUBPROGRAM
   - TOO MANY NAMED COMMONS IN YY SUBPROGRAM
   - TOO MANY TRANSFER VECTORS IN YY SUBPROGRAM
   - ILLEGAL TYPE OF CARD IN YY SUBPROGRAM
   - RELOCATION TABLES ARE TOO LARGE
   - INCORRECT CARD ORDER IN YY SUBPROGRAM
4. ILLEGAL DISK INPUT TO BSS LOADER
5. LOADER ADJUSTMENT HAS LOW ORIGIN
6. REPEATED UK INTERRUPTS FROM DISK
7. EPGK INTERRUPT FROM DISK
8. COMMON XX WAS NOT IN THE SYMBOL TABLE WHEN THE DEFINE CARD WAS
   ENCOUNTERED IN SUBPROGRAM YY
9. THE 50TH DEFINE CARD HAS BEEN ENCOUNTERED. THE REST (IF ANY) WILL BE
   IGNORED
10. NO ENTRY POINT WITH NAME *MAIN* - JOB WILL NOT BE RUN

Segmented jobs, each prefixed ERROR -:

1. SEGMENTS NOT PROPERLY ATTACHED
2. SEGMENTS HAVE TOO MANY LEVELS (no more than eight)
3. ORIGIN CARD OVERLAYS PREVIOUS CODING. ORIGIN IGNORED
4. SEG END IN COMMON TABLE NOT IN NODE TBL (out of phase)
5. DUPLICATE DATA COMMONS
6. DATA COMMON NOT IN PROPER SEGMENT
7. MAIN SEGMENT NOT FOUND (out of phase)
8. THE PROGRAM EXCEEDS STORAGE IN SEG XX
9. ILLEGAL TRANSFER BETWEEN SEGMENTS
10. TOO MUCH STORAGE USED BY RELOCATION TABLE
11. IN LOCATION OF RELOCATION TABLE (out of phase)

## 9. What STRAP II must punch

6729 pp.183-188; 6129 pp.22-23; 6751 pp.30-31, 34.

| pseudo-op | effect |
|---|---|
| `PUNREL` | relocatable mode. Later non-PUNREL punch pseudo-ops turn it off |
| `PUNFPC,S,C` | FORTRAN program card, from following `ENTER`s |
| `A ENTER,B` | entry name A (8 chars), point B, 19 bits |
| `PUNCDC` | common definition card, from following `COMBLOCK`s |
| `A COMBLOCK,N` | named common, size N, 18 bits; reserves nothing |
| `SLCRCOM,B` | location counter zero relative to common B; blank B is blank common |
| `ORIGIN,N` | O card |
| `FEND` | FORTRAN branch card |

- Named commons are numbered from 1; blank is 0 (6729 pp.185-186). Blank
  common takes only DR, no DRZ (6729 p.187). STRAP punches no card for a
  blank-common address: "To insure that no data will be loaded into
  blank common, STRAP does not punch an output card where the address
  field is left blank following an SLCRCOM" (N28-1081 page 3, C28-6129
  PDF p.61, read in the ink 2026-11-11). Same page, FEND: "If END is
  specified, no branch card will be punched", said of a FORTRAN program
  or subprogram.
- Unit formats behind this: 6729 pp.184-185 (Figures 17-19): `ZICOMM`, bits
  24-26 and 56-58, `Sinrl1`, `Sinrl2`, `Sinua`.
- Worked programs: 6729 p.184; 6751 pp.34-35; C28 p.15 (two).
- **Which addresses relocate** (read in the ink 2026-11-11: 6729
  pp.56, 178, 183-188; 6129 Appendix p.55, PDF 58). Each symbol table
  entry carries `Zst35` (1 once location-counter dependence is decided),
  `Zst36` (0 if location-counter dependent, 1 if not) and
  `Zstcom`/`Zstcon` (relocate as an upper address relative to common
  `Zstcon`, 0 being blank common); a symbol defined after `SLCRCOM` gets
  `Zstcom` = 1 and the common's number (6729 p.185). The one printed
  symbol rule, p.185: "When both Zstl3 [so printed; Zst35 meant] is on
  and Zst36 is off, it is necessary to look at Zstcom. If Zstcom is zero,
  the address is to be relocated as a lower address; if on, ... as an
  upper address relative to the common whose number is given in Zstcon."
  So a decided, location-counter-dependent symbol with `Zstcom` 0 is
  program-relative: stage 1's case.
- VALUE returns `Sinrl1` and `Sinrl2`, each (BU,1), "relocation
  indicators", footnoted "See Section on relocation ops" (6729 p.56), and
  in its third output word `Sincom` and `Sinua` (p.185, Figure 18).
  INSERT, in Pass 2, reads them, and on `Sinrl1` = 1, `Sinrl2` = 0,
  `Sinua` = 1 puts the common number at `ZICOMM` (p.185); the relocation
  section gives no other case. **How VALUE combines terms is not
  printed.** The one rule in print is an error: "MORE THAN 1 LOC. CTR.
  DEP. SYMBOL", detected by INSERT, number 123 in 6729 p.178 and 121 in
  6129 Appendix p.55, "Address field contains more than one location
  counter symbol which may cause trouble in relocation". So: no
  location-counter-dependent symbol, absolute; one, relocatable; more
  than one, flagged. **UNSPECIFIED: what `Sinrl1`/`Sinrl2` mean.** Two
  readings fit INSERT's test, and both are kept: (a) `Sinrl1` = one or
  more location-counter-dependent symbols, `Sinrl2` = more than one; (b)
  they mirror the unit's bits 24 and 25 (relocate; address or refill
  field), which fits `ZICOMM` being "for the address from an address
  field" (p.184). The code carries a count of location-counter-dependent
  symbols, which error 123's text grounds, and names neither bit.

Transfer-vector convention: "beginning in cell 1 of the program"; A8 names;
calls by `SIC,$X15 ; B,name` (6751 p.31).

## 10. Gaps and contradictions

### Gaps: UNSPECIFIED, and I did not fill them

- **G1.** Which eight classes C22-6678-0 listed, and so why N22 says 14 and
  the listing 15. Super T, or B, may be the difference. That edition is
  listed at CHM 102663038 (`docs/chm/README.md` l.361) and is not in
  `docs/chm/`.
- **G2.** Which MCP E4 and BSS target: the March 1963 listing (15 classes)
  or the 1964 manuals (18). An owner's decision, not the documents'.
- **G3.** The check-sum algorithm in any document (section 5.3).
- **G4.** Printed p.329's code (section 7.2). Hex A-F's card code in
  particular.
- **G5.** BSS's code, its size, its memory layout, its own limits ("exceeded
  available storage" is the only statement on table capacity).
- **G6.** How BSS writes subprograms to TWS: the arc header's 2 words, what
  fills the end of a deck, and the disk-address field's exact width (18 bits
  in Figure 4 and Figure 39, the last 18 bits of word 3 in Figure 1).
- **G7.** The library's type-area form: `LB` + 36-bit name is the listing's
  (L p.327 ll.23-25); how an A8 entry name reduces to a 36-bit name is
  UNSPECIFIED. Which type areas exist, and their contents: FIOD, IOCS, FISIP,
  SPTXT, UST are names only.
- **G8.** Link program: calling sequence, its code, where it lives, how a
  transfer-vector entry is encoded when it goes to the link ("in addition to
  the branch ... the absolute address ... and the segment number", no
  layout), how it re-enters the loader, and how a table entry is made
  current for a segment load. L has no entry for it, and `YARSL` runs the
  table chain from `KSILO+9.32` to `SRNXAD`=0.
- **G9.** Link table mask: which bit means which segment. "A bit string";
  99 segments and two words are all that is stated.
- **G10.** Encoding of segment numbers and attached-segment lists in the node
  table (binary or BCD, order, terminator, number of words per entry).
- **G11.** How a segment's relocation entries are grouped and ordered, and
  how a segment's end is marked, when the table is one chain.
- **G12.** The T card's printing. C28 p.6 and 6678-1 p.13 say T cards are
  printed; 6678-1 p.13 also says B TYPE and T SUBTYPE cards after the first
  binary card are. The listing's `ATCARD`, `ASUPRT` print nothing. Which
  program prints them, if not the loader, is not stated in the pages read.
- **G13.** The index word's meaning on a subprogram's first instruction card,
  once BSS is past it: BSS reads the count from it (C28 p.9), and the loader
  uses `SRTVL`. Whether the word's other fields matter is UNSPECIFIED.
- **G14.** `DEFINE` card column layout past column 14, and punctuation
  (`DEF,C` and `DEFI,` as drawn on C28 p.20).
- **G15.** The required contents of fields marked "Not used" in the tables:
  zero or don't-care.
- **G16.** Scope of the storage map beyond its columns, and whether map output
  goes to the listing tape (only "printing").
- **G17.** Alignment when the relocated origin is not on a half-word: the
  listing advances both pointers to the next half-word (L p.324 ll.54-56, L
  p.325 l.1, as read); no document says relocatable instruction cards may do
  this or describes what the skipped bits are.
- **G18.** Transfer-vector source when `SRCCT` is odd or zero: the listing
  computes `table + 3.0 + SRCCT half-words`, which is not on a word for odd
  counts, and transmits to a word (L p.327 ll.2-4). What the transmit does
  with the odd half-word was not checked, and Figure 4 does not say.

### Contradictions and differences

- **C1. Number of classes.** 8, 14, 15, 18, section 3. The listing and 6728-0
  agree at 15.
- **C2. Relocation-bit coding.**
  - C28 p.19, 6729 p.188, 6751 p.33: `10..0`, `10..1..`, `10..10` blank,
    `10..11i` named, so a flag bit before i.
  - 6728-0 p.85, 6728-1 p.90: `1000`, `1010`, `1001C`, `1011C`, "C ... encoded
    in i bits", "For blank common references, C=0", widths "1, 4, or 4+i"
    (6728-0 p.81).
  - L p.325 ll.22-33 tests a flag (`BB,.3($6)`) and reads i starting one bit
    later (`.4($6)`), so its widths are 1, 4, 5, 5+i as read. **The listing
    sides with C28.** Follow it; a program built from the guides alone would
    be one bit off.
- **C3. Secondary bit count.** Columns 8-9: C28 p.19, 6729 p.187, 6129 p.22, L
  (`LF(BU,60),ALDBF.48`, low 24 bits). Columns "9-10": 6751 p.33. Its own
  diagram draws 8-9, 10 loading base.
- **C4. Branch card.**
  - C28 p.18: 3 sequence, 4 check sum, 5 unused, 6-7 address.
  - 6129 p.23's table has 3 identification, 4 sequence, 5 check sum, 6-7 "Not
    presently used / 24-bit transfer address", with the 2.0-2.11 row printed
    against the end of the code-column note. It may be a slipped table.
  - L uses C28's (`ALDBF.24`, `ALDBF.60`).
- **C5. Last data column, and 72.**
  - Up to 744 bits, columns 11-72: C28 p.5, p.19; 6751 p.33.
  - 11.0-71.11, with "A nine column field" 72.0-80.11 ignored: 6729 pp.187-188.
  - 736 bits ending 71.11, identification from 73.0: 6129 p.22, which also says
    "(columns 10 through 72)" and a primary count "from 0 to 748".
  - The listing does not limit the count except by its 10 bits and `AHGHWD`,
    but its check sum stops at column 71 (as read). A data bit in column 72
    is loaded and not summed.
- **C6. O card field.** `xxxxxx.x` (C28 p.21); `xxxxxx.0` (6729 p.188); "8
  Hollerith characters in columns 2-9" (6728-0 p.81; 6728-1 p.89); L converts 6
  digits only, count `AOXW1` 6.
- **C7. Address of the relocation tables.** `KSILO+0.32` (6728-0 p.80);
  `KSILO+9.32` (6728-1 p.88; C28 Figure 7; L). The -0 reading is a misprint or a
  slip; p.80 itself lists "address of relocation tables 9.32".
- **C8. Relocation-table word 0.**
  - Card count at 28-47 in C28 Figure 4; 18 bits at 0.28 in 6728 Figures 39 and
    44, and in L (`LF(BU,18),.28($1)`).
  - Library name: "the first 48 bits ... the entry point name" (C28 p.10); "a
    36-bit field containing a type-area name" (6728) and L (36 bits, `LB`
    prefix).
  - Common fields: 32-50 in Figure 4; "(BU, 32), 2.32" in the 6728 figures.
- **C9. Decimal-point test.** 12,3,8 or 12,1,3,8 (C28 p.4; L); "12, 3, 8 or 1, 3,
  8" (6728-0 p.85); "12, 3, 8; 12, 1, 3, 8; or 1" (6728-1 p.90).
- **C10. Transfer-vector length.**
  - "index word whose count field" (C28 pp.7, 9).
  - "The first 18 bits of cell zero must contain an integer" with, in the same
    place, `XW,,ENDTV-BEGINTV`, which is a count field (6751 p.31); `XW,,2` (6751
    p.34); `DD(BU),1.0` (6729 p.184).
- **C11. Node cards and FORTRAN source.** "FORTRAN subprograms must be compiled
  before node cards are inserted" (6751 p.35). C28 p.16's Example 3 is COMPILGO
  with a `T SUBTYPE, FORTRAN` subprogram between node cards, each node behind a
  `T SUBTYPE, BIN`.
- **C12. "Figure 5".** C28 p.13 Phase 7 refers to Figure 5 for the communication
  region, which is Figure 7.
- **C13. Messages.** Section 8.1. The listing has no "LAST CORRECT CARD" line, no
  K, A, Z wording, and `LOAD.` for `LOD.`
- **C14. Dump format.** 0.40 (C28 p.21) and "not 4.32 but 0.32" (N22 p.11). Octal
  .40 is decimal 32, so these probably agree. `ABDMP` and the format's use are
  not exercised here.
- **C15. Blank common storage.** "In a BSS environment, problem program storage
  is not cleared" (C28 p.4); "the rest of the PP memory ... is set to plus (+)
  infinity for non-segmented jobs" (6728-1 p.89). L: no such code on the `YARSL`
  path; 6728-0 p.81 lacks the phrase.
- **C16. BSS's error text for the ID.** C28 p.22, message 1: "Y is the
  identification in column 4". Column 4 is the check sum everywhere else; the
  loader's messages take the identification from columns 73-80 (C28 p.22).

## 11. What was and was not read

Read as page images:

- C28: pp.1-24, all.
- 6678-1: pp.12-14, 53.
- 6728-0: pp.79-86, 195-196.
- 6728-1: pp.88-94.
- 6729: pp.183-189.
- 6751: pp.28-36.
- 6129: printed pp.22-23.
- N22: pp.3, 11.

Rendered and not read: 6678-1 p.15; 6728-1 pp.87, 95-100; 6728-0 pp.87-92, p.197;
6729 pp.190-196; 6129 printed pp.24-26; 7030 Reference Manual p.29 (CBR, seen only
in OCR).

Not read:

- 6751 pp.1-27 and p.37. Contact sheet only, for pp.19-27.
- The remainder of each document.
- CHM and DTIC holdings were **not swept**. L-1's note says BSS "travels with
  FORTRAN" and to look in the DTIC decks; I searched only `docs/dtic/README.md`
  and `docs/chm/README.md` for the words BSS and loader. The claim "IBM's code is
  lost" is the caller's, not established by this file.
- The listing's own page images. Listing facts come from the checked decks.
