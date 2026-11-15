#!/usr/bin/env python3
"""Secondary operations: each only on its own family of operation.

PART 1, field P.
Reference Manual printed p.21, read in the ink 2026-11-15: "In variable-
field-length instructions, the field P, bits 32-34, is available to specify
the choice between address modification and progressive indexing.  The
codes 0 and 4 in the field P indicate standard address modification.  The
codes 1-3 and 5-7 indicate progressive indexing", code 4 being the
immediate mode.  Found by the op-table reconstruction (step 4a-ii): the
host accepted three combinations no instruction word can hold, and
assembled each without an error to a word that dropped half of what was
written:

  refused_fp     "+(V+I)(N),100" gave exactly the word of "+(N),100"
                 (a half-word FP instruction has no field P)
  refused_imm    "LI(V+IC)(BU,8),5" packed 5 as an immediate under P = 2
  refused_conn   a connective with an explicit (N) or (U): strap_asm
                 refused it only at emit time, so the op table took it
  optable        lookup() gives None for each, as strap_asm refuses it
  controls       the printed forms keep their words: Figure 7's
                 "L(V+I)(BU,7,8)", C22-6578's "K(BU,7)(V+I)", immediate
                 "LI(BU,8)", connective "CI0001(BU,6)" (MCP printed
                 p.125 line 28), and FP "+(N)"

PART 2, the family rule (strap_asm.secondary_error, used by both
strap_asm and the STRAP II host's op table).  C22-6729 printed p.22, read
in the ink: "Thus the cases, such as -- + (BU, 3) (SEOP) and CW (V + I) --
are illegal, although in each instance the primary op does allow a
secondary op"; both are in refused_family.  V+I ... V-ICR only on VFL
and connective operations; SEOP only on an I-O op with an SEOP form; CR
CCR CD CDSC SCR SCCR SCD SCDSC only on CW (N28-1081; C22-6729 Fig. 24
p.192, "100 for a secondary op in the CW instruction"); at most one per
statement (message 4, "MORE THAN ONE SECONDARY OP", C22-6729 p.178;
"RD(SEOP)(V+I)" and "CW(CCR)(CD)" are what only that rule catches).
Before, "B(CCR)", "XW(CD)", "LX(SEOP)", "RD(CCR)", "RD(V+I)" assembled
with the secondary dropped, and lookup() took any secondary on any op.

  refused_family  each of those, plus "RDSEOP(SEOP)", "CCW(SEOP)" and two
                  progressive secondaries on one L, is an AssemblerError
  optable_family  lookup() is None for each
  legal_family    every (op, secondary) family the corpus writes still
                  assembles and looks up: CW(CDSC) and the rest, RD(SEOP),
                  GONG(SEOP), GONGSEOP, SUSEOP, L(V+I), CT0011(V+I)

  ibm_spelling_family  C28-6129's printed spellings (+NMG, *N+, M+NMG,
                  SU; strap_asm.IBM_SPELLING) take their op's secondary and
                  assemble to the host spelling's word.  A CONTROL only:
                  strap_asm's own path respells before the guard, so
                  removing secondary_error's new respelling fails nothing
                  here (measured 2026-11-15); the bug it fixes reached only
                  the 7030 op table, through optab7030.secondary_code,
                  where check_strap2_secondary.py's sweep and
                  check_strap2_7030_optab.py catch it.

MEASURED INJECTIONS, 2026-11-15 (each on a copy, reverted by cmp; control
passes before and after):
    the immediate refusal removed           FAIL refused_imm, optable
    the connective refusal removed          FAIL refused_conn, optable
    the CW-only rule removed                FAIL refused_family, optable_family
    the SEOP rule removed                   FAIL refused_family, optable_family
    the progressive-family rule removed     FAIL refused_fp, optable,
                                                 refused_family, optable_family
    the more-than-one rule removed          FAIL refused_family, optable_family
                                            (NOTHING until the mixed pairs went
                                            in: classify refuses two
                                            progressives by itself)
    the guard not called in emit_statement  FAIL refused_fp, refused_family
    the guard not called in optable.lookup  FAIL optable, optable_family
    strap_asm and optable before the fix    FAIL all six refusal checks
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
import strap_asm as a                      # noqa: E402
from strap2 import optable                  # noqa: E402

failures = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else ": " + detail))
    if not ok:
        failures.append(name)


def assemble(stmt):
    try:
        return a.assemble(" " + stmt + "\n").words
    except a.AssemblerError as e:
        return "AE:" + str(e)
    except Exception as e:
        return type(e).__name__ + ":" + str(e)


def refused(stmts, words):
    bad = [(s, r) for s in stmts for r in [assemble(s)]
           if not (isinstance(r, str) and r.startswith("AE:") and words in r)]
    return not bad, str(bad)


SECS = ["V+I", "V+IC", "V+ICR", "V-I", "V-IC", "V-ICR"]
check("refused_fp: FP op with a progressive secondary",
      *refused([f"+({s})(N),100" for s in SECS] +
               ["SRT(V+I),100", "E+(V-I)(U),1", "*A(V+IC)(N),100"],
               "a secondary op of VFL and connective operations only"))
check("refused_imm: immediate with a progressive secondary",
      *refused([f"LI({s})(BU,8),5" for s in SECS] +
               ["*I(V+I)(BU,8),5", "+I(V-ICR)(BU,8),5", "CI0001(V+I)(BU,6),5"],
               "immediate addressing and a progressive"))
check("refused_conn: connective with (N) or (U)",
      *refused(["C0001(N),100", "C0001(U),100", "CM0101(N),100", "LF(U),100"],
               "a connective with a floating-point data description"))

LOOK = [("+", "N", ("V+I",)), ("SRT", None, ("V+I",)), ("LI", "BU", ("V+IC",)),
        ("*I", "BU", ("V+I",)), ("C0001", "N", ()), ("C0001", "U", ())]
bad = []
for op, m, s in LOOK:
    try:
        e = optable.lookup(op, m, s)
    except Exception as ex:
        e = type(ex).__name__
    if e is not None:
        bad.append((op, m, s, getattr(e, "kind", e)))
check("optable: each refused combination is None", not bad, str(bad))

WANT = {
    "+(N),100": {32: 0x19002000000000},
    "L(V+IC)(BU,8),5": {32: 0x58044001050},
    "+(V+I)(BU,8),100": {32: 0x648024001010},
    "LI(BU,8),5": {32: 0x500008084001050},
    "CI0001(BU,6),5": {32: 0x1400008083000270},
    "C0001(BU,8),100": {32: 0x648004000270},
}
bad = [(s, assemble(s)) for s, w in WANT.items() if assemble(s) != w]
check("controls keep their words", not bad, str(bad))
ok = all(not isinstance(assemble(s), str) for s in
         ["L(V+I)(BU,7,8),100", "K(BU,7)(V+I),100", "+(V-ICR)(BU,8),100"])
check("controls: Figure 7 and C22-6578 orderings assemble", ok)
bad = [(n, m, s) for n, m, s in [("L", "BU", ("V+IC",)), ("C0001", "BU", ()),
                                ("+", "N", ()), ("LI", "BU", ())]
       if optable.lookup(n, m, s) is None]
check("controls: optable keeps them", not bad, str(bad))

BADFAM = ["B(CCR),100", "XW(CD),100", "LX(SEOP),1,100", "RD(CCR),1,100",
          "RD(V+I),1,100", "RDSEOP(SEOP),1,100", "CCW(SEOP),1,100",
          "L(V+I)(V+IC)(BU,8),100", "DD(SEOP),5", "RD(SEOP)(V+I),1,100",
          "CW(CCR)(CD),100,1", "+(SEOP)(BU,3),100", "CW(V+I),100,1"]
bad = [(s, r) for s in BADFAM for r in [assemble(s)]
       if not (isinstance(r, str) and r.startswith("AE:")
               and ("secondary op" in r or "SEOP form" in r))]
check("refused_family: a secondary on another family's op", not bad, str(bad))

LOOKF = [("B", None, ("CCR",)), ("XW", None, ("CD",)), ("LX", None, ("SEOP",)),
         ("RD", None, ("CCR",)), ("RD", None, ("V+I",)), ("RDSEOP", None, ("SEOP",)),
         ("CCW", None, ("SEOP",)), ("L", "BU", ("V+I", "V+IC")), ("DD", None, ("SEOP",)),
         ("RD", None, ("SEOP", "V+I")), ("CW", None, ("CCR", "CD")),
         ("+", "BU", ("SEOP",)), ("CW", None, ("V+I",))]
bad = [(op, m, s) for op, m, s in LOOKF if optable.lookup(op, m, s) is not None]
check("optable_family: lookup() is None for each", not bad, str(bad))

GOOD = ["CW(CCR),100,1", "CW(CD),100,1", "CW(CDSC),100,1", "CW(CR),100,1",
        "CW(SCR),100,1", "RD(SEOP),1,100", "W(SEOP),1,100", "CTL(SEOP),1,100",
        "LOC(SEOP),1,100", "REL(SEOP),1,100", "GONG(SEOP),1", "REW(SEOP),1",
        "GONGSEOP,1", "SUSEOP,1,100", "L(V+I)(BU,8),100", "CT0011(V+I)(BU,8),100",
        "SF(V+ICR)(BU,8),100", "M+(V+ICR)(BU,8),100"]
bad = [(s, assemble(s)) for s in GOOD if isinstance(assemble(s), str)]
GOODL = [("CW", None, ("CDSC",)), ("RD", None, ("SEOP",)), ("GONG", None, ("SEOP",)),
         ("GONGSEOP", None, ()), ("SUSEOP", None, ()), ("L", "BU", ("V+I",)),
         ("CT0011", "BU", ("V+I",)), ("REW", None, ("SEOP",))]
bad += [(op, m, s) for op, m, s in GOODL if optable.lookup(op, m, s) is None]
check("legal_family: the corpus's families still assemble and look up", not bad, str(bad))

SPELL = [("+NMG(V+I)(BU,8),100", "+MGN(V+I)(BU,8),100"),
         ("*N+(V+I)(BU,8),100", "*+N(V+I)(BU,8),100"),
         ("M+NMG(V-IC)(BU,8),100", "M+MGN(V-IC)(BU,8),100"),
         ("SU(SEOP),1,100", "LOC(SEOP),1,100")]
bad = [(p, assemble(p)) for p, q in SPELL
       if isinstance(assemble(p), str) or assemble(p) != assemble(q)]
bad += [(p, assemble(q)) for p, q in SPELL if isinstance(assemble(q), str)]
check("ibm_spelling_family: a printed spelling takes its op's secondaries", not bad, str(bad))

if failures:
    print(f"*** {len(failures)} CHECK(S) FAILED ***")
    sys.exit(1)
print("ALL CHECKS PASSED")
