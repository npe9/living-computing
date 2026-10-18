#!/usr/bin/env python3
"""verify_ibox4_refill_listing.py -- IBOX-4 routine 1238 test 1, first
check (../decks/ibox4_refill.strap) against jb_ax4b p.58, with the BIT
constants it loads from the table at 013054 on pp.191-192.

R (Refill).  This is the block that caught execute() reading the
address-MODIFIER field instead of the effective address.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ibox4_refill.strap").read())

DATA_ROWS = [
    ('013071.00', '20.00 00 000000.00 00', 'BIT13 XW, (8)20.00, 0, 0   bit 13 -> VALUE 020'),
    ('013072.00', '10.00 00 000000.00 00', 'BIT14 XW, (8)10.00, 0, 0   bit 14 -> VALUE 010'),
    ('013074.00', '2.00 00 000000.00 00',  'BIT16 XW, (8)2.00, 0, 0    bit 16 -> VALUE 002'),
    ('013147.00', '0.00 00 000000.00 10',  'BIT59 XW, 0, 0, 16         bit 59 -> REFILL 020'),
]

CODE_ROWS = [
    ('005303.00', '13147.36 10', 'I381 LX, $X15, BIT59   check basic control - all addresses'),
    ('005303.40', '13072.00 10', 'LX, $X0, BIT14   in comments below are octal'),
    ('005304.00', '10.01 10',    'SX, $X0, 8'),
    ('005304.40', '13074.00 10', 'LX, $X0, BIT16'),
    ('005305.00', '1.01 30',     'SV, $X0, 2'),
    ('005305.40', '13071.00 10', 'LX, $X0, BIT13'),
    ('005306.00', '0.02 10',     'LX, $X1, 0'),
    ('005306.40', '0.43 30',     'SV, $X1, 1'),
    ('005307.00', '37.02 00',    'R, $X15'),
    ('005307.40', '0.30 00',     'NOP'),
    ('005310.00', '0.30 00',     'NOP'),
    ('005310.40', '0.30 00',     'NOP'),
    ('005311.00', '0.77 04',     'KVI, $X15, (8)0.40'),
    ('005311.40', '5313.73 42',  'BXH, $+2.0'),
    ('005312.00', '1310.00 80',  'SIC, SEN   refilled X15 from locn 1 instead'),
    ('005312.40', '1304.10 00',  'B, SERS    of locn 20'),
    ('005313.00', '5437.50 00',  'B, I3813   term test 1'),
]

if __name__ == "__main__":
    fails = check_rows(prog, DATA_ROWS, label="data")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
