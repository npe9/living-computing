#!/usr/bin/env python3
"""verify_mcp_bootstrap_p20.py -- MCP INITIALIZATION, printed page 20:
the communication-region entries and the search for the console
channel (../decks/mcp_bootstrap_p20.strap).
docs/MCP_Mar63_001-249.pdf PDF p.27, header "PAGE NUMBER 20".
AGENTS.md rule 3.

Seventeen printed rows with binary output.

>>> THE CONSOLE'S EQUIPMENT CODE IS OCTAL 2, and this page is the
only place in the transcribed corpus that gives one. <<<  Line 14 is
"LFI(BU,4),(8)2" commented "-ENTER CONSOLE EQUIPMENT CODE", and line
15 compares it against ".52($10)".  X EQP T maps a card's equipment
letter to a four-bit code and sits on an untranscribed page; one of
its values is now known from the program that uses it.

>>> X EQP T IS PRINTED p.35, TRANSCRIBED 2026-10-22, AND IT AGREES:
its second entry is CONSOLE, code 2.  A value derived from the
program that uses it, checked against the table it came from. <<<

AND IT CONFIRMS SEQUIP FROM A THIRD PAGE: C22-6728 printed p.246
names bits 52-55 of a channel status table entry SEQUIP, printed p.17
line 54 WRITES four bits at .52, and this page READS four bits at .52
and calls it "the equipment field".

S MCP IS CROSS-CHECKED BETWEEN TWO PAGES.  Line 11 puts it at
002150.00, and printed p.19 line 43's "LV,$10,SMCP" assembles to
002150.24 30 -- the same address recovered from a different page's
binary output.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p20.strap").read())

SYMBOLS = {
    "X20A":   "000777.00",
    "X20A1":  "001001.40",
    "X20A2":  "001003.40",
    "X20A3":  "001004.40",
    "XERR20": "001005.40",
    "X20A4":  "001006.00",
    "XERR21": "001007.00",
    "X20A5":  "001007.40",
}

ROWS = [
    ("000777.00", "000011.07 50",
     "line 6   X20A  SC,$3,$R  -RESTORE SIZE OF CST"),
    ("000777.40", "000011.24 50",            "line 7   LC,$10,$R"),
    ("001000.00", "000001.25 05",            "line 8   V+I,$10,1.0"),
    ("001000.40", "002152.25 10",
     "line 9   SX,$10,S X CHAN  -SAVE BASE OF CST AND SIZE IN COMM REGIN"),
    ("001001.00", "000037.25 08",
     "line 10  C-I,$10,32.0-1.0  -GET SIZE OF BASIC EXCHG CST"),
    ("001001.40", "002150.25 30",
     "line 11  X20 A 1  SV,$10,S MCP  -SET BASE OF MCP IN COMM REGION"),
    ("001002.00", "000040.25 05",
     "line 12  V+I,$10,32.0  -COMP LOC OF FIRST BASIC EACH CHG CHANNL"),
    ("001002.40", "100000.00 80 404000.06 70",
     "line 14  LFI(BU,4),(8)2  -ENTER CONSOLE EQUIPMENT CODE"),
    ("001003.40", "000000.64 8A 004000.23 10",
     "line 15  X20 A 2  KF(BU,4),.52($10)  -TEST AGAINST EQUIPMENT FIELD"),
    ("001004.40", "001006.36 C2",
     "line 16  X20 A 3  BAE,X20A4  -IF CONSOLE PRESENT"),
    ("001005.00", "001003.65 48",
     "line 17  CB+,$10,X20 A 2  -IF TESTED ALL CHANNELS"),
    ("001005.40", "001005.44 00",
     "line 18  XERR 20  BD,$  -YES *ERROR* NO CONSOLE"),
    ("001006.00", "000000.31 8A 001007.74 00",
     "line 19  X 20 A 4  BZB,+.25($10),X20A5  -IF CONSOL AVAILABLE"),
    ("001007.00", "001007.04 00",
     "line 20  XERR21  BD,$  -NO$ERROR * CONSOLE NOT AVAILABLE"),
    ("001007.40", "000011.25 10",
     "line 21  X 20 A 5  SX,$10,$R  -CONSOLE CST ENTRY"),
    ("001010.00", "002152.00 80 023026.70 10",
     "line 22  -(BU,19),SXCHAN,45  -LESS BASE OF CST"),
    ("001011.00", "002156.00 80 023027.20 D0",
     "line 23  ST(BU,19),SYCOCH,46  -CONSLOE CHANNEL NUMBER TO COMM REGION"),
]

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP p.20 "))
