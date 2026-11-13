#!/usr/bin/env python3
"""check_strap2_subscripts.py -- STRAP II's array subscripts on a DR symbol.

Source, read in the ink 2026-11-12: C28-6129 printed p.40 (PDF 44), DR item 9:
  "A DR(dds), (L, L', L'', ..., L^r) reserves space for an L x L' x L'' ... array
  of data fields ... Any symbol A appearing in the name field is attached to the
  first element of the array, and the dds is attached to the symbol ... a
  specific element of the array may be addressed by writing: A(q, q', ..., q^r)
  ... the first element of the array has the address: A(0,0,0,...,0) ...
  Address of A(q,q',q'',...,q^r) = Address of A(0,0,...0) + FL x (q + q'L +
  q''LL' + q'''LL'L'' + ...) where FL is the field length of any element".
  "to apply index register I to the second element of a one dimensional array
  A, write: A(1)(I)".  "SYN must be used to define a symbol as an interior
  element ... and have the dimensional addressing properties carried along.
  A DR(N), (10,20) / B SYN, A(5,5) ... A(0,0) - B(-5,-5); A(1,0) - B(-4,-5);
  A(1,1) - B(-4,-4)".

Before this, strap2 took every parenthesized entry after a symbol as an index
register: L,T(2,1) on a 3 x 4 array assembled as T($1).

The coded expression keeps no parentheses between the subscripts and the
index (C22-6729 pp.198-199); what decides is how an entry is written.  A last
entry in bit style is the index ("A(1)(I) where I must be a bit address"),
the integers are subscripts.  In the ink: MCP printed p.334 line 35,
YLJM1($9) on YLJM1 DRZ(BU),(4), prints 235410.00 89, and printed p.129 line 2,
KCSREG($11) on a DRZ(BU,64),1, prints 216312.00 8B (both decks' !CHECKs);
C22-6729 p.177's 71 SUBSCRIPT WRITTEN AS BIT and 75 1 SUBS. TOO MANY, LAST
USED AS INDEX.  A wrong count takes the recovery p.177's text names: 75 the
last used as the index, 76 the extras ignored, 77 the others taken 0; none is
serious (p.176; N28-1081 page 13), each given once per statement.  NOT
WRITTEN, refused: message 71, whose recovery is not printed.  (A first draft let the count decide; it refused
both MCP decks, caught by the suite.)

MEASURED INJECTIONS, 2026-11-12, value.py / pass1.py / pass2.py restored by
copy and cmp, PYTHONDONTWRITEBYTECODE=1, control all 22 passing, observed:
  every entry an index (the old      19: all but T(0,0), W($4) and p.40's
    behaviour)                       A(0,0) pair
  a DR's dimensions not attached     the same 19
  a SYN does not carry them          U(1,1) and the three p.40 B(...) checks
  the dimensions reversed            T(2,1), T(2,3), T(2,1)($3), U, U(1,1),
                                     T(2,1,3), T(2,1,3,4), T(2,1,3)($4), and
                                     p.40's B and A(9,19)
  each dimension one less            the same 10
  a word stride, not FL              13: the T, U and W checks with a nonzero
                                     offset, and B SYN,T(1)
  a bit-style entry not the index    T(2,1)($3), W(1)($4), W($4),
                                     T(2,1,3)($4), T(2,$1)
  75 not given / its last entry      only T(2,1,3), each
    not the index
  76 not given / extras kept as      T(2,1,3,4) and T(2,1,3)($4), each
    the index
  77 not given                       T(2,$1), T(1), B SYN,T(1), and both
                                     line checks
  VALUE's notes never given          the eight message checks
  notes given at each evaluation     T(2,1,3), T(2,1,3,4), T(2,1,3)($4),
                                     T(2,$1), T(1)
  a referenced SYN's notes kept      only "L,B before B SYN,T(1)" (77 printed
                                     on L,B's line too: found by review
                                     of the first commit, bf14a7d)
  notes not cleared in unit_a        UNDETECTED: with a referenced SYN's
                                     notes dropped, none is left over; the
                                     clear is kept as hygiene
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
import strap2                   # noqa: E402
from strap2.listing import listing_of            # noqa: E402

fails = 0


def check(label, got, want):
    global fails
    ok = got == want
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} {label}: got {got!r}" + ("" if ok else f", want {want!r}"))


HEAD = ["         SLC,(8)100.0", " T       DR(BU,16),(3,4)", " U       SYN,T(1,1)",
        " V       DR(N),10", " W       DR(BU,8),5",
        " BB      SYN,1.32"]


def printed(stmt):
    """The statement's first address field and index, as the listing prints."""
    try:
        r = strap2.compile_cards(HEAD + ["         " + stmt, "         END"])
    except (strap2.StrapError, strap2.optable._a.AssemblerError) as x:
        return "refused: " + str(x).split(":")[0]
    lines = listing_of(r, r.p1.print_names).text("0", 1).splitlines()
    line = next(ln for ln in lines if ln.rstrip().endswith(stmt))
    got = " ".join(line.split()[2:4])
    return got + "".join(f" +{n}" for n, *_ in r.msg.items)


check("L,T(0,0): the first element is T", printed("L,T(0,0)"), "000100.00 80")
check("L,T(2,1): T + 16 x (2 + 1 x 3) = 101.20", printed("L,T(2,1)"), "000101.20 80")
check("L,T(2,3): T + 16 x (2 + 3 x 3) = 102.60", printed("L,T(2,3)"), "000102.60 80")
check("L,T(2,1)($3): one more entry is the index", printed("L,T(2,1)($3)"), "000101.20 83")
check("L,U: U SYN,T(1,1) is T + 16 x 4", printed("L,U"), "000101.00 80")
check("L,U(1,1): U carries T's dimensions", printed("L,U(1,1)"), "000102.00 80")
check("L,W(2): one dimension, 8-bit fields", printed("L,W(2)"), "000115.20 80")
check("L,W(1)($4): p.40's A(1)(I)", printed("L,W(1)($4)"), "000115.10 84")
check("L,W($4): a lone bit-style entry is the index (MCP p.334 YLJM1($9))",
      printed("L,W($4)"), "000115.00 84")
check("L,T(2,1,3): message 75, the last used as the index",
      printed("L,T(2,1,3)"), "000101.20 83 +75")
check("L,T(2,1,3,4): message 76, the extras ignored", printed("L,T(2,1,3,4)"), "000101.20 80 +76")
check("L,T(2,1,3)($4): message 76, the index kept", printed("L,T(2,1,3)($4)"), "000101.20 84 +76")
check("L,T(2,$1): the bit-style entry is the index; 77, the other taken 0",
      printed("L,T(2,$1)"), "000100.40 81 +77")
check("L,T(BB,2), BB 1.32: a bit-style subscript, refused (71 not written)",
      printed("L,T(BB,2)"), "refused: a subscript written as a bit address")
check("L,T(1): message 77, the others taken 0", printed("L,T(1)"), "000100.20 80 +77")

r = strap2.compile_cards(["         SLC,(8)100.0", " A       DR(N),(10,20)", " B       SYN,A(5,5)",
                          " P       SYN,A(0,0)", " Q       SYN,B(-5,-5)", " R       SYN,A(1,0)",
                          " S       SYN,B(-4,-5)", " X       SYN,A(9,19)", " Y       SYN,B(4,14)",
                          "         END"])


def at(n):
    return oct(r.val.symbol_value(r.st.search(n))[0] // 64)


check("p.40: B SYN,A(5,5) is A + 5 + 5 x 10 words", at("B"), oct(0o100 + 55))
check("p.40: A(0,0) and B(-5,-5) are one storage", (at("P"), at("Q")), (oct(0o100),) * 2)
check("p.40: A(1,0) and B(-4,-5)", (at("R"), at("S")), (oct(0o101),) * 2)
r77 = strap2.compile_cards(["         SLC,(8)100.0", " T       DR(BU,16),(3,4)", " B       SYN,T(1)",
                            "         END"])
check("B SYN,T(1): message 77 on the SYN, B is T + 16",
      ([n for n, *_ in r77.msg.items], oct(r77.val.symbol_value(r77.st.search("B"))[0])),
      ([77], oct(0o100 * 64 + 16)))
def lines77(cards):
    r = strap2.compile_cards(["         SLC,(8)100.0", " T       DR(BU,16),(3,4)"] + cards
                             + ["         END"])
    text = listing_of(r, r.p1.print_names).text("0", 1)
    return [ln.split()[3] for ln in text.splitlines() if ln.rstrip().endswith(" 77")]


check("L,B before B SYN,T(1): 77 on the SYN's line only (line 4)",
      lines77(["         L,B", " B       SYN,T(1)"]), ["4"])
check("L,B after B SYN,T(1): 77 on the SYN's line only (line 3)",
      lines77([" B       SYN,T(1)", "         L,B"]), ["3"])
check("p.40: A(9,19), the last element, and B(4,14)", (at("X"), at("Y")), (oct(0o100 + 199),) * 2)

print("ALL CHECKS PASSED" if not fails else f"{fails} FAILED")
sys.exit(1 if fails else 0)
