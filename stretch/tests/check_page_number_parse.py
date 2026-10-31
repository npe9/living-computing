#!/usr/bin/env python3
"""check_page_number_parse.py -- mcp_survey.page_number() must REFUSE
rather than guess.

Every string below is REAL tesseract output, cached in
docs/mcp_page_map.json from a 600-dpi pass over the MCP scan. The
point of the test is not that the parser reads them -- most of these
cannot be read -- but that it does not INVENT a number for them.

>>> WHY A WRONG ANSWER IS WORSE THAN NO ANSWER HERE. <<<  A page whose
number is None is reported as needing a second look and is recovered
from the modal offset. A page that confidently reports the wrong
number is reported as fine. Two parsers that were written, measured
and removed both failed this way; see docs/ocr_calibration.md.

  * "take the last run of digits" picked up the distribution date
    "3/01" that shares the crop, so every total OCR failure came back
    as PAGE 1.
  * a glyph-confusion map (l->1, o/C->0, a/B->8, T/q/?->7) turned
    "qT" into 77 where the truth is 7 and "a7" into 87 where it is 57.

    BE HONEST ABOUT THAT ONE: measured over the 249 numbered pages
    the map reads SIX MORE correctly (232 vs 226) and FIVE MORE
    WRONGLY (15 vs 10).  Two of the cases below -- "2l" and "12C" --
    it gets RIGHT, and this file still demands None for them.  That
    is deliberate.  Every error of both parsers is caught by the
    modal-offset check, so neither is dangerous on today's corpus;
    the asymmetry is that a REFUSAL CAN NEVER BE UNDETECTABLE AND A
    FABRICATION CAN.  A guessed number landing on the modal offset
    would pass silently.  Six readings are given up to make that
    impossible, and the offset recovers them for nothing.

Both are re-introduceable in one line, which is why they are pinned
here and not only in prose.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "strap"))
from mcp_survey import page_number                      # noqa: E402

# (raw OCR, expected, why)
CASES = [
    # --- reads cleanly ---
    ("/C1 3/01 PAGE NUMBER 103", 103, "the ordinary case"),
    ("s/Cl 3/01 PAGE NUMBER £101", 101,
     "a stray mark before the digits is skipped"),
    ("/Cl 3/01 PAGE NUMBER 104 ,", 104, "trailing punctuation is not a digit"),
    ("IO) 3/01 PAGE NUMRER 102", 102, "NUMBER itself is misread as NUMRER"),
    ("R/C 1 2/07 DACE NiiMReD 117", 117, "...and as NiiMReD"),

    # --- must REFUSE: the number did not survive OCR ---
    ("/C1 3/01 PAGE NUMBER qT", None,
     "7 came back as qT. Must NOT be 1 from the date, nor 77 from a map"),
    ("fO01 3/01 PAGE NUMBER rai", None,
     "77 came back as rai. Must NOT be 1 from the date, nor 81 from a map"),
    ("/C1 3/01 PAGE NUMBER 2l ,", None,
     "21 with the 1 read as l. Must NOT be 2 -- digits followed by a "
     "LETTER are not a complete number"),
    ("/Cl 3/01 PAGE NUMBER 12C .", None,
     "120 with the 0 read as C, the drum's own confusion. Must NOT be 12"),
    ("/O1 37/01 PAGE NUMBER a7", None,
     "57 with the 5 read as a. Must NOT be 87 from a map"),

    # --- must REFUSE: no header at all ---
    ("", None, "a blank front-matter page"),
    ("o .", None, "front matter, specks only"),
    ("E RECORD, IF START iS PUSHED, NEXT TAPE RECORD WILL BE", None,
     "body text in the header band: no NUMBER anchor, so no number"),
    ("ge A F = MmMikisigniiogr +s: ns 2% , |", None,
     "a badly degraded header"),
]


def main():
    fails = 0
    for raw, want, why in CASES:
        got = page_number(raw)
        ok = got == want
        if not ok:
            fails += 1
        print(f"{'PASS' if ok else 'FAIL'} page_number({raw!r:<58}) = "
              f"{got!r:<6} expected {want!r:<6} -- {why}")
    # The date must never be mistaken for the page number, whatever
    # else happens: "3/01" is in every one of these crops.
    for raw, want, _ in CASES:
        if want is None and page_number(raw) == 1:
            print(f"FAIL page_number({raw!r}) returned 1 -- that is the "
                  f"distribution date 3/01, not a page number")
            fails += 1
    if fails:
        print(f"\n{fails} TEST(S) FAILED")
    else:
        print(f"\nALL TESTS PASSED ({len(CASES)} recorded OCR strings)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
