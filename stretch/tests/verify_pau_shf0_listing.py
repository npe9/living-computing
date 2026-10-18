#!/usr/bin/env python3
"""verify_pau_shf0_listing.py -- the PAU GATES ROUTINE's SHF0 block
(../decks/pau_shf0.strap) against jb_af1c p.180 (code) and p.199
(index control word and data tables).

This is the first LOOP in the suite.  Everything transcribed before it
is a straight line over a constant pool; this one loads an index
register from a control word with LX, indexes both its operands
through it, and closes with CBR+ -- count, branch and refill.  So the
rows here check three things no earlier table does: that an indexed
VFL operand encodes its index register in the second half-word (the
"81" where an unindexed operand prints "80"), that XW lays out VALUE,
COUNT and REFILL where the machine reads them, and that CBR+'s
count-and-branch encoding is right.

The shift is by zero, which is why the block needs no result table:
the expected values are the inputs.  Its error exits on p.198 name the
three failures it can report -- "ZERO SHIFT HI 52 BITS", "ZERO SHIFT
LOW 44 BITS" and "ZERO PRE SHIFT DECODING".
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/pau_shf0.strap").read())

DATA_ROWS = [
    ('024120.00', '0000125252525252525252', 'WRDA'),
    ('024121.00', '0000052525252525252525', 'WRDA+1'),
    ('024122.00', '1252525252525250000000', 'WRDB'),
    ('024123.00', '0525252525252524000000', 'WRDB+1'),
]

CODE_ROWS = [
    ('024117.00', '0.00 00 000040.50 4F', 'XA XW, 0, 2, XA'),
    ('022367.00', '24117.02 10', 'LX, $X1, XA'),
    ('022367.40', '24120.00 81 000040.20 50', 'SHF0 L(BU,64), WRDA($X1), 64'),
    ('022370.40', '24122.00 81 000000.20 10', '+(BU,64), WRDB($X1), 0'),
    ('022371.40', '0.47 20', 'SHF(U), 0'),
    ('022372.00', '24120.14 81 064040.15 70', 'CT0110(BU,52), WRDA+.12($X1), 64'),
    ('022373.00', '13.71 80 023733.34 00', 'BZB, $RZ, CHKSZ'),
    ('022374.00', '24122.00 81 054012.15 70', 'CT0110(BU,44), WRDB($X1), 20'),
    ('022375.00', '13.71 80 023733.34 00', 'BZB, $RZ, CHKSZ'),
    ('022376.00', '22367.43 4C', 'CBR+, $X1, SHF0'),
    ('022376.40', '22377.50 00', 'B, $+1.'),
    ('022377.00', '22367.50 00', 'B, SHF0'),
]

if __name__ == "__main__":
    fails = check_rows(prog, DATA_ROWS, label="data")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
