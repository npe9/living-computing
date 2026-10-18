#!/usr/bin/env python3
"""verify_fp_arith_f219b_listing.py -- F219 "NOISY MODE TEST ROUTINE",
sub-blocks K through P2 (../decks/fp_arith_f219b.strap) against
jb_af1c pp.171-172.

F219A carried A-J and stopped at 021537.40 with noisy mode still on.
K-P2 reach the operations A-J never touched under it: multiply,
divide, reciprocal divide, store root and add double.

The whole point of the block is what noisy mode does to an operation
whose intermediate result is already 96 bits wide.  p.87's rule is
that ones enter the positions vacated by LEFT-SHIFT NORMALIZATION --
and for multiply and divide those positions are in the low half that
a 48-bit answer discards.  Every expected value here is therefore the
CLEAN result, and the block passes only if noisy mode does not leak
upward.  F219O's own printed comment says so outright: "CHECK NO LOW
ORDER ONE BITS IN RESULT".
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f219b.strap").read())

CONST_ROWS = [
    ('022045.00', '0001177777777777777760', 'FPK32'),
    ('022050.00', '0001125252525252525240', 'FPK35'),
    ('022053.00', '0031052525252525252520', 'FPK38'),
    ('022071.00', '0001024713560247135620', 'FPK52'),
    ('022115.00', '0001500000000000000000', 'FPK74'),
    ('022121.00', '0001100000000000000000', 'FPK80'),
    ('022141.00', '0000525252525252525260', 'FPK99'),
    ('022262.00', '0005010000000000000000', 'FK81'),
    ('022263.00', '0002100000000000000000', 'FK82'),
    ('022300.00', '0004017777777777777760', 'FK95'),
    ('022301.00', '0003017777777777777760', 'FK96'),
    ('022327.00', '0000523456701234567100', 'FK118'),
    ('022335.00', '0002417777777777777760', 'FK124'),
]

CODE_ROWS = [
    # -- F219K compare magnitude for range
    ('021537.40', '21540.10 00', 'K B, $+.32'),
    # The 150-dpi render shows '13.76 30' here; at 400 dpi it is
    # plainly '13.76 80', an 8 whose upper loop the ruled line clips.
    # F219A's identical BB1 on indicator 63 prints '13.77 80', which
    # settles it without the crop: the two differ only in the
    # indicator's bit address.
    ('021540.00', '13.76 80 021541.34 0E', 'K BB1, $AH, $+1.0'),
    ('021541.00', '22335.44 60', 'K DL(U), FK124'),
    ('021541.40', '22045.03 60', 'K KMGR(N), FPK32'),
    ('021542.00', '1310.00 80', 'K SIC, SEN'),
    ('021542.40', '1304.37 40', 'K BZAH, SERS   error if AH off'),
    # -- F219L multiply
    ('021543.00', '21543.50 00', 'L B, $+.32'),
    ('021543.40', '22071.40 60', 'L L(U), FPK52'),
    ('021544.00', '22121.01 A0', 'L *(N), FPK80'),
    ('021544.40', '22327.00 80 074042.15 70', 'L CT0110(BU,60), FK118, 68'),
    ('021545.40', '1310.00 80', 'L SIC, SEN'),
    ('021546.00', '1304.35 42', 'L BRGZ, SERS'),
    # -- F219M divide
    ('021546.40', '21547.10 00', 'M B, $+.32'),
    ('021547.00', '22300.40 60', 'M L(U), FK95'),
    ('021547.40', '22301.01 E0', 'M /(N), FK96'),
    ('021550.00', '22115.00 80 074042.15 70', 'M CT0110(BU,60), FPK74, 68'),
    ('021551.00', '1310.00 80', 'M SIC, SEN'),
    ('021551.40', '1304.35 42', 'M BRGZ, SERS'),
    # -- F219N reciprocal divide
    ('021552.00', '21552.50 00', 'N B, $+.32'),
    ('021552.40', '22301.40 60', 'N L(U), FK96'),
    ('021553.00', '22300.03 E0', 'N R/(N), FK95'),
    ('021553.40', '22115.00 80 074042.15 70', 'N CT0110(BU,60), FPK74, 68'),
    ('021554.40', '1310.00 80', 'N SIC, SEN'),
    ('021555.00', '1304.35 42', 'N BRGZ, SERS'),
    # -- F219O store root
    ('021555.40', '21556.10 00', 'O B, $+.32'),
    ('021556.00', '22262.40 60', 'O L(U), FK81'),
    ('021556.40', '22355.06 E0', 'O SRT(N), ROS'),
    ('021557.00', '22263.00 80 000000.20 50', 'O L(BU,64), FK82'),
    ('021560.00', '22355.00 80 074002.15 70', 'O CT0110(BU,60), ROS, 4'),
    ('021561.00', '1310.00 80', 'O SIC, SEN'),
    ('021561.40', '1304.35 42', 'O BRGZ, SERS'),
    # -- F219P1 add double, equal exponents, both extended by 48
    ('021562.00', '22053.44 60', 'P1 DL(U), FPK38'),
    ('021562.40', '22053.14 80 060012.06 70', 'P1 C0011(BU,48), FPK38+.12, 20'),
    ('021563.40', '22050.04 20', 'P1 D+(N), FPK35'),
    ('021564.00', '22141.14 80 060042.15 70', 'P1 CT0110(BU,48), FPK99+.12, 68'),
    ('021565.00', '1310.00 80', 'P1 SIC, SEN'),
    ('021565.40', '1304.35 42', 'P1 BRGZ, SERS'),
    ('021566.00', '22045.14 80 060012.15 70', 'P1 CT0110(BU,48), FPK32+.12, 20'),
    ('021567.00', '1310.00 80', 'P1 SIC, SEN'),
    ('021567.40', '1304.35 42', 'P1 BRGZ, SERS'),
    # -- F219P2 the same pair, sides swapped
    ('021570.00', '22050.44 60', 'P2 DL(U), FPK35'),
    ('021570.40', '22053.04 20', 'P2 D+(N), FPK38'),
    ('021571.00', '22141.14 80 060042.15 70', 'P2 CT0110(BU,48), FPK99+.12, 68'),
    ('021572.00', '1310.00 80', 'P2 SIC, SEN'),
    ('021572.40', '1304.35 42', 'P2 BRGZ, SERS'),
    ('021573.00', '22053.14 80 060012.15 70', 'P2 CT0110(BU,48), FPK38+.12, 20'),
    # Printed at the TOP of p.172, above F219P3: the listing's rows
    # are not in address order there.
    ('021574.00', '1310.00 80', 'P2 SIC, SEN'),
    ('021574.40', '1304.35 42', 'P2 BRGZ, SERS'),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
