"""MCP INITIALIZATION, printed p.67 -- THE MULTI-UNIT AND SINGLE-UNIT
ASSIGNMENT ATTEMPTS.

Fifty-six lines, thirty-eight of which compile.
decks/mcp_bootstrap_p67.strap carries the derivations.

IT PLACES BOTH OF printed p.66's FORWARD REFERENCES: p.66 line 45
branches to T A2E and line 49 to T A7, and lines 5 and 50 here are
those labels, at 003775.00 and 004020.40.

NINE BARE VFL STATEMENTS, AND EVERY dds COMES FROM A PAGE ALREADY
TRANSCRIBED -- p.61's T CTACH (18), T CTSCH (7) and T INDB (1),
p.62's T RLSYM (7) and T TYPE (4), p.63's T EQUIP (4) and T UNITK
(4).  T INDB is a `DD` LABEL and not a SYN, which makes this a
second independent instance of the shape printed p.66 found.

T CTACH AND T CTSCH ARE THE TWO HALVES OF ONE WORD AND BOTH ARE
SPENT HERE.  printed p.61 lines 13 and 14 declare them as
SYN(BU,18),T CTEMP+0.0 and SYN(BU,7),T CTEMP+0.25; line 32 here
compiles 003265.00 and line 25 compiles 003265.31.  The absolute
channel number and the symbolic one, eighteen bits and seven, in one
temp word -- declared six pages back.

ALL THIRTY-EIGHT ROWS AND ALL NINE SYMBOLS PASSED ON THE FIRST RUN.

MEASURED INJECTIONS -- the observed sets, run through tests/inject.py.

  T CTSCH 003265.31 -> 003265.32 -- 1 FAIL, line 25.  That is the
  SYMBOLIC half of the temp channel word, declared on printed p.61
  as T CTEMP+0.25 and spent here.
  T INDB loses its (BU,1) -- 1 FAIL, line 41, reading 000000 for
  001000.  T INDB is a `DD` LABEL, not a SYN (p.61 line 24 is
  "DD(BU,1),0"), so this is the dds rule checked on the second kind
  of symbol.
  T UNITK 0.59 -> 0.58 -- 1 FAIL, line 35, reading 000000.72 for
  000000.73.
  T CHSXW (8)2152.0 -> (8)2153.0 -- 1 FAIL, line 50.  printed p.62
  line 56's last SYN card, which resolves through S X CHAN to an
  address fixed on a page far earlier than this one.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p67.strap").read())

SYMBOLS = {
    # printed p.66's two stand-ins, placed here.
    "TA2E":  "003775.00",
    "TA7":   "004020.40",
    # Labels this page defines and uses itself.
    "TA6":   "003777.00",
    "TA6A":  "004002.00",
    "TA6B":  "004003.40",
    "TA6C":  "004004.40",
    "TA6D":  "004005.40",
    "TAQ":   "004016.40",
    "TA7A":  "004021.00",
}

ROWS = [
    ("003774.00", "003756.72 C0",
     "line 1   BZXE,T B2"),
    ("003774.40", "004020.50 00",
     "line 2   B,T A7"),
    ("003775.00", "003273.23 80  003777.34 02",
     "line 5   T A2E  BB"),
    ("003776.00", "003273.31 80  003756.74 0E",
     "line 6   BB1,T INDZ"),
    ("003777.00", "003271.24 10",
     "line 12  T A6  LX"),
    ("003777.40", "000000.13 84  007000.06 70",
     "line 13  LF,T RLSYM"),
    ("004000.40", "000022.22 00",
     "line 14  Z,T X3"),
    ("004001.00", "003267.11 50",
     "line 15  SC,T WORK1"),
    ("004001.40", "004046.34 C2",
     "line 16  BRZ,T A3"),
    ("004002.00", "000000.13 8A  007000.23 10",
     "line 17  T A6A  KF"),
    ("004003.00", "004004.76 C2",
     "line 18  BAE,T A6C"),
    ("004003.40", "004002.25 48",
     "line 19  T A6B  CB+"),
    ("004004.00", "004005.50 00",
     "line 20  B,T A6D"),
    ("004004.40", "000001.05 00",
     "line 22  T A6C  C+I"),
    ("004005.00", "004003.50 00",
     "line 23  B,T A6B"),
    ("004005.40", "003265.31 80  007000.23 10",
     "line 25  T A6D  KF"),
    ("004006.40", "003273.05 90",
     "line 26  KC,T LUCT"),
    ("004007.00", "004016.73 42",
     "line 27  BXH,T AQ"),
    ("004007.40", "004046.36 C0",
     "line 28  BZAE,T A3"),
    ("004010.00", "003265.00 80  022027.20 50",
     "line 32  L,T CTACH,46"),
    ("004011.00", "000011.04 10",
     "line 33  LX,T X3,$R"),
    ("004011.40", "000000.14 32",
     "line 34  LV,T IXJ"),
    ("004012.00", "000000.73 82  004027.20 50",
     "line 35  L,T UNITK,46"),
    ("004013.00", "000011.14 50",
     "line 36  LC,T IXJ,$R"),
    ("004013.40", "003273.24 80  004065.34 00",
     "line 37  BZB,T INDA"),
    ("004014.40", "003273.23 80  004016.74 02",
     "line 38  BB,T MODE"),
    ("004015.40", "003315.06 90",
     "line 39  KV,T PPRUN"),
    ("004016.00", "004065.32 C0",
     "line 40  BZXE,T C3Z"),
    ("004016.40", "003273.25 80  001000.36 F0",
     "line 41  T AQ  CM1111"),
    ("004017.40", "000001.23 05",
     "line 42  V+I,T X2"),
    ("004020.00", "004046.10 00",
     "line 43  B,T A3"),
    ("004020.40", "002152.04 10",
     "line 50  T A7  LX"),
    ("004021.00", "000000.64 82  004034.34 02",
     "line 51  T A7A  BB"),
    ("004022.00", "000000.31 82  004034.34 02",
     "line 52  BB,T CHAVL"),
    ("004023.00", "000000.03 84  004000.06 70",
     "line 53  LF,T TYPE"),
    ("004024.00", "000000.64 82  004000.23 10",
     "line 54  KF,T EQUIP"),
    ("004025.00", "004034.36 C0",
     "line 55  BZAE,T B7"),
    ("004025.40", "000000.33 82  004035.34 02",
     "line 56  BB,T MULTI"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.67 ")
finish(fails)
