#!/usr/bin/env python3
"""verify_fp_arith_f217we_listing.py -- F217-W "DIVIDE DOUBLE TEST",
sub-block F217WE "REMAINDER UNFLO IND TESTS"
(programs/fp_arith_f217we.strap) against jb_af1c pp.160-161.

Two sub-tests that between them define the REMAINDER UNDERFLOW
indicator (RU, 34).  WE1 divides FK98 (-1021) by FK97 (-1022), both
unflagged, so the remainder exponent is the adjusted dividend exponent
less 48 = -1070, out of range by GENERATION -- RU must come on.  WE2
uses F217WA1's flagged pair, whose remainder exponent is the
dividend's own +1028: EF of 1 but PROPAGATED and positive -- RU must
stay off.

Each row opens with a BRUZ to clear RU, because RU is permanent; WE2
is the row that asks for RU OFF and so is exactly the one a stale
indicator would break.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f217we.strap").read())

CONST_ROWS = [
    ("022235.00", "1000024713560247135620", "FK59"),
    ("022264.00", "1002051627340516273440", "FK83"),
    ("022302.00", "0777251627340516273440", "FK97"),
    ("022303.00", "0776624713560247135620", "FK98"),
]

CODE_ROWS = [
    ("021120.40", "22303.44 60", "WE1 DL(U), FK98"),
    ("021121.00", "21121.61 46", "WE1 BRUZ, $+.32"),
    ("021121.40", "22302.45 E0", "WE1 D/(U), FK97   generated EF+1, ES+1"),
    ("021122.00", "1310.00 80",  "WE1 SIC"),
    ("021122.40", "1304.21 40",  "WE1 BZRU, SERS    error if RU off"),
    ("021123.00", "22264.44 60", "WE2 DL(U), FK83"),
    ("021123.40", "21124.21 46", "WE2 BRUZ, $+.32"),
    ("021124.00", "22235.45 E0", "WE2 D/(U), FK59   propagated EF+1"),
    ("021124.40", "1310.00 80",  "WE2 SIC"),
    ("021125.00", "1304.21 42",  "WE2 BRU, SERS     error if RU on"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
