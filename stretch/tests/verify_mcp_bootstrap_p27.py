#!/usr/bin/env python3
"""verify_mcp_bootstrap_p27.py -- MCP INITIALIZATION, printed page 27:
"TO ASSIGN", the tape-mounting message, and "TO MOVE"
(../decks/mcp_bootstrap_p27.strap).
docs/MCP_Mar63_001-249.pdf PDF p.34, header "PAGE NUMBER 27".
AGENTS.md rule 3.

Thirty printed rows with binary output, lines 5-48, and twelve
symbol locations.

>>> NO ASSEMBLER WORK.  This is the first page since p.17 that the
assembler took as it stood.  Its one unfamiliar form, XW with a
NEGATIVE value AND a flag field, was already right:

    line 9   XW,-1,0,0,4    -> 000000.01- 100 000000 000000
    line 40  XW,-1.0,0,0,6  -> 000001.00- 110 000000 000000

C22-6531 printed p.18 says the sign is bit 24 of the value field and
the flag digit occupies bits 25-27, and both rows print exactly that:
the same magnitude written two ways (-1 bit versus -1.0 words) lands
in the same 24-bit value field two places apart. <<<

>>> SECTION 13 OF docs/listing_typography.md, FIVE TIMES ON ONE PAGE.
Lines 5 and 36 are the same instruction -- LVI,$15,<a label on this
page> -- and the drum printed the trailing byte as "C1" on both.  It
is 01.  The page proves it against itself: the two rows differ ONLY
in bit 18, the half-word selector of their operands (X24 2 at .00
prints .37, p.26's X23 3 at .40 printed .77), so their opcode bytes
cannot differ.  Rows 9, 21, 25 and 27 carry the same glyph in octal columns, where a
C cannot occur at all -- line 21's second group prints "002000.2C A0"
and the C is the 0 of .20.

But the page also prints a REAL C, twice, and in the same column that
lied on lines 5 and 36: lines 23 and 24 end "AC", where the C is the
index register $12 of "0.0($12)".  Line 21, with no index, ends "A0"
one row above it.  The glyph alone decides nothing; what decides is
that an octal column cannot hold a C and an index field can.  The
first draft of this file read both AC rows as A0 and the assembler
caught it. <<<

CROSS-PAGE CHECK: X24, this page's first label, sits at 001464.00 --
the address p.26 line 33's "B,X24" was already compiled to print.
Two pages transcribed a week apart agree on one branch target.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p27.strap").read())

# Defined INSIDE the transcribed range: these are the real check that
# addresses land where the listing's own location column says.
SYMBOLS = {
    "X24":    "001464.00",
    "X241":   "001466.40",
    "X242":   "001467.00",
    "XERR24": "001470.40",
    "X24A":   "001472.00",
    "X24A2":  "001473.00",
    "X24A3":  "001474.40",
    "X25":    "001500.00",
    "X251":   "001501.00",
    "X252":   "001502.00",
    "X253":   "001503.00",
    "XERR25": "001504.40",
}

ROWS = [
    # ---- TO ASSIGN ----
    ("001464.00", "001467.37 01",
     "line 5   X24  LVI,$15,X24 2  -ENTER PARAMETER LOCATION"),
    ("001464.40", "004474.25 80 001000.36 F0",
     "line 6   CM1111(BU,1),T IPLB1+.21  -CONVERT BE IN ASSIGN TO BD"),
    ("001465.40", "004540.65 80 001000.36 F0",
     "line 7   CM1111(BU,1),T IPLB2+.21  -CONVERT BE IN ASSIGN TO BD"),
    ("001466.40", "003701.10 00",           "line 8   X24 1  B,T ASIGN"),
    ("001467.00", "000000.01- 100 000000 000000",
     "line 9   X24 2  XW,-1,0,0,4  -MODE"),
    ("001470.00", "001467.00 10",
     "line 11  LX,$0,X24 2  -INITIALIZE $IND"),
    ("001470.40", "000551.00 80",           "line 12  X ERR 24  SIC,X ERR AD"),
    ("001471.00", "000133.30 40",
     "line 13  BZXCZ,X ERROR  -IF ASSIGNMENT ERROR"),
    ("001471.40", "001500.10 00",           "line 14  B,X25"),
    # ---- enter the tape mounting message in the message block ----
    ("001472.00", "004455.01 80 004570.74 00",
     "line 20  X24 A  BZB,T SBHDI,T PENY  -IF PASSED OVER FIRST TWO"),
    ("001473.00", "004432.00 80 002000.20 A0",
     "line 21  X24 A 2  TI,8,T BUFB1,X MSG BK  -SAVE CURRENT MESSAGE"),
    ("001474.00", "001473.71 B0",
     "line 22  LVE,$12,X24A2+.32  -GET CURRENT MESSAGE LOCATION"),
    ("001474.40", "001773.00 80 000000.02 AC",
     "line 23  X24 A 3  TI,1,X MSG,0.0($12)  -REPLACE MSG PREFIX"),
    ("001475.40", "001774.00 80 000011.02 AC",
     "line 24  TI,1,X MSG CR,9.0($12)  -INSERT CARRIAGE RETURN"),
    ("001476.40", "000012.31 05",           "line 25  V+I,$12,10.0"),
    ("001477.00", "001473.71 D0",
     "line 26  SVA,$12,X24A2+.32  -NEXT AVAILABLE MESSAGE SLOT"),
    ("001477.40", "004575.50 00",           "line 27  B,T P3"),
    # ---- TO MOVE ----
    ("001500.00", "000024.34 30",
     "line 32  X25  LV,$14,$4  -GET THE BASE OF AREA CONTAINING IOD"),
    ("001500.40", "000001.35 05",
     "line 35  V+I,$14,1.0  -ADVANCE TO ALPHA +1.0"),
    ("001501.00", "001503.37 01",
     "line 36  X25 1  LVI,$15,X25 3  -ENTER MOVE LINKAGE PARAMETER"),
    ("001501.40", "001503.35 D0",           "line 37  SVA,$14,X25 3"),
    ("001502.00", "005014.10 00",           "line 39  X25 2  B,T MOVE"),
    ("001503.00", "000001.00- 110 000000 000000",
     "line 40  X25 3  XW,-1.0,0,0,6  -IOD TABLE LOCATION/EXIT DISP"),
    ("001504.00", "001503.00 10",
     "line 42  LX,$0,X25 3  -SET UP TO TEST ERROR"),
    ("001504.40", "000551.00 80",           "line 43  X ERR 25  SIC,X ERR AD"),
    ("001505.00", "000133.30 40",
     "line 44  BZXCZ,X ERROR  -IF MOVE ERROR"),
    ("001505.40", "000017.35 05",
     "line 45  V+I,$14,15.0  -ADVANCE TO NEXT TABLE"),
    ("001506.00", "000027.34 90",
     "line 46  KV,$14,$7  -TEST CURRENT TABLE ADDRESS"),
    ("001506.40", "001503.35 30",           "line 47  SV,$14,X25 3"),
    ("001507.00", "001502.32 42",
     "line 48  BXL,X25 2  -IF PROCESSED LAST TABLE"),
]

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP p.27 "))
