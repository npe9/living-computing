"""MCP INITIALIZATION, printed p.70 -- MULTI-UNIT ASSIGNMENT, AND THE
UNLOAD PATH.

Fifty-six lines, thirty-eight of which compile.
decks/mcp_bootstrap_p70.strap carries the derivations.

IT PLACES THREE STAND-INS FROM TWO EARLIER PAGES: T A3F1 (p.68),
T A5A and T A5MA (p.69).

>>> TWO MORE BARE WRITTEN MINUSES -- THE CORPUS GOES FROM TWO TO
FOUR ON ONE PAGE. <<<  Lines 37 and 40 are "-(BU,18),T CHSXW,46"
and "- (BU,4),T IXJ+0.42,46", the second with a space after the
minus.  Before printed p.69 this project had exactly ONE in the
whole corpus (MCP printed p.18 line 35, the row that found every
unsigned subtract in the model was an addition); p.69 made it two.

AND THE MODIFIER IS VISIBLE IN BOTH, against a plain row two lines
away each time:

    line 36  ST,T ABSCH(T IXA),46   022027.20 D0
    line 37  -(BU,18),T CHSXW,46    022027.30 10
    line 39  L,T UNITK(T X3),46     004027.20 50
    line 40  - (BU,4),T IXJ+0.42,46 004027.30 10

printed p.69's STATI IS CONFIRMED FROM A SECOND ROW.  That page's
line 24 gave STATI = 0.26 with dds (BU,1), both read off one row --
the only symbol there that is not a "T" name.  Line 45 here is
"BB,STATI(T IXJ),T A5LC" compiling 000000.32 86, and 0o32 is 26.

TWO NEW MNEMONICS, both written as printed: line 12's CBH (byte C8)
and line 19's BBN (byte 0A).

ALL THIRTY-EIGHT ROWS AND ALL EIGHT SYMBOLS PASSED ON THE FIRST RUN.

MEASURED INJECTIONS -- the observed sets, run through tests/inject.py.

  Line 37's minus becomes a plus -- 1 FAIL, 022027.20 for
  022027.30.
  Line 40's minus becomes a plus -- 1 FAIL, 004027.20 for
  004027.30.
  Those two, with p.69's, are THREE SEPARATE ROWS whose only
  distinguishing bit is the negative-sign modifier.  Before
  2026-10-19 all three would have compiled an ADDITION and nothing
  in the suite would have noticed.
  STATI 0.26 -> 0.27 -- 1 FAIL, line 45.  That symbol was derived
  from ONE row on printed p.69 and this is the row that checks it.
  T COT (8)5002.0 -> (8)5003.0 -- 3 FAIL, lines 38, 42 and 50.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p70.strap").read())

SYMBOLS = {
    # Stand-ins from printed pp.68 and 69, placed here.
    "TB3":    "004127.00",
    "TA3F1":  "004132.00",
    "TA5A":   "004137.00",
    "TA5MA":  "004142.40",
    # Labels this page defines and uses itself.
    "TABBN":  "004135.40",
    "TA5M1":  "004141.40",
    "TA5LC":  "004157.40",
    "TIPL3":  "004164.40",
}

ROWS = [
    ("004127.00", "004066.15 48",
     "line 5   T B3  CB+"),
    ("004127.40", "003273.26 80  004132.34 04",
     "line 6   BZBZ,T INDC"),
    ("004130.40", "003273.27 80  001000.36 F0",
     "line 7   CM1111,T INDD"),
    ("004131.40", "004065.50 00",
     "line 8   B,T C3"),
    ("004132.00", "000025.12 10",
     "line 10  T A3F1  LX"),
    ("004132.40", "003756.70 42",
     "line 11  BXCZ,T B2"),
    ("004133.00", "004047.12 C8",
     "line 12  CBH,T A3D"),
    ("004133.40", "003273.23 80  004135.74 02",
     "line 16  BB,T MODE"),
    ("004134.40", "003315.06 90",
     "line 17  KV,T PPRUN"),
    ("004135.00", "003756.72 C0",
     "line 18  BZXE,T B2"),
    ("004135.40", "003273.24 80  003756.74 0A",
     "line 19  T ABBN  BBN"),
    ("004136.40", "004046.10 00",
     "line 20  B,T A3"),
    ("004137.00", "000000.24 1F",
     "line 28  T A5A  LX"),
    ("004137.40", "004141.63 40",
     "line 29  BZXF,T A5M1"),
    ("004140.00", "000000.76 86  001000.36 F0",
     "line 31  CM1111,T UNRES"),
    ("004141.00", "004142.50 00",
     "line 32  B,T A5MA"),
    ("004141.40", "000000.77 86  001000.36 F0",
     "line 33  T A5M1  CM1111"),
    ("004142.40", "000000.00 84  004420.74 0E",
     "line 34  T A5MA  BB1"),
    ("004143.40", "000011.05 30",
     "line 35  SV,T X3,$R"),
    ("004144.00", "000000.56 84  022027.20 D0",
     "line 36  ST,T ABSCH"),
    ("004145.00", "002152.00 80  022027.30 10",
     "line 37  -(BU,18)"),
    ("004146.00", "005002.14 80  007027.20 D0",
     "line 38  ST(BU,7)"),
    ("004147.00", "000000.73 82  004027.20 50",
     "line 39  L,T UNITK"),
    ("004150.00", "000026.52 80  004027.30 10",
     "line 40  - (BU,4)"),
    ("004151.00", "000000.07 84  003027.20 D0",
     "line 41  ST,T ABSUN"),
    ("004152.00", "005002.57 80  003027.20 D0",
     "line 42  ST(BU,3)"),
    ("004153.00", "000000.03 84  003745.34 00",
     "line 43  BZB,T TYPE"),
    ("004154.00", "000000.33 86  003745.34 02",
     "line 44  BB,T FDISP"),
    ("004155.00", "000000.32 86  004157.74 02",
     "line 45  BB,STATI"),
    ("004156.00", "000000.34 84  022000.07 70",
     "line 46  CT0011,T FREEL"),
    ("004157.00", "003745.34 C2",
     "line 47  BRZ,T A2A"),
    ("004157.40", "005002.13 02",
     "line 50  T A5LC  LCI"),
    ("004160.00", "000000.13 56",
     "line 51  SC,T IXB"),
    ("004160.40", "000000.40 86  001000.36 F0",
     "line 52  CM1111,T CHOWN"),
    ("004161.40", "000000.35 86  001000.00 F0",
     "line 53  CM0000,T UNASG"),
    ("004162.40", "000000.65 86  001000.00 F0",
     "line 54  CM0000,SIMNT"),
    ("004163.40", "000000.63 86  001000.00 F0",
     "line 55  CM0000,SMOUNT"),
    ("004164.40", "001472.10 00",
     "line 56  T IPL3  B,DMCP"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.70 ")
finish(fails)
