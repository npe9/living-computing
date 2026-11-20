#!/usr/bin/env python3
"""Extract raw code-area words from a .sav file for Bluespec loading."""
import struct
import sys

HERE = __file__.rsplit('/', 1)[0]
sys.path.insert(0, HERE)
from unlsav import Reader, parse_module, load_opcodes


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
            return header, preds, code
    raise ValueError('module %d not found' % mod_idx)


def code_to_words(code):
    """Convert parsed code items to 40-bit memory words.

    Instructions ('inst', addr, val, o) -> {8'h23, val}
      set_atom_N (1 <= o <= 15) mapped to model set_atom (0x00) with atom=N
    Integers ('int', addr, val) -> need tag encoding
    Atom refs ('atomref', addr, aid, name) -> model-defined placeholders
    Strings, tables skipped (not yet mapped)
    
    Known limitation: the PIMOS .sav format uses inline set_atom_N
    opcodes (0x01-0x0f).  The model only has a single set_atom (0x00)
    with the atom ID in operand c, so sav2hex maps set_atom_N to
    set_atom with atom=N.  This loses the compact encoding but is
    functionally equivalent.
    """
    out = []
    for item in code:
        kind = item[0]
        if kind == 'inst':
            _, addr, val, o = item
            if 1 <= o <= 15:
                # set_atom_N: map to model set_atom (0x00) with atom=N in c
                val = (0x00 << 24) | (val & 0xffffff00) | o
            out.append((0x23 << 32) | (val & 0xffffffff))
        elif kind == 'int':
            _, addr, val = item
            # Integer encoding: tag 0x02, value in low 32 bits
            out.append((0x02 << 32) | (val & 0xffffffff))
        elif kind == 'atomref':
            _, addr, aid, name = item
            # UREF encoding: tag 0x01, atom ID in low bits
            out.append((0x01 << 32) | (aid & 0xffffffff))
        else:
            # Skip other items for now (strings, tables, atoms)
            pass
    return out


def main():
    if len(sys.argv) < 2:
        print("Usage: sav2hex.py <file.sav> [module_index]")
        return 1
    raw = open(sys.argv[1], 'rb').read()
    mod_idx = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    header, preds, code = extract_module(raw, mod_idx)
    mod_name, pkg_name, _, _ = header
    print("// Module %d: %s/%s, %d predicates, %d code items" % (
        mod_idx, mod_name, pkg_name, len(preds), len(code)))
    for name, arity, loc in preds:
        print("//   pred: %s/%d @ 0x%04x" % (name, arity, loc))
    words = code_to_words(code)
    print("//   %d loadable words" % len(words))
    for i, w in enumerate(words):
        print("pu.load(%4d, 40'h%010x);  // %s" % (
            i, w, hex(w)[2:].zfill(10)))


if __name__ == '__main__':
    sys.exit(main())
