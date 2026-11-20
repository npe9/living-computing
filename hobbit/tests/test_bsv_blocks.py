#!/usr/bin/env python3
"""Tests for tools/bsv_blocks.py, the declaration-level `.bsv` structure tool.

Each test is a case the tool got wrong during its construction: the
expressions with braces, the interface and method *declarations* that have
no `end…`, the one-line `function … = …;` whose `=` may sit on the next
line, the unbalanced file it must refuse, and the word-boundary rule of
`rename`.  The fixtures are strings, so the tests do not depend on the
repository's own sources (they would go stale with them).
"""

import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(os.path.dirname(HERE), "tools", "bsv_blocks.py")
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))

import bsv_blocks as bb  # noqa: E402


FIXTURE = """\
package P;
typedef struct {
  Word a;
  Bit#(3) b;
} Pair;

interface Top;
  method Action put(Word x);
  method Word get();
endinterface

module mkTop(Top);
  Reg#(Word) r <- mkReg(0);
  interface Server srv;
  interface Put request = toPut(mkFIFOF);

  function Word twice(Word x) =
    (x << 1) | {30'd0, x[1:0]};

  function Bool isZero(Word x);
    Bool z = (x == 0);
    return z;
  endfunction

  rule step;
    let lane = {28'd0, r[3:0]};
    r <= lane;
  endrule
endmodule
endpackage
"""


def run_tool(*args):
    return subprocess.run([sys.executable, TOOL, *args],
                          capture_output=True, text=True)


class StructureTest(unittest.TestCase):
    def test_module_ends_at_its_own_endmodule(self):
        root, _ = bb.parse_blocks(FIXTURE)
        mods = [b for b in bb.walk(root) if b.kind == "module"]
        self.assertEqual([m.name for m in mods], ["mkTop"])
        self.assertTrue(mods[0].closed)
        # the module's last line is `endmodule`, not the package's
        self.assertEqual(mods[0].end_line, FIXTURE[:FIXTURE.index("endmodule")].count("\n") + 1)

    def test_interface_and_method_declarations_are_not_blocks(self):
        root, _ = bb.parse_blocks(FIXTURE)
        # `interface Top;` is the real interface block ...
        tops = [b for b in bb.walk(root) if b.kind == "interface"]
        self.assertEqual([(t.name, t.start_line, t.end_line) for t in tops],
                         [("Top", 7, 10)])
        # ... and the two declaration forms inside the module are not blocks
        self.assertEqual([b for b in bb.walk(root) if b.start_line in (14, 15)], [])

    def test_one_line_function_with_the_expression_on_the_next_line(self):
        root, _ = bb.parse_blocks(FIXTURE)
        fns = [b for b in bb.walk(root) if b.kind == "function"]
        self.assertEqual([f.start_line for f in fns], [20])
        self.assertEqual(fns[0].name, "isZero")

    def test_braces_in_expressions_do_not_close_a_struct(self):
        root, _ = bb.parse_blocks(FIXTURE)
        structs = [b for b in bb.walk(root) if b.kind == "struct"]
        self.assertTrue(structs[0].closed, "the `{30'd0, x[1:0]}` braces must not close the struct")
        self.assertEqual(structs[0].start_line, 2)

    def test_unclosed_module_is_reported(self):
        with tempfile.NamedTemporaryFile("w", suffix=".bsv", delete=False) as f:
            f.write("module m;\n  rule r;\n    x <= 1;\n  endrule\n")
            path = f.name
        try:
            out = run_tool("check", path)
            self.assertEqual(out.returncode, 1)
            self.assertIn("unclosed module m", out.stdout)
        finally:
            os.unlink(path)

    def test_rename_respects_word_boundaries_and_comments(self):
        text = "  rule r;\n    // step is not stepped\n    step <= step + stepish;\n  endrule\n"
        seg, count = bb.rewrite_span(text, 0, len(text), "step", "advance")
        self.assertEqual(count, 2)
        self.assertIn("// step is not stepped", seg)
        self.assertIn("advance <= advance + stepish", seg)

    def test_move_dry_run_reports_without_writing(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "a.bsv")
            dst = os.path.join(d, "b.bsv")
            open(src, "w").write("module a;\n  rule gone;\n    x <= 1;\n  endrule\nendmodule\n")
            open(dst, "w").write("module b;\n  rule keep;\n  endrule\nendmodule\n")
            before = open(src).read(), open(dst).read()
            out = run_tool("move", src, "--block", "rule gone", "--to", dst, "--module", "b")
            self.assertEqual(out.returncode, 0, out.stderr)
            self.assertIn("rule gone;", out.stdout)
            self.assertEqual((open(src).read(), open(dst).read()), before)


if __name__ == "__main__":
    unittest.main()
