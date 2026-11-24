#!/usr/bin/env python3
"""tools/p9boot.py boots the shipped kernel image s9term on the reference
model as far as its first console line (docs/p9boot.md).

The run is deterministic: the same instructions, the same order of first
reaches, the same bytes.  This pins the start of the boot -- `_startup`'s
physical-mode set-up and CRET into virtual mode, `main` through
`mmuinit` and `pageinit`, and the line pageinit prints on the screen
(the `screenputs` tap) and on Quart channel 0 (the kernel's printq) --
about 2.6 million instructions, 25-30 s.  The longer run, to the boot
program's prompt, is the recorded command in docs/p9boot.md.

Discriminating checks, observed 2026-11-23 (each injection one edit,
reverted by the reverse edit, the file's sha256 checked equal):

* sem: PX ignored (16-bit absolutes zero-extended): ERROR
  test_milestones_in_order, FAIL test_instruction_count, test_mmu_state,
  test_no_events_before_the_line, test_stops_at_the_first_line (the
  run stops in _startup).
* sem: ``State.csp`` always SP: ERROR test_milestones_in_order, FAIL
  test_instruction_count, test_mmu_state, test_stops_at_the_first_line.
* p9boot: MEMSIZE 16 MB in ppage0: FAIL test_instruction_count,
  test_stops_at_the_first_line (pageinit prints other numbers).

The idle skip (CHOICES['idle-skip']; IdleSkipEquivalenceTest, PromptTest),
observed 2026-11-23, each injection made in a scratch copy of
tools/p9boot.py (the real file untouched):

* skip one lap too many (N = floor(...) + 1, the guard that keeps the
  last skipped lap before the event removed): FAIL test_same_run
  (cycles 3757855 != 3757854), test_prompt (22530558 != 22530554),
  test_mostly_idle.
* retire the skipped laps' cycles but not their instructions (steps not
  advanced): FAIL test_same_run (cycles), test_the_skip_was_taken (1816
  skips, not 7), test_prompt (2957466 instructions).

Console input (CHOICES['console-input']; the typed byte in
IdleSkipEquivalenceTest, KeyboardTest), observed 2026-11-23, same method:

* the idle skip ignores pending input (Quart.next_event without the
  receive line): FAIL test_same_run (the functions reached differ:
  kbdcr2nl at 2,971,368 instead of 2,954,365); KeyboardTest stays green
  (the reply is late, but the prompt was not idle).
* every character takes 1 s on the line: FAIL test_the_byte_arrived
  (0 != 1), test_the_skip_was_taken (490000 != 450896),
  test_typed_and_taken (307,168,375 instructions).
* the console on channel 2, as the shipped screen.c's kbdinit(2) would
  have it: FAIL test_the_byte_arrived, test_the_skip_was_taken (8
  skips), test_typed_and_taken (max-steps: /boot never gets a byte).
* (Not used: cir never reporting RxAvail leaves s9term's `interrupt()`
  polling a request nobody clears -- a hang, not a failure.)

EEPROM and SONIC (IIC_CHOICES, SONIC_CHOICES; NetworkTest), observed
2026-11-23, same method:

* CAM address bytes taken high byte first: FAIL test_sonic_set_up only
  (the BOOTP request is a broadcast, so it still goes out).
* the SONIC's DMA reading the packet in the other byte-lane order: FAIL
  test_bootp_request only (destination ff ff ff ff 54 52).
* the PCF8584's first read after the address returning data, not the
  dummy byte: FAIL test_bootp_request, test_console ("sonic ether: 54 00
  00 0b 0b 00"), test_eeprom_read, test_sonic_set_up.

The Quart's FIFOs and interrupt bids (QuartBidTest; the SC68C94 1994
spec, docs/devices/README.md), observed 2026-11-24, each injection in a
scratch copy of tools/p9boot.py (build/gfx/inject.py):

* the first pending bid wins, not the largest: FAIL
  test_rx_against_tx_and_counter (0x15 where the transmitter's 0x78 wins).
* RX_FIFO back at 3: FAIL test_rx_against_tx_and_counter (0x78: the
  receiver holds 3 and bids 0x6C, below the transmitter).
* the counter on channel a/c (0x14/0x16): FAIL both tests.
* the transmitter bidding with no free count (0x08|ch): FAIL
  test_rx_against_tx_and_counter (the counter's 0x15 wins).

CRET with MSP > SP + 256 (CHOICES['cret-msp']; NoServerTest), observed
2026-11-23: p9boot not setting System.cret_clamp: FAIL
test_ten_requests_then_the_prompt only, the run REFUSED at _cret+0x0
("CRET restores SP=0x7ffff680 MSP=0x7ffff7f0, outside SP <= MSP <=
SP+256") on the first alarm note's return.

The join replay (JoinReplayTest; SONIC receive, CHOICES['rtc'],
console input at rc's prompt).  Against tests/net/join_echo.pcap,
observed 2026-11-23, each injection made in a scratch copy of
tools/p9boot.py (build/a5/inj/{A,B,C}; the real file untouched), the
class run alone:

* console input upper-cased by Quart.feed (only `echo hello` has
  letters; the boot answers are CRs): FAIL test_every_frame_as_recorded
  (model frame 266 differs: rc's 9P walk of `ECHO` where the recording
  has `echo`), FAIL test_init_rc_and_echo (max-steps);
  test_bootp_reply_and_time stays green.
* the receive descriptor's byte count without the 4 FCS bytes
  (etherkproc subtracts 4, so every frame is cut short): FAIL
  test_every_frame_as_recorded (model frame 1: the BOOTP request sent
  again where the recording has the ARP), FAIL test_init_rc_and_echo
  (max-steps), ERROR test_bootp_reply_and_time (the RTC never set).
* the timekeeper's load taking mday and month swapped: FAIL
  test_bootp_reply_and_time only ("1993-03-01 12:00:48").

Against the earlier tests/net/join_init.pcap (to `init: starting`, the
same class then), also observed 2026-11-23: Lpkt not reading the next
receive resource (frames overwrite one buffer) failed all three, model
frame 2 differing.

Not covered by this test (each left it green): the nonpaged STE base
ignored (the kernel's segments are identity-mapped), the stack cache on
with CONFIG.SE = 0, and the Quart sr never showing TxRDY (the UART line
comes after the stop).  test_sem_system.py covers the first two.
"""

import os
import sys
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HOBBIT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HOBBIT, "tools"))

import p9boot  # noqa: E402

S9TERM = os.path.join(HOBBIT, "tools", "plan9-1e", "hobbit", "s9term")
JOIN_PCAP = os.path.join(HERE, "net", "join_echo.pcap")
LINE = (b"1364 free pages, 5456K bytes, swap 27856K, highwater 272K, "
        b"headroom 340K\n")
FRAME = b"\xff" * 6 + b"\x02\x00\x00\x00\x00\xfe\x08\x06" + bytes(46)
PROMPT = b"root is from (il, tcp, incon, 9600, 19200)[il]: "
ETHERLINE = b"sonic ether: 52 54 00 00 0b 0b\n"


class QuartBidTest(unittest.TestCase):
    """QUART_CHOICES['cir'] and ['sr'] against the SC68C94 1994 product
    specification (docs/devices/README.md "Quart"): the numerically
    largest bid wins; a receiver with n bytes bids (n<<5)|0x0C|ch, an
    empty transmitter 0x78|ch, the counter 0x15/0x17; FIFOs 8 deep.
    Pure Python, no boot."""

    def quart(self):
        self.t = 0.0
        q = p9boot.Quart(25, lambda: self.t)
        for ch in range(4):
            q.ports[ch].update(csr=0xCC, mr=[0x13, 0x07], rx=True)
        return q

    def latch(self, q):
        q.write(0x2A * 4, 0, 0xF)
        return q.glob["cir"], q.glob["gicr"], q.glob["gibcr"]

    def test_rx_against_tx_and_counter(self):
        q = self.quart()
        q.duarts[0]["imr"] = 0x0A | 0x01     # RxRDYa, CtrRDY, TxRDYa
        q.duarts[0].update(acr=0xF0, ctu=0, ctl=1, running=True,
                           next_tick=0.0)
        self.assertEqual(self.latch(q), (0x15, 1, 0))   # counter alone
        q.ports[0]["tx"] = True
        self.assertEqual(self.latch(q), (0x78, 0, 7))   # tx beats counter
        q.feed(0, b"ab")
        self.t = 1.0
        self.assertEqual(self.latch(q), (0x78, 0, 7))   # tx beats rx (2)
        q.feed(0, b"cdefghij")
        self.t = 2.0
        self.assertEqual(self.latch(q), (0xEC, 0, 7))   # rx (8, as 7) wins
        self.assertEqual(len(q.ports[0]["fifo"]), 8)    # 8 deep
        self.assertEqual(bytes(q.ports[0]["pending"]), b"ij")
        self.assertEqual(q.read(1 * 4) & 0x02, 0x02)    # sr FFULL at 8

    def test_counter_of_duart_cd(self):
        q = self.quart()
        q.duarts[1]["imr"] = 0x08
        q.duarts[1].update(acr=0xF0, ctu=0, ctl=1, running=True,
                           next_tick=0.0)
        self.assertEqual(self.latch(q), (0x17, 3, 0))


class FirstLineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.boot = p9boot.Boot(S9TERM)
        cls.boot.until = b"\n"
        cls.status = cls.boot.run(4000000)

    def test_stops_at_the_first_line(self):
        self.assertIn("screenputs printed", self.status)
        self.assertEqual(bytes(self.boot.console["screenputs"]), LINE)

    def test_milestones_in_order(self):
        names = [n for _, n in self.boot.reached]
        order = ["_startup", "_virtual", "main", "confinit", "printinit",
                 "eiasetup", "screeninit", "mmuinit", "pageinit", "print",
                 "screenputs"]
        pos = [names.index(n) for n in order]
        self.assertEqual(pos, sorted(pos))
        # _startup is physical; _virtual is the first instruction after
        # the CRET that turns on the MMU (raml.s).
        self.assertEqual(self.boot.reached[0], (0, "_startup"))
        self.assertEqual(self.boot.reached[1], (STEPS["_virtual"],
                                                "_virtual"))
        self.assertEqual(dict((n, s) for s, n in self.boot.reached)["main"],
                         STEPS["main"])

    def test_instruction_count(self):
        self.assertEqual(self.boot.steps, STEPS["first-line"])

    def test_no_events_before_the_line(self):
        self.assertEqual(self.boot.exceptions, [])
        self.assertEqual(self.boot.interrupts, 0)

    def test_mmu_state(self):
        st = self.boot.state
        sysm = self.boot.sysm
        # mmuinit's mmusetstb(PADDR(KSTBADDR)) with STB_C.
        self.assertEqual(sysm.stb, 0x80001800)
        self.assertEqual(sysm.config, 0x003F0000)
        self.assertEqual(st.vb, 0x80000000)
        self.assertTrue(st.psw & p9boot.hobbit_sem.PSW_VIRTUAL)


class IdleSkipEquivalenceTest(unittest.TestCase):
    """CHOICES['idle-skip'] retires whole idle-loop laps without executing
    them; the run must be the run without the skip, instruction for
    instruction.  A counter period of 4 ms puts seven clock interrupts
    into the first 3.4 M instructions (the idle loop starts at ~2.9 M),
    and a byte typed 50 ms after pageinit's line arrives on Quart channel
    0 during the first idle stretch (0.1656 s), so a skip has to stop for
    it as well (CHOICES['console-input'])."""

    @classmethod
    def setUpClass(cls):
        cls.runs = []
        for skip in (False, True):
            boot = p9boot.Boot(S9TERM)
            boot.quart.period_override = 0.004
            boot.idle_skip = skip
            boot.script = [(b"headroom 340K\n", b"x")]
            boot.think = 0.05
            boot.attach(p9boot.Wire(boot.sonic.clock,
                                    script=[(0.175, FRAME)]))
            status = boot.run(3400000)
            cls.runs.append((boot, status))

    def summary(self, boot, status):
        st = boot.state
        return dict(status=status, steps=boot.steps, cycles=boot.cycles,
                    pc=st.pc, psw=st.psw, sp=st.sp, isp=st.isp,
                    interrupts=boot.interrupts, exceptions=boot.exceptions,
                    reached=boot.reached, ram=sorted(boot.board.ram.items()),
                    console=dict(boot.console),
                    quart=repr(boot.quart.duarts))

    def test_same_run(self):
        (plain, s0), (skipped, s1) = self.runs
        a, b = self.summary(plain, s0), self.summary(skipped, s1)
        for key in a:
            self.assertEqual(a[key], b[key], key)

    def test_the_skip_was_taken(self):
        plain, skipped = self.runs[0][0], self.runs[1][0]
        self.assertEqual(plain.skipped_steps, 0)
        self.assertEqual(skipped.skips, 8)
        self.assertEqual(skipped.skipped_steps, IDLE["equiv-skipped"])
        self.assertEqual(plain.interrupts, 8)

    def test_the_frame_arrived(self):
        for boot, _ in self.runs:
            # etherattach has not enabled the receiver yet.
            self.assertEqual([(t, o) for t, _, o in boot.sonic.received],
                             [(IDLE["frame-time"], "receiver off")])

    def test_the_byte_arrived(self):
        for boot, _ in self.runs:
            self.assertEqual(boot.quart.ports[0]["received"], 1)
            self.assertEqual(bytes(boot.console["screenputs"]), LINE + b"x")


class PromptTest(unittest.TestCase):
    """To /boot's prompt with the 25 Hz override, in ~30 s with the idle
    skip.  Before the EEPROM answered (CHOICES['iic'] then), this run took
    22,530,554 instructions both without the skip (6 minutes) and with it
    (29 s); reading the EEPROM in iicreset adds 6,535 (22,537,089).  Since
    2026-11-24 an exception's record costs Table 4-36's 9 + D + A, not 0:
    22,537,005 (the clock runs ahead, the idle loop is left sooner);
    22,537,007 with the Quart bids of the same day as well."""

    @classmethod
    def setUpClass(cls):
        cls.boot = p9boot.Boot(S9TERM)
        cls.boot.quart.period_override = 0.04
        cls.boot.until = b"root is from"
        cls.status = cls.boot.run(30000000)

    def test_prompt(self):
        self.assertIn("screenputs printed", self.status)
        self.assertEqual(self.boot.steps, STEPS["prompt"])
        self.assertEqual(self.boot.cycles, IDLE["prompt-cycles"])
        self.assertEqual(self.boot.interrupts, 26)
        self.assertEqual(bytes(self.boot.console["screenputs"]),
                         LINE + PROMPT)

    def test_mostly_idle(self):
        self.assertEqual(self.boot.skipped_steps, IDLE["prompt-skipped"])


class NetworkTest(unittest.TestCase):
    """Return typed at /boot's prompt on the console line, Quart channel 0
    (CHOICES['console-input']): kbdcr2nl makes it NL, it is echoed, and
    /boot takes its default, il.  iicreset has read the EEPROM
    (IIC_CHOICES), etherattach prints its address, and /boot broadcasts
    BOOTP through the SONIC (SONIC_CHOICES): the first frame on the wire
    ends the run."""

    @classmethod
    def setUpClass(cls):
        cls.boot = p9boot.Boot(S9TERM)
        cls.boot.script = [(b"il]: ", b"\r")]
        cls.boot.attach(p9boot.Wire(cls.boot.sonic.clock))
        cls.boot.until_frames = 1
        cls.status = cls.boot.run(400000000)

    def test_console(self):
        boot = self.boot
        self.assertIn("1 frames on the wire", self.status)
        self.assertEqual(boot.quart.ports[0]["received"], 1)
        self.assertEqual(bytes(boot.console["screenputs"]),
                         LINE + PROMPT + b"\n" + ETHERLINE)
        names = [n for _, n in boot.reached]
        for name in ("kbdcr2nl", "echo", "etherattach", "etherkproc",
                     "eepromread"):
            self.assertIn(name, names)
        self.assertEqual(boot.steps, STEPS["bootp"])

    def test_bootp_request(self):
        t, way, f = self.boot.wire.log[0]
        self.assertEqual(way, "tx")
        self.assertEqual(f[:6], b"\xff" * 6)
        self.assertEqual(f[6:12], p9boot.EEPROM_EA)
        self.assertEqual(f[12:14], b"\x08\x00")
        ip = f[14:34]
        self.assertEqual(p9boot.ip_checksum(ip), 0)
        self.assertEqual((ip[9], ip[12:16], ip[16:20]),
                         (17, b"\0\0\0\0", b"\xff\xff\xff\xff"))
        udp = f[34:42]
        self.assertEqual(udp[:4], b"\x00\x44\x00\x43")   # 68 > 67
        bootp = f[42:]
        self.assertEqual(bootp[:3], b"\x01\x01\x06")
        self.assertEqual(bootp[28:34], p9boot.EEPROM_EA)
        self.assertEqual(bootp[236:240], b"p9  ")
        self.assertEqual(len(f), 14 + 20 + 372)   # UDP length 372

    def test_eeprom_read(self):
        boot = self.boot
        ee = boot.syms.by_name["eeprom"]
        got = bytes(boot.board.byte(ee + i) for i in range(17))
        self.assertEqual(got, p9boot.eeprom_image()[:17])
        self.assertEqual(got[11:13], b"\x00\x14")       # mask, clock 20

    def test_sonic_set_up(self):
        sonic = self.boot.sonic
        self.assertEqual(sonic.cam, {0: p9boot.EEPROM_EA})
        self.assertEqual(sonic.regs[sonic.CE], 1)
        self.assertEqual(sonic.regs[sonic.RCR], 0xE000)
        self.assertEqual(sonic.regs[sonic.IMR], 0x7771)
        self.assertTrue(sonic.regs[sonic.CR] & sonic.RXEN)


class NoServerTest(unittest.TestCase):
    """/boot with nobody answering (a Wire with no peer): sys/src/9/boot's
    BOOTP loop sends its request ten times, an alarm note interrupting
    each wait, then asks for the address by hand.  Each note's return
    is a CRET with MSP more than 256 above SP (notify() lowers the user
    SP by 0x170 and keeps MSP): CHOICES['cret-msp']."""

    @classmethod
    def setUpClass(cls):
        cls.boot = p9boot.Boot(S9TERM)
        cls.boot.script = [(b"il]: ", b"\r")]
        cls.boot.attach(p9boot.Wire(cls.boot.sonic.clock))
        cls.boot.until = b"My IP address"
        cls.status = cls.boot.run(3200000000)

    def test_ten_requests_then_the_prompt(self):
        boot = self.boot
        self.assertIn("My IP address", self.status)
        self.assertTrue(bytes(boot.console["screenputs"]).endswith(
            ETHERLINE + b"My IP address[0.0.0.0]: "))
        log = boot.wire.log
        self.assertEqual([way for _, way, _ in log], ["tx"] * 10)
        # the same request but for the IP id (1..10) and header checksum
        frames = [f for _, _, f in log]
        self.assertEqual({f[:18] + f[20:24] + f[26:] for f in frames},
                         {frames[0][:18] + frames[0][20:24] + frames[0][26:]})
        self.assertEqual([f[18] << 8 | f[19] for f in frames],
                         list(range(1, 11)))
        self.assertTrue(all(p9boot.ip_checksum(f[14:34]) == 0
                            for f in frames))
        # a 1 s alarm is 25 ticks: 14.2 s at the default counter rate
        # (CHOICES['clock']: 0xFFFF counts, 0.569 s a tick)
        gaps = [b[0] - a[0] for a, b in zip(log, log[1:])]
        self.assertTrue(all(14.0 < g < 14.5 for g in gaps), gaps)
        self.assertEqual(boot.sysm.cret_clamps, 10)
        self.assertEqual(boot.steps, STEPS["no-server"])


class JoinReplayTest(unittest.TestCase):
    """The join with the 1e file server in QEMU and the first command at
    rc's prompt, replayed (ETHER_CHOICES['replay']).
    tests/net/join_echo.pcap is the first 615 frames of the --pcap of a
    live tools/p9join.py run of 2026-11-23 (lockstep, -icount 4; the
    whole run is docs/p9boot.md "Commands at rc's prompt"): BOOTP
    answered by the server's ip/bootp (10.9.0.2, fs/auth/gw 10.9.0.1,
    bootf /hobbit/s9term), ARP, IL to il!10.9.0.1!17008, nop, session,
    attach as none, the time from the root's access time (written to the
    timekeeper, CHOICES['rtc']), /hobbit/init from the server, termrc and
    /usr/none's empty profile, init's restart of rc, its prompt, and
    `echo hello` typed on the console and run.  The replay re-runs the
    model and delivers the server's recorded frames at their recorded
    cycle offsets from the model frame they followed; every frame the
    model sends must equal the recording byte for byte.  ~3 min of CPU
    (it replaced the run to `init: starting` of tests/net/join_init.pcap,
    the first live join, ~1 min, which is kept as a record)."""

    @classmethod
    def setUpClass(cls):
        cls.boot = p9boot.Boot(S9TERM)
        cls.boot.script = [(b"il]: ", b"\r"), (b"user[none]: ", b"\r"),
                           (b"% ", b"echo hello\r")]
        cls.replay = p9boot.Replay(JOIN_PCAP, p9boot.EEPROM_EA)
        cls.boot.attach(p9boot.Wire(cls.boot.sonic.clock,
                                    replay=cls.replay))
        cls.boot.until = b"% echo hello\nhello\n% "
        cls.status = cls.boot.run(STEPS["echo"] + 1000000)

    def test_init_rc_and_echo(self):
        boot = self.boot
        self.assertIn("echo hello", self.status)
        self.assertTrue(bytes(boot.console["screenputs"]).endswith(
            b"\nuser[none]: \narp: rcvd for 10.9.0.1\n"
            b"nop...session...time...\ninit: starting /bin/rc\n"
            b"\ninit: starting /bin/rc\n% echo hello\nhello\n% "))
        self.assertEqual([s for s, _w, _r in boot.typed],
                         [286977111, 288647258, 711874390])
        self.assertEqual(boot.steps, STEPS["echo"])

    def test_every_frame_as_recorded(self):
        self.assertIsNone(self.replay.mismatch)
        self.assertEqual(self.boot.sysm.cret_clamps, 0)
        self.assertEqual(self.replay.pos, len(self.replay.steps))
        recorded = p9boot.read_pcap(JOIN_PCAP)
        self.assertEqual([f for _, _, f in self.boot.wire.log],
                         [f for _, f in recorded])
        self.assertEqual(
            [o for _, _, o in self.boot.sonic.received],
            ["received"] * sum(1 for _, w, _ in self.boot.wire.log
                               if w == "rx"))

    def test_bootp_reply_and_time(self):
        rx = [f for _, w, f in self.boot.wire.log if w == "rx"]
        self.assertIn(b"/hobbit/s9term", rx[0])
        self.assertIn(b"p9  255.255.255.0 10.9.0.1 10.9.0.1 10.9.0.1",
                      rx[0])
        (t, secs), = self.boot.rtc.sets
        self.assertEqual(time.strftime("%Y-%m-%d %H:%M:%S",
                                       time.gmtime(secs)),
                         "1993-01-03 12:00:48")


STEPS = {"_virtual": 2064, "main": 125203, "first-line": 2131084,
         "prompt": 22537007, "bootp": 287845682,
         "no-server": 3131202422, "echo": 715861422}
IDLE = {"equiv-skipped": 426968, "prompt-skipped": 19555620,
        "prompt-cycles": 22890757, "frame-time": 0.175}


if __name__ == "__main__":
    unittest.main()
