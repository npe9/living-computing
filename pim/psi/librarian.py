#!/usr/bin/env python3
"""The Librarian's loader, reconstructed: package templates (.ptf) to class
objects.  OURS throughout (SIMPOS's own loader is lost); every rule it
applies is labelled with its source below.

    python3 -I psi/librarian.py report [--held DIR] [--after reverse|forward]
    python3 -I psi/librarian.py class PKG##NAME [--held DIR] [--listing]
    python3 -I psi/librarian.py free [--held DIR]          the "102 classes" check

Without --held the eleven .ptf files are read from the repo's archives in
memory (psi/held.py); with --held DIR from an extraction made by
`python3 -I psi/held.py extract DIR`.  Nothing is written, nothing from an
archive is executed.

WHAT IS SOURCED, WHAT IS MEASURED, WHAT IS OURS

Template reading (MEASURED here, on all 1,455 classes of the 11 packages;
container format from asm/ptfdump.py):
  the trailer is 13 terms, anchored on the atoms `<class id>, template`:
    id, template, stamp1, stamp2,
    class-predicate codes     vector of code refs, or 0
    class slots               vector of (name, flag, init) triples, or 0
    instance-predicate codes  vector of code refs, or 0
    instance slots            triples, or 0
    local-predicate offsets   vector of integers, or 0
    dynamic predicates        0, or (once) a vector of (local offset, flag)
                              pairs matching the source's `:- dynamic(P/N)`
    natures                   [self, declared natures...] as written in the source
    referenced classes        vector of class ids, or 0
    union                     natures without self, plus referenced classes
  Term tags are KL0's (layers/KL0.md §2, whose pairing these confirm:
  0 int, 1 atom, 2 list, 3 strg, 0x0a flt, 0x17 svct, 0x18 hvct; code
  references are 4b00 4c00 offset, i.e. loc/cod with a GC bit).
  A code reference names the predicate whose header (atom, kind<<8|arity,
  predh, 0) points at that offset.  Header kinds (layers/FORMATS.md §2):
    0x25/0x35 class/instance primary, 0x27 class after-demon, 0x36
    instance before-demon, 0x37 instance after-demon (INFERENCE there),
    0x26 class before-demon (by pattern; never observed), 0x22/0x32
    class/instance slot initialisation, 0x11 local, 0x12 `$or$N`.
  Slot flag bits (MEASURED; witnessed against source by plaintext.py):
    0x10 attribute (clear: component, whose name is pkg##class$slot, the
         renaming TM-388 §3.5 describes); 0x02 the initial value is computed
         by the slot-initialisation predicate at the code reference;
    0x01 `slot is Class` (the value is the class id).

Linearisation (SOURCED, TM-388 §3.2 pp.38-39): depth-first over the
nature list, the first occurrence wins, the class itself where `*` is
written and first if `*` is omitted.  Cycles are illegal (TM-388 p.39,
TR-044 IV.4).  The template stores the nature list unlinearised (MEASURED),
so this is the loader's job (TH App A p.243: resolved at load time).  In
a template the class's own id stands where `*` was (INFERENCE: no held
source writes `*`).  A nature naming a class that is not loaded (a
`simpos##` class, an unheld package, an unqualified name found nowhere)
stays in the order as an opaque node and the result is marked partial:
what that class inherits is unknown.  Every class implicitly inherits
class `class` (TM-388 §3.6); it is not held, so it is a flag on the class
object, not a node of the order.

Method combination (SOURCED, TM-388 §3.4 pp.42-43, TR-044 pp.18-21):
before-demons ANDed in inheritance order, then the primaries as
alternatives in inheritance order, then the after-demons ANDed.  The
after-demon order is a SWITCH (`after_order`):
  'reverse'  TM-388 p.42 ("what is first inherited is executed last";
             worked example b1,b2,b3,(p1;p2;p3;fail),a3,a2,a1) and TR-044
             p.20.  Default.
  'forward'  Nakashima's thesis p.243 (m :- b0,...,bn, p, a0,...,an).
Class methods and instance methods combine separately.  Locals are not
inherited.

Slots (SOURCED, TM-388 §3.5): attributes of the same name collapse to one
slot, the first initial value in inheritance order winning; components
are private per class (their template names are already distinct).
Initialisation runs as an after-demon of `new`; the plan recorded here
lists each slot's initial value, predicate or class.  Slot numbers are
assigned in order of first appearance in the linearisation (OURS).

Method and slot tables (SOURCED in structure, TH App A Fig. A-1 p.241 and
p.242): a hash table of an index part, 2^N entries of (base of synonyms,
number of synonyms), and a contents part where each key's synonyms are
contiguous (direct chaining); the hash is the low N bits of the key (the
descriptor's mask is 2^N - 1); the method key is k = n*2^24 + a + n (a
the selector's atom number, n the arity), the slot key the slot name's
atom number.  OURS, not given by the thesis: the table size (smallest
power of two >= the number of keys), the atom numbers (interned in load
order), counting the receiver in n (as the template's arity does), and
the word layout (Python objects here).

Method bodies stay KL0: each predicate keeps its cells as asm/ptfdump.py
decodes them, for a later interpreter.
"""
import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'asm'))
sys.path.insert(0, HERE)
import ptfdump as P  # noqa: E402
import held  # noqa: E402

KIND = {0x25: ('class', 'primary'), 0x26: ('class', 'before'), 0x27: ('class', 'after'),
        0x22: ('class', 'slot_init'),
        0x35: ('instance', 'primary'), 0x36: ('instance', 'before'), 0x37: ('instance', 'after'),
        0x32: ('instance', 'slot_init'),
        0x11: ('local', 'local'), 0x12: ('local', 'or')}
ROLE_KIND = {v: k for k, v in KIND.items()}
ATTRIBUTE, BY_CODE, IS_CLASS = 0x10, 0x02, 0x01
IMPLICIT_ROOT = 'class'


class LoadError(Exception):
    pass


class CycleError(LoadError):
    pass


# --------------------------------------------------------------------------
# templates

class Pred:
    """One predicate of a template: header fields plus its KL0 cells."""

    def __init__(self, name, arity, kind, qual=0, offset=None, cells=(), label=None):
        self.name, self.arity, self.kind, self.qual = name, arity, kind, qual
        self.offset, self.cells, self.label = offset, list(cells), label
        self.section, self.role = KIND.get(kind, ('?', 'kind%02x' % kind))

    @property
    def selector(self):
        return (self.name, self.arity)

    def __repr__(self):
        return '<%s %s %s/%d>' % (self.section, self.role, self.name, self.arity)


class Slot:
    """A slot declaration as the template holds it."""

    def __init__(self, name, flag, init):
        self.name, self.flag, self.init = name, flag, init   # init: (kind, value)

    @property
    def attribute(self):
        return bool(self.flag & ATTRIBUTE)

    @property
    def short(self):
        """The source-level name: a component's pkg##class$ prefix removed."""
        return self.name.split('$', 1)[1] if '$' in self.name and '##' in self.name else self.name

    def __repr__(self):
        return '<%s %s %r>' % ('attribute' if self.attribute else 'component', self.name, self.init)


class Template:
    """A class template: what the compiler left for the loader."""

    def __init__(self, cid, natures, class_preds=(), instance_preds=(), locals_=(),
                 class_slots=(), instance_slots=(), refs=(), union=(), stamp=(0, 0),
                 symbols=(), origin='synthetic'):
        self.id = cid
        self.package, self.name = cid.split('##', 1) if '##' in cid else ('', cid)
        self.natures = list(natures)
        self.class_preds, self.instance_preds = list(class_preds), list(instance_preds)
        self.locals = list(locals_)
        self.class_slots, self.instance_slots = list(class_slots), list(instance_slots)
        self.refs, self.union, self.stamp = list(refs), list(union), stamp
        self.symbols, self.origin = list(symbols), origin
        self.failures = []
        self.unreferenced_headers = []
        self.extra = None
        self.dynamic = []      # [(local Pred, flag term)] from trailer field 9

    @classmethod
    def synthetic(cls, name, natures=(), package='test', methods=(), **kw):
        """A template written by hand (tests).  NATURES may contain '*';
        METHODS is a list of (section, role, name, arity, label)."""
        cid = '%s##%s' % (package, name)
        nat = []
        for n in natures:
            nat.append(cid if n == '*' else (n if '##' in n else '%s##%s' % (package, n)))
        if cid not in nat:
            nat.insert(0, cid)
        t = cls(cid, nat, **kw)
        for section, role, mname, arity, label in methods:
            p = Pred(mname, arity, ROLE_KIND[(section, role)], label=label)
            (t.class_preds if section == 'class' else t.instance_preds).append(p)
        return t

    def preds(self):
        return self.class_preds + self.instance_preds + self.locals + [
            s.init[1] for s in self.class_slots + self.instance_slots if s.init[0] == 'code']


# trailer terms -------------------------------------------------------------

def _term(rec, b, i):
    w = b[i]
    t = w >> 8
    if w == 0x0000:
        return ('int', b[i + 1] << 16 | b[i + 2]), i + 3
    if w == 0x0a00:
        return ('flt', b[i + 1] << 16 | b[i + 2]), i + 3
    if t == 0x01:
        return ('atom', P.sym(rec, b[i + 1])), i + 2
    if w in (0x1800, 0x1700):
        n, i, el = b[i + 1], i + 2, []
        for _ in range(n):
            e, i = _term(rec, b, i)
            el.append(e)
        return ('vec' if w == 0x1800 else 'svec', el), i
    if w == 0x0200:
        a, i = _term(rec, b, i + 1)
        d, i = _term(rec, b, i)
        return ('list', a, d), i
    if w == 0x4b00 and b[i + 1] == 0x4c00:
        return ('code', b[i + 2]), i + 3
    if w == 0x1b00:
        return ('mod', b[i + 1]), i + 2
    if t == 0x03:
        n = b[i + 1]
        return ('str', ''.join(P.ch(x) for x in b[i + 2:i + 2 + n])), i + 2 + n
    return ('raw', w), i + 1


def _value(t):
    k = t[0]
    if k in ('int', 'atom', 'str', 'code'):
        return t[1]
    if k == 'flt':
        import struct
        return struct.unpack('>f', struct.pack('>I', t[1]))[0]
    return t


def _tokens(rec, stop):
    """The code cells of a record up to word STOP (the trailer anchor), as
    asm/ptfdump.py cells() reads them, without its stop at cell L.
    ptfdump's cell numbering drifts after some hash tables (MEASURED: in
    84 of 162 tables followed by a header the table spans
    mask+1 + 2*keys + 2 cells, one more than ptfdump counts; other cases
    vary), so nothing here relies on a token's own cell number across
    predicates: each predicate is found by its header, whose predh cell
    carries the true offset."""
    b = rec['body']
    i, n, out = 5, b[4], []

    def one(i):
        t = b[i] >> 8
        if t in P.W3:
            return (t, b[i] & 255, b[i + 1] << 16 | b[i + 2]), i + 3
        if t in P.W2:
            return (t, b[i] & 255, b[i + 1]), i + 2
        return None, i

    while i < stop:
        if b[i] >> 8 == 0xa0:
            op, mask, cnt, size = b[i + 1], b[i + 2], b[i + 3], b[i + 4]
            i += 5
            ents = []
            for _ in range(cnt):
                key, i = one(i)
                if key is None:
                    return out, 'hash table entry not decoded at word %d' % i
                ents.append((key, b[i], b[i + 1]))
                i += 2
            out.append((n, 0xa0, op, (mask, size, ents)))
            n += size + 1
            continue
        cell, j = one(i)
        if cell is None:
            return out, 'cell not decoded at word %d (%04x), %d words before the trailer' % (
                i, b[i], stop - i)
        out.append((n,) + cell)
        i = j
        n += 1
    return out, None


def _headers(rec, cs):
    """{code offset: (token index of the name, name, kind, qual, arity)}
    for every (atom, int, predh, 0) quadruple in the token stream."""
    out = {}
    for k in range(len(cs) - 3):
        a, f, h, z = cs[k:k + 4]
        if a[1] == 1 and a[2] == 0 and f[1] == 0 and h[1] == 0x24 and z[1] == 0 and z[3] == 0:
            if (f[3] & 255) == h[3] >> 24:
                out[h[3] & 0xffff] = (k, P.sym(rec, a[3]), (f[3] >> 8) & 255, f[3] >> 16, h[3] >> 24)
    return out


def template_from_record(pkg, rec):
    """Template from one ptfdump class record; problems go to .failures."""
    b, syms, cid = rec['body'], rec['syms'], rec['id']
    t = Template(cid, [], symbols=syms, origin='ptf')
    if t.package != pkg:
        t.failures.append('class id %s not in package %s' % (cid, pkg))
    try:
        si, ti = syms.index(cid), syms.index('template')
    except ValueError:
        t.failures.append('trailer: no id/template atoms')
        return t
    starts = [i for i in range(5, len(b) - 3)
              if b[i] == 0x0100 and b[i + 1] == si and b[i + 2] == 0x0100 and b[i + 3] == ti]
    if not starts:
        t.failures.append('trailer: anchor not found')
        return t
    if len(starts) > 1:
        t.failures.append('trailer: %d anchors, first used' % len(starts))
    i, terms = starts[0], []
    try:
        for _ in range(13):
            x, i = _term(rec, b, i)
            terms.append(x)
        if terms[9][0] == 'vec':
            # MEASURED once (tour##tt_belief_system): field 9 is a vector of
            # 19 (local offset, 0 | mod 2) pairs, and its source declares
            # 19 `:- dynamic(P/N);` in the local part (tour_bel.esp:177):
            # the dynamic-predicate table.  The 0 / mod 2 flag is UNKNOWN.
            t.extra = terms[9]
            terms[9] = ('int', 0)
    except IndexError:
        t.failures.append('trailer: ran off the record')
        return t
    (_id, _tp, s1, s2, cm, csl, im, isl, loc, f9, nat, refs, uni) = terms
    t.stamp = (_value(s1), _value(s2))
    cs, err = _tokens(rec, starts[0])
    if err:
        t.failures.append('code: ' + err)
    heads = _headers(rec, cs)
    starts_sorted = sorted(h[0] for h in heads.values()) + [len(cs)]
    used = set()

    def pred_at(off, sections, what):
        h = heads.get(off)
        if h is None:
            t.failures.append('%s: no header for code @%x' % (what, off))
            return None
        k, name, kind, qual, arity = h
        if KIND.get(kind, ('?',))[0] not in sections:
            t.failures.append('%s: %s/%d @%x has kind %02x' % (what, name, arity, off, kind))
        used.add(off)
        nxt = min(s for s in starts_sorted if s > k)
        toks = cs[k + 4:nxt]
        # cells renumbered from the header's own offset (see _tokens)
        body = [(off + c[0] - toks[0][0],) + tuple(c[1:]) for c in toks] if toks else []
        return Pred(name, arity, kind, qual, off, body)

    def vec(x, what):
        if x == ('int', 0):
            return []
        if x[0] != 'vec':
            t.failures.append('%s: not a vector: %r' % (what, x[0]))
            return []
        return x[1]

    for x in vec(cm, 'class methods'):
        if x[0] != 'code':
            t.failures.append('class methods: element %r' % (x[0],))
            continue
        p = pred_at(x[1], ('class',), 'class methods')
        if p:
            t.class_preds.append(p)
    for x in vec(im, 'instance methods'):
        if x[0] != 'code':
            t.failures.append('instance methods: element %r' % (x[0],))
            continue
        p = pred_at(x[1], ('instance',), 'instance methods')
        if p:
            t.instance_preds.append(p)
    for x in vec(loc, 'locals'):
        if x[0] != 'int':
            t.failures.append('locals: element %r' % (x[0],))
            continue
        p = pred_at(x[1], ('local',), 'locals')
        if p:
            t.locals.append(p)
    for x, out, sec, kind in ((csl, t.class_slots, 'class slots', 0x22),
                              (isl, t.instance_slots, 'instance slots', 0x32)):
        el = vec(x, sec)
        if len(el) % 3:
            t.failures.append('%s: %d elements' % (sec, len(el)))
            continue
        for j in range(0, len(el), 3):
            nm, fl, iv = el[j:j + 3]
            if nm[0] != 'atom' or fl[0] != 'int':
                t.failures.append('%s: triple %r %r' % (sec, nm[0], fl[0]))
                continue
            flag = fl[1]
            if flag & BY_CODE:
                p = pred_at(iv[1], (KIND[kind][0],), sec) if iv[0] == 'code' else None
                if p is not None and p.kind != kind:
                    t.failures.append('%s: init predicate %s has kind %02x' % (sec, p.name, p.kind))
                init = ('code', p)
            elif flag & IS_CLASS:
                init = ('is', _value(iv))
            else:
                init = ('const', _value(iv))
            out.append(Slot(nm[1], flag, init))
    if f9 != ('int', 0):
        t.failures.append('trailer field 9 is not 0 (%s)' % f9[0])
    if t.extra is not None:
        el = t.extra[1]
        for j in range(0, len(el) - 1, 2):
            p = pred_at(el[j][1], ('local',), 'dynamic') if el[j][0] == 'int' else None
            if p is not None:
                t.dynamic.append((p, el[j + 1]))
    if nat[0] != 'vec' or any(x[0] != 'atom' for x in nat[1]):
        t.failures.append('natures: not a vector of atoms')
    else:
        t.natures = [x[1] for x in nat[1]]
        if cid not in t.natures:
            t.failures.append('natures: own id absent')
            t.natures.insert(0, cid)
    t.refs = [x[1] for x in vec(refs, 'refs') if x[0] == 'atom']
    t.union = [x[1] for x in vec(uni, 'union') if x[0] == 'atom']
    t.unreferenced_headers = sorted((h[1], h[4], h[2]) for off, h in heads.items()
                                    if off not in used)
    return t


# --------------------------------------------------------------------------
# hash tables (TH App A Fig. A-1)

class HashTable:
    """Index of 2^N (base, count) entries; contents with each key's
    synonyms contiguous; hash = key & mask (TH App A Fig. A-1, p.242).
    The size rule is OURS."""

    def __init__(self, entries):
        n = len(entries)
        bits = 0
        while (1 << bits) < n:
            bits += 1
        self.bits, self.mask = bits, (1 << bits) - 1
        buckets = collections.defaultdict(list)
        for k, v in entries:
            buckets[k & self.mask].append((k, v))
        self.index, self.contents = [], []
        for h in range(1 << bits):
            syn = buckets.get(h, [])
            self.index.append((len(self.contents), len(syn)))
            self.contents.extend(syn)

    def lookup(self, key):
        base, count = self.index[key & self.mask]
        for k, v in self.contents[base:base + count]:
            if k == key:
                return v
        return None

    def max_synonyms(self):
        return max((c for _b, c in self.index), default=0)


def method_key(atom_number, arity):
    """TH App A p.242: k = n * 2^24 + a + n."""
    return arity * (1 << 24) + atom_number + arity


# --------------------------------------------------------------------------
# class objects

class Combined:
    """A combined method (TM-388 §3.4)."""

    def __init__(self, selector, section, before, primaries, after):
        self.selector, self.section = selector, section
        self.before, self.primaries, self.after = before, primaries, after

    def text(self, name=lambda cid, p: p.label or cid.split('##')[-1]):
        """The combination in TM-388 p.43's notation."""
        parts = [name(c, p) for c, p in self.before]
        parts.append('(' + ';'.join([name(c, p) for c, p in self.primaries] + ['fail']) + ')')
        parts += [name(c, p) for c, p in self.after]
        return ':%s/%d :- %s' % (self.selector + (','.join(parts),))

    def __repr__(self):
        return '<combined %s %s/%d: %d before, %d primary, %d after>' % (
            (self.section,) + self.selector + (len(self.before), len(self.primaries), len(self.after)))


class SlotEntry:
    def __init__(self, number, slot, owner):
        self.number, self.slot, self.owner = number, slot, owner

    @property
    def name(self):
        return self.slot.name

    def __repr__(self):
        return '<slot %d %s from %s>' % (self.number, self.slot.name, self.owner)


class ClassObject:
    def __init__(self, template):
        self.template, self.id = template, template.id
        self.order, self.opaque, self.complete = [], [], True
        self.implicit_root = IMPLICIT_ROOT
        self.class_methods, self.instance_methods = {}, {}
        self.class_slots, self.instance_slots = [], []
        self.class_method_table = self.instance_method_table = None
        self.class_slot_table = self.instance_slot_table = None

    def __repr__(self):
        return '<class object %s: %d in order%s>' % (
            self.id, len(self.order), '' if self.complete else ' (partial)')


class Librarian:
    """Loads templates and builds class objects."""

    def __init__(self, after_order='reverse'):
        if after_order not in ('reverse', 'forward'):
            raise ValueError(after_order)
        self.after_order = after_order
        self.templates = {}
        self.packages = collections.OrderedDict()   # declared name -> info
        self.atoms = {}
        self._built = {}

    # loading ---------------------------------------------------------------
    def atom(self, name):
        """Atom number (OURS: interned in load order)."""
        if name not in self.atoms:
            self.atoms[name] = len(self.atoms)
        return self.atoms[name]

    def add(self, t):
        if t.id in self.templates:
            raise LoadError('class %s loaded twice' % t.id)
        self.templates[t.id] = t
        self.packages.setdefault(t.package, dict(file=None, attrs={}, classes=[]))['classes'].append(t.id)
        for s in t.symbols:
            self.atom(s)
        self._built.clear()
        return t

    def load_ptf(self, data, label=None):
        name, attrs, recs = P.parse_bytes(data)
        info = self.packages.setdefault(name, dict(file=None, attrs={}, classes=[]))
        info['file'], info['attrs'] = label, attrs
        for rec in recs:
            self.add(template_from_record(name, rec))
        return name

    def load_held(self, pkgs=None, root=None):
        out = []
        for p in pkgs or held.PTF:
            out.append(self.load_ptf(held.ptf_bytes(p, root), p))
        return out

    # resolution ------------------------------------------------------------
    def resolve(self, ref, from_pkg):
        """-> (status, id).  status: 'held', 'simpos', 'unheld_package',
        'missing' (package held, class not in it), 'unqualified' (found in
        no package).  Unqualified names: the own package first, then the
        other loaded packages, in load order (ESP.md §9: the package
        environment; its priority rule is not modelled)."""
        if '##' in ref:
            pkg = ref.split('##', 1)[0]
            if ref in self.templates:
                return 'held', ref
            if pkg == 'simpos':
                return 'simpos', ref
            if pkg not in self.packages:
                return 'unheld_package', ref
            return 'missing', ref
        own = '%s##%s' % (from_pkg, ref)
        if own in self.templates:
            return 'held', own
        for pkg in self.packages:
            cand = '%s##%s' % (pkg, ref)
            if cand in self.templates:
                return 'held', cand
        return 'unqualified', ref

    def linearise(self, cid, _stack=()):
        """-> (order, opaque): order is the TM-388 inheritance order (ids;
        opaque nodes included); opaque is [(ref, status)] for natures that
        are not loaded."""
        if cid in _stack:
            raise CycleError('inheritance loop: %s' % ' -> '.join(_stack + (cid,)))
        t = self.templates[cid]
        order, opaque = [], []
        for n in t.natures:
            if n == cid:
                seq, op = [cid], []
            else:
                st, rid = self.resolve(n, t.package)
                if st == 'held':
                    seq, op = self.linearise(rid, _stack + (cid,))
                else:
                    seq, op = [rid], [(rid, st)]
            for x in seq:
                if x not in order:
                    order.append(x)
            for x in op:
                if x not in opaque:
                    opaque.append(x)
        return order, opaque

    def build(self, cid):
        if cid in self._built:
            return self._built[cid]
        t = self.templates[cid]
        co = ClassObject(t)
        co.order, co.opaque = self.linearise(cid)
        co.complete = not co.opaque
        held_order = [c for c in co.order if c in self.templates]
        for section, store in (('class', co.class_methods), ('instance', co.instance_methods)):
            groups = collections.OrderedDict()
            for c in held_order:
                tc = self.templates[c]
                for p in (tc.class_preds if section == 'class' else tc.instance_preds):
                    g = groups.setdefault(p.selector, dict(before=[], primary=[], after=[]))
                    g[p.role].append((c, p))
            for sel, g in groups.items():
                after = g['after'] if self.after_order == 'forward' else list(reversed(g['after']))
                store[sel] = Combined(sel, section, g['before'], g['primary'], after)
        for section in ('class', 'instance'):
            seen, entries = set(), []
            for c in held_order:
                tc = self.templates[c]
                for s in (tc.class_slots if section == 'class' else tc.instance_slots):
                    key = s.name
                    if key in seen:
                        continue          # attribute: first in inheritance order wins
                    seen.add(key)
                    entries.append(SlotEntry(len(entries), s, c))
            setattr(co, section + '_slots', entries)
        co.class_method_table = HashTable(
            [(method_key(self.atom(n), a), m) for (n, a), m in co.class_methods.items()])
        co.instance_method_table = HashTable(
            [(method_key(self.atom(n), a), m) for (n, a), m in co.instance_methods.items()])
        co.class_slot_table = HashTable([(self.atom(e.name), e.number) for e in co.class_slots])
        co.instance_slot_table = HashTable([(self.atom(e.name), e.number) for e in co.instance_slots])
        self._built[cid] = co
        return co

    def send(self, co, section, name, arity):
        """Look a selector up the way the microcode would (Fig. A-1)."""
        table = co.class_method_table if section == 'class' else co.instance_method_table
        if name not in self.atoms:
            return None
        return table.lookup(method_key(self.atoms[name], arity))

    def slot_number(self, co, section, name):
        table = co.class_slot_table if section == 'class' else co.instance_slot_table
        if name not in self.atoms:
            return None
        return table.lookup(self.atoms[name])

    def build_all(self):
        out, failed = {}, {}
        for cid in self.templates:
            try:
                out[cid] = self.build(cid)
            except LoadError as e:
                failed[cid] = str(e)
        return out, failed

    # the "needs no SIMPOS" closure ----------------------------------------
    def free_of_simpos(self, ids=None, edges='natures'):
        """Classes with no path to a class that is not loaded.  EDGES:
        'natures' (inheritance only) or 'union' (natures and the trailer's
        referenced-classes vector).  Restricted to IDS if given (and only
        edges into IDS then count as held)."""
        scope = set(ids if ids is not None else self.templates)
        memo = {}

        def outs(c):
            t = self.templates[c]
            refs = [n for n in t.natures if n != c]
            if edges == 'union':
                refs += t.refs
            for r in refs:
                st, rid = self.resolve(r, t.package)
                yield (rid if st == 'held' and rid in scope else None)

        def dep(c, stack=()):
            if c in memo:
                return memo[c]
            if c in stack:
                return False
            r = any(x is None or dep(x, stack + (c,)) for x in outs(c))
            if not stack or r:
                memo[c] = r
            return r

        return sorted(c for c in scope if not dep(c))


# --------------------------------------------------------------------------
# reports

def package_report(lib):
    rows = []
    built, failed = lib.build_all()
    for pkg, info in lib.packages.items():
        ids = info['classes']
        kinds = collections.Counter()
        res = collections.Counter()
        fails = 0
        partial = 0
        unq = collections.Counter()
        unref = collections.Counter()
        self_not_first = extra = 0
        for cid in ids:
            t = lib.templates[cid]
            fails += bool(t.failures)
            self_not_first += bool(t.natures) and t.natures[0] != cid
            extra += t.extra is not None
            for _n, _a, k in t.unreferenced_headers:
                unref['%02x' % k] += 1
            for p in t.preds():
                if p is not None:
                    kinds['%02x' % p.kind] += 1
            for n in t.natures:
                if n == cid:
                    continue
                st, rid = lib.resolve(n, pkg)
                res[st] += 1
                if st != 'held':
                    unq[rid] += 1
            if cid in built and not built[cid].complete:
                partial += 1
        rows.append(dict(package=pkg, file=info['file'], classes=len(ids),
                         built=sum(1 for c in ids if c in built), cycle=sum(1 for c in ids if c in failed),
                         template_failures=fails, partial=partial, natures=dict(res),
                         kinds=dict(sorted(kinds.items())), unresolved=unq,
                         unreferenced_headers=dict(sorted(unref.items())),
                         self_not_first=self_not_first, extra=extra))
    return rows


def main(argv):
    root = None
    if '--held' in argv:
        root = argv[argv.index('--held') + 1]
    order = 'reverse'
    if '--after' in argv:
        order = argv[argv.index('--after') + 1]
    args = [a for k, a in enumerate(argv) if not a.startswith('--')
            and (k == 0 or argv[k - 1] not in ('--held', '--after'))]
    lib = Librarian(after_order=order)
    lib.load_held(root=root)
    if not args or args[0] == 'report':
        for r in package_report(lib):
            print('%-10s (%s) %4d classes, %4d built, %d cycles, %d templates with failures, '
                  '%d partial (an unloaded ancestor)' % (r['package'], r['file'], r['classes'], r['built'],
                                                         r['cycle'], r['template_failures'], r['partial']))
            print('    natures: %s' % ' '.join('%s %d' % kv for kv in sorted(r['natures'].items())))
            print('    predicate kinds: %s' % ' '.join('%s:%d' % kv for kv in r['kinds'].items()))
            print('    headers no trailer vector names: %s; self not first in natures: %d; '
                  'extra trailer field: %d' % (r['unreferenced_headers'] or 'none',
                                               r['self_not_first'], r['extra']))
            top = r['unresolved'].most_common(6)
            print('    unloaded natures (%d distinct): %s' % (len(r['unresolved']),
                                                              ' '.join('%s %d' % kv for kv in top)))
        for cid, t in lib.templates.items():
            for f in t.failures:
                print('FAILURE %s: %s' % (cid, f))
        return 0
    if args[0] == 'free':
        six = [c for c in lib.templates if lib.templates[c].package in
               ('pimfep', 'pimscsi', 'pimmcsp', 'pimmutil', 'mpsicsp', 'paragraph')]
        for scope_name, scope in (('six psdpim+paragraph packages', six), ('all eleven', None)):
            for e in ('natures', 'union'):
                free = lib.free_of_simpos(scope, e)
                by = collections.Counter(c.split('##')[0] for c in free)
                print('%s, edges=%s: %d free  %s' % (scope_name, e, len(free),
                                                     ' '.join('%s %d' % kv for kv in sorted(by.items()))))
        return 0
    if args[0] == 'class':
        co = lib.build(args[1])
        t = co.template
        print('%s  (template stamp %s %s)' % (co.id, t.stamp[0], t.stamp[1]))
        print('natures as written: %s' % ' '.join(t.natures))
        print('inheritance order: %s%s' % (' '.join(co.order), '' if co.complete else '  PARTIAL'))
        for r, st in co.opaque:
            print('   not loaded: %s (%s)' % (r, st))
        for section in ('class', 'instance'):
            for e in getattr(co, section + '_slots'):
                print('%s slot %d %s flag %02x init %s (from %s)' % (
                    section, e.number, e.name, e.slot.flag,
                    e.slot.init if e.slot.init[0] != 'code' else ('code', e.slot.init[1]), e.owner))
            for sel, m in getattr(co, section + '_methods').items():
                print('%s %s' % (section, m.text(lambda c, p: '%s:%s' % (c.split('##')[-1], p.role[0]))))
        for p in t.locals:
            print('local %s/%d @%x %d cells' % (p.name, p.arity, p.offset, len(p.cells)))
        if '--listing' in argv:
            rec = dict(syms=t.symbols)
            for p in t.preds():
                print('== %r @%x' % (p, p.offset))
                for c in p.cells:
                    print('%5x  %s' % (c[0], P.show(rec, c)))
        for f in t.failures:
            print('FAILURE %s' % f)
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
