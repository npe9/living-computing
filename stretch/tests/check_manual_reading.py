#!/usr/bin/env python3
"""check_manual_reading.py -- Vision's text layer of the eleven
programming-environment manuals is whole and fresh.

docs/vision/manuals/ (tools/read_manuals.py) is a FINDING AID, like
docs/ocr/: nothing in it is a source (docs/ocr/README.md).  What this
keeps true is that it is all there and that each STEM.txt is exactly
what its boxes produce, so a search of it searches every page.

CHECKS
  manual_pages   every PDF page of every manual has its box file
                 (counts from pdfinfo, 2026-11-03: 1,166 pages)
  text_fresh     each STEM.txt equals the reading order rebuilt from
                 its boxes

MEASURED INJECTIONS (python3 check_manual_reading.py --inject):
    control                                   PASS
    one box file removed                      FAIL manual_pages
    one line of a .txt edited                 FAIL text_fresh
"""
import io
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import read_manuals     # noqa: E402

PAGES = {"C22-6728_7030_MCP_Sys_Analysis_Guide": 270,
         "C22-6728-1_7030_MCP_Sys_Analysis_Guide": 280,
         "C22-6729_7030_STRAP_II_Sys_Analysis_Guide": 211,
         "C28-6129_STRAP-II_with_update_Apr63": 79,
         "C22-6678-1_7030_MCP_Reference_Jun64": 57,
         "C28-6379-0_MCP_Loader": 24,
         "C22-6751_7030_FORTRAN_IV_May63": 37,
         "J22-6559_MCP_UsersGuide_Dec60": 19,
         "N22-0085_MCP_RefMan_Upd_May63": 12,
         "X28-6131_MCP_PocketCard": 2,
         "22-6530-2_7030RefMan": 175}


def main(out=read_manuals.OUT):
    fails = 0
    missing = [f"{s} p.{p}" for s, n in PAGES.items() for p in range(1, n + 1)
               if not os.path.exists(os.path.join(out, s, "p%03d.tsv" % p))]
    print(("PASS" if not missing else "FAIL") + f" manual_pages = {len(PAGES)} manuals, "
          f"{sum(PAGES.values())} pages, {len(missing)} missing {missing[:3]}")
    fails += bool(missing)
    stale = []
    for s in PAGES:
        buf = io.StringIO()
        for p in range(1, PAGES[s] + 1):
            f = os.path.join(out, s, "p%03d.tsv" % p)
            if os.path.exists(f):
                buf.write("==== PDF page %d ====\n" % p)
                buf.write("\n".join(read_manuals.order(read_manuals.boxes(f))) + "\n")
        t = os.path.join(out, s + ".txt")
        if not os.path.exists(t) or open(t).read() != buf.getvalue():
            stale.append(s)
    print(("PASS" if not stale else "FAIL") + f" text_fresh = {len(PAGES) - len(stale)} of "
          f"{len(PAGES)} .txt files match their boxes {stale[:3]}")
    fails += bool(stale)
    print("ALL TESTS PASSED" if not fails else f"{fails} FAILURE(S)")
    return 1 if fails else 0


def inject():
    res = []
    td = tempfile.mkdtemp(prefix="manual-inject-")
    m = os.path.join(td, "manuals")
    shutil.copytree(read_manuals.OUT, m)
    res.append(("control", main(m)))
    victim = os.path.join(m, "C28-6379-0_MCP_Loader", "p010.tsv")
    os.rename(victim, victim + ".gone")
    res.append(("box file removed", main(m)))
    os.rename(victim + ".gone", victim)
    t = os.path.join(m, "C22-6751_7030_FORTRAN_IV_May63.txt")
    s = open(t).read().split("\n")
    s[50] += " X"
    open(t, "w").write("\n".join(s))
    res.append(("txt edited", main(m)))
    shutil.rmtree(td)
    print("INJECTIONS: " + ", ".join(f"{n} -> {'FAIL' if r else 'PASS'}" for n, r in res))


if __name__ == "__main__":
    if sys.argv[1:] == ["--inject"]:
        inject()
    else:
        sys.exit(main())
