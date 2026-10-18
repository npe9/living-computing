#!/usr/bin/env python3
"""verify_fp_arith_f218d_listing.py -- F218 "STORE ROOT TEST",
sub-block F218D "TESTS OF INDICATORS"
(../decks/fp_arith_f218d.strap) against jb_af1c p.168.

One sub-test, two questions, closing F218A's last gap.  SRT is the
floating-point operation that SETS MOP rather than clearing it, and IR
comes on when the accumulator sign, as modified by the absolute
modifier, is negative.  An LN load makes it negative, Z,$IND clears
the indicator word, a plain SRT runs, and both must come on.  F218A12
set IR and cleared it with a BIRZ without ever asking; this is where
it is asked.

TRANSCRIPTION NOTE: the source column reads "LN%N=,FPK72" but the
printed code is 22114.10 60, and 022114 is FPK73.  Rendered from the
printed code, as F214C2's similar disagreement was.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f218d.strap").read())
CONST_ROWS = [("022114.00", "0030000000000000000400", "FPK73")]
CODE_ROWS = [
    ("021440.00", "21440.50 00", "D B, $+.32"),
    ("021440.40", "22114.10 60", "D LN(N), FPK73   (see note)"),
    ("021441.00", "13.22 00",    "D Z, $IND"),
    ("021441.40", "22355.46 E0", "D SRT(U), ROS"),
    ("021442.00", "1310.00 80",  "D SIC"),
    ("021442.40", "1304.33 C0",  "D BZMOP, SERS   error if MOP off"),
    ("021443.00", "1310.00 80",  "D SIC"),
    ("021443.40", "1304.14 C0",  "D BZIR, SERS    error if IR off"),
    ("021444.00", "13.22 00",    "D Z, $IND"),
]
if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
