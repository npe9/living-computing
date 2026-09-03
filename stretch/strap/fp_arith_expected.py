#!/usr/bin/env python3
"""fp_arith_expected.py -- build the operand words for programs/
fp_arith.strap and derive the expected stored results, from the same
7030 single-precision format the model uses (Reference Manual pp.78-79):
bit 0 EF, 1-10 EM, 11 ES, 12-59 fraction (point left of bit 12), 60
fraction sign, 61-63 flags. Value = (-1)^s * F * 2^((-1)^es E).

Prints the patched operand words (TWO, THREE) as gen_tb DD overrides
via the run_program.sh path is not wired for that, so this script is
run by the test harness to both patch the image and give the four
expected result words. Normalized fractions have 1 > F >= 1/2.
"""
import sys

def enc(value):
    # value: a positive python Fraction-like float that is an exact
    # binary fraction. Returns the 64-bit word.
    if value == 0:
        return 0
    sign = 0
    v = value
    # Normalize: find e so that 1/2 <= F < 1, F = v / 2^e.
    e = 0
    F = v
    while F >= 1.0:
        F /= 2.0; e += 1
    while F < 0.5:
        F *= 2.0; e -= 1
    frac = int(round(F * (1 << 48)))
    if frac == (1 << 48):        # rounding pushed to 1.0
        frac >>= 1; e += 1
    em = abs(e); es = 1 if e < 0 else 0
    return (0 << 63) | (em << 53) | (es << 52) | ((frac & ((1<<48)-1)) << 4) | (sign << 3)

TWO = enc(2.0)
THREE = enc(3.0)
results = [2.0, 6.0, 9.0, 3.0]
words = [enc(r) for r in results]
# Emit: TWO/THREE image patches and R1..R4 checks. Layout addresses
# come from the caller.
print("TWO=0x%016x THREE=0x%016x R1=0x%016x R2=0x%016x R3=0x%016x R4=0x%016x"
      % (TWO, THREE, words[0], words[1], words[2], words[3]))
