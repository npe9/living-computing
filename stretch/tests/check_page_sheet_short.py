#!/usr/bin/env python3
"""tools/page_sheet.py on a page with no line fit, and on one with a fit.

Printed p.296 (vol 2 PDF p.47) prints eleven lines; Vision reads three
of its line numbers ("1*", "2*", "1C"), and strap/listing_read.py's
fit_lines needs six, so it returns None.  page_sheet used to unpack that
None and die with a TypeError.  The fit's gate is NOT lowered (it is the
same gate tools/listing_reading.py uses, and the page has no rows to
place anyway); the sheet says the fit failed and prints what it has.

CHECKS

  short_page_runs      page_sheet 296 exits 0, writes no traceback
  short_page_says_so   and its output says LINE FIT FAILED, with the
                       count read (3) against the count needed (6)
  control_runs         page_sheet 266 (a normal page) exits 0
  control_has_rows     and prints its rows (a line-1 row, 30+ lines),
                       with hex bytes placed, and no LINE FIT FAILED

MEASURED INJECTION (2026-11-06):

    control, nothing changed                          PASS
    the fix reverted (page_sheet unpacks fit_lines'
    result unguarded)                                 FAIL short_page_runs,
                                                      short_page_says_so
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SHEET = os.path.join(ROOT, "tools", "page_sheet.py")
fails = 0


def check(name, cond, text):
    global fails
    print(("PASS " if cond else "FAIL ") + name + " = " + text)
    fails += not cond


def sheet(printed):
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(os.path.join(ROOT, d) for d in ("strap", "tests", "tools"))
    return subprocess.run([sys.executable, SHEET, str(printed)], cwd=ROOT, env=env,
                          capture_output=True, text=True)


r = sheet(296)
check("short_page_runs", r.returncode == 0 and "Traceback" not in r.stderr,
      f"exit {r.returncode}" + (", " + r.stderr.strip().splitlines()[-1] if r.stderr.strip() else ""))
check("short_page_says_so",
      re.search(r"LINE FIT FAILED ON THIS PAGE: 3 line numbers read .* 6 needed", r.stdout) is not None,
      (r.stdout.splitlines()[1] if len(r.stdout.splitlines()) > 1 else "(no output)")[:100])

c = sheet(266)
lines = c.stdout.splitlines()
check("control_runs", c.returncode == 0 and "Traceback" not in c.stderr, f"exit {c.returncode}")
check("control_has_rows",
      len(lines) >= 30 and any(re.match(r"\s+1 ", ln) for ln in lines)
      and any(re.search(r" h[0-9A-F]{2} ", ln) for ln in lines)
      and "LINE FIT FAILED" not in c.stdout,
      f"{len(lines)} lines of output")

print("ALL TESTS PASSED" if not fails else f"{fails} CHECK(S) FAILED")
sys.exit(1 if fails else 0)
