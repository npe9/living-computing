#!/usr/bin/env python3
"""check_field_arithmetic.py -- *, / and parentheses in a field, as STRAP II
compiles them, in both assemblers (G3.1, docs/source_audit.md).

THE PAGES, read in the page images 2026-11-16:
  C22-6729 printed p.198 (Appendix C): the operator codes are "111 .+ ...
  110 .L ... 101 .R ... 100 U-, a unitary - ... 011 * 010 / 001 + 000 -".
  Eight codes fill the 3-bit field, and "**" is not one of them.
  C22-6729 printed p.107 (MQDNUM): "The current arithmetic operations which
  may be specified on a numeric DD are: First order operations +(addition)
  -(subtraction)  Second order operations *(multiplication) /(division)
  Third order operations **(powering)", and "in powering the exponent must
  be an integer in the range 2^-18 < n < 2^+18".  So "**" belongs to a
  NUMERIC DD alone, which MQDNUM evaluates to a floating word at once; it is
  never coded, which is why Appendix C has no code for it.  (strap2's dnum.py
  has it; tests/check_strap2_dd.py.)  In an address field both assemblers
  refuse it, which is the last row below.
  C22-6729 printed p.207: "Implied multiplication is not allowed in field
  arithmetic."
  C22-6578 printed p.42, comment (a) on Problem 4.8's "V-ICR,$3,N*N-1.0":
  "STRAP I does not perform multiplication of addresses, but STRAP II will
  do it properly."

WHAT IS CHOSEN: no page gives the arithmetic of * and / on a bit address.
strap2/value.py chose it (an integer scales both parts; two bit addresses
multiply as totals; a quotient by a bit address is an integer) and strap_asm
now copies it (strap_asm._arith_bi), so this check holds the two to each
other and to the bit-address form each card means under that choice.  The
integer and bit parts are converted by the address's function (C22-6729
printed p.144; tests/check_address_function.py).

Each row is a card with arithmetic and the card it must assemble the same as,
checked in each assembler and then the two against each other (N SYN, 8 is
an integer; SAM SYN, 400.0 a bit address):

  row                     card                  same as
  p.42 4.8 (19-bit)       V-ICR,$3,N*N-1.0      V-ICR,$3,31.0
  18-bit                  L(N), N*N-1.0         L(N), 63.0
  24-bit                  L(BU,8), N*N-1.0      L(BU,8), 0.0  (64 - 64 bits)
  int * bit               B, 2*SAM              B, 800.0
  bit * int               B, SAM*2              B, 800.0
  bit / bit -> integer    B, SAM/1.0            B, 200.0  (400 half words)
  parentheses, / int      B, (SAM+N)/2          B, 202.0
  minus a parenthesis     B, SAM-(N+1)          B, 395.32
  unary minus (U-)        B, -(N+1)+SAM         B, 395.32
  zero divisor ignored    B, SAM/0              B, SAM    (p.177's 78)
  radix operand           B, (8)17*2            B, 15.0
  ** refused (p.107)      B, N**2               both refuse

MEASURED INJECTIONS, 2026-11-16, each reverted from a saved copy and
checked with cmp (FAIL lines observed):
  strap_asm: _is_arith_field always False (the old flat tokenizer)
      all twelve rows' strap_asm and agree checks, each a refusal
      "cannot parse expression" (24)
  strap_asm: two bit addresses' product into the INTEGER part
      bit * bit (strap_asm, agree) (2)
  strap_asm: / by an integer on the totals, into the integer part
      parentheses, / int; zero divisor ignored (strap_asm, agree) (4)
  strap_asm: unary minus negating only the bit part
      unary minus (U-) (strap_asm, agree) (2).  The first try had only
      "SAM-(N+1)", a BINARY minus, and nothing failed; the U- row was
      added for it.
  strap_asm.split_field_trailing_paren: the operator test removed (the
      old reading, "(N+1)" taken as an index)
      minus a parenthesis (strap_asm, agree) (2): "expression 'SAM-' ends
      in an operator"
  control: PASS 38

NOT COVERED: a field that STARTS with an arithmetic parenthesis and ends
with it, "(N+1)" alone, is still read by strap_asm as an index on a null
address (MCP printed p.126's "KV,2,($1)" is the form that rule is for);
strap2 classifies it at its ')' (check_strap2_getfld_paren.py).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
import strap_asm  # noqa: E402
import strap2     # noqa: E402

HEAD = """N       SYN, 8
SAM     SYN, 400.0
START   NOP
"""
TAIL = """        BEW, $
        END, START
"""

CASES = [
    ("p.42 4.8 (19-bit)", "V-ICR,$3,N*N-1.0", "V-ICR,$3,31.0"),
    ("18-bit", "L(N), N*N-1.0", "L(N), 63.0"),
    ("24-bit", "L(BU,8), N*N-1.0", "L(BU,8), 0.0"),
    ("int * bit", "B, 2*SAM", "B, 800.0"),
    ("bit * int", "B, SAM*2", "B, 800.0"),
    ("bit * bit", "B, SAM*1.0", "B, 25600.0"),
    ("bit / bit -> integer", "B, SAM/1.0", "B, 200.0"),
    ("parentheses, / int", "B, (SAM+N)/2", "B, 202.0"),
    ("minus a parenthesis", "B, SAM-(N+1)", "B, 395.32"),
    ("unary minus (U-)", "B, -(N+1)+SAM", "B, 395.32"),
    ("zero divisor ignored", "B, SAM/0", "B, SAM"),
    ("radix operand", "B, (8)17*2", "B, 15.0"),
]

fails = 0
passes = 0


def check(name, ok, detail=""):
    global fails, passes
    if ok:
        passes += 1
        print(f"PASS {name}")
    else:
        fails += 1
        print(f"FAIL {name} {detail}")


def words(asm, card):
    src = HEAD + "        " + card + "\n" + TAIL
    try:
        if asm == "strap_asm":
            img = strap_asm.assemble(src)
        else:
            img = strap2.assemble(src, strap_asm.DEFAULT_ORIGIN_BITS)
    except Exception as x:      # noqa: BLE001  a refusal is a result here
        return f"refused: {x}"
    return dict(img.words)


def show(w):
    return w if isinstance(w, str) else {k: f"{v:016x}" for k, v in w.items()}


for name, card, means in CASES:
    got = {}
    for asm in ("strap_asm", "strap2"):
        a, b = words(asm, card), words(asm, means)
        got[asm] = a
        check(f"{name}: {asm}: '{card}' assembles as '{means}'",
              not isinstance(a, str) and a == b, f"{show(a)} vs {show(b)}")
    check(f"{name}: strap_asm and strap2 agree", got["strap_asm"] == got["strap2"])

for asm in ("strap_asm", "strap2"):
    w = words(asm, "B, N**2")
    check(f"** refused (p.107: a numeric DD's operation only): {asm}",
          isinstance(w, str) and w.startswith("refused"), show(w))

print(f"{passes} passed, {fails} failed")
sys.exit(1 if fails else 0)
