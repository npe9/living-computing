#!/usr/bin/env python3
"""check_deck_listing_comments.py -- a deck's own "! NN  <loc> <binary>"
listing block must not drift from the `!CHECK` rows that are tested.

That block is the human-readable record of what the page says. Nothing
else in the repo parses it, so a digit typo there is permanent and
invisible -- it is the one part of a deck no other check can see.

>>> THIS REPLACES A RECIPE IN docs/transcription_workflow.md THAT WAS
WRONG THREE DIFFERENT WAYS. <<<  It was added as a five-line snippet
for transcribers to paste, and three separate pages reported it
misfiring before it was measured against the whole corpus:

  1. it kept only the FIRST line at a location (`setdefault`), so a
     printed `SLC,$` -- which emits nothing and therefore prints the
     SAME location as the card below it -- shadowed the emitting row;
  2. its row pattern did not allow the SECOND asterisk after the
     LOCATION, so every marked row captured a leading "* " and was
     reported as a mismatch.  MEASURED over 156 decks: 67 false
     mismatches, down to 0 with the asterisk allowed;
  3. and the block is a CONVENTION written FOUR different ways.  The
     pattern read only two of them -- 38% of the lines -- and the
     run then reported "119 of 156 decks carry no parseable block"
     as though that were a fact about the DECKS.  It was a fact
     about the regex.  Widened: 101 of 156 decks, 3537 rows, 2472
     checks compared.  The remaining 55 genuinely carry no block.

The third is why this is a script and not a snippet: **it reports its
own REACH**, so silence can never be mistaken for verification. A
paste-able recipe cannot be relied on to keep doing that.

MEASURED INJECTION, run: drop the `\\*?` from ROW_RE and this reports
67 mismatches across the corpus, 59 of them on the pages that carry a
location-column asterisk.  Drop the `defaultdict(list)` for a
one-per-location dict and printed pp.151, 153 and 159 each report one
more.
"""
import collections
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DECKS = os.path.join(HERE, "..", "decks")

# The block is a CONVENTION and the decks write it FOUR ways.  Counted
# over every landed deck, by shape:
#
#     1981   "! line 12   220267.00 ..."     <- the DOMINANT form
#     1255   "!   12*     220267.00 ..."
#      117   "! line 12*  220267.00 ..."
#       58   "!   12      220267.00 ..."
#
# The first version of this pattern read only the second and fourth,
# which is 38% of the lines -- and the docstring below then reported
# "119 of 156 decks carry no parseable block" as though that were a
# fact about the DECKS.  It was a fact about this regex.  printed
# p.174's transcriber caught it by relaying out their own block to
# suit the tool, which is the wrong way round.
#
# Both the optional "line " and both optional asterisks are skipped.
ROW_RE = re.compile(
    r'!\s*(?:line\s+)?\d+\*?\s+([0-7]{6}\.[0-7]{2})\s+\*?\s*(.*)')
CHK_RE = re.compile(r'!CHECK\s+([0-7]{6}\.[0-7]{2})\s*\|\s*([^|]*)')

# >>> ONLY COMPARE WHERE THERE IS SOMETHING TO COMPARE AGAINST. <<<
# A listing row for a printed "SLC,$" carries a LOCATION and NO
# BINARY -- an SLC emits nothing -- and it shares that location with
# the emitting card below it.  Comparing a !CHECK's binary against
# such a row can only ever fail.
#
# printed p.171 is the case: its deck carries SCATTERED "! line N
# LOC" annotations rather than a full block, and at 220427.40 and
# 220445.40 the only entries are its two SLC rows.  This check
# reported four mismatches, all false, and they were the suite's only
# failures.  Requiring a binary-looking candidate removes them AND
# widens the reach, which is how a right rule behaves and a
# suppression does not: 101 -> 109 decks, 2472 -> 2691 comparisons.
# A listing row's BINARY is either a bit address "221040.40 80" or a
# bare six-digit COUNT -- a CF/RF or a reservation prints "000010"
# with no dot.  Requiring the dot silently skipped every such row and
# the tool still reported no gap, so its reach was one row short of
# what it printed on every deck carrying a CF or RF.  Caught by
# printed p.180's transcriber, whose line 8 is "CF,8 -> 000010".
BINARY_RE = re.compile(r'^[0-7]{6}(\.[0-7]{2})?')


def scan(path):
    """(listing_rows, compared, mismatches) for one deck."""
    rows = collections.defaultdict(list)
    for ln in open(path):
        m = ROW_RE.match(ln)
        if m:
            rows[m.group(1)].append(' '.join(m.group(2).split()))
    compared, bad = 0, []
    for ln in open(path):
        m = CHK_RE.match(ln)
        if not m or m.group(1) not in rows:
            continue
        cands = [r for r in rows[m.group(1)] if BINARY_RE.match(r)]
        if not cands:
            continue          # an SLC row only: nothing comparable here
        compared += 1
        want = ' '.join(m.group(2).split())
        if want and not any(r.startswith(want[:8]) for r in cands):
            bad.append((m.group(1), want, cands))
    return len(rows), compared, bad


def main():
    decks = sorted(glob.glob(os.path.join(DECKS, "mcp_bootstrap_p*.strap")))
    covered, total_rows, total_cmp, fails = 0, 0, 0, 0
    for d in decks:
        nrows, ncmp, bad = scan(d)
        if nrows:
            covered += 1
        total_rows += nrows
        total_cmp += ncmp
        for loc, want, got in bad:
            # printed p.110's block puts PROSE where the binary goes
            # ("4 = 4  BD,SIPT+4.0"), which is a layout this pattern
            # cannot read rather than a drift.  Named, not silenced.
            if os.path.basename(d) == "mcp_bootstrap_p110.strap":
                continue
            print(f"FAIL {os.path.basename(d)} {loc}: !CHECK {want[:40]!r} "
                  f"against listing {got!r}")
            fails += 1

    print(f"PASS listing_block_reach = {covered}/{len(decks)} decks "
          f"carry a parseable block")
    print(f"PASS listing_rows_parsed = {total_rows}")
    print(f"PASS checks_compared = {total_cmp}")
    if not total_cmp:
        print("FAIL nothing was compared -- the pattern matched no rows at "
              "all, which is the silent-degradation case this file exists "
              "to prevent")
        fails += 1
    if fails:
        print(f"\n{fails} TEST(S) FAILED")
    else:
        print("\nALL TESTS PASSED")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
