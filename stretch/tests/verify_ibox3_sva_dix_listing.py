#!/usr/bin/env python3
"""verify_ibox3_sva_dix_listing.py -- IBOX-3 routine 1222 blocks
I2228-I2230 (../decks/ibox3_sva_dix.strap) against jb_ax3a p.143 (code)
and p.165 (the 1222 constants).

The 19-bit half of SVA's width rule.  Same six checks as the floating
point block (ibox3_sva_fp) with two comparisons reversed: after storing
a lone bit 18, an FP target must compare LOW against I22K3D and a
direct index target must compare HIGH.  The listing says it in words
too -- "STORES BIT 18" is the FP failure, "FAILS TO STORE BIT 18" is
this one.

The target here is $X3, word 19: index core storage, not ordinary
memory.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ibox3_sva_dix.strap").read())

DATA_ROWS = [
    ('031305.00', '777777.00 00 000000.00 00', 'I22K3A XW, (8)777777.0, 0, 0'),
    ('031306.00', '0.77 00 000000.00 00', 'I22K3B XW, (8)0.77, 0, 0'),
    ('031307.00', '0.40 00 000000.00 00', 'I22K3C XW, 0.32, 0, 0'),
    ('031310.00', '0.37 00 000000.00 00', 'I22K3D XW, 0.31, 0, 0'),
    ('031311.00', '0.01 00 000000.00 00', 'I22K3E XW, 0.01, 0, 0'),
    ('031314.00', '0.00 30', 'I22K4 LV, $X0, 0.0   direct index template'),
    ('031314.40', '0.30 00', 'NOP'),
]

CODE_ROWS = [
    ('030273.00', '31305.00 10', 'I2228 LX, $X0, I22K3A'),
    ('030273.40', '31314.02 10', 'LX, $X1, I22K4'),
    ('030274.00', '23.03 10', 'SX, $X1, $X3'),
    ('030274.40', '23.01 D0', 'SVA, $X0, $X3'),
    ('030275.00', '23.04 10', 'LX, $X2, $X3'),
    ('030275.40', '31306.04 90', 'KV, $X2, I22K3B'),
    ('030276.00', '30300.33 42', 'BXH, $+2.0'),
    ('030276.40', '1310.00 80', 'SIC, SEN'),
    ('030277.00', '1304.10 00', 'B, SERS   fails to store any bits in 0-17'),
    ('030277.40', '30302.50 00', 'B, I2229'),
    ('030300.00', '31305.04 90', 'KV, $X2, I22K3A'),
    ('030300.40', '30301.72 42', 'BXL, $+1.0'),
    ('030301.00', '30302.50 00', 'B, $+1.32'),
    ('030301.40', '1310.00 80', 'SIC, SEN'),
    ('030302.00', '1304.10 00', 'B, SERS   fails to store all bits in 0-17'),
    ('030302.40', '23.03 10', 'I2229 SX, $X1, $X3'),
    ('030303.00', '31307.00 10', 'LX, $X0, I22K3C'),
    ('030303.40', '23.01 D0', 'SVA, $X0, $X3'),
    ('030304.00', '23.04 10', 'LX, $X2, $X3'),
    ('030304.40', '31306.04 90', 'KV, $X2, I22K3B'),
    ('030305.00', '30306.33 42', 'BXH, $+1.0'),
    ('030305.40', '30307.50 00', 'B, $+2.0'),
    ('030306.00', '1310.00 80', 'SIC, SEN'),
    ('030306.40', '1304.10 00', 'B, SERS   picks up some bits in 0-17'),
    ('030307.00', '30311.50 00', 'B, I2230'),
    ('030307.40', '31310.04 90', 'KV, $X2, I22K3D'),
    ('030310.00', '30311.73 42', 'BXH, $+1.32'),
    ('030310.40', '1310.00 80', 'SIC, SEN'),
    ('030311.00', '1304.10 00', 'B, SERS   fails to store bit 18'),
    ('030311.40', '23.03 10', 'I2230 SX, $X1, $X3'),
    ('030312.00', '31310.00 10', 'LX, $X0, I22K3D'),
    ('030312.40', '23.01 D0', 'SVA, $X0, $X3'),
    ('030313.00', '23.04 10', 'LX, $X2, $X3'),
    ('030313.40', '31307.04 90', 'KV, $X2, I22K3C'),
    ('030314.00', '30316.32 42', 'BXL, $+2.0'),
    ('030314.40', '1310.00 80', 'SIC, SEN'),
    ('030315.00', '1304.10 00', 'B, SERS   picks up some bits in 0-18'),
    ('030315.40', '30320.10 00', 'B, I2230A'),
    ('030316.00', '31311.04 90', 'KV, $X2, I22K3E'),
    ('030316.40', '30320.32 42', 'BXL, $+1.32'),
    ('030317.00', '1310.00 80', 'SIC, SEN'),
    ('030317.40', '1304.10 00', 'B, SERS   store some bits in 19-23'),
]

if __name__ == "__main__":
    fails = check_rows(prog, DATA_ROWS, label="data")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
