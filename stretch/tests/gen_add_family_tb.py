#!/usr/bin/env python3
"""gen_add_family_tb.py -- the 128-cell ADD-family truth table of
R23-9694 (7030 CE Introductory Programming, Vol. 2) printed p.107,
run on the model.

THE PAGE, in its own words:

    "The four operations ADD, ADD TO MAGNITUDE, ADD TO MEMORY, and
    ADD MAGNITUDE TO MEMORY allow a flexible handling of the signs of
    the factors and the result.  Not all possible combinations are
    provided, however, and in some cases the results may not be
    obvious.  The following table shows the storage or accumulator
    field that is produced by all possible combinations of operations,
    sign modifiers, operand signs, and relative magnitudes of
    operands.

    The storage field is assumed to be signed in all cases.  When the
    unsigned modifier is specified, the field length is adjusted
    accordingly and the absolute value of the storage field is used in
    the operation.  However, IN AN UNSIGNED TO-MEMORY OPERATION, THE
    ORIGINAL SIGN OF THE FIELD REMAINS IN STORAGE and is therefore
    shown in the table as part of the result field."

Sixteen rows -- four operations, each plain / N / U / U&N -- by eight
columns of (memory operand, accumulator operand) sign-and-magnitude
pairs.  Every cell is a signed magnitude.  128 independent checks
against IBM's own numbers.

WHY THIS TABLE AND NOT ANOTHER.  Every operation in it was built in
this repository on 2026-10-19 -- M+MG, +MG, and the unsigned-subtract
correction underneath them all -- and the bug that correction fixed
(`fieldToSM` dropping the negative sign modifier on an unsigned field,
so every unsigned subtract was an addition) lives in exactly the `U`
and `U,N` rows below.  Reference Manual Figure 12 found it with ONE
cell.  This page has 128.

**THE `N` SUFFIX IS WHAT MAKES THE TABLE REACHABLE.**  Four of the
sixteen rows are to-memory operations with the negative sign modifier,
and until the suffix was built (C22-6531 Appendix A footnote 4,
witnessed by Reference Manual Figure 14) there was no way to spell
`M+N` or `M+MGN` at all -- the written-minus forms `M-` and `M-MG`
are deliberately absent from VFL_INT_WRITTEN_MINUS for want of a
source.  The table could not have been run a commit earlier.

WHAT IS NOT CHECKED, and the page marks them so it is worth saying:
the eight cells carrying `*` turn on the LOST CARRY indicator, and the
underlined cells "differ from those produced from a similar floating
point operation".  This generator checks VALUES only.  The lost-carry
cells are listed in LOST_CARRY below so that the next person can turn
them into indicator checks without re-reading the page.

HOW A CELL IS ENCODED.  Each operand is a 16-bit signed field at byte
size 8 -- an 8-bit magnitude over an 8-bit sign byte -- placed in the
low 16 bits of its own word and addressed as `W+.48`.  The sign byte
is the RIGHTMOST byte (fieldToSM takes `raw >> byteSize` as the
magnitude and bit `byteSize-1` as the sign), so the magnitude is at
word bits 48-55 and the sign at 56-63.

That layout is what makes the `U` rows expressible: "the field length
is adjusted accordingly" means the unsigned field is the NUMERIC BYTE
ALONE, `(BU,8,8)` at the same address `W+.48`, with the sign byte
sitting outside it -- which is exactly why an unsigned to-memory
operation leaves the original sign in storage.  Nothing special is
needed in the model for that clause; it falls out of the addressing.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "strap"))

from gen_tb import generate
from strap_asm import assemble, AssemblerError

DECK = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    os.pardir, "decks", "add_family_signs.strap")

# The eight columns, as the page heads them:
#   Memory Operand        3+  5+  3+  5+  3-  5-  3-  5-
#   Accumulator Operand   5+  3+  5-  3-  5+  3+  5-  3-
COLUMNS = [(3, 5), (5, 3), (3, -5), (5, -3), (-3, 5), (-5, 3), (-3, -5), (-5, -3)]

# The sixteen rows, transcribed cell for cell.  `mnemonic` is how this
# assembler spells the row; `mode` is the data description.  "to_mem"
# marks the rows whose result replaces the storage operand.
#
# A plain `-`/`-MG` would serve for the two to-accumulator N rows, but
# the N suffix is used throughout so that all sixteen rows are spelled
# one way and the two to-memory N rows are not a special case.
ROWS = [
    ("Add",                        "+",      False, ["8+","8+","2-","2+","2+","2-","8-","8-"]),
    ("Add, N",                     "+N",     False, ["2+","2-","8-","8-","8+","8+","2-","2+"]),
    ("Add, U",                     "+",      False, ["8+","8+","2-","2+","8+","8+","2-","2+"]),
    ("Add, U,N",                   "+N",     False, ["2+","2-","8-","8-","2+","2-","8-","8-"]),
    ("Add to Magnitude",           "+MG",    False, ["8+","8+","8-","8-","2+","0+","2-","0-"]),
    ("Add to Magnitude, N",        "+MGN",   False, ["2+","0+","2-","0-","8+","8+","8-","8-"]),
    ("Add to Magnitude, U",        "+MG",    False, ["8+","8+","8-","8-","8+","8+","8-","8-"]),
    ("Add to Magnitude, U,N",      "+MGN",   False, ["2+","0+","2-","0-","2+","0+","2-","0-"]),
    ("Add to Memory",              "M+",     True,  ["8+","8+","2-","2+","2+","2-","8-","8-"]),
    ("Add to Memory, N",           "M+N",    True,  ["2-","2+","8+","8+","8-","8-","2+","2-"]),
    ("Add to Memory, U",           "M+",     True,  ["8+","8+","2+","2+","8-","8-","2-","2-"]),
    ("Add to Memory, U,N",         "M+N",    True,  ["2+","2+","8+","8+","2-","2-","8-","8-"]),
    ("Add Magnitude to Memory",    "M+MG",   True,  ["8+","8+","8+","8+","0-","2-","0-","2-"]),
    ("Add Magnitude to Memory, N", "M+MGN",  True,  ["0+","2+","0+","2+","8-","8-","8-","8-"]),
    ("Add Magnitude to Memory, U", "M+MG",   True,  ["8+","8+","8+","8+","8-","8-","8-","8-"]),
    ("Add Magnitude to Memory, U,N","M+MGN", True,  ["0+","2+","0+","2+","0-","2-","0-","2-"]),
]

# Rows 2, 3, 6, 7, 10, 11, 14, 15 (0-based) are the unsigned ones --
# every row whose name carries a "U".
def is_unsigned(name):
    return ", U" in name

# The `*` cells: "The lost carry indicator is turned on."  Row index
# and column index, 0-based.  Not checked by this generator.
LOST_CARRY = [(10, 2), (10, 6), (11, 0), (11, 4)]


def enc(mag, neg):
    """A 16-bit signed field: magnitude over an 8-bit sign byte."""
    return (mag << 8) | (0x80 if neg else 0)


def cell_expected(text):
    """"8+" -> the encoded 16-bit field."""
    return enc(int(text[:-1]), text[-1] == "-")


def build_deck():
    lines = []
    w = lines.append
    w("! add_family_signs.strap -- GENERATED by tests/gen_add_family_tb.py.")
    w("! Do not edit by hand; edit the generator, which carries the page")
    w("! citation and the transcribed table.")
    w("!")
    w("! R23-9694 (7030 CE Introductory Programming, Vol. 2) printed")
    w("! p.107: the 128-cell table of ADD, ADD TO MAGNITUDE, ADD TO")
    w("! MEMORY and ADD MAGNITUDE TO MEMORY over every combination of")
    w("! sign modifiers, operand signs and relative magnitudes.")
    w("!")
    w("! Each cell loads its accumulator operand, runs its operation")
    w("! against its own private copy of the memory operand, and -- for")
    w("! the to-accumulator rows -- stores the accumulator.  The")
    w("! to-memory rows are checked in place.")
    w("")
    w("        SLC, (8)2000.0")
    w("")
    for ri, (name, mn, to_mem, cells) in enumerate(ROWS):
        uns = is_unsigned(name)
        dds = "BU,8,8" if uns else "B,16,8"
        w("! -- row %-2d %s" % (ri, name))
        for ci, (m, a) in enumerate(COLUMNS):
            tag = "C%02X%X" % (ri, ci)
            w("        L(B,16,8), A%s+.48, 0" % tag)
            w("        %s(%s), M%s+.48, 0" % (mn, dds, tag))
            if not to_mem:
                w("        ST(B,16,8), R%s+.48, 0" % tag)
        w("")
    w("PASS    BEW, $")
    w("")
    w("! Operands, word-aligned.  Each cell gets its own memory word,")
    w("! because the to-memory rows destroy theirs.")
    w("        SLC, (8)4000.0")
    w("")
    for ri, (name, mn, to_mem, cells) in enumerate(ROWS):
        for ci, (m, a) in enumerate(COLUMNS):
            tag = "C%02X%X" % (ri, ci)
            w("M%-7s DD(BU,64,8), %d" % (tag, enc(abs(m), m < 0)))
            w("A%-7s DD(BU,64,8), %d" % (tag, enc(abs(a), a < 0)))
            if not to_mem:
                w("R%-7s DD(BU,64,8), 0" % tag)
    w("")
    w("        END, START")
    # The first instruction needs the START label.
    out = "\n".join(lines) + "\n"
    return out.replace("        L(B,16,8), AC000+.48, 0",
                       "START   L(B,16,8), AC000+.48, 0", 1)


def main():
    if len(sys.argv) != 2:
        print("usage: %s ModuleName" % sys.argv[0], file=sys.stderr)
        sys.exit(1)
    module_name = sys.argv[1]

    src = build_deck()
    with open(DECK, "w") as f:
        f.write(src)

    try:
        prog = assemble(src)
    except AssemblerError as e:
        print("error: %s" % e, file=sys.stderr)
        sys.exit(1)

    checks = []
    for ri, (name, mn, to_mem, cells) in enumerate(ROWS):
        for ci, text in enumerate(cells):
            tag = "C%02X%X" % (ri, ci)
            sym = ("M" if to_mem else "R") + tag
            word = prog.symtab[sym] // 64
            label = "r%02d_c%d" % (ri, ci)
            checks.append((label, str(word), cell_expected(text)))

    print(generate(module_name, prog, checks,
                   pc_check=prog.symtab["PASS"] // 32,
                   cycle_bound=200000,
                   step_cap=400000))


if __name__ == "__main__":
    main()
