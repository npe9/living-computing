#!/usr/bin/env python3
"""tools/beboot.py, the Hobbit BeBox board (docs/bebox_hobbit.md).

Two parts.  The device tests need no image: they pin the board's
registers and the 53C94's sequences to the pages they come from.  The
boot tests run Be's Nov 23 1994 kernel and skip, loudly, with the fetch
command, when the disk image (held out of git: docs/bebox/MANIFEST.md)
is not on disk or not the recorded one.  No byte of Be's software is in
this file: the tests pin console text, step counts and function names.

Discriminating checks, observed 2026-11-24 (each injection one edit to
tools/beboot.py, reverted by the reverse edit; `git diff` clean after):

INJECTIONS
"""
import hashlib
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HOBBIT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HOBBIT, "tools"))
import beboot  # noqa: E402

DISK = os.path.join(HOBBIT, "build", "bebox", "hdd-hobbit-9308000058",
                    "hobbit-9308000058.img")
DISK_SHA256 = "9da58f90498800000dcba8a979f58a040e52ae5921694991fc9317e6e31cc0dc"
FETCH = "sh hobbit/docs/bebox/fetch.sh"


def disk_or_skip():
    if not os.path.exists(DISK):
        raise unittest.SkipTest("SKIPPED: %s is not on disk; run `%s`"
                                % (DISK, FETCH))
    h = hashlib.sha256()
    with open(DISK, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    if h.hexdigest() != DISK_SHA256:
        raise unittest.SkipTest("SKIPPED: %s is not the recorded image "
                                "(sha256 %s)" % (DISK, h.hexdigest()))
    return DISK


class Clock:
    def __init__(self):
        self.t = 0

    def __call__(self):
        return self.t


class BoardTest(unittest.TestCase):
    """Appendix A of the 16 Sep 1993 hardware manual, pages 1-3."""

    def setUp(self):
        self.board = beboot.Board(8 << 20)
        self.regs = beboot.BoardRegs(self.board)
        for n in range(8):
            self.board.io.add(beboot.IO_BASE + 3 + 4 * n, 3, self.regs, n,
                              beboot.BoardRegs.NAMES[n])
        self.board.io.add(0x00800DC3, 3, beboot.WhoAmI(self.board), 0, "who")

    def test_register_lane(self):
        # 0x00800007, CPU 1's I/O mask: bits 7:0 of the word at 0x00800004.
        self.board.write(0x00800004, 0x000000A5, 0x1)
        self.assertEqual(self.regs.io_mask[0], 0xA5)
        self.assertEqual(self.board.read(0x00800004), 0xA5)

    def test_wrong_lane_stops(self):
        with self.assertRaises(beboot.Stop):
            self.board.write(0x00800004, 0xA5000000, 0x8)

    def test_who_am_i(self):
        # Page 2: CBM 4 = CPU 1, 5 = CPU 2; the kernel's _get_cpu_id
        # returns (value & 15) - 4.
        self.board.current_cpu = 1
        self.assertEqual(self.board.read(0x00800DC0) & 15, 4)
        self.board.current_cpu = 2
        self.assertEqual(self.board.read(0x00800DC0) & 15, 5)

    def test_unmodelled_stops_with_the_region(self):
        for pa, region in ((0x00000100, "boot flash"),
                           (0x00801000, "beyond the 4 KB"),
                           (0x60000000, "shadow RAM"),
                           (0x90000000, "slot 2"),
                           (0x00800400, "PC port 0x100")):
            with self.assertRaises(beboot.Stop) as cm:
                self.board.read(pa)
            self.assertIn(region, str(cm.exception))

    def test_ram(self):
        self.board.write(0x08000048, 0x01000000, 0xF)
        self.board.write(0x08000048, 0x00000033, 0x1)
        self.assertEqual(self.board.read(0x08000048), 0x01000033)


class RtcTest(unittest.TestCase):
    def test_vrt_and_bcd_time(self):
        clock = Clock()
        rtc = beboot.Mc146818(clock)
        rtc.write(0, 0x0D)
        self.assertEqual(rtc.read(1), 0x00)     # CHOICES['rtc']: battery dead
        rtc.write(0, 0x00)
        rtc.write(1, 0x59)                      # 59 s, BCD
        clock.t = 2.0
        rtc.write(0, 0x00)
        self.assertEqual(rtc.read(1), 0x01)     # a minute later, 01 s
        rtc.write(0, 0x0D)
        self.assertEqual(rtc.read(1), 0x80)


class Ncr53c94Test(unittest.TestCase):
    """The 53C94 data sheet (Feb 1990): Table 8 p. 18, p. 33."""

    class Disk:
        name = "fake"

        def execute(self, cdb):
            if cdb[0] == 0x08:
                return 0, bytes(range(256)) * 2, 0, None
            return 0, None, 0, None

    def setUp(self):
        self.clock = Clock()
        self.ncr = beboot.Ncr53c94({0: self.Disk()}, 10, self.clock)

    def take_interrupt(self):
        self.clock.t += 10
        st = self.ncr.read(4)
        self.assertTrue(st & 0x80)
        return st, self.ncr.read(5), self.ncr.read(6)

    def test_selection_time_out(self):
        for b in (0, 0, 0, 0, 0, 0):
            self.ncr.write(2, b)
        self.ncr.write(4, 3)                    # nobody at ID 3
        self.ncr.write(3, 0x41)
        st, isr, seq = self.take_interrupt()
        self.assertEqual((isr, seq & 7), (0x20, 0))

    def test_read_through_pseudo_dma(self):
        for b in (0x08, 0, 0, 0, 1, 0):         # READ(6) one block
            self.ncr.write(2, b)
        self.ncr.write(4, 0)
        self.ncr.write(3, 0x41)
        st, isr, seq = self.take_interrupt()
        self.assertEqual((st & 7, isr, seq & 7), (1, 0x18, 4))
        self.ncr.write(0, 0x00)
        self.ncr.write(1, 0x02)                 # 512 bytes
        self.ncr.write(3, 0x90)
        words = [self.ncr.pdma_read() for _ in range(256)]
        self.assertEqual(words[0], 0x0001)
        self.assertEqual(words[255], 0xFEFF)
        st, isr, seq = self.take_interrupt()
        self.assertEqual((st & 0x17, isr), (0x13, 0x10))   # TC zero, status
        self.ncr.write(3, 0x11)                 # initiator command complete
        st, isr, seq = self.take_interrupt()
        self.assertEqual((st & 7, isr), (7, 0x08))
        self.assertEqual((self.ncr.read(2), self.ncr.read(2)), (0, 0))
        self.ncr.write(3, 0x12)                 # message accepted
        st, isr, seq = self.take_interrupt()
        self.assertEqual(isr, 0x20)

    def test_unknown_command_stops(self):
        with self.assertRaises(beboot.Stop):
            self.ncr.write(3, 0x42)             # select with ATN: not used


class Mcs3201Test(unittest.TestCase):
    """The MCS3201 data sheet (Motorola, 1991): sections 5.2-5.6 pp. 12-13,
    7.9-7.12 pp. 23-24.  The sequences are the kernel's _InitDrive and
    _PrepareMedia."""

    def setUp(self):
        self.clock = Clock()
        self.fdc = beboot.Mcs3201({1: {"medium": None, "cyl": 5}},
                                  self.clock)

    def command(self, *bs):
        for b in bs:
            self.assertEqual(self.fdc.read(4) & 0xC0, 0x80)   # _WriteData
            self.fdc.write(5, b)

    def results(self, n):
        out = []
        for _ in range(n):
            self.assertEqual(self.fdc.read(4) & 0xD0, 0xD0)   # _ReadData
            out.append(self.fdc.read(5))
        self.assertEqual(self.fdc.read(4) & 0xD0, 0x80)
        return out

    def test_recalibrate_then_sense(self):
        self.fdc.write(2, 0x2D)                 # motor 1, DMA/INT, drive 1
        self.command(0x03, 0x3F, 0x10)          # SPECIFY SRT 3: 13 ms/step
        self.command(0x07, 0x01)                # RECALIBRATE drive 1
        self.assertEqual(self.fdc.read(4), 0x82)    # RQM, drive 1 busy
        self.clock.t = 5 * 0.013                # five steps, not settled
        self.assertFalse(self.fdc.irq())
        self.clock.t = 5 * 0.013 + 0.001
        self.assertTrue(self.fdc.irq())
        self.command(0x08)                      # SENSE INTERRUPT STATUS
        self.assertFalse(self.fdc.irq())        # p. 23: resets the INT
        self.assertEqual(self.results(2), [0x21, 0])   # SE | drive 1, PCN 0

    def test_interrupt_gated_by_dor(self):
        self.fdc.write(2, 0x25)                 # DMA/INT enable clear
        self.command(0x03, 0x3F, 0x10)
        self.command(0x0F, 0x01, 0x07)          # SEEK drive 1 to 7
        self.clock.t = 1.0
        self.assertTrue(self.fdc.int_line())
        self.assertFalse(self.fdc.irq())
        self.fdc.write(2, 0x2D)
        self.assertTrue(self.fdc.irq())
        self.command(0x08)
        self.assertEqual(self.results(2), [0x21, 7])

    def test_sense_with_nothing_pending_is_invalid(self):
        self.command(0x08)
        self.assertEqual(self.results(1), [0x80])

    def test_no_diskette_sets_disk_change(self):
        self.fdc.write(2, 0x2D)
        self.assertEqual(self.fdc.read(7), 0x80)

    def test_unmodelled_stops(self):
        with self.assertRaises(beboot.Stop):
            self.fdc.write(5, 0xE6)             # READ DATA: no diskette path
        fdc = beboot.Mcs3201({}, self.clock)
        with self.assertRaises(beboot.Stop):
            fdc.write(2, 0x08)                  # DOR bit 2 low: a reset


if __name__ == "__main__":
    unittest.main()
