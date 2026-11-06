#!/usr/bin/env python3
"""MCP's own error list, printed p.444, against the decks -- both ways.

The assembly that printed MCP ended with its diagnostics, printed p.444
(MCP_Mar63_250-445.pdf PDF p.194), eight rows:

    PAGE  15, LINE 15, FIELD 1 -- MORE THAN 1 LOC.CTR.DEP. SYMBOL 123
    PAGE  37, LINE  9, FIELD 1 -- MORE THAN 1 LOC.CTR.DEP. SYMBOL 123
    PAGE 156, LINE 28, FIELD 1 -- INDEX NOT ALLOWED              115
    PAGE 195, LINE 44, FIELD 1 -- INDEX NOT ALLOWED              115
    PAGE 103, LINE  7, FIELD 1 -- MORE THAN 1 LOC.CTR.DEP. SYMBOL 123
    PAGE 356, LINE 42, ------- -- NO MODE                         92
    PAGE 363, LINE 33, ------- -- DR OR DD WITHOUT DDS            46
    PAGE 364, LINE 48, ------- -- FIELD LENGTH GREATER THAN 64    36

The numbers and wording are N28-1081's diagnostic list (bound in
C28-6129, PDF pp.71-73).  N28-1081 is the APRIL 1963 newsletter and
this listing is MARCH 1963 (see docs/NEXT.md's dating trap), so the
newsletter is not the witness here: the listing itself prints these
five numbers with these words, which is what says the numbering was
already in use.  PAGE and LINE are the printed page and line:
each of the eight lines prints its line number "15**", "28**", where
every other line prints one "*" -- IBM's per-line error flag, seen on
all eight at 300 dpi.

It is the WHOLE assembly's list, so it says two things: these eight
cards drew these diagnostics, and NO OTHER CARD drew any of them.  The
check predicts the rows from every landed deck and compares the sets.

  115  strap_asm itself: an index on an XW VALUE or a CW ADDRESS is
       ignored and recorded (strap_asm._strip_index; the decks for
       printed pp.156 and 195 used to drop the printed "($12)").
  123  a card that is not a SYN, whose FIELD 1 names two or more
       location-counter-dependent symbols (a storage label, a SYN to
       "$" or to an expression naming one, or a name the decks know
       only as a stand-in).  The listing's own scope: printed p.2's
       "CW(CR),X IPL BS,X BS END-X IPL BS,1" has the difference in
       FIELD 2 and printed p.13's "SYN, 1.0 + X BS END - X IPL BS" is
       a SYN, and neither is on the list.
   46  a DR, DRZ or DD with no dds.
   36  a DD, DR or DRZ whose dds field length is over 64.
   92  an E+I/E-I/E+AI/E-AI with no dds (one witness; the U default it
       takes is C28-6129 printed p.46, tests/check_listing_field_rules).

Pages that are not landed -- volume 1 printed pp.1, 5-12 and the
missing printed p.329 -- can hold none of the eight rows, and could
hold a card the rules would flag; the list says they hold none.

MEASURED INJECTIONS (python3 check_error_list.py --inject):
    control                                   PASS
    p.156 and p.195 without "($12)" again     FAIL rows_match_the_list
                                              (two 115 rows missing)
    "($12)" added to p.195 line 40's CW       FAIL rows_match_the_list
                                              (one 115 row extra)
    123's SYN exemption removed               FAIL (p.13 extra)
    123 counted in every field                FAIL (p.2 extra)
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
from strap_asm import assemble, iter_statements           # noqa: E402

DECKS = os.path.join(HERE, "..", "decks")
LISTED = {
    (15, 15, 123), (37, 9, 123), (156, 28, 115), (195, 44, 115),
    (103, 7, 123), (356, 42, 92), (363, 33, 46), (364, 48, 36),
}
STANDIN = re.compile(r'^\(8\)[0-7]+(\.[0-7]*)?$')
NAME = re.compile(r'(?<![0-9.$])[A-Z][A-Z0-9]*')
HERE_SYM = re.compile(r'(^|[^A-Z0-9$])\$($|[^A-Z0-9])')
LINE = re.compile(r'!\s*line\s+(\d+)')
EPLUSI = {"E+I", "E-I", "E+AI", "E-AI"}


def deck_pages(edits=()):
    out = {}
    for f in glob.glob(os.path.join(DECKS, "mcp_bootstrap_p*.strap")):
        m = re.search(r"_p(\d+)\.strap$", f)
        if m:
            out[int(m.group(1))] = open(f).read()
    for page, old, new in edits:
        assert out[page].count(old) == 1, (page, old)
        out[page] = out[page].replace(old, new)
    return out


def printed_line(src, lineno):
    m = LINE.search(src.splitlines()[lineno - 1])
    return int(m.group(1)) if m else None


def location_dependent(pages, rng):
    """The names that are location-counter dependent in printed pages rng."""
    places, syns, standins = set(), {}, set()
    for p in rng:
        for st in iter_statements(pages.get(p, "")):
            n = (st.name or "").upper()
            if not n:
                continue
            f = [x.replace(" ", "") for x in st.fields]
            if st.op.upper() != "SYN":
                places.add(n)
            elif len(f) == 1 and STANDIN.match(f[0]):
                standins.add(n)
            else:
                syns[n] = ",".join(f).upper()
    lcd = places | (standins - set(syns))
    changed = True
    while changed:
        changed = False
        for n, e in syns.items():
            if n not in lcd and (any(t in lcd for t in NAME.findall(e))
                                 or HERE_SYM.search(e)):
                lcd.add(n)
                changed = True
    return lcd


def predicted(pages, syn_exempt=True, field1_only=True):
    rows = set()
    lcd = {p: s for rng in (range(2, 99), range(99, 440))
           for s in [location_dependent(pages, rng)] for p in rng}
    for p, src in sorted(pages.items()):
        for d in assemble(src).diagnostics:
            rows.add((p, printed_line(src, d[0]), d[1]))
        for st in iter_statements(src):
            op = st.op.upper().lstrip("$")
            if op == "END":
                continue
            line = printed_line(src, st.lineno)
            fields = st.fields if not field1_only else st.fields[:1]
            if not (syn_exempt and op == "SYN"):
                for fld in fields:
                    toks = [t for t in NAME.findall(fld.replace(" ", "").upper())
                            if t in lcd.get(p, ())]
                    if len(toks) >= 2:
                        rows.add((p, line, 123))
            dds = (st.mods[0].split(",") if st.mods else [])
            if op in ("DR", "DRZ", "DD") and not st.mods:
                rows.add((p, line, 46))
            if (op in ("DR", "DRZ", "DD") and len(dds) > 1
                    and dds[1].strip().isdigit() and int(dds[1]) > 64):
                rows.add((p, line, 36))
            if op in EPLUSI and not st.mods:
                rows.add((p, line, 92))
    return rows


def main(edits=(), **kw):
    got = predicted(deck_pages(edits), **kw)
    for r in sorted(got - LISTED):
        print(f"     printed p.{r[0]} line {r[1]} draws {r[2]}, not on printed p.444")
    for r in sorted(LISTED - got):
        print(f"     printed p.444 lists p.{r[0]} line {r[1]} {r[2]}, which no deck draws")
    ok = got == LISTED
    print(f"{'PASS' if ok else 'FAIL'} rows_match_the_list = {len(got)} rows"
          + ("" if ok else f", expected the {len(LISTED)} printed"))
    print("ALL TESTS PASSED" if ok else "1 TEST(S) FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    if sys.argv[1:] == ["--inject"]:
        res = [("control", main())]
        print('-- injected: p.156 and p.195 without "($12)" again')
        res.append(("noindex", main(edits=[
            (156, "ELABCW  XW,SSCRPM($12),1,$", "ELABCW  XW,SSCRPM,1,$     "),
            (195, "        CW,SSCRPM($12),1.0           ! line 44",
                  "        CW,SSCRPM,1.0                ! line 44")])))
        print('-- injected: "($12)" added to p.195 line 40\'s CW')
        res.append(("extra", main(edits=[
            (195, "        CW,$+1.0,1.0                 ! line 40",
                  "        CW,$+1.0($12),1.0            ! line 40")])))
        print("-- injected: 123's SYN exemption removed")
        res.append(("syn", main(syn_exempt=False)))
        print("-- injected: 123 counted in every field")
        res.append(("fields", main(field1_only=False)))
        print("INJECTIONS: " + ", ".join(f"{n} -> {'FAIL' if r else 'PASS'}" for n, r in res))
    else:
        sys.exit(main())
