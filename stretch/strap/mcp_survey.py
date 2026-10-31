#!/usr/bin/env python3
"""mcp_survey.py -- read EVERY page of an MCP listing scan, at the dpi
each measurement actually needs, and emit a machine-readable map.

>>> WHY THIS EXISTS. <<<  Transcription had been going one page at a
time, and every page began by rendering a header and confirming its
number by eye, because PDF PAGE != PRINTED PAGE and the offset is NOT
CONSTANT (mcp_crop.sh says so: volume 1 duplicates pp.1-2 and carries
blanks).  That is a per-page manual step on a 256-page document, and
it is why the work kept stopping at whatever page attention ran out
on.  This reads all of them in one run and says which pages are left.

WHAT IT MEASURES, and at what resolution, and why that one:

  printed page number   600 dpi, a crop WIDE ENOUGH TO INCLUDE THE
                        WORDS "PAGE NUMBER", tesseract --psm 7 and NO
                        whitelist.  Every part of that was forced by
                        measurement and each obvious choice was worse:

                          * a tight crop of the digits with a DIGIT
                            WHITELIST returns "1" for 101.  Without the
                            whitelist the same crop reads "Lol" -- this
                            drum's 1 is an l and its 0 is an o, so the
                            whitelist leaves tesseract nothing legal to
                            map them to and it drops them.
                          * upscaling that crop 300%/400%, or rendering
                            it at 900 dpi, returns NOTHING AT ALL.
                          * keeping "PAGE NUMBER" in the frame fixes
                            101, because the surrounding word gives the
                            segmenter something to work with.
                          * at 400 dpi that still read printed 102 as
                            107.  At 600 dpi it is right.

                        Measured over PDF pages 103-115, whose printed
                        numbers are known from the decks: 13 of 13.
                        The number is the LAST run of digits on the
                        line -- "3/01" and stray marks come earlier --
                        and the result is still CHECKED, not trusted;
                        see "THE PAGE MAP CHECKS ITSELF" below.

  LOCATION column       600 dpi, psm 6, whitelist "0123456789.+*".
                        This is mcp_ocr.py's window and resolution.
                        That file measures its own accuracy at ROUGHLY
                        85% of lines on a drum-printer scan and says in
                        capitals that it is a cross-check and not a
                        source.  THAT IS FINE HERE and would not be
                        fine in a deck: a survey asks "does this page
                        carry locations, about how many, over what
                        range", and losing one line in seven changes
                        none of those answers.  DO NOT transcribe from
                        this output.

  "+" suffix            A definitions page prints its LOCATION with a
                        trailing "+" (it is a SYMBOL VALUE, not an
                        address; the location counter never moves).  A
                        code page does not.  So the proportion of "+"
                        rows separates "defines things" from "compiles
                        things" without reading a single statement.
                        mcp_ocr.py's whitelist omits "+"; this one adds
                        it, which is the only difference in the window.

THE PAGE MAP CHECKS ITSELF, which is the point of doing all of them.
One page's OCR can misread 103 as 108 and nothing local would notice.
Over the whole document the numbers must RUN CONSECUTIVELY, so the
check is not "is this digit right" but "does the sequence step by one"
-- and a misread shows up as a break between two neighbours that agree
with each other.  The report prints every break and every offset
change rather than smoothing them, because an offset change is a real
feature of this scan and a break is a real OCR failure, and they look
different: an offset change persists, a misread is one page wide.

Usage:
    python3 mcp_survey.py                 # whole PDF, cached
    python3 mcp_survey.py --pages 88-115  # a range, for checking
    python3 mcp_survey.py --report        # re-read the cache only
"""

import argparse
import collections
import concurrent.futures
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(HERE, "..", "docs", "MCP_Mar63_001-249.pdf")
CACHE = os.path.join(HERE, "..", "docs", "mcp_page_map.json")

# "PAGE NUMBER <n>", in 600-dpi pixels.  The window deliberately
# includes the WORDS: see the docstring -- the digits alone do not read.
# Calibrated against PDF pages 103-115, whose printed numbers 96-108
# are known from the decks transcribed under them.
HDR = dict(dpi=600, x=6150, y=277, w=3300, h=105)

# LINE + LOCATION, in 600-dpi pixels: mcp_crop.sh's "loc" window
# (X=400 W=2400) over mcp_ocr.py's row span (y=720, H=4200).
LOC = dict(dpi=600, x=400, y=720, w=2400, h=4200)


def _render(page, box, tmp):
    out = os.path.join(tmp, "p")
    subprocess.run(["pdftoppm", "-f", str(page), "-l", str(page),
                    "-r", str(box["dpi"]), "-png",
                    "-x", str(box["x"]), "-y", str(box["y"]),
                    "-W", str(box["w"]), "-H", str(box["h"]),
                    PDF, out], check=True, capture_output=True)
    for name in sorted(os.listdir(tmp)):
        if name.endswith(".png"):
            return os.path.join(tmp, name)
    return None


def _ocr(png, psm, whitelist):
    cmd = ["tesseract", png, "stdout", "--psm", str(psm)]
    if whitelist:
        cmd += ["-c", "tessedit_char_whitelist=" + whitelist]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout


def survey_page(page):
    """Everything this tool knows about one PDF page."""
    rec = {"pdf": page, "printed": None, "rows": 0, "plus": 0,
           "first": None, "last": None, "raw": "", "loc_raw": ""}
    # tesseract cannot read what pdftoppm writes into /tmp here, so each
    # worker gets its own directory (same reason mcp_ocr.py mkdtemps).
    with tempfile.TemporaryDirectory() as tmp:
        png = _render(page, HDR, tmp)
        if png:
            txt = _ocr(png, 7, None)
            rec["raw"] = " ".join(txt.split())
            rec["printed"] = page_number(rec["raw"])
    with tempfile.TemporaryDirectory() as tmp:
        png = _render(page, LOC, tmp)
        if png:
            txt = _ocr(png, 6, None)
            rec["loc_raw"] = txt
            locs = []
            for line in txt.splitlines():
                # A location is six octal digits, a dot and two more.
                # The line number sits to its left in the same window,
                # so anchor on the dotted form rather than on position.
                #
                # >>> PERMISSIVE ON PURPOSE, AND THE OPPOSITE OF
                # page_number() ABOVE. <<<  This drum prints 0 as an
                # open C or O, so printed p.108's eight SYN cards come
                # back as "OCCCCC.CCt", "OCCCC2.CC+", "OCCCO3.00+".
                # A pattern demanding \d matched NONE of them, the
                # page was recorded as carrying ZERO located rows, and
                # it was classified as compiling nothing -- which went
                # into an agent's brief as "this page COMPILES NOTHING"
                # for a page that is eight SYN cards.  (The agent
                # ignored it and transcribed them. The brief was
                # wrong, not the agent.)
                #
                # The rule that separates this from page_number(): a
                # VALUE must be read strictly, because a wrong value is
                # a confident error.  A COUNT should be read loosely,
                # because a missed row is a silent undercount and the
                # count feeds no arithmetic.  So O and C count as
                # digits here and must never do so there.
                # the optional space is real: tesseract renders
                # printed p.108 line 12 as "OCCCCC. 32+".
                hit = re.search(r"([0-9OCoc]{4,6}\. ?[0-9OCoc]{1,2})([+t]?)", line)
                if hit:
                    locs.append(hit.group(0))
            rec["rows"] = len(locs)
            # "+" often prints as a "t" to tesseract.
            rec["plus"] = sum(1 for s in locs if s.endswith(("+", "t")))
            if locs:
                rec["first"], rec["last"] = locs[0], locs[-1]
    return rec


def page_number(raw):
    """The printed page number in one header line, or None.

    >>> TWO OBVIOUS PARSERS ARE WORSE THAN NO PARSER. <<<  Both of the
    following were written, measured and removed; see
    docs/ocr_calibration.md.  They matter because each produced a
    CONFIDENT WRONG ANSWER where this one refuses.

    1. "take the last run of digits".  The same crop carries the
       distribution date "3/01", so a page whose number failed to OCR
       at all came back as PAGE 1 with nothing to show it had failed.
       Hence: anchor on the word NUMBER, and take only what follows.

    2. "map the drum's glyph confusions" (l->1, o/C->0, a/B->8,
       T/q/?->7).  Measured over the 249 numbered pages it reads
       SIX MORE pages correctly (232 against 226) and FIVE MORE
       pages WRONGLY (15 against 10), converting eleven refusals
       into a mix.  It is still not used, and the reason is not
       accuracy: a refusal can never be undetectable and a
       fabrication can.  A guessed number that happened to land on
       the modal offset would pass every check here silently, and a
       parser that guesses more has more chances to do it.  The six
       readings given up are recovered from the offset for free.

    tesseract renders "NUMBER" as NUMRER, NiiMReD, NLMRER, AUMBER and
    worse, so the anchor is fuzzy -- a word starting N, ending R or D
    -- and the LAST such word wins, because "PAGE" never matches it.
    """
    if not raw:
        return None
    end = None
    for m in re.finditer(r"[A-Za-z]{3,9}", raw):
        w = m.group(0).upper()
        if w.startswith("N") and w.endswith(("R", "D")):
            end = m.end()
    if end is None:
        return None
    # The negative lookahead rejects a LETTER too, not just a digit:
    # "PAGE NUMBER 2l" is 21 with the 1 read as an l, and matching
    # just the "2" would report page 2 -- confidently, wrongly.  Let
    # it refuse; the modal-offset check recovers it for free.
    tok = re.match(r"[^0-9A-Za-z]{0,3}([0-9]{1,3})(?![0-9A-Za-z])", raw[end:])
    return int(tok.group(1)) if tok else None


def classify(rec):
    """A coarse label, from the measurements only."""
    if rec["rows"] == 0:
        return "no-locations"          # comments, blank, or unreadable
    if rec["plus"] >= 0.8 * rec["rows"]:
        return "definitions"           # SYN values, counter never moves
    if rec["plus"] == 0:
        return "code"
    return "mixed"


def report(recs):
    recs = sorted(recs, key=lambda r: r["pdf"])
    print(f"{'PDF':>4} {'printed':>7} {'off':>4} {'rows':>5} {'+':>4}  "
          f"{'first':>10} {'last':>10}  kind")
    prev_printed = prev_off = None
    breaks, offsets = [], []
    for r in recs:
        p = r["printed"]
        off = (r["pdf"] - p) if p is not None else None
        kind = classify(r)
        print(f"{r['pdf']:>4} {str(p):>7} {str(off):>4} {r['rows']:>5} "
              f"{r['plus']:>4}  {str(r['first']):>10} {str(r['last']):>10}"
              f"  {kind}")
        if p is not None and prev_printed is not None and p != prev_printed + 1:
            breaks.append((prev_printed, p, r["pdf"]))
        if off is not None and off != prev_off:
            offsets.append((r["pdf"], p, off))
            prev_off = off
        if p is not None:
            prev_printed = p
    # >>> THE CHECK IS GLOBAL, BECAUSE A LOCAL ONE CAN BE FOOLED. <<<
    # "Printed numbers run consecutively, so a misread breaks the
    # sequence" sounds sufficient and is not: on this scan PDF 80-83
    # are four CONSECUTIVE pages that agree with each other at offset
    # +67, every one of them printed 73-76 with the leading 7 read as
    # a 1.  Scan quality is correlated down a document, so the same
    # misreading repeating is ordinary, not freak, and it defeats any
    # check made of local agreement.  The OFFSET is a property of the
    # whole scan, so the modal offset is not foolable that way: here
    # it wins 226 to 6.
    offs = collections.Counter(r["pdf"] - r["printed"]
                               for r in recs if r["printed"] is not None)
    if offs:
        modal, n = offs.most_common(1)[0]
        print()
        print(f"=== OFFSET: modal {modal:+d} on {n} of {sum(offs.values())} "
              f"readable pages ===")
        for off, c in offs.most_common():
            if off != modal:
                pages = [r["pdf"] for r in recs
                         if r["printed"] is not None
                         and r["pdf"] - r["printed"] == off]
                print(f"  offset {off:+d} on {c}: PDF {pages}")
        agree = [r["pdf"] for r in recs if r["printed"] is not None
                 and r["pdf"] - r["printed"] == modal]
        if agree:
            print(f"  modal pages span PDF {min(agree)}..{max(agree)} "
                  f"= printed {min(agree)-modal}..{max(agree)-modal}")
        print()
        print("=== PAGES NEEDING A SECOND LOOK ===")
        suspect = [r["pdf"] for r in recs
                   if r["printed"] is None
                   or r["pdf"] - r["printed"] != modal]
        print(f"  {len(suspect)} of {len(recs)}: {suspect}")
        print("  (each is RECOVERABLE as pdf - modal; none needs "
              "re-rendering.  A page with no number at all is front "
              "matter, not a failure.)")
    kinds = {}
    for r in recs:
        kinds[classify(r)] = kinds.get(classify(r), 0) + 1
    print()
    print("=== PAGES BY KIND ===")
    for k, n in sorted(kinds.items(), key=lambda kv: -kv[1]):
        print(f"  {k:<14} {n}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", help="PDF page range, e.g. 88-115")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--report", action="store_true",
                    help="re-read the cache and report, render nothing")
    ap.add_argument("--reparse", action="store_true",
                    help="re-derive the page numbers from the CACHED raw "
                         "OCR text and report; renders nothing.  This is "
                         "the loop to use when changing page_number(): "
                         "the OCR is the slow part and it does not change, "
                         "so a parser can be measured against all 256 "
                         "pages in under a second instead of 2m30s.")
    a = ap.parse_args()

    cache = {}
    if os.path.exists(CACHE):
        cache = {int(k): v for k, v in json.load(open(CACHE)).items()}

    if a.report or a.reparse:
        if a.reparse:
            for rec in cache.values():
                rec["printed"] = page_number(rec.get("raw", ""))
            json.dump({str(k): v for k, v in sorted(cache.items())},
                      open(CACHE, "w"), indent=1)
        report(list(cache.values()))
        return 0

    n = int(subprocess.run(["pdfinfo", PDF], capture_output=True, text=True)
            .stdout.split("Pages:")[1].split()[0])
    if a.pages:
        lo, hi = (int(x) for x in a.pages.split("-"))
    else:
        lo, hi = 1, n
    todo = [p for p in range(lo, hi + 1)]
    print(f"surveying PDF pages {lo}-{hi} of {n}, {a.jobs} at a time",
          file=sys.stderr)
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for rec in ex.map(survey_page, todo):
            cache[rec["pdf"]] = rec
            print(f"  PDF {rec['pdf']:>4} -> printed {rec['printed']}, "
                  f"{rec['rows']} located rows", file=sys.stderr)
    json.dump({str(k): v for k, v in sorted(cache.items())},
              open(CACHE, "w"), indent=1)
    report([cache[p] for p in sorted(cache) if lo <= p <= hi])
    return 0


if __name__ == "__main__":
    sys.exit(main())
