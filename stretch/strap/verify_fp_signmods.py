#!/usr/bin/env python3
"""verify_fp_signmods.py -- the FP sign-modifier loads (LN/LA/LNA)
assembled bit-for-bit against the machine code printed in the 7030
floating-point diagnostic jb_af1c (docs/jb_af1c_floating-point.pdf,
routine F200B). FPK2 is placed at its listed word 22007 (octal) via
SLC so the address field matches too. A = absolute sign, N = negative
(invert) sign, NA = both; the op field distinguishes them (bits 18-20
after the address). This is the reverse test the FP diagnostic drove:
the assembler could not encode these until now.
"""
import sys
from strap_asm import assemble
from listing_oracle import check_rows, finish

# The four load forms of FPK2, unnormalized (%U= = (U)); FPK2 placed at
# octal 22007 so the whole half-word matches the printout.
SRC = """
        SLC, (8)10052.0
        L(U), FPK2
        LA(U), FPK2
        LN(U), FPK2
        LNA(U), FPK2
        SLC, (8)22007.0
FPK2    DD(BU,64), 0
        END, $
"""
# (octal loc, printed half-word) from jb_af1c F200B1-B4.
ROWS = [
    ("010052.00", "22007.40 60", "L(U),FPK2   (no sign mod)"),
    ("010052.40", "22007.60 60", "LA(U),FPK2  (absolute sign)"),
    ("010053.00", "22007.50 60", "LN(U),FPK2  (negative sign)"),
    ("010053.40", "22007.70 60", "LNA(U),FPK2 (negative absolute)"),
]

if __name__ == "__main__":
    finish(check_rows(assemble(SRC), ROWS))
