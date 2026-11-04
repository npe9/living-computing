#!/usr/bin/env python3
"""Read the 7030 programming-environment manuals with macOS Vision.

    python3 tools/read_manuals.py STEM[:FIRST-LAST] ...   # read pages
    python3 tools/read_manuals.py --text STEM ...         # rebuild .txt only
    python3 tools/read_manuals.py --list                  # the manual set

For docs/STEM.pdf writes docs/vision/manuals/STEM/pNNN.tsv (PDF page,
"y x conf text w h", normalised, from tools/vision_ocr.swift --boxes)
and docs/vision/manuals/STEM.txt, the pages in READING ORDER with a
"==== PDF page N ====" line before each.

READING ORDER.  These manuals set prose in two columns between
full-width headings and tables (C22-6729 p.10 has both on one page),
and sorting by y alone interleaves the columns line by line.  A page is
cut into horizontal BANDS at every line that crosses the gutter; within
a band the left column is read before the right.  The .tsv keeps every
box, so a better ordering can be rebuilt with --text without re-reading.

usesLanguageCorrection stays OFF, as for the listing: these pages are
full of mnemonics, bit ranges and octal, which correction "fixes" into
words.  The reading is a TEXT LAYER for search and citation; a quotation
that a rule depends on is still checked against the page image.
"""
import glob
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import multi_read     # noqa: E402

OUT = os.path.join(ROOT, "docs", "vision", "manuals")
MANUALS = [
    "C22-6728_7030_MCP_Sys_Analysis_Guide",
    "C22-6728-1_7030_MCP_Sys_Analysis_Guide",
    "C22-6729_7030_STRAP_II_Sys_Analysis_Guide",
    "C28-6129_STRAP-II_with_update_Apr63",
    "C22-6678-1_7030_MCP_Reference_Jun64",
    "C28-6379-0_MCP_Loader",
    "C22-6751_7030_FORTRAN_IV_May63",
    "J22-6559_MCP_UsersGuide_Dec60",
    "N22-0085_MCP_RefMan_Upd_May63",
    "X28-6131_MCP_PocketCard",
    "22-6530-2_7030RefMan",
]
GUTTER = (0.47, 0.53)


def n_pages(pdf):
    out = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    return int(next(l.split()[1] for l in out.splitlines() if l.startswith("Pages:")))


def read_page(stem, page, ocr):
    pdf = os.path.join(ROOT, "docs", stem + ".pdf")
    d = os.path.join(OUT, stem)
    os.makedirs(d, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        base = os.path.join(td, "pg")
        subprocess.run(["pdftoppm", "-f", str(page), "-l", str(page), "-r", "300",
                        "-gray", "-png", "-singlefile", pdf, base], check=True)
        out = subprocess.run([ocr, base + ".png", "--boxes"], capture_output=True,
                             text=True, check=True).stdout
    open(os.path.join(d, "p%03d.tsv" % page), "w").write(out)


def boxes(path):
    out = []
    for ln in open(path):
        p = ln.rstrip("\n").split("\t")
        if len(p) >= 6:
            out.append((float(p[0]), float(p[1]), p[3], float(p[4]), float(p[5])))
    return out


def lines_of(bs):
    """Group boxes into printed lines by y overlap; each line left to right."""
    out = []
    for b in sorted(bs):
        y, x, t, w, h = b
        if out and abs(out[-1][0][0] - y) < 0.5 * max(h, out[-1][0][4]):
            out[-1].append(b)
        else:
            out.append([b])
    return [sorted(l, key=lambda b: b[1]) for l in out]


def order(bs):
    """Reading-order text of one page (see the docstring)."""
    spans = lambda b: b[1] < GUTTER[0] and b[1] + b[3] > GUTTER[1]
    right = [b for b in bs if b[1] >= GUTTER[0]]
    left = [b for b in bs if b[1] + b[3] <= GUTTER[1]]
    two_col = len(right) >= 5 and len(left) >= 5
    if not two_col:
        return [" ".join(b[2] for b in l) for l in lines_of(bs)]
    cuts = sorted(b[0] for b in bs if spans(b))
    text, lo = [], -1.0
    for cut in cuts + [2.0]:
        band = [b for b in bs if lo < b[0] < cut and not spans(b)]
        for col in ([b for b in band if b[1] < GUTTER[0]], [b for b in band if b[1] >= GUTTER[0]]):
            text += [" ".join(b[2] for b in l) for l in lines_of(col)]
        if cut < 2.0:
            text += [" ".join(b[2] for b in l) for l in lines_of([b for b in bs if b[0] == cut and spans(b)])]
        lo = cut
    return text


def write_text(stem):
    pages = sorted(glob.glob(os.path.join(OUT, stem, "p*.tsv")))
    with open(os.path.join(OUT, stem + ".txt"), "w") as f:
        for p in pages:
            f.write("==== PDF page %d ====\n" % int(os.path.basename(p)[1:4]))
            f.write("\n".join(order(boxes(p))) + "\n")
    return len(pages)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--list"]:
        for m in MANUALS:
            print(m, n_pages(os.path.join(ROOT, "docs", m + ".pdf")))
        sys.exit(0)
    if a and a[0] == "--text":
        for stem in a[1:] or MANUALS:
            print(stem, write_text(stem), "pages")
        sys.exit(0)
    ocr = multi_read.vision_bin()
    for spec in a:
        stem, _, rng = spec.partition(":")
        n = n_pages(os.path.join(ROOT, "docs", stem + ".pdf"))
        lo, hi = map(int, rng.split("-")) if rng else (1, n)
        for page in range(lo, hi + 1):
            read_page(stem, page, ocr)
        print(f"{stem}: PDF pp.{lo}-{hi} read", flush=True)
