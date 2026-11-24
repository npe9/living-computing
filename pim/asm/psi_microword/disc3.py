#!/usr/bin/env python3
"""AS1F(33-31) in SD1F/ADF numbering? Usage: python3 -I disc3.py ARCHIVE"""
import os, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stores
NAMES1 = ['0', 'xr', 'yr', '3?', 'mdr1', 'mdr2', 'mar1', 'mar2']
NAMES2 = ['0', 'yr', 'mdr1', 'mdr2']
ms = stores.members(sys.argv[1])
psi = stores.raw64(ms['syspsi'])
_, img2 = stores.mekbn_images(ms['pimm.MEkbn'])
for name, w in (('syspsi', psi), ('img2', img2)):
    nz = [x for x in w if x]
    print('==', name)
    nxt = [w[a + 1] for a, x in enumerate(w[:-1]) if x and x >> 61 & 1 and (x >> 23 & 7) == 0 and w[a + 1]]
    nxt2 = [w[a + 1] for a, x in enumerate(w[:-1]) if x and x >> 61 & 1 and x >> 59 & 1 and (x >> 23 & 7) == 0 and w[a + 1]]
    nxt1 = [w[a + 1] for a, x in enumerate(w[:-1]) if x and x >> 61 & 1 and not x >> 59 & 1 and (x >> 23 & 7) == 0 and w[a + 1]]
    for lab, s in (('all', nz), ('after read', nxt), ('after read, b59=0', nxt1), ('after read, b59=1', nxt2)):
        c = Counter(y >> 31 & 7 for y in s)
        print('  AS1F %-18s n=%5d ' % (lab, len(s)) + ' '.join('%s:%.2f' % (NAMES1[k], c[k] / len(s)) for k in range(8)))
    j = Counter((x >> 31 & 7, x >> 29 & 3) for x in nz)
    print('  top (AS1F,AS2F) pairs:', ', '.join('%s+%s:%d' % (NAMES1[a], NAMES2[b], n) for (a, b), n in j.most_common(12)))
