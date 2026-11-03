#!/usr/bin/env python3
"""Cache macOS Vision's reading of every MCP listing page that has a deck.

    python3 tools/vision_cache.py [PRINTED ...]

Writes docs/vision/mcp_pNNN.tsv -- one row per Vision text observation,
"y<TAB>x<TAB>confidence<TAB>text", y from the top, coordinates
normalised to the page.  The suite reads the CACHE, never Vision, so
tests/check_vision_cross_reading.py runs anywhere and runs fast; this
script is the only thing that needs a Mac.

Rendering is 300 dpi greyscale of PDF page = printed + 7.  That offset
is NOT trusted: each page's own "PAGE NUMBER" header is read back by
the check, so a wrong offset fails loudly instead of comparing a deck
against its neighbour's page.

Vision is run with usesLanguageCorrection OFF (tools/vision_ocr.swift).
Regenerate after an OS upgrade and diff: the reading is a function of
the recogniser version, and a changed cache is a changed witness.
"""
import os, subprocess, sys, glob, re, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PDF = os.path.join(ROOT, "docs", "MCP_Mar63_001-249.pdf")
OUT = os.path.join(ROOT, "docs", "vision")
OFFSET = 7


def binary():
    b = os.path.join(os.environ.get("TMPDIR", "/var/tmp"), "stretch-vision", "vision_ocr")
    if not os.path.exists(b):
        os.makedirs(os.path.dirname(b), exist_ok=True)
        subprocess.run(["swiftc", "-O", "-o", b,
                        os.path.join(HERE, "vision_ocr.swift")], check=True)
    return b


def deck_pages():
    out = []
    for p in glob.glob(os.path.join(ROOT, "decks", "mcp_bootstrap_p*.strap")):
        out.append(int(re.search(r"_p(\d+)\.strap$", p).group(1)))
    return sorted(out)


def cache(printed, ocr):
    os.makedirs(OUT, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        base = os.path.join(td, "pg")
        subprocess.run(["pdftoppm", "-f", str(printed + OFFSET), "-l",
                        str(printed + OFFSET), "-r", "300", "-gray", "-png",
                        PDF, base], check=True)
        png = glob.glob(base + "*.png")[0]
        r = subprocess.run([ocr, png], capture_output=True, text=True, check=True)
    path = os.path.join(OUT, "mcp_p%03d.tsv" % printed)
    with open(path, "w") as f:
        f.write(r.stdout)
    return path, r.stdout.count("\n")


if __name__ == "__main__":
    ocr = binary()
    pages = [int(a) for a in sys.argv[1:]] or deck_pages()
    for p in pages:
        path, n = cache(p, ocr)
        print(f"p.{p}: {n} observations -> {os.path.relpath(path, ROOT)}", flush=True)
