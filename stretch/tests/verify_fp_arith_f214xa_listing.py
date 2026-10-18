#!/usr/bin/env python3
"""verify_fp_arith_f214xa_listing.py -- F214-X "MULTIPLY DOUBLE TEST",
sub-block F214XA "ARITHMETIC CHECKS"
(../decks/fp_arith_f214xa.strap) against jb_af1c p.142.

This is the block that introduces D* (opcode 1011010) to the model:
Ref. Manual p.97, "the same as MULTIPLY, except that the 96-bit
product fraction is placed in accumulator bits 12-107".  Every
sub-test checks the result in three pieces -- exponent at offset 116,
high fraction at 68 (IBM 12-59), LOW fraction at 20 (IBM 60-107) --
where F214A, the MULTIPLY block, could only check the first two.

XA2 is what separates D* from *: its product's high half is zero and
the whole answer sits in the low half, which MULTIPLY never writes.

D*(U) prints as "<addr>.45 A0" where *(U) prints "<addr>.41 A0"; the
two opcodes differ in one bit and it lands in that octal digit.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f214xa.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022071.00", "0001024713560247135620", "FPK52"),
    ("022072.00", "0000400000000000000040", "FPK53"),
    ("022073.00", "0001451627340516273440", "FPK54"),
    ("022205.00", "1777400000000000000000", "FK35"),
    ("022206.00", "1000177777777777777760", "FK36"),
    ("022235.00", "1000024713560247135620", "FK59"),
    ("022237.00", "1000224713560247135620", "FK61"),
    ("022243.00", "1577600000000000000060", "FK65"),
    ("022310.00", "0001476543120765431260", "FK103"),
]

SIC  = "1310.00 80"
BRGZ = "1304.35 42"

CODE_ROWS = [
    # XA1 -- exponents in XFP rng; Fig.32 ties to the accumulator and
    # FK35's zero fraction makes the whole 96-bit product zero.
    ("020113.00", "22206.40 60",              "XA1 L(U), FK36              exp acc + +1024"),
    ("020113.40", "22205.45 A0",              "XA1 D*(U), FK35             exp.mem++2047"),
    ("020114.00", "22235.00 80 014072.15 70", "XA1 CT0110(BU,12), FK59, 116   test result exp++1024"),
    ("020115.00", SIC, "XA1 SIC"), ("020115.40", BRGZ, "XA1 BRGZ"),
    ("020116.00", "22205.14 80 060042.15 70", "XA1 CT0110(BU,48), FK35+.12, 68  check result fract+0"),
    ("020117.00", SIC, "XA1 SIC"), ("020117.40", BRGZ, "XA1 BRGZ"),
    ("020120.00", "22205.14 80 060012.15 70", "XA1 CT0110(BU,48), FK35+.12, 20"),
    ("020121.00", SIC, "XA1 SIC"), ("020121.40", BRGZ, "XA1 BRGZ"),

    # XA2 -- exponents in N rng; the one that pins D* apart from *.
    ("020122.00", "22071.40 60",              "XA2 L(U), FPK52             exp.acc++2"),
    ("020122.40", "22072.45 A0",              "XA2 D*(U), FPK53            exp.mem++1"),
    ("020123.00", "22073.00 80 014072.15 70", "XA2 CT0110(BU,12), FPK54, 116  check result exp++3"),
    ("020124.00", SIC, "XA2 SIC"), ("020124.40", BRGZ, "XA2 BRGZ"),
    ("020125.00", "22005.14 80 060042.15 70", "XA2 CT0110(BU,48), FPK0+.12, 68   check high order fract"),
    ("020126.00", SIC, "XA2 SIC"), ("020126.40", BRGZ, "XA2 BRGZ"),
    ("020127.00", "22073.14 80 060012.15 70", "XA2 CT0110(BU,48), FPK54+.12, 20  check low order fract"),
    ("020130.00", SIC, "XA2 SIC"), ("020130.40", BRGZ, "XA2 BRGZ"),

    # XA3 -- exponents in XFN rng; Fig.32 ties to the accumulator.
    ("020131.00", "22237.40 60",              "XA3 L(U), FK61              exp.acc.+-1024"),
    ("020131.40", "22243.45 A0",              "XA3 D*(U), FK65             exp.mem+-1791"),
    ("020132.00", "22237.00 80 014072.15 70", "XA3 CT0110(BU,12), FK61, 116   check result exp+-1024"),
    ("020133.00", SIC, "XA3 SIC"), ("020133.40", BRGZ, "XA3 BRGZ"),
    ("020134.00", "22005.14 80 060042.15 70", "XA3 CT0110(BU,48), FPK0+.12, 68   check high order fract"),
    ("020135.00", SIC, "XA3 SIC"), ("020135.40", BRGZ, "XA3 BRGZ"),
    ("020136.00", "22310.14 80 060012.15 70", "XA3 CT0110(BU,48), FK103+.12, 20  chk low order fract"),
    ("020137.00", SIC, "XA3 SIC"), ("020137.40", BRGZ, "XA3 BRGZ"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
