#!/usr/bin/env python3
"""Read the numeric columns of an MCP listing page out of an OCR reading.

Shared by tools/score_readers.py and tests/check_vision_cross_reading.py,
so the scorer and the suite pair rows the same way.

An OCR reading is a list of (y, x, text), y and x normalised to the full
page (docs/vision/mcp_pNNN.tsv for Vision, .tes.tsv for tesseract).

ROW PAIRING.  The line number is read off the LINE column and FITTED,
y = y0 + (line - 1) * pitch, with a median fit, so one misread line
number cannot mispair a row; a field is then sampled at its line's y.

ALPHABET CONSTRAINT: octal has no letters, so C O Q D -> 0 and I l | -> 1;
anything else is UNREAD.  In a token with no period, a run of exactly
eight octal digits is a group whose period was not read; the period goes
after the sixth, where the printing grid puts it.
"""
import re
import statistics

LINE_X = (0.165, 0.199)
LOC_X = (0.190, 0.222)
BIN_X = (0.278, 0.310)
OCT_FIX = str.maketrans({"C": "0", "O": "0", "Q": "0", "D": "0", "c": "0",
                         "o": "0", "I": "1", "l": "1", "|": "1", ",": "."})
OCT = re.compile(r"^[0-7]{6}\.[0-7]{2}$")
GROUP = re.compile(r"[0-7]{6}\.[0-7]{2}(?![0-7])")      # digits may precede: a fused LINE
UNDOTTED = re.compile(r"(?<![0-7])[0-7]{8}(?![0-7])")
# One printed character, as a fraction of page width: 30.06 px at 300 dpi
# (strap/listing_grid.py) on a 17-inch, 5100 px page.
CHAR_W = 30.06 / 5100


def load(path):
    out = []
    for ln in open(path):
        p = ln.rstrip("\n").split("\t")
        if len(p) >= 4:
            out.append((float(p[0]), float(p[1]), p[3]))
    return out


def groups(x, tok):
    """[(x_of_group, "oooooo.oo")] for every octal group INSIDE a token.

    Tesseract fuses columns -- "12003777.40" is LINE 12 and LOCATION
    003777.40 -- so a token is searched, and each group placed at its
    own x by character offset, not at the token's left edge."""
    t = tok.translate(OCT_FIX)
    if "." in t:
        return [(x + m.start() * CHAR_W, m.group()) for m in GROUP.finditer(t)]
    # no period read at all: the grid puts it after the sixth digit
    return [(x + m.start() * CHAR_W, m.group()[:6] + "." + m.group()[6:])
            for m in UNDOTTED.finditer(t)]


# Row pitch, measured per page by strap/listing_grid.py: 49.81-50.36 px
# at 300 dpi on the 3300 px page.  A fit outside it has paired line
# numbers to the wrong rows, so the measured range bounds the fit.
PITCH = (49.81 / 3300, 50.36 / 3300)
FIT_MIN_POINTS, FIT_MIN_AGREE = 6, 0.6


def fit_lines(obs):
    """(y0, pitch, agree, n) from LINE-column reads, or None.

    None when fewer than six line numbers were read, or fewer than 60%
    of them sit on the fitted grid: such a page CANNOT be paired, and is
    reported unfit rather than compared row-against-wrong-row."""
    pts = []
    for y, x, t in obs:
        if LINE_X[0] <= x <= LINE_X[1]:
            d = re.sub(r"[*#\s]", "", t).translate(OCT_FIX)
            if re.fullmatch(r"\d{1,2}", d) and 1 <= int(d) <= 60:
                pts.append((int(d), y))
    if len(pts) < FIT_MIN_POINTS:
        return None
    pitches = [(y2 - y1) / (n2 - n1) for (n1, y1) in pts for (n2, y2) in pts
               if n2 - n1 >= 3]
    if not pitches:
        return None
    pitch = min(max(statistics.median(pitches), PITCH[0]), PITCH[1])
    y0 = statistics.median(y - (n - 1) * pitch for n, y in pts)
    agree = sum(1 for n, y in pts if abs(y - (y0 + (n - 1) * pitch)) < 0.35 * pitch)
    if agree < FIT_MIN_AGREE * len(pts):
        return None
    return y0, pitch, agree, len(pts)


def field_at(obs, y, pitch, xwin):
    best = None
    for oy, ox, t in obs:
        if abs(oy - y) >= 0.45 * pitch:
            continue
        for gx, v in groups(ox, t):
            if xwin[0] <= gx <= xwin[1] and (best is None or abs(oy - y) < best[0]):
                best = (abs(oy - y), v)
    return best[1] if best else None


