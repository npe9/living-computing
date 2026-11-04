#!/usr/bin/env python3
"""Read EVERY page of both MCP listing volumes with two engines.

    python3 tools/read_every_page.py VOL:PDF [VOL:PDF ...]
    python3 tools/read_every_page.py all        # prints the VOL:PDF list

For each PDF page writes, under docs/vision/all/:

    v1_pdf010.vis.tsv   macOS Vision, whole page, 300 dpi
    v1_pdf010.tes.tsv   tesseract on THIS page's LOCATION column and its
                        BINARY half word 1 and 2 columns, each cropped
                        alone, 600 dpi
    v1_pdf010.vcol.tsv  macOS Vision again, on the same two column crops,
                        300 dpi -- the SAME engine, so it never counts as a
                        second witness; it raises Vision's coverage (vol 2
                        PDF p.34: 45 location groups against 26 whole-page)
    v1_pdf010.geom      the measured column frame, or "none"

    python3 tools/read_every_page.py --vcol VOL:PDF ...   adds only .vcol.tsv
    python3 tools/read_every_page.py --crops VOL:PDF ...  re-reads the crops

Keyed by PDF page, NOT printed page: the offset between them is not
constant in either volume, and the printed number is read back off each
page's own header (strap/listing_read.py page_number) instead of assumed.

WHY THIS CONFIGURATION.  Measured on 19 pages with truth
(tools/README_vision.md): one column per tesseract crop, cut where the
page's own geometry puts it, raised tesseract's coverage from 57% to 83%
of locations and from 20% to 70% of binary half words.  The crops are
placed from Vision's reading of the same page because the two volumes
are scanned in different frames (vol 1 5100 px wide, LOCATION at x
~0.20; vol 2 4499 px, at ~0.094).

usesLanguageCorrection stays OFF (tools/vision_ocr.swift).
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "strap"))
import multi_read             # noqa: E402
import listing_read as R      # noqa: E402

PDFS = {1: os.path.join(ROOT, "docs", "MCP_Mar63_001-249.pdf"),
        2: os.path.join(ROOT, "docs", "MCP_Mar63_250-445.pdf")}
OUT = os.path.join(ROOT, "docs", "vision", "all")


def n_pages(vol):
    out = subprocess.run(["pdfinfo", PDFS[vol]], capture_output=True, text=True).stdout
    return int(next(l.split()[1] for l in out.splitlines() if l.startswith("Pages:")))


def render(vol, pdf, dpi, td):
    from PIL import Image
    base = os.path.join(td, "r%d" % dpi)
    subprocess.run(["pdftoppm", "-f", str(pdf), "-l", str(pdf), "-r", str(dpi),
                    "-gray", "-png", "-singlefile", PDFS[vol], base], check=True)
    png = base + ".png"
    return png, Image.open(png).size


def crops(vol, pdf, g, dpi, td):
    """[(png, frame)] for this page's LOCATION, BINARY h1 and h2 columns."""
    from PIL import Image
    png, _ = render(vol, pdf, dpi, td)
    im = Image.open(png)
    W, H = im.size
    cw = g["char_w"]
    out = []
    for cell in (g["loc_cell"], g["bin_cell"], g["bin_cell"] + 14):
        x0, x1 = (cell - 1.0) * cw, (cell + 10.5) * cw
        crop = os.path.join(td, "c%d_%d.png" % (dpi, cell))
        im.crop((int(x0 * W), 0, int(x1 * W), H)).save(crop)
        out.append((crop, (x0, x1 - x0)))
    return out


def write_rows(path, rows):
    with open(path, "w") as f:
        for y, x, c, t in sorted(rows):
            f.write(f"{y:.4f}\t{x:.4f}\t{c:.3f}\t{t}\n")


def read_vcol(vol, pdf, ocr):
    stem = os.path.join(OUT, "v%d_pdf%03d" % (vol, pdf))
    gl = open(stem + ".geom").read().strip()
    rows = []
    if gl != "none":
        with tempfile.TemporaryDirectory() as td:
            for png, fr in crops(vol, pdf, json.loads(gl), 300, td):
                rows += [r for r in multi_read.run_vision(png, fr, ocr)]
    write_rows(stem + ".vcol.tsv", rows)
    return gl != "none"


def read_crops(vol, pdf, ocr):
    """Re-read only the column crops (tesseract and Vision) from the stored
    frame; the whole-page Vision reading is kept."""
    stem = os.path.join(OUT, "v%d_pdf%03d" % (vol, pdf))
    gl = open(stem + ".geom").read().strip()
    rows, vrows = [], []
    if gl != "none":
        g = json.loads(gl)
        with tempfile.TemporaryDirectory() as td:
            for png, fr in crops(vol, pdf, g, 600, td):
                rows += multi_read.run_tesseract(png, fr)
            for png, fr in crops(vol, pdf, g, 300, td):
                vrows += multi_read.run_vision(png, fr, ocr)
    write_rows(stem + ".tes.tsv", rows)
    write_rows(stem + ".vcol.tsv", vrows)
    return gl != "none"


def read(vol, pdf, ocr):
    os.makedirs(OUT, exist_ok=True)
    stem = os.path.join(OUT, "v%d_pdf%03d" % (vol, pdf))
    with tempfile.TemporaryDirectory() as td:
        png, (w, h) = render(vol, pdf, 300, td)
        vis = multi_read.run_vision(png, (0.0, 1.0), ocr)
        vis.sort()
        with open(stem + ".vis.tsv", "w") as f:
            for y, x, c, t in vis:
                f.write(f"{y:.4f}\t{x:.4f}\t{c:.3f}\t{t}\n")
        g = R.geometry([(y, x, t) for y, x, _, t in vis], w, h)
        with open(stem + ".geom", "w") as f:
            f.write(json.dumps(dict(g, w_px=w, h_px=h)) + "\n" if g else "none\n")
        rows, vrows = [], []
        if g:
            for png, fr in crops(vol, pdf, g, 600, td):
                rows += multi_read.run_tesseract(png, fr)
            for png, fr in crops(vol, pdf, g, 300, td):
                vrows += multi_read.run_vision(png, fr, ocr)
        write_rows(stem + ".tes.tsv", rows)
        write_rows(stem + ".vcol.tsv", vrows)
    return bool(g)


if __name__ == "__main__":
    if sys.argv[1:] == ["all"]:
        for vol in (1, 2):
            for p in range(1, n_pages(vol) + 1):
                print(f"{vol}:{p}")
        sys.exit(0)
    ocr = multi_read.vision_bin()
    args, fn = sys.argv[1:], read
    if args and args[0] == "--vcol":
        args, fn = args[1:], read_vcol
    if args and args[0] == "--crops":
        args, fn = args[1:], read_crops
    for a in args:
        vol, pdf = map(int, a.split(":"))
        ok = fn(vol, pdf, ocr)
        print(f"v{vol} PDF p.{pdf}: {'listing frame found' if ok else 'NO listing frame'}", flush=True)
