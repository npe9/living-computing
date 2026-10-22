#!/usr/bin/env python3
"""verify_mcp_bootstrap_p30.py -- MCP INITIALIZATION, printed page 30:
"MCP TYPE REQUEST REPORT" and "MCP MODE REPORT"
(../decks/mcp_bootstrap_p30.strap).
docs/MCP_Mar63_001-249.pdf PDF p.37, header "PAGE NUMBER 30".
AGENTS.md rule 3.

Twenty-three printed rows with binary output and nine symbol
locations.

>>> THE ASSEMBLER GAINED THE PARENTHETICAL INTEGER ENTRY MODE FOR
LINE 27, and the manual was read before anything was written.
C28-6129 Section II, printed p.25 (PDF 29), "Field Entry Mode":

  "A final STRAP entry mode that is used as a field entry mode is the
   parenthetical integer entry mode...  The general format for this
   entry mode is:  (.n)A(n+1)
   The symbol .n represents the BIT ADDRESS OF THE RIGHTMOST BIT of
   the field into which the integer or bit pattern is to be entered.
   The integer A(n+1) is formed as an unsigned field, n+1 bits in
   length..., and inserted into the leftmost n+1 bits of the
   addressed instruction or data entry field by means of a LOGICAL
   OR type operation."

So line 27's "X MO CW1(.25)1" ORs a one into bit 25 of the full word
the CW compiles -- the CHAIN flag -- and the row prints its flag
group as "100".  See decks/parenthetical_entry.strap and
verify_parenthetical_entry.py for the mode itself. <<<

>>> AND IT RETIRES A FOUR-MONTH-OLD SUBSTITUTION.  printed p.8 line
34 is the same construct, "CW,X ZEROS,3,X MSG CW(.25)1", and
decks/mcp_bootstrap_p7_p8.strap had been writing "CW(CCR),X
ZEROS,3,X MSG CW" instead, on the explicit grounds that inventing
the semantics from one row is what rule 4 forbids.  That row is now
verbatim too, and the equality the old note ASSERTED -- that the two
spellings compile the same word -- is now a check. <<<

CONTIGUOUS WITH p.29 BY FALL-THROUGH: p.29 ends with a full-word
TRANSMIT at 001552.40 and this page's first instruction is at
001553.40.  X32, the forward reference this page branches to twice,
is at 001601.00, which is exactly where printed p.31 begins.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p30.strap").read())

SYMBOLS = {
    "XREJ1":  "001553.40",
    "XREJ2":  "001557.40",
    "XREJ3":  "001562.00",
    "XMODE1": "001564.00",
    "XMODE3": "001570.40",
    "XMOCW":  "001573.00",
    "XMOCW1": "001574.00",
    "XMODE":  "001575.00",
    # Line 36's "X MODE K SYN,$-X MODE" measures the message: the
    # listing prints 000004.00+, four words, and the deck computes it
    # from the DDs rather than being told.
    "XMODEK": "000004.00",
}

ROWS = [
    # ---- MCP type request report ----
    ("001553.40", "002156.36 30",
     "line 5   X REJ 1  LV,$15,S YCOCH  -GET CONSOLE CHANNEL NUMBER"),
    ("001554.00", "001034.36 80 001564.34 00",
     "line 6   BZB,X LR IN+.30,X MODE 1  - IF JOBS ARE TO BE REJECTED"),
    ("001555.00", "001035.44 80 004000.31 70",
     "line 7   CT1100(BU,4),X LR IN+1.36"),
    ("001556.00", "001557.74 C0",            "line 8   BZRZ,X REJ 2"),
    ("001556.40", "001035.44 80 004000.00 F0",
     "line 9   CM0000(BU,4),X LR IN+1.36"),
    ("001557.40", "001035.50 80 004000.31 70",
     "line 10  X REJ 2  CT1100(BU,4),X LR IN+1.40"),
    ("001560.40", "001562.34 C0",            "line 11  BZRZ,X REJ 3"),
    ("001561.00", "001035.50 80 004000.00 F0",
     "line 12  CM0000(BU,4),X LR IN+1.40"),
    ("001562.00", "001035.44 80 010400.24 30",
     "line 13  X REJ 3  LCV(DU,8,4),X LR IN+1.36  -CONVERT NUMBER"),
    ("001563.00", "002161.40 80 022000.20 D0",
     "line 14  ST(BU,18),S REJ JB  -SAVE COUNT"),
    # ---- MCP mode report ----
    ("001564.00", "001034.37 80 001601.34 00",
     "line 19  X MODE1  BZB,X LR IN+.31,X 32  - IF NON-INSTALLATION MODE"),
    ("001565.00", "001035.62 80 002000.06 70",
     "line 20  LF(BU,2),X LRIN+1.50"),
    ("001566.00", "400000.00 80 402000.23 10", "line 21  KFI(BU,2),(2)10"),
    ("001567.00", "001601.37 42",             "line 22  BAH,X32"),
    ("001567.40", "002151.10 80 002000.20 D0",
     "line 23  ST(BU,2),S COM RG+.8  - ENTER MODE IN COM REG"),
    ("001570.40", "002151.11 80 001661.74 02",
     "line 24  X MODE 3  BB,S COM RG+.9,X36  -IF OFFLINE MODE"),
    ("001571.40", "002151.10 80 001617.34 02",
     "line 25  BB,S COM RG+.8,X33AA  -NO*IF BYPASS"),
    ("001572.40", "001647.50 00",
     "line 26  B,X35  -OVERLAPPED MODE ON LINE"),
    # ---- the two control words and the message ----
    ("001573.00", "001037.00+ 100 000003 001574",
     "line 27  X MO CW  CW,X ZEROS,3,X MO CW1(.25)1"),
    ("001574.00", "001575.00+ 000 000004 000000",
     "line 28  X MO CW1  CW,X MODE,X MODE K  -CW USED TO REQUEST MODE"),
    ("001575.00", "375",
     "line 31  X MODE  DD(BU,8),(2)1111 1101  -CONTROL CODE CARRIAGE RETURN"),
    # Lines 32's twenty-eight characters are what put these two
    # where they are: the message runs from 001575.10 to 001600.50,
    # and nothing in the deck states that -- the DD counts it.
    ("001600.50", "375",
     "line 33  DD(BU,8),(2) 1111 1101  -CARRIAGE RETURN"),
    ("001600.60", "376",
     "line 34  DD(BU,8),(2) 1111 1110  -END OF MSG"),
]

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP p.30 "))
