#!/usr/bin/env python3
"""verify_ibox4_refill_nop_listing.py -- IBOX-4 routine 1238 test 2,
cases 2G and 2H (../decks/ibox4_refill_nop.strap) against jb_ax4b p.65,
with constants from p.67 and the common table on p.190.

The refill ADDRESS GATE, pinned from both sides: word 0 refills, words
1-15 do not.  Taken as one program because the obvious spelling of the
rule passes one case and fails the other.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ibox4_refill_nop.strap").read())

DATA_ROWS = [
    ('013034.00', '0.00 00 000000.00 00',      'I00Z XW, 0, 0, 0   zero indx wd'),
    ('013036.00', '777777.77 80 000000.00 00', 'I00VO XW, -(8)777777.77, 0, 0   indx wd of ones'),
    ('005576.00', '1.00 00 000360.00 00',      'I38XW5 XW, 1.0, 15, 0   value word 1, count 15'),
    ('005577.00', '5674.00 00 000000.00 00',   'I38XW6 XW, (8)5674.0, 0, 0   -> error table'),
]

CODE_ROWS = [
    ('005527.00', '13036.00 10', 'I382G LX, $X0, I00VO   test 2G - chk refill frm locn 0'),
    ('005527.40', '20.02 00',    'R, $X0'),
    ('005530.00', '13034.00 90', 'KV, $X0, I00Z'),
    ('005530.40', '5532.32 C2',  'BXE, $+1.32'),
    ('005531.00', '1310.00 80',  'SIC, SEN'),
    ('005531.40', '1304.10 00',  'B, SERS   failed to refill frm locn 0'),
    ('005532.00', '5576.34 10',  'I3822 LX, $X14, I38XW5   test 2H - chk no refill frm'),
    ('005532.40', '5577.36 10',  'LX, $X15, I38XW6         locns 1 through 17'),
    ('005533.00', '20.22 00',    'Z, $X0'),
    ('005533.40', '5535.35 D0',  'I3823 SVA, $X14, I3824'),
    ('005534.00', '5537.37 D0',  'SVA, $X15, I3825'),
    ('005534.40', '765432.41 01','LVI, $X0, (8)765432.40'),
    ('005535.00', '0.01 03',     'I3824 LRI, $X0, 0.0   patched each pass'),
    ('005535.40', '20.02 00',    'R, $X0'),
    ('005536.00', '765432.41 04','KVI, $X0, (8)765432.40'),
    ('005536.40', '5537.72 C2',  'BXE, $+1.0'),
    ('005537.00', '0.10 00',     'I3825 B, 0   listing "$B,0" -- did refill'),
    ('005537.40', '1.35 05',     'I3826 V+I, $X14, 1.0'),
    ('005540.00', '1.35 08',     'C-I, $X14, 1'),
    ('005540.40', '5542.30 42',  'BXCZ, I3827'),
    ('005541.00', '2.37 05',     'V+I, $X15, 2.0'),
    ('005541.40', '5533.50 00',  'B, I3823'),
    ('005542.00', '5543.10 00',  'I3827 B, $+1.0'),
]

if __name__ == "__main__":
    fails = check_rows(prog, DATA_ROWS, label="data")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
