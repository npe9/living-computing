#!/usr/bin/env python3
"""The MCP listing's PRINTING GRID, fitted per page, with SKEW.

>>> WHAT THIS REPLACES. <<<  The first version of this file carried
`phase()`, which picked the grid offset putting least ink on the cell
seams, and recorded that it was UNSTABLE: over x=700..4900 it returned
3 and over x=200..1800 it returned 20, two thirds of a cell apart.
The diagnosis in that file ("use a fixed phase confirmed by eye") was
wrong about the cause.

**The phase was never unstable.  It is a FUNCTION OF y, because the
pages are SKEWED.**  Fitting the phase in separate y bands shows a
clean trend: printed p.193 drifts -5.25 px per 1000 px of y, which is
-0.301 degrees and nearly HALF A CELL across the text block.  The
model was missing a parameter, so every estimate of the missing
parameter disagreed with every other.

THE MODEL.  A character cell's left edge is

    x(k, y) = phase0 + skew * y + k * cpitch

fitted per page by maximising the circular concentration of glyph
midpoints over (cpitch, skew) jointly.

MEASURED, eight pages (printed 95, 139, 172, 186, 190, 192, 193, 196):

    cpitch   30.055 .. 30.060 px at 300 dpi   -> 9.982 CPI
    skew     -0.115 .. -0.286 degrees, always NEGATIVE
    phase0   varies per page; it is scan registration

Note the pitch is 9.982 CPI and NOT the nominal 10.00.  An earlier
commit here claimed "10.00 CPI x 6.00 LPI exactly" from a
single-page autocorrelation; that was precise to about 0.2%, and 0.2%
of 143 cells is a quarter of a cell by the right margin.  The row
pitch is likewise 49.81..50.36 px (5.96..6.02 LPI) and must be fitted
per page -- printed p.172 is the outlier at 50.36.

>>> THE VALIDATOR IS INDEPENDENT OF THE FITTING OBJECTIVE. <<<  The
fraction of ink within +-1 px of a seam, compared against the SAME
page with the grid shifted half a cell.  A ratio well above 1 means
the seams really do land in the gutters.  Boldness cancels because
both numbers use the same ink -- it must be a RATIO: an absolute
threshold called printed p.186 a failure at 9.01% when an overlay
showed its grid correctly aligned, because that page simply prints
heavier.  With skew fitted:

    seam ink    1.38% .. 1.93%     (was 2.05% .. 9.01%)
    ratio       7.65 .. 10.58      (was 1.29 .. 7.23)

on all eight pages.

>>> WHAT IS NOT MEASURED. <<<  ROW skew.  A pure page rotation would
make the row grid's dy/dx equal and opposite to the character grid's
dx/dy, and that cross-check DOES NOT CONFIRM: fitted from per-glyph
ink centroids the row skew comes out ~0 on four pages and +0.401 deg
on printed p.196, against its character skew of -0.115.  The row
signal is too weak for the method -- a glyph's vertical centroid
depends strongly on which glyph it is (a period sits low, an
apostrophe high) and that variation swamps 0.2 degrees.  So: use the
fitted row PITCH, and do not trust a row skew from this file.

Nothing here classifies a glyph.  This is the half that cuts the page
into cells; off-the-shelf OCR reads this drum at 43% (docs/NEXT.md)
and that remains the number a trained reader has to beat.
"""
import numpy as np

DPI = 300


def _runs(v):
    out = []; s = None
    for i, x in enumerate(v):
        if x and s is None: s = i
        elif not x and s is not None: out.append((s, i)); s = None
    if s is not None: out.append((s, len(v)))
    return out


def glyph_midpoints(ink, x0=200, x1=5000, y0=150, y1=2700):
    """(x_mid, y_of_row) for isolated ink blobs.

    Row bands outside 12..70 px are dropped: that removes the DASHED
    RULES (6-9 px) and the runs where two text lines merged (90..449
    px).  Blobs wider than 32 px are dropped as touching pairs.
    """
    sub = ink[y0:y1, x0:x1]; pts = []
    for (a, b) in _runs(sub.sum(axis=1) > 2):
        if not (12 <= b - a <= 70):
            continue
        cp = sub[a:b].sum(axis=0); ym = (a + b) / 2.0 + y0
        for (c, d) in _runs(cp > 0):
            if 4 <= d - c <= 32:
                pts.append(((c + d) / 2.0 + x0, ym))
    return np.array(pts)


def fit(ink, x0=200, x1=5000, y0=150, y1=2700):
    """Fit (cpitch, phase0, skew) for one page.  None if too little ink."""
    pts = glyph_midpoints(ink, x0, x1, y0, y1)
    if len(pts) < 200:
        return None
    xs, ys = pts[:, 0], pts[:, 1]
    best = None
    for p in np.arange(29.8, 30.4, 0.005):
        for sk in np.arange(-0.010, 0.0101, 0.001):
            th = 2 * np.pi * ((xs - sk * ys) % p) / p
            R = float(np.hypot(np.cos(th).mean(), np.sin(th).mean()))
            if best is None or R > best[0]:
                best = (R, p, sk)
    R, p, sk = best
    th = 2 * np.pi * ((xs - sk * ys) % p) / p
    ang = np.arctan2(np.sin(th).mean(), np.cos(th).mean()) % (2 * np.pi)
    return dict(cpitch=p, skew=sk, R=R, n=len(pts),
                phase0=(ang * p / (2 * np.pi) - p / 2.0) % p)


def cell_x(g, k, y):
    """Left edge of character cell k on the scan line y."""
    return g['phase0'] + g['skew'] * y + k * g['cpitch']


def seam_fraction(ink, g, x0=200, x1=5000, y0=150, y1=2700, shift=0.0, hw=1):
    """Ink within +-hw px of a cell seam, under the skewed grid."""
    p, ph, sk = g['cpitch'], g['phase0'] + shift, g['skew']
    tot = ink[y0:y1, x0:x1].sum()
    if not tot:
        return None
    seam = 0
    for y in range(y0, y1):
        row = ink[y]; base = ph + sk * y
        k = int(np.ceil((x0 - base) / p))
        while True:
            x = int(round(base + k * p))
            if x >= x1: break
            if x >= x0: seam += row[max(x0, x - hw):x + hw + 1].sum()
            k += 1
    return seam / tot


def quality(ink, g, **kw):
    """(seam_fraction, ratio_against_half_cell_shift).  Ratio >> 1 is good;
    the RATIO is the measure, not the fraction -- see the docstring."""
    f = seam_fraction(ink, g, shift=0.0, **kw)
    c = seam_fraction(ink, g, shift=g['cpitch'] / 2.0, **kw)
    return f, (c / f if f else 0.0)
