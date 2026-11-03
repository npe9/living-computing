#!/usr/bin/env python3
"""A TRAINED SECOND READING of the listing's NUMERIC columns.

Builds on strap/listing_grid.py, which fits the per-page skewed cell
grid.  This file cuts cells out of that grid, labels them from what
the decks already know, and classifies them by nearest template.

>>> THE COLUMN LAYOUT IS FIXED IN CELL COORDINATES. <<<  Measured by
locating the periods: they peak at k=40, 55 and 69 on every page
tried (printed 139, 192, 193, 196) with no exceptions.

    k 34..42   LOCATION        "oooooo.oo", period at k=40
    k 49..57   BINARY half 1   period at k=55
    k 58       SPACE           mean ink 2 -- it really is empty
    k 59..60   HEX BYTE        mean ink 237 / 242
    k 63..71   BINARY half 2   period at k=69

Verified across eight pages before any cell was harvested, because an
off-by-one in k silently mislabels every sample.

>>> HOW ROWS ARE PAIRED TO LABELS, AND WHY NOT ORDINALLY. <<<  The
first attempt zipped detected rows to the deck's located lines in
order.  That is WRONG whenever the two counts disagree, and it
disagreed on all but 4 of 47 pages.  Worse, it fails SILENTLY: the
contaminated labels scored 95.1% and the error structure gave it
away -- cell positions 0 and 1 were 100% correct (the "221" prefix is
near-constant down a page, so a mispairing still lands the right
label) while position 7 was 17.3% wrong, almost all of it symmetric
0<->4, which is exactly ".00" against ".40".

The fix is to BOOTSTRAP: read the location with the digit classifier
and keep a row only when the 9 characters read are EXACTLY a location
the deck lists.  That pairs 46 pages instead of 4 and cannot pair a
row to the wrong line.

>>> RESULTS, leave-one-PAGE-out, 1-NN. <<<

LOCATION column, 9 classes (octal digits and the period), scored
WITHOUT using any row->line mapping -- read each row and ask whether
the string read is one the deck lists:

    characters correct     98.0%       (tesseract baseline: 43%)
    whole 9-char strings   82.0%

HEX BYTE, 16 classes, 2,642 cells over 46 pages:

    overall                89.3%
    0   93.1%      8   90.4%
    C   78.7%      B   78.1%      D   82.2%

>>> THE NEGATIVE RESULT, AND IT IS THE IMPORTANT ONE. <<<  **Nearest
template does NOT solve C against 0.**  C->0 is 20 and 0->C is 19,
the single largest confusion after 0<->8.  Two normalisers were
tried and they make no difference: cropping each glyph to its ink
bounding box gives 88.8% and C=76.9%; keeping the whole cell frame,
so that extent and position survive, gives 89.3% and C=78.7%.  The
hypothesis that bbox-cropping was destroying the width difference
between a narrow C and a round 0 is therefore REJECTED.

This agrees with docs/transcription_workflow.md's existing measured
negative on O/0/C, and it is a much stronger test of it: that one was
two hand-picked features on n=6 per class, this is 2,642 labelled
cells and the whole bitmap.  **The glyph ladder is not retired by a
trained reader.**  A round glyph still has to be settled by the
corpus, by a manual, or by the assembler.

>>> WHAT IT IS GOOD FOR, WHICH IS NOT NOTHING. <<<  An INDEPENDENT
second reading of the LOCATION and BINARY columns -- independent of
the volume OCR, which is the point.  Ten rows of `C`-for-`0` reached
the corpus because listing blocks were pasted from that OCR (see
NEXT.md), and the check that should have caught them was comparing 8
of 12 characters.  At 98% on locations this reader disagrees loudly
enough to flag those rows for a human, and it has never seen the OCR.
It is a FLAGGER, not a transcriber: rule 3 is unchanged.
"""
import numpy as np

CELL_H, CELL_W = 24, 20
LOC_K0, LOC_N, LOC_DOT_K = 34, 9, 40
HEX_K = (59, 60)


def norm_bbox(c):
    """Crop to ink, resize, L2-normalise.  88.8% on hex."""
    if c.size == 0 or c.sum() == 0:
        return np.zeros(CELL_H * CELL_W)
    from PIL import Image
    ys, xs = np.nonzero(c)
    sub = c[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    im = Image.fromarray((sub.astype(np.uint8)) * 255).resize((CELL_W, CELL_H))
    v = np.asarray(im, dtype=float).ravel() / 255.0
    n = np.linalg.norm(v)
    return v / n if n else v


def norm_frame(c):
    """Keep the cell frame, resize, L2-normalise.  89.3% on hex."""
    if c.size == 0 or c.sum() == 0:
        return np.zeros(CELL_H * CELL_W)
    from PIL import Image
    im = Image.fromarray((c.astype(np.uint8)) * 255).resize((CELL_W, CELL_H))
    v = np.asarray(im, dtype=float).ravel() / 255.0
    n = np.linalg.norm(v)
    return v / n if n else v


def is_period(c):
    """A period: a small blob low in the cell.

    The ink bounds matter and the first version had them wrong -- it
    capped ink at 70 when a period on this drum carries about 107, so
    it found 6 periods on a page with 43 and the column anchor was
    lost.  Widened after printing a cell as ASCII art and counting.
    """
    if c.size == 0:
        return False
    t = c.sum()
    if not (30 <= t <= 220):
        return False
    ys, _ = np.nonzero(c)
    if len(ys) == 0:
        return False
    h = c.shape[0]
    return ys.mean() > 0.58 * h and (ys.max() - ys.min()) <= 0.45 * h


def classify(vectors, train_vecs, train_labels):
    """1-NN by cosine similarity (vectors are L2-normalised)."""
    X = np.asarray(vectors); T = np.asarray(train_vecs)
    return [train_labels[k] for k in (X @ T.T).argmax(axis=1)]
