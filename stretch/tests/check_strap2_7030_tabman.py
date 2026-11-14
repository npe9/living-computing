#!/usr/bin/env python3
"""check_strap2_7030_tabman.py -- the 7030 TABMAN (decks/strap2_7030.strap,
SEARCH, ADDORD, ADDUNO, ANEXT, RSERCH), assembled by the host STRAP II and run on the
Bluespec model, against the host TABMAN (strap/strap2/tabman.py),
docs/strap2_7030.md step 3b.

>>> Both are RECONSTRUCTIONS of IBM's TABMAN to C22-6729 pp.40-53. <<<

The driver (generated here, NOT part of the reconstruction) makes each call
with the printed calling sequence, LVI,$15,$+1.0; B,<routine>; ,tbl ...,
and records after it: which exit was taken, the control block's four words,
and $0-$7 (TABMAN saves and restores them, Boxes 1-3, 31).  The host
replays the same calls at the same bit addresses.  Compared: every exit,
every control-block snapshot at Fig. 8's positions, the registers, and at
the end the tables and the vle area bit for bit.

MEASURED INJECTIONS into the deck, 2026-11-13, restored by copy and cmp,
control all passing; the number of failing checks, then the first calls:
  Acompi not done (compares 64 bits)        22: calls 4-6 ...
  a deleted match found                     8: calls 10-12 ...
  ordered: no stop at a higher entry        16: calls 1, 3-6 ...
  unordered deleted miss: index at entry    1: call 19 SEARCH T2 7
  ADDUNO never replaces a deleted last      5: calls 20-23, table 2
  ADDORD does not move the table up         15: calls 4-6 ...
  TBMOV always forward                      4: call 27, tables 1 and 3
  $4 not restored                           30: every call
  ADDORD's normal at 3.0 (Box 9 as drawn)   9: calls 0-3, 11 ...
  Agetv without the vle head                3: calls 24, 25, 27
  N not counted                             30
  ADDUNO leaves TO                          3: calls 30, 31
  the vle's ID not written                  1: the vle area
(The unordered deleted-miss injection measured NOTHING until call 19,
SEARCH T2 7 after its deletion, was added.)
ANEXT and RSERCH (3b-ii), MEASURED 2026-11-13, the same way:
  ANEXT ignores Afirst                      the run never halts (Anexta 0:
                                            the scan starts at bit 0)
  ANEXT takes a deleted vle                 2: call 41
  ANEXT ignores the ID                      2: call 37 (ID 18, no vles)
  ANEXT reads the ID at bits 24-29          13: calls 32-41
  ANEXT's no more at the normal return      3: calls 34, 37, 41
  Anexta not past the found vle             9
  ANEXT's $2 not restored when found        4: calls 32, 33, 36, 40
  RSERCH found at the not-found return      3: calls 42, 43, 45
  RSERCH leaves DX                          2: calls 42, 45
The gaps closed after 3b-ii (calls 46-58 on table 5, AL 64 and ADDL 25:
an argument of 64 bits and one of 8, al < AL; vles whose functions are moved
FORWARD from cells above the vle area, one of 100 bits so TBMOV's forward
loop steps twice; halt 12 runs; $0 checked), MEASURED 2026-11-13, the same
way (the counts above were measured before these calls were added):
  TEC not checked (Box 4)                   1: halt 12, TEC 1
  al > AL not checked                       1: halt 12, al 40 > AL 32
  $0 restored from $1's save word           46: every call
  TBMOV forward: source not advanced        1: the vle area (the 100-bit
                                            function's second word)
  TBMOV forward: a short last step moves 64 the run never halts
  TBMOV always backward                     NOTHING, unobservable by design:
                                            no forward move in TABMAN
                                            overlaps its destination, so
                                            either direction copies it.
p.44's third form (step 3c, calls 58-72 on table 5), MEASURED 2026-11-13,
the same way:
  compare length al, not the dictionary     17: calls 59-62 ... (it measured
    part (al mod 64 in the 6-bit field)        NOTHING until call 58, "AB"
                                               then 0, was added)
  Agetv without the rest                    10: calls 59-62 ...
  n not written                             11: calls 59-62 ...
  the rest not moved                        1: the vle area
  a rest makes no vle                       16: calls 59-62 ...
  whole characters not checked              1: halt 12 (al 36)
  the vle length without the rest           5: calls 70-72 (ANEXT), the
                                               vle area
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
from strap2.bits import BitMem                      # noqa: E402
from strap2.cards import deck_cards                 # noqa: E402
from strap2 import tabman as T                      # noqa: E402

DECK = os.path.join(HERE, "..", "decks", "strap2_7030.strap")
BSV = os.path.join(HERE, "..", "bsv")
MODULE = "StretchStrap2x7030TbTb"
STEPS = 20000000
fails = 0


def check(label, got, want):
    global fails
    ok = got == want
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} {label}" + ("" if ok else f":\n  got  {got!r}\n  want {want!r}"))


# the tables: (AL, ADDL, ordered, ID)
TABLES = {1: (32, 6, True, 0o22), 2: (32, 6, False, 0o23),
          3: (32, 25, True, 0o30), 4: (32, 6, True, 0o24),
          5: (64, 25, True, 0o31), 6: (32, 6, True, 0o32)}
# table 5 is the symbol table's shape (Fig. 21: 64, 25; EL 96, so entries at
# half words); its arguments and functions sit above the tables, so TBMOV
# also runs forward.  Table 6 has TEC 1, for the halt-12 run only.
TWORDS = 16             # each table's area, words
VWORDS = 32             # the vle area

# the calls: (routine, table, argument, function, fl); ("DEL", table, n): the
# driver deletes the table's entry n (not a TABMAN routine, p.45 N)
CALLS = [
    ("ADDORD", 1, 50, 150, 6), ("ADDORD", 1, 30, 130, 6), ("ADDORD", 1, 90, 190, 6),
    ("ADDORD", 1, 70, 170, 6), ("ADDORD", 1, 50, 1, 6),
    ("SEARCH", 1, 70), ("SEARCH", 1, 60), ("SEARCH", 1, 99), ("SEARCH", 1, 10),
    ("DEL", 1, 1), ("SEARCH", 1, 50), ("ADDORD", 1, 50, 7, 6), ("SEARCH", 1, 50),
    ("ADDUNO", 2, 9, 9, 6), ("ADDUNO", 2, 3, 3, 6), ("ADDUNO", 2, 7, 7, 6),
    ("SEARCH", 2, 5), ("SEARCH", 2, 3), ("DEL", 2, 2), ("SEARCH", 2, 7),
    ("ADDUNO", 2, 4, 4, 6),
    ("ADDUNO", 2, 8, 8, 6), ("ADDORD", 2, 1, 1, 6), ("SEARCH", 2, 1),
    ("ADDORD", 3, 11, 0b101, 40), ("ADDORD", 3, 12, 3, 40), ("ADDORD", 3, 5, 4, 6),
    ("SEARCH", 3, 12), ("SEARCH", 3, 5),
    ("ADDORD", 4, 5, 5, 6), ("ADDUNO", 4, 2, 2, 6), ("SEARCH", 4, 2),
    ("ANEXT", 0o30), ("ANEXT", 0o30), ("ANEXT", 0o30), ("AFIRST",), ("ANEXT", 0o30),
    ("ANEXT", 0o22), ("VDEL", 1), ("AFIRST",), ("ANEXT", 0o30), ("ANEXT", 0o30),
    ("RSERCH", 3, 12), ("RSERCH", 3, 5), ("RSERCH", 3, None), ("RSERCH", 1, 90),
    ("ADDORD", 5, 0x5000000000000001, 7, 25), ("ADDORD", 5, 0x3000000000000002, 8, 25),
    ("ADDORD", 5, 0x9000000000000003, 9, 40), ("ADDORD", 5, 0x4000000000000000, 10, 25),
    ("ADDORD", 5, 0x3000000000000001, 11, 25), ("SEARCH", 5, 0x9000000000000003),
    ("SEARCH", 5, 0x50000000, 32), ("SEARCH", 5, 0x3000000000000001),
    ("ADDORD", 5, 0x44, 12, 25, 8), ("SEARCH", 5, 0x8000000000000000),
    ("ADDORD", 5, 0x6000000000000000, (1 << 99) | 0x5A5A5A5A5A5A5A5A5, 100),
    ("SEARCH", 5, 0x6000000000000000),
    # p.44's third form (step 3c): ABCDEFGH and two more characters, al 80
    ("ADDORD", 5, 0x4142000000000000, 15, 25),     # "AB": a 16-bit compare would hit it
    ("ADDORD", 5, (0x4142434445464748 << 16) | 0x2A31, 13, 25, 80),
    ("SEARCH", 5, (0x4142434445464748 << 16) | 0x2A31, 80),
    ("SEARCH", 5, (0x4142434445464748 << 8) | 0x5A, 72),
    ("ADDORD", 5, (0x4142434445464748 << 8) | 0x5A, 14, 25, 72),
    ("ADDORD", 5, (0x2122232425262728 << 24) | 0x313233, (1 << 39) | 5, 40, 88),
    ("SEARCH", 5, 0x2122232425262728),
    ("RSERCH", 5, 0x41424344), ("RSERCH", 5, 0x21222324),
    ("AFIRST",), ("ANEXT", 0o31), ("ANEXT", 0o31), ("ANEXT", 0o31), ("ANEXT", 0o31),
    ("ANEXT", 0o31),
]
# a call's al: SEARCH (r, n, arg[, al]); ADDORD, ADDUNO (r, n, arg, f, fl[, al])


def al_of(c):
    k = 3 if c[0] == "SEARCH" else 5
    return c[k] if len(c) > k else TABLES[c[1]][0]
CODES = {"found": 1, "not found": 2, "normal": 3, "already there": 4, "error": 5,
         "no more": 6}
SPECIAL = ("DEL", "AFIRST", "VDEL")      # driver actions, not TABMAN calls


def wb(bits):
    return f"{bits // 64}.{bits % 64}"


def host(addr, calls=None):
    """Replay on the host TABMAN at the deck's addresses: per call its exit,
    the control block's four words, and the final memory."""
    t = T.Tabman(BitMem(), addr["AUVTAB"])
    t.define_universal(addr["VLEA"])
    for n, (al, addl, ordered, ident) in TABLES.items():
        t.define(addr[f"TCB{n}"], addr[f"TBLA{n}"], ident, al, addl, ordered)
    t.put(addr["TCB6"], "TEC", 1)
    initial = {n: [t.mem.get(addr[f"TCB{n}"] + 64 * w, 64) for w in range(4)] for n in TABLES}
    log = []
    dels = {}
    for c in (CALLS if calls is None else calls):
        if c[0] == "AFIRST":
            t.afirst = True
            log.append(None)
            continue
        if c[0] == "VDEL":
            v = vles(t)[c[1]]
            dels[len(log)] = v
            t.mem.put(v, 1, 1)
            log.append(None)
            continue
        if c[0] == "ANEXT":
            ex = t.anext(c[1])
            log.append((ex, [t.anextx << 40, t.anexta << 40, 0, 0]))
            continue
        cb = addr[f"TCB{c[1]}"]
        if c[0] == "RSERCH":
            fa = faddr(t, cb, c[2])
            ex = t.rserch(cb, fa)[0]
            dels[len(log)] = fa
            log.append((ex, [t.mem.get(cb + 64 * w, 64) for w in range(4)]))
            continue
        if c[0] == "DEL":
            e = t.entries(cb)[c[2]]
            dels[len(log)] = e
            t.delete(cb, e)
            log.append(None)
            continue
        al = al_of(c)
        if c[0] == "SEARCH":
            ex = t.search(cb, c[2], al)
        elif c[0] == "ADDORD":
            ex = t.addord(cb, c[2], al, c[3], c[4])
        else:
            ex = t.adduno(cb, c[2], al, c[3], c[4])
        log.append((ex, [t.mem.get(cb + 64 * w, 64) for w in range(4)]))
    return initial, log, dels, t


def vles(t):
    """The vle locations, bottom up."""
    out, p = [], t.auvbot
    while p < t.auvtab:
        out.append(p)
        p += t.mem.get(p + 1, 13)
    return out


def faddr(t, cb, arg):
    """The function address of the entry with this argument; 1 for none."""
    if arg is None:
        return 1
    e = next(e for e in t.entries(cb) if t.argument(cb, e, 32) == arg)
    return t.function_address(cb, e)


def driver(addr, initial, dels, calls=None):
    calls = CALLS if calls is None else calls
    L = ["START   L(BU,24), VLEX", "        ST(BU,24), AUVTAB", "        ST(BU,24), AUVTAB+.32"]
    k = 0
    for i, c in enumerate(calls):
        n = c[1] if len(c) > 1 else 0
        if c[0] == "AFIRST":
            L += ["        LI(BU,1), 1", "        ST(BU,1), AFIRST"]
            continue
        if c[0] == "VDEL":
            L += ["        LI(BU,1), 1", f"        ST(BU,1), VLEA+{wb(dels[i] - addr['VLEA'])}"]
            continue
        if c[0] == "DEL":
            e = dels[i] - addr[f"TBLA{n}"]
            L += ["        LI(BU,1), 1", f"        ST(BU,1), TBLA{n}+{wb(e)}",
                  f"        M-1(BU,16), TCB{n}+3.48"]
            continue
        L += [f"        LVI, ${r}, {100 + r}.0" for r in range(0, 8)]
        if c[0] == "ANEXT":
            L += ["        LVI, $15, $+1.0", "        B, ANEXT",
                  f"        DD(BU,32), (16){c[1] << 8:08X}",
                  f"        B, E{i}M", f"        B, E{i}M", f"        B, E{i}R"]
        elif c[0] == "RSERCH":
            L += [f"        LV, $12, RA{i}", "        LVI, $15, $+1.0", "        B, RSERCH",
                  f"        , TCB{n}", "        , 0($12)", f"        B, E{i}N", f"        B, E{i}F"]
        else:
            L += [f"        LV, $10, ALC{i}", f"        LV, $11, FL{i}",
                  "        LVI, $15, $+1.0", f"        B, {c[0]}",
                  f"        , TCB{n}", f"        , ARG{i}", "        , 0($10)"]
        if c[0] in ("ANEXT", "RSERCH"):
            pass
        elif c[0] != "SEARCH":
            L += [f"        , FN{i}", "        , 0($11)"]
        if c[0] in ("ANEXT", "RSERCH"):
            pass
        elif c[0] == "SEARCH":
            L += [f"        B, E{i}N", f"        B, E{i}F"]
        elif c[0] == "ADDORD":
            L += [f"        B, E{i}A", f"        B, E{i}E", f"        B, E{i}R"]
        else:
            L += [f"        B, E{i}R"]
        for lab, code in (("F", 1), ("N", 2), ("R", 3), ("A", 4), ("E", 5), ("M", 6)):
            L += [f"E{i}{lab}    LI(BU,8), {code}", f"        B, E{i}X"]
        L += [f"E{i}X    ST(BU,8), LOG+{k}.0"]
        src = ["ANEXTX", "ANEXTA", "ZERO", "ZERO"] if c[0] == "ANEXT" else \
            [f"TCB{n}+{w}.0" for w in range(4)]
        L += [x for w in range(4) for x in (f"        L(BU,64), {src[w]}",
                                            f"        ST(BU,64), SNAP+{4 * k + w}.0")]
        L += [f"        SX, ${r}, REG+{8 * k + r}.0" for r in range(0, 8)]
        k += 1
    L += ["DONE    BEW, $", "        CNOP"]
    late = []
    for i, c in enumerate(calls):
        if c[0] in SPECIAL or c[0] == "ANEXT":
            continue
        if c[0] == "RSERCH":
            L += [f"RA{i}    XW, {wb(dels[i])}, 0, 0"]
            continue
        al = al_of(c)
        fl = c[4] if c[0] != "SEARCH" else 0
        d = late if c[1] == 5 else L
        a128 = c[2] << (128 - al)
        d += [f"ARG{i}    DD(BU,64), (16){(c[2] << (64 - al)) if al <= 64 else a128 >> 64:016X}"]
        if al > 64:                 # a third-form argument: its rest in the next word
            d += [f"        DD(BU,64), (16){a128 & ((1 << 64) - 1):016X}"]
        d += [
              f"FN{i}     DD(BU,64), (16){(c[3] << (64 - fl)) if 0 < fl <= 64 else (c[3] << (128 - fl)) >> 64 if fl else 0:016X}"]
        if fl > 64:                 # a two-word function: TBMOV's forward loop steps twice
            d += [f"        DD(BU,64), (16){(c[3] << (128 - fl)) & ((1 << 64) - 1):016X}"]
        L += [f"FL{i}     XW, {wb(fl)}, 0, 0", f"ALC{i}    XW, {wb(al)}, 0, 0"]
    for n, (al, addl, ordered, ident) in TABLES.items():
        L += [f"AL{n}     XW, {wb(al)}, 0, 0"]
        L += [f"TCB{n}    DD(BU,64), (16){initial[n][0]:016X}"] + \
             [f"        DD(BU,64), (16){initial[n][w]:016X}" for w in (1, 2, 3)]
    L += ["ZERO    DD(BU,64), 0", "VLEX    XW, VLEA, 0, 0", f"LOG     DRZ(BU,64), {k}", f"SNAP    DRZ(BU,64), {4 * k}",
          f"REG     DRZ(BU,64), {8 * k}"]
    L += [f"TBLA{n}   DRZ(BU,64), {TWORDS}" for n in TABLES]
    L += [f"VLEA    DRZ(BU,64), {VWORDS}"] + late
    out = []
    for x in L:
        if x[:1] not in (" ", "!"):
            lab, rest = x.split(None, 1)
            x = f"{lab:<8}{rest}"
        out.append(x)
    return "\n".join(out) + "\n"


def text_of(drv):
    src = open(DECK).read()
    assert src.endswith("        END\n")
    return src[:-len("        END\n")] + drv + "        END, START\n"


def assemble(text):
    p2 = strap2.compile_cards(deck_cards(text), strap_asm.DEFAULT_ORIGIN_BITS)
    names = ["AUVTAB", "VLEA", "LOG", "SNAP", "REG", "ERRC"] + \
        [f"TCB{n}" for n in TABLES] + [f"TBLA{n}" for n in TABLES]
    return {n: p2.val.symbol_value(p2.st.search(n))[0] for n in names}


def run_text(text, addr):
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, MODULE + ".strap")
        with open(path, "w") as fh:
            fh.write(text)
        first = addr["LOG"] // 64
        last = addr["VLEA"] // 64 + VWORDS
        args = [os.path.join(HERE, "run_program.sh"), path, MODULE, "ASM=strap2",
                f"DUMP={first},{last - first}", f"STEPS={STEPS}", f"CYCLES<={STEPS}",
                f"FASTLOAD={os.path.join(tmp, MODULE + '.hex')}",
                f"ERRC:{addr['ERRC'] // 64}=0x0"]
        r = subprocess.run(args, capture_output=True, text=True, cwd=HERE)
        for name in os.listdir(BSV):            # by exact name, never a glob
            if name in (MODULE + ".bsv", MODULE + "_sim", MODULE + "_sim.so"):
                os.remove(os.path.join(BSV, name))
    return r


def halt_run(calls):
    """ERRC after a driver of these calls alone (halt 12 expected)."""
    zero = {n: [0, 0, 0, 0] for n in TABLES}
    names = ["AUVTAB", "VLEA"] + [f"TCB{m}" for m in TABLES] + [f"TBLA{m}" for m in TABLES]
    addr = assemble(text_of(driver({n: 0 for n in names}, zero, {}, calls)))
    initial = host(addr, [])[0]
    text = text_of(driver(addr, initial, {}, calls))
    r = run_text(text, addr)
    errc = re.search(r"(PASS|FAIL) ERRC = (\d+)", r.stdout)
    return int(errc.group(2)) >> 40 if errc else None


def main():
    zero = {n: [0, 0, 0, 0] for n in TABLES}
    addr = assemble(text_of(driver({n: 0 for n in
                                    ["AUVTAB", "VLEA"] + [f"TCB{m}" for m in TABLES] +
                                    [f"TBLA{m}" for m in TABLES]}, zero,
                                   {i: 0 for i, c in enumerate(CALLS)
                                    if c[0] in ("DEL", "VDEL", "RSERCH")})
                            ))
    # (the first assembly only finds the addresses; DEL offsets are 0 there)
    initial, log, dels, t = host(addr)
    drv = driver(addr, initial, dels)
    text = text_of(drv)
    check("control: the second assembly keeps the addresses", assemble(text), addr)
    calls = [x for x in log if x is not None]
    check("control: the host takes every kind of exit",
          sorted({x[0] for x in calls}), sorted(CODES))
    r = run_text(text, addr)
    out = r.stdout
    if r.returncode or "step cap" in out or "MEMDUMP" not in out:
        print("FAIL the 7030 TABMAN did not run to its halt:\n" + (out + r.stderr)[-2000:])
        return 1
    mem = {int(a): int(v, 16) for a, v in re.findall(r"MEMDUMP (\d+) ([0-9a-f]+)", out)}
    errc = re.search(r"(PASS|FAIL) ERRC = (\d+)", out)
    check("ERRC is 0 (no failure halt)", int(errc.group(2)) >> 40 if errc else None, 0)
    k = 0
    for i, c in enumerate(CALLS):
        if c[0] in SPECIAL:
            continue
        ex, cbw = log[i]
        lw, sw = addr["LOG"] // 64 + k, addr["SNAP"] // 64 + 4 * k
        got_ex = mem.get(lw, 0) >> 56
        got_cb = [mem.get(sw + w, 0) for w in range(4)]
        regs = [mem.get(addr["REG"] // 64 + 8 * k + r, 0) >> 40 for r in range(0, 8)]
        name = f"call {i} " + " ".join(str(x) for x in c[:3])
        check(f"{name}: the exit ({ex})", got_ex, CODES[ex])
        check(f"{name}: the control block, Fig. 8", [f"{w:016X}" for w in got_cb],
              [f"{w:016X}" for w in cbw])
        check(f"{name}: $0-$7 restored", regs, [(100 + r) * 64 for r in range(0, 8)])
        k += 1
    for n in TABLES:
        a = addr[f"TBLA{n}"] // 64
        check(f"table {n}'s entries, bit for bit", [f"{mem.get(a + w, 0):016X}" for w in range(TWORDS)],
              [f"{t.mem.get((a + w) * 64, 64):016X}" for w in range(TWORDS)])
    a = addr["VLEA"] // 64
    check("the vle area ends inside the words compared", t.auvtab <= (a + VWORDS) * 64, True)
    check("the vle area, bit for bit", [f"{mem.get(a + w, 0):016X}" for w in range(VWORDS)],
          [f"{t.mem.get((a + w) * 64, 64):016X}" for w in range(VWORDS)])
    check("halt 12: TEC 1, a compare the guide does not describe",
          halt_run([("SEARCH", 6, 1)]), 12)
    check("halt 12: a rest that is not whole characters (al 36, AL 32; Fig. 22's 8n)",
          halt_run([("SEARCH", 1, 1, 36)]), 12)
    m = re.search(r"cycles = (\d+)", out)
    print(f"INFO model steps: {m.group(1) if m else '?'}")
    print("ALL CHECKS PASSED" if not fails else f"{fails} FAILED")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
