#!/usr/bin/env python3
"""verify_mcp_bootstrap_p52.py -- DECODE SECTION OF MCP, the
dispatcher entry and the initialization routine, printed page 52
(../decks/mcp_bootstrap_p52.strap).
docs/MCP_Mar63_001-249.pdf PDF p.59, header "PAGE NUMBER 52".
AGENTS.md rule 3.

Forty-five printed rows with binary output and seven symbol
locations.

>>> LINE 7 IS L DECOD AT 002737.00 -- THE ENTRY printed p.47's
LINKAGE FORMAT NAMES -- AND IT OPENS WITH AN EIGHT-WORD SWAP. <<<

p.47's worked call is "LVI,$15,X / B,L DECOD / X VF,A / CF,B / VF,C",
with A the first word address of the break-down area and B the mode;
lines 8 and 9 read exactly that.  The SWAPI of eight words is the
largest in the corpus and the tenth caller; line 12 is a second, of
three.

THE IOD AND REEL DISPATCH IS FOUR CHARACTERS WIDE.  Lines 19-25 load
twenty-four bits of the card and compare them against L IOD and
L REEL, branching to L IODRN or L REELR and otherwise to L ERROR with
a flag of 9.  Twenty-four bits is four BCD characters, so the
comparison reads "IOD " and "REEL" and no more.

>>> A dds TRAVELS THROUGH A SYN ACROSS A PAGE BOUNDARY, AND LINES 36
AND 37 ARE THE PROOF. <<<

Both are bare connectives with no data description written:

    line 36   CM0000,L INFAD    prints 001000.00 F0  -- length ONE
    line 37   CM0000,L COUNT    prints 007000.00 F0  -- length SEVEN

L INFAD is printed p.48 line 52's "DD(BU,1),0" and L COUNT is its
line 49's "DRZ(BU,7),(1)", so the two rows differ ONLY in a property
carried from four pages away.  C22-6531 printed p.31 is the rule and
printed p.45 is where strap_asm learned it; this is where it crosses
a page boundary.

THIS PAGE IS listing_typography.md 13d AT ITS THICKEST.  The drum
prints DIGIT ZERO AS C across whole rows: line 24 prints its own
location as "CCCC11.37" and line 35 its operand as "C.O", so the rows
announce themselves.  Five bytes were settled by DECODE plus a row
already checked elsewhere in this corpus:

    line 24       "C2" is 02 -- LCI is an immediate index operation,
                  whose byte's high nibble is zero; printed p.43 line
                  33's "LVI,$3,5.0" prints 000005.07 01.
    line 35       "FC" is F0.
    lines 39, 52, 53  "CA", "C0", "C8" are 0A, 00 and 08; printed
                  p.40 line 40's "Z,0.0($15)" prints 000000.22 0F.

AND TWO ROWS ARE NOT THE ARTIFACT, which is the other half of the
rule: lines 21 and 23 print "003021.76 C6" and "003147.76 C6" and
both Cs are REAL -- printed p.43 line 43's "BAE,Q CK" prints
002447.76 C2 and is checked.  What mattered on those two rows is the
OCTAL pair, which cannot hold a C: 0o76 has bit 18 SET, so L IODRN
and L REELR are at .40 and not .00.  Reading them as .00 was this
deck's first draft and three rows failed.

TWO INJECTIONS, OBSERVED FAILURE SETS WRITTEN DOWN:

  L INFAD's stand-in dds dropped, "SYN(BU,1)" -> "SYN" -- 1 FAIL,
  line 36, reading 000000.00 F0 where the listing prints 001000.00
  F0, and line 37 still passes because L COUNT keeps its own.  That
  is the cross-page dds in one row.
  L IODRN's stand-in moved back to 003021.00 -- 1 FAIL, line 21,
  reading 003021.36 where the listing prints .76.  Bit 18 is one
  octal digit and it is the whole difference between a half word.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p52.strap").read())

SYMBOLS = {
    # >>> THE ENTRY printed p.47 NAMES.
    "LDECOD": "002737.00",
    "LOVER":  "002745.40",
    "LFWA":   "002750.00",
    "LINIT":  "002755.00",
    "LINITA": "002757.40",
    "LOOPU":  "002766.40",
    "LOOPC":  "002772.00",
}

ROWS = [
    ("002737.00", "002571.00 80  000023.20 E0",
     "line 7   L DECOD  SWAPI,8,L TY,L IODX  -SAVE INDEXES"),
    ("002740.00", "000000.06 3F",
     "line 8   LV,L IODX,0.0($15)  -GET FWA CONTENTS"),
    ("002740.40", "000000.46 5F",
     "line 9   LC,L IODX,0.32($15)  -CHECK FOR NOT OVERLAP"),
    ("002741.00", "002745.70 42",
     "line 10  BXCZ,L OVER  -IF OVERLAP MODE"),
    ("002741.40", "002601.62 80  002745.74 0E",
     "line 11  BB1,L OVBIT,L OVER  -CHECK AND SET"),
    ("002742.40", "000024.00 80  002720.06 E0",
     "line 12  SWAPI,3,L XPP,L NOSAV  -SAVE THE OVERLAP INDEXES"),
    ("002743.40", "002557.00 80  000024.06 A0",
     "line 13  TI,3,L PPURF,L XPP  -AND INITIALIZE"),
    ("002744.40", "000000.22 04",
     "line 14  Z,0.0(L XPP)  -ZERO FIRST PPREF"),
    ("002745.00", "000001.22 04",
     "line 15  Z,1.0(L XPP)"),
    ("002745.40", "000001.00 83  000000.20 50",
     "line 16  L OVER  L(BU,64),1.0(L IODX),0.0"),
    ("002746.40", "002601.51 80  002755.34 02",
     "line 17  BB,L FINB,L INIT  -BRANCH ON FINAL BIT"),
    ("002747.40", "003170.34 C6",
     "line 18  BRZZ,L FINAL  -BRANCH ON ZERO FWA"),
    ("002750.00", "000001.00 83  030000.20 50",
     "line 19  L FWA  L(BU,24),1.0(L IODX),0.0"),
    ("002751.00", "002734.00 80  030000.21 10",
     "line 20  K(BU,24),L IOD,0.0"),
    ("002752.00", "003021.76 C6",
     "line 21  BAEZ,L IODRN  -IOD----BRANCH."),
    ("002752.40", "002735.00 80  030000.21 10",
     "line 22  K(BU,24),L REEL,0.0"),
    ("002753.40", "003147.76 C6",
     "line 23  BAEZ,L REELR  -REEL----BRANCH."),
    ("002754.00", "000011.37 02",
     "line 24  LCI,$15,9.0  -NEITHER -- ERROR FLAG  [listing prints C2]"),
    ("002754.40", "003241.10 00",
     "line 25  B,L ERROR  -BRANCH TO ERROR"),
    ("002755.00", "000001.00 83  030000.20 50",
     "line 31  L INIT  L(BU,24),1.0(L IODX)"),
    ("002756.00", "002603.13 10",
     "line 32  SX,L XIO,L SAVEY  -SAVE THE IOREQ"),
    ("002756.40", "002604.15 10",
     "line 33  SX,L XFR,L SAVEZ  -SAVE THE FREEL TABLE"),
    ("002757.00", "002760.74 C2",
     "line 34  BRZ,L INITA+1.  -IF REJ END COMBO"),
    ("002757.40", "002601.51 80  001000.00 F0",
     "line 35  L INITA  CM0000(BU,1),L FINB,0.0  [listing FC]"),
    ("002760.40", "002601.73 80  001000.00 F0",
     "line 36  CM0000,L INFAD  -ZERO THE INF DISK  [dds length ONE]"),
    ("002761.40", "002601.53 80  007000.00 F0",
     "line 37  CM0000,L COUNT  -ZERO RLSYM NO.  [dds length SEVEN]"),
    ("002762.40", "002606.24 10",
     "line 38  LX,L WORKX,L CLEAR  -CLEAR RLSYM COUNTS"),
    ("002763.00", "000000.22 0A",
     "line 39  Z,0.0(L WORKX)  [listing prints CA]"),
    ("002763.40", "002763.25 4C",
     "line 40  CBR+,L WORKX,$-.32"),
    ("002764.00", "000027.16 10",
     "line 41  LX,L XSU,L XSU  -CHECK FOR INDEX"),
    ("002764.40", "002767.71 46",
     "line 42  BXVZZ,L OOPU+1."),
    ("002765.00", "002617.17 0D",
     "line 43  V-I,L XSU,L SYMU-1.  -CLEAR SYMBOLIC"),
    ("002765.40", "000027.16 50",
     "line 44  LC,L XSU,L XSU"),
    ("002766.00", "002620.22 00",
     "line 45  Z,L SYMU"),
    ("002766.40", "002620.22 07",
     "line 46  L OOPU  Z,L SYMU(L XSU)"),
    ("002767.00", "002766.57 C8",
     "line 47  CB-,L XSU,L OOPU"),
    ("002767.40", "000030.20 10",
     "line 48  LX,L XSC,L XSC  -CHECK FOR INDEX"),
    ("002770.00", "002773.31 46",
     "line 49  BXVZZ,L OOPC+1."),
    ("002770.40", "002657.21 0D",
     "line 50  V-I,L XSC,L SYMC-1.  -CLEAR SYMBOLIC"),
    ("002771.00", "000030.20 50",
     "line 51  LC,L XSC,L XSC"),
    ("002771.40", "002660.22 00",
     "line 52  Z,L SYMC  [listing prints C0]"),
    ("002772.00", "002660.22 08",
     "line 53  L OOPC  Z,L SYMC(L XSC)  [listing prints C8]"),
    ("002772.40", "002772.21 C8",
     "line 54  CB-,L XSC,L OOPC"),
    ("002773.00", "000031.22 10",
     "line 55  LX,L XNT,L XNT  -CHECK FOR INDEX"),
    ("002773.40", "002776.71 46",
     "line 56  BXVZZ,L OOPN+1."),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.52 ")
finish(fails)
