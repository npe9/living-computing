#!/usr/bin/env python3
"""verify_mcp_image.py -- MCP's whole IPL bootstrap, merged from the
eight page transcriptions into one program (strap/mcp_image.py).

EIGHT VERIFIED PAGES ARE NOT A VERIFIED IMAGE.  Each page file was
checked against its own printed page, and each SYNs the symbols the
others place.  The merge is where two transcriptions can disagree
without anyone noticing, so this file checks three things the page
verifiers cannot:

  1. EVERY STAND-IN AGREED WITH WHAT IT STANDS IN FOR.  mcp_image.py
     asserts that while merging; this file re-runs it so the suite
     sees it fail rather than a later build.

  2. EVERY SYMBOL LANDS WHERE ITS OWN PAGE VERIFIER SAYS.  The
     SYMBOLS dict of each verify_mcp_bootstrap_*.py is imported and
     compared against the merged image -- about a hundred assertions
     that cost nothing and that no page verifier makes about the
     whole.

  3. THE IMAGE REPRODUCES THE TWO NUMBERS THE LISTING STATES ABOUT
     ITSELF.  Printed p.2's IPL control word counts X BS END -
     X IPL BS = 0o560 = 368 words, the record the tape carries.
     Printed p.13's X IPL K is 1.0 + that = 0o561 = 369, the
     bootstrap including its own control word.  If the merge is
     wrong, one of these moves.
"""
import importlib

from mcp_image import build

prog, src, defined, external = build()

failed = 0


def check(what, got, want):
    global failed
    ok = got == want
    failed += not ok
    print(("PASS " if ok else "FAIL ") + f"MCP image {what}: {got} "
          + ("== " if ok else "!= ") + f"{want}")


# --- 3. the two numbers the listing states about itself -------------
iplbs, bsend, iplk = (prog.symtab[n] for n in ("XIPLBS", "XBSEND", "XIPLK"))
check("X BS END - X IPL BS, the record the tape carries (p.2's CW count)",
      f"{(bsend - iplbs)//64:#o} words", f"{0o560:#o} words")
check("X IPL K, the bootstrap including its control word (p.13 line 27)",
      f"{iplk//64:#o} words", f"{0o561:#o} words")
check("the image's extent", f"{min(prog.words):#o}..{max(prog.words):#o}",
      f"{0o40:#o}..{0o620:#o}")
check("words occupied", max(prog.words) - min(prog.words) + 1, 369)

# --- 2. every page verifier's own SYMBOLS dict ----------------------
total = 0
for mod_name in ("verify_mcp_bootstrap_p2", "verify_mcp_bootstrap_p3",
                 "verify_mcp_bootstrap_p4", "verify_mcp_bootstrap_p5_p6",
                 "verify_mcp_bootstrap_p7_p8", "verify_mcp_bootstrap_p9_p12",
                 "verify_mcp_bootstrap_p13", "verify_mcp_bootstrap_p14"):
    # Each verifier runs its own checks on import and exits non-zero on
    # failure, so importing it here is a second run of that page.
    mod = importlib.import_module(mod_name)
    bad = []
    for sym, octal in mod.SYMBOLS.items():
        w, b = octal.split(".")
        want = int(w, 8) * 64 + int(b, 8)
        if sym not in prog.symtab:
            bad.append(f"{sym} missing from the image")
        elif prog.symtab[sym] != want:
            bad.append(f"{sym} at bit {prog.symtab[sym]}, {octal} is bit {want}")
    total += len(mod.SYMBOLS)
    print(("PASS " if not bad else "FAIL ")
          + f"MCP image {mod_name}'s {len(mod.SYMBOLS)} symbols land where "
            f"that page prints them" + ("" if not bad else f" -- {bad}"))
    failed += bool(bad)

print(f"PASS MCP image {total} symbols checked across eight page verifiers; "
      f"{len(external)} symbols are external to the bootstrap and keep a "
      f"single stand-in")

if failed:
    raise SystemExit(1)
print("ALL TESTS PASSED")
