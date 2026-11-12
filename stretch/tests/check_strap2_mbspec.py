#!/usr/bin/env python3
"""check_strap2_mbspec.py -- STRAP II's MBSPEC, the option-character help for an
illegal op (C22-6729 pp.92-93, chart BL; MIBA pp.94-95, chart CA; read in the
ink 2026-11-12).

p.93: "a 0 was punched for an O, a 1 for an I, a 2 for a Z, a 5 for an S, or
vice versa"; box 6 prints the order of the test words, "SXXXXXXX, XSXXXXXX,
SSXXXXXX, XXSXXXXX, etc."; box 10, a successful search with Llbts.8 on gives
"an error message informing the programmer a change has been made" -- message
129, OP OR SS CHANGED INTO LEGAL MNEMONICS (p.178).  p.95: MIBA's three
returns, the second "to relook-up ... the formerly illegally specified
operation mnemonic which MIBA has now adjusted with the MBSPEC subroutine".
N28-1081 p.13: messages 1-18 are the serious ones, so 129 does not stop the
deck (CHOSEN on that reading).

No pair of legal mnemonics in this table is one MBSPEC word apart in two ways
(searched 2026-11-12: 374 primary and BI-type mnemonics, none), so the order
is checked on the generator itself, against p.93's list.

MEASURED INJECTIONS, 2026-11-12, optable.py / pass1.py restored by copy and cmp,
control all passing:
  MBSPEC never called              5T, 51C, LV1, B0P, the assemble() check
  the first character not tried    the order check, 5T, 51C, the assemble()
                                   check (it uses 5T)
  the last character lowest        the order check
  one substitution at a time only  51C, the order check
  message 129 serious (fatal)      the assemble() check
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
import strap2                   # noqa: E402
from strap2.optable import mbspec   # noqa: E402

fails = 0


def check(label, got, want):
    global fails
    ok = got == want
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} {label}: got {got!r}" + ("" if ok else f", want {want!r}"))


def one(op, addr="5"):
    r = strap2.compile_cards(["         SLC,(8)100.0", f"         {op},{addr}", "         END"])
    return [n for n, *_ in r.msg.items], r.image.words.get(0o100, 0)


check("p.93 box 6's order: SXX, XSX, SSX, XXS ... (the first character lowest)",
      list(mbspec("SOS"))[:4], ["5OS", "S0S", "50S", "SO5"])
check("a word with no possible error character gets no help", list(mbspec("QQ")), [])
for bad, good, why in (("5T", "ST", "5 for S, the first character"),
                       ("51C", "SIC", "two substitutions, SSX"),
                       ("LV1", "LVI", "1 for I"),
                       ("B0P", "BOP", "0 for O in a BI-type op: MIBA's relook-up")):
    want = one(good)[1]
    check(f"{bad} is {good} ({why}), with message 129", one(bad), ([129], want))
check("QQ: no help, message 1", one("QQ")[0], [1])
check("ST: legal, no message", one("ST")[0], [])
try:
    strap2.assemble("        SLC,(8)100.0\n        5T,5\n        END,(8)100.0\n")
    went = "assembled"
except strap2.StrapError:
    went = "refused"
check("message 129 is not serious (N28-1081 p.13): the deck assembles", went, "assembled")

print("ALL CHECKS PASSED" if not fails else f"{fails} FAILED")
sys.exit(1 if fails else 0)
