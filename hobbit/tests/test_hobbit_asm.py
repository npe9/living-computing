#!/usr/bin/env python3
"""Tests for hobbit/asm/hobbit_asm.py.

Run from anywhere:

    python3 hobbit/tests/test_hobbit_asm.py

The expected encodings are transcribed from the ATT92010 Programmer's
Reference Manual (January 1993).  Page numbers below are the printed page
numbers, not PDF page indices.  Plan 9's 1st Edition linker is the second
oracle in test_plan9_opcode_cross_check.

Bug injection, observed 2026-11-19
----------------------------------
Injected bug: in one_parcel_encoding(), the source field (bits 9:5) and
destination field (bits 4:0) were swapped:

    - return [(opcode << 10) | (_field5(sc, sv) << 5) | _field5(dc, dv)]
    + return [(opcode << 10) | (_field5(dc, dv) << 5) | _field5(sc, sv)]

Observed failing checks with that bug in place (the OBSERVED set, not a
prediction; 16 failures):
    TestHandEncodings.test_hand_checked_encodings
        [subtests: ADD $3,R8; MOV R4,R8; MOV *R4,R8; MOV R4,*R8;
         CMPEQ $5,R4; CMPGT R4,R8; MOVA R4,R8]
    TestHandEncodings.test_hand_cases_round_trip
        [the same seven subtests]
    TestRoundTripAndErrors.test_cli_assemble_disassemble_round_trip
        [disassembly of the sample became ADD $2,R12]
    TestRoundTripAndErrors.test_width_suffix_forces_three_parcel_form
        [the control assertion on 0x5062]
All other checks (Tables 1-18/1-20 opcode grid, the 3/5-parcel hand
cases, test_one_parcel_disassembly_text, malformed-input diagnostics, and
the Plan 9 optab cross-check) passed, which is the point: a field swap
does not move the opcode field, and symmetric one-parcel cases such as
ADD3 $1,R4 and MOV $1,R4 encode the same either way.  Reverted; the
suite is green again.
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ASM_PATH = ROOT / "asm" / "hobbit_asm.py"
OPTAB_PATH = (ROOT / "tools" / "plan9-1e" / "sys" / "src" / "cmd" / "zl" /
              "optab.c")

_spec = importlib.util.spec_from_file_location("hobbit_asm", ASM_PATH)
ha = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(ha)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def assemble(text: str, allow_unimplemented: bool = False):
    """Return (raw parcels, listing, addresses) for assembly text."""
    listing, parcels, addresses = ha.listing_from_assembly(
        text, "<test>", allow_unimplemented)
    return parcels, listing, addresses


def words_for(parcels):
    padded, _ = ha.pad_parcels(list(parcels))
    return ha.parcels_to_words(padded)


def disassemble(parcels):
    # Exact parcel sequence: do not add the 32-bit word pad here, so a
    # single one-parcel instruction does not grow a trailing NOP.
    return ha.disassemble_parcels(list(parcels))


def run_cli(*args: str):
    return subprocess.run([sys.executable, str(ASM_PATH), *args],
                          capture_output=True, text=True)


# ---------------------------------------------------------------------------
# 1. The opcode[5:0] grid of Tables 1-18 / 1-20 (printed pp. 1-23, 1-25)
# ---------------------------------------------------------------------------

# Rows are opcode[5:3], columns opcode[2:0].  None is the manual's
# "unimp*" cell, whose unimplemented-instruction sequence is executed.
GRID = [
    ["MONADIC", "ORI", "ANDI", "ADDI", "MOVA", "UREM", "MOV", "DQM"],
    [None, None, None, None, "TADD", "TSUB", None, None],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, "CMPGT", "CMPHI", "CMPEQ"],
    ["SUB", "OR", "AND", "ADD", "XOR", "REM", "MUL", "DIV"],
    [None, None, None, None, "SHR", "USHR", "SHL", "UDIV"],
    ["SUB3", "OR3", "AND3", "ADD3", "XOR3", "REM3", "MUL3", "DIV3"],
    [None, None, None, None, "SHR3", "USHR3", "SHL3", None],
]

MANUAL_OPCODE = {}
for _row, _cells in enumerate(GRID):
    for _col, _name in enumerate(_cells):
        if _name and _name != "MONADIC":
            MANUAL_OPCODE[_name] = (_row << 3) | _col


class TestOpcodeGrid(unittest.TestCase):
    def test_grid_has_35_mnemonics(self):
        # PRM Tables 1-18/1-20: 35 populated grid cells after excluding
        # the monadic cell.
        self.assertEqual(len(MANUAL_OPCODE), 35)

    def test_three_parcel_opcode_fields_match_tables_1_18(self):
        """Every non-unimp cell of Table 1-18 (printed p. 1-23)."""
        for name, expected in sorted(MANUAL_OPCODE.items()):
            with self.subTest(mnemonic=name):
                if name == "MOVA":
                    # MOVA rejects an immediate source (PRM p. 3-33).
                    text = ".3 MOVA R0x1234,R4\n"
                else:
                    text = f".3 {name} $0x1000,R4\n"
                parcels, _, _ = assemble(text)
                self.assertEqual(len(parcels), 3,
                                 f"{name}: three-parcel form length")
                first = parcels[0]
                self.assertEqual(first & 0xC000, 0x8000,
                                 f"{name}: '10' length prefix, PRM p. 1-23")
                self.assertEqual((first >> 8) & 0x3F, expected,
                                 f"{name}: Table 1-18 opcode[5:0]")

    def test_five_parcel_opcode_fields_match_tables_1_20(self):
        """Every non-unimp cell of Table 1-20 (printed p. 1-25)."""
        for name, expected in sorted(MANUAL_OPCODE.items()):
            with self.subTest(mnemonic=name):
                if name == "MOVA":
                    text = ".5 MOVA R0x1234,R4\n"
                else:
                    text = f".5 {name} $0x12345678,R4\n"
                parcels, _, _ = assemble(text)
                self.assertEqual(len(parcels), 5,
                                 f"{name}: five-parcel form length")
                first = parcels[0]
                self.assertEqual(first & 0xC000, 0xC000,
                                 f"{name}: '11' length prefix, PRM p. 1-24")
                self.assertEqual((first >> 8) & 0x3F, expected,
                                 f"{name}: Table 1-20 opcode[5:0]")


# ---------------------------------------------------------------------------
# 2. Hand-checked encodings
# ---------------------------------------------------------------------------

# Each entry states the printed source of the bit pattern.  Fields:
# (assembly text, exact parcels, citation).
HAND_CASES = [
    # Table 1-17 (p. 1-22) and the instruction pages.  Niladic parcel is
    # 0x0b00 | subcode[9:0].
    ("NOP", [0x2C02], "Table 1-17 p. 1-22; NOP p. 3-35 (0x0B/0x2)"),
    ("CLRE", [0x2C0A], "Table 1-17 p. 1-22; CLRE p. 3-12 (0x0B/0xA)"),
    ("CPU", [0x2C00], "Table 1-17 p. 1-22; CPU p. 3-14 (0x0B/0x0)"),
    ("RETURN R16", [0x0806],
     "Table 1-16 p. 1-22; RETURN p. 3-40 (subcode 2, offset 16/16=1)"),
    ("CATCH R32", [0x0809],
     "Table 1-16 p. 1-22; CATCH p. 3-11 (subcode 1, offset 32/16=2)"),
    ("POPN R16", [0x0807],
     "Table 1-16 p. 1-22; POPN p. 3-38 (subcode 3)"),
    ("ENTER R-16", [0x0BFC],
     "Table 1-16 p. 1-22; ENTER p. 3-21 (one-filled 8-bit -1, subcode 0)"),
    ("ENTER R-4096", [0x0800],
     "ENTER p. 3-21 (one-filled 8-bit 0 is -4096, not zero)"),
    ("ENTER R-2048", [0x0A00],
     "ENTER p. 3-21 (one-filled 8-bit 0x80 is -2048)"),
    # Table 1-15 (p. 1-22), five-bit source in 9:5 and destination in
    # 4:0; stack offsets are divided by four (PRM p. 1-21).
    ("ADD $3,R8", [0x5062],
     "Table 1-15 p. 1-22 ADD.CS (0x14); ADD p. 3-5"),
    ("ADD3 $1,R4", [0x5421],
     "Table 1-15 p. 1-22 ADD3.CS (0x15); ADD p. 3-5"),
    ("MOV $1,R4", [0x7021],
     "Table 1-15 p. 1-22 MOV.CS (0x1C); MOV p. 3-32"),
    ("MOV R4,R8", [0x6022],
     "Table 1-15 p. 1-22 MOV.SS (0x18); MOV p. 3-32"),
    ("MOV *R4,R8", [0x6422],
     "Table 1-15 p. 1-22 MOV.IS (0x19); MOV p. 3-32"),
    ("MOV R4,*R8", [0x6822],
     "Table 1-15 p. 1-22 MOV.SI (0x1A); MOV p. 3-32"),
    ("CMPEQ $5,R4", [0x40A1],
     "Table 1-15 p. 1-22 CMPEQ.CS (0x10); CMP p. 3-13"),
    ("CMPGT R4,R8", [0x4422],
     "Table 1-15 p. 1-22 CMPGT.SS (0x11); CMP p. 3-13"),
    ("SHL3 $5,R4", [0x78A1],
     "Table 1-15 p. 1-22 SHL3.CS (0x1E); SHL p. 3-41"),
    ("SHR3 $31,R4", [0x7FE1],
     "Table 1-15 p. 1-22 SHR3.CS (0x1F); SHR p. 3-41"),
    ("MOVA R4,R8", [0x7422],
     "Table 1-15 p. 1-22 MOVA.SS (0x1D); MOVA p. 3-33"),
    ("KCALL $16", [0x0004],
     "Table 1-15 p. 1-22 KCALL; KCALL p. 3-29 (imm10*4)"),
    ("CALL 0x0006", [0x0403],
     "Table 1-15 p. 1-22 CALL; CALL p. 3-9 (pcrel10*2, offset 6)"),
    ("JMP 0x0004", [0x0C02],
     "Table 1-15 p. 1-22 JMP; JMP p. 3-28 (pcrel10*2, offset 4)"),
    ("JMPFN 0x0004", [0x1002],
     "Table 1-15 p. 1-22 JMPFN; JMP p. 3-28"),
    ("JMPTY 0x0004", [0x1C02],
     "Table 1-15 p. 1-22 JMPTY; JMP p. 3-28"),
    # Three-parcel monadic: 10 | opcode 000000 | smode | subcode, then a
    # 32-bit operand (PRM p. 1-23, Table 1-19 p. 1-24, Table 1-23 p. 1-26).
    (".3 LDRAA 0x0004", [0x80EA, 0x0000, 0x0004],
     "LDRAA p. 3-31 (0x00/0xA, flow32); Table 1-19 p. 1-24"),
    # Three-parcel dyadic: 10 | opcode[5:0] | smode | dmode, then source
    # and destination 16-bit fields (PRM p. 1-23, Table 1-21 p. 1-25).
    (".3 ADD $0x1000,R4", [0xA3FD, 0x1000, 0x0004],
     "Table 1-18 p. 1-23 ADD=0x23; ADD p. 3-5; Table 1-21 p. 1-25"),
    # Five-parcel: 11 | opcode[5:0] | smode | dmode, then source-hi,
    # source-lo, destination-hi, destination-lo (PRM pp. 1-24 to 1-25).
    (".5 ADD $0x12345678,R4",
     [0xE3FD, 0x1234, 0x5678, 0x0000, 0x0004],
     "Table 1-20 p. 1-25 ADD=0x23; ADD p. 3-5"),
    # CPU is a prefix; the following instruction uses mode 0x7 for the
    # register, and the register number is in the operand field
    # (CPU p. 3-14; Table 1-22 p. 1-26; Table 1-24 p. 1-26).  SHAD=0x6.
    ("MOV $0x1234,%SHAD", [0x2C00, 0x86F7, 0x1234, 0x0006],
     "CPU p. 3-14; Tables 1-22/1-24 p. 1-26; MOV p. 3-32"),
    ("ADD $16,%SHAD", [0x2C00, 0xA3F7, 0x0010, 0x0006],
     "CPU p. 3-14; ADD p. 3-5; Tables 1-22/1-24 p. 1-26"),
    # The manual's own PSW-sequence example: MOV %SP,%SHAD is a register
    # read of SP (code 3) and a register write of SHAD (code 6).
    ("MOV %SP,%SHAD", [0x2C00, 0x8677, 0x0003, 0x0006],
     "PRM p. 1-15 (MOV %SP, %SHAD); CPU p. 3-14; Tables 1-22/1-24 p. 1-26"),
]


class TestHandEncodings(unittest.TestCase):
    def test_hand_checked_encodings(self):
        self.assertGreaterEqual(len(HAND_CASES), 12)
        for text, expected, citation in HAND_CASES:
            with self.subTest(text=text, citation=citation):
                parcels, _, _ = assemble(text)
                got = " ".join(f"{p:04X}" for p in parcels)
                want = " ".join(f"{p:04X}" for p in expected)
                self.assertEqual(parcels, expected,
                                 f"{text}: got [{got}], expected [{want}]; "
                                 f"{citation}")

    def test_one_parcel_disassembly_text(self):
        # Canonical text for the one-parcel forms.  The disassembler must
        # not turn a known form into a plausible but different mnemonic.
        expected = {
            0x2C02: "NOP",
            0x2C0A: "CLRE",
            0x2C00: "CPU",
            0x0806: "RETURN R16",
            0x0809: "CATCH R32",
            0x0807: "POPN R16",
            0x0BFC: "ENTER R-16",
            0x0800: "ENTER R-4096",
            0x0A00: "ENTER R-2048",
            0x5062: "ADD $3,R8",
            0x5421: "ADD3 $1,R4",
            0x7021: "MOV $1,R4",
            0x6022: "MOV R4,R8",
            0x6422: "MOV *R4,R8",
            0x6822: "MOV R4,*R8",
            0x40A1: "CMPEQ $5,R4",
            0x4422: "CMPGT R4,R8",
            0x78A1: "SHL3 $5,R4",
            0x7FE1: "SHR3 $31,R4",
            0x7422: "MOVA R4,R8",
            0x0004: "KCALL $0x10",
            0x0403: "CALL 0x0006",
            0x0C02: "JMP 0x0004",
            0x1002: "JMPFN 0x0004",
            0x1C02: "JMPTY 0x0004",
        }
        for parcel, text in expected.items():
            with self.subTest(parcel=f"{parcel:04X}"):
                self.assertEqual(disassemble([parcel]), [text])

    def test_hand_cases_round_trip(self):
        # Disassemble every known hand case and assemble the text again.
        for text, expected, citation in HAND_CASES:
            with self.subTest(text=text, citation=citation):
                lines = disassemble(expected)
                again, _, _ = assemble("\n".join(lines) + "\n")
                self.assertEqual(again, expected,
                                 f"round-trip through {lines!r}")


# ---------------------------------------------------------------------------
# 3. CLI round-trip and diagnostics
# ---------------------------------------------------------------------------

SAMPLE = """\
; a small program with 1-, 3- and 5-parcel instructions
start:  NOP
        ADD $3,R8
        .3 ADD $0x1000,R4
        .5 ADD $0x12345678,R4
        MOV $0x1234,%SHAD
        .3 CALL later
        LDRAA target
        ENTER R-16
        CATCH R32
        JMP start
later:  CLRE
target: .1 NOP
"""


class TestRoundTripAndErrors(unittest.TestCase):
    def test_cli_assemble_disassemble_round_trip(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            src = td / "sample.s"
            img = td / "sample.hex"
            lst = td / "sample.lst"
            src.write_text(SAMPLE, encoding="ascii")
            r = run_cli("-o", str(img), "--list", str(lst), str(src))
            self.assertEqual(r.returncode, 0, r.stderr)
            text = img.read_text(encoding="ascii")
            lines = text.splitlines()
            self.assertTrue(lines)
            self.assertTrue(all(re.fullmatch(r"[0-9A-F]{8}", l) for l in lines),
                            "image must be 8 hex digits per 32-bit word")
            listing = lst.read_text(encoding="ascii")
            self.assertIn("000000: 2C02", listing)
            self.assertIn("E3FD 1234 5678 0000 0004", listing)
            self.assertIn("%SHAD", listing)

            r = run_cli("--disasm", str(img))
            self.assertEqual(r.returncode, 0, r.stderr)
            dis = r.stdout
            for needed in ("NOP", "ADD $3,R8", ".3 ADD $4096,R4",
                           ".5 ADD $305419896,R4", "CPU",
                           ".3 MOV $4660,%SHAD", ".3 CALL", ".3 LDRAA",
                           "ENTER R-16", "CATCH R32", "JMP 0x0000"):
                self.assertIn(needed, dis)

            dis_src = td / "sample.dis.s"
            img2 = td / "sample2.hex"
            dis_src.write_text(dis, encoding="ascii")
            r = run_cli("-o", str(img2), str(dis_src))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(img.read_text(encoding="ascii"),
                             img2.read_text(encoding="ascii"),
                             "disassembly must reassemble bit-exactly")

    def test_bare_stack_offset_names_the_required_operand(self):
        # A bare number is a label/absolute operand, not a stack offset.
        # The diagnostic must name the stack syntax the instruction wants.
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            src = td / "w.s"
            src.write_text("        ENTER -16\n", encoding="ascii")
            r = run_cli("-o", str(td / "w.hex"), str(src))
            self.assertNotEqual(r.returncode, 0)
            self.assertIn(
                f"{src}:1: error: ENTER expects a stack offset "
                f"(ENTER R-16; PRM p. 3-21)", r.stderr)

    def test_bad_mnemonic_reports_file_and_line(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            src = td / "bad.s"
            src.write_text("; comment\nFOO R1\n", encoding="ascii")
            r = run_cli("-o", str(td / "x.hex"), str(src))
            self.assertNotEqual(r.returncode, 0)
            self.assertIn(f"{src}:2: error: unknown mnemonic FOO", r.stderr)

    def test_wrong_parcel_length_reports_file_and_line(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            src = td / "badlen.s"
            src.write_text("; comment\n.5 NOP\n", encoding="ascii")
            r = run_cli("-o", str(td / "x.hex"), str(src))
            self.assertNotEqual(r.returncode, 0)
            self.assertIn(f"{src}:2: error:", r.stderr)
            self.assertIn("no 10-byte form", r.stderr)

    def test_truncated_image_reports_file_and_line(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            img = td / "trunc.hex"
            img.write_text("C0000000\n", encoding="ascii")
            r = run_cli("--disasm", str(img))
            self.assertNotEqual(r.returncode, 0)
            self.assertIn(f"{img}:1: error: truncated five-parcel", r.stderr)

    def test_bad_image_line_reports_file_and_line(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            img = td / "bad.hex"
            img.write_text("ZZZZZZZZ\n", encoding="ascii")
            r = run_cli("--disasm", str(img))
            self.assertNotEqual(r.returncode, 0)
            self.assertIn(f"{img}:1: error: image word must be exactly",
                          r.stderr)

    def test_unimplemented_parcel_is_clearly_marked(self):
        # One-parcel opcode 0x08 is an unimp* cell of Table 1-15 (p. 1-22).
        self.assertEqual(disassemble([0x2000]),
                         ["unimplemented 0x2000 ; one-parcel opcode 0x08 "
                          "(Table 1-15, p. 1-22)"])
        # Three-parcel opcode 0x10 is an unimp* cell of Table 1-18 (p. 1-23).
        text = disassemble([0x9000, 0x0000, 0x0000])
        self.assertIn("unimplemented", text[0])
        self.assertIn("opcode 0x10", text[0])

    def test_mode_7_without_cpu_is_unsigned_half_stack_offset(self):
        # Table 1-21 (p. 1-25): mode 0x7 is Roffset:UH unless a CPU
        # prefix makes it the register mode (Table 1-22, p. 1-26).
        # MetaWare High C emits it (43 sites in Be's 1994 kernels; these
        # are three of them and one five-parcel form).  Injection,
        # observed 2026-11-24: restoring the old "mode 7 needs CPU"
        # refusal in both operand() helpers failed this test only.
        cases = [
            ([0xA1F7, 0x0004, 0x002A], ".3 OR $4,R42:UH"),
            ([0x867A, 0x000E, 0x0008], ".3 MOV R14:UH,*R8:H"),
            ([0x9F7B, 0x000C, 0x0014], ".3 CMPEQ R12:UH,*R20:UH"),
            ([0xC67D, 0x0000, 0x0084, 0x0000, 0x0040],
             ".5 MOV R132:UH,R64"),
        ]
        for parcels, text in cases:
            with self.subTest(text=text):
                self.assertEqual(disassemble(parcels), [text])
                again, _, _ = assemble(text + "\n")
                self.assertEqual(again, parcels)
        # With the prefix, 0x7 is still a register (Table 1-22).
        self.assertEqual(disassemble([0x2C00, 0x867D, 0x000A, 0x0004])[1],
                         ".3 MOV %ID,R4")

    def test_allow_unimplemented_flag_marks_listing(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            src = td / "flush.s"
            src.write_text("FLUSHD\n", encoding="ascii")
            r = run_cli("-o", str(td / "x.hex"), str(src))
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("PRM p. 3-22", r.stderr)

            lst = td / "flush.lst"
            r = run_cli("--allow-unimplemented", "-o", str(td / "x.hex"),
                        "--list", str(lst), str(src))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("2C06", lst.read_text(encoding="ascii"))
            self.assertIn("[unimplemented]", lst.read_text(encoding="ascii"))

    def test_unimplemented_encoding_refused_without_flag(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            src = td / "fadd.s"
            src.write_text("FADD $1,R4\n", encoding="ascii")
            r = run_cli("-o", str(td / "x.hex"), str(src))
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("no ATT92010 encoding", r.stderr)
            self.assertIn("unimp*", r.stderr)

    def test_width_suffix_forces_three_parcel_form(self):
        one, _, _ = assemble("ADD $3,R8\n")
        three, _, _ = assemble("ADD $3,R8:B\n")
        self.assertEqual(one, [0x5062])
        self.assertEqual(len(three), 3)
        self.assertEqual(three[0], 0xA3F4)  # opcode 0x23, smode F, dmode 4


# ---------------------------------------------------------------------------
# 4. Plan 9's optab.c genop values (tools/plan9-1e/.../zl/optab.c)
# ---------------------------------------------------------------------------

class TestPlan9OpcodeCrossCheck(unittest.TestCase):
    def _optab(self):
        text = OPTAB_PATH.read_text(encoding="latin-1")
        return {m.group(1): int(m.group(2), 16)
                for m in re.finditer(
                    r"\{\s*A([A-Z0-9]+),\s*T\w+,\s*(0x[0-9a-fA-F]+),",
                    text)}

    def test_bell_labs_main_prologue_parcels(self):
        """Our encoder against the shipped binary, parcel for parcel.

        `_main` in the 1st Edition's `echo` begins, in address order,
        with `ENTER R-16` (0x0BFC) — which `zl` inserts for
        `TEXT _main(SB), 1, $12` — then `MOV R0,_clock` as the three
        parcels 0x86DC 0x0000 0x4008.  The text is a sequence of
        little-endian 32-bit words whose *high* half is the earlier
        parcel (zl's SPUT writes big-endian and cflush reverses each
        four-byte group while swizflag is set), so parcels are read
        high half first; reading them in file order swaps every pair
        and was the old, wrong reading.
        """
        import struct
        binary = (ROOT / "tools" / "plan9-1e" / "hobbit" / "bin" / "echo").read_bytes()
        magic, text, data, bss, syms, entry, spsz, pcsz = struct.unpack(">8I", binary[:32])
        self.assertEqual(magic, 0x197)
        symtab = binary[32 + text + data:32 + text + data + syms]
        names = {}
        for i in range(0, len(symtab) // 28 * 28, 28):
            value, typ = struct.unpack(">IB", symtab[i:i + 5])
            name = symtab[i + 5:i + 25].split(b"\0")[0].decode("latin-1")
            names[name] = value
        self.assertEqual(names["_main"], entry)
        off = 32 + (entry - 0x1020)          # text base 0x1020 (1e loader)
        words = [binary[off + 4*k:off + 4*k + 4] for k in range(2)]
        parcels = []
        for w in words:
            parcels.append(w[3] << 8 | w[2])
            parcels.append(w[1] << 8 | w[0])
        self.assertEqual(parcels[:4], [0x0BFC, 0x86DC, 0x0000, 0x4008],
                         "the shipped binary's _main prologue")
        self.assertEqual(parcels[0], 0x0BFC, "ENTER R-16, inserted for TEXT")
        assembled, _, _ = assemble("MOV R0, *$0x4008")
        self.assertEqual(assembled, parcels[1:4],
                         "our encoder must reproduce Bell Labs' MOV parcels")

    def test_optab_contains_all_35_grid_mnemonics(self):
        optab = self._optab()
        missing = sorted(n for n in MANUAL_OPCODE if n not in optab)
        self.assertEqual(missing, [], f"missing from {OPTAB_PATH}")

    def test_assembled_opcode_fields_match_optab_genop(self):
        """zl/asm.c puts genop in the 3/5-parcel opcode[5:0] field:
           0x8000 | genop << 8  (andasm, three parcel)
           0xc000 | genop << 8  (andasm, five parcel)
        so the assembled field must equal optab.c's genop byte.
        """
        optab = self._optab()
        for name, manual in sorted(MANUAL_OPCODE.items()):
            with self.subTest(mnemonic=name):
                self.assertIn(name, optab)
                self.assertEqual(optab[name], manual,
                                 f"{name}: optab.c genop versus Table 1-18/1-20")
                for force in (3, 5):
                    if name == "MOVA":
                        text = f".{force} MOVA R0x1234,R4\n"
                    elif force == 3:
                        text = f".3 {name} $0x1000,R4\n"
                    else:
                        text = f".5 {name} $0x12345678,R4\n"
                    parcels, _, _ = assemble(text)
                    self.assertEqual((parcels[0] >> 8) & 0x3F, optab[name],
                                     f"{name}: {force}-parcel opcode field")


if __name__ == "__main__":
    unittest.main(verbosity=2)
