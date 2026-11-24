#!/usr/bin/env python3
"""An instruction-set model of the AT&T WE DSP3210 (the Hobbit BeBox's DSPs).

Written from the *WE DSP3210 Digital Signal Processor Information Manual*,
AT&T Microelectronics, September 1991 (docs/dsp3210/MANIFEST.md; page
numbers are the printed ones) and checked against Be's own DSP code on the
Nov 1994 disk (docs/dsp3210.md).  Decoding is tools/dsp3210dis.py's.

What is modelled, with the page each rule comes from:

  - the register file: r0 (zero) .. r22, pc (reads as the instruction's
    address + 8), pcsh; ps, emr, spc, pcw, dauc, ctr (Table 10-2, 4-6..4-11);
  - the delayed branch: the instruction after goto/call/return executes
    before the target, ireturn has no delay (Latency 3, p. 4-14);
    call stores the address after the delay slot in rM;
  - do / dolock / doblock K, {L, rM}: the next K+1 instructions L+1 (rM+1)
    times (p. 4-31);
  - CA arithmetic/logic, 16- and 32-bit, conditional, with the n z v c
    flags of Table 4-1 (p. 4-3);
  - the memory map of Figure 3-4 (p. 3-10), selected by pcw C/PN: boot
    ROM and MMIO at 0x0/0x400 or 0x50030000/0x50030400, on-chip RAM1/RAM0
    at 0xE000/0xF000 (2 x 1K words), everything else on the bus;
  - reset and the boot ROM (Appendix A, pp. A-1..A-4), modelled
    behaviourally: pcw[10..13] come from the BIO[7..4] pins; with BRC = 1
    the ROM copies 8 header bytes from the low bytes of the words at
    0x60000000 (address, then count, big-endian as Be's vcArmDsp writes
    them) and, after count more bytes from 0x60000020, branches to the
    address; with BRC = 0 it waits for IREQ1, takes the vector at physical
    0 and clears it;
  - interrupts: emr bit n enables the source whose vector is r22 + 8n (the
    boot ROM's table, p. A-3, and emr, Table 10-7); entry saves pc into
    pcsh and the DAU state into shadows, ireturn restores them (7.5.1);
    waiti stops execution until an enabled interrupt (3.2.3);
  - the timer (tcon 0x413, timer 0x414; Table 10-11), counting CKI/2 or
    CKI/4 at four CKI per instruction (Figure 1-3: 60 ns at 66 MHz);
  - the DAU: DSP32 floating point (N = M * 2^(e-128), M = (-2)^s + 0.f,
    e = 0 is zero; p. 3-8), the multiply/accumulate formats 1-4 and the
    special functions of format 5 (Tables 4-2, 4-4), the IEEE conversions
    of 8.2.4.1, and three latencies of 4.4.2: a DA memory write becomes
    visible four instructions later, an accumulator used as a multiplier
    input is the value of three instructions before, and a DAU condition
    is the flags of four instructions before.

Not modelled (each fails loud where reachable, or is documented as a
stand-in): the 40-bit accumulator's exact rounding (accumulators hold a
Python float, truncated to the 32-bit format on every store; bit-exact
DAU arithmetic needs the guard-bit rules of 8.2.3 transcribed), mu-law /
A-law ic/oc, seed, the serial port's bit timing and DMA (the SIO and DMA
registers are plain storage; `sio_out`/`sio_in` hooks see obuf writes and
supply ibuf), dolock bus locking, the error exceptions other than illegal
opcode.

Bus: `read(addr, size)` and `write(addr, size, value)` callbacks, size in
bytes (1, 2, 4), big-endian values (B/LN = 1, the Be modules' byte order).
"""
import math
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dsp3210dis as dis  # noqa: E402

M32 = 0xFFFFFFFF

# ------------------------------------------------------------ DSP32 float


def dsp_to_float(w):
    """32-bit DSP32 word -> Python float (exact).  p. 3-8."""
    e = w & 0xFF
    if e == 0:
        return 0.0
    s = w >> 31
    f = (w >> 8) & 0x7FFFFF
    m = (-2.0 if s else 1.0) + f / 8388608.0
    return math.ldexp(m, e - 128)


def float_to_dsp(x):
    """Python float -> DSP32 word, mantissa truncated toward minus infinity
    (two's-complement truncation), clamped to the format's range."""
    if x == 0.0 or math.isnan(x):
        return 0
    if math.isinf(x):
        return 0x7FFFFFFF if x > 0 else 0x800000FF
    m, ex = math.frexp(x)          # x = m * 2^ex, 0.5 <= |m| < 1
    if x > 0:
        m, ex = m * 2.0, ex - 1    # 1 <= m < 2
        f = int(math.floor((m - 1.0) * 8388608.0))
        s = 0
    else:
        m, ex = m * 2.0, ex - 1    # -2 < m <= -1
        if m == -1.0:              # -1 is -2 * 2^-1 in this format
            m, ex = -2.0, ex - 1
        f = int(math.floor((m + 2.0) * 8388608.0))
        s = 1
        if f >= 8388608:           # rounding carried into -1: renormalise
            f, ex = 0, ex - 1
    e = ex + 128
    if e > 255:
        return 0x7FFFFFFF if s == 0 else 0x800000FF
    if e < 1:
        return 0
    return (s << 31) | (f << 8) | e


def ieee_to_dsp(w):
    """IEEE single -> DSP32 (8.2.4.1, p. 8-12)."""
    e = (w >> 23) & 0xFF
    if e == 255:
        return 0x7FFFFFFF if not w >> 31 else 0x800000FF
    if e == 0:
        return 0
    return float_to_dsp(struct.unpack(">f", struct.pack(">I", w))[0])


def dsp_to_ieee(w):
    x = dsp_to_float(w)
    return struct.unpack(">I", struct.pack(">f", x))[0] if x else 0


def s32(v):
    v &= M32
    return v - (1 << 32) if v & 0x80000000 else v


def sx(v, bits):
    v &= (1 << bits) - 1
    return v - (1 << bits) if v >> (bits - 1) else v


class DspError(Exception):
    """A path the model does not implement, or an illegal instruction with
    no handler: fail loud."""


# ------------------------------------------------------------ the core

RAM_BASE = 0xE000
RAM_SIZE = 0x2000
MMIO_LO, MMIO_HI = 0x400, 0x800
ONCHIP_C = 0x0             # C/PN = 1 (computer mode)
ONCHIP_P = 0x50030000      # C/PN = 0 (processor mode)

PCW_CPN = 1 << 10
PCW_BRC = 1 << 13

# I/O register codes (R field)
PS, EMR, SPC, PCW, DAUC, CTR = 0, 8, 10, 12, 14, 15

VEC_EXT0, VEC_TIMER, VEC_SIOIN, VEC_SIOOUT = 8, 9, 11, 12
VEC_DMAIN, VEC_DMAOUT, VEC_EXT1 = 13, 14, 15
VEC_ILLEGAL = 2


class DSP3210:
    """One DSP3210.  `read`/`write` reach the board bus for every address
    that is not on-chip."""

    CKI_PER_INSN = 4

    def __init__(self, read, write, name="dsp"):
        self.bus_read = read
        self.bus_write = write
        self.name = name
        self.ram = bytearray(RAM_SIZE)
        self.sio_out = None        # callback(word) on obuf write
        self.sio_in = None         # callback() -> word or None for ibuf
        self.on_bio = None         # callback(pins) when the BIO outputs change
        self.cycles = 0            # instruction cycles since construction
        self.reset(bio_pins=0)
        self.running = False       # held in reset until released

    # -------------------------------------------------- the board's view
    # The interface tools/beboot.py drives (docs/dsp3210.md "Interface").

    def hold_reset(self):
        """RESTN low: the DSP stops; on-chip RAM keeps its contents."""
        self.running = False

    def release(self, bio_pins=0xF0):
        """RESTN high: latch pcw[10..13] from BIO[7..4] and run the boot
        ROM.  0xF0 gives pcw bits 10-13 all set, the value of Be's
        vcos.cfg `Boot= 0x3d80` (C/PN = 1, BRC = 1); that the BeBox straps
        the pins that way is inferred from that file, not seen on a
        schematic."""
        self.reset(bio_pins)

    def run(self, n):
        """Advance n instruction cycles (4 CKI each); time passes in reset
        and in waiti too.  Returns the number of instructions executed."""
        done = 0
        for _ in range(n):
            self.cycles += 1
            if self.running and self.step():
                done += 1
        return done

    @property
    def idle(self):
        """In reset, or in waiti with no enabled interrupt pending and the
        timer stopped: nothing changes until the board does something."""
        if not self.running:
            return True
        return (self.waiting and not self.mmio.get(0x413, 0) & 1
                and not self.irq_latched & self.ior[EMR] & 0xFF00)

    # -------------------------------------------------- reset and boot ROM

    def reset(self, bio_pins=0x90):
        """Hold in reset: pcw[10..13] latch BIO[7..4] (Table 10-8).  The
        default 0x90 is BIO7 = 1 (C/PN, computer mode), BIO4 = 1 (BRC):
        Be's vcos.cfg asks for pcw 0x3d80, whose bits 10-13 are all set,
        so BIO5/BIO6 (DRAM signalling, RW sense) are left for the caller."""
        self.r = [0] * 32          # indexed by the 5-bit CAU code
        self.pcsh = 0
        pcw = 0x3B80 & ~(0xF << 10)  # reset values: wait states, B/LN, M/IN
        for i in range(4):
            if bio_pins & (1 << (4 + i)):
                pcw |= 1 << (10 + i)
        self.ior = {PS: 0, EMR: 0, SPC: 0, PCW: pcw, DAUC: 0, CTR: 0}
        self.flags = dict(n=0, z=0, v=0, c=0)
        self.acc = [0.0, 0.0, 0.0, 0.0]
        self.acc_hist = [list(self.acc)] * 4
        self.dflags = dict(N=0, Z=1, V=0, U=0)
        self.dflag_hist = [dict(self.dflags)] * 4
        self.pending = []          # [countdown, addr, size, value] DA writes
        self.mmio = {}
        self.timer_count = 0
        self.timer_init = 0
        self.timer_frac = 0
        self.irq_pins = 0          # bit 0 IREQ0, bit 1 IREQ1 (level)
        self.irq_latched = 0       # set of vector numbers pending
        self.in_interrupt = False
        self.shadow = None
        self.waiting = False
        self.loops = []            # [start, end, remaining]
        self.pc = 0
        self.npc = 4
        self.steps = 0
        self.boot_state = None
        self.running = True
        self._rom_reset()

    def _rom_reset(self):
        """Run Appendix A's code for the reset vector, behaviourally."""
        pcw = self.ior[PCW]
        if not pcw & PCW_CPN:      # processor mode: start at external 0
            self._jump(0)
            return
        if pcw & PCW_BRC:          # BRC = 1: load from byte-wide memory
            hdr = [self.bus_read(0x60000000 + 4 * i, 4) & 0xFF for i in range(8)]
            for i, b in enumerate(hdr):
                self.ram[i] = b    # *r3++ = (byte) r4 into 0xE000..
            addr = int.from_bytes(bytes(hdr[0:4]), "big")
            count = int.from_bytes(bytes(hdr[4:8]), "big")
            r2 = 0x60000020
            for i in range(count):
                self.store(addr + i, 1, self.bus_read(r2, 4) & 0xFF)
                r2 += 4
            self.r[1], self.r[2], self.r[5] = addr, r2, count
            self.boot_state = ("brc1", addr, count)
            self._jump(addr)
            return
        # BRC = 0: r22 = 0x50030000, emr = 0x8000, C/PN := 0, waiti.
        self.r[26] = 0x50030000
        self.ior[EMR] = 0x8000
        self.ior[PCW] = pcw & ~PCW_CPN
        self.boot_state = ("brc0-wait",)
        self.waiting = True

    def _rom_ext1(self):
        """Boot ROM vector 15 (p. A-4): pcsh = *0; emr = 0; *0 = 0; ireturn."""
        vec = self.bus_read(0, 4)
        self.ior[EMR] = 0
        self.bus_write(0, 4, 0)
        self.boot_state = ("brc0", vec)
        self.in_interrupt = False
        self._jump(vec)

    def _jump(self, a):
        self.pc = a & M32
        self.npc = (a + 4) & M32

    # -------------------------------------------------- memory

    def onchip_base(self):
        return ONCHIP_C if self.ior[PCW] & PCW_CPN else ONCHIP_P

    def _local(self, addr):
        off = addr - self.onchip_base()
        if 0 <= off < 0x10000:
            return off
        return None

    def load(self, addr, size):
        addr &= M32
        off = self._local(addr)
        if off is not None:
            if off >= RAM_BASE:
                return int.from_bytes(self.ram[off - RAM_BASE:off - RAM_BASE + size], "big")
            if MMIO_LO <= off < MMIO_HI:
                return self._mmio_read(off, size)
            if off < MMIO_LO:
                raise DspError("%s: data read of boot ROM 0x%x (no ROM image)"
                               % (self.name, addr))
            raise DspError("%s: read of reserved on-chip 0x%x" % (self.name, addr))
        return self.bus_read(addr, size)

    def store(self, addr, size, value):
        addr &= M32
        value &= (1 << (8 * size)) - 1
        off = self._local(addr)
        if off is not None:
            if off >= RAM_BASE:
                self.ram[off - RAM_BASE:off - RAM_BASE + size] = value.to_bytes(size, "big")
                return
            if MMIO_LO <= off < MMIO_HI:
                self._mmio_write(off, size, value)
                return
            raise DspError("%s: write to on-chip 0x%x" % (self.name, addr))
        self.bus_write(addr, size, value)

    def fetch(self, addr):
        off = self._local(addr)
        if off is not None and off < MMIO_LO:
            raise DspError("%s: fetch from boot ROM 0x%x outside the modelled "
                           "reset/IREQ1 paths" % (self.name, addr))
        return self.load(addr, 4)

    # MMIO (Figure 3-5, big-endian addresses; mmio.h)
    def _mmio_read(self, off, size):
        if off == 0x404 and self.sio_in is not None:
            v = self.sio_in()
            if v is not None:
                self.mmio[0x404] = v
        if off == 0x414:
            return self.timer_count & M32
        return self.mmio.get(off, 0) & ((1 << (8 * size)) - 1)

    def _mmio_write(self, off, size, value):
        if off == 0x41E:           # bio: 2-bit fields per pin (Table 10-13)
            out = self.mmio.get("bio_out", 0)
            for i in range(8):
                f = (value >> (2 * i)) & 3
                if f == 1:
                    out &= ~(1 << i)
                elif f == 2:
                    out |= 1 << i
                elif f == 3:
                    out ^= 1 << i
            changed = out != self.mmio.get("bio_out", 0)
            self.mmio["bio_out"] = out
            if changed and self.on_bio is not None:
                self.on_bio(out)
            self.mmio[0x41E] = sum(((out >> i) & 1) << (2 * i + 1) for i in range(8))
            return
        self.mmio[off] = value
        if off == 0x414:
            self.timer_count = self.timer_init = value
        if off == 0x408 and self.sio_out is not None:
            self.sio_out(value)

    # -------------------------------------------------- registers

    def get(self, code, addr):
        if code == 15:
            return (addr + 8) & M32
        if code == 30:
            return self.pcsh
        if code in (22, 23):
            return M32 if code == 22 else 1
        if code not in dis.CAU_VALID:
            raise DspError("%s: reserved register code %d at 0x%x" % (self.name, code, addr))
        return self.r[code]

    def put(self, code, value):
        if code == 0:
            return
        if code == 15:
            self._jump(value)          # writing pc: undelayed
            return
        if code == 30:
            self.pcsh = value & M32
            return
        self.r[code] = value & M32

    # -------------------------------------------------- interrupts

    def set_irq(self, pin, level):
        """Drive IREQ0 (pin 0) or IREQ1 (pin 1); 1 = asserted."""
        if level:
            self.irq_pins |= 1 << pin
            self.irq_latched |= 1 << (VEC_EXT0 if pin == 0 else VEC_EXT1)
        else:
            self.irq_pins &= ~(1 << pin)

    def _take_interrupt(self):
        pend = self.irq_latched & self.ior[EMR] & 0xFF00
        if not pend or self.in_interrupt:
            return False
        for vec in range(8, 16):       # EXT0 highest ... EXT1 lowest
            if pend & (1 << vec):
                break
        self.irq_latched &= ~(1 << vec)
        self.waiting = False
        if self.boot_state == ("brc0-wait",) and vec == VEC_EXT1:
            self._rom_ext1()
            return True
        self.in_interrupt = True
        self.pcsh = self.pc
        self.shadow = (list(self.acc), dict(self.dflags), self.ior[DAUC],
                       [list(l) for l in self.loops], self.npc)
        self.loops = []
        self._jump(self.r[26] + 8 * vec)
        return True

    def _ireturn(self):
        if self.shadow is not None:
            self.acc, self.dflags, self.ior[DAUC], self.loops, _npc = self.shadow
            self.shadow = None
        self.in_interrupt = False
        self._jump(self.pcsh)

    # -------------------------------------------------- timer

    def _tick(self):
        tcon = self.mmio.get(0x413, 0)
        if not tcon & 1:
            return
        div = {0: 2, 1: 4}.get(tcon >> 5)
        if div is None:
            return                     # external BIO0 clock: not modelled
        self.timer_frac += self.CKI_PER_INSN
        while self.timer_frac >= div:
            self.timer_frac -= div
            if self.timer_count == 0:
                continue
            self.timer_count -= 1
            if self.timer_count == 0:
                self.irq_latched |= 1 << VEC_TIMER
                if tcon & 2:
                    self.timer_count = self.timer_init

    # -------------------------------------------------- conditions

    def cond(self, c):
        f = self.flags
        if c < 16:
            n, z, v, cc = f["n"], f["z"], f["v"], f["c"]
            t = [False, True, not n, n, not z, z, not v, v, not cc, cc,
                 not (n ^ v), n ^ v, not (z or (n ^ v)), z or (n ^ v),
                 not (cc or z), cc or z][c]
            return bool(t)
        if c < 26:
            d = self.dflag_hist[0]     # established four instructions before
            N, Z, V, U = d["N"], d["Z"], d["V"], d["U"]
            return bool([not U, U, not N, N, not Z, Z, not V, V,
                         not (N or Z), N or Z][c - 16])
        if 32 <= c < 48:
            ioc = self.mmio
            ibf = 0x404 in ioc and ioc.get("ibf", 0)
            m = {32: not ibf, 33: ibf, 34: False, 35: True,
                 40: False, 41: True, 42: False, 43: False,
                 44: not (self.irq_pins & 1), 45: bool(self.irq_pins & 1),
                 46: not (self.irq_pins & 2), 47: bool(self.irq_pins & 2)}
            if c in m:
                return bool(m[c])
        raise DspError("%s: condition code %d not modelled" % (self.name, c))

    # -------------------------------------------------- CA ALU

    def _alu(self, f, a, b, e, addr):
        """F field function on 32-bit a, b; e = 1 for 32-bit.  Returns
        (result or None for no store, flags)."""
        bits = 32 if e else 16
        mask = (1 << bits) - 1
        sign = 1 << (bits - 1)
        c = v = 0
        if f == 0:                      # +
            r = (a & mask) + (b & mask)
            c = r >> bits & 1
            v = int(((a ^ r) & (b ^ r) & sign) != 0)
        elif f in (4, 7, 2):            # -, compare, reverse subtract
            if f == 2:
                a, b = b, a
            r = (a & mask) - (b & mask)
            c = int(r < 0)              # borrow
            v = int(((a ^ b) & (a ^ r) & sign) != 0)
        elif f == 3:                    # carry-reverse add
            ra = int(format(a & mask, "0%db" % bits)[::-1], 2)
            rb = int(format(b & mask, "0%db" % bits)[::-1], 2)
            s = ra + rb
            c = s >> bits & 1
            r = int(format(s & mask, "0%db" % bits)[::-1], 2)
        elif f == 1:
            r = (a << (b & 31))
            c = (r >> bits) & 1 if b & 31 else 0
        elif f == 12:
            r = (a & mask) >> (b & 31)
        elif f == 13:
            r = sx(a, bits) >> (b & 31)
        elif f == 9:                    # rotate right by 1 through... (no carry)
            r = ((a & mask) >> 1) | ((a & 1) << (bits - 1))
            c = a & 1
        elif f == 11:
            r = ((a << 1) & mask) | ((a >> (bits - 1)) & 1)
            c = (a >> (bits - 1)) & 1
        elif f == 6:
            r = a & ~b
        elif f == 8:
            r = a ^ b
        elif f == 10:
            r = a | b
        elif f in (14, 15):
            r = a & b
        else:
            raise DspError("%s: ALU function %d at 0x%x" % (self.name, f, addr))
        res = r & mask
        flags = dict(n=int(bool(res & sign)), z=int(res == 0), v=v, c=c)
        if not e:
            res = sx(res, 16) & M32
        if f in (7, 15):
            return None, flags
        return res, flags

    # -------------------------------------------------- one instruction

    def step(self):
        """Execute one instruction cycle.  Returns False while waiting."""
        if not self.running:
            return False
        self._tick()
        self._drain_writes()
        if self._take_interrupt():
            pass
        if self.waiting:
            return False
        addr = self.pc
        word = self.fetch(addr)
        nxt = self.npc
        self.pc, self.npc = nxt, (nxt + 4) & M32
        self._dflag_new = None
        self._execute(word, addr)
        # do loops: after the last instruction of the body, go back.
        if self.loops:
            lp = self.loops[-1]
            if self.pc == lp[1] and self.npc == (lp[1] + 4) & M32:
                if lp[2] > 0:
                    lp[2] -= 1
                    self._jump(lp[0])
                else:
                    self.loops.pop()
        self.dflag_hist = self.dflag_hist[1:] + [dict(self.dflags)]
        self.acc_hist = self.acc_hist[1:] + [list(self.acc)]
        self.steps += 1
        return True

    def _drain_writes(self):
        keep = []
        for w in self.pending:
            w[0] -= 1
            if w[0] <= 0:
                self.store(w[1], w[2], w[3])
            else:
                keep.append(w)
        self.pending = keep

    def _branch(self, target):
        """Delayed: the instruction already in npc runs first."""
        self.npc = target & M32

    def _execute(self, w, addr):
        top3 = w >> 29
        if top3 in (1, 2, 3):
            self._da(w, addr)
            return
        if top3 >= 5:
            m = (((w >> 21) & 0xFF) << 16) | (w & 0xFFFF)
            r = (w >> 16) & 31
            if top3 == 5:
                self._branch(self.get(r, addr) + m)
            elif top3 == 6:
                self.put(r, m)
            else:
                self.put(r, addr + 8)
                self._branch(m)
            return
        e = w >> 31
        op = (w >> 25) & 0x3F
        if op >> 2 == 0:
            if not e:
                return self._illegal(w, addr)
            c = (w >> 21) & 63
            rb = (w >> 16) & 31
            n = sx(w, 16)
            if c == 1 and rb == 30 and n == 0:
                self._ireturn()
                return
            if self.cond(c):
                self._branch(self.get(rb, addr) + n)
            return
        if op >> 1 == 2:
            return self._illegal(w, addr)
        if op >> 1 == 3:
            if not e:                           # if (rM-- >= 0) goto
                rm = (w >> 21) & 31
                rb = (w >> 16) & 31
                val = s32(self.get(rm, addr))
                self.put(rm, val - 1)
                if val >= 0:
                    self._branch(self.get(rb, addr) + sx(w, 16))
                return
            k = (w >> 11) & 0x7F
            cnt = self.get(w & 31, addr) & 0x7FF if (w >> 25) & 1 else w & 0x7FF
            if (w >> 23) & 1:
                k = 0                           # doblock: K = 0 implicit
            start = self.pc
            self.loops.append([start, (start + 4 * (k + 1)) & M32, cnt])
            return
        if op >> 1 == 4:
            r1_ = (w >> 21) & 31
            r2_ = (w >> 16) & 31
            if not e:                           # call rB+N (rM)
                tgt = self.get(r2_, addr) + sx(w, 16)
                self.put(r1_, addr + 8)
                self._branch(tgt)
            else:                               # rD = rS <<| N
                v = (self.get(r2_, addr) & 0xFFFF) | ((w & 0xFFFF) << 16)
                self.put(r1_, v)
                self.flags.update(n=v >> 31, z=int(v == 0), v=0, c=0)
            return
        if op >> 1 == 5:                        # rD = rS3 + N
            rd = (w >> 21) & 31
            rs = (w >> 16) & 31
            a = self.get(rs, addr)
            res, fl = self._alu(0, a, sx(w, 16) & M32, e, addr)
            self.put(rd, res)
            self.flags.update(fl)
            return
        if op == 0b001100:                      # register ALU, conditional
            f = (w >> 21) & 15
            rd = (w >> 16) & 31
            rs1 = (w >> 11) & 31
            c = (w >> 5) & 63
            rs2 = w & 31
            if not self.cond(c):
                return
            a = self.get(rs1, addr)
            if rs2 in (22, 23):
                if f == 0 and rd == rs1 == 25:      # sp++ / sp--: by 4
                    b = 4 if rs2 == 23 else (-4) & M32
                elif f == 0:
                    b = 1 if rs2 == 23 else M32
                else:
                    b = 1
            else:
                b = self.get(rs2, addr)
            res, fl = self._alu(f, a, b, e, addr)
            if res is not None:
                self.put(rd, res)
            self.flags.update(fl)
            return
        if op == 0b001101:                      # rD = rD F N
            f = (w >> 21) & 15
            rd = (w >> 16) & 31
            n = sx(w, 16) & M32
            res, fl = self._alu(f, self.get(rd, addr), n, e, addr)
            if res is not None:
                self.put(rd, res)
            self.flags.update(fl)
            return
        if op in (0b001110, 0b001111):
            self._move(w, addr, e, op)
            return
        self._illegal(w, addr)

    def _illegal(self, w, addr):
        raise DspError("%s: illegal instruction 0x%08x at 0x%x" % (self.name, w, addr))

    # moves -----------------------------------------------------------
    SIZE = {0: 1, 1: 1, 2: 2, 3: 2, 4: 1, 7: 4}

    def _load_conv(self, wsz, v):
        if wsz == 1:
            return sx(v, 8) & M32
        if wsz == 3:
            return sx(v, 16) & M32
        if wsz == 4:
            return (v & 0xFF) << 8
        return v

    def _store_val(self, wsz, v):
        if wsz == 4:
            return (v >> 8) & 0xFF
        return v

    def _mem_operand(self, w, addr):
        rp = (w >> 11) & 31
        ri = w & 31
        p = self.get(rp, addr)
        return rp, ri, p

    def _postmod(self, rp, ri, size, addr):
        if ri == 0:
            return
        if rp == 25:
            size = 4                           # sp: always by 4
        if ri == 22:
            self.put(rp, self.r[rp] - size)
        elif ri == 23:
            self.put(rp, self.r[rp] + size)
        else:
            self.put(rp, self.r[rp] + self.get(ri, addr))

    def _set_load_flags(self, v):
        self.flags.update(n=(v >> 31) & 1, z=int(v & M32 == 0), v=0, c=0)

    def _move(self, w, addr, e, op):
        t = (w >> 24) & 1
        wsz = (w >> 21) & 7
        rh = (w >> 16) & 31
        if wsz not in self.SIZE:
            return self._illegal(w, addr)
        size = self.SIZE[wsz]
        if not e:                               # 7a *L
            ea = self.onchip_base() + (w & 0xFFFF)
            if t:
                self.store(ea, size, self._store_val(wsz, self.get(rh, addr)))
            else:
                v = self._load_conv(wsz, self.load(ea, size))
                self.put(rh, v)
                self._set_load_flags(v)
            return
        if op == 0b001110 and (w >> 10) & 1:    # 7b rH <-> ior
            io = w & 31
            if t:
                if io == SPC and rh == 0:
                    if wsz == 7:
                        self.waiting = True     # waiti
                        return
                    raise DspError("%s: spc = r0 (%s) at 0x%x not modelled"
                                   % (self.name, "bkpt/sftrst", addr))
                self._ior_write(io, self.get(rh, addr), size, addr)
            else:
                v = self._load_conv(wsz, self._ior_read(io, addr))
                self.put(rh, v)
                self._set_load_flags(v)
            return
        rp, ri, p = self._mem_operand(w, addr)
        if op == 0b001110:                      # 7c rH <-> *rP
            if t:
                self.store(p, size, self._store_val(wsz, self.get(rh, addr)))
            else:
                v = self._load_conv(wsz, self.load(p, size))
                self._postmod(rp, ri, size, addr)
                self.put(rh, v)
                self._set_load_flags(v)
                return
            self._postmod(rp, ri, size, addr)
            return
        if t:                                   # 7d *rP <-> ior
            self.store(p, size, self._ior_read(rh, addr))
        else:
            self._ior_write(rh, self.load(p, size), size, addr)
        self._postmod(rp, ri, size, addr)

    def _ior_read(self, io, addr):
        if io == PS:
            f = self.flags
            d = self.dflags
            return (f["c"] | f["v"] << 1 | f["z"] << 2 | f["n"] << 3
                    | d["U"] << 4 | d["V"] << 5 | d["Z"] << 6 | d["N"] << 7)
        if io in self.ior:
            return self.ior[io]
        raise DspError("%s: I/O register %d at 0x%x" % (self.name, io, addr))

    def _ior_write(self, io, v, size, addr):
        if io == PCW and self.ior[PCW] & PCW_BRC and False:
            return
        if io == PS:
            self.flags.update(c=v & 1, v=(v >> 1) & 1, z=(v >> 2) & 1, n=(v >> 3) & 1)
            self.dflags.update(U=(v >> 4) & 1, V=(v >> 5) & 1, Z=(v >> 6) & 1, N=(v >> 7) & 1)
            return
        if io not in self.ior:
            raise DspError("%s: I/O register %d at 0x%x" % (self.name, io, addr))
        mask = (1 << (8 * size)) - 1
        self.ior[io] = (self.ior[io] & ~mask) | (v & mask)

    # DAU -----------------------------------------------------------

    def _da_ptr(self, f):
        p, i = f >> 3, f & 7
        if p == 0 or p == 15:
            return None
        return p, i

    def _da_post(self, p, i, size=4):
        if i == 0:
            return
        if i == 6:
            self.r[p] = (self.r[p] - size) & M32
        elif i == 7:
            self.r[p] = (self.r[p] + size) & M32
        else:
            self.r[p] = (self.r[p] + self.r[16 + i]) & M32   # r15..r19 = codes 17..21

    def _da_read(self, f, mult, size=4):
        """X/Y operand: (float value, raw word).  mult: multiplier input,
        which sees an accumulator as of three instructions before."""
        p, i = f >> 3, f & 7
        if p == 0:
            if i > 3:
                raise DspError("%s: DA operand 0x%x" % (self.name, f))
            v = (self.acc_hist[-2] if mult else self.acc)[i]
            return v, float_to_dsp(v)
        if p == 15:
            raise DspError("%s: DA operand p=1111 (undocumented)" % self.name)
        raw = self.load(self.r[p], size)
        self._da_post(p, i, size)
        return dsp_to_float(raw), raw

    def _da_write(self, f, value_word, size=4):
        p, i = f >> 3, f & 7
        if p == 0:
            if i == 7:
                return
            raise DspError("%s: DA Z operand 0x%x" % (self.name, f))
        self.pending.append([4, self.r[p], size, value_word])
        self._da_post(p, i, size)

    def _set_dflags(self, x):
        word = float_to_dsp(x)
        e = word & 0xFF
        self.dflags = dict(N=word >> 31, Z=int(e == 0),
                           V=int(abs(x) > 3.40282e38), U=int(x != 0 and e == 0))

    def _da(self, w, addr):
        n = (w >> 21) & 3
        xf, yf, zf = (w >> 14) & 0x7F, (w >> 7) & 0x7F, w & 0x7F
        if (w >> 27) == 0b01111:
            self._special((w >> 23) & 15, n, yf, zf, addr)
            return
        fmt = w >> 29
        m = (w >> 26) & 7
        neg = -1.0 if (w >> 24) & 1 else 1.0
        sgn = -1.0 if (w >> 23) & 1 else 1.0
        if fmt == 1 and m == 6:                 # FADD-TAP: aN = [-](Z=Y) +- X
            y, yraw = self._da_read(yf, False)
            x, _ = self._da_read(xf, False)
            self._da_write(zf, yraw)
            res = neg * y + sgn * x
        else:
            consts = {4: 0.0, 5: 1.0}
            if m in consts:
                am = consts[m]
            elif m < 4:
                am = self.acc[m]
            else:
                return self._illegal(w, addr)
            if fmt == 1:                        # aN = [-]Y +- aM*X
                y, _ = self._da_read(yf, False)
                x, _ = self._da_read(xf, True)
                mx = am if m > 3 else dsp_to_float(float_to_dsp(am))
                res = neg * y + sgn * mx * x
                if zf != 7:
                    self._da_write(zf, float_to_dsp(res))
            elif fmt == 2:                      # aN = [-]aM +- (Z=Y)*X
                y, yraw = self._da_read(yf, True)
                x, _ = self._da_read(xf, True)
                self._da_write(zf, yraw)
                res = neg * am + sgn * y * x
            else:                               # [Z=] aN = [-]aM +- Y*X
                y, _ = self._da_read(yf, True)
                x, _ = self._da_read(xf, True)
                res = neg * am + sgn * y * x
                if zf != 7:
                    self._da_write(zf, float_to_dsp(res))
        self.acc[n] = dsp_to_float(float_to_dsp(res)) if res else 0.0
        self.acc[n] = res if abs(res) < 3.5e38 else self.acc[n]
        self._set_dflags(res)

    def _special(self, g, n, yf, zf, addr):
        dauc = self.ior[DAUC]
        size = 4
        if g in (2, 3):
            size = 2
        if g in (0, 1):
            raise DspError("%s: ic/oc (mu-law/A-law) not modelled" % self.name)
        y_raw = None
        if yf >> 3 == 0:
            y_raw = float_to_dsp(self.acc[yf & 7]) if yf & 7 < 4 else None
            yval = self.acc[yf & 7]
            if g in (2, 9) or g == 8:
                y_raw = float_to_dsp(yval)
        else:
            p, i = yf >> 3, yf & 7
            y_raw = self.load(self.r[p], size)
            self._da_post(p, i, size)
            yval = dsp_to_float(y_raw)
        out_word = None
        res = None
        if g == 2:                              # float16
            res = float(sx(y_raw if yf >> 3 else int(yval), 16))
        elif g == 8:                            # float32
            res = float(s32(y_raw if yf >> 3 else int(yval)))
        elif g in (3, 9):                       # int16 / int32
            mode = (dauc >> 4) & 3              # 00 nearest, else truncate (Table 8-3)
            x = yval
            iv = int(math.floor(x + 0.5)) if mode == 0 else (
                int(math.floor(x)) if mode == 1 else int(x))
            bits = 16 if g == 3 else 32
            lo, hi = -(1 << (bits - 1)), (1 << (bits - 1)) - 1
            iv = max(lo, min(hi, iv))
            res = float(iv)
            out_word = iv & ((1 << bits) - 1)
            self.acc[n] = dsp_to_float(float_to_dsp(res))
            self._set_dflags(res)
            if zf != 7:
                self._da_write(zf, out_word, 2 if g == 3 else 4)
            return
        elif g == 4:                            # round to 32-bit
            res = dsp_to_float(float_to_dsp(yval))
        elif g in (5, 6, 7):                    # ifalt / ifaeq / ifagt
            d = self.dflags
            take = {5: d["N"], 6: d["Z"], 7: not (d["N"] or d["Z"])}[g]
            if take:
                self.acc[n] = yval
            if zf != 7 and (take or not dauc & 0x40):
                self._da_write(zf, float_to_dsp(self.acc[n]))
            return
        elif g == 12:                           # ieee: DSP -> IEEE
            out_word = dsp_to_ieee(y_raw if y_raw is not None else float_to_dsp(yval))
            res = yval
        elif g == 13:                           # dsp: IEEE -> DSP
            word = ieee_to_dsp(y_raw)
            res = dsp_to_float(word)
        else:
            raise DspError("%s: special function %d not modelled" % (self.name, g))
        self.acc[n] = res
        self._set_dflags(res)
        if zf != 7:
            self._da_write(zf, out_word if out_word is not None else float_to_dsp(res))


# ------------------------------------------------------------ for beboot


class Dsp3210:
    """The board's view of one DSP, the interface agreed with
    tools/beboot.py (docs/dsp3210.md "Interface").

    `bus` gives `read(addr, size) -> int`, `write(addr, value, size)` and
    `pins(name, level)`; addresses are DSP bus addresses, sizes 1/2/4
    bytes.  BIO output pins are reported as pins("bio0".."bio7", level).
    Constructed held in reset.  Picklable when `bus` is."""

    CLOCKS_PER_STEP = DSP3210.CKI_PER_INSN      # 4 CKI per instruction

    def __init__(self, n, bus):
        self.n = n
        self.bus = bus
        self.core = DSP3210(self._read, self._write, name="dsp%d" % n)
        self.core.on_bio = self._bio
        self._pins = 0

    def _read(self, addr, size):
        return self.bus.read(addr, size)

    def _write(self, addr, size, value):
        self.bus.write(addr, value, size)

    def _bio(self, out):
        for i in range(8):
            if (out ^ self._pins) >> i & 1:
                self.bus.pins("bio%d" % i, out >> i & 1)
        self._pins = out

    def release(self):
        """Rising edge of the board's reset bit: boot as Appendix A says."""
        self.core.release()

    def hold(self):
        self.core.hold_reset()

    def set_interrupt(self, level, pin=1):
        """The board's interrupt to the DSP, a level.  IREQ1 by default:
        the boot ROM's BRC = 0 path starts on IREQ1 (p. A-4), so a board
        that lets the host start a DSP wires the host's line there;
        inferred, not seen on a BeBox schematic."""
        self.core.set_irq(pin, level)

    def step(self):
        """One instruction cycle (or one cycle of reset or waiti).
        Returns the DSP clocks (CKI) it took."""
        self.core.run(1)
        return self.CLOCKS_PER_STEP

    @property
    def pc(self):
        return self.core.pc

    @property
    def idle(self):
        return self.core.idle


if __name__ == "__main__":
    print(__doc__)
