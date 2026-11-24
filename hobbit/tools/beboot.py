#!/usr/bin/env python3
"""Boot a Hobbit BeBox kernel (Be Inc., 1994) on the reference model.

The Hobbit BeBox is a different board from the Plan 9 terminal that
tools/p9boot.py models: two ATT92010s, RAM at 0x08000000, a 4 KB I/O
window at 0x00800000 holding PC-compatible chips one byte per word, an
NCR 53C94 SCSI controller, BeBus slots at 0x80000000 + n * 0x10000000,
and three DSP3210s (docs/bebox_hobbit.md).  This file is that board.
The processor is sem/hobbit_sem.py's privileged machine (`System`), one
per CPU on a shared bus, exactly as p9boot uses it; p9boot itself is not
changed.  None of the Plan 9 board's chips (Quart, WD33C93, SONIC,
PCF8584, MK48T02) is on this board, so no device class is shared with
p9boot: only the bus contract (`read(pa)`, `write(pa, data, mask)`, mask
bit 3 = bits 31:24) and the run-loop shape.

No boot ROM survives (docs/bebox/MANIFEST.md), so the run starts the
way the ROM hands over: the kernel's ELF file, taken from a disk image's
/system/kernel (tools/befs1.py) or given directly, is loaded at its
addresses and entered.  Every modelling choice the sources leave open is
named in CHOICES; nothing is a silent default.  An access to anything
not modelled stops the run, loudly, with the PC, the device and the
access.

The images are untrusted data: run with `python3 -I`.

    python3 -I tools/beboot.py --disk build/bebox/hdd-hobbit-9308000058/hobbit-9308000058.img \\
        [--kernel FILE] [--max-steps N] [--memsize MB] [--until TEXT]
"""

import argparse
import bisect
import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "sem"))
import beelf        # noqa: E402
import befs1        # noqa: E402
import hobbit_sem   # noqa: E402

MASK32 = 0xFFFFFFFF

# Appendix A of the Be machine hardware documentation (16 Sep 1993),
# "Overall physical memory map" (page 3) -- docs/bebox_hobbit.md.
FLASH_BASE, FLASH_SIZE = 0x00000000, 0x80000      # 0.5 MB implemented
IO_BASE, IO_SIZE = 0x00800000, 0x1000             # 4 KB implemented
RAM_BASE = 0x08000000
DSP_SHADOW = 0x60000000                           # 2 MB (page 4)

# The word at RAM_BASE + 0x48 holds the memory size: the kernel's _main
# reads *$0x8000048 into _memsize, and _hack_for_old_bootroms replaces a
# value not in its table of six sizes with 8 MB ("Old boot roms -
# assuming 8 meg").
MEMSIZE_WORD = RAM_BASE + 0x48

# CHOICES['clock']
CPU_HZ = 25e6
# CHOICES['scsi-timing']: cycles from a 53C94 command to its interrupt.
NCR_IRQ_DELAY = 2500
# CHOICES['idle-skip']: the kernel whose idle loop was read.
IDLE_KERNEL_SHA256 = ("450716b22c33ed105684cdbe660b73e1843f2308b66fa76f2a153be1"
                      "12167b0b")

# CHOICES['floppy']: seconds from a seek's last step (or a recalibrate
# on cylinder 0) to its interrupt.
FDC_SETTLE = 100e-6

CHOICES = {
    "rom": "No boot ROM image survives (docs/bebox/MANIFEST.md).  The run "
           "does the ROM's job: the kernel's ELF segments are loaded at "
           "their addresses (physical RAM: the kernels link at 0x080c0100 "
           "or 0x08200100), the memory size is stored at 0x08000048, and "
           "CPU 1 starts at the ELF entry.  Any access to the flash range "
           "stops the run.",
    "memsize": "16 MB unless --memsize says otherwise; it must be one of "
               "the six sizes in _hack_for_old_bootroms's table, or the "
               "kernel itself falls back to 8 MB.",
    "entry-state": "CPU 1 starts with PSW = SP-current (bit 9) and IPL 0 "
                   "(interrupts masked), CONFIG = SE (stack cache on: "
                   "_main1 prints 'WARNING: Stack cache disabled.' "
                   "otherwise, so the ROM is taken to have set it), "
                   "SHAD = 0, VB = 0, STB = 0, and SP = MSP = ISP = the "
                   "last page of RAM + 0x800 (a temporary stack; _main "
                   "moves both stacks with _set_stacks before using "
                   "them).  The ROM's real state at its jump is unknown.",
    "ram-init": "RAM not loaded from the kernel reads as 0.",
    "cpu-id": "The ID register (CPU escape, ID) reads 0x1000003B, "
              "hobbit_sem.System's default, on the default 92010 part.  "
              "No Be kernel holds the 92010's value: both compare the "
              "register only with 0x0E33D03B (a 92020) to choose their "
              "'020' code, so any other value takes the 92010 path, which "
              "is the board's (Be's introduction of 15 Sep 1993: two "
              "92010s; docs/bebox_hobbit.md).",
    "clock": "Model time is CPU 1's Chapter 4 cycles at 25 MHz, the clock "
             "of the prototype's two 92010s as johnrash/bebox's "
             "design/hardware.md gives it (docs/bebox_hobbit.md; not yet "
             "from a Be document).  It drives the RTC.",
    "rtc": "The MC146818-style clock at ports 0x70/0x71 starts with "
           "register D's VRT bit clear (battery dead), so the kernel "
           "initialises its RAM and time; the time then runs with model "
           "time (Mc146818).",
    "printer": "Nothing is attached to the printer port: its status "
               "register reads 0x7F (no interrupt is ever raised).",
    "scsi-timing": "A 53C94 command's interrupt asserts 2,500 cycles "
                   "(100 us at 25 MHz) after the command is written, or "
                   "after the last byte of a DMA transfer passes the "
                   "pseudo-DMA port; selection, the target's work and the "
                   "bus phases take no other time.",
    "floppy": "The MCS3201 (Mcs3201) has one drive, drive 1, the one the "
              "kernel selects (_MotorOn writes DOR 0x2d), with no diskette "
              "in it: DIR bit 7 (disk change) stays set, so _PrepareMedia "
              "reports no medium.  Drive 1's head starts on cylinder 0.  "
              "The ROM is taken to have left the controller out of reset "
              "(DOR 0x0C) with no interrupt pending, because the kernel "
              "never resets it on the way up and its _FloppyInterrupt "
              "ignores an interrupt it did not ask for (intType 0), which "
              "on a level-triggered line would never end.  A seek or "
              "recalibrate interrupts (16 - SRT) ms per step after the "
              "command, plus 100 us.",
    "keyboard": "An AT keyboard and a PS/2 mouse are attached to the "
                "VL82C106's controller (typewritten.org's machine 0058 has "
                "both; bebox_hardware.md section 7); no key is pressed and "
                "the mouse does not move.  The controller's mode register "
                "starts at 0x00 (what the ROM left there is not known; the "
                "kernel reads and rewrites it) and its status reads SYS = 1 "
                "and the keyboard switch enabled.",
    "disks": "--disk images are SCSI targets 0, 1, ... in order (the "
             "first holds /system/kernel unless --kernel is given).  "
             "INQUIRY answers 'BEBOOT HOBBIT DISK'.  Each target has "
             "one logical unit, LUN 0; the kernel probes LUNs 0-7 and is "
             "answered for 1-7 as a SCSI-2 disk would (ScsiDisk.execute).",
    "disk-writes": "Writes to a disk go to an in-memory overlay; the image "
                   "file is never modified.",
    "interrupts": "Levels as the kernel's vector table uses them "
                  "(_init_vector_table copies 13 handlers: VB+20 _inth_l1 "
                  "-> _cpu_inth, the internal interrupt register; VB+28 "
                  "_inth_l3 -> _io_int_dispatch, the I/O interrupt "
                  "register; VB+36 _inth_l5 -> _slot_int_dispatch; VB+40 "
                  "_inth_l6 -> _joy_inth; VB+44/48 the timers).  CPU n "
                  "sees IL 3 while (I/O interrupt register & its mask) != "
                  "0 and IL 1 while bit n-1 of the internal interrupt "
                  "register is set.  Timer overflows are taken at level 1 "
                  "through VB+44/48 (PRM Table 1-14), before the internal "
                  "interrupt.  An interrupt is taken when its level is "
                  "below the PSW's IPL (Table 1-8, hobbit_sem."
                  "interrupt_accepted).",
    "idle-skip": "A harness shortcut, on by default (--no-idle-skip turns "
                 "it off), written for the Nov 23 1994 kernel only "
                 "(IDLE_KERNEL_SHA256; off for any other).  The idle thread "
                 "_null_thread loops at +0x4: CALL _fix_3_minute_bug (which "
                 "disables interrupts, reads TIMER1, restores them), ADD "
                 "$1,R16, JMP back -- no memory or device access but its "
                 "own stack.  When every running CPU is at that head, has "
                 "taken two laps of equal steps and cycles, may take an "
                 "interrupt (IPL > 3) and has none pending, the laps up to "
                 "just before the next timed event (a timer overflow, a "
                 "53C94 or MCS3201 interrupt) are not executed: each CPU's "
                 "steps, cycles and timers advance by whole laps and its "
                 "R16 by the lap count.  The run is otherwise the same "
                 "instruction for instruction (BootTest checks it against "
                 "a run without the skip).",
    "interleave": "CPU 2 is held in reset until the kernel sets bit 1 of "
                  "the processor reset register (0x0080001B); it then "
                  "starts at the ELF entry in CPU 1's entry state with its "
                  "own temporary stack (the ROM's code for CPU 2 is not "
                  "known).  The two CPUs are stepped one instruction at a "
                  "time, the one with fewer model cycles first.",
}


class Stop(Exception):
    """The run stops: something the board model does not cover."""


def lane_mask(lane):
    """Byte lane n of a big-endian word (lane 0 = bits 31:24) as the bus
    mask (bit 3 = bits 31:24)."""
    return 1 << (3 - lane)


# ---------------------------------------------------------------------------
# The I/O window: 8-bit registers, one per word (Appendix A, page 1: the
# board registers at 0x00800003 + 4n; johnrash/bebox's design/hardware.md
# for the PC ports at 0x00800000 + port * 4 + 3, checked against the
# kernel's own constants, docs/bebox_hobbit.md "Device addresses").
# ---------------------------------------------------------------------------

def port_addr(port):
    return IO_BASE + port * 4 + 3


class IoWindow:
    def __init__(self, board):
        self.board = board
        self.regs = {}          # word offset -> (lane, device, reg, name)

    def add(self, addr, lane, device, reg, name):
        off = (addr - IO_BASE) & ~3
        if off in self.regs:
            raise ValueError("I/O word 0x%08x claimed twice" % addr)
        self.regs[off] = (lane, device, reg, name)

    def _find(self, off, what):
        r = self.regs.get(off & ~3)
        if r is None:
            raise Stop("I/O window: no register modelled at 0x%08x "
                       "(PC port 0x%03x) on %s"
                       % (IO_BASE + off, off // 4, what))
        return r

    def add_word(self, addr, device, name):
        """A device that takes the whole word (device.read(off),
        device.write(off, data, mask))."""
        off = (addr - IO_BASE) & ~3
        if off in self.regs:
            raise ValueError("I/O word 0x%08x claimed twice" % addr)
        self.regs[off] = (None, device, None, name)

    def read(self, off):
        lane, dev, reg, name = self._find(off, "a read")
        if lane is None:
            return dev.read(off) & MASK32
        return (dev.read(reg) & 0xFF) << (8 * (3 - lane))

    def write(self, off, data, mask):
        r = self.regs.get(off & ~3)
        if r is not None and r[0] is None:
            r[1].write(off, data, mask)
            return
        lane, dev, reg, name = self._find(
            off, "a write of 0x%08x mask %x" % (data, mask))
        # A word store (the kernel's _fetch_and_or: an interlocked ORI on
        # 0x00800004) drives every lane; the register latches its own.
        # A store that does not drive the register's lane stops.
        if not mask & lane_mask(lane):
            raise Stop("I/O window: %s (0x%08x) written with byte mask %x, "
                       "which does not include its lane %d" % (name, IO_BASE + (off & ~3),
                                            mask, lane))
        dev.write(reg, (data >> (8 * (3 - lane))) & 0xFF)


class BoardRegs:
    """Appendix A pages 1-2: the board's own 8-bit registers.

    reg 0 I/O interrupt register (read only: bit 7 SCSI, 6 mouse,
    5 keyboard, 4 RTC, 3 printer, 2 SER1, 1 SER2, 0 floppy; 1 =
    interrupting); 1, 2 the CPU 1 and CPU 2 masks (1 = not masking);
    3 slot interrupts (bit n-1 = slot n); 4, 5 slot masks; 6 processor
    reset (bit 6 DSP3, 5 DSP2, 4 DSP1, 1 Hobbit B; 0 = reset, 1 = run);
    7 internal processor interrupts (6..4 DSP3..1, 1 Hobbit B, 0 Hobbit
    A).  'Who am I' is separate (WhoAmI)."""

    NAMES = ["I/O interrupt", "CPU 1 I/O mask", "CPU 2 I/O mask",
             "slot interrupt", "CPU 1 slot mask", "CPU 2 slot mask",
             "processor reset", "internal interrupt"]

    def __init__(self, board):
        self.board = board
        self.io_mask = [0, 0]
        self.slot_mask = [0, 0]
        self.reset = 0
        self.internal = 0
        self.slot_steer = None
        self.io_sources = {}        # bit -> callable() -> bool

    def io_status(self):
        st = 0
        for bit, f in self.io_sources.items():
            if f():
                st |= 1 << bit
        return st

    def read(self, reg):
        if reg == 0:
            return self.io_status()
        if reg in (1, 2):
            return self.io_mask[reg - 1]
        if reg == 3:
            raise Stop("read of 0x0080000F (Appendix A: slot interrupt "
                       "register; the kernel's _slot_int_steer)")
        if reg in (4, 5):
            return self.slot_mask[reg - 4]
        if reg == 6:
            return self.reset
        if reg == 7:
            return self.internal
        raise Stop("board register %d read" % reg)

    def write(self, reg, value):
        if reg in (1, 2):
            self.io_mask[reg - 1] = value
        elif reg in (4, 5):
            self.slot_mask[reg - 4] = value
        elif reg == 3:
            # Appendix A (Sep 1993) prints 0x0080000F as the read-only
            # slot interrupt register; the Nov 1994 kernel names its
            # pointer to it _slot_int_steer and writes 0 there
            # (_slot_init+0xe).  The write is kept; what it steers is not
            # known, so a read still stops.
            self.slot_steer = value
        elif reg == 6:
            if value & ~0x02 & 0xFF:
                raise Stop("processor reset register written 0x%02x: "
                           "a DSP released from reset (not modelled)"
                           % value)
            old, self.reset = self.reset, value
            self.board.reset_changed(old, value)
        elif reg == 7:
            self.internal = value
        else:
            raise Stop("write of 0x%02x to the read-only %s register"
                       % (value, self.NAMES[reg]))


class WhoAmI:
    """Appendix A page 2, 0x00800DC3: bits 7:4 the joystick buttons
    (none pressed: read as 1? -- not known; 0 is returned, a choice made
    visible here), bits 3:0 the current bus master, 4 = CPU 1, 5 = CPU 2.
    _get_cpu_id returns (value & 15) - 4."""

    def __init__(self, board):
        self.board = board

    def read(self, reg):
        return 3 + self.board.current_cpu     # CPU 1 -> 4, CPU 2 -> 5

    def write(self, reg, value):
        raise Stop("write of 0x%02x to Who Am I" % value)


class Uart:
    """A PC serial port's eight registers (port base + 0..7): an 8250
    family UART as the PC ports are (the kernel's _scc_init/_scc_out/
    _scc_in touch +0, +1, +3, +4, +5).  Transmission is immediate (THR
    empty and transmitter empty always set in LSR); received bytes come
    from `feed`.

    Interrupts as the VL16C452 sheet gives them (VTI manual pp. 6-57..
    6-60): the THRE interrupt is raised when the THR empties and when
    IER bit 1 is set with the THR empty ("When interrupts are
    subsequently enabled, an interrupt occurs due to THRE", p. 6-60),
    and cleared by a read of the IIR that reports it or by a write to
    the THR (p. 6-57); the INT output is enabled by MCR bit 3, OUT2
    (p. 6-58, Figure 3 p. 6-59)."""

    NAMES = ["RBR/THR/DLL", "IER/DLM", "IIR/FCR", "LCR", "MCR", "LSR",
             "MSR", "SCR"]

    def __init__(self, name):
        self.name = name
        self.out = bytearray()
        self.rx = collections.deque()
        self.ier = self.lcr = self.mcr = self.scr = 0
        self.dll = self.dlm = 0
        self.fcr = 0
        self.thre = False           # THRE interrupt pending

    def feed(self, data):
        self.rx.extend(data)

    def _source(self):
        if self.ier & 1 and self.rx:
            return 0x04
        if self.ier & 2 and self.thre:
            return 0x02
        return 0x01

    def irq(self):
        return bool(self.mcr & 0x08) and self._source() != 0x01

    def read(self, reg):
        dlab = self.lcr & 0x80
        if reg == 0:
            if dlab:
                return self.dll
            return self.rx.popleft() if self.rx else 0
        if reg == 1:
            return self.dlm if dlab else self.ier
        if reg == 2:
            iir = self._source()
            if iir == 0x02:
                self.thre = False
            return iir
        if reg == 3:
            return self.lcr
        if reg == 4:
            return self.mcr
        if reg == 5:
            return 0x60 | (1 if self.rx else 0)
        if reg == 6:
            return 0xB0         # CTS, DSR, DCD asserted
        return self.scr

    def write(self, reg, value):
        dlab = self.lcr & 0x80
        if reg == 0:
            if dlab:
                self.dll = value
            else:
                self.out.append(value)
                self.thre = True        # sent at once: the THR is empty
        elif reg == 1:
            if dlab:
                self.dlm = value
            else:
                if value & 2 and not self.ier & 2:
                    self.thre = True
                self.ier = value & 0x0F
        elif reg == 2:
            self.fcr = value
        elif reg == 3:
            self.lcr = value
        elif reg == 4:
            self.mcr = value
        elif reg == 7:
            self.scr = value
        else:
            raise Stop("%s: write of 0x%02x to read-only %s"
                       % (self.name, value, self.NAMES[reg]))


class Parallel:
    """The PC printer port at 0x378 (data), 0x379 (status), 0x37A
    (control): Appendix A's 'Printer' interrupt bit, the kernel's
    _par_init/_io_init.  No printer is attached (CHOICES['printer']):
    status reads 0x7F, data and control read back what was written."""

    def __init__(self):
        self.data = 0
        self.control = 0

    def read(self, reg):
        return (self.data, 0x7F, self.control)[reg]

    def write(self, reg, value):
        if reg == 0:
            self.data = value
        elif reg == 2:
            self.control = value
        else:
            raise Stop("printer port: write of 0x%02x to the status "
                       "register" % value)


class Mc146818:
    """The PC real-time clock at ports 0x70 (index) and 0x71 (data): 14
    clock and control registers and 50 bytes of battery-backed RAM.
    The kernel (_readrtc/_writertc, _rtc_init) uses it as the PC's: it
    reads register D's VRT bit (7) and, if the RAM is valid, its own
    checksum over registers 14..63, else rewrites them from defaults.

    CHOICES['rtc']: the clock starts with VRT = 0 (a dead battery), so the
    kernel initialises the RAM and sets the time itself; the time then
    runs with model time.  Registers A (UIP never set), B, C read as
    stored, D as VRT = 1 once anything has been written."""

    def __init__(self, clock):
        self.clock = clock          # callable() -> model seconds
        self.index = 0
        self.ram = [0] * 64
        self.ram[0x0B] = 0x02       # 24-hour, BCD
        self.vrt = False
        self.base = 0.0             # model time when the time was set
        self.time = [0] * 10        # sec, alarm, min, alarm, hour, alarm,
                                    # wday, mday, month, year (binary)

    def _bcd(self):
        return not (self.ram[0x0B] & 0x04)

    def _now(self):
        import calendar
        import time
        t = self.time
        try:
            base = calendar.timegm((1900 + t[9] + (100 if t[9] < 70 else 0),
                                    max(t[8], 1), max(t[7], 1), t[4], t[2],
                                    t[0], 0, 0, 0))
        except (ValueError, OverflowError):
            base = 0
        now = time.gmtime(base + int(self.clock() - self.base))
        return {0: now.tm_sec, 2: now.tm_min, 4: now.tm_hour,
                6: (now.tm_wday + 1) % 7 + 1, 7: now.tm_mday,
                8: now.tm_mon, 9: now.tm_year % 100}

    def read(self, reg):
        if reg == 0:
            raise Stop("RTC: read of the index port 0x70")
        i = self.index
        if i in (0, 2, 4, 6, 7, 8, 9):
            v = self._now()[i]
            return ((v // 10) << 4 | v % 10) if self._bcd() else v
        if i in (1, 3, 5):
            return self.time[i]
        if i == 0x0A:
            return self.ram[i] & 0x7F
        if i == 0x0C:
            return 0
        if i == 0x0D:
            return 0x80 if self.vrt else 0
        return self.ram[i]

    def write(self, reg, value):
        if reg == 0:
            self.index = value & 0x3F
            return
        i = self.index
        self.vrt = True
        if i in (0, 2, 4, 6, 7, 8, 9):
            now = self._now()
            for k in now:
                self.time[k] = now[k]
            v = ((value >> 4) * 10 + (value & 0xF)) if self._bcd() else value
            self.time[i] = v
            self.base = self.clock()
        elif i in (1, 3, 5):
            self.time[i] = value
        elif i in (0x0C, 0x0D):
            raise Stop("RTC: write of 0x%02x to read-only register %d"
                       % (value, i))
        else:
            self.ram[i] = value


# ---------------------------------------------------------------------------
# SCSI: the NCR 53C94 (data sheet Feb 1990, docs/bebox/MANIFEST.md) on lane
# 2 of the I/O words 0x00800800 + reg * 4 (the kernel's _reg_base =
# 0x00800802, __cmd_reg = 0x0080080E ...), its 16-bit pseudo-DMA port at
# 0x00800842 (__pseudo_dma_reg), and disks behind it.
# ---------------------------------------------------------------------------

NCR_BASE = 0x00800802
NCR_PDMA = 0x00800842

# SCSI phases as the status register's bits 2:0 report them (MSG, C/D, I/O).
PH_DATA_OUT, PH_DATA_IN, PH_COMMAND, PH_STATUS = 0, 1, 2, 3
PH_MSG_OUT, PH_MSG_IN = 6, 7

INT_DISCONNECT, INT_BUS_SERVICE, INT_FUNCTION_COMPLETE = 0x20, 0x10, 0x08
INT_ILLEGAL, INT_SCSI_RESET = 0x40, 0x80


class ScsiDisk:
    """A direct-access target backed by a disk image, read only: writes go
    to an in-memory overlay (CHOICES['disk-writes']), never to the file.
    Commands not listed stop the run."""

    def __init__(self, path, name):
        self.f = open(path, "rb")
        self.f.seek(0, 2)
        self.blocks = self.f.tell() // 512
        self.name = name
        self.overlay = {}
        self.sense = (0, 0)             # (key, additional sense code)
        self.reads = self.writes = 0

    def read_block(self, lba):
        if lba in self.overlay:
            return self.overlay[lba]
        self.f.seek(lba * 512)
        return self.f.read(512)

    def execute(self, cdb):
        """Returns (status, data in or None, bytes expected out or 0,
        callback for the data out)."""
        op = cdb[0]
        if cdb[1] >> 5 and op != 0x03:
            # CHOICES['disks']: one logical unit.  The LUN is CDB byte 1
            # bits 7:5 (selection without ATN sends no IDENTIFY).  As
            # SCSI-2 has it: INQUIRY answers peripheral qualifier 3,
            # type 0x1F (byte 0 = 0x7F); anything else is CHECK CONDITION,
            # ILLEGAL REQUEST, LOGICAL UNIT NOT SUPPORTED (0x25).
            if op == 0x12:
                return 0, bytes([0x7F, 0, 1, 1, 31, 0, 0, 0]
                                + [0x20] * 28)[:cdb[4]], 0, None
            self.sense = (5, 0x25)
            return 2, None, 0, None
        if op == 0x00:                                  # TEST UNIT READY
            return 0, None, 0, None
        if op == 0x03:                                  # REQUEST SENSE
            key, asc = self.sense
            self.sense = (0, 0)
            data = bytes([0x70, 0, key, 0, 0, 0, 0, 10, 0, 0, 0, 0, asc, 0,
                          0, 0, 0, 0])
            return 0, data[:cdb[4] or 4], 0, None
        if op == 0x12:                                  # INQUIRY
            data = (bytes([0, 0, 1, 1, 31, 0, 0, 0]) + b"BEBOOT  "
                    + b"HOBBIT DISK     " + b"1994")
            return 0, data[:cdb[4]], 0, None
        if op == 0x25:                                  # READ CAPACITY
            return 0, (self.blocks - 1).to_bytes(4, "big") + \
                (512).to_bytes(4, "big"), 0, None
        if op in (0x08, 0x28, 0x0A, 0x2A):              # READ/WRITE 6/10
            if op in (0x08, 0x0A):
                lba = ((cdb[1] & 0x1F) << 16) | (cdb[2] << 8) | cdb[3]
                n = cdb[4] or 256
            else:
                lba = int.from_bytes(cdb[2:6], "big")
                n = int.from_bytes(cdb[7:9], "big")
            if lba + n > self.blocks:
                self.sense = (5, 0x21)          # illegal request, LBA range
                return 2, None, 0, None
            if op in (0x08, 0x28):
                self.reads += n
                return 0, b"".join(self.read_block(lba + i)
                                   for i in range(n)), 0, None

            def store(data, lba=lba, n=n):
                self.writes += n
                for i in range(n):
                    self.overlay[lba + i] = bytes(data[512 * i:512 * (i + 1)])
            return 0, None, 512 * n, store
        raise Stop("SCSI %s: command 0x%02x not modelled (CDB %s)"
                   % (self.name, op, cdb.hex()))


class Ncr53c94:
    """The 53C94 as the kernel's driver (scsi_sim.c: _init_53c94,
    _sim_execute_scsi_io, _data_xfer_in[_dma], _data_xfer_out[_dma],
    _command_complete, _sim_reset_bus) drives it, initiator only.

    Registers: data sheet Table 7 (p. 12).  Select without ATN: Table 8
    (p. 18): time-out -> interrupt 0x20, step 0; complete -> 0x18, step
    4.  Transfer information, initiator command complete, message
    accepted: p. 33.  Reset SCSI bus: p. 29 (RSTO tied to RSTI, so a SCSI
    reset interrupt unless Config 1 bit 6 disables it).  The INT output
    is the board's I/O interrupt bit 7 (Appendix A).  A command the
    driver does not use stops the run."""

    def __init__(self, targets, irq_delay, clock):
        self.targets = targets          # id -> ScsiDisk
        self.irq_delay = irq_delay      # cycles from command to INT
        self.clock = clock              # callable() -> cycles
        self.reset_chip()
        self.dest = 0
        self.config1 = 0
        self.log = []

    def reset_chip(self):
        self.fifo = collections.deque()
        self.tc = 0                     # transfer count register
        self.counter = 0
        self.tc_zero = False
        self.isr = 0
        self.seq = 0
        self.int_at = None              # cycle at which INT asserts
        self.phase = None               # None: bus free
        self.target = None
        self.data_in = b""              # bytes the target will send
        self.out_need = 0
        self.out_buf = bytearray()
        self.out_store = None
        self.status_byte = 0
        self.dma = None                 # "in" / "out" during a DMA transfer

    # -- the INT line --
    def int_active(self):
        return self.int_at is not None and self.clock() >= self.int_at

    def _interrupt(self, isr, seq=None):
        self.isr = isr
        if seq is not None:
            self.seq = seq
        self.int_at = self.clock() + self.irq_delay

    def irq(self):
        return self.int_active()

    def _status(self):
        st = 0x80 if self.int_active() else 0
        if self.tc_zero:
            st |= 0x10
        return st | (self.phase if self.phase is not None else 0)

    def read(self, reg):
        if reg == 0:
            return self.counter & 0xFF
        if reg == 1:
            return (self.counter >> 8) & 0xFF
        if reg == 2:
            if not self.fifo:
                raise Stop("53C94: FIFO read while empty")
            return self.fifo.popleft()
        if reg == 4:
            return self._status()
        if reg == 5:
            v = self.isr if self.int_active() else 0
            if self.int_active():
                self.isr = 0
                self.int_at = None
            return v
        if reg == 6:
            return self.seq
        if reg == 7:
            n = len(self.fifo)
            if self.dma == "in":
                n = min(16, len(self.data_in))
            return (self.seq << 5) | min(n, 16)
        if reg == 8:
            return self.config1
        raise Stop("53C94: read of register %d" % reg)

    def write(self, reg, value):
        if reg == 0:
            self.tc = (self.tc & 0xFF00) | value
        elif reg == 1:
            self.tc = (self.tc & 0x00FF) | (value << 8)
        elif reg == 2:
            self.fifo.append(value)
            if len(self.fifo) > 16:
                raise Stop("53C94: FIFO overflow")
        elif reg == 3:
            self.command(value)
        elif reg == 4:
            self.dest = value & 7
        elif reg == 8:
            self.config1 = value
        elif reg in (5, 6, 7, 9, 0x0A, 0x0B, 0x0C):
            pass        # time-out, sync period/offset, clock, test, config
        else:
            raise Stop("53C94: write of 0x%02x to register %d" % (value, reg))

    def command(self, cmd):
        dma = bool(cmd & 0x80)
        code = cmd & 0x7F
        self.log.append(cmd)
        if dma:
            self.counter = self.tc or 0x10000
            self.tc_zero = False
        if code == 0x00:                                # NOP
            return
        if code == 0x01:                                # flush FIFO
            self.fifo.clear()
            return
        if code == 0x02:                                # reset chip
            self.reset_chip()
            return
        if code == 0x03:                                # reset SCSI bus
            self.phase = None
            if not self.config1 & 0x40:
                self._interrupt(INT_SCSI_RESET)
            return
        if code == 0x41 and not dma:                    # select without ATN
            target = self.targets.get(self.dest)
            if target is None:
                self.fifo.clear()
                self.phase = None
                self._interrupt(INT_DISCONNECT, 0)
                return
            cdb = bytes(self.fifo)
            self.fifo.clear()
            group = cdb[0] >> 5
            want = {0: 6, 1: 10, 2: 10, 5: 12}.get(group, 6)
            if len(cdb) < want:
                raise Stop("53C94: %d CDB bytes in the FIFO, command 0x%02x "
                           "needs %d" % (len(cdb), cdb[0], want))
            self.target = target
            status, data, need, store = target.execute(cdb[:want])
            self.status_byte = status
            self.data_in = data or b""
            self.out_need, self.out_store = need, store
            self.out_buf = bytearray()
            if self.data_in:
                self.phase = PH_DATA_IN
            elif need:
                self.phase = PH_DATA_OUT
            else:
                self.phase = PH_STATUS
            self._interrupt(INT_BUS_SERVICE | INT_FUNCTION_COMPLETE, 4)
            return
        if code == 0x10:                                # transfer information
            if self.phase == PH_DATA_IN:
                if dma:
                    self.dma = "in"
                    return          # bytes leave through the PDMA port
                self.fifo.append(self.data_in[0])
                self.data_in = self.data_in[1:]
                if not self.data_in:
                    self.phase = PH_STATUS
                self._interrupt(INT_BUS_SERVICE)
                return
            if self.phase == PH_DATA_OUT:
                if dma:
                    self.dma = "out"
                    return
                while self.fifo:
                    self._out_byte(self.fifo.popleft())
                self._interrupt(INT_BUS_SERVICE)
                return
            raise Stop("53C94: transfer information in phase %s"
                       % self.phase)
        if code == 0x11 and not dma:                    # initiator cmd complete
            if self.phase != PH_STATUS:
                raise Stop("53C94: command complete in phase %s" % self.phase)
            self.fifo.extend([self.status_byte, 0x00])  # status, COMMAND COMPLETE
            self.phase = PH_MSG_IN
            self._interrupt(INT_FUNCTION_COMPLETE)
            return
        if code == 0x12 and not dma:                    # message accepted
            self.phase = None
            self.target = None
            self._interrupt(INT_DISCONNECT)
            return
        raise Stop("53C94: command 0x%02x not modelled" % cmd)

    def _out_byte(self, b):
        self.out_buf.append(b)
        if len(self.out_buf) == self.out_need:
            self.out_store(self.out_buf)
            self.phase = PH_STATUS

    def _dma_step(self, n):
        self.counter -= n
        if self.counter <= 0:
            self.counter = 0
            self.tc_zero = True
            self.dma = None
            self._interrupt(INT_BUS_SERVICE)

    # the pseudo-DMA port: a 16-bit word, the earlier byte in bits 15:8
    def pdma_read(self):
        if self.dma != "in" or len(self.data_in) < 2:
            raise Stop("53C94: pseudo-DMA read with no data-in transfer "
                       "running (%d bytes left)" % len(self.data_in))
        v = (self.data_in[0] << 8) | self.data_in[1]
        self.data_in = self.data_in[2:]
        if not self.data_in:
            self.phase = PH_STATUS
        self._dma_step(2)
        return v

    def pdma_write(self, value):
        if self.dma != "out":
            raise Stop("53C94: pseudo-DMA write with no data-out transfer "
                       "running")
        self._out_byte(value >> 8)
        self._out_byte(value & 0xFF)
        self._dma_step(2)


class PdmaPort:
    """0x00800840: the 53C94's pseudo-DMA port in bits 15:0 of the word
    (the kernel reads and writes *0x00800842 as a half word)."""

    def __init__(self, ncr):
        self.ncr = ncr

    def read(self, off):
        return self.ncr.pdma_read()

    def write(self, off, data, mask):
        if mask != 0x3:
            raise Stop("pseudo-DMA port written with byte mask %x" % mask)
        self.ncr.pdma_write(data & 0xFFFF)


# ---------------------------------------------------------------------------
# The floppy controller: a Motorola MCS3201 at the PC's secondary address
# 0x370 (docs/bebox_hardware.md section 8; data sheet
# docs/devices/MCS3201_IBM_PC_XT_AT_Floppy_Disk_Controller_1991.pdf, which
# has no text layer: pages read from the page images).
# ---------------------------------------------------------------------------

class Mcs3201:
    """The MCS3201's four registers the kernel touches: DOR (0x372, write
    only), main status (0x374, read only), data (0x375), and DIR/DCR
    (0x377: read the digital input register, write the diskette control
    register) -- data sheet section 5, pp. 12-13.

    Commands modelled: SPECIFY (0x03), RECALIBRATE (0x07), SENSE
    INTERRUPT STATUS (0x08) and SEEK (0x0F), the four the kernel issues
    before it reads a sector (_InitDrive, _PrepareMedia).  Any other
    command byte stops the run, as does a reset of the controller through
    the DOR (CHOICES['floppy']).  Drives are `drives[n]`: None (no drive)
    or a dict with 'medium' (None = no diskette) and 'cyl' (the head's
    cylinder)."""

    NAMES = ["0x370", "0x371", "DOR", "0x373", "MSR", "data", "0x376",
             "DIR/DCR"]
    # Command byte (low five bits) -> bytes in the command phase
    # (section 6, pp. 15-19).
    LENGTHS = {0x03: 3, 0x07: 2, 0x08: 1, 0x0F: 3}

    def __init__(self, drives, clock):
        self.drives = drives
        self.clock = clock          # -> model seconds
        # CHOICES['floppy']: the ROM left the controller out of reset,
        # DMA and interrupts enabled, no drive selected, no interrupt
        # pending.
        self.dor = 0x0C
        self.dcr = 0
        self.srt = None             # step rate time, set by SPECIFY
        self.cmd = []               # command phase bytes so far
        self.results = []           # result phase bytes still to read
        self.pcn = [0, 0, 0, 0]     # present cylinder per drive
        self.busy = 0               # MSR bits 3:0, drives seeking
        self.pending = []           # (time, drive, st0) seek/recal ends
        self.done = []              # (drive, st0) ended, not yet sensed
        self.log = []

    # -- the interrupt line (section 7.11, p. 23) --------------------------
    def _advance(self):
        now = self.clock()
        due = [p for p in self.pending if p[0] <= now]
        for p in due:
            self.pending.remove(p)
            self.done.append((p[1], p[2]))
            self.busy &= ~(1 << p[1])

    def int_line(self):
        self._advance()
        return bool(self.done)

    def irq(self):
        """I/O interrupt register bit 0: the INT pin, gated by DOR bit 3
        (DMA and interrupt enable, p. 12; Appendix A / chapter 7 p. 4)."""
        return bool(self.dor & 0x08) and self.int_line()

    # -- registers ---------------------------------------------------------
    def _msr(self):
        """Section 5.3, p. 12: 7 RQM, 6 DIO (1 = to the host), 5 non-DMA
        execution, 4 controller busy, 3:0 drive n seeking."""
        self._advance()
        if self.results:
            return 0x80 | 0x40 | 0x10 | self.busy
        return 0x80 | (0x10 if self.cmd else 0) | self.busy

    def _drive(self):
        return self.drives.get(self.dor & 3)

    def read(self, reg):
        if reg == 4:
            return self._msr()
        if reg == 5:
            if not self.results:
                raise Stop("MCS3201 data register read outside a result "
                           "phase")
            return self.results.pop(0)
        if reg == 7:
            # Section 5.5, p. 13: bit 7 DSKCHG, bits 6:0 always 0.  The
            # line is the selected drive's; with no diskette it stays set.
            d = self._drive()
            if d is None:
                raise Stop("MCS3201 DIR read with drive %d selected, which "
                           "is not modelled" % (self.dor & 3))
            return 0x80 if d["medium"] is None else 0x00
        raise Stop("MCS3201 register %s read" % self.NAMES[reg])

    def write(self, reg, value):
        if reg == 2:
            if not value & 0x04 or not self.dor & 0x04:
                raise Stop("MCS3201 DOR written 0x%02x: a controller reset "
                           "(not modelled)" % value)
            self.dor = value
        elif reg == 7:
            self.dcr = value & 3        # section 5.6: the data rate
        elif reg == 5:
            self._command_byte(value)
        else:
            raise Stop("MCS3201 register %s written 0x%02x"
                       % (self.NAMES[reg], value))

    # -- commands ----------------------------------------------------------
    def _command_byte(self, value):
        if self.results:
            raise Stop("MCS3201 command byte 0x%02x written during a "
                       "result phase" % value)
        self.cmd.append(value)
        op = self.cmd[0] & 0x1F
        n = self.LENGTHS.get(op)
        if n is None:
            raise Stop("MCS3201 command 0x%02x not modelled" % self.cmd[0])
        if len(self.cmd) < n:
            return
        cmd, self.cmd = self.cmd, []
        self.log.append(tuple(cmd))
        if op == 0x03:                          # SPECIFY: SRT/HUT, HLT/ND
            self.srt = cmd[1] >> 4
            if cmd[2] & 1:
                raise Stop("MCS3201 SPECIFY with ND (non-DMA) set")
        elif op == 0x08:                        # SENSE INTERRUPT STATUS
            self._advance()
            if self.done:
                drive, st0 = self.done.pop(0)
                self.results = [st0, self.pcn[drive]]
            else:
                self.results = [0x80]           # invalid (p. 24)
        else:                                   # RECALIBRATE, SEEK
            drive = cmd[1] & 3
            if self.srt is None:
                raise Stop("MCS3201 seek before SPECIFY")
            d = self.drives.get(drive)
            if d is None:
                raise Stop("MCS3201 seek on drive %d, not modelled" % drive)
            target = 0 if op == 0x07 else cmd[2]
            steps = abs(d["cyl"] - target)
            d["cyl"] = target
            self.pcn[drive] = target
            # Section 7.12: SRT is 1 to 16 ms, F = 1 ms (p. 24).
            t = self.clock() + FDC_SETTLE + steps * (16 - self.srt) / 1000.0
            self.busy |= 1 << drive
            self.pending.append((t, drive, 0x20 | drive))   # SE, normal


# ---------------------------------------------------------------------------
# The keyboard controller: the VL82C106's 8042-compatible controller at
# ports 0x60/0x64 (docs/bebox_hardware.md section 7; VTI Computer Products
# data manual 1990, VL82C106 pp. 6-197..6-202, PDF pp. 452-457).
# ---------------------------------------------------------------------------

class Vl82c106Kbc:
    """The programmer interface of p. 6-197: status (0x64 read), command
    (0x64 write), output buffer (0x60 read), input buffer (0x60 write).

    Controller commands modelled (p. 6-202): 0x20 read mode, 0x60 write
    mode, 0xA7/0xA8 disable/enable mouse, 0xA9 mouse interface test,
    0xAA self test, 0xAB keyboard interface test, 0xAD/0xAE disable/enable
    keyboard, 0xD4 write to mouse.  The keyboard and mouse at the other
    end answer the PS/2 commands the kernel sends (_kb_init, _SetLEDs,
    _mouse_init): CHOICES['keyboard'].  Anything else stops the run.
    The controller answers at once: IBF never reads 1."""

    KBD, MOUSE = 0, 1

    def __init__(self):
        self.mode = 0x00            # CHOICES['keyboard']
        self.out = collections.deque()   # (byte, source)
        self.last = 0
        self.cd = 0                 # status bit 3: last write was a command
        self.expect = None          # what the next 0x60 write is for
        self.log = []

    def _put(self, source, *bs):
        for b in bs:
            self.out.append((b & 0xFF, source))

    def status(self):
        """Figure 5 (PS/2 status, p. 6-202): 0 OBF, 1 IBF, 2 SYS, 3 C/D,
        4 keyboard enable switch, 5 output buffer source (1 = mouse)."""
        st = 0x10 | 0x04 | (self.cd << 3)     # not inhibited; SYS: the ROM ran
        if self.out:
            st |= 0x01
            if self.out[0][1] == self.MOUSE:
                st |= 0x20
        return st

    def kbd_irq(self):
        return bool(self.out) and self.out[0][1] == self.KBD and bool(self.mode & 1)

    def mouse_irq(self):
        return bool(self.out) and self.out[0][1] == self.MOUSE and bool(self.mode & 2)

    def read(self, reg):
        if reg == 4:
            return self.status()
        if self.out:
            self.last = self.out.popleft()[0]
        return self.last                    # an empty buffer: the last byte

    def write(self, reg, value):
        if reg == 4:
            self.cd = 1
            self._command(value)
        else:
            self.cd = 0
            self._data(value)

    def _command(self, c):
        self.log.append(("cmd", c))
        if c == 0x20:
            self._put(self.KBD, self.mode)
        elif c in (0x60, 0xD4):
            self.expect = c
        elif c == 0xA7:
            self.mode |= 0x20
        elif c == 0xA8:
            self.mode &= ~0x20
        elif c in (0xA9, 0xAB):
            self._put(self.KBD, 0x00)           # interface test passed
        elif c == 0xAA:
            self._put(self.KBD, 0x55)           # self test passed
        elif c == 0xAD:
            self.mode |= 0x10
        elif c == 0xAE:
            self.mode &= ~0x10
        else:
            raise Stop("VL82C106 keyboard controller command 0x%02x not "
                       "modelled" % c)

    def _data(self, b):
        expect, self.expect = self.expect, None
        if expect == 0x60:
            self.log.append(("mode", b))
            self.mode = b
        elif expect == 0xD4:
            self.log.append(("mouse", b))
            self._mouse(b)
        elif expect == "led":
            self.log.append(("kbd", b))
            self._put(self.KBD, 0xFA)
        else:
            self.log.append(("kbd", b))
            self._keyboard(b)

    def _keyboard(self, b):
        """An AT (MF2) keyboard: ECHO answers 0xEE; SET LEDS (0xED, then
        the LED byte), ENABLE (0xF4) and SET DEFAULT (0xF6) acknowledge
        with 0xFA; RESET (0xFF) acknowledges and passes its test (0xAA)."""
        if b == 0xEE:
            self._put(self.KBD, 0xEE)
        elif b == 0xED:
            self._put(self.KBD, 0xFA)
            self.expect = "led"
        elif b in (0xF4, 0xF5, 0xF6):
            self._put(self.KBD, 0xFA)
        elif b == 0xFF:
            self._put(self.KBD, 0xFA, 0xAA)
        else:
            raise Stop("keyboard command 0x%02x not modelled" % b)

    def _mouse(self, b):
        """A PS/2 mouse: READ ID (0xF2) answers 0xFA then ID 0x00;
        ENABLE (0xF4), DISABLE (0xF5), SET DEFAULT (0xF6) acknowledge;
        RESET (0xFF) answers 0xFA, 0xAA, 0x00."""
        if b == 0xF2:
            self._put(self.MOUSE, 0xFA, 0x00)
        elif b in (0xF4, 0xF5, 0xF6):
            self._put(self.MOUSE, 0xFA)
        elif b == 0xFF:
            self._put(self.MOUSE, 0xFA, 0xAA, 0x00)
        else:
            raise Stop("mouse command 0x%02x not modelled" % b)


# ---------------------------------------------------------------------------
# The bus
# ---------------------------------------------------------------------------

class Board:
    def __init__(self, memsize):
        self.ram = {}
        self.ram_hi = RAM_BASE + memsize
        self.memsize = memsize
        self.io = IoWindow(self)
        self.current_cpu = 1
        self.on_reset = None        # callable(old, new) for the run loop

    def reset_changed(self, old, new):
        if self.on_reset is not None:
            self.on_reset(old, new)

    def where(self):
        return "physical"

    def read(self, pa):
        pa &= ~3 & MASK32
        if RAM_BASE <= pa < self.ram_hi:
            return self.ram.get(pa, 0)
        if IO_BASE <= pa < IO_BASE + IO_SIZE:
            return self.io.read(pa - IO_BASE)
        raise Stop(self._nothing(pa, "read"))

    def write(self, pa, data, mask):
        pa &= ~3 & MASK32
        if RAM_BASE <= pa < self.ram_hi:
            if mask == 0xF:
                self.ram[pa] = data & MASK32
            else:
                expanded = 0
                for bit in range(4):
                    if mask & (1 << bit):
                        expanded |= 0xFF << (8 * bit)
                old = self.ram.get(pa, 0)
                self.ram[pa] = (old & ~expanded) | (data & expanded)
            return
        if IO_BASE <= pa < IO_BASE + IO_SIZE:
            self.io.write(pa - IO_BASE, data & MASK32, mask)
            return
        raise Stop(self._nothing(pa, "write of 0x%08x mask %x"
                                 % (data & MASK32, mask)))

    @staticmethod
    def _nothing(pa, what):
        if FLASH_BASE <= pa < FLASH_BASE + FLASH_SIZE:
            region = "the boot flash (no dump survives)"
        elif pa < IO_BASE + 0x800000 and pa >= IO_BASE:
            region = "the I/O range beyond the 4 KB implemented"
        elif RAM_BASE <= pa < DSP_SHADOW:
            region = "RAM beyond the configured size"
        elif DSP_SHADOW <= pa < DSP_SHADOW + 0x200000:
            region = "the DSPs' 2 MB shadow RAM"
        elif 0x80000000 <= pa < 0xE0000000:
            region = "BeBus slot %d" % ((pa >> 28) - 7)
        else:
            region = "an unassigned range"
        return "nothing modelled at physical 0x%08x (%s): %s" % (pa, region, what)


# ---------------------------------------------------------------------------
# The machine
# ---------------------------------------------------------------------------

class Cpu:
    def __init__(self, n, board, entry, stack):
        self.n = n
        self.sysm = hobbit_sem.System(bus=board)
        self.sysm.config = hobbit_sem.CONFIG_SE
        self.state = hobbit_sem.State(
            pc=entry, sp=stack, msp=stack, psw=hobbit_sem.PSW_SP,
            isp=stack, vb=0, config_kl=False, cache=[0] * 64,
            system=self.sysm)
        self.cycles = 0
        self.steps = 0
        self.idle_last = None       # ((steps, cycles, T1, T2), lap, steady)


def find_idle_head(elf):
    """CHOICES['idle-skip']: _null_thread+0x4, checked instruction by
    instruction; None (no skip) for any other kernel."""
    import hashlib
    if hashlib.sha256(elf.blob).hexdigest() != IDLE_KERNEL_SHA256:
        return None
    base = elf.by_name["_null_thread"]
    head = base + 4
    got = [t for _, t in elf.disassemble(head, head + 10)]
    want = [".3 CALL 0x%08x" % elf.by_name["_fix_3_minute_bug"],
            "ADD $1,R16", "JMP 0x%08x" % head]
    if got != want:
        raise SystemExit("beboot: _null_thread+0x4 is %r, not the idle loop "
                         "CHOICES['idle-skip'] was written for" % got)
    return head


def read_kernel(args):
    if args.kernel:
        return beelf.Elf(args.kernel), args.kernel
    vol = befs1.Volume(args.disk[0])
    data = vol.read(vol.lookup("/system/kernel"))
    path = os.path.join(args.workdir, "kernel")
    os.makedirs(args.workdir, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    return beelf.Elf(path), "%s:/system/kernel" % args.disk[0]


class Machine:
    def __init__(self, elf, memsize=16 << 20):
        self.elf = elf
        self.board = Board(memsize)
        self.board.on_reset = self.reset_changed
        self.regs = BoardRegs(self.board)
        io = self.board.io
        for n in range(8):
            io.add(IO_BASE + 3 + 4 * n, 3, self.regs, n, BoardRegs.NAMES[n])
        io.add(0x00800DC3, 3, WhoAmI(self.board), 0, "Who Am I")
        self.ser1 = Uart("SER1")
        self.ser2 = Uart("SER2")
        for n in range(8):
            io.add(port_addr(0x3F8 + n), 3, self.ser1, n,
                   "SER1 " + Uart.NAMES[n])
            io.add(port_addr(0x2F8 + n), 3, self.ser2, n,
                   "SER2 " + Uart.NAMES[n])
        self.rtc = Mc146818(lambda: self.cpus[0].cycles / CPU_HZ)
        io.add(port_addr(0x70), 3, self.rtc, 0, "RTC index")
        io.add(port_addr(0x71), 3, self.rtc, 1, "RTC data")
        self.regs.io_sources[4] = self.rtc_irq
        self.disks = {}
        self.ncr = Ncr53c94(self.disks, NCR_IRQ_DELAY,
                            lambda: self.cpus[0].cycles)
        for n in range(16):
            io.add(NCR_BASE + 4 * n, 2, self.ncr, n, "53C94 register %d" % n)
        io.add_word(NCR_PDMA, PdmaPort(self.ncr), "53C94 pseudo-DMA")
        self.regs.io_sources[7] = self.ncr.irq
        self.fdc = Mcs3201({1: {"medium": None, "cyl": 0}},
                           lambda: self.cpus[0].cycles / CPU_HZ)
        for n in (2, 4, 5, 7):
            io.add(port_addr(0x370 + n), 3, self.fdc, n,
                   "MCS3201 " + Mcs3201.NAMES[n])
        self.regs.io_sources[0] = self.fdc.irq
        self.kbc = Vl82c106Kbc()
        io.add(port_addr(0x60), 3, self.kbc, 0, "keyboard data")
        io.add(port_addr(0x64), 3, self.kbc, 4, "keyboard status/command")
        self.regs.io_sources[5] = self.kbc.kbd_irq
        self.regs.io_sources[6] = self.kbc.mouse_irq
        self.par = Parallel()
        for n, name in enumerate(("data", "status", "control")):
            io.add(port_addr(0x378 + n), 3, self.par, n, "printer " + name)
        # SER1 on bit 1, SER2 on bit 2: both kernels' _ser_init
        # (_io_int_set(1, _sera_inth)); the 1993 draft has them the other
        # way round (docs/bebox_hardware.md section 5).
        self.regs.io_sources[1] = self.ser1.irq
        self.regs.io_sources[2] = self.ser2.irq
        for addr, word in elf.words().items():
            if not (RAM_BASE <= addr < self.board.ram_hi):
                raise SystemExit("beboot: kernel word at 0x%08x is outside "
                                 "RAM" % addr)
            self.board.ram[addr] = word
        self.board.ram[MEMSIZE_WORD] = memsize
        top = RAM_BASE + memsize
        self.cpus = [Cpu(1, self.board, elf.entry, top - 0x1000 + 0x800)]
        self.cycles = 0
        self.reached = []
        self.seen = set()
        self.events = collections.deque(maxlen=200)
        self.interrupts = 0
        self.trace = None           # deque of pre-states (--trace N)
        self.idle_head = find_idle_head(elf)
        self.idle_skip = self.idle_head is not None
        self.skips = self.skipped_steps = 0
        text = elf.sections[".text"]
        self.text_lo, self.text_hi = text[3], text[3] + text[5]

    def rtc_irq(self):
        return False            # no periodic, alarm or update interrupt yet

    def reset_changed(self, old, new):
        if new & 2 and not old & 2 and len(self.cpus) == 1:
            top = RAM_BASE + self.board.memsize
            cpu = Cpu(2, self.board, self.elf.entry, top - 0x2000 + 0x800)
            cpu.cycles = self.cpus[0].cycles
            self.cpus.append(cpu)
            self.events.append((self.cpus[0].steps, "CPU 2 released"))
        elif old & 2 and not new & 2 and len(self.cpus) == 2:
            raise Stop("CPU 2 put back into reset (not modelled)")

    def deliver(self, cpu):
        """CHOICES['interrupts']: one interrupt per instruction boundary,
        the lowest level first."""
        st = cpu.state
        sysm = cpu.sysm
        i = cpu.n - 1
        ipl = (st.psw >> hobbit_sem.PSW_IPL_SHIFT) & 7
        if ipl <= 1:
            return
        if sysm.timer1_pending:
            sysm.timer1_pending = False
            hobbit_sem.take_interrupt(st, 1, 44)
        elif sysm.timer2_pending:
            sysm.timer2_pending = False
            hobbit_sem.take_interrupt(st, 1, 48)
        elif self.regs.internal & (1 << i):
            hobbit_sem.take_interrupt(st, 1)
        elif ipl > 3 and self.regs.io_status() & self.regs.io_mask[i]:
            hobbit_sem.take_interrupt(st, 3)
        else:
            return
        self.interrupts += 1

    def next_event(self):
        """The model cycle (CPU 1's clock) of the next timed device event,
        or None."""
        due = []
        if self.ncr.int_at is not None:
            due.append(self.ncr.int_at)
        due.extend(t * CPU_HZ for t, _, _ in self.fdc.pending)
        return min(due) if due else None

    def try_idle_skip(self, cpu, budget):
        """CHOICES['idle-skip']: called with `cpu` at the idle head after
        its interrupt check; returns the steps skipped.  A lap is measured,
        not computed: its steps, model cycles and the two timers' own
        increments (which differ from model cycles where an instruction
        retires in 0 cycles), between two visits to the head."""
        sysm = cpu.sysm
        here = (cpu.steps, cpu.cycles, sysm.timer1, sysm.timer2)
        last = cpu.idle_last
        lap = None
        if last is not None:
            lap = tuple((x - y) & MASK32 if i >= 2 else x - y
                        for i, (x, y) in enumerate(zip(here, last[0])))
        steady = lap is not None and last[1] == lap and lap[1] > 0
        cpu.idle_last = (here, lap, steady)
        if not steady:
            return 0
        horizon = self.next_event()
        limits = {}
        for c in self.cpus:
            st = c.state
            sysm = c.sysm
            if (st.pc != self.idle_head or c.idle_last is None
                    or c.idle_last[0][0] != c.steps or not c.idle_last[2]):
                return 0
            if (st.psw & hobbit_sem.PSW_USER
                    or (st.psw >> hobbit_sem.PSW_IPL_SHIFT) & 7 <= 3):
                return 0
            if (sysm.timer1_pending or sysm.timer2_pending
                    or self.regs.internal & (1 << (c.n - 1))
                    or self.regs.io_status() & self.regs.io_mask[c.n - 1]):
                return 0
            if not hobbit_sem._in_cache(st, (st.sp + 16) & ~3):
                return 0
            steps, cyc, d1, d2 = c.idle_last[1]
            # Laps before an enabled timer would overflow; that overflow
            # is an event for every CPU, so it bounds the model time.
            for ie, value, d in ((hobbit_sem.CONFIG_T1IE, sysm.timer1, d1),
                                 (hobbit_sem.CONFIG_T2IE, sysm.timer2, d2)):
                if sysm.config & ie and d:
                    laps = ((1 << 32) - 1 - value) // d
                    t = c.cycles + laps * cyc
                    horizon = t if horizon is None else min(horizon, t)
        if horizon is None:
            raise Stop("idle on every CPU with no timer running and no "
                       "device event pending: the loop would never end")
        plan = []
        for c in self.cpus:
            steps, cyc, d1, d2 = c.idle_last[1]
            n = (int(horizon) - 1 - c.cycles) // cyc
            plan.append((c, n, steps, cyc, d1, d2))
        # Each CPU laps on its own until just before the horizon, as it
        # would unskipped: the two laps need not be the same length.
        total = sum(p[1] * p[2] for p in plan)
        if any(p[1] <= 0 for p in plan) or total > budget:
            return 0
        for c, n, steps, cyc, d1, d2 in plan:
            st = c.state
            w = (st.sp + 16) & ~3
            st.cache[(w >> 2) & 63] = (st.cache[(w >> 2) & 63] + n) & MASK32
            c.steps += n * steps
            c.cycles += n * cyc
            c.sysm.timer1 = (c.sysm.timer1 + n * d1) & MASK32
            c.sysm.timer2 = (c.sysm.timer2 + n * d2) & MASK32
            c.idle_last = ((c.steps, c.cycles, c.sysm.timer1, c.sysm.timer2),
                           (steps, cyc, d1, d2), True)
        self.skips += 1
        self.skipped_steps += total
        return total

    def run(self, max_steps, until=None):
        status = "max-steps"
        cpu = self.cpus[0]
        try:
            total = 0
            while total < max_steps:
                cpu = min(self.cpus, key=lambda c: c.cycles)
                self.board.current_cpu = cpu.n
                st = cpu.state
                pc = st.pc
                if not st.psw & hobbit_sem.PSW_USER:
                    # Kernel code outside the text is legitimate: a new
                    # thread's first instructions are a trampoline that
                    # _setup_thread_ctx writes on its stack.
                    if self.text_lo <= pc < self.text_hi:
                        name = self.elf.func(pc)[0]
                    else:
                        name = "kernel code at 0x%08x" % (pc & ~0xFFF)
                    if name not in self.seen:
                        self.seen.add(name)
                        self.reached.append((total, cpu.n, name))
                if self.trace is not None:
                    self.trace.append((total, cpu.n, pc, st.sp, st.msp,
                                       st.isp, st.psw, cpu.sysm.shad))
                rec, cpu.state = hobbit_sem.step(st)
                st = cpu.state
                cpu.steps += 1
                total += 1
                cpu.cycles += max(rec.cyc, 1)
                self.deliver(cpu)
                if self.idle_skip and cpu.state.pc == self.idle_head:
                    total += self.try_idle_skip(cpu, max_steps - total)
                if cpu.sysm.events:
                    for kind, ident, epc in cpu.sysm.events:
                        self.events.append((total, "CPU %d %s 0x%x at %s %s" % (
                            cpu.n, kind, ident, self.elf.where(epc),
                            rec.reason if rec.trap else "")))
                    del cpu.sysm.events[:]
                if until is not None and until in self.ser1.out:
                    status = "until: %r on SER1" % until.decode("latin-1")
                    break
        except hobbit_sem.Refusal as exc:
            status = "REFUSED on CPU %d at %s (pc %08x, parcels %s): %s" % (
                cpu.n, self.elf.where(cpu.state.pc), cpu.state.pc,
                " ".join("%04x" % p for p in exc.parcels), exc.reason)
        except Stop as exc:
            status = "STOP on CPU %d at %s (pc %08x): %s" % (
                cpu.n, self.elf.where(cpu.state.pc), cpu.state.pc, exc)
        self.steps = sum(c.steps for c in self.cpus)
        return status


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--disk", action="append", default=[],
                    help="a Hobbit BeBox disk image (befs1); SCSI target 0, "
                         "then 1, ... (CHOICES['disks'])")
    ap.add_argument("--kernel", help="the kernel ELF file instead of the "
                    "disk's /system/kernel")
    ap.add_argument("--workdir", default=os.path.join(HERE, "..", "build",
                                                      "bebox", "beboot"))
    ap.add_argument("--memsize", type=int, default=16, help="MB")
    ap.add_argument("--max-steps", type=int, default=2000000)
    ap.add_argument("--trace", type=int, default=0,
                    help="print the last N instructions before the stop")
    ap.add_argument("--show", type=int, default=40,
                    help="print the last N first-reached functions")
    ap.add_argument("--until", help="stop once SER1 has printed this text")
    ap.add_argument("--no-idle-skip", action="store_true",
                    help="execute every idle lap (CHOICES['idle-skip'])")
    args = ap.parse_args(argv)
    if not args.disk and not args.kernel:
        ap.error("give --disk or --kernel")
    elf, source = read_kernel(args)
    m = Machine(elf, args.memsize << 20)
    if args.no_idle_skip:
        m.idle_skip = False
    for i, path in enumerate(args.disk):
        m.disks[i] = ScsiDisk(path, "target %d" % i)
    print("beboot: %s, entry 0x%08x, %d MB" % (source, elf.entry,
                                               args.memsize))
    if args.trace:
        m.trace = collections.deque(maxlen=args.trace)
    status = m.run(args.max_steps,
                   args.until.encode("latin-1") if args.until else None)
    for step, cpu, name in m.reached[-args.show:]:
        print("reached %9d CPU %d %s" % (step, cpu, name))
    for step, what in list(m.events)[-20:]:
        print("event %9d %s" % (step, what))
    for i, d in sorted(m.disks.items()):
        print("SCSI target %d: %d blocks read, %d written (overlay)"
              % (i, d.reads, d.writes))
    print("interrupts taken: %d" % m.interrupts)
    if m.skips:
        print("idle skip: %d skips, %d steps not executed"
              % (m.skips, m.skipped_steps))
    print("SER1: %r" % bytes(m.ser1.out).decode("latin-1"))
    if m.ser2.out:
        print("SER2: %r" % bytes(m.ser2.out).decode("latin-1"))
    print("beboot: %d steps (%s), %d functions reached"
          % (m.steps, ", ".join("CPU %d %d" % (c.n, c.steps) for c in m.cpus),
             len(m.reached)))
    if m.trace:
        for (n, c, pc, sp, msp, isp, psw, shad) in m.trace:
            text = ""
            if elf.text_lo <= pc < elf.text_hi if hasattr(elf, "text_lo") else m.text_lo <= pc < m.text_hi:
                text = elf.disassemble(pc, pc + 2)[0][1]
            print("trace %9d CPU %d %08x %-26s sp %08x msp %08x isp %08x "
                  "psw %08x shad %08x  %s" % (n, c, pc, elf.where(pc), sp, msp,
                                              isp, psw, shad, text))
    print("beboot: " + status)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
