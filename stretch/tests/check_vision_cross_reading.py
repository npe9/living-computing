#!/usr/bin/env python3
"""check_vision_cross_reading.py -- two OCR ENGINES, macOS Vision and
tesseract, as an independent second reading of every landed MCP deck's
page.

>>> WHY THIS EXISTS. <<<  Ten rows of `C`-for-`0` once reached the
corpus because listing blocks were pasted from the volume OCR instead
of read, and the check that should have caught them compared 8 of 12
characters.  Neither engine has seen that OCR.  They read the page.

It also LICENSES the engines for the 243 pages that have no deck yet:
this is the measurement, against bit-exact ground truth, that says how
far a reading can be trusted.

>>> WHY TWO ENGINES. <<<  Measured on 19 pages (tools/README_vision.md):
Vision at other resolutions repeats 50-75% of its own errors, so a
Vision-only disagreement is a ~2% signal, mostly its systematic 7->1.
Tesseract shared ONE error with Vision in that sample.  So:

    Vision disagrees, tesseract does not confirm  -> CANDIDATE, counted
    Vision AND tesseract read the SAME value, and
    it is not the deck's                          -> FAIL, unless
                                                     tests/vision_adjudicated.tsv
                                                     says the ink shows
                                                     the deck is right

>>> WHAT IT READS. <<<  docs/vision/mcp_pNNN.tsv (Vision, 300 dpi whole
page, tools/vision_cache.py) and mcp_pNNN.tes.tsv (tesseract, column
crop, tools/tess_cache.py).  The suite never runs an OCR engine.

>>> WHAT IT COMPARES -- DEPTH, NOT JUST REACH. <<<

  1. the page's own PAGE NUMBER header against the deck's page;
  2. LOCATION, all nine characters, per LINE;
  3. the OCTAL part of BINARY half word 1 ("221512.40"), all nine
     characters, per LINE.

Rows are keyed by LINE NUMBER (strap/listing_truth.py), never by value:
adjacent locations differ in one or two characters, and value pairing
reports neighbours as disagreements (it did, 1,012 times).  The line's
y is fitted from the LINE column (strap/listing_read.py).

NOT COMPARED, said out loud: the hex byte (C-for-0 defeats every
method tried); binary half word 2; the NAME and STATEMENT columns; the
19 pages listing_truth.py names as carrying no line-keyed row.

FLOORS, so a broken probe cannot pass by comparing nothing: Vision's
agreement on compared fields must be >= 95% (measured 97.9% on the 19
pages), and the line fit must hold on >= 90% of pages with truth.

MEASURED INJECTIONS (python3 check_vision_cross_reading.py --inject):

    control, nothing changed                       PASS
    deck LOCATION p.112 line 1, 215100.00 -> 215101.00
                                                   FAIL engines_agree_with_deck
    cached header p.112, 112 -> 113                FAIL header_page_number

The deck row is the first both engines read as the deck does; the
first attempt picked line 3, which tesseract does not read, and the
injection PASSED -- it could not be caught by construction.  The first
header attempt matched "PAGE NUMBER 112" as one token; Vision reads the
number as its own token, nothing was changed, and it PASSED too.  Both
injections now assert that they changed their file.

BEFORE THE PITCH BOUND (strap/listing_read.py), 14 rows FAILED here on
p.53, 95 and 156: their LINE columns read badly, the fit's pitch came
out 0.0120-0.0148 against a measured 0.0151-0.0153, and rows were
compared with their neighbours.  Bounded and gated, those pages are
reported unfit instead (12 of 174), and no row fails.
"""
import collections
import glob
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "strap"))
import listing_truth                                           # noqa: E402
from listing_read import LOC_X, BIN_X, load, fit_lines, field_at  # noqa: E402

ADJUDICATED = os.path.join(HERE, "vision_adjudicated.tsv")
VIS_FLOOR = 0.95
FIT_FLOOR = 0.90


def page_number(obs):
    """The header's PAGE NUMBER, or None if Vision did not read one."""
    top = sorted(o for o in obs if o[0] < 0.06)
    for i, (y, x, t) in enumerate(top):
        m = re.search(r"PAGE NUMBER\s*(\d+)", t)
        if m:
            return int(m.group(1))
        if "PAGE NUMBER" in t:
            for y2, x2, t2 in top:
                if abs(y2 - y) < 0.006 and x2 > x and re.fullmatch(r"\d{1,3}", t2.strip()):
                    return int(t2.strip())
    return None


def load_adjudicated():
    """{(page, field, deck, read): (verdict, reason)}"""
    out = {}
    if os.path.exists(ADJUDICATED):
        for ln in open(ADJUDICATED):
            if ln.startswith("#") or not ln.strip():
                continue
            p = ln.rstrip("\n").split("\t")
            out[(int(p[0]), p[1], p[2], p[3])] = (p[4], p[5] if len(p) > 5 else "")
    return out


def compare(page, root, cache):
    res, fails = collections.Counter(), []
    vis = load(os.path.join(cache, "mcp_p%03d.tsv" % page))
    tp = os.path.join(cache, "mcp_p%03d.tes.tsv" % page)
    tes = load(tp) if os.path.exists(tp) else []
    pn = page_number(vis)
    if pn is None:
        res["header_unread"] += 1
    elif pn != page:
        fails.append(("header", str(page), str(pn)))
    else:
        res["header_ok"] += 1

    truth = listing_truth.truth(page, root)
    if not truth:
        return res, fails
    res["pages_with_truth"] += 1
    f = fit_lines(vis)
    if f is None:
        res["pages_unfit"] += 1
        return res, fails
    y0, pitch, _, _ = f
    for line, (loc, b1) in sorted(truth.items()):
        y = y0 + (line - 1) * pitch
        for field, want, xw in (("location", loc, LOC_X), ("binary", b1, BIN_X)):
            if not want:
                continue
            v = field_at(vis, y, pitch, xw)
            t = field_at(tes, y, pitch, xw)
            res[field + "_rows"] += 1
            if v is None:
                continue
            res[field + "_vis_read"] += 1
            if v == want:
                res[field + "_vis_agree"] += 1
                if t == want:
                    res[field + "_both_agree"] += 1
            elif t == v:
                fails.append((field + "@line %d" % line, want, v))
            else:
                res[field + "_candidate"] += 1
    return res, fails


def main(root=ROOT, cache=None):
    cache = cache or os.path.join(root, "docs", "vision")
    adj = load_adjudicated()
    tot = collections.Counter()
    nfail = pages = 0
    for d in sorted(glob.glob(os.path.join(root, "decks", "mcp_bootstrap_p*.strap"))):
        m = re.search(r"_p(\d+)\.strap$", d)
        if not m:
            continue
        page = int(m.group(1))
        if not os.path.exists(os.path.join(cache, "mcp_p%03d.tsv" % page)):
            continue
        pages += 1
        res, fails = compare(page, root, cache)
        tot.update(res)
        for field, dv, rv in fails:
            verdict = adj.get((page, field.split("@")[0], dv, rv))
            if verdict and verdict[0] == "vision-misread":
                tot["adjudicated"] += 1
                continue
            name = "header_page_number" if field == "header" else "engines_agree_with_deck"
            print(f"FAIL {name}: p.{page} {field}: deck {dv!r}, "
                  f"{'Vision' if field == 'header' else 'Vision AND tesseract'} read {rv!r}")
            nfail += 1

    def ok(cond, name, text):
        nonlocal nfail
        print(("PASS " if cond else "FAIL ") + name + " = " + text)
        nfail += not cond

    ok(pages > 0, "vision_pages", f"{pages} decks with a cached reading")
    ok(True, "header_page_number", f"{tot['header_ok']} agree, {tot['header_unread']} unread")
    wt = tot["pages_with_truth"]
    ok(wt and (wt - tot["pages_unfit"]) / wt >= FIT_FLOOR, "line_fit",
       f"{wt - tot['pages_unfit']} of {wt} pages with truth (floor {FIT_FLOOR:.0%})")
    for field in ("location", "binary"):
        rd, ag = tot[field + "_vis_read"], tot[field + "_vis_agree"]
        ok(rd and ag / rd >= VIS_FLOOR, field + "_depth",
           f"9 of 9 characters; Vision read {rd} of {tot[field + '_rows']} rows, "
           f"{ag} agree ({100 * ag / max(1, rd):.2f}%, floor {VIS_FLOOR:.0%}); "
           f"{tot[field + '_both_agree']} confirmed by tesseract; "
           f"{tot[field + '_candidate']} Vision-only candidates")
    ok(True, "adjudicated", f"{tot['adjudicated']} both-engine readings the ink overrules")
    print("ALL TESTS PASSED" if not nfail else f"{nfail} FAILURE(S)")
    return 1 if nfail else 0


def both_agree_row(page, root=ROOT):
    """The first LOCATION line on `page` that BOTH engines read as the deck
    does -- the only kind of row a deck perturbation can be caught on."""
    cache = os.path.join(root, "docs", "vision")
    vis = load(os.path.join(cache, "mcp_p%03d.tsv" % page))
    tes = load(os.path.join(cache, "mcp_p%03d.tes.tsv" % page))
    y0, pitch, _, _ = fit_lines(vis)
    for line, (loc, _) in sorted(listing_truth.truth(page, root).items()):
        y = y0 + (line - 1) * pitch
        if field_at(vis, y, pitch, LOC_X) == loc == field_at(tes, y, pitch, LOC_X):
            return line, loc
    raise SystemExit(f"p.{page}: no row both engines read -- injection cannot run")


def inject(page=112):
    """The docstring's three measured injections, each on a scratch copy.
    Each asserts it CHANGED its file: an injection that edits nothing
    passes for the wrong reason."""
    def scratch():
        td = tempfile.mkdtemp(prefix="vision-inject-")
        shutil.copytree(os.path.join(ROOT, "decks"), os.path.join(td, "decks"))
        os.symlink(os.path.join(ROOT, "tests"), os.path.join(td, "tests"))
        shutil.copytree(os.path.join(ROOT, "docs", "vision"), os.path.join(td, "docs", "vision"))
        return td
    results = []
    td = scratch()
    results.append(("control", main(td)))

    line, loc = both_agree_row(page)
    bad = loc[:5] + ("1" if loc[5] != "1" else "2") + loc[6:]
    deck = os.path.join(td, "decks", "mcp_bootstrap_p%d.strap" % page)
    s = open(deck).read()
    t = re.sub(r"^(!CHECK\s+)" + re.escape(loc) + r"(\s*\|[^\n]*\|\s*line\s+%d\b)" % line,
               r"\g<1>" + bad + r"\g<2>", s, count=1, flags=re.M)
    assert t != s, "deck injection changed nothing"
    open(deck, "w").write(t)
    print(f"-- injected: p.{page} line {line} LOCATION {loc} -> {bad}")
    results.append((f"deck location p.{page} line {line}", main(td)))
    shutil.rmtree(td)

    td = scratch()
    c = os.path.join(td, "docs", "vision", "mcp_p%03d.tsv" % page)
    s = open(c).read()
    t = re.sub(r"^(0\.0[0-5]\d*\t0\.[789]\d*\t[\d.]+\t)%d$" % page,
               r"\g<1>%d" % (page + 1), s, count=1, flags=re.M)
    assert t != s, "header injection changed nothing"
    open(c, "w").write(t)
    print(f"-- injected: p.{page} cached header {page} -> {page + 1}")
    results.append(("cached header", main(td)))
    shutil.rmtree(td)
    print("INJECTIONS: " + ", ".join(f"{n} -> {'FAIL' if r else 'PASS'}" for n, r in results))


if __name__ == "__main__":
    if sys.argv[1:] == ["--inject"]:
        inject()
    else:
        sys.exit(main())
