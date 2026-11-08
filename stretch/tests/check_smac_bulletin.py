#!/usr/bin/env python3
"""check_smac_bulletin.py -- the reconstructed SMAC processor
(strap/smac.py) against every worked example in its own bulletin,
J28-6128 "SMAC Language Processor" (6/61, CHM 102634360), with the
errata sheet (CHM 102634361) applied.  Read in the ink.

Each check gives a generator as the bulletin prints it, a subject
statement as the bulletin prints it, and the output the bulletin prints
(or, where it prints no output, the output its text describes).

  p.5-6   MOUT: NAME MADD,A,B,C -> NAME L,A / +,B / ST,C   (printed)
  p.5     MMVPT,QPT1,3,QPT2 puts QPT2 at arg1               (described)
  p.6-7   MKPEQI / MKCEQI on OP,R23?T,FGH,IJKL, as the errata
          corrects them: MKPEQI 4 R23?T equal, MKPEQI 5 FG unequal,
          MKCEQI 4 R23?T equal, MKCEQI 5 FG equal          (printed)
  p.8-9   one MOUTF generator for MOP1..MOP4                (described)
  p.9     MOUTV,5,SK2,1 for MADD,A,B,C,D,E,F,G              (described)
  p.10    MOUTV with three sets, the same statement          (described)
  p.10-11 MOUTV with N: MADD,A,B,C,D and MADD,A,B           (printed)
  p.11-12 MADMY, examples 1-3, N = 3, 4, 0                  (printed)
  p.12    /Q/ unique per execution, // a slash               (described)
  errata  both spellings, MKPEQ and MKPEQI, accepted

ONE DISCREPANCY IN THE BULLETIN, RECORDED: p.1 says OP is "up to nine
alphabetic characters", but its own examples on pp.8-9 use MOP1-MOP4.
The processor accepts digits after the M, as the examples do.
"""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
from smac import Library, Processor, SmacError                # noqa: E402

fails = 0


def card(tag, var, col1=" "):
    return (col1 + tag.ljust(8) + var).rstrip()


def deck(*rows):
    """rows: (tag, var) pairs, or a bare string for a card with no tag."""
    return "\n".join(card(*r) if isinstance(r, tuple) else card("", r) for r in rows)


def run(lib, subject_rows):
    return [c.rstrip() for c in Processor(lib).run(deck(*subject_rows).splitlines())]


def check(name, got, want):
    global fails
    want = [w.rstrip() if isinstance(w, str) else w for w in want]
    ok = got == want
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} {name}")
    if not ok:
        print("   got: ", got)
        print("   want:", want)


# p.5-6 MOUT
lib = Library()
lib.add(["MADD"], deck("MBGEN", "MOUT,QPT1,SK1", "MEXIT", ("SK1", "MBSKL"),
                       ("/2/", "L,/4/"), "+,/5/", "ST,/6/", "MEGEN"))
check("p.6 MOUT: NAME MADD,A,B,C", run(lib, [("NAME", "MADD,A,B,C")]),
      [card("NAME", "L,A"), card("", "+,B"), card("", "ST,C")])

# p.5 MMVPT
lib = Library()
lib.add(["MOP"], deck("MBGEN", "MMVPT,QPT1,3,QPT2", "MOUT,QPT2,SK1", "MEXIT",
                      ("SK1", "MBSKL"), "L,/1/", "ST,/4/", "MEGEN"))
check("p.5 MMVPT,QPT1,3,QPT2 points QPT2 at arg1",
      run(lib, [("TAG", "MOP,A1,A2,A3,A4")]), [card("", "L,A1"), card("", "ST,A4")])

# p.6-7 MKPEQI / MKCEQI, with the errata's corrections of p.7.  Each row:
# the comparison's result as the bulletin prints it, then whether the
# branch to TAG1 (here NAME) follows: EQ ops branch on equal, NEQ on unequal.
for op, n, chars, result in (("MKPEQI", 4, "R23?T", "equal"), ("MKPEQI", 5, "FG", "unequal"),
                             ("MKCEQI", 4, "R23?T", "equal"), ("MKCEQI", 5, "FG", "equal"),
                             ("MKPNEQI", 5, "FG", "unequal"), ("MKCNEQI", 5, "FG", "equal")):
    lib = Library()
    lib.add(["MOP"], deck("MBGEN", f"{op},QPT1,{n},{chars},NAME", "MOUT,QPT1,SKFALL",
                          "MEXIT", ("NAME", "MOUT,QPT1,SKTAKEN"), "MEXIT",
                          ("SKTAKEN", "MBSKL"), "TAKEN", ("SKFALL", "MBSKL"), "FALL", "MEGEN"))
    taken = (result == "equal") != ("NEQ" in op)
    check(f"p.7 {op},QPT1,{n},{chars} on OP,R23?T,FGH,IJKL: {result}, "
          f"{'branch' if taken else 'no branch'}",
          run(lib, [("", "MOP,R23?T,FGH,IJKL")]), [card("", "TAKEN" if taken else "FALL")])

# errata: the bulletin's own spelling is kept too
lib = Library()
lib.add(["MOP"], deck("MBGEN", "MKPEQ,QPT1,4,X,HIT", "MOUT,QPT1,S", "MEXIT",
                      ("HIT", "MOUT,QPT1,T"), "MEXIT", ("S", "MBSKL"), "NE",
                      ("T", "MBSKL"), "EQ", "MEGEN"))
check("p.6 the bulletin's spelling MKPEQ also accepted", run(lib, [("", "MOP,X")]),
      [card("", "EQ")])

# p.8-9 one MOUTF generator for four operations
lib = Library()
lib.add(["MOP1", "MOP2", "MOP3", "MOP4"], deck(
    "MBGEN", "MOUTF,SK1,3,SK2,0,SK3,5", "MEXIT",
    ("SK1", "MBSKL"), ("/2/", "L,/4/"), "*,/5/", "ST,/6/", "B,$/3/",
    ("SK2", "MBSKL"), ("/2/", "B,$SUBRT"), ",/3/",   # printed indented under B: alignment only
    ("SK3", "MBSKL"), ("/2/", "L,/4/"), "+,/5/", "-,/6/", "*,/7/", "ST,/8/",
    "MEGEN"))
check("p.8 MOUTF: NAME MOP1,A1,A2,A3", run(lib, [("NAME", "MOP1,A1,A2,A3")]),
      [card("NAME", "L,A1"), card("", "*,A2"), card("", "ST,A3"), card("", "B,$MOP1")])
check("p.8 MOUTF: NAME MOP2", run(lib, [("NAME", "MOP2")]),
      [card("NAME", "B,$SUBRT"), card("", ",MOP2")])
check("p.8 MOUTF: NAME MOP3,C1,C2,C3,C4,C5", run(lib, [("NAME", "MOP3,C1,C2,C3,C4,C5")]),
      [card("NAME", "L,C1"), card("", "+,C2"), card("", "-,C3"), card("", "*,C4"),
       card("", "ST,C5")])
check("p.8 MOUTF: NAME MOP4,D1,D2,D3", run(lib, [("NAME", "MOP4,D1,D2,D3")]),
      [card("NAME", "L,D1"), card("", "*,D2"), card("", "ST,D3"), card("", "B,$MOP4")])

LONG = [card("", "L,A")] + [card("", "+," + x) for x in "BCDEF"] + [card("", "ST,G")]

# p.9 MOUTV, single set
lib = Library()
lib.add(["MADD"], deck("MBGEN", "MOUT,QPT1,SK1", "MOUTV,5,SK2,1", "MOUT,QPT1,SK3",
                       "MEXIT", ("SK1", "MBSKL"), ("/2/", "L,/4/"), ("SK2", "MBSKL"),
                       "+,/5/", ("SK3", "MBSKL"), "ST,/10/", "MEGEN"))
check("p.9 MOUTV,5,SK2,1: MADD,A,B,C,D,E,F,G", run(lib, [("", "MADD,A,B,C,D,E,F,G")]), LONG)

# p.10 MOUTV, three sets
lib = Library()
lib.add(["MADD"], deck("MBGEN", "MOUTV,1,SK1,1,5,SK2,1,1,SK3,1", "MEXIT",
                       ("SK1", "MBSKL"), ("/2/", "L,/4/"), ("SK2", "MBSKL"), "+,/1/",
                       ("SK3", "MBSKL"), "ST,/1/", "MEGEN"))
check("p.10 MOUTV three sets: MADD,A,B,C,D,E,F,G", run(lib, [("", "MADD,A,B,C,D,E,F,G")]), LONG)

# p.10-11 MOUTV with N
lib = Library()
lib.add(["MADD"], deck("MBGEN", "MOUTV,1,SK1,1,N,SK2,1,1,SK3,1", "MEXIT",
                       ("SK1", "MBSKL"), ("/2/", "L,/4/"), ("SK2", "MBSKL"), "+,/1/",
                       ("SK3", "MBSKL"), "ST,/1/", "MEGEN"))
check("p.10 MOUTV with N: MADD,A,B,C,D", run(lib, [("", "MADD,A,B,C,D")]),
      [card("", "L,A"), card("", "+,B"), card("", "+,C"), card("", "ST,D")])
check("p.11 MOUTV with N: MADD,A,B", run(lib, [("", "MADD,A,B")]),
      [card("", "L,A"), card("", "ST,B")])

# p.11-12 MADMY
lib = Library()
lib.add(["MADMY"], deck("MBGEN", "MOUTV,1,SKEL1,1,N,SKEL2,2,2,SKEL3,1", "MEXIT",
                        ("SKEL1", "MBSKL"), ("/2/", "L,/4/"), ("SKEL2", "MBSKL"),
                        "+,/1/", "*,/2/", ("SKEL3", "MBSKL"), "ST,/1/", "MEGEN"))
check("p.12 MADMY example 1, N = 3", run(lib, [("NAME", "MADMY,A,B,C,D,E,F,G,H,I")]),
      [card("NAME", "L,A"), card("", "+,B"), card("", "*,C"), card("", "+,D"),
       card("", "*,E"), card("", "+,F"), card("", "*,G"), card("", "ST,H"),
       card("", "ST,I")])
check("p.12 MADMY example 2, N = 4", run(lib, [("NAME", "MADMY,A,B,C,D,E,F,G,H,I,J,K")]),
      [card("NAME", "L,A"), card("", "+,B"), card("", "*,C"), card("", "+,D"),
       card("", "*,E"), card("", "+,F"), card("", "*,G"), card("", "+,H"),
       card("", "*,I"), card("", "ST,J"), card("", "ST,K")])
check("p.12 MADMY example 3, N = 0", run(lib, [("NAME", "MADMY,A,B,C")]),
      [card("NAME", "L,A"), card("", "ST,B"), card("", "ST,C")])

# p.12 /Q/ and //
lib = Library()
lib.add(["MLOOP"], deck("MBGEN", "MOUT,QPT1,SK", "MEXIT", ("SK", "MBSKL"),
                        ("A/Q/", "L,/4/"), "//,/5/", "BZ,A/Q/", "MEGEN"))
got = run(lib, [("", "MLOOP,X,Y"), ("", "MLOOP,U,V")])
t1, t2 = got[0][1:9].strip(), got[3][1:9].strip()
check("p.12 /Q/: one tag per execution, used consistently, Q inside, <= 8",
      [t1 != t2, "Q" in t1, len(t1) <= 8, got[2].endswith(t1), got[5].endswith(t2)],
      [True] * 5)
check("p.12 //: a literal slash", [got[1]], [card("", "/,Y")])

# a STRAP statement in generator logic needs a 7030: the host spec says so
lib = Library()
lib.add(["MOP"], deck("MBGEN", "L,QLIT($2)", "MEXIT", "MEGEN"))
try:
    run(lib, [("", "MOP,1")])
    ok = False
except SmacError as e:
    ok = "STRAP" in str(e)
fails += not ok
print(f"{'PASS' if ok else 'FAIL'} a STRAP statement in logic fails loud on the host")

# non-SMAC statements pass through untouched, with their comments
lib = Library()
lib.add(["MOP"], deck("MBGEN", "MEXIT", "MEGEN"))
check("STRAP and comment cards pass through", run(lib, [("X", "L,Y'  A COMMENT")]),
      [card("X", "L,Y'  A COMMENT")])

print("ALL TESTS PASSED" if not fails else f"{fails} TEST(S) FAILED")
sys.exit(1 if fails else 0)
