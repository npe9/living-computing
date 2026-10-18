#!/usr/bin/env python3
"""verify_fp_arith_f219e_listing.py -- F219 "NOISY MODE TEST ROUTINE",
sub-blocks Z, A1A, B1A and C1A (../decks/fp_arith_f219e.strap) against
jb_af1c p.174.  These finish the routine: the listing's next two rows
are BD, ROSA and a CNOP at 021746.00, the exit.

What is left to test by this point is the four operations that work on
PARTS of a floating-point number rather than the number -- F+ on the
fraction alone, SHF on the fraction alone, E+ and E+I on the exponent
alone.  Two are affected by noisy mode and two are not, and the
listing says which: F219A1A carries "TEST NOT AFFECTED BY NOISY MODE"
on both of its compares, and expects FPK0's zeros in the low half.
p.102 is the rule -- "No noisy mode 1-bits are entered on left shift
if noisy mode is specified" -- which makes SHF the one left shift in
the machine that does not fill.

Two immediate operands here are written as bit addresses, which is how
STRAP spells them and how the listing prints them: SHF's count of 128
is 16384.0 and prints 040000.07, and E+I's immediate of 5 is 640.0 and
prints 001200.07.  Both were pinned against the assembler before this
table was written rather than guessed from the octal.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f219e.strap").read())

CONST_ROWS = [
    ('022005.00', '0000000000000000000000', 'FPK0'),
    ('022006.00', '1777777777777777777777', 'FPK1'),
    ('022020.00', '0003001252525252525240', 'FPK11'),
    ('022022.00', '0003400525252525252520', 'FPK13'),
    ('022045.00', '0001177777777777777760', 'FPK32'),
    ('022103.00', '0002177777777777777760', 'FPK62'),
    ('022107.00', '0001000000000000000000', 'FPK67'),
    ('022112.00', '0030000000000000001420', 'FPK71'),
    ('022120.00', '0001000000000000000160', 'FPK77'),
    ('022125.00', '0001000077777777777760', 'FPK87'),
    ('022155.00', '0023377777777777777760', 'FK11'),
    ('022343.00', '0002577777777777777760', 'FK130'),
]

CODE_ROWS = [
    # -- F219Z add to fraction
    ('021713.00', '21713.50 00', 'Z B, $+.32'),
    ('021713.40', '22020.44 60', 'Z DL(U), FPK11'),
    ('021714.00', '22045.14 80 060012.06 70', 'Z C0011(BU,48), FPK32+.12, 20'),
    ('021715.00', '22022.05 20', 'Z F+(N), FPK13'),
    ('021715.40', '22005.00 80 014072.15 70', 'Z CT0110(BU,12), FPK0, 116'),
    ('021716.40', '1310.00 80', 'Z SIC, SEN'),
    ('021717.00', '1304.35 42', 'Z BRGZ, SERS'),
    ('021717.40', '22006.14 80 060042.15 70', 'Z CT0110(BU,48), FPK1+.12, 68'),
    ('021720.40', '1310.00 80', 'Z SIC, SEN'),
    ('021721.00', '1304.35 42', 'Z BRGZ, SERS'),
    ('021721.40', '22006.14 80 060012.15 70', 'Z CT0110(BU,48), FPK1+.12, 20'),
    ('021722.40', '1310.00 80', 'Z SIC, SEN'),
    ('021723.00', '1304.35 42', 'Z BRGZ, SERS'),
    # -- F219A1A shift fraction
    ('021723.40', '21724.10 00', 'A1A B, $+.32'),
    ('021724.00', '22125.44 60', 'A1A DL(U), FPK87'),
    ('021724.40', '40000.07 20', 'A1A SHF(N), 16384.0'),
    ('021725.00', '22107.00 80 074042.15 70', 'A1A CT0110(BU,60), FPK67, 68  not affected by noisy mode'),
    ('021726.00', '1310.00 80', 'A1A SIC, SEN'),
    ('021726.40', '1304.35 42', 'A1A BRGZ, SERS'),
    ('021727.00', '22005.14 80 060012.15 70', 'A1A CT0110(BU,48), FPK0+.12, 20  not affected by noisy mode'),
    ('021730.00', '1310.00 80', 'A1A SIC, SEN'),
    ('021730.40', '1304.35 42', 'A1A BRGZ, SERS'),
    # -- F219B1A add to exponent
    ('021731.00', '21731.50 00', 'B1A B, $+.32'),
    ('021731.40', '22120.44 60', 'B1A DL(U), FPK77'),
    ('021732.00', '22045.14 80 060012.06 70', 'B1A C0011(BU,48), FPK32+.12, 20'),
    ('021733.00', '22112.05 60', 'B1A E+(N), FPK71'),
    ('021733.40', '22343.00 80 074042.15 70', 'B1A CT0110(BU,60), FK130, 68'),
    ('021734.40', '1310.00 80', 'B1A SIC, SEN'),
    ('021735.00', '1304.35 42', 'B1A BRGZ, SERS'),
    ('021735.40', '22103.14 80 060012.15 70', 'B1A CT0110(BU,48), FPK62+.12, 20'),
    ('021736.40', '1310.00 80', 'B1A SIC, SEN'),
    ('021737.00', '1304.35 42', 'B1A BRGZ, SERS'),
    # -- F219C1A add to exponent immediate
    ('021737.40', '21740.10 00', 'C1A B, $+.32'),
    ('021740.00', '22120.44 60', 'C1A DL(U), FPK77'),
    ('021740.40', '22045.14 80 060012.06 70', 'C1A C0011(BU,48), FPK32+.12, 20'),
    ('021741.40', '1200.07 60', 'C1A E+I(N), 640.0'),
    ('021742.00', '22155.00 80 074042.15 70', 'C1A CT0110(BU,60), FK11, 68'),
    ('021743.00', '1310.00 80', 'C1A SIC, SEN'),
    ('021743.40', '1304.35 42', 'C1A BRGZ, SERS'),
    ('021744.00', '22155.14 80 060012.15 70', 'C1A CT0110(BU,48), FK11+.12, 20'),
    ('021745.00', '1310.00 80', 'C1A SIC, SEN'),
    ('021745.40', '1304.35 42', 'C1A BRGZ, SERS'),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
