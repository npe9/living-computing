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
     about the regex.  SEVEN defects in all, found one at a time by
     seven different page transcribers; the reach went 37 -> 101 ->
     109 -> 117 -> 123 decks and 1231 -> 3066 comparisons as each
     was fixed, with zero mismatches at every step.

     THE REMAINING 49 ARE NOT A GAP.  Characterised once rather than
     discovered again: they carry PROSE notes with locations in them
     ("p.104 line 6 is the last SLC seen, SLC,$ printed 215020.71")
     and no tabular block at all.  123/172 is the ceiling, not a
     shortfall, and a future reader should not go looking for an
     eighth layout.

The third is why this is a script and not a snippet: **it reports its
own REACH**, so silence can never be mistaken for verification. A
paste-able recipe cannot be relied on to keep doing that.

MEASURED INJECTION 2, run on printed p.192 line 1, whose listing row
and !CHECK both read "221512.40 80".  Perturbing the LISTING ROW:

    location word  221512 -> 221513   CAUGHT (and was caught before)
    bit offset .40 -> .41             MISSED before, CAUGHT now
    opcode byte 80 -> 91              MISSED before, CAUGHT now

Widening the comparison from want[:8] to the whole field turned up
SEVEN disagreements that had stood green, and a second scan for
non-octal digits in an octal field turned up THREE more.  All ten are
`C` printed where the page prints `0` -- printed pp.37, 95, 139 and
172 -- i.e. the listing block had been pasted from the volume OCR
instead of read.  THAT IS THE WHOLE POINT OF THE BLOCK: it is supposed
to be an INDEPENDENT second witness to the !CHECK, and an OCR paste is
not independent.  The B0/BC pair on p.95 was settled by sweeping the
index register through the oracle -- the index lands in the FIRST half
word's byte (82 for $2) and the second half word's byte is B0 for
every index, so BC cannot be a reading.

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
# The space before the LOCATION's asterisk is also optional -- decks
# write both "221352.00 *" and "221352.00*".  Requiring it dropped
# rows on TWENTY-FOUR decks, +236 rows corpus-wide, and several
# (printed pp.99, 101, 104, 107) went from almost nothing to fully
# read: they were effectively unchecked while the tool reported a
# reach that counted them.  printed p.187's transcriber found it
# after losing 2 of 24 rows on their own page and still seeing
# ALL TESTS PASSED.
ROW_RE = re.compile(
    r'!\s*(?:line\s+)?\d+\*?\s+([0-7]{6}\.[0-7]{2})\s*\*?\s*(.*)')
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
        # >>> COMPARE THE WHOLE FIELD. <<<  This read want[:8] until
        # 2026-11-02, which is the location word, the '.' and the FIRST
        # octal digit of the bit offset -- 8 of the 12 characters in
        # "221512.40 80".  It was blind to the second offset digit and
        # to the entire trailing hex byte, WHICH IS THE OPERATION CODE,
        # and so reported 0 mismatches over 3,313 comparisons while ten
        # rows disagreed.  See MEASURED INJECTION 2 in the docstring.
        if want and not any(r.startswith(want) for r in cands):
            bad.append((m.group(1), want, cands))
    return len(rows), compared, bad


# A binary group prints as "oooooo.oo HH": two OCTAL fields and one HEX
# byte.  An 8, a 9 or a letter in an octal field cannot be a reading of
# the page -- it is OCR, and `C` for `0` is the volume OCR's signature
# substitution.  This catches the corruption on rows that carry no
# !CHECK, which the comparison above cannot reach.
_GROUP_OK = re.compile(r'^[0-7]{6}\.[0-7]{2}$')
_GROUP_SHAPE = re.compile(r'^[0-9A-Z]{6}\.[0-9A-Z]{2}$')


def bad_octal(path):
    """Binary-group octal fields in `path` that are not octal."""
    out = []
    for ln in open(path, errors='replace'):
        m = ROW_RE.match(ln)
        if not m:
            continue
        toks = m.group(2).split()
        i = 0
        while i < len(toks) and _GROUP_SHAPE.match(toks[i]):
            if not _GROUP_OK.match(toks[i]):
                out.append(toks[i])
            i += 2 if (i + 1 < len(toks)
                       and re.fullmatch(r'[0-9A-Z]{2}', toks[i + 1])) else 1
    return out


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

    octal_bad, octal_decks = 0, 0
    for d in decks:
        toks = bad_octal(d)
        if toks:
            octal_decks += 1
        for tok in toks:
            print(f"FAIL {os.path.basename(d)}: {tok!r} is not octal in a "
                  f"binary group -- OCR contamination, not a reading")
            octal_bad += 1
    fails += octal_bad
    print(f"PASS listing_block_octal_clean = {octal_bad} bad groups in "
          f"{octal_decks} of {len(decks)} decks")
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
