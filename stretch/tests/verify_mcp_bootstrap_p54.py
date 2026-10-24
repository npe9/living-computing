#!/usr/bin/env python3
"""verify_mcp_bootstrap_p54.py -- the DISK-TRACK CHECK ROUTINE and
the TAPE IOD ROUTINE, printed page 54
(../decks/mcp_bootstrap_p54.strap).
docs/MCP_Mar63_001-249.pdf PDF p.61, header "PAGE NUMBER 54".
AGENTS.md rule 3.

Forty-eight printed rows with binary output and ten symbol
locations.

>>> IT CONFIRMS TWO MORE OF printed p.53's STAND-INS: L CODE at
003042.00 and L IODTP at 003077.00. <<<

A THIRD "$" IN FRONT OF AN OPERATION.  Line 15 is
"$SF(BU,4),.48(L XNT)" and it compiles as a plain SF.  printed p.43
line 6 was "$B,Q GO$A" and printed p.53 line 14 "$TI,...".  THREE
INSTANCES IN THREE SOURCE DECKS, every one inert, and all three on
operations whose compiled row is ordinary.  C28-6129 printed p.37
accounts for a "$" on an OPERAND and says nothing about one on an
OPERATION.  Three is a pattern rather than an oddity: whatever the
"$" marks, it is not in the object program.

>>> AND printed p.51's L BLANK dds TRAVELS HERE, WHICH IS A THIRD
WITNESS FOR ITS LENGTH. <<<

Line 32 is a BARE "KF,L BLANK" and prints 060600 -- a length of
0o60, FORTY-EIGHT, and a byte size of 6.  p.51 line 34 declares
"L BLANK (AY)DD(BU,48,6)", and its eight characters of blanks were
settled by measuring the Y terminator's column in pixels, with the
declared (BU,48,6) as the only other witness.  This row is a third
and a different kind: the dds is not merely declared on p.51, it is
USED here by a row whose own printed length depends on it.  A wrong
dds on p.51 makes this row wrong too.

L ZBIT IS AN INTEGER AND LINE 41 USES IT AS A BIT ADDRESS.
"BZB1,L ZBIT(L XNT),L NORM" prints 000000.77 89 -- 0o77 is 63 -- and
printed p.50 line 40 defines "L ZBIT SYN(BU,1),63" with the listing
putting 63 in the INTEGER column and the location at zero.  So an
integer-classified symbol lands in a 24-bit bit-address field as the
number itself, which is what C22-6531 printed p.11 says an integer
does: it "adds into the low-order position of the field".

LINE 55 IS A HALT: "BD,$" at 003104.00, printing 003104.04 00 --
branch disabled to its own address.  The second deliberate stop this
project has transcribed, after printed p.6 line 1's "BD,$ -LOOP".

TWO INJECTIONS, OBSERVED FAILURE SETS WRITTEN DOWN:

  L BLANK's stand-in dds changed from (BU,48,6) to (BU,48,8) -- 1
  FAIL, line 32, reading 060000 where the listing prints 060600.
  NOT 061000, which is what this note predicted: a byte size of
  EIGHT does not fit a three-bit field and goes in as ZERO
  (C28-6129 printed p.16, "byte size is treated modulo 8"), so the
  injection reads as a byte size of 8-meaning-0 rather than as the
  literal 8.  printed p.51's byte size, checked from three pages
  away.
  L ZBIT's stand-in 63 -> 62 -- 1 FAIL, line 41, reading 000000.76
  for 000000.77, and nothing else: the symbol is used once.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p54.strap").read())

SYMBOLS = {
    # >>> printed p.53's TWO STAND-INS.
    "LCODE":  "003042.00",
    "LIODTP": "003077.00",
    "LOOPNT": "003042.40",
    "LNONCH": "003050.00",
    "LIOD2":  "003050.40",
    "LFOUND": "003055.40",
    "LNON":   "003062.00",
    "LNEW":   "003066.00",
    "LDSKC":  "003072.40",
    "LDSKD":  "003075.00",
    "LOOPSU": "003100.40",
    "LETA":   "003103.40",
    "LIOD3":  "003104.40",
}

ROWS = [
    ("003041.00", "000006.37 02",
     "line 1   LCI,$15,6.0  -NO TYPE MATCHED"),
    ("003041.40", "003241.10 00",
     "line 2   B,L ERROR  -WITH ERROR FLAG OF 6"),
    ("003042.00", "002567.22 10",
     "line 3   L CODE  LX,L XNT,L NTPUX"),
    ("003042.40", "000000.00 89  060000.20 50",
     "line 4   L OOPNT  L(BU,48),0.0(L XNT),0.0"),
    ("003043.40", "003050.74 C6",
     "line 5   BRZZ,L IOD2"),
    ("003044.00", "000004.00 83  060000.21 10",
     "line 6   K(BU,48),4.0(L IODX),0.0"),
    ("003045.00", "003050.36 C0",
     "line 7   BZAE,L NONCH  -NO EQUAL"),
    ("003045.40", "000000.60 89  004000.06 70",
     "line 8   LF(BU,4),.48(L XNT)  -EQUAL CHAN FOUND"),
    ("003046.40", "000000.74 8A  004000.23 10",
     "line 9   KF(BU,4),.60(L WORKX)"),
    ("003047.40", "003062.36 C2",
     "line 10  BAE,L NON  -IF EQUIP IS SAME"),
    ("003050.00", "003042.63 48",
     "line 11  L NONCH  CB+,L XNT,L OOPNT  -TRY AGAIN"),
    ("003050.40", "000004.00 83  000000.02 A9",
     "line 12  L IOD2  TI,1,4.0(L IODX),0.0(L XNT)"),
    ("003051.40", "002601.31 80  007000.22 B0",
     "line 13  M+1,L TAPEC  -STEP REEL COUNTER"),
    ("003052.40", "000000.74 8A  004000.20 50",
     "line 14  L(BU,4),.60(L WORKX)  -GET TYPE"),
    ("003053.40", "000000.60 89  004000.12 F0",
     "line 15  $SF(BU,4),.48(L XNT)  -AND PLACE IN CHANNEL"),
    ("003054.40", "000000.03 85  004000.20 D0",
     "line 16  ST(BU,4),T TYPE(L XIO)"),
    ("003055.40", "000000.34 84  010000.22 B0",
     "line 17  L FOUND  M+1,T UNCT(L XPP)  -STEP UNIT COUNT"),
    ("003056.40", "002601.40 80  011000.20 50",
     "line 18  L(BU,9),L IOSCR,0.0  -ENTER IODSQ IN IOREQ."),
    ("003057.40", "000000.23 85  011000.20 D0",
     "line 19  ST(BU,9),T IODSQ(L XIO)"),
    ("003060.40", "002601.40 80  011000.22 B0",
     "line 20  M+1(BU,9),L IOSCR  -STEP IODSQ."),
    ("003061.40", "000001.13 07",
     "line 21  V+ICR,L XIO,1.0  -STEP IOREQ. INDEX."),
    ("003062.00", "000002.00 83  060000.06 70",
     "line 26  L NON  LF(BU,48),2.0(L IODX)  -IS TYPE DISK"),
    ("003063.00", "002723.00 80  060000.23 10",
     "line 27  KF(BU,48),L DISK"),
    ("003064.00", "003066.36 C6",
     "line 28  BAEZ,L NEW  - DISK----BRANCH"),
    ("003064.40", "002724.00 80  060000.23 10",
     "line 29  KF(BU,48),L TRACK"),
    ("003065.40", "003237.76 C4",
     "line 30  BZAEZ,L NORM  - NON DISK OR TRACK"),
    ("003066.00", "000005.00 83  060000.20 50",
     "line 31  L NEW  L(BU,48),5.0(L IODX)  -IS NUMBER FIELD BLANK"),
    ("003067.00", "002736.00 80  060600.23 10",
     "line 32  KF,L BLANK  [dds from printed p.51]"),
    ("003070.00", "003075.36 C6",
     "line 33  BAEZ,L DSKD  -YES"),
    ("003070.40", "000023.24 30",
     "line 34  LV,L WORKX,L IODX  -IS THE NUMBER FIELD"),
    ("003071.00", "000010.25 02",
     "line 35  LCI,L WORKX,8"),
    ("003071.40", "002601.65 80  006000.06 70",
     "line 36  LF(BU,6),L BLZOR+.2"),
    ("003072.40", "000005.00 8A  006600.23 10",
     "line 37  L DSKC  KF(BU,6,6),5.(L WORKX)"),
    ("003073.40", "003237.76 C4",
     "line 38  BZAEZ,L NORM  -A NON ZERO ENTRY"),
    ("003074.00", "002601.24 B0",
     "line 39  V+,L WORKX,L NO6  -STEP TO NEXT CHAR"),
    ("003074.40", "003072.64 48",
     "line 40  CB,L WORKX,L DSKC"),
    ("003075.00", "000000.77 89  003237.74 0C",
     "line 41  L DSKD  BZB1,L ZBIT(L XNT),L NORM"),
    ("003076.00", "000007.37 02",
     "line 42  LCI,$15,7.0  -NO -- ERROR FLAG 7."),
    ("003076.40", "003241.10 00",
     "line 43  B,L ERROR"),
    ("003077.00", "002601.52 80  001000.00 F0",
     "line 48  L IODTP  CM0000(BU,1),L NTB,0.0  -SET NON-TAPE BIT"),
    ("003100.00", "002565.16 10",
     "line 49  LX,L XSU,L SYMUX  -IS THIS UNIT IN"),
    ("003100.40", "000000.00 87  060000.20 50",
     "line 50  L OOPSU  L(BU,48),0.0(L XSU),0.0"),
    ("003101.40", "003104.74 C6",
     "line 51  BRZZ,L IOD3"),
    ("003102.00", "000005.00 83  060000.21 10",
     "line 52  K(BU,48),5.0(L IODX),0.0"),
    ("003103.00", "003137.76 C6",
     "line 53  BAEZ,L SET  - YES----STEP"),
    ("003103.40", "003100.57 48",
     "line 54  L ETA  CB+,L XSU,L OOPSU"),
    ("003104.00", "003104.04 00",
     "line 55  BD,$  -INTERNAL UNIT TABLE"),
    ("003104.40", "000005.00 83  000000.02 A7",
     "line 56  L IOD3  TI,1,5.0(L IODX),0.0(L XSU)"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.54 ")
finish(fails)
