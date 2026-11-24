#!/usr/bin/env python3
"""Register-access traces for the Quart and interrupt-path RTL.

Two jobs, one trace format:

  capture  Run tools/p9boot.py (the reference model booting s9term) with
           recorders on the Quart, Irq, IOCTL and incon devices, and write
           every access the kernel made, in order, with the value the model
           answered.  p9boot.py is not edited: its classes are wrapped from
           here before main() builds the board.

  vectors  Replay a trace (captured, or written by hand under tests/) into
           a FRESH set of the Python models (p9boot.Quart, Irq, Register,
           Latch) and write the hex vector file the Bluesim testbench
           (QuartReplayTb.bsv) replays into the RTL.  Every read value, the
           fail-loud outcome of every access (the model's Stop/BusError),
           the Quart's irq and IL6 after every access, and every byte the
           Quart transmits are expectations in the vector file.  For a
           captured trace the fresh model must also reproduce the captured
           read values (a self-check of the replay itself).

Trace format, one record a line, '#' comments:

  a DEV r OFF [= VAL|ERR|RTLERR]          read  (DEV: quart irq ioctl incon)
  a DEV w OFF DATA MASK [= ok|ERR|RTLERR] write (MASK bit 3 = bits 31:24)

  ERR: the Python model stops the run (Stop / BusError) and the RTL must
  fault.  RTLERR: the model accepts the access but the RTL does not
  implement what it asks for (HobbitQuart.bsv, "Faults"), so the RTL faults
  while the model must answer normally: the divergence is tested, not
  hidden.
  t D N        the counter of DUART D expired N times since the last record
  x CH BYTE    a byte reached channel CH's receive FIFO
  e EXT        the other interrupt requests (Irq status bits, Quart's bit 1
               excluded): sonic, scsi ... as the board had them
  s [QIRQ IL6] sample the Quart irq and IL6 (expected values optional)

Time.  The Python models are lazy in model time; the RTL runs on clocks.
The replay is event-driven: the model's clock only moves at a `t` record,
to the instant the counter expires, and an `x` record puts a byte in the
FIFO at the current instant.  The testbench waits for the RTL's own
counter to expire the same number of times (it checks the period in
clocks separately) and drives the byte in on the pin or stream.  So both
sides see the same events between the same two accesses; what the RTL
does in between (transmit on the pin) is drained before each access, the
condition under which the model's zero-time transmitter is exact.

Vector file: one 128-bit hex word a line (QuartReplayTb.bsv's layout):
  [127:124] op   1 access, 2 tick, 3 rx, 4 tx byte, 5 ext, 6 sample, 0 end
  [123:120] dev  0 quart, 1 irq, 2 ioctl, 3 incon
  [119]     write   [118:115] mask   [114:103] offset
  [102:71]  wdata   [70:39] expected read value
  [38] expected fault  [37] expected Quart irq  [36] expected IL6
  [35:32] channel / duart   [31:16] count (tick)   [15:0] byte / ext
"""

import argparse
import collections
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
TOOLS = HERE.parents[2] / "tools"
sys.path.insert(0, str(TOOLS))
import p9boot  # noqa: E402
import hobbit_sem  # noqa: E402  (p9boot put sem/ on the path)

DEVS = {"quart": 0, "irq": 1, "ioctl": 2, "incon": 3}
FAILS = (p9boot.Stop, hobbit_sem.BusError)


# --------------------------------------------------------------------- capture
class Recorder:
    def __init__(self, out):
        self.out = out
        self.quart = None
        self.irq = None
        self.inside = 0         # nesting: only the outermost access logs
        self.ext = 0
        self.counts = collections.Counter()

    def line(self, s):
        self.out.write(s + "\n")

    def ext_now(self):
        if self.irq is None:
            return 0
        st = 0
        for n, f in self.irq.sources.items():
            if n != 1 and f():
                st |= 1 << n
        return st

    def pre(self):
        e = self.ext_now()
        if e != self.ext:
            self.ext = e
            self.line("e %x" % e)

    def post(self):
        q = 1 if (self.quart is not None and self.quart.irq()) else 0
        self.pre()
        il6 = 1 if (self.irq is not None and self.irq.asserted()) else 0
        self.line("s %d %d" % (q, il6))


def install(rec):
    """Wrap the device classes; p9boot.main() then builds them."""
    Q, I, R, L = p9boot.Quart, p9boot.Irq, p9boot.Register, p9boot.Latch

    def accessor(cls, name, which):
        orig_r, orig_w = cls.read, cls.write

        def read(self, off):
            dev = which(self)
            if dev is None or rec.inside:
                return orig_r(self, off)
            rec.pre()
            rec.inside += 1
            try:
                v = orig_r(self, off)
            except FAILS:
                rec.inside -= 1
                rec.line("a %s r %x = ERR" % (dev, off))
                raise
            rec.inside -= 1
            rec.line("a %s r %x = %x" % (dev, off, v))
            rec.counts[(dev, "r", off)] += 1
            rec.post()
            return v

        def write(self, off, data, mask):
            dev = which(self)
            if dev is None or rec.inside:
                return orig_w(self, off, data, mask)
            rec.pre()
            rec.inside += 1
            try:
                orig_w(self, off, data, mask)
            except FAILS:
                rec.inside -= 1
                rec.line("a %s w %x %x %x = ERR" % (dev, off, data, mask))
                raise
            rec.inside -= 1
            rec.line("a %s w %x %x %x = ok" % (dev, off, data, mask))
            rec.counts[(dev, "w", off)] += 1
            rec.post()

        cls.read, cls.write = read, write

    accessor(Q, "quart", lambda s: "quart")
    accessor(I, "irq", lambda s: "irq")
    accessor(R, "ioctl", lambda s: "ioctl" if s.name == "IOCTL" else None)
    accessor(L, "incon", lambda s: "incon" if s.name == "incon" else None)

    q_init, i_init = Q.__init__, I.__init__

    def qi(self, *a, **k):
        q_init(self, *a, **k)
        rec.quart = self

    def ii(self, *a, **k):
        i_init(self, *a, **k)
        rec.irq = self

    Q.__init__, I.__init__ = qi, ii

    tick = Q._tick

    def _tick(self, d):
        du = self.duarts[d]
        before = du["next_tick"]
        tick(self, d)
        after = du["next_tick"]
        if before is not None and after != before:
            n = int(round((after - before) / self._period(d)))
            rec.line("t %d %d" % (d, n))

    Q._tick = _tick

    rx = Q._rx

    def _rx(self, ch):
        port = self.ports[ch]
        before = port["received"]
        rx(self, ch)
        n = port["received"] - before
        if n:
            for b in list(port["fifo"])[-n:]:
                rec.line("x %d %x" % (ch, b))

    Q._rx = _rx


def capture(args):
    with open(args.trace, "w") as out:
        out.write("# captured by quart_trace.py capture from tools/p9boot.py"
                  " %s\n" % " ".join(args.p9boot))
        rec = Recorder(out)
        install(rec)
        rc = p9boot.main(args.p9boot)
        out.write("# end of capture\n")
    print("quart_trace: %d accesses captured" % sum(rec.counts.values()))
    for k, v in sorted(rec.counts.items()):
        print("  %-6s %s +0x%02x  %d" % (k[0], k[1], k[2], v))
    return rc


# --------------------------------------------------------------------- vectors
class Models:
    """A fresh board of the four devices, driven by the trace's events."""

    def __init__(self):
        self.now = 0.0
        self.quart = p9boot.Quart(25, lambda: self.now)
        self.irq = p9boot.Irq()
        self.ext = 0
        self.irq.sources[1] = self.quart.irq
        for n in range(16):
            if n != 1:
                self.irq.sources[n] = (lambda n=n: bool(self.ext >> n & 1))
        self.ioctl = p9boot.Register("IOCTL")
        self.incon = p9boot.Latch("incon")
        self.dev = {"quart": self.quart, "irq": self.irq,
                    "ioctl": self.ioctl, "incon": self.incon}

    def tick(self, d, n):
        du = self.quart.duarts[d]
        for _ in range(n):
            if not du["running"] or du["next_tick"] is None:
                raise SystemExit("trace: tick of DUART %d, not running" % d)
            if du["next_tick"] < self.now:
                raise SystemExit("trace: DUART %d tick in the past" % d)
            self.now = du["next_tick"]
            self.quart._tick(d)

    def rx(self, ch, b):
        port = self.quart.ports[ch]
        before = port["received"]
        port["pending"].append(b)
        port["next_rx"] = self.now
        self.quart._rx(ch)
        if port["received"] != before + 1:
            raise SystemExit("trace: byte 0x%02x on channel %d not taken "
                             "(FIFO full or receiver off)" % (b, ch))


def word(op, dev=0, wr=0, mask=0, off=0, wdata=0, exp=0, err=0, qirq=0,
         il6=0, ch=0, cnt=0, arg=0):
    v = (op << 124 | dev << 120 | wr << 119 | mask << 115 | off << 103
         | wdata << 71 | exp << 39 | err << 38 | qirq << 37 | il6 << 36
         | ch << 32 | cnt << 16 | arg)
    return "%032x" % v


def vectors(args):
    m = Models()
    out = []
    stats = collections.Counter()
    checked = 0
    for lineno, raw in enumerate(open(args.trace), 1):
        s = raw.split("#")[0].split()
        if not s:
            continue
        where = "%s:%d" % (args.trace, lineno)
        k = s[0]
        if k == "a":
            dev, rw, off = s[1], s[2], int(s[3], 16)
            want = None
            if "=" in s:
                want = s[s.index("=") + 1]
            obj = m.dev[dev]
            outs = [bytes(p["out"]) for p in m.quart.ports]
            if rw == "r":
                try:
                    v, err = obj.read(off) & 0xFFFFFFFF, 0
                except FAILS:
                    v, err = 0, 1
                got = "ERR" if err else "%x" % v
                out.append(word(1, DEVS[dev], 0, 0, off, 0, v, err))
                stats[(dev, "r", off, "ERR" if err else "ok")] += 1
            else:
                data, mask = int(s[4], 16), int(s[5], 16)
                try:
                    obj.write(off, data, mask)
                    err = 0
                except FAILS:
                    err = 1
                got = "ERR" if err else "ok"
                out.append(word(1, DEVS[dev], 1, mask, off, data, 0, err))
                stats[(dev, "w", off, got)] += 1
            if want == "RTLERR":
                if err:
                    raise SystemExit("%s: RTLERR, but the model stopped too"
                                     % where)
                out[-1] = word(1, DEVS[dev], 1 if rw == "w" else 0,
                               0 if rw == "r" else mask, off,
                               0 if rw == "r" else data, 0, 1)
                stats[("rtl-only fault", dev, rw, off)] += 1
                checked += 1
            elif want is not None:
                checked += 1
                if want.lower() != got.lower():
                    raise SystemExit("%s: replay answered %s, the capture "
                                     "%s" % (where, got, want))
            for ch, p in enumerate(m.quart.ports):
                if want == "RTLERR":
                    break           # the RTL drops what it faults on
                for b in bytes(p["out"])[len(outs[ch]):]:
                    out.append(word(4, ch=ch, arg=b))
                    stats[("tx", ch)] += 1
        elif k == "t":
            d, n = int(s[1]), int(s[2])
            m.tick(d, n)
            out.append(word(2, ch=d, cnt=n))
            stats[("tick", d)] += n
        elif k == "x":
            ch, b = int(s[1]), int(s[2], 16)
            m.rx(ch, b)
            out.append(word(3, ch=ch, arg=b))
            stats[("rx", ch)] += 1
        elif k == "e":
            m.ext = int(s[1], 16) & ~2
            out.append(word(5, arg=m.ext))
        elif k == "s":
            q = 1 if m.quart.irq() else 0
            il6 = 1 if m.irq.asserted() else 0
            if len(s) >= 3:
                checked += 1
                if (int(s[1]), int(s[2])) != (q, il6):
                    raise SystemExit("%s: replay irq/IL6 %d %d, capture %s "
                                     "%s" % (where, q, il6, s[1], s[2]))
            out.append(word(6, qirq=q, il6=il6))
            stats["sample"] += 1
        else:
            raise SystemExit("%s: unknown record %r" % (where, k))
    out.append(word(0))
    if len(out) > args.depth:
        raise SystemExit("trace: %d vectors, the testbench holds %d"
                         % (len(out), args.depth))
    with open(args.out, "w") as f:
        f.write("\n".join(out) + "\n")
    print("quart_trace: %s -> %s: %d vectors, %d captured values "
          "re-checked" % (args.trace, args.out, len(out), checked))
    if args.stats:
        for key, v in sorted(stats.items(), key=str):
            print("  %-40s %d" % (key, v))
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("capture")
    c.add_argument("trace")
    c.add_argument("p9boot", nargs=argparse.REMAINDER,
                   help="p9boot.py's own arguments (after --)")
    v = sub.add_parser("vectors")
    v.add_argument("trace")
    v.add_argument("out")
    v.add_argument("--depth", type=int, default=1 << 20)
    v.add_argument("--stats", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "capture":
        if args.p9boot and args.p9boot[0] == "--":
            args.p9boot = args.p9boot[1:]
        return capture(args)
    return vectors(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
