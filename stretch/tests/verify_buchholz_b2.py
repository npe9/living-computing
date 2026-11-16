#!/usr/bin/env python3
"""verify_buchholz_b2.py printed|substituted -- Buchholz Appendix B, Table
B.2, "Cube-root Extraction" (printed pp.296-297), checked against the
BOOK'S OWN CLAIM over several N instead of against one word.

    printed      decks/buchholz_b2_cube_root.strap, the table as printed.
                 FAILS until the model builds VFL STORE ROUNDED; it is that
                 operation's acceptance test and is not in run_tests.sh.
    substituted  decks/buchholz_b2_cube_root_srd_substituted.strap, the same
                 program with SRD replaced by the Reference Manual's own
                 equivalent (that deck's header).  Registered.

WHAT IS CHECKED, AND WHERE EACH EXPECTATION COMES FROM.  Nothing here is
taken from a run.  The page says (printed p.296) that the starting value
"will give full 48-bit accuracy for any N in three iterations (k = 3),
except for a possible rounding error in the last iteration".  So for each
N, with X the word left at 205.0 read as a 7030 floating-point number
(Reference Manual 22-6530-2 printed pp.78-79: bit 0 exponent flag, 1-10
exponent, 11 exponent sign, 12-59 fraction, 60 sign, 61-63 flags) and u
one unit in the last place of X's fraction:

    x_root           (X - u)**3 <= N < (X + 2u)**3

in exact rational arithmetic.  X = the 48-bit truncation of the true root
satisfies X**3 <= N < (X + u)**3; the window is that, widened by the one
unit of "possible rounding error" on each side.  X must also be
normalized, positive, and carry no flag.

    three_halves_n   203.0 holds 3N/2 exactly (note 2).  Every N below has
                     at most 46 fraction bits, so 3N/2 is exact in 48 and no
                     rounding rule is assumed.
    x1               count 3 run down to 0 by note 13's "traverse loop three
                     times": value 0.0, count 0, refill 200 = 0xC8.
    PC               the BEW: 112.0 as printed (224), 113.0 substituted (226).

THE EIGHT N, chosen for what the VFL part does with the exponent P
(notes 3-6: p = (P + 1)/3 rounded, sign and magnitude):

    100              P = 7    p = 3
    8                P = 4    p = 2    a perfect cube; root fraction 0.5
    3                P = 2    p = 1    (P+1)/3 exact
    1                P = 1    p = 1    N's own fraction is 0.5
    0.375            P = -1   p = 0    P + 1 is zero: a zero with a sign
    0.75 * 2**-6     P = -6   p = -2   negative, rounds away from zero
    2**-6            P = -5   p = -1   negative, rounds toward zero
    (2**48-4)/2**48 * 2**20   P = 20  p = 7   the largest fraction used

THE REACH IS PRINTED.  A run that died, or a dump that came back without
word 205, is a failure and says so; the exit status is the verdict.
"""
import os
import re
import subprocess
import sys
import tempfile
from fractions import Fraction

# (label, 48-bit fraction as an integer, exponent)
CASES = [
    ("100",          0xC80000000000, 7),
    ("8",            0x800000000000, 4),
    ("3",            0xC00000000000, 2),
    ("1",            0x800000000000, 1),
    ("0.375",        0xC00000000000, -1),
    ("0.75*2**-6",   0xC00000000000, -6),
    ("2**-6",        0x800000000000, -5),
    ("max_fraction", 0xFFFFFFFFFFFC, 20),
]

DECKS = {
    "printed":     ("buchholz_b2_cube_root.strap", 224),
    "substituted": ("buchholz_b2_cube_root_srd_substituted.strap", 226),
}


def word(frac, exp):
    return (abs(exp) << 53) | ((1 if exp < 0 else 0) << 52) | (frac << 4)


def value(frac, exp):
    return Fraction(frac, 1 << 48) * Fraction(2) ** exp


def norm(v):
    """(fraction, exponent) of an exact positive rational, 1/2 <= f < 1."""
    e = 0
    while v >= 1:
        v /= 2; e += 1
    while v < Fraction(1, 2):
        v *= 2; e -= 1
    f = v * (1 << 48)
    assert f.denominator == 1, "not exact in 48 bits"
    return int(f), e


def main():
    if len(sys.argv) not in (2, 3) or sys.argv[1] not in DECKS:
        raise SystemExit("usage: verify_buchholz_b2.py printed|substituted [DECK]")
    deck_name, halt = DECKS[sys.argv[1]]
    here = os.path.dirname(os.path.abspath(__file__))
    # An optional second argument names another copy of the deck: that is
    # how an injection is run without editing the one in decks/.
    path = sys.argv[2] if len(sys.argv) == 3 else os.path.join(here, "..", "decks", deck_name)
    with open(path) as f:
        src = f.read()
    n_line = re.compile(r"^(\s+DD\(BU,64,8\), \(16\))[0-9A-F]{16}(\s+! DATA, N)$", re.M)
    if len(n_line.findall(src)) != 1:
        print("FAIL the deck does not have exactly one 'DATA, N' line")
        return 1
    fails = 0
    ran = 0
    with tempfile.TemporaryDirectory() as tmp:
        for label, frac, exp in CASES:
            n = value(frac, exp)
            t_frac, t_exp = norm(n * 3 / 2)
            deck = os.path.join(tmp, "b2.strap")
            with open(deck, "w") as f:
                f.write(n_line.sub(lambda m: m.group(1) + "%016X" % word(frac, exp) + m.group(2), src))
            r = subprocess.run(
                ["./run_program.sh", deck, "StretchBuchB2Tb", f"PC={halt}",
                 f"three_halves_n:203=0x{word(t_frac, t_exp):016X}",
                 "x1:17=0xC8", "DUMP=205,1"],
                cwd=here, capture_output=True, text=True)
            lines = [ln for ln in r.stdout.splitlines()
                     if ln.startswith(("PASS", "FAIL", "StretchCore: OP SET"))]
            for ln in lines:
                print(f"[N={label}] {ln}")
            if r.returncode != 0 and not lines:
                print(r.stdout[-1500:], r.stderr[-1500:])
                print(f"[N={label}] FAIL run_program.sh exit status {r.returncode}")
                fails += 1
                continue
            fails += sum(1 for ln in lines if ln.startswith("FAIL"))
            # A refused instruction is a failure whatever X came out as: four
            # of the eight N happen to land inside the window with the SRD
            # refused (observed 2026-11-15), and that is luck, not a pass.
            if any(ln.startswith("StretchCore: OP SET") for ln in lines):
                print(f"[N={label}] FAIL the model refused an instruction (OP set)")
                fails += 1
            m = re.search(r"^MEMDUMP 205 ([0-9a-f]{16})$", r.stdout, re.M)
            if not m:
                print(f"[N={label}] FAIL x_root: no dump of word 205")
                fails += 1
                continue
            ran += 1
            x = int(m.group(1), 16)
            x_frac = (x >> 4) & ((1 << 48) - 1)
            x_exp = (x >> 53) & 0x3FF
            if (x >> 52) & 1:
                x_exp = -x_exp
            clean = (x >> 63) == 0 and (x & 0xF) == 0 and (x_frac >> 47) == 1
            xv = value(x_frac, x_exp)
            u = Fraction(2) ** (x_exp - 48)
            ok = clean and (xv - u) ** 3 <= n < (xv + 2 * u) ** 3
            print(f"[N={label}] {'PASS' if ok else 'FAIL'} x_root = 0x{x:016x} "
                  f"= {float(xv)!r}, true root {float(n) ** (1 / 3)!r}"
                  + ("" if clean else " (not a clean normalized positive number)"))
            if not ok:
                fails += 1
    print(f"{ran} of {len(CASES)} values of N ran to a dump; {fails} check(s) failed")
    if fails or ran != len(CASES):
        print("1 TEST(S) FAILED" if fails else "FAIL short reach")
        return 1
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
