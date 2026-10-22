#!/usr/bin/env python3
"""verify_mcp_bootstrap_p25.py -- MCP INITIALIZATION, printed page 25:
the printer channel search and the start of "TO UNCODE"
(../decks/mcp_bootstrap_p25.strap).  docs/MCP_Mar63_001-249.pdf PDF
p.32, header "PAGE NUMBER 25".  AGENTS.md rule 3.

Thirty-two printed rows with binary output.

>>> THE PRINTER'S EQUIPMENT CODE IS OCTAL 5.  Line 17 is
"LFI(BU,4),(8)5" commented "-ENTER PRINTER EQUIPMENT CODE" and line
18 compares it against ".52($10)", the SEQUIP field.  With printed
p.20's console = 2, two of X EQP T's values are now known from the
programs that use them. <<<

>>> AND THE PAGE NEEDED A NULL OPERATION FIELD.  Lines 42-43 are
",0.0($7)" and ",2.0($7)" -- statements with NO operation, written as
nothing but the comma.  C22-6531 printed p.7: "A MAJOR FIELD MAY BE
NULL ... if nothing but the comma denoting the field termination is
written", and "a null field is always compiled as a zero".

What they emit is the ADDRESS-AND-INDEX HALF WORD EVERY FULL-WORD
FORMAT BEGINS WITH, and that is printed rather than inferred:
Reference Manual printed p.163 draws INTEGER, CONNECTIVE,
INPUT-OUTPUT, TRANSMIT, SIC BRANCH and BRANCH ON BIT with an
identical first half -- ADDRESS (0-23) | 1000 (24-27) | I (28-31) --
six diagrams, one shape.  The "1000" is a literal of the full-word
forms, not the operation's bits; no half-word format on that page has
it.

AND LINE 51 CORROBORATES IT A THIRD TIME from inside this very page:
"BB,2.04($7),X22 2" is a REAL branch on bit, a full-word format, and
its first half prints 000002.04 87 -- same address shape, same 1000,
same index 7.  The null operations lay down exactly that half and
nothing after bit 31. <<<

TWO ROWS WERE MISREAD AT 150 dpi AND THE OPCODE SETTLED BOTH, which
is listing_typography.md 13's rule doing its job: line 24's byte is
D0 and not C0, because ST's nine-bit operation field ends in the
literal 1 at bit 59 that C0 would clear; and line 35's is 01 and not
C1, because LVI's immediate-index template "jjjj10000xxxx" puts 0000
at bits 24-27 and 0001 at 28-31.  Decoding decided both before the
900 dpi render confirmed them.

X IO STK IS CHECKED AS A SYMBOL: line 6 is "SYN,$-X IO STA" and
printed p.24 line 54's control word already took a count of 5 from
it, before this page was read.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p25.strap").read())

SYMBOLS = {
    "XIOSTK": "000005.00",
    "X20B":   "001417.00",
    "X20B1A": "001421.40",
    "X20B1":  "001423.00",
    "X20B3":  "001424.00",
    "X20B4":  "001426.40",
    "X20B2":  "001427.00",
    "X22":    "001430.40",
    "X221":   "001433.00",
    "X222":   "001433.40",
    "X222AA": "001434.00",
    "X222A":  "001435.00",
    "X223":   "001440.40",
    "X224":   "001441.40",
}

ROWS = [
    ("001412.10", "002",                     "line 1   DD(BU,8),(2)00000010  -RED$"),
    ("001416.40", "375",                     "line 3   DD(BU,8),(2) 1111 1101  -CARRIAGE RETURN"),
    ("001416.50", "376",                     "line 4   DD(BU,8),(2) 1111 1110  -END OF MSG"),
    ("001417.00", "002152.24 10",
     "line 12  X20 B  LX,$10,S X CHAN  -INITIALIZE FOR PRINTER CHANNEL SEARCH"),
    ("001417.40", "000040.25 05",
     "line 13  V+I,$10,32.0  -COMPUTE FIRST CST ENTRY FOR BASIC CHG"),
    ("001420.00", "000037.25 08",
     "line 15  C-I,$10,31.0  -COMPUT NUMBER OF CHANNEL IN BASIC EXCHANGE"),
    ("001420.40", "240000.00 80 404000.06 70",
     "line 17  LFI(BU,4),(8)5  -ENTER PRINTER EQUIPMENT CODE"),
    ("001421.40", "000000.64 8A 004000.23 10",
     "line 18  X20 B 1A  KF(BU,4),.52($10)  -TEST AGAINST EQUIPMENT FIELD"),
    ("001422.40", "001424.36 C2",            "line 19  BAE,X20 B3  -IF PRINTER PRESENT"),
    ("001423.00", "001427.25 4A",            "line 20  X20 B 1  CBZ+,$10,X20 B 2  -IF NO PRINTER"),
    ("001423.40", "001421.50 00",            "line 21  B,X20 B 1A"),
    ("001424.00", "000011.25 10",            "line 22  X20 B 3  SX,$10,$R  -PRINTER CST ENTRY"),
    ("001424.40", "002152.00 80 023026.70 10",
     "line 23  -(BU,19),S X CHAN,45  -LESS BASE OF CST"),
    ("001425.40", "002156.40 80 023000.20 D0",
     "line 24  ST(BU,19),SY PR CH  -PRINTER CHANN NUM TO COMM RIGON"),
    ("001426.40", "001430.50 00",            "line 25  X20 B4  B,X22"),
    ("001427.00", "002156.40 80 023000.37 70",
     "line 26  X20 B 2  CT1111(BU,19),SY PR CH  -ILLEGAL CHANN NUM"),
    ("001430.00", "001426.50 00",            "line 27  B,X20B4"),
    ("001430.40", "000002.36 84 510000.07 70",
     "line 32  X22  CT0011(V-I)(BU,8),+2.30($4)  -COMPUTE BASE OF AREA"),
    ("001431.40", "002201.25 80 001000.36 F0", "line 33  CM1111(BU,1),YIPL1+.21"),
    ("001432.40", "000024.16 30",
     "line 34  LV,$7,$4  -CONTAINING IOD AND REEL CARDS"),
    ("001433.00", "001435.35 01",
     "line 35  X22 1  LVI,$14,X22 2 A  -ENTER RETURNED PARAMETER SLOT"),
    ("001433.40", "002166.10 00",            "line 36  X22 2  B,YUNCOD  -TO UNCODE ROUTINE"),
    ("001435.00", "000000.00+ 000 000000 000000",
     "line 39  X22 2 A  XW,0  -FOR TOE, FIELD COUNT, IO REF NUMBER"),
    ("001436.00", "000004.00+",              "line 41  VF,4.0  -EXPECT IOD AND REEL CARDS"),
    ("001436.40", "000000.00 87",            "line 42  ,0.0($7)  -GET CARD AT"),
    ("001437.00", "000002.00 87",            "line 43  ,2.0($7)  -PUT TABLE AT"),
    ("001437.40", "001440.50 00",            "line 44  B,X22 3  -NOT IOD OR REEL CARD"),
    ("001440.00", "001441.50 00",            "line 45  B,X22 4  -NORMAL"),
    ("001440.40", "000551.00 80",            "line 46  X22 3  SIC,XERRAD"),
    ("001441.00", "000133.10 00",            "line 47  B,X ERROR  -ERROR IN UNCODE"),
    ("001441.40", "777777.00 8E 000000.04 A7",
     "line 48  X22 4  TI,2,-1.0($14),0.0($7)  -SAVE RETURNED PARAMETER IN TABLE"),
    ("001442.40", "000017.17 05",            "line 50  V+I,$7,15.0"),
    ("001443.00", "000002.04 87 001433.74 02",
     "line 51  BB,2.04($7),X22 2  -IF PROCESSED LAST CARD"),
]

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP p.25 "))
