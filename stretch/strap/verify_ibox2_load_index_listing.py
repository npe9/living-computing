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
    # -- the SIC-linked subroutine and the value-field bit sweep.
    # Every row here is a HALF word: the first generated table gave
    # SIC and BXVZ two half-words each and the addresses walked off
    # by one per case, which the oracle caught immediately.
    ('006521.40', '6526.00 80', 'SIC, I0010   go chk ix 0 is 0'),
    ('006522.00', '6523.10 00', 'B, I007'),
    ('006522.40', '6526.50 00', 'B, I0011'),
    ('006523.00', '17306.00 10', 'I007 LX, $X0, I00Z'),
    ('006523.40', '6524.70 42', 'BXCZ, I008'),
    ('006524.00', '6525.10 00', 'B, I009'),
    ('006524.40', '6526.31 42', 'I008 BXVZ, I0010'),
    ('006525.00', '1310.00 80', 'I009 SIC, SEN'),
    ('006525.40', '1304.10 00', 'B, SERS   count or value not zero'),
    ('006526.00', '0.10 00', 'I0010 B, 0.0   the word SIC writes into'),
    ('006526.40', '17326.00 10', 'I0011 LX, $X0, BIT0'),
    ('006527.00', '1310.00 80', 'SIC, SEN'),
    ('006527.40', '1304.31 42', 'BXVZ, SERS   no bit 0'),
    ('006530.00', '6526.00 80', 'SIC, I0010   clr ix 0'),
    ('006530.40', '6523.10 00', 'B, I007'),
    ('006531.00', '17327.00 10', 'LX, $X0, BIT1'),
    ('006531.40', '1310.00 80', 'SIC, SEN'),
    ('006532.00', '1304.31 42', 'BXVZ, SERS   no bit 1'),
    ('006532.40', '6526.00 80', 'SIC, I0010   clr ix 0'),
    ('006533.00', '6523.10 00', 'B, I007'),
    ('006533.40', '17330.00 10', 'LX, $X0, BIT2'),
    ('006534.00', '1310.00 80', 'SIC, SEN'),
    ('006534.40', '1304.31 42', 'BXVZ, SERS   no bit 2'),
    ('006535.00', '6526.00 80', 'SIC, I0010   clr ix 0'),
    ('006535.40', '6523.10 00', 'B, I007'),
    ('006536.00', '17331.00 10', 'LX, $X0, BIT3'),
    ('006536.40', '1310.00 80', 'SIC, SEN'),
    ('006537.00', '1304.31 42', 'BXVZ, SERS   no bit 3'),
    ('006537.40', '6526.00 80', 'SIC, I0010   clr ix 0'),
    ('006540.00', '6523.10 00', 'B, I007'),
    ('006540.40', '17332.00 10', 'LX, $X0, BIT4'),
    ('006541.00', '1310.00 80', 'SIC, SEN'),
    ('006541.40', '1304.31 42', 'BXVZ, SERS   no bit 4'),
    ('006542.00', '6526.00 80', 'SIC, I0010   clr ix 0'),
    ('006542.40', '6523.10 00', 'B, I007'),
    ('006543.00', '17333.00 10', 'LX, $X0, BIT5'),
    ('006543.40', '1310.00 80', 'SIC, SEN'),
    ('006544.00', '1304.31 42', 'BXVZ, SERS   no bit 5'),
    ('006544.40', '6526.00 80', 'SIC, I0010   clr ix 0'),
    ('006545.00', '6523.10 00', 'B, I007'),
    ('006545.40', '17334.00 10', 'LX, $X0, BIT6'),
    ('006546.00', '1310.00 80', 'SIC, SEN'),
    ('006546.40', '1304.31 42', 'BXVZ, SERS   no bit 6'),
    ('006547.00', '6526.00 80', 'SIC, I0010   clr ix 0'),
    ('006547.40', '6523.10 00', 'B, I007'),
    ('006550.00', '17335.00 10', 'LX, $X0, BIT7'),
    ('006550.40', '1310.00 80', 'SIC, SEN'),
    ('006551.00', '1304.31 42', 'BXVZ, SERS   no bit 7'),
]

if __name__ == "__main__":
    fails = check_rows(prog, DATA_ROWS, label="data")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
