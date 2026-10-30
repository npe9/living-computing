#!/usr/bin/env python3
"""Find an MCP listing page's COLUMN BOUNDARIES from the page itself.

>>> WHY THIS EXISTS. <<<  mcp_crop.sh carries the column geometry as
constants -- `loc) X=400 W=2400`, `code) X=2800 W=2000` -- calibrated by
hand against printed p.2 while transcribing it.  That works for pages
laid out like p.2 and silently lands on the WRONG COLUMN otherwise: on
2026-10-30 the `code` crop of printed p.83 returned the
data-description column ("BU,100,10"), because p.83 is a sparse
definitions page whose ink sits elsewhere.  The transcription stopped
there, on a geometry constant rather than on anything about the page.

So: measure the gutters instead of assuming them.  A listing page is
ink in columns separated by vertical whitespace, and a column-wise ink
profile finds the gutters without knowing anything about the page.

    python3 mcp_columns.py PRINTED_PAGE [DPI]

prints each detected column's x, width and ink mass, so a caller can
pick one by position, and emits a ready-to-run pdftoppm line for each.

WHAT IT DOES NOT DO: name the columns.  Naming needs the header row and
that is a separate reading; the x-ordering is LINE, LOCATION, BINARY
OUTPUT, NAME, STATEMENT on every page seen so far, but this tool
reports what it measures and lets the caller decide.
"""
import subprocess, sys, os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(HERE, "..", "docs", "MCP_Mar63_001-249.pdf")


def render(printed, dpi, out):
    page = printed + 7          # confirm against the page's own header
    subprocess.run(["pdftoppm", "-f", str(page), "-l", str(page),
                    "-r", str(dpi), "-png", PDF, out],
                   check=True, capture_output=True)
    for suffix in (f"-{page:03d}.png", f"-{page}.png"):
        if os.path.exists(out + suffix):
            return out + suffix
    raise SystemExit("pdftoppm wrote no file I can find")


def columns(path, min_gutter_frac=0.005, ink_floor=0.010):
    """Column runs of a page, as (x0, x1, ink_mass).

    min_gutter_frac: a gap must be this fraction of the page width to
    count as a gutter -- smaller gaps are the spaces between words.
    ink_floor: a pixel column with less ink than this fraction of its
    height is blank; it is not zero because scans carry speckle.

    BOTH DEFAULTS ARE MEASURED, NOT CHOSEN.  On printed p.83 at 300 dpi
    (5100 px wide) the per-x ink profile has median 0.018 and max 0.217,
    and the blank-run census is:

        floor 0.002  ->  3 runs of width >= 25   (page margins only)
        floor 0.005  ->  3 runs                  (page margins only)
        floor 0.010  ->  8 runs                  (the real gutters)

    and the gutters that appear at 0.010 are 38 to 108 px wide, so a
    minimum of 0.005 * width = 25 px admits them while still rejecting
    the inter-word spaces.  The first version of this function used
    0.002 and 0.012 -- both guesses -- and reported the whole page as
    ONE column, which is the same failure mcp_crop.sh has, arrived at
    from the other direction.
    """
    im = Image.open(path).convert("L")
    a = np.asarray(im, dtype=np.float32) / 255.0
    ink = (1.0 - a)                      # 1 = black

    # >>> DROP THE RULED ROWS FIRST. <<<  A listing page is covered in
    # dashed horizontal separators and a printed border, and those put
    # ink at EVERY x -- so a naive column profile finds one column
    # spanning the page, which is what the first version of this did.
    # A row that is inked across most of its width is a rule, not text.
    row_cover = (ink > 0.35).mean(axis=1)
    text_rows = row_cover < 0.20
    if text_rows.sum() < 10:             # nothing but rules; bail loudly
        raise SystemExit("no text rows found -- is this a blank page?")
    prof = ink[text_rows].mean(axis=0)   # per-x mean ink, rules excluded
    w = len(prof)
    inked = prof > ink_floor
    min_gutter = max(3, int(w * min_gutter_frac))

    runs, start = [], None
    gap = 0
    for x in range(w):
        if inked[x]:
            if start is None:
                start = x
            gap = 0
        else:
            if start is not None:
                gap += 1
                if gap >= min_gutter:
                    runs.append((start, x - gap))
                    start = None
                    gap = 0
    if start is not None:
        runs.append((start, w - 1))
    return [(x0, x1, float(prof[x0:x1 + 1].sum())) for x0, x1 in runs
            if x1 > x0]


def main():
    if len(sys.argv) < 2:
        raise SystemExit(f"usage: {sys.argv[0]} PRINTED_PAGE [DPI]")
    printed = int(sys.argv[1])
    dpi = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    out = f"/tmp/mcp_cols_p{printed}"
    path = render(printed, dpi, out)
    im = Image.open(path)
    cols = columns(path)
    print(f"printed p.{printed} = PDF p.{printed + 7}, {im.width}x{im.height} at {dpi} dpi")
    print(f"CONFIRM the page's own 'PAGE NUMBER' header reads {printed}.")
    print(f"{len(cols)} column runs:\n")
    print(f"  {'#':>2}  {'x0':>6} {'x1':>6} {'width':>6}  {'ink':>8}")
    for i, (x0, x1, mass) in enumerate(cols):
        print(f"  {i:>2}  {x0:>6} {x1:>6} {x1-x0:>6}  {mass:>8.1f}")
    print("\nto crop one, at the dpi you want (scale x,W by dpi/%d):" % dpi)
    for i, (x0, x1, _) in enumerate(cols):
        print(f"  # col {i}:  pdftoppm -f {printed+7} -l {printed+7} -r DPI -png "
              f"-x $(({x0}*DPI/{dpi})) -W $((({x1-x0})*DPI/{dpi})) ... ")


if __name__ == "__main__":
    main()
