#!/usr/bin/env python3
"""verify_fp_arith_f207cd_listing.py -- the transcribed F207C + F207D
blocks (../decks/fp_arith_f207cd.strap: LOAD DOUBLE zeroes the sign
byte's flag bits, and the data flag indicators follow the addressed
operand) checked bit-for-bit against jb_af1c p.90, plus its two
constants against the pool p.176.
"""
import sys
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f207cd.strap").read())

CONST_ROWS = [
    ("022006.00", "1777777777777777777777", "FPK1"),
    ("022007.00", "1777777777777777777760", "FPK2"),
]

CODE_ROWS = [
    ("014524.00", "14524.44 00", "BD, $+.32"),
    ("014524.40", "12.00 80 010000.36 F0", "CM1111(BU,8), 10."),
    ("014525.40", "22006.44 60", "DL(U), FPK1"),
    ("014526.00", "12.05 80 003000.07 70", "CT0011(BU,3), 10.5"),
    ("014527.00", "1310.00 80", "SIC, SEN"),
    ("014527.40", "1304.35 42", "BRGZ, SERS"),
    ("014530.00", "13.43 80 014531.34 0E", "BB1, $TF, $+1."),
    ("014531.00", "13.44 80 014532.34 0E", "BB1, $UF, $+1."),
    ("014532.00", "13.45 80 014533.34 0E", "BB1, $VF, $+1."),
    ("014533.00", "22007.44 60", "DL(U), FPK2"),
    ("014533.40", "1310.00 80", "SIC, SEN"),
    ("014534.00", "1304.21 C2", "BTF, SERS"),
    ("014534.40", "1310.00 80", "SIC, SEN"),
    ("014535.00", "1304.22 42", "BUF, SERS"),
    ("014535.40", "1310.00 80", "SIC, SEN"),
    ("014536.00", "1304.22 C2", "BVF, SERS"),
    ("014536.40", "13.22 00", "Z, $IND"),
    ("014537.00", "22006.44 60", "DL(U), FPK1"),
    ("014537.40", "1310.00 80", "SIC, SEN"),
    ("014540.00", "1304.21 C0", "BZTF, SERS"),
    ("014540.40", "1310.00 80", "SIC, SEN"),
    ("014541.00", "1304.22 40", "BZUF, SERS"),
    ("014541.40", "1310.00 80", "SIC, SEN"),
    ("014542.00", "1304.22 C0", "BZVF, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
