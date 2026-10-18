#!/usr/bin/env python3
"""gen_card_reader_tb.py -- punch an ASCII deck and read it back on
the machine.

SIMH-STYLE IN, PUNCHES OUT.  The deck below is text, one line per
card; `cards.py` turns each line into the 960 bits a real IBM 7503
would present to the Exchange, and this loads them into StretchIO's
reader before the program runs.  `programs/card_reader.strap` then
does two ordinary `RD`s against channel 32 and knows nothing about
any of it.

WHAT THE CHECKS ACTUALLY PROVE, which is more than "a word moved":
every expectation is computed by `cards.py` from the deck text, so a
pass means the fifteen words the machine read ARE the fifteen words
that line punches to.  And the first card's first word is spelled out
column by column in the run line, so a failure says which column.
"""
import sys

from cards import card_words, column_bits, describe, WORDS_PER_CARD
from gen_tb import generate
from strap_asm import assemble

PROGRAM = "programs/card_reader.strap"

# A deck.  Two cards, because a reader that returned the same card
# twice would pass a one-card test.
DECK = [
    "MCP BOOTSTRAP CARD DECK",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789 +-*/$,.():='",
]


def pack_control_word(data_addr, count):
    """Figure 35's layout, as mktape.py's does; unitReady 1, no flags."""
    return ((data_addr & 0x3FFFF) << 46) | (1 << 45) | ((count & 0x3FFFF) << 18)


def main():
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} ModuleName", file=sys.stderr)
        sys.exit(1)
    prog = assemble(open(PROGRAM).read())
    sym = lambda n: prog.symtab[n] // 64

    # The two control words the program's RDs will fetch.
    prog.words[sym("CTLW1")] = pack_control_word(sym("CARD1"), WORDS_PER_CARD)
    prog.words[sym("CTLW2")] = pack_control_word(sym("CARD2"), WORDS_PER_CARD)

    reader = []
    for line in DECK:
        reader.extend(card_words(line))

    checks = []
    for n, (line, base) in enumerate(zip(DECK, ("CARD1", "CARD2")), 1):
        w = card_words(line)
        # The FIRST word of each card, which is columns 1 through 5
        # and a bit, is the one worth naming a column for.
        checks.append((f"card{n}_word0_cols_1_to_5", str(sym(base)), w[0]))
        # The LAST word, column 75 onward: a reader that stopped early
        # would pass the first check and fail this one.
        checks.append((f"card{n}_word14_cols_75_to_80",
                       str(sym(base) + WORDS_PER_CARD - 1), w[-1]))
        # And the middle, so a transfer that moved only the ends fails.
        checks.append((f"card{n}_word7_middle",
                       str(sym(base) + 7), w[7]))

    # A card the deck does NOT contain must not appear: card 2's first
    # word read into card 1's area would pass every check above if the
    # two cards were identical, so assert they differ.
    assert card_words(DECK[0])[0] != card_words(DECK[1])[0], \
        "the two cards start with the same word; pick a different deck"

    print(generate(sys.argv[1], prog, checks,
                   reader_image=reader,
                   pc_check=prog.symtab["PASS"] // 32,
                   step_cap=4000))


if __name__ == "__main__":
    main()
