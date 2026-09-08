#!/usr/bin/env python3
"""verify_fp_arith_f213c_listing.py -- F213 "ADD TO EXPONENT TEST",
sub-block F213C "TEST UNCHANGED REGISTERS"
(programs/fp_arith_f213c.strap) against jb_af1c p.129.  This completes
F213.

The sign byte is checked in ONE eight-bit connective here, where
F212XC needed two (0-3 and 5-7): E+ never writes the sign, so bit 4
does not have to be excluded.  That difference is visible in the
printed code -- "12.00 80 010000.07 70" for CT0011(BU,8) against
F212XC's "12.00 80 004000.07 70" for CT0011(BU,4).

FAE4 is the listing's own label at 017245.00 and the exit sits at
017263.00 where the page has "BD,$+1.0".
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f213c.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022006.00", "1777777777777777777777", "FPK1"),
]

SIC  = "1310.00 80"
BRGZ = "1304.35 42"

CODE_ROWS = [
    # F213C1 -- everything zeroed; FPK1 is XFN, so Fig.32 gives the
    # memory exponent, and the low 20 bits and sign byte must survive.
    ("017245.00", "10.22 00",                     "Z, $L"),
    ("017245.40", "11.22 00",                     "Z, $R"),
    ("017246.00", "12.22 00",                     "Z, $SB"),
    ("017246.40", "22006.45 60",                  "E+(U), FPK1"),
    ("017247.00", "22005.00 80 024000.13 70",     "CT0101(BU,20), FPK0"),
    ("017250.00", SIC, "SIC, SEN"), ("017250.40", BRGZ, "BRGZ, SERS"),
    ("017251.00", "12.00 80 010000.07 70",        "CT0011(BU,8), $SB"),
    ("017252.00", SIC, "SIC, SEN"), ("017252.40", BRGZ, "BRGZ, SERS"),

    # F213C2 -- everything ones, which makes the ACCUMULATOR XFN; FPK0
    # is N, so this time the accumulator's exponent survives.
    ("017253.00", "17253.50 00",                  "B, $+.32"),
    ("017253.40", "22006.00 80 000040.36 70",     "C1111(BU,64), FPK1, 64"),
    ("017254.40", "22006.00 80 000000.36 70",     "C1111(BU,64), FPK1"),
    ("017255.40", "12.00 80 010000.36 F0",        "CM1111(BU,8), $SB"),
    ("017256.40", "22005.45 60",                  "E+(U), FPK0"),
    ("017257.00", "22006.00 80 024000.25 70",     "CT1010(BU,20), FPK1"),
    ("017260.00", SIC, "SIC, SEN"), ("017260.40", BRGZ, "BRGZ, SERS"),
    ("017261.00", "12.00 80 010000.31 70",        "CT1100(BU,8), $SB"),
    ("017262.00", SIC, "SIC, SEN"), ("017262.40", BRGZ, "BRGZ, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
