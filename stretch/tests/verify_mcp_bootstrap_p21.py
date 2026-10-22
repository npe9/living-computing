#!/usr/bin/env python3
"""verify_mcp_bootstrap_p21.py -- MCP INITIALIZATION, printed page 21:
"MCP SOURCE TAPE VERIFICATION" (../decks/mcp_bootstrap_p21.strap).
docs/MCP_Mar63_001-249.pdf PDF p.28, header "PAGE NUMBER 21".
AGENTS.md rule 3.

Twenty-eight printed rows with binary output.

WHAT THE PAGE DOES: it prints the IPL tape's date on the console, so
the operator can see which system he has just loaded.  It gets the
console channel out of the communication region -- which printed p.20
put there -- suppresses leading zeros digit by digit, patches the
four digits into the message text with M+MG, and writes it.

>>> THE MESSAGE IS PATCHED IN PLACE.  Lines 37-38 are
"(IQS*)DD(BU,64,8),00 MONTH *" and ",00 DAY  *": the text carries
zeros as PLACEHOLDERS and lines 17-20 ADD four-bit digits into them.
That is why the leading-zero suppression CLEARS a digit rather than
skipping it -- a cleared placeholder prints as a blank. <<<

THREE ROW KINDS ARE DELIBERATELY ABSENT FROM THE TABLE BELOW, and
each for a reason that is itself a fact about the listing:

  * The (IQS*)DD rows, 35/37/38, print NOTHING in the binary output
    column, exactly as printed pp.9-12's message rows do.  No
    character code is checked because none is printed.  What pins
    their text lengths instead is the LOCATION of everything after
    them, which the symbol table below checks: X MONTH at 001047.50
    and X DAY at 001050.60 are only reachable if line 35 is eighteen
    characters and X MONTH is nine.
  * The DR rows, 26 and 28, print "000003.00" -- the RESERVED SIZE,
    not a stored word.  Nothing is emitted at those addresses.
  * Line 42's SYN prints its VALUE, "000005.00+ ... BU,10 ,10", which
    is a symbol definition and not storage either.  It is checked as
    X DATE K == 000005.00 in SYMBOLS.

THE BRANCH-ADDRESS FIELD IS NINETEEN BITS AND THE PRINTED FORM HIDES
IT.  Line 23's output is "000057.50 00": the ".50" group is
instruction bits 18-23 and bit 18 is the HALF-WORD selector, so
101000 is word 000057, right half -- location 000057.40.  Read as a
plain bit offset 0o50 is 40 decimal, not a half-word boundary at all.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p21.strap").read())

SYMBOLS = {
    "XDATE":  "001012.00",
    "XDATE2": "001015.40",
    "XDATE3": "001020.40",
    "XDATE4": "001022.40",
    "XDATE5": "001025.40",
    "XLRIN":  "001034.00",
    "XZEROS": "001037.00",
    "XDCW":   "001042.00",
    "XDCW1":  "001043.00",
    "XDCW2":  "001044.00",
    "XDATE1": "001045.00",
    "XMONTH": "001047.50",
    "XDAY":   "001050.60",
    "XDATEK": "000005.00",
}

ROWS = [
    ("001012.00", "002156.36 30",
     "line 5   X DATE  LV,$15,SY CO CH  -GET CONSOLE CHANNEL"),
    ("001012.40", "000043.00 80 040000.20 50", "line 6   L(BU,32),X VERFY"),
    ("001013.40", "000011.44 80 001015.74 00",
     "line 7   BZB,$R+.36,X DATE 2  -IF A-8 ZERO"),
    ("001014.40", "000011.44 80 004000.00 F0",
     "line 8   CM0000(BU,4),$R+.36  -YES * CLEAR TENS DIGIT OF MONTH"),
    ("001015.40", "000011.54 80 001020.74 00",
     "line 9   X DATE 2  BZB,$R+.44,X DATE 3  -IF A-8 ZERO, EIGHT, OR NINE"),
    ("001016.40", "000011.56 80 001020.74 00",
     "line 10  BZB,$R+.46,X DATE 3  -YES * IF A-8 ZERO"),
    ("001017.40", "000011.54 80 004000.00 F0",
     "line 11  CM0000(BU,4),$R+.44  -YES*CLEAR UNITS DIGIT OF MONTH"),
    ("001020.40", "000011.64 80 001022.74 04",
     "line 12  X DATE 3  BZBZ,$R+.52,X DATE 4  -IF A-8 ZERO"),
    ("001021.40", "000011.64 80 004000.00 F0",
     "line 13  CM0000(BU,4),$R+.52  -YES * CLEAR TENS DIGIT OF DAY"),
    ("001022.40", "000011.74 80 001025.74 00",
     "line 14  X DATE 4  BZB,$R+.60,X DATE 5  -IF A-8 ZERO, EIGHT, OR NINE"),
    ("001023.40", "000011.76 80 001025.74 00",
     "line 15  BZB,$R+.62,X DATE 5  -YES * IF A-8 ZERO"),
    ("001024.40", "000011.74 80 004000.00 F0",
     "line 16  CM0000(BU,4),$R+.60  -CLEAR UNITS DIGIT OF DAY"),
    ("001025.40", "001047.53 80 004014.22 90",
     "line 17  X DATE 5  M+MG(BU,4),X MONTH+.3,24  -GET TENS DIGIT"),
    ("001026.40", "001047.63 80 004010.22 90",
     "line 18  M+MG(BU,4),X MONTH+.8+.3,16  -GET UNITS DIGIT"),
    ("001027.40", "001050.63 80 004004.22 90",
     "line 19  M+MG(BU,4),X DAY+.3,8  -GET TENS DIGIT"),
    ("001030.40", "001050.73 80 004000.22 90",
     "line 20  M+MG(BU,4),X DAY+.8+.3  -GET UNITS DIGIT"),
    ("001031.40", "000000.00 8F 001042.13 00",
     "line 21  W(SEOP),0.0($15),X D CW  -IDENTIFY DATE OF SOURCE TAPE"),
    ("001032.40", "000066.40 80",            "line 22  SIC,X7 3"),
    ("001033.00", "000057.50 00",            "line 23  B,X7 1  -IO TEST"),
    ("001033.40", "001052.10 00",
     "line 24  B,XIO  -TO IO STATUS REPORT"),
    ("001042.00", "001037.00+ 100 000003 001043",
     "line 29  X D CW  CW,X ZEROS,3,X D CW 1(.25)1"),
    ("001043.00", "001045.00+ 000 000005 000000",
     "line 30  X D CW 1  CW,XDATE1,XDATEK,0  -CW USED TO STATE DATE"),
    ("001044.00", "001034.00+ 000 000003 000000",
     "line 31  X D CW 2  CW,X LR IN,3,0  -CW USED TO GET IPL OPTIONS"),
    ("001045.00", "375",
     "line 33  X DATE 1  DD(BU,8),(2)1111 1101  -INITIAL CARRIAGE RETURN"),
    ("001045.10", "002",                     "line 34  DD(BU,8),(2)00000010  -RED$"),
    ("001047.40", "375",
     "line 36  DD(BU,8),(2)1111 1101  -CARRIAGE RETURN FOR FIRST LINE"),
    ("001051.60", "375",
     "line 39  DD(BU,8),(2)1111 1101  -CARRIAGE RETURN FOR SECOND LINE"),
    ("001051.70", "376",
     "line 40  DD(BU,8),(2) 1111 1110  -END OF MSG"),
]

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP p.21 "))
