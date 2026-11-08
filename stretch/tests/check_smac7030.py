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
  B. J28-6128 pp.8-12: MOUTF for MOP1-MOP4 (p.8) and MOUTV with N for
     MADD (pp.10-11) and MADMY (p.12's example 1).  Expected cards written by hand.
  C. Edge cases, against smac.py: a tag not starting in column 2, null and
     trailing parameters, commas in parentheses, "MEOJ,", unknown M
     operations, comment forms, a blank card, a continuation of a STRAP
     statement, columns 73-80, $SCR and $FETCH's printed forms, /10/, //,
     and a slash inside a skeleton's comment.
  D. Each failure halts at HALTE with its code in QERR, where smac.py
     raises SmacError too.  Codes 1-3 are limits of this version only:
     smac.py expands those cases, and the 7030 program must refuse them
     rather than get them wrong.
  E. No simulator: all 78 generators of the MCP library compile and
     assemble, and each stored card image equals its IQS text.

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


def run_7030(module, lib, cards, n_out, tmp):
    """Returns (halt name, QERR, output cards or None, messages)."""
    ops = list(lib.gens)
    text, f = build.build(lib, ops, cards, n_out)
    sym = f["symtab"]
    path = os.path.join(tmp, module + ".strap")
    with open(path, "w") as fh:
        fh.write(text)
    first = f["outcnt_word"]
    args = [os.path.join(HERE, "run_program.sh"), path, module,
            f"DUMP={first},{1 + n_out * 10}", "STEPS=4000000",
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

MCP = smac_mcp.library()
EDGE_LIB = smac_mcp.library()
EDGE_LIB.add(["MEDGE"], deck("MBGEN", "MOUTF,SK1,7,SK2,0", "MEXIT",
                             ("SK1", "MBSKL"), ("/2/", "L,/4/"), "ST,/10/", "A//B",
                             ",0.'  A/B /4/ IS NOT SUBSTITUTED",
                             ("SK2", "MBSKL"), "NOP", "MEGEN"))
EDGE_LIB.add(["MLONGNAME"], deck("MBGEN", "MOUTF,SK1,1", "MEXIT",
                                 ("SK1", "MBSKL"), "NINE,/4/", "MEGEN"))
EDGE_IN = [
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


ERRORS = [
    # (name, code, library, cards, does smac.py raise too?)
    ("1 continuation on a SMAC statement", 1, MCP, [card("", "MRD,A,"), "*        B"], False),
    ("2 inner macro", 2,
     err_lib("MBGEN", "MOUTF,SK,1", "MEXIT", ("SK", "MBSKL"), "MRD,/4/", "MEGEN"),
     [card("", "MBAD,A")], False),
    ("3 /Q/", 3, err_lib("MBGEN", "MOUTF,SK,0", "MEXIT", ("SK", "MBSKL"), "L,/Q/", "MEGEN"),
     [card("", "MBAD")], False),
    ("4 a lone slash", 4, err_lib("MBGEN", "MOUTF,SK,0", "MEXIT", ("SK", "MBSKL"), "L,A/B", "MEGEN"),
     [card("", "MBAD")], True),
    ("5 /n/ past the parameters", 5,
     err_lib("MBGEN", "MOUTF,SK,0", "MEXIT", ("SK", "MBSKL"), "L,/4/", "MEGEN"),
     [card("", "MBAD")], True),
    ("6 a tag overflows columns 2-9", 6,
     err_lib("MBGEN", "MOUTF,SK,0", "MEXIT", ("SK", "MBSKL"), ("/2/X", "L,A"), "MEGEN"),
     [card("EIGHTCHR", "MBAD")], True),
    ("7 MOUTV's N is not whole", 7,
     err_lib("MBGEN", "MOUTV,N,SK,2", "MEXIT", ("SK", "MBSKL"), "L,/1/", "MEGEN"),
     [card("", "MBAD,A,B,C")], True),
    ("8 MOUTF has no skeleton", 8, MCP, [card("", "MEND")], True),
]


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
            build.link_generator(build.compile_generator(g, q))
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
        edge_want = smac.expand(EDGE_LIB, "\n".join(EDGE_IN))
        edge_lib = smac.Library()
        for op in ("MRD", "MEOJ", "MSCR", "MFETCH", "MABEX", "MEND", "MEDGE", "MLONGNAME"):
            edge_lib.gens[op] = EDGE_LIB.gens[op]
        edge_want = smac.expand(edge_lib, "\n".join(EDGE_IN))
        jobs["C"] = ("StretchSmac7030CTb", edge_lib, EDGE_IN, len(edge_want) + 5)
        for i, (name, code, lib, cards, raises) in enumerate(ERRORS):
            small = smac.Library()
            for op in lib.gens:
                if op in ("MRD", "MEND", "MBAD"):
                    small.gens[op] = lib.gens[op]
            jobs[f"D{code}"] = (f"StretchSmac7030D{code}Tb", small, cards, 5)
        with ThreadPoolExecutor(4) as ex:
            res = dict(zip(jobs, ex.map(lambda j: run_7030(*j, tmp), jobs.values())))

        h, qe, got, note = res["B"]
        result(h == "HALT" and qe == 0, f"B: bulletin examples end with QERR {qe} ({h})")
        compare("B: J28-6128 pp.8-12, hand-written cards", got, BUL_WANT, note)
        result(smac.expand(BUL, "\n".join(BUL_IN)) == [c.rstrip() for c in BUL_WANT],
               "B: smac.py gives the same hand-written cards")
        h, qe, got, note = res["C"]
        result(h == "HALT" and qe == 0, f"C: edge cases end with QERR {qe} ({h})")
        compare("C: edge cases against smac.py", got, edge_want, note)

        for name, code, lib, cards, raises in ERRORS:
            h, qe, got, note = res[f"D{code}"]
            result(h == "HALT" and qe == code, f"D: {name} halts with code {code} (got {qe}, {h})")
            try:
                smac.expand(lib, "\n".join(cards))
                host = False
            except smac.SmacError:
                host = True
            result(host == raises,
                   f"D: {name}: smac.py {'raises' if raises else 'expands it (a limit of this version)'}")
    print(f"{'ALL CHECKS PASSED' if not fails else str(fails) + ' CHECK(S) FAILED'}")
    return 1 if fails else 0


sys.exit(main())
