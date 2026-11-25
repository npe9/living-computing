#!/usr/bin/env python3
"""The 1st Edition boot ROM (docs/boot_rom.md).

* TestRomRule: p9kbuild's 9rom link line is the mkfile's `9rom` rule
  word for word, and TYPE=rom gives CFLAGS -w -Drom, rommain, roml.s,
  librom.a.
* TestMkrom: p9kbuild.mkrom (mkrom.c transcribed) on a made-up -H1
  image: text from offset 80 (libmach hobbitboot), each word's bytes
  b2 b3 b0 b1, data after the text, (text+data)%4 zero bytes.
* TestRomImage: the committed tools/p9kbuild/9rom is the recorded
  image; 9rom.com is mkrom of it; text+data fit the ROM's 64-page STE.
* TestRomBoot: tools/p9rom.py runs the committed 9rom from reset (PC 0,
  PSW 0, CONFIG 0) to romboot's `>>>` prompt on uart0, and the monitor
  answers `e` and `r` (see the class for what is checked).

* TestRomMemory: memsize follows the RAM fitted (4, 16 MB), and with no
  aliasing meminit takes a bus error at 0x80800080.
* TestRomJoinReplay (~100 s): `e fs il` and `b -s il /hobbit/s9term`
  against tests/net/rom_join.pcap, the wire of the live tools/p9rom.py
  --join run of 2026-11-24 (docs/boot_rom.md section 5, "third run";
  sha256 f74abe00196d2b00042e970234711635b3643692d275060d030c6f7bdd62bd0e),
  replayed (p9boot ETHER_CHOICES['replay']).  It checks the frames sent,
  the hand-off at step 281,845,240 (PC, PSW, VB, CONFIG, PPage0), RAM =
  the s9term file (p9rom.compare_loaded) plus three controls at the
  same hand-off that must differ, and s9term's first line on uart0.
* TestRomJoinToRc (P9ROM_LONG=1, ~6 min): the same replay on to rc's
  `% ` at 2,056,900,324 instructions, every recorded frame used.

Injections, each applied alone, the whole file run, then reverted by the
exact reverse replacement (file byte-identical afterwards); OBSERVED:

1. tools/p9rom.py RomImage loads the ROM words big-endian instead of
   little: ERROR setUpClass (TestRomBoot: the first fetch is refused,
   "ISP 0x00000000 cannot hold the 16-byte event frame"), FAIL
   test_no_mirror, FAIL test_sizes.
2. tools/p9kbuild.py mkrom writes b0 b1 b2 b3 (no half swap): FAIL
   test_header_is_not_in_the_rom, test_order_and_padding, test_com.
3. tools/p9rom.py MirrorBoard never folds (no aliasing): FAIL test_env,
   test_handoff_words, test_prompt, test_sizes.
4. MirrorBoard folds over device ranges too (the SONIC at 0xA4400000
   becomes RAM; etherreset's `while(sonic->cr & Rrra)` never ends):
   FAIL test_env, test_prompt, test_sizes (262 s: the runs go to their
   step limits).
5. tools/p9rom.py compare_loaded compares the text only (no data
   segment), TestRomJoinReplay alone: FAIL test_wrong_loads_are_caught
   only ('text 219968 and data 70388 bytes equal' for the flipped data
   word).
6. compare_loaded reads RAM 4 bytes above each word (a wrong load
   address), TestRomJoinReplay alone: FAIL test_loaded_image_is_the_file
   ('70240 words differ, first at 0x80004000') and
   test_wrong_loads_are_caught.
(5 and 6 by build/rom/inject2.py, the file's sha256 equal afterwards.)
7. one extra cycle after every idle-skip check in RomRun.run (the
   skipped path no longer the executed one), TestRomIdleSkip alone:
   FAIL test_same_run (713225 != 716845: the `e` reply comes out at a
   different instruction).
* TestRomIdleSkip (~20 s): ROM_CHOICES['idle-skip'] leaves the run to
  `>>>` and through `e` (716,845 instructions) the same in cycles, PC,
  PSW, uart0, interrupts and every RAM word as with the skip off.
"""

import hashlib
import os
import pathlib
import struct
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
HOBBIT = HERE.parent
sys.path.insert(0, str(HOBBIT / "tools"))
sys.path.insert(0, str(HOBBIT / "sem"))
import p9kbuild  # noqa: E402

ROM9 = HOBBIT / "tools" / "p9kbuild" / "9rom"


class TestRomRule(unittest.TestCase):
    def test_ld_line_is_the_mkfiles(self):
        mk = (p9kbuild.REL / "sys/src/9/hobbit/mkfile").read_text()
        rule = mk.split("\n9rom:", 1)[1].split("\n\n", 1)[0]
        ld = [ln.strip() for ln in rule.splitlines()
              if ln.strip().startswith("$LD")][0].split()
        subst = {"$target": "9rom", "roml.$O": "roml.z", "$CONF.$O":
                 "rom.z", "boot$CONF.root.$O": "bootrom.root.z",
                 "$LIBRARY": "librom.a"}
        want = [subst.get(w, w) for w in ld[1:]]
        got = (["-o", "9rom"] + p9kbuild.ROM_LINK_FLAGS +
               ["roml.z", "rom.z", "bootrom.root.z", "librom.a"] +
               p9kbuild.ROM_LINK_LIBS)
        self.assertEqual(got, want)
        self.assertEqual(rule.splitlines()[-1].strip(), "size 9$CONF")

    def test_type_rom(self):
        class A:
            conf, type = "rom", None
        self.assertEqual(p9kbuild.ktype(A), "rom")
        self.assertEqual(p9kbuild.cflags("rom"), ["-w", "-Drom"])
        objs = p9kbuild.kernel_objects("term", t="rom")
        self.assertIn("rommain", objs)
        self.assertNotIn("rammain", objs)
        A.conf = "term"
        self.assertEqual(p9kbuild.ktype(A), "ram")


def h1(text, data, textbase=0xC0000000, database=0xC0604000):
    w = [0x161 << 16, 0, 80 + len(text) + len(data), 0, (0x38 << 16) | 7,
         (407 << 16) | 0o437, len(text), len(data), 0, 0, textbase,
         database, database + len(data), 0xFFFFFFFF, 0, 0, 0, 0,
         0xFFFFFFFF, 0]
    return struct.pack(">20I", *w) + text + data


class TestMkrom(unittest.TestCase):
    def test_order_and_padding(self):
        text = bytes(range(8))
        data = bytes(range(0x10, 0x16))     # 6 bytes: 1 word + 2 left
        com = p9kbuild.mkrom(h1(text, data))
        self.assertEqual(com[:8], bytes([2, 3, 0, 1, 6, 7, 4, 5]))
        self.assertEqual(com[8:12], bytes([0x12, 0x13, 0x10, 0x11]))
        # the 2 trailing data bytes are dropped (segment(): whole groups
        # only) and (8+6)%4 = 2 zero bytes appended (mkrom.c:93)
        self.assertEqual(com[12:], bytes(2))

    def test_header_is_not_in_the_rom(self):
        com = p9kbuild.mkrom(h1(b"\x11\x22\x33\x44", b""))
        self.assertEqual(com, b"\x33\x44\x11\x22")


def _image():
    if not ROM9.exists():
        raise unittest.SkipTest("no %s" % ROM9)
    return ROM9.read_bytes()


class TestRomImage(unittest.TestCase):
    def test_recorded(self):
        self.assertEqual(hashlib.sha256(_image()).hexdigest(),
                         p9kbuild.NINEROM_SHA256)

    def test_com(self):
        _image()
        com = (ROM9.parent / "9rom.com").read_bytes()
        self.assertEqual(com, p9kbuild.mkrom(_image()))

    def test_fits(self):
        import p9exec
        _image()
        k = p9exec.read_kernel(str(ROM9))
        self.assertTrue(k["text"] + k["data"] <= p9kbuild.ROM_STE_BYTES)
        self.assertEqual(p9exec.check_kernel(
            k, p9exec.kernel_symbols(k), p9kbuild.ROM_DATA,
            p9kbuild.ROM_ENTRY), [])


BANNER = (b"200 free pages, 800K bytes, swap 800K, highwater 40K, headroom "
          b"48K\r\nHobbit ROM Sat Nov  7 04:28:37 GMT 1992\r\n>>>")
ENV = [("sysname", "hobbit"), ("station", "99"),
       ("bootfile", "/hobbit/9cpu"), ("bootmode", "d"),
       ("fs", "incon!nj/astro/Nfs")]


def env_of(nv):
    """rom.h Env: int nentry; uchar sum[4]; Entry{name[16] value[48]}[11]."""
    n = int.from_bytes(nv[0:4], "little")
    out = []
    for i in range(n):
        e = nv[8 + 64 * i:8 + 64 * (i + 1)]
        out.append((e[:16].split(b"\0")[0].decode(),
                    e[16:].split(b"\0")[0].decode()))
    return out


class TestRomBoot(unittest.TestCase):
    """The committed 9rom from reset to `>>>`, then `e` (~25 s)."""

    @classmethod
    def setUpClass(cls):
        _image()
        import p9rom
        r = p9rom.RomRun(ROM9)
        cls.first = []
        st = r.state
        import hobbit_sem
        for _ in range(2):          # the first two instructions
            pc = st.pc
            rec, st = hobbit_sem.step(st)
            cls.first.append((pc, rec.insn0, rec.insn1, st.pc))
        r.state, r.steps = st, 2
        k = r.k
        cls.data_at_main = None

        def at_main(run):
            if cls.data_at_main is None:
                base = 0x80000000 + (k["database"] - 0xC0400000)
                cls.data_at_main = b"".join(
                    run.board.read(base + 4 * i).to_bytes(4, "little")
                    for i in range((k["data"] + 3) // 4))[:k["data"]]
        r.watch[r.syms.by_name["main"]] = at_main
        r.until = b">>>"
        cls.status1 = r.run(5_000_000)
        cls.steps1 = r.steps
        cls.uart1 = r.uart(0)
        cls.fpi = r.board.read(0x80000074)
        cls.memsize = r.board.read(0x80000080)
        cls.past = list(r.rom.past)
        r.script = [(b">>>", b"e\r")]
        r.script_from = len(cls.uart1) - 3
        cls.status2 = r.run(20_000_000)
        cls.uart2 = r.uart(0)
        cls.nv = bytes(r.rtc.nvram)
        cls.r = r

    def test_reset_vector(self):
        # roml.s:13 JMP *$(PROMBASE+6): a three-parcel absolute jump to
        # the next instruction; then FLUSHP (2c04) at physical 6
        self.assertEqual(self.first[0], (0, 0x80F3, 0x0000, 6))
        self.assertEqual(self.first[1][:2], (6, 0x2C04))

    def test_prompt(self):
        self.assertIn("uart0 printed", self.status1)
        self.assertEqual(self.uart1, BANNER)
        self.assertEqual(self.steps1, 681566)

    def test_data_copied(self):
        k = self.r.k
        off = k["data_off"]
        want = bytearray(k["blob"][off:off + k["data"]])
        # roml.s:109-110 then set m and mach0 to MACHADDR before main
        for name in ("m", "mach0"):
            o = self.r.syms.by_name[name] - k["database"]
            want[o:o + 4] = (0xC0602000).to_bytes(4, "little")
        self.assertEqual(self.data_at_main, bytes(want))
        # _copy's last iteration reads one halfword past the data image
        self.assertEqual(self.past, [k["text"] + k["data"]])

    def test_handoff_words(self):
        self.assertEqual(self.memsize, 8 << 20)
        self.assertEqual(self.fpi, self.r.syms.by_name["fprt0"])

    def test_env(self):
        self.assertEqual(env_of(self.nv), ENV)
        want = b"".join(("%s=%s\r\n" % e).encode() for e in ENV)
        self.assertEqual(self.uart2, BANNER + b"e\r\n" + want + b">>>")


class TestRomMemory(unittest.TestCase):
    """meminit needs RAM to alias above its size (ROM_CHOICES)."""

    def test_sizes(self):
        _image()
        import p9rom
        for mb in (4, 16):
            r = p9rom.RomRun(ROM9, memsize=mb << 20)
            r.until = b">>>"
            self.assertIn("uart0 printed", r.run(5_000_000))
            self.assertEqual(r.board.read(0x80000080), mb << 20)

    def test_no_mirror(self):
        _image()
        import p9rom
        r = p9rom.RomRun(ROM9, mirror=False)
        st = r.run(5_000_000)
        self.assertIn("BUS ERROR at meminit", st)
        self.assertIn("0x80800080", st)


class TestRomIdleSkip(unittest.TestCase):
    def test_same_run(self):
        _image()
        import p9rom
        runs = []
        for skip in (True, False):
            r = p9rom.RomRun(ROM9)
            r.idle_skip = skip
            r.until = b">>>"
            r.run(5_000_000)
            r.script = [(b">>>", b"e\r")]
            r.script_from = len(r.uart(0)) - 3
            self.assertIn("uart0 printed", r.run(5_000_000))
            st = r.state
            runs.append((r.steps, r.cycles, st.pc, st.psw, r.uart(0),
                         r.interrupts, dict(r.board.ram), r.skipped_steps))
        on, off = runs
        self.assertEqual(on[0], 716845)
        self.assertEqual(on[:-1], off[:-1])
        self.assertEqual((on[-1], off[-1]), (18064, 0))


ROM_JOIN_PCAP = HERE / "net" / "rom_join.pcap"
S9TERM = HOBBIT / "tools" / "plan9-1e" / "hobbit" / "s9term"


def rom_join_replay(until, max_steps):
    """The ROM's `b` over IL, the server's frames replayed from
    tests/net/rom_join.pcap (p9boot ETHER_CHOICES['replay']).  At the
    hand-off it also runs p9rom.compare_loaded on two wrong loads, as
    controls: one RAM word of s9term's text, then one of its data, with
    a bit flipped, and the
    image placed 4 bytes higher than it was linked (r.controls)."""
    _image()
    import p9boot
    import p9exec
    import p9rom
    r = p9rom.RomRun(ROM9)
    kimg = p9exec.read_kernel(str(S9TERM))
    r.kimg = kimg
    r.next_syms = p9boot.Symbols(p9exec.kernel_symbols(kimg))
    r.script = [(b">>>", b"e fs il\r"),
                (b">>>", b"b -s il /hobbit/s9term\r"),
                (b"user[none]: ", b"\r")]
    replay = p9boot.Replay(str(ROM_JOIN_PCAP), p9boot.EEPROM_EA)
    r.attach(p9boot.Wire(r.sonic.clock, replay=replay))
    r.rom_fprt0 = r.syms.by_name["fprt0"]
    r.controls = {}
    record = r.record_handoff

    def record_and_controls():
        h = record()
        ram = r.board.ram
        for name, a in (("text", kimg["textbase"] + 0x1000),
                        ("data", kimg["database"] + 0x100)):
            ram[a] ^= 1
            r.controls[name] = p9rom.compare_loaded(r, kimg)
            ram[a] ^= 1
        shifted = dict(kimg, textbase=kimg["textbase"] + 4,
                       database=kimg["database"] + 4)
        r.controls["shifted"] = p9rom.compare_loaded(r, shifted)
        return h
    r.record_handoff = record_and_controls
    r.until = until
    status = r.run(max_steps)
    return r, replay, status


class TestRomJoinReplay(unittest.TestCase):
    """`e fs il`, then `b -s il /hobbit/s9term` against the 1e file
    server, replayed: the frames of the live run (docs/boot_rom.md
    section 5) up to the hand-off and s9term's first line.  Checks the
    frames the model sends against the recording, the hand-off state,
    and RAM at s9term's text and data against the file
    (p9rom.compare_loaded)."""

    @classmethod
    def setUpClass(cls):
        cls.r, cls.replay, cls.status = rom_join_replay(
            b"headroom 340K", HANDOFF_STEPS + 3_000_000)

    def test_handoff(self):
        h = self.r.handoff
        self.assertEqual((h["step"], h["pc"], h["psw"], h["vb"],
                          h["config"]),
                         (HANDOFF_STEPS, 0x80004000, 0, 0, 0x3F0000))
        self.assertEqual((h["memsize"], h["argc"], h["argv"]),
                         (8 << 20, 1, [b"b"]))
        self.assertEqual(h["fpi"], self.r.rom_fprt0)

    def test_loaded_image_is_the_file(self):
        self.assertEqual(self.r.handoff["loaded"],
                         "text 219968 and data 70388 bytes equal")

    def test_wrong_loads_are_caught(self):
        # the controls: the same comparison, the same RAM, a wrong load
        self.assertEqual(self.r.controls["text"],
                         "1 words differ, first at 0x80005000")
        self.assertEqual(self.r.controls["data"],
                         "1 words differ, first at 0x80039c40")
        self.assertEqual(self.r.controls["shifted"],
                         "70240 words differ, first at 0x80004004")

    def test_frames_as_recorded(self):
        self.assertIsNone(self.replay.mismatch)

    def test_s9term_first_line(self):
        self.assertIn("uart0 printed", self.status)
        self.assertTrue(self.r.uart(0).endswith(
            b"219968+70388+98476 entry: 0x80004000\r\n" + S9TERM_LINE))


@unittest.skipUnless(os.environ.get("P9ROM_LONG"),
                     "SKIPPED: P9ROM_LONG=1 replays the ROM's join on "
                     "to rc's prompt")
class TestRomJoinToRc(unittest.TestCase):
    """The same replay on to init and rc's `% ` prompt: every recorded
    frame used, and the console as the live run's."""

    @classmethod
    def setUpClass(cls):
        cls.r, cls.replay, cls.status = rom_join_replay(
            b"% ", RC_STEPS + 1_000_000)

    def test_rc_prompt(self):
        self.assertIn("uart0 printed", self.status)
        self.assertEqual(self.r.steps, RC_STEPS)
        self.assertTrue(self.r.uart(0).endswith(RC_TAIL))

    def test_every_frame(self):
        self.assertIsNone(self.replay.mismatch)
        self.assertEqual(self.replay.pos, len(self.replay.steps))


S9TERM_LINE = (b"1364 free pages, 5456K bytes, swap 27856K, highwater "
               b"272K, headroom 340K")
HANDOFF_STEPS = 281845240
RC_STEPS = 2056900324
RC_TAIL = (S9TERM_LINE + b"\r\nsonic ether: 52 54 00 00 0b 0b\r\nuser[none]: "
           b"\r\narp: rcvd for 10.9.0.1\r\nnop...session...time...\r\n"
           b"init: starting /bin/rc\r\n\r\ninit: starting /bin/rc\r\n% ")


if __name__ == "__main__":
    unittest.main()
