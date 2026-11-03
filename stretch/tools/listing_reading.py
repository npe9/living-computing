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
                                   and BINARY half word 1 (octal part),
                                   each with a status

STATUS of a field, from the two engines:

  agreed          Vision and tesseract read the same value
  conflict        the readings differ -- every value recorded

Vision is read twice, whole page and column crops (.vcol.tsv), but it is
ONE engine: measured, it repeats 50-75% of its own errors across
framings.  So two Vision readings that agree are still `vision-only`;
`agreed` always means tesseract read the same value as Vision.
  vision-only     only Vision read it
  tesseract-only  only tesseract read it
  unread          neither

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
    gl = open(stem + ".geom").read().strip()
    page = {"header": R.page_number(vis), "frame": gl != "none", "fit": False, "lines": {}}
    if gl == "none":
        return page
    g = json.loads(gl)
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
        for fld, xw in (("loc", g["loc_x"]), ("bin", g["bin_x"])):
            row[fld] = status((R.field_at(vis, y, pitch, xw, cw),
                               R.field_at(vcol, y, pitch, xw, cw)),
                              R.field_at(tes, y, pitch, xw, cw))
        if row["loc"][0] != "unread" or row["bin"][0] != "unread":
            page["lines"][line] = row
    # ORDER CHECK on agreed locations: out of order with BOTH agreed
    # neighbours, which are in order with each other
    ag = [(l, R.bit_address(r["loc"][1])) for l, r in sorted(page["lines"].items())
          if r["loc"][0] == "agreed"]
    for i in range(1, len(ag) - 1):
        (_, a), (line, v), (_, b) = ag[i - 1], ag[i], ag[i + 1]
        if a <= b and not a <= v <= b:
            page["lines"][line]["loc"] = ("agreed-out-of-order", page["lines"][line]["loc"][1])
    return page


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
    return infer_printed(pages)


def tables(pages):
    """(listing_pages.tsv, listing_reading.tsv) as text."""
    a = ["vol\tpdf\tprinted\tprinted_from\tframe\tline_fit\tlines\t"
         "loc_agreed\tloc_other\tbin_agreed\tbin_other\n"]
    b = ["vol\tpdf\tprinted\tline\tlocation\tloc_status\tbinary_h1\tbin_status\n"]
    for (vol, pdf), p in sorted(pages.items()):
        ls = p["lines"].values()
        la = sum(r["loc"][0] == "agreed" for r in ls)
        ba = sum(r["bin"][0] == "agreed" for r in ls)
        a.append(f"{vol}\t{pdf}\t{p['printed'] or ''}\t{p['printed_how']}\t"
                 f"{int(p['frame'])}\t{int(p['fit'])}\t{len(p['lines'])}\t"
                 f"{la}\t{len(p['lines']) - la}\t{ba}\t{len(p['lines']) - ba}\n")
        for line, r in sorted(p["lines"].items()):
            b.append(f"{vol}\t{pdf}\t{p['printed'] or ''}\t{line}\t{r['loc'][1]}\t"
                     f"{r['loc'][0]}\t{r['bin'][1]}\t{r['bin'][0]}\n")
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


def score(pages):
    """Each status, against what the landed decks assert, nine of nine."""
    c = collections.Counter()
    seen = set()
    for (vol, pdf), p in sorted(pages.items()):
        if vol != 1 or p["printed_how"] != "header" or p["printed"] in seen:
            continue
        truth = listing_truth.truth(p["printed"])
        if not truth:
            continue
        seen.add(p["printed"])
        for line, (loc, b1) in truth.items():
            r = p["lines"].get(line)
            for fld, want in (("loc", loc), ("bin", b1)):
                if not want:
                    continue
                st, v = r[fld] if r else ("not-paired", "")
                c[(fld, st, "n")] += 1
                if st in ("agreed", "agreed-out-of-order", "vision-only", "tesseract-only"):
                    c[(fld, st, "ok")] += (v == want)
                elif st == "conflict":
                    c[(fld, st, "ok")] += want in v.split("|")
    print(f"scored against {len(seen)} landed pages (vol 1, header-read)")
    for fld in ("loc", "bin"):
        tot = sum(n for (f, s, k), n in c.items() if f == fld and k == "n")
        print(f"  {'LOCATION' if fld == 'loc' else 'BINARY h1'}  ({tot} rows with truth)")
        for st in ("agreed", "agreed-out-of-order", "conflict", "vision-only",
                   "tesseract-only", "unread", "not-paired"):
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
