#!/usr/bin/env python3
"""verify_ibox1_kci_listing.py -- IBOX-1 routine IKCI-IKCI12
(programs/ibox1_kci.strap) against ja_ax1a pp.40-41 (code) and p.28
(the IBKVD* constant table at 004202.00-004206.40).

Chosen by measurement: KCI was one of the five index operations still
shown unreachable after the C+I and C-I chains closed their three.

Everything here is a branch that must or must not be taken, so the
listing needs no arithmetic derivation -- but it does pin the 18-bit
immediate at both ends (all ones, one in bit 0, one in bit 17) and it
distinguishes "branch and leave the indicator on" from "branch and
zero it", which no other block in the suite does three deep.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ibox1_kci.strap").read())

DATA_ROWS = [
    ('004202.00', '0.00+', 'IBKVDA  +0S'),
    ('004202.40', '777777.77+', 'IBKVDB  +1S'),
    ('004203.00', '377777.77+', 'IBKVDC  +1S 0 in bit 0'),
    ('004203.40', '777777.76+', 'IBKVDD  +1S 0 in bit 23'),
    ('004204.00', '777776.77+', 'IBKVDE  +1S 0 in bit 17'),
    ('004204.40', '400000.00+', 'IBKVDF  +0S 1 in bit 0'),
    ('004205.00', '0.01+', 'IBKVDG  +0S 1 in bit 23'),
    ('004205.40', '1.00+', 'IBKVDH  +0S 1 in bit 17'),
    ('004206.00', '400001.00+', 'IBKVDU'),
    ('004206.40', '377777.00+', 'IBKVDV'),
]

CODE_ROWS = [
    ('004763.00', '4202.02 50', 'IKCI LC, $X1, IBKVDA   LC, 18-0 S'),
    ('004763.40', '0.03 0A', 'IKCI1 KCI, $X1, 0   KCI, 18-0 S'),
    ('004764.00', '4765.32 C6', 'BXEZ, $+1.0   branch if XE'),
    ('004764.40', '4764.44 00', 'BD, $   hang up if not XE'),
    ('004765.00', '777777.03 0A', 'IKCI2 KCI, $X1, (8)777777   KCI, 18-1 S'),
    ('004765.40', '4766.72 46', 'BXLZ, $+1.0   branch if XL'),
    ('004766.00', '4766.04 00', 'BD, $   hang up if not XL'),
    ('004766.40', '400000.03 0A', 'IKCI3 KCI, $X1, (8)400000   KCI, 1+17-0 S'),
    ('004767.00', '4767.32 44', 'BZXLZ, $   hang up if not XL'),
    ('004767.40', '1.03 0A', 'IKCI4 KCI, $X1, 1   KCI, 17-0 S + 1 in 17'),
    ('004770.00', '4771.32 42', 'BXL, $+1.0   branch if XL, leave XL on'),
    ('004770.40', '4770.44 00', 'BD, $   hang up if not XL'),
    ('004771.00', '4771.32 44', 'BZXLZ, $   hang up if XL off'),
    ('004771.40', '4204.42 50', 'IKCI5 LC, $X1, IBKVDF   LC, 1 in 0+17-0 S'),
    ('004772.00', '400000.03 0A', 'IKCI6 KCI, $X1, (8)400000'),
    ('004772.40', '4773.72 C6', 'BXEZ, $+1.0   branch if XE'),
    ('004773.00', '4773.04 00', 'BD, $   hang up if not XE'),
    ('004773.40', '1.03 0A', 'IKCI7 KCI, $X1, 1   KCI, 17-0 S + 1 in 17'),
    ('004774.00', '4774.33 44', 'BZXHZ, $   hang up if not XH'),
    ('004774.40', '777777.03 0A', 'IKCI8 KCI, $X1, (8)777777   KCI, 18-1 S'),
    ('004775.00', '4776.32 42', 'BXL, $+1.0   branch if XL, leave XL on'),
    ('004775.40', '4775.44 00', 'BD, $   hang up if not XL'),
    ('004776.00', '4776.32 44', 'BZXLZ, $   hang up if XL off'),
    ('004776.40', '4776.72 46', 'BXLZ, $   hang up if XL on'),
    ('004777.00', '377777.03 0A', 'IKCI9 KCI, $X1, (8)377777   KCI, 0+17-1 S'),
    ('004777.40', '5000.73 46', 'BXHZ, $+1.0   branch if XH'),
    ('005000.00', '5000.04 00', 'BD, $   hang up if not XH'),
    ('005000.40', '777776.03 0A', 'IKCI10 KCI, $X1, (8)777776   KCI, 17-1 S + 0 in 17'),
    ('005001.00', '5002.33 44', 'BZXHZ, $+1.0   branch if not XH'),
    ('005001.40', '5001.44 00', 'BD, $   hang up if XH'),
    ('005002.00', '5002.32 40', 'BZXL, $   hang up if not XL'),
    ('005002.40', '5003.72 46', 'BXLZ, $+1.0   branch if XL'),
    ('005003.00', '5003.04 00', 'BD, $   hang up if not XL'),
    ('005003.40', '5003.72 C6', 'BXEZ, $   hang up if XE'),
    ('005004.00', '0.03 0A', 'IKCI11 KCI, $X1, 0   KCI, 18-0 S'),
    ('005004.40', '5005.73 42', 'BXH, $+1.0   branch if XH'),
    ('005005.00', '5005.04 00', 'BD, $   hang up if not XH'),
    ('005005.40', '5005.73 44', 'BZXHZ, $   hang up if XH off'),
    ('005006.00', '5006.32 46', 'BXLZ, $   hang up if XL'),
    ('005006.40', '5006.72 C6', 'BXEZ, $   hang up if XE'),
]

if __name__ == "__main__":
    fails = check_rows(prog, DATA_ROWS, label="data")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
