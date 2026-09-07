#!/usr/bin/env python3
"""verify_fp_arith_f212a24_30_listing.py -- F212A24-A30
(programs/fp_arith_f212a24_30.strap) against jb_af1c pp.118-119, plus
its constants against the pools pp.176-178.

Encodings new to this block:

  SHFL(N),1 prints "200.27 20" -- the same address as SHFL(U),1 with
  the UNNORMALIZED bit clear instead of set. F212A26 exists to show
  that makes no difference: p.102, "The operation is not affected by
  the normalization modifier."

  CM1111(BU,6,8), DAM+.12 prints "16500.14 80 006000.36 F0" -- six
  ones written into the address field of the instruction at DAM, at
  bit offset 12. The byte size 8 is the default, so (BU,6) assembles
  identically; the three-field form is what the page shows.

  CT0110(BU,60), FK53, 68 checks SIXTY bits at offset 68 rather than
  the 48 used everywhere earlier in F212 -- IBM 0-59, the exponent
  together with the high fraction, because A27-A30 are asking that the
  shift left the EXPONENT alone.

The block's last row is the routine's own exit at 016536.40, and DAM
is the listing's own label at its own address 016500.00; both fall out
of the transcription rather than being placed by hand, so they check
every instruction length in between.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f212a24_30.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022123.00", "0000500000000000000000", "FPK84"),
    ("022125.00", "0001000077777777777760", "FPK87"),
    ("022126.00", "0001000177777777777740", "FPK88"),
    ("022167.00", "1777403777777777777760", "FK21"),
    ("022200.00", "1577617777777777777760", "FK30"),
    ("022227.00", "1777577777777777777000", "FK53"),
    ("022230.00", "1577777777777777777600", "FK54"),
]

CODE_ROWS = [
    # F212A24 -- the LC-off row, in full.
    ("016470.00", "16470.53 46", "BLCZ, $+.32"),
    ("016470.40", "22123.44 60", "DL(U), FPK84"),
    ("016471.00", "32600.77 20", "SHFR(U), 107"),
    ("016471.40", "22005.14 80 060042.15 70", "CT0110(BU,48), FPK0+.12, 68"),
    ("016472.40", "1310.00 80", "SIC, SEN"),
    ("016473.00", "1304.35 42", "BRGZ, SERS"),
    ("016473.40", "22005.14 80 060012.15 70", "CT0110(BU,48), FPK0+.12, 20"),
    ("016474.40", "1310.00 80", "SIC, SEN"),
    ("016475.00", "1304.35 42", "BRGZ, SERS"),
    ("016475.40", "1310.00 80", "SIC, SEN"),
    ("016476.00", "1304.13 42", "BLC, SERS"),

    # F212A25 -- the self-modifying row, in full.
    ("016476.40", "22125.44 60", "DL(U), FPK87"),
    ("016477.00", "16500.14 80 006000.36 F0", "CM1111(BU,6,8), DAM+.12"),
    ("016500.00", "0.67 20", "DAM: SHFL(U), 0"),
    ("016500.40", "22125.14 80 060042.15 70", "CT0110(BU,48), FPK87+.12, 68"),
    ("016501.40", "1310.00 80", "SIC, SEN"),
    ("016502.00", "1304.35 42", "BRGZ, SERS"),
    ("016502.40", "22005.14 80 060012.15 70", "CT0110(BU,48), FPK0+.12, 20"),

    # F212A26 -- normalization modifier ignored.
    ("016504.40", "22125.44 60", "DL(U), FPK87"),
    ("016505.00", "200.27 20", "SHFL(N), 1"),
    ("016505.40", "22126.14 80 060042.15 70", "CT0110(BU,48), FPK88+.12, 68"),

    # F212A27-A30 -- flagged operands, 60-bit checks.
    ("016511.40", "16512.10 00", "B, $+.32"),
    ("016512.00", "22167.44 60", "DL(U), FK21"),
    ("016512.40", "1200.67 20", "SHFL(U), 5"),
    ("016513.00", "22227.00 80 074042.15 70", "CT0110(BU,60), FK53, 68"),
    ("016517.00", "22227.44 60", "DL(U), FK53"),
    ("016517.40", "1200.77 20", "SHFR(U), 5"),
    ("016520.00", "22167.00 80 074042.15 70", "CT0110(BU,60), FK21, 68"),
    ("016524.00", "16524.50 00", "B, $+.32"),
    ("016524.40", "22200.44 60", "DL(U), FK30"),
    ("016525.00", "600.67 20", "SHFL(U), 3"),
    ("016525.40", "22230.00 80 074042.15 70", "CT0110(BU,60), FK54, 68"),
    ("016531.40", "22230.44 60", "DL(U), FK54"),
    ("016532.00", "600.77 20", "SHFR(U), 3"),
    ("016532.40", "22200.00 80 074042.15 70", "CT0110(BU,60), FK30, 68"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
