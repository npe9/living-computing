"""MCP INITIALIZATION, printed p.56 -- THE REEL CARD ROUTINE, THE
FINAL ROUTINE, AND THE SORT'S ENTRY.

Fifty-six lines, forty-one of which compile, in three boxed sections
the listing names itself.  decks/mcp_bootstrap_p56.strap carries the
derivations.

IT RUNS STRAIGHT INTO printed p.57: line 56 stands at 003205.40, one
half word, and p.57 line 1 is 003206.00.

IT DEFINES L SEARA, which p.57 line 30 branches BACK to and could
only carry as a stand-in -- line 55, 003205.00.

EVERY BRANCH OFF THE PAGE LANDS ON A TRANSCRIBED ONE: L ERROR and
L NORM and L ERR4 on p.58, L FIN3 and L SKIP on p.57.  Seven
stand-ins confirmed by their definitions.

T IODCT AND T LREFN ARE SYN(BU,12) AND THE LENGTH FIELD IS WHAT SAYS
SO.  Lines 39, 40 and 42 write the operation bare, and the second
group's leading octal is the length times 512: 014000/512 = 12.  The
same arithmetic reads 010000 as 8, 022000 as 18 and 060000 as 48 on
rows that write their dds explicitly.

ALL FORTY-ONE ROWS WERE BIT-EXACT ON THE FIRST RUN, including the
derived (BU,12), both branch-target expressions and the negative
whole-word address.

MEASURED INJECTIONS -- the observed sets, run through tests/inject.py.

  T IODCT loses its (BU,12) -- 1 FAIL, line 39, reading 000000 for
  014000.  That is the derivation itself: the length comes from the
  symbol because the statement writes none.
  L BLANK loses its byte size -- 1 FAIL, line 11 ONLY, reading
  060000 for 060600.  printed p.55 line 18 uses the same symbol with
  "(BU,48)" WRITTEN and is untouched by the same injection, which is
  the dds rule demonstrated on one operand across two pages.
  Line 13's "L REEL2-0.32" becomes "L REEL2" -- 1 FAIL, reading
  003161.34 for 003160.74: a half word.
  Line 33's "L FIN2-1." becomes "L FIN2" -- 1 FAIL, reading
  003175.34 for 003174.34: a whole word.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p56.strap").read())

SYMBOLS = {
    "LREELR": "003147.40",
    "LREEL1": "003151.40",
    "LREEL2": "003161.00",
    "LFINAL": "003170.00",
    "LFIN2":  "003175.00",
    "LFINI":  "003200.40",
    "LSEARA": "003205.00",
}

ROWS = [
    ("003147.40", "002601.52 80  003151.74 00",
     "line 5   L REELR BZB"),
    ("003150.40", "000005.37 02",
     "line 6   LCI"),
    ("003151.00", "003241.10 00",
     "line 7   B,L ERROR"),
    ("003151.40", "000000.61 87  003237.74 0E",
     "line 8   L REEL1 BB1"),
    ("003152.40", "000002.00 83  060000.06 70",
     "line 10  LF(BU,48)"),
    ("003153.40", "002736.00 80  060600.21 10",
     "line 11  K,L BLANK"),
    ("003154.40", "003237.76 C6",
     "line 12  BAEZ,L NORM"),
    ("003155.00", "002601.62 80  003160.74 02",
     "line 13  BB,L OVBIT"),
    ("003156.00", "000000.00 86  000000.20 50",
     "line 14  L(BU,64)"),
    ("003157.00", "003161.34 C6",
     "line 15  BRZZ,L REEL2"),
    ("003157.40", "000003.37 02",
     "line 16  LCI"),
    ("003160.00", "003262.50 00",
     "line 17  B,L ERR4"),
    ("003160.40", "000000.22 06",
     "line 18  Z,0.0(L XFR)"),
    ("003161.00", "000002.00 83  000000.02 A6",
     "line 19  L REEL2 TI,1"),
    ("003162.00", "000000.00 84  000000.20 50",
     "line 20  L(BU,64)"),
    ("003163.00", "000000.62 87  007027.20 10",
     "line 21  +(BU,7)"),
    ("003164.00", "000032.00 80  000000.20 D0",
     "line 22  ST(BU,64)"),
    ("003165.00", "000026.00 80  022000.20 50",
     "line 23  L(BU,18)"),
    ("003166.00", "000000.34 8A  022000.20 D0",
     "line 24  ST(BU,18)"),
    ("003167.00", "000001.15 07",
     "line 25  V+ICR"),
    ("003167.40", "003237.50 00",
     "line 26  B,L NORM"),
    ("003170.00", "777777.00 83  000001.02 A4",
     "line 32  L FINAL TI,1,-1.0"),
    ("003171.00", "002601.51 80  003174.34 0C",
     "line 33  BZB1,L FINB"),
    ("003172.00", "000000.13 34",
     "line 35  SV"),
    ("003172.40", "000000.32 8F  003241.34 02",
     "line 36  BB,0.26($15)"),
    ("003173.40", "003232.10 00",
     "line 37  B,L FIN3"),
    ("003174.00", "000000.32 8F  003241.34 02",
     "line 38  BB,0.26($15)"),
    ("003175.00", "000000.64 84  014000.20 50",
     "line 39  L FIN2  L,T IODCT"),
    ("003176.00", "000000.50 84  014000.21 10",
     "line 40  K,T LREFN"),
    ("003177.00", "003200.76 46",
     "line 41  BALZ,L FINI"),
    ("003177.40", "000000.50 84  014000.20 D0",
     "line 42  ST,T LREFN"),
    ("003200.40", "002605.23 10",
     "line 47  L FINI  SX"),
    ("003201.00", "000032.22 00",
     "line 48  Z,L WORKX"),
    ("003201.40", "000023.22 00",
     "line 49  Z,L IODX"),
    ("003202.00", "000000.24 34",
     "line 50  LV"),
    ("003202.40", "002601.53 80  007027.20 50",
     "line 51  L(BU,7),L COUNT"),
    ("003203.40", "003231.74 C6",
     "line 52  BRZZ,L SKIP"),
    ("003204.00", "000011.24 50",
     "line 53  LC"),
    ("003204.40", "002602.25 50",
     "line 54  SC"),
    ("003205.00", "002602.06 50",
     "line 55  L SEARA LC"),
    ("003205.40", "002607.07 01",
     "line 56  LVI"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.56 ")
finish(fails)
