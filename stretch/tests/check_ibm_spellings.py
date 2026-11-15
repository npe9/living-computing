#!/usr/bin/env python3
"""check_ibm_spellings.py -- IBM's printed spellings assemble to the bits of
the spellings this assembler already had.

C28-6129 (Appendices A and C), N28-1081 and the guide's Appendix B print
operations this assembler wrote another way (tests/check_strap2_mnemonics.py
finds them: its ORDER, PSEUDO_SPELLING and SIGN_GAP buckets).  strap_asm's
IBM_SPELLING maps each to its spelling here, and an I-O operation written
"xxxSEOP" to xxx(SEOP).  Each PAIR below is assembled both ways, by
strap_asm.assemble, and must give the same words; each is also looked up in
strap/strap2/optable.py both ways and must give the same skeleton.

SIGN_GAP forms have no listing yet; each is paired with the form the
family's rule makes it:
  -A        "+" with both modifiers         = +NA   (C28-6129 App. C p.47)
  VFL M-MG  M+MG with the invert bit        = M+MGN (App. A p.44, C p.49)
  VFL -MGI  +MG, invert, immediate          = +MGNI (App. A footnote 3)
  VFL M-MGI M+MG, invert, immediate         = M+MGNI
The right-hand forms are ones the host already took (+NA is N28-1081's;
+MGNI and M+MGNI are its own suffix grammar).

AND A BUG IT FOUND.  FP "-(N),X" assembled to exactly "+(N),X": the
classify step turns "-" into "+" with invert=1, and the FP encode path (in
strap_asm.py and in strap2/optable.py) took the invert bit only from
strip_fp_sign's suffixes.  C28-6129 App. C p.47 prints FP "- a-m -> a".
Fixed in both; the "-(N)" and "-(U)" pairs below are its test.  No listing
in the corpus prints a bare FP subtract.

MEASURED INJECTIONS, 2026-11-15 (on a copy; control passes before and
after; each reverted from a saved copy and checked with cmp):
  IBM_SPELLING loses "*A+"                    -> 2 checks fail
  the xxxSEOP rule removed                    -> 6
  the FP minus fix reverted in strap_asm      -> 2
  the FP minus fix reverted in optable        -> 2
  the "-A" rule (strip_fp_sign) removed       -> 2
  "M-MG" not in VFL_INT_WRITTEN_MINUS         -> 4
  optable.lookup without ibm_spelling         -> 19
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
import strap_asm as A               # noqa: E402
from strap2 import optable as T     # noqa: E402

PRE = "X       SYN, (8)100.0\n        SLC, (8)200.0\n"
PAIRS = [
    # (IBM's, this assembler's, lookup mode)
    ("*A+(N),X", "*+A(N),X", "N"),
    ("*N+(N),X", "*+N(N),X", "N"),
    ("*N+(BU,8),X", "*+N(BU,8),X", "BU"),
    ("*NA+(N),X", "*+NA(N),X", "N"),
    ("*NI+(BU,8),5", "*+NI(BU,8),5", "BU"),
    ("+NMG(N),X", "+MGN(N),X", "N"),
    ("D+NMG(N),X", "D+MGN(N),X", "N"),
    ("M+NMG(N),X", "M+MGN(N),X", "N"),
    ("CBZR,$X1,X", "CBRZ,$X1,X", None),
    ("CBZR+,$X1,X", "CBRZ+,$X1,X", None),
    ("CBZR-,$X1,X", "CBRZ-,$X1,X", None),
    ("CBZRH,$X1,X", "CBRZH,$X1,X", None),
    ("SU,(8)20,(8)300", "LOC,(8)20,(8)300", None),
    ("SUSEOP,(8)20,(8)300", "LOC(SEOP),(8)20,(8)300", None),
    ("SPFLSEOP,(8)20", "SPFL(SEOP),(8)20", None),
    ("GONGSEOP,(8)20", "GONG(SEOP),(8)20", None),
    ("-A(N),X", "+NA(N),X", "N"),
    # Not a spelling: the bug its controls found.  FP "-" is "+" with N
    # (C28-6129 App. C p.47 "- a-m -> a"); it assembled to "+" until
    # 2026-11-15.
    ("-(N),X", "+N(N),X", "N"),
    ("-(U),X", "+N(U),X", "U"),
    ("M-MG(BU,8),X", "M+MGN(BU,8),X", "BU"),
    ("-MGI(BU,8),5", "+MGNI(BU,8),5", "BU"),
    ("M-MGI(BU,8),5", "M+MGNI(BU,8),5", "BU"),
]
PSEUDO = [("NOPRINT", "NOPRNT"), ("PUNSYN", "PUNSYM"), ("PRNNOR", "PRNOR")]


def words(card):
    try:
        p = A.assemble(PRE + "        " + card + "\n")
        return sorted(p.words.items())
    except Exception as e:
        return "refused: " + str(e)[:60]


def skel(op, mode, sec=()):
    try:
        e = T.lookup(op, mode, sec)
        return None if e is None else (e.kind, e.skeleton)
    except Exception as e:
        return "error"


def split(card):
    op = card.split(",")[0]
    sec = ()
    if "(SEOP)" in op:
        op, sec = op.replace("(SEOP)", ""), ("SEOP",)
    return op.split("(")[0], sec


fails = []
for ibm, here, mode in PAIRS:
    a, b = words(ibm), words(here)
    ok = isinstance(a, list) and a == b
    (o1, s1), (o2, s2) = split(ibm), split(here)
    k1, k2 = skel(o1, mode, s1), skel(o2, mode, s2)
    ok2 = k1 is not None and k1 != "error" and k1 == k2
    print(("PASS " if ok else "FAIL ") + "assembles alike: %-22s %-22s" % (ibm, here)
          + ("" if ok else " %s / %s" % (a, b)))
    print(("PASS " if ok2 else "FAIL ") + "looks up alike:  %-22s %-22s" % (o1, o2))
    if not ok:
        fails.append(ibm)
    if not ok2:
        fails.append("lookup " + ibm)
for ibm, here in PSEUDO:
    ok = words(ibm) == words(here) and skel(ibm, None) == skel(here, None) is not None
    print(("PASS " if ok else "FAIL ") + "pseudo-op %s is %s" % (ibm, here))
    if not ok:
        fails.append(ibm)
if fails:
    print("\n%d FAILED" % len(fails))
    sys.exit(1)
print("\nALL IBM SPELLING CHECKS PASSED")
