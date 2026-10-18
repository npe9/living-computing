#!/usr/bin/env python3
"""verify_ibox3_lr_listing.py -- IBOX-3 routine 1230 blocks I301/I302
(../decks/ibox3_lr.strap) against jb_ax3a p.200 (code) and p.213/214
(the BIT table).

LR was the last of the nine index operations a combined injection
showed the suite could not reach, and it was recorded as BLOCKED
because I-Box 1's LR test round-trips the refill through the indicator
register.  I-Box 3 tests the same operation with no indicator register
in it at all: a tape's test for an operation is not the only test.

Each block runs the same LR three times -- from external memory, from
index core storage ($X1, word 17) and from internal memory ($R, word 9)
-- and compares each result against a reference SR put into $X2.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ibox3_lr.strap").read())

DATA_ROWS = [
    ('033351.00', '2.00 00 000000.00 00', 'BIT16 XW, (8)2.00, 0, 0'),
    ('033352.00', '1.00 00 000000.00 00', 'BIT17 XW, (8)1.00, 0, 0'),
    ('033427.00', '0.00 00 000000.00 02', 'BIT62 XW, 0, 0, 2'),
    ('033430.00', '0.00 00 000000.00 01', 'BIT63 XW, 0, 0, 1'),
]

CODE_ROWS = [
    ('032636.40', '33430.00 10', 'I301 LX, $X0, BIT63   operand used in LR'),
    ('032637.00', '32637.44 00', 'BD, $+.32'),
    ('032637.40', '21.01 70', 'SR, $X0, $X1   place in index storage'),
    ('032640.00', '11.01 70', 'SR, $X0, $R   place in internal reg'),
    ('032640.40', '22.01 70', 'SR, $X0, $X2   set up X2 for KV'),
    ('032641.00', '33352.00 70', 'LR, $X0, BIT17'),
    ('032641.40', '33301.01 70', 'SR, $X0, I30ST'),
    ('032642.00', '33301.04 90', 'KV, $X2, I30ST'),
    ('032642.40', '1310.00 80', 'SIC, SEN   failed to load bit 63'),
    ('032643.00', '1304.32 C0', 'BZXE, SERS   from ext mem'),
    ('032643.40', '21.00 70', 'LR, $X0, $X1'),
    ('032644.00', '33301.01 70', 'SR, $X0, I30ST'),
    ('032644.40', '33301.04 90', 'KV, $X2, I30ST'),
    ('032645.00', '1310.00 80', 'SIC, SEN   failed to load bit 63'),
    ('032645.40', '1304.32 C0', 'BZXE, SERS   from index storage'),
    ('032646.00', '11.00 70', 'LR, $X0, $R'),
    ('032646.40', '33301.01 70', 'SR, $X0, I30ST'),
    ('032647.00', '33301.04 90', 'KV, $X2, I30ST'),
    ('032647.40', '1310.00 80', 'SIC, SEN   failed to load bit 63'),
    ('032650.00', '1304.32 C0', 'BZXE, SERS   from internal reg'),
    ('032650.40', '33427.00 10', 'I302 LX, $X0, BIT62   operand used in LR'),
    ('032651.00', '21.01 70', 'SR, $X0, $X1   place in index storage'),
    ('032651.40', '11.01 70', 'SR, $X0, $R   place in internal reg'),
    ('032652.00', '22.01 70', 'SR, $X0, $X2   set up X2 for KV'),
    ('032652.40', '33351.00 70', 'LR, $X0, BIT16'),
    ('032653.00', '33301.01 70', 'SR, $X0, I30ST'),
    ('032653.40', '33301.04 90', 'KV, $X2, I30ST'),
    ('032654.00', '1310.00 80', 'SIC, SEN   failed to load bit 62'),
    ('032654.40', '1304.32 C0', 'BZXE, SERS   from ext mem'),
    ('032655.00', '21.00 70', 'LR, $X0, $X1'),
    ('032655.40', '33301.01 70', 'SR, $X0, I30ST'),
    ('032656.00', '33301.04 90', 'KV, $X2, I30ST'),
    ('032656.40', '1310.00 80', 'SIC, SEN   failed to load bit 62'),
    ('032657.00', '1304.32 C0', 'BZXE, SERS   from index storage'),
    ('032657.40', '11.00 70', 'LR, $X0, $R'),
    ('032660.00', '33301.01 70', 'SR, $X0, I30ST'),
    ('032660.40', '33301.04 90', 'KV, $X2, I30ST'),
    ('032661.00', '1310.00 80', 'SIC, SEN   failed to load bit 62'),
    ('032661.40', '1304.32 C0', 'BZXE, SERS   from internal reg'),
]

if __name__ == "__main__":
    fails = check_rows(prog, DATA_ROWS, label="data")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
