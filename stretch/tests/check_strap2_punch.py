#!/usr/bin/env python3
"""check_strap2_punch.py -- STRAP II's absolute binary deck (strap/strap2/punch.py).

Sources, read in the ink 2026-11-09: C28-6129 pp.22-23 (PDF 26-27) for the
origin, flow and branch cards, with N28-1081's errata (page 18, PDF p.76:
"0 to 736", "through 71", the branch card's corrected columns, END with no
address branching to 41.8); C22-6729 chart OV p.155 (DR) and charts OP, OS.
The column and row convention, and the check sum, are MCP's loader as
docs/bss_loader_spec.md reads it (listing printed pp.320-334), AS READ: no
loader path has run on the model yet.

What is checked, and how strong each oracle is:
  A  every deck in decks/: the cards are encoded to columns, DECODED HERE from
     the columns alone (not by punch.py), loaded as the loader's absolute path
     does, and the result compared with the assembled image bit for bit, with
     the branch address against END.  Strong: any lost, moved or extra bit shows.
  B  the card fields of Appendix E's deck, by hand from C28 pp.22-23.
  C  what each event does to the deck: a full origin card, then flow cards; DRs
     in a row adding up; a DRZ zeroing; a DR after a DRZ punched apart; END
     with no address, by both editions.
  D  PUNFUL is not written: the assembly goes on and `images` refuses.
The card-close lines against the two printed listings are in
check_strap2_listing.py (DERIVED: the prints' second '*').

MEASURED INJECTIONS, 2026-11-09, PYTHONDONTWRITEBYTECODE=1, each restored from a
saved copy and compared; control all passing here and in check_strap2_listing.py
(whose failures are given after the bar):
  origin card 748 bits (the 1961 text):    C1 | p.48 marks
  flow card 736 bits:                      A1, A2, C1
  data from 10.7, not 10.8:                A1, A2, B3
  sequence from 0:                         A1, A2, B2, B4
  check sum without column 1:              A1, A2
  zero flag inverted:                      A1, A2, B2
  rows reversed in a column:               A1, A2, B1-B4
  DRs in a row not added:                  A1, A2 | p.48 marks
  a DR after data waits to punch:          A1, A2, B2, C4, C5 | both pages' marks
  END with no address to the first origin: C2
  no punch after the last unit:            A1, A2
  a gap in the counter starts a new card:  C1 | p.48 marks
  the mark on the last line, not located:  | both pages' marks
"""
import glob
import os
import sys
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
import strap_asm                                  # noqa: E402
from strap2 import compile_cards                  # noqa: E402
from strap2.cards import deck_cards               # noqa: E402
from strap2.punch import PunchError               # noqa: E402

fails = 0


def check(label, got, want):
    global fails
    if got == want:
        print(f"PASS {label}")
    else:
        fails += 1
        print(f"FAIL {label}: got {got!r}, want {want!r}")


def card(name, stmt):
    return " " + name.ljust(8) + stmt


def checksum(cols):
    """Written here from docs/bss_loader_spec.md 5.3, apart from punch.py: the
    12-bit columns 1, 2, 3 and 5 through 71 added, then the high part folded
    into the low with its carry."""
    total = sum(cols[c - 1] for c in (1, 2, 3)) + sum(cols[c - 1] for c in range(5, 72))
    while total > 0o7777:
        total = (total & 0o7777) + (total >> 12)
    return total


def field(cols, at, n):
    """n bits from card bit `at`: column c, row r is bit 12(c-1)+r."""
    v = 0
    for k in range(at, at + n):
        v = (v << 1) | ((cols[k // 12] >> (11 - k % 12)) & 1)
    return v


def decode_and_load(images):
    """The loader's absolute path, from the columns.  Returns the bits loaded,
    the branch address, and a list of complaints (class, sequence, check sum)."""
    mem, at, branch, bad = {}, None, None, []
    for seq, cols in enumerate(images, 1):
        if field(cols, 24, 12) != seq:
            bad.append(f"card {seq}: sequence {field(cols, 24, 12)}")
        if cols[3] != checksum(cols):
            bad.append(f"card {seq}: check sum")
        kind = {0o7: "origin", 0o5: "flow", 0o15: "branch"}.get(cols[0] & 0o17)
        if cols[0] >> 4 or kind is None:
            bad.append(f"card {seq}: column 1 {cols[0]:04o}")
            continue
        if kind == "branch":
            branch = field(cols, 60, 24)
            continue
        if kind == "origin":
            zero, after, n = field(cols, 48, 1), field(cols, 49, 1), field(cols, 50, 10)
            at, skip, data = field(cols, 60, 24), field(cols, 84, 24), 116
        else:
            zero = after = skip = 0
            n, data = 800, 52
        if skip and not after:
            for k in range(skip if zero else 0):
                mem[at + k] = 0
            at += skip
        for k in range(n):
            mem[at + k] = field(cols, data + k, 1)
        at += n
        if skip and after:
            for k in range(skip if zero else 0):
                mem[at + k] = 0
            at += skip
    return mem, branch, bad


def image_differences(p2, mem):
    im, bad = p2.image, 0
    for src in (im._written, im._fill):
        for w, m in src.items():
            for b in range(64):
                if m >> (63 - b) & 1 and mem.get(w * 64 + b) != (im.words.get(w, 0) >> (63 - b)) & 1:
                    bad += 1
    for k, v in mem.items():
        if v != (im.words.get(k // 64, 0) >> (63 - k % 64)) & 1:
            bad += 1
    return bad


def one(path):
    base = os.path.basename(path)
    try:
        p2 = compile_cards(deck_cards(open(path).read()), strap_asm.DEFAULT_ORIGIN_BITS)
    except Exception:          # noqa: BLE001  refusing to assemble is not ours
        return base, "not assembled", ""
    if p2.punch.unwritten:
        return base, "unwritten", p2.punch.unwritten
    mem, branch, bad = decode_and_load(p2.punch.images(clock=0o1234))
    diff = image_differences(p2, mem)
    want = None if p2.end_pc is None else p2.end_pc * 32
    if bad or diff or (want is not None and branch != want):
        return base, "differs", f"{bad[:2]} {diff} bits, branch {branch} want {want}"
    return base, "same", ""


# A. Every deck.
if __name__ == "__main__":
    counts, unwritten = {}, []
    with ProcessPoolExecutor() as ex:
        for base, how, detail in ex.map(one, sorted(glob.glob(os.path.join(HERE, "..", "decks", "*.strap")))):
            counts[how] = counts.get(how, 0) + 1
            if how == "differs":
                print(f"   {base}: {detail}")
            if how == "unwritten":
                unwritten.append((base, detail))
    check("A1 decks whose cards load to their image", counts.get("same", 0), 725)
    check("A2 none differ", counts.get("differs", 0), 0)
    check("A3 the five that stop at PUNFUL or PUNORG", sorted(unwritten),
          [("mcp_bootstrap_p320.strap", "PUNFUL"), ("mcp_bootstrap_p335.strap", "PUNFUL"),
           ("mcp_bootstrap_p361.strap", "PUNFUL"), ("mcp_bootstrap_p381.strap", "PUNFUL"),
           ("mcp_bootstrap_p99.strap", "PUNORG")])

    # B. Appendix E's deck, field by field.
    sys.path.insert(0, HERE)
    src = open(os.path.join(HERE, "check_strap2_listing.py")).read()
    ns = {}
    exec(src[src.index("APPE_CARDS = ["):src.index("# Every field as printed.")], {"card": card}, ns)
    p2 = compile_cards(ns["APPE_CARDS"])
    cards = p2.punch.images(clock=0o5162)
    check("B1 four cards: three origin, then the branch",
          [c[0] for c in cards], [0o7, 0o7, 0o7, 0o15])
    c1 = cards[0]
    check("B2 card 1: ID, sequence, zero, after, count, origin, skip",
          (c1[1], c1[2], field(c1, 48, 1), field(c1, 49, 1), field(c1, 50, 10),
           field(c1, 60, 24), field(c1, 84, 24)),
          (0o5162, 1, 0, 1, 576, 0o100 * 64, 64))
    check("B3 card 1's first data bits are ABLE's LX at 10.8",
          field(c1, 116, 32), p2.image.words[0o100] >> 32)
    check("B4 the branch card: sequence 4, to ABLE", (cards[3][2], field(cards[3], 60, 24)),
          (4, 0o100 * 64))
    check("B5 columns 72-80 blank", [c[71:] for c in cards], [[0] * 9] * 4)

    # C. Events.
    long = compile_cards([card("", "SLC,64.")] + [card("", "B,0")] * 60 + [card("", "END")])
    check("C1 60 half-words: origin 23, flow 25, origin 12, branch",
          [(c.kind, c.nbits) for c in long.punch.cards],
          [("origin", 736), ("flow", 800), ("origin", 384), ("branch", 0)])
    check("C2 END with no address goes to 41.8 (N28-1081 errata)",
          long.punch.cards[-1].address, 0o41 * 64)
    old = compile_cards([card("", "SLC,64."), card("", "B,0"), card("", "END")], edition="C28-6129")
    check("C3 by the 1961 text, to the first origin", old.punch.cards[-1].address, 0o100 * 64)
    drs = compile_cards([card("", "SLC,64."), card("", "B,0"), card("", "B,0"),
                         card("", "DR(N),2"), card("", "DR(N),3"), card("", "B,0"),
                         card("", "END,0")])
    check("C4 a DR after data: skip after; a DR in a row: added, before the next",
          [(c.kind, c.nbits, c.skip, c.after) for c in drs.punch.cards],
          [("origin", 64, 128, True), ("origin", 32, 192, False), ("branch", 0, 0, False)])
    z = compile_cards([card("", "SLC,64."), card("", "B,0"), card("", "B,0"),
                       card("", "DRZ(N),1"), card("", "DR(N),1"), card("", "B,0"),
                       card("", "END,0")])
    check("C5 DRZ zeroes; a DR after a DRZ goes on a card of its own",
          [(c.nbits, c.skip, c.zero, c.after) for c in z.punch.cards if c.kind != "branch"],
          [(64, 64, True, True), (32, 64, False, False)])

    # D. Not written.
    pf = compile_cards([card("", "SLC,64."), card("", "B,0"), card("", "PUNFUL"),
                        card("", "B,0"), card("", "END,0")])
    try:
        pf.punch.images()
        check("D1 PUNFUL: images refuse", "accepted", "PunchError")
    except PunchError:
        check("D1 PUNFUL: images refuse", "PunchError", "PunchError")

    print("punch: FAILED" if fails else "punch: all passed")
    sys.exit(1 if fails else 0)
