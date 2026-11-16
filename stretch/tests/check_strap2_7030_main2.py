#!/usr/bin/env python3
"""check_strap2_7030_main2.py -- the 7030 STRAP II's MAIN, Boxes 25-26
(decks/strap2_7030.strap, step 4b-ii; Chart AA p.14, pp.22-23, Figs. 20,
23, 24 pp.189, 192, the messages of p.176, read in the ink 2026-11-15), run
on the Bluespec model over statements with a parenthesis after the op.

WHAT IS COMPARED.  After each statement the driver records MSTAT, Bop, $5,
MMSG (a bit a message number), Ibuffw, the unit's eight fixed-format words
and the four words after them (the coded expressions).

THE ORACLES.
  guide   Box 26 as pp.22-23 give it, worked here over the generated tables
          (optab7030): all eight words, bit for bit, $5, Bop, the messages,
          the status, Ibuffw, and the coded bits a symbolic field or a
          P-mode symbol leaves.  The fields Boxes 25-26 own are ZIDDS,
          ZIFDDS, ZIFPMN, ZIFFLF, ZIFSFL, ZIFBSF, ZIFSBS, ZIFDSF, ZILPMS,
          ZIFALL, ZIOPX and ZIOTPT; every other bit is as Boxes 2 and 23
          left it.
  host    the host Pass 1 (strap2/pass1.py) on the same statement, wherever
          it gives no message but 36 or 37, or gives 2 or 4 alone: the
          messages as a set; then, field by field, ZIDDS, ZIFDDS, ZIFFLF,
          ZIFSFL, ZIFBSF, ZIFSBS, ZIFDSF, ZIFPMN; ZIOTPT; the op index at
          the unit's location against the index key of the host's entry;
          and a symbolic field's coded bits.
          NOT compared with the host, and why:
            ZIOTPT's mode bits (VFL bits 51 and 53, floating bit 18): the
              host's skeleton carries the mode from Pass 1; on the 7030 the
              dds goes into the binary in DECODE (p.140 Boxes 5, 7-8).
            ZIOTPT of a pseudo-op: the host keeps other things there.
            LINK's op index: the host's MQLINK makes the unit an
              instruction's.
            ZIFALL, ZILBO, ZIFBO, ZIFP2, ZINFLD: later boxes' in the host.
            P-mode's ZILPMS, ZIDDS, ZIFDSF and coded bits: the host keeps a
              coded expression and a made-up dds; p.23 keeps the symbol's
              characters (the guide oracle checks those).
          Four names' statements are known to differ and are pinned
          (ONE_FAMILY below: a question for the table, 4a-iii).
          A statement the host gives any other message is counted in an
          INFO line, by the kind of the op's entry, and checked by the
          guide oracle alone.  Message 1 there is the host refusing a mode
          that does not fit the op (D+(BU,8), M+1(N)), which p.177 gives to
          DECODE (91), not MAIN.
          The host rows are counted in an INFO line: messages for every
          row; the dds fields only where the unit stands (status 0 and no
          message 2 or 4); ZIOTPT but for pseudo-ops; the op index but for
          LINK and a unit still ambiguous with no dds and no secondary.

THE SWEEP.  Every name of the 7030 op table but EXT and the null op, with
(V+I), (SEOP) and (CR), and with (BU,8), (B,24,8), (U) and (N): 471 names,
3297 statements.  Then the cases of CASES below: every route of Box 26 and
each message, and statements with no modifier (4b-i's, unchanged).

WHERE THE 7030 PROGRAM AND THE HOST DIFFER (each expected value below is
the guide's, with its page):
  two dds, +(BU,8)(BU,4)     7030 message 5 (p.176); the host none
  +(BU,8,0 unclosed          7030 message 35 (p.176); the host 33
  +(CX)                      7030 message 2 (p.22: C starts a secondary);
                             the host 91
  CW(U), CW(N)               a dds on the 7030 (p.22: U and N do not start
                             a secondary); the host's message 2
  +(P,A)                     ZILPMS 8, the symbol's characters (p.23); the
                             host 26, a coded expression
  M+N, M+NMG, +N, +NMG       ONE_FAMILY below

The run is cut into eight chunks, each its own testbench, run side by
side: 68.6M model steps in all.  Run from stretch/tests with
PYTHONDONTWRITEBYTECODE=1.  About 10 minutes on a loaded machine.

MEASURED INJECTIONS, 2026-11-16, into Box 26 in a copy of the deck (the
deck itself untouched, checked with cmp against the saved copy); control:
all 22 checks pass, 68.3M model steps; the host rows compared (INFO):
messages 2757, dds fields 1446, ZIOTPT 1271, op index 1437.
  1 the secondary code always 001 (MS1     FAIL guide sweep, host sweep,
    takes no code from the op index)       guide cases, host cases, p.23's
                                           +(BU,3)(SEOP)/CW(V+I), the
                                           floating-mode rule
  2 p.23 not done: an ambiguous op with a  FAIL guide sweep, host sweep (op
    secondary keeps its own op index       index), guide cases, host cases,
    ($5, ZIOPX not OPIVFL)                 p.23's +(V+I) check, the
                                           floating-mode rule
  3 a symbolic field's Ibuffw not moved    FAIL guide cases, host cases (the
    past it                                second symbol overwrites the
                                           first), the +(BU,A) check
  4 message 2 tested before message 4      FAIL guide cases, host cases,
                                           the p.176 4-and-5 check
  5 a floating mode leaves $5 and ZIOPX    FAIL guide sweep, host sweep (op
    on the ambiguous index (not OPIFP)     index), guide cases, host cases,
                                           the floating-mode rule
  6 a null byte size 0, not the mode's     FAIL guide sweep, host sweep,
    (MMTAB)                                ONE_FAMILY's list, guide cases,
                                           host cases
  7 Box 25 never taken (EXT's modifier     FAIL guide cases, host cases,
    read as Box 26's)                      the Box 25 check
  8 (,8) does not settle an ambiguous op   FAIL guide cases, host cases,
    (MJ9's CHOSEN arm removed)             the +(,8) check
An earlier form of the host oracle skipped the op index of every unit
that still held an ambiguous index, and 2 and 5 then passed the host
sweep; it was changed to compare wherever the unit has a dds or a
secondary, and everything above was re-run.
"""
import concurrent.futures
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
sys.path.insert(0, HERE)
import strap_asm                                    # noqa: E402
import strap2                                       # noqa: E402
from strap2 import optab7030 as O, optable as T     # noqa: E402
from strap2 import unit as U                        # noqa: E402
from strap2.a8 import a8_bits                       # noqa: E402
from strap2.bits import field as bits_of            # noqa: E402
from strap2.cards import deck_cards                 # noqa: E402
from strap2.pass1 import Pass1                      # noqa: E402
from check_strap2_7030 import BSV, card, iqs_words  # noqa: E402
import printed_ops                                  # noqa: E402

DECK = os.path.join(HERE, "..", "decks", "strap2_7030.strap")
MODULE = "StretchStrap2x7030Main2Tb"
STEPS = 200000000
UNITW = 12                  # the unit's eight words and four coded words
REC = 5 + UNITW             # status, Bop, $5, MMSG, Ibuffw, the unit
CHUNKS = 8
fails = 0


def check(label, got, want):
    global fails
    if got == want:
        print(f"PASS {label}")
    else:
        fails += 1
        print(f"FAIL {label}: got {str(got)[:900]}, want {str(want)[:300]}")


DRIVER = """START   SIC, XINLK
        B, XINPUT
        LVI, $9, OUTR
MD1     SV, $9, MDP
        LVI, $9, UNITA
        SV, $9, IBUFFW
        L(BU,24), ULIM
        ST(BU,24), IBUFLM
        L(BU,64), MZERO
""" + "".join(f"""        ST(BU,64), UNITA+{k}.0
""" for k in range(8, UNITW)) + """        SIC, MAINLK
        B, MAIN
        LV, $9, MDP
        L(BU,24), MSTAT
        KI(BU,24), 1
        BAE, DONE
        ST(BU,24), 0.0($9)
        L(BU,64), BOP
        ST(BU,64), 1.0($9)
        SV, $5, 2.0($9)
        L(BU,64), MMSG
        ST(BU,64), 3.0($9)
        L(BU,64), IBUFFW
        ST(BU,64), 4.0($9)
""" + "".join(f"""        L(BU,64), UNITA+{k}.0
        ST(BU,64), {5 + k}.0($9)
""" for k in range(UNITW)) + """        V+I, $9, {rec}.0
        M+1(BU,24), OUTN
        B, MD1
DONE    BEW, $
        CNOP
MDP     DD(BU,64), 0
ULIM    XW, UNITA+{unitw}.0, 0, 0
UNITA   DRZ(BU,64), {unitw}
OUTN    DD(BU,64), 0
OUTR    DRZ(BU,64), {n}
"""


def deck_text(cards, n_stmts):
    src = open(DECK).read()
    rows = []
    for c in cards:
        rows += [f"        DD(BU,64), (16){w:016X}" for w in iqs_words(c)]
    src = src.replace("INX     XW, INB, 0, 0\n", f"INX     XW, INB, {len(cards)}, 0\n", 1)
    assert src.endswith("        END\n")
    return (src[:-len("        END\n")] + "\n".join(rows) + "\n" +
            DRIVER.format(n=REC * (n_stmts + 4), rec=REC, unitw=UNITW) + "        END, START\n")


def pack(stmts):
    """Statements to cards, several a card with semicolons between them
    (the last ends at GETCHA's false one, p.20)."""
    cards, line = [], []
    for s in stmts:
        assert len(s) < 62 and ";" not in s and "'" not in s, s
        if line and len(";".join(line + [s])) > 63:
            cards.append(card(" ", "", ";".join(line)))
            line = []
        line.append(s)
    if line:
        cards.append(card(" ", "", ";".join(line)))
    return cards


def run_chunk(i, stmts):
    """One testbench over stmts: (the records, the unit's word address,
    the model's step count), or a string saying what went wrong."""
    module = f"{MODULE}{i}"
    cards = pack(stmts)
    text = deck_text(cards, len(stmts))
    p2 = strap2.compile_cards(deck_cards(text), strap_asm.DEFAULT_ORIGIN_BITS)
    word = lambda n: p2.val.symbol_value(p2.st.search(n))[0] // 64      # noqa: E731
    out = word("OUTR")
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, module + ".strap")
        with open(path, "w") as fh:
            fh.write(text)
        args = [os.path.join(HERE, "run_program.sh"), path, module, "ASM=strap2",
                f"DUMP={out - 1},{1 + REC * (len(stmts) + 2)}",
                f"STEPS={STEPS}", f"CYCLES<={STEPS}",
                f"FASTLOAD={os.path.join(tmp, module + '.hex')}",
                f"ERRC:{word('ERRC')}=0x0"]
        r = subprocess.run(args, capture_output=True, text=True, cwd=HERE)
    for name in os.listdir(BSV):            # by exact name, never a glob
        if name in (module + ".bsv", module + "_sim", module + "_sim.so"):
            os.remove(os.path.join(BSV, name))
    o = r.stdout
    if r.returncode or "step cap" in o:
        return f"chunk {i}: " + (o + r.stderr)[-1200:]
    if not re.search(r"^PASS ERRC", o, re.M):
        return f"chunk {i}: ERRC is not 0: " + o[-600:]
    mem = {int(a): int(v, 16) for a, v in re.findall(r"MEMDUMP (\d+) ([0-9a-f]+)", o)}
    n_out = mem.get(word("OUTN"), 0) >> 40
    if n_out != len(stmts):
        return f"chunk {i}: {n_out} records for {len(stmts)} statements"
    recs = [[mem.get(out + REC * k + j, 0) for j in range(REC)] for k in range(n_out)]
    m = re.search(r"cycles = (\d+)", o)
    return recs, word("UNITA"), int(m.group(1)) if m else 0


# ---- the guide oracle: Box 26 worked over the generated tables ------------
LOCMASK = ((1 << 18) - 1) << O.LOC_SHIFT
MODES = {"BU": (5, 8, 0), "B": (7, 1, 0), "DU": (4, 4, 0), "D": (6, 4, 0),
         "N": (3, 4, 1), "U": (1, 4, 1), "": (5, 8, 3)}
FLAG = {"DDS": 25, "PMN": 26, "FLF": 27, "SFL": 28, "BSF": 29, "SBS": 30, "DSF": 31}


class Guide:
    def __init__(self, tb):
        self.tb = tb
        self.word2 = {n: tb.primary_word2(n) for n in tb.order}
        self.sec = {w1: w2 for w1, w2, _ in O.secondaries()}
        iv, ifp, hi = tb.resolved()
        self.opivfl, self.opifp, self.hi = tb.idx + iv, tb.idx + ifp, hi << 32

    def index(self, loc):
        return self.tb.index_word(self.tb.indexes[loc - self.tb.idx])

    def box26(self, name, groups):
        """(status, messages, loc, the eight words, the coded bits) for
        NAME(g1)(g2)..., each group well formed and closed."""
        w2 = self.word2[name]
        loc, sk = w2 >> O.LOC_SHIFT, w2 & ~LOCMASK
        flags, dds, lpms, zifall, coded = set(), 0, 0, 1, ""
        msgs, secn, secbad, ddsn, wasamb = set(), 0, False, 0, False
        status = 0

        def unit():
            w = [0] * 8
            for f in flags:
                w[2] |= 1 << (63 - FLAG[f])
            w[3] = (lpms << 39) | (zifall << 38) | (dds << 1)
            w[5] = loc << O.LOC_SHIFT
            w[6] = sk
            return w

        if groups and name == "EXT":
            return 6, msgs, loc, unit(), coded
        for g in groups:
            if g[:1] in ("V", "S", "C"):                # p.22: a secondary
                secn += 1
                if len(g) > 7:
                    secbad = True
                if secn != 1:
                    continue
                ix = self.index(loc)
                key = O.name_word(g[:7], O.field(ix, 24, 3))
                if key not in self.sec:
                    secbad = True
                elif O.field(ix, 38, 1):                # p.23: ambiguous
                    wasamb = True
                    sk = self.hi | (sk & 0xFFFFFFFF) | self.sec[key]
                    loc = self.opivfl
                else:
                    sk |= self.sec[key]
                continue
            ddsn += 1
            if ddsn == 2:                               # p.176: message 5
                return 7, {5}, loc, unit(), coded
            parts = g.split(",")
            mode = parts[0]
            if mode == "P":                             # p.23: P-mode
                sym = parts[1]
                coded += a8_bits(sym)
                lpms = 8 * len(sym)
                flags.add("PMN")
                zifall = 0
                continue
            if mode not in MODES:
                return 9, msgs, loc, unit(), coded
            code, bs, cls = MODES[mode]
            anything = cls != 3
            if cls in (0, 1):
                if O.field(self.index(loc), 38, 1):     # p.23: "Once again"
                    if cls == 0:
                        sk = self.hi | (sk & 0xFFFFFFFF)
                        loc = self.opivfl
                    else:
                        sk &= ~0xFFFFFFFF
                        loc = self.opifp
                elif cls == 1 and wasamb:
                    secbad = True
            fl = 0
            for which, text in zip(("FL", "BS"), parts[1:3]):
                if text == "":
                    continue
                anything = True
                if text.isdigit():
                    v = int(text)
                    if which == "FL":
                        if v > 64:
                            msgs.add(36)
                        fl = v & 63
                        flags.add("FLF")
                    else:
                        if v > 8:
                            msgs.add(37)
                        bs = v & 15
                        flags.add("BSF")
                elif text.isalnum() and text[0].isalpha():
                    coded += "1000100" + bits_of(len(text), 7) + a8_bits(text) + "0000"
                    flags.add("SFL" if which == "FL" else "SBS")
                    zifall = 0
                else:
                    return 10, msgs, loc, unit(), coded
            if anything:
                dds = (code << 10) | (fl << 4) | bs
                flags |= {"DDS", "DSF"}
                if cls == 3 and O.field(self.index(loc), 38, 1):
                    sk = self.hi | (sk & 0xFFFFFFFF)    # (,8): CHOSEN, VFL
                    loc = self.opivfl
        if secn >= 2:
            msgs, status = msgs | {4}, 7
        elif secbad:
            msgs, status = msgs | {2}, 7
        return status, msgs, loc, unit(), coded


# ---- the host oracle ------------------------------------------------------
HOSTF = ["ZIDDS", "ZIFDDS", "ZIFFLF", "ZIFSFL", "ZIFBSF", "ZIFSBS", "ZIFDSF", "ZIFPMN"]
MODEBITS = (1 << 12) | (1 << 10) | (1 << 45)    # VFL bits 51, 53; floating bit 18


def host_unit(stmt):
    """The host Pass 1 on one statement: None if it raises, else (messages,
    the fields of HOSTF, ZIOTPT, its op entry, a reader of the coded bits)."""
    p1 = Pass1([f"         {stmt}", "         END"])
    try:
        p1.run()
    except Exception:                   # noqa: BLE001
        return None
    u = p1.units
    un = u.first
    return ([n for n, *_ in p1.msg.items], {f: u.get(un, getattr(U, f)) for f in HOSTF},
            u.get(un, U.ZIOTPT), T.ENTRIES[u.get(un, U.ZIOPX)],
            lambda n: bits_of(p1.mem.get(un + U.FIXED_BITS, n), n) if n else "")


def unit_field(words, f):
    off, n = f
    w = words[off // 64]
    return (w >> (64 - off % 64 - n)) & ((1 << n) - 1)


# name, groups; and for a statement the guide oracle does not work (one not
# well formed), the text and (status, messages) wanted, with the page
CASES = [
    # no modifier: 4b-i's unit, unchanged
    ("LX", []), ("+", []), ("B", []), ("CW", []), ("DD", []),
    # p.23's own examples, and the classes of Fig. 24
    ("+", ["BU,3", "SEOP"]), ("CW", ["V+I"]), ("CW", ["CCR"]), ("CW", ["SCDSC"]),
    ("RD", ["SEOP"]), ("+", ["V-ICR"]), ("LX", ["SEOP"]), ("+I", ["V+I"]),
    # an ambiguous op settled: by a secondary, by a mode, both, either order
    ("+", ["V+I"]), ("L", ["V+IC"]), ("+", ["BU,8", "V+I"]), ("+", ["V+I", "BU,8"]),
    ("+", ["N", "V+I"]), ("+", ["V+I", "N"]), ("L", ["U", "V+I"]), ("M+1", ["V+I", "N"]),
    ("+", ["D,12,4"]), ("ST", ["DU"]), ("*", ["B"]), ("K", ["U"]), ("-", ["N"]),
    # two secondaries (4 before 2), too long
    ("+", ["V+I", "V-I"]), ("LX", ["SEOP", "SEOP"]), ("+", ["SEOP", "V+I"]),
    ("+", ["VERYLONGS"]), ("+", ["CX"]), ("+", ["V+ICRXX"]),
    # the dds: nulls, the substitutes, 64, the adjustments (36, 37)
    ("+", ["BU,8"]), ("+", [""]), ("+", [","]), ("L", [",24"]), ("+", [",8"]), ("+", ["BU,,4"]), ("+", ["BU"]),
    ("+", ["BU,64"]), ("+", ["BU,72"]), ("+", ["BU,8,9"]), ("+", ["BU,200,15"]),
    ("+", ["B,1,1"]), ("LX", ["BU,8"]), ("DD", ["BU,64"]), ("DD", ["N"]), ("M+1", ["BU,24,8"]),
    # symbolic fields: the coded expression stays, Ibuffw past it
    ("+", ["BU,A"]), ("+", ["BU,8,A"]), ("+", ["BU,ALPHA,BETA9"]), ("+", ["D,FL,4"]),
    ("L", ["N,X"]),
    # P-mode
    ("+", ["P,A"]), ("L", ["P,ALPHA1"]), ("DD", ["P,Q9"]),
    # two dds (message 5), a mode that is none (9), a field for VALUE (10)
    ("+", ["BU,8", "BU,4"]), ("+", ["XX"]), ("+", ["BUX"]), ("+", ["BU,4+4"]),
    ("+", ["BU,$1"]), ("+", ["BU,8,A+1"]),
    # EXT (Box 25)
    ("EXT", ["BU,8"]),
]
ILL_FORMED = [
    ("+(V+I,0", 7, {33}, "p.176: 33, the secondary not closed"),
    ("+(BU,8,0", 7, {35}, "p.176: 35, the dds not closed"),
    ("+(BU$),0", 7, {35}, "p.176: 35, the mode ended by neither , nor )"),
    ("+(P),0", 9, set(), "CHOSEN: P-mode with no symbol"),
    ("+(P,+A),0", 9, set(), "CHOSEN: a P-mode symbol starts alphameric"),
    ("+(P,A,B),0", 7, {35}, "p.176: 35"),
    ("+( BU , 8 )( V+I ),0", None, None, "blanks: as +(BU,8)(V+I)"),
]
# OPEN, for the table (4a-iii), not for Box 26.  The 7030 table gives these
# four names a one-family entry, not Fig. 23's ambiguous format: M+N, M+NMG
# and +N a floating one (with VFL's secondary code), +NMG a VFL one.  The
# host compiles the first three as VFL when a VFL dds or a secondary is
# written, and +NMG as floating with (N) or (U).  Box 26 cannot make an op
# VFL whose entry holds no VFL half, nor floating one that holds no floating
# half, so on the 7030 they stay as their entry has them.  Which is IBM's
# table is not settled here; the statements that differ are pinned so a
# change shows.
ONE_FAMILY = {"M+N", "M+NMG", "+N", "+NMG"}
ONE_FAMILY_DIFFERS = [
    "M+N(V+I),0", "M+N(BU,8),0", "M+N(B,24,8),0",
    "M+NMG(V+I),0", "M+NMG(BU,8),0", "M+NMG(B,24,8),0",
    "+N(V+I),0", "+N(BU,8),0", "+N(B,24,8),0",
    "+NMG(U),0", "+NMG(N),0"]
HOST_DIFFERS = {"+(BU,8)(BU,4),0": "two dds, p.176's message 5; the host none",
                # p.22: U and N are not first characters of a secondary, so
                # CW(U) is a dds on the 7030; the host takes any CW
                # parenthesis as a secondary, message 2.  (Message 34, "THIS
                # OP SHOULD NOT HAVE DDS", p.176, is not written: the guide
                # does not say which ops.)
                "CW(U),0": "a dds on CW; the host's message 2",
                "CW(N),0": "a dds on CW; the host's message 2"}
SWEEP = [["V+I"], ["SEOP"], ["CR"], ["BU,8"], ["B,24,8"], ["U"], ["N"]]


def text_of(name, groups):
    return name + "".join(f"({g})" for g in groups) + ",0"


def main():
    tb = O.Tables(printed_ops.optab_names()).layout()
    guide = Guide(tb)
    names = [n for n in tb.order if n not in ("", "EXT")]
    items = [(n, g) for n in names for g in SWEEP] + CASES
    stmts = [text_of(n, g) for n, g in items] + [s for s, *_ in ILL_FORMED]
    n_sweep = len(names) * len(SWEEP)

    k = min(CHUNKS, max(1, len(stmts) // 40))
    size = -(-len(stmts) // k)
    chunks = [stmts[i:i + size] for i in range(0, len(stmts), size)]
    # the first alone, so the shared model objects are built once
    results = [run_chunk(0, chunks[0])]
    with concurrent.futures.ThreadPoolExecutor(len(chunks)) as ex:
        results += list(ex.map(lambda t: run_chunk(*t), list(enumerate(chunks))[1:]))
    bad = [r for r in results if isinstance(r, str)]
    check(f"the runs: {len(chunks)} chunks, a record a statement, ERRC 0", bad[:2], [])
    if bad:
        return
    recs = [r for res in results for r in res[0]]
    uas = [res[1] for res in results for _ in res[0]]    # each record's unit address
    steps = sum(res[2] for res in results)

    bad_g = {"sweep": [], "cases": []}
    bad_h = {"sweep": [], "cases": []}
    nh = {"sweep": 0, "cases": 0}
    host_only, statuses, known = [], {}, []
    counted = {"messages": 0, "fields": 0, "ZIOTPT": 0, "op index": 0}
    pseudo_of = lambda n: T.lookup(n).pseudo                            # noqa: E731
    for i, (n, groups) in enumerate(items):
        where = "sweep" if i < n_sweep else "cases"
        s = stmts[i]
        r, ua = recs[i], uas[i]
        st, bop, r5, mmsg, ibuffw = r[0] >> 40, r[1], r[2] >> 40, r[3], r[4] >> 40
        unit, codew = r[5:13], r[13:]
        msgs = {b for b in range(64) if mmsg >> (63 - b) & 1}
        g_st, g_msgs, g_loc, g_unit, g_coded = guide.box26(n, groups)
        statuses[st] = statuses.get(st, 0) + 1
        got_coded = "".join(bits_of(w, 64) for w in codew)[:len(g_coded)]
        got = (st, sorted(msgs), bop, [hex(w) for w in unit])
        want = (g_st, sorted(g_msgs), O.name_word(n), [hex(w) for w in g_unit])
        if st in (0, 7):        # $5, Ibuffw and the coded bits: where Box 26 ran on
            got += (r5, ibuffw, got_coded)
            want += (g_loc << 6, (ua + 8) * 64 + len(g_coded), g_coded)
        if got != want:
            bad_g[where].append((s, got, want))
        # the host
        h = host_unit(s)
        if s in HOST_DIFFERS:
            host_only.append((s, "differs: " + HOST_DIFFERS[s]))
            continue
        if st in (9, 10):
            host_only.append((s, f"the 7030 stand-in stops, status {st}"))
            continue
        if h is None or not (set(h[0]) <= {36, 37} or h[0] in ([2], [4])):
            host_only.append((s, "the host raises" if h is None else f"the host's {h[0]}"))
            continue
        hmsgs, hf, hz, he, hbits = h
        nh[where] += 1
        counted["messages"] += 1
        diff = []
        if set(hmsgs) != msgs:
            diff.append(("messages", sorted(msgs), hmsgs))
        if st == 0 and not set(hmsgs) & {2, 4}:
            pmode = unit_field(unit, U.ZIFPMN)
            for f in HOSTF:
                if pmode and f in ("ZIDDS", "ZIFDSF"):
                    continue
                if unit_field(unit, getattr(U, f)) != hf[f]:
                    diff.append((f, unit_field(unit, getattr(U, f)), hf[f]))
            loc = unit[5] >> O.LOC_SHIFT
            key = tb.indexes[loc - tb.idx] if 0 <= loc - tb.idx < len(tb.indexes) else None
            amb = key is not None and O.field(tb.index_word(key), 38, 1)
            if amb and (unit_field(unit, U.ZIFDDS) or any(g[:1] and g[:1] in "VSC" for g in groups)):
                amb = False         # Box 26 should have settled it: compare all
            counted["fields"] += 1
            counted["ZIOTPT"] += not pseudo_of(n)
            pseudo = pseudo_of(n)
            if not pseudo:
                m = ~MODEBITS & ((0xFFFFFFFF if amb else ~0) & (1 << 64) - 1)
                if unit[6] & m != hz & m:
                    diff.append(("ZIOTPT", hex(unit[6]), hex(hz)))
            if he.ambiguous:
                # the host keeps an ambiguous op on its one entry, the VFL
                # skeleton with ZOAMB on; a unit Box 26 settled is the VFL one
                he = T.lookup(n, "BU")
            hkey = (O.question_bits(he), 0 if he.kind == "fp" and T.lookup(n).ambiguous
                    else O.secondary_code(n), tuple(he.fills))
            if not amb and not (pseudo and not he.pseudo):
                counted["op index"] += 1
                if key != hkey:
                    diff.append(("op index", key, hkey))
            if not pmode and got_coded != hbits(len(g_coded)):
                diff.append(("coded", got_coded, hbits(len(g_coded))))
        if diff and n in ONE_FAMILY:
            known.append(s)
        elif diff:
            bad_h[where].append((s, diff))
    check(f"guide, the sweep: {n_sweep} statements ({len(names)} names x {len(SWEEP)}), "
          "status, messages, Bop, $5, Ibuffw, the eight words bit for bit", bad_g["sweep"][:4], [])
    check(f"host, the sweep: {nh['sweep']} statements, the messages (and Box 26's fields "
          "where the unit stands)",
          bad_h["sweep"][:4], [])
    check("host, the sweep: the four names of ONE_FAMILY differ from the host in just these",
          sorted(known), sorted(ONE_FAMILY_DIFFERS))
    check(f"guide, the cases: {len(CASES)} statements, the same and the coded bits",
          bad_g["cases"][:4], [])
    check(f"host, the cases: {nh['cases']} statements, the messages (and Box 26's fields "
          "where the unit stands)",
          bad_h["cases"][:4], [])
    base = len(items)
    for j, (s, want_st, want_m, why) in enumerate(ILL_FORMED):
        r = recs[base + j]
        msgs = {b for b in range(64) if r[3] >> (63 - b) & 1}
        if want_st is None:     # the same record as its plain spelling
            k = stmts.index("+(BU,8)(V+I),0")
            check(f"{s!r}: {why}", r[:3] + r[5:], recs[k][:3] + recs[k][5:])
        else:
            check(f"{s!r} gives status {want_st}, messages {sorted(want_m)} ({why})",
                  (r[0] >> 40, msgs), (want_st, want_m))
    # the named behaviours, one check each, so an injection shows by name
    by = {stmts[i]: recs[i] for i in range(len(items))}
    ua_of = {stmts[i]: uas[i] for i in range(len(items))}

    def got(s):
        r = by[s]
        return (r[0] >> 40, sorted(b for b in range(64) if r[3] >> (63 - b) & 1))
    check("p.23: +(BU,3)(SEOP) and CW(V+I) are message 2",
          (got("+(BU,3)(SEOP),0"), got("CW(V+I),0")), ((7, [2]), (7, [2])))
    check("p.23: +(V+I) is the VFL unit: OPIVFL in ZIOPX and $5, the VFL skeleton",
          (by["+(V+I),0"][10] >> O.LOC_SHIFT, by["+(V+I),0"][2] >> 46, hex(by["+(V+I),0"][11])),
          (guide.opivfl, guide.opivfl,
           hex(guide.hi | (guide.word2["+"] & 0xFFFFFFFF) | (1 << 29))))
    check("p.176: two secondaries are message 4, two dds message 5",
          (got("+(V+I)(V-I),0"), got("+(SEOP)(V+I),0"), got("+(BU,8)(BU,4),0")),
          ((7, [4]), (7, [4]), (7, [5])))
    check("the host's rule: a floating mode and a secondary, either order, message 2",
          (got("+(N)(V+I),0"), got("+(V+I)(N),0")), ((7, [2]), (7, [2])))
    check("p.23: +(BU,A) keeps its coded expression: ZIFSFL on, ZIFALL off, Ibuffw past it",
          (unit_field(by["+(BU,A),0"][5:13], U.ZIFSFL), unit_field(by["+(BU,A),0"][5:13], U.ZIFALL),
           (by["+(BU,A),0"][4] >> 40) - (ua_of["+(BU,A),0"] + 8) * 64), (1, 0, 26))
    check("p.23: +(BU,8) erases its coded expression: Ibuffw as it was, ZIFALL on",
          ((by["+(BU,8),0"][4] >> 40) - (ua_of["+(BU,8),0"] + 8) * 64,
           unit_field(by["+(BU,8),0"][5:13], U.ZIFALL)), (0, 1))
    check("p.23: +(P,ALPHA1)'s ZILPMS is the symbol's 48 bits",
          unit_field(by["L(P,ALPHA1),0"][5:13], U.ZILPMS), 48)
    check("CHOSEN: +(,8) makes the ambiguous op VFL, as +(BU,8): ZIOPX, $5 and ZIOTPT",
          (by["+(,8),0"][10], by["+(,8),0"][2], hex(by["+(,8),0"][11])),
          (by["+(BU,8),0"][10], by["+(BU,8),0"][2], hex(by["+(BU,8),0"][11])))
    check("Box 25: EXT(BU,8) is status 6 and the unit Box 23's", got("EXT(BU,8),0"), (6, []))
    print(f"INFO host rows compared: {counted} (messages for every row; the dds fields where "
          "the unit stands, status 0 and no 2 or 4; ZIOTPT but for pseudo-ops; the op index "
          "but where the unit is still ambiguous with no dds or secondary, and LINK)")
    m1 = {}
    for s, why in host_only:
        if why == "the host's [1]":
            n = s.split("(")[0]
            e = T.lookup(n)
            k = ("ambiguous " if e.ambiguous else "") + e.kind
            m1[k] = m1.get(k, 0) + 1
    print(f"INFO the host's message-1 rows by the entry's kind: {dict(sorted(m1.items()))}")
    print(f"INFO statuses: {dict(sorted(statuses.items()))}")
    kinds = {}
    for s, why in host_only:
        kinds[str(why)] = kinds.get(str(why), 0) + 1
    print(f"INFO checked by the guide oracle alone (the host raises or gives another message): "
          f"{len(host_only)} {dict(sorted(kinds.items()))}")
    print(f"INFO model steps: {steps} in {len(chunks)} chunks")


if __name__ == "__main__":
    main()
    if fails:
        print(f"*** {fails} CHECK(S) FAILED ***")
        sys.exit(1)
    print("ALL CHECKS PASSED")
