#!/usr/bin/env python3
"""cards.py -- punched cards for the IBM 7503 reader, from ASCII.

SIMH-STYLE, which means: a deck is a text file, one line per card, and
this turns each line into the 960 bits a real card presents to the
machine.  80 columns of 12 punch rows.  A short line is blank-padded
to 80; a long one is an error, because silently truncating a card is
how a deck quietly stops being the deck you wrote.

    deck.txt  ->  mkcards.py  ->  15 words per card  ->  chanReader

---------------------------------------------------------------------
THE PUNCH PATTERNS ARE DERIVED, NOT COPIED, AND THE DERIVATION CHECKS
---------------------------------------------------------------------
C28-6129 printed p.16 names STRAP's `(CC*)` entry mode -- "converted
to 12-bit bytes, where each byte reflects the multiple punch actually
read" -- and tabulates the card code NOWHERE.  The Reference Manual's
four character grids on printed p.166 are all 8-bit.  So there is no
7030 document in this corpus that gives a punch combination directly.

There does not need to be.  THE 48 CHARACTER SET GRID *IS* THE CARD'S
OWN STRUCTURE.  Its four occupied columns are the four zone punches
and its sixteen rows are the digit punches:

    grid column 0000  ->  no zone punch
    grid column 0001  ->  the 0 punch
    grid column 0010  ->  the 11 punch
    grid column 0011  ->  the 12 punch

    grid row 0001-1001  ->  that digit row, 1 through 9
    grid row 0000       ->  no digit punch (so the zone stands alone:
                            12 is "+", 11 is "-", none is blank)
    grid row 1010       ->  the 0 row when there is no zone, else 8-2
                            (the 0 row is taken by the zone punch)
    grid row 1011       ->  8-3
    grid row 1100       ->  8-4

That rule, applied to the grid this project read at 150 dpi off
printed p.166, reproduces the standard IBM card code at every one of
twenty-two spot checks -- A = 12-1, J = 11-1, S = 0-2, 0 = the 0 row
alone, "." = 12-8-3, "$" = 11-8-3, "," = 0-8-3, "=" = 8-3, "'" = 8-4,
"(" = 0-8-4, ")" = 12-8-4, "*" = 11-8-4, ":" = 0-8-2, "/" = 0-1.  Two
independent things agreeing, which is this project's standard: a
derivation from a page it read, and a code that was never 7030-
specific in the first place because it belongs to the CARD and the
keypunch, not to the computer.

---------------------------------------------------------------------
>>> TWO THINGS HERE ARE ASSUMPTIONS, AND BOTH ARE CHECKABLE <<<
---------------------------------------------------------------------
1. THE BIT ORDER WITHIN A COLUMN.  This packs the twelve rows in
   reading order down the card -- 12, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8,
   9 -- with the 12 row as the most significant bit of the 12-bit
   byte.  That is the natural choice and the one IBM's own numbering
   suggests, and it is NOT sourced.

2. THE COLUMN ORDER WITHIN THE 960 BITS.  This packs column 1 into
   the first twelve bits of the first word, column 2 into the next
   twelve, and so on to column 80 in the last twelve bits of the
   fifteenth word, with no padding (80 x 12 = 960 = 15 x 64 exactly).
   Also not sourced.

Both are answered by `docs/R23-9702_7503_Card_Rdr_7614_Rdr_Ctl_CE_1961
.pdf`, the Customer Engineering manual for this exact pair of units,
which is in this repository and whose Figure 4.5-1 ("Communication
Lines", printed p.28) `docs/exchange_and_io.md` 3.13 already cites for
the channel interface.  CHANGE THE TWO CONSTANTS BELOW WHEN IT IS
READ; everything else in this file is independent of them.

Note also that a real 7503 reads a card ROW BY ROW, not column by
column -- eighty punches at a time, twelve times -- so somewhere in
the 7614 there is a transposition.  Where that happens does not change
what the Exchange sees, which is what this file produces, but it does
change what an FPGA model of the 7614 has to do.
"""
import sys

from charsets import A as BCD_48

# See "TWO THINGS HERE ARE ASSUMPTIONS" above.
ROW_ORDER = (12, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
COLUMNS = 80
WORDS_PER_CARD = COLUMNS * 12 // 64        # 15, exactly, no padding

_ZONE = {0: (), 1: (0,), 2: (11,), 3: (12,)}


def punches(ch):
    """The punch rows for one character, as a set of row numbers.

    Derived from the 48 Character Set grid; see the module docstring.
    """
    up = ch.upper()
    if up not in BCD_48:
        raise ValueError(
            f"{ch!r} is not in the 48 character set (Reference Manual "
            f"printed p.166); this reader punches no other code")
    code = BCD_48[up]
    zone = _ZONE[code >> 4]
    row = code & 0xF
    if row == 0:
        digits = ()
    elif row <= 9:
        digits = (row,)
    elif row == 10:
        # The 0 ROW when the column has no zone punch; 8-2 when it
        # does, because the zone has taken the 0 row.
        digits = (0,) if not zone else (8, 2)
    elif row == 11:
        digits = (8, 3)
    elif row == 12:
        digits = (8, 4)
    else:
        raise AssertionError(row)
    return set(zone) | set(digits)


def column_bits(ch):
    """One column as a 12-bit integer, the 12 row most significant."""
    rows = punches(ch)
    v = 0
    for r in ROW_ORDER:
        v = (v << 1) | (1 if r in rows else 0)
    return v


def card_words(line):
    """One card -- a text line -- as WORDS_PER_CARD 64-bit words."""
    if len(line) > COLUMNS:
        raise ValueError(
            f"card is {len(line)} characters; a card has {COLUMNS} columns "
            f"and this will not truncate one silently: {line!r}")
    text = line.ljust(COLUMNS)
    bits = 0
    for ch in text:
        bits = (bits << 12) | column_bits(ch)
    return [(bits >> (64 * (WORDS_PER_CARD - 1 - i))) & 0xFFFFFFFFFFFFFFFF
            for i in range(WORDS_PER_CARD)]


def deck_words(lines):
    """A whole deck, card after card, as one flat list of words."""
    out = []
    for n, line in enumerate(lines, 1):
        try:
            out.extend(card_words(line.rstrip("\n")))
        except ValueError as e:
            raise ValueError(f"card {n}: {e}") from None
    return out


def read_deck(path):
    with open(path) as f:
        return deck_words(f.read().splitlines())


def describe(line):
    """One card as a human-readable punch list, for eyeballing."""
    out = []
    for i, ch in enumerate(line.ljust(COLUMNS)[:COLUMNS], 1):
        p = sorted(punches(ch), key=lambda r: ROW_ORDER.index(r))
        if p:
            out.append(f"col {i:2d} {ch!r} punches " + "-".join(map(str, p)))
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} DECK.txt [--punches]", file=sys.stderr)
        sys.exit(1)
    lines = open(sys.argv[1]).read().splitlines()
    if "--punches" in sys.argv:
        for n, line in enumerate(lines, 1):
            print(f"--- card {n}: {line!r}")
            for d in describe(line):
                print("   ", d)
        sys.exit(0)
    words = deck_words(lines)
    print(f"{len(lines)} cards = {len(words)} words "
          f"({WORDS_PER_CARD} per card)")
    for i, w in enumerate(words):
        if i % WORDS_PER_CARD == 0:
            print(f"  card {i // WORDS_PER_CARD + 1}")
        print(f"    {w:016x}")
