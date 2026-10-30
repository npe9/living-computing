#!/usr/bin/env python3
"""check_symbol_spellings.py -- catch a transcription error that every
other check in this repository is blind to: a SYMBOL NAME misread off
the listing.

listing_oracle.py compares LOCATIONS and BINARY OUTPUT. It never looks
at a label's SPELLING, because a label is not in the machine code. So
a deck that reads `T FMODE` as `T FMCDE` assembles perfectly, passes
its page check, and is simply the wrong name -- and stays wrong until
somebody merges two decks and a symbol fails to resolve.

WHAT MAKES THE CHECK POSSIBLE is that every deck SYNs its own
externals from its own page. When two pages reference the same word,
two different transcribers read the same name independently. Agreement
is evidence; disagreement is a defect in one of them.

TWO SOURCES OF NAME->LOCATION, because one was not enough. The first
version of this file read only SYN lines, and it MISSED A LIVE DEFECT
it should have caught: decks/mcp_bootstrap_p98.strap spelled a word
YLCL2 where printed p.39 spells it YLOL2, at the one location both
print. It escaped because p.98 defines the name with a VF card, not a
SYN, so the two never grouped. A label can be defined by anything
that occupies storage, so this now also reads the `!SYM NAME octal`
blocks, which give a name its ABSOLUTE location however it was
defined, and resolves literal SYN addresses to the same bit number so
the two sources share one key.

WHAT IT STILL CANNOT CATCH is both decks being wrong together. printed
p.39 and printed p.98 agreed on SYSMCD for a word whose own comment
reads "-TWO BIT OPERATING MODE"; nothing here could have flagged that,
and only reading the comment did. See docs/transcription_workflow.md,
"THE COMMENT COLUMN IS ENGLISH".

WHAT MAKES IT PRECISE is restricting it to the drum's own failure
modes (docs/transcription_workflow.md, "THREE GLYPH PAIRS BREAK ON
THIS DRUM"): O/C, C/D, B/8, O/0, C/0, plus a wholly dropped or added
character. A bare edit-distance check does not work -- it fires on
XMSG15/XMSG16 and TIXF/TIXK, which are deliberately distinct names,
and on SBAMCP/TBAMCP and LIREF/TIREF, where the differing character
is the FIRST one and MCP's S/T/L table prefixes are a real naming
convention. Hence: the first character must match, and the single
differing character must be one the printer actually confuses.

Measured on the corpus as of 2026-10-30: 605 SYN definitions across
~90 MCP decks, 2 hits, 0 false positives. Both hits are real:

  addr 1.6   TIODCK (p.84)      vs TIODK  (p.91)  -- printed T IODK
  addr 2.48  TFMCDE (pp.85,93)  vs TFMODE (p.91)  -- printed T FMODE,
             and its own comment on p.85 line 11 reads "-FILE MCDE",
             i.e. MODE, which is how the O was settled.

Usage: run from tests/ with no arguments. Exit status is the number of
disagreeing pairs, so a hit fails the suite.
"""

import collections
import itertools
import os
import re
import sys

DECKS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "decks")

# The glyph pairs this printer actually confuses. See
# docs/transcription_workflow.md and docs/listing_typography.md.
CONFUSABLE = {frozenset("OC"), frozenset("CD"), frozenset("B8"),
              frozenset("O0"), frozenset("C0")}

SYN_RE = re.compile(r'^\s*([A-Z0-9$]+)\s+SYN(?:\([^)]*\))?\s*,\s*([^!\s]+)',
                    re.IGNORECASE)


def drum_confusion(a, b):
    """Why `a` and `b` might be two readings of ONE printed name, or None.

    The first character must agree: MCP really does name the same word
    SBAMCP and TBAMCP from two different tables, and flagging that is
    noise, not a finding.
    """
    if a[0] != b[0]:
        return None
    if len(a) == len(b):
        diff = [(x, y) for x, y in zip(a, b) if x != y]
        if len(diff) == 1 and frozenset(diff[0]) in CONFUSABLE:
            return "glyph %s/%s" % diff[0]
        return None
    if abs(len(a) - len(b)) == 1:
        lo, hi = (a, b) if len(a) < len(b) else (b, a)
        for i in range(len(hi)):
            if hi[:i] + hi[i + 1:] == lo:
                return "extra %r in %s" % (hi[i], hi)
    return None


SYM_RE = re.compile(r'^!SYM\s+([A-Z0-9$]+)\s+([0-7]+\.[0-7]+)\s*$',
                    re.IGNORECASE)


def _as_bit(addr):
    """A literal bit address as an int, or None if it is symbolic.

    Keying on the TEXT would not do: printed p.39 writes (8)5464.40
    and a !SYM block writes 005464.40 for the same bit.
    """
    try:
        import strap_asm
        return strap_asm.eval_expr(addr, {}, 0, lineno=0)
    except Exception:
        return None


def collect(deck_dir=DECKS):
    """key -> {name -> {pages}} over every MCP deck.

    The key is a resolved bit number where the address is a literal,
    and the raw text otherwise, so symbolic forms like SCOMRG+.8 still
    group with each other.
    """
    addr_names = collections.defaultdict(lambda: collections.defaultdict(set))
    aliases = set()
    names = re.compile(r'mcp_bootstrap_p(\d+(?:_p\d+)?)\.strap$')
    for fn in sorted(os.listdir(deck_dir)):
        m = names.search(fn)
        if not m:
            continue
        page = m.group(1)
        with open(os.path.join(deck_dir, fn), encoding="utf-8",
                  errors="replace") as fh:
            for line in fh:
                hit = SYN_RE.match(line)
                if hit:
                    name, addr = hit.group(1).upper(), hit.group(2).strip().rstrip(',')
                    if addr.startswith('$'):      # index-register aliases
                        continue
                    bit = _as_bit(addr)
                    if bit is None and addr.upper().isalnum():
                        # "S UN A  SYN, S UN A A" -- a deck giving one
                        # word a second name ON PURPOSE.  Two names at
                        # one location is exactly what this file looks
                        # for, so an explicit alias has to be excluded
                        # or printed p.99's SUNA/SUNAA reads as a
                        # misspelling.  Only a bare symbol counts;
                        # SCOMRG+.8 is an offset, not an alias.
                        aliases.add(frozenset((name, addr.upper())))
                    addr_names[bit if bit is not None else addr][name].add(page)
                    continue
                hit = SYM_RE.match(line)
                if hit:
                    # A !SYM line gives a name its absolute location
                    # however the deck defined it -- SYN, VF, DD or a
                    # label on an instruction.
                    name, loc = hit.group(1).upper(), hit.group(2)
                    bit = _as_bit("(8)%s" % loc)
                    if bit is not None:
                        addr_names[bit][name].add(page)
    return addr_names, aliases


def main():
    addr_names, aliases = collect()
    total = sum(len(v) for v in addr_names.values())
    bad = []
    for addr, names in sorted(addr_names.items(), key=lambda kv: str(kv[0])):
        for a, b in itertools.combinations(sorted(names), 2):
            if frozenset((a, b)) in aliases:
                continue
            why = drum_confusion(a, b)
            if why:
                bad.append((addr, a, sorted(names[a]), b, sorted(names[b]), why))
    for addr, a, pa, b, pb, why in bad:
        print("FAIL two spellings of one symbol at %s: %s (pp.%s) vs %s (pp.%s) -- %s"
              % (addr, a, ",".join(pa), b, ",".join(pb), why))
    if bad:
        print("FAIL %d symbol(s) spelled two ways; one reading of each is wrong"
              % len(bad))
    else:
        print("PASS %d symbol definitions, no symbol spelled two ways" % total)
    return len(bad)


if __name__ == "__main__":
    sys.exit(main())
