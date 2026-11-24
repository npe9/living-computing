#!/usr/bin/env python3
"""tools/p9boot.py boots the shipped kernel image s9term on the reference
model as far as its first console line (docs/p9boot.md).

The run is deterministic: the same instructions, the same order of first
reaches, the same bytes.  This pins the start of the boot -- `_startup`'s
physical-mode set-up and CRET into virtual mode, `main` through
`mmuinit` and `pageinit`, and the line pageinit prints on the screen
(the `screenputs` tap) and on Quart channel 0 (the kernel's printq) --
about 2.6 million instructions, 25-30 s.  The longer run, to the boot
program's prompt, is the recorded command in docs/p9boot.md.

Discriminating checks, observed 2026-11-23 (each injection one edit,
reverted by the reverse edit, the file's sha256 checked equal):

* sem: PX ignored (16-bit absolutes zero-extended): ERROR
  test_milestones_in_order, FAIL test_instruction_count, test_mmu_state,
  test_no_events_before_the_line, test_stops_at_the_first_line (the
  run stops in _startup).
* sem: ``State.csp`` always SP: ERROR test_milestones_in_order, FAIL
  test_instruction_count, test_mmu_state, test_stops_at_the_first_line.
* p9boot: MEMSIZE 16 MB in ppage0: FAIL test_instruction_count,
  test_stops_at_the_first_line (pageinit prints other numbers).

The idle skip (CHOICES['idle-skip']; IdleSkipEquivalenceTest, PromptTest),
observed 2026-11-23, each injection made in a scratch copy of
tools/p9boot.py (the real file untouched):

* skip one lap too many (N = floor(...) + 1, the guard that keeps the
  last skipped lap before the event removed): FAIL test_same_run
  (cycles 3757855 != 3757854), test_prompt (22530558 != 22530554),
  test_mostly_idle.
* retire the skipped laps' cycles but not their instructions (steps not
  advanced): FAIL test_same_run (cycles), test_the_skip_was_taken (1816
  skips, not 7), test_prompt (2957466 instructions).

Not covered by this test (each left it green): the nonpaged STE base
ignored (the kernel's segments are identity-mapped), the stack cache on
with CONFIG.SE = 0, and the Quart sr never showing TxRDY (the UART line
comes after the stop).  test_sem_system.py covers the first two.
"""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HOBBIT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HOBBIT, "tools"))

import p9boot  # noqa: E402

S9TERM = os.path.join(HOBBIT, "tools", "plan9-1e", "hobbit", "s9term")
LINE = (b"1364 free pages, 5456K bytes, swap 27856K, highwater 272K, "
        b"headroom 340K\n")
PROMPT = b"root is from (il, tcp, incon, 9600, 19200)[il]: "


class FirstLineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.boot = p9boot.Boot(S9TERM)
        cls.boot.until = b"\n"
        cls.status = cls.boot.run(4000000)

    def test_stops_at_the_first_line(self):
        self.assertIn("screenputs printed", self.status)
        self.assertEqual(bytes(self.boot.console["screenputs"]), LINE)

    def test_milestones_in_order(self):
        names = [n for _, n in self.boot.reached]
        order = ["_startup", "_virtual", "main", "confinit", "printinit",
                 "eiasetup", "screeninit", "mmuinit", "pageinit", "print",
                 "screenputs"]
        pos = [names.index(n) for n in order]
        self.assertEqual(pos, sorted(pos))
        # _startup is physical; _virtual is the first instruction after
        # the CRET that turns on the MMU (raml.s).
        self.assertEqual(self.boot.reached[0], (0, "_startup"))
        self.assertEqual(self.boot.reached[1], (STEPS["_virtual"],
                                                "_virtual"))
        self.assertEqual(dict((n, s) for s, n in self.boot.reached)["main"],
                         STEPS["main"])

    def test_instruction_count(self):
        self.assertEqual(self.boot.steps, STEPS["first-line"])

    def test_no_events_before_the_line(self):
        self.assertEqual(self.boot.exceptions, [])
        self.assertEqual(self.boot.interrupts, 0)

    def test_mmu_state(self):
        st = self.boot.state
        sysm = self.boot.sysm
        # mmuinit's mmusetstb(PADDR(KSTBADDR)) with STB_C.
        self.assertEqual(sysm.stb, 0x80001800)
        self.assertEqual(sysm.config, 0x003F0000)
        self.assertEqual(st.vb, 0x80000000)
        self.assertTrue(st.psw & p9boot.hobbit_sem.PSW_VIRTUAL)


class IdleSkipEquivalenceTest(unittest.TestCase):
    """CHOICES['idle-skip'] retires whole idle-loop laps without executing
    them; the run must be the run without the skip, instruction for
    instruction.  A counter period of 4 ms puts seven clock interrupts
    into the first 3.4 M instructions (the idle loop starts at ~2.9 M)."""

    @classmethod
    def setUpClass(cls):
        cls.runs = []
        for skip in (False, True):
            boot = p9boot.Boot(S9TERM)
            boot.quart.period_override = 0.004
            boot.idle_skip = skip
            status = boot.run(3400000)
            cls.runs.append((boot, status))

    def summary(self, boot, status):
        st = boot.state
        return dict(status=status, steps=boot.steps, cycles=boot.cycles,
                    pc=st.pc, psw=st.psw, sp=st.sp, isp=st.isp,
                    interrupts=boot.interrupts, exceptions=boot.exceptions,
                    reached=boot.reached, ram=sorted(boot.board.ram.items()),
                    console=dict(boot.console),
                    quart=repr(boot.quart.duarts))

    def test_same_run(self):
        (plain, s0), (skipped, s1) = self.runs
        a, b = self.summary(plain, s0), self.summary(skipped, s1)
        for key in a:
            self.assertEqual(a[key], b[key], key)

    def test_the_skip_was_taken(self):
        plain, skipped = self.runs[0][0], self.runs[1][0]
        self.assertEqual(plain.skipped_steps, 0)
        self.assertEqual(skipped.skips, 7)
        self.assertEqual(skipped.skipped_steps, IDLE["equiv-skipped"])
        self.assertEqual(plain.interrupts, 8)


class PromptTest(unittest.TestCase):
    """To /boot's prompt with the 25 Hz override, in ~30 s with the idle
    skip; the instruction count is the one measured without the skip
    (22,530,554, 6 minutes, docs/p9boot.md, before the skip existed)."""

    @classmethod
    def setUpClass(cls):
        cls.boot = p9boot.Boot(S9TERM)
        cls.boot.quart.period_override = 0.04
        cls.boot.until = b"root is from"
        cls.status = cls.boot.run(30000000)

    def test_prompt(self):
        self.assertIn("screenputs printed", self.status)
        self.assertEqual(self.boot.steps, STEPS["prompt"])
        self.assertEqual(self.boot.cycles, IDLE["prompt-cycles"])
        self.assertEqual(self.boot.interrupts, 26)
        self.assertEqual(bytes(self.boot.console["screenputs"]),
                         LINE + PROMPT)

    def test_mostly_idle(self):
        self.assertEqual(self.boot.skipped_steps, IDLE["prompt-skipped"])


STEPS = {"_virtual": 2064, "main": 125203, "first-line": 2131084,
         "prompt": 22530554}
IDLE = {"equiv-skipped": 490000, "prompt-skipped": 19573088,
        "prompt-cycles": 22890723}


if __name__ == "__main__":
    unittest.main()
