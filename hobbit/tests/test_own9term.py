#!/usr/bin/env python3
"""Our 9term (the kernel A3 links from the release's sources with the
release's tools, docs/plan9_boot_plan.md) on the reference model, and the
kbd.c scan codes its console is typed in (tools/p9scancode.py,
tools/p9boot.py CHOICES['console-keyboard']).  docs/p9boot.md, "Our 9term".

The image is a build product and is not in git (the repository is public,
and release-derived kernels are not vendored).  It is looked for at
$HOBBIT_9TERM, else build/p9kbuild/9term (where `p9kbuild.py all` and
`link` leave it), and used only if its sha256 is p9kbuild.NINETERM_SHA256.
Without it the image tests are SKIPPED, loudly, with the command that makes
it (about 3 h 15 min on the reference model); EncoderTest always runs.

* EncoderTest: the scan codes against kbd.c's own tables (no image).
* FirstLineTest (~15 s): to pageinit's line, which differs from s9term's
  (3 pages more kernel: 1362 free pages), with kbdinit's Noclick byte on
  Quart channel 2 and nothing on channel 0 (no printq on a ram kernel).
* ReturnTest (~25-55 s): /boot's prompt at the release clockinit's 25 Hz,
  Return typed as scan codes on channel 2, `il` taken (etherattach, the
  SONIC's line).

Discriminating checks, observed 2026-11-24 (each injection one edit in
the working file, reverted by the reverse edit, `git diff` checked):

* p9scancode: a key's release sent without the Up bit (k, k): FAIL
  test_every_press_is_released, test_known_codes, test_round_trip
  (`eecchhoo`).  ReturnTest stays green: /boot takes the first `\\n` and
  the line is drawn before the second matters.
* p9boot: the console-keyboard choice never taken (typing on channel 0,
  as for s9term): FAIL test_the_keyboard_and_no_serial_console (0 != 2),
  test_il_taken ('max-steps': rawkbdputc never gets a code).
* p9scancode: skeymap characters sent without Lshift around them: FAIL
  test_known_codes, test_round_trip (`|` typed as `\\`).
* p9boot: MEMSIZE 16 MB in ppage0: FAIL test_the_line (`2795 free
  pages, 11180K bytes, ...`), test_il_taken (the same line), and
  test_typed_at_the_prompt (step 22,562,886, not 22,515,681; observed
  before the Quart's bids were corrected, which moved the pin by 6).
"""
import hashlib
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HOBBIT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HOBBIT, "tools"))

import p9boot      # noqa: E402
import p9kbuild    # noqa: E402
import p9scancode  # noqa: E402

IMAGE = os.environ.get("HOBBIT_9TERM",
                       os.path.join(HOBBIT, "build", "p9kbuild", "9term"))
BUILD = ("python3 hobbit/tools/p9kbuild.py all --build hobbit/build/p9kbuild"
         "   # ~3 h 15 min; or `link --kgen K` given the kgen products")


def image_ok():
    if not os.path.exists(IMAGE):
        return "no 9term at %s; make it with: %s" % (IMAGE, BUILD)
    with open(IMAGE, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    if digest != p9kbuild.NINETERM_SHA256:
        return "%s has sha256 %s, not the recorded 9term" % (IMAGE, digest)
    return None


WHY = image_ok()
if WHY:
    print("test_own9term: SKIPPING the image tests: " + WHY,
          file=sys.stderr)

LINE = (b"1362 free pages, 5448K bytes, swap 27848K, highwater 272K, "
        b"headroom 340K\n")
PROMPT = b"root is from (il, tcp, incon, 9600, 19200)[il]: "
ETHERLINE = b"sonic ether: 52 54 00 00 0b 0b\n"
# "prompt" re-pinned 22515681 -> 22515687 when the Quart's interrupt bids
# were corrected (docs/devices/README.md; master's p9boot.py still gives
# 22515681, checked 2026-11-24).
STEPS = {"main": 128548, "first-line": 2135886, "prompt": 22515687}


class EncoderTest(unittest.TestCase):
    """kbd.c rawkbdputc's decoding, run backwards over its own tables."""

    @classmethod
    def setUpClass(cls):
        cls.enc = p9scancode.Encoder()
        cls.keymap, cls.skeymap = cls.enc.keymap, cls.enc.skeymap

    def decode(self, codes):
        """rawkbdputc's shift/ctrl handling, enough for typed text."""
        out, shifted, ctrled = [], False, False
        names = self.enc.names
        for code in codes:
            if code in (names["Lshift"], names["Rshift"]):
                shifted = True
            elif code in (names["Lshift"] | 0x80, names["Rshift"] | 0x80):
                shifted = False
            elif code in (names["Lctrl"], names["Rctrl"]):
                ctrled = True
            elif code in (names["Lctrl"] | 0x80, names["Rctrl"] | 0x80):
                ctrled = False
            elif not code & 0x80:
                ch = (self.skeymap if shifted else self.keymap)[code]
                out.append(ch & 0x1f if ctrled else ch)
        return bytes(out)

    def test_tables(self):
        self.assertEqual((len(self.keymap), len(self.skeymap)), (128, 128))
        self.assertEqual(self.keymap[9:12], [ord("q"), ord("a"), ord("s")])
        self.assertEqual(self.skeymap[7], ord("!"))
        self.assertEqual(self.enc.names["Lshift"], 5)

    def test_known_codes(self):
        # keymap[19] 'z', [10] 'a', [82] ' ', [50] '\n'; '|' is skeymap[56].
        self.assertEqual(self.enc.encode(b"za \r"),
                         bytes([19, 0x93, 10, 0x8a, 82, 0xd2, 50, 0xb2]))
        self.assertEqual(self.enc.encode(b"|"),
                         bytes([5, 56, 56 | 0x80, 5 | 0x80]))

    def test_round_trip(self):
        script = (b"echo hello\rls /hobbit | wc\rcat /lib/ndb/local\r"
                  b"cd /usr/none\rza hello.s\rzl hello.z -lc\rls -l\r"
                  b"sum hello.z z.out\rz.out\recho end of script\r"
                  b"ABC ~!@#$%^&*()_+{}:\"<>? \x04")
        self.assertEqual(self.decode(self.enc.encode(script)),
                         script.replace(b"\r", b"\n"))

    def test_every_press_is_released(self):
        codes = self.enc.encode(b"Hello, World|\r")
        downs = [c for c in codes if not c & 0x80]
        ups = [c & 0x7f for c in codes if c & 0x80]
        self.assertEqual(sorted(downs), sorted(ups))


@unittest.skipIf(WHY, WHY)
class FirstLineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.boot = p9boot.Boot(IMAGE)
        cls.boot.until = b"\n"
        cls.status = cls.boot.run(4000000)

    def test_the_line(self):
        self.assertIn("screenputs printed", self.status)
        self.assertEqual(bytes(self.boot.console["screenputs"]), LINE)
        self.assertEqual(self.boot.steps, STEPS["first-line"])
        reached = dict((n, s) for s, n in self.boot.reached)
        self.assertEqual(reached["main"], STEPS["main"])

    def test_the_keyboard_and_no_serial_console(self):
        names = [n for _, n in self.boot.reached]
        self.assertLess(names.index("kbdinit"), names.index("pageinit"))
        self.assertNotIn("bitreverse", names)       # s9term's devbit.c
        self.assertEqual(self.boot.console_channel, 2)
        # kbdinit: eiarawput(portno, Noclick) -- 0x08 on channel 2; ram
        # kernels set no printq, so channel 0 carries nothing.
        self.assertEqual(bytes(self.boot.quart.ports[2]["out"]), b"\x08")
        self.assertEqual(bytes(self.boot.quart.ports[0]["out"]), b"")
        self.assertEqual(self.boot.exceptions, [])
        self.assertEqual(self.boot.interrupts, 0)


@unittest.skipIf(WHY, WHY)
class ReturnTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.boot = p9boot.Boot(IMAGE)
        cls.boot.script = [(b"il]: ", b"\r")]
        cls.boot.until = ETHERLINE
        cls.status = cls.boot.run(60000000)

    def test_typed_at_the_prompt(self):
        self.assertEqual(self.boot.typed, [(STEPS["prompt"], b"il]: ",
                                            b"\r")])

    def test_il_taken(self):
        self.assertIn("screenputs printed", self.status)
        self.assertEqual(bytes(self.boot.console["screenputs"]),
                         LINE + PROMPT + b"\n" + ETHERLINE)
        names = [n for _, n in self.boot.reached]
        self.assertLess(names.index("kbdputc"), names.index("etherattach"))
        # Both codes of the Return key were offered on channel 2, the
        # press was read (the release need not be by the time the line
        # is drawn).
        self.assertGreaterEqual(self.boot.quart.ports[2]["received"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
