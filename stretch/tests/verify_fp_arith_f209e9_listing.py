#!/usr/bin/env python3
"""verify_fp_arith_f209e9_listing.py -- F209E9
(../decks/fp_arith_f209e9.strap: ADD DOUBLE TO MAGNITUDE's forced zero
must leave the Lost Significance indicator OFF) against jb_af1c
pp.108-109, plus its two constants against the pool p.176.

All six code rows below were read off the printed encoding column
individually. The block closes on 015770.00, the routine's own exit,
and PASS sits there. F209 is transcribed end to end with this block.

E9 is the suite's only oracle for the !forcedZero term in
r.ls = (res.frac == 0) && !(a.frac == 0 && b.frac == 0) && !forcedZero.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f209e9.strap").read())

CONST_ROWS = [
    ("022053.00", "0031052525252525252520", "FPK38"),
    ("022060.00", "0031125252525252525250", "FPK43"),
]

CODE_ROWS = [
    ("015765.00", "15765.50 00", "B, $+.32"),
    ("015765.40", "15766.15 46", "BLSZ, $+.32"),
    ("015766.00", "22053.54 60", "DLN(U), FPK38"),
    ("015766.40", "22060.76 20", "D-MGA(U), FPK43"),
    ("015767.00", "1310.00 80", "SIC, SEN"),
    ("015767.40", "1304.15 42", "BLS, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
