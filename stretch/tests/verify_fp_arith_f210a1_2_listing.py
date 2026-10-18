#!/usr/bin/env python3
"""verify_fp_arith_f210a1_2_listing.py -- F210A1-A2
(../decks/fp_arith_f210a1_2.strap: STORE ROUNDED in the XFP and XFN
ranges) against jb_af1c p.110, plus its five constants against the
pools pp.176-177.

All 22 code rows below were read off the printed encoding column
individually. The block closes on 016014.00, where F210A3 begins, and
PASS sits there.

The printed comments write the flagged exponents as +2047 and -1791
where the constants decode to XFP +1023 and XFN -767 -- the listing
counts EF as contributing 1024. The constants are checked as printed.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f210a1_2.strap").read())

CONST_ROWS = [
    ("022037.00", "1777577777777777777760", "FPK26"),
    ("022100.00", "1577600000000000000000", "FPK59"),
    ("022173.00", "1577777777777777777760", "FK25"),
    ("022205.00", "1777400000000000000000", "FK35"),
    ("022212.00", "1777577777777777777770", "FK40"),
]

CODE_ROWS = [
    ("015775.00", "15775.50 00", "B, $+.32"),
    ("015775.40", "22037.44 60", "DL(U), FPK26"),
    ("015776.00", "22212.14 80 060012.06 70", "C0011(BU,48), FK40+.12, 20"),
    ("015777.00", "22355.42 E0", "SRD(U), ROS"),
    ("015777.40", "22205.00 80 000000.20 50", "L(BU), FK35"),
    ("016000.40", "22355.00 80 074002.15 70", "CT0110(BU,60), ROS, 4"),
    ("016001.40", "1310.00 80", "SIC, SEN"),
    ("016002.00", "1304.35 42", "BRGZ, SERS"),
    ("016002.40", "22355.74 80 016004.74 00", "BZB, ROS+.60, $+2.0"),
    ("016003.40", "1310.00 80", "SIC, SEN"),
    ("016004.00", "1304.10 00", "B, SERS"),
    ("016004.40", "16005.10 00", "B, $+.32"),
    ("016005.00", "22173.44 60", "DL(U), FK25"),
    ("016005.40", "22173.14 80 060012.06 70", "C0011(BU,48), FK25+.12, 20"),
    ("016006.40", "22355.42 E0", "SRD(U), ROS"),
    ("016007.00", "22100.00 80 000000.20 50", "L(BU), FPK59"),
    ("016010.00", "22355.00 80 074002.15 70", "CT0110(BU,60), ROS, 4"),
    ("016011.00", "1310.00 80", "SIC, SEN"),
    ("016011.40", "1304.35 42", "BRGZ, SERS"),
    ("016012.00", "22355.74 80 016014.34 00", "BZB, ROS+.60, $+2.0"),
    ("016013.00", "1310.00 80", "SIC, SEN"),
    ("016013.40", "1304.10 00", "B, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
