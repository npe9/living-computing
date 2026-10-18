#!/usr/bin/env python3
"""verify_fp_arith_f210b_listing.py -- F210B1-B2
(../decks/fp_arith_f210b.strap: SRD must leave the accumulator and its
sign byte register unchanged) against jb_af1c p.111, plus its two
constants against the pool p.176.

All 27 code rows below were read off the printed encoding column
individually. The block closes on 016107.40, the routine's own exit,
and PASS sits there.

FSR2 is the listing's own label at its real address, 016064.00.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f210b.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022006.00", "1777777777777777777777", "FPK1"),
]

CODE_ROWS = [
    ("016064.00", "22005.00 80 000040.00 70", "C0000(BU,64), FPK0, 64"),
    ("016065.00", "22005.00 80 000000.00 70", "C0000(BU,64), FPK0"),
    ("016066.00", "12.00 80 010000.00 F0", "CM0000(BU,8), 10.0"),
    ("016067.00", "22355.42 E0", "SRD(U), ROS"),
    ("016067.40", "22005.00 80 000040.13 70", "CT0101(BU,64), FPK0, 64"),
    ("016070.40", "1310.00 80", "SIC, SEN"),
    ("016071.00", "1304.35 42", "BRGZ, SERS"),
    ("016071.40", "22005.00 80 000000.13 70", "CT0101(BU,64), FPK0"),
    ("016072.40", "1310.00 80", "SIC, SEN"),
    ("016073.00", "1304.35 42", "BRGZ, SERS"),
    ("016073.40", "12.00 80 010000.07 70", "CT0011(BU,8), 10.0"),
    ("016074.40", "1310.00 80", "SIC, SEN"),
    ("016075.00", "1304.35 42", "BRGZ, SERS"),
    ("016075.40", "16076.10 00", "B, $+.32"),
    ("016076.00", "22006.00 80 000040.36 70", "C1111(BU,64), FPK1, 64"),
    ("016077.00", "22006.00 80 000000.36 70", "C1111(BU,64), FPK1"),
    ("016100.00", "12.00 80 010000.36 F0", "CM1111(BU,8), 10.0"),
    ("016101.00", "22355.42 E0", "SRD(U), ROS"),
    ("016101.40", "22006.00 80 000040.25 70", "CT1010(BU,64), FPK1, 64"),
    ("016102.40", "1310.00 80", "SIC, SEN"),
    ("016103.00", "1304.35 42", "BRGZ, SERS"),
    ("016103.40", "22006.00 80 000000.25 70", "CT1010(BU,64), FPK1"),
    ("016104.40", "1310.00 80", "SIC, SEN"),
    ("016105.00", "1304.35 42", "BRGZ, SERS"),
    ("016105.40", "12.00 80 010000.31 70", "CT1100(BU,8), 10.0"),
    ("016106.40", "1310.00 80", "SIC, SEN"),
    ("016107.00", "1304.35 42", "BRGZ, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
