#!/usr/bin/env python3
"""verify_ibox4_prog_ix_v_listing.py -- IBOX-4 routine 148's TEST 5E and
TEST 5F (../decks/ibox4_prog_ix_v.strap) against jb_ax4b p.150 (code),
p.153 (routine constants) and p.191 (the bit table).

Chosen by measurement, not by page order: nine index-arithmetic
operations were shown unreachable by the whole suite in one combined
injection, and this block uses three of them -- KC, SR and V-I -- in a
straight line with no SVA, so it runs as it stands where most of
IBOX-4 does not.

The two tests share their expected values.  I48XW6 starts the index
value at I48K25's address (011352) and V+ICR adds one word; I48XW7
starts it at I48K27's address (011354) and V-I subtracts one.  Both
land on 011353, which is I48K28's value field, so one constant checks
both directions.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ibox4_prog_ix_v.strap").read())

CODE_ROWS = [
    ('011352.00', '123456.70 00 000000.00 00', 'K25 XW, (8)123456.70'),
    ('011353.00', '765432.10 00 000000.00 00', 'K26 XW, (8)765432.10'),
    ('011354.00', '123456.70 00 000000.00 00', 'K27 XW, (8)123456.70'),
    ('011355.00', '11353.00 00 000020.00 00', 'K28 XW, K26, 1, 0'),
    ('011366.00', '11352.00 00 000020.22 ED', 'XW6 XW, K25, 1, K28'),
    ('011367.00', '11354.00 00 000020.00 00', 'XW7 XW, K27, 1, 0'),
    ('013075.00', '1.00 00 000000.00 00', 'BIT17 XW, (8)1.00, 0, 0'),
    # -- TEST 5E: V+ICR
    ('011214.00', '11366.02 10', 'T5E LX, $X1, XW6   test 5E, chk prog ix V+ICR'),
    ('011214.40', '1.00 81 300000.20 50', 'L(V+ICR)(BU,64,8), 1.0($X1)'),
    ('011215.40', '11.04 10', 'LX, $X2, $R'),
    ('011216.00', '11352.04 90', 'KV, $X2, K25'),
    ('011216.40', '1310.00 80', 'SIC, SEN'),
    ('011217.00', '1304.32 C0', 'BZXE, SERS   failed to obtain correct operand'),
    ('011217.40', '11355.02 90', 'KV, $X1, K28'),
    ('011220.00', '1310.00 80', 'SIC, SEN'),
    ('011220.40', '1304.32 C0', 'BZXE, SERS   failed to modify ix value correctly'),
    ('011221.00', '13075.03 90', 'KC, $X1, BIT17'),
    ('011221.40', '1310.00 80', 'SIC, SEN'),
    ('011222.00', '1304.32 C0', 'BZXE, SERS   modified index count incorrectly'),
    ('011222.40', '21.03 70', 'SR, $X1, $X1'),
    ('011223.00', '21.02 10', 'LX, $X1, $X1'),
    ('011223.40', '1310.00 80', 'SIC, SEN'),
    ('011224.00', '1304.31 40', 'BZXVZ, SERS   refilled incorrectly'),
    # -- TEST 5F: V-I
    ('011224.40', '11367.02 10', 'T5F LX, $X1, XW7   test 5F, chk prog ix V-I'),
    ('011225.00', '1.00 81 500000.20 50', 'L(V-I)(BU,64,8), 1.0($X1)'),
    ('011226.00', '11.04 10', 'LX, $X2, $R'),
    ('011226.40', '11352.04 90', 'KV, $X2, K25'),
    ('011227.00', '1310.00 80', 'SIC, SEN'),
    ('011227.40', '1304.32 C0', 'BZXE, SERS   failed to obtain correct operand'),
    ('011230.00', '11355.02 90', 'KV, $X1, K28'),
    ('011230.40', '1310.00 80', 'SIC, SEN'),
    ('011231.00', '1304.32 C0', 'BZXE, SERS   failed to modify ix value correctly'),
    ('011231.40', '13075.03 90', 'KC, $X1, BIT17'),
    ('011232.00', '1310.00 80', 'SIC, SEN'),
    ('011232.40', '1304.32 C0', 'BZXE, SERS   modified index count'),
    ('011233.00', '21.03 70', 'SR, $X1, $X1'),
    ('011233.40', '21.02 10', 'LX, $X1, $X1'),
    ('011234.00', '1310.00 80', 'SIC, SEN'),
    ('011234.40', '1304.31 40', 'BZXVZ, SERS   refilled'),
]

if __name__ == "__main__":
    finish(check_rows(prog, CODE_ROWS, label="code"))
