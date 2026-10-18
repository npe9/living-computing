#!/usr/bin/env python3
"""verify_ibox1_lvni_listing.py -- IBOX-1 routine IBH30-IBH40
(../decks/ibox1_lvni.strap) against ja_ax1a p.30.

LVNI, load value negative immediate -- the last of the eight modeled
index operations a coverage screen found in zero suite programs to have
a compact block.  Twenty half-words, no external constants: the V+
operand IBH39 is a BD,$ inside the block, used as data.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ibox1_lvni.strap").read())

CODE_ROWS = [
    ('004301.00', '0.43 09',    'IBH30 LVNI, $X1, 0.32'),
    ('004301.40', '4311.42 B0', 'V+, $X1, IBH39'),
    ('004302.00', '4307.03 30', 'SV, $X1, IBH34'),
    ('004302.40', '1.03 09',    'IBH31 LVNI, $X1, 1.0'),
    ('004303.00', '4311.42 B0', 'V+, $X1, IBH39'),
    ('004303.40', '4310.03 30', 'SV, $X1, IBH36'),
    ('004304.00', '1.43 09',    'IBH32 LVNI, $X1, 1.32'),
    ('004304.40', '4311.42 B0', 'V+, $X1, IBH39'),
    ('004305.00', '4311.03 30', 'SV, $X1, IBH38'),
    ('004305.40', '2.03 09',    'IBH33 LVNI, $X1, 2.0'),
    ('004306.00', '4311.42 B0', 'V+, $X1, IBH39'),
    ('004306.40', '4310.43 30', 'SV, $X1, IBH37'),
    ('004307.00', '4307.00 00', 'IBH34 BE, $   becomes BD, IBH38'),
    ('004307.40', '4312.04 00', 'IBH35 BD, IBH40   remains BD, IBH40'),
    ('004310.00', '4310.00 00', 'IBH36 BE, $   becomes BD, IBH37'),
    ('004310.40', '4310.40 00', 'IBH37 BE, $   becomes BD, IBH35'),
    ('004311.00', '4311.00 00', 'IBH38 BE, $   becomes BD, IBH36'),
    ('004311.40', '4311.44 00', 'IBH39 BD, $   also the V+ operand'),
    ('004312.00', '777777.30 00', 'IBH40 NOP, (8)777777.0'),
    ('004312.40', '777777.30 00', 'NOP, (8)777777.0'),
]

if __name__ == "__main__":
    finish(check_rows(prog, CODE_ROWS, label="code"))
