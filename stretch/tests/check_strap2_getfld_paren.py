#!/usr/bin/env python3
"""check_strap2_getfld_paren.py -- GETFLD classifies a parenthesis at its ')'.

Source, read in the ink 2026-11-13: C22-6729 Chart BK p.82 and its text p.85.
At a closing parenthesis, Box 64 asks "ONE ABSOLUTE DATUM ONLY"; if so, Box 65
"POSSIBLE GP" and Box 66 ".L OPERATOR" take a g.p.; else Box 79 "SUBSCRIPT
ALLOWED" (Gfsfsb, set only after a programmer symbol, p.84 Boxes 25-27), Box 80
"NUMBER OF OPERATORS EQUAL 0", Box 81 "TEST RADIX IND", Box 74 "SAVE VALUE OF
RADIX FROM CODED EXPRESSION" (p.85: "The value of the radix is stored in
Gfsrad").  No box reads a character past the ')'.  Box 7 (symbol or $) is
tested before Box 8 (number), p.80.

Before this the host decided a radix by looking past the ')' for a digit
(_radix_prefix), and a g.p. or an index-only field by reading ahead on the card
(_peek_gp, _closes_field), which a 7030 GETCHA, one character in $3 and no
pushback, cannot do, and which never saw a continuation card.

The change keeps every deck's coded expressions: all 70,126 fields GETFLD
encodes in the 734 decks, encode() of each before and after, are identical
(2026-11-13).  So the checks below are the inputs where the two rules differ;
no deck writes them.

CHOSEN, the guide does not draw it: Box 76 "ARITHMETIC PARENTHESES LEGAL" is an
operator inside the parenthesis (Boxes 43-49, p.85: "If there was no operator
to make the parentheses arithmetic ...") at the start of a datum; after a point
it is S/X, as Fig. 29 p.201 prints.  And a radix with no datum after it,
L,(3), is refused (66), where the old host made 3 an index.

MEASURED INJECTIONS, 2026-11-13, getfld.py restored by copy and cmp,
PYTHONDONTWRITEBYTECODE=1, control all passing before and after:
  the old getfld.py (looks ahead)        (8)A, (16)A0, (A+1), (3), the split (8
  a radix only if a digit follows        (8)A, (16)A0, (3)
  A-F begin a number in radix 16         (16)A0
  no parenthesis is arithmetic           (A+1)
  a lone datum is arithmetic             the ($1) control, (A)
  a system symbol is an absolute datum   the ($1) control
(The split g.p. passes under the old host too: _peek_gp needed only the '.'.)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
import strap2                   # noqa: E402
from strap2.listing import listing_of            # noqa: E402

fails = 0


def check(label, got, want):
    global fails
    ok = got == want
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} {label}: got {got!r}" + ("" if ok else f", want {want!r}"))


HEAD = ["         SLC,(8)100.0", " A       SYN,5", " A0      SYN,7"]


def printed(*cards):
    """The last statement's address field and index, as the listing prints."""
    try:
        r = strap2.compile_cards(HEAD + list(cards) + ["         END"])
    except Exception as x:          # noqa: BLE001  StrapError, AssemblerError
        return "refused: " + str(x).split(":")[0].replace("message ", "")
    lines = listing_of(r, r.p1.print_names).text("0", 1).splitlines()
    want = cards[0].split()[0]
    line = next(ln for ln in lines if want in ln)
    return " ".join(line.split()[2:4])


def stmt(s):
    return "         " + s


def cont(s):
    return "*        " + s


check("control: L,(8)17, a radix before its number", printed(stmt("L,(8)17")), "000000.17 80")
check("control: L,(16)10", printed(stmt("L,(16)10")), "000000.20 80")
check("control: MCP p.126's KV,2,($1) form, a system symbol alone is S/X",
      printed(stmt("L,($1)")), "000000.00 81")
check("L,(8)A: the radix is taken at ')', whatever follows", printed(stmt("L,(8)A")), "000000.05 80")
check("L,(16)A0: Box 7 before Box 8, A0 is a symbol", printed(stmt("L,(16)A0")), "000000.07 80")
check("L,(A): no operator, not arithmetic (Box 82), S/X", printed(stmt("L,(A)")), "000000.00 85")
check("L,(A+1): an operator, arithmetic (CHOSEN, Box 76)", printed(stmt("L,(A+1)")), "000000.06 80")
check("L,(3): a radix with no datum after it, refused (CHOSEN)", printed(stmt("L,(3)")), "refused: 66")
check("a radix split across a continuation card, (8 / )17",
      printed(stmt("L,(8").ljust(72), cont(")17")), "000000.17 80")
check("a g.p. split across a continuation card, .55(.6 / 3)21",
      printed(stmt("XW,.55(.6").ljust(72), cont("3)21")), printed(stmt("XW,.55(.63)21")))

print("ALL CHECKS PASSED" if not fails else f"{fails} FAILED")
sys.exit(1 if fails else 0)
