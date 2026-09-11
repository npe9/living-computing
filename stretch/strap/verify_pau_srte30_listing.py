#!/usr/bin/env python3
"""verify_pau_srte30_listing.py -- the PAU GATES ROUTINE's SRTE30 check
(programs/pau_srte30.strap) against jb_af1c p.195 and p.199.

The first square-root case in the suite with an ODD exponent.  Every
earlier one -- CHKSSR's fourteen single-bit positions and the four
multi-bit perfect squares -- is built by a VFL load that leaves the
exponent field zero.  This block adds a one into IBM 10, the low bit
of EM, making the exponent +1, and its fraction is a single bit at the
very bottom (IBM 59).

Its branch is BBZ, not the BZB every other check uses: BZB branches
when the indicator is zero, BBZ when it is one.  So it halts when RZ
is ON -- when the root came out zero -- and the message says why:
"SHIFT R1-BIT LOST".  The block asserts the bit is not lost.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/pau_srte30.strap").read())

DATA_ROWS = [
    ('024122.00', '1252525252525250000000', 'WRDB'),
    ('024123.00', '0525252525252524000000', 'WRDB+1'),
    ('024237.00', '0000000000000000000000', 'SRSG'),
]

CODE_ROWS = [
    ('023666.40', '24122.00 80 001042.20 50', 'SR30 L(BU,1), WRDB, 68'),
    ('023667.40', '24122.00 80 001072.60 10', '+(BU,1), WRDB, 117'),
    ('023670.40', '24237.46 E0', 'SRT(U), SRSG'),
    ('023671.00', '13.71 80 023672.74 06', 'BBZ, $RZ, SRTE30'),
    ('023672.00', '23673.50 00', 'B, $+1.32'),
    ('023672.40', '1310.00 80', 'SRTE30 SIC, SEN'),
    ('023673.00', '1304.10 00', 'B, SERS   shift r1-bit lost'),
]

if __name__ == "__main__":
    fails = check_rows(prog, DATA_ROWS, label="data")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
