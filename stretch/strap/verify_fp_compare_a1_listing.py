#!/usr/bin/env python3
"""verify_fp_compare_a1_listing.py -- the transcribed F202A1..A6 block
(programs/fp_compare_f202a1.strap) checked bit-for-bit against jb_af1c
p.30, plus its four constants against the pool on p.176. IBM's own
STRAP output is the oracle. Same regular nine-half-word sub-test shape
as verify_fp_compare_listing.py.
"""
import sys
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_compare_f202a1.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022010.00", "0000125252525252525240", "FPK3"),
    ("022016.00", "0000125252525252525000", "FPK9"),
    ("022032.00", "0031177777777777777767", "FPK21"),
]

SIC = "1310.00 80"
BZAE = "1304.36 C0"; BZAH = "1304.37 40"; BZAL = "1304.36 40"
BAL = "1304.36 42";  BAE = "1304.36 C2";  BAH = "1304.37 42"
L0 = "22005.40 60"; L3 = "22010.40 60"; L9 = "22016.40 60"

def octinc(loc, halves):
    w, b = loc.split(".")
    total = int(w, 8) * 2 + (1 if b == "40" else 0) + halves
    return f"{total // 2:06o}.{'40' if total % 2 else '00'}"

def subtest(start, load_mc, cmp_mc, br1, br2, br3, name):
    mcs = [load_mc, "13.22 00", cmp_mc, SIC, br1, SIC, br2, SIC, br3]
    return [(octinc(start, i), mc, f"{name}[{i}]")
            for i, mc in enumerate(mcs)]

CODE_ROWS = (
    subtest("011301.00", L0, "22005.41 20", BZAE, BAL, BAH, "A1/FPK0=") +
    subtest("011305.40", L3, "22005.41 20", BZAH, BAL, BAE, "A2/FPK0")  +
    subtest("011312.00", L0, "22010.41 20", BZAL, BAE, BAH, "A3/FPK3")  +
    subtest("011316.40", L3, "22016.41 20", BZAH, BAL, BAE, "A4/FPK9")  +
    subtest("011323.00", L9, "22010.41 20", BZAL, BAE, BAH, "A5/FPK3")  +
    subtest("011327.40", L3, "22032.41 20", BZAL, BAE, BAH, "A6/FPK21")
)

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
