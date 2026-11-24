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
skip), ~1 min.

Discriminating checks, observed 2026-11-24, each injection made in a
scratch copy of tools/p9term.py put first on the path
(build/gfx/inject.py; the real file's sha256 checked unchanged after),
the whole file run:

* buttons sent active high (`0x80 | (down & 7)`): FAIL test_packet,
  test_long_move, test_mouse (mouse.buttons); the screen is unchanged.
* dy not negated (`my = dy`): FAIL test_packet, test_long_move,
  test_mouse ((70, 0): the second move clamped at the top),
  test_cursor_moved, test_checksum, test_stopped_by_the_script (the
  cursor redrawn elsewhere: 32,506,699 instead of 32,506,727).
* the LCD's row-group address shifted 4 bits a write, not 6: FAIL
  test_panel, test_panel_is_the_bitmap.
* the dump's pixels taken from the high bits of a byte first: FAIL
  test_panel_is_the_bitmap, test_cursor_moved, test_checksum.
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


STEPS = {"fired": [22537089, 32506727, 42502277]}
BASE = 0x805B7968       # xalloc(198656) + 2048 (screeninit+0x4c..+0x68)
DIGEST = "183d08cc55bda49eb4fdd3ee7a213b18623a0d70fc18340f1b38a5abe9546eea"


if __name__ == "__main__":
    unittest.main()
