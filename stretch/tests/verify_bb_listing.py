#!/usr/bin/env python3
"""verify_bb_listing.py -- Branch on Bit assembled bit-for-bit against
the machine code printed in the 7030 floating-point diagnostic jb_af1c
(docs/jb_af1c_floating-point.pdf p.40, routine F202D, "DATA FLAG OFF"
block). IBM's own STRAP output is the strongest encoding oracle in this
project; this is the printed-listing cross-check of a real BB line that
verify_bb_encoding.py's header named as still outstanding.

It also exercises the half-word placement of a full-word instruction:
each BB1 sits at octal .40 (half-word 1), so the 64-bit instruction
straddles a word boundary (Reference Manual p.39) -- the case
strap_asm.Image.deposit_word_instr and listing_oracle.word_at were
added for. The three lines and their printed code, transcribed:

    BB1,$TF,$+1.   13.43 80 011671.74 0E   at 011670.40
    BB1,$UF,$+1.   13.44 80 011672.74 0E   at 011671.40
    BB1,$VF,$+1.   13.45 80 011673.74 0E   at 011672.40

$TF/$UF/$VF are indicator-register bits 35/36/37 (octal 43/44/45 of
word 11 = octal word 13), which the assembler resolves to bit
addresses; $+1. is the branch target, one word past the instruction.
The op byte 0E = 00001110 = literal-tail 0000 + modifier 11 (set to
one) + condition 1 + index 0, i.e. BB1 exactly.
"""
import sys
from strap_asm import assemble
from listing_oracle import check_rows, finish

SRC = """
        SLC, (8)11670.40
        BB1, $TF, $+1.
        BB1, $UF, $+1.
        BB1, $VF, $+1.
        END, $
"""

ROWS = [
    ("011670.40", "13.43 80 011671.74 0E", "BB1,$TF,$+1."),
    ("011671.40", "13.44 80 011672.74 0E", "BB1,$UF,$+1."),
    ("011672.40", "13.45 80 011673.74 0E", "BB1,$VF,$+1."),
]

if __name__ == "__main__":
    finish(check_rows(assemble(SRC), ROWS))
