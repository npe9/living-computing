#!/usr/bin/env python3
"""mcp_coverage_report.py -- which decks verify less than their page
prints?  ADVISORY.  It points at pages worth looking at; it does not
decide anything.

>>> THIS WAS WRITTEN AS A SUITE TEST AND DEMOTED TO A TOOL, because
its premise is not true. <<<  Both pages it accused turned out to be
at least partly innocent, and the write-up is the useful part.

THE IDEA.  verify_mcp_page.py compares a deck against the `!CHECK`
rows THE DECK ITSELF DECLARES, so a deck declaring two checks for a
page printing twenty-four rows passes cleanly having verified almost
nothing.  Nothing else in the suite can see that, because everything
else starts from the deck.  docs/mcp_page_map.json does not: it is an
OCR pass over the PAGE (strap/mcp_survey.py), independent of every
deck.  So compare them.

WHY IT IS NOT A TEST.

  1. FIRST PREMISE, "a definition prints a trailing + so subtract the
     + rows": it depends on OCR READING the "+", and on printed p.85
     the OCR saw it on 2 rows of about 15.  The other thirteen were
     counted as machine code, p.85's correct deck was reported short
     by eleven rows, and an agent was dispatched to close a gap that
     does not exist.  Caught by rendering the page and looking.
     A TEST WHOSE EXPECTED VALUE IS ITSELF AN OCR READING INHERITS
     THAT OCR'S FAILURES.

  2. SECOND PREMISE, "every located row is either a !SYM or a
     !CHECK": also false.  printed p.86's lines 8, 10, 12, 14 and 16
     are (AX)DD character rows that print a LOCATION AND NO BINARY
     COLUMN AT ALL -- there is nothing for a !CHECK to compare
     against.  So a page can carry located rows that are neither
     definitions nor checkable code, and the count cannot be
     predicted from the deck.

What survives is the comparison as a POINTER.  A deck accounting for
far fewer rows than the page shows is worth a look, and looking is
cheap: render the LOCATION and BINARY columns and see whether the
missing rows print any binary.  Two looks produced one real finding
(printed p.86 checks six of its control words and none of the scan
TABLE data beside them, which strap/prosa.py's fixture depends on)
and one false alarm.  That is a reasonable yield for a tool and an
unacceptable one for a test.

    python3 strap/mcp_coverage_report.py
"""

import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MAP = os.path.join(HERE, "..", "docs", "mcp_page_map.json")
DECKS = os.path.join(HERE, "..", "decks")

# printed page -> (allowed shortfall, why).  Each is a row the page
# prints and the deck cannot check, for a reason that is not "nobody
# looked".
EXPECTED = {
    99: (2, "lines 9 and 10 are (CC*)DD card images and strap_asm has no "
            "CC entry mode -- its 12-bit card code is tabulated in no "
            "document read so far; printed p.15 set the same precedent"),
}


def main():
    if not os.path.exists(MAP):
        print("FAIL docs/mcp_page_map.json is missing -- run "
              "strap/mcp_survey.py")
        return 1
    m = json.load(open(MAP))
    # Only pages whose number agrees with the volume's verified +7
    # offset; see docs/ocr_calibration.md.
    by = {r["printed"]: r for k, r in m.items()
          if r["printed"] is not None and int(k) - r["printed"] == 7}

    fails = 0
    checked = 0
    for f in sorted(glob.glob(os.path.join(DECKS, "mcp_bootstrap_p*.strap"))):
        hit = re.search(r"_p(\d+)\.strap$", f)
        if not hit:
            continue
        page = int(hit.group(1))
        if page not in by:
            continue
        txt = open(f, encoding="utf-8", errors="replace").read()
        nchk = len(re.findall(r"^!CHECK ", txt, re.M))
        nsym = len(re.findall(r"^!SYM ", txt, re.M))
        if not nchk and not nsym:
            continue            # not a block-carrying deck
        s = by[page]
        want = s["rows"]
        allow, why = EXPECTED.get(page, (0, None))
        checked += 1
        have = nchk + nsym
        if have + allow < want:
            fails += 1
            print(f"LOOK printed p.{page}: deck accounts for {have} rows "
                  f"({nchk} !CHECK + {nsym} !SYM), the page survey found "
                  f"{want} carrying a location"
                  + (f" (allowing {allow}: {why})" if allow else "")
                  + f" -- {want - have - allow} printed row(s) are neither "
                  f"checked nor declared")
        elif allow and have + allow >= want > have:
            print(f"  ok printed p.{page}: {have} accounted, {want - have} "
                  f"expected shortfall -- {why}")
        else:
            print(f"  ok printed p.{page}: {have} accounted "
                  f"({nchk} !CHECK + {nsym} !SYM) >= {want} found")
    if fails:
        print(f"\n{fails} of {checked} decks account for fewer rows than "
              f"their page shows. THAT IS A POINTER, NOT A VERDICT -- render\n"
              f"the LOCATION and BINARY columns and see whether the missing\n"
              f"rows print any binary at all. See this file's docstring.")
    else:
        print(f"\n{checked} decks account for every row the survey found")
    return 0        # advisory: never fails a build


if __name__ == "__main__":
    sys.exit(main())
