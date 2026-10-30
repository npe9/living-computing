#!/usr/bin/env python3
"""Turn a hand-written verify_mcp_bootstrap_pNN.py into the !SYM/!CHECK
block its deck should carry, so migrating a page is mechanical.

Runs the verifier with check_rows and finish STUBBED, captures the
SYMBOLS and ROWS it would have passed, and prints the block.  Nothing
is guessed: the literals come from the file that is already the
page's oracle.
"""
import sys, runpy, io, contextlib

path = sys.argv[1]
page = sys.argv[2]

captured = {}
def fake_check_rows(prog, rows, symbols=None, label=""):
    captured["rows"] = rows
    captured["symbols"] = symbols or {}
    return 0
def fake_finish(fails):
    pass

import listing_oracle
listing_oracle.check_rows = fake_check_rows
listing_oracle.finish = fake_finish

buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    runpy.run_path(path, run_name="__main__")

print(f"! ---- CHECKS, read by tests/verify_mcp_page.py {page} --------")
for name, loc in captured["symbols"].items():
    print(f"!SYM   {name:8s} {loc}")
for row in captured["rows"]:
    loc, printed, note = row[0], row[1], row[2]
    width = f" | {row[3]}" if len(row) > 3 else ""
    print(f"!CHECK {loc} | {printed} | {note}{width}")
