#!/usr/bin/env python3
"""Tests for tools/p9exec.py's kernel-image mode, and the s9term facts.

Run from anywhere:

    python3 hobbit/tests/test_p9exec.py

What the checks are evidence about
----------------------------------
`tools/plan9-1e/hobbit/s9term` is the kernel image the 1st Edition ships
(550,846 bytes).  `p9exec.read_kernel` reads it by zl/asm.c's case 1
(`-H1`); `check_kernel` states what asm.c and pass.c make true of any
such file.  The tests pin:

* the header s9term carries, word by word (docs/s9term.md, "Header");
* that `check_kernel` passes it, and *fails* each corrupted copy below
  for the reason named -- the negatives are the injections: a wrong
  fixed header word, a truncated file, a moved `etext`, a data base that
  no longer follows the text;
* the build facts docs/s9term.md reads out of the image, at the file
  offsets it gives: KERNDATE, the device and stream lists, the conffile,
  the embedded boot program's Exec header, the first instructions at the
  entry against raml.s;
* that the user-binary path is unchanged (a shipped binary is not a
  kernel, and `read_kernel` refuses it).

Observed when the file-size check in `check_kernel` was deleted
(2026-11-23): `test_truncated_file_fails` failed, and nothing else.
"""

from __future__ import annotations

import os
import pathlib
import struct
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
TOOLS = HERE.parent / "tools"
sys.path.insert(0, str(TOOLS))

import p9exec  # noqa: E402

REL = TOOLS / "plan9-1e"
S9TERM = REL / "hobbit" / "s9term"


def va_off(k, va):
    """File offset of a data address (data is stored as is, at 80+text)."""
    assert k["database"] <= va < k["database"] + k["data"], hex(va)
    return k["data_off"] + (va - k["database"])


def word(k, va):
    o = va_off(k, va)
    return int.from_bytes(k["blob"][o:o + 4], "little")


def sym(syms, name, types="DdBbTt"):
    hits = [v for v, t, n in syms if n == name and t in types]
    assert len(hits) == 1, (name, hits)
    return hits[0]


class TestHeader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.k = p9exec.read_kernel(str(S9TERM))
        cls.syms = p9exec.kernel_symbols(cls.k)

    def test_header_words(self):
        w = self.k["words"]
        self.assertEqual(len(self.k["blob"]), 550846)
        self.assertEqual(w[0], 0x01610000)          # magic 0x161, 0 sections
        self.assertEqual(w[2], 0x46e84)             # 80 + text + data
        self.assertEqual(w[3], 0x379e0)             # 8,136 symbols
        self.assertEqual(w[5], 0x0197011f)          # 407<<16 | 0437
        self.assertEqual((w[6], w[7], w[8]), (0x35b40, 0x112f4, 0x180ac))
        self.assertEqual((w[9], w[10], w[11], w[12]),
                         (0x80004000, 0x80004000, 0x80039b40, 0x8004ae34))
        self.assertEqual(w[14], 0x7f5a)             # pc/line table
        self.assertEqual(len(self.syms), 8136)

    def test_checks_pass(self):
        self.assertEqual(p9exec.check_kernel(self.k, self.syms), [])

    def test_entry_is_startup_and_decodes_as_raml_s(self):
        self.assertEqual(sym(self.syms, "_startup", "T"), self.k["entry"])
        parcels = p9exec.parcel_stream(self.k)
        first = [parcels[i] for i in range(4)]
        # raml.s:13 FLUSH = FLUSHP; FLUSHI (niladic 0x0B subcodes 4, 3),
        # then CPU, the escape of `MOV $..., %CONFIG` (raml.s:14).
        self.assertEqual(first, [0x2c04, 0x2c03, 0x2c00, 0xc6f7])

    def test_is_kernel_detection(self):
        self.assertTrue(p9exec.is_kernel(str(S9TERM)))
        cat = str(REL / "hobbit" / "bin" / "cat")
        self.assertFalse(p9exec.is_kernel(cat))
        with self.assertRaises(SystemExit):
            p9exec.read_kernel(cat)
        self.assertEqual(p9exec.read(cat)["magic"], 0x197)

    def test_main_accepts_the_image(self):
        self.assertEqual(p9exec.main([str(S9TERM), "--decode", "0"]), 0)


class TestCorruptedCopies(unittest.TestCase):
    """Each corruption must fail check_kernel for its own reason."""

    def corrupt(self, edit):
        blob = bytearray(S9TERM.read_bytes())
        blob = edit(blob)
        fd, path = tempfile.mkstemp()
        os.write(fd, bytes(blob))
        os.close(fd)
        self.addCleanup(os.remove, path)
        k = p9exec.read_kernel(path)
        return " | ".join(p9exec.check_kernel(k, p9exec.kernel_symbols(k)))

    def test_fixed_header_word_fails(self):
        def edit(b):
            b[13 * 4:14 * 4] = (0).to_bytes(4, "big")
            return b
        self.assertIn("header word 13", self.corrupt(edit))

    def test_truncated_file_fails(self):
        self.assertIn("80 + text + data + syms + lcsize",
                      self.corrupt(lambda b: b[:-4]))

    def test_moved_etext_fails(self):
        k = p9exec.read_kernel(str(S9TERM))
        syms = p9exec.kernel_symbols(k)
        i = [n for _v, _t, n in syms].index("etext")
        off = k["sym_off"] + 28 * i

        def edit(b):
            b[off:off + 4] = (0x80039b44).to_bytes(4, "big")
            return b
        self.assertIn("`etext` is 0x80039b44", self.corrupt(edit))

    def test_data_base_fails(self):
        def edit(b):
            b[11 * 4:12 * 4] = (0x80040000).to_bytes(4, "big")
            return b
        got = self.corrupt(edit)
        self.assertIn("bss base != data base + data", got)


class TestBuildFacts(unittest.TestCase):
    """The numbers docs/s9term.md reports, read where it says they are."""

    @classmethod
    def setUpClass(cls):
        cls.k = p9exec.read_kernel(str(S9TERM))
        cls.syms = p9exec.kernel_symbols(cls.k)

    def cstr(self, va):
        o = va_off(self.k, va)
        return self.k["blob"][o:self.k["blob"].index(b"\0", o)]

    def test_kerndate(self):
        va = sym(self.syms, "kerndate")
        self.assertEqual(va_off(self.k, va), 0x35cc4)
        self.assertEqual(word(self.k, va), 721110517)   # 1992-11-07 04:28:37 UTC

    def test_device_list_is_the_term_config(self):
        p = word(self.k, sym(self.syms, "devchar"))
        self.assertEqual(va_off(self.k, p), 0x46d30)
        # One byte per device, in the order of sys/src/9/hobbit/term's
        # `dev` section: root cons env pipe proc srv mnt dup iic eia rtc
        # incon dk scsi wren ether arp iproute ip bit kprof.
        self.assertEqual(self.cstr(p), b"/ce|psMd2trikSwlaPIbT")
        self.assertEqual(self.cstr(word(self.k, sym(self.syms, "conffile"))),
                         b"term")

    def test_stream_list_order(self):
        # streaminit (term.c, from mkdevc): newqinfo(&urpinfo) ... in the
        # order of term's `stream` section.  Each is `MOV $xinfo, R4`
        # (c6fd <hi> <lo> 0000 0004) and a CALL.
        lo = sym(self.syms, "streaminit", "T")
        parcels = p9exec.parcel_stream(self.k)
        i = (lo - self.k["textbase"]) // 2
        seen = []
        for j in range(i, i + 40):
            if parcels[j] == 0xc6fd:
                seen.append((parcels[j + 1] << 16) | parcels[j + 2])
        want = [sym(self.syms, n + "info") for n in
                ("urp", "ip", "async", "fcall")]
        self.assertEqual(seen, want)

    def test_embedded_boot_program(self):
        va = sym(self.syms, "bootcode")
        n = word(self.k, sym(self.syms, "bootlen"))
        self.assertEqual(n, 26796)
        o = va_off(self.k, va)
        # mkroot: `strip boot.out` then xd -1x: the file's bytes as is, so
        # the Exec header is big-endian as in any 1e binary.
        magic, text, data, bss, syms, entry, spsz, pcsz = struct.unpack(
            ">8I", self.k["blob"][o:o + 32])
        self.assertEqual(magic, 0x197)
        self.assertEqual((text, data, bss, syms, entry),
                         (0x5cf8, 0xb94, 0x4d0, 0, 0x66d2))
        self.assertEqual(32 + text + data, n)       # stripped: no symbols

    def test_initcode(self):
        o = va_off(self.k, sym(self.syms, "initcode"))
        magic, text, data, bss, syms, entry = struct.unpack(
            ">6I", self.k["blob"][o:o + 24])
        self.assertEqual((magic, text, data, syms, entry),
                         (0x197, 0x14, 0x8, 0, 0x1020))


if __name__ == "__main__":
    unittest.main(verbosity=2)
