#!/usr/bin/env python3
"""verify_fp_arith_f210d_listing.py -- F210D1-D2
(../decks/fp_arith_f210d.strap: SRD's MOP and LOST CARRY indicators)
against jb_af1c p.112, plus its two constants against the pool p.176.

All 13 code rows below were read off the printed encoding column
individually. The block closes on 016137.40, the routine's own exit,
and PASS sits there. F210 is transcribed end to end with this block.

D2 is the LC oracle recorded as missing since F210A5: A5 produces the
rounding overflow and asks what it did to the stored word, D2 asks
what it did to the indicator.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f210d.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022045.00", "0001177777777777777760", "FPK32"),
]

CODE_ROWS = [
    ("016130.40", "16131.10 00", "B, $+.32"),
    ("016131.00", "16131.73 C6", "BMOPZ, $+.32"),
    ("016131.40", "22005.44 60", "DL(U), FPK0"),
    ("016132.00", "22355.42 E0", "SRD(U), ROS"),
    ("016132.40", "1310.00 80", "SIC, SEN"),
    ("016133.00", "1304.33 C0", "BZMOP, SERS"),
    ("016133.40", "16134.10 00", "B, $+.32"),
    ("016134.00", "16134.53 46", "BLCZ, $+.32"),
    ("016134.40", "22045.44 60", "DL(U), FPK32"),
    ("016135.00", "22045.14 80 060012.06 70", "C0011(BU,48), FPK32+.12, 20"),
    ("016136.00", "22355.42 E0", "SRD(U), ROS"),
    ("016136.40", "1310.00 80", "SIC, SEN"),
    ("016137.00", "1304.13 40", "BZLC, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
