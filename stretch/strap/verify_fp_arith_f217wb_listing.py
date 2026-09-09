#!/usr/bin/env python3
"""verify_fp_arith_f217wb_listing.py -- F217-W "DIVIDE DOUBLE TEST",
sub-block F217WB "TEST SIGN AND MOD COMBS"
(programs/fp_arith_f217wb.strap) against jb_af1c p.160.

D/'s version of F217B: four rows, each checking the quotient sign in
sign byte bit 4.  WB4's A modifier is invisible (FPK55's sign is
already 1), so WB3 and WB4 expect the same answer.

D/NA(U) prints ".75 E0" against D/(U)'s ".45 E0".
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f217wb.strap").read())

CONST_ROWS = [
    ("022071.00", "0001024713560247135620", "FPK52"),
    ("022074.00", "0001024713560247135630", "FPK55"),
    ("022104.00", "0001051627340516273440", "FPK64"),
]
SIC  = "1310.00 80"
BSER = "1304.10 00"
CODE_ROWS = [
    ("021064.40", "22104.54 60", "WB1 DLN(U), FPK64"),
    ("021065.00", "22071.45 E0", "WB1 D/(U), FPK52"),
    ("021065.40", "12.04 80 021067.74 02", "WB1 BB, $SB+.4, $+2.0   sign +1"),
    ("021066.40", SIC, "WB1 SIC"), ("021067.00", BSER, "WB1 B, SERS"),
    ("021067.40", "22104.44 60", "WB2 DL(U), FPK64"),
    ("021070.00", "22074.45 E0", "WB2 D/(U), FPK55"),
    ("021070.40", "12.04 80 021072.74 02", "WB2 BB, $SB+.4, $+2.0   sign +1"),
    ("021071.40", SIC, "WB2 SIC"), ("021072.00", BSER, "WB2 B, SERS"),
    ("021072.40", "22104.54 60", "WB3 DLN(U), FPK64"),
    ("021073.00", "22074.45 E0", "WB3 D/(U), FPK55"),
    ("021073.40", "12.04 80 021075.74 00", "WB3 BZB, $SB+.4, $+2.0  sign +0"),
    ("021074.40", SIC, "WB3 SIC"), ("021075.00", BSER, "WB3 B, SERS"),
    ("021075.40", "22104.54 60", "WB4 DLN(U), FPK64"),
    ("021076.00", "22074.75 E0", "WB4 D/NA(U), FPK55"),
    ("021076.40", "12.04 80 021100.74 00", "WB4 BZB, $SB+.4, $+2.0  sign +0"),
    ("021077.40", SIC, "WB4 SIC"), ("021100.00", BSER, "WB4 B, SERS"),
]
if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
