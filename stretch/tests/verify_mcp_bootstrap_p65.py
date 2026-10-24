"""MCP INITIALIZATION, printed p.65 -- THE ENTRY POINT TO THE ASSIGN
ROUTINE.

Fifty-six lines, thirty-eight of which compile.
decks/mcp_bootstrap_p65.strap carries the derivations.

>>> LINE 6 IS T ASIGN, THE ADDRESS THE BOOT RUN HAS BEEN BRANCHING
TO. <<<  decks/mcp_bootstrap_p27.strap line 60 is "X241 B,T ASIGN"
and the PC trail has ended at half-word 3970 = 003701.00 since
printed p.58 landed.  The row is "T ASIGN SWAPI,12,$1,T ASAVE"
compiling 000021.00 80 003274.30 E0: 000021 is word 0o21 = 16+1 =
$1; 003274 is T ASAVE, printed p.61 line 52's DRZ(BU,64),(15); and
".30" -> bits 19-22 = 0110 = TWELVE.  Twelve index registers into a
fifteen-word save area.

LINE 5's CNOP COMPILES NOTHING, and that is the other half of a
distinction printed p.24 drew.  printed p.64 line 39's DRZ ends
exactly at 003701.00, so the counter was already rounded and the
CNOP has no location and no binary -- where p.24 line 44, p.61 line
51 and p.64 line 5 all HAD to pad and print 000000.30 00.

SEVEN BARE VFL STATEMENTS TAKE THEIR dds FROM SYMBOLS DERIVED BEFORE
printed p.62 WAS READ.  Line 27's "L,T UNCT(T IXE),46" writes no dds
and compiles 010027.20 50 -- 010000/512 = 8 -- from T UNCT's own
SYN(BU,8), which pp.54 and 58 derived and p.62 line 10 confirmed.
Likewise line 46 (T RCAD, 8), line 51 (T TYPE, 4) and line 52
(T TYAD, 8).  The pages that DECLARE them and the page that SPENDS
them bare are both transcribed and the bits agree.

ALL THIRTY-EIGHT ROWS AND ALL NINE SYMBOLS PASSED ON THE FIRST RUN.

MEASURED INJECTIONS -- the observed sets, run through tests/inject.py.

  T ASAVE (8)3274.0 -> (8)3275.0 -- 1 FAIL, line 6's second group.
  That address is printed p.61 line 52's DRZ, four pages back.
  T ASIGN's swap count 12 -> 11 -- 1 FAIL, reading 003274.26 for
  003274.30.  The count lives in bits 19-22 of the second
  half-word's address field, so one less register changes the
  printed octal pair and nothing else.
  T UNCT loses its (BU,8) -- 1 FAIL, line 27 reading 000027.20 50
  for 010027.20 50.  THAT IS THE dds RULE CHECKED FROM THE SPENDING
  SIDE: line 27 writes "L,T UNCT(T IXE),46" with no dds, so the
  length comes from the symbol, and printed p.62 line 10 is the card
  that declares it.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p65.strap").read())

SYMBOLS = {
    "TASIGN": "003701.00",
    "TB1F":   "003704.00",
    "TB1C":   "003706.40",
    "TA1":    "003710.00",
    "TD1":    "003722.40",
    "TCLEAR": "003724.00",
    "TSETAC": "003726.00",
    "TSETBC": "003727.40",
    "TCOMPA": "003730.40",
}

ROWS = [
    ("003701.00", "000021.00 80  003274.30 E0",
     "line 6   T ASIGN SWAPI,12"),
    ("003702.00", "000000.24 1F",
     "line 7   LX,T CTWDX"),
    ("003702.40", "003273.23 80  006000.00 F0",
     "line 8   CM0000(BU,6)"),
    ("003703.40", "004215.31 40",
     "line 9   BZXVZ,T A9"),
    ("003704.00", "003706.63 40",
     "line 10  T B1F  BZXF"),
    ("003704.40", "003313.06 10",
     "line 14  LX,T IXE,T PPURF"),
    ("003705.00", "000000.46 80  004416.74 02",
     "line 15  BB,T ASGNP,T D"),
    ("003706.00", "003710.10 00",
     "line 16  B,T A1"),
    ("003706.40", "003272.06 10",
     "line 21  T B1C  LX"),
    ("003707.00", "003273.30 80  002000.00 F0",
     "line 22  CM0000(BU,2)"),
    ("003710.00", "000000.47 83  004417.34 02",
     "line 23  T A1  BB,T LPPEN"),
    ("003711.00", "000000.44 83  004211.74 02",
     "line 24  BB,T JBPRO"),
    ("003712.00", "000000.46 83  004203.74 02",
     "line 25  BB,T ASGNP"),
    ("003713.00", "000000.10 33",
     "line 26  LV,T IXA"),
    ("003713.40", "000000.34 83  010027.20 50",
     "line 27  L,T UNCT,46"),
    ("003714.40", "000011.10 50",
     "line 28  LC,T IXA,$R"),
    ("003715.00", "004201.70 42",
     "line 29  BXCZ,T B8C"),
    ("003715.40", "003271.11 03",
     "line 30  LRI"),
    ("003716.00", "003271.11 10",
     "line 31  SX"),
    ("003716.40", "000000.45 83  004361.34 02",
     "line 32  BB,T RJECT"),
    ("003717.40", "000000.24 1F",
     "line 33  LX,T CTWDX"),
    ("003720.00", "003723.23 42",
     "line 34  BXF,T D1+.32"),
    ("003720.40", "003273.33 80  003722.74 06",
     "line 35  BBZ,T LOOP1"),
    ("003721.40", "003651.06 90",
     "line 36  KV"),
    ("003722.00", "003743.73 40",
     "line 37  BZXH,T A2"),
    ("003722.40", "003651.07 30",
     "line 38  T D1  SV"),
    ("003723.00", "003647.24 10",
     "line 44  LX,T X1,T TYARA"),
    ("003723.40", "000011.22 00",
     "line 45  Z,$R"),
    ("003724.00", "000000.20 8A  010000.20 D0",
     "line 46  T CLEAR ST"),
    ("003725.00", "003650.24 F0",
     "line 47  V+CR"),
    ("003725.40", "003724.30 40",
     "line 48  BZXCZ,T CLEAR"),
    ("003726.00", "000000.22 84  003727.74 00",
     "line 49  T SETAC BZB"),
    ("003727.00", "003373.11 01",
     "line 50  LVI"),
    ("003727.40", "000000.03 84  004000.20 50",
     "line 51  T SETBC L,T TYPE"),
    ("003730.40", "000000.00 8A  010000.21 10",
     "line 52  T COMPA K,T TYAD"),
    ("003731.40", "003733.76 C2",
     "line 53  BAE,T C1"),
    ("003732.00", "003650.24 D0",
     "line 54  V+C"),
    ("003732.40", "003730.70 40",
     "line 55  BZXCZ,T COMPA"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.65 ")
finish(fails)
