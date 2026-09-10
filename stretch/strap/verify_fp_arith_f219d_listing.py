#!/usr/bin/env python3
"""verify_fp_arith_f219d_listing.py -- F219 "NOISY MODE TEST ROUTINE",
sub-blocks T through Y (programs/fp_arith_f219d.strap) against jb_af1c
pp.173-174.

F219Y closes a gap the plan has carried since the divide work: "p.99
gives the remainder register a role nothing uses yet; D/ is what needs
it."  This is that block.  It checks the quotient against FK138, the
49th quotient bit on its own against FPK80's fraction -- the listing's
comment reads "NOISY MODE FAILED IF 49TH QUOT BIT NOT A ONE" -- and
then the REMAINDER REGISTER against FK139.  Nothing in the suite had
read $RM before.

F219V is the multiply-double counterpart to F219L's single-precision
multiply, and the two point opposite ways.  L wanted the clean product
because its noisy fill landed in a discarded half; V keeps the whole
96-bit product, so its low half is checked against FK7's
0x1fffffffffff -- forty-five noisy ones and three bits of the
product's own tail.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f219d.strap").read())

CONST_ROWS = [
    ('022036.00', '0001560000000000000000', 'FPK25'),
    ('022040.00', '1777677777777777777760', 'FPK27'),
    ('022041.00', '0200177777777777777760', 'FPK28'),
    ('022045.00', '0001177777777777777760', 'FPK32'),
    ('022062.00', '0027377777777777777760', 'FPK45'),
    ('022071.00', '0001024713560247135620', 'FPK52'),
    ('022120.00', '0001000000000000000160', 'FPK77'),
    ('022121.00', '0001100000000000000000', 'FPK80'),
    ('022125.00', '0001000077777777777760', 'FPK87'),
    ('022145.00', '0003700000000000000000', 'FK3'),
    ('022146.00', '0143177777777777777760', 'FK4'),
    ('022147.00', '0000400000000000001000', 'FK5'),
    ('022150.00', '0025323456701234567100', 'FK6'),
    ('022151.00', '0001017777777777777760', 'FK7'),
    ('022152.00', '0001400000000000000040', 'FK8'),
    ('022153.00', '0001143210765432106760', 'FK9'),
    ('022154.00', '0025377777777777777760', 'FK10'),
    ('022234.00', '0003377777777777777760', 'FK58'),
    ('022333.00', '0025777777777777777760', 'FK122'),
    ('022345.00', '0003077000000000000000', 'FK132'),
    ('022352.00', '0034400000000000000000', 'FK137'),
    ('022353.00', '0002501010101010100770', 'FK138'),
    ('022354.00', '0023374767676767677000', 'FK139'),
]

CODE_ROWS = [
    # -- F219T store rounded
    ('021641.40', '21642.10 00', 'T B, $+.32'),
    ('021642.00', '22125.44 60', 'T DL(U), FPK87'),
    ('021642.40', '22045.14 80 060012.06 70', 'T C0011(BU,48), FPK32+.12, 20'),
    ('021643.40', '22355.02 E0', 'T SRD(N), ROS'),
    ('021644.00', '22145.00 80 000000.20 50', 'T L(BU), FK3'),
    ('021645.00', '22355.00 80 074002.15 70', 'T CT0110(BU,60), ROS, 4'),
    ('021646.00', '1310.00 80', 'T SIC, SEN'),
    ('021646.40', '1304.35 42', 'T BRGZ, SERS'),
    # -- F219U1 store low order, exp acc = 96
    ('021647.00', '22041.44 60', 'U1 DL(U), FPK28'),
    ('021647.40', '22125.14 80 060012.06 70', 'U1 C0011(BU,48), FPK87+.12, 20'),
    ('021650.40', '22355.04 E0', 'U1 SLO(N), ROS'),
    ('021651.00', '22146.00 80 000000.20 50', 'U1 L(BU,64), FK4'),
    ('021652.00', '22355.00 80 074002.15 70', 'U1 CT0110(BU,60), ROS, 4'),
    ('021653.00', '1310.00 80', 'U1 SIC, SEN'),
    ('021653.40', '1304.35 42', 'U1 BRGZ, SERS'),
    # -- F219U2 store low order, exp acc < 48
    ('021654.00', '22036.44 60', 'U2 DL(U), FPK25'),
    ('021654.40', '22040.14 80 060012.06 70', 'U2 C0011(BU,48), FPK27+.12, 20'),
    ('021655.40', '22355.04 E0', 'U2 SLO(N), ROS'),
    ('021656.00', '22062.00 80 000000.20 50', 'U2 L(BU,64), FPK45'),
    ('021657.00', '22355.00 80 074002.15 70', 'U2 CT0110(BU,60), ROS, 4'),
    ('021660.00', '1310.00 80', 'U2 SIC, SEN'),
    ('021660.40', '1304.35 42', 'U2 BRGZ, SERS'),
    # -- F219V multiply double
    ('021661.00', '21661.50 00', 'V B, $+.32'),
    ('021661.40', '22071.40 60', 'V L(U), FPK52'),
    ('021662.00', '22147.05 A0', 'V D*(N), FK5'),
    ('021662.40', '22150.00 80 074042.15 70', 'V CT0110(BU,60), FK6, 68'),
    ('021663.40', '1310.00 80', 'V SIC, SEN'),
    ('021664.00', '1304.35 42', 'V BRGZ, SERS'),
    ('021664.40', '22151.14 80 060012.15 70', 'V CT0110(BU,48), FK7+.12, 20'),
    ('021665.40', '1310.00 80', 'V SIC, SEN'),
    ('021666.00', '1304.35 42', 'V BRGZ, SERS'),
    # -- F219W load factor
    ('021666.40', '21667.10 00', 'W B, $+.32'),
    ('021667.00', '22120.04 A0', 'W LFT(N), FPK77'),
    ('021667.40', '22333.00 80 000000.20 50', 'W L(BU), FK122'),
    ('021670.40', '16.00 80 074002.15 70', 'W CT0110(BU,60), $FT, 4'),
    ('021671.40', '1310.00 80', 'W SIC, SEN'),
    ('021672.00', '1304.35 42', 'W BRGZ, SERS'),
    # -- F219X multiply and add
    ('021672.40', '21673.10 00', 'X B, $+.32'),
    ('021673.00', '22152.44 60', 'X DL(U), FK8'),
    ('021673.40', '22153.14 80 060012.06 70', 'X C0011(BU,48), FK9+.12, 20'),
    ('021674.40', '22071.44 A0', 'X LFT(U), FPK52'),
    ('021675.00', '22147.03 A0', 'X *+(N), FK5'),
    ('021675.40', '22154.00 80 074042.15 70', 'X CT0110(BU,60), FK10, 68'),
    ('021676.40', '1310.00 80', 'X SIC, SEN'),
    ('021677.00', '1304.35 42', 'X BRGZ, SERS'),
    ('021677.40', '22154.14 80 060012.15 70', 'X CT0110(BU,48), FK10+.12, 20'),
    ('021700.40', '1310.00 80', 'X SIC, SEN'),
    ('021701.00', '1304.35 42', 'X BRGZ, SERS'),
    # -- F219Y divide double (continues onto p.174)
    ('021701.40', '21702.10 00', 'Y B, $+.32'),
    ('021702.00', '22352.40 60', 'Y L(U), FK137'),
    ('021702.40', '22234.14 80 060012.06 70', 'Y C0011(BU,48), FK58+.12, 20'),
    # The 150-dpi render reads '.03' here; at 600 dpi it is plainly
    # '.05', and the arithmetic said so first: D* on the line above
    # prints .05, and D/ differs from it only in the low opcode bits,
    # not in the leading one that sets that octal digit.  '.03' is R/'s
    # encoding, which is the row two blocks earlier.
    ('021703.40', '22345.05 E0', 'Y D/(N), FK132'),
    ('021704.00', '22353.00 80 074042.15 70', 'Y CT0110(BU,60), FK138, 68'),
    ('021705.00', '1310.00 80', 'Y SIC, SEN'),
    ('021705.40', '1304.35 42', 'Y BRGZ, SERS'),
    ('021706.00', '22121.14 80 060012.15 70', 'Y CT0110(BU,48), FPK80+.12, 20  49th quotient bit'),
    ('021707.00', '1310.00 80', 'Y SIC, SEN'),
    ('021707.40', '1304.35 42', 'Y BRGZ, SERS   noisy mode failed if 49th quot bit not a one'),
    ('021710.00', '22354.00 80 000000.20 50', 'Y L(BU), FK139   check the remainder'),
    ('021711.00', '15.00 80 074002.15 70', 'Y CT0110(BU,60), $RM, 4'),
    ('021712.00', '1310.00 80', 'Y SIC, SEN'),
    ('021712.40', '1304.35 42', 'Y BRGZ, SERS'),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
