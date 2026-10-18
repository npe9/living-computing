#!/usr/bin/env python3
"""verify_fp_arith_f209e1_4_listing.py -- F209E1-E4
(../decks/fp_arith_f209e1_4.strap: ADD DOUBLE TO MAGNITUDE's forced
zero result, the four sign-modifier combinations) against jb_af1c
pp.107-108, plus its three constants against the pool p.176.

All 47 code rows below were read off the printed encoding column
individually. The block closes on 015727.40, where F209E5 begins, and
PASS sits there.

E4's sign-bit failure path is BRGZ,SERS (1304.35 42) where E1-E3 use
B,SERS (1304.10 00). The encodings distinguish them, so this is the
listing's own variation and is transcribed as printed.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f209e1_4.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022052.00", "0031125252525252525240", "FPK37"),
    ("022053.00", "0031052525252525252520", "FPK38"),
]

CODE_ROWS = [
    ("015672.00", "22053.44 60", "DL(U), FPK38"),
    ("015672.40", "22052.56 20", "D-MG(U), FPK37"),
    ("015673.00", "22005.14 80 060012.15 70", "CT0110(BU,48), FPK0+.12, 20"),
    ("015674.00", "1310.00 80", "SIC, SEN"),
    ("015674.40", "1304.35 42", "BRGZ, SERS"),
    ("015675.00", "22005.14 80 060042.15 70", "CT0110(BU,48), FPK0+.12, 68"),
    ("015676.00", "1310.00 80", "SIC, SEN"),
    ("015676.40", "1304.35 42", "BRGZ, SERS"),
    ("015677.00", "12.04 80 015701.34 00", "BZB, 10.4, $+2.0"),
    ("015700.00", "1310.00 80", "SIC, SEN"),
    ("015700.40", "1304.10 00", "B, SERS"),
    ("015701.00", "15701.50 00", "B, $+.32"),
    ("015701.40", "22053.44 60", "DL(U), FPK38"),
    ("015702.00", "22052.76 20", "D-MGA(U), FPK37"),
    ("015702.40", "22005.14 80 060012.15 70", "CT0110(BU,48), FPK0+.12, 20"),
    ("015703.40", "1310.00 80", "SIC, SEN"),
    ("015704.00", "1304.35 42", "BRGZ, SERS"),
    ("015704.40", "22005.14 80 060042.15 70", "CT0110(BU,48), FPK0+.12, 68"),
    ("015705.40", "1310.00 80", "SIC, SEN"),
    ("015706.00", "1304.35 42", "BRGZ, SERS"),
    ("015706.40", "12.04 80 015710.74 00", "BZB, 10.4, $+2.0"),
    ("015707.40", "1310.00 80", "SIC, SEN"),
    ("015710.00", "1304.10 00", "B, SERS"),
    ("015710.40", "15711.10 00", "B, $+.32"),
    ("015711.00", "22053.54 60", "DLN(U), FPK38"),
    ("015711.40", "22052.56 20", "D-MG(U), FPK37"),
    ("015712.00", "22005.14 80 060012.15 70", "CT0110(BU,48), FPK0+.12, 20"),
    ("015713.00", "1310.00 80", "SIC, SEN"),
    ("015713.40", "1304.35 42", "BRGZ, SERS"),
    ("015714.00", "22005.14 80 060042.15 70", "CT0110(BU,48), FPK0+.12, 68"),
    ("015715.00", "1310.00 80", "SIC, SEN"),
    ("015715.40", "1304.35 42", "BRGZ, SERS"),
    ("015716.00", "12.04 80 015720.34 02", "BB, 10.4, $+2.0"),
    ("015717.00", "1310.00 80", "SIC, SEN"),
    ("015717.40", "1304.10 00", "B, SERS"),
    ("015720.00", "15720.50 00", "B, $+.32"),
    ("015720.40", "22053.54 60", "DLN(U), FPK38"),
    ("015721.00", "22052.76 20", "D-MGA(U), FPK37"),
    ("015721.40", "22005.14 80 060012.15 70", "CT0110(BU,48), FPK0+.12, 20"),
    ("015722.40", "1310.00 80", "SIC, SEN"),
    ("015723.00", "1304.35 42", "BRGZ, SERS"),
    ("015723.40", "22005.14 80 060042.15 70", "CT0110(BU,48), FPK0+.12, 68"),
    ("015724.40", "1310.00 80", "SIC, SEN"),
    ("015725.00", "1304.35 42", "BRGZ, SERS"),
    ("015725.40", "12.04 80 015727.74 02", "BB, 10.4, $+2.0"),
    ("015726.40", "1310.00 80", "SIC, SEN"),
    ("015727.00", "1304.35 42", "BRGZ, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
