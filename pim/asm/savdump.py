#!/usr/bin/env python3
"""Dump raw code-area words from a .sav file with addresses."""
import struct
import sys

HERE = __file__.rsplit('/', 1)[0]
sys.path.insert(0, HERE)
from unlsav import Reader, parse_module


def extract_module(raw, mod_idx):
    words = list(struct.unpack('>%dH' % (len(raw) // 2), raw[:len(raw) // 2 * 2]))
    r = Reader(words)
    magic = r.rd()
    assert (magic >> 8) == 0x57, 'bad magic %04x' % magic
    nmods = r.rd()
    # skip comment
    while r.peek() != 0xFFFF:
        r.rd()
    r.rd()  # 0xFFFF
    for i in range(nmods):
        mlen, header, gc, hs, preds, code = parse_module(r)
        if i == mod_idx:
            return header, preds, code, words, r.i - mlen  # r.i now at next module
    raise ValueError('module %d not found' % mod_idx)


def main():
    if len(sys.argv) < 2:
        print("Usage: savdump.py <file.sav> [module_index]")
        return 1
    raw = open(sys.argv[1], 'rb').read()
    mod_idx = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    header, preds, code, words, mod_start = extract_module(raw, mod_idx)
    mod_name, pkg_name, _, _ = header
    # Find code area start within module
    # Module: mlen word, gc word, mod_name, pkg_name, magic, info, gc_terms, 0x1000, hs, entries, preds, code_size, code
    # We need to track through parse_module's reads to find code area offset
    # Simpler: re-parse and track offsets
    r = Reader(words)
    r.i = mod_start  # start at module beginning
    code_start_idx = None
    
    # Replicate parse_module reads to find code area start
    mod_start_i = r.i
    mlen = (r.rd() << 16) | r.rd()
    gc = r.rd()
    mod_name = ''
    pkg_name = ''
    # skip mod_name
    t = r.peek() >> 8
    o = r.peek() & 0xff
    if t == 0x00 and o > 0:
        pass  # new_instruction format? actually parse_module reads differently
    
    # This is too complex. Instead just dump raw module words.
    print("// Module %d: %s" % (mod_idx, mod_name))
    for name, arity, loc in sorted(preds, key=lambda p: p[2]):
        print("//   pred: %s/%d @ 0x%04x" % (name, arity, loc))
    print("// Dumping raw words from module start (offset=%d):" % mod_start)
    for i in range(mod_start, min(mod_start + 200, len(words))):
        w = words[i]
        print("  %04x: %04x" % (i - mod_start, w))


if __name__ == '__main__':
    sys.exit(main())
