#!/usr/bin/env python3
"""verify_fp_arith_f213xc_listing.py -- F213-X "ADD TO EXPONENT
IMMEDIATE TEST", sub-block F213-XC "TEST UNCHANGED REGS"
(../decks/fp_arith_f213xc.strap) against jb_af1c p.136.  This
completes F213-X.

The instruction lengths are what settle this block's one oddity.  XC2's
final CT1100 has no SIC/branch after it -- every other check in F213
does -- and the addresses leave no room for a missing row: the CT1100
is a full word occupying 017626.40 and 017627.00, and BD,$+1.0 is
printed at 017627.40.  So the check really is computed and discarded.
See the program header.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f213xc.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022006.00", "1777777777777777777777", "FPK1"),
]

SIC  = "1310.00 80"
BRGZ = "1304.35 42"

CODE_ROWS = [
    # F213XC1 -- everything zeroed; both exponents N, an ordinary sum.
    ("017613.00", "10.22 00",                   "Z, $L"),
    ("017613.40", "11.22 00",                   "Z, $R"),
    ("017614.00", "12.22 00",                   "Z, $SB"),
    ("017614.40", "1400.47 60",                 "E+I(U), +6"),
    ("017615.00", "22005.00 80 024000.13 70",   "CT0101(BU,20), FPK0"),
    ("017616.00", SIC, "SIC, SEN"), ("017616.40", BRGZ, "BRGZ, SERS"),
    ("017617.00", "12.00 80 010000.07 70",      "CT0011(BU,8), $SB"),
    ("017620.00", SIC, "SIC, SEN"), ("017620.40", BRGZ, "BRGZ, SERS"),

    # F213XC2 -- all ones, which makes the accumulator XFN, so this one
    # takes the flagged path.
    ("017621.00", "22006.00 80 000040.36 70",   "C1111(BU,64), FPK1, 64"),
    ("017622.00", "22006.00 80 000000.36 70",   "C1111(BU,64), FPK1"),
    ("017623.00", "12.00 80 010000.36 F0",      "CM1111(BU,8), $SB"),
    ("017624.00", "1600.47 60",                 "E+I(U), +7"),
    ("017624.40", "22006.00 80 024000.25 70",   "CT1010(BU,20), FPK1"),
    ("017625.40", SIC, "SIC, SEN"), ("017626.00", BRGZ, "BRGZ, SERS"),
    ("017626.40", "12.00 80 010000.31 70",      "CT1100(BU,8), $SB  (result never tested)"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
