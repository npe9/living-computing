#!/usr/bin/env python3
"""verify_ibox2_load_index_listing.py -- the IBOX-2 tape's LOAD INDEX
CNTRL CHECK (programs/ibox2_load_index.strap) against jb_ax2a p.6
(code) and p.200 (index words).

The first block transcribed from jb_ax2a; the tape had never been
opened.  It clears the bar this session has been applying -- name the
model path it reaches and check nothing already reaches it -- because
NOTHING in the suite touches $X0 at all and only one program anywhere
uses BXCZ or BXVZ.

Index register zero is special as an ADDRESS MODIFIER (i=0 means "no
indexing") but is an ordinary register for LX and the index
indicators, and I002 is what pins that: loading it with an index word
of all ones and then taking BOTH branches leads to the error "BOTH
COUNT AND VALUE ZERO", so a register 0 that read back as zero -- the
RISC convention, and a plausible implementation -- is exactly what
this catches.

The three XW forms below all matched the listing on the first attempt,
including the negative value (100VO prints 777777.77 80, sign bit set)
and the count-only word (100CO prints 0.00 0F 777760.00 00).
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ibox2_load_index.strap").read())

DATA_ROWS = [
    ('017307.00', '1777777777777777777777', 'I00O index word of ones'),
]

CODE_ROWS = [
    ('017306.00', '0.00 00 000000.00 00', 'I00Z XW, 0, 0, 0, 0'),
    ('017310.00', '777777.77 80 000000.00 00', 'I00VO XW, -(8)777777.77, 0, 0'),
    ('017311.00', '0.00 0F 777760.00 00', 'I00CO XW, 0, (8)777777, 0'),
    ('006506.00', '17306.00 10', 'I001 LX, $X0, I00Z   load with zero'),
    ('006506.40', '6510.70 42', 'BXCZ, I002'),
    ('006507.00', '6510.71 42', 'BXVZ, I002'),
    ('006507.40', '1310.00 80', 'SIC, SEN'),
    ('006510.00', '1304.10 00', 'B, SERS   both count and value not zero'),
    ('006510.40', '17307.00 10', 'I002 LX, $X0, I00O   load with ones'),
    ('006511.00', '6512.30 42', 'BXCZ, I003'),
    ('006511.40', '6514.10 00', 'B, I005'),
    ('006512.00', '6513.31 42', 'I003 BXVZ, I004'),
    ('006512.40', '6514.10 00', 'B, I005'),
    ('006513.00', '1310.00 80', 'I004 SIC, SEN'),
    ('006513.40', '1304.10 00', 'B, SERS   both count and value zero'),
    ('006514.00', '17306.00 10', 'I005 LX, $X0, I00Z   load with zero'),
    ('006514.40', '6516.70 42', 'BXCZ, I006'),
    ('006515.00', '6516.71 42', 'BXVZ, I006'),
    ('006515.40', '1310.00 80', 'SIC, SEN'),
    ('006516.00', '1304.10 00', 'B, SERS   both count and value not zero'),
    ('006516.40', '17310.00 10', 'I006 LX, $X0, I00VO   value all ones'),
    ('006517.00', '1310.00 80', 'SIC, SEN'),
    ('006517.40', '1304.31 42', 'BXVZ, SERS   no bits in value field'),
    ('006520.00', '17311.00 10', 'LX, $X0, I00CO   count all ones'),
    ('006520.40', '1310.00 80', 'SIC, SEN'),
    ('006521.00', '1304.30 42', 'BXCZ, SERS   no bits in count field'),
]

if __name__ == "__main__":
    fails = check_rows(prog, DATA_ROWS, label="data")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
