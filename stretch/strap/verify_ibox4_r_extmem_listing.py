#!/usr/bin/env python3
"""verify_ibox4_r_extmem_listing.py -- IBOX-4 routine 1238 test 2, case
2A (programs/ibox4_r_extmem.strap) against jb_ax4b p.64, constants p.67.

R with its operand in EXTERNAL MEMORY rather than index core storage --
the case that needs two sequential reads, and the block that drove that
form into execute().
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ibox4_r_extmem.strap").read())

DATA_ROWS = [
    ('005574.00', '123456.76 0B 064202.47 2E',
     'I38XW3 XW, (8)123456.76, (8)543210, (8)123456'),
    ('005625.00', '0.00 00 000000.13 7C',
     'I38K1 XW, 0, 0, I38XW3   count 0, refill -> I38XW3'),
    ('005627.00', '0.30 00 000000.30 00', 'I38RFL NOP / NOP   scratch index word'),
]

CODE_ROWS = [
    ('005476.00', '5625.02 10', 'I3821 LX, $X1, I38K1   start 6 cases of addressing'),
    ('005476.40', '5627.03 10', 'SX, $X1, I38RFL   test 2A - op adr is EM'),
    ('005477.00', '5627.02 00', 'R, I38RFL         rf adr is EM'),
    ('005477.40', '0.30 00',    'NOP'),
    ('005500.00', '0.30 00',    'NOP'),
    ('005500.40', '5627.00 10', 'LX, $X0, I38RFL'),
    ('005501.00', '5574.00 90', 'KV, $X0, I38XW3'),
    ('005501.40', '5503.32 C2', 'BXE, $+1.32'),
    ('005502.00', '1310.00 80', 'SIC, SEN'),
    ('005502.40', '1304.10 00', 'B, SERS   failed to refill ext mem frm ext mem'),
]

if __name__ == "__main__":
    fails = check_rows(prog, DATA_ROWS, label="data")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
