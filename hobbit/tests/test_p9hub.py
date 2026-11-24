#!/usr/bin/env python3
"""The Hobbit on the three-machine 1e network, replayed without QEMU
(docs/p9boot.md "On the 1e network"; docs/qemu_1e_server.md 5e).

tests/net/hub_cpu.pcap is the --pcap of a live `tools/p9join.py --hub`
run (fs9, cpu9 and the model on tools/qemu1e/hub.py, the lockstep over
both QEMUs; the command is in the doc): s9term boots from fs9, the user
glenda types a wrong password, which fs9's check service refuses
(`check: bad user response`, /boot asks `user[glenda]` again), then
glenda93, which it accepts (`check: user glenda ok`); at rc's prompt
`ip/ipconfig` (termrc's hobbit case starts no ARP answerer) and `cpu -h
cpu9`, authenticated by fs9's rexauth; on cpu9 `ls /mnt/term/hobbit`
(the Hobbit's name space, served back by its own exportfs), cat
/dev/sysname and /dev/user.  The replay re-runs the model and delivers
the network's recorded frames at their recorded cycle offsets from the
model frame they followed; every frame the model sends must equal the
recording byte for byte, so the key the model's /boot derives from the
password, its encrypted challenge response and the rexauth exchange are
all checked against what the live auth server accepted.

Injections, observed 2026-11-24 against the suite's run (to init), the
class run alone:

* console input upper-cased by Quart.feed (a scratch copy of
  tools/p9boot.py, build/hub/inj/A2; the real file untouched): FAIL
  test_every_frame_as_recorded (model frame 4 differs: check's response
  names GLENDA where the recording has glenda, and its encrypted
  challenge differs), FAIL test_refused_then_logged_in (`user[none]:
  GLENDA`, then nothing: the replay stops answering), FAIL test_steps
  (three lines typed of five).
* the wrong key: P9HUB_PASSWORD=glenda94 (the second password, the one
  check accepted, one character off): FAIL test_every_frame_as_recorded
  (model frame 11 differs: the second check response, user glenda, its
  8 encrypted challenge bytes not the recording's), FAIL
  test_refused_then_logged_in (no `nop...session...time...`: check's OK
  never comes), FAIL test_steps (409,307,318 steps: max-steps).

So the test checks the key the model derives from the typed password
(passtokey), its DES encryption of the server's challenge (#c/crypt),
and the console path that carries the password, against what fs9's
live check service accepted.
"""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HOBBIT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HOBBIT, "tools"))

import p9boot  # noqa: E402

S9TERM = os.path.join(HOBBIT, "tools", "plan9-1e", "hobbit", "s9term")
HUB_PCAP = os.environ.get("P9HUB_PCAP",
                          os.path.join(HERE, "net", "hub_cpu.pcap"))
GLENDA = os.environ.get("P9HUB_PASSWORD", "glenda93")
CMDS = (b"ls /mnt/term/hobbit; cat /dev/sysname; echo; cat /dev/user; "
        b"echo; echo end of cpu")


class HubReplayTest(unittest.TestCase):
    """glenda's refused and accepted log-ins, replayed to init (the
    suite's run); P9HUB_CPU=1 replays on through `ip/ipconfig`, `cpu -h
    cpu9` and the commands on cpu9 (STEPS["end"], ~8 min of host time on
    a loaded machine)."""

    FULL = os.environ.get("P9HUB_CPU") == "1"

    @classmethod
    def setUpClass(cls):
        cls.boot = p9boot.Boot(S9TERM)
        cls.boot.script = [
            (b"il]: ", b"\r"), (b"user[none]: ", b"glenda\r"),
            (b"password: ", b"wrongpw1\r"), (b"user[glenda]: ", b"\r"),
            (b"password: ", GLENDA.encode() + b"\r"),
            (b"% ", b"ip/ipconfig\r"), (b"% ", b"cpu -h cpu9\r"),
            (b"cpu9% ", CMDS + b"\r")]
        cls.replay = p9boot.Replay(HUB_PCAP, p9boot.EEPROM_EA)
        cls.boot.attach(p9boot.Wire(cls.boot.sonic.clock,
                                    replay=cls.replay))
        cls.boot.until = (b"\nend of cpu\n" if cls.FULL else
                          b"nop...session...time...\ninit: starting /bin/rc\n")
        cls.status = cls.boot.run(STEPS["end" if cls.FULL else "init"]
                                  + 1000000)
        cls.screen = bytes(cls.boot.console["screenputs"])

    def test_every_frame_as_recorded(self):
        self.assertIsNone(self.replay.mismatch)
        self.assertEqual(self.boot.sysm.cret_clamps, 0)
        self.assertEqual(self.replay.pos, len(self.replay.steps)
                         if self.FULL else FRAMES["init-tx"])
        recorded = p9boot.read_pcap(HUB_PCAP)
        log = [f for _, _, f in self.boot.wire.log]
        self.assertEqual(len(log), len(recorded) if self.FULL
                         else FRAMES["init"])
        self.assertEqual(log, [f for _, f in recorded][:len(log)])
        self.assertEqual(
            [o for _, _, o in self.boot.sonic.received],
            ["received"] * sum(1 for _, w, _ in self.boot.wire.log
                               if w == "rx"))

    def test_refused_then_logged_in(self):
        """check said NO to wrongpw1 (/boot asks the user again) and OK
        to glenda93; the auth dial did not fail."""
        self.assertIn(b"user[none]: glenda\npassword: \n"
                      b"arp: rcvd for 10.9.0.1\nuser[glenda]: \n"
                      b"password: \n", self.screen)
        self.assertNotIn(b"not checked", self.screen)
        self.assertIn(b"nop...session...time...\ninit: starting /bin/rc\n",
                      self.screen)

    def test_cpu_on_cpu9(self):
        if not self.FULL:
            self.skipTest("P9HUB_CPU=1")
        self.assertIn("end of cpu", self.status)
        self.assertTrue(self.screen.endswith(
            b"cpu9% " + CMDS + b"\n"
            b"/mnt/term/hobbit/bin\n/mnt/term/hobbit/include\n"
            b"/mnt/term/hobbit/init\n/mnt/term/hobbit/lib\n"
            b"/mnt/term/hobbit/mkfile\n/mnt/term/hobbit/s9term\n"
            b"cpu9\nglenda\nend of cpu\n"), self.screen[-400:])

    def test_steps(self):
        typed = [s for s, _w, _r in self.boot.typed]
        if self.FULL:
            self.assertEqual(typed, STEPS["typed"])
            self.assertEqual(self.boot.steps, STEPS["end"])
        else:
            self.assertEqual(typed, STEPS["typed"][:5])
            self.assertEqual(self.boot.steps, STEPS["init"])


# the live run's (build/hub/live4, 2026-11-24): the steps each line was
# typed at, init's first line, and the stop at `end of cpu`
STEPS = {"typed": [286977195, 288647338, 289407297, 313565409, 313927179,
                   1054675769, 1211181842, 1508419483],
         "init": 408307318, "end": 1580420168}
# at init's first line: frames on the wire, the model's among them
FRAMES = {"init": 197, "init-tx": 94}


if __name__ == "__main__":
    unittest.main()
