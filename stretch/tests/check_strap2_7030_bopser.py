#!/usr/bin/env python3
"""check_strap2_7030_bopser.py -- the 7030 STRAP II's BOPSER
(decks/strap2_7030.strap, step 4a), assembled by the host STRAP II and run on
the Bluespec model, against the host's specification strap/strap2/bopser.py
(C22-6729 pp.65-67, Charts BA and BB, Figure 11).

The driver (generated below, NOT part of the reconstruction) calls BOPSER by
p.67's linkage on SYSCB for every one of SYSTAB's 193 names and for names it
lacks: below the first, above the last, and each name with its last
character code one higher.  For each it records LLXW's value field on the
found exit, all ones on the not-found exit.  The host runs bopser.py over the
same assembled image for the same keys.  Then SYSCB's pairs are compared.

Run from stretch/tests with PYTHONDONTWRITEBYTECODE=1.

MEASURED INJECTIONS into the deck, 2026-11-15, restored by copy and cmp,
control all passing:
  LLNEW: the first odd count not increased  2: the 193 names, SYSCB's pairs
  Box 7 from the table, not table - length  1: the 193 names (this one
                                               measured NOTHING in
                                               check_strap2_7030_getfld.py,
                                               which looks up only a few)
  a decrement's sign not set                1: SYSCB's pairs (the search
                                               subtracts the magnitude)
  Box 15: the lists not stepped             1: the 193 names
  BOPSER's indicator never set              1: SYSCB's pairs
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
from strap2 import bopser                           # noqa: E402
from strap2.bits import BitMem                      # noqa: E402
from strap2.cards import deck_cards                 # noqa: E402
from check_strap2_7030 import BSV                   # noqa: E402

DECK = os.path.join(HERE, "..", "decks", "strap2_7030.strap")
MODULE = "StretchStrap2x7030BopTb"
STEPS = 20000000
MISS = (1 << 24) - 1
fails = 0


def check(label, got, want):
    global fails
    if got == want:
        print(f"PASS {label}")
    else:
        fails += 1
        print(f"FAIL {label}: got {got!r}, want {want!r}")


def assemble(text):
    return strap2.compile_cards(deck_cards(text), strap_asm.DEFAULT_ORIGIN_BITS)


def driver(keys):
    L = ["START   NOP"]
    for i in range(len(keys)):
        L += [f"        L(BU,64), KEY+{i}.0", "        ST(BU,64), GFKEY",
              "        SIC, $15", "        B, BOPSER", "        , SYSCB",
              f"        B, NF{i}", "        L(BU,24), LLXW", f"        B, ST{i}",
              f"NF{i}    L(BU,24), BDMISS",
              f"ST{i}    ST(BU,24), RES+{i}.0"]
    L += ["DONE    BEW, $", "        CNOP",
          f"BDMISS  DD(BU,64), (16){MISS << 40:016X}",
          "KEY     SYN, $"]
    L += [f"        DD(BU,64), (16){k:016X}" for k in keys]
    L += [f"RES     DRZ(BU,64), {len(keys)}"]
    return "\n".join(L) + "\n"


def deck_text(keys):
    src = open(DECK).read()
    assert src.endswith("        END\n")
    return src[:-len("        END\n")] + driver(keys) + "        END, START\n"


def main():
    # the names, from the assembled deck itself
    base = assemble(deck_text([0]))
    word = lambda n: base.val.symbol_value(base.st.search(n))[0] // 64
    systab, cb = word("SYSTAB"), word("SYSCB")
    names = [base.image.words.get(systab + 2 * i, 0) for i in range(193)]
    check("control: SYSTAB holds 193 names in ascending order",
          (len(set(names)), names == sorted(names)), (193, True))
    misses = [names[0] - 1, names[-1] + 1] + [n + 1 for n in names[::7] if n + 1 not in names]
    keys = names + misses
    p2 = assemble(deck_text(keys))
    word = lambda n: p2.val.symbol_value(p2.st.search(n))[0] // 64
    # the host specification over the same image
    mem = BitMem()
    for w, v in p2.image.words.items():
        mem.put(64 * w, 64, v)
    cbit, gfkey = 64 * word("SYSCB"), 64 * word("GFKEY")
    want = []
    for k in keys:
        mem.put(gfkey, 64, k)
        r = bopser.bopser(mem, cbit)
        want.append(r.llxw if r.found else MISS)
    check("control: the host finds every name at its own entry's function",
          want[:193], [64 * word("SYSTAB") + 128 * i + 64 for i in range(193)])
    check("control: the host finds none of the misses", set(want[193:]), {MISS})
    cbw = [mem.get(cbit + 64 * k, 64) for k in range(9)]
    res = word("RES")
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, MODULE + ".strap")
        with open(path, "w") as fh:
            fh.write(deck_text(keys))
        args = [os.path.join(HERE, "run_program.sh"), path, MODULE, "ASM=strap2",
                f"STEPS={STEPS}", f"CYCLES<={STEPS}",
                f"FASTLOAD={os.path.join(tmp, MODULE + '.hex')}",
                f"ERRC:{word('ERRC')}=0x0"]
        args += [f"R{i}:{res + i}=0x{v << 40:x}" for i, v in enumerate(want)]
        args += [f"SYSCB{k}:{word('SYSCB') + k}=0x{v:x}" for k, v in enumerate(cbw)]
        r = subprocess.run(args, capture_output=True, text=True, cwd=HERE)
    for name in os.listdir(BSV):            # by exact name, never a glob
        if name in (MODULE + ".bsv", MODULE + "_sim", MODULE + "_sim.so"):
            os.remove(os.path.join(BSV, name))
    out = r.stdout
    if r.returncode or "step cap" in out:
        check("the run", (out + r.stderr)[-800:], "ok")
        return
    res_fail = re.findall(r"^FAIL (R\d+)", out, re.M)
    cb_fail = re.findall(r"^FAIL (SYSCB\d)", out, re.M)
    check("ERRC is 0", bool(re.search(r"^PASS ERRC", out, re.M)), True)
    check(f"every one of the 193 names: the 7030 LLXW equals bopser.py's",
          [f for f in res_fail if int(f[1:]) < 193], [])
    check(f"every one of the {len(misses)} misses: not found, as bopser.py",
          [f for f in res_fail if int(f[1:]) >= 193], [])
    check("SYSCB's word and its 8 pair words equal bopser.py's", cb_fail, [])
    m = re.search(r"cycles = (\d+)", out)
    print(f"INFO model steps: {m.group(1) if m else '?'}")


if __name__ == "__main__":
    main()
    print("ALL CHECKS PASSED" if not fails else f"{fails} FAILED")
    sys.exit(1 if fails else 0)
