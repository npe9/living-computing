#!/usr/bin/env python3
"""Capture every access the shipped kernel makes to the timekeeper
(IONAK+0x2000..0x3FFF) and the IIC controller (IOBASE+0x80..0x87) during
the replayed join of tests/test_p9boot.py JoinReplayTest: s9term booted
on the reference model, BOOTP/IL to the recorded 1e server, the time set
from the server ('time...'), init, rc and `echo hello`.

Writes two trace files (format in rtc.md "Trace format"):
    rtc_join.trace   every access to the timekeeper
    iic_join.trace   every access to the PCF8584

    python3 hobbit/fpga/dev/rtc_iic_capture.py [OUTDIR]     (~3 min)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HOBBIT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HOBBIT, "tools"))
sys.path.insert(0, os.path.join(HOBBIT, "sem"))

import p9boot  # noqa: E402

S9TERM = os.path.join(HOBBIT, "tools", "plan9-1e", "hobbit", "s9term")
JOIN_PCAP = os.path.join(HOBBIT, "tests", "net", "join_echo.pcap")
STEPS_ECHO = 715866474          # tests/test_p9boot.py STEPS["echo"]


class Tap:
    """Delegates to a device model and records (cycle, op, off, data,
    mask, result, function) for every access."""

    def __init__(self, dev, boot, log):
        self.dev, self.boot, self.log = dev, boot, log

    def _where(self):
        return self.boot.syms.func(self.boot.state.pc)[0]

    def read(self, off):
        v = self.dev.read(off)
        self.log.append((self.boot.cycles, "R", off, 0, 0, v, self._where()))
        return v

    def write(self, off, data, mask):
        self.dev.write(off, data, mask)
        self.log.append((self.boot.cycles, "W", off, data, mask, None,
                         self._where()))


def tap(boot, dev, log):
    for i, (lo, hi, d) in enumerate(boot.board.devices):
        if d is dev:
            boot.board.devices[i] = (lo, hi, Tap(dev, boot, log))
            return
    raise SystemExit("device not on the board")


def write_trace(path, log, title):
    with open(path, "w") as f:
        f.write("# %s\n" % title)
        f.write("# captured by rtc_iic_capture.py from the JoinReplayTest "
                "run of s9term (tests/test_p9boot.py)\n")
        f.write("# cycle op off data mask result function  "
                "(cycle = model cycles at %d Hz)\n" % p9boot.CPU_HZ)
        for c, op, off, data, mask, res, fn in log:
            f.write("%d %s %04x %08x %x %s %s\n" % (
                c, op, off, data, mask,
                "-" if res is None else "%08x" % res, fn))


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else HERE
    boot = p9boot.Boot(S9TERM)
    rtclog, iiclog = [], []
    tap(boot, boot.rtc, rtclog)
    tap(boot, boot.iic, iiclog)
    boot.script = [(b"il]: ", b"\r"), (b"user[none]: ", b"\r"),
                   (b"% ", b"echo hello\r")]
    replay = p9boot.Replay(JOIN_PCAP, p9boot.EEPROM_EA)
    boot.attach(p9boot.Wire(boot.sonic.clock, replay=replay))
    boot.until = b"% echo hello\nhello\n% "
    status = boot.run(STEPS_ECHO + 1000000)
    print(status)
    if boot.steps != STEPS_ECHO or replay.mismatch is not None:
        raise SystemExit("the run did not reproduce JoinReplayTest "
                         "(steps %d, mismatch %r)" % (boot.steps,
                                                      replay.mismatch))
    write_trace(os.path.join(out, "rtc_join.trace"), rtclog,
                "MK48T02 timekeeper accesses, IONAK+0x2000 offsets")
    write_trace(os.path.join(out, "iic_join.trace"), iiclog,
                "PCF8584 accesses, IOBASE+0x80 offsets")
    print("rtc: %d accesses, iic: %d accesses, rtc sets %r"
          % (len(rtclog), len(iiclog), boot.rtc.sets))


if __name__ == "__main__":
    main()
