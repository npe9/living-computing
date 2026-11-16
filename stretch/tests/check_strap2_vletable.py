"""check_strap2_vletable.py -- the host STRAP II's vle table walks, on every deck.

C22-6729 p.13 (read in the ink): a symbol's vle "contains ... information about
the symbol such as its data description, and its value or the coded expression
of the value of the symbol"; ANEXT (pp.50-51) steps the vle table by each vle's
13-bit length (Fig. 22 p.191).  So after every assembly the table must walk
from Auvbot to exactly Auvtab, every vle must be one of the kinds the host
makes (S symbol, Y special, D dimensions, Fig. 22), every coded expression a
symbol points at (ZEXPR, ZFLX, ZBSX) must lie inside that symbol's own vle,
and every ZDIMX inside a D vle.  symtab.py's header gives the layout and what
in it is CHOSEN.

Run from stretch/tests with PYTHONDONTWRITEBYTECODE=1.

MEASURED INJECTIONS, 2026-11-15, restored by copy and cmp, control (all 733
decks walk) passing:
  extend does not grow the vle's length     462 decks do not walk, 2 do not
                                            assemble, 269 walk
  extend writes a headless block (the old   the same: 462 do not walk
    store_coded layout)
  the D vle written with ID S               92 decks bad (ZDIMX not in a D vle)
  a DR's dimensions appended to its own vle 92 decks bad, the same
"""
import glob
import os
import sys
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
sys.path.insert(0, HERE)

fails = 0


def check(name, got, want):
    global fails
    if got == want:
        print(f"PASS {name}")
    else:
        fails += 1
        print(f"FAIL {name}: got {got!r}, want {want!r}")


def one(path):
    import strap_asm
    import strap2
    from strap2.cards import deck_cards
    from strap2.symtab import A6_ID, SymbolError
    base = os.path.basename(path)
    try:
        p2 = strap2.compile_cards(deck_cards(open(path).read()), strap_asm.DEFAULT_ORIGIN_BITS)
    except Exception:          # noqa: BLE001  refusing to assemble is not ours
        return base, "not assembled", ""
    st = p2.st
    try:
        walked = st.walk()
    except SymbolError as x:
        return base, "does not walk", str(x)
    ids = {A6_ID[k]: k for k in ("S", "Y", "D")}
    bad = []
    ends = {}
    for (v, ident), nxt in zip(walked, [w for w, _ in walked[1:]] + [st.t.auvtab]):
        if ident not in ids:
            bad.append(f"ID {ident:o} at {v}")
        ends[v] = (nxt, ids.get(ident))
    starts = sorted(ends)
    import bisect

    def owner(addr):
        i = bisect.bisect_right(starts, addr) - 1
        return starts[i] if i >= 0 else None

    for f in st.vles:
        home = owner(f)
        if home is None or ends[home][1] not in ("S", "Y"):
            bad.append(f"function {f} not in an S or Y vle")
            continue
        for fld in ("ZEXPR", "ZFLX", "ZBSX"):
            a = st.get(f, fld)
            if a and owner(a) != home:
                bad.append(f"{fld} of {st.name_of.get(f)!r} outside its vle")
        a = st.get(f, "ZDIMX")
        if a and ends.get(owner(a), (0, None))[1] != "D":
            bad.append(f"ZDIMX of {st.name_of.get(f)!r} not in a D vle")
    if bad:
        return base, "bad", bad[:3]
    return base, "walks", len(walked)


if __name__ == "__main__":
    counts = {}
    with ProcessPoolExecutor() as ex:
        for base, how, detail in ex.map(one, sorted(glob.glob(os.path.join(HERE, "..", "decks", "*.strap")))):
            counts[how] = counts.get(how, 0) + 1
            if how in ("does not walk", "bad"):
                print(f"   {base}: {how}: {detail}")
    print(f"INFO {counts}")
    check("every assembled deck's vle table walks, kinds and pointers in place",
          (counts.get("does not walk", 0), counts.get("bad", 0)), (0, 0))
    check("the decks walked", counts.get("walks", 0), 801)   # 801: 748 with the fourteen C22-6578 ch.2 decks, then the nine Buchholz App. B decks (757), then the C22-6578 ch.3 and ch.4 decks (792), then index_after_index_store (793), then vfl_divide_box (794), then repro_cm_indicator_bit (795), then the four C22-6578 4.6 decks (799), then the two 4.7 decks (801)
    print("ALL CHECKS PASSED" if not fails else f"{fails} FAILED")
    sys.exit(1 if fails else 0)
