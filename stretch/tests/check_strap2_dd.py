#!/usr/bin/env python3
"""check_strap2_dd.py -- strap/strap2's numeric DD, against C28-6129's own
examples, printed pp.19, 27-30, read in the ink, values worked by hand from what
each example says.  Figure 3 p.19 is STRAP II's own printed output.

A word that holds an inexact fraction is compared in its upper 40 fraction bits
where the manual gives only the formula: MQDDPA truncates at each step (C22-6729
p.111), and the manual prints no such word.

Injections, measured 2026-11-09 in a copy of the tree, each reverted and compared:
  fraction rounded to 48 bits      p.29 b, "the same", p.359 lines 38, 39, 40
  power table left unnormalized    p.359 line 40, the 1.E512 row
  U exponent ignores Fn            p.28 a (both), p.28 b, p.29 c
  S replaces the number's sign     only p.28 c
  a U fraction not normalized      p.29 b's 17.5 is refused, exit at that row
  B's sign byte on the left        13, all the p.29 B rows and p.30 b's first
  B's sign bit always 8            p.29 d (two), p.30 b
  D loses the sign                 only p.30 a's first
  D ignores the byte size          only p.30 c
  the E exponent applied apart     p.28 a, 17.5 E 5, p.29 a's first (.005E3 is no
                                   longer 5), p.29 c's first, p.30 a's second
  a field's entry mode lost        p.28 a (both), p.29 c, p.29 a, then a refusal
  the DD's radix not on its g.p.   only p.30 c
  the field length's g.p. lost     only p.30 d
  a later length forgets its count the assembler refuses at that row
Measured 2026-11-12, pass1.py, restored by copy and cmp:
  message 36 never given           only "DD(BU,72): message 36" (the
                                   length is still 8: the dds's six-bit
                                   field truncated it before message 36
                                   was written)
  a long length clamped to 64      only "the length truncated to 8"
  message 37 from 10, not 9        only "DD(BU,64,9)"
  message 37 does not stop the deck only "DD(BU,64,9)"
  message 38 never given           "DD(BU,.40)" and "DD(BU,64,.8)"
  37's CC exemption removed        only "(CC*)DD(BU,,12)" (and, in the
                                   suite, every MCP page with a CC DD
                                   refuses its deck -- how it was found)
  a bit-style length's bits dropped only "DD(BU,.40)" (with 1.0 the integer
                                   part 0 encodes 64 and nothing failed, so
                                   the check uses .40)
  DDI (pass2.py ddi_a, i_SIMAD), measured 2026-11-12:
  the DDI's count not zeroed       only the PUNREL check
  a DDI that takes space           both LI checks, the space check, the
                                   signed check, the PUNREL check
  a signed immediate in two's      only "LI(D, 8, 4), -IDATA"
    complement
  floating point accepted          only the refusal check
  the whole change undone (DDI     every DDI check but "LI, IDATA", which
    assembled as a DD)             the old code passes by coincidence
"""
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
import strap2                   # noqa: E402

fails = 0
ORG = 0o100


def check(label, got, want):
    global fails
    ok = got == want
    fails += not ok
    show = "" if ok else f": got {[oct(x) if isinstance(x, int) else x for x in got] if isinstance(got, list) else got!r} want {[oct(x) if isinstance(x, int) else x for x in want] if isinstance(want, list) else want!r}"
    print(f"{'PASS' if ok else 'FAIL'} {label}{show}")


def words(stmt, n=1):
    p = strap2.assemble(f"        SLC,(8)100.0\n{stmt}\n        END,(8)100.0\n")
    return [p.words.get(ORG + k, 0) for k in range(n)]


def fword(exp, frac48, sb=0):
    """Reference Manual pp.78-79: EF, EM 10, ES, fraction 48, S T U V."""
    return (abs(exp) << 53) | ((1 if exp < 0 else 0) << 52) | (frac48 << 4) | sb


def normal(v, sb=0):
    v = F(v)
    neg = v < 0
    v = abs(v)
    e = 0
    while v >= 1:
        v /= 2
        e += 1
    while v * 2 < 1:
        v *= 2
        e -= 1
    return fword(e, (v.numerator << 48) // v.denominator, sb | (8 if neg else 0))


def approx(got, want):
    """Exponent, upper 40 fraction bits, sign byte."""
    keep = lambda w: (w >> (4 + 8) << 4) | (w & 15)
    return [keep(x) for x in got] == [keep(x) for x in want]


# -- p.19 Figure 3: printed by STRAP II ---------------------------------------
check("Fig. 3: 28671X7 prints 0007+ 6777700000000000 +000, 183007S7 0022+ 5453370000000000 +TUV",
      words("DOG     DD(N),28671X7,183007S7", 2),
      [(0o0007 << 53) | (0o6777700000000000 << 4),
       (0o0022 << 53) | (0o5453370000000000 << 4) | 7])
check("Fig. 3: (8)DD(BU,12),5703 prints 5703", words("        (8)DD(BU,12),5703")[0] >> 52, 0o5703)
check("Fig. 3: DD(BU,24),28671 prints 00067777", words("        DD(BU,24),28671")[0] >> 40, 0o00067777)

# -- p.28 Normalized --------------------------------------------------------
check("p.28 a: 54.73 E 4", words("        DD(N), 54.73 E 4"), [normal(547300)])
check("p.28 b: a negative sign and S 10 are the same word",
      words("        DD(N), -54.73 E 4"), words("        DD(N), 54.73 E 4 S 10"))
check("p.28 b: the sign bit is one, the flags zero",
      words("        DD(N), -54.73 E 4")[0] & 15, 8)
check("p.28 c: S 5: the sign one, T and V one, U zero", words("        DD(N),-54.73 E 4 S 5")[0] & 15, 0b1101)
check("p.28 d: four words, and S 17 in the last",
      words("        DD(N), 1, 3E-5, -45.7, 12 S 17", 5)[3:], [normal(12, 0o17), 0])
check("p.28 d: 1 is .5 x 2**1", words("        DD(N), 1")[0], fword(1, 1 << 47))
got = words("        DD(N), 1/3, 472*351, 4-7*5/21 S 4", 3)
check("p.28 e: arithmetic, with S in the last field",
      bool(approx(got, [normal(F(1, 3)), normal(472 * 351), normal(4 - F(35, 21), 4)])), True)
got = words("        DD(N), 27.9/31.4/12/14E5, 4+3*7/5*6", 2)
check("p.28 f: 27.9/(31.4 x 12 x 14 x 10**5), then 4 + (3x7x6)/5: 12E5's E binds first",
      bool(approx(got, [normal(F(279, 10) / F(314, 10) / 12 / (14 * 10 ** 5)), normal(4 + F(3 * 7 * 6, 5))])), True)
got = words("        DD(N), 1/7-3/11+1.4321E-2, .12+1/144", 2)
check("p.28 g", bool(approx(got, [normal(F(1, 7) - F(3, 11) + F(14321, 10 ** 6)),
                                  normal(F(12, 100) + F(1, 144))])), True)
check("p.28: 4 * $PI * 1E-7 has pi's exponent and first bits",
      words("        DD(N), 4 * $PI * 1E-7")[0] >> 20,
      normal(F(4) * F(3141592653589793238, 10 ** 18) * F(1, 10 ** 7)) >> 20)
check("$E", words("        DD(N), $E")[0] >> 20, normal(F(2718281828459045235, 10 ** 18)) >> 20)
check("$M", words("        DD(N), $M")[0] >> 20, normal(F(4342944819032518277, 10 ** 19)) >> 20)
check("$N", words("        DD(N), $N")[0] >> 20, normal(F(6931471805599453094, 10 ** 19)) >> 20)

# -- pp.28-29 Unnormalized --------------------------------------------------
got = words("        DD(U), (F21) -343.7, (F10) 432", 2)
check("p.28 a: (F21)-343.7, exponent 27 as printed, 343 joined to 21 bits, negative",
      got[0], fword(27, (343 << 21) + int(F(7, 10) * (1 << 21)), 8))
check("p.28 a: (F10)432: ten zeros at the right, entered at the bit before them",
      got[1], fword(38, 432 << 10))
got = words("        (F15)DD(U), 767.52, 767.52 X-12 S11", 2)
frac = int(F(76752, 100) * (1 << 15))
check("p.28 b: (F15) applies to both", got[0], fword(33, frac))
check("p.28 b: X overrules the exponent, S11 makes it negative", got[1], fword(-12, frac, 0o11))
got = words("        (F15)DD(U), 767.52, (F20) 767.52 S11 X-12, 398", 3)
check("p.29 c: a field's mode overrules, S and X in either order",
      got[1], fword(-12, int(F(76752, 100) * (1 << 20)), 0o11))
check("p.29 c: (F15) still applies to 398", got[2], fword(33, 398 << 15))
got = words("        DD(U), 17, 17X-35", 2)
check("p.29 a: an integer with no mode has exponent 48", got[0], fword(48, 17))
check("p.29 a: X-35", got[1], fword(-35, 17))
# The charts' result, not the exact one: C22-6729 p.109 boxes 36-38 and p.111 box 13
# make 17.5 175 x (1/10 truncated), so it is one unit low in 48 bits, and 1.0 and
# .5 likewise.  No printed word decides this; see docs/strap2/README.md.
check("p.29 b: 17.5 is normalized, by the charts just below 17.5",
      words("        DD(U), 17.5"), [fword(5, (1 << 48) * 35 // 64 - 1)])
check("the same: 1.0 is just below one", words("        DD(N), 1.0"), [fword(0, (1 << 48) - 1)])
check("1.E1 has no running exponent and is exact", words("        DD(N), 1.E1"), [fword(4, 5 << 45)])
check("p.29 note: 17 E 5 is an integer", words("        DD(U), 17 E 5"), [fword(48, 1700000)])
got = words("        DD(U), 17 E-5")[0]
check("p.29 note: 17 E-5 is a fraction and normalized", got >> 12, normal(F(17, 100000)) >> 12)
check("p.29 note: 17.5 E 5 is treated as a fraction and normalized", words("        DD(U), 17.5 E 5"), [normal(1750000)])
check("p.29 note: an integer above 2**48 is normalized",
      words("        DD(U), 1E15")[0] >> 12, normal(10 ** 15) >> 12)

# -- p.29 Binary signed ------------------------------------------------------
got = words("        (F7)DD(B,,4), .005E3S13, -17, 143.2S11, (8)77760, 777", 5)
check("p.29 a: the point and E cancel, S13 in a 4-bit byte", got[0], ((5 << 7) << 4) | 0o13)
check("p.29 a: -17 takes S10", got[1], ((17 << 7) << 4) | 0o10)
check("p.29 a: 143.2 at F7, truncated", got[2], (int(F(1432, 10) * 128) << 4) | 0o11)
check("p.29 a: octal overrules (F7) in the fourth field", got[3], 0o77760 << 4)
check("p.29 a: (F7) still applies to 777", got[4], (777 << 7) << 4)
got = words("        (2)DD(B,16,8), 1101101S377")[0] >> 48
check("p.29 b: 16 bits: eight of data, then the sign byte", got, (0b1101101 << 8) | 0o377)
got = words("        (F12)DD(B,24), 1.324E3, -72.1E-4, 3.4E-4S1")
check("p.29 c: F12, implied byte 1", got[0] >> 40, (1324 << 12) << 1)
got = words("        DD(B), 1489, -1272, (F13)-972.16, 13948S1, 12E5", 5)
check("p.29 d: FL 64, BS 1: 1489", got[0], 1489 << 1)
check("p.29 d: -1272 has the 1-bit sign", got[1], (1272 << 1) | 1)
check("p.29 d: a field's (F13)", got[2], (int(F(97216, 100) * (1 << 13)) << 1) | 1)
check("p.29 d: S1", got[3], (13948 << 1) | 1)
check("p.29 d: 12E5", got[4], 1200000 << 1)

# -- pp.29-30 Binary unsigned ------------------------------------------------
got = words("        (F13)DD(BU, 30), 17.2, 183, (8) 70707", 2)
v = (int(F(172, 10) * (1 << 13)) << 34) | ((183 << 13) << 4) | (0o70707 >> 26)
check("p.30 a: three 30-bit fields packed from the left", got[0], v)
check("p.29: a sign on BU is ignored", words("        DD(BU,24), -5")[0] >> 40, 5)

# -- p.30 Decimal -----------------------------------------------------------
got = words("        DD(D), -9534812, +173E5, 18E10S13", 3)
check("p.30 a: FL 64, BS 4, digits then a 4-bit sign", got[0], (0x9534812 << 4) | 8)
check("p.30 a: +173E5", got[1], 0x17300000 << 4)
check("p.30 a: 18E10S13", got[2], (0x180000000000 << 4) | 0o13)
check("p.30 b: a binary integer to decimal: 111010001101 is 3725",
      words("        (2)DD(D, 20), 111010001101S7")[0] >> 44, (0x3725 << 4) | 7)
check("p.30 c: four zeros in each byte's zone, then the sign byte",
      words("        DD(D, , 8), 432E3"), [0x0004030200000000])
got = words("        DD(DU), 8430051, (8) 77241, 82E10", 3)
check("p.30 DU a: 16 digits, no sign", got[0], 0x8430051)
check("p.30 DU a: octal to decimal", got[1], 0x32417)
check("p.30 DU a: 82E10", got[2], 0x820000000000)

# -- p.30 general parenthetical ----------------------------------------------
got = words("        DD(N), 572(.59)1, 347.89E12(.63, 2)1011", 2)
check("p.30 a: (.59)1 ORs bit 59", got[0], normal(572) | (1 << 4))
check("p.30 a: the sign byte by (.63,2)1011", got[1], normal(F(34789, 100) * 10 ** 12) | 0b1011)
p = strap2.assemble("        SLC,(8)100.0\nSAM     DD(BU,64),0\n        DD(B), (F9)-35.7(.24)SAM+4\n        END,(8)100.0\n")
want = (((int(F(357, 10) * 512) << 1) | 1) | ((((0o100 * 64) + 4) << 39) & ((1 << 64) - 1)))
check("p.30 b: an address in the first part, by the converted number", p.words[0o101], want)
got = words("        (8)DD(BU), 4762(.10)707(10, .20)34")[0]
check("p.30 c: 707 octal, 34 decimal", got, 0o4762 | (0o707 << 53) | (34 << 43))
check("p.30 d: 111 ORed into the high bits of each 12-bit field",
      words("        DD(BU, 12(.2)7, 8), 787, 788")[0] >> 40, ((0o7000 | 787) << 12) | (0o7000 | 788))

# -- MCP printed p.359: the powering, printed by STRAP II --------------------
check("p.359 line 38: 1.E32 prints 0153+ 4734265552025560: dropped bits begin with a 1, truncated",
      words("        DD(N), 1.E32")[0], (0o0153 << 53) | (0o4734265552025560 << 4))
check("p.359 line 39: 1.E64 prints 0325+ 6047403722377717",
      words("        DD(N), 1.E64")[0], (0o0325 << 53) | (0o6047403722377717 << 4))
check("p.359 line 40: 1.E128 prints 0652+ 4473510762300351",
      words("        DD(N), 1.E128")[0], (0o0652 << 53) | (0o4473510762300351 << 4))
try:
    words("        DD(N), 1.E512")
    check("1.E512 is refused: p.359 prints a word no cited rule gives", "assembled", "refused")
except strap2.StrapError as err:
    check("1.E512 is refused: p.359 prints a word no cited rule gives", "113:" in str(err) or "exponent" in str(err), True)

check("a null field is zero (C22-6531 p.7)", words("        DD(BU,32),,,")[0], 0)
check("(F4) on an 8-bit field", words("        (F4)DD(BU,8), 3")[0] >> 56, 3 << 4)

# -- C22-6729 p.34: a length resting on a later symbol (14I-14J) ---------------
p = strap2.assemble("""
        SLC,(8)100.0
A       DD(BU,K),1,2
B       DD(BU,8),9
K       SYN,F-G
G       DD(BU,8),0
F       DD(BU,8),0
H       DD(BU,3),0
        END,(8)100.0
""")
check("p.34: B stands 2 x K bits past A, K found only after Pass 2a's B", p.symtab["B"], 0o100 * 64 + 16)
check("the bits: 1 and 2 in 8-bit fields, then 9", p.words[0o100] >> 40, (1 << 16) | (2 << 8) | 9)
p = strap2.assemble("""
        SLC,(8)100.0
A       (A*)DD(BU,,K),AB*
B       DD(BU,8),9
K       SYN,F-G
G       DD(BU,8),0
F       DD(BU,8),0
        END,(8)100.0
""")
check("alphabetic: two characters at a later b.s.", p.symtab["B"], 0o100 * 64 + 16)

# -- A field length over 64: C22-6729 p.176 (message 36, MAIN) and p.137 box
# 20, "an error message to be given and the field length to be truncated",
# read in the ink 2026-11-12.  READ: truncated in the dds's six-bit field
# (0 for 64), the high bits dropped as C28-6129 p.33 uses the word: 72 is 8.
r = strap2.compile_cards(["         SLC,(8)100.0",
                          " A       DD(BU,72),(8)040002001000010000400004",
                          " B       DD(BU,64),1", "         END"])
check("DD(BU,72): message 36, FIELD LENGTH GREATER THAN 64",
      [n for n, *_ in r.msg.items], [36])
check("DD(BU,72): the length truncated to 8, so B starts at 100.08 and A holds 004",
      (r.val.symbol_value(r.st.search("B"))[0], r.image.words[0o100] >> 56),
      (0o100 * 64 + 8, 0o004))
r = strap2.compile_cards(["         SLC,(8)100.0", " A       DD(BU,64),1", "         END"])
check("DD(BU,64): no message", [n for n, *_ in r.msg.items], [])
# Messages 37 and 38 (p.176; p.137 boxes 20, 29, read in the ink 2026-11-12).
def msgs(dd):
    r = strap2.compile_cards(["         SLC,(8)100.0", " A       " + dd,
                              " B       DD(BU,8),1", "         END"])
    return [n for n, *_ in r.msg.items], r.val.symbol_value(r.st.search("B"))[0], r.punch.unwritten
got = msgs("DD(BU,64,9),5")
check("DD(BU,64,9): message 37, and the deck refuses (the truncation is not printed)",
      (got[0], bool(got[2])), ([37], True))
check("DD(BU,64,8): no message", msgs("DD(BU,64,8),5")[0], [])
check("(CC*)DD(BU,,12): no message 37 -- p.30, CC implies BS = 12 (MCP p.2 line 4 writes it)",
      37 in msgs("(CC*)DD(BU,,12),AB*")[0], False)
got = msgs("DD(BU,.40),5")
check("DD(BU,.40): message 38, and the combined value, 40 bits, is the length (B at 100.40)",
      got[:2], ([38], 0o100 * 64 + 40))
check("DD(BU,64,.8): message 38 for a bit-style byte size", msgs("DD(BU,64,.8),5")[0], [38])

# -- DDI: C28-6129 printed pp.16-17, read in the ink 2026-11-12 -------------
# "IDATA DDI(DU, 4, 4), 4 / LI, IDATA": the symbol table holds ...0100; LI's
# address field 0100 then zeros; LI(DU, 8, 4) gives 00000100...; LI(D, 8, 4),
# -IDATA gives 01001000....  "purely definitive ... no space or binary output".
def ddi(*body):
    r = strap2.compile_cards(["         SLC,(8)100.0", " IDATA   DDI(DU, 4, 4), 4"]
                             + list(body) + ["         END"])
    return r, r.image.words.get(0o100, 0) >> 40
r, a = ddi("         LI, IDATA")
check("p.17: the symbol table holds 4, right justified in 24 bits",
      r.val.symbol_value(r.st.search("IDATA"))[:2], (0, 4))
check("p.17: LI, IDATA compiles 0100 left justified", a, 0b0100 << 20)
check("p.17: DDI compiles no space: LI is the only word, at 100",
      sorted(r.image.words), [0o100])
check("p.17: LI(DU, 8, 4), IDATA compiles 00000100", ddi("         LI(DU, 8, 4), IDATA")[1], 0b00000100 << 16)
check("p.17: LI(D, 8, 4), -IDATA compiles 01001000 (magnitude, then the sign byte)",
      ddi("         LI(D, 8, 4), -IDATA")[1], 0b01001000 << 16)
r = strap2.compile_cards(["         PUNREL", " K       DDI(BU,24), (8)7777", "         LI,K",
                          "         END"])
check("a DDI's value is an integer: under PUNREL it is not relocated",
      [c.codes for c in r.punch.cards if c.kind == "rinstr"], ["00"])
r = strap2.compile_cards(["         SLC,(8)100.0", " F       DDI(N), 5", "         END"])
check("p.17: a floating point use mode is not acceptable: the deck refuses",
      bool(r.punch.unwritten), True)

print("ALL CHECKS PASSED" if not fails else f"{fails} FAILED")
sys.exit(1 if fails else 0)
