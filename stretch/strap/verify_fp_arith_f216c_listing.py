#!/usr/bin/env python3
"""verify_fp_arith_f216c_listing.py -- F216 "MULTIPLY AND ADD TEST",
sub-block F216C "TEST OF UNCHANGED REGISTERS"
(programs/fp_arith_f216c.strap) against jb_af1c p.151.

*+'s version of F214XB.  p.98: "accumulator bits 108-127 remain
unchanged", and the sum's sign replaces sign byte bit 4 -- so C1 and
C2 check IBM 108-127 and the sign byte's other seven bits from both
polarities.  C2 is the load-bearing one: DL zeroes IBM 60-107 while
leaving 108-127 as ones, so *+ genuinely writes across 60-107 and the
twenty bits above must survive.

SB 5-7 are the flag bits, so C2 pins that *+ carries the accumulator's
flags through unchanged.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f216c.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022006.00", "1777777777777777777777", "FPK1"),
    ("022071.00", "0001024713560247135620", "FPK52"),
    ("022103.00", "0002177777777777777760", "FPK62"),
    ("022121.00", "0001100000000000000000", "FPK80"),
]

SIC  = "1310.00 80"
BRGZ = "1304.35 42"

CODE_ROWS = [
    # C1
    ("020464.00", "22005.00 80 000000.20 50", "C1 L(BU), FPK0"),
    ("020465.00", "12.00 80 010000.00 F0",    "C1 CM0000(BU,8), $SB"),
    ("020466.00", "22071.44 A0",              "C1 LFT(U), FPK52"),
    ("020466.40", "22121.43 A0",              "C1 *+(U), FPK80"),
    ("020467.00", "22005.00 80 024000.13 70", "C1 CT0101(BU,20), FPK0   R44-63 remain +0"),
    ("020470.00", SIC, "C1 SIC"), ("020470.40", BRGZ, "C1 BRGZ"),
    ("020471.00", "12.00 80 004000.07 70",    "C1 CT0011(BU,4), $SB     SB0-3 remain +0"),
    ("020472.00", SIC, "C1 SIC"), ("020472.40", BRGZ, "C1 BRGZ"),
    ("020473.00", "12.05 80 003000.07 70",    "C1 CT0011(BU,3), $SB+.5  SB5-7 remain +0"),
    ("020474.00", SIC, "C1 SIC"), ("020474.40", BRGZ, "C1 BRGZ"),
    # C2
    ("020475.00", "22006.00 80 000000.20 50", "C2 L(BU), FPK1"),
    ("020476.00", "22006.00 80 000040.36 70", "C2 C1111(BU,64), FPK1, 64"),
    ("020477.00", "22103.44 60",              "C2 DL(U), FPK62"),
    ("020477.40", "12.00 80 010000.36 F0",    "C2 CM1111(BU,8), $SB"),
    ("020500.40", "22071.44 A0",              "C2 LFT(U), FPK52"),
    ("020501.00", "22121.43 A0",              "C2 *+(U), FPK80"),
    ("020501.40", "22006.00 80 024000.25 70", "C2 CT1010(BU,20), FPK1   R44-63 remain +1 s"),
    ("020502.40", SIC, "C2 SIC"), ("020503.00", BRGZ, "C2 BRGZ"),
    ("020503.40", "12.00 80 004000.31 70",    "C2 CT1100(BU,4), $SB     SB0-3 remain +1 s"),
    ("020504.40", SIC, "C2 SIC"), ("020505.00", BRGZ, "C2 BRGZ"),
    ("020505.40", "12.05 80 003000.31 70",    "C2 CT1100(BU,3), $SB+.5  SB5-7 remain +1 s"),
    ("020506.40", SIC, "C2 SIC"), ("020507.00", BRGZ, "C2 BRGZ"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
