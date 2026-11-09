# STRAP II data formats and external behaviour

Transcribed from the ink of IBM form C22-6729, *IBM 7030 Assembly Program
(STRAP II), Programming Systems Analysis Guide*
(`docs/C22-6729_7030_STRAP_II_Sys_Analysis_Guide.pdf`). PDF page = printed
page on every page cited here (checked on each). `p.N` is the printed page.

Conventions in this file:

- Bit numbering is the guide's: bit 0 is the leftmost. `w.b` is word w, bit b.
- **UNSPECIFIED** means the guide leaves it open in the pages read. Nothing
  is filled in. §15 says what was and was not read, so the reach of each
  negative is visible.
- **DERIVED** marks a conclusion of this transcription rather than a sentence
  of the guide; the evidence is given.
- **[printed]** marks something copied as it stands although it looks wrong.
- Underlined symbols in the guide are locations. "Value", "count" and "refill"
  field are the guide's words for index-word fields (p.175, p.90).

---

## 1. COMREC (Communication Record)

A 25-word table in core, used by MCP and the processors. The first eight and a
half words are MCP's alone. STRAP II expects words 7.32 through 24.63 set up
as below (p.8).

### 1.1 Code and unit numbers (p.8)

| Code | Meaning | | Unit | Meaning |
|---|---|---|---|---|
| 0 | Not used | | 0 | System Input or System Output |
| 1 | Card code | | 1-10 | Not used |
| 2 | A6 code | | 11 | Disk |
| 3 | A8 code | | | |
| 4 | Not used | | | |
| 5 | IQS code | | | |
| 6 | Binary code | | | |
| 7 | Not used | | | |

### 1.2 Word by word (pp.8-10)

| Bits | Contents | Behaviour |
|---|---|---|
| 0.00-7.31 | Reserved for MCP | p.8. Word 1 is nevertheless read by STRAP II: it holds the number of arcs in temporary working storage (p.131 Box 8). |
| 7.32-7.39 | dashes | p.8 |
| 7.40 | A pre-processor can turn it on | Last in a chain: if on when STRAP II is last, STRAP II turns on MCP's reject bit (p.8). |
| 7.41 | STRAP II sets it if one or more undefined, multiply-defined and/or circularly defined symbols exist | Last in chain, COMPILGO, STRAP: MCP's reject bit turned on if 7.41 and/or 7.42 on. Not last: available to the post-processor (p.8). |
| 7.42 | STRAP II sets it on: improper op code; improper secondary op code; entry mode preceding a non-DD; extra secondary op code; more than one DDS; location counter does not agree; assembly error; symbolic statement too long | As 7.41 (p.8). |
| 7.43 | STRAP II sets it if any error condition which has not been suppressed has occurred | p.8 |
| 7.44-7.63 | Purpose column blank | p.8 |
| 8.00-8.17 | Input: relative arc number | Word "must always be set up by the pre-processor" (p.9), but see §14 C3. First in chain: input from System Input. Otherwise disk or System Input as word 8 says (p.9). |
| 8.18-8.24 | dashes | p.9 |
| 8.25-8.27 | Input code number | p.9; selects the conversion routine by digit selection (p.131 Box 4) |
| 8.28-8.31 | Input unit number | p.9 |
| 8.32-8.47 | dashes | p.9 |
| 8.48-8.63 | Input: unit records per I-O command | p.9; the blocking factor (p.131 Boxes 5, 6). Disk: multiplied by words per card for the read word count (p.131). |
| 9.00-9.17 | Listing: relative arc number | Must be set by the pre-processor. Last in chain: via System Output. Otherwise disk beginning in the relative arc given, or System Output, as word 9 says (p.9, p.167). |
| 9.18-9.24 | dashes | p.9 |
| 9.25-9.27 | Listing code | p.9 |
| 9.28-9.31 | Listing unit | p.9 |
| 9.32-9.39 | Lines per page of listing | p.9; OEDIT's physical line count (p.165) |
| 9.40-9.47 | dashes | p.9 |
| 9.48-9.63 | Listing: unit records per I-O command | p.9 |
| 10.00-10.17 | Binary: relative arc number | Must be set by the pre-processor (p.9) |
| 10.18-10.24 | dashes | p.9 |
| 10.25-10.27 | Binary code | p.9 |
| 10.28-10.31 | Binary unit | p.9 |
| 10.32-10.47 | dashes | p.9 |
| 10.48-10.63 | Binary: unit records per I-O command | p.9 |
| 11.00-11.17 | Intermediate File 1: relative arc number | Always on disk; half word used; 11.18-11.63 dashes (p.10) |
| 12.00-12.17 | Intermediate File 2: relative arc number | Same (p.10) |
| 13.00-13.17 | Intermediate Name File: relative arc number | Same (p.10) |
| 14.00-24.63 | dashes | p.10 |

Binary destination cases (p.9):

| Situation | Binary goes to |
|---|---|
| Last in chain, compile and go | Disk beginning in relative arc 0. If a punch option exists in COMREC, also via System Output. |
| Last in chain, compile only | System Output |
| Not last in chain | Disk and System Output |

The bit that is the "punch option" is UNSPECIFIED (p.9 names no bit). Word 10
"as specified" for the not-last case: p.163 On Exit 2.

### 1.3 Behaviour at the ends of the assembly

- If STRAP II finds it is first in the chain it sets word 8 itself: System
  Input, card code, blocking factor one, `Spool0` on (p.131 Boxes 1, 9). If
  word 8 indicates System Input, `Spool0` is turned on (p.131 Boxes 2, 7).
- 8.00-8.17 is saved in word 0 of the input buffer (p.131 Box 3).
- Starting arc of the name file = (word 1's arc count) - 1. Available arcs are
  divided 1/32 to the name file, 31/32 to the intermediate file (p.131 Box 8).
- At the end, the data in word 9 is placed in word 8, with "bits 00-18"
  [printed; §14 C1] containing the relative arc number of the last arc of
  listing (p.11). The end-of-assembly procedure updates the Communication
  Record with where the documents are, then gives MCP control (p.36).

### 1.4 COMREC error messages (p.179)

See §9.4. A bad input word terminates; a bad listing or binary word falls back
to System Output.

---

## 2. Output on disk

### 2.1 Header index word (p.10)

The first word of each arc written is an index word:

| Bits | Contents |
|---|---|
| 0-17 | Relative arc number where the current output is continued |
| 18-19 | Not used |
| 20 | On: present record is binary code |
| 21 | On: present record is A6 code |
| 22 | On: present record is A8 code |
| 23 | Not used |
| 24 | Off: present record is listing. On: binary output |
| 25 | On: last record of the type of output specified by bit 24 |
| 26 | On: present record is IQS code |
| 27 | Not used |
| 28-45 | Number of unit records per arc (lines per arc, cards per arc) |
| 46-63 | Listing arc: relative arc number of the previous arc of listing |

The second word of each record is a "dummy" word. Data begins in the third
word (p.10; "starting at word 2", pp.163, 167).

The first block of listing and of binary go in the arcs specified (p.10).
Succeeding arc numbers are in word 0 bits 0-17, the count in 28-45, bit 25 on
the final arc (pp.163, 167). Next free arc for either output comes from
`Oarcx`, which is stepped (pp.163, 167). End of listing: bit 25 of word 0 set,
count = (max lines - 1) - blocking count (p.167 Box 16).

### 2.2 Layout (p.11, Fig. 2)

From relative arc 0 upward: interspersed binary and listing records, in records
of arc length. From the top of the disk downward: the name file first, then the
intermediate expanded unit files. Listing and binary are left "sandwiched"
(p.11).

Words per arc and arcs per disk are UNSPECIFIED in the pages read.

---

## 3. The expanded instruction unit

One per statement. A record at least eight words long: a control word and seven
fixed words. Then the coded expressions (or special configurations, as for
PUNSYM), then the print image of the statement field (p.12). All units use the
same memory area while being processed, so a unit is reachable only then (p.12).
Absolute address of the current unit: value field of $6 in Pass 1, of $3 in
Pass 2 (p.12, p.175).

### 3.1 Control word (Fig. 15 p.90, Fig. 20 p.189)

| Bits | Contents |
|---|---|
| 0-17 | Address of next word (beginning of format, p.90) |
| 18-24 | Zero |
| 25 | a: on if last control word |
| 26 | b: on if last control word in file |
| 27 | Zero |
| 28-45 | Number of words in unit: count field, next word available minus last control word `Icwa` (p.90 Box 1) |
| 46-63 | Address of next control word: refill field, from `Ibuffw` (p.90 Box 1) |

The end-of-file index word is of "particular format" (p.26), which is DERIVED to
be bit 26 on; p.26 does not say so.

### 3.2 Fixed portion (Fig. 20 p.189, Fig. 17 p.184)

Bit positions below were settled by measuring cell positions in a 220 dpi
crop of p.189; the tick labels alone are ambiguous by one on some rows. Cross-check:
ZIADAB, ZIADSY, ZILCFD, ZILSST, ZILPMS and ZIOPX come out as 25-bit fields ending at 24
or 56, matching the 25-bit signed counter values of Fig. 22, the 25-bit vle address of
Fig. 21, and SINB, SINI (BU,25) of Fig. 9; Fig. 15 p.90 anchors a = 25, b = 26.

**ZIADAB word**

| Bits | Name | Contents |
|---|---|---|
| 0-24 | ZIADAB | Absolute portion of the location counter, put here in Pass 2 |
| 25-31 | ZILBO | Length of binary output (unit not stated; §14 G7) |
| 32-56 | ZIADSY | Symbolic portion of the location counter, put here in Pass 2 |
| 57 | ZIFNME | c: name |
| 58 | ZIFP2 | d: DECODE gets unit |
| 59 | ZIFBO | e: binary output |
| 60 | ZIFDD | f: DD |
| 61-63 | | Zero |

**ZILCFD word**

| Bits | Name | Contents |
|---|---|---|
| 0-24 | ZILCFD | Length of coded fields, in bits (p.25) |
| 25 | ZIFDDS | g: explicit dds |
| 26 | ZIFPMN | h: P-mode |
| 27 | ZIFFLF | i: f.l. filled in |
| 28 | ZIFSFL | j: symbolic f.l. |
| 29 | ZIFBSF | k: b.s. filled in |
| 30 | ZIFSBS | l: symbolic b.s. |
| 31 | ZIFDSF | m: dds filled in |
| 32-56 | ZILSST | Length of symbolic statement, in 8-bit characters (p.25) |
| 57-63 | ZINXBO | Number of extra words of binary output |

**ZILPMS word**

| Bits | Name | Contents |
|---|---|---|
| 0-24 | ZILPMS | Length of P-mode symbol |
| 25 | ZIFALL | n: nothing left for DECODE |
| 26-27 | | Zero |
| 28-31 | ZINAME | Name check digit (0-9, p.173) |
| 32-49 | ZINFLD | Number of fields |
| 50-62 | ZIDDS | Dds information (13 bits; §4.6) |
| 63 | | Separate cell, unlabeled: UNSPECIFIED |

**ZICDID word**: bits 0-63 card ID in absolute form (a tick at 32 only).

**ZIOPX word**

| Bits | Name | Contents |
|---|---|---|
| 0-24 | ZIOPX | Location of operation question bits |
| 25-29 | | Error flags (five; "five error symbol flags" pp.34, 36) |
| 30 | | p: suppress e.m.: the sixth flag, on when the suppress character `($)` appeared before the instruction (p.25) |
| 31-63 | | Zero |

Six flags are ORed into each unit after Pass 1 and after Pass 2a, from an
intermediate flag buffer (p.25). p.25 says the first five denote a symbol
undefined, multiply-defined without contradictions, circularly defined or defined
in terms of an error symbol: that names four kinds for five flags. At the end of
Pass 1 only the sixth can be on (p.25). p.157 Box 2 names undefined, multiply and
pseudo-defined symbols and contagious errors. Which bit is which is UNSPECIFIED.
See §14 C8.

**ZIOTPT word**: bits 0-63 binary output.

**ZICOMM word** (last fixed word; Fig. 17 and table pp.184-185)

| Bits | Contents |
|---|---|
| 0-17 | ZICOMM: number of named common for the address from an address field |
| 18-23 | Zero, to force a full word address |
| 24 | 0 address not to be relocated; 1 to be relocated |
| 25 | 0 address to be relocated is from an address field; 1 from a refill field |
| 26 | 0 relocate as a lower address; 1 as an upper address |
| 27-31 | Not used (drawn zero) |
| 32-49 | Number of named common for the address from a second address field or a refill field of a full word instruction |
| 50-55 | Zero, to force a full word address |
| 56, 57, 58 | As 24, 25, 26, for the second address |
| 59-63 | Not used (drawn zero) |

Fig. 20's six rows plus this word are the seven fixed words of p.12. p.184 says
the word "had to be added", and Fig. 20's title says "not including relocation
fields": no conflict.

p.157 Box 12 says the binary output is picked up "from word 5 of the
instruction unit". That matches ZIOTPT only when counting the fixed words from
ZIADAB = 0, which is DERIVED.

### 3.3 Order of the variable portion (p.12, pp.23, 25-27)

After the initial eight words: (1) the dds coded expression, if the data
description could not be evaluated; (2) the coded expressions for the address
fields, in statement order; (3) the print image of the statement field, inserted
after all fields are analysed, at a full word location, with its count of 8-bit
characters in ZILSST. ZILCFD is the bit length of the encoded fields, so
statement characters = unit + size of fixed format + ZILCFD (p.25 Box 44). Except
for a comment or a B-type card block, blanks after the last non-blank do not go in;
the semicolon is removed from the print image (p.25 Boxes 42, 43). A dds coded expression evaluated in Pass 1 is
erased by resetting `Ibuffw`, unless the dds has a general parenthetical entry
on a DD, in which case it stays for OUTPUT (p.23).

P-mode: the P-mode symbol's characters are the dds coded expression, and its
length is in ZILPMS (p.23). The name is not in the unit; it is in the name file
(p.12).

### 3.4 Field reuse by statement type

| Statement | Field | Use | Page |
|---|---|---|---|
| DD | ZIOTPT.32 | `Ibuffw` setting: where the DD's coded expression/binary is placed in the unit | pp.26, 100 |
| DD | ZIOTPT bit 25 | On: numeric DD. Set by MQDD | p.158 |
| Numeric DD | variable portion | Fig. 26 (§3.6); Pass 1 binary is double precision floating, normalized except Fn-type, unnormalized | pp.26, 100 |
| Alphabetic DD | ZINFLD | Count of characters in the D field | p.102 |
| Alphabetic DD | ZIOTPT 0-23, 24 | Byte size symbolic: 0-23 number of characters, bit 24 = 0. Absolute: 0-23 number of bits in D field, bit 24 = 1 | p.102 |
| Alphabetic DD | ZIOTPT.26 | 0 entry mode A, P or IQS; 1 CC | p.102 |
| Alphabetic DD | ZIOTPT.27 | 1: OUTPUT may have to truncate the DD message's characters | p.102 |
| Multi-field DD | ZINFLD | Number of units | p.158 |
| DD, DR | ZIOTPT | Final binary output length, kept here rather than in ZILBO | p.34 |
| DR | ZIOTPT | Location of the basic vle dimension entry | p.27 |
| DR | ZIOTPT value field | Final product of dimensions as a negative number; the sign says computed | pp.27, 32 |
| PUNID | ZIOTPT value field | Location of the ID, stored in the unit's work area, blank-padded to eight | p.27 |
| REM, SEM | ZIOTPT value field | Location of a four-word mask in the variable part. Bit per numbered message; 0 restore, 1 suppress | p.32 |
| PUNSYM | variable part | Each symbol preceded by an 8-bit character count; always directly after the fixed format | pp.32, 115 |
| IOD | ZILPMS | Reference number (binary counter) | pp.97, 148 |
| IOD, REEL | ZIFP2 off, ZIFALL on | NMCP, not DECODE, handles them | p.97 |
| IOD, REEL | variable part | 80-column A8 card image; reference number and exit-address fields are filled by NMCP in A8 | p.148 |
| SYN | fields moved | dds coded expressions and address coding go to `Msyte`, not the unit; ZIFALL off, ZIFP2 off | p.27 |
| SYN | counter fields | Pass 2 puts bit and integer values into ZIADAB/ZIADSY with the five error flags; dimension reference also | p.36 |
| LINK | ZIOPX | Changed to address the op index of an LVI; coded expr of `LVI, 15, $+2`; ZIFBO, ZIFALL, ZIFP2 on | p.32 |
| Phoney symbol | | See §4.7 | p.204 |

Where the extra binary words counted by ZINXBO sit is UNSPECIFIED in the pages
read (§14 G7).

### 3.5 Binary skeleton fill

The op-question string's first 24 bits hold the address of the first fill control
word (p.22). Fill words: value field = address of INSERT subroutine; count field
= number of coded expressions given to it (one except INDMK and LVS); refill
field = next fill word (p.144). The INSERT subroutines and their error-flag
rules are listed on p.144. Example fill list for a VFL op:
`XW, S24A, 1, $+1; XW, SOFF, 1, 0`; and for LVS:
`XW, SJFLD, 1, $+1; XW, SBIT, 16, 0` (p.144).

### 3.6 Numeric DD entry (Fig. 26 p.193)

Repeated per field while e = 1.

| Order | Width | Contents |
|---|---|---|
| a | 1 | 1 numeric DD in Fn entry mode; 0 not |
| (a=1 only) | 11 | Fraction length |
| exponent | 12 | Exponent |
| fraction | 96 | Fraction |
| sign | 8 | Sign byte |
| b | 1 | 1 normalized mode; 0 not |
| c | 1 | 1 special exponent present; 0 not |
| special exponent | 12 | Drawn in every row |
| d | 1 | 1 has general parenthetical integer entry (G.P.); 0 not |
| G.P. | 6 | If d = 1, followed by a coded expression for the G.P. |
| e | 1 | 1 format repeats for another field; 0 end of the encoding |

Whether the special-exponent and G.P. fields are present when c or d is 0 is
not stated in the figure (§14 C6). Absent data: a GP with no data stores a zero
coded expression (p.100). Null dds: BU for alphabetic DD's, N for others
(p.100).

### 3.7 Dimension entry (Fig. 27 p.194, Fig. 22 p.191)

Vle form: `0 | 13 total length of vle | 6 D-A6 | dimension information`. Unit
form: the dimension information alone.

Dimension information:

| Form | Layout |
|---|---|
| Primitive | 5 number of D's; bit 0; then coded expressions for D1 ... D(n-1), 24 bits minimum each; then garbage if needed |
| Evaluated | 5 number of D's; bit 1; then 24-bit fields; then garbage if needed |

Footnotes (p.194): total primitive length is padded to at least 24(n-1)+6 bits
to allow conversion; after conversion the excess is garbage. VALUE performs the
transition when the dimension reference is required. Product contents: §14 C7.

---

## 4. Symbol table and other managed tables

### 4.1 Table control block (Fig. 8 p.44, table p.45)

| Field | Symbol | Rel. loc. | Bits | Contents |
|---|---|---|---|---|
| FX | `Azfx` | 0.0 | 64 | Index word referring to the function part of an entry |
| DX | `Azdx` | 1.0 | 64 | Index word referring to dictionary location |
| FW | `Azfw` | 2.0 | 24 | Location of first entry; half-word address |
| ID | `Azid` | 2.25 | 6 | Identification |
| LW | `Azlw` | 2.32 | 24 | Location of last entry; half-word address |
| TO | `Azto` | 2.57 | 1 | Type of table: 0 ordered, 1 unordered |
| TM | `Aztm` | 2.58 | 1 | Table delete mark |
| TEC | `Aztec` | 2.62 | 1 | Type of compare (values UNSPECIFIED in the pages read) |
| EL | `Azel` | 3.0 | 16 | Length of fixed entry in dictionary (filled in by subroutine) |
| AL | `Azal` | 3.16 | 16 | Length of argument in dictionary |
| ADDL | `Azaddl` | 3.32 | 16 | Length of function in dictionary |
| N | `Azn` | 3.48 | 16 | Number of undeleted entries in dictionary |

Bits 2.31, 2.56, 2.59-2.61, 2.63: drawn zero or unlabeled (p.44).

### 4.2 Universal control block (p.45)

| Field | Length | Contents |
|---|---|---|
| `Auvtab` | 24 of half word | Word addressed contains first available bit location of the vle table (built upwards) |
| `Auvbot` | 24 of half word | Lowest bit address usable in the vle block |
| `Autcb` | 18 of half word | Location of first table control block |
| `Aunt` | 18 of half word | Number of table control blocks, including any marked for deletion, unless at end |

Dictionary parts of different tables are in non-adjacent storage; vle portions
of all tables share one consolidated block. A vle's address is in the last 25
bits of the dictionary function (p.44). Search: linear under seven entries,
binary from seven (p.45 Box 7).

An entry has one of three forms: argument and function in the fixed portion, no
vle (MIBA table); argument fixed, function in vle (STRAP special symbol);
part of the argument fixed, rest of the argument and function in vle (input
symbol) (p.44).

Vle-only entries (no dictionary part): hi-lo; old vle portion(s) of a symbol
multiply defined with no contradictions; a dimension entry in addition to its
symbol entry for a name on a DR, DRZ or SYN (p.13). Each dictionary entry of the
symbol table must have a vle (p.13). Unordered material with an ID character is
fetched by linear search; alphabetically ordered material by binary search
(p.13).

### 4.3 Dictionary entries (Fig. 21 p.190)

Each starts with bit 0, the delete indicator (0 not deleted), and bit 1, the vle
indicator (1 there is a vle).

| Table | Bits 0, 1 | Argument | Function |
|---|---|---|---|
| Symbol | 0, 1 | 64: first eight characters of the name | 25: signed address of its vle |
| `$` or internal special symbol | 0, 1 | 64: 2^8-1, then n, then 0. n = 0 for `$` itself | 25: as above |
| Tail | 0, 0 or 1 | 32: first four characters of the tail | 25: signed vle address if tail > 4 characters; number of the tail if <= 4 |
| 7030 indicators | 0, 0 | 32: mnemonic | 6: number (0-63) |

Special symbol: 24 bits, first eight bits all ones, remaining sixteen determined
when made. `111111110000000000000000` is the one for a programmer's `$`
(p.205). Three A8 characters, the first all ones (p.13). The width of n and the
rest of the 64: §14 C9.

The figure does not give the character used to pad short names. Blanks are
UNSPECIFIED for the dictionary (they are stated for the system-symbol collection
buffer, p.75, and for IDs, p.27).

### 4.4 Vle entries (Fig. 22 p.191)

Common head: bit 0 delete indicator, then 13 length of this entire vle, then 6
ID in A6 code.

| Kind | ID | Layout after the 20-bit head |
|---|---|---|
| Symbol remainder | S | 12 length of the rest, if any, of the name; 8n rest of the name; 231 minimum function |
| Internal special symbol | Y | 12 = 0; 231 minimum function |
| Tail remainder | T | 12; 8n rest of the tail; 8 number of the tail |
| Evaluated dimension | D | 5, then evaluation indicator bit = 1; then products n1, n1 x n2, n1 x n2 x n3 ... |
| Hi-lo | H | 25 signed value from absolute counter; 25 signed value from symbolic counter |

The function portion's format is "defined by the ZST... bits" (Fig. 22). p.135
Box 8 confirms the order: delete mark, length, ID, length of the remainder,
remainder, function. Data moved from the unit to the entry includes the length of
binary output, coded expressions for a P-mode dds on a still ambiguous op, explicit
dds of a DD or the coded expression for a symbolic dds, and the coded expression for
a DR's dimension (p.25). DDI and SYN must each have a name (p.25).

### 4.5 The function portion: catalogue of ZST names

**The 231-bit layout is UNSPECIFIED.** No figure or table in the guide gives it,
though p.13 says it exists. Appendix D says only that `ZST...` are SYN's giving
relative locations (p.202). What the guide does give:

| Name | Meaning when on | Page |
|---|---|---|
| Zst0 | Everything defined and computed (value, dds, dimension) | pp.135, 137 |
| Zst1 | Symbol undefined | p.170 box 4 |
| Zst3 | Existence of dds reference address has been decided | p.135 |
| Zst4 | Circularly defined | p.170 box 16 |
| Zst10 | Mode known | p.137 |
| Zst11 | Field length established | p.137 |
| Zst12 | Symbolic field length exists | p.137 |
| Zst13 | Paired with Zst36 to decide common relocation (printed "Zstl3") | p.185 |
| Zst14 | Byte size established | p.137 |
| Zst15 | Symbolic byte size exists | p.137 |
| Zst17 | Processing bit for mode; on during processing means circular | p.135 |
| Zst22 | Multiply defined, no contradictions | p.170 box 12 |
| Zst23 | Multiply defined with contradictions | p.170 box 14 |
| Zst24 | Symbol used; P-mode look-up turns it on | pp.140, 170 |
| Zst26 | Real value computed and entered | p.137 |
| Zst32 | Use the dds reference address (only if dds is implicit) | p.135 |
| Zst35 | 0 location counter dependence not decided; 1 decided | p.185 |
| Zst36 | 0 location counter dependent; 1 not | p.185 |
| Zst37 | Marked to be punched (turned on by NPNSYM) | p.168 |
| Zstcom | 0 relocate as lower address; 1 as upper address relative to Zstcon | p.185 |
| Zstcon | 0 blank common; otherwise number of named common (18-bit, p.186) | p.185 |
| Zstcnt | Field holding the name's check digit | p.173 |

The numbered bits are DERIVED to be single-bit positions at their numbers, from
the naming only. p.203 says the Zst bits also hold a "dds reference address"
(address of explicit data description to be used) and a "dimension reference
address" (the count position of the dimension information, usually further out
in the same entry); widths and positions are UNSPECIFIED. Also present but
unplaced: the settings of $4 and $6 (pp.13, 203), symbolic error flags, and the
value or coded expression of the symbol (p.13). The 231 minimum is the only size
given.

Relocation rule (p.185): when Zst13 is on and Zst36 is off, look at Zstcom. Zero
means relocate as a lower address; on means relocate as an upper address relative
to the common numbered in Zstcon. Data following an SLCRCOM: Pass 1 sets Zstcom =
1 and Zstcon to the common number.

### 4.6 System symbol table (Fig. 25 p.193)

| Width | Contents |
|---|---|
| 64 | System symbol without the `$` (argument) |
| 24 | Location |
| a | 0 location is the machine location; 1 an address within STRAP II of the floating point constant |
| b | 0 available at this installation; 1 not |
| 13 | DDS information: c, d, e are the mode, then F.L., then B.S. |

Mode bits: c 0 floating, 1 not; d 0 unnormalized or unsigned, 1 normalized or
signed; e 0 decimal, 1 binary.

**DERIVED**: F.L. is 6 bits with 0 meaning 64, B.S. is 4 bits. Fig. 29 (p.201)
gives the system-symbol dds as `101 000000 1000` labelled BU, 64, 8. It agrees
with ZIDDS's 13 bits and App. C's "13 bits of data description". This is one
worked instance, not a general statement.

The contents of the table are UNSPECIFIED; only `$LZC` is given as (BU, 7, 8)
(p.207). `$X2`, `$X3` appear in Fig. 29 at 18.0 and 19.0.

CPLTNM's output: prefix `110` then the 24-bit value, at accumulator offset 64 (Fig. 12
p.71). CPLTSY's output: datum prefix `11100` and the 24-bit value in the accumulator at
offset zero; sign byte `0000S000`, S = 0 regular system symbol, S = 1
mathematical constant (Fig. 13 p.75, caption [printed] "CPLTNM's", list of
illustrations p.6 assigns it to CPLTSY). For a lone `$`: 7 zero bits, then
`00101011` for the `$`, then 8 zeros, 8 zeros, a zero bit; `Bsymbx` left at that
last bit (Fig. 14 p.76). Also the DDS goes in `Cpldds` (p.75).

### 4.7 Op tables (Figs. 23, 24 p.192)

| Row | Non-ambiguous | Ambiguous | Pseudo |
|---|---|---|---|
| 0-63 | Mnemonic, 8 characters | Mnemonic | Mnemonic |
| Skeleton | 0-63 skeleton | 0-31 floating skeleton; 32-63 last half of VFL skeleton | none |
| Location | 0-23 location of op index | 0-23 location of op index | 0-23 location of op index; 32-50 digit-select pseudo op number |

Each caption says "Two Word Format" though three rows are drawn (§14 C10).

An ambiguous op is processed as floating until diagnosis of the dds or address
proves otherwise (p.22).

Secondary op entry (Fig. 24): word one is an 8-bit code byte `00000abc`, then
56 bits of mnemonic; word two is the skeleton. abc: 000 -; 001 secondary op in a
VFL instruction; 020 [printed] SEOP; 100 secondary op in the CW instruction. A
secondary mnemonic can be at most seven characters. The code comes from the
current op index (p.22). So `+(BU, 3) (SEOP)` and `CW (V+I)` look up as
`1SEOPbbb` and `4V+Ibbb` and fail (pp.22-23).

Op index (pp.22, 204): location of fill words (first 24 bits); masked yes/no
question bits; a code number if the op takes a secondary. Named question bits:
`Zoddsa` dds needed (p.140), `Zoimm` immediate VFL (p.22), `Zopo` pseudo-op
(p.140), `ZOREEL` REEL card (chart p.147). An MCP op has a special bit in its op index
(p.97). The table contents and the bit assignment are UNSPECIFIED (p.202 says
only that `ZO...` are relative locations). BOPSER's control block is Fig. 11
p.67: 0-23 test word address, 24-26 narrow cells (one is BOPSER's indicator; which is
not labelled), 27 zero, 28-45 bit length of an entry, 46-63 number of entries, then
`DRZ(BU), N` where N = ceil(log2(entries)), holding the increment-decrement pairs. The
table must be ordered, test word 64 bits, entry at least 64 bits (p.67).

Pseudo-op number: "three different phases" branch on it by digit select (p.22).
Three-digit select pseudo-op tables hold the pseudo-ops of App. B (p.196 note 3,
p.36). Their numbering is UNSPECIFIED.

### 4.8 Phoney entry, pseudo-defined symbols

A name on an op that produces no binary, and is not an MCP op, SYN, DR or DDI:
a "phoney" or specially marked entry, the instruction gets an error message, and
a reference gets the location counter of the next instruction (p.204). UITER
ignores phoney entries; a REEL's name is one (p.97). How it is marked is
UNSPECIFIED.

Undefined symbol: dds (N), location the next available full word above the
upper limit of the assembled program (p.205). Entries of undefined type are made
by VALUE once UITER has turned on its indicator after Pass 1 (p.32).

Symbol kinds (pp.205-206): undefined, unused, multiply defined without
contradiction (`RAT SYN, 5` / `RAT SYN(BU, 32), 5`), multiply defined with
contradictions (`DOG LX, 5, CAT` / `DOG SX, 5, MONKEY`), circular (`A SYN, B+2`
/ `B SYN, A`), contagious.

### 4.9 Tails

The tail number string has ten 8-bit bytes, one per level, preceded in MQTAIL's
table by an A8 asterisk, "an illegal character for a symbol". A tail is appended
as up to eleven A8 characters (`*, n1 ... n10`) (p.125). n = number of levels in
effect. Zero field = no tail at this level (p.75, p.125). Conflict on the mark
character: §14 C11. Tails live in their own table with their own control block
(p.32). Error 83 limits the appended length (p.177).

### 4.10 Name file (GNLOAD p.88, NAMEIN p.161)

Separate from the symbol table; on disk; not in memory during all passes (p.79).

| Item | Contents |
|---|---|
| 1st byte | Number of A8 characters in the name + one for the check character |
| 2nd byte | Check character; progresses 0-9 and repeats |
| next n bytes | Name in A8. A name under eight characters is assumed eight long |
| End of buffer | Byte of all ones |
| End of file | Byte of all zeros |

Two buffers; the terminating arc is written as end of file (p.88). NAMEIN checks
the count against 128 and on exhaustion sets bit 25 in `Namexw`; value field of
`Namexw` holds the address of the check character (p.161). OUTPUT compares this
with ZINAME; see errors 12-14. Only the first 50 characters of a symbol are
printed in the symbol lists (p.172). `$00` is entered at the end of Pass 1
(p.26).

---

## 5. Coded expressions (Appendix C, pp.197-201)

A bit string, not word aligned. Grammar checked by a throwaway parser against
Figs. 28 and 29; §5.5.

### 5.1 Prefix (p.197; p.58 Box 8, Box 14)

First bit 1 = expression exists. Bits two to four:

| Prefix | Name | Following |
|---|---|---|
| 1000 | Normal | Data list, ended by a 0 after the last datum's own terminating 0; operator list, ended by 0; whole expression ended by a 0. Operators in the order they are performed |
| 1001 | Special index | Three more bits, then the normal encoding; result is an index with basic value 0. The three bits are UNSPECIFIED |
| 1010 | Padded | Normal encoding, then after its last 0 an arbitrary number of 1's and a final 0 |
| 1011 | Special signed value | 25-bit value including sign, then padding as above |
| 1100 | Super special | Normal encoding: "normal case finished by DECODE". Tells DECODE the information has been used |
| 1101 | Fully evaluated | Two full words (128 bits) in the format of VALUE's output (§7) |
| 1110 | Long prefix | Three more bits |
| 1110000 | Integer value | Normal encoding; a non-zero bit part is added to the integer part with an error message |
| 1110001 | Absolute | Normal encoding; values set positive after computation |
| 1110010 | Absolute integer | Integer, then absolute |
| 1110011 | 17-bit constant | 17-bit number used for I value, S/X portion taken as S, and padding. Internal to VALUE |
| 1111 | Null | In subscript position after a datum: terminates the datum, same as a single 0. As a field: null field, with padding as in padded/signed; ends at the first 0 |

Null field in GETFLD: prefix stored and $2 spaced six bits (p.85). A zero 1A means
no expression.

### 5.2 Datum (pp.197-198)

First bit 1 = datum exists.

| Prefix | Name | Following |
|---|---|---|
| 100 | Symbolic | 7-bit number of A8 bytes, then the symbol in A8 |
| 110 | Absolute | 24-bit binary number, as integer part |
| 101 | Sub-expression | A coded expression whose values are used |
| 111 | Long prefix | Two more bits |
| 11100 | System symbol | 24-bit binary number as bit-style part, then 13 bits of data description |
| 11101, 11110, 11111 | Not used | |

After a symbol or system symbol come subscripts and index (item 2E). Subscript
follows the symbol it refers to. An index is encoded like a subscript, after the
last datum and before the operators (p.198); in Fig. 29 `($X2+3.0)` is so placed,
after the subscript on `7`, the last datum (§5.5).

### 5.3 Operator (p.198)

9 bits: 1, then 3-bit code, then 5-bit datum number after which it follows.

| Code | Operator | Context |
|---|---|---|
| 111 | `.+`, a `.` | as in `2.3`, `A.B` |
| 110 | `.L`, a `.` left | as in `2.`, `2.+3` |
| 101 | `.R`, a `.` right | as in `.2`, `2+.3` |
| 100 | `U-`, unary minus | as in `-7`, `A*-2` |
| 011 | `*` | |
| 010 | `/` | |
| 001 | `+` | |
| 000 | `-` | as in `2-3`, `A-2` |

Priority: more parentheses = higher; within a pair, essentially table order
(p.199 note 4). Compare p.204's stated order (§14 C12).

### 5.4 Items (p.198)

| Item | Bits | Contents |
|---|---|---|
| 1A | 1 | 1 expression exists; 0 no (more) expressions |
| 1B | 3 | Type (normally 000) |
| 2A | 1 | 1 datum exists; 0 no (more) data |
| 2B | 2 | 10 absolute; 00 symbolic |
| 2C | 24 or 7 | Absolute value, or length of 2D in bytes |
| 2D | variable | Symbol in A8 |
| 2E | 1 | 1 coded expression(s) for symbol subscript exists; 0 no (more). "Subscript" may be index |
| 2F | variable | Coded expression for the subscript |
| 3A | 1 | 1 operator exists; 0 no (more) |
| 3B | 3 | Operator code |
| 3C | 5 | Datum reference number |
| 4A | 1 | 1 `(.n)` entry follows; 0 no (more) |
| 4B | 6 | n, binary |
| 4C | variable | Coded expression to be ORed in |

Notes (p.198-199): 2E and 2F repeat for each subscript until 2E = 0. 2A through
2E(F) repeat until 2A = 0. 3A-3C and 4A-4C repeat likewise. **2E is 1A of the
inner expression** (the "cereal box", p.199 note 2): a 1 in 2E is also the
expression's first bit. A 0 in 4A is equivalent to a 0 in 1A of "its own coded
expression" (note 5).

**A subscript's expression has no 4A.** DERIVED from Figs. 28-29: the subscripts
end at the operator-list 0, and the next bit is the enclosing 2E; the top level
has a further 0, labelled "No G.P." or "End".

A G.P.: 1, six bits N, then a coded expression ORed into the field; it follows
the operators (p.198). If a GP is allowed and none follows, the bit at the end
is set to 0 (p.85 Boxes 37, 46). GP heading stored, $2 spaced 8 bits (p.85 Box 38),
which is DERIVED to be the 1 and the 6, and the 1 of the next expression's 1A.

### 5.5 Test vectors

A throwaway parser of §5.1-§5.4 consumed each vector below exactly, with no bits left
over and all terminators in place, which is the check on the rule that subscripts lack 4A.
The transcription of the elided bytes was filled only for that check.

Figure 28 (p.200), `((JOE - 1)/4.)*4+1).` [printed; parentheses unbalanced]:

```
1000 100 0000011 00100001 00100110 00110101 0
110 000000000000000000000001 0
110 000000000000000000000100 0
110 000000000000000000000100 0
110 000000000000000000000001 0
0
1 000 00001
1 110 00011
1 010 00010
1 011 00011
1 001 00100
1 110 00101
0
0
```

208 bits. Data: JOE, 1, 4, 4, 1. Operators in execution order: `-` after 1st,
`.L` after 3rd, `/` after 2nd, `*` after 3rd, `+` after 4th, `.L` after 5th.

Figure 29 (p.201), `+(BU,2+7*3,8-3*2), PEACHES CREAM OF WHEAT +7.(3-6*18)($X2+3.0),
MILK-CREAM ($X3+7)`. Spaces are mine; `[...]` is elided in the print.

Field beginning `PEACHES`:

```
1000 100 0010011 [PEACHESCREAMOFWHEAT: 00100111 ... 00010011] 0
110 [7, 24 bits]
1 000 110 [3] 0 110 [6] 0 110 [18] 0 0
      1 011 00010  1 000 00001  0
1 000 11100 [18.0, printed 00...010010000000; label 22.0] 101 000000 1000 0
      110 [3] 0 110 [0] 0 0
      1 111 00010  1 001 00001  0
0 0
1 111 00010
1 001 00001
0
0
```

447 bits with the 19 bytes. Length `0010011` = 19: **embedded blanks are not in
the symbol**, as p.205 says of a symbol.

Field beginning `MILK`:

```
1000 100 0000100 [MILK: 00100100 ... 00100010] 0
100 0000101 [CREAM: 00110011 ... 00100100]
1 000 11100 [19.0, printed 00...010011000000; label 23.0] 101 000000 1000 0
      110 [7] 0 0
      1 001 00001  0
0 0
1 000 00001
0
0
```

196 bits. The labels 22.0 and 23.0 are octal for the printed bit patterns 18.0 and
19.0 (DERIVED). The source line gives these data as `$X2` and `$X3`; the guide does not
otherwise state their locations.

No coded expression is shown for the `(BU,2+7*3,8-3*2)` field. The figure starts
at `PEACHES`.

A8 codes shown by the figures: `J` 00100001, `K` 00100010, `M` 00100100, `O`
00100110, `P` 00100111, `T` 00010011, `C` 00110011, `E` 00110101, `$` 00101011.
No A8 or A6 table is in the guide (§14 G3).

### 5.6 Other things carried as coded expressions

Tails: not. Unit dds: §3.3. Stored in Msyte: SYN (p.27). Special symbol function:
"SYN-like coded expression" for $6 + $4, (p.13, p.34).

---

## 6. Field syntax rules relevant to encoding (Appendix F, p.207; p.204)

- An index, if used, must be the last entry in the field. `B, JOE+1.32($3)` not
  `B, JOE($3)+1.32`.
- A subscript must immediately follow its symbol. `BB, JACK(1,2)+.32, BILL` not
  `BB, JACK+.32(1,2), BILL`.
- A gp must follow all other type information. Index and gp cannot share a field:
  illegal `L, JOE($2)(.31)3`; legal `L, JOE(.63)2(.31)3`; legal
  `L, JOE($2),0(.31)3`.
- A gp cannot be the first entry in a field. `.n` must be absolute; the pattern
  may be absolute or symbolic. Not inside other parentheses except a DD's data
  description.
- Symbol-table entries are made for all statement names, even if not meaningful
  (SKIP, TAIL, ...). Implied multiplication is not allowed.
- Radix in an 'address' field of a numeric DD: leading-mode radix applies if none
  is before the first operand; one before the first operand overrules it for that
  field; otherwise radix 10. A gp on the FL or BS of a DD ORs into each data field:
  `DD(BU, 32(.6)7), 0, 1, 2, 3, 4`.
- P-mode: `L(P, $LZC), ALPHA` assembles with dds (BU, 7, 8).
- SYN, DR, DDI and DRZ cannot have a gp (p.204).
- An expression: constants and variables, subscripted or not, separated by operation
  symbols and parentheses, followed by an index or a gp but not both (p.204).
- dds types (p.205): explicit, `L(BU, 64), CONSTANT` is (BU, 64); implicit, from
  `CONSTANT DD(BU, 7), 7`, is (BU, 7); pseudo, an undefined symbol's (N).
- Floating point E and E+I get a dds of U from DECODE without an implicit or explicit
  dds (p.205).
- Default dds, DECODE: ambiguous, or clearly VFL: (BU, 64, 8); VFL immediate:
  (BU, 24, 8); floating only: normalized except E and E+I, unnormalized (p.140).
  Null dds on DR: (N, 64, 4) (p.27).
- Name: legal characters in cols 2-9 of a card block including embedded blanks;
  symbol: the same excluding them (pp.204-205). Continuation card has `*` in col 1
  (p.203). Radix 2-16 (p.26).

---

## 7. VALUE's output and work words

### 7.1 Output (Fig. 9 p.58)

| Word | Bits | Name | Contents |
|---|---|---|---|
| 0 | 0-24 | SINB | B value |
| 0 | 25-28 | | Unlabeled |
| 0 | 29 | SINSX | Subscript/index |
| 0 | 30 | SINRL1 | Relocation flag 1 |
| 0 | 31 | SINRL2 | Relocation flag 2 |
| 0 | 32-56 | SINI | I value (57-63 unlabeled) |
| 1 | 0-24 | SINDDS | DDS reference |
| 1 | 25-27 | SINM | Mode bits |
| 1 | 28-31 | SINX | Index |
| 1 | 32-56 | SINDIM | Dimension reference |
| 1 | 57 | SINMQ | Mode bits given |
| 1 | 58 | SINXQ | Index given |
| 1 | 59-62 | SINSER | Symbol error flags (4) |
| 1 | 63 | | Zero |
| 2 | 0-17 | SINCOM | Number of named common (Fig. 18 p.185) |
| 2 | 18 | SINUA | 0 lower address at exit from VALUE; 1 upper |
| 2 | 19-63 | | Not used, zero |

INSERT reads the values at `Sinb`, `Sini`, `Sinx` (p.144). INSERT checks the flags
after inserting: Sinrl1 = 1, Sinrl2 = 0, Sinua = 1 means INSERT puts the number in
`Sincom` at `Zicomm` of the unit (p.185).

### 7.2 Heading and work area (Fig. 10 p.60, Fig. 19 p.186)

Five-word heading before a work area. Field names and legend are on p.60; this
file records only the relocation word needed for format compatibility: fifth
word VVCOM 0-17, VINUA 18, 19-63 zero, same assignment as the third output word
(pp.185-186). Datum and subscript words in the work area are floating with exponent
0-11, fraction 12-59, and bit 63 = 0 datum, 1 subscript (p.60). VALUE's internals
are left to the logic chapter.

---

## 8. Errors: records and lists

### 8.1 Mechanism (pp.37-39)

Each detection makes a 32-bit entry in one of five lists: Pass 1, UITER, Pass 2a,
UITER, Pass 2b. All messages print at the end of the listing with page and line
and, as necessary, the address field (p.37). A detected error executes `EX, A`
where A is the address of a CW instruction; the execute exception interrupt goes
through MCP to ERR via `$15`'s table of exits; ERR's manipulation of the interrupt
location counter gives A; rank in `Errtab` is the message number (p.38).

| Record | Layout | Figure |
|---|---|---|
| Pass 1, 2a, 2b | 20 unit number; 4 field number; 8 number of error message | Fig. 3 p.38 |
| UITER | 24 location of symbol table entry; 8 zero | Fig. 4 p.38 |
| Initial, preceding each list | 24 number of errors, if any, which have not been listed; 8 zero | Fig. 5 p.38 |
| Final, for ERRPRT | 12 page; 8 line; 4 field; 8 number of error message | Fig. 6 p.39 |

UITER's Fig. 4 has zeros where a message number would be; §14 C13. ERRNUM matches
unit (lists 1, 3, 5) or symbol (lists 2, 4) against the current counter, with page
from the accumulator at offset 8 and line at offset 0, sets field to zero for lists
2 and 4, and puts those lists in chronological order (p.39). ERRPRT sorts into page
and line and prints; a message then states the errors not listed by exceeding the
buffer (p.158).

Counters: `Unit` (BU,20), `Field` (BU,4), `Symbol` (BU,24) (p.38). Unit starts at
one each pass and steps per unit: Pass 1 after INTOUT, 2a and 2b after INTIN.
Field: zero per unit, plus one per address field. Symbol: UITER, function address
of the vle being analysed; Pass 2, function address for the unit's entry, else
zero; Pass 1, always `Msyte` (p.173). Note MIOD increments Field an extra time
(p.97).

`Errtab` is ordered 64-bit control words, each locating a variable-length message;
`Errfwa` and `Errtop` bound each list (p.38). Serious messages have their words at
the head; `Esss` is the count (p.38). Serious = numbered 1-28 (p.205); these can
also go to the console typewriter via a Correction card (p.176, p.38). Serious text
and control words are in section A0, non-serious in A2 (p.174). Suppression: §3.4
REM/SEM four-word mask, major mask updated by the intermediate mask at each such
unit, in every pass (pp.32, 36).

Also: MACHER, `SIC, Machez; B, MACHER`. Location in message comes from `Machez`;
optional dump, of the current unit in Pass 1 and of the vle in UITER/Pass 2,
governed by an indicator STRAP defines as not-to-dump. In Pass 1 it returns to MAIN's
wind-up, not the user. In UITER it marks the vle completed (p.173). Phase indicators
`Fpass1`, `Fuiter`, `Fpass2`, `Fpass3`: on-settings are tabled on p.173.

Error-symbol flags are ORed into the unit, and print before the instruction on the
listing (p.34, p.157 Box 2). DECODE ORs VALUE's flags
into the intermediate mask (p.34).

Non-numbered listing lists, from NUNDSY pp.170-172: undefined symbols with address
immediately; then unused, multiply with contradictions, circular; unused also with
address; first 50 characters; SPNUS suppresses unused. Multiply defined without
contradiction gets a numbered message (p.172).

## 9. Error messages

**The condition is UNSPECIFIED beyond the message itself** unless a page is cited:
p.12 says write-ups generally do not mention which errors they detect, and that the
detecting logic area is what p.176ff gives. Messages are the ink; each prints its
number at the end. "Serious" is 1-28 (p.176 footnote). In the last column, a link from
another page to a number is DERIVED from subject and logic area unless that page gives
the message's own words: no page but p.176ff states an error number.

### 9.1 Numbers 1-45 (p.176)

| No. | Area | Message | Further condition text |
|---|---|---|---|
| 1 | MAIN | ILLEGAL OP CODE | Lookup, MIBA and MBSPEC all fail; unit set as `SIC, $15; BE, 0` (p.22). COMREC 7.42. |
| 2 | MAIN | ILLEGAL SECONDARY OP | COMREC 7.42 |
| 3 | MAIN | ENTRY MODE WITH NON DD OPER. | COMREC 7.42 |
| 4 | MAIN | MORE THAN ONE SECONDARY OP | COMREC 7.42 |
| 5 | MAIN | MORE THAN ONE DDS | COMREC 7.42 |
| 6 | NPS2 | PASS 2A AND 2B LOC. CTR. DO NOT AGREE | 2b checks 2a's counter on binary or later; on discrepancy the 2a setting is used (p.36). COMREC 7.42. |
| 7 | MACHER | ASSEMBLY ERROR | p.173; existence bit off (p.58 Box 13); UITER value not established in Pass 2 (p.137 Box 13). COMREC 7.42. |
| 8 | GETFLD | VLE SYMBOL TABLE EXCEEDED | |
| 9 | GETFLD | SYM. BUFF. HAS BEEN EXCEEDED | |
| 10 | GETCHA | GETCHA BUFFER FULL | |
| 11 | | SPARE | |
| 12 | OUTPUT | REACHED FLAG IN NAMEXW PRIOR TO END INSTRUCTION | Bit 25 of Namexw (p.161) |
| 13 | OUTPUT | FLAG NOT SET IN NAMEXW AT END INSTRUCTION | p.157 Boxes 31, 32 |
| 14 | OUTPUT | NAME CHECK CHARACTERS DO NOT COMPARE | Name file vs unit (p.173) |
| 15-17 | | SPARE | |
| 18 | MAIN | SYM TBL ENTRY MADE UNORDERED | |
| 19 | ANEXT | SYMBOL TABLE IS INCORRECT | |
| 20-28 | | SPARE | |
| 29 | MAIN | IMPROPER 1ST CHAR | |
| 30 | MAIN | MORE THAN ONE $ | |
| 31 | MAIN | ILLEGAL ENTRY MODE | p.180 condition 6 |
| 32 | MAIN | ENTRY MODE NOT CLOSED BY RIGHT PAREN | |
| 33 | MAIN | 2NDARY OP NOT CLOSED BY RIGHT PAREN | |
| 34 | MAIN | THIS OP SHOULD NOT HAVE DDS | |
| 35 | MAIN | DDS NOT CLOSED BY RT. PAREN | |
| 36 | MAIN | FIELD LENGTH GREATER THAN 64 | |
| 37 | MAIN | BYTE SIZE GREATER THAN 8 | |
| 38 | MAIN | BIT STYLE NO. IN DDS | |
| 39 | MAIN | NEG. FL OR BS HAS BEEN COMPLEMENTED | |
| 40 | MAIN | EXTRA FIELDS | |
| 41 | MAIN | SHOULD HAVE NO NAME | Phoney entry (p.204) |
| 42 | MAIN | STRAP ASSIGNED DDS | Default dds, DECODE (p.140) is a separate area; link not stated |
| 43 | MQS | SYN WITHOUT A NAME | |
| 44 | MQS | SYN WITHOUT AN ADDRESS FIELD | |
| 45 | MQDD | UNATTAINABLE VALUE | |

### 9.2 Numbers 46-95 (p.177)

| No. | Area | Message | Further condition text |
|---|---|---|---|
| 46 | MQR | DR OR DD WITHOUT DDS | |
| 47 | DNUM | CHAR ILLEGAL IN RADIX SPEC. | |
| 48 | DNUM | MORE THAN ONE POINT | |
| 49 | CPLTSY | SYMBOL IS TOO LONG | |
| 50 | DNUM | MORE THAN ONE E IN NUM. DD | |
| 51 | CPLTSY | MORE THAN 1 $ IN SYSTEM SYM. | |
| 52 | MDIMRF | MULTIPLE DIMENSIONS NOT IN PAREN | |
| 53 | OUTPUT | VALUE ROUNDED TO FULL WORD | |
| 54 | MDIMRF | DIMENSION NOT CLOSED BY RIGHT PAREN | |
| 55 | MPUNID | NO COMMA AFTER PUNID | |
| 56 | CPLTSY | NON-EXISTENT SYSTEM SYMBOL | Not in table, MBSPEC fails; or marked unavailable at this installation (p.75, Fig. 25 b) |
| 57 | OUTPUT | PSEUDO LOC. CTR. TOO HIGH | |
| 58 | MQTAIL | UNTAIL LEVEL MORE THAN TAIL | |
| 59 | MQTAIL | NULL TAIL | |
| 60 | MQTAIL | TAIL NOT CLOSED BY RIGHT PAREN | |
| 61 | MQTAIL | ILLEGAL TAIL LEVEL CHARACTER | |
| 62 | MQTAIL | ILLEGAL CHARACTER IN TAIL | |
| 63 | CPLTNM | DIGIT INCORRECT FOR RADIX | Digit equals or exceeds the radix; the digit is still used (p.71) |
| 64 | MQP | ILLEGAL CHARACTER IN PUNSYM | p.115 Boxes 15, 8, 9 stops collecting; link not stated |
| 65 | MQDD | MORE THAN 1 RADIX OR PAREN. ENTRY | Radix at the later point (p.100 Boxes 27-29) |
| 66 | GETFLD | SYNTAX ERROR | Radix or GP seen again with Gfsfxa on (p.85 Boxes 62, 57, 51); radix indicator already on (Boxes 65-74) |
| 67 | GETFLD | INAPPROPRIATE CHAR. | Not `,` or `)` with parentheses count non-zero (p.85 Boxes 42, 48); parens could be arithmetic but not closed (Boxes 76-83) |
| 68 | GETFLD | GP ERROR | One absolute datum and a GP or radix already processed (p.85 Boxes 64, 73): message number not stated |
| 69 | VALUE | TRUNCATION IN INDEX VALUE | |
| 70 | VALUE | INDEX IN WRONG PLACE, IT IS IGNORED | |
| 71 | VALUE | SUBSCRIPT WRITTEN AS BIT | |
| 72 | VALUE | CANT SUBSCRIPT CONSTANT, TRY INDEX | |
| 73 | VALUE | SUBSCRIPT OR INDEX INCORRECT | |
| 74 | VALUE | CANNOT SUBSCRIPT SYMBOL WITH NO DDS | |
| 75 | VALUE | 1 SUBS. TOO MANY, LAST USED AS INDEX | |
| 76 | VALUE | TOO MANY SUBSCRIPTS, EXTRA IGNORED | |
| 77 | VALUE | TOO FEW SUBSCRIPTS, OTHERS TAKEN 0 | |
| 78 | VALUE | DIVISION BY ZERO, DIVISOR IGNORED | |
| 79 | GETCHA | INCORRECT CARD CODE CHAR. | p.180 condition 3 (§14 C14) |
| 80 | GETCHA | ILLEGAL CHAR. IN FIRST COL. | p.180 condition 1 |
| 81 | GETCHA | ILLEGAL CHAR. IN NAME FIELD | p.180 condition 2 |
| 82 | GETFLD | (.0) HAS BEEN INTERPRETED AS PAREN INTEGER | |
| 83 | MAIN | SYMBOL TOO LONG FOR SPECIFIED TAIL | |
| 84 | MQDALF | CC ENTRY MODE WITHOUT BS 12 | |
| 85 | MQDALF | BS NOT 8 | |
| 86 | VALUE | ONLY INTEGER VALUES ALLOWED | |
| 87 | DECODE | THE FL IS GREATER THAN 64 | More than 64 bits or in bit style; FL truncated (p.137 Box 20) |
| 88 | DECODE | BYTE SIZE GREATER THAN 8 | More than 8 or in bit style; BS truncated (p.137 Box 29) |
| 89 | DECODE | BIT TYPE NOT ALLOW. | |
| 90 | DECODE | NEG. FIELD HAS BEEN COMPLEMENTED | |
| 91 | DECODE | MODE INCONSISTENT WITH OP | |
| 92 | DECODE | NO MODE | |
| 93 | DECODE | TOO MANY FIELDS | |
| 94 | DECODE | ERROR IN GP | |
| 95 | DECODE | NEGATIVE GP HAS BEEN COMPLEMENTED | |

### 9.3 Numbers 96-148 (pp.178-179)

| No. | Area | Message | Further condition text |
|---|---|---|---|
| 96 | MDUP | NO FIELDS, STATEMENT IGNORED | |
| 97 | DECODE | BIT TYPE UNUSUAL | |
| 98 | DECODE | NEGATIVE PARAMETERS ON EXT | |
| 99 | DECODE | PARAMETER GREATER THAN 64 | |
| 100 | NPS2 | ADDR LESS THAN 33. | |
| 101 | NSYN | ERR IN DDS | |
| 102 | MIOD | ILLEGAL SEQ. OF MCP CARDS | MCP op after a non-MCP non-comment; printed, not punched (p.23 Boxes 30-32) |
| 103 | MIOD | IOD CARD SHOULD HAVE NAME | |
| 104 | MIOD | I/O TBL OF EXITS ADDR NULL | |
| 105 | MIOD | REEL CARD DOESNT NEED NAME | |
| 106 | MDUP | MISSING FIELD | |
| 107 | MX | EXT NOT FOLLOWED BY CORRECT PARTITION CHAR | |
| 108 | GETFLD | GP IS NOT ALLOWED | |
| 109 | MAIN | RADIX SPECIFIED AT THE END OF A DD | |
| 110 | MQM | BIT STYLE NUMBER USED TO REFER. ERR | |
| 111 | MQM | ERR MESSAGE SPECIFIED IS UNKNOWN | |
| 112 | MQDDPP | 0 BASE IN DD | A = 0 in A**B; floating zero put in the accumulator (p.113) |
| 113 | MQDDPP | EXP. NOT IN RANGE | B out of range; bound used (p.113; §14 C15) |
| 114 | INSERT | NEGATIVE FIELD HAS BEEN COMP. | Two's complement in an unsigned field (p.144) |
| 115 | INSERT | INDEX NOT ALLOWED | |
| 116 | INSERT | ADDRESS FIELD HAS BEEN TRUNCATED | Bits truncated to fit (p.144) |
| 117 | INSERT | ONLY K FIELD ALLOW. | |
| 118 | INSERT | ADDR INCLUDES BITS NOT NORMAL IN OP | Candidates on p.144 (S1918A, STTI, SSIC24, S24CW, STT19A): number not stated |
| 119 | INSERT | SLC HAS AN INTEGER | |
| 120 | INSERT | BIT TYPE ADDR UNUSUAL HERE | |
| 121 | INSERT | BIT ADDRESSED TWICE IN LVS OR INDMK | |
| 122 | NEXT | INSTR. NOT ALLOWED IN EXT | Extract from a pseudo-op gets zeros and a message (p.34 Boxes 18A, 18B): number not stated |
| 123 | INSERT | MORE THAN 1 LOC. CTR. DEP. SYMBOL | |
| 124 | NPNSYM | SYM ON PUNSYM NOT IN PROG. | Not found; undefined entry made; Zst37 on (p.168) |
| 125 | MQDALF | NO TERMINATING CHARACTER | End of card block ends the DD (pp.26, 102) |
| 126 | GETCHA | FORCED COMMENT CARD | Illegal continuation card (p.182): number not stated |
| 127 | OUTPUT | PUNID IN PUNFUL SEQUENCE -- STATE. IGNORED | |
| 128 | NUNDSY | MULTIPLY ASSUMED | |
| 129 | MAIN | OP OR SS CHANGED INTO LEGAL MNEMONICS | Indicator `Llbts.8` after a successful search (p.93 Box 10) |
| 130 | DECODE | FIELD LENGTH MORE THAN 24 | |
| 131 | NUNDSY | MULT. DEFINED SYM WITH NO CONTRADICTION | Zst22 (pp.170, 172) |
| 132 | DECODE | CANNOT EVALUATE DDI | |
| 133 | NEXT | INCONSISTENCY IN EXT PARAMETERS | |
| 134 | OUTPUT | PSEUDO LOC. COUNTER CHECK | |
| 135 | GETCHA | ID SEQUENCE | |
| 136 | OUTPUT | RELOCATABLE PSEUDO-OP., NOT IN PUNREL MODE | p.186 |
| 137 | OUTPUT | COMBLOCK STATEMENT WHEN NOT IN PUNCDC MODE | p.186 |
| 138 | OUTPUT | ENTER STATEMENT, NOT IN PUNFPC MODE | p.186 |
| 139 | OUTPUT | NAME LONGER THAN 8 CH. ON COMBLOCK OR ENTER | |
| 140 | MAIN | NO FIELDS ON RELOCATABLE STATEMENT | |
| 141 | MAIN | RELOCATABLE STATEMENT NEEDS A NAME | COMBLOCK without a name; address field still encoded (p.186) |
| 142 | MAIN | COMMON NAME UNDEFINED | |
| 143 | MIOD | EXIT ADDR IS NULL | |
| 144 | MIOD | NO B ON IOD | |
| 145 | MDUP | FIELD IS ZERO | |
| 146 | MDUP | REPEAT PSEUDO-OP WITHIN REPEAT BLOCK, STATEMENT IGNORED | |
| 147 | MDUP | PARAMETER EXCEEDS MAXIMUM ALLOWED | |
| 148 | MDUP | REPEAT PSEUDO-OP ILLEGAL HERE, REPEAT TERMINATED | |

COMREC 7.42 versus the numbers (DERIVED): its first seven items are messages 1-7 in
order. "Symbolic statement too long" has no number; the nearest is the INTOUT I-O
message below.

### 9.4 I-O messages (p.179)

Each is unnumbered text.

| Area | Message |
|---|---|
| XERR | UNCORRECTED ERROR READING DISK / RELATIVE ARC *number* / STRAP ASSEMBLY TERMINATED |
| XINPUT | COMREC FOR INPUT FILE IN ERROR / STRAP ASSEMBLY TERMINATED |
| XERR | UNCORRECTED ERROR WRITING DISK / RELATIVE ARC *number* |
| INTOUT | THE FOLLOWING INSTRUCTION IS TOO LARGE FOR STRAP BUFFER / *current contents of the card image buffer* |
| OPLIST | COMREC FOR LISTING OUTPUT IN ERROR - LISTING ON SYSTEM OUTPUT |
| OPPUN | COMREC FOR BINARY OUTPUT IN ERROR - BINARY ON SYSTEM OUTPUT |
| OPPUN | PUNFUL, COMPILE AND GO BOTH SPECIFIED |
| OPLIST or OPPUN | INSUFFICIENT DISK STORAGE FOR STRAP OUTPUT / STRAP ASSEMBLY TERMINATED |

XERR retries on unit check (p.37). What counts as an erroneous COMREC word is
UNSPECIFIED.

---

## 10. Coprocessor interface (pp.180-182)

Pass 1 may enter a coprocessor. Six conditions, and a seventh entry for "want
another card":

| Entry | Condition | Detector | VF of $3 on entry (p.181) |
|---|---|---|---|
| A (1) | Illegal STRAP or MCP character in column 1 | GETCHA | The illegal character in A8 |
| B (2) | Illegal programmer symbol in columns 2-9: first character of a name must be alphabetic, others alphameric | GETCHA | Zero |
| C (3) | Non-IBM card code character | XINPUT | The illegal 12-bit card code character |
| D (4) | Immediately before the pseudo-op END is processed | GETCHA | |
| E (5) | Illegal operation code | MAIN | Next character after the op code, assumed under nine characters; if more than eight, the ninth; A8 |
| F (6) | Inappropriate character in an entry mode. Modes allowed: Radix, IQS, CC, A, Fn | MAIN | The entry-mode character in A8 |
| G | "Want another card" | | |

A character in A8 or card code is positioned in the rightmost 8 or 12 bits of $3's
value field (p.181).

Setup in STRAP's common work area, without which Pass 1 treats these strictly as
errors: `Hhcom4` on; transfer table at `Hhcopr` = `B, entry A` ... `B, entry G`
(p.180). `Hhcom4` on and a condition not wanted: that slot is `B, 0($15)`. `Hhcom4`
off: the STRAP II transfer vector must be in the table (p.180).

Calling sequence: `SIC, $15; B, entry X`, then three returns: `B,` condition not
wanted; `B,` insert cards; `B,` want another card (p.180).

$7 on entry (pp.180-181):

| Part | Meaning |
|---|---|
| VF | Location of the card image with the trouble condition |
| CF | Bits STRAP II has processed on it; VF + CF = position of the pertinent character |
| RF | Code of the image: 1 CC, 2 A6, 3 A8, 4 not used, 5 IQS |
| $7.25 | 0 image in IBM card code; 1 in the code in RF |
| $7.26 | 0 usual; 1 no more material for a "want another card" request |

$7 on exit, insert cards (p.181):

| Part | Meaning |
|---|---|
| VF | Location of the insert buffer |
| CF | Count + 1 of the images. 1 means nothing inserted; 0 cannot be specified |
| RF | Code of the insert |
| $7.25 | 0 buffer in A8; 1 in the code in RF |
| $7.26 | 0 only as many cards were requested as needed; 1 one too many was requested |
| $7.27 | 0 a continuation card may follow the insert; 1 may not |

Options: decline; or accept and do 2a (request cards one at a time) then 2b (0 to
n images in a buffer) or just 2b. The final return is insert cards. For a card
code condition, the present card block is ended first if it has good units (p.181).

Rules (pp.181-182): save and restore all index registers except $7 on re-entry. An
extra card must be in the insert; it is checked for an illegal continuation, which
becomes a comment with an error. Information remaining on an error card is lost
unless put in an insert. END must be alone in its card block while `Hhcom4` is on.
"Want another" images are in original input code, not A8. Pass 1 will not have scanned
them for END; the coprocessor must, then ask no more, return by insert cards, and the
insert must at least include END. Insert groups should not contain END: if detected,
entry 4 is used once with `Hhcom5` on (p.181). Conditions come from original input,
not an insert.

---

## 11. Relocation pseudo-ops and binary cards

### 11.1 Pseudo-ops (p.183)

| Op | Form | Use | Notes |
|---|---|---|---|
| ORIGIN | `ORIGIN, N` | Special origin card | Name not meaningful. N location, absolute or symbolic |
| PUNREL | `PUNREL` | Relocatable mode | Name, address not meaningful |
| PUNFPC | `PUNFPC, S, C` | Fortran program card | S program size, C blank common size; absolute or symbolic |
| ENTER | `A ENTER, B` | Info for program card | A any eight characters but quote and semicolon. B entry point |
| PUNCDC | `PUNCDC` | Common definition card | |
| COMBLOCK | `A COMBLOCK, N` | Define named common | A up to 8 characters. N block size |
| SLCRCOM | `SLCRCOM, B` | Set location relative to common | B absolute or symbolic: named common; blank: blank common |
| FEND | `FEND` | Fortran branch card | |

Example program on p.184.

### 11.2 Processing (pp.186-187)

- PUNREL: Pass 1 sets bit `Punrel`. Other punch pseudo-ops turn it off, and Pass 2
  sets it also. Pass 2 refuses relocation pseudo-ops when not in PUNREL (136).
- PUNFPC: encodes sizes; second field may be blank. In PUNREL, OUTPUT enters PUNFPC
  mode and leaves it at a non-ENTER (138).
- ENTER: name entry; address encoded. In PUNFPC mode, OUTPUT fetches the 64-bit A8
  name from the name file, or eight A8 blanks if no name; evaluates the address by
  VALUE; 19-bit field. Card punched at a non-ENTER or full. Additional cards have
  blank size fields.
- PUNCDC, COMBLOCK: as above. COMBLOCK reserves nothing. `Zstcom` = 1, `Zstcon` =
  18-bit reference number. No name: error, encoding continues (141). Name from file,
  size by VALUE, 18-bit field.
- SLCRCOM: Pass 1 sets `Mupper`; entries are relative to an upper address. Blank
  address: common 0. Otherwise looks up the name; marked with the common number from
  its entry. Pass 2 sets the location counter to zero. In blank common use DR only.
  Blank common is defined by `SLCRCOM` with no field, not by COMBLOCK. `BL1
  COMBLOCK, 5`, `SLCRCOM, BL1`, `JOE DD(N), 5, 10, 15, 20, 25`: references to JOE mark
  relocatable as an upper address relative to common #1.

### 11.3 Card layouts in col.row notation (pp.187-188)

Which physical row is `.0` is UNSPECIFIED. All have cols 72.0-80.11, nine columns
ignored by the loader, usable for card code identification and sequencing. Col 2
is the identification column, col 3 sequence number, col 4 check sum, on all but the
Origin card. Check sum algorithm and the sequence scheme are UNSPECIFIED (§14 G4).

| Card | Col 1 punches | Page |
|---|---|---|
| Relocatable Data | 6, 7, 8, 9 | p.187 |
| Common Definition | 5, 7, 8, 9 | p.187 |
| Fortran Branch | 5, 6, 7, 8, 9 | p.187 |
| Fortran Program | 5, 6, 7, 9 | p.188 |
| Relocatable Binary Instruction | 5, 7, 9 | p.188 |
| Special Origin | O- | p.188 |

Relocatable Data Card (p.187):

| Bits | Use |
|---|---|
| 5.0 | 0 skipping, 1 setting to zero |
| 5.1 | 0 skip/zero before card contents load, 1 after |
| 5.2-5.11 | Bit count (10) |
| 6.0-7.11 | Origin |
| 8.0-9.11 | Bits to skip or zero, before or after loading (24) |
| 10.0-10.11 | Loading base |
| 11.0-71.11 | Data only |

Holds DD data and a count from DR or DRZ. Skip-before when no data or DR waiting;
skip-after when there is data; a waiting DRZ forces an origin card first (p.158).

Common Definition Card (p.187): 5.0-8.11 not used (48). Then nine 7-column groups:
9.0-14.3 first name (64); 14.4-15.9 size (18); 15.10-15.11 not used (2); 16.0-21.3,
21.4-22.9, 22.10-22.11 second; third at 23.0-29.11; 30, 37, 44, 51, 58, 65.

Fortran Program Card (p.188): 5.0-5.11 not used; 6.0-7.5 program size (18); 7.6-8.11
blank common size (18); 9.0-14.3 first entry name (64 A8); 14.4-15.10 entry address
(19); 15.11 not used; 16.0-21.3 name [printed "first", read second]; 21.4-22.10
address; 22.11 not used; then at 23, 30, 37, 44, 51, 58, 65.

Fortran Branch Card (p.187): 5.0-71.11 not used. Result of FEND.

Relocatable Binary Instruction Card (p.188): 5.0-5.11 bit count, excluding relocation
bits; 6.0-7.11 origin; 8.0-8.11 not used; 9.0-71.11 variable binary, instructions only
(XW's, CF's, RF's, no DD's or DR's), followed by variable relocation bits.

Relocation bits (p.188), a prefix code per address:

| Pattern | Meaning |
|---|---|
| 0 | No relocation |
| 1 0 ... | Relocation |
| 1 0 0 .. | First 18 bits (address) |
| 1 0 1 .. | Last 18 bits (refill) |
| 1 0 . . 0 | As lower address |
| 1 0 . . 1 .. | As upper address |
| 1 0 . . 1 0 | Blank common |
| 1 0 . . 1 1 i | Named common, i its number; length of i is determined by the number of named commons |

The second bit (the 0 after the leading 1) is "reserved for later definition"
(p.188). **DERIVED**, reading each `..` as one don't-care position in the rows
above (the print is a 250 dpi crop of p.188, spaced as shown): bit 1 = 1, bit 2 =
reserved 0, bit 3 = 0 first 18 / 1 last 18, bit 4 = 0 lower / 1 upper, and only if
upper, bit 5 = 0 blank common / 1 named, then i. See §14 G5.

Special Origin Card (p.188): 2.0-9.11 new origin, full word location punched as
`xxxxxx.0` octal; 10.0-71.11 not used.

### 11.4 Other binary

Not in this guide in the pages read: the absolute binary card and PUNORG/PUNFUL/PUNNOR
formats. The plan's pointer is C28-6129 pp.22-23. Known here: PUNFUL has no control
information, so a DR is punched as blank words or cards of the DR length (p.158 Boxes
1, 2). SLCR: OUTPUT stops punching until the next SLC (p.36).

IOD handling, p.157 Boxes 15, 16: IOD cards specified by the programmer are punched,
and also: absolute decks, `TYPE, GO` / `LIM, __, __`; relocatable decks, `TYPE, GO` /
`LIM, __, __`; Fortran decks, `TYPE, GO, FORTRAN`. NMCPA1 creates and punches them in
Pass 2a (chart p.147). IOD and REEL go out as eighty-column A8 images (p.148); no
exit address means that field is blank (p.148). Their column positions are UNSPECIFIED
in the pages read.

SYN cards from PUNSYM/PUNALL, after all binary (p.169):

| Columns | Contents |
|---|---|
| 2-9 | Name |
| 10-12 | SYN |
| 13-22 | (Mode, FL, BS), |
| 23-38 | (8) +xxxxxx.xx bit value |
| 42-53 | (8) +xxxxxxxx integer value |
| 56-60 | ($xx) index value |
| 61-72 | , (Dim.1, Dim.2, ..., Dim.x) |
| 73-80 | Identification |

Continuation (for name, dimension or both): 1 asterisk, 2-9 name, 10-xx dimension
reference. No cards for undefined entries. PUNALL: all symbols. Dimensions recovered
by dividing products (p.169).

Listing: page heading has the initial time, card ID from cols 73-80, ID from the latest
PRNID, page number, location counter within a word at start of page, column titles
(p.165). The end has total time, unit count, `THE END` on a page by itself (p.36). Column
positions of the line are UNSPECIFIED in the pages read. DDs print as: floating:
exponent, fraction, sign byte; fixed: sign byte separate for signed data (pp.158-159).
Multi-field DD fields advance by a standard 120 bits plus extras (p.159).

---

## 12. Appendix B: additional instructions and pseudo-ops (pp.195-196)

"Additional": not in the 7030 Reference Manual. Mnemonic limit 8 characters. A
pseudo-op is an op that produces no binary, with exceptions EXT and CNOP (p.196),
and p.27 and p.205 say XW, CF, RF, VF, CW, INDMK, CNOP are not pseudo-ops.

Pseudo-ops: COMBLOCK, CNOP (conditional no op), DDI, DR, DRZ, DUPLI, END, ENTER, EXT,
FEND, LINK, NOPRINT, NOPUN, NOSEQ (no sequence number in binary), ORIGIN, PRND, PRNID,
PRNOR, PRNS, PRNTALL, PUNALL, PUNCDC, PUNFPC, PUNFUL, PUNID, PUNNOR, PUNORG, PUNREL,
PUNSYN (or PUNSYM), REM, RESEQ (restore punching sequence number with one), SEM, SKIP,
SLC, SLCR, SLCRCOM, SPNUS, SYN, TAIL, TLB, UNTAIL.

General: CF, CW, DD, INDMK, RF, VF, XW. MCP: IOD, REEL.

I-O (form `OP, A7(I)`, channel address, the unit being the last selected by a LOC):
BS/BSSEOP, BSFL/BSFLSEOP, ECC/ECCSEOP, ERG/ERGSEOP, EVEN/EVENSEOP, GONG/GONGSEOP,
HD/HDSEOP, KLN, LD/LDSEOP, NOECC, ODD/ODDSEOP, ODDECC, ODDNEC, RLF/RLFSEOP, RLN/RLNSEOP,
RWDUNL, SP/SPSEOP, SPFL/SPFLSEOP, TLB, TILF, UNLOAD.

Secondary: CCR, CD, CDSC, CR, SCCR, SCR, SCD, SCDSC.

Their skeletons and the base-instruction table are UNSPECIFIED.

## 13. Appendices D, G, H; sections and registers

### 13.1 Symbol prefixes (App. D p.202)

A table management; AZZ triggers; AZ relative location in table control block; AY
temporary; AX bit lengths; AW relative locations in entries; AU universal block; AS index
saves. B buffers. CC CCA8. CP CPLTSY, CPLTNM. D DD. E error messages; EF error flags. F
control flags. GC GETCHA. GF GETFLD. H interrupts. I intermediate I-O. J MOVE. K DECODE.
LL BOPSER. LLL MBSPEC. M Pass 1 main flow. N Pass 2 main flow. O OUTPUT. P, R, W none. QC
character (256-bit) question strings. S insertion. T tables and setup. TOPA op fill
control words. TOPQ op question (64-bit) strings. U UITER. V VALUE. X I-O. ZI unit, ZO op
question, ZST vle function: SYN's.

### 13.2 Deck (App. G p.208)

Card columns 1, 2, 10, 66 head the drawing.

```
col 1   col 2       col 10                                 col 66
B                   HED, REP, PCSTRAP, ,
        SCSTRAP0
B                   LIM, 000042, (upper limit)
B                   IOD, TRACK                              1
B                   HED, REP, SCSTRAP0, ,
T
                    STRAP bootstrap binary deck.
                    Followed by C and P cards if any.
B                   HED, REP, SCSTRAP1, LOAD, ,
T
                    Binary deck for STRAP sections: 0, A0, A1, 1;
                    Followed by C and P cards if any.
B                   HED, REP, SCSTRAP2, LOAD, ,
T
                    Binary deck for STRAP sections: A2, 2;
                    Followed by C and P cards if any.
```

`SCSTRAP0` is on a row of its own with no col 1 character, as printed; a bracket joins
it to the first row, so whether it is a separate card is UNSPECIFIED. The meaning of `000042` and of 1 in col 66 is UNSPECIFIED here.

### 13.3 Memory map (App. H, Fig. 30 p.209; sections p.174)

```
Bootstrap | Sec 0 | A0 | A1 | Sec 1 |      | A3
SCSTRAP0  |<---- SCSTRAP1 ---------->|
                       | A2 | Sec 2 |
                       |<- SCSTRAP2 ->|
```

SCSTRAP2 overlays A1 and Sec 1, starting at A1's start and ending short of Sec 1's end
as drawn. A3 buffers sit beyond. MCP brings in all of Pass 2 from disk (p.26). Addresses
are UNSPECIFIED.

| Type area on disk | Section | Contents (p.174) |
|---|---|---|
| SCSTRAP0 | Bootstrap | |
| SCSTRAP1 | 0 | Subroutines common to Passes 1 and 2 |
| | A0 | Common constants, work areas; I-O routine constants; common error messages; all control words for error messages; all serious messages |
| | A1 | Pass 1 constants, work areas |
| | 1 | Pass 1 subroutines |
| SCSTRAP2 | A2 | Pass 2 constants, work areas; all non-serious messages |
| | 2 | Pass 2 subroutines |
| | A3 | Buffers (e.g. `Tsymba`, `Ibufa`) |

### 13.4 Index registers (p.175)

| $ | Pass 1 | Pass 2 |
|---|---|---|
| 0 | VF calling-sequence reads in TABMAN; RF during RNX | same |
| 1 | - | - |
| 2 | RNX | RNX |
| 3 | A8 character from GETCHA | Address of unit |
| 4 | - | Absolute portion of location counter |
| 5 | Address of question bits | same |
| 6 | Address of unit | Symbolic portion of location counter (3-char special symbol) |
| 7, 8, 9 | Random | Random |
| 10, 11 | VALUE | VALUE |
| 12 | - | NAMEIN |
| 13 | INTOUT | OUTPUT |
| 14 | GETCHA | NAMEIN |
| 15 | VF linkage; RF table of exits for maskable interrupts | same |

Registers other than $7-$9 are saved on entry and restored on exit by routines using
them otherwise. STRAP II writes the pass to the console's numeric display lights (p.173).
Note that the text of p.26 says the same.

---

## 14. Gaps and contradictions

### Gaps (needed for code; not in the guide as read)

- **G1. Symbol function layout.** The 231-bit minimum function has no diagram (§4.5).
  Only names and meanings, scattered. Any reconstruction must CHOOSE bit positions for
  the multi-bit fields and flag them; the numbered flags give a partial skeleton.
- **G2. Op table and op index contents.** No mnemonic list with skeletons, no question-bit
  assignment, no fill-word lists beyond p.144's examples, no pseudo-op select numbers
  (§4.7). The plan already records this.
- **G3. Character codes.** No A8, A6, IQS or CC conversion table; only nine A8 values in
  Figs. 14, 28, 29 (§5.5).
- **G4. Card mechanics.** Check-sum algorithm; sequence number and ID encoding; row
  order within col.row; binary packing of data in cols 11-71. Bit count semantics beyond
  p.188's "excluding relocation bits". (§11.3)
- **G5. Relocation bit strings.** Dots on p.188 are ambiguous in width; length of `i`
  has no formula; order of the strings against addresses unstated. The two bits per
  address in the unit have different names from those on the card; mapping unstated.
- **G6. Absolute binary and listing line.** No absolute card format (use C28-6129), and
  no print-position table.
- **G7. Unit details.** ZILBO's unit, the location of ZINXBO extra words, bit ZILPMS.63,
  which ZIOPX flag is which, the marked "phoney" form, whether `Aztec` is 0 or 1 for what.
- **G8. Numbers.** Max unit size, buffer sizes (`Ibufa`, `Tsymba`, the vle block), words
  per arc. p.90: three unit buffers, A, B, C; ten unused words test.
- **G9. Conditions.** For most numbered errors only a message exists (§9). p.12 says so.
- **G10. Special index (1001).** The three additional bits are undefined. p.58's table
  does not give them either. System symbol list, and the "punch option" COMREC bit.

### Contradictions and oddities

- **C1.** p.11 "bits 00-18" for last arc against 0-17 for the arc number everywhere.
- **C2.** p.22 op-question location "first 18 bits of the function part" against Fig. 23
  "bits 0-23" (p.192).
- **C3.** p.9 "word 8 must always be set up by the pre-processor" against p.131: STRAP II
  sets word 8 when first in chain. p.9 itself says first in chain means System Input.
- **C4.** Fig. 24 abc code `020` is not a 3-bit value; [printed]. Probably 010.
- **C5.** Items 2A-2B (p.198) list only absolute and symbolic, against p.197's sub-expression
  `101` and long-prefix `111`. Fig. 29 uses `11100`.
- **C6.** p.159's "standard 120 bits" per DD field against Fig. 26: a + 12 + 96 + 8 + b +
  c + d + e = 121 with no special exponent or G.P., and the figure draws those two
  unconditionally. Either 120 omits one flag or the figure's conditional fields differ.
- **C7.** Fig. 27 labels evaluated fields D1, D2, ..., D1D2...D(n-1); Fig. 22 labels the
  same n1, n1 x n2, n1 x n2 x n3. p.169 (products) supports Fig. 22. Also Fig. 22's
  evaluated head shows 5 + flag, Fig. 27's "Dimension Information" starts the same; agree.
- **C8.** Five error flags in the unit (pp.25, 34, 36; 25-29 in Fig. 20) against four-bit
  SINSER and VVSER (Figs. 9, 10).
- **C9.** Special symbol: 24 bits with 16 determined (p.205), three A8 (p.13); Fig. 21 draws
  a 64-bit field as 2^8-1, n, 0, with n of no stated width. p.205 and Fig. 21 reconcile if
  n is 16 bits and the rest 40 zeros (DERIVED).
- **C10.** Fig. 23 captions "Two Word Format" over three rows. If the location row is a part
  of the skeleton word, it overlaps the skeleton; if separate, the entry is three words.
  Fig. 11 and p.22 do not settle it. Non-ambiguous and ambiguous rows both have it.
- **C11.** Tail mark: asterisk (p.125) against `$`-character (p.75). p.125 also says up to
  ten levels and "n mod(8)" on a level over eight (Box 38).
- **C12.** p.204 lists the priority: 1st `+ -`, 2nd `* /`, 3rd `**` as "descending order of
  combination", so `**` lowest in that phrasing. p.198 has no `**` operator code at all,
  yet MQDDPP handles `A ** B` in DDs (p.113), where numbers are not coded expressions.
- **C13.** Fig. 4 has no message number field; zeros fill its last 8 bits, yet p.38 says
  the rank is in "the 32-bit entry", and p.37 says each entry prints a message. UITER's
  message number has no place as drawn.
- **C14.** Illegal card character: p.180 says XINPUT detects it, p.177 error 79 says
  GETCHA, and p.79 says GETCHA, MAIN, or XINPUT inform the coprocessor.
- **C15.** p.113: "When B < 2^-18 ... -1 + 2^-18; when B < 2^+18 ... -1 + 2^+18". The second
  relation is [printed] and must be wrong as a range test.
- **C16.** Coprocessor: p.180 says six conditions plus a seventh entry; p.182 "possible
  seven entry points" agrees; `Hhcopr` drawn A-G. Numeric conditions 1-6 are A-F (DERIVED).
- **C17.** Two names for one thing: `ZIFNME` (Fig. 20) and `Zifname` (p.25), `ZIFPMN`
  and `Zifpm` (p.140). Printed "PRINID" and "PRNID", "NOPRINT" and "NOPRNT", "PUNSYN" and
  "PUNSYM" (pp.27, 34, 195). Fig. 13's caption names CPLTNM, p.6's list CPLTSY. p.188's
  program-card second name reads "first".
- **C18.** Fig. 28's source line has unbalanced parentheses as printed.
- **C19.** Same test, two numbers: FL > 64 is messages 36 (MAIN) and 87 (DECODE); BS > 8
  is 37 and 88. DERIVED: Pass 1 and Pass 2 versions.
- **C20.** Five flags, four named: p.25 lists undefined, multiply-defined without
  contradictions, and circular or error-defined; NUNDSY has a separate Zst23 for
  contradictions. See C8.

---

## 15. Reach of this reading

Read as page images: printed pp.3, 6-11, 173-211 (all assigned; 210 is the comment sheet,
211 the back cover, with no body page after 209), and 12-14, 22, 23, 25-27, 32, 34, 36-39, 44,
45, 58, 60, 67, 71, 75, 76, 79, 85, 86, 88-90, 93, 97, 100, 102, 113, 115, 125, 131, 135, 136, 137,
140, 144, 147, 148, 157-159, 161, 163-165, 167-172. Zoomed crops: pp.75, 76, 184, 188, 189, 193,
200, 201.

Pages 200 and 201 are rotated; they were read rotated upright.

Not read as images, and so the reach of every UNSPECIFIED: the rest of pp.15-172, and pp.1, 2, 4, 5
(front matter). Those were swept only through
`docs/ocr/` for `Zst`, `Zi`, `Zo`, `Ef`, dictionary, column, check sum, sequence, print, card
code, A8, name file, extra word, control block, op index, and COMREC. The OCR is often wrong, so
an UNSPECIFIED here is strong for anything these words would name, and weaker otherwise. Pass 1 and Pass 2 logic pages
are being read by the two other agents; their results may close G7 and parts of G9.
