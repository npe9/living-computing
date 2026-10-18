#!/usr/bin/env python3
"""verify_pau_shfr12_listing.py -- the PAU GATES ROUTINE's SHFR1 and
SHFR2 blocks (../decks/pau_shfr12.strap) against jb_af1c pp.180-181
(code) and p.199 (index control word and data tables).

These are the blocks that fix what SHF0 could not see.  SHF0's shift
is by zero, so its expected values are its input tables and the
compares index them through the same register as the operands -- a
wrong index moves both sides together and the block reports nothing.
SHFR1 and SHFR2 compare against SEPARATE tables (WRDAR1/WRDBR1,
WRDAR2/WRDBR2), so the compares no longer move with the operands.

The tables are built from alternating bits on purpose.  The two
entries give 96-bit fractions of aaaa... and 5555..., so a right shift
of n lands on a different constant for every n, and every one of the
four expected values was computed from the input tables before the
first run.

One row is a deliberate substitution and is NOT in the table below:
the listing's `B,SSW` between the two blocks is the SSIP return, and
standing alone this program falls through into SHFR2 instead.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/pau_shfr12.strap").read())

DATA_ROWS = [
    ('024120.00', '0000125252525252525252', 'WRDA'),
    ('024121.00', '0000052525252525252525', 'WRDA+1'),
    ('024122.00', '1252525252525250000000', 'WRDB'),
    ('024123.00', '0525252525252524000000', 'WRDB+1'),
    ('024124.00', '0000052525252525252525', 'WRDAR1'),
    ('024125.00', '0000025252525252525252', 'WRDAR1+1'),
    ('024126.00', '0525252525252524000000', 'WRDBR1'),
    ('024127.00', '1252525252525250000000', 'WRDBR1+1'),
    ('024130.00', '0000025252525252525252', 'WRDAR2'),
    ('024131.00', '0000012525252525252525', 'WRDAR2+1'),
    ('024132.00', '1252525252525250000000', 'WRDBR2'),
    ('024133.00', '0525252525252524000000', 'WRDBR2+1'),
]

CODE_ROWS = [
    ('024117.00', '0.00 00 000040.50 4F', 'XA XW, 0, 2, XA'),
    # -- SHFR1, shift right one
    ('022400.40', '24120.00 81 000040.20 50', 'SHFR1 L(BU,64), WRDA($X1), 64'),
    ('022401.40', '24122.00 81 000000.20 10', '+(BU,64), WRDB($X1), 0'),
    ('022402.40', '300.47 20', 'SHF(U), -1'),
    ('022403.00', '24124.14 81 064040.15 70', 'CT0110(BU,52), WRDAR1+.12($X1), 64'),
    ('022404.00', '13.71 80 022405.74 00', 'BZB, $RZ, PE4A'),
    ('022405.00', '22406.50 00', 'B, $+1.32'),
    ('022405.40', '1310.00 80', 'PE4A SIC, SEN'),
    ('022406.00', '1304.10 00', 'B, SERS   R1 shift-hi 52 bits or exp dec'),
    ('022406.40', '24126.00 81 054012.15 70', 'CT0110(BU,44), WRDBR1($X1), 20'),
    ('022407.40', '13.71 80 022411.34 00', 'BZB, $RZ, PE4B'),
    ('022410.40', '22412.10 00', 'B, $+1.32'),
    ('022411.00', '1310.00 80', 'PE4B SIC, SEN'),
    ('022411.40', '1304.10 00', 'B, SERS   R1 shift-low 44 bits'),
    ('022412.00', '22400.43 4C', 'CBR+, $X1, SHFR1'),
    ('022412.40', '22413.50 00', 'B, $+1.'),
    ('022413.00', '22400.50 00', 'B, SHFR1'),
    ('022413.40', '1311.40 80', 'SIC, SENO+.32'),
    # 022414.00 is the substituted B,SSW -- not checked, see the docstring
    # -- SHFR2, shift right two
    ('022414.40', '24120.00 81 000040.20 50', 'SHFR2 L(BU,64), WRDA($X1), 64'),
    ('022415.40', '24122.00 81 000000.20 10', '+(BU,64), WRDB($X1), 0'),
    ('022416.40', '500.47 20', 'SHF(U), -2'),
    ('022417.00', '24130.14 81 064040.15 70', 'CT0110(BU,52), WRDAR2+.12($X1), 64'),
    ('022420.00', '13.71 80 022421.74 00', 'BZB, $RZ, PE6A'),
    ('022421.00', '22422.50 00', 'B, $+1.32'),
    ('022421.40', '1310.00 80', 'PE6A SIC, SEN'),
    ('022422.00', '1304.10 00', 'B, SERS   R2 shift-hi 52 bits or exp dec'),
    ('022422.40', '24132.00 81 054012.15 70', 'CT0110(BU,44), WRDBR2($X1), 20'),
    ('022423.40', '13.71 80 022425.34 00', 'BZB, $RZ, PE6B'),
    ('022424.40', '22426.10 00', 'B, $+1.32'),
    ('022425.00', '1310.00 80', 'PE6B SIC, SEN'),
    ('022425.40', '1304.10 00', 'B, SERS   R2 shift-low 44 bits'),
    ('022426.00', '22414.43 4C', 'CBR+, $X1, SHFR2'),
    ('022426.40', '22427.50 00', 'B, $+1.'),
    ('022427.00', '22414.50 00', 'B, SHFR2'),
    ('022427.40', '1311.40 80', 'SIC, SENO+.32'),
]

if __name__ == "__main__":
    fails = check_rows(prog, DATA_ROWS, label="data")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
