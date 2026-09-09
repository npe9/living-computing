#!/usr/bin/env python3
"""verify_fp_arith_f216a_listing.py -- F216 "MULTIPLY AND ADD TEST",
sub-block F216A "ARITHMETIC CHECKS" (programs/fp_arith_f216a.strap)
against jb_af1c pp.147-148.

The block that adds *+ (opcode 0111010), the only operation that reads
the factor register -- which is why F215 had to come first.  In the
model it is fpMulDouble feeding fpAddDouble, per p.98's own
description.

Each sub-test builds a 96-bit accumulator with DL(U) plus a
C0011(BU,48) of FPK27's fraction into IBM 60-107, loads FT, and
multiplies-and-adds.  A1-A3 are range-table cases where the
accumulator survives; A4 and A5 are ones where the product wins; A6 is
the only unflagged sub-test and so the only real 96-bit addition
(eb1a23eb1a23 7fffffffffff + 14e5dc14e5dc 800000000000 = all ones,
no carry).

*+(U) prints as "<addr>.43 A0".

TRANSCRIPTION NOTE: A5's exponent check is commented "+1026" in the
scan but compares against FK36, whose exponent field is +1024 -- and
p.99 gives the product the XFP operand's exponent, FK59's +1024, not
the sum.  F214XA1 uses FK36 as +1024 independently.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f216a.strap").read())

CONST_ROWS = [
    ("022040.00", "1777677777777777777760", "FPK27"),
    ("022045.00", "0001177777777777777760", "FPK32"),
    ("022071.00", "0001024713560247135620", "FPK52"),
    ("022121.00", "0001100000000000000000", "FPK80"),
    ("022162.00", "0001412345670123456700", "FK16"),
    ("022164.00", "0002165432107654321060", "FK18"),
    ("022206.00", "1000177777777777777760", "FK36"),
    ("022235.00", "1000024713560247135620", "FK59"),
    ("022236.00", "1000300000000000000000", "FK60"),
    ("022237.00", "1000224713560247135620", "FK61"),
    ("022245.00", "1577500000000000000000", "FK67"),
    ("022246.00", "1777565432107654321060", "FK68"),
    ("022247.00", "1777765432107654321060", "FK69"),
]

SIC   = "1310.00 80"
BRGZ  = "1304.35 42"
SETLO = "22040.14 80 060012.06 70"    # C0011(BU,48), FPK27+.12, 20
CKLO  = "22040.14 80 060012.15 70"    # CT0110(BU,48), FPK27+.12, 20
CK16  = "22162.14 80 060042.15 70"    # CT0110(BU,48), FK16+.12, 68
CK67  = "22245.14 80 060012.15 70"    # CT0110(BU,48), FK67+.12, 20

CODE_ROWS = [
    # A1
    ("020312.00", "22246.44 60",              "A1 DL(U), FK68        exp++2047"),
    ("020312.40", SETLO,                      "A1 C0011(BU,48), FPK27+.12, 20"),
    ("020313.40", "22235.44 A0",              "A1 LFT(U), FK59       exp++1024"),
    ("020314.00", "22245.43 A0",              "A1 *+(U), FK67        exp++1791"),
    ("020314.40", "22246.00 80 074042.15 70", "A1 CT0110(BU,60), FK68, 68"),
    ("020315.40", SIC, "A1 SIC"), ("020316.00", BRGZ, "A1 BRGZ"),
    ("020316.40", CKLO,                       "A1 CT0110(BU,48), FPK27+.12, 20"),
    ("020317.40", SIC, "A1 SIC"), ("020320.00", BRGZ, "A1 BRGZ"),
    # A2
    ("020320.40", "22164.44 60",              "A2 DL(U), FK18        exp++4"),
    ("020321.00", SETLO,                      "A2 C0011(BU,48), FPK27+.12, 20"),
    ("020322.00", "22237.44 A0",              "A2 LFT(U), FK61       exp+-1024"),
    ("020322.40", "22121.43 A0",              "A2 *+(U), FPK80       exp++2"),
    ("020323.00", "22164.00 80 074042.15 70", "A2 CT0110(BU,60), FK18, 68"),
    ("020324.00", SIC, "A2 SIC"), ("020324.40", BRGZ, "A2 BRGZ"),
    ("020325.00", CKLO,                       "A2 CT0110(BU,48), FPK27+.12, 20"),
    ("020326.00", SIC, "A2 SIC"), ("020326.40", BRGZ, "A2 BRGZ"),
    # A3
    ("020327.00", "22164.44 60",              "A3 DL(U), FK18        exp++4"),
    ("020327.40", SETLO,                      "A3 C0011(BU,48), FPK27+.12, 20"),
    ("020330.40", "22071.44 A0",              "A3 LFT(U), FPK52      exp++2"),
    ("020331.00", "22236.43 A0",              "A3 *+(U), FK60        exp+-1024"),
    ("020331.40", "22164.00 80 074042.15 70", "A3 CT0110(BU,60), FK18, 68"),
    ("020332.40", SIC, "A3 SIC"), ("020333.00", BRGZ, "A3 BRGZ"),
    ("020333.40", CKLO,                       "A3 CT0110(BU,48), FPK27+.12, 20"),
    ("020334.40", SIC, "A3 SIC"), ("020335.00", BRGZ, "A3 BRGZ"),
    # A4 -- the product wins
    ("020335.40", "22164.44 60",              "A4 DL(U), FK18        exp++4"),
    ("020336.00", SETLO,                      "A4 C0011(BU,48), FPK27+.12, 20"),
    ("020337.00", "22237.44 A0",              "A4 LFT(U), FK61       exp+-1024"),
    ("020337.40", "22245.43 A0",              "A4 *+(U), FK67        exp++1791"),
    ("020340.00", "22245.00 80 014072.15 70", "A4 CT0110(BU,12), FK67, 116"),
    ("020341.00", SIC, "A4 SIC"), ("020341.40", BRGZ, "A4 BRGZ"),
    ("020342.00", CK16,                       "A4 CT0110(BU,48), FK16+.12, 68"),
    ("020343.00", SIC, "A4 SIC"), ("020343.40", BRGZ, "A4 BRGZ"),
    ("020344.00", CK67,                       "A4 CT0110(BU,48), FK67+.12, 20"),
    ("020345.00", SIC, "A4 SIC"), ("020345.40", BRGZ, "A4 BRGZ"),
    # A5
    ("020346.00", "22247.44 60",              "A5 DL(U), FK69        exp+-2047"),
    ("020346.40", SETLO,                      "A5 C0011(BU,48), FPK27+.12, 20"),
    ("020347.40", "22235.44 A0",              "A5 LFT(U), FK59       exp++1024"),
    ("020350.00", "22121.43 A0",              "A5 *+(U), FPK80       exp++2"),
    ("020350.40", "22206.00 80 014072.15 70", "A5 CT0110(BU,12), FK36, 116"),
    ("020351.40", SIC, "A5 SIC"), ("020352.00", BRGZ, "A5 BRGZ"),
    ("020352.40", CK16,                       "A5 CT0110(BU,48), FK16+.12, 68"),
    ("020353.40", SIC, "A5 SIC"), ("020354.00", BRGZ, "A5 BRGZ"),
    ("020354.40", CK67,                       "A5 CT0110(BU,48), FK67+.12, 20"),
    ("020355.40", SIC, "A5 SIC"), ("020356.00", BRGZ, "A5 BRGZ"),
    # A6 -- the only unflagged sub-test
    ("020356.40", "22164.44 60",              "A6 DL(U), FK18        exp++4"),
    ("020357.00", SETLO,                      "A6 C0011(BU,48), FPK27+.12, 20"),
    ("020360.00", "22071.44 A0",              "A6 LFT(U), FPK52      exp++2"),
    ("020360.40", "22121.43 A0",              "A6 *+(U), FPK80       exp++2"),
    ("020361.00", "22164.00 80 014072.15 70", "A6 CT0110(BU,12), FK18, 116"),
    ("020362.00", SIC, "A6 SIC"), ("020362.40", BRGZ, "A6 BRGZ"),
    ("020363.00", "22045.14 80 060042.15 70", "A6 CT0110(BU,48), FPK32+.12, 68"),
    ("020364.00", SIC, "A6 SIC"), ("020364.40", BRGZ, "A6 BRGZ"),
    ("020365.00", "22045.14 80 060012.15 70", "A6 CT0110(BU,48), FPK32+.12, 20"),
    ("020366.00", SIC, "A6 SIC"), ("020366.40", BRGZ, "A6 BRGZ"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
