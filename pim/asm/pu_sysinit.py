#!/usr/bin/env python3
"""What sysinit is: a systematic reading of PMPSI.DIR/sysinit (8,286
64-bit words, header load address 0x5000, entry 0x5000).

Results and labels: docs/pu_microcode_inference.md section 5.  In brief
(each item pinned by --check):

  0x5000-0x523f   an initialisation microprogram (Fig. 3-25 words; its
                  absolute calls land inside it)
  0x5240-0x527f   small control words (ffff masks)
  0x5280-0x533f   three 64 x 8-byte tag dispatch tables (TGT images,
                  thesis p.126: TGT 512 entries = 8 set-ups x 64 tags);
                  0x5300 is the KL1 one (VERIFIED for column 2 at six
                  dispatch sites of image 2)
  0x5580-0x57ff,
  0x6080-0x614f   message text (exceptions, "ERROR_..._(system)")
  0x5b80-0x5f80   a mnemonic for every decode index 0..0x3ff (header
                  word 0x400), 64-bit big-endian text
  0x5f80-0x603f   console text (step-trace formats)
  0x6800-0x6c0f   the decode table, word for word sysidat
  0x7000-0x705d   microcode again

Usage:
    python3 asm/pu_sysinit.py --check     the pinned measurements
    python3 asm/pu_sysinit.py --map       the 64-word block map
    python3 asm/pu_sysinit.py --tgt [T]   a tag table (5280, 52c0, 5300)
    python3 asm/pu_sysinit.py --mnemonics [LO HI]
"""
import csv
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kbn                                # noqa: E402
import psdpim                             # noqa: E402
from mekbn import field, flow             # noqa: E402
import pu_store                           # noqa: E402
from pu_store import INIT_BASE, IDAT_BASE, MNEMONIC_TABLE   # noqa: E402
import pu_cfg                             # noqa: E402

END = INIT_BASE + 8286
TGT_TABLES = (0x5280, 0x52c0, 0x5300)
KL1_TGT = 0x5300
KL1_COL_FOR_3A = 2            # the column the CNDF-7 set-up with EM1 = 3a selects
SETUP_EM1 = 0x3a
EM1_MASK = ~(0x3f << 10) & ((1 << 64) - 1)
KL0_TSV = os.path.join(HERE, '..', 'psi', 'kl0_opcodes.tsv')
TGT_STRIDE = 8                # bytes per tag row; an injection point


def text(w):
    return w.to_bytes(8, 'big')


def is_text(w):
    return w and sum(32 <= c < 127 for c in text(w)) >= 6


def block_kind(st, s):
    """A label for the 64-word block at s, from simple measures."""
    ws = [st.iw(a) for a in range(s, min(s + 64, END))]
    nz = [w for w in ws if w]
    if not nz:
        return 'zero'
    if IDAT_BASE <= s < IDAT_BASE + len(st.idat):
        return 'decode'
    if MNEMONIC_TABLE <= s < MNEMONIC_TABLE + 0x401:
        return 'mnemonic'
    if s in TGT_TABLES:
        return 'tgt'
    tx = sum(1 for w in nz if is_text(w))
    if tx * 2 > len(nz):
        return 'text'
    land = code = 0
    for a in range(s, min(s + 64, END)):
        x = st.iw(a)
        if x and field(x, 'JMPF') == 5:
            code += 1
            t = field(x, 'EM')
            land += INIT_BASE <= t < END and bool(st.iw(t))
    dbgf = sum(1 for w in nz if w >> 63)
    if dbgf * 20 <= len(nz) and code and land == code:
        return 'code'
    return 'data'


def block_map(st):
    out, cur = [], None
    for s in range(INIT_BASE, END, 64):
        k = block_kind(st, s)
        if cur and cur[0] == k:
            cur[2] = min(s + 64, END)
        else:
            cur = [k, s, min(s + 64, END)]
            out.append(cur)
    return [(k, '%04x-%04x' % (a, b - 1)) for k, a, b in out]


def tgt(st, base):
    """table[k][tag] = byte k of word base + tag (64 tags x 8 set-ups)."""
    return [[(st.iw(base + t) >> (TGT_STRIDE * k)) & 0xff for t in range(64)] for k in range(8)]


KL1_PAIRS = [(2 * i, 2 * i + 1) for i in range(32)
             if kbn.TAGS.get(2 * i, '').endswith('o') and kbn.TAGS.get(2 * i + 1, '').endswith('x')]


def family(tag):
    n = kbn.TAGS.get(tag, '?%02x' % tag)
    n = {'EUNDFo': 'UNDF', 'EUNDFx': 'UNDF', 'EHOOKo': 'HOOK', 'EHOOKx': 'HOOK',
         'EMHOKo': 'MHOOK', 'EMHOKx': 'MHOOK', 'HOOKo': 'HOOK', 'HOOKx': 'HOOK'}.get(n, n)
    return n[:-1] if n[-1:] in 'ox' and n not in ('MHOOK',) else n


def tgt_measure(st):
    out = {}
    tabs = {b: tgt(st, b) for b in TGT_TABLES}
    # o/x pairs of KL1 tags sent to the same byte, per table (over 8 columns)
    out['ox_same'] = {'%04x' % b: sum(1 for k in range(8) for o, x in KL1_PAIRS if T[k][o] == T[k][x])
                      for b, T in tabs.items()}
    out['ox_pairs'] = len(KL1_PAIRS) * 8
    T = tabs[KL1_TGT]
    # the vector-arity column: VECT0o..VECT6o, VECTo (tags 0x10..0x1e even)
    out['vect_column'] = [T[3][t] for t in range(0x10, 0x20, 2)]
    out['instr_tags_rows_equal'] = len({st.iw(KL1_TGT + t) for t in range(0x20, 0x24)})
    col = T[KL1_COL_FOR_3A]
    out['col2_classes'] = {c: sorted(kbn.TAGS.get(t, '%02x' % t) for t in range(64)
                                     if col[t] == c and t in kbn.TAGS)
                           for c in sorted(set(col)) if c != max(col)}
    out['col2_other'] = (max(col), sum(1 for t in range(64) if col[t] == max(col)))
    return out


def sites_3a(im):
    def setup(p):
        return field(p, 'JMPF') == 0 and field(p, 'CNDF') == pu_cfg.CASE_SETUP_CNDF
    return [(a, flow(a, x)[1]) for a, x in enumerate(im)
            if x and field(x, 'JMPF') == pu_cfg.CASE_JMPF and setup(im[a - 1])
            and field(im[a - 1], 'EM1') == SETUP_EM1]


def row_pattern(im, t, n=15):
    seen, ids = {}, []
    for i in range(n):
        w = im[t + i] & EM1_MASK
        seen.setdefault(w, len(seen))
        ids.append(seen[w])
    return ids


def agreement(st, im, t, base, k):
    """For a candidate (table, column): adjacent rows of one tag family that
    have equal code (EM1 masked), and adjacent rows of different families
    that differ, over the rows the column produces."""
    col = tgt(st, base)[k]
    cls = defaultdict(set)
    for g in range(64):
        if g in kbn.TAGS:
            cls[col[g]].add(family(g))
    rows = sorted(cls)
    if len(rows) < 4 or max(rows) > 31 or rows != list(range(len(rows))):
        return None
    fam = [next(iter(cls[r])) if len(cls[r]) == 1 else '*' for r in rows]
    ids = row_pattern(im, t, len(rows))
    same = [(r, r + 1) for r in rows[:-1] if fam[r] == fam[r + 1] != '*']
    diff = [(r, r + 1) for r in rows[:-1] if fam[r] != fam[r + 1]]
    return (sum(1 for a, b in same if ids[a] == ids[b]), len(same),
            sum(1 for a, b in diff if ids[a] != ids[b]), len(diff))


def column_test(st):
    """Column 2 of the KL1 table at the image-2 dispatch sites with EM1 = 3a,
    and how the other 23 table/column candidates do there."""
    im = st.img2
    out = {}
    for a, t in sites_3a(im):
        res = {}
        for b in TGT_TABLES:
            for k in range(8):
                r = agreement(st, im, t, b, k)
                if r:
                    res['%04x/%d' % (b, k)] = r
        mine = res.get('%04x/%d' % (KL1_TGT, KL1_COL_FOR_3A))
        best = max(res.values(), key=lambda r: (r[0] + r[2], r[1])) if res else None
        out['%04x' % a] = (''.join('%x' % i for i in row_pattern(im, t)), mine,
                           sorted(k for k, r in res.items() if r == best), len(res))
    return out


def mnemonics(st):
    return [st.mnemonic(i) for i in range(0x400)]


def subseq(short, long):
    it = iter(long)
    return all(c in it for c in short)


def norm(s):
    return ''.join(c for c in s.upper() if c.isalnum())


def mnemonic_measure(st):
    names = mnemonics(st)
    out = {'header': (st.iw(MNEMONIC_TABLE) & 0xffffffff, st.iw(MNEMONIC_TABLE) >> 32),
           'nonblank': sum(1 for n in names if n)}
    kl0 = []
    with open(KL0_TSV) as f:
        for row in csv.DictReader(f, delimiter='\t'):
            cls = {'pmi': 0, 'blt': 1}.get(row['class'])
            if cls is not None and len(row['opcode']) == 2:
                kl0.append((cls << 8 | int(row['opcode'], 16), row['mnemonic']))
    k1n = psdpim.names()
    kl1 = [((tag & 3) << 8 | op, n) for tag in (0x22, 0x23) for op, n in k1n.get(tag, {}).items()]

    def score(pairs, shift):
        hits = 0
        for idx, n in pairs:
            m = names[(idx + shift) % 0x400]
            hits += bool(m) and subseq(norm(m)[:3], norm(n))
        return hits
    for key, pairs in (('kl0', kl0), ('kl1', kl1)):
        out[key] = (len(pairs), score(pairs, 0), score(pairs, 1), score(pairs, -1))
    out['anchors'] = [names[i] for i in (0x05f, 0x0f0, 0x02a, 0x0aa, 0x140, 0x141, 0x150, 0x151)]
    return out


def pointer_measure(st):
    """Distinct 16-bit fields per region equal to a decode-entry start, against
    the density of starts in 0..0x7fff."""
    k0, k1 = set(st.kl0_roots()), set(st.kl1_roots())
    regions = {}
    for kind, span in block_map(st):
        a, b = (int(v, 16) for v in span.split('-'))
        vals = set()
        for x in range(a, b + 1):
            w = st.iw(x)
            for k in range(4):
                v = w >> (16 * k) & 0xffff
                if 0 < v < 0x8000:
                    vals.add(v)
        regions.setdefault('%s %s' % (span, kind), set()).update(vals)
    out = {}
    for kind, vals in sorted(regions.items()):
        out[kind] = (len(vals), len(vals & k0), round(len(vals) * len(k0) / 0x8000, 1),
                     len(vals & k1), round(len(vals) * len(k1) / 0x8000, 1))
    return out


def code_measure(st):
    out = {}
    for lo, hi in ((0x5000, 0x5240), (0x7000, END)):
        calls = [(a, field(st.iw(a), 'EM')) for a in range(lo, hi)
                 if st.iw(a) and field(st.iw(a), 'JMPF') == 5]
        inside = sum(1 for _, t in calls if lo <= t < hi and st.iw(t))
        upper = sum(1 for _, t in calls if t >= pu_store.SHARED_LO and not INIT_BASE <= t < END)
        out['%04x' % lo] = (len(calls), inside, upper,
                            sum(1 for a in range(lo, hi) if st.iw(a) >> 63))
    return out


def measure(st=None):
    st = st or pu_store.stores()
    got = {}
    h = st.init_header
    got['header'] = tuple(int.from_bytes(h[i:i + 4], 'little') for i in (0, 4, 8))
    hd = st.idat_header
    got['sysidat_header'] = tuple(int.from_bytes(hd[i:i + 4], 'little') for i in (0, 4, 8))
    got['sysidat_equal'] = sum(1 for i, w in enumerate(st.idat) if st.iw(IDAT_BASE + i) == w)
    got['map'] = block_map(st)
    got['code'] = code_measure(st)
    got['tgt'] = tgt_measure(st)
    got['column2'] = column_test(st)
    got['mnemonics'] = mnemonic_measure(st)
    got['pointers'] = pointer_measure(st)
    return got


PINNED = {'header': (20480, 8286, 20480),
 'sysidat_header': (26624, 1040, 20480),
 'sysidat_equal': 1040,
 'map': [('code', '5000-503f'),
         ('data', '5040-507f'),
         ('code', '5080-513f'),
         ('data', '5140-517f'),
         ('code', '5180-523f'),
         ('data', '5240-527f'),
         ('tgt', '5280-533f'),
         ('zero', '5340-537f'),
         ('data', '5380-543f'),
         ('zero', '5440-553f'),
         ('data', '5540-56ff'),
         ('text', '5700-57bf'),
         ('data', '57c0-5b7f'),
         ('mnemonic', '5b80-5fbf'),
         ('text', '5fc0-603f'),
         ('data', '6040-607f'),
         ('text', '6080-617f'),
         ('data', '6180-623f'),
         ('zero', '6240-627f'),
         ('data', '6280-677f'),
         ('zero', '6780-67ff'),
         ('decode', '6800-69ff'),
         ('zero', '6a00-6bff'),
         ('decode', '6c00-6c3f'),
         ('data', '6c40-6f3f'),
         ('zero', '6f40-6fff'),
         ('code', '7000-705d')],
 'code': {'5000': (39, 38, 1, 1), '7000': (3, 2, 0, 0)},
 'tgt': {'ox_same': {'5280': 126, '52c0': 101, '5300': 129},
         'ox_pairs': 168,
         'vect_column': [6, 8, 10, 12, 14, 16, 18, 20],
         'instr_tags_rows_equal': 1,
         'col2_classes': {0: ['UNDF'],
                          1: ['EUNDFo'],
                          2: ['EUNDFx'],
                          3: ['HOOKo', 'HOOKx'],
                          4: ['EHOOKo'],
                          5: ['EHOOKx'],
                          6: ['MHOOK'],
                          7: ['EMHOKo'],
                          8: ['EMHOKx'],
                          9: ['RHOOKo'],
                          10: ['RHOOKx'],
                          11: ['EXREFo', 'EXREFx', 'EXVALo', 'EXVALx'],
                          12: ['EXMRF'],
                          13: ['MGHOK']},
         'col2_other': (14, 46)},
 'column2': {'0221': ('000111222334005', (7, 7, 6, 7), ['5300/2'], 7),
             '0263': ('000111222334506', (7, 7, 7, 7), ['5300/2'], 7),
             '1d40': ('000111222334567', (7, 7, 7, 7), ['5300/2'], 7),
             '2d3f': ('000111222330000', (7, 7, 4, 7), ['5300/2'], 7),
             '2ed7': ('012034034345060', (0, 7, 7, 7), ['52c0/7'], 7),
             '3c61': ('000000000000001', (7, 7, 1, 7), ['5300/2'], 7)},
 'mnemonics': {'header': (1024, 65536),
               'nonblank': 824,
               # 153 rows, 124 named, before MENDELS's blt 3e freeze and 3f
               # melt (2026-11-27): the table names them FREEZE and MELT;
               # 155, 126 before blt 6c integer_to_floating_point and 6d
               # floating_point_to_integer (MENDELS temporary_menu step,
               # 2026-11-27): the table names them NtoSFL and NtoINT;
               # 157, 128 before blt 13 number and e8 if_number (MENDELS
               # window mixins step, 2026-11-27): the table names them
               # NUMB? (a hit) and jmpUNUM (no hit: the e0-eb names start
               # jmpU, as e0 and e1's do); 160, 130 since pmi 30
               # get_vector_0 (MENDELS, 2026-11-28): the table names it
               # GVCT0 (beside GVCT1, GVCT2 and PVCT0 at b0)
               'kl0': (160, 130, 53, 64),
               'kl1': (205, 179, 57, 55),
               'anchors': ['ALLOC', 'PROC', 'GLIST', 'PLIST', 'ADD', 'SUB', 'AND', 'OR']},
 'pointers': {'5000-503f code': (110, 12, 1.3, 3, 0.7),
              '5040-507f data': (69, 10, 0.8, 3, 0.4),
              '5080-513f code': (224, 16, 2.6, 3, 1.4),
              '5140-517f data': (93, 12, 1.1, 1, 0.6),
              '5180-523f code': (164, 11, 1.9, 4, 1.1),
              '5240-527f data': (24, 3, 0.3, 0, 0.2),
              '5280-533f tgt': (153, 15, 1.8, 1, 1.0),
              '5340-537f zero': (0, 0, 0.0, 0, 0.0),
              '5380-543f data': (34, 1, 0.4, 0, 0.2),
              '5440-553f zero': (0, 0, 0.0, 0, 0.0),
              '5540-56ff data': (287, 11, 3.3, 3, 1.8),
              '5700-57bf text': (192, 4, 2.2, 1, 1.2),
              '57c0-5b7f data': (237, 15, 2.7, 2, 1.5),
              '5b80-5fbf mnemonic': (496, 3, 5.7, 3, 3.2),
              '5fc0-603f text': (82, 1, 0.9, 1, 0.5),
              '6040-607f data': (101, 4, 1.2, 1, 0.6),
              '6080-617f text': (170, 3, 2.0, 2, 1.1),
              '6180-623f data': (6, 0, 0.1, 0, 0.0),
              '6240-627f zero': (0, 0, 0.0, 0, 0.0),
              '6280-677f data': (633, 35, 7.3, 11, 4.1),
              '6780-67ff zero': (0, 0, 0.0, 0, 0.0),
              '6800-69ff decode': (478, 227, 5.5, 3, 3.1),
              '6a00-6bff zero': (0, 0, 0.0, 0, 0.0),
              '6c00-6c3f decode': (75, 6, 0.9, 0, 0.5),
              '6c40-6f3f data': (393, 27, 4.5, 0, 2.5),
              '6f40-6fff zero': (0, 0, 0.0, 0, 0.0),
              '7000-705d code': (139, 13, 1.6, 5, 0.9)}}


def check():
    got = measure()
    fails = []

    def cmp(path, g, p):
        if isinstance(p, dict):
            for k in p:
                cmp(path + [str(k)], g.get(k) if isinstance(g, dict) else None, p[k])
        elif g != p:
            fails.append('%s: got %r, pinned %r' % ('.'.join(path), g, p))
    cmp([], got, PINNED)
    for f in fails:
        print('FAIL pu_sysinit ' + f)
    t, m = got['tgt'], got['mnemonics']
    print('pu_sysinit: sysidat = sysinit %04x+ in %d/%d words; KL1 o/x tag pairs given one byte '
          'in %s of %d (by table); column 2 of %04x matches the family grouping at %d image-2 '
          'sites; mnemonic table names %d/%d KL0 and %d/%d KL1 opcodes (index +1: %d, %d)'
          % (IDAT_BASE, got['sysidat_equal'], len(pu_store.stores().idat), t['ox_same'],
             t['ox_pairs'], KL1_TGT,
             sum(1 for v in got['column2'].values() if v[1] and v[1][0] == v[1][1] and v[1][1]),
             m['kl0'][1], m['kl0'][0], m['kl1'][1], m['kl1'][0], m['kl0'][2], m['kl1'][2]))
    print('pu_sysinit --check: %s' % ('FAIL' if fails else 'PASS'))
    return not fails


def main(argv):
    if not argv or argv[0] == '--check':
        return 0 if check() else 1
    st = pu_store.stores()
    if argv[0] == '--report':
        for k, v in measure(st).items():
            print(k, v)
    elif argv[0] == '--map':
        for k, span in block_map(st):
            print(span, k)
    elif argv[0] == '--tgt':
        base = int(argv[1], 16) if len(argv) > 1 else KL1_TGT
        T = tgt(st, base)
        for g in range(64):
            print('%02x %-8s %s' % (g, kbn.TAGS.get(g, ''), ' '.join('%02x' % T[k][g] for k in range(8))))
    elif argv[0] == '--mnemonics':
        lo = int(argv[1], 16) if len(argv) > 1 else 0
        hi = int(argv[2], 16) if len(argv) > 2 else 0x400
        for i in range(lo, hi):
            print('%03x %s' % (i, st.mnemonic(i)))
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
