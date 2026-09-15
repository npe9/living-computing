#!/usr/bin/env python3
"""verify_ibox1_kvni_listing.py -- IBOX-1 routine IKVNI-IKVNI8
(programs/ibox1_kvni.strap) against ja_ax1a p.40, with the two IBKVD
constants it loads from p.28.

KVNI, compare value NEGATIVE immediate -- the sign-flipped twin of KVI.
One of the eight modeled index operations a coverage screen found in
zero suite programs.  Purely hang-based: every check is a branch that
must or must not be taken.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ibox1_kvni.strap").read())

DATA_ROWS = [
    ('004202.00', '0.00 00',      'IBKVDA VF, 0.00   +0S'),
    ('004212.00', '400000.00 80', 'IBKVDO VF, -(8)400000.00   -0S, 1 in bit 0'),
]

CODE_ROWS = [
    ('004746.40', '4212.02 30',   'IKVNI LV, $X1, IBKVDO   LV, -, 24-0 S'),
    ('004747.00', '400000.03 0C', 'IKVNI1 KVNI, $X1, (8)400000.0   1 in bit 0 + 18-0 S'),
    ('004747.40', '4747.72 42',   'BXL, $   hang up if low'),
    ('004750.00', '4750.33 42',   'BXH, $   hang up if high'),
    ('004750.40', '4750.72 C4',   'BZXEZ, $   hang up if not equal'),
    ('004751.00', '377777.03 0C', 'IKVNI2 KVNI, $X1, (8)377777.0   18-1 S + 0 in 18'),
    ('004751.40', '4751.73 42',   'BXH, $   hang up if high'),
    ('004752.00', '4752.32 C2',   'BXE, $   hang up if equal'),
    ('004752.40', '4752.72 44',   'BZXLZ, $   hang up if not low'),
    ('004753.00', '400000.43 0C', 'IKVNI3 KVNI, $X1, (8)400000.40   1 in 0 + 1..+17-0 S'),
    ('004753.40', '4753.72 C2',   'BXE, $   hang up if equal'),
    ('004754.00', '4754.33 44',   'BZXHZ, $   hang up if not high'),
    ('004754.40', '4202.02 30',   'IKVNI4 LV, $X1, IBKVDA   LV, +, 24-0 S'),
    ('004755.00', '0.03 0C',      'IKVNI5 KVNI, $X1, 0.0   18-0 S'),
    ('004755.40', '4756.72 C6',   'BXEZ, $+1.0   branch if XE'),
    ('004756.00', '4756.04 00',   'BD, $   hang up if not XE'),
    ('004756.40', '0.43 0C',      'IKVNI6 KVNI, $X1, 0.32   18-0 S + 1 in 18'),
    ('004757.00', '4760.33 46',   'BXHZ, $+1.0   branch if XH'),
    ('004757.40', '4757.44 00',   'BD, $   hang up if not XH'),
    ('004760.00', '777777.43 0C', 'IKVNI7 KVNI, $X1, (8)777777.40   19-1 S'),
    ('004760.40', '4761.73 46',   'BXHZ, $+1.0   branch if XH'),
    ('004761.00', '4761.04 00',   'BD, $   hang up if not XH'),
    ('004761.40', '0.30 00',      'CNOP'),
    ('004762.00', '777777.70 00', 'IKVNI8 VF, (8)777777.70   executed as NOP,-.32'),
    ('004762.40', '777777.70 00', 'VF, (8)777777.70   executed as NOP,-.32'),
]

if __name__ == "__main__":
    fails = check_rows(prog, DATA_ROWS, label="data")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
