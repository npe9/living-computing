#!/usr/bin/env python3
"""verify_mcp_bootstrap_p45.py -- THE BREAKDOWN ROUTINE, printed page
45 (../decks/mcp_bootstrap_p45.strap).
docs/MCP_Mar63_001-249.pdf PDF p.52, header "PAGE NUMBER 45".
AGENTS.md rule 3.

Forty-three printed rows with binary output and eleven symbol
locations.

>>> LINE 10 IS S BRK8, AT 002502.00 -- THE ADDRESS THE BOOT RUN HAS
BEEN STOPPING AT. <<<

printed p.38 line 17 is "BD,S BRK8" and its binary put S BRK8 at
002502.00, seven pages before this one was opened.  With pp.43 and 44
in the image the PC trail reached half-word 2692, which is that
address, and stopped on a zero.  This page fills it.

AND THE PAGE IS SIGNED: lines 6-7 read "-SBRK8,  6 BIT BCD VERSION,
16 BITS BETWEEN FIELDS.        LARRY LEVY", the first author's name
this project has transcribed out of the MCP listing.

THREE SYMBOLS ARE INDEX REGISTERS, AND LINE 19 IS THE ROW THAT PROVED
IT.  printed p.46 lines 22-24 define "QX INN SYN,$1", "QX OUT SYN,$2",
"QX CF9 SYN,$3", and this page uses them as a J field (line 10) AND as
an index (line 19).  C22-6531 printed p.31: "the meaning of the newly
defined symbol A is that whenever A is written in the program, the
effect is the same as if Y had been written.  THE MEANING OF SYN IS
ALWAYS ONE OF EXACT SUBSTITUTION."  "$1" was already context-dependent
in strap_asm -- register 1 in an I or J field, bit address 000021.00
in an address field -- and storing a SYN's VALUE loses that:
000021.00 in a four-bit field is 0.  Line 19 prints 81 and the old
assembler gave 80.

A dds TRAVELS THROUGH A SYN TOO.  Lines 20 and 22 are "KF,Q CMA" and
"KF,Q BLNK" with no data description written, and both print 006600 --
length 6, byte size 6, the table character's properties.  Same
sentence of p.31: "data properties (dds) associated with Y ... are
TRANSFERRED to A."  strap_asm had been accepting a dds on a SYN and
silently dropping it; these two rows are the check that it no longer
does.

THREE MORE SWAPs, ON THE ERROR PATH.  Lines 47-49 are
"SWAPI,1,QX INN,Q SAV1" and its two fellows, under Q 2BIG, which line
24's "CBRZ,QX CF9,Q 2BIG" reaches when a card field is longer than its
output slot.  SWAP now has six documented callers: two on printed
p.40, one on p.43, three here.

LINE 30 IS listing_typography.md 13 IN A NEW SHAPE.  At 900 dpi the
row prints "3C* C02520.00   C02516.50 C0" -- THREE separate zeros come
out as C in ONE row, in the line number, the location and the trailing
byte -- so this is a per-ROW artifact, not the per-glyph one 13 has
recorded until now.  The byte is 00: printed p.43 line 50's "B,Q CHK"
prints 002454.10 00 for the same shape, and 1100 is the conditional
branch line 21 prints as C2.

THREE INJECTIONS, OBSERVED FAILURE SETS WRITTEN DOWN:

  "QX INN SYN,$1" -> "SYN,(8)21.0", the address instead of the
  register -- 7 FAILs: lines 10, 13, 14, 19, 26, 39 and 41.  Lines
  47-49 do NOT fail, and that is right: a SWAPI's first half word
  carries the index register's ADDRESS, which is 000021.00 either
  way.
  "Q CMA SYN(BU,6,6)" -> "SYN" -- 1 FAIL, line 20, and Q BLNK's
  line 22 still passes because it keeps its own dds.
  "TI,2" -> "TI,3" -- 2 FAILs: line 50's row and the extent check.

THE PAGE STATES ITS OWN TRANSMIT EXTENT.  Line 50's "TI,2,$L,Q SAV4"
prints a count of 2 in its J field and Q SAV4 is 002552.00, two words
below Q SAV6 at 002554.00 -- so the transmit fills the gap exactly.  A
count of one would leave 002553 unwritten and a count of three would
overwrite Q SAV6.  Checked below in its own check, because the count
and the two addresses come from three different rows.
"""
from listing_oracle import check_rows, finish, loc_bits, read_bits
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p45.strap").read())

SYMBOLS = {
    # THE ONE THE WHOLE PAGE IS FOR.
    "SBRK8": "002502.00",
    "QNEXT": "002507.40",
    "QSTEP": "002515.00",
    "QBL":   "002516.40",
    "QIFC":  "002520.40",
    "QZERO": "002522.00",
    "QREDY": "002523.40",
    "QRSTR": "002526.00",
    "Q2BIG": "002530.00",
    # Two of the fourteen stand-ins, the pair the TI extent check
    # below reads.  The rest are checked by the rows that use them.
    "QSAV4": "002552.00",
    "QSAV6": "002554.00",
}

ROWS = [
    ("002502.00", "002547.03 10", "line 10  S BRK8  SX,QX INN,Q SAV1  -SAVE INDEX REGISTERS"),
    ("002502.40", "002550.05 10", "line 11  SX,QX OUT,Q SAV2"),
    ("002503.00", "002551.07 10", "line 12  SX,QX CF9,Q SAV3"),
    ("002503.40", "000000.02 3F", "line 13  LV,QX INN,0.($15)  -INITIALIZE IN"),
    ("002504.00", "000000.42 5F", "line 14  LC,QX INN,.32($15)  -INITIALIZE N"),
    ("002504.40", "000001.04 3F", "line 15  LV,QX OUT,1.($15)  -INITIALIZE OUT"),
    ("002505.00", "002555.06 10", "line 16  LX,QX CF9,QW CF9  -COUNT CHARS IN STORED"),
    ("002505.40", "000001.40 8F  022000.00 F0",
     "line 17  CM0000(BU,18,8),1.32($15)  -INITIALIZE FIELD COUNT"),
    # "18+Q KSIZ" IS AN EXPRESSION IN THE LENGTH FIELD, and 030040
    # carries the 24 it comes to.
    ("002506.40", "002556.37 80  030040.20 50", "line 18  L(BU,18+QKSIZ),QCOUNT,64"),
    # >>> THE ROW THAT PROVED THE INDEX-REGISTER SYN.  81, not 80.
    ("002507.40", "000000.06 81  106000.06 70",
     "line 19  Q NEXT  LF(V+I)(BU,Q KSIZ),Q KSIZ(QX INN)  -LOAD INPUT CHAR. STEP X"),
    # >>> AND THE TWO THAT PROVED THE dds TRAVELS.  006600 is a
    # length of 6 and a byte size of 6, written nowhere on the row.
    ("002510.40", "002556.31 80  006600.23 10", "line 20  KF,Q CMA  -IS THIS A COMMA"),
    ("002511.40", "002520.76 C2", "line 21  BAE,Q IF C"),
    ("002512.00", "002556.61 80  006600.23 10", "line 22  KF,Q BLNK  -IS THIS A BLANK"),
    ("002513.00", "002515.36 C2", "line 23  BAE,Q STEP"),
    ("002513.40", "002530.06 4E", "line 24  CBRZ,QX CF9,Q 2BIG  -TEST FOR OVERSIZED FIELD"),
    ("002514.00", "000000.06 82  106000.12 F0",
     "line 25  SF(V+I)(BU,Q KSIZ),Q KSIZ(QX OUT)  -STORE CHAR. STEP X"),
    ("002515.00", "002507.42 48", "line 26  Q STEP  CB,QX INN,Q NEXT  -TEST FOR LAST INPUT CHAR"),
    ("002515.40", "000001.40 8F  022000.22 B0",
     "line 27  M+1(BU,18),1.32($15)  -COUNT LAST FIELD"),
    ("002516.40", "002526.06 4A", "line 28  Q BL  CBZ,QX CF9,Q RSTR  -STORE R.H. BLANKS"),
    ("002517.00", "000000.06 82  106040.12 F0",
     "line 29  SF(V+I)(BU,Q KSIZ),Q KSIZ(QX OUT),64  -IF NECESSARY"),
    # listing_typography.md 13, THREE ZEROS IN ONE ROW.
    ("002520.00", "002516.50 00", "line 30  B,Q BL"),
    ("002520.40", "000001.40 8F  022000.22 B0",
     "line 32  Q IF C  M+1(BU,18),1.32($15)  -COUNT THIS FIELD"),
    ("002521.40", "002523.46 4E", "line 33  CBRZ,QX CF9,Q REDY  -TEST FOR SHORT INPUT FIELD"),
    ("002522.00", "000000.06 82  106040.12 F0",
     "line 34  Q ZERO  SF(V+I)(BU,Q KSIZ),Q KSIZ(QX OUT),64  -STORE R.H. BLANKS"),
    ("002523.00", "002522.06 4C", "line 35  CBR,QX CF9,Q ZERO"),
    ("002523.40", "002556.04 B0", "line 36  Q REDY  V+,QX OUT,Q SKIP  -SKIP TO BEG OF NEXT OUTPUT"),
    ("002524.00", "000001.40 8F  022043.23 10", "line 37  KF(BU,18),1.32($15),64+QKSIZ"),
    ("002525.00", "002526.37 40", "line 38  BZAH,QRSTR"),
    ("002525.40", "002507.42 48", "line 39  CB,QX INN,Q NEXT  -TEST FOR LAST INPUT CHAR"),
    ("002526.00", "002547.02 10", "line 41  Q RSTR  LX,QX INN,Q SAV1  -RESTORE INDEX REGISTERS"),
    ("002526.40", "002550.04 10", "line 42  LX,QX OUT,Q SAV2"),
    ("002527.00", "002551.06 10", "line 43  LX,QX CF9,Q SAV3"),
    ("002527.40", "000002.50 0F", "line 44  B,2.32($15)  -NORMAL RETURN"),
    ("002530.00", "000001.40 8F  022000.22 B0",
     "line 46  Q 2BIG  M+1(BU,18),1.32($15)  -COUNT THIS FIELD"),
    # >>> THE THREE SWAPs, on the oversized-field path.
    ("002531.00", "000021.00 80  002547.02 E0",
     "line 47  SWAPI,1,QX INN,Q SAV1  -RESTORE INDEXES BUT SAVE"),
    ("002532.00", "000022.00 80  002550.02 E0",
     "line 48  SWAPI,1,QX OUT,Q SAV2  -  PRESENT VALUES"),
    ("002533.00", "000023.00 80  002551.02 E0",
     "line 49  SWAPI,1,QX CF9,Q SAV3  -  AT QBRK8"),
    ("002534.00", "000010.00 80  002552.04 A0", "line 50  TI,2,$L,Q SAV4  -SAVE $L AND $R"),
    ("002535.00", "002554.37 10", "line 51  SX,$15,Q SAV6"),
    ("002535.40", "000002.10 0F", "line 52  B,2.($15)  -ERROR RETURN"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.45 ")

# ---------------------------------------------------------------------
# LINE 50'S TRANSMIT FILLS THE GAP BETWEEN Q SAV4 AND Q SAV6 EXACTLY.
#
# The count and the two addresses come from three different rows, so
# nothing above compares them with each other.  A count of one would
# leave 002553 unwritten -- printed p.46 line 20 names it "-STORE $R"
# -- and a count of three would overwrite Q SAV6.
#
# The count is the J field of the TRANSMIT's second half word, bits
# 51-54 of the instruction (Reference Manual printed p.30, "the field
# J, bits 51-54").
# ---------------------------------------------------------------------
count = read_bits(prog, loc_bits("002534.00") + 51, 4)
span = (loc_bits("002554.00") - loc_bits("002552.00")) // 64
if count == span == 2:
    print(f"PASS MCP p.45 line 50's TI count {count} fills Q SAV4..Q SAV6 "
          f"exactly, {span} words")
else:
    print(f"FAIL MCP p.45 line 50's TI count is {count} and the gap from "
          f"Q SAV4 to Q SAV6 is {span} words")
    fails += 1

finish(fails)
