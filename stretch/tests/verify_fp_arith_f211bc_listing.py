#!/usr/bin/env python3
"""verify_fp_arith_f211bc_listing.py -- F211B1 and F211C
(../decks/fp_arith_f211bc.strap: SLO leaves the accumulator unchanged,
and sets MOP) against jb_af1c p.114, plus its two constants against the
pool p.176.

All 20 code rows below were read off the printed encoding column
individually. The block closes on 016262.40, the routine's own exit,
and PASS sits there. F211 is transcribed through A10 and B-C with this
block; A5-A6 are deliberately skipped as more SLO(U) exponent-walking.

F211C has no LC question, where F210D2 had one for SRD -- matching
p.97, which lists no LOST CARRY among SLO's indicators.

FSLO2 is the listing's own label at its real address, 016245.00.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f211bc.strap").read())

CONST_ROWS = [
    ("022006.00", "1777777777777777777777", "FPK1"),
    ("022052.00", "0031125252525252525240", "FPK37"),
]

CODE_ROWS = [
    ("016245.00", "22006.00 80 000040.36 70", "C1111(BU,64), FPK1, 64"),
    ("016246.00", "22006.00 80 000000.36 70", "C1111(BU,64), FPK1"),
    ("016247.00", "12.00 80 010000.36 F0", "CM1111(BU,8), 10.0"),
    ("016250.00", "22355.44 E0", "SLO(U), ROS"),
    ("016250.40", "22006.00 80 000040.25 70", "CT1010(BU,64), FPK1, 64"),
    ("016251.40", "1310.00 80", "SIC, SEN"),
    ("016252.00", "1304.35 42", "BRGZ, SERS"),
    ("016252.40", "22006.00 80 000000.25 70", "CT1010(BU,64), FPK1"),
    ("016253.40", "1310.00 80", "SIC, SEN"),
    ("016254.00", "1304.35 42", "BRGZ, SERS"),
    ("016254.40", "12.00 80 010000.31 70", "CT1100(BU,8), 10.0"),
    ("016255.40", "1310.00 80", "SIC, SEN"),
    ("016256.00", "1304.35 42", "BRGZ, SERS"),
    ("016256.40", "16257.10 00", "B, $+.32"),
    ("016257.00", "16257.73 C6", "BMOPZ, $+.32"),
    ("016257.40", "22052.44 60", "DL(U), FPK37"),
    ("016260.00", "22052.14 80 060012.06 70", "C0011(BU,48), FPK37+.12, 20"),
    ("016261.00", "22355.44 E0", "SLO(U), ROS"),
    ("016261.40", "1310.00 80", "SIC, SEN"),
    ("016262.00", "1304.33 C0", "BZMOP, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
