#!/usr/bin/env python3
"""The MCP listing's PRINTING GRID, measured rather than assumed.

>>> THE PAGE IS A DETERMINISTIC 2-D GRID. <<<  Measured 2026-11-02 by
autocorrelating the ink profile of printed p.192 rendered at 300 dpi:

    character pitch   30 px at 300 dpi  =  10.00 characters per inch
    line pitch        50 px at 300 dpi  =   6.00 lines per inch

Both peaks are unambiguous (r=0.684 at lag 30 against 0.675 at 31;
r=0.468 at lag 50 against 0.423 at 49), and both land on the standard
line-printer values exactly.  So a character cell is addressable as

    x = xphase + k * 30        y = yphase + n * 50

and NOTHING about glyph shape needs to be known to cut the page into
cells.  An overlay of this grid on p.192 puts every character in its
own cell with the rules falling in the gutters.

WHY THIS MATTERS.  docs/NEXT.md records that off-the-shelf OCR reads
this drum at 43% on the symbol pages, and that its errors are all the
project's own glyph ladder -- C/D/0/O and 1/I/L.  A per-character
classifier trained on the corpus is the obvious answer, and a
classifier needs cells.  This file is that half, and it is the half
that is now measured.

>>> WHAT IS NOT DONE, AND THE TRAP IN IT. <<<  `phase()` below is NOT
RELIABLE.  It picks the offset putting least ink on the cell seams,
and that objective is unstable in the x range it is given: over
x=700..4900 it returns 3, over x=200..1800 it returns 20.  Phase is
mod 30, so those two disagree by two thirds of a cell and one of them
slices every glyph in half.  A caller that trusts it silently
harvests garbage.  USE A FIXED PHASE CONFIRMED BY EYE against an
overlay until this is replaced with an objective that is stable --
aligning to detected glyph bounding boxes, or maximising between-cell
ink variance, are the two candidates, neither tried.

ROW SEGMENTATION BY INK DOES NOT WORK EITHER, and the grid is why it
does not have to.  On p.192 an ink-run segmenter finds 51 runs for 51
printed lines, which looks like a result and is a coincidence: the
runs include the DASHED RULES (6-9 px tall) and merge adjacent text
lines (runs of 90, 100, 110, 289 and 449 px).  Filtering to >=20 px
leaves 43 runs for 51 lines.  Step the line pitch instead.
"""
import numpy as np

DPI = 300
CHAR_PITCH = DPI / 10.0        # 10.00 CPI, autocorrelated
LINE_PITCH = DPI / 6.0         # 6.00 LPI, autocorrelated


def autocorr_pitch(profile, lo, hi):
    """Dominant period of an ink profile, in pixels, searched in [lo,hi)."""
    p = np.asarray(profile, dtype=float)
    p = p - p.mean()
    ac = np.correlate(p, p, mode='full')[len(p) - 1:]
    ac /= ac[0]
    return max(range(lo, hi), key=lambda L: ac[L]), ac


def cell(ink, yphase, xphase, n, k):
    """The (n,k)th character cell as a boolean bitmap."""
    a = int(round(yphase + n * LINE_PITCH)); b = int(round(a + LINE_PITCH))
    c = int(round(xphase + k * CHAR_PITCH)); d = int(round(c + CHAR_PITCH))
    return ink[a:b, c:d]


def phase(ink, x0, x1):
    """UNSTABLE -- see the module docstring. Kept so the next reader can
    reproduce the instability rather than rediscover it."""
    prof = ink[:, x0:x1].sum(axis=0)
    return min(range(int(CHAR_PITCH)),
               key=lambda ph: prof[ph::int(CHAR_PITCH)].sum())
