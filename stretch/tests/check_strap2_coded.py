#!/usr/bin/env python3
"""check_strap2_coded.py -- GETFLD against C22-6729's printed coded expressions.

Figures 28 and 29, pp.200-201, read in the ink, are the only part of STRAP II
for which the guide prints the exact bits, so GETFLD's output is compared with
them bit for bit, with no dependence on any other assembler here.

Injections, measured 2026-11-09, each reverted from a saved copy and compared:
  no end-of-data bit in coded.py     12 fails, among them Fig. 28's bit string and
                                     208-bit length, and both Fig. 29 fields'
  Fig. 29's .( coded as .L           only "Fig. 29: the PEACHES field, bit string"
  a unary minus's operator number +1 only "-7 is U- on datum 1", "A*-2 is U- after 1"
  A8 J wrong in a8.py                only "A8 J as printed"
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
from strap2.a8 import a8_bits          # noqa: E402
from strap2.bits import field          # noqa: E402
from strap2.cards import Getcha        # noqa: E402
from strap2.coded import encode        # noqa: E402
from strap2.getfld import Getfld       # noqa: E402

fails = 0


def check(label, got, want):
    global fails
    ok = got == want
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} {label}")
    if not ok:
        print(f"  got  {got}\n  want {want}")


def abs24(n):
    return "110" + field(n, 24)


def sysym(name):
    # Fig. 29: $X2 18.0, $X3 19.0, both 101 000000 1000 (BU,64,8).
    table = {"X2": 18 * 64, "X3": 19 * 64}
    return (table[name], 0b1010000001000) if name in table else None


def fields(statement):
    """GETFLD over a statement field, with $3 on the character before."""
    g = Getcha([(" " * 9 + statement).ljust(72)])
    g.next()
    out = []
    f = Getfld(g, sysym)
    have = True
    while True:
        out.append(encode(f.field(have_first=have)))
        have = False
        if g.ch != ",":
            return out


# The nine A8 values the guide prints: Figs. 28-29, and Fig. 14 for $.
for ch, bits in (("J", "00100001"), ("K", "00100010"), ("M", "00100100"), ("O", "00100110"),
                 ("P", "00100111"), ("T", "00010011"), ("C", "00110011"), ("E", "00110101"),
                 ("$", "00101011")):
    check(f"A8 {ch} as printed", a8_bits(ch), bits)


def op(code, number):
    return "1" + code + field(number, 5)


def sym(text):
    return "100" + field(len(text), 7) + a8_bits(text)


# Fig. 28 p.200.  The page prints "((JOE - 1)/4.)*4+1)." with one '(' short;
# its data and operators are those of the balanced form.
fig28 = ("1000" + sym("JOE") + "0" + abs24(1) + "0" + abs24(4) + "0" +
         abs24(4) + "0" + abs24(1) + "0" + "0" +
         op("000", 1) + op("110", 3) + op("010", 2) + op("011", 3) +
         op("001", 4) + op("110", 5) + "0" + "0")
got = fields("(((JOE - 1)/4.)*4+1).")[0]
check("Fig. 28: the bit string", got, fig28)
check("Fig. 28: 208 bits", len(got), 208)

SYSD = "1010000001000"
fig29a = ("1000" + sym("PEACHESCREAMOFWHEAT") + "0" + abs24(7) +
          "1000" + abs24(3) + "0" + abs24(6) + "0" + abs24(18) + "0" + "0" +
          op("011", 2) + op("000", 1) + "0" +
          "1000" + "11100" + field(18 * 64, 24) + SYSD + "0" +
          abs24(3) + "0" + abs24(0) + "0" + "0" +
          op("111", 2) + op("001", 1) + "0" +
          "0" + "0" +
          op("111", 2) + op("001", 1) + "0" + "0")
fig29b = ("1000" + sym("MILK") + "0" + sym("CREAM") +
          "1000" + "11100" + field(19 * 64, 24) + SYSD + "0" +
          abs24(7) + "0" + "0" + op("001", 1) + "0" +
          "0" + "0" + op("000", 1) + "0" + "0")
got = fields("PEACHES CREAM OF WHEAT +7.(3-6*18)($X2+3.0), MILK-CREAM ($X3+7)")
check("Fig. 29: the PEACHES field, bit string", got[0], fig29a)
check("Fig. 29: the PEACHES field, 447 bits", len(got[0]), 447)
check("Fig. 29: the MILK field, bit string", got[1], fig29b)
check("Fig. 29: the MILK field, 196 bits", len(got[1]), 196)

# Appendix C's and Appendix F's other forms, by the rules of pp.198, 207.
check("-7 is U- on datum 1", fields("-7")[0],
      "1000" + abs24(7) + "0" + "0" + op("100", 0) + "0" + "0")
check("A*-2 is U- after 1, then *", fields("A*-2")[0],
      "1000" + sym("A") + "0" + abs24(2) + "0" + "0" +
      op("100", 1) + op("011", 1) + "0" + "0")
check("2.+3 is .L then +", fields("2.+3")[0],
      "1000" + abs24(2) + "0" + abs24(3) + "0" + "0" +
      op("110", 1) + op("001", 1) + "0" + "0")
check("2+.3 is .R after 1, then +", fields("2+.3")[0],
      "1000" + abs24(2) + "0" + abs24(3) + "0" + "0" +
      op("101", 1) + op("001", 1) + "0" + "0")
check("a null field is 1111 0, six bits with its end (p.85)", fields(",")[0], "111100")
check("the g.p. JOE(.63)2(.31)3 chains (p.207)", fields("JOE(.63)2(.31)3")[0],
      "1000" + sym("JOE") + "0" + "0" + "0" +
      "1" + field(63, 6) + "1000" + abs24(2) + "0" + "0" + "0" +
      "1" + field(31, 6) + "1000" + abs24(3) + "0" + "0" + "0" + "0")
check("the radix (8)41.0 applies through the point", fields("(8)41.10")[0],
      "1000" + abs24(0o41) + "0" + abs24(8) + "0" + "0" + op("111", 1) + "0" + "0")

print("ALL CHECKS PASSED" if not fails else f"{fails} CHECK(S) FAILED")
sys.exit(1 if fails else 0)
