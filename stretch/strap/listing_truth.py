#!/usr/bin/env python3
"""What a landed MCP deck ASSERTS about its printed page, keyed by LINE.

Two places hold it, and a reader of either alone sees about half the
corpus:

  * `!CHECK LOC | PRINTED | line N ...` inside decks/mcp_bootstrap_pNN.strap
    -- every deck from about printed p.83 on;
  * `ROWS = [("LOC", "PRINTED", "line N ..."), ...]` inside
    tests/verify_mcp_bootstrap_pNN.py -- the 75 early decks, and the
    two-page files p5_p6 and p7_p8, whose rows say "p.N line M".

UNCOVERED, said out loud (measured 2026-11-03, printed pp.3-196): 19
pages carry no line-keyed row -- 9-12 (message text; rows name the
label, not the line), 47 59 60 81 82 100, and 99 101 102 104-109
(prose annotations, no !CHECK).  175 pages, 6,039 lines are covered.

The first cross-check against macOS Vision read only the deck files,
and reported 1,012 "unpaired" rows that were the early decks' rows
sitting in their test files.  Reach, not data.

Keyed by LINE NUMBER because pairing a reading to the truth by VALUE
fails on this listing: adjacent locations routinely differ in one or
two characters (221515.00, 221515.40), so a missing row pairs a
location with its neighbour and reports a disagreement that is not
there.  The line number is printed in its own column and is the join.
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

OCT = r"[0-7]{6}\.[0-7]{2}"
_CHK = re.compile(r"^!CHECK\s+(" + OCT + r")\s*\|\s*([^|]*)\|\s*line\s+(\d+)")
_ROW = re.compile(r'\(\s*"(' + OCT + r')"\s*,\s*"([^"]*)"\s*,\s*"(?:p\.(\d+)\s+)?line\s+(\d+)')
_MULTI = re.compile(r"verify_mcp_bootstrap_p(\d+)_p(\d+)\.py$")


def _first_octal(printed):
    t = printed.split()
    return t[0] if t and re.fullmatch(OCT, t[0]) else None


def truth(page, root=ROOT):
    """{line: (location, binary_half1_octal_or_None)} for one printed page."""
    out = {}
    deck = os.path.join(root, "decks", "mcp_bootstrap_p%d.strap" % page)
    if os.path.exists(deck):
        for ln in open(deck, errors="replace"):
            m = _CHK.match(ln.strip())
            if m:
                out.setdefault(int(m.group(3)), (m.group(1), _first_octal(m.group(2))))
    for ver in _verify_files(page, root):
        multi = _MULTI.search(ver) is not None
        for m in _ROW.finditer(open(ver, errors="replace").read()):
            # A two-page file names the page in each row ("p.5 line 5");
            # a row that does not name it cannot be placed, so it is skipped.
            if multi and (m.group(3) is None or int(m.group(3)) != page):
                continue
            out.setdefault(int(m.group(4)), (m.group(1), _first_octal(m.group(2))))
    return out


def _verify_files(page, root):
    tests = os.path.join(root, "tests")
    one = os.path.join(tests, "verify_mcp_bootstrap_p%d.py" % page)
    out = [one] if os.path.exists(one) else []
    for f in sorted(os.listdir(tests)):
        m = _MULTI.search(f)
        if m and int(m.group(1)) <= page <= int(m.group(2)):
            out.append(os.path.join(tests, f))
    return out
