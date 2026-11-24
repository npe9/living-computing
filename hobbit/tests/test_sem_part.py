#!/usr/bin/env python3
"""The reference model's part switch: ATT92010 (default) or ATT92020S.

``hobbit_sem.State.part`` selects the part; docs/att92020.md is the
evidence for every difference.  The 92020S differs from the 92010 only
where a source says so -- its JTAG ID -- and is refused
(``hobbit_sem.Unsourced92020``) where no source says what it does:

* the encodings the 92010 leaves unassigned, which is where the 92020's
  Wait For Interrupt (sourced to exist, MPR 7:14 p. 1, encoding unknown)
  must be;
* a FLUSHPBE whose own address and target differ in bit 10, which Be's
  November 1994 kernel avoids on the 020 (_flushpbe_020, _pbe_off,
  _pbe_on), and a FLUSHPBE with a stack-offset-indirect operand, whose
  target address the PRM leaves ambiguous;
* a CONFIG write that sets the 92010's reserved bits 15:0;
* every step, unless the run opts in to the 92010's Chapter 4 timing.

The 92020M and 92020MX are refused outright (multiplexed bus, no timing).

Discriminating checks, observed 2026-11-24.  Each injection was one edit
to ``sem/hobbit_sem.py`` in a scratch copy of sem/ and tests/ (the
regression suite was running in the worktree), this file was run, and
the edit was reverted with ``git apply -R`` of its own patch (``git
diff`` of the copy then empty).  Observed failures, and nothing else:

(a) ``PARTS["92020S"]`` ident 0x0E33D03B -> 0x1000003B: FAIL
    test_92020s_id_is_the_value_bes_kernel_tests.
(b) ``_read_control`` returning ``sysm.ident`` for every part (the two
    92020 lines removed): FAIL test_92020s_id_is_the_value_bes_kernel_tests.
(c) ``_reserved_encoding`` raising plain ``Unsupported`` for the
    92020S too: ERROR test_reserved_niladic_names_wait_for_interrupt
    (the Unsupported escapes assertRaises(Unsourced92020)), FAIL
    test_reserved_one_parcel_opcode_on_92020s,
    test_reserved_monadic_subcode_on_92020s.
(d) the FLUSHPBE check's ``(pc ^ target) >> 10`` changed to ``>> 11``:
    FAIL test_flushpbe_bit_10_mismatch_is_refused_on_92020s.
(e) the FLUSHPBE mode-0xD read of the word removed (the slot's address
    SP+4 used as the target instead): ERROR
    test_flushpbe_matching_bit_10_retires_on_92020s (refused), FAIL
    test_flushpbe_bit_10_mismatch_is_refused_on_92020s (retired).
(f) the timing gate refusing even with the opt-in (``and not
    state.borrow_92010_timing`` removed): ERROR
    test_92020s_id_is_the_value_bes_kernel_tests,
    test_config_reserved_bits_refused_on_92020s,
    test_flushpbe_matching_bit_10_retires_on_92020s; FAIL
    test_golden_traces_identical_under_92020s,
    test_reserved_niladic_names_wait_for_interrupt.  (The tests that
    expect a refusal anyway still passed.)
(f2) the timing gate removed (no refusal without the opt-in): FAIL
    test_92020s_without_timing_opt_in_is_refused.
(g) the CONFIG reserved-bit check removed: FAIL
    test_config_reserved_bits_refused_on_92020s.
(h) ``REFUSED_PARTS`` emptied: FAIL test_92020m_and_mx_are_refused,
    test_cli_refuses_m_and_mx.
(i) the FLUSHPBE mode-0xE refusal removed: FAIL
    test_flushpbe_indirect_operand_is_refused_on_92020s.
(a)-(h) were re-run after (i)'s code was added, with the same results.
"""

import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HOBBIT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HOBBIT, "sem"))
sys.path.insert(0, HERE)

import hobbit_sem as h  # noqa: E402
from test_sem_system import code, machine  # noqa: E402

CPU = 0x2C00
MOV_ID_R4 = [CPU, 0x867D, 0x000A, 0x0004]     # CPU; MOV %ID,R4 (Be's _get_id)
FLUSHPBE_R4 = [0x80DC, 0x0000, 0x0004]        # FLUSHPBE R4 (Be's _flushpbe_ok)


def m020(**kw):
    ram, sysm, st = machine(**kw)
    st.part = "92020S"
    st.borrow_92010_timing = True
    return ram, sysm, st


class DefaultPartTest(unittest.TestCase):
    def test_default_part_is_92010(self):
        self.assertEqual(h.State().part, "92010")
        self.assertFalse(h.State().borrow_92010_timing)

    def test_92010_id_is_mask_two(self):
        # Table 1-4 p. 1-11: version 1 (mask two), part 0, AT&T 0x3B.
        ram, sysm, st = machine()
        code(ram, 0x1000, MOV_ID_R4)
        h.step(st)
        self.assertEqual(ram.m[0x804], 0x1000003B)


class Part92020STest(unittest.TestCase):
    def test_92020s_id_is_the_value_bes_kernel_tests(self):
        # Be's kernels: _main1 compares _get_id()'s result with
        # 0x0e33d03b before "Running on Hobbit 020 processor".
        ram, sysm, st = m020()
        code(ram, 0x1000, MOV_ID_R4)
        h.step(st)
        self.assertEqual(ram.m[0x804], 0x0E33D03B)
        self.assertEqual(ram.m[0x804] & 0xFFF, 0x03B)   # p. 1-11 AT&T code

    def test_92020s_without_timing_opt_in_is_refused(self):
        ram, sysm, st = machine()
        st.part = "92020S"
        code(ram, 0x1000, [0x2C02])                       # NOP
        with self.assertRaises(h.Unsourced92020) as cm:
            h.step(st)
        self.assertIn("timing", cm.exception.reason)
        self.assertEqual(st.pc, 0x1000)

    def test_reserved_niladic_names_wait_for_interrupt(self):
        # Niladic subcode 0x00B: unassigned in Table 1-17 (p. 1-22).
        ram, sysm, st = m020()
        code(ram, 0x1000, [0x2C0B])
        with self.assertRaises(h.Unsourced92020) as cm:
            h.step(st)
        self.assertIn("Wait For Interrupt", cm.exception.reason)
        ram, sysm, st = machine()                         # the 92010: as before
        code(ram, 0x1000, [0x2C0B])
        with self.assertRaises(h.Unsupported) as cm:
            h.step(st)
        self.assertNotIsInstance(cm.exception, h.Unsourced92020)
        self.assertEqual(cm.exception.reason,
                         "unsupported: niladic subcode 0x00b (Table 1-17, "
                         "p. 1-22)")

    def test_reserved_one_parcel_opcode_on_92020s(self):
        for model in (machine, m020):
            ram, sysm, st = model()
            code(ram, 0x1000, [(0x08 << 10) | 0x21])
            with self.assertRaises(h.Unsupported) as cm:
                h.step(st)
            self.assertEqual(isinstance(cm.exception, h.Unsourced92020),
                             model is m020)

    def test_reserved_monadic_subcode_on_92020s(self):
        for model in (machine, m020):
            ram, sysm, st = model()
            code(ram, 0x1000, [0x80DE, 0x0000, 0x0004])
            with self.assertRaises(h.Unsupported) as cm:
                h.step(st)
            self.assertEqual(isinstance(cm.exception, h.Unsourced92020),
                             model is m020)

    def test_flushpbe_matching_bit_10_retires_on_92020s(self):
        # _flushpbe_020 runs FLUSHPBE R20 from 0x80c012c (bit 10 clear)
        # for a target with bit 10 clear, from 0x80c0766 (set) otherwise.
        for pc, target in ((0x1000, 0x2000), (0x1400, 0x2400)):
            ram, sysm, st = m020(pc=pc)
            ram.m[0x804] = target
            code(ram, pc, FLUSHPBE_R4)
            h.step(st)
            self.assertEqual(st.pc, pc + 6)

    def test_flushpbe_bit_10_mismatch_is_refused_on_92020s(self):
        for pc, target in ((0x1000, 0x2400), (0x1400, 0x2000)):
            ram, sysm, st = m020(pc=pc)
            ram.m[0x804] = target
            code(ram, pc, FLUSHPBE_R4)
            with self.assertRaises(h.Unsourced92020):
                h.step(st)
            self.assertEqual(st.pc, pc)
            # The 92010 has no such rule (p. 3-26): it retires.
            ram, sysm, st = machine(pc=pc)
            ram.m[0x804] = target
            code(ram, pc, FLUSHPBE_R4)
            h.step(st)
            self.assertEqual(st.pc, pc + 6)

    def test_flushpbe_indirect_operand_is_refused_on_92020s(self):
        # FLUSHPBE *R4 (0x80EC): Table 3-2 (p. 3-4) and the p. 3-27 note
        # disagree on which address it names, and the 020 rule needs it.
        ram, sysm, st = m020()
        ram.m[0x804] = 0x2000
        code(ram, 0x1000, [0x80EC, 0x0000, 0x0004])
        with self.assertRaises(h.Unsourced92020):
            h.step(st)
        ram, sysm, st = machine()                         # the 92010: no-op
        ram.m[0x804] = 0x2000
        code(ram, 0x1000, [0x80EC, 0x0000, 0x0004])
        h.step(st)
        self.assertEqual(st.pc, 0x1006)

    def test_config_reserved_bits_refused_on_92020s(self):
        # CPU; MOV $0x00010001,%CONFIG.  The 92010 drops bits 15:0
        # (Table 1-2, p. 1-10, "reserved (=0)").
        prog = [CPU, 0xC6F7, 0x0001, 0x0001, 0x0000, 0x0004]
        ram, sysm, st = machine()
        code(ram, 0x1000, prog)
        h.step(st)
        self.assertEqual(sysm.config, 0x00010000)
        ram, sysm, st = m020()
        code(ram, 0x1000, prog)
        with self.assertRaises(h.Unsourced92020):
            h.step(st)
        self.assertEqual((st.pc, sysm.config), (0x1000, 0))
        ram, sysm, st = m020()                            # bits 31:16 only
        code(ram, 0x1000, [CPU, 0xC6F7, 0x0001, 0x0000, 0x0000, 0x0004])
        h.step(st)
        self.assertEqual(sysm.config, 0x00010000)

    def test_92020m_and_mx_are_refused(self):
        for name in ("92020M", "92020MX", "92020", "92030"):
            with self.assertRaises(ValueError):
                h.part_info(name)
            st = h.State(pc=0, sp=0x100, msp=0x180, part=name)
            st.memory[0] = 0x2C020000
            with self.assertRaises(h.Unsupported):
                h.step(st)
        for name in ("92020M", "92020MX"):
            with self.assertRaises(ValueError) as cm:
                h.part_info(name)
            self.assertIn("refused", str(cm.exception))
        self.assertEqual(h.part_info("92020S").pfb_bytes, 6144)
        self.assertEqual(h.part_info("92010").pfb_bytes, 3072)
        self.assertEqual(h.part_info("92020S").stack_cache_bytes, h.SCSIZE)


class GoldenUnderBothPartsTest(unittest.TestCase):
    def test_golden_traces_identical_under_92020s(self):
        # Binary compatibility (MPR 7:14 p. 1; AT&T, 18 Oct 1993): every
        # hand-derived golden program retires identically on both parts
        # (cyc borrowed from the 92010, as the 92020S run must opt in to).
        golden = os.path.join(HERE, "golden")
        sem = os.path.join(HOBBIT, "sem", "hobbit_sem.py")
        names = sorted(f[:-4] for f in os.listdir(golden)
                       if f.endswith(".hex"))
        self.assertGreaterEqual(len(names), 24)
        for n in names:
            args = [sys.executable, sem, "--image",
                    os.path.join(golden, n + ".hex"), "--sp", "0x100",
                    "--msp", "0x180"]
            if n == "017":
                args += ["--psw", "0x8600"]
            base = subprocess.run(args, capture_output=True, text=True)
            alt = subprocess.run(args + ["--part", "92020S",
                                         "--borrow-92010-timing"],
                                 capture_output=True, text=True)
            hri = [l for l in base.stdout.splitlines() if l.startswith("HRI")]
            self.assertTrue(hri, n)
            self.assertEqual(base.stdout, alt.stdout, n)
            with open(os.path.join(golden, n + ".trace")) as f:
                want = [l.strip() for l in f if l.startswith("HRI")]
            self.assertEqual(len(hri), len(want), n)

    def test_cli_refuses_m_and_mx(self):
        sem = os.path.join(HOBBIT, "sem", "hobbit_sem.py")
        img = os.path.join(HERE, "golden", "001.hex")
        for name in ("92020M", "92020MX"):
            r = subprocess.run([sys.executable, sem, "--image", img, "--sp",
                                "0x100", "--msp", "0x180", "--part", name],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 2)
            self.assertIn("refused", r.stderr)


if __name__ == "__main__":
    unittest.main()
