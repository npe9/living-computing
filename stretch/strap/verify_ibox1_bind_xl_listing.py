#!/usr/bin/env python3
"""verify_ibox1_bind_xl_listing.py -- IBOX-1 routine IBIN35-IBIN41
(programs/ibox1_bind_xl.strap) against ja_ax1a p.25.

The "RESTART OF ROUTINE" section that tests BRANCH ON XL, and with it
the only place in the deck that writes the INDICATOR REGISTER through
ordinary storage: SV,$X1,$IND+.32.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ibox1_bind_xl.strap").read())

SYMBOLS = {
    "IBIN35": "004062.00", "IBIN36": "004063.40", "IBXWZ6": "004067.40",
    "IBXWZ":  "004070.00", "IBIN41": "004071.00", "PASS":   "004072.00",
}

DATA_ROWS = [
    # A half-word constant: the listing prints a VF as its 24-bit value
    # and sign only.  0.10 octal is 2**3, which in a 24-bit field is IBM
    # bit 20 -- and the SV below lands it at 32+20 = 52, which is XL.
    ('004067.40', '0.10+',               'IBXWZ6 VF, (8)0.10   equals %XL IND%'),
    ('004070.00', '0.00 00 000000.00 00', 'IBXWZ XW, 0, 0, 0, 0  common XW'),
]

CODE_ROWS = [
    ('004062.00', '4070.02 10', 'IBIN35 LX, $X1, IBXWZ    set XW to zero'),
    ('004062.40', '4067.42 30', 'LV, $X1, IBXWZ6          load bit 20, %XL IND%'),
    ('004063.00', '13.43 30',   'SV, $X1, $IND+.32        store in IND reg.'),
    ('004063.40', '4063.72 40', 'IBIN36 BZXL, $      hang up if bit off'),
    ('004064.00', '4065.32 42', 'IBIN37 BXL, $+1.0   dont branch if bit off'),
    ('004064.40', '4064.44 00', 'BD, $               hang up if no branch'),
    ('004065.00', '4065.32 44', 'IBIN38 BZXLZ, $     hang up if bit off or turn off'),
    ('004065.40', '4065.72 42', 'IBIN39 BXL, $       hang up if bit on'),
    ('004066.00', '4067.32 40', 'IBIN40 BZXL, $+1.0  branch if bit off'),
    ('004066.40', '4066.44 00', 'BD, $               hang up if bit on'),
    ('004067.00', '4071.10 00', 'B, IBIN41           branch out'),
    ('004071.00', '777777.70+', 'IBIN41 VF, (8)777777.70  executed as NOP,-.32'),
    ('004071.40', '777777.70+', 'VF, (8)777777.70         executed as NOP,-.32'),
]

if __name__ == "__main__":
    fails = check_rows(prog, [], symbols=SYMBOLS)
    fails += check_rows(prog, DATA_ROWS, label="data ")
    fails += check_rows(prog, CODE_ROWS, label="code ")
    finish(fails)
