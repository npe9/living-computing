#!/usr/bin/env python3
"""verify_mcp_bootstrap_p19.py -- MCP INITIALIZATION, printed page 19:
the DISK/CONSOLE half of the IOCD processing and the move of the
status tables into upper storage
(../decks/mcp_bootstrap_p19.strap).  docs/MCP_Mar63_001-249.pdf PDF
p.26, header "PAGE NUMBER 19".  AGENTS.md rule 3.

Forty-four printed rows with binary output.

>>> THIS PAGE WAS OPENED TO SETTLE A PREDICTION, AND IT DID.  Line 9
is "CM1111(BU,1),.61($3)" commented "-SET UNIT COUNT TO TWO".  SUNITK
had been derived as bits 59-62 from printed p.18 line 30, which sets
ONE bit at .59 and calls the result eight; two is 0b0010, which is
not a bit at a field's left edge, so the prediction committed before
this page was read was that p.19 must set a single bit at .61.  It
does.  Two pages, two values, two offsets, one field width. <<<

THE TWO FORWARD REFERENCES INTO THIS PAGE WERE BOTH RECOVERED FROM
ENCODINGS and are both exact.  X18 = 000740.40 came off printed p.18
line 2's branch-address field; X19 = 000756.40 was recovered from
p.17's indicator encoding.  This page begins at 000740.40 and its
line 23 sits at 000756.40.

AND X IOD BEGINS WHERE X IOCD ENDS.  Line 23 compares thirty-six bits
-- three columns, the characters "IOD" -- against 001750.40, and p.17
put X IOCD at 001747.60 with a length of 48 bits, which runs to
001750.40 exactly.  The two card keywords are adjacent literals.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p19.strap").read())

SYMBOLS = {
    "X18":    "000740.40",
    "X181":   "000742.00",
    "X182":   "000747.00",
    "X183":   "000751.00",
    "X184":   "000753.00",
    "X185":   "000755.00",
    "X19":    "000756.40",
    "XERR19": "000757.40",
    "X191":   "000761.00",
    "X192":   "000765.40",
    "X20":    "000770.40",
    "X201":   "000772.40",
    "X202":   "000776.40",
}

ROWS = [
    ("000740.40", "777777.43 81 030000.07 70",
     "line 2   X18  CT0011(BU,24),-.29($1)"),
    ("000741.40", "000737.34 C2",            "line 3   BRZ,X17 1"),
    ("000742.00", "000006.03 0A",
     "line 4   X18 1  KCI,$1,6.0  -LOGICAL MULTI UNIT * DISK OR CONSOL"),
    ("000742.40", "000753.33 40",            "line 6   BZXH,X 18 4"),
    ("000743.00", "000002.37 02",            "line 7   LCI,$15,2.0"),
    ("000743.40", "000000.37 33",
     "line 8   SV,$15,0.0($3)  -YES * ENTER UST ADDRESS IN CST"),
    ("000744.00", "000000.75 83 001000.36 F0",
     "line 9   CM1111(BU,1),.61($3)  -SET UNIT COUNT TO TWO"),
    ("000745.00", "000000.33 83 001000.36 F0",
     "line 10  CM1111(BU,1),.27($3)  -MULIT BIT ON IN CST"),
    ("000746.00", "000000.35 83 001000.00 F0",
     "line 11  CM0000(BU,1),.29($3)  -MEANINGLESS ASG BIT OFF"),
    ("000747.00", "000000.31 83 000751.34 00",
     "line 12  X18 2  BZB,.25($3),X18 3  -IF CHANNEL AVAILABLE"),
    ("000750.00", "000000.34 8F 001000.36 F0",
     "line 13  CM1111(BU,1),.28($15)  -NO * THEN UNIT NOT AVAILABLE"),
    ("000751.00", "000000.35 8F 001000.36 F0",
     "line 14  X18 3  CM1111(BU,1),.29($15)  -YES * UNIT STATUS TO NOT ASSIGNED"),
    ("000752.00", "000747.37 48",
     "line 16  CB+,$15,X18 2  -IF PROCESSED TWO LOGICAL UNITS *"),
    ("000752.40", "000737.10 00",
     "line 17  B,X17 1  -RETURN FOR NEXT CARD"),
    ("000753.00", "000000.31 83 000755.34 00",
     "line 18  X18 4  BZB,.25($3),X18 5  -IF CHANNEL AVAILABLE"),
    ("000754.00", "000000.34 83 001000.36 F0",
     "line 19  CM1111(BU,1),.28($3)  -SINGLE UNIT STATUS TO NOT AVAILABLE"),
    ("000755.00", "000000.35 83 001000.36 F0",
     "line 21  X18 5  CM1111(BU,1),.29($3)  -AND TO NOT ASSIGNED"),
    ("000756.00", "000737.10 00",
     "line 22  B,X17 1  -RETURN FOR NEXT CARD"),
    ("000756.40", "001750.40 80 044006.23 10",
     "line 23  X19  KF(BU,36),XIOD,12  -COMPARE AGAINST * IOD *"),
    ("000757.40", "000551.00 80",
     "line 24  X ERR 19  SIC,X ERR AD"),
    ("000760.00", "000133.36 C4",
     "line 25  BZAEZ,X ERROR  -NOT AN IOD CARD EITHER -IOD*"),
    ("000760.40", "002155.37 30",
     "line 27  SV,$15,S LR BU  -SAVE BASE OF IO ASSIGNMENT TABLES"),
    ("000761.00", "000037.34 50",
     "line 29  X 191  LC,$14,$15  - ENTER CURRENT UST TESTING ADDRESS IN CF"),
    ("000761.40", "000762.35 D0",            "line 30  SVA,$14,$+.32"),
    ("000762.00", "000000.35 08",
     "line 31  C-I,$14,0.0  - COMPUTE SIZE OF UST AREA"),
    ("000762.40", "000035.21 30",
     "line 32  SV,$8,$13  -TEMPORARILLY SAVE BASE OF MCP"),
    ("000763.00", "000034.35 50",
     "line 33  SC,$14,$12  -TEMPORARILLY SAVE SIZE OF UST"),
    ("000763.40", "000764.31 D0",            "line 34  SVA,$12,$+.32"),
    ("000764.00", "000000.33 0D",            "line 35  V-I,$13,0.0"),
    ("000764.40", "000000.00 8E 000000.34 2D",
     "line 36  T,$14,0.0($14),0.0($13)  -MOVE UST TA UPPER STORAGE"),
    ("000765.40", "000033.07 50",            "line 37  X19 2  SC,$3,$11"),
    ("000766.00", "000025.26 B0",
     "line 38  V+ ,$11,$5  -UPPER BOUND OF OLD CST"),
    ("000766.40", "000001.33 0D",
     "line 39  V-I,$13,1.0  -UPPER BOUND OF OLD CST"),
    ("000767.00", "000001.07 00",
     "line 40  C+I,$3,1.0  -ADJUST ADDRESS AND COUNT FOR TRANSFER"),
    ("000767.40", "000000.00 8B 000000.07 2D",
     "line 41  TB,$3,0.0($11),0.0($13)  -MOVE BIASED CTS"),
    ("000770.40", "000023.24 10",
     "line 42  X20  LX,$10,$3  -SIZE OF CST"),
    ("000771.00", "002150.24 30",            "line 43  LV,$10,SMCP"),
    ("000771.40", "001726.25 D0",
     "line 44  SVA,$10,X37 8  -PRESERVE ADDRESS OF COMREG"),
    ("000772.00", "000035.24 30",
     "line 45  LV,$10,$13  -UPPER LIMIT OF CST"),
    ("000772.40", "000000.33 8A 000776.74 00",
     "line 46  X20 1  BZB,.27($10),X20 2  -IF MULTI"),
    ("000773.40", "000000.22 3A",            "line 47  LV,$9,0.0($10)  -YES"),
    ("000774.00", "000774.75 D0",            "line 48  SVA,$14,$+.32"),
    ("000774.40", "000000.23 0D",            "line 49  V-I,$9,0.0"),
    ("000775.00", "000035.22 B0",            "line 50  V+ ,$9,$13"),
    ("000775.40", "000001.23 05",            "line 51  V+I,$9,1.0"),
    ("000776.00", "000000.23 3A",
     "line 52  SV,$9,0.0($10)  -INSERT UNBIASED UST ADDRESS"),
    ("000776.40", "000772.65 C8",            "line 53  X20 2  CB-,$10,X20 1"),
]

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP p.19 "))
