#!/usr/bin/env python3
"""verify_ibox1_bind_ind_listing.py -- IBOX-1 routines IBIN35-IBIN55
(programs/ibox1_bind_ind.strap) against ja_ax1a pp.25-26.

The three "RESTART OF ROUTINE" sections that test BRANCH ON XL, XE and
XH -- the only places in the deck that write the INDICATOR REGISTER
through ordinary storage, with SV,$X1,$IND+.32.  One constant changes
between them: value bit 20, 21, 22 -> indicator bit 52, 53, 54.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ibox1_bind_ind.strap").read())

SYMBOLS = {
    "IBIN35": "004062.00", "IBIN36": "004063.40", "IBXWZ6": "004067.40",
    "IBXWZ":  "004070.00", "IBIN41": "004071.00",
    "IBIN42": "004072.00", "IBXWZ7": "004077.40", "IBIN48": "004100.00",
    "IBIN49": "004101.00", "IBXWZ8": "004106.40", "IBIN55": "004107.00",
    "PASS":   "004110.00",
}

DATA_ROWS = [
    # A half-word constant: the listing prints a VF as its 24-bit value
    # and sign only.  0.10 octal is 2**3, which in a 24-bit field is IBM
    # bit 20 -- and the SV below lands it at 32+20 = 52, which is XL.
    ('004067.40', '0.10+',                'IBXWZ6 VF, (8)0.10   equals %XL IND%'),
    ('004077.40', '0.04+',                'IBXWZ7 VF, (8)0.04   equals %XE IND%'),
    ('004106.40', '0.02+',                'IBXWZ8 VF, (8)0.02   equals %XH IND%'),
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

XE_ROWS = [
    ('004072.00', '4070.02 10', 'IBIN42 LX, $X1, IBXWZ    set XW to zero'),
    ('004072.40', '4077.42 30', 'LV, $X1, IBXWZ7          load bit 21, %XE IND%'),
    ('004073.00', '13.43 30',   'SV, $X1, $IND+.32        store in IND reg.'),
    ('004073.40', '4073.72 C0', 'IBIN43 BZXE, $      hang up if bit off'),
    ('004074.00', '4075.32 C2', 'IBIN44 BXE, $+1.0   dont branch if bit off'),
    ('004074.40', '4074.44 00', 'BD, $               hang up if no branch'),
    ('004075.00', '4075.32 C4', 'IBIN45 BZXEZ, $     hang up if bit off or turn off'),
    ('004075.40', '4075.72 C2', 'IBIN46 BXE, $       hang up if bit on'),
    ('004076.00', '4077.32 C0', 'IBIN47 BZXE, $+1.0  branch if bit off'),
    ('004076.40', '4076.44 00', 'BD, $               hang up if bit on'),
    ('004077.00', '4100.10 00', 'B, IBIN48           branch out'),
    ('004100.00', '777777.70+', 'IBIN48 VF, (8)777777.70  executed as NOP,-.32'),
    ('004100.40', '777777.70+', 'VF, (8)777777.70         executed as NOP,-.32'),
]

# NOTE on these five rows.  Read first at a smaller crop as ...72/...32
# and they are ...73/...33; the assembler disagreed and the assembler
# was right.  What flagged it before the re-render was the pattern
# across the indicators: bits 19-23 carry the indicator address and the
# op byte's high bit splits each pair, so XCZ/XVLZ = 24, XVZ/XVGZ = 25,
# XL/XE = 26 and XH must be 27 -- an XH sharing XL's 26 would have made
# BZXH and BZXL the same instruction.  Re-rendered at full scale, the
# digits are 3s.
XH_ROWS = [
    ('004101.00', '4070.02 10', 'IBIN49 LX, $X1, IBXWZ    set XW to zero'),
    ('004101.40', '4106.42 30', 'LV, $X1, IBXWZ8          load bit 22, %XH IND%'),
    ('004102.00', '13.43 30',   'SV, $X1, $IND+.32        store in IND reg.'),
    ('004102.40', '4102.73 40', 'IBIN50 BZXH, $      hang up if bit off'),
    ('004103.00', '4104.33 42', 'IBIN51 BXH, $+1.0   dont branch if bit off'),
    ('004103.40', '4103.44 00', 'BD, $               hang up if no branch'),
    ('004104.00', '4104.33 44', 'IBIN52 BZXHZ, $     hang up if bit off or turn off'),
    ('004104.40', '4104.73 42', 'IBIN53 BXH, $       hang up if bit on'),
    ('004105.00', '4106.33 40', 'IBIN54 BZXH, $+1.0  branch if bit off'),
    ('004105.40', '4105.44 00', 'BD, $               hang up if bit on'),
    ('004106.00', '4107.10 00', 'B, IBIN55           branch out'),
    ('004107.00', '777777.70+', 'IBIN55 VF, (8)777777.70  executed as NOP,-.32'),
    ('004107.40', '777777.70+', 'VF, (8)777777.70         executed as NOP,-.32'),
]

if __name__ == "__main__":
    fails = check_rows(prog, [], symbols=SYMBOLS)
    fails += check_rows(prog, DATA_ROWS, label="data ")
    fails += check_rows(prog, CODE_ROWS, label="XL ")
    fails += check_rows(prog, XE_ROWS,   label="XE ")
    fails += check_rows(prog, XH_ROWS,   label="XH ")
    finish(fails)
