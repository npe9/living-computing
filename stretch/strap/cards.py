#!/usr/bin/env python3
"""cards.py -- punched cards for the IBM 7503 reader, from ASCII.

SIMH-STYLE, which means: a deck is a text file, one line per card, and
this turns each line into the 960 bits a real card presents to the
machine.  80 columns of 12 punch rows.  A short line is blank-padded
to 80; a long one is an error, because silently truncating a card is
how a deck quietly stops being the deck you wrote.

    deck.txt  ->  cards.py  ->  15 words per card  ->  chanReader

---------------------------------------------------------------------
THE PUNCH PATTERNS ARE PRINTED, AND FINDING THAT OUT COST THREE OF
THEM
---------------------------------------------------------------------
>>> C22-6678-1 printed p.56 = PDF p.56, "APPENDIX F. CHARACTER
CODES", tabulates the card code DIRECTLY. <<<  Four columns --
Character, IQS, BCD, Punches -- and the header says "The following
table lists the octal codes, by character, for eight-bit IQS,
six-bit BCD, and the corresponding column binary punches."  That is
the source this table is now transcribed from.

THIS FILE PREVIOUSLY ASSERTED THAT NO SUCH TABLE EXISTED, which was
wrong, and the way it was wrong is the useful part.  It derived the
punches from the 48 Character Set grid on Reference Manual printed
p.166, whose four occupied columns are the four zone punches and
whose sixteen rows are the digit punches, and it justified doing so
on the grounds that the code "was never 7030-specific in the first
place because it belongs to the CARD and the keypunch, not to the
computer."

THE DERIVATION AGREES WITH APPENDIX F ON 46 OF 49 CHARACTERS -- every
letter, every digit, blank, and most of the specials -- AND THE THREE
IT MISSES ARE EXACTLY WHERE THAT JUSTIFICATION FAILS:

    char   Appendix F   the derivation gave
    '      0-3-8        4-8            <- transposed
    ,      4-8          0-3-8          <- transposed
    ;      11-0         not in the set
    :      NO PUNCHES   0-2-8

The quote and the comma have each other's punches, and the 7030 set
spends 11-0 on a semicolon and gives the colon no card code at all.
Those are precisely the slots where the conventional commercial code
and the 7030's 48-character set disagree -- so "it belongs to the
card, not the computer" was true for the letters and digits and false
for the punctuation, which is the only place it mattered.

tests/verify_c22_6678_appendix_f.py runs that whole comparison, so
the derivation is kept as a cross-check rather than as the source.

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
card-code table anywhere in its 86 pages, by design: the
punch-to-character mapping is not the READER's business.

That much stands.  What this file used to conclude from it -- that
therefore no 7030 document could give the mapping, so deriving it was
"the only place a 7030 document could put it" -- does not follow and
is false.  The mapping is not the reader's business; it IS the
software's, and MCP's own reference manual prints it in Appendix F.
A unit manual's silence is evidence about that unit, not about the
corpus.

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

# C22-6678-1 printed p.56, APPENDIX F. CHARACTER CODES, the "Punches"
# column, transcribed at 200 dpi.  A character mapped to None is
# printed in the table WITH AN IQS CODE AND NO PUNCHES: it exists in
# the character set and has no card representation.  There are three
# of them and the colon is one, which is why the card-reader test's
# deck does not contain one.
#
# The IQS and BCD columns are transcribed too, in
# tests/verify_c22_6678_appendix_f.py, which is where the whole table
# is checked; here only the punches are needed.
APPENDIX_F = {
    "A": (12, 1), "B": (12, 2), "C": (12, 3), "D": (12, 4), "E": (12, 5),
    "F": (12, 6), "G": (12, 7), "H": (12, 8), "I": (12, 9),
    "J": (11, 1), "K": (11, 2), "L": (11, 3), "M": (11, 4), "N": (11, 5),
    "O": (11, 6), "P": (11, 7), "Q": (11, 8), "R": (11, 9),
    "S": (0, 2), "T": (0, 3), "U": (0, 4), "V": (0, 5), "W": (0, 6),
    "X": (0, 7), "Y": (0, 8), "Z": (0, 9),
    "0": (0,), "1": (1,), "2": (2,), "3": (3,), "4": (4,),
    "5": (5,), "6": (6,), "7": (7,), "8": (8,), "9": (9,),
    " ": (),                                   # printed "none"
    "+": (12,), "$": (11, 3, 8), "=": (3, 8), "*": (11, 4, 8),
    "(": (0, 4, 8), "/": (0, 1), ")": (12, 4, 8), "'": (0, 3, 8),
    ";": (11, 0), ",": (4, 8), ".": (12, 3, 8), "-": (11,),
    '"': None, ":": None, "?": None,
}


def punches(ch):
    """The punch rows for one character, as a set of row numbers.

    C22-6678-1 printed p.56, Appendix F; see the module docstring.
    """
    up = ch.upper()
    if up not in APPENDIX_F:
        raise ValueError(
            f"{ch!r} is not in Appendix F's character set (C22-6678-1 "
            f"printed p.56); this reader punches no other code")
    rows = APPENDIX_F[up]
    if rows is None:
        raise ValueError(
            f"{ch!r} is in Appendix F's character set but the Punches "
            f"column is BLANK: it has no card representation")
    return set(rows)


def punches_from_grid(ch):
    """The same thing DERIVED from the 48 Character Set grid.

    Reference Manual printed p.166: the grid's four occupied columns
    are the four zone punches and its sixteen rows are the digit
    punches.  Kept because it is an independent path to the same
    answer, and tests/verify_c22_6678_appendix_f.py measures how far
    it gets -- 46 of 49, missing exactly the punctuation where the
    7030's set and the conventional one disagree.  NOT used to punch
    anything.
    """
    up = ch.upper()
    if up not in BCD_48:
        raise ValueError(
            f"{ch!r} is not in the 48 character set (Reference Manual "
            f"printed p.166)")
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


def card_words_cols(line, overrides=None):
    """`card_words`, but with raw 12-bit COLUMN values allowed.

    `overrides` maps a ZERO-BASED column index to the twelve bits of
    that column, most significant bit first in ROW_ORDER -- row 12
    first, exactly as `column_bits` returns them.  Columns not named
    come from `line` through the character table as usual.

    >>> WHY THIS EXISTS: A 7030 CARD IS NOT ALWAYS CHARACTERS. <<<
    Reference Manual printed p.21, already quoted at the top of this
    file: "The data punched in the IBM card used with the 7030 System
    is in a binary form.  Each card punch position is a possible data
    bit, with a punched hole representing the data bit."  The
    character table above is the KEYPUNCH's mapping and belongs to
    cards people type; a field that MCP reads as raw bits has no
    character for it, and `card_words` cannot express one.

    >>> THE MOTIVATION FIRST WRITTEN HERE WAS WRONG, and the
    capability is right anyway. <<<  It said the IOD control card
    needed this because printed p.40 reads "ten SIX-BIT fields, two per
    column, which no single character can produce".  It does not:
    `C22-6728-1` printed p.66 says Uncode converts the card to BCD into
    `Y UCBF1` via SCA6 first, so those ten six-bit fields are ten
    ORDINARY BCD CHARACTERS in card columns 63-72, one per column, and
    a keypunch produces them.  See tests/verify_card_columns.py.

    What remains true is the need: a 7030 card may carry a field that
    has no character -- p.21's "each card punch position is a possible
    data bit" -- and `card_words` cannot express one.  This can.  The
    IOD card simply turned out not to be an example.
    """
    if overrides is None:
        return card_words(line)
    if len(line) > COLUMNS:
        raise ValueError(
            f"card is {len(line)} characters; a card has {COLUMNS} columns "
            f"and this will not truncate one silently: {line!r}")
    text = line.ljust(COLUMNS)
    cols = [column_bits(ch) for ch in text]
    for c, bits in overrides.items():
        if not 0 <= c < COLUMNS:
            raise ValueError(f"column {c} is outside 0..{COLUMNS - 1}")
        if not 0 <= bits < (1 << 12):
            raise ValueError(f"column {c}: {bits} does not fit twelve bits")
        cols[c] = bits
    bits = 0
    for v in cols:
        bits = (bits << 12) | v
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
