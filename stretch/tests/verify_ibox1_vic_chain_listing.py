#!/usr/bin/env python3
"""verify_ibox1_vic_chain_listing.py -- IBOX-1 routine IBP14A-IBP29
(../decks/ibox1_vic_chain.strap) against ja_ax1a pp.36-37.

V-IC ("add to value immediate + count"), one of the eight modeled index
operations a coverage screen found in zero suite programs.  Four steps,
each manufacturing two branch instructions out of its own result.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ibox1_vic_chain.strap").read())

CODE_ROWS = [
    ('004565.00', '4612.02 10', 'IBP14A LX, $X1, IBPA2   set up XW'),
    ('004565.40', '0.43 0E',    'IBP15 V-IC, $X1, 0.32   V-.02, C-1.0'),
    ('004566.00', '4611.03 30', 'SV, $X1, IBP28   store value'),
    ('004566.40', '6105.03 50', 'SC, $X1, ISTOY'),
    ('004567.00', '6105.02 30', 'LV, $X1, ISTOY'),
    ('004567.40', '6106.02 B0', 'V+, $X1, COM04'),
    ('004570.00', '4604.03 30', 'SV, $X1, IBP19'),
    ('004570.40', '4611.02 30', 'LV, $X1, IBP28'),
    ('004571.00', '2.03 0E',    'IBP16 V-IC, $X1, 2.0   V-2.0, C-1.0'),
    ('004571.40', '4610.43 30', 'SV, $X1, IBP27   store value'),
    ('004572.00', '6105.03 50', 'SC, $X1, ISTOY'),
    ('004572.40', '6105.02 30', 'LV, $X1, ISTOY'),
    ('004573.00', '6106.02 B0', 'V+, $X1, COM04'),
    ('004573.40', '4610.03 30', 'SV, $X1, IBP26'),
    ('004574.00', '4610.42 30', 'LV, $X1, IBP27'),
    ('004574.40', '777776.03 0E', 'IBP17 V-IC, $X1, (8)777776.0   C-1.0'),
    ('004575.00', '777777.03 05', 'V+I, $X1, (8)777777.0   V+1.0'),
    ('004575.40', '4606.43 30', 'SV, $X1, IBP23   store value'),
    ('004576.00', '6105.03 50', 'SC, $X1, ISTOY'),
    ('004576.40', '6105.02 30', 'LV, $X1, ISTOY'),
    ('004577.00', '6106.02 B0', 'V+, $X1, COM04'),
    ('004577.40', '4607.03 30', 'SV, $X1, IBP24'),
    ('004600.00', '4606.42 30', 'LV, $X1, IBP23'),
    ('004600.40', '2.03 0E',    'IBP18 V-IC, $X1, 2.0   V-2.0, C-1.0'),
    ('004601.00', '4607.43 30', 'SV, $X1, IBP25   store value'),
    ('004601.40', '6105.03 50', 'SC, $X1, ISTOY'),
    ('004602.00', '6105.02 30', 'LV, $X1, ISTOY'),
    ('004602.40', '6106.02 B0', 'V+, $X1, COM04'),
    ('004603.00', '4606.03 30', 'SV, $X1, IBP22'),
    ('004603.40', '0.30 00',    'NOP, 0.0'),
    ('004604.00', '4604.10 00', 'IBP19 B, $   becomes a branch to IBP26'),
    ('004604.40', '0.30 00',    'CNOP'),
    ('004605.00', '4611.10 00', 'IBP20 B, IBP28   branch to value test'),
    ('004605.40', '4613.10 00', 'IBP21 B, IBP29   branch out'),
    ('004606.00', '4606.10 00', 'IBP22 B, $   becomes a branch to IBP20'),
    ('004606.40', '4606.50 00', 'IBP23 B, $   becomes a branch to IBP25'),
    ('004607.00', '4607.10 00', 'IBP24 B, $   becomes a branch to IBP22'),
    ('004607.40', '4607.50 00', 'IBP25 B, $   becomes a branch to IBP21'),
    ('004610.00', '4610.10 00', 'IBP26 B, $   becomes a branch to IBP24'),
    ('004610.40', '4610.50 00', 'IBP27 B, $   becomes a branch to IBP23'),
    ('004611.00', '4611.10 00', 'IBP28 B, $   becomes a branch to IBP27'),
    ('004613.00', '777777.70 00', 'IBP29 VF, (8)777777.70   executed as NOP,-.32'),
    ('004613.40', '777777.70 00', 'VF, (8)777777.70   executed as NOP,-.32'),
]

DATA_ROWS = [
    ('004612.00', '4611.04 00 114237.77 FF', 'IBPA2 XW, IBP28+(8)0.04, (8)4611, -1'),
]

if __name__ == "__main__":
    fails = check_rows(prog, CODE_ROWS, label="code")
    fails += check_rows(prog, DATA_ROWS, label="data")
    finish(fails)
