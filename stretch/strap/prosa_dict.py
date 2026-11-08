#!/usr/bin/env python3
"""prosa_dict.py -- RECONSTRUCTION of MCP's PROSA dictionary and index
(type areas 11A11DIC and 11B11IND), and the overlay type areas placed
after MCP.

>>> THIS IS A RECONSTRUCTION, labelled as AGENTS.md and
>>> docs/programming_environment.md require.  IBM's system build
>>> (UPDATE-30) made these two type areas; no listing of them exists.
>>> The FORMATS are IBM's, read in the ink.  The CONTENTS are computed
>>> here from the transcribed listing.  Every choice the documents
>>> leave open is marked CHOSEN below. <<<

SOURCES, each read in the ink unless a line says otherwise
----------------------------------------------------------
C22-6728 (the -0 edition of the MCP Systems Analysis Guide), printed
p.164 = PDF p.164, "PROSA Controls":

  * the dictionary "consists of as many arcs as necessary to provide
    a two word entry for each type area".  Word 1: TYPE bits 0-11,
    AREA bits 12-47, "the type area name in A6 code".  Word 2: ARC
    bits 0-11, WORD bits 12-20, SIZE bits 28-45.  "all entries for a
    given type occur on a single arc of the dictionary.  The
    dictionary is in alphanumeric order by type area."
  * the index "contains a one word entry for each type": TYPE bits
    0-11, ARC bits 32-43, WORD bits 44-52, TYPE NO. bits 56-63.  "The
    arc word address is that of the first dictionary entry for the
    type.  The type number is the number of areas listed under that
    type in the dictionary.  The disk address of the index is
    contained in the second dictionary entry."

The -1 edition (C22-6728-1, PDF p.178) describes a later scheme with
a "short dictionary" set by IPL.  The March 1963 listing's code is
the -0 scheme: an index search, and then a dictionary search.  So the
-0 edition is the authority here.

C22-6728 printed p.96, master tape: the order of the first four type
areas "is always the same": 11A11DIC, 11B11IND, 11C11IPL, 11D11MCP.

THE CODE THAT READS THEM fixes what the prose leaves open (MCP
listing, transcribed in decks/mcp_bootstrap_p*.strap):

  * printed p.317 lines 23-44, C NDX F.  It reads dictionary arc 0 in
    full (CWDCRD, "XW,CDSKBF,512").  It takes the index's ARC from
    "L(BU,12),CDSKBF+3.0": word 2 of the SECOND entry.  It reads the
    index with "CW,CINDEX,40,0" FROM THE START OF THAT ARC.
    So, DERIVED: the index starts on an arc boundary, it is 40 words,
    and the dictionary in front of it fills whole arcs.
  * printed p.316 lines 44-50, X SQ SCH.  A sequential search of all
    40 index words, comparing value fields (bits 0-23).  Unused index
    words must therefore never match a type: they are ZERO.
  * printed p.312 lines 27-42, C RODE.  The dictionary search for a
    type starts at its index entry's WORD (bits 44-52).  It is bounded
    by the NEXT index entry's WORD, and a zero there goes to C NARK
    (printed p.314 line 47, "LVI,6,510.0", the end of the arc).  So
    the index is in dictionary order and is zero after the last type.
  * printed p.317 lines 1-12, X 2WD LK.  A sequential, two-word
    stride compare of the 48-bit name.  The ORDER within a type does
    not affect a search.
  * printed p.4 lines 19-27, the IPL bootstrap.  It reads X BUFER+1,
    +3, +5 and +7, word 2 of dictionary entries 0-3, as index words
    and uses their count fields (bits 28-45 = SIZE).  "LVS,$X1,$X12,
    $X14 -WORDS PRECEEDING MCP" sums the DICTIONARY and INDEX sizes.
    So the IPL type area follows the index with no gap, and MCP
    follows the IPL (printed p.15 line 17 sums three).

CHOSEN, and why each is harmless to the code above
---------------------------------------------------
  * the order of the type areas after 11D11MCP is the dictionary's
    own order.  No reader depends on it.
  * type areas are packed with no gap (C22-6728 printed p.163: "The
    requested material does not have to start at an arc boundary").
    IBM's UPDATE-30 may have aligned major packages to arcs; the
    documents do not say.
  * "alphanumeric order" is taken as the order of the A6 code VALUES.
    IBM's collating sequence differs from code order for digits and
    specials, but no search here depends on order within a type.
    Across types, 11 sorts before 22 either way.
  * the name codes come from strap/charsets.py's 48-character set,
    the same table strap_asm uses to assemble MCP's own request
    (printed p.269 line 24, "(AX)DD(BU,12,6),22X", and line 48,
    "(AX)DD(BU,36,6),SCOMD X").  The two sides are therefore
    consistent by construction.  Neither is checked against a printed
    bit, since no listing prints A-mode bits (charsets.py).

WHAT IS IN PROSA, from the listing's PUNID cards
------------------------------------------------
  11A11DIC, 11B11IND  this file
  11C11IPL            printed pp.15-36 + the IPL cards (prosa.py)
  11D11MCP            printed pp.99-319, the resident body (prosa.py)
  22LOADER            printed pp.320-334, assembled at Y MPBUF
  22$DUMP             printed pp.335-360, at Y MPBUF
  22SCOMD             printed pp.361-380, at Y MPBUF
  22$EOJ              printed pp.381-439, at Y PPMEM (020000)

Not included: 33RESTRT.  C22-6678-1 printed p.40 lists a Restart type
area, but no deck in the March 1963 listing carries that PUNID.  Also
not included: 11E11BSP, the bootstrap, which is the tape's FIRST file
(C22-6728 printed p.96).

>>> THE LOADER HAS A HOLE.  Printed p.329 (235112.00-235153.40) is not
in the scan (mcp_image.MISSING_PAGES).  Its 34 words carry GAP_TAG
plus their own address.  The loader must not be run (E4) until that
page is found. <<<
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import charsets                                            # noqa: E402
import mcp_image                                           # noqa: E402

ARC_WORDS = 512                 # an arc; printed p.317's CWDCRD
INDEX_WORDS = 40                # printed p.317 line 47, "CW,CINDEX,40,0"

GAP_TAG = 0x6A6A000000000000    # a word the scan lost; low bits = address

# printed p.319 line 14: "Y MPBUF DRZ(BU),1088"; p.269 line 11 Y PPMEM.
YMPBUF = 0o234424
YMPBUF_END = YMPBUF + 1088
YPPMEM = 0o020000
RESIDENT = (99, 319)
# (name, first printed page, last printed page, origin)
OVERLAYS = (("22LOADER", 320, 334, YMPBUF),
            ("22$DUMP ", 335, 360, YMPBUF),
            ("22SCOMD ", 361, 380, YMPBUF),
            ("22$EOJ  ", 381, 439, YPPMEM))
# printed p.329, missing from the scan: mcp_image.MISSING_PAGES.
LOADER_GAP = set(range(0o235112, 0o235153 + 1))


def a6(name):
    """An eight-character type-area name as a 48-bit A6 code."""
    assert len(name) == 8, repr(name)
    v = 0
    for ch in name:
        v = (v << 6) | charsets.A[ch]
    return v


def dict_entry(name, arc, word, size):
    """C22-6728 printed p.164, the two-word dictionary entry.
    IBM bit 0 is the most significant bit of the 64-bit word."""
    assert 0 <= arc < 4096 and 0 <= word < 512 and 0 <= size < 2 ** 18
    return [a6(name) << 16,
            (arc << 52) | (word << 43) | (size << 18)]


def index_entry(type2, arc, word, count):
    """C22-6728 printed p.164, the one-word index entry."""
    assert 0 <= count < 256
    return ((a6(type2 + "      ") >> 36) << 52) | (arc << 20) | (word << 11) | count


def _pages(a, b):
    skip = mcp_image.NO_DECK_PAGES | mcp_image.MISSING_PAGES
    return [(mcp_image.DECK("mcp_bootstrap_p%d.strap" % n), "printed p.%d" % n)
            for n in range(a, b + 1) if n not in skip]


def overlay_program(first, last):
    """The resident pages plus one overlay's, assembled together."""
    return mcp_image.build(False, _pages(*RESIDENT) + _pages(first, last),
                           end_at="SDISP")[0]


def overlay_image(first, last, origin):
    """The overlay's own words, from its origin to the last word one of
    its statements wrote: (words, gap_addresses)."""
    prog = overlay_program(first, last)
    if origin == YMPBUF:
        lo, hi = YMPBUF, YMPBUF_END
    else:
        lo, hi = origin, 0o215000
    written = [a for a in prog.written_words if lo <= a < hi]
    end = max(written)
    words, gaps = [], []
    for a in range(origin, end + 1):
        if a in LOADER_GAP and first <= 329 <= last:
            words.append(GAP_TAG | a)
            gaps.append(a)
        else:
            # a reservation or unwritten fill reads as zero, as a DRZ does
            words.append(prog.words.get(a, 0) if a in prog.written_words else 0)
    return words, gaps


def build(ipl_area_words, mcp_words):
    """The PROSA record from its first word: dictionary, index, IPL area,
    MCP, overlays.  Returns (words, layout), where layout maps each name
    to (offset, size)."""
    areas = [("11C11IPL", ipl_area_words), ("11D11MCP", mcp_words)]
    overlays = {name: overlay_image(a, b, o)[0] for name, a, b, o in OVERLAYS}
    names = ["11A11DIC", "11B11IND"] + [n for n, _ in areas] + sorted(overlays, key=a6)
    # the four the tape order fixes come first in code order too
    assert names[:4] == sorted(names[:4], key=a6) and names[:4] == sorted(names, key=a6)[:4]
    n_entries = len(names)
    dict_words = -(-2 * n_entries // ARC_WORDS) * ARC_WORDS
    sizes = {"11A11DIC": dict_words, "11B11IND": INDEX_WORDS}
    sizes.update(dict(areas))
    sizes.update({n: len(w) for n, w in overlays.items()})
    order = ["11A11DIC", "11B11IND", "11C11IPL", "11D11MCP"] + \
        [n for n in names[4:]]
    layout, at = {}, 0
    for n in order:
        layout[n] = (at, sizes[n])
        at += sizes[n]
    total = at
    # The index's place is derived, not chosen: printed p.317 reads it
    # from the start of an arc.
    assert layout["11B11IND"][0] % ARC_WORDS == 0
    # The bootstrap's LVS adds value fields whose bits 18-23 are a BIT
    # address; word 2's WORD field reaches bit 20.  For the index and
    # the IPL that must be zero, i.e. their offsets are multiples of 8.
    for n in ("11A11DIC", "11B11IND", "11C11IPL"):
        assert layout[n][0] % 8 == 0, n

    dictionary = []
    for n in names:
        off, size = layout[n]
        dictionary += dict_entry(n, off // ARC_WORDS, off % ARC_WORDS, size)
    assert len(dictionary) <= ARC_WORDS, "the dictionary outgrew one arc"
    dictionary += [0] * (dict_words - len(dictionary))

    index, seen = [], {}
    for k, n in enumerate(names):
        t = n[:2]
        if t not in seen:
            seen[t] = len(index)
            index.append([t, (2 * k) // ARC_WORDS, (2 * k) % ARC_WORDS, 0])
        index[seen[t]][3] += 1
    index_words = [index_entry(*e) for e in index]
    assert len(index_words) < INDEX_WORDS     # a zero entry ends C RODE
    index_words += [0] * (INDEX_WORDS - len(index_words))

    words = [None] * total
    words[0:dict_words] = dictionary
    off = layout["11B11IND"][0]
    words[off:off + INDEX_WORDS] = index_words
    for n, w in overlays.items():
        off = layout[n][0]
        words[off:off + len(w)] = w
    return words, layout


if __name__ == "__main__":
    for name, a, b, o in OVERLAYS:
        w, gaps = overlay_image(a, b, o)
        print(f"{name!r}: printed pp.{a}-{b}, origin {o:06o}, {len(w)} words, "
              f"{len(gaps)} gap words")
