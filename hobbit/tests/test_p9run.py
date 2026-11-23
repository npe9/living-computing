#!/usr/bin/env python3
"""A2 on the reference model: the shipped 1e toolchain runs.

`tools/p9run.py` runs a 1st Edition Plan 9 Hobbit binary on
`sem/hobbit_sem.py` with the kernel's side (exec frame, system calls,
the floating-point handler) played by the host.  These tests are the
oracle for the Bluespec run of the same binaries:

* the shipped `za` assembles every `.s` of `sys/src/libc/hobbit` into
  an object **byte-identical** to the member of the shipped
  `hobbit/lib/libc.a` built from the same source in 1993;
* the shipped `zl` links an object `za` just made against the shipped
  `libc.a`, and the linked program runs and prints;
* `echo` prints its arguments and `cat` copies a file, byte-exact;
* little-endian data (PSW.UL / CONFIG.KL, PRM pp. 1-3, 1-4), which 1e
  runs with and which the model did not have before this file.

Discriminating checks, observed 2026-11-20.  Twelve bugs were injected
one at a time (22 tests; run with P9RUN_MAX_STEPS=1700000 so a program
that loops fails quickly), each reverted by rewriting the saved file; the
suite was green before and after.  "za 12" means all twelve sources of
`test_za_reproduces_every_shipped_libc_object` failed.

  sem: little-endian lanes read as big-endian (`_lane_shift`)
      10 tests: the 3 LittleEndian lane tests, the kernel/user rule test,
      the byte load through step(), echo, za usage, za main9, za 12,
      za->zl->run, zl undefined.  cat did NOT fail: it never reads a byte.
  sem: kernel level obeys PSW.UL (`_little_endian`)
      1 test: test_user_bit_is_ignored_at_kernel_level_and_kl_decides
  sem: an "unimp" dyadic opcode is refused instead of trapped
      6 tests: both UnimplementedSequence tests, za usage, za main9,
      za 12, za->zl->run
  p9run: argv pointer one slot high (`exec_frame`)
      9 tests: the frame test, echo, cat, the outside-root test, za usage,
      za main9, za 12, za->zl->run, zl undefined
  p9run: argc not written
      4 tests: the frame test, echo, cat, the outside-root test (za and zl
      never read argc: ARGBEGIN walks argv)
  p9run: FSUB computed source - destination
      1 test: test_fsub_is_destination_minus_source_and_fdiv_likewise
  p9run: Double stored high word first
      1 test: test_fmov_immediate_single_to_absolute_double (za's own
      FMOV is of 0.0, so no object changed)
  p9run: three-operand FP result stored to the destination
      1 test: test_three_operand_result_goes_to_the_accumulator
  p9run: seek ignores its type argument
      2 tests: za->zl->run, zl undefined (za never seeks)
  p9run: the system call's result not stored
      5 tests: cat, za main9, za 12, za->zl->run, zl undefined
  p9run: the data segment not loaded
      6 tests: echo, za usage, za main9, za 12, za->zl->run, zl undefined
  p9run: KRET's PSW not restored
      7 tests: cat, echo, za usage, za main9, za 12, za->zl->run,
      zl undefined

Not discriminated by anything here: FADD/FMUL/FDIV rounding against
fpi.c (the arithmetic is host IEEE double, not fpi.c's `Internal`), and
errstr's text.

`ArCalls` and `Ar` (A3, 2026-11-23): fstat and rfork(RFNOTEG) as the
shipped `ar` uses them, and `ar t`/`x`/`vu` and `rl` on members of the
shipped libc.a.  Five bugs injected one at a time into tools/p9run.py
(each reverted by rewriting the saved file; `ArCalls Ar` green before
and after), observed failures:

  fstat: mtime + 1
      test_fstat_writes_convD2M_of_the_host_file,
      test_ar_vu_rebuilds_the_shipped_members_and_headers
  fstat: length in VLONG's high word, not its low
      the same two, and test_rl_writes_the_table_then_stops_at_its_fork
  fstat: mode a constant 0644, not the file's bits
      test_fstat_writes_convD2M_of_the_host_file,
      test_ar_vu_rebuilds_the_shipped_members_and_headers
  rfork: RFNOTEG refused
      test_rfork_rfnoteg_returns_zero, test_ar_vu_..., test_rl_...
  fstat: no evenaddr() check
      test_fstat_to_an_odd_buffer_stops only

`ar t` and `ar x` never call fstat or rfork, so none of these reach
them; they are there as the oracle that the archive reader agrees with
the shipped file.

`StackCacheContents` (added later the same day, with `State.cache`) has
no injection table of its own: the injection that matters for it is the
Bluespec comparison, where running the reference model without the
array (`state.cache = None` in tools/p9run.py) makes `za main9.s` differ
from the core at record 29,664 (docs/conformance_1to1.md 1c).
"""

import io
import os
import pathlib
import shutil
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
HOBBIT = HERE.parent
sys.path.insert(0, str(HOBBIT / "tools"))
sys.path.insert(0, str(HOBBIT / "sem"))
import build_zl_inferno   # noqa: E402
import hobbit_sem as sem  # noqa: E402
import p9run              # noqa: E402

REL = HOBBIT / "tools" / "plan9-1e"
BIN = REL / "hobbit" / "bin"
LIBC = REL / "hobbit" / "lib" / "libc.a"
LIBSRC = REL / "sys" / "src" / "libc" / "hobbit"

#: every assembler source of libc/hobbit; each has a libc.a member
SOURCES = ["argv0", "main9", "main9p", "memmove", "memset", "setjmp",
           "strchr", "strcmp", "strcpy", "strlen", "strncmp", "strrchr"]

HELLO = """\
TEXT main(SB), 1, $16
	MOV	$1, R4
	MOV	$hellomsg+0(SB), R8
	MOV	$9, R12
	CALL	write(SB)
	RETURN

DATA	hellomsg+0(SB), $"hello 1e"
DATA	hellomsg+8(SB), $"\\n"
GLOBL	hellomsg+0(SB), $16
"""


#: The longest run here is zl linking hello (697,197); a program that has
#: gone wrong loops, and the cap keeps that a failure, not a wait.
MAX_STEPS = int(os.environ.get("P9RUN_MAX_STEPS", "3000000"))


def run(root, binary, *args):
    out = io.BytesIO()
    status, steps, kernel, _ops = p9run.run(
        str(binary), [os.path.basename(str(binary))] + list(args),
        str(root), MAX_STEPS, out)
    return status, out.getvalue(), kernel, steps


class Tree(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp(prefix="p9run-"))
        self.addCleanup(shutil.rmtree, self.root)
        (self.root / "hobbit" / "lib").mkdir(parents=True)
        shutil.copy(LIBC, self.root / "hobbit" / "lib" / "libc.a")


class Toolchain(Tree):
    def test_za_reproduces_every_shipped_libc_object(self):
        members = build_zl_inferno.read_members(str(LIBC))
        for name in SOURCES:
            with self.subTest(source=name):
                shutil.copy(LIBSRC / (name + ".s"), self.root)
                status, console, _k, _n = run(self.root, BIN / "za",
                                              name + ".s")
                self.assertEqual(status, "exits('')")
                self.assertEqual(console, b"")
                made = (self.root / (name + ".z")).read_bytes()
                self.assertEqual(made, members[name + ".z"])

    def test_za_main9_syscalls_and_count(self):
        # The instruction count is the reference for the Bluespec run's
        # retirement count; the syscall sequence is what its shim must do.
        shutil.copy(LIBSRC / "main9.s", self.root)
        status, _c, k, steps = run(self.root, BIN / "za", "main9.s")
        self.assertEqual(status, "exits('')")
        self.assertEqual([name for name, _r in k.trace],
                         ["brk_", "open", "open", "create", "brk_",
                          "open", "read", "read", "close",
                          "open", "read", "read", "close",
                          "write", "exits"])
        self.assertEqual(steps, 125572)
        # Floating point reaches the handler by the unimplemented
        # instruction sequence; za's cinit has the one FMOV at 0x26d0.
        self.assertEqual(k.fp_traps, [(0x26D0, ["FMOV"])])

    def test_za_then_zl_then_the_program_runs(self):
        (self.root / "hello.s").write_text(HELLO)
        status, console, _k, _n = run(self.root, BIN / "za", "hello.s")
        self.assertEqual((status, console), ("exits('')", b""))
        status, console, _k, _n = run(self.root, BIN / "zl", "-o", "hello",
                                      "hello.z", "-lc")
        self.assertEqual((status, console), ("exits('')", b""))
        status, console, k, _n = run(self.root, self.root / "hello")
        self.assertEqual(console, b"hello 1e\n")
        # `_main` passes exits() the address of `_exits<>`, which za
        # records as a static in the MOV and as an extern in the DATA (so
        # in every shipped binary it is libc's `_exits` *function*, e.g.
        # cat's `MOV $0x12da,R4`): the status is that function's bytes,
        # `KCALL $8; RETURN R0` read as little-endian data.
        self.assertEqual(k.exit_msg, "\x02\x08\x02")

    def test_zl_reports_an_undefined_symbol_and_removes_the_output(self):
        members = build_zl_inferno.read_members(str(LIBC))
        (self.root / "main9.z").write_bytes(members["main9.z"])
        status, console, k, _n = run(self.root, BIN / "zl", "-o", "x.out",
                                     "main9.z")
        self.assertEqual(status, "exits('error')")
        self.assertIn(b"_main: undefined: main", console)
        self.assertIn("remove", [name for name, _r in k.trace])
        self.assertFalse((self.root / "x.out").exists())


class Programs(Tree):
    def test_echo_prints_its_arguments(self):
        status, console, _k, _n = run(self.root, BIN / "echo", "hello",
                                      "world")
        self.assertEqual((status, console), ("exits('')", b"hello world\n"))

    def test_cat_copies_a_named_file(self):
        src = REL / "sys" / "src" / "9" / "hobbit" / "trap.c"
        shutil.copy(src, self.root / "trap.c")
        status, console, _k, _n = run(self.root, BIN / "cat", "trap.c")
        self.assertEqual(status, "exits('')")
        self.assertEqual(console, src.read_bytes())

    def test_za_usage(self):
        status, console, _k, _n = run(self.root, BIN / "za")
        self.assertEqual(status, "exits('error')")
        self.assertEqual(console, b"usage: za [-options] file.s\n")

    def test_a_path_outside_the_root_is_refused(self):
        status, _c, _k, _n = run(self.root, BIN / "cat", "../../etc/passwd")
        self.assertIn("outside --root", status)


class ExecFrame(unittest.TestCase):
    def test_frame_is_sysexec_and_execregs(self):
        st = sem.State()
        sp, msp = p9run.exec_frame(st, ["za", "main9.s"])
        m = p9run.Machine(st)
        # nbytes = 3 + 8 = 11 -> 12; ssize = 4*3 + 12 = 24; (24+4)&7 -> 28
        self.assertEqual(msp, 0x80000000)
        self.assertEqual(sp, 0x80000000 - 48)       # QUADALIGN(28 + 12)
        self.assertEqual(m.word(sp), 0x80000000 - 4)
        self.assertEqual(m.word(sp + 4), 2)         # argc, the accumulator
        vec = m.word(sp + 8)
        self.assertEqual(vec, 0x80000000 - 28)
        self.assertEqual(m.cstring(m.word(vec)), b"za")
        self.assertEqual(m.cstring(m.word(vec + 4)), b"main9.s")
        self.assertEqual(m.word(vec + 8), 0)


class Fpi(unittest.TestCase):
    """fpihobbit.c's decode: operand order, modes, the sequence strings."""

    def machine(self, parcels, sp=0x1000):
        st = sem.State(pc=0x100, sp=sp, msp=sp + 0x100, psw=p9run.PSW_USER)
        for i in range(0, len(parcels), 2):
            pair = parcels[i:i + 2] + [0]
            st.memory[0x100 + 2 * i] = (pair[0] << 16) | pair[1]
        return st, p9run.Machine(st)

    def test_fmov_immediate_single_to_absolute_double(self):
        # za's cinit: d1f1 <single 1.5> <addr>; the next parcel is not FP
        st, m = self.machine([0xD1F1, 0x3FC0, 0x0000, 0x0000, 0x2000, 0x7006])
        self.assertEqual(p9run.fpi(m, st), ["FMOV"])
        self.assertEqual(st.pc, 0x10A)
        # fpi.h Double is {l, h}: the low word is at the lower address
        self.assertEqual((m.word(0x2000), m.word(0x2004)),
                         (0x00000000, 0x3FF80000))

    def test_fsub_is_destination_minus_source_and_fdiv_likewise(self):
        st, m = self.machine([0xA8DD, 0x0010, 0x0014,     # FSUB R16.W, R20.W
                              0xAADD, 0x0010, 0x0014,     # FDIV R16.W, R20.W
                              0x7006])
        m.set_word(0x1010, 3)
        m.set_word(0x1014, 20)
        self.assertEqual(p9run.fpi(m, st), ["FSUB", "FDIV"])
        self.assertEqual(m.word(0x1014), 5)               # (20 - 3) / 3 -> 5
        self.assertEqual(st.pc, 0x10C)

    def test_three_operand_result_goes_to_the_accumulator(self):
        st, m = self.machine([0xBBDD, 0x0010, 0x0014, 0x7006])   # FADD3
        m.set_word(0x1010, 3)
        m.set_word(0x1014, 20)
        p9run.fpi(m, st)
        self.assertEqual((m.word(0x1004), m.word(0x1014)), (23, 20))

    def test_compare_sets_and_clears_the_flag(self):
        st, m = self.machine([0x99DD, 0x0010, 0x0014, 0x7006])   # FCMPGT
        m.set_word(0x1010, 7)
        m.set_word(0x1014, 2)
        p9run.fpi(m, st)
        self.assertTrue(st.psw & 0x10)                    # source > destination
        st.pc = 0x100
        m.set_word(0x1010, 1)
        p9run.fpi(m, st)
        self.assertFalse(st.psw & 0x10)

    def test_a_non_fp_opcode_is_left_alone(self):
        st, m = self.machine([0x86DC, 0x0000, 0x2004])
        self.assertEqual(p9run.fpi(m, st), [])
        self.assertEqual(st.pc, 0x100)


class UnimplementedSequence(unittest.TestCase):
    def test_fp_opcode_takes_the_p_1_39_sequence(self):
        # FMOV $1.5, *$0x2000.D (five-parcel opcode 0x11, "unimp" in
        # Table 1-20): trap=1, the one store is *(CSP) = PC, and PC, SP
        # and MSP stay at their pre-state for the handler.
        st = sem.State(pc=0x100, sp=0x1000, msp=0x1100, psw=p9run.PSW_USER)
        st.memory[0x100] = 0xD1F13FC0
        st.memory[0x104] = 0x00000000
        st.memory[0x108] = 0x20000000
        rec, st = sem.step(st)
        self.assertEqual((rec.trap, rec.mem_we, rec.mem_addr, rec.mem_wdata,
                          rec.mem_wmask), (1, 1, 0x1000, 0x100, 0xF))
        self.assertEqual((st.pc, st.sp, st.msp), (0x100, 0x1000, 0x1100))
        self.assertEqual(st.memory[0x1000], 0x100)

    def test_three_parcel_unimp_opcode_also_traps(self):
        st = sem.State(pc=0x100, sp=0x1000, msp=0x1100, psw=p9run.PSW_USER)
        st.memory[0x100] = 0xA8DD0010          # FSUB R16.W, R20.W
        st.memory[0x104] = 0x00140000
        rec, st = sem.step(st)
        self.assertEqual((rec.trap, rec.mem_wdata), (1, 0x100))


class LittleEndian(unittest.TestCase):
    """PRM p. 1-3/1-4: PSW.UL at user level, CONFIG.KL at kernel level."""

    WORD = 0x11223344

    def state(self, psw, kl=False):
        st = sem.State(psw=psw, config_kl=kl)
        st.memory[0x2000] = self.WORD
        return st

    def load(self, st, ea, size, signed=False):
        return sem._load(st, None, sem.Operand(size, signed, ea=ea))

    def test_big_endian_bytes_figure_1_2(self):
        st = self.state(sem.PSW_SP | sem.PSW_USER)
        self.assertEqual([self.load(st, 0x2000 + k, 1) for k in range(4)],
                         [0x11, 0x22, 0x33, 0x44])
        self.assertEqual([self.load(st, 0x2000 + k, 2) for k in (0, 2)],
                         [0x1122, 0x3344])

    def test_little_endian_bytes_figure_1_3(self):
        st = self.state(sem.PSW_SP | sem.PSW_USER | sem.PSW_USER_LE)
        self.assertEqual([self.load(st, 0x2000 + k, 1) for k in range(4)],
                         [0x44, 0x33, 0x22, 0x11])
        self.assertEqual([self.load(st, 0x2000 + k, 2) for k in (0, 2)],
                         [0x3344, 0x1122])

    def test_user_bit_is_ignored_at_kernel_level_and_kl_decides(self):
        st = self.state(sem.PSW_SP | sem.PSW_USER_LE)          # kernel, UL set
        self.assertEqual(self.load(st, 0x2000, 1), 0x11)
        st = self.state(sem.PSW_SP, kl=True)
        self.assertEqual(self.load(st, 0x2000, 1), 0x44)
        st = self.state(sem.PSW_SP | sem.PSW_USER, kl=True)    # user, KL set
        self.assertEqual(self.load(st, 0x2000, 1), 0x11)

    def test_little_endian_store_lanes_and_mask(self):
        st = self.state(sem.PSW_SP | sem.PSW_USER | sem.PSW_USER_LE)
        got = sem._prepare_store(st, None, sem.Operand(1, False, ea=0x2001),
                                 0xAB)
        self.assertEqual(got, (0x2000, 0x1122AB44, 0x0000AB00, 0x2))
        got = sem._prepare_store(st, None, sem.Operand(2, False, ea=0x2002),
                                 0xBEEF)
        self.assertEqual(got, (0x2000, 0xBEEF3344, 0xBEEF0000, 0xC))

    def test_big_endian_store_lanes_and_mask(self):
        st = self.state(sem.PSW_SP | sem.PSW_USER)
        got = sem._prepare_store(st, None, sem.Operand(1, False, ea=0x2001),
                                 0xAB)
        self.assertEqual(got, (0x2000, 0x11AB3344, 0x00AB0000, 0x4))
        got = sem._prepare_store(st, None, sem.Operand(2, False, ea=0x2002),
                                 0xBEEF)
        self.assertEqual(got, (0x2000, 0x1122BEEF, 0x0000BEEF, 0x3))

    def test_a_little_endian_byte_load_through_step(self):
        # MOV *$0x2001:UB, R4 (three-parcel MOV, source mode 1, dest 0xD)
        st = self.state(sem.PSW_SP | sem.PSW_USER | sem.PSW_USER_LE)
        st.pc, st.sp, st.msp = 0x100, 0x1000, 0x1100
        st.memory[0x100] = (0x861D << 16) | 0x2001
        st.memory[0x104] = 0x0004 << 16
        rec, st = sem.step(st)
        self.assertEqual((rec.mem_addr, rec.mem_wdata), (0x1004, 0x33))


class StackCacheContents(unittest.TestCase):
    """The stack cache's 64 words, when the model keeps them
    (`State.cache`): the printed loops of pp. 3-19 (ENTER) and 3-10/3-11
    (CATCH), and p. 1-5/1-12's window.  The slot of an address is its
    bits 7:2 -- the cache is 64 words and the window never exceeds 256
    bytes -- which is the Bluespec core's indexing too, so the *value* an
    uninitialised stack word reads is agreed between the two models by
    construction, not independently derived."""

    def state(self, sp, msp):
        st = sem.State(pc=0x100, sp=sp, msp=msp, psw=sem.PSW_SP)
        st.cache = [0] * 64
        return st

    @staticmethod
    def put(st, addr, *parcels):
        for i in range(0, len(parcels), 2):
            pair = list(parcels[i:i + 2]) + [0]
            st.memory[addr + 2 * i] = (pair[0] << 16) | pair[1]

    def test_a_store_inside_the_window_goes_to_the_cache(self):
        st = self.state(0x1000, 0x1100)
        self.put(st, 0x100, 0x86FD, 0x0007, 0x0004)          # MOV $7, R4
        rec, st = sem.step(st)
        self.assertEqual((rec.mem_addr, rec.mem_wdata), (0x1004, 7))
        self.assertEqual(st.cache[(0x1004 >> 2) & 63], 7)
        self.assertNotIn(0x1004, st.memory)

    def test_a_store_outside_the_window_goes_to_memory(self):
        st = self.state(0x1000, 0x1000)                      # empty cache
        self.put(st, 0x100, 0x86FD, 0x0007, 0x0004)
        rec, st = sem.step(st)
        self.assertEqual(st.memory[0x1004], 7)
        self.assertEqual(st.cache, [0] * 64)

    def test_without_the_array_every_store_is_memory(self):
        st = sem.State(pc=0x100, sp=0x1000, msp=0x1100, psw=sem.PSW_SP)
        self.put(st, 0x100, 0x86FD, 0x0007, 0x0004)
        rec, st = sem.step(st)
        self.assertEqual(st.memory[0x1004], 7)

    def test_enter_extends_the_window_without_loading_it(self):
        # p. 3-19: ENTER moves SP; it loads nothing.  The new frame's
        # words read what their slots last held, not what memory holds.
        st = self.state(0x1000, 0x1040)
        st.memory[0xFF4] = 0x1234                    # memory's old word
        st.cache[(0xFF4 >> 2) & 63] = 0xDEAD         # the slot's old word
        self.put(st, 0x100, 0x0BFC, 0x6022)          # ENTER R-16; MOV R4,R8
        rec, st = sem.step(st)
        self.assertEqual((st.sp, st.msp), (0xFF0, 0x1040))
        rec, st = sem.step(st)
        self.assertEqual((rec.mem_addr, rec.mem_wdata), (0xFF8, 0xDEAD))
        self.assertEqual(st.memory[0xFF4], 0x1234)   # untouched

    def test_enter_flushes_whole_blocks_from_the_top(self):
        # p. 3-19: while (MSP > SHAD && MSP - target > SCSIZE) the block
        # at MSP-16 goes to memory and MSP -= 16.
        st = self.state(0x1000, 0x1100)
        st.cache = [0xC0DE0000 + i for i in range(64)]
        self.put(st, 0x100, 0x0BFC)                  # ENTER R-16
        rec, st = sem.step(st)
        self.assertEqual((st.sp, st.msp), (0xFF0, 0x10F0))
        self.assertEqual([st.memory[a] for a in range(0x10F0, 0x1100, 4)],
                         [0xC0DE003C, 0xC0DE003D, 0xC0DE003E, 0xC0DE003F])
        self.assertNotIn(0x10EC, st.memory)          # one block, no more

    def test_catch_fills_the_words_it_brings_in(self):
        # pp. 3-10/3-11: the cache is filled upward from MSP from memory.
        st = self.state(0x1000, 0x1000)
        for k in range(8):
            st.memory[0x1000 + 4 * k] = 0xA0 + k
        self.put(st, 0x100, 0x0809)                  # CATCH R32
        rec, st = sem.step(st)
        self.assertEqual((st.sp, st.msp), (0x1000, 0x1020))
        self.assertEqual([st.cache[(a >> 2) & 63]
                          for a in range(0x1000, 0x1020, 4)],
                         [0xA0 + k for k in range(8)])
        self.assertEqual(st.cache[(0x1020 >> 2) & 63], 0)   # not beyond

    def test_enter_with_a_memory_target_flushes_everything(self):
        # p. 3-19 "flush stack cache unconditionally"; p. 3-20 case 4:
        # the target is the word AT the absolute address.
        st = self.state(0x1000, 0x1020)
        for a in range(0x1000, 0x1020, 4):
            st.cache[(a >> 2) & 63] = 0xB000 + a
        st.memory[0x2000] = 0xFF0
        self.put(st, 0x100, 0x80C9, 0x0000, 0x2000)  # ENTER *$0x2000
        rec, st = sem.step(st)
        self.assertEqual((st.sp, st.msp), (0xFF0, 0xFF0))
        self.assertEqual([st.memory[a] for a in range(0x1000, 0x1020, 4)],
                         [0xB000 + a for a in range(0x1000, 0x1020, 4)])

    def test_kernel_entry_flush_is_that_enter(self):
        st = self.state(0x1000, 0x1020)
        for a in range(0x1000, 0x1020, 4):
            st.cache[(a >> 2) & 63] = 0xB000 + a
        p9run.kernel_entry_flush(st)
        self.assertEqual((st.sp, st.msp), (0x1000, 0x1000))
        self.assertEqual(st.memory[0x1004], 0xB000 + 0x1004)


def archive(data):
    """[(name, 60-byte header, body, offset of the header)]."""
    out, off = [], 8
    while off + 60 <= len(data):
        hdr = data[off:off + 60]
        size = int(hdr[48:58].decode().strip())
        out.append((hdr[0:16].decode("latin-1").rstrip(), hdr,
                    data[off + 60:off + 60 + size], off))
        off += 60 + size + (size & 1)
    return out


def symdef_by_member(data):
    """rl.c's table (4-byte offset, NNAME=20 name, type, 3 pad), as
    (member the offset points at, name up to the NUL, 'T' or 'D')."""
    members = archive(data)
    at = {off: name for name, _h, _b, off in members}
    body = members[0][2]
    out = []
    for i in range(0, len(body), 28):
        e = body[i:i + 28]
        out.append((at[int.from_bytes(e[0:4], "little")],
                    e[4:24].split(b"\0")[0].decode(), "TD"[e[24]]))
    return out


class ArCalls(unittest.TestCase):
    """fstat and rfork as ar uses them (sysfstat, sysrfork, convD2M)."""

    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp(prefix="p9ar-"))
        self.addCleanup(shutil.rmtree, self.root)
        st = sem.State()
        self.m = p9run.Machine(st)
        self.k = p9run.Kernel(str(self.root), self.m, 0x2000, io.BytesIO())

    def test_fstat_writes_convD2M_of_the_host_file(self):
        path = self.root / "a-file-name.z"
        path.write_bytes(b"x" * 1234)
        os.chmod(path, 0o664)
        os.utime(path, (726010000, 726010682))
        f = open(path, "rb")
        self.addCleanup(f.close)
        self.k.fds[3] = f
        self.m.set_bytes(0x3000, b"\xAA" * 120)
        self.assertEqual(self.k.call(11, self._args(3, 0x3000)), 0)
        d = self.m.bytes(0x3000, 116)
        self.assertEqual(d[0:28], b"a-file-name.z" + b"\0" * 15)  # name
        self.assertEqual(d[28:56], b"none" + b"\0" * 24)          # uid
        self.assertEqual(d[56:84], b"none" + b"\0" * 24)          # gid
        ino = os.stat(path).st_ino & 0x7FFFFFFF
        self.assertEqual(d[84:88], ino.to_bytes(4, "little"))    # qid.path
        self.assertEqual(d[88:92], bytes(4))                     # qid.vers
        self.assertEqual(d[92:96], (0o664).to_bytes(4, "little"))  # mode
        self.assertEqual(d[96:100], (726010000).to_bytes(4, "little"))
        self.assertEqual(d[100:104], (726010682).to_bytes(4, "little"))
        self.assertEqual(d[104:112], (1234).to_bytes(8, "little"))  # length
        self.assertEqual(d[112:116], b"M\0\0\0")             # type 'M', dev 0
        self.assertEqual(self.m.bytes(0x3000 + 116, 4), b"\xAA" * 4)

    def test_fstat_of_a_directory_carries_chdir(self):
        d = p9run.Kernel.dir_bytes("x", os.stat(self.root))
        self.assertEqual(d[95] & 0x80, 0x80)                  # mode CHDIR
        self.assertEqual(d[87] & 0x80, 0x80)                  # qid CHDIR

    def test_fstat_of_a_closed_fd_is_ebadfd(self):
        self.assertEqual(self.k.call(11, self._args(7, 0x3000)), 0xFFFFFFFF)
        self.assertEqual(self.k.errstr, b"fd out of range or not open")

    def test_fstat_to_an_odd_buffer_stops(self):
        self.k.fds[3] = open(__file__, "rb")
        self.addCleanup(self.k.fds[3].close)
        with self.assertRaisesRegex(p9run.Stop, "odd address"):
            self.k.call(11, self._args(3, 0x3002))

    def test_fstat_of_the_console_is_refused(self):
        with self.assertRaisesRegex(p9run.Stop, "console"):
            self.k.call(11, self._args(1, 0x3000))

    def test_rfork_rfnoteg_returns_zero(self):
        self.assertEqual(self.k.call(19, self._args(8)), 0)

    def test_rfork_of_a_process_is_refused(self):
        with self.assertRaisesRegex(p9run.Stop, r"rfork\(0x14\): RFPROC"):
            self.k.call(19, self._args(0x14))                # fork()

    def test_rfork_other_flags_are_refused(self):
        for flag in (0x1, 0x2, 0x4, 0x9):
            with self.subTest(flag=flag):
                with self.assertRaisesRegex(p9run.Stop, "only RFNOTEG"):
                    self.k.call(19, self._args(flag))

    def _args(self, *args):
        sp = 0x4000
        for i, v in enumerate(args):
            self.m.set_word(sp + 4 + 4 * i, v)
        return sp


class Ar(Tree):
    """The shipped `ar` and `rl` against the shipped libc.a (A3)."""

    MEMBERS = ["abort.z", "strlen.z", "getfcr.z"]

    def setUp(self):
        super().setUp()
        self.shipped = LIBC.read_bytes()
        shutil.copy(LIBC, self.root / "libc.a")
        self.entries = {n: (h, b) for n, h, b, _o in archive(self.shipped)}

    def test_ar_t_lists_every_member(self):
        status, console, _k, _n = run(self.root, BIN / "ar", "t", "libc.a")
        self.assertEqual(status, "exits('')")
        self.assertEqual(console.decode().split(),
                         [n for n, _h, _b, _o in archive(self.shipped)])

    def test_ar_x_extracts_members_byte_exact(self):
        status, _c, _k, _n = run(self.root, BIN / "ar", "x", "libc.a",
                                 *self.MEMBERS)
        self.assertEqual(status, "exits('')")
        for n in self.MEMBERS:
            self.assertEqual((self.root / n).read_bytes(), self.entries[n][1])

    def put_members(self):
        """The members' bytes, dated and moded as their headers say."""
        for n in self.MEMBERS:
            hdr, body = self.entries[n]
            (self.root / n).write_bytes(body)
            os.chmod(self.root / n, int(hdr[40:48].decode().strip(), 8))
            t = int(hdr[16:28].decode().strip())
            os.utime(self.root / n, (t, t))

    def test_ar_vu_rebuilds_the_shipped_members_and_headers(self):
        self.put_members()
        status, console, k, _n = run(self.root, BIN / "ar", "vu", "new.a",
                                     *self.MEMBERS)
        self.assertEqual(status, "exits('')")
        self.assertEqual(console, b"ar: creating new.a\n" + b"".join(
            b"a - " + n.encode() + b"\n" for n in self.MEMBERS))
        self.assertIn("fstat", [name for name, _r in k.trace])
        made = archive((self.root / "new.a").read_bytes())
        self.assertEqual([(n, h, b) for n, h, b, _o in made],
                         [(n,) + self.entries[n] for n in self.MEMBERS])

    def test_rl_writes_the_table_then_stops_at_its_fork(self):
        self.put_members()
        status, _c, _k, _n = run(self.root, BIN / "ar", "vu", "new.a",
                                 *self.MEMBERS)
        self.assertEqual(status, "exits('')")
        status, _c, _k, _n = run(self.root, BIN / "rl", "new.a")
        # rl.c writerl(): the table is written and closed, then
        # fexec() forks to run ar -- which p9run refuses, loudly.
        self.assertEqual(status, "p9run: refused rfork(0x14): RFPROC (a new "
                         "process) is not modelled")
        hdr = self.entries["__.SYMDEF"][0]
        os.chmod(self.root / "__.SYMDEF", int(hdr[40:48].decode(), 8))
        t = int(hdr[16:28].decode())
        os.utime(self.root / "__.SYMDEF", (t, t))
        # writerl()'s next step, played: ar rb <first member> lib __.SYMDEF
        status, _c, _k, _n = run(self.root, BIN / "ar", "rb", "abort.z",
                                 "new.a", "__.SYMDEF")
        self.assertEqual(status, "exits('')")
        made = (self.root / "new.a").read_bytes()
        self.assertEqual([n for n, _h, _b, _o in archive(made)],
                         ["__.SYMDEF"] + self.MEMBERS)
        # Every entry points at the member that defines it, with the
        # shipped table's names and types in the shipped table's order.
        want = [e for e in symdef_by_member(self.shipped)
                if e[0] in self.MEMBERS]
        self.assertEqual(symdef_by_member(made), want)
        self.assertEqual(len(want), 6)      # abort, strlen, 4 in getfcr


if __name__ == "__main__":
    unittest.main()
