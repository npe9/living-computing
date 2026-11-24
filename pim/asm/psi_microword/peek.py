#!/usr/bin/env python3
"""Peek at sysinit bytes. Usage: python3 -I peek.py ARCHIVE"""
import os, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stores
ms = stores.members(sys.argv[1])
r = ms['sysinit']
print(r[:32].hex())
body = r[256:]
for off in (0, 8 * 0x100, 8 * 0x1000, 8 * 0x2000):
    for i in range(off, off + 64, 8):
        w = body[i:i + 8]
        print('%05x' % (0x5000 + i // 8), w.hex(), ''.join(chr(c) if 32 <= c < 127 else '.' for c in w))
# byte-position stats
for p in range(8):
    c = Counter(body[i + p] for i in range(0, len(body), 8))
    hi = sum(v for k, v in c.items() if k & 0x80)
    print('byte', p, 'distinct', len(c), 'bit7 set', hi, 'top', c.most_common(5))
# Words equal to syspsi words anywhere?
psi = set(stores.raw64(ms['syspsi']))
init = stores.raw64(ms['sysinit'])
print('sysinit nonzero words found anywhere in syspsi:', sum(1 for x in init if x and x in psi), 'of', sum(1 for x in init if x))
# try sysinit as 40-bit/.kbn-container words
