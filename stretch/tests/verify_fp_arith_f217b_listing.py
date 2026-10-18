#!/usr/bin/env python3
"""verify_fp_arith_f217b_listing.py -- F217 "DIVIDE TEST ROUTINE",
sub-block F217B "TESTS OF SIGN AND MODIFIER COMBINATIONS"
(../decks/fp_arith_f217b.strap) against jb_af1c p.155.

Four rows, each checking the quotient sign in sign byte bit 4.  The
pool supplies sign-pairs for the purpose: FPK52/FPK55 and FPK64/FPK69
are each the same number but for bit 3.

B4's A modifier is invisible -- FPK55's sign is already 1, so
absolute-then-negate lands where negate alone would -- so B3 and B4
expect the same answer.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f217b.strap").read())

CONST_ROWS = [
    ("022071.00", "0001024713560247135620", "FPK52"),
    ("022074.00", "0001024713560247135630", "FPK55"),
    ("022104.00", "0001051627340516273440", "FPK64"),
]

SIC  = "1310.00 80"
BSER = "1304.10 00"

CODE_ROWS = [
    ("020666.40", "22104.50 60", "B1 LN(U), FPK64"),
    ("020667.00", "22071.41 E0", "B1 /(U), FPK52"),
    ("020667.40", "12.04 80 020671.74 02", "B1 BB, $SB+.4, $+2.0   sign +1"),
    ("020670.40", SIC, "B1 SIC"), ("020671.00", BSER, "B1 B, SERS"),

    ("020671.40", "22104.40 60", "B2 L(U), FPK64"),
    ("020672.00", "22074.41 E0", "B2 /(U), FPK55"),
    ("020672.40", "12.04 80 020674.74 02", "B2 BB, $SB+.4, $+2.0   sign +1"),
    ("020673.40", SIC, "B2 SIC"), ("020674.00", BSER, "B2 B, SERS"),

    ("020674.40", "20675.10 00", "B3 B, $+.32"),
    ("020675.00", "22104.50 60", "B3 LN(U), FPK64"),
    ("020675.40", "22074.41 E0", "B3 /(U), FPK55"),
    ("020676.00", "12.04 80 020700.34 00", "B3 BZB, $SB+.4, $+2.0  sign +0"),
    ("020677.00", SIC, "B3 SIC"), ("020677.40", BSER, "B3 B, SERS"),

    ("020700.00", "20700.50 00", "B4 B, $+.32"),
    ("020700.40", "22104.50 60", "B4 LN(U), FPK64"),
    ("020701.00", "22074.71 E0", "B4 /NA(U), FPK55"),
    ("020701.40", "12.04 80 020703.74 00", "B4 BZB, $SB+.4, $+2.0  sign +0"),
    ("020702.40", SIC, "B4 SIC"), ("020703.00", BSER, "B4 B, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
