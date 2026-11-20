#!/usr/bin/env python3
"""Structure of the Pseudo PIM/m firmware file PMPSI.DIR/pimm.MEkbn.

What is read here (docs/pseudo_pimm_microcode.md has the evidence and
says which statements are measured and which inferred):

  file words (40-bit: 32-bit value, 8-bit tag), load address 0x4200
    0x00000-0x007ff  decode table, 1024 two-word entries (asm/psdpim.py)
    0x00800-0x008ec  descriptor 1: links, image 1 base and length, and
                     a list of decode indices (classes 0 and 1)
    0x00900-0x0b8ff  image 1: 0x5800 microinstructions, identical to
                     syspsi (the PSI-III system firmware) 0..0x57ff
    0x0b900-0x0b9a9  descriptor 2: image 2 base and length, and the
                     list of decode indices of classes 2 and 3
    0x0ba00-0x189ff  image 2: 0x6800 microinstructions, the KL1
                     microprogram

  A microinstruction is two consecutive file words, low 32 bits first,
  both tags zero.  The microinstruction at address A of the KL1
  microprogram is file words 0xba00 + 2*A and 0xba00 + 2*A + 1.

  A decode entry's second word gives the start address two ways:
    tag byte & 0x18 == 0:  address = value bits 14..0
    tag byte & 0x18 != 0:  address = (decode index >> 7) << 11
                                     | value bits 9..0,
                           and value bits 15..10 are a 6-bit tag
                           immediate (ATOM for wait_atom, VECT3o for
                           wait_vector_3, COD for code, ...).

  Microinstruction fields that are established: bits 25..23 (TR-733's
  JMPF) select the branch kind and bits 15..0 (EM1..EM3) are its
  operand: JMPF 5 takes bits 15..0 as an absolute address; JMPF 2, 3, 6
  and 7 take bits 9..0 as an address in the current 1024-word page and
  bits 15..10 as a 6-bit immediate.  The other field boundaries printed
  by --dis are TR-733 fig. 4 as measured from the figure: a hypothesis.

Usage:
    python3 asm/mekbn.py --check            the pinned checks
    python3 asm/mekbn.py --segments         the file's layout
    python3 asm/mekbn.py --entries          KL1 start address per instruction
    python3 asm/mekbn.py --dis ADDR [N]     N microinstructions of image 2 (hex ADDR)
    python3 asm/mekbn.py --tag NAME         image-2 microinstructions carrying that
                                            tag immediate in a page-relative branch
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kbn      # noqa: E402
import psdpim   # noqa: E402

LOAD = 0x4200
DESC1, IMG1, IMG1_LEN = 0x800, 0x900, 0x5800
DESC2, IMG2, IMG2_LEN = 0xb900, 0xba00, 0x6800
RUN1 = (0x805, 0x8eb)     # file words holding descriptor 1's index list
RUN2 = (0xb902, 0xb9a8)

# TR-733 fig. 4, positions measured from the figure (hypothesis), except
# JMP and EM, which are checked below.
FIELDS = [('CCF', 62, 58), ('DST', 56, 52), ('SC1', 51, 47), ('SC2', 46, 42),
          ('SD1', 41, 39), ('SD2', 38, 37), ('AS1', 36, 34), ('AS2', 33, 32),
          ('AD', 31, 29), ('AL', 28, 26), ('JMP', 25, 23), ('CND', 22, 19),
          ('x18', 18, 18), ('x17', 17, 16), ('EM', 15, 0)]
PAGE_RELATIVE = (2, 3, 6, 7)
ABSOLUTE = 5

PINNED = dict(
    img1_nonzero=17496, img1_equal_syspsi=17496, img2_nonzero=18343,
    img2_equal_img1=15, image_tags_nonzero=0,
    run2_len=331, run2_distinct=324, run2_descents=0, run2_landing=331,
    run2_descents_low15_only=22, run2_landing_low15_only=319,
    run1_len=459, run1_descents=7, run1_landing=457, run1_descents_low15_only=61,
    kl1_entries=216, kl1_entries_landing=216,
    sysidat=(1040, 496, 16, 0),
    syspsi_jmp5=(1455, 1455), img2_jmp5=(2127, 1889, 238, 238, 15),
    img2_page_relative=((2, 532, 525), (3, 246, 246), (6, 1497, 1497), (7, 231, 231)),
)

# name -> tag immediate its decode entry must carry.  None of these was
# used to find the rule; the tag values are asm/kbn.py's TAGS (from the
# PIMOS inspector's source).
ENTRY_TAGS = {
    'atom': 'ATOMo', 'integer': 'INTo', 'list': 'LISTo', 'code': 'COD', 'module': 'MOD',
    'wait_atom': 'ATOMo', 'wait_nil': 'ATOMo', 'wait_integer': 'INTo', 'wait_list': 'LISTo',
    'wait_vector': 'VECTo', 'set_atom': 'ATOMo', 'put_atom': 'ATOMo', 'write_atom': 'ATOMo',
    'set_integer': 'INTo', 'put_integer': 'INTo', 'write_integer': 'INTo',
    'switch_on_non_integer': 'INTo', 'switch_on_non_atom': 'ATOMo',
    'switch_on_non_list': 'LISTo', 'collect_list': 'LISTo', 'collect_vector': 'VECTo',
}
TAG = {v: k for k, v in kbn.TAGS.items()}


def field(x, name):
    for n, hi, lo in FIELDS:
        if n == name:
            return (x >> lo) & ((1 << (hi - lo + 1)) - 1)
    raise KeyError(name)


class Firmware:
    def __init__(self):
        self.ws = psdpim.words(psdpim.member('PMPSI.DIR/pimm.MEkbn'))
        self.img1 = self._image(IMG1, IMG1_LEN)
        self.img2 = self._image(IMG2, IMG2_LEN)
        self.tb = psdpim.table(self.ws)
        self.names = psdpim.names()

    def _image(self, base, n):
        ws = self.ws
        return [ws[base + 2 * i][0] | ws[base + 2 * i + 1][0] << 32 for i in range(n)]

    def run(self, span):
        """A descriptor's list of decode indices (16-bit, high half first)."""
        out = []
        for i in range(*span):
            out += [self.ws[i][0] >> 16, self.ws[i][0] & 0xffff]
        return out[:-1]         # the last word (tag 0a) holds one index

    def entry(self, index):
        return self.tb[index >> 8][index & 255]

    def start(self, index, low15_only=False):
        """(address, tag immediate or None) of a decode entry."""
        (_, _), (v, t) = self.entry(index)
        if t & 0x18 and not low15_only:
            return (index >> 7) << 11 | v & 0x3ff, v >> 10 & 0x3f
        return v & 0x7fff, None

    def kl1_entries(self):
        """{name: (index, address, tag immediate)} for classes 2 (GMI), 3 (KLB)."""
        out = {}
        for cls, tag in ((2, 0x22), (3, 0x23)):
            named = dict(self.names[tag])
            for fam, lo, hi in psdpim.FAMILIES[tag]:
                for op in range(lo, hi + 1):
                    named.setdefault(op, '%s[%02x]' % (fam, op - lo))
            for op in range(256):
                if self.tb[cls][op] != psdpim.EMPTY:
                    idx = cls << 8 | op
                    out[named.get(op, '%d:%02x' % (cls, op))] = (idx,) + self.start(idx)
        return out


def syspsi():
    raw = psdpim.member('PMPSI.DIR/syspsi')[256:]
    return [int.from_bytes(raw[i:i + 8], 'little') for i in range(0, len(raw), 8)]


def sorted_run(fw, run, image, **kw):
    seq = [fw.start(i, **kw)[0] for i in run]
    descents = sum(1 for a, b in zip(seq, seq[1:]) if b < a)
    landing = sum(1 for a in seq if a < len(image) and image[a])
    return descents, landing


def measure():
    fw = Firmware()
    psi = syspsi()
    got = {}
    got['img1_nonzero'] = sum(1 for x in fw.img1 if x)
    got['img1_equal_syspsi'] = sum(1 for a, x in enumerate(fw.img1) if x and x == psi[a])
    got['img1_differs'] = sum(1 for a, x in enumerate(fw.img1) if x != psi[a])
    got['img2_nonzero'] = sum(1 for x in fw.img2 if x)
    got['img2_equal_img1'] = sum(1 for a, x in enumerate(fw.img1) if x and x == fw.img2[a])
    got['image_tags_nonzero'] = sum(1 for v, t in fw.ws[IMG1:IMG1 + 2 * IMG1_LEN] if t) + \
        sum(1 for v, t in fw.ws[IMG2:IMG2 + 2 * IMG2_LEN] if t)
    # the descriptors' pointers are file words + the header's load address
    ws = fw.ws
    got['pointers'] = [
        ws[0x801] == (LOAD + 0x803, 0x1c), ws[0x802] == (LOAD + DESC2, 0x0b),
        ws[0x803] == (LOAD + IMG1, 0), ws[0x804] == (IMG1_LEN << 16, 0),
        ws[DESC2] == (LOAD + IMG2, 0), ws[DESC2 + 1] == (IMG2_LEN << 16, 0),
        # decode word 1's high half names the descriptor link word of its image
        all(fw.tb[c][op][0][0] >> 16 == LOAD + 0x801 for c in (0, 1) for op in range(256)
            if fw.tb[c][op] != ((0, 0), (0, 0))),
        all(fw.tb[c][op][0][0] >> 16 == LOAD + 0x802 for c in (2, 3) for op in range(256)
            if fw.tb[c][op] != psdpim.EMPTY),
        int.from_bytes(psdpim.member('PMPSI.DIR/pimm.MEkbn')[:4], 'little') == LOAD,
    ]
    # descriptor 2's list is exactly the populated entries of classes 2, 3,
    # in order of start address
    r1, r2 = fw.run(RUN1), fw.run(RUN2)
    populated = {c << 8 | op for c in (2, 3) for op in range(256)
                 if fw.tb[c][op] != psdpim.EMPTY}
    got['run2_is_populated_kl1'] = set(r2) == populated
    got['run2_len'], got['run2_distinct'] = len(r2), len(set(r2))
    got['run2_descents'], got['run2_landing'] = sorted_run(fw, r2, fw.img2)
    got['run2_descents_low15_only'], got['run2_landing_low15_only'] = \
        sorted_run(fw, r2, fw.img2, low15_only=True)
    got['run1_len'] = len(r1)
    got['run1_descents'], got['run1_landing'] = sorted_run(fw, r1, fw.img1)
    got['run1_descents_low15_only'] = sorted_run(fw, r1, fw.img1, low15_only=True)[0]
    ents = fw.kl1_entries()
    got['kl1_entries'] = len({fw.entry(i) for i, _, _ in ents.values()})
    got['kl1_entries_landing'] = len({fw.entry(i) for i, a, _ in ents.values()
                                      if a < IMG2_LEN and fw.img2[a]})
    # tag immediates carried by decode entries
    bad = [n for n, t in ENTRY_TAGS.items() if ents[n][2] != TAG[t]]
    bad += ['wait_vector_%d' % n for n in range(7)
            if fw.start(0x3a8 + n)[1] != TAG['VECT%do' % n]]
    got['entry_tags_wrong'] = bad
    # tag immediates in the code the put_vector_N entries start at
    pv = []
    for n in range(7):
        a = fw.start(0x338 + n)[0]
        ok = a + 1 < IMG2_LEN and any(field(fw.img2[a + k], 'EM') >> 10 == TAG['VECT%do' % n]
                                      for k in (0, 1))
        if not ok:
            pv.append(n)
    got['put_vector_tags_wrong'] = pv
    # branch kinds
    j5 = [x & 0xffff for x in psi if x and field(x, 'JMP') == ABSOLUTE]
    got['syspsi_jmp5'] = (len(j5), sum(1 for t in j5 if t < len(psi) and psi[t]))
    j5 = [x & 0xffff for x in fw.img2 if x and field(x, 'JMP') == ABSOLUTE]
    far = [t for t in j5 if t >= IMG2_LEN]
    got['img2_jmp5'] = (len(j5), sum(1 for t in j5 if t < IMG2_LEN and fw.img2[t]),
                        len(far), sum(1 for t in far if t < len(psi) and psi[t]), len(set(far)))
    rel = []
    for j in PAGE_RELATIVE:
        hits = [(a, x) for a, x in enumerate(fw.img2) if x and field(x, 'JMP') == j]
        rel.append((j, len(hits),
                    sum(1 for a, x in hits if fw.img2[a & ~0x3ff | x & 0x3ff])))
    got['img2_page_relative'] = tuple(rel)
    # sysidat is the class 0/1 half of the decode table, packed: value and
    # tag of the second word, a zero byte, the first word's low 16 bits
    raw = psdpim.member('PMPSI.DIR/sysidat')[256:]
    recs = [raw[i:i + 8] for i in range(0, len(raw), 8)]

    def same(r, index):
        (v1, _), (v2, t2) = fw.entry(index)
        return (int.from_bytes(r[:4], 'little'), r[4], r[5],
                int.from_bytes(r[6:], 'little')) == (v2, t2, 0, v1 & 0xffff)
    differ = [i for i in range(512) if not same(recs[i], i)]
    got['sysidat'] = (len(recs), 512 - len(differ),
                      sum(1 for k in range(16) if same(recs[1024 + k], 0x1a0 + k)),
                      sum(1 for r in recs[512:1024] if any(r)))
    got['sysidat_differ_1a0_1af'] = differ == list(range(0x1a0, 0x1b0))
    return got


def check():
    got = measure()
    want = dict(PINNED, img1_differs=0, pointers=[True] * 9, run2_is_populated_kl1=True,
                entry_tags_wrong=[], put_vector_tags_wrong=[],
                sysidat_differ_1a0_1af=True)
    bad = {k: (got.get(k), v) for k, v in want.items() if got.get(k) != v}
    if bad:
        print('mekbn: FAIL %r' % bad)
        return 1
    print('mekbn: PASS (image 1 = syspsi 0..57ff on all %d non-zero words; descriptor '
          'pointers are file word + 4200; descriptor 2 lists the %d populated KL1 decode '
          'entries in start-address order with 0 descents and every start on a non-zero '
          'microinstruction (22 descents, %d landing, if the low 15 bits are taken as the '
          'address throughout); %d entry tag immediates and 7 put_vector_N routines carry '
          'the tag kbn.TAGS predicts; JMPF 5 absolute %d/%d in syspsi; JMPF 2,3,6,7 '
          'page-relative)'
          % (got['img1_equal_syspsi'], got['run2_distinct'], got['run2_landing_low15_only'],
             len(ENTRY_TAGS) + 7, got['syspsi_jmp5'][1], got['syspsi_jmp5'][0]))
    return 0


def fmt(a, x):
    s = '%04x %016x ' % (a, x)
    if not x:
        return s
    s += ' '.join('%s=%x' % (n, field(x, n)) for n, _, _ in FIELDS if field(x, n))
    j, em = field(x, 'JMP'), field(x, 'EM')
    if j == ABSOLUTE:
        s += '   -> %04x' % em
    elif j in PAGE_RELATIVE:
        s += '   -> %04x imm %02x %s' % (a & ~0x3ff | em & 0x3ff, em >> 10,
                                        kbn.TAGS.get(em >> 10, ''))
    return s


def main(argv):
    if '--check' in argv:
        return check()
    fw = Firmware()
    if '--segments' in argv:
        print('load address %04x, %d words' % (LOAD, len(fw.ws)))
        for name, a, b in (('decode table', 0, 0x800), ('descriptor 1', DESC1, 0x8ed),
                           ('image 1 (= syspsi 0..57ff)', IMG1, IMG1 + 2 * IMG1_LEN),
                           ('descriptor 2', DESC2, 0xb9aa),
                           ('image 2 (KL1 microprogram)', IMG2, IMG2 + 2 * IMG2_LEN)):
            print('  %05x-%05x  %s' % (a, b - 1, name))
        return 0
    if '--entries' in argv:
        for name, (idx, a, t) in sorted(fw.kl1_entries().items(), key=lambda kv: kv[1][1]):
            print('%04x  %03x  %-34s %s' % (a, idx, name,
                                            '' if t is None else 'imm %02x %s'
                                            % (t, kbn.TAGS.get(t, ''))))
        return 0
    if '--dis' in argv:
        i = argv.index('--dis')
        a = int(argv[i + 1], 16)
        n = int(argv[i + 2]) if len(argv) > i + 2 else 16
        for k in range(a, min(a + n, IMG2_LEN)):
            print(fmt(k, fw.img2[k]))
        return 0
    if '--tag' in argv:
        t = TAG[argv[argv.index('--tag') + 1]]
        for a, x in enumerate(fw.img2):
            if x and field(x, 'JMP') in PAGE_RELATIVE and field(x, 'EM') >> 10 == t:
                print(fmt(a, x))
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
