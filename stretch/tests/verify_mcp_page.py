#!/usr/bin/env python3
"""Check ANY transcribed MCP page against its own deck's listing block.

    python3 verify_mcp_page.py 84

>>> WHY THIS EXISTS. <<<  Every transcribed page has had its own
verifier -- 76 of them -- and each one re-types, as Python literals,
facts the deck already records in its listing comments.  That is a
second place to keep the same data in step, and the per-page file is
the single largest piece of hand work in
docs/transcription_workflow.md.  A page should cost a deck and one
registration line.

>>> IT READS A MARKED BLOCK, NOT THE PROSE COMMENTS. <<<  The decks'
"!   line 7  004627.40  000000.30 00   CNOP" comments are for a human
and are not parseable without guessing where the BINARY OUTPUT column
stops and the data description begins -- "002155.00+ +00000000  B ,31
,01" has three fields that all look alike.  Guessing there would make
the checker's silence meaningless.  So a deck declares its checks
explicitly:

    !SYM   TMMAX   004630.00
    !CHECK 004627.40 | 000000.30 00 | line 7  CNOP
    !CHECK 004630.00 | 7777 | line 8  T MMAX DD(BU,12),4095 | 12

!SYM is a symbol and the location the page prints for it.
!CHECK is a location, the BINARY OUTPUT exactly as printed, a note,
and optionally a WIDTH IN BITS for a DD that prints as bare octal.
Both are passed straight to listing_oracle.check_rows, which is what
the hand-written verifiers call.

A deck with no such lines is reported as unchecked rather than passed,
because a checker that passes a page it did not look at is worse than
no checker.
"""
import os
import re
import sys

from listing_oracle import check_rows, finish
from strap_asm import assemble

DECK = "../decks/mcp_bootstrap_p%s.strap"


def parse(text):
    syms, rows, bad = {}, [], []
    for n, raw in enumerate(text.splitlines(), 1):
        s = raw.strip()
        if s.startswith("!SYM"):
            parts = s[4:].split()
            if len(parts) != 2:
                bad.append(f"line {n}: !SYM takes NAME and LOCATION, got {s!r}")
                continue
            syms[parts[0]] = parts[1]
        elif s.startswith("!CHECK"):
            parts = [p.strip() for p in s[6:].split("|")]
            if len(parts) < 3:
                bad.append(f"line {n}: !CHECK takes LOC | PRINTED | NOTE "
                           f"[| WIDTH], got {s!r}")
                continue
            row = [parts[0], parts[1], parts[2]]
            if len(parts) > 3 and parts[3]:
                row.append(int(parts[3]))
            rows.append(tuple(row))
    return syms, rows, bad


def main():
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} PRINTED_PAGE")
    page = sys.argv[1]
    path = DECK % page
    if not os.path.exists(path):
        raise SystemExit(f"FAIL no deck for printed p.{page} at {path}")
    text = open(path).read()
    syms, rows, bad = parse(text)
    for b in bad:
        print(f"FAIL MCP p.{page} malformed check: {b}")
    if not syms and not rows:
        print(f"FAIL MCP p.{page}: the deck declares no !SYM or !CHECK "
              f"lines, so nothing was checked")
        sys.exit(1)
    prog = assemble(text)
    fails = check_rows(prog, rows, syms, label=f"MCP p.{page} ") + len(bad)
    print(f"MCP p.{page}: {len(syms)} symbols, {len(rows)} listing rows")
    finish(fails)


if __name__ == "__main__":
    main()
