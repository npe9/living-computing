#!/usr/bin/env python3
"""verify_fp_arith_f215c_listing.py -- F215 "LOAD FACTOR TEST",
sub-block F215C "TEST CHANGED REGS" (../decks/fp_arith_f215c.strap)
against jb_af1c p.145.

One check, and it closes what F215A/F215B could not reach: p.98's "FT
bits 61-63 are set to zero".  CM1111 fills word 14 with ones, LFT
follows, and CT0110(BU,3) over $FT+.61 demands zeros back.

Still blind to one fault: FPK2's own flag bits are zero, so an LFT
copying the operand's flags would also write 000 here.  What C catches
is an LFT that leaves those bits alone.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f215c.strap").read())

CONST_ROWS = [("022007.00", "1777777777777777777760", "FPK2")]

CODE_ROWS = [
    ("020231.40", "22007.00 80 000000.20 50", "C L(BU), FPK2"),
    ("020232.40", "16.00 80 000000.36 F0",    "C CM1111(BU,64), $FT"),
    ("020233.40", "22007.44 A0",              "C LFT(U), FPK2"),
    ("020234.00", "16.75 80 003000.15 70",    "C CT0110(BU,3), $FT+.61   bits 61-63 zero?"),
    ("020235.00", "1310.00 80", "C SIC"), ("020235.40", "1304.35 42", "C BRGZ"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
