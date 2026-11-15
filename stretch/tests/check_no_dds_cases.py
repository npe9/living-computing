#!/usr/bin/env python3
"""No data description anywhere: C28-6129 printed p.7's three cases, over
the whole printed operation set.

C28-6129 printed p.7 (C22-6729 p.140 Box 5 says the same, read in the ink
2026-11-15): where "there is no way for STRAP to obtain a data description
from either the symbolic address or an explicit data description field":
  1. "The operation symbol can stand for either VFL or floating point
     operations (+, -, *, /).  The operation is compiled as a VFL operation
     with the data description (BU, 64, 8)."
  2. "... a VFL operation only (M + 1, for example) ... (BU, 64, 8).  If the
     operation is clearly VFL immediate, (BU, 24, 8) is assigned."
  3. "... only a floating point operation (-A, or *NA) ... normalized
     floating point, except for ... E+I ... and its modified forms, where
     unnormalized is assumed."
Which case a name is in is read off the printed set (check_strap2_mnemonics:
printed as a VFL spelling, a floating-point one, or both); names in its
REFUSED buckets are left out.

Found 2026-11-15, and fixed:
  - thirteen signed forms printed both ways (LN, STN, M-, -MG, *N, ...)
    compiled bare as floating point, not case 1's VFL;
  - "+NMG", printed VFL only, compiled bare as floating point;
  - twenty-four VFL N and NI forms (CVN, KFN, LNI, *NI, ...) had no bare
    reading at all;
  - a bare VFL immediate took (BU, 64, 8), so "LI,5" was refused;
  - "+I(N),100" compiled to exactly the word of "+(N),100" (the I is VFL
    immediate addressing, which no floating-point word holds).
No deck wrote any of these bare.

Checks:
  cases      lookup(name) with no mode: case 1 VFL and ambiguous, case 2
             VFL or connective and not ambiguous, case 3 floating point
  words      strap_asm: each case 1 and 2 name assembles bare to the word
             of name(BU,64,8) (name(BU,24,8) when immediate); each case 3
             name to name(N), or name(U) in the E and E+I families
  fp_imm     "+I(N)", "LI(N)", "-MGI(N)" are refused; E+I is not

MEASURED 2026-11-15: 28 names in case 1, 188 in case 2, 101 in case 3.

MEASURED INJECTIONS (each on a copy, reverted by cmp; control passes
before and after):
    the case-1 block off (NO_DDS_VFL_FORMS)     FAIL cases, words
    the case-2 N/NI fallback off                FAIL cases, words
    the bare immediate back to (BU, 64, 8)      FAIL words
    the FP-immediate refusal off                FAIL fp_imm
    +NMG counted ambiguous in optable           FAIL cases
    strap_asm and optable before the fix        FAIL cases, words, fp_imm
"""
import io
import os
import sys
import contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
sys.path.insert(0, HERE)
import strap_asm as A                       # noqa: E402
with contextlib.redirect_stdout(io.StringIO()):
    try:
        import check_strap2_mnemonics as CM  # noqa: E402  (the printed set)
    except SystemExit:
        pass

failures = []


def check(what, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + what + ("" if ok else ": " + detail))
    if not ok:
        failures.append(what)


def word(stmt):
    try:
        w = A.assemble(" " + stmt + "\n").words
        return w.get(32)
    except Exception as e:                  # noqa: BLE001
        return f"{type(e).__name__}: {str(e)[:50]}"


REFUSED = set().union(*CM.REFUSED.values())
cases = {"1": [], "2": [], "3": []}
for name, srcs in sorted(CM.printed.items()):
    k = CM.kinds_of(srcs)
    if not (k & {"V", "F"}) or name in REFUSED:
        continue
    cases["1" if {"V", "F"} <= k else "2" if "V" in k else "3"].append(name)
print("names per case:", {c: len(v) for c, v in cases.items()})

bad = []
for c, names in cases.items():
    for n in names:
        e = CM.look(n)
        if e is None:
            bad.append((n, c, None))
        elif c == "1" and not (e.kind == "vfl" and e.ambiguous):
            bad.append((n, c, e.kind))
        elif c == "2" and not (e.kind in ("vfl", "conn") and not getattr(e, "ambiguous", False)):
            bad.append((n, c, e.kind))
        elif c == "3" and e.kind != "fp":
            bad.append((n, c, e.kind))
check("cases: every printed name's bare entry is its p.7 case", not bad, str(bad[:20]))

bad = []
for c, names in cases.items():
    for n in names:
        e = CM.look(n)
        if c in ("1", "2"):
            dds = "(BU,24,8)" if getattr(e, "immediate", False) else "(BU,64,8)"
        else:
            fam = A.strip_fp_sign(A.ibm_spelling(n, [])[0])
            fam = fam[0] if fam else A.ibm_spelling(n, [])[0]
            dds = "(U)" if fam in ("E+", "E+I") else "(N)"
        got, want = word(n + ",0"), word(n + dds + ",0")
        if got != want or not isinstance(got, int):
            bad.append((n, got, n + dds, want))
check("words: bare equals the case's default dds, in strap_asm", not bad, str(bad[:12]))

bad = [(s, word(s)) for s in ("+I(N),100", "LI(N),100", "-MGI(N),100")
       if not (isinstance(word(s), str) and "immediate addressing on a floating" in word(s))]
if not isinstance(word("E+I,1"), int):
    bad.append(("E+I,1", word("E+I,1")))
check("fp_imm: the I suffix on a floating-point op is refused", not bad, str(bad))

if failures:
    print(f"*** {len(failures)} CHECK(S) FAILED ***")
    sys.exit(1)
print("ALL CHECKS PASSED")
