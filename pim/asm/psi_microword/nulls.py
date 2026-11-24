#!/usr/bin/env python3
"""Null controls for syspsi: other byte orders / offsets.
Score: bit63 rate; JMPF(26-23)=5 absolute-target landing; MI(bit26; bits25-23).
Usage: python3 -I nulls.py ARCHIVE"""
import os, sys, math
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stores
def mi(pairs):
    n = len(pairs); a = Counter(p[0] for p in pairs); b = Counter(p[1] for p in pairs); ab = Counter(pairs)
    return sum(c / n * math.log2(c * n / (a[x] * b[y])) for (x, y), c in ab.items())
raw = stores.members(sys.argv[1])['syspsi']
def score(lab, w):
    nz = [x for x in w if x]
    j5 = [x for x in nz if (x >> 23 & 15) == 5]
    land = sum(1 for x in j5 if (x & 0xffff) < len(w) and w[x & 0xffff])
    print('%-28s bit63 %5.2f%%  JMPF5 n=%5d lands %5.1f%% (baseline %.1f%%)  MI(b26;b25-23) %.3f' % (
        lab, 100.0 * sum(x >> 63 for x in nz) / len(nz), len(j5), 100.0 * land / max(1, len(j5)),
        100.0 * len(nz) / len(w), mi([(x >> 26 & 1, x >> 23 & 7) for x in nz])))
score('LE, header 256 (as held)', stores.raw64(raw))
score('BE, header 256', stores.raw64(raw, order='big'))
le = stores.raw64(raw)
score('LE, 32-bit halves swapped', [(x >> 32) | (x & 0xffffffff) << 32 for x in le])
for off in (257, 260, 264 - 4):
    score('LE, offset %d' % off, stores.raw64(raw, off=off))
