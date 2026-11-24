#!/usr/bin/env python3
"""sysidat vs Fig. 3-22 nanocode (50 bits). Usage: python3 -I idat.py ARCHIVE"""
import os, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stores
ms = stores.members(sys.argv[1])
raw = ms['sysidat']
print('header', raw[:16].hex())
w = stores.raw64(raw)
psi = stores.raw64(ms['syspsi'])
nz = [(i, x) for i, x in enumerate(w) if x]
print('entries', len(w), 'nonzero', len(nz))
print('per-bit set counts 63..0:')
print(' '.join('%d:%d' % (b, sum(x >> b & 1 for _, x in nz)) for b in range(63, -1, -1)))
print('max value bit length', max(x.bit_length() for _, x in nz))
for i, x in nz[:12]:
    print('%03x %016x' % (i, x))
# low 16 bits: absolute 15-bit address? MAF 10 bits + page?
c15 = sum(1 for _, x in nz if psi[x & 0x7fff])
print('low15 as syspsi address lands non-zero:', c15, 'of', len(nz))
for sh in (7, 8):
    c = sum(1 for i, x in nz if psi[((i >> sh) << 11 | x & 0x3ff) & 0x7fff])
    print('page=(index>>%d)<<11 | low10 lands:' % sh, c)
