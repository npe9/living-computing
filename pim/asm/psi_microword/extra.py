#!/usr/bin/env python3
"""Extra checks. Usage: python3 -I extra.py ARCHIVE"""
import os, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stores
ms = stores.members(sys.argv[1])
psi = stores.raw64(ms['syspsi']); _, img2 = stores.mekbn_images(ms['pimm.MEkbn'])
init = stores.raw64(ms['sysinit']); idat = stores.raw64(ms['sysidat'])
ps = set(x for x in psi if x)
nz2 = [x for x in img2 if x]
print('img2 nonzero words also present in syspsi:', sum(1 for x in nz2 if x in ps), 'of', len(nz2))
print('img2[a]==syspsi[a]:', sum(1 for a, x in enumerate(img2) if x and x == psi[a]))
seg = init[0x1800:0x1800 + len(idat)]
print('sysinit[0x1800:+1040] == sysidat word-for-word:', sum(1 for a, b in zip(seg, idat) if a == b), 'of', len(idat),
      ' nonzero equal', sum(1 for a, b in zip(seg, idat) if a and a == b))
nzi = [(i, x) for i, x in enumerate(idat) if x]
for sel in range(4):
    grp = [(i, x) for i, x in nzi if (x >> 35 & 3) == sel]
    a15 = sum(1 for i, x in grp if psi[x & 0x7fff])
    pg = sum(1 for i, x in grp if psi[((i >> 7) << 11 | x & 0x3ff) & 0x7fff])
    print('idat bits36-35=%d n=%3d  low15 lands %3d  page(i>>7)|low10 lands %3d' % (sel, len(grp), a15, pg))
# ALF(28-27) vs EM2 code set
for name, w in (('syspsi', psi), ('img2', img2)):
    nz = [x for x in w if x]
    for alf in range(4):
        g = [x for x in nz if (x >> 27 & 3) == alf]
        em2 = Counter(x >> 4 & 63 for x in g)
        print('%s ALF=%d n=%5d distinct EM2 %2d top %s' % (name, alf, len(g), len(em2), em2.most_common(6)))
