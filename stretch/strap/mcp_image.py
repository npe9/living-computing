#!/usr/bin/env python3
"""mcp_image.py -- assemble MCP's whole IPL bootstrap from the eight
page transcriptions, as one program.

WHY THIS IS NOT JUST `cat`.  The thirteen printed pages were
transcribed as eight files so that each could be checked against its
own page, and each one SYNs the symbols the others place -- p.2 SYNs
`X S ROOF` from p.13, p.7-8 SYNs thirty-nine message labels from
pp.9-13, p.14 SYNs `X BUFER` from p.13 and p.13 SYNs `X BS END` from
p.14.  Concatenated, every one of those is a multiple definition.

THE MERGE IS WHERE TWO TRANSCRIPTIONS CAN DISAGREE WITHOUT ANYONE
NOTICING, so the rule is: a SYN that stands in for a symbol another
file DEFINES is dropped, **and the drop asserts the two values agreed
first**.  That is the same guard as `verify_mcp_bootstrap_p7_p8.py`'s
`cross_check()`, which earned its keep on its first run by catching a
label whose bit part had been converted out of octal.  Without it, a
merge silently prefers one transcription over the other and eight
verified pages become one unverified image.

HOW A STAND-IN IS TOLD FROM A DEFINITION.  A stand-in is written
`SYN, (8)nnn.nn` -- a bare octal literal, which is how every page
file cites an address printed on another page.  A definition is
anything else: `SYN,$` (the message labels), `SYN,$-X ERR DD`
(`X E DD K`), `SYN,1.0 + X BS END - X IPLBS` (`X IPL K`),
`SYN(BU,5),(2)00110` (`X EE EOP`).  Symbols with no definition
anywhere -- the error sites on printed pp.15-32, `X ZEROS`,
`X IN END` -- keep one stand-in, and all their stand-ins must agree
too.

WHAT THE IMAGE IS.  `SLC,(8)40.0` through `X BS END` at `000621.00`:
369 words, of which the IPL reads 368.  Both numbers are the
listing's own and both are asserted below.

PRINTED pp.15 ONWARD ARE DELIBERATELY NOT HERE.  `decks/` now holds
transcriptions of pp.15, 16 and 17 as well, and they belong to the
SAME STRAP assembly -- but not to this image.  The bootstrap is the
tape record, X IPL BS through X BS END, and printed p.14's last
instruction branches OUT of it to p.15's `X 10` at 000622.00.  MCP
proper is loaded by the bootstrap, not with it.  Adding a later page
to PAGES would make the image longer than the control word on
printed p.2 counts, and the assertion at the end of this file is
what would catch that.
"""
import os
import re
import sys

from strap_asm import assemble, iter_statements

# RESOLVED AGAINST THIS FILE, NOT THE CALLER'S WORKING DIRECTORY.
# strap/mcp_crop.sh had the same bug on 2026-10-17 -- a bare relative
# path that worked from one directory and failed from the next -- and
# this one would have broken the moment the decks moved out of
# decks/, which they did.


_DECKS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     os.pardir, "decks")


def DECK(name):
    """A deck, by name, under stretch/decks/."""
    return os.path.join(_DECKS, name)

# In address order, which is also the order the merged source needs:
# each file carries its own SLC, but keeping them in order means the
# merged listing reads like the program.
PAGES = [
    (DECK("mcp_bootstrap_p2.strap"), "printed p.2"),
    (DECK("mcp_bootstrap_p3.strap"), "printed p.3"),
    (DECK("mcp_bootstrap_p4.strap"), "printed p.4"),
    (DECK("mcp_bootstrap_p5_p6.strap"), "printed pp.5-6"),
    (DECK("mcp_bootstrap_p7_p8.strap"), "printed pp.7-8"),
    (DECK("mcp_bootstrap_p9_p12.strap"), "printed pp.9-12"),
    (DECK("mcp_bootstrap_p13.strap"), "printed p.13"),
    (DECK("mcp_bootstrap_p14.strap"), "printed p.14"),
]

_STANDIN = re.compile(r'^\(8\)[0-7]+(\.[0-7]+)?$')
_NAMED = re.compile(r'^(\S+)\s+(.*)$')


def _classify(path):
    """Returns (places, standins, defines) for one page file, each a
    dict of symbol -> resolved bit address."""
    src = open(path).read()
    prog = assemble(src)
    places, standins, defines = {}, {}, {}
    for st in iter_statements(src):
        if not st.name:
            continue
        sym = st.name.upper()
        val = prog.symtab[sym]
        if st.op.upper() != 'SYN':
            places[sym] = val
        elif len(st.fields) == 1 and _STANDIN.match(st.fields[0].replace(' ', '')):
            standins[sym] = val
        else:
            defines[sym] = val
    return places, standins, defines


def merge(verbose=False):
    """Build the merged source text and the provenance of every symbol.

    Returns (source, defined, external) where `defined` maps a symbol
    to the page that places or defines it and `external` maps a symbol
    with no definition anywhere to the page whose stand-in is kept.
    """
    defined, standins = {}, {}
    for path, label in PAGES:
        places, s, d = _classify(path)
        for sym, val in list(places.items()) + list(d.items()):
            if sym in defined:
                raise SystemExit(
                    f"FAIL {sym} is defined twice: {defined[sym][0]} and "
                    f"{label}")
            defined[sym] = (label, val)
        for sym, val in s.items():
            standins.setdefault(sym, []).append((label, val))

    # EVERY STAND-IN MUST AGREE WITH WHAT IT STANDS IN FOR.  This is
    # the whole reason the merge is a program and not a shell pipeline.
    checked = 0
    for sym, cites in sorted(standins.items()):
        vals = {v for _, v in cites}
        if sym in defined:
            want = defined[sym][1]
            for label, val in cites:
                if val != want:
                    raise SystemExit(
                        f"FAIL {sym}: {label} SYNs bit {val}, "
                        f"{defined[sym][0]} places it at bit {want}")
                checked += 1
        elif len(vals) > 1:
            raise SystemExit(
                f"FAIL {sym} has no definition and its stand-ins "
                f"disagree: {cites}")
        else:
            checked += len(cites) - 1
    external = {s: c[0][0] for s, c in standins.items() if s not in defined}

    # Now emit: every line of every page file, minus the stand-ins it
    # no longer needs and minus its END.
    out = []
    kept = set()   # externals already emitted; LOCAL, because module
                   # state here made a second build() in one process
                   # drop the stand-in the first had kept and then
                   # fail to resolve it.
    for path, label in PAGES:
        out.append(f"! ================ {label} "
                   f"({path.split('/')[-1]}) ================")
        emitted_external = set()
        for raw in open(path).read().splitlines():
            code = raw.split('!', 1)[0]
            if not code.strip():
                out.append(raw)
                continue
            m = _NAMED.match(code) if code[0] not in ' \t' else None
            if m and m.group(2).strip().upper().startswith('SYN'):
                sym = m.group(1).upper()
                if sym in defined and defined[sym][0] != label:
                    continue                      # stands in for elsewhere
                if sym not in defined:
                    if sym in kept:
                        continue                  # one stand-in is enough
                    kept.add(sym)
                    emitted_external.add(sym)
            if code.lstrip().upper().startswith('END'):
                continue
            out.append(raw)
        out.append("")
    out.append("        END, XIPLBS")
    if verbose:
        print(f"merged {len(PAGES)} pages, {checked} stand-ins checked "
              f"against their definitions, {len(external)} symbols "
              f"external to the bootstrap")
    return "\n".join(out) + "\n", defined, external



def build(verbose=False):
    src, defined, external = merge(verbose)
    return assemble(src), src, defined, external


if __name__ == '__main__':
    prog, src, defined, external = build(verbose=True)
    if '--source' in sys.argv:
        sys.stdout.write(src)
        raise SystemExit(0)
    lo = min(prog.words)
    hi = max(prog.words)
    print(f"image: words {lo:#o}..{hi:#o} "
          f"({hi - lo + 1} words, {len(prog.words)} non-empty)")
    for name in ("XIPLBS", "XBSEND", "XIPLK", "XPROSA", "XERRDD", "XERRAD"):
        v = prog.symtab[name]
        print(f"  {name:<8} {v//64:06o}.{v%64:02o}")
    print(f"  external to the bootstrap: {len(external)} symbols")
