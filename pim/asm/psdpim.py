#!/usr/bin/env python3
"""Read the Pseudo PIM/m firmware archive (docs/nonlocal/psdpim.tar.Z).

Two things are read here, and nothing else in the archive is decoded:

1. The instruction decode table at the head of PMPSI.DIR/pimm.MEkbn.
   The file is in the IPL image's container (asm/kbn.py: a 256-byte
   header, then 256-byte blocks of 51 five-byte words, the 32-bit value
   low byte first, then a tag byte).  Its first 2048 words are 1024
   two-word entries indexed by

       (low two bits of the instruction cell's tag) * 256 + opcode byte

   so class 0 is PMI (tag 20), 1 BLT (21), 2 GMI (22), 3 KLB (23).  An
   entry of {00002000:00, 00000000:00} means "no such instruction".
   This reading is checked, not assumed: see --check.

2. The text of the console packages (INSTALL.DIR/*.ptf): two-byte JIS
   characters, row 23 being the ASCII letters and digits.  The record
   inspectors' menus name the fields of the shoen record, the foster
   parent record in order; the multiple suspension record's menu has
   four unnumbered items.

Everything here describes the Pseudo PIM/m (the PIM/m KL1 firmware on a
PSI-III workstation, 1991-94), not a PIM/m processing element.

Usage:
    python3 asm/psdpim.py --check          the pinned agreement checks
    python3 asm/psdpim.py --table [CLASS]  print a class of the table
    python3 asm/psdpim.py --text MEMBER    print a package's text
"""
import io
import os
import re
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
TAR = os.path.join(HERE, '..', 'docs', 'nonlocal', 'psdpim.tar.Z')
ENCODING = os.path.join(HERE, '..', 'docs', 'kl1_encoding.md')

EMPTY = ((0x00002000, 0x00), (0x00000000, 0x00))
CLASSES = {0: 0x20, 1: 0x21, 2: 0x22, 3: 0x23}

# Opcode families the encoding table gives as ranges: the register (or
# size) is in the opcode byte.
FAMILIES = {
    0x23: [('set_atom', 0x00, 0x0f), ('put_vector_N', 0x38, 0x3e),
           ('put_atom', 0x40, 0x5f), ('wait_atom', 0x80, 0x9f),
           ('wait_vector_N', 0xa8, 0xae), ('get_atom', 0xc0, 0xdf)],
    0x22: [],
}
# Families whose members all share one entry (the register is an
# operand); the vector families have an entry per size.
SHARED = ('set_atom', 'put_atom', 'wait_atom', 'get_atom')

PINNED = dict(
    words=100864,
    klb_named=125, klb_family=246, klb_empty=11,
    klb_named_but_empty=['wait_different_value'],
    gmi_named=80, gmi_empty=177, gmi_named_but_empty=['scsi_transfer'],
    image_cells=13156, image_empty=[],
    sav_instructions=726053, sav_empty=['22/dc scsi_transfer x1'],
    shoen_fields=24, fp_fields=14,
)


def member(suffix):
    raw = subprocess.run(['gzip', '-dc', TAR], stdout=subprocess.PIPE, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
        for m in tf.getmembers():
            if m.name.endswith(suffix):
                return tf.extractfile(m).read()
    raise KeyError(suffix)


def words(raw):
    """The (value, tag) words of a file in the .kbn container."""
    size = int.from_bytes(raw[4:6], 'little') | int.from_bytes(raw[6:8], 'little') << 16
    out = []
    body = raw[256:]
    for b in range(0, len(body), 256):
        blk = body[b:b + 256]
        for i in range(51):
            w = blk[i * 5:i * 5 + 5]
            if len(w) == 5:
                out.append((int.from_bytes(w[:4], 'little'), w[4]))
    return out[:size]


def table(ws=None):
    """entry[class][opcode] = ((value, tag), (value, tag))."""
    ws = ws or words(member('PMPSI.DIR/pimm.MEkbn'))
    return [[(ws[2 * (c * 256 + op)], ws[2 * (c * 256 + op) + 1]) for op in range(256)]
            for c in range(4)]


def names():
    """{tag: {opcode: name}} from docs/kl1_encoding.md's main tables."""
    text = open(ENCODING).read()
    out = {}
    pat = r'\| `([^`]+)` \| `16#"([0-9a-fA-F]+)"` \| `16#"([0-9a-fA-F]+)"` \| `([^`]*)` \|'
    for m in re.finditer(pat, text):
        out.setdefault(int(m.group(2), 16), {})[int(m.group(3), 16)] = m.group(1)
    return out


PUNCT = {0x21: ' ', 0x24: ',', 0x25: '.', 0x27: ':', 0x28: ';', 0x29: '?', 0x2a: '!',
         0x32: '_', 0x3f: '/', 0x40: '\\', 0x43: '|', 0x47: "'", 0x49: '"', 0x4a: '(',
         0x4b: ')', 0x4e: '[', 0x4f: ']', 0x50: '{', 0x51: '}', 0x5c: '+', 0x5d: '-',
         0x61: '=', 0x63: '<', 0x64: '>', 0x70: '$', 0x73: '%', 0x74: '#', 0x75: '&',
         0x76: '*', 0x77: '@', 0x30: '^', 0x41: '~', 0x2e: '`'}


def text(raw, shortest=4):
    """Runs of two-byte JIS letters, digits and punctuation, as ASCII."""
    out, cur, i = [], '', 0
    while i < len(raw) - 1:
        a, b = raw[i], raw[i + 1]
        if a == 0x23 and 0x21 <= b < 0x7f:
            cur += chr(b)
            i += 2
        elif a == 0x21 and b in PUNCT:
            cur += PUNCT[b]
            i += 2
        else:
            if len(cur) >= shortest:
                out.append(cur)
            cur = ''
            i += 1
    if len(cur) >= shortest:
        out.append(cur)
    return out


def menu(lines, first):
    """The numbered lines 'N : Label :' starting at the line `first`."""
    i = lines.index(first)
    out = []
    while i < len(lines):
        m = re.match(r'([0-9A-F]+) +: ?(.*?) *:? *$', lines[i])
        if not m or int(m.group(1), 16) != len(out):
            break
        out.append(m.group(2).rstrip(' :').strip())
        i += 1
    return out


def records():
    """Field lists from the console's Shoen Tree inspector."""
    lines = text(member('INSTALL.DIR/pimmcsp.ptf'))
    fp = menu(lines, '0  : Shoen ID             : ')
    rest = lines[lines.index('0  : Shoen ID             : ') + 1:]
    shoen = menu(rest, '0  : Shoen ID             : ')
    i = lines.index('Multiple Suspend Record')
    msusp = [s.rstrip(' >') for s in lines[i - 4:i]]
    return dict(foster_parent=fp, shoen=shoen, multiple_suspend=msusp)


def measure():
    ws = words(member('PMPSI.DIR/pimm.MEkbn'))
    tb = table(ws)
    nm = names()
    got = dict(words=len(ws))
    for cls, tag, key in ((3, 0x23, 'klb'), (2, 0x22, 'gmi')):
        named = nm[tag]
        fam = {}
        for name, lo, hi in FAMILIES[tag]:
            for op in range(lo, hi + 1):
                fam[op] = name
        known = set(named) | set(fam)
        empty = [op for op in range(256) if tb[cls][op] == EMPTY]
        got[key + '_named'] = len(named)
        got[key + '_empty'] = len(empty)
        got[key + '_named_but_empty'] = sorted(named[op] for op in empty if op in named)
        if key == 'klb':
            got['klb_family'] = len(known)
        # the two-way agreement: nothing unknown has an entry, and no
        # family member is empty
        got[key + '_unknown_with_entry'] = [hex(op) for op in range(256)
                                            if op not in known and tb[cls][op] != EMPTY]
        got[key + '_family_empty'] = [hex(op) for op in empty if op in fam]
        for name, lo, hi in FAMILIES[tag]:
            same = len({tb[cls][op] for op in range(lo, hi + 1)}) == 1
            if same != (name in SHARED):
                got.setdefault('family_shape', []).append(name)
    # every instruction cell of the IPL image has an entry
    sys.path.insert(0, HERE)
    import kbndis
    cells = kbndis.Image().cells
    used = {}
    for t, v in cells:
        if t in (0x22, 0x23):
            used[(t & 3, v >> 24)] = used.get((t & 3, v >> 24), 0) + 1
    got['image_cells'] = sum(used.values())
    got['image_empty'] = sorted('%d:%02x x%d' % (c, op, n) for (c, op), n in used.items()
                                if tb[c][op] == EMPTY)
    # ... and every instruction of the .sav object set, but one
    import census
    key, used = census.census(None)[:2]
    got['sav_instructions'] = sum(used.values())
    got['sav_empty'] = sorted('%02x/%02x %s x%d' % (t, op, key[(t, op)][0], n)
                              for (t, op), n in used.items() if tb[t & 3][op] == EMPTY)
    r = records()
    got['shoen_fields'] = len(r['shoen'])
    got['fp_fields'] = len(r['foster_parent'])
    got['msusp'] = r['multiple_suspend']
    return got


def check():
    got = measure()
    want = dict(PINNED, klb_unknown_with_entry=[], klb_family_empty=[],
                gmi_unknown_with_entry=[], gmi_family_empty=[],
                msusp=['prev', 'next', 'goal', 'rival'])
    bad = {k: (got.get(k), v) for k, v in want.items() if got.get(k) != v}
    if 'family_shape' in got:
        bad['family_shape'] = got['family_shape']
    if bad:
        print('psdpim: FAIL %r' % bad)
        return 1
    print('psdpim: PASS (pimm.MEkbn begins with a 1024-entry decode table: of %d KLB '
          'and %d GMI opcodes in kl1_encoding.md all have an entry but %s and %s, no '
          'opcode outside the table and its families has one, the atom families share '
          'an entry and the vector families do not; %d instruction cells of the IPL '
          'image all decode, and the %d instructions of the .sav object set but one '
          'scsi_transfer; console menus give %d shoen and %d foster-parent fields)'
          % (got['klb_named'], got['gmi_named'], got['klb_named_but_empty'][0],
             got['gmi_named_but_empty'][0], got['image_cells'], got['sav_instructions'],
             got['shoen_fields'],
             got['fp_fields']))
    return 0


def main(argv):
    if '--check' in argv:
        return check()
    if '--table' in argv:
        i = argv.index('--table')
        cls = int(argv[i + 1]) if len(argv) > i + 1 else 3
        tb, nm = table(), names().get(CLASSES[cls], {})
        for op in range(256):
            (v0, t0), (v1, t1) = tb[cls][op]
            print('%02x %-30s %08x:%02x %08x:%02x' % (op, nm.get(op, ''), v0, t0, v1, t1))
        return 0
    if '--text' in argv:
        for s in text(member(argv[argv.index('--text') + 1])):
            print(s)
        return 0
    if '--records' in argv:
        for k, v in records().items():
            print(k)
            for i, f in enumerate(v):
                print('  %2X  %s' % (i, f))
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
