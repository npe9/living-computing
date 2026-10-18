#!/usr/bin/env python3
"""verify_fp_arith_f211a3_4_listing.py -- F211A3-A4
(../decks/fp_arith_f211a3_4.strap: the first UNFLAGGED SLO, and so the
first exercise of its exponent-minus-48 rule) against jb_af1c p.113,
plus its four constants against the pools pp.176-177.

All 20 code rows below were read off the printed encoding column
individually. The block closes on 016201.00, where F211A5 begins, and
PASS sits there.

A3 stores FPK28's fraction at 256 - 48 = 208 (FPK44) and A4 stores
FPK38's at 50 - 48 = 2 (FPK39); the listing's own comments say
"EXP+208" and "EXPONENT++2".
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f211a3_4.strap").read())

CONST_ROWS = [
    ("022041.00", "0200177777777777777760", "FPK28"),
    ("022053.00", "0031052525252525252520", "FPK38"),
    ("022054.00", "0001052525252525252520", "FPK39"),
    ("022061.00", "0150177777777777777760", "FPK44"),
]

CODE_ROWS = [
    ("016163.00", "22041.44 60", "DL(U), FPK28"),
    ("016163.40", "22041.14 80 060012.06 70", "C0011(BU,48), FPK28+.12, 20"),
    ("016164.40", "22355.44 E0", "SLO(U), ROS"),
    ("016165.00", "22061.00 80 000000.20 50", "L(BU), FPK44"),
    ("016166.00", "22355.00 80 074002.15 70", "CT0110(BU,60), ROS, 4"),
    ("016167.00", "1310.00 80", "SIC, SEN"),
    ("016167.40", "1304.35 42", "BRGZ, SERS"),
    ("016170.00", "22355.74 80 016172.34 00", "BZB, ROS+.60, $+2.0"),
    ("016171.00", "1310.00 80", "SIC, SEN"),
    ("016171.40", "1304.10 00", "B, SERS"),
    ("016172.00", "22053.44 60", "DL(U), FPK38"),
    ("016172.40", "22053.14 80 060012.06 70", "C0011(BU,48), FPK38+.12, 20"),
    ("016173.40", "22355.44 E0", "SLO(U), ROS"),
    ("016174.00", "22054.00 80 000000.20 50", "L(BU), FPK39"),
    ("016175.00", "22355.00 80 074002.15 70", "CT0110(BU,60), ROS, 4"),
    ("016176.00", "1310.00 80", "SIC, SEN"),
    ("016176.40", "1304.35 42", "BRGZ, SERS"),
    ("016177.00", "22355.74 80 016201.34 00", "BZB, ROS+.60, $+2.0"),
    ("016200.00", "1310.00 80", "SIC, SEN"),
    ("016200.40", "1304.10 00", "B, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
