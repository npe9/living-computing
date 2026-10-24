"""MCP INITIALIZATION, printed p.61 -- THE ASSIGN PROGRAM'S CONSTANTS
AND INDEX NAMES.

Fifty-six lines, twenty of which compile a word.
decks/mcp_bootstrap_p61.strap carries the derivations.

ONE ROW CONFIRMS printed p.60's SYN CARDS FROM THIS PAGE'S OWN
BINARY.  Line 19 is "T SAV XW,T PREFT,T PPC,T PPREF" compiling
003317.00+ 000 000024 003314, and an XW's third group is its COUNT:
000024 = 20 decimal, which is exactly what p.60 line 6 declares as
"T PPC SYN,20" -- printed there with NULL in the binary column
because a SYN compiles nothing.  p.60 says the number, p.61 spends
it.

ROWS DELIBERATELY ABSENT, following printed p.24's precedent: line
52's DRZ prints its SIZE (000017.00 = 15 words), not a word, and the
seventeen index SYNs print their VALUE -- those are checked in
SYMBOLS instead, which is the stronger place for them.

LINE 51's CNOP IS IN THE TABLE and prints 000000.30 00, a NOP half
word.  The counter stood at 003273.34 after line 30's last one-bit
DD, so this is a CNOP that HAD TO PAD -- the same distinction
printed p.24 line 44 draws.

ALL TWENTY ROWS AND ALL THIRTY-EIGHT SYMBOLS PASSED ON THE FIRST RUN.

MEASURED INJECTIONS -- the observed sets, run through tests/inject.py.

  T PPC 20 -> 21 -- 1 FAIL, line 19, reading 000025 for 000024 in the
  XW's COUNT group.  That is printed p.60's SYN card checked from
  p.61's binary, and the injection is what shows the two are joined.
  T PREFT (8)3317.0 -> (8)3320.0 -- 1 FAIL, line 19's VALUE group.
  T X1 $10 -> $9 -- 5 FAIL: T CTWDX, T X1, T IXF, T IXK and T IXL,
  because four of the seventeen index names are SYNs to T X1 rather
  than to a register.  One card moves five symbols.
  T LUCT DD(BU,18) -> DD(BU,17) -- every one of the ten following
  one-bit DDs moves by a bit (T ONE 110289 for 110290, and so on).
  The location column alone pins all eleven widths.
  Line 51's CNOP removed -- 2 FAIL: the CNOP row reads 000000.00 00
  for 000000.30 00, and T ASAVE lands at bit 110300 instead of
  110336.  So the CNOP both emits and pads, and the injection shows
  both halves at once.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p61.strap").read())

_XW = "000000.00+ 000 000000 000000"

SYMBOLS = {
    # The words this page defines.
    "TNEXT":  "003264.40",
    "TCTEMP": "003265.00",
    "TIPL":   "003266.00",
    "TWORK1": "003267.00",
    "TWORK2": "003270.00",
    "TREFIL": "003271.00",
    "TSAV":   "003272.00",
    "TLUCT":  "003273.00",
    "TONE":   "003273.22",
    "TMODE":  "003273.23",
    "TINDA":  "003273.24",
    "TINDB":  "003273.25",
    "TINDC":  "003273.26",
    "TINDD":  "003273.27",
    "TINDE":  "003273.30",
    "TINDZ":  "003273.31",
    "TLOOP":  "003273.32",
    "TLOOP1": "003273.33",
    "TASAVE": "003274.00",
    # >>> THE TWO dds SYNs, whose location column prints the
    # RESOLVED VALUE: T CTEMP is 003265.00 and +0.25 is 0o31.
    "TCTACH": "003265.00",
    "TCTSCH": "003265.31",
    # >>> AND THE SEVENTEEN INDEX NAMES.  Each resolves to the index
    # register's WORD address, 16+n, which is what the listing's
    # location column prints on a SYN row.  SEVEN OF THEM ALIAS
    # ANOTHER ALIAS rather than a register.
    "TCTWDX": "000032.00",   # SYN,T X1  -> $10
    "TX1":    "000032.00",   # $10
    "TX2":    "000031.00",   # $9
    "TX1BR":  "000021.00",   # $1
    "TX3":    "000022.00",   # $2
    "TIXA":   "000024.00",   # $4
    "TIXB":   "000025.00",   # $5
    "TIXE":   "000023.00",   # $3
    "TIXF":   "000032.00",   # SYN,T X1  -> $10
    "TIXG":   "000030.00",   # $8
    "TIXH":   "000022.00",   # SYN,T X3  -> $2
    "TIXI":   "000025.00",   # SYN,T IXB -> $5
    "TIXJ":   "000026.00",   # $6
    "TIXD":   "000027.00",   # $7
    "TIXK":   "000032.00",   # SYN,T X1  -> $10
    "TIXL":   "000032.00",   # SYN,T X1  -> $10
    "TIXM":   "000030.00",   # SYN,T IXG -> $8
}

ROWS = [
    ("003264.40", "000000.00+",
     "line 7   T NEXT  VF,  -THE ADDR OF THE NEXT PP TO BE RUN"),
    ("003265.00", _XW,
     "line 8   T CTEMP XW  -TEMP SYMBOLIC CHAN WORD"),
    ("003266.00", "000000.00+",
     "line 9   T IPL  VF,0.0  -CHAN ADDRESSES FOR IPL"),
    ("003267.00", _XW,
     "line 16  T WORK1 XW  -TEMPORARY WORKING WORD"),
    ("003270.00", _XW,
     "line 17  T WORK2 XW  -TEMPORARY WORKING WORD"),
    ("003271.00", _XW,
     "line 18  T REFIL XW  -TEMP STORAGE FOR IX -A-"),
    ("003272.00", "003317.00+ 000 000024 003314",
     "line 19  T SAV  XW,T PREFT,T PPC,T PPREF"),
    ("003273.00", "000000",
     "line 20  T LUCT DD(BU,18),0  -LARGEST UNIT COUNT ON ONE CHANNEL", 18),
    ("003273.22", "1",
     "line 21  T ONE  DD(BU,1),1  -CONSTANT OF ONE", 1),
    ("003273.23", "0",
     "line 22  T MODE DD(BU,1),0  -SINGLE OR FULL NOT-OVERLAP MODE", 1),
    ("003273.24", "0",
     "line 23  T INDA DD(BU,1),0  -SAME CHANNEL ALLOWED INDICATOR", 1),
    ("003273.25", "0",
     "line 24  T INDB DD(BU,1),0  -THE SPLIT CHANNEL INDICATOR", 1),
    ("003273.26", "0",
     "line 25  T INDC DD(BU,1),0  -UNIT FOUND -- MULTI-UNIT CHECK", 1),
    ("003273.27", "0",
     "line 26  T INDD DD(BU,1),0  -BYPASS OPTIMISED REEL MTINGS", 1),
    ("003273.30", "0",
     "line 27  T INDE DD(BU,1),0  -THE ADVANCE AND SAVE INDEX IND", 1),
    ("003273.31", "0",
     "line 28  T INDZ DD(BU,1),0  -MORE MULTI-UNITS AVAILABLE", 1),
    ("003273.32", "0",
     "line 29  T LOOP DD(BU,1),0  -TO PREVENT A LOOP IN SECTION ELEVEN", 1),
    ("003273.33", "0",
     "line 30  T LOOP1 DD(BU,1),0  -LOOP PREVENTER NUMBER 2", 1),
    ("003273.40", "000000.30 00",
     "line 51  CNOP  (the one that had to PAD)"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.61 ")
finish(fails)
