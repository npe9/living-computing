#!/usr/bin/env python3
"""verify_fp_arith_f212a1_11_listing.py -- F212A1-A11
(../decks/fp_arith_f212a1_11.strap: the SHIFT FRACTION left-shift walk)
against jb_af1c p.115, plus its twelve constants against the pool p.176.

The rows below were read off the printed encoding column individually.
The interest here is the SHF encoding itself, which no earlier block in
this series exercised: the amount rides in the ADDRESS field as
amount<<7, and the DIRECTION is spelled with the sign modifiers, not
with address bit 11 -- Reference Manual p.102, "the sign of the shift
... is subject to modification by the sign modifiers".  So SHFL(U),n
prints as (n<<7 octal).67 20 with the direction bit CLEAR, and A1's
SHFL(U),0 is the degenerate "0.67 20".

SAP13 is the listing's own label at its real address, 016267.40.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f212a1_11.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
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

# F212A1 in full, then the one row per sub-test that differs for
# A2-A11: the SHFL amount and the FPK the high half is checked against.
# (The SIC/BRGZ/CT0110-of-FPK0 rows repeat verbatim and are covered by
# A1's copies plus the location check, which only lines up if every
# instruction in between is the right length.)
CODE_ROWS = [
    ("016267.40", "22125.44 60", "DL(U), FPK87"),
    ("016270.00", "0.67 20", "SHFL(U), 0"),
    ("016270.40", "22125.14 80 060042.15 70", "CT0110(BU,48), FPK87+.12, 68"),
    ("016271.40", "1310.00 80", "SIC, SEN"),
    ("016272.00", "1304.35 42", "BRGZ, SERS"),
    ("016272.40", "22005.14 80 060012.15 70", "CT0110(BU,48), FPK0+.12, 20"),
    ("016273.40", "1310.00 80", "SIC, SEN"),
    ("016274.00", "1304.35 42", "BRGZ, SERS"),

    ("016274.40", "22125.44 60", "DL(U), FPK87            F212A2"),
    ("016275.00", "200.67 20", "SHFL(U), 1"),
    ("016275.40", "22126.14 80 060042.15 70", "CT0110(BU,48), FPK88+.12, 68"),

    ("016301.40", "22125.44 60", "DL(U), FPK87            F212A3"),
    ("016302.00", "400.67 20", "SHFL(U), 2"),
    ("016302.40", "22127.14 80 060042.15 70", "CT0110(BU,48), FPK89+.12, 68"),

    ("016306.40", "22125.44 60", "DL(U), FPK87            F212A4"),
    ("016307.00", "600.67 20", "SHFL(U), 3"),
    ("016307.40", "22130.14 80 060042.15 70", "CT0110(BU,48), FPK90+.12, 68"),

    ("016313.40", "22125.44 60", "DL(U), FPK87            F212A5"),
    ("016314.00", "1000.67 20", "SHFL(U), 4"),
    ("016314.40", "22131.14 80 060042.15 70", "CT0110(BU,48), FPK91+.12, 68"),

    ("016320.40", "22125.44 60", "DL(U), FPK87            F212A6"),
    ("016321.00", "1200.67 20", "SHFL(U), 5"),
    ("016321.40", "22132.14 80 060042.15 70", "CT0110(BU,48), FPK92+.12, 68"),

    ("016325.40", "22125.44 60", "DL(U), FPK87            F212A7"),
    ("016326.00", "1400.67 20", "SHFL(U), 6"),
    ("016326.40", "22133.14 80 060042.15 70", "CT0110(BU,48), FPK93+.12, 68"),

    ("016332.40", "22125.44 60", "DL(U), FPK87            F212A8"),
    ("016333.00", "1600.67 20", "SHFL(U), 7"),
    ("016333.40", "22134.14 80 060042.15 70", "CT0110(BU,48), FPK94+.12, 68"),

    ("016337.40", "22125.44 60", "DL(U), FPK87            F212A9"),
    ("016340.00", "2000.67 20", "SHFL(U), 8"),
    ("016340.40", "22135.14 80 060042.15 70", "CT0110(BU,48), FPK95+.12, 68"),

    ("016344.40", "22125.44 60", "DL(U), FPK87            F212A10"),
    ("016345.00", "2200.67 20", "SHFL(U), 9"),
    ("016345.40", "22136.14 80 060042.15 70", "CT0110(BU,48), FPK96+.12, 68"),

    ("016351.40", "22125.44 60", "DL(U), FPK87            F212A11"),
    ("016352.00", "2400.67 20", "SHFL(U), 10"),
    ("016352.40", "22137.14 80 060042.15 70", "CT0110(BU,48), FPK97+.12, 68"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
