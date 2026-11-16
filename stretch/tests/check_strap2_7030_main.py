#!/usr/bin/env python3
"""check_strap2_7030_main.py -- the 7030 STRAP II's MAIN, Boxes 2-24
(decks/strap2_7030.strap, step 4b-i; Chart AA p.14, pp.19-22, read in the
ink 2026-11-15), run on the Bluespec model over one statement a card.

THE ORACLES.  For every name of the 7030 op table, "NAME,0":
  table      Bop is the name in A8, blank-filled; ZIOPX's bits 0-17 and $5
             are the op index's location, and ZIOTPT the entry's second
             word with those bits cleared -- what optab7030 laid out
  host       for a name that is neither ambiguous nor a pseudo-op, and that
             the host STRAP II compiles as "NAME,0" without a message: the
             host Pass 1 unit's ZIOTPT, and the op index at the unit's
             location against the index key of the host's entry
             (ENTRIES[ZIOPX]).  A name the host folds into another entry
             (SUSEOP into LOC, SEOP in the skeleton) is compared but for the
             secondary-code field, which the 7030 table sets to 0.  The
             host's ZIOPX is its own entry number, so it is compared
             through that map, not bit for bit (CHOSEN for 4b-i; the
             host's unit moves to Box 23's representation when the unit
             file must match bit for bit, step 4e).
  the rest   every other fixed-format word is zero but ZIFALL (Box 2)
and the stand-ins: a branch-on-indicator op and a misspelling (status 5,
MIBA and MBSPEC not written), nine op characters (5), a modifier (LX(SEOP):
since step 4b-ii Box 26 runs, and this one is status 7, message 2, with
Box 23 done; it was status 6 when Box 24 stopped), an illegal character first (2) and in the op (2), ( first
(3), ' first (4), the null op ",0" (Box 8 to Box 17: the table holds it,
p.21), and two statements on one card (Box 38 stops at the real
semicolon).

Run from stretch/tests with PYTHONDONTWRITEBYTECODE=1.

MEASURED INJECTIONS, 2026-11-15, into MAIN in the deck, restored from a copy
checked with cmp; control: all checks pass, 12,662,727 model steps.
  Box 23 keeps bits 0-17 in ZIOTPT   FAIL table, host
  the op limit is eight characters   FAIL table, host (SPFLSEOP and the
                                     other 8-character names: status 5)
  Box 8's comma not the null op      FAIL table, host, stand-in: null op
  Box 38 does not stop at ;          FAIL one record a statement (1 of 483:
                                     the whole deck read as one statement)
  NOTHING: the op limit as ten.  "ABCDEFGHI" is not in the table either way,
  so it is status 5 at any limit above eight; the ninth character's store
  past BOP is not seen by these checks.  The ninth-character rule is CHOSEN
  and stays unproven here.
"""
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
from strap2.cards import deck_cards                 # noqa: E402
from strap2.pass1 import Pass1                      # noqa: E402
from strap2.unit import ZIOPX, ZIOTPT              # noqa: E402
from check_strap2_7030 import BSV, card, iqs_words  # noqa: E402
import printed_ops                                  # noqa: E402

DECK = os.path.join(HERE, "..", "decks", "strap2_7030.strap")
MODULE = "StretchStrap2x7030MainTb"
STEPS = 60000000
REC = 11                    # status, Bop, $5, the unit's eight words
fails = 0


def check(label, got, want):
    global fails
    if got == want:
        print(f"PASS {label}")
    else:
        fails += 1
        print(f"FAIL {label}: got {str(got)[:700]}, want {str(want)[:300]}")


DRIVER = """START   SIC, XINLK
        B, XINPUT
        LVI, $9, OUTR
MD1     SV, $9, MDP
        LVI, $9, UNITA
        SV, $9, IBUFFW
        SIC, MAINLK
        B, MAIN
        LV, $9, MDP
        L(BU,24), MSTAT
        KI(BU,24), 1
        BAE, DONE
        ST(BU,24), 0.0($9)
        L(BU,64), BOP
        ST(BU,64), 1.0($9)
        SV, $5, 2.0($9)
""" + "".join(f"""        L(BU,64), UNITA+{k}.0
        ST(BU,64), {3 + k}.0($9)
""" for k in range(8)) + """        V+I, $9, {rec}.0
        M+1(BU,24), OUTN
        B, MD1
DONE    BEW, $
        CNOP
MDP     DD(BU,64), 0
UNITA   DRZ(BU,64), 8
OUTN    DD(BU,64), 0
OUTR    DRZ(BU,64), {n}
"""


def deck_text(cards):
    src = open(DECK).read()
    rows = []
    for c in cards:
        rows += [f"        DD(BU,64), (16){w:016X}" for w in iqs_words(c)]
    src = src.replace("INX     XW, INB, 0, 0\n", f"INX     XW, INB, {len(cards)}, 0\n", 1)
    assert src.endswith("        END\n")
    return (src[:-len("        END\n")] + "\n".join(rows) + "\n" +
            DRIVER.format(n=REC * (len(cards) + 4), rec=REC) + "        END, START\n")


def host_unit(stmt):
    """The host Pass 1's unit for one statement: (messages, ZIOTPT, entry)."""
    p1 = Pass1([f"         {stmt}", "         END"])
    try:
        p1.run()
    except Exception as x:              # noqa: BLE001
        return ("raise", str(x)[:60]), None, None
    msgs = [n for n, *_ in p1.msg.items]
    u = p1.units
    return msgs, u.get(u.first, ZIOTPT), T.ENTRIES[u.get(u.first, ZIOPX)]


def main():
    tb = O.Tables(printed_ops.optab_names()).layout()
    names = list(tb.order)
    word2 = {n: tb.primary_word2(n) for n in names}
    LOCMASK = ((1 << 18) - 1) << O.LOC_SHIFT

    stmts = [(n, f"{n},0") for n in names]
    special = [("BAE", "BAE,0", 5), ("too long", "ABCDEFGHI,0", 5),
               ("modifier", "LX(SEOP),$1,0", 7), ("illegal first", ")X,0", 2),
               ("illegal in op", "LX)Y,0", 2), ("entry mode", "(A)DD,0", 3),
               ("quote", "'COMMENT", 4), ("null op", ",0", 0)]
    cards = [card(" ", "", s) for _, s in stmts] + [card(" ", "", s) for _, s, _ in special]
    cards.append(card(" ", "", "B,0;LX,$1,0"))
    text = deck_text(cards)
    p2 = strap2.compile_cards(deck_cards(text), strap_asm.DEFAULT_ORIGIN_BITS)
    word = lambda n: p2.val.symbol_value(p2.st.search(n))[0] // 64      # noqa: E731
    out = word("OUTR")
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, MODULE + ".strap")
        with open(path, "w") as fh:
            fh.write(text)
        args = [os.path.join(HERE, "run_program.sh"), path, MODULE, "ASM=strap2",
                f"DUMP={out - 1},{1 + REC * (len(cards) + 2)}",
                f"STEPS={STEPS}", f"CYCLES<={STEPS}",
                f"FASTLOAD={os.path.join(tmp, MODULE + '.hex')}",
                f"ERRC:{word('ERRC')}=0x0"]
        r = subprocess.run(args, capture_output=True, text=True, cwd=HERE)
    for name in os.listdir(BSV):            # by exact name, never a glob
        if name in (MODULE + ".bsv", MODULE + "_sim", MODULE + "_sim.so"):
            os.remove(os.path.join(BSV, name))
    o = r.stdout
    if r.returncode or "step cap" in o:
        check("the run", (o + r.stderr)[-1500:], "ok")
        return
    mem = {int(a): int(v, 16) for a, v in re.findall(r"MEMDUMP (\d+) ([0-9a-f]+)", o)}
    n_out = mem.get(word("OUTN"), 0) >> 40
    recs = [[mem.get(out + REC * k + j, 0) for j in range(REC)] for k in range(n_out)]
    check("ERRC is 0", bool(re.search(r"^PASS ERRC", o, re.M)), True)
    check("one record a statement (two on the last card)", n_out, len(cards) + 1)
    status = lambda rec: rec[0] >> 40                                    # noqa: E731
    ZIFALL_ONLY = 1 << (63 - 25)

    bad_t, bad_z, bad_h, nh, skipped, folded = [], [], [], 0, [], []
    for k, (n, s) in enumerate(stmts):
        st, bop, r5 = recs[k][:3]
        unit = recs[k][3:]
        w5, w6 = unit[5], unit[6]
        w2 = word2[n]
        got = (status(recs[k]), bop, w5, w6, r5 >> 40)
        want = (0, O.name_word(n), w2 & LOCMASK, w2 & ~LOCMASK, (w2 >> O.LOC_SHIFT) << 6)
        if got != want:
            bad_t.append((n, got, want))
        if [unit[j] for j in (0, 1, 2, 3, 4, 7)] != [0, 0, 0, ZIFALL_ONLY, 0, 0]:
            bad_z.append((n, [hex(unit[j]) for j in (0, 1, 2, 3, 4, 7)]))
        e = T.lookup(n)
        if e.ambiguous or e.pseudo:
            continue
        msgs, hz, he = host_unit(s)
        if msgs or he is None:
            skipped.append(n)
            continue
        nh += 1
        hkey = tb._index_key(he.name, he)
        loc = w5 >> O.LOC_SHIFT
        got_key = tb.indexes[loc - tb.idx] if 0 <= loc - tb.idx < len(tb.indexes) else None
        if he.name != n and n.endswith("SEOP"):
            # FOLDED: the host takes "SUSEOP" as LOC's entry with SEOP in the
            # skeleton (so ZIOTPT still agrees); the 7030 table gives the
            # name its own op index, the same but for the secondary code
            # (0: SEOP is already written, so no secondary follows).
            folded.append(n)
            same = got_key is not None and (got_key[0], got_key[2]) == (hkey[0], hkey[2])
        else:
            same = got_key == hkey
        if w6 != hz or not same:
            bad_h.append((n, hex(w6), hex(hz), loc, got_key, hkey))
    check(f"table: every one of the {len(stmts)} names, Bop, ZIOPX, ZIOTPT and $5 as laid out",
          bad_t[:6], [])
    check("Box 2: words 0-4 and 7 zero but ZIFALL", bad_z[:6], [])
    check(f"host: {nh} instructions' ZIOTPT and op index equal the host Pass 1 unit's",
          bad_h[:6], [])
    print(f"INFO host comparison skipped (host message or no unit): {len(skipped)} {skipped[:12]}")
    print(f"INFO folded by the host into another entry (...SEOP, op index compared but for the secondary code): {len(folded)} {folded[:12]}")
    base = len(stmts)
    for i, (label, s, want) in enumerate(special):
        check(f"stand-in: {label} {s!r} gives status {want}", status(recs[base + i]), want)
    k = base + [lab for lab, _, _ in special].index("modifier")
    check("modifier: Box 23 done before Box 24 (LX's op index)",
          recs[k][3 + 5], word2["LX"] & LOCMASK)
    k = base + len(special)
    check("two statements on a card: B then LX",
          (recs[k][1], recs[k + 1][1]), (O.name_word("B"), O.name_word("LX")))
    m = re.search(r"cycles = (\d+)", o)
    print(f"INFO model steps: {m.group(1) if m else '?'}")


if __name__ == "__main__":
    main()
    if fails:
        print(f"*** {fails} CHECK(S) FAILED ***")
        sys.exit(1)
    print("ALL CHECKS PASSED")
