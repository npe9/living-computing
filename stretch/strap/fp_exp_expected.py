#!/usr/bin/env python3
"""fp_exp_expected.py -- operands and expected results for
programs/fp_exp_shift.strap (E+I, E+, SHF), in the 7030 single-precision
format (Reference Manual pp.101-102). Same encoder as fp_arith_expected.
"""
def enc(value):
    if value == 0: return 0
    e, F = 0, value
    while F >= 1.0: F /= 2.0; e += 1
    while F < 0.5: F *= 2.0; e -= 1
    frac = int(round(F*(1<<48)))
    if frac == (1<<48): frac >>= 1; e += 1
    em, es = abs(e), (1 if e < 0 else 0)
    return (em<<53)|(es<<52)|((frac&((1<<48)-1))<<4)

TWO   = enc(2.0)            # exp 2, frac 0.5
ONE   = enc(1.0)            # exp 1 (E+ uses only its exponent)
# E+I adds immediate exponent +1 (address 128 -> field 2 -> em=1) to 2.0 -> 4.0
EPLI  = enc(4.0)
# E+ adds ONE's exponent (+1) to 2.0 -> 4.0
EPL   = enc(4.0)
# SHF right 1: frac 0.5 -> 0.25, exponent 2 unchanged (unnormalized)
em, frac = 2, (1<<47)>>1     # 0.5 = bit47; >>1 = 0.25
SHF = (em<<53)|((frac&((1<<48)-1))<<4)
print(f"TWO=0x{TWO:016x} ONE=0x{ONE:016x} REPLI=0x{EPLI:016x} REPL=0x{EPL:016x} RSHF=0x{SHF:016x}")
