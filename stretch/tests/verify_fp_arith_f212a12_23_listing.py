#!/usr/bin/env python3
"""verify_fp_arith_f212a12_23_listing.py -- F212A12-A23
(../decks/fp_arith_f212a12_23.strap: the LC row and the SHIFT FRACTION
right-shift walk) against jb_af1c pp.116-118, plus its constants
against the pool p.176.

Two encodings here are new to this series:

  Z,$IND ("13.22 00") clears the indicator register.  The listing
  prints the operand as "SIND" -- that is STRAP's "$IND" with the
  dollar sign read as an S by the scan.  $IND is the C22-6531
  Appendix A system symbol for word 11, and MISC code 4 is Z, which
  together give exactly 13.22 00.

  SHFR(U),n ("(n<<7 octal).77 20") carries the SAME address as
  SHFL(U),n -- the direction bit is CLEAR in both -- and differs only
  in bits 19-20, the A and N sign modifiers.  Reference Manual p.102:
  the direction bit "is subject to modification by the sign
  modifiers", so STRAP spells right as A+N (force the sign positive,
  then invert it) rather than by setting address bit 11.  Emitting
  n*128+64 for SHFR would disagree with the page AND be a left shift.

The block's last row sits at 016467.40 and the listing's F212A24
begins at 016470.00, which the location column below checks: the
addresses only line up if every instruction between them is the
length this assembler thinks it is.

FSHF1 is this transcription's label for the listing's own address
016356.40; the page leaves that row unlabelled.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f212a12_23.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022047.00", "0001000000000000000020", "FPK34"),
    ("022125.00", "0001000077777777777760", "FPK87"),
    ("022126.00", "0001000177777777777740", "FPK88"),
    ("022127.00", "0001000377777777777700", "FPK89"),
    ("022130.00", "0001000777777777777600", "FPK90"),
    ("022131.00", "0001001777777777777400", "FPK91"),
    ("022132.00", "0001003777777777777000", "FPK92"),
    ("022133.00", "0001007777777777776000", "FPK93"),
    ("022134.00", "0001017777777777774000", "FPK94"),
    ("022135.00", "0001037777777777770000", "FPK95"),
    ("022136.00", "0001077777777777760000", "FPK96"),
    ("022137.00", "0001177777777777740000", "FPK97"),
]

CODE_ROWS = [
    # F212A12 -- the 96-bit / lost-carry row, in full.
    ("016356.40", "13.22 00", "Z, $IND"),
    ("016357.00", "22005.44 60", "DL(U), FPK0"),
    ("016357.40", "22047.14 80 060012.06 70", "C0011(BU,48), FPK34+.12, 20"),
    ("016360.40", "32600.67 20", "SHFL(U), 107"),
    ("016361.00", "22005.14 80 060042.15 70", "CT0110(BU,48), FPK0+.12, 68"),
    ("016362.00", "1310.00 80", "SIC, SEN"),
    ("016362.40", "1304.35 42", "BRGZ, SERS"),
    ("016363.00", "22005.14 80 060012.15 70", "CT0110(BU,48), FPK0+.12, 20"),
    ("016364.00", "1310.00 80", "SIC, SEN"),
    ("016364.40", "1304.35 42", "BRGZ, SERS"),
    ("016365.00", "1310.00 80", "SIC, SEN"),
    ("016365.40", "1304.13 40", "BZLC, SERS"),

    # F212A13 -- the first SHFR, in full.
    ("016366.00", "22005.44 60", "DL(U), FPK0"),
    ("016366.40", "22137.14 80 060012.06 70", "C0011(BU,48), FPK97+.12, 20"),
    ("016367.40", "0.77 20", "SHFR(U), 0"),
    ("016370.00", "22005.14 80 060042.15 70", "CT0110(BU,48), FPK0+.12, 68"),
    ("016371.00", "1310.00 80", "SIC, SEN"),
    ("016371.40", "1304.35 42", "BRGZ, SERS"),
    ("016372.00", "22137.14 80 060012.15 70", "CT0110(BU,48), FPK97+.12, 20"),
    ("016373.00", "1310.00 80", "SIC, SEN"),
    ("016373.40", "1304.35 42", "BRGZ, SERS"),

    # A14-A23: the SHFR amount and the FPK the low half lands on.
    # LOCATIONS: A14's two rows and A23's two rows were read off the
    # page (016375.40/016400.00 and 016463.40/016466.00); A15-A22's
    # were DERIVED from the uniform six-word stride those anchors fix,
    # not read individually.  The stride is independently checked at
    # both ends -- by those four rows, and by the block ending at
    # 016467.40 with the page's F212A24 at 016470.00 -- so a wrong
    # instruction length anywhere in between would break one of them.
    ("016375.40", "200.77 20", "SHFR(U), 1     F212A14"),
    ("016400.00", "22136.14 80 060012.15 70", "CT0110(BU,48), FPK96+.12, 20"),
    ("016403.40", "400.77 20", "SHFR(U), 2     F212A15"),
    ("016406.00", "22135.14 80 060012.15 70", "CT0110(BU,48), FPK95+.12, 20"),
    ("016411.40", "600.77 20", "SHFR(U), 3     F212A16"),
    ("016414.00", "22134.14 80 060012.15 70", "CT0110(BU,48), FPK94+.12, 20"),
    ("016417.40", "1000.77 20", "SHFR(U), 4    F212A17"),
    ("016422.00", "22133.14 80 060012.15 70", "CT0110(BU,48), FPK93+.12, 20"),
    ("016425.40", "1200.77 20", "SHFR(U), 5    F212A18"),
    ("016430.00", "22132.14 80 060012.15 70", "CT0110(BU,48), FPK92+.12, 20"),
    ("016433.40", "1400.77 20", "SHFR(U), 6    F212A19"),
    ("016436.00", "22131.14 80 060012.15 70", "CT0110(BU,48), FPK91+.12, 20"),
    ("016441.40", "1600.77 20", "SHFR(U), 7    F212A20"),
    ("016444.00", "22130.14 80 060012.15 70", "CT0110(BU,48), FPK90+.12, 20"),
    ("016447.40", "2000.77 20", "SHFR(U), 8    F212A21"),
    ("016452.00", "22127.14 80 060012.15 70", "CT0110(BU,48), FPK89+.12, 20"),
    ("016455.40", "2200.77 20", "SHFR(U), 9    F212A22"),
    ("016460.00", "22126.14 80 060012.15 70", "CT0110(BU,48), FPK88+.12, 20"),
    ("016463.40", "2400.77 20", "SHFR(U), 10   F212A23"),
    ("016466.00", "22125.14 80 060012.15 70", "CT0110(BU,48), FPK87+.12, 20"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
