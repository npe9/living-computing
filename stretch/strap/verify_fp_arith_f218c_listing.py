#!/usr/bin/env python3
"""verify_fp_arith_f218c_listing.py -- F218 "STORE ROOT TEST",
sub-block F218C "TEST UNCHANGED REGISTERS"
(programs/fp_arith_f218c.strap) against jb_af1c p.168.

p.95: "The entire accumulator and its sign byte remain unchanged."
SRT is the only floating-point operation of which that holds without
exception, so this is the only unchanged-registers block in the
diagnostic that checks the WHOLE eight-bit sign byte -- F214XB, F216C
and F217WD all had to skip bit 4.

The SRT here is SRTA, so the imaginary root indicator cannot come on.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f218c.strap").read())
CONST_ROWS = [("022006.00", "1777777777777777777777", "FPK1")]
SIC  = "1310.00 80"
BRGZ = "1304.35 42"
CODE_ROWS = [
    ("021426.40", "22006.00 80 000040.36 70", "C C1111(BU,64), FPK1, 64"),
    ("021427.40", "22006.00 80 000000.36 70", "C C1111(BU,64), FPK1"),
    ("021430.40", "12.00 80 010000.36 F0",    "C CM1111(BU,8), $SB"),
    ("021431.40", "22355.66 E0",              "C SRTA(U), ROS"),
    ("021432.00", "22006.00 80 000040.25 70", "C1 CT1010(BU,64), FPK1, 64  L 0-63 +1 s"),
    ("021433.00", SIC, "C SIC"), ("021433.40", BRGZ, "C BRGZ"),
    ("021434.00", "22006.00 80 000000.25 70", "C2 CT1010(BU,64), FPK1      R 0-63 +1 s"),
    ("021435.00", SIC, "C SIC"), ("021435.40", BRGZ, "C BRGZ"),
    ("021436.00", "12.00 80 010000.31 70",    "C3 CT1100(BU,8), $SB        SB 0-7 +1 s"),
    ("021437.00", SIC, "C SIC"), ("021437.40", BRGZ, "C BRGZ"),
]
if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
