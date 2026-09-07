#!/usr/bin/env python3
"""verify_fp_arith_f212b_listing.py -- F212B "TESTS OF SIGN AND
MODIFIER COMBINATIONS" (programs/fp_arith_f212b.strap) against jb_af1c
p.119, plus its constants against the pool p.176.

The whole point of the block is the four modifier spellings, and their
encodings are the thing to check: every row carries the SAME address
200 octal (amount 1, direction bit CLEAR) and they differ only in bits
19-20.

    B1  SHFR(U),1    "200.77 20"   A=1 N=1
    B2  SHFA(U),1    "200.67 20"   A=1 N=0
    B3  SHFN(U),1    "200.57 20"   A=0 N=1
    B4  SHFNA(U),1   "200.77 20"   A=1 N=1

B1 and B4 assemble identically -- the page really does print the same
word twice -- so those two pin the STRAP spellings rather than the
machine. B3 is the only row where N acts without A.

FSF3 is the listing's own label at its own address, 016540.40, and the
block's last row sits at 016567.40 where the page has "BD,$+1.0".
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f212b.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022125.00", "0001000077777777777760", "FPK87"),
    ("022126.00", "0001000177777777777740", "FPK88"),
    ("022136.00", "0001077777777777760000", "FPK96"),
    ("022137.00", "0001177777777777740000", "FPK97"),
]

CODE_ROWS = [
    # F212B1 -- SHFR, in full.
    ("016540.40", "22005.44 60", "DL(U), FPK0"),
    ("016541.00", "22137.14 80 060012.06 70", "C0011(BU,48), FPK97+.12, 20"),
    ("016542.00", "200.77 20", "SHFR(U), 1"),
    ("016542.40", "22005.14 80 060042.15 70", "CT0110(BU,48), FPK0+.12, 68"),
    ("016543.40", "1310.00 80", "SIC, SEN"),
    ("016544.00", "1304.35 42", "BRGZ, SERS"),
    ("016544.40", "22136.14 80 060012.15 70", "CT0110(BU,48), FPK96+.12, 20"),
    ("016545.40", "1310.00 80", "SIC, SEN"),
    ("016546.00", "1304.35 42", "BRGZ, SERS"),

    # F212B2 -- SHFA, the only LEFT shift in the block.
    ("016546.40", "22125.44 60", "DL(U), FPK87"),
    ("016547.00", "200.67 20", "SHFA(U), 1"),
    ("016547.40", "22126.14 80 060042.15 70", "CT0110(BU,48), FPK88+.12, 68"),
    ("016551.40", "22005.14 80 060012.15 70", "CT0110(BU,48), FPK0+.12, 20"),

    # F212B3 -- SHFN, N without A.
    ("016553.40", "22005.44 60", "DL(U), FPK0"),
    ("016554.00", "22137.14 80 060012.06 70", "C0011(BU,48), FPK97+.12, 20"),
    ("016555.00", "200.57 20", "SHFN(U), 1"),
    ("016555.40", "22005.14 80 060042.15 70", "CT0110(BU,48), FPK0+.12, 68"),
    ("016557.40", "22136.14 80 060012.15 70", "CT0110(BU,48), FPK96+.12, 20"),

    # F212B4 -- SHFNA.
    ("016561.40", "22005.44 60", "DL(U), FPK0"),
    ("016562.00", "22137.14 80 060012.06 70", "C0011(BU,48), FPK97+.12, 20"),
    ("016563.00", "200.77 20", "SHFNA(U), 1"),
    ("016563.40", "22005.14 80 060042.15 70", "CT0110(BU,48), FPK0+.12, 68"),
    ("016565.40", "22136.14 80 060012.15 70", "CT0110(BU,48), FPK96+.12, 20"),
    ("016566.40", "1310.00 80", "SIC, SEN"),
    ("016567.00", "1304.35 42", "BRGZ, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
