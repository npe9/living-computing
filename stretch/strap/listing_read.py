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

GEOMETRY.  The two scanned volumes do not share a frame: vol 1 is 5100
px wide with LOCATION at x ~0.202, vol 2 is 4499 px wide with it at
~0.095.  geometry() measures the frame ON EACH PAGE from the reading
itself -- LOCATION is the leftmost column of octal groups, BINARY half
word 1 the strongest column 13-17 characters right of it -- and every
function takes that frame.  Without one, the vol 1 constants below are
used, which is what the scored and suite-checked pages were read with.
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


def geometry(obs, w_px=5100, h_px=3300):
    """The page's column frame, measured from its own octal groups, or None."""
    cw = 30.06 / w_px
    cells = {}
    for y, x, t in obs:
        for gx, _ in groups(x, t, cw):
            k = round(gx / cw)
            cells[k] = cells.get(k, 0) + 1
    if not cells:
        return None
    merged = {k: sum(cells.get(k + d, 0) for d in (-1, 0, 1)) for k in cells}
    top = max(merged.values())
    if top < 5:
        return None
    # LOCATION: the leftmost column with a BINARY partner 13-17 cells right.
    # "Leftmost strong column" alone picked BINARY on pages whose LOCATION
    # column reads badly (vol 2 PDF pp.1, 103, 104, 137).
    loc = b = None
    for k in sorted(k for k, n in merged.items() if n >= max(3, 0.1 * top)):
        near = {j: n for j, n in merged.items() if 13 <= j - k <= 17 and n >= 3}
        if near:
            loc = max((j for j in (k - 1, k, k + 1)), key=lambda j: cells.get(j, 0))
            b = max(near, key=lambda j: (near[j], cells.get(j, 0)))
            break
    if loc is None:
        return None
    lx, bx = loc * cw, b * cw
    return {"char_w": cw,
            "line_x": (lx - 6.5 * cw, lx - 1.5 * cw),
            "loc_x": (lx - 2.0 * cw, lx + 3.5 * cw),
            "bin_x": (bx - 2.0 * cw, bx + 3.5 * cw),
            "pitch": (PITCH_PX[0] / h_px, PITCH_PX[1] / h_px),
            "loc_cell": loc, "bin_cell": b}


def groups(x, tok, char_w=None):
    """[(x_of_group, "oooooo.oo")] for every octal group INSIDE a token.

    Tesseract fuses columns -- "12003777.40" is LINE 12 and LOCATION
    003777.40 -- so a token is searched, and each group placed at its
    own x by character offset, not at the token's left edge."""
    cw = char_w or CHAR_W
    t = tok.translate(OCT_FIX)
    if "." in t:
        return [(x + m.start() * cw, m.group()) for m in GROUP.finditer(t)]
    # no period read at all: the grid puts it after the sixth digit
    return [(x + m.start() * cw, m.group()[:6] + "." + m.group()[6:])
            for m in UNDOTTED.finditer(t)]


# Row pitch.  strap/listing_grid.py's ink fit says 49.81-50.36 px at 300
# dpi; Vision's LINE-column positions say 49.58 (q10-q90 49.32-49.69, 183
# vol 1 pages) -- the two measurements DISAGREE by ~0.5% and that is not
# resolved.  The bound only has to reject mispaired fits, which come out
# at 28-49 px (pp.53, 95, 156; vol 2 PDF p.30), so it spans both.
PITCH_PX = (49.2, 50.4)
PITCH = (PITCH_PX[0] / 3300, PITCH_PX[1] / 3300)
FIT_MIN_POINTS, FIT_MIN_AGREE = 6, 0.6


def fit_lines(obs, g=None):
    """(y0, pitch, agree, n) from LINE-column reads, or None.

    The pitch is SCANNED over its physical bound (see below).

    None when fewer than six line numbers were read, or fewer than 60%
    of them sit on the fitted grid: such a page CANNOT be paired, and is
    reported unfit rather than compared row-against-wrong-row."""
    line_x = g["line_x"] if g else LINE_X
    bounds = g["pitch"] if g else PITCH
    # pts: (candidate line numbers, y).  A bare single digit d may be the
    # tens digit of a number whose units Vision lost ("46*" read "4" on
    # vol 2), so it stands for d or 10d..10d+9; "4*" or "12" is exact.
    pts = []
    for y, x, t in obs:
        if line_x[0] <= x <= line_x[1]:
            d = re.sub(r"[*#\s]", "", t).translate(OCT_FIX)
            if not (re.fullmatch(r"\d{1,2}", d) and 1 <= int(d) <= 60):
                continue
            n = int(d)
            bare = len(d) == 1 and t.strip() == d and n <= 6
            cands = [n] + [m for m in range(10 * n, 10 * n + 10) if m <= 60] if bare else [n]
            pts.append((cands, y))
    if len(pts) < FIT_MIN_POINTS:
        return None

    def on_grid(y0, pitch):
        out = []
        for cands, y in pts:
            n = min(cands, key=lambda m: abs(y - (y0 + (m - 1) * pitch)))
            if abs(y - (y0 + (n - 1) * pitch)) < 0.35 * pitch:
                out.append((n, y))
        return out

    # The pitch is physically known, so it is SCANNED across the bound, not
    # estimated: a median of pairwise pitches was wrecked (2-16 px) on vol 2
    # pages where "16" reads "1".  For each pitch, every exact read proposes
    # a y0; the (pitch, y0) with the most points on the grid wins.
    # The scan only CHOOSES the points; the line is then least-squares
    # fitted to them.  Taking the scan's own pitch picked the bound's
    # lower edge every time: at +-0.35 row many pitches tie on count.
    exact = [(c[0], y) for c, y in pts if len(c) == 1] or [(c[0], y) for c, y in pts]
    best = []
    for i in range(13):
        pitch = bounds[0] + (bounds[1] - bounds[0]) * i / 12
        for n, y in exact:
            on = on_grid(y - (n - 1) * pitch, pitch)
            if len(on) > len(best):
                best = on
    if len(best) < FIT_MIN_AGREE * len(pts):
        return None
    mn = statistics.mean(n for n, _ in best)
    my = statistics.mean(y for _, y in best)
    sxx = sum((n - mn) ** 2 for n, _ in best)
    pitch = sum((n - mn) * (y - my) for n, y in best) / sxx if sxx else bounds[0]
    pitch = min(max(pitch, bounds[0]), bounds[1])
    y0 = statistics.median(y - (n - 1) * pitch for n, y in best)
    agree = len(on_grid(y0, pitch))
    if agree < FIT_MIN_AGREE * len(pts):
        return None
    return y0, pitch, agree, len(pts)


def field_at(obs, y, pitch, xwin, char_w=None):
    best = None
    for oy, ox, t in obs:
        if abs(oy - y) >= 0.45 * pitch:
            continue
        for gx, v in groups(ox, t, char_w):
            if xwin[0] <= gx <= xwin[1] and (best is None or abs(oy - y) < best[0]):
                best = (abs(oy - y), v)
    return best[1] if best else None




def page_number(obs):
    """The header's PAGE NUMBER, or None if it was not read."""
    top = sorted(o for o in obs if o[0] < 0.06)
    for y, x, t in top:
        m = re.search(r"PAGE NUMBER\s*(\d+)", t)
        if m:
            return int(m.group(1))
        if "PAGE NUMBER" in t:
            for y2, x2, t2 in top:
                if abs(y2 - y) < 0.006 and x2 > x and re.fullmatch(r"\d{1,3}", t2.strip()):
                    return int(t2.strip())
    return None


def bit_address(loc):
    """'221515.40' -> word * 64 + bit; the bit field is two octal digits."""
    w, b = loc.split(".")
    return int(w, 8) * 64 + int(b, 8)
