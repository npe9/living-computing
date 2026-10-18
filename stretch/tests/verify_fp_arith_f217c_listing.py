#!/usr/bin/env python3
"""verify_fp_arith_f217c_listing.py -- F217 "DIVIDE TEST ROUTINE",
sub-block F217C (unchanged registers) (../decks/fp_arith_f217c.strap)
against jb_af1c p.155.

p.93: the quotient replaces accumulator bits 0-59, "accumulator bits
60-127 remain unchanged", and no remainder is retained.  Fill L, R and
the sign byte with ones, divide, and demand R and the sign byte's
other seven bits survive.  Bit 4 is skipped -- it is the quotient
sign.  SB 5-7 are the flag bits.

FPK1 is a valid divisor (fraction ffffffffffff), so the division
really happens; both operands are XFN at -2047 and p.94 gives the
quotient the divisor's exponent sign-reversed, but nothing here checks
the result.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f217c.strap").read())

CONST_ROWS = [("022006.00", "1777777777777777777777", "FPK1")]

SIC  = "1310.00 80"
BRGZ = "1304.35 42"

CODE_ROWS = [
    ("020703.40", "22006.00 80 000040.36 70", "C C1111(BU,64), FPK1, 64"),
    ("020704.40", "22006.00 80 000000.36 70", "C C1111(BU,64), FPK1"),
    ("020705.40", "12.00 80 010000.36 F0",    "C CM1111(BU,8), $SB"),
    ("020706.40", "22006.41 E0",              "C /(U), FPK1"),
    ("020707.00", "22006.00 80 000000.25 70", "C CT1010(BU,64), FPK1   R remain +1 s"),
    ("020710.00", SIC, "C SIC"), ("020710.40", BRGZ, "C BRGZ"),
    ("020711.00", "12.00 80 004000.31 70",    "C CT1100(BU,4), $SB     SB0-3 remain +1 s"),
    ("020712.00", SIC, "C SIC"), ("020712.40", BRGZ, "C BRGZ"),
    ("020713.00", "12.05 80 003000.31 70",    "C CT1100(BU,3), $SB+.5  SB5-7 remain +1 s"),
    ("020714.00", SIC, "C SIC"), ("020714.40", BRGZ, "C BRGZ"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
