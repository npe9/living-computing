# STRAP II: the specification and the host-side reconstruction

IBM's STRAP II is lost. These three files specify it from C22-6729, its
internals guide. `strap/strap2/` implements them host-side and is
RECONSTRUCTION, in the order `../reconstruction_plan.md` gives. A 7030 program
that assembles its own source to the same bits comes after it.

| file | covers |
|---|---|
| `formats.md` | COMREC, disk output, the unit, tables, coded expressions, errors 1-148, relocation, the deck, the memory map |
| `pass1.md` | the order of a card block, GETFLD, GETCHA, MQDD and the other Pass 1 routines, what fills each unit field |
| `pass2.md` | UITER, the two location counters, DECODE, INSERT, NEXT, TABMAN, VALUE, OUTPUT, the listing |

## How far to trust them

Three agents read the guide separately, each in the ink for its own scope, on
2026-11-08. Each file states the pages it did not read and lists the
contradictions it found. In `formats.md`, UNSPECIFIED is weaker for pp.15-172,
which it swept by OCR only; `pass1.md` and `pass2.md` read most of those pages.

Checked by a second reader against the ink: **Fig. 20 p.189 only**, every field
of the control word and fixed portion, which `formats.md` and `pass1.md` agree
with. The rest is one reader's work and should be reread before it is relied on.
A disagreement between these files is a reason to go back to the page.

## How far the code reaches

`strap/strap2/` follows the guide's phases: Pass 1 writes expanded units in
Fig. 20's bits, with GETFLD's coded expressions (App. C) inside them; UITER and
Pass 2a keep the two location counters and resolve the cascade of special
symbols; Pass 2b decodes each unit and fills in the word. It is not `strap_asm`
restructured, but it borrows `opcodes.py` and `strap_asm`'s `enc_*` encoders as
leaf facts. Measured 2026-11-09:

| check | result |
|---|---|
| `tests/check_strap2_coded.py` | Figs. 28 and 29 pp.200-201, bit for bit (208, 447 and 196 bits) |
| `tests/check_strap2.py` | what the guide says and `strap_asm` does not do, by hand |
| listing oracles run on strap2 (`check_strap2_oracles.py`) | 273 of 273 `verify_*.py`; 351 of 351 MCP pages |
| image of every deck against `strap_asm`'s | 719 the same; 7 with the known difference below; 1 both refuse |

The known difference: `strap_asm` puts a NOP in a half word rounded over before
a DR(N) or DRZ(N), and p.33 makes only a CNOP a NOP. strap2 follows the guide. No
listing prints those halves, so no oracle can decide.

**PUNREL, stage 1, is written:** PUNREL from the start of the program sets the
counter to 0 (p.33) and punches relocatable data and instruction cards
(6729 pp.187-188) and ORIGIN's O card; more than one location-counter symbol in
a field is message 123, and here the deck then stops (CHOSEN: the message
says only that it "may cause trouble in relocation", so `END-START` refuses); ORIGIN outside PUNREL is message 136.
MCP's own loader relocates such a deck to the absolute program
(`tests/gen_loader_deck_tb.py rel`). Under PUNREL, END punches no branch card
(CHOSEN).

**PUNREL, stage 2, is written:** PUNFPC/ENTER punch the FORTRAN program card,
PUNCDC/COMBLOCK the common definition card (6729 pp.186-188), nine entries a
card and continuation cards after; FEND ends the program with the FORTRAN
branch card (N28-1081 page 3). They may precede PUNREL, as in p.184's
example. Sizes are 18-bit fields, so an integer counts words and a part word
rounds up; ENTER's point is a half-word address. Outside PUNREL each is
message 136 (FEND then ends as END does, CHOSEN); ENTER and COMBLOCK out of
their mode are 138 and 137. A zero DR dimension is accepted: p.184 writes
`COMLAST DR(N), 0`. MCP's loader, outside a BSS job, returns code 4 for all
three cards, as its ATBL and AFPCRD say it must
(`tests/gen_loader_deck_tb.py fortran`).

**PUNREL, stage 3, is written:** SLCRCOM sets the counter to zero in a common
(6729 p.187): blank common when its field is blank, else the named common the
COMBLOCK numbered. Data in a named common goes on relocatable data cards with
the common's number as loading base; in blank common nothing is punched
(N28-1081 page 3). A reference to a common's symbol is relocated as an upper
address: `1 x a 1 0` blank, `1 x a 1 1 i` named, i as wide as the count of
named commons (6729 p.188; the loader, printed pp.324-325). p.184's example
program assembles (`check_strap2_punch.py` R16-R17). An SLC leaves the common
(CHOSEN).

**DDI is written** (C28-6129 pp.16-17): no space; the datum converted to
binary, right-justified in 24 bits in the symbol table, the dds kept (a null
length 24); an immediate instruction takes the length from the right end,
left-justified. A signed use mode in an immediate field is the magnitude and a
sign byte (p.17's `LI(D, 8, 4), -IDATA` = 01001000). Refused: floating-point
modes, a negative datum (the pages show none), message 132.

MBSPEC (C22-6729 pp.92-95, read in the ink 2026-11-12). An op that neither
BOPSER nor MIBA finds is retried with the option characters 0/O, 1/I, 2/Z, 5/S
substituted, in p.93's order (SXXXXXXX, XSXXXXXX, SSXXXXXX, ...: a binary count,
first character lowest). The first legal one is used and message 129 is given;
it is not serious (N28-1081 p.13), so the deck assembles. CHOSEN: the first
character is tried too, as p.93's list shows, though box 2's text says "the
second or any subsequent". The same help is given to a `$` system symbol
before error 56 (p.75), and to a secondary op whose first character is in
p.22's block of legal secondary first characters (C, S, V), before error 91.
`tests/check_strap2_mbspec.py`.

Secondary ops by class (C22-6729 pp.22-23, Fig. 24 p.192, read in the ink
2026-11-12). The secondary table is searched under a code from the primary
op: 001 VFL, 020 SEOP, 100 CW. So `+(BU,3)(SEOP)` and `CW(V+I)` are message 2,
and two secondaries are message 4. Before this, a secondary the op could not
take was dropped silently. CHOSEN: a CTL function op takes CTL's SEOP (MCP's
printed `REW(SEOP)`, p.165 line 11, is CTL(SEOP) in its machine code); a
floating op with a progressive secondary is message 2 (p.23's "establishes
the op as a variable field type op" might instead give a mode error).
`tests/check_strap2_secondary.py`.

DUPLI and REPEAT (N28-1081 page 1; C22-6729 p.27, MDUP and XINPUT; read in the
ink 2026-11-12). `DUPLI, X, Y` gives the next X card images Y more times: XINPUT
passes them on as it stacks them, then gives n*d from its duplicating block, so
each card is read Y + 1 times. A name is dropped from the copies; a card with
the comment character in the name field is copied whole. X and Y not written
integers, or fewer than X cards left: refused (no message number is printed).
CHOSEN: the X cards start at the next initial card. Before this, DUPLI was
accepted and did nothing. `tests/check_strap2_dupli.py`.

PRNTALL (N28-1081 page 2; C22-6729 charts EG, EH pp.170-171; read in the ink
2026-11-12). Specified anywhere, it prints every symbol with the address at
which it was defined, after the undefined, unused, multiple and circular lists
(box 30A re-enters NUNDSY with the PRNTALL switch on). CHOSEN: the header's
words, "ALL SYMBOLS" (box 7 prints none); every vle, so a name defined twice
prints at both definitions. `tests/check_strap2_prntall.py`.

**Not yet written:** PUNREL after absolute output; an instruction in a
named common; a COMBLOCK without a name (p.186 gives a message with no number);
a low SLC under PUNFUL; the coprocessor;
subscripts with dimensions; the system symbols' register-length
dds; `$INF` (N28-1081 page 20 adds it, 12, infinity);
the listing's page headings after the first; the field number in an error record
(always 0); and the Correction card's typewriter copy of serious messages. An
unwritten path refuses loudly.

**The error list** (`errtab.py`, `listing.py`, `tests/check_strap2_errprt.py`).
ERRNUM gives each message the page and line of its statement's last line (C28-6129
p.20), and ERRPRT prints them in page and line order after the symbol lists, before
the seconds (guide pp.37-39, p.158 box 35). The words are the number's own, from
either surviving list, `errors=`: the guide's pp.176-179 (1-148, serious 1-28) or the
update's revised Appendix D, N28-1081 pp.13-15 (1-150, serious 1-18); they differ in
wording at 24 numbers. The host's own message text stays on `p2.msg` for
`StrapError`. The 1963 form also prints an extra `*` after the line number on every
line an error references (N28-1081 page 13). Building it found messages 91 and 121
recorded twice, by Pass 2a and 2b, and 121 recorded with no unit; both now come once,
from 2b, against their statement. CHOSEN: the error line's layout; no limit on the
list. `formats.md` had message 60 as "TAIL NOT CLOSED"; the ink (p.177) has "TAIL
LEVEL NOT CLOSED", as the update does.

**The listing** (`listing.py`, `tests/check_strap2_listing.py`) matches all three printed
STRAP II listings field for field: C28-6129 Fig. 3 p.19 (1961), all 24 lines and both
memory bounds; N28-1081's Appendix E (the April 1963 update bound into C28-6129, PDF
p.74), the same program in the 1963 form, all 25 lines, its NULL, bounds and heading; and
C22-6678-1 p.48 (1964), 69 lines, from its own IOD and PRNS cards. `form=`, `mark=` and
`quote=` select the line mark, comment mark, heading and lower bound, which changed at
different times. The print positions are CHOSEN. Left unreproduced: the blank line after
Fig. 3's line 13; Appendix E line 13's `-` in the NAME column; and p.48's second `*` on
line 2 (PRNS).

**The binary deck and the second `*`** (`punch.py`, `tests/check_strap2_punch.py`).
OUTPUT puts each unit's binary in the punch buffer and punches absolute origin, flow and
branch cards by C28-6129 pp.22-23 and the update's errata (736 bits on an origin card,
800 on a flow card, END with no address to 41.8) and chart OV for DR and DRZ. The column
and row convention and the check sum are MCP's loader's, as `../bss_loader_spec.md`
reads them, and MCP's own loader has now read them: `tests/gen_loader_deck_tb.py` runs
the transcribed JOB CONTROL BINARY LOADER (printed pp.320-334) on the model over a
six-card absolute deck STRAP II punched (origin, flow, flow, origin, origin, branch),
and core equals the image bit for bit with no card taking the error return; a check
sum without its fold draws IBM's code 1, sequence numbers from 0 code 2. Every deck in `decks/` punches a deck which, decoded from the columns and loaded,
gives its assembled image bit for bit, 731 of them. The punch events reproduce the
second `*` the 1963 and 1964 prints show after the location: Appendix E's lines 17, 19,
23 and 25, and p.48's CW, BUF1, EPGK, MESG and END, every marked located line in both,
and no other. The update's text says that `*` marks a line with an error; the prints say
a punched card (DERIVED). Both are kept, `star="punch"` and `star="error"`. p.48's mark
on line 2, after the IOD card, is the one the punch does not place: the IOD card is
listed and punched at its own unit (chart OP boxes 15, 16).

**The MCP cards** (`punch.py` `deck`, `deck_images`; `check_strap2_punch.py` E). The deck
opens with NMCPA1's `TYPE,GO` and `LIM,n1,n2` cards (C22-6678-1 pp.7-8; guide p.157
boxes 15-16), `B` in column 1 and the text from column 10, in the card code of App. F
p.56. An IOD card is reproduced as submitted with its reference number in columns
63-66 and its exit table's word address in 67-72, octal (p.9): p.48's goes out as
`...0001000114`, EXIT being word 114. A REEL card is reproduced with 63-80 blank (p.10).
Each goes out at its own unit, ahead of a binary card still filling. Binary cards alone
are sequence-numbered. CHOSEN, and in `punch.py`'s header: n1 is the first origin
card's origin, n2 the word after the highest, counting the undefined symbols' words;
a null exit punches 000000; a statement that does not fit columns 10-62 on one card
stops the deck as PUNFUL does; columns 73-80 blank; the TYPE card's options not copied.
p.48's LIM (000041, 000145) is DERIVED: no print of that deck's cards survives.

**PUNID, TLB, NOPUN, PUNNOR** (chart OR, C22-6729 p.151; C28-6129 pp.13, 36-37, 39;
`check_strap2_punch.py` F).
MPUNID keeps the ID's first eight characters, blanks significant (guide p.27); OUTPUT
punches the card in process and every later binary card carries the ID in columns
73-80, outside the check sum. TLB prints its address, punches an origin card and a
branch card (41.8 with no address), and the deck goes on with an origin card. NOPUN
suppresses punching until PUNNOR (errata page 19). CHOSEN: nothing at all is punched
under NOPUN, END's branch card included. An SLCR punches the card in process and stops
punching until the next SLC (guide p.36, C28-6129 p.39; chart OT p.153 draws nothing).
NOSEQ and RESEQ (chart OU p.154, N28-1081 page 2) punch the card in process; NOSEQ
leaves the sequence column blank thereafter, RESEQ starts the count again at 1.
PUNORG (chart OR, C28-6129 p.36) punches the card in process and makes every card after
an origin card until PUNNOR (CHOSEN: PUNNOR "restores normal punching"); it ends a NOPUN.
`mcp_bootstrap_p99.strap`, which has one, now punches and loads to its image.

**PUNFUL and entry mode CC** (`check_strap2_punch.py` G). PUNFUL (chart OR; chart OS
p.152 for SLC; chart OV boxes 1-2) punches full cards: 80 columns of column binary, with
no control fields, sequence number or ID. An SLC above the counter, and a DR, become
zeros on the card. PUNNOR, PUNORG (and PUNREL) end it, punching a short card filled
out with zeros (CHOSEN). A PUNID under PUNFUL gets message 127 and is ignored. A low SLC
is NOT WRITTEN: chart OS keeps the counter "for comparison" and no page shows the
comparison. Entry mode CC converts each character to the 12-bit column App. F punches
for it (C28-6129 p.16), with 84 for a byte size other than 12 and 79 for a character with
no punches. The byte's bit order is the column as the reader delivers it, row 12 high: read
in MCP's loader, whose card-type table ATBL (printed p.331 lines 24-38) compares column 1
with 4200 for B, 2010 for O and 1300 for 0-2-3 (G9). Two `(CC*)DD(BU,,12)` statements of 45 and 35 characters, as MCP printed p.320
lines 2-3 give them, then punch one full card that reads back as
`B        HED, REP, 22LOADER, LOAD,,` with `22LOADER` in columns 73-80: an MCP control
card. All 731 decks in `decks/` now punch; each binary deck loads to its image bit for bit,
and the four MCP decks with PUNFUL open with one full card that matches the image.
Since 2026-11-10 MCP's seven PUNFUL header cards are assembled from their real DDs: the
BSP, IPL and MCP decks' (printed pp.2, 15, 99) and the four overlays' (pp.320, 335, 361,
381). They were comments behind SLC stand-ins, or left out, while the old assembler
refused CC. Each full card reads back as its `HED` control card (A5), and each second DD
lands at its printed location (A7). The blanks were measured in the ink at the listing's
fixed pitch (8 after the `B`, 27 before the name), which is MCP's control-card form
(C22-6678-1 pp.7-10). What is assembled under PUNFUL is punched, not loaded: STRAP II
assembles those units into a scratch image the punch reads (`pass2.unit_b`), and the old
assembler does the same (A6). On pp.2 and 15 the program is assembled over the header's
addresses, and the loaded image is unchanged on all seven pages.

Chart OS asks "1ST SLC" before any comparison and names no scope. It is read as the
first SLC since PUNFUL: p.99 continues the assembly of pp.2-98 (p.98 ends with
`UNTAIL`, not `END`), so its line 11 `SLC,(8)215000.` follows SLCs on pp.2 and 15.
Under PUNFUL, after the two header DDs, an assembly-wide reading would punch the jump
from 005476.34 as some 14,000 full cards of zeros (G8).

p.256 line 34, `RDLEOF (CC*)DD(BU,,12),B        COMD,OFFLINE,*`, is the one CC
statement not under PUNFUL. It is a card image MCP keeps in storage, and since
2026-11-10 it is assembled. Its 264 bits are in the MCP image at 230411.00, where they
were zeros before; the 22 characters are measured in the ink (A8).
One row is pinned against the page: p.48 line 5 prints `LVE,,CW+1.0` as `...01 80`,
where the pocket card and MCP's own listing give `B0`
(`tests/verify_mcpref_example2_listing.py`).

**Error flags, MULTI and the symbol lists** (`tests/check_strap2_flags.py`), from
C28-6129 pp.20-21, its April 1963 update N28-1081 page 7 (PDF p.65), and the guide's
p.25, p.32, chart RE pp.126-127 and charts EG-EH pp.170-172, all read in the ink.
VALUE reports the error symbols it meets, which are ORed into Fig. 20's five flag
bits in Pass 2a and again in 2b, and print as UNDEF, QUEST, MULTI, PSEUDO or CONTAG
on an unnumbered line before the statement. MULTI decides in Pass 1 as chart RE
does: a repeat is legal only for two SYNs of equal value, and then keeps the old
dds and index. NUNDSY lists the undefined, the unused, the contradictory multiples
and the circular after the statements, and gives message 131 for a legal multiple.
Messages 11 and 21, which strap2 had invented, are gone: the guide's list (pp.176-179)
and the update's revised Appendix D (N28-1081 pp.13-15) have 11 as SPARE and 21 in
a spare block (20-28 in the guide, 19-28 in the update). (The 1961 Appendix D, C28 p.54, numbers differently: there 11
is ASSEMBLY ERROR and 21 an improper first character, the later 29.) `assemble(strict=True)` refuses every message the host marks fatal, and COMREC
7.41 (p.8). COMREC 7.42 is p.8's list, which is messages 1-7 in order (DERIVED):
not the serious messages, and not the host's fatal.
**No surviving listing prints a flag or a list**, and MCP's listing predates the
update (`../NEXT.md`), so this is checked against text and charts only.

Three disagreements, each run or pinned in the test:
- **Which edition.** C28-6129 puts MULTI before the second definition and before a
  statement referring to the symbol; N28-1081 puts MULTI before both definitions and
  CONTAG before the reference. `edition=` selects; the update is the default.
- **p.20's QUEST example** is a label and a SYN. Chart RE boxes 1 and 12 allow only
  two SYNs, so strap2 says MULTI.
- **p.21 (5) gives A the second value**, 500.0; p.21 (3) and the guide p.127 keep
  the first. Pinned to the first, and the update's errata (page 18) confirm it:
  "not value 500.0 but value 1000.0".

CHOSEN: the flag bits' order; a flag line unnumbered, at the location column; QUEST
on every definition and PSEUDO on the base's; both vles of a multiple marked, the
name listed once; the used test on the dictionary's vle; box 13's equality as the
same coded expression or equal known bit addresses; COMREC 7.41 not set by a legal
multiple; the list headers' words; the contagious bit (Zst5). Chart EG prints a
header before the undefined symbols only when PRNTALL is on, so none prints.

**IOD** (Pass 1's MIOD, pp.96-97). The name's value, the reference number as a word
address, is DERIVED from one print, p.48's `,RON` = `000001.00 80`; no page states it.

**Numeric DD** (`dnum.py`, `tests/check_strap2_dd.py`): each field goes to Fig. 26
p.193 in Pass 1, with MQDNUM's and DNUM's 96-bit truncating arithmetic, and OUTPUT
makes the word from the dds, by C28-6129 pp.27-30. The test runs that manual's
examples, Fig. 3 p.19 as printed, and MCP p.359's powers of ten.

**A decision no page can check.** The charts make `1.0` come out low. DNUM's box 36
raises the radix to the running exponent, box 38 multiplies (p.109), a negative power
is an inversion (p.111 box 13), and the inverse truncates. So `1.0` is 10 x (1/10
truncated), which is one unit below 1 in 48 bits; `.5` and `17.5` likewise. OUTPUT
does not round: p.359's 1.E32 shows that. Against this, IBM's own examples write
`DD(N), 0.5` and `DD(N), 1.0` (C22-6578; Performance Characteristics Vol. 2), which
suggests programmers trusted them, but no page prints such a word in binary. strap2
follows the charts, and `strap_asm`, using the exact value, gives exactly 1. A
printed word for any fraction would settle it.

**CHOSEN for numeric DD:** one bit `m` after Fig. 26's sign byte for the number's own
sign, since the figure has no place for it; MQLL4 as an exact quotient truncated at 96
bits rather than p.111's three steps; a quotient counts as a fraction unless whole;
the system constants as 96-bit truncations; `$INF` refused.

**A lead, not a result: MCP p.359 lines 41-42.** 1.E512 and 9.99999E615 both print
exponent `3246+`, which is 1702 as eleven bits: twice 851, the exponent of 10**256. So
the 10**512 table entry seems to keep the square's exponent, unnormalized, with the
exponent flag set. The fractions (zero, and `736432...`) remain unexplained, and strap2
still refuses both.

**What building it found:**

- **A8 is the Reference Manual p.166 48-character set.** All nine values the
  guide prints match it. This is DERIVED, not stated. `;` is given 0o035, CHOSEN.
- **Radix is per field, not per instruction.** The listing has
  `LFI(BU,8),(8)..,8`, contrary to the reading of p.70.
- **`$` before an operation suppresses the end mark** (p.25, Fig. 20's bit p).
  This explains the listing's `$B,Q GO$A`, previously unexplained.
- **The value model subsumes `strap_asm`'s text hacks.** VALUE keeps the bit-style
  and integer parts apart, and INSERT adds them by the address function: 18-bit
  (B>>6)+I, 19-bit (B>>5)+I, 24-bit B+I, LX and SX (B>>5)+(I<<1).
- **Page decks' stand-in SYNs must sit under the page's TAIL.** Real tails
  require it, so `decks/mcp_bootstrap_p43.strap` and `p261` moved theirs.
- **The two sources disagree on UNTAIL:** C28-6129 p.38 says "all levels up to and
  including", guide p.125 says otherwise. Unresolved.

**CHOSEN in the code:** the function layout (`symtab.FUNCTION`, 324 bits; Zst<n>
is bit n of it); the op-table index and entries, built lazily (`optable.py`); the
A8 value of `;`; the extra-unit code ZIEXT2; a lone `$` coded as symbolic `$`
plus absolute 0 with `.L` and `+`; and a card scaffold, `cards.deck_cards`,
turning free-form decks into 80 columns.

## What the guide does not give

The implementation has to choose these, and label each choice CHOSEN:

1. **The symbol function's layout.** 231 bits, named by scattered ZST symbols,
   and tabulated on no page found. The names and meanings survive.
2. **The operation tables.** No contents, no op-index bits and no pseudo-op
   select numbers. The operations themselves are known from C28-6129, the
   Reference Manual and `strap/opcodes.py`.
3. **GETFLD's syntax-matrix cells.** pp.83-84 give only the legends; Appendix F
   constrains the cells.
4. **The A8, A6 and CC code tables**, of which nine A8 values are seen.
5. **Card details:** the check sum, the sequence scheme and the row order.
   Absolute formats are in C28-6129 pp.22-23, and the listing's loader
   (`../bss_loader_spec.md`) shows a check sum being read.
6. **Which error flag is which**, and most errors' exact detection points.

Items 1-4 are internal: they cannot change the object code. So the oracles still
apply to what comes out: the code columns of the MCP listing and of C22-6678-1
p.48, all STRAP II's own output, and CHM 102633945, a page of STRAP's own code.
