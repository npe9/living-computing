#!/usr/bin/env python3
"""Tests for the A1 syscall shim, hobbit/tools/p9shim.py.

Run from anywhere:

    python3 hobbit/tests/test_p9shim.py

What the checks are evidence about
----------------------------------
The syscall numbers are not taken from memory: each row of `SYSCALLS`
carries the parcels of the 1e libc stub as they sit in
`tools/plan9-1e/hobbit/bin/cat`, and `test_ids_come_from_the_stub_parcels`
decodes the number back out of those parcels.  A wrong number in the
table, or a wrong parcel beside it, fails there with the parcel printed.

The argument convention is checked against what the stubs imply: the
arguments are the three words at CSP+4/+8/+12 (the accumulator first) and
the result comes back in the accumulator, because the stub's own
`RETURN R0` pops nothing (offset 0, PRM p. 3-40).

The result contract is the stub's: the host writes the result word and
then the ready word, and the stub returns exactly that word in the
accumulator.  So the host model may return any 32-bit value, and the
tests pin the values that matter to 1e's cat: a partial read returns its
count and advances the offset, end of file returns 0, open returns
descriptor 3, write returns the caller's n.

The stub's shape is checked parcel by parcel: the bootstrap's jump, the
wait on RDY, the load of RES into the accumulator, and RETURN R0.

Injections made and reverted (2026-11-19), with the tests observed to
fail -- each list is the whole failure set of the 21 tests:

  * RDY and RES swapped in `stub_source`: `test_the_stub_parcels`;
  * `MOV *$RES, R4` changed to `MOV *$RES, R8`: `test_the_stub_parcels`;
  * `JMPTY` changed to `JMPFY` (the loop sense inverted, which is how the
    stub first went wrong): `test_the_stub_parcels`;
  * `take = min(n, size - off)` changed to `take = n`:
    `test_read_fills_the_users_buffer_and_returns_the_file_length`,
    `test_read_at_eof_returns_zero` and
    `test_open_returns_descriptor_three_and_reads_from_the_top`.
    `test_a_partial_read_returns_its_count_and_advances` does *not* fail
    under it (its requests are shorter than the file), so the short-file
    bound is pinned by the other three.

(Injecting by overwriting the file within one second left a stale
`tools/__pycache__` once and showed a failure on the restored tree;
remove the cache when a restored run disagrees with the source.)
"""

from __future__ import annotations

import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
HOBBIT = HERE.parent
sys.path.insert(0, str(HOBBIT / "tools"))

import p9shim  # noqa: E402


class TestSyscallTable(unittest.TestCase):
    def test_ids_come_from_the_stub_parcels(self):
        for num, s in sorted(p9shim.SYSCALLS.items()):
            with self.subTest(syscall=s.name):
                p0 = s.parcels[0]
                if p0 & 0x8000:
                    # three-parcel KCALL imm32 (Table 1-19, PRM p. 1-24)
                    self.assertEqual((p0 >> 8) & 0x3F, 0x00,
                                     f"{s.name}: parcel {p0:#06x} is not a monadic KCALL")
                    imm = (s.parcels[1] << 16) | s.parcels[2]
                    self.assertEqual(imm, num,
                                     f"{s.name}: KCALL ${imm} at 0x{s.stub:04x}")
                else:
                    # one-parcel KCALL imm10: zero-extended, x4 (PRM p. 3-29)
                    self.assertEqual(p0 >> 10, 0x00,
                                     f"{s.name}: parcel {p0:#06x} is not a KCALL")
                    self.assertEqual((p0 & 0x3FF) * 4, num,
                                     f"{s.name}: KCALL immediate in {p0:#06x}")
                # every one of them ends in RETURN R0 (0x0802)
                self.assertEqual(s.parcels[-1], 0x0802,
                                 f"{s.name}: not RETURN R0")

    def test_the_set_is_the_six_the_boot_plan_needs(self):
        self.assertEqual(sorted(p9shim.SYSCALLS), [1, 4, 8, 14, 15, 20])
        self.assertEqual([p9shim.SYSCALLS[n].name for n in (1, 4, 8, 14, 15, 20)],
                         ["errstr", "close", "exits", "open", "read", "write"])

    def test_argument_addresses_are_the_accumulator_and_up(self):
        self.assertEqual(p9shim.args_of(0x5000), (0x5004, 0x5008, 0x500C))
        self.assertEqual(p9shim.arg_addr(0x5000, 0), 0x5004)
        self.assertEqual(p9shim.arg_addr(0x5000, 2), 0x500C)

    def test_exits_carries_the_message_pointer_in_the_accumulator(self):
        # main9.s: MOV $_exits<>+0(SB), R4 ; CALL exits
        self.assertEqual(p9shim.SYSCALLS[8].args, ("msg",))


class TestHostSyscalls(unittest.TestCase):
    SP = 0x5000
    FILE = b"hello, hobbit\n"
    NAME = "/tmp/p9shim.txt"

    def setUp(self):
        self.mem = p9shim.Mem()
        self.shim = p9shim.Shim(self.FILE, self.NAME, self.mem)
        for i in range(3):
            self.mem.write(self.SP + 4 + 4 * i, 0)

    def arg(self, k):
        return self.SP + 4 + 4 * k

    def test_write_moves_the_users_buffer_to_the_console(self):
        buf = 0x6000
        self.mem.write_bytes(buf, self.FILE)
        self.mem.write(self.arg(0), 1)          # fd = stdout
        self.mem.write(self.arg(1), buf)
        self.mem.write(self.arg(2), len(self.FILE))
        result, what = self.shim.syscall(20, self.SP)
        self.assertEqual(what, "write")
        self.assertEqual(result, len(self.FILE))
        self.assertEqual(bytes(self.shim.console), self.FILE)

    def test_a_short_write_returns_the_callers_count(self):
        buf = 0x6001                            # not word aligned
        self.mem.write_bytes(buf, self.FILE)
        self.mem.write(self.arg(0), 2)          # fd = stderr
        self.mem.write(self.arg(1), buf)
        self.mem.write(self.arg(2), 5)
        result, _ = self.shim.syscall(20, self.SP)
        self.assertEqual(result, 5)
        self.assertEqual(bytes(self.shim.console), self.FILE[:5])

    def test_a_write_to_a_file_descriptor_is_refused(self):
        self.mem.write(self.arg(0), 3)
        with self.assertRaises(SystemExit) as ctx:
            self.shim.syscall(20, self.SP)
        self.assertIn("only the console", str(ctx.exception))

    def test_bytes_are_big_endian_in_the_word(self):
        # PRM p. 1-4: the byte at a word address is bits 31:24.
        self.mem.write_bytes(0x6000, b"\x11\x22\x33\x44")
        self.assertEqual(self.mem.read(0x6000), 0x11223344)
        self.assertEqual(self.mem.read_byte(0x6001), 0x22)

    def test_read_fills_the_users_buffer_and_returns_the_file_length(self):
        buf = 0x6000
        self.mem.write(self.arg(0), 0)      # fd = stdin
        self.mem.write(self.arg(1), buf)
        self.mem.write(self.arg(2), 8192)
        result, what = self.shim.syscall(15, self.SP)
        self.assertEqual(what, "read")
        self.assertEqual(result, len(self.FILE))
        self.assertEqual(self.mem.read_bytes(buf, len(self.FILE)), self.FILE)

    def test_read_at_eof_returns_zero(self):
        buf = 0x6000
        self.mem.write(self.arg(0), 0)
        self.mem.write(self.arg(1), buf)
        self.mem.write(self.arg(2), 8192)
        self.shim.syscall(15, self.SP)                 # consume the file
        result, what = self.shim.syscall(15, self.SP)
        self.assertEqual((result, what), (0, "read"))

    def test_a_partial_read_returns_its_count_and_advances(self):
        buf = 0x6000
        self.mem.write(self.arg(0), 0)
        self.mem.write(self.arg(1), buf)
        self.mem.write(self.arg(2), 4)
        result, _ = self.shim.syscall(15, self.SP)
        self.assertEqual(result, 4)
        self.assertEqual(self.mem.read_bytes(buf, 4), self.FILE[:4])
        result, _ = self.shim.syscall(15, self.SP)
        self.assertEqual(result, 4)
        self.assertEqual(self.mem.read_bytes(buf, 4), self.FILE[4:8])

    def test_a_read_of_an_unopened_descriptor_is_refused(self):
        self.mem.write(self.arg(0), p9shim.FILE_FD)
        self.mem.write(self.arg(1), 0x6000)
        self.mem.write(self.arg(2), 4)
        with self.assertRaises(SystemExit) as ctx:
            self.shim.syscall(15, self.SP)
        self.assertIn("refused read", str(ctx.exception))

    def test_open_returns_descriptor_three_and_reads_from_the_top(self):
        path = 0x7000
        self.mem.write_bytes(path, self.NAME.encode() + b"\0")
        self.mem.write(self.arg(0), path)
        self.mem.write(self.arg(1), 0)
        result, what = self.shim.syscall(14, self.SP)
        self.assertEqual((result, what), (3, "open"))
        buf = 0x6000
        self.mem.write(self.arg(0), 3)
        self.mem.write(self.arg(1), buf)
        self.mem.write(self.arg(2), 8192)
        r, _ = self.shim.syscall(15, self.SP)
        self.assertEqual(r, len(self.FILE))
        self.assertEqual(self.mem.read_bytes(buf, len(self.FILE)), self.FILE)
        self.mem.write(self.arg(0), 3)
        self.assertEqual(self.shim.syscall(4, self.SP), (0, "close"))
        self.assertFalse(self.shim.fd_open(3))

    def test_exits_has_no_result_and_stops(self):
        result, what = self.shim.syscall(8, self.SP)
        self.assertIsNone(result)
        self.assertEqual(what, "exits")

    def test_unknown_syscall_is_refused_with_the_number_and_the_cite(self):
        for num in (0, 2, 3, 21, 99):
            with self.subTest(num=num):
                with self.assertRaises(SystemExit) as ctx:
                    self.shim.syscall(num, self.SP)
                msg = str(ctx.exception)
                self.assertIn(str(num), msg)
                self.assertIn("libc.a", msg)
                self.assertIn("write.z", msg)


class TestStub(unittest.TestCase):
    ENTRY = 0x12BC            # cat's _main

    def build(self, entry=None):
        return p9shim.build_stub(entry if entry is not None else self.ENTRY)

    @staticmethod
    def parcel(words, i):
        return (words[i >> 1] >> (16 if (i & 1) == 0 else 0)) & 0xFFFF

    def test_the_stub_fits_the_exec_header(self):
        words, addr, _ = self.build()
        self.assertLessEqual(len(words) * 4, p9shim.EXEC_HEADER_BYTES)
        self.assertEqual(len(words), 5, "ten parcels")
        self.assertEqual(addr["p9stub"], p9shim.EXEC_HEADER + 4)

    def test_the_stub_parcels(self):
        words, addr, _ = self.build()
        i = (addr["p9stub"] - p9shim.EXEC_HEADER) // 2
        got = [self.parcel(words, i + k) for k in range(8)]
        self.assertEqual(got[0], 0x9FFC, "CMPEQ $imm16, *$abs16 (Table 1-18)")
        self.assertEqual(got[1], 0x0000, "the immediate: zero")
        self.assertEqual(got[2], p9shim.RDY, "the ready word")
        self.assertEqual(got[3], 0x1FFD, "JMPTY back three parcels")
        self.assertEqual(got[4], 0x86CD, "MOV *$abs16, Roffset")
        self.assertEqual(got[5], p9shim.RES, "the result word")
        self.assertEqual(got[6], 0x0004, "R4: the accumulator (p. 1-7)")
        self.assertEqual(got[7], 0x0802, "RETURN R0")

    def test_the_device_words_are_distinct_and_outside_the_user_stack(self):
        devs = {p9shim.RDY, p9shim.RES, p9shim.DB, p9shim.VB}
        self.assertEqual(len(devs), 4)
        self.assertEqual(p9shim.DB, p9shim.ISP0 - 12, "KCALL's *(ISP-12) = src")
        for d in devs:
            self.assertLess(d, p9shim.EXEC_HEADER)

    def test_the_bootstrap_jump_lands_on_main(self):
        words, _, _ = self.build()
        self.assertEqual(self.parcel(words, 0), 0x7021, "MOV $1,R4: argc")
        # the jump is pcrel (the assembler's 0-based layout) and must land
        # on _main when the stub is placed at 0x1000
        p1 = self.parcel(words, 1)
        self.assertEqual(p1 >> 10, 0x03, "JMP")
        disp = p1 & 0x3FF
        self.assertEqual(0x1002 + 2 * disp, self.ENTRY)

    def test_a_window_that_is_not_the_exec_header_is_refused(self):
        with self.assertRaises(SystemExit) as ctx:
            p9shim.check_window(0x2AD0)      # echo's _main
        self.assertIn("0x2800", str(ctx.exception))

    def test_a_file_beyond_the_immediate_is_refused(self):
        with self.assertRaises(SystemExit) as ctx:
            p9shim.Shim(b"x" * 0x10000, "f", p9shim.Mem())
        self.assertIn("16 bits", str(ctx.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
