#!/usr/bin/env python3
"""Run the 1st Edition Hobbit boot ROM (`9rom`) on the reference model,
from reset.

`9rom` is what `sys/src/9/hobbit/mkfile`'s `9rom` rule links (`zl -l -H1
-T0xC0000000 -D0xC0604000 -E0x0 roml.$O rom.$O bootrom.root.$O librom.a
-lc`); `tools/p9kbuild.py link --conf rom` makes it on the model and
`tools/p9kbuild/9rom` is the committed product (docs/boot_rom.md).  The
ROM is a whole Plan 9 kernel (CONF=rom, TYPE=rom) that runs out of the
EPROM; its /boot is `sys/src/9/boot/romboot.c`, the `>>>` monitor.

This harness is the board of `tools/p9boot.py` (the same device models:
Quart, Irq, IOCTL, timekeeper/NVRAM, IIC/EEPROM, WD33C93, SONIC, incon
latch) with three differences, each a choice in ROM_CHOICES:

  * the image is the EPROM at physical PROMBASE (0), not RAM: text then
    data, as roml.s's `_copy` expects (ROM_CHOICES['rom-image']);
  * the part starts at physical 0 in the reset state of PRM p. 1-35
    (PC 0, PSW 0, CONFIG 0, VB 0) -- nothing of the ROM is skipped;
  * RAM mirrors (ROM_CHOICES['ram-mirror']): rommain.c meminit sizes
    memory by writing PPage0.memsize and watching for the write to show
    up 1 MB, 2 MB, ... above it.

Console output is Quart channel 0 (rommain.c:40-41: eiaspecial(0,
&printq, &kbdq, 19200)).  `--type 'WAIT=REPLY'` types REPLY once channel
0's output (after the previous match) contains WAIT: on channel 0 to the
ROM, and after the hand-off to s9term's keyboard (channel 2, scan codes;
ROM_CHOICES['console-input']).  `--until TEXT` stops once channel 0's
output contains TEXT.

    python3 tools/p9rom.py tools/p9kbuild/9rom --until '>>>'
"""

import argparse
import bisect
import os
import pathlib
import struct
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "sem"))
import p9boot          # noqa: E402
import p9exec          # noqa: E402
import p9term          # noqa: E402
import hobbit_sem      # noqa: E402

MASK32 = 0xFFFFFFFF
PROMBASE = 0x00000000
VROMBASE = 0xC0000000
RAMBASE = p9boot.RAMBASE
IOBASE = p9boot.IOBASE
IONAK = p9boot.IONAK
ROM_BYTES = 64 * 4096           # roml.s:46 NPSTE(PROMBASE, 64, STE_V)
ROM9 = HERE / "p9kbuild" / "9rom"
Stop = p9boot.Stop

ROM_CHOICES = {
    "rom-image": "The EPROM holds the -H1 image's text from physical 0 "
                 "and its data right after (etext), each 32-bit word as "
                 "zl wrote it (the words the CPU reads; text parcels big-"
                 "endian, p. 1-4 note).  roml.s's _copy reads the data "
                 "from $etext(SB) (VROMBASE + text) and copies it to "
                 "KDATABASE+0x4000 = -D, so this layout is what the code "
                 "requires.  mkrom.c's .com file is the same bytes with "
                 "the two halves of every word exchanged (b2 b3 b0 b1), "
                 "the EPROM programmer's order; how the board's EPROMs "
                 "are wired to the bus is not in the release.  The ROM "
                 "decodes 256 KB (the STE's 64 pages); a write is a bus "
                 "error.",
    "rom-past-image": "A read of the ROM past the image returns 0xFFFFFFFF "
                      "(erased EPROM) and is recorded (RomImage.past; "
                      "--strict-rom stops instead).  roml.s's _copy "
                      "(:69-75) does read one halfword past the data "
                      "image: it tests `CMPHI R4, $edata(SB)` before each "
                      "copy, so it copies at R4 = edata too -- one "
                      "halfword beyond the data, into the first word of "
                      "the BSS, which _clear then zeroes.",
    "ram-mirror": "RAM is MEMSIZE (default 8 MB) at RAMBASE and repeats "
                  "every MEMSIZE up to IOBASE, except where a device "
                  "decodes (the SONIC at 0xA4400000, io.h).  rommain.c "
                  "meminit "
                  "(:66-91) needs some such behaviour: it stops at the "
                  "first 1 MB step where a write to PPage0.memsize "
                  "changes the word at the step, and it has no bus-error "
                  "path.  How the real board decoded RAM above the "
                  "fitted size is not in the release; partial address "
                  "decoding (aliasing) is what the code assumes.",
    "devices": "Every device model and its choices are tools/p9boot.py's "
               "(CHOICES, QUART_CHOICES, IIC_CHOICES, SONIC_CHOICES); "
               "the NVRAM starts all zero unless --nvram FILE gives its "
               "2040 bytes.",
    "irq": "As p9boot: Irq's request is taken at interrupt level 6 "
           "(raml.s/roml.s: _vectors+0x28 = interrupt) when the PSW's "
           "IPL is 7.",
    "idle-skip": "p9boot's CHOICES['idle-skip'] (the same function), in "
                 "the running kernel's runproc: the ROM's own (text read "
                 "from the EPROM, runhiq/runloq at their physical "
                 "addresses, KDATABASE 0xC0600000 = 0x80200000) and, "
                 "after the hand-off, the loaded kernel's (--kernel).  "
                 "Retired laps count as instructions, so step counts are "
                 "the unskipped run's.  --no-idle-skip turns it off.",
    "console-input": "--type replies go to Quart channel 0 (the ROM's "
                     "console) until the hand-off; after it, if the "
                     "loaded kernel has kbdinit (s9term), to channel 2 as "
                     "PC scan codes, as p9boot CHOICES['console-keyboard'] "
                     "types them.",
}

# roml.s: KDATABASE (virtual 0xC0600000) is physical RAMBASE + 2 MB
KDATA_VA = 0xC0400000            # virtual address of physical RAMBASE


class MirrorBoard(p9boot.Board):
    """p9boot.Board with RAM repeating every memsize up to IOBASE
    (ROM_CHOICES['ram-mirror'])."""

    def __init__(self, memsize, mirror=True):
        super().__init__(memsize)
        self.memsize = memsize
        self.mirror = mirror

    def _fold(self, pa):
        pa &= ~3 & MASK32
        if (self.mirror and RAMBASE + self.memsize <= pa < IOBASE
                and self._device(pa)[0] is None):
            return RAMBASE + (pa - RAMBASE) % self.memsize
        return pa

    def read(self, pa):
        return super().read(self._fold(pa))

    def write(self, pa, data, mask):
        return super().write(self._fold(pa), data, mask)


class RomImage:
    """The EPROM at PROMBASE (ROM_CHOICES['rom-image'])."""

    def __init__(self, path, strict=False):
        self.past = []              # physical addresses read past the image
        self.strict = strict
        self.k = p9exec.read_kernel(str(path))
        k = self.k
        if k["textbase"] != VROMBASE:
            raise SystemExit("%s: text base 0x%08x, not VROMBASE"
                             % (path, k["textbase"]))
        blob = k["blob"]
        n = k["text"] + k["data"]
        if n > ROM_BYTES:
            raise SystemExit("%s: text+data %d > the ROM's %d" % (
                path, n, ROM_BYTES))
        body = blob[k["text_off"]:k["text_off"] + n]
        body += bytes(-len(body) % 4)
        self.words = [int.from_bytes(body[i:i + 4], "little")
                      for i in range(0, len(body), 4)]

    def read(self, off):
        i = off >> 2
        if i >= len(self.words):
            # ROM_CHOICES['rom-past-image']
            self.past.append(PROMBASE + off)
            if self.strict:
                raise Stop("read of the boot ROM at physical 0x%08x, past "
                           "the image (%d bytes)"
                           % (PROMBASE + off, 4 * len(self.words)))
            return 0xFFFFFFFF
        return self.words[i]

    def write(self, off, data, mask):
        raise hobbit_sem.BusError("bus: write to the boot ROM at physical "
                                  "0x%08x" % (PROMBASE + off))


class RomRun:
    def __init__(self, image=ROM9, memsize=p9boot.MEMSIZE, mirror=True,
                 nvram=None, ea=p9boot.EEPROM_EA, strict_rom=False):
        self.board = MirrorBoard(memsize, mirror)
        self.rom = RomImage(image, strict_rom)
        self.k = self.rom.k
        self.board.add(PROMBASE, PROMBASE + ROM_BYTES, self.rom)
        self.cycles = 0
        clock = lambda: self.cycles / float(p9boot.CPU_HZ)
        self.ioctl = p9boot.Register("IOCTL")
        self.irq = p9boot.Irq()
        self.quart = p9boot.Quart(25, clock)
        self.rtc = p9boot.Timekeeper(clock, p9boot.RTC_BASE)
        if nvram is not None:
            self.rtc.nvram[:len(nvram)] = nvram
        self.iic = p9boot.Iic(p9boot.eeprom_image(ea))
        self.incon = p9boot.Latch("incon")
        self.scsi = p9boot.Wd33c93()
        self.sonic = p9boot.Sonic(self.board, clock)
        self.irq.sources[1] = self.quart.irq
        self.irq.sources[9] = self.sonic.irq
        self.irq.sources[10] = lambda: self.scsi.intr
        b = self.board
        b.add(IONAK + 0x2000, IONAK + 0x4000, self.rtc)
        b.add(IOBASE + 0x0080, IOBASE + 0x0088, self.iic)
        b.add(IONAK + 0x0100, IONAK + 0x0108, self.scsi)
        b.add(0xA4400000, 0xA4400100, self.sonic)
        b.add(IOBASE + 0x0000, IOBASE + 0x0014, self.incon)
        b.add(IONAK + 0x0000, IONAK + 0x0004, self.ioctl)
        b.add(IONAK + 0x0080, IONAK + 0x0090, self.irq)
        b.add(IOBASE + 0x0100, IOBASE + 0x0200, self.quart)
        # the terminal's LCD (io.h Lcdisp), for a loaded s9term
        self.lcd = p9term.LcdPanel(clock)
        b.add(IOBASE + 0x3000, IOBASE + 0x3008, self.lcd)
        self.wire = None
        self.handoff = None         # what gotopc left (record_handoff)
        self.next_syms = None       # the loaded kernel's symbols
        self.kimg = None            # the image `b` should have loaded
        self.syms = p9boot.Symbols(p9exec.kernel_symbols(self.k))
        # ROM_CHOICES['idle-skip']
        self.idle_skip = True
        self.idle_last = None
        self.skipped_steps = self.skipped_cycles = self.skips = 0
        self.idle_head, self.idle_words = p9boot.find_idle_loop(
            self, parcel=self._rom_parcel,
            data_pa=lambda va: va - KDATA_VA + RAMBASE)
        # ROM_CHOICES['console-input']
        self.console_channel, self.console_encode = 0, bytes
        self.sysm = hobbit_sem.System(bus=self.board)
        self.sysm.cret_clamp = True     # as p9boot CHOICES['cret-msp']
        # PRM p. 1-35: the reset state; PC 0 (the reset vector, physical)
        self.state = hobbit_sem.State(pc=0, sp=0, msp=0, psw=0, isp=0,
                                      vb=0, config_kl=False,
                                      cache=[0] * 64, system=self.sysm)
        self.steps = 0
        self.interrupts = 0
        self.nevents = 0
        self.reached = []           # (step, function) first reaches
        self.seen = set()
        self.script = []            # [(wait bytes, reply bytes)]
        self.script_from = 0
        self.typed = []             # (step, wait, reply)
        self.until = None
        self.watch = {}             # pc -> callable

    def _rom_parcel(self, va):
        w = self.rom.words[(va - VROMBASE) >> 2]
        return (w & 0xFFFF) if va & 2 else (w >> 16)

    def next_event(self):
        """As p9boot Boot.next_event (no timed input script here)."""
        times = [t for t in (self.quart.next_event(),
                             self.sonic.next_event()) if t is not None]
        return min(times) if times else None

    try_idle_skip = p9boot.Boot.try_idle_skip

    def enter_kernel(self, syms):
        """Go on in the kernel `b` loaded: its symbols, its idle loop, its
        keyboard (ROM_CHOICES['idle-skip'], ['console-input'])."""
        self.syms = syms
        self.idle_last = None
        self.idle_head, self.idle_words = p9boot.find_idle_loop(self)
        if "kbdinit" in syms.by_name:
            self.console_channel = 2
            self.console_encode = p9boot.p9scancode.Encoder().encode

    def uart(self, ch=0):
        return bytes(self.quart.ports[ch]["out"])

    def where(self, pc):
        """Symbolic kernel PC: physical ROM addresses (before _virtual)
        are named by their VROMBASE address."""
        if self.state.psw & hobbit_sem.PSW_USER:
            return "user 0x%08x" % pc
        v = pc + VROMBASE if pc < ROM_BYTES else pc
        return self.syms.where(v) + ("" if v == pc else " (physical)")

    def attach(self, wire):
        self.wire = wire
        self.sonic.wire = wire

    def record_handoff(self):
        """The first kernel-mode instruction outside the ROM's text: the
        state roml.s gotopc KRETs to, and PPage0 as romboot's `b` left
        it (rom.h; the offsets are the struct's, docs/boot_rom.md)."""
        st, sy, b = self.state, self.sysm, self.board
        pp = RAMBASE
        argc = b.read(pp + p9boot.PPAGE0_ARGC)

        def cstr(pa):
            out = bytearray()
            while len(out) < 256:
                c = b.byte(pa + len(out))
                if c == 0:
                    break
                out.append(c)
            return bytes(out)
        argv = []
        for i in range(argc):
            ptr = b.read(pp + p9boot.PPAGE0_ARGC + 4 + 4 * i)
            argv.append(cstr(ptr) if RAMBASE <= ptr < IOBASE else ptr)
        self.handoff = dict(step=self.steps, pc=st.pc, psw=st.psw,
                            vb=st.vb, config=sy.config,
                            memsize=b.read(pp + 0x80),
                            fpi=b.read(pp + 0x74), argc=argc, argv=argv,
                            vectors=[b.read(pp + 4 * i) for i in range(16)])
        if self.kimg is not None:
            self.handoff["loaded"] = compare_loaded(self, self.kimg)
        return self.handoff

    def event_pc(self, pc):
        """An event's PC: kernel text by symbol, anything else raw (user
        processes run below VROMBASE)."""
        if VROMBASE <= pc < VROMBASE + ROM_BYTES:
            return self.syms.where(pc)
        return "0x%08x" % pc

    def _console(self):
        out = self.quart.ports[0]["out"]
        while self.script:
            wait, reply = self.script[0]
            at = out.find(wait, self.script_from)
            if at < 0:
                break
            self.script.pop(0)
            self.script_from = at + len(wait)
            self.typed.append((self.steps, wait, reply))
            self.quart.feed(self.console_channel, self.console_encode(reply))
        if self.until is not None and self.until in out[self.script_from:]:
            raise Stop("uart0 printed %r" % self.until)

    def run(self, max_steps, progress=0):
        st = self.state
        sysm = self.sysm
        status = "max-steps"
        port = self.quart.ports[0]
        seen_out = 0
        cur_lo = cur_hi = 0
        nextp = progress
        try:
            while self.steps < max_steps:
                pc = st.pc
                if not (cur_lo <= pc < cur_hi):
                    if st.psw & hobbit_sem.PSW_USER:
                        cur_lo, cur_hi, name = 0, VROMBASE, "user mode"
                    else:
                        if (self.handoff is None
                                and RAMBASE <= pc < IOBASE):
                            self.record_handoff()
                            if self.next_syms is None:
                                raise Stop("the ROM jumped to 0x%08x in "
                                           "RAM (gotopc)" % pc)
                            self.enter_kernel(self.next_syms)
                        v = pc + VROMBASE if pc < ROM_BYTES else pc
                        i = bisect.bisect_right(self.syms.addrs, v) - 1
                        if i < 0:
                            raise Stop("kernel PC 0x%08x below the "
                                       "kernel's text" % pc)
                        lo = self.syms.addrs[i]
                        hi = (self.syms.addrs[i + 1]
                              if i + 1 < len(self.syms.addrs) else MASK32)
                        off = v - pc
                        cur_lo, cur_hi = lo - off, hi - off
                        name = self.syms.names[i]
                    if name not in self.seen:
                        self.seen.add(name)
                        self.reached.append((self.steps, name))
                hook = self.watch.get(pc)
                if hook is not None:
                    hook(self)
                rec, st = hobbit_sem.step(st)
                self.state = st
                self.steps += 1
                self.cycles += rec.cyc
                if (st.psw >> 12) & 7 == 7 and self.irq.asserted():
                    hobbit_sem.take_interrupt(st, 6)
                    self.interrupts += 1
                    del sysm.events[:]
                elif st.pc == self.idle_head and self.idle_skip:
                    self.try_idle_skip(max_steps)
                if sysm.events:
                    for kind, ident, epc in sysm.events:
                        self.nevents += 1
                        if self.nevents <= 40:
                            print("p9rom: step %d: %s 0x%x at %s %s" % (
                                self.steps, kind, ident, self.event_pc(epc),
                                rec.reason if rec.trap else ""),
                                file=sys.stderr)
                    del sysm.events[:]
                w = self.wire
                if w is not None:
                    if w.inbound and w.inbound[0][0] <= self.cycles:
                        self.sonic.poll()
                    if (w.sock is not None
                            and self.steps % p9boot.PEER_POLL == 0):
                        w.poll_peer(0.0, self.cycles / float(p9boot.CPU_HZ))
                if len(port["out"]) != seen_out:
                    seen_out = len(port["out"])
                    self._console()
                if progress and self.steps >= nextp:
                    nextp += progress
                    print("p9rom: %d steps at %s, model time %.3f s" % (
                        self.steps, self.where(st.pc),
                        self.cycles / float(p9boot.CPU_HZ)),
                        file=sys.stderr)
        except hobbit_sem.BusError as exc:
            status = "BUS ERROR at %s (pc %08x): %s" % (
                self.where(st.pc), st.pc, exc)
        except hobbit_sem.Refusal as exc:
            status = "REFUSED at %s (pc %08x, parcels %s): %s" % (
                self.where(st.pc), st.pc,
                " ".join("%04x" % p for p in exc.parcels), exc.reason)
        except Stop as exc:
            status = "STOP at %s (pc %08x): %s" % (self.where(st.pc),
                                                  st.pc, exc)
        return status


def compare_loaded(r, k):
    """RAM at the image's text and data addresses against the image's
    words (taken at the hand-off; text words as zl wrote them)."""
    blob = k["blob"]
    bad = []
    for base, off, n in ((k["textbase"], k["text_off"], k["text"]),
                         (k["database"], k["data_off"], k["data"])):
        for i in range(0, n - 3, 4):
            if r.board.read(base + i) != int.from_bytes(
                    blob[off + i:off + i + 4], "little"):
                bad.append(base + i)
    return ("text %d and data %d bytes equal" % (k["text"], k["data"])
            if not bad else "%d words differ, first at 0x%08x"
            % (len(bad), bad[0]))


def unescape(text):
    return text.encode("latin-1").decode("unicode_escape").encode("latin-1")


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("image", nargs="?", default=str(ROM9))
    ap.add_argument("--max-steps", type=int, default=20_000_000)
    ap.add_argument("--memsize", type=int, default=p9boot.MEMSIZE)
    ap.add_argument("--no-mirror", action="store_true",
                    help="RAM above MEMSIZE is a bus error")
    ap.add_argument("--strict-rom", action="store_true",
                    help="stop at a read of the ROM past the image")
    ap.add_argument("--nvram", help="2040-byte NVRAM image")
    ap.add_argument("--save-nvram", help="write the NVRAM here at the end")
    ap.add_argument("--until", help="stop when uart0 prints this")
    ap.add_argument("--type", action="append", default=[],
                    metavar="WAIT=REPLY")
    ap.add_argument("--progress", type=int, default=0)
    ap.add_argument("--join", metavar="OUT", help="boot the 1e file server "
                    "in QEMU (tools/p9join.py's start_server, lockstep "
                    "ServerClock) and put the SONIC on its wire; writes "
                    "OUT/{hobbit.pcap,server.pcap,server.log,uart0}")
    ap.add_argument("--ports", default="10931,10932", metavar="SERVER,HOBBIT",
                    help="--join: the wire's UDP ports (not p9join's "
                    "defaults, so a concurrent p9join run is not hit)")
    ap.add_argument("--free-run", action="store_true",
                    help="--join: the server on the wall clock")
    ap.add_argument("--kernel", help="after gotopc, go on with this "
                    "image's symbols (the file `b` loaded) instead of "
                    "stopping; the hand-off is checked against it")
    ap.add_argument("--no-idle-skip", action="store_true",
                    help="execute every lap of runproc's idle loop "
                    "(ROM_CHOICES['idle-skip'])")
    ap.add_argument("--milestones", action="store_true",
                    help="print every function reached first, in order")
    a = ap.parse_args(argv)
    nv = pathlib.Path(a.nvram).read_bytes() if a.nvram else None
    r = RomRun(a.image, a.memsize, not a.no_mirror, nv,
               strict_rom=a.strict_rom)
    r.idle_skip = not a.no_idle_skip
    if a.until:
        r.until = unescape(a.until)
    for t in a.type:
        w, _, rep = t.partition("=")
        r.script.append((unescape(w), unescape(rep)))
    kimg = None
    if a.kernel:
        kimg = p9exec.read_kernel(a.kernel)
        r.next_syms = p9boot.Symbols(p9exec.kernel_symbols(kimg))
        r.kimg = kimg
    srv = clock = None
    if a.join:
        import p9join
        os.makedirs(a.join, exist_ok=True)
        ps, ph = (int(x) for x in a.ports.split(","))
        srv = p9join.start_server(a.join, ["-icount", "shift=4"], ps, ph)
        wire = p9boot.Wire(r.sonic.clock,
                           pcap=os.path.join(a.join, "hobbit.pcap"),
                           peer="127.0.0.1:%d" % ps,
                           local="127.0.0.1:%d" % ph)
        if not a.free_run:
            clock = p9join.ServerClock(srv, os.path.join(p9join.Q, "9dos.q"))
            clock.attach(0.0)
            wire.peer_clock = clock
        r.attach(wire)
    try:
        status = r.run(a.max_steps, a.progress)
    finally:
        if srv is not None:
            if clock is not None:
                clock.cont()
            try:
                print("--- server screen\n" + srv.screen().rstrip())
            finally:
                srv.quit()
    print("p9rom: %s" % status)
    if r.wire is not None:
        print("p9rom: %d frames" % len(r.wire.log))
        for t, way, frame in r.wire.log[:40]:
            print("  %.6f %s %s" % (t, way, p9boot.decode_frame(frame)))
    if r.handoff is not None:
        h = r.handoff
        print("p9rom: hand-off at step %d: pc 0x%08x psw 0x%x vb 0x%x "
              "config 0x%x; PPage0 memsize 0x%x fpi 0x%08x argc %d argv %r"
              % (h["step"], h["pc"], h["psw"], h["vb"], h["config"],
                 h["memsize"], h["fpi"], h["argc"], h["argv"]))
        if kimg is not None:
            print("p9rom: loaded image vs %s (at the hand-off): %s" % (
                a.kernel, h["loaded"]))
    if a.join:
        with open(os.path.join(a.join, "uart0"), "wb") as f:
            f.write(r.uart(0))
    print("p9rom: %d instructions (%d of them idle laps retired by %d "
          "skips), %d interrupts, model time %.3f s" % (
              r.steps, r.skipped_steps, r.skips, r.interrupts,
              r.cycles / float(p9boot.CPU_HZ)))
    if a.milestones:
        for s, n in r.reached:
            print("p9rom:   %10d  %s" % (s, n))
    for st, w, rep in r.typed:
        print("p9rom: typed %r at step %d after %r" % (rep, st, w))
    if r.rom.past:
        print("p9rom: %d read(s) of the ROM past the image, first at "
              "0x%08x" % (len(r.rom.past), r.rom.past[0]))
    print("p9rom: memsize (PPage0+0x80) = 0x%x" % r.board.read(RAMBASE + 0x80))
    out = r.uart(0)
    print("p9rom: uart0 %d bytes:" % len(out))
    sys.stdout.write(out.decode("latin-1"))
    print()
    if a.save_nvram:
        pathlib.Path(a.save_nvram).write_bytes(bytes(r.rtc.nvram))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
