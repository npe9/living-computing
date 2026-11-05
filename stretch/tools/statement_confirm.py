#!/usr/bin/env python3
"""Confirm a statement draft by ASSEMBLING it against the binary the engines read.

    python3 tools/statement_confirm.py            # write the table
    python3 tools/statement_confirm.py --score    # against the landed decks

Rule 3's loop, run on the reading itself: for every line whose LOCATION
and BINARY h1 are trusted (agreed, or confirmed by the arithmetic or the
symbol cross-check), each candidate card -- the repaired STATEMENT from
the whole page and from the text crop (tools/statement_repair.py) -- is
assembled by strap/strap_asm.py AT THAT LOCATION, with the symbols it
names SYN'd to where the reading found them defined.  A candidate is

  asm-confirmed  when it assembles to BINARY h1 (and h2, when printed)
                 exactly, and Vision's hex byte, where read, does not
                 contradict the assembled one;
  asm-bound      when it does so only once its symbols are BOUND to
                 definitions it did not spell: each operand symbol the
                 reading does not define is replaced by a look-alike
                 (up to two) that it does, and a name defined at several
                 locations tries each (MCP is several assemblies); bound
                 only when exactly one binding assembles.  The BINARY is
                 as sure as asm-confirmed's (hex 216 of 216 on landed
                 pages) but the SPELLING is the NAME column's reading of
                 the definition, right only 64% of the time
                 (XICCD for XIOCD) -- the symbol's location is what it
                 settles;
  draft          otherwise (the first candidate is kept).

THE HEX BYTE IS NEEDED.  The octal fields alone confirmed `BDS` for
`BDSZ` (hex C2 against C6) and an index read `34` for `$4` (82 against
84).  Vision's hex is compared under its look-alike classes, measured on
5,242 landed bytes: 0/C/D (C0 for 00 212 times, 00 for D0 49) and 8/B
(88 for 8B 18): one byte that differs outside them vetoes.  C against 0
is never settled by the image (tools/README_vision.md), so the
assembler's hex is what the table records.

CONFIRMED MEANS BINARY-EQUIVALENT, not the printed spelling: `$15` for
the printed `$X15` assembles the same.  The table says which binary
the card produces; the spelling is still read off the page (rule 3).

Symbols are those of OTHER landed pages plus the reading's own NAME
column, so a landed page never repairs itself from its deck.
"""
import collections
import csv
import itertools
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "strap"))
sys.path.insert(0, HERE)
import listing_read as R        # noqa: E402
import listing_truth            # noqa: E402
import strap_asm                # noqa: E402
import listing_reading          # noqa: E402
import page_sheet               # noqa: E402
import statement_repair as SR   # noqa: E402

OUT = os.path.join(ROOT, "docs", "vision", "listing_statements.tsv")
TRUST_LOC = ("agreed", "arith-confirmed", "sym-confirmed")
TRUST_BIN = ("agreed", "sym-confirmed")
LOOK = str.maketrans({"C": "0", "D": "0", "B": "8"})


def reading(root=ROOT):
    return list(csv.DictReader(open(os.path.join(root, "docs", "vision", "listing_reading.tsv")),
                               delimiter="\t", quoting=csv.QUOTE_NONE))


SYM = re.compile(r"(?<![A-Z0-9$.])([A-Z][A-Z0-9]*)")


def operands(stmt):
    return sorted(set(SYM.findall(stmt.split(",", 1)[1]))) if "," in stmt else []


def assemble(stmt, loc, defs, binding=None):
    """(h1, hex1, h2, hex2) of `stmt` assembled at bit address `loc`, or None.
    Symbols are SYN'd from `binding` {name: location}, else from `defs`
    when the name has one location."""
    if binding is None:
        binding = {n: next(iter(defs[n])) for n in operands(stmt) if len(defs.get(n, ())) == 1}
    pre = "".join("%-8sSYN, (8)%s\n" % (n, v) for n, v in sorted(binding.items()))
    try:
        p = strap_asm.assemble(pre + "        " + stmt + "\n", origin_bits=loc)
    except Exception:
        return None
    if not p.words:
        return None
    w = min(p.words)
    bits = p.words[w] << 64 | p.words.get(w + 1, 0)
    v = (bits >> (64 - loc % 64)) & ((1 << 64) - 1)
    return ("%06o.%02o" % (v >> 46 & 0o777777, v >> 40 & 0o77), "%02X" % (v >> 32 & 0xFF),
            "%06o.%02o" % (v >> 14 & 0o777777, v >> 8 & 0o77), "%02X" % (v & 0xFF))


class Hex:
    """Vision's hex bytes, one page frame loaded at a time."""
    def __init__(self, root):
        self.root, self.key, self.page = root, None, None

    def __call__(self, r, half):
        k = (r["vol"], r["pdf"])
        if k != self.key:
            stem = os.path.join(self.root, "docs", "vision", "all", "v%s_pdf%03d" % (r["vol"], int(r["pdf"])))
            g = json.loads(open(stem + ".geom").read())
            self.key = k
            self.page = (g, R.load(stem + ".vis.tsv") + R.load(stem + ".vcol.tsv"),
                         R.fit_lines(R.load(stem + ".vis.tsv"), g))
        g, vis, f = self.page
        y0, pitch, _, _ = f
        return page_sheet.hex_after(vis, y0 + (int(r["line"]) - 1) * pitch, pitch,
                                    g["bin_cell"] + 14 * half, g["char_w"])


def bind(stmt, loc, defs, fits):
    """(statement, assembled) for the ONE binding of `stmt`'s symbols to
    read definitions that assembles and fits, or None (see asm-bound)."""
    toks = operands(stmt)
    if not toks or len(toks) > 3:
        return None
    opts = []
    for x in toks:
        vs = [x] if x in defs else [k for k in sorted(defs) if SR.one_lookalike(x, k, 2)][:6]
        opts.append([(v, l) for v in vs for l in sorted(defs[v])][:8])
    if not all(opts):
        return None
    hits = {}
    for combo in itertools.product(*opts):
        s2 = stmt.split(",", 1)
        rest = s2[1]
        for x, (v, _) in zip(toks, combo):
            rest = re.sub(r"(?<![A-Z0-9$.])" + x + r"(?![A-Z0-9])", v, rest)
        s2 = s2[0] + "," + rest
        a = assemble(s2, loc, defs, {v: l for v, l in combo})
        if fits(a):
            hits[s2] = a
            if len(hits) > 1:
                return None
    return next(iter(hits.items())) if hits else None


def confirm(rows, root=ROOT):
    """[(row, status, statement, assembled)] for every line with a draft."""
    defs = collections.defaultdict(set)
    for r in rows:
        nm = listing_reading.name_of({"name": r["name_draft"]})
        if nm and r["loc_status"] in TRUST_LOC:
            defs[nm].add(r["location"])
    C = SR.corpus()
    every_s = set().union(*(s for s, _ in C.values()))
    every_o = set().union(*(o for _, o in C.values()))
    known = {}

    def vocab(page):
        """Symbols and mnemonics of every landed page but this one."""
        if page not in C:
            return every_s | set(defs), every_o
        if page not in known:
            known[page] = (set().union(*(s for q, (s, _) in C.items() if q != page)) | set(defs),
                           set().union(*(o for q, (_, o) in C.items() if q != page)))
        return known[page]

    hexes = Hex(root)
    out = []
    for r in rows:
        page = int(r["printed"]) if r["vol"] == "1" and r["printed"] else None
        syms, ops = vocab(page)
        cands = []
        for src in ("statement_draft", "statement_crop"):
            _, st = SR.repair(r[src], syms, ops, whole=True)
            if st and st not in cands:
                cands.append(st)
        if not cands:
            continue
        got, status = None, "draft"
        if r["loc_status"] in TRUST_LOC and r["bin_status"] in TRUST_BIN:
            loc = R.bit_address(r["location"])

            def fits(a):
                if not a or a[0] != r["binary_h1"] or (r["binary_h2"] and a[2] != r["binary_h2"]):
                    return False
                for half, i in ((0, 1), (1, 3)):
                    if half and not r["binary_h2"]:
                        continue
                    vh = hexes(r, half)
                    if vh and vh.translate(LOOK) != a[i].translate(LOOK):
                        return False
                return True
            for st in cands:
                a = assemble(st, loc, defs)
                if fits(a):
                    got, status = (st, a), "asm-confirmed"
                    break
            if not got:
                got = bind(cands[0], loc, defs, fits)
                status = "asm-bound" if got else "draft"
        if got:
            out.append((r, status, got[0], " ".join(got[1][:2] + (got[1][2:] if r["binary_h2"] else ()))))
        else:
            out.append((r, "draft", cands[0], ""))
    return out


def table(rows, root=ROOT):
    lines = ["vol\tpdf\tprinted\tline\tstatus\tstatement\tassembled\n"]
    for r, st, stmt, a in confirm(rows, root):
        lines.append(f"{r['vol']}\t{r['pdf']}\t{r['printed']}\t{r['line']}\t{st}\t{stmt}\t{a}\n")
    return "".join(lines)


def score(root=ROOT, quiet=False):
    """Counter over landed lines with a deck statement: eligible (trusted
    location and binary), confirmed, text-equal, and hex checked/right."""
    c = collections.Counter()
    want_cache = {}
    tab = list(csv.DictReader(open(OUT if root == ROOT else os.path.join(root, "docs", "vision",
                                                                       "listing_statements.tsv")),
                              delimiter="\t", quoting=csv.QUOTE_NONE))
    rd = {(r["vol"], r["pdf"], r["line"]): r for r in reading(root)}
    for t in tab:
        if t["vol"] != "1" or not t["printed"]:
            continue
        page = int(t["printed"])
        if page not in want_cache:
            want_cache[page] = (listing_truth.statements(page, root), listing_truth.printed(page, root))
        stmts, printed = want_cache[page]
        want = stmts.get(int(t["line"]))
        if not want:
            continue
        r = rd[(t["vol"], t["pdf"], t["line"])]
        c["eligible"] += r["loc_status"] in TRUST_LOC and r["bin_status"] in TRUST_BIN
        if t["status"] not in ("asm-confirmed", "asm-bound"):
            continue
        k = "confirmed" if t["status"] == "asm-confirmed" else "bound"
        c[k] += 1
        c[k + "_text"] += t["statement"] == SR._norm(re.split(r"\s-", want)[0])
        pr = printed.get(int(t["line"]), (None, ""))[1].split()
        a = t["assembled"].split()
        if len(pr) > 1 and re.fullmatch(r"[0-9A-F]{2}", pr[1]):
            c["hex"] += 1
            c["hex_ok"] += a[1] == pr[1]
            if a[1] != pr[1]:
                c.setdefault("bad", []).append((page, t["line"], t["statement"], a[1], pr[1]))
    if not quiet:
        e = max(1, c["eligible"])
        print(f"{c['eligible']} landed lines with a deck statement and a trusted LOCATION + BINARY h1")
        print(f"  asm-confirmed            {c['confirmed']:5d}  {100 * c['confirmed'] / e:.1f}%")
        print(f"  ... text equals the deck {c['confirmed_text']:5d}  "
              f"{100 * c['confirmed_text'] / max(1, c['confirmed']):.1f}%")
        print(f"  asm-bound                {c['bound']:5d}  {100 * c['bound'] / e:.1f}%")
        print(f"  ... text equals the deck {c['bound_text']:5d}  "
              f"{100 * c['bound_text'] / max(1, c['bound']):.1f}%")
        print(f"  ... hex byte equals the deck's printed one: {c['hex_ok']} of {c['hex']}")
    return c


if __name__ == "__main__":
    if sys.argv[1:] == ["--score"]:
        score()
    else:
        open(OUT, "w").write(table(reading()))
        n = collections.Counter(l.split("\t")[4] for l in open(OUT).read().splitlines()[1:])
        print(dict(n))
