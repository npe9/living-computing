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

CPLTNM, A DIGIT TOO LARGE FOR ITS RADIX (the last 16 checks, 2026-11-15).
C22-6729 p.71, Boxes 3-8, read in the ink: "If the digit equals or exceeds the
radix, an error message is executed, but the digit is still used in the
computation of the numeric datum."  p.177: "63  CPLTNM  DIGIT INCORRECT FOR
RADIX  63".  p.176's footnote names only 1-28 ("can be made to appear on the
console typewriter by the use of a Correction card") and N28-1081 page 13 says
"Messages 1-18 are considered as serious error messages by STRAP", so 63 is in
neither set.  Until 2026-11-15 the host refused the field (FieldError 63).
CHOSEN, the pages do not say: 63 once for each such digit; a letter past F is
used as G = 16 up; a radix or a g.p.'s n written with a letter is read in
decimal with the letter's value, as the 7030 deck's CPDEC does (int() raised
a bare ValueError on it once the digit was no longer refused).
NOT COVERED: a numeric DD's own number, which DNUM reads (p.71: "GETFLD does
not collect the numeric characters in the statement field of a numeric DD"),
still refuses with 47.

Injections, measured 2026-11-15, getfld.py / pass1.py restored by copy and
cmp, control all 38 passing; observed:
  63 refuses the field (the old       12: (8)19, 19A, (8)899, (2)12, (16)1G,
    behaviour)                        (8)19,(8)17, (1A)1F, JOE(.1A)3,
                                      JOE(.3,1A)1F, JOE(.3,8)9, L,(8)19 and
                                      the strict shim
  63 given, the digit not used        8: (8)19, 19A, (8)899, (2)12, (16)1G,
                                      (8)19,(8)17, JOE(.3,8)9, L,(8)19
  the digit used, 63 not given        the same 12 as the old behaviour
  63 once for a number, not for       only (8)899
    each digit
  63 kept in notes, not passed to     L,(8)19 and the strict shim
    note()
  pass1 gives 63 as fatal             L,(8)19 and the strict shim
  pass1 drops GETFLD's note           L,(8)19 and the strict shim
  _decimal is int(text) (the old)     (1A)1F, JOE(.1A)3, JOE(.3,1A)1F
  _decimal reads a letter as 0        the same 3
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


# -- CPLTNM: a digit too large for its radix, C22-6729 p.71 and p.177 ----------
def noted(statement):
    """(each field's coded expression, the numbers of GETFLD's notes), or what
    refused it."""
    g = Getcha([(" " * 9 + statement).ljust(72)])
    g.next()
    out = []
    f = Getfld(g, sysym)
    have = True
    try:
        while True:
            out.append(encode(f.field(have_first=have)))
            have = False
            if g.ch != ",":
                return out, [n for n, _ in f.notes]
    except Exception as x:
        return f"refused: {type(x).__name__} {x}"


def number(n):
    return "1000" + abs24(n) + "0" + "0" + "0" + "0"


check("control: 17 alone is one absolute datum", noted("17"), ([number(17)], []))
check("control: (8)17 is 15, no message", noted("(8)17"), ([number(0o17)], []))
check("p.71: (8)19 gives 63 and still uses the 9: 1 x 8 + 9 = 17",
      noted("(8)19"), ([number(17)], [63]))
check("p.71: 19A in radix 10 gives 63 and uses A as 10: 200", noted("19A"), ([number(200)], [63]))
check("p.71: (8)899 gives 63 for each such digit (CHOSEN): 593",
      noted("(8)899"), ([number(8 * 64 + 9 * 8 + 9)], [63, 63, 63]))
check("p.71: (2)12 is 1 x 2 + 2 = 4, 63 once", noted("(2)12"), ([number(4)], [63]))
check("p.71: (16)1F is in range, no message", noted("(16)1F"), ([number(31)], []))
check("a letter past F goes on as G = 16 (CHOSEN): (16)1G is 32, 63",
      noted("(16)1G"), ([number(32)], [63]))
check("63 in one field does not refuse the next: (8)19,(8)17",
      noted("(8)19,(8)17"), ([number(17), number(0o17)], [63]))
check("a radix written 1A is read 1 x 10 + 10 = 20 (CHOSEN), 63: (1A)1F is 35",
      noted("(1A)1F"), ([number(35)], [63]))
check("a g.p. written (.1A) is bit 20 (CHOSEN), 63, as JOE(.20)3 is coded",
      noted("JOE(.1A)3"), (fields("JOE(.20)3"), [63]))
check("a g.p.'s radix written (.3,1A) is 20 (CHOSEN), 63: JOE(.3,1A)1F as JOE(.3)35",
      noted("JOE(.3,1A)1F"), (fields("JOE(.3)35"), [63]))
check("p.71: a g.p.'s value in its radix, JOE(.3,8)9, gives 63 and uses the 9",
      noted("JOE(.3,8)9"), (fields("JOE(.3)9"), [63]))

import strap2                           # noqa: E402
from strap2.listing import listing_of   # noqa: E402


def statement(stmt):
    """The statement's printed address, the messages as (number, fatal), and
    the listing's lines for message 63."""
    try:
        r = strap2.compile_cards(["         SLC,(8)100.0", "         " + stmt, "         END"])
    except Exception as x:
        return f"refused: {type(x).__name__} {x}"
    lines = listing_of(r, r.p1.print_names).text("0", 1).splitlines()
    line = next(ln for ln in lines if ln.rstrip().endswith(stmt))
    return (line.split()[2], [(n, fatal) for n, _t, _u, fatal in r.msg.items],
            [" ".join(ln.split()) for ln in lines if ln.rstrip().endswith("  63")])


check("L,(8)19 assembles with address 21 octal and message 63 on its line, not fatal",
      statement("L,(8)19"),
      ("000000.21", [(63, False)], ["PAGE 1 LINE 2 FIELD 0 DIGIT INCORRECT FOR RADIX 63"]))
check("control: L,(8)17 has no message", statement("L,(8)17"), ("000000.17", [], []))


def strict(stmt):
    try:
        p = strap2.assemble("         SLC,(8)100.0\n         " + stmt + "\n         END\n")
    except Exception as x:
        return f"refused: {type(x).__name__} {x}"
    return [n for n, *_ in p.messages]


check("the strict shim (strap2.assemble) does not stop at 63", strict("L,(8)19"), [63])

print("ALL CHECKS PASSED" if not fails else f"{fails} CHECK(S) FAILED")
sys.exit(1 if fails else 0)
