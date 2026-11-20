#!/usr/bin/env python3
"""Decode the PIMOS IPL heap image (pimm_ipl.kbn).

The format is defined by pimos/src/library/kbn/kbnfile.kl1 (the file
writer), kbn.kl1 (module layout) and kbnheap.kl1 (tags):

  header  128 16-bit words, little-endian on disk (kbn_file_header then
          swap_bytes): words 0-1 LoadAddress, 2-3 CodeSize (cells),
          4-5 StartAddress, 6-7 ModuleAddress, 126-127 Version; each a
          32-bit value as low word, high word.
  body    256-byte blocks of 51 cells and one pad byte; a cell is five
          bytes: the 32-bit value low byte first, then the 8-bit tag
          (kbn_file_heap).

Addresses are in cells.  A module is {module-tag, self+1}, then
{cdesc, 16#06 << 24 | Length}, {integer, GCSize}, the GC area, the
entry table and the code (kbn.kl1 encode_module); its structured
constants follow it.

Usage:
    python3 asm/kbn.py [--check] [FILE.kbn]
"""
import collections
import io
import os
import struct
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import census  # noqa: E402

TAR = os.path.join(HERE, '..', 'docs', 'nonlocal', 'pimosobj.tar.Z')

# The machine's tags, from debugger/inspector/tagtbl.kl1 get_tag_name/2
# (59 entries, transcribed whole).  kbnheap.kl1 tag/2 agrees on every tag
# it names and adds 3F (ex_float).  The o/x suffix is not explained in
# the source; it is the low bit, and every pointer the image builder
# writes has it set.
TAGS = {
    0x00: 'INTo', 0x01: 'INTx', 0x02: 'ATOMo', 0x03: 'ATOMx',
    0x04: 'LISTo', 0x05: 'LISTx', 0x06: 'REFo', 0x07: 'REFx',
    0x08: 'UNDF', 0x0a: 'HOOKo', 0x0b: 'HOOKx', 0x0c: 'MHOOK',
    0x0d: 'VDESC', 0x0e: 'STRGo', 0x0f: 'STRGx', 0x10: 'VECT0o',
    0x11: 'VECT0x', 0x12: 'VECT1o', 0x13: 'VECT1x', 0x14: 'VECT2o',
    0x15: 'VECT2x', 0x16: 'VECT3o', 0x17: 'VECT3x', 0x18: 'VECT4o',
    0x19: 'VECT4x', 0x1a: 'VECT5o', 0x1b: 'VECT5x', 0x1c: 'VECT6o',
    0x1d: 'VECT6x', 0x1e: 'VECTo', 0x1f: 'VECTx', 0x20: 'PMI',
    0x21: 'BLT', 0x22: 'GMI', 0x23: 'KLB', 0x24: 'PREDH',
    0x25: 'CDESC', 0x26: 'COD', 0x27: 'MOD', 0x28: 'MGHOK',
    0x29: 'EXMRF', 0x2a: 'EUNDFo', 0x2b: 'EUNDFx', 0x2c: 'EHOOKo',
    0x2d: 'EHOOKx', 0x2e: 'EMHOKo', 0x2f: 'EMHOKx', 0x30: 'FLTo',
    0x31: 'FLTx', 0x32: 'EXREFo', 0x33: 'EXREFx', 0x34: 'EXVALo',
    0x35: 'EXVALx', 0x36: 'RHOOKo', 0x37: 'RHOOKx', 0x38: 'SHREC',
    0x39: 'FPREC', 0x3a: 'FPRECt', 0x3b: 'DREF',
    0x3f: 'ex_float (kbnheap.kl1)',
}

CELLS_PER_BLOCK = 51

PINNED = dict(load=0xe0000000, size=18300, start=0xe0001e81,
              module=0xe0001e25, version=0x01973460, modules=20,
              in_modules=17010, constants=1270, table=20,
              instructions=13156, pred_heads=349, unknown_ops=0,
              distinct_ops=143, bad=0, tme=492, tme_to_clause=475)


def image(path=None):
    if path:
        return open(path, 'rb').read()
    raw = subprocess.run(['gzip', '-dc', TAR], stdout=subprocess.PIPE,
                         check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
        for m in tf.getmembers():
            if m.name.endswith('pimm_ipl.kbn'):
                return tf.extractfile(m).read()
    raise SystemExit('no pimm_ipl.kbn in %s' % TAR)


def decode(d):
    h = struct.unpack('<128H', d[:256])
    f = lambda i: h[i] | (h[i + 1] << 16)
    hdr = dict(load=f(0), size=f(2), start=f(4), module=f(6), version=f(126))
    bad = sum(1 for i in range(8, 126) if h[i])        # header filler
    cells = []
    for b in range(256, len(d), 256):
        blk = d[b:b + 256]
        for i in range(CELLS_PER_BLOCK):
            v, t = struct.unpack('<IB', blk[5 * i:5 * i + 5])
            cells.append((t, v))
        bad += blk[255] != 0                           # pad byte
    load, size = hdr['load'], hdr['size']
    bad += sum(1 for c in cells[size:] if c != (0, 0))  # past CodeSize
    cells = cells[:size]

    # Modules: a module-tag cell pointing at the next cell, a cdesc.
    mods = []
    for a, (t, v) in enumerate(cells):
        if t == 0x27 and v == load + a + 1 and cells[a + 1][0] == 0x25:
            desc = cells[a + 1][1]
            bad += (desc >> 24) != 0x06
            mods.append((a, desc & 0xffffff, cells[a + 2][1]))
    inside = [False] * size
    for a, ln, _gc in mods:
        for i in range(a, a + 2 + ln):
            bad += inside[i]                           # overlap
            inside[i] = True

    # The last len(mods) cells are REFo (06), one per module, each
    # pointing at a module's MOD cell; the REFx (07) cells inside modules
    # point at these.  An external module reference is thus a two-step
    # reference chain, which lets a module be replaced by changing one cell.
    tbl = size - len(mods)
    heads = set(load + a for a, _, _ in mods)
    bad += set(v for t, v in cells[tbl:]) != heads
    bad += any(t != 0x06 for t, v in cells[tbl:])
    key = census.opcode_table()
    used = collections.Counter()
    tags = collections.Counter()
    n = collections.Counter()
    for a, (t, v) in enumerate(cells):
        tags[t] += 1
        bad += t not in TAGS
        if a >= tbl:
            n['table'] += 1
        elif inside[a]:
            n['in_modules'] += 1
        else:
            n['constants'] += 1
        if t in (0x22, 0x23):
            bad += not inside[a]
            n['instructions'] += 1
            op = v >> 24
            if t == 0x23 and (op & 0x1f if op >= 0x40 else op & 0x0f) \
                    and (t, op) not in key:
                # set/put/wait/get_atom with the register in the opcode
                # byte and a 24-bit atom number (kbn.kl1 encode_code_1)
                try:
                    op = census.atom_base(op)
                except ValueError:
                    pass
            if (t, op) in key:
                used[(t, op)] += 1
            else:
                n['unknown_ops'] += 1
        elif t == 0x24:
            n['pred_heads'] += 1
        elif t == 0x07:                                # into the table
            bad += not (inside[a] and tbl <= v - load < size)
        elif t == 0x06:
            bad += a < tbl
    # The header's two addresses: ModuleAddress is a module's cdesc
    # cell; StartAddress is an instruction in that module, directly
    # after a predicate head and one more word.
    ma, sa = hdr['module'] - load, hdr['start'] - load
    home = [m for m in mods if m[0] + 1 == ma]
    bad += len(home) != 1
    if home:
        bad += not (ma < sa < ma + home[0][1])
    bad += cells[sa][0] != 0x23 or cells[sa - 2][0] != 0x24
    # Label units: a try_me_else (23/68) label is 16 signed bits and the
    # assembler computes target - (here + 2).  If the unit is cells, the
    # target is the next clause: try_me_else, suspend or otherwise.
    for a, (t, v) in enumerate(cells):
        if t == 0x23 and v >> 24 == 0x68:
            off = v & 0xffff
            tgt = a + 2 + (off - 0x10000 if off & 0x8000 else off)
            n['tme'] += 1
            if 0 <= tgt < size and cells[tgt][0] == 0x23 \
                    and cells[tgt][1] >> 24 in (0x68, 0x69, 0x6a):
                n['tme_to_clause'] += 1
    got = dict(hdr, tme=n['tme'], tme_to_clause=n['tme_to_clause'],
               modules=len(mods), in_modules=n['in_modules'],
               constants=n['constants'], table=n['table'],
               instructions=n['instructions'], pred_heads=n['pred_heads'],
               unknown_ops=n['unknown_ops'], distinct_ops=len(used), bad=bad)
    return got, cells, mods, tags, used, key


def main(argv):
    paths = [a for a in argv if not a.startswith('--')]
    got, cells, mods, tags, used, key = decode(image(paths[0] if paths else None))
    if '--check' in argv:
        if got != PINNED:
            print('kbn: FAIL\n  got    %r\n  pinned %r' % (got, PINNED))
            return 1
        print('kbn: PASS (%(size)d cells, %(modules)d modules, '
              '%(instructions)d instructions, every cell placed)' % got)
        return 0
    print('load %(load)08x  size %(size)d cells  start %(start)08x  '
          'module %(module)08x  version %(version)08x' % got)
    print(got)
    for a, ln, gc in mods:
        print('  module @%5d  length %5d  gc %3d' % (a, ln, gc))
    for t, c in sorted(tags.items(), key=lambda x: -x[1]):
        print('  tag %02x %-24s %6d' % (t, TAGS.get(t, '?'), c))
    arms = census.model_opcodes()
    have = sum(c for (t, op), c in used.items() if t == 0x23 and op in arms)
    print('model arms cover %d of %d opcodes, %d of %d instructions'
          % (sum(1 for (t, op) in used if t == 0x23 and op in arms),
             len(used), have, sum(used.values())))
    for (t, op), c in used.most_common():
        print('  %6d  %02x/%02x %s%s' % (c, t, op,
              '  ' if (t == 0x23 and op in arms) else '- ', key[(t, op)][0]))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
