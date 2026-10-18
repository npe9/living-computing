#!/usr/bin/env python3
"""verify_fp_arith_f208d1_6_listing.py -- F208D1-D6
(../decks/fp_arith_f208d1_6.strap: ADD DOUBLE's Lost Carry and Lost
Significance indicator tests) checked bit-for-bit against jb_af1c
pp.98-99, plus its eight constants against the pool pp.176-177.

All 35 code rows below were read off the printed encoding column
individually. The block's arithmetic closes on 015167.40, which is
where the listing's next sub-test F208D7 (label SAP9G, "TEST EXPONENT
RANGE INDICATORS") begins, and that is where PASS sits here.
"""
import sys
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f208d1_6.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022032.00", "0031177777777777777767", "FPK21"),
    ("022044.00", "0031000000000000000000", "FPK31"),
    ("022046.00", "0001177777777777777740", "FPK33"),
    ("022056.00", "0001040000000000000000", "FPK41"),
    ("022057.00", "0001460000000000000000", "FPK42"),
    ("022202.00", "0027125252525252525000", "FK32"),
    ("022205.00", "1777400000000000000000", "FK35"),
]

CODE_ROWS = [
    ("015145.00", "15145.53 46", "BLCZ, $+.32"),
    ("015145.40", "22032.44 60", "DL(U), FPK21"),
    ("015146.00", "22032.44 20", "D+(U), FPK21"),
    ("015146.40", "1310.00 80", "SIC, SEN"),
    ("015147.00", "1304.13 40", "BZLC, SERS"),
    ("015147.40", "15150.10 00", "B, $+.32"),
    ("015150.00", "15150.53 46", "BLCZ, $+.32"),
    ("015150.40", "22032.44 60", "DL(U), FPK21"),
    ("015151.00", "22032.04 20", "D+(N), FPK21"),
    ("015151.40", "1310.00 80", "SIC, SEN"),
    ("015152.00", "1304.13 42", "BLC, SERS"),
    ("015152.40", "15153.10 00", "B, $+.32"),
    ("015153.00", "15153.55 46", "BLSZ, $+.32"),
    ("015153.40", "22044.44 60", "DL(U), FPK31"),
    ("015154.00", "22046.14 80 060012.06 70", "C0011(BU,48), FPK33+.12, 20"),
    ("015155.00", "22046.54 20", "D-(U), FPK33"),
    ("015155.40", "1310.00 80", "SIC, SEN"),
    ("015156.00", "1304.15 40", "BZLS, SERS"),
    ("015156.40", "15157.15 46", "BLSZ, $+.32"),
    ("015157.00", "22005.44 60", "DL(U), FPK0"),
    ("015157.40", "22005.44 20", "D+(U), FPK0"),
    ("015160.00", "1310.00 80", "SIC, SEN"),
    ("015160.40", "1304.15 42", "BLS, SERS"),
    ("015161.00", "15161.55 46", "BLSZ, $+.32"),
    ("015161.40", "22032.44 60", "DL(U), FPK21"),
    ("015162.00", "22056.14 80 060012.06 70", "C0011(BU,48), FPK41+.12, 20"),
    ("015163.00", "22057.44 20", "D+(U), FPK42"),
    ("015163.40", "1310.00 80", "SIC, SEN"),
    ("015164.00", "1304.15 40", "BZLS, SERS"),
    ("015164.40", "15165.10 00", "B, $+.32"),
    ("015165.00", "15165.55 46", "BLSZ, $+.32"),
    ("015165.40", "22205.44 60", "DL(U), FK35"),
    ("015166.00", "22202.44 20", "D+(U), FK32"),
    ("015166.40", "1310.00 80", "SIC, SEN"),
    ("015167.00", "1304.15 42", "BLS, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
