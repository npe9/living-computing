#!/usr/bin/env python3
"""verify_fp_arith_f204c_listing.py -- the transcribed F204C block
(programs/fp_arith_f204c.strap: ADD TO MEMORY leaves $L/$R/$SB
unchanged) checked bit-for-bit against jb_af1c p.59, plus its three
constants against the pool p.176. IBM's own STRAP output is the oracle.
"""
import sys
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f204c.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022006.00", "1777777777777777777777", "FPK1"),
    ("022007.00", "1777777777777777777760", "FPK2"),
]

CODE_ROWS = [
    ("012614.40", "12615.04 00", "BD,$+.32"),
    ("012615.00", "22007.00 80 000000.20 50", "L(BU),FPK2"),
    ("012616.00", "22355.00 80 000000.20 D0", "ST(BU),ROS"),
    ("012617.00", "10.22 00", "Z,$L"),
    ("012617.40", "11.22 00", "Z,$R"),
    ("012620.00", "12.22 00", "Z,$SB"),
    ("012620.40", "22355.40 A0", "M+(U),ROS"),
    ("012621.00", "22005.00 80 000040.13 70", "CT0101(BU,64),FPK0,64"),
    ("012622.00", "1310.00 80", "SIC,SEN"),
    ("012622.40", "1304.35 42", "BRGZ,SERS"),
    ("012623.00", "22005.00 80 000000.13 70", "CT0101(BU,64),FPK0"),
    ("012624.00", "1310.00 80", "SIC,SEN"),
    ("012624.40", "1304.35 42", "BRGZ,SERS"),
    ("012625.00", "12.00 80 010000.07 70", "CT0011(BU,8),10.0"),
    ("012626.00", "1310.00 80", "SIC,SEN"),
    ("012626.40", "1304.35 42", "BRGZ,SERS"),
    ("012627.00", "22355.00 80 000000.00 F0", "CM0000(BU),ROS"),
    ("012630.00", "22006.00 80 000040.36 70", "C1111(BU,64),FPK1,64"),
    ("012631.00", "22006.00 80 000000.36 70", "C1111(BU,64),FPK1"),
    ("012632.00", "12.00 80 010000.36 F0", "CM1111(BU,8),10.0"),
    ("012633.00", "22355.40 A0", "M+(U),ROS"),
    ("012633.40", "22006.00 80 000040.25 70", "CT1010(BU,64),FPK1,64"),
    ("012634.40", "1310.00 80", "SIC,SEN"),
    ("012635.00", "1304.35 42", "BRGZ,SERS"),
    ("012635.40", "22006.00 80 000000.25 70", "CT1010(BU,64),FPK1"),
    ("012636.40", "1310.00 80", "SIC,SEN"),
    ("012637.00", "1304.35 42", "BRGZ,SERS"),
    ("012637.40", "12.00 80 010000.31 70", "CT1100(BU,8),10.0"),
    ("012640.40", "1310.00 80", "SIC,SEN"),
    ("012641.00", "1304.35 42", "BRGZ,SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
