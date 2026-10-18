#!/usr/bin/env python3
"""verify_fp_arith_f213a10_13_listing.py -- F213 "ADD TO EXPONENT
TEST", sub-block F213A "NORMALIZATION MODIFIER" sub-tests A10-A13
(../decks/fp_arith_f213a10_13.strap) against jb_af1c pp.126-127, plus
its constants against the pools pp.176-178.  This completes F213.

These are the only NORMALIZED E+ rows in the diagnostic and the
printed code is what says so: ".05 60" here against ".45 60" in
A1-A9, differing in the unnorm bit alone (000101 vs 100101).  In both
groups the absSign and invSign bits are zero, which is the evidence
for the coverage note in the program header -- nothing in F213 tests
the sign modifiers on E+ at all.

FAE2 stands in for the listing's own flow into 017127.00; the block's
exit sits at 017161.00 where the page has "BD,$+1.0", and it falls out
of the transcription rather than being placed.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f213a10_13.strap").read())

CONST_ROWS = [
    ("022045.00", "0001177777777777777760", "FPK32"),
    ("022125.00", "0001000077777777777760", "FPK87"),
    ("022126.00", "0001000177777777777740", "FPK88"),
    ("022137.00", "0001177777777777740000", "FPK97"),
    ("022167.00", "1777403777777777777760", "FK21"),
    ("022210.00", "0777572525252525252520", "FK38"),
    ("022211.00", "0777625252525252525240", "FK39"),
    ("022220.00", "1746577777777777777760", "FK46"),
    ("022221.00", "0031000017777777777760", "FK47"),
    ("022222.00", "0030177777777777600000", "FK48"),
    ("022232.00", "1777225252525252525240", "FK56"),
    ("022233.00", "1022577777777777777760", "FK57"),
    ("022234.00", "0003377777777777777760", "FK58"),
]

SIC  = "1310.00 80"
BRGZ = "1304.35 42"
HI60 = "80 074042.15 70"    # CT0110(BU,60), <k>, 68  -- IBM 0-59
LO   = "80 060012.15 70"    # CT0110(BU,48), <k>+.12, 20
IN   = "80 060012.06 70"    # C0011(BU,48),  <k>+.12, 20

CODE_ROWS = [
    # F213A10 -- flagged operand, normalization suppressed.
    ("017127.00", "17127.50 00",        "B, $+.32"),
    ("017127.40", "22167.44 60",        "DL(U), FK21"),
    ("017130.00", "22167.14 " + IN,     "C0011(BU,48), FK21+.12, 20"),
    ("017131.00", "22211.05 60",        "E+(N), FK39"),
    ("017131.40", "22167.00 " + HI60,   "CT0110(BU,60), FK21, 68"),
    ("017132.40", SIC, "SIC, SEN"), ("017133.00", BRGZ, "BRGZ, SERS"),
    ("017133.40", "22167.14 " + LO,     "CT0110(BU,48), FK21+.12, 20"),
    ("017134.40", SIC, "SIC, SEN"), ("017135.00", BRGZ, "BRGZ, SERS"),

    # F213A11 -- generated EF with ES 1, normalization suppressed.
    ("017135.40", "17136.10 00",        "B, $+.32"),
    ("017136.00", "22211.44 60",        "DL(U), FK39"),
    ("017136.40", "22211.14 " + IN,     "C0011(BU,48), FK39+.12, 20"),
    ("017137.40", "22211.05 60",        "E+(N), FK39"),
    ("017140.00", "22232.00 " + HI60,   "CT0110(BU,60), FK56, 68"),
    ("017141.00", SIC, "SIC, SEN"), ("017141.40", BRGZ, "BRGZ, SERS"),
    ("017142.00", "22232.14 " + LO,     "CT0110(BU,48), FK56+.12, 20"),
    ("017143.00", SIC, "SIC, SEN"), ("017143.40", BRGZ, "BRGZ, SERS"),

    # F213A12 -- generated EF with ES 0, normalization occurs; the
    # 96-bit shift of 12 that pulls FK46's low half up into FK48's.
    ("017144.00", "17144.50 00",        "B, $+.32"),
    ("017144.40", "22221.44 60",        "DL(U), FK47"),
    ("017145.00", "22220.14 " + IN,     "C0011(BU,48), FK46+.12, 20"),
    ("017146.00", "22210.05 60",        "E+(N), FK38"),
    ("017146.40", "22233.00 " + HI60,   "CT0110(BU,60), FK57, 68"),
    ("017147.40", SIC, "SIC, SEN"), ("017150.00", BRGZ, "BRGZ, SERS"),
    ("017150.40", "22222.14 " + LO,     "CT0110(BU,48), FK48+.12, 20"),
    ("017151.40", SIC, "SIC, SEN"), ("017152.00", BRGZ, "BRGZ, SERS"),

    # F213A13 -- no EF, normalization occurs; a 96-bit shift of 10.
    ("017152.40", "17153.10 00",        "B, $+.32"),
    ("017153.00", "22125.44 60",        "DL(U), FPK87"),
    ("017153.40", "22045.14 " + IN,     "C0011(BU,48), FPK32+.12, 20"),
    ("017154.40", "22126.05 60",        "E+(N), FPK88"),
    ("017155.00", "22234.00 " + HI60,   "CT0110(BU,60), FK58, 68"),
    ("017156.00", SIC, "SIC, SEN"), ("017156.40", BRGZ, "BRGZ, SERS"),
    ("017157.00", "22137.14 " + LO,     "CT0110(BU,48), FPK97+.12, 20"),
    ("017160.00", SIC, "SIC, SEN"), ("017160.40", BRGZ, "BRGZ, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
