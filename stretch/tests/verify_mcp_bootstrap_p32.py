#!/usr/bin/env python3
"""verify_mcp_bootstrap_p32.py -- MCP INITIALIZATION, printed page 32:
the rest of the message-deletion passes, and the message that tells
the operator which channel the spool reader is on
(../decks/mcp_bootstrap_p32.strap).
docs/MCP_Mar63_001-249.pdf PDF p.39, header "PAGE NUMBER 32".
AGENTS.md rule 3.

Thirty-six printed rows with binary output and ten symbol locations.

>>> THE PAGE REACHES BACK FIVE PAGES, AND THAT IS THE CHECK.  Lines
24, 44 and 48 all address "X24 A2+.32".  X24A2 is printed p.27 line
21, transcribed from THAT page's own location column three commits
ago as 001473.00, and this page's three rows print 001473.40 -- the
same address plus thirty-two bits.  Line 22's "B,X33 1A" reaches
back one page to printed p.31 line 35.  Neither address was read
off p.32; both are SYN'd from the pages that define them, so the
rows are a cross-page measurement and not a transcription. <<<

>>> "TI,$10" IS A COUNT, NOT A REGISTER, and the page proves it
against its own binary.  Line 46 is "TI,$10,X RDR MG,0.0($14)".
Reference Manual printed p.30: for immediate-count transmits "the
full word count is specified by instruction bits 51-54".  The
printed second half word is 000000.24 AE, whose bits 19-22 are 1010
= ten -- the count.  The "$" is the programmer's hand; every
TRANSMIT in decks/ writes that field as a bare digit and this one
does too. <<<

NO ASSEMBLER WORK, for the fifth page in six.  The one mnemonic the
page introduces, "Z" (line 18's "Z,0.0($12)", clearing the first
word of a message as a marker), was already built.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p32.strap").read())

SYMBOLS = {
    "X34":    "001632.40",
    "X341":   "001635.00",
    "X341A":  "001643.40",
    "X342":   "001644.00",
    "XERR29": "001646.40",
    "X35":    "001647.40",
    "X351":   "001650.40",
    "X353":   "001653.00",
    "X35A":   "001660.00",
    # Line 53's "X37A SYN,X37" prints 001666.40+ -- a SYN that only
    # renames, and the one row on the page whose value comes from a
    # page not yet transcribed.
    "X37A":   "001666.40",
}

ROWS = [
    # ---- message deletion passes continued ----
    ("001632.40", "000000.32 1C", "line 4   X34  LX,$13,0.0($12)  -GET CHANNEL ="),
    ("001633.00", "000035.32 B0", "line 5   V+,$13,$13  -DOUBLE IT"),
    ("001633.40", "000035.00 80 022000.20 30",
     "line 6   LCV(BU,18),$13  -CONVERT CHANNEL TO DECIMAL"),
    ("001634.40", "002000.31 01",
     "line 7   LVI,$12,X MSG BK  -INITIALIZE FOR MESSAGE BLOCK"),
    ("001635.00", "000006.33 8C 004000.23 10", "line 8   X34 1  KF(BU,4),6.27($12)"),
    ("001636.00", "001644.36 C0",
     "line 10  BZAE,X34 2  -IF TESTS SHOULD CONTINUE"),
    ("001636.40", "000006.23 8C 004002.23 10",
     "line 11  KF(BU,4),6.19($12),4  -YES"),
    ("001637.40", "001644.36 C0",
     "line 13  BZAE,X34 2  -IF TEST SHOULD CONTINUE"),
    ("001640.00", "000011.35 30",  "line 14  SV,$14,$R  -GET UNIT NUMBER"),
    ("001640.40", "000007.23 8C 004027.23 10", "line 15  KF(BU,4),7.19($12),46"),
    ("001641.40", "001644.36 C0",
     "line 17  BZAE,X34 2  -IF CHANNEL FOR WHICH SEARCHED"),
    ("001642.00", "000000.22 0C",
     "line 18  Z,0.0($12)  -CLEAR FIRST WORD OF MESSAGE AS MARKER"),
    ("001642.40", "001647.40 4A", "line 20  CBZ,$0,X35  -IF FOUND TWO MESSAGE"),
    ("001643.00", "002154.34 10", "line 21  LX,$14,S W TAPE  -NO* GET F"),
    ("001643.40", "001620.10 00",
     "line 22  X34 1 A  B,X33 1A  -FIND SECOND MESSAGE (printed p.31)"),
    ("001644.00", "000012.31 05",
     "line 23  X34 2  V+I,$12,10.0  -ADVANCE TO NEXT MESSAGE"),
    ("001644.40", "001473.40 80 022027.06 70",
     "line 24  LF(BU,18),X24A2+.32,46  -GET NEXT ADDRESS (printed p.27)"),
    ("001645.40", "000011.30 90", "line 26  KV,$12,$R"),
    ("001646.00", "001635.32 42", "line 27  BXL,X34 1  -IF EXHAUSTED ALL MSG"),
    ("001646.40", "000551.00 80", "line 28  XERR 29  SIC,X ERR AD"),
    ("001647.00", "000133.10 00", "line 29  B,X ERROR  -BOTH MESSAGES NOT FOUND"),
    # ---- build the reader-channel message ----
    ("001647.40", "002154.74 30",
     "line 36  X35  LV,$14,S READ R  -GET SPOOL CARD READER IODR F"),
    ("001650.00", "002153.34 B0",
     "line 37  V+,$14,S BA MCP  -SPOOL READER FILE ENTRY IN IO LOCATION"),
    ("001650.40", "000000.34 1E", "line 38  X35 1  LX,$14,0.0($14)  -GET UAT"),
    ("001651.00", "000000.34 1E", "line 39  LX,$14,0.0($14)  -GET CHANNEL NUMBER"),
    ("001651.40", "000036.34 B0", "line 40  V+,$14,$14  -DOUBLE IT"),
    ("001652.00", "000036.00 80 022000.20 30",
     "line 41  LCV(BU,18),$14  -CONVERT TO DECIMAL"),
    ("001653.00", "001771.53 80 004402.22 90",
     "line 42  X35 3  M+MG(BU,4,4),X RDR CR+.3,4  -ADD CHANNEL TO MSG IN IQS"),
    ("001654.00", "001771.63 80 004400.22 90",
     "line 43  M+MG(BU,4,4),X RDR CR+.8+.3  -ADD CHANNEL TO MSG IN IQS"),
    ("001655.00", "001473.75 B0",
     "line 44  LVE,$14,X 24 A2 +.32  -GET CURRENT MESS BLOCK LOCATION"),
    ("001655.40", "001765.00 80 000000.24 AE",
     "line 46  TI,$10,X RDR MG,0.0($14)  -MOVE MSG TO MSG BLOCK"),
    ("001656.40", "000012.35 05",
     "line 47  V+I,$14,10.0  -ADVANCE TO NEXT AVAILABLE MESSAGE BLOCK"),
    ("001657.00", "001473.75 D0",
     "line 48  SVA,$14,X24 A2 +.32  -SAVE MESS BLOCK LOC"),
    ("001657.40", "001666.50 00", "line 49  B,X37"),
    ("001660.00", "002151.11 80 001661.74 02",
     "line 51  X35 A  BB,S COM RG+.9,X36  -IF OVERLAPPED ON LINE"),
    ("001661.00", "001647.50 00",
     "line 52  B,X35  -YES*SPECIFY READER CHANNEL"),
]

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP p.32 "))
