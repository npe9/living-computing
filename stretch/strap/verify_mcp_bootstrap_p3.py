#!/usr/bin/env python3
"""verify_mcp_bootstrap_p3.py -- MCP's IPL bootstrap, printed page 3
(programs/mcp_bootstrap_p3.strap) against the listing's own printed
machine code.  docs/MCP_Mar63_001-249.pdf PDF p.10, header "PAGE
NUMBER 3".  AGENTS.md rule 3.

CITED BY PRINTED PAGE AND CHECKED BY PDF PAGE.  This listing's
PDF->printed offset is +7 for the bootstrap but is NOT constant across
the two volumes, so every citation here was read off the page's own
"PAGE NUMBER" header rather than computed.

THIRTY-NINE ROWS CARRY MACHINE CODE.  Thirty-eight are checked here.
The thirty-ninth, line 6, is a standoff between the page and
X22-6533; it is named in UNCHECKED below with the whole of the
evidence, and programs/mcp_bootstrap_p3.strap's header has the rest.

RESOLUTION.  Statement column at 600 dpi, BINARY OUTPUT at 900, per
docs/listing_typography.md 11 -- and line 10 is why that rule exists:
its trailing byte reads 80 at 900 dpi and is B0.  The arithmetic
caught it before the eye did.  LVE's operation code is 11011
(X22-6533 DIRECT INDEX ARITHMETIC, bits 23-27), so bits 24-27 are
1011, so the printed nibble must be B.  Re-rendered at 1800 dpi it is
a B, with the left vertical a worn printer drops first.  THE RULE
WORTH CARRYING: decode the opcode field, then look at the glyph.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("programs/mcp_bootstrap_p3.strap").read())

# The eighteen symbols this page defines, at the locations it prints in
# its LOCATION column.  These are genuine: the assembler places them
# from the instruction stream.  The three SYN'd externals -- XIPLBS,
# XERROR, XERRAD -- are NOT here, because a SYN makes its own address
# come out right by construction; each is taken from the page that
# defines it (p.2 line 24, p.5 line 5, p.13 line 37 respectively).
SYMBOLS = {
    "X1":     "000052.40",
    "X1CCW":  "000053.40",
    "XERR00": "000054.40",
    "X71":    "000057.40",
    "XERR02": "000060.40",
    "XERR03": "000061.40",
    "X71CCW": "000062.40",
    "XERR04": "000063.40",
    "X73":    "000066.40",
    "XERR05": "000067.00",
    "X8":     "000070.00",
    "XER05A": "000071.00",
    "XER05B": "000072.00",
    "XER05C": "000073.00",
    "X81":    "000074.00",
    "XER05D": "000075.00",
    "XER05E": "000101.00",
    "X82":    "000102.00",
}

# THE ROW THIS FILE DOES NOT CHECK, kept here so that it is counted
# rather than forgotten:
#
#   000053.40   000017.40 30   000041.21 00   X1 CCW  CCW,15.32,X IPL BS
#
# bits 24-27 print as 0011 where X22-6533's INPUT-OUTPUT OPERATIONS
# format puts the literal 1000.  The channel address (000017.40 = 992
# = 31 << 5) and the entire second half-word (X IPL BS as a word
# address; .21 = unused bit 50, OP 1000 = CCW, then the literal's
# first bit) are both exactly what this assembler emits.  The glyph
# was re-rendered at 1800 dpi beside line 7's 80 and is a 3.
UNCHECKED = 1

ROWS = [
    # ---- FIND IPL CHANNEL NUMBER ----
    ("000052.40", "000053.40 80 023000.22 B0",
     "line 5   X1  M+1(BU,19),X1 CCW  - ADVANCE CHANNEL"),
    # line 6 omitted -- see UNCHECKED above
    ("000054.40", "000551.00 80",
     "line 7   X ERR 00  SIC,X ERR AD"),
    ("000055.00", "000133.03 46",
     "line 8   BEKJZ,X ERROR  -IF EXCHANGE ERROR"),
    ("000055.40", "000041.77 80 000052.74 00",
     "line 9   BZB,X IPL BS+.63,X1  -IS IT IPL CHANNEL"),
    # THE TRAILING BYTE IS B0, NOT 80.  LVE = 11011 at bits 23-27
    # (X22-6533 DIRECT INDEX ARITHMETIC), so bits 24-27 = 1011 = B.
    # Read as 80 at 900 dpi; 1800 dpi and the arithmetic both say B.
    ("000056.40", "000053.77 B0",
     "line 10  LVE,15,X1 CCW  - OBTAIN NUMBER OF IPL CHANNEL"),
    ("000057.00", "000070.10 00",
     "line 11  B,X8  -TO SPACE OVER TAPE MARK"),
    # ---- IO TEST ----
    ("000057.40", "000551.00 80",
     "line 17  X7 1  SIC,X ERR AD"),
    ("000060.00", "000133.03 46",
     "line 18  BEKJZ,X ERROR  -IF EXCHANGE ERROR"),
    ("000060.40", "000551.00 80",
     "line 19  X ERR 02  SIC,X ERR AD"),
    ("000061.00", "000133.03 C6",
     "line 20  BUNRJZ,X ERROR  -UNIT NOT READY REJECT"),
    ("000061.40", "000551.00 80",
     "line 21  X ERR 03  SIC,X ERR AD"),
    ("000062.00", "000133.04 46",
     "line 22  BCBJZ,X ERROR  -IF CHANNEL BUSY REJECT"),
    ("000062.40", "000000.00 8F 000041.21 00",
     "line 23  X7 1 CCW  CCW,0($15),X IPL BS"),
    ("000063.40", "000551.00 80",
     "line 24  X ERR 04  SIC,X ERR AD"),
    ("000064.00", "000133.03 46",
     "line 25  BEKJZ,X ERROR  -IF EXCHANGE ERROR FOR CCW"),
    ("000064.40", "000041.30 80 000062.74 02",
     "line 26  BB,X IPL BS+.24,X7 1 CCW  -IO OPERATION COMPLETED"),
    ("000065.40", "000041.23 80 005000.07 70",
     "line 27  CT0011(BU,5),X IPL BS+.19"),
    ("000066.40", "000000.34 C2",
     "line 28  X7 3  BRZ,0.0  -SUCCESSFUL"),
    ("000067.00", "000551.00 80",
     "line 29  X ERR 05  SIC,X ERR AD"),
    ("000067.40", "000133.10 00",
     "line 30  B,X ERROR  -IO STATUS BIT ON"),
    # ---- SPACE OVER TAPE MARK ----
    # THE FIRST SPFL IN THE CORPUS.  .15 = 001101 at bits 50-55 is
    # unused bit 50, then OP 0110 = CTLSEOP, then the literal's first
    # bit -- so the pseudo-operation IS a CONTROL -- and 000077 in the
    # code field is Reference Manual p.132's "077 Space File".
    ("000070.00", "000000.00 8F 000077.15 00",
     "line 35  X8  SPFL(SEOP),0.0($15)  -SPACE OVER TAPE MARK"),
    ("000071.00", "000551.00 80",
     "line 36  X ER 05A  SIC,X ERR AD"),
    ("000071.40", "000133.03 46",
     "line 37  BEKJZ,X ERROR  -IF EXCHANGE ERROR"),
    ("000072.00", "000551.00 80",
     "line 38  X ER 05B  SIC,X ERR AD"),
    ("000072.40", "000133.03 C6",
     "line 39  BUNRJZ,X ERROR  -IF UNIT NOT READY REJECT"),
    ("000073.00", "000551.00 80",
     "line 40  X ER 05C  SIC,X ERR AD"),
    ("000073.40", "000133.04 46",
     "line 41  BCBJZ,X ERROR  -IF CHANNEL BUSY REJECT"),
    ("000074.00", "000000.00 8F 000041.21 00",
     "line 42  X8 1  CCW,0($15),X IPL BS  -GET STATUS BITS"),
    ("000075.00", "000551.00 80",
     "line 43  X ER 05D  SIC,X ERR AD"),
    ("000075.40", "000133.03 46",
     "line 44  BEKJZ,X ERROR  -IF EXCHANGE ERROR"),
    ("000076.00", "000041.30 80 000074.34 02",
     "line 45  BB,X IPL BS+.24,X 8 1  -IF SEOP OFF"),
    ("000077.00", "000041.25 80 000101.34 04",
     "line 46  BZBZ,X IPL BS+.21,XER05E  -OFF * IF EE ON"),
    ("000100.00", "000041.23 80 000102.34 00",
     "line 47  BZB,X IPL BS+.19,X8 2  -YES*TEST FOR UK"),
    ("000101.00", "000551.00 80",
     "line 48  X ER 05E  SIC,X ERR AD"),
    ("000101.40", "000133.10 00",
     "line 49  B,X ERROR  -ERROR IN SPACING"),
    # REL WITH NO SECOND OPERAND.  Reference Manual p.111: RELEASE's
    # second effective address is "not used; ignored".  The listing
    # prints 000000 in the field and writes no operand for it.
    ("000102.00", "000000.00 8F 000000.33 00",
     "line 50  X8 2  REL(SEOP),0.0($15)  -CLEAR EE AND EOP STATUS BIT"),
    ("000103.00", "000066.40 80",
     "line 51  SIC,X7 3"),
    ("000103.40", "000057.50 00",
     "line 52  B,X7 1  - TO IO TEST"),
]

print(f"NOTE MCP p.3 {len(ROWS)} rows checked, {UNCHECKED} row (line 6) "
      f"deliberately unchecked -- see this file's UNCHECKED comment")
finish(check_rows(prog, ROWS, SYMBOLS, label="MCP p.3 "))
