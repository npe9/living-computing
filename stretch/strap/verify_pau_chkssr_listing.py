#!/usr/bin/env python3
"""verify_pau_chkssr_listing.py -- the PAU GATES ROUTINE's CHKSSR block
(programs/pau_chkssr.strap) against jb_af1c pp.192-193 (code) and
pp.199-200 (data).

CHKSSR walks a single one-bit down the radicand and takes its square
root at each position.  It was chosen over the routine's remaining
shift blocks because it is a different and sharper shape: no index
register (so none of the index blindness the shift blocks have), a
straight line with a separate error exit per case, and a direct
bit-by-bit exercise of STORE ROOT, which F219O touched exactly once.

The expected values are one constant read at sliding offsets: the
48-bit window into SMANL1 starting at bit 50 is 000001000000, at 51 is
000002000000, at 52 is 000004000000 -- successive powers of two, one
per case.  All seven were computed from the constants and checked
against an integer square root before the first run.

A note on the operand offset field, which cost one pass of this table:
it is the offset DIVIDED BY TWO, so an accumulator offset of 68 prints
as 0010(42) octal and 70 as 0010(43).  The assembler had it right and
the first version of this generator did not -- the listing oracle
catching the transcription rather than the model, which is the
direction it is supposed to work in as often as the other.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/pau_chkssr.strap").read())

DATA_ROWS = [
    ('024122.00', '1252525252525250000000', 'WRDB'),
    ('024123.00', '0525252525252524000000', 'WRDB+1'),
    ('024201.00', '0000000000000000000000', 'SMANO'),
    ('024206.00', '0000400000000000000000', 'SMANL1'),
    ('024207.00', '0001000000000000000000', 'SMANL2'),
    ('024210.00', '0001400000000000000000', 'SMANL3'),
    ('024211.00', '0002000000000000000000', 'SMANL4'),
    ('024237.00', '0000000000000000000000', 'SRSG'),
]

CODE_ROWS = [
    ('023410.40', '24201.00 80 001000.20 50', 'CHKSSR L(BU,1), SMANO, 0'),
    ('023411.40', '24237.46 E0', 'SRT(U), SRSG'),
    ('023412.00', '24237.14 80 060042.20 50', 'L(BU,48), SRSG+.12, 68'),
    ('023413.00', '24201.00 80 060042.15 70', 'CT0110(BU,48), SMANO, 68'),
    ('023414.00', '13.71 80 023415.74 00', 'BZB, $RZ, SRTE1'),
    ('023415.00', '23416.50 00', 'B, $+1.32'),
    ('023415.40', '1310.00 80', 'SRTE1 SIC, SEN'),
    ('023416.00', '1304.10 00', 'B, SERS   rdcnd was all zero'),
    ('023416.40', '24122.00 80 001042.20 50', 'L(BU,1), WRDB, 68'),
    ('023417.40', '24237.46 E0', 'SRT(U), SRSG'),
    ('023420.00', '24237.14 80 060042.20 50', 'L(BU,48), SRSG+.12, 68'),
    ('023421.00', '24206.62 80 060042.15 70', 'CT0110(BU,48), SMANL1+.50, 68'),
    ('023422.00', '13.71 80 023423.74 00', 'BZB, $RZ, SRTE2'),
    ('023423.00', '23424.50 00', 'B, $+1.32'),
    ('023423.40', '1310.00 80', 'SRTE2 SIC, SEN'),
    ('023424.00', '1304.10 00', 'B, SERS   rdcnd had 1 in pos 59'),
    ('023424.40', '24122.00 80 001043.20 50', 'L(BU,1), WRDB, 70'),
    ('023425.40', '24237.46 E0', 'SRT(U), SRSG'),
    ('023426.00', '24237.14 80 060042.20 50', 'L(BU,48), SRSG+.12, 68'),
    ('023427.00', '24206.63 80 060042.15 70', 'CT0110(BU,48), SMANL1+.51, 68'),
    ('023430.00', '13.71 80 023431.74 00', 'BZB, $RZ, SRTE3'),
    ('023431.00', '23432.50 00', 'B, $+1.32'),
    ('023431.40', '1310.00 80', 'SRTE3 SIC, SEN'),
    ('023432.00', '1304.10 00', 'B, SERS   rdcnd had 1 in pos 57'),
    ('023432.40', '24122.00 80 001044.20 50', 'L(BU,1), WRDB, 72'),
    ('023433.40', '24237.46 E0', 'SRT(U), SRSG'),
    ('023434.00', '24237.14 80 060042.20 50', 'L(BU,48), SRSG+.12, 68'),
    ('023435.00', '24206.64 80 060042.15 70', 'CT0110(BU,48), SMANL1+.52, 68'),
    ('023436.00', '13.71 80 023437.74 00', 'BZB, $RZ, SRTE4'),
    ('023437.00', '23440.50 00', 'B, $+1.32'),
    ('023437.40', '1310.00 80', 'SRTE4 SIC, SEN'),
    ('023440.00', '1304.10 00', 'B, SERS   rdcnd had 1 in pos 55'),
    ('023440.40', '24122.00 80 001045.20 50', 'L(BU,1), WRDB, 74'),
    ('023441.40', '24237.46 E0', 'SRT(U), SRSG'),
    ('023442.00', '24237.14 80 060042.20 50', 'L(BU,48), SRSG+.12, 68'),
    ('023443.00', '24206.65 80 060042.15 70', 'CT0110(BU,48), SMANL1+.53, 68'),
    ('023444.00', '13.71 80 023445.74 00', 'BZB, $RZ, SRTE5'),
    ('023445.00', '23446.50 00', 'B, $+1.32'),
    ('023445.40', '1310.00 80', 'SRTE5 SIC, SEN'),
    ('023446.00', '1304.10 00', 'B, SERS   rdcnd had 1 in pos 53'),
    ('023446.40', '24122.00 80 001046.20 50', 'L(BU,1), WRDB, 76'),
    ('023447.40', '24237.46 E0', 'SRT(U), SRSG'),
    ('023450.00', '24237.14 80 060042.20 50', 'L(BU,48), SRSG+.12, 68'),
    ('023451.00', '24206.66 80 060042.15 70', 'CT0110(BU,48), SMANL1+.54, 68'),
    ('023452.00', '13.71 80 023453.74 00', 'BZB, $RZ, SRTE6'),
    ('023453.00', '23454.50 00', 'B, $+1.32'),
    ('023453.40', '1310.00 80', 'SRTE6 SIC, SEN'),
    ('023454.00', '1304.10 00', 'B, SERS   rdcnd had 1 in pos 51'),
    ('023454.40', '24122.00 80 001047.20 50', 'L(BU,1), WRDB, 78'),
    ('023455.40', '24237.46 E0', 'SRT(U), SRSG'),
    ('023456.00', '24237.14 80 060042.20 50', 'L(BU,48), SRSG+.12, 68'),
    ('023457.00', '24206.67 80 060042.15 70', 'CT0110(BU,48), SMANL1+.55, 68'),
    ('023460.00', '13.71 80 023461.74 00', 'BZB, $RZ, SRTE7'),
    ('023461.00', '23462.50 00', 'B, $+1.32'),
    ('023461.40', '1310.00 80', 'SRTE7 SIC, SEN'),
    ('023462.00', '1304.10 00', 'B, SERS   rdcnd had 1 in pos 49'),
]

if __name__ == "__main__":
    fails = check_rows(prog, DATA_ROWS, label="data")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
