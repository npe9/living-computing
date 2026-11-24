#!/usr/bin/env python3
"""rtc_iic_check.py -- the RTL of the timekeeper (Rtc.bsv, mkRtc) and the
IIC bus (Iic.bsv, mkIic) against the Python models they replicate
(tools/p9boot.py Timekeeper and Iic), access for access.

    python3 hobbit/fpga/dev/rtc_iic_check.py          (~1 min)
    python3 hobbit/fpga/dev/rtc_iic_check.py -v       (list every sequence)

bsc 2026.01 compiles the two packages to Verilog; Verilator builds each
with rtc_iic_tb.cpp, which replays an access list into the device and
prints, per access, the cycle that took it, the response, the sticky
fault code and (IIC) the LED latch.  The same accesses go into a fresh
model at the same cycles (the RTC's clock is Fraction(cycle,
TICKS_PER_SEC), exact), and every read's value and every fault are
compared.  Sequences (rtc.md / iic.md "Test"):

  join traces   rtc_join.trace / iic_join.trace: every access s9term made
                in tests/test_p9boot.py JoinReplayTest (rtc_iic_capture.py),
                cycles scaled 20 MHz -> TICKS_PER_SEC; the IIC reads are
                also checked against the values recorded in that run
  synthetic     the second-boundary phase at reset and after a load;
                freeze (R), set (W) as devrtc.c setrtc does it; the control
                corners; minute/hour/day/month/year rollovers incl. Feb
                28/29 and 1999->2000, 2069->1970; 300 random dates (wday);
                NVRAM with romboot's Env at 0 and key.c's Nvrsafe at 1924;
                ledputbyte; a slave that does not acknowledge; EEPROM reads
                from other offsets and across 255->0
  faults        each access the model refuses must fault the RTL with the
                matching code, and the RTL-only faults (rtc.md, iic.md)
                must fault where the model does not

Exit status 0 iff every comparison holds.

Bug injection (AGENTS.md "proven discriminating"): rtc_iic_inject.py
injects each bug into the BSV, runs this check, and reverts by reverse
patch.  OBSERVED failures, 2026-11-24 (79 sequences; every other sequence
still agreed):

  R1 divider not restarted on a load (div <= 0)            71/79
     phase after a load, sec at load+1000 and load+2000, all 4 skews
     (load+999/+1001 agree: the second comes one cycle late).  The first
     run, before the phase probes were one per sequence, passed 52/52.
  R2 leap year from the units digit only                   77/79
     rollover Feb 28 1996, rollover Feb 29 1996
  R3 a new snapshot on every R/W control write             76/79
     W cleared with R still set loads and unfreezes; R then W without a
     new snapshot; fault: W cleared with nothing held
  R4 weekday table, March 2 -> 3                           78/79
     300 random dates
  R5 clock-register reads ignore the held set              74/79
     freeze with R; held set visible while W is set; R then W; fault:
     a load of month 0x13; RTL-only fault: Feb 30
  R6 April has 31 days                                     78/79
     rollover Apr 30
  R7 NVRAM index from addr[11:1]                           17/79
     62 RTC sequences: all but phase at reset at cycles 0, 998, 999
     and the RTL-only lane-1 fault (which faults before the index)
  R8 clock-register write without W accepted               77/79
     fault: written without RTCWRITE; fault: written with R only
  I1 repeated START's address taken as a data byte         75/79
     iic_join.trace; EEPROM reads from 5, from 250, from 0
  I2 LRB inverted                                          73/79
     iic_join.trace; ledputbyte; no-acknowledge slave; EEPROM x3
  I3 BB reads busy, not free                               72/79
     as I2, plus PIN set and STA|STO together
  I4 0xC0 does not complete the byte in progress           75/79
     iic_join.trace; EEPROM x3
  I5 LED latch write count not kept                        78/79
     ledputbyte x3
  I6 S0 read with ACK does not advance the pointer         75/79
     iic_join.trace; EEPROM x3
  I7 S0 readable with ESO off                              78/79
     fault: S0 read with ESO off
"""
import os
import random
import shutil
import subprocess
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
HOBBIT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HOBBIT, "tools"))
sys.path.insert(0, os.path.join(HOBBIT, "sem"))

import p9boot  # noqa: E402
import hobbit_sem  # noqa: E402

BUILD = os.path.join(HERE, "build")
TICKS_PER_SEC = 1000
SCALE = p9boot.CPU_HZ // TICKS_PER_SEC   # model cycles per RTL cycle
assert SCALE * TICKS_PER_SEC == p9boot.CPU_HZ

CTL, SEC, MIN, HOUR, WDAY, MDAY, MON, YEAR = (0x1FE0 + 4 * i
                                              for i in range(8))
REGNAME = {CTL: "control", SEC: "sec", MIN: "min", HOUR: "hour",
           WDAY: "wday", MDAY: "mday", MON: "mon", YEAR: "year"}
S0, S1 = 0, 4

# RTL fault codes (Rtc.bsv, Iic.bsv)
RTC_REG_NO_W, RTC_BAD_LOAD, RTC_LANE, RTC_NO_HELD = 1, 2, 3, 4
IIC_OFFSET, IIC_S0_ESO_OFF, IIC_REGSEL, IIC_LANE = 1, 2, 3, 4


# ---- build -------------------------------------------------------------

def bsc_paths():
    bsc = os.environ.get("BSC_BIN")
    if not bsc:
        cellar = "/opt/homebrew/Cellar/bsc"
        vers = sorted(os.listdir(cellar)) if os.path.isdir(cellar) else []
        if not vers:
            raise SystemExit("bsc not found; set BSC_BIN")
        bsc = os.path.join(cellar, vers[-1], "bin", "bsc")
    lib = os.path.normpath(os.path.join(os.path.dirname(bsc), "..",
                                        "libexec", "lib"))
    return bsc, lib


def start_bcd():
    """{year, mon, mday, wday, hour, min, sec} of p9boot.RTC_BASE, from
    the model's own register function, so the two cannot drift."""
    tk = p9boot.Timekeeper(lambda: 0, p9boot.RTC_BASE)
    sec, mn, hour, wday, mday, mon, year = tk._regs(p9boot.RTC_BASE)
    v = 0
    for b in (year, mon, mday, wday, hour, mn, sec):
        v = (v << 8) | b
    return v


def build(quiet=True):
    bsc, lib = bsc_paths()
    os.makedirs(BUILD, exist_ok=True)
    env = dict(os.environ, BLUESPECDIR=lib)
    out = None if not quiet else subprocess.DEVNULL
    for pkg, top in (("Rtc.bsv", "mkRtc"), ("Iic.bsv", "mkIic")):
        subprocess.run([bsc, "-verilog", "-g", top, "-u", "-vdir", BUILD,
                        "-bdir", BUILD, "-info-dir", BUILD, "-p", "+",
                        pkg], cwd=HERE, env=env, check=True, stdout=out,
                       stderr=out)
    libv = [os.path.join(lib, "Verilog", m) for m in
            ("RegFileLoad.v", "FIFO2.v")]
    for top, extra in (("mkRtc", ["-GticksPerSec=%d" % TICKS_PER_SEC,
                                  "-GstartBcd=56'h%014x" % start_bcd()]),
                       ("mkIic", ["-DDEV_IIC"])):
        mdir = os.path.join(BUILD, "obj_" + top)
        cflags = ["-CFLAGS", "-DDEV_IIC"] if top == "mkIic" else []
        subprocess.run(["verilator", "--cc", "--exe", "--build", "-j", "4",
                        "-Wno-fatal", "-Wno-lint", "-Wno-style", "--no-timing",
                        "--top-module", top, "-Mdir", mdir,
                        "-o", "tb_" + top,
                        os.path.join(BUILD, top + ".v")] + libv
                       + [os.path.join(HERE, "rtc_iic_tb.cpp")]
                       + [e for e in extra if e.startswith("-G")] + cflags,
                       cwd=HERE, check=True, stdout=out,
                       stderr=subprocess.DEVNULL if quiet else None)


def run_rtl(top, accesses):
    tb = os.path.join(BUILD, "obj_" + top, "tb_" + top)
    text = "".join("%d %s %x %x %x\n" % a for a in accesses)
    p = subprocess.run([tb], input=text, cwd=HERE, capture_output=True,
                       text=True)
    if p.returncode:
        raise SystemExit("%s harness failed: %s" % (top, p.stderr))
    rows = []
    for line in p.stdout.split("\n"):
        if line:
            a, d, f, led, n = line.split()
            rows.append((int(a), int(d, 16), int(f, 16), int(led, 16),
                         int(n, 16)))
    if len(rows) != len(accesses):
        raise SystemExit("%s harness: %d results for %d accesses"
                         % (top, len(rows), len(accesses)))
    return rows


# ---- the models ----------------------------------------------------------

class RtcModel:
    def __init__(self):
        self.now = 0
        self.m = p9boot.Timekeeper(lambda: Fraction(self.now, TICKS_PER_SEC),
                                   p9boot.RTC_BASE)

    def access(self, cyc, op, addr, data, be):
        self.now = cyc
        try:
            if op == "R":
                return self.m.read(addr & ~3), None
            self.m.write(addr & ~3, data, be)
            return None, None
        except hobbit_sem.BusError as e:
            return None, ("BusError", str(e), RTC_REG_NO_W)
        except TypeError as e:          # load with nothing held
            return None, ("TypeError", str(e), RTC_NO_HELD)
        except ValueError as e:         # timegm refuses the loaded date
            return None, ("ValueError", str(e), RTC_BAD_LOAD)


class IicModel:
    def __init__(self):
        self.m = p9boot.Iic(p9boot.eeprom_image())

    def access(self, cyc, op, addr, data, be):
        try:
            if op == "R":
                return self.m.read(addr & ~3), None
            self.m.write(addr & ~3, data, be)
            return None, None
        except p9boot.Stop as e:
            msg = str(e)
            code = (IIC_S0_ESO_OFF if "serial interface off" in msg
                    else IIC_REGSEL if "register select" in msg
                    else IIC_OFFSET)
            return None, ("Stop", msg, code)


# ---- sequences -------------------------------------------------------------

class Seq:
    """An access list; `t` is the target cycle of the next access."""

    def __init__(self, name, dev, expect_rtl_fault=None, recorded=None,
                 exact=False):
        self.name, self.dev = name, dev
        self.exact = exact
        self.acc = []
        self.t = 0
        self.gapc = 4
        # (index, code): the RTL must fault here although the model does not
        self.expect_rtl_fault = expect_rtl_fault
        self.recorded = recorded         # recorded read values (join trace)

    def at(self, t):
        self.t = max(self.t, t)
        return self

    def r(self, addr):
        self.acc.append((self.t, "R", addr, 0, 0))
        self.t += self.gapc

    def w(self, addr, data, be=1):
        self.acc.append((self.t, "W", addr, data, be))
        self.t += self.gapc


def bcd(v):
    return ((v // 10) << 4) | (v % 10)


def setrtc(s, y, mo, d, h, mi, se, ctl=0):
    """devrtc.c setrtc: control |= RTCWRITE; year, mon, mday, hour, min,
    sec; control &= ~RTCWRITE (control read before each update)."""
    s.r(CTL)
    s.w(CTL, ctl | 0x80)
    for reg, v in ((YEAR, y % 100), (MON, mo), (MDAY, d), (HOUR, h),
                   (MIN, mi), (SEC, se)):
        s.w(reg, bcd(v))
    s.r(CTL)
    s.w(CTL, ctl & ~0x80)


def rtctime(s):
    """devrtc.c rtctime."""
    s.r(CTL)
    s.w(CTL, 0x40)
    for reg in (SEC, MIN, HOUR, MDAY, MON, YEAR):
        s.r(reg)
    s.r(CTL)
    s.w(CTL, 0x00)


def read_all(s):
    for reg in (CTL, SEC, MIN, HOUR, WDAY, MDAY, MON, YEAR):
        s.r(reg)


def load_trace(path, dev):
    s = Seq(os.path.basename(path), dev, recorded=[])
    for line in open(path):
        if line.startswith("#"):
            continue
        c, op, off, data, mask, res = line.split()[:6]
        s.at(int(c) // SCALE)
        s.acc.append((s.t, op, int(off, 16), int(data, 16), int(mask, 16)))
        s.recorded.append(None if res == "-" else int(res, 16))
    return s


def rtc_sequences():
    T = TICKS_PER_SEC
    seqs = []

    # One probe read per sequence, so it is taken at exactly its cycle
    # (`exact`: the harness's accept cycle must equal the target).
    for c in (0, T - 2, T - 1, T, T + 1, 2 * T - 1, 2 * T, 2 * T + 1):
        s = Seq("phase at reset: sec at cycle %d" % c, "rtc", exact=True)
        s.at(c)
        s.r(SEC)
        seqs.append(s)

    # A load (the control write clearing W) at a known cycle, then one read
    # at load+k: the next second must come at exactly load+T.
    for skew in (0, 1, T // 2, T - 1):
        for k in (2, T - 1, T, T + 1, 2 * T - 1, 2 * T):   # 2: the earliest
            s = Seq("phase after a load at skew %d: sec at load+%d"
                    % (skew, k), "rtc", exact=True)
            s.at(3 * T + skew)
            setrtc(s, 1993, 5, 17, 8, 30, 15)
            load = s.acc[-1][0]
            s.t = load + k
            s.r(SEC)
            seqs.append(s)

    s = Seq("freeze with R across seconds", "rtc")
    s.at(T - 20)
    s.w(CTL, 0x40)
    for c in (T - 10, T + 10, 3 * T):
        s.at(c)
        read_all(s)
    s.w(CTL, 0x00)
    read_all(s)
    s.at(4 * T)
    rtctime(s)
    seqs.append(s)

    s = Seq("held set visible while W is set; unwritten fields keep the "
            "snapshot", "rtc")
    s.at(T + 7)
    s.w(CTL, 0x80)
    read_all(s)
    s.w(MIN, 0x42)
    s.w(HOUR, 0x07)
    read_all(s)
    s.at(5 * T)
    read_all(s)
    s.w(CTL, 0x00)
    read_all(s)
    s.at(7 * T)
    read_all(s)
    seqs.append(s)

    s = Seq("W cleared with R still set loads and unfreezes", "rtc")
    s.at(2 * T + 3)
    s.w(CTL, 0xC0)
    s.w(YEAR, 0x88)
    s.w(MON, 0x07)
    s.w(MDAY, 0x04)
    s.w(CTL, 0x40)
    read_all(s)
    s.at(4 * T)
    read_all(s)
    s.w(CTL, 0x40)                      # R already set: no new snapshot
    s.at(6 * T)
    read_all(s)
    s.w(CTL, 0x00)
    read_all(s)
    seqs.append(s)

    s = Seq("R then W without a new snapshot, then W cleared", "rtc")
    s.at(T + 1)
    s.w(CTL, 0x40)
    s.at(3 * T)
    s.w(CTL, 0xC0)                      # snapshot stays the one at T+1
    read_all(s)
    s.w(SEC, 0x30)
    s.w(CTL, 0x40)
    read_all(s)
    s.at(6 * T)
    read_all(s)
    seqs.append(s)

    s = Seq("control S and calibration bits are stored", "rtc")
    s.w(CTL, 0x25)
    read_all(s)
    s.w(CTL, 0x3F)
    read_all(s)
    s.w(CTL, 0x00)
    read_all(s)
    seqs.append(s)

    s = Seq("kernel time-of-day: setrtc then rtctime twice", "rtc")
    s.at(T // 3)
    setrtc(s, 1993, 1, 3, 12, 0, 48)
    s.at(T + T // 2)
    rtctime(s)
    rtctime(s)
    seqs.append(s)

    rolls = [
        ((1993, 1, 3, 12, 0, 58), "minute"),
        ((1993, 1, 3, 12, 59, 58), "hour"),
        ((1993, 1, 3, 23, 59, 58), "day"),
        ((1993, 1, 31, 23, 59, 58), "Jan 31"),
        ((1993, 4, 30, 23, 59, 58), "Apr 30"),
        ((1993, 6, 30, 23, 59, 58), "Jun 30"),
        ((1993, 9, 30, 23, 59, 58), "Sep 30"),
        ((1993, 11, 30, 23, 59, 58), "Nov 30"),
        ((1993, 2, 28, 23, 59, 58), "Feb 28 1993"),
        ((1996, 2, 28, 23, 59, 58), "Feb 28 1996"),
        ((1996, 2, 29, 23, 59, 58), "Feb 29 1996"),
        ((2000, 2, 28, 23, 59, 58), "Feb 28 2000"),
        ((2000, 2, 29, 23, 59, 58), "Feb 29 2000"),
        ((1970, 1, 1, 0, 0, 0), "epoch"),
        ((1999, 12, 31, 23, 59, 58), "1999 -> 2000"),
        ((2069, 12, 31, 23, 59, 58), "2069 -> (19)70"),
        ((1993, 12, 31, 23, 59, 58), "Dec 31"),
        ((1993, 7, 31, 23, 59, 58), "Jul 31"),
        ((1993, 8, 31, 23, 59, 58), "Aug 31"),
    ]
    for when, name in rolls:
        s = Seq("rollover " + name, "rtc")
        s.at(T // 4)
        setrtc(s, *when)
        load = s.acc[-1][0]
        for k in (1, T - 1, T, 2 * T - 1, 2 * T, 3 * T):
            s.at(load + k)
            read_all(s)
        seqs.append(s)

    rnd = random.Random(0x1993)
    s = Seq("300 random dates 1970..2069, wday after each load", "rtc")
    for _ in range(300):
        y = rnd.randint(1970, 2069)
        mo = rnd.randint(1, 12)
        dim = [31, 29 if y % 4 == 0 else 28, 31, 30, 31, 30, 31, 31, 30,
               31, 30, 31][mo - 1]
        setrtc(s, y, mo, rnd.randint(1, dim), rnd.randint(0, 23),
               rnd.randint(0, 59), rnd.randint(0, 59))
        read_all(s)
    seqs.append(s)

    s = Seq("NVRAM: romboot Env at 0, key.c Nvrsafe at 1924, all 2040",
            "rtc")
    s.gapc = 3
    env = bytearray(4 + 4 + 11 * 64)
    env[0] = 5
    for i, (n, v) in enumerate((("sysname", "hobbit"), ("station", "99"),
                                ("bootfile", "/hobbit/9cpu"),
                                ("bootmode", "d"),
                                ("fs", "incon!nj/astro/Nfs"))):
        base = 8 + 64 * i
        env[base:base + len(n)] = n.encode()
        env[base + 16:base + 16 + len(v)] = v.encode()
    for i, b in enumerate(env):
        s.w(4 * i, 0xABCDEF00 | b)      # junk in bits 31:8 is ignored
    # auth.h Nvrsafe: machkey[DESKEYLEN 7], machsum, authkey[7], authsum,
    # config[CONFIGLEN 14], configsum = 31 bytes at 1024+900 (key.c)
    safe = bytes(rnd.randrange(256) for _ in range(7 + 1 + 7 + 1 + 14 + 1))
    for i, b in enumerate(safe):
        s.w(4 * (1924 + i), b)
    s.w(4 * 2039, 0x5A)
    for i in range(2040):
        s.r(4 * i + (i & 3))            # byte offsets within the word too
    seqs.append(s)
    return seqs


def rtc_faults():
    T = TICKS_PER_SEC
    seqs = []
    s = Seq("fault: clock register written without RTCWRITE", "rtc")
    s.r(SEC)
    s.w(SEC, 0x12)
    seqs.append(s)

    s = Seq("fault: clock register written with R only", "rtc")
    s.w(CTL, 0x40)
    s.w(MIN, 0x12)
    seqs.append(s)

    s = Seq("fault: W cleared with nothing held", "rtc")
    s.w(CTL, 0x80)
    s.w(CTL, 0x40)          # load, R left set, held dropped
    s.w(CTL, 0xC0)          # R was set: no snapshot
    s.w(CTL, 0x00)          # the model has no held set
    seqs.append(s)

    s = Seq("fault: a load of month 0x13", "rtc")
    s.at(T)
    s.w(CTL, 0x80)
    s.w(MON, 0x13)
    s.r(MON)
    s.w(CTL, 0x00)
    seqs.append(s)

    s = Seq("RTL-only fault: a load of Feb 30", "rtc",
            expect_rtl_fault=(4, RTC_BAD_LOAD))
    s.w(CTL, 0x80)
    s.w(MON, 0x02)
    s.w(MDAY, 0x30)
    s.r(MDAY)
    s.w(CTL, 0x00)
    seqs.append(s)

    s = Seq("RTL-only fault: write on byte lane 1 only", "rtc",
            expect_rtl_fault=(0, RTC_LANE))
    s.w(4 * 10, 0x1200, be=2)
    seqs.append(s)
    return seqs


def iic_master(s, slave):
    """deviic.c master(): S0 = slave, S1 = PIN|ESO|STA, iicack()."""
    s.w(S0, slave)
    s.w(S1, 0xC4)
    s.r(S1)
    s.r(S1)


def iic_release(s):
    s.w(S1, 0xC3)
    s.r(S1)


def iic_reset(s):
    s.w(S0, 0x10)
    s.w(S1, 0x20)
    s.w(S0, 0x18)
    s.w(S1, 0x40)
    s.r(S1)


def iic_sequences():
    seqs = []
    s = Seq("ledputbyte x3 after iicreset", "iic")
    iic_reset(s)
    for c in (0x01, 0xFE, 0x55):
        iic_master(s, 0x40)
        s.w(S0, c)
        s.r(S1)
        s.r(S1)
        iic_release(s)
    seqs.append(s)

    s = Seq("a slave that does not acknowledge (0x90), then release", "iic")
    iic_reset(s)
    iic_master(s, 0x90)
    s.w(S0, 0x33)
    s.r(S1)
    iic_release(s)
    s.r(S1)
    seqs.append(s)

    for start, n in ((5, 12), (250, 12), (0, 40)):
        s = Seq("EEPROM read from %d, %d bytes" % (start, n), "iic")
        iic_reset(s)
        iic_master(s, 0xA4)
        s.w(S0, start)
        s.r(S1)
        s.w(S0, 0xA5)
        s.r(S1)
        s.w(S1, 0xC5)
        s.r(S1)
        s.r(S1)
        s.r(S0)                         # the dummy read
        for _ in range(n):
            s.r(S1)
            s.r(S0)
        s.w(S1, 0xC0)
        s.r(S1)
        s.r(S0)
        iic_release(s)
        seqs.append(s)

    s = Seq("PIN set and STA|STO together", "iic")
    iic_reset(s)
    s.w(S1, 0xC0)
    s.r(S1)
    s.w(S1, 0x46)                       # STA|STO: neither branch
    s.r(S1)
    s.w(S1, 0x00)                       # ESO off: ctl stored only
    s.r(S1)
    seqs.append(s)
    return seqs


def iic_faults():
    seqs = []
    s = Seq("fault: S0 read with ESO off", "iic")
    s.w(S0, 0x10)
    s.r(S0)
    seqs.append(s)

    s = Seq("fault: S0 write selecting S3 (interrupt vector)", "iic")
    s.w(S1, 0x10)
    s.w(S0, 0x00)
    seqs.append(s)

    s = Seq("fault: S0 write selecting ES2|ES1", "iic")
    s.w(S1, 0x30)
    s.w(S0, 0x00)
    seqs.append(s)

    s = Seq("fault: read of offset 8 (outside S0/S1)", "iic")
    s.r(8)
    seqs.append(s)

    s = Seq("fault: write of offset 0xc", "iic")
    s.w(0xC, 0x00)
    seqs.append(s)

    s = Seq("RTL-only fault: write on byte lane 2 only", "iic",
            expect_rtl_fault=(0, IIC_LANE))
    s.w(S1, 0x400000, be=4)
    seqs.append(s)
    return seqs


# ---- comparison --------------------------------------------------------------

def compare(seq, cov, verbose):
    top = "mkRtc" if seq.dev == "rtc" else "mkIic"
    rows = run_rtl(top, seq.acc)
    model = RtcModel() if seq.dev == "rtc" else IicModel()
    errs = []
    for i, ((_, op, addr, data, be), (acc, rdata, fault, led, ledn)) in \
            enumerate(zip(seq.acc, rows)):
        want, exc = model.access(acc, op, addr, data, be)
        what = "#%d %s %s+%x" % (i, op, seq.dev, addr)
        if seq.exact and acc != seq.acc[i][0]:
            errs.append("%s: taken at cycle %d, not at its target %d"
                        % (what, acc, seq.acc[i][0]))
        if exc is not None:
            if not seq.name.startswith("fault:") or i != len(seq.acc) - 1:
                errs.append("%s: the model refused an access the sequence "
                            "does not expect to fault: %s (%s)"
                            % (what, exc[0], exc[1]))
            if fault != exc[2]:
                errs.append("%s: model %s (%s), RTL fault %d (want %d)"
                            % (what, exc[0], exc[1], fault, exc[2]))
            cov["faults matched"] += fault == exc[2]
            break                       # a fault ends the sequence
        if seq.expect_rtl_fault and i == seq.expect_rtl_fault[0]:
            code = seq.expect_rtl_fault[1]
            if fault != code:
                errs.append("%s: RTL fault %d, want RTL-only fault %d"
                            % (what, fault, code))
            cov["RTL-only faults"] += fault == code
            break
        if fault:
            errs.append("%s: RTL fault %d, the model accepted it"
                        % (what, fault))
            break
        if op == "R":
            if rdata != want:
                errs.append("%s at cycle %d: RTL %08x, model %08x"
                            % (what, acc, rdata, want))
            if seq.dev == "rtc":
                key = REGNAME.get(addr & ~3, "nvram")
            else:
                key = "S1" if addr & 4 else "S0"
            cov["%s %s reads" % (seq.dev, key)] += 1
            if seq.recorded is not None and seq.dev == "iic":
                if rdata != seq.recorded[i]:
                    errs.append("%s: RTL %08x, recorded in the run %08x"
                                % (what, rdata, seq.recorded[i]))
                cov["iic reads equal to the recorded run"] += 1
            if (seq.recorded is not None and seq.dev == "rtc"
                    and REGNAME.get(addr & ~3, "nvram") in
                    ("nvram", "control")):
                if rdata != seq.recorded[i]:
                    errs.append("%s: RTL %08x, recorded in the run %08x"
                                % (what, rdata, seq.recorded[i]))
                cov["rtc untimed reads equal to the recorded run"] += 1
        else:
            cov["%s writes" % seq.dev] += 1
        if seq.dev == "iic":
            mled = model.m.led
            if ledn != len(mled) % 256 or (mled and led != mled[-1]):
                errs.append("%s: LED latch RTL %02x/%d, model %r"
                            % (what, led, ledn, mled[-4:]))
    else:
        if seq.name.startswith("fault:"):
            errs.append("%s: the model never refused" % seq.name)
        if seq.expect_rtl_fault:
            errs.append("%s: the expected RTL-only fault never came"
                        % seq.name)
    if verbose or errs:
        print("%-4s %-66s %5d accesses  %s"
              % (seq.dev, seq.name, len(seq.acc),
                 "ok" if not errs else "FAIL"))
    for e in errs[:8]:
        print("     " + e)
    if len(errs) > 8:
        print("     ... %d more" % (len(errs) - 8))
    return not errs


def main():
    verbose = "-v" in sys.argv
    if not shutil.which("verilator"):
        raise SystemExit("verilator not found")
    build()
    import collections
    cov = collections.Counter()
    seqs = [load_trace(os.path.join(HERE, "rtc_join.trace"), "rtc"),
            load_trace(os.path.join(HERE, "iic_join.trace"), "iic")]
    seqs += rtc_sequences() + rtc_faults() + iic_sequences() + iic_faults()
    ok = 0
    for s in seqs:
        ok += compare(s, cov, verbose)
    print()
    for k in sorted(cov):
        print("  %-48s %7d" % (k, cov[k]))
    print("\n%d of %d sequences agree" % (ok, len(seqs)))
    sys.exit(0 if ok == len(seqs) else 1)


if __name__ == "__main__":
    main()
