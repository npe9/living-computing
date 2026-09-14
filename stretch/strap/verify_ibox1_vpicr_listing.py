#!/usr/bin/env python3
"""verify_ibox1_vpicr_listing.py -- IBOX-1 routine IBN-IBN11
(programs/ibox1_vpicr.strap) against ja_ax1a p.35 (code) and p.34 (the
constants at 004512.00-004523.00).

Chosen by measurement: V+ICR's REFILL path was one of the five index
operations still shown unreachable.

The first test refills and stores the refilled word over IBN1, where it
is EXECUTED as two instructions ("NOP,0" then "BD,IBN3").  The second
test does not refill and checks the value, count and refill fields
separately, each by manufacturing a different branch.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ibox1_vpicr.strap").read())

DATA_ROWS = [
    ('004512.00', '4523.44 00 000020.11 4F', 'IBM61 XW, IBN+.4, 1, IBM70'),
    ('004513.00', '4535.44 00 000040.11 66', 'IBM62 XW, IBN4+.36, 2, IBN9'),
    ('004514.00', '0.00 00 000000.00 00', 'IBM63 XW, 0,0,0   temp IX wd storage'),
    ('004515.00', '0.00 00 000000.00 00', 'IBM64 XW'),
    ('004516.00', '0.00 00 000000.00 00', 'IBM65 XW'),
    ('004517.00', '0.30 00', 'IBM70 NOP, 0'),
    ('004517.40', '4527.44 00', 'BD, IBN3'),
    ('004520.00', '0.00 00', 'IBM71 BE, 0   count storage area'),
    ('004520.40', '0.00 00', 'IBM72 BE, 0   refill storage area'),
    ('004521.00', '0.00 00', 'IBM73 BE, 0   temp V storage'),
    ('004521.40', '0.00 00', 'IBM74 BE, 0   temp C storage'),
    ('004522.00', '0.00 00', 'IBM75 BE, 0   temp R storage'),
    ('004522.40', '4542.44+', 'IBM76 VF, IBN8+(8).04   dummy address'),
    ('004523.00', '1.04+', 'IBM77 VF, 1.4   one word and 4 bits'),
]

CODE_ROWS = [
    ('004523.40', '4512.02 10', 'IBN LX, $X1, IBM61   start V+ICR tests'),
    ('004524.00', '2.03 07', 'V+ICR, $X1, 2.0   V was IBN+.4, C was 1, R was IBM70'),
    ('004524.40', '4526.03 10', 'SX, $X1, IBN1   IBN1 should now be two valid op'),
    ('004525.00', '0.30 00', 'NOP, 0   space for store close to'),
    ('004525.40', '0.30 00', 'CNOP, 0   instruct fetch interlock'),
    ('004526.00', '4526.00 00', 'IBN1 BE, $   becomes NOP,0'),
    ('004526.40', '4526.40 00', 'BE, $   becomes BD,IBN3'),
    ('004527.00', '4527.04 00', 'IBN2 BD, $'),
    ('004527.40', '4513.02 10', 'IBN3 LX, $X1, IBM62   start next test'),
    ('004530.00', '2.03 07', 'V+ICR, $X1, 2.0'),
    ('004530.40', '4514.03 10', 'SX, $X1, IBM63'),
    ('004531.00', '4521.03 30', 'SV, $X1, IBM73   temp storage V is'),
    ('004531.40', '4536.43 30', 'SV, $X1, IBN5'),
    ('004532.00', '6105.03 50', 'SC, $X1, ISTOY'),
    ('004532.40', '6105.02 30', 'LV, $X1, ISTOY'),
    ('004533.00', '4521.43 30', 'SV, $X1, IBM74   C is 1'),
    ('004533.40', '6105.03 70', 'SR, $X1, ISTOY'),
    ('004534.00', '6105.02 30', 'LV, $X1, ISTOY'),
    ('004534.40', '4522.03 30', 'SV, $X1, IBM75   R is IBN9'),
    ('004535.00', '0.30 00', 'IBN4 NOP, 0'),
    ('004535.40', '4521.02 30', 'LV, $X1, IBM73'),
    ('004536.00', '0.30 00', 'NOP, 0'),
    ('004536.40', '4536.40 00', 'IBN5 BE, $   becomes BD,IBN4+2.4 if V correct'),
    ('004537.00', '4537.04 00', 'BD, $'),
    ('004537.40', '4540.44 00', 'BD, IBN6   to test count field'),
    ('004540.00', '4540.04 00', 'BD, $'),
    ('004540.40', '4522.42 30', 'IBN6 LV, $X1, IBM76   test count field for 1'),
    ('004541.00', '4521.42 B0', 'V+, $X1, IBM74'),
    ('004541.40', '4542.43 30', 'IBN7 SV, $X1, IBN8'),
    ('004542.00', '0.30 00', 'NOP, 0'),
    ('004542.40', '4542.40 00', 'IBN8 BE, $   becomes BD,IBN8+1 if count correct'),
    ('004543.00', '0.30 00', 'NOP'),
    ('004543.40', '4522.02 30', 'LV, $X1, IBM75   test refill field'),
    ('004544.00', '4523.02 B0', 'V+, $X1, IBM77'),
    ('004544.40', '4546.03 30', 'SV, $X1, IBN9'),
    ('004545.00', '0.30 00', 'NOP, 0'),
    ('004545.40', '0.30 00', 'NOP, 0'),
    ('004546.00', '4546.00 00', 'IBN9 BE, $   becomes BD,IBN10 if refill unchanged'),
    ('004546.40', '4546.44 00', 'BD, $'),
    ('004547.00', '4550.44 00', 'IBN10 BD, IBN11'),
    ('004547.40', '0.30 00', 'NOP, 0'),
    ('004550.00', '777777.70 00', 'NOP, -1'),
    ('004550.40', '0.30 00', 'IBN11 NOP, 0.0'),
]

if __name__ == "__main__":
    fails = check_rows(prog, DATA_ROWS, label="data")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
