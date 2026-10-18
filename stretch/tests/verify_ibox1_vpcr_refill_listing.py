#!/usr/bin/env python3
"""verify_ibox1_vpcr_refill_listing.py -- IBOX-1 routine IBG55-IBG64
(../decks/ibox1_vpcr_refill.strap) against ja_ax1a p.23.

V+CR's first test, the DIRECT-INDEX add-to-value-count-and-refill.  One
V+CR drives the count to zero and must refill; the three stores that
follow check the refilled value, count and refill separately.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ibox1_vpcr_refill.strap").read())

CODE_ROWS = [
    ('003754.00', '3766.02 10', 'IBG55 LX, $X1, IBG63   LX with count 1 = one'),
    ('003754.40', '3763.42 F0', 'IBG56 V+CR, $X1, IBG59   should cause refill'),
    ('003755.00', '3762.43 30', 'SV, $X1, IBG57   if not SV will be B, IBG63'),
    ('003755.40', '6105.03 50', 'SC, $X1, ISTOY'),
    ('003756.00', '6105.02 30', 'LV, $X1, ISTOY'),
    ('003756.40', '6106.02 B0', 'V+, $X1, COM04'),
    ('003757.00', '3764.43 30', 'SV, $X1, IBG61   which will cause hang up'),
    ('003757.40', '0.30 00',    'NOP, 0.0'),
    ('003760.00', '6105.03 70', 'SR, $X1, ISTOY'),
    ('003760.40', '6105.02 30', 'LV, $X1, ISTOY'),
    ('003761.00', '6106.02 B0', 'V+, $X1, COM04'),
    ('003761.40', '3763.03 30', 'SV, $X1, IBG58   to be stored at IBG57'),
    ('003762.00', '3762.42 30', 'LV, $X1, IBG57'),
    ('003762.40', '3762.50 00', 'IBG57 B, $   should become BD, IBG61'),
    ('003763.00', '3763.10 00', 'IBG58 B, $   should become BD, IBG64'),
    ('003763.40', '0.04 00',    'IBG59 BD, (8)0.0   the V+CR operand, value 4'),
    ('003764.00', '777777.50 00', 'IBG60 VF, (8)777777.50'),
    ('003764.40', '3764.50 00', 'IBG61 B, $   should become BD, IBG58'),
    ('003767.00', '777777.30 00', 'IBG64 NOP, (8)777777.0'),
    ('003767.40', '777777.30 00', 'NOP, (8)777777.0'),
]

DATA_ROWS = [
    ('003765.00', '3764.44 00 077460.07 F7', 'IBG62 XW, IBG61+(8)0.04, (8)3763, IBG64   refill XW'),
    ('003766.00', '3766.04 00 000020.07 F5', 'IBG63 XW, IBG63+(8)0.04, 1, IBG62   initial XW'),
]

if __name__ == "__main__":
    fails = check_rows(prog, CODE_ROWS, label="code")
    fails += check_rows(prog, DATA_ROWS, label="data")
    finish(fails)
