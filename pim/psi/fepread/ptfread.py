#!/usr/bin/env python3
"""Read-only listing of compiled ESP (KL0) predicates of a held .ptf
package, with the constant pool resolved.  OURS; used to read pimfep.ptf
for docs/fep_services.md §6.

    python3 -I psi/fepread/ptfread.py PKG                 classes, predicates
    python3 -I psi/fepread/ptfread.py PKG CLASS           every predicate, listed
    python3 -I psi/fepread/ptfread.py PKG CLASS NAME[/N]  those predicates only
    (add --skel for selectors, calls, constants and immediates only)
    python3 -I psi/fepread/ptfread.py PKG --strings       every string constant
    python3 -I psi/fepread/ptfread.py PKG --keys          hash-switch keys per predicate

It imports asm/ptfdump.py (container), psi/librarian.py (predicates by
their headers) and psi/held.py (the archives, in memory) read-only.

What this file adds, all MEASURED on the held packages (check.py pins
them):

  The constant pool.  The trailer of a class record is a sequence of
  top-level terms; term k is cell k+2 of the class's code object, and
  the code starts at cell h2 = 2 + number of terms.  pool_check():
  true of all 47 classes of pimfep and of 548 of the 554 classes of
  the six PIM packages when a class reference `8b00 0d00 nnnn` is read
  as one term; four of the six misses are in pimscsi, whose pools hold
  terms this reader does not decode, so PIMSCSI POOLS ARE NOT RELIED
  ON.  A 16-bit operand of an instruction at cell n that is negative
  addresses cell n + 2 + operand, the rule ptfdump already uses for
  local calls.
  `8b00 0d00 nnnn` (tags loc|GC, obj) names the class whose id is symbol
  nnnn of the class's symbol table (every one of the 1,559 in the six
  packages is a symbol holding `##`, or `self`).
  Strings: `0310 n` + n 16-bit JIS characters; `0308 n` + n BYTES packed
  two to a word (an 8-bit string; librarian's _term reads the count as
  words, which is wrong for these and is not used here).

  Hash-switch tables.  A table spans mask+1 + 2*keys + 2 cells
  (table_span(); the hypothesis of psi/README.md "Cell numbering").
  span_check(): with that span every predicate of the six packages,
  142 of them holding a table, ends four cells before the next
  predicate's entry and every local call lands on an entry.  The
  table's fourth header word, which ptfdump calls `size`, is not a
  size: cell + 2 + that word is where a miss goes (the cell after the
  table, or the catch-all clause).  A key's target is the first cell of
  its clause when the key has one clause, and the cell BEFORE that
  key's `e5` (try) when it has more (command_type/2, convert/2).
  The integer cell after a `c7` is the cell count of the whole switch
  block that follows it.

Opcode names are NOT known from a document.  The few used in comments
are the known-plaintext readings of docs/binary_reverse_engineering.md
§4.2 and of witness.py; the listing prints raw opcodes.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
sys.path.insert(0, os.path.join(HERE, '..'))
import ptfdump as P      # noqa: E402
import librarian as L    # noqa: E402
import held              # noqa: E402

# JIS X 0208 row 1 punctuation not in ptfdump's table is left as <xxxx>.


def jis(words):
    """Text of 16-bit JIS words; control words 0000-00ff as \\xNN."""
    out = []
    for w in words:
        if w < 0x100:
            out.append('\\x%02x' % w)
        else:
            out.append(P.ch(w))
    return ''.join(out)


def jis_unicode(words):
    """(text as the JIS X 0208 codec gives it, words it could not
    decode).  Words below 0x100 are kept as control characters."""
    out, bad = [], []
    for w in words:
        if w < 0x100:
            out.append(chr(w))
            continue
        try:
            out.append((b'\x1b$B' + bytes((w >> 8, w & 255)) + b'\x1b(B').decode('iso2022_jp'))
        except UnicodeDecodeError:
            bad.append(w)
            out.append('\ufffd')
    return ''.join(out), bad


def term(rec, b, i):
    """One trailer term at word i: (term, next i)."""
    w = b[i]
    t = w >> 8
    if w == 0x0000:
        v = b[i + 1] << 16 | b[i + 2]
        return ('int', v - (1 << 32) if v >> 31 else v), i + 3
    if w == 0x0a00:
        return ('flt', b[i + 1] << 16 | b[i + 2]), i + 3
    if t == 0x01:
        return ('atom', P.sym(rec, b[i + 1])), i + 2
    if w in (0x1800, 0x1700):
        n, i, el = b[i + 1], i + 2, []
        for _ in range(n):
            e, i = term(rec, b, i)
            el.append(e)
        return ('vec' if w == 0x1800 else 'svec', el), i
    if w == 0x0200:
        a, i = term(rec, b, i + 1)
        d, i = term(rec, b, i)
        return ('list', a, d), i
    if w == 0x4b00 and b[i + 1] == 0x4c00:
        return ('code', b[i + 2]), i + 3
    if w == 0x8b00 and b[i + 1] == 0x0d00:
        return ('class', P.sym(rec, b[i + 2])), i + 3
    if w == 0x0310:
        n = b[i + 1]
        return ('str', jis(b[i + 2:i + 2 + n]), tuple(b[i + 2:i + 2 + n])), i + 2 + n
    if w == 0x0308:
        n = b[i + 1]
        nw = (n + 1) // 2
        raw = b''.join(bytes((x >> 8, x & 255)) for x in b[i + 2:i + 2 + nw])[:n]
        return ('str8', raw.decode('latin-1')), i + 2 + nw
    return ('raw', w), i + 1


def show_term(t):
    k = t[0]
    if k == 'int':
        return '%d' % t[1]
    if k == 'atom':
        return t[1]
    if k == 'str':
        return '"%s"' % t[1]
    if k == 'str8':
        return '8"%s"' % t[1].replace('\n', '\\n').replace('\r', '\\r').replace('\0', '\\0')
    if k == 'class':
        return '#' + t[1]
    if k == 'code':
        return 'code@%x' % t[1]
    if k in ('vec', 'svec'):
        return ('{%s}' if k == 'svec' else 'vec{%s}') % ', '.join(show_term(x) for x in t[1])
    if k == 'list':
        el = []
        while t[0] == 'list':
            el.append(show_term(t[1]))
            t = t[2]
        tail = '' if t == ('atom', '[]') else '|' + show_term(t)
        return '[%s%s]' % (', '.join(el), tail)
    if k == 'flt':
        return 'flt:%08x' % t[1]
    return '?%04x' % t[1]


class Cls:
    """One class record: template (librarian), pool, predicates."""

    def __init__(self, pkg, rec):
        self.pkg, self.rec, self.id = pkg, rec, rec['id']
        self.name = self.id.split('##')[-1]
        b = rec['body']
        self.L, self.h1, self.h2 = b[1] << 16 | b[2], b[3], b[4]
        self.t = L.template_from_record(pkg, rec)
        syms = rec['syms']
        si, ti = syms.index(self.id), syms.index('template')
        st = [i for i in range(5, len(b) - 3)
              if b[i] == 0x0100 and b[i + 1] == si and b[i + 2] == 0x0100 and b[i + 3] == ti][0]
        self.pool = {}
        i, k = st, 2
        while i < len(b):
            try:
                x, i = term(rec, b, i)
            except IndexError:
                x, i = ('raw', b[i]), i + 1
            self.pool[k] = x
            k += 1
        self.pool_end = k
        self.preds = sorted(self.t.preds(), key=lambda p: p.offset)
        self.entry = {p.offset: p for p in self.preds}

    def sym(self, n):
        return P.sym(self.rec, n)


def load(pkg):
    """[Cls] of a held package (pimfep, pimscsi, paragraph, ...)."""
    _name, _a, recs = P.parse_bytes(held.ptf_bytes(pkg))
    return [Cls(pkg, r) for r in recs]


def find(classes, name):
    for c in classes:
        if c.name == name:
            return c
    raise KeyError(name)


# ---------------------------------------------------------------------------
# cells of one predicate, renumbered

def s16(v):
    v &= 0xffff
    return v - 0x10000 if v & 0x8000 else v


LOCAL_CALL = (0x60, 0x61, 0x62)


def _renumber(p, spans):
    """Cells of predicate p with table k spanning spans[k] cells."""
    out, n, k = [], p.offset, 0
    for c in p.cells:
        out.append((n,) + tuple(c[1:]))
        if c[1] == 0xa0:
            n += spans[k]
            k += 1
        else:
            n += 1
    return out, n


def table_span(tab):
    """Cells a hash-switch table occupies: mask+1 index cells, two per
    key, and two more (the hypothesis of psi/README.md "Cell numbering";
    span_check() counts how often it holds)."""
    mask, _miss, ents = tab
    return mask + 1 + 2 * len(ents) + 2


def cells_of(c, p):
    """(cells renumbered from the header's offset, table spans, misses).
    A miss is a local call that does not land on a predicate entry, or
    a predicate that does not end four cells (the next header) before
    the next entry, or one cell after L for the last one (the record
    ends with one more atom cell, the package name)."""
    spans = [table_span(x[3]) for x in p.cells if x[1] == 0xa0]
    cs, end = _renumber(p, spans)
    later = [q.offset for q in c.preds if q.offset > p.offset]
    bad = 0
    for n, t, lo, v in cs:
        if t == 0x20 and v >> 24 in LOCAL_CALL and n + 2 + s16(v) not in c.entry:
            bad += 1
    if (end + 4 != min(later)) if later else (end != c.L + 1):
        bad += 1
    return cs, spans, bad


def span_check(pkgs):
    """(predicates, predicates with a table, misses among all, misses
    among those with a table)."""
    n = nt = bad = badt = 0
    for pkg in pkgs:
        for c in load(pkg):
            for p in c.preds:
                _cs, sp, b = cells_of(c, p)
                n += 1
                nt += bool(sp)
                bad += b > 0
                badt += b > 0 and bool(sp)
    return n, nt, bad, badt


def operand_note(c, n, t, lo, v):
    """Text for what an instruction's 16-bit operand addresses, if it
    addresses a pool cell or a predicate entry."""
    if t != 0x20:
        return ''
    op, d = v >> 24, s16(v)
    tgt = n + 2 + d
    if op in LOCAL_CALL:
        q = c.entry.get(tgt)
        return '   -> %s/%d' % (q.name, q.arity) if q else '   -> @%x ?' % tgt
    if d < 0 and 2 <= tgt < c.h2 and tgt in c.pool:
        return '   pool[%x] = %s' % (tgt, show_term(c.pool[tgt]))
    return ''


def show_cell(c, cell):
    n, t, lo, v = cell
    if t == 0xa0:
        mask, size, ents = v
        keys = []
        for key, idx, tgt in ents:
            keys.append('%s->%x' % (key_text(c, key), tgt))
        return 'hash op %04x mask %x size %d: %s' % (lo, mask, size, ' '.join(keys))
    return P.show(c.rec, cell) .split('   ->')[0] + operand_note(c, n, t, lo, v)


def key_text(c, key):
    t, lo, v = key
    if t == 0x00:
        return '%d' % v
    if t == 0x01:
        return c.sym(v)
    return '?%02x:%x' % (t, v)


KINDS = {0x25: 'class', 0x35: 'instance', 0x26: 'class-before', 0x27: 'class-after',
         0x36: 'before', 0x37: 'after', 0x22: 'class-slot', 0x32: 'slot',
         0x11: 'local', 0x12: 'or'}


def listing(c, p, out=None):
    out = out if out is not None else []
    cs, spans, bad = cells_of(c, p)
    out.append('%s %s/%d  @%x%s' % (KINDS.get(p.kind, '%02x' % p.kind), p.name, p.arity,
                                    p.offset, '   (%d unresolved refs)' % bad if bad else ''))
    for cell in cs:
        out.append('  %4x  %s' % (cell[0], show_cell(c, cell)))
    return out


INT_OPS = (0x27, 0x47, 0xa7)     # get / unify / put integer (witness.py)


def skeleton(c, p):
    """The listing reduced to what is readable without an interpreter:
    selectors, local calls, pool references, atoms, integer immediates,
    vector heads (3N get, bN put) and switch tables."""
    cs, _sp, _bad = cells_of(c, p)
    out = ['%s %s/%d  @%x' % (KINDS.get(p.kind, '%02x' % p.kind), p.name, p.arity, p.offset)]
    for cell in cs:
        n, t, lo, v = cell
        keep = t in (0x01, 0x60, 0xa0, 0x00)
        if t == 0x20:
            op = v >> 24
            keep = (op in LOCAL_CALL or op in INT_OPS or bool(operand_note(c, n, t, lo, v))
                    or 0x30 <= op <= 0x37 or 0xb0 <= op <= 0xb7 or op in (0xc7, 0xcc, 0xca))
        if keep:
            out.append('  %4x  %s' % (n, show_cell(c, cell)))
    return out


def immediates(c, p):
    """[(cell, opcode, value)] integer immediates of get/unify/put
    integer instructions, and integer cells, of one predicate."""
    cs, _sp, _bad = cells_of(c, p)
    out = []
    for n, t, lo, v in cs:
        if t == 0x20 and v >> 24 in INT_OPS:
            out.append((n, v >> 24, v & 0xffff))
        elif t == 0x00:
            out.append((n, None, v))
    return out


def hash_keys(c, p):
    """[[key text, ...]] one list per hash table of the predicate."""
    return [[key_text(c, k) for k, _i, _t in x[3][2]] for x in p.cells if x[1] == 0xa0]


def strings(c):
    """[(pool cell, text, JIS words or None for an 8-bit string)] every
    string in the pool, nested ones too."""
    out = []

    def walk(k, t):
        if t[0] == 'str':
            out.append((k, t[1], t[2]))
        elif t[0] == 'str8':
            out.append((k, t[1], None))
        elif t[0] in ('vec', 'svec'):
            for x in t[1]:
                walk(k, x)
        elif t[0] == 'list':
            walk(k, t[1])
            walk(k, t[2])
    for k in sorted(c.pool):
        walk(k, c.pool[k])
    return out


def pool_users(c):
    """{pool cell: [(pred, cell n, opcode)]}."""
    out = {}
    for p in c.preds:
        cs, _s, _b = cells_of(c, p)
        for n, t, lo, v in cs:
            if t == 0x20:
                d = s16(v)
                tgt = n + 2 + d
                if d < 0 and 2 <= tgt < c.h2 and v >> 24 not in LOCAL_CALL:
                    out.setdefault(tgt, []).append((p, n, v >> 24))
    return out


def pool_check(pkgs):
    """(classes, classes with h2 == 2 + terms, class refs, class refs
    naming a class id or self)."""
    n = ok = refs = good = 0
    for pkg in pkgs:
        for c in load(pkg):
            n += 1
            ok += c.pool_end == c.h2
            for t in c.pool.values():
                if t[0] == 'class':
                    refs += 1
                    good += '##' in t[1] or t[1] == 'self'
    return n, ok, refs, good


def main(argv):
    args = [a for a in argv if not a.startswith('--')]
    if not args:
        print(__doc__)
        return 2
    cl = load(args[0])
    if '--strings' in argv:
        for c in cl:
            users = pool_users(c)
            for k, s, _w in strings(c):
                who = sorted({'%s/%d' % (p.name, p.arity) for p, _n, _o in users.get(k, [])})
                print('%-28s pool[%2x] %-40r %s' % (c.name, k, s, ' '.join(who)))
        return 0
    if '--keys' in argv:
        for c in cl:
            for p in c.preds:
                for ks in hash_keys(c, p):
                    print('%-28s %s/%d: %s' % (c.name, p.name, p.arity, ' '.join(ks)))
        return 0
    if len(args) == 1:
        for c in cl:
            print('%s  L %d h2 %d' % (c.name, c.L, c.h2))
            for p in c.preds:
                print('    %-12s %s/%d @%x' % (KINDS.get(p.kind, '?'), p.name, p.arity, p.offset))
        return 0
    c = find(cl, args[1])
    want = args[2:]
    print('class %s  L %d h1 %d h2 %d' % (c.id, c.L, c.h1, c.h2))
    if not want:
        print('natures: %s' % ' '.join(c.t.natures))
        for k in sorted(c.pool):
            if k >= 6:
                print('  pool[%2x] %s' % (k, show_term(c.pool[k])))
    for p in c.preds:
        if want and not any(w == p.name or w == '%s/%d' % (p.name, p.arity) for w in want):
            continue
        print('\n'.join(skeleton(c, p) if '--skel' in argv else listing(c, p)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
