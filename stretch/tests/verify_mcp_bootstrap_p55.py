"""MCP INITIALIZATION, printed p.55 -- THE CHANNEL SYMBOL TABLE SEARCH.

Forty-four lines and all forty-four compile.
decks/mcp_bootstrap_p55.strap carries the derivations.

>>> THIS PAGE CLOSES THE GAP. <<<  printed p.54's line 56 ends at
003105.40, which is line 1 here, and line 44 ends at 003147.40, which
is printed p.56 line 5.  pp.54-58 are now contiguous to the bit,
which is what strap/prosa.py requires before the image may hold them.

LINE 12 IS A HALT, the third this project has transcribed: "BD,$" at
003116.40, commented "-INTERNAL CHANNEL TABLE EXCEEDED".

L BLANK APPEARS BARE ON p.56 AND WITH ITS dds HERE, and the two rows
differ by exactly the byte size: line 18's "K(BU,48),L BLANK" is
060000.21 10 and p.56 line 11's "K,L BLANK" is 060600.21 10.  Same
symbol, same operation, one page apart -- the cleanest instance of
C22-6531 printed p.31's dds rule this project has.

ALL FORTY-FOUR ROWS PASSED ONCE LINE 40'S OPCODE BYTE WAS CORRECTED
FROM 80 TO B0 -- see the deck header: 900 dpi got that B/8 pair wrong
and 1800 dpi plus five already-transcribed "V+" rows settled it.

MEASURED INJECTIONS -- the observed sets, run through tests/inject.py.

  L SYMC (8)2660.0 -> (8)2661.0 -- 3 FAIL, lines 14, 22 and 32.  The
  third is the sharp one: line 32 writes "L SYMC-1." and fails
  reading 002660 for 002657, so the expression moves with the symbol.
  T RLSYM 0.11 -> 0.12 -- 2 FAIL, lines 20 and 27.
  L XSC $8 -> $7 -- 6 FAIL (lines 6, 7, 11, 13, 14, 15 and on), in
  the J field, the opcode byte and a branch target alike.
  Line 30's "-.8" loses its sign -- 1 FAIL, reading 002607.10 for
  002606.70: eight bits back from L RLCT crosses into the previous
  word, so the sign changes both halves of the printed address.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p55.strap").read())

SYMBOLS = {
    "LOOPSC": "003113.00",
    "LIOD4":  "003117.00",
    "LCHAN":  "003120.00",
    "LENTER": "003130.40",
    # printed p.54 SYNs L SET; this page places it.
    "LSET":   "003137.40",
    "LSETA":  "003142.40",
}

ROWS = [
    ("003105.40", "002601.31 80  007000.20 50",
     "line 1   L,L TAPEC"),
    ("003106.40", "000000.62 87  007000.20 D0",
     "line 2   ST(BU,7)"),
    ("003107.40", "002601.31 80  007000.22 B0",
     "line 3   M+1,L TAPEC"),
    ("003110.40", "002733.74 80  004000.20 50",
     "line 4   L(BU,4)"),
    ("003111.40", "000000.03 85  004000.20 D0",
     "line 5   ST(BU,4),T TYPE"),
    ("003112.40", "002566.20 10",
     "line 6   LX,L XSC"),
    ("003113.00", "000000.00 88  060000.20 50",
     "line 7   L OOPSC L(BU,48)"),
    ("003114.00", "003117.34 C6",
     "line 8   BRZZ,L IOD4"),
    ("003114.40", "000004.00 83  060000.21 10",
     "line 9   K(BU,48)"),
    ("003115.40", "003120.36 C6",
     "line 10  BAEZ,L CHAN"),
    ("003116.00", "003113.21 48",
     "line 11  CB+"),
    ("003116.40", "003116.44 00",
     "line 12  BD,$"),
    ("003117.00", "000004.00 83  000000.02 A8",
     "line 13  L IOD4  TI,1"),
    ("003120.00", "002660.21 0D",
     "line 14  L CHAN  V-I"),
    ("003120.40", "000011.21 30",
     "line 15  SV"),
    ("003121.00", "000000.71 87  007027.20 D0",
     "line 16  ST(BU,7)"),
    ("003122.00", "000004.00 83  060000.20 50",
     "line 17  L(BU,48)"),
    ("003123.00", "002736.00 80  060000.21 10",
     "line 18  K(BU,48),L BLANK"),
    ("003124.00", "003130.76 C4",
     "line 19  BZAEZ,L ENTER"),
    ("003124.40", "000000.13 85  007000.00 F0",
     "line 20  CM0000(BU,7)"),
    ("003125.40", "000000.60 87  001000.36 F0",
     "line 21  CM1111(BU,1)"),
    ("003126.40", "002660.21 05",
     "line 22  V+I"),
    ("003127.00", "000000.00 88  000000.00 F0",
     "line 23  CM0000(BU,64)"),
    ("003130.00", "003055.50 00",
     "line 24  B,L FOUND"),
    ("003130.40", "000001.21 05",
     "line 25  L ENTER V+I"),
    ("003131.00", "000030.13 80  007000.20 50",
     "line 26  L(BU,7),L XSC+.11"),
    ("003132.00", "000000.13 85  007000.20 D0",
     "line 27  ST(BU,7),T RLSYM"),
    ("003133.00", "000032.22 00",
     "line 28  Z,L WORKX"),
    ("003133.40", "000032.16 80  007000.20 D0",
     "line 29  ST(BU,7)"),
    ("003134.40", "002606.70 8A  010000.22 B0",
     "line 30  M+1(BU,8)"),
    ("003135.40", "002601.53 80  007000.20 D0",
     "line 31  ST(BU,7),L COUNT"),
    ("003136.40", "002657.21 05",
     "line 32  V+I,L SYMC-1."),
    ("003137.00", "003055.50 00",
     "line 33  B,L FOUND"),
    ("003137.40", "000004.00 83  060000.06 70",
     "line 34  L SET  LF(BU,48)"),
    ("003140.40", "002736.00 80  060000.23 10",
     "line 35  KF(BU,48),L BLANK"),
    ("003141.40", "003142.76 C0",
     "line 36  BZAE,L SETA"),
    ("003142.00", "003237.74 C0",
     "line 37  BZRZ,L NORM"),
    ("003142.40", "002566.20 10",
     "line 38  L SETA  LX"),
    ("003143.00", "000000.71 87  007027.20 50",
     "line 39  L(BU,7)"),
    ("003144.00", "000011.20 B0",
     "line 40  V+,L XSC,$R"),
    ("003144.40", "000000.00 88  060000.20 50",
     "line 41  L(BU,48)"),
    ("003145.40", "000004.00 83  060000.21 10",
     "line 42  K(BU,48)"),
    ("003146.40", "003237.76 C6",
     "line 43  BAEZ,L NORM"),
    ("003147.00", "003103.50 00",
     "line 44  B,L ETA"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.55 ")
finish(fails)
