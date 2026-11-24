#!/usr/bin/env python3
"""The Hobbit terminal's screen, LCD and mouse (tools/p9term.py, wired into
tools/p9boot.py; docs/p9boot.md "The terminal: screen, keyboard, mouse").

UnitTest is pure Python: the Mouse Systems packet as s9term's mouseputc
decodes it, and the LCD panel's addressing.  TerminalTest boots s9term to
/boot's prompt (25 Hz, as PromptTest), moves the mouse twice through
Quart channel 3 with the left button down on the second packet, and
dumps the screen: the bitmap's geometry, the LCD panel equal to the
bitmap, the kernel's mouse state and the cursor where the mouse went,
and the pixels' checksum.  ~45 M instructions (most retired by the idle
skip), ~1 min.  GtextureTest calls s9term's own gtexture alone (why 8½'s
background is white).  EightHalfReplayTest replays a live session as
tor into 8½ (tests/net/8half.pcap) and pins its screen; the longest
test here: 742 s of wall time, 315 s of CPU, on a loaded machine
(2026-11-24; P9TERM_8HALF=ls, to the end: 1082 s, 470 s of CPU).

Discriminating checks, observed 2026-11-24, each injection made in a
scratch copy of tools/p9term.py put first on the path
(build/gfx/inject.py; the real file's sha256 checked unchanged after),
the whole file run:

* buttons sent active high (`0x80 | (down & 7)`): FAIL test_packet,
  test_long_move, test_mouse (mouse.buttons); the screen is unchanged.
* dy not negated (`my = dy`): FAIL test_packet, test_long_move,
  test_mouse ((70, 0): the second move clamped at the top),
  test_cursor_moved, test_checksum, test_stopped_by_the_script (the
  cursor redrawn elsewhere: 32,506,699 instead of 32,506,727; both
  numbers 2 lower than now, measured before the Quart's interrupt bids
  were corrected the same day).
* the LCD's row-group address shifted 4 bits a write, not 6: FAIL
  test_panel, test_panel_is_the_bitmap.
* the dump's pixels taken from the high bits of a byte first: FAIL
  test_panel_is_the_bitmap, test_cursor_moved, test_checksum.

EightHalfReplayTest, observed 2026-11-24 the same way
(build/gfx/inject_half.sh), the class alone:

* the LCD's address shifted 4 bits a write: FAIL test_panel_is_the_bitmap.
* the dump's pixel order reversed: FAIL test_checksum,
  test_panel_is_the_bitmap.
* dy not negated, with P9TERM_8HALF=ls: FAIL test_checksum,
  test_stopped_by_the_script (2,985,362,639 steps, not 2,985,469,493:
  the window swept elsewhere), test_the_live_screenshot; every frame
  still as recorded (the sweep and `ls` touch only the terminal).
"""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HOBBIT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HOBBIT, "tools"))

import p9boot  # noqa: E402
import p9term  # noqa: E402

S9TERM = os.path.join(HOBBIT, "tools", "plan9-1e", "hobbit", "s9term")


class UnitTest(unittest.TestCase):

    def decode(self, pkt):
        """s9term's mouseputc (0x8002c926; devbit.c mouseputc) on one
        packet: (buttons, dx, dy) as mouseupdate gets them."""
        b = [0, 4, 2, 6, 1, 5, 3, 7]
        msg = [c - 256 if c & 0x80 else c for c in pkt]
        self.assertEqual(pkt[0] & 0xF0, 0x80)
        for c in pkt[1:]:
            self.assertNotEqual(c & 0xF0, 0x80, "a delta byte resyncs")
        return (b[(msg[0] & 7) ^ 7], msg[1] + msg[3], -(msg[2] + msg[4]))

    def test_packet(self):
        self.assertEqual(self.decode(p9term.mouse_packet(10, -20)),
                         (0, 10, -20))
        self.assertEqual(self.decode(p9term.mouse_packet(0, 0, "L")),
                         (1, 0, 0))
        self.assertEqual(self.decode(p9term.mouse_packet(-3, 5, "M")),
                         (2, -3, 5))
        self.assertEqual(self.decode(p9term.mouse_packet(200, -200, "R")),
                         (4, 200, -200))
        self.assertEqual(self.decode(p9term.mouse_packet(1, 1, "LR")),
                         (5, 1, 1))

    def test_long_move(self):
        data = p9term.mouse_packets(-450, 333, "L")
        self.assertEqual(len(data) % 5, 0)
        moves = [self.decode(data[i:i + 5]) for i in range(0, len(data), 5)]
        self.assertEqual(sum(m[1] for m in moves), -450)
        self.assertEqual(sum(m[2] for m in moves), 333)
        self.assertTrue(all(m[0] == 1 for m in moves))

    def test_panel(self):
        """screenupdate's sequence for rows 260..263, columns 0..1."""
        lcd = p9term.LcdPanel()
        y = 260
        lcd.write(0, y >> 8, 0xF)
        lcd.write(0, (y >> 2) & 0x3F, 0xF)
        lcd.write(4, 0b11100100, 0xF)       # column 0: rows 0, 1, 2, 3
        lcd.write(4, 0xFFFFFF03, 0xF)       # column 1: low byte only
        W = p9term.LCD_W
        self.assertEqual([lcd.level[(y + r) * W] for r in range(4)],
                         [0, 1, 2, 3])
        self.assertEqual([lcd.level[(y + r) * W + 1] for r in range(4)],
                         [3, 0, 0, 0])
        self.assertEqual(sum(lcd.written), 8)


class TerminalTest(unittest.TestCase):
    """To /boot's prompt at 25 Hz; at the prompt a mouse move of (+100,
    +50), 0.5 s later (-30, +200) with the left button down, 0.5 s later
    the screen."""

    @classmethod
    def setUpClass(cls):
        cls.boot = p9boot.Boot(S9TERM)
        cls.boot.quart.period_override = 0.04
        cls.boot.set_inputs([
            "screen 'il]: ' mouse 100 50",
            "after 0.5 mouse -30 200 L",
            "after 0.5 stop"])
        cls.status = cls.boot.run(60000000)
        cls.info, cls.pix = cls.boot.screen_pixels()

    def test_stopped_by_the_script(self):
        self.assertIn("input script: stop", self.status)
        self.assertEqual([s for s, _c, _l in self.boot.inputs.fired],
                         STEPS["fired"])

    def test_geometry(self):
        info = self.info
        self.assertEqual(info["width"], 48)
        self.assertEqual(info["ldepth"], 1)
        self.assertEqual(info["r"], (0, 0, 768, 1024))
        self.assertEqual(info["size"], (768, 1024))
        self.assertEqual(info["base"], BASE)

    def test_panel_is_the_bitmap(self):
        bad, written = self.boot.panel_check()
        self.assertEqual(bad, 0)
        self.assertGreater(written, 768 * 32)

    def test_mouse(self):
        m = self.boot.syms.by_name["mouse"]
        self.assertEqual(self.boot.mouse_xy(), (70, 250))
        self.assertEqual(self.boot.kernel_word(m + 0x0C), 1)   # buttons
        self.assertEqual(self.boot.quart.ports[3]["received"], 10)

    def test_cursor_moved(self):
        """The arrow (16 x 16 at mouse.xy + (-1, -1)) is drawn there, and
        the screen below the two text lines is background (3) elsewhere."""
        pix, W = self.pix, 768
        box = [pix[y * W + x] for y in range(249, 265) for x in range(69, 85)]
        self.assertIn(0, box)
        self.assertIn(3, box)
        rest = [pix[y * W + x] for y in range(40, 1024) for x in range(W)
                if not (249 <= y < 265 and 69 <= x < 85)]
        self.assertEqual(set(rest), {3})

    def test_checksum(self):
        self.assertEqual(p9boot.screen_digest(self.pix), DIGEST)


class GtextureTest(unittest.TestCase):
    """s9term's own gtexture (0x80035430), called alone on the reference
    model: why 8½'s background and scroll-bar thumbs are white
    (docs/p9boot.md "8½ as `tor`").  The destination is 32 x 4 at
    ldepth 1, the source 8½'s lightgrey texture at ldepth 0 (rows 8 2 8 2,
    as the kernel held them in the live run), f = S.  A 4-pixel-wide
    texture comes out all zero (white): the image replicates the row only
    to 16 bits and then reads its top 16.  The same rows already
    replicated to 32 pixels come out as the grey (a control: the call and
    the reading of the result work)."""

    DST, DB, SRC, SB, STK, RET = (0x80700000, 0x80700100, 0x80700200,
                                  0x80700300, 0x80780000, 0x80004000)

    @classmethod
    def setUpClass(cls):
        cls.boot = p9boot.Boot(S9TERM)

    def gtexture(self, tex_w, rows):
        boot, hs = self.boot, p9boot.hobbit_sem
        put = lambda a, v: boot.board.set_word(a, v & 0xFFFFFFFF)
        for a, base, width, ld, r in (
                (self.DST, self.DB, 2, 1, (0, 0, 32, 4)),
                (self.SRC, self.SB, 1, 0, (0, 0, tex_w, 4))):
            for i, v in enumerate([base, 0, width, ld] + list(r) * 2):
                put(a + 4 * i, v)
        for i in range(8):
            put(self.DB + 4 * i, 0)
        for i, v in enumerate(rows):
            put(self.SB + 4 * i, v)
        for i, v in enumerate([self.RET, self.DST, 0, 0, 32, 4, self.SRC,
                               12]):                    # f = S
            put(self.STK + 4 * i, v)
        st = hs.State(pc=boot.syms.by_name["gtexture"], sp=self.STK,
                      msp=self.STK, psw=0, isp=self.STK, vb=0,
                      config_kl=True, cache=[0] * 64, system=boot.sysm)
        n = 0
        while st.pc != self.RET and n < 100000:
            _rec, st = hs.step(st)
            n += 1
        self.assertEqual(st.pc, self.RET)
        return [boot.board.read(self.DB + 4 * i) for i in range(8)]

    def test_narrow_texture_is_white(self):
        self.assertEqual(self.gtexture(4, (8, 2, 8, 2)), [0] * 8)

    def test_word_wide_texture_is_grey(self):
        # each 1 bit becomes the 2-bit pixel 3 (black): one in four
        self.assertEqual(self.gtexture(32, (0x88888888, 0x22222222) * 2),
                         [0xC0C0C0C0] * 2 + [0x0C0C0C0C] * 2 +
                         [0xC0C0C0C0] * 2 + [0x0C0C0C0C] * 2)


class EightHalfReplayTest(unittest.TestCase):
    """8½ as tor, replayed (docs/p9boot.md "8½ as `tor`").
    tests/net/8half.pcap is the --pcap of the live tools/p9join.py run of
    2026-11-24 (--user tor, --input tests/net/8half.input; the command
    is in the doc), 1311 frames; HALF_INPUT is that run's --input-log less
    its screenshots.  The replay boots s9term from the 1e file server's
    recorded answers, logs in as tor (`password not checked!`), runs
    tor's profile and 8½, and stops where the live run took its
    screenshot `q1`: 8½ settled, 8½start's window with rc's `term% `,
    the background white (s9term's gtexture: GtextureTest).

    P9TERM_8HALF=ls replays the rest of the recording too: button 3's
    menu, a New window swept from (60, 640) to (700, 1000), `ls` typed
    in it, and the screen compared with tests/net/8half_ls.png, the live
    run's last screenshot."""

    FULL = os.environ.get("P9TERM_8HALF") == "ls"

    @classmethod
    def setUpClass(cls):
        cls.boot = p9boot.Boot(S9TERM)
        cls.boot.script = [(b"il]: ", b"\r"), (b"user[none]: ", b"tor\r"),
                           (b"password: ", b"password\r")]
        cls.replay = p9boot.Replay(HALF_PCAP, p9boot.EEPROM_EA)
        cls.boot.attach(p9boot.Wire(cls.boot.sonic.clock,
                                    replay=cls.replay))
        cls.boot.set_inputs(HALF_INPUT if cls.FULL else
                            ["at-cycle %d stop" % HALF["q1"][0]])
        cls.status = cls.boot.run(4000000000)
        cls.info, cls.pix = cls.boot.screen_pixels()
        cls.at = HALF["ls" if cls.FULL else "q1"]

    def test_stopped_by_the_script(self):
        self.assertIn("input script: stop", self.status)
        self.assertEqual((self.boot.cycles, self.boot.steps), self.at[:2])

    def test_every_frame_as_recorded(self):
        self.assertIsNone(self.replay.mismatch)
        self.assertEqual(self.boot.sysm.cret_clamps, 0)
        # the stop at q1 comes 60 s of model time before the next frame
        self.assertEqual(self.replay.pos, 583 if self.FULL else 542)
        self.assertEqual(len(self.replay.steps), 583)

    def test_logged_in_as_tor(self):
        screen = bytes(self.boot.console["screenputs"])
        self.assertIn(b"user[none]: tor\npassword: \n", screen)
        self.assertIn(b"boot: password not checked!", screen)
        self.assertTrue(screen.endswith(b"init: starting /bin/rc\n"))

    def test_panel_is_the_bitmap(self):
        bad, _written = self.boot.panel_check()
        self.assertEqual(bad, 0)

    def test_window(self):
        """8½start's window (0 0 785 602, clipped by the screen): its
        bottom border, y = 601, black from x = 0 to the screen's edge;
        below it white, but for the arrow (and, with `ls`, the new
        window)."""
        pix, W = self.pix, 768
        self.assertEqual(set(pix[601 * W:602 * W]), {3})
        if not self.FULL:
            self.assertEqual(set(pix[602 * W:]), {0})

    def test_checksum(self):
        self.assertEqual(p9boot.screen_digest(self.pix), self.at[2])

    def test_the_live_screenshot(self):
        if not self.FULL:
            self.skipTest("P9TERM_8HALF=ls")
        w, h, grey = read_png(os.path.join(HERE, "net", "8half_ls.png"))
        self.assertEqual((w, h), (768, 1024))
        self.assertEqual(grey, bytes(255 - 85 * v for v in self.pix))


def read_png(path):
    """(w, h, grey bytes) of an 8-bit grey PNG as p9term.write_image
    writes it (filter 0 on every row)."""
    import struct
    import zlib
    with open(path, "rb") as f:
        d = f.read()
    off, idat, w, h = 8, b"", 0, 0
    while off < len(d):
        n, = struct.unpack(">I", d[off:off + 4])
        kind, body = d[off + 4:off + 8], d[off + 8:off + 8 + n]
        if kind == b"IHDR":
            w, h = struct.unpack(">II", body[:8])
        elif kind == b"IDAT":
            idat += body
        off += 12 + n
    raw = zlib.decompress(idat)
    return w, h, b"".join(raw[y * (w + 1) + 1:(y + 1) * (w + 1)]
                          for y in range(h))


HALF_PCAP = os.path.join(HERE, "net", "8half.pcap")
# the live run's --input-log, less its screenshots
HALF_INPUT = [
    "at-cycle 1995163610 move 400 800",
    "at-cycle 2005163610 buttons R",
    "at-cycle 2070787649 buttons -",
    "at-cycle 2132006774 move 60 640",
    "at-cycle 2142006774 buttons R",
    "at-cycle 2152006774 move 700 1000 R",
    "at-cycle 2162006774 buttons -",
    "at-cycle 2774578184 type 'ls\\r'",
    "at-cycle 2988614887 stop"]
# (cycles, steps, sha256 of the pixels) at the live run's q1 and its end
HALF = {"q1": (1391163610, 1388344680,
               "7a182d449ee765366d511f50fca9861cdc070ed44bf9e41ca48881ae932892cb"),
        "ls": (2988614887, 2985469493,
               "a908ac2986d9e6b3457b6d90922a3d8f1a338f8f2b6fb4090e2f0092734d9f63")}

STEPS = {"fired": [22537091, 32506729, 42502279]}
BASE = 0x805B7968       # xalloc(198656) + 2048 (screeninit+0x4c..+0x68)
DIGEST = "183d08cc55bda49eb4fdd3ee7a213b18623a0d70fc18340f1b38a5abe9546eea"


if __name__ == "__main__":
    unittest.main()
