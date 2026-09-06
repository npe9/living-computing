#!/usr/bin/env python3
"""verify_fp_arith_f207b_listing.py -- the transcribed F207B block
(programs/fp_arith_f207b.strap: LOAD DOUBLE leaves accumulator bits
108-127 alone, two sub-tests) checked bit-for-bit against jb_af1c
p.90, plus its two constants against the pool p.176.
"""
import sys
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f207b.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022006.00", "1777777777777777777777", "FPK1"),
]

CODE_ROWS = [
    ("014510.00", "14510.44 00", "BD, $+.32"),
    ("014510.40", "22006.00 80 000040.36 70", "C1111(BU,64), FPK1, 64"),
    ("014511.40", "22006.00 80 000000.36 70", "C1111(BU,64), FPK1"),
    ("014512.40", "22005.44 60", "DL(U), FPK0"),
    ("014513.00", "22006.00 80 024000.15 70", "CT0110(BU,20), FPK1"),
    ("014514.00", "1310.00 80", "SIC, SEN"),
    ("014514.40", "1304.35 42", "BRGZ, SERS"),
    ("014515.00", "14515.50 00", "B, $+.32"),
    ("014515.40", "22005.00 80 000040.00 70", "C0000(BU,64), FPK0, 64"),
    ("014516.40", "22005.00 80 000000.00 70", "C0000(BU,64), FPK0"),
    ("014517.40", "22006.44 60", "DL(U), FPK1"),
    ("014520.00", "22005.00 80 024000.15 70", "CT0110(BU,20), FPK0"),
    ("014521.00", "1310.00 80", "SIC, SEN"),
    ("014521.40", "1304.35 42", "BRGZ, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
