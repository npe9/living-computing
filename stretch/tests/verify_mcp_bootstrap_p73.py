"""MCP INITIALIZATION, printed p.73 -- SORT THE UNIT COUNT TABLE,
then the MULTI UNIT SCAN.

Fifty-six lines, forty-one of which compile, under FOUR boxed
headings -- the most on any page of the ASSIGN program.
decks/mcp_bootstrap_p73.strap carries the derivations.

>>> LINE 25 IS THE ADDRESS THE BOOT RUN'S TRAIL NOW NAMES. <<<
printed p.72 line 27 is "BB,T MULTI(T IXF),T A9D", and T A9D is
004275.40 = this page's line 25.  The run walks p.72's channel
status table and leaves it here.

A BUBBLE SORT, lines 8-18, two deep over the multi-unit count
table.  The two loops are named apart ONLY by their index fields:
line 16 is 004267.24 C8 (bits 19-22 = 1010 = T IXF) and line 18 is
004265.04 C8 (0010 = T IXH).

>>> THE INDEX FIELD CAUGHT A MISREAD STATEMENT. <<<  Line 2 read
"LVI,T IXF,T CHCUC" at 600 dpi.  Its code is 003661.05 01, whose
bits 19-22 are 0010 = $2 = T IXH.  At 1200 dpi the glyph is an H.
F and H are the hardest pair in the statement column at this size,
and eight rows on this page turn on it -- THE CODE COLUMN IS THE
AUTHORITY FOR AN INDEX NAME.

>>> M+1, AN OPERATION THE ASSEMBLER HAD AND NO PAGE HAD USED. <<<
Line 55 is "M+1,T CHCNT(T IXH)" -- add one to memory -- compiling
004000.22 B0 where p.72 line 26's plain "M+" is 010000.20 90.  The
arithmetic is exact: a VFL operation's low four bits are the byte's
high nibble and its high bits sit in bits 22-23 of the second
group.  M+1 is operation 43 = 0b101011, so the byte is 0xB0 and bit
22 carries the 32, printing ".22" where M+ (9) prints ".20" and *
(25) prints ".21".  Three operations one byte apart in the printed
column, all three agreeing with opcodes.VFL_INT_CODES unchanged.

TWO BYTES THE C/ZERO RULE DECIDED, IN OPPOSITE DIRECTIONS.  Line
33 prints "004306.C3 C1"; the octal pair cannot hold a C
(listing_typography.md 13e) so it is 004306.03 01, and p.72 line
32's twin "T A9BA LVI,T X1BR,T B9" = 004246.03 01 confirms both
glyphs.  But line 35 prints "C04322.74 CO" and line 42 prints
"C04246.34 C2": there the LOCATION's leading C is a zero while the
BYTES are real C's -- p.72 line 34's BZRZ is C0 and its line 18's
BRZ is C2.  One row, two fields, the rule read each way.

MEASURED INJECTIONS -- the observed sets, run through tests/inject.py.
The mutated file is the DECK, not the assembler.

  Line 55's M+1 becomes a plain M+ -- 1 FAIL at 004316.40, reading
  004000.20 90 for 004000.22 B0.  Both the byte and bit 22 move,
  which is the whole of what separates the two operations.
  Line 2's T IXH becomes the T IXF it was first read as -- 1 FAIL at
  004264.00, reading 003661.25 01 for 003661.05 01.  THIS IS THE
  MISREAD ITSELF, and the row that caught it.
  Line 18's outer CBH takes the inner loop's index -- 1 FAIL at
  004274.00, reading 004265.24 C8 for 004265.04 C8.  The sort would
  still have assembled; only the index field says which loop it is.
  Line 35's BZRZ becomes BRZ -- 1 FAIL at 004305.40, reading
  004322.74 C2 for 004322.74 C0.  The two bytes the C/zero rule had
  to tell apart, told apart.
  Line 44's offset 46 becomes 40 -- 1 FAIL at 004310.40, reading
  022024.20 D0 for 022027.20 D0.  The printed field is the offset
  halved (46 -> 0o27, 40 -> 0o24), so it scales with the operand.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p73.strap").read())

SYMBOLS = {
    # The address printed p.72 line 27 branches to.
    "TA9D":  "004275.40",
    # Labels this page defines and uses itself.
    "TD9A":  "004265.00",
    "TD9B":  "004267.00",
    "TD9C":  "004272.40",
    "TD9":   "004274.40",
    "TA9E":  "004300.00",
    "TA9F":  "004303.00",
    "TA9FA": "004304.00",
    "TA9G":  "004306.00",
    "TC9":   "004315.40",
}

ROWS = [
    ("004263.00", "003660.30 80  001000.36 F0",
     "line 1   CM1111(BU,1)"),
    ("004264.00", "003661.05 01",
     "line 2   LVI,T IXH"),
    ("004264.40", "003657.05 10",
     "line 3   SX,T FCHSC"),
    ("004265.00", "000022.24 10",
     "line 8   T D9A  LX"),
    ("004265.40", "004274.70 42",
     "line 9   BXCZ,T D9"),
    ("004266.00", "000000.00 82  040020.06 70",
     "line 10  LF(BU,32)"),
    ("004267.00", "000000.24 8A  004024.23 10",
     "line 11  T D9B  KF"),
    ("004270.00", "004272.77 40",
     "line 12  BZAH,T D9C"),
    ("004270.40", "000000.20 3A",
     "line 13  LV,T IXG"),
    ("004271.00", "000000.00 8A  040020.20 D0",
     "line 14  ST(BU,32)"),
    ("004272.00", "000011.21 30",
     "line 15  SV,T IXG,$R"),
    ("004272.40", "004267.24 C8",
     "line 16  T D9C  CBH"),
    ("004273.00", "000000.00 82  040020.20 D0",
     "line 17  ST(BU,32)"),
    ("004274.00", "004265.04 C8",
     "line 18  CBH,T IXH"),
    ("004274.40", "000000.24 1F",
     "line 20  T D9  LX"),
    ("004275.00", "003704.10 00",
     "line 21  B,T B1F"),
    ("004275.40", "000000.73 8A  004027.20 50",
     "line 25  T A9D  L"),
    ("004276.40", "000011.20 50",
     "line 26  LC,T IXG,$R"),
    ("004277.00", "004246.30 42",
     "line 27  BXCZ,T B9"),
    ("004277.40", "000000.20 3A",
     "line 28  LV,T UNTBA"),
    ("004300.00", "000000.31 8A  004303.34 02",
     "line 29  T A9E  BB"),
    ("004301.00", "000000.40 88  004304.34 02",
     "line 30  BB,T CHOWN"),
    ("004302.00", "000000.34 88  004315.74 00",
     "line 31  BZB,T UNAVL"),
    ("004303.00", "000000.35 88  004422.74 00",
     "line 32  T A9F  BZB"),
    ("004304.00", "004306.03 01",
     "line 33  T A9FA  LVI"),
    ("004304.40", "000000.76 88  002000.07 70",
     "line 34  CT0011(BU,2)"),
    ("004305.40", "004322.74 C0",
     "line 35  BZRZ,T C10"),
    ("004306.00", "004300.21 48",
     "line 36  T A9G  CB+"),
    ("004306.40", "000000.24 82  004000.06 70",
     "line 41  LF,T CHCNT"),
    ("004307.40", "004246.34 C2",
     "line 42  BRZ,T B9"),
    ("004310.00", "000011.25 30",
     "line 43  SV,T IXF,$R"),
    ("004310.40", "000000.00 82  022027.20 D0",
     "line 44  ST,T CHADD"),
    ("004311.40", "000000.45 05",
     "line 45  V+I,T IXH"),
    ("004312.00", "000001.05 00",
     "line 46  C+I,T IXH"),
    ("004312.40", "003273.00 80  022000.23 10",
     "line 47  KF,T LUCT"),
    ("004313.40", "004246.37 40",
     "line 48  BZAH,T B9"),
    ("004314.00", "003273.00 80  022000.20 D0",
     "line 49  ST,T LUCT"),
    ("004315.00", "004246.10 00",
     "line 50  B,T B9"),
    ("004315.40", "000000.64 8A  004306.34 00",
     "line 54  T C9  BZB"),
    ("004316.40", "000000.24 82  004000.22 B0",
     "line 55  M+1,T CHCNT"),
    ("004317.40", "004306.10 00",
     "line 56  B,T A9G"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.73 ")
finish(fails)
