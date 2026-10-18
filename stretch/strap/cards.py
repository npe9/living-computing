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
THE LAYOUT IS SOURCED: R23-9702, the 7503/7614 CE manual
---------------------------------------------------------------------
Both of the things this file had to assume are now read off
`docs/R23-9702_7503_Card_Rdr_7614_Rdr_Ctl_CE_1961.pdf`, the Customer
Engineering manual for this exact pair of units, **Figure 4.3-1,
"Data Bit Relation -- Card to Data Word", printed p.21**, all 72
filled cells read at 600 dpi.  Both assumptions held.

1. BIT ORDER WITHIN A COLUMN: 12, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 --
   straight down the card, the 12 row FIRST and genuinely the most
   significant, because the figure's DATA WORD band runs word bit 0
   to 63 left to right.  No zone/digit split, no reordering.

2. COLUMN ORDER: column 1 first, columns ascending.  A COLUMN
   STRADDLES A BYTE BOUNDARY, at one and a half bytes each: column 1
   is byte 1 plus the top half of byte 2, column 2 is the bottom half
   of byte 2 plus byte 3, so two columns are three bytes and six
   columns are nine.  Packing the twelve-bit columns end to end, as
   below, produces exactly that.  The figure fills only columns 1-6,
   but printed p.37 and p.64 independently pin byte 118 as the first
   byte of card column 79, which makes the mapping uniform across all
   eighty.

THE INTERFACE MOVES EIGHT-BIT BYTES, NOT TWELVE-BIT ONES, and that is
worth keeping straight.  Printed p.19: "A block of data (the data in
one punched card) is transferred to the exchange in 120 eight-bit
bytes with an associated parity bit for each data byte", over eight
parallel lines plus a ninth for parity.  The twelve-bit column is
STRAP's unit -- C28-6129's `(CC*)` entry mode -- not the channel's.
120 x 8 = 960 = 15 x 64 either way.

>>> AND "15 WORDS" IS NON-ECC MODE ONLY <<<  Printed p.64: in ECC
mode "six consecutive card columns define one data word ... The ECC
card contains a maximum of 13 data words in card columns 1 to 78.
Columns 79 and 80 are not used."  Thirteen words, not fifteen, and
two columns thrown away.  This file punches the non-ECC layout; an
ECC deck is a different shape and is not implemented.

---------------------------------------------------------------------
AND THE MANUAL SAYS WHY THERE IS NO CARD CODE IN IT
---------------------------------------------------------------------
Printed p.21: "The data punched in the IBM card used with the 7030
System is in a binary form.  Each card punch position is a possible
data bit, with a punched hole representing the data bit."

**The 7503/7614 does no character translation at all.**  There is no
card-code table anywhere in its 86 pages, by design, and that is the
answer to why C28-6129 names `(CC*)` and tabulates nothing: the
punch-to-character mapping is a property of the KEYPUNCH and the
convention, never of the 7030.  So deriving it from the 48 Character
Set grid above is not a workaround -- it is the only place a 7030
document could put it.

A REAL 7503 READS ROW BY ROW AND TRANSMITS COLUMN BY COLUMN.  Printed
p.21, verbatim: "Although the card is read in rows (starting from the
9 row through the 12 row), the data are transmitted in column to the
exchange."  The transposition is not logic -- printed p.36: "the
buffer is an 80 x 12 matrix", loaded eighty bits per row pulse and
read out through a twelve-way column ring crossed with a ten-way zone
ring, with the row drivers deliberately scrambled across the core
planes ("The apparent indiscriminate assignment of the row drivers to
the core planes results from an expedient core array wiring format").
That changes nothing about what the Exchange sees, which is what this
file produces; it is most of what an FPGA model of the 7614 has to
contain.
"""
import sys

from charsets import A as BCD_48

# R23-9702 printed p.21, Figure 4.3-1; see the docstring.
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
