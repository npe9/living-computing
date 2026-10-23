#!/usr/bin/env python3
"""verify_mcp_bootstrap_p49.py -- RESERVATIONS, TABLES AND COUNTERS
continued, printed page 49 (../decks/mcp_bootstrap_p49.strap).
docs/MCP_Mar63_001-249.pdf PDF p.56, header "PAGE NUMBER 49".
AGENTS.md rule 3.

Six printed rows with binary output and seven symbol locations.
EIGHT LINES, the shortest page this project has transcribed.

>>> IT STARTS AT 002602.00 AND THAT IS A ROUNDING, NOT A NEW ORIGIN.
<<<

printed p.48's last datum is line 52's one-bit "L INFAD DD(BU,1),0"
at 002601.73, ending at 002601.74, and an XW rounds to the next full
word.  There is no SLC on this page at all -- the location counter
carries over, which is what a single STRAP assembly looks like when
the listing's page break falls mid-deck.

LINE 5 IS A SELF-REFILLING CLEAR WORD and it states a number the next
row states again: "L CLEAR XW,L RLCT,4,$" prints count four, and line
6's "L RLCT DRZ(BU,64),(4)" reserves four words.  LAST PP landing at
002613.00 is what checks the second four against the first.

THREE SPELLINGS OF A NULL VALUE FIELD ON ONE PAGE: lines 1 and 4 are
a bare "XW", lines 2 and 3 "XW,0", line 8 "XW," -- and all five
compile the same all-zero index word.  C22-6531 printed p.7: "A null
field is always compiled as a zero."  That the listing uses all three
spellings within eight lines is the best evidence this project has
that they are interchangeable, and all five rows are checked.

TWO INJECTIONS, OBSERVED FAILURE SETS WRITTEN DOWN:

  Line 5's count 4 -> 5 -- 1 FAIL, line 5's row, and NO symbol moves:
  an index word's count is not a reservation.
  Line 6's "(4)" -> "(5)" -- 1 FAIL, LAST PP's symbol check, and
  NOT line 8's row: the fifth reserved word is zero and an all-zero
  index word is what that row expects, so the row reads correctly at
  an address the symbol no longer occupies.  PREDICTED 2 AND
  OBSERVED 1, which is worth the sentence -- a row check pinned to
  an ADDRESS cannot see a symbol move into or out of it when the
  storage either side is identical.  The symbol check is what
  catches it, and that is why both are here.

The two injections are each other's mirror, which is the point: the
page states "four" twice and only one of the two is a size.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p49.strap").read())

SYMBOLS = {
    "LSAVE":  "002602.00",
    "LSAVEY": "002603.00",
    "LSAVEZ": "002604.00",
    "LPUT":   "002605.00",
    "LCLEAR": "002606.00",
    "LRLCT":  "002607.00",
    # Four words later, which is what checks line 6's reservation.
    "LASTPP": "002613.00",
}

ROWS = [
    # THREE SPELLINGS, ONE WORD.  Bare XW, "XW,0" and "XW," all
    # compile all-zero.
    ("002602.00", "000000.00+ 000 000000 000000", "line 1   L SAVE  XW  -TO SAVE LXNT INDEX"),
    ("002603.00", "000000.00+ 000 000000 000000", "line 2   L SAVEY  XW,0"),
    ("002604.00", "000000.00+ 000 000000 000000", "line 3   L SAVEZ  XW,0"),
    ("002605.00", "000000.00+ 000 000000 000000", "line 4   L PUT  XW"),
    # The self-refilling clear word: value L RLCT, count 4, refill
    # itself.
    ("002606.00", "002607.00+ 000 000004 002606", "line 5   L CLEAR  XW,L RLCT,4,$  -XW"),
    ("002613.00", "000000.00+ 000 000000 000000",
     "line 8   LAST PP  XW,  -ADD. OF LAST PP ENTERED IN TBL"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.49 ")
finish(fails)
