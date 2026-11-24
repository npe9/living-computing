#!/usr/bin/env python3
"""tools/p9symdef.py: every byte of the shipped __.SYMDEF tables is
accounted for.

Past each name's NUL, a table byte is either one an earlier name of the
same member left in readar()'s `Prog p` (replayed from libmach's
obj.c/zobj.c) or the stack at readar()'s entry, which /mips/bin/rl's
frames predict (the module doc).  The shipped hobbit libc.a: 631 and
1,992 of its 2,623 such bytes, none left over.  The Hobbit rl on the
model (p9kbuild archeck) differs from it in exactly 212 stack bytes;
here that is checked on a table with the model's id[17] (i's low byte,
3, little-endian) written in.

Discriminating, observed 2026-11-23: five bugs injected into
tools/p9symdef.py one at a time, this file run each time, the exact
patch reversed after; nothing failed but what is listed.

  MIPS_PRE's Bseek argument little-endian (01 00 00 00 at id[5..8])
      4 tests: shipped libc, every library (libc.a only), the Hobbit-rl
      table, the in-call change
  buf predicted one byte early (id[8..15])
      4 tests (8 failures): shipped libc, every library (all five), the
      Hobbit-rl table, the in-call change
  _readz does not store the name's terminator
      4 tests (8 errors: explain() stops, readrl's names no longer
      those of the table), all five libraries
  objlookup's first test drops `names[id] >= i`
      1 test: every library, libgnot.a only (an error: explain() stops
      on a name that no longer matches)
  readar also processes the record that ends at the member's end
      0 tests: no shipped member ends in a record whose processing would
      change a 'T'/'D' name.  Not discriminated here.
"""

import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
TOOLS = HERE.parent / "tools"
sys.path.insert(0, str(TOOLS))
import p9symdef  # noqa: E402

LIB = TOOLS / "plan9-1e" / "hobbit" / "lib"


class Shipped(unittest.TestCase):
    def test_shipped_libc(self):
        c, odd = p9symdef.explain((LIB / "libc.a").read_bytes())
        self.assertEqual(odd, [])
        self.assertEqual(c["entries"], 201)
        self.assertEqual((c["in_call"], c["in_call_same"]), (631, 631))
        self.assertEqual((c["pre"], c["pre_mips"], c["pre_unknown"]),
                         (1992, 1992, 0))

    def test_every_vendored_library(self):
        for name in ("libc.a", "libbio.a", "libg.a", "libgnot.a",
                     "libauth.a"):
            with self.subTest(lib=name):
                c, odd = p9symdef.explain((LIB / name).read_bytes())
                self.assertEqual(odd, [])
                self.assertEqual(c["pre_unknown"], 0)
                self.assertGreater(c["pre_mips"], 0)

    def test_the_hobbit_rl_table_differs_in_its_stack_bytes(self):
        data = (LIB / "libc.a").read_bytes()
        body = bytearray(p9symdef.symdef_body(data))
        for k in range(len(body) // p9symdef.RLENTSIZE):
            body[p9symdef.RLENTSIZE * k + 4 + 17] = 3   # objtype's i, LE
        c, odd = p9symdef.explain(data, bytes(body))
        self.assertEqual(len(odd), 201)
        self.assertEqual({o[2] for o in odd}, {17})
        self.assertTrue(all(o[3] == "MIPS 00" and o[4] == 3 for o in odd))
        self.assertEqual(c["in_call_same"], 631)

    def test_an_in_call_byte_changed_is_found(self):
        data = (LIB / "libc.a").read_bytes()
        entries = p9symdef.readrl(data)
        k, j = next((k, j) for k, e in enumerate(entries)
                    for j in range(len(e[0]) + 1, p9symdef.NNAME)
                    if isinstance(e[1][j], int))
        body = bytearray(p9symdef.symdef_body(data))
        body[p9symdef.RLENTSIZE * k + 4 + j] ^= 0xFF
        _c, odd = p9symdef.explain(data, bytes(body))
        self.assertEqual(len(odd), 1)
        self.assertEqual(odd[0][2], j)
        self.assertTrue(odd[0][3].startswith("in-call"))


if __name__ == "__main__":
    unittest.main()
