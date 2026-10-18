#!/usr/bin/env python3
"""verify_fp_arith_f214c_listing.py -- F214 "MULTIPLY TEST ROUTINE",
sub-block F214C "TESTS OF UNCHANGED REGISTERS"
(../decks/fp_arith_f214c.strap) against jb_af1c pp.138-139.

C2 is the block that settles what F214A could not: it fills the sign
byte, the left word and the right word with ones, multiplies by zero,
and demands "TEST R +1 S" -- the whole right word still ones.  A
multiply writing a 96-bit product into IBM 12-107 would zero IBM
64-107 and fail, so MULTIPLY LEAVES IBM 64-127 ALONE.

C2's first check has its two listing columns disagree: the source
column reads FPK1 while the printed code is 22005, which is FPK0.
Reproduced here from the PRINTED CODE.  CT1010's truth table
(1,0,1,0 over (memory,accumulator)) does not depend on the memory
operand at all, so the disagreement cannot change the test -- and the
row immediately after it prints 22006 and does read FPK1, which is the
only reason the discrepancy is visible.

F214C is the listing's own label at 017731.00 and the exit sits at
017760.40 where the page has "B,$+1.".
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f214c.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022006.00", "1777777777777777777777", "FPK1"),
    ("022075.00", "0002024713560247135627", "FPK56"),
]

SIC  = "1310.00 80"
BRGZ = "1304.35 42"

CODE_ROWS = [
    # C1 -- clear everything, multiply, require zeros to survive.
    ("017731.00", "12.00 80 010000.00 F0",    "C1 CM0000(BU,8), $SB"),
    ("017732.00", "22005.00 80 000040.00 70", "C1 C0000(BU,64), FPK0, 64"),
    ("017733.00", "22005.00 80 000000.00 70", "C1 C0000(BU,64), FPK0"),
    ("017734.00", "22075.41 A0",              "C1 *(U), FPK56"),
    ("017734.40", "22005.00 80 004040.13 70", "C1 CT0101(BU,4), FPK0, 64   test L60-63 +0"),
    ("017735.40", SIC, "C1 SIC"), ("017736.00", BRGZ, "C1 BRGZ"),
    ("017736.40", "22005.00 80 000000.13 70", "C1 CT0101(BU,64), FPK0      test R +0"),
    ("017737.40", SIC, "C1 SIC"), ("017740.00", BRGZ, "C1 BRGZ"),
    ("017740.40", "12.00 80 004000.07 70",    "C1 CT0011(BU,4), $SB        test SB0-3 +0"),
    ("017741.40", SIC, "C1 SIC"), ("017742.00", BRGZ, "C1 BRGZ"),
    ("017742.40", "12.05 80 003000.07 70",    "C1 CT0011(BU,3), $SB+.5     test SB5-7 +0"),
    ("017743.40", SIC, "C1 SIC"), ("017744.00", BRGZ, "C1 BRGZ"),

    # C2 -- fill everything with ones, multiply by zero, require the
    # ones to survive.  The R check is the load-bearing one.
    ("017744.40", "17745.10 00",              "C2 B, $+.32"),
    ("017745.00", "22006.00 80 000000.20 50", "C2 L(BU), FPK1"),
    ("017746.00", "12.00 80 010000.36 F0",    "C2 CM1111(BU,8), $SB"),
    ("017747.00", "22006.00 80 000040.36 70", "C2 C1111(BU,64), FPK1, 64"),
    ("017750.00", "22005.41 A0",              "C2 *(U), FPK0"),
    ("017750.40", "22005.00 80 004040.25 70", "C2 CT1010(BU,4), FPK0, 64   test L60-63 +1 s"),
    ("017751.40", SIC, "C2 SIC"), ("017752.00", BRGZ, "C2 BRGZ"),
    ("017752.40", "22006.00 80 000000.25 70", "C2 CT1010(BU,64), FPK1      test R +1 s"),
    ("017753.40", SIC, "C2 SIC"), ("017754.00", BRGZ, "C2 BRGZ"),
    ("017754.40", "12.00 80 004000.31 70",    "C2 CT1100(BU,4), $SB        test SB0-3 +1 s"),
    ("017755.40", SIC, "C2 SIC"), ("017756.00", BRGZ, "C2 BRGZ"),
    ("017756.40", "12.05 80 003000.31 70",    "C2 CT1100(BU,3), $SB+.5     test SB5-7 +1 s"),
    ("017757.40", SIC, "C2 SIC"), ("017760.00", BRGZ, "C2 BRGZ"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
