#!/usr/bin/env python3
"""verify_mcp_bootstrap_p28.py -- MCP INITIALIZATION, printed page 28:
computing the base of MCP and of the MCP IO location table, the PROSA
size check, and the start of relocation
(../decks/mcp_bootstrap_p28.strap).
docs/MCP_Mar63_001-249.pdf PDF p.35, header "PAGE NUMBER 28".
AGENTS.md rule 3.

Twenty-nine printed rows with binary output, lines 5-51, and ten
symbol locations.

>>> THE FIRST PAGE OF THE MCP WITH VFL ARITHMETIC ON IT.  Everything
before this page has been index arithmetic, transmits, branches and
connectives.  Here the bootstrap computes with the variable-field-
length unit -- 18-bit unsigned fields at bit offset 46 of a word:

    L(BU,18),S MARK,46     -(BU,18),S LR BU,46     LC,$11,$R

Bits 46-63 is the last 18 bits of a 64-bit word, so a (BU,18) at .46
is "the low 18 bits" written the only way a bit-addressed machine
can write it.  THE ASSEMBLER NEEDED NOTHING FOR ANY OF IT. <<<

>>> EVERY EXTERNAL ADDRESS HERE WAS DECODED, NOT READ.  The layout
that makes that possible is printed in the Reference Manual on
printed p.19 (PDF 22), under "Instruction Format" and "Operand
Address" -- a page the manual's index does not point at, reached
from the CONTENTS line "Index Format ... 19":

    Figure 6's second diagram:   | ADDRESS | J | OP. | I |

    "A half word operand is implied by most branch, index
     modification, and transmit operations.  This group of operations
     has an address part of 19 BITS.  The 18 high-order bits address
     full words.  THE LOW-ORDER BIT ADDRESSES THE FIRST OR SECOND
     HALF of the full word."

So bits 0-17 are the word, bit 18 is the half-word selector, J is at
19-22 and the operation runs to bit 27.  "LC,$12,S MAX RN" prints
".70" = 111000: half 1, register 1100 = $12 -- so S MAX RN is at
002155.40 and not 002155.00.  Twenty-nine rows agree with eleven
addresses read that one way.

The same sentence settles the VFL rows BY EXCLUSION: integer
arithmetic and connectives "ha[ve] an address part of 24 bits", so
"L(BU,18),S MARK,46" carries no J and no half-selector, and its
printed 002162.40 is a plain bit address. <<<

CONTIGUOUS WITH p.27 BY FALL-THROUGH, not by branch: p.27 ends with
"BXL,X25 2" at 001507.00, a half word, and this page's first
instruction is at 001507.40.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p28.strap").read())

SYMBOLS = {
    "X261":   "001507.40",
    "X262":   "001512.00",
    "X263":   "001514.00",
    "X264":   "001514.40",
    "X265":   "001515.00",
    "XERR26": "001517.40",
    "X28":    "001523.00",
    "X29":    "001525.40",
    "X292":   "001527.00",
    "X295":   "001531.40",
}

ROWS = [
    # ---- compute base of MCP and MCP IO location table ----
    ("001507.40", "002162.40 80 022027.20 50",
     "line 5   X26 1  L(BU,18),S MARK,46  -UPPER BOUND OF TABLES"),
    ("001510.40", "002155.00 80 022027.30 10",
     "line 6   -(BU,18),S LR BU,46  -LESS LOWER BOUND"),
    ("001511.40", "000011.26 50",         "line 7   LC,$11,$R  -SIZE OF TABLE"),
    ("001512.00", "002152.00 80 022027.20 50",
     "line 8   X26 2  L(BU,18),S X CHAN,46  -BASE OF CST"),
    ("001513.00", "000033.34 80 022027.30 10",
     "line 9   -(BU,18),$11+.28,46  -LESS SIZE OF ASSIGNMENT TABLES"),
    ("001514.00", "000011.30 30",         "line 10  X26 3  LV,$12,$R  -BASE OF MCP"),
    ("001514.40", "002150.31 30",
     "line 11  X26 4  SV,$12,S MCP  -SAVE BASE OF MCP IN COM REGION"),
    ("001515.00", "002153.31 30",
     "line 12  X26 5  SV,$12,S BAMCP  -SAVE BASE OF MCP IO LOCATION TABLE"),
    ("001515.40", "002155.00 80 022027.30 10",
     "line 13  -(BU,18),S LR BU,46  -BIAS FACTOR FOR RELOCATION"),
    # ---- test for correct size of PROSA ----
    ("001516.40", "002157.00 30",
     "line 18  LV,$0,S DK MCP  -GET COUNT OF PROSA ARCS"),
    ("001517.00", "000621.40 90",
     "line 19  KV,$0,X UPDAT  -TEST AGAINST COUNT OF PROSA RECORDS ON TAPE"),
    ("001517.40", "000551.00 80",         "line 21  X ERR 26  SIC,X ERR AD"),
    ("001520.00", "000133.32 C0",
     "line 22  BZXE,X ERROR  -IF PROSA ARC COUNT EQUALS ARCS ASSIGNED"),
    ("001520.40", "000007.01 05",
     "line 24  V+I,$0,(8)7.0  -ROUND TO NUMBER OF TRACKS"),
    ("001521.00", "000020.17 80 003000.00 F0", "line 25  CM0000(BU,3),$0+.15"),
    ("001522.00", "002157.01 30",         "line 26  SV,$0,S DK MCP  -SAVE TRACK ADDRESS"),
    ("001522.40", "002157.41 30",         "line 27  SV,$0,S SYRFT  -SAVE TRACK ADDRESS"),
    # ---- compute size of MCP IO location table ----
    ("001523.00", "000034.00 80 022000.06 70",
     "line 33  X28  LF(BU,18),$12  -ENTER BASE OF MCP"),
    ("001524.00", "002155.70 50",
     "line 34  LC,$12,S MAX RN  -GET SIZED IO LOCATION TABLE"),
    ("001524.40", "002155.30 30",
     "line 35  LV,$12,S LR BU  -GET LOCATION OF IO LOCATION TABLE"),
    ("001525.00", "000001.31 00",
     "line 36  C+I,$12,1.0  -ADD ONE TO MAXIMUM REFERENCE NUMBER"),
    # ---- begin relocation: file area actuated entry ----
    ("001525.40", "001551.71 4A",
     "line 43  X29  CBZ+,$12,X31 2  -GET THE CURRENT FAT ADDRESS"),
    ("001526.00", "000000.26 3C",         "line 45  LV,$11,0.0($12)  -GET UAT ADDRESS"),
    ("001526.40", "001525.71 42",         "line 46  BXVZ,X29  - IF ZERO TABLE ELEMENT"),
    ("001527.00", "000003.00 8B 022000.23 10", "line 47  X29 2  KF(BU,18),3.0($11)"),
    ("001530.00", "001547.36 42",         "line 48  BAL,X 31"),
    ("001530.40", "000003.00 8B 022027.22 90",
     "line 49  M+MG(BU,18),3.0($11),46  -BIAS FAT LAST ACTIVATED ENTRY"),
    ("001531.40", "000010.22 1B",
     "line 50  X29 5  LX,$9,8.0($11)  -GET UAT REEL ENTRIES"),
    ("001532.00", "001537.71 42",
     "line 51  BXVZ,X30 4  -IF TAPE * NO TO BIAS UAT ADDRESS IN CST OR UST"),
]

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP p.28 "))
