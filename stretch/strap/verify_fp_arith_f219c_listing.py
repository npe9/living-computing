#!/usr/bin/env python3
"""verify_fp_arith_f219c_listing.py -- F219 "NOISY MODE TEST ROUTINE",
sub-blocks P3 through S (programs/fp_arith_f219c.strap) against
jb_af1c p.172.

Where F219B's blocks were mostly the negative half of p.87's rule --
multiply, divide and store root all want the CLEAN answer, because the
positions noisy mode fills lie below the 48 bits the result keeps --
these are the positive half.  Every one is a double-precision
operation whose low 48 bits are a real part of the answer and get
their own CT, so the ones normalization shifts in are visible.  In
F219R1 and F219S they are the entire content of the low half:
nineteen ones (FK128) and two ones (FPK58) respectively.

F219Q2 is the sharpest: the 96-bit sum has thirteen leading zeros and
normalizing it gives 0xffffffffffff_ffffffffe000, so the expected low
half of 0xffffffffffff is that value plus thirteen noisy ones.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f219c.strap").read())

CONST_ROWS = [
    ('022012.00', '0001025252525252525240', 'FPK5'),
    ('022025.00', '0011400000052525252520', 'FPK16'),
    ('022026.00', '0000125252525240000000', 'FPK17'),
    ('022027.00', '0003176525252525252520', 'FPK18'),
    ('022044.00', '0031000000000000000000', 'FPK31'),
    ('022045.00', '0001177777777777777760', 'FPK32'),
    ('022050.00', '0001125252525252525240', 'FPK35'),
    ('022053.00', '0031052525252525252520', 'FPK38'),
    ('022054.00', '0001052525252525252520', 'FPK39'),
    ('022075.00', '0002024713560247135627', 'FPK56'),
    ('022077.00', '0000400000000000000070', 'FPK58'),
    ('022117.00', '0001123456701234567100', 'FPK76'),
    ('022141.00', '0000525252525252525260', 'FPK99'),
    ('022144.00', '0003052535777777777760', 'FK2'),
    ('022336.00', '0003052527777777777760', 'FK125'),
    ('022342.00', '0000000000000037777760', 'FK128'),
]

CODE_ROWS = [
    # -- F219P3 add double, exponents equal
    ('021575.00', '22012.44 60', 'P3 DL(U), FPK5'),
    ('021575.40', '22045.14 80 060012.06 70', 'P3 C0011(BU,48), FPK32+.12, 20'),
    ('021576.40', '22054.04 20', 'P3 D+(N), FPK39'),
    ('021577.00', '22045.14 80 060042.15 70', 'P3 CT0110(BU,48), FPK32+.12, 68'),
    ('021600.00', '1310.00 80', 'P3 SIC, SEN'),
    ('021600.40', '1304.35 42', 'P3 BRGZ, SERS'),
    ('021601.00', '22045.14 80 060012.15 70', 'P3 CT0110(BU,48), FPK32+.12, 20'),
    ('021602.00', '1310.00 80', 'P3 SIC, SEN'),
    ('021602.40', '1304.35 42', 'P3 BRGZ, SERS'),
    # -- F219Q1 add double to magnitude, exp mem + exp acc + +48
    ('021603.00', '22053.44 60', 'Q1 DL(U), FPK38'),
    ('021603.40', '22053.14 80 060012.06 70', 'Q1 C0011(BU,48), FPK38+.12, 20'),
    ('021604.40', '22050.06 20', 'Q1 D+MG(N), FPK35'),
    ('021605.00', '22141.14 80 060042.15 70', 'Q1 CT0110(BU,48), FPK99+.12, 68'),
    ('021606.00', '1310.00 80', 'Q1 SIC, SEN'),
    ('021606.40', '1304.35 42', 'Q1 BRGZ, SERS'),
    ('021607.00', '22045.14 80 060012.15 70', 'Q1 CT0110(BU,48), FPK32+.12, 20'),
    ('021610.00', '1310.00 80', 'Q1 SIC, SEN'),
    ('021610.40', '1304.35 42', 'Q1 BRGZ, SERS'),
    # -- F219Q2 exponents unequal
    ('021611.00', '22025.44 60', 'Q2 DL(U), FPK16'),
    ('021611.40', '22336.14 80 060012.06 70', 'Q2 C0011(BU,48), FK125+.12, 20'),
    ('021612.40', '22027.06 20', 'Q2 D+MG(N), FPK18'),
    ('021613.00', '22144.00 80 014072.15 70', 'Q2 CT0110(BU,12), FK2, 116'),
    ('021614.00', '1310.00 80', 'Q2 SIC, SEN'),
    ('021614.40', '1304.35 42', 'Q2 BRGZ, SERS'),
    ('021615.00', '22045.14 80 060042.15 70', 'Q2 CT0110(BU,48), FPK32+.12, 68'),
    ('021616.00', '1310.00 80', 'Q2 SIC, SEN'),
    ('021616.40', '1304.35 42', 'Q2 BRGZ, SERS'),
    ('021617.00', '22045.14 80 060012.15 70', 'Q2 CT0110(BU,48), FPK32+.12, 20'),
    ('021620.00', '1310.00 80', 'Q2 SIC, SEN'),
    ('021620.40', '1304.35 42', 'Q2 BRGZ, SERS'),
    # -- F219R1 load double, 0 < leading zeros < 48
    ('021621.00', '22025.04 60', 'R1 DL(N), FPK16'),
    ('021621.40', '22026.00 80 074042.15 70', 'R1 CT0110(BU,60), FPK17, 68'),
    ('021622.40', '1310.00 80', 'R1 SIC, SEN'),
    ('021623.00', '1304.35 42', 'R1 BRGZ, SERS'),
    ('021623.40', '22342.14 80 060012.15 70', 'R1 CT0110(BU,48), FK128+.12, 20'),
    ('021624.40', '1310.00 80', 'R1 SIC, SEN'),
    ('021625.00', '1304.35 42', 'R1 BRGZ, SERS'),
    # -- F219R2 load double, 48 leading zeros
    ('021625.40', '22044.04 60', 'R2 DL(N), FPK31'),
    ('021626.00', '22044.00 80 074042.15 70', 'R2 CT0110(BU,60), FPK31, 68'),
    ('021627.00', '1310.00 80', 'R2 SIC, SEN'),
    ('021627.40', '1304.35 42', 'R2 BRGZ, SERS'),
    ('021630.00', '22044.14 80 060012.15 70', 'R2 CT0110(BU,48), FPK31+.12, 20'),
    ('021631.00', '1310.00 80', 'R2 SIC, SEN'),
    ('021631.40', '1304.35 42', 'R2 BRGZ, SERS'),
    # -- F219S load double with flag
    ('021632.00', '22075.06 60', 'S DLWF(N), FPK56'),
    ('021632.40', '22117.00 80 074042.15 70', 'S CT0110(BU,60), FPK76, 68'),
    ('021633.40', '1310.00 80', 'S SIC, SEN'),
    ('021634.00', '1304.35 42', 'S BRGZ, SERS'),
    ('021634.40', '22077.14 80 060012.15 70', 'S CT0110(BU,48), FPK58+.12, 20'),
    ('021635.40', '1310.00 80', 'S SIC, SEN'),
    ('021636.00', '1304.35 42', 'S BRGZ, SERS'),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
