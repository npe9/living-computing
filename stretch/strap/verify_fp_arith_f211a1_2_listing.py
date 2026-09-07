#!/usr/bin/env python3
"""verify_fp_arith_f211a1_2_listing.py -- F211A1-A2
(programs/fp_arith_f211a1_2.strap: STORE LOW ORDER with a flagged
accumulator exponent) against jb_af1c p.113, plus its four constants
against the pool p.178.

All 21 code rows below were read off the printed encoding column
individually. The block closes on 016163.00, where F211A3 begins, and
PASS sits there.

A2's printed comment reads "ACC EXP IN XFP RNG" where FK25 decodes to
XFN -767; the listing repeated A1's comment. Transcribed as printed.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f211a1_2.strap").read())

CONST_ROWS = [
    ("022171.00", "1777525252525252525240", "FK23"),
    ("022173.00", "1577777777777777777760", "FK25"),
    ("022200.00", "1577617777777777777760", "FK30"),
    ("022212.00", "1777577777777777777770", "FK40"),
]

CODE_ROWS = [
    ("016144.40", "22212.44 60", "DL(U), FK40"),
    ("016145.00", "13.22 00", "Z, $IND"),
    ("016145.40", "22171.14 80 060012.06 70", "C0011(BU,48), FK23+.12, 20"),
    ("016146.40", "22355.44 E0", "SLO(U), ROS"),
    ("016147.00", "22171.00 80 000000.20 50", "L(BU), FK23"),
    ("016150.00", "22355.00 80 074002.15 70", "CT0110(BU,60), ROS, 4"),
    ("016151.00", "1310.00 80", "SIC, SEN"),
    ("016151.40", "1304.35 42", "BRGZ, SERS"),
    ("016152.00", "22355.74 80 016154.34 02", "BB, ROS+.60, $+2.0"),
    ("016153.00", "1310.00 80", "SIC, SEN"),
    ("016153.40", "1304.10 00", "B, SERS"),
    ("016154.00", "22173.44 60", "DL(U), FK25"),
    ("016154.40", "22200.14 80 060012.06 70", "C0011(BU,48), FK30+.12, 20"),
    ("016155.40", "22355.44 E0", "SLO(U), ROS"),
    ("016156.00", "22200.00 80 000000.20 50", "L(BU), FK30"),
    ("016157.00", "22355.00 80 074002.15 70", "CT0110(BU,60), ROS, 4"),
    ("016160.00", "1310.00 80", "SIC, SEN"),
    ("016160.40", "1304.35 42", "BRGZ, SERS"),
    ("016161.00", "22355.74 80 016163.34 00", "BZB, ROS+.60, $+2.0"),
    ("016162.00", "1310.00 80", "SIC, SEN"),
    ("016162.40", "1304.10 00", "B, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
