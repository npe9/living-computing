#!/usr/bin/env python3
"""check_mcp_body_image.py -- MCP's BODY, printed pp.99-439, merged
into one image per overlay and made to account for every word.

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

every_page_row_holds_in_image, MEASURED 2026-11-05 (7,113 rows+syms):

    control                                       PASS, 0
    VF labels' (B,25) removed from strap_asm      FAIL, 3 (pp.221, 225,
                                                  228: M+-1,V TSQ)
    p.220's defining "V EOFX DD(BU,1)" made       FAIL, 1 (p.215 line 45,
    (BU,2), in a scratch copy of decks/           CM0C00,V EOFX), and
                                                  merge() no longer
                                                  refuses it: the use
                                                  on another page is
                                                  what catches it

overlay_fill_is_exactly_the_known_words, MEASURED 2026-11-06:

    control                                       PASS, both images
    printed p.331 dropped from the LOADER         FAIL LOADER (32, 0):
                                                  0o235222.. -- and NOTHING
                                                  ELSE fails: the merge and
                                                  every row hold, because the
                                                  other pages' stand-ins cover
                                                  its symbols
    written_words made every word in the image    FAIL both (0, 582) and
                                                  (0, 784)

  re-measured 2026-11-06 with three overlays (through printed p.377):
    control                                       PASS, all three images
    written_words made every word in the image    FAIL all three: LOADER
                                                  (0, 582), $DUMP (0, 133),
                                                  SCOMD (0, 589)

  $EOJ, the low-core program (printed pp.381-439), MEASURED 2026-11-06:
    control                                       PASS, all four images
    printed p.389 dropped                         FAIL slc_holes (25 words)
    printed p.381 dropped                         FAIL low_region_origin
                                                  (0o20031)
    reserved words no longer excluded from the    FAIL (1, 0): 020252, p.387's
    SLC holes                                     YI4TA DR(BU),(1)

THE END TARGET IS A PLACEHOLDER.  build() always appends "END, <sym>",
and MCP's body entry point has not been established, so SDISP is
passed to make it assemble and nothing here depends on it.  Finding
the real entry is open work.
"""
import contextlib
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
sys.path.insert(0, HERE)
import mcp_image                                          # noqa: E402
import verify_mcp_page                                    # noqa: E402
from listing_oracle import check_rows                     # noqa: E402

FIRST, LAST = 99, 439

# >>> THE BODY IS ONE RESIDENT PART AND THREE OVERLAYS. <<<  printed
# p.319 line 14 reserves "Y MPBUF DRZ(BU),1088 -RESERVE ROOM FOR
# OVERLAID AREA", and three programs are assembled INTO it: the JOB
# CONTROL BINARY LOADER (PUNID 22LOADER, printed p.320 line 10
# "SLC,YMPBUF"), the debugger/$DUMP (PUNID 22$DUMP, printed p.335
# line 8 "SLC,YMPBUF", the same 234424.00) and the SYSTEM COMMAND
# package (PUNID 22SCOMD, card series WA, printed p.361 line 7
# "SLC,YMPBUF").  They occupy the same
# words, so no one image holds both: merging them refused at once on
# words p.320 and p.335 both write.  Each overlay is merged with the
# resident pages it runs beside, and each image is checked whole.
RESIDENT = (99, 319)
OVERLAYS = (("LOADER", 320, 334), ("$DUMP", 335, 360), ("SCOMD", 361, 380),
            ("$EOJ", 381, LAST))

# >>> AND A FOURTH PROGRAM IS NOT IN Y MPBUF AT ALL. <<<  printed p.381
# lines 2-3 are SCOMD's last two cards; line 5 is "PUNID,22$EOJ" and
# line 7 "SLC,YPPMEM" -- 020000.00 (printed p.269 line 11, "YPPMEM
# SYN,(8)20000."), the problem-program origin, far below the body.  It
# is merged with the resident pages like an overlay, since it calls
# them, and its own words are accounted for as a second region.
LOW_ORIGIN = {"$EOJ": 0o020000}


def _pages(a, b):
    skip = mcp_image.NO_DECK_PAGES | mcp_image.MISSING_PAGES
    return [(mcp_image.DECK("mcp_bootstrap_p%d.strap" % n), "printed p.%d" % n)
            for n in range(a, b + 1) if n not in skip]


def body_pages():
    """Every landed body page, resident and overlay, in printed order."""
    return _pages(FIRST, LAST)


# The SLC-covered holes each image must show, pinned by VALUE (see
# the note in check_image).  Thirteen are printed p.112's five SLC
# cards (SIPT+4.0, +9.0, +18.0, +20.0, +22.0), the "PARALLEL IO
# INTERRUPT SLOTS" its own line 11 names; four are printed p.256's CC
# stand-in ("RDLEOF (CC*)DD(BU,,12),B  COMD, OFFLINE,": 22 twelve-bit
# characters, 264 bits from 230411.00 to 230415.10, which strap_asm
# refuses, so the deck SLCs to line 35's printed 230415.40 and these
# four words are its DATA, not a lost row -- they leave this list when
# CC entry mode is implemented).
RESIDENT_SKIP_HOLES = {
    0o215104, 0o215105, 0o215106,
    0o215110, 0o215111, 0o215112, 0o215113,
    0o215121, 0o215122, 0o215123, 0o215124,
    0o215126,
    0o215130,
    0o230411, 0o230412, 0o230413, 0o230414,
}
OVERLAY_SKIP_HOLES = {
    "LOADER": set(),
    "$DUMP": set(),
    "SCOMD": set(),
    "$EOJ": set(),
}

# >>> INSIDE THE OVERLAID AREA A LOST PAGE IS NOT A HOLE. <<<  Y MPBUF
# is a DRZ, and its zero fill puts every one of its words into the
# image, so every_word_accounted_for cannot see a page missing from an
# overlay: printed p.329, which the scan lacks, passed it with 0
# unaccounted.  strap_asm now records the words a statement actually
# WROTE (written_words), and the words of Y MPBUF that only the fill
# holds are pinned here by value, each run with its printed reason.
YMPBUF = (0o234424, 0o236524)          # printed p.319 line 14, 1088 words
def _span(a, b):
    return set(range(a, b + 1))
FILL_ONLY = {
    "LOADER": (
        # printed p.329, MISSING FROM THE SCAN (mcp_image.MISSING_PAGES):
        # p.328 ends at 235111.40, p.330 opens at 235154.00.
        _span(0o235112, 0o235153)
        # printed p.332 line 35, "Y RLDTA DR(N),(1)" -- prints 000001.00.
        | {0o235307}
        # printed p.334, "Y LJM1 DRZ" -- prints 000004.00.
        | _span(0o235410, 0o235413)
        # printed p.334 line 53, "C DSKBF DRZ" -- prints 001000.00, the
        # disk fetch buffer (TC000001).
        | _span(0o235464, 0o236463)
        # past p.334's Z FINIS VF at 236464.00: the end of Y MPBUF,
        # which the LOADER does not use.
        | _span(0o236465, 0o236523)),
    "$DUMP": (
        # printed p.358 lines 34-37, the dump's four DRZ(N) work areas
        # ATEMPD 236043, ABUFF 236044, APCOL1 236105, AMNMBF 236126,
        # ending where AHLFWD's flag word prints at 236147.
        _span(0o236043, 0o236146)
        # printed p.359 lines 40-42, one card "DD(N),1.E128,1.E512,
        # 9.99999E615": 1.E512 and 9.99999E615 lie outside the range
        # C28-6129 printed p.27 gives and print one exponent for two
        # numbers, so the card is not assembled (the deck SLCs past).
        | _span(0o236211, 0o236213)
        # past printed p.360's last VF at 236425.00 -- p.361's header
        # cards at 236425.31 belong to the SCOMD image -- the end of
        # Y MPBUF, which the $DUMP does not use.
        | _span(0o236426, 0o236523)),
    "SCOMD": (
        # printed p.363 lines 31-32, "J STLR DR(BU,64),(16)" and
        # "J C BUF DR(BU,6),(80)": reservations, not zeroed.
        _span(0o234530, 0o234556)
        # printed p.363 line 33, "J FLD B DRZ,(12)" -- a DR(N), twelve
        # words from 234560.00.
        | _span(0o234560, 0o234573)
        # printed p.365 line 15, "J ERZ DRZ(BU,64),1".
        | {0o234636}
        # printed p.371 line 45, "Z ST IND DRZ(N),(1)".
        | {0o235155}
        # past printed p.380's VDUB at 235570.00: printed p.381 lines
        # 2-3, two (CC*)DD trailer cards from 235570.10, stood in by SLCs
        # because the CC entry mode is not implemented (as p.361's are),
        # and then the end of Y MPBUF.  Shrinks when CC lands.
        | _span(0o235571, 0o236523)),
    # The $EOJ is not assembled into Y MPBUF: the whole buffer is the
    # resident DRZ's fill.
    "$EOJ": _span(YMPBUF[0], YMPBUF[1] - 1),
}

# A floor on the rows each image checks, so an image that silently
# lost its pages cannot pass on an empty check.  The first image
# checks every resident row; an overlay checks its own pages.
ROWS_FLOOR = {"LOADER": 7000, "$DUMP": 1000, "SCOMD": 600, "$EOJ": 500}


def main():
    fails = 0

    def check(name, got, want):
        nonlocal fails
        ok = got == want
        if not ok:
            fails += 1
        print(f"{'PASS' if ok else 'FAIL'} {name} = {got}"
              f"{'' if ok else f' expected {want}'}")

    check("body_page_count", len(body_pages()), 335)
    resident = _pages(*RESIDENT)
    for name, a, b in OVERLAYS:
        print(f"--- {name}: resident pp.{RESIDENT[0]}-{RESIDENT[1]} + pp.{a}-{b} ---")
        # The resident pages' rows are checked in the first image only:
        # they are the same cards in both.
        check_image(check, name, resident + _pages(a, b),
                    None if name == OVERLAYS[0][0] else _pages(a, b),
                    RESIDENT_SKIP_HOLES | OVERLAY_SKIP_HOLES[name], FILL_ONLY[name],
                    LOW_ORIGIN.get(name))
    if fails:
        print(f"\n{fails} TEST(S) FAILED")
    else:
        print("\nALL TESTS PASSED")
    return 1 if fails else 0


def check_image(check_, name, pages, row_pages, expected_skip_holes, fill_only,
                low_origin=None):
    def check(label, got, want):
        check_(f"{name}: {label}", got, want)

    # merge() raises SystemExit on a symbol or dds disagreement, which
    # is the whole cross-check.  Reaching the next line IS the result.
    prog, src, defined, external = mcp_image.build(
        False, pages, end_at="SDISP")
    print(f"PASS {name}: merges_without_disagreement = {len(defined)} defined, "
          f"{len(external)} external")

    # >>> EVERY PAGE'S ROWS MUST HOLD IN THE MERGED IMAGE. <<<
    # verify_mcp_page checks a deck against its listing with that
    # deck's OWN stand-ins, and merge() drops the stand-in of every
    # symbol some page defines -- so a use is only ever proved against
    # the defining card HERE.  printed p.221 line 20, "M+1,V TSQ",
    # verified on its own page with "V TSQ SYN(B,25,1)" and assembled
    # 031100.22 in the image against a printed 031100.02, because
    # printed p.220 defines V TSQ with a VF card and VF labels had no
    # dds; C22-6531 printed p.19 gives them (B, 25).  Three rows of
    # 7,113 failed when this was first run (2026-11-05), all of them
    # that one rule.
    #
    # It is also what lets merge() hold only EXTERNAL symbols to one
    # stand-in dds: for a symbol the image defines, this proves the
    # defining dds gives the printed bits at every use, which is what
    # agreeing stand-in strings were standing in for.
    rows_total, row_fails = 0, 0
    row_pages = pages if row_pages is None else row_pages
    for path, label in row_pages:
        syms, rows, _ = verify_mcp_page.parse(open(path).read())
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            f = check_rows(prog, rows, syms, label=label + " ")
        rows_total += len(rows) + len(syms)
        row_fails += f
        for line in buf.getvalue().splitlines():
            if f and line.startswith("FAIL"):
                print("     " + line[:170])
    check("every_page_row_holds_in_image", row_fails, 0)
    # The first image carries the resident pages' 7,000-odd rows; an
    # overlay's own pages carry a few hundred.
    check("image_rows_checked", rows_total >= ROWS_FLOOR[name], True)

    # The words below the body are a separate program's region (the
    # $EOJ); each region is accounted for over its own span, so the
    # gap between them is not "holes".
    low = sorted(w for w in prog.words if w < 0o215000)
    words = sorted(w for w in prog.words if w >= 0o215000)
    check("origin_is_the_MCP_body", oct(words[0]), oct(0o215000))
    check("low_region_origin", oct(low[0]) if low else None,
          None if low_origin is None else oct(low_origin))
    check("image_is_nonempty", len(prog.words) > 1500, True)

    holes = {w for w in range(words[0], words[-1] + 1)
             if w not in prog.words}
    if low:
        holes |= {w for w in range(low[0], low[-1] + 1) if w not in prog.words}
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
    # So the skips that coincide with holes are pinned by VALUE.
    # Thirteen are printed p.112's five SLC cards (SIPT+4.0, +9.0,
    # +18.0, +20.0, +22.0), the "PARALLEL IO INTERRUPT SLOTS" its own
    # line 11 names; four are printed p.256's CC stand-in, below.  A
    # new one means a page or a row went missing.
    # expected_skip_holes: passed in (RESIDENT_SKIP_HOLES and the
    # overlay's own, above).
    # A reserved word is accounted for by its own DR card, even when an
    # SLC's span also covers it: the body's first SLC (040 -> 215000)
    # spans the whole $EOJ region, so printed p.387 line 31's "Y I4TA
    # DR(BU),(1)" at 020252.00 read as an SLC hole until this.
    got_skip_holes = (holes - reserved) & skipped
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

    got_fill = {w for w in range(*YMPBUF) if w not in prog.written_words}
    extra, missing = sorted(got_fill - fill_only), sorted(fill_only - got_fill)
    if extra:
        print("     UNEXPECTED fill-only words in Y MPBUF (a lost page or row?): "
              + ", ".join("0o%o" % w for w in extra[:12]))
    if missing:
        print("     expected fill-only words in Y MPBUF now written: "
              + ", ".join("0o%o" % w for w in missing[:12]))
    check("overlay_fill_is_exactly_the_known_words", (len(extra), len(missing)), (0, 0))

    # And the two kinds are both actually exercised here, so a future
    # change that silently stopped recording one would show up.
    check("holes_include_reservations", len(holes & reserved) > 0, True)
    check("holes_include_slc_skips", len(holes & skipped) > 0, True)
    print(f"     {len(holes)} hole words = {len(holes & reserved)} reserved "
          f"+ {len((holes - reserved) & skipped)} SLC-skipped")



if __name__ == "__main__":
    sys.exit(main())
