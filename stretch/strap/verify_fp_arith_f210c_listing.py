#!/usr/bin/env python3
"""verify_fp_arith_f210c_listing.py -- F210C1-C2
(programs/fp_arith_f210c.strap: SRD must place the accumulator's flag
bits in storage bits 61-63) against jb_af1c pp.111-112, plus its one
constant against the pool p.176.

All 22 code rows below were read off the printed encoding column
individually. The block closes on 016130.40, where F210D "TESTS OF
INDICATORS" begins, and PASS sits there.

C1 pre-loads ROS with ones before zeroing the accumulator, which makes
it a test of COPYING the flags rather than of leaving them alone: a
model that never wrote bits 61-63 would pass C2 and fail C1.

FSR3 is the listing's own label at its real address, 016111.40.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f210c.strap").read())

CONST_ROWS = [
    ("022006.00", "1777777777777777777777", "FPK1"),
]

CODE_ROWS = [
    ("016111.40", "22355.00 80 000000.36 F0", "CM1111(BU), ROS"),
    ("016112.40", "10.22 00", "Z, $L"),
    ("016113.00", "11.22 00", "Z, $R"),
    ("016113.40", "12.22 00", "Z, $SB"),
    ("016114.00", "22355.42 E0", "SRD(U), ROS"),
    ("016114.40", "22355.75 80 003000.07 70", "CT0011(BU,3), ROS+.61"),
    ("016115.40", "1310.00 80", "SIC, SEN"),
    ("016116.00", "1304.35 42", "BRGZ, SERS"),
    ("016116.40", "12.05 80 003000.07 70", "CT0011(BU,3), 10.5"),
    ("016117.40", "1310.00 80", "SIC, SEN"),
    ("016120.00", "1304.35 42", "BRGZ, SERS"),
    ("016120.40", "16121.10 00", "B, $+.32"),
    ("016121.00", "22006.00 80 000040.36 70", "C1111(BU,64), FPK1, 64"),
    ("016122.00", "22006.00 80 000000.36 70", "C1111(BU,64), FPK1"),
    ("016123.00", "12.00 80 010000.36 F0", "CM1111(BU,8), 10.0"),
    ("016124.00", "22355.42 E0", "SRD(U), ROS"),
    ("016124.40", "22355.75 80 003000.31 70", "CT1100(BU,3), ROS+.61"),
    ("016125.40", "1310.00 80", "SIC, SEN"),
    ("016126.00", "1304.35 42", "BRGZ, SERS"),
    ("016126.40", "12.05 80 003000.31 70", "CT1100(BU,3), 10.5"),
    ("016127.40", "1310.00 80", "SIC, SEN"),
    ("016130.00", "1304.35 42", "BRGZ, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
