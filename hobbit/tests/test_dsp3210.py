#!/usr/bin/env python3
"""tools/dsp3210dis.py and tools/dsp3210.py, the Hobbit BeBox's DSP3210s
(docs/dsp3210.md).

Three parts.  The decoder tests pin the encodings to the manual's own
encoded examples (WE DSP3210 Information Manual, Sept 1991, section 4.6;
page numbers printed on the page).  The module tests disassemble Be's
DSP code from the Nov 1994 disk and skip, loudly, when the image (held
out of git: docs/bebox/MANIFEST.md) is absent; no Be or AT&T code is in
this file, only instruction words, addresses and short decoded texts.
The model tests run hand-encoded programs on a flat bus.

Discriminating checks, observed 2026-11-24 with the disk image present
(HOBBIT_9308000058 set).  Each injection is a text edit, reverted by the
exact reverse edit, with the file then compared byte for byte against its
copy from before.  Run with python -B: an injection of the same size
inside one second leaves a stale .pyc that Python trusts.  Observed
failures:

- dsp3210dis, branch dispatch back to `op >> 1 == 0` (the first draft's
  bug that made I/O-condition branches "reserved"):
  test_io_condition_branch.
- dsp3210dis, B and M of the do formats swapped:
  test_do_forms, test_os_boot_mover.
- dsp3210, the delayed branch made immediate (_branch calls _jump):
  test_call_return, test_dau_condition_latency, test_delayed_branch,
  test_loop_counter, test_os_boot_standalone, test_reset_release_run.
- dsp3210, the pc read as address + 4 instead of + 8: the same six.
- dsp3210, do-loop body one instruction short (end = start + 4*K):
  test_do_loop, test_os_boot_standalone.
- dsp3210, DA memory write committed at once (countdown 1, not 4):
  test_da_write_latency.
- dsp3210, DAU condition from the current flags (dflag_hist[-1]):
  test_dau_condition_latency.
- dsp3210, float_to_dsp's negative mantissa as sign-magnitude:
  test_float_format.
- dsp3210, SHIFT-OR keeping only rS's low half: test_shift_or.
- dsp3210, BRC=1 boot taking the address from header bytes 4-7: every
  test that boots the model (17), test_alu_flags .. test_wrapper.
- dsp3210, interrupt vector r22 + 8*(n-1):
  test_bio_and_irq, test_timer_interrupt.

Tried and not discriminating: doblock taking K from its field instead
of forcing 0.  Every doblock in the code has K = 0 encoded.
"""
import os
import struct
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HOBBIT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HOBBIT, "tools"))
import dsp3210  # noqa: E402
import dsp3210dis as dis  # noqa: E402
import befs1  # noqa: E402

DISK = os.environ.get("HOBBIT_9308000058") or os.path.join(
    HOBBIT, "build", "bebox", "hdd-hobbit-9308000058", "hobbit-9308000058.img")
FETCH = "sh hobbit/docs/bebox/fetch.sh"


def text(w, addr=0x100):
    return dis.decode(w, addr).text


# --------------------------------------------------------------- encoders
# Field packers for Table 10-1 (p. 10-1..10-2); register codes Table 10-2.
R = {"r%d" % i: i for i in range(15)}
R.update({"r%d" % (15 + i): 17 + i for i in range(5)})
R.update({"r20": 24, "r21": 25, "r22": 26, "pc": 15, "pcsh": 30, "-1": 22, "+1": 23})
COND = {"true": 1, "false": 0, "ne": 4, "eq": 5, "gt": 12, "lt": 11, "mi": 3,
        "vs": 7, "ibe": 32, "obe": 35, "alt": 19, "age": 18}


def br(cond, rb, n=0):                  # 0b
    return (1 << 31) | (COND[cond] << 21) | (R[rb] << 16) | (n & 0xFFFF)


def loopc(rm, rb, n):                   # 3a
    return (0b000011 << 26) | (R[rm] << 21) | (R[rb] << 16) | (n & 0xFFFF)


def do_imm(k, l):                       # 3b
    return (0b1000110 << 25) | (k << 11) | l


def call(rb, n, rm):                    # 4a
    return (0b000100 << 26) | (R[rm] << 21) | (R[rb] << 16) | (n & 0xFFFF)


def add3(rd, rs, n, long=True):         # 5a/5b
    return ((1 if long else 0) << 31) | (0b00101 << 26) | (R[rd] << 21) | (R[rs] << 16) | (n & 0xFFFF)


def alu(f, rd, rs1, rs2, cond="true", long=True):   # 6a/6b
    return ((1 if long else 0) << 31) | (0b001100 << 25) | (f << 21) | (R[rd] << 16) \
        | (R[rs1] << 11) | (COND[cond] << 5) | R[rs2]


def alui(f, rd, n, long=True):          # 6c/6d
    return ((1 if long else 0) << 31) | (0b001101 << 25) | (f << 21) | (R[rd] << 16) | (n & 0xFFFF)


def set24(rd, m):                       # 8b
    return (0b110 << 29) | ((m >> 16) << 21) | (R[rd] << 16) | (m & 0xFFFF)


def mov(t, w, rh, rp, ri="r0"):         # 7c
    return (1 << 31) | (0b001110 << 25) | (t << 24) | (w << 21) | (R[rh] << 16) | (R[rp] << 11) | R[ri]


def iomov(t, w, rh, io):                # 7b
    return (1 << 31) | (0b001110 << 25) | (t << 24) | (w << 21) | (R[rh] << 16) | (1 << 10) | io


def daop(p, i=0):
    return (p << 3) | i


def da(fmt, m, f, s, n, x, y, z):       # formats 1-3
    return (fmt << 29) | (m << 26) | (f << 24) | (s << 23) | (n << 21) | (x << 14) | (y << 7) | z


def special(g, n, y, z):                # format 5
    return (0b01111 << 27) | (g << 23) | (n << 21) | (y << 7) | z


NOP = 0x80000000
WAITI = iomov(1, 7, "r0", 10)
NOWRITE = 0b0000111
ACC = lambda i: i  # noqa: E731


class DecoderTest(unittest.TestCase):
    """Encodings against the manual's examples (section 4.6)."""

    def test_control_examples(self):
        self.assertEqual(text(0x80000000), "nop")                      # NOP p. 4-62
        self.assertEqual(text(0x80340000), "return (r18)")             # RETURN p. 4-65
        self.assertEqual(text(0x803E0000), "ireturn")                  # IRETURN p. 4-58
        # GOTO-COND p. 4-48: 10000 000010 00001 0x0800
        self.assertEqual(text(0x80410800), "if (pl) goto r1+2048")
        # GOTO-LOOP p. 4-49: 000011 00001 00010 0xff55
        self.assertEqual(text(0x0C22FF55, 0x200), "if (r1-- >= 0) goto r2-171")

    def test_alu_examples(self):
        # INCR/DECR p. 4-55: if(vs) r5 = r5 + 1, (short)
        self.assertEqual(text(alu(0, "r5", "r5", "+1", "vs", long=False)),
                         "if (vs) r5 = (short) r5 + 1")
        # SUBTRACT p. 4-84: if(mi) r10 = -r5
        self.assertEqual(text(0x988A0065), "if (mi) r10 = -r5")
        # SET p. 4-70: r2 = 0x800 as 16-bit add to r0
        self.assertEqual(text(0x14400800), "r2 = (short) 2048")
        # SHIFT-OR p. 4-75: 100100 00010 00001 0x0800
        self.assertEqual(text(0x90410800), "r2 = r1 <<| 0x0800")

    def test_da_example(self):
        # FMULT-ACC-STORE p. 4-40: *r1++ = a0 = a1 - *r2-- * *r3++r17
        w = da(3, 1, 0, 1, 0, 0b0011011, 0b0010110, 0b0001111)
        self.assertEqual(w, 0x6486CB0F)
        self.assertEqual(text(w), "*r1++ = a0 = a1 - *r2-- * *r3++r17")

    def test_io_condition_branch(self):
        # Be's audio driver polls the SIO with "if (obf) goto ." (C = 100010)
        self.assertEqual(text(0x844FFFF8, 0x830), "if (obf) goto 0x830")
        self.assertEqual(text(0x840FFFF8, 0x830), "if (ibe) goto 0x830")

    def test_do_forms(self):
        self.assertEqual(text(0x8C00056C), "do 0, 1388")
        self.assertEqual(text(0x8E800002), "doblock r2  /* K=0 */")    # M = bit 23
        self.assertEqual(text(0x8F000002), "dolock 0, r2")             # B = bit 24
        self.assertEqual(text(0x8E001805), "do 3, r5")

    def test_reserved(self):
        self.assertFalse(dis.decode(0x00000000).valid)                 # 0a
        self.assertFalse(dis.decode(0x08000000).valid)                 # 2a


def disk_or_skip(test):
    if not os.path.exists(DISK):
        test.skipTest("Nov 1994 disk image absent; fetch it with: " + FETCH)


def module_words(path):
    vol = befs1.Volume(DISK)
    data = vol.read(vol.lookup(path))
    import tempfile
    with tempfile.TemporaryDirectory() as t:
        out = os.path.join(t, "m")
        with open(out, "wb") as f:
            f.write(data)
        return dis.Coff(out)


class ModuleTest(unittest.TestCase):
    """Be's DSP code on the Nov 1994 disk."""

    def get(self, path):
        disk_or_skip(self)
        return module_words(path)

    def listing(self, coff):
        import io
        buf = io.StringIO()
        stats = dis.disassemble(coff, buf)
        return buf.getvalue(), stats

    def test_tnop_module(self):
        """mml/tnop against mml/tnop.s, word for word (13 words)."""
        text_, st = self.listing(self.get("/system/vcos/mml/tnop"))
        self.assertEqual(st, {"words": 13, "reserved": 0})
        for want in ("r1 = r1 - 1", "if (gt) goto 0x7c", "return (r18)",
                     "do 0, 1388", "goto 0x68"):
            self.assertIn(want, text_)

    def test_vftax_module(self):
        text_, st = self.listing(self.get("/system/vcos/mml/vftax"))
        self.assertEqual(st, {"words": 72, "reserved": 0})
        for want in ("a2 = dsp(*r2)", "a3 = float16(*r1++)", "do 3, r5",
                     "a0 = a1 + a2 * a3", "*r3++ = a0 = int16(a0)",
                     "if (gt) r6 = r2", "r5 = r6 >> 1"):
            self.assertIn(want, text_)

    def test_os_boot_mover(self):
        text_, st = self.listing(self.get("/system/vcos/mml/os"))
        self.assertEqual(st["words"], 491)
        self.assertIn("r22 = pc+208  /* 0x130 */", text_)
        self.assertIn("doblock r4  /* K=0 */", text_)
        self.assertIn("pcw = (short) r10", text_)


# ------------------------------------------------------------- the model

class Bus:
    def __init__(self):
        self.mem = {}

    def read(self, a, size):
        return int.from_bytes(bytes(self.mem.get(a + i, 0) for i in range(size)), "big")

    def write(self, a, size, v):
        for i, b in enumerate(v.to_bytes(size, "big")):
            self.mem[a + i] = b

    def words(self, a, ws):
        for i, w in enumerate(ws):
            self.write(a + 4 * i, 4, w)


CODE = 0x60001000


def machine(prog, base=CODE):
    bus = Bus()
    bus.words(base, prog)
    # boot block (BRC = 1): address MSB first, count 0, in word low bytes
    for i, b in enumerate(base.to_bytes(4, "big")):
        bus.write(0x60000000 + 4 * i, 4, b)
    d = dsp3210.DSP3210(bus.read, bus.write)
    d.reset()
    d.r = [0] * 32       # drop the boot ROM's r1/r2/r5 left-overs
    return d, bus


def run(d, n):
    for _ in range(n):
        d.step()


class FloatTest(unittest.TestCase):
    def test_float_format(self):
        # p. 3-8: N = M * 2^(e-128), M = (-2)^s + 0.f
        self.assertEqual(dsp3210.float_to_dsp(1.0), 0x00000080)
        self.assertEqual(dsp3210.float_to_dsp(-1.0), 0x8000007F)
        self.assertEqual(dsp3210.float_to_dsp(-0.75), 0xC000007F)
        self.assertEqual(dsp3210.float_to_dsp(-2.0), 0x80000080)
        self.assertEqual(dsp3210.dsp_to_float(0x7FFFFFFF), (2 - 2 ** -23) * 2.0 ** 127)
        self.assertEqual(dsp3210.dsp_to_float(0x12345600), 0.0)       # e = 0: zero

    def test_ieee(self):
        # 8.2.4.1: infinities clamp, e = 0 is zero
        self.assertEqual(dsp3210.ieee_to_dsp(0x3F800000), 0x80)
        self.assertEqual(dsp3210.ieee_to_dsp(0x7F800000), 0x7FFFFFFF)
        self.assertEqual(dsp3210.ieee_to_dsp(0xFF800000), 0x800000FF)
        self.assertEqual(dsp3210.ieee_to_dsp(0x80000000), 0)
        self.assertEqual(dsp3210.dsp_to_ieee(0x8000007F), 0xBF800000)


class ModelTest(unittest.TestCase):
    def test_boot_rom_brc1(self):
        d, _ = machine([NOP])
        self.assertEqual(d.boot_state, ("brc1", CODE, 0))
        self.assertEqual(d.pc, CODE)
        self.assertTrue(d.ior[dsp3210.PCW] & dsp3210.PCW_CPN)

    def test_boot_rom_brc1_copy(self):
        bus = Bus()
        hdr = (0xE100).to_bytes(4, "big") + (8).to_bytes(4, "big")
        for i, b in enumerate(hdr + bytes([0x80, 0, 0, 0, 0x80, 0, 0, 0])):
            bus.write(0x60000000 + 4 * i, 4, b)
        d = dsp3210.DSP3210(bus.read, bus.write)
        d.reset()
        self.assertEqual(d.pc, 0xE100)
        self.assertEqual(d.load(0xE100, 4), NOP)
        self.assertEqual(d.load(0xE104, 4), NOP)

    def test_delayed_branch(self):
        prog = [br("true", "pc", 8),            # 0: goto 0x10
                add3("r1", "r0", 1),            # 4: delay slot: runs
                add3("r2", "r0", 2),            # 8: skipped
                add3("r3", "r0", 3),            # c: skipped
                add3("r4", "r0", 4)]            # 10: target
        d, _ = machine(prog)
        run(d, 3)
        self.assertEqual((d.r[1], d.r[2], d.r[3], d.r[4]), (1, 0, 0, 4))

    def test_call_return(self):
        prog = [call("pc", 8, "r18"),           # 0: call 0x10, r18 = 8
                add3("r1", "r0", 1),            # 4: delay slot
                add3("r2", "r0", 2),            # 8: return lands here
                NOP,                            # c
                br("true", "r18"),              # 10: return (r18)
                add3("r3", "r0", 3)]            # 14: delay slot
        d, _ = machine(prog)
        run(d, 5)
        self.assertEqual(d.r[R["r18"]], CODE + 8)
        self.assertEqual((d.r[1], d.r[2], d.r[3]), (1, 2, 3))

    def test_loop_counter(self):
        prog = [add3("r1", "r0", 2),            # 0
                add3("r2", "r2", 1),            # 4: body
                loopc("r1", "pc", -12),         # 8: if (r1-- >= 0) goto 4
                NOP]                            # c
        d, _ = machine(prog)
        run(d, 1 + 3 * 3)
        self.assertEqual(d.r[2], 3)
        self.assertEqual(d.r[1] & 0xFFFFFFFF, 0xFFFFFFFF)

    def test_do_loop(self):
        prog = [do_imm(1, 4),                   # do next 2 insns 5 times
                add3("r1", "r1", 1),
                add3("r2", "r2", 2),
                add3("r3", "r3", 3)]
        d, _ = machine(prog)
        run(d, 1 + 2 * 5 + 1)
        self.assertEqual((d.r[1], d.r[2], d.r[3]), (5, 10, 3))

    def test_alu_flags(self):
        prog = [set24("r1", 0x7FFF),
                add3("r2", "r1", 1, long=False),     # 16-bit overflow
                set24("r3", 5),
                alu(4, "r4", "r3", "r3"),            # 0: z
                alui(13, "r1", 1)]                   # r1 $>>= 1
        d, _ = machine(prog)
        run(d, 2)
        self.assertEqual(d.r[2], 0xFFFF8000)        # sign-extended (short)
        self.assertEqual((d.flags["v"], d.flags["n"]), (1, 1))
        run(d, 3)
        self.assertEqual(d.r[1], 0x3FFF)
        d2, _ = machine([set24("r3", 5), alu(4, "r4", "r3", "r3")])
        run(d2, 2)
        self.assertEqual((d2.r[4], d2.flags["z"]), (0, 1))

    def test_shift_or(self):
        # SHIFT-OR p. 4-75: N << 16 OR'ed with all of rS, always 32-bit
        prog = [set24("r1", 0x345678),
                0x90410800,                         # r2 = r1 <<| 0x0800
                0x90220800]                         # r1 = r2 <<| 0x0800 (OR again)
        d, _ = machine(prog)
        run(d, 2)
        self.assertEqual(d.r[2], 0x08345678)
        run(d, 1)
        self.assertEqual(d.r[1], 0x08345678)

    def test_load_store(self):
        # 7c, Table 10-1; W = 1 char (sign-extends), 2 ushort, 3 short
        prog = [set24("r1", 0xE000),
                set24("r2", 0xFF34),
                mov(1, 2, "r2", "r1", "+1"),        # *r1++ = (short) r2
                add3("r1", "r1", -2),
                mov(0, 1, "r3", "r1"),              # r3 = (char) *r1
                mov(0, 2, "r4", "r1", "+1"),        # r4 = (ushort) *r1++
                add3("r1", "r1", -2),
                mov(0, 3, "r5", "r1")]              # r5 = (short) *r1
        d, _ = machine(prog)
        run(d, 8)
        self.assertEqual(d.load(0xE000, 2), 0xFF34)
        self.assertEqual(d.r[3], 0xFFFFFFFF)
        self.assertEqual(d.r[4], 0xFF34)
        self.assertEqual(d.r[5], 0xFFFFFF34)
        self.assertEqual(d.r[1], 0xE000)

    def test_mac(self):
        # a0 = 0.0 + Y*X from on-chip memory: 1.5 * -0.75
        prog = [set24("r1", 0xE000),
                set24("r2", 0xE004),
                da(3, 4, 0, 0, 0, daop(2), daop(1), NOWRITE),   # a0 = *r1 * *r2
                NOP]
        d, _ = machine(prog)
        d.store(0xE000, 4, dsp3210.float_to_dsp(1.5))
        d.store(0xE004, 4, dsp3210.float_to_dsp(-0.75))
        run(d, 4)
        self.assertEqual(d.acc[0], -1.125)
        self.assertEqual(text(prog[2]), "a0 = *r1 * *r2")

    def test_da_write_latency(self):
        # p. 4-14 Latency 1: a DA write is readable four instructions later
        z = daop(3)                              # *r3
        prog = [set24("r3", 0xE000),
                special(4, 0, ACC(1), z),        # *r3 = a0 = round(a1)
                mov(0, 7, "r4", "r3"),           # +1: old value
                NOP, NOP,
                mov(0, 7, "r5", "r3")]           # +4: new value
        d, _ = machine(prog)
        d.acc[1] = 2.0
        d.store(0xE000, 4, 0x11111111)
        run(d, 6)
        self.assertEqual(d.r[4], 0x11111111)
        self.assertEqual(d.r[5], dsp3210.float_to_dsp(2.0))

    def test_dau_condition_latency(self):
        # p. 4-15 Latency 4: the condition is the flags of four insns before
        prog = [special(4, 0, ACC(1), NOWRITE),  # a0 = round(a1) = -1: N
                br("alt", "pc", 16),             # +1: still the old flags
                NOP,
                NOP,
                br("alt", "pc", 4),              # +4: sees N
                NOP,
                add3("r1", "r0", 1),             # skipped by the second branch
                add3("r2", "r0", 2)]
        d, _ = machine(prog)
        d.acc[1] = -1.0
        run(d, 7)
        self.assertEqual((d.r[1], d.r[2]), (0, 2))

    def test_timer_interrupt(self):
        # The timer (p. 9-?) counts down at CKI/2 with tcon = 1; at zero it
        # latches vector 9 (Table 9-?), enabled by emr bit 9; waiti stops
        # until then; the vector is r22 + 8*9; ireturn goes back to pcsh.
        vec = 0xE800
        prog = [set24("r22", vec),
                set24("r1", 0x200),                   # emr bit 9: timer
                iomov(1, 3, "r1", 8),                 # emr = (short) r1
                WAITI,                                # c
                add3("r7", "r0", 7),                  # 10: after the return
                NOP, NOP, NOP]
        d, bus = machine(prog)
        for i, w in enumerate([add3("r9", "r0", 9), 0x803E0000]):
            d.store(vec + 8 * 9 + 4 * i, 4, w)
        run(d, 3)                                    # r22, r1, emr
        self.assertEqual(d.ior[dsp3210.EMR], 0x200)
        d.store(0x414, 4, 40)                        # timer = 40
        d.store(0x413, 1, 0x01)                      # enable, CKI/2
        run(d, 1)                                    # waiti
        self.assertTrue(d.waiting)
        run(d, 15)                                   # 2 counts per insn
        self.assertTrue(d.waiting)
        self.assertEqual(d.r[9], 0)
        run(d, 6)
        self.assertEqual(d.r[9], 9)
        self.assertEqual(d.r[7], 7)
        self.assertFalse(d.in_interrupt)
        self.assertEqual(d.pcsh, CODE + 0x10)


class InterfaceTest(unittest.TestCase):
    """The calls tools/beboot.py makes (docs/dsp3210.md "Interface")."""

    def test_reset_release_run(self):
        bus = Bus()
        bus.words(CODE, [add3("r1", "r1", 1), br("true", "pc", -12), NOP])
        for i, b in enumerate(CODE.to_bytes(4, "big")):
            bus.write(0x60000000 + 4 * i, 4, b)
        d = dsp3210.DSP3210(bus.read, bus.write)
        self.assertTrue(d.idle)                       # held in reset
        self.assertEqual(d.run(10), 0)
        d.release()
        self.assertEqual(d.ior[dsp3210.PCW] & 0x3C00, 0x3C00)   # Boot= 0x3d80
        d.r[1] = 0
        self.assertEqual(d.run(9), 9)
        self.assertEqual(d.r[1], 3)                   # add, goto, delay add ...
        d.hold_reset()
        self.assertEqual(d.run(5), 0)
        self.assertEqual(d.r[1], 3)
        self.assertEqual(d.cycles, 24)

    def test_bio_and_irq(self):
        seen = []
        prog = [set24("r22", 0xE800), set24("r1", 0x8000),
                iomov(1, 3, "r1", 8),                 # emr: EXT1 only
                set24("r3", 0x41E), set24("r2", 2),
                mov(1, 2, "r2", "r3"),                # bio = 2: BIO0 high
                WAITI, NOP, NOP]
        d, _ = machine(prog)
        d.on_bio = seen.append
        d.store(0xE800 + 8 * 15, 4, add3("r9", "r0", 9))
        d.store(0xE800 + 8 * 15 + 4, 4, 0x803E0000)
        d.run(7)
        self.assertEqual(seen, [1])
        self.assertTrue(d.waiting)
        self.assertTrue(d.idle)
        d.set_irq(1, 1)                               # IREQ1
        self.assertFalse(d.idle)
        d.run(3)
        self.assertEqual(d.r[9], 9)


class BoardBus:
    """beboot's bus shape: write(addr, value, size), pins(name, level)."""

    def __init__(self):
        self.b = Bus()
        self.pinlog = []

    def read(self, a, size):
        return self.b.read(a, size)

    def write(self, a, value, size):
        self.b.write(a, size, value)

    def pins(self, name, level):
        self.pinlog.append((name, level))


class BeBootTest(unittest.TestCase):
    """The Dsp3210 wrapper beboot drives, and that a run pickles."""

    def test_wrapper(self):
        import pickle
        bus = BoardBus()
        prog = [set24("r3", 0x41E), set24("r2", 2 << 2),
                mov(1, 2, "r2", "r3"),                # bio: BIO1 high
                add3("r1", "r1", 1), br("true", "pc", -12), NOP]
        bus.b.words(CODE, prog)
        for i, b in enumerate(CODE.to_bytes(4, "big")):
            bus.b.write(0x60000000 + 4 * i, 4, b)
        d = dsp3210.Dsp3210(2, bus)
        self.assertEqual(d.step(), 4)                 # in reset: time passes
        d.release()
        self.assertEqual(d.pc, CODE)
        for _ in range(3):
            d.step()
        self.assertEqual(bus.pinlog, [("bio1", 1)])
        d2 = pickle.loads(pickle.dumps(d))
        for x in (d, d2):
            x.core.r[1] = 0
            for _ in range(6):
                x.step()
        self.assertEqual(d.core.r[1], d2.core.r[1])
        self.assertEqual(d.pc, d2.pc)
        d.hold()
        self.assertTrue(d.idle)



def relocate(coff, symbols):
    """Lay out a VCOS module at its paddrs and apply its COFF relocations
    (10-byte entries: vaddr, symbol index, type).  Types as observed in
    mml/os: 44 a 32-bit word, 46 the 24-bit immediate of a format 8b
    `rN = (ushort24) A` (Ne bits 28-21 high, N bits 15-0 low), 47 the N of
    the `rN <<| N` after it, which takes bits 31-16 of the pair's value.
    The value is symbols[index] + A.  The type meanings are INFERRED from
    the code pairs they land on, and the symbol values are the caller's:
    the module's symbol table is absent (symptr 0x382b lies past the end),
    so what vcas_server's loader gives each index is not known."""
    img = bytearray(max(s["paddr"] + s["size"] for s in coff.sections))
    for sec in coff.sections:
        img[sec["paddr"]:sec["paddr"] + sec["size"]] = coff.data(sec)
    pair = {}
    unresolved = []
    for sec in coff.sections:
        for k in range(sec["nreloc"]):
            e = coff.blob[sec["relptr"] + 10 * k: sec["relptr"] + 10 * k + 10]
            va, sym, typ = struct.unpack(">IIH", e)
            if sym not in symbols:
                unresolved.append((sec["name"], va, sym, typ))
                continue
            w = struct.unpack(">I", img[va:va + 4])[0]
            if typ == 44:
                w = (w + symbols[sym]) & 0xFFFFFFFF
            elif typ == 46:
                v = (((w >> 21) & 0xFF) << 16 | (w & 0xFFFF)) + symbols[sym]
                pair[va + 4] = v
                w = (w & 0xE01F0000) | ((v >> 16) & 0xFF) << 21 | (v & 0xFFFF)
            elif typ == 47:
                w = (w & 0xFFFF0000) | (pair[va] >> 16) & 0xFFFF
            else:
                raise AssertionError("relocation type %d" % typ)
            img[va:va + 4] = struct.pack(">I", w)
    return img, unresolved


class VcosBootTest(unittest.TestCase):
    """mml/os's __boot from Be's boot block, standing alone: the BRC = 1
    ROM path enters the module in host memory, __boot sets up the timer
    and pcw, copies __vcos on-chip with doblock and enters it.

    Inputs that are INFERRED, not read from the loader: the module image at
    DSP 0x60010000; symbol 12 (the vector table's handler pointers) is the
    module base; 63/68 put __vcos's copy at on-chip 0xE000 (68 is 0x20
    past 63, as the copy starts at the section header while the return
    address counts from the code); 81 (r21, the stack) at 0xE400; pcw
    word 0x128 holds vcos.cfg's Boot= 0x3d80.  The run ends where __vcos
    reads its execution-list pointer, which the host has not set: a
    load through 0, the boot ROM, which is not modelled."""

    BASE = 0x60010000

    def test_os_boot_standalone(self):
        disk_or_skip(self)
        coff = module_words("/system/vcos/mml/os")
        b = self.BASE
        img, unresolved = relocate(coff, {12: b, 63: 0xE000 - 0x69C,
                                          68: 0xE000 - 0x69C + 0x20,
                                          81: 0xE400 - 0x69C})
        # the five external symbols of __vcos, and __ModH's
        self.assertEqual(sorted(u[2] for u in unresolved), [13, 56, 58, 59, 62, 76])
        img[0x128:0x12C] = struct.pack(">I", 0x3D80)
        bus = Bus()
        for i, x in enumerate(img):
            bus.mem[b + i] = x
        for i, x in enumerate((b + 0x58).to_bytes(4, "big")):
            bus.write(0x60000000 + 4 * i, 4, x)
        d = dsp3210.DSP3210(bus.read, bus.write)
        d.reset(0xF0)
        seen = []
        with self.assertRaisesRegex(dsp3210.DspError, "data read of boot ROM 0x0"):
            for _ in range(1000):
                seen.append(d.pc)
                d.step()
        self.assertEqual(d.steps, 176)                      # the 177th faults
        self.assertEqual(seen[-1], 0xE114)
        self.assertEqual(d.mmio[0x413], 0x2F)               # timer running
        self.assertEqual(d.ior[dsp3210.PCW], 0x3D80)
        self.assertEqual(d.ior[dsp3210.DAUC], 12)
        self.assertEqual(d.r[26], b + 0x130)                # vector table
        self.assertIn(0xE108, seen)                         # __vcos entered on-chip
        self.assertEqual(d.ram[:0x188], bytes(img[0x67C:0x67C + 0x188]))


if __name__ == "__main__":
    unittest.main()
