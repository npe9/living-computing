#!/usr/bin/env python3
"""verify_fp_arith_f204a_listing.py -- the transcribed F204A1..A3 block
(programs/fp_arith_f204a.strap, the FP Add-to-Memory arithmetic checks)
checked bit-for-bit against jb_af1c p.53, plus its four constants
against the pools on p.176-177. IBM's own STRAP output is the oracle.
"""
import sys
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f204a.strap").read())

CONST_ROWS = [
    ("022053.00", "0031052525252525252520", "FPK38"),
    ("022171.00", "1777525252525252525240", "FK23"),
    ("022172.00", "1577452525252525252520", "FK24"),
    ("022173.00", "1577777777777777777760", "FK25"),
]

LBU  = "22171.00 80 000000.20 50"   # L(BU),FK23
STBU = "22355.00 80 000000.20 D0"   # ST(BU,64),ROS
MADD = "22355.40 A0"                # M+(U),ROS
CT   = "22355.00 80 000000.15 70"   # CT0110(BU,64),ROS
SIC  = "1310.00 80"
BRGZ = "1304.35 42"

def subtest(start, load_op_mc, name):
    # 5 words: L(BU) / ST(BU) / [L(U) M+] / CT0110 / [SIC BRGZ]
    return [
        (f"{start:06o}.00", LBU,  f"{name} L(BU),FK23"),
        (f"{start+1:06o}.00", STBU, f"{name} ST(BU,64),ROS"),
        (f"{start+2:06o}.00", load_op_mc, f"{name} L(U),op"),
        (f"{start+2:06o}.40", MADD, f"{name} M+(U),ROS"),
        (f"{start+3:06o}.00", CT,   f"{name} CT0110,ROS"),
        (f"{start+4:06o}.00", SIC,  f"{name} SIC,SEN"),
        (f"{start+4:06o}.40", BRGZ, f"{name} BRGZ,SERS"),
    ]

CODE_ROWS = (
    subtest(0o12331, "22172.40 60", "A1/FK24") +   # L(U),FK24
    subtest(0o12336, "22053.40 60", "A2/FPK38") +  # L(U),FPK38
    subtest(0o12343, "22173.40 60", "A3/FK25")     # L(U),FK25
)

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
