#!/usr/bin/env python3
"""verify_fp_arith_f210a5_listing.py -- F210A5
(programs/fp_arith_f210a5.strap: STORE ROUNDED's unnormalized overflow
must NOT move the exponent) against jb_af1c p.110, plus its two
constants against the pools pp.176-177.

All 11 code rows below were read off the printed encoding column
individually. The block closes on 016041.40, where the routine's "TEST
NORMALIZATION MODIFIER" section and F210A6 begin, and PASS sits there.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f210a5.strap").read())

CONST_ROWS = [
    ("022045.00", "0001177777777777777760", "FPK32"),
    ("022107.00", "0001000000000000000000", "FPK67"),
]

CODE_ROWS = [
    ("016032.00", "16032.50 00", "B, $+.32"),
    ("016032.40", "22045.44 60", "DL(U), FPK32"),
    ("016033.00", "22045.14 80 060012.06 70", "C0011(BU,48), FPK32+.12, 20"),
    ("016034.00", "22355.42 E0", "SRD(U), ROS"),
    ("016034.40", "22107.00 80 000000.20 50", "L(BU), FPK67"),
    ("016035.40", "22355.00 80 074002.15 70", "CT0110(BU,60), ROS, 4"),
    ("016036.40", "1310.00 80", "SIC, SEN"),
    ("016037.00", "1304.35 42", "BRGZ, SERS"),
    ("016037.40", "22355.74 80 016041.74 00", "BZB, ROS+.60, $+2.0"),
    ("016040.40", "1310.00 80", "SIC, SEN"),
    ("016041.00", "1304.10 00", "B, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
