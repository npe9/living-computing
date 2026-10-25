"""MCP INITIALIZATION, printed p.71 -- SINGLE UNIT ASSIGNMENT, AND
THE ALL-UNITS-ASSIGNED CHECK.

Fifty-six lines, thirty-six of which compile.
decks/mcp_bootstrap_p71.strap carries the derivations.

>>> THIS PAGE CLOSES THE RANGE ON T ASIGN'S FORWARD BRANCH. <<<
Line 52 is "B,T A1" at 004214.40, one half word, ending at
004215.00 -- which is printed p.72 line 4, and 004215.00 is T A9,
the address printed p.65 line 9 branches to and the boot run's PC
trail has named ever since.

IT ALSO PLACES FIVE STAND-INS: T A5S (printed p.68), and T A8,
T B8C, T B8Z and T B8 (all printed p.66).

LINES 1 AND 2 ARE STATEMENTS WITH NO OPERATION -- ",DFREE" and
",9." -- the parameter block of printed p.70 line 56's "B,DMCP",
straddling the page break.  A null operation compiles a half word
and both rows print one.  "9." is nine WORDS and nine in octal is
11.

LINE 26 IS A listing_typography.md 13d ROW.  At 1800 dpi it prints
C0C024.02 C0, and the SIX-DIGIT OCTAL field contains two of those C
glyphs -- octal has no C, so the drum dropped the left stroke on
every zero in the row.  The opcode's first glyph has the same shape,
so the row is 000024.02 00, which is what printed p.66 line 4's
"R,T X1" (000032.02 00) independently says.

ALL THIRTY-SIX ROWS AND ALL ELEVEN SYMBOLS PASSED ON THE FIRST RUN.

MEASURED INJECTIONS -- the observed sets, run through tests/inject.py.

  Line 2's "9." loses its dot -- 1 FAIL, reading 000000.11 for
  000011.00.  The dot moves nine from the BIT field to the WORD
  field and the printed pair shows it in both halves at once.
  T LOOP1 +1 bit -- 2 FAIL, lines 39 and 51, the two rows that
  bump it.
  T H (8)4420.0 -> (8)4421.0 -- 1 FAIL, line 15.  One word on is
  T K, so this injection moves one forward reference onto another.
  T SAV (8)3272.0 -> (8)3273.0 -- 1 FAIL, line 43.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p71.strap").read())

SYMBOLS = {
    # Stand-ins from printed pp.66 and 68, placed here.
    "TA5S":  "004167.40",
    "TA8":   "004176.00",
    "TB8C":  "004201.40",
    "TB8Z":  "004203.40",
    "TB8":   "004211.40",
    # Labels this page defines and uses itself.
    "TA5Z":  "004172.00",
    "TA5SA": "004173.00",
    "TA8A":  "004176.40",
    "TA8BB": "004200.00",
    "TB8A":  "004205.40",
    "TA8B":  "004210.40",
}

ROWS = [
    ("004165.00", "000000.00 80",
     "line 1   ,DFREE"),
    ("004165.40", "000011.00 80",
     "line 2   ,9."),
    ("004166.00", "000000.40 86  001000.00 F0",
     "line 3   CM0000,T CHOWN"),
    ("004167.00", "003745.10 00",
     "line 4   B,T A2A"),
    ("004167.40", "000000.24 1F",
     "line 10  T A5S  LX"),
    ("004170.00", "004172.23 42",
     "line 11  BXF,T A5Z"),
    ("004170.40", "000000.77 82  001000.36 F0",
     "line 12  CM1111,T OVRES"),
    ("004171.40", "004173.10 00",
     "line 13  B,T A5SA"),
    ("004172.00", "000000.76 82  001000.36 F0",
     "line 14  T A5Z  CM1111"),
    ("004173.00", "000000.00 84  004420.34 0E",
     "line 15  T A5SA  BB1"),
    ("004174.00", "000011.05 30",
     "line 16  SV,T X3,$R"),
    ("004174.40", "000000.56 84  022027.20 D0",
     "line 17  ST,T ABSCH"),
    ("004175.40", "003756.50 00",
     "line 18  B,T B2"),
    ("004176.00", "000024.02 00",
     "line 26  T A8  R,T IXA"),
    ("004176.40", "000000.22 84  004200.34 00",
     "line 27  T A8A  BZB"),
    ("004177.40", "003373.11 01",
     "line 28  LVI,T IOREQ"),
    ("004200.00", "000000.00 84  004210.74 00",
     "line 29  T A8BB  BZB"),
    ("004201.00", "004176.51 48",
     "line 30  CB+,T A8A"),
    ("004201.40", "000000.46 83  001000.36 F0",
     "line 33  T B8C  CM1111"),
    ("004202.40", "000000.24 1F",
     "line 34  LX,T CTWDX"),
    ("004203.00", "004421.23 42",
     "line 35  BXF,T K"),
    ("004203.40", "000002.07 07",
     "line 37  T B8Z  V+ICR"),
    ("004204.00", "004205.70 40",
     "line 38  BZXCZ,T B8A"),
    ("004204.40", "003273.33 80  001000.22 B0",
     "line 39  M+1,T LOOP1"),
    ("004205.40", "003273.30 80  003710.34 02",
     "line 40  T B8A  BB"),
    ("004206.40", "000000.24 1F",
     "line 41  LX,T CTWDX"),
    ("004207.00", "003710.23 42",
     "line 42  BXF,T A1"),
    ("004207.40", "003272.07 10",
     "line 43  SX,T IXE,T SAV"),
    ("004210.00", "003710.10 00",
     "line 44  B,T A1"),
    ("004210.40", "000000.24 1F",
     "line 46  T A8B  LX"),
    ("004211.00", "004360.23 42",
     "line 47  BXF,T AREJX"),
    ("004211.40", "000002.07 07",
     "line 48  T B8  V+ICR"),
    ("004212.00", "003273.30 80  001000.36 F0",
     "line 49  CM1111,T INDE"),
    ("004213.00", "003710.30 40",
     "line 50  BZXCZ,T A1"),
    ("004213.40", "003273.33 80  001000.22 B0",
     "line 51  M+1,T LOOP1"),
    ("004214.40", "003710.10 00",
     "line 52  B,T A1"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.71 ")
finish(fails)
