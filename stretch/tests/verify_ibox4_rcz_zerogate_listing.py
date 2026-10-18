#!/usr/bin/env python3
"""verify_ibox4_rcz_zerogate_listing.py -- IBOX-4 routine 1238 test 3's
second half (../decks/ibox4_rcz_zerogate.strap) against jb_ax4b p.66,
with constants from p.67 and the BIT table on p.191.

"CHECK ZERO GATING OF RCZ": RCZ must NOT refill while the count is
non-zero, walked over every one of the 18 count bits.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ibox4_rcz_zerogate.strap").read())

DATA_ROWS = [
    ('013054.00', '400000.00 00 000000.00 00', 'BIT0  -> count 2^17'),
    ('013071.00', '20.00 00 000000.00 00',     'BIT13 -> count 2^4'),
    ('013075.00', '1.00 00 000000.00 00',      'BIT17 -> count 2^0'),
    ('005574.00', '123456.76 0B 064202.47 2E', 'I38XW3'),
    ('005600.00', '13054.00 00 000440.00 00',  'I38XW7 XW, (8)13054.0, 18, 0   -> BIT0, count 18'),
    ('005601.00', '5732.00 00 000000.00 00',   'I38XW8 XW, (8)5732.0, 0, 0     -> error table'),
]

CODE_ROWS = [
    ('005551.00', '5600.34 10', 'I382Z LX, $X14, I38XW7   check zero gating of RCZ'),
    ('005551.40', '5601.36 10', 'LX, $X15, I38XW8'),
    ('005552.00', '5553.75 D0', 'I3829 SVA, $X14, I3830'),
    ('005552.40', '5556.37 D0', 'SVA, $X15, I3831'),
    ('005553.00', '5574.01 03', 'LRI, $X0, (8)5574'),
    ('005553.40', '0.00 50',    'I3830 LC, $X0, 0   patched each pass'),
    ('005554.00', '13034.00 30','LV, $X0, I00Z'),
    ('005554.40', '20.06 00',   'RCZ, $X0'),
    ('005555.00', '13034.00 90','KV, $X0, I00Z'),
    ('005555.40', '5556.72 C2', 'BXE, $+1.0'),
    ('005556.00', '0.10 00',    'I3831 B, 0   listing "$B,0" -- refill when count not zero'),
    ('005556.40', '1.35 08',    'I3832 C-I, $X14, 1'),
    ('005557.00', '5561.30 42', 'BXCZ, I3833'),
    ('005557.40', '1.35 05',    'V+I, $X14, 1.0'),
    ('005560.00', '2.37 05',    'V+I, $X15, 2.0'),
    ('005560.40', '5552.10 00', 'B, I3829'),
    ('005561.00', '5562.10 00', 'I3833 B, $+1.0'),
]

if __name__ == "__main__":
    fails = check_rows(prog, DATA_ROWS, label="data")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
