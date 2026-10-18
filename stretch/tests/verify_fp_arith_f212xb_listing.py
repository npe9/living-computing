#!/usr/bin/env python3
"""verify_fp_arith_f212xb_listing.py -- F212-X "ADD TO FRACTION
ROUTINE", sub-block F212XB "SIGN AND MODIFIERS"
(../decks/fp_arith_f212xb.strap) against jb_af1c p.123, plus its
constants against the pool p.176.

The two F+ rows are what this block is for, and they differ in exactly
one bit of the printed code:

    F+A%U   22055.65 20    .65 = 110101 -> unnorm 1, absSign 1, invSign 0
    F-A%U   22055.75 20    .75 = 111101 -> unnorm 1, absSign 1, invSign 1

so F-A is F+ with both sign modifiers, the same written-minus shape as
M-A, D-A and D-MGA, and strap_asm's strip_fp_sign gained the rule for
it here (F+A already fell out of the generic "A" suffix, since "F+" is
a real FP op and "F-" is not).

FPK23 is the constant whose pool reading F205B settled as "...250"
rather than the scan's apparent "...230"; this block depends on it
again, and on the same side -- XB1 subtracts 555555555555 from
aaaaaaaaaaaa and expects FPK24, which only the "250" reading gives.

FAF3 is the listing's own label at 016742.00 and the block's exit sits
at 016762.00 where the page has "BD,$+1.0"; both fall out of the
transcription, so the instruction lengths in between are checked.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f212xb.strap").read())

CONST_ROWS = [
    ("022033.00", "0000577777777777777760", "FPK22"),
    ("022034.00", "0000525252525252525250", "FPK23"),
    ("022035.00", "0000452525252525252530", "FPK24"),
    ("022055.00", "0001052525252525252530", "FPK40"),
]

SIC  = "1310.00 80"
BRGZ = "1304.35 42"

CODE_ROWS = [
    # F212XB1 -- MS+ACS+A+1, N+0: A forces the operand positive, so the
    # magnitudes subtract.
    ("016742.00", "22034.44 60",                 "DL(U), FPK23"),
    ("016742.40", "22033.14 80 060012.06 70",    "C0011(BU,48), FPK22+.12, 20"),
    ("016743.40", "22055.65 20",                 "F+A(U), FPK40"),
    ("016744.00", "22035.00 80 074042.15 70",    "CT0110(BU,60), FPK24, 68"),
    ("016745.00", SIC,                           "SIC, SEN"),
    ("016745.40", BRGZ,                          "BRGZ, SERS"),
    ("016746.00", "22033.14 80 060012.15 70",    "CT0110(BU,48), FPK22+.12, 20"),
    ("016747.00", SIC,                           "SIC, SEN"),
    ("016747.40", BRGZ,                          "BRGZ, SERS"),
    ("016750.00", "12.04 80 016752.34 02",       "BB, 10.4, $+2.0"),
    ("016751.00", SIC,                           "SIC, SEN"),
    ("016751.40", "1304.10 00",                  "B, SERS"),

    # F212XB2 -- MS+ACS+N+A+1: A forces positive and N inverts, so the
    # signs agree and the magnitudes add.
    ("016752.00", "22034.44 60",                 "DL(U), FPK23"),
    ("016752.40", "22033.14 80 060012.06 70",    "C0011(BU,48), FPK22+.12, 20"),
    ("016753.40", "22055.75 20",                 "F-A(U), FPK40"),
    ("016754.00", "22033.00 80 074042.15 70",    "CT0110(BU,60), FPK22, 68"),
    ("016755.00", SIC,                           "SIC, SEN"),
    ("016755.40", BRGZ,                          "BRGZ, SERS"),
    ("016756.00", "22033.14 80 060012.15 70",    "CT0110(BU,48), FPK22+.12, 20"),
    ("016757.00", SIC,                           "SIC, SEN"),
    ("016757.40", BRGZ,                          "BRGZ, SERS"),
    ("016760.00", "12.04 80 016762.34 02",       "BB, 10.4, $+2.0"),
    ("016761.00", SIC,                           "SIC, SEN"),
    ("016761.40", "1304.10 00",                  "B, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
