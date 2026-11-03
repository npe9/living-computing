#!/usr/bin/env python3
"""check_listing_reading.py -- the two-engine reading of EVERY page of
both MCP listing volumes is whole, consistent, fresh, and as good as it
says against the 164 pages that have bit-exact ground truth.

The reading is docs/vision/listing_reading.tsv and listing_pages.tsv,
built by tools/listing_reading.py from docs/vision/all/ (Vision whole
page + Vision column crops, one engine; tesseract column crops, the
other).  It is the acquisition source for the 243 printed pages that
have no deck.  It is NOT a transcription; rule 3 still applies.

CHECKS

  every_page_read      all 451 PDF pages (256 + 195) have all four files
  printed_numbers      each printed number is read off at most one page;
                       vol 1 printed = PDF - 7 throughout; vol 2 printed =
                       PDF + 249 then + 250, never going back (printed
                       329 is absent from the scan)
  tables_fresh         the committed tables are what the cache produces
  agreed_vs_deck       every `agreed` field on a landed page, nine of
                       nine characters, is the deck's -- or the ink was
                       inspected and tests/vision_adjudicated.tsv says the
                       engines misread it ("every-location"/"every-binary")
  floors               coverage and accuracy of each status, measured
                       2026-11-03, so a broken reader cannot pass by
                       reading less (values in FLOORS)

MEASURED INJECTIONS (python3 check_listing_reading.py --inject):

    control, nothing changed                          PASS
    deck LOCATION p.83 line 14, 004632.00 -> 004631.00
                                                      FAIL agreed_vs_deck
    PDF p.120 header 113 -> 112 (PDF p.119's number)  FAIL printed_numbers
                                                      (and tables_fresh)
    one row of listing_reading.tsv edited             FAIL tables_fresh

The deck injection first picked a row whose truth lives in a
tests/verify_*.py file, edited nothing, and stopped on its own assert;
it now picks the first agreed row that has a deck !CHECK line.

THE FOUR ADJUDICATED ROWS are all binary, all a faint 7 read 1 (or a
broken 0 read 6) by BOTH engines, each inspected on the ink.  Agreement
is therefore ~99.9%, not proof; the two agreed LOCATIONS of the same
kind are caught by the order check (`agreed-out-of-order`).
"""
import collections
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "strap"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import listing_truth        # noqa: E402
import listing_reading      # noqa: E402

PDF_PAGES = {1: 256, 2: 195}
VOL2_OFFSETS = (249, 250)
ADJUDICATED = os.path.join(HERE, "vision_adjudicated.tsv")
# (field, status): (min share of rows with truth, min accuracy).  Measured
# 2026-11-03 on 164 pages: loc agreed 67.8% / 100.00%, bin agreed 62.7% /
# 99.88% before adjudication; vision-only 99.03% / 99.07%.
FLOORS = {("loc", "agreed"): (0.60, 0.999), ("bin", "agreed"): (0.55, 0.998),
          ("loc", "vision-only"): (0.0, 0.98), ("bin", "vision-only"): (0.0, 0.98)}


def adjudicated():
    out = set()
    for ln in open(ADJUDICATED):
        if ln.startswith("#") or not ln.strip():
            continue
        p = ln.rstrip("\n").split("\t")
        if p[1].startswith("every-") and p[4] == "vision-misread":
            out.add((int(p[0]), p[1][6:], p[2], p[3]))
    return out


def main(root=ROOT):
    fails = 0

    def ok(cond, name, text):
        nonlocal fails
        print(("PASS " if cond else "FAIL ") + name + " = " + text)
        fails += not cond

    all_dir = os.path.join(root, "docs", "vision", "all")
    missing = [f"v{v}_pdf{p:03d}{ext}" for v, n in PDF_PAGES.items() for p in range(1, n + 1)
               for ext in (".vis.tsv", ".vcol.tsv", ".tes.tsv", ".geom")
               if not os.path.exists(os.path.join(all_dir, f"v{v}_pdf{p:03d}{ext}"))]
    ok(not missing, "every_page_read",
       f"{sum(PDF_PAGES.values())} PDF pages, {len(missing)} files missing {missing[:4]}")

    pages = listing_reading.load_all(all_dir)

    seen = collections.defaultdict(list)
    bad = []
    last2 = VOL2_OFFSETS[0]
    for (vol, pdf), p in sorted(pages.items()):
        if p["printed_how"] != "header":
            continue
        seen[p["printed"]].append((vol, pdf))
        off = p["printed"] - pdf
        if vol == 1 and off != -7:
            bad.append((vol, pdf, p["printed"]))
        if vol == 2:
            if off not in VOL2_OFFSETS or off < last2:
                bad.append((vol, pdf, p["printed"]))
            last2 = max(last2, off)
    dup = {k: v for k, v in seen.items() if len(v) > 1}
    ok(not dup and not bad, "printed_numbers",
       f"{len(seen)} printed numbers read off headers; {len(dup)} read twice {list(dup.items())[:3]}; "
       f"{len(bad)} off their volume's offset {bad[:3]}")

    a, b = listing_reading.tables(pages)
    pa = os.path.join(root, "docs", "vision", "listing_pages.tsv")
    pb = os.path.join(root, "docs", "vision", "listing_reading.tsv")
    fresh = os.path.exists(pa) and open(pa).read() == a and os.path.exists(pb) and open(pb).read() == b
    ok(fresh, "tables_fresh",
       f"{a.count(chr(10)) - 1} pages, {b.count(chr(10)) - 1} lines"
       + ("" if fresh else " -- STALE: run python3 tools/listing_reading.py"))

    adj = adjudicated()
    c = collections.Counter()
    used = 0
    landed = set()
    for (vol, pdf), p in sorted(pages.items()):
        if vol != 1 or p["printed_how"] != "header" or p["printed"] in landed:
            continue
        truth = listing_truth.truth(p["printed"], root)
        if not truth:
            continue
        landed.add(p["printed"])
        for line, (loc, b1) in truth.items():
            r = p["lines"].get(line)
            for fld, want in (("loc", loc), ("bin", b1)):
                if not want:
                    continue
                st, v = r[fld] if r else ("not-paired", "")
                c[(fld, "rows")] += 1
                c[(fld, st)] += 1
                if st in ("agreed", "vision-only"):
                    c[(fld, st, "ok")] += v == want
                if st == "agreed" and v != want:
                    key = (p["printed"], "location" if fld == "loc" else "binary", want, v)
                    if key in adj:
                        used += 1
                        c[(fld, st, "ok")] += 1
                        continue
                    print(f"FAIL agreed_vs_deck: p.{p['printed']} line {line} "
                          f"{'LOCATION' if fld == 'loc' else 'BINARY h1'}: deck {want}, "
                          f"Vision AND tesseract read {v}")
                    fails += 1
    ok(used == len(adj), "agreed_vs_deck",
       f"{len(landed)} landed pages; {used} of {len(adj)} adjudicated misreads still occur")

    for (fld, st), (share, acc) in FLOORS.items():
        n, rows = c[(fld, st)], c[(fld, "rows")]
        good = c[(fld, st, "ok")]
        ok(rows and n / rows >= share and good / max(1, n) >= acc, f"floor_{fld}_{st}",
           f"{n} of {rows} rows ({100 * n / max(1, rows):.1f}%, floor {100 * share:.0f}%), "
           f"{100 * good / max(1, n):.2f}% right (floor {100 * acc:.1f}%)")

    print("ALL TESTS PASSED" if not fails else f"{fails} FAILURE(S)")
    return 1 if fails else 0


def inject():
    """The docstring's injections, each on a scratch copy that it asserts it changed."""
    def scratch():
        td = tempfile.mkdtemp(prefix="reading-inject-")
        shutil.copytree(os.path.join(ROOT, "decks"), os.path.join(td, "decks"))
        os.symlink(os.path.join(ROOT, "tests"), os.path.join(td, "tests"))
        shutil.copytree(os.path.join(ROOT, "docs", "vision"), os.path.join(td, "docs", "vision"))
        return td
    res = []
    td = scratch()
    res.append(("control", main(td)))
    shutil.rmtree(td)

    td = scratch()
    pages = listing_reading.load_all(os.path.join(td, "docs", "vision", "all"))
    # the first agreed row whose truth is a deck !CHECK line (early pages
    # keep theirs in tests/verify_*.py, which this must not edit)
    target = None
    for (vol, pdf), p in sorted(pages.items()):
        if target or vol != 1 or not p["printed"]:
            continue
        deck = os.path.join(td, "decks", "mcp_bootstrap_p%d.strap" % p["printed"])
        if not os.path.exists(deck):
            continue
        s = open(deck).read()
        for line, r in sorted(p["lines"].items()):
            loc = r["loc"][1]
            if r["loc"][0] != "agreed":
                continue
            bad = loc[:5] + ("1" if loc[5] != "1" else "2") + loc[6:]
            t = re.sub(r"^(!CHECK\s+)" + re.escape(loc) + r"(\s*\|[^\n]*\|\s*line\s+%d\b)" % line,
                       r"\g<1>" + bad + r"\g<2>", s, count=1, flags=re.M)
            if t != s:
                target = (p["printed"], line, loc)
                break
    assert target, "deck injection found no row to change"
    page, line, loc = target
    open(deck, "w").write(t)
    print(f"-- injected: p.{page} line {line} LOCATION {loc} -> {bad}")
    res.append((f"deck location p.{page} line {line}", main(td)))
    shutil.rmtree(td)

    td = scratch()
    f = os.path.join(td, "docs", "vision", "all", "v1_pdf120.vis.tsv")
    s = open(f).read()
    t = re.sub(r"^(0\.0[0-5]\d*\t0\.[789]\d*\t[\d.]+\t)113$", r"\g<1>112", s, count=1, flags=re.M)
    if t == s:
        t = s.replace("PAGE NUMBER 113", "PAGE NUMBER 112", 1)
    assert t != s, "header injection changed nothing"
    open(f, "w").write(t)
    print("-- injected: PDF p.120 header 113 -> 112, the number of PDF p.119")
    res.append(("cached header", main(td)))
    shutil.rmtree(td)

    td = scratch()
    f = os.path.join(td, "docs", "vision", "listing_reading.tsv")
    s = open(f).read().split("\n")
    s[100] = s[100].replace("agreed", "vision-only", 1) if "agreed" in s[100] else s[100] + "x"
    open(f, "w").write("\n".join(s))
    print("-- injected: listing_reading.tsv row 100 edited")
    res.append(("table row", main(td)))
    shutil.rmtree(td)
    print("INJECTIONS: " + ", ".join(f"{n} -> {'FAIL' if r else 'PASS'}" for n, r in res))


if __name__ == "__main__":
    if sys.argv[1:] == ["--inject"]:
        inject()
    else:
        sys.exit(main())
