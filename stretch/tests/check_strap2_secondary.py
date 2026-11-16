#!/usr/bin/env python3
"""check_strap2_secondary.py -- STRAP II's secondary ops belong to their primary
op's class (C22-6729 pp.22-23, boxes 24-26; Fig. 24 p.192; read in the ink
2026-11-12).

p.22: the secondary op table's argument begins with "a special leading 8-bit
byte code number to identify the type of instruction which may have this
secondary op.  This code number is obtained from the current op index ...
Thus the cases, such as -- + (BU, 3) (SEOP) and CW (V + I) -- are illegal,
although in each instance the primary op does allow a secondary op.  For these
operations, MAIN would attempt to look up the corresponding argument 1SEOPbbb
or 4V+Ibbbb ... Since neither argument is in the table, the illegal op would be
detected without further cross checking."  Fig. 24's codes: 001 VFL, 020 SEOP,
100 CW, 000 none.  Message 2, ILLEGAL SECONDARY OP; 4, MORE THAN ONE (p.176).

Before this, strap2 dropped a secondary its op could not take, and assembled
+(BU,3)(SEOP) as plain +.

CHOSEN: a CTL function op has CTL's SEOP class -- MCP prints REW(SEOP) (printed
p.165 line 11, machine code CTL(SEOP)'s), SPFL(SEOP), GONG(SEOP).

MEASURED INJECTIONS, 2026-11-12, pass1.py restored by copy and cmp, control
all passing:
  the class check removed          +(BU,3)(SEOP), CW(V+I) (message 1, not 2),
                                   RD(V+I), B(SEOP)
  message 4 removed                only (V+I)(V-I) (message 1, not 4)
  a function op not CTL's class    only REW(SEOP)
  an I/O op given VFL's class      RD(V+I), RD(SEOP), REW(SEOP), and
                                   check_strap2_mbspec's RD(SE0P)
  CW given V+I too                 only CW(V+I) (message 1: the CW table
                                   itself refuses it)

THE SWEEP (2026-11-15): every name of the 7030 op table with V+I, SEOP and
CR, 1413 statements, against the abc of its op index (optab7030).  It found
117 immediate ops giving message 1 for a progressive secondary where the
7030 gives 2 (the op index says none: no field P), SU(SEOP) refused though
SU is LOC, and +NMG / *N+ given no secondaries in the 7030 table because
strap_asm.secondary_error did not respell IBM's spellings.
MEASURED INJECTIONS for the sweep, 2026-11-15 (pass1.py, strap_asm.py
restored by copy and cmp; control passing; run with check_secondary_ops.py
and check_strap2_7030_optab.py):
  immediates given VFL's secondaries again   only the sweep
  SU not respelled in pass1                  only the sweep
  secondary_error not respelling              the sweep, and the op-table
                                             test's block_fresh and decode
CORRECTED THE SAME DAY from p.23 (read in the ink): a secondary makes an
ambiguous op VFL, so +N(V+I) with no dds is (BU,64,8)'s word, not message 2;
the class is now the abc in pass1 too.  MEASURED INJECTIONS, 2026-11-15,
same method:
  strap_asm's p.23 rule removed              the +N(V+I) check and the sweep
  pass1's floating-mode guard removed        only L(N)(V+I)
  pass1's class by kind, not the abc         only the sweep
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
import strap2                   # noqa: E402

fails = 0


def check(label, got, want):
    global fails
    ok = got == want
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} {label}: got {got!r}" + ("" if ok else f", want {want!r}"))


def one(stmt):
    try:
        r = strap2.compile_cards(["         SLC,(8)100.0", f"         {stmt}", "         END"])
    except strap2.StrapError as x:
        return str(x).split(":")[0], None
    return [n for n, *_ in r.msg.items], r.image.words.get(0o100, 0)


check("p.23: +(BU,3)(SEOP) is illegal (1SEOP), message 2", one("+(BU,3)(SEOP),100.0")[0], [2])
check("p.23: CW(V+I) is illegal (4V+I), message 2", one("CW(V+I),100.0")[0], [2])
check("RD(V+I): a VFL secondary on an I/O op, message 2", one("RD(V+I),$X2,200")[0], [2])
check("B(SEOP): a branch takes no secondary, message 2", one("B(SEOP),100.0")[0], [2])
check("+(BU,3)(V+I)(V-I): message 4", one("+(BU,3)(V+I)(V-I),100.0")[0], [4])
got, plain = one("+(BU,3)(V+I),100.0"), one("+(BU,3),100.0")
check("+(BU,3)(V+I): legal, and the word differs from plain +",
      (got[0], got[1] != plain[1]), ([], True))
check("L(N)(V+I): a floating mode written makes the class floating's (CHOSEN), message 2",
      one("L(N)(V+I),100.0")[0], [2])
check("+N(V+I): p.23, the secondary makes an ambiguous op VFL; the word is (BU,64,8)'s",
      (one("+N(V+I),100.0")[0], one("+N(V+I),100.0")[1] == one("+N(V+I)(BU,64,8),100.0")[1]),
      ([], True))
check("RD(SEOP): legal", one("RD(SEOP),$X2,200")[0], [])
check("CW(CR): legal", one("CW(CR),100.0")[0], [])
check("REW(SEOP): a CTL function op takes CTL's SEOP (MCP p.165 line 11)",
      one("REW(SEOP),0.0($14)")[0], [])

# The sweep: every name of the 7030 table (tests/printed_ops.optab_names)
# with one secondary of each family, against the abc its op index carries
# (strap2/optab7030.secondary_code, Fig. 24 p.192): message 2 exactly when
# the family is not the op's.  EXT is left out: its parentheses are its
# parameters (C28-6129 printed p.19), not a secondary.  A legal pair must
# give no message at all.  An ambiguous op with no dds takes the secondary
# as VFL: p.23, read in the ink, "the presence of a secondary op
# establishes the op as a variable field type op" (+N(V+I), M+N(V+I) and
# M+NMG(V+I) were message 2 before).
sys.path.insert(0, HERE)
import printed_ops                                  # noqa: E402
from strap2 import optab7030 as O                   # noqa: E402

REP = {O.ABC["VFL"]: "V+I", O.ABC["SEOP"]: "SEOP", O.ABC["CW"]: "CR"}
bad, n = [], 0
for name in printed_ops.optab_names():
    # "" is the null op (p.21 Box 8: a comma first looks up a blank Bop):
    # an entry of the table, but no statement writes a secondary on it.
    if name in ("EXT", ""):
        continue
    code = O.secondary_code(name)
    for fam, sec in REP.items():
        msgs = one(f"{name}({sec}),100.0")[0]
        want2 = fam != code
        n += 1
        if msgs != ([2] if want2 else []):
            bad.append((name, sec, msgs, code))
check(f"sweep: message 2 exactly when the op index's abc refuses the family ({n} statements)",
      bad[:12], [])

print("ALL CHECKS PASSED" if not fails else f"{fails} FAILED")
sys.exit(1 if fails else 0)
