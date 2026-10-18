#!/usr/bin/env python3
"""verify_fp_arith_f209d6_9_listing.py -- F209D6-D9
(../decks/fp_arith_f209d6_9.strap: ADD DOUBLE TO MAGNITUDE's Lost
Significance indicator) against jb_af1c p.107, plus its eight
constants against the pools p.176.

All 26 code rows below were read off the printed encoding column
individually. The block closes on 015670.00, the routine's own exit
("BD,$+1.0"), and PASS sits there.

D8's header comment reads "LS INDICATOR OFF" while its one question is
BZLS, "error if LS ind off" -- which requires LS ON. The encodings
distinguish BZLS (40) from BLS (42), so this is the listing's own
inconsistency and is transcribed as printed.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f209d6_9.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022032.00", "0031177777777777777767", "FPK21"),
    ("022044.00", "0031000000000000000000", "FPK31"),
    ("022045.00", "0001177777777777777760", "FPK32"),
    ("022056.00", "0001040000000000000000", "FPK41"),
    ("022057.00", "0001460000000000000000", "FPK42"),
    ("022205.00", "1777400000000000000000", "FK35"),
    ("022210.00", "0777572525252525252520", "FK38"),
]

CODE_ROWS = [
    ("015652.00", "15652.50 00", "B, $+.32"),
    ("015652.40", "15653.15 46", "BLSZ, $+.32"),
    ("015653.00", "22044.44 60", "DL(U), FPK31"),
    ("015653.40", "22045.14 80 060012.06 70", "C0011(BU,48), FPK32+.12, 20"),
    ("015654.40", "22045.56 20", "D-MG(U), FPK32"),
    ("015655.00", "1310.00 80", "SIC, SEN"),
    ("015655.40", "1304.15 40", "BZLS, SERS"),
    ("015656.00", "15656.50 00", "B, $+.32"),
    ("015656.40", "15657.15 46", "BLSZ, $+.32"),
    ("015657.00", "22005.44 60", "DL(U), FPK0"),
    ("015657.40", "22005.46 20", "D+MG(U), FPK0"),
    ("015660.00", "1310.00 80", "SIC, SEN"),
    ("015660.40", "1304.15 42", "BLS, SERS"),
    ("015661.00", "15661.50 00", "B, $+.32"),
    ("015661.40", "15662.15 46", "BLSZ, $+.32"),
    ("015662.00", "22032.44 60", "DL(U), FPK21"),
    ("015662.40", "22056.14 80 060012.06 70", "C0011(BU,48), FPK41+.12, 20"),
    ("015663.40", "22057.46 20", "D+MG(U), FPK42"),
    ("015664.00", "1310.00 80", "SIC, SEN"),
    ("015664.40", "1304.15 40", "BZLS, SERS"),
    ("015665.00", "15665.50 00", "B, $+.32"),
    ("015665.40", "15666.15 46", "BLSZ, $+.32"),
    ("015666.00", "22205.44 60", "DL(U), FK35"),
    ("015666.40", "22210.46 20", "D+MG(U), FK38"),
    ("015667.00", "1310.00 80", "SIC, SEN"),
    ("015667.40", "1304.15 42", "BLS, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
