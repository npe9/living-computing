#!/usr/bin/env python3
"""verify_mcp_bootstrap_p15.py -- MCP INITIALIZATION, printed page 15
(../decks/mcp_bootstrap_p15.strap).  docs/MCP_Mar63_001-249.pdf PDF
p.22, header "PAGE NUMBER 15".  AGENTS.md rule 3.

THE FIRST PAGE OF MCP PROPER.  Printed p.14 ends the bootstrap with
"B,X 10"; X 10 is line 17 of this page, at 000622.00.  Everything
transcribed before this was the IPL bootstrap.

TWO OF THE SYMBOLS HERE ARE WEAKER EVIDENCE THAN THE REST, and the
deck says so: S MCP and S ROOF are communication-region symbols whose
defining page has not been transcribed, so their values are read off
THIS page's own binary output (line 21's second half-word, line 23's
address field).  Every other external -- X IN END, X BUFER, X S ROOF,
X ERR AD, X ERROR -- comes from the page that defines it.  A check
whose input came from the same printed row it checks is not a check;
these two rows are marked in ROWS below so a later reader can see
which they are.

THE INDICATOR ROWS ARE A REAL CHECK, THREE TIMES OVER.  Lines 29, 31
and 33 print 000133.03 46, 000133.03 C6 and 000133.04 46.  The branch
address in all three is X ERROR = 000133.00, known from printed p.5;
the indicator field (bits 19-24) comes out 6, 7 and 8, which are EKJ,
UNRJ and CBJ -- exactly what the row comments say ("IF EXCHANGE
ERROR", "IF DISK NOT READY", "IF DISK BUSY").  Line 29 is also
bit-for-bit the same half-word printed p.3 line 8 prints, on a page
read months earlier for other reasons.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p15.strap").read())

SYMBOLS = {
    "XIN":    "000621.00",
    "XUPDAT": "000621.40",
    "X10":    "000622.00",
    "X101":   "000623.00",
    "X104":   "000627.00",
    "X105":   "000630.00",
    "XERR12": "000631.00",
    "XERR13": "000632.00",
}

ROWS = [
    # ---- two BE instructions used as DATA ----
    ("000621.00", "004645.00 00",
     "line 15  X IN  BE,X IN END-X IN  -SIZE OF IPL FOR UPDATE PROGRAM"),
    ("000621.40", "000000.00 00",
     "line 16  X UPDAT  BE,0  -NUMBER OF PROSA ARCS"),
    # ---- MOVE COMMUNICATION REGION TO IPL AREA ----
    ("000622.00", "000150.23 0B",
     "line 17  X10  LVS,$9,$12,$11,$14  -COMPUTE NUMBER OF WORDS "
     "PRECEEDING MCP"),
    ("000622.40", "011406.21 B9",
     "line 19  LVE,$8,X BUFER($9)  - GET (MCP)"),
    ("000623.00", "011406.40 59",
     "line 20  X10 1  LC,$0,X BUFER +.32($9)  -GET SIZE OF COMM REGION"),
    # S MCP's value was READ OFF THIS ROW -- see the docstring.
    ("000623.40", "011406.00 89 002150.00 20",
     "line 21  T,$0,X BUFER($9),S MCP  -MOVE COMM REGION"),
    ("000624.40", "000546.00 70",
     "line 22  LR,$0,X S ROOF"),
    # S ROOF's value was READ OFF THIS ROW -- see the docstring.
    ("000625.00", "002162.01 70",
     "line 23  SR,$0,S ROOF  -PLACE 7030 SIZE IN COMM REGION"),
    ("000625.40", "011406.00 89 000000.24 28",
     "line 24  T,$10,X BUFER($9),0.0($8)  -PLACE MCP IN STORAGE"),
    ("000626.40", "000000.16 30",
     "line 25  LV,7,0.0  -INITIALIZE FIRST TIME THROUGH"),
    ("000627.00", "000000.00 80 000000.17 00",
     "line 26  X10 4  LOC(SEOP),0.0,0.0  -POSITION TO ARC ZERO"),
    # ---- DISK IO TEST ----
    ("000630.00", "000551.00 80",
     "line 28  X10 5  SIC,X ERR AD"),
    ("000630.40", "000133.03 46",
     "line 29  BEKJZ,X ERROR  -IF EXCHANGE ERROR"),
    ("000631.00", "000551.00 80",
     "line 30  X ERR 12  SIC,X ERR AD"),
    ("000631.40", "000133.03 C6",
     "line 31  BUNRJZ,X ERROR  -IF DISK NOT READY"),
    ("000632.00", "000551.00 80",
     "line 32  X ERR 13  SIC,X ERR AD"),
    ("000632.40", "000133.04 46",
     "line 33  BCBJZ,X ERROR  -IF DISK BUSY"),
]

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP p.15 "))
