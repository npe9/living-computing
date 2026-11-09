"""a8.py -- A8, STRAP II's internal character code.

C22-6729 uses A8 throughout and has no table of it.  It prints nine values
(J K M O P T C E in Figs. 28-29 p.200-201, $ in Fig. 14 p.76).  All nine are
the 48 Character Set of the Reference Manual, printed p.166, as read in
charsets.py.  DERIVED: A8 is that set in eight bits.  "A6" is the same code
without the two high bits, and p.191's vle IDs are A6 graphics.

CHOSEN: ';' is not in the 48 set and cannot be on a 1963 card by that table,
but p.20 tests for it, so it needs a code.  0o035 is unoccupied.  It is
internal: it never reaches a symbol or the object code.
"""
from charsets import A as _A48

A8 = dict(_A48)
A8[";"] = 0o035


def a8(ch):
    """The A8 code of one character; lower case folds, as a card has none."""
    return A8.get(ch.upper(), 0)


def a8_bits(text):
    return "".join(format(a8(c), "08b") for c in text)


A6 = {c: v & 0o77 for c, v in A8.items()}
