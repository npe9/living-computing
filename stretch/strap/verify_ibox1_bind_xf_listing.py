#!/usr/bin/env python3
"""verify_ibox1_bind_xf_listing.py -- IBOX-1 routine IBIN1-IBIN6
(programs/ibox1_bind_xf.strap) against ja_ax1a p.24.

"BRANCH ON I BOX INDICATORS", the XF group: the deck's own test of the
index FLAG indicator and of the branch-on-indicator grammar, including
the trailing-Z clear.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ibox1_bind_xf.strap").read())

DATA_ROWS = [
    # The listing writes "XW,-1,0,0,4"; this assembler's fourth field is a
    # one-bit flag, so the source writes 1.  The WORD is identical.
    ('004030.00', '0.01 C0 000000.00 00', 'IBXWZO XW, -1, 0, 0, 1   common XW for XF, XCZ, XVLZ'),
]

CODE_ROWS = [
    ('004023.00', '4030.02 10', 'IBINX LX, $X1, IBXWZO   turn on XF, XCZ, XVLZ'),
    ('004023.40', '4023.63 40', 'IBIN1 BZXF, $      hang up if bit off'),
    ('004024.00', '4025.23 42', 'IBIN2 BXF, $+1.0   dont branch if bit off'),
    ('004024.40', '4024.44 00', 'BD, $              hang up if no branch'),
    ('004025.00', '4025.23 44', 'IBIN3 BZXFZ, $     hang up if bit off or turn off'),
    ('004025.40', '4025.63 42', 'IBIN4 BXF, $       hang up if bit on'),
    ('004026.00', '4027.23 40', 'IBIN5 BZXF, $+1.0  branch if bit off'),
    ('004026.40', '4026.44 00', 'BD, $              hang up if bit on'),
    ('004027.00', '4031.10 00', 'B, IBIN6           branch out'),
    ('004031.00', '777777.70 00', 'IBIN6 VF, (8)777777.70   executed as NOP,-.32'),
    ('004031.40', '777777.70 00', 'VF, (8)777777.70         executed as NOP,-.32'),
]

if __name__ == "__main__":
    # PASS's address is a LISTING fact, not something to read back out of
    # the assembler: 004032.00 is exactly where the deck's next routine
    # (IBIN8, the XCZ group) begins, so the block ends where the page says
    # it ends.  Deriving the expectation from prog.symtab instead would
    # move the goalpost with the ball -- any pad or filler that shifted
    # the layout would shift the expectation too and stay green.
    fails = check_rows(prog, [], symbols={"PASS": "004032.00"}, label="")
    fails += check_rows(prog, DATA_ROWS, label="data")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
