#!/usr/bin/env python3
"""p9host.py -- the host end of the ULX3S SoC's host link (forwarding mode).

Speaks hobbit/fpga/rtl/hostlink.v's framed protocol (fpga/README.md, "The
host link") over a serial device. It loads the kernel with
tools/p9link.py's stream, starts it, and then answers every forwarded I/O
access ('F') from tools/p9boot.py's device models, so the kernel boots
before the devices are RTL:

  * The device models are p9boot.Boot's: Quart, Irq, incon, ioctl, RTC,
    IIC, SCSI, SONIC and the LCD, at the addresses p9boot maps.
  * Their clock is the board's core clock count. Each 'F' frame and each
    periodic 'T' frame carries it (clk5), and it becomes Boot.cycles,
    p9boot's time base, the model's cycles at CPU_HZ.
  * The interrupt level is 6 (CHOICES['irq-level']) while the Irq model
    asserts, and 7 otherwise. It is sent as 'I' whenever it changes.
  * The console is Quart channel 0's output. It goes to stdout and to
    --console FILE. With --interactive, stdin is typed into channel 0.
  * SONIC frames go to a UDP peer such as tools/qemu1e/hub.py
    (--ether-peer/--ether-local, as in p9boot.py), and optionally to a
    pcap file.

    p9host.py DEVICE [--image IMAGE] [--sparse] [--baud N] [--console FILE]
              [--iolog FILE] [--max-clocks N] [--interactive]
              [--ether-peer H:P --ether-local H:P] [--pcap FILE]

--rtl N names the devices the bitstream has as RTL (hobbit_soc's DEV_RTL,
fpga/socdev/HobbitSocDevs.bsv's bits: 0 incon/ioctl/irq, 1 Quart, 2 RTC,
3 IIC, 4 Lcdisp, 5 SONIC); their accesses never arrive here. With bit 0 the host
sends its forwarded devices' interrupt sources ('S') to the RTL Irq instead
of a level. With bit 1 the console is the 'C' bytes of the RTL Quart, and
typed bytes go out as 'K'.

DEVICE is the FTDI port in a hardware window, or the pseudo-terminal that
fpga/sim/soc_main.cpp opens with SOC_PTY. fpga/sim/run_soc_host.sh is the
end-to-end check: the Verilator SoC through a pty, with this program as
the host. Without --sparse every RAM word of the 8 MB is sent, because a
powered-up SDRAM holds no particular value.
"""
import argparse
import os
import pathlib
import select
import struct
import sys
import termios
import tty

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import p9boot          # noqa: E402
import p9link          # noqa: E402

hobbit_sem = p9boot.hobbit_sem
REPLY_LEN = {"p": 11, "w": 1, "r": 5, "b": 1, "g": 1, "F": 15, "T": 6,
             "C": 2}


class Link:
    def __init__(self, path, baud):
        self.fd = os.open(path, os.O_RDWR | os.O_NOCTTY)
        tty.setraw(self.fd)
        if baud:
            set_baud(self.fd, baud)
        self.buf = bytearray()

    def write(self, data):
        view = memoryview(data)
        while view:
            n = os.write(self.fd, view)
            view = view[n:]

    def fill(self, n, timeout=None):
        """Read until at least n bytes are buffered; False on timeout/EOF."""
        while len(self.buf) < n:
            r, _, _ = select.select([self.fd], [], [], timeout)
            if not r:
                return False
            try:
                chunk = os.read(self.fd, 4096)
            except OSError:         # the pty's other end closed
                return False
            if not chunk:
                return False
            self.buf.extend(chunk)
        return True

    def frame(self, timeout=None):
        """The next complete board frame as bytes, or None."""
        if not self.fill(1, timeout):
            return None
        c = chr(self.buf[0])
        n = REPLY_LEN.get(c)
        if n is None:
            raise SystemExit("p9host: unexpected byte 0x%02x from the board"
                             % self.buf[0])
        if not self.fill(n, timeout):
            return None
        f = bytes(self.buf[:n])
        del self.buf[:n]
        return f


def set_baud(fd, baud):
    name = "B%d" % baud
    if hasattr(termios, name):
        a = termios.tcgetattr(fd)
        a[4] = a[5] = getattr(termios, name)
        termios.tcsetattr(fd, termios.TCSANOW, a)
    elif sys.platform == "darwin":
        import fcntl
        IOSSIOSPEED = 0x80085402      # _IOW('T', 2, speed_t)
        fcntl.ioctl(fd, IOSSIOSPEED, struct.pack("L", baud))
    else:
        raise SystemExit("p9host: cannot set %d baud here" % baud)


def clk5(b):
    return int.from_bytes(b, "big")


class Host:
    def __init__(self, link, boot, args):
        self.link, self.boot, self.args = link, boot, args
        self.level = 7
        self.sent = [0, 0, 0, 0]
        self.console = open(args.console, "wb") if args.console else None
        self.iolog = open(args.iolog, "w") if args.iolog else None
        self.reads = self.writes = self.errors = 0
        self.src = 0
        self.err_seen = {}
        self.seen = b""
        self.script = []
        for item in args.type:
            wait, sep, reply = item.partition("=")
            if not sep:
                raise SystemExit("p9host: --type wants TEXT=REPLY")
            self.script.append((p9boot.unescape(wait), p9boot.unescape(reply)))

    def sync(self):
        self.link.write(b"P")
        while True:
            f = self.link.frame(10.0)
            if f is None:
                raise SystemExit("p9host: no answer to P")
            if f[:1] == b"p":
                return f

    def load(self, frames):
        for fr in frames:
            self.link.write(fr)
            want = b"g" if fr[:1] == b"G" else b"b"
            while True:
                f = self.link.frame(30.0)
                if f is None:
                    raise SystemExit("p9host: no reply to a load frame")
                if f[:1] == want:
                    break
                self.other(f)

    def other(self, f):
        if f[:1] == b"C":
            self.emit(f[1:2])
        elif f[:1] == b"T":
            self.boot.cycles = clk5(f[1:6])
            self.poll()

    def access(self, f):
        b = self.boot
        we = f[1] & 1
        a = int.from_bytes(f[2:6], "big")
        d = int.from_bytes(f[6:10], "big")
        b.cycles = clk5(f[10:15])
        v = 0
        try:
            if we:
                b.board.write(a, d, 0xF)
                self.writes += 1
            else:
                v = b.board.read(a) & 0xFFFFFFFF
                self.reads += 1
        except (hobbit_sem.BusError, p9boot.Stop) as exc:
            # The model refuses the access; the board gets 0.  Read-modify-
            # writes of halfword stores to the write-only LCD are the
            # common case (fpga/README.md, "Unrecorded I/O reads").
            self.errors += 1
            key = (we, a)
            self.err_seen[key] = self.err_seen.get(key, 0) + 1
            if self.err_seen[key] <= 3:
                print("p9host: %s %08x at clock %d: %s%s" % (
                    "write" if we else "read", a, b.cycles, exc,
                    " (further ones not shown)" if self.err_seen[key] == 3
                    else ""), file=sys.stderr)
        if self.iolog:
            self.iolog.write("%s %08x %08x %d\n" % (
                "W" if we else "R", a, d if we else v, b.cycles))
        self.link.write(b"D" + struct.pack(">I", v))
        self.poll()

    def poll(self):
        b = self.boot
        w = b.wire
        if w is not None:
            if w.sock is not None:
                w.poll_peer(0.0, b.cycles / float(p9boot.CPU_HZ))
            if w.inbound and w.inbound[0][0] <= b.cycles:
                b.sonic.poll()
        rtl = self.args.rtl
        if not rtl & 2:
            out = b.quart.ports[0]["out"]
            if len(out) > self.sent[0]:
                new = bytes(out[self.sent[0]:])
                self.sent[0] = len(out)
                self.emit(new, count=False)
        if rtl & 1:
            # The Irq is RTL: send the forwarded devices' source bits.
            src = b.irq.status()
            if rtl & 2:
                src &= ~(1 << 1)        # the RTL Quart drives bit 1
            if rtl & 32:
                src &= ~(1 << 9)        # the RTL SONIC drives bit 9
            if src != self.src:
                self.src = src
                self.link.write(b"S" + struct.pack(">H", src))
        else:
            lv = 6 if b.irq.asserted() else 7
            if lv != self.level:
                self.level = lv
                self.link.write(b"I" + bytes([lv]))

    def emit(self, new, count=True):
        if count:
            self.sent[0] += len(new)
        sys.stdout.buffer.write(new)
        sys.stdout.flush()
        if self.console:
            self.console.write(new)
            self.console.flush()
        # --type TEXT=REPLY: p9boot's CHOICES['console-input'], keyed on
        # the console's text (the kernel's prompts appear on channel 0).
        self.seen += new
        while self.script and self.script[0][0] in self.seen:
            wait, reply = self.script.pop(0)
            self.seen = self.seen[self.seen.index(wait) + len(wait):]
            self.type(reply)

    def type(self, data):
        if self.args.rtl & 2:
            # One byte per 'K'; the board's 19200-baud line takes one
            # character per ~0.5 ms, far faster than typing.
            for c in data:
                self.link.write(b"K" + bytes([c]))
        else:
            self.boot.quart.feed(0, data)

    def serve(self):
        stdin = sys.stdin.fileno() if self.args.interactive else None
        while True:
            if stdin is not None:
                r, _, _ = select.select([stdin], [], [], 0)
                if r:
                    data = os.read(stdin, 256)
                    if data:
                        self.type(data.replace(b"\n", b"\r"))
            f = self.link.frame(1.0 if stdin is not None else 600.0)
            if f is None:
                if stdin is not None:
                    continue
                return "the link went quiet or closed"
            if f[:1] == b"F":
                self.access(f)
            else:
                self.other(f)
            if self.args.max_clocks and self.boot.cycles >= self.args.max_clocks:
                return "core clock %d reached" % self.boot.cycles


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("device")
    ap.add_argument("--image", default=str(HERE / "plan9-1e" / "hobbit" /
                                          "s9term"))
    ap.add_argument("--sparse", action="store_true",
                    help="load only nonzero RAM words (RAM known zero)")
    ap.add_argument("--no-load", action="store_true",
                    help="the board is already loaded and started")
    ap.add_argument("--baud", type=int, default=1000000,
                    help="line rate; 0 leaves it alone (a pty)")
    ap.add_argument("--console", metavar="FILE")
    ap.add_argument("--iolog", metavar="FILE",
                    help="every forwarded access: R|W addr value clock")
    ap.add_argument("--max-clocks", type=int, default=0)
    ap.add_argument("--type", action="append", default=[],
                    metavar="TEXT=REPLY",
                    help="once the console shows TEXT, type REPLY (as "
                         "p9boot.py --type); repeatable, in order")
    ap.add_argument("--interactive", action="store_true",
                    help="type stdin into the console (Quart channel 0)")
    ap.add_argument("--rtl", type=lambda v: int(v, 0), default=0,
                    help="the bitstream's DEV_RTL bits (default 0: all "
                         "devices forwarded)")
    ap.add_argument("--counter-period", type=float, metavar="SECONDS")
    ap.add_argument("--ether-peer", metavar="HOST:PORT")
    ap.add_argument("--ether-local", metavar="HOST:PORT")
    ap.add_argument("--pcap", metavar="FILE")
    args = ap.parse_args(argv)

    boot = p9boot.Boot(args.image)
    if args.counter_period is not None:
        boot.quart.period_override = args.counter_period
    if args.ether_peer or args.pcap:
        boot.attach(p9boot.Wire(boot.sonic.clock, pcap=args.pcap,
                                peer=args.ether_peer, local=args.ether_local))
    link = Link(args.device, args.baud)
    host = Host(link, boot, args)
    p = host.sync()
    print("p9host: board answered: status %02x, %d core clocks, %d retired"
          % (p[1], clk5(p[2:7]), int.from_bytes(p[7:11], "big")),
          file=sys.stderr)
    if not args.no_load:
        frames, nrom, nram, entry = p9link.load_stream(
            args.image, args.sparse, 256)
        print("p9host: loading %d ROM and %d RAM words, then G %08x"
              % (nrom, nram, entry), file=sys.stderr)
        host.load(frames)
    why = host.serve()
    print("p9host: %s; %d forwarded reads, %d writes, %d bus errors, "
          "console %d bytes" % (why, host.reads, host.writes, host.errors,
                                host.sent[0]), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
