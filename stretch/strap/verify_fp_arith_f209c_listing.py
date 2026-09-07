#!/usr/bin/env python3
"""verify_fp_arith_f209c_listing.py -- the whole of F209C
(programs/fp_arith_f209c.strap: ADD DOUBLE TO MAGNITUDE's two
"UNCHANGED REGISTERS" sub-tests) against jb_af1c pp.105-106, plus its
three constants against the pool p.176.

All 21 code rows below were read off the printed encoding column
individually. The block closes on 015614.40, where F209D begins, and
PASS sits there.
"""
import sys
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f209c.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022006.00", "1777777777777777777777", "FPK1"),
    ("022067.00", "0031377777777777777760", "FPK50"),
]

CODE_ROWS = [
    ("015576.40", "10.22 00", "Z, $L"),
    ("015577.00", "11.22 00", "Z, $R"),
    ("015577.40", "12.22 00", "Z, $SB"),
    ("015600.00", "22067.46 20", "D+MG(U), FPK50"),
    ("015600.40", "22005.00 80 024000.13 70", "CT0101(BU,20), FPK0"),
    ("015601.40", "1310.00 80", "SIC, SEN"),
    ("015602.00", "1304.35 42", "BRGZ, SERS"),
    ("015602.40", "12.00 80 010000.15 70", "CT0110(BU,8), 10.0"),
    ("015603.40", "1310.00 80", "SIC, SEN"),
    ("015604.00", "1304.35 42", "BRGZ, SERS"),
    ("015604.40", "15605.10 00", "B, $+.32"),
    ("015605.00", "22006.00 80 000040.36 70", "C1111(BU,64), FPK1, 64"),
    ("015606.00", "22006.00 80 000000.36 70", "C1111(BU,64), FPK1"),
    ("015607.00", "12.00 80 010000.36 F0", "CM1111(BU,8), 10.0"),
    ("015610.00", "22005.46 20", "D+MG(U), FPK0"),
    ("015610.40", "22006.00 80 024000.25 70", "CT1010(BU,20), FPK1"),
    ("015611.40", "1310.00 80", "SIC, SEN"),
    ("015612.00", "1304.35 42", "BRGZ, SERS"),
    ("015612.40", "12.00 80 010000.31 70", "CT1100(BU,8), 10.0"),
    ("015613.40", "1310.00 80", "SIC, SEN"),
    ("015614.00", "1304.35 42", "BRGZ, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
