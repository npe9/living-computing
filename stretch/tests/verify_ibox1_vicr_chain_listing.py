#!/usr/bin/env python3
"""verify_ibox1_vicr_chain_listing.py -- IBOX-1 routine IBP30-IBP53
(../decks/ibox1_vicr_chain.strap) against ja_ax1a p.37.

V-ICR ("add to value immediate, count, + refill"), one of the eight
modeled index operations a coverage screen found in zero suite programs
and a combined injection then confirmed.  Three tests: a V-ICR that
refills straight over a pair of live instructions, one that must not
refill, and one that must.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ibox1_vicr_chain.strap").read())

CODE_ROWS = [
    ('004614.00', '4620.02 10', 'IBP30 LX, $X1, IBPA3   set up XW'),
    ('004614.40', '2.03 0F',    'V-ICR, $X1, 2.0   should refill'),
    ('004615.00', '4616.03 10', 'SX, $X1, IBP31'),
    ('004615.40', '0.30 00',    'NOP, 0.0'),
    ('004616.00', '4616.00 00', 'IBP31 BE, $   becomes NOP, (8)525252.0'),
    ('004616.40', '4616.40 00', 'BE, $   becomes B, IBP33'),
    ('004617.00', '4617.04 00', 'IBP32 BD, $   hang up'),
    ('004621.00', '525252.30 00', 'IBPA4 NOP, (8)525252.0'),
    ('004621.40', '4622.10 00', 'B, IBP33   refill XW'),
    ('004622.00', '4650.02 10', 'IBP33 LX, $X1, IBPA5   set up XW'),
    ('004622.40', '2.43 0F',    'IBP34 V-ICR, $X1, 2.32   shouldnt refill V-2.32'),
    ('004623.00', '4640.03 30', 'IBP35 SV, $X1, IBP46   store value'),
    ('004623.40', '6105.03 50', 'SC, $X1, ISTOY'),
    ('004624.00', '6105.02 30', 'LV, $X1, ISTOY'),
    ('004624.40', '4647.03 30', 'IBP36 SV, $X1, IBPSTO'),
    ('004625.00', '6105.03 70', 'SR, $X1, ISTOY'),
    ('004625.40', '6105.02 30', 'LV, $X1, ISTOY'),
    ('004626.00', '6106.02 B0', 'V+, $X1, COM04'),
    ('004626.40', '6104.03 30', 'IBP37 SV, $X1, ISTOZ'),
    ('004627.00', '6104.02 30', 'LV, $X1, ISTOZ'),
    ('004627.40', '4647.02 B0', 'IBP38 V+, $X1, IBPSTO   add C+R'),
    ('004630.00', '4646.03 30', 'IBP39 SV, $X1, IBP52   store C+R'),
    ('004630.40', '4640.02 30', 'LV, $X1, IBP46'),
    ('004631.00', '0.30 00',    'NOP, 0.0'),
    ('004631.40', '0.43 0F',    'IBP40 V-ICR, $X1, 0.32   should refill'),
    ('004632.00', '4644.03 30', 'IBP41 SV, $X1, IBP50   store value'),
    ('004632.40', '6105.03 50', 'SC, $X1, ISTOY'),
    ('004633.00', '6105.02 30', 'LV, $X1, ISTOY'),
    ('004633.40', '4647.03 30', 'IBP42 SV, $X1, IBPSTO'),
    ('004634.00', '6105.03 70', 'SR, $X1, ISTOY'),
    ('004634.40', '6105.02 30', 'LV, $X1, ISTOY'),
    ('004635.00', '6106.02 B0', 'V+, $X1, COM04'),
    ('004635.40', '6104.03 30', 'IBP43 SV, $X1, ISTOZ'),
    ('004636.00', '6104.02 10', 'LX, $X1, ISTOZ'),
    ('004636.40', '4647.02 B0', 'IBP44 V+, $X1, IBPSTO   add C+R'),
    ('004637.00', '4643.03 30', 'IBP45 SV, $X1, IBP49   store C+R'),
    ('004637.40', '6104.02 10', 'LX, $X1, ISTOZ'),
    ('004640.00', '0.00 00',    'IBP46 BE, 0   becomes BD, IBP49'),
    ('004640.40', '4640.44 00', 'BD, $'),
    ('004641.00', '0.00 00',    'IBP47 BE, 0'),
    ('004641.40', '4641.44 00', 'BD, $'),
    ('004642.00', '0.00 00',    'IBP48 BE, 0'),
    ('004642.40', '4642.44 00', 'BD, $'),
    ('004643.00', '0.00 00',    'IBP49 BE, 0   becomes BD, IBP50'),
    ('004643.40', '4643.44 00', 'BD, $'),
    ('004644.00', '0.00 00',    'IBP50 BE, 0   becomes BD, IBP52'),
    ('004644.40', '4644.44 00', 'BD, $'),
    ('004645.00', '0.00 00',    'IBP51 BE, 0'),
    ('004645.40', '4645.44 00', 'BD, $'),
    ('004646.00', '0.00 00',    'IBP52 BE, 0   becomes BD, IBP53'),
    ('004646.40', '4646.44 00', 'BD, $'),
    ('004647.00', '0.00 00',    'IBPSTO BE, 0   store area'),
    ('004647.40', '4647.44 00', 'BD, $'),
    ('004652.00', '777777.70 00', 'IBP53 VF, (8)777777.70   executed as NOP,-.32'),
    ('004652.40', '777777.70 00', 'VF, 262143.56   executed as NOP,-.32'),
]

DATA_ROWS = [
    ('004620.00', '4620.42 00 000020.11 91', 'IBPA3 XW, IBPA3+0.34, 1, IBPA4'),
    ('004650.00', '4645.44 00 000040.11 A9', 'IBPA5 XW, IBP51+0.36, 2, IBPA6'),
    ('004651.00', '4646.04 00 000100.11 A0', 'IBPA6 XW, IBP52+0.04, 4, IBP46'),
]

if __name__ == "__main__":
    fails = check_rows(prog, CODE_ROWS, label="code")
    fails += check_rows(prog, DATA_ROWS, label="data")
    finish(fails)
