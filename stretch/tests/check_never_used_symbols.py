#!/usr/bin/env python3
"""The assembler's own "SYMBOLS NEVER USED IN PROGRAM", MCP printed
pp.440-443, checked against the decks.

The last pages of the MCP listing are not code.  printed pp.440-443
(MCP_Mar63_250-445.pdf PDF pp.190-193) list every symbol the
assembly defined and never referenced, with its value -- 187 names,
transcribed in tests/mcp_never_used_symbols.tsv.  That is an oracle
from outside every page: the value was printed by IBM's assembler, not
read off the page that defines the symbol, so a deck can agree with
its own page and still be caught here.

TWO QUESTIONS PER ROW.

  value_as_printed   the deck that DEFINES the symbol (a storage card,
                     or a SYN that is not an "(8)..." stand-in) gives
                     the printed value.  Rows marked "* 1" are looked
                     up in volume 1 printed pp.2-98, the TAIL,(2)G
                     block, and the rest in pp.99 on, because the two
                     assemblies define some names twice (TIPL3 is
                     004164.40 in the bootstrap and 021464.40 in $EOJ;
                     the list prints both).
  never_referenced   no statement in that range names the symbol
                     outside its own definition.

AN INTEGER SYN PRINTS AS ZERO.  Two rows print 000000.00 for symbols
SYN'd to a number with no point: ACRD (printed p.210 line 4
"ACRD SYN,10") and XEEEOP (printed p.13 line 28 "XEEEOP SYN(BU,5),
(2)00110").  Every symbol written in point notation prints its
address: SIODK "SYN(BU,12), 1.06" prints 000001.06, PCLK "SYN,0.45"
prints 000000.55, DSIT "SYN, 36.0" prints 000044.00.  The list prints
an address column, and an integer is not an address (C22-6578 printed
p.64 A4.8.2(c) separates the two kinds).  That is the listing's own
behaviour with two witnesses, not a stated rule; it decides only what
this table prints, not what the assembler does with the integer.

NOT REACHABLE: UNUSE1 and UNUSE2 are IOD cards from the IOD listing at
the front of volume 1 (PDF p.8 lines 2 and 9, "UNUSE1 IOD,NOT USED,0,
PULL THIS CARD BEFORE UPDATING"; printed 000002.00 and 000007.00).  No deck assembles an IOD card; the check
counts them as unreachable by name, so a third unreachable row fails.

THE SPELLINGS.  Fourteen printed names differ from the decks' only by
the drum's known wear (B->E, T->I, P->F, open O, 0/O, 1/I), and the
table's note says which.  One went the other way: p.442's YSFLOR
prints a CLOSED O, and printed p.134's label had been read YSFLCR
from an open glyph with no outside witness; the deck now spells it
YSFLOR.

AND THE OTHER DIRECTION.  unlisted_unused_are_explained: every name a
deck defines, never names and never stands in for must be on the list.
Volume 1's TAIL block and the body are landed, so that is checkable,
and it holds but for sixteen names, each kept in ABSENT with why:

  * seven LOADER labels on printed pp.328, 330 and 331 (AOCT4A,
    AOCTH2, ADCRD1, ADCRD2, APCRD5, AERR6, AERR7).  The list says they
    are used, no landed card names them, and printed p.329 -- the
    LOADER's 235112.00-235153.40, between them -- is missing from the
    scan.  The list is the evidence that p.329 names them.  APT168
    (p.291, a LOADER constant) likely the same; not established;
  * JCFIX, named by the IOD card "JCIOD IOD,CONSOLE,JCFIX,CONS1"
    (volume 1 PDF p.8 line 10), which no deck assembles;
  * seven volume-1 names (X9A1, X105, XIO1A, XIOAA, X322, X323A, TG),
    whose references can only be on printed pp.1 and 5-12, not landed.

A label naming itself is a use: "YMCPHP BD,YMCPHP" (p.133), "PK2
XW,2.0,2,PK2" (p.293), "XIN BE,XINEND-XIN" (p.15) and three more are
off the list, which is how the rule was found.

MEASURED INJECTIONS (python3 check_never_used_symbols.py --inject):
    control                                   PASS
    the integer-prints-as-zero rule removed   FAIL value_as_printed 2
                                              (ACRD, XEEEOP)
    p.134 back to "YSFLCR"                    FAIL value_as_printed 1
                                              (YSFLOR undefined)
    p.432's TMREJ6 one half word on           FAIL value_as_printed 1
    p.324's ALDA5 named by a new SYN          FAIL never_referenced 1 (and
                                              unlisted_unused_are_explained:
                                              the new QQQQQ is unused)
    the ALDA5 row dropped from the table      FAIL unlisted_unused_are_explained
    a self-reference no longer a use          FAIL unlisted_unused_are_explained
"""
import collections
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
from strap_asm import assemble, iter_statements           # noqa: E402

DECKS = os.path.join(HERE, "..", "decks")
TABLE = os.path.join(HERE, "mcp_never_used_symbols.tsv")
UNREACHABLE = {"UNUSE1", "UNUSE2"}
# Defined, never named in the decks, and still not on the list: the
# reference is on a card no deck holds.
P329 = ("printed p.329, the LOADER's 235112.00-235153.40, is missing from "
        "the scan; it is the only LOADER code not landed")
VOL1 = ("volume 1 printed pp.1 and 5-12 are not landed")
ABSENT = {
    "AOCT4A": P329, "AOCTH2": P329, "ADCRD1": P329, "ADCRD2": P329,
    "APCRD5": P329, "AERR6": P329, "AERR7": P329,
    "APT168": "printed p.291 line 25, a LOADER constant in the resident "
              "part; most likely p.329 too, not established",
    "JCFIX": "printed p.295 line 35; the IOD card \"JCIOD IOD,CONSOLE,"
             "JCFIX,CONS1\" (volume 1 PDF p.8 line 10) names it",
    "X9A1": VOL1, "X105": VOL1, "XIO1A": VOL1, "XIOAA": VOL1,
    "X322": VOL1, "X323A": VOL1, "TG": VOL1,
}
SELF_USE = True
STANDIN = re.compile(r'^\(8\)[0-7]+(\.[0-7]*)?$')
INTEGER = re.compile(r'^(\([0-9]+\))?[0-9A-F]+$')
NAME = re.compile(r'[A-Z][A-Z0-9]*')


def fmt(v):
    return f"{v >> 6:06o}.{v & 63:02o}"


def table():
    rows = []
    for ln in open(TABLE):
        if ln.startswith("#") or ln.startswith("page\t"):
            continue
        page, row, printed, name, tail, value, note = ln.rstrip("\n").split("\t")
        rows.append((int(page), int(row), name, tail == "*1", value))
    return rows


def deck_pages(edit=None):
    """{printed page: source}, with an optional (page, old, new) edit."""
    out = {}
    for f in glob.glob(os.path.join(DECKS, "mcp_bootstrap_p*.strap")):
        m = re.search(r"_p(\d+)\.strap$", f)
        if m:
            out[int(m.group(1))] = open(f).read()
    if edit:
        page, old, new = edit
        assert out[page].count(old) == 1, (page, old)
        out[page] = out[page].replace(old, new)
    return out


def scan(src, wanted):
    """One deck: (defs, labels, standins, uses).  defs maps each wanted
    name the deck DEFINES (not by an "(8)..." stand-in) to (value,
    integer-SYN?); labels is every name it defines that way; uses is
    every name a statement names, its own label included -- "YMCPHP
    BD,YMCPHP" (printed p.133 line 9) is a use, and the list leaves it
    out."""
    prog = None
    defs, labels, standins, uses = {}, set(), set(), set()
    for st in iter_statements(src):
        name = (st.name or "").upper()
        fields = [f.replace(" ", "") for f in st.fields]
        standin = (st.op.upper() == "SYN" and len(fields) == 1
                   and STANDIN.match(fields[0]))
        if name:
            (standins if standin else labels).add(name)
        if name in wanted and not standin:
            if prog is None:
                prog = assemble(src)
            integer = (st.op.upper() == "SYN" and len(fields) == 1
                       and INTEGER.match(fields[0].upper()) is not None)
            defs[name] = (prog.symtab[name], integer)
        # A deck's closing "END, <name>" is the harness's, not a printed
        # card (printed p.32's deck ends "END, X34" to assemble alone).
        if st.op.upper() == "END":
            continue
        uses.update(t for t in NAME.findall(",".join(fields).upper())
                    if SELF_USE or t != name)
    return defs, labels, standins, uses


def main(edit=None, int_rule=True, drop_row=None):
    fails = 0

    def check(label, got, want):
        nonlocal fails
        ok = got == want
        fails += not ok
        print(f"{'PASS' if ok else 'FAIL'} {label} = {got}"
              + ("" if ok else f" expected {want}"))

    rows = table()
    check("rows_transcribed", len(rows), 187)
    if drop_row:
        rows = [r for r in rows if r[2] != drop_row]
    pages = deck_pages(edit)
    wanted = {r[2] for r in rows}
    found = {t: collections.defaultdict(list) for t in (True, False)}
    used = {t: collections.defaultdict(list) for t in (True, False)}
    labels = {t: {} for t in (True, False)}
    standins = {t: set() for t in (True, False)}
    for p, src in sorted(pages.items()):
        tail = 2 <= p <= 98
        d, lab, sd, u = scan(src, {w for w in wanted if w in src})
        for k, v in d.items():
            found[tail][k].append((p, v))
        for k in lab:
            labels[tail].setdefault(k, p)
        standins[tail] |= sd
        for k in u:
            used[tail][k].append(p)

    bad_value, bad_use, unreachable = [], [], []
    for page, row, name, tail, value in rows:
        if name in UNREACHABLE and not found[tail].get(name):
            unreachable.append(name)
            continue
        got = []
        for p, (v, integer) in found[tail].get(name, []):
            got.append((p, "000000.00" if integer and int_rule else fmt(v)))
        if not any(v == value for p, v in got):
            bad_value.append(f"p.{page} row {row} {name} printed {value}, decks {got or 'none'}")
        if used[tail].get(name):
            bad_use.append(f"p.{page} row {row} {name} named on printed p."
                           + ", ".join(map(str, used[tail][name])))
    for b in bad_value + bad_use:
        print("     " + b)
    check("value_as_printed", len(bad_value), 0)
    check("never_referenced", len(bad_use), 0)
    check("unreachable_are_the_iod_cards", sorted(unreachable), sorted(UNREACHABLE))

    # The other direction: a name the decks define, never name and
    # never stand in for must be on the list -- unless the reference is
    # on a card no deck holds, which ABSENT names, each with its reason.
    listed = {(r[3], r[2]) for r in rows}
    absent = {}
    for tail in (True, False):
        for name, p in labels[tail].items():
            if (not used[tail].get(name) and name not in standins[tail]
                    and (tail, name) not in listed):
                absent[name] = p
    for name in sorted(set(absent) - set(ABSENT)):
        print(f"     {name} (printed p.{absent[name]}) is defined, never named, and not on the list")
    for name in sorted(set(ABSENT) - set(absent)):
        print(f"     {name} was expected off the list and no longer is: {ABSENT[name]}")
    check("unlisted_unused_are_explained", sorted(absent), sorted(ABSENT))
    print("ALL TESTS PASSED" if not fails else f"{fails} TEST(S) FAILED")
    return fails


if __name__ == "__main__":
    if sys.argv[1:] == ["--inject"]:
        res = [("control", main())]
        print("-- injected: the integer-prints-as-zero rule removed")
        res.append(("intrule", main(int_rule=False)))
        print('-- injected: p.134 back to "YSFLCR"')
        res.append(("ysflcr", main(edit=(134, "YSFLOR  SYN,", "YSFLCR  SYN,"))))
        print("-- injected: p.432's TMREJ6 one half word on")
        res.append(("tmrej6", main(edit=(432, "TMREJ6  V+ICR", "        NOP\nTMREJ6  V+ICR"))))
        print("-- injected: p.324's ALDA5 named by a new SYN")
        res.append(("alda5", main(edit=(324, "ALDA5   Z,$3", "ALDA5   Z,$3\nQQQQQ   SYN,ALDA5"))))
        print("-- injected: the ALDA5 row dropped from the table")
        res.append(("droprow", main(drop_row="ALDA5")))
        print("-- injected: a self-reference no longer a use")
        SELF_USE = False
        res.append(("selfuse", main()))
        SELF_USE = True
        print("INJECTIONS: " + ", ".join(f"{n} -> {'FAIL' if r else 'PASS'}" for n, r in res))
    else:
        sys.exit(main())
