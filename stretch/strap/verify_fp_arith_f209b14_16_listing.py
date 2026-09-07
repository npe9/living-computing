#!/usr/bin/env python3
"""verify_fp_arith_f209b14_16_listing.py -- F209B14-B16, the last
three sub-tests of ADD DOUBLE TO MAGNITUDE's sign and modifier
combinations, against jb_af1c p.105, plus its four constants against
the pool p.176.

All 39 code rows below were read off the printed encoding column
individually. The block closes on 015574.40, where the listing's own
exit sequence (BD,$+1.0 / B,FADM2 / SIC,SENO+.32 / B,SSW) begins, and
PASS sits there -- so F209B is now transcribed end to end.
"""
import sys
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f209b14_16.strap").read())

CONST_ROWS = [
    ("022032.00", "0031177777777777777767", "FPK21"),
    ("022052.00", "0031125252525252525240", "FPK37"),
    ("022053.00", "0031052525252525252520", "FPK38"),
    ("022055.00", "0001052525252525252530", "FPK40"),
]

CODE_ROWS = [
    ("015543.00", "15543.50 00", "B, $+.32"),
    ("015543.40", "22032.54 60", "DLN(U), FPK21"),
    ("015544.00", "22052.14 80 060012.06 70", "C0011(BU,48), FPK37+.12, 20"),
    ("015545.00", "22055.66 20", "D+MGA(U), FPK40"),
    ("015545.40", "22032.14 80 060012.15 70", "CT0110(BU,48), FPK21+.12, 20"),
    ("015546.40", "1310.00 80", "SIC, SEN"),
    ("015547.00", "1304.35 42", "BRGZ, SERS"),
    ("015547.40", "22032.14 80 060042.15 70", "CT0110(BU,48), FPK21+.12, 68"),
    ("015550.40", "1310.00 80", "SIC, SEN"),
    ("015551.00", "1304.35 42", "BRGZ, SERS"),
    ("015551.40", "12.04 80 15553.74 02", "BB, 10.04, $+2.0"),
    ("015552.40", "1310.00 80", "SIC, SEN"),
    ("015553.00", "1304.10 00", "B, SERS"),
    ("015553.40", "15554.10 00", "B, $+.32"),
    ("015554.00", "22032.54 60", "DLN(U), FPK21"),
    ("015554.40", "22052.14 80 060012.06 70", "C0011(BU,48), FPK37+.12, 20"),
    ("015555.40", "22055.56 20", "D-MG(U), FPK40"),
    ("015556.00", "22032.14 80 060012.15 70", "CT0110(BU,48), FPK21+.12, 20"),
    ("015557.00", "1310.00 80", "SIC, SEN"),
    ("015557.40", "1304.35 42", "BRGZ, SERS"),
    ("015560.00", "22032.14 80 060042.15 70", "CT0110(BU,48), FPK21+.12, 68"),
    ("015561.00", "1310.00 80", "SIC, SEN"),
    ("015561.40", "1304.35 42", "BRGZ, SERS"),
    ("015562.00", "12.04 80 15564.34 02", "BB, 10.04, $+2.0"),
    ("015563.00", "1310.00 80", "SIC, SEN"),
    ("015563.40", "1304.10 00", "B, SERS"),
    ("015564.00", "15564.50 00", "B, $+.32"),
    ("015564.40", "22053.54 60", "DLN(U), FPK38"),
    ("015565.00", "22052.14 80 060012.06 70", "C0011(BU,48), FPK37+.12, 20"),
    ("015566.00", "22055.76 20", "D-MGA(U), FPK40"),
    ("015566.40", "22055.14 80 060012.15 70", "CT0110(BU,48), FPK40+.12, 20"),
    ("015567.40", "1310.00 80", "SIC, SEN"),
    ("015570.00", "1304.35 42", "BRGZ, SERS"),
    ("015570.40", "22055.14 80 060042.15 70", "CT0110(BU,48), FPK40+.12, 68"),
    ("015571.40", "1310.00 80", "SIC, SEN"),
    ("015572.00", "1304.35 42", "BRGZ, SERS"),
    ("015572.40", "12.04 80 15574.74 02", "BB, 10.04, $+2.0"),
    ("015573.40", "1310.00 80", "SIC, SEN"),
    ("015574.00", "1304.10 00", "B, SERS"),
]


if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
