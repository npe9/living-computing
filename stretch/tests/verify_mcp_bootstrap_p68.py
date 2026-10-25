"""MCP INITIALIZATION, printed p.68 -- THE UNIT AVAILABILITY TESTS
AND THE MULTI-UNIT CHANNEL SCAN.

Fifty-six lines, forty-one of which compile.
decks/mcp_bootstrap_p68.strap carries the derivations.

IT PLACES THREE OF printed p.67's FOUR FORWARD REFERENCES: line 7 is
T B7 at 004034.00, line 12 is T A7D at 004035.00 and line 30 is T A3
at 004046.00.  The fourth, T C3Z, is one word past this page's last
line and belongs to printed p.69.

>>> TWO EIGHT-LINE BLOCKS THAT DIFFER ONLY IN THEIR INDEX. <<<
Lines 1-8 and 16-23 are the same test written twice -- once on T X3
and once on T IXJ -- and the binary differs in ONE NIBBLE per row,
the index in the opcode byte: 82 against 86, which is $2 against $6.
Every other field is identical.  That is a transcription check the
page provides itself: a misread digit in either block disagrees with
the other.

"$R+.32" IS AN EXPRESSION ON A SYSTEM SYMBOL.  Line 38's
"KC,T X3,$R+.32" compiles 000011.45 90 -- $R is word 9 and ".45" has
bit 18 SET, the half-word selector, so the operand is word 9's
second half, where line 37's "LC,T IXJ,$R" put the count.

ALL FORTY-ONE ROWS AND ALL EIGHT SYMBOLS PASSED ON THE FIRST RUN.

MEASURED INJECTIONS -- the observed sets, run through tests/inject.py.

  T UNRES 0.62 -> 0.61 -- 4 FAIL, TWO IN EACH TWIN BLOCK (lines 3
  and 6, lines 18 and 21).  That is the twin structure demonstrated:
  one symbol, two blocks, the same two rows in each.
  T IXJ $6 -> $7 -- 6 FAIL, all of them in the SECOND block and in
  rows that carry the index.  The first block is untouched, which is
  what makes the pair a check rather than a duplication.
  Line 38's "$R+.32" loses its half word -- 1 FAIL, reading
  000011.05 for 000011.45.  Bit 18 is the half-word selector, so the
  operand moves from word 9's second half to its first.
  T CHCNT 0.20 -> 0.21 -- 1 FAIL, line 36.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p68.strap").read())

SYMBOLS = {
    # printed p.67's three stand-ins, placed here.
    "TB7":    "004034.00",
    "TA7D":   "004035.00",
    "TA3":    "004046.00",
    # Labels this page defines and uses itself.
    "TA7CA":  "004037.40",
    "TC7":    "004045.00",
    "TA3D":   "004047.00",
    "TA3C":   "004056.40",
    "TA3CA":  "004060.40",
}

ROWS = [
    ("004026.40", "000000.34 82  004034.34 02",
     "line 1   BB,T UNAVL"),
    ("004027.40", "000000.35 82  004034.34 00",
     "line 2   BZB,T UNASG"),
    ("004030.40", "000000.76 82  002000.07 70",
     "line 3   CT0011(BU,2)"),
    ("004031.40", "004167.74 C2",
     "line 4   BRZ,T A5S"),
    ("004032.00", "003273.23 80  004034.34 00",
     "line 5   BZB,T MODE"),
    ("004033.00", "000000.76 82  004167.74 00",
     "line 6   BZB,T UNRES"),
    ("004034.00", "004021.05 48",
     "line 7   T B7  CB+"),
    ("004034.40", "003756.50 00",
     "line 8   B,T B2"),
    ("004035.00", "000000.14 32",
     "line 12  T A7D  LV"),
    ("004035.40", "000000.73 82  004027.20 50",
     "line 13  L,T UNITK,46"),
    ("004036.40", "000011.14 50",
     "line 14  LC,T IXJ,$R"),
    ("004037.00", "004034.30 42",
     "line 15  BXCZ,T B7"),
    ("004037.40", "000000.34 86  004045.34 02",
     "line 16  T A7CA  BB"),
    ("004040.40", "000000.35 86  004045.34 00",
     "line 17  BZB,T UNASG"),
    ("004041.40", "000000.76 86  002000.07 70",
     "line 18  CT0011(BU,2)"),
    ("004042.40", "004137.34 C2",
     "line 19  BRZ,T A5A"),
    ("004043.00", "003273.23 80  004045.34 00",
     "line 20  BZB,T MODE"),
    ("004044.00", "000000.76 86  004137.34 00",
     "line 21  BZB,T UNRES"),
    ("004045.00", "004037.55 48",
     "line 22  T C7  CB+"),
    ("004045.40", "004034.10 00",
     "line 23  B,T B7"),
    ("004046.00", "000000.12 19",
     "line 30  T A3  LX"),
    ("004046.40", "003756.70 42",
     "line 31  BXCZ,T B2"),
    ("004047.00", "000000.14 55",
     "line 32  T A3D  LC"),
    ("004047.40", "000022.15 50",
     "line 33  SC,T IXJ,T X3"),
    ("004050.00", "000000.14 32",
     "line 34  LV,T IXJ"),
    ("004050.40", "000000.73 82  004027.20 50",
     "line 35  L,T UNITK,46"),
    ("004051.40", "000000.24 85  004007.06 70",
     "line 36  LF,T CHCNT,14"),
    ("004052.40", "000011.14 50",
     "line 37  LC,T IXJ,$R"),
    ("004053.00", "000011.45 90",
     "line 38  KC,T X3,$R+.32"),
    ("004053.40", "000000.13 84  007000.06 70",
     "line 39  LF,T RLSYM"),
    ("004054.40", "004065.34 C2",
     "line 40  BRZ,T C3Z"),
    ("004055.00", "004056.73 40",
     "line 41  BZXH,T A3C"),
    ("004055.40", "003273.25 80  004132.34 00",
     "line 42  BZB,T INDB"),
    ("004056.40", "003273.24 80  004065.34 02",
     "line 46  T A3C  BB"),
    ("004057.40", "003271.24 10",
     "line 47  LX,T IXK"),
    ("004060.00", "000011.05 30",
     "line 48  SV,T X3,$R"),
    ("004060.40", "000000.56 8A  022027.23 10",
     "line 49  T A3CA  KF"),
    ("004061.40", "004064.76 C0",
     "line 50  BZAE,T A3CB"),
    ("004062.00", "000000.13 8A  007000.06 70",
     "line 54  LF,T RLSYM"),
    ("004063.00", "000000.13 84  007000.23 10",
     "line 55  KF,T RLSYM"),
    ("004064.00", "004132.36 C0",
     "line 56  BZAE,T A3F1"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.68 ")
finish(fails)
