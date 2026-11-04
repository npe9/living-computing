#!/usr/bin/env python3
"""One reading of the MCP listing's numeric columns, every page, both volumes.

    python3 tools/listing_reading.py            # write the tables
    python3 tools/listing_reading.py --score    # measure each status
                                                # against the landed decks

Reads docs/vision/all/ (tools/read_every_page.py) and writes

  docs/vision/listing_pages.tsv    one row per PDF page: printed page
                                   (from its own header, or inferred from
                                   its neighbours and SAID so), frame
                                   found, line fit, counts by status
  docs/vision/listing_reading.tsv  one row per printed LINE: LOCATION
                                   and BINARY half words 1 and 2 (octal
                                   parts), each with a status

STATUS of a field, from the two engines:

NAME + STATEMENT is a Vision DRAFT only (name_statement_draft): tesseract
reads 8% of statements exactly and is right only 20 of 26 times when it
agrees with Vision, so there is no second engine for text.  Measured
against the decks' source (--score): see tools/README_vision.md.

  agreed          Vision and tesseract read the same value
  conflict        the readings differ -- every value recorded

Vision is read twice, whole page and column crops (.vcol.tsv), but it is
ONE engine: measured, it repeats 50-75% of its own errors across
framings.  So two Vision readings that agree are still `vision-only`;
`agreed` always means tesseract read the same value as Vision.
  vision-only     only Vision read it
  tesseract-only  only tesseract read it
  unread          neither

LOCATION ARITHMETIC (see arithmetic()) adds two statuses for LOCATION:
arith-confirmed and arith-only.  CROSS-PAGE SYMBOLS (see symbols()) add
two for BINARY h1: sym-confirmed and sym-only.

ORDER CHECK, independent of the image: STRAP assigns locations in
order, so an `agreed` location that falls OUTSIDE its two agreed
neighbours, while they are in order with each other, is demoted to
`agreed-out-of-order`.  Measured reason: on a faint 7 both engines read
1 (p.67 line 13, 003777.40 read 003717.40), and agreement alone does not
catch it.  NOT "lower than the line above": that first version flagged
11 correct rows, because an ORG legitimately steps backwards (printed
pp.8, 30) and one bad value then condemned every row after it.

Nothing here is a transcription.  A value of any status is a reading,
to be confirmed by rule 3 (transcribe, assemble, compare) before a deck
lands.  --score says how far each status can be trusted.
"""
import collections
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "strap"))
import listing_read as R      # noqa: E402
import listing_truth          # noqa: E402

ALL = os.path.join(ROOT, "docs", "vision", "all")
PAGES_OUT = os.path.join(ROOT, "docs", "vision", "listing_pages.tsv")
LINES_OUT = os.path.join(ROOT, "docs", "vision", "listing_reading.tsv")


def status(vs, t):
    """vs: Vision's readings (whole page, column crop) -- ONE engine; t: tesseract."""
    vs = sorted({v for v in vs if v})
    if t and t in vs:
        return "agreed", t
    if t and vs:
        return "conflict", "|".join(vs + [t])
    if len(vs) == 2:
        return "conflict", "|".join(vs)
    if vs:
        return "vision-only", vs[0]
    if t:
        return "tesseract-only", t
    return "unread", ""


def read_page(stem):
    vis = R.load(stem + ".vis.tsv")
    tes = R.load(stem + ".tes.tsv")
    vcol = R.load(stem + ".vcol.tsv") if os.path.exists(stem + ".vcol.tsv") else []
    # Vision on the text region alone: it keeps the one-letter fragments
    # that open names ("K K TAPE", read "TAPE" off the whole page) and gets
    # 47% of labels against 32%, but STATEMENTS worse (46.0% against 51.7%
    # repaired) -- so both drafts are kept, each for what it reads best.
    vtext = R.load(stem + ".vtext.tsv") if os.path.exists(stem + ".vtext.tsv") else []
    gl = open(stem + ".geom").read().strip()
    page = {"header": R.page_number(vis), "frame": gl != "none", "fit": False, "lines": {}}
    if gl == "none":
        return page
    g = json.loads(gl)
    if "bin2_x" not in g:         # frames stored before half word 2 was read
        cw = g["char_w"]
        bx = g["bin_cell"] * cw
        g["bin2_x"] = (bx + 12.0 * cw, bx + 17.5 * cw)
    if "text_x" not in g:
        bx = g["bin_cell"] * g["char_w"]
        g["text_x"] = (bx + 28.0 * g["char_w"], bx + 76.5 * g["char_w"])
    f = R.fit_lines(vis, g)
    if f is None:
        return page
    page["fit"] = True
    y0, pitch, _, _ = f
    cw = g["char_w"]
    # the lowest line printed is where the last LOCATION was read
    last = max([round((y - y0) / pitch) + 1 for y, x, t in vis + vcol + tes
                if g["loc_x"][0] <= x <= g["loc_x"][1] and R.groups(x, t, cw)] + [0])
    for line in range(1, min(last, 60) + 1):
        y = y0 + (line - 1) * pitch
        row = {}
        for fld, xw in (("loc", g["loc_x"]), ("bin", g["bin_x"]), ("bin2", g["bin2_x"])):
            row[fld] = status((R.field_at(vis, y, pitch, xw, cw),
                               R.field_at(vcol, y, pitch, xw, cw)),
                              R.field_at(tes, y, pitch, xw, cw))
        row["text"] = R.text_at(vis, y, pitch, g["text_x"])
        row["text_crop"] = R.text_at(vtext, y, pitch, g["text_x"])
        row["name"], _ = R.text_fields(vtext, y, pitch, g)
        _, row["stmt"] = R.text_fields(vis, y, pitch, g)
        _, row["stmt_crop"] = R.text_fields(vtext, y, pitch, g)
        if any(row[k][0] != "unread" for k in ("loc", "bin", "bin2")) or row["text"] or row["text_crop"]:
            page["lines"][line] = row
    # ORDER CHECK on agreed locations: out of order with BOTH agreed
    # neighbours, which are in order with each other
    ag = [(l, R.bit_address(r["loc"][1])) for l, r in sorted(page["lines"].items())
          if r["loc"][0] == "agreed"]
    for i in range(1, len(ag) - 1):
        (_, a), (line, v), (_, b) = ag[i - 1], ag[i], ag[i + 1]
        if a <= b and not a <= v <= b:
            page["lines"][line]["loc"] = ("agreed-out-of-order", page["lines"][line]["loc"][1])
    arithmetic(page["lines"])
    return page


def _length(row):
    """An instruction's length in bits from its printed shape: a full word
    prints half word 2, a half word does not."""
    return 64 if row["bin2"][1] else 32


def arithmetic(lines):
    """LOCATION ARITHMETIC: line n+1's location is line n's plus n's length.

    Measured on the landed pages: 4,966 of 4,988 consecutive instruction
    lines step by exactly their printed length (the 22 that do not are
    half words before a word boundary).  So a location the engines did
    NOT agree on is

      arith-confirmed  when one of its readings equals the prediction from
                       a trusted neighbour (1,440 of 1,440 right on the
                       landed pages);
      arith-only       when nothing was read and a trusted neighbour
                       predicts it (59 of 62 right).

    Trusted = agreed or arith-confirmed.  Predicted forwards from the line
    above and backwards from the line below, repeated until nothing
    changes, so a confirmation can carry along a run of lines."""
    fmt = lambda b: "%06o.%02o" % (b // 64, b % 64)
    trusted = lambda r: r["loc"][0] in ("agreed", "arith-confirmed") and r["bin"][1]
    changed = True
    while changed:
        changed = False
        for n in sorted(lines):
            r = lines[n]
            st, v = r["loc"]
            if st in ("agreed", "agreed-out-of-order", "arith-confirmed", "arith-only"):
                continue
            preds = set()
            a, b = lines.get(n - 1), lines.get(n + 1)
            if a and trusted(a):
                preds.add(fmt(R.bit_address(a["loc"][1]) + _length(a)))
            if b and trusted(b) and r["bin"][1]:
                preds.add(fmt(R.bit_address(b["loc"][1]) - _length(r)))
            vals = v.split("|") if v else []
            hit = [p for p in preds if p in vals]
            if len(hit) == 1:
                r["loc"] = ("arith-confirmed", hit[0])
                changed = True
            elif not vals and len(preds) == 1:
                r["loc"] = ("arith-only", next(iter(preds)))
                changed = True


# an operand that names a symbol, at the head of the statement: OP,SYM,
# OP,SYM+.n, OP,SYM+n.m -- anything after it (index, second field) left out
_REF = re.compile(r"^([A-Z][A-Z0-9+\-]*),([A-Z][A-Z0-9]*)((?:\+?\d*\.\d+|\+\d+(?:\.\d*)?)?)(?=$|[,(])")
_DELTA = {}


def op_delta(op):
    """BINARY h1's 24-bit field minus the bit address of its operand, for
    mnemonic `op`, from the ASSEMBLER (strap/strap_asm.py), never from a fit:
    a half-word branch carries its opcode in bits 19-23 (B +8, BD +4, BXE
    +26, BRZ +28), a bit-addressed or VFL field is the address itself (0).
    None when strap_asm does not take the mnemonic (a misread one)."""
    if op not in _DELTA:
        import strap_asm
        _DELTA[op] = None
        for tail in (",T", ",T,U", ",T\n        B,U"):
            src = "T       SYN, (8)221741.40\nU       SYN, (8)001000.00\n        %s%s\n" % (op, tail)
            try:
                p = strap_asm.assemble(src)
            except Exception:
                continue
            if not p.words:          # a pseudo-op: no binary to predict
                break
            h1, t = p.words[min(p.words)] >> 40, p.symtab["T"]
            _DELTA[op] = (h1 - t) if h1 >> 6 == t >> 6 else None
            break
    return _DELTA[op]


def symbols(pages):
    """CROSS-PAGE SYMBOLS: a BINARY h1 that names a symbol holds that
    symbol's LOCATION, read off the line that DEFINES it -- on any of the
    451 pages.  So a BINARY h1 the engines did not agree on is

      sym-confirmed  when one of its readings equals the prediction from a
                     defining line (NAME column, location agreed or
                     arith-confirmed), plus the operand's offset, plus the
                     mnemonic's opcode bits (op_delta);
      sym-only       when nothing was read and the name has ONE location.

    MCP is several assemblies (GKRUH is 002374 on printed p.42 and 230574
    on p.260), so a name may have several locations: each is a candidate,
    and only a reading that equals exactly one confirms.

    CONFIRM ONLY, never deny: on agreed binaries (100% right on the landed
    pages) 94 of 1,141 predictions disagree -- a symbol look-alike in the
    statement, a misread NAME, a local name reused.  A mismatch says the
    check is wrong far more often than the binary."""
    fmt = lambda b: "%06o.%02o" % (b // 64, b % 64)
    defs = collections.defaultdict(set)
    for p in pages.values():
        for r in p["lines"].values():
            nm = re.sub(r"\s+", "", R.printer_charset(r["name"])).replace("_", "")
            if r["loc"][0] in ("agreed", "arith-confirmed") and re.fullmatch(r"[A-Z][A-Z0-9]{1,7}", nm):
                defs[nm].add(R.bit_address(r["loc"][1]))
    for p in pages.values():
        for r in p["lines"].values():
            st, v = r["bin"]
            if st not in ("conflict", "vision-only", "tesseract-only", "unread"):
                continue
            m = _REF.match(re.split(r"\s[-=]", R.printer_charset(r["stmt"]))[0].replace(" ", ""))
            if not m or m.group(2) not in defs:
                continue
            op, sym, off = m.groups()
            d = op_delta(op)
            if d is None:
                continue
            o = 0
            if off:
                w, _, b = off.lstrip("+").partition(".")
                o = int(w or 0) * 64 + int(b or 0)
            preds = {fmt(a + o + d) for a in defs[sym]}
            vals = v.split("|") if v else []
            hit = [x for x in preds if x in vals]
            if len(hit) == 1:
                r["bin"] = ("sym-confirmed", hit[0])
            elif not vals and len(preds) == 1:
                r["bin"] = ("sym-only", next(iter(preds)))


def infer_printed(pages):
    """Fill unread headers from neighbours when both sides agree on the offset."""
    keys = sorted(pages)
    for i, k in enumerate(keys):
        p = pages[k]
        p["printed"], p["printed_how"] = p["header"], "header" if p["header"] else ""
        if p["header"]:
            continue
        vol, pdf = k
        before = next((pages[j]["header"] - j[1] for j in reversed(keys[:i])
                       if j[0] == vol and pages[j]["header"]), None)
        after = next((pages[j]["header"] - j[1] for j in keys[i + 1:]
                      if j[0] == vol and pages[j]["header"]), None)
        if before is not None and before == after:
            p["printed"], p["printed_how"] = pdf + before, "inferred"
        else:
            p["printed"], p["printed_how"] = None, "unknown"
    return pages


def load_all(all_dir=ALL):
    pages = {}
    for geom in glob.glob(os.path.join(all_dir, "v*_pdf*.geom")):
        m = re.search(r"v(\d)_pdf(\d+)\.geom$", geom)
        if not os.path.exists(geom[:-5] + ".tes.tsv"):
            continue                  # tools/read_every_page.py still writing it
        pages[(int(m.group(1)), int(m.group(2)))] = read_page(geom[:-5])
    symbols(pages)
    return infer_printed(pages)


def tables(pages):
    """(listing_pages.tsv, listing_reading.tsv) as text."""
    a = ["vol\tpdf\tprinted\tprinted_from\tframe\tline_fit\tlines\t"
         "loc_agreed\tloc_other\tbin_agreed\tbin_other\n"]
    b = ["vol\tpdf\tprinted\tline\tlocation\tloc_status\tbinary_h1\tbin_status\t"
         "binary_h2\tbin2_status\tname_statement_draft\tname_statement_crop\t"
         "name_draft\tstatement_draft\tstatement_crop\n"]
    for (vol, pdf), p in sorted(pages.items()):
        ls = p["lines"].values()
        la = sum(r["loc"][0] == "agreed" for r in ls)
        ba = sum(r["bin"][0] == "agreed" for r in ls)
        a.append(f"{vol}\t{pdf}\t{p['printed'] or ''}\t{p['printed_how']}\t"
                 f"{int(p['frame'])}\t{int(p['fit'])}\t{len(p['lines'])}\t"
                 f"{la}\t{len(p['lines']) - la}\t{ba}\t{len(p['lines']) - ba}\n")
        for line, r in sorted(p["lines"].items()):
            b.append(f"{vol}\t{pdf}\t{p['printed'] or ''}\t{line}\t{r['loc'][1]}\t"
                     f"{r['loc'][0]}\t{r['bin'][1]}\t{r['bin'][0]}\t"
                     f"{r['bin2'][1]}\t{r['bin2'][0]}\t{r['text']}\t{r['text_crop']}\t"
                     f"{r['name']}\t{r['stmt']}\t{r['stmt_crop']}\n")
    return "".join(a), "".join(b)


def write(pages):
    a, b = tables(pages)
    open(PAGES_OUT, "w").write(a)
    open(LINES_OUT, "w").write(b)


def summary(pages):
    c = collections.Counter()
    for p in pages.values():
        c["pages"] += 1
        c["frame"] += p["frame"]
        c["fit"] += p["fit"]
        c["printed_" + p["printed_how"]] += 1
        for r in p["lines"].values():
            c["lines"] += 1
            c["loc_" + r["loc"][0]] += 1
            c["bin_" + r["bin"][0]] += 1
    for k in sorted(c):
        print(f"  {k:28s} {c[k]}")


def _stmt(t):
    """Spaces and the remark dropped; the remark starts at a spaced '-'."""
    return re.sub(r"\s+", "", re.split(r"\s-", R.printer_charset(t))[0])


def score(pages):
    """Each status, against what the landed decks assert, nine of nine."""
    c, tx = collections.Counter(), collections.Counter()
    seen = set()
    for (vol, pdf), p in sorted(pages.items()):
        if vol != 1 or p["printed_how"] != "header" or p["printed"] in seen:
            continue
        truth = listing_truth.truth(p["printed"])
        if not truth:
            continue
        seen.add(p["printed"])
        h2 = listing_truth.half2(p["printed"])
        for line, want in listing_truth.statements(p["printed"]).items():
            r = p["lines"].get(line)
            got = r["text"] if r else ""
            tx["n"] += 1
            tx["empty"] += not got
            tx["ok"] += bool(got) and _stmt(got).endswith(_stmt(want))
        for line, (loc, b1) in truth.items():
            r = p["lines"].get(line)
            for fld, want in (("loc", loc), ("bin", b1), ("bin2", h2.get(line))):
                if not want:
                    continue
                st, v = r[fld] if r else ("not-paired", "")
                c[(fld, st, "n")] += 1
                if st in ("agreed", "agreed-out-of-order", "vision-only", "tesseract-only",
                          "arith-confirmed", "arith-only", "sym-confirmed", "sym-only"):
                    c[(fld, st, "ok")] += (v == want)
                elif st == "conflict":
                    c[(fld, st, "ok")] += want in v.split("|")
    print(f"scored against {len(seen)} landed pages (vol 1, header-read)")
    print(f"  NAME+STATEMENT draft  ({tx['n']} lines with a deck statement)")
    print(f"     ends with the deck's statement, spaces and remark dropped: "
          f"{tx['ok']}  {100 * tx['ok'] / max(1, tx['n']):.1f}%")
    print(f"     empty: {tx['empty']}")
    for fld in ("loc", "bin", "bin2"):
        tot = sum(n for (f, s, k), n in c.items() if f == fld and k == "n")
        name = {"loc": "LOCATION", "bin": "BINARY h1", "bin2": "BINARY h2"}[fld]
        print(f"  {name}  ({tot} rows with truth)")
        for st in ("agreed", "agreed-out-of-order", "arith-confirmed", "arith-only",
                   "sym-confirmed", "sym-only", "conflict",
                   "vision-only", "tesseract-only", "unread", "not-paired"):
            n = c[(fld, st, "n")]
            if not n:
                continue
            ok = c[(fld, st, "ok")]
            acc = "" if st in ("unread", "not-paired") else \
                f"{100 * ok / n:7.2f}% {'(either value)' if st == 'conflict' else 'right'}"
            print(f"     {st:22s} {n:5d} {100 * n / tot:6.1f}%   {acc}")


if __name__ == "__main__":
    pages = load_all()
    if sys.argv[1:] == ["--score"]:
        score(pages)
    else:
        write(pages)
        summary(pages)
