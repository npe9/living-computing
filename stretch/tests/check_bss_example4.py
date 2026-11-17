#!/usr/bin/env python3
"""check_bss_example4.py -- the RECONSTRUCTED BSS processor
(decks/bss_7030.strap, plan R2a) run on the model against C28-6379-0
printed p.17, Example 4, "Typical BSS Storage Map".

>>> decks/bss_7030.strap is a RECONSTRUCTION, not IBM's code.  Agreement with
>>> the printed map shows that the reconstruction's allocation rules reproduce
>>> IBM's printed result for decks built to the map's sizes, not that its code
>>> is IBM's. <<<

THE ORACLE, transcribed from the page image (C28-6379-0 PDF p.17 = printed
p.17, rendered at 400 dpi and read 2026-11-17; MAP_SUB and MAP_COM below):
ten subprogram rows (NAME, ORIGIN, REL. E. P., SIZE, LIB.; SEG. NO. blank)
and five common rows (NAME, ORIGIN, AMOUNT; SEG. NO. blank), every number in
octal, "**" between the halves on each of the ten data rows.

THE INPUT, built here, not in decks/: Example 4's subprograms as STRAP II
stubs (strap/strap2 punches them: PUNFPC/ENTER, PUNCDC/COMBLOCK, PUNREL,
relocatable instruction and data cards), each of its printed size with its
entry points at their printed relative addresses.  What the page does NOT
print, and is CHOSEN here so that the map's rows discriminate:
  * the transfer vectors (the calls).  *MAIN* calls FISIP* first and IOCS*
    last, so the library is fetched FISIP*, IOCS*; UST* is called only by
    IOCS*, so it is fetched in a second round, after the input's names;
    IOCS* is called from two subprograms (*MAIN*, DERIV) and SPTXT*, IOCS*'s
    second entry, by VALUE after IOCS* is in: no refetch, no duplicate.
  * the commons: first declared in the order DIFF, A (*MAIN*), STE (STEP),
    POL (POLY); A redeclared larger (100 then 146 by STEP) and smaller (30 by
    VALUE), DIFF smaller (4 by DERIV); blank common 6 (*MAIN*) then 14
    (STEP).  Designed so that "first wins" and "last wins" would each move
    a set; only the dropped largest-wins (first wins) is measured below.
  * RANDM's program card carries the size all 1's (C28 p.7, a FORTRAN-made
    card), so its 7 words must come from the scan of its cards; every other
    card carries its assembled size.
  * the library's order on disk: UST*, SIN (never called), IOCS*, FISIP*, so
    the relocation table's library entries (by disk order, p.9) differ from
    the map's (by fetch order, p.7).
  * U, the problem program's upper limit in KSILO+8.32: 213713 + max(14,
    T) = 213766 octal, T = 43 words the relocation table.  So THE BLANK
    COMMON ORIGIN ROW (213713) HOLDS BY CONSTRUCTION and is not evidence;
    the named commons' four origins and the ten subprogram rows are.
The relocation table (the loader's layout, docs/bss_loader_spec.md 5.4) and
KSILO words 8-11 are checked word for word against expect(), computed
here from the stubs; that half tests the deck against its own CHOSEN rules
(the deck's header, C3-C14), not against a printed page.  The relocation
table is NOT yet fed to MCP's loader (that is R2b).

FURTHER RUNS, the messages (C28 pp.22-23): UST* removed from the library
(T.V. UST* INCOMPLETE IN IOCS* SUBPROGRAM, with the console line), *MAIN*
renamed (message 10), U lowered (message 2), and message 3's ILLEGAL TYPE
OF CARD (a column-1 code 77 card in STEP), INCORRECT CARD ORDER (STEP's
common card moved after its instruction card) and RELOCATION TABLES ARE TOO
LARGE (U = 30 words).

FIRST RUN, 2026-11-17: every map row, the table and KSILO+8 matched at the
first run (305,752 model steps); KSILO+9..+11 failed only on Bluesim's
0xAA... in bits the deck does not write, so the test now plants KSILO 8-11
as MCP leaves them (zero but U).  The console line first failed on three
unwritten characters of CONB (the deck now copies the 40-character padded
text).  CONTROL, first commit: 32 checks.  2026-11-17 second pass: KSILO
9-11 planted with a 0xAA sentinel, ERRC's sentinel moved to the byte read,
three more message-3 runs; CONTROL now ALL CHECKS PASSED, 35 checks,
305,759 steps.

MEASURED INJECTIONS into decks/bss_7030.strap, scripted, each restored from
a saved copy verified with cmp (OBSERVED sets; the message runs passed in
each):
  - "the largest wins" dropped for named commons (DD4's store to the
    survivor's amount sent to TMPB, so the first declaration's size stays):
    4 fail -- common rows 3 (A 213603 000100), 4 (STE 213575) and 5 (POL
    213431), and the relocation table (5 words: 213716, 213727, 213730,
    213740, 213751, every word holding A's, STE's or POL's origin).
  - "the largest wins" dropped for blank common (SCPROG's BZAH a NOP, so the
    last card's size is kept): 1 fails, common row 1's amount (000000).
  - the data card's secondary count left out of the scanned extent: 9 fail
    -- RANDM's size (000002), the origins of rows 4-10, and 17 table words.
  - the library sorted by storage address (fetch order) instead of disk
    address: 1 fails, the relocation table (213754, 213755, 213763, 213764:
    UST*'s and FISIP*'s words 0 and 1 swap places; IOCS*'s stay).
  - KSILO+11.0 never written (its ST a NOP): 1 fails, KSILO+11 (the
    sentinel aaaaaaaaaaaaaaaa survives).
  (Re-measured after the second pass: the first four sets unchanged.)
"""
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
sys.path.insert(0, HERE)
from strap2 import compile_cards                    # noqa: E402
from strap2.cards import deck_cards                 # noqa: E402
from strap2.a8 import A8, A6, a8                    # noqa: E402
import strap_asm                                    # noqa: E402

BSV = os.path.join(HERE, "..", "bsv")
DECK = os.path.join(HERE, "..", "decks", "bss_7030.strap")
MODULE = "StretchBssExample4Tb"
STEPS = 20000000
KSILO = 0o220451
DUMP_FIRST, DUMP_LAST = 0o200000, KSILO + 12
fails = 0

# C28-6379-0 printed p.17, as read in the page image.
MAP_SUB = [("*MAIN*", "000041", "000010.0", "000745", "NO"),
           ("STEP", "001006", "000022.0", "000441", "NO"),
           ("RANDM", "001447", "000000.0", "000007", "NO"),
           ("POLY", "001456", "000022.0", "000346", "NO"),
           ("DERIV", "002024", "000022.0", "000271", "NO"),
           ("VALUE", "002315", "000022.0", "000134", "NO"),
           ("FISIP*", "002451", "000001.0", "000007", "YES"),
           ("IOCS*", "002460", "000002.0", "003037", "YES"),
           ("SPTXT*", "002460", "001124.0", "E. P.", "YES"),
           ("UST*", "005517", "000001.0", "000002", "YES")]
MAP_COM = [("", "213713", "000014"),
           ("DIFF", "213703", "000010"),
           ("A", "213535", "000146"),
           ("STE", "213527", "000006"),
           ("POL", "213363", "000144")]


def check(label, got, want):
    global fails
    ok = got == want
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} {label}" + ("" if ok else f": got {got!r}, want {want!r}"))


# The subprograms: (entries [(name, relative word)], size words (None: the
# card says all 1's), blank common words, [(common, words)], calls).
SUBS = [
    ([("*MAIN*", 0o10)], 0o745, 6, [("DIFF", 8), ("A", 64)],
     ["FISIP*", "STEP", "POLY", "DERIV", "VALUE", "IOCS*"]),
    ([("STEP", 0o22)], 0o441, 12, [("STE", 6), ("A", 102)], ["RANDM", "POLY"]),
    ([("RANDM", 0)], None, 0, [], []),
    ([("POLY", 0o22)], 0o346, 0, [("POL", 100)], ["RANDM"]),
    ([("DERIV", 0o22)], 0o271, 0, [("DIFF", 4)], ["IOCS*", "POLY"]),
    ([("VALUE", 0o22)], 0o134, 0, [("A", 24)], ["SPTXT*", "DERIV"]),
]
LIB = {  # in disk order (CHOSEN)
    "UST*": ([("UST*", 1)], 2, 0, [], []),
    "SIN": ([("SIN", 1)], 4, 0, [], []),
    "IOCS*": ([("IOCS*", 2), ("SPTXT*", 0o1124)], 0o3037, 0, [], ["UST*"]),
    "FISIP*": ([("FISIP*", 1)], 7, 0, [], []),
}


def a8_word(name):
    return int.from_bytes(bytes(a8(c) for c in name.ljust(8)), "big")


def stub_source(entries, size, blank, commons, calls):
    src = ["        PUNFPC,%s,%d" % ("(8)777777" if size is None else "LAST", blank)]
    src += ["%-8sENTER,E%d" % (n, k) for k, (n, _w) in enumerate(entries)]
    if commons:
        src.append("        PUNCDC")
        src += ["%-8sCOMBLOCK,%d" % (c, w) for c, w in commons]
    src.append("        PUNREL")
    at0 = [k for k, (_n, w) in enumerate(entries) if w == 0]
    src.append("%-8sXW,0,%d" % ("E%d" % at0[0] if at0 else "", len(calls)))
    src += ["        DD(BU,64),(16)%016X" % a8_word(c) for c in calls]
    pos = 1 + len(calls)
    for k, (_n, w) in enumerate(entries):
        if w == 0:
            continue
        assert w >= pos
        if w > pos:
            src.append("        DR(BU,64),%d" % (w - pos))
        src += ["E%d      B,E%d" % (k, k), "        NOP"]
        pos = w + 1
    if size is None:            # RANDM: its extent is 7 words, a DD at word 6
        src += ["        DR(BU,64),5", "        DD(BU,64),0"]
    elif size > pos:
        src.append("        DR(BU,64),%d" % (size - pos))
    src += ["LAST    SYN,$", "        END"]
    return src


def punch(lines):
    p2 = compile_cards(deck_cards("\n".join(lines) + "\n"))
    assert not p2.msg.items and not p2.punch.unwritten, (p2.msg.items[:3], p2.punch.unwritten)
    return p2.punch.images(clock=0o1234)


def card_words(cols):
    bits = 0
    for c in cols:
        bits = (bits << 12) | (c & 0o7777)
    return [(bits >> (64 * (14 - i))) & ((1 << 64) - 1) for i in range(15)]


def tws_offset(k):
    """Card k's word on TWS: 34 cards of 15 words an arc of 512 (p.332)."""
    return (k // 34) * 512 + (k % 34) * 15


def build(subs=SUBS, lib=LIB, upper=None, mangle=None):
    """The deck's source with the input after INPUT, and what to expect."""
    decks = [punch(stub_source(*s)) for s in subs]
    if mangle:
        mangle(decks)
    fb = punch(["        PUNREL", "        FEND"])
    tws, firsts = [], []
    for d in decks:
        firsts.append(len(tws))
        tws += d
    tws += fb
    tws_words = []
    for k, cols in enumerate(tws):
        while len(tws_words) < tws_offset(k):
            tws_words.append(0)
        tws_words += card_words(cols)
    base = 0o210400
    tws_at = base
    lib_at = tws_at + len(tws_words)
    lib_words, lib_addr, directory = [], {}, []
    for name, s in lib.items():
        d = punch(stub_source(*s))
        lib_addr[name] = lib_at + len(lib_words)
        for e, _w in s[0]:
            directory.append((e, lib_addr[name], len(d)))
        for cols in d:
            lib_words += card_words(cols)
    dir_at = lib_at + len(lib_words)
    rows = ["TWS     SYN, $"] + ["        DD(BU,64), (16)%016X" % w for w in tws_words]
    rows += ["        DD(BU,64), (16)%016X" % w for w in lib_words]
    rows.append("LIBDIR  SYN, $")
    for e, at, n in directory:
        rows.append("        DD(BU,64), (16)%016X" % a8_word(e))
        rows.append("        XW, (8)%o.0, %d" % (at, n))
    rows.append("        DD(BU,64), 0")
    exp = expect(subs, lib, decks, firsts, lib_addr)
    u = exp["U"] if upper is None else upper
    # KSILO word 8 holds the upper limit; 9-11 a sentinel, so a field the
    # deck never writes shows (the bits outside C12's fields must survive).
    rows += ["        SLC, (8)%o.0" % (KSILO + 8), "        DD(BU,64), (16)%016X" % (u << 14)]
    rows += ["        DD(BU,64), (16)%016X" % SENT] * 3
    src = open(DECK).read()
    for old, new in (("TWSA    XW, INPUT", "TWSA    XW, TWS"), ("LIBA    XW, INPUT", "LIBA    XW, LIBDIR")):
        assert src.count(old) == 1
        src = src.replace(old, new)
    tail = "INPUT   SYN, $\n        END, BSS\n"
    assert src.endswith(tail)
    src = src[:-len("        END, BSS\n")] + "\n".join(rows) + "\n        END, BSS\n"
    assert dir_at < 0o213000
    return src, exp


def tvskel():
    p = strap_asm.assemble("        SLC,(8)1000.0\n        B,0\n        NOP\n")
    return p.words[0o1000]


def expect(subs, lib, decks, firsts, lib_addr):
    """The relocation table and KSILO words, from the deck's rules C3-C14."""
    origin, ep = {}, {}
    at = 0o41
    for (entries, size, *_r), d in zip(subs, decks):
        origin[entries[0][0]] = at
        at += size if size is not None else 7
    fetched, queue = [], [c for s in subs for c in s[4]]
    known = {e for s in subs for e, _w in s[0]}
    while queue:
        c = queue.pop(0)
        if c in known:
            continue
        name = next((n for n, s in lib.items() if c in [e for e, _w in s[0]]), None)
        if name is None:            # a message run: nothing to expect
            return {"U": None}
        fetched.append(name)
        known |= {e for e, _w in lib[name][0]}
        queue += lib[name][4]
    for name in fetched:
        origin[name] = at
        at += lib[name][1]
    allsubs = [(s, False) for s in subs] + [(lib[n], True) for n in fetched]
    for (entries, *_r), _l in allsubs:
        for e, w in entries:
            ep[e] = origin[entries[0][0]] * 2 + w * 2
    # commons: second-table order, largest wins, downward from blank's base
    blank = max(s[2] for s, _l in allsubs)
    amount, order = {}, []
    for (_e, _s, _b, commons, _c), _l in allsubs:
        for c, w in commons:
            if c not in amount:
                order.append(c)
                amount[c] = w
            amount[c] = max(amount[c], w)
    entries_order = [s for s, _l in allsubs[:len(subs)]] + \
        [lib[n] for n in sorted(fetched, key=lambda n: lib_addr[n])]
    sizes = [(3 * 64 + len(s[3]) * 32) // 64 + len(s[4]) for s in entries_order]
    t = sum(sizes)
    u = 0o213713 + max(blank, t)
    b = u - max(blank, t)
    corg, top = {}, b
    for c in order:
        top -= amount[c]
        corg[c] = top
    skel = tvskel()
    table, r = {}, b
    for k, s in enumerate(entries_order):
        entries, _size, _blank, commons, calls = s
        name = entries[0][0]
        is_lib = name in lib
        if is_lib:
            a6 = 0
            for ch in name.ljust(6)[:6]:
                a6 = (a6 << 6) | A6.get(ch, 0)
            w0 = (a6 << 28) | 1
        else:
            i = [x[0][0][0] for x in subs].index(name)
            w0 = (tws_offset(firsts[i]) << 46) | (len(decks[i]) << 18)
        nxt = 0 if k == len(entries_order) - 1 else r + sizes[k]
        words = {0: w0, 1: (origin[name] << 46) | (len(calls) << 18) | nxt, 2: len(commons) << 45}
        for j, (c, _w) in enumerate(commons, 1):
            w, half = divmod(4 + j, 2)
            words[w] = words.get(w, 0) | (corg[c] << (46 - 32 * half))
        v0 = (3 * 64 + len(commons) * 32) // 64
        for j, c in enumerate(calls):
            words[v0 + j] = (skel & ~(((1 << 19) - 1) << 45)) | (ep[c] << 45)
        for w, v in words.items():
            table[r + w] = v
        r += sizes[k]
    main = ep.get("*MAIN*", 0)
    f24 = ((1 << 24) - 1)
    two = (f24 << 40) | (f24 << 8)          # 24-bit fields at .0 and .32
    ks = {KSILO + 8: (0o41 << 46) | (u << 14),
          KSILO + 9: (SENT & ~two) | (b << 46) | (b << 14),
          KSILO + 10: (SENT & ~two) | (main << 45) | (main << 13),
          KSILO + 11: SENT & ~(f24 << 40)}
    return {"U": u, "B": b, "T": t, "table": table, "ksilo": ks,
            "table_span": (b, b + t)}


SENT = 0xAAAAAAAAAAAAAAAA
A8INV = {v: k for k, v in A8.items()}


def run(src, tmp, tag):
    path = os.path.join(tmp, MODULE + tag + ".strap")
    with open(path, "w") as fh:
        fh.write(src)
    p2 = compile_cards(deck_cards(src), strap_asm.DEFAULT_ORIGIN_BITS)

    def word(n):
        return p2.val.symbol_value(p2.st.search(n))[0] // 64
    mod = MODULE + tag
    args = [os.path.join(HERE, "run_program.sh"), path, mod, "ASM=strap2",
            f"DUMP={DUMP_FIRST},{DUMP_LAST - DUMP_FIRST}", f"STEPS={STEPS}",
            f"CYCLES<={STEPS}", f"FASTLOAD={os.path.join(tmp, mod + '.hex')}"]
    r = subprocess.run(args, capture_output=True, text=True, cwd=HERE)
    for name in os.listdir(BSV):            # by exact name, never a glob
        if name in (mod + ".bsv", mod + "_sim", mod + "_sim.so"):
            os.remove(os.path.join(BSV, name))
    out = r.stdout
    if r.returncode or "step cap" in out:
        return None, (out + r.stderr)[-2000:]
    mem = {int(a): int(v, 16) for a, v in re.findall(r"MEMDUMP (\d+) ([0-9a-f]+)", out)}
    m = re.search(r"cycles = (\d+)", out)

    def text(at, nwords):
        return "".join(A8INV.get((mem[at + i] >> (56 - 8 * k)) & 255, "?")
                       for i in range(nwords) for k in range(8))
    nlines = mem[word("OUTN")] >> 46
    lines = [text(word("OUTB") + 15 * i, 15) for i in range(nlines)]
    return {"errc": mem[word("ERRC")] >> 56, "lines": lines, "mem": mem,
            "console": text(word("CONB"), 5).rstrip(),
            "steps": int(m.group(1)) if m else None}, out


def map_rows(lines):
    """The map's data rows as fields, by the deck's columns (C13)."""
    subs, coms, seps = [], [], []
    for ln in lines[2:]:
        subs.append(tuple(ln[c:c + w].strip() for c, w in ((0, 8), (12, 6), (24, 8), (36, 6), (48, 3))))
        seps.append(ln[64:66])
        coms.append(tuple(ln[c:c + w].strip() for c, w in ((72, 8), (84, 6), (96, 6))))
    return subs, coms, seps


def main():
    with tempfile.TemporaryDirectory() as tmp:
        src, exp = build()
        got, out = run(src, tmp, "")
        if got is None:
            print("FAIL the reconstructed BSS did not run to its halt:\n" + out)
            return 1
        check("control: U planted = 213713 + max(14, T) (the blank row is by construction)",
              (exp["U"], exp["T"]), (0o213766, 43))
        check("ERRC 0: the map printed, the tables and KSILO set", got["errc"], 0)
        lines = got["lines"]
        check("12 lines printed: two headers, ten data rows", len(lines), 12)
        check("header 1 holds **SUBPROGRAMS** and **COMMONS**",
              lines[0].split() if lines else None, ["**SUBPROGRAMS**", "**COMMONS**"])
        check("header 2: NAME ORIGIN REL. E. P. SIZE LIB. SEG. NO. NAME ORIGIN AMOUNT SEG. NO.",
              " ".join(lines[1].split()) if len(lines) > 1 else None,
              "NAME ORIGIN REL. E. P. SIZE LIB. SEG. NO. NAME ORIGIN AMOUNT SEG. NO.")
        subs, coms, seps = map_rows(lines)
        for k, want in enumerate(MAP_SUB):
            check(f"p.17 subprogram row {k + 1}: {' '.join(want)}",
                  subs[k] if k < len(subs) else None, want)
        for k, want in enumerate(MAP_COM):
            check(f"p.17 common row {k + 1}: {' '.join(w for w in want if w)}",
                  coms[k] if k < len(coms) else None, want)
        check("rows 6-10 have no common", coms[5:], [("", "", "")] * 5)
        check("'**' on all ten data rows", seps, ["**"] * 10)
        mem = got["mem"]
        b0, b1 = exp["table_span"]
        bad = [(f"{a:o}", f"{mem.get(a, 0):016x}", f"{exp['table'].get(a, 0):016x}")
               for a in range(b0, b1) if mem.get(a, 0) != exp["table"].get(a, 0)]
        check(f"the relocation table, {b1 - b0} words at {b0:o} (loader layout, C3-C14)", bad, [])
        for a, v in sorted(exp["ksilo"].items()):
            check(f"KSILO+{a - KSILO} = {v:016x}", f"{mem.get(a, 0):016x}", f"{v:016x}")
        print(f"INFO model steps: {got['steps']}")

        # The messages (C28 pp.22-23).
        lib2 = {k: v for k, v in LIB.items() if k != "UST*"}
        src, _e = build(lib=lib2, upper=exp["U"])
        got, out = run(src, tmp, "Tv")
        check("UST* not in the library: ERRC 3, message 3",
              got and got["errc"], 3)
        check("... the listing: JOB TERMINATED - T.V. UST* INCOMPLETE IN IOCS* SUBPROGRAM",
              got and [" ".join(x.split()) for x in got["lines"]],
              ["JOB TERMINATED - T.V. UST* INCOMPLETE IN IOCS* SUBPROGRAM"])
        check("... the console: BSS TERMINATED JOB - PROGRAMMER ERROR",
              got and got["console"], "BSS TERMINATED JOB - PROGRAMMER ERROR")
        subs2 = [([("PROG", 0o10)],) + SUBS[0][1:]] + SUBS[1:]
        src, _e = build(subs=subs2, upper=exp["U"])
        got, out = run(src, tmp, "Nm")
        check("no *MAIN*: ERRC 10, NO ENTRY POINT WITH NAME *MAIN* - JOB WILL NOT BE RUN",
              got and (got["errc"], [" ".join(x.split()) for x in got["lines"]]),
              (10, ["NO ENTRY POINT WITH NAME *MAIN* - JOB WILL NOT BE RUN"]))
        src, _e = build(upper=0o5521 + 43 + 100)
        got, out = run(src, tmp, "Ov")
        check("U too low for the commons: ERRC 2, JOB REJECTED - COMMON AND PROGRAM OVERLAP.",
              got and (got["errc"], [" ".join(x.split()) for x in got["lines"]]),
              (2, ["JOB REJECTED - COMMON AND PROGRAM OVERLAP."]))
        # message 3's other reasons: a card of no class, a common definition
        # card after the first instruction card, and U under the table.
        def bad_card(decks):
            decks[1].insert(1, [0o77] + [0] * 79)
        src, _e = build(upper=exp["U"], mangle=bad_card)
        got, out = run(src, tmp, "Il")
        check("a card of no class in STEP: ERRC 3, ILLEGAL TYPE OF CARD IN STEP SUBPROGRAM",
              got and (got["errc"], [" ".join(x.split()) for x in got["lines"]], got["console"]),
              (3, ["JOB TERMINATED - ILLEGAL TYPE OF CARD IN STEP SUBPROGRAM"],
               "BSS TERMINATED JOB - PROGRAMMER ERROR"))

        def late_common(decks):
            d = decks[1]
            k = [c[0] for c in d].index(0o27)
            i = [c[0] for c in d].index(0o25)
            d.insert(i, d.pop(k))
        src, _e = build(upper=exp["U"], mangle=late_common)
        got, out = run(src, tmp, "Or")
        check("STEP's common card after its instruction card: ERRC 3, INCORRECT CARD ORDER IN STEP SUBPROGRAM",
              got and (got["errc"], [" ".join(x.split()) for x in got["lines"]]),
              (3, ["JOB TERMINATED - INCORRECT CARD ORDER IN STEP SUBPROGRAM"]))
        src, _e = build(upper=30)
        got, out = run(src, tmp, "Tl")
        check("U = 30 words, under the 43-word table: ERRC 3, RELOCATION TABLES ARE TOO LARGE",
              got and (got["errc"], [" ".join(x.split()) for x in got["lines"]]),
              (3, ["JOB TERMINATED - RELOCATION TABLES ARE TOO LARGE"]))
    print("ALL CHECKS PASSED" if not fails else f"{fails} FAILED")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
