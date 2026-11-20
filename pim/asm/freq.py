#!/usr/bin/env python3
"""Frequency analysis of KL1-B opcodes across all .sav modules."""
import struct, sys, collections

sys.path.insert(0, '.')
from unlsav import Reader, parse_module, load_opcodes


def main():
    if len(sys.argv) < 2:
        print("Usage: freq.py <file.sav>")
        return 1
    raw = open(sys.argv[1], 'rb').read()
    words = list(struct.unpack('>%dH' % (len(raw)//2), raw[:len(raw)//2*2]))
    r = Reader(words)
    magic = r.rd()
    nmod = r.rd()
    sep = r.rd()
    assert sep == 0xFFFF
    if magic in (0x5702, 0x5802):
        clen = (r.rd() << 16) | r.rd()
        for _ in range(clen):
            r.rd()

    ops = load_opcodes()
    freq = collections.Counter()
    unknown = collections.Counter()
    mod_unknown = collections.Counter()

    for m in range(nmod):
        mlen, names, gc_terms, hs, preds, code = parse_module(r)
        mod_name = names[0][1] if names[0][1] else '#%d' % names[0][0]
        for item in code:
            if item[0] == 'inst':
                _, addr, val, tag = item
                op = (val >> 24) & 0xff
                ent = ops.get(op)
                if ent:
                    name, typ, _ = ent[0]
                    freq[name] += 1
                else:
                    unknown[op] += 1
                    mod_unknown[(op, mod_name)] += 1

    print("=== Known instruction frequencies ===")
    for name, count in freq.most_common(80):
        print("  %5d  %s" % (count, name))

    print("\n=== Unknown opcode frequencies ===")
    for op, count in unknown.most_common():
        print("  %5d  0x%02x" % (count, op))
        # Show which modules use it
        mods = [(mod, c) for (o, mod), c in mod_unknown.items() if o == op]
        for mod, c in sorted(mods, key=lambda x: -x[1])[:5]:
            print("         %3d in %s" % (c, mod))

    print("\nTotal known: %d, total unknown: %d" % (sum(freq.values()), sum(unknown.values())))


if __name__ == '__main__':
    sys.exit(main())
