#!/usr/bin/env python3
"""verify_ibox4_rcz_listing.py -- IBOX-4 routine 1238 test 3, first
check (programs/ibox4_rcz.strap) against jb_ax4b p.66, with its two
constants from p.67.

RCZ (Refill on Count Zero) -- the last of the operations the
whole-opcode screen found implemented and driven by nothing.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ibox4_rcz.strap").read())

DATA_ROWS = [
    ('005574.00', '123456.76 0B 064202.47 2E',
     'I38XW3 XW, (8)123456.76, (8)543210, (8)123456'),
    ('005625.00', '0.00 00 000000.13 7C',
     'I38K1 XW, 0, 0, I38XW3   count 0, refill -> I38XW3'),
]

CODE_ROWS = [
    ('005546.00', '5625.00 10', 'I3828 LX, $X0, I38K1   start check of RCZ'),
    ('005546.40', '20.06 00',   'RCZ, $X0'),
    ('005547.00', '5574.00 90', 'KV, $X0, I38XW3'),
    ('005547.40', '5551.32 C2', 'BXE, $+1.32'),
    ('005550.00', '1310.00 80', 'SIC, SEN'),
    ('005550.40', '1304.10 00', 'B, SERS   RCZ fails to refill when ct zero'),
]

if __name__ == "__main__":
    fails = check_rows(prog, DATA_ROWS, label="data")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
