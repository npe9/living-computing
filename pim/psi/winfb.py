#!/usr/bin/env python3
"""The window device layer: a 1-bit framebuffer and its drawing commands.

This is the Python reference of docs/simpos/window_hardware_plan.md
(H0/H1) and of the "device layer" of window_environment_plan.md §4.1
(M5's primitive set).  Both plans make it the contract: the Bluespec box
bsv/WinFbBox.bsv (mkWinFbBox) runs the same command stream and its frame
is compared with this module's byte for byte (bsv/run_win_tb.sh).  The
plan says the reference is written first and its command format is then
frozen for the RTL; this file is that freeze (2026-11-25).

EVERYTHING HERE IS OURS SCAFFOLDING.  The PSI's display controller is not
documented (window_hardware_plan.md §1.1); what is sourced is:
  - the bit order: MSB = the leftmost dot, rows of 16-bit words
    (TM-115 p74-76, PROSE; window_environment_plan.md §1.1);
  - 1 = a set (black) dot, which is also PBM P4's convention
    (window_hardware_plan.md §4 "Why PBM P4");
  - the raster operations set, reset, exclusive_or (for drawing) and
    copy, reverse (for transfers) of window.md W§2.5;
  - the primitive list fb_fill, fb_line, fb_glyph, fb_copy,
    fb_save/fb_restore (window_environment_plan.md §4.1, itself OURS);
  - the font: test_11.font of the HELD psdpim archive (FONT.DIR), f822
    format, decoded as window_environment_plan.md §1.4 records (21 header
    words; nchar 8-word records (code, x, y, width, height, bias, 0, 0);
    one strip of `height` rows, ceil(strip width / 16) words a row, MSB
    leftmost).  It is read in memory from docs/nonlocal/psdpim.tar.Z
    (gzip -dc + tarfile, as asm/psdpim.py does); nothing is extracted to
    disk and nothing in the archive is executed.

The frame (OURS, the plan's §2.1 choice): 1,280 x 1,024 dots, one bit
each, 80 words of 16 bits a row, initially all 0 (white).

THE COMMAND STREAM (OURS, frozen).  A text file, one command a line; it is
also a Verilog $readmemh file, which is how the Bluesim bench reads it:

    PP_AAAA_BBBB_CCCC_DDDD_EEEE_FFFF   // mnemonic (a comment, ignored)

26 hex digits = 104 bits: an opcode byte PP and six 16-bit unsigned
operands A..F.  Blank lines and `//` comments are ignored; underscores are
ignored (both by $readmemh and here).  PP's high nibble is the primitive,
its low nibble the raster op R:

  prim  mnemonic                      A     B     C     D     E      F
  0     end                           -     -     -     -     -      -
  1     fill  x y w h R               x     y     w     h     -      -
  2     line  x1 y1 x2 y2 width style R  x1  y1    x2    y2    width  style
  3     glyph font code x y R         font  code  x     y     -      -
  4     copy  sx sy w h dx dy R       sx    sy    w     h     dx     dy
  5     save  id x y w h base         id    x     y     w     h      base
  6     restore id R                  id    -     -     -     -      -
  7     dump                          -     -     -     -     -      -
  8-f   reserved (OURS: patterns etc. later); answered BADOP

  R: 0 set (d | s), 1 reset (d & ~s), 2 xor (d ^ s), 3 copy (s),
     4 reverse (~s); 5-f answered BADOP, nothing drawn, for every
     primitive (save and dump included).  d is the frame
     dot, s the source dot; a fill's and a line's source is a 1 dot.
     For a glyph the op covers the glyph's whole cell rectangle, so
     set/xor/reset are transparent and copy/reverse opaque (OURS).
     save ignores R (it copies); dump and end ignore it.

`end` stops the stream; it is not a box command.  At `end`, and at every
`dump`, the frame is appended to the output as one PBM P4 image, so a
fault that is later drawn over still shows in an earlier image.

Every command but `end` gets one status (two hex digits a line in the
status file; the bench writes the same file):
  00 OK, 01 BADOP, 02 BADFONT, 03 MISSING (the font's 0xffff glyph was
  drawn in place of a code it lacks, so a gap is never silent; with no
  0xffff record nothing is drawn), 04 BADSAVE (id >= 16, or the area
  would pass the end of bitmap memory), 05 NOSAVE (restore of an id
  never saved).  Whatever the status, a refused command draws nothing.

Coordinates and clipping (OURS).  All operands are unsigned, so only the
right and bottom edges clip (the plan's §2.4: the box clips only to the
screen; windows are clipped by the stand-in window manager).
  - fill/glyph/restore: the destination rectangle is cut to the frame;
    w or h 0, or a corner at x >= 1280 or y >= 1024, draws nothing (OK).
  - copy: nothing if sx, dx >= 1280 or sy, dy >= 1024; else
    w := min(w, 1280 - sx, 1280 - dx), h := min(h, 1024 - sy, 1024 - dy).
    The source is read whole before anything is written, so an
    overlapping copy behaves as a copy through a buffer.
  - line: Bresenham over the endpoints, both included:
        dx = |x2-x1|, dy = -|y2-y1|, err = dx + dy, i = 0
        loop: if style bit (15 - i mod 16) is 1: plot the pen at (x, y)
              stop if (x, y) = (x2, y2)
              e2 = 2 err; if e2 >= dy: err += dy, x += sign
                          if e2 <= dx: err += dx, y += sign
              i += 1
    The pen (OURS) is `width` dots across the major axis: (x, y+k) for
    k < width when |x2-x1| >= |y2-y1|, else (x+k, y).  Each pen dot is
    one read-modify-write in order, so xor over an overlap is defined;
    dots off the frame are skipped; width 0 draws nothing.  style is a
    16-bit dash pattern, 0xffff solid.
  - glyph: font 0 is test_11 (others BADFONT).  The record of `code` is
    drawn with its cell's top-left at (x, y) (OURS: the bias field, 3
    in test_11, is not applied; it is the stand-in's business for the
    baseline).  Codes are looked up as the plan's §2.5 index does: JIS
    rows/columns 0x21-0x7e, control codes 0-0x1f and 0xffff.
  - save id x y w h base: the rectangle, cut to the frame, is copied to
    bitmap memory (65,536 words of 16 bits; the plan's §2.3 says save
    areas first go to spare block RAM) at word `base`, ceil(w/16) words
    a row, each row's dots left-aligned from bit 15 of its first word;
    the pad dots of a row's last word are left as they were.  The host
    allocates `base` (OURS).  The slot table has 16 entries; a re-save
    of an id replaces its entry.  BADSAVE if id >= 16 or
    base + ceil(w/16) * h > 65,536 (the entry is then unchanged).
  - restore id R: the saved rectangle is drawn back where it was saved,
    through R (normally copy).  The entry stays, so restore can repeat.

Use:
    python3 -I psi/winfb.py run STREAM OUT.pbm STATUS.txt
    python3 -I psi/winfb.py asm MNEMONICS.txt STREAM     (mnemonic -> stream)
    python3 -I psi/winfb.py gen NAME [SEED] > STREAM     (the bench streams)
    python3 -I psi/winfb.py fonthex OUT.hex              (test_11 words, BRAM load)
    python3 -I psi/winfb.py streams                      (list gen NAMEs)
The unit tests are psi/test_winfb.py.
"""
import io
import os
import random
import struct
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
TAR = os.path.join(HERE, '..', 'docs', 'nonlocal', 'psdpim.tar.Z')
FONT_MEMBER = 'psdpim/FONT.DIR/test_11.font'

W, H = 1280, 1024           # OURS (plan §2.1)
WPR = W // 16
FULL = (1 << W) - 1
SAVE_WORDS = 65536          # OURS
SAVE_SLOTS = 16             # OURS

END, FILL, LINE, GLYPH, COPY, SAVE, RESTORE, DUMP = range(8)
PRIMS = ['end', 'fill', 'line', 'glyph', 'copy', 'save', 'restore', 'dump']
NARGS = [0, 4, 6, 4, 6, 6, 1, 0]
HAS_ROP = [False, True, True, True, True, False, True, False]
ROPS = ['set', 'reset', 'xor', 'copy', 'reverse']
OK, BADOP, BADFONT, MISSING, BADSAVE, NOSAVE = range(6)
PBM_HEADER = b'P4\n%d %d\n' % (W, H)


def rop(r, s, d, m):
    """Op r of source bits s on frame bits d, within mask m (ints)."""
    if r == 0:
        v = d | s
    elif r == 1:
        v = d & ~s
    elif r == 2:
        v = d ^ s
    elif r == 3:
        v = s
    else:
        v = ~s
    return (d & ~m) | (v & m)


# --------------------------------------------------------------- the font
def font_bytes():
    raw = subprocess.run(['gzip', '-dc', TAR], stdout=subprocess.PIPE,
                         check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
        return tf.extractfile(FONT_MEMBER).read()


class Font:
    """An f822 font (window_environment_plan.md §1.4)."""

    def __init__(self, data):
        w = struct.unpack('>%dH' % (len(data) // 2), data)
        if w[0] != 0xf822:
            raise ValueError('not an f822 font: %04x' % w[0])
        self.words = list(w)
        self.n, self.strip_bits, self.height = w[4], w[5], w[6]
        self.wpr = (self.strip_bits + 15) // 16
        self.base = 21 + 8 * self.n
        if len(w) != self.base + self.height * self.wpr:
            raise ValueError('f822 length identity fails')
        self.records = {}
        for i in range(self.n):
            code, x, y, gw, gh, bias = w[21 + 8 * i:27 + 8 * i]
            self.records[code] = (x, y, gw, gh, bias)
        self.rows = []      # each strip row as one int, MSB = bit 0
        for j in range(self.height):
            v = 0
            for k in range(self.wpr):
                v = (v << 16) | w[self.base + j * self.wpr + k]
            self.rows.append(v)

    def bits(self, x, y, gw, row):
        """The gw dots of strip row y+row from x, as an int (MSB first)."""
        nb = self.wpr * 16
        return (self.rows[y + row] >> (nb - x - gw)) & ((1 << gw) - 1)


_FONT = None


def test_11():
    global _FONT
    if _FONT is None:
        _FONT = Font(font_bytes())
    return _FONT


def jis_indexable(code):
    hi, lo = code >> 8, code & 0xff
    return code < 0x20 or code == 0xffff or (
        0x21 <= hi <= 0x7e and 0x21 <= lo <= 0x7e)


# ------------------------------------------------------------ the device
class Frame:
    def __init__(self, font=None):
        self.rows = [0] * H          # row y as an int; dot x is bit W-1-x
        self.save = [0] * SAVE_WORDS
        self.slots = [None] * SAVE_SLOTS
        self.font = font
        self.dumps = []              # PBM images, one per dump / end
        self.status = []

    # -- helpers -----------------------------------------------------
    def dot(self, x, y):
        return (self.rows[y] >> (W - 1 - x)) & 1

    def count(self):
        return sum(bin(r).count('1') for r in self.rows)

    def pbm(self):
        return PBM_HEADER + b''.join(r.to_bytes(W // 8, 'big')
                                     for r in self.rows)

    def span(self, x, w):
        return ((1 << w) - 1) << (W - x - w)

    def put_rect(self, x, y, w, h, r, src_rows):
        """Draw rows of w bits (ints, MSB = leftmost) at (x, y), cut."""
        if x >= W or y >= H or w == 0 or h == 0:
            return
        cw, ch = min(w, W - x), min(h, H - y)
        for j in range(ch):
            s = src_rows[j] >> (w - cw)          # keep the left cw dots
            sh = W - x - cw
            self.rows[y + j] = rop(r, s << sh, self.rows[y + j],
                                   ((1 << cw) - 1) << sh)

    # -- primitives ----------------------------------------------------
    def fill(self, x, y, w, h, r):
        self.put_rect(x, y, w, h, r, [(1 << w) - 1] * h)
        return OK

    def copy(self, sx, sy, w, h, dx, dy, r):
        if sx >= W or dx >= W or sy >= H or dy >= H:
            return OK
        w = min(w, W - sx, W - dx)
        h = min(h, H - sy, H - dy)
        if w == 0 or h == 0:
            return OK
        src = [(self.rows[sy + j] >> (W - sx - w)) & ((1 << w) - 1)
               for j in range(h)]                 # read whole, then write
        self.put_rect(dx, dy, w, h, r, src)
        return OK

    def line(self, x1, y1, x2, y2, width, style, r):
        if width == 0:
            return OK
        dx, dy = abs(x2 - x1), -abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        xmajor = dx >= -dy
        err, x, y, i = dx + dy, x1, y1, 0
        while True:
            if (style >> (15 - (i & 15))) & 1:
                for k in range(width):
                    px, py = (x, y + k) if xmajor else (x + k, y)
                    if px < W and py < H:
                        m = 1 << (W - 1 - px)
                        self.rows[py] = rop(r, m, self.rows[py], m)
            if x == x2 and y == y2:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy
            i += 1
        return OK

    def glyph(self, font, code, x, y, r):
        if font != 0 or self.font is None:
            return BADFONT
        f = self.font
        st = OK
        rec = f.records.get(code) if jis_indexable(code) else None
        if rec is None:
            st = MISSING
            rec = f.records.get(0xffff)
            if rec is None:
                return st
        gx, gy, gw, gh, _bias = rec
        self.put_rect(x, y, gw, gh, r,
                      [f.bits(gx, gy, gw, j) for j in range(gh)])
        return st

    def save_area(self, sid, x, y, w, h, base):
        if sid >= SAVE_SLOTS:
            return BADSAVE
        if x >= W or y >= H or w == 0 or h == 0:
            w = h = 0
        else:
            w, h = min(w, W - x), min(h, H - y)
        pitch = (w + 15) // 16
        if base + pitch * h > SAVE_WORDS:
            return BADSAVE
        for j in range(h):
            v = ((self.rows[y + j] >> (W - x - w)) & ((1 << w) - 1)) \
                << (16 * pitch - w)
            for k in range(pitch):
                sh = 16 * (pitch - 1 - k)
                word = (v >> sh) & 0xffff
                left = w - 16 * k                # dots in this word
                m = 0xffff if left >= 16 else (0xffff << (16 - left)) & 0xffff
                a = base + j * pitch + k
                self.save[a] = (self.save[a] & ~m & 0xffff) | (word & m)
        self.slots[sid] = (x, y, w, h, base)
        return OK

    def restore(self, sid, r):
        if sid >= SAVE_SLOTS:
            return BADSAVE
        if self.slots[sid] is None:
            return NOSAVE
        x, y, w, h, base = self.slots[sid]
        pitch = (w + 15) // 16
        src = []
        for j in range(h):
            v = 0
            for k in range(pitch):
                v = (v << 16) | self.save[base + j * pitch + k]
            src.append(v >> (16 * pitch - w))
        self.put_rect(x, y, w, h, r, src)
        return OK

    # -- the stream ------------------------------------------------------
    def command(self, op, a):
        """Run one decoded command; returns its status (None for end)."""
        prim, r = op >> 4, op & 15
        if prim == END:
            self.dumps.append(self.pbm())
            return None
        if prim > DUMP or r > 4:
            st = BADOP
        elif prim == FILL:
            st = self.fill(a[0], a[1], a[2], a[3], r)
        elif prim == LINE:
            st = self.line(a[0], a[1], a[2], a[3], a[4], a[5], r)
        elif prim == GLYPH:
            st = self.glyph(a[0], a[1], a[2], a[3], r)
        elif prim == COPY:
            st = self.copy(a[0], a[1], a[2], a[3], a[4], a[5], r)
        elif prim == SAVE:
            st = self.save_area(*a)
        elif prim == RESTORE:
            st = self.restore(a[0], r)
        else:
            self.dumps.append(self.pbm())
            st = OK
        self.status.append(st)
        return st

    def run(self, records):
        for op, a in records:
            if self.command(op, a) is None:
                return
        raise ValueError('stream has no end record')


# ----------------------------------------------------------- the format
def encode(op, a):
    a = list(a) + [0] * (6 - len(a))
    for v in a:
        if not 0 <= v <= 0xffff:
            raise ValueError('operand out of range: %r' % v)
    return '%02x_' % op + '_'.join('%04x' % v for v in a)


def mnemonic(op, a):
    prim, r = op >> 4, op & 15
    if prim > DUMP:
        return 'reserved %02x' % op
    s = PRIMS[prim] + ''.join(' %d' % v for v in a[:NARGS[prim]])
    if HAS_ROP[prim]:
        s += ' ' + (ROPS[r] if r < len(ROPS) else 'rop%d' % r)
    return s


def line_of(op, a):
    return '%s   // %s' % (encode(op, a), mnemonic(op, a))


def parse_stream(text):
    """Records [(op, [A..F])] from the stream text."""
    out = []
    for ln, line in enumerate(text.splitlines(), 1):
        line = line.split('//', 1)[0].strip().replace('_', '')
        if not line:
            continue
        if len(line.split()) != 1 or len(line) != 26:
            raise ValueError('line %d: not a 26-digit record' % ln)
        v = int(line, 16)
        out.append((v >> 96, [(v >> (80 - 16 * i)) & 0xffff
                              for i in range(6)]))
    return out


def assemble(text):
    """Mnemonic lines ('fill 1 2 3 4 xor') to stream text."""
    out = []
    for ln, line in enumerate(text.splitlines(), 1):
        t = line.split('#', 1)[0].split()
        if not t:
            continue
        prim = PRIMS.index(t[0])
        n = NARGS[prim]
        args = [int(v, 0) for v in t[1:1 + n]]
        rest = t[1 + n:]
        r = 3 if prim in (SAVE,) else 0
        if HAS_ROP[prim]:
            if len(rest) != 1:
                raise ValueError('line %d: needs one op' % ln)
            r = ROPS.index(rest[0])
        elif rest:
            raise ValueError('line %d: extra operands' % ln)
        if len(args) != n:
            raise ValueError('line %d: needs %d operands' % (ln, n))
        out.append(line_of(prim << 4 | r, args))
    return '\n'.join(out) + '\n'


def run_stream(text, font=None):
    fr = Frame(font if font is not None else test_11())
    fr.run(parse_stream(text))
    return fr


# ---------------------------------------------------------- the streams
# Each builder returns mnemonic text (assembled by `gen`).  The directed
# ones pin one behaviour each; the random ones mix everything with a
# fixed seed.  The bench runs every name in STREAMS.

def s_fill_edges(_seed):
    """Unaligned fills of every op; a 16-aligned fill cannot see a
    flipped bit order, these can."""
    L = []
    for i in range(17):
        L.append('fill %d %d %d 3 set' % (3 + 17 * i, 4 + 5 * i, 1 + i))
    L += ['fill 0 200 1280 40 set', 'fill 5 210 1270 10 xor',
          'fill 17 205 33 30 reset', 'fill 1275 300 10 10 set',
          'fill 0 1020 20 20 set', 'fill 1279 1023 1 1 set',
          'fill 2000 10 5 5 set', 'fill 100 100 0 5 set',
          'fill 300 300 31 9 copy', 'fill 300 300 31 9 reverse',
          'fill 301 302 29 5 reverse', 'dump',
          'fill 0 0 1280 1024 xor', 'end']
    return '\n'.join(L)


def s_xor_twice(_seed):
    return '\n'.join(['fill 10 10 300 200 set',
                      'fill 37 41 113 77 xor', 'dump',
                      'fill 37 41 113 77 xor', 'dump',
                      'fill 7 9 1 1 xor', 'fill 7 9 1 1 xor', 'end'])


def s_copy_overlap(_seed):
    """A pattern copied onto itself in the four directions and with
    every op; overlapping copies need the right scan order."""
    L = ['fill 100 100 50 40 set', 'fill 110 105 7 7 reset',
         'fill 133 120 3 19 xor', 'fill 100 139 50 1 reset']
    L += ['copy 100 100 60 50 103 100 copy', 'dump',
          'copy 100 100 60 50 97 100 copy', 'dump',
          'copy 100 100 60 50 100 104 copy', 'dump',
          'copy 100 104 60 50 100 101 copy', 'dump',
          'copy 95 98 70 60 117 113 copy',
          'copy 120 110 70 60 101 99 copy', 'dump',
          'copy 100 100 64 48 400 400 set',
          'copy 100 100 64 48 401 450 reset',
          'copy 100 100 64 48 405 500 xor',
          'copy 100 100 64 48 413 550 reverse',
          'copy 100 100 64 48 0 0 copy',
          'copy 1200 1000 200 200 10 600 copy',
          'copy 10 600 200 200 1250 990 copy',
          'copy 3000 0 10 10 0 0 copy', 'end']
    return '\n'.join(L)


def s_save_restore(_seed):
    """Hide/show: a window saved, drawn over, restored exactly."""
    L = ['fill 200 200 300 200 set', 'fill 202 202 296 196 reset',
         'fill 210 210 50 14 set', 'fill 211 230 77 3 xor',
         'save 0 205 205 123 77 0', 'save 1 600 600 17 5 1000',
         'fill 150 150 400 400 xor', 'dump',
         'restore 0 copy', 'dump',
         'fill 0 0 1280 1024 set', 'restore 1 copy', 'restore 0 copy',
         'dump', 'restore 0 xor', 'restore 5 copy',
         'save 16 0 0 8 8 0', 'save 2 0 0 1280 1024 0',
         'save 3 1270 1020 50 50 65535', 'save 4 0 0 16 4 65533',
         'save 4 0 0 16 3 65533', 'restore 4 reverse', 'end']
    return '\n'.join(L)


def s_glyphs(_seed):
    """test_11 text: the Login PIMOS prompt run and every op."""
    L = []
    text = [0x2341, 0x2342, 0x2367, 0x2121, 0x2125, 0x2164, 0x2330,
            0x2339, 0x235a, 0x237a, 0x2132, 0x215d, 0x0001, 0x001f,
            0xffff, 0x2122, 0x0041, 0x7f7f]
    for i, c in enumerate(text):
        L.append('glyph 0 %d %d 20 set' % (c, 30 + 11 * i))
    for i, r in enumerate(ROPS):
        L.append('fill %d 60 40 20 set' % (30 + 50 * i))
        for k in range(5):
            L.append('glyph 0 %d %d %d %s' % (0x2341 + k, 33 + 50 * i
                                                + 7 * k, 63 + k, r))
    # "Shell>> " in test_11, as PIMOS's console prompt
    for i, c in enumerate([0x2353, 0x2368, 0x2365, 0x236c, 0x236c,
                           0x2164, 0x2164, 0x2121]):
        L.append('glyph 0 %d %d 200 copy' % (c, 200 + 11 * i))
    # Login PIMOS's first prompt (docs/fep_services.md §6.9), as test_11
    # draws it in the requester's window
    for i, c in enumerate(jis_text(LOGIN_PROMPT)):
        L.append('glyph 0 %d %d 300 set' % (c, 20 + 11 * i))
    L += ['glyph 1 9025 0 0 set', 'glyph 0 9025 1275 1020 set', 'end']
    return '\n'.join(L)


LOGIN_PROMPT = 'Enter FEP node name--------->'


def jis_text(s):
    """ASCII text as the full-width JIS X 0208 codes test_11 holds (OURS
    table for the few characters used: window_hardware_plan.md §3.1)."""
    out = []
    for ch in s:
        if 'A' <= ch <= 'Z':
            out.append(0x2341 + ord(ch) - ord('A'))
        elif 'a' <= ch <= 'z':
            out.append(0x2361 + ord(ch) - ord('a'))
        elif '0' <= ch <= '9':
            out.append(0x2330 + ord(ch) - ord('0'))
        else:
            out.append({' ': 0x2121, '.': 0x2125, ':': 0x2127, '_': 0x2132,
                        '-': 0x215d, '>': 0x2164}[ch])
    return out


def s_lines(_seed):
    L = []
    for k in range(16):
        L.append('line 640 500 %d %d 1 65535 set' % (640 + 37 * (k - 8),
                                                     500 + 29 * (8 - k)))
    L += ['line 10 10 300 10 3 65535 set', 'line 10 20 10 300 2 43690 set',
          'line 20 20 290 290 1 61680 xor', 'line 290 20 20 290 4 65535 xor',
          'line 30 400 900 420 1 65535 copy',
          'line 900 430 30 410 1 52428 reverse',
          'line 1270 1000 1300 1100 5 65535 set',
          'line 5 5 5 5 1 65535 set', 'line 7 7 9 9 0 65535 set',
          'line 100 900 100 900 1 0 set', 'end']
    return '\n'.join(L)


def _rand_stream(seed, n, prims):
    rnd = random.Random(seed)

    def coord(lim):
        return rnd.choice([rnd.randrange(lim), rnd.randrange(lim + 64),
                           rnd.randrange(64), lim - rnd.randrange(1, 40)])

    L = []
    for _ in range(n):
        p = rnd.choice(prims)
        r = rnd.choice(ROPS)
        if p == 'fill':
            big = rnd.random() < 0.1
            w = rnd.randrange(1, 1300) if big else rnd.randrange(0, 70)
            h = rnd.randrange(1, 300) if big else rnd.randrange(0, 40)
            L.append('fill %d %d %d %d %s' % (coord(W), coord(H), w, h, r))
        elif p == 'copy':
            sx, sy = coord(W), coord(H)
            if rnd.random() < 0.5:     # overlapping, any direction
                dx = max(0, sx + rnd.randrange(-20, 21))
                dy = max(0, sy + rnd.randrange(-12, 13))
            else:
                dx, dy = coord(W), coord(H)
            L.append('copy %d %d %d %d %d %d %s' % (
                sx, sy, rnd.randrange(0, 120), rnd.randrange(0, 60),
                dx, dy, r))
        elif p == 'save':
            w, h = rnd.randrange(0, 100), rnd.randrange(0, 50)
            L.append('save %d %d %d %d %d %d' % (
                rnd.randrange(18), coord(W), coord(H), w, h,
                rnd.choice([rnd.randrange(0, 60000), 65536 - 100])))
        elif p == 'restore':
            L.append('restore %d %s' % (rnd.randrange(18), r))
        elif p == 'line':
            L.append('line %d %d %d %d %d %d %s' % (
                coord(W), coord(H), coord(W), coord(H),
                rnd.choice([0, 1, 1, 1, 2, 3]),
                rnd.choice([0xffff, 0xffff, rnd.randrange(65536)]), r))
        elif p == 'glyph':
            c = rnd.choice([0x2341 + rnd.randrange(26),
                            0x2361 + rnd.randrange(26),
                            0x2330 + rnd.randrange(10),
                            rnd.randrange(0x20), rnd.randrange(65536),
                            0x2121 + rnd.randrange(94)])
            L.append('glyph %d %d %d %d %s' % (
                0 if rnd.random() < 0.95 else 1, c, coord(W), coord(H), r))
        elif p == 'dump':
            L.append('dump')
    L.append('end')
    return '\n'.join(L)


def s_rand_h0(seed):
    return _rand_stream(seed, 400, ['fill'] * 5 + ['copy'] * 4 +
                        ['save', 'restore', 'restore', 'dump'])


def s_rand_h1(seed):
    return _rand_stream(seed, 400, ['fill'] * 3 + ['copy'] * 3 +
                        ['save', 'restore', 'dump'] + ['line'] * 3 +
                        ['glyph'] * 4)


# name -> (builder, seed, milestone)
STREAMS = {
    'fill_edges': (s_fill_edges, 0, 'H0'),
    'xor_twice': (s_xor_twice, 0, 'H0'),
    'copy_overlap': (s_copy_overlap, 0, 'H0'),
    'save_restore': (s_save_restore, 0, 'H0'),
    'rand_h0_1': (s_rand_h0, 1, 'H0'),
    'rand_h0_2': (s_rand_h0, 2, 'H0'),
    'rand_h0_3': (s_rand_h0, 3, 'H0'),
    'glyphs': (s_glyphs, 0, 'H1'),
    'lines': (s_lines, 0, 'H1'),
    'rand_h1_1': (s_rand_h1, 11, 'H1'),
    'rand_h1_2': (s_rand_h1, 12, 'H1'),
}


def gen(name, seed=None):
    f, s, _m = STREAMS[name]
    text = assemble(f(s if seed is None else seed))
    if name == 'save_restore':
        # two raw records the assembler will not write: a reserved
        # primitive and a reserved op (both BADOP, nothing drawn)
        text = text.replace(line_of(END << 4, []),
                            line_of(0x93, [1, 1, 5, 5, 0, 0]) + '\n' +
                            line_of(0x17, [1, 1, 5, 5, 0, 0]) + '\n' +
                            line_of(END << 4, []))
    return text


def write_font_hex(path):
    f = test_11()
    with open(path, 'w') as fh:
        for v in f.words:
            fh.write('%04x\n' % v)


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    cmd = argv[0]
    if cmd == 'run':
        with open(argv[1]) as fh:
            fr = run_stream(fh.read())
        with open(argv[2], 'wb') as fh:
            fh.write(b''.join(fr.dumps))
        with open(argv[3], 'w') as fh:
            fh.write(''.join('%02x\n' % s for s in fr.status))
    elif cmd == 'asm':
        with open(argv[1]) as fh:
            text = assemble(fh.read())
        with open(argv[2], 'w') as fh:
            fh.write(text)
    elif cmd == 'gen':
        sys.stdout.write(gen(argv[1], int(argv[2]) if len(argv) > 2
                             else None))
    elif cmd == 'fonthex':
        write_font_hex(argv[1])
    elif cmd == 'streams':
        for k, (_f, s, m) in STREAMS.items():
            print(k, m, s)
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
