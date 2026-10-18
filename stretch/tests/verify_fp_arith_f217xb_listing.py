#!/usr/bin/env python3
"""verify_fp_arith_f217xb_listing.py -- F217-XB "TEST SIGN AND MOD
COMBS" (../decks/fp_arith_f217xb.strap) against jb_af1c p.163.

R/'s sign matrix.  It uses the pool's sign-pair FPK64/FPK69 -- the
same number but for bit 3 -- so the memory sign changes and nothing
else does.  FPK69 is the constant F217A's transcription confused with
FPK64; here both appear side by side and the sign is all that is
checked.

The modifier goes on the R/, whose addressed operand is the DIVIDEND,
so these four rows are the only place in F217-X exercising p.94's
"the sign of the dividend is modified by the sign modifiers".
XB4's A is invisible (FPK69's sign is already 1), so XB3 and XB4
expect the same answer.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f217xb.strap").read())
CONST_ROWS = [
    ("022071.00", "0001024713560247135620", "FPK52"),
    ("022104.00", "0001051627340516273440", "FPK64"),
    ("022111.00", "0001051627340516273450", "FPK69"),
]
SIC  = "1310.00 80"
BSER = "1304.10 00"
CODE_ROWS = [
    ("021165.00", "22071.50 60", "XB1 LN(U), FPK52"),
    ("021165.40", "22104.43 E0", "XB1 R/(U), FPK64"),
    ("021166.00", "12.04 80 021170.34 02", "XB1 BB, $SB+.4, $+2.0   is sign 1"),
    ("021167.00", SIC, "XB1 SIC"), ("021167.40", BSER, "XB1 B, SERS"),
    ("021170.00", "22071.40 60", "XB2 L(U), FPK52"),
    ("021170.40", "22111.43 E0", "XB2 R/(U), FPK69"),
    ("021171.00", "12.04 80 021173.34 02", "XB2 BB, $SB+.4, $+2.0   is sign 1"),
    ("021172.00", SIC, "XB2 SIC"), ("021172.40", BSER, "XB2 B, SERS"),
    ("021173.00", "22071.50 60", "XB3 LN(U), FPK52"),
    ("021173.40", "22111.43 E0", "XB3 R/(U), FPK69"),
    ("021174.00", "12.04 80 021176.34 00", "XB3 BZB, $SB+.4, $+2.0  is sign 0"),
    ("021175.00", SIC, "XB3 SIC"), ("021175.40", BSER, "XB3 B, SERS"),
    ("021176.00", "22071.50 60", "XB4 LN(U), FPK52"),
    ("021176.40", "22111.73 E0", "XB4 R/NA(U), FPK69"),
    ("021177.00", "12.04 80 021201.34 00", "XB4 BZB, $SB+.4, $+2.0  is sign 0"),
    ("021200.00", SIC, "XB4 SIC"), ("021200.40", BSER, "XB4 B, SERS"),
]
if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
