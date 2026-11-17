#!/usr/bin/env python3
"""check_address_function.py -- an integer in an address counts the units of
the address's FUNCTION, not of its field (C22-6729 printed p.144; G3.2).

C22-6729 printed p.144 (INSERT), read in the page image 2026-11-16:

  "Algebraic addition of bit and integer addresses is performed according to
   the type of field into which the sum is to be inserted.  For example, if
   the address SAM + 10 is to be inserted into an 18-bit address, the routine
   adds 10 full words to the address of SAM; if a 19-bit address, it adds 10
   half words; if a 24-bit address, it adds 10 bits.  Note that the addition
   is determined by the function of the address, not the size of the field.
   To fill the addresses in the instruction TI, 7, SAM + 10, PAT + 10, the
   routine adds 10 full words to both addresses.  Although SAM + 10 is a
   24-bit field and PAT + 10 is a 19-bit field, both function as 18-bit
   addresses."

C28-6129 printed p.4 (PDF p.8) writes the transmit format "OP, J, A18(I),
A'18(I')" for the same reason.  No listing row in the corpus writes an
integer in a transmit address (every T/TI/SWAP row in the decks and in the
MCP, C22-6578, C22-6531 and C28-6129 OCR writes "+1.0" or "+14."), so p.144
is the only witness for that row, and both assemblers follow it.

Each case is a pair of cards that must assemble to the same words: the
integer form and the bit-address form p.144 says it means.  Each assembler
is checked on its own (strap_asm's ADDRESS_FUNCTION table; strap2's INSERT
routines in pass2.py), and then the two against each other.

  case            integer form              means
  p144 TI         TI, 7, SAM+10, PAT+10     TI, 7, SAM+10.0, PAT+10.0
  p144 TI minus   TI, 7, SAM-3, PAT-3       TI, 7, SAM-3.0, PAT-3.0
  p144 SWAP       SWAP, 2, SAM+1, PAT+2     SWAP, 2, SAM+1.0, PAT+2.0
  p144 18-bit     L(N), SAM+10 (FP, S18A)   L(N), SAM+10.0
  p144 19-bit     B, SAM+10  (S19IA)        B, SAM+5.0
  p144 24-bit     L(BU,8), SAM+10 (S24A)    L(BU,8), SAM+.10
  RM p.24 SX      SX, $X1, 8   (S18X)       SX, $X1, 8.0
  SYN integer SX  SX, $X1, N   (N SYN, 8)   SX, $X1, 8.0
  SYN integer TI  TI, 7, SAM+N, PAT+N       TI, 7, SAM+8.0, PAT+8.0

Before G3.2 the two assemblers agreed with each other, and not with the
page, on every transmit row, and disagreed with each other on "SYN integer
SX" (the injections below reproduce each old form): strap_asm compiled transmit's A1
through eval_expr (an integer counted bits) and A2 with a half-word shift;
strap2 used S24A's and S19IA's arithmetic for STTI and STT19A; and
strap_asm left an integer SYN symbol unshifted in LX/SX, where strap2 (and
a literal integer) counted words.  No deck's image changed (every deck,
both assemblers, hashed before and after).

The controls are the existing listing oracles: verify_ax5b_16087_listing.py
holds IBM's printed "TI,1,BIT0($X1),$IND" and verify_ibox4_listing.py's
I-Box 4 p.58 rows hold "SX,$X0,8"; both stay green under this rule.

MEASURED INJECTIONS, 2026-11-16, each reverted from a saved copy and checked
with cmp (FAIL lines observed):
  strap_asm ADDRESS_FUNCTION["STTI"] (0, 6) -> (0, 0), the old eval_expr
      p144 TI, p144 TI minus, p144 SWAP, SYN integer TI -- strap_asm and
      both-agree rows (8)
  strap_asm ADDRESS_FUNCTION["STT19A"] (5, 6) -> (5, 5), the old shift 5
      the same four cases, strap_asm and both-agree rows (8)
  strap2 pass2.i_STTI back to S24A's v.B + v.I
      p144 TI, p144 TI minus, p144 SWAP, SYN integer TI -- strap2 and
      both-agree rows (8)
  strap_asm eval_addr_field: an integer SYN symbol not shifted (raw)
      SYN integer SX, SYN integer TI -- strap_asm and both-agree rows (4)
  control, none of the above: PASS 27
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
import strap_asm  # noqa: E402
import strap2     # noqa: E402

HEAD = """N       SYN, 8
SAM     SYN, 400.0
PAT     SYN, 500.0
START   NOP
"""
TAIL = """        BEW, $
        END, START
"""

CASES = [
    ("p144 TI", "TI, 7, SAM+10, PAT+10", "TI, 7, SAM+10.0, PAT+10.0"),
    ("p144 TI minus", "TI, 7, SAM-3, PAT-3", "TI, 7, SAM-3.0, PAT-3.0"),
    ("p144 SWAP", "SWAP, 2, SAM+1, PAT+2", "SWAP, 2, SAM+1.0, PAT+2.0"),
    ("p144 18-bit", "L(N), SAM+10", "L(N), SAM+10.0"),
    ("p144 19-bit", "B, SAM+10", "B, SAM+5.0"),
    ("p144 24-bit", "L(BU,8), SAM+10", "L(BU,8), SAM+.10"),
    ("RM p.24 SX", "SX, $X1, 8", "SX, $X1, 8.0"),
    ("SYN integer SX", "SX, $X1, N", "SX, $X1, 8.0"),
    ("SYN integer TI", "TI, 7, SAM+N, PAT+N", "TI, 7, SAM+8.0, PAT+8.0"),
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


for name, integer, means in CASES:
    got = {}
    for asm in ("strap_asm", "strap2"):
        a, b = words(asm, integer), words(asm, means)
        got[asm] = a
        check(f"{name}: {asm}: '{integer}' assembles as '{means}'", a == b,
              f"{a if isinstance(a, str) else ''}{b if isinstance(b, str) else ''}")
    check(f"{name}: strap_asm and strap2 agree", got["strap_asm"] == got["strap2"])

print(f"{passes} passed, {fails} failed")
sys.exit(1 if fails else 0)
