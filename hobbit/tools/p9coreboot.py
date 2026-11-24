#!/usr/bin/env python3
"""Record the reference boot of s9term for replay on the Bluespec core.

`tools/p9boot.py` boots the shipped kernel image on the reference model
(`sem/hobbit_sem.py` with a `System`).  This file runs that same boot,
unchanged -- it imports `p9boot` and wraps three calls from the outside
(`hobbit_sem.step`, `hobbit_sem.take_interrupt` and the board's `read`)
-- and writes what the Bluespec core needs to execute the same boot
without a second device model (docs/p9boot.md, "The boot on the core"):

    ref.hri     the retirement record of every instruction, in order
    console     the bytes the kernel wrote to the console (Quart channel 0)
    boot.rec    the replay: the boot memory, the start PC, every device
                register read the kernel made (by record number) and
                every interrupt the board raised (by record number)

The replay record, one line each, hex fields:

    M addr word        an initial word of physical memory (the loaded
                       image and the ROM's hand-off page; p9boot.py)
    S pc               the entry
    D n pa value       the n-th record's instruction read `value` from
                       the device register at physical `pa`
    W n pa value mask  the n-th record's instruction wrote a device
                       register (checked, and the console is taken from
                       these on the core side)
    I n level pc       after record n the board raised interrupt `level`
                       and the reference took it; `pc` is the
                       instruction that had not executed (p. 1-37)
    E n                the reference run stopped after record n

    python3 tools/p9coreboot.py record OUTDIR --max-steps N [--until TEXT]
        [--counter-period S]
    python3 tools/p9coreboot.py compare ref.hri core.log [--limit N]

`compare` streams both files and stops at the first record that differs
in any field but `cyc` (tools/p9trace_cmp.py's rule, without loading the
traces into memory: a boot is millions of records).
"""

import argparse
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import p9boot          # noqa: E402

hobbit_sem = p9boot.hobbit_sem
MASK32 = 0xFFFFFFFF
QUART_TX0 = 0xB000010C


class Recorder:
    """Wraps a p9boot.Boot from the outside and writes the replay."""

    def __init__(self, boot, outdir):
        self.boot = boot
        self.n = 0                      # records retired so far
        os.makedirs(outdir, exist_ok=True)
        self.hri = open(os.path.join(outdir, "ref.hri"), "w")
        self.rec = open(os.path.join(outdir, "boot.rec"), "w")
        # The reference's console: the bytes written to Quart channel 0's
        # transmit holding register (io.h Duart.txfifo), the same register
        # bsv/p9kern.c takes the core's console from.
        self.console = open(os.path.join(outdir, "console"), "wb")
        self.dev_reads = 0
        self.dev_writes = 0
        self.interrupts = 0
        board = boot.board
        for pa in sorted(board.ram):
            if board.ram[pa]:
                self.rec.write("M %x %x\n" % (pa, board.ram[pa]))
        self.rec.write("S %x\n" % boot.state.pc)
        self._read = board.read
        self._write = board.write
        board.read = self.read
        board.write = self.write
        self._step = hobbit_sem.step
        self._take = hobbit_sem.take_interrupt
        hobbit_sem.step = self.step
        hobbit_sem.take_interrupt = self.take_interrupt

    def ram(self, pa):
        b = self.boot.board
        return b.ram_lo <= (pa & ~3 & MASK32) < b.ram_hi

    def read(self, pa):
        v = self._read(pa)
        if not self.ram(pa):
            self.dev_reads += 1
            self.rec.write("D %x %x %x\n" % (self.n + 1, pa & ~3 & MASK32,
                                             v & MASK32))
        return v

    def write(self, pa, data, mask):
        if not self.ram(pa):
            self.dev_writes += 1
            self.rec.write("W %x %x %x %x\n" % (self.n + 1, pa & ~3 & MASK32,
                                                data & MASK32, mask))
            if pa & ~3 & MASK32 == QUART_TX0:
                self.console.write(bytes([data & 0xFF]))
        return self._write(pa, data, mask)

    def step(self, st, *a, **k):
        rec, st = self._step(st, *a, **k)
        self.n += 1
        self.hri.write(rec.line() + "\n")
        return rec, st

    def take_interrupt(self, st, level, *a, **k):
        self.interrupts += 1
        self.rec.write("I %x %x %x\n" % (self.n, level, st.pc & MASK32))
        return self._take(st, level, *a, **k)

    def close(self):
        hobbit_sem.step = self._step
        hobbit_sem.take_interrupt = self._take
        self.rec.write("E %x\n" % self.n)
        self.rec.close()
        self.hri.close()
        self.console.close()


def record(args):
    boot = p9boot.Boot(args.image)
    # The idle skip (p9boot CHOICES['idle-skip']) retires idle-loop laps
    # without executing them; the core executes every one, so the recording
    # must too.
    boot.idle_skip = False
    if args.counter_period is not None:
        boot.quart.period_override = args.counter_period
    if args.until:
        boot.until = args.until.encode("latin-1").decode(
            "unicode_escape").encode("latin-1")
    r = Recorder(boot, args.outdir)
    try:
        status = boot.run(args.max_steps)
    finally:
        r.close()
    print("p9coreboot: %s" % status)
    print("p9coreboot: %d records, %d device reads, %d device writes, "
          "%d interrupts" % (r.n, r.dev_reads, r.dev_writes, r.interrupts))
    for stepno, name in boot.reached:
        print("  %10d  %s" % (stepno, name))
    with open(os.path.join(args.outdir, "functions"), "w") as f:
        for stepno, name in boot.reached:
            f.write("%d %s\n" % (stepno, name))
    return 0


LINE = re.compile(
    r"^HRI pc=([0-9a-f]+) insn=([0-9a-f]+) sp=([0-9a-f]+)>([0-9a-f]+) "
    r"msp=([0-9a-f]+)>([0-9a-f]+) we=(\d) addr=([0-9a-f]+) "
    r"data=([0-9a-f]+) mask=([0-9a-f]+) trap=(\d) cyc=(\d+)")
FIELDS = ("pc", "insn", "sp_before", "sp_after", "msp_before", "msp_after",
          "we", "addr", "data", "mask", "trap")


def stream(path):
    with open(path, errors="replace") as f:
        for raw in f:
            m = LINE.match(raw)
            if m:
                g = m.groups()
                yield tuple(int(x, 16) for x in g[:11]), int(g[11]), \
                    raw.rstrip("\n")


def compare_streams(ref_path, dut_path, limit=None, functions=None):
    """(ok, n, text): n records compared."""
    names = []
    if functions and os.path.exists(functions):
        with open(functions) as f:
            for line in f:
                s, name = line.rstrip("\n").split(None, 1)
                names.append((int(s), name))
    ref = stream(ref_path)
    dut = stream(dut_path)
    n = 0
    same_cyc = 0
    last = []
    for r in ref:
        if limit is not None and n >= limit:
            break
        d = next(dut, None)
        if d is None:
            reached = [nm for s, nm in names if s <= n]
            return False, n, (
                "FAIL: the core retired %d records; the reference has more. "
                "Next expected:\n  ref  %s\n  last function reached: %s"
                % (n, r[2], reached[-1] if reached else "?"))
        n += 1
        if d[0] != r[0]:
            bad = [FIELDS[k] for k in range(11) if d[0][k] != r[0][k]]
            reached = [nm for s, nm in names if s < n]
            lines = ["FAIL at record %d: %s differ (last function reached "
                     "before it: %s)" % (n, ", ".join(bad),
                                         reached[-1] if reached else "?")]
            for x in last:
                lines.append("  both %s" % x)
            lines.append("  ref  %s" % r[2])
            lines.append("  core %s" % d[2])
            return False, n, "\n".join(lines)
        if d[1] == r[1]:
            same_cyc += 1
        last = (last + [r[2]])[-4:]
    return True, n, ("MATCH: %d records agree in every field but cyc "
                     "(%d also agree in cyc)" % (n, same_cyc))


def compare(args):
    ok, n, text = compare_streams(args.ref, args.dut, args.limit,
                                  args.functions)
    print(text)
    return 0 if ok else 1


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record")
    r.add_argument("outdir")
    r.add_argument("--image", default=str(HERE / "plan9-1e" / "hobbit" /
                                          "s9term"))
    r.add_argument("--max-steps", type=int, default=125300)
    r.add_argument("--until", metavar="TEXT")
    r.add_argument("--counter-period", type=float, metavar="SECONDS")
    c = sub.add_parser("compare")
    c.add_argument("ref")
    c.add_argument("dut")
    c.add_argument("--limit", type=int)
    c.add_argument("--functions", help="the `functions` file record wrote")
    args = ap.parse_args(argv)
    return record(args) if args.cmd == "record" else compare(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
