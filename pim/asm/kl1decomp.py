#!/usr/bin/env python3
"""Prototype decompiler: KL1-B object code of the IPL image back to
KL1 clauses.  Read-only; a probe for docs/binary_reverse_engineering.md.

Method: a predicate's code is walked symbolically from its entry, one
walk per path through the indexing instructions (try_me_else,
switch_on_*, hash_on_constant).  Passive instructions (wait_*, read_*,
switch_*) bind the head's variables to patterns, guard built-ins
become guard goals, everything else becomes body goals; a path that
reaches proceed/execute is printed as one clause `Head :- Guard | Body`.
A path whose pattern contradicts itself is dropped.  MRB instructions
(collect_*, mark_element) are dropped: they have no source form.

What this does NOT do: recover variable names, comments, macro forms
(`fep#read`, `string#"..."` come back as numbers and strings), the
original clause order where the compiler's indexing merged clauses, or
negative type knowledge on a switch's else branch (so an else path can
print a clause the source did not have as such).  `X@n` marks a goal
enqueued with a priority or processor operand.

    python3 asm/kl1decomp.py MODULE [PRED/N]   decompile
    python3 asm/kl1decomp.py --check            sweep + fidelity numbers
    python3 asm/kl1decomp.py --fidelity MODULE SOURCE_SUFFIX
                                                clause counts vs a .kl1
"""
import collections
import copy
import re
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bltdir  # noqa: E402
import kbndis  # noqa: E402

TWO = ('f_r_r_r', 'r4', 'r5', 'r6', 'r7', 'r_c40', 'c40', 'c8_c40', 'r_r_c16_i',
       'r_c16_c8_exe', 'r_c16_c8_ext')
LOAD = 0xe0000000
MAXPATHS = 4000

# modules of the IPL image with same-named source in pimos.tar.Z
SOURCES = {
    'jis_to_ascii': 'src/bios/boot/jtoa.kl1',
    'exception_table': 'src/kernel/builtin/excpt_tbl.kl1',
    'scsi_common': 'src/bios/scsi/scsi_common.kl1',
    'scsi_processor': 'src/bios/scsi/scsi_processor.kl1',
    'scsi': 'src/bios/scsi/scsi_handler.kl1',
    'scsi_builtin': 'src/bios/scsi/scsi_blt.kl1',
    'shoen': 'src/kernel/builtin/shoen.kl1',
    'builtin_utility': 'src/kernel/builtin/string.kl1',
}


class Dead(Exception):
    pass


class Var:
    n = 0

    def __init__(self, hint=None):
        self.ref = None
        self.hint = hint


class Vec:
    def __init__(self, size=None, elems=None):
        self.size = size            # int, or a term (Var) when read by a guard
        self.elems = elems if elems is not None else []


class Lst:
    def __init__(self):
        self.elems = [None, None]


class Atom:
    def __init__(self, name):
        self.name = name


class Int:
    def __init__(self, v):
        self.v = v


class Raw:
    def __init__(self, text):
        self.text = text


def deref(t):
    while isinstance(t, Var) and t.ref is not None:
        t = t.ref
    return t


class Dis:
    """Instruction boundaries and operand decoding on top of kbndis."""

    def __init__(self):
        self.im = kbndis.Image()
        self.cells = self.im.cells
        self.fam = {}
        for op, ents in kbndis.load_opcodes().items():
            for nm, ty, tag in ents:
                m = re.fullmatch(r'(f_r_r(?:_r)?)\((.+)\)', ty)
                if m:
                    f = m.group(2)
                    f = int(f[4:-1], 16) if f.startswith('16#') else int(f)
                    self.fam.setdefault((tag, op), {})[f] = (nm, m.group(1))
        rows, _ = bltdir.table()
        self.dirs = {}
        for kind, name, d, _src in rows:
            self.dirs.setdefault((kind, name), d)

    def name(self, a):
        t, v = self.cells[a]
        if t not in (0x22, 0x23):
            return None, ''
        k = (t, v >> 24)
        if k in self.fam:
            # one opcode, several instructions: the function number is
            # the x field (klb_opr.kl1 p({f_r_r,F}...), p({f_r_r_r,F}...))
            return self.fam[k].get((v >> 16) & 255, ('f%02x_%d' % (
                v >> 24, (v >> 16) & 255), 'f_r_r_r'))
        if k in self.im.key:
            return self.im.key[k][0], self.im.typ.get(k, '')
        import census
        b = census.atom_base(v >> 24)
        return self.im.key[(0x23, b)][0], 'atomfam'

    def length(self, a):
        """Cells taken by the instruction at a."""
        name, ty = self.name(a)
        v = self.cells[a][1]
        if name == 'switch_on_constant':
            return 1 + 2 * (v & 0xffff)
        if name == 'hash_on_constant':
            size = (v & 0xffff) + 1
            pairs = 0
            for s in range(a + 2, a + 2 + size):
                st, sv = self.cells[s]
                if st == 0x00:
                    pairs += sv >> 16
            return 2 + size + 2 * pairs
        return 2 if ty in TWO else 1

    def label(self, a, v=None):
        c16 = (self.cells[a][1] if v is None else v) & 0xffff
        return a + 2 + (c16 - 0x10000 if c16 & 0x8000 else c16)

    def sweep(self, addr, ln):
        """Instruction starts in a predicate; None if the sweep does not
        end exactly at its end."""
        starts, a = [], addr
        while a < addr + ln:
            if self.cells[a][0] not in (0x22, 0x23):
                return None
            starts.append(a)
            a += self.length(a)
        return starts if a == addr + ln else None

    def const(self, a, depth=0):
        """The constant term a heap cell denotes (kbnheap.kl1 layout)."""
        t, v = self.cells[a]
        return self.term(t, v, depth)

    def term(self, t, v, depth=0):
        im = self.im
        if depth > 40:
            return Raw('...')
        if t in (0x00, 0x01):
            return Int(v - (1 << 32) if v >> 31 else v)
        if t in (0x02, 0x03):
            # kbnatom.kl1: the atom number of '[]' is fixed to zero
            return Atom(im.atom(v) if v & 0xffffff else '[]')
        if t in (0x04, 0x05):
            p = v - LOAD
            x = Lst()
            x.elems = [self.const(p, depth + 1), self.const(p + 1, depth + 1)]
            return x
        if 0x10 <= t <= 0x1d:
            n = (t - 0x10) // 2
            p = v - LOAD
            return Vec(n, [self.const(p + i, depth + 1) for i in range(n)])
        if t in (0x1e, 0x1f):
            p = v - LOAD                       # VDESC, INT n, INT n, elements
            n = self.cells[p + 1][1]
            e = self.cells[p][1] - LOAD
            return Vec(n, [self.const(e + i, depth + 1) for i in range(n)])
        if t in (0x0e, 0x0f):
            p = v - LOAD
            d = self.cells[p][1]
            words, typ, pad = d & 0xffffff, (d >> 24) & 7, d >> 27
            raw = b''.join(self.cells[p + 1 + i][1].to_bytes(4, 'big')
                           for i in range(words))
            if typ == 4:
                n = len(raw) // 2 - pad
                s = ''.join(_jis(raw[2 * i:2 * i + 2]) for i in range(n))
                return Raw('"%s"' % s)
            if typ == 3:
                n = len(raw) - pad
                return Raw('string8#"%s"' % ''.join(
                    chr(b) if 32 <= b < 127 else '\\x%02x' % b for b in raw[:n]))
            return Raw('string(type %d, %d words)' % (typ, words))
        if t in (0x06, 0x07):
            return self.const(v - LOAD, depth + 1)
        if t == 0x27:
            p = v - LOAD
            return Raw('module#%s' % im.atom(self.cells[p + 2][1]))
        if t in (0x30, 0x31):
            import struct
            return Raw(repr(struct.unpack('>f', v.to_bytes(4, 'big'))[0]))
        return Raw('<%s %08x>' % (kbndis.kbn.TAGS.get(t, '%02x' % t), v))


def _jis(w):
    if w[0] == 0:
        return chr(w[1]) if 32 <= w[1] < 127 else '\\x%02x' % w[1]
    try:
        import unicodedata
        return unicodedata.normalize(
            'NFKC', (b'\x1b$B' + w).decode('iso2022_jp'))
    except UnicodeDecodeError:
        return '\\j%02x%02x' % (w[0], w[1])


INFIX = {'less_than': '<', 'not_less_than': '>=', 'equal': '=:=',
         'not_equal': '=\\='}
ARITH = {'add': '+', 'subtract': '-', 'multiply': '*', 'divide': '/',
         'modulo': 'mod', 'shift_left': '<<', 'shift_right': '>>',
         'and': '/\\', 'or': '\\/', 'exclusive_or': 'xor'}
GUARD_TYPE = ('wait', 'atom', 'integer', 'list', 'floating_point')
SKIP = ('collect_value', 'collect_list', 'collect_vector', 'mark_element',
        'nop', 'clause_info')


class State:
    def __init__(self, arity):
        self.head = [Var() for _ in range(arity)]
        self.r = {i: v for i, v in enumerate(self.head)}
        self.args = {}
        self.sp = None
        self.guard = []
        self.body = []
        self.level = 0          # number of otherwise/alternatively passed
        self.sep = []           # which, in order
        self.sig = ()           # the keys taken at switch/hash_on_constant
        self.notes = []

    def reg(self, n):
        if n not in self.r:
            self.r[n] = Var()
        return self.r[n]


class Decomp:
    def __init__(self, dis=None):
        self.d = dis or Dis()
        self.im = self.d.im
        self.unknown = collections.Counter()
        self.seen = collections.Counter()

    # --- pattern binding ------------------------------------------------
    def match(self, st, reg, term):
        """A passive test: register `reg` must be `term` (Atom/Int)."""
        cur = deref(st.reg(reg))
        if isinstance(cur, Var):
            cur.ref = term
            return
        if isinstance(cur, (Atom, Int)):
            if type(cur) is not type(term) or \
                    (cur.name if isinstance(cur, Atom) else cur.v) != \
                    (term.name if isinstance(term, Atom) else term.v):
                raise Dead()
            return
        raise Dead()

    def structure(self, st, reg, kind, n=None):
        cur = deref(st.reg(reg))
        if isinstance(cur, Var):
            new = Lst() if kind == 'list' else Vec(n)
            cur.ref = new
            cur = new
        elif kind == 'list' and not isinstance(cur, Lst):
            raise Dead()
        elif kind == 'vec':
            if not isinstance(cur, Vec):
                raise Dead()
            if n is not None:
                sz = deref(cur.size) if not isinstance(cur.size, int) else cur.size
                if isinstance(sz, Int):
                    sz = sz.v
                if isinstance(sz, int):
                    if sz != n:
                        raise Dead()
                elif isinstance(sz, Var):
                    sz.ref = Int(n)
                elif cur.size is None:
                    cur.size = n
        st.sp = [cur, 0]
        return cur

    def elem(self, st):
        s, i = st.sp
        st.sp[1] += 1
        while len(s.elems) <= i:
            s.elems.append(None)
        return s, i

    def put_elem(self, st, term):
        if st.sp is None:
            st.notes.append('write with no structure')
            return
        s, i = self.elem(st)
        s.elems[i] = term

    # --- one instruction ---------------------------------------------------
    def step(self, st, a, work):
        """Execute the instruction at a.  Returns the next address or
        None at a terminal; appends alternative (state, addr) to work."""
        d, im = self.d, self.im
        name, ty = d.name(a)
        t, v = d.cells[a]
        x, y, z, c16 = (v >> 16) & 255, (v >> 8) & 255, v & 255, v & 0xffff
        s16 = c16 - 0x10000 if c16 & 0x8000 else c16
        nxt = a + d.length(a)
        self.seen[name] += 1
        w2 = d.cells[a + 1][1] if ty in TWO else 0
        R = st.reg

        if name in SKIP:
            return nxt
        if name == 'try_me_else':
            work.append((copy.deepcopy(st), d.label(a)))
            return nxt
        if name in ('otherwise', 'read_eagerly'):
            # read_eagerly stands where the source has `alternatively.`
            # (INFERENCE from its position between clause groups)
            st.level += 1
            st.sep.append('otherwise' if name == 'otherwise'
                          else 'alternatively')
            return nxt
        if name == 'suspend' or name == 'fail':
            return None
        if name == 'jump':
            return d.label(a)
        if name in ('switch_on_non_integer', 'switch_on_non_atom',
                    'switch_on_non_list', 'switch_on_non_vector'):
            lab = (a + 1) + 2 + _s32(d.cells[a + 1][1]) - 1 \
                if name == 'switch_on_non_vector' else d.label(a)
            if name == 'switch_on_non_vector':
                # the label word is relative as cal_location_address
                # computes it from the instruction's own address
                lab = a + 2 + _s32(d.cells[a + 1][1])
            cur = deref(R(x))
            kind = name[len('switch_on_non_'):]
            is_kind = {'integer': Int, 'atom': Atom, 'list': Lst,
                       'vector': Vec}[kind]
            if isinstance(cur, Var):
                work.append((copy.deepcopy(st), lab))
            elif not isinstance(cur, is_kind):
                return lab
            if kind == 'list':
                self.structure(st, x, 'list')
            elif kind == 'vector':
                vec = self.structure(st, x, 'vec')
                if vec.size is None:
                    vec.size = Var()
                st.r[y] = vec.size if not isinstance(vec.size, int) \
                    else Int(vec.size)
            elif isinstance(cur, Var):
                cur.ref = Var('int' if kind == 'integer' else 'atom')
                st.guard.append((kind, [cur.ref]))
            return nxt
        if name == 'switch_on_constant':
            cur = deref(R(x))
            els = None
            for i in range(c16):
                k = a + 1 + 2 * i
                kt, kv = d.cells[k]
                key = d.term(kt, kv)
                data = d.cells[k + 1][1]
                els = d.label(k + 1, data >> 16)
                tgt = d.label(k + 1, data)
                if isinstance(cur, Var) and cur.hint is None:
                    s2 = copy.deepcopy(st)
                    s2.sig += ((a, i),)
                    try:
                        self.match(s2, x, key)
                        work.append((s2, tgt))
                    except Dead:
                        pass
                elif isinstance(cur, Var):          # typed placeholder
                    s2 = copy.deepcopy(st)
                    s2.sig += ((a, i),)
                    deref(s2.reg(x)).ref = key
                    s2.guard = [g for g in s2.guard
                                if not (g[0] in ('integer', 'atom')
                                        and deref(g[1][0]) is deref(s2.reg(x)))]
                    work.append((s2, tgt))
                elif type(cur) is type(key) and _val(cur) == _val(key):
                    return tgt
            return els
        if name == 'hash_on_constant':
            size = c16 + 1
            miss = (a + 1) + 2 + _s32(d.cells[a + 1][1])
            cur = deref(R(x))
            for s in range(a + 2, a + 2 + size):
                stg, sv = d.cells[s]
                if stg != 0x00:
                    continue
                for j in range(sv >> 16):
                    k = s + (sv & 0xffff) + 2 * j
                    key = d.term(*d.cells[k])
                    tgt = k + 1 + 1 + _s32(d.cells[k + 1][1])
                    if isinstance(cur, Var):
                        s2 = copy.deepcopy(st)
                        s2.sig += ((a, k),)
                        c2 = deref(s2.reg(x))
                        c2.ref = key
                        s2.guard = [g for g in s2.guard
                                    if not (g[0] in ('integer', 'atom')
                                            and deref(g[1][0]) is key)]
                        work.append((s2, tgt))
                    elif type(cur) is type(key) and _val(cur) == _val(key):
                        return tgt
            return miss

        # passive unification
        if name == 'wait_atom':
            self.match(st, (v >> 24) - 0x80, Atom(im.atom(v)))
            return nxt
        if name == 'wait_integer':
            self.match(st, x, Int(s16))
            return nxt
        if name == 'wait_nil':
            self.match(st, x, Atom('[]'))
            return nxt
        if name == 'wait_constant':
            self.match(st, x, d.term(*d.cells[a + 1]))
            return nxt
        if name == 'wait_list':
            self.structure(st, x, 'list')
            return nxt
        if name.startswith('wait_vector'):
            n = (v >> 24) - 0xa8 if name != 'wait_vector' else c16
            self.structure(st, x, 'vec', n)
            return nxt
        if name == 'wait_value':
            st.guard.append(('=', [R(x), R(y)]))
            return nxt
        if name in ('read_variable', 'read_variable_without_deref'):
            s, i = self.elem(st)
            if s.elems[i] is None:
                s.elems[i] = Var()
            st.r[x] = s.elems[i]
            return nxt
        if name in ('read_atom', 'read_integer', 'read_nil', 'read_constant'):
            term = {'read_atom': lambda: Atom(im.atom(v)),
                    'read_integer': lambda: Int(_s24(v)),
                    'read_nil': lambda: Atom('[]'),
                    'read_constant': lambda: d.term(*d.cells[a + 1])}[name]()
            s, i = self.elem(st)
            cur = deref(s.elems[i]) if s.elems[i] is not None else None
            if cur is None:
                s.elems[i] = term
            elif isinstance(cur, Var):
                cur.ref = term
            elif type(cur) is not type(term) or _val(cur) != _val(term):
                raise Dead()
            return nxt

        # register loads
        if name == 'put_atom':
            st.r[(v >> 24) - 0x40] = Atom(im.atom(v))
            return nxt
        if name == 'put_integer':
            st.r[x] = Int(s16)
            return nxt
        if name == 'put_nil':
            st.r[x] = Atom('[]')
            return nxt
        if name == 'put_constant':
            st.r[x] = d.term(*d.cells[a + 1])
            return nxt
        if name == 'put_structured_constant':
            st.r[x] = d.const(d.label(a))
            return nxt
        if name in ('put_value', 'put_marked_value'):
            st.r[x] = R(y)
            return nxt
        if name in ('put_variable', 'put_marked_variable'):
            st.r[x] = st.r[y] = Var()
            return nxt
        if name == 'put_list':
            st.r[x] = Lst()
            st.sp = [st.r[x], 0]
            return nxt
        if name.startswith('put_vector'):
            n = (v >> 24) - 0x38 if name != 'put_vector' else c16
            st.r[x] = Vec(n, [None] * n)
            st.sp = [st.r[x], 0]
            return nxt
        if name == 'put_reused_structure':
            old = deref(R(y))
            st.r[x] = Lst() if isinstance(old, Lst) else Vec(z, [None] * z)
            st.sp = [st.r[x], 0]
            return nxt
        if name in ('write_variable', 'write_marked_variable'):
            st.r[x] = Var()
            self.put_elem(st, st.r[x])
            return nxt
        if name in ('write_value', 'write_marked_value'):
            self.put_elem(st, R(x))
            return nxt
        if name == 'write_atom':
            self.put_elem(st, Atom(im.atom(v)))
            return nxt
        if name == 'write_integer':
            self.put_elem(st, Int(_s24(v)))
            return nxt
        if name == 'write_nil':
            self.put_elem(st, Atom('[]'))
            return nxt
        if name == 'write_constant':
            self.put_elem(st, d.term(*d.cells[a + 1]))
            return nxt

        # goal arguments
        if name in ('set_value', 'set_marked_value'):
            st.args[x] = R(y)
            return nxt
        if name in ('set_variable', 'set_marked_variable'):
            st.args[x] = st.r[y] = Var()
            return nxt
        if name == 'set_integer':
            st.args[x] = Int(s16)
            return nxt
        if name == 'set_atom':
            st.args[v >> 24] = Atom(im.atom(v))
            return nxt
        if name == 'set_nil':
            st.args[x] = Atom('[]')
            return nxt
        if name == 'set_constant':
            st.args[x] = d.term(*d.cells[a + 1])
            return nxt

        # body unification
        if name in ('get_value', 'get_bound_value'):
            st.body.append(('=', [R(x), R(y)]))
            return nxt
        if name == 'get_atom':
            st.body.append(('=', [R((v >> 24) - 0xc0), Atom(im.atom(v))]))
            return nxt
        if name == 'get_integer':
            st.body.append(('=', [R(x), Int(s16)]))
            return nxt
        if name == 'get_nil':
            st.body.append(('=', [R(x), Atom('[]')]))
            return nxt
        if name == 'get_constant':
            st.body.append(('=', [R(x), d.term(*d.cells[a + 1])]))
            return nxt

        # goals
        if name in ('enqueue_goal', 'enqueue_goal_external',
                    'enqueue_goal_with_priority', 'enqueue_goal_to_processor'):
            n = x
            pragma = None
            if name == 'enqueue_goal_external':
                ext = im.external(a)
                pred = '%s:%s' % (ext[0], ext[1].rsplit('/', 1)[0]) if ext \
                    else 'external@%d' % a
            else:
                pred = self.predname(d.label(a))
            if name in ('enqueue_goal_with_priority',
                        'enqueue_goal_to_processor'):
                n = w2 >> 24
                pragma = ('priority' if name.endswith('priority')
                          else 'processor', R(x))
            st.body.append((pred, [st.args.get(i + 1, Raw('?'))
                                   for i in range(n)], pragma))
            st.args = {}
            return nxt
        if name in ('execute', 'execute_external'):
            if name == 'execute_external':
                ext = im.external(a)
                pred = '%s:%s' % (ext[0], ext[1].rsplit('/', 1)[0]) if ext \
                    else 'external@%d' % a
            else:
                pred = self.predname(d.label(a))
            st.body.append((pred, [R(i) for i in range(x)]))
            return None
        if name == 'proceed':
            return None

        # built-ins: guard (tag 23) and body (tag 22)
        regs = self.operands(ty, v, w2)
        if regs is not None:
            # tag 23: 70..7f are actions (console, halt, ...) except 76,
            # the word/tag_and_value family, which the image uses in guards
            kind = 'guard' if t == 0x23 and (v >> 24 == 0x76 or
                                             not 0x70 <= v >> 24 <= 0x7f) \
                else 'body'
            base = name[2:] if name.startswith('b_') and \
                (kind, name) not in d.dirs else name
            dirs = d.dirs.get((kind, name)) or d.dirs.get(('guard', base)) \
                or d.dirs.get(('body', name)) or ''
            if len(dirs) != len(regs):
                dirs = 'i' * len(regs)
                if name not in GUARD_TYPE and name not in INFIX and regs:
                    self.unknown['direction of ' + name] += 1
            terms = []
            for dch, rn in zip(dirs, regs):
                if dch == 'o':
                    st.r[rn] = Var()
                terms.append(R(rn))
            (st.guard if kind == 'guard' else st.body).append((name, terms))
            return nxt
        self.unknown[name] += 1
        st.body.append(("'$%s'" % name, [Raw('%d,%d,%d' % (x, y, z))]))
        return nxt

    def operands(self, ty, v, w2):
        x, y, z = (v >> 16) & 255, (v >> 8) & 255, v & 255
        if ty == 'r':
            return [x]
        if ty == 'r_r':
            return [x, y]
        if ty == 'r_r_r':
            return [x, y, z]
        if ty in ('r4', 'r5', 'r6', 'r7'):
            extra = [(w2 >> 24) & 255, (w2 >> 16) & 255, (w2 >> 8) & 255,
                     w2 & 255]
            return [x, y, z] + extra[:int(ty[1]) - 3]
        if ty == 'f_r_r_r':
            return [y, z, (w2 >> 24) & 255]
        if ty == 'f_r_r':
            return [y, z]
        if ty == 'no':
            return []
        return None

    def predname(self, tgt):
        m, p = self.im.where(tgt)
        if p and p[2] == tgt:
            return p[0].rsplit('/', 1)[0]
        return '%s@%d' % (p[0].rsplit('/', 1)[0] if p else '?', tgt)

    # --- a predicate --------------------------------------------------------
    def predicate(self, modname, pred):
        m = [m for m in self.im.mods if m['name'] == modname][0]
        name, ln, addr = [p for p in m['preds'] if p[0] == pred][0]
        arity = int(name.rsplit('/', 1)[1])
        work = [(State(arity), addr)]
        cands, paths = [], 0
        truncated = False
        while work:
            st, a = work.pop()
            paths += 1
            if paths > MAXPATHS:
                truncated = True
                break
            try:
                steps = 0
                while a is not None:
                    if not (addr <= a < addr + ln):
                        st.notes.append('left the predicate at %d' % a)
                        break
                    last = a
                    a = self.step(st, a, work)
                    steps += 1
                    if steps > 5000:
                        break
            except Dead:
                continue
            lname = self.d.name(last)[0]
            if lname in ('suspend', 'fail'):
                continue
            head, guard, body = Render().clause(name.rsplit('/', 1)[0], st)
            cands.append(dict(level=st.level, exit=last, nbody=len(st.body),
                              sep=tuple(st.sep), sig=frozenset(st.sig),
                              n=len(head) + len(guard), order=len(cands),
                              text='%s :- %s |\n    %s.\n' % (head, guard, body)))
        # HEURISTIC: of the paths that end at the same exit instruction
        # with the same constant keys taken, the one with the shortest
        # head and guard is printed; so is a path that took a subset of
        # another's keys.  The longer ones carry what an earlier
        # clause's indexing had already established on the way there.
        clauses = []
        for c in cands:
            same = [o for o in cands if o is not c and
                    (o['level'], o['exit'], o['nbody'], o['sep']) ==
                    (c['level'], c['exit'], c['nbody'], c['sep'])]
            if any(o['sig'] < c['sig'] or
                   (o['sig'] == c['sig'] and
                    (o['n'], o['order']) < (c['n'], c['order']))
                   for o in same):
                continue
            clauses.append((c['level'], c['order'], c['text'], c['sep']))
        clauses.sort(key=lambda c: (c[0], c[1]))
        return clauses, truncated


def _s32(v):
    return v - (1 << 32) if v >> 31 else v


def _s24(v):
    v &= 0xffffff
    return v - (1 << 24) if v >> 23 else v


def _val(t):
    return t.name if isinstance(t, Atom) else t.v if isinstance(t, Int) \
        else t.text if isinstance(t, Raw) else id(t)


class Render:
    def __init__(self):
        self.names = {}
        self.count = collections.Counter()

    def scan(self, t, depth=0):
        t = deref(t)
        if isinstance(t, Var):
            self.count[id(t)] += 1
        elif isinstance(t, (Vec, Lst)) and depth < 60:
            for e in t.elems:
                if e is not None:
                    self.scan(e, depth + 1)
            if isinstance(t, Vec) and not isinstance(t.size, int) \
                    and t.size is not None and not isinstance(deref(t.size), Int):
                self.scan(t.size, depth + 1)

    def t(self, t, depth=0):
        t = deref(t)
        if t is None:
            return '_'
        if depth > 60:
            return '...'
        if isinstance(t, Var):
            if self.count[id(t)] <= 1 and t.hint is None:
                return '_'
            if id(t) not in self.names:
                self.names[id(t)] = _varname(len(self.names))
            return self.names[id(t)]
        if isinstance(t, Atom):
            return t.name if re.fullmatch(r'[a-z][A-Za-z0-9_]*|\[\]', t.name) \
                else "'%s'" % t.name
        if isinstance(t, Int):
            return str(t.v)
        if isinstance(t, Raw):
            return t.text
        if isinstance(t, Lst):
            out, cur, n = [], t, 0
            while isinstance(cur, Lst) and n < 200:
                out.append(self.t(cur.elems[0], depth + 1))
                cur = deref(cur.elems[1]) if cur.elems[1] is not None else None
                n += 1
            if isinstance(cur, Atom) and cur.name == '[]':
                return '[%s]' % ', '.join(out)
            return '[%s|%s]' % (', '.join(out), self.t(cur, depth + 1))
        if isinstance(t, Vec):
            size = t.size
            if size is not None and not isinstance(size, int):
                size = deref(size)
                size = size.v if isinstance(size, Int) else None
            es = list(t.elems)
            if size is not None:
                es += [None] * (size - len(es))
            parts = [self.t(e, depth + 1) for e in es]
            first = deref(es[0]) if es and es[0] is not None else None
            if size is None:
                if not parts:
                    if id(t) not in self.names:
                        self.names[id(t)] = _varname(len(self.names))
                    return self.names[id(t)]
                return '{%s ...}' % ', '.join(parts)
            if isinstance(first, Atom) and len(es) > 1 and \
                    re.fullmatch(r'[a-z][A-Za-z0-9_]*', first.name):
                return '%s(%s)' % (first.name, ', '.join(parts[1:]))
            return '{%s}' % ', '.join(parts)
        return '?'

    def goal(self, g):
        name, args = g[0], g[1]
        a = [self.t(x) for x in args]
        if name == '=':
            s = '%s = %s' % (a[0], a[1])
        elif name in INFIX:
            s = '%s %s %s' % (a[0], INFIX[name], a[1])
        elif (name[2:] if name.startswith('b_') else name) in ARITH \
                and len(a) == 3:
            s = '%s := %s %s %s' % (
                a[2], a[0], ARITH[name[2:] if name.startswith('b_') else name], a[1])
        else:
            s = '%s(%s)' % (name, ', '.join(a)) if a else name
        if len(g) > 2 and g[2]:
            s += '@%s(%s)' % (g[2][0], self.t(g[2][1]))
        return s

    def clause(self, name, st):
        for h in st.head:
            self.scan(h)
        for g in st.guard + st.body:
            for x in g[1]:
                self.scan(x)
            if len(g) > 2 and g[2]:
                self.scan(g[2][1])
        head = '%s(%s)' % (name, ', '.join(self.t(h) for h in st.head)) \
            if st.head else name
        guard = ', '.join(
            self.goal(g) for g in st.guard
            if not (g[0] in GUARD_TYPE and
                    isinstance(deref(g[1][0]), (Atom, Int, Raw)))) or 'true'
        body = ',\n    '.join(self.goal(g) for g in st.body) or 'true'
        body += ''.join('\n    %% %s' % n for n in st.notes)
        return head, guard, body


def _varname(i):
    return chr(ord('A') + i % 26) + (str(i // 26) if i >= 26 else '')


# --- fidelity against source ----------------------------------------------
def source_clauses(suffix):
    """{name/arity: clause count} of a .kl1 file in pimos.tar.Z, by a
    crude reader: comments and quoted text removed, clauses split at a
    full stop followed by white space, the head's arity counted at
    bracket depth 1."""
    import io
    import subprocess
    import tarfile
    raw = subprocess.run(['gzip', '-dc', bltdir.TAR], stdout=subprocess.PIPE,
                         check=True).stdout
    text = None
    with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
        for m in tf.getmembers():
            if m.name.endswith(suffix):
                text = tf.extractfile(m).read().decode('latin1')
    if text is None:
        raise KeyError(suffix)
    text = re.sub(r'"(?:[^"\\\n]|\\.|"")*"', '""', text)
    text = re.sub(r"'(?:[^'\n]|'')*'", 'q', text)
    text = re.sub(r'%.*', '', text)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    out = collections.Counter()
    for cl in re.split(r'\.(?:\s+|$)', text):
        cl = cl.strip()
        if not cl or cl.startswith(':-') or cl == 'otherwise' \
                or cl == 'alternatively':
            continue
        m = re.match(r'([a-z][A-Za-z0-9_]*)\s*(\(?)', cl)
        if not m:
            continue
        ar = 0
        if m.group(2):
            depth, ar = 0, 1
            for ch in cl[m.end() - 1:]:
                if ch in '([{':
                    depth += 1
                elif ch in ')]}':
                    depth -= 1
                    if depth == 0:
                        break
                elif ch == ',' and depth == 1:
                    ar += 1
        out['%s/%d' % (m.group(1), ar)] += 1
    return out


def fidelity(dc, modname, suffix):
    src = source_clauses(suffix)
    m = [m for m in dc.im.mods if m['name'] == modname][0]
    rows = []
    for name, _ln, _a in m['preds']:
        cl, trunc = dc.predicate(modname, name)
        rows.append((name, len(cl), src.get(name), trunc))
    return rows, src


def main(argv):
    dc = Decomp()
    d, im = dc.d, dc.im
    if '--check' in argv:
        preds = ok = 0
        labels = bad_labels = 0
        for m in im.mods:
            for name, ln, addr in m['preds']:
                preds += 1
                starts = d.sweep(addr, ln)
                if starts is None:
                    print('sweep fails: %s:%s' % (m['name'], name))
                    continue
                ok += 1
                ss = set(starts)
                for a in starts:
                    nm, _ty = d.name(a)
                    if nm in kbndis.LABEL_OPS and nm not in (
                            'suspend', 'otherwise'):
                        labels += 1
                        tgt = d.label(a)
                        if addr <= tgt < addr + ln and tgt not in ss:
                            bad_labels += 1
        print('sweep: %d of %d predicates end exactly; %d labels, %d inside '
              'their predicate but off an instruction boundary'
              % (ok, preds, labels, bad_labels))
        total = trunc = clauses = 0
        for m in im.mods:
            for name, _ln, _a in m['preds']:
                cl, tr = dc.predicate(m['name'], name)
                total += 1
                trunc += tr
                clauses += len(cl)
        names = len(dc.seen)
        unk = sorted(k for k in dc.unknown)
        print('decompiled: %d predicates, %d clauses, %d truncated; '
              '%d instruction names met, not handled or direction '
              'unknown: %s' % (total, clauses, trunc, names, unk))
        print('%-16s %5s %7s %7s %7s  %s' % (
            'module', 'preds', 'in src', 'equal', 'differ', 'source'))
        for modname, suffix in SOURCES.items():
            rows, src = fidelity(dc, modname, suffix)
            insrc = [r for r in rows if r[2] is not None]
            eq = [r for r in insrc if r[1] == r[2]]
            print('%-16s %5d %7d %7d %7d  %s' % (
                modname, len(rows), len(insrc), len(eq),
                len(insrc) - len(eq), suffix))
        return 0
    if '--fidelity' in argv:
        i = argv.index('--fidelity')
        rows, src = fidelity(dc, argv[i + 1], argv[i + 2])
        for name, n, s, tr in rows:
            print('%-34s decompiled %3d  source %s%s' % (
                name, n, '-' if s is None else s, '  TRUNCATED' if tr else ''))
        return 0
    args = [a for a in argv if not a.startswith('--')]
    if not args:
        print(__doc__)
        return 1
    m = [m for m in im.mods if m['name'] == args[0]]
    if not m:
        print('no module %s' % args[0])
        return 1
    for name, ln, addr in m[0]['preds']:
        if len(args) > 1 and name != args[1]:
            continue
        cl, tr = dc.predicate(args[0], name)
        print('%% %s:%s  @%d, %d cells%s' % (
            args[0], name, addr, ln, '  (TRUNCATED)' if tr else ''))
        level = 0
        for lv, _i, text, sep in cl:
            while level < lv:
                print('%s.' % sep[level])
                level += 1
            print(text)
    if dc.unknown:
        print('%% not handled: %s' % dict(dc.unknown))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
