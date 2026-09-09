#!/usr/bin/env python3
"""verify_fp_arith_f217xa_listing.py -- F217-XA "RECIPROCAL DIVIDE
TESTS" (programs/fp_arith_f217xa.strap) against jb_af1c p.162.

The block that adds R/ (opcode 0111110).  p.94 defines it as DIVIDE
"with the exception of the interchange of the operands used for
dividends and divisor", and this block is F217A with exactly that
swap: XA1-XA7 use A1-A7's pairs reversed between accumulator and
storage and check against the SAME seven constants, so an arm that
divided the accumulator by the operand would fail every row.

XA8 is the zero divisor from the opposite side: for R/ the accumulator
IS the divisor, so FPK29's zero fraction suppresses the operation and
the check is that FPK29 is still sitting there.

R/(U) prints "<addr>.43 E0" against /(U)'s ".41 E0" and D/(U)'s ".45".
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f217xa.strap").read())

CONST_ROWS = [
    ('022042.00', '0000400000000000000000', 'FPK29'),
    ('022071.00', '0001024713560247135620', 'FPK52'),
    ('022104.00', '0001051627340516273440', 'FPK64'),
    ('022121.00', '0001100000000000000000', 'FPK80'),
    ('022235.00', '1000024713560247135620', 'FK59'),
    ('022236.00', '1000300000000000000000', 'FK60'),
    ('022264.00', '1002051627340516273440', 'FK83'),
    ('022265.00', '1002100000000000000000', 'FK84'),
    ('022266.00', '1000051627340516273440', 'FK85'),
    ('022267.00', '1577651627340516273440', 'FK86'),
    ('022270.00', '0000100000000000000000', 'FK87'),
    ('022271.00', '1577624713560247135620', 'FK88'),
    ('022272.00', '1000251627340516273440', 'FK89'),
    ('022273.00', '1000100000000000000000', 'FK90'),
    ('022305.00', '1577700000000000000000', 'FK100'),
]

CODE_ROWS = [
    ('021133.00', '22235.40 60', 'XA1 L(U), FK59'),
    ('021133.40', '22264.43 E0', 'XA1 R/(U), FK83'),
    ('021134.00', '22265.00 80 074042.15 70', 'XA1 CT0110(BU,60), FK84, 68'),
    ('021135.00', '1310.00 80', 'XA1 SIC'),
    ('021135.40', '1304.35 42', 'XA1 BRGZ'),
    ('021136.00', '22266.40 60', 'XA2 L(U), FK85'),
    ('021136.40', '22071.43 E0', 'XA2 R/(U), FPK52'),
    ('021137.00', '22236.00 80 074042.15 70', 'XA2 CT0110(BU,60), FK60, 68'),
    ('021140.00', '1310.00 80', 'XA2 SIC'),
    ('021140.40', '1304.35 42', 'XA2 BRGZ'),
    ('021141.00', '22235.40 60', 'XA3 L(U), FK59'),
    ('021141.40', '22267.43 E0', 'XA3 R/(U), FK86'),
    ('021142.00', '22236.00 80 074042.15 70', 'XA3 CT0110(BU,60), FK60, 68'),
    ('021143.00', '1310.00 80', 'XA3 SIC'),
    ('021143.40', '1304.35 42', 'XA3 BRGZ'),
    ('021144.00', '22071.40 60', 'XA4 L(U), FPK52'),
    ('021144.40', '22104.43 E0', 'XA4 R/(U), FPK64'),
    ('021145.00', '22121.00 80 074042.15 70', 'XA4 CT0110(BU,60), FPK80, 68'),
    ('021146.00', '1310.00 80', 'XA4 SIC'),
    ('021146.40', '1304.35 42', 'XA4 BRGZ'),
    ('021147.00', '22104.40 60', 'XA5 L(U), FPK64'),
    ('021147.40', '22071.43 E0', 'XA5 R/(U), FPK52'),
    ('021150.00', '22270.00 80 074042.15 70', 'XA5 CT0110(BU,60), FK87, 68'),
    ('021151.00', '1310.00 80', 'XA5 SIC'),
    ('021151.40', '1304.35 42', 'XA5 BRGZ'),
    ('021152.00', '22071.40 60', 'XA6 L(U), FPK52'),
    ('021152.40', '22267.43 E0', 'XA6 R/(U), FK86'),
    ('021153.00', '22305.00 80 074042.15 70', 'XA6 CT0110(BU,60), FK100, 68'),
    ('021154.00', '1310.00 80', 'XA6 SIC'),
    ('021154.40', '1304.35 42', 'XA6 BRGZ'),
    ('021155.00', '22272.40 60', 'XA7 L(U), FK89'),
    ('021155.40', '22271.43 E0', 'XA7 R/(U), FK88'),
    ('021156.00', '22273.00 80 074042.15 70', 'XA7 CT0110(BU,60), FK90, 68'),
    ('021157.00', '1310.00 80', 'XA7 SIC'),
    ('021157.40', '1304.35 42', 'XA7 BRGZ'),
    ('021160.00', '22042.40 60', 'XA8 L(U), FPK29'),
    ('021160.40', '22071.43 E0', 'XA8 R/(U), FPK52'),
    ('021161.00', '22042.00 80 074042.15 70', 'XA8 CT0110(BU,60), FPK29, 68'),
    ('021162.00', '1310.00 80', 'XA8 SIC'),
    ('021162.40', '1304.35 42', 'XA8 BRGZ'),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
