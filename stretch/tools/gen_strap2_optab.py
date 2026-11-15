#!/usr/bin/env python3
"""Write the 7030 STRAP II's operation tables into decks/strap2_7030.strap.

    python3 tools/gen_strap2_optab.py

The block (strap/strap2/optab7030.py) goes just before the deck's input
block, the comment that opens with ANCHOR: INB must stay the deck's last
symbol, since the 7030 tests put their cards straight after it
(check_strap2_7030.py, check_strap2_7030_getfld.py).  An old block is
removed first, wherever it is.  Its membership
is tests/printed_ops.optab_names().  tests/check_strap2_7030_optab.py fails
"block_fresh" until this has been run after a change to the host's table.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STRETCH = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(STRETCH, "strap"))
sys.path.insert(0, os.path.join(STRETCH, "tests"))
from strap2 import optab7030 as O     # noqa: E402
import printed_ops                    # noqa: E402

DECK = os.path.join(STRETCH, "decks", "strap2_7030.strap")
ANCHOR = "!\n! The input block: "


def main():
    src = open(DECK).read()
    block = O.Tables(printed_ops.optab_names()).layout().deck_text()
    i, j = src.find(O.BEGIN), src.find(O.END)
    if i >= 0 and j > i:
        src = src[:i] + src[j + len(O.END) + 1:]
    assert src.count(ANCHOR) == 1, "the deck's input block comment is missing"
    k = src.index(ANCHOR)
    src = src[:k] + block + src[k:]
    with open(DECK, "w") as fh:
        fh.write(src)
    print(f"wrote {block.count(chr(10))} lines to {os.path.relpath(DECK)}")


if __name__ == "__main__":
    main()
