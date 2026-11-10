#!/usr/bin/env python3
"""check_strap2.py -- what strap/strap2 does because the guide says so, which
strap_asm does not do at all: the origin, the two location counters, real tails,
the unit's bit format, UITER's circular and undefined rules, ambiguous operations.
Values written by hand from the pages cited.

Injections, measured 2026-11-09, each reverted from a saved copy and compared:
  written tail ignored            only B1
  special symbol ignores FL       C1-C3, then a KeyError at C4
  special symbol not rounded      only C7, C8
  origin 0, not 41 octal          only A1, A2, A3
  no zero for a circular symbol   a KeyError at part E
  implicit floating lost          only F1, F2
  the two-field VFL rule lost     only F4
  undefined symbols half apart    only G2, G3 (G3 re-measured 2026-11-09)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
import strap_asm                # noqa: E402
import strap2                   # noqa: E402
from strap2.cards import deck_cards     # noqa: E402
from strap2 import unit as U    # noqa: E402

fails = 0


def check(label, got, want):
    global fails
    ok = got == want
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} {label}" + ("" if ok else f": got {got!r} want {want!r}"))


def W(n, b=0):
    return n * 64 + b


# ---- A. p.33: with no SLC the absolute counter starts at 41 octal.  MCP p.48.
deck = open(os.path.join(HERE, "..", "decks", "mcpref_example2.strap")).read()
with_slc = strap2.assemble(deck)
lines = [ln for ln in deck.splitlines() if not ln.split("!")[0].strip().upper().startswith("SLC")]
without = strap2.assemble("\n".join(lines))
check("A1 p.48 with its transcription SLC removed gives the same image",
      without.words == with_slc.words, True)
check("A2 START is at 000041.00 with no SLC", without.symtab["START"], W(0o41))
check("A3 the END transfer is START (p.48 END prints 000041.00)", without.end_pc, W(0o41) // 32)

# ---- B. pp.74-75, 123-125: tails are real, and written tails override.
p = strap2.assemble("""
        TAIL, A
X       SYN, 1
        UNTAIL, (1)
        TAIL, B
X       SYN, 2
Y       SYN, X$A
Z       SYN, X
        UNTAIL, (1)
V       SYN, X
X       SYN, 3
""")
check("B1 X under tail A and X under tail B are two symbols",
      (p.symtab["Y*02"], p.symtab["Z*02"]), (1, 2))
check("B2 X with no tail is a third", p.symtab["V"], 3)

# ---- C. pp.13, 19, 33-34: the symbolic counter.  A dimension that rests on a
# later symbol gets a new special symbol, and locations cascade from it.
p = strap2.assemble("""
        SLC, (8)100.0
A       DR(BU,64), (N)
B       XW, 0, 0, 0
C       B, H1
H1      B, C
        SLC, (8)200.0
G       DD(BU,8), 1
F       DD(BU,8), 1
N       SYN, F-G
        END, A
""")
check("C1 N is known only after Pass 2a, and the DR takes 8 words", p.symtab["B"], W(0o110))
check("C2 C follows B", p.symtab["C"], W(0o111))
check("C3 H1 a half word on", p.symtab["H1"], W(0o111, 32))
check("C4 C's branch holds H1, through the special symbol", p.words[0o111] >> 32,
      strap_asm.enc_branch_or_misc(W(0o111, 32) >> 5, strap_asm.UNCOND_BRANCH_CODES["B"], False, 0))

p = strap2.assemble("""
        SLC, (8)100.0
A       DR(BU,3), (N)
B       XW, 0, 0, 0
E       DD(BU,8), 1
N       SYN, 5
""")
check("C6 rounding under no special symbol: 15 bits round to a word for XW",
      p.symtab["B"], W(0o101))

p = strap2.assemble("""
        SLC, (8)100.0
A       DR(BU,3), (N)
B       XW, 0, 0, 0
D       DD(BU,8), 1
        SLC, (8)200.0
G       DD(BU,8), 1
F       DD(BU,8), 1
N       SYN, F-G
""")
check("C7 p.33: a full word wanted under a special symbol not at one: 8 x 3 bits "
      "rounds up", p.symtab["B"], W(0o101))
check("C8 the label after it stands on the rounded symbol", p.symtab["D"], W(0o102))
p = strap2.assemble("""
        SLC, (8)100.0
A       DR(BU,3), (N)
D       DD(BU,8), 1
        SLC, (8)200.0
G       DD(BU,8), 1
F       DD(BU,8), 1
N       SYN, F-G
""")
check("C9 no rounding wanted: D is 24 bits on", p.symtab["D"], W(0o100, 24))

# ---- D. SLC may rest on a later symbol in STRAP II, by the same counter.
p = strap2.assemble("""
        SLC, HERE
A       B, A
HERE    SYN, (8)200.0
""")
check("D1 an SLC on a later SYN", p.symtab["A"], W(0o200))

# ---- E. p.32, C28-6129 p.21: circular definitions.
p = strap2.assemble("A SYN,B\nB SYN,A+5\n", strict=False)
check("E1 A SYN,B; B SYN,A+5 gives A=0", p.symtab["A"], 0)
check("E2 ... and B=5", p.symtab["B"], 5)

# ---- F. pp.22, 24, 140: an ambiguous operation.
base = "        SLC, (8)100.0\n{}\nN       B, N\nX       DD(N), 1.0\n"
imp = strap2.assemble(base.format("        L, X"))
exp = strap2.assemble(base.format("        L(N), X"))
vfl = strap2.assemble(base.format("        L(BU,64,8), X"))
check("F1 L on a floating symbol is floating, as L(N) (half word)", imp.words, exp.words)
check("F2 ... so the next label is a half word on", imp.symtab["N"], W(0o100, 32))
check("F3 L(BU,64,8) is a full word", vfl.symtab["N"], W(0o101))
two = strap2.assemble(base.format("        L, X, 3"))
check("F4 p.24: two fields make it VFL", two.symtab["N"], W(0o101))

# ---- G. p.205, C28-6129 p.20: undefined symbols.
src = "        SLC, (8)100.0\nA       XW, U1, 0, 0\nB       XW, U2, 0, 0\nC       XW, U1, 0, 0\n"
try:
    strap2.assemble(src)
    check("G1 strict refuses an undefined symbol", False, True)
except strap_asm.AssemblerError:
    check("G1 strict refuses an undefined symbol", True, True)
p = strap2.assemble(src, strict=False)
check("G2 pseudo-defined: next full word above the upper limit, in order",
      (p.symtab["U1"], p.symtab["U2"]), (W(0o103), W(0o104)))
p2 = strap2.compile_cards(deck_cards(src))
check("G3 NUNDSY lists both, at their addresses (chart EG boxes 4, 8, 9)",
      p2.lists["undefined"], [("U1", W(0o103)), ("U2", W(0o104))])

# ---- H. Fig. 20 p.189: the unit, read back as bits.
p2 = strap2.compile_cards(deck_cards(
    "NAME    L(BU,7,8), NAME+1 ' A REMARK\n        END, NAME\n"), 0o100 * 64)
units = list(p2.units.intin())
u = p2.units
check("H1 two units", len(units), 2)
n = units[0]
check("H2 ZIFNME on the named unit", u.get(n, U.ZIFNME), 1)
check("H3 ZIFBO, ZIFP2", (u.get(n, U.ZIFBO), u.get(n, U.ZIFP2)), (1, 1))
check("H4 ZINFLD", u.get(n, U.ZINFLD), 1)
check("H5 ZIDDS is mode 101, f.l. 7, b.s. 8", u.get(n, U.ZIDDS), 0b1010001111000)
check("H6 ZIADAB is the absolute counter", u.get(n, U.ZIADAB), W(0o100))
coded = u.get(n, U.ZILCFD)
at = (n + U.FIXED_BITS + coded + 63) // 64 * 64
text = "".join(chr(p2.mem.get(at + 8 * k, 8)) for k in range(u.get(n, U.ZILSST)))
check("H7 p.25: the image at the next full word after unit + fixed + ZILCFD",
      text, "L(BU,7,8), NAME+1 ' A REMARK")
check("H8 the control word's refill reaches the next unit",
      u.get(n, U.CW_REFILL) * 64, units[1])
check("H9 the name's check digit", u.get(n, U.ZINAME), 1)

# ---- I. p.25: $ before the instruction is suppress e.m.
p2 = strap2.compile_cards(deck_cards("        $B, 0\n"), 0o100 * 64)
check("I1 bit p of the ZIOPX word", p2.units.get(next(iter(p2.units.intin())), U.ZISUPP), 1)

print("ALL CHECKS PASSED" if not fails else f"{fails} CHECK(S) FAILED")
sys.exit(1 if fails else 0)
