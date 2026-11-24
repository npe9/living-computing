#!/usr/bin/env python3
"""Boot s9term on the reference model with its root from the 1e file
server in QEMU (docs/p9boot.md "The join"; docs/qemu_1e_server.md).

  server   tools/qemu1e: 9dos.q from fd.img, kfs on fs.img, `rc /serve
           10.9.0.1 255.255.255.0` (1e's ip/bootp, aux/listen il)
  Hobbit   tools/p9boot.py: s9term, the SONIC's frames on UDP
           127.0.0.1:10902 <-> 127.0.0.1:10901, one ethernet frame per
           datagram (QEMU -netdev dgram)

The two machines share one time base (p9boot ETHER_CHOICES['lockstep']):
QEMU runs with -icount (its clock follows its own instructions) and is
paused (QMP `stop`) while the model is busy, then run (`cont`) until its
own tick counter has caught up with model time; while the model idles,
the server runs and the model waits for it.  --free-run gives the old
behaviour (the server on the wall clock, the busy model ~200 times slow).

--hub puts the Hobbit on the three-machine 1e network of
docs/qemu_1e_server.md section 5 instead: tools/qemu1e/hub.py joins fs9
(the file and auth server), cpu9 (the CPU server, booted from
build/qemu-cpu/fd-cpu.img as net_test.py boots it, listening on il) and
the Hobbit, each on its own hub port; the lockstep then runs both QEMUs
by their own tick counters (ClockGroup).  --password-first WRONG types a
wrong password first, to show the auth server refusing it.

The model types Return at `root is from` (il) and at `user[none]`, then
each --type TEXT=REPLY in order.  The run ends at TEXT on the Hobbit's
screen (--until, default `init: starting`), at a stop of the model, or at
--max-steps.  Needs tools/qemu1e/build.sh to have been run.  Writes
build/a4net/join/{hobbit.pcap,server.pcap,server.log,console,uart0}
(--out).
"""
import argparse
import os
import re
import select
import struct
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
HOBBIT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "qemu1e"))
import p9boot   # noqa: E402
import qemu1e   # noqa: E402
import net1e    # noqa: E402
from hub import Hub  # noqa: E402

Q = os.path.join(HOBBIT, "build", "qemu")
QC = os.path.join(HOBBIT, "build", "qemu-cpu")
HOBBIT_MAC = bytes.fromhex("525400000b0b")     # p9boot.EEPROM_EA
S9TERM = os.path.join(HERE, "plan9-1e", "hobbit", "s9term")
PS, PH = 10901, 10902


class ServerClock:
    """The 1e server's own clock, as the model's peer clock
    (p9boot ETHER_CHOICES['lockstep']).  Its time is MACHP(0)->ticks
    (pc/clock.c `m->ticks++`, HZ 20 in pc/mem.h), read from guest memory
    with QMP `pmemsave`; the address is found in the server's kernel by
    clock()'s own first instructions (`mov m,%eax; incl 12(%eax)`: `m`
    is the Mach pointer, `ticks` its fourth word).  QEMU is paused with
    `stop` and resumed with `cont`, which pauses its virtual clock and
    so the guest's timer: the guest sees no time pass while stopped."""

    HZ = 20
    CLOCK = re.compile(rb"\x83\xec\x0c\x83\x64\x24\x04\x00\x8b\x05(....)"
                       rb"\xff\x40\x0c\xe8", re.S)

    def __init__(self, machine, kernel):
        self.m = machine
        hits = self.CLOCK.findall(open(kernel, "rb").read())
        if len(hits) != 1:
            raise SystemExit("%s: clock() not found once (%d)" % (
                kernel, len(hits)))
        self.mptr = struct.unpack("<I", hits[0])[0] & 0x7FFFFFFF
        self.fn = os.path.join(machine.workdir, "ticks.%s.bin" % machine.id)
        self.quantum = 1.0 / self.HZ
        self.base = 0.0
        self.t0 = 0
        self.runs = 0
        self.wall = 0.0         # wall seconds the server ran
        self.running = True
        self.held = None        # ticks while stopped (they cannot move)

    def _read(self, pa, n):
        self.m.cmd("pmemsave", val=pa, size=n,
                   filename=os.path.abspath(self.fn))
        with open(self.fn, "rb") as f:
            return f.read()

    def ticks(self):
        if not self.running and self.held is not None:
            return self.held
        mach, = struct.unpack("<I", self._read(self.mptr, 4))
        t = struct.unpack("<I", self._read((mach & 0x7FFFFFFF) + 12, 4))[0]
        if not self.running:
            self.held = t
        return t

    def attach(self, model_time):
        """Pause the server and make its clock read model_time now."""
        self.stop()
        self.t0 = self.ticks()
        self.base = model_time

    def now(self):
        return self.base + (self.ticks() - self.t0) / float(self.HZ)

    def stop(self):
        if self.running:
            self.m.cmd("stop")
            self.running = False

    def cont(self):
        if not self.running:
            self.held = None
            self.m.cmd("cont")
            self.running = True

    def run_until(self, t, sock=None):
        """Run the server until its clock reads t or, with sock, until a
        datagram is waiting there (True).  A server already at t is not
        run at all."""
        if self.now() >= t:
            return bool(sock is not None
                        and select.select([sock], [], [], 0)[0])
        w0 = time.time()
        self.runs += 1
        self.cont()
        try:
            while True:
                if sock is not None:
                    if select.select([sock], [], [], 0.002)[0]:
                        return True
                else:
                    time.sleep(0.002)
                if self.now() >= t:
                    return False
        finally:
            self.stop()
            self.wall += time.time() - w0


class ClockGroup:
    """Several QEMUs as the model's one peer clock (ETHER_CHOICES
    ['lockstep'] on the hub, docs/p9boot.md "On the 1e network").  Each
    member is a ServerClock on its own machine's ticks.  The group's time
    is the laggard's, so the model's busy-time check (a quantum behind)
    runs whichever QEMU is behind; run_until resumes every member whose
    clock is short of t, stops each as its own clock reaches t, and
    stops them all when a datagram waits at the Hobbit's socket.  While
    they run together the QEMUs are not locked to each other: each
    follows its own -icount pace, and the faster is held at t until the
    other catches up."""

    def __init__(self, clocks):
        self.clocks = clocks
        self.quantum = min(c.quantum for c in clocks)
        self.runs = 0
        self.wall = 0.0

    def attach(self, model_time):
        for c in self.clocks:
            c.attach(model_time)

    def now(self):
        return min(c.now() for c in self.clocks)

    def stop(self):
        for c in self.clocks:
            c.stop()

    def cont(self):
        for c in self.clocks:
            c.cont()

    def run_until(self, t, sock=None):
        behind = [c for c in self.clocks if c.now() < t]
        if not behind:
            return bool(sock is not None
                        and select.select([sock], [], [], 0)[0])
        w0 = time.time()
        self.runs += 1
        for c in behind:
            c.runs += 1
            c.cont()
        try:
            while True:
                if sock is not None:
                    if select.select([sock], [], [], 0.002)[0]:
                        return True
                else:
                    time.sleep(0.002)
                for c in behind:
                    if c.running and c.now() >= t:
                        c.stop()
                if not any(c.running for c in behind):
                    return False
        finally:
            for c in behind:
                c.stop()
            self.wall += time.time() - w0


def start_server(wd, extra=(), ps=PS, ph=PH):
    net = ("-netdev dgram,id=n0,local.type=inet,local.host=127.0.0.1,"
           "local.port=%d,remote.type=inet,remote.host=127.0.0.1,"
           "remote.port=%d -device ne2k_isa,iobase=0x300,irq=9,netdev=n0,"
           "mac=52:54:00:12:34:56 -object filter-dump,id=f0,netdev=n0,"
           "file=server.pcap" % (ps, ph))
    srv = qemu1e.Machine(wd, fd=os.path.join(Q, "fd.img"),
                         hd=os.path.join(Q, "fs.img"),
                         hd2=os.path.join(Q, "arch.img"), net=net.split(),
                         extra=["-snapshot"] + list(extra),
                         log=os.path.join(wd, "server.log"))
    srv.wait("boot from", 30)
    srv.type("\n")
    srv.wait("root is from", 60)
    srv.type("\n")
    srv.wait("user", 60)
    srv.type("glenda\n")
    srv.wait("password", 10)
    srv.type("password\n")
    srv.wait("^%", 60)
    srv.type("rc /serve 10.9.0.1 255.255.255.0\n")
    srv.wait("tcp: announce", 120)
    return srv


def start_cpu9(wd, extra, local, remote):
    """cpu9 as net_test.py boots it: 9pccpu.qs from fd-cpu.img, its root
    from fs9 over IL; the host key typed at /boot (boot/key.c, no nvram)
    and at init's console lock; then what cpurc's kremvax case does,
    `ip/ipconfig` (ip/arpd, the ARP answerer) and `aux/listen il`."""
    m = qemu1e.Machine(wd, fd=os.path.join(QC, "fd-cpu.img"),
                       net=net1e.net("cpu9", local, remote, pcap="cpu9.pcap"),
                       extra=["-snapshot"] + list(extra),
                       log=os.path.join(wd, "cpu9.log"))
    net1e.boot(m, "il")
    m.wait("password", 120)
    m.type(net1e.CPU9_PW + "\n")
    net1e.wait_prompt(m, r"cpu9 password: *$", 900)
    m.type(net1e.CPU9_PW + "\n")
    net1e.wait_prompt(m, r"% *$", 300)
    m.type("ip/ipconfig; aux/listen il; echo cpu9 listening\n")
    m.wait("^cpu9 listening", 60)
    time.sleep(3)
    return m


class LoggedBoot(p9boot.Boot):
    """p9boot.Boot that calls on_typed() after each scripted reply."""
    on_typed = None

    def tap_screenputs(self):
        n = len(self.typed)
        try:
            super().tap_screenputs()
        finally:
            if self.on_typed is not None and len(self.typed) > n:
                self.on_typed(self.typed[n:])


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--image", default=S9TERM,
                    help="the Hobbit kernel image (default the shipped "
                         "s9term; a 9term linked from the release types "
                         "on its kbd.c keyboard, p9boot "
                         "CHOICES['console-keyboard'])")
    ap.add_argument("--max-steps", type=int, default=3000000000)
    ap.add_argument("--until", default="init: starting")
    ap.add_argument("--progress", type=int, default=5000000)
    ap.add_argument("--out", default=os.path.join(HOBBIT, "build", "a4net",
                                                  "join"))
    ap.add_argument("--free-run", action="store_true",
                    help="let the server run on the wall clock (no "
                         "lockstep; ETHER_CHOICES['peer'])")
    ap.add_argument("--icount", metavar="SHIFT", default="4",
                    help="run QEMU with -icount shift=SHIFT (default 4: "
                         "the server's clock follows its instructions, "
                         "16 ns each; 'off' for QEMU's host clock)")
    ap.add_argument("--type", action="append", default=[],
                    metavar="TEXT=REPLY",
                    help="after the two boot answers, type REPLY once the "
                         "screen shows TEXT (p9boot --type)")
    ap.add_argument("--user", default="none",
                    help="the answer to /boot's user[none] (default none); "
                         "another user is asked a password (--password) "
                         "and the boot goes on unchecked (no auth server)")
    ap.add_argument("--password", default="password",
                    help="typed at password: for a user other than none")
    ap.add_argument("--input", metavar="SCRIPT",
                    help="timed keyboard and mouse input (p9boot --input, "
                         "p9term TERM_CHOICES['input'])")
    ap.add_argument("--input-line", action="append", default=[],
                    metavar="LINE")
    ap.add_argument("--screen-every", type=int, default=0, metavar="N",
                    help="write OUT/screen-K.png every N instructions")
    ap.add_argument("--ports", default="%d,%d" % (PS, PH),
                    metavar="SERVER,HOBBIT",
                    help="the UDP ports of the two ends of the wire")
    ap.add_argument("--hub", action="store_true",
                    help="the three-machine network: fs9, cpu9 and the "
                         "Hobbit on tools/qemu1e/hub.py (needs "
                         "build/qemu-cpu/fd-cpu.img, cpukernel.sh)")
    ap.add_argument("--port-base", type=int, default=10941, metavar="B",
                    help="with --hub: fs9 B/B+1, the Hobbit B+2/B+3, cpu9 "
                         "B+4/B+5 (machine/hub), as net_test.py's "
                         "PORT_BASE (default 10941)")
    ap.add_argument("--password-first", metavar="WRONG",
                    help="type WRONG at the first password:, then Return "
                         "at /boot's user[USER]: and --password")
    ap.add_argument("--fs9-cmd", action="append", default=[],
                    metavar="LINE",
                    help="type LINE at fs9's rc (it runs -snapshot) after "
                         "/serve, before the Hobbit starts")
    args = ap.parse_args(argv)
    os.makedirs(args.out, exist_ok=True)
    extra = ([] if args.icount == "off"
             else ["-icount", "shift=%s" % args.icount])
    hub = cpu9 = None
    machines = []
    slog = open(os.path.join(args.out, "screens.log"), "w")

    def screens(tag):
        for name, m in machines:
            try:
                sc = m.screen()
            except Exception as e:     # a dead QEMU must not stop the log
                sc = "(%s)" % e
            slog.write("--- %s: %s\n%s\n" % (tag, name, sc.rstrip()))
        slog.flush()

    if args.hub:
        B = args.port_base
        ps, ph = B + 3, B + 2       # the Hobbit's hub port, its own end
        hub = Hub([(B + 1, B), (B + 3, B + 2), (B + 5, B + 4)],
                  filters={1: [HOBBIT_MAC]},
                  pcap=os.path.join(args.out, "hub.pcap"))
        hub.start()
        srv = start_server(args.out, extra, B, B + 1)
        machines.append(("fs9", srv))
        try:
            for line in args.fs9_cmd:
                srv.type(line + "\n")
                time.sleep(2)
            cpu9 = start_cpu9(args.out, extra, B + 4, B + 5)
        except BaseException:
            srv.quit()
            hub.stop()
            raise
        machines.append(("cpu9", cpu9))
        screens("before the Hobbit")
    else:
        ps, ph = (int(x) for x in args.ports.split(","))
        srv = start_server(args.out, extra, ps, ph)
        machines.append(("fs9", srv))
        for line in args.fs9_cmd:
            srv.type(line + "\n")
            time.sleep(2)
    clock = None
    t0 = time.time()
    try:
        boot = LoggedBoot(args.image)
        boot.on_typed = lambda items: screens(
            "after typing %r at step %d" % (items[-1][2], items[-1][0]))
        boot.script = [(b"il]: ", b"\r")]
        if args.user == "none":
            boot.script.append((b"user[none]: ", b"\r"))
        else:
            boot.script.append((b"user[none]: ",
                                args.user.encode() + b"\r"))
            if args.password_first:
                boot.script.append((b"password: ",
                                    args.password_first.encode() + b"\r"))
                boot.script.append((("user[%s]: " % args.user).encode(),
                                    b"\r"))
            boot.script.append((b"password: ",
                                args.password.encode() + b"\r"))
        for item in args.type:
            wait, sep, reply = item.partition("=")
            boot.script.append((p9boot.unescape(wait),
                                p9boot.unescape(reply)))
        boot.until = p9boot.unescape(args.until)
        boot.progress = args.progress
        lines = []
        if args.input:
            with open(args.input) as f:
                lines += f.read().splitlines()
        lines += args.input_line
        if lines:
            boot.set_inputs(lines)
        if args.screen_every:
            boot.screen_at = [
                (k * args.screen_every,
                 os.path.join(args.out, "screen-%04d.png" % k))
                for k in range(1, args.max_steps // args.screen_every + 1)]
        wire = p9boot.Wire(
            boot.sonic.clock, pcap=os.path.join(args.out, "hobbit.pcap"),
            peer="127.0.0.1:%d" % ps, local="127.0.0.1:%d" % ph)
        if not args.free_run:
            clock = ServerClock(srv, os.path.join(Q, "9dos.q"))
            if cpu9 is not None:
                clock = ClockGroup([clock, ServerClock(
                    cpu9, os.path.join(QC, "9pccpu.qs"))])
            clock.attach(0.0)
            wire.peer_clock = clock
        boot.attach(wire)
        status = boot.run(args.max_steps)
        if clock is not None:
            print("p9join: lockstep: server clock %.3f s, %d runs, %.0f s "
                  "of wall time" % (clock.now(), clock.runs, clock.wall))
            for c in getattr(clock, "clocks", ()):
                print("p9join: lockstep: %s clock %.3f s, %d runs" % (
                    c.m.id, c.now(), c.runs))
            clock.cont()
    finally:
        try:
            screens("at the end")
            for name, m in machines:
                s = m.screen()
                m._log(s)
                print("--- %s screen\n%s" % (name, s.rstrip()))
        finally:
            for name, m in machines:
                m.quit()
            if hub is not None:
                hub.stop()
                print("p9join: hub frames received per port (fs9, hobbit, "
                      "cpu9): %s; not repeated to the Hobbit (filtered): %d"
                      % (hub.counts, hub.filtered[1]))
            slog.close()
    print("p9join: %s" % status)
    for t, secs in boot.rtc.sets:
        print("p9join: rtc set at %.3f s to %s" % (t, time.strftime(
            "%Y-%m-%d %H:%M:%S", time.gmtime(secs))))
    print("p9join: %d instructions (%d idle-skipped), model time %.3f s, "
          "host %.0f s" % (boot.steps, boot.skipped_steps,
                           boot.cycles / float(p9boot.CPU_HZ),
                           time.time() - t0))
    print("p9join: %d frames" % len(boot.wire.log))
    for t, way, frame in boot.wire.log[:60]:
        print("  %.6f %s %s" % (t, way, p9boot.decode_frame(frame)))
    for stepno, wait, reply in boot.typed:
        print("p9join: step %d: typed %r after %r" % (stepno, reply, wait))
    if boot.inputs is not None:
        for stepno, cycles, line in boot.inputs.fired:
            print("p9join: step %d (cycle %d): input %s" % (stepno, cycles,
                                                            line))
        with open(os.path.join(args.out, "input.log"), "w") as f:
            f.write("".join(l + "\n" for l in boot.inputs.log_lines()))
    boot.dump_screen(os.path.join(args.out, "screen.png"))
    for chan, data in sorted(boot.console.items()):
        print("p9join: console %s: %r" % (chan, bytes(data)))
    with open(os.path.join(args.out, "console"), "wb") as f:
        f.write(bytes(boot.console["screenputs"]))
    with open(os.path.join(args.out, "uart0"), "wb") as f:
        f.write(bytes(boot.quart.ports[0]["out"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
