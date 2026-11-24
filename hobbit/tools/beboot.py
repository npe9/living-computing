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
              "hobbit_sem.System's default (92010 mask two).  The Nov 1994 "
              "kernel compares it with 0x0E33D03B (its 92020 value) to "
              "choose its '020' code; the board's real part is a 92010 "
              "(docs/bebox_hobbit.md).",
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

    def read(self, off):
        lane, dev, reg, name = self._find(off, "a read")
        return (dev.read(reg) & 0xFF) << (8 * (3 - lane))

    def write(self, off, data, mask):
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
    from `feed`."""

    NAMES = ["RBR/THR/DLL", "IER/DLM", "IIR/FCR", "LCR", "MCR", "LSR",
             "MSR", "SCR"]

    def __init__(self, name):
        self.name = name
        self.out = bytearray()
        self.rx = collections.deque()
        self.ier = self.lcr = self.mcr = self.scr = 0
        self.dll = self.dlm = 0
        self.fcr = 0

    def feed(self, data):
        self.rx.extend(data)

    def irq(self):
        return bool((self.ier & 1 and self.rx) or self.ier & 2)

    def read(self, reg):
        dlab = self.lcr & 0x80
        if reg == 0:
            if dlab:
                return self.dll
            return self.rx.popleft() if self.rx else 0
        if reg == 1:
            return self.dlm if dlab else self.ier
        if reg == 2:
            if self.ier & 1 and self.rx:
                return 0x04
            if self.ier & 2:
                return 0x02
            return 0x01
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
        elif reg == 1:
            if dlab:
                self.dlm = value
            else:
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


def read_kernel(args):
    if args.kernel:
        return beelf.Elf(args.kernel), args.kernel
    vol = befs1.Volume(args.disk)
    data = vol.read(vol.lookup("/system/kernel"))
    path = os.path.join(args.workdir, "kernel")
    os.makedirs(args.workdir, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    return beelf.Elf(path), "%s:/system/kernel" % args.disk


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
        self.par = Parallel()
        for n, name in enumerate(("data", "status", "control")):
            io.add(port_addr(0x378 + n), 3, self.par, n, "printer " + name)
        self.regs.io_sources[2] = self.ser1.irq
        self.regs.io_sources[1] = self.ser2.irq
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
        self.events = []
        self.trace = None           # deque of pre-states (--trace N)
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
    ap.add_argument("--disk", help="a Hobbit BeBox disk image (befs1)")
    ap.add_argument("--kernel", help="the kernel ELF file instead of the "
                    "disk's /system/kernel")
    ap.add_argument("--workdir", default=os.path.join(HERE, "..", "build",
                                                      "bebox", "beboot"))
    ap.add_argument("--memsize", type=int, default=16, help="MB")
    ap.add_argument("--max-steps", type=int, default=2000000)
    ap.add_argument("--trace", type=int, default=0,
                    help="print the last N instructions before the stop")
    ap.add_argument("--until", help="stop once SER1 has printed this text")
    args = ap.parse_args(argv)
    if not args.disk and not args.kernel:
        ap.error("give --disk or --kernel")
    elf, source = read_kernel(args)
    m = Machine(elf, args.memsize << 20)
    print("beboot: %s, entry 0x%08x, %d MB" % (source, elf.entry,
                                               args.memsize))
    if args.trace:
        m.trace = collections.deque(maxlen=args.trace)
    status = m.run(args.max_steps,
                   args.until.encode("latin-1") if args.until else None)
    for step, cpu, name in m.reached[-40:]:
        print("reached %9d CPU %d %s" % (step, cpu, name))
    for step, what in m.events[-20:]:
        print("event %9d %s" % (step, what))
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
