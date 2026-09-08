#!/usr/bin/env python3
"""verify_fp_arith_f214xb_listing.py -- F214-X "MULTIPLY DOUBLE TEST",
sub-block F214XB "TEST UNCHANGED REGS"
(programs/fp_arith_f214xb.strap) against jb_af1c p.143.

D*'s counterpart to F214C.  p.97 says D* writes accumulator bits
12-107; XB1 and XB2 check that it stops there, demanding R 44-63 (=
IBM 108-127) survive from both polarities.  XB2 is the load-bearing
one, because D* really does write IBM 64-107 with FPK52 x FPK53.

The SB checks deliberately skip bit 4 (the result sign, which D* may
write) and so cover the flag bits 5-7, which D* must carry through
from the accumulator.

TRANSCRIPTION NOTE: the scan prints XB2's first check at 020157.40,
which cannot be right -- the D* above it is at 020156.40 and XB1
shows D* is a half word.  At 020157.00 all eleven following rows land
on their printed addresses; at .40 none of them do.  Rendered here as
020157.00.

The listing labels the block "F214B" in its left column, reusing the
name of the MULTIPLY sign-modifier block; renamed F214XB here.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f214xb.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022006.00", "1777777777777777777777", "FPK1"),
    ("022071.00", "0001024713560247135620", "FPK52"),
    ("022072.00", "0000400000000000000040", "FPK53"),
]

SIC  = "1310.00 80"
BRGZ = "1304.35 42"

CODE_ROWS = [
    # XB1 -- 0 s remain 0.
    ("020142.00", "22071.00 80 000040.06 70", "XB1 C0011(BU,64), FPK52, 64"),
    ("020143.00", "22005.00 80 000000.00 70", "XB1 C0000(BU,64), FPK0"),
    ("020144.00", "12.00 80 010000.00 F0",    "XB1 CM0000(BU,8), $SB"),
    ("020145.00", "22072.45 A0",              "XB1 D*(U), FPK53"),
    ("020145.40", "22005.00 80 024000.13 70", "XB1 CT0101(BU,20), FPK0   does R44-63 remain +0"),
    ("020146.40", SIC, "XB1 SIC"), ("020147.00", BRGZ, "XB1 BRGZ"),
    ("020147.40", "12.00 80 004000.07 70",    "XB1 CT0011(BU,4), $SB     does SB0-3 remain +0"),
    ("020150.40", SIC, "XB1 SIC"), ("020151.00", BRGZ, "XB1 BRGZ"),
    ("020151.40", "12.05 80 003000.07 70",    "XB1 CT0011(BU,3), $SB+.5  does SB5-7 remain +0"),
    ("020152.40", SIC, "XB1 SIC"), ("020153.00", BRGZ, "XB1 BRGZ"),

    # XB2 -- 1 s remain 1 s.  The R check is the load-bearing row.
    ("020153.40", "22071.00 80 000040.06 70", "XB2 C0011(BU,64), FPK52, 64"),
    ("020154.40", "22006.00 80 000000.36 70", "XB2 C1111(BU,64), FPK1"),
    ("020155.40", "12.00 80 010000.36 F0",    "XB2 CM1111(BU,8), $SB"),
    ("020156.40", "22072.45 A0",              "XB2 D*(U), FPK53"),
    ("020157.00", "22006.00 80 024000.25 70", "XB2 CT1010(BU,20), FPK1   does R44-63 remain +1 s"),
    ("020160.00", SIC, "XB2 SIC"), ("020160.40", BRGZ, "XB2 BRGZ"),
    ("020161.00", "12.00 80 004000.31 70",    "XB2 CT1100(BU,4), $SB     does SB0-3 remain +1 s"),
    ("020162.00", SIC, "XB2 SIC"), ("020162.40", BRGZ, "XB2 BRGZ"),
    ("020163.00", "12.05 80 003000.31 70",    "XB2 CT1100(BU,3), $SB+.5  does SB5-7 remain +1 s"),
    ("020164.00", SIC, "XB2 SIC"), ("020164.40", BRGZ, "XB2 BRGZ"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
