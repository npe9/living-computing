#!/usr/bin/env python3
"""verify_fp_arith_f210a6_7_listing.py -- F210A6-A7
(../decks/fp_arith_f210a6_7.strap: SRD(N) in the XFP and XFN ranges,
where normalization is suppressed) against jb_af1c p.111, plus its
five constants against the pools pp.178-179.

All 16 code rows below were read off the printed encoding column
individually. The block closes on 016054.40, where F210A8 "TEST
NORMALIZATION PROCESS" begins, and PASS sits there.

These are the first SRD(N) in the diagnostic; every sub-test through
A5 is SRD(U). Their expected results FK109 and FK110 are still
unnormalized, which is what makes them the oracle for the suppression.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f210a6_7.strap").read())

CONST_ROWS = [
    ("022167.00", "1777403777777777777760", "FK21"),
    ("022170.00", "0400177777777777777760", "FK22"),
    ("022200.00", "1577617777777777777760", "FK30"),
    ("022316.00", "1777404000000000000000", "FK109"),
    ("022317.00", "1577620000000000000000", "FK110"),
]

CODE_ROWS = [
    ("016041.40", "16042.10 00", "B, $+.32"),
    ("016042.00", "22167.44 60", "DL(U), FK21"),
    ("016042.40", "22170.14 80 060012.06 70", "C0011(BU,48), FK22+.12, 20"),
    ("016043.40", "22355.02 E0", "SRD(N), ROS"),
    ("016044.00", "22316.00 80 000000.20 50", "L(BU), FK109"),
    ("016045.00", "22355.00 80 074002.15 70", "CT0110(BU,60), ROS, 4"),
    ("016046.00", "1310.00 80", "SIC, SEN"),
    ("016046.40", "1304.35 42", "BRGZ, SERS"),
    ("016047.00", "16047.50 00", "B, $+.32"),
    ("016047.40", "22200.44 60", "DL(U), FK30"),
    ("016050.00", "22170.14 80 060012.06 70", "C0011(BU,48), FK22+.12, 20"),
    ("016051.00", "22355.02 E0", "SRD(N), ROS"),
    ("016051.40", "22317.00 80 000000.20 50", "L(BU), FK110"),
    ("016052.40", "22355.00 80 074002.15 70", "CT0110(BU,60), ROS, 4"),
    ("016053.40", "1310.00 80", "SIC, SEN"),
    ("016054.00", "1304.35 42", "BRGZ, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
