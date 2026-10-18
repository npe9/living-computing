#!/usr/bin/env python3
"""verify_fp_arith_f217xc_listing.py -- F217-XC "TEST UNCHANGED REGS"
(../decks/fp_arith_f217xc.strap) against jb_af1c p.163.

R/'s writeback is DIVIDE's -- accumulator bits 60-127 and the sign
byte's other seven bits must survive.  It cannot discriminate where
the flag bits come from: the sign byte is filled with ones (flags 7)
and the dividend FPK1 also has flags 7, so taking SB 5-7 from the
accumulator or from the dividend both write 111.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f217xc.strap").read())
CONST_ROWS = [("022006.00", "1777777777777777777777", "FPK1")]
SIC  = "1310.00 80"
BRGZ = "1304.35 42"
CODE_ROWS = [
    ("021201.00", "22006.00 80 000040.36 70", "XC C1111(BU,64), FPK1, 64"),
    ("021202.00", "22006.00 80 000000.36 70", "XC C1111(BU,64), FPK1"),
    ("021203.00", "12.00 80 010000.36 F0",    "XC CM1111(BU,8), $SB"),
    ("021204.00", "22006.43 E0",              "XC R/(U), FPK1"),
    ("021204.40", "22006.00 80 000000.25 70", "XC CT1010(BU,64), FPK1   R remain +1 s"),
    ("021205.40", SIC, "XC SIC"), ("021206.00", BRGZ, "XC BRGZ"),
    ("021206.40", "12.00 80 004000.31 70",    "XC CT1100(BU,4), $SB     SB 0-3 remain +1 s"),
    ("021207.40", SIC, "XC SIC"), ("021210.00", BRGZ, "XC BRGZ"),
    ("021210.40", "12.05 80 003000.31 70",    "XC CT1100(BU,3), $SB+.5  SB 5-7 remain +1 s"),
    ("021211.40", SIC, "XC SIC"), ("021212.00", BRGZ, "XC BRGZ"),
]
if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
