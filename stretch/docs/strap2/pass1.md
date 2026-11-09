# STRAP II Pass 1: specification from C22-6729

Source: `docs/C22-6729_7030_STRAP_II_Sys_Analysis_Guide.pdf`, read as page
images. A bracket such as `[23]` is a printed page; PDF page = printed page on
every page cited here (each folio was seen). `AA.3` means flow chart AA box 3.
Text is authority for meaning, charts for order; where they differ the fact is
listed in section 8. UNSPECIFIED means the pages read do not settle it.
"INFERRED" marks a reading of a chart that the text does not state.

Pages read in the ink: 3-4, 12-32, 63-135, 137, 170, 173-174, 176-187, 189-198,
202-207. Not read: 5-11 (COMREC layout), 33-36, 37-62 (common section: ERR,
MOVE, TABMAN, ADDORD, VALUE, XERR), 136, 138-169, 171-172, 175, 188, 199-201,
208-211. Claims "the guide does not say" rest on the pages read plus a per-page
grep of `docs/ocr/`, which is unreliable on charts; each such claim says so.

The caller's page ranges differ from the contents page [3]: Pass 1 logic areas
are 63-135 (not 57), the Pass 1 description ends on p.32 (Box 67 continues past
the Pass 2 charts, pp.28-31), and MQP [114-115] and MX [128-129] are also in
the range.

## 1. Conventions

### 1.1 Register roles during Pass 1

| Item | Use | Page |
|---|---|---|
| VF of $3 | current input character, A8 code | 20, 79 |
| VF of $5 | location of the current op index | 22; `$X5` in 95 |
| VF of $6 | absolute address of the current unit's fixed format; fields are addressed off $6 in Pass 1 | 12, 19 |
| refill field of $15 | STRAP II's table of exits for maskable interrupts | 19 |
| $7 | parameter register for GNLOAD; coprocessor communication | 88, 180-181 |

Many index registers have fixed uses in the assembly [19]; the full list is
UNSPECIFIED in the pages read.

### 1.2 Character testing

For each card-code character and for specific groupings there is a 256-bit
question block, permanently masked, located by a symbol beginning `Qc`,
addressed by the A8 character in VF of $3, e.g. `BB, Qcdola($3), Mb` [20]. A
pre-processor can pass a special A8 character by setting the high-order two
bits of the A8 character to one and the corresponding question block bit; it is
then taken as alphameric [20]. Block contents beyond the named tests are
UNSPECIFIED.

### 1.3 Card and block

- Column 1: `*` is a continuation mark [203]; a card with no mark is the initial
  card [204]. A comment character in column 1 of an initial card makes the card
  a comment [79]. The comment character is the quote: AA.7 is labelled QUOTE and
  joins the comment path on chart AB [14-15]; quotes open the comments in the
  example [184]; ENTER names exclude "the quote and semicolon" [183].
- Columns 2-9: name [204]. The first name character must be alphabetic, the rest
  alphameric [180].
- Columns 10-72: statement field [79].
- Columns 73-80: identification [20].
- Card block: the initial card and the continuation cards immediately after it
  [203]. Several statements separated by `;` may be in a block [20, 25].
- Name: legal characters in 2-9 including embedded blanks [204]. Symbol: the same
  excluding the blanks [205]; the name goes to the name file, the symbol to the
  symbol table [20, 79].

### 1.4 Unit

A control word followed by the fixed format, then coded expression(s), then the
print image [12]. A unit occupies "at least eight words" [12]: control word plus
seven fixed words. Figure 20 shows six because it excludes relocation fields; the
seventh is ZICOMM [184]. Fixed format layout (the bit positions are read from the
figure's cell grid at 170 dpi [189]; the formats document governs if it differs):

| Word | Field | Bits | Meaning [189] |
|---|---|---|---|
| ctl | next word address | 0-17 | start of format [90, 189] |
| ctl | zeros | 18-24 | |
| ctl | a | 25 | last control word in buffer [90, 91] |
| ctl | b | 26 | last control word in file [90] |
| ctl | zero | 27 | |
| ctl | word count | 28-45 | words in unit [90] |
| ctl | refill | 46-63 | address of next control word [90] |
| 1 | ZIADAB | 0-24 | absolute location counter; filled in Pass 2 |
| 1 | ZILBO | 25-31 | length of binary output |
| 1 | ZIADSY | 32-56 | symbolic location counter; filled in Pass 2 |
| 1 | ZIFNME | 57 | c: name (the text writes `Zifname` [25]) |
| 1 | ZIFP2 | 58 | d: DECODE gets unit |
| 1 | ZIFBO | 59 | e: binary output |
| 1 | ZIFDD | 60 | f: DD |
| 2 | ZILCFD | 0-24 | length of coded fields (bits) [25] |
| 2 | ZIFDDS | 25 | g: explicit dds |
| 2 | ZIFPMN | 26 | h: P-mode |
| 2 | ZIFFLF | 27 | i: f.l. filled in |
| 2 | ZIFSFL | 28 | j: symbolic f.l. |
| 2 | ZIFBSF | 29 | k: b.s. filled in |
| 2 | ZIFSBS | 30 | l: symbolic b.s. |
| 2 | ZIFDSF | 31 | m: dds filled in |
| 2 | ZILSST | 32-56 | length of symbolic statement (8-bit characters) [25] |
| 2 | ZINXBO | 57-63 | number of extra words of binary output |
| 3 | ZILPMS | 0-24 | length of P-mode symbol [23] |
| 3 | ZIFALL | 25 | n: nothing left for DECODE |
| 3 | ZINAME | 28-31 | name check digit [25, 88, 173] |
| 3 | ZINFLD | 32-49 | number of fields |
| 3 | ZIDDS | 50-62 | dds information (13 bits; bit 63 unlabelled in the figure) |
| 4 | ZICDID | 0-63 | card ID |
| 5 | ZIOPX | 0-24 | location of op question bits |
| 5 | error flags | 25-29 | five error symbol flags [25, 189] |
| 5 | p | 30 | suppress e.m. |
| 6 | ZIOTPT | 0-63 | binary output; other uses in section 5 |
| 7 | ZICOMM | | relocation word [184-185] |

ZIFALL starts on for every unit [19] and is turned off when coded expressions
remain [23, 24, 27, 129]. Its meaning is legend n above.

### 1.5 Symbol table entry

Dictionary part: delete bit, vle bit, first eight characters of name, 25-bit signed
address of the vle [190]. The vle: delete bit, 13-bit total length, 6-bit ID, 12-bit
length of rest of name, 8n bits rest of name, function, 231 bits minimum [191]. IDs
(A6 graphics): S symbol, Y internal STRAP II symbol, T tail, D dimension, H hi-lo
[191, 194]. Every dictionary entry must have a vle portion because of how named
units are coordinated with their entries in Pass 2 [13]. Vle-only entries (no
dictionary part): hi-lo candidates, old vles of multiply-defined symbols without
contradiction, dimension entries [13].

Function layout: there is no table of Zst positions; p.191 says only "format of
function defined by the ZST...bits" and p.202 says they are SYNs (sweep: `Zst`
occurs on pp.13, 135, 137, 140, 168, 170, 173, 185, 186, 191, 202, 203). Meanings
seen, names as printed: Zst0 everything defined and computed [135, 137], Zst1
undefined [170], Zst3 existence of dds reference decided [135], Zst4 circularly
defined [170], Zst10 mode known [137], Zst11 f.l. established [137], Zst12 symbolic
f.l. exists [137], Zst14 b.s. established [137], Zst15 symbolic b.s. exists [137],
Zst17 processing bit for mode [135], Zst22 multiply-defined, no contradictions
[170], Zst23 multiply-defined with contradictions [170], Zst24 used [170], Zst26
real value computed and entered [137], Zst32 use dds reference address [135], Zst35,
Zst36 location counter dependence [185], Zstcom, Zstcon common [185], Zstcnt check
digit [173]. Bit positions and any other fields are UNSPECIFIED.

### 1.6 Coded expressions

Format is Appendix C [197-198]. GETFLD's spacing numbers in 3.6 follow it:
symbolic datum `100` + 7-bit byte count + symbol; absolute datum `110` + 24 bits;
system symbol datum `11100` + 24 bits + 13 bits dds; normal prefix `1000`; operator
= 1 + 3-bit code + 5-bit datum number; codes `111 .+`, `110 .L`, `101 .R`, `100 U-`,
`011 *`, `010 /`, `001 +`, `000 -` [197-198].

## 2. Order of processing

### 2.1 Entry, once [19, chart AA.1]

1. Save the time clock (OUTPUT marks binary cards with it; end of assembly computes
   total time).
2. Write current pass on console numeric display lights.
3. Have MCP change two IOD addresses: console and disk.
4. Check $UB for machine size; set internal symbol table limits.
5. Initialize ERR and VALUE.
6. Set refill field of $15 to the table of exits for maskable interrupts.
7. Fetch COMREC; if STRAP II is first in the chain, set COMREC to indicate System
   Input. Go to MAIN.
8. Turn on ZM and EXE in the mask register so MCP gives these interrupts to STRAP II.

The list prints 8 after the "go to MAIN" of 7; true order of 7 and 8 is UNSPECIFIED.
GETCHA's first entry calls XINPUT and fills the error branch vector [77, 79].

### 2.2 Per instruction: chart order

Each statement in a block runs this loop once.

**Box 2, MAIN, initialize [19-20].** Zero `Bem` (2 words). Blank `Bop`. Zero the error
field counter `Field`. The unit counter is not touched here (starts at 1, stepped at
end of the former unit). Zero the fixed format of the unit. Off: if-modifier,
if-pseudo-dds (not in unit). On: ZIFALL. Zero the mask of five error symbol indicators
and the suppress indicator. Reset GETFLD's indicators, flags, radix. Reset `Bopx` and
`Bsystx`. Round `Ibuffw` to a full word and save it in $6. Update `Ibuffw` past the
fixed format; this start of coded expressions is saved to compute their length later.
Put the buffer's upper limit in `Bcfxtx` (reset for each instruction because GETFLD
can be pointed elsewhere, e.g. the vle for a SYN). Put columns 73-80 in ZICDID; a
multi-card instruction gets the ID of the card it started on; every instruction started
on one image gets the same ID, with no listing indent.

**Boxes 3-4 [20].** If `Fblend` on: previous instruction ended a block, this one starts
a new block; turn on `Fblena`, turn off `Fblend`. `Fblend` is initially on. When `Fblena`
is turned off is UNSPECIFIED (see 8).

**Box 5.** GETCHA gives the next character, skipping blanks unless `Gcaz` on [20].

**Box 6-9, 10 [14, 20-21].** Legal first characters: legal op characters, `(`, `;`, `'`,
`$`, `,` [20].
- Legal op character: to 12. `$` also goes to `Mb` (the label of box 12) by the example
  on p.20. How `$` reaches the suppress flag and whether it enters `Bop` is UNSPECIFIED;
  `$` before the instruction sets suppress [25]. Error 30 is MORE THAN ONE $ [176].
- `(`: box 11 (entry mode), then 12.
- `,` (null op): to the junction before 13, `Bop` still blank; `Bopx` is already set for
  the look-up of the null op [21].
- `'`: to AB.7B. `;`: to AB.9H.
- Otherwise error, enter coprocessor (AA.9). Error 29 by message [176]; corrective
  action UNSPECIFIED.

**Box 11, entry mode [21].** Build `Bem` before the op characters. First index word:
radix on the current D field; second: parameter, if any, specified before the op. In
each, value field: terminating character of an alphabetic DD; bits 36-60: radix; bits
61-63 `Bemt`, `Bemu`, `Bemv`:

| Bemt | Bemu | Bemv | Meaning |
|---|---|---|---|
| 1 | 0/1 | 0/1 | alphabetic entry mode |
| 1 | 0 | 0 | A |
| 1 | 0 | 1 | CC |
| 1 | 1 | 0 | IQS |
| 0 | 0 | 0 | none given |
| 0 | 0 | 1 | Fn |
| 0 | 1 | 0 | (r) radix |
| 0 | 1 | 1 | (.n) parenthetical integer |

MAIN gets a leading F-entry number with CPLTNM [71]. The entry-mode grammar, including
what ends it, is UNSPECIFIED beyond these; see errors 3, 31, 32.

**Boxes 7, 7B, 9C, 9D (first character quote) [20].** Named block first character:
make up `DRZ(N), 1` for the unit. Then, named or not, relay to GETCHA until `;` (box 38,
MEDAF). The intermediate characters only go to the listing.

**Boxes 9H-9G (first character semicolon) [15, 21].**

| Fblend | Fblena | Case | Action |
|---|---|---|---|
| off | any | more than one `;` after an instruction not last in the block | make `DRZ(N), 1` |
| on | on | `;` is first character of this block | `DRZ(N), 1` if named, else comment unit |
| on | off | false `;`; a real `;` already ended the block | if that block had a name, make the symbol table entry now; no unit; go to box 2 |

Moving precoded `DRZ(N),1` or the comment unit into the current unit [21]: save and
restore ZICDID; set $5 to the op index; adjust `Bcfldx` so the later redefinition of
`Ibuffw` by it is correct; turn on `Fiod`. Then to box 38. The comment unit prints a
blank line [21].

**Boxes 12-15 [21-22].** Collect through GETCHA, each tested legal, up to eight
characters in `Bop` or to the next separator. Chart 13: `,` `;` `'` ends with `Fmodif`
off. `(` sets `Fmodif`. Any other: error, enter coprocessor.

**Boxes 17-22 [22, 14].** BOPSER on the ordered primary op table. Found: 23. Not found:
MIBA, which returns op determined, or retry after MBSPEC substitution (back to 17), or
illegal. On exhausted retries the unit becomes `SIC, $15; BE, 0` (the chart for EXT shows
the same pattern; see 8) and the error is given. Error 1 by message; coprocessor entry 5
[180].

**Box 23 [22].** From the op entry put the skeleton and the op index location in the unit
(ZIOPX) and $5. Table formats [192]:
- Non-ambiguous: mnemonic word; skeleton word; op-index location in bits 0-23.
- Ambiguous: skeleton of floating form 0-31 (op-index location in 0-23), VFL bits 32-63.
  One table entry only; the unit is processed as floating until diagnosis of dds or
  address fields proves otherwise; in Pass 2a, if the dds was evaluated after DECODE's
  VALUE call and it is still ambiguous, DECODE assigns VFL dds.
- Pseudo: op-index location 0-23; digit-select number 32-50.

Op question bits: `Zo` names [22]; the string's first 24 bits hold the first fill control
word address; a binary-producing op with a secondary op also holds the secondary code
[22]. Op table contents are not in the guide (see 8).

**Boxes 24-26 [22-23].** `Fmodif` on and op is EXT: postpone (to MX). `Fmodif` on otherwise:

- Secondary op: if the character after `(` is in the block of legal secondary first
  characters, collect and look up in the secondary table, MBSPEC may help. Up to seven
  characters; leading byte in `Bop2x` is the code from the current op index, so wrong
  pairs such as `+(BU,3)(SEOP)` and `CW(V+I)` yield arguments absent from the table.
  Entry format [192]: 8-bit code `abc`, values as printed: 000 -, 001 VFL secondary op, 020 SEOP, 100 CW
  secondary. If ambiguous op, a secondary op makes it VFL: VFL skeleton, VFL op index in
  unit and $5.
- P-mode, absolute, symbolic or absolute-symbolic dds: treat as P-mode through CPLTSY into
  the coded-expression area. This symbol is the dds coded expression. Compute ZILPMS =
  VF of `Ibuffw` minus VF of `Bsymbx`, the latter set = `Ibuffw` before the call [23].
- Otherwise GETFLD encodes byte size and field length in the unit, then VALUE [23].
  For each expression VALUE evaluates: adjust erroneous parameters, store value in its
  fixed field, turn on the dds-field-filled indicator, erase the expression by resetting
  `Ibuffw`, unless a g.p. goes with it. If DD with g.p.: keep the expression and space
  `Ibuffw` over it; OUTPUT evaluates it in 2b. For each expression VALUE cannot evaluate:
  turn on symbolic-f.l. or symbolic-b.s. in the unit, keep it for DECODE, space `Ibuffw`
  over it, turn off ZIFALL. Then the mode indicator is turned on; a null f.l. or b.s. gets
  STRAP II's substituted number (not stated here; the `DD` and `DR` defaults are in 3.12 and 3.18).
  An ambiguous op with an explicit dds is resolved now.

Ordering of entries in the coded expression area [12]: unevaluated dds first, then the
address fields in statement order.

**Box 27 ME [23].** `Bcfldx` := `Ibuffw`.

**Boxes 30A-32 [23, 97].** MCP bit in op index on: MIOD, then box 38. Not MCP and not a
comment: turn on `Fiod`. MCP ops are legal only as the initial instructions, comments
excepted; later ones get an error and print but are not punched [23]. Error 102 [178].

**Box 33 [15].** Pseudo-op branches. Text path: pseudo-ops go to box 63 ff., others to
34. Chart labels are opposite; see 8.

**Box 34 MEA [23].** Put length of a non-ambiguous binary-producing instruction in
ZILBO (DD and DR handled separately). Turn on ZIFBO and ZIFP2.

**Boxes 35-37 [23-24].** Loop GETFLD; the counter's start is taken from the first of the
op's fill index words, located by the value field of the op index word; up to that many
times. Per field: step `Field` and ZINFLD. Turn off ZIFALL. No reset of `Bcfxtx`, which
GETFLD updates. Two or more fields on an ambiguous op makes it VFL: change the unit.
On a `$` in an address field see 3.6.

Too many fields: error 40 EXTRA FIELDS [176]; test not shown on the chart.

**Box 38 MEDAF [24].** Relay GETCHA until `;` in $3, real or false. Other characters only
enter the statement buffer.

**Box 39 MEDB [24-25].** `Ibuffw` := first bit after the coded expressions, from `Bcfldx`.
GETFLD does not update `Ibuffw`.

**Boxes 40-41 [25].** First unit of block with name: turn on ZIFNME; store check digit in
ZINAME. DDI and SYN must each have a name [25].

**Boxes 42-43 [25].** Compute ZILSST. Round `Ibuffw` to a full word so the image starts on
a full word, except for a comment card block and a B-type card block. The buffer holds
nothing after the last non-blank. Strip the ending semicolon. MOVE the image in. Update
`Ibuffw` past it.

**Box 44 MEDC [25].** ZILCFD = bits of coded fields. Pass 2 locates the image at unit
location + fixed size + ZILCFD.

**Boxes 45-49 [17, 25].** First unit of block: if named, turn off `Fnosym` and form the
symbol table entry (49); if not, turn on `Fnosym` (47). The phoney entry for a pseudo-op
that should not have a name is also set up here: see error 41 [176, 204, 25]. SYN and MCP
entries were made in their own subroutines [25]. Fields carried over [13, 25]: ZINAME and
counters common to unit and entry (Zstcnt [173]); length of binary output; coded
expressions for a P-mode dds of a still-ambiguous op; explicit dds of a DD; coded
expression for the dimension of a DR. The exact function positions are UNSPECIFIED.

**Boxes 50-53 [17, 25].** Last unit of block (`Fblend` on): if `Fnosym` = 0, ADDORD the
entry, with tail appended if a NOP/branch set by MQTAIL is a branch; if ADDORD says
multiply defined, MULTI (3.22); GNLOAD. If `Fnosym` = 1, leave it on and go to 54. A block
ended by an explicit `;` has `Fblend` off here, so the entry waits for the false `;`
(9G).

**Box 54 MEF [25].** OR six flags into word 5. The intermediate error-flag buffer is
separate. At end of Pass 1 only suppress can be on. Which of bits 25-29 is which is
UNSPECIFIED.

**Boxes 57-59 [26, 173].** INTOUT; step unit counter; if not END, go to box 2.

**Boxes 60-62 [17, 24, 26].** END with `;` from GETCHA: INTOUT's special call ends the file
with a particular index word that lets INTIN detect the last unit. Enter $00 in the symbol
table, vle a SYN-like coded expression of two data: symbolic portion, absolute portion [24];
Pass 2 ORs $6, $7 into its fields per unit [24]. Then ZZXY between-passes: load Pass 2,
`Fpass1` off and `Fpass2` on, console display, enter UITER [26].

### 2.3 Pseudo-op branch: box 63 ff.

DD or DDI: MQDD (DDI is marked but treated as DD in Pass 1) [26]. Otherwise digit select
on the pseudo-op number. The number is used in three phases; they are in each of three
digit-select tables [22, 196]. Chart AE [18]:

| Ops | Route | Page |
|---|---|---|
| PUNFUL PUNNOR PUNORG PRNS PRND PRNID; SKIP NOPUN NOPRNT PRNOR; PUNALL SPNUS PRNTALL NOSEQ RESEQ | box 38 only | 18, 27 |
| DUPLI | MDUP (text), box 38 only (chart); see 8 | 18, 27 |
| PUNID | MPUNID in text, NPUNID on chart, then 38 | 18, 27 |
| TLB SLC END SLCR | MQL: set Pass 2 indicators; GETFLD the field; set GETFLD count here | 18, 27 |
| EXT | MX, then main flow for second unit | 18, 27, 128-129 |
| SYN | MQS | 18, 27, 121-122 |
| DR DRZ | MQR, MDIMRF | 18, 27, 116-120 |
| PUNSYM | MQP | 18, 32, 114-115 |
| SEM REM | MQM | 18, 32 |
| TAIL UNTAIL | MQTAIL, MQT | 18, 32, 123-125 |
| LINK | MQLINK | 18, 32 |

Chart page ends there, with its line continuing; relocation ops are not on it. Relocation
behaviour is in 3.26. XW, CF, RF, VF, CW, INDMK, CNOP are not in the table because they
produce one piece of binary of predetermined length [27].

## 3. Routines

Listed in contents order. "Errors" gives numbers from the list [176-179]; flow charts print
only ERROR MESSAGE, so a box number gets a message number only where the text names it or
one candidate exists.

### 3.1 BOPSER [65-67]

Call: `SIC, $15; B, BOPSER`; `, address of control block(I)`; `B, fix-up` (not found exit);
normal return (found). Control block [67, Figure 11]: 0-23 test-word address; 24, 25, 27
unlabelled; 26 BOPSER's indicator, shown 0, set only by BOPSER; 28-45 bit length of an
entry; 46-63 number of entries; then `DRZ(BU), N` for the pairs. N = ceiling(log2(entries)).
Restrictions: table ordered; test word and entry minimum are 64 bits. Output: VF of `Llxw`
= address of the function of the entry.

Algorithm: index registers $7, $8, $9 hold addresses of increment list, table, decrement
list [67]. Null table test gives LZC; max tests = 18 - LZC, saved in count of $7 [67]. First
search of a table builds increment/decrement pairs via LLNEW/LLZERO [66]: repeatedly halve
remaining count, odd count first time adds 1 and sets the first-odd indicator, later odd
adds 1 and an extra pair; each pair = count times entry length, positive as increment,
negative as decrement. First probe = (table location - entry length) + first increment. On
compare: equal exit found (compute function address, LLEND); not equal decrement count;
zero exit not found; else box 12 asks whether the next entry to be tested is higher (HIER:
LLACHI, use the increment) or lower (LOER: LLACLO, use the decrement) in the table; box 15
steps both list locations; back to the compare [65].

Users: MAIN (both op tables), CPLTSY (system symbols) [67].

### 3.2 CCA8 [68-69]

Call: `SIC,$15; B,CCA8`; `,A(I)` card-code buffer; `,B(I)` A8 buffer; `,n(I)` count; `B,fixup`
error return; normal return. Table look-up by 12-bit card code; a zero field in the table means
illegal. On illegal: reference index word in right half of accumulator: value = address of next
card-code character; count = characters remaining excluding the illegal one; exit via error.
Re-entry: keep $15, load the legal 12-bit substitute at accumulator offset 107, `B,0($15)`.
Preserves indicators, masks, index registers. User: XINPUT. The table contents are in a table the
guide does not reprint (pages read). Error 79 (GETCHA) by message [177]; coprocessor entry 3
[180].

### 3.3 CPLTNM [70-71]

In: first character in $3; radix in 8-bit `Gfsrad`, zero means 10 (zeroed in instruction
initialization), up to 16 with A-F = 10-15. Call `SIC, Cpltnz; B, CPLTNM`.

Loop in floating point: PR := PR * radix + digit; a digit >= radix gets error 63 and is still
used; GETCHA; repeat while alphameric. Out: first following character in $3; number at accumulator
offset 64 as 24 bits with 3 marker bits `110` [71, Figure 12]. Users: GETFLD, MAIN (F-entry),
MQDD (radix; g.p.). GETFLD does not collect numbers of a numeric DD's statement field [71].

### 3.4 CPLTSY [72-76]

In: first character (`$` or alphabetic) in $3; target in VF of `Bsymbx`. Call `SIC, Cpltsz; B,
CPLTSY`. Users: MAIN (P-mode), MQP, MQDD, GETFLD [74].

Box 1: zero length counter, levels counter, if-system switch; set NOP/B switches; registers to
`Bsymbx` buffer and CPLTSY's word buffer. If `$`: system switch on, blank the buffer, max 8
characters excluding `$`. Else max 128.

Boxes 2-11A: for each character: over max → error (49), skip to tail (box 16). Add to counter.
Store in CPLTSY's buffer (system) or at `Bsymbx` (programmer). GETCHA. Alphameric: repeat. If
system and next character `$`: error 51, to box 16. System otherwise: box 12. Not system: box 14
moves tail control data to CPLTSY's buffer, box 15.

Box 12-13B: symbol was just `$`: Figure 14 configuration at `Bsymbx`: 7 bits `0000000`, then `$`
as the byte `00101011`, then two zero bytes, then one zero bit; `Bsymbx` updated to that zero bit,
31 bits on; `Gfdol` turned on to tell GETFLD the type of re-entry [75-76]. It forms part of the
symbolic datum of GETFLD's expression [76]. The count field is shown zero, not 3; see 8.

Box 15, `$` after a programmer symbol: tail follows.

Boxes 16-29, each tail: GETCHA; terminator: box 24. Alphameric: collect in CPLTSY's buffer. `$`:
box 22. Otherwise error (62), box 24. Box 22: no tail characters: zero the current level field in
control data; then 28. Else step tail count, ADDORD into the tail table; if already there,
decrement count so TAILOR's data keeps the highest number [74-75]. Store the number in the level's
field, 28 recompute levels in effect, 29 step level counter, to 15. Tail on a symbol overrides any
existing tail on the same level for that symbol only [74].

Boxes 30-31: tails in effect: append if length permits; n + 1 bytes: a `$` character then n level
fields [75]; n from last calculation. Error 83 may be this; test not shown. See 8 for `*`.

Boxes 32-41: BOPSER in system symbols (8 characters, blanked background). Not found: MBSPEC; no
help: error 56. If found: `Cpldds` gets the dds; accumulator at offset zero gets the datum: Figure
13 draws prefix `11100` + 24 bits (location of constant, or value) at the low end, with sign byte
`0000S000`, S=0 regular, S=1 mathematical constant [75]. Fig 25: `a` constant, `b` unavailable at installation, `c,d,e` mode, then F.L., B.S.
13 bits [193]. Copy dds to `Cpldds`. If found but marked unavailable, or still not found: symbol
stored at `Bsymbx`, `Bsymbx` updated. An updated `Bsymbx` tells the caller: no value, or programmer
symbol [75]. If MBSPEC altered it: error 129 [178] (box 41; one candidate). For a constant, MQDNUM
sees a negative location [107].

### 3.5 GETCHA [77-79]

Call `SIC, Getchz; B, GETCHA`. Out: character in $3. Functions [79]: give characters; name; symbol;
statement to `Bsyst`; block end via `Fend` (`Fblend`, see 8) and false `;`; coprocessor.

Flow:
1. First entry: XINPUT, set up coprocessor table, switches [77].
2. Error from MAIN: coprocessor if it wants control, else fall through.
3. If not name-processed: inspect column 1. Illegal char (coprocessor char): coprocessor, or error
   80. Quote: save in statement buffer; skip name. Else process 2-9: illegal character: coprocessor
   or error 81 and "appropriate corrective action" [79]; otherwise save in name and symbol buffers.
4. Next statement character. Exhausted: end of statement field, 5 below. Fetch; `E` of `END` tested:
   coprocessor (entry 4) only when `Hhcom4`. Save in statement buffer. Comment from 1-9 is passed once
   to MAIN; while within such a comment nothing more is given. Else set char for user and exit.
5. End of statement field: if END card, go to 6. Else next card by XINSP2 when inserting, else XINPUT.
   Continuation: process its name field, keep going. Otherwise:
6. End of block: if named GNLOAD; reset; set `Fblend`, false `;`. Exit.

Comment rules [79]:
- In 2-9 of initial: entire block is comment; comment char is written over column 1; blank the char
  in the name field.
- In 2-9 of continuation: rest of that card comment; name may continue on following continuation
  cards; statement of those is comment.
- In column 1 of initial: entire card comment.
- In 10-72: rest of the unit is comment. Every character goes to `Bsyst` and to MAIN; MAIN relays till
  `;`. With comment from 1-9, MAIN sees only the first and then the block-end.

INFERRED: a `;` inside a statement comment ends the comment, since MAIN stops relaying when `;` is in
$3 [24, 79].

Errors 10, 79, 80, 81, 126, 135 [176-178]; 126 FORCED COMMENT, 135 ID SEQUENCE have no stated test
except that an illegal continuation card from a coprocessor becomes a comment with an error [182]. See
also section 7.

### 3.6 GETFLD [80-86]

In: `Bcfldx` VF full-word buffer start; `Bcfxtx` VF first bit after buffer; `Gfchar` on if $3 already
holds the first character; `Gfnogp` on if g.p. forbidden. Call `SIC, Getflz; B, GETFLD`. Out: `Bcfldx`
updated, $3 first character after field, `Fsymb` on if a non-absolute-system symbol occurred [83].
Users: MAIN, MQM, MDIMRF, MDIMRT, MIOD, MDUP, MX, MQS [83]. `Bcfxtx` not full word is rounded down.
The end of the buffer may be used as intermediate store [83].

**Syntax control [83-84].** Separators: `(` `.` `+` `-` `*` `/` `)`. S-code (what precedes): 0 B
beginning or unary minus; 1 S symbol, number, or parameter; 2 SZ preceded by decimal; 3 O operation;
4 `.` preceded by S; 5 `.Z` not preceded by S. U-code (what follows): 0 symbol/number/parameter; 1
`+ -`; 2 `* /` or END; 3 `.`; 4 arithmetic `( )`. Both start at 0; U from the current token; S from
the last look-up. Each cell yields legal/illegal and the new S. **Matrix cells: UNSPECIFIED**; only
the legends exist (sweep: "matrix" on p.83 only). Constraints that exist are in Appendix F [207]:
index last in field; subscript immediately after its symbol; g.p. last; index and g.p. not both; g.p.
not first; n of `.n` absolute; g.p. not inside parentheses except in a DD's dds; no implied
multiplication. Appendix C operator list [198] shows examples: `2.3`, `A.B`, `2.`, `2.+3`, `.2`,
`2+.3`, `-7`, `A*-2`, `2-3`, `A-2`.

**Flow:**

- Box 1: round `Bcfxtx` down; `Gfpcnt` = 0; `Gfnull`, `Gfgenp` off; position in `Bcfldz`; $2 past the
  first prefix bit.
- Box 2 GFCBIN: `Gfsave` = 0 and push buffer one word; if `Gfrads` store its value in `Gfsrad`.
- Boxes 3-4: GETCHA unless first character held.
- Box 5: `(`: zero `Gfgenp`, `Gfrads`, `Gfsfrd`, `Gfsfxa`, `Gfsfxb`; `Gfpcnt`+1; `Bcfldx` back three
  bits, removing prefix; `Gfapan` = 1; to box 2.
- Boxes 6-8: `Gfsfsb` off; dispatch.
- Box 15, 22-29: symbol or `$`: reserve 10 bits; CPLTSY. System and defined: back 10; prefix, value,
  dds; forward 43. `$`: prefix and value, forward 20; add `.L` and `+` operator [24, 84]; to 58. Else
  prefix and length; `Gfsfsb` on; to 58. Coded `$` is datum $00 (24 bits) and an absolute datum of 24
  zeros, operator `.L and plus` [24]; the `$` in an address field must be followed by `;`, `,`, `+`,
  `-`, `*` or `/` for this [24].
- Boxes 16-17: number: CPLTNM; `Gfrads` off; prefix, datum, dds, forward 28; to 58.
- Box 58-59: datum count +1, end of datum; if last operator was `.L` change it to `.+`.
- Boxes 30, 39, 47, 52-55: `+ - . * /`: store operator and datum number; set U; `Gfspar` = 1; op count +1;
  GETCHA; U,S check, failure to box 9; save S; `Gflong` check; to box 5.
- Boxes 31, 32, 40, 41: otherwise check end legality. Not legal and not null: box 9. Null: `Gfnull` on.
  Pull up buffer.
- Boxes 33-35: `Gfpcnt` = 0 and null: null prefix; $2 forward 6.
- Boxes 36-38, 45-46, 50: g.p. forbidden and none: exit. Forbidden but one follows: GETCHA to end of
  instruction unit (error 108). Allowed and none: end bit 0, exit. Allowed and one: g.p. heading; $2
  forward 8; zero first `GETFLD` word; to box 2.
- Boxes 42, 48: `Gfpcnt` nonzero: `Gfnull` off; neither `,` nor `)`: error 67.
- Boxes 56, 60: `,` or `)` and `Gfsfxb` on: `)` subtracts from count; GFZA; prefix `1000`.
- Box 61: end-of-subexpression, $2 forward 1. Boxes 62, 57, 51: `,` indicates subscript. `Gfsfxb` on:
  process it. Off: `Gfsfxa` off: set it; on: error 66 [85]. Box 63: other: `)`: error; else GETCHA.
- Boxes 43, 44, 49: not null: GFZA. No operator made arithmetic parens: mark subexpression.
- Boxes 64, 73: one absolute datum and `Gfsfxa` on: error.
- Boxes 76-78, 82, 83: cannot be arithmetic: `Gfsfxb` on, to GFZA. Can be but not `)`: error 67. `)`: op
  and datum number to buffer; GETCHA; `Gfspas` on.
- Boxes 65, 66, 79-81, 74: test g.p. or radix: neither: `Gfsfsb`; off and zero operators: `Gfrads` on;
  already on: error 66. Box 74 value goes in `Gfsrad`.
- Boxes 67-70: syntax allows end and no g.p. yet: `Gfgend` on; value in `Gfgpv`; remove op.
- Box 71: neither `)` nor `,`: error; `)` check for g.p.; `,` with count not 1: error.
- Box 9-10 and 11-14, 19-21, recovery: restore buffer, null coded expression, error, then scan: `, ; '`
  with count 0 exits; `)` tests count; `(` adds.

Errors [176-178]: 8, 9, 66 (named Syntax Error [85]), 67 (Inappropriate Character [85]), 68, 82, 108.

Null coded expression (illegal combination) is evaluated later as zero [24, 83]. GETFLD does not touch
`Ibuffw` [24]. `Bcfxtx` is set by caller and updated in the loop [24]. SYN uses a separate buffer
indicator since `GFLONG` handles only the unit [27].

### 3.7 GNLOAD [87-88]

In: $7 VF = name location, CF = count; `SIC, Gnexit; B, GNLOAD`. CF zero means end of file. Two
buffers, written to disk as filled. Record: byte count of A8 characters + 1 (check); check character,
0-9 repeating; n A8 bytes, names under eight assumed eight long. End of second buffer: all-ones byte.
File end: all-zero byte. The flag in $7: name is last; store count zero, switch 1 on. `Gnflag` on if no
room in second; write; return to first [88]. Check digit progression is here; Pass 2 synchronous
check is on ZINAME/Zstcnt [173, 25].

### 3.8 INTOUT [89-91]

`SIC, Intouz; B, INTOUT`. `Ibuffw` holds next full word available. Three buffers A, B, C [90]. Box 1:
count of unit = `Ibuffw` - `Icwa`; goes in count field; new control word address = `Ibuffw`, in refill
field; `Ibuffw` + 1. Box 2: past current buffer end? Box 11: flag bit 25; Boxes 12-14: on A, area-A on;
write. Boxes 3-4: `Intcnt` is stepped by each EOP; if zero, or (after checks) at least ten free words in
C: return. Box 5: area-A off means last written was C, update `Ibulwa`. Box 6: subtract one; rotate
last-word table. Box 7: zero: wait for EOP. Boxes 8-10: area-A on: turn off, move incomplete unit to A,
refill of last control word updated, new control word in A. IOFULL (entry shown at 89 before 7) is
called when an overlong unit needs room [89, 98, 101]; its calling sequence: see 2 in [90] (identical
to the normal call as printed). Message: instruction too large [179]. END call: see 2.2.

### 3.9 MBSPEC [92-93]

`SIC, $15; B, MBSPEC`; `, address of test word(I)`; `B,fix-up` no further help; normal return possible
help. Preset `Llbts` zero before work on a symbol; test word 8 A8 characters [93]. Box 1 turns off
`Llbts.8`. The eight indicators stay as last set between calls.

Starting from the second character (Box 2: "second or any subsequent character"), substitutes in the
pairs `0`/`O`, `1`/`I`, `2`/`Z`, `5`/`S`, either direction [93]; two tables hold the set. Order as printed:
`SXXXXXXX, XSXXXXXX, SSXXXXXX, XXSXXXXX, etc.` [93]; INFERRED: a binary count over the possible-error
positions, low position first [92]. Any substitution sets `Llbts.8` and exits help. No help exit: original illegal form. On a later
successful search with `Llbts.8` on, the user gives error 129 [93].

The list on p.93 shows position 1 can be substituted though Box 2 says from second; see 8.

### 3.10 MIBA [94-95]

Entry: branch from MAIN; mnemonic in `Bop`. Saved and restored one index register. Three returns to
MAIN: continue; re-look-up after MBSPEC; illegal [95]. Unit errors: not `B...` or not legal, MIERR on;
then Boxes 10, 22: MBSPEC; possible help: error message, return correction. Candidates 1, 129.

Table: one entry per indicator, mnemonic to 4 characters plus number 0-63 [95, 190]. Variations: BI,
BIZ, BZI, BZIZ. Box 3 subtract 8 from the length. Box 4: over 32 bits to 11, skipping the first search.
Search (chart label SEARCH): op minus first character found: BI; not found, last `Z`: blank it in temp:
search op minus first and last; 2nd `Z` and op not six characters: search minus first and second; then
last `Z`: minus first, second, last. Bit settings: see 8. Then Box 7: op code and indicator number in the
skeleton in the unit; Box 8: op index into unit and $5. Op code bits are UNSPECIFIED here.

### 3.11 MIOD [96-97]

From main, not called. REEL and IOD have the MCP bit. `Fiod` should be off (else error 102) [97].

IOD: name required, else error 103 [178] (Box 5). Save unit buffer control address; GETFLD the type
field; reset to saved address, erasing it, leaving `,` in $3 [97]. Step `Field`. Not comma: Box 7B
error. Else GETFLD exit address; step `Field`, ZINFLD +1. ZINFLD counts only this field [97]; the error
counter was stepped twice. Reference-number counter (starts zero) +1, kept in ZILPMS. ZIFP2 off so NMCP,
not DECODE, has the unit. Name: symbol entry into `Msyte` as MAIN would do. ZIFALL on so DECODE does not
see it in Pass 2's main flow; NMCP calls VALUE [97]. Charts 11 and 14 print the opposite settings; see 8. Exit to Medaf. 104, 143 (null
exit), 144 (no B on IOD) are the available numbers [178].

REEL: ZIFALL on. Name error 105. Phoney symbol entry [97, 96]. Chart test seems inverted; see 8. To Medaf.

### 3.12 MQDD [98-100]

No calling sequence; branch; ends at Medaf; dds is complete [100]. ZIFDD set in Box 1 INFERRED ("set DD
unit indicators"). `Ibuffw` to ZIOTPT.32 [26, 100]. Variable format is Figure 26 [193].

Flow:
- Box 2: dds given? No: alphabetic → BU, 8, 8 [98]; else N, 64, 4 and error (candidates 42, 46). Chart
  connector routing shows these not rejoining at 3; see 8.
- 3 MQDDAA: `Ibuffw` to ZIOTPT.32. CK.29 re-enters here for a further data field.
- 4, 12, 18: too little room: IOFULL move unit to buffer start and adjust.
- 5: alphabetic: MQDALF. Exit to Medaf from there [100, 26].
- 6-7: GETCHA; `(`: 14 MQDEMB, CPLTNM, radix or g.p. 19: g.p.: 22 zero coded expression, 23 GETFLD g.p.,
  to 27. Radix: to 8.
- 8: `Bemv`: 15 store Fn; 9.
- 9: next `.`, hex or digit: 16 MQDNUM; 20 store; 24 g.p./radix bit (turn off): 33. Else: 25.
- 25 MQDC: special sign: 21 store, 25. Otherwise 26.
- 26 MQDE: `X` special exponent: 32 evaluate (MQDNUM), store, to 25. Otherwise 27.
- 27 MQDK, 28: `.` or `(`: 33 MQDEMA G.P. or radix. 36: g.p.: 23. Radix: 37 error (65). 29.
- 29 MQDL: `,`: 3. 30: `;`: Medaf. Otherwise 31 error, 35 GETCHA, 29.

Variable portion, Fig. 26: `a` = 1 (Fn entry mode): 11 bit f.l. + 12 bit exponent + 96 bit fraction unnormalized;
otherwise `a` = 0: 12 + 96 normalized [26, 193]. Then 8 sign byte, `b` normalized mode, `c` special
exponent, 12 special exponent, `d` g.p. present, 6 g.p. n, g.p. expression if `d`, `e` repeat [193].
Radix 2-16 [26, 107]. Errors: 45, 65 by list [176, 177]; 109 RADIX AT END is MAIN's [178]. OUTPUT
adjusts to final form [26]. The text's "Boxes 13, 14" for sign [100] are 25, 21 on the chart.

### 3.13 MQDALF [101-103]

In: `,` in $3; `Bem+1.0` VF terminating character; `Bemt`, `Bemu`, `Bemv`; `Ibuffw`; `Ibuflw` upper
bound. Out: `Ibuffw` updated; next non-blank after terminator in $3.

Box 1: `Gcaz` on. Each input: terminator stops; block end stops (with false `;` still in $3). Chart: first
character tested in 2, 3, then 4 sets up. 4: dds absolute or symbolic. Symbolic: keep 8 bits per A/IQS,
12 per CC; leading zeros; OUTPUT truncates. Absolute: keep the b.s. bits of each, except CC forces 12
[102]. 5-9 dispatch; 10 count; 11 update; 12-13 `IOFULL` if full.

End [102]: ZINFLD count field = character count. ZIOTPT 0-23: if symbolic b.s., characters, bit 24 = 0;
if absolute, bits, bit 24 = 1. ZIOTPT.26: 0 A, P, or IQS; 1 CC. ZIOTPT.27: 1 if OUTPUT may truncate.
Text "A, P, or IQS": chart has CC, IQS, A only; see 8. Errors: 84, 85, 125 [177, 178].

### 3.14 MQDNUM [104-107]

Call `SIC, Mqdnuz; B, MQDNUM`; first character in $3. Out: non-blank after in $3; double in accumulator.

Levels: each `(` non-g.p. pushes an eight-word entry at `Mqnnd`: result pairs for orders 1, 2, 3 and two
misc. words [107]. Order 4 is common, from DNUM. Chart calls it 0th level. Operators: `+ -`, `* /`, `**`
(exponent whole, range) [107], and `*/` meaning negative power by chart [104, 106].

Each new datum: DNUM or CPLTSY, result to order 4 [107, 104]. CPLTSY system symbol constant: negative
location [107]. Not true system symbol: error, zero result (CG.38, 41). Combination rule [107]:

1. Any operator: combine 4 and 3 as indicated; result in 3; indicators of 4, 3 to transfer.
2. Also on `*` `/`: combine 3 and 2; result in 2; set 3, 2 to transfer.
3. Also on `+` `-`: combine 2 and 1.
4. Set indicator for the new operator.

Switch: position 1: MQ4 (or MQ2 at second order), position 2: negative exponent (or MQLL4), position 3:
move. Box 44 is add or subtract. End [105]: MQDNC1; `)` with an open level: housekeeping; result becomes
order 4 of previous level. `)` without mate: error, set results. Otherwise proper end `,` `'`(see 8) `;`
`S` `X`: set results and exit; otherwise error, zero, exit. Chart 5 sends `(.` to G.P. by CG.21. Hex
letter after no datum: to DNUM. No list entry names MQDNUM (see 7).

### 3.15 DNUM [108-110]

Call `SIC, Dnuz; B, DNUM`. In: first character in $3; radix in `Drad`, set by MQDD. Out: double in
accumulator; next non-blank in $3. Operand: `[+-]n`, `[+-]n.n`, `[+-]n.nE[+-]e` [110].

Flow: indicators A (point), B (specified exponent), C (radix not 10), D (radix above 10) off. Then:

- Sign: `-` sets inst to subtract; GETCHA.
- Digit 0-9 (or, D on, a letter that could be a number, A-F [110]): if below radix, P.R. := P.R. * radix
  + or - n; if A on, running exponent -1. Digit too large: error (47 or 63 by message), used anyway.
- Non-digit legal letter otherwise: point: first, A on; second: error 48. Loop GETCHA.
- End: C on and A on: DNADJ on the running exponent with this radix, A off. C is turned off.
- `E`: A, B on; radix := 10; save P.R.; GETCHA; parse the exponent by re-entering at 5 with
  running sign reset.
- End with B: add e to running exponent; restore results. Exponent nonzero: DNADJ. Exit.
- DNADJ: `MQ4` radix^exponent, then `MQ2` times result.

Error 50 is MORE THAN ONE E; no test on chart. Results are floating double [110].

### 3.16 MQDDPA [111-113]

Accumulator results [112]. `MQ1` A+-B: VF $7 A, VF $8 B (`Mqiz`). `MQ2` A*B (`Mq2z`). `MQLL4` A/B (`Mql4z`).
`MQDDPP` A**B (`Mqddpw`). `MQ3` A**-1: VF $8 A (`Mq3z`). A, B double precision. B whole in range
[112]. Division: Q1 + R1/b1 - Q2*Q1 where Q1 + R1/b1 = (a1+a2)/b1, Q2 = b2/b1 [111-112]. MQDDPP:
zero base: error 112, result zero. B out of range: error 113; bound used (printed values: see 8). Fix
to 18-bit "new" exponent, on bit means table entry base^(2^n) in a 36-word buffer; multiply selected
entries [113]. Zero exponent: one; one: base [111]. Negative: MQ3 [111].

### 3.17 MQP [114-115]

Via digit select with `,` in $3. Each field: GETCHA. Alphabetic: `Bsymbx` one byte past free area so the
8-bit count can precede; CPLTSY; store; update; step ZINFLD and `Field`. Then `,` repeats; not terminator:
error, exit. Numeric first: error (64), skip to `,` or terminator. Null or number-started skipped [115].
List follows fixed format so its location = unit + fixed length [32]. Same SYN cards as NQBTP, NPNSYM [32].
Also: "first, if the symbol begins with non-alphameric [115]" stops; chart: 2 no → 11 no → connector 2 at 8.

### 3.18 MQR [116-117]

Via digit select. Box 1: not ZIFDDS: `FPDDS`=1, error 46, N,64,4, filled [116, 27]. No field: exit. Set
not-all-processed indicators. No name: MDIMRF with MAIN's words, `Ibuffw` at the free variable area; Box 12
adjust. Named: enter MDIMRF by MDIMRT. Before VDIMEN save dim location in ZIOTPT VF [27, 117]. VDIMEN tries;
product goes negative in VF of ZIOTPT now or Pass 2; negative means computed [27, 32]. Default rule: null dds
gets N,64,4 [27]. Entry goes to the unit; named too, prefixed by header bits in vle [27].

### 3.19 MDIMRF, MDIMRT [118-120]

`SIC, Mdimrz; B, MDIMRF` for unit (no name); `... MDIMRT` for vle (SYN, named DR/DRZ). $3 holds character before.
`Mdimrx` free area. Out: $3 character after; `Mdimrx` updated; $1 VF dim ref address [119].

MDIMRT: bounds from table management block; save vle start; ID `D` (6 bits); `LPFLGB`=1. Both: 5-bit count zero,
bit not evaluated, save start. GETCHA. `(`: `LPFLGA`=1, step `Field`; GETCHA. Each dim: start; GETFLD with first
character held, no g.p.; shorter than 24 bits: pad (padded prefix [120]); count +1. `,`: no parens: error 52;
GETCHA loop. End: parens: `)` else error 54, GETCHA. Vle: finish heading: 13-bit length, update table. VDIMEN
later overwrites with 24-bit products and turns the if-evaluated bit on [119, 194]. Note: primitive entry
total length must be >= 24(n-1)+6 [194]. MAIN inserts the address in the function [119].

### 3.20 MQS [121-122]

Via digit select with `,` in $3; out with comment or `;` in $3. No name (`Fname` off): error 43, exit to collect
[122]. Zero `Msyte` and set vle control; mark as SYN. Move mode, f.l., b.s. indicators and uncomputed expressions
to `Msyte`; erase in unit; `Ibuffw` stepped back: unit free = first bit after fixed part [27, 122]. Chart label
on this test: see 8. No address: error 44, mark unused. Else: GETFLD to `Msyte` with upper limit changed and an
indicator set; `Field`+1 even though one field only. Turn off ZIFALL; leave ZIFP2 off: UITER and VALUE decode it
[27]. Dimension: MDIMRT; address in the SYN's vle [27] (not shown on chart). Then reset; `Bcfldx` locates where
to put GETCHA's buffer [122]. The symbol enters at block end [27].

### 3.21 MQTAIL, MQT (TAILOR) [123-125]

Data [125]: ten 8-bit level bytes, in-use count, highest level, number of latest tail; preceded by A8 `*` so MAIN
copies a prefix directly. CPLTSY overlays on its copy. Tail table: own control block; entries [190-191]:
four characters or vle; number.

MQTAIL: GETCHA. `;` `'`: error 59, treated as 1st level `;`, goes to the untail branch. Switch in MAIN to
branch. `(`: GETCHA; digit: save level, GETCHA; `)` else error 61/62; or `)`: GETCHA: level 1. Alphabetic: level 1.
Otherwise error. Complete in `MQTBUF` (chart); count +1; ADDORD; present: count -1; store number in level field
and count; raise in-use; zero between [125]. Exit computes levels and turns NOP if tail 0.

MQT: GETCHA; `;` `'`: level 1. `(` digit(s). `10`: zero all. `9`: first nine. Else zero specified; level over 8:
`n mod 8` zeroed [125]. Level over tailed: error 58; equal: NOP. Exit: scan back for highest nonzero [125].

Character collection for the tail body in MQTAIL is UNSPECIFIED; the chart has `MQTBUF` only at box 19.

Name/CPLTSY uses are in 2.2 and 3.4 [25, 32]. Levels specified 1-10 [125].

### 3.22 MULTI [126-127]

In: ADDORD says multiply defined; `Msyte` holds the new function [127]. Legal requires new and old both SYN and
values equal; else contradicted: dictionary not changed; old parameters kept; Zst23 INFERRED [170]. Legal:
inherit dds, dim, index from old if old has them, or if new does not; never overruled [126-127]; dimref, dds ref
locate them; mark new vle (Zst22 INFERRED); change dictionary. In all cases a vle entered for every name since
ANEXT needs one [127]. Update table (count unchanged). How values compare in Pass 1 is UNSPECIFIED.

### 3.23 MX [128-129]

Entry `(` in $3; exit `)` in $3. ZIFP2 on; ZIFALL off. Three GETFLD fields L, LP, N, each `Gfnogp`. Missing N
after LP `)`: special encoding. Not partitioned: box 14-16; rest of block collected; unit adjusted to
`SIC, $15; BE, 0` (see 8); error 107 by message. Normal: main flow makes second unit. Parameters' unit done at
`)`; second unit at `;`. OUTPUT does extraction. Field counter per fields, INFERRED from "fields" [129].

### 3.24 XINIT [130-131]

`SIC, Xret; B, XINIT`. 1: COMREC first in chain: word 8 set: System Input, card code, blocking factor one [131];
`Spool0` on. Else 2: System Input per COMREC: `Spool0` on. Otherwise 3: arc address from word 8 bits 0-17 in
word 0 of input buffer; blocking VF = word 1. 4: bits 25-27 of word 8 digit-select the code; address in the branch
after `Xreada`. 5-6: bits 48-63 in `Xblkl` count and System Input sequence; disk: times card words gives the read
count. 8: word 1 COMREC temporary arcs; minus one starts name file; 1/32 name, 31/32 intermediate. COMREC format
is not in the pages read (see header).

### 3.25 XINPUT [132-134]

`LVI,15,$+2; B,XINPUT`; `,place`; `B,non-IBM return`; `B,EOF before END`; normal. `Xinsp1` unconverted: place,
spacer, `B,EOF`. `Xinsp2`: $7 VF source, CF cards, RF code; place, spacer, spacer. Flow: wait on `Xind2` [133];
XSP1 on: move raw. Off: convert; XSP2 on: off, $7 zero: last-insert, return. Else step. END: return. If blank: set
indicator. Count zero: refill, System Input or from word 1 of prior block; reset; else decrement. Blank card: back
to 1 [133-134]. Conversion: CCA8 or per the code [131]. DUPLI: `Xsp3`, `Xrepl` 0-17 n, `Xrep2` d: stacks n, gives
each; next n*d from duplicate block, then resumes [27]. Chart does not show this (sweep: `Xsp3` p.27 only).

### 3.26 Routines with no write-up

- MQM: chart [18], users of GETFLD [83], errors 110, 111. Text [32]: four-word mask in the unit, bit on = suppress,
  location in VF of ZIOTPT; GETFLD and VALUE for numbers; major mask updated on Pass 2 processing; no decoding.
- MPUNID (NPUNID): chars by `Gcaz`, stored in the unit; ZIOTPT VF locates; padded blank to 8 [27]. Error 55.
- MDUP: as in XINPUT; errors 96, 106, 145, 146, 147, 148.
- MQL: Pass 2 indicators; encode; loop counter; END alone in block when `Hhcom4` [27, 182].
- MQLINK: expression for `LVI, 15, $+2`; ZIOPX and $5 redirect; ZIFBO, ZIFALL, ZIFP2 on [32].
- Relocation: PUNREL turns on `Punrel` [186]. Other punch ops off through Pass 2. PUNFPC encodes both sizes; second
  may be blank. ENTER: entry for name; encodes. COMBLOCK: entry with Zstcom one, Zstcon block number 18 bits; no name
  error; still encodes. SLCRCOM: `Mupper` on; blank → common 0; else look up the name and take its number [186-187].
  Entries after it have Zstcom 1, Zstcon. Errors 140, 141, 142 [178]. Routing is not on chart AE.
- GFLONG, IOFULL, GFZA: no sections.

## 4. Symbol file and name file summary

`Bsyst` to unit; name buffer to GNLOAD; symbol buffer to ADDORD [20, 79]. Name file: 1/32 of arcs [131]; symbol file:
memory always [79]. Check digit in both, plus unit [25, 88, 173]. `Symbol` counter is `Msyte` through Pass 1 [173].

## 5. ZIOTPT uses

| Unit | Use | Page |
|---|---|---|
| Binary op | skeleton, then binary | 19, 95 |
| DD | .32 location of binary | 26, 100 |
| Alpha DD | 0-23 length; 24, 26, 27 flags | 102 |
| PUNID | VF location of ID | 27 |
| SEM REM | VF mask location | 32 |
| DR | VF dimension, then negative product | 27, 32 |

## 6. Coprocessor [180-182]

Enabled by `Hhcom4` and table `Hhcopr`: `B,entry A`..G. Off: strict error, [180]. Conditions: 1 illegal column 1; 2
illegal name character; 3 non-IBM card code (XINPUT); 4 before END (GETCHA); 5 illegal op (MAIN); 6 bad entry mode
character (MAIN); G: want another card. Call: `SIC,$15; B,entry X`; `B,` not wanted; `B,` insert cards; `B,` want
another. $7: VF card, CF bits done, RF code (1 CC, 2 A6, 3 A8, 5 IQS), .25 code form, .26 no more. VF $3: entry 1 char;
2 zero; 3 12-bit; 5 next character after op, or ninth; 6 char. Hhcom5: END seen in insert. Insert exit: $7 VF buffer,
CF count+1, RF code, .25, .26, .27. Terminates good block first. Rest of error card lost unless reinserted; END must
be alone in its block; the coprocessor must find END itself on want-another; control only for original input [181-182].

## 7. Errors

Numbers and logic areas from the list [176-179]; the condition column is the message unless a text citation is given.
"Serious" is 1-28 [205].

| No. | Routine | Message | When |
|---|---|---|---|
| 1 | MAIN | ILLEGAL OP CODE | retries exhausted [22] |
| 2 | MAIN | ILLEGAL SECONDARY OP | not in table [22] |
| 3 | MAIN | ENTRY MODE WITH NON DD OPER. | UNSPECIFIED place |
| 4, 5 | MAIN | MORE THAN ONE SECONDARY OP; DDS | UNSPECIFIED place |
| 18 | MAIN | SYM TBL ENTRY MADE UNORDERED | UNSPECIFIED |
| 29 | MAIN | IMPROPER 1ST CHAR | AA.9 [14] |
| 30 | MAIN | MORE THAN ONE $ | UNSPECIFIED place |
| 31, 32 | MAIN | ILLEGAL ENTRY MODE; NOT CLOSED | UNSPECIFIED place; coprocessor entry 6 [180] |
| 33, 35 | MAIN | NOT CLOSED BY PAREN | UNSPECIFIED place |
| 34 | MAIN | THIS OP SHOULD NOT HAVE DDS | UNSPECIFIED place |
| 36-39 | MAIN | FL>64, BS>8, BIT STYLE, NEG COMPLEMENTED | "erroneously specified parameters adjusted" [23] |
| 40 | MAIN | EXTRA FIELDS | presumably box 37; UNSPECIFIED |
| 41 | MAIN | SHOULD HAVE NO NAME | phoney entry [25, 204] |
| 42 | MAIN | STRAP ASSIGNED DDS | null dds substituted [23]; candidate MQDD.11 |
| 43, 44 | MQS | NO NAME; NO ADDRESS | [121-122] |
| 45 | MQDD | UNATTAINABLE VALUE | UNSPECIFIED |
| 46 | MQR | DR OR DD WITHOUT DDS | MQR.8 |
| 47, 48, 50 | DNUM | ILLEGAL IN RADIX; 2 POINTS; 2 E | 17 or 20; 20; no box |
| 49, 51, 56 | CPLTSY | TOO LONG; 2 $; NONEXISTENT | 3; 11B; 34 |
| 52, 54 | MDIMRF | NOT IN PAREN; NOT CLOSED | 19; 22 |
| 55 | MPUNID | NO COMMA | |
| 58-62 | MQTAIL | | see 3.21 |
| 63 | CPLTNM | DIGIT INCORRECT | CPLTNM.5 |
| 64 | MQP | ILLEGAL CHAR | 12; 10 candidate |
| 65 | MQDD | 2 RADIX OR PAREN | 37 |
| 66-68, 82, 108 | GETFLD | | see 3.6; 68 and 82 place UNSPECIFIED |
| 8, 9 | GETFLD | VLE; SYM BUFF EXCEEDED | via GFLONG presumably |
| 10 | GETCHA | BUFFER FULL | statement or name buffer; UNSPECIFIED |
| 79-81 | GETCHA | CODE; COL 1; NAME | [79, 180] |
| 83 | MAIN | TOO LONG FOR TAIL | [75] |
| 84, 85, 125 | MQDALF | | UNSPECIFIED place |
| 96, 106, 145-148 | MDUP | | UNSPECIFIED place |
| 102-105, 143, 144 | MIOD | | 3.11 |
| 107 | MX | | 3.23 |
| 109 | MAIN | RADIX AT END OF DD | UNSPECIFIED place |
| 110, 111 | MQM | | UNSPECIFIED place |
| 112, 113 | MQDDPP | | [113] |
| 126 | GETCHA | FORCED COMMENT | [182] |
| 129 | MAIN | CHANGED INTO LEGAL | after MBSPEC [93] |
| 135 | GETCHA | ID SEQUENCE | UNSPECIFIED |
| 140-142 | MAIN | RELOCATION | UNSPECIFIED place |

I-O: XERR read, write; XINPUT COMREC bad; INTOUT too large [179].

MACHER [173]: inspects where expected data is missing. In Pass 1 returns to MAIN wind-up, not caller; optional dump
of the current unit. `Machez` holds the location. Error 7.

## 8. Gaps and contradictions

**Gaps**

1. GETFLD syntax matrix cells: not printed (3.6). The op table, secondary table, system symbol table and indicator table
   contents, and Zo bit assignments: absent from the pages read; plan line in `reconstruction_plan.md` S-1 agrees for the
   opcode table.
2. Chart boxes print ERROR MESSAGE with no number; most MAIN errors (3-5, 30-40, 109, 140-142) have no stated detection
   point. No error list entry for MQDNUM. Numbers 3, 4, 5, 18 and those in section 7 marked so are UNSPECIFIED by place.
3. MQM, MDUP, MPUNID, MQL, MQLINK, GFLONG, IOFULL, GFZA have no write-up (sweep: MQM pp.18, 83, 178; MDUP 27, 83, 178,
   179; MQLINK 18, 32); relocation pseudo-ops are not on chart AE.
4. TABMAN, ADDORD, VALUE, VDIMEN, ERR (37-62) define what Pass 1 calls; not read for this document.
5. Zst bit positions and function layout; assignment of ZIOPX flags 25-29; six vs. five flags listed by name [25].
6. `Msyte` layout, entry-mode grammar, tail text collection in MQTAIL, `Fblena` reset (see 9 below), MAIN's route for `$`,
   how MULTI compares values in Pass 1, handling of non-listed characters.
7. A8 card code table; `Qc` block contents. A8 values only for `$` by Fig. 14.
8. Whether box 53 GNLOAD or GETCHA.40 writes the name (both printed; see 12).
9. AD.46 annotation "TURN ... NO (OFF)" does not say what is turned off. If `Fname` is reset here, the later unit tests
   (MQS, MIOD, AB.9H) make sense; that is INFERRED. `Fblena` reset is likewise absent; chart AD.45 would otherwise see
   every later unit as first.

**Contradictions**

0. Figure 24 labels a three-cell field `abc` but prints the value `020` for SEOP [192]; a digit 2 cannot fit one bit.
10. Chart AB.33 sends pseudo-ops YES to AC.28 (MEA, binary path), NO to AE.29 (pseudo branch), opposite of Boxes 33-34,
    63-67 [15, 23, 26]. Reading at 170 dpi confirms the labels. Text followed here.
11. `Fblend` [20] vs `Fend` [79]. `Zifname` [25] vs ZIFNME [189]. `Zifpm` / ZIFPMN. `$X5` [95] vs `$5`.
12. Name file: GETCHA makes it [25, 78.40] and AD.53 is GNLOAD [17].
13. DUPLI: text MDUP [27], chart AE collect-only [18]. `MPUNID` text, `NPUNID` chart [27, 18]; the `N` prefix is Pass 2
    by Appendix D [202].
14. Comment terminal in MQDNUM printed `@` [107], elsewhere quote [14, 26, 183, 184]. MQDD.30 tests `;` only, while p.26
    expects comment also; a comment after a numeric DD reaches error 31 by the chart.
15. Tail marker: `$` [75] vs `*` [125]. Level bytes: `n` of up to 10, with `n mod 8` on level over eight [125] but explicit
    `9`, `10` boxes [124].
16. MIOD.11 TURN ON ZIFP2 and MIOD.14 TURN OFF ZIFALL vs text ZIFP2 off, ZIFALL on [96, 97]. MIOD.16: chart errors when no name; text and error 105 mean named [96,
    97, 178]; the phoney entry follows the name.
17. MQS.4 YES skips transfer, NO (IMPLIED) transfers [121]; text says transfer when determined [27, 122]. As labelled it
    moves dds for implied.
18. MIBA bits: text 29, 30 [95]; chart BI 30, BIZ 29, BZI none, BZIZ 28 [94].
19. MX.14 prints TURN ON NO-G.P. where an error is expected; MX.15 prints `DE,0` (`BE,0` at 22) [128].
20. GETFLD.77 chart `,`; text `)` [82, 85].
21. MQDDPP bound text: "B<2^-18 assigns -1 + 2^-18; B<2^+18 assigns -1 + 2^+18" [113]; range conditions are printed
    with the same relation, so the second clearly means > but the guide does not say so.
22. Figure 12 caption `$L`, text offset 64 [71]. Figure 13 caption says CPLTNM, on CPLTSY [75]; offset zero in text;
    figure's accumulator position is low-order.
23. MBSPEC Box 2 "second or any subsequent" vs list starting with position 1 [93].
24. MQDD.17 and .11 connectors do not rejoin at 3, 4 as drawn [98]; text [100] has no such step. MQDD text box numbers
    13, 14 for sign are 25, 21 on chart [98, 100].
25. MQDALF: `A, P, or IQS` [102] vs chart three modes [101]; p.21 has no P mode.
26. Chart DNUM numbers box 5 as `3` [108]; text uses 5 [110]. BOPSER has two boxes 3 [65], text 2, 3 [67]. p.24 "24 bits"
    for $00 vs. Figure 14 three bytes after the 7-bit count, and 20-bit spacing at Box 28-29 [24, 76, 84].
27. ZINFLD holds characters on an alphabetic DD [102], fields elsewhere [115]. Figure 14 shows a zero count field for
    a symbol that p.24 treats as a three-byte $00, and GETFLD box 25-27's "prefix and length" is the only other length
    source; who writes the count for `$` is UNSPECIFIED.
