#!/usr/bin/env python3
"""verify_mcp_bootstrap_p23.py -- MCP INITIALIZATION, printed page 23:
the IPL DATE constant's validation and the I/O status report loop
(../decks/mcp_bootstrap_p23.strap).  docs/MCP_Mar63_001-249.pdf PDF
p.30, header "PAGE NUMBER 23".  AGENTS.md rule 3.

Fifty-four printed rows with binary output.

>>> THE MONTH AND DAY LIMITS ARE PRINTED IN HEXADECIMAL -- (16)13 and
(16)32 -- and that is not an arbitrary radix.  The characters being
compared are a PAIR of BCD digits packed one per nibble, so 0x13 IS
the digit pair 1,3 and 0x32 IS 3,2.  The comparison is on the digits;
hexadecimal is the only radix in which the constant looks like the
number it bounds.  Printed p.22 does the same with (16)24 and (16)60
for hours, minutes and seconds. <<<

FOUR PAGES NOW SHARE X LR IN: printed p.21 reserved it, p.22 read the
operator's reply into it, and this page reads the date half and then
the channel number out of it at +1.24.

THREE FORWARD REFERENCES WERE GUESSED ".40" AND ARE ".00", and these
rows caught all three.  The branch-address field is NINETEEN bits and
bit 18 -- the top bit of the printed ".bb" group -- is the HALF-WORD
selector: 001207.36 has it CLEAR (left half of 001207) while
001225.76 has it SET (right half of 001225).  Defaulting an unknown
forward reference to ".40" is a coin flip.

X VDATE SITS 0o70 BITS PAST X VTIME.  p.22 line 35's immediate is
001242.02 and line 15's here is 001242.70, so the two constants are
in the same word region on a page nobody has transcribed yet -- which
is a prediction that page will have to satisfy.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p23.strap").read())

SYMBOLS = {
    "XVLP":   "001130.00",
    "XVCONT": "001132.40",
    "XVIORP": "001152.00",
    "XIC1":   "001153.40",
    "XICA":   "001155.40",
    "XIOAA":  "001156.40",
    "XICB":   "001162.40",
    "XIO2":   "001163.00",
    "XIO2A":  "001166.00",
}

_L = "000000.04 81 104000.20 50"      # L(BU,4)(V+I),.4($1)
_S6 = "000000.06 82 104000.20 D0"     # ST(BU,4)(V+I),.6($2)
_S12 = "000000.14 82 104000.20 D0"    # ST(BU,4)(V+I),.12($2)
_L8 = "000000.10 81 110000.20 50"     # L(BU,8)(V+I),.8($1)
_SIC = "000066.40 80"                 # SIC,X7 3
_BX71 = "000057.50 00"                # B,X7 1
_LVI = "001034.43 01"                 # LVI,$1,XLRIN+.32

ROWS = [
    ("001121.40", _LVI,                      "line 1   LVI,$1,XLRIN+.32"),
    ("001122.00", _L8,
     "line 2   L(BU,8)(V+I),.8($1)  - TESTS FOR VALID COMBINATIONS"),
    ("001123.00", "046000.00 80 410000.23 10", "line 3   KFI(BU,8),(16)13"),
    ("001124.00", "001225.76 40",            "line 4   BZAL,XVTDER"),
    ("001124.40", _L8,                       "line 5   L(BU,8)(V+I),.8($1)"),
    ("001125.40", "144000.00 80 410000.23 10", "line 6   KFI(BU,8),(16)32"),
    ("001126.40", "001225.76 40",            "line 7   BZAL,XVTDER"),
    ("001127.00", _LVI,                      "line 8   LVI,$1,XLRIN+.32"),
    ("001127.40", "000006.07 02",            "line 9   LCI,$3,6.0"),
    ("001130.00", _L,                        "line 10  XVLP  L(BU,4)(V+I),.4($1)"),
    ("001131.00", "000000.00 80 404000.23 10", "line 11  KFI(BU,4),0"),
    ("001132.00", "001207.36 C2",
     "line 12  BAE,XVZER1  - REPLACE WITH BCD ZERO"),
    ("001132.40", "001130.06 48",            "line 13  XVCONT  CB,$3,XVLP"),
    ("001133.00", _LVI,                      "line 14  LVI,$1,XLRIN+.32"),
    ("001133.40", "001242.70 80 430024.20 50", "line 15  LI(BU,24),XVDATE,40"),
    ("001134.40", "000011.04 30",            "line 16  LV,$2,$R"),
    ("001135.00", "000000.02 82 101000.20 50", "line 17  L(BU,1)(V+I),.2($2)"),
    ("001136.00", _L,                        "line 18  L(BU,4)(V+I),.4($1)"),
    ("001137.00", _S6,
     "line 19  ST(BU,4)(V+I),.6($2)  -STORE IN DATE SLOT"),
    ("001140.00", _L,                        "line 20  L(BU,4)(V+I),.4($1)"),
    ("001141.00", _S12,                      "line 21  ST(BU,4)(V+I),.12($2)"),
    ("001142.00", _L,                        "line 22  L(BU,4)(V+I),.4($1)"),
    ("001143.00", _S6,                       "line 23  ST(BU,4)(V+I),.6($2)"),
    ("001144.00", _L,                        "line 24  L(BU,4)(V+I),.4($1)"),
    ("001145.00", _S12,                      "line 25  ST(BU,4)(V+I),.12($2)"),
    ("001146.00", _L,                        "line 26  L(BU,4)(V+I),.4($1)"),
    ("001147.00", _S6,                       "line 27  ST(BU,4)(V+I),.6($2)"),
    ("001150.00", _L,                        "line 28  L(BU,4)(V+I),.4($1)"),
    ("001151.00", _S6,                       "line 29  ST(BU,4)(V+I),.6($2)"),
    ("001152.00", "001034.35 80 001417.34 00",
     "line 30  XVIORP  BZB,X LR IN+.29,X 20B  - IF I/O STATUS REPORT DESIRED"),
    ("001153.00", "001166.10 00",
     "line 31  B,X IO 2A  - YES TO CHANGE TABLES"),
    ("001153.40", "000000.00 8F 001410.13 00",
     "line 32  XIC 1  W(SEOP),0.0($15),X IO CW  -YES*REQUEST NEXT IO STATUS"),
    ("001154.40", _SIC,                      "line 34  SIC,X7 3"),
    ("001155.00", _BX71,                     "line 35  B,X7 1  -TO IO TEST"),
    ("001155.40", "000000.00 8F 000041.21 00",
     "line 36  XIC A  CCW,0.0($15),X IPL BS  -GET STATUS BITS"),
    ("001156.40", "000551.00 80",            "line 37  XIO AA  SIC,X ERR AD"),
    ("001157.00", "000133.03 46",            "line 38  BEKJZ,X ERROR  -IF EKJ"),
    ("001157.40", "000041.27 80 001155.74 00",
     "line 39  BZB,X IPL BS+.23,X IO A"),
    ("001160.40", "000000.00 8F 000000.33 00",
     "line 40  REL(SEOP),0.0($15)  - CLEAR CS STATUS BIT"),
    ("001161.40", _SIC,                      "line 41  SIC, X7 3"),
    ("001162.00", _BX71,                     "line 42  B,X7 1  - IO TEST"),
    ("001162.40", "001163.10 00",            "line 43  XIC B  B,XIO 2"),
    ("001163.00", "000000.00 8F 001044.11 00",
     "line 44  X IO 2  RD(SEOP),0.0($15),X D CW2  -GET CHANNEL AND UNIT"),
    ("001164.00", _SIC,                      "line 46  SIC,X7 3"),
    ("001164.40", _BX71,                     "line 47  B,X7 1  -TO IO TEST"),
    ("001165.00", "001034.35 80 001417.34 00",
     "line 48  BZB,X LR IN+.29,X20B  - IF DONE OUT"),
    ("001166.00", "001035.30 80 010427.24 30",
     "line 49  XIO 2A  LCV(DU,8),X LR IN+1.24,46  -CONVERT CHANNEL NUMBER"),
    ("001167.00", "000011.34 30",            "line 50  LV,$14,$R  -GET CHANNEL NUMBER"),
    ("001167.40", "002152.34 B0",            "line 51  V+,$14,SXCHAN  -GET CST SLOT"),
    ("001170.00", "000000.33 8E 001176.34 00",
     "line 52  BZB,.27($14),X IO 4  -IF MULTI UNIT CHANNEL"),
    ("001171.00", "001035.74 80 001177.74 02",
     "line 53  BB,X LR IN +1.60,XIO5  -YES* IF ENTIRE CHANNEL DOWN"),
    ("001172.00", "000000.34 3E",            "line 54  LV,$14,0.0($14)  -GET UST BASE"),
    ("001172.40", "001035.75 80 003000.20 50",
     "line 55  L(BU,3),XLRIN+1.61  -ENTER UNIT NUMBER"),
    ("001173.40", "000036.00 80 022000.22 90",
     "line 56  M+MG(BU,18),$14  -COMPUTE UST ENTRY ADDRESS"),
]

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP p.23 "))
