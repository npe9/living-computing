#!/usr/bin/env python3
"""Discriminate thesis Fig. 3-25 vs TR-733 fig. 4 in bits 36..23.
Usage: python3 -I disc.py ARCHIVE"""
import os, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stores
from test_layout import THESIS, TR733, f, hist, fmt

ms = stores.members(sys.argv[1])
psi = stores.raw64(ms['syspsi'])
img1, img2 = stores.mekbn_images(ms['pimm.MEkbn'])
for name, w in (('syspsi', psi), ('img2', img2)):
    nz = [x for x in w if x]
    print('==', name)
    for lab, lay in (('TR733', TR733),):
        for fld in ('AS1F', 'AS2F', 'ADF', 'ALF', 'JMPF'):
            print('  %s %-4s %d-%d %s' % (lab, fld, lay[fld][0], lay[fld][1], fmt(hist(nz, lay[fld]), 0)))
    # bit 26 vs bits 25..23
    ct = Counter((x >> 26 & 1, x >> 23 & 7) for x in nz)
    print('  bit26 x bits25-23:')
    for b in (0, 1):
        print('    b26=%d ' % b + ' '.join('%d:%d' % (j, ct[(b, j)]) for j in range(8)))
    # bit 26 vs CNDF nonzero, for each j
    ct2 = Counter((x >> 26 & 1, x >> 23 & 7, (x >> 19 & 15) != 0) for x in nz)
    print('  P(CNDF!=0 | b26, j):')
    for b in (0, 1):
        print('    b26=%d ' % b + ' '.join('%d:%d/%d' % (j, ct2[(b, j, True)], ct2[(b, j, True)] + ct2[(b, j, False)]) for j in range(8)))
    # bits 28..27 vs bit 26 joint (is bit 26 part of ALF?)
    ct3 = Counter((x >> 27 & 3, x >> 26 & 1) for x in nz)
    print('  bits28-27 x bit26:', ' '.join('%d%d:%d' % (a, b, ct3[(a, b)]) for a in range(4) for b in (0, 1)))
    # bit 26 when no ALU activity: AS1(33-31)==0 and AS2(30-29)==0 and ALF(28-27)==0
    q = [x for x in nz if (x >> 29 & 31) == 0 and (x >> 27 & 3) == 0]
    print('  words with bits33-27 all zero: %d, bit26 set in %d' % (len(q), sum(x >> 26 & 1 for x in q)))
    q2 = [x for x in nz if (x >> 23 & 7) == 5]
    print('  JMP(25-23)=5 words %d, bit26 set %d' % (len(q2), sum(x >> 26 & 1 for x in q2)))
