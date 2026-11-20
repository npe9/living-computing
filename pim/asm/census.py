#!/usr/bin/env python3
"""Census of the PIMOS 3.6 object set: every .sav decodes, and what it uses.

Reads the object files from a directory, or (default) straight out of
docs/nonlocal/pimosobj.tar.Z.  For every module of every .sav it walks
the code area with unlsav.parse_module and classifies each three-word
item [0x00TT, V1, V2] by its word tag TT:

  0x22, 0x23  an instruction; the opcode is the top byte of the value
              (inst_tab.kl1 gives a Tag and an Op per mnemonic)
  0x24        a predicate head word, (Arity<<24) | offset
              (assemble.kl1 make_pred_head)
  0x30        a floating-point constant (IEEE single in the value, e.g.
              0xbf800000); the second word of a two-word constant
              instruction

Instructions are looked up by (tag, opcode) in docs/kl1_encoding.md
plus the thirteen quick forms that are commented out in the 1992
inst_tab.kl1 but present in the 1994 binaries: put_vector_0..6
(0x38-0x3e) and wait_vector_1..6 (0xa9-0xae), inst_tab.kl1 lines 65-71
and 157-162.

  census.py            print the census
  census.py --check    exit 1 unless the pinned totals below hold
  census.py --model    also report which opcodes bsv/PimKL1B.bsv has an
                       arm for (a text match on the source, so a
                       stand-in arm counts)
"""
import collections
import io
import os
import re
import struct
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from unlsav import Reader, parse_module, load_opcodes  # noqa: E402

TARBALL = os.path.join(HERE, '..', 'docs', 'nonlocal', 'pimosobj.tar.Z')
MODEL = os.path.join(HERE, '..', 'bsv', 'PimKL1B.bsv')

# Observed 2026-11-19 on pimosobj.tar.Z (sha256 2c9a8f69...).
PINNED = dict(files=20, modules=502, instructions=726053, checksums=20,
              pred_heads=12344, floats=103, unknown=0, distinct=197)


def sav_files(src):
    """Yield (name, bytes) for each .sav, from a directory or the tarball."""
    if src and os.path.isdir(src):
        for n in sorted(os.listdir(src)):
            if n.endswith('.sav'):
                yield n, open(os.path.join(src, n), 'rb').read()
        return
    # .Z is LZW compress(1) data; gzip -dc reads it, tarfile does not.
    raw = subprocess.run(['gzip', '-dc', src or TARBALL], check=True,
                         stdout=subprocess.PIPE).stdout
    with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
        for m in sorted(tf.getmembers(), key=lambda m: m.name):
            if m.name.endswith('.sav'):
                yield os.path.basename(m.name), tf.extractfile(m).read()


def opcode_table():
    key = {}
    for op, ents in load_opcodes().items():
        for name, typ, tag in ents:
            key.setdefault((tag, op), []).append(name)
    for i in range(7):
        key[(0x23, 0x38 + i)] = ['put_vector_%d' % i]
    for i in range(1, 7):
        key[(0x23, 0xa8 + i)] = ['wait_vector_%d' % i]
    return key


def atom_base(op):
    """Base opcode of an atom instruction: write_atom (23) and read_atom
    (b3) stand alone; the others carry a register in the low bits."""
    if op in (0x23, 0xb3):
        return op
    for base, span in ((0x00, 0x10), (0x40, 0x20), (0x80, 0x20), (0xc0, 0x20)):
        if base <= op < base + span:
            return base
    raise ValueError('atom-form opcode %02x' % op)


def model_opcodes():
    src = open(MODEL).read()
    arms = set(int(m.group(1), 16) for m in re.finditer(
        r"8'h([0-9a-f]{2})\s*:\s*(?!haltR <= True;   // unimpl)", src))
    arms |= set(int(m.group(1), 16)
                for m in re.finditer(r"op == 8'h([0-9a-f]{2})", src))
    return arms | set(range(0x41, 0x60))      # put_atom_1..31 quick forms


def census(src):
    key = opcode_table()
    used = collections.Counter()
    unknown = collections.Counter()
    per_file = []
    heads = floats = modules = 0
    for name, raw in sav_files(src):
        w = list(struct.unpack('>%dH' % (len(raw) // 2), raw[:len(raw) // 2 * 2]))
        r = Reader(w)
        magic, nmod, sep = r.rd(), r.rd(), r.rd()
        assert sep == 0xFFFF, name
        if magic in (0x5702, 0x5802):
            r.i += ((r.rd() << 16) | r.rd()) + 0
        n_inst = 0
        for _ in range(nmod):
            code = parse_module(r)[5]
            for it in code:
                if it[0] == 'atom':
                    # [0x23xx, atom name]: the five atom instructions.
                    # xx carries the register in its low bits for four
                    # of them (set_atom 00-0f, put_atom 40-5f, wait_atom
                    # 80-9f, get_atom c0-df); they are counted under the
                    # family's base opcode.
                    used[(0x23, atom_base(it[2] & 0xff))] += 1
                    n_inst += 1
                    continue
                if it[0] != 'inst':
                    continue
                tag, op = it[3], (it[2] >> 24) & 0xff
                if tag == 0x24:
                    heads += 1
                elif tag == 0x30:
                    floats += 1
                elif (tag, op) in key:
                    used[(tag, op)] += 1
                    n_inst += 1
                else:
                    unknown[(tag, op)] += 1
        modules += nmod
        # What follows the last module is a 32-bit checksum: the XOR of
        # every 16-bit word before it (load.kl1 reports "Checksum Error").
        x = 0
        for v in w[:r.i]:
            x ^= v
        left = 'checksum ok' if w[r.i:] == [0, x] else \
            '%d trailing words UNEXPLAINED' % (len(w) - r.i)
        per_file.append((name, nmod, n_inst, left))
    return key, used, unknown, per_file, heads, floats, modules


def main(argv):
    flags = [a for a in argv if a.startswith('--')]
    paths = [a for a in argv if not a.startswith('--')]
    key, used, unknown, per_file, heads, floats, modules = census(paths[0] if paths else None)
    total = sum(used.values())
    got = dict(files=len(per_file), modules=modules, instructions=total,
               checksums=sum(1 for f in per_file if f[3] == 'checksum ok'),
               pred_heads=heads, floats=floats, unknown=sum(unknown.values()),
               distinct=len(used))
    if '--check' in flags:
        if got != PINNED:
            print('census: FAIL\n  got    %r\n  pinned %r' % (got, PINNED))
            return 1
        print('census: PASS (%(files)d files, %(modules)d modules, '
              '%(instructions)d instructions, %(pred_heads)d predicates, '
              '0 unknown)' % got)
        return 0
    for name, nmod, n_inst, left in per_file:
        print('%-30s %4d modules %7d instructions  (%s)'
              % (name, nmod, n_inst, left))
    print('total: %r' % got)
    for (tag, op), c in unknown.most_common():
        print('  UNKNOWN %02x/%02x %d' % (tag, op, c))
    arms = model_opcodes() if '--model' in flags else None
    if arms is not None:
        have = [k for k in used if k[0] == 0x23 and k[1] in arms]
        cov = sum(used[k] for k in have)
        print('model arms: %d of %d opcodes, %d of %d instructions (%.1f%%)'
              % (len(have), len(used), cov, total, 100.0 * cov / total))
    print('%7s  %-5s %s' % ('count', 'tag/op', 'mnemonic'))
    for (tag, op), c in used.most_common():
        names = key[(tag, op)]
        label = names[0] if len(names) == 1 else '%s (+%d sharing the opcode)' % (names[0], len(names) - 1)
        mark = '' if arms is None else ('  ' if (tag == 0x23 and op in arms) else '- ')
        print('%7d  %02x/%02x %s%s' % (c, tag, op, mark, label))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
