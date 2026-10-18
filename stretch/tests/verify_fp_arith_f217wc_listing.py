#!/usr/bin/env python3
"""verify_fp_arith_f217wc_listing.py -- F217-W "DIVIDE DOUBLE TEST",
sub-block F217WC "TEST CHANGED REGS" (../decks/fp_arith_f217wc.strap)
against jb_af1c p.160.

One check, and it is the other half of p.94's writeback rule: where
F217WA pinned what D/ WRITES, this pins what it ZEROES -- "Accumulator
bits 61-107 are set to zero", which the listing's header spells out as
"CHK L 61-63 AND R 0-43 +0".  Both accumulator words are filled with
ones first, so the zeroing has to happen rather than be inherited.

The check is a 47-bit CT0110 at offset 20, whose right end is IBM 107.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f217wc.strap").read())
CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022006.00", "1777777777777777777777", "FPK1"),
]
CODE_ROWS = [
    ("021100.40", "22006.00 80 000040.36 70", "WC C1111(BU,64), FPK1, 64"),
    ("021101.40", "22006.00 80 000000.36 70", "WC C1111(BU,64), FPK1"),
    ("021102.40", "22006.45 E0",              "WC D/(U), FPK1"),
    ("021103.00", "22005.00 80 057012.15 70", "WC CT0110(BU,47), FPK0, 20  acc bits zero"),
    ("021104.00", "1310.00 80", "WC SIC"), ("021104.40", "1304.35 42", "WC BRGZ"),
]
if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
