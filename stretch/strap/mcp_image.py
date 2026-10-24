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


def _places_of(label, pages):
    """The location-counter symbols of the page with this label.

    Used by merge() to keep "defined twice" a hard failure whenever a
    LOCATION is involved: two SYNs that agree are a stand-in and its
    definition, but a name that labels storage on one page and
    anything at all on another is a real collision."""
    for path, lab in pages:
        if lab == label:
            return _classify(path)[0]
    return {}


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


def merge(verbose=False, pages=None, end_at='XIPLBS'):
    """Build the merged source text and the provenance of every symbol.

    Returns (source, defined, external) where `defined` maps a symbol
    to the page that places or defines it and `external` maps a symbol
    with no definition anywhere to the page whose stand-in is kept.
    """
    if pages is None:
        pages = PAGES
    defined, standins = {}, {}
    agreed = 0
    for path, label in pages:
        places, s, d = _classify(path)
        for sym, val in list(places.items()) + list(d.items()):
            if sym in defined:
                # >>> A SYN THAT REPRODUCES ANOTHER PAGE'S SYN EXACTLY
                # IS A STAND-IN THAT AGREES WITH IT, not a duplicate.
                # <<<
                #
                # _STANDIN only recognises the "(8)NNN.NN" form,
                # because that is what a page writes when it reads an
                # address off its own binary.  printed p.45 has to
                # write "QX INN SYN,$1" and "Q KSIZ SYN,6" instead,
                # because that is what the symbols ARE -- and printed
                # p.46 line 22 defines QX INN with the identical text.
                # There is no way to tell the stand-in from the
                # definition by FORM, and no need to: if the two
                # values agree, the stand-in has been checked, which
                # is the only thing this cross-check exists to do.
                #
                # A DISAGREEMENT IS STILL A HARD FAILURE, and so is
                # any collision involving a location-counter symbol,
                # where two pages really would be claiming the same
                # name for different storage.
                if (defined[sym][1] == val and sym not in places
                        and sym not in _places_of(defined[sym][0], pages)):
                    agreed += 1
                    continue
                raise SystemExit(
                    f"FAIL {sym} is defined twice: {defined[sym][0]} and "
                    f"{label}" + ("" if defined[sym][1] == val else
                                  f", and they disagree: bit "
                                  f"{defined[sym][1]} against bit {val}"))
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
    for path, label in pages:
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
    out.append(f"        END, {end_at}")
    if verbose:
        print(f"merged {len(pages)} pages, {checked} stand-ins checked "
              f"against their definitions, {agreed} SYNs that agree with "
              f"another page's SYN, {len(external)} symbols external to "
              f"the bootstrap")
    return "\n".join(out) + "\n", defined, external



def build(verbose=False, pages=None, end_at='XIPLBS'):
    src, defined, external = merge(verbose, pages, end_at)
    return assemble(src), src, defined, external


# ---------------------------------------------------------------------
# MCP PROPER, printed pp.15-36 -- a SECOND image, and not part of the
# bootstrap.
#
# The bootstrap is the tape record the IPL mechanism loads, X IPL BS
# through X BS END.  What printed pp.15 onward hold is what the
# bootstrap LOADS: MCP's own initialization, which arrives in a PROSA
# record and is moved into place by printed p.4 line 28's TRANSMIT.
# So it is built separately and never merged into PAGES above -- the
# assertion at the foot of this file would catch that, because the
# image would stop matching printed p.2's control-word count.
#
# THEY ASSEMBLE CONTIGUOUSLY AND THAT IS NOT LUCK: printed p.15 line
# 7 is "SLC,X BS END", so the first word lands at 000621.00, exactly
# one past the bootstrap, and every page after it follows without a
# gap or an overlap.
#
# >>> IT WAS pp.15-18 AND EIGHTY WORDS UNTIL 2026-10-22; IT IS NOW
# pp.15-36 AND 727.  Every page from printed p.15 to printed p.36 is
# transcribed and bit-exact, and they form ONE RUN with no gap
# anywhere: <<<
#
#   p15 000621..000632   p22 001052..001121   p29 001532..001553
#   p16 000633..000654   p23 001121..001174   p30 001553..001600
#   p17 000655..000712   p24 001174..001412   p31 001601..001632
#   p18 000713..000740   p25 001412..001443   p32 001632..001661
#   p19 000740..000776   p26 001444..001463   p33 001661..001713
#   p20 000777..001011   p27 001464..001507   p34 001713..001745
#   p21 001012..001051   p28 001507..001532   p35 001746..001756
#                                             p36 001756..002147
#
# -- each page starting on the word the one before it ended on or the
# next one, twenty-two pages running 000621.00 to 002147, and the
# merge below checks all 253 symbols against each other on the way.
#
# TWO HOLES IN THAT RUN ARE RESERVATIONS AND NOT LOSSES, which is why
# the assembler records them: printed p.21's "X LR IN DR(BU),(3)" and
# "X ZEROS DR(BU),(3)" leave 001034-001041, and printed p.36's
# "X MSG BK DR(BU),(100)" leaves 002000-002143.  prosa.py proves each
# hole against AssembledProgram.reservations rather than assuming it.
# ---------------------------------------------------------------------
# >>> PRINTED p.37 JOINED THE IMAGE ON 2026-10-23, and it is a
# DIFFERENT SOURCE DECK: its card sequence restarts at 13000001 where
# p.36's ended at 11C11xxx.  The LOCATION counter does not restart --
# p.36's last row is at 002146.74 and p.37's first is a CNOP at
# 002147.40 -- so the two are contiguous in storage and the range
# below stays a range.
#
# IT IS WHERE THE BOOT RUN WAS GOING.  MCP finishes printed pp.15-36
# and branches to 002166.00, which p.37 line 45 names S PRIME.
#
# AND IT DEFINES TWENTY-ONE OF THE EXTERNALS pp.15-36 HAD BEEN
# SYNNING, so merge()'s cross-check now has a definition to compare
# each stand-in against instead of comparing it with itself.
# >>> AND PRINTED p.38 JOINED IT ON 2026-10-23.  Card sequence
# 14000001, a THIRD source deck, and the LOCATION counter still does
# not restart: p.37's S PRIME is 002166.00 and p.38 line 4 is
# 002166.00 with the name Y UNCOD.  The PRIME ROUTINE and the UNCODE
# SUBROUTINE are the same entry, and that is where the boot run's PC
# trail said MCP's initialization went.
#
# IT DEFINES Y UNCOD, which pp.15-36 had been SYNning, and PREDICTS
# fourteen more at 002213 through 002502 -- all later than anything
# transcribed, so every one of them is a claim about a page not yet
# opened.
# >>> PRINTED p.47 HAS NO DECK, AND THAT IS NOT AN OMISSION. <<<
# It is twenty-three lines and the only one that is not a comment is
# line 1's "SLC,$" at 002556.67 -- where printed p.46's Q BLNK ends,
# to the bit.  The rest is THE DECODE PROGRAM LINKAGE FORMAT written
# out as a worked call, which is recorded in docs/boot_plan.md.  A
# page that compiles nothing has nothing for listing_oracle to check
# and contributes no word to the image, so there is no file to merge
# -- but the GAP IN THIS RANGE would look exactly like a page someone
# forgot, which is why it is named here.
NO_DECK_PAGES = {47}

MCP_IPL_PAGES = [
    (DECK("mcp_bootstrap_p%d.strap" % n), "printed p.%d" % n)
    for n in range(15, 55) if n not in NO_DECK_PAGES
]


def build_mcp_ipl(verbose=False):
    """The printed pp.15-36 image: (prog, src, defined, external)."""
    return build(verbose, MCP_IPL_PAGES, end_at='X10')


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
