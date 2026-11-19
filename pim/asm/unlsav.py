#!/usr/bin/env python3
"""Decode PIMOS unloader files (.sav) and disassemble their KL1-B code.

The format is defined by pimos/src/library/unloader/encoder.kl1 and
documented in docs/pimos_binaries.md.  This tool walks the 16-bit
big-endian word stream: file header, comment, then per module
[length, GCSize, GC terms, predicate table, code size, code, 0xFFFF].

The code serialization is [VAL1, VAL2, Tag] for a general instruction
(value = VAL1:VAL2, opcode = VAL1's top byte) and [0x23xx, atom-name]
for the atom special cases.  The opcode map is read from
docs/kl1_encoding.md.

Usage:
    python3 asm/unlsav.py FILE.sav [--disasm N]
"""
import re
import struct
import sys

HERE = __file__.rsplit('/', 1)[0]
ENCODING = HERE + '/../docs/kl1_encoding.md'

MAGIC = {
    0x5502: 'module',
    0x5602: 'package',
    0x5702: 'comment',
    0x5802: 'commented package',
    0x5902: 'term',
}


def load_opcodes(path=ENCODING):
    text = open(path).read()
    ops = {}
    pat = r'\| `([^`]+)` \| `16#"([0-9a-fA-F]+)"` \| `16#"([0-9a-fA-F]+)"` \| `([^`]*)` \|'
    for m in re.finditer(pat, text):
        name, tag, op, typ = m.groups()
        ops.setdefault(int(op, 16), []).append((name, typ, int(tag, 16)))
    return ops


class Reader:
    def __init__(self, words):
        self.w = words
        self.i = 0
        self.atoms = {}

    def rd(self):
        v = self.w[self.i]
        self.i += 1
        return v

    def peek(self):
        return self.w[self.i]


def read_atom_name(r):
    """Atom: ID, L1, L2, then one char word each (decoder.kl1 get_atom_name).

    ID >= 0x8000 defines a new atom (ID & 0x7FFF); ID < 0x8000 is a
    reference to an atom already defined earlier in the stream.  The
    reference resolves through the reader's atom table.
    """
    aid = r.rd()
    if aid < 0x8000:
        return aid, r.atoms.get(aid, '')
    ln = (r.rd() << 16) | r.rd()
    chars = bytes(r.rd() & 0xff for _ in range(ln))
    name = chars.decode('latin1')
    r.atoms[aid & 0x7fff] = name
    return aid & 0x7fff, name


def parse_term(r):
    t = r.peek()
    # decode_atomic(16#"00",16#"00",...) is an atom: a 0x0000 prefix
    # followed by the atom name (decoder.kl1 get_atom_name).
    if t == 0x0000:
        r.rd()
        aid, name = read_atom_name(r)
        return ('atom', aid, name)
    # A bare atom name is an AtomID >= 0x8000 (module/package name,
    # decode_module_name -> get_atom_name).  Atom IDs are 16-bit, not
    # confined to 0x8000-0x80ff.
    if t >= 0x8000:
        aid, name = read_atom_name(r)
        return ('atom', aid, name)
    if (t & 0xff00) == 0x0100:
        r.rd()
        return ('int', t & 0xff)
    if (t & 0xff00) == 0x0200:
        r.rd()
        return ('int', -((~t + 1) & 0xff))
    if t == 0x0300:
        r.rd()
        return ('int', (r.rd() << 16) | r.rd())
    if (t & 0xff00) == 0x0600:
        r.rd()
        size = t & 0xff
        ln = (r.rd() << 16) | r.rd()
        # decode_string reads two 16-bit words per iteration and
        # extracts 32/size characters from the 32-bit word, so the
        # encoded string is 2 * ceil(ln*size/32) 16-bit words.
        nwords = 2 * ((ln * size + 31) // 32)
        chars = bytes(r.rd() & 0xff for _ in range(nwords))
        return ('string', ln)
    if t == 0x0700:
        r.rd()
        ln = (r.rd() << 16) | r.rd()
        return ('vector', [parse_term(r) for _ in range(ln)])
    if t == 0x0800:
        r.rd()
        ln = (r.rd() << 16) | r.rd()
        return ('list', [parse_term(r) for _ in range(ln)])
    if t == 0x1900:
        r.rd()
        read_atom_name(r)
        read_atom_name(r)
        return ('module',)
    if t == 0x0900:
        r.rd()
        read_atom_name(r)
        read_atom_name(r)
        return ('module',)
    if t == 0x0a00:
        r.rd()
        read_atom_name(r)
        read_atom_name(r)
        r.rd()  # arity
        pkg = r.peek()
        if pkg == 0x0000:
            r.rd()
            read_atom_name(r)
        elif pkg == 0x0100:
            r.rd()
        return ('extcall',)
    if t == 0x0500:
        r.rd()
        for _ in range(6):
            r.rd()
        return ('exfloat',)
    r.rd()
    return ('?', hex(t))


def parse_module(r):
    mod_start = r.i
    if r.i + 3 > len(r.w):
        raise ValueError('truncated module header at %d' % r.i)
    mlen = (r.rd() << 16) | r.rd()
    module_end = mod_start + mlen
    gc = r.rd()
    # decode_module_name: module atom, package atom (decoder.kl1
    # decode_module_name -> get_atom_name, not decode).
    mod_name = read_atom_name(r)
    pkg_name = read_atom_name(r)
    # decode_module_info: MagicNum (integer), InfoVec (vector)
    magic = parse_term(r)
    info = parse_term(r)
    # decode_GC_area: terms until the 0x1000 end marker
    gc_terms = []
    while r.peek() != 0x1000:
        gc_terms.append(parse_term(r))
    r.rd()  # 0x1000
    hs = r.rd()
    entries = r.rd()
    # decode_entry_table: [atom, Arity, Loc1, Loc2]
    preds = []
    for _ in range(entries):
        aid, name = read_atom_name(r)
        arity = r.rd()
        loc = (r.rd() << 16) | r.rd()
        preds.append((name, arity, loc))
    # decode_code_area: [S1,S2] = SizeOfCodeArea, then the code words
    # until 0xFFFF (decoder.kl1 decode_code_area -> decode_code).
    # The code starts immediately after the size field; no search.
    code_size = (r.rd() << 16) | r.rd()
    w = r.w
    code = []
    terminated = False
    while r.i + 2 < len(w):
        tag = r.rd()
        t = tag >> 8
        o = tag & 0xff
        if tag == 0xffff:
            terminated = True
            break
        elif t == 0x23:
            aid, name = read_atom_name(r)
            code.append(('atom', tag, name))
        elif t == 0x00 and o > 0:
            v1 = r.rd()
            v2 = r.rd()
            code.append(('inst', (v1 << 16) | v2, o))
        elif t == 0x00 and o == 0:
            aid, name = read_atom_name(r)
            code.append(('atomref', aid, name))
        elif t == 0x01:
            code.append(('int', o))
        elif t == 0x02:
            code.append(('int', -((~o + 1) & 0xff)))
        elif t == 0x03:
            hi = r.rd()
            lo = r.rd()
            code.append(('int', (hi << 16) | lo))
        elif t == 0x06:
            ln = (r.rd() << 16) | r.rd()
            nwords = 2 * ((ln * o + 31) // 32)
            chars = bytes(r.rd() & 0xff for _ in range(nwords))
            code.append(('string', chars.decode('latin1')))
        elif tag == 0x1100:
            size = r.rd()
            ent = r.rd()
            for _ in range(ent):
                a = r.rd()
                at = a >> 8
                if at == 0x01 or at == 0x02:
                    pass
                elif at == 0x03:
                    r.rd()
                    r.rd()
                elif at == 0x00:
                    read_atom_name(r)
                else:
                    break
                r.rd()  # L1
                r.rd()  # L2
            code.append(('table', size, ent))
        else:
            break
    if not terminated:
        raise ValueError('module at %d: code area not terminated by 0xFFFF'
                         % mod_start)
    return mlen, (mod_name, pkg_name, magic, info), gc_terms, hs, preds, code


def disasm(item, ops):
    if item[0] == 'atom':
        _, tag, name = item
        return 'atom[%04x] %s' % (tag, name)
    if item[0] == 'atomref':
        _, aid, name = item
        return 'atomref %d %s' % (aid, name)
    if item[0] == 'int':
        return 'int %d' % item[1]
    if item[0] == 'string':
        return 'string %r' % item[1]
    _, val, tag = item
    op = (val >> 24) & 0xff
    ent = ops.get(op)
    if not ent:
        return '??? op=%02x val=%08x' % (op, val)
    name, typ, _ = ent[0]
    a, b, c = (val >> 16) & 0xff, (val >> 8) & 0xff, val & 0xff
    imm16, imm24 = val & 0xffff, val & 0xffffff
    forms = {
        'no': name,
        'r': '%s r%d' % (name, a),
        'r_r': '%s r%d, r%d' % (name, a, b),
        'r_r_r': '%s r%d, r%d, r%d' % (name, a, b, c),
        'c8': '%s %d' % (name, a),
        'c16': '%s %d' % (name, imm16),
        'c24': '%s %d' % (name, imm24),
        'c8_r': '%s %d, r%d' % (name, a, b),
        'r_c16': '%s r%d, %d' % (name, a, imm16),
        'atom': '%s atom' % name,
    }
    return forms.get(typ, '%s[%s] %08x' % (name, typ, val))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    show = 8
    if '--disasm' in sys.argv:
        show = int(sys.argv[sys.argv.index('--disasm') + 1])
        args = [a for a in args if a != str(show)]
    if not args:
        print(__doc__)
        return 2
    raw = open(args[0], 'rb').read()
    words = list(struct.unpack('>%dH' % (len(raw) // 2), raw[:len(raw) // 2 * 2]))
    r = Reader(words)
    magic = r.rd()
    nmod = r.rd()
    sep = r.rd()
    if magic not in MAGIC or sep != 0xffff:
        print('not an unloader file: magic=%#06x sep=%#06x' % (magic, sep))
        return 1
    print('magic=%#06x (%s) modules=%d' % (magic, MAGIC[magic], nmod))
    if magic in (0x5702, 0x5802):
        clen = (r.rd() << 16) | r.rd()
        comment = bytes(r.rd() & 0xff for _ in range(clen))
        print('comment: %s' % comment.decode('latin1'))
    ops = load_opcodes()
    for m in range(nmod):
        try:
            mlen, names, gc_terms, hs, preds, code = parse_module(r)
        except (IndexError, ValueError) as e:
            print('\nmodule %d: stopped at word %d (%s)' % (m, r.i, e))
            break
        mod_name, pkg_name, magic, info = names
        mn = mod_name[1] if mod_name[1] else '#%d' % mod_name[0]
        pn = pkg_name[1] if pkg_name[1] else '#%d' % pkg_name[0]
        print('\nmodule %d: %s/%s length=%d hash=%d preds=%d code=%d'
              % (m, pn, mn, mlen, hs, len(preds), len(code)))
        for t in gc_terms[:4]:
            print('  gc: %s' % (str(t)[:90],))
        for p in preds[:4]:
            print('  pred: %-24s arity %d @ %#06x' % p)
        for item in code[:show]:
            print('  %s' % disasm(item, ops))
    return 0


if __name__ == '__main__':
    sys.exit(main())
