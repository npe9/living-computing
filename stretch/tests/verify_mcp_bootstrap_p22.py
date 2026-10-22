#!/usr/bin/env python3
"""verify_mcp_bootstrap_p22.py -- MCP INITIALIZATION, printed page 22:
"OPERATOR STATUS REPORT FOR IO" (../decks/mcp_bootstrap_p22.strap).
docs/MCP_Mar63_001-249.pdf PDF p.29, header "PAGE NUMBER 22".
AGENTS.md rule 3.

Fifty printed rows with binary output.

WHAT THE PAGE DOES: it READS the IPL options the operator typed and
validates them.  Six characters of IPL TIME, each tested for being a
valid digit and then in PAIRS against (16)24 and (16)60 -- hours
under twenty-four, minutes and seconds under sixty -- then the same
digit validation over the IPL DATE in the second half of the buffer.

THREE PAGES SHARE ONE BUFFER.  Line 5 reads into X LR IN, which
printed p.21 line 26 RESERVED with "DR(BU),(3)", using X D CW 2,
which p.21 line 31 BUILT.  And printed p.21 line 24's "B,XIC" is what
branches here: X IC at 001052.00 was recovered from that branch's
encoding before this page was opened, and it is exact.

>>> THE PAGE FOUND AN ASSEMBLER GAP, which is the useful part of this
file.  Lines 20, 23 and 26 are "KFI(BU,8),(16)24" and
"KFI(BU,8),(16)60" -- a RADIX-SIXTEEN literal in an IMMEDIATE
operand.  tokenize_expr capped the "(R)" radix at TEN, so the page
would not assemble at all, while parse_dd_value had always accepted
any radix: the same literal was legal as data and illegal as an
operand.  The cap is now sixteen and the digits A-F are matched only
after a prefix has introduced them, so a bare identifier can never be
read as hexadecimal. <<<

WHAT MAKES THE FIX EVIDENCE RATHER THAN A GUESS: the two rows print
110000.00 80 410000.23 10 and 300000.00 80 410000.23 10, whose
address fields are 0x24 and 0x60 left-justified in the 24-bit field.
Had the prefix meant anything else, those two words would not match.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p22.strap").read())

SYMBOLS = {
    "XIC":    "001052.00",
    "XVLOOP": "001057.40",
    "XVBACK": "001072.40",
    "XVLOP2": "001073.40",
    "XVCONS": "001076.00",
    "XVLOPS": "001116.40",
}

_L = "000000.04 81 104000.20 50"      # L(BU,4)(V+I),.4($1)
_S6 = "000000.06 82 104000.20 D0"     # ST(BU,4)(V+I),.6($2)
_S12 = "000000.14 82 104000.20 D0"    # ST(BU,4)(V+I),.12($2)

ROWS = [
    ("001052.00", "000000.00 8F 001044.11 00",
     "line 5   X IC  RD(SEOP),0.0($15),X D CW2  -GET IPL OPTIONS"),
    ("001053.00", "000066.40 80",            "line 6   SIC,X7 3"),
    ("001053.40", "000057.50 00",            "line 7   B,X7 1  -IO TEST"),
    ("001054.00", "000006.07 02",            "line 9   LCI,$3,6.0"),
    ("001054.40", "001034.03 01",            "line 10  LVI,$1,XLRIN"),
    ("001055.00", "001034.00 80 000000.20 50", "line 11  L(BU,64),XLRIN"),
    ("001056.00", "000000.00 80 430024.23 10",
     "line 12  KFI(BU,24),0,40  -NO TIME ENTERED"),
    ("001057.00", "001211.76 C2",            "line 13  BAE,XVNOTM"),
    ("001057.40", _L,
     "line 14  XVLOOP  L(BU,4)(V+I),.4($1)  -TEST FOR VALID CHARACTER."),
    ("001060.40", "440000.00 80 404000.23 10", "line 15  KFI(BU,4),9"),
    ("001061.40", "001225.77 42",            "line 16  BAH,XVTDER"),
    ("001062.00", "001057.46 48",            "line 17  CB,3,XVLOOP"),
    ("001062.40", "001034.03 01",            "line 18  LVI,$1,XLRIN"),
    ("001063.00", "000000.10 81 110000.20 50",
     "line 19  L(BU,8)(V+I),.8($1)  -TEST FOR VALID COMBINATIONS."),
    ("001064.00", "110000.00 80 410000.23 10", "line 20  KFI(BU,8),(16)24"),
    ("001065.00", "001225.76 40",            "line 21  BZAL,XVTDER"),
    ("001065.40", "000000.10 81 110000.20 50", "line 22  L(BU,8)(V+I),.8($1)"),
    ("001066.40", "300000.00 80 410000.23 10", "line 23  KFI(BU,8),(16)60"),
    ("001067.40", "001225.76 40",            "line 24  BZAL,XVTDER"),
    ("001070.00", "000000.10 81 110000.20 50", "line 25  L(BU,8)(V+I),.8($1)"),
    ("001071.00", "300000.00 80 410000.23 10", "line 26  KFI(BU,8),(16)60"),
    ("001072.00", "001225.76 40",            "line 27  BZAL,XVTDER"),
    ("001072.40", "001034.03 01",            "line 28  XVBACK  LVI,$1,XLRIN"),
    ("001073.00", "000006.07 02",            "line 29  LCI,$3,6.0"),
    ("001073.40", _L,                        "line 30  XVLOP2  L(BU,4)(V+I),.4($1)"),
    ("001074.40", "000000.00 80 404000.23 10", "line 31  KFI(BU,4),0"),
    ("001075.40", "001204.76 C2",
     "line 32  BAE,XVZER  -REPLACE WITH BCD ZERO"),
    ("001076.00", "001073.46 48",            "line 33  XVCONS  CB,$3,XVLOP2"),
    ("001076.40", "001034.03 01",            "line 34  LVI,$1,XLRIN"),
    ("001077.00", "001242.02 80 430024.20 50", "line 35  LI(BU,24),XVTIME,40"),
    ("001100.00", "000011.04 30",            "line 36  LV,$2,$R"),
    ("001100.40", "000000.02 82 101000.20 50", "line 37  L(BU,1)(V+I),.2($2)"),
    ("001101.40", _L,                        "line 38  L(BU,4)(V+I),.4($1)"),
    ("001102.40", _S6,
     "line 39  ST(BU,4)(V+I),.6($2)  - STORE IN TIME SLOT"),
    ("001103.40", _L,                        "line 40  L(BU,4)(V+I),.4($1)"),
    ("001104.40", _S12,                      "line 41  ST(BU,4)(V+I),.12($2)"),
    ("001105.40", _L,                        "line 42  L(BU,4)(V+I),.4($1)"),
    ("001106.40", _S6,                       "line 43  ST(BU,4)(V+I),.6($2)"),
    ("001107.40", _L,                        "line 44  L(BU,4)(V+I),.4($1)"),
    ("001110.40", _S12,                      "line 45  ST(BU,4)(V+I),.12($2)"),
    ("001111.40", _L,                        "line 46  L(BU,4)(V+I),.4($1)"),
    ("001112.40", _S6,                       "line 47  ST(BU,4)(V+I),.6($2)"),
    ("001113.40", _L,                        "line 48  L(BU,4)(V+I),.4($1)"),
    ("001114.40", _S6,                       "line 49  ST(BU,4)(V+I),.6($2)"),
    ("001115.40", "000006.07 02",            "line 51  LCI,$3,6.0"),
    ("001116.00", "001034.43 01",            "line 52  LVI,$1,XLRIN+.32"),
    ("001116.40", _L,
     "line 53  XVLOPS  L(BU,4)(V+I),.4($1)  - TESTS FOR VALID CHARACTERS"),
    ("001117.40", "440000.00 80 404000.23 10", "line 54  KFI(BU,4),9"),
    ("001120.40", "001225.77 42",            "line 55  BAH,XVTDER"),
    ("001121.00", "001116.46 48",            "line 56  CB,$3,XVLOPS"),
]

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP p.22 "))
