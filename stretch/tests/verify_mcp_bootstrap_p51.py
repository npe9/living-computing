#!/usr/bin/env python3
"""verify_mcp_bootstrap_p51.py -- TYPE SYMBOLS AND CODES, and the IOD
AND REEL COMPARISONS, printed page 51
(../decks/mcp_bootstrap_p51.strap).
docs/MCP_Mar63_001-249.pdf PDF p.58, header "PAGE NUMBER 51".
AGENTS.md rule 3.

Nine printed rows with binary output and seven symbol locations.

>>> L DISK LANDS AT 002723.00 AND THAT IS printed p.48's LAST
STAND-IN. <<<

p.48 line 18 is "L XTYPE  XW,L DISK,9,$" -- a refilling index word
over NINE entries -- and this page has exactly nine type symbols,
DISK through TAPE.  The count and the table are three pages apart and
they agree.

EVERY TYPE DATUM IS TEN CHARACTERS AND THE ADDRESSES PROVE IT: each
entry's four-bit code sits at .74, bit 60, and the next entry at the
next word.

>>> AND THE TRAILING BLANK COUNTS WERE MEASURED, NOT EYEBALLED. <<<

The statement column was rendered at 600 dpi and the ink runs read
off numerically, the way listing_typography.md settles a glyph.  One
character pitch is about 61 px in that crop, and every "Y" terminator
in the nine type rows sits at x = 1818-1868 -- the same card column,
so every datum is ten characters.  The same measurement settles the
three rows no address can:

    L IOD   (line 30)  Y at 1818  -- ten characters, "IOD" + 7 blanks
    L REEL  (line 32)  Y at 1819  -- ten characters, "REEL" + 6
    L BLANK (line 34)  Y at 1701  -- TWO pitches earlier, so EIGHT
                                     characters, 48 bits

L BLANK's eight has a second witness: its own dds is "(BU,48,6)" and
8 x 6 is 48, where L IOD's and L REEL's declared 64 is NOT 10 x 6.
Neither witness is conclusive alone -- strap_asm's own note says a
converted DD's size is characters times byte size and the declared
length "plays no part" -- but they agree.

L IOD's AND L REEL's LENGTHS ARE PINNED BY NOTHING ELSE, and that is
the printed p.44 shape again: lines 31 and 33 are CNOPs that round
sixty bits up to sixty-four, so a datum of nine or ten characters
leaves the next row exactly where it is.  printed p.52's first
compiled word is 002737.00, which bounds L BLANK only to 33-64 bits.
THE CODE THAT COMPARES AGAINST THEM will settle it and is not
transcribed yet.

TWO INJECTIONS, OBSERVED FAILURE SETS WRITTEN DOWN:

  One blank dropped from line 8's "DISK" datum -- 12 FAILs: every
  type symbol from L TRACK on moves six bits and every code row with
  it, the first of them reading 03 where the listing prints 01.  The
  table is a chain of fixed-width entries and this is what holds it.
  Line 25's "(8)10" -> "(8)11" -- 1 FAIL, the last code row, and no
  symbol moves.  That row is the witness for the radix substitution:
  the listing prints 10 in a column that is octal throughout, and
  eight is what the ninth type code has to be.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p51.strap").read())

SYMBOLS = {
    "LNOSAV": "002720.00",
    # >>> printed p.48's LAST STAND-IN, and the base of the nine.
    "LDISK":  "002723.00",
    "LTRACK": "002724.00",
    "LTAPE":  "002733.00",
    "LIOD":   "002734.00",
    "LREEL":  "002735.00",
    "LBLANK": "002736.00",
}

# The nine four-bit type codes, each at bit 60 of its own word.  Four
# bits print as two octal digits here, so the width is given.
ROWS = [
    ("002723.74", "01", "line 9   DISK     (8)DD(BU,4),1", 4),
    ("002724.74", "01", "line 11  TRACK    (8)DD(BU,4),1", 4),
    ("002725.74", "02", "line 13  CONSOLE  (8)DD(BU,4),2", 4),
    ("002726.74", "03", "line 15  READER   (8)DD(BU,4),3", 4),
    ("002727.74", "04", "line 17  PUNCH    (8)DD(BU,4),4", 4),
    ("002730.74", "05", "line 19  PRINTER  (8)DD(BU,4),5", 4),
    ("002731.74", "06", "line 21  IQS      (8)DD(BU,4),6", 4),
    ("002732.74", "07", "line 23  (blank)  (8)DD(BU,4),7", 4),
    # >>> THE WITNESS FOR THE RADIX SUBSTITUTION: "10" is EIGHT.
    ("002733.74", "10", "line 25  TAPE     (8)DD(BU,4),10", 4),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.51 ")
finish(fails)
