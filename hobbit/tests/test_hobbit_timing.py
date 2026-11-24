#!/usr/bin/env python3
"""Tests for sem/hobbit_timing.py, the timing twin (plan milestone C2).

Two parts:

* every hand-derived golden trace (tests/golden/NNN.trace, `cyc` derived
  by hand from the printed tables before any model ran it): the twin's
  `cyc` equals the trace's on every record, with nothing undetermined;
* synthetic streams, one per rule the twin applies and the one-instruction
  model or the core could get wrong: the fold hosts (p. 4-7, DS pp. 26-27),
  Table 4-35's rows by compare distance for folded and unfolded jumps,
  the jump after a trap's return, KRET as a non-host, a CPU-prefixed host,
  ENTER's E (p. 3-19) and Table 4-34's DQM forms.

The za and zc runs are checked in tests/run_p9host_tests.sh, on the
reference traces that script already makes.

Injected defects (observed 2026-11-24; each put into sem/hobbit_timing.py
alone, the run below, then the patch reversed and `git diff` clean):

  I1 a five-parcel instruction is a fold host
     (`d.host_ok = (n == 3 and ...)` -> `(n in (3, 5) and ...)`):
       FAIL test_five_parcel_host_does_not_fold  AssertionError: 0 != 1
       FAIL test_unfolded_4_or_more              AssertionError: 0 != 1
       and nothing else (the goldens pass: none puts a one-parcel jump
       after a five-parcel instruction).  On za's reference trace:
       224 records "twin 0 trace 1" (JMPTN 135, JMPFN 86, JMPTY 3) --
       cyc_classify's class 1, the core's defect.
  I2 the core's rule, a flat 3 for every mispredicted folded branch
     (`if fold: return 3` ahead of the distance rows in `price`):
       FAIL test_folded_4_or_more             AssertionError: 3 != 0
       FAIL test_folded_mispredict_distances  AssertionError: 3 != 2
       On za: 161 records "twin 3 trace 2" and 77 "twin 3 trace 1" --
       classes 2 and 3.
  I3 a trap record leaves PSW.F's provenance alone (the trap branch of
     `after_record` does not set self.flag):
       FAIL test_jump_after_trap  AssertionError: 3 is not None
       On zc the twin then agrees with the reference on all 1,651,700
       records: the 16 jumps after a trap's return take the reference's 1.
  I4 KRET counted as a fold host (BRANCHING_NILADIC emptied):
       FAIL test_kret_is_not_a_host  AssertionError: 0 != 1
       The s9term boot's first 3,000,000 records do not reach the case
       (no KRET returns to the instruction physically after it).
  I5 the boot record's `I n` keyed as record n, not n - 1 (the fix of
     2026-11-24, `- 1` removed in `load_boot_rec`):
       FAIL test_boot_rec_line_keys_the_interrupted_record
       ({1: ...} != {0: ...}), and nothing else.
"""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HOBBIT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HOBBIT, "sem"))
import hobbit_timing as ht  # noqa: E402

GOLDEN = os.path.join(HERE, "golden")


def board(**over):
    b = ht.read_board(ht.BOARD)
    b.update(over)
    return b


def run(stream, brd=None, words=None, after=None):
    """stream: (pc, parcels, extra) tuples; extra may set sp/msp/we/addr/
    trap.  Returns the twin's (cyc, why, name, folded) per record."""
    brd = brd or board()
    mem = ht.Memory()
    for pc, parcels, _x in stream:
        for k, p in enumerate(parcels):
            a = pc + 2 * k
            w = mem.words.get(a & ~3, 0)
            if a & 2:
                w = (w & 0xFFFF0000) | p
            else:
                w = (w & 0xFFFF) | (p << 16)
            mem.words[a & ~3] = w
    if words:
        mem.words.update(words)
    recs = []
    for pc, parcels, x in stream:
        p = parcels + [0]
        recs.append((pc, (p[0] << 16) | p[1], x.get("sp", 0x100),
                     x.get("spa", x.get("sp", 0x100)), x.get("msp", 0x180),
                     x.get("mspa", x.get("msp", 0x180)), x.get("we", 0),
                     x.get("addr", 0), x.get("data", 0), x.get("mask", 0),
                     x.get("trap", 0), 0))
    return ht.Twin(ht.Rows(ht.TIMING_CSV, brd), brd, mem, after).run(recs)


CMPEQ = 0x4000          # CMPEQ $0,R0   (Table 1-15 0x10)
ADD = 0x5000            # ADD $0,R0     (0x14)
NOP = 0x2C02            # niladic NOP
KRET = 0x2C01
MOV3 = [0x86FD, 0x0001, 0x0004]       # MOV $1,R4, three parcels
MOV5 = [0xC6FD, 0, 1, 0, 4]           # five parcels


def jmp(op, off):
    """One-parcel jump with a 10-bit parcel offset (Table 1-15)."""
    return (op << 10) | (off & 0x3FF)


JMPTN, JMPTY = 0x06, 0x07


class Goldens(unittest.TestCase):
    def test_every_golden(self):
        names = sorted(f[:-6] for f in os.listdir(GOLDEN)
                       if f.endswith(".trace"))
        self.assertGreaterEqual(len(names), 24)
        brd = board()
        for n in names:
            recs = ht.read_trace(os.path.join(GOLDEN, n + ".trace"))
            mem = ht.Memory()
            mem.load_hex(os.path.join(GOLDEN, n + ".hex"))
            out = ht.Twin(ht.Rows(ht.TIMING_CSV, brd), brd, mem).run(recs)
            for i, (rec, (c, why, name, _f)) in enumerate(zip(recs, out)):
                self.assertEqual(c, rec[11], "golden %s record %d %s: %s"
                                 % (n, i, name, why))


class Folding(unittest.TestCase):
    def test_three_parcel_host_folds(self):
        out = run([(0, MOV3, {}), (6, [jmp(JMPTY, 8)], {}),
                   (0x16, [NOP], {})])
        self.assertEqual(out[1][:1] + (out[1][3],), (0, True))

    def test_five_parcel_host_does_not_fold(self):
        # p. 4-7: "a previous one- or three-parcel instruction"
        out = run([(0, MOV5, {}), (10, [jmp(JMPTY, 8)], {}),
                   (0x1a, [NOP], {})])
        self.assertEqual(out[1][0], 1)

    def test_kret_is_not_a_host(self):
        # p. 4-7: a fold pairs a *non-branching* operation with a branch
        out = run([(0, [KRET], {}), (2, [jmp(JMPTY, 8)], {}),
                   (0x12, [NOP], {})])
        self.assertEqual(out[1][0], 1)

    def test_reached_by_transfer_is_unfolded(self):
        # the record before is a taken jump, not the instruction before
        out = run([(0, [ADD], {}), (2, [jmp(JMPTY, 0x10)], {}),
                   (0x22, [jmp(JMPTY, 8)], {}), (0x32, [NOP], {})])
        self.assertEqual([o[0] for o in out[1:3]], [0, 1])

    def test_cpu_prefixed_host(self):
        out = run([(0, [0x2C00] + MOV3, {}), (8, [jmp(JMPTY, 8)], {}),
                   (0x18, [NOP], {})])
        self.assertEqual(out[1][0], 0)
        out = run([(0, [0x2C00] + MOV3, {}), (8, [jmp(JMPTY, 8)], {}),
                   (0x18, [NOP], {})], board(fold_into_cpu_prefixed="no"))
        self.assertEqual(out[1][0], 1)


class Interrupts(unittest.TestCase):
    def test_boot_rec_line_keys_the_interrupted_record(self):
        # `I n level pc`: n records retired, so the interrupt follows
        # record n - 1 (the s9term boot's I 2b78cc is after line 2,848,972)
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".rec",
                                         delete=False) as f:
            f.write("M 0 12345678\nI 1 5 80000100\n")
        try:
            after = ht.Memory().load_boot_rec(f.name)
        finally:
            os.unlink(f.name)
        self.assertEqual(after, {0: 0x80000100})

    def test_no_fold_across_an_interrupt(self):
        # the jump after the interrupted ADD is the handler's successor,
        # not the ADD's, so it is reached by a transfer and does not fold
        out = run([(0, [ADD], {}), (2, [jmp(JMPTY, 8)], {}),
                   (0x12, [NOP], {})], after={0: 2})
        self.assertEqual(out[1][0], 1)
        out = run([(0, [ADD], {}), (2, [jmp(JMPTY, 8)], {}),
                   (0x12, [NOP], {})])
        self.assertEqual(out[1][0], 0)


class Table435(unittest.TestCase):
    def mispredict(self, between, host5=False):
        """CMPEQ, `between` ADDs (or a five-parcel MOV last), then a
        JMPTN that is taken (predicted N: wrong)."""
        s = [(0, [CMPEQ], {})]
        pc = 2
        for _ in range(between - (1 if host5 else 0)):
            s.append((pc, [ADD], {}))
            pc += 2
        if host5:
            s.append((pc, MOV5, {}))
            pc += 10
        s.append((pc, [jmp(JMPTN, 0x20)], {}))
        s.append((pc + 0x40, [NOP], {}))
        return run(s)[-2]

    def test_folded_mispredict_distances(self):
        # folded into the CMPEQ itself, then into an ADD 1 and 2 later
        self.assertEqual(self.mispredict(0)[0], 3)
        self.assertEqual(self.mispredict(1)[0], 2)
        self.assertEqual(self.mispredict(2)[0], 1)
        for b in (0, 1, 2):
            self.assertTrue(self.mispredict(b)[3])

    def test_folded_4_or_more(self):
        self.assertEqual(self.mispredict(3)[0], 0)
        self.assertEqual(self.mispredict(7)[0], 0)

    def test_unfolded_4_or_more(self):
        self.assertEqual(self.mispredict(3, host5=True)[0], 1)

    def test_unfolded_after_compare(self):
        # the five-parcel host is itself 1 back: unfolded, distance 1 -> 2
        self.assertEqual(self.mispredict(1, host5=True)[0], 2)

    def test_jump_after_trap(self):
        # a trap record (the unimplemented sequence; its handler is not in
        # the stream), then the jump after the trapped instruction
        base = [(0, [CMPEQ], {}), (2, [0x8000 | (0x08 << 8), 0, 0],
                                   {"trap": 1, "we": 1, "addr": 0x100,
                                    "mask": 0xF})]
        out = run(base + [(8, [jmp(JMPTN, 0x20)], {}),
                          (0x48, [NOP], {})])
        self.assertEqual(out[1][0], 8)            # 7 + A
        self.assertIsNone(out[2][0])              # flag's provenance unknown
        self.assertFalse(out[2][3])               # reached by KRET: unfolded
        out = run(base + [(8, [jmp(JMPTN, 0x20)], {}), (10, [NOP], {})])
        self.assertEqual(out[2][0], 1)            # correct, unfolded


class Enter(unittest.TestCase):
    def test_enter_stack_offset_flush(self):
        # ENTER R-64 (stk8 field 252): target 0xc0; MSP 0x200 -> 0x1c0
        out = run([(0, [0x0800 | (252 << 2)],
                    {"sp": 0x100, "spa": 0xC0, "msp": 0x200,
                     "mspa": 0x1C0})])
        self.assertEqual(out[0][0], 1 + 4 * 4)

    def test_enter_no_flush(self):
        out = run([(0, [0x0800 | (252 << 2)],
                    {"sp": 0x100, "spa": 0xC0, "msp": 0x180,
                     "mspa": 0x180})])
        self.assertEqual(out[0][0], 1)


class Dqm(unittest.TestCase):
    # A = 2 separates the double-word forms: SC->SC 4, SC/M 2 + D = 6,
    # M->M 2.D = 8, constant to SC 3, constant to M 1 + D = 5.
    B = dict(A=2, D=4, Q=8, S=2)

    def dqm(self, smode, src, dst, words=None, quad=False, **b):
        dmode = 0xE if quad else 0x8
        p0 = 0x8000 | (7 << 8) | (smode << 4) | dmode
        return run([(0, [p0, src, 0x10], {"we": 1, "addr": dst,
                                          "mask": 0xF})],
                   board(**dict(self.B, **b)), words)[0][0]

    def test_forms(self):
        self.assertEqual(self.dqm(0xF, 0, 0x110), 3)       # const -> SC
        self.assertEqual(self.dqm(0xF, 0, 0x400), 5)       # const -> M
        self.assertEqual(self.dqm(0xD, 0x20, 0x110), 4)    # SC -> SC
        self.assertEqual(self.dqm(0xD, 0x20, 0x400), 6)    # SC -> M
        # *R32: the pointer at SP+32 is 0x800, outside the window
        self.assertEqual(self.dqm(0xE, 0x20, 0x400,
                                  {0x120: 0x800}), 8)      # M -> M

    def test_scm_quad_reading(self):
        self.assertEqual(self.dqm(0xD, 0x20, 0x400, quad=True), 4 + 4)
        self.assertEqual(self.dqm(0xD, 0x20, 0x400, quad=True,
                                  dqm_scm_qw="2100"), 4 + 8)

    def test_unknown_pointer_is_undetermined(self):
        self.assertIsNone(self.dqm(0xE, 0x20, 0x400))


if __name__ == "__main__":
    unittest.main()
