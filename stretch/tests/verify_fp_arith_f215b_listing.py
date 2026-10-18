#!/usr/bin/env python3
"""verify_fp_arith_f215b_listing.py -- F215 "LOAD FACTOR TEST",
sub-block F215B "TEST SIGN + MOD COMBS" (../decks/fp_arith_f215b.strap)
against jb_af1c p.144.

Four LFTs whose only check is FT bit 60 -- p.98's "the sign of the
addressed operand as modified by the sign modifiers is placed in FT
bit 60".  The encodings differ only in the two modifier bits: LFT
prints .44, LFTA .64 (+20 octal), LFTN .54 (+10), LFTNA .74 (+30).

B3 and B4 give the same answer because FPK32's sign is already zero,
so B4's absolute modifier does nothing -- the recurring blind spot for
A over an already-positive sign.  B2 is the row that exercises A.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f215b.strap").read())

CONST_ROWS = [
    ("022006.00", "1777777777777777777777", "FPK1"),
    ("022045.00", "0001177777777777777760", "FPK32"),
]

SIC  = "1310.00 80"
BSER = "1304.10 00"

CODE_ROWS = [
    ("020215.40", "22006.44 A0",           "B1 LFT(U), FPK1      MS 1, N+A 0"),
    ("020216.00", "16.74 80 020220.34 02", "B1 BB, $FT+.60, $+2.0   sign +1"),
    ("020217.00", SIC, "B1 SIC"), ("020217.40", BSER, "B1 B, SERS"),

    ("020220.00", "22006.64 A0",           "B2 LFTA(U), FPK1     MS 1, A 1"),
    ("020220.40", "16.74 80 020222.74 00", "B2 BZB, $FT+.60, $+2.0  sign +0"),
    ("020221.40", SIC, "B2 SIC"), ("020222.00", BSER, "B2 B, SERS"),

    ("020222.40", "22045.54 A0",           "B3 LFTN(U), FPK32    MS 0, N 1"),
    ("020223.00", "16.74 80 020225.34 02", "B3 BB, $FT+.60, $+2.0   sign +1"),
    ("020224.00", SIC, "B3 SIC"), ("020224.40", BSER, "B3 B, SERS"),

    ("020225.00", "22045.74 A0",           "B4 LFTNA(U), FPK32   MS 0, N+A 1"),
    ("020225.40", "16.74 80 020227.74 02", "B4 BB, $FT+.60, $+2.0   sign +1"),
    ("020226.40", SIC, "B4 SIC"), ("020227.00", BSER, "B4 B, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
