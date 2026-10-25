"""THE MERGE MUST REJECT A SYMBOL DECLARED WITH TWO DATA DESCRIPTIONS.

This is the regression test for the 2026-10-25 image bug, and the bug
is worth restating because the shape of it is what the test is for.

printed p.62 line 11 declares "T JBPRO SYN(BU,1),0.36" and three other
decks declared "T JBPRO SYN,0.36" with the dds left off -- correctly,
as far as those pages go, because they only BRANCH on the bit and a
branch never uses a length.  printed p.80 line 24 is
"CM1111,T JBPRO(T IXG)" and writes no dds, so it takes its length FROM
THE SYMBOL (C22-6531 printed p.31).

EVERY DECK STILL VERIFIED BIT-FOR-BIT, because within one deck a
symbol has exactly one declaration.  Only the MERGE saw both, took the
one without the dds, and compiled length 0 -- which effLength reads as
SIXTY-FOUR.  The model then refused the instruction as a
crossing-field write, correctly, and MCP never set its job-processed
bit.  Three rows across printed pp.66, 75 and 80 were wrong in the
image while every page-level test passed.

mcp_image.merge() compared ADDRESSES and nothing else, so nothing
fired: the addresses agreed exactly.  It now also requires every
declaration of a symbol to carry the same data description, and on its
first run that guard found SIXTEEN conflicting symbols -- two of them
(T INDE, T MODE) with CONTRADICTORY lengths rather than a missing one.

MEASURED INJECTION: this test takes a deck that declares a symbol with
a dds, strips the dds, and requires the merge to fail.  Without the
guard the merge succeeds and the image is silently wrong, which is
precisely the state the corpus was in.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'strap'))
import mcp_image

DECK = os.path.join(os.path.dirname(__file__), '..', 'decks',
                    'mcp_bootstrap_p80.strap')
GOOD = "TJBPRO  SYN(BU,1), 0.36"
BAD = "TJBPRO  SYN, 0.36"

fails = 0


def check(name, ok, detail=""):
    global fails
    print(("PASS " if ok else "FAIL ") + name + (("  " + detail) if detail else ""))
    if not ok:
        fails += 1


# 1. The corpus as it stands must merge.
try:
    mcp_image.build(False, mcp_image.MCP_IPL_PAGES, end_at='X10')
    check("the corpus merges with every dds agreeing", True)
except SystemExit as e:
    check("the corpus merges with every dds agreeing", False, str(e))

# 2. Strip one dds and the merge must refuse.  try/finally, because a
#    deck left mutated would poison every later test in the suite.
original = open(DECK).read()
if GOOD not in original:
    check("the injection anchor is present in printed p.80", False,
          "expected %r" % GOOD)
else:
    try:
        open(DECK, "w").write(original.replace(GOOD, BAD, 1))
        try:
            mcp_image.build(False, mcp_image.MCP_IPL_PAGES, end_at='X10')
            check("a stripped dds is REFUSED by the merge", False,
                  "the merge accepted it -- the guard is not working")
        except SystemExit as e:
            msg = str(e)
            check("a stripped dds is REFUSED by the merge",
                  "TJBPRO" in msg and "data description" in msg, msg[:90])
    finally:
        open(DECK, "w").write(original)

# 3. And the deck is back exactly as it was.
check("printed p.80's deck is restored byte-for-byte",
      open(DECK).read() == original)

print("ALL TESTS PASSED" if fails == 0 else "%d TEST(S) FAILED" % fails)
raise SystemExit(1 if fails else 0)
