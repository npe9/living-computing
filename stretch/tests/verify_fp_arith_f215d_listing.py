#!/usr/bin/env python3
"""verify_fp_arith_f215d_listing.py -- F215 "LOAD FACTOR TEST",
sub-block F215D "TEST UNCHANGED REGS" (../decks/fp_arith_f215d.strap)
against jb_af1c p.145.

p.98: "The accumulator does not participate in the operation and
remains unchanged."  Left word, right word and sign byte are filled
with ones, an LFT runs, and all three must come back ones.  Unlike
F214XB this checks the WHOLE sign byte including bit 4, since LFT
writes no accumulator sign at all.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f215d.strap").read())

CONST_ROWS = [("022006.00", "1777777777777777777777", "FPK1")]

SIC  = "1310.00 80"
BRGZ = "1304.35 42"

CODE_ROWS = [
    ("020236.00", "22006.00 80 000040.36 70", "D C1111(BU,64), FPK1, 64"),
    ("020237.00", "22006.00 80 000000.36 70", "D C1111(BU,64), FPK1"),
    ("020240.00", "12.00 80 010000.36 F0",    "D CM1111(BU,8), $SB"),
    ("020241.00", "22006.44 A0",              "D LFT(U), FPK1"),
    ("020241.40", "22006.00 80 000040.25 70", "D CT1010(BU,64), FPK1, 64  does L remain +1 s"),
    ("020242.40", SIC, "D SIC"), ("020243.00", BRGZ, "D BRGZ"),
    ("020243.40", "22006.00 80 000000.25 70", "D CT1010(BU,64), FPK1      does R remain +1 s"),
    ("020244.40", SIC, "D SIC"), ("020245.00", BRGZ, "D BRGZ"),
    ("020245.40", "12.00 80 010000.31 70",    "D CT1100(BU,8), $SB        does SB remain +1 s"),
    ("020246.40", SIC, "D SIC"), ("020247.00", BRGZ, "D BRGZ"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
