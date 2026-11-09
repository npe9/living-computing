#!/usr/bin/env python3
"""check_smac7030.py -- the 7030 SMAC (decks/smac7030_shell.strap), running
on the Bluespec model, against strap/smac.py, card for card.

>>> Both are RECONSTRUCTIONS of IBM's SMAC, so agreement shows that the
>>> 7030 program implements the host specification.  It does not show that
>>> either is IBM's.  The printed anchors are in parts A and B: C22-6678-1
>>> p.47's card images, and J28-6128 pp.8-11's examples, whose expected
>>> cards are written out below by hand from the bulletin. <<<

  A. C22-6678-1 printed p.47, the one SMAC program IBM printed: every
     output card equals smac.expand's.
  B. J28-6128's worked examples, pp.5-12: MMVPT, MOUT, the compares in both
     spellings, MOUTF, and MOUTV in all its forms.  Expected cards written
     by hand from the bulletin, and smac.py must give them too.
  C. Edge cases, against smac.py: tag forms, null and trailing parameters,
     commas in parentheses, "MEOJ,", unknown M operations, comment forms,
     blank cards, continuation cards on SMAC and STRAP statements, columns
     73-80, $SCR and $FETCH's printed forms, /10/, //, /Q/, and macros
     nested two deep with outer parameters used after the inner returns.
  D. Each failure halts at HALTE with its code in QERR.  smac.py raises on
     the same conditions, except codes 11 and 13, limits of this version.
  E. No simulator: all 78 generators of the MCP library compile and
     assemble, and each stored card image equals its IQS text.
  F. What only a 7030 SMAC can do: STRAP statements in generator logic
     (p.12, p.13 items 2-3), reading QLIT, storing QCN (p.5), testing QGUB,
     QCIBIT, QMACBIT and QINBIT (p.13), and using X9 across an inner macro
     (p.13 item 6); and a SMAC statement in logic (p.12).  smac.py cannot
     run these, so the expected cards are written by hand.
  G. The /Q/ counter carries: from Q0099, the next is Q0100.
  H. SMAC compiling generators (J28-6128 p.3, docs/smac_7030.md step 5), using
     the special library decks/smac_special_library.smac, on the model.  The
     Python stand-in compiles that library once.  With it SMAC then compiles
     (H1) the special library's own source, which must reproduce word for
     word the library it is running, and (H2, H3) every generator above,
     each of which must assemble to the stand-in's image, word for word.
     H4 is the special library's failure paths.  A generator whose source
     has a continuation card in a skeleton halts with 17, a limit of this
     version.

A byte outside the IQS table in an output card fails the case.  Core
outside the image reads back 0xAA on the model, so that is a diagnosis.

PROVEN DISCRIMINATING: the injections and their observed failure sets are
in tests/run_tests.sh beside this test's entry.
"""
import os
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
import charsets                                              # noqa: E402
import smac                                                  # noqa: E402
import smac_mcp                                              # noqa: E402
import smac7030_build as build                               # noqa: E402

# Each library keeps its generators' source, for part H.
_library_add = smac.Library.add


def _add_keeping_source(self, ops, text):
    self.__dict__.setdefault("sources", []).append((list(ops), text))
    return _library_add(self, ops, text)


smac.Library.add = _add_keeping_source

fails = 0
INV = {v: k for k, v in charsets.IQS.items()}
BSV = os.path.join(HERE, "..", "bsv")


def result(ok, msg):
    global fails
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} {msg}")


def card(tag, var, col1=" "):
    return col1 + tag.ljust(8) + var


def deck(*rows):
    return "\n".join(card(*r) if isinstance(r, tuple) else card("", r) for r in rows)


STEPS = {f"StretchSmac7030H2{k}Tb": 400000000 for k in "abcd"}


def run_7030(module, lib, cards, n_out, tmp, uniq_start=None):
    """Returns (halt name, QERR, output cards or None, messages)."""
    ops = list(lib.gens)
    text, f = build.build(lib, ops, cards, n_out, uniq_start)
    sym = f["symtab"]
    path = os.path.join(tmp, module + ".strap")
    with open(path, "w") as fh:
        fh.write(text)
    first = f["outcnt_word"]
    args = [os.path.join(HERE, "run_program.sh"), path, module,
            f"DUMP={first},{1 + n_out * 10}", f"STEPS={STEPS.get(module, 30000000)}",
            f"FASTLOAD={os.path.join(tmp, module + '.hex')}"]
    # A check against 0 prints QERR's value whichever way it comes out; the
    # value is read from that line, and a nonzero one is judged by the case.
    args.append(f"QERR:{sym['BTERR'] // 64}=" + "0x0")
    r = subprocess.run(args, capture_output=True, text=True, cwd=HERE)
    out = r.stdout
    for name in os.listdir(BSV):            # by exact name, never a glob
        if name in (module + ".bsv", module + "_sim", module + "_sim.so"):
            os.remove(os.path.join(BSV, name))
    if "step cap" in out or r.returncode:
        return "NOHALT", None, None, (out + r.stderr)[-800:]
    m = re.search(r"(?:PASS|FAIL) QERR = (\d+)", out)
    qerr = int(m.group(1)) >> 40 if m else None
    mem = {int(a): int(v, 16) for a, v in re.findall(r"MEMDUMP (\d+) ([0-9a-f]+)", out)}
    count = mem[first] >> 40
    if count > n_out:
        return "HALT", qerr, None, f"count {count} is past the {n_out} dumped"
    cards_out, bad = [], None
    for i in range(count):
        s = ""
        for w in range(10):
            v = mem[first + 1 + i * 10 + w]
            for k in range(8):
                c = (v >> (56 - 8 * k)) & 255
                if c not in INV:
                    bad = f"card {i} column {w * 8 + k + 1}: byte {c:#04x} is not IQS"
                s += INV.get(c, "?")
        cards_out.append(s.rstrip())
    return "HALT", qerr, cards_out, bad


# ---- the cases ------------------------------------------------------
P47 = [l.rstrip("\n") for l in open(os.path.join(HERE, "..", "decks", "mcpref_example1.smac"))
       if not l.startswith("!")]

BUL = smac.Library()
BUL.add(["MOP1", "MOP2", "MOP3", "MOP4"], deck(
    "MBGEN", "MOUTF,SK1,3,SK2,0,SK3,5", "MEXIT",
    ("SK1", "MBSKL"), ("/2/", "L,/4/"), "*,/5/", "ST,/6/", "B,$/3/",
    ("SK2", "MBSKL"), ("/2/", "B,$SUBRT"), ",/3/",
    ("SK3", "MBSKL"), ("/2/", "L,/4/"), "+,/5/", "-,/6/", "*,/7/", "ST,/8/", "MEGEN"))
BUL.add(["MADD"], deck("MBGEN", "MOUTV,1,SK1,1,N,SK2,1,1,SK3,1", "MEXIT",
                       ("SK1", "MBSKL"), ("/2/", "L,/4/"), ("SK2", "MBSKL"), "+,/1/",
                       ("SK3", "MBSKL"), "ST,/1/", "MEGEN"))
BUL.add(["MADMY"], deck("MBGEN", "MOUTV,1,SKEL1,1,N,SKEL2,2,2,SKEL3,1", "MEXIT",
                        ("SKEL1", "MBSKL"), ("/2/", "L,/4/"), ("SKEL2", "MBSKL"),
                        "+,/1/", "*,/2/", ("SKEL3", "MBSKL"), "ST,/1/", "MEGEN"))
BUL_IN = [card("NAME", "MOP1,A1,A2,A3"), card("NAME", "MOP2"),
          card("NAME", "MOP3,C1,C2,C3,C4,C5"), card("NAME", "MOP4,D1,D2,D3"),
          card("", "MADD,A,B,C,D"), card("", "MADD,A,B"),
          card("NAME", "MADMY,A,B,C,D,E,F,G,H,I")]
BUL_WANT = [card("NAME", "L,A1"), card("", "*,A2"), card("", "ST,A3"), card("", "B,$MOP1"),
            card("NAME", "B,$SUBRT"), card("", ",MOP2"),
            card("NAME", "L,C1"), card("", "+,C2"), card("", "-,C3"), card("", "*,C4"),
            card("", "ST,C5"),
            card("NAME", "L,D1"), card("", "*,D2"), card("", "ST,D3"), card("", "B,$MOP4"),
            card("", "L,A"), card("", "+,B"), card("", "+,C"), card("", "ST,D"),
            card("", "L,A"), card("", "ST,B"),
            card("NAME", "L,A"), card("", "+,B"), card("", "*,C"), card("", "+,D"),
            card("", "*,E"), card("", "+,F"), card("", "*,G"), card("", "ST,H"),
            card("", "ST,I")]

# the remaining worked examples, each generator under its own name so one
# run holds them all
COMP = [("MKPEQI", 4, "R23?T", "equal"), ("MKPEQI", 5, "FG", "unequal"),
        ("MKCEQI", 4, "R23?T", "equal"), ("MKCEQI", 5, "FG", "equal"),
        ("MKPNEQI", 5, "FG", "unequal"), ("MKCNEQI", 5, "FG", "equal"),
        ("MKPEQ", 4, "R23?T", "equal"), ("MKCNEQ", 5, "XX", "unequal")]
for i, (op, n, chars, res) in enumerate(COMP):
    name = f"MC{i}"
    BUL.add([name], deck("MBGEN", f"{op},QPT1,{n},{chars},NAME", "MOUT,QPT1,SKFALL",
                         "MEXIT", ("NAME", "MOUT,QPT1,SKTAKEN"), "MEXIT",
                         ("SKTAKEN", "MBSKL"), "TAKEN", ("SKFALL", "MBSKL"), "FALL", "MEGEN"))
    taken = (res == "equal") != ("NEQ" in op)
    BUL_IN.append(card("", f"{name},R23?T,FGH,IJKL"))
    BUL_WANT.append(card("", "TAKEN" if taken else "FALL"))
BUL.add(["MOUTP6"], deck("MBGEN", "MOUT,QPT1,SK1", "MEXIT", ("SK1", "MBSKL"),
                         ("/2/", "L,/4/"), "+,/5/", "ST,/6/", "MEGEN"))
BUL.add(["MMV5"], deck("MBGEN", "MMVPT,QPT1,3,QPT2", "MOUT,QPT2,SK1", "MEXIT",
                       ("SK1", "MBSKL"), "L,/1/", "ST,/4/", "MEGEN"))
BUL.add(["MV9"], deck("MBGEN", "MOUT,QPT1,SK1", "MOUTV,5,SK2,1", "MOUT,QPT1,SK3",
                      "MEXIT", ("SK1", "MBSKL"), ("/2/", "L,/4/"), ("SK2", "MBSKL"),
                      "+,/5/", ("SK3", "MBSKL"), "ST,/10/", "MEGEN"))
BUL.add(["MV10"], deck("MBGEN", "MOUTV,1,SK1,1,5,SK2,1,1,SK3,1", "MEXIT",
                       ("SK1", "MBSKL"), ("/2/", "L,/4/"), ("SK2", "MBSKL"), "+,/1/",
                       ("SK3", "MBSKL"), "ST,/1/", "MEGEN"))
LONG = [card("", "L,A")] + [card("", "+," + x) for x in "BCDEF"] + [card("", "ST,G")]
BUL_IN += [card("NAME", "MOUTP6,A,B,C"), card("TAG", "MMV5,A1,A2,A3,A4"),
           card("", "MV9,A,B,C,D,E,F,G"), card("", "MV10,A,B,C,D,E,F,G"),
           card("NAME", "MADMY,A,B,C,D,E,F,G,H,I,J,K"), card("NAME", "MADMY,A,B,C"),
           card("X", "L,Y'  A COMMENT")]
BUL_WANT += [card("NAME", "L,A"), card("", "+,B"), card("", "ST,C"),
             card("", "L,A1"), card("", "ST,A4")] + LONG + LONG + [
    card("NAME", "L,A"), card("", "+,B"), card("", "*,C"), card("", "+,D"),
    card("", "*,E"), card("", "+,F"), card("", "*,G"), card("", "+,H"),
    card("", "*,I"), card("", "ST,J"), card("", "ST,K"),
    card("NAME", "L,A"), card("", "ST,B"), card("", "ST,C"),
    card("X", "L,Y'  A COMMENT")]

MCP = smac_mcp.library()
EDGE_LIB = smac_mcp.library()
EDGE_LIB.add(["MEDGE"], deck("MBGEN", "MOUTF,SK1,7,SK2,0", "MEXIT",
                             ("SK1", "MBSKL"), ("/2/", "L,/4/"), "ST,/10/", "A//B",
                             ",0.'  A/B /4/ IS NOT SUBSTITUTED",
                             ("SK2", "MBSKL"), "NOP", "MEGEN"))
EDGE_LIB.add(["MLONGNAME"], deck("MBGEN", "MOUTF,SK1,1", "MEXIT",
                                 ("SK1", "MBSKL"), "NINE,/4/", "MEGEN"))
EDGE_LIB.add(["MLOOP"], deck("MBGEN", "MOUT,QPT1,SK", "MEXIT", ("SK", "MBSKL"),
                             ("A/Q/", "L,/4/"), "//,/5/", "BZ,A/Q/", "MEGEN"))
EDGE_LIB.add(["MIN2"], deck("MBGEN", "MOUT,QPT1,SK", "MEXIT", ("SK", "MBSKL"),
                            ("/2/", "LX,/4/"), ("B/Q/", "BZ,B/Q/"), "MEGEN"))
EDGE_LIB.add(["MIN1"], deck("MBGEN", "MOUT,QPT1,SK", "MEXIT", ("SK", "MBSKL"),
                            ("/2/", "L1,/4/"), ("IN", "MIN2,/5/"), "L2,/5/", "MEGEN"))
EDGE_LIB.add(["MOUTER"], deck("MBGEN", "MMVPT,QPT1,1,QPT3", "MOUTV,N,SK,1", "MOUT,QPT3,SKZ", "MEXIT",
                              ("SK", "MBSKL"), ("A/Q/", "MIN1,X/1/,Y"), "AFTER,A/Q/",
                              ("SKZ", "MBSKL"), "LAST,/1/", "MEGEN"))
EDGE_IN = [
    "*        L,A HEAD THAT IS STARRED",
    card("TAGC", "MRD,A,"), "*        B,", "*        C",
    card("", "MRD,A,'  COMMENT"), "*        IGNORED",
    card("", "MRD,A,"), "", "*        B",
    "C A COMMENT CARD", "*        MRD,STAR",
    card("", "L,D"), "", "*        ,MORE",
    card("", "MLOOP,X,Y"), card("", "MLOOP,U,V"),
    card("TOP", "MOUTER,P,R"),
    "  TAGB   MRD,A,B",                       # tag starts in column 3
    " X Y     MRD,A,B",                       # a blank inside the tag field
    card("", "MRD,,B"), card("", "MRD,A,"), card("", "MRD,,"),
    card("", "MEOJ,"), card("", "MEOJ"),
    card("", "MRD,(A,B),C"), card("", "MRD,(A,(B,C)),D'  COMMENT, WITH COMMA"),
    card("", "MRD , A , B "), card("", "   MRD,A,B"),
    card("", "MNOSUCH,A,B"), card("", "M"), card("", "MRDX,A"),
    card("", "MRD (A),B"),
    card("'", "MRD,A,B"), card("", "'MRD,A,B"),
    "C COLUMN ONE MAKES THIS A COMMENT, MRD,A,B",
    "",
    card("TAGONLY", ""),
    card("", "MRD,A,B").ljust(72) + "ID000002",
    card("", "L,A").ljust(72) + "ID000001",
    "*        CONTINUING L,A",
    card("", "L,B"),
    "*        ,MORE",
    card("", "MSCR,FWA,N,END"), card("LAB", "MFETCH,22LOADER,0,BUF,0,ERR,END"),
    card("", "MABEX"), card("", "MABEX,TBL"),
    card("HERE", "MEDGE,A,B,C,D,E,F,G"), card("", "MEDGE"),
    card("", "MLONGNAME,X"), card("", "MLONGNAMEX,X"),
    card("", "MEND,INIT"),
]


def err_lib(*rows):
    lib = smac_mcp.library()
    lib.add(["MBAD"], deck(*rows))
    return lib


def lit(rows):
    return err_lib("MBGEN", *rows, "MEXIT", ("SK", "MBSKL"), "L,X", "MEGEN")


LONGARGS = [card("", "MBAD," + ",".join("A" * 30))] + \
    ["*        ," + ",".join("A" * 30) for _ in range(3)] + ["*        ,A,B,C,D,E,F,G,H"]
ERRORS = [
    # (name, code, library, cards, does smac.py raise too?, /Q/ start)
    ("4 a lone slash", 4, err_lib("MBGEN", "MOUTF,SK,0", "MEXIT", ("SK", "MBSKL"), "L,A/B", "MEGEN"),
     [card("", "MBAD")], True, None),
    ("5 /n/ past the parameters", 5,
     err_lib("MBGEN", "MOUTF,SK,0", "MEXIT", ("SK", "MBSKL"), "L,/4/", "MEGEN"),
     [card("", "MBAD")], True, None),
    ("6 a tag overflows columns 2-9", 6,
     err_lib("MBGEN", "MOUTF,SK,0", "MEXIT", ("SK", "MBSKL"), ("/2/X", "L,A"), "MEGEN"),
     [card("EIGHTCHR", "MBAD")], True, None),
    ("7 MOUTV's N is not whole", 7,
     err_lib("MBGEN", "MOUTV,N,SK,2", "MEXIT", ("SK", "MBSKL"), "L,/1/", "MEGEN"),
     [card("", "MBAD,A,B,C")], True, None),
    ("8 MOUTF has no skeleton", 8, MCP, [card("", "MEND")], True, None),
    ("9 a pointer before it is defined", 9, lit(["MOUT,QPT3,SK"]), [card("", "MBAD")], True, None),
    ("10 QCN never stored", 10, lit(["MMVPT,QPT1,QCN,QPT2"]), [card("", "MBAD")], True, None),
    ("11 too many parameters", 11, lit([]), LONGARGS, False, None),
    ("12 macros nested too deep", 12,
     err_lib("MBGEN", "MOUTF,SK,0", "MEXIT", ("SK", "MBSKL"), "MBAD", "MEGEN"),
     [card("", "MBAD")], True, None),
    ("13 the /Q/ counter runs out", 13, lit([]), [card("", "MBAD")], False, "9999"),
    ("14 ten continuation cards", 14, MCP,
     [card("", "MRD,A,")] + ["*        B"] * 10, True, None),
    ("15 MGETL on a non-literal", 15, lit(["MGETL,QPT1,4"]), [card("", "MBAD,ABC")], True, None),
]

# ---- F: STRAP in generator logic; expected cards by hand ---------------
F_LIB = smac.Library()
F_LIB.add(["MSEL"], deck("MBGEN", "MGETL,QPT1,4", "L(BU,24),QLIT($2)", "+(BU,24),KTWO($1)",
                         "ST(BU,24),QCN($2)", "MMVPT,QPT1,QCN,QPT2", "MOUT,QPT2,SK", "MEXIT",
                         ("KTWO", "DD(BU,24),2"), ("SK", "MBSKL"), "L,/1/", "MEGEN"))
F_LIB.add(["MUSE"], deck("MBGEN", "BB,QGUB($2),OLD($1)", "MOUT,QPT1,S1", "MEXIT",
                         ("OLD", "MOUT,QPT1,S2"), "MEXIT",
                         ("S1", "MBSKL"), "FIRST", ("S2", "MBSKL"), "AGAIN", "MEGEN"))
F_LIB.add(["MPREV"], deck("MBGEN", "BB,QCIBIT($2),P1($1)", "MOUT,QPT1,S0", "MEXIT",
                          ("P1", "MOUT,QPT1,S1"), "MEXIT",
                          ("S0", "MBSKL"), "NOTMAC", ("S1", "MBSKL"), "AFTERMAC", "MEGEN"))
F_LIB.add(["MLEVEL"], deck("MBGEN", "LVI,$9,99.0", "BZB,QMACBIT($2),BAD($1)",
                           "BB,QINBIT($2),IN($1)", "MOUT,QPT1,S0", "MEXIT",
                           ("IN", "MOUT,QPT1,S1"), "MEXIT",
                           ("BAD", "MOUT,QPT1,S2"), "MEXIT",
                           ("S0", "MBSKL"), "TOP", ("S1", "MBSKL"), "INNER",
                           ("S2", "MBSKL"), "NOMACBIT", "MEGEN"))
F_LIB.add(["MKEEP"], deck("MBGEN", "LVI,$9,7.0", "MOUT,QPT1,SK", "KVI,$9,7.0", "BXE,OK($1)",
                          "MOUT,QPT1,SB", "MEXIT", ("OK", "MOUT,QPT1,SG"), "MEXIT",
                          ("SK", "MBSKL"), "MLEVEL", ("SG", "MBSKL"), "X9KEPT",
                          ("SB", "MBSKL"), "X9LOST", "MEGEN"))
F_LIB.add(["MSET9"], deck("MBGEN", "MEXIT", ("SK", "MBSKL"), "LVI,$9,/4/", "MEGEN"))
F_LIB.add(["MVLOAD"], deck("MBGEN", "MOUTF,SK,1", "MEXIT", ("SK", "MBSKL"), "LVI,$9,/4/", "MEGEN"))
F_LIB.add(["MINLOG"], deck("MBGEN", "MVLOAD,5.0", "KVI,$9,5.0", "BXE,OK($1)", "MOUT,QPT1,SB", "MEXIT",
                           ("OK", "MOUT,QPT1,SG"), "MEXIT", ("SG", "MBSKL"), "LOGICOK",
                           ("SB", "MBSKL"), "LOGICBAD", "MEGEN"))
F_LIB.add(["MNUM"], deck("MBGEN", "MGETL,QPT1,4", "L(BU,24),QLIT($2)", "K(BU,24),K127($1)", "BAE,OK($1)",
                         "MOUT,QPT1,SB", "MEXIT", ("OK", "MOUT,QPT1,SG"), "MEXIT",
                         "CNOP", ("K127", "DD(BU,24),127"),
                         ("SG", "MBSKL"), "LITOK", ("SB", "MBSKL"), "LITBAD", "MEGEN"))
F_IN = [card("", "MSEL,2,X,Y"), card("", "MUSE"), card("", "MUSE"), card("", "L,A"),
        card("", "MPREV"), card("", "MPREV"), "C A COMMENT IS NOT A STATEMENT", card("", "MPREV"),
        card("", "L,B"), card("", "MPREV"), card("", "MLEVEL"), card("", "MKEEP"),
        card("", "MINLOG"), card("", "MNUM,127"), card("", "MNUM,127.")]
F_WANT = [card("", "L,X"), card("", "FIRST"), card("", "AGAIN"), card("", "L,A"),
          card("", "NOTMAC"), card("", "AFTERMAC"), "C A COMMENT IS NOT A STATEMENT",
          card("", "AFTERMAC"), card("", "L,B"), card("", "NOTMAC"), card("", "TOP"),
          card("", "INNER"), card("", "X9KEPT"), card("", "LOGICOK"), card("", "LITOK"), card("", "LITOK")]

G_LIB = smac.Library()
G_LIB.add(["MTG"], deck("MBGEN", "MOUTF,SK,0", "MEXIT", ("SK", "MBSKL"), ("A/Q/", "NOP"), "MEGEN"))
# For part H: comment cards in a skeleton are not skeleton statements.
G_LIB.add(["MCOMNT"], deck("MBGEN", "MOUTF,SK,0", "MEXIT", ("SK", "MBSKL"), ("'NOTE", "A NOTE"),
                           "L,A", ("", "A COLUMN 1 NOTE", "C"), "ST,B", "MEGEN"))


# ---- H: SMAC compiles generators ---------------------------------------
SPECIAL, SPECIAL_GROUPS = build.special_library()


def source_cards(lib, skip=()):
    """Every generator's source cards once, and the Generator for each."""
    cards, gens = [], []
    for ops, text in lib.sources:
        if ops[0] in skip:
            continue
        cards += [c.rstrip() for c in text.splitlines() if c.strip()]
        gens.append(lib.gens[ops[0]])
    return cards, gens


def special_plus(lib):
    both = smac.Library()
    both.gens.update(SPECIAL.gens)
    both.gens.update(lib.gens)
    return both


def compare_images(label, res, gens, lib_of):
    h, qe, got, note = res
    result(h == "HALT" and qe == 0, f"{label}: ends with QERR {qe} ({h})")
    if got is None or note or qe != 0:
        result(False, f"{label}: no output to compare ({note})")
        return
    q = build.shell_symbols()
    texts = build.split_compiled(got)
    result(len(texts) == len(gens), f"{label}: {len(gens)} generators out, got {len(texts)}")
    same = 0
    for g, t in zip(gens, texts):
        a = build.link_generator(t)
        b = build.link_generator(build.compile_generator(g, q, lib_of(g)))
        if a == b:
            same += 1
        else:
            where = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]), "length")
            result(False, f"{label}: {g.ops} differs at word {where} ({len(a)}, {len(b)} words)")
    result(same == len(gens), f"{label}: {same} of {len(gens)} generators word for word")


def sp(*rows):
    return [card(*r) if isinstance(r, tuple) else card("", r) for r in rows]


H_ERRORS = [
    ("16 MBSKL has no tag", 16, sp("MBGEN", "MEXIT", "MBSKL", "L,A", "MEGEN")),
    ("16 no MEGEN follows", 16, sp("MBGEN", "MEXIT", ("SK", "MBSKL"), "L,A")),
    ("17 a continuation in a skeleton", 17,
     sp("MBGEN", "MEXIT", ("SK", "MBSKL"), "L,A,") + ["*        B"] + sp("MEGEN")),
    ("18 every end mark in the text", 18, sp("MBGEN", "MEXIT", ("SK", "MBSKL"), 'L,?"&:=', "MEGEN")),
    ("19 MOUTF with an odd argument", 19, sp("MBGEN", "MOUTF,SK", "MEXIT", "MEGEN")),
    ("19 MOUTF with sixteen pairs", 19,
     sp("MBGEN", "MOUTF" + ",S,1" * 12 + ",") + ["*        " + ",".join(["S,1"] * 4)] + sp("MEXIT", "MEGEN")),
    ("19 MOUTV not in threes", 19, sp("MBGEN", "MOUTV,1,SK", "MEXIT", "MEGEN")),
    ("20 MOUTV with two N", 20, sp("MBGEN", "MOUTV,N,S,1,N,S,1", "MEXIT", "MEGEN")),
    ("21 nine characters in a compare", 21, sp("MBGEN", "MKPEQI,QPT1,1,NINECHARS,T", "MEXIT", "MEGEN")),
    ("22 a skeleton of 100 statements", 22,
     sp("MBGEN", "MEXIT", ("SK", "MBSKL")) + sp(*["NOP"] * 100) + sp("MEGEN")),
]


# 74 of the MCP library's 78 generators are p.14's rule with another operation
# name, so the suite compiles these six, one of each shape.  SMAC7030_FULL=1
# compiles all 78: measured 2026-11-08, 78 of 78 word for word, 73 minutes.
MCP_SHAPES = ("MRD", "MEOJ", "MSCR", "MFETCH", "MABEX", "MEND")
H = {}


def h_jobs():
    """The part H jobs.  The cards out are at most the stand-in's lines,
    doubled for the two DD cards each skeleton statement becomes."""
    q = build.shell_symbols()

    def room(gens, lib):
        return 5 + sum(2 * build.compile_generator(g, q, lib).count("\n") for g in gens)

    jobs = {}
    h1 = [c for _, cs in SPECIAL_GROUPS for c in cs]
    H["1"] = [SPECIAL.gens[n[0]] for n, _ in SPECIAL_GROUPS]
    jobs["H1"] = ("StretchSmac7030H1Tb", SPECIAL, h1, room(H["1"], SPECIAL))
    skip = ()
    if not os.environ.get("SMAC7030_FULL"):
        skip = tuple(op for op in MCP.gens if op not in MCP_SHAPES)
    H["2"] = {}
    for key, lib, sk in (("a", MCP, skip), ("b", BUL, ()), ("c", EDGE_LIB, tuple(MCP.gens)),
                         ("d", G_LIB, ())):
        c, g = source_cards(lib, sk)
        H["2"][key] = (g, lib)
        jobs["H2" + key] = (f"StretchSmac7030H2{key}Tb", SPECIAL, c, room(g, lib))
    h3c, H["3"] = source_cards(F_LIB)
    jobs["H3"] = ("StretchSmac7030H3Tb", special_plus(F_LIB), h3c, room(H["3"], F_LIB))
    for i, (name, code, cards) in enumerate(H_ERRORS):
        jobs[f"H4{i}"] = (f"StretchSmac7030H4x{i}Tb", SPECIAL, cards, 200)
    return jobs


def h_checks(res):
    compare_images("H1: SMAC compiles its special library, against itself",
                   res["H1"], H["1"], lambda g: SPECIAL)
    for key, what in (("a", "the MCP library"), ("b", "the bulletin's"), ("c", "the edge cases'"),
                      ("d", "the /Q/ case's")):
        g, lib = H["2"][key]
        compare_images(f"H2: {what} generators against the stand-in", res["H2" + key], g,
                       lambda _, one=lib: one)
    compare_images("H3: generators with STRAP in logic", res["H3"], H["3"], lambda g: F_LIB)
    for i, (name, code, cards) in enumerate(H_ERRORS):
        h, qe, got, note = res[f"H4{i}"]
        result(h == "HALT" and qe == code, f"H4: {name} halts with code {code} (got {qe}, {h})")


def compare(label, got, want, note):
    want = [c.rstrip() for c in want]
    if got is None or note:
        result(False, f"{label}: {note}")
        return
    diffs = [i for i, (g, w) in enumerate(zip(got, want)) if g != w]
    ok = len(got) == len(want) and not diffs
    detail = ""
    if not ok:
        detail = f" ({len(got)} cards, want {len(want)}"
        if diffs:
            i = diffs[0]
            detail += f"; card {i}: got {got[i]!r} want {want[i]!r}"
        detail += ")"
    result(ok, f"{label}: {len(want)} cards expected, all must be identical{detail}")


def main():
    with tempfile.TemporaryDirectory() as tmp:
        # E first: no simulator
        n = 0
        q = {k: 0 for k in build.Q_SYMBOLS}
        for op, g in MCP.gens.items():
            build.link_generator(build.compile_generator(g, q, MCP))
            n += 1
        result(n == 78, f"E: all {n} generators of the MCP library compile and assemble")
        text, f = build.build(MCP, list(MCP.gens), P47, 90)
        result(f["lib_words"] > 0, f"E: the full library links, {f['lib_words']} words of generators")

        # A serially: it may have to recompile mkStretchCore, and the rest
        # then only reuse it.
        p47_want = smac.expand(MCP, "\n".join(P47))
        lib47 = smac.Library()
        for op in ("MRD", "MEOJ", "MWAIT", "MBSP", "MCOMM", "MABEOJ", "MIODEF", "MRET", "MEND"):
            lib47.gens[op] = MCP.gens[op]
        h, q47, got, note = run_7030("StretchSmac7030ATb", lib47, P47, len(p47_want) + 5, tmp)
        result(h == "HALT" and q47 == 0, f"A: p.47 ends with QERR {q47} ({h})")
        compare("A: C22-6678-1 p.47 against smac.py", got, p47_want, note)

        jobs = {"B": ("StretchSmac7030BTb", BUL, BUL_IN, len(BUL_WANT) + 5)}
        edge_lib = smac.Library()
        for op in ("MRD", "MEOJ", "MSCR", "MFETCH", "MABEX", "MEND", "MEDGE", "MLONGNAME",
                   "MLOOP", "MIN1", "MIN2", "MOUTER"):
            edge_lib.gens[op] = EDGE_LIB.gens[op]
        edge_want = smac.expand(edge_lib, "\n".join(EDGE_IN))
        jobs["C"] = ("StretchSmac7030CTb", edge_lib, EDGE_IN, len(edge_want) + 5)
        jobs["F"] = ("StretchSmac7030FTb", F_LIB, F_IN, len(F_WANT) + 5)
        jobs["G"] = ("StretchSmac7030GTb", G_LIB, [card("", "MTG"), card("", "MTG")], 5, tmp, "0099")
        for name, code, lib, cards, raises, start in ERRORS:
            small = smac.Library()
            for op in lib.gens:
                if op in ("MRD", "MEND", "MBAD"):
                    small.gens[op] = lib.gens[op]
            jobs[f"D{code}"] = (f"StretchSmac7030D{code}Tb", small, cards, 5, tmp, start)

        jobs.update(h_jobs())

        def go(j):
            return run_7030(*j) if len(j) == 6 else run_7030(*j, tmp)
        with ThreadPoolExecutor(4) as ex:
            res = dict(zip(jobs, ex.map(go, jobs.values())))

        h, qe, got, note = res["B"]
        result(h == "HALT" and qe == 0, f"B: bulletin examples end with QERR {qe} ({h})")
        compare("B: J28-6128 pp.5-12, hand-written cards", got, BUL_WANT, note)
        result(smac.expand(BUL, "\n".join(BUL_IN)) == [c.rstrip() for c in BUL_WANT],
               "B: smac.py gives the same hand-written cards")
        h, qe, got, note = res["C"]
        result(h == "HALT" and qe == 0, f"C: edge cases end with QERR {qe} ({h})")
        compare("C: edge cases against smac.py", got, edge_want, note)
        h, qe, got, note = res["F"]
        result(h == "HALT" and qe == 0, f"F: STRAP in logic ends with QERR {qe} ({h})")
        compare("F: STRAP in logic, hand-written cards", got, F_WANT, note)
        h, qe, got, note = res["G"]
        compare("G: /Q/ carries from Q0099", got,
                [card("AQ0100", "NOP"), card("AQ0101", "NOP")], note)

        h_checks(res)

        for name, code, lib, cards, raises, start in ERRORS:
            h, qe, got, note = res[f"D{code}"]
            result(h == "HALT" and qe == code, f"D: {name} halts with code {code} (got {qe}, {h})")
            if raises:
                try:
                    smac.expand(lib, "\n".join(cards))
                    host = False
                except smac.SmacError:
                    host = True
                result(host, f"D: {name}: smac.py raises too")
    print(f"{'ALL CHECKS PASSED' if not fails else str(fails) + ' CHECK(S) FAILED'}")
    return 1 if fails else 0


sys.exit(main())
