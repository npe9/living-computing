#!/usr/bin/env python3
"""Tests for tools/cyc_classify.py on synthetic HRI pairs.

One synthetic reference/core pair per known class (the three `za`
classes and zc's after-a-trap class), and one pair with a disagreement no
class explains, which must make the tool exit 1.

Injections (observed 2026-11-24, each reverted by its exact reverse):

* `cause()` without the five-parcel clause: test_five_parcel_host fails
  (its record is "unexplained") and test_all_known_classes_exit_0 fails
  (exit 1); the other four pass.
* `T435_INCORRECT = {0: 3, 1: 1, 2: 1}` (distance 1 priced as distance
  2): test_folded_mispredict_dist1 and test_all_known_classes_exit_0
  fail; the other four pass.
* (2026-11-24, when JMP was added) `COND` without 0x03: FAIL
  test_five_parcel_host_unconditional_jmp ("cyc differs on 1" not found
  in "... 0, cyc differs on 0") and FAIL test_all_known_classes_exit_0
  ("cyc differs on 5" not found; 4); the other five pass.  The JMP
  disagreement is then invisible, not "unexplained": this is the gap
  that hid zc's 11,772 JMPs folded into five-parcel hosts.

Revert an injection and then delete `tools/__pycache__/cyc_classify.*`:
the second injection keeps the file's size, and a restore within the
same second is then served from the injected bytecode (it happened
once: the suite failed after a byte-identical restore).
"""

import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "..", "tools"))
import cyc_classify  # noqa: E402


def hri(pc, insn, cyc, trap=0):
    return ("HRI pc=%x insn=%08x sp=1000>1000 msp=1100>1100 we=0 addr=0 "
            "data=0 mask=00 trap=%d cyc=%d" % (pc, insn, trap, cyc))


# (pc, first parcel, ref cyc, core cyc, trap)
FIVE = [(0x100, 0xdffb, 1, 1, 0),          # five-parcel host, 10 bytes
        (0x10a, 0x1801, 1, 0, 0),          # JMPTN, predicted N, not taken
        (0x10c, 0x5043, 1, 1, 0)]
DIST1 = [(0x200, 0x9ff5, 1, 1, 0),         # CMPEQ (three-parcel 0x1f)
         (0x206, 0x5043, 1, 1, 0),         # ADD, one-parcel 0x14: a host
         (0x208, 0x180b, 2, 3, 0),         # JMPTN folded, taken: mispredict
         (0x300, 0x5043, 1, 1, 0)]
DIST2 = [(0x400, 0x9ff5, 1, 1, 0),         # CMPEQ
         (0x406, 0xa3fd, 1, 1, 0),         # three-parcel 0x23
         (0x40c, 0x5043, 1, 1, 0),         # ADD: the host
         (0x40e, 0x1ff7, 1, 3, 0),         # JMPTY folded, not taken
         (0x410, 0x5043, 1, 1, 0)]
TRAP = [(0x500, 0x9ff5, 1, 1, 0),          # CMPEQ, then three others
        (0x506, 0x5043, 1, 1, 0),
        (0x508, 0x5043, 1, 1, 0),
        (0x50a, 0xd9f5, 8, 8, 1),          # an unimplemented five-parcel
        (0x514, 0x1009, 1, 3, 0),          # JMPFN, taken: mispredict
        (0x600, 0x5043, 1, 1, 0)]
FIVE_JMP = [(0x900, 0xdffb, 1, 1, 0),      # five-parcel host
            (0x90a, 0x0c10, 1, 0, 0),      # JMP, folded by the core
            (0x92a, 0x5043, 1, 1, 0)]
ODD = [(0x700, 0x5043, 1, 1, 0),
       (0x702, 0x5043, 1, 1, 0),
       (0x800, 0x1401, 1, 2, 0),           # JMPFY reached by a transfer
       (0x802, 0x5043, 1, 1, 0)]


def run(seq, extra=()):
    with tempfile.TemporaryDirectory() as d:
        r, c = os.path.join(d, "ref.hri"), os.path.join(d, "core.log")
        with open(r, "w") as f:
            f.write("\n".join(hri(pc, p << 16, rc, t)
                              for pc, p, rc, _, t in seq) + "\n")
        with open(c, "w") as f:
            f.write("\n".join(hri(pc, p << 16, cc, t)
                              for pc, p, _, cc, t in seq) + "\n")
        out = io.StringIO()
        with redirect_stdout(out):
            rc = cyc_classify.main([r, c] + list(extra))
        return rc, out.getvalue()


class Classes(unittest.TestCase):
    def test_five_parcel_host(self):
        rc, out = run(FIVE)
        self.assertEqual(rc, 0, out)
        self.assertIn("ref 1 core 0      1  five-parcel host", out)

    def test_five_parcel_host_unconditional_jmp(self):
        rc, out = run(FIVE_JMP)
        self.assertEqual(rc, 0, out)
        self.assertIn("cyc differs on 1", out)
        self.assertIn("ref 1 core 0      1  five-parcel host", out)

    def test_folded_mispredict_dist1(self):
        rc, out = run(DIST1)
        self.assertEqual(rc, 0, out)
        self.assertIn("ref 2 core 3      1  folded mispredict, dist 1", out)

    def test_folded_mispredict_dist2(self):
        rc, out = run(DIST2)
        self.assertEqual(rc, 0, out)
        self.assertIn("ref 1 core 3      1  folded mispredict, dist 2", out)

    def test_after_trap(self):
        rc, out = run(TRAP)
        self.assertEqual(rc, 0, out)
        self.assertIn("after a trap's return", out)

    def test_unexplained_exits_1(self):
        rc, out = run(ODD)
        self.assertEqual(rc, 1, out)
        self.assertIn("unexplained", out)

    def test_all_known_classes_exit_0(self):
        rc, out = run(FIVE + DIST1 + DIST2 + TRAP + FIVE_JMP, ["--all"])
        self.assertEqual(rc, 0, out)
        self.assertIn("cyc differs on 5", out)


if __name__ == "__main__":
    unittest.main()
