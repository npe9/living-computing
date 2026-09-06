#!/usr/bin/env python3
"""verify_fp_arith_f208c_listing.py -- the whole of F208C
(programs/fp_arith_f208c.strap: ADD DOUBLE's two "TEST UNCHANGED
REGISTERS" sub-tests) checked bit-for-bit against jb_af1c p.98, plus
its three constants against the pool p.176.

Every one of the 21 code rows below was read off the printed encoding
column individually. The block's arithmetic closes on 015143.00,
where the listing's own exit sequence (BD,$+1.0 / B,FAD4) begins, and
that is where PASS sits here.
"""
import sys
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f208c.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022006.00", "1777777777777777777777", "FPK1"),
    ("022067.00", "0031377777777777777760", "FPK50"),
]

CODE_ROWS = [
    ("015125.00", "10.22 00", "Z, $L"),
    ("015125.40", "11.22 00", "Z, $R"),
    ("015126.00", "12.22 00", "Z, $SB"),
    ("015126.40", "22067.44 20", "D+(U), FPK50"),
    ("015127.00", "22005.00 80 024000.13 70", "CT0101(BU,20), FPK0"),
    ("015130.00", "1310.00 80", "SIC, SEN"),
    ("015130.40", "1304.35 42", "BRGZ, SERS"),
    ("015131.00", "12.05 80 003000.07 70", "CT0011(BU,3), 10.5"),
    ("015132.00", "1310.00 80", "SIC, SEN"),
    ("015132.40", "1304.35 42", "BRGZ, SERS"),
    ("015133.00", "15133.50 00", "B, $+.32"),
    ("015133.40", "22006.00 80 000040.36 70", "C1111(BU,64), FPK1, 64"),
    ("015134.40", "22006.00 80 000000.36 70", "C1111(BU,64), FPK1"),
    ("015135.40", "12.00 80 010000.36 F0", "CM1111(BU,8), 10.0"),
    ("015136.40", "22005.44 20", "D+(U), FPK0"),
    ("015137.00", "22006.00 80 024000.25 70", "CT1010(BU,20), FPK1"),
    ("015140.00", "1310.00 80", "SIC, SEN"),
    ("015140.40", "1304.35 42", "BRGZ, SERS"),
    ("015141.00", "12.05 80 003000.31 70", "CT1100(BU,3), 10.5"),
    ("015142.00", "1310.00 80", "SIC, SEN"),
    ("015142.40", "1304.35 42", "BRGZ, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
