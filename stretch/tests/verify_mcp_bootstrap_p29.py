#!/usr/bin/env python3
"""verify_mcp_bootstrap_p29.py -- MCP INITIALIZATION, printed page 29:
relocation of the reel addresses and of the file/unit area tables
(../decks/mcp_bootstrap_p29.strap).
docs/MCP_Mar63_001-249.pdf PDF p.36, header "PAGE NUMBER 29".
AGENTS.md rule 3.

Twenty-five printed rows with binary output, lines 6-38, and eleven
symbol locations.

>>> FOUR CROSS-PAGE CHECKS, IN BOTH DIRECTIONS.  printed p.28 was
transcribed first and its branch encodings fixed three addresses
before this page was opened; the page's own location column now
states all three, and one branch here closes the loop backwards:

  p.28 l.51  BXVZ,X30 4      001537.71 42   ->  X30 4  001537.40
  p.28 l.48  BAL,X31         001547.36 42   ->  X31    001547.00
  p.28 l.43  CBZ+,$12,X31 2  001551.71 4A   ->  X31 2  001551.40
  p.29 l.35  B,X29           001525.50 00   ->  X29    001525.40 (p.28)

A branch address that two independently transcribed pages agree on is
not a reading -- it is a measurement. <<<

>>> AND NO ASSEMBLER WORK, for the second page running.  The one row
that looked like it needed some, line 38's "T,$11,...", is the
corpus's ordinary direct-count TRANSMIT written with the listing's
register spelling; the deck writes the bare "11" that every other
TRANSMIT in decks/ writes, and Reference Manual printed p.30 says
what that field is: "the field J, bits 51-54, SPECIFIES AN INDEX
REGISTER". <<<
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p29.strap").read())

SYMBOLS = {
    "X30":   "001532.40",
    "X301":  "001533.00",
    "X302":  "001533.40",
    "X303":  "001535.40",
    "X304":  "001537.40",
    "X305":  "001541.40",
    "X305A": "001542.40",
    "X306":  "001544.00",
    "X31":   "001547.00",
    "X311":  "001551.00",
    "X312":  "001551.40",
}

ROWS = [
    ("001532.40", "000000.24 39",
     "line 6   X30  LV,$10,0.0($9)  -GET NEXT REEL ADDR ENTRY"),
    ("001533.00", "001535.71 42",
     "line 7   X30 1  BXVZ,X30 3  -IF NEXT REEL ADDRESS"),
    ("001533.40", "000000.00 89 022000.22 90",
     "line 8   X30 2  M+MG(BU,18),0.0($9)  -BIAS NEXT REEL ADDR"),
    ("001534.40", "000000.22 3A",
     "line 9   LV,$9,0.0($10)  -SET UP FOR NEXT"),
    ("001535.00", "001532.50 00",
     "line 10  B,X30  -MORE BIASING TO BE DONE"),
    ("001535.40", "000010.00 8B 022027.22 90",
     "line 11  X30 3  M+MG(BU,18),8.0($11),46  -BIAS FIRST REEL ADDR"),
    ("001536.40", "000010.40 8B 022027.22 90",
     "line 12  M+MG(BU,18),8.32($11),46  -BIAS CURRENT REEL"),
    ("001537.40", "000033.32 30",
     "line 21  X30 4  LV,$13,$11  -GET COPY OF UAT"),
    ("001540.00", "000000.34 3D",
     "line 22  LV,$14,0.0($13)  -GET CHANNEL"),
    ("001540.40", "000036.34 B0",            "line 23  V+,$14,$14  -DOUBLE IT"),
    ("001541.00", "002152.34 B0",
     "line 24  V+,$14,S X CHAN  -GET CST ENTRY"),
    ("001541.40", "000000.33 8E 001544.34 02",
     "line 25  X30 5  BB,.27($14),X30 6  -IF MULTI UNIT"),
    ("001542.40", "000000.00 8E 022027.22 90",
     "line 26  X30 5 A  M+MG(BU,18),0.0($14),46  -FORM BIASED UAT ADDR"),
    ("001543.40", "001547.10 00",            "line 27  B,X31  -GO TO BIAS IO"),
    ("001544.00", "000000.34 3E",
     "line 28  X30 6  LV,$14,0.0($14)  -GET BASE OF UST"),
    ("001544.40", "000000.74 BD",
     "line 29  V+,$14,.32($13)  -GET UST ENTRY"),
    ("001545.00", "000000.00 8E 022000.23 10",
     "line 30  KF(BU,18),0.0($14)"),
    ("001546.00", "001547.36 42",            "line 31  BAL,X31  -IF NO BIASING"),
    ("001546.40", "001542.50 00",
     "line 32  B,X30 5 A  -GO TO BIAS UAT"),
    ("001547.00", "000000.00 8C 022027.22 90",
     "line 33  X31  M+MG(BU,18),0.0($12),46  -BIAS UAT"),
    ("001550.00", "000000.40 8C 022027.22 90",
     "line 34  M+MG(BU,18),.32($12),46  -BIAS FAT"),
    ("001551.00", "001525.50 00",
     "line 35  X31 1  B,X29  -PROCESS NEXT IO LOCATION"),
    ("001551.40", "002150.34 30",
     "line 36  X31 2  LV,$14,S MCP  -GET BASE OF MCP"),
    ("001552.00", "002155.32 30",
     "line 37  LV,$13,S LR BU  -GET BASE OF DEBIASED"),
    ("001552.40", "000000.00 8D 000000.26 2E",
     "line 38  T,$11,0.0($13),0.0($14)  -MOVE THE RELOCATED"),
]

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP p.29 "))
