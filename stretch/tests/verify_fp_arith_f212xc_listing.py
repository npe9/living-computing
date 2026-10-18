#!/usr/bin/env python3
"""verify_fp_arith_f212xc_listing.py -- F212-X "ADD TO FRACTION
ROUTINE", sub-block F212XC "TEST UNCHANGED REGS"
(../decks/fp_arith_f212xc.strap) against jb_af1c pp.123-124, plus its
constants against the pool p.176.  This completes F212-X.

The block addresses the accumulator through the system symbols rather
than through data words, and the printed code confirms the assignment
opcodes.py carries: $L is word 8, $R word 9, $SB word 10, printed in
OCTAL as 10, 11 and 12 respectively -- which is also why XB's source
"BB,10.4" prints as "12.04".

FAF4 is the listing's own label at 016764.00 and the block's exit sits
at 017005.40 where the page has "BD,$+1.0"; both fall out of the
transcription, so the instruction lengths in between are checked --
including the one printed address the page gets wrong (see the
program's transcription note on the SIC at 017000.40).
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f212xc.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022006.00", "1777777777777777777777", "FPK1"),
    ("022032.00", "0031177777777777777767", "FPK21"),
    ("022052.00", "0031125252525252525240", "FPK37"),
]

SIC  = "1310.00 80"
BRGZ = "1304.35 42"

CODE_ROWS = [
    # F212XC1 -- everything zeroed, then an F+ whose operand carries
    # memory flags 7.
    ("016764.00", "10.22 00",                   "Z, $L"),
    ("016764.40", "11.22 00",                   "Z, $R"),
    ("016765.00", "12.22 00",                   "Z, $SB"),
    ("016765.40", "22032.45 20",                "F+(U), FPK21"),
    ("016766.00", "22005.00 80 024000.13 70",   "CT0101(BU,20), FPK0"),
    ("016767.00", SIC,                          "SIC, SEN"),
    ("016767.40", BRGZ,                         "BRGZ, SERS"),
    ("016770.00", "12.00 80 004000.07 70",      "CT0011(BU,4), $SB"),
    ("016771.00", SIC,                          "SIC, SEN"),
    ("016771.40", BRGZ,                         "BRGZ, SERS"),
    ("016772.00", "12.05 80 003000.07 70",      "CT0011(BU,3), $SB+.5"),
    ("016773.00", SIC,                          "SIC, SEN"),
    ("016773.40", BRGZ,                         "BRGZ, SERS"),

    # F212XC2 -- everything set to ones (which makes the accumulator
    # XFN, so this F+ performs no addition), then the same checks.
    ("016774.00", "22006.00 80 000040.36 70",   "C1111(BU,64), FPK1, 64"),
    ("016775.00", "22006.00 80 000000.36 70",   "C1111(BU,64), FPK1"),
    ("016776.00", "12.00 80 010000.36 F0",      "CM1111(BU,8), $SB"),
    ("016777.00", "22052.45 20",                "F+(U), FPK37"),
    ("016777.40", "22006.00 80 024000.25 70",   "CT1010(BU,20), FPK1"),
    ("017000.40", SIC,                          "SIC, SEN"),
    ("017001.00", BRGZ,                         "BRGZ, SERS"),
    ("017001.40", "12.00 80 004000.31 70",      "CT1100(BU,4), $SB"),
    ("017002.40", SIC,                          "SIC, SEN"),
    ("017003.00", BRGZ,                         "BRGZ, SERS"),
    ("017003.40", "12.05 80 003000.31 70",      "CT1100(BU,3), $SB+.5"),
    ("017004.40", SIC,                          "SIC, SEN"),
    ("017005.00", BRGZ,                         "BRGZ, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
