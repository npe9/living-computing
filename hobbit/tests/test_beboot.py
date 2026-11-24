#!/usr/bin/env python3
"""tools/beboot.py, the Hobbit BeBox board (docs/bebox_hobbit.md).

Two parts.  The device tests need no image: they pin the board's
registers and the 53C94's sequences to the pages they come from.  The
boot tests run Be's Nov 23 1994 kernel and skip, loudly, with the fetch
command, when the disk image (held out of git: docs/bebox/MANIFEST.md)
is not on disk or not the recorded one.  No Be code or data is in this
file; the tests pin the kernel's console lines (short quotations of its
messages), step counts and function names.

Discriminating checks, observed 2026-11-24 (each injection one edit to
tools/beboot.py, reverted by the reverse edit, the file compared byte for
byte with a copy taken before; the default tests, BEBOOT_LONG unset):

- WhoAmI returns 4 + current_cpu (CPU 1 reads 5): test_who_am_i,
  BootTest.test_banner, test_cpu2_started, test_scsi_initialised,
  test_steps.
- SER1/SER2 interrupt bits swapped back to the 1993 draft's order:
  BootTest.test_interrupt_wiring.
- 53C94 selection completes with interrupt 0x08 instead of 0x18 (no bus
  service bit): test_read_through_pseudo_dma only (the kernel's boot to
  "Disk cache is" does not tell them apart).
- ScsiDisk answers every LUN as LUN 0: test_other_luns,
  BootTest.test_banner, test_steps (the console lists LUNs 1-7).
- MCS3201 seek-end ST0 without the drive number: test_recalibrate_then_
  sense, test_interrupt_gated_by_dor.
- I/O window accepts a store on any lane: test_wrong_lane_stops.
- Keyboard controller self test answers 0x54: test_kb_init.
- A read of the IIR does not clear the THRE interrupt: test_thre_interrupt.
- Display card (TridentVga), each failing only the named tests:
  3DA read not resetting the attribute flip-flop: test_attribute_flip_flop;
  the DAC index not advancing after blue: test_dac_write_auto_increments;
  engine registers read big-endian: test_fill, test_overlapping_blit_down,
  test_overlapping_blit_right (errors: the linear/x-y check stops);
  an upward blit copied top row first: test_overlapping_blit_down;
  reading index 0Bh not selecting the new-mode registers:
  test_old_and_new_mode_registers; the board ignoring the read lanes
  (every port of the word read): test_port_is_the_byte,
  test_old_and_new_mode_registers, test_attribute_flip_flop (errors: the
  unmodelled neighbour port stops); the DAC read as 6-bit (x4):
  test_screen_png, test_screen_paging_mode_doubles_the_pitch; paging
  mode ignored: test_screen_paging_mode_doubles_the_pitch.
- Processor reset register accepting bit 7 as well as the DSP bits, or
  not logging a DSP's release: test_dsp_reset_bits_are_kept only.
- DSP emulation hooks (CHOICES['dsp'] emulated, DspEmulationTest with
  FakeDsp), each failing only the named tests: the shadow RAM not aliased
  to RAM: test_shadow_ram_is_low_ram (error); little-endian lanes on the
  DSP bus: test_shadow_ram_is_low_ram, test_dsp_reaches_the_board_
  registers; no on-chip check: test_off_window_stops_name_the_dsp; the
  interrupt bits not forwarded: test_interrupt_is_a_level; one DSP clock
  per cycle: test_release_starts_at_the_cpu_time, test_two_dsp_clocks_
  per_cpu_cycle; no idle-skip guard: test_no_idle_skip_while_a_dsp_runs;
  release() or hold() not called: test_release_and_hold; an emulator
  exception not wrapped: test_emulator_error_is_a_dsp_stop (error); a
  release starting at clock 0: test_release_starts_at_the_cpu_time; Who
  Am I giving the CPU number to a DSP: test_dsp_reaches_the_board_
  registers; inert mode creating DSPs: test_inert_creates_nothing; an
  idle DSP stepped: test_idle_dsp_jumps_to_the_cpu_time; idle DSPs
  counted busy: that test and test_no_idle_skip_while_a_dsp_runs; the
  outside-window log dropped: test_dsp_reaches_the_board_registers; a
  stop without the access: test_off_window_stops_name_the_dsp.
- With BEBOOT_LONG=1, the idle skip leaving R16 of _null_thread unchanged:
  MountTest.test_idle_skip_changes_nothing only (MountTest's header).
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

    def test_dsp_reset_bits_are_kept(self):
        # Page 2: reset register bits 6..4 = DSP3..1 (vcas_server's
        # _veDspStart ORs 0x10 in for DSP1).  CHOICES['dsp']: kept, logged,
        # nothing runs.  A bit the page does not name stops.
        self.board.write(0x00800018, 0x00000012, 0x1)
        self.assertEqual(self.regs.reset, 0x12)
        self.assertEqual(self.regs.dsp_log, [(1, True)])
        self.board.write(0x00800018, 0x00000002, 0x1)
        self.assertEqual(self.regs.dsp_log, [(1, True), (1, False)])
        with self.assertRaises(beboot.Stop):
            self.board.write(0x00800018, 0x00000082, 0x1)

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


BANNER = (b"\n\rBe Labradors Kernel version of Nov 23 1994 time 12:11:01\n\r"
          b"(C) Copyright, Be Incorporated, 1991-1994\n\r\n\r"
          b"Kernel running from RAM in MULTIPROCESSOR mode\n\r"
          b"01000000 bytes of RAM (16 MBytes)\n\r")


# Instructions executed (both CPUs, skipped idle laps included) when the
# text appears on SER1, observed 2026-11-24.
STEPS = {"cache": 6081674, "mount": 29180553}
SCAN = (b"starting cpu 1\n\rpath 0 target 0 lun 0 inqdata "
        b"'BEBOOT  HOBBIT DISK     1994'\n\rDisk cache is")
NO_DISKETTE = (b"DiskChanged returned TRUE\n\r"
               b"PrepareMedia: DiskChanged TRUE twice (i.e. no disk in drive)\n\r"
               b"flo_read: err was -27\n\rReadPhySector -1\n\r")
MOUNT = (SCAN + b" 4096K bytes\n\rRecal floppy drive 1, attempt 1\n\r"
         + NO_DISKETTE + b"fsmount failure\n\r" + NO_DISKETTE
         + b"Cache I/O error\n\r" + NO_DISKETTE
         + b"Volume 'be' w/size 332487 sectors mounted as id 0 on "
           b"/dev/scsi_disk_driver_000")


class FakeElf:
    """Just enough of a kernel ELF for a Machine with no code in RAM."""
    blob = b""
    entry = 0x08001000
    sections = {".text": (0, 0, 0, 0x08001000, 0, 0x10)}

    def words(self):
        return {}

    def func(self, pc):
        return "fake", 0

    def where(self, pc):
        return "fake+0x%x" % pc


class FakeDsp:
    """A stand-in for tools/dsp3210.py's Dsp3210: each step runs the next
    scripted bus operation and takes `clocks` DSP clocks."""

    def __init__(self, n, bus):
        self.n, self.bus = n, bus
        self.pc = 0x60000000
        self.log = []
        self.irq = None
        self.ops = []
        self.steps = 0
        self.clocks = 1
        self.idle = False

    def release(self):
        self.log.append("release")

    def hold(self):
        self.log.append("hold")

    def set_interrupt(self, level):
        self.irq = level

    def step(self):
        if self.ops:
            self.ops.pop(0)(self.bus)
        self.steps += 1
        return self.clocks


class DspEmulationTest(unittest.TestCase):
    """CHOICES['dsp'] emulated, with FakeDsp: the board side only."""

    RESET, INTERNAL = 0x00800018, 0x0080001C    # words of 0x80001B, 0x80001F

    def setUp(self):
        self.m = beboot.Machine(FakeElf())
        self.m.dsp_mode = "emulated"
        self.m.dsp_class = FakeDsp

    def reset(self, value):
        self.m.board.write(self.RESET, value, 0x1)

    def internal(self, value):
        self.m.board.write(self.INTERNAL, value, 0x1)

    def test_release_and_hold(self):
        self.reset(0x10)
        d = self.m.dsps[1]
        self.assertEqual((d.n, d.log), (1, ["release"]))
        self.assertEqual(self.m.dsps_running(), [1])
        self.reset(0x00)
        self.assertEqual(d.log, ["release", "hold"])
        self.assertEqual(self.m.dsps_running(), [])
        self.reset(0x50)                        # DSP1 again, and DSP3
        self.assertIs(self.m.dsps[1], d)
        self.assertEqual(d.log, ["release", "hold", "release"])
        self.assertEqual(self.m.dsps_running(), [1, 3])

    def test_inert_creates_nothing(self):
        self.m.dsp_mode = "inert"
        self.reset(0x70)
        self.assertEqual(self.m.dsps, {})
        self.assertEqual(self.m.regs.reset, 0x70)

    def test_shadow_ram_is_low_ram(self):
        self.reset(0x10)
        bus = self.m.dsps[1].bus
        bus.write(0x60000010, 0xDEADBEEF, 4)
        self.assertEqual(self.m.board.ram[0x08000010], 0xDEADBEEF)
        bus.write(0x60000013, 0x55, 1)          # big-endian: bits 7:0
        bus.write(0x60000010, 0x1234, 2)        # bits 31:16
        self.assertEqual(self.m.board.ram[0x08000010], 0x1234BE55)
        self.assertEqual(bus.read(0x60000010, 1), 0x12)
        self.assertEqual(bus.read(0x60000012, 2), 0xBE55)
        bus.write(0x601FFFFC, 7, 4)
        self.assertEqual(self.m.board.ram[0x081FFFFC], 7)
        with self.assertRaises(beboot.DspStop):
            bus.read(0x60200000, 4)             # past the 2 MB

    def test_off_window_stops_name_the_dsp(self):
        self.reset(0x20)
        bus = self.m.dsps[2].bus
        for f, says in (
                (lambda: bus.read(0x0000E000, 4), "on-chip"),
                (lambda: bus.write(0x50000000, 0x1234, 2),
                 "write of size 2 value 0x1234 at 0x50000000: nothing "
                 "modelled"),
                (lambda: bus.write(0x60000001, 0, 2), "aligned"),
                (lambda: bus.pins("bio0", 1), "bio0")):
            with self.assertRaises(beboot.DspStop) as cm:
                f()
            self.assertEqual(cm.exception.n, 2)
            self.assertIn("DSP2 at pc 60000000", str(cm.exception))
            self.assertIn(says, str(cm.exception))
        self.assertIsNone(self.m.board.dsp_master)

    def test_interrupt_is_a_level(self):
        self.internal(0x10)                     # before release
        self.reset(0x10)
        d = self.m.dsps[1]
        self.assertIs(d.irq, True)
        self.internal(0x30)
        self.assertIs(d.irq, True)
        self.internal(0x00)
        self.assertIs(d.irq, False)
        self.assertEqual(self.m.regs.internal, 0)

    def test_dsp_reaches_the_board_registers(self):
        # Appendix A page 4: from 0x10000 up is Be machine memory, so the
        # internal interrupt register is at its own address.
        self.reset(0x40)
        bus = self.m.dsps[3].bus
        self.assertEqual(bus.read(0x00800DC3, 1) & 15, 3)    # Who Am I
        bus.write(0x0080001F, 0x01, 1)                       # Hobbit A
        self.assertEqual(self.m.regs.internal, 0x01)
        self.assertEqual(dict(bus.outside), {("read", 1, 0x00800DC3): 1,
                                             ("write", 1, 0x0080001F): 1})

    def test_two_dsp_clocks_per_cpu_cycle(self):
        self.reset(0x30)
        self.m.dsps[2].clocks = 3
        self.m.cpus[0].cycles = 10
        self.m.step_dsps()
        self.assertEqual((self.m.dsps[1].steps, self.m.dsp_clock[1]), (20, 20))
        self.assertEqual((self.m.dsps[2].steps, self.m.dsp_clock[2]), (7, 21))
        self.reset(0x10)                        # DSP2 held: it stops
        self.m.cpus[0].cycles = 20
        self.m.step_dsps()
        self.assertEqual(self.m.dsp_clock[1], 40)
        self.assertEqual(self.m.dsp_clock[2], 21)

    def test_idle_dsp_jumps_to_the_cpu_time(self):
        self.reset(0x10)
        d = self.m.dsps[1]
        d.idle = True
        self.m.cpus[0].cycles = 1000
        self.m.step_dsps()
        self.assertEqual((d.steps, self.m.dsp_clock[1]), (0, 2000))
        self.assertEqual(self.m.dsp_idle_clocks[1], 2000)
        self.assertEqual(self.m.dsps_busy(), [])
        d.idle = False
        self.assertEqual(self.m.dsps_busy(), [1])

    def test_release_starts_at_the_cpu_time(self):
        self.m.cpus[0].cycles = 100
        self.reset(0x10)
        self.assertEqual(self.m.dsp_clock[1], 200)

    def test_emulator_error_is_a_dsp_stop(self):
        self.reset(0x10)
        d = self.m.dsps[1]

        def bad(bus):
            raise RuntimeError("opcode 0x12345678 not implemented")
        d.ops.append(bad)
        self.m.cpus[0].cycles = 1
        with self.assertRaises(beboot.DspStop) as cm:
            self.m.step_dsps()
        self.assertEqual(cm.exception.n, 1)
        self.assertIn("RuntimeError: opcode", str(cm.exception))

    def test_no_idle_skip_while_a_dsp_runs(self):
        cpu = self.m.cpus[0]
        called = []

        def next_event():
            called.append(1)
            return None
        self.m.next_event = next_event
        for running, idle in ((False, False), (True, False), (True, True)):
            self.reset(0x10 if running else 0x00)
            if running:
                self.m.dsps[1].idle = idle
            running = running and not idle
            here = (cpu.steps, cpu.cycles, cpu.sysm.timer1, cpu.sysm.timer2)
            lap = (5, 10, 10, 10)
            cpu.idle_last = (tuple(h - d for h, d in zip(here, lap)), lap,
                             True)
            del called[:]
            self.assertEqual(self.m.try_idle_skip(cpu, 1000), 0)
            # A steady lap reaches the event horizon unless a DSP runs.
            self.assertEqual(called, [] if running else [1])


def boot_machine(skip=True):
    import befs1
    import beelf
    vol = befs1.Volume(disk_or_skip())
    work = os.path.join(HOBBIT, "build", "bebox", "beboot")
    os.makedirs(work, exist_ok=True)
    path = os.path.join(work, "kernel-test")
    with open(path, "wb") as f:
        f.write(vol.read(vol.lookup("/system/kernel")))
    vol.f.close()
    m = beboot.Machine(beelf.Elf(path))
    m.disks[0] = beboot.ScsiDisk(DISK, "target 0")
    m.idle_skip = skip
    return m


class UartTest(unittest.TestCase):
    """VL16C452 pp. 6-57..6-60: the THRE interrupt."""

    def test_thre_interrupt(self):
        u = beboot.Uart("t")
        u.write(4, 0x08)                        # OUT2: INT enabled
        self.assertFalse(u.irq())
        u.write(1, 0x02)                        # ETBEI with the THR empty
        self.assertTrue(u.irq())
        self.assertEqual(u.read(2), 0x02)       # IIR: THRE ...
        self.assertFalse(u.irq())               # ... which clears it
        self.assertEqual(u.read(2), 0x01)
        u.write(0, 0x41)                        # a byte: THR empties again
        self.assertTrue(u.irq())
        u.write(4, 0x00)                        # OUT2 low gates INT
        self.assertFalse(u.irq())
        self.assertEqual(bytes(u.out), b"A")


class KeyboardControllerTest(unittest.TestCase):
    """VL82C106 pp. 6-197..6-202; the sequences of _kb_init and
    _mouse_init."""

    def setUp(self):
        self.kbc = beboot.Vl82c106Kbc()

    def answer(self):
        self.assertTrue(self.kbc.read(4) & 1)           # OBF
        return self.kbc.read(0)

    def test_kb_init(self):
        k = self.kbc
        k.write(4, 0xAA)
        self.assertEqual(self.answer(), 0x55)
        k.write(4, 0xAB)
        self.assertEqual(self.answer(), 0x00)
        k.write(4, 0xAE)
        k.write(0, 0xEE)
        self.assertEqual(self.answer(), 0xEE)
        k.write(0, 0xED)
        self.assertEqual(self.answer(), 0xFA)
        k.write(0, 0x02)
        self.assertEqual(self.answer(), 0xFA)
        self.assertFalse(k.read(4) & 1)

    def test_mode_and_interrupts(self):
        k = self.kbc
        k.write(4, 0x60)
        k.write(0, 0x41)                        # EKI, KCC
        k.write(4, 0x20)
        self.assertTrue(k.kbd_irq())            # mode byte in the buffer
        self.assertFalse(k.mouse_irq())
        self.assertEqual(k.read(0), 0x41)
        self.assertFalse(k.kbd_irq())

    def test_mouse(self):
        k = self.kbc
        k.write(4, 0x60)
        k.write(0, 0x02)                        # EMI only
        k.write(4, 0xD4)
        k.write(0, 0xF2)                        # READ ID
        self.assertEqual(k.read(4) & 0x21, 0x21)    # OBF, from the mouse
        self.assertTrue(k.mouse_irq())
        self.assertEqual((k.read(0), k.read(0)), (0xFA, 0x00))

    def test_unmodelled_stops(self):
        with self.assertRaises(beboot.Stop):
            self.kbc.write(4, 0xC0)             # read input port


class TridentVgaTest(unittest.TestCase):
    """The display card's register file (VGADOC TRIDENT.TXT for the
    Trident registers, the IBM VGA layout for the rest) and the old
    graphics engine as app_server's driver programs it (XFree86
    trident_regs.h for the register names; docs/bebox_hobbit.md "The
    display card")."""

    REGS = 0xD1000000

    def setUp(self):
        self.board = beboot.Board(8 << 20)
        self.clock = Clock()
        self.vga = self.board.vga = beboot.TridentVga(self.clock)

    def out(self, port, value):
        """A byte store to VGA port ``port``, as app_server's _t_* helpers
        do it: the byte at 0xD1000000 + port."""
        lane = port & 3
        self.board.write(self.REGS + port, value << (8 * (3 - lane)),
                         beboot.lane_mask(lane))

    def inp(self, port):
        lane = port & 3
        self.board.read_mask = beboot.lane_mask(lane)
        try:
            return (self.board.read(self.REGS + port) >> (8 * (3 - lane))) & 0xFF
        finally:
            self.board.read_mask = 0xF

    def ge(self, index, value):
        """_write_long: the index byte to 0xD100217A, then the value with
        its bytes reversed as one word to 0xD100217C, so the card's
        little-endian register gets its low byte first."""
        self.out(0x217A, index)
        self.board.write(self.REGS + 0x217C,
                         int.from_bytes(value.to_bytes(4, "little"), "big"),
                         0xF)

    def test_port_is_the_byte(self):
        self.out(0x3C3, 1)
        self.assertEqual(self.vga.enable, 1)
        self.out(0x3D4, 0x13)
        self.out(0x3D5, 0x64)
        self.assertEqual(self.vga.crtc[0x13], 0x64)
        self.assertEqual(self.inp(0x3D5), 0x64)
        self.assertEqual(self.inp(0x3D4), 0x13)

    def test_old_and_new_mode_registers(self):
        # VGADOC: writing index 0Bh selects the old mode registers,
        # reading it selects the new ones and returns the chip version.
        self.out(0x3C4, 0x0B)
        self.out(0x3C5, 0)
        self.out(0x3C4, 0x0D)
        self.out(0x3C5, 0x38)
        self.assertEqual(self.vga.old_mode[0x0D], 0x38)
        self.assertEqual(self.vga.seq[0x0D], 0)
        self.out(0x3C4, 0x0B)
        self.assertEqual(self.inp(0x3C5), beboot.TRIDENT_ID)
        self.out(0x3C4, 0x0D)
        self.out(0x3C5, 0x01)
        self.assertEqual(self.vga.seq[0x0D], 0x01)
        self.assertEqual(self.vga.old_mode[0x0D], 0x38)

    def test_attribute_flip_flop(self):
        self.out(0x3D4, 0x00)
        self.out(0x3D5, 0x7E)
        self.out(0x3D4, 0x06)
        self.out(0x3D5, 0x99)
        self.inp(0x3DA)                 # resets the flip-flop
        self.out(0x3C0, 0x10)
        self.out(0x3C0, 0x41)
        self.out(0x3C0, 0x11)
        self.out(0x3C0, 0x00)
        self.assertEqual(self.vga.attr[0x10], 0x41)
        self.out(0x3C0, 0x20)           # index with palette access off
        self.assertEqual(self.vga.attr_index, 0x20)
        self.inp(0x3DA)
        self.assertFalse(self.vga.attr_flip)

    def test_dac_write_auto_increments(self):
        self.out(0x3C8, 254)
        for v in (1, 2, 3, 4, 5, 6):
            self.out(0x3C9, v)
        self.assertEqual(self.vga.dac[254], [1, 2, 3])
        self.assertEqual(self.vga.dac[255], [4, 5, 6])

    def setup_engine(self):
        self.ge(0xB8, (599 << 16) | 799)    # MWIDTH: pitch 800
        self.ge(0xBC, 3)
        self.ge(0x98, (599 << 16) | 799)
        self.ge(0x9C, 3)

    def test_fill(self):
        self.setup_engine()
        self.ge(0xF8, (2 << 16) | 5)        # x 5, y 2
        self.ge(0xE4, 2 * 800 + 5)
        self.ge(0xE0, (1 << 16) | 3)        # 4 wide, 2 high
        self.ge(0xC8, 0x303)
        self.ge(0xD8, 0x2A)
        self.ge(0xDC, 0x2A)
        self.ge(0xC4, 0xFFFF)
        self.ge(0xFC, 0x0A000000)
        fb = self.vga.fb
        self.assertEqual(fb[2 * 800 + 4:2 * 800 + 10], b"\0" + b"\x2a" * 4 + b"\0")
        self.assertEqual(fb[3 * 800 + 5:3 * 800 + 9], b"\x2a" * 4)
        self.assertEqual(fb[4 * 800 + 5], 0)
        self.assertEqual(fb[1 * 800 + 5], 0)
        # Status (index 0x90) reads idle: _wait_graphic_engine's word
        # read of 0xD100217C, bit 31.
        self.out(0x217A, 0x90)
        self.assertEqual(self.board.read(self.REGS + 0x217C) & 0x80000000, 0)

    def blit(self, sx, sy, dx, dy, w, h, d, src=None, dest=None):
        """As _tri_blit1 programs it: direction d, start corners."""
        xneg, yneg = d in (4, 7), d in (2, 7)
        corner = lambda x, y: ((y + (h - 1 if yneg else 0)) * 800 +
                               x + (w - 1 if xneg else 0))
        self.ge(0xF0, (sy << 16) | sx)
        self.ge(0xE8, corner(sx, sy) if src is None else src)
        self.ge(0xF8, (dy << 16) | dx)
        self.ge(0xE4, corner(dx, dy) if dest is None else dest)
        self.ge(0xE0, ((h - 1) << 16) | (w - 1))
        self.ge(0xC8, 3)
        self.ge(0xFC, 0xA8000000 | d)

    def test_overlapping_blit_down(self):
        # Rows 0-2 copied one row down, bottom row first (direction 2),
        # as copy_to_hidden moves the screen: an overlapping copy that
        # must read each source row before it is overwritten.
        self.setup_engine()
        fb = self.vga.fb
        for y in range(3):
            fb[y * 800:y * 800 + 4] = bytes([y + 1]) * 4
        self.blit(0, 0, 0, 1, 4, 3, 2)
        self.assertEqual([fb[y * 800] for y in range(4)], [1, 1, 2, 3])

    def test_overlapping_blit_right(self):
        self.setup_engine()
        fb = self.vga.fb
        fb[0:4] = b"\x01\x02\x03\x04"
        self.blit(0, 0, 2, 0, 4, 1, 4)
        self.assertEqual(fb[0:6], b"\x01\x02\x01\x02\x03\x04")

    def test_blit_with_inconsistent_addresses_stops(self):
        self.setup_engine()
        with self.assertRaises(beboot.Stop):
            self.blit(0, 0, 0, 1, 4, 3, 2, src=0)     # top corner, not bottom

    def test_unmodelled_stops(self):
        for action in (lambda: self.out(0x3D7, 1),           # enhancement
                       lambda: self.out(0x3B4, 1),           # mono CRTC
                       lambda: self.ge(0x80, 1),             # unnamed index
                       lambda: self.ge(0xFC, 0x12345678)):   # other command
            with self.assertRaises(beboot.Stop):
                self.setup_engine()
                action()
        self.out(0x217A, 0x94)
        with self.assertRaises(beboot.Stop):
            self.board.read(self.REGS + 0x217C)
        with self.assertRaises(beboot.Stop):
            self.board.read(0xD0100000)                  # past 1 MB

    def test_screen_png(self):
        import zlib
        for i, v in ((0x01, 1), (0x07, 0), (0x12, 1), (0x13, 2),
                     (0x14, 0x40), (0x0C, 0), (0x0D, 0)):
            self.out(0x3D4, i)
            self.out(0x3D5, v)
        self.out(0x3C8, 7)
        for v in (255, 0, 0xDD):
            self.out(0x3C9, v)
        self.board.write(0xD0000000, 0x07000000, 0xF)    # pixel (0,0) = 7
        png = self.vga.png()
        self.assertEqual(png[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(png[16:24], (16).to_bytes(4, "big") +
                         (2).to_bytes(4, "big"))
        n = int.from_bytes(png[33:37], "big")
        raw = zlib.decompress(png[41:41 + n])
        self.assertEqual(len(raw), 2 * (1 + 16 * 3))
        self.assertEqual(raw[:7], b"\0" + bytes([255, 0, 0xDD]) + b"\0\0\0")

    def test_screen_paging_mode_doubles_the_pitch(self):
        # VGADOC, old mode control 2 bit 4: the CRTC offset counts double.
        # app_server sets it (old 0Dh = 0x38) with CR13 = 50 for 800 bytes.
        import zlib
        self.out(0x3C4, 0x0B)
        self.out(0x3C5, 0)
        self.out(0x3C4, 0x0D)
        self.out(0x3C5, 0x10)
        for i, v in ((0x01, 1), (0x07, 0), (0x12, 1), (0x13, 1),
                     (0x14, 0x40)):
            self.out(0x3D4, i)
            self.out(0x3D5, v)
        self.out(0x3C8, 5)
        for v in (1, 2, 3):
            self.out(0x3C9, v)
        self.vga.fb[16] = 5                  # row 1, pitch 16 not 8
        png = self.vga.png()
        n = int.from_bytes(png[33:37], "big")
        raw = zlib.decompress(png[41:41 + n])
        self.assertEqual(raw[49:53], b"\0\x01\x02\x03")


class ScsiDiskLunTest(unittest.TestCase):
    """CHOICES['disks']: one LUN; LUNs 1-7 answer as SCSI-2 has it."""

    def setUp(self):
        import tempfile
        self.f = tempfile.NamedTemporaryFile()
        self.f.write(bytes(512 * 4))
        self.f.flush()
        self.disk = beboot.ScsiDisk(self.f.name, "t")

    def tearDown(self):
        self.disk.f.close()
        self.f.close()

    def test_lun0_inquiry(self):
        st, data, _, _ = self.disk.execute(bytes([0x12, 0, 0, 0, 36, 0]))
        self.assertEqual((st, data[0], data[8:14]), (0, 0, b"BEBOOT"))

    def test_other_luns(self):
        st, data, _, _ = self.disk.execute(bytes([0x12, 0x20, 0, 0, 36, 0]))
        self.assertEqual((st, data[0]), (0, 0x7F))
        st, data, _, _ = self.disk.execute(bytes([0x00, 0xE0, 0, 0, 0, 0]))
        self.assertEqual(st, 2)
        st, data, _, _ = self.disk.execute(bytes([0x03, 0xE0, 0, 0, 18, 0]))
        self.assertEqual((data[2], data[12]), (5, 0x25))


class BootTest(unittest.TestCase):
    """The Nov 23 1994 kernel from the `be` disk, from entry to SER1's
    'Disk cache is' (about 6M instructions, ~2-3 min): the banner, CPU 2
    released, the SCSI scan finding one LUN on target 0."""

    @classmethod
    def setUpClass(cls):
        cls.m = boot_machine()
        cls.status = cls.m.run(STEPS["cache"] + 1000, b"Disk cache is")

    @classmethod
    def tearDownClass(cls):
        cls.m.disks[0].f.close()

    def test_banner(self):
        self.assertIn("until", self.status)
        self.assertEqual(bytes(self.m.ser1.out), BANNER + SCAN)

    def test_steps(self):
        self.assertEqual(self.m.steps, STEPS["cache"])

    def test_cpu2_started(self):
        self.assertEqual(len(self.m.cpus), 2)
        names = [n for _, c, n in self.m.reached if c == 2]
        self.assertIn("_null_thread", names)
        self.assertEqual(self.m.regs.reset, 0x02)

    def test_interrupt_wiring(self):
        # docs/bebox_hardware.md section 6: SER1 bit 1, SER2 bit 2 (the
        # kernels' _ser_init), floppy 0, RTC 4, keyboard 5, mouse 6, SCSI 7.
        m = self.m
        self.assertEqual(m.regs.io_sources,
                         {0: m.fdc.irq, 1: m.ser1.irq, 2: m.ser2.irq,
                          4: m.rtc_irq, 5: m.kbc.kbd_irq,
                          6: m.kbc.mouse_irq, 7: m.ncr.irq})

    def test_scsi_initialised(self):
        names = [n for _, _, n in self.m.reached]
        for name in ("_init_vector_table", "_spin_init", "_init_53c94",
                     "_start_cpu"):
            self.assertIn(name, names)


@unittest.skipUnless(os.environ.get("BEBOOT_LONG"),
                     "SKIPPED: BEBOOT_LONG=1 runs the boot to the mount "
                     "(~29M instructions, ~10 min, twice)")
class MountTest(unittest.TestCase):
    """On to the root volume: the SCSI scan (LUN 0 only), the floppy
    driver finding no diskette in drive 1 (the kernel's own messages),
    and 'be' mounted from target 0.

    Observed 2026-11-24 with the idle skip leaving _null_thread's R16
    (its lap counter) unadvanced: test_idle_skip_changes_nothing fails
    (CPU 1's stack cache differs, 555439 laps counted without the skip,
    528940 with it) and nothing else.  Before the skip measured the
    timers' own increments per lap (a 0-cycle folded JMP counts a model
    cycle but no timer tick), this test found the skipped run 41,580
    instructions short of the mount."""

    @classmethod
    def setUpClass(cls):
        cls.m = boot_machine()
        cls.status = cls.m.run(STEPS["mount"] + 1000, b"/dev/scsi_disk_driver_000")

    @classmethod
    def tearDownClass(cls):
        cls.m.disks[0].f.close()

    def test_console(self):
        self.assertIn("until", self.status)
        self.assertEqual(bytes(self.m.ser1.out), BANNER + MOUNT)

    def test_steps(self):
        self.assertEqual(self.m.steps, STEPS["mount"])

    def test_idle_skip_changes_nothing(self):
        """CHOICES['idle-skip']: the same run with every idle lap executed
        ends in the same state, register for register and word for word."""
        self.assertGreater(self.m.skips, 0)
        ref = boot_machine(skip=False)
        try:
            status = ref.run(STEPS["mount"] + 1000,
                             b"/dev/scsi_disk_driver_000")
        finally:
            ref.disks[0].f.close()
        self.assertEqual(status, self.status)
        self.assertEqual(ref.steps, self.m.steps)
        self.assertEqual(bytes(ref.ser1.out), bytes(self.m.ser1.out))

        def cpu_state(c):
            st, s = c.state, c.sysm
            return (c.steps, c.cycles, st.pc, st.sp, st.msp, st.psw, st.isp,
                    list(st.cache), s.timer1, s.timer2, s.config)
        self.assertEqual([cpu_state(c) for c in ref.cpus],
                         [cpu_state(c) for c in self.m.cpus])
        self.assertEqual(ref.board.ram, self.m.board.ram)

    def test_floppy_commands(self):
        self.assertEqual(self.m.fdc.log[:3],
                         [(0x03, 0x3F, 0x10), (0x07, 0x01), (0x08,)])


if __name__ == "__main__":
    unittest.main()
