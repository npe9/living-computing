#!/usr/bin/env python3
"""Microsequencer model and whole-firmware control-flow graphs of the
held PSI-III control stores: syspsi (ESP/KL0) and the KL1 program
(pimm.MEkbn image 2, run with syspsi's 0x6800..0x7fff above it).

The rules, their evidence labels and the results are in
docs/pu_microcode_inference.md (sections 2-4).  Every number that
section quotes is pinned in PINNED and checked by --check.

Sequencer rules (label; source):
  S1  JMPF 0 / 8: next address = a + 1                    VERIFIED (mekbn s.8)
  S2  JMPF 1 EM bit 3: jump (EM & 0x7ff0) | CNDF          VERIFIED (mekbn s.8)
  S2b JMPF 1 jump with EM bit 2 set: multiway, the low
      target bits ORed in at run time                     INFERRED here (s.2.2): targets
                                                          aligned to 8/16, MEASURED
  S3  JMPF 1 EM bit 3 clear, bit 2 clear: end of the
      machine instruction (next is the decode dispatch)   VERIFIED (mekbn s.8)
  S4  JMPF 1 EM bit 2: return (pop MSTK)                  VERIFIED (mekbn s.8);
                                                          MSTK DOCUMENTED (thesis p.126)
  S5  JMPF 1 EM bit 1: S2-S4 conditional                  VERIFIED (mekbn s.8)
  S6  JMPF 4: a + signed EM bits 3..0                     VERIFIED (mekbn s.8)
  S7  JMPF 5 call absolute EM; 7 / f call page-relative;
      6 / e / b page-relative jump; a page-relative
      conditional branch                                  VERIFIED (mekbn s.8)
  S8  4-bit JMPF 3: multiway "case_branch": base
      (page | EM bits 9..0), low bits ORed from TDAR
      (the TGT byte selected by a CNDF 7 set-up word)     INFERRED here (s.2.2):
                                                          mechanism DOCUMENTED (thesis
                                                          p.131), 16-alignment MEASURED,
                                                          one TGT column VERIFIED
  S9  JMPF 1 with EM = 7fff: not an address (computed /
      special form; its "targets" are 12 DBGF-only filler
      words at syspsi 7ff0-7ffb)                          INFERRED (s.2.3)
  S10 4-bit JMPF 2: open (falls through here)             UNKNOWN (psi_microword 7)
  S11 decode dispatch: KL1 entries from pimm.MEkbn
      classes 2/3, KL0 entries from sysidat classes 0/1   MEASURED (mekbn s.3,
                                                          psi_microword 4.4)
  S12 decode-entered tag tables: a 32-aligned entry whose
      words at +4r start rows (the word before cannot
      fall through) is entered at each row by the S
      stage's tag multiway                                INFERRED (thesis p.134 mechanism;
                                                          mekbn s.9 row structure)
  S13 the non-zero words at 0..15 are entry vectors
      (reset, traps); 0..f equal in both firmwares        INFERRED (s.3)

Usage:
    python3 asm/pu_cfg.py --check        the pinned measurements
    python3 asm/pu_cfg.py --report       headline numbers, both firmwares
    python3 asm/pu_cfg.py --cross        the cross-image evidence
    python3 asm/pu_cfg.py --fanin N      the N highest fan-in addresses
"""
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mekbn                         # noqa: E402
from mekbn import field, flow, jk    # noqa: E402
import pu_store                      # noqa: E402
from pu_store import SHARED_LO, IMG1_LEN, DATE_WORD   # noqa: E402

CASE_JMPF = 3          # 4-bit JMPF code of the multiway (S8); an injection point
CASE_SETUP_CNDF = 7    # CNDF of the set-up word that precedes it
CASE_WIDTH = 16        # TDAR bits ORed into the base (4 bits)
SPECIAL_EM = 0x7fff    # S9
J1_CASE_BIT = 4        # S2b: a JMPF 1 jump with EM bit 2 is a multiway (aligned targets)
VECTORS = 16           # S13: the non-zero words at 0..15 are entry vectors
ROW_STRIDE, TABLE_ALIGN = 4, 32    # S12


def rule(a, x, im):
    """(kind, [targets], falls_through) of the word x at address a."""
    if not x:
        return 'zero', [], False
    j4 = field(x, 'JMPF')
    if jk(x) == 1 and field(x, 'EM') == SPECIAL_EM:
        return 'special', [], bool(field(x, 'EM') & mekbn.J1_COND)
    em = field(x, 'EM')
    if j4 == CASE_JMPF or jk(x) == 1 and em & mekbn.J1_JUMP and em & J1_CASE_BIT:
        base = flow(a, x)[1]
        ts = [base | d for d in range(CASE_WIDTH) if (base | d) < len(im) and im[base | d]]
        return ('case' if j4 == CASE_JMPF else 'case1'), ts, flow(a, x)[2]
    kind, t, falls = flow(a, x)
    if kind == 'next':
        return 'seq', [], True
    if kind == 'jmpf2':
        return 'open', [], True
    if kind in ('end', 'return'):
        return kind, [], falls
    if a == DATE_WORD and im[a] >> 32 == 2:      # the date stamp of image 2 (data)
        return 'data', [], False
    return kind, [t], falls


class CFG:
    """Static CFG of one WCS configuration from its roots."""

    def __init__(self, im, roots, name=''):
        self.im, self.name = im, name
        self.roots = dict(roots)
        self.rules = {a: rule(a, x, im) for a, x in enumerate(im) if x}
        self._reach()

    def static_targets(self, a):
        kind, ts, falls = self.rules[a]
        return ts

    def _reach(self):
        im, seen, work = self.im, set(), [a for a in self.roots if self.im[a]]
        self.dangling = Counter()        # targets on zero words
        while work:
            a = work.pop()
            if a in seen or not im[a]:
                continue
            seen.add(a)
            kind, ts, falls = self.rules[a]
            nxt = list(ts)
            if falls or kind == 'call':
                nxt.append(a + 1)
            for t in nxt:
                if t < len(im) and im[t]:
                    work.append(t)
                elif t in ts:
                    self.dangling[t] += 1
        self.reach = seen

    def fanin(self):
        """{target: number of distinct referencing words} over static targets."""
        c = Counter()
        for a, x in enumerate(self.im):
            if x:
                for t in set(bases(a, x, self.im)[1]):
                    c[t] += 1
        return c

    def intra_edges(self, a):
        """Edges inside a routine: everything except call -> target."""
        kind, ts, falls = self.rules[a]
        out = [] if kind == 'call' else list(ts)
        if falls or kind == 'call':
            out.append(a + 1)
        return [t for t in out if t in self.reach]

    def sccs(self):
        """Non-trivial strongly connected components (iterative Tarjan)
        of the intra-routine graph over reachable words, and self-loops."""
        index, low, onstack, stack, comps = {}, {}, set(), [], []
        counter = [0]
        for root in sorted(self.reach):
            if root in index:
                continue
            work = [(root, iter(self.intra_edges(root)))]
            index[root] = low[root] = counter[0]; counter[0] += 1
            stack.append(root); onstack.add(root)
            while work:
                v, it = work[-1]
                adv = False
                for w in it:
                    if w not in index:
                        index[w] = low[w] = counter[0]; counter[0] += 1
                        stack.append(w); onstack.add(w)
                        work.append((w, iter(self.intra_edges(w))))
                        adv = True
                        break
                    elif w in onstack:
                        low[v] = min(low[v], index[w])
                if adv:
                    continue
                work.pop()
                if work:
                    low[work[-1][0]] = min(low[work[-1][0]], low[v])
                if low[v] == index[v]:
                    comp = []
                    while True:
                        w = stack.pop(); onstack.discard(w); comp.append(w)
                        if w == v:
                            break
                    if len(comp) > 1:
                        comps.append(sorted(comp))
        selfl = [a for a in self.reach if a in self.intra_edges(a)]
        return comps, selfl

    def unreachable_runs(self, lo=0, hi=None):
        hi = len(self.im) if hi is None else hi
        runs, start = [], None
        for a in range(lo, hi + 1):
            dead = a < hi and self.im[a] and a not in self.reach
            if dead and start is None:
                start = a
            elif not dead and start is not None:
                runs.append((start, a - start))
                start = None
        return runs


def tag_table_rows(im, entries):
    """S12: extra roots entry + 4r for 32-aligned decode entries."""
    out = {}
    for e in entries:
        if e % TABLE_ALIGN:
            continue
        for r in range(1, TABLE_ALIGN // ROW_STRIDE):
            a = e + r * ROW_STRIDE
            if a < len(im) and im[a] and not (im[a - 1] and rule(a - 1, im[a - 1], im)[2]):
                out[a] = 'row'
    return out


def configs(st=None):
    """The two WCS configurations with their roots."""
    st = st or pu_store.stores()
    k1 = st.kl1_roots()
    k1.update({a: v for a, v in tag_table_rows(st.kl1_wcs, k1).items() if a not in k1})
    k0 = st.kl0_roots()
    k0.update({a: v for a, v in tag_table_rows(st.psi, k0).items() if a not in k0})
    for a in range(VECTORS):
        if st.img2[a]:
            k1.setdefault(a, 'vector%x' % a)
        if st.psi[a]:
            k0.setdefault(a, 'vector%x' % a)
    return {'kl1': CFG(st.kl1_wcs, k1, 'KL1 (image 2 + syspsi upper)'),
            'kl0': CFG(st.psi, k0, 'KL0 (syspsi)')}


def repeated(im, lo, hi, k=4):
    """Identical k-word windows of non-zero words; (distinct repeated, sites, top)."""
    pos = defaultdict(list)
    for a in range(lo, hi - k + 1):
        w = tuple(im[a:a + k])
        if all(w):
            pos[w].append(a)
    reps = {}
    for w, ps in pos.items():
        keep, last = [], -k
        for p in ps:
            if p >= last + k:
                keep.append(p); last = p
        if len(keep) > 1:
            reps[w] = keep
    top = sorted(reps.items(), key=lambda kv: (-len(kv[1]), kv[1][0]))[:5]
    return len(reps), sum(len(v) for v in reps.values()), [(len(v), '%04x' % v[0]) for _, v in top]


def case_sites(im):
    """S8 evidence: JMPF 3 words, how many 16-aligned, how many after a CNDF-7 set-up."""
    w = [(a, x) for a, x in enumerate(im) if x and field(x, 'JMPF') == CASE_JMPF]
    al = sum(1 for a, x in w if flow(a, x)[1] % 16 == 0)
    su = sum(1 for a, x in w if field(im[a - 1], 'JMPF') == 0 and
             field(im[a - 1], 'CNDF') == CASE_SETUP_CNDF)
    others = [(a, x) for a, x in enumerate(im) if x and field(x, 'JMPF') in (6, 0xe, 0xb, 7, 0xa)]
    oal = sum(1 for a, x in others if flow(a, x)[1] % 16 == 0)
    return len(w), al, su, len(others), oal


def bases(a, x, im):
    """Static (named) targets of a word: a multiway's base, not its expansion."""
    kind, ts, falls = rule(a, x, im)
    if kind in ('zero', 'special', 'data', 'seq', 'open', 'end', 'return'):
        return kind, []
    return kind, [flow(a, x)[1]]


def cross(st=None):
    """The evidence on image 2's jumps above 0x67ff (section 3)."""
    st = st or pu_store.stores()
    psi, img2 = st.psi, st.img2
    out = {}
    eq = sorted(a for a in range(SHARED_LO) if img2[a] and img2[a] == psi[a])
    out['equal_words'] = ['%04x' % a for a in eq]
    up = defaultdict(list)            # image 2 -> syspsi upper
    for a, x in enumerate(img2):
        kind, ts = bases(a, x, img2)
        for t in ts:
            if t >= SHARED_LO:
                up[t].append((a, kind))
    low = defaultdict(list)           # syspsi lower (image 1) -> upper
    for a in range(IMG1_LEN):
        kind, ts = bases(a, psi[a], psi)
        for t in ts:
            if t >= SHARED_LO:
                low[t].append(a)
    sp = sum(1 for a, x in enumerate(img2)
             if x and rule(a, x, img2)[0] == 'special')
    out['img2_to_upper'] = (len(up), sum(len(v) for v in up.values()),
                            sum(1 for t in up if psi[t]), len(set(up) & set(low)), sp)
    out['kl0_to_upper'] = (len(low), sum(len(v) for v in low.values()))
    # the vector table 6c00..6c25: every entry reads and calls a group handler 6c30+2k
    vt = [a for a in range(0x6c00, 0x6c26) if psi[a]]
    vt_ok = sum(1 for a in vt if rule(a, psi[a], psi)[0] == 'call'
                and 0x6c30 <= rule(a, psi[a], psi)[1][0] <= 0x6c3e
                and psi[a] >> 61 & 1)
    stubs = [a for a in range(SHARED_LO) if img2[a] and bases(a, img2[a], img2) == ('call', [0x6c21])]
    # a stub is "call 6c21" standing alone: the words around it are zero or end the routine
    stub_alone = sum(1 for a in stubs if not img2[a - 1] or not rule(a - 1, img2[a - 1], img2)[2])
    out['vector_table'] = (len(vt), vt_ok, len(up.get(0x6c21, [])), len(stubs), stub_alone)
    # upper syspsi -> below 0x6800: the 0x6000/0x6400 interface
    back = defaultdict(list)
    for a in range(SHARED_LO, 0x8000):
        kind, ts = bases(a, psi[a], psi)
        for t in ts:
            if t < SHARED_LO:
                back[t].append(a)

    def starts(im, t):
        p = im[t - 1] if t else 0
        return bool(im[t]) and not (p and rule(t - 1, p, im)[2])
    iface = sorted(t for t in back if 0x6000 <= t < 0x6440)
    out['interface'] = (len(iface), sum(len(back[t]) for t in iface),
                        sum(1 for t in iface if not psi[t]),
                        sum(1 for t in iface if not psi[t] and img2[t]),
                        sum(1 for t in iface if img2[t]),
                        sum(1 for t in iface if starts(img2, t)))
    other = sorted(t for t in back if not 0x6000 <= t < 0x6440)
    out['upper_to_low_other'] = ['%04x:%s' % (t, 'eq' if t in eq else 'i2' if img2[t] else 'z')
                                 for t in other]
    # the page dispatch 6f02/6f04/6f06 -> 6000, 6400, 6800
    out['page_dispatch'] = [(flow(a, psi[a])[1], rule(a, psi[a], psi)[0]) for a in (0x6f02, 0x6f04, 0x6f06)]
    # filler words that S9 "targets" would land on
    out['filler_7ff0'] = sum(1 for a in range(0x7ff0, 0x7ffc) if psi[a] == 1 << 63)
    return out


def measure(st=None):
    st = st or pu_store.stores()
    cf = configs(st)
    got = {}
    for key, g in cf.items():
        im = g.im
        nz = sum(1 for x in im if x)
        kinds = Counter(r[0] for r in g.rules.values())
        comps, selfl = g.sccs()
        runs = g.unreachable_runs()
        fan = g.fanin()
        top = [('%04x' % t, n) for t, n in sorted(fan.items(), key=lambda kv: (-kv[1], kv[0]))[:8]]
        got[key] = {
            'nonzero': nz, 'roots': len(g.roots), 'reachable': len(g.reach),
            'kinds': dict(sorted(kinds.items())),
            'dangling': (len(g.dangling), sum(g.dangling.values())),
            'sccs': (len(comps), max(len(c) for c in comps), len(selfl)),
            'unreachable': (sum(n for _, n in runs), len(runs)),
            'largest_dead': [('%04x' % s, n) for s, n in sorted(runs, key=lambda r: -r[1])[:4]],
            'fanin_top': top,
            'fanin_ge10': sum(1 for n in fan.values() if n >= 10),
        }
    got['kl1']['upper_reached'] = sum(1 for a in cf['kl1'].reach if a >= SHARED_LO)
    got['kl0']['upper_reached'] = sum(1 for a in cf['kl0'].reach if a >= SHARED_LO)
    got['case_img2'] = case_sites(st.img2)
    got['case_psi'] = case_sites(st.psi)
    got['repeated_img2'] = repeated(st.img2, 0, SHARED_LO)
    got['repeated_psi'] = repeated(st.psi, 0, 0x8000)
    w4 = {tuple(st.psi[a:a + 4]) for a in range(0x8000 - 3) if all(st.psi[a:a + 4])}
    got['shared_4seq'] = sum(1 for a in range(SHARED_LO - 3)
                             if all(st.img2[a:a + 4]) and tuple(st.img2[a:a + 4]) in w4)
    got['cross'] = cross(st)
    return got


PINNED = {'kl1': {'nonzero': 23556,
         'roots': 353,
         'reachable': 12591,
         'kinds': {'branch': 711,
                   'call': 3077,
                   'case': 200,
                   'case1': 386,
                   'data': 1,
                   'end': 829,
                   'jump': 5902,
                   'open': 16,
                   'return': 1606,
                   'seq': 10779,
                   'special': 49},
         'dangling': (2, 4),
         'sccs': (221, 99, 25),
         'unreachable': (10965, 869),
         'largest_dead': [('540a', 358), ('7487', 303), ('7893', 228), ('72dd', 218)],
         'fanin_top': [('6c21', 244),
                       ('0d87', 66),
                       ('082b', 53),
                       ('3331', 52),
                       ('0d88', 46),
                       ('4678', 42),
                       ('1924', 39),
                       ('6c22', 39)],
         'fanin_ge10': 127,
         'upper_reached': 1762},
 'kl0': {'nonzero': 24414,
         'roots': 528,
         'reachable': 14738,
         'kinds': {'branch': 1203,
                   'call': 2129,
                   'case': 294,
                   'case1': 491,
                   'end': 1011,
                   'jump': 6894,
                   'open': 26,
                   'return': 1197,
                   'seq': 11120,
                   'special': 49},
         'dangling': (5, 8),
         'sccs': (321, 285, 72),
         'unreachable': (9676, 907),
         'largest_dead': [('3cce', 301), ('59a0', 247), ('78ab', 204), ('2cd9', 178)],
         'fanin_top': [('682c', 155),
                       ('08c3', 145),
                       ('6c05', 64),
                       ('6c04', 50),
                       ('6800', 42),
                       ('5405', 41),
                       ('33a3', 38),
                       ('5406', 38)],
         'fanin_ge10': 125,
         'upper_reached': 2962},
 'case_img2': (199, 156, 108, 2259, 169),
 'case_psi': (294, 248, 108, 4304, 268),
 'repeated_img2': (304, 760, [(17, '0886'), (17, '0cc4'), (10, '0887'), (7, '0448'), (6, '2da7')]),
 'repeated_psi': (514, 1356, [(17, '6ac6'), (12, '2f93'), (10, '2f9a'), (8, '2315'), (8, '2ba1')]),
 'shared_4seq': 100,
 'cross': {'equal_words': ['0000',
                           '0002',
                           '0003',
                           '0004',
                           '0005',
                           '0006',
                           '0009',
                           '000a',
                           '000c',
                           '000d',
                           '000e',
                           '000f',
                           '3d84',
                           '4281',
                           '483b'],
           'img2_to_upper': (24, 333, 23, 11, 14),
           'kl0_to_upper': (94, 638),
           'vector_table': (30, 30, 244, 185, 66),
           'interface': (11, 81, 5, 5, 11, 8),
           'upper_to_low_other': ['0000:eq',
                                  '0384:z',
                                  '038c:z',
                                  '0391:z',
                                  '039b:z',
                                  '039d:z',
                                  '03c4:z',
                                  '03c6:z',
                                  '0400:i2',
                                  '0403:z',
                                  '2004:i2',
                                  '510f:i2'],
           'page_dispatch': [(24576, 'case1'), (25600, 'case1'), (26624, 'case1')],
           'filler_7ff0': 12}}


def check():
    got = measure()
    fails = []

    def cmp(path, g, p):
        if isinstance(p, dict):
            for k in p:
                cmp(path + [k], g.get(k) if isinstance(g, dict) else None, p[k])
        elif g != p:
            fails.append('%s: got %r, pinned %r' % ('.'.join(path), g, p))
    cmp([], got, PINNED)
    for f in fails:
        print('FAIL pu_cfg ' + f)
    k1, k0, cx = got['kl1'], got['kl0'], got['cross']
    print('pu_cfg: KL1 WCS %d words, %d reached from %d roots, %d dead runs; KL0 %d, %d from %d; '
          'JMPF 3 targets 16-aligned %d/%d (img2) %d/%d (syspsi); image 2 -> syspsi upper: %d '
          'targets (%d non-zero there, %d also used by KL0), 6c21 called %d times; upper -> '
          '6000-643f: %d targets, %d zero in syspsi and non-zero in image 2'
          % (k1['nonzero'], k1['reachable'], k1['roots'], k1['unreachable'][1], k0['nonzero'],
             k0['reachable'], k0['roots'], got['case_img2'][1], got['case_img2'][0],
             got['case_psi'][1], got['case_psi'][0], cx['img2_to_upper'][0],
             cx['img2_to_upper'][2], cx['img2_to_upper'][3], cx['vector_table'][2],
             cx['interface'][0], cx['interface'][3]))
    print('pu_cfg --check: %s' % ('FAIL' if fails else 'PASS'))
    return not fails


def main(argv):
    if not argv or argv[0] == '--check':
        return 0 if check() else 1
    st = pu_store.stores()
    if argv[0] == '--report':
        got = measure(st)
        for k, v in got.items():
            print(k, v)
    elif argv[0] == '--cross':
        for k, v in cross(st).items():
            print(k, v)
    elif argv[0] == '--fanin':
        n = int(argv[1]) if len(argv) > 1 else 20
        for key, g in configs(st).items():
            names = dict(g.roots)
            fan = g.fanin()
            print('==', g.name)
            for t, c in sorted(fan.items(), key=lambda kv: -kv[1])[:n]:
                print('  %04x %4d %s' % (t, c, names.get(t, '')))
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
