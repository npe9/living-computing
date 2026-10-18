#!/usr/bin/env python3
"""verify_fp_arith_f212c_listing.py -- F212C "TEST UNCHANGED
REGISTERS" (../decks/fp_arith_f212c.strap) against jb_af1c pp.119-120,
plus its one constant against the pool p.176.

Three encodings worth naming here:

  BBZ, 8.13, $+1.0 prints "10.15 80 016573.74 06". The page shows the
  source as "BBZ,8,13,$+1." -- that comma is STRAP's word.bit point,
  scanned wrong; 0o10/0o15 in the assembled word are word 8 and bit 13,
  which is what settles it. Its target is the next instruction, so the
  branch is a no-op either way.

  CT1010(BU,12), FPK1, 116 checks TWELVE bits at offset 116 -- IBM 0-11,
  the exponent field -- and CT1010(BU,20), FPK1 checks TWENTY at offset
  0, which is IBM 108-127, the part of the right half outside the
  96-bit fraction. Those two offsets are the whole point of the block.

  CT1100(BU,8), 10.0 reads word 10, the sign byte.

FSF4 is the listing's own label at 016571.40, and the block's last row
is at 016605.00 where the page has "BD,$+1.0".
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f212c.strap").read())

CONST_ROWS = [
    ("022006.00", "1777777777777777777777", "FPK1"),
]

CODE_ROWS = [
    ("016571.40", "22006.00 80 000040.36 70", "C1111(BU,64), FPK1, 64"),
    ("016572.40", "10.15 80 016573.74 06", "BBZ, 8.13, $+1.0"),
    ("016573.40", "22006.00 80 000000.36 70", "C1111(BU,64), FPK1"),
    ("016574.40", "12.00 80 010000.36 F0", "CM1111(BU,8), 10.0"),
    ("016575.40", "200.67 20", "SHFL(U), 1"),
    ("016576.00", "22006.00 80 014072.25 70", "CT1010(BU,12), FPK1, 116   F212C1"),
    ("016577.00", "1310.00 80", "SIC, SEN"),
    ("016577.40", "1304.35 42", "BRGZ, SERS"),
    ("016600.00", "22006.00 80 024000.25 70", "CT1010(BU,20), FPK1        F212C2"),
    ("016601.00", "1310.00 80", "SIC, SEN"),
    ("016601.40", "1304.35 42", "BRGZ, SERS"),
    ("016602.00", "12.00 80 010000.31 70", "CT1100(BU,8), 10.0         F212C3"),
    ("016603.00", "1310.00 80", "SIC, SEN"),
    ("016603.40", "1304.35 42", "BRGZ, SERS"),
    ("016604.00", "1310.00 80", "SIC, SEN"),
    ("016604.40", "1304.35 42", "BRGZ, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
