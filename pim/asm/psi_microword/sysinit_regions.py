#!/usr/bin/env python3
"""sysinit: per-512-word region, text-like words, DBGF, and the JMPF bit26 coupling.
Usage: python3 -I sysinit_regions.py ARCHIVE"""
import os, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stores
ms = stores.members(sys.argv[1])
body = ms['sysinit'][256:]
init = stores.raw64(ms['sysinit'])
def texty(i):
    w = body[8 * i:8 * i + 8]
    return all(32 <= c < 127 or c == 0 for c in w) and sum(32 <= c < 127 for c in w) >= 4
R = 512
tot = Counter()
for s in range(0, len(init), R):
    ws = list(range(s, min(s + R, len(init))))
    nz = [i for i in ws if init[i]]
    tx = [i for i in nz if texty(i)]
    code = [init[i] for i in nz if not texty(i)]
    j2 = [x for x in code if (x >> 23 & 7) == 2]
    print('%05x-%05x nz %3d text %3d  code: DBGF %3d  j=2 %3d with b26 %3d  j=5 %3d with b26 %3d' % (
        0x5000 + s, 0x5000 + ws[-1], len(nz), len(tx), sum(x >> 63 for x in code), len(j2),
        sum(x >> 26 & 1 for x in j2), sum(1 for x in code if (x >> 23 & 7) == 5),
        sum(1 for x in code if (x >> 23 & 7) == 5 and x >> 26 & 1)))
