#!/usr/bin/env python3
"""verify_fp_arith_f215e_listing.py -- F215 "LOAD FACTOR TEST",
sub-block F215E "TEST ARITH RESULT INDICATORS"
(programs/fp_arith_f215e.strap) against jb_af1c pp.145-146.

p.98: RLZ/RZ/RGZ/RN are "set according to the arithmetic result which
appears in the FT register".  Three sub-tests, one per outcome, each
clearing $IND first and then asking about the indicator that must be
on AND the ones that must be off -- so a model setting every result
indicator fails rather than passing three "is it on?" checks.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f215e.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022006.00", "1777777777777777777777", "FPK1"),
    ("022045.00", "0001177777777777777760", "FPK32"),
]

SIC   = "1310.00 80"
ZIND  = "13.22 00"

CODE_ROWS = [
    # E1 -- negative non-zero: RLZ and RN on, RZ and RGZ off.
    ("020251.40", ZIND,           "E1 Z, $IND"),
    ("020252.00", "22006.44 A0",  "E1 LFT(U), FPK1"),
    ("020252.40", SIC, "E1 SIC"),
    ("020253.00", "1304.34 40",   "E1 BZRLZ, SERS   error if RLZ off"),
    ("020253.40", SIC, "E1 SIC"),
    ("020254.00", "1304.35 C0",   "E1 BZRN, SERS    error if RN off"),
    ("020254.40", SIC, "E1 SIC"),
    ("020255.00", "1304.34 C2",   "E1 BRZ, SERS     error if RZ on"),
    ("020255.40", SIC, "E1 SIC"),
    ("020256.00", "1304.35 42",   "E1 BRGZ, SERS"),

    # E2 -- zero: RZ on, the rest off.
    ("020256.40", ZIND,           "E2 Z, $IND"),
    ("020257.00", "22005.44 A0",  "E2 LFT(U), FPK0"),
    ("020257.40", SIC, "E2 SIC"),
    ("020260.00", "1304.34 C0",   "E2 BZRZ, SERS    error if RZ off"),
    ("020260.40", SIC, "E2 SIC"),
    ("020261.00", "1304.34 42",   "E2 BRLZ, SERS    error if RLZ on"),
    ("020261.40", SIC, "E2 SIC"),
    ("020262.00", "1304.35 C2",   "E2 BRN, SERS     error if RN on"),
    ("020262.40", SIC, "E2 SIC"),
    ("020263.00", "1304.35 42",   "E2 BRGZ, SERS"),

    # E3 -- positive non-zero: RGZ on, the rest off.
    ("020263.40", ZIND,           "E3 Z, $IND"),
    ("020264.00", "22045.44 A0",  "E3 LFT(U), FPK32"),
    ("020264.40", SIC, "E3 SIC"),
    ("020265.00", "1304.35 40",   "E3 BZRGZ, SERS   error if RGZ off"),
    ("020265.40", SIC, "E3 SIC"),
    ("020266.00", "1304.34 42",   "E3 BRLZ, SERS    error if RLZ on"),
    ("020266.40", SIC, "E3 SIC"),
    ("020267.00", "1304.35 C2",   "E3 BRN, SERS     error if RN on"),
    ("020267.40", SIC, "E3 SIC"),
    ("020270.00", "1304.34 C2",   "E3 BRZ, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
