#!/usr/bin/env python3
"""Disassemble functions of the s9term kernel image by name, with data
symbols named, using asm/hobbit_asm.py (docs/p9boot.md "The terminal").

  python3 tools/p9kdis.py screeninit       # a function
  python3 tools/p9kdis.py '?^mouse'        # symbols matching a regex
  python3 tools/p9kdis.py ^eiaspecial      # who calls or mentions it

CALL targets print relative to the function's start (the disassembler
is given the function's parcels from 0): target = start + offset.
"""
import os
import re
import sys
H = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.join(H, 'tools')); sys.path.insert(0, os.path.join(H, 'asm'))
import p9exec, hobbit_asm
K = os.path.join(H, 'tools/plan9-1e/hobbit/s9term')
k = p9exec.read_kernel(K)
syms = p9exec.kernel_symbols(k)
text = sorted((v, n) for v, t, n in syms if t in 'Tt')
by = {}
for v, t, n in syms:
    by.setdefault(n, v)
rev = {}
for v, t, n in syms:
    if t in 'TtDdBb':
        rev.setdefault(v, n)
blob = k['blob']


def parcels(a, b):
    out = []
    for addr in range(a, b, 2):
        off = k['text_off'] + (addr - k['textbase']) // 4 * 4
        w = int.from_bytes(blob[off:off + 4], 'little')
        out.append((w & 0xffff) if addr & 2 else (w >> 16))
    return out


def sub(m):
    v = int(m.group(0), 16)
    if v in rev:
        return m.group(0) + '<' + rev[v] + '>'
    return m.group(0)


def dis(name):
    a = by[name]
    i = [v for v, n in text].index(a)
    b = text[i + 1][0]
    lines = hobbit_asm.disassemble_parcels(parcels(a, b))
    pc = a
    for L in lines:
        n = 1 if not L.startswith('.') else int(L[1])
        print('%08x +%-4x %s' % (pc, pc - a, re.sub(r'0x8[0-9a-f]{7}', sub, L)))
        pc += 2 * n


def callers(target):
    tv = by[target]
    for i, (a, n) in enumerate(text[:-1]):
        b = text[i + 1][0]
        if b - a > 20000:
            continue
        try:
            lines = hobbit_asm.disassemble_parcels(parcels(a, b))
        except Exception:
            continue
        pc = a
        for L in lines:
            m = re.search(r'CALL (-?0x[0-9a-f]+)$', L)
            if m and a + int(m.group(1), 16) == tv:
                print('%s+0x%x calls %s' % (n, pc - a, target))
            if (('$%d' % (tv - (1 << 32))) in L or ('$%d' % tv) in L
                    or ('$0x%08x' % tv) in L):
                print('%s+0x%x mentions %s: %s' % (n, pc - a, target, L))
            pc += 2 * (1 if not L.startswith('.') else int(L[1]))


for n in sys.argv[1:]:
    if n.startswith('^'):
        callers(n[1:])
        continue
    if n.startswith('?'):
        for v, t, nm in sorted(syms):
            if re.search(n[1:], nm) and t in 'TtDdBb':
                print(hex(v), t, nm)
        continue
    print('==', n)
    dis(n)
