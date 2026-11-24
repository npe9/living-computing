#!/usr/bin/env python3
"""Boot a 1st Edition Plan 9 Hobbit kernel image on the reference model.

`sem/hobbit_sem.py` executes the instructions with its privileged
machine (`hobbit_sem.System`: control registers, CSP = ISP, the MMU walk,
the event sequences -- all from the printed PRM).  This file is the
*board*: the memory, the boot ROM's hand-off and the devices the kernel
touches, each taken from the kernel's own sources in
`tools/plan9-1e/sys/src/9/hobbit/` (io.h, mem.h, rom.h, deveia.c, ...).
What the sources do not say is a choice, named in `CHOICES` below and in
docs/p9boot.md; nothing is left as a silent default.

The image is a `zl -H1` kernel (docs/s9term.md): text and data are loaded
at their link addresses, which are physical RAM (mem.h: KZERO = RAMBASE =
0x80000000), and the part starts at the entry in the reset state of PRM
p. 1-35 (PSW = 0, CONFIG = 0, SHAD = 0) -- the state the boot ROM would
have reached the kernel in had it jumped there; see CHOICES["reset"].

The run stops, loudly, at the first thing the model cannot do: a refusal
of the reference model, a physical address no device claims, an entry to
the boot ROM (the kernel's `softreset`, its panic path), or the step
limit.  It reports the function reached (from the image's symbols), the
instruction count, every function reached for the first time in order
(the milestones), and the bytes the kernel wrote to each console channel:

  uart<n>     bytes written to the Quart's transmit holding registers
  screenputs  the (s, n) arguments of each call to `screenputs`, read at
              the function's entry -- a harness tap on the kernel's own
              screen output, not a device (the bitmap itself is memory)

    python3 tools/p9boot.py tools/plan9-1e/hobbit/s9term --max-steps N \\
        [--out DIR]
"""

import argparse
import bisect
import calendar
import collections
import math
import os
import pathlib
import socket
import struct
import sys
import time
import zlib

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "sem"))
import p9exec          # noqa: E402
import hobbit_sem      # noqa: E402

MASK32 = 0xFFFFFFFF

# mem.h / io.h
RAMBASE = 0x80000000
IOBASE = 0xB0000000
IONAK = IOBASE + 0x08000000
PROMBASE = 0x00000000
VROMBASE = 0xC0000000

# Every modelling choice the sources leave open, with its reason.
CHOICES = {
    "memsize": "8 MB of RAM at 0x80000000 (PPage0.memsize = 8 MB). The "
               "ROM measures it (rommain.c meminit: memsize = 1 MB steps "
               "until a write does not read back); the size of a 1993 "
               "board is not in the release.",
    "ram-init": "RAM not loaded from the image reads as 0 (real DRAM "
                "would hold garbage; _startup clears only the STB and "
                "Mach pages and _virtual the BSS).",
    "ppage0": "The ROM's hand-off page (rom.h PPage0 at RAMBASE): "
              "memsize as above, argc = 0, env.nentry = 0, everything "
              "else 0, except the word at 0x74 (below).",
    "fpi-vector": "PPage0+0x74, which s9term's _virtual copies into the "
                  "niladic-trap and unimplemented-instruction vectors "
                  "(VB+8, VB+12), holds ROM_SENTINEL: the release ships "
                  "no ROM image (fpi lives there), so reaching it stops "
                  "the run.",
    "reset": "The kernel starts at its entry with the PRM reset state "
             "(p. 1-35: PSW = 0, CONFIG = 0, SHAD = 0, PC = entry instead "
             "of 0) and SP = MSP = ISP = VB = STB = 0 (undefined after an "
             "external reset, p. 1-36); the ROM's own state at its jump "
             "is not known.",
    "irq-level": "Every board interrupt reaches the part at IL 6: "
                 "s9term's vector table sends only 'interrupt 6' to "
                 "interrupt() (raml.s _vectors), every other level to "
                 "trap(), which panics.",
    "irq-status": "Irq.status0/1 report the raw request of each source "
                  "(bit n = io.h IRQ number n); IL 6 is asserted while "
                  "(status & mask) != 0. interrupt() masks status with "
                  "its own copy of the enables, which suggests status is "
                  "unmasked.",
    "clock": "Model time is the sum of the records' Chapter 4 cycles at "
             "20 MHz, the lower of the data sheet's two rated clocks "
             "(ATT92010 data sheet p. 1, Table 44). It paces the Quart's "
             "counter, i.e. the kernel's clock interrupt.",
    "iic": "The PCF8584 IIC controller (io.h IICADDR) and the PCF8582 "
           "EEPROM behind it answer deviic.c's sequences (IIC_CHOICES): "
           "iicreset reads io.h's Eeprom, whose ether address devether.c "
           "uses and whose clock (20) paces delay().",
    "rtc": "io.h's Nvram (IONAK 0x2000, 2040 bytes) and RTCdev (IONAK "
           "0x3FE0, eight words) are one 2K-byte timekeeper's NVRAM and "
           "clock registers, a byte per word in bits 7:0 (Nvram's uchar "
           "val; pad[3]): control, then sec, min, hour, wday, mday, mon, "
           "year in BCD.  devrtc.c's RTCREAD (0x40) and RTCWRITE (0x80) "
           "bits are taken to freeze the registers for a read and to "
           "load them when RTCWRITE clears (the scheme of the MK48T02 "
           "class of part; no data sheet is in the release).  The clock "
           "starts at 1993-01-03 12:00:00 UTC (the QEMU server's -rtc "
           "base, docs/qemu_1e_server.md) and runs on model time; NVRAM "
           "starts zero.",
    "lcd": "Bart's LCD (io.h Lcdisp at IOACK 0x3000) accepts and counts "
           "writes; it is never read by the kernel.",
    "cret-msp": "hobbit_sem.System.cret_clamp is on: a CRET whose restored "
                "MSP is more than 256 bytes above its SP has its CATCH "
                "portion stop with the cache full (p. 3-10: 'or the cache "
                "is full') and MSP = SP + 256, instead of the reference "
                "model's refusal.  p. 1-13 calls stack-cache results with "
                "MSP > SP + 256 unpredictable, but s9term's notify() "
                "builds exactly such a frame (it lowers the user SP by "
                "0x170 for the Ureg, the note and the arguments and keeps "
                "MSP), and raml.s's _exception resets an MSP found above "
                "SP + SCSIZE on entry, so the kernel expected the state "
                "to occur.  The run reports how many CRETs were clamped.",
    "console-input": "The console's input is Quart channel 0: s9term's "
                     "screeninit calls eiaspecial(0, &printq, &kbdq, 19200) "
                     "and eiaspecial(3, 0, &mouseq, 1200) (observed at the "
                     "calls, step 127,557 and 127,705) and never kbdinit "
                     "-- its screen.c predates kbd.c (docs/s9term.md), so "
                     "there are no scan codes: kbdq.putc is kbdcr2nl, "
                     "ASCII with CR made NL, as from a serial terminal.  "
                     "--type TEXT=REPLY types REPLY on that line once the "
                     "screen has shown TEXT (after the previous match), "
                     "--think seconds later (default 0), at the line's "
                     "character rate (QUART_CHOICES['rx']).  TEXT is seen "
                     "at screenputs' entry, before the ~0.4 M instructions "
                     "that draw it, so with no think time the reply arrives "
                     "while the prompt is still being drawn and its echo "
                     "reaches Quart channel 0 before the prompt does "
                     "(putstrn draws, then calls uartputs).",
    "idle-skip": "A harness shortcut, on by default (--no-idle-skip turns "
                 "it off).  s9term's idle loop is runproc+0x8..+0x1e (proc.c "
                 "`while(runhiq.head==0 && runloq.head==0);` with spllo): "
                 "two compares of the run-queue heads with 0 and two "
                 "conditional jumps, no stores.  When the PC is at its head "
                 "with both heads 0, IPL 7 and no interrupt asserted, and "
                 "the last two iterations cost the same cycles, the harness "
                 "retires N whole iterations at once: steps += 4N, cycles "
                 "+= N x (cycles per iteration), with N the largest count "
                 "that ends before the next timed device event (the Quart "
                 "counter, a scripted byte, a frame).  The iterations "
                 "executed afterwards, the interrupt and everything after "
                 "it are the run without the skip, instruction for "
                 "instruction (tests/test_p9boot.py compares the two).  "
                 "TIMER1/TIMER2 are advanced by the same cycles and "
                 "instructions; the skip is not taken while a timer "
                 "interrupt is enabled.  With nothing timed pending the "
                 "loop could never end, and the run stops.",
}

CPU_HZ = 20000000                   # CHOICES['clock']
ROM_SENTINEL = VROMBASE + 0xF00     # virtual; physical PROMBASE + 0xF00
PPAGE0_MEMSIZE = 0x80
PPAGE0_ARGC = 0x200
PPAGE0_ENV = 0x300
PPAGE0_FPI = 0x74
MEMSIZE = 8 * 1024 * 1024


class Stop(Exception):
    pass


class Board:
    """Physical address space: RAM, the boot ROM's range and the devices.

    `read(pa)` and `write(pa, data, mask)` are the `hobbit_sem.System.bus`
    contract (mask bit 3 = bits 31:24)."""

    def __init__(self, memsize=MEMSIZE):
        self.ram = {}
        self.ram_lo = RAMBASE
        self.ram_hi = RAMBASE + memsize
        self.devices = []           # (lo, hi, device)
        self.log = []

    def add(self, lo, hi, dev):
        self.devices.append((lo, hi, dev))

    def _device(self, pa):
        for lo, hi, dev in self.devices:
            if lo <= pa < hi:
                return dev, pa - lo
        return None, 0

    def read(self, pa):
        pa &= ~3 & MASK32
        if self.ram_lo <= pa < self.ram_hi:
            return self.ram.get(pa, 0)
        dev, off = self._device(pa)
        if dev is None:
            if PROMBASE <= pa < PROMBASE + 0x80000:
                raise Stop("read of the boot ROM at physical 0x%08x (the "
                           "release ships no ROM image)" % pa)
            raise hobbit_sem.BusError("bus: no device at physical 0x%08x "
                                      "(read)" % pa)
        return dev.read(off) & MASK32

    def write(self, pa, data, mask):
        pa &= ~3 & MASK32
        if self.ram_lo <= pa < self.ram_hi:
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
        dev, off = self._device(pa)
        if dev is None:
            raise hobbit_sem.BusError("bus: no device at physical 0x%08x "
                                      "(write 0x%08x mask %x)"
                                      % (pa, data, mask))
        dev.write(off, data & MASK32, mask)

    # byte helpers for the harness (the kernel runs little-endian: CONFIG.KL)
    def byte(self, pa):
        return (self.read(pa) >> (8 * (pa & 3))) & 0xFF

    def set_word(self, pa, value):
        self.write(pa, value, 0xF)


class Register:
    """A plain read/write word (IOCTL, io.h IOCTLADDR = IONAK(ulong, 0))."""

    def __init__(self, name, value=0):
        self.name = name
        self.value = value

    def read(self, off):
        if off:
            raise hobbit_sem.BusError("%s: no register at +0x%x"
                                      % (self.name, off))
        return self.value

    def write(self, off, data, mask):
        if off or mask != 0xF:
            raise hobbit_sem.BusError("%s: write at +0x%x mask %x"
                                      % (self.name, off, mask))
        self.value = data


class Irq:
    """io.h `Irq` at IONAK(Irq, 0x0080): mask0, mask1, status0, status1.

    status bit n is the request of io.h IRQ n (IRQQUART 1, IRQINCON 5,
    IRQSCSIDMA 8, IRQSONIC 9, IRQSCSI 10); the sources are polled.
    CHOICES['irq-status'] and ['irq-level']."""

    def __init__(self):
        self.mask = [0, 0]
        self.sources = {}           # irq number -> callable() -> bool

    def status(self):
        st = 0
        for n, f in self.sources.items():
            if f():
                st |= 1 << n
        return st

    def read(self, off):
        idx = off // 4
        if idx in (0, 1):
            return self.mask[idx]
        if idx == 2:
            return self.status() & 0xFF
        if idx == 3:
            return (self.status() >> 8) & 0xFF
        raise hobbit_sem.BusError("Irq: read at +0x%x" % off)

    def write(self, off, data, mask):
        idx = off // 4
        if idx in (0, 1) and mask == 0xF:
            self.mask[idx] = data & 0xFF
            return
        raise hobbit_sem.BusError("Irq: write at +0x%x" % off)

    def asserted(self):
        enabled = self.mask[0] | (self.mask[1] << 8)
        return bool(self.status() & enabled)


class Quart:
    """io.h `Quart` (Signetics 68C94) at IOACK(Quart, 0x0100).

    The register map is io.h's (each `unsigned` is one word); behaviour is
    what deveia.c relies on, and the rest is a stated choice (QUART_CHOICES
    below, docs/p9boot.md).  The release has no data sheet for the part."""

    def __init__(self, ticks_per_second, clock):
        self.clock = clock          # callable() -> model time in seconds
        self.ports = [dict(mr=[0, 0], mrp=0, csr=0, tx=False, rx=False,
                           out=bytearray(), fifo=collections.deque(),
                           pending=collections.deque(), next_rx=None,
                           received=0) for _ in range(4)]
        self.duarts = [dict(acr=0, imr=0, ctu=0, ctl=0, opr=0, iopcra=0,
                            iopcrb=0, running=False, ready=False,
                            next_tick=None) for _ in range(2)]
        self.glob = dict(bcr=[0, 0, 0, 0], icr=0, brg=0, setclk=[0, 0],
                         cir=0, gicr=0, gibcr=0, ack=0, nak=0, pwr=None)
        self.hz = ticks_per_second
        # QUART_CHOICES['counter-period']: None follows the count.
        self.period_override = None
        self.writes = collections.Counter()

    # --- the counter/timer: QUART_CHOICES['counter'] -------------------
    def _tick(self, d):
        du = self.duarts[d]
        if du["running"] and du["next_tick"] is not None:
            now = self.clock()
            if now >= du["next_tick"]:
                du["ready"] = True
                period = self._period(d)
                while du["next_tick"] <= now:
                    du["next_tick"] += period

    def _period(self, d):
        du = self.duarts[d]
        count = (du["ctu"] << 8) | du["ctl"]
        if (du["acr"] & 0x70) != 0x70 or count == 0:
            raise Stop("Quart: counter %d started in a mode the model does "
                       "not have (acr 0x%02x, count %d)"
                       % (d, du["acr"], count))
        if self.period_override is not None:
            return self.period_override
        # deveia.c clockinit: x = Crystal/(2*16*HZ), acr = TimerD16; one
        # CtrRDY per square-wave period, i.e. every 2*x clocks of X1/16.
        return 2.0 * count / (3686400 / 16.0)

    # --- the receivers: QUART_CHOICES['rx'], ['rx-line'] -----------------
    def char_time(self, ch):
        """Seconds per character on channel ch: 1 start bit, the mr1 data
        bits and parity, the mr2 stop bits, at the csr's rate (deveia.c's
        BD* codes, BRGSet2)."""
        port = self.ports[ch]
        baud = CSR_BAUD.get(port["csr"])
        if baud is None:
            raise Stop("Quart: input on channel %d at csr 0x%02x, a rate "
                       "the model does not know" % (ch, port["csr"]))
        mr1, mr2 = port["mr"]
        bits = 1 + 5 + (mr1 & 3) + (0 if mr1 & 0x10 else 1)
        bits += 2 if (mr2 & 0x0F) == 0x0F else 1
        return bits / float(baud)

    def feed(self, ch, data, delay=0.0):
        """Bytes on channel ch's receive line, one character time apart,
        the first `delay` seconds and one character time from now."""
        port = self.ports[ch]
        if not port["pending"] and port["next_rx"] is None:
            port["next_rx"] = self.clock() + delay + self.char_time(ch)
        port["pending"].extend(data)

    def _rx(self, ch):
        port = self.ports[ch]
        now = self.clock()
        while (port["pending"] and port["next_rx"] is not None
               and now >= port["next_rx"]):
            if len(port["fifo"]) >= RX_FIFO or not port["rx"]:
                port["next_rx"] = None      # held: QUART_CHOICES['rx']
                break
            arrived = port["next_rx"]
            port["fifo"].append(port["pending"].popleft())
            port["received"] += 1
            port["next_rx"] = (arrived + self.char_time(ch)
                               if port["pending"] else None)

    def _rx_pop(self, ch):
        self._rx(ch)
        port = self.ports[ch]
        if not port["fifo"]:
            return 0
        c = port["fifo"].popleft()
        if port["pending"] and port["next_rx"] is None:
            port["next_rx"] = self.clock() + self.char_time(ch)
        return c

    def rx_ready(self, ch):
        self._rx(ch)
        return bool(self.ports[ch]["fifo"])

    def next_event(self):
        """The next time a counter expires or a byte arrives
        (CHOICES['idle-skip'])."""
        times = [p["next_rx"] for p in self.ports
                 if p["pending"] and p["next_rx"] is not None]
        for d in (0, 1):
            self._tick(d)
            du = self.duarts[d]
            if du["running"] and du["next_tick"] is not None:
                times.append(du["next_tick"])
        return min(times) if times else None

    def isr(self, d):
        self._tick(d)
        du = self.duarts[d]
        v = 0
        a, b = self.ports[2 * d], self.ports[2 * d + 1]
        if a["tx"]:
            v |= 0x01                       # TxRDYa
        if b["tx"]:
            v |= 0x10                       # TxRDYb
        if du["ready"]:
            v |= 0x08                       # CtrRDY
        if self.rx_ready(2 * d):
            v |= 0x02                       # RxRDYa
        if self.rx_ready(2 * d + 1):
            v |= 0x20                       # RxRDYb
        return v

    def irq(self):
        return any(self.isr(d) & self.duarts[d]["imr"] for d in (0, 1))

    def _update(self):
        """A write to `update` latches the current interrupt into cir,
        gicr and gibcr (deveia.c eiaintr).  QUART_CHOICES['cir']."""
        self.glob["cir"] = 0
        self.glob["gicr"] = 0
        self.glob["gibcr"] = 0
        for d in (0, 1):
            pend = self.isr(d) & self.duarts[d]["imr"]
            if pend & 0x08:
                self.glob.update(cir=0x14, gicr=2 * d, gibcr=0)
                return
        for d in (0, 1):
            pend = self.isr(d) & self.duarts[d]["imr"]
            for bit, ch in ((0x02, 2 * d), (0x20, 2 * d + 1)):
                if pend & bit:
                    n = min(len(self.ports[ch]["fifo"]), 7)
                    self.glob.update(cir=0x0C, gicr=ch, gibcr=n)
                    return
        for d in (0, 1):
            pend = self.isr(d) & self.duarts[d]["imr"]
            for bit, ch in ((0x01, 2 * d), (0x10, 2 * d + 1)):
                if pend & bit:
                    self.glob.update(cir=0x08, gicr=ch, gibcr=1)
                    return

    def read(self, off):
        idx = off // 4
        if idx < 0x20:
            d, r = divmod(idx, 16)
            du = self.duarts[d]
            port = self.ports[2 * d + (1 if r >= 8 else 0)]
            rr = r & 7 if r in (0, 1, 2, 3, 8, 9, 10, 11) else None
            if rr == 0:
                v = port["mr"][port["mrp"]]
                port["mrp"] = 1
                return v
            if rr == 1:                     # sr: QUART_CHOICES['sr']
                pn = 2 * d + (1 if r >= 8 else 0)
                v = 0x0C if port["tx"] else 0x00
                if self.rx_ready(pn):
                    v |= 0x01               # RxRDY
                    if len(port["fifo"]) >= RX_FIFO:
                        v |= 0x02           # FFULL
                return v
            if rr == 3:                     # rxfifo
                return self._rx_pop(2 * d + (1 if r >= 8 else 0))
            if r == 4:
                return 0                    # ipcr
            if r == 5:
                return self.isr(d)
            if r == 12:
                return du["opr"]
            if r == 13:
                return 0                    # ipr: inputs all 0
            if r == 14:                     # start counter
                du["running"] = True
                du["ready"] = False
                du["next_tick"] = self.clock() + self._period(d)
                return 0
            if r == 15:                     # stop: acknowledge CtrRDY
                self._tick(d)
                du["ready"] = False
                return 0
            if r in (6, 7):
                return du["ctu" if r == 6 else "ctl"]
        g = self.glob
        if idx == 0x28:
            return g["cir"]
        if idx == 0x29:
            return g["gicr"]
        if idx == 0x2A:
            return g["gibcr"]
        if idx == 0x2B:                     # grxfifo: the latched channel
            return self._rx_pop(g["gicr"] & 3)
        if idx == 0x2C:
            return g["icr"]
        if 0x20 <= idx < 0x24:
            return g["bcr"][idx - 0x20]
        raise Stop("Quart: read of +0x%x (register 0x%02x) is not modelled"
                   % (off, idx))

    def write(self, off, data, mask):
        if mask != 0xF:
            raise Stop("Quart: partial write at +0x%x" % off)
        idx = off // 4
        data &= 0xFF
        self.writes[idx] += 1
        if idx < 0x20:
            d, r = divmod(idx, 16)
            du = self.duarts[d]
            pn = 2 * d + (1 if r >= 8 else 0)
            port = self.ports[pn]
            rr = r & 7 if r in (0, 1, 2, 3, 8, 9, 10, 11) else None
            if rr == 0:
                port["mr"][port["mrp"]] = data
                port["mrp"] = 1
                return
            if rr == 1:
                port["csr"] = data
                return
            if rr == 2:                     # cr: QUART_CHOICES['cr']
                if data & 0x03 == 0x01:
                    port["rx"] = True
                    if port["pending"] and port["next_rx"] is None:
                        port["next_rx"] = self.clock() + self.char_time(pn)
                elif data & 0x03 == 0x02:
                    port["rx"] = False
                if data & 0x0C == 0x04:
                    port["tx"] = True
                elif data & 0x0C == 0x08:
                    port["tx"] = False
                cmd = data & 0x70
                if cmd == 0x10:
                    port["mrp"] = 0
                elif cmd == 0x30:
                    port["tx"] = False
                elif cmd == 0x20:
                    port["rx"] = False
                return
            if rr == 3:
                port["out"].append(data)
                return
            key = {4: "acr", 5: "imr", 6: "ctu", 7: "ctl", 12: "opr",
                   13: "iopcra", 14: "iopcrb"}.get(r)
            if key:
                du[key] = data
                return
        g = self.glob
        if 0x20 <= idx < 0x24:
            g["bcr"][idx - 0x20] = data
            return
        if idx in (0x24, 0x25):
            g["pwr"] = idx
            return
        if idx in (0x26, 0x27):
            g["nak" if idx == 0x26 else "ack"] += 1
            return
        if idx == 0x2A:
            self._update()
            return
        if idx == 0x2B:
            self.ports[g["gicr"] & 3]["out"].append(data)
            return
        if idx == 0x2C:
            g["icr"] = data
            return
        if idx == 0x2D:
            g["brg"] = data
            return
        if idx in (0x2E, 0x2F):
            g["setclk"][idx - 0x2E] = data
            return
        raise Stop("Quart: write of 0x%02x to +0x%x (register 0x%02x) is "
                   "not modelled" % (data, off, idx))


CSR_BAUD = {0x11: 110, 0x22: 38400, 0x44: 300, 0x55: 600, 0x66: 1200,
            0x88: 2400, 0x99: 4800, 0xBB: 9600, 0xCC: 19200}
RX_FIFO = 3

QUART_CHOICES = {
    "sr": "sr reads TxRDY|TxEMT (0x0C) while the channel's transmitter is "
          "enabled and 0 otherwise: a byte written to txfifo leaves at "
          "once. RxRDY (0x01) while the receive FIFO holds a byte, FFULL "
          "(0x02) while it holds three.",
    "rx": "Input (--type) arrives on a channel's receive line one "
          "character time apart (1 start bit, mr1's data and parity bits, "
          "mr2's stop bits, at csr's rate under BRGSet2: 19200 baud 8N1 = "
          "0.52 ms on channel 0) into a three-byte receive FIFO.  A byte "
          "that finds the FIFO full or the receiver disabled waits on the "
          "line (no overrun is modelled) and follows one character time "
          "after the next byte is read.  isr RxRDYa (0x02) / RxRDYb (0x20) "
          "while the FIFO is not empty (mr1 bit 6, FFULL interrupts, is 0 "
          "in deveia.c's uartsetup); grxfifo and rxfifo pop it, an empty "
          "FIFO reads 0.",
    "cr": "cr's enable/disable bits (deveia.c RxEnable 0x01, RxDisable "
          "0x02, TxEnable 0x04, TxDisable 0x08) and the reset commands "
          "MrReset 0x10 (mr pointer to mr1), RxReset 0x20, TxReset 0x30 "
          "change state; ErrReset, BrkStart/BrkStop and the rest are "
          "accepted and ignored.",
    "isr": "isr is TxRDYa (0x01) / TxRDYb (0x10) while the transmitter "
           "is enabled and CtrRDY (0x08) once the counter has expired "
           "until a read of `stop`; RxRDYa/b as QUART_CHOICES['rx'].",
    "counter": "The counter of each DUART, started by a read of `start`, "
               "sets CtrRDY every 2*count/(3.6864 MHz/16) seconds of "
               "model time (deveia.c clockinit's formula gives HZ = 25 "
               "per second that way).",
    "counter-period": "s9term's clockinit is older than the release's: it "
                      "writes ctu = ctl = 0xFF (count 65535, acr 0xF0), "
                      "which by the formula above is a CtrRDY every "
                      "0.569 s, while its tsleep divides by MS2HZ = 40 "
                      "(HZ = 25).  The default follows the count (the "
                      "hardware as documented); --counter-period 0.04 "
                      "gives the 25 Hz the software assumes, a stated "
                      "deviation for reaching the boot program sooner.",
    "cir": "A write of `update` latches the highest pending, enabled "
           "source: the counter (cir 0x14 CtAvail, gicr = 2*duart), then "
           "a receiver (cir 0x0C RxAvail, gicr = channel, gibcr = bytes in "
           "its FIFO), then a transmitter (cir 0x08 TxAvail0, gicr = "
           "channel, gibcr = 1); the order is a choice (the part's bidding "
           "registers bcr are written by eiasetup but not modelled).  "
           "With nothing pending cir reads 0, which ends eiaintr's loop.",
    "irq": "The Quart requests IRQ 1 (io.h IRQQUART) while any isr bit "
           "is enabled in its DUART's imr.",
}


class Symbols:
    def __init__(self, syms):
        text = sorted((v, n) for v, t, n in syms if t in "Tt")
        self.addrs = [v for v, _ in text]
        self.names = [n for _, n in text]
        self.by_name = {}
        for v, t, n in syms:
            self.by_name.setdefault(n, v)

    def func(self, pc):
        i = bisect.bisect_right(self.addrs, pc) - 1
        if i < 0:
            return "?", 0
        return self.names[i], self.addrs[i]

    def where(self, pc):
        name, base = self.func(pc)
        return "%s+0x%x" % (name, pc - base)


IDLE_LAP_STEPS = 4
CONSOLE_CHANNEL = 0     # s9term: eiaspecial(0, &printq, &kbdq, 19200)


def text_parcel(board, addr):
    """The parcel at a text address as loaded: the high half of a word is
    the earlier parcel (docs/s9term.md)."""
    w = board.ram.get(addr & ~3, 0)
    return (w & 0xFFFF) if addr & 2 else (w >> 16)


def find_idle_loop(boot):
    """CHOICES['idle-skip']: the idle loop of runproc, checked parcel for
    parcel in the image (a different image makes this fail loudly rather
    than skip the wrong code).  s9term, runproc = 0x80006492:

      +0x08  dffc 0000 0000 <runhiq+8>   compare $0 with runhiq.head
      +0x12  1007                        JMPFN +0x20 (a process: leave)
      +0x14  dffc 0000 0000 <runloq+8>   compare $0 with runloq.head
      +0x1e  1ff5                        JMPTY +0x08 (both empty: again)

    Returns the head's address and the two words the loop reads."""
    by = boot.syms.by_name
    base = by["runproc"]
    hi, lo = by["runhiq"] + 8, by["runloq"] + 8
    want = [(base + 0x08, [0xdffc, 0, 0, hi >> 16, hi & 0xFFFF]),
            (base + 0x12, [0x1007]),
            (base + 0x14, [0xdffc, 0, 0, lo >> 16, lo & 0xFFFF]),
            (base + 0x1e, [0x1ff5])]
    for addr, parcels in want:
        got = [text_parcel(boot.board, addr + 2 * i)
               for i in range(len(parcels))]
        if got != parcels:
            raise SystemExit("p9boot: runproc+0x%x is %s, not the idle loop "
                             "CHOICES['idle-skip'] was written for"
                             % (addr - base, " ".join("%04x" % p for p in got)))
    return base + 0x08, (hi, lo)


def load_kernel(path, board):
    k = p9exec.read_kernel(path)
    blob = k["blob"]
    for i in range(k["text"] // 4):
        off = k["text_off"] + 4 * i
        board.ram[k["textbase"] + 4 * i] = int.from_bytes(
            blob[off:off + 4], "little")
    for i in range((k["data"] + 3) // 4):
        off = k["data_off"] + 4 * i
        board.ram[k["database"] + 4 * i] = int.from_bytes(
            blob[off:off + 4].ljust(4, b"\0"), "little")
    return k


def rom_handoff(board, memsize):
    """CHOICES['ppage0'] / ['fpi-vector']."""
    board.set_word(RAMBASE + PPAGE0_MEMSIZE, memsize)
    board.set_word(RAMBASE + PPAGE0_ARGC, 0)
    board.set_word(RAMBASE + PPAGE0_ENV, 0)
    board.set_word(RAMBASE + PPAGE0_FPI, ROM_SENTINEL)


class Timekeeper:
    """io.h Nvram (IONAK 0x2000, 2040 bytes) and RTCdev (IONAK 0x3FE0):
    one byte per word, in bits 7:0 (CHOICES['rtc']).  The eight RTCdev
    words are a timekeeper's control, sec, min, hour, wday, mday, mon,
    year in BCD; devrtc.c sets RTCREAD (0x40) in control to read them
    and RTCWRITE (0x80) to set them.  The clock runs on model time from
    `base` (seconds since 1970)."""

    NVRAM = 0x0000
    NVRAMLEN = 2040
    RTC = 0x1FE0

    def __init__(self, clock, base):
        self.clock = clock
        self.offset = base          # epoch seconds at model time 0
        self.nvram = bytearray(self.NVRAMLEN)
        self.control = 0
        self.held = None            # the registers while R or W is set
        self.sets = []              # (model time, epoch seconds) written

    def now(self):
        return int(self.offset + self.clock())

    def _regs(self, t):
        tm = time.gmtime(t)
        bcd = lambda v: ((v // 10) << 4) | (v % 10)
        return [bcd(tm.tm_sec), bcd(tm.tm_min), bcd(tm.tm_hour),
                bcd((tm.tm_wday + 1) % 7 + 1), bcd(tm.tm_mday),
                bcd(tm.tm_mon), bcd(tm.tm_year % 100)]

    def read(self, off):
        if off < self.NVRAMLEN * 4:
            return self.nvram[off >> 2]
        i = (off - self.RTC) >> 2
        if i == 0:
            return self.control
        regs = self.held if self.held is not None else self._regs(self.now())
        return regs[i - 1]

    def write(self, off, data, mask):
        v = data & 0xFF
        if off < self.NVRAMLEN * 4:
            self.nvram[off >> 2] = v
            return
        i = (off - self.RTC) >> 2
        if i:
            if self.held is None or not self.control & 0x80:
                raise hobbit_sem.BusError(
                    "rtc: clock register %d written without RTCWRITE" % i)
            self.held[i - 1] = v
            return
        was = self.control
        self.control = v
        if v & 0xC0 and not was & 0xC0:
            self.held = self._regs(self.now())
        elif was & 0x80 and not v & 0x80:
            dec = [((b >> 4) * 10) + (b & 15) for b in self.held]
            year = dec[6] + (2000 if dec[6] < 70 else 1900)
            t = calendar.timegm((year, dec[5], dec[4], dec[2] & 0x3F,
                                 dec[1], dec[0] & 0x7F, 0, 0, 0))
            self.offset = t - self.clock()
            self.sets.append((self.clock(), t))
            self.held = None
        elif not v & 0xC0:
            self.held = None


class Lcd:
    """io.h `Lcdisp` at IOACK(Lcdisp, 0x3000): ctl, data; CHOICES['lcd']."""

    def __init__(self):
        self.writes = collections.Counter()

    def read(self, off):
        raise Stop("LCD: read of +0x%x (write-only in the kernel)" % off)

    def write(self, off, data, mask):
        self.writes[off] += 1


class Latch:
    """A device whose writes are accepted and recorded and whose reads
    return a stated constant (`reads`: offset -> value); any other read
    stops the run, so a register the kernel starts to depend on is found,
    not guessed."""

    def __init__(self, name, reads=None):
        self.name = name
        self.reads = dict(reads or {})
        self.writes = collections.Counter()
        self.last = {}

    def read(self, off):
        if off in self.reads:
            return self.reads[off]
        raise Stop("%s: read of +0x%x is not modelled" % (self.name, off))

    def write(self, off, data, mask):
        self.writes[off] += 1
        self.last[off] = data


class Wd33c93:
    """io.h SCSIADDR/SCSIDATA (WD33C93A) at IONAK 0x100 / 0x104.

    The interface is the one scsi.c uses (its register and bit names are
    quoted): a write to SCSIADDR selects a register, a read of it returns
    the auxiliary status (Raux: Intrpend 0x80, Cip 0x10, Bsy 0x20); data
    accesses go to the selected register and advance the selection
    (start() writes Rlun..Rdestid and scsiregs() reads 0x00..0x18 that
    way), except at Rcmd (0x18) and Rdata (0x19).  WD_CHOICES."""

    def __init__(self, irq_hook=None):
        self.regs = [0] * 0x20
        self.sel = 0
        self.intr = False
        self.commands = []

    def read(self, off):
        if off == 0:
            return 0x80 if self.intr else 0x00
        if off == 4:
            r = self.sel
            v = self.regs[r]
            if r == 0x17:                   # Rstatus: reading clears INT
                self.intr = False
            self._advance()
            return v
        raise Stop("WD33C93A: read of +0x%x" % off)

    def _advance(self):
        if self.sel not in (0x18, 0x19):
            self.sel = (self.sel + 1) & 0x1F

    def write(self, off, data, mask):
        data &= 0xFF
        if off == 0:
            self.sel = data & 0x1F
            return
        if off != 4:
            raise Stop("WD33C93A: write of +0x%x" % off)
        r = self.sel
        self.regs[r] = data
        self._advance()
        if r == 0x18:
            self.command(data)

    def command(self, cmd):
        self.commands.append(cmd)
        if cmd == 0x00:                     # Creset
            # WD_CHOICES['reset']: status 0x01 with Eaf (own ID 0x08) set,
            # 0x00 without.
            self.regs[0x17] = 0x01 if self.regs[0x00] & 0x08 else 0x00
            self.intr = True
            return
        if cmd in (0x06, 0x07, 0x08, 0x09):  # select [and transfer]
            # WD_CHOICES['no-targets']: nothing answers the selection.
            self.regs[0x17] = 0x42
            self.intr = True
            return
        raise Stop("WD33C93A: command 0x%02x is not modelled" % cmd)


WD_CHOICES = {
    "reset": "After Creset (0x00) the chip interrupts with status 0x01 "
             "when the own-ID register has Eaf (0x08, 'enable advanced "
             "features') and 0x00 otherwise -- the WD33C93A's two reset "
             "codes as the data sheet gives them; the release has no "
             "data sheet, and s9term's resetscsi only waits for the "
             "interrupt and reads the status.",
    "no-targets": "No SCSI target is attached: every selection ends with "
                  "the selection-timeout status 0x42 and an interrupt.",
    "irq": "The chip requests IRQ 10 (io.h IRQSCSI) while Intrpend is "
           "set.",
}


class Sonic:
    """io.h `Sonic` (DP83932) at 0xA4400000 (SONICADDR, mapped one-to-one
    by mmuiomap).  Registers are words at their io.h offsets (cr 0x00 ..
    dcr2 0x3F), 16 bits wide.

    The release has no DP83932 data sheet and none is in the repository.
    The behaviour is what s9term's devether.c relies on, every point an
    inference recorded in SONIC_CHOICES; where the driver leaves a detail
    open, QEMU's model of the same part (hw/net/dp8393x.c, written against
    the data sheet) is followed and cited as such.  Descriptor fields are
    32-bit words in RAM (dcr Dw32 0x0020, the driver's `ulong` fields)
    holding a 16-bit value; the SONIC writes them zero-extended.

    `wire` is the host side: `wire.transmit(frame, t)` gets each frame
    the SONIC sends (no FCS) and `wire.next_frame()` / `wire.take(t)`
    deliver inbound frames at model time t."""

    CR, DCR, RCR, TCR, IMR, ISR, UTDA, CTDA = range(8)
    URDA, CRDA = 0x0D, 0x0E
    EOBC, URRA, RSA, REA, RRP, RWP = 0x13, 0x14, 0x15, 0x16, 0x17, 0x18
    CEP, CAP2, CAP1, CAP0, CE, CDP, CDC = range(0x21, 0x28)
    SR, RSC, MPT = 0x28, 0x2B, 0x2E

    # cr
    HTX, TXP, RXDIS, RXEN, STP, ST, RST, RRRA, LCAM = (
        0x0001, 0x0002, 0x0004, 0x0008, 0x0010, 0x0020, 0x0080, 0x0100,
        0x0200)
    # isr
    RDE, TXDN, PKTRX, LCD = 0x0040, 0x0200, 0x0400, 0x1000
    # receive status / rcr
    PRX, LPKT, BC, PRO, BRD = 0x0001, 0x0040, 0x0080, 0x1000, 0x2000
    EOL = 1

    def __init__(self, board, clock):
        self.board = board
        self.clock = clock
        self.regs = collections.defaultdict(int)
        self.regs[self.CR] = self.RST | self.STP | self.RXDIS
        self.commands = []
        self.cam = {}
        self.crba = 0               # current receive buffer, byte address
        self.rbwc = 0               # its remaining 16-bit words
        self.rx_eol = False         # last descriptor's link had EOL
        self.wire = None
        self.sent = []              # (model time, frame)
        self.received = []          # (model time, frame, outcome)

    # --- memory, as the SONIC's bus master sees it ----------------------
    def _get(self, base, index):
        return self.board.read(base + 4 * index) & 0xFFFF

    def _put(self, base, index, value):
        self.board.write(base + 4 * index, value & 0xFFFF, 0xF)

    def _bytes(self, pa, n):
        return bytes(self.board.byte(pa + i) for i in range(n))

    def _write_bytes(self, pa, data):
        for i, c in enumerate(data):
            a = pa + i
            self.board.write(a & ~3, c << (8 * (a & 3)), 1 << (a & 3))

    def _addr(self, upper, lower):
        return ((self.regs[upper] << 16) | self.regs[lower]) & MASK32

    # --- registers ------------------------------------------------------
    def read(self, off):
        return self.regs[off // 4] & 0xFFFF

    def write(self, off, data, mask):
        idx = off // 4
        data &= 0xFFFF
        r = self.regs
        if idx == self.CR:
            self.commands.append(data)
            self.command(data)
            return
        if idx == self.ISR:                 # SONIC_CHOICES['isr']
            r[idx] &= ~data
            return
        if idx in (self.RSA, self.REA, self.RRP, self.RWP):
            data &= 0xFFFC
        r[idx] = data

    def irq(self):
        return bool(self.regs[self.ISR] & self.regs[self.IMR])

    def command(self, cmd):
        r = self.regs
        if r[self.CR] & self.RST and not cmd & self.RST:
            r[self.CR] &= ~self.RST         # leaving software reset
            return
        r[self.CR] |= cmd & 0x03BF
        if cmd & self.RXDIS:
            r[self.CR] &= ~self.RXEN
        if cmd & self.RXEN:
            r[self.CR] &= ~self.RXDIS
        if cmd & self.RST:
            r[self.CR] &= ~(self.LCAM | self.RRRA | self.TXP | self.HTX)
            r[self.CR] |= self.RST | self.RXDIS
            return
        if cmd & self.RRRA:
            self.read_rra()
            r[self.CR] &= ~self.RRRA
        if cmd & self.LCAM:
            self.load_cam()
            r[self.CR] &= ~self.LCAM
        if cmd & self.TXP:
            self.transmit()
            r[self.CR] &= ~self.TXP
        if cmd & ~(self.HTX | self.TXP | self.RXDIS | self.RXEN | self.STP
                   | self.ST | self.RST | self.RRRA | self.LCAM):
            raise Stop("SONIC: command 0x%04x is not modelled" % cmd)

    def read_rra(self):
        """SONIC_CHOICES['rra']: the next receive resource into crba/rbwc."""
        r = self.regs
        rrp = self._addr(self.URRA, self.RRP)
        self.crba = (self._get(rrp, 1) << 16) | self._get(rrp, 0)
        self.rbwc = (self._get(rrp, 3) << 16) | self._get(rrp, 2)
        r[self.RRP] = (r[self.RRP] + 16) & 0xFFFF
        if r[self.RRP] == r[self.REA]:
            r[self.RRP] = r[self.RSA]
        if r[self.RRP] == r[self.RWP]:
            raise Stop("SONIC: the receive resources ran out (rrp = rwp), "
                       "which s9term's ring never lets happen")

    def load_cam(self):
        """SONIC_CHOICES['cam']: cdc entries of (cep, cap0..2) from cdp
        (upper half: urra), then the CAM enable word."""
        r = self.regs
        cdp = self._addr(self.URRA, self.CDP)
        n = r[self.CDC] & 0x1F
        while n:
            ent = self._get(cdp, 0) & 0xF
            ea = b"".join(bytes([w & 0xFF, w >> 8])
                          for w in (self._get(cdp, i) for i in (1, 2, 3)))
            self.cam[ent] = ea
            n -= 1
            cdp += 16
        r[self.CDC] = 0
        r[self.CDP] = cdp & 0xFFFF
        r[self.CE] = self._get(cdp, 0)
        r[self.ISR] |= self.LCD

    def transmit(self):
        """SONIC_CHOICES['transmit']."""
        r = self.regs
        now = self.clock()
        while True:
            tda = (r[self.UTDA] << 16) | (r[self.CTDA] & 0xFFFE)
            size = self._get(tda, 2)
            nfrag = self._get(tda, 3)
            frame = b""
            for i in range(nfrag):
                ptr = ((self._get(tda, 5 + 3 * i) << 16)
                       | self._get(tda, 4 + 3 * i))
                frame += self._bytes(ptr, self._get(tda, 6 + 3 * i))
            if len(frame) != size:
                raise Stop("SONIC: descriptor 0x%08x: %d fragment bytes, "
                           "packet size %d" % (tda, len(frame), size))
            self.sent.append((now, frame))
            if self.wire is None:
                raise Stop("SONIC: a frame was transmitted and no network "
                           "is attached (--ether)")
            self.wire.transmit(frame, now)
            self._put(tda, 0, 0x0001)       # status: PTX
            link = self._get(tda, 4 + 3 * nfrag)
            r[self.CTDA] = link
            if link & self.EOL:
                break
        r[self.ISR] |= self.TXDN

    # --- receive --------------------------------------------------------
    def accepts(self, frame):
        """SONIC_CHOICES['filter']."""
        r = self.regs
        dst = frame[:6]
        if r[self.RCR] & self.PRO and not dst[0] & 1:
            return 0
        if r[self.RCR] & self.BRD and dst == b"\xff" * 6:
            return self.BC
        for ent, ea in self.cam.items():
            if r[self.CE] & (1 << ent) and ea == dst:
                return 0
        return None

    def receive(self, frame):
        """SONIC_CHOICES['receive']: one inbound frame (no FCS)."""
        r = self.regs
        now = self.clock()
        if not r[self.CR] & self.RXEN:
            self.received.append((now, frame, "receiver off"))
            return
        kind = self.accepts(frame)
        if kind is None:
            self.received.append((now, frame, "not for this station"))
            return
        data = frame + struct.pack("<I", zlib.crc32(frame) & MASK32)
        padded = ((len(data) - 1) | 3) + 1
        if padded > self.rbwc * 2:
            raise Stop("SONIC: frame of %d bytes does not fit the receive "
                       "buffer (%d words left)" % (len(frame), self.rbwc))
        if self.rx_eol:
            link = self._get(self._addr(self.URDA, self.CRDA), 5)
            if link & self.EOL:
                r[self.MPT] = (r[self.MPT] + 1) & 0xFFFF
                self.received.append((now, frame, "no descriptor (EOL)"))
                return
            self._put(self._addr(self.URDA, self.CRDA), 6, 0)
            r[self.CRDA] = link
            self.rx_eol = False
            r[self.ISR] |= self.PKTRX
        rda = self._addr(self.URDA, self.CRDA) & ~1
        start = self.crba
        self._write_bytes(start, data + b"\xff" * (padded - len(data)))
        self.crba += padded
        self.rbwc -= padded // 2
        status = self.PRX | kind
        if self.rbwc < r[self.EOBC]:
            status |= self.LPKT
        self._put(rda, 0, status)
        self._put(rda, 1, len(data))
        self._put(rda, 2, start & 0xFFFF)
        self._put(rda, 3, start >> 16)
        self._put(rda, 4, r[self.RSC])
        link = self._get(rda, 5)
        if link & self.EOL:
            self.rx_eol = True
            r[self.ISR] |= self.RDE
        else:
            self._put(rda, 6, 0)            # in_use: to the host
            r[self.CRDA] = link
            r[self.ISR] |= self.PKTRX
        r[self.RSC] = (r[self.RSC] & 0xFF00) | ((r[self.RSC] + 1) & 0xFF)
        if status & self.LPKT:
            self.read_rra()
            r[self.RSC] = ((r[self.RSC] + 0x100) & 0xFF00)
        self.received.append((now, frame, "received"))

    def next_event(self):
        return self.wire.next_time() if self.wire is not None else None

    def poll(self):
        """Deliver every inbound frame whose time has come."""
        if self.wire is None:
            return
        now = self.clock()
        while True:
            frame = self.wire.take(now)
            if frame is None:
                return
            self.receive(frame)


SONIC_CHOICES = {
    "registers": "Registers are io.h's words, 16 bits wide; reset state "
                 "cr = Rst|Stp|Rxdis (QEMU dp8393x_reset).  Writing cr "
                 "with Rst clear while in reset only leaves reset "
                 "(QEMU dp8393x_do_command), which is what devether.c's "
                 "`cr = Rst; dcr = ...; cr = 0` relies on.",
    "isr": "isr is write-one-to-clear (devether.c's interrupt routine "
           "writes back the bits it read: `sonic->isr = isr`); IRQ 9 "
           "(io.h IRQSONIC) while isr & imr is not 0.",
    "rra": "Rrra and every exhausted buffer read the 4-word resource at "
           "urra:rrp (buffer pointer, word count), advance rrp by 16 "
           "bytes (32-bit descriptors) and wrap it from rea to rsa; the "
           "command completes at once (cr reads it clear).  rrp reaching "
           "rwp stops the run (devether.c puts rwp past rea so it never "
           "does).",
    "cam": "Lcam reads cdc entries of (cep, cap0, cap1, cap2) from "
           "urra:cdp, each cap the next two address bytes low byte first "
           "(devether.c: cap0 = ea[1]<<8 | ea[0]), then the CAM-enable "
           "word; done at once, isr Lcd set (the driver ignores it).  "
           "The upper half of cdp is urra, as in QEMU's dp8393x_cdp.",
    "transmit": "Txp transmits from utda:ctda: packet size (word 2), "
                "fragment count (3), per fragment ptr0, ptr1, size, then "
                "the link; each frame goes to the wire at once (no "
                "deferral, collisions or line time), the status word "
                "becomes 0x0001 (PTX: neither Host 0 nor Interface ~0, "
                "Ptx set, as devether.c tests), ctda becomes the link, and "
                "the next descriptor follows unless the link has EOL; then "
                "isr Txdn.  ctda keeping the link with EOL means a later "
                "Txp starts at the descriptor after the last one sent, "
                "which is what etheroput's bare `cr = Txp` needs (QEMU "
                "dp8393x_do_transmit_packets does the same).  The frame "
                "carries no FCS (tcr CRCI clear: the SONIC appends it).",
    "receive": "An inbound frame (rcr's filter below, receiver enabled) "
               "goes into the current buffer with its CRC-32 FCS "
               "appended, padded to 4 bytes; the descriptor at urda:crda "
               "gets status Prx (| Bc for broadcast, | Lpkt when the "
               "buffer has fewer than eobc words left), byte count "
               "(frame + 4, which etherkproc subtracts), the buffer "
               "address, the sequence number; then, unless its link has "
               "EOL, in_use = 0 (Host), crda = link and isr Pktrx.  With "
               "EOL the descriptor is kept (isr Rde) and its link re-read "
               "at the next frame; still EOL, the frame is dropped and "
               "counted in mpt (QEMU dp8393x_receive).  Lpkt reads the "
               "next resource, so with eobc = buffer words - 2 each frame "
               "has its own buffer and the buffers advance with the "
               "descriptors, as etherkproc's rb[rh] needs.",
    "filter": "Accepted: any unicast with rcr Pro, broadcast with Brd, "
              "and a destination equal to an enabled CAM entry; frames "
              "the SONIC itself sent are not looped back (a real "
              "transceiver does not hear its own frames as input).",
    "dma": "Descriptor and buffer addresses are physical (mem.h PADDR is "
           "the identity), read and written through the board's RAM; "
           "packet bytes are stored in address order in the board's "
           "little-endian byte lanes (the kernel runs with CONFIG.KL), "
           "which the first frame checks: it decodes as ff:ff:ff:ff:ff:ff, "
           "the EEPROM's address, type 0x0800.",
}


RTC_BASE = 726062400     # 1993-01-03 12:00:00 UTC (CHOICES['rtc'])

EEPROM_EA = bytes([0x52, 0x54, 0x00, 0x00, 0x0B, 0x0B])


def eeprom_image(ea=EEPROM_EA):
    """IIC_CHOICES['eeprom']: io.h's Eeprom (16 bytes), then 0x00."""
    head = bytes([0xA6, 0x00, 0xD9, 0x20, 0x10])    # EEPROMMAGIC "A600D92010"
    rest = bytes([0x00,          # mask
                  CPU_HZ // 1000000,   # clock, MHz: delay()'s loop count
                  0x00, 0x00, 0x00])   # dsp, pcb, rev
    return (head + ea + rest).ljust(256, b"\0")


class Iic:
    """io.h `Iic` (PCF8584 IIC-bus controller) at IOACK(Iic, 0x0080):
    data (S0), ctl (S1).  On the bus: the PCF8582 EEPROM at 0xA4 and the
    PCF8574 LED latch at 0x40 (deviic.c).  IIC_CHOICES."""

    PIN, ESO, ES1, ES2, STA, STO, ACK = (0x80, 0x40, 0x20, 0x10, 0x04,
                                         0x02, 0x01)
    BB, LRB = 0x01, 0x08            # status: bus free (not busy), no ack

    def __init__(self, eeprom=None):
        self.mem = bytearray(eeprom if eeprom is not None else eeprom_image())
        self.own = None
        self.clockreg = None
        self.ctl = 0
        self.s0 = 0
        self.pin = True
        self.lrb = False
        self.busy = False
        self.slave = None           # address byte of the current transfer
        self.ptr = 0
        self.ptr_set = False
        self.led = []
        self.writes = collections.Counter()
        self.log = []

    def status(self):
        v = 0x80 if self.pin else 0
        if self.lrb:
            v |= self.LRB
        if not self.busy:
            v |= self.BB
        return v

    def read(self, off):
        if off == 4:
            return self.status()
        if off != 0:
            raise Stop("IIC: read of +0x%x" % off)
        if not self.ctl & self.ESO:
            raise Stop("IIC: S0 read with the serial interface off")
        v = self.s0
        if self.busy and self.slave is not None and self.slave & 1:
            # Master receiver: a read of S0 starts the next byte, acked if
            # the last control word had ACK (IIC_CHOICES['receive']).
            if self.ctl & self.ACK:
                self._receive()
        return v

    def _receive(self):
        self.s0 = self.mem[self.ptr & 0xFF]
        self.ptr += 1
        self.pin = False
        self.lrb = False

    def write(self, off, data, mask):
        data &= 0xFF
        self.writes[off] += 1
        self.log.append((off, data))
        if off == 0:
            if not self.ctl & self.ESO:
                sel = self.ctl & (self.ES1 | self.ES2)
                if sel == 0:
                    self.own = data
                elif sel == self.ES1:
                    self.clockreg = data
                else:
                    raise Stop("IIC: write to register select 0x%02x"
                               % sel)
                return
            self.s0 = data
            if self.busy and self.slave is not None and not self.slave & 1:
                self._transmitted(data)
            return
        if off != 4:
            raise Stop("IIC: write of +0x%x" % off)
        self.ctl = data
        if not data & self.ESO:
            return
        if data & self.STA and not data & self.STO:
            self._start()
        elif data & self.STO and not data & self.STA:
            self.busy = False
            self.slave = None
            self.pin = True
        elif data & self.PIN and self.busy and self.slave is not None \
                and self.slave & 1:
            # ACK taken away in mid-read (eepromread's 0xC0): the byte
            # being received completes, not acknowledged.
            self.pin = False
        elif data & self.PIN:
            self.pin = True

    def _start(self):
        """(Repeated) START with the address byte in S0."""
        addr = self.s0
        self.busy = True
        self.slave = addr
        self.pin = False
        dev = addr & 0xFE
        self.lrb = dev not in (0xA4, 0x40)
        if dev == 0xA4 and not addr & 1:
            self.ptr_set = False

    def _transmitted(self, data):
        dev = self.slave & 0xFE
        self.pin = False
        if dev == 0xA4:
            if not self.ptr_set:
                self.ptr = data
                self.ptr_set = True
            else:
                # IIC_CHOICES['repeated-start']: held in S0 as the address
                # of the START that follows; not written to the EEPROM.
                self.pin = True
                return
        elif dev == 0x40:
            self.led.append(data)
        self.lrb = dev not in (0xA4, 0x40)


IIC_CHOICES = {
    "bus": "The PCF8584 (deviic.c) answers as the part does for the "
           "driver's sequences: S1 reads PIN (0x80, clear once a byte has "
           "gone or come), LRB (0x08, 'Nak': set when no slave "
           "acknowledged) and BB (0x01, 'Busfree': set while no START is "
           "outstanding); S0' (own address) and S2 (clock) are written "
           "through the ES1 select before ESO.  Every transfer completes "
           "at once.  Devices on the bus: the PCF8582 EEPROM (0xA4) and "
           "the PCF8574 LED latch (0x40); any other address is not "
           "acknowledged.  No data sheet is in the release; the sequences "
           "are inferred from deviic.c's code and comments.",
    "repeated-start": "eepromread writes the read address (0xA5) to S0 "
                      "after the word address, reads S1, waits, then "
                      "sets STA: the byte is taken as the repeated "
                      "START's address and not as a data byte to the "
                      "EEPROM (which would write it at location 0); the "
                      "driver's own comment ('we have to flush the data "
                      "we wrote above') is unsure what the part does.",
    "receive": "Master receiver: the first read of S0 after the address "
               "returns the address byte (deviic.c: 'We get some junk "
               "back') and every read of S0 with ACK set starts the next "
               "byte; a control write of PIN|ESO (ACK off) completes the "
               "byte in progress, which the driver reads as one more.  So "
               "eepromread reads 17 bytes, the 16 of io.h's Eeprom and "
               "one stored past it (into rtclock), EEPROM byte 16 = 0.",
    "eeprom": "The EEPROM holds io.h's Eeprom: magic a6 00 d9 20 10 "
              "(EEPROMMAGIC \"A600D92010\" read as hex digits; nothing in "
              "the kernel checks it), ea 52:54:00:00:0b:0b (locally "
              "administered, the address tools/qemu1e/ndb.local gives "
              "the Hobbit, so the 1e server's ip/bootp answers it), mask 0, clock 20 "
              "(MHz: delay() loops ms*1000*clock/2 times, and CHOICES "
              "clock is 20 MHz), dsp, pcb, rev 0; the rest of its 256 "
              "bytes 0.  The values of a 1993 board are not in the "
              "release.",
}


class Pcap:
    """A libpcap file (LINKTYPE_ETHERNET, nanosecond stamps: one model
    cycle is 50 ns), one record per frame, stamped with model time;
    frames without FCS."""

    def __init__(self, path):
        self.f = open(path, "wb")
        self.f.write(struct.pack("<IHHiIII", 0xA1B23C4D, 2, 4, 0, 0,
                                 65535, 1))
        self.f.flush()

    def write(self, t, frame):
        ns = int(round(t * 1e9))
        sec, nsec = divmod(ns, 1000000000)
        self.f.write(struct.pack("<IIII", sec, nsec, len(frame), len(frame)))
        self.f.write(frame)
        self.f.flush()


def read_pcap(path):
    """[(t, frame)] from a little-endian pcap (ns or µs stamps)."""
    with open(path, "rb") as f:
        data = f.read()
    magic, = struct.unpack_from("<I", data)
    scale = {0xA1B23C4D: 1e9, 0xA1B2C3D4: 1e6}.get(magic)
    if scale is None:
        raise SystemExit("%s: not a little-endian pcap" % path)
    out, off = [], 24
    while off + 16 <= len(data):
        sec, frac, incl, _ = struct.unpack_from("<IIII", data, off)
        off += 16
        out.append((sec + frac / scale, data[off:off + incl]))
        off += incl
    return out


def ip_checksum(data):
    if len(data) & 1:
        data += b"\0"
    s = sum(struct.unpack("!%dH" % (len(data) // 2), data))
    while s >> 16:
        s = (s & 0xFFFF) + (s >> 16)
    return ~s & 0xFFFF


def ipv4(text):
    return bytes(int(x) for x in text.split("."))


def decode_frame(frame):
    """A one-line description of an ethernet frame (ARP, IP/UDP/BOOTP,
    IL), for the run's report."""
    def mac(b):
        return ":".join("%02x" % c for c in b)

    def ip(b):
        return ".".join(str(c) for c in b)
    if len(frame) < 14:
        return "runt %d bytes" % len(frame)
    dst, src, etype = frame[:6], frame[6:12], (frame[12] << 8) | frame[13]
    head = "%s > %s" % (mac(src), mac(dst))
    body = frame[14:]
    if etype == 0x0806 and len(body) >= 28:
        op = (body[6] << 8) | body[7]
        return "%s ARP %s who-has %s tell %s (%s)" % (
            head, {1: "request", 2: "reply"}.get(op, op), ip(body[24:28]),
            ip(body[14:18]), mac(body[8:14]))
    if etype != 0x0800 or len(body) < 20:
        return "%s type 0x%04x, %d bytes" % (head, etype, len(frame))
    ihl = (body[0] & 0xF) * 4
    proto = body[9]
    s = "%s IP %s > %s" % (head, ip(body[12:16]), ip(body[16:20]))
    if ip_checksum(body[:ihl]) != 0:
        s += " (BAD IP CHECKSUM)"
    seg = body[ihl:(body[2] << 8) | body[3]]
    if proto == 17 and len(seg) >= 8:
        sport, dport, ulen, usum = struct.unpack("!HHHH", seg[:8])
        s += " UDP %d > %d len %d" % (sport, dport, ulen)
        pkt = seg[8:]
        if 67 in (sport, dport) and len(pkt) >= 236:
            op, htype, hlen = pkt[0], pkt[1], pkt[2]
            s += " BOOTP %s htype %d hlen %d xid %s ciaddr %s yiaddr %s " \
                 "siaddr %s chaddr %s file %r vend %r" % (
                     {1: "request", 2: "reply"}.get(op, op), htype, hlen,
                     pkt[4:8].hex(), ip(pkt[12:16]), ip(pkt[16:20]),
                     ip(pkt[20:24]), mac(pkt[28:34]),
                     pkt[108:236].split(b"\0")[0].decode("latin-1"),
                     pkt[236:].rstrip(b"\0")[:64])
        return s
    if proto == 40:
        return s + " IL %d bytes" % len(seg)
    return s + " proto %d" % proto


class Replay:
    """Answers recorded from a live session (ETHER_CHOICES['replay']): a
    pcap of the wire, as --pcap writes it, read as alternating runs of
    the model's frames and the network's.  When the model transmits the
    frame recorded next, the network frames recorded after it (up to the
    next model frame) are scheduled at their recorded offsets from it.
    A transmitted frame that differs from the recording is reported and
    stops the replay."""

    def __init__(self, path, ea):
        # [(tx frame, [(offset in cycles, rx frame)])]; nanosecond pcap
        # stamps are whole cycles (50 ns), so the offsets are exact
        self.steps = []
        tx_c = None
        for t, frame in read_pcap(path):
            c = int(round(t * CPU_HZ))
            if frame[6:12] == ea:
                self.steps.append((frame, []))
                tx_c = c
            elif self.steps:
                self.steps[-1][1].append((c - tx_c, frame))
        self.pos = 0
        self.mismatch = None

    def answer(self, frame):
        if self.mismatch is not None or self.pos >= len(self.steps):
            return []
        want, replies = self.steps[self.pos]
        if frame != want:
            self.mismatch = (self.pos, frame, want)
            return []
        self.pos += 1
        return replies


class Wire:
    """The host side of the SONIC's cable (ETHER_CHOICES).

    Every frame either way is written to `pcap`.  Inbound frames come
    from a recorded session (`replay`), from a schedule (`script`), or
    from a UDP peer (one raw
    ethernet frame per datagram, QEMU's `-netdev dgram` / `-netdev
    socket,udp=` framing): a datagram is given the model time at which
    the harness reads it."""

    def __init__(self, clock, pcap=None, replay=None, peer=None,
                 local=None, script=None):
        self.clock = clock
        self.pcap = Pcap(pcap) if pcap else None
        self.replay = replay
        self.inbound = []           # sorted [(due cycle, n, frame)]
        self.n = 0
        self.log = []               # (t, "tx"/"rx", frame)
        self.sock = None
        self.peer = None
        if peer:
            host, port = peer.rsplit(":", 1)
            self.peer = (host, int(port))
            lhost, lport = (local or "127.0.0.1:0").rsplit(":", 1)
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((lhost, int(lport)))
            self.sock.setblocking(False)
        for t, frame in script or ():
            self.schedule(frame, t)

    def schedule(self, frame, t):
        """Deliver `frame` at the first cycle at or after model time t."""
        self.schedule_cycle(frame, int(math.ceil(t * CPU_HZ - 1e-6)))

    def schedule_cycle(self, frame, due):
        self.inbound.append((due, self.n, frame))
        self.n += 1
        self.inbound.sort()

    def transmit(self, frame, t):
        self.log.append((t, "tx", frame))
        if self.pcap:
            self.pcap.write(t, frame)
        if self.sock is not None:
            self.sock.sendto(frame, self.peer)
        if self.replay is not None:
            c = int(round(t * CPU_HZ))
            for offset, reply in self.replay.answer(frame):
                self.schedule_cycle(reply, c + offset)

    def next_time(self):
        return self.inbound[0][0] / float(CPU_HZ) if self.inbound else None

    def take(self, now):
        if self.inbound and self.inbound[0][0] <= int(round(now * CPU_HZ)):
            t, _, frame = self.inbound.pop(0)
            self.log.append((now, "rx", frame))
            if self.pcap:
                self.pcap.write(now, frame)
            return frame
        return None

    def poll_peer(self, timeout, base):
        """Datagrams from the peer; with a timeout, wait up to that many
        wall-clock seconds for the first.  Each is stamped base + the
        wall-clock seconds waited (ETHER_CHOICES['peer'])."""
        if self.sock is None:
            return 0
        got = 0
        t0 = time.time()
        if timeout > 0:
            self.sock.settimeout(timeout)
        try:
            while True:
                try:
                    data, _ = self.sock.recvfrom(65536)
                except (BlockingIOError, socket.timeout):
                    break
                self.schedule(data, base + (time.time() - t0))
                got += 1
                self.sock.setblocking(False)
        finally:
            self.sock.setblocking(False)
        return got


ETHER_CHOICES = {
    "wire": "The SONIC's cable is the harness's Wire: frames the SONIC "
            "transmits are written to --pcap and sent to --ether-peer; "
            "inbound frames come from --ether-replay, from "
            "--ether-script (a pcap whose frames are delivered at their "
            "timestamps), or from the peer.  A frame is in the SONIC at "
            "the model time it is delivered (no line time).",
    "peer": "--ether-peer HOST:PORT [--ether-local HOST:PORT]: one raw "
            "ethernet frame per UDP datagram, no FCS, no header -- the "
            "framing of QEMU's `-netdev dgram,...remote.type=inet` and "
            "`-netdev socket,udp=HOST:PORT,localaddr=HOST:PORT`.  The "
            "socket is polled every PEER_POLL instructions and, when the "
            "kernel is idle with nothing due, waited on in wall-clock time "
            "for as long as the model time to the next event (so idle "
            "model time runs at the wall clock's rate while a peer is "
            "attached; busy time runs at the reference model's speed, "
            "~100,000 instructions a second, ~200 times slower than a "
            "20 MHz part).  A datagram gets the model time it is read at.",
    "replay": "--ether-replay PCAP answers the model's frames with a "
              "recorded live session's (--pcap of a run joined to the 1e "
              "server in QEMU): when the model transmits the next "
              "recorded frame, byte for byte, the server's frames that "
              "followed it are delivered at the same model-time offsets "
              "they had in the recording.  So a test can run the network "
              "path without QEMU, with the real server's answers.",
}

PEER_POLL = 20000
PEER_IDLE_MAX = 1.0


class Boot:
    def __init__(self, image, memsize=MEMSIZE, out=None, ea=EEPROM_EA):
        self.board = Board(memsize)
        self.cycles = 0
        self.ioctl = Register("IOCTL")
        self.irq = Irq()
        self.quart = Quart(25, lambda: self.cycles / float(CPU_HZ))
        self.lcd = Lcd()
        self.rtc = Timekeeper(lambda: self.cycles / float(CPU_HZ),
                              RTC_BASE)
        self.board.add(IONAK + 0x2000, IONAK + 0x4000, self.rtc)
        self.iic = Iic(eeprom_image(ea))
        self.board.add(IOBASE + 0x0080, IOBASE + 0x0088, self.iic)
        # devincon.c Device at IOACK(Device, 0x0000): ctl, csr, pad, data.
        self.incon = Latch("incon")
        self.scsi = Wd33c93()
        self.irq.sources[10] = lambda: self.scsi.intr
        self.board.add(IONAK + 0x0100, IONAK + 0x0108, self.scsi)
        self.sonic = Sonic(self.board, lambda: self.cycles / float(CPU_HZ))
        self.irq.sources[9] = self.sonic.irq
        self.wire = None
        self.until_frames = 0       # stop once this many frames were seen
        self.board.add(0xA4400000, 0xA4400100, self.sonic)
        self.board.add(IOBASE + 0x0000, IOBASE + 0x0014, self.incon)
        self.irq.sources[1] = self.quart.irq
        self.board.add(IONAK + 0x0000, IONAK + 0x0004, self.ioctl)
        self.board.add(IONAK + 0x0080, IONAK + 0x0090, self.irq)
        self.board.add(IOBASE + 0x0100, IOBASE + 0x0200, self.quart)
        self.board.add(IOBASE + 0x3000, IOBASE + 0x3008, self.lcd)
        self.k = load_kernel(image, self.board)
        rom_handoff(self.board, memsize)
        self.syms = Symbols(p9exec.kernel_symbols(self.k))
        self.out = out
        self.sysm = hobbit_sem.System(bus=self.board)
        self.sysm.cret_clamp = True     # CHOICES['cret-msp']
        self.state = hobbit_sem.State(pc=self.k["entry"], sp=0, msp=0,
                                      psw=0, isp=0, vb=0, config_kl=False,
                                      cache=[0] * 64, system=self.sysm)
        self.steps = 0
        self.progress = 0
        self.interrupts = 0
        self.exceptions = []
        self.until = None           # bytes: stop once screenputs shows them
        self.nevents = 0
        self.etext = self.k["textbase"] + self.k["text"]
        self.reached = []           # (step, function) first reaches
        self.seen = set()
        self.console = collections.defaultdict(bytearray)
        self.taps = {}
        sp = self.syms.by_name.get("screenputs")
        if sp is not None:
            self.taps[sp] = self.tap_screenputs
        # CHOICES['idle-skip']
        self.idle_skip = True
        self.idle_head, self.idle_words = find_idle_loop(self)
        self.idle_last = None       # (steps, cycles, cycles of last lap)
        self.skipped_steps = 0
        self.skipped_cycles = 0
        self.skips = 0
        # CHOICES['console-input']: (text to wait for, bytes to type)
        self.script = []
        self.script_from = 0
        self.think = 0.0            # seconds from TEXT to the first byte
        self.typed = []

    def next_event(self):
        """The earliest model time (seconds) after now at which a device
        changes state by itself, or None."""
        times = [t for t in (self.quart.next_event(),
                             self.sonic.next_event()) if t is not None]
        return min(times) if times else None

    def attach(self, wire):
        self.wire = wire
        self.sonic.wire = wire

    def try_idle_skip(self, max_steps):
        """CHOICES['idle-skip']: called with the PC at the idle loop's
        head, after the interrupt check."""
        st = self.state
        sysm = self.sysm
        last = self.idle_last
        lap = None
        if last is not None and self.steps - last[0] == IDLE_LAP_STEPS:
            lap = self.cycles - last[1]
        self.idle_last = (self.steps, self.cycles, lap)
        if lap is None or last[2] != lap or lap <= 0:
            return
        if (st.psw & hobbit_sem.PSW_USER
                or (st.psw >> hobbit_sem.PSW_IPL_SHIFT) & 7 != 7):
            return
        if any(self.board.read(a) for a in self.idle_words):
            return
        if (sysm.config & (hobbit_sem.CONFIG_T1IE | hobbit_sem.CONFIG_T2IE)
                or sysm.timer1_pending or sysm.timer2_pending):
            return
        if self.irq.asserted():
            return
        nxt = self.next_event()
        w = self.wire
        if w is not None and w.sock is not None:
            # ETHER_CHOICES['peer']: idle time runs at the wall clock.
            now = self.cycles / float(CPU_HZ)
            wait = PEER_IDLE_MAX if nxt is None else nxt - now
            if wait > 0:
                w.poll_peer(min(wait, PEER_IDLE_MAX), now)
                nxt = self.next_event()
            if nxt is None:
                return
        if nxt is None:
            raise Stop("idle in runproc with nothing runnable and no timed "
                       "device event pending: the loop would never end")
        hz = float(CPU_HZ)
        n = int((nxt * hz - self.cycles) / lap)
        while n > 0 and (self.cycles + n * lap) / hz >= nxt:
            n -= 1
        n = min(n, (max_steps - self.steps) // IDLE_LAP_STEPS)
        if n <= 0:
            return
        self.steps += IDLE_LAP_STEPS * n
        self.cycles += lap * n
        self.skipped_steps += IDLE_LAP_STEPS * n
        self.skipped_cycles += lap * n
        self.skips += 1
        hobbit_sem._count_timers(st, lap * n, IDLE_LAP_STEPS * n)
        self.idle_last = (self.steps, self.cycles, lap)

    def arg(self, n):
        """Argument n (0-based) at a function's entry: the CALL left the
        return PC at *(CSP) and the arguments follow (R4, R8, ...)."""
        st = self.state
        return hobbit_sem._read_word(st, None, (st.csp + 4 + 4 * n) & MASK32)

    def vbyte(self, va):
        st = self.state
        w = hobbit_sem._read_word(st, None, va & ~3)
        return (w >> (8 * (va & 3))) & 0xFF

    def log_event(self, kind, ident, pc, reason):
        self.nevents += 1
        if self.nevents <= 100:
            where = (self.syms.where(pc) if pc >= RAMBASE
                     else "user 0x%08x" % pc)
            print("p9boot: step %d: %s 0x%x at %s %s" % (
                self.steps, kind, ident, where, reason), file=sys.stderr)

    def tap_screenputs(self):
        s, n = self.arg(0), self.arg(1)
        data = bytes(self.vbyte(s + i) for i in range(max(0, min(n, 4096))))
        self.console["screenputs"] += data
        screen = self.console["screenputs"]
        while self.script:
            wait, reply = self.script[0]
            at = screen.find(wait, self.script_from)
            if at < 0:
                break
            # CHOICES['console-input']
            self.script.pop(0)
            self.script_from = at + len(wait)
            self.typed.append((self.steps, wait, reply))
            self.quart.feed(CONSOLE_CHANNEL, reply, self.think)
        if self.until is not None and self.until in screen:
            raise Stop("screenputs printed %r" % self.until)

    def run(self, max_steps):
        st = self.state
        sysm = self.sysm
        syms = self.syms
        status = "max-steps"
        cur_lo, cur_hi = 0, 0
        next_progress = self.progress or 0
        try:
            while self.steps < max_steps:
                pc = st.pc
                if not (cur_lo <= pc < cur_hi):
                    if st.psw & hobbit_sem.PSW_USER:
                        # A user process: kernel symbols do not apply.
                        cur_lo, cur_hi = 0, RAMBASE
                        name = "user mode"
                    else:
                        if pc < self.k["textbase"] or pc >= self.etext:
                            raise Stop("kernel PC 0x%08x left the kernel "
                                       "text (the boot ROM: softreset or "
                                       "a ROM vector)" % pc)
                        i = bisect.bisect_right(syms.addrs, pc) - 1
                        cur_lo = syms.addrs[i]
                        cur_hi = (syms.addrs[i + 1]
                                  if i + 1 < len(syms.addrs) else MASK32)
                        name = syms.names[i]
                    if name not in self.seen:
                        self.seen.add(name)
                        self.reached.append((self.steps, name))
                tap = self.taps.get(pc)
                if tap is not None:
                    tap()
                rec, st = hobbit_sem.step(st)
                self.steps += 1
                self.cycles += rec.cyc
                if (st.psw >> 12) & 7 == 7 and self.irq.asserted():
                    # IL 6 (CHOICES['irq-level']) is below IPL 7 only.
                    hobbit_sem.take_interrupt(st, 6)
                    self.interrupts += 1
                    del sysm.events[:]
                elif st.pc == self.idle_head and self.idle_skip:
                    self.try_idle_skip(max_steps)
                w = self.wire
                if w is not None:
                    if w.inbound and w.inbound[0][0] <= self.cycles:
                        self.sonic.poll()
                    if self.until_frames and len(w.log) >= self.until_frames:
                        raise Stop("%d frames on the wire" % len(w.log))
                    if w.sock is not None and self.steps % PEER_POLL == 0:
                        w.poll_peer(0.0, self.cycles / float(CPU_HZ))
                if self.progress and self.steps >= next_progress:
                    next_progress = (self.steps // self.progress + 1) \
                        * self.progress
                    print("p9boot: %d steps, at %s, model time %.3f s" % (
                        self.steps, syms.where(st.pc),
                        self.cycles / float(CPU_HZ)), file=sys.stderr)
                if sysm.events:
                    for kind, ident, epc in sysm.events:
                        self.log_event(kind, ident, epc,
                                       rec.reason if rec.trap else "")
                    del sysm.events[:]
                if rec.trap:
                    self.exceptions.append((self.steps, rec.pc, rec.reason))
                    last = self.exceptions[-10:]
                    if (len(last) == 10 and len({e[1] for e in last}) == 1
                            and last[0][0] > self.steps - 1000):
                        raise Stop("the same event 10 times in a row at "
                                   "%s: %s" % (syms.where(rec.pc),
                                               rec.reason))
        except hobbit_sem.Refusal as exc:
            status = "REFUSED at %s (pc %08x, parcels %s): %s" % (
                syms.where(st.pc), st.pc,
                " ".join("%04x" % p for p in exc.parcels), exc.reason)
        except Stop as exc:
            status = "STOP at %s (pc %08x): %s" % (syms.where(st.pc), st.pc,
                                                  exc)
        return status


def unescape(text):
    return text.encode("latin-1").decode("unicode_escape").encode("latin-1")


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("image")
    ap.add_argument("--max-steps", type=int, default=1000000)
    ap.add_argument("--memsize", type=int, default=MEMSIZE)
    ap.add_argument("--out", help="directory for console files")
    ap.add_argument("--counter-period", type=float, metavar="SECONDS",
                    help="override the Quart counter's CtrRDY period "
                         "(QUART_CHOICES['counter-period'])")
    ap.add_argument("--until", metavar="TEXT",
                    help="stop once screenputs has printed TEXT")
    ap.add_argument("--type", action="append", default=[],
                    metavar="TEXT=REPLY",
                    help="once the screen shows TEXT, type REPLY on the "
                         "console line (Quart channel 0); backslash escapes "
                         "as in Python, e.g. 'il]: =\\r'; repeatable, in "
                         "order (CHOICES['console-input'])")
    ap.add_argument("--think", type=float, default=0.0, metavar="SECONDS",
                    help="model time between the screen showing TEXT and "
                         "the first byte of REPLY (default 0)")
    ap.add_argument("--ea", metavar="XX:XX:XX:XX:XX:XX",
                    help="the EEPROM's ethernet address (IIC_CHOICES "
                         "['eeprom'], default 52:54:00:00:0b:0b)")
    ap.add_argument("--pcap", metavar="FILE",
                    help="write every frame, both ways, to FILE")
    ap.add_argument("--ether-replay", metavar="PCAP",
                    help="answer with a recorded session's frames "
                         "(ETHER_CHOICES['replay'])")
    ap.add_argument("--ether-script", metavar="PCAP",
                    help="inbound frames, delivered at their timestamps")
    ap.add_argument("--ether-peer", metavar="HOST:PORT",
                    help="exchange frames with a UDP peer, one frame per "
                         "datagram (QEMU -netdev dgram/socket,udp=)")
    ap.add_argument("--ether-local", metavar="HOST:PORT",
                    help="the local UDP address for --ether-peer")
    ap.add_argument("--until-frames", type=int, default=0, metavar="N",
                    help="stop once N frames have crossed the wire")
    ap.add_argument("--no-idle-skip", action="store_true",
                    help="execute every iteration of the idle loop "
                         "(CHOICES['idle-skip'])")
    ap.add_argument("--progress", type=int, default=0, metavar="N",
                    help="report the current function every N steps")
    args = ap.parse_args(argv)
    ea = EEPROM_EA
    if args.ea:
        ea = bytes(int(x, 16) for x in args.ea.split(":"))
    boot = Boot(args.image, args.memsize, args.out, ea=ea)
    if (args.pcap or args.ether_replay or args.ether_script
            or args.ether_peer):
        replay = Replay(args.ether_replay, ea) if args.ether_replay else None
        script = read_pcap(args.ether_script) if args.ether_script else ()
        boot.attach(Wire(boot.sonic.clock, pcap=args.pcap, replay=replay,
                         peer=args.ether_peer, local=args.ether_local,
                         script=script))
    boot.progress = args.progress
    boot.idle_skip = not args.no_idle_skip
    boot.think = args.think
    boot.until_frames = args.until_frames
    if args.counter_period is not None:
        boot.quart.period_override = args.counter_period
    if args.until:
        boot.until = unescape(args.until)
    for item in args.type:
        wait, sep, reply = item.partition("=")
        if not sep:
            ap.error("--type wants TEXT=REPLY, not %r" % item)
        boot.script.append((unescape(wait), unescape(reply)))
    t0 = time.time()
    status = boot.run(args.max_steps)
    dt = time.time() - t0
    print("p9boot: %s" % status)
    print("p9boot: %d instructions in %.1f s (%d of them idle-loop "
          "iterations retired by %d idle skips)"
          % (boot.steps, dt, boot.skipped_steps, boot.skips))
    print("p9boot: functions reached, in order (step: name):")
    for stepno, name in boot.reached:
        print("  %10d  %s" % (stepno, name))
    if boot.wire is not None:
        if boot.wire.replay is not None and boot.wire.replay.mismatch:
            pos, got, want = boot.wire.replay.mismatch
            print("p9boot: replay: model frame %d differs from the "
                  "recording:\n  got  %s\n  want %s"
                  % (pos, decode_frame(got), decode_frame(want)))
        print("p9boot: %d frames on the wire:" % len(boot.wire.log))
        for t, way, frame in boot.wire.log:
            print("  %.6f %s %s" % (t, way, decode_frame(frame)))
    for t, frame, outcome in boot.sonic.received:
        if outcome != "received":
            print("p9boot: inbound frame at %.6f not taken: %s" % (t, outcome))
    for stepno, wait, reply in boot.typed:
        print("p9boot: step %d: typed %r after %r" % (stepno, reply, wait))
    for n, port in enumerate(boot.quart.ports):
        if port["pending"] or port["fifo"]:
            print("p9boot: uart%d input not yet read: %r" % (
                n, bytes(port["fifo"]) + bytes(port["pending"])))
        if port["out"]:
            boot.console["uart%d" % n] = port["out"]
    print("p9boot: %d interrupts taken, model time %.3f s" % (
        boot.interrupts, boot.cycles / float(CPU_HZ)))
    if boot.sysm.cret_clamps:
        print("p9boot: %d CRETs with MSP > SP + 256 clamped "
              "(CHOICES['cret-msp'])" % boot.sysm.cret_clamps)
    if boot.sysm.untimed:
        print("p9boot: untimed (cyc 0): %s" % dict(boot.sysm.untimed))
    for chan, data in sorted(boot.console.items()):
        print("p9boot: console %s: %d bytes: %r" % (chan, len(data),
                                                    bytes(data)))
        if args.out:
            os.makedirs(args.out, exist_ok=True)
            with open(os.path.join(args.out, chan), "wb") as f:
                f.write(data)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
