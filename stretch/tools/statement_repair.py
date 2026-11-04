#!/usr/bin/env python3
"""Repair Vision's NAME+STATEMENT draft with what STRAP and the corpus know.

    python3 tools/statement_repair.py --score     # leave-one-page-out

A draft line ("KKUSTM LV.8,SMARK", "SV,$9,0.01$91") becomes a CANDIDATE
DECK CARD -- label and statement in the decks' space-free spelling --
by three kinds of repair, each one a constraint, not a guess at meaning:

  SYNTAX   STRAP's operand grammar: an unmatched ")" after "1$" was a
           "(" ("0.01$9)" -> "0.0($9)"); "[" "{" are "("; "]" "}" are
           ")"; "$O" is "$0"; a mnemonic is never followed by "." (it
           was ","); "SYM.22" is not STRAP, so "SYMT.22" was "SYM+.22";
           a token that starts like a number is one ("0.C" -> "0.0").
  OPCODE   the statement's mnemonic must be one the corpus uses; a
           mnemonic one look-alike away from exactly ONE known mnemonic
           is snapped to it ("CN1111" -> "CM1111").
  SYMBOL   an operand one look-alike away from exactly ONE symbol known
           from OTHER pages is snapped to it.  82% of the symbols a page
           uses are defined or SYN'd on another landed page (3,687 of
           4,490).  Scoring is leave-one-page-out, so a page never
           repairs itself with its own symbols.

LOOK-ALIKES are the pairs measured to confuse on this drum: 0/O/C/D/Q,
1/I/L, 8/B, 5/S, 2/Z, M/N, U/V, 6/G.

STILL A DRAFT.  A repaired card is checked the only way that counts:
assembled, against the BINARY the two engines read (rule 3).  The
repair raises how often that first assembly is already right.
"""
import collections
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "strap"))
import listing_read as R     # noqa: E402
import listing_truth          # noqa: E402

LOOK = [set("0OCDQ"), set("1IL"), set("8B"), set("5S"), set("2Z"), set("MN"), set("UV"), set("6G")]
LOOKALIKE = {}
for grp in LOOK:
    for ch in grp:
        LOOKALIKE.setdefault(ch, set()).update(grp - {ch})
SEP = re.compile(r"([,()+\-*/=])")
TEXT_OPS = ("DD", "(IQS", "(A*)", "(A8", "(IQS*)")   # character data: never repaired


def one_lookalike(a, b, most=1):
    """a and b are equal but for 1..most look-alike substitutions."""
    if len(a) != len(b) or a == b:
        return False
    d = [(x, y) for x, y in zip(a, b) if x != y]
    return len(d) <= most and all(y in LOOKALIKE.get(x, ()) for x, y in d)


DIGIT = str.maketrans({"O": "0", "C": "0", "D": "0", "Q": "0", "I": "1", "L": "1"})


def numeric(tok):
    """A token that starts like a number is a number: letters in it are
    look-alikes of digits ("0.C" -> "0.0", "O.0" -> "0.0")."""
    if re.fullmatch(r"[0-9OCDQIL]*[.][0-9OCDQIL]*|[0-9][0-9OCDQIL]*", tok) and re.search(r"[0-9.]", tok):
        return tok.translate(DIGIT)
    return tok


def corpus():
    """{page: (labels-and-SYNs, mnemonics)} from the landed decks' cards."""
    out = {}
    for f in glob.glob(os.path.join(ROOT, "decks", "mcp_bootstrap_p*.strap")):
        m = re.search(r"_p(\d+)\.strap$", f)
        if not m:
            continue
        syms, ops = set(), set()
        for ln in open(f, errors="replace"):
            if ln.startswith("!") or not ln.strip():
                continue
            code = ln.split("!")[0].rstrip()
            if not code.strip():
                continue
            if not code[0].isspace():
                syms.add(code.split()[0])
                code = code.split(None, 1)[1] if len(code.split(None, 1)) > 1 else ""
            mm = re.match(r"\s*([A-Z][A-Z0-9+\-]*)", code)
            if mm:
                ops.add(mm.group(1))
        out[int(m.group(1))] = (syms, ops)
    return out


def snap(tok, known, most=1):
    tok = numeric(tok)
    if tok in ("Q", "O") and tok not in known:
        return "0"
    if tok in known or not re.match(r"[A-Z5]", tok):
        return tok
    c = [k for k in known if one_lookalike(tok, k, most)]
    return c[0] if len(c) == 1 else tok


def repair(draft, syms, ops, name=None, whole=False):
    """(label, statement), space-free, from one line's draft.

    With `name` given, `draft` is the STATEMENT column alone (split by
    column, strap/listing_read.py text_fields) and no guess is made about
    where the statement starts -- the guess took a NAME fragment "K" for
    the mnemonic K."""
    if name is not None:
        lab, _ = ("", "")
        nm = re.sub(r"\s+", "", R.printer_charset(name)).replace("_", "")
        nm = snap(nm, syms, most=2) if nm else ""
        _, st = repair(draft, syms, ops, whole=True) if draft else ("", "")
        return nm, st
    t = R.printer_charset(draft)
    t = re.split(r"\s[-=]", t)[0].strip()               # the remark
    t = t.translate(str.maketrans({"[": "(", "{": "(", "]": ")", "}": ")"}))
    words = t.split()
    # the statement starts at the first word that begins with a mnemonic
    # (or at the first word, when the text is the STATEMENT column alone)
    start = 0 if whole and words else None
    lead = {"2": "Z", "5": "S", "8": "B", "0": "O", "1": "I", "6": "G"}
    for i, w in enumerate(words if start is None else words[:1]):
        if w[:1] in lead and re.match(r"\d[A-Z0-9+\-]*[,(.]", w):
            w = words[i] = lead[w[0]] + w[1:]      # "2,0.0" is "Z,0.0"
        head = re.match(r"([A-Z(][A-Z0-9+\-*()]*?)(?=[,(.]|$)", w)
        if head and (head.group(1) in ops or any(one_lookalike(head.group(1), o) for o in ops)
                     or w.startswith(TEXT_OPS)):
            start = i
            break
        if whole:
            start = 0
            break
    if start is None:
        return "", re.sub(r"\s+", "", t)
    label = "".join(words[:start])
    stmt = "".join(words[start:])
    if stmt.startswith(TEXT_OPS) or "DD(" in stmt[:4]:
        return snap(label, syms) if label else "", stmt
    stmt = re.sub(r"\$O\b", "$0", stmt).replace("_", "")
    # "+" read as "T" between a symbol and a bit offset (SCCW+.22 read
    # SCCHT.22): "SYM.22" is not STRAP, "SYM+.22" is
    stmt = re.sub(r"([A-Z0-9])T(\.\d)", r"\1+\2", stmt)
    stmt = stmt.replace("(8U", "(BU")              # BU's B read 8
    # "($9)" read "1$91": both parentheses lost to 1s, at the end
    stmt = re.sub(r"[1IL]\$(\d+)[1IL]$", r"($\1)", stmt)
    # an unmatched ")" after a "1$" / "I$": that 1 was the "("
    while stmt.count(")") > stmt.count("(") and re.search(r"[1IL]\$\d+\)", stmt):
        stmt = re.sub(r"[1IL](\$\d+\))", r"(\1", stmt, count=1)
    m = re.match(r"([A-Z][A-Z0-9+\-]*)(.*)$", stmt)
    if m:
        op, rest = m.group(1), m.group(2)
        if rest.startswith("."):          # a mnemonic is never followed by "."
            rest = "," + rest[1:]
        if op not in ops:
            # a mnemonic may carry several look-alikes: CMIIII, CMOCO0
            c = [o for o in ops if one_lookalike(op, o, most=4)]
            op = c[0] if len(c) == 1 else op
        parts = SEP.split(rest)
        rest = "".join(snap(p, syms) if not SEP.fullmatch(p) else p for p in parts)
        stmt = op + rest
    return (snap(label, syms) if label else ""), stmt


_LAB = re.compile(r"^([A-Z][A-Z0-9]*)\s+(\S.*?)\s*!\s*line\s+(\d+)\b")


def labels_of(page):
    """{line: label} for cards that carry one, SYN stand-ins excluded.
    Only pp.100+ decks keep the printed name (spaces removed); earlier
    decks prefix their own (printed "S ROOF" is XSROOF)."""
    out = {}
    f = os.path.join(ROOT, "decks", "mcp_bootstrap_p%d.strap" % page)
    if not os.path.exists(f):
        return out
    for ln in open(f, errors="replace"):
        m = _LAB.match(ln)
        if m and not m.group(2).startswith("SYN"):
            out.setdefault(int(m.group(3)), m.group(1))
    return out


def _norm(s):
    return re.sub(r"\s+", "", s)


def score(quiet=False):
    """Counter(n, raw, repaired, repaired_suffix), leave-one-page-out."""
    import csv
    C = corpus()
    reading = collections.defaultdict(dict)
    for r in csv.DictReader(open(os.path.join(ROOT, "docs", "vision", "listing_reading.tsv")),
                            delimiter="\t", quoting=csv.QUOTE_NONE):
        if r["vol"] == "1" and r["printed"]:
            reading[int(r["printed"])][int(r["line"])] = r
    c = collections.Counter()
    for page in sorted(C):
        others_s = set().union(*(s for p, (s, _) in C.items() if p != page))
        others_o = set().union(*(o for p, (_, o) in C.items() if p != page))
        labels = labels_of(page)
        for line, want in listing_truth.statements(page).items():
            r = reading[page].get(line, {})
            draft = r.get("name_statement_draft", "")
            c["n"] += 1
            w = _norm(re.split(r"\s-", want)[0])
            raw = _norm(re.split(r"\s-", R.printer_charset(draft))[0])
            c["raw"] += raw.endswith(w) and bool(raw)
            _, stmt = repair(draft, others_s, others_o)
            c["repaired"] += stmt == w
            c["repaired_suffix"] += bool(stmt) and stmt.endswith(w)
            _, st2 = repair(r.get("statement_draft", ""), others_s, others_o, whole=True)
            c["split"] += st2 == w
            _, st3 = repair(r.get("statement_crop", ""), others_s, others_o, whole=True)
            c["split_crop"] += st3 == w
            c["split_either"] += w in (st2, st3)
            if page >= 100 and line in labels:
                c["ln"] += 1
                nm, _ = repair("", others_s, others_o, name=r.get("name_draft", ""))
                c["label"] += nm == labels[line]
    if quiet:
        return c
    n = c["n"]
    print(f"{n} lines with a deck statement, leave-one-page-out")
    print(f"  raw draft ends with the statement      {c['raw']:5d}  {100 * c['raw'] / n:.1f}%")
    print(f"  repaired statement EQUALS it           {c['repaired']:5d}  {100 * c['repaired'] / n:.1f}%")
    print(f"  repaired statement ends with it        {c['repaired_suffix']:5d}  {100 * c['repaired_suffix'] / n:.1f}%")
    print(f"  SPLIT BY COLUMN, whole page, EQUALS    {c['split']:5d}  {100 * c['split'] / n:.1f}%")
    print(f"  SPLIT BY COLUMN, text crop, EQUALS     {c['split_crop']:5d}  {100 * c['split_crop'] / n:.1f}%")
    print(f"  either source equals                   {c['split_either']:5d}  {100 * c['split_either'] / n:.1f}%")
    print(f"  LABEL (pp.100+, crop NAME column)      {c['label']:5d} of {c['ln']}  {100 * c['label'] / max(1, c['ln']):.1f}%")
    return c


if __name__ == "__main__":
    if sys.argv[1:] == ["--score"]:
        score()
