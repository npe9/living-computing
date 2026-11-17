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
  ONE PAGE READS THE OTHER WAY, recorded and not settled: the glossary,
  C22-6729 printed p.204, "Priority of Operations -- When arithmetic
  operations are specified in an instruction field, there is a definite
  order by which they are combined ... 1st order operation + and -.  2nd
  order operation * and /.  3rd order operation **."  Its "orders" are
  p.107's words for MQDNUM, so this check reads it as the numeric DD's
  (p.207 calls a numeric DD's operands its "'address' field"); Appendix C
  could not code "**" in any other field.
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

SYN, CW, TRANSMIT'S J AND "(N+1)" ALONE (G3 follow-up, 2026-11-17).  strap_asm
refused "Q SYN, N*2", "CW, SAM*2, N*2" and "T, N/4, ..." ("cannot parse
expression"), and read "(N+1)" alone as an index on a null address; strap2
took all four.  The rows after "radix operand" hold them, with strap2 the
oracle on every row (the "agree" checks).  The pages:
  A SYN KEEPS ITS TWO PARTS (DERIVED).  C22-6729 printed p.13: the vle holds
  "its value or the coded expression of the value of the symbol"; Chart RD,
  printed p.54, looks a symbol up and puts its info, or the VALUE of its
  sub-expression, in the list; printed p.57's workspace data are "I-value and
  B-value"; printed p.59 Box 6: "If the result is not to be made an integer,
  i.e., Vvint is off, then exit; otherwise combine integer and bit values, and
  set bit value to zero ... Put integer and bit values into VALUE's output
  words, Sini and Sinb."  INSERT adds them by the address's function (printed
  p.144).  No page tabulates the vle's function (Fig. 22, printed p.191), so
  where the two parts are stored is not printed.  So a SYN is an integer when its bit part is zero
  ("N*2", and "SAM/1.0", a quotient of two bit addresses), a bit address when
  its integer part is zero, and otherwise MIXED, its parts kept apart
  (strap_asm SymTab.sym_ipart).  The mixed case was wrong WITHOUT arithmetic
  too: "QM SYN, SAM+N" then "B, QM" gave 800 half words, strap2 808.
  CW's fields are SCW, S18CF and S18RF and J's is STJFLD (printed p.144),
  which strap2 fills with (bit part >> 6) + integer part; "CW, SAM+1" gave
  word 400 where strap2 gives 401.  Every register field (J, LV's, LX's)
  takes the same through eval_reg when it has arithmetic or a mixed SYN:
  "LV, N/4, SAM" was refused, and "LV, QS, SAM" (QS SYN, 1.0+2) gave 1
  where strap2 gives 3.  An index field (eval_index) takes strap2's own S/X
  rule, value.py's, CHOSEN there: the bit part's word if there is one, else
  the integer part, so SAM(QS) is index 1.
  "(N+1)" ALONE: printed p.85, Boxes 43, 44, 49, "If there was no operator to
  make the parentheses arithmetic, the coded expression is set to indicate a
  sub-expression"; Boxes 76-78, "If the parenthesis could not be arithmetic,
  Gfsfxb (processing-subscript indicator) is turned on".  CHOSEN, as strap2's
  getfld.py chooses it (Box 76 draws no test): an operator inside, including
  a unary minus and a point, makes it arithmetic; without one it is an index
  on a zero datum, MCP printed p.126's "KV,2,($1)" (000000.04 91), the
  control rows.
No deck's image changed under either assembler (all 825 decks hashed,
words and symbol table, before and after).

MEASURED INJECTIONS, 2026-11-17, each reverted from a saved copy and checked
with cmp (FAIL lines observed; each "row" is the row's strap_asm check and its
agree check):
  sym_parts ignores sym_ipart (a mixed SYN is a bit address again)
      rows mixed SYN SAM+N (19-bit), (LX, 18), through a bare SYN,
      SAM*2+N/4, before a point, CW mixed SYN, register field mixed SYN
      (14).  The 24-bit control row did not fail, as it should not.
  SYN by parts never makes an integer
      rows SYN N*2 (19-bit), (LX, 18), SYN SAM/1.0 (6)
  CW back to the text rule (total, shifted when written as an address)
      rows CW mixed field SAM+1, CW mixed SYN (4)
  eval_reg without the parts path
      rows transmit J N/4, (N+4)/4, 1.0*2, register field N/4 (refused),
      register field mixed SYN (10)
  eval_reg's parts path as the total, bit part unshifted
      rows transmit J 1.0*2, register field mixed SYN (4).  The J 1.0*2
      row was added for this: N/4 and (N+4)/4 have no bit part.
  eval_index summing the parts / eval_index as eval_reg
      row index mixed SYN (2) each; "index N/4" fails neither, since
      eval_reg's parts path gives it 2 as well
  "(N+1)" alone read as an index again
      rows (N+1), (-N), (N.), ($1+1) alone is arithmetic (8)
  every lone parenthesis arithmetic (no operator test)
      rows ($1) and (N) alone is an index (4): the controls
  a mixed symbol's integer part before a point counting bits
      rows mixed SYN before a point, (N.) alone is arithmetic (4)
  referenced_symbols without the arithmetic path
      every row (74): HEAD's "QI SYN, N*2" is refused
  control: PASS 113

NOT ALIGNED, probed: an index written with a bit and an integer part and no
arithmetic, "B, SAM($1+1)", is index 2 in strap_asm and 1 in strap2 (its
S/X rule drops the integer part).  This difference was there before G3.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
import strap_asm  # noqa: E402
import strap2     # noqa: E402

HEAD = """N       SYN, 8
SAM     SYN, 400.0
QI      SYN, N*2
QM      SYN, SAM+N
QA      SYN, SAM*2+N/4
QR      SYN, QM
QD      SYN, SAM/1.0
QS      SYN, 1.0+2
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
    # SYN, CW and transmit's J (G3, 2026-11-17).
    ("SYN N*2 is an integer (19-bit)", "B, QI", "B, 8.0"),
    ("SYN N*2 is an integer (LX, 18)", "LX, $1, QI", "LX, $1, 16.0"),
    ("SYN SAM/1.0 is an integer", "B, QD", "B, 200.0"),
    ("mixed SYN SAM+N (19-bit)", "B, QM", "B, 404.0"),
    ("mixed SYN SAM+N (LX, 18)", "LX, $1, QM", "LX, $1, 408.0"),
    ("mixed SYN SAM+N (24-bit, control)", "L(BU,8), QM", "L(BU,8), 400.8"),
    ("mixed SYN through a bare SYN", "B, QR", "B, 404.0"),
    ("mixed SYN SAM*2+N/4", "B, QA", "B, 801.0"),
    ("mixed SYN before a point", "B, QM.", "B, 408.0"),
    ("CW, SAM*2, N*2", "CW, SAM*2, N*2", "CW, 800.0, 16"),
    ("CW mixed field SAM+1", "CW, SAM+1, N+1, SAM", "CW, 401.0, 9, 400.0"),
    ("CW mixed SYN", "CW, QM, QM", "CW, 408.0, 408"),
    ("transmit J N/4", "T, N/4, SAM, SAM", "T, 2, SAM, SAM"),
    ("transmit J (N+4)/4", "T, (N+4)/4, SAM, SAM", "T, 3, SAM, SAM"),
    ("transmit J 1.0*2 (a bit part)", "T, 1.0*2, SAM, SAM", "T, 2, SAM, SAM"),
    ("register field N/4", "LV, N/4, SAM", "LV, 2, SAM"),
    ("register field, mixed SYN 1.0+2", "LV, QS, SAM", "LV, 3, SAM"),
    ("index N/4", "B, SAM(N/4)", "B, SAM(2)"),
    ("index, mixed SYN 1.0+2 (strap2: B's word)", "B, SAM(QS)", "B, SAM(1)"),
    ("(N+1) alone is arithmetic", "B, (N+1)", "B, 4.32"),
    ("(-N) alone is arithmetic", "B, (-N)", "B, -N"),
    ("(N.) alone is arithmetic", "B, (N.)", "B, 8.0"),
    ("($1+1) alone is arithmetic", "B, ($1+1)", "B, 17.32"),
    ("($1) alone is an index (p.126, control)", "KV,2,($1)", "KV,2,0($1)"),
    ("(N) alone is an index (control)", "B, (N)", "B, 0(N)"),
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
