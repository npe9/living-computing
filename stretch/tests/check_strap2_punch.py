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
  D  PUNREL is not written: the assembly goes on and `images` refuses.
  E  the MCP cards, C22-6678-1 pp.7-10 read in the ink: GO and LIM first (guide
     p.157 boxes 15-16), the IOD of p.48 reproduced with its reference number and
     exit word, a REEL as submitted, the card code by hand from App. F p.56, and
     binary sequence numbers counting binary cards alone.  LIM's bounds for p.48
     are DERIVED (no print of p.48's deck survives).
  F  chart OR (C22-6729 p.151), read in the ink 2026-11-10, with C28-6129
     pp.13, 36-37, 39 (PDF 17, 40-41, 43) and N28-1081's errata page 19 (NOPUN ends at
     any punch pseudo-op): PUNID punches the card in process and stores the ID
     (MPUNID, guide p.27: blanks significant, padded to eight) for columns 73-80;
     TLB an origin card and a branch card, the next card an origin card; NOPUN
     suppresses until PUNNOR.
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
MEASURED 2026-11-10, the same way, for E (A-D passing in each):
  IOD exit in bits, not words:             E3, E6
  no GO card:                              E1, E2, E8
  LIM n1 from the default origin 41:       E7
  undefined symbols' words not in n2:      E7
  sequence numbers count control cards:    E5
  control cards after all the binary:      E1, E4, E5, E8
  reference number 3 decimal digits:       E3, E4, E6
  name not reproduced:                     E3
  an IOD past column 62 accepted:          E9
MEASURED 2026-11-10 for F (A-E passing in each but where named):
  PUNID does not punch the card in process: F9
  TLB leaves the origin indicator off:     F10
  NOPUN does not suppress:                 F1, F2
  PUNNOR does not end NOPUN:               F1, F2
  ID inside the check sum:                 A1, A2 (problem_1_5_method1 has a PUNID), F4
  ID in columns 72-79:                     F3
  TLB address not printed:                 F5
  MPUNID without Gcaz:                     F2, F3
  no message 55:                           F7
  TLB with no address to the first origin: F6
  SLCR does not stop punching:             F11
  SLC does not restore punching:           F11
  SLCR keeps the card in process:          F12
  NOSEQ does not punch the card in process: F13, F14
  NOSEQ ignored:                           F13, F14
  RESEQ does not clear the count:          F13
  RESEQ leaves NOSEQ on:                   F13
  PUNORG ignored:                          F15
  PUNNOR does not end PUNORG:              F15
  PUNORG does not end NOPUN:               F16
  PUNORG keeps the card in process:        F17
  the count advanced under NOSEQ:          none, and none can: only RESEQ ends
                                           NOSEQ, and RESEQ clears the count
  G  PUNFUL (chart OR p.151, OS p.152, OV boxes 1-2 p.158; C28-6129 pp.23, 36)
     and entry mode CC (C28-6129 p.16; App. F p.56), read in the ink 2026-11-10.
     A's decoder skips a card whose column 1 is not a binary card's, as MCP's
     loader cannot load a PUNFUL card (C28 p.23); A5 reads each such card.
     MEASURED (A-F passing but where named):
  CC rows reversed (row 9 high):           G1, G4
  a full card numbered like a binary card: G2
  no 84:                                   G3
  no 79:                                   G3
  an SLC above the counter adds no zeros:  A4, G4
  a DR under PUNFUL adds no zeros:         G4
  PUNNOR does not end PUNFUL:              G4
  PUNORG does not end PUNFUL:              A1, A3, A4, G2
  a short full card dropped:               A4, G1, G2, G4, G5, G7
  no 127:                                  G5
  a low SLC accepted:                      G6
  PUNFUL does not end NOPUN:               G7
  A4-A7: MCP's seven PUNFUL header cards (printed pp.2, 15, 99, 320, 335, 361,
     381), assembled since 2026-11-10 (they were comments or omitted).  The
     A-column entries above were measured when A4 still loaded each full card
     into memory and compared it with the image; since STRAP II keeps PUNFUL
     data out of its image, A4 counts full cards and A5 reads them.  MEASURED
     for the four overlay decks:
  the decks as they were (stand-ins):      A5, A7
  p.320 line 2 one column short:           A5, A7
  strap_asm loads what is under PUNFUL:    A6 (check_mcp_body_image also
                                           fails $DUMP, SCOMD and $EOJ;
                                           LOADER's card is past Y MPBUF)
  CC rows reversed (row 9 high):           A5, G1, G4
  and for all seven:
  pp.2, 15, 99 as they were (omitted):     A4, A5, A7
  STRAP II puts PUNFUL data in its image:  A1, A2, A4, A5 (pp.2 and 15 then
                                           refuse: the program overlays them)
  "1ST SLC" read as "no data yet":         A4 (p.99 punches its SLC's jump
                                           as full cards), G8
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
    seq = 0
    for cols in images:
        kind = {0o7: "origin", 0o5: "flow", 0o15: "branch"}.get(cols[0] & 0o17)
        if cols[0] >> 4 or kind is None:
            continue        # not a binary card: a PUNFUL card, for MCP to read
        seq += 1
        if field(cols, 24, 12) != seq:
            bad.append(f"card {seq}: sequence {field(cols, 24, 12)}")
        if cols[3] != checksum(cols):
            bad.append(f"card {seq}: check sum")
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
    images = p2.punch.images(clock=0o1234)
    mem, branch, bad = decode_and_load(images)
    full = []
    import cards as hollerith
    inv = {hollerith.column_bits(ch): ch for ch in " ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,.()*/$=+-'"}
    for c, cols in zip(p2.punch.cards, images):
        if c.kind == "full":
            # A PUNFUL card is not loaded (C28-6129 p.23), and since 2026-11-10
            # STRAP II keeps what it assembles under PUNFUL out of its image
            # (pass2.unit_b), so the decoded cards and the image agree without
            # it.  A5 checks what the card says.
            full.append("".join(inv.get(x, "?") for x in cols))
    diff = image_differences(p2, mem)
    want = None if p2.end_pc is None else p2.end_pc * 32
    if bad or diff or (want is not None and branch != want):
        return base, "differs", f"{bad[:2]} {diff} bits, branch {branch} want {want}"
    return base, "same", tuple(full)


# A. Every deck.
if __name__ == "__main__":
    counts, unwritten, fulls = {}, [], []
    with ProcessPoolExecutor() as ex:
        for base, how, detail in ex.map(one, sorted(glob.glob(os.path.join(HERE, "..", "decks", "*.strap")))):
            counts[how] = counts.get(how, 0) + 1
            if how == "same" and detail:
                fulls.append((base, detail))
            if how == "differs":
                print(f"   {base}: {detail}")
            if how == "unwritten":
                unwritten.append((base, detail))
    check("A1 decks whose cards load to their image", counts.get("same", 0), 730)
    check("A2 none differ", counts.get("differs", 0), 0)
    check("A3 none stops", sorted(unwritten), [])
    # MCP's seven PUNFUL header cards: the BSP, IPL and MCP decks' (printed pp.2,
    # 15, 99) and the four overlays' (pp.320, 335, 361, 381).  Each is the "B HED,
    # REP, <name>, LOAD,," control card (C22-6678-1 pp.7-10: B in column 1, the
    # statement from column 10, the ID in 73-80), from the decks' own (CC*)DD
    # statements, whose blanks were measured in the ink (the decks' headers).
    # pp.2 and 15 print no blank after the commas.
    names = {"p2": ("11E11BSP", False), "p15": ("11C11IPL", False), "p99": ("11D11MCP", True),
             "p320": ("22LOADER", True), "p335": ("22$DUMP", True), "p361": ("22SCOMD", True),
             "p381": ("22$EOJ", True)}
    deck = lambda pg: f"mcp_bootstrap_{pg}.strap"
    check("A4 the seven MCP decks with PUNFUL open with one full card each",
          sorted((b, len(t)) for b, t in fulls), sorted((deck(pg), 1) for pg in names))

    def hed(nm, sp):
        text = f"HED, REP, {nm}, LOAD,," if sp else f"HED,REP,{nm},LOAD,,"
        return ("B" + " " * 8 + text).ljust(72) + nm.ljust(8)
    check("A5 and reads back as the deck's HED control card",
          sorted((b, t[0]) for b, t in fulls), sorted((deck(pg), hed(*v)) for pg, v in names.items()))

    # The old assembler (strap_asm, scaffolding) on the same decks: what is
    # assembled under PUNFUL moves the counter and loads nothing, and the two
    # header DDs sit at their printed locations (the second is where 45
    # columns of the first end).  On pp.2 and 15 the program is assembled over
    # those addresses afterwards, so A6 looks at pp.99 and the overlays only.
    printed = {"p2": (0o41 * 64, 0o51 * 64 + 0o34), "p15": (0o621 * 64, 0o631 * 64 + 0o34),
               "p99": (0o5466 * 64, 0o5476 * 64 + 0o34),
               "p320": (0o236524 * 64, 0o236534 * 64 + 0o34), "p335": (0o236464 * 64 + 0o31, 0o236474 * 64 + 0o65),
               "p361": (0o236425 * 64 + 0o31, 0o236435 * 64 + 0o65), "p381": (0o235570 * 64 + 0o10, 0o235600 * 64 + 0o44)}
    spans, locs = [], []
    real_iter = strap_asm.iter_statements
    for pg, (a, b) in printed.items():
        seen = []
        strap_asm.iter_statements = lambda src: seen.extend(real_iter(src)) or seen
        try:
            prog = strap_asm.assemble(open(os.path.join(HERE, "..", "decks", deck(pg))).read())
        finally:
            strap_asm.iter_statements = real_iter
        if pg not in ("p2", "p15"):
            spans.append((pg, [w for w in prog.written_words if a // 64 <= w < (a + 960 + 63) // 64]))
        locs.append((pg, [s.addr for s in seen if s.op.upper() == "DD" and (s.entry or "").startswith("CC")]))
    check("A6 strap_asm loads no word of the header cards", spans,
          [(pg, []) for pg in printed if pg not in ("p2", "p15")])
    check("A7 and puts them at their printed locations", locs, [(pg, list(ab)) for pg, ab in printed.items()])

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
    pf = compile_cards([card("", "SLC,64."), card("", "B,0"), card("", "PUNREL"),
                        card("", "B,0"), card("", "END,0")])
    try:
        pf.punch.images()
        check("D1 PUNREL: images refuse", "accepted", "PunchError")
    except PunchError:
        check("D1 PUNREL: images refuse", "PunchError", "PunchError")

    # E. The MCP cards (C22-6678-1 pp.7-10): GO, LIM, then IOD and REEL as
    # submitted at their units, then the binary cards, numbered from 1.
    src = open(os.path.join(HERE, "..", "decks", "mcpref_example2.strap")).read()
    kept = [s for s in src.splitlines()
            if not s.startswith("        SLC, (8)41.0") and not s.startswith("RON     SYN")]
    p48 = compile_cards(["BRON      IOD,TAPE,EXIT,,,ODD,HD,CSAVE", card("", "PRNS")]
                        + deck_cards("\n".join(kept)))
    deck = p48.punch.deck()
    check("E1 p.48: GO, LIM, the IOD, then binary",
          [h for h, _ in deck[:4]], ["text", "text", "text", "binary"])
    check("E2 GO and LIM: B in 1, from 10; p.48 runs 41 to the word after 144",
          [c for _, c in deck[:2]], ["B         TYPE,GO", "B         LIM,000041,000145"])
    iod = next((c for h, c in deck if h == "text" and c.startswith("BRON")), "").ljust(80)
    check("E3 the IOD as submitted, reference 0001 in 63-66, EXIT's word 000114 in 67-72",
          (iod[:62].rstrip(), iod[62:66], iod[66:72], iod[72:].strip()),
          ("BRON      IOD,TAPE,EXIT,,,ODD,HD,CSAVE", "0001", "000114", ""))
    im = p48.punch.deck_images(clock=0o1234)
    k = next(i for i, (h, _) in enumerate(deck) if h == "binary")
    # Hollerith by hand from App. F p.56: B is 12-2, rows 12 and 2; 0 is row 0
    # alone; 1 is row 1; blank is none.  Row 12 high, then 11, 0, 1 ... 9.
    check("E4 the IOD card in the card code: B, 0, 1, blank",
          (im[k - 1][0], im[k - 1][62], im[k - 1][65], im[k - 1][79]), (0o4200, 0o1000, 0o400, 0))
    check("E5 binary cards numbered from 1 after the three",
          [field(c, 24, 12) for c in im[k:]], list(range(1, len(im) - k + 1)))
    m2 = compile_cards(["BX        IOD,TAPE,EXIT", "BY        IOD,DISK,EXIT",
                        "B         REEL,ABC,DEF", card("", "SLC,64."), card("EXIT", "B,0"),
                        card("", "B,Q"), card("", "END,0")])
    t = [c for h, c in m2.punch.deck() if h == "text"]
    check("E6 the second IOD is 0002; REEL has nothing past its statement",
          [x.ljust(80)[62:72] for x in t if "IOD" in x] + [x for x in t if "REEL" in x],
          ["0001000100", "0002000100", "B         REEL,ABC,DEF"])
    check("E7 LIM from the first origin; an undefined symbol's word counted",
          [x for x in t if "LIM," in x], ["B         LIM,000100,000102"])

    late = compile_cards([card("", "SLC,64."), card("EXIT", "B,0"), "B         REEL,ABC",
                          card("", "B,0"), card("", "END,0")])
    check("E8 a REEL after code goes out at its unit, ahead of the card still filling (CHOSEN)",
          [h if h == "binary" else c[10:14] for h, c in late.punch.deck()],
          ["TYPE", "LIM,", "REEL", "binary", "binary"])
    big = compile_cards(["BX       IOD,TAPE,EXIT," + "A" * 40, card("EXIT", "B,0"), card("", "END,0")])
    check("E9 an IOD past column 62 is not written", (big.punch.unwritten or "").startswith("IOD"), True)

    # F. Chart OR (C22-6729 p.151): PUNID, TLB, NOPUN, PUNNOR.
    from strap2.listing import listing_of
    f = compile_cards([card("", "PUNID,AB CD"), card("", "SLC,64."), card("A", "B,0"),
                       card("", "TLB,A"), card("", "B,0"), card("", "NOPUN"), card("", "B,0"),
                       card("", "PUNNOR"), card("", "PUNID,XY"), card("", "B,0"),
                       card("", "END,A")])
    fc = f.punch.cards
    check("F1 the cards: origin, TLB's branch, origin (not flow), NOPUN's B,0 not "
          "punched, origin after PUNNOR, END's branch",
          [(c.kind, c.origin // 32 if c.kind != "branch" else c.address // 32) for c in fc],
          [("origin", 0o200), ("branch", 0o200), ("origin", 0o201), ("origin", 0o203),
           ("branch", 0o200)])
    check("F2 the ID on each card: PUNID punches the card in process first",
          [c.ident for c in fc], ["AB CD   "] * 3 + ["XY      "] * 2)
    fi = f.punch.images(clock=0)
    # By hand from App. F p.56: A 12-1, B 12-2, C 12-3, D 12-4; row 12 high.
    check("F3 columns 73-80 in the card code", fi[0][72:80],
          [0o4400, 0o4200, 0, 0o4100, 0o4040, 0, 0, 0])
    mem, branch, bad = decode_and_load(fi)
    check("F4 the ID is outside the check sum", bad, [])
    fl = listing_of(f, f.p1.print_names)
    check("F5 the TLB line prints its address (chart OR: store TLB address in print line)",
          [(ln.location, ln.binary) for ln in fl.lines if ln.statement == "TLB,A"],
          [("000100.40", "000100.00")])
    t0 = compile_cards([card("", "SLC,64."), card("", "B,0"), card("", "SLC,128."), card("", "B,0"),
                        card("", "TLB"), card("", "B,0"), card("", "END,0")])
    check("F6 TLB with no address goes to 41.8 (N28-1081 errata), not the first origin",
          [c.address for c in t0.punch.cards if c.kind == "branch"], [0o41 * 64, 0])
    nc = compile_cards([card("", "PUNID"), card("", "SLC,64."), card("", "B,0"), card("", "END,0")])
    check("F7 PUNID with no comma: 55, and no ID",
          ([m[0] for m in nc.msg.items], [c.ident for c in nc.punch.cards]), ([55], [None, None]))
    lp = compile_cards([card("", "PUNID,ABCDEFGHIJ"), card("", "SLC,64."), card("", "B,0"),
                        card("", "END,0")])
    check("F8 eight characters kept", lp.punch.cards[0].ident, "ABCDEFGH")

    fl2 = compile_cards([card("", "PUNID,P"), card("", "SLC,64."), card("", "B,0"),
                         card("", "PUNID,Q"), card("", "B,0"), card("", "END,0")])
    check("F9 a PUNID between contiguous data: two cards, each with its own ID",
          [(c.kind, c.nbits, (c.ident or "").strip()) for c in fl2.punch.cards],
          [("origin", 32, "P"), ("origin", 32, "Q"), ("branch", 0, "Q")])
    full = compile_cards([card("", "SLC,64.")] + [card("", "B,0")] * 23
                         + [card("", "TLB,0")] + [card("", "B,0")] * 25 + [card("", "END,0")])
    check("F10 after TLB, an origin card, even after a full one",
          [(c.kind, c.nbits) for c in full.punch.cards],
          [("origin", 736), ("branch", 0), ("origin", 736), ("origin", 64), ("branch", 0)])

    rel = compile_cards([card("", "SLC,64."), card("", "B,0"), card("", "SLCR,0"),
                         card("P", "DD(BU,24,8),0"), card("", "B,0"), card("", "SLC,128."),
                         card("", "B,P"), card("", "END,0")])
    check("F11 SLCR: the card goes out, nothing until the next SLC (guide p.36)",
          [(c.kind, c.origin // 32, c.nbits) for c in rel.punch.cards if c.kind != "branch"],
          [("origin", 0o200, 32), ("origin", 0o400, 32)])
    check("F12 the card in process is punched at the SLCR's own unit (CHOSEN)",
          rel.punch.events[0][0], list(rel.units.intin())[2])

    sq = compile_cards([card("", "SLC,64."), card("", "B,0"), card("", "B,0"), card("", "NOSEQ"),
                        card("", "B,0"), card("", "RESEQ"), card("", "B,0"), card("", "END,0")])
    si = sq.punch.images(clock=0)
    check("F13 NOSEQ punches the card and leaves column 3 blank; RESEQ punches and "
          "starts again at 1 (chart OU p.154)",
          [(field(c, 0, 12), field(c, 50, 10) if c[0] == 0o7 else None, field(c, 24, 12))
           for c in si],
          [(0o7, 64, 1), (0o7, 32, 0), (0o7, 32, 1), (0o15, None, 2)])
    check("F14 the check sum still holds on each", [c[3] == checksum(c) for c in si], [True] * 4)

    po = compile_cards([card("", "SLC,64."), card("", "PUNORG")] + [card("", "B,0")] * 60
                       + [card("", "PUNNOR")] + [card("", "B,0")] * 60 + [card("", "END,0")])
    check("F15 PUNORG: every card an origin card; PUNNOR: flow cards again (C28-6129 p.36)",
          [(c.kind, c.nbits) for c in po.punch.cards],
          [("origin", 736), ("origin", 736), ("origin", 448),
           ("origin", 736), ("flow", 800), ("origin", 384), ("branch", 0)])
    pn = compile_cards([card("", "SLC,64."), card("", "NOPUN"), card("", "B,0"), card("", "PUNORG"),
                        card("", "B,0"), card("", "END,0")])
    check("F16 PUNORG ends a NOPUN (N28-1081 errata page 19)",
          [(c.kind, c.origin // 32) for c in pn.punch.cards if c.kind != "branch"],
          [("origin", 0o201)])
    pf2 = compile_cards([card("", "SLC,64."), card("", "B,0"), card("", "PUNORG"), card("", "B,0"),
                         card("", "END,0")])
    check("F17 PUNORG punches the card in process (chart OR p.151)",
          [(c.kind, c.nbits) for c in pf2.punch.cards], [("origin", 32), ("origin", 32), ("branch", 0)])

    # G. PUNFUL and the CC entry mode: MCP's header cards (printed p.320 lines 1-3).
    import cards as hollerith
    inv = {hollerith.column_bits(ch): ch for ch in " ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,.()*/$=+-'"}
    d1 = ("B" + " " * 8 + "HED, REP, 22LOADER, LOAD,,").ljust(45)
    hdr = compile_cards([card("", "PUNFUL"), card("", "SLC,(8)100.0"),
                         card("", "(CC*)DD(BU,,12)," + d1 + "*"),
                         card("", "(CC*)DD(BU,,12)," + " " * 27 + "22LOADER*"),
                         card("", "PUNORG"), card("", "PUNID,22LOADER"), card("", "RESEQ"),
                         card("", "SLC,(8)200.0"), card("", "B,0"), card("", "END,0")])
    hi = hdr.punch.images()
    check("G1 the full card reads back as the control card it spells (CC: the column "
          "as read, row 12 high; DERIVED)",
          "".join(inv.get(x, "?") for x in hi[0]),
          "B        HED, REP, 22LOADER, LOAD,,                                     22LOADER")
    check("G2 then an origin card numbered 1 with the new ID, and the branch",
          [(c.kind, c.seq, c.ident) for c in hdr.punch.cards],
          [("full", 0, None), ("origin", 1, "22LOADER"), ("branch", 2, "22LOADER")])
    bad = compile_cards([card("", "SLC,64."), card("", "(CC*)DD(BU,,8),AB:*"), card("", "END,0")])
    check("G3 CC: 84 without byte size 12, 79 for ':' (no punches in App. F)",
          sorted(m[0] for m in bad.msg.items), [79, 84])
    gaps = compile_cards([card("", "PUNFUL"), card("", "SLC,64."), card("", "(CC*)DD(BU,,12),A*"),
                          card("", "SLC,64.24"), card("", "(CC*)DD(BU,,12),B*"),
                          card("", "DR(BU,12),1"), card("", "(CC*)DD(BU,,12),C*"),
                          card("", "PUNNOR"), card("", "B,0"), card("", "END,0")])
    gc = gaps.punch.cards
    check("G4 an SLC above the counter and a DR are zeros on the card; PUNNOR punches the "
          "short card filled out with zeros and ends PUNFUL",
          ([hollerith.column_bits(ch) for ch in "A B C"] + [0] * 75
           == gaps.punch.images()[0], [c.kind for c in gc]),
          (True, ["full", "origin", "branch"]))
    pid = compile_cards([card("", "PUNFUL"), card("", "SLC,64."), card("", "PUNID,X"),
                         card("", "(CC*)DD(BU,,12),A*"), card("", "PUNNOR"), card("", "END,0")])
    check("G5 PUNID under PUNFUL: 127, ignored",
          ([m[0] for m in pid.msg.items], [c.ident for c in pid.punch.cards]), ([127], [None, None]))
    low = compile_cards([card("", "PUNFUL"), card("", "SLC,128."), card("", "(CC*)DD(BU,,12),A*"),
                         card("", "SLC,64."), card("", "(CC*)DD(BU,,12),B*"), card("", "END,0")])
    check("G6 an SLC below the counter under PUNFUL is not written", low.punch.unwritten,
          "PUNFUL low SLC")
    # MCP printed p.99 lines 8-12: PUNFUL, the two header DDs, then SLC,(8)215000.
    # and only then PUNORG.  Chart OS asks "1ST SLC" first: the SLC stores the
    # counter and punches no zeros.
    p99 = compile_cards([card("", "SLC,64."), card("", "PUNFUL"),
                         card("", "(CC*)DD(BU,,12),A*"), card("", "SLC,(8)215000."),
                         card("", "PUNORG"), card("", "B,0"), card("", "END,0")])
    check("G8 the first SLC under PUNFUL after data stores the counter: one full card, no zeros",
          [c.kind for c in p99.punch.cards], ["full", "origin", "branch"])
    nf = compile_cards([card("", "SLC,64."), card("", "NOPUN"), card("", "PUNFUL"),
                        card("", "(CC*)DD(BU,,12),A*"), card("", "END,0")])
    check("G7 PUNFUL ends a NOPUN (errata page 19)", [c.kind for c in nf.punch.cards],
          ["full", "branch"])

    print("punch: FAILED" if fails else "punch: all passed")
    sys.exit(1 if fails else 0)
