#!/usr/bin/env python3
"""Dump code area items with their start and end addresses."""
import struct, sys
sys.path.insert(0, '.')
from unlsav import Reader, parse_module, load_opcodes, disasm

raw = open(sys.argv[1], 'rb').read()
words = list(struct.unpack('>%dH' % (len(raw)//2), raw[:len(raw)//2*2]))
r = Reader(words)

# Skip header
magic = r.rd()
nmod = r.rd()
sep = r.rd()
assert sep == 0xFFFF
if magic in (0x5702, 0x5802):
    clen = (r.rd() << 16) | r.rd()
    for _ in range(clen):
        r.rd()

ops = load_opcodes()
mod_idx = int(sys.argv[2]) if len(sys.argv) > 2 else 0

for m in range(nmod):
    mlen, names, gc_terms, hs, preds, code = parse_module(r)
    if m == mod_idx:
        mod_name, pkg_name, _, _ = names
        mn = mod_name[1] if mod_name[1] else '#%d' % mod_name[0]
        pn = pkg_name[1] if pkg_name[1] else '#%d' % pkg_name[0]
        print('Module %d: %s/%s' % (m, pn, mn))
        for name, arity, loc in sorted(preds, key=lambda p: p[2]):
            print('  pred: %s/%d @ 0x%04x' % (name, arity, loc))
        # Print code items with start/end addresses
        addr = 0
        for item in code:
            item_addr = item[1]
            # Compute size from next item or from item type
            print('  %04x: %s' % (item_addr, disasm(item, ops)))
        break
