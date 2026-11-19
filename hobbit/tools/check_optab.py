#!/usr/bin/env python3
"""Cross-check Plan 9's Hobbit toolchain against the printed tables of the
ATT92010 Programmer's Reference Manual (January 1993).

Two independent checks, both against the vendored 1st Edition sources in
tools/plan9-1e:

1. Opcode field.  tools/plan9-1e/sys/src/cmd/zl/optab.c gives each
   instruction's `genop` byte.  In zl/asm.c the three- and five-parcel
   encoders use

       three parcel:  s = 0x8000 | (genop << 8)     (asm.c, andasm)
       five parcel:   s = 0xc000 | (genop << 8)     (asm.c, andasm)

   so genop is the manual's opcode[5:0] field, directly comparable with
   Tables 1-18 (printed p. 1-23) and 1-20 (printed p. 1-25), which are
   the same opcode[5:3] x opcode[2:0] grid.

2. Mnemonic inventory.  Table 3-1 (printed pp. 3-1 to 3-2) lists the
   manual's 46 mnemonic entries; zc/z.out.h is Plan 9's enum of
   assembler mnemonics.  Every manual entry should have a Plan 9
   spelling, except the four conditional jumps, which Plan 9 splits
   into JMPTY/JMPTN/JMPFY/JMPFN exactly as the manual names them.

Observed result (2026-11-19):
  check 1: 35 mnemonics checked, 0 mismatches.
  check 2: 45 of the 46 manual entries have a Plan 9 mnemonic; the one
           missing is CLRE ("clear PSW enter guard bit", manual p. 1-22,
           a niladic).  Plan 9's za therefore cannot assemble CLRE.
  50 optab entries are outside the Tables 1-18/1-20 grid: the Table 1-19
  monadics and Table 1-17 niladics (different subcode fields, not
  checked here) and 26 floating-point mnemonics the 92010 manual marks
  "unimp" and traps.

Run from anywhere:  python3 hobbit/tools/check_optab.py
Exit status is nonzero if check 1 finds a mismatch, or if check 2's
missing-mnemonic set is anything other than the pinned {"CLRE"}: the
gate is that the vendored sources and the transcriptions stay in the
state recorded above.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OPTAB = HERE / "plan9-1e/sys/src/cmd/zl/optab.c"
OUTH = HERE / "plan9-1e/sys/src/cmd/zc/z.out.h"

# Tables 1-18 / 1-20 of the PRM, rows opcode[5:3] = 0..7, columns
# opcode[2:0] = 0..7.  None = "unimp" (the trap).
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
MANUAL = {}
for row, cells in enumerate(GRID):
    for col, name in enumerate(cells):
        if name and name != "MONADIC":
            MANUAL[name] = (row << 3) | col

# Table 3-1 mnemonics, expanded: [3] gives NAME and NAME3, and the four
# conditional jumps are spelled out.
TABLE31 = """ADD ADD3 ADDI AND AND3 ANDI CALL CATCH CLRE CMPEQ CMPGT CMPHI
CPU CRET DIV DIV3 DQM ENTER FLUSHD FLUSHDCE FLUSHI FLUSHP FLUSHPBE
FLUSHPTE JMP JMPTY JMPTN JMPFY JMPFN KCALL KRET LDRAA MOV MOVA MUL MUL3
NOP OR OR3 ORI POPN RETURN REM REM3 SHL SHL3 SHR SHR3 SUB SUB3 TADD TESTC
TESTV TSUB UDIV UREM USHR USHR3 XOR XOR3""".split()

# Plan 9 pseudo-ops (segments, data, symbol tables), not instructions.
PSEUDO = {"XXX", "DATA", "GLOBL", "HISTORY", "GOK", "LONG", "NAME",
          "TEXT", "WORD", "END"}

# Plan 9's assembler has no CLRE ("clear PSW enter guard bit", PRM
# p. 1-22).  Pinned rather than tolerated: any other absence is a change.
EXPECTED_MISSING = {"CLRE"}


def optab_entries():
    text = OPTAB.read_text(errors="replace")
    entries = {}
    for m in re.finditer(r"\{\s*A([A-Z0-9]+),\s*T\w+,\s*(0x[0-9a-fA-F]+),",
                         text):
        entries[m.group(1)] = int(m.group(2), 16)
    return entries


def outh_mnemonics():
    text = OUTH.read_text(errors="replace")
    body = text[text.index("enum\tas"):]
    body = body[:body.index("AEND")]
    return {m.group(1) for m in re.finditer(r"^\tA([A-Z0-9]+),", body, re.M)}


def main():
    entries = optab_entries()
    checked = mismatched = 0
    for name, opcode in sorted(MANUAL.items()):
        checked += 1
        if name not in entries:
            mismatched += 1
            print(f"MISSING FROM OPTAB: {name} (manual 0x{opcode:02x})")
        elif entries[name] != opcode:
            mismatched += 1
            print(f"MISMATCH {name}: manual 0x{opcode:02x}, "
                  f"optab 0x{entries[name]:02x}")
    print(f"check 1: {checked} mnemonics checked, {mismatched} mismatches")

    names = outh_mnemonics()
    missing = sorted(n for n in TABLE31 if n not in names)
    for n in missing:
        print(f"MISSING FROM z.out.h: {n}")
    print(f"check 2: Table 3-1 {len(TABLE31)} entries, "
          f"{len(missing)} without a Plan 9 mnemonic")

    extras = sorted(n for n in entries if n not in MANUAL and n not in PSEUDO)
    print(f"optab entries outside Tables 1-18/1-20: {len(extras)}")
    unexpected = set(missing) != EXPECTED_MISSING
    if unexpected:
        print(f"unexpected missing set: {missing} (expected "
              f"{sorted(EXPECTED_MISSING)})")
    return 1 if mismatched or unexpected else 0


if __name__ == "__main__":
    sys.exit(main())
