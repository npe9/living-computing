#!/usr/bin/env python3
"""verify_mcp_bootstrap_p26.py -- MCP INITIALIZATION, printed page 26:
"TO DECODE" (../decks/mcp_bootstrap_p26.strap).
docs/MCP_Mar63_001-249.pdf PDF p.33, header "PAGE NUMBER 26".
AGENTS.md rule 3.

Twenty-six printed rows with binary output.

>>> THE ASSEMBLER GAINED "CF" FOR THIS PAGE, and C22-6531 gave the
rounding rules that the page's own locations then check. <<<

  printed p.19:  4. CF "COUNT FIELD"  CF, COUNT
  "The location counter is rounded to the next HALF word.  The
   contents of the count field are compiled as an 18-BIT INTEGER IN
   POSITIONS 0-17.  The location counter stands at BIT 18 at the end
   of the operation."
  5. RF "REFILL FIELD" -- "the same as CF, except Refill is
   substituted for Count."

  printed p.18:  3. VF "VALUE FIELD"  VF, VALUE
  "...compiled as a 24-bit plus sign quantity in positions 0-24 of
   the next half word.  THE LOCATION COUNTER STANDS AT BIT 25 at the
   end of the operation."

and the same page's table says the widths again as data descriptions:
XW (BU), VF (B,25), CF or RF (BU,18).

LINES 14-18 ARE THE CHECK, and they only come out right if BOTH
rules hold: the VF at 001447.40 ends at bit 25, the CF after it
rounds to 001450.00, that CF ends at bit 18, and the VF after THAT
rounds to 001450.40.  VF had been emitting a whole half word --
claiming seven bits it does not own -- which never showed until a CF
had to share a boundary with one.  Both widths are now what the
manual says.

THE CF ROWS PRINT 000001: six octal digits, eighteen bits, no sign
and no hex byte, which is exactly how this listing prints an 18-bit
field and not how it prints a half word.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p26.strap").read())

SYMBOLS = {
    "X23":    "001444.00",
    "X231":   "001444.40",
    "X232":   "001446.00",
    "X232A":  "001447.00",
    "X233":   "001447.40",
    "X23N":   "001451.40",
    "X234":   "001452.00",
    "X235":   "001453.00",
    "X236":   "001454.40",
    "XLAST":  "001462.00",
}

_XW = "000000.00+ 000 000000 000000"

ROWS = [
    ("001444.00", "000024.34 30",
     "line 5   X23  LV,$14,$4  -GET BASE OF AREA CONTAINING IOD"),
    ("001444.40", "001447.77 01",
     "line 7   X23 1  LVI,$15,X23 3  -ENTER DECODE LINKAGE PARAMETER"),
    ("001445.00", "002201.25 80 001000.36 F0",
     "line 9   CM1111(BU,1),Y IPL 1+.21  -MAKE BE IN UNCODE INTO BD"),
    ("001446.00", "000001.35 05",
     "line 10  X23 2  V+I,$14,1.0  -ADVANCE POINTER TO SECOND WORD"),
    ("001446.40", "001447.75 D0",            "line 12  SVA,$14,X23 3"),
    ("001447.00", "002737.10 00",            "line 13  X23 2A  B,LDECOD  -TO DECODE ROUTINE"),
    ("001447.40", "000000.00+",
     "line 14  X23 3  VF,0.0  -LOCATION OF TABLE TO BE PROCESSED (ALPHA)"),
    ("001450.00", "000001",                  "line 16  CF,1.0  -NON ZERO FOR BYPASS MODE"),
    ("001450.40", "000000.00+",              "line 17  VF,0.0  -ERROR DISPOSITION"),
    ("001451.00", "001452.10 00",            "line 18  B,X23 4  -ERROR RETURN"),
    ("001451.40", "001453.10 00",            "line 19  X23 N  B,X23 5  -NORMAL"),
    ("001452.00", "000551.00 80",            "line 20  X23 4  SIC,X ERR AD"),
    ("001452.40", "000133.10 00",
     "line 21  B,X ERROR  -IO REQUIREMENTS REJECTED"),
    ("001453.00", "000016.35 05",
     "line 22  X23 5  V+I,$14,14.  -ADVANCE TO NEXT TABLE"),
    ("001453.40", "000027.34 90",
     "line 23  KV,$14,$7  -TEST NEXT TABLE ADDRESS FOR ADDRESS OF MCPP CARD"),
    ("001454.00", "001446.32 42",
     "line 25  BXL,X23 2  -IF PROCESSED LAST TABLE"),
    ("001454.40", "001434.00 80 001461.02 A0",
     "line 26  X23 6  TI,1,X22 2AA,X LAST-1.0  -ENTER NAME AT ALPHA-1.0"),
    ("001455.40", "000037.00 80",            "line 27  SIC,$15"),
    ("001456.00", "002737.10 00",            "line 28  B,L DECOD"),
    ("001456.40", "001462.00+",              "line 29  VF,X LAST  -LOCATION OF ALPHA"),
    ("001457.00", "000001",                  "line 30  CF,1  -BYPASS MODE"),
    ("001457.40", "000000.00+",              "line 31  VF,0  -ERROR DISPOSITION"),
    ("001460.00", "001452.10 00",            "line 32  B,X23 4  -ERROR RETURN"),
    ("001460.40", "001464.10 00",            "line 33  B,X24  -NORMAL RETURN"),
    ("001461.00", _XW,
     "line 34  XW,0  -TABLE SLOTS FOR LAST TIME THROUGH"),
    ("001462.00", _XW,                       "line 35  X LAST  XW,0"),
    ("001463.00", _XW,                       "line 36  XW,0"),
]

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP p.26 "))
