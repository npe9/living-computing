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

The two-value result contract is checked as a contract: every result the
host model returns must be 0 or the file's length (`Kind.ZERO` /
`Kind.SIZE`), because that is all PSW.F can name; a request that would
need any other value is refused, and these tests pin the refusals.

The stub's shape is checked parcel by parcel: the bootstrap's absolute
jump, the two spins, the two ACKs in the user's stack word R20, and the
generated size immediate.  Injecting a one-parcel change (for example
swapping the ACK values 1 and 2) fails `test_the_handshake_parcels`.
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
        result, kind, what = self.shim.syscall(20, self.SP)
        self.assertEqual(what, "write")
        self.assertEqual(result, len(self.FILE))
        self.assertEqual(kind, p9shim.Kind.SIZE,
                         "write returns the user's n, which is the size")
        self.assertEqual(bytes(self.shim.console), self.FILE)

    def test_a_write_whose_count_the_channel_cannot_name_is_refused(self):
        self.mem.write(self.arg(0), 1)
        self.mem.write(self.arg(1), 0x6000)
        self.mem.write(self.arg(2), 5)
        with self.assertRaises(SystemExit) as ctx:
            self.shim.syscall(20, self.SP)
        self.assertIn("only 0 and", str(ctx.exception))

    def test_read_fills_the_users_buffer_and_returns_the_file_length(self):
        buf = 0x6000
        self.mem.write(self.arg(0), 0)      # fd = stdin
        self.mem.write(self.arg(1), buf)
        self.mem.write(self.arg(2), 8192)
        result, kind, what = self.shim.syscall(15, self.SP)
        self.assertEqual(what, "read")
        self.assertEqual(result, len(self.FILE))
        self.assertEqual(kind, p9shim.Kind.SIZE)
        self.assertEqual(self.mem.read_bytes(buf, len(self.FILE)), self.FILE)

    def test_read_at_eof_returns_zero_through_the_zero_path(self):
        buf = 0x6000
        self.mem.write(self.arg(0), 0)
        self.mem.write(self.arg(1), buf)
        self.mem.write(self.arg(2), 8192)
        self.shim.syscall(15, self.SP)                 # consume the file
        result, kind, what = self.shim.syscall(15, self.SP)
        self.assertEqual(result, 0)
        self.assertEqual(kind, p9shim.Kind.ZERO)

    def test_a_partial_read_is_refused_rather_than_returned_wrong(self):
        self.mem.write(self.arg(0), 0)
        self.mem.write(self.arg(1), 0x6000)
        self.mem.write(self.arg(2), 4)
        with self.assertRaises(SystemExit) as ctx:
            self.shim.syscall(15, self.SP)
        self.assertIn("only 0 and", str(ctx.exception))

    def test_open_returns_the_file_length_as_its_fd(self):
        path = 0x7000
        self.mem.write_bytes(path, self.NAME.encode() + b"\0")
        self.mem.write(self.arg(0), path)
        self.mem.write(self.arg(1), 0)
        result, kind, what = self.shim.syscall(14, self.SP)
        self.assertEqual((result, kind), (len(self.FILE), p9shim.Kind.SIZE))
        buf = 0x6000
        self.mem.write(self.arg(0), len(self.FILE))
        self.mem.write(self.arg(1), buf)
        self.mem.write(self.arg(2), 8192)
        r, _, _ = self.shim.syscall(15, self.SP)
        self.assertEqual(r, len(self.FILE))
        self.assertEqual(self.mem.read_bytes(buf, len(self.FILE)), self.FILE)
        self.mem.write(self.arg(0), len(self.FILE))
        r, kind, what = self.shim.syscall(4, self.SP)
        self.assertEqual((r, kind, what), (0, p9shim.Kind.ZERO, "close"))
        self.assertFalse(self.shim.fd_open(len(self.FILE)))

    def test_exits_has_no_result_and_stops(self):
        result, kind, what = self.shim.syscall(8, self.SP)
        self.assertIsNone(result)
        self.assertIsNone(kind)
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
    SIZE = 7532               # raml.s, the file the default run serves

    def build(self, size=None, entry=None):
        return p9shim.build_stub(entry if entry is not None else self.ENTRY,
                                 self.SIZE if size is None else size)

    def test_the_stub_fits_the_exec_header_exactly(self):
        words, addr, _ = self.build()
        self.assertEqual(len(words) * 4, p9shim.EXEC_HEADER_BYTES)
        for name in ("p9stub", "p9armed", "p9ret"):
            self.assertIn(name, addr)
            self.assertGreaterEqual(addr[name], p9shim.EXEC_HEADER)
            self.assertLess(addr[name], p9shim.EXEC_HEADER + p9shim.EXEC_HEADER_BYTES)

    def test_the_handshake_parcels(self):
        words, addr, _ = self.build()

        def parcel(i):
            return (words[i >> 1] >> (16 if (i & 1) == 0 else 0)) & 0xFFFF

        def at(name):
            return (addr[name] - p9shim.EXEC_HEADER) // 2

        i = at("p9stub")
        self.assertEqual(parcel(i), 0x1000, "JMPFN to itself: wait for F=1")
        self.assertEqual(parcel(i + 1), 0x86FC, "MOV $1,*ACK: ACK 1")
        self.assertEqual(parcel(i + 2), 0x0001)
        self.assertEqual(parcel(i + 3), p9shim.ACK, "the ACK word")
        a = at("p9armed")
        self.assertEqual(parcel(a), 0x1400, "JMPFY to itself: wait for F=0")
        self.assertEqual(parcel(a + 1), 0x86FC, "MOV $2,*ACK: ACK 2")
        self.assertEqual(parcel(a + 2), 0x0002)
        self.assertEqual(parcel(a + 3), p9shim.ACK)
        # default zero, then the branch on the value bit, then the size
        self.assertEqual(parcel(a + 4), 0x7001, "MOV $0,R4")
        self.assertEqual(parcel(a + 5), 0x1004, "JMPFN p9ret")
        self.assertEqual(parcel(a + 6), 0x86FD, "MOV $7532,R4")
        self.assertEqual(parcel(a + 7), 7532)
        self.assertEqual(parcel(a + 8), 0x0004)
        self.assertEqual(parcel(at("p9ret")), 0x0802, "RETURN R0")

    def test_the_stub_is_exactly_the_exec_header(self):
        words, _, _ = self.build()
        self.assertEqual(len(words), 8)
        # the bootstrap's jump is pcrel (the assembler's 0-based layout) and
        # must land on _main when the stub is placed at 0x1000
        p1 = (words[0] & 0xFFFF)
        self.assertEqual(p1 >> 10, 0x03, "JMP")
        disp = p1 & 0x3FF
        self.assertEqual(0x1002 + 2 * disp, self.ENTRY)

    def test_a_large_size_still_fits(self):
        # 0x7fff is the largest size that still encodes as a signed 16-bit
        # immediate; the three-parcel MOV carries it and the stub is 32 bytes.
        words, _, _ = self.build(size=0x7FFF)
        self.assertEqual(len(words) * 4, p9shim.EXEC_HEADER_BYTES)

    def test_a_size_that_needs_the_wide_form_is_refused(self):
        # 0xffff is negative as a 16-bit immediate, so the assembler picks
        # the five-parcel MOV and the stub outgrows the Exec header: the
        # generator must say so rather than overlap the text.
        with self.assertRaises(SystemExit) as ctx:
            self.build(size=0xFFFF)
        self.assertIn("36 bytes", str(ctx.exception))

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
