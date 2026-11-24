#!/usr/bin/env python3
"""Test Nakashima 1991 Fig. 3-25 (PSI-III microword) against the held stores.

Usage: python3 -I test_layout.py ARCHIVE
"""
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stores  # noqa: E402

# Thesis Fig. 3-25, widths left to right, positions assume left = bit 63.
THESIS_W = [('DBGF', 1), ('CCF', 5), ('WRBF', 1), ('DSTF', 5), ('SC1F', 5), ('SC2F', 5),
            ('SD1F', 3), ('SD2F', 2), ('ADF', 3), ('AS1F', 3), ('AS2F', 2), ('ALF', 2),
            ('JMPF', 4), ('CNDF', 4), ('MCF', 1), ('TGIF', 2), ('EM1', 6), ('EM2', 6), ('EM3', 4)]
# TR-733 fig. 4 as transcribed in docs/literature_gaps.md App. C 2.3 (geometry-measured).
TR733_W = [('b63', 1), ('CCF', 5), ('b57', 1), ('DSTF', 5), ('SC1F', 5), ('SC2F', 5),
           ('SD1F', 3), ('SD2F', 2), ('AS1F', 3), ('AS2F', 2), ('ADF', 3), ('ALF', 3),
           ('JMPF', 3), ('CNDF', 4), ('b18', 1), ('b17_16', 2), ('EM1', 6), ('EM2', 6), ('EM3', 4)]


def layout(ws):
    out, hi = {}, 64
    for n, w in ws:
        out[n] = (hi - 1, hi - w)
        hi -= w
    assert hi == 0
    return out


THESIS, TR733 = layout(THESIS_W), layout(TR733_W)


def f(x, rng):
    h, l = rng
    return x >> l & ((1 << (h - l + 1)) - 1)


def hist(words, rng):
    return Counter(f(x, rng) for x in words)


def fmt(c, n):
    return ' '.join('%x:%d' % (k, v) for k, v in sorted(c.items()))


def report(name, words, lay):
    nz = [x for x in words if x]
    print('== %s: %d words, %d non-zero' % (name, len(words), len(nz)))
    for fld, rng in lay.items():
        c = hist(nz, rng)
        print('  %-5s %2d-%2d  distinct %3d  zero %5.1f%%  %s' % (
            fld, rng[0], rng[1], len(c), 100.0 * c.get(0, 0) / max(1, len(nz)),
            fmt(c, len(nz)) if len(c) <= 16 else ''))


def per_bit(words):
    nz = [x for x in words if x]
    return [sum(x >> b & 1 for x in nz) / len(nz) for b in range(64)]


def landing(words, base, targets):
    n = len(words)
    hit = sum(1 for t in targets if base <= t < base + n and words[t - base])
    inr = sum(1 for t in targets if base <= t < base + n)
    return hit, inr, len(targets)


def main(tar):
    ms = stores.members(tar)
    psi = stores.raw64(ms['syspsi'])
    img1, img2 = stores.mekbn_images(ms['pimm.MEkbn'])
    init = stores.raw64(ms['sysinit'])
    idat = stores.raw64(ms['sysidat'])
    print('syspsi', len(psi), 'sysinit', len(init), 'sysidat', len(idat))
    print('img1==syspsi[0:5800] nonzero-equal', sum(1 for a, x in enumerate(img1) if x and x == psi[a]),
          'of', sum(1 for x in img1 if x))
    # is sysinit an overlay of syspsi at 0x5000?
    eq = sum(1 for a, x in enumerate(init) if x and 0x5000 + a < len(psi) and psi[0x5000 + a] == x)
    print('sysinit nonzero', sum(1 for x in init if x), 'equal to syspsi[0x5000+a]', eq,
          'syspsi[0x5000:0x705e] nonzero', sum(1 for x in psi[0x5000:0x5000 + len(init)] if x))

    for name, w in (('syspsi', psi), ('img2 (KL1)', img2), ('sysinit', init), ('sysidat', idat)):
        report(name + ' THESIS', w, THESIS)
    print()
    print('per-bit set fraction (syspsi non-zero words), bit 63..0:')
    pb = per_bit(psi)
    for b in range(63, -1, -1):
        print('  b%02d %.3f' % (b, pb[b]), end='\n' if b % 8 == 0 else '')
    pb2 = per_bit(init)
    print('per-bit set fraction (sysinit), bit 63..0:')
    for b in range(63, -1, -1):
        print('  b%02d %.3f' % (b, pb2[b]), end='\n' if b % 8 == 0 else '')


if __name__ == '__main__':
    main(sys.argv[1])
