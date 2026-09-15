#!/usr/bin/env python3
"""verify_ibox1_vpc_chain_listing.py -- IBOX-1 routine IBG39-IBG54
(programs/ibox1_vpc_chain.strap) against ja_ax1a pp.22-23.

V+C, the direct-index "add to value and count", one of the eight
modeled index operations a coverage screen found in zero suite programs
and a combined injection then confirmed.  Four tests, each manufacturing
two branch instructions out of its own result.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ibox1_vpc_chain.strap").read())

CODE_ROWS = [
    ('003725.00', '3752.02 10', 'IBG39 LX, $X1, IBG53   load index'),
    ('003725.40', '3751.42 D0', 'IBG40 V+C, $X1, IBEN7   add to value a half'),
    ('003726.00', '3744.43 30', 'SV, $X1, IBG47   diminish count by one'),
    ('003726.40', '6105.03 50', 'SC, $X1, ISTOY'),
    ('003727.00', '6105.02 30', 'LV, $X1, ISTOY'),
    ('003727.40', '6106.02 B0', 'V+, $X1, COM04'),
    ('003730.00', '3747.03 30', 'SV, $X1, IBG50   store values'),
    ('003730.40', '3744.42 30', 'LV, $X1, IBG47'),
    ('003731.00', '3751.42 D0', 'IBG41 V+C, $X1, IBEN7   + counts'),
    ('003731.40', '3743.43 30', 'SV, $X1, IBG45   into proper'),
    ('003732.00', '6105.03 50', 'SC, $X1, ISTOY'),
    ('003732.40', '6105.02 30', 'LV, $X1, ISTOY'),
    ('003733.00', '6106.02 B0', 'V+, $X1, COM04'),
    ('003733.40', '3745.03 30', 'SV, $X1, IBG48   areas + try'),
    ('003734.00', '3743.42 30', 'LV, $X1, IBG45'),
    ('003734.40', '3751.42 D0', 'IBG42 V+C, $X1, IBEN7   to branch thru.'),
    ('003735.00', '3743.03 30', 'SV, $X1, IBG44'),
    ('003735.40', '6105.03 50', 'SC, $X1, ISTOY'),
    ('003736.00', '6105.02 30', 'LV, $X1, ISTOY'),
    ('003736.40', '6106.02 B0', 'V+, $X1, COM04'),
    ('003737.00', '3746.03 30', 'SV, $X1, IBG49'),
    ('003737.40', '3743.02 30', 'LV, $X1, IBG44'),
    ('003740.00', '3751.42 D0', 'IBG43 V+C, $X1, IBEN7'),
    ('003740.40', '3744.03 30', 'SV, $X1, IBG46'),
    ('003741.00', '6105.03 50', 'SC, $X1, ISTOY'),
    ('003741.40', '6105.02 30', 'LV, $X1, ISTOY'),
    ('003742.00', '6106.02 B0', 'V+, $X1, COM04'),
    ('003742.40', '3750.03 30', 'SV, $X1, IBG51'),
    ('003743.00', '3743.00 00', 'IBG44 BE, $   value  -> BD, IBG47'),
    ('003743.40', '3743.40 00', 'IBG45 BE, $   test   -> BD, IBG46'),
    ('003744.00', '3744.00 00', 'IBG46 BE, $   area.  -> BD, IBG48'),
    ('003744.40', '3744.40 00', 'IBG47 BE, $   area.  -> BD, IBG45'),
    ('003745.00', '3745.04 00', 'IBG48 BD, $   count  -> BE, IBG51'),
    ('003745.40', '3745.44 00', 'BD, $'),
    ('003746.00', '3746.04 00', 'IBG49 BD, $   test   -> BE, IBG50'),
    ('003746.40', '3746.44 00', 'BD, $'),
    ('003747.00', '3747.04 00', 'IBG50 BD, $   area.  -> BE, IBG52'),
    ('003747.40', '3747.44 00', 'BD, $'),
    ('003750.00', '3750.04 00', 'IBG51 BD, $          -> BE, IBG49'),
    ('003750.40', '3750.44 00', 'BD, $'),
    ('003751.00', '3753.10 00', 'IBG52 B, IBG54'),
    ('003751.40', '0.40 00',    'IBEN7 BE, 0.32   common value'),
    ('003753.00', '777777.30 00', 'IBG54 NOP, (8)777777.0'),
    ('003753.40', '777777.30 00', 'NOP, (8)777777.0'),
]

DATA_ROWS = [
    ('003752.00', '3743.04 00 077240.00 00', 'IBG53 XW, IBG44+(8)0.04, (8)3752, 0   common XW'),
]

if __name__ == "__main__":
    fails = check_rows(prog, CODE_ROWS, label="code")
    fails += check_rows(prog, DATA_ROWS, label="data")
    finish(fails)
