#!/usr/bin/env python3
"""check_strap2_prntall.py -- STRAP II's PRNTALL: every symbol and its address,
at the end of the listing.

Sources, read in the ink 2026-11-12:
  N28-1081 page 2 (C28-6129 PDF 60): "PRNTALL / If this pseudo-operation is
    specified anywhere in the program, a list of all symbols will be printed
    at the end of the program, with the address at which they were defined."
  C22-6729 charts EG, EH (pp.170-171) and p.172: after the undefined, unused,
    multiply and circularly defined lists, box 30A "WAS PRNTALL SPECIFIED",
    30B turns on the PRNTALL switch, 30C re-enters NUNDSY; EG box 6B
    "PRINTING ALL SYMBOLS" -> box 7 prints a header "FOR ALL SYMBOLS", boxes
    8-9 RSERCH and NCVAD print each symbol's address; EH box 18A skips the
    stacked lists on that pass.  Only the first 50 characters print (p.172).

CHOSEN: the header's words (box 7 prints none); every vle, so a name defined
twice prints twice, each with its own definition's address.

Before this, strap2 accepted PRNTALL and printed nothing.

MEASURED INJECTIONS, 2026-11-12, pass2.py / listing.py restored by copy and
cmp, PYTHONDONTWRITEBYTECODE=1, control all passing:
  the PRNTALL flag never set       the three PRNTALL checks (not the first)
  the list never printed           the same three
  only the dictionary's vle        only the defined-twice check
  printed before the unused list   the three PRNTALL checks
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
from strap2 import compile_cards                 # noqa: E402
from strap2.listing import listing_of            # noqa: E402

fails = 0


def check(label, got, want):
    global fails
    ok = got == want
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} {label}: got {got!r}" + ("" if ok else f", want {want!r}"))


def tail(*extra, at_start=False):
    body = [" A       LX,$1,B", " B       LX,$2,5", " C       SYN,(8)200.0", "         B,A"]
    cards = (["         PRNTALL"] if at_start else []) + ["         SLC,(8)100.0"] + body
    cards += list(extra) + ["         END"]
    p2 = compile_cards(cards)
    text = listing_of(p2, p2.p1.print_names).text("0", 1)
    lines = text.splitlines()
    k = next(i for i, ln in enumerate(lines) if ln.strip().endswith("END"))
    return lines[k + 1:-1]


check("no PRNTALL: only the unused list", tail(),
      ["SYMBOLS DEFINED BUT NOT USED", "C  000200.00"])
check("PRNTALL: after the unused list, every symbol with its address",
      tail("         PRNTALL"),
      ["SYMBOLS DEFINED BUT NOT USED", "C  000200.00",
       "ALL SYMBOLS", "A  000100.00", "B  000100.40", "C  000200.00"])
check("PRNTALL anywhere: first card of the program", tail(at_start=True)[2:],
      ["ALL SYMBOLS", "A  000100.00", "B  000100.40", "C  000200.00"])
got = tail(" D       SYN,(8)300.0", " D       SYN,(8)400.0", "         PRNTALL")
check("a name defined twice prints at both definitions",
      got[got.index("ALL SYMBOLS"):] if "ALL SYMBOLS" in got else got, ["ALL SYMBOLS", "A  000100.00", "B  000100.40",
                                       "C  000200.00", "D  000300.00", "D  000400.00"])

print("ALL CHECKS PASSED" if not fails else f"{fails} FAILED")
sys.exit(1 if fails else 0)
