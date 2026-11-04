#!/usr/bin/env python3
"""A transcription work sheet for one printed MCP page, from the reading.

    python3 tools/page_sheet.py PRINTED

One row per printed line: LOCATION, BINARY h1, its hex byte, h2, its hex
byte, and the NAME+STATEMENT draft, each numeric field marked with its
status from docs/vision/listing_reading.tsv:

    =  agreed (Vision and tesseract)       ~  Vision only
    ?  conflict, every value shown         t  tesseract only
    !  agreed but out of order             .  unread
    +  one engine's value, confirmed by     a  no engine read it; the
       location arithmetic                     arithmetic supplies it

Under each draft, "->" is tools/statement_repair.py's CANDIDATE CARD:
label (from the NAME+STATEMENT crop, which keeps one-letter name
fragments) and statement (from the whole page, which reads statements
better) in the decks' space-free spelling, repaired with
STRAP's grammar and the symbols known from every OTHER landed page.

The hex bytes are Vision's alone, folded to 0-9 A-F (O, Q, D -> 0;
I, l -> 1) and marked `h`: C against 0 is NOT settled by any image
method tried (tools/README_vision.md), so every C and 0 in a hex byte
is the assembler's to settle.

THIS IS A WORK SHEET, NOT A TRANSCRIPTION.  Rule 3 is unchanged: the
deck is read off the page image, and its !CHECKs off the page.  The
sheet says where to look hardest: every mark other than `=`.
"""
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "strap"))
import listing_read as R    # noqa: E402
sys.path.insert(0, HERE)
import statement_repair     # noqa: E402

MARK = {"agreed": "=", "vision-only": "~", "conflict": "?", "tesseract-only": "t",
        "agreed-out-of-order": "!", "unread": ".", "arith-confirmed": "+", "arith-only": "a"}
HEX_FIX = str.maketrans({"O": "0", "Q": "0", "D": "0", "I": "1", "L": "1", "|": "1"})


def page_of(printed):
    for r in csv.DictReader(open(os.path.join(ROOT, "docs", "vision", "listing_pages.tsv")),
                            delimiter="\t", quoting=csv.QUOTE_NONE):
        if r["printed"] == str(printed):
            return int(r["vol"]), int(r["pdf"])
    raise SystemExit(f"printed p.{printed} is not in docs/vision/listing_pages.tsv")


def hex_after(obs, y, pitch, gx_cell, cw):
    """The two characters printed after the octal group that starts at cell
    gx_cell, from Vision's tokens on the line; None if not read."""
    for oy, ox, t in obs:
        if abs(oy - y) >= 0.45 * pitch:
            continue
        u = R.printer_charset(t)
        for gx, g in R.groups(ox, u, cw):
            if abs(gx / cw - gx_cell) <= 1.5:
                m = re.search(re.escape(g[:6]) + r"\.?" + re.escape(g[7:]) + r"\s*(\S\S?)", u.translate(R.OCT_FIX))
                if m:
                    h = u[m.start(1):m.start(1) + 2].translate(HEX_FIX)
                    if re.fullmatch(r"[0-9A-F]{2}", h):
                        return h
        # a hex byte read as its own token
        if abs(ox / cw - (gx_cell + 10)) <= 1.0:
            h = R.printer_charset(t).strip().translate(HEX_FIX)
            if re.fullmatch(r"[0-9A-F]{2}", h):
                return h
    return None


def main(printed):
    vol, pdf = page_of(printed)
    rows = [r for r in csv.DictReader(open(os.path.join(ROOT, "docs", "vision", "listing_reading.tsv")),
                                      delimiter="\t", quoting=csv.QUOTE_NONE) if r["vol"] == str(vol) and r["pdf"] == str(pdf)]
    stem = os.path.join(ROOT, "docs", "vision", "all", "v%d_pdf%03d" % (vol, pdf))
    g = json.loads(open(stem + ".geom").read())
    vis = R.load(stem + ".vis.tsv") + R.load(stem + ".vcol.tsv")
    y0, pitch, _, _ = R.fit_lines(R.load(stem + ".vis.tsv"), g)
    cw = g["char_w"]
    C = statement_repair.corpus()
    syms = set().union(*(s for p, (s, _) in C.items() if p != printed))
    ops = set().union(*(o for p, (_, o) in C.items() if p != printed))
    print(f"printed p.{printed} = vol {vol} PDF p.{pdf}; {len(rows)} lines read")
    print(f"{'ln':>3} {'LOCATION':11s} {'BINARY h1':11s} hx  {'h2':11s} hx  NAME+STATEMENT (draft)")
    for r in rows:
        line = int(r["line"])
        y = y0 + (line - 1) * pitch
        f = lambda v, s: (MARK[s] + (v.split("|")[0] if v else "")).ljust(11)
        h1 = hex_after(vis, y, pitch, g["bin_cell"], cw) if r["binary_h1"] else None
        h2 = hex_after(vis, y, pitch, g["bin_cell"] + 14, cw) if r["binary_h2"] else None
        print(f"{line:3d} {f(r['location'], r['loc_status'])} {f(r['binary_h1'], r['bin_status'])} "
              f"{('h' + h1) if h1 else '   '} {f(r['binary_h2'], r['bin2_status'])} "
              f"{('h' + h2) if h2 else '   '} {r['name_statement_draft']}")
        lab, st = statement_repair.repair(r["statement_draft"], syms, ops, name=r["name_draft"])
        _, st2 = statement_repair.repair(r["statement_crop"], syms, ops, whole=True)
        if st2 and st2 != st:
            st += f"   | crop: {st2}"
        if st:
            print(f"{'':52s}-> {lab:8s} {st}")


if __name__ == "__main__":
    main(int(sys.argv[1]))
