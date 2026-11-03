#!/usr/bin/env python3
"""Several INDEPENDENT readings of one MCP listing page, in one frame.

    python3 tools/multi_read.py OUTDIR PRINTED [PRINTED ...]

writes OUTDIR/pNNN/<reader>.tsv, each line "y<TAB>x<TAB>conf<TAB>text"
with y and x NORMALISED TO THE FULL PAGE, so rows from different
readers line up by y alone.

READERS.  Two engines, several resolutions, two framings:

    vis_full_200 / _300 / _400   macOS Vision, whole page
    vis_crop_300 / _600          macOS Vision, LINE..BINARY column crop
    tes_crop_300 / _600          tesseract --psm 6, same crop, whitelisted
                                 to 0-9 A-F . * so it cannot emit O or I

The point is INDEPENDENCE.  Vision's measured errors are systematic --
7 read as 1, 0 read as 6 -- and a reader cannot catch its own
systematic error.  Tesseract is a different engine with different
failure modes, and resolution changes how a worn glyph renders.  Only
measurement says whether those errors are independent enough for a
vote to cancel them; tools/README_vision.md records what it said.

usesLanguageCorrection stays OFF (tools/vision_ocr.swift).
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PDF = os.path.join(ROOT, "docs", "MCP_Mar63_001-249.pdf")
OFFSET = 7
CROP_X0, CROP_X1 = 0.165, 0.40      # LINE, LOCATION, BINARY half 1, hex byte

READERS = ["vis_full_200", "vis_full_300", "vis_full_400",
           "vis_crop_300", "vis_crop_600", "tes_crop_300", "tes_crop_600"]


def vision_bin():
    b = os.path.join(os.environ.get("TMPDIR", "/var/tmp"), "stretch-vision", "vision_ocr")
    if not os.path.exists(b):
        os.makedirs(os.path.dirname(b), exist_ok=True)
        subprocess.run(["swiftc", "-O", "-o", b,
                        os.path.join(HERE, "vision_ocr.swift")], check=True)
    return b


def render(printed, dpi, td, crop):
    from PIL import Image
    base = os.path.join(td, f"r{dpi}")
    png = base + ".png"
    if not os.path.exists(png):
        subprocess.run(["pdftoppm", "-f", str(printed + OFFSET), "-l",
                        str(printed + OFFSET), "-r", str(dpi), "-gray", "-png",
                        "-singlefile", PDF, base], check=True)
    if not crop:
        return png, (0.0, 1.0)
    out = base + "_crop.png"
    if not os.path.exists(out):
        im = Image.open(png)
        w, h = im.size
        im.crop((int(CROP_X0 * w), 0, int(CROP_X1 * w), h)).save(out)
    return out, (CROP_X0, CROP_X1 - CROP_X0)


def run_vision(png, frame, ocr):
    x0, xw = frame
    out = subprocess.run([ocr, png], capture_output=True, text=True, check=True).stdout
    rows = []
    for ln in out.splitlines():
        p = ln.split("\t")
        if len(p) >= 4:
            rows.append((float(p[0]), x0 + float(p[1]) * xw, float(p[2]), p[3]))
    return rows


def run_tesseract(png, frame):
    from PIL import Image
    x0, xw = frame
    w, h = Image.open(png).size
    out = subprocess.run(
        ["tesseract", png, "-", "--psm", "6",
         "-c", "tessedit_char_whitelist=0123456789ABCDEF.*", "tsv"],
        capture_output=True, text=True).stdout
    rows = []
    for ln in out.splitlines()[1:]:
        p = ln.split("\t")
        if len(p) < 12 or not p[11].strip():
            continue
        left, top, conf = int(p[6]), int(p[7]), float(p[10])
        rows.append((top / h, x0 + (left / w) * xw, conf / 100.0, p[11]))
    return rows


def read_page(printed, outdir, ocr):
    d = os.path.join(outdir, "p%03d" % printed)
    os.makedirs(d, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        for r in READERS:
            eng, frame, dpi = r.split("_")
            png, fr = render(printed, int(dpi), td, frame == "crop")
            rows = run_vision(png, fr, ocr) if eng == "vis" else run_tesseract(png, fr)
            rows.sort()
            with open(os.path.join(d, r + ".tsv"), "w") as f:
                for y, x, c, t in rows:
                    f.write(f"{y:.4f}\t{x:.4f}\t{c:.3f}\t{t}\n")


if __name__ == "__main__":
    outdir = sys.argv[1]
    ocr = vision_bin()
    for p in sys.argv[2:]:
        read_page(int(p), outdir, ocr)
        print(f"p.{p} read by {len(READERS)} readers", flush=True)
