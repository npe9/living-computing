#!/usr/bin/env python3
"""verify_fp_compare_listing.py -- the transcribed F202A15..A20 block
(../decks/fp_compare_f202a.strap) checked bit-for-bit against the
machine code printed in jb_af1c p.33, plus the seven FP constants it
uses against the pools on p.176-178. IBM's own STRAP output is the
oracle.

Each sub-test is nine half-words with a regular shape:
    L(U),<opnd>   Z,$IND   K(U),<cmp>   SIC,SEN B?,SERS   (x3 SIC/branch)
so the rows are generated from a compact per-sub-test spec (start
location, the load and compare machine words, and the three branch
words) rather than hand-listed 54 times.
"""
import sys
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_compare_f202a.strap").read())

# Constants (pools, p.176-178), each the 22-octal-digit machine word.
CONST_ROWS = [
    ("022006.00", "1777777777777777777777", "FPK1"),
    ("022007.00", "1777777777777777777760", "FPK2"),
    ("022032.00", "0031177777777777777767", "FPK21"),
    ("022037.00", "1777577777777777777760", "FPK26"),
    ("022040.00", "1777677777777777777760", "FPK27"),
    ("022204.00", "0200377777777777777770", "FK34"),
    ("022212.00", "1777577777777777777770", "FK40"),
]

SIC = "1310.00 80"

def octinc(loc, halves):
    """Advance an 'wwwwww.bb' octal location by `halves` half-words."""
    w, b = loc.split(".")
    total = int(w, 8) * 2 + (1 if b == "40" else 0) + halves
    return f"{total // 2:06o}.{'40' if total % 2 else '00'}"

def subtest(start, load_mc, cmp_mc, br1, br2, br3, name):
    """Nine rows: load, Z,$IND, compare, then three SIC + branch pairs."""
    mcs = [load_mc, "13.22 00", cmp_mc, SIC, br1, SIC, br2, SIC, br3]
    labels = [f"{name} L(U)", "Z,$IND", "K(U)", "SIC,SEN", "b1",
              "SIC,SEN", "b2", "SIC,SEN", "b3"]
    return [(octinc(start, i), mc, f"{name}:{lab}")
            for i, (mc, lab) in enumerate(zip(mcs, labels))]

L21 = "22032.40 60"   # L(U),FPK21
L2  = "22007.40 60"   # L(U),FPK2
BZAH = "1304.37 40"; BZAL = "1304.36 40"
BAL = "1304.36 42";  BAE = "1304.36 C2"; BAH = "1304.37 42"

CODE_ROWS = (
    subtest("011400.00", L21, "22040.41 20", BZAH, BAL, BAE, "A15/FPK27") +
    subtest("011404.40", L21, "22006.41 20", BZAH, BAL, BAE, "A16/FPK1")  +
    subtest("011411.00", L21, "22204.41 20", BZAH, BAL, BAE, "A17/FK34")  +
    subtest("011415.40", L21, "22212.41 20", BZAH, BAL, BAE, "A18/FK40")  +
    subtest("011422.00", L2,  "22037.41 20", BZAL, BAE, BAH, "A19/FPK26") +
    subtest("011426.40", L2,  "22032.41 20", BZAL, BAE, BAH, "A20/FPK21")
)

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
