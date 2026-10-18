#!/usr/bin/env python3
"""verify_mcp_bootstrap_p18.py -- MCP INITIALIZATION, printed page 18:
the UNIT STATUS TABLE half of the IOCD processing
(../decks/mcp_bootstrap_p18.strap).  docs/MCP_Mar63_001-249.pdf PDF
p.25, header "PAGE NUMBER 18".  AGENTS.md rule 3.

Twenty-eight printed rows with binary output.

THE PAGE FOUND AN ASSEMBLER GAP, and it is the useful part of this
file.  Line 34 is "LFI(BU,18),8.0", the first LFI in this corpus.
LF is the connective C0011; C22-6531 Appendix A printed p.58 footnote
10 says the connective mnemonics are "also subject to Footnote 3",
and footnote 3 is the "I" suffix for immediate addressing.
strap_asm.py stripped that suffix only for VFL_INT_CODES operations,
so LFI raised a KeyError.

What makes the fix evidence rather than a guess: assembled as plain
LF, the word came out 000010.00 80 **0**22000.06 70 against the
listing's 000010.00 80 **4**22000.06 70.  Sixty-three of sixty-four
bits already correct, and the field that differed is P (bits 32-34),
whose value is 4 for immediate addressing and 0 for direct.  Twenty-
seven of this page's twenty-eight rows passed before the change and
the twenty-eighth is the one that named it.

THE FORWARD REFERENCE IS X18, line 2's branch target, and this is a
page where a forward reference is cheap to check later: it must be
000740.40, the half-word immediately after line 45.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p18.strap").read())

SYMBOLS = {
    "X141":   "000714.00",
    "X15":    "000717.00",
    "XERR18": "000722.40",
    "X151":   "000723.40",
    "X152":   "000724.40",
    "X16":    "000727.40",
    "X161":   "000731.40",
    "X17":    "000736.00",
    "X171":   "000737.00",
}

ROWS = [
    ("000713.00", "777777.77 81 000740.74 00",
     "line 2   BZB,-.1($1),X18  -TAPE EQUIPMENT TYPE ENTRY"),
    ("000714.00", "000010.37 02",
     "line 4   X14 1  LCI,$15,8.0  -UST ENTRY COUNTER"),
    ("000714.40", "000000.37 33",
     "line 5   SV,$15,0.0($3)  -INSERT UNIT STATUS TABLE ADDRESS IN CST"),
    ("000715.00", "000000.35 83 001000.00 F0",
     "line 7   CM0000(BU,1),.29($3)  -TURN OFF MEANINGLESS ASSIGN BIT"),
    ("000716.00", "000000.33 83 001000.36 F0",
     "line 9   CM1111(BU,1),.27($3)  -YES * MULTI BIT TO ON IN CST"),
    ("000717.00", "000000.14 84 114000.07 70",
     "line 13  X15  CT0011(V+I)(BU,12),.12($4)  -TEST UNIT AVAILABLE FIELD"),
    ("000720.00", "000731.74 C2",
     "line 14  BRZ,X 16 1  -IF NULL THEN DONE WITH MULTI-UNIT IOCD"),
    ("000720.40", "777777.66 84 000724.74 02",
     "line 16  BB,0.0-.10($4),X152  -UNIT AVAILABLE"),
    ("000721.40", "777777.64 84 000723.74 02",
     "line 17  BB,0.0-.12($4),X151  -IF UNIT NOT AVAILABLE SET IT NOT "
     "AVAILABLE BIT"),
    ("000722.40", "000551.00 80", "line 19  XERR 18  SIC,XERRAD"),
    ("000723.00", "000133.10 00",
     "line 20  B,X ERROR  -IOCD PUNCHED INCORRECTLY"),
    ("000723.40", "000000.34 8F 001000.36 F0",
     "line 21  X15 1  CM1111(BU,1),.28($15)  -UNIT AVAILABLE BIT TO ON"),
    ("000724.40", "000000.35 8F 001000.36 F0",
     "line 22  X15 2  CM1111(BU,1),.29($15)  -UNIT NOT ASSIGNED BIT TO ON"),
    ("000725.40", "000000.33 8F 001000.36 F0",
     "line 23  CM1111(BU,1),.27($15)  -TAPE DISPOSITION BIT TO ON"),
    ("000726.40", "000000.47 8F 001000.36 F0",
     "line 24  CM1111(BU,1),.39($15)  -SELECT STATUS ON"),
    ("000727.40", "000717.37 48",
     "line 28  X16  CB+,$15,X15  -IF PROCESSED EIGHT UNITS"),
    ("000730.00", "000000.73 83 001000.36 F0",
     "line 30  CM1111(BU,1),.59($3)  -UNIT COUNT IN CST TO 8"),
    ("000731.00", "000737.10 00", "line 31  B,X17 1  -TO SET UP FOR NEXT CARD"),
    ("000731.40", "000010.37 0A", "line 32  X16 1  KCI,$15,8.0"),
    ("000732.00", "000736.32 C2",
     "line 33  BXE,X 17  -NO UNITS AT ALL ON MULTI CHANNEL"),
    # THE ROW THAT NAMED THE GAP -- see the module docstring.  The P
    # field is 4 (immediate); plain LF would print 022000.06 here.
    ("000732.40", "000010.00 80 422000.06 70", "line 34  LFI(BU,18),8.0"),
    ("000733.40", "000037.34 80 022000.30 10",
     "line 35  -(BU,18),$15+.28  -COMPUTE THE NUMBER OF UNITS IN UST"),
    ("000734.40", "000000.73 83 004000.20 D0",
     "line 37  ST(BU,4),.59($3)  -INSERT NUMBER OF UNITS"),
    ("000735.40", "000737.10 00", "line 38  B,X17 1  -TO SET UP FOR NEXT CARD"),
    ("000736.00", "000000.00 83 021000.00 F0",
     "line 42  X 17  CM0000(BU,17),0.0($3)  -CLEAR CST ADDRESS IN SCT ENTRY"),
    ("000737.00", "000017.33 05", "line 43  X 17 1  V+I,$13,15.0"),
    ("000737.40", "000035.10 30",
     "line 44  LV,$4,$13  -ENTER ADDRESS OF NEXT CARD"),
    ("000740.00", "000670.50 00", "line 45  B,X13 1  -PROCESS NEXT CARD"),
]

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP p.18 "))
