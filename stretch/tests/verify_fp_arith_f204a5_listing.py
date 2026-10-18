#!/usr/bin/env python3
"""verify_fp_arith_f204a5_listing.py -- the transcribed F204A5 block
(../decks/fp_arith_f204a5.strap, a discriminating M+ Add-to-Memory
test) checked bit-for-bit against jb_af1c p.53, plus its three
constants against the pool on p.176. IBM's own STRAP output is oracle.
"""
import sys
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f204a5.strap").read())

CONST_ROWS = [
    ("022045.00", "0001177777777777777760", "FPK32"),
    ("022050.00", "0001125252525252525240", "FPK35"),
    ("022054.00", "0001052525252525252520", "FPK39"),
]

CODE_ROWS = [
    ("012355.00", "22050.00 80 000000.20 50", "L(BU),FPK35"),
    ("012356.00", "22355.00 80 000000.20 D0", "ST(BU,64),ROS"),
    ("012357.00", "22054.40 60", "L(U),FPK39"),
    ("012357.40", "22355.40 A0", "M+(U),ROS"),
    ("012360.00", "22045.00 80 000000.20 50", "L(BU,64),FPK32"),
    ("012361.00", "22355.00 80 000000.15 70", "CT0110(BU,64),ROS"),
    ("012362.00", "1310.00 80", "SIC,SEN"),
    ("012362.40", "1304.35 42", "BRGZ,SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
