#!/usr/bin/env python3
"""check_smac_mcpref_example1.py -- the reconstructed SMAC (strap/smac.py)
with its MCP macro library (strap/smac_mcp.py) on the one SMAC program
IBM printed: C22-6678-1 printed p.47, "PROGRAMMING EXAMPLE 1"
(../decks/mcpref_example1.smac).

FOUR KINDS OF CHECK (D comes before C in the code).
  A. Every card that is not a SMAC statement reaches STRAP exactly as
     punched, in order (34 cards: control, comment and STRAP cards).
  B. Each of the 18 SMAC statements expands to the calling sequence
     C22-6678-1 printed p.14 prescribes.  The expected cards are
     written out below by hand from p.14, not computed by the library.
  C. The expansion, assembled by the scaffolding assembler, gives the
     machine code STRAP II itself printed for the same pseudo-ops on
     C22-6678-1 printed p.48 (VERSION 03/15/64): B,$MCP 000040.10 00,
     $WAIT 000013.40 80, $EOJ 000101.00 80, $ABEOJ 000104.00 80,
     $COMM 000043.40 80, $IODEF 000015.00 80, and the first IOD's
     reference number 000001.00 80 (p.48's ,RON).  $RD (1.0) and $BSP
     (6.0) do not appear on p.48; their values are Appendix A's
     (printed p.42).  This is a cross-document check: SMAC's
     expansion, written to p.14, reproduces what IBM's STRAP II printed
     for p.48's hand-written calling sequences.
  D. The pseudo-ops whose printed expansion departs from p.14 (see
     strap/smac_mcp.py): $SCR (printed p.20), $FETCH (printed p.21),
     and $ABEX in both of its printed forms (printed p.23).

FOR THE SCAFFOLD ONLY, two things are given here that STRAP II would
derive: SUEJEAN SYN 1.0 (the IOD card's name; strap_asm reads no IOD
cards), and the names "MESG 1"/"MESG 2", printed with a blank, are
closed up to MESG1/MESG2, as the statements that refer to them spell
them.  The origin, 000041.00, is p.48's.

PROVEN DISCRIMINATING: the injections and their observed failure sets
are in tests/run_tests.sh beside this test's entry.
"""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
import smac                                                  # noqa: E402
import smac_mcp                                              # noqa: E402
import strap_asm                                             # noqa: E402
from listing_oracle import check_rows, finish                # noqa: E402

DECK = os.path.join(HERE, "..", "decks", "mcpref_example1.smac")
cards = [l.rstrip("\n") for l in open(DECK) if not l.startswith("!")]
out = smac.expand(smac_mcp.library(), "\n".join(cards))
fails = 0


def result(ok, msg):
    global fails
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} {msg}")


# ---- A. non-SMAC cards pass through verbatim, in order ---------------
lib = smac_mcp.library()
plain = []
for c in cards:
    k = smac.Card.parse(c)
    stmt = smac.split_comment(k.var)[0]
    op = smac.split_args(stmt)[0] if stmt.strip() else ""
    if not (k.col1 == "" and not k.tag.startswith("'") and op in lib):
        plain.append(c.rstrip())
it = iter(out)
in_order = all(any(o == p for o in it) for p in plain)
result(len(plain) == 34 and in_order,
       f"A: {len(plain)} non-SMAC cards reach STRAP verbatim and in order")


# ---- B. each SMAC statement -> p.14's calling sequence ---------------
def seq(tag, op, *params):
    head = [(" " + tag.ljust(8) + "B,$MCP").rstrip(), " " * 9 + ",$" + op]
    return head + [" " * 9 + "," + p for p in params]


EXPECT = [
    ("READ    MRD,SUEJEAN,CW1", seq("READ", "RD", "SUEJEAN", "CW1")),
    ("MEOJ", seq("", "EOJ")),
    ("WAIT    MWAIT,SUEJEAN", seq("WAIT", "WAIT", "SUEJEAN")),
    ("MRD,SUEJEAN,CW1", seq("", "RD", "SUEJEAN", "CW1")),
    ("MBSP,SUEJEAN", seq("", "BSP", "SUEJEAN")),
    ("MWAIT,SUEJEAN", seq("", "WAIT", "SUEJEAN")),
    ("MCOMM,MESG1,3.", seq("", "COMM", "MESG1", "3.")),
    ("MABEOJ", seq("", "ABEOJ")),
    ("UNITBAD MIODEF,SUEJEAN,MESG2+2.0", seq("UNITBAD", "IODEF", "SUEJEAN", "MESG2+2.0")),
    ("MCOMM,MESG2,4.", seq("", "COMM", "MESG2", "4.")),
    ("MABEOJ", seq("", "ABEOJ")),
    ("EPGK    MCOMM,MESG3,5.", seq("EPGK", "COMM", "MESG3", "5.")),
    ("MABEOJ", seq("", "ABEOJ")),
    ("MRET", seq("", "RET")), ("MRET", seq("", "RET")),
    ("MRET", seq("", "RET")), ("MRET", seq("", "RET")),
    ("MEND,INIT", [" " * 9 + "END,INIT"]),
]
# walk the output, skipping the pass-through cards, in source order
rest = [o for o in out if o not in plain]
pos = 0
for src, want in EXPECT:
    got = rest[pos:pos + len(want)]
    result(got == want, f"B: {src} -> {' / '.join(w.strip() for w in want)}")
    pos += len(want)
result(pos == len(rest), f"B: nothing else was put out ({len(rest) - pos} extra cards)")

# ---- D. the pseudo-ops whose printed expansion departs from p.14 ------
def exp(stmt):
    return [o.split("'")[0].rstrip() for o in
            smac.expand(lib, (" " + "".ljust(8) + stmt).rstrip())]


I9 = " " * 9
result(exp("MSCR,FWA,N,END") ==
       [I9 + "B,$MCP", I9 + ",$SCR", I9 + ",FWA", I9 + ",N", I9 + ",0.", I9 + "B,END"],
       "D: MSCR,FWA,N,END -> p.20: ,FWA / ,N / ,0. (M.) / B,END")
result(exp("MFETCH,22LOADER,0,BUF,0,ERR,END") ==
       [I9 + "B,$MCP", I9 + ",$FETCH", I9 + "(AX)DD(BU,48,6),22LOADERX", I9 + ",0",
        I9 + ",BUF", I9 + ",0", I9 + ",0.", I9 + "B,ERR", I9 + "B,END"],
       "D: MFETCH -> p.21: (AX)DD(BU,48,6) name, M., B,ERROR, B,END")
result(exp("MABEX") == [I9 + "B,$MCP", I9 + ",$ABEX"] and
       exp("MABEX,TBL") == [I9 + "B,$MCP", I9 + ",$ABEX", I9 + ",TBL"],
       "D: MABEX as printed (bare) and as its expansion implies (,FWA): both kept")
try:
    exp("MSCR,FWA,N")
    ok = False
except smac.SmacError:
    ok = True
result(ok, "D: MSCR without END fails loud (p.20 needs it for the end return)")

# ---- C. assembled, against p.48's printed code -----------------------
sc = smac.to_scaffold(out).replace("MESG 1 ", "MESG1  ").replace("MESG 2 ", "MESG2  ")
try:
    prog = strap_asm.assemble("        SLC, (8)41.0\nSUEJEAN SYN, 1.0\n" + sc)
except strap_asm.AssemblerError as e:
    result(False, f"C: the expansion does not assemble: {e}")
    finish(fails)
MCP, P48 = "000040.10 00", "p.48"
ROWS = [
    ("000041.40", MCP, "READ B,$MCP (p.48)"),
    ("000042.00", "000001.00 80", ",$RD (App. A 1.0)"),
    ("000042.40", "000001.00 80", ",SUEJEAN = p.48's ,RON"),
    ("000043.00", "000100.00 80", ",CW1"),
    ("000045.40", MCP, "MEOJ B,$MCP"),
    ("000046.00", "000101.00 80", ",$EOJ (p.48)"),
    ("000046.40", MCP, "WAIT B,$MCP"),
    ("000047.00", "000013.40 80", ",$WAIT (p.48)"),
    ("000047.40", "000001.00 80", ",SUEJEAN"),
    ("000057.00", MCP, "MBSP B,$MCP"),
    ("000057.40", "000006.00 80", ",$BSP (App. A 6.0)"),
    ("000065.00", "000043.40 80", ",$COMM (p.48)"),
    ("000065.40", "000104.00 80", ",MESG1"),
    ("000066.00", "000003.00 80", ",3. = p.48's ,3.0"),
    ("000067.00", "000104.00 80", ",$ABEOJ (p.48)"),
    ("000067.40", MCP, "UNITBAD B,$MCP"),
    ("000070.00", "000015.00 80", ",$IODEF (p.48)"),
    ("000070.40", "000001.00 80", ",SUEJEAN"),
    ("000071.00", "000112.00 80", ",MESG2+2.0"),
]
SYMBOLS = {"READ": "000041.40", "WAIT": "000046.40", "UNITBAD": "000067.40",
           "EPGK": "000074.40", "CW1": "000100.00", "MESG1": "000104.00",
           "MESG2": "000110.00"}
fails += check_rows(prog, ROWS, SYMBOLS, label="C: ")
finish(fails)
