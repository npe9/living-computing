#!/usr/bin/env python3
"""verify_pau_chkssr2_listing.py -- the multi-bit square-root cases of
the PAU GATES ROUTINE's CHKSSR sequence (programs/pau_chkssr2.strap)
against jb_af1c p.195 (code) and pp.199-200 (data).

Where the single-bit sweep pins WHERE the root lands, these four pin
how several root bits are developed in turn.  The radicands are
perfect squares whose roots have two, three and four bits set:

    .1001      = (3/4)^2    -> .11        c00000000000
    .011001    = (5/8)^2    -> .101       a00000000000
    .110001    = (7/8)^2    -> .111       e00000000000
    .11100001  = (15/16)^2  -> .1111      f00000000000

All four computed from the constants and checked against an integer
square root before the first run.  The listing names each in its own
error exit, which is how the radicand bit patterns above are known to
be right rather than inferred.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/pau_chkssr2.strap").read())

DATA_ROWS = [
    ('024204.00', '0001600000000000000000', 'SMANR3'),
    ('024205.00', '0002200000000000000000', 'SMANR4'),
    ('024213.00', '0000025000000000000000', 'NORL2'),
    ('024237.00', '0000000000000000000000', 'SRSG'),
    ('024240.00', '1420000000000000000000', 'SRCNSA'),
    ('024241.00', '1440000000000000000000', 'SRCNSB'),
    ('024242.00', '1604740000000000000000', 'SRCNSC'),
]

CODE_ROWS = [
    # -- square root of .1001
    ('023636.40', '24205.10 80 004070.20 50', 'CHKSS2 L(BU,4), SMANR4+.8, 112'),
    ('023637.40', '24237.46 E0', 'SRT(U), SRSG'),
    ('023640.00', '24237.14 80 060042.20 50', 'L(BU,48), SRSG+.12, 68'),
    ('023641.00', '24204.12 80 060042.15 70', 'CT0110(BU,48), SMANR3+.10, 68'),
    ('023642.00', '13.71 80 023643.74 00', 'BZB, $RZ, SRTE26'),
    ('023643.00', '23644.50 00', 'B, $+1.32'),
    ('023643.40', '1310.00 80', 'SRTE26 SIC, SEN'),
    ('023644.00', '1304.10 00', 'B, SERS   sq rt of .1001----'),
    # -- square root of .011001
    ('023644.40', '24241.00 80 005067.20 50', 'L(BU,5), SRCNSB, 110'),
    ('023645.40', '24237.46 E0', 'SRT(U), SRSG'),
    ('023646.00', '24237.14 80 060042.20 50', 'L(BU,48), SRSG+.12, 68'),
    ('023647.00', '24213.20 80 060042.15 70', 'CT0110(BU,48), NORL2+.16, 68'),
    ('023650.00', '13.71 80 023651.74 00', 'BZB, $RZ, SRTE27'),
    ('023651.00', '23652.50 00', 'B, $+1.32'),
    ('023651.40', '1310.00 80', 'SRTE27 SIC, SEN'),
    ('023652.00', '1304.10 00', 'B, SERS   sq rt of .011001---'),
    # -- square root of .110001
    ('023652.40', '24240.00 80 006067.20 50', 'L(BU,6), SRCNSA, 110'),
    ('023653.40', '24237.46 E0', 'SRT(U), SRSG'),
    ('023654.00', '24237.14 80 060042.20 50', 'L(BU,48), SRSG+.12, 68'),
    ('023655.00', '24204.11 80 060042.15 70', 'CT0110(BU,48), SMANR3+.9, 68'),
    ('023656.00', '13.71 80 023657.74 00', 'BZB, $RZ, SRTE28'),
    ('023657.00', '23660.50 00', 'B, $+1.32'),
    ('023657.40', '1310.00 80', 'SRTE28 SIC, SEN'),
    ('023660.00', '1304.10 00', 'B, SERS   sq rt of .110001----'),
    # -- square root of .11100001
    ('023660.40', '24242.00 80 010066.20 50', 'L(BU,8), SRCNSC, 108'),
    ('023661.40', '24237.46 E0', 'SRT(U), SRSG'),
    ('023662.00', '24237.14 80 060042.20 50', 'L(BU,48), SRSG+.12, 68'),
    ('023663.00', '24242.12 80 060042.15 70', 'CT0110(BU,48), SRCNSC+.10, 68'),
    ('023664.00', '13.71 80 023665.74 00', 'BZB, $RZ, SRTE29'),
    ('023665.00', '23666.50 00', 'B, $+1.32'),
    ('023665.40', '1310.00 80', 'SRTE29 SIC, SEN'),
    ('023666.00', '1304.10 00', 'B, SERS   sq rt of .11100001---'),
]

if __name__ == "__main__":
    fails = check_rows(prog, DATA_ROWS, label="data")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
