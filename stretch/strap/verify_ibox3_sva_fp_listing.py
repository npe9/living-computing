#!/usr/bin/env python3
"""verify_ibox3_sva_fp_listing.py -- IBOX-3 routine 1222 blocks
I2231-I2233 (programs/ibox3_sva_fp.strap) against jb_ax3a p.144 (code)
and p.165 (the 1222 constants).

The listing's own SVA test, and the sub-block that pins the address
field WIDTH -- which the Reference Manual does not state.  p.29 gives
"18, 19, or 24 bits" and attributes 18 only to TRANSMIT/SWAP second
half-words; the deck's error messages say a FLOATING POINT target that
"STORES BIT 18" is broken, while three pages earlier a DIRECT INDEX
target that "FAILS TO STORE BIT 18" is broken.  FP's address is 18 bits
(a/b/c modifiers at 18-20); every other half-length format has 19.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ibox3_sva_fp.strap").read())

DATA_ROWS = [
    ('031304.00', '0.00 60', 'I22K2 L(N), 0.0   FP load'),
    ('031304.40', '0.30 00', 'NOP'),
    ('031305.00', '777777.00 00 000000.00 00', 'I22K3A XW, (8)777777.0, 0, 0   bits 0-17 ones'),
    ('031306.00', '0.77 00 000000.00 00', 'I22K3B XW, (8)0.77, 0, 0   bits 18-23 ones'),
    ('031307.00', '0.40 00 000000.00 00', 'I22K3C XW, 0.32, 0, 0   bit 18'),
    ('031310.00', '0.37 00 000000.00 00', 'I22K3D XW, 0.31, 0, 0   bits 19-23'),
    ('031311.00', '0.01 00 000000.00 00', 'I22K3E XW, 0.01, 0, 0   bit 23'),
]

CODE_ROWS = [
    ('030324.00', '31305.00 10', 'I2231 LX, $X0, I22K3A'),
    ('030324.40', '31304.02 10', 'LX, $X1, I22K2'),
    ('030325.00', '31322.03 10', 'SX, $X1, I22WRK'),
    ('030325.40', '31322.01 D0', 'SVA, $X0, I22WRK'),
    ('030326.00', '31322.04 10', 'LX, $X2, I22WRK'),
    ('030326.40', '31306.04 90', 'KV, $X2, I22K3B'),
    ('030327.00', '30331.33 42', 'BXH, $+2.0'),
    ('030327.40', '1310.00 80', 'SIC, SEN'),
    ('030330.00', '1304.10 00', 'B, SERS   fails to store any bits in 0-17'),
    ('030330.40', '30333.50 00', 'B, I2232'),
    ('030331.00', '31305.04 90', 'KV, $X2, I22K3A'),
    ('030331.40', '30332.72 42', 'BXL, $+1.0'),
    ('030332.00', '30333.50 00', 'B, $+1.32'),
    ('030332.40', '1310.00 80', 'SIC, SEN'),
    ('030333.00', '1304.10 00', 'B, SERS   fails to store all bits in 0-17'),
    ('030333.40', '31322.03 10', 'I2232 SX, $X1, I22WRK'),
    ('030334.00', '31307.00 10', 'LX, $X0, I22K3C'),
    ('030334.40', '31322.01 D0', 'SVA, $X0, I22WRK'),
    ('030335.00', '31322.04 10', 'LX, $X2, I22WRK'),
    ('030335.40', '31306.04 90', 'KV, $X2, I22K3B'),
    ('030336.00', '30337.33 42', 'BXH, $+1.0'),
    ('030336.40', '30340.50 00', 'B, $+2.0'),
    ('030337.00', '1310.00 80', 'SIC, SEN'),
    ('030337.40', '1304.10 00', 'B, SERS   picks up some bits in 0-17'),
    ('030340.00', '30342.50 00', 'B, I2233'),
    ('030340.40', '31310.04 90', 'KV, $X2, I22K3D'),
    ('030341.00', '30342.72 42', 'BXL, $+1.32'),
    ('030341.40', '1310.00 80', 'SIC, SEN'),
    ('030342.00', '1304.10 00', 'B, SERS   stores bit 18'),
    ('030342.40', '31322.03 10', 'I2233 SX, $X1, I22WRK'),
    ('030343.00', '31310.00 10', 'LX, $X0, I22K3D'),
    ('030343.40', '31322.01 D0', 'SVA, $X0, I22WRK'),
    ('030344.00', '31322.04 10', 'LX, $X2, I22WRK'),
    ('030344.40', '31310.04 90', 'KV, $X2, I22K3D'),
    ('030345.00', '30347.32 42', 'BXL, $+2.0'),
    ('030345.40', '1310.00 80', 'SIC, SEN'),
    ('030346.00', '1304.10 00', 'B, SERS   picks up some bits in 0-18'),
    ('030346.40', '30351.10 00', 'B, I2234'),
    ('030347.00', '31311.04 90', 'KV, $X2, I22K3E'),
    ('030347.40', '30351.32 42', 'BXL, $+1.32'),
    ('030350.00', '1310.00 80', 'SIC, SEN'),
    ('030350.40', '1304.10 00', 'B, SERS   stores some bits in 19-23'),
]

if __name__ == "__main__":
    fails = check_rows(prog, DATA_ROWS, label="data")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
