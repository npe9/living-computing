#!/usr/bin/env python3
"""Per 4-bit JMPF (thesis bits 26-23): do EM-encoded targets land on non-zero words?
Usage: python3 -I targets.py ARCHIVE"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stores
ms = stores.members(sys.argv[1])
psi = stores.raw64(ms['syspsi'])
_, img2 = stores.mekbn_images(ms['pimm.MEkbn'])
init = stores.raw64(ms['sysinit'])
def run(name, w, base=0, ws=None):
    ws = ws if ws is not None else range(len(w))
    nzc = sum(1 for x in w if x)
    print('== %s  occupancy baseline %.1f%%' % (name, 100.0 * nzc / len(w)))
    for j in range(16):
        abs_hit = abs_in = rel_hit = n = 0
        for a in ws:
            x = w[a]
            if not x or (x >> 23 & 15) != j:
                continue
            n += 1
            t = x & 0xffff
            if base <= t < base + len(w):
                abs_in += 1
                abs_hit += bool(w[t - base])
            pa = ((a + base) & ~0x3ff) | (x & 0x3ff)
            if base <= pa < base + len(w):
                rel_hit += bool(w[pa - base])
        if n:
            print('  JMPF %x n=%5d  EM15..0 absolute: in-range %5.1f%% lands %5.1f%%   page-relative EM9..0 lands %5.1f%%' % (
                j, n, 100.0 * abs_in / n, 100.0 * abs_hit / max(1, abs_in), 100.0 * rel_hit / n))
run('syspsi', psi)
run('img2', img2)
run('sysinit 5000-51ff (base 0x5000, targets within sysinit)', init, 0x5000, range(0, 0x200))
