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

Not covered by this test (each left it green): the nonpaged STE base
ignored (the kernel's segments are identity-mapped), the stack cache on
with CONFIG.SE = 0, and the Quart sr never showing TxRDY (the UART line
comes after the stop).  test_sem_system.py covers the first two.
"""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HOBBIT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HOBBIT, "tools"))

import p9boot  # noqa: E402

S9TERM = os.path.join(HOBBIT, "tools", "plan9-1e", "hobbit", "s9term")
LINE = (b"1364 free pages, 5456K bytes, swap 27856K, highwater 272K, "
        b"headroom 340K\n")
FRAME = b"\xff" * 6 + b"\x02\x00\x00\x00\x00\xfe\x08\x06" + bytes(46)
PROMPT = b"root is from (il, tcp, incon, 9600, 19200)[il]: "
ETHERLINE = b"sonic ether: 52 54 00 00 0b 0b\n"


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
    (29 s); reading the EEPROM in iicreset adds 6,535 (22,537,089)."""

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


STEPS = {"_virtual": 2064, "main": 125203, "first-line": 2131084,
         "prompt": 22537089, "bootp": 287845754}
IDLE = {"equiv-skipped": 426976, "prompt-skipped": 19555708,
        "prompt-cycles": 22890721, "frame-time": 0.175}


if __name__ == "__main__":
    unittest.main()
