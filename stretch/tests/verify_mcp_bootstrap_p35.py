#!/usr/bin/env python3
"""verify_mcp_bootstrap_p35.py -- MCP INITIALIZATION, printed page 35:
"MCP IPL DEFINITIONS" -- the card types in Hollerith, THE EQUIPMENT
TABLE, and the MCP pseudo-op codes
(../decks/mcp_bootstrap_p35.strap).
docs/MCP_Mar63_001-249.pdf PDF p.42, header "PAGE NUMBER 35".
AGENTS.md rule 3.

Thirty-two printed data rows and ten symbol locations -- every row
on the page.

>>> THE EQUIPMENT TABLE IS HERE, PRINTED, and tests/gen_mcp_p17_tb.py
has been SYNTHESISING it since the testbench was written: an invented
order and one known code.  X EQP T at 001752.00 is nine entries of
DD(BU,24) + DD(BU,4) + DD(BU,1) -- twenty-nine bits each:

  bits 0-23   the SECOND LETTER of the two-letter equipment code,
              as its twelve-bit CARD COLUMN, right-justified
  bits 24-27  the equipment code
  bit 28      1 for a MULTI-UNIT channel, 0 for single

  entry  column  letter       code  multi   the page's own comment
      0  000000  (none)          0      0   -NO EQUIPMENT
      1  002200  K  (11-2)       1      0   -DISK * DK
      2  002020  N  (11-5)       2      0   -CONSOLE *CN
      3  004040  D  (12-4)       3      0   -READER * RD
      4  001040  U  (0-4)        4      0   -PUNCH *PU
      5  002001  R  (11-9)       5      0   -PRINTER * PR
      6  000000  (none)          0      0   -UNUSED
      7  000000  (none)          0      0   -UNUSED
      8  002004  P  (11-7)      10      1   -TAPE MULTI * TP

THE SECOND LETTER ALONE IDENTIFIES THE UNIT.  This repository had
already noticed that C22-6728 p.88's CN/DK/PR/PU/TP/RD have second
letters N,K,R,U,P,D, all distinct; this table is WHY that matters --
MCP never looks at the first letter.  The twelve-bit columns are
checked against strap/cards.py below, which gets them from
C22-6678-1 Appendix F, so two documents agree on six letters.

TWO OF THE CODES WERE ALREADY KNOWN from the programs that use them
-- console = 2 (printed p.20 line 14's "LFI(BU,4),(8)2") and printer
= 5 (printed p.25 line 17) -- and both agree.  The other seven are
new, and so is the ORDER. <<<

>>> AND THE WIDTHS ARE STATED, NOT GUESSED.  The listing prints a
DD as bare octal digits and the digit count does not determine the
width: three digits is 7, 8 or 9 bits.  This page puts DD(BU,24),
DD(BU,4) and DD(BU,1) next to each other, so a guessed width would
silently read the next datum's bits.  Every row below passes its
width to the oracle. <<<

Lines 44-48's five SYNs close four cross-page loops: D MCP is
printed p.27's X24A, D RET is printed p.34 line 45's operand, S JC4
is printed p.33 line 43's, S COMD is printed p.33 lines 27 and 36's.
None of the four was read off this page.
"""
import sys

from cards import column_bits
from listing_oracle import check_rows, finish, loc_bits, read_bits
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p35.strap").read())

SYMBOLS = {
    "XPROWR": "001746.00",
    "XMCPP":  "001747.00",
    "XIOCD":  "001747.60",
    "XIOD":   "001750.40",
    "XEQPT":  "001752.00",
    # The five pseudo-op codes.  Four of these are addresses earlier
    # pages compiled into instructions before this page was opened.
    "DMCP":   "001472.00",
    "DRET":   "000041.00",
    "DCOMM":  "000043.40",
    "SJC4":   "000116.40",
    "SCOMD":  "000120.00",
}

ROWS = [
    ("001746.00", "000000.00+ 000 000000 000000",
     "line 5   X PROWR  XW,0  -COMPUTED DISK WRITE CW CARDS"),
    ("001747.00", "2040410020042004",
     "line 8   X MCPP  DD(BU,48),(8)2040410020042004  -MCPP IN HOLLERITH", 48),
    ("001747.60", "4001201041004040",
     "line 9   X IOCD  DD(BU,48),(8)4001201041004040  -IOCD IN HOLLERITH", 48),
    ("001750.40", "400120104040",
     "line 10  X IOD  DD(BU,36),(8)400120104040  -IOD IN HOLLERITH", 36),
    ("001751.40", "000000.30 00",
     "line 12  CNOP  -START XEQPT AT FULL WORD BOUNDARY"),
    # ---- the equipment table, nine entries of 24 + 4 + 1 bits ----
    ("001752.00", "00000000", "line 14  X EQP T  DD(BU,24),(8)0000", 24),
    ("001752.30", "00",       "line 15  DD(BU,4),(8)0  -NO EQUIPMENT", 4),
    ("001752.34", "0",        "line 16  DD(BU,1),0  -SINGLE UNIT CHANNEL", 1),
    ("001752.35", "00002200", "line 17  DD(BU,24),(8)2200", 24),
    ("001752.65", "01",       "line 18  DD(BU,4),(8)1  -DISK * DK", 4),
    ("001752.71", "0",        "line 19  DD(BU,1),0  -SINGLE UNIT CHANNEL", 1),
    ("001752.72", "00002020", "line 20  DD(BU,24),(8)2020", 24),
    ("001753.22", "02",       "line 21  DD(BU,4),(8)2  -CONSOLE *CN", 4),
    ("001753.26", "0",        "line 22  DD(BU,1),0  -SINGLE UNIT CHANNEL", 1),
    ("001753.27", "00004040", "line 23  DD(BU,24),(8)4040", 24),
    ("001753.57", "03",       "line 24  DD(BU,4),(8)3  -READER * RD", 4),
    ("001753.63", "0",        "line 25  DD(BU,1),0  -SINGLE UNIT CHANNEL", 1),
    ("001753.64", "00001040", "line 26  DD(BU,24),(8)1040", 24),
    ("001754.14", "04",       "line 27  DD(BU,4),(8)4  -PUNCH *PU", 4),
    ("001754.20", "0",        "line 28  DD(BU,1),0  -SINGLE UNIT CHANNEL", 1),
    ("001754.21", "00002001", "line 29  DD(BU,24),(8)2001", 24),
    ("001754.51", "05",       "line 30  DD(BU,4),(8)5  -PRINTER * PR", 4),
    ("001754.55", "0",        "line 31  DD(BU,1),0  -SINGLE UNIT CHANNEL", 1),
    ("001754.56", "00000000", "line 32  DD(BU,24),(8)0", 24),
    ("001755.06", "00",       "line 33  DD(BU,4),(8)0  -UNUSED", 4),
    ("001755.12", "0",        "line 34  DD(BU,1),0  -SINGLE UNIT CHANNEL", 1),
    ("001755.13", "00000000", "line 35  DD(BU,24),(8)0", 24),
    ("001755.43", "00",       "line 36  DD(BU,4),(8)0  -UNUSED", 4),
    ("001755.47", "0",        "line 37  DD(BU,1),0  -SINGLE UNIT CHANNEL", 1),
    ("001755.50", "00002004", "line 38  DD(BU,24),(8)2004", 24),
    ("001756.00", "10",       "line 39  DD(BU,4),(8)10  -TAPE MULTI * TP", 4),
    ("001756.04", "1",        "line 40  DD(BU,1),1  -MULTI UNIT CHANNEL", 1),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.35 ")

# ---------------------------------------------------------------
# THE TABLE'S 24-BIT FIELDS ARE CARD COLUMNS, and two documents have
# to agree about them: this listing, and C22-6678-1 Appendix F as
# transcribed into strap/cards.py.  If they disagree, one of the two
# transcriptions is wrong and the equipment lookup on printed p.17
# is reading something this project does not understand.
# ---------------------------------------------------------------
SECOND_LETTERS = [
    ("001752.35", "K", "DK", 1, 0),
    ("001752.72", "N", "CN", 2, 0),
    ("001753.27", "D", "RD", 3, 0),
    ("001753.64", "U", "PU", 4, 0),
    ("001754.21", "R", "PR", 5, 0),
    ("001755.50", "P", "TP", 0o10, 1),
]
for loc, letter, pair, code, multi in SECOND_LETTERS:
    bits = loc_bits(loc)
    got_col = read_bits(prog, bits, 24)
    want_col = column_bits(letter)
    got_code = read_bits(prog, bits + 24, 4)
    got_multi = read_bits(prog, bits + 28, 1)
    ok = (got_col == want_col and got_code == code and got_multi == multi)
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} MCP p.35 {loc} {pair}: column "
          f"{got_col:#014b} (card column of {letter!r} is {want_col:#014b}), "
          f"code {got_code}, multi {got_multi}")

# ---------------------------------------------------------------
# THE THREE CARD-TYPE LITERALS ARE THE PUNCHED CHARACTERS, and this
# check is what caught a misreading of the page.
#
# Line 10's name field reads "X ICD" at 900 dpi and the comment
# "-ICD IN HOLLERITH".  THE DATUM SAYS OTHERWISE: 0o400120104040 is
# the three columns of "IOD", not "ICD" -- and the same row prints
# its own "DD(BU,36)" as "CD(BU,36)", which is
# docs/listing_typography.md 13 with an O instead of a zero.  The
# deck calls the symbol X IOD, which is also what printed p.19 line
# 23's "KF(BU,36),X IOD,12  -COMPARE AGAINST * IOD *" calls it, so
# mcp_image.merge() now checks p.19's stand-in against p.35's
# placement instead of carrying it as an external.
# ---------------------------------------------------------------
LITERALS = [
    ("001747.00", "MCPP", 48, "line 8   X MCPP"),
    ("001747.60", "IOCD", 48, "line 9   X IOCD"),
    ("001750.40", "IOD",  36, "line 10  X IOD"),
]
for loc, text, width, note in LITERALS:
    got = read_bits(prog, loc_bits(loc), width)
    want = int("".join("%03x" % column_bits(c) for c in text), 16)
    ok = got == want
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} MCP p.35 {loc} {note}: datum "
          f"{got:0{-(-width//3)}o} is the card columns of {text!r} "
          f"({want:0{-(-width//3)}o})")

# The entries the page calls unused, and the first entry, must be
# zero in all three fields -- "NO EQUIPMENT" is how a channel with
# nothing on it matches.
for loc in ("001752.00", "001754.56", "001755.13"):
    bits = loc_bits(loc)
    v = read_bits(prog, bits, 29)
    ok = v == 0
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} MCP p.35 {loc} unused entry is "
          f"twenty-nine zero bits: {v}")

finish(fails)
