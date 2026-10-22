#!/usr/bin/env python3
"""verify_mcp_bootstrap_p33.py -- MCP INITIALIZATION, printed page 33:
unassigning the spool reader in offline overlapped mode, and the
switch that primes the System Command routine
(../decks/mcp_bootstrap_p33.strap).
docs/MCP_Mar63_001-249.pdf PDF p.40, header "PAGE NUMBER 33".
AGENTS.md rule 3.

Forty-five printed rows with binary output and fourteen symbol
locations -- every row on the page.

>>> ELEVEN NULL-OPERATION ROWS, the form the assembler gained for
printed p.25 and had seen three times since.  Lines 27-31, 36-40 and
43 are the parameter list the "BD,0.0($12)" above each group
branches into: ", S COMD", ", 4.0", ", 0.0($14)", ", 28.0", ", 0.0".
C28-6129 printed p.6 is the specification -- "it compiles the
statement as a half word with a 24-bit address field, the 25th bit
set to one and all the rest of the bits set to zero" -- and every
one of the eleven prints exactly that. <<<

>>> X36 IS THE ADDRESS THREE EARLIER PAGES ALREADY COMPILED.
printed p.30 line 24, p.31 line 24 and p.32 line 51 all branch to
X36, and all three were transcribed before this page was opened;
each compiled 001661.74, half 1 of word 001661.  This page's
location column opens at 001661.40. <<<

ONE SPELLING SUBSTITUTED, and the deck says so: line 33's
"BZB1,X VSWCH.19,X37 4A" is written "BZB1,XVSWCH+.19,X374A" here.
The printed address 001672.23 is XVSWCH (001672.00) plus nineteen
bits, so the two are the same address; whether STRAP-II accepts
"SYMBOL.bits" as an implicit sum is an open question and this deck
does not answer it.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p33.strap").read())

SYMBOLS = {
    "X36":    "001661.40",
    "X363":   "001663.00",
    "X364":   "001664.40",
    "X37":    "001666.40",
    "X371":   "001667.40",
    "X374":   "001671.40",
    "XVSWCH": "001672.00",
    "XVPRIM": "001677.00",
    "XVNOGO": "001677.40",
    "X374A":  "001700.40",
    "X376":   "001704.00",
    "X371A":  "001706.00",
    "X371B":  "001707.00",
    "X377":   "001710.00",
}

_NOP_PARAM = "  (null operation field, C28-6129 printed p.6)"

ROWS = [
    # ---- offline overlapped: unassign the spool reader ----
    ("001661.40", "002154.74 30",
     "line 5   X36  LV,$14,S READ R  -GET SPOOL READER IOP REFERENCE NUMBERS"),
    ("001662.00", "002153.34 B0",
     "line 6   V+,$14,S BA MCP  -SPOOL READ ENTRY IN IO LOCATION TABLE"),
    ("001662.40", "000000.34 1E", "line 7   LX,$14,0.0($14)  -GET UAT"),
    ("001663.00", "000000.34 1E", "line 8   X36 3  LX,$14,0.0($14)  -GET CHANNEL NUMBER"),
    ("001663.40", "000036.34 B0", "line 9   V+,$14,$14  -DOUBLE IT"),
    ("001664.00", "002152.34 B0", "line 10  V+,$14,S X CHAN  -GET CST ENTRY"),
    ("001664.40", "000000.35 8E 001000.36 F0",
     "line 11  X36 4  CM1111(BU,1),.29($14)  -UNIT STATUS TO NOT ASSIGNED"),
    ("001665.40", "000000.40 8E 001000.00 F0",
     "line 12  CM0000(BU,1),.32($14)  -OWNERSHIP STATUS TO PP"),
    # ---- prime the system command routine ----
    ("001666.40", "002160.72 30",
     "line 17  X37  LV,$13,S PR OUT  -SAVED RETURN ADDRESS FOR PRIME"),
    ("001667.00", "002160.30 30",
     "line 18  LV,$12,S PR IN  -ENTRY TO PRIME ROUTINE"),
    ("001667.40", "002151.10 80 001707.34 02",
     "line 19  X37 1  BB,S COM RG+.8,X371B  -IF BYPS"),
    ("001670.40", "002151.11 80 001706.34 02",
     "line 20  BB,S COM RG+.9,X371A  -NO * IF ON LINE MODE"),
    ("001671.40", "001761.35 01", "line 21  X37 4  LVI,$14,X ON LIN  -ON LINE"),
    ("001672.00", "001677.70 00", "line 22  XVSWCH  NOP,XVNOGO"),
    ("001672.40", "001677.35 D0", "line 23  SVA,$14,XVPRIM"),
    ("001673.00", "001241.35 01", "line 24  LVI,$14,XVCLOK"),
    ("001673.40", "000000.00 8D", "line 25  SIC,0.0($13)"),
    ("001674.00", "000000.04 0C", "line 26  BD,0.0($12)"),
    ("001674.40", "000120.00 80", "line 27  ,S COMD" + _NOP_PARAM),
    ("001675.00", "000004.00 80", "line 28  ,4.0" + _NOP_PARAM),
    ("001675.40", "000000.00 8E", "line 29  ,0.0($14)" + _NOP_PARAM),
    ("001676.00", "000034.00 80", "line 30  ,28.0" + _NOP_PARAM),
    ("001676.40", "000000.00 80", "line 31  ,0.0" + _NOP_PARAM),
    ("001677.00", "001677.35 01",
     "line 32  XVPRIM  LVI,$14,$  (the location counter)"),
    ("001677.40", "001672.23 80 001700.74 0C",
     "line 33  XVNOGO  BZB1,X VSWCH.19,X37 4A"),
    ("001700.40", "000000.00 8D", "line 34  X37 4 A  SIC,0.0($13)"),
    ("001701.00", "000000.04 0C",
     "line 35  BD,0.0($12)  -PRIME SYSTEM COMMAND ROUTINE"),
    ("001701.40", "000120.00 80", "line 36  ,S COMD" + _NOP_PARAM),
    ("001702.00", "000004.00 80",
     "line 37  ,4.0  -IPL INDICATOR AS SENDER OF COMMAND"),
    ("001702.40", "000000.00 8E",
     "line 38  ,0.0($14)  -LOCATION OF COMMAND IN BCD"),
    ("001703.00", "000014.00 80", "line 39  ,12.0" + _NOP_PARAM),
    ("001703.40", "000000.00 80", "line 40  ,0.0  -ERROR RETURN"),
    ("001704.00", "000000.00 8D", "line 41  X37 6  SIC,0.0($13)"),
    ("001704.40", "000000.04 0C", "line 42  BD,0.0($12)  -PRIME JOB CONTROL 4"),
    ("001705.00", "000116.40 80", "line 43  ,S JC4" + _NOP_PARAM),
    ("001705.40", "001710.10 00", "line 44  B,X37 7"),
    ("001706.00", "001763.35 01", "line 45  X37 1A  LVI,$14,X OF LIN  -OFF LINE"),
    ("001706.40", "001672.10 00", "line 46  B,XVSWCH"),
    ("001707.00", "001757.35 01",
     "line 47  X37 1 B  LVI,$14,X BYPAS  - PRIME SYSTEM COMM FOR BYPASS MODE"),
    ("001707.40", "001672.10 00", "line 48  B,XVSWCH"),
    ("001710.00", "002163.34 30", "line 49  X37 7  LV,$14,S IA  -GET $IA"),
    ("001710.40", "000002.35 30", "line 50  SV,$14,$IA"),
    ("001711.00", "001777.42 60", "line 51  LWF(U),X BOUND  -GET MCP BOUNDS"),
    ("001711.40", "000003.00 80 000040.20 D0", "line 52  ST(BU),$UB,64"),
    ("001712.40", "001034.34 80 001726.34 02",
     "line 53  BB,X LR IN+.28,X 37 8  - BRANCH IF SUPPRESS MESSAGES"),
]

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP p.33 "))
