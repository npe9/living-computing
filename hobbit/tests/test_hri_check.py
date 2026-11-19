#!/usr/bin/env python3
"""Discriminating tests for hri_check.py.

Every test drives the real CLI as a subprocess and asserts the exact exit
status and the named first divergence.  The suite is deliberately noisy about
which check catches which bug.

OBSERVED failures:
    Deliberate injection: compare() unconditionally added "mask" to its ignore
    set.  Running ``python3 tests/test_hri_check.py`` then produced 27 tests,
    1 failure, exit status 1:

        test_mask_change  FAIL
            AssertionError: 0 != 1 : Summary: instructions compared=1 result=PASS

    No other test failed.  Reverting the injection restored 27/27 passing.
"""

import os
import shlex
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "hri_check.py")

BASE = (
    "HRI pc=0000 insn=00000000 sp=00000000>00000000 "
    "msp=00000000>00000000 we=0 addr=00000000 data=00000000 "
    "mask=00 trap=0"
)


def line(**overrides):
    """Build a well-formed HRI line with optional field overrides."""
    fields = {
        "pc": "0000",
        "insn": "00000000",
        "sp": "00000000>00000000",
        "msp": "00000000>00000000",
        "we": "0",
        "addr": "00000000",
        "data": "00000000",
        "mask": "00",
        "trap": "0",
    }
    fields.update(overrides)
    return (
        "HRI pc=%(pc)s insn=%(insn)s sp=%(sp)s msp=%(msp)s we=%(we)s "
        "addr=%(addr)s data=%(data)s mask=%(mask)s trap=%(trap)s" % fields
    )


class RvfiCheckTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dut_path = os.path.join(self.tmp.name, "dut.txt")
        self.spec_path = os.path.join(self.tmp.name, "spec.txt")

    def tearDown(self):
        self.tmp.cleanup()

    # -- helpers ---------------------------------------------------------
    def write(self, path, lines):
        with open(path, "w", encoding="utf-8") as f:
            for item in lines:
                f.write(item + "\n")

    def run_files(self, dut_lines, spec_lines, *extra):
        self.write(self.dut_path, dut_lines)
        self.write(self.spec_path, spec_lines)
        return subprocess.run(
            [
                sys.executable,
                SCRIPT,
                "--dut-lines",
                self.dut_path,
                "--spec-lines",
                self.spec_path,
            ]
            + list(extra),
            capture_output=True,
            text=True,
        )

    def run_commands(self, dut_cmd, spec_cmd, *extra):
        return subprocess.run(
            [sys.executable, SCRIPT, "--dut", dut_cmd, "--spec", spec_cmd]
            + list(extra),
            capture_output=True,
            text=True,
        )

    def assert_divergence(self, result, expected):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(expected, result.stdout)
        self.assertIn("result=FAIL", result.stdout)

    # -- one changed field per class ------------------------------------
    def test_pc_change(self):
        """Catches a differ that ignores the pc field."""
        self.assert_divergence(
            self.run_files([line(pc="0000")], [line(pc="0001")]),
            "line 1 field PC: dut=0x0000 spec=0x0001 pc=0x0000",
        )

    def test_insn_change(self):
        """Catches a differ that ignores the insn field."""
        self.assert_divergence(
            self.run_files([line(insn="00000000")], [line(insn="00000001")]),
            "line 1 field INSN: dut=0x00000000 spec=0x00000001 pc=0x0000",
        )

    def test_sp_change(self):
        """Catches a differ that ignores sp before>after."""
        self.assert_divergence(
            self.run_files(
                [line(sp="00000000>00000000")],
                [line(sp="00000001>00000000")],
            ),
            "line 1 field SP: dut=0x00000000>0x00000000 "
            "spec=0x00000001>0x00000000 pc=0x0000",
        )

    def test_msp_change(self):
        """Catches a differ that ignores msp before>after."""
        self.assert_divergence(
            self.run_files(
                [line(msp="00000000>00000000")],
                [line(msp="00000000>00000001")],
            ),
            "line 1 field MSP: dut=0x00000000>0x00000000 "
            "spec=0x00000000>0x00000001 pc=0x0000",
        )

    def test_we_change(self):
        """Catches a differ that ignores the write-enable field."""
        self.assert_divergence(
            self.run_files([line(we="0")], [line(we="1")]),
            "line 1 field WE: dut=0x0 spec=0x1 pc=0x0000",
        )

    def test_addr_change(self):
        """Catches a differ that ignores the write address."""
        self.assert_divergence(
            self.run_files([line(addr="00000000")], [line(addr="00000001")]),
            "line 1 field ADDR: dut=0x00000000 spec=0x00000001 pc=0x0000",
        )

    def test_data_change(self):
        """Catches a differ that ignores the write data."""
        self.assert_divergence(
            self.run_files([line(data="00000000")], [line(data="00000001")]),
            "line 1 field DATA: dut=0x00000000 spec=0x00000001 pc=0x0000",
        )

    def test_mask_change(self):
        """Catches a differ that ignores the write mask."""
        self.assert_divergence(
            self.run_files([line(mask="00")], [line(mask="01")]),
            "line 1 field MASK: dut=0x00 spec=0x01 pc=0x0000",
        )

    def test_trap_change(self):
        """Catches a differ that ignores the trap flag."""
        self.assert_divergence(
            self.run_files([line(trap="0")], [line(trap="1")]),
            "line 1 field TRAP: dut=0x0 spec=0x1 pc=0x0000",
        )

    # -- line count ------------------------------------------------------
    def test_added_line(self):
        """Catches a differ that only compares the common prefix."""
        self.assert_divergence(
            self.run_files(
                [line(pc="0000"), line(pc="0004")],
                [line(pc="0000")],
            ),
            "line 2 field LENGTH: dut=2 spec=1 pc=0x0004",
        )

    def test_dropped_line(self):
        """Catches a differ that only compares the common prefix."""
        self.assert_divergence(
            self.run_files(
                [line(pc="0000")],
                [line(pc="0000"), line(pc="0004")],
            ),
            "line 2 field LENGTH: dut=1 spec=2 pc=0x0004",
        )

    # -- malformed lines -------------------------------------------------
    def test_malformed_dut_line(self):
        """Catches a differ that silently skips a bad DUT line."""
        bad = line(mask="00")[: -len(" trap=0")]
        result = self.run_files([bad], [line()])
        self.assertEqual(result.returncode, 1)
        self.assertIn("malformed HRI line at line 1 in DUT", result.stderr)

    def test_malformed_spec_line(self):
        """Catches a differ that silently skips a bad spec line."""
        bad = line(mask="00")[: -len(" trap=0")]
        result = self.run_files([line()], [bad])
        self.assertEqual(result.returncode, 1)
        self.assertIn("malformed HRI line at line 1 in SPEC", result.stderr)

    def test_malformed_line_2(self):
        """Catches a differ that only validates the first line."""
        bad = line(pc="0004")[: -len(" trap=0")]
        result = self.run_files([line(), bad], [line(), line(pc="0004")])
        self.assertEqual(result.returncode, 1)
        self.assertIn("malformed HRI line at line 2 in DUT", result.stderr)

    def test_malformed_extra_tail(self):
        """Catches a differ that reports a length mismatch without parsing the extra line."""
        bad = line(pc="0004")[: -len(" trap=0")]
        result = self.run_files([line(), bad], [line()])
        self.assertEqual(result.returncode, 1)
        self.assertIn("malformed HRI line at line 2 in DUT", result.stderr)

    # -- ignore-fields / max-lines --------------------------------------
    def test_ignore_fields(self):
        """Catches a differ that ignores --ignore-fields."""
        result = self.run_files(
            [line(mask="00")], [line(mask="01")], "--ignore-fields", "mask"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("result=PASS", result.stdout)

    def test_ignore_sp_msp(self):
        """Catches a differ that ignores sp/msp ignoring."""
        result = self.run_files(
            [line(sp="00000000>00000000", msp="00000000>00000000")],
            [line(sp="00000001>00000002", msp="00000003>00000004")],
            "--ignore-fields",
            "sp msp",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_ignore_unknown_field(self):
        """Catches a differ that silently accepts a bogus ignored field."""
        result = self.run_files(
            [line()], [line()], "--ignore-fields", "bogus"
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown --ignore-fields", result.stderr)

    def test_max_lines(self):
        """Catches a differ that ignores --max-lines."""
        result = self.run_files(
            [line(pc="0000"), line(pc="0004")],
            [line(pc="0000"), line(pc="0004", trap="1")],
            "--max-lines",
            "1",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("result=PASS", result.stdout)

    def test_max_lines_zero(self):
        """Catches a differ that treats --max-lines 0 as unlimited."""
        result = self.run_files(
            [line(pc="0000")], [line(pc="0001")], "--max-lines", "0"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("instructions compared=0", result.stdout)

    # -- first divergence and pc ----------------------------------------
    def test_first_divergence_only(self):
        """Catches a differ that reports every mismatch instead of the first."""
        result = self.run_files(
            [line(pc="0000"), line(pc="0004", addr="00000000")],
            [line(pc="0001"), line(pc="0004", addr="00000002")],
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("line 1 field PC", result.stdout)
        self.assertNotIn("line 2", result.stdout)

    def test_pc_of_diverging_instruction(self):
        """Catches a differ that prints the wrong instruction pc."""
        result = self.run_files(
            [line(pc="0000"), line(pc="0004", addr="00000000")],
            [line(pc="0000"), line(pc="0004", addr="00000002")],
        )
        self.assert_divergence(
            result,
            "line 2 field ADDR: dut=0x00000000 spec=0x00000002 pc=0x0004",
        )

    # -- command mode ----------------------------------------------------
    def test_command_mode_identical(self):
        """Catches a differ that only supports --dut-lines/--spec-lines."""
        self.write(self.dut_path, [line()])
        self.write(self.spec_path, [line()])
        result = self.run_commands(
            "cat " + shlex.quote(self.dut_path),
            "cat " + shlex.quote(self.spec_path),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("result=PASS", result.stdout)

    def test_command_mode_diverging(self):
        """Catches a differ that runs commands but does not compare them."""
        self.write(self.dut_path, [line(pc="0000")])
        self.write(self.spec_path, [line(pc="0001")])
        result = self.run_commands(
            "cat " + shlex.quote(self.dut_path),
            "cat " + shlex.quote(self.spec_path),
        )
        self.assert_divergence(
            result, "line 1 field PC: dut=0x0000 spec=0x0001 pc=0x0000"
        )

    def test_command_failure(self):
        """Catches a differ that silently treats a failed command as empty."""
        result = self.run_commands("false", "true")
        self.assertEqual(result.returncode, 1)
        self.assertIn("command failed with exit status 1", result.stderr)

    # -- exit status and summary ----------------------------------------
    def test_identical_pass(self):
        """Catches a differ that exits nonzero on identical traces."""
        result = self.run_files([line()], [line()])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("instructions compared=1", result.stdout)
        self.assertIn("result=PASS", result.stdout)

    def test_empty_traces_pass(self):
        """Catches a differ that crashes on empty traces."""
        result = self.run_files([], [])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("instructions compared=0", result.stdout)
        self.assertIn("result=PASS", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
