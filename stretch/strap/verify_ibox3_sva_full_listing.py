#!/usr/bin/env python3
"""verify_ibox3_sva_full_listing.py -- IBOX-3 routine 1222 section I2221
(programs/ibox3_sva_full.strap) against jb_ax3a pp.139-140 (code) and
p.165 (the 1222 constants).

The 24-bit third of SVA's width rule, and the one the other two blocks
cannot reach: their templates are half-length (I22K2 op 0x60, I22K4 op
0x30), so nothing in the suite drove dirIndexOp's full-word arm until
this block.  I22K1 is "$L%BU,0" -- a full-word VFL Load, bits 24-27 =
1000, the length tag p.140 names as case 4, "STORE 24 BITS".

Two data bits, 22 and 23, both above a 19-bit field, each stored to all
three memories: I22WRK (external), $R (word 9, internal) and $X1 itself
(word 17, index core storage).
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ibox3_sva_full.strap").read())

DATA_ROWS = [
    ('031301.00', '0.02 80 000000.00 00', 'IBIT22 XW, -(8)0.02, 0, 0'),
    ('031302.00', '0.01 80 000000.00 00', 'IBIT23 XW, -(8)0.01, 0, 0'),
    ('031303.00', '0.00 80 000000.20 50', 'I22K1 L, 0.0   full-word VFL template'),
]

CODE_ROWS = [
    ('030167.00', '31301.00 10', 'I2221 LX, $X0, IBIT22   SVA to 3 mems, data bit 22'),
    ('030167.40', '31303.02 10', 'LX, $X1, I22K1'),
    ('030170.00', '31322.03 10', 'SX, $X1, I22WRK'),
    ('030170.40', '31322.01 D0', 'SVA, $X0, I22WRK'),
    ('030171.00', '11.03 10', 'SX, $X1, $R'),
    ('030171.40', '11.01 D0', 'SVA, $X0, $R'),
    ('030172.00', '21.01 D0', 'SVA, $X0, $X1'),
    ('030172.40', '0.30 00', 'NOP'),
    ('030173.00', '0.30 00', 'NOP'),
    ('030173.40', '0.30 00', 'NOP'),
    ('030174.00', '31322.00 90', 'KV, $X0, I22WRK'),
    ('030174.40', '30176.32 C2', 'BXE, $+1.32'),
    ('030175.00', '1310.00 80', 'SIC, SEN'),
    ('030175.40', '1304.10 00', 'B, SERS   SVA above bit to ext mem failed'),
    ('030176.00', '11.00 90', 'KV, $X0, $R'),
    ('030176.40', '30200.32 C2', 'BXE, $+1.32'),
    ('030177.00', '1310.00 80', 'SIC, SEN'),
    ('030177.40', '1304.10 00', 'B, SERS   SVA above bit to int mem failed'),
    ('030200.00', '21.00 90', 'KV, $X0, $X1'),
    ('030200.40', '30202.32 C2', 'BXE, $+1.32'),
    ('030201.00', '1310.00 80', 'SIC, SEN'),
    ('030201.40', '1304.10 00', 'B, SERS   SVA above bit to ix core stg failed'),
    ('030202.00', '31302.00 10', 'LX, $X0, IBIT23   SVA to 3 mems, data bit 23'),
    ('030202.40', '31303.02 10', 'LX, $X1, I22K1'),
    ('030203.00', '31322.03 10', 'SX, $X1, I22WRK'),
    ('030203.40', '31322.01 D0', 'SVA, $X0, I22WRK'),
    ('030204.00', '11.03 10', 'SX, $X1, $R'),
    ('030204.40', '11.01 D0', 'SVA, $X0, $R'),
    ('030205.00', '21.01 D0', 'SVA, $X0, $X1'),
    ('030205.40', '0.30 00', 'NOP'),
    ('030206.00', '0.30 00', 'NOP'),
    ('030206.40', '0.30 00', 'NOP'),
    ('030207.00', '31322.00 90', 'KV, $X0, I22WRK'),
    ('030207.40', '30211.32 C2', 'BXE, $+1.32'),
    ('030210.00', '1310.00 80', 'SIC, SEN'),
    ('030210.40', '1304.10 00', 'B, SERS   SVA above bit to ext mem failed'),
    ('030211.00', '11.00 90', 'KV, $X0, $R'),
    ('030211.40', '30213.32 C2', 'BXE, $+1.32'),
    ('030212.00', '1310.00 80', 'SIC, SEN'),
    ('030212.40', '1304.10 00', 'B, SERS   SVA above bit to int mem failed'),
    ('030213.00', '21.00 90', 'KV, $X0, $X1'),
    ('030213.40', '30215.32 C2', 'BXE, $+1.32'),
    ('030214.00', '1310.00 80', 'SIC, SEN'),
    ('030214.40', '1304.10 00', 'B, SERS   SVA above bit to ix core stg failed'),
]

if __name__ == "__main__":
    fails = check_rows(prog, DATA_ROWS, label="data")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
