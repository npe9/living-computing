#!/usr/bin/env python3
"""verify_fp_arith_f217wd_listing.py -- F217-W "DIVIDE DOUBLE TEST",
sub-block F217WD "TEST UNCHANGED REGS"
(../decks/fp_arith_f217wd.strap) against jb_af1c p.160.

The third face of p.94's writeback rule: WA checked what D/ writes, WC
what it zeroes, WD what it leaves alone -- IBM 108-127 and every sign
byte bit but 4.  From the same all-ones start WC demands IBM 61-107
become ZERO and WD demands IBM 108-127 stay ONES, so between them they
put the boundary exactly where p.94 does.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f217wd.strap").read())
CONST_ROWS = [("022006.00", "1777777777777777777777", "FPK1")]
SIC  = "1310.00 80"
BRGZ = "1304.35 42"
CODE_ROWS = [
    ("021107.00", "22006.00 80 000040.36 70", "WD C1111(BU,64), FPK1, 64"),
    ("021110.00", "22006.00 80 000000.36 70", "WD C1111(BU,64), FPK1"),
    ("021111.00", "12.00 80 010000.36 F0",    "WD CM1111(BU,8), $SB"),
    ("021112.00", "22006.45 E0",              "WD D/(U), FPK1"),
    ("021112.40", "22006.00 80 024000.25 70", "WD CT1010(BU,20), FPK1   R44-63 remain +1 s"),
    ("021113.40", SIC, "WD SIC"), ("021114.00", BRGZ, "WD BRGZ"),
    ("021114.40", "12.00 80 004000.31 70",    "WD CT1100(BU,4), $SB     SB0-3 remain +1 s"),
    ("021115.40", SIC, "WD SIC"), ("021116.00", BRGZ, "WD BRGZ"),
    ("021116.40", "12.05 80 003000.31 70",    "WD CT1100(BU,3), $SB+.5  SB5-7 remain +1 s"),
    ("021117.40", SIC, "WD SIC"), ("021120.00", BRGZ, "WD BRGZ"),
]
if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
