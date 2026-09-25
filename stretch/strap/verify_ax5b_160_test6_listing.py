#!/usr/bin/env python3
"""verify_ax5b_160_test6_listing.py -- jb_ax5b "I-Box 5", routine 1260,
TEST 6 (programs/ax5b_160_test6.strap) against the listing's own
printed machine code, PDF pp.61-64, octal 022062.00-022214.40.  159
rows, 182 half-words, one unbroken run; the block occupies more
half-words than it has rows because 23 of the rows are full-word VFL
TRANSMIT IMMEDIATEs.

CITED BY PDF PAGE.  jb_ax5b's listing pages carry no printed page
numbers -- the "12 11 10 9" down the left margin is fanfold
carriage-tape line numbering, and the only printed numbers are in the
front write-up, which is scanned 2-up.  Every verify_ax5b_*.py here
says "PDF p.NN" for that reason.

WHERE THIS CUTS, AND WHY.  The block was asked for from I6098
(022073.00).  It is cut eleven source lines earlier, at TEST 6's own
header row I6096 (022062.00), because that is what gives this check
two GENUINE internal address witnesses instead of none: "BD,I6098" at
022071.40 and "BD,I6096" at 022211.40.  Cut at 022073.00 the block
holds no label reference that is not a SYN.  The prologue costs four
more externals and two address expressions, all of which this
assembler already handles.

WHAT TEST 6 CHECKS, from its own header at 022062.00-022063.00:

  -TEST 6 CHKS THAT FREE INSTRUCTION
  -IS IN FACT FREE, AND THAT I-BOX
  -INDS SET ONLY CORRECT INDS.

The second clause is what 022073.00 onward does, fifteen times: clear
(or fill) the indicator register, perform ONE index operation, snapshot
word 11 into an index word, move the snapshot's refill field into the
value field, and demand an exact 18-bit pattern.

THE MECHANISM IS ENTIRELY PRIMARY-SOURCED.  Reference Manual printed
p.24 (PDF p.27), STORE REFILL (SR): "The refill field, bits 46-63, of
the index word specified by J replaces bits 0-17 of the half word
specified by bits 0-18 of the effective address.  Bits 18-24 of the
half word are set to zero."  Printed p.25 (PDF p.28), COMPARE VALUE
IMMEDIATE (KVI): "The address part, bits 0-18, of the instruction is
compared with bits 0-18 of the value field of the index word specified
by J.  Zeros are compared with bits 19-24 of the value field."  So
"SR,$X1,$X1 / KVI,$X1,(8)N" compares indicators 46-63 against N
exactly.  Printed p.24 again: "The index-flag and index-result
indicators are set in all of the preceding direct index arithmetic
operations.  The index-comparison indicators are unchanged" -- which
is why LX moves XCZ/XVLZ/XVZ/XVGZ and leaves XL/XE/XH alone; and
p.25's "The index flag and index comparison indicators are set in each
of the last three operations; the index result indicators are not set
in these operations" is the mirror image for KV/KVI.  Printed p.42
(PDF p.45): "The indicator register has address 11.  Bit positions
0-19 may be read, but not loaded ... Bit positions 20-63 may either be
read or loaded", so "Z,$IND" and "TI,1,I00O,$IND" reach 20-63 only --
all this test needs.

THE INDICATOR NUMBERS come from Figure 11, the Indicator List, printed
p.43 (PDF p.46): 48 XCZ, 49 XVLZ, 50 XVZ, 51 XVGZ, 52 XL, 53 XE, 54
XH, all with mask 0 ("Those corresponding to indicators 48-63 are
permanently set to 0", printed p.48), the first four "Reset by index
arithmetic ops. other than comparisons" and the last three "Reset by
index comparison operations".  Their conditions are printed p.23 (PDF
p.26): XCZ "set to one when the count field is zero", XVLZ "when the
value field is non-zero and negative", XVZ "when the value field is
zero", XVGZ "when the value field is non-zero and positive".

THE THIRTEEN PRINTED CONSTANTS DERIVE FROM THAT, and they match.
After SR, value-field bit b holds indicator 46+b, so the individual
indicators are XCZ (8)100000, XVLZ (8)40000, XVZ (8)20000, XVGZ
(8)10000, XL (8)4000, XE (8)2000, XH (8)1000, and "46-63 all on" is
(8)777777.  With the deck's own operands -- PDF p.114 read at 600 dpi
gives I00Z "XW,0,0,0,0  -ZERO INDX WD." 024502.00, I00O
"DD(BU,64,8),1777777777777777777777  -INDX WD. OF ONES." 024503.00,
BIT16 "XW,(8)2.00,0,0" 024542.00, BIT17 "XW,(8)1.00,0,0" 024543.00;
verify_ax5b_160k_listing.py gives I60K9 "XW,-1.0,0,0", I60K10
"XW,1.0,1,0", I60K11 "XW,-3.0,63,0"; verify_ibox2_load_index_listing
.py gives BIT30 "XW,0,32768,0" -- every one of the thirteen falls out:

  140000 = XCZ+XVLZ      I60K9  (count 0, value -1)
  120000 = XCZ+XVZ       I00Z   (count 0, value 0)
   40000 = XVLZ          I60K11 (count 63, value -3)
   20000 = XVZ           BIT30  (count 32768, value 0)
   10000 = XVGZ          I60K10 (count 1, value +1)
  617777 = ~(XCZ,XVLZ,XVZ)   from all-ones, then I60K10
  627777 = ~(XCZ,XVLZ,XVGZ)  from all-ones, then BIT30
  647777 = ~(XCZ,XVZ,XVGZ)   from all-ones, then I60K11
    4000 = XL            KV 1.0 against 2.0
    2000 = XE            KV 1.0 against 1.0
    1000 = XH            KV 2.0 against 1.0
  771777 = ~(XL,XE)      from all-ones, then KV -> XH
  772777 = ~(XL,XH)      from all-ones, then KV -> XE
  774777 = ~(XE,XH)      from all-ones, then KV -> XL

That is a derivation CONFIRMED against the page, not something this
file tests.  What this file tests is field placement.

Two of the clear-group comments understate what their constant says:
"-CLR XVLZ AND XVZ." (617777) and "-CLR XVLZ AND XVGZ." (627777) both
also have bit 2 clear, i.e. XCZ cleared too.  The constants are right
for the hardware; the comments just do not list it.

BRANCH POLARITY, since a committed file in this repo once had it
backwards.  Printed p.40 (PDF p.43), BRANCH ON INDICATOR: "This
operation causes the specified indicator to be tested.  If its value
matches that of bit 30 of the instruction, bits 0-18 of the effective
address replace the instruction counter contents."  Printed p.41 (PDF
p.44), STORE INSTRUCTION COUNTER IF: "This instruction may always be
prefixed to one of the half-word branching instructions.  It is
executed if and only if the associated branching is successful."  So
"SIC,SEN / BZXE,SERS" is ONE full-word instruction that reports only
when XE is OFF: the branch is the OK path, the error message names the
ANOMALY.  Both polarities are printed in this block and both decode
that way -- BXE at 022077.00 is "22100.72 C2", hex C2 = 11000010 with
bit 30 = 1, and every BZXE is "1304.32 C0", hex C0 = 11000000 with bit
30 = 0.  Same indicator in both: bits 19-24 = 110101 = 53 = XE.

THE ERROR IDIOM HAS TWO SHAPES, ONE POLARITY.  The prologue and the
first group branch OVER an unconditional error pair ("BD,I6098",
"BXE,$+1.32", each followed by "SIC,SEN / B,SERS"); every later group
folds the test into the SIC-prefixed branch ("SIC,SEN / BZXE,SERS").

THE NOPS ARE NOT EXPLAINED BY THESE PAGES.  Most groups put two
between the SR and the KVI; two groups (022101.40 and 022106.00) have
none; and nothing a NOP can do could change what the KVI reads --
printed p.40: "The address and index fields of NO OPERATION are not
interpreted, so they cannot cause any indicators to be actuated; no
addressable bits or locations are altered."  That they are the "free
instruction ... in fact free" of the header is CONJECTURE, recorded as
such; the two groups without them show they are not structurally
required.

ERROR MESSAGES, VERBATIM, WITH OCTAL LOCATIONS

  022062.00  -TEST 6 CHKS THAT FREE INSTRUCTION
  022062.40  -IS IN FACT FREE, AND THAT I-BOX
  022063.00  -INDS SET ONLY CORRECT INDS.
  022064.40  -2 NOPS
  022072.40  -FULL CONTROL GIVEN TO FREE INST.
  022073.00  -XCZ AND XVLZ
  022100.00  -XCZ AND XVLZ NOT SET CORRECTLY.
  022100.40  -XCZ AND XVZ
  022104.00  -XCZ AND XVZ NOT SET CORRECTLY.
  022104.40  -CLR XCZ AND XVLZ, XVZ.
  022110.40  -ABOVE 3 INDS NOT CLRD CORRECTLY.
  022111.00  -XVLZ
  022115.40  -XVLZ NOT SET CORRECTLY.
  022116.00  -XVZ
  022122.40  -XVZ NOT SET CORRECTLY.
  022123.00  -XVGV
  022127.40  -XVGZ NOT SET CORRECTLY.
  022130.00  -CLR XVLZ AND XVZ.
  022135.00  -XVLZ AND XVD NOT CLRD OK.
  022135.40  -CLR XVLZ AND XVGZ.
  022142.40  -XVLZ AND XVGZ NOT CLRD OK.
  022143.00  -CLR XVZ AND XVGZ
  022150.00  -XVZ AND XVGZ NOT CLRD OK.
  022150.40  -XL.
  022156.00  -XL NOT SET OK.
  022156.40  -XE
  022163.00  -XE NOT SET OK.
  022163.40  -XH
  022170.00  -XH NOT SET OK.
  022170.40  -CLR XL AND XE.
  022175.40  -XL AND XE NOT CLRD OK.
  022176.00  -CLR XL AND XH.
  022203.00  -XL AND XH NOT CLRD OK
  022203.40  -CLR XE AND XH.
  022210.40  -XE + XH NOT CLRD OK.
  022212.40  -TO SSIP.
  022213.40  -UPDATE CONTINUITY CHECK.

Four of those are the deck's own spellings and are kept: "-XVGV" at
022123.00 against "-XVGZ NOT SET CORRECTLY." two rows later; "XVD" at
022135.00, which is not an indicator (XVZ is meant); "-XL AND XH NOT
CLRD OK" at 022203.00, the one message with no terminal period; and
"-XVZ NOT SET CORRECTLY." at 022122.40, which is followed one
character cell later by a second smaller, slightly raised mark.  All
four read at 600 dpi.  The stray mark is not the same glyph as the
sentence's period and is most likely printer debris, so it is recorded
here rather than written into the message.

WITNESS TIERING.  EVERY SYN IS AN INPUT TO THIS CHECK, NOT A WITNESS:
each external's address was read out of the very row that names it, so
those rows verify only opcode and modifier bits.  That covers
I60SX1, I60S1, I60XW1, I6082A, I60IT, I60K8, I60K9, I60K10,
I60K11, I00Z, I00O, BIT7, BIT16, BIT17, BIT25, BIT30, BIT38, SEN,
SERS, LSEN0, SSW and IC260 -- 22 symbols, every one an assumption.

Genuinely witnessed addresses, three tiers:

  TIER 1, internal labels the location counter had to reach.
    I6098 = 022073.00.  Eighteen half-words of prologue separate it
      from the SLC, and "BD,I6098" at 022071.40 prints "22073.04 00".
      Confirmed against p.61's own label column.
    I6097 = 022072.00.  Same tier by construction (sixteen half-words
      past the SLC); nothing in the block references it, so it is
      counter evidence only.  Asserted below anyway.
    I6096 = 022062.00 is NOT a third: the SLC sets the counter to
      022062.0 and I6096 is the first label after it, so checking it
      checks the SLC against the number this transcription fed the
      SLC.  It is the block's anchor, not evidence.  What "BD,I6096"
      at 022211.40 does witness is the REFERENCE -- that a backward
      label reference 175 half-words long lands in bits 0-18 with the
      right bit 18.

  TIER 2, self-relative rows, each a witness to the location counter
    at its own row (which in turn depends on every preceding row being
    sized right):
      022065.40  CB+,$X1,$-.32
      022070.00  BE,$+.32
      022077.00  BXE,$+1.32
      022211.00  B,$+1.0
      022213.00  BD,$+.32

  TIER 3, cross-deck corroboration that promotes nothing.  I6082A is
    a SYN here, but 017227.00 is a label defined INSIDE
    verify_ax5b_16082_16083_listing.py's transcribed range, and
    022064.40's "LX,$X2,I6082A-1.0" prints 17226 -- that address minus
    one word.  Two decks, one number.

BIT-18 SELF-CHECKS, each decoded out of the printed octal pair (the
pair is bits 18-23, so bit 18 is its TOP bit) and read back against
the page.  Seven rows where bit 18 is the half-word select of a branch
address (Reference Manual p.40: "Bits 0-18, the address, represent the
branch address"):

  022065.40  CB+,$X1,$-.32  22065.03 48  pair 03 = 000011, bit18 = 0
             -> 022065.00, and 022065.40 - 32 bits = 022065.00.
  022070.00  BE,$+.32       22070.40 00  pair 40 = 100000, bit18 = 1
             -> 022070.40 = this row + 32 bits.
  022071.40  BD,I6098      22073.04 00  pair 04 = 000100, bit18 = 0
             -> 022073.00, where p.61's label column prints I6098.
  022077.00  BXE,$+1.32     22100.72 C2  pair 72 = 111010, bit18 = 1
             -> 022100.40 = this row + 64 + 32 bits.
  022211.00  B,$+1.0        22212.10 00  pair 10 = 001000, bit18 = 0
             -> 022212.00 = this row + 64 bits.
  022211.40  BD,I6096      22062.04 00  pair 04 = 000100, bit18 = 0
             -> 022062.00, where p.61's label column prints I6096.
  022213.00  BD,$+.32       22213.44 00  pair 44 = 100100, bit18 = 1
             -> 022213.40 = this row + 32 bits.

And two rows where the SAME printed position means something else, in
which the distinction is the point.  LOAD INDEX and STORE INDEX use
"bits 0-17 of the effective address" (Reference Manual p.23/p.24, and
p.24's programming note: "The LOAD INDEX and STORE INDEX operations
involve transmission of full words"), so their 19-bit field's bit 18
is a low-order bit forced to zero, not a half-word selector:

  022064.40  LX,$X2,I6082A-1.0  17226.04 10  pair 04, bit18 = 0, and
             017227.00 - 1.0 = 017226.00, a WORD address.
  022067.00  SX,$X1,I60IT+39.0  23250.03 10  pair 03, bit18 = 0, and
             023201 + 39 = 023250, again a word address.  (The 03
             against the 04 above is bits 19-22 = the index field: X1
             = 0001 with bit 23 = 1 for SX, X2 = 0010 with bit 23 = 0
             for LX.)

PROVEN DISCRIMINATING.  Observed failure sets, never predicted ones.
Seven of them, each made with `rm -rf __pycache__` run in stretch/strap
on BOTH sides of the measurement, reverted by reversing the exact
patch, with `git diff` confirmed empty afterwards.  The first four move
the OCTAL PAIR, the next two move only the HEX BYTE, and the last is a
measured null.

  DIR_INDEX_CODES["SR"] 0b10111 -> 0b00111   (bit 23, in the pair)
      16 rows, every SR in the block: 022066.00, 022075.00, 022102.40,
      022107.00, 022113.00, 022120.00, 022125.00, 022132.40,
      022140.00, 022145.40, 022153.40, 022160.40, 022165.40,
      022173.00, 022200.40, 022206.00 -- "21.03 70" -> "21.02 70" and
      "23.07 70" -> "23.06 70".

  MISC_CODES["NOP"] 0b110 -> 0b010           (bits 21-23, in the pair)
      27 rows, every NOP: 022071.00, 022075.40, 022076.00, 022113.40,
      022114.00, 022120.40, 022121.00, 022125.40, 022126.00,
      022133.00, 022133.40, 022140.40, 022141.00, 022146.00,
      022146.40, 022154.00, 022154.40, 022161.00, 022161.40,
      022166.00, 022166.40, 022173.40, 022174.00, 022201.00,
      022201.40, 022206.40, 022207.00 -- "0.30 00" -> "0.20 00".

  the branch-on-indicator path's addr19 mask 0x7FFFF -> 0x7FFFE
      1 row: 022077.00 alone, "22100.72 C2" -> "22100.32 C2".  One row
      is the STRONG result here, not a thin one: 022077.00 is the
      block's only branch-on-indicator whose target is a .40 half-word,
      and the 14 BZXE rows all aim at SERS = 001304.00, whose bit 18 is
      already zero, so they cannot move.  Forcing bit 18 to zero moving
      exactly the rows whose target is a .40 half-word, and nothing
      else, is the half-word select doing precisely what the print
      format says it does.

  the UNCONDITIONAL-branch/misc path's addr19 mask, same change
      2 rows: 022070.00 "22070.40 00" -> "22070.00 00" and 022213.00
      "22213.44 00" -> "22213.04 00".  Again exactly the .40 targets:
      022071.40 (-> 022073.00), 022211.40 (-> 022062.00) and 022211.00
      (-> 022212.00) all aim at .00 half-words and stay put, and every
      NOP already carries address 0.  Between this injection and the
      one above, five of the seven bit-18 decodes listed earlier are
      WITNESSED; the remaining two -- 022071.40 and 022211.40, both
      bit 18 = 0 -- are hand decodes corroborated by p.61's own label
      column, which no bit-18 injection can move.

  INDICATOR_BITS["XE"] 53 -> 52              (bit 24, in the hex byte)
      15 rows: the 14 BZXE rows -- 022104.00, 022110.40, 022115.40,
      022122.40, 022127.40, 022135.00, 022142.40, 022150.00,
      022156.00, 022163.00, 022170.00, 022175.40, 022203.00,
      022210.40 -- "1304.32 C0" -> "1304.32 40", plus 022077.00's BXE,
      "22100.72 C2" -> "22100.72 42".  Note WHERE it shows: 110101 and
      110100 differ only in the bit that lands at 24, so the octal
      pair does not move at all and a check reading only the octal
      field would miss it entirely.

  IMM_INDEX_CODES["KVI"] 0b0100 -> 0b0101    (the hex opcode byte)
      15 rows, every KVI: 022076.40, 022103.00, 022107.40, 022114.40,
      022121.40, 022126.40, 022134.00, 022141.40, 022147.00,
      022155.00, 022162.00, 022167.00, 022174.40, 022202.00,
      022207.40 -- the "04" byte -> "05".

  INDICATOR_BITS["XCZ"] 48 -> 49             MEASURED NULL: 0 rows.
      Nothing fails, and the arithmetic reason matters more than the
      result.  XCZ, XVLZ, XVZ, XVGZ, XL and XH never reach the
      encoder anywhere in this block: they appear only inside
      hand-written octal immediates on the KVI rows, which the
      assembler takes as literals.  The ONLY index indicator this
      block encodes is XE, on the BXE/BZXE rows.  So TEST 6 -- a test
      whose whole subject is seven index indicators -- is a listing
      witness for the NUMBERING of exactly one of them.  The other six
      numbers rest on Figure 11 (p.43), quoted above, not on this
      page.  The null was confirmed to be a null and not a crash: the
      run still printed "TILING OK: 159 rows" and 162 PASS lines.

FOR THE RECORD, two things the task asked about that do not arise
here.  There is no CNOP in this block, and no row that prints a
location without machine code, so nothing had to be SLC'd across or
SYN'd in the middle.  The 182 half-words tile 022062.00-022214.40
exactly; the tiling is asserted mechanically below rather than counted
by hand.

NOTHING HERE IS A FIRST for this assembler, and the nearest relative
should be named: verify_ax5b_160102_listing.py already witnesses the
identical "SR,$X1,$X1 / KV" refill-into-value idiom at 022300.00 and
022305.00, with the same "21.03 70".  SIC/B/BD/BE/NOP/LX/SX/Z/TI/KVI/
KV/CB+/V+ all have listing witnesses here; BXE is in I6099 and I60102,
BZXE in 1258 TEST 2, I60102 and TEST 3A.  What TEST 6 adds is scale
and repetition in one straight line -- 23 full-word TRANSMIT
IMMEDIATEs, 27 NOPs, 18 SICs, 16 LXs, 16 SRs, 15 KVI immediates, 15
branch-on-XE rows, 9 Z,$IND and 6 KVs -- plus the two long internal BD
references and a second, independent witness for I6082A's address.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish, loc_bits

prog = assemble(open("programs/ax5b_160_test6.strap").read())

ROWS = [
    # ---- I6096: build the interruption table (PDF p.61) ------------
    ('022062.00', '23041.00 80',
     'I6096 SIC,I60SX1    (ext) "-TEST 6 CHKS THAT FREE INSTRUCTION"'),
    ('022062.40', '22741.10 00',
     'B,I60S1              (ext) "-IS IN FACT FREE, AND THAT I-BOX"'),
    ('022063.00', '24570.00 80 000014.02 A0',
     'TI,1,BIT38,$MASK      (ext) FULL WORD  "-INDS SET ONLY CORRECT INDS."'),
    ('022064.00', '23065.02 10',
     'LX,$X1,I60XW1        (ext) count 64, refill I60IT'),
    ('022064.40', '17226.04 10',
     'LX,$X2,I6082A-1.0    (ext) "-2 NOPS"; 017227.00 - 1.0'),
    ('022065.00', '23201.05 11',
     'SX,$X2,I60IT($X1)    (ext) index-modified store into the table'),
    ('022065.40', '22065.03 48',
     'CB+,$X1,$-.32          self-relative: back one half-word'),
    ('022066.00', '2.03 70',
     'SR,$X1,$IA             the Interruption Address register'),
    ('022066.40', '23051.02 10',
     'LX,$X1,I60K8         (ext) I60K8 is "BD,I6097"'),
    ('022067.00', '23250.03 10',
     'SX,$X1,I60IT+39.0    (ext) table entry 39; 023201 + 39 = 023250'),
    ('022067.40', '13.22 00',
     'Z,$IND'),
    ('022070.00', '22070.40 00',
     'BE,$+.32               enable; bit 18 -> 022070.40'),
    ('022070.40', '24553.02 10',
     'LX,$X1,BIT25          (ext) the index-flag bit'),
    ('022071.00', '0.30 00',
     'NOP'),
    ('022071.40', '22073.04 00',
     'BD,I6098              INTERNAL label -- a real address check'),
    ('022072.00', '1310.00 80',
     'I6097 SIC,SEN        (ext)'),
    ('022072.40', '1304.10 00',
     'B,SERS                (ext) "-FULL CONTROL GIVEN TO FREE INST."'),

    # ---- I6098: XCZ and XVLZ ---------------------------------------
    ('022073.00', '13.22 00',
     'I6098 Z,$IND          "-XCZ AND XVLZ"'),
    ('022073.40', '23052.00 10',
     'LX,$X0,I60K9         (ext) XW,-1.0,0,0: count 0, value -1'),
    ('022074.00', '13.00 80 000021.02 A0',
     'TI,1,$IND,$X1          FULL WORD: word 11 -> index word 1'),
    ('022075.00', '21.03 70',
     'SR,$X1,$X1             refill 46-63 -> bits 0-17 of word 17'),
    ('022075.40', '0.30 00',
     'NOP'),
    ('022076.00', '0.30 00',
     'NOP'),
    ('022076.40', '140000.03 04',
     'KVI,$X1,(8)140000.0    XCZ(48) + XVLZ(49)'),
    ('022077.00', '22100.72 C2',
     'BXE,$+1.32             bit 30 = 1: branch when XE is ON'),
    ('022077.40', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('022100.00', '1304.10 00',
     'B,SERS                (ext) "-XCZ AND XVLZ NOT SET CORRECTLY."'),

    # ---- XCZ and XVZ ------------------------------------------------
    ('022100.40', '13.22 00',
     'Z,$IND                 "-XCZ AND XVZ"'),
    ('022101.00', '24502.00 10',
     'LX,$X0,I00Z          (ext) p.114 "-ZERO INDX WD."'),
    ('022101.40', '13.00 80 000021.02 A0',
     'TI,1,$IND,$X1          FULL WORD'),
    ('022102.40', '21.03 70',
     'SR,$X1,$X1             no NOPs in this group -- see the header'),
    ('022103.00', '120000.03 04',
     'KVI,$X1,(8)120000.0    XCZ(48) + XVZ(50)'),
    ('022103.40', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('022104.00', '1304.32 C0',
     'BZXE,SERS             (ext) "-XCZ AND XVZ NOT SET CORRECTLY."'),

    # ---- clear XCZ, XVLZ, XVZ ---------------------------------------
    ('022104.40', '24503.00 80 000013.02 A0',
     'TI,1,I00O,$IND       (ext) FULL WORD  "-CLR XCZ AND XVLZ, XVZ."'),
    ('022105.40', '23053.00 10',
     'LX,$X0,I60K10        (ext) XW,1.0,1,0'),
    ('022106.00', '13.00 80 000021.02 A0',
     'TI,1,$IND,$X1          FULL WORD'),
    ('022107.00', '21.03 70',
     'SR,$X1,$X1'),
    ('022107.40', '617777.03 04',
     'KVI,$X1,(8)617777.0    48,49,50 off, 51 on, rest on'),
    ('022110.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('022110.40', '1304.32 C0',
     'BZXE,SERS             (ext) "-ABOVE 3 INDS NOT CLRD CORRECTLY."'),

    # ---- XVLZ alone -------------------------------------------------
    ('022111.00', '13.22 00',
     'Z,$IND                 "-XVLZ"'),
    ('022111.40', '23054.00 10',
     'LX,$X0,I60K11        (ext) XW,-3.0,63,0: count 63, value -3'),
    ('022112.00', '13.00 80 000021.02 A0',
     'TI,1,$IND,$X1          FULL WORD'),
    ('022113.00', '21.03 70',
     'SR,$X1,$X1'),
    ('022113.40', '0.30 00',
     'NOP'),
    ('022114.00', '0.30 00',
     'NOP'),
    ('022114.40', '40000.03 04',
     'KVI,$X1,(8)40000.0     XVLZ(49) alone'),
    ('022115.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('022115.40', '1304.32 C0',
     'BZXE,SERS             (ext) "-XVLZ NOT SET CORRECTLY."'),

    # ---- XVZ alone --------------------------------------------------
    ('022116.00', '13.22 00',
     'Z,$IND                 "-XVZ"'),
    ('022116.40', '24560.00 10',
     'LX,$X0,BIT30          (ext) XW,0,32768,0: count non-zero, value 0'),
    ('022117.00', '13.00 80 000021.02 A0',
     'TI,1,$IND,$X1          FULL WORD'),
    ('022120.00', '21.03 70',
     'SR,$X1,$X1'),
    ('022120.40', '0.30 00',
     'NOP'),
    ('022121.00', '0.30 00',
     'NOP'),
    ('022121.40', '20000.03 04',
     'KVI,$X1,(8)20000.0     XVZ(50) alone'),
    ('022122.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('022122.40', '1304.32 C0',
     'BZXE,SERS             (ext) "-XVZ NOT SET CORRECTLY." + stray mark'),

    # ---- XVGZ alone -------------------------------------------------
    ('022123.00', '13.22 00',
     'Z,$IND                 "-XVGV" -- the deck\'s own spelling'),
    ('022123.40', '23053.00 10',
     'LX,$X0,I60K10        (ext) count 1, value +1'),
    ('022124.00', '13.00 80 000021.02 A0',
     'TI,1,$IND,$X1          FULL WORD'),
    ('022125.00', '21.03 70',
     'SR,$X1,$X1'),
    ('022125.40', '0.30 00',
     'NOP'),
    ('022126.00', '0.30 00',
     'NOP'),
    ('022126.40', '10000.03 04',
     'KVI,$X1,(8)10000.0     XVGZ(51) alone'),
    ('022127.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('022127.40', '1304.32 C0',
     'BZXE,SERS             (ext) "-XVGZ NOT SET CORRECTLY."'),

    # ---- clear, with I60K10 again -----------------------------------
    ('022130.00', '24503.00 80 000013.02 A0',
     'TI,1,I00O,$IND       (ext) FULL WORD  "-CLR XVLZ AND XVZ."'),
    ('022131.00', '23053.00 10',
     'LX,$X0,I60K10        (ext)'),
    ('022131.40', '13.00 80 000021.02 A0',
     'TI,1,$IND,$X1          FULL WORD'),
    ('022132.40', '21.03 70',
     'SR,$X1,$X1'),
    ('022133.00', '0.30 00',
     'NOP'),
    ('022133.40', '0.30 00',
     'NOP'),
    ('022134.00', '617777.03 04',
     'KVI,$X1,(8)617777.0'),
    ('022134.40', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('022135.00', '1304.32 C0',
     'BZXE,SERS             (ext) "-XVLZ AND XVD NOT CLRD OK."'),

    # ---- clear, with BIT30 ------------------------------------------
    ('022135.40', '24503.00 80 000013.02 A0',
     'TI,1,I00O,$IND       (ext) FULL WORD  "-CLR XVLZ AND XVGZ."'),
    ('022136.40', '24560.00 10',
     'LX,$X0,BIT30          (ext)'),
    ('022137.00', '13.00 80 000021.02 A0',
     'TI,1,$IND,$X1          FULL WORD'),
    ('022140.00', '21.03 70',
     'SR,$X1,$X1'),
    ('022140.40', '0.30 00',
     'NOP'),
    ('022141.00', '0.30 00',
     'NOP'),
    ('022141.40', '627777.03 04',
     'KVI,$X1,(8)627777.0    48,49,51 off, 50 on'),
    ('022142.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('022142.40', '1304.32 C0',
     'BZXE,SERS             (ext) "-XVLZ AND XVGZ NOT CLRD OK."'),

    # ---- clear, with I60K11 -----------------------------------------
    ('022143.00', '24503.00 80 000013.02 A0',
     'TI,1,I00O,$IND       (ext) FULL WORD  "-CLR XVZ AND XVGZ"'),
    ('022144.00', '23054.00 10',
     'LX,$X0,I60K11        (ext)'),
    ('022144.40', '13.00 80 000021.02 A0',
     'TI,1,$IND,$X1          FULL WORD'),
    ('022145.40', '21.03 70',
     'SR,$X1,$X1'),
    ('022146.00', '0.30 00',
     'NOP'),
    ('022146.40', '0.30 00',
     'NOP'),
    ('022147.00', '647777.03 04',
     'KVI,$X1,(8)647777.0    48,50,51 off, 49 on'),
    ('022147.40', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('022150.00', '1304.32 C0',
     'BZXE,SERS             (ext) "-XVZ AND XVGZ NOT CLRD OK."'),

    # ---- XL, by COMPARE VALUE (PDF p.62) ----------------------------
    ('022150.40', '24543.02 10',
     'LX,$X1,BIT17          (ext) "-XL."  X1 := value 1.0'),
    ('022151.00', '24542.04 10',
     'LX,$X2,BIT16          (ext) X2 := value 2.0'),
    ('022151.40', '13.22 00',
     'Z,$IND'),
    ('022152.00', '24542.02 90',
     'KV,$X1,BIT16          (ext) 1.0 against 2.0 -> XL'),
    ('022152.40', '13.00 80 000023.02 A0',
     'TI,1,$IND,$X3          FULL WORD: now via index word 3'),
    ('022153.40', '23.07 70',
     'SR,$X3,$X3'),
    ('022154.00', '0.30 00',
     'NOP'),
    ('022154.40', '0.30 00',
     'NOP'),
    ('022155.00', '4000.07 04',
     'KVI,$X3,(8)4000.0      XL(52) alone'),
    ('022155.40', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('022156.00', '1304.32 C0',
     'BZXE,SERS             (ext) "-XL NOT SET OK."'),

    # ---- XE ---------------------------------------------------------
    ('022156.40', '13.22 00',
     'Z,$IND                 "-XE"'),
    ('022157.00', '24543.02 90',
     'KV,$X1,BIT17          (ext) 1.0 against 1.0 -> XE'),
    ('022157.40', '13.00 80 000023.02 A0',
     'TI,1,$IND,$X3          FULL WORD'),
    ('022160.40', '23.07 70',
     'SR,$X3,$X3'),
    ('022161.00', '0.30 00',
     'NOP'),
    ('022161.40', '0.30 00',
     'NOP'),
    ('022162.00', '2000.07 04',
     'KVI,$X3,(8)2000.0      XE(53) alone'),
    ('022162.40', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('022163.00', '1304.32 C0',
     'BZXE,SERS             (ext) "-XE NOT SET OK."'),

    # ---- XH (PDF p.63) ----------------------------------------------
    ('022163.40', '13.22 00',
     'Z,$IND                 "-XH"'),
    ('022164.00', '24543.04 90',
     'KV,$X2,BIT17          (ext) 2.0 against 1.0 -> XH'),
    ('022164.40', '13.00 80 000023.02 A0',
     'TI,1,$IND,$X3          FULL WORD'),
    ('022165.40', '23.07 70',
     'SR,$X3,$X3'),
    ('022166.00', '0.30 00',
     'NOP'),
    ('022166.40', '0.30 00',
     'NOP'),
    ('022167.00', '1000.07 04',
     'KVI,$X3,(8)1000.0      XH(54) alone'),
    ('022167.40', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('022170.00', '1304.32 C0',
     'BZXE,SERS             (ext) "-XH NOT SET OK."'),

    # ---- clear XL and XE (PDF p.64) ---------------------------------
    ('022170.40', '24503.00 80 000013.02 A0',
     'TI,1,I00O,$IND       (ext) FULL WORD  "-CLR XL AND XE."'),
    ('022171.40', '24543.04 90',
     'KV,$X2,BIT17          (ext) leaves XH on, XL and XE off'),
    ('022172.00', '13.00 80 000023.02 A0',
     'TI,1,$IND,$X3          FULL WORD'),
    ('022173.00', '23.07 70',
     'SR,$X3,$X3'),
    ('022173.40', '0.30 00',
     'NOP'),
    ('022174.00', '0.30 00',
     'NOP'),
    ('022174.40', '771777.07 04',
     'KVI,$X3,(8)771777.0    52,53 off, 54 on'),
    ('022175.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('022175.40', '1304.32 C0',
     'BZXE,SERS             (ext) "-XL AND XE NOT CLRD OK."'),

    # ---- clear XL and XH --------------------------------------------
    ('022176.00', '24503.00 80 000013.02 A0',
     'TI,1,I00O,$IND       (ext) FULL WORD  "-CLR XL AND XH."'),
    ('022177.00', '24543.02 90',
     'KV,$X1,BIT17          (ext) leaves XE on'),
    ('022177.40', '13.00 80 000023.02 A0',
     'TI,1,$IND,$X3          FULL WORD'),
    ('022200.40', '23.07 70',
     'SR,$X3,$X3'),
    ('022201.00', '0.30 00',
     'NOP'),
    ('022201.40', '0.30 00',
     'NOP'),
    ('022202.00', '772777.07 04',
     'KVI,$X3,(8)772777.0    52,54 off, 53 on'),
    ('022202.40', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('022203.00', '1304.32 C0',
     'BZXE,SERS             (ext) "-XL AND XH NOT CLRD OK"  (no period)'),

    # ---- clear XE and XH --------------------------------------------
    ('022203.40', '24503.00 80 000013.02 A0',
     'TI,1,I00O,$IND       (ext) FULL WORD  "-CLR XE AND XH."'),
    ('022204.40', '24542.02 90',
     'KV,$X1,BIT16          (ext) 1.0 against 2.0 -> XL on'),
    ('022205.00', '13.00 80 000023.02 A0',
     'TI,1,$IND,$X3          FULL WORD'),
    ('022206.00', '23.07 70',
     'SR,$X3,$X3'),
    ('022206.40', '0.30 00',
     'NOP'),
    ('022207.00', '0.30 00',
     'NOP'),
    ('022207.40', '774777.07 04',
     'KVI,$X3,(8)774777.0    53,54 off, 52 on'),
    ('022210.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('022210.40', '1304.32 C0',
     'BZXE,SERS             (ext) "-XE + XH NOT CLRD OK."'),

    # ---- exit -------------------------------------------------------
    ('022211.00', '22212.10 00',
     'B,$+1.0                self-relative: +64 bits -> 022212.00'),
    ('022211.40', '22062.04 00',
     'BD,I6096              INTERNAL label 175 half-words back'),
    ('022212.00', '1311.40 80',
     'SIC,LSEN0+.32         (ext)'),
    ('022212.40', '1301.10 00',
     'B,SSW                 (ext) "-TO SSIP."'),
    ('022213.00', '22213.44 00',
     'BD,$+.32               bit 18 -> 022213.40'),
    ('022213.40', '22737.32 10',
     'LX,$X13,IC260        (ext) "-UPDATE CONTINUITY CHECK."'),
    ('022214.00', '24531.32 B0',
     'V+,$X13,BIT7          (ext) TEST 6 done = bit 7'),
    ('022214.40', '22737.33 10',
     'SX,$X13,IC260        (ext)'),
]

# The block must TILE 022062.00-022214.40 with no gap and no overlap.
# check_rows() reads each listed location on its own and would never
# notice a missing row, so the coverage is asserted here rather than
# counted by hand -- a four-token printed row is a full word, anything
# else a half-word.
_b = loc_bits('022062.00')
for _loc, _printed, _note in ROWS:
    assert loc_bits(_loc) == _b, f"row {_loc} should be at bit {_b}"
    _b += 64 if len(_printed.split()) == 4 else 32
assert _b == loc_bits('022214.40') + 32, f"block ends at bit {_b}"
print(f"TILING OK: {len(ROWS)} rows, "
      f"{(_b - loc_bits('022062.00')) // 32} half-words, "
      f"022062.00-022214.40")

# Only labels DEFINED inside the transcribed range belong here.  Of the
# three, I6098 and I6097 are evidence and I6096 is the anchor the
# SLC put there -- see the docstring.
SYMBOLS = {'I6096': '022062.00', 'I6097': '022072.00',
           'I6098': '022073.00'}

finish(check_rows(prog, ROWS, SYMBOLS, label='1260 T6 '))
