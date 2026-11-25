#!/usr/bin/env python3
"""Read-only dump of SIMPOS package files (.ptf): compiled ESP / KL0.

Reads INSTALL.DIR/*.ptf from docs/nonlocal/psdpim.tar.Z and
object/paragraph.ptf from docs/nonlocal/pimosobj.tar.Z (the latter has
ESP source in pimos.tar.Z src_util/paragraph: the known plaintext the
format below was settled against).  Nothing is written.

Container, 16-bit big-endian words (MEASURED on all six files; see
--check):
  0001, name; n attributes; n class names (each 0040, name);
  0000 0000; n; then n class records, each: length (32 bits, words),
  2 attributes (version, class_id), a symbol table (count, then
  length-prefixed two-byte JIS names), and a body:
    1b00, L (32 bits: cells of the class's code object), h1, h2,
    then cells h2..L-1, then a trailer of terms (method vectors,
    superclasses, constants) that fills cells 0..h2-1 (INFERENCE).
  A cell is one of
    20xx/21xx + 32 bits   KL0 instruction: class 0 (PMI) / 1 (BLT),
                          opcode = top byte, three operand bytes
    60rr sym              instruction with an atom operand (rr & 0x80:
                          put, else get; low bits the register)
    01aa sym              atom; aa != 0: a method selector of arity aa
    0000 + 32 bits        integer;  0a00 + 32 bits  float
    2400 + 32 bits        predicate head: arity << 24 | offset
    a000 op mask n size, n * (key cell, index, target)   hash table,
                          spanning mask+1 + 2n + 2 cells (table_span)
  A predicate is: atom name, integer (kind << 8 | arity), head, 0,
  then code at the head's offset.  kind 0x25 class method, 0x35
  instance method, 0x11/0x12 local (INFERENCE from the trailer vectors).
  Local call targets are cell + 2 + signed 16 bits (opcodes 60, 61, 62).

Opcode NUMBERS are not printed in any held document; the MNEMONICS are
(TM-444 PDF p6-16, 30-31; TR-236 PDF p5), so a number is tied to a
mnemonic only by a witness (psi/kl0_opcodes.tsv).  The listing prints
opcodes in hex with atoms and selectors resolved.

Usage:
    python3 asm/ptfdump.py                 packages and counts
    python3 asm/ptfdump.py PKG             classes of a package
    python3 asm/ptfdump.py PKG CLASS       predicates, sends, listing
    python3 asm/ptfdump.py PKG CLASS --pairs   integer/atom fact pairs
    python3 asm/ptfdump.py --opcodes       opcode use against sysidat
    python3 asm/ptfdump.py --check
PKG is pimfep, pimscsi, pimmcsp, pimmutil, mpsicspR or paragraph.
"""
import collections
import io
import os
import struct
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
NONLOCAL = os.path.join(HERE, '..', 'docs', 'nonlocal')
PKGS = {'pimfep': ('psdpim.tar.Z', 'INSTALL.DIR/pimfep.ptf'),
        'pimscsi': ('psdpim.tar.Z', 'INSTALL.DIR/pimscsi.ptf'),
        'pimmcsp': ('psdpim.tar.Z', 'INSTALL.DIR/pimmcsp.ptf'),
        'pimmutil': ('psdpim.tar.Z', 'INSTALL.DIR/pimmutil.ptf'),
        'mpsicspR': ('psdpim.tar.Z', 'INSTALL.DIR/mpsicspR.ptf'),
        'paragraph': ('pimosobj.tar.Z', 'object/paragraph.ptf')}
# (classes, classes whose cells tokenize to exactly L, cells stored,
#  class-0 instructions, class-1 instructions), observed 2026-11-24 with
#  table_span (2026-11-20 with the size-word span: 552 of 554 exact,
#  and fewer cells, because the drifted count reached L early).
PINNED = {'pimfep': (47, 47, 28935, 18658, 1765),
          'pimscsi': (24, 24, 12977, 8311, 1147),
          'pimmcsp': (281, 281, 156090, 103403, 9158),
          'pimmutil': (51, 51, 54615, 40312, 3223),
          'mpsicspR': (30, 30, 15616, 9629, 723),
          'paragraph': (121, 121, 93582, 56580, 14804)}
PINNED_FEP = (100, 400, 620)     # distinct names; codes of ipl and io

PUNCT = {0x21: ' ', 0x24: ',', 0x25: '.', 0x27: ':', 0x28: ';', 0x29: '?', 0x2a: '!',
         0x32: '_', 0x3f: '/', 0x40: '\\', 0x43: '|', 0x47: "'", 0x49: '"', 0x4a: '(',
         0x4b: ')', 0x4e: '[', 0x4f: ']', 0x50: '{', 0x51: '}', 0x5c: '+', 0x5d: '-',
         0x61: '=', 0x63: '<', 0x64: '>', 0x70: '$', 0x73: '%', 0x74: '#', 0x75: '&',
         0x76: '*', 0x77: '@', 0x30: '^', 0x41: '~', 0x2e: '`'}
W3 = (0x00, 0x0a, 0x20, 0x21, 0x22, 0x23, 0x24)
W2 = (0x01, 0x60)
KINDS = {0x25: 'class', 0x35: 'instance', 0x11: 'local', 0x12: 'local2'}


def member(tar, suffix):
    raw = subprocess.run(['gzip', '-dc', os.path.join(NONLOCAL, tar)],
                         stdout=subprocess.PIPE, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
        for m in tf.getmembers():
            if m.name.endswith(suffix):
                return tf.extractfile(m).read()
    raise KeyError(suffix)


def ch(w):
    a, b = w >> 8, w & 255
    if a == 0x23 and 0x21 <= b < 0x7f:
        return chr(b)
    if a == 0x21 and b in PUNCT:
        return PUNCT[b]
    return '<%04x>' % w


def parse(pkg):
    """[{id, syms, body}] for a package."""
    return parse_bytes(member(*PKGS[pkg]))


def parse_bytes(d):
    """parse() on the bytes of a .ptf file (used by psi/librarian.py)."""
    ws = list(struct.unpack('>%dH' % (len(d) // 2), d[:len(d) // 2 * 2]))
    i = 1

    def s():
        nonlocal i
        n = ws[i]
        t = ''.join(ch(x) for x in ws[i + 1:i + 1 + n])
        i += 1 + n
        return t

    def attrs(n):
        nonlocal i
        out = {}
        for _ in range(n):
            k = s()
            i += 2
            n2 = ws[i]
            if n2 and (ws[i + 1] >> 8) in (0x21, 0x23):
                out[k] = s()
            else:
                out[k] = ws[i + 1:i + 1 + n2]
                i += 1 + n2
        return out

    assert ws[0] == 1
    name = s()
    na = ws[i]
    i += 1
    pattrs = attrs(na)
    nc = ws[i]
    i += 1
    for _ in range(nc):
        assert ws[i] == 0x40
        i += 1
        s()
    assert ws[i] == 0 and ws[i + 1] == 0 and ws[i + 2] == nc
    i += 3
    out = []
    for _ in range(nc):
        ln = ws[i] << 16 | ws[i + 1]
        end = i + 2 + ln
        i += 2
        na = ws[i] << 16 | ws[i + 1]
        i += 2
        a = attrs(na)
        ns = ws[i]
        i += 1
        syms = [s() for _ in range(ns)]
        out.append(dict(id=a.get('class_id'), syms=syms, body=ws[i:end]))
        i = end
    assert len(ws) - i <= 3, 'trailing data'
    return name, pattrs, out


def table_span(mask, keys):
    """Cells a hash table occupies: mask+1 index cells, two per key, and
    two more (MEASURED 2026-11-24 on all eleven held packages, 1,455
    classes: numbered this way, 32,901 of 32,901 predicate heads sit at
    their code offset - 2 and 35,542 of 35,542 local-call targets of
    opcodes 60/61/62 land on a head; numbered by the table's size word
    + 1, as before, 3,662 heads in 91 classes were displaced).  The
    "size" word is the miss offset (psi/fepread/ptfread.py): a key not
    found goes to cell + 2 + the word, which is the cell after the table
    (word = mask+2*keys+1) in 149 of 212 tables and a later cell in the
    rest."""
    return mask + 1 + 2 * keys + 2


def cells(c):
    """(cells, words used, cell count reached, L, h1, h2).  A cell is
    (index, tag, low byte, value)."""
    b = c['body']
    assert b[0] == 0x1b00
    L, h1, h2 = b[1] << 16 | b[2], b[3], b[4]
    i, n, out = 5, h2, []

    def one(i):
        t = b[i] >> 8
        if t in W3:
            return (t, b[i] & 255, b[i + 1] << 16 | b[i + 2]), i + 3
        if t in W2:
            return (t, b[i] & 255, b[i + 1]), i + 2
        return None, i

    while n < L:
        if b[i] >> 8 == 0xa0:
            op, mask, cnt, size = b[i + 1], b[i + 2], b[i + 3], b[i + 4]
            i += 5
            ents = []
            for _ in range(cnt):
                key, i = one(i)
                ents.append((key, b[i], b[i + 1]))
                i += 2
            out.append((n, 0xa0, op, (mask, size, ents)))
            n += table_span(mask, cnt)
            continue
        cell, j = one(i)
        if cell is None:
            break
        out.append((n,) + cell)
        i = j
        n += 1
    return out, i, n, L, h1, h2


def preds(c, cs):
    """[(offset, kind, qualifier, name, arity)] in code order, for the
    regular headers (code two cells after the head)."""
    out = []
    for k in range(len(cs) - 3):
        a, f, h, z = cs[k:k + 4]
        if (a[1] == 1 and a[2] == 0 and f[1] == 0 and h[1] == 0x24 and z[1] == 0
                and h[3] & 0xffff >= h[0] + 2 and h[3] >> 24 == f[3] & 255):
            out.append((h[3] & 0xffff, (f[3] >> 8) & 255, f[3] >> 16,
                        c['syms'][a[3]], h[3] >> 24))
    return out


def sym(c, n):
    return c['syms'][n] if n < len(c['syms']) else '?sym%x' % n


def show(c, cell):
    n, t, lo, v = cell
    if t in (0x20, 0x21):
        c16 = v & 0xffff
        s16 = c16 - 0x10000 if c16 & 0x8000 else c16
        txt = '%s %02x  %02x %02x %02x' % ('pmi' if t == 0x20 else 'blt', v >> 24,
                                             (v >> 16) & 255, (v >> 8) & 255, v & 255)
        if t == 0x20 and v >> 24 in (0x60, 0x61, 0x62):
            txt += '   -> @%x' % (n + 2 + s16)
        return txt
    if t == 0x60:
        return 'pmi-atom %s r%d, %s' % ('put' if lo & 0x80 else 'get', lo & 0x7f, sym(c, v))
    if t == 0x01:
        return ('selector %s/%d' % (sym(c, v), lo)) if lo else 'atom %s' % sym(c, v)
    if t == 0x00:
        return 'integer %d (%x)' % (v, v)
    if t == 0x0a:
        return 'float %r' % struct.unpack('>f', struct.pack('>I', v))[0]
    if t == 0x24:
        return 'head arity %d offset %x' % (v >> 24, v & 0xffff)
    if t == 0xa0:
        mask, size, ents = v
        return 'hash op %04x mask %x, %d keys, %d cells' % (lo, mask, len(ents), size)
    return '?'


def trailer(c, i):
    """The terms after the code, as text items (best effort)."""
    b, out = c['body'], []
    while i < len(b):
        w = b[i]
        if w == 0x0000 and i + 2 < len(b):
            out.append('%d' % (b[i + 1] << 16 | b[i + 2]))
            i += 3
        elif w >> 8 == 0x01 and i + 1 < len(b):
            out.append(sym(c, b[i + 1]))
            i += 2
        elif w == 0x1800 and i + 1 < len(b):
            out.append('vector(%d):' % b[i + 1])
            i += 2
        elif w == 0x4b00 and i + 2 < len(b) and b[i + 1] == 0x4c00:
            out.append('code@%x' % b[i + 2])
            i += 3
        elif w == 0x0310 and i + 1 < len(b):
            n = b[i + 1]
            out.append('"%s"' % ''.join(ch(x) for x in b[i + 2:i + 2 + n]))
            i += 2 + n
        else:
            out.append('%04x' % w)
            i += 1
    return out


def sends(c, cs, lo, hi):
    return sorted({'%s/%d' % (sym(c, v), b) for n, t, b, v in cs
                   if lo <= n < hi and t == 0x01 and b})


def pairs(c, cs):
    """(integer, atom) for each adjacent 'pmi 27 r, int16' / 'get atom'
    pair of cells: the shape of a compiled table of facts t(Int, Atom)."""
    out = []
    for a, b in zip(cs, cs[1:]):
        if a[1] == 0x20 and a[3] >> 24 == 0x27 and b[1] == 0x60 and not b[2] & 0x80:
            out.append((a[3] & 0xffff, sym(c, b[3])))
    return out


def summary(pkg):
    name, _a, cl = parse(pkg)
    exact = stored = c0 = c1 = 0
    use = collections.Counter()
    for c in cl:
        cs, _i, n, L, _h1, _h2 = cells(c)
        exact += n == L
        stored += len(cs)
        for _n, t, _lo, v in cs:
            if t in (0x20, 0x21):
                use[(t & 3, v >> 24)] += 1
        c0 += sum(1 for x in cs if x[1] == 0x20)
        c1 += sum(1 for x in cs if x[1] == 0x21)
    return (len(cl), exact, stored, c0, c1), use, cl


def sysidat():
    """The KL0 decode table: 1,024 eight-byte entries after a 256-byte
    header, index class * 256 + opcode; all-zero = no instruction."""
    raw = member('psdpim.tar.Z', 'PMPSI.DIR/sysidat')[256:]
    return [raw[i:i + 8] for i in range(0, 8 * 1024, 8)]


def opcodes():
    tb = sysidat()
    total = collections.Counter()
    for pkg in PKGS:
        total.update(summary(pkg)[1])
    res = {}
    for cls in (0, 1):
        pop = [op for op in range(256) if any(tb[cls * 256 + op])]
        used = sorted(op for (c, op) in total if c == cls)
        res[cls] = (len(pop), len(used), [op for op in used if op not in pop],
                    sum(n for (c, op), n in total.items() if c == cls))
    return res, total


def check():
    bad = []
    for pkg, want in PINNED.items():
        got = summary(pkg)[0]
        if got != want:
            bad.append((pkg, got, want))
    res, _t = opcodes()
    for cls in (0, 1):
        if res[cls][2]:
            bad.append(('opcodes without a sysidat entry', cls, res[cls][2]))
    _n, _a, cl = parse('pimfep')
    c = [c for c in cl if c['id'].endswith('##fep_command_code_table')][0]
    ps = dict((a, n) for n, a in pairs(c, cells(c)[0]))
    if (len(ps), ps.get('ipl'), ps.get('io')) != PINNED_FEP:
        bad.append(('fep table', len(ps), ps.get('ipl'), ps.get('io')))
    if bad:
        print('ptfdump: FAIL %r' % bad)
        return 1
    print('ptfdump: PASS (6 packages, %d classes, %d tokenize exactly; every KL0 '
          'opcode used (%d class 0, %d class 1) has a sysidat entry; fep table %d names)'
          % (sum(v[0] for v in PINNED.values()), sum(v[1] for v in PINNED.values()),
             res[0][1], res[1][1], len(ps)))
    return 0


def main(argv):
    if '--check' in argv:
        return check()
    if '--opcodes' in argv:
        res, total = opcodes()
        for cls in (0, 1):
            pop, used, miss, n = res[cls]
            print('class %d: sysidat has %d of 256 entries; packages use %d opcodes in '
                  '%d instructions; used without an entry: %r' % (cls, pop, used, n, miss))
            print('  ' + ' '.join('%02x:%d' % (op, k) for (c, op), k in
                                  sorted(total.items(), key=lambda x: -x[1]) if c == cls))
        return 0
    args = [a for a in argv if not a.startswith('--')]
    if not args:
        for pkg in PKGS:
            (n, exact, stored, c0, c1), _u, cl = summary(pkg)
            print('%-10s %3d classes (%3d tokenize exactly)  %6d cells stored  %6d PMI '
                  '%5d BLT instructions  %5d symbols'
                  % (pkg, n, exact, stored, c0, c1, sum(len(c['syms']) for c in cl)))
        return 0
    if args[0] not in PKGS:
        print(__doc__)
        return 2
    _name, _a, cl = parse(args[0])
    if len(args) == 1:
        for c in cl:
            cs, _i, n, L, h1, h2 = cells(c)
            ps = preds(c, cs)
            k = collections.Counter(KINDS.get(p[1], 'other') for p in ps)
            print('%-34s L %5d h %3d %3d  %3d syms  preds: %2d class %3d instance '
                  '%3d local %2d other' % (c['id'].split('##')[1], L, h1, h2, len(c['syms']),
                                           k['class'], k['instance'],
                                           k['local'] + k['local2'], k['other']))
        return 0
    c = [c for c in cl if c['id'].split('##')[1] == args[1]]
    if not c:
        print('no class %s' % args[1])
        return 1
    c = c[0]
    cs, i, n, L, h1, h2 = cells(c)
    if '--pairs' in argv:
        for num, atom in pairs(c, cs):
            print('%5d  %s' % (num, atom))
        return 0
    ps = preds(c, cs)
    print('class %s: L %d, h1 %d, h2 %d, %d symbols' % (c['id'], L, h1, h2, len(c['syms'])))
    print('trailer: ' + ' '.join(trailer(c, i)))
    for k, (off, kind, q, name, ar) in enumerate(ps):
        hi = ps[k + 1][0] - 4 if k + 1 < len(ps) else L
        print('%-8s %x %s/%d  @%x  %d cells  sends: %s'
              % (KINDS.get(kind, 'kind%02x' % kind), q, name, ar, off, hi - off,
                 ' '.join(sends(c, cs, off, hi))))
    if '--list' in argv:
        for cell in cs:
            print('%5x  %s' % (cell[0], show(c, cell)))
            if cell[1] == 0xa0:
                for key, idx, tgt in cell[3][2]:
                    print('         %s -> %x' % (show(c, (0,) + key), tgt))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
