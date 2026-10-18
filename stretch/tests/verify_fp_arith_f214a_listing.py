#!/usr/bin/env python3
"""verify_fp_arith_f214a_listing.py -- F214 "MULTIPLY TEST ROUTINE",
sub-block F214A "ARITHMETIC CHECKS" (../decks/fp_arith_f214a.strap)
against jb_af1c p.137, plus its constants against the pools
pp.176-179.

Multiply prints ".41 A0" unnormalized and ".01 A0" normalized: 100001
and 000001 for bits 18-23, so unnorm, no sign modifiers, code[0:2] 001,
and 0xA0 giving code[3:6] 1010 -- code 0011010, `*`.  L alongside it is
".40 60", code 0000110.

The constants are the substance of this block, and FK60 is the one
that had to be settled by arithmetic rather than by reading: the pool
row is overwritten by handwritten annotations, and the two candidate
readings differ in whether the fraction is zero.  A2's title ("NON
ZERO MULTIPLICAND FRACT."), the exponent, and the product itself all
pick 1000300000000000000000 -- FK59.frac x FK60.frac keeping the top
48 bits is 14e5dc14e5dc, exactly the fraction of FK15, the constant A2
compares against.

SAP17 is the listing's own label at 017634.40 and the exit sits at
017671.40 where the page has "B,$+1."; both fall out of the
transcription.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f214a.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022071.00", "0001024713560247135620", "FPK52"),
    ("022121.00", "0001100000000000000000", "FPK80"),
    ("022161.00", "0002012345670123456700", "FK15"),
    ("022205.00", "1777400000000000000000", "FK35"),
    ("022235.00", "1000024713560247135620", "FK59"),
    ("022236.00", "1000300000000000000000", "FK60"),
    ("022237.00", "1000224713560247135620", "FK61"),
    ("022240.00", "0777424713560247135620", "FK62"),
    ("022241.00", "0777500000000000000000", "FK63"),
    ("022307.00", "1775523456701234567100", "FK102"),
]

SIC  = "1310.00 80"
BRGZ = "1304.35 42"
E12  = "80 014072.15 70"      # CT0110(BU,12), k, 116
F48  = "80 060042.15 70"      # CT0110(BU,48), k+.12, 68
B60  = "80 074042.15 70"      # CT0110(BU,60), k, 68

CODE_ROWS = [
    # A1 -- XFP * XFP, zero multiplicand fraction.
    ("017634.40", "17635.10 00",       "A1 B, $+.32"),
    ("017635.00", "22235.40 60",       "A1 L(U), FK59"),
    ("017635.40", "22205.41 A0",       "A1 *(U), FK35"),
    ("017636.00", "22235.00 " + E12,   "A1 CT0110(BU,12), FK59, 116"),
    ("017637.00", SIC, "A1 SIC"), ("017637.40", BRGZ, "A1 BRGZ"),
    ("017640.00", "22005.14 " + F48,   "A1 CT0110(BU,48), FPK0+.12, 68"),
    ("017641.00", SIC, "A1 SIC"), ("017641.40", BRGZ, "A1 BRGZ"),

    # A2 -- XFP * XFN, non-zero multiplicand fraction.
    ("017642.00", "17642.50 00",       "A2 B, $+.32"),
    ("017642.40", "22235.40 60",       "A2 L(U), FK59"),
    ("017643.00", "22236.41 A0",       "A2 *(U), FK60"),
    ("017643.40", "22235.00 " + E12,   "A2 CT0110(BU,12), FK59, 116"),
    ("017644.40", SIC, "A2 SIC"), ("017645.00", BRGZ, "A2 BRGZ"),
    ("017645.40", "22161.14 " + F48,   "A2 CT0110(BU,48), FK15+.12, 68"),
    ("017646.40", SIC, "A2 SIC"), ("017647.00", BRGZ, "A2 BRGZ"),

    # A3 -- XFN * N.
    ("017647.40", "17650.10 00",       "A3 B, $+.32"),
    ("017650.00", "22237.40 60",       "A3 L(U), FK61"),
    ("017650.40", "22121.41 A0",       "A3 *(U), FPK80"),
    ("017651.00", "22237.00 " + E12,   "A3 CT0110(BU,12), FK61, 116"),
    ("017652.00", SIC, "A3 SIC"), ("017652.40", BRGZ, "A3 BRGZ"),
    ("017653.00", "22161.14 " + F48,   "A3 CT0110(BU,48), FK15+.12, 68"),
    ("017654.00", SIC, "A3 SIC"), ("017654.40", BRGZ, "A3 BRGZ"),

    # A4 -- N * N, the exponents add.
    ("017655.00", "17655.50 00",       "A4 B, $+.32"),
    ("017655.40", "22071.40 60",       "A4 L(U), FPK52"),
    ("017656.00", "22121.41 A0",       "A4 *(U), FPK80"),
    ("017656.40", "22161.00 " + B60,   "A4 CT0110(BU,60), FK15, 68"),
    ("017657.40", SIC, "A4 SIC"), ("017660.00", BRGZ, "A4 BRGZ"),

    # A5 -- normalization occurs.
    ("017660.40", "17661.10 00",       "A5 B, $+.32"),
    ("017661.00", "22240.40 60",       "A5 L(U), FK62"),
    ("017661.40", "22241.01 A0",       "A5 *(N), FK63"),
    ("017662.00", "22307.00 " + B60,   "A5 CT0110(BU,60), FK102, 68"),
    ("017663.00", SIC, "A5 SIC"), ("017663.40", BRGZ, "A5 BRGZ"),

    # A6 -- a flagged operand suppresses normalization.
    ("017664.00", "17664.50 00",       "A6 B, $+.32"),
    ("017664.40", "22235.40 60",       "A6 L(U), FK59"),
    ("017665.00", "22236.01 A0",       "A6 *(N), FK60"),
    ("017665.40", "22235.00 " + E12,   "A6 CT0110(BU,12), FK59, 116"),
    ("017666.40", SIC, "A6 SIC"), ("017667.00", BRGZ, "A6 BRGZ"),
    ("017667.40", "22161.14 " + F48,   "A6 CT0110(BU,48), FK15+.12, 68"),
    ("017670.40", SIC, "A6 SIC"), ("017671.00", BRGZ, "A6 BRGZ"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
