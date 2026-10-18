#!/usr/bin/env python3
"""verify_ibox1_bind_listing.py -- IBOX-1 routine IBIN1-IBIN34
(../decks/ibox1_bind.strap) against ja_ax1a pp.24-25.

"BRANCH ON I BOX INDICATORS", all five groups: the deck's own test of
the index FLAG, COUNT ZERO, VALUE LESS THAN ZERO and VALUE ZERO
and VALUE GREATER THAN ZERO indicators, and of the
branch-on-indicator grammar including the
trailing-Z clear.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ibox1_bind.strap").read())

# PASS's address is a LISTING fact, not something to read back out of the
# assembler: 004062.00 is the half-word after the routine's last printed
# line, IBIN34's second NOP at 004061.40.  Deriving the expectation from
# prog.symtab instead would move the goalpost with the ball -- any pad or
# filler that shifted the layout would shift the expectation too and stay
# green.  Every other label below is checked the same way, against the
# address the page prints beside it.
SYMBOLS = {
    "IBINX":  "004023.00", "IBIN1":  "004023.40", "IBXWZO": "004030.00",
    "IBIN6":  "004031.00", "IBIN8":  "004032.00", "IBIN13": "004036.00",
    "IBIN15": "004037.00", "IBIN20": "004043.00",
    "IBXWZ1": "004051.00", "IBIN27": "004052.00",
    "IBIN29": "004053.40", "IBXWZ2": "004060.00", "IBIN34": "004061.00",
    "PASS":   "004062.00",
}

# The two seed words.  IBXWZO is value -1, flag 1, count 0, refill 0;
# IBXWZ1 is value 0, flag 0, count 1, refill 0.  See the program header
# on the fourth-field discrepancy -- the source writes the flag as 1
# where the listing writes 4, and the ASSEMBLED WORD is what is checked.
#
# IBXWZ1 is also what fixes the operand ORDER on this tape: its 1 lands
# on IBM bit 45, the bottom of the count field, so count is the second
# operand in the four-operand form just as it is in the three-operand one.
DATA_ROWS = [
    ('004030.00', '0.01 C0 000000.00 00', 'IBXWZO XW, -1, 0, 0, 1   common XW for XF, XCZ, XVLZ'),
    ('004051.00', '0.00 00 000020.00 00', 'IBXWZ1 XW, 0, 1, 0, 0    common XW for XVZ'),
    ('004060.00', '0.01 00 000020.00 00', 'IBXWZ2 XW, 1, 1, 0, 0    common XW for XVGZ'),
]

XF_ROWS = [
    ('004023.00', '4030.02 10', 'IBINX LX, $X1, IBXWZO   turn on XF, XCZ, XVLZ'),
    ('004023.40', '4023.63 40', 'IBIN1 BZXF, $      hang up if bit off'),
    ('004024.00', '4025.23 42', 'IBIN2 BXF, $+1.0   dont branch if bit off'),
    ('004024.40', '4024.44 00', 'BD, $              hang up if no branch'),
    ('004025.00', '4025.23 44', 'IBIN3 BZXFZ, $     hang up if bit off or turn off'),
    ('004025.40', '4025.63 42', 'IBIN4 BXF, $       hang up if bit on'),
    ('004026.00', '4027.23 40', 'IBIN5 BZXF, $+1.0  branch if bit off'),
    ('004026.40', '4026.44 00', 'BD, $              hang up if bit on'),
    ('004027.00', '4031.10 00', 'B, IBIN6           branch out'),
    ('004031.00', '777777.70+', 'IBIN6 VF, (8)777777.70   executed as NOP,-.32'),
    ('004031.40', '777777.70+', 'VF, (8)777777.70         executed as NOP,-.32'),
]

XCZ_ROWS = [
    ('004032.00', '4032.30 40', 'IBIN8 BZXCZ, $      hang up if bit off'),
    ('004032.40', '4033.70 42', 'IBIN9 BXCZ, $+1.0   dont branch if bit off'),
    ('004033.00', '4033.04 00', 'BD, $               hang up if no branch'),
    ('004033.40', '4033.70 44', 'IBIN10 BZXCZZ, $    hang up if bit off or turn off'),
    ('004034.00', '4034.30 42', 'IBIN11 BXCZ, $      hang up if bit on'),
    ('004034.40', '4035.70 40', 'IBIN12 BZXCZ, $+1.0 branch if bit off'),
    ('004035.00', '4035.04 00', 'BD, $               hang up if bit on'),
    ('004035.40', '4036.10 00', 'B, IBIN13           branch out'),
    ('004036.00', '777777.70+', 'IBIN13 VF, (8)777777.70  executed as NOP,-.32'),
    ('004036.40', '777777.70+', 'VF, (8)777777.70         executed as NOP,-.32'),
]

XVLZ_ROWS = [
    ('004037.00', '4037.30 C0', 'IBIN15 BZXVLZ, $      hang up if bit off'),
    ('004037.40', '4040.70 C2', 'IBIN16 BXVLZ, $+1.0   dont branch if bit off'),
    ('004040.00', '4040.04 00', 'BD, $                 hang up if no branch'),
    ('004040.40', '4040.70 C4', 'IBIN17 BZXVLZZ, $     hang up if bit off or turn off'),
    ('004041.00', '4041.30 C2', 'IBIN18 BXVLZ, $       hang up if bit on'),
    ('004041.40', '4042.70 C0', 'IBIN19 BZXVLZ, $+1.0  branch if bit off'),
    ('004042.00', '4042.04 00', 'BD, $                 hang up if bit on'),
    ('004042.40', '4043.10 00', 'B, IBIN20             branch out'),
    ('004043.00', '777777.70+', 'IBIN20 VF, (8)777777.70  executed as NOP,-.32'),
    ('004043.40', '777777.70+', 'VF, (8)777777.70         executed as NOP,-.32'),
]

XVZ_ROWS = [
    ('004044.00', '4051.02 10', 'LX, $X1, IBXWZ1   turn on XVZ'),
    ('004044.40', '4044.71 40', 'IBIN22 BZXVZ, $      hang up if bit off'),
    ('004045.00', '4046.31 42', 'IBIN23 BXVZ, $+1.0   dont branch if bit off'),
    ('004045.40', '4045.44 00', 'BD, $                hang up if no branch'),
    ('004046.00', '4046.31 44', 'IBIN24 BZXVZZ, $     hang up if bit off or turn off'),
    ('004046.40', '4046.71 42', 'IBIN25 BXVZ, $       hang up if bit on'),
    ('004047.00', '4050.31 40', 'IBIN26 BZXVZ, $+1.0  branch if bit off'),
    ('004047.40', '4047.44 00', 'BD, $                hang up if bit on'),
    ('004050.00', '4052.10 00', 'B, IBIN27            branch out'),
    ('004052.00', '777777.70+', 'IBIN27 VF, (8)777777.70  executed as NOP,-.32'),
    ('004052.40', '777777.70+', 'VF, (8)777777.70         executed as NOP,-.32'),
]

XVGZ_ROWS = [
    ('004053.00', '4060.02 10', 'LX, $X1, IBXWZ2   turn on XVGZ'),
    ('004053.40', '4053.71 C0', 'IBIN29 BZXVGZ, $      hang up if bit off'),
    ('004054.00', '4055.31 C2', 'IBIN30 BXVGZ, $+1.0   dont branch if bit off'),
    ('004054.40', '4054.44 00', 'BD, $                 hang up if no branch'),
    ('004055.00', '4055.31 C4', 'IBIN31 BZXVGZZ, $     hang up if bit off or turn off'),
    ('004055.40', '4055.71 C2', 'IBIN32 BXVGZ, $       hang up if bit on'),
    ('004056.00', '4057.31 C0', 'IBIN33 BZXVGZ, $+1.0  branch if bit off'),
    ('004056.40', '4056.44 00', 'BD, $                 hang up if bit on'),
    ('004057.00', '4061.10 00', 'B, IBIN34             branch out'),
    ('004061.00', '777777.70+', 'IBIN34 VF, (8)777777.70  executed as NOP,-.32'),
    ('004061.40', '777777.70+', 'VF, (8)777777.70         executed as NOP,-.32'),
]

if __name__ == "__main__":
    fails = check_rows(prog, [], symbols=SYMBOLS)
    fails += check_rows(prog, DATA_ROWS, label="data ")
    fails += check_rows(prog, XF_ROWS,   label="XF ")
    fails += check_rows(prog, XCZ_ROWS,  label="XCZ ")
    fails += check_rows(prog, XVLZ_ROWS, label="XVLZ ")
    fails += check_rows(prog, XVZ_ROWS,  label="XVZ ")
    fails += check_rows(prog, XVGZ_ROWS, label="XVGZ ")
    finish(fails)
