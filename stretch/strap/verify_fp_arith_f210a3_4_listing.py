#!/usr/bin/env python3
"""verify_fp_arith_f210a3_4_listing.py -- F210A3-A4
(programs/fp_arith_f210a3_4.strap: STORE ROUNDED in the N range, the
sub-tests that pin where the rounding one is added) against jb_af1c
p.110, plus its five constants against the pools pp.176-177.

All 21 code rows below were read off the printed encoding column
individually. The block closes on 016032.00, where F210A5 begins, and
PASS sits there.

A3's CT0110 uses accumulator offset 68 where A1, A2 and A4 use 4 --
the only such difference in the routine so far, and transcribed as the
encoding column reads (074042.15 70 against 074002.15 70).
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f210a3_4.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022006.00", "1777777777777777777777", "FPK1"),
    ("022047.00", "0001000000000000000020", "FPK34"),
    ("022107.00", "0001000000000000000000", "FPK67"),
    ("022110.00", "0000000000000000000020", "FPK68"),
]

CODE_ROWS = [
    ("016014.00", "16014.50 00", "B, $+.32"),
    ("016014.40", "22005.44 60", "DL(U), FPK0"),
    ("016015.00", "22355.42 E0", "SRD(U), ROS"),
    ("016015.40", "22110.00 80 000000.20 50", "L(BU), FPK68"),
    ("016016.40", "22355.00 80 074042.15 70", "CT0110(BU,60), ROS, 68"),
    ("016017.40", "1310.00 80", "SIC, SEN"),
    ("016020.00", "1304.35 42", "BRGZ, SERS"),
    ("016020.40", "22355.74 80 016022.74 00", "BZB, ROS+.60, $+2.0"),
    ("016021.40", "1310.00 80", "SIC, SEN"),
    ("016022.00", "1304.10 00", "B, SERS"),
    ("016022.40", "16023.10 00", "B, $+.32"),
    ("016023.00", "22107.44 60", "DL(U), FPK67"),
    ("016023.40", "22006.14 80 060012.06 70", "C0011(BU,48), FPK1+.12, 20"),
    ("016024.40", "22355.42 E0", "SRD(U), ROS"),
    ("016025.00", "22047.00 80 000000.20 50", "L(BU), FPK34"),
    ("016026.00", "22355.00 80 074002.15 70", "CT0110(BU,60), ROS, 4"),
    ("016027.00", "1310.00 80", "SIC, SEN"),
    ("016027.40", "1304.35 42", "BRGZ, SERS"),
    ("016030.00", "22355.74 80 016032.34 00", "BZB, ROS+.60, $+2.0"),
    ("016031.00", "1310.00 80", "SIC, SEN"),
    ("016031.40", "1304.10 00", "B, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
