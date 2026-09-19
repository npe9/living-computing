#!/usr/bin/env python3
"""verify_ssip_sip17_listing.py -- SSIP's SIP16/SIP17 reset blocks
(programs/ssip_sip17_reset.strap) against ja_ua1_ssip PDF pp.17-18.

Twenty branch-on-indicator-and-clear instructions in NUMERIC ORDER,
bits 0-19, so the block is a self-checking table of the indicator
numbering AND the branch-on-indicator encoding at once: an error
anywhere in that range shows up as exactly one row's mismatch.

Cite by PDF page -- this tape's listing carries no printed page
numbers (PDF pp.7-52, 1-up fanfold).
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ssip_sip17_reset.strap").read())

# SIP16: the block that resets the interrupt system's own control
# state, including the PERMANENTLY PROTECTED words 1, 2 and 3 (p.31).
# Rows naming an external symbol (INT, DSIP*) check the opcode and
# modifier bits only, their address having come from the same print.
SIP16_ROWS = [
    ('001563.40', '1.33 30',    'SV, $X13, 1.0     reset interval timer (word 1, P)'),
    ('001564.00', '2060.32 10', 'LX, $X13, DSIP31  SSIP mask constant (ext)'),
    ('001564.40', '14.33 10',   'SX, $X13, 12.0    reset mask (word 12)'),
    ('001565.00', '0.32 10',    'SIP16 LX, $X13, 0.0  X13 := the protected zero'),
    ('001565.40', '3.33 10',    'SX, $X13, 3.0     reset boundaries + control bit (word 3, P)'),
    ('001566.00', '1353.33 01', 'LVI, $X13, INT    interrupt table origin (ext)'),
    ('001566.40', '2.33 30',    'SV, $X13, 2.0     reset interrupt address (word 2, P)'),
    ('001567.00', '2025.32 30', 'LV, $X13, DSIP1   reset switches A and B (ext)'),
    ('001567.40', '2046.33 30', 'SV, $X13, DSIP20  (ext)'),
    ('001570.00', '2046.73 30', 'SV, $X13, DSIP21  (ext, same word second half)'),
    ('001570.40', '2047.32 30', 'LV, $X13, DSIP22  test switch C is not on (ext)'),
]

ROWS = [
    # SIP17 labels the BXVLZ, not the chain -- see the program header.
    ('001571.00', '1571.30 C2', 'SIP17 BXVLZ, $   * error made in SSIP'),
    ('001571.40', '0.32 10',    'LX, $X13, 0.0    X13 := the protected zero'),
    ('001572.00', '1572.40 46', 'BMKZ, $+.32      0  machine check'),
    ('001572.40', '1573.00 C6', 'BIKZ, $+.32      1  -RESET INDICATORS'),
    ('001573.00', '1573.41 46', 'BIJZ, $+.32      2  instruction reject'),
    ('001573.40', '1574.01 C6', 'BEKZ, $+.32      3  exchange check'),
    ('001574.00', '1574.42 46', 'BTSZ, $+.32      4  time signal'),
    ('001574.40', '1575.02 C6', 'BCPUZ, $+.32     5  CPU signal'),
    ('001575.00', '1575.43 46', 'BEKJZ, $+.32     6  exchange check reject'),
    ('001575.40', '1576.03 C6', 'BUNRJZ, $+.32    7  unit not ready reject'),
    ('001576.00', '1576.44 46', 'BCBJZ, $+.32     8  channel busy reject'),
    ('001576.40', '1577.04 C6', 'BEPGKZ, $+.32    9  exchange program check'),
    ('001577.00', '1577.45 46', 'BUKZ, $+.32      10 unit check'),
    ('001577.40', '1600.05 C6', 'BEEZ, $+.32      11 end exception'),
    ('001600.00', '1600.46 46', 'BEOPZ, $+.32     12 end of operation'),
    ('001600.40', '1601.06 C6', 'BCSZ, $+.32      13 channel signal'),
    # Slot 14 is a PLAIN branch: there is no indicator 14 to test, which
    # is an independent witness to INDICATOR_BITS' gap at that bit.
    ('001601.00', '1601.50 00', 'B, $+.32         14 RESERVED -- plain branch'),
    ('001601.40', '1602.07 C6', 'BOPZ, $+.32      15 operation code invalid'),
    ('001602.00', '1602.50 46', 'BADZ, $+.32      16 address invalid'),
    ('001602.40', '1603.10 C6', 'BUSAZ, $+.32     17 unended sequence of addresses'),
    ('001603.00', '1603.51 46', 'BEXEZ, $+.32     18 execute exception'),
    ('001603.40', '1604.11 C6', 'BDSZ, $+.32      19 data store'),
    ('001604.00', '13.33 10',   'SX, $X13, 11.0   reset rest of ind.'),
]

# B,RET1's address came from the print (RET1 is defined outside this
# block and given by SYN), so this row checks the opcode and modifier
# bits only -- the convention listing_oracle's header sets out.
EXTERNAL_ROWS = [
    ('001604.40', '1307.10 00', 'B, RET1          (address from the print)'),
]

if __name__ == "__main__":
    fails = check_rows(prog, [], symbols={"SIP16": "001565.00",
                                          "SIP17": "001571.00"})
    fails += check_rows(prog, SIP16_ROWS, label="SIP16 ")
    fails += check_rows(prog, ROWS, label="chain ")
    fails += check_rows(prog, EXTERNAL_ROWS, label="ext ")
    finish(fails)
