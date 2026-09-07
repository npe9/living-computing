#!/usr/bin/env python3
"""verify_fp_arith_f209d1_5_listing.py -- F209D1-D5
(programs/fp_arith_f209d1_5.strap: ADD DOUBLE TO MAGNITUDE's
arithmetic result indicators RLZ, RZ, RGZ and RN) against jb_af1c
pp.106-107, plus its seven constants against the pool p.176.

All 57 code rows below were read off the printed encoding column
individually. The block closes on 015652.00, where F209D6 begins,
and PASS sits there.

D1's third question is BRGZ (1304.35 42) where its printed comment
says "error if RZ on"; D2 asks that question with BRZ (1304.34 C2).
The encodings distinguish them, so this is the listing's own
inconsistency and is transcribed as printed.
"""
import sys
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f209d1_5.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022006.00", "1777777777777777777777", "FPK1"),
    ("022044.00", "0031000000000000000000", "FPK31"),
    ("022045.00", "0001177777777777777760", "FPK32"),
    ("022052.00", "0031125252525252525240", "FPK37"),
    ("022053.00", "0031052525252525252520", "FPK38"),
    ("022054.00", "0001052525252525252520", "FPK39"),
]

CODE_ROWS = [
    ("015614.40", "15615.10 00", "B, $+.32"),
    ("015615.00", "22044.54 60", "DLN(U), FPK31"),
    ("015615.40", "22052.14 80 060012.06 70", "C0011(BU,48), FPK37+.12, 20"),
    ("015616.40", "22054.46 20", "D+MG(U), FPK39"),
    ("015617.00", "1310.00 80", "SIC, SEN"),
    ("015617.40", "1304.34 40", "BZRLZ, SERS"),
    ("015620.00", "1310.00 80", "SIC, SEN"),
    ("015620.40", "1304.35 C0", "BZRN, SERS"),
    ("015621.00", "1310.00 80", "SIC, SEN"),
    ("015621.40", "1304.35 42", "BRGZ, SERS"),
    ("015622.00", "1310.00 80", "SIC, SEN"),
    ("015622.40", "1304.35 42", "BRGZ, SERS"),
    ("015623.00", "15623.50 00", "B, $+.32"),
    ("015623.40", "22052.54 60", "DLN(U), FPK37"),
    ("015624.00", "22053.46 20", "D+MG(U), FPK38"),
    ("015624.40", "1310.00 80", "SIC, SEN"),
    ("015625.00", "1304.34 40", "BZRLZ, SERS"),
    ("015625.40", "1310.00 80", "SIC, SEN"),
    ("015626.00", "1304.35 C0", "BZRN, SERS"),
    ("015626.40", "1310.00 80", "SIC, SEN"),
    ("015627.00", "1304.34 C2", "BRZ, SERS"),
    ("015627.40", "1310.00 80", "SIC, SEN"),
    ("015630.00", "1304.35 42", "BRGZ, SERS"),
    ("015630.40", "15631.10 00", "B, $+.32"),
    ("015631.00", "22006.00 80 000000.36 70", "C1111(BU,64), FPK1"),
    ("015632.00", "22005.44 60", "DL(U), FPK0"),
    ("015632.40", "22005.46 20", "D+MG(U), FPK0"),
    ("015633.00", "1310.00 80", "SIC, SEN"),
    ("015633.40", "1304.34 C0", "BZRZ, SERS"),
    ("015634.00", "1310.00 80", "SIC, SEN"),
    ("015634.40", "1304.34 42", "BRLZ, SERS"),
    ("015635.00", "1310.00 80", "SIC, SEN"),
    ("015635.40", "1304.35 C2", "BRN, SERS"),
    ("015636.00", "1310.00 80", "SIC, SEN"),
    ("015636.40", "1304.35 42", "BRGZ, SERS"),
    ("015637.00", "15637.50 00", "B, $+.32"),
    ("015637.40", "22044.44 60", "DL(U), FPK31"),
    ("015640.00", "22045.46 20", "D+MG(U), FPK32"),
    ("015640.40", "1310.00 80", "SIC, SEN"),
    ("015641.00", "1304.35 40", "BZRGZ, SERS"),
    ("015641.40", "1310.00 80", "SIC, SEN"),
    ("015642.00", "1304.34 42", "BRLZ, SERS"),
    ("015642.40", "1310.00 80", "SIC, SEN"),
    ("015643.00", "1304.35 C2", "BRN, SERS"),
    ("015643.40", "1310.00 80", "SIC, SEN"),
    ("015644.00", "1304.34 C2", "BRZ, SERS"),
    ("015644.40", "15645.10 00", "B, $+.32"),
    ("015645.00", "22052.44 60", "DL(U), FPK37"),
    ("015645.40", "22053.46 20", "D+MG(U), FPK38"),
    ("015646.00", "1310.00 80", "SIC, SEN"),
    ("015646.40", "1304.35 40", "BZRGZ, SERS"),
    ("015647.00", "1310.00 80", "SIC, SEN"),
    ("015647.40", "1304.34 42", "BRLZ, SERS"),
    ("015650.00", "1310.00 80", "SIC, SEN"),
    ("015650.40", "1304.35 C2", "BRN, SERS"),
    ("015651.00", "1310.00 80", "SIC, SEN"),
    ("015651.40", "1304.34 C2", "BRZ, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
