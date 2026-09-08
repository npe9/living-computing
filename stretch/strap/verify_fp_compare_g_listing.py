#!/usr/bin/env python3
"""verify_fp_compare_g_listing.py -- the transcribed F202G11..G18 block
(programs/fp_compare_f202g.strap, the KR Compare-for-Range tests)
checked bit-for-bit against jb_af1c p.45, plus its six constants against
the pools on p.176-178. IBM's own STRAP output is the oracle.
"""
import sys
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_compare_f202g.strap").read())

CONST_ROWS = [
    ("022006.00", "1777777777777777777777", "FPK1"),
    # FPK23: the scan's last group reads as "230" or "250" -- 3 and 5
    # are near-identical in the pool's typewriter font.  It is "250",
    # settled by F205B, whose B20/B22 add FPK4 to the magnitude of
    # FPK23 and expect the all-ones FPK22.  This file asserted "230"
    # until 2026-09-07; G17/G18's KR compares pass either way, which is
    # why the disagreement with verify_fp_arith_f205b_listing.py went
    # unnoticed.
    ("022034.00", "0000525252525252525250", "FPK23"),
    ("022173.00", "1577777777777777777760", "FK25"),
    ("022202.00", "0027125252525252525000", "FK32"),
    ("022204.00", "0200377777777777777770", "FK34"),
    ("022212.00", "1777577777777777777770", "FK40"),
]

CODE_ROWS = [
    # G11 (AH on)
    ("012036.40", "13.76 80 012037.74 0E", "G11 BB1,$AH,$+1"),
    ("012037.40", "22202.40 60", "G11 L(U),FK32"),
    ("012040.00", "22204.41 60", "G11 KR(U),FK34"),
    ("012040.40", "1310.00 80", "G11 SIC,SEN"),
    ("012041.00", "1304.37 40", "G11 BZAH,SERS"),
    # G12 (AH off)
    ("012041.40", "22202.40 60", "G12 L(U),FK32"),
    ("012042.00", "13.22 00", "G12 Z,$IND"),
    ("012042.40", "22204.41 60", "G12 KR(U),FK34"),
    ("012043.00", "1310.00 80", "G12 SIC,SEN"),
    ("012043.40", "1304.37 42", "G12 BAH,SERS"),
    # G13 (AH on)
    ("012044.00", "13.76 80 012045.34 0E", "G13 BB1,$AH,$+1"),
    ("012045.00", "22006.40 60", "G13 L(U),FPK1"),
    ("012045.40", "22006.41 60", "G13 KR(U),FPK1"),
    ("012046.00", "1310.00 80", "G13 SIC,SEN"),
    ("012046.40", "1304.37 40", "G13 BZAH,SERS"),
    # G14 (AH off)
    ("012047.00", "22006.40 60", "G14 L(U),FPK1"),
    ("012047.40", "13.22 00", "G14 Z,$IND"),
    ("012050.00", "22006.41 60", "G14 KR(U),FPK1"),
    ("012050.40", "1310.00 80", "G14 SIC,SEN"),
    ("012051.00", "1304.36 C2", "G14 BAE,SERS"),
    # G15 (AH on)
    ("012051.40", "13.76 80 012052.74 0E", "G15 BB1,$AH,$+1"),
    ("012052.40", "22212.40 60", "G15 L(U),FK40"),
    ("012053.00", "22173.41 60", "G15 KR(U),FK25"),
    ("012053.40", "1310.00 80", "G15 SIC,SEN"),
    ("012054.00", "1304.36 C0", "G15 BZAE,SERS"),
    # G16 (AH off)
    ("012054.40", "22212.40 60", "G16 L(U),FK40"),
    ("012055.00", "13.22 00", "G16 Z,$IND"),
    ("012055.40", "22173.41 60", "G16 KR(U),FK25"),
    ("012056.00", "1310.00 80", "G16 SIC,SEN"),
    ("012056.40", "1304.36 42", "G16 BAL,SERS"),
    # G17 (AH on)
    ("012057.00", "13.76 80 012060.34 0E", "G17 BB1,$AH,$+1"),
    ("012060.00", "22204.40 60", "G17 L(U),FK34"),
    ("012060.40", "22034.41 60", "G17 KR(U),FPK23"),
    ("012061.00", "1310.00 80", "G17 SIC,SEN"),
    ("012061.40", "1304.37 40", "G17 BZAH,SERS"),
    # G18 (AH off)
    ("012062.00", "22204.40 60", "G18 L(U),FK34"),
    ("012062.40", "13.22 00", "G18 Z,$IND"),
    ("012063.00", "22034.41 60", "G18 KR(U),FPK23"),
    ("012063.40", "1310.00 80", "G18 SIC,SEN"),
    ("012064.00", "1304.36 C2", "G18 BAE,SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
