"""check_strap2_bopser.py -- the host BOPSER (strap/strap2/bopser.py) against
C22-6729 pp.65-67 (Charts BA, BB, Figure 11), read in the ink 2026-11-15.

Run from stretch/tests with PYTHONDONTWRITEBYTECODE=1.

MEASURED INJECTIONS into bopser.py, 2026-11-15, restored by copy and cmp,
control all passing; the number of failing checks, then the first:
  N = ceiling(log2 entries), p.67 as printed  3: every entry found, Knuth's
                                               DELTA, the 256-entry table
  the first odd count halved without +1     5: every entry, the halves for
                                               193, Box 7, DELTA, 256
  a later odd count not increased           3: every entry, the halves, DELTA
  Box 7 from the table, not table - length  2: every entry, Box 7
  the pairs remade on every search          1: the stored pairs
  Llxw the entry, not its function          1: every entry
  the same pair used again (Box 15)         3: every entry, a miss found (a
                                               word outside the table), 256
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
from strap2 import bopser as B         # noqa: E402
from strap2.bits import BitMem         # noqa: E402

fails = 0


def check(name, got, want):
    global fails
    if got == want:
        print(f"PASS {name}")
    else:
        fails += 1
        print(f"FAIL {name}: got {got!r}, want {want!r}")


CB, TW = 64 * 10, 64 * 2
TABLE = None


def table(n, el=128):
    """Keys 2, 4, ..., 2n; each entry's second word 1000 + its index.  The
    word after the table holds all ones, which no test word equals; the word
    before it is the control block's last pair word (bopser.py)."""
    global TABLE
    mem = BitMem()
    TABLE = B.define(mem, CB, TW, el, n)
    mem.put(TABLE + n * el, 64, (1 << 64) - 1)
    for i in range(n):
        mem.put(TABLE + i * el, 64, 2 * (i + 1))
        mem.put(TABLE + i * el + 64, 64, 1000 + i)
    return mem


def find(mem, key, n=None):
    mem.put(TW, 64, key)
    return B.bopser(mem, CB)


# Every key of every table of 1 to 300 entries, and every miss between them.
bad_hit, bad_miss = [], []
for n in range(1, 301):
    mem = table(n)
    for i in range(n):
        r = find(mem, 2 * (i + 1))
        if not r.found or mem.get(r.llxw, 64) != 1000 + i:
            bad_hit.append((n, i))
    for k in range(1, 2 * n + 2, 2):
        if find(mem, k).found:
            bad_miss.append((n, k))
check("every entry of tables of 1-300 entries is found, Llxw its function",
      bad_hit[:5], [])
check("no argument the table lacks is found", bad_miss[:5], [])

# The pairs, for SYSTAB's size: 193 entries of 128 bits.
mem = table(193)
r = find(mem, 2 * 97)
n = 18 - B.lzc18(193)
inc = [B._get_index(mem, CB + 64 + 32 * k) for k in range(n)]
dec = [B._get_index(mem, CB + 64 + 32 * (n + k)) for k in range(n)]
check("N = 18 - LZC = 8 for 193 entries (CHOSEN; p.67's ceiling(log2) is 8 too)", n, 8)
check("LLNEW's halves for 193: 97 48 24 12 6 3 2 1, times the entry length",
      inc, [h * 128 for h in (97, 48, 24, 12, 6, 3, 2, 1)])
check("  and the decrements are their negatives", dec, [-x for x in inc])
check("Box 7: the first entry tested is (table - length) + the first increment",
      r.probes[0], TABLE - 128 + 97 * 128)
check("the table is the word after the pair space (CHOSEN)", TABLE, CB + 64 * 9)
check("BOPSER's indicator is on after the first search (Boxes 4-5)",
      mem.get(CB + 26, 1), 1)
B._put_index(mem, CB + 64 + 32 * (n + 1), 0)    # spoil the second decrement (the first is never used)
check("a second search uses the stored pairs, not new ones (Box 4)",
      find(mem, 2).found, False)
check("the halves are Knuth's DELTA (Algorithm C), n = 1..4999",
      all(B.pairs(m) == [(m + 2 ** (j - 1)) // 2 ** j
                         for j in range(1, m.bit_length() + 1)] for m in range(1, 5000)),
      True)
check("a power-of-two table, 256 entries: every entry found (p.67's N misses one)",
      all(find(table(256), 2 * (i + 1)).found for i in range(256)), True)
check("a null table: not found (Box 2)", find(table(0), 2).found, False)
try:
    B.define(BitMem(), CB, TW, 32, 4)
    got = "accepted"
except B.BopserError:
    got = "refused"
check("an entry under 64 bits is refused (p.67 restriction 4)", got, "refused")

print("ALL CHECKS PASSED" if not fails else f"{fails} FAILED")
sys.exit(1 if fails else 0)
