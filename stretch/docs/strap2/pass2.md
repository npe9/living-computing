# STRAP II after Pass 1, and the common section: a specification from C22-6729

Source: `docs/C22-6729_7030_STRAP_II_Sys_Analysis_Guide.pdf`, read as page
images in the ink, 2026-11-08. `(p.N)` is its printed page; on every page cited
the printed folio equals the PDF page. `C28 p.N` is
`docs/C28-6129_STRAP-II_with_update_Apr63.pdf` printed page (PDF page = printed
+ 4), a user manual dated earlier than the guide's listing specimen; it is used
only where the guide is silent, and is always labelled. `MCP p.48` is C22-6678-1
printed p.48.

Conventions of this file:

- **UNSPECIFIED** means no page read says it. It is not filled in here.
- **INFERENCE** marks my reading, kept separate from what IBM printed.
- Chart boxes are written `FB/14J` (chart letters, box). A flow chart's arrowhead
  is the `X` beside the target box; connector directions were read that way.
- Unit and symbol fields use IBM's `Zi...`/`Zst...` names. Their bit layouts belong
  to the formats section; Fig. 20 (p.189) is quoted here only where needed.

Reach: see section 13 for the pages not read.

---

## 1. Phases and order

STRAP II is two passes, the second in two parts (p.12). The whole order is
(p.28 chart FA; p.32; p.35):

    Pass 1 -> between-passes procedure -> UITER (first) -> Pass 2a
           -> UITER (second) -> Pass 2b -> end-of-assembly procedure

Between-passes after Pass 1 (p.26 box 62): MCP brings in all of Pass 2 from disk;
`Fpass1` off, `Fpass2` on; pass indication written on the console numeric display
lights; enter `UITER`. Pass 1's last action is to enter the symbol `$00` in the
symbol table (p.26 boxes 57-61).

Phase indicators (p.173):

| Indicator | On during |
|---|---|
| `Fpass1` | Pass 1 |
| `Fuiter` | both UITERs |
| `Fpass2` | UITER 1, Pass 2a, Pass 2b |
| `Fpass3` | UITER 2, Pass 2b |

`Np2ind` is the Pass 2a indicator: zero in Pass 1 and UITER 1 (p.135), set at the
start of Pass 2a (p.33 boxes 3,4), still on inside UITER 2, and turned off as
UITER 2 returns to Pass 2b, when `Fpass3` is turned on (p.35 box 24). In Pass 2b
`Np2ind` = 0 (p.147 NMCP box 1).

Counters (p.173): `Unit` is set to one at the start of each pass and stepped per
unit, in 2a and 2b after the use of `INTIN`. `Field` is zeroed per unit and stepped
per address field. `Symbol` holds, in UITER, the address of the function portion of
the vle of the entry being analyzed; in 2a and 2b the same for the entry of the
current unit, otherwise zero; in Pass 1 always the value `Msyte`. Formats in ERR:
`Unit` (BU, 20), `Field` (BU, 4), `Symbol` (BU, 24) (p.38).

Index registers in Pass 2 (p.175):

| $ | Pass 2 use |
|---|---|
| 0 | value: calling-sequence reads in TABMAN; refill: during RNX |
| 2 | RNX |
| 3 | address of the unit being processed |
| 4 | absolute portion of the location counter |
| 5 | address of the question bits of the instruction |
| 6 | symbolic portion of the location counter (current 3-character special symbol) |
| 7,8,9 | used randomly |
| 10,11 | VALUE |
| 12,14 | NAMEIN |
| 13 | OUTPUT |
| 15 | value: subroutine linkage; refill: table of exits for maskable interrupts |
| 1 | no use printed |

Subroutines are called by three linkages: `LVI, 15, $+2; B, X` with parameters
following; `SIC, Xz; B, X`; and for I-O a `CNOP`, then `SIC`, `B`, `CW` (pp.47, 140,
163). Symbol naming initials: Appendix D (p.202).

---

## 2. Symbol table structures used by these phases

Dictionary entry (Fig. 21, p.190): delete bit, vle-exists bit, then for a symbol:
first 8 characters of the name (64 bits), then a 25-bit signed address of its vle.

Special symbols (Fig. 21, p.190; p.205): dictionary entry = delete, vle bit,
eight 1 bits, `n`, zero fill to 64, then the vle address. "n = 0 for the $ itself."
The symbol is 24 bits: eight 1 bits and sixteen "determined at the time the symbol
is made"; `11111111 00000000 00000000` is the programmer's `$` (p.205). (p.13 says
"three A8 character, the first ... all ones", the same 24 bits.) How `n` is chosen
for each new symbol: **UNSPECIFIED**.

Vle kinds (Fig. 22, p.191; p.190), all: delete bit, 13-bit total length, 6-bit A6 ID:

| ID | Entry | Then |
|---|---|---|
| `S` | remainder of a symbol | 12-bit length of rest of name; rest of name (8n); function (231 bits minimum) |
| `Y` | special symbol | 12 bits of zero; function (231 minimum) |
| `T` | tail remainder | 12; rest of tail; 8-bit tail number |
| `D` | evaluated dimension | 5 bits; evaluation indicator = 1; products n1, n1xn2, ... (Fig. 27 p.194: 24 bits each) |
| `H` | hi-lo | 25-bit signed absolute counter value; 25-bit signed symbolic counter value (no dictionary portion, p.13) |

The delete mark, length, ID, length of rest of argument and rest of argument
precede the function field (p.135 box 8). A vle's ID lets `ANEXT` scan by kind
(p.51). Every dictionary entry has a vle, because each named unit must be matched
to one in Pass 2 (p.13, p.127).

**The function layout is not given.** Fig. 22 says "Format of function defined by
the ZST...bits" and p.202 calls ZST... the relative locations in the function, but
no page read tabulates their positions. Named bits and their printed meanings:

| Name | Meaning | Page |
|---|---|---|
| `Zst0` | everything (value, dds, dimension) defined and computed | 135, 137 |
| `Zst1` | symbol undefined | 170 |
| `Zst3` | existence of dds reference decided | 135 |
| `Zst4` | circularly defined | 170 |
| `Zst10` | mode known | 137 |
| `Zst11` | field length established | 137 |
| `Zst12` | symbolic field length exists | 137 |
| `Zst14` | byte size established | 137 |
| `Zst15` | symbolic byte size exists | 137 |
| `Zst17` | "processing bit for mode"; on = circular value | 135 |
| `Zst22` | multiply defined, no contradictions | 170 |
| `Zst23` | multiply defined with contradictions | 170 |
| `Zst24` | symbol has been used | 140, 170 |
| `Zst26` | real value computed and entered | 137 |
| `Zst32` | use dds reference address (implicit dds only) | 135 |
| `Zst35` | location-counter dependence decided | 185 |
| `Zst36` | 0 = location-counter dependent; 1 = not | 185 |
| `Zst37` | marked to be punched by PUNSYM (chart: "TURN ON ZST37") | 168 |
| `Zstcnt` | number linking the name to the name file: the check digit's copy | 173 |
| `Zstcom` | relocate as lower (0) or upper (1) address | 185 |
| `Zstcon` | 0 blank common, otherwise named-common number | 185 |

Also in the function: value, the absolute and symbolic counters (p.13, p.36), dds
reference address, dimension reference address (p.203), symbol error flags (p.36).
Pass 1 moves into it the length of binary output, coded expressions for a P-mode
dds, explicit dds of a DD, coded expression for a DR dimension (p.25). Dimension
reference address "refers to the count position of the dimension information usually
... further out in the vle" (p.203, p.127). Primitive-to-evaluated conversion of a
dimension: Fig. 27, p.194, done by VALUE.

---

## 3. The between-phases area: UITER

Entered with `B, UITER`; runs twice (p.135). Iterates over the symbol table to
establish a dds and value for each symbol, and computes memory bounds (p.135).
Control: `ANEXT` over the vle table (box 7, p.135).

`Utab`: pushdown table of 64-bit entries; bits 0-23 the location in the symbol table
of the problem symbol, bits 32-56 the level in the symbolic chain. An entry is made
each time `VALUE` returns through `Vbreak` while UITER is processing a SYN chain
(p.135). "A non-P mode symbol initiates a new level" (p.32). Any incomplete symbol
still needed to evaluate the original is kept on this list and evaluated in turn
(p.32).

| Sym | Field | Contents (p.135) |
|---|---|---|
| U3 ($3) | value | location of the base symbol of the chain |
| U4 ($4) | value | location of latest `Utab` entry |
| U4 ($4) | count | current level of evaluation |
| U9 ($5) | value | location of the symbol currently being evaluated |

The `Utab` push/pop itself, and how the base of the chain is resumed after the deeper
symbol is finished, are drawn only as boxes 11, 23, 33, 35: **UNSPECIFIED** in detail.
UITER updates the `Symbol` counter as it goes (p.32).

### 3.1 Flow, as drawn (chart GB, p.136, read at 200 dpi; text pp.135, 137)

```
1 UITER; 2 initialize; 3 ERRIN
   if UITER 1 -> 7 (Np2ind = 0, p.135)
   if UITER 2 -> 4 UHL
4 UHL  ANEXT for hi-lo (H) entries: no more -> 7; more -> 5 establish hi-lo values -> 4
7 UGOA ANEXT next symbol table entry: no more -> 15 exit
8 space to function
9 branch-on-bit-and-set-to-one Zst0: was on -> 7; was off -> 16
16 Zst3 (dds reference decided)? no -> 23 UDDS; yes -> 17
23 UDDS  if Zst17 on (circular) give dds reference address of zero; else VALUE -> 31
31 Zst3? yes -> UVAL(10); no -> MACHER(6)
17 Zst32 (use dds reference)? yes -> UVAL(10); no -> 24
24 Zst10 (mode known)? no -> MACHER(6); yes -> 25
25 Zst11 (f.l. established)? yes -> 18; no -> 32

   -- field length established --
18 Zst12 (symbolic f.l.)? no -> LBS1(27); yes -> 19
19 VSKIP over the f.l. coded expression -> LBS1(27)

   -- field length not established --
32 Zst12? no -> LBS1(27); yes -> 33
33 UEVALA get value of the symbolic entry -> 34
34 Zst26? yes -> 20 entered at top; no -> 26
26 branch-on-bit-and-set-to-one Zst0: was on -> LBS1(27); was off -> 20
20 Kamms: add and compare results
      exit "F.L. established"     -> 18
      exit "F.L. not established" -> LBS1(27)

   -- byte size --
27 LBS1 Zst14 (b.s. established)? yes -> 21; no -> 28
21 skip the b.s. coded expression if a symbolic b.s. exists, VSKIP -> 30
28 Zst15 (symbolic b.s.)? no -> 30; yes -> 35
35 UEVALA get value of the symbolic entry -> 36
36 Zst26? yes -> 29; no -> 30
29 Kamms: add and compare results
      exit "B.S. established"     -> 21
      exit "B.S. not established" -> 30

30 UVALC restore original entry to location in U3 -> 22
22 branch-on-bit-and-set-to-one Zst0: was on -> UVAL(10); was off -> 14
14 Np2ind zero? yes -> UVAL(10); no -> MACHER(6)

   -- value --
10 UVAL Zst26 (real value computed and entered)? yes -> 7; no -> 11
11 if circular value, assign zero; else VALUE to establish a value.
   A DR whose dimension product is unformed: VDIMEN; if not formed, turn off Zst0
12 Zst26? yes -> 7; no -> 13
13 Np2ind zero? yes -> 7; no -> MACHER(6)

6  MACHER (error routine; marks the vle as completed, p.173) -> 7
   (arm zoomed at 300 dpi: it joins the vertical line to box 7, not box 11)
```

So a symbol unresolved in UITER 1 simply waits; one still unresolved in UITER 2
goes to `MACHER` (p.137 box 13: "The value should be established by the end of
Pass 2a; if it is not, branch to MACHER").

Not settled by the text: box 26 is printed under the heading "Box 27" on p.137.
Its NO arm goes into Kamms as drawn, so Kamms runs although not everything is
defined. Taken as drawn.

### 3.2 Kamms

"Kamms procedure in DECODE" is called only from boxes 20 and 29 (pp.136-137):

- Field length: must be not more than 64 bits and not in bit style.
- Byte size: not more than 8 bits and not in bit style.
- Illegal: error message and truncation. "Bit and integer values are combined."

Which message (numbers 87, 88, 89, 97 by name, p.177-178), the truncation mask, and
what "combined" adds in what units: **UNSPECIFIED**. No other page describes Kamms.

### 3.3 Hi-lo and memory bounds (UITER 2)

`Uhl` inspects each hi-lo vle (p.35 box 24; p.137 boxes 4,5). Hi-lo entries are made
by Pass 2a (section 4.3). The reduction rule is **UNSPECIFIED** in the guide. C28
p.20: lower bound = address of the full word immediately before the first word
used; upper = the full word immediately following the last word used.

### 3.4 Error symbols (p.32-33, p.206)

- After Pass 1, UITER turns on the indicator (`Vcundf`: INFERENCE, p.32 does not
  name it, p.57 defines that bit) that tells VALUE it may make
  an undefined-type entry during each UITER or Pass 2 evaluation of a symbol VALUE
  can not find (pp.32-33, p.57). During Pass 1 not finding one was allowed.
- Only UITER can detect the undefined symbols in a SYN chain; during the first scan
  it marks them (p.32).
- UITER sets the circular and contagious flags in an entry as it completes it in
  the first scan, and assigns zero to the **base symbol** of a circularly defined
  chain (p.32). Example printed in C28 p.21: `A SYN,B; B SYN,A+5` gives A=0, B=5.
- Whenever VALUE evaluates a symbol it marks it as referenced from an address field
  (p.33). This is the "used" condition for NUNDSY.
- Multiply defined symbols were found in `ADDORD` and marked in `MULTI` in Pass 1
  (p.33, p.127). Legal: `MULTI` repoints the dictionary to a new vle holding the
  accumulated data; a later definition can't overrule an existing dds, dimension or
  index (p.127). Contradictory: dictionary unchanged, so the first definition is
  used in all references (p.127). Either way a basic vle exists for each name (p.127).
- Of the five irregular kinds only the two multiply-defined kinds are mutually
  exclusive (p.33). Kinds: undefined, multiple without contradiction, multiple with
  contradictions, circular, contagious (pp.205-206).

Undefined symbols: dds (N), location = next available full word above the upper
limit (p.205, "pseudo-defined symbol"). C28 p.20: sequential full-word locations in
order encountered. Where this assignment happens: **UNSPECIFIED** (see Gap 3).

Serviceability: `Symbol` carries the entry; UITER errors go in the symbol-keyed ERR
format (section 9.2).

---

## 4. Pass 2 main flow (NPS2), charts FA-FD pp.28-31, text pp.32-36

Pass 2a assigns location counter values and attempts to assemble; Pass 2b finishes
values, checks the counters, and produces documents (pp.13, 204). Each unit passes
through singly; the name file is not touched before 2b (p.13).

### 4.1 Skeleton, common to 2a and 2b

```
NPS2 (3) Pass 2a initialization                [UITER 1 returned; decision 2 = yes]
NPS3 (4) Pass 2b initialization                [UITER 2 returned; decision 2 = no]
NGUNTB (5A) INTIN: fetch unit
(5B) EOF? yes -> (23) Pass 2a? yes -> (24) UITER -> NPS3 (4)
                                no  -> NPS2B (31) end of assembly
(6)  per-unit initialization
(7)  Pass 2a? no -> (8) first unit of 2b? yes -> (25) NMCPA1 -> joins
(9)  MCP unit? yes -> (26) NMCP; no -> (10) set no-punch-further-MCP switch
NA (11) second of two EXT units? yes -> (13)
(12A) rounding necessary? yes -> (12B) round
(12C) CNOP? yes -> (12D) still needs adjusting? no -> FC 31; yes -> (12E) make NOP
(13) save location counter setting in the vle of the $ entry
(14A) coded expressions to decode? yes -> (14B) DECODE [VALUE, INSERT] -> (14C)
      no -> (15)
(14C) produces binary output? yes -> (14E); no -> (14D) DR? yes -> (14E); no -> (15)
(14E) Pass 2a? yes -> (14F) store counters; no -> (27) check counters
(14G) second of the 2 EXT units? yes -> (14L) NEXT2 -> FC 31
(14H) DD or DR? no -> (14K); yes -> (14I) absolute total length computed?
      yes -> (14K); no -> (14J)
(14K) update location counter by absolute length of binary output -> FC 31
(14J) new relative symbolic counter, zero absolute counter -> FC 31
(15) Pass 2a? yes -> (16) SYN? no -> (17) store counters. All arms -> NUPOT
NUPOT (18A) pseudo-op specified in an EXT statement? yes -> (18B) NEXT2 extract zeros -> NGUNT
(19A) pseudo-op? yes -> (19B) NPOC digit-select branch table; no -> NP08
NP08 (20) Pass 2a? no -> (28) check counters
NGUNT (21) OR the special set of error flags into the unit
(22) Pass 2a? no -> (30) OUTPUT.  All arms -> INTIN
```

Unnumbered returns: routines of 19B come back to (19C): Pass 2a -> NGUNT; else -> NP08.

`INTIN` is entered once more after the END unit so its EOF recycles the units for 2b
(p.33). The re-entry location is set at NPS2 (p.33).

### 4.2 Per-unit initialization, boxes 5A-6 (p.33)

Zero `Field`; step `Unit`, update `Symbol`; `$3` := location of the new unit; `$5` :=
location of the new instruction's op index; zero the five error flags for an
erroneous symbol; if the unit has a name, compute and save the location of the
function portion of its vle. Field counter is stepped in Pass 2 by the routines that
process address fields, generally DECODE.

### 4.3 NPS2 initialization (boxes 3,4, p.33)

- `Np2ind` on. Save the location of the `$` symbol table entry.
- Initialize the unit-fetching and error routines. Unit counter and `$4`, `$6` := 0.
- Absolute counter := 41 (octal), or 0 in PUNREL mode. Enter it in hi-lo as first
  entry. An SLC as first unit overrules this low entry.
- Units of 41 octal: the listing shows `000041.00`, i.e. word 41 octal (MCP p.48).

NPS3's content: **UNSPECIFIED** except by implication (`Np2ind` off, `Fpass3` on).
Whether it resets the counters, and how 2b reconstructs the location, is in Gap 2.

### 4.4 The two location counters (pp.13, 19, 33-34, 203)

```
location = (value of the special symbol in $6, if any) + $4
```

- `$4` absolute portion. `$6` location of the vle of the current special symbol; zero
  if no symbolic portion (p.33 boxes 12A,12B, p.34).
- Reason: while the length of binary output or the required rounding is unknown, the
  value of an unevaluated programmer symbol would be needed (p.13).

**New symbolic counter** (14J, also 12B and NEXT): enter a new special symbol,
ADDUNO, unordered: it is always the currently last symbol (p.13). Its function
holds a SYN-like coded expression giving the sum of the current symbolic counter and
the absolute counter (p.13, p.34). `$6` := location of its vle; `$4` := 0 (p.34).
"Thus a cascading of STRAP II special symbols" (p.34). UITER 2 evaluates them along
with all symbols (p.19, p.35).

**When it happens**:
- DD/DR whose total length is not yet established (14I-14J, p.34). The final length
  of a DD or DR is kept in `Ziotpt`, not `Zilbo` (p.34). For a DR the sign of the
  `Ziotpt` value field shows the dimension has been computed (p.32).
- Rounding when the symbol in `$6` is not at the required type of location (12B, below).
- EXT when the N parameter is unavailable (section 7).

**Rounding, 12A-12B (p.33)**: previous processing added only the length, so rounding
is tested at the beginning of each unit in 2a. A DD or a DR in non-floating-point
mode: none. Otherwise the op question bits say full or half word.
- `$6` = 0: round `$4` at once.
- `$6` <> 0 and the present symbolic counter symbol is at the required type: round
  `$4` only.
- Otherwise: enter a new symbolic counter symbol marked with the appropriate full or
  half word indicator; `$4` := 0; `$6` := its location.

Where that full/half indicator lives: **UNSPECIFIED** (Figs. 21-22 show none).

A DR in floating mode rounds to a full word (p.33; C28 p.18). Message 53 "VALUE
ROUNDED TO FULL WORD" is OUTPUT's (p.177).

**CNOP, 12C-12E (pp.33-34)**: further adjustment may be needed; the CNOP is then
processed effectively as a NOP unit.

**Box 13**: current `$4`, `$6` go in the function of the `$` entry (p.34), so `$` in an
expression evaluates to the unit's location.

**Storing counters, 14F, 17 (p.34, p.13)**: after DECODE, and for pseudo-ops other than
SYN, the counters are put into the unit (`Ziadab`, `Ziadsy`, p.189) and into the
vle of any companion symbol table entry. Hi-lo candidates are entered by VALUE-independent
Pass 2a actions: the initial value, SLC, END (pp.33, 35). "the location counter values
that are candidates for hi-lo values" get symbol table entries in 2a (p.33); which
units besides those: **UNSPECIFIED**.

**Advance, 14K**: if the unit yields binary output or is a DR and the absolute length
is known, add it to `$4` (p.34). Then OR the symbolic error flags in and repeat.

### 4.5 Pass 2a pseudo-op treatment (19B, chart FD, pp.34-35)

| Op | Branch | Pass 2a action |
|---|---|---|
| PRNID | NPRNID | give the unit to OUTPUT in 2a as well as 2b; flags ORed first. These are the only material printed in 2a: all PRNIDs precede the listing and each also appears in place in 2b |
| SYN | NSYN | if the value is complete, as box 21; if not, try once more with a section of UITER |
| SLC, SLCR | NSLC | adjust both counters. SLC: hi-lo entry, SLCR indicator off, hi-lo-can-be-made on. SLCR: no entry, indicator on, can-be-made off |
| END | NEND | enter its location in hi-lo |
| EXT | NEXT | parameters' expressions evaluated and saved; counter += length by N; rounding of the next EXT unit not performed; multiple-field DD statement adds extra |
| PUNSYM | NPNSYM | mark each named vle for punching (chart EB p.168: SEARCH each symbol; not found -> UNDEF entry, message 124 `SYM ON PUNSYM NOT IN PROG.` (p.178); turn on Zst37) |
| SEM | NBSEM | update the major error mask in the error routine from the current unit's mask |
| REM | NBREM | same |
| SPNUS | NSPRES | turn on an indicator for NUNDSY |

Wind-up only (box 20, p.34; p.31): PUNID, PUNFUL, PUNNOR, PUNORG, PRNS, PRND, SKIP,
NOPUN, TLB, DDI, NOPRNT, TAIL, UNTAIL, PRNOR, PUNALL, PRNTALL, DUPLI, NOSEQ, RESEQ.
Not pseudo-ops in box 21 (p.34): the five flags ORed at once and cycle repeated; MCP
ops, DD and DR follow the same action.

Box 9, 10, 26 (p.33): MCP units are processed in 2b; in 2a the first op not MCP
(comments excepted) sets a switch preventing later non-contiguous MCP ops being
punched, although they are listed. Box 11 (p.33): for EXT only the first of two units
adjusts the counter. Boxes 18A,18B (p.34): extracting from a pseudo-op supplies zeros
and an error message (122, NEXT, p.178).

`LINK` is not on chart FD's branch list (pp.31); it has a do-nothing entry in OT (p.153).
Pass 1 has made it an `LVI, 15, $+2` unit with `Zifbo`, `Zifall`, `Zifp2` on (p.32), so it
travels the ordinary instruction path. **INFERENCE**.

### 4.6 UITER 2 (box 24, p.35)

Reached by INTIN's EOF exit at the end of 2a. Concludes dds and values, Uhl memory
bounds, returns to NPS3 with `Np2ind` off and `Fpass3` on. "At this time all the names
of the assembly are evaluated" (p.35). Error list initialized (section 9).

### 4.7 Pass 2b (pp.35-36)

- First cycle only (boxes 7, 8, 25): GO and LIM cards by `NMCPA1`, the only output not
  punched by OUTPUT. GO and LIM do not appear on the listing, nor do SKIP and NOPRNT.
  GO and LIM precede each binary deck (p.35).
- Floating format of all numeric DDs is adjusted, general parenthetical field entries
  on DDs are treated, EXTract binary is extracted, documents are produced (p.35).
- **Boxes 14E, 27, 20, 28**: location previously stored in the unit and symbol entry is
  checked against the present setting. For a non-binary unit the check is later (box
  28). On a discrepancy an error is given and **the Pass 2a setting is used** (p.36).
  Message 6, NPS2, "PASS 2A AND 2B LOC. CTR. DO NOT AGREE" (p.176).
- Message 100, NPS2, "ADDR LESS THAN 33." (p.178). Its test: **UNSPECIFIED**.
- Final combination: "Pass 2b will then combine the absolute and evaluated symbolic
  value, if any, so that each actual location counter value can be put into the
  absolute field of each unit for the output program" (p.19). `Ziadab` is the source of
  the location OUTPUT prints (p.13).

Pseudo-ops needing nothing further in 2b, box 19 (p.36): PRNID, PUNID, PUNFUL, PUNNOR,
PUNORG, PRNS, PRND, SKIP, NOPUN, TLB, DDI, DD, DR, DRZ, NOPRNT, PUNSYM, TAIL, UNTAIL,
PRNOR, PUNALL, SPUNS [sic], PRNTALL, DUPLI, NOSEQ, RESEQ. Those treated (p.36):

| Op | Pass 2b action |
|---|---|
| SLC, SLCR | adjust the counter; the absolute value is now available. OUTPUT stops punching on an SLCR until the next SLC |
| END | check symbolic and absolute counters; set INTIN's end-of-file location |
| EXT | as 2a; length of binary now established and saved; box 28 |
| SYN | bit and integer values taken from the symbol's absolute and symbolic counter fields and put in the unit's absolute and symbolic counter fields; five error flags ORed into the unit; dimension reference address moved to the unit |
| SEM, REM | as 2a. Mask update occurs in every pass since a message condition can arise in any |

### 4.8 End of assembly (boxes 5B, 23, 31; pp.36, 150)

Print the total time and total number of units used. Print `THE END` on a page by
itself and, with an additional SKIP, display it to the operator. Update COMREC with
where the documents are. Return COMREC to MCP and give MCP control. Chart OQ p.150
ends with OEDIT time message then `$EOJ`. COMREC: word 9 data goes to word 8, bits 00-18
the relative arc of the last listing arc (p.11).

---

## 5. DECODE, chart DC p.139, text p.140

Purpose: resolves coded expressions (p.138). Entered from 2a and 2b if `Zifp2` is one
(p.140). Call `SIC, Decodz; B, DECODE`. Sets `Zifall` to one on entry; zero on exit if
binary output could not be completely assembled (p.140).

```
1 finished? (test Zifall) yes -> exit        [see Gap 12]
2 Zoddsa of op question bits: dds needed? no -> KE(9)
3 explicit? (Zifdds)  no -> KB(5)  yes -> 4
4 by P-mode? (Zifpm)  no -> KE(9)  yes -> 6
5 KB construct the convention dds (below) -> KAB(7)
6 SEARCH the P-mode symbol; turn on its Zst24 -> KAB(7)
7 KAB established? no -> Zifall off, exit
8 put in the dds field of the unit -> KE
9 KE Zopo: pseudo-op? yes -> KF(16); no -> KEBA(10)
10 KEBA VALUE an address field (uses Valinx)
11 value available? yes -> KEE(13) INSERT; no -> 12
12 another field? yes -> 10; no -> 14
14 GP? no -> exit. yes -> KEF(15) evaluate and insert GP, if unable Zifall off; exit
16 KF DDI? -> KDDI(17) evaluate via part of OUTPUT, OR into unit, change to SYN; exit
18 DD? -> KFNA(19) length = field length x number of fields, store in unit; exit
20 DR? -> KFA4(21) VDIMEN; dimension x field length, store in unit; exit
22 EXT? -> KXAB(23) VALUE parameters; if available store for extract section; exit
   otherwise -> 10 "normal insertion of address field" (text Boxes 22,23)
```

Convention dds, Box 5 (p.140): when a dds is needed and none given:
1. ambiguous op: (BU, 64, 8)
2. clearly VFL: (BU, 64, 8)
3. clearly VFL with immediate: (BU, 24, 8)
4. floating only: normalized, except E and E+I which are unnormalized (U, p.205).

Message 42 "STRAP ASSIGNED DDS" is MAIN's (p.176), 92 "NO MODE" DECODE's (p.177).
Others by DECODE (pp.177-178): 87 FL>64, 88 BS>8, 89 BIT TYPE NOT ALLOW, 90 NEG. FIELD
COMPLEMENTED, 91 MODE INCONSISTENT WITH OP, 93 TOO MANY FIELDS, 94 ERROR IN GP, 95 NEG.
GP COMPLEMENTED, 97 BIT TYPE UNUSUAL, 98 NEG. PARAMETERS ON EXT, 99 PARAMETER>64, 130 FL
>24, 132 CANNOT EVALUATE DDI.

Each VALUE's error indicators are ORed into the intermediate error-symbol mask; later
that mask is ORed in the unit so that when printed the instruction is preceded by the
error-symbol message (p.34). When a coded expression cannot be evaluated, 2a still scans
the whole expression, by a special re-entry to the evaluator, so all undefined symbols in
it get entered (p.19). SYN and MCP ops are not decoded here (p.34). Every binary-producing
unit (incl. DR, DRZ, EXT, LINK, DD, DDI) goes to DECODE in 2a (p.34).

DDI (p.34): processed as a DD in Pass 1; in Pass 2 DECODE evaluates it using OUTPUT's
facilities, then adjusts the unit so Pass 2 treats it as a SYN.

---

## 6. INSERT (p.144), relocation (p.185)

Call `SIC, Sgez; B, <address>`, where the address is from the current fill index word.
For each type of instruction `MAIN` puts in the unit the location of a chained set of fill
index words (p.144). Each fill XW (p.144):

- value: address of the INSERT subroutine to put a value in a particular field of the
  skeleton
- count: number of coded expressions given to it (one almost always; INDMK and LVS
  are exceptions)
- refill: location of the XW for the next field

Examples: VFL op: `XW, S24A, 1, $+1; XW, SOFF, 1, 0`. LVS: `XW, SJFLD, 1, $+1; XW, SBIT,
16, 0`. (p.144)

The rules (p.144):

- Absolute values from `Sinb`, `Sini`, `Sinx`.
- Algebraic add of bit and integer according to the **function** of the address, not
  field size. SAM+10 as 18-bit: 10 full words. As 19-bit: 10 half words. As 24-bit: 10
  bits. In `TI, 7, SAM+10, PAT+10` both function as 18-bit addresses: 10 full words.
- Two's complement replaces a negative result for an unsigned field.
- Bits truncated where necessary and messages executed.
- Immediate addresses: filled per the given field length unless it contains a bit
  address or the given length exceeds 24, then a 24-bit address.

The list (p.144):

| Routine | Fills |
|---|---|
| S18A | 18-bit address and I field |
| S18NI | 18-bit address, no index allowed |
| S19NI | 19-bit address, no index allowed |
| S19KF | 19-bit address, K field |
| S19IA | 19-bit address and I field |
| S1918A | 19-bit address and I field, error-flagged if 19th bit not zero |
| S24A | 24-bit address and I field |
| STTI | 24-bit address and I, error-flagged if more than 18 bits specified |
| SSIC24 | 24-bit address and I, error-flagged if more than 19 bits specified |
| S24SNI | 24-bit signed field with index if any |
| S24CW | 24-bit signed field, error-flagged if more than 18 bits specified |
| SFLGS | flag bits 25-27 |
| S19BBK | 19-bit branch address and K field |
| STT19A | 19-bit transmit address and I, error-flagged if more than 18 bits |
| S18CF | 18-bit count field |
| S18RF | 18-bit refill field |
| SOFF | offset and I field |
| SCHAN | 7-bit channel address and I field |
| SXP10 | signed exponent field or normal fraction shift |
| SBIT | index indicator bits for LVS |
| SJFLD | J field |
| STJFLD | J field for transmit and swap |
| SIMAD | immediate addresses |
| SINDMK | indicator mask |

Bit positions of these fields, and which op has which chain: **UNSPECIFIED** (Gap 5).
Messages by INSERT (p.178): 114 negative field complemented, 115 index not allowed, 116
truncated, 117 only K field, 118 bits not normal in op, 119 SLC has an integer, 120 bit
type addr unusual, 121 bit addressed twice in LVS or INDMK, 123 more than 1 loc. ctr. dep.
symbol.

Relocation (p.185): with bit `Zst35`, `Zst36`; after inserting binary in `Ziotpt`, INSERT checks
`Sinrl1`, `Sinrl2`, `Sinua`. If `Sinrl1`=1, `Sinrl2`=0, `Sinua`=1, it inserts in `Zicomm`
the common number in `Sincom`. `Zicomm` (Fig. 17, p.184) is the last word of the fixed format.
PUNREL handling, relocation pseudo-ops, cards: pp.183-188.

---

## 7. NEXT, chart RC p.145, text p.146 (Pass 2's EXT)

Entered from the digit-select table. A two-unit ext: `NEXT2` handles the second (FB/14L).

```
1 modify Pass 2: skip rounding the location counter, branch to special updating,
  and stop the extract of a pseudo-op
2 come from DECODE?  (Zifp2 is always on in Pass 2)
    no  -> 3 store N value in Zilbo for updating -> return to Pass 2
    yes -> NEXTB 4 branch by parameter form
```

| Form | Bits | Test | Then |
|---|---|---|---|
| `(,,)`, `(,LP)`, `(L,)`, `(L,LP)` | 000, 010, 100, 110 | NEXTF 7: `Zifall` on, values for all? | yes -> 5. no -> 8 symbolic counter, return |
| `(,,N)`, `(L,,N)` | 001, 101 | NEXTE 9 | yes -> 5. no -> 10 |
| `(,LP,N)` | 011 | NEXTD 12 | yes -> 5. no -> 10 |
| `(L,LP,N)` | 111 | 13 | yes -> 14 test consistency, error (133) -> 5. no -> 10 |

- 5: store parameters for OUTPUT: N inserted in the unit; return.
- 8: set up symbolic counter when N not specified and others cannot be evaluated.
- 10: value for N? yes -> 5. no -> 11 set up symbolic counter: N can't be evaluated; return.

Actual extraction happens in OUTPUT (chart OP boxes 3,4: "construct requested extract", and
p.35). Semantics of L, LP, N: **UNSPECIFIED** on these pages; the constructing algorithm too.

---

## 8. Table management, the common section (TABMAN pp.43-53)

Tables: symbols (`Tsymb`, p.169), 7030 indicators (MIBA), tails. Control block per table
(Fig. 8, pp.44-45):

| Field | Symbol | Rel. loc. | Bits | Contents |
|---|---|---|---|---|
| FX | `Azfx` | 0.0 | 64 | index word referring to function part of an entry |
| DX | `Azdx` | 1.0 | 64 | index word referring to dictionary location |
| FW | `Azfw` | 2.0 | 24 | first entry, halfword address |
| ID | `Azid` | 2.25 | 6 | identification |
| LW | `Azlw` | 2.32 | 24 | last entry, halfword address |
| TO | `Azto` | 2.57 | 1 | 0 ordered, 1 unordered |
| TM | `Aztm` | 2.58 | 1 | delete mark |
| TEC | `Aztec` | 2.62 | 1 | type of compare |
| EL | `Azel` | 3.0 | 16 | entry length (filled by subroutine) |
| AL | `Azal` | 3.16 | 16 | argument length |
| ADDL | `Azaddl` | 3.32 | 16 | function length |
| N | `Azn` | 3.48 | 16 | undeleted entries |

Universal control block (p.45): `Auvtab` next bit of vle table (built upwards), `Auvbot` lowest
usable bit, `Autcb` first control block, `Aunt` number of blocks. If a vle exists its address
is in the last 25 bits of the function (p.44). The vle table is one consolidated block (p.44).
Three entry forms, p.44. Meanings of TEC values, and TM's use: **UNSPECIFIED**.

Common entry (boxes 1-3, p.45): save $0-$7; zero `Azzc`, `Azzb`; read control-block location into
$5 value. Exit (p.46 box 31): restore $0-$7, `B, -1($15)`. A 19-bit -1 is one halfword (p.144).

**SEARCH** (p.47): `LVI,15,$+2; B,SEARCH; ,tbl; ,arg(I); ,al(I); B,fixup ['not found]; normal`.
Compare setup `Acompi` sets field length to the argument (box 4). Under seven items, or
unordered: linear; ordered and seven or more: binary (p.45 box 7, p.47). A deleted match is a
miss (chart box 11). Found (box 14): $15 + 2.32 (the exit's -0.32 lands on the normal return).
Location of equal entry placed in control block; if a vle exists, `Agetv` computes function
address; function address placed in control block (boxes 18-26, p.46). Not found, not ADDORD
(box 12): $15 + 2.0, lands on not-found; index words then give next-higher entry (ordered) or
next location after the table (unordered) (p.47).

**ADDORD** (p.48): `tbl, arg(I), al(I), funct(I), fl(I); B,fixup ['already there]; B,fixup
['error: unordered, item not in order]; normal`. Restrictions: table ascending; overflow is the
programmer's care. Unordered table: added out of order, error exit via ADDUNO. Else SEARCH;
found: already-there exit with index words at the item (box 32,33: + 0.32 extra). Not found:
table moved up, entry inserted, control block updated. Box 9 adds 3.32 (see Gap 11). Pass 1's
`MULTI` hooks here (p.127).

**ADDUNO** (p.49): `tbl, arg(I), al(I), funct(I), fl(I); normal`. Box 10 adds 3.0. No space check.
Last entry to $6, `Afndma` tests it for delete mark; `$2` := its address if deleted, else next
free location (p.46 boxes 10-24). Mark unordered. If not replacing a deleted item, last word
in control block += entry length (boxes 27,28). Count + 1, entry moved to `$2`, exit `Arest`
(boxes 29-31). Also updates last-vle address in universal block (p.49). p.49 calls the last-entry
field `Azew`.

**ANEXT** (pp.50-51, 53): `LVI,15,$+2; B,ANEXT; ,ID; ,linkage to fixup; , ['two halfwords: no more
vle]; normal`. ID in bits 18-23 of its halfword. Initially bit `Afirst` on; it is turned off by
the test; turn it on to restart. Save $2. `Afirst` on: $2 := first location of vle table. Off:
next from XW `Anexta`. ID differs and more entries: $2 += length just tested, retest. None: "no
more" return. IDs equal, not deleted: location into XW `Anextx`, `Anexta` := next vle, normal
exit. Deleted: as if not found. Message 19 "SYMBOL TABLE IS INCORRECT" (p.176).

**RSERCH** (pp.52-53): "get address of symbol". Save $0-$7; `Azzs` := 1. Save index register I of
the calling sequence. Compare each dictionary entry's function address with the given address:
not equal, more -> by entry length; none -> $15 + 1.32, exit (not found). Found: dictionary
and function locations put in control block. If I specified: dictionary entry moved to location
in I's value, value += length moved. $15 + 2.0. Exit `B,-1($15)`. Its linkage layout:
**UNSPECIFIED** (no page prints it).

**MOVE** (pp.40-42): `LVI,15,$+2; B,MOVE; ,from(I); ,to(I); ,bits(I); normal`. Destroys accumulator
and arithmetic, comparison and result indicators. A=P.Q, B=R.S, N=T.U, A+N=Z=X.Y. N=0 or A=B:
return. Q=S [#2]: save the words at P.0, X.0 in V, W to protect overlap; `L = N-Y-(64-Q)/64`;
L<0: from V at offset Q, N bits to B. L=0: last 64-Q of V to B; if Y<>0 first Y of W to B+N-Y.
L>0: transmit L words forward (P.64 to R.64) or backward; then V, W. #3: progressive load/store of
T words forward from A to B if A<B else backward from A+N to B+N; then U odd bits. Users: OEDIT,
OUTPUT, OPLIST, VALUE, TABMAN (p.41).

### 8.1 VALUE, chart RD p.54, text pp.55-60

Entries (p.55):

| Entry | Call | Effect |
|---|---|---|
| `VSKIP` | `LVI,15,$+2; B,VSKIP` | `Valinx` advanced past expression; undefined entries made if `Vcundf` |
| `VDIMEN` | `...; B,fixup [@not evaluated]; normal` | $1 locates dimension statement. Evaluated: $1 = location of product of dimensions. Else $1 unchanged. Same `Vcundf` rule. |
| `VMOVE` | `...; B,VMOVE` | `Valinx` from, `Vmovex` to; both advanced. Same `Vcundf` rule. |
| `VALUE` | `...; B,fixup [@break]; normal` | `Valinx` locates. Bits: `Vcbv`, `Vcbsx`, `Vcbdim`, `Vcbdds` = 1 means do not attempt value+index, S/X, dimension, dds |

**Break exit** when a symbol lacks needed data (p.55-56): $1 locates its function; `Vnbv`,
`Vnbsx`, `Vnbdim`, `Vnbdds` what is needed; `Vfbv`, `Vfbsx`, `Vfbdim`, `Vfbdds` what is affected; `Vcb`
bits unchanged. Caller may change `Vcb` bits or fill the symbol table, and may call VALUE on other
expressions, and returns to `Vrtrn` (retries where it ran into trouble if improved; if not,
notes what can no longer be evaluated and proceeds) or `Vpunt` (as if all `Vcb` on then `Vrtrn`)
(p.56-57). Turning a `Vcb` off in a break is ignored (p.57).

**Normal exit** (p.56, Figs. 9 p.58, 18 p.185): `Valinx` past expression; if `Vcundf`, undefined
entries made.

| Name | dds | Contents |
|---|---|---|
| `Sinb` | (B,25) | bit style value |
| `Sini` | (B,25) | integer value |
| `Sinx` | (BU,4) | index |
| `Sinxq` | (BU,1) | index given |
| `Sinrl1`, `Sinrl2` | (BU,1) | relocation |
| `Sinsx` | (BU,2) p.56; (BU,1) Fig. 9 | 00 integer style (S), 10 bit style (X) |
| `Sindim` | (B,25) | dimension reference |
| `Sindds` | (B,25) | dds reference |
| `Sindsq` | (BU,1) | dds reference known (p.56) |
| `Sinm` | (BU,3) | mode bits (Fig. 9) |
| `Sinmq` | (BU,1) | mode given (Fig. 9) |
| `Sinser` | (BU,4) | symbol error flags |
| `Sincom`, `Sinua` | third word | named common; lower/upper (Fig. 18) |

`Vfbnot` on, with appropriate `Vfb` bits, if anything could not be found (p.56).

**Undefined** (p.57): `Vcundf` on: standard entry made and VALUE proceeds as though found, even
if all `Vcb` on. Off: no longer computable items noted, no break.

**Workspace** (p.57, Fig. 10 p.60): push list; five-word heading, workspace, next heading, ...
as many as existence bits encountered. $10 current heading, $11 location in workspace. Heading:
`VVE` (entry point = ($15)vf at entry; flags `VVCDR`, `VVCDRL`, `VVCDRM`, `VCH` storage for Vcb;
`VVBRK` break point, `VVSYMB` last datum symbol), `VVHUP`/`VVHDN` (next heading above / below; `VVPAD`,
`VVINT`, `VVABS`), `VVINX` (input index at external break; `VVSPX`, `VVSUBQ`, `VVTOP`; `VVSYX` location of
symbol entry in error), `VVDDS` (dds reference; `VVXQ`, `VVMQ`, `VVX`; `VVDIM`; `VINRL1`, `VINRL2`, `VVSER`),
fifth word `VVCOM`, `VINUA` (Fig. 19 p.186). Data: I-value and B-value, normalized floating point
words; subscript the same with low bit 1.

**Flow**:

- Box 12: bit `Valdfg` zero (no VDIMEN special entry) -> 13. Box 17: get dimension reference, set
  control bits, VALUE it, form product, set completed bit; else `VBREAK` (p.57).
- Box 13: existence bit (first bit of expression) off -> `MACHER` (p.58).
- Box 8, prefix bits two to four (p.58, chart RD; Appendix C p.197):

| Prefix | Type | Chart action |
|---|---|---|
| 000 | normal | VB |
| 100 | super special (finished by DECODE) | VB, same encoding |
| 001 | special index | special index bit on, space 3 bits, then VB |
| 010 | padded | padding bit on, VB; pad over at end |
| 011 | special signed | VA3: next 25 bits as B value; 23 space padding (p.197: `1011` then 25 bits with sign) |
| 101 | fully evaluated | VA5: next 2 words into list; 22 space index, exit |
| 110 | long, 3 more bits | VA6 box 14: 000 integer; 001 absolute; 010 absolute integer (VA61); 011 VA63, 17-bit constant into list; 23 |
| 111 | null | zero into list |

- VB, Box 3: another datum per no-more-datum bit. Off -> box 4. On: turn off `Vvsymb`, `Vvcdr`,
  `Vvcdrl`, `Vvcdrm`; box 9 (p.58).
- Box 9, datum prefix (p.59; p.197): 100 symbol -> SEARCH (10); 101 sub-expression -> recursive VALUE,
  put value in work area (18); 110 absolute 24 bits, integer value; 111-- long; 11100 system symbol
  (VSS, 24-bit bit-style value, then dds, 13 bits; 24), to connector 40 -> 3. 11101, 11110, 11111 unused.
- Box 10 symbol found: 11 `VBREAK` if needed; 16 requested info established? yes -> 20 put in list.
  Not found: 15 OK to enter? (`Vcundf`) -> 19 ADDORD -> 11; no -> exit from datum.
- Boxes 4,5 (p.58-59): `Vcbv` or `Vtbv` on: value not wanted; `Vcbsx` on: S/X not wanted. Neither wanted ->
  6. Else pick table address; per operator: get section entry and operand type; get datum number; get
  left/right operands; perform. None -> 6.
- Box 6 (p.59): $11 := $10. S/X unknown: `Vtbsx` trouble bit. No values computed: `Vz`. Index if `Vvspx`. If
  off and `Vvabs`: both signs plus. `Vvint` off: exit; else combine and bit value := 0. Skip padding. Results in
  `Sini`, `Sinb`.

Encoding (App. C pp.197-199): prefix; data each ended by a 0 bit, last also 0 for end-of-data;
index after last datum before operators; operators 1 + 3-bit code + 5-bit datum number, ended by 0;
then GP: 1 + 6-bit n + coded expression. 111 `.+`, `a.`; 110 `.L`; 101 `.R`; 100 unary -; 011 *; 010 /;
001 +; 000 -. Operators in order performed. Subscripts follow their symbol as regular expressions. Worked
examples Figs. 28, 29 (pp.200-201) are read by the formats reader. Parentheses are compiled away by
datum numbers (p.198; p.199 note 4). Bit and integer arithmetic of each operator (`.L`, `.R`, mixed): **UNSPECIFIED**.
Scaling for subscripts with dimension products: **UNSPECIFIED** beyond messages 71-77 (p.177).

---

## 9. Errors

### 9.1 Numbering

Message number = rank of its control word in `Errtab`, a table of ordered 64-bit CWs (p.38). On
detection STRAP executes `EX, A` where A is a CW: execute exception. MCP goes via the table of
exits ($15 refill) to ERR, which recovers A from the interrupt location counter and subtracts (p.38).
Serious ones, 1-28, are at the front, count `Esss`, printable on the console typewriter under a Correction
card (pp.38, 176). Messages pp.176-179, listed with their detecting area. I-O messages p.179.

### 9.2 ERRIN, ERR, ERRNUM, ERRPRT

Five lists of 32-bit entries: Pass 1, UITER 1, Pass 2a, UITER 2, Pass 2b (p.37). Bounds `Errfwa`,
`Errtop`; each list preceded by a record of (24-bit number of errors not listed, 8 zero bits) (Fig. 5, p.38).

- `ERRIN`: at the start of each part; stacks the first location of each list (p.37).
- `ERR`, per exception: Pass 1/2a/2b form (Fig. 3): unit 20, field 4, message 8. UITER form (Fig. 4):
  symbol entry location 24, then 8 bits printed as zero (Gap 8). Returns to MCP to resume (p.38).
- `ERRNUM`, per unit after OUTPUT's errors (p.37): seeks entries with the `Unit` value (lists 1, 3, 5) or
  the `Symbol` value (lists 2, 4); page 12 bits from accumulator offset 8; line 8 bits at offset 0;
  fields zeroed for lists 2, 4; puts those two in chronological order, the others being so already
  (p.39). Final form, Fig. 6: page 12, line 8, field 4, number 8.
- `ERRPRT`: once at the very end, merges the five lists (p.37), sorts into page and line sequence, lists
  via OPLIST, then a message of the number not listed because the buffer was exceeded (p.158 box 35).
- Implemented in `strap/strap2/listing.py` (`errnum`, `errprt`) and `errtab.py`; N28-1081 page 13 adds that
  the list prints "in sequence by page and line number" and that each line containing an error gets an extra
  `*` after the line number and its `*`.

An error references the last line of the statement's binary output (C28 p.20).

SEM, REM: four-word intermediate mask in the variable part; bit = message status, 0 restore, 1 suppress;
`Ziotpt` value locates it (p.32). `$`-prefix suppresses (p.25: sixth flag; Fig. 20 p).

### 9.3 Error flags

Set of six in `Ziopx` (p.25, p.189): five symbol flags and suppress; intermediate buffer in each pass; ORed
into the unit after each unit in Pass 1 and 2a (p.25). After Pass 1 only the sixth can be on (p.25). VALUE
tells the caller (`Sinser`) when an expression contains error symbols (p.25, p.34). OUTPUT prints these before
the statement (p.34, p.157 box 2). Texts (C28 pp.20-21): `UNDEF`, `QUEST` (multiple no contradiction), `MULTI`,
`PSEUDO` (circular), `CONTAG`, on the line immediately preceding the first line of the statement. p.157 box 2:
"for undefined, multiply and pseudo-defined symbols and contagious errors".

### 9.4 MACHER, XERR

`MACHER`: `SIC, Machez; B, MACHER`; internal error action, message 7; optional dump defined off. In Pass 1
returns to wind-up in MAIN, not the caller. From UITER, marks the vle as completed (p.173). Dump is of
unit in Pass 1; of vle in UITER, Pass 2 (p.173).

`XERR` (chart WA p.61, p.62): the user's UK fix-up puts the arc number in $8 value, the I-O CW address in $9
value, branches to `Xerrrd` / `Xerrwr`. `Wrop` on = write. Load I-O op into $7 value; 100 in $8 count; save
table of exits at `Xerr9` (2,3,10). Locate arc, suppress EOP, new TOE: EOP -> `Xerr4a`, UK -> `Xerr2`; start;
save $7-$9 at `Xerr5`; `$RET` (4-8). `Xerr4a`: restore TOE, branch to the original EOP fix-up (12-14). `Xerr2`:
restore 7,8,9; count-1; nonzero -> retry (15-17). Zero: message "UNCORRECTED ERROR READING/WRITING DISK" +
"RELATIVE ARC" via System Output (18,11,21,19). Write -> user EOP fix-up, assembly continues; read ->
terminate (20,22). Pp.62, 179.

---

## 10. INTIN and NAMEIN

**INTIN** (chart II p.141, IJ p.142, p.143): initial `SIC, Intiz; B, Ininit`; thereafter `SIC, Intiz; B, INTIN`.
Control word preceding the unit goes to `Ibufxw`. Three buffers, three write CWs (5,6). It reads, passes units
out, and rewrites them, so unit updates of 2a persist to 2b (p.138).

```
1 BEW,$ waits for first read; EOP fix-up turns it to NOP
2 Ibufxw bit 25 (last in buffer)? yes -> INWR(5)
IRFL 3 next CW into Ibufxw by refilling $2
4 last in buffer? no -> exit; yes -> 10
10 CW bit 26 (last in file)? yes -> INWR(5)
IBAH 11 read count > 0? no -> wait; 12 subtract 1 -> exit
INWR 5 swap write CWs; 6 write buffer
7 CW bit 26? no -> 3;  yes -> 8 write an extra buffer indicating EOF; 9 swap I-O data in COMREC; exit

IRDINT (EOP on read): 13 buffer the EOF record? -> $RET.
  14 count+1. 15 SW2 off (first time): 20 turn on -> IREAD.
  16 READ IND 1 on: off, -> IREAD 18 swap read CWs; 19 read; $RET
             off: 17 turn on READ IND 2; exit
IWRINT (EOP on write): 21 READ IND 2 on: off, -> IREAD. off: 22 turn on READ IND 1. exit
```

CW format: Fig. 20 p.189 (next word 0-17; 25 last CW; 26 last in file; 28-45 words; 46-63 next CW).

**NAMEIN** (chart NI p.160, p.161): initial `SIC, Nameiz; B, Namint`; then `SIC, Nameiz; B, NAMEIN`. Called only for
named units. Exit: `Namexw` value = address in memory of the check character; count = characters; bit 25 = file
exhausted. Two buffers.

```
init 19: first-read indicator, C on; read
1 wait for first read; 2 step $2 to first character of the name
3 count > 128 (chart; text: "If less", equal unspecified)? yes -> 12 D on; NAMETB. no -> 4 count into Namexw
5 count = 0? yes -> 9 flag Namexw as EOF
6 check character address -> Namexw value
7 count of next name + buffer location past end? yes -> NAMETB(13)
NAMEIY 8 C off -> exit. C on, turn off -> 10 reading on; 11 read; -> 1 as drawn (text: B on, read initiated)
NAMETB 13 wait read complete; 14 C on; 15 D on: 16 next count;
17 reset to first buffer; 18 D off: exit. D on, off -> 2
```

Name file entry = count, name, check digit, by inference from the flow; written by GETCHA (p.25). Check
digit 0-9, in `Ziname` and `Zstcnt` (p.173). OUTPUT checks: 14 digits differ; 12 flag reached before END; 13 flag
not set at END (p.176; p.157 boxes 31,32). SKIP spaces over the name, chart OR.

---

## 11. Pass 2b output: OUTPUT and friends

### 11.1 OUTPUT, chart OP/OQ pp.149-150, p.157

`SIC, Outgz; B, Outgo` (p.157). Uses $13. Names on chart: OLCN (13), GNME (14), OSS (5), OAUS (27), OERNOP (29),
OPSYM (33), OINST (9), OPT2 (7). Connector `OP15` enters at OLCN (print location); `OP14` at GNME (no
location); `OQ21` to exit.

```
1 first time? yes -> 6 OEDIT: page heading and program boundaries
2 print error flags
3 unit follows EXT? yes -> 4 construct requested extract -> OINST
OPT2 7 unit has binary output? no -> 16; yes -> 8
8 DD? yes -> 17 [chart OW]
OINST 9 store binary in punch buffer
10 determine type of card
11 buffer full? yes -> 18 move data; 22 fill loader info (origin, ID, seq no...); 26 OPPUN
12 store binary in print line (word 5 of the unit; convert)
OLCN 13 store location counter in print line
GNME 14 name? yes -> 19 NAMEIN; 23 store in print line.   May require an extra line.
OSS 5 store symbolic statement in print line.  May need more than one line.
OAUS 27 store card identification in print line
28 OEDIT: line number; heading if new page
OERNOP 29 errors with unit? yes -> 37 ERRNUM
30 OPLIST
31 last unit? no -> exit
32 check end of name file
OPSYM 33 SYN cards? yes -> NQBTP
   NUNDSY;  ERRPRT;  OEDIT time and units;  $EOJ
16 MCP statement? yes -> 15 list and punch IOD cards; exit
20 pseudo-op? no -> 21 print comment; exit.  yes -> 24 branch table; 25 routines -> OP14 or OP15
```

Boxes 15,16 (p.157): IOD cards, plus: absolute decks `TYPE,GO` and `LIM,__,__`; relocatable decks the same;
Fortran decks `TYPE,GO,FORTRAN`. Third digit-select table (p.36).

Multiple-field DD (`Zinfld`, `Oenm`) p.158-159: after printing the first field OUTPUT processes the others instead
of returning. Index word to the D field stepped by a standard 120 bits plus Fn, special exponent, gp bits. Prints
the new location and returns to box 2. Fig. 26 p.193 is the encoding.

Pseudo-ops (charts OR, OS, OT, OU; pp.151-154):

| Op | Print entry | Action |
|---|---|---|
| PRNID | OP14 | store and OPLIST statement |
| PUNID | OP14 | punch card in existing mode; store new ID |
| PUNFUL | OP14 | punch; PUNFUL indicator on |
| PUNNOR | OP14 | punch; origin card indicator on |
| PUNORG | OP14 | punch; origin and PUNORG indicators on |
| PRNS | OP14 | double space off |
| PRND | OP14 | double space on |
| SKIP | OQ21 | new page on; space name file past any name (not listed) |
| NOPUN | OP14 | punch; NOPUN on |
| TLB | OP14 | store TLB address in print; punch origin and branch cards; origin on |
| END | OP15 | store branch address in print; punch final card; last-unit indicator; punch branch card |
| SLCR | OP14 | nothing |
| EXT | OP14 | store parameters of unit; switch for following unit |
| SYN | OP14 | look up bit value, integer value, store; store index and dds |
| DDI | OP14 | nothing |
| NOPRNT | OP14 | on |
| PUNSYM | OP14 | indicator for SYN cards at end |
| SEM, REM, TAIL, LINK, SPNUS | OP14 | nothing |
| UNTAIL | OP15 | nothing |
| PRNOR | OP14 | NOPRNT and double space off |
| PUNALL | OP14 | SYN cards at end; punch all |
| NOSEQ | OP14 | punch; suppress sequence number on |
| RESEQ | OP14 | punch; that bit off; clear sequence field |
| PRNTALL | OP14 | allow printing entire symbol table |
| DUPLI | OP14 | nothing |

SLC, chart OS p.152, to OP15: PUNFUL off -> force origin card, set origin indicator, store new value. PUNFUL on: first
SLC -> store new value. Otherwise SLC < counter -> low-SLC indicator, store counter for comparison (message 57,
134 plausibly). Else turn off low-SLC; equal -> nothing; greater -> difference processed as DRZ in PUNFUL.

DR, chart OV p.155, p.158: PUNFUL: punch equivalent blank words/cards, no control information possible. DRZ waiting: origin
card first. Data over origin-card capacity: punch. DR waiting and data in buffer: punch; no data: add to previous DR
length. No DR waiting: no data -> skip before loading; data -> skip after loading, unless more than a full card: punch
first (10-13). Then count skip by DR length, store dimension value in print line (9). OP15.

DD, chart OW p.156, p.158: numeric (`Ziotpt.25`, MQDD) goes right. Alphabetic: gp ORed via `O6pal`, data to punch buffer;
`OPNOUT` punch if exceeded (4). OP15 with **no conversion to print**. Numeric: gp OR'ed in each unit of a multiple-unit DD, in
temporary (5); `Oenm` if `Zinfld` multiple (6,7); store data and gp, signed-data sign byte stored separately (8);
`OPNOLT` (9); convert for print (10): "not in octal-hex": Floating: exponent, fraction, sign byte. Fixed: sign byte
separate. Advance (12). OP15.

Symbolic byte size truncation of alphabetic DD is done by OUTPUT in the final pass (p.26). Numeric DD binary in the
unit is double-precision floating (normalized; Fn unnormalized) until OUTPUT adjusts it (p.26); algorithm **UNSPECIFIED** on
these pages.

### 11.2 Listing line

From the charts: `[line no][location][binary][name][statement incl. comment][card ID]`.

- Line numbers per page, kept by OUTPUT; OEDIT's count is physical lines per page, from COMREC word 9 bits 32-39 (p.165, p.9).
- Name file supplies the name; statement from the unit: `$3` + fixed size + `Zilcfd` bits (p.25). Statement length, `Zilsst`. Blanks past
  the last non-blank and the semicolon are not stored (p.25). Comment and B-type cards are not a true image (p.25).
- Octal-hex (C28 p.18): 24 bits octal with a point between 6th and 7th digits, then 2 hex digits; a full-word instruction is two.
- SYN (C28 p.20, Fig. 3 line 2): bit value in location column with sign; integer in octal at binary column. DR: words.bits reserved.
- Columns' print positions, overflow rule, comment column: **UNSPECIFIED** in guide.

### 11.3 OEDIT, chart EI p.164, p.165

`SIC, Oedita; B, OEDIT`. Inputs: `Oqend` end time message; `Oqinit` initial; `Onpge` new page; `Odbsp` double spacing.

```
1 Oqend? 15 elapsed; 16 OPLIST time message
2 Oqinit? 3 init lines/page
OQAA 4 Onpge? no: 7 line count exceeded? no: 8 Odbsp? 9 count+2; 10 double; 11 save / 12 count+1; 13 single; 14 save
5 OPLIST page heading; 6 carriage for double space
```

Page heading (p.165): initial time clock, card ID columns 73-80, ID from most recent PRNID, page number, location counter
(within a word) at page start, column titles. First-time heading adds program boundaries (p.157 box 6). Heading text:
**UNSPECIFIED** in guide; printed in N28-1081's Appendix E, section 12. C28 p.19 Fig. 3 prints `TIME CLOCK`, `PAGE`, `LOCATION`, `BINARY OUTPUT`, `NAME`, `STATEMENT`, `... LOWER
MEMORY BOUND`, `... UPPER MEMORY BOUND`, `THIS ASSEMBLY REQUIRED nn SECONDS`.

### 11.4 OPLIST, chart OL p.166, p.167

`CNOP; SIC, Oplisz; B, OPLIST; CW, loc, words`. Terminate: `Oprien`=1. Wait `Olfull` reset by write EOP. Switch 1 NOP-branch by `OPLIPU`
(chart "OPINT", first of either routine inits both). Convert, move, step `Olblk`. Last entry or block full: `Spool1` -> `$SPR`, blank buffer;
`Oldisk` -> next arc from `Oarcx` in the first word, `Oarcx` stepped, count in first word, `$W`. Reset to word 2, max line count. Last: bit
25 word 0; count = (max-1) - blocking count; stored in count field. Arc word: bits 0-17 next arc, 28-45 lines, 25 last. (p.10.)

Listing destination (p.167, p.9): last compiler in chain: `$SPR`; not last: disk or system output per COMREC word 9.

### 11.5 OPPUN, chart OM p.162, p.163

`CNOP; SIC, Oppunz; B, OPPUN; CW, loc, words`. Terminate with `Orien`=1; without a card: `CNOP; SIC, Oppunz; B, Oppunx; NOP; NOP`. Wait
`Opfull`. Switch 2. Move under `Opblk`. Last or full: `Opdisk` -> arc from `Oarcx`, count, `$W`; `Spool2` -> `$SPU`. Reset. Last also: EOF word.
Destination (pp.9, 163): last, compile only: System Output; compile & go: disk from arc 0, also System Output if punch option;
not last: disk and System Output.

Listing and binary interleave by `Oarcx` (p.11, Fig. 2). Arc header (p.10): 0-17 next arc; 20 binary, 21 A6, 22 A8; 24 off listing, on binary;
25 last; 26 IQS; 28-45 records per arc; 46-63 previous listing arc. Second word a dummy; data in third (p.10). Messages p.179.

### 11.6 NMCP, chart EA p.147, p.148

`NMCPA1` once, 2b first unit: create GO; Fortran job -> `TYPE,GO,FORTRAN` punched; else `NMCPNP` OPPUN GO, then LIM and OPPUN. LIM's fields, deck bounds:
**UNSPECIFIED** beyond p.157's form. `NMCP`, 2b per MCP op: (Np2ind=0): reference number from a binary counter in the fixed part, as A8, into the
80-column card image in the unit (2); `Zoreel`=1 -> exit (3); VALUE exit address from a coded expression in the variable part (4), A8 into the image
(5, `NMCPBR`); none given: blank (p.148). Field positions: **UNSPECIFIED**.

### 11.7 NQBTP, chart EB p.168, p.169

From OUTPUT only if `Opsym` is a Branch; PUNSYM or PUNALL sets it, NQBTP restores. PUNALL also `Nqpall`. Walk from `Tsymb + Azfw` (1), PUNALL or
marked (2,3) -> eight name characters; dds, values, index (4); dimensions (5,6) recomputed by dividing products; `Opunsa` CW, OPPUN (7);
continuation if name > 8 or extra dimensions (8,9 -> 7); undefined not punched (p.169). Restore (10-12).

Card (p.169): 2-9 Name; 10-12 SYN; 13-22 (Mode,FL,BS),; 23-38 `(8) +xxxxxx.xx`; 42-53 `(8) +xxxxxxxx`; 56-60 `($xx)`; 61-72 `,(Dim1,...,Dimx)`;
73-80 ID. Continuation: 1 `*`; 2-9 name; 10-xx dimension reference.

### 11.8 NUNDSY, charts EG, EH pp.170-171, p.172

Direct from OUTPUT. One iteration via ANEXT with `RSERCH` for the name; first 50 characters only.

```
init; 2 ANEXT, no more -> NMOVLE; 3 function
4 Zst1: undefined: 5 bypass on? no: 6A on; 6B printing all? 7 header; 8 RSERCH, 9 NCVAD convert and print address; next
NISUSE 10A SPNUS? or 10B Zst24 used? -> 12. else 11 stack function, count
12 Zst22: 13 error message (131); next.   14 Zst23: 15 stack.  16 Zst4: 17 stack.
NMOVLE 18A printing all? no: 18B unused? 19 header; 20-23 table walk, RSERCH, NCVAD
NANYMD 24 any multiply? 25 header; 26 NLISTO.  NANYCI 27 circular? 28; 29 NLISTO.
30A PRNTALL? 30B switch on, 30C re-enter NUNDSY.  30D housekeeping, exit
NCVAD: function address, BCD, OPLIST, blank.   NLISTO: function, RSERCH, OPLIST, blank, more.
```

Unused list prints address; multiply and circular print names (p.172, p.171). PRNTALL prints whole table with address (p.158). Message 128
"MULTIPLY ASSUMED" (p.178). Text of headers: **UNSPECIFIED**.

### 11.9 Punch cards

Relocatable: pp.187-188 (data, common definition, Fortran branch, Fortran program, binary instruction, special origin, relocation bits). Absolute card:
guide silent; C28 p.22 gives the origin card, code 1.9,1.10,1.11; ID col 2 is 12 bits of `$TC`; sequence 3; checksum 4; 5.0 skip/zero; 5.1 before/after;
5.2-5.11 primary count (0-748); 6-7 origin; 8-9 secondary; 10.8-71.11 up to 736 bits; 73-80 ID. Rest of that manual's card section not read here.

---

## 12. Comparison with MCP p.48, a real STRAP II listing (`VERSION 03/15/64`)

Read at 220 dpi, with C28 p.19 Fig. 3 (1963) alongside.

**Agree**

| Feature | Listing | Guide |
|---|---|---|
| Start with no SLC at `000041.00` | line 3 | absolute counter's initial 41 octal (p.33). So `SLC,(8)41.0` in `decks/mcpref_example2.strap` is a transcription device. Message 100 `ADDR LESS THAN 33.` (p.178): 33 decimal equals 41 octal, the same number; the guide, the error table and this listing agree |
| IOD and PRNS: no location, no code | lines 1, 2 | MCP goes box 15, exit (chart OP). PRNS enters at OP14 (chart OR) |
| No GO, LIM lines | - | p.35 |
| Line number per page, restart | 1-44, 1-25 | p.165; page 12 and line 8 bits (p.39) |
| Two half-words for full-word instruction | line 12 | C28 p.18 |
| 24-bit octal, point, 2 hex | `000040.10 00` | C28 p.18 |
| DR prints size | `000017.00` for 15 | chart OV box 9, C28 p.20 |
| DR location then skip | `000056.00`, `000075.00` | p.158 |
| END prints transfer | `000145.00 000041.00` | chart OT, to OP15 |
| Alpha DD: location but no code | line 24 (`000143.00`) | chart OW path bypasses box 10. C28 p.20 is silent for alpha |
| Half-word after CW rounding | `000053.00` half-word then `000054.00` CW | 12A-12B, p.33 |
| Statement in right half, comment right of it | all | p.36; C28 p.18 |
| Name column before statement | START, CW ... | chart OP |
| Line-1 `B RON` | col. 1 type, name | card image kept in the unit, p.148 |

**Differ, or the guide is silent**

- Line mark: 1963 `n-`, 1964 `n*`. Guide silent.
- The second `*` after location: 000054.00, 000056.00, 000131.00, 000142.00, 000145.00, and alone on line 2. Two readings, both recorded, neither implemented:
  - **The text.** N28-1081's revised Appendix D (page 13, C28 PDF p.71, read in the ink): "On the listing itself an extra asterisk is printed following the line number
    and asterisk on all lines containing an error." Both prints put it after the location, not the line number. No page says which errors these lines carry.
  - **The prints: a binary card is punched at the line** (DERIVED). The second specimen is N28-1081's Appendix E (page 16, PDF p.74): `*` on lines 17, 19, 23 (the three DRs:
    FOX, ZEBRA, SOME OTHER LONG NAME) and 25 (END); none on any instruction, DD, XW or SYN. Every starred line in both prints is one at which OUTPUT must punch:
    a DR with data in the buffer (p.158 boxes 6-13: BUF1, MESG, FOX, ZEBRA, SOME OTHER LONG NAME), END's final card (OP15), or a card filled: 736 information bits, 23
    half-words (C28 p.22, and the errata's "0 to 736"), and CW at 000054.00 and EPGK at 000131.00 are each the 23rd half-word from a card's start (41.00, 116.00).
    The unstarred DRs, BUF2 and EXIT, follow a DR with nothing between (box 8: "the DR length can be added to the previous DR length"). Line 2's PRNS follows the
    IOD card, which is punched (MCP cards). The earlier rejection of the card reading, "116 to 131 is only 18 half-words", miscounted: it is 22 half-words, so 131.00 is
    the 23rd. Testable once OPPUN is written; it must give exactly these ten lines.
- Apostrophe after each statement: guide silent here. Deck's header reads it as C28 p.2's comment mark.
- STRAP II's own heading is printed in N28-1081's Appendix E: `TIME CLOCK`, `PUNID`, `CARD ID`, `DIST. OF 3/01`, `3/01`, `PAGE NUMBER 1`, then `LINE LOCATION
  BINARY OUTPUT NAME STATEMENT ... LOCATION 000100`, the slots p.165 lists. So p.48's JOB/TIME/DATE/VERSION block above is MCP's, and the figure cropped STRAP's heading
  (DERIVED). strap2 prints TIME CLOCK, PAGE NUMBER, the titles and LOCATION; the sources of PUNID, CARD ID and the two `3/01` fields are not stated.
- Not visible on the figure as printed: `TIME CLOCK`/`PAGE` header form, column headings, LOWER/UPPER MEMORY BOUND, `REQUIRED nn SECONDS`, `THE END`. Figure may be cropped. Printed instead above:
  `JOB,PPNAME`; `TIME 14/27/18, DATE 04/13/64, VERSION 03/15/64`; `B TYPE,COMPILGO,STRAP,NOPUNCH`. p.165 has no version or date. Whether STRAP II or MCP prints that block: **UNSPECIFIED**.
- CW line format `000056.00+ 000 000017 000000` agrees with C28 p.18 "index word" form. Guide does not say.
- Page split at 44 is one run's setting (COMREC 9.32-9.39). The first page's 44 count includes lines 1, 2.
- `,RON` assembling to `000001.00 80`: guide gives the counter (p.148), not the symbol's value here. See Pass 1's MIOD (not read here).
- Card ID (OP/27): none visible. Listed run had a blank field, or not printed; undetermined.
- Lists at the start vs end: C28 p.20 prints four symbol lists at the beginning; guide prints them after the program (chart OQ, p.157, p.37). The figure shows neither.

---

## 13. Gaps and contradictions

Page sweep basis: every page below was read in the ink. Sweeps for names used `docs/ocr` as a finding aid, then read the hit.

**Not read**: pp.1-2, 4-7, 8, 15-18, 20-24, 27, 63-126, 128-134 (Pass 1, another reader), 180-182 (coprocessor), 195-196 (App. B), 207-211 (Apps. F-H, seen only in OCR), and
`C28-6129` beyond printed pp.18-22. A claim of absence below is limited to the pages read plus the OCR sweep.

**Gaps**

1. **Zst layout absent.** Function bit positions are not tabulated (Fig. 22 defers to them; p.202 names them; OCR sweep of `zst` hits only pp.135, 137, 140, 168, 170, 173, 185-186, 191, 202-203). Same for offsets of `Zi...` beyond Fig. 20.
2. **Pass 2b's counters.** NPS3 is not described. p.35-36 check 2b's "present setting" against 2a, and p.19 says 2b combines; the initial state and how symbolic portions recompute in 2b: unspecified.
3. **Undefined symbol assignment.** p.205 and C28 p.20 give the value; no routine assigns it. UITER 2's box 13 sends any valueless symbol to MACHER (p.137), and undefined symbols are in the table by then (p.33). Either they're valued at box 11, or Zst1 bypasses. Unspecified. (Hi-lo running first in UITER 2 fits, as INFERENCE only.)
4. **Kamms** appears only at pp.136-137. Not described.
5. **INSERT bit positions and fill chains.** Names only (p.144). Which op takes which chain lives in op index and `TOPA` tables (p.202; Fig. 23 p.192): the BOPSER table contents the plan already lists as lost.
6. **Special symbol `n` rule; its full/half indicator** (p.33 vs Figs. 21-22). Coded expression for "sum" can be guessed from SYN but is not printed.
7. **Hi-lo candidates** beyond first, SLC, END (p.33, 35) and hi-lo reduction.
8. **UITER error record** (Fig. 4, p.38, zoomed) has 8 zero bits and no place for a message number, yet ERRNUM needs it (Fig. 6). `ERRPRT` has no write-up beyond pp.37, 158.
9. **`Utab` mechanics**, EXT's extract construction, DD conversion, `.L`/`.R` arithmetic, subscript scaling, column positions, heading and list texts, LIM fields, `Zicomm` insertion positions.

**Contradictions**

10. WROP: text "on, a write" (p.62) vs chart box 18 on -> READ message, off -> WRITE (p.61). Box 20 agrees with the text.
11. ADDORD normal return: linkage puts normal at tbl+3.32 (p.48), exit is `B,-1($15)` (p.46). Box 9 "$X15 by 3.32" (p.43, zoomed) lands on tbl+3.0, the error exit. ADDUNO's 3.0 lands correctly at +2.32 for its own linkage; its error exit "made from ADDUNO" (p.48) can't be derived. Found return works (2.32+0.32-0.32). Code must follow p.48 behaviour, not the increment.
12. DECODE box 1 tests `Zifall` "on" as finished, but `Zifall` is "set to one on entry" (p.140). Fig. 20 n: "nothing left for DECODE". Order of test and set is unspecified; p.19 sets it on in Pass 1.
13. NEXT box 2 tests whether DECODE handled the unit by `Zifp2` and adds it "is always on in Pass 2" (p.146); the test can't discriminate.
14. MOVE situation 3 is printed `Q = S`, the same as situation 2 (p.41, zoomed). The flow needs Q not = S.
15. Unit width: p.12 says 8 words; Fig. 20 shows control + 6. Resolved by `Zicomm` (Fig. 17 p.184). p.157's "word 5" is `Ziotpt` only counting from `Ziadab` = 0.
16. Five symbol flags (p.33, p.34, p.189) vs `Sinser` (BU, 4) (p.56, Fig. 9) and `VVSER`. p.25's list of "first five" names only four or arguably five. Bit assignment: unspecified.
17. `Sinsx` is (BU, 2) on p.56; (BU, 1) in Fig. 9, p.58. `Sinm`, `Sinmq` appear only in Fig. 9. `Sindsq` appears only on p.56. `Zifpm` (p.140) is `ZIFPMN` in Fig. 20 (p.189).
18. UITER: text says "Box 27" twice (p.137), first meaning 26. p.137 box 21 "Branch to box 30 if ... not exist"; chart merges both to 43 then 30.
19. Chart FA/8 says "first unit through Pass 2A" on the not-2a arm; text p.35 "first cycle through Pass 2b".
20. OUTPUT text boxes 33, 34, 35, 36, 38, 39 (pp.157-158) are unnumbered or absent on chart OQ.
21. NAMEIN text uses indicators A, B, C, D (p.161); the chart shows first-read, reading, C, D (p.160).
22. XERR text names both `Xerrz` (Boxes 4-8) and `Xerr2` (Box 15); I take them as one (p.62).
23. Unit counter at NPS2: zero (p.33); "set to one at the start of each pass" (p.173).
24. `SPNUS` (pp.31, 35, 172) vs `SPUNS` (p.36). Chart labels the routine `NSPRES`.
25. Boxes 22, 23 of DECODE say "GETFLD goes to VALUE" (p.140), chart VALUE (p.139); GETFLD is Pass 1.
26. Contradictory multiples: first definition stands (p.127, C28 p.21 MULTI), yet C28 p.21's CONTAG example (`A SYN,1000.0; A SYN,500.0`) says 500.0. strap2 pins the first (`tests/check_strap2_flags.py` E3). **RESOLVED** by N28-1081's errata (page 18, C28 PDF p.76, read in the ink): "page 21 - column 2 - line 5: not value 500.0 but value 1000.0".
28. C28 p.20's QUEST example is a label then a SYN of the same value; chart RE (p.126) boxes 1 and 12 make any repeat that is not SYN over SYN contradictory. strap2 follows the chart (test B9).
29. N28-1081 page 7 (C28-6129 PDF p.65, April 1963) supersedes C28 p.21 on MULTI: the flag precedes both definitions, and a reference to the symbol gets CONTAG where p.21 (5) gives MULTI. Both are kept, as `Pass2(edition=)`.
31. Lists at the start or the end: C28 p.20 says the beginning, the guide the end. **RESOLVED** by N28-1081's errata (page 18): "page 20 - column 1 - line 35: not beginning of the listing but end of the listing".
32. The lower memory bound: C28 p.20 makes it the word before the first used, and Fig. 3 prints 000077.00; Appendix E (1963), the same program, prints 000100.00, the first word used. The errata leave p.20 standing. `Listing(form=)` keeps both.
30. Chart EG box 6B prints a header for the undefined list only when printing all symbols (box 7); the normal undefined list has none, as read.
27. Lists and errors: guide at the end (p.37, p.150); C28 p.20 at the start. Guide is the later and governs.
