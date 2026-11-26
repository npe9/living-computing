#!/usr/bin/env python3
"""The display device of the SIMPOS window stand-ins (OURS, 2026-11-25).

docs/simpos/window_environment_plan.md §4.1 puts the window classes in ESP
stand-ins (package simpos) over "one narrow device layer, written in
Python through the existing SIMPOS_MODELS hook in psi/kl0.py".  This file
is that hook's target.  It does no window management: the stand-ins
(psi/standin/window_pane.esp, standard_io_window.esp, pmacs_window.esp)
decide every rectangle, glyph position, scroll and cursor; they send the
primitives below and this device runs each one as ONE command of the
frozen winfb command set (psi/winfb.py, the H0/H1 contract), on one
winfb.Frame per machine.  That is the PSI/UX split the plan cites (Giho
9106 p86, PROSE: SIMPOS's window manager made the drawing requests and a
"SIMPOS window server" outside SIMPOS drew them), and it means that what
a live kl0 run drew is a winfb command stream: `stream_text()` replays
through `winfb.run_stream` (and so through bsv/WinFbBox.bsv's bench) to
the same frame.

THE SELECTORS (class methods of simpos##bitmap_display; the class name is
SIMPOS's, USAGE window.md §2.13 `get_mouse/2`; every selector and its
argument order here is OURS, as the plan §4.1 says it would be):

  :fill(#bitmap_display, X, Y, W, H, Op)            winfb `fill`
  :glyph(#bitmap_display, Font, Code, X, Y, Op)     winfb `glyph`
  :copy(#bitmap_display, SX, SY, W, H, DX, DY, Op)  winfb `copy`
  :line(#bitmap_display, X1, Y1, X2, Y2, Wd, Op)    winfb `line`, solid
  :save(#bitmap_display, Id, X, Y, W, H, Base)      winfb `save` (window M7)
  :restore(#bitmap_display, Id, Op)                 winfb `restore` (M7)
  :load_font(#bitmap_display, File, ^Id, ^W, ^H)    the plan's font_load
  :default_font(#bitmap_display, ^Id, ^W, ^H)       OURS (see below)
  :get_size(#bitmap_display, ^W, ^H)                1280 x 944

Op is an atom: set, reset, exclusive_or (W§2.5's drawing operations),
copy, reverse (W§2.5's transfer operations).  save/restore (window M7,
2026-11-25) are the save areas of TM-225 p10 / TM-126 p5 (PROSE, window.md
§4.1: "a hidden window's image is kept in a per-window save area in bitmap
memory"): the slot Id (0-15) and the word Base in winfb's 65,536-word
bitmap memory are chosen by the ESP stand-in standin/save_memory.esp, not
here; a slot or area the memory cannot hold is winfb's BADSAVE, so a
Refusal, and a restore of a slot never saved is NOSAVE, also a Refusal.  A refused command (winfb
status BADOP, BADFONT, BADSAVE, NOSAVE) is a kl0 Refusal: nothing is ever
dropped silently.  MISSING (a code test_11 lacks) draws the font's 0xffff
box and succeeds, so a gap shows on the screen (the plan §1.4).

Fonts.  `load_font` reads a file of the mounted file system
(psi/simpos_fs.py places psdpim's FONT.DIR under `font:`, HELD
placement) and decodes it as f822 (winfb.Font, the plan §1.4, MEASURED).
The command set draws only font 0 = test_11 (winfb's freeze), so a file
whose words are test_11's gets id 0 and any other font a new id whose
metrics are answered but whose glyphs refuse when drawn.  The cell the
stand-ins step by is the font's space character (16#2121), as TM-115
p16-17 says the cursor size is reset from it (PROSE, window.md §2.2).
`default_font` answers test_11 straight from the archive: it is the OURS
substitute for the window's default font_13, which is not held (the plan
§1.4), used only when a window is drawn before any set_font/2.

Screen.  winfb's frame is 1,280 x 1,024 (OURS, hardware plan §2.1);
get_size answers the logical 1,280 x 944 (INFERENCE, the plan §1.1: TM-785
p9 and kl1graph's full-screen window); the rows below 944 are left for the
status band (status_band.esp, window M6).

Views (the plan §4.2): `png_bytes` (a 1-bit PNG at the frame's real
size, stdlib zlib; 0 = black in PNG greyscale, so the frame's bits are
inverted), `read_cells` (the text of a window read back from the
FRAMEBUFFER by matching each cell against the font's glyphs, so a
transcript proves dots, not a shadow), `stream_text` and `pbm_sha256`.

Use:  python3 -I psi/windev.py png IN.pbm OUT.png     (any winfb PBM)
The live screens are made by psi/winshot.py; the tests are
psi/test_espc.py `test_win_*`.
"""
import hashlib
import os
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import winfb  # noqa: E402

SCREEN_W, SCREEN_H = 1280, 944          # INFERENCE (module docstring)
OPS = {'set': 0, 'reset': 1, 'exclusive_or': 2, 'copy': 3, 'reverse': 4}
SPACE = 0x2121


class Device:
    """One machine's screen: a winfb frame and the commands run on it."""

    def __init__(self):
        self.frame = winfb.Frame(winfb.test_11())
        self.log = []                   # [(op byte, [A..F])], in order
        self.fonts = []                 # id -> winfb.Font (id 0 test_11)

    def run(self, prim, rop, args):
        op = prim << 4 | rop
        args = list(args) + [0] * (6 - len(args))
        st = self.frame.command(op, args)
        self.log.append((op, args))
        return st

    def stream_text(self):
        return ''.join(winfb.line_of(op, a) + '\n' for op, a in self.log) + \
            winfb.line_of(winfb.END << 4, []) + '\n'

    def font_id(self, font):
        if font.words == winfb.test_11().words:
            return 0
        for i, f in enumerate(self.fonts):
            if i and f.words == font.words:
                return i
        if not self.fonts:
            self.fonts.append(winfb.test_11())
        self.fonts.append(font)
        return len(self.fonts) - 1


def device(m):
    """The device of kl0 machine M (made at its first use; it lives as long
    as the machine, across m.reset(), as a screen does)."""
    d = getattr(m, 'windev', None)
    if d is None:
        d = m.windev = Device()
    return d


def cell_of(font):
    rec = font.records.get(SPACE)
    if rec is None:
        return font.words[13], font.words[14]
    return rec[2], rec[3]


# ------------------------------------------------------------- the models
def install(models, K):
    """Add the device's selectors to kl0's SIMPOS_MODELS.  K is the kl0
    module object (passed in: kl0 may be __main__)."""
    D = 'simpos##bitmap_display'

    def ints(m, n, what):
        out = []
        for i in range(n):
            v = K.deref(m.x[i])
            if isinstance(v, K.Var):
                raise K.Refusal('unbound argument', 'bitmap_display %s: argument %d unbound' % (what, i + 1))
            if not isinstance(v, int) or not 0 <= v <= 0xffff:
                raise K.Refusal('simpos', 'bitmap_display %s: argument %d is %r, not a dot coordinate' % (what, i + 1, v))
            out.append(v)
        return out

    def op_of(m, i, what):
        v = K.deref(m.x[i])
        if not isinstance(v, K.Atom) or v.name not in OPS:
            raise K.Refusal('simpos', 'bitmap_display %s: operation %r' % (what, v))
        return OPS[v.name]

    def check(st, what):
        if st not in (winfb.OK, winfb.MISSING):
            raise K.Refusal('simpos', 'bitmap_display %s: winfb status %d' % (what, st))

    def fill(m):
        a = ints(m, 4, 'fill/6')
        check(device(m).run(winfb.FILL, op_of(m, 4, 'fill/6'), a), 'fill/6')
        return m.proceed()

    def glyph(m):
        a = ints(m, 4, 'glyph/6')
        check(device(m).run(winfb.GLYPH, op_of(m, 4, 'glyph/6'), a), 'glyph/6')
        return m.proceed()

    def copy(m):
        a = ints(m, 6, 'copy/8')
        check(device(m).run(winfb.COPY, op_of(m, 6, 'copy/8'), a), 'copy/8')
        return m.proceed()

    def line(m):
        a = ints(m, 5, 'line/7')
        check(device(m).run(winfb.LINE, op_of(m, 5, 'line/7'), a + [0xffff]), 'line/7')
        return m.proceed()

    def save(m):
        a = ints(m, 6, 'save/7')
        check(device(m).run(winfb.SAVE, 0, a), 'save/7')
        return m.proceed()

    def restore(m):
        a = ints(m, 1, 'restore/3')
        check(device(m).run(winfb.RESTORE, op_of(m, 1, 'restore/3'), a), 'restore/3')
        return m.proceed()

    def answer(m, base, font_id, font):
        w, h = cell_of(font)
        ok = (m.unify(m.x[base], font_id) and m.unify(m.x[base + 1], w)
              and m.unify(m.x[base + 2], h))
        return m.proceed() if ok else m.fail()

    def load_font(m):
        f = K.deref(m.x[0])
        if not isinstance(f, K.Instance):
            raise K.Refusal('simpos', 'bitmap_display load_font/5 on %r, not a file' % (f,))
        name = m.get_slot(f, 'full_name')
        if not isinstance(name, K.Str):
            raise K.Refusal('simpos', 'bitmap_display load_font/5: %r has no full name' % (f,))
        import simpos_fs
        raw = simpos_fs.raw_of(name.text.rsplit('.', 1)[0])
        if raw is None:
            raise K.Refusal('simpos', 'bitmap_display load_font/5: %s holds no bytes here' % name.text)
        try:
            font = winfb.Font(raw)
        except ValueError:
            return m.fail()             # not an f822 font: create/3 fails
        return answer(m, 1, device(m).font_id(font), font)

    def default_font(m):
        return answer(m, 0, 0, winfb.test_11())

    def get_size(m):
        ok = m.unify(m.x[0], SCREEN_W) and m.unify(m.x[1], SCREEN_H)
        return m.proceed() if ok else m.fail()

    models.update({
        (D, 'class', 'fill', 6): fill,
        (D, 'class', 'glyph', 6): glyph,
        (D, 'class', 'copy', 8): copy,
        (D, 'class', 'line', 7): line,
        (D, 'class', 'save', 7): save,
        (D, 'class', 'restore', 3): restore,
        (D, 'class', 'load_font', 5): load_font,
        (D, 'class', 'default_font', 4): default_font,
        (D, 'class', 'get_size', 3): get_size,
    })


# -------------------------------------------------------------- the views
def pbm_sha256(frame):
    return hashlib.sha256(frame.pbm()).hexdigest()


def png_bytes(frame, height=None):
    """FRAME (a winfb.Frame) as a 1-bit greyscale PNG (stdlib only)."""
    h = winfb.H if height is None else height
    nb = winfb.W // 8
    full = (1 << winfb.W) - 1
    raw = b''.join(b'\x00' + (full ^ r).to_bytes(nb, 'big') for r in frame.rows[:h])

    def chunk(kind, data):
        return (struct.pack('>I', len(data)) + kind + data +
                struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff))
    return (b'\x89PNG\r\n\x1a\n' +
            chunk(b'IHDR', struct.pack('>IIBBBBB', winfb.W, h, 1, 0, 0, 0, 0)) +
            chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))


def png_rows(data):
    """The frame rows of a PNG png_bytes wrote (for the round-trip check)."""
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    i, idat, w, h = 8, b'', None, None
    while i < len(data):
        n = struct.unpack('>I', data[i:i + 4])[0]
        kind, body = data[i + 4:i + 8], data[i + 8:i + 8 + n]
        if kind == b'IHDR':
            w, h, depth, ctype = struct.unpack('>IIBB', body[:10])
            assert (depth, ctype) == (1, 0)
        elif kind == b'IDAT':
            idat += body
        i += 12 + n
    raw = zlib.decompress(idat)
    nb = w // 8
    full = (1 << w) - 1
    rows = []
    for j in range(h):
        line = raw[j * (nb + 1):(j + 1) * (nb + 1)]
        assert line[0] == 0
        rows.append(full ^ int.from_bytes(line[1:], 'big'))
    return rows


def glyph_table(font):
    """{cell bits: code} for every glyph of FONT (one int per cell)."""
    out = {}
    for code in sorted(font.records):
        gx, gy, gw, gh, _ = font.records[code]
        v = 0
        for j in range(gh):
            v = (v << gw) | font.bits(gx, gy, gw, j)
        out.setdefault((gw, gh, v), code)
    return out


def read_cells(frame, x, y, cols, rows, font=None):
    """The text in the COLS x ROWS cells from (X, Y) of FRAME, read back
    from its dots: each cell is matched against the font's glyphs (and
    their inverse, which is how the block cursor shows: '#' marks a cursor
    over a blank cell, a lower-case glyph read inverted is wrapped in
    '[ ]').  '?' is a cell that matches no glyph.  -> list of strings,
    trailing blanks stripped."""
    import ptfdump as P
    font = font or winfb.test_11()
    cw, ch = cell_of(font)
    table = glyph_table(font)
    full = (1 << cw) - 1
    out = []
    for r in range(rows):
        s = ''
        for c in range(cols):
            px, py = x + c * cw, y + r * ch
            v = 0
            for j in range(ch):
                v = (v << cw) | ((frame.rows[py + j] >> (winfb.W - px - cw)) & full)
            inv = v ^ ((1 << (cw * ch)) - 1)
            if v == 0:
                s += ' '
            elif (cw, ch, v) in table:
                code = table[(cw, ch, v)]
                s += ' ' if code == SPACE else P.ch(code)
            elif inv == 0:
                s += '#'
            elif (cw, ch, inv) in table:
                s += '[%s]' % P.ch(table[(cw, ch, inv)])
            else:
                s += '?'
        out.append(s.rstrip())
    return out


def main(argv):
    if len(argv) == 3 and argv[0] == 'png':
        with open(argv[1], 'rb') as f:
            data = f.read()
        fr = winfb.Frame()
        hdr = winfb.PBM_HEADER
        assert data[:len(hdr)] == hdr, 'not a winfb PBM'
        body = data[len(hdr):len(hdr) + winfb.W // 8 * winfb.H]
        fr.rows = [int.from_bytes(body[j * 160:(j + 1) * 160], 'big') for j in range(winfb.H)]
        with open(argv[2], 'wb') as f:
            f.write(png_bytes(fr))
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
