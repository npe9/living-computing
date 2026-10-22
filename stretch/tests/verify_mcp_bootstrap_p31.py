#!/usr/bin/env python3
"""verify_mcp_bootstrap_p31.py -- MCP INITIALIZATION, printed page 31:
reading the installation's operating mode off the MCPP card, and the
bypass-mode unassign loop (../decks/mcp_bootstrap_p31.strap).
docs/MCP_Mar63_001-249.pdf PDF p.38, header "PAGE NUMBER 31".
AGENTS.md rule 3.

Thirty-five printed rows with binary output and thirteen symbol
locations -- every row on the page.

>>> NO ASSEMBLER WORK, for the fourth page in five.  The one form
this page introduces, PROGRESSIVE INDEXING, has been in the
assembler since the I-Box decks and this is simply the first MCP
page to use it:

  line 6  CT0000(V+I)(BU,8),+1.44($4)  -> 000001.54 84 110000.01 70
  line 7  L(V+I)(BU,48),.48($4)        -> 000000.60 84 160000.20 50

C28-6129 printed p.4 writes the format as "OP1(OP2)(dds), A24(I),
OF7(I')" -- a secondary operation in its own parentheses -- and the
MCPP card is walked field by field by the instruction that reads it.

>>> AND THE PAGE SETTLES ANOTHER C.  Line 24's trailing byte prints
"0C" at 900 dpi and was transcribed "00" from the 600 dpi render.
It is 0C, and the C is real: "BZB1" differs from "BZB" exactly in
bits 28-31, which is where the "set the bit to one" lives, and line
32's plain BZB two rows later prints "00" in the same column.  The
assembler refused the 00 reading before the higher render was taken.
Third time this page family has turned on a C (see
docs/listing_typography.md 13b) and the second time the ASSEMBLER
found it rather than the eye. <<<

REACHED BY BRANCH FROM p.30, twice: that page's line 19
"BZB,X LR IN+.31,X 32" and line 22 "BAH,X32" both compile X32 =
001601.00, which is this page's first row, and p.30's last data byte
ends at 001600.70 -- so the pages are contiguous as well as linked.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p31.strap").read())

SYMBOLS = {
    "X32":    "001601.00",
    "X322":   "001604.40",
    "X323":   "001605.40",
    "X323A":  "001613.00",
    "X323B":  "001614.00",
    "X323C":  "001615.00",
    "X33":    "001616.00",
    "X33AA":  "001617.00",
    "X331":   "001617.40",
    "X331A":  "001620.00",
    "X332":   "001620.40",
    "X334":   "001623.40",
    "X335":   "001624.40",
}

ROWS = [
    # ---- from the MCPP card, determine the installation mode ----
    ("001601.00", "000027.10 30",              "line 5   X32  LV,$4,$7"),
    ("001601.40", "000001.54 84 110000.01 70",
     "line 6   CT0000(V+I)(BU,8),+1.44($4)  -ADVANCE TO CARD TYPE FIELD"),
    ("001602.40", "000000.60 84 160000.20 50",
     "line 7   L(V+I)(BU,48),.48($4)  -ENTER CARD TYPE FIELD"),
    ("001603.40", "001747.00 80 060000.23 10", "line 8   KF(BU,48),X MCPP"),
    ("001604.40", "000551.00 80",              "line 9   X32 2  SIC,X ERR AD"),
    ("001605.00", "000133.36 C0",
     "line 10  BZAE,X ERROR  - IF MCPP CARD"),
    ("001605.40", "000000.00 84 030000.20 50",
     "line 11  X32 3  L(BU,24),0.0($4)  -GET MCP INSTALATION MODE FIELD"),
    ("001606.40", "002144.00 80 030000.23 10", "line 12  KF(BU,24),X ONOV"),
    ("001607.40", "001647.76 C2",
     "line 13  BAE,X35  -IF ON LINE OVERLAPPED"),
    ("001610.00", "002145.00 80 030000.23 10", "line 14  KF(BU,24),X OFOV"),
    ("001611.00", "001614.36 C2",
     "line 15  BAE,X 32 3 B  -IF OFF LINE OVERLAPPED"),
    ("001611.40", "002146.00 80 030000.23 10", "line 16  KF(BU,24),X BYPS"),
    ("001612.40", "001615.36 C2",              "line 17  BAE,X32 3C  - IF BYPASS"),
    ("001613.00", "000551.00 80",              "line 18  X32 3 A  SIC,X ERR AD"),
    ("001613.40", "000133.10 00",
     "line 19  B,X ERROR  -INCORRECT MODE ENTRY"),
    ("001614.00", "002151.11 80 001661.74 0C",
     "line 24  X32 3B  BZB1,S COM RG+.9,X36  -MODE CODE TO 01"),
    ("001615.00", "002151.10 80 001000.36 F0",
     "line 25  X32 3C  CM1111(BU,1),S COM RG+.8  -MODE CODE TO 10"),
    # ---- bypass mode: delete the spool messages, unassign units ----
    ("001616.00", "002151.10 80 001660.34 00",
     "line 32  X33  BZB,S COM RG+.8,X35A  -IF BYPASS"),
    ("001617.00", "000002.01 02",
     "line 33  X33 A A  LCI,$0,2  -YES*SET UP TO DELETE 2 MSG"),
    ("001617.40", "002153.74 30",
     "line 34  X 33 1  LV,$14,S R TAPE  -BYPASS GET SPOOL REAL TYPE IOD NUMBER"),
    ("001620.00", "002153.34 B0",
     "line 35  X33 1 A  V+,$14,S BA MCP  -SPOOL TAPE ENTRY IN IO LOC TABLE"),
    ("001620.40", "000000.30 1E",
     "line 36  X33 2  LX,$12,0.0($14)  -GET UAT ADD FOR DELET OF MOUNT MSG"),
    ("001621.00", "000000.34 1E",
     "line 37  LX,$14,0.0($14)  -GET UAT ADDRESS IN DUPLICATE"),
    ("001621.40", "000000.32 1E",
     "line 38  LX,$13,0.0($14)  -GET CHANNEL NUMBER"),
    ("001622.00", "000035.32 B0",              "line 39  V+,$13,$13  -DOUBLE CHANNEL ="),
    ("001622.40", "000000.74 3E",
     "line 40  LV,$14,.32($14)  -GET UNIT NUMBER"),
    ("001623.00", "002152.32 B0",              "line 41  V+,$13,S X CHAN  -CST ENTRY"),
    ("001623.40", "000000.32 3D",
     "line 42  X33 4  LV,$13,0.0($13)  -GET UST ENTRY"),
    ("001624.00", "000036.32 B0",              "line 43  V+,$13,$14  -UST ENTRY"),
    ("001624.40", "000000.35 8D 001000.36 F0",
     "line 44  X33 5  CM1111(BU,1),.29($13)  -ASSIGNED BIT OFF"),
    ("001625.40", "000000.40 8D 001000.00 F0",
     "line 45  CM0000(BU,1),.32($13)  -OWNERSHIP BIT OFF"),
    ("001626.40", "000000.63 8D 001000.00 F0",
     "line 46  CM0000(BU,1),.51($13)  -MOUNT BIT OFF"),
    ("001627.40", "000000.65 8D 001000.00 F0",
     "line 47  CM0000(BU,1),.53($13)  -SI MMT OFF"),
    ("001630.40", "000000.32 8D 001000.00 F0",
     "line 48  CM0000(BU,1),.26($13)  -STATI OFF"),
    ("001631.40", "000000.33 8D 001000.36 F0",
     "line 49  CM1111(BU,1),.27($13)  -DISP TO 1"),
]

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP p.31 "))
