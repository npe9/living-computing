#!/usr/bin/env python3
"""The Hobbit terminal's display and input devices, for tools/p9boot.py.

s9term's screen is a RAM bitmap (`gscreen`) that `screenupdate` copies to
Bart's LCD through the two `Lcdisp` registers; its keyboard is the serial
console on Quart channel 0; its mouse is a serial mouse on Quart channel
3.  This module holds what p9boot needs for them, kept apart from the
board's other devices:

  Stop          the exception p9boot stops a run with (p9boot.Stop)
  LcdPanel      io.h `Lcdisp` (IOACK 0x3000): a shadow of the panel,
                built from what screenupdate writes (TERM_CHOICES['lcd'])
  framebuffer   read `gscreen` (GBitmap) from kernel memory: geometry and
                pixels (TERM_CHOICES['framebuffer'])
  write_image   PNG (zlib, no dependencies) or PGM of a grey image
  mouse_packet  one Mouse Systems 5-byte packet, as s9term's mouseputc
                decodes it (TERM_CHOICES['mouse'])
  InputScript   timed keyboard and mouse input, screenshots
                (TERM_CHOICES['input'])

Every fact here is read from s9term itself (its disassembly; the image
is older than the shipped sources, docs/s9term.md), and cited by function
and offset; the shipped sources are cited where they agree.  What neither
says is a choice, in TERM_CHOICES, also in docs/p9boot.md.
"""

import collections
import shlex
import struct
import zlib


class Stop(Exception):
    """The run cannot go on: p9boot reports where and why."""


TERM_CHOICES = {
    "framebuffer": "The screen is s9term's `gscreen`, a GBitmap in kernel "
                   "memory (screeninit+0x4c..+0xa4: base = xalloc(198656) "
                   "+ 2048, width 48 words, ldepth 1, r = (0,0,768,1024)): "
                   "768 x 1024 pixels of 2 bits, 192 bytes a row, row y at "
                   "base + 192y.  The dump reads the struct at dump time "
                   "(the base comes from xalloc).  Pixel order: islittle "
                   "(screen.c:24; s9term reverses its font and cursor "
                   "bits into that order with bitreverse), pixel 4k+j of a "
                   "row in bits 2j+1..2j of byte k, the bytes in address "
                   "order of the little-endian kernel (CONFIG.KL).  Shade: "
                   "s9term's getcolor (0x80026aa0) maps pixel 0 to white "
                   "(~0) and every other value to black; the dump draws "
                   "value v as grey 255 - 85v, i.e. 1 and 2 as greys, a "
                   "choice (nothing in the image distinguishes them, and "
                   "8½'s textures and fonts are 1-bit, which gbitblt "
                   "widens to 0 and 3).",
    "lcd": "Bart's LCD (io.h Lcdisp at IOACK 0x3000: ctl +0, data +4) is "
           "modelled as a 768 x 1024 panel of 2-bit cells, from what "
           "s9term's screenupdate (0x80026368) sends: for each group of "
           "four rows y..y+3 it writes ctl = y>>8 and then ctl = "
           "(y>>2)&0x3f (+0x78..+0xa0), and then, from x = 0, for each "
           "bitmap byte four data words (+0x134..+0x17c): word j holds "
           "pixel 4k+j of the four rows, row r in bits 2r+1..2r (its "
           "swiz13 table, built by lcdscsion 0x800262dc without the "
           "shipped source's ((m<<2)|m)>>1 step, then ~m).  The panel "
           "takes each ctl write's low 6 bits into an 8-bit row-group "
           "address shifted 6 bits at a time, and each ctl write resets "
           "the column to 0; each data write fills column `col` of the "
           "four rows with its low 8 bits and moves one column right.  "
           "The panel shows level 3 as white (the kernel sends ~pixel, "
           "and pixel 0 is white) and 0 as black, cells never written "
           "black.  No LCD data sheet is in the release; this is the "
           "reading under which the panel equals the bitmap, which the "
           "run checks (`panel == framebuffer` in the report).  The "
           "kernel never reads the LCD.",
    "keyboard": "s9term's keyboard is the serial console: main+0x8a calls "
                "eiaspecial(0, &printq, &kbdq, 19200), and kbdq.putc is "
                "kbdcr2nl (eiaspecial+0x68): ASCII bytes on Quart channel "
                "0, CR made NL, as from a terminal on the serial line.  "
                "The image has no kbd.c (no kbdinit: the shipped "
                "screen.c's kbdinit(2), a scan-code keyboard on channel 2 "
                "at 600 baud, came later), so there are no scan codes to "
                "model.  8½ reads the same bytes through /dev/cons in raw "
                "mode.  A 9term linked from the release does have kbd.c: "
                "for such an image (kbdinit defined) p9boot's "
                "CHOICES['console-keyboard'] puts the console on channel 2 "
                "as scan codes (tools/p9scancode.py), and the input "
                "script's `type` goes the same way (Boot.console_channel, "
                "Boot.console_encode).",
    "mouse": "The mouse is on Quart channel 3 at 1200 baud: main+0xa4 "
             "calls eiaspecial(3, 0, &mouseq, 1200), and printinit+0x6e "
             "sets mouseq.putc = mouseputc (0x8002c926; m3mouseputc, the "
             "Microsoft 3-byte decoder, is in the image but nothing "
             "installs it, and mousetype is never written).  mouseputc "
             "is devbit.c's 'Logitech 5 byte packed binary' decoder, the "
             "Mouse Systems format: a byte with high nibble 8 starts a "
             "packet, whose low 3 bits are the buttons, active low (bit 2 "
             "left, bit 1 middle, bit 0 right: its table b[] = {0, 4, 2, "
             "6, 1, 5, 3, 7} after ^7, Plan 9 buttons 1, 2, 4); then dx1, "
             "dy1, dx2, dy2 as signed bytes, dx = dx1 + dx2 and dy = "
             "-(dy1 + dy2) (y up).  So no delta byte may be 0x80..0x8F "
             "(it would restart the packet): mouse_packet keeps each in "
             "-100..100 and splits larger moves.  mouseupdate adds the "
             "delta to mouse.xy (mouse+0x10, +0x14) clamped to [0, 768] "
             "x [0, 1024], one count one pixel.  The packet's 5 bytes "
             "arrive back to back at 1200 baud 8N1 (QUART_CHOICES['rx']), "
             "41.7 ms a packet.",
    "input": "--input SCRIPT (or --input-line LINE, repeatable) gives "
             "timed input, one item per line, each waiting for the one "
             "before it: WHEN ACTION.  WHEN is `after S` (S model seconds "
             "after the previous item fired, or after the start), `at-"
             "cycle C` (model cycle C, what --input-log writes), `screen "
             "TEXT` (screenputs has shown TEXT, as --type), `quiet S` (no "
             "LCD write for S model seconds since the previous item: the "
             "screen has settled) or `step N`.  ACTION is `type TEXT` "
             "(backslash escapes; on the console line), `mouse DX DY "
             "[BUTTONS]` (relative, screen axes, y down), `move X Y "
             "[BUTTONS]` (to a position the script tracks: the kernel's "
             "mouse.xy when the script first moves, then its own sum of "
             "deltas, clamped as mouseupdate clamps), `buttons B` (a "
             "packet with no motion), `screen FILE` (dump the bitmap), "
             "`lcd FILE` (dump the panel), `mark` (nothing: a point the next "
             "item's time counts from) or `stop`.  BUTTONS is a set of "
             "L, M, R or `-` for none.  The model is deterministic, so a "
             "script fires at the same instructions in a replay; "
             "--input-log FILE writes what fired as `at-cycle` lines.",
}

LCD_W, LCD_H = 768, 1024


class LcdPanel:
    """io.h `Lcdisp` at IOACK(Lcdisp, 0x3000): ctl (+0), data (+4).
    TERM_CHOICES['lcd'].  `level` holds one 2-bit cell per pixel, row
    major; `written` marks the cells a data write reached."""

    def __init__(self, clock=None):
        self.clock = clock
        self.writes = collections.Counter()
        self.quad = 0
        self.col = 0
        self.level = bytearray(LCD_W * LCD_H)
        self.written = bytearray(LCD_W * LCD_H)
        self.last_write = None      # model time of the last write
        self.overruns = 0           # data written past the last column

    def read(self, off):
        raise Stop("LCD: read of +0x%x (write-only in the kernel)" % off)

    def write(self, off, data, mask):
        self.writes[off] += 1
        if self.clock is not None:
            self.last_write = self.clock()
        if off == 0:
            self.quad = ((self.quad << 6) | (data & 0x3F)) & 0xFF
            self.col = 0
            return
        if off != 4:
            return
        col = self.col
        self.col += 1
        if col >= LCD_W:
            self.overruns += 1
            return
        v = data & 0xFF
        i = 4 * self.quad * LCD_W + col
        lv, wr = self.level, self.written
        for r in range(4):
            lv[i] = (v >> (2 * r)) & 3
            wr[i] = 1
            i += LCD_W

    def grey(self):
        """The panel as 8-bit grey rows (level 3 white)."""
        return bytes(85 * v for v in self.level)


def framebuffer(read_word, gscreen):
    """TERM_CHOICES['framebuffer']: (info, pixels) of the GBitmap at
    kernel address `gscreen`; pixels is a bytearray of values, row major,
    and info a dict of base, width (words), ldepth, r."""
    w = [read_word(gscreen + 4 * i) for i in range(8)]
    base, _zero, width, ldepth = w[0], w[1], w[2], w[3]
    sx = lambda v: v - (1 << 32) if v & 0x80000000 else v
    r = tuple(sx(v) for v in w[4:8])
    info = dict(base=base, width=width, ldepth=ldepth, r=r)
    if not base or ldepth > 3 or width <= 0:
        return info, None
    minx, miny, maxx, maxy = r
    wd, ht = maxx - minx, maxy - miny
    bpp = 1 << ldepth
    ppb = 8 // bpp
    pmask = (1 << bpp) - 1
    stride = 4 * width
    lut = [bytes(((b >> (bpp * j)) & pmask) for j in range(ppb))
           for b in range(256)]
    pix = bytearray()
    for y in range(miny, maxy):
        row = base + stride * (y - miny)
        raw = bytearray()
        for a in range(row, row + stride, 4):
            raw += read_word(a).to_bytes(4, "little")
        line = b"".join(lut[b] for b in raw)
        pix += line[:wd]
    info["size"] = (wd, ht)
    return info, pix


def shade(pix, ldepth):
    """Pixel values to 8-bit grey, 0 white (TERM_CHOICES['framebuffer'])."""
    top = (1 << (1 << ldepth)) - 1
    table = bytes(255 - (255 * v) // top for v in range(top + 1))
    return pix.translate(table.ljust(256, b"\0"))


def write_image(path, width, height, grey):
    """An 8-bit grey image: PGM if `path` ends in .pgm, else PNG."""
    if path.endswith(".pgm"):
        with open(path, "wb") as f:
            f.write(b"P5\n%d %d\n255\n" % (width, height))
            f.write(bytes(grey))
        return
    raw = b"".join(b"\0" + bytes(grey[y * width:(y + 1) * width])
                   for y in range(height))

    def chunk(kind, data):
        c = struct.pack(">I", len(data)) + kind + data
        return c + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0,
                                           0, 0, 0)))
        f.write(chunk(b"IDAT", zlib.compress(raw, 9)))
        f.write(chunk(b"IEND", b""))


BUTTON_BITS = {"L": 4, "M": 2, "R": 1}     # TERM_CHOICES['mouse']
MOUSE_CHANNEL = 3
MOUSE_STEP = 100


def parse_buttons(text):
    if text in ("-", "", None):
        return ""
    bad = set(text) - set("LMR")
    if bad:
        raise ValueError("buttons are L, M, R or -: %r" % text)
    return text


def mouse_packet(dx, dy, buttons=""):
    """One Mouse Systems packet for a move of (dx, dy) screen pixels
    (y down) with `buttons` (a string of L, M, R) held; |dx|, |dy| <=
    2 * MOUSE_STEP."""
    down = 0
    for b in buttons:
        down |= BUTTON_BITS[b]
    my = -dy                            # mouseputc: dy = -(dy1 + dy2)
    if max(abs(dx), abs(my)) > 2 * MOUSE_STEP:
        raise ValueError("packet delta too large")
    x1, y1 = dx // 2, my // 2
    x2, y2 = dx - x1, my - y1
    return bytes([0x80 | (~down & 7)] + [v & 0xFF for v in (x1, y1, x2, y2)])


def mouse_packets(dx, dy, buttons=""):
    """A move split into packets of at most 2 * MOUSE_STEP a coordinate."""
    out = b""
    lim = 2 * MOUSE_STEP
    while True:
        sx = max(-lim, min(lim, dx))
        sy = max(-lim, min(lim, dy))
        out += mouse_packet(sx, sy, buttons)
        dx -= sx
        dy -= sy
        if not dx and not dy:
            return out


def unescape(text):
    return text.encode("latin-1").decode("unicode_escape").encode("latin-1")


class InputScript:
    """TERM_CHOICES['input'].  `boot` is the p9boot.Boot it drives (its
    quart, cycles, lcd, console and dump_screen)."""

    def __init__(self, boot, lines=()):
        self.boot = boot
        self.items = []
        for n, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            self.items.append(self.parse(line, n + 1))
        self.prev_cycle = 0         # when the previous item fired
        self.prev_screen = 0        # screen offset after the last match
        self.fired = []             # (steps, cycles, line)
        self.pos = None             # the script's idea of mouse.xy
        self.buttons = ""
        self.stopped = False

    @staticmethod
    def parse(line, n=0):
        words = shlex.split(line, posix=True)
        if len(words) < 2:
            raise ValueError("input line %d: %r: want WHEN ACTION" % (n, line))
        when = words[0]
        if when == "screen":
            arg, rest = unescape(words[1]), words[2:]
        elif when in ("after", "quiet"):
            arg, rest = float(words[1]), words[2:]
        elif when in ("at-cycle", "step"):
            arg, rest = int(words[1]), words[2:]
        else:
            raise ValueError("input line %d: unknown WHEN %r" % (n, when))
        if not rest:
            raise ValueError("input line %d: no action" % n)
        act, args = rest[0], rest[1:]
        if act == "type":
            args = [unescape(" ".join(args))]
        elif act in ("mouse", "move"):
            if len(args) not in (2, 3):
                raise ValueError("input line %d: %s X Y [BUTTONS]" % (n, act))
            args = [int(args[0]), int(args[1]),
                    parse_buttons(args[2] if len(args) == 3 else "-")]
        elif act == "buttons":
            args = [parse_buttons(args[0] if args else "-")]
        elif act in ("screen", "lcd"):
            if len(args) != 1:
                raise ValueError("input line %d: %s FILE" % (n, act))
        elif act not in ("stop", "mark"):
            raise ValueError("input line %d: unknown action %r" % (n, act))
        return dict(when=when, arg=arg, act=act, args=args, line=line)

    # --- when the next item is due ------------------------------------
    def due_cycle(self):
        """The model cycle at which the next item is due, if it waits on
        time (None for screen text, or nothing left)."""
        if not self.items:
            return None
        it = self.items[0]
        hz = self.boot.cpu_hz
        if it["when"] == "after":
            return self.prev_cycle + int(round(it["arg"] * hz))
        if it["when"] == "at-cycle":
            return it["arg"]
        if it["when"] == "quiet":
            last = self.boot.lcd.last_write
            base = self.prev_cycle
            if last is not None:
                base = max(base, int(round(last * hz)))
            return base + int(round(it["arg"] * hz))
        return None

    def next_time(self):
        """p9boot.Boot.next_event: the model time of the next timed item."""
        c = self.due_cycle()
        return None if c is None else c / float(self.boot.cpu_hz)

    def poll(self):
        """Fire every item that is due now; called from p9boot's run loop
        (cheaply: Boot keeps the due cycle)."""
        b = self.boot
        while self.items:
            it = self.items[0]
            w = it["when"]
            if w == "step":
                if b.steps < it["arg"]:
                    return
            elif w == "screen":
                screen = b.console["screenputs"]
                at = screen.find(it["arg"], self.prev_screen)
                if at < 0:
                    return
                self.prev_screen = at + len(it["arg"])
            else:
                c = self.due_cycle()
                if b.cycles < c:
                    return
            self.items.pop(0)
            self.fire(it)

    def fire(self, it):
        b = self.boot
        self.prev_cycle = b.cycles
        self.fired.append((b.steps, b.cycles, it["line"]))
        act, args = it["act"], it["args"]
        if act == "type":
            b.quart.feed(b.console_channel, b.console_encode(args[0]))
        elif act in ("mouse", "move", "buttons"):
            if self.pos is None:
                self.pos = b.mouse_xy()
            if act == "buttons":
                dx = dy = 0
                buttons = args[0]
            elif act == "mouse":
                dx, dy, buttons = args
            else:
                dx, dy = args[0] - self.pos[0], args[1] - self.pos[1]
                buttons = args[2]
            self.pos = (max(0, min(LCD_W, self.pos[0] + dx)),
                        max(0, min(LCD_H, self.pos[1] + dy)))
            self.buttons = buttons
            b.quart.feed(MOUSE_CHANNEL, mouse_packets(dx, dy, buttons))
        elif act == "screen":
            b.dump_screen(args[0])
        elif act == "lcd":
            b.dump_lcd(args[0])
        elif act == "stop":
            raise Stop("input script: stop (%s)" % it["line"])
        # "mark": nothing; the item only times the next one

    def log_lines(self):
        """The fired items as `at-cycle` lines (--input-log)."""
        out = []
        for _steps, cycles, line in self.fired:
            words = shlex.split(line)
            n = 2
            out.append("at-cycle %d %s" % (
                cycles, " ".join(shlex.quote(w) for w in words[n:])))
        return out
