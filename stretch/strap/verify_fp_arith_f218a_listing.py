#!/usr/bin/env python3
"""verify_fp_arith_f218a_listing.py -- F218 "STORE ROOT TEST",
sub-block F218A "ARITHMETIC CHECKS" (programs/fp_arith_f218a.strap)
against jb_af1c p.165.

The block that adds SRT (opcode 1101110), the last floating-point
operation without an implementation.  p.93: the exponent is halved,
and an odd exponent has one added and the fraction shifted right first
-- except in the XFP and XFN ranges, where "the exponent is not
modified as a result of the shift".  A5 is exactly that: FK126 at
+1791, odd, whose answer keeps +1791.

Each sub-test loads the EXPECTED answer into the accumulator's right
word, the operand into the left, stores the root to ROS and compares.
That makes every row a store-close-to-fetch, which is why SRT had to
join storeTarget.

SRT(U) prints "<addr>.46 E0".
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f218a.strap").read())

CONST_ROWS = [
    ('022042.00', '0000400000000000000000', 'FPK29'),
    ('022107.00', '0001000000000000000000', 'FPK67'),
    ('022112.00', '0030000000000000001420', 'FPK71'),
    ('022113.00', '0001560000000000000000', 'FPK72'),
    ('022114.00', '0030000000000000000400', 'FPK73'),
    ('022115.00', '0001500000000000000000', 'FPK74'),
    ('022116.00', '0001400000000000000000', 'FPK75'),
    ('022236.00', '1000300000000000000000', 'FK60'),
    ('022254.00', '1577440000000000000000', 'FK74'),
    ('022255.00', '1000010000000000000000', 'FK75'),
    ('022256.00', '1000040000000000000000', 'FK76'),
    ('022257.00', '1000240000000000000000', 'FK78'),
    ('022337.00', '1577420000000000000000', 'FK126'),
]

CODE_ROWS = [
    ('021252.40', '021253.10 00', 'A1 B, $+.32'),
    ('021253.00', '22042.00 80 000000.20 50', 'A1 L(BU,64), FPK29   (expected answer)'),
    ('021254.00', '22107.40 60', 'A1 L(U), FPK67'),
    ('021254.40', '22355.46 E0', 'A1 SRT(U), ROS'),
    ('021255.00', '22355.00 80 000000.15 70', 'A1 CT0110(BU,64), ROS'),
    ('021256.00', '1310.00 80', 'A1 SIC'),
    ('021256.40', '1304.35 42', 'A1 BRGZ'),
    ('021257.00', '021257.50 00', 'A2 B, $+.32'),
    ('021257.40', '22113.00 80 000000.20 50', 'A2 L(BU,64), FPK72   (expected answer)'),
    ('021260.40', '22112.00 60', 'A2 L(N), FPK71'),
    ('021261.00', '22355.46 E0', 'A2 SRT(U), ROS'),
    ('021261.40', '22355.00 80 000000.15 70', 'A2 CT0110(BU,64), ROS'),
    ('021262.40', '1310.00 80', 'A2 SIC'),
    ('021263.00', '1304.35 42', 'A2 BRGZ'),
    ('021263.40', '021264.10 00', 'A3 B, $+.32'),
    ('021264.00', '22107.00 80 000000.20 50', 'A3 L(BU,64), FPK67   (expected answer)'),
    ('021265.00', '22116.40 60', 'A3 L(U), FPK75'),
    ('021265.40', '22355.46 E0', 'A3 SRT(U), ROS'),
    ('021266.00', '22355.00 80 000000.15 70', 'A3 CT0110(BU,64), ROS'),
    ('021267.00', '1310.00 80', 'A3 SIC'),
    ('021267.40', '1304.35 42', 'A3 BRGZ'),
    ('021270.00', '021270.50 00', 'A4 B, $+.32'),
    ('021270.40', '22115.00 80 000000.20 50', 'A4 L(BU,64), FPK74   (expected answer)'),
    ('021271.40', '22114.00 60', 'A4 L(N), FPK73'),
    ('021272.00', '22355.46 E0', 'A4 SRT(U), ROS'),
    ('021272.40', '22355.00 80 000000.15 70', 'A4 CT0110(BU,64), ROS'),
    ('021273.40', '1310.00 80', 'A4 SIC'),
    ('021274.00', '1304.35 42', 'A4 BRGZ'),
    ('021274.40', '22254.00 80 000000.20 50', 'A5 L(BU,64), FK74   (expected answer)'),
    ('021275.40', '22337.40 60', 'A5 L(U), FK126'),
    ('021276.00', '22355.46 E0', 'A5 SRT(U), ROS'),
    ('021276.40', '22355.00 80 000000.15 70', 'A5 CT0110(BU,64), ROS'),
    ('021277.40', '1310.00 80', 'A5 SIC'),
    ('021300.00', '1304.35 42', 'A5 BRGZ'),
    ('021300.40', '021301.10 00', 'A6 B, $+.32'),
    ('021301.00', '22256.00 80 000000.20 50', 'A6 L(BU,64), FK76   (expected answer)'),
    ('021302.00', '22255.40 60', 'A6 L(U), FK75'),
    ('021302.40', '22355.46 E0', 'A6 SRT(U), ROS'),
    ('021303.00', '22355.00 80 000000.15 70', 'A6 CT0110(BU,64), ROS'),
    ('021304.00', '1310.00 80', 'A6 SIC'),
    ('021304.40', '1304.35 42', 'A6 BRGZ'),
    ('021305.00', '021305.50 00', 'A7 B, $+.32'),
    ('021305.40', '22236.00 80 000000.20 50', 'A7 L(BU,64), FK60   (expected answer)'),
    ('021306.40', '22257.40 60', 'A7 L(U), FK78'),
    ('021307.00', '22355.46 E0', 'A7 SRT(U), ROS'),
    ('021307.40', '22355.00 80 000000.15 70', 'A7 CT0110(BU,64), ROS'),
    ('021310.40', '1310.00 80', 'A7 SIC'),
    ('021311.00', '1304.35 42', 'A7 BRGZ'),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
