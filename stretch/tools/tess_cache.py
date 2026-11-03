#!/usr/bin/env python3
"""Cache tesseract's reading of every MCP listing page that has a deck.

    python3 tools/tess_cache.py [PRINTED ...]

Writes docs/vision/mcp_pNNN.tes.tsv beside Vision's mcp_pNNN.tsv, in
the same format and the same frame (y, x normalised to the FULL page),
so tests/check_vision_cross_reading.py can ask whether the two ENGINES
agree.  Reader is tools/multi_read.py's tes_crop_300: the LINE..BINARY
crop at 300 dpi, whitelisted to 0-9 A-F . *.

WHY A SECOND ENGINE AND NOT A SECOND RESOLUTION: measured on 19 pages
(tools/README_vision.md), Vision repeats 50-75% of its own errors
across resolutions; tesseract shared one error with it in the sample.
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import multi_read          # noqa: E402
import vision_cache        # noqa: E402


def cache(printed):
    with tempfile.TemporaryDirectory() as td:
        png, fr = multi_read.render(printed, 300, td, True)
        rows = sorted(multi_read.run_tesseract(png, fr))
    path = os.path.join(vision_cache.OUT, "mcp_p%03d.tes.tsv" % printed)
    with open(path, "w") as f:
        for y, x, c, t in rows:
            f.write(f"{y:.4f}\t{x:.4f}\t{c:.3f}\t{t}\n")
    return path, len(rows)


if __name__ == "__main__":
    pages = [int(a) for a in sys.argv[1:]] or vision_cache.deck_pages()
    for p in pages:
        path, n = cache(p)
        print(f"p.{p}: {n} observations -> {os.path.relpath(path, vision_cache.ROOT)}", flush=True)
