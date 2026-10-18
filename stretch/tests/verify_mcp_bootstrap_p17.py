#!/usr/bin/env python3
"""verify_mcp_bootstrap_p17.py -- MCP INITIALIZATION, printed page 17,
"PROCESS IOCD CARDS SETTING UP CST AND LST"
(../decks/mcp_bootstrap_p17.strap).  docs/MCP_Mar63_001-249.pdf PDF
p.24, header "PAGE NUMBER 17".  AGENTS.md rule 3.

Forty-two printed rows with binary output, and the densest VFL on any
MCP page read so far: three connectives in their indexed progressive
form (CT0111(V+I), CT0011(V+I), KF(V+I)), two CM1111 and a CM0000
against single bits, an LCV with a decimal-unsigned (DU,8,4) mode and
a byte-size-4 radix conversion, and a load with a NEGATIVE offset
(line 53's "-.5($1)", which prints 777777.73 as its address field).
Every one of them has to reproduce both half-words.

ONE GLYPH CORRECTION IS BAKED INTO THIS FILE, line 42: 000025.06 B0,
not 80.  It read as 80 at 200 dpi and again at 900 dpi; the assembler
disagreeing is what caught it, and 1800 dpi settled it.  That is the
8/B hazard of docs/listing_typography.md item 11 for the third time,
and the first time a 900-dpi render was already in hand and the eye
still supplied the expected glyph -- the row sits in a column where
nearly every neighbour genuinely is 80.

THE PAGE IS ALSO THE ANSWER TO "WHICH DEVICES".  MCP does not know
its own configuration; it reads it off IOCD cards, one per unit,
converts the channel number out of Hollerith, and looks the two-letter
equipment code up in X EQP T.  So what the model must present is
whatever the IOCD deck says it presents.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p17.strap").read())

SYMBOLS = {
    "X13":    "000655.00",
    "X13AA":  "000660.00",
    "XER16C": "000661.40",
    "X13AA1": "000662.40",
    "X13A":   "000665.40",
    "X131":   "000670.40",
    "X131A":  "000671.40",
    "X132":   "000674.00",
    "X132AA": "000676.00",
    "X132A":  "000702.00",
    "X133":   "000702.40",
    "X134":   "000704.40",
    "X135":   "000706.40",
    "X136":   "000711.00",
}

ROWS = [
    # ---- clear the working area ----
    ("000655.00", "001750.03 02",
     "line 5   X13  LCI,$1,1000.0  -SIZE OF WORKING AREA TO BE USED"),
    ("000655.40", "011406.22 00",
     "line 6   Z,X BUFER  -CLEAR FIRST WORD OF BUFFER"),
    ("000656.00", "011406.00 80 011407.02 20",
     "line 7   T,$1,X BUFER,X BUFER+1.0  -CLEAR 1000 WORDS"),
    ("000657.00", "005466.11 01",
     "line 8   LVI,$4,X IN END  -END OF ASSEMBLED AND MOVE MCP IPL"),
    # ---- find the first IOCD card ----
    ("000657.40", "000016.11 02",
     "line 12  LCI,$4,14  -SET UP TO TEST 14 WORDS FOR FIRST IOCD"),
    ("000660.00", "000001.54 84 000662.74 02",
     "line 13  X13 A A  BB,1.44($4),X13 A A1  -IF ZONE BIT OF IOCD"),
    ("000661.00", "000660.11 48",
     "line 14  CB+,$4,X13 A A  -IF SEARCH FRUITLESS"),
    ("000661.40", "000551.00 80", "line 15  X ER 16C  SIC,X ERR AD"),
    ("000662.00", "000133.10 00", "line 16  B,X ERROR  -NO IOCD DETECTED"),
    # ---- preset the CST ----
    ("000662.40", "000024.32 30", "line 17  X13 A A1  LV,$13,$4"),
    ("000663.00", "011406.13 01", "line 18  LVI,$5,X BUFER"),
    ("000663.40", "000025.36 30", "line 19  LV,$15,$5"),
    ("000664.00", "000100.37 05",
     "line 20  V+I,$15,64.0  -BASE OF AREA CONTAINING UST"),
    ("000664.40", "000037.34 30",
     "line 21  LV,$14,$15  -SAVE BASE OF UST AREA"),
    ("000665.00", "000077.03 02",
     "line 22  LCI,$1,63.0  -INITIALIZE TO PRESET 64 WORDS"),
    ("000665.40", "000000.31 85 001000.36 F0",
     "line 23  X13 A  CM1111(BU,1),.25($5)  -CHANNEL NOT AVAILABLE "
     "BIT TO ON"),
    ("000666.40", "000000.35 85 001000.36 F0",
     "line 24  CM1111(BU,1),.29($5)  -NOT ASSIGNED BIT ON IN CST"),
    ("000667.40", "000000.00 85 000001.02 25",
     "line 25  T,$1,0.0($5),1.0($5)  -ALL CST ENTRIES TO NOT AVAILABLE"),
    # ---- convert one card's channel number ----
    ("000670.40", "000001.54 84 110000.17 70",
     "line 26  X13 1  CT0111(V+I)(BU,8),1.44($4)  -ADVANCE TO NEX "
     "FIELD * CARD TYPE"),
    ("000671.40", "000000.62 84 160000.20 50",
     "line 28  X13 1A  L(V+I)(BU,48),.48+.2($4)  -ENTER COLUMN "
     "CONTAINING IOCD"),
    ("000672.40", "001747.60 80 060000.23 10", "line 30  KF(BU,48),X IOCD"),
    ("000673.40", "000756.76 C0", "line 31  BZAE,X19  -NOT AN IOCD CARD"),
    ("000674.00", "000000.14 84 107000.07 70",
     "line 32  X13 2  CT0011(V+I)(BU,7),.12($4)  -TEST TENS POSITION "
     "OF CHANNEL"),
    ("000675.00", "000007.24 80 010427.24 30",
     "line 34  LCV(DU,8,4),$LZC+.3,46  -CONVERT TO OCTAL NUMBER"),
    ("000676.00", "000000.26 84 120000.07 70",
     "line 35  X13 2 AA  CT0011(V+I)(BU,16),.22($4)  -TEST UNITS "
     "POSITION"),
    ("000677.00", "000007.24 80 004027.20 10",
     "line 36  +(BU,4),$LZC+.3,46  -FORM CHANNEL NUMBER"),
    # ---- highest channel, and the CST entry ----
    ("000700.00", "000011.06 30",
     "line 37  LV,$3,$R  -CURRENT CHANNEL NUMBER FROM IOCD"),
    ("000700.40", "000023.07 90", "line 38  KC,$3,$3"),
    ("000701.00", "000702.32 40",
     "line 39  BZXL,X132A  -IF HIGEST CHANNEL YET ENCOUNTERED"),
    ("000701.40", "000023.06 50",
     "line 41  LC,$3,$3  -SAVE NEW HIGEST CHANNEL"),
    # THE 8/B ROW.  B0, not 80 -- see the module docstring.
    ("000702.00", "000025.06 B0", "line 42  X13 2A  V+,$3,$5  -ENTRY IN CST"),
    ("000702.40", "000000.14 84 000704.74 02",
     "line 43  X13 3  BB,.12($4),X13 4  -IS CHANNEL AVAILABLE"),
    ("000703.40", "000000.31 83 001000.00 F0",
     "line 44  CM0000(BU,1),.25($3)  -YES * CHANNEL AVAILABLE FLAG TO ON"),
    # ---- equipment code lookup ----
    ("000704.40", "000000.30 84 114000.20 50",
     "line 46  X13 4  L(V+I)(BU,12),.24($4)  -SECOND LETTER OF "
     "HOLLERITH EQUIPMENT"),
    ("000705.40", "001752.03 01",
     "line 47  LVI,$1,X EQP T  -BASE OF EQUIPMENT TABLE"),
    ("000706.00", "000012.03 02",
     "line 48  LCI,$1,10.0  -SIZE OF EQUIPMENT TABLE +1"),
    ("000706.40", "000551.00 80", "line 49  X13 5  SIC,X ERR AD"),
    ("000707.00", "000133.02 4A",
     "line 50  CBZ,$1,X ERROR  -WRONG EQUIPMENT CODE"),
    ("000707.40", "000000.35 81 130000.23 10",
     "line 51  KF(V+I)(BU,24),.29($1)  -MATCH * ADVANCE TO NEXT SLOT"),
    ("000710.40", "000706.76 C0", "line 52  BZAE,X 13 5"),
    ("000711.00", "777777.73 81 004000.20 50",
     "line 53  X13 6  L(BU,4),-.5($1)  -ENTER EQUPMENT CODE FROM TABLE"),
    ("000712.00", "000000.64 83 004000.20 D0",
     "line 54  ST(BU,4),.52($3)  -INSERT IN CST ENTRY"),
]

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP p.17 "))
