#!/usr/bin/env python3
"""check_strap2_flags.py -- STRAP II's symbol error flags, MULTI and NUNDSY, from
the pages' own examples, all read in the ink:

  C28-6129 printed pp.20-21 (PDF 24-25): the five flags and their examples.
  N28-1081 page 7 (C28-6129 PDF 65), April 1963: MULTI before BOTH definitions,
    CONTAG before an instruction referring to a multiply defined symbol.
  C22-6729 p.25 (the flags ORed into the unit; VALUE reports them), p.32 (UITER
    marks circular and contagious, zero to a chain's base), p.126 chart RE and
    p.127 (MULTI), p.157 box 2, pp.170-172 charts EG, EH (NUNDSY).

No STRAP II listing that survives prints a flag or a list, and the MCP listing
(March 1963) predates the update.  So everything here is checked against the
text and charts, not against a listing.

Where the pages disagree, the test pins one and says which:
  * C28-6129 p.20 calls `SYMBOL LI,...` then `SYMBOL SYN,1000.0` QUEST.  Chart RE
    boxes 1 and 12 make a repeat legal only when both are SYN, so strap2 follows
    the chart: MULTI.
  * C28-6129 p.21 (5) says A gets 500.0 from `A SYN,1000.0; A SYN,500.0`; its own
    (3) and the guide p.127 say the first value stands.  Pinned: 1000.0.
  * C28-6129 p.21 (5) puts MULTI before the Add that refers to A; N28-1081 page 7
    puts CONTAG there.  Both are run, by edition.

MEASURED INJECTIONS, 2026-11-09, PYTHONDONTWRITEBYTECODE=1, each reverted from a
saved copy compared with cmp.  Failing checks, control all passing:
  flags never ORed into the unit:      A1, A2, A2a, A8, B1-B3, B9, C1, C6, D4, D5,
                                       E1, E2, E4, E5, E7
  QUEST and MULTI swapped:             B1-B3, B9, C1, C6, E1, E2, E5
  editions' reference flag swapped:    E1, E2, E4
  C28-6129's MULTI on both definitions: C6
  the used bit ignored:                A5, A10
  no circular list:                    D2
  lists after the seconds:             A9, A10
  MULTI's equal-value test missing:    B1-B7, B10
  contagion never marked:              D3, D5, E1, E4, E7
  no OR in Pass 2b:                    E7
  the old index not kept:              B8
  the old dds not kept:                B10, B10a
  undefined symbols a half word apart: A4, A10 (and check_strap2 G2, G3)
  SPNUS ignored:                       A12
  no message 131:                      B5
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
import strap2                                    # noqa: E402
from strap2 import compile_cards                 # noqa: E402
from strap2.cards import deck_cards              # noqa: E402
from strap2.listing import listing_of            # noqa: E402

fails = 0


def check(label, got, want):
    global fails
    ok = got == want
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} {label}" + ("" if ok else f": got {got!r} want {want!r}"))


def W(n, b=0):
    return n * 64 + b


def run(src, edition="N28-1081"):
    p2 = compile_cards(deck_cards(src), edition=edition)
    return p2, listing_of(p2, p2.p1.print_names)


def flags_before(lst, statement):
    """The flags on the line before the first line whose statement is this."""
    for k, ln in enumerate(lst.lines):
        if not ln.flags and ln.statement.replace(" ", "") == statement:
            prev = lst.lines[k - 1] if k else None
            return prev.flags if prev is not None and prev.flags else []
    raise KeyError(statement)


def value(p2, name):
    st = p2.st
    f = st.dictionary[name]
    return st.get(f, "ZVALB") + st.get(f, "ZVALI")


def refused(src):
    try:
        strap2.assemble(src)
        return False
    except strap2.StrapError:
        return True


# ---- A. UNDEF, C28-6129 p.20 (1).
src = ("        SLC, (8)100.0\n"
       "A       XW, U1, 0, 0\n"
       "B       XW, U2, 0, 0\n"
       "C       XW, U1, 0, 0\n"
       "        END, A\n")
p2, lst = run(src)
check("A1 UNDEF before the statement holding U1", flags_before(lst, "XW,U1,0,0"), ["UNDEF"])
check("A2 UNDEF before the one holding U2", flags_before(lst, "XW,U2,0,0"), ["UNDEF"])
check("A2a UNDEF before C's, which holds U1 again",
      [ln.flags for ln in lst.lines if ln.flags], [["UNDEF"]] * 3)
check("A3 none before END,A", flags_before(lst, "END,A"), [])
check("A4 the undefined list, at the full words after the last used, in order",
      p2.lists["undefined"], [("U1", W(0o103)), ("U2", W(0o104))])
check("A5 B and C never used, listed with addresses (chart EH boxes 18B-22)",
      p2.lists["unused"], [("B", W(0o101)), ("C", W(0o102))])
check("A6 COMREC 7.41 on (p.8)", 41 in p2.comrec_errors(), True)
check("A7 strict refuses it", refused(src), True)
text = lst.text()
lines = text.splitlines()
check("A8 the flag line has no line number",
      [s for s in lines if s.strip() == "UNDEF"], ["    UNDEF"] * 3)
check("A9 the seconds are the last item (C28-6129 p.20)", "SECONDS" in lines[-1], True)
check("A10 the lists come after the statements, undefined first",
      lines[-6:-1], ["U1  000103.00", "U2  000104.00", "SYMBOLS DEFINED BUT NOT USED",
                     "B  000101.00", "C  000102.00"])
check("A11 the statements are numbered through, flags not counted",
      [ln.number for ln in lst.lines if not ln.flags], [1, 2, 3, 4, 5])

# SPNUS suppresses the unused list (chart EG box 10A, p.172).
p2, _ = run("        SPNUS\n" + src)
check("A12 SPNUS: no unused list", p2.lists["unused"], [])

# ---- B. QUEST, guide p.127: A SYN,32.0 and A SYN(BU,32),32.0($2) are legal.
src = ("        SLC, (8)100.0\n"
       "A       SYN, 32.0\n"
       "A       SYN(BU,32), 32.0($2)\n"
       "        L, A\n"
       "        END, 0\n")
p2, lst = run(src)
st = p2.st
f = st.dictionary["A"]
check("B1 QUEST before the first definition", flags_before(lst, "SYN,32.0"), ["QUEST"])
check("B2 QUEST before the second", flags_before(lst, "SYN(BU,32),32.0($2)"), ["QUEST"])
check("B3 QUEST before the reference (p.25: VALUE reports it)", flags_before(lst, "L,A"), ["QUEST"])
check("B4 the value, and the index the second gave (p.127)",
      (value(p2, "A"), st.get(f, "ZX"), st.get(f, "ZXQ")), (W(32), 2, 1))
check("B5 message 131 once (chart EG box 13)",
      [m[0] for m in p2.msg.items], [131])
check("B6 not on the multiply-defined list", p2.lists["multiple"], [])
check("B7 COMREC 7.41 off, so strict accepts it", refused(src), False)

# The old definition's index holds (chart RE boxes 20-22).
p2, _ = run("A       SYN, 32.0($3)\nA       SYN, 32.0\n        END, 0\n")
f = p2.st.dictionary["A"]
check("B8 the first definition's index holds", (p2.st.get(f, "ZX"), p2.st.get(f, "ZXQ")), (3, 1))

# ... and so does its dds (chart RE boxes 14, 16; p.127 "not possible to overrule").
p2, _ = run("A       SYN(N), 32.0\nA       SYN(BU,32), 32.0\n        END, 0\n")
f = p2.st.dictionary["A"]
check("B10 the first definition's dds holds",
      p2.st.get(f, "ZDDS"), p2.st.get(p2.st.get(f, "ZOLDF"), "ZDDS"))
check("B10a ... and differs from the second's, so B10 tells",
      p2.st.get(f, "ZDDS") != strap2.optable.dds13("BU", 32, 8), True)

# C28-6129 p.20's own QUEST example, a label and a SYN: chart RE says MULTI.
src = ("        SLC, 1000.0\n"
       "SYMBOL  B, 0\n"
       "        SLC, 1001.0\n"
       "SYMBOL  SYN, 1000.0\n"
       "        END, 0\n")
p2, lst = run(src)
check("B9 p.20's label-and-SYN is MULTI by chart RE boxes 1, 12, not p.20's QUEST",
      (flags_before(lst, "B,0"), flags_before(lst, "SYN,1000.0"), p2.lists["multiple"]),
      (["MULTI"], ["MULTI"], [("SYMBOL", None)]))

# ---- C. MULTI, C28-6129 p.21 (3): A SYN,100.0; A SYN,100.32.
src = ("A       SYN, 100.0\n"
       "A       SYN, 100.32\n"
       "        L, A\n"
       "        END, 0\n")
p2, lst = run(src)
check("C1 N28-1081: MULTI before both definitions",
      (flags_before(lst, "SYN,100.0"), flags_before(lst, "SYN,100.32")), (["MULTI"], ["MULTI"]))
check("C2 the first value stands (p.21 (3), guide p.127)", value(p2, "A"), W(100))
check("C3 each SYN line prints its own definition's value",
      [ln.location for ln in lst.lines if ln.statement.startswith("SYN")],
      ["000144.00+", "000144.40+"])  # 100 decimal is 144 octal
check("C4 on the multiply-defined list once", p2.lists["multiple"], [("A", None)])
check("C5 strict refuses it", refused(src), True)
p2, lst = run(src, edition="C28-6129")
check("C6 C28-6129: MULTI before the second definition only",
      (flags_before(lst, "SYN,100.0"), flags_before(lst, "SYN,100.32")), ([], ["MULTI"]))

# Guide p.127: B L,JOE; B L,JOE($2): the first B is used in all references.
p2, _ = run("JOE     DR(N), 1\nB       L, JOE\nB       L, JOE($2)\n        B, B\n        END, 0\n")
check("C7 p.127: two labels contradict; the first stands",
      (p2.lists["multiple"], value(p2, "B")), ([("B", None)], W(0o42)))

# ---- D. PSEUDO, C28-6129 p.21 (4): A SYN,B; B SYN,A+5 gives A=0, B=5.
src = ("A       SYN, B\n"
       "B       SYN, A+5\n"
       "        END, 0\n")
p2, lst = run(src)
check("D1 A=0, B=5", (value(p2, "A"), value(p2, "B")), (0, 5))
check("D2 the circular list names the base, A", p2.lists["circular"], [("A", None)])
check("D3 B, defined through A, is contagious (p.32)",
      p2.st.get(p2.st.dictionary["B"], "ZSTCTG"), 1)
check("D4 PSEUDO before B's line, which refers to A", flags_before(lst, "SYN,A+5"), ["PSEUDO"])
check("D5 PSEUDO and CONTAG before A's: its definition, and B in it",
      flags_before(lst, "SYN,B"), ["PSEUDO", "CONTAG"])
check("D6 strict refuses it", refused(src), True)

# ---- E. CONTAG, C28-6129 p.21 (5).
src = ("        SLC, 500.0\n"
       "A       SYN, 1000.0\n"
       "A       SYN, 500.0\n"
       "B       SYN, A\n"
       "        L(N), B\n"
       "        +(N), A\n"
       "        END, 0\n")
p2, lst = run(src, edition="C28-6129")
check("E1 C28-6129: MULTI before the Add, CONTAG before the Load, as p.21 prints",
      (flags_before(lst, "+(N),A"), flags_before(lst, "L(N),B")), (["MULTI"], ["CONTAG"]))
check("E2 B's own line: it refers to A", flags_before(lst, "SYN,A"), ["MULTI"])
check("E3 A and B are 1000.0, against p.21's 500.0 (p.21 (3), p.127)",
      (value(p2, "A"), value(p2, "B")), (W(1000), W(1000)))
p2, lst = run(src)
check("E4 N28-1081: CONTAG before both the Add and the Load",
      (flags_before(lst, "+(N),A"), flags_before(lst, "L(N),B")), (["CONTAG"], ["CONTAG"]))
check("E5 N28-1081: MULTI before both definitions of A",
      (flags_before(lst, "SYN,1000.0"), flags_before(lst, "SYN,500.0")), (["MULTI"], ["MULTI"]))
check("E6 the CONTAG of a reference does not reach the lists", p2.lists["circular"], [])

# Contagion through an undefined symbol is found only in the second UITER, so
# 2b's flags count (CHOSEN, pass2.unit_b).
p2, lst = run("B       SYN, U+1.0\n        L, B\n        END, 0\n")
check("E7 B through undefined U: CONTAG on L,B and UNDEF on B's own line",
      (flags_before(lst, "L,B"), flags_before(lst, "SYN,U+1.0")), (["CONTAG"], ["UNDEF"]))

# ---- F. the edition is checked.
try:
    compile_cards(deck_cards("        END, 0\n"), edition="1965")
    check("F1 an unknown edition is refused", False, True)
except ValueError:
    check("F1 an unknown edition is refused", True, True)

print("flags: all passed" if not fails else f"{fails} CHECK(S) FAILED")
sys.exit(1 if fails else 0)
