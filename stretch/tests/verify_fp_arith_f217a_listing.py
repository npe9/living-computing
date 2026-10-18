#!/usr/bin/env python3
"""verify_fp_arith_f217a_listing.py -- F217 "DIVIDE TEST ROUTINE",
sub-block F217A "ARITHMETIC CHECKS" (../decks/fp_arith_f217a.strap)
against jb_af1c p.154.

The block that adds / (opcode 0011110), first of the four operations
still unimplemented (/, R/, D/, SRT all want the same divider).

A2 and A3 pin p.94's table the right way round: both have an XFP
divisor and both give the DIVISOR's exponent sign-reversed, -1024,
rather than the dividend's -- A3 in particular, whose dividend is XFN
at -1791.  An implementation testing the dividend's range first passes
A1, A4, A5, A6 and A7 and fails A3.

A8 is the zero divisor: p.93 leaves the accumulator and the sign byte
untouched, so the arm writes nothing at all.

/(U) prints as "<addr>.41 E0".
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f217a.strap").read())

CONST_ROWS = [
    ("022042.00", "0000400000000000000000", "FPK29"),
    ("022071.00", "0001024713560247135620", "FPK52"),
    ("022104.00", "0001051627340516273440", "FPK64"),
    ("022121.00", "0001100000000000000000", "FPK80"),
    ("022235.00", "1000024713560247135620", "FK59"),
    ("022236.00", "1000300000000000000000", "FK60"),
    ("022264.00", "1002051627340516273440", "FK83"),
    ("022265.00", "1002100000000000000000", "FK84"),
    ("022266.00", "1000051627340516273440", "FK85"),
    ("022267.00", "1577651627340516273440", "FK86"),
    ("022270.00", "0000100000000000000000", "FK87"),
    ("022271.00", "1577624713560247135620", "FK88"),
    ("022272.00", "1000251627340516273440", "FK89"),
    ("022273.00", "1000100000000000000000", "FK90"),
    ("022305.00", "1577700000000000000000", "FK100"),
]

SIC  = "1310.00 80"
BRGZ = "1304.35 42"

CODE_ROWS = [
    ("020632.40", "22264.40 60", "A1 L(U), FK83"),
    ("020633.00", "22235.41 E0", "A1 /(U), FK59"),
    ("020633.40", "22265.00 80 074042.15 70", "A1 CT0110(BU,60), FK84, 68"),
    ("020634.40", SIC, "A1 SIC"), ("020635.00", BRGZ, "A1 BRGZ"),

    ("020635.40", "22071.40 60", "A2 L(U), FPK52"),
    ("020636.00", "22266.41 E0", "A2 /(U), FK85"),
    ("020636.40", "22236.00 80 074042.15 70", "A2 CT0110(BU,60), FK60, 68"),
    ("020637.40", SIC, "A2 SIC"), ("020640.00", BRGZ, "A2 BRGZ"),

    ("020640.40", "22267.40 60", "A3 L(U), FK86"),
    ("020641.00", "22235.41 E0", "A3 /(U), FK59"),
    ("020641.40", "22236.00 80 074042.15 70", "A3 CT0110(BU,60), FK60, 68"),
    ("020642.40", SIC, "A3 SIC"), ("020643.00", BRGZ, "A3 BRGZ"),

    ("020643.40", "22104.40 60", "A4 L(U), FPK64"),
    ("020644.00", "22071.41 E0", "A4 /(U), FPK52"),
    ("020644.40", "22121.00 80 074042.15 70", "A4 CT0110(BU,60), FPK80, 68"),
    ("020645.40", SIC, "A4 SIC"), ("020646.00", BRGZ, "A4 BRGZ"),

    ("020646.40", "22071.40 60", "A5 L(U), FPK52"),
    ("020647.00", "22104.41 E0", "A5 /(U), FPK64"),
    ("020647.40", "22270.00 80 074042.15 70", "A5 CT0110(BU,60), FK87, 68"),
    ("020650.40", SIC, "A5 SIC"), ("020651.00", BRGZ, "A5 BRGZ"),

    ("020651.40", "22267.40 60", "A6 L(U), FK86"),
    ("020652.00", "22071.41 E0", "A6 /(U), FPK52"),
    ("020652.40", "22305.00 80 074042.15 70", "A6 CT0110(BU,60), FK100, 68"),
    ("020653.40", SIC, "A6 SIC"), ("020654.00", BRGZ, "A6 BRGZ"),

    ("020654.40", "22271.40 60", "A7 L(U), FK88"),
    ("020655.00", "22272.41 E0", "A7 /(U), FK89"),
    ("020655.40", "22273.00 80 074042.15 70", "A7 CT0110(BU,60), FK90, 68"),
    ("020656.40", SIC, "A7 SIC"), ("020657.00", BRGZ, "A7 BRGZ"),

    ("020657.40", "22071.40 60", "A8 L(U), FPK52"),
    ("020660.00", "22042.41 E0", "A8 /(U), FPK29   zero divisor"),
    ("020660.40", "22071.00 80 014072.15 70", "A8 CT0110(BU,12), FPK52, 116"),
    ("020661.40", SIC, "A8 SIC"), ("020662.00", BRGZ, "A8 BRGZ"),
    ("020662.40", "22071.14 80 060042.15 70", "A8 CT0110(BU,48), FPK52+.12, 68"),
    ("020663.40", SIC, "A8 SIC"), ("020664.00", BRGZ, "A8 BRGZ"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
