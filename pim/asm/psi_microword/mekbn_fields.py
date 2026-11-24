#!/usr/bin/env python3
"""Field statistics of syspsi and the KL1 image AS asm/mekbn.py DECODES THEM.

Unlike the other scripts here (which carry their own layout tables), this
one imports mekbn and uses its FIELDS, field() and flow(), so running it
before and after a change to mekbn.py's layout measures that change.
Used for psi_microword.md section 7 (2026-11-23).

Usage: python3 -I asm/psi_microword/mekbn_fields.py   (from pim/)
"""
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import mekbn  # noqa: E402


def name_of(*cands):
    names = [n for n, _, _ in mekbn.FIELDS]
    for c in cands:
        if c in names:
            return c
    return None


def main():
    fw = mekbn.Firmware()
    psi = mekbn.syspsi()
    print('FIELDS:', ' '.join('%s %d-%d' % f for f in mekbn.FIELDS))
    covered = set()
    for _, hi, lo in mekbn.FIELDS:
        covered |= set(range(lo, hi + 1))
    print('bits not in any field:', sorted(set(range(64)) - covered, reverse=True))
    jn, aln = name_of('JMPF', 'JMP'), name_of('ALF', 'AL')
    for name, im in (('syspsi', psi), ('img2', fw.img2)):
        nz = [(a, x) for a, x in enumerate(im) if x]
        n = len(im)
        print('== %s: %d non-zero words' % (name, len(nz)))
        print('  bit 63 zero: %d of %d' % (sum(1 for _, x in nz if not x >> 63), len(nz)))
        for f, hi, lo in mekbn.FIELDS:
            c = Counter(mekbn.field(x, f) for _, x in nz)
            print('  %-5s %2d-%2d distinct %5d zero %5.1f%% %s' % (
                f, hi, lo, len(c), 100.0 * c.get(0, 0) / len(nz),
                ' '.join('%x:%d' % kv for kv in sorted(c.items())) if len(c) <= 16 else ''))
        # jumps per code of the jump field, under mekbn.flow()
        print('  per %s code: n, flow kinds, targets, in range, landing on non-zero' % jn)
        tot = [0, 0, 0]
        for k in range(1 << (mekbn.FIELDS[[f for f, _, _ in mekbn.FIELDS].index(jn)][1]
                             - mekbn.FIELDS[[f for f, _, _ in mekbn.FIELDS].index(jn)][2] + 1)):
            ws = [(a, x) for a, x in nz if mekbn.field(x, jn) == k]
            if not ws:
                continue
            fl = [mekbn.flow(a, x) for a, x in ws]
            tg = [t for _, t, _ in fl if t is not None]
            inr = [t for t in tg if 0 <= t < n]
            land = sum(1 for t in inr if im[t])
            tot = [tot[0] + len(tg), tot[1] + len(inr), tot[2] + land]
            print('    %x n=%5d %-40s targets %5d in range %5d land %5d' % (
                k, len(ws), dict(Counter(kd for kd, _, _ in fl)), len(tg), len(inr), land))
        print('  all targets %d, in range %d, landing %d' % tuple(tot))
        # ALU operation
        if hasattr(mekbn, 'alu_op'):
            c = Counter(mekbn.alu_op(x) for _, x in nz)
            print('  alu_op():', ', '.join('%s:%d' % kv for kv in c.most_common()))
        c = Counter(mekbn.field(x, aln) for _, x in nz)
        print('  %s values: %s' % (aln, ' '.join('%x:%d' % kv for kv in sorted(c.items()))))
        for v in sorted(c):
            em2 = Counter(x >> 4 & 63 for _, x in nz if mekbn.field(x, aln) == v)
            print('    %s=%x: EM2 (bits 9-4) distinct %2d, top %s' % (
                aln, v, len(em2), em2.most_common(5)))


if __name__ == '__main__':
    main()
