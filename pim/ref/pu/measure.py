#!/usr/bin/env python3
"""The measurements behind ref/pu's INFERRED rules, pinned.

Counts only (no microinstruction is printed).  Each number is over the
whole of image 2 of pimm.MEkbn and, where it says so, the PSI-III's
syspsi: the held stores, read through asm/mekbn.py.

  bit26_successor   for each 4-bit JMPF code whose low three bits are 3,
                    4 or 6, with and without CNDF: (words, words whose
                    next word is zero or an explicit target).  An
                    unconditional jump is followed by such a word; a
                    conditional one falls through to code.
  self_jumps        (words jumping to themselves, of them with bit 26,
                    the addresses without it)
  cnd9 / cndb       CNDF 9 words: (count, with TGIF 0, top EM1 values);
                    CNDF b words: (count, with TGIF non-zero, top EM2 values)
  odpf1             the decode entries whose nano-code ODPF is 1
  mekbn_under_bit26 mekbn's flow measures with tested() replaced by the
                    bit-26 rule: after a call (returns, ends) and decode
                    entries (ends, returns), image 2 and syspsi, each as
                    (under mekbn.tested(), under the bit-26 rule).  The
                    syspsi entries here are all those linked 4a01 (125 under
                    mekbn's rule; mekbn's own pin, 122, takes descriptor
                    1's index list, which omits 12 of them)

  python3 ref/pu/measure.py           print and check against PINNED
"""
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import mekbn  # noqa: E402
import kbn  # noqa: E402
import setup as SU  # noqa: E402
from mekbn import field, jk  # noqa: E402


def tagname(v):
    return kbn.TAGS.get(v, '%02x' % v)


def targets(img, fw=None):
    tg = set()
    for a, x in enumerate(img):
        if x:
            t = mekbn.flow(a, x)[1]
            if t is not None:
                tg.add(t)
    if fw:
        tg |= {v[1] for v in fw.kl1_entries().values()}
    return tg


def successor(img, tg):
    out = {}
    for a, x in enumerate(img[:-1]):
        if not x or jk(x) not in (3, 4, 6):
            continue
        key = '%x%s' % (field(x, 'JMPF'), '+cnd' if field(x, 'CNDF') else '')
        w, z = out.get(key, (0, 0))
        y = img[a + 1]
        out[key] = (w + 1, z + (1 if not y or a + 1 in tg else 0))
    return out


def self_jumps(img):
    loops = [(a, x) for a, x in enumerate(img) if x and mekbn.flow(a, x)[:2] == ('jump', a)]
    return (len(loops), sum(1 for _, x in loops if field(x, 'JMPF') & 8),
            ['%04x' % a for a, x in loops if not field(x, 'JMPF') & 8])


def cnd(img, value, free, cmp):
    ws = [x for x in img if x and jk(x) != 1 and field(x, 'CNDF') == value]
    tg = sum(1 for x in ws if (field(x, 'TGIF') == 0) == (free == 'zero'))
    top = Counter(tagname(field(x, cmp)) for x in ws).most_common(4)
    return (len(ws), tg, [t for t, _ in top])


def under_bit26(fw, psi):
    """(under mekbn's tested(), under the bit-26 rule) for each measure."""
    kl1 = set(v[1] for v in fw.kl1_entries().values())
    cls01 = set(fw.start(i)[0] for i in range(512)
                if fw.entry(i)[0][0] >> 16 == 0x4a01)

    def entry_ends(img, starts):
        e = [mekbn.first_end(img, s) for s in starts if s < len(img)]
        return (e.count('end'), e.count('return'))

    def one():
        f2, fp = mekbn.flow_measure(fw.img2), mekbn.flow_measure(psi)
        return {'img2_after_call': f2['after_call'], 'syspsi_after_call': fp['after_call'],
                'img2_entry_ends': entry_ends(fw.img2, kl1),
                'syspsi_entry_ends': entry_ends(psi, cls01),
                'syspsi_unconditional_self_jumps': fp['self_jumps'][1]}
    before = one()
    saved = mekbn.tested
    mekbn.tested = lambda x: bool(field(x, 'JMPF') & 8)
    try:
        after = one()
    finally:
        mekbn.tested = saved
    return {k: (before[k], after[k]) for k in before}


def measure():
    fw = mekbn.Firmware()
    psi = mekbn.syspsi()
    odpf1 = sorted(n for n, (idx, a, imm) in fw.kl1_entries().items()
                   if SU.nano(fw, idx)['ODPF'] == 1)
    return {
        'img2_bit26_successor': successor(fw.img2, targets(fw.img2, fw)),
        'syspsi_bit26_successor': successor(psi, targets(psi)),
        'img2_self_jumps': self_jumps(fw.img2),
        'syspsi_self_jumps': self_jumps(psi),
        'img2_cnd9': cnd(fw.img2, 9, 'zero', 'EM1'),
        'img2_cndb': cnd(fw.img2, 0xb, 'nonzero', 'EM2'),
        'odpf1': odpf1,
        'mekbn_under_bit26': under_bit26(fw, psi),
    }


PINNED = {
    'img2_bit26_successor': {'3': (160, 133), '3+cnd': (39, 27), '4': (271, 201),
                             '4+cnd': (71, 54), '6': (588, 278), '6+cnd': (503, 259),
                             'b': (32, 1), 'b+cnd': (15, 2), 'c': (151, 5), 'c+cnd': (118, 9),
                             'e': (114, 19), 'e+cnd': (292, 32)},
    'syspsi_bit26_successor': {'3': (159, 108), '3+cnd': (135, 66), '4': (469, 329),
                               '4+cnd': (93, 55), '6': (888, 478), '6+cnd': (740, 379),
                               'b': (15, 6), 'b+cnd': (15, 1), 'c': (232, 14),
                               'c+cnd': (183, 10), 'e': (306, 40), 'e+cnd': (519, 40)},
    'img2_self_jumps': (23, 23, []),
    'syspsi_self_jumps': (37, 36, ['4de1']),
    'img2_cnd9': (453, 448, ['ATOMo', 'INTo', 'REFo', 'VDESC']),
    'img2_cndb': (56, 24, ['ATOMo', 'INTo', 'VDESC', 'REFo']),
    'odpf1': ['collect_list', 'enqueue_goal', 'enqueue_goal_to_processor', 'proceed',
              'put_list', 'put_marked_variable', 'put_variable', 'put_vector_N[01]',
              'put_vector_N[02]', 'set_list', 'set_marked_variable', 'set_variable',
              'write_marked_variable', 'write_variable'],
    'mekbn_under_bit26': {'img2_after_call': ((222, 10), (234, 9)),
                          'syspsi_after_call': ((250, 13), (264, 7)),
                          'img2_entry_ends': ((96, 0), (107, 0)),
                          'syspsi_entry_ends': ((125, 0), (119, 0)),
                          'syspsi_unconditional_self_jumps': (0, 1)},
}


def check(quiet=False):
    got = measure()
    bad = [k for k in PINNED if got.get(k) != PINNED[k]]
    for k in sorted(got):
        if not quiet or k in bad:
            print('%s %s: %s' % ('FAIL' if k in bad else 'ok  ', k, got[k]))
    return not bad


if __name__ == '__main__':
    sys.exit(0 if check() else 1)
