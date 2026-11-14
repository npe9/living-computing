#!/usr/bin/env python3
"""check_strap2_tabman.py -- the host TABMAN (strap/strap2/tabman.py), C22-6729
pp.40-53, docs/strap2_7030.md step 3a.

The control block is read here at Fig. 8 p.44's printed bit positions (FX 0.0,
DX 1.0, FW 2.0, ID 2.25, LW 2.32, TO 2.57, TM 2.58, TEC 2.62, EL 3.0, AL 3.16,
ADDL 3.32, N 3.48), not through tabman.py's own field table, so a misreading
shared by the two would not pass.  Each check names the page it rests on.

MEASURED INJECTIONS into tabman.py, 2026-11-13 (re-measured after SEARCH
became chart-literal), restored by copy and cmp, PYTHONDONTWRITEBYTECODE=1,
control all passing; the number of failing checks, then the first:
  a deleted match found                     4: SEARCH deleted, ADDORD ...
  an unordered search skips deleted equals  1: unordered first equal
  ADDUNO never replaces a deleted last      3: ADDUNO replaced, LW, ...
  ADDORD on an unordered table: normal      1: ADDORD unordered
  not found, ordered: after the table       11: ADDORD order, DX, ...
  ANEXT ignores Afirst                      1: ANEXT restarts
  RSERCH's index not advanced               1: RSERCH with an index
  EL not rounded to a half word             16: EL at 3.0, ...
  ADDORD inserts without moving the table   13
  the function field holds the function's   5: the vle's signed address,
    address                                    FX Agetv, RSERCH x3
  ADDUNO leaves TO                          1: ADDUNO marks ordered
  ANEXT takes a deleted vle                 1: ANEXT deleted
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
from strap2 import tabman as T          # noqa: E402

fails = 0


def check(label, got, want):
    global fails
    ok = got == want
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} {label}" + ("" if ok else f": got {got!r}, want {want!r}"))


CB = 64 * 100           # the control block
FW = 64 * 200           # the first entry
IND = 0o22


def fig8(t, name):
    """A control-block field at Fig. 8's printed position (word.bit, bits)."""
    word, bit, n = {"FX": (0, 0, 24), "DX": (1, 0, 24), "FW": (2, 0, 24),
                    "ID": (2, 25, 6), "LW": (2, 32, 24), "TO": (2, 57, 1),
                    "TM": (2, 58, 1), "TEC": (2, 62, 1), "EL": (3, 0, 16),
                    "AL": (3, 16, 16), "ADDL": (3, 32, 16), "N": (3, 48, 16)}[name]
    return t.mem.get(CB + 64 * word + bit, n)


def args(t):
    return [(t.mem.get(e + 2, 32), t.mem.get(e, 1)) for e in
            range(fig8(t, "FW"), fig8(t, "LW") + 1, fig8(t, "EL"))]


def table(ordered=True, addl=6):
    t = T.new()
    t.define(CB, FW, IND, 32, addl, ordered)
    return t


# Fig. 8 and EL (CHOSEN: 2 + AL + ADDL to a half word)
t = table()
check("Fig. 8: FW at 2.0", fig8(t, "FW"), FW)
check("Fig. 8: ID at 2.25", fig8(t, "ID"), IND)
check("Fig. 8: AL 3.16, ADDL 3.32", (fig8(t, "AL"), fig8(t, "ADDL")), (32, 6))
check("EL at 3.0: an indicator entry, 2+32+6 bits, is two half words (CHOSEN)",
      fig8(t, "EL"), 64)
check("an empty ordered table: N 0, TO 0", (fig8(t, "N"), fig8(t, "TO")), (0, 0))

# ADDORD in order (p.48)
got = [t.addord(CB, a, 32, a + 100, 6) for a in (50, 30, 90, 70)]
check("ADDORD: four new arguments, each the normal exit", got, ["normal"] * 4)
check("ADDORD: the table ascending (p.48 restriction 1)", args(t),
      [(30, 0), (50, 0), (70, 0), (90, 0)])
check("ADDORD: N at 3.48 counts them", fig8(t, "N"), 4)
check("ADDORD: LW at 2.32 is the last entry", fig8(t, "LW"), FW + 3 * 64)
check("ADDORD: DX locates the entry just put in (p.48)", fig8(t, "DX"), FW + 2 * 64)
check("ADDORD: its function, 76 in 6 bits, after the argument",
      t.mem.get(FW + 2 * 64 + 34, 6), 170 % 64)
check("ADDORD: the same argument again is 'already there'",
      t.addord(CB, 50, 32, 1, 6), "already there")
check("  and DX locates the equal item (p.48)", fig8(t, "DX"), FW + 64)
check("  and N is unchanged", fig8(t, "N"), 4)

# SEARCH (p.47)
check("SEARCH 70: found", t.search(CB, 70, 32), "found")
check("  DX the entry, FX its function (p.47)", (fig8(t, "DX"), fig8(t, "FX")),
      (FW + 128, FW + 128 + 34))
check("SEARCH 60, ordered: not found", t.search(CB, 60, 32), "not found")
check("  the index words locate the next higher entry, 70 (p.47)",
      (fig8(t, "DX"), fig8(t, "FX")), (FW + 128, FW + 128))
check("SEARCH 99, ordered, above all: the location after the table",
      (t.search(CB, 99, 32), fig8(t, "DX")), ("not found", FW + 256))

# the delete mark (Box 11; Fig. 21's bit 0)
t.delete(CB, FW + 64)
check("a deleted entry: bit 0 of the entry, N one less", (t.mem.get(FW + 64, 1), fig8(t, "N")), (1, 3))
check("SEARCH: a deleted match is a miss (Box 11)", t.search(CB, 50, 32), "not found")
check("ADDORD: a deleted equal argument does not stop a new one",
      t.addord(CB, 50, 32, 7, 6), "normal")
check("  the new one stands before the deleted one (the index words' place)", args(t),
      [(30, 0), (50, 0), (50, 1), (70, 0), (90, 0)])
check("  and SEARCH now finds the new one", (t.search(CB, 50, 32), fig8(t, "DX")),
      ("found", FW + 64))
x = table(ordered=False)
for a in (4, 6, 4):
    x.adduno(CB, a, 32, a, 6)
x.delete(CB, FW)
check("unordered: the first equal argument deleted is a miss, though a later "
      "one is not (Boxes 7, 11)", x.search(CB, 4, 32), "not found")

# ADDUNO (p.49)
u = table(ordered=False)
got = [u.adduno(CB, a, 32, a, 6) for a in (9, 3, 7)]
check("ADDUNO: the normal exit", got, ["normal"] * 3)
check("ADDUNO: entries in the order given, TO 1 at 2.57", (args(u), fig8(u, "TO")),
      ([(9, 0), (3, 0), (7, 0)], 1))
check("SEARCH 5, unordered: not found, the location after the table (p.47)",
      (u.search(CB, 5, 32), fig8(u, "DX")), ("not found", FW + 3 * 64))
u.delete(CB, FW + 2 * 64)
u.adduno(CB, 4, 32, 4, 6)
check("ADDUNO: a deleted last entry is replaced (p.49, Boxes 19, 28)", args(u),
      [(9, 0), (3, 0), (4, 0)])
check("  LW unchanged, N back to 3", (fig8(u, "LW"), fig8(u, "N")), (FW + 128, 3))
u.adduno(CB, 8, 32, 8, 6)
check("ADDUNO: otherwise after the last entry, LW one entry on (Box 27)",
      (args(u)[-1], fig8(u, "LW")), ((8, 0), FW + 192))

# ADDORD on an unordered table (p.48): added at the end, the error exit
check("ADDORD, unordered table: the error exit (p.48)", u.addord(CB, 1, 32, 1, 6), "error")
check("  and the entry is at the end", args(u)[-1], (1, 0))

# ADDUNO marks an ordered table unordered (p.49 item 2)
o = table()
o.addord(CB, 5, 32, 5, 6)
o.adduno(CB, 2, 32, 2, 6)
check("ADDUNO on an ordered table marks it unordered (TO 1)", fig8(o, "TO"), 1)

# a function longer than ADDL: a vle (p.44, Fig. 22)
v = table(addl=25)
bottom = v.auvbot
v.addord(CB, 11, 32, 0b101, 40)
e = FW
check("a vle: the entry's bit 1 on (Fig. 21)", v.mem.get(e + 1, 1), 1)
check("  its function field is the vle's signed address (Fig. 21)",
      v.mem.get_signed(e + 34, 25), bottom)
check("  the vle head: deleted 0, length 32+40, ID, remainder length 0 (Fig. 22)",
      (v.mem.get(bottom, 1), v.mem.get(bottom + 1, 13), v.mem.get(bottom + 14, 6),
       v.mem.get(bottom + 20, 12)), (0, 72, IND, 0))
check("  the function in it", v.mem.get(bottom + 32, 40), 0b101)
check("  FX is the function's address (Agetv, Boxes 20-25)", fig8(v, "FX"), bottom + 32)
check("  Auvtab one vle on (p.45)", v.auvtab, bottom + 72)
v.addord(CB, 12, 32, 3, 40)
v.addord(CB, 13, 32, 4, 40)

# ANEXT (pp.50-51)
other = bottom + 72
v.mem.put(other + 14, 6, 0o30)                  # a vle of another table
check("ANEXT: the first vle with the ID", (v.anext(IND), v.anextx), ("normal", bottom))
check("ANEXT: skips another ID", (v.anext(IND), v.anextx), ("normal", bottom + 144))
check("ANEXT: then no more", v.anext(IND), "no more")
v.afirst = True
check("ANEXT: Afirst on restarts at the vle table's start (p.51)",
      (v.anext(IND), v.anextx), ("normal", bottom))
v.mem.put(bottom + 144, 1, 1)
v.afirst = True
v.anext(IND)
check("ANEXT: a deleted vle is passed over (p.53 Boxes 8, 9)", v.anext(IND), "no more")

# RSERCH (pp.52-53)
check("RSERCH: the entry whose function is at bottom+72+32",
      v.rserch(CB, bottom + 104), ("found", None))
check("  DX the entry", fig8(v, "DX"), FW + 64)
check("RSERCH: an address no entry has", v.rserch(CB, bottom + 1)[0], "not found")
dest = 64 * 300
got = v.rserch(CB, bottom + 32, dest)
check("RSERCH with an index: the entry moved there, the value one entry on (p.53)",
      (got, v.mem.get(dest + 2, 32)), (("found", dest + 64), 11))

# the exits, in bits from tbl (p.46: B,-1($15) one half word back)
check("exits: SEARCH found at 2.0, not found at 1.32 (p.47)",
      (T.EXITS[("SEARCH", "found")], T.EXITS[("SEARCH", "not found")]), (128, 96))
check("exits: ADDORD already 2.32, error 3.0, normal 3.32 (p.48; Gap 11 CHOSEN)",
      tuple(T.EXITS[("ADDORD", k)] for k in ("already there", "error", "normal")),
      (160, 192, 224))
check("exits: ADDUNO normal 2.32 (p.49), ANEXT no more 0.32, normal 1.32 (p.51)",
      (T.EXITS[("ADDUNO", "normal")], T.EXITS[("ANEXT", "no more")],
       T.EXITS[("ANEXT", "normal")]), (160, 32, 96))

# fail loud
try:
    w = table()
    w.put(CB, "TEC", 1)
    w.search(CB, 1, 32)
    got = "accepted"
except T.TabmanError:
    got = "refused"
check("TEC 1, a compare the guide does not describe, is refused", got, "refused")

print("ALL CHECKS PASSED" if not fails else f"{fails} FAILED")
sys.exit(1 if fails else 0)
