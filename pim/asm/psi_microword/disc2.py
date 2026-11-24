#!/usr/bin/env python3
"""Bits 33..29: thesis AS1F(33-31)/AS2F(30-29) vs TR-733 AS2(33-32)/AD(31-29).
Usage: python3 -I disc2.py ARCHIVE"""
import os, sys, math
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stores

def mi(pairs):
    n = len(pairs); a = Counter(p[0] for p in pairs); b = Counter(p[1] for p in pairs); ab = Counter(pairs)
    return sum(c / n * math.log2(c * n / (a[x] * b[y])) for (x, y), c in ab.items())

ms = stores.members(sys.argv[1])
psi = stores.raw64(ms['syspsi'])
_, img2 = stores.mekbn_images(ms['pimm.MEkbn'])
for name, w in (('syspsi', psi), ('img2', img2)):
    nz = [x for x in w if x]
    print('==', name)
    for b, lo, hi in ((31, (33, 32), (30, 29)), (26, (28, 27), (25, 23)), (34, (36, 35), (33, 32))):
        L = [(x >> b & 1, x >> lo[1] & ((1 << (lo[0]-lo[1]+1)) - 1)) for x in nz]
        H = [(x >> b & 1, x >> hi[1] & ((1 << (hi[0]-hi[1]+1)) - 1)) for x in nz]
        print('  MI(bit%d; bits%d-%d)=%.4f  MI(bit%d; bits%d-%d)=%.4f' % (b, lo[0], lo[1], mi(L), b, hi[0], hi[1], mi(H)))
    # after a read strobe (bit 61) word, next word's 33-32 and 30-29
    nxt = [w[a + 1] for a, x in enumerate(w[:-1]) if x and x >> 61 & 1 and (x >> 23 & 7) == 0 and w[a + 1]]
    base = nz
    for lab, s in (('33-32', 32), ('30-29', 29)):
        c1 = Counter(y >> s & 3 for y in nxt); c0 = Counter(y >> s & 3 for y in base)
        print('  next-after-read bits %s: %s   (all words: %s)' % (lab,
              ' '.join('%d:%.2f' % (k, c1[k] / len(nxt)) for k in range(4)),
              ' '.join('%d:%.2f' % (k, c0[k] / len(base)) for k in range(4))))
