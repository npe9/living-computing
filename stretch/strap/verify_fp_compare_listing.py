#!/usr/bin/env python3
"""verify_fp_compare_listing.py -- the transcribed F202A19/F202A20
block (programs/fp_compare_f202a.strap) checked bit-for-bit against the
machine code printed in jb_af1c p.33, plus the three FP constants it
uses against the pool on p.176. IBM's own STRAP output as the oracle.
"""
import sys
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_compare_f202a.strap").read())

# Constants (pool, p.176), each the 22-octal-digit machine word.
CONST_ROWS = [
    ("022007.00", "1777777777777777777760", "FPK2"),
    ("022032.00", "0031177777777777777767", "FPK21"),
    ("022037.00", "1777577777777777777760", "FPK26"),
]

# Code (p.33), each half-word as printed "wwwwww.bb HH".
CODE_ROWS = [
    ("011422.00", "22007.40 60", "F202A19 L(U),FPK2"),
    ("011422.40", "13.22 00",    "Z,$IND"),
    ("011423.00", "22037.41 20", "K(U),FPK26"),
    ("011423.40", "1310.00 80",  "SIC,SEN"),
    ("011424.00", "1304.36 40",  "BZAL,SERS"),
    ("011424.40", "1310.00 80",  "SIC,SEN"),
    ("011425.00", "1304.36 C2",  "BAE,SERS"),
    ("011425.40", "1310.00 80",  "SIC,SEN"),
    ("011426.00", "1304.37 42",  "BAH,SERS"),
    ("011426.40", "22007.40 60", "F202A20 L(U),FPK2"),
    ("011427.00", "13.22 00",    "Z,$IND"),
    ("011427.40", "22032.41 20", "K(U),FPK21"),
    ("011430.00", "1310.00 80",  "SIC,SEN"),
    ("011430.40", "1304.36 40",  "BZAL,SERS"),
    ("011431.00", "1310.00 80",  "SIC,SEN"),
    ("011431.40", "1304.36 C2",  "BAE,SERS"),
    ("011432.00", "1310.00 80",  "SIC,SEN"),
    ("011432.40", "1304.37 42",  "BAH,SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
