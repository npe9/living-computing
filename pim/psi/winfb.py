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
  8, 9  reserved; answered BADOP
  a     read  x y w h                 x     y     w     h     -      -
  b     target which kind base pitch w h  which kind base pitch w     h
  c-f   reserved; answered BADOP

  (a and b are the 2026-11-26 EXTENSION of the frozen set, OURS and
  owner-approved: docs/simpos/m8_stops.md §7, window_hardware_plan.md
  §2.4 "The 2026-11-26 extension", and the section of that name below.
  8 and 9 stay reserved so that the streams written before it, which use
  0x90 and 0x93 as reserved records, mean what they meant.)

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
  never saved), 06 BADSURF (the extension: a target area that bitmap
  memory cannot hold, or a copy between two different areas that share
  words).  Whatever the status, a refused command draws nothing.

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

THE 2026-11-26 EXTENSION (OURS, owner-approved; docs/simpos/m8_stops.md):
drawing targets and reading dots back.  Basis: TM-225 p10 (PROSE: a
hidden window's image lives in a save area of the display's bitmap
memory, and output to a hidden window writes that area), TM-125 p17
(PRINTED-INTERFACE: get_point_value/4 reads a dot), TM-115 p82 (PROSE:
1.0's bitmap areas loaded from strings).  The command format, the
operands and every rule below are OURS.
  - A SURFACE is the frame (1,280 x 1,024, as above) or an AREA of bitmap
    memory (base, pitch, w, h): w x h dots, row j's dots from bit 15 of
    word base + j * pitch (MSB leftmost, as a save area's rows).  The box
    has two surface registers, the DESTINATION (where fill, line, glyph
    and copy draw) and the SOURCE (where copy and read take dots from);
    both are the frame at reset.  save, restore and dump are unchanged:
    they always move dots between the frame and bitmap memory.  The host
    allocates areas and save areas (OURS) so that they share no words.
    Bitmap memory is all 0 at reset, as the frame is (OURS): an area or
    a pad word reads 0 until it is written.  bsv/WinFbBox.bsv clears its
    bitmap RAM at reset beside the frame, inside the frame's 81,920
    cycles, so reset takes no longer (window_hardware_plan.md §2.4).
  - target which kind base pitch w h: which 0 sets the destination, 1 the
    source; kind 0 is the frame (base..h ignored), 1 an area.  BADOP if
    which > 1 or kind > 1; BADSURF (the register unchanged) if kind 1 and
    w = 0, h = 0, pitch = 0, pitch > 255, pitch < ceil(w / 16) or
    base + pitch * h > 65,536.  R is ignored.
  - On an area every primitive clips to the area's w x h as it clips to
    the frame's 1,280 x 1,024 (the right and bottom edges); a row's dots
    past w (its last word's pad) are never written.
  - copy runs from the source surface to the destination surface:
    nothing if sx >= the source's w or dx >= the destination's w (sy, dy
    likewise); else w := min(w, sw - sx, dw - dx), h likewise.  The
    source is read whole before anything is written (as before).  BADSURF,
    nothing drawn, when both are areas, not the same area (equal base and
    pitch), and their words [base, base + pitch * h) meet: the RTL's
    scan-order rule for an overlapping copy needs one coordinate system.
  - read x y w h: the rectangle of the SOURCE surface, cut as a fill is
    cut, is answered as data words (as a dump's frame is), ceil(w'/16)
    words a row, row-major, each row's dots from bit 15 of its first word
    and the pad dots of its last word 0; then its status (OK).  A cut
    rectangle with no dots answers no words.  R is ignored.
  - The reference keeps the read words in `Frame.reads`, in order; `run`
    writes them to a fourth file, one word a line in 4 hex digits, which
    the bench writes too (win_read.txt).

Use:
    python3 -I psi/winfb.py run STREAM OUT.pbm STATUS.txt [READS.txt]
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
READ, TARGET = 10, 11           # the 2026-11-26 extension (the header)
PRIMS = ['end', 'fill', 'line', 'glyph', 'copy', 'save', 'restore', 'dump',
         None, None, 'read', 'target']
NARGS = [0, 4, 6, 4, 6, 6, 1, 0, 0, 0, 4, 6]
HAS_ROP = [False, True, True, True, True, False, True, False, False, False,
           False, False]
ROPS = ['set', 'reset', 'xor', 'copy', 'reverse']
OK, BADOP, BADFONT, MISSING, BADSAVE, NOSAVE, BADSURF = range(7)
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
        # the 2026-11-26 extension: the destination and source surfaces
        # (None = the frame, else an area (base, pitch, w, h)) and the
        # words answered by read
        self.dst = None
        self.src = None
        self.reads = []

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

    # a surface's size, its row width in bits, and its rows (an area's row
    # j is the int of its pitch words, MSB = dot 0)
    @staticmethod
    def dims(s):
        return (W, H) if s is None else (s[2], s[3])

    @staticmethod
    def bits(s):
        return W if s is None else 16 * s[1]

    def get_row(self, s, y):
        if s is None:
            return self.rows[y]
        base, pitch = s[0] + y * s[1], s[1]
        v = 0
        for k in range(pitch):
            v = (v << 16) | self.save[base + k]
        return v

    def set_row(self, s, y, v):
        if s is None:
            self.rows[y] = v
            return
        base, pitch = s[0] + y * s[1], s[1]
        for k in range(pitch):
            self.save[base + k] = (v >> (16 * (pitch - 1 - k))) & 0xffff

    def put_rect(self, x, y, w, h, r, src_rows, s=None):
        """Draw rows of w bits (ints, MSB = leftmost) at (x, y) of surface
        S (the frame when None), cut to it."""
        sw, sh = self.dims(s)
        if x >= sw or y >= sh or w == 0 or h == 0:
            return
        cw, ch = min(w, sw - x), min(h, sh - y)
        nb = self.bits(s)
        for j in range(ch):
            src = src_rows[j] >> (w - cw)        # keep the left cw dots
            sh_ = nb - x - cw
            self.set_row(s, y + j, rop(r, src << sh_, self.get_row(s, y + j),
                                       ((1 << cw) - 1) << sh_))

    def get_rect(self, s, x, y, w, h):
        """The rows of the w x h rectangle at (x, y) of surface S (already
        cut to it), as ints of w bits, MSB = leftmost."""
        nb = self.bits(s)
        return [(self.get_row(s, y + j) >> (nb - x - w)) & ((1 << w) - 1)
                for j in range(h)]

    # -- primitives ----------------------------------------------------
    def fill(self, x, y, w, h, r):
        self.put_rect(x, y, w, h, r, [(1 << w) - 1] * h, self.dst)
        return OK

    def copy(self, sx, sy, w, h, dx, dy, r):
        S, D = self.src, self.dst
        if S is not None and D is not None and S[:2] != D[:2]:
            s0, s1 = S[0], S[0] + S[1] * S[3]
            d0, d1 = D[0], D[0] + D[1] * D[3]
            if s0 < d1 and d0 < s1:
                return BADSURF
        (sw, sh), (dw, dh) = self.dims(S), self.dims(D)
        if sx >= sw or dx >= dw or sy >= sh or dy >= dh:
            return OK
        w = min(w, sw - sx, dw - dx)
        h = min(h, sh - sy, dh - dy)
        if w == 0 or h == 0:
            return OK
        src = self.get_rect(S, sx, sy, w, h)      # read whole, then write
        self.put_rect(dx, dy, w, h, r, src, D)
        return OK

    def line(self, x1, y1, x2, y2, width, style, r):
        if width == 0:
            return OK
        s = self.dst
        sw, sh = self.dims(s)
        nb = self.bits(s)
        dx, dy = abs(x2 - x1), -abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        xmajor = dx >= -dy
        err, x, y, i = dx + dy, x1, y1, 0
        while True:
            if (style >> (15 - (i & 15))) & 1:
                for k in range(width):
                    px, py = (x, y + k) if xmajor else (x + k, y)
                    if px < sw and py < sh:
                        m = 1 << (nb - 1 - px)
                        self.set_row(s, py, rop(r, m, self.get_row(s, py), m))
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
                      [f.bits(gx, gy, gw, j) for j in range(gh)], self.dst)
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

    # -- the 2026-11-26 extension ----------------------------------------
    def read(self, x, y, w, h):
        s = self.src
        sw, sh = self.dims(s)
        if x >= sw or y >= sh or w == 0 or h == 0:
            return OK
        w, h = min(w, sw - x), min(h, sh - y)
        pitch = (w + 15) // 16
        for v in self.get_rect(s, x, y, w, h):
            v <<= 16 * pitch - w
            for k in range(pitch):
                self.reads.append((v >> (16 * (pitch - 1 - k))) & 0xffff)
        return OK

    def target(self, which, kind, base, pitch, w, h):
        if which > 1 or kind > 1:
            return BADOP
        if kind == 0:
            s = None
        elif (w == 0 or h == 0 or pitch == 0 or pitch > 255 or
              16 * pitch < w or base + pitch * h > SAVE_WORDS):
            return BADSURF
        else:
            s = (base, pitch, w, h)
        if which == 0:
            self.dst = s
        else:
            self.src = s
        return OK

    # -- the stream ------------------------------------------------------
    def command(self, op, a):
        """Run one decoded command; returns its status (None for end)."""
        prim, r = op >> 4, op & 15
        if prim == END:
            self.dumps.append(self.pbm())
            return None
        if prim > TARGET or prim in (8, 9) or r > 4:
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
        elif prim == READ:
            st = self.read(a[0], a[1], a[2], a[3])
        elif prim == TARGET:
            st = self.target(*a)
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
    if prim >= len(PRIMS) or PRIMS[prim] is None:
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
          'copy 3000 0 10 10 0 0 copy',
          # a source whose last dot is the first of a word, the funnel
          # needing that word (catches a short source-word range)
          'fill 16 700 1 1 set', 'fill 48 700 3 1 set',
          'copy 1 700 16 1 0 701 copy', 'copy 33 700 16 1 70 702 copy',
          'end']
    return '\n'.join(L)


def s_save_restore(_seed):
    """Hide/show: a window saved, drawn over, restored exactly."""
    L = ['fill 200 200 300 200 set', 'fill 202 202 296 196 reset',
         'fill 210 210 50 14 set', 'fill 211 230 77 3 xor',
         'save 0 205 207 123 77 0', 'save 1 600 611 17 5 1000',
         'fill 590 600 40 30 xor',
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


# the 2026-11-26 extension's streams (read and target; the header)
def s_reads(_seed):
    """Reads of the frame: every alignment of a row's first and last dot,
    widths 1, 15, 16, 17, 33, clipped at both edges, empty, and a read of
    what was just drawn by each primitive (a read must not change the
    frame: the dumps around them check it)."""
    L = ['fill 3 3 40 9 set', 'fill 5 4 30 5 xor', 'line 0 20 100 25 2 61680 set',
         'glyph 0 9025 60 0 copy', 'fill 1270 1015 10 9 set', 'dump']
    for x0 in (0, 1, 7, 15, 16, 17, 31):
        for w in (1, 15, 16, 17, 33):
            L.append('read %d 3 %d 2' % (x0, w))
    L += ['read 0 0 100 30', 'read 60 0 11 14', 'read 1270 1015 64 64',
          'read 1279 1023 5 5', 'read 1280 0 4 4', 'read 0 1024 4 4',
          'read 10 10 0 4', 'read 10 10 4 0', 'dump', 'end']
    return '\n'.join(L)


def s_targets(_seed):
    """Drawing on areas of bitmap memory and copying between surfaces."""
    L = [  # an area 70 x 30 at word 1000, pitch 5 (80 dots; 10 pad dots)
         'target 0 1 1000 5 70 30', 'fill 0 0 70 30 set', 'fill 3 2 50 7 xor',
         'line 0 0 69 29 1 65535 reset', 'line 60 0 10 25 3 52428 xor',
         'glyph 0 9025 20 12 copy', 'glyph 0 9026 65 20 set',     # cut at the right
         'fill 66 25 40 40 xor',                                  # cut on two sides
         'target 1 1 1000 5 70 30', 'read 0 0 70 30', 'read 63 27 20 20',
         # the area onto the frame, frame to area, then area to area
         'target 0 0 0 0 0 0', 'copy 0 0 70 30 101 201 copy',
         'copy 5 5 70 30 300 300 xor', 'dump',
         'target 1 0 0 0 0 0', 'target 0 1 3000 3 40 20',
         'fill 0 0 40 20 reset', 'copy 98 199 40 20 0 0 copy',
         'target 1 1 3000 3 40 20', 'read 0 0 40 20',
         'target 0 1 1000 5 70 30', 'copy 0 0 40 20 13 4 reverse',
         'target 1 1 1000 5 70 30', 'read 0 0 70 30',
         # one area onto itself: the scan order of an overlapping copy
         'target 0 1 1000 5 70 30', 'copy 0 0 60 25 3 2 copy',
         'copy 4 3 60 25 0 0 copy', 'copy 0 0 60 25 9 0 copy', 'read 0 0 70 30',
         # areas that share words: BADSURF, nothing drawn
         'target 1 1 1003 5 70 30', 'copy 0 0 10 10 0 0 copy', 'read 0 0 70 30',
         # refused targets (the registers unchanged)
         'target 0 1 0 0 16 4', 'target 0 1 0 1 17 4', 'target 0 1 0 256 4 4',
         'target 0 1 65530 4 64 2', 'target 0 1 0 4 0 4', 'target 0 1 0 4 4 0',
         'target 2 0 0 0 0 0', 'target 0 2 0 0 0 0',
         'fill 0 0 4 4 set', 'read 0 0 16 1',
         'target 0 1 65532 4 64 1', 'fill 0 0 64 1 set', 'target 1 1 65532 4 64 1',
         'read 0 0 64 1',
         # a save area and an area: save and restore stay frame <-> memory
         'target 1 0 0 0 0 0', 'target 0 0 0 0 0 0',
         'save 0 101 201 70 30 2000', 'fill 100 200 80 40 xor', 'restore 0 copy',
         'target 1 1 2000 5 70 30', 'read 0 0 70 30', 'end']
    return '\n'.join(L)


def _rand_x(seed, targets):
    """Every primitive with reads (and, when TARGETS, targets) mixed in,
    the coordinates drawn for the surface in use."""
    rnd = random.Random(seed)
    areas = [(0, 4, 64, 40), (200, 7, 100, 60), (700, 1, 16, 9), (900, 25, 400, 30),
             (2000, 5, 70, 30), (2050, 5, 70, 30), (65536 - 2 * 40, 2, 32, 40)]
    dst = src = (W, H)

    def coord(lim):
        return rnd.choice([rnd.randrange(lim), rnd.randrange(lim + 16),
                           rnd.randrange(min(lim, 32)), max(0, lim - rnd.randrange(1, 20))])
    L = []
    for _ in range(500):
        p = rnd.choice(['fill'] * 4 + ['copy'] * 4 + ['line'] * 3 + ['glyph'] * 2 +
                       ['read'] * 3 + ['target'] * (3 if targets else 0) +
                       ['save', 'restore', 'dump'])
        r = rnd.choice(ROPS)
        if p == 'target':
            which = rnd.randrange(2)
            if rnd.random() < 0.3:
                L.append('target %d 0 0 0 0 0' % which)
                sz = (W, H)
            elif rnd.random() < 0.1:
                L.append('target %d 1 %d %d %d %d' % (which, rnd.randrange(65536), rnd.randrange(300),
                                                      rnd.randrange(5000), rnd.randrange(300)))
                continue      # maybe refused: the sizes below may be stale (they only steer coordinates)
            else:
                b, pt, w, h = rnd.choice(areas)
                L.append('target %d 1 %d %d %d %d' % (which, b, pt, w, h))
                sz = (w, h)
            if which:
                src = sz
            else:
                dst = sz
        elif p == 'fill':
            L.append('fill %d %d %d %d %s' % (coord(dst[0]), coord(dst[1]), rnd.randrange(0, 90),
                                              rnd.randrange(0, 50), r))
        elif p == 'copy':
            L.append('copy %d %d %d %d %d %d %s' % (coord(src[0]), coord(src[1]), rnd.randrange(0, 120),
                                                    rnd.randrange(0, 60), coord(dst[0]), coord(dst[1]), r))
        elif p == 'line':
            L.append('line %d %d %d %d %d %d %s' % (coord(dst[0]), coord(dst[1]), coord(dst[0]),
                                                    coord(dst[1]), rnd.choice([0, 1, 1, 2, 3]),
                                                    rnd.choice([0xffff, rnd.randrange(65536)]), r))
        elif p == 'glyph':
            L.append('glyph 0 %d %d %d %s' % (rnd.choice([0x2341 + rnd.randrange(26), 0x2330 + rnd.randrange(10),
                                                          rnd.randrange(65536)]),
                                              coord(dst[0]), coord(dst[1]), r))
        elif p == 'read':
            L.append('read %d %d %d %d' % (coord(src[0]), coord(src[1]), rnd.randrange(0, 70),
                                           rnd.randrange(0, 12)))
        elif p == 'save':
            L.append('save %d %d %d %d %d %d' % (rnd.randrange(17), coord(W), coord(H), rnd.randrange(0, 90),
                                                 rnd.randrange(0, 40), rnd.randrange(0, 65000)))
        elif p == 'restore':
            L.append('restore %d %s' % (rnd.randrange(17), r))
        else:
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


def s_rand_r(seed):
    return _rand_x(seed, False)


def s_rand_x2(seed):
    return _rand_x(seed, True)


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
    # the 2026-11-26 extension: read X1, target X2 (milestone labels OURS)
    'reads': (s_reads, 0, 'X1'),
    'rand_r_1': (s_rand_r, 31, 'X1'),
    'rand_r_2': (s_rand_r, 32, 'X1'),
    'targets': (s_targets, 0, 'X2'),
    'rand_x2_1': (s_rand_x2, 21, 'X2'),
    'rand_x2_2': (s_rand_x2, 22, 'X2'),
    'rand_x2_3': (s_rand_x2, 23, 'X2'),
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
    if name == 'reads':
        # the extension's raw records: read and target with reserved ops
        # (BADOP, nothing read, the register unchanged), the reserved
        # primitives 8, 9 and c, and a read after them (the frame)
        text = text.replace(line_of(END << 4, []),
                            line_of(0xa5, [0, 0, 16, 1, 0, 0]) + '\n' +
                            line_of(0xbf, [0, 1, 0, 4, 64, 4]) + '\n' +
                            line_of(0x80, [0, 0, 16, 1, 0, 0]) + '\n' +
                            line_of(0x90, [0, 1, 0, 4, 64, 4]) + '\n' +
                            line_of(0xc0, [0, 0, 16, 1, 0, 0]) + '\n' +
                            line_of(0xa0, [0, 3, 16, 1, 0, 0]) + '\n' +
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
        if len(argv) > 4:
            with open(argv[4], 'w') as fh:
                fh.write(''.join('%04x\n' % v for v in fr.reads))
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
