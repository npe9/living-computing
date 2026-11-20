#!/usr/bin/env python3
"""Disassemble the PIMOS IPL image by name.

Joins the cells of pimm_ipl.kbn (asm/kbn.py) with the atom table in
pimm_ipl.sym (written by kbnatom.kl1: one "number name" line per atom,
two-byte JIS text) and the operand types of inst_tab.kl1.

What is read from the image, and how:
  module name     cells 3 and 4 of a module: {atom, module}, {atom, package}
  predicate       {atom, name}, {integer, 0}, {predicate head,
                  arity << 24 | offset of this cell in the module},
                  {integer, length << 16}, then `length` cells of code
  atom operands   the low 24 bits of an atom instruction are an atom number
  labels          16 signed bits, target = here + 2 + offset, in cells

Usage:
    python3 asm/kbndis.py                 list modules
    python3 asm/kbndis.py MODULE          list its predicates
    python3 asm/kbndis.py MODULE PRED/N   disassemble one predicate
    python3 asm/kbndis.py --check
"""
import hashlib
import io
import os
import re
import subprocess
import sys
import tarfile
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import census  # noqa: E402
import kbn  # noqa: E402
from unlsav import load_opcodes  # noqa: E402

LABEL_OPS = ('try_me_else', 'otherwise', 'suspend', 'jump', 'execute',
             'enqueue_goal', 'enqueue_goal_with_priority',
             'enqueue_goal_to_processor')

# (module, predicates) in image order, observed 2026-11-20.
PINNED = [
    ('ipl_file_decoder', 41), ('exception_table', 14), ('scsi_fep_file', 18),
    ('scsi_fep_general', 3), ('scsi_fep_module', 38), ('scsi_fep_util', 7),
    ('ipl_scsi', 14), ('ipl', 34), ('jis_to_ascii', 3),
    ('ipl_link_table', 9), ('ipl_loader', 32), ('ipl_module', 29),
    ('ipl_pool', 27), ('scsi_builtin', 2), ('scsi_common', 13), ('scsi', 9),
    ('scsi_processor', 3), ('shoen', 22), ('builtin_utility', 8), ('top', 23),
]
PINNED_START = ('ipl', 'boot/0')
PINNED_ATOMS = 486
# Predicates with their arities and code lengths, spot-pinned, and a
# digest of every (module, predicate/arity, length) in the image.
PINNED_PREDS = [('jis_to_ascii', 'convert_loop/4', 27),
                ('jis_to_ascii', 'convert_element/2', 241),
                ('scsi', 'command_executer/2', 24),
                ('ipl', 'ipl_monitor/3', 142)]
PINNED_DIGEST = '865dfa48ec1130ab'


def member(suffix):
    raw = subprocess.run(['gzip', '-dc', kbn.TAR], stdout=subprocess.PIPE,
                         check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
        for m in tf.getmembers():
            if m.name.endswith(suffix):
                return tf.extractfile(m).read()
    raise SystemExit('no %s in %s' % (suffix, kbn.TAR))


def jis(raw):
    out = []
    for i in range(0, len(raw) - 1, 2):
        w = raw[i:i + 2]
        if w == b'\x00\x0a':
            out.append('\n')
        else:
            out.append((b'\x1b$B' + w).decode('iso2022_jp', 'replace'))
    return unicodedata.normalize('NFKC', ''.join(out))


def atoms():
    sym = {}
    for line in jis(member('pimm_ipl.sym')).splitlines()[1:]:
        p = line.split()
        if p and re.fullmatch(r'[0-9A-F]+', p[0]):
            sym[int(p[0], 16)] = p[1] if len(p) > 1 else ''
    return sym


class Image:
    def __init__(self):
        self.got, self.cells, mods, _t, _u, self.key = kbn.decode(kbn.image())
        self.sym = atoms()
        self.load = self.got['load']
        self.typ = {}
        for op, ents in load_opcodes().items():
            for name, t, tag in ents:
                self.typ.setdefault((tag, op), t)
        self.mods = []
        self.bad = 0
        for a, ln, _gc in mods:
            preds = []
            for i in range(a + 2, a + 2 + ln):
                c = self.cells
                if c[i][0] == 0x24 and c[i - 2][0] == 0x02 and c[i - 1][0] == 0x00:
                    # head value = its offset from the module's cdesc
                    # cell; next word = code length << 16
                    self.bad += c[i][1] & 0xffffff != i - (a + 1)
                    self.bad += c[i + 1][0] != 0 or c[i + 1][1] & 0xffff != 0
                    preds.append(('%s/%d' % (self.atom(c[i - 2][1]), c[i][1] >> 24),
                                  c[i + 1][1] >> 16, i + 2))
            self.mods.append(dict(addr=a, length=ln, preds=preds,
                                  name=self.atom(self.cells[a + 3][1]),
                                  package=self.atom(self.cells[a + 4][1])))

    def atom(self, v):
        return self.sym.get(v & 0xffffff, '#%x' % (v & 0xffffff))

    def predkey(self, v):
        """A predicate key, arity << 24 | (atom number + arity)
        (kbnatom.kl1 pred_atom), as 'name/arity'."""
        ar = v >> 24
        return '%s/%d' % (self.atom((v & 0xffffff) - ar), ar)

    def external(self, a):
        """The target of execute_external / enqueue_goal_external at a.
        The operand is a location, target - (here + 2)
        (klb_opr.kl1 cal_location_address), of a four-cell entry in
        the module's GC area: {integer}, {REFx to the module's REFo cell},
        {atom, predicate key}, {atom, module name}.
        Returns (module name, 'pred/arity', code address or None)."""
        c16 = self.cells[a][1] & 0xffff
        e = a + 2 + (c16 - 0x10000 if c16 & 0x8000 else c16)
        c = self.cells
        if not (c[e][0] == 0x00 and c[e + 1][0] == 0x07
                and c[e + 2][0] == 0x02 and c[e + 3][0] == 0x02):
            return None
        mod, pred = self.atom(c[e + 3][1]), self.predkey(c[e + 2][1])
        head = c[c[e + 1][1] - self.load][1] - self.load   # via the table
        for m in self.mods:
            if m['addr'] == head:
                if m['name'] != mod:
                    return None
                for n, _ln, addr in m['preds']:
                    if n == pred:
                        return mod, pred, addr
        return mod, pred, None

    def where(self, addr):
        for m in self.mods:
            if m['addr'] <= addr < m['addr'] + 2 + m['length']:
                best = None
                for p in m['preds']:
                    if p[2] <= addr:
                        best = p
                return m, best
        return None, None

    def dis(self, a):
        t, v = self.cells[a]
        op = v >> 24
        if t in (0x22, 0x23):
            k = (t, op)
            if k not in self.key:
                b = census.atom_base(op)
                return '%s %d, %s' % (self.key[(0x23, b)][0], op - b, self.atom(v))
            name = self.key[k][0]
            ty = self.typ.get(k, '')
            x, y, z, c16 = (v >> 16) & 255, (v >> 8) & 255, v & 255, v & 0xffff
            if ty.startswith('atom'):
                return '%s %s' % (name, self.atom(v))
            if name in ('execute_external', 'enqueue_goal_external'):
                ext = self.external(a)
                if ext:
                    return '%s %d, %s:%s%s' % (name, x, ext[0], ext[1],
                                               '' if ext[2] else '   ; NOT IN IMAGE')
            if name in LABEL_OPS:
                tgt = a + 2 + (c16 - 0x10000 if c16 & 0x8000 else c16)
                m, p = self.where(tgt)
                lab = '@%d' % tgt
                if p and p[2] == tgt:
                    lab = p[0]
                return '%s %d, %s' % (name, x, lab)
            return '%s %d,%d,%d' % (name, x, y, z) + ('   ; %s' % ty if ty else '')
        if t == 0x24:
            return '; predicate head %08x' % v
        if t == 0x02:
            return 'atom %s' % (self.predkey(v) if v >> 24 else self.atom(v))
        if t == 0x00:
            return 'integer %d' % (v - (1 << 32) if v >> 31 else v)
        return '%s %08x' % (kbn.TAGS.get(t, 'tag %02x' % t), v)


def main(argv):
    im = Image()
    if '--check' in argv:
        got = [(m['name'], len(m['preds'])) for m in im.mods]
        m, p = im.where(im.got['start'] - im.load)
        start = (m['name'], p[0]) if m and p else None
        named = sum(len(m['preds']) for m in im.mods)
        allp = [(m['name'], n, ln) for m in im.mods for n, ln, _a in m['preds']]
        digest = hashlib.sha256(repr(allp).encode()).hexdigest()[:16]
        ext = [im.external(a) for a, (t, v) in enumerate(im.cells)
               if t == 0x23 and v >> 24 in (0x62, 0x66)]
        # the image is closed: every external call lands on a predicate in it
        ok = (got == PINNED and start == PINNED_START
              and len(ext) == 92 and all(e and e[2] for e in ext)
              and all(x in allp for x in PINNED_PREDS)
              and digest == PINNED_DIGEST
              and named == im.got['pred_heads'] and len(im.sym) == PINNED_ATOMS
              and all(m['package'] == 'pimos' for m in im.mods)
              and im.bad == 0)
        if not ok:
            print('kbndis: FAIL\n  modules %r\n  start %r  named %d of %d  atoms %d  bad %d  digest %s'
                  % (got, start, named, im.got['pred_heads'], len(im.sym), im.bad, digest))
            return 1
        print('kbndis: PASS (20 modules named, %d of %d predicates named, '
              'start is %s:%s)' % ((named, named) + start))
        return 0
    args = [a for a in argv if not a.startswith('--')]
    if not args:
        for m in im.mods:
            print('@%5d  %s::%-18s %5d cells  %3d predicates'
                  % (m['addr'], m['package'], m['name'], m['length'], len(m['preds'])))
        return 0
    m = [m for m in im.mods if m['name'] == args[0]]
    if not m:
        print('no module %s' % args[0])
        return 1
    m = m[0]
    if len(args) == 1:
        for name, ln, addr in m['preds']:
            print('@%5d  %4d cells  %s' % (addr, ln, name))
        return 0
    ps = m['preds']
    for name, ln, addr in ps:
        if name == args[1]:
            for a in range(addr, addr + ln):
                print('%5d  %02x:%08x  %s' % (a, im.cells[a][0], im.cells[a][1], im.dis(a)))
            return 0
    print('no predicate %s in %s' % (args[1], args[0]))
    return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
