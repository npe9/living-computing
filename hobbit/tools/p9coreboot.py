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
    R n pa value mask  a device wrote RAM (SONIC's descriptors and
                       buffers): the word at physical `pa`, lanes `mask`
                       (bit 3 = bits 31:24), once record n has retired.
                       A write made while the n-th instruction executes
                       (a register write that starts a transmit, say) is
                       tagged n; one made between instructions (a frame
                       arriving, a console tap) is tagged with the record
                       before it.  The core's RAM is the testbench's, so
                       the testbench makes the write at that boundary.
    E n                the reference run stopped after record n

    python3 tools/p9coreboot.py record OUTDIR --max-steps N [--until TEXT]
        [--counter-period S] [--type TEXT=REPLY ...] [--think S]
        [--ether-replay PCAP] [--zstd]
    python3 tools/p9coreboot.py compare ref.hri[.zst] core.log|- [--limit N]
        [--side FILE]

`compare` streams both files and stops at the first record that differs
in any field but `cyc` (tools/p9trace_cmp.py's rule, without loading the
traces into memory: a boot is millions of records).  With `-` it reads
the simulator's output from a pipe and stops it at the first difference;
`--side` keeps the output's other lines (the testbench's P9KERN report).
`--zstd` writes ref.hri.zst instead of ref.hri: at ~127 bytes a record
an uncompressed trace of the whole join (618M records) would be ~80 GB.
--type, --think and --ether-replay are p9boot's (the join to rc's
prompt, docs/p9boot.md "Commands at rc's prompt").
"""

import argparse
import os
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import p9boot          # noqa: E402

hobbit_sem = p9boot.hobbit_sem
MASK32 = 0xFFFFFFFF
QUART_TX0 = 0xB000010C


class Recorder:
    """Wraps a p9boot.Boot from the outside and writes the replay."""

    def __init__(self, boot, outdir, zstd=False):
        self.boot = boot
        self.n = 0                      # records retired so far
        os.makedirs(outdir, exist_ok=True)
        self.zproc = None
        if zstd:
            self.zproc = subprocess.Popen(
                ["zstd", "-q", "-f", "-3", "-T2", "-o",
                 os.path.join(outdir, "ref.hri.zst")],
                stdin=subprocess.PIPE)
            self.hri = open(self.zproc.stdin.fileno(), "w", closefd=False,
                            buffering=1 << 20)
        else:
            self.hri = open(os.path.join(outdir, "ref.hri"), "w")
        # Device writes into RAM (the `R` lines): a RAM write made inside a
        # device's register access, or between instructions, is a device's.
        self.in_step = False
        self.dev_depth = 0
        self.dma_writes = 0
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
        if self.ram(pa):
            return self._read(pa)
        self.dev_depth += 1
        try:
            v = self._read(pa)
        finally:
            self.dev_depth -= 1
        if True:
            self.dev_reads += 1
            self.rec.write("D %x %x %x\n" % (self.n + 1, pa & ~3 & MASK32,
                                             v & MASK32))
        return v

    def write(self, pa, data, mask):
        if self.ram(pa):
            if self.dev_depth or not self.in_step:
                self.dma_writes += 1
                # made before record n+1 retires; inside a device call in
                # a step it is that step's (n+1), between steps after n
                self.rec.write("R %x %x %x %x\n" % (
                    self.n + 1 if self.in_step else self.n,
                    pa & ~3 & MASK32, data & MASK32, mask))
            return self._write(pa, data, mask)
        self.dev_writes += 1
        self.rec.write("W %x %x %x %x\n" % (self.n + 1, pa & ~3 & MASK32,
                                            data & MASK32, mask))
        if pa & ~3 & MASK32 == QUART_TX0:
            self.console.write(bytes([data & 0xFF]))
        self.dev_depth += 1
        try:
            return self._write(pa, data, mask)
        finally:
            self.dev_depth -= 1

    def step(self, st, *a, **k):
        self.in_step = True
        try:
            rec, st = self._step(st, *a, **k)
        finally:
            self.in_step = False
        self.n += 1
        self.hri.write(rec.line() + "\n")
        return rec, st

    def take_interrupt(self, st, level, *a, **k):
        # The interrupt sequence's own frame writes are the CPU's (the
        # core makes them), not a device's: counted as a step.
        self.interrupts += 1
        self.rec.write("I %x %x %x\n" % (self.n, level, st.pc & MASK32))
        self.in_step = True
        try:
            return self._take(st, level, *a, **k)
        finally:
            self.in_step = False

    def close(self):
        hobbit_sem.step = self._step
        hobbit_sem.take_interrupt = self._take
        self.rec.write("E %x\n" % self.n)
        self.rec.close()
        self.hri.close()
        if self.zproc is not None:
            self.zproc.stdin.close()
            self.zproc.wait()
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
        boot.until = p9boot.unescape(args.until)
    for item in args.type:
        wait, sep, reply = item.partition("=")
        if not sep:
            raise SystemExit("--type wants TEXT=REPLY, not %r" % item)
        boot.script.append((p9boot.unescape(wait), p9boot.unescape(reply)))
    boot.think = args.think
    if args.ether_replay:
        boot.attach(p9boot.Wire(boot.sonic.clock, replay=p9boot.Replay(
            args.ether_replay, p9boot.EEPROM_EA)))
    r = Recorder(boot, args.outdir, zstd=args.zstd)
    try:
        status = boot.run(args.max_steps)
    finally:
        r.close()
    print("p9coreboot: %s" % status)
    print("p9coreboot: %d records, %d device reads, %d device writes, "
          "%d interrupts, %d device writes into RAM"
          % (r.n, r.dev_reads, r.dev_writes, r.interrupts, r.dma_writes))
    w = boot.wire
    if w is not None and w.replay is not None and w.replay.mismatch:
        print("p9coreboot: replay: model frame %d differs from the "
              "recording" % w.replay.mismatch[0])
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


def parse(raw):
    m = LINE.match(raw)
    g = m.groups()
    return tuple(int(x, 16) for x in g[:11]), int(g[11])


def open_text(path):
    """A trace: a file, a .zst file (through zstd -dc), or `-`."""
    if path == "-":
        return sys.stdin
    if path.endswith(".zst"):
        p = subprocess.Popen(["zstd", "-dcq", path], stdout=subprocess.PIPE)
        return open(p.stdout.fileno(), errors="replace", closefd=False,
                    buffering=1 << 20)
    return open(path, errors="replace", buffering=1 << 20)


def stream(path, side=None):
    """(line without cyc, cyc text, line) for each HRI line; other lines
    go to `side`."""
    f = open_text(path)
    for raw in f:
        if raw.startswith("HRI "):
            line = raw.rstrip("\n")
            k = line.rfind(" cyc=")
            yield line[:k], line[k + 5:], line
        elif side is not None:
            side.write(raw)
            side.flush()


def compare_streams(ref_path, dut_path, limit=None, functions=None,
                    side=None):
    """(ok, n, text): n records compared.  Equal text (but cyc) is a
    match without parsing; otherwise the fields are compared, so a PC
    printed in a different width still matches."""
    names = []
    if functions and os.path.exists(functions):
        with open(functions) as f:
            for line in f:
                s, name = line.rstrip("\n").split(None, 1)
                names.append((int(s), name))
    ref = stream(ref_path)
    dut = stream(dut_path, side)
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
        if d[0] != r[0] and parse(d[2])[0] != parse(r[2])[0]:
            pd, pr = parse(d[2])[0], parse(r[2])[0]
            bad = [FIELDS[k] for k in range(11) if pd[k] != pr[k]]
            reached = [nm for s, nm in names if s < n]
            lines = ["FAIL at record %d: %s differ (last function reached "
                     "before it: %s)" % (n, ", ".join(bad),
                                         reached[-1] if reached else "?")]
            for x in last:
                lines.append("  both %s" % x)
            lines.append("  ref  %s" % r[2])
            lines.append("  core %s" % d[2])
            for _k, nxt in zip(range(3), ref):
                lines.append("  ref+ %s" % nxt[2])
            return False, n, "\n".join(lines)
        if d[1] == r[1]:
            same_cyc += 1
        last = (last + [r[2]])[-4:]
    # The rest of the simulator's output (its drained records and its
    # report) still goes to `side`.
    for _ in dut:
        pass
    return True, n, ("MATCH: %d records agree in every field but cyc "
                     "(%d also agree in cyc)" % (n, same_cyc))


def compare(args):
    side = open(args.side, "w") if args.side else None
    ok, n, text = compare_streams(args.ref, args.dut, args.limit,
                                  args.functions, side)
    if side is not None:
        side.close()
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
    r.add_argument("--type", action="append", default=[],
                   metavar="TEXT=REPLY")
    r.add_argument("--think", type=float, default=0.0, metavar="SECONDS")
    r.add_argument("--ether-replay", metavar="PCAP")
    r.add_argument("--zstd", action="store_true")
    c = sub.add_parser("compare")
    c.add_argument("ref")
    c.add_argument("dut")
    c.add_argument("--limit", type=int)
    c.add_argument("--functions", help="the `functions` file record wrote")
    c.add_argument("--side", help="write the DUT's non-HRI lines here")
    args = ap.parse_args(argv)
    return record(args) if args.cmd == "record" else compare(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
