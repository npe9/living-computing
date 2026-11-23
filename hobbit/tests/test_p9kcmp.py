#!/usr/bin/env python3
"""Tests for tools/p9kcmp.py, the comparison of a linked kernel with s9term.

Run from anywhere:

    python3 hobbit/tests/test_p9kcmp.py

What the checks are evidence about
----------------------------------
`p9kcmp` says which of its MUST items agree between a kernel image and
the shipped `s9term`, and exits non-zero only when one does not.  A
kernel linked from the vendored sources (A3, docs/plan9_boot_plan.md)
is compared with it in the long run (`p9kbuild.py link`); the image is
a build product, not committed, so the suite checks the tool here:

* s9term against itself: every MUST item `same`, exit 0;
* a copy of s9term with one thing changed per MUST item: that item (and
  the ones listed with it, which read the same bytes) prints DIFFERENT
  and the exit is 1 -- each of these is an injection;
* a change the tool must only report (a text byte inside a library
  function, away from the entry and streaminit): exit 0;
* the object list recovered from the `z`/`f` history equals the
  link-order table of docs/s9term.md, which until now came from a
  scratch script;
* the device-character decoder reads both widths (s9term's one byte,
  the shipped zc's two-byte runes).

Observed 2026-11-23 when the `initcode` check was deleted from
`compare()`: test_initcode_must failed (exit 0 and no `initcode` line),
and nothing else.  (Recorded below after the run.)
"""

from __future__ import annotations

import io
import pathlib
import struct
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
TOOLS = HERE.parent / "tools"
sys.path.insert(0, str(TOOLS))

import p9exec  # noqa: E402
import p9kcmp  # noqa: E402

S9TERM = p9kcmp.S9TERM
BLOB = S9TERM.read_bytes()
REF = p9kcmp.Image(S9TERM)


def run(blob):
    """compare(blob's image, s9term) -> (exit, {item: same?}, text)."""
    with tempfile.NamedTemporaryFile(suffix=".9term") as f:
        f.write(blob)
        f.flush()
        out = io.StringIO()
        status = p9kcmp.compare(p9kcmp.Image(f.name), REF, out)
    text = out.getvalue()
    items = {}
    section = None
    for line in text.splitlines():
        if line.startswith("MUST"):
            section = "must"
        elif line.startswith("REPORTED"):
            section = None
        elif section == "must" and line.startswith("  "):
            w = line.split()
            items[w[0]] = w[1] == "same"
    return status, items, text


def data_off(va):
    k = REF.k
    return k["data_off"] + va - k["database"]


def set_word(blob, va, value):
    o = data_off(va)
    blob[o:o + 4] = value.to_bytes(4, "little")


def set_parcel(blob, va, value):
    """Text: little-endian 32-bit words, the earlier parcel in bits 31:16."""
    k = REF.k
    o = k["text_off"] + ((va - k["textbase"]) & ~3)
    w = int.from_bytes(blob[o:o + 4], "little")
    if (va - k["textbase"]) & 2:
        w = (w & 0xFFFF0000) | value
    else:
        w = (w & 0xFFFF) | (value << 16)
    blob[o:o + 4] = w.to_bytes(4, "little")


def rename_f(blob, old, new):
    """Rename an `f` (file-name component) symbol record."""
    k = REF.k
    for i in range(k["sym_off"], k["sym_off"] + k["syms"], 28):
        if blob[i + 4] == ord("f") and blob[i + 5:i + 25].split(b"\0")[0] \
                == old:
            blob[i + 5:i + 25] = new.ljust(20, b"\0")
            return
    raise AssertionError(old)


class TestSelf(unittest.TestCase):
    def test_s9term_against_itself(self):
        status, items, text = run(BLOB)
        self.assertEqual(status, 0, text)
        self.assertEqual(sorted(items), sorted(
            ["format", "header", "entry", "objects", "libraries", "kerndate",
             "conffile", "devchar", "devtab", "streams", "initcode"]))
        self.assertTrue(all(items.values()), text)
        self.assertIn("text by object: 0 objects differ", text)


class TestMustItems(unittest.TestCase):
    """One change per MUST item; the DIFFERENT set is what was observed."""

    def changed(self, edit, want):
        blob = bytearray(BLOB)
        edit(blob)
        status, items, text = run(bytes(blob))
        self.assertEqual(status, 1, text)
        self.assertEqual(sorted(k for k, v in items.items() if not v),
                         sorted(want), text)

    def test_format_must(self):
        # Drop the last pc/line byte: the file is no longer 80+text+data+
        # syms+lcsize long.
        self.changed(lambda b: b.__delitem__(-1), ["format"])

    def test_header_must(self):
        # The entry moved two bytes in: still inside the text (format
        # passes) but neither -E nor `_startup`.
        def edit(b):
            b[0x24:0x28] = struct.pack(">I", 0x80004002)
        self.changed(edit, ["header", "entry"])

    def test_entry_instruction_must(self):
        # FLUSHI (2c03) at _startup+2 made FLUSHP.
        self.changed(lambda b: set_parcel(b, 0x80004002, 0x2C04), ["entry"])

    def test_objects_must(self):
        # The first object's history now names another file.
        self.changed(lambda b: rename_f(b, b"raml.s", b"roml.s"),
                     ["objects", "libraries"])

    def test_libraries_must(self):
        # A libgnot object renamed to a libc member's name: libc would
        # come before the rest of libgnot.
        self.changed(lambda b: rename_f(b, b"gaddr.c", b"atol.c"),
                     ["libraries"])

    def test_kerndate_must(self):
        self.changed(lambda b: set_word(b, REF.sym("kerndate"), 721110518),
                     ["kerndate"])

    def test_conffile_must(self):
        def edit(b):
            o = data_off(REF.word(REF.sym("conffile")))
            b[o] = ord("x")
        self.changed(edit, ["conffile"])

    def test_devchar_must(self):
        def edit(b):
            o = data_off(REF.word(REF.sym("devchar")))
            b[o + 1] = ord("C")
        self.changed(edit, ["devchar"])

    def test_devtab_must(self):
        def edit(b):
            base = REF.sym("devtab")
            a, c = REF.word(base), REF.word(base + 4)
            set_word(b, base, c)
            set_word(b, base + 4, a)
        self.changed(edit, ["devtab"])

    def test_streams_must(self):
        # The first `MOV $urpinfo, R4` of streaminit made `$ipinfo`.
        ip = REF.sym("ipinfo")

        def edit(b):
            lo = REF.sym("streaminit", "T")
            parcels = p9exec.parcel_stream(REF.k)
            i = (lo - REF.k["textbase"]) // 2
            j = next(j for j in range(i, i + 40) if parcels[j] == 0xC6FD)
            va = REF.k["textbase"] + 2 * j
            set_parcel(b, va + 2, ip >> 16)
            set_parcel(b, va + 4, ip & 0xFFFF)
        self.changed(edit, ["streams"])

    def test_initcode_must(self):
        def edit(b):
            o = data_off(REF.sym("initcode")) + 40
            b[o] ^= 0xFF
        self.changed(edit, ["initcode"])

    def test_missing_symbol_is_different_not_a_crash(self):
        def edit(b):
            k = REF.k
            for i in range(k["sym_off"], k["sym_off"] + k["syms"], 28):
                if b[i + 5:i + 25].split(b"\0")[0] == b"kerndate":
                    b[i + 5:i + 13] = b"kernDATE"
        self.changed(edit, ["kerndate"])


class TestReportedOnly(unittest.TestCase):
    def test_library_text_byte_is_reported_not_failed(self):
        blob = bytearray(BLOB)
        set_parcel(blob, REF.sym("strtol", "T") + 8, 0x2C04)
        status, items, text = run(bytes(blob))
        self.assertEqual(status, 0, text)
        self.assertTrue(all(items.values()), text)


class TestObjects(unittest.TestCase):
    """docs/s9term.md, "Link order and library members"."""

    def test_link_order_table(self):
        objs = REF.objects()
        names = [o[0].rsplit("/", 1)[-1].rsplit(".", 1)[0] for o in objs]
        firsts = {o[0].rsplit("/", 1)[-1]: (o[1], o[2]) for o in objs}
        self.assertEqual(names[:2], ["raml", "term"])
        self.assertEqual(firsts["raml.s"], ("_startup", 0x80004000))
        self.assertEqual(firsts["term.c"], ("streaminit", 0x800043D6))
        self.assertEqual(firsts["rammain.c"], ("pusharg", 0x80004422))
        self.assertEqual(firsts["gsegment.c"], ("_setdda", 0x800346C4))
        self.assertEqual(firsts["arith.c"], ("add", 0x80038272))
        self.assertEqual(firsts["abs.c"], ("abs", 0x80038992))
        libram = ("rammain mmu page pgrp proc qlock sysproc devroot devcons "
                  "devenv devpipe devproc devsrv devmnt devdup deveia devrtc "
                  "devincon devdk devscsi scsi devwren deviic devether devarp "
                  "deviproute devip tcpinput tcpoutput tcptimer tcpif stil "
                  "devkprof sturp stip stasync stfcall stream fcall scsibuf "
                  "screen devbit trap alarm alloc chan clock dev fault "
                  "taslock segment swap net print queue sysfile "
                  "bbmalloc").split()
        gnot = ("gsegment gaddr gpoint gsubfstring gtexture gbitblt "
                "gbitbltclip").split()
        g = "arith clipline rectclip".split()
        c = ("abs atol crypt memchr memcmp rune strcat strncpy strtol "
             "strtoul utflen utfrune memmove memset strchr strcmp strcpy "
             "strlen strncmp").split()
        self.assertEqual(names[2:], libram + gnot + g + c)
        archives = [("libram.a", set(p9kcmp.kernel_member_names())),
                    ("-lgnot", set(p9kcmp.members(p9kcmp.LIB / "libgnot.a"))),
                    ("-lg", set(p9kcmp.members(p9kcmp.LIB / "libg.a"))),
                    ("-lc", set(p9kcmp.members(p9kcmp.LIB / "libc.a")))]
        self.assertEqual(p9kcmp.assign(objs, archives),
                         ["raml.s", "term.c"] + ["libram.a"] * len(libram)
                         + ["-lgnot"] * len(gnot) + ["-lg"] * len(g)
                         + ["-lc"] * len(c))

    def test_object_sizes_cover_the_text(self):
        sizes = p9kcmp.object_sizes(REF, REF.objects())
        self.assertEqual(sum(n for _p, n in sizes), REF.k["text"])


class TestChars(unittest.TestCase):
    def test_bytes(self):
        self.assertEqual(p9kcmp.chars(b"/ce|\0xx"), ("/ce|", 1))

    def test_runes(self):
        self.assertEqual(p9kcmp.chars("/ce|".encode("utf-16-le") + b"\0\0x"),
                         ("/ce|", 2))

    def test_wide_rune_refused(self):
        with self.assertRaises(ValueError):
            p9kcmp.chars(b"/\0c\0\x00\x01\0\0")


if __name__ == "__main__":
    unittest.main(verbosity=2)
