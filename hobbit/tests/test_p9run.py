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

A3's system calls (2026-11-23: `Redirection`, `Stat`, `Create`,
`Devices`, `Processes`, `ArAndRl`, `KernelInputs`; 50 tests in all).
Nine bugs were injected into tools/p9run.py one at a time
(P9RUN_MAX_STEPS=1700000), the whole file run each time, the saved file
written back after; nothing failed but what is listed:

  convD2M: the length and its high word swapped
      2 tests: Stat fstat-of-a-file, ArAndRl (ar sizes its members by
      dirfstat)
  fstat of a redirected fd says a file (type M), not a pipe
      1 test: Stat fstat-of-a-pipe-and-the-console
  redirected stdout written to the console
      4 tests: Redirection stdin/stdout, Redirection cat, KernelInputs
      mkstreamlist, KernelInputs init.h
  #c/pid not padded to NUMSIZE
      1 test: Devices c_pid (ar's mktemp does not care: it takes digits)
  fork: the child's rfork returns the pid instead of 0
      1 test: ArAndRl
  exec: /bin not bound to /hobbit/bin
      1 test: ArAndRl
  wait returns a pid one too high
      1 test: ArAndRl
  rfork(RFNOTEG) taken as a fork
      2 tests: Processes rfork-without-rfproc, ArAndRl
  create ignores perm
      1 test: Create

Not injected: `#e`, notify, Enochild, the exec of a missing file.

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
the shipped file.  (That table was observed before the merge with the
fork/exec/wait work, against `ar_fstat`/`dir_bytes`, which the merge
replaced by `sys_fstat`/`convD2M`; `test_rl_writes_the_table_then_
stops_at_its_fork` is now `test_rl_writes_the_table_and_its_fork_puts_
it_first`, and the two rfork-refusal tests became
`test_a_fork_that_shares_memory_or_is_recorded_is_refused` and
`test_rfork_group_flags_without_rfproc_return_zero`.  Not re-injected.)

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
import struct
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
HOBBIT = HERE.parent
sys.path.insert(0, str(HOBBIT / "tools"))
sys.path.insert(0, str(HOBBIT / "sem"))
import build_zl_inferno   # noqa: E402
import hobbit_sem as sem  # noqa: E402
import p9kgen             # noqa: E402
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


# --------------------------------------------------------------------
# A3: the system calls the kernel's generated inputs need (tools/p9kgen.py)
# --------------------------------------------------------------------

NUM = {v: k for k, v in p9run.SYSCALLS.items()}
SP = 0x10000            # where a test puts the caller's frame
STR = 0x20000           # strings
BUF = 0x30000           # result buffers


class KernelCall(unittest.TestCase):
    """One system call against a bare machine: the arguments at SP+4..,
    as the libc stub leaves them."""

    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp(prefix="p9run-"))
        self.addCleanup(shutil.rmtree, self.root)
        self.out = io.BytesIO()
        self.console = io.BytesIO()
        self.st = sem.State()
        self.m = p9run.Machine(self.st)
        self.k = p9run.Kernel(str(self.root), self.m, 0x8000, self.console,
                              stdin=b"abc", stdout=self.out)
        self.addCleanup(lambda: [f.close() for f in self.k.fds.values()
                                 if f not in (None, "console")])

    def call(self, name, *args):
        words, s = [], STR
        for a in args:
            if isinstance(a, (str, bytes)):
                b = a.encode() if isinstance(a, str) else a
                self.m.set_bytes(s, b + b"\0")
                words.append(s)
                s += len(b) + 1
            else:
                words.append(a & 0xFFFFFFFF)
        for i, w in enumerate(words):
            self.m.set_word(SP + 4 + 4 * i, w)
        return self.k.call(NUM[name], SP)

    def dir_at(self, addr):
        b = self.m.bytes(addr, p9run.DIRLEN)
        name, uid, gid = (b[i:i + 28].split(b"\0")[0] for i in (0, 28, 56))
        qpath, qvers, mode, atime, mtime, length, hlen = struct.unpack(
            "<7I", b[84:112])
        typ, dev = struct.unpack("<HH", b[112:116])
        return dict(name=name, uid=uid, qpath=qpath, mode=mode, mtime=mtime,
                    length=length, hlen=hlen, type=chr(typ), dev=dev)


class Redirection(KernelCall):
    def test_stdin_is_read_and_stdout_captured_fd2_stays_console(self):
        self.assertEqual(self.call("read", 0, BUF, 2), 2)
        self.assertEqual(self.m.bytes(BUF, 2), b"ab")
        self.assertEqual(self.call("read", 0, BUF, 10), 1)
        self.assertEqual(self.call("read", 0, BUF, 10), 0)   # end of file
        self.m.set_bytes(BUF, b"out")
        self.assertEqual(self.call("write", 1, BUF, 3), 3)
        self.m.set_bytes(BUF, b"err")
        self.assertEqual(self.call("write", 2, BUF, 3), 3)
        self.assertEqual((self.out.getvalue(), self.console.getvalue()),
                         (b"out", b"err"))

    def test_seek_on_a_pipe_is_eisstream(self):
        self.assertEqual(self.call("seek", 0, 0, 0), 0xFFFFFFFF)
        self.assertEqual(self.k.errstr, b"seek on a stream")

    def test_cat_copies_standard_input_to_standard_output(self):
        out = io.BytesIO()
        text = (REL / "sys/src/9/hobbit/term").read_bytes()
        status, steps, _k, _o = p9run.run(str(BIN / "cat"), ["cat"],
                                          str(self.root), MAX_STEPS,
                                          self.console, stdin=text,
                                          stdout=out)
        self.assertEqual((status, out.getvalue(), self.console.getvalue()),
                         ("exits('')", text, b""))


class Stat(KernelCall):
    def test_fstat_of_a_file_is_convD2M_of_the_file_servers_dir(self):
        (self.root / "f.c").write_bytes(b"x" * 1234)
        fd = self.call("open", "f.c", 0)
        self.assertEqual(self.call("fstat", fd, BUF), 0)
        d = self.dir_at(BUF)
        self.assertEqual((d["name"], d["uid"], d["length"], d["hlen"],
                          d["type"], d["mode"] & p9run.CHDIR),
                         (b"f.c", b"bootes", 1234, 0, "M", 0))
        self.assertEqual(d["mtime"],
                         int(os.stat(self.root / "f.c").st_mtime))

    def test_stat_of_a_directory_sets_chdir_in_mode_and_qid(self):
        (self.root / "d").mkdir()
        self.assertEqual(self.call("stat", "/d", BUF), 0)
        d = self.dir_at(BUF)
        self.assertEqual((d["name"], d["mode"] & p9run.CHDIR,
                          d["qpath"] & p9run.CHDIR, d["length"]),
                         (b"d", p9run.CHDIR, p9run.CHDIR, 0))

    def test_stat_of_a_missing_file_fails_with_enonexist(self):
        self.assertEqual(self.call("stat", "nothere", BUF), 0xFFFFFFFF)
        self.assertEqual(self.k.errstr, b"file does not exist")

    def test_fstat_of_a_pipe_and_of_the_console(self):
        self.assertEqual(self.call("fstat", 1, BUF), 0)
        d = self.dir_at(BUF)
        self.assertEqual((d["name"], d["type"], d["qpath"], d["mode"]),
                         (b"pipe", "|", (1 << 5) | 31, 0o666))
        self.assertEqual(self.call("fstat", 2, BUF), 0)
        d = self.dir_at(BUF)
        self.assertEqual((d["name"], d["type"], d["qpath"], d["mtime"]),
                         (b"cons", "c", 3, p9run.KERNDATE))

    def test_fstat_of_a_closed_fd_fails_and_a_device_stat_is_refused(self):
        self.assertEqual(self.call("fstat", 7, BUF), 0xFFFFFFFF)
        with self.assertRaises(p9run.Stop):
            self.call("stat", "#c/cons", BUF)


class Create(KernelCall):
    def test_a_new_files_perm_is_anded_with_the_directorys(self):
        os.chmod(self.root, 0o755)
        self.call("create", "z.out", 1, 0o775)
        self.assertEqual(os.stat(self.root / "z.out").st_mode & 0o777, 0o755)
        os.chmod(self.root / "z.out", 0o600)
        self.call("create", "z.out", 1, 0o775)          # exists: unchanged
        self.assertEqual(os.stat(self.root / "z.out").st_mode & 0o777, 0o600)


class Devices(KernelCall):
    def test_c_pid_reads_readnum_of_the_pid(self):
        fd = self.call("open", "#c/pid", 0)
        self.assertEqual(self.call("read", fd, BUF, 20), 12)
        self.assertEqual(self.m.bytes(BUF, 12), b"          1 ")

    def test_e_is_an_empty_directory(self):
        fd = self.call("open", "#e", 0)
        self.assertEqual(self.call("read", fd, BUF, 116), 0)
        self.call("fstat", fd, BUF)
        d = self.dir_at(BUF)
        self.assertEqual((d["name"], d["type"], d["mode"]),
                         (b".", "e", p9run.CHDIR | 0o700))
        self.assertEqual(self.call("open", "#e/path", 0), 0xFFFFFFFF)

    def test_any_other_device_is_refused(self):
        with self.assertRaises(p9run.Stop):
            self.call("open", "#t/eia1", 0)


class Processes(KernelCall):
    def test_notify_keeps_the_handler(self):
        self.assertEqual(self.call("notify", 0x12D0), 0)
        self.assertEqual(self.k.notify, 0x12D0)

    def test_rfork_without_rfproc(self):
        self.assertEqual(self.call("rfork", p9run.RFNOTEG), 0)
        self.assertEqual(self.k.noteid, 2)
        self.assertEqual(self.call("rfork", p9run.RFNAMEG | p9run.RFCNAMEG),
                         0xFFFFFFFF)
        self.assertEqual(self.k.errstr, b"bad arg in system call")
        with self.assertRaises(p9run.Stop):
            self.call("rfork", p9run.RFCFDG)

    def test_wait_with_no_children_is_enochild(self):
        self.assertEqual(self.call("wait", BUF), 0xFFFFFFFF)
        self.assertEqual(self.k.errstr, b"no living children")

    def test_exec_of_a_missing_file_fails(self):
        self.m.set_word(BUF, 0)
        self.assertEqual(self.call("exec", "/bin/none", BUF), 0xFFFFFFFF)


class ArAndRl(Tree):
    """ar (rfork(RFNOTEG), mktemp: #c/pid and stat) and rl (fork, exec of
    /bin/ar through lib/namespace's bind, wait) on the shipped binaries."""

    def test_ar_then_rl_puts_a_symdef_first(self):
        members = build_zl_inferno.read_members(str(LIBC))
        (self.root / "main9.z").write_bytes(members["main9.z"])
        (self.root / "tmp").mkdir()
        shutil.copytree(BIN, self.root / "hobbit" / "bin")
        status, console, k, _n = run(self.root, BIN / "ar", "vu", "x.a",
                                     "main9.z")
        self.assertEqual(status, "exits('')")
        self.assertEqual(console, b"ar: creating x.a\na - main9.z\n")
        self.assertIn(("rfork", 0), k.trace)
        out = io.BytesIO()
        status, steps, k, _o = p9run.run(str(BIN / "rl"), ["rl", "x.a"],
                                         str(self.root), MAX_STEPS, out)
        self.assertEqual((status, out.getvalue()), ("exits('')", b""))
        # one child: the fork, exec("/bin/ar", "ar rb main9.z x.a
        # __.SYMDEF"), its exits; the parent's wait returns its pid
        (pid, text, csteps, ctrace, cstatus), = k.children
        self.assertEqual((pid, text, cstatus), (2, "ar", "exits('')"))
        self.assertIn(("exec", 0), ctrace)
        self.assertIn(("wait", 2), k.trace)
        self.assertFalse((self.root / "__.SYMDEF").exists())   # removed
        a = (self.root / "x.a").read_bytes()
        self.assertEqual(a[:8], b"!<arch>\n")
        self.assertEqual(a[8:17], b"__.SYMDEF")
        self.assertIn(b"main9.z", a[60:])


class KernelInputs(unittest.TestCase):
    """A sample of tools/p9kgen.py (the whole of it is a recorded long
    run, docs/plan9_boot_plan.md A3): the rc scripts' quoting, a
    sed | awk list, and init.h against the shipped kernel's initcode[]."""

    def setUp(self):
        self.out = pathlib.Path(tempfile.mkdtemp(prefix="p9kgen-"))
        self.addCleanup(shutil.rmtree, self.out)
        p9kgen.make_tree(self.out)
        self.rc = p9kgen.Rc(self.out, io.StringIO())

    def test_rc_pieces_skips_comments_and_takes_here_documents(self):
        p = p9kgen.rc_pieces(p9kgen.BOOT / "mkboot")
        # mkboot's comments quote 'boot', 'misc' and 'cfs.root'; none of
        # them is a piece
        self.assertEqual([k for k, _t in p], ["h", "q", "h", "q", "q"])
        self.assertTrue(p[2][1].startswith("\t{ 0 },\n};\n"))
        p = p9kgen.rc_pieces(p9kgen.PORT / "mkextract")
        self.assertEqual(p[2][1], ' }\n\t\t$0 ~ "^')

    def test_mkstreamlist_term(self):
        # sed '/^$/d; /^#/d' term | awk '...' 'field=^stream'
        out = p9kgen.mklist(self.rc, "mkstreamlist", "stream", "term")
        self.assertEqual(out.split(),
                         [b"sturp.z", b"stip.z", b"stasync.z", b"stfcall.z"])

    def test_init_h_is_the_shipped_kernels_initcode(self):
        text = p9kgen.mkfile_init_h(self.rc).decode()
        mine = p9kgen.c_bytes(text)
        theirs, room = p9kgen.kernel_array("initcode", len(mine))
        self.assertEqual((mine, len(mine), room), (theirs, 60, 60))
        self.assertTrue(text.startswith("uchar initcode[]={\n0x00,0x00,"))


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
        self.assertEqual(d[28:56], b"bootes" + b"\0" * 22)        # uid: eve
        self.assertEqual(d[56:84], b"bootes" + b"\0" * 22)        # gid
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
        d = self.k.dir_entry(str(self.root))
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

    def test_fstat_of_the_console_is_devcons_cons(self):
        # (refused before 2026-11-23: devcons.c consdir "cons" now)
        self.assertEqual(self.k.call(11, self._args(1, 0x3000)), 0)
        self.assertEqual(self.m.bytes(0x3000, 5), b"cons\0")
        self.assertEqual(self.m.bytes(0x3000 + 112, 2), b"c\0")

    def test_rfork_rfnoteg_returns_zero(self):
        self.assertEqual(self.k.call(19, self._args(8)), 0)

    def test_a_fork_that_shares_memory_or_is_recorded_is_refused(self):
        # fork() itself runs now (Processes, ArAndRl, Ar); RFMEM and a
        # fork under --record are what stays refused.
        with self.assertRaisesRegex(p9run.Stop, r"rfork\(0x34\)"):
            self.k.call(19, self._args(0x34))                # RFPROC|RFMEM
        self.k.recording = True
        with self.assertRaisesRegex(p9run.Stop, "recorded"):
            self.k.call(19, self._args(0x14))                # fork()

    def test_rfork_group_flags_without_rfproc_return_zero(self):
        # sysrfork without RFPROC: new name/env/fd/note groups
        for flag in (0x1, 0x2, 0x4, 0x9):
            with self.subTest(flag=flag):
                self.assertEqual(self.k.call(19, self._args(flag)), 0)

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

    def test_rl_writes_the_table_and_its_fork_puts_it_first(self):
        self.put_members()
        status, _c, _k, _n = run(self.root, BIN / "ar", "vu", "new.a",
                                 *self.MEMBERS)
        self.assertEqual(status, "exits('')")
        # rl.c writerl(): the table is written and closed, then fexec()
        # forks and execs `ar rb abort.z new.a __.SYMDEF` and waits.
        # The table's header carries its file's date and mode: the clock
        # fixed at the shipped table's date, the directory 0775 so that
        # create's 0664 survives (open(2): perm & the directory's).
        hdr = self.entries["__.SYMDEF"][0]
        os.chmod(self.root, 0o775)
        shutil.copytree(BIN, self.root / "hobbit" / "bin")   # /bin/ar
        out = io.BytesIO()
        status, _s, k, _o = p9run.run(
            str(BIN / "rl"), ["rl", "new.a"], str(self.root), MAX_STEPS, out,
            clock=int(hdr[16:28].decode()))
        self.assertEqual((status, out.getvalue()), ("exits('')", b""))
        self.assertEqual([(t, s) for _p, t, _n, _tr, s in k.children],
                         [("ar", "exits('')")])
        self.assertFalse((self.root / "__.SYMDEF").exists())
        made = (self.root / "new.a").read_bytes()
        mine = archive(made)[0][1]          # all but the size (3 members)
        self.assertEqual((mine[:48], mine[58:]), (hdr[:48], hdr[58:]))
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
