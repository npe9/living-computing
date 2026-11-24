#!/usr/bin/env python3
"""Boot s9term on the reference model with its root from the 1e file
server in QEMU (docs/p9boot.md "The join"; docs/qemu_1e_server.md).

  server   tools/qemu1e: 9dos.q from fd.img, kfs on fs.img, `rc /serve
           10.9.0.1 255.255.255.0` (1e's ip/bootp, aux/listen il)
  Hobbit   tools/p9boot.py: s9term, the SONIC's frames on UDP
           127.0.0.1:10902 <-> 127.0.0.1:10901, one ethernet frame per
           datagram (QEMU -netdev dgram)

The model types Return at `root is from` (il) and at `user[none]`.  The
run ends at TEXT on the Hobbit's screen (default `init: starting`), at a
stop of the model, or at --max-steps.  Needs tools/qemu1e/build.sh to
have been run.  Writes build/a4net/join/{hobbit.pcap,server.pcap,
server.log,console}.
"""
import argparse
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
HOBBIT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "qemu1e"))
import p9boot   # noqa: E402
import qemu1e   # noqa: E402

Q = os.path.join(HOBBIT, "build", "qemu")
S9TERM = os.path.join(HERE, "plan9-1e", "hobbit", "s9term")
PS, PH = 10901, 10902


def start_server(wd):
    net = ("-netdev dgram,id=n0,local.type=inet,local.host=127.0.0.1,"
           "local.port=%d,remote.type=inet,remote.host=127.0.0.1,"
           "remote.port=%d -device ne2k_isa,iobase=0x300,irq=9,netdev=n0,"
           "mac=52:54:00:12:34:56 -object filter-dump,id=f0,netdev=n0,"
           "file=server.pcap" % (PS, PH))
    srv = qemu1e.Machine(wd, fd=os.path.join(Q, "fd.img"),
                         hd=os.path.join(Q, "fs.img"),
                         hd2=os.path.join(Q, "arch.img"), net=net.split(),
                         extra=["-snapshot"],
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


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--max-steps", type=int, default=3000000000)
    ap.add_argument("--until", default="init: starting")
    ap.add_argument("--progress", type=int, default=5000000)
    ap.add_argument("--out", default=os.path.join(HOBBIT, "build", "a4net",
                                                  "join"))
    args = ap.parse_args(argv)
    os.makedirs(args.out, exist_ok=True)
    srv = start_server(args.out)
    t0 = time.time()
    try:
        boot = p9boot.Boot(S9TERM)
        boot.script = [(b"il]: ", b"\r"), (b"user[none]: ", b"\r")]
        boot.until = args.until.encode()
        boot.progress = args.progress
        boot.attach(p9boot.Wire(
            boot.sonic.clock, pcap=os.path.join(args.out, "hobbit.pcap"),
            peer="127.0.0.1:%d" % PS, local="127.0.0.1:%d" % PH))
        status = boot.run(args.max_steps)
    finally:
        try:
            s = srv.screen()
            srv._log(s)
            print("--- server screen\n" + s.rstrip())
        finally:
            srv.quit()
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
    for chan, data in sorted(boot.console.items()):
        print("p9join: console %s: %r" % (chan, bytes(data)))
    with open(os.path.join(args.out, "console"), "wb") as f:
        f.write(bytes(boot.console["screenputs"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
