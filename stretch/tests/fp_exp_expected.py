#!/usr/bin/env python3
"""fp_exp_expected.py -- operands and expected results for
../decks/fp_exp_shift.strap (E+I, E+, SHF), in the 7030 single-precision
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
# SHF right 1 leaves the accumulator unnormalized: fraction 0.5 -> 0.25
# with exponent 2 unchanged.  The program then stores it with ST(N), and
# STORE NORMALIZES -- Ref. Manual p.90, "When normalized operation is
# specified, the 48-bit operand fraction in the accumulator is
# normalized before being placed in storage" -- so what lands in RSHF is
# 0.5 at exponent 1, the same value renormalized.
#
# This expectation used to be the unnormalized 0.25 at exponent 2,
# because the ST arm did not normalize at all.  jb_af1c F219G is what
# found that: it stores FPK77 with ST(N) and demands FK122, which is
# FPK77 normalized with noisy mode's ones shifted in.  The listing and
# the manual agree against this hand-written expectation, so it is the
# expectation that was wrong.
em, frac = 1, (1<<47)        # 0.25 at exponent 2, renormalized by ST(N)
SHF = (em<<53)|((frac&((1<<48)-1))<<4)
print(f"TWO=0x{TWO:016x} ONE=0x{ONE:016x} REPLI=0x{EPLI:016x} REPL=0x{EPL:016x} RSHF=0x{SHF:016x}")
