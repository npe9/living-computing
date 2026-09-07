#!/usr/bin/env python3
"""verify_fp_arith_f210a8_listing.py -- F210A8
(programs/fp_arith_f210a8.strap: the one sub-test where SRD actually
normalizes) against jb_af1c p.111, plus its three constants against
the pool p.178.

All 8 code rows below were read off the printed encoding column
individually. The block closes on 016062.00, the routine's own exit,
and PASS sits there.

FK47 (exponent +50, fraction 000fffffffff) with FK22's all-ones low
half rounds to 001000000000, which normalizes eleven places left to
800000000000 with the exponent going +50 -> +39 -- exactly FK52.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f210a8.strap").read())

CONST_ROWS = [
    ("022170.00", "0400177777777777777760", "FK22"),
    ("022221.00", "0031000017777777777760", "FK47"),
    ("022226.00", "0023500000000000000000", "FK52"),
]

CODE_ROWS = [
    ("016054.40", "16055.10 00", "B, $+.32"),
    ("016055.00", "22221.44 60", "DL(U), FK47"),
    ("016055.40", "22170.14 80 060012.06 70", "C0011(BU,48), FK22+.12, 20"),
    ("016056.40", "22355.02 E0", "SRD(N), ROS"),
    ("016057.00", "22226.00 80 000000.20 50", "L(BU), FK52"),
    ("016060.00", "22355.00 80 074002.15 70", "CT0110(BU,60), ROS, 4"),
    ("016061.00", "1310.00 80", "SIC, SEN"),
    ("016061.40", "1304.35 42", "BRGZ, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
