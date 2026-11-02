#!/usr/bin/env python3
"""check_mcp_body_image.py -- MCP's BODY, printed pp.99-192, merged
into one image and made to account for every word it spans.

>>> THE BODY IS NOT A LONGER BOOTSTRAP.  IT IS A SECOND ASSEMBLY. <<<
printed p.98 closes the tail block with "UNTAIL,(2)" and printed p.99
line 11 moves the origin with "SLC,(8)215000.", so a name may denote
one thing in pp.15-98 and another here.  The first attempt simply
extended MCP_IPL_PAGES and the merge refused at once -- "SMCP is
defined twice: printed p.37 and printed p.103, and they disagree:
bit 72192 against bit 4620288" -- which is the split stating itself.

WHAT THIS CHECKS THAT NO PER-PAGE TEST CAN.  verify_mcp_page compares
one deck against one printed listing.  Merging puts every external
SYN next to the card that DEFINES it, and that is a different and
stronger question.  Five defects fell out of it, every one invisible
to 603 green sections:

  * a stand-in written "(8)215003." (bare trailing dot) classified as
    a competing DEFINE;
  * printed p.157 carrying a VERBATIM COPY of p.103's "SCOMRG
    XW,(8)520000." defining card -- an XW is a PLACE, so the copy
    landed at p.157's own counter, bit 2048 instead of 215001.00;
  * SL, SM and STDMOD declared with NO dds on pages that only USE
    them (a VFL operation writing no dds takes its length from the
    SYMBOL, so the merge would have picked one silently);
  * a SYN to a bare symbol not inheriting its target's dds, which made
    three pages spelling printed p.99's "S UN A SYN,S UN AA" alias
    look like they contradicted five pages spelling (BU,25);
  * printed pp.153 and 155 carrying "SYN, 12"/"SYN, 11" where p.154's
    DEFINING card prints "SYN,12.0"/"SYN,11.0".

THE WORD ACCOUNTING IS THE POINT OF THE LAST TEST BELOW.  A missing
word reads as ZERO and a zero half word is BRANCH ENABLED to location
zero, so a hole and a lost transcription must never be confused.  Two
things make a hole legitimate and both are PRINTED EVIDENCE in the
deck:

  * a DR/DRZ reservation -- "nothing is emitted, and that is the
    point";
  * a FORWARD SLC -- the counter moves on and what lies between is not
    this deck's.

printed p.112 is why the second had to be recorded.  Five printed SLC
cards (SIPT+4.0, +9.0, +18.0, +20.0, +22.0, the line-11 comment
naming them "PARALLEL IO INTERRUPT SLOTS") skip exactly thirteen
words -- 215104-6, 215110-13, 215121-4, 215126 and 215130 -- and NO
DECK IN THE CORPUS EMITS AT ANY OF THEM.  That deck calls them "slots
of the table that other pages fill"; they are not filled, and the
volume OCR's only trace of one is a REFERENCE, "V-I,2,SIPT+1.0"
against 215104.05, "TYPE OF INTERRUPT AS FULL WORD".  They are
storage, and the SLC is IBM's own statement that they are.

MEASURED INJECTION, run, with what it actually printed.  Stop
recording the SLC spans (drop the slc_skips.append in strap_asm's SLC
branch) and TWO checks fail, not the one predicted:

    every_word_accounted_for   13   expected 0
    holes_include_slc_skips    False expected True

and the first names 0o215104, 0o215105, 0o215106, 0o215110 ... in
order.  The second failing as well is the point of having it: it is
there so that a change which silently stopped recording ONE of the two
kinds of legitimate hole cannot hide behind the other.

THE END TARGET IS A PLACEHOLDER.  build() always appends "END, <sym>",
and MCP's body entry point has not been established, so SDISP is
passed to make it assemble and nothing here depends on it.  Finding
the real entry is open work.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
import mcp_image                                          # noqa: E402

FIRST, LAST = 99, 192


def body_pages():
    return [(mcp_image.DECK("mcp_bootstrap_p%d.strap" % n), "printed p.%d" % n)
            for n in range(FIRST, LAST + 1)
            if n not in mcp_image.NO_DECK_PAGES]


def main():
    fails = 0

    def check(name, got, want):
        nonlocal fails
        ok = got == want
        if not ok:
            fails += 1
        print(f"{'PASS' if ok else 'FAIL'} {name} = {got}"
              f"{'' if ok else f' expected {want}'}")

    pages = body_pages()
    check("body_page_count", len(pages), 93)

    # merge() raises SystemExit on a symbol or dds disagreement, which
    # is the whole cross-check.  Reaching the next line IS the result.
    prog, src, defined, external = mcp_image.build(
        False, pages, end_at="SDISP")
    print(f"PASS merges_without_disagreement = {len(defined)} defined, "
          f"{len(external)} external")

    words = sorted(prog.words)
    check("origin_is_the_MCP_body", oct(words[0]), oct(0o215000))
    check("image_is_nonempty", len(prog.words) > 1500, True)

    holes = {w for w in range(words[0], words[-1] + 1)
             if w not in prog.words}
    reserved = prog.reserved_words()
    skipped = prog.skipped_words()
    unaccounted = sorted(holes - reserved - skipped)
    if unaccounted:
        print("     unaccounted words: "
              + ", ".join("0o%o" % w for w in unaccounted[:12]))
    check("every_word_accounted_for", len(unaccounted), 0)

    # >>> AND THE SLC-COVERED HOLES MUST BE EXACTLY THE KNOWN ONES.
    # <<<  Accepting ANY SLC skip as legitimate re-opened the hole the
    # original contract existed to close.  Every deck substitutes a
    # hard origin SLC for its printed "SLC,$", so a page LOST from the
    # list -- or a row lost off the bottom of a page -- is jumped over
    # by the NEXT deck's origin SLC and counts as accounted for.
    # Measured: drop printed p.140 from the page list and the build
    # still reports 0 unaccounted.  printed p.175's transcriber
    # spotted it before it could mislead anyone.
    #
    # So the skips that coincide with holes are pinned by VALUE.  All
    # thirteen are printed p.112's five SLC cards (SIPT+4.0, +9.0,
    # +18.0, +20.0, +22.0), the "PARALLEL IO INTERRUPT SLOTS" its own
    # line 11 names.  A new one means a page or a row went missing.
    expected_skip_holes = {
        0o215104, 0o215105, 0o215106,
        0o215110, 0o215111, 0o215112, 0o215113,
        0o215121, 0o215122, 0o215123, 0o215124,
        0o215126,
        0o215130,
    }
    got_skip_holes = holes & skipped
    extra = sorted(got_skip_holes - expected_skip_holes)
    missing = sorted(expected_skip_holes - got_skip_holes)
    if extra:
        print("     UNEXPECTED SLC-covered holes (a lost page or row?): "
              + ", ".join("0o%o" % w for w in extra[:12]))
    if missing:
        print("     expected SLC-covered holes now filled: "
              + ", ".join("0o%o" % w for w in missing[:12]))
    check("slc_holes_are_exactly_the_known_ones",
          (len(extra), len(missing)), (0, 0))

    # And the two kinds are both actually exercised here, so a future
    # change that silently stopped recording one would show up.
    check("holes_include_reservations", len(holes & reserved) > 0, True)
    check("holes_include_slc_skips", len(holes & skipped) > 0, True)
    print(f"     {len(holes)} hole words = {len(holes & reserved)} reserved "
          f"+ {len(holes & skipped)} SLC-skipped")

    if fails:
        print(f"\n{fails} TEST(S) FAILED")
    else:
        print("\nALL TESTS PASSED")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
