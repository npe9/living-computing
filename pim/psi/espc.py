#!/usr/bin/env python3
"""An ESP compiler producing KL0 code and class templates: step 3 of the
SIMPOS route (docs/simpos/README.md §5).  OURS throughout: ICOT's ESP
compiler is lost, and nothing here is a copy of it.

    python3 -I psi/espc.py compile FILE.esp [--package P] [--listing]
    python3 -I psi/espc.py check [paragraph|kappa2|utter ...] [--tsv OUT]
    python3 -I psi/espc.py behave             compiled paragraph classes against paragraph.ptf

WHAT IT PRODUCES

The same in-memory form the loader (psi/librarian.py) builds from a .ptf:
a `Template` per class (natures, slot triples with their flags, the class,
instance and local predicates with their header kinds, the referenced
classes) whose predicates carry KL0 cells numbered as the loader numbers
them (pool constants from cell 13, after the 13 trailer terms; each
predicate's code after its 4 header cells).  The template also carries
its own constant pool (`Template.pool`), which psi/kl0.py uses instead of
reading a held record.  Templates are added to a `Librarian` and run by
`kl0.Machine` like loaded ones.

WHAT IT MAY EMIT

Only opcodes with a row in psi/kl0_opcodes.tsv, and only in the operand
patterns those rows say were witnessed (`Asm` checks every cell
against the table).  A construct that would need anything else is refused
with `CompileRefusal(construct, detail)`, naming the construct: e.g. `X+Y`
on two registers (no witnessed register add), a vector of four or more
elements built in a body (no witnessed put_vector_n), `=\\=` (no witness of
what it compiles to), a negative integer immediate (sign unwitnessed).

THE LANGUAGE (layers/ESP.md; TM-388 App. A grammar)

Parsed with the census reader (asm/simpos_census/esplex.py, the PRG
operator table, and espscan.parse_file's class splitter and include and
add_operator handling).  Compiled: class and instance slots (attribute,
component, `:= constant`, `is Class`, `(S := V :- Goals)`), natures with
`*`, class and instance methods, before and after demons, local
predicates, body disjunctions (as `$or$N` local predicates, kind 0x12),
cut, method sends `:m(R,...)`, slot access `O!s` and `O!s := V`, the
comparison macros, immediate arithmetic, and the constant macros `#C`,
`#"c"` and `R#"digits"`, and `with_macro` banks' plain clause-level rules
`Pattern => Expansion` (TM-388 §3.7.3; see "macro banks" below).  Not
compiled (refused by name): bank rules with when/where/with/by/`:-`, `==>`
and inserta/insertz (refused per predicate, 'macro rule'), `->`,
`not`/`\\+`, `Class:m(...)` and `:Class:m(...)`, other constant macros
(`key#`, `mouse#`, ...), floats.

CODE SHAPE (OURS, shaped on the held code; see psi/README.md "The ESP
compiler" for what was measured)

- Registers: a method's receiver is the last argument register (A n-1)
  and the other arguments A0..A n-2 (MEASURED, psi/kl0.py); a local's
  arguments A0..  Temporaries are allocated target-first: a value that is
  an argument of the chunk's call goes into that argument's register when
  it is free, else into the lowest free register that is not a pending
  argument register; a scratch register (a slot name) is the lowest free
  one.  Arguments are put in descending register order, a live value in
  the way being moved first.  These rules reproduce the held cells of
  e.g. list_index_buffer get_contents/2 and icon_button set_position/3.
- Permanent variables (in two or more chunks) live in Y, numbered head
  arguments first (register order), then in order of first occurrence;
  the environment is allocated lazily, before the first instruction that
  needs it.
- Clauses: try_me_else / retry_me_else / trust_me (e4/e2/e0) chains, no
  first-argument indexing (the held code indexes; counted as a class of
  difference).
- Cut (MEASURED over paragraph and kappa, 2026-11-24): dc n=arity as the
  first goal; d2 as the last goal and d0 elsewhere without an
  environment; d5 for `!, fail` at the end; with an environment, d1
  (before any call) or d3 (after one) with n = the environment size, and
  d4 with n = 8 + the size as the last goal.

CHECKS (psi/test_espc.py pins them)

- `check`: per class, natures, slots and flags, the declared method and
  local sets (refused ones included) and the demon set against the held
  template; per predicate, the compiled cells against the held cells in a
  position-independent form, each pair classified (exact, registers only,
  moves and environment, clause order, indexing, held uses an opcode with
  no row in the table, other).  A `$or$N` is matched by where it is
  called from (`parent#k`), not by N: the held numbering is not the
  source's order.
- `behave`: the compiled paragraph classes alone in a library against
  paragraph.ptf alone: test_kl0.py's calls, then kl0's census of the
  .ptf's methods called the same way on the compiled classes.
- `standins()`: psi/standin/*.esp compiled into package `simpos` and
  flagged, so kl0 refuses a method a stand-in lacks as a SIMPOS call.
"""
import collections
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'asm'))
sys.path.insert(0, os.path.join(HERE, '..', 'asm', 'simpos_census'))
import esplex  # noqa: E402
import espscan  # noqa: E402
import ptfdump as P  # noqa: E402
import librarian as LB  # noqa: E402

sys.setrecursionlimit(50000)
TSV = os.path.join(HERE, 'kl0_opcodes.tsv')


class CompileRefusal(Exception):
    """A construct the compiler will not translate (no witnessed opcode,
    or not modelled).  CONSTRUCT is a short name, ranked in reports."""

    def __init__(self, construct, detail=''):
        Exception.__init__(self, '%s: %s' % (construct, detail))
        self.construct, self.detail = construct, detail


# --------------------------------------------------------------------------
# the opcode table: what may be emitted

def witnessed():
    import csv
    with open(TSV) as f:
        rows = [r for r in csv.DictReader(f, delimiter='\t') if r['witness'].strip()]
    return {(r['class'], r['opcode']): r['mnemonic'] for r in rows}


WITNESSED = witnessed()


# --------------------------------------------------------------------------
# terms (esplex nodes are lists: [kind, payload..., line])

def kind(t):
    return t[0]


def is_var(t):
    return t[0] == 'var'


def is_void(t):
    return t[0] == 'var' and t[1] == '_'


def atom_name(t):
    return t[1] if t[0] in ('atom', 'qatom') else None


def num_value(t):
    """An integer literal, or None (floats and 0'c refused elsewhere)."""
    if t[0] != 'num':
        return None
    s = t[1]
    try:
        return int(s)
    except ValueError:
        pass
    if s.startswith("0'") and len(s) == 3:
        return jis_code(s[2])
    raise CompileRefusal('float constant', s)


_PUNCT_INV = {v: k for k, v in P.PUNCT.items()}


def jis_code(c):
    """The 16-bit JIS code of one character, as ptfdump.ch decodes it:
    0x23xx for ASCII letters and digits, 0x21xx for the punctuation table,
    the JIS X 0208 code (EUC-JP bytes less 0x8080) otherwise."""
    if c.isascii() and c.isalnum():
        return 0x2300 | ord(c)
    if c in _PUNCT_INV:
        return 0x2100 | _PUNCT_INV[c]
    try:
        b = c.encode('euc_jp')
    except UnicodeEncodeError:
        raise CompileRefusal('character', 'no JIS code for %r' % c)
    if len(b) != 2:
        raise CompileRefusal('character', 'no two-byte JIS code for %r' % c)
    return (b[0] & 0x7f) << 8 | (b[1] & 0x7f)


def jis_text(s):
    """A source string as the loader reads the held one back (ptfdump.ch
    of each 16-bit JIS cell)."""
    return ''.join(P.ch(jis_code(c)) for c in s)


def flat(t, op=','):
    if t is not None and t[0] == 'cmp' and t[1] == op and len(t[2]) == 2:
        return flat(t[2][0], op) + flat(t[2][1], op)
    return [] if t is None else [t]


def vars_of(t, acc=None):
    """Named variables of T in order of first occurrence ('_' excluded)."""
    if acc is None:
        acc = []
    k = t[0]
    if k == 'var':
        if t[1] != '_' and t[1] not in acc:
            acc.append(t[1])
    elif k == 'cmp':
        for a in t[2]:
            vars_of(a, acc)
    elif k == 'list':
        for a in t[1]:
            vars_of(a, acc)
        if t[2] is not None:
            vars_of(t[2], acc)
    elif k == 'brace':
        vars_of(t[1], acc)
    return acc


def var_count(t, acc):
    k = t[0]
    if k == 'var':
        if t[1] != '_':
            acc[t[1]] += 1
    elif k == 'cmp':
        for a in t[2]:
            var_count(a, acc)
    elif k == 'list':
        for a in t[1]:
            var_count(a, acc)
        if t[2] is not None:
            var_count(t[2], acc)
    elif k == 'brace':
        var_count(t[1], acc)
    return acc


# --------------------------------------------------------------------------
# macro banks (TM-388 §3.7.3 pp.72-75, PDF pp.84-87)
#
# SOURCED: a class `with_macro Bank` has its clauses expanded by the bank's
# clause-level macros, which apply "for an argument of the head part ...
# and for a goal and its argument of the body part" (p.72); a rule is
# `Pattern => Expansion [when G] [where T] [with Clauses] [by Obj] [:- Cond]`
# (p.73); with no when/where the pattern is simply replaced (p.62, p.74);
# a bank inherits the banks of its `nature` (p.74).  Expansion is top-down
# (TM-388 §3.7, layers/ESP.md §7): a term is tried before its arguments.
# MEASURED (kappa2, 2026-11-24): 3,895 of its rules are plain `P => E`
# (3,811 of them `@name => constant`); 15 carry `:-` and one is `==>`.
# OURS: rules are tried in the bank's own order, then its natures'
# (depth first, first rule wins); a matched term's expansion is expanded
# again; variables of an expansion that the pattern does not bind are
# renamed apart per use; slot initial values and slot-initialisation
# bodies are expanded like clause arguments.  A rule with a tail (when,
# where, with, by, `:-`) or a class-level `==>` rule is not modelled: a
# predicate whose clause matches one is refused ('macro rule'); so is a
# back-quoted term (expansion suppressed, p.71: unmodelled).

MACRO_TAILS = ('when', 'where', 'with', 'by', ':-')


def term_key(t):
    """The principal functor of a source term, for rule lookup."""
    k = t[0]
    if k == 'cmp':
        return ('cmp', t[1], len(t[2]))
    if k in ('atom', 'qatom'):
        return ('atom', t[1])
    if k in ('num', 'str'):
        return (k, t[1])
    if k == 'list':
        return ('list',)
    if k == 'brace':
        return ('brace',)
    return None


def macro_match(p, t, b):
    """One-way match of rule pattern P against term T, binding P's
    variables in B (a dict).  -> True/False."""
    k = p[0]
    if k == 'var':
        if p[1] == '_':
            return True
        if p[1] in b:
            return strip_lines(b[p[1]]) == strip_lines(t)
        b[p[1]] = t
        return True
    if t[0] == 'var':
        return False
    if k in ('atom', 'qatom'):
        return t[0] in ('atom', 'qatom') and t[1] == p[1]
    if k in ('num', 'str'):
        return t[0] == k and t[1] == p[1]
    if k == 'cmp':
        return (t[0] == 'cmp' and t[1] == p[1] and len(t[2]) == len(p[2])
                and all(macro_match(x, y, b) for x, y in zip(p[2], t[2])))
    if k == 'list':
        if t[0] != 'list' or len(t[1]) != len(p[1]):
            return False
        if not all(macro_match(x, y, b) for x, y in zip(p[1], t[1])):
            return False
        if p[2] is None or t[2] is None:
            return p[2] is None and t[2] is None
        return macro_match(p[2], t[2], b)
    if k == 'brace':
        return t[0] == 'brace' and macro_match(p[1], t[1], b)
    return False


def strip_lines(t):
    k = t[0]
    if k == 'cmp':
        return ('cmp', t[1], tuple(strip_lines(a) for a in t[2]))
    if k == 'list':
        return ('list', tuple(strip_lines(a) for a in t[1]),
                None if t[2] is None else strip_lines(t[2]))
    if k == 'brace':
        return ('brace', strip_lines(t[1]))
    return (k, t[1])


def macro_subst(t, b, fresh):
    k = t[0]
    if k == 'var':
        if t[1] == '_':
            return t
        if t[1] in b:
            return b[t[1]]
        if t[1] not in fresh:
            fresh[t[1]] = ['var', '_M%d_%s' % (len(fresh) + MacroBank.serial[0], t[1]), t[-1]]
        return fresh[t[1]]
    if k == 'cmp':
        return ['cmp', t[1], [macro_subst(a, b, fresh) for a in t[2]], t[-1]]
    if k == 'list':
        return ['list', [macro_subst(a, b, fresh) for a in t[1]],
                None if t[2] is None else macro_subst(t[2], b, fresh), t[-1]]
    if k == 'brace':
        return ['brace', macro_subst(t[1], b, fresh), t[-1]]
    return t


class MacroBank:
    """The clause-level rules of a bank and its natures, in lookup order."""
    serial = [0]

    def __init__(self, name, banks):
        self.name = name
        self.rules = collections.defaultdict(list)    # key -> [(pattern, expansion, plain, where)]
        seen = []

        def visit(n):
            if n in seen:
                return
            seen.append(n)
            d = banks.get(n)
            if d is None:
                if n != 'esp_macro_expander':
                    raise CompileRefusal('with_macro', 'macro bank %s not held' % n)
                return
            for r in d.get('macros', []):
                self.add(r, n)
            for _pkg, nat in d.get('natures') or []:
                visit(nat)
            if d.get('macro_bank'):
                visit(d['macro_bank'][1])
        visit(name)
        self.banks = seen

    def add(self, r, bank):
        t, tails = r, []
        while t[0] == 'cmp' and t[1] in MACRO_TAILS and len(t[2]) == 2:
            tails.append(t[1])
            t = t[2][0]
        if t[0] == 'cmp' and t[1] in ('=>', '==>') and len(t[2]) == 2:
            pat, exp = t[2]
            plain = t[1] == '=>' and not tails
            key = term_key(pat)
            if key is not None:
                self.rules[key].append((pat, exp, plain, bank))

    def expand(self, t, depth=0):
        """T with every rule applied top-down -> new term (CompileRefusal
        for an unmodelled rule form)."""
        if depth > 60:
            raise CompileRefusal('macro rule', 'expansion over 60 deep at %s' % (term_key(t),))
        k = t[0]
        if k == 'cmp' and t[1] in ('`', '``'):
            raise CompileRefusal('macro rule', 'back-quoted term (expansion suppressed)')
        for pat, exp, plain, bank in self.rules.get(term_key(t), ()):
            b = {}
            if macro_match(pat, t, b):
                if not plain:
                    raise CompileRefusal('macro rule', '%s rule with when/where/:- (bank %s)' % (
                        '%s/%d' % term_key(t)[1:] if term_key(t)[0] == 'cmp' else term_key(t)[-1], bank))
                MacroBank.serial[0] += 100
                return self.expand(macro_subst(exp, b, {}), depth + 1)
        if k == 'cmp':
            return ['cmp', t[1], [self.expand(a, depth) for a in t[2]], t[-1]]
        if k == 'list':
            return ['list', [self.expand(a, depth) for a in t[1]],
                    None if t[2] is None else self.expand(t[2], depth), t[-1]]
        if k == 'brace':
            return ['brace', self.expand(t[1], depth), t[-1]]
        return t


# --------------------------------------------------------------------------
# source terms to values

ARITH = ('+', '-', '*', '/')


class Unit:
    """A compile unit: the classes of one package (for name qualification)."""

    def __init__(self, package, known=None, banks=None):
        self.package = package
        self.local_classes = set()
        self.known = dict(known or {})    # unqualified name -> qualified id (other packages)
        self.banks = dict(banks or {})    # macro bank name -> its parsed definition
        self.bank_cache = {}

    def bank(self, name):
        b = self.bank_cache.get(name)
        if b is None:
            b = self.bank_cache[name] = MacroBank(name, self.banks)
        return b

    def qualify(self, pkg, name):
        if name == '*':
            return '*'
        if pkg:
            return '%s##%s' % (pkg, name)
        if name in self.local_classes:
            return '%s##%s' % (self.package, name)
        if name in self.known:
            return self.known[name]
        return 'simpos##%s' % name


def classify(t, unit):
    """A term in a body or head position -> a value description:
    ('var', name) ('void',) ('atom', n) ('int', v) ('str', s) ('class', id)
    ('list', [items], tail) ('vec', [items]) ('slot', obj, name)
    ('arith', op, a, b)."""
    k = t[0]
    if k == 'var':
        return ('void',) if t[1] == '_' else ('var', t[1])
    if k in ('atom', 'qatom'):
        return ('atom', t[1])
    if k == 'num':
        return ('int', num_value(t))
    if k == 'str':
        return ('str', jis_text(t[1]))
    if k == 'list':
        items = [classify(x, unit) for x in t[1]]
        tail = classify(t[2], unit) if t[2] is not None else ('atom', '[]')
        return ('list', items, tail)
    if k == 'brace':
        return ('vec', [classify(x, unit) for x in flat(t[1])])
    if k == 'cmp':
        f, args = t[1], t[2]
        if f == '#' and len(args) == 1:
            a = args[0]
            if a[0] == 'str':
                if len(a[1]) != 1:
                    raise CompileRefusal('character constant', '#"%s" is not one character' % a[1])
                return ('int', jis_code(a[1]))
            nm = espscan.name_of(a)
            if nm:
                return ('class', unit.qualify(nm[0], nm[1]))
            raise CompileRefusal('#macro', 'unrecognised #%r' % (a[:2],))
        if f == '#' and len(args) == 2:
            a, b = args
            if a[0] == 'num' and b[0] == 'str':
                return ('int', int(b[1], int(a[1])))
            if atom_name(a) == 'string' and b[0] == 'str':
                return ('str', jis_text(b[1]))
            raise CompileRefusal('constant macro %s#' % (atom_name(a) or a[0]), 'no value table held')
        if f == '!' and len(args) == 2:
            nm = atom_name(args[1])
            if nm is None:
                raise CompileRefusal('dynamic slot name', 'Obj!X with X not an atom')
            return ('slot', classify(args[0], unit), nm)
        if f in ARITH and len(args) == 2:
            return ('arith', f, classify(args[0], unit), classify(args[1], unit))
        if f == '-' and len(args) == 1:
            v = classify(args[0], unit)
            if v[0] == 'int':
                return ('int', -v[1])
            raise CompileRefusal('arithmetic -X', 'unary minus on a non-constant (no witnessed opcode)')
        # a compound term f(a,...) is the vector {f,a,...} (TM-388 p.26)
        return ('vec', [('atom', f)] + [classify(x, unit) for x in args])
    raise CompileRefusal('term', 'unrecognised term kind %r' % (k,))


def ground(v):
    k = v[0]
    if k in ('atom', 'int', 'str', 'class'):
        return True
    if k == 'list':
        return all(ground(x) for x in v[1]) and ground(v[2])
    if k == 'vec':
        return all(ground(x) for x in v[1])
    return False


def pool_term(v):
    """A ground value as the raw pool term kl0.build reads."""
    k = v[0]
    if k == 'atom':
        return ('atom', v[1])
    if k == 'int':
        return ('int', v[1] & 0xffffffff)
    if k == 'str':
        return ('str', v[1])
    if k == 'class':
        return ('classref', v[1])
    if k == 'vec':
        return ('vec', [pool_term(x) for x in v[1]])
    if k == 'list':
        out = pool_term(v[2])
        for x in reversed(v[1]):
            out = ('list', pool_term(x), out)
        return out
    raise CompileRefusal('pool', 'not a constant: %r' % (k,))


def value_vars(v, acc):
    k = v[0]
    if k == 'var':
        acc[v[1]] += 1
    elif k in ('list',):
        for x in v[1]:
            value_vars(x, acc)
        value_vars(v[2], acc)
    elif k == 'vec':
        for x in v[1]:
            value_vars(x, acc)
    elif k == 'slot':
        value_vars(v[1], acc)
    elif k == 'arith':
        value_vars(v[2], acc)
        value_vars(v[3], acc)
    return acc


def small(v):
    return isinstance(v, int) and 0 <= v < 0x8000


# --------------------------------------------------------------------------
# goals

BUILTINS = {
    # name/arity: (blt opcode, operand roles) -- roles: 'in' an input
    # register, 'out' an output register.  Each from a witnessed row.
    ('new_heap_vector', 2): ('19', ('out', 'in')),      # V = N only
    ('first', 2): ('21', ('in', 'out')),
    ('second', 2): ('22', ('in', 'out')),
    ('vector_element', 3): ('20', ('in', 'in', 'out')),
    ('set_vector_element', 3): ('28', ('in', 'in', 'in')),
    ('set_first', 2): ('29', ('in', 'in')),
    ('set_second', 2): ('2a', ('in', 'in')),
}
# comparison macros: source operator -> (blt opcode, swap operands)
# (witnessed by source text, not by mnemonic: kl0_opcodes.tsv rows 62,
# 65, 66, 67; `X =< Y` compiles to `67 Y X`, p_icon.esp `Y=<Icon!height/2`)
COMPARE = {'==': ('62', False), '\\==': ('65', False), '<': ('66', False),
           '>': ('66', True), '=<': ('67', True), '>=': ('67', False)}
UNWITNESSED_GOALS = {'=:=', '=\\=', '@<', '@>', '@=<', '@>=', '=..'}


class Goal:
    def __init__(self, kind, **kw):
        self.kind = kind
        self.__dict__.update(kw)

    def __repr__(self):
        return '<goal %s>' % self.kind


# --------------------------------------------------------------------------
# emission

class Asm:
    """Instructions of one predicate, before layout.  Each item is
    ('cell', tag, lo, value) | ('local', op, a, pred_key) | ('choice', op,
    a, label) | ('pool', op, a, term) | ('sym', tag, lo, name) | ('label', L)."""

    def __init__(self):
        self.items = []
        self.nlabel = 0

    def label(self):
        self.nlabel += 1
        return self.nlabel

    def place(self, lab):
        self.items.append(('label', lab))

    def _check(self, cls, op, mn=None):
        if (cls, '%02x' % op) not in WITNESSED:
            raise CompileRefusal('opcode', '%s %02x has no witnessed row' % (cls, op))

    def pmi(self, op, a=0, b=0, c=0):
        self._check('pmi', op)
        for x in (a, b, c):
            if not 0 <= x < 256:
                raise CompileRefusal('register', 'operand %d out of range' % x)
        self.items.append(('cell', 0x20, 0, op << 24 | a << 16 | b << 8 | c))

    def pmi16(self, op, a, imm):
        self._check('pmi', op)
        if not 0 <= imm < 0x8000:
            raise CompileRefusal('integer immediate', '%d: only 0..0x7fff witnessed' % imm)
        self.items.append(('cell', 0x20, 0, op << 24 | a << 16 | imm))

    def blt(self, op, a=0, b=0, c=0):
        self._check('blt', op)
        for x in (a, b, c):
            if not 0 <= x < 256:
                raise CompileRefusal('register', 'operand %d out of range' % x)
        self.items.append(('cell', 0x21, 0, op << 24 | a << 16 | b << 8 | c))

    def atom(self, mode, reg, name):
        # atom cells: get 60rr (rr < 0x4c), unify 604c, put 60(80|r)
        key = {'get': 'get', 'unify': 'unify', 'put': 'put'}[mode]
        if ('atom', key) not in WITNESSED:
            raise CompileRefusal('opcode', 'atom cell %s' % key)
        if mode == 'get':
            if reg >= 0x4c:
                raise CompileRefusal('register', 'get_atom on A%d (>= 0x4c is the unify form)' % reg)
            lo = reg
        elif mode == 'unify':
            lo = 0x4c
        else:
            if reg >= 0x80:
                raise CompileRefusal('register', 'put_atom on A%d' % reg)
            lo = 0x80 | reg
        self.items.append(('sym', 0x60, lo, name))

    def selector(self, name, arity):
        self.items.append(('sym', 0x01, arity, name))

    def local(self, op, a, key):
        self._check('pmi', op)
        self.items.append(('local', op, a, key))

    def choice(self, op, a, lab):
        self._check('pmi', op)
        self.items.append(('choice', op, a, lab))

    def pool(self, op, a, term):
        self._check('pmi', op)
        self.items.append(('pool', op, a, term))


# --------------------------------------------------------------------------
# the clause compiler

class Clause:
    """One clause: head argument values in register order, body goals."""

    def __init__(self, head, goals, src=None):
        self.head, self.goals, self.src = head, goals, src


class PredDef:
    def __init__(self, name, arity, kind, clauses=None, label=None):
        self.name, self.arity, self.kind = name, arity, kind
        self.clauses = clauses or []
        self.label = label
        self.refusal = None

    @property
    def key(self):
        return (self.name, self.arity, self.kind)


class Regs:
    """Register state of one chunk: holder[r] = ('var', name) | ('val', id)
    | ('perm', name) (a cached copy of a Y variable) | None."""

    def __init__(self):
        self.holder = {}
        self.where = {}           # var name -> register (temporaries and cached Y)
        self.remaining = collections.Counter()   # uses left in the chunk
        self.pending = set()      # argument registers of the chunk's call not yet placed

    def live(self, r):
        h = self.holder.get(r)
        if h is None:
            return False
        if h[0] == 'var':
            return self.remaining[h[1]] > 0
        if h[0] in ('val', 'pvar'):
            return True
        return False              # a cached Y copy can always be reloaded

    def free(self, r):
        return not self.live(r)

    def lowest(self, avoid=()):
        r = 0
        while not self.free(r) or r in avoid:
            r += 1
        return r

    def set(self, r, h):
        old = self.holder.get(r)
        if old is not None and old[0] in ('var', 'perm', 'pvar') and self.where.get(old[1]) == r:
            del self.where[old[1]]
        self.holder[r] = h
        if h is not None and h[0] in ('var', 'perm', 'pvar'):
            self.where[h[1]] = r

    def drop(self, r):
        self.set(r, None)


class PredCompiler:
    def __init__(self, cc, pred):
        self.cc, self.pred = cc, pred
        self.asm = Asm()

    def compile(self):
        cl = self.pred.clauses
        n = len(cl)
        labels = [self.asm.label() for _ in cl]
        for i, c in enumerate(cl):
            if n > 1:
                self.asm.place(labels[i])
                if i == 0:
                    self.asm.choice(0xe4, self.pred.arity, labels[1])
                elif i < n - 1:
                    self.asm.choice(0xe2, 0, labels[i + 1])
                else:
                    self.asm.pmi(0xe0)
            ClauseCompiler(self, c).compile()
        return self.asm


class ClauseCompiler:
    def __init__(self, pc, clause):
        self.pc, self.cc, self.asm = pc, pc.cc, pc.asm
        self.clause = clause
        self.arity = pc.pred.arity

    # -- analysis -----------------------------------------------------------
    def analyse(self):
        goals = self.clause.goals
        self.chunk_of_goal = []
        chunk = 0
        occ = collections.defaultdict(set)
        counts = collections.defaultdict(collections.Counter)    # chunk -> var -> n
        for v in self.clause.head:
            for name, k in value_vars(v, collections.Counter()).items():
                occ[name].add(0)
                counts[0][name] += k
        self.ncalls = 0
        for g in goals:
            self.chunk_of_goal.append(chunk)
            for name, k in g.vars.items():
                occ[name].add(chunk)
                counts[chunk][name] += k
            if g.kind in ('call', 'send'):
                chunk += 1
                self.ncalls += 1
        self.counts = counts
        self.perm = [v for v in self._order(occ) if len(occ[v]) > 1]
        self.y = {v: i for i, v in enumerate(self.perm)}
        last_is_call = goals and goals[-1].kind in ('call', 'send')
        self.need_env = bool(self.perm) or self.ncalls > 1 or (self.ncalls == 1 and not last_is_call)
        self.env = False
        self.pending_perm = {}     # head arguments to save in Y at the allocate
        self.seen = set()          # variables already initialised
        self.unsafe = set()        # Y variables first made by put_variable_p, not yet used
        self.after_call = False

    def _order(self, occ):
        out = []
        for v in self.clause.head:
            for name in value_vars(v, collections.Counter()):
                if name not in out:
                    out.append(name)
        for g in self.clause.goals:
            for name in g.vars:
                if name not in out:
                    out.append(name)
        return out

    def ensure_env(self):
        if not self.env:
            if not self.need_env:
                raise CompileRefusal('internal', 'environment needed but not planned')
            self.asm.pmi(0x5f, len(self.perm))
            self.env = True
            # head arguments that are permanent are saved now (the held code
            # saves them at the allocate, after the first built-ins: e.g.
            # list_index_buffer $or$2/4 `66 00 04, d0, 5f 03, 20 01 00, 20 02 01`)
            for name in sorted(self.pending_perm, key=lambda v: self.y[v]):
                r = self.R.where.get(name)
                self.asm.pmi(0x20, r, self.y[name])
                self.R.set(r, ('perm', name))
            self.pending_perm = {}

    @property
    def envsize(self):
        return len(self.perm)

    # -- the chunk's register state ----------------------------------------
    def new_chunk(self, k, call=None):
        self.R = Regs()
        for name, n in self.counts.get(k, {}).items():
            if name not in self.y:
                self.R.remaining[name] = n
        self.targets = {}
        if call is not None:
            for i, a in enumerate(call.args):
                if a[0] == 'var' and a[1] not in self.y and a[1] not in self.targets:
                    self.targets[a[1]] = i
            self.R.pending = set(range(len(call.args)))

    def use(self, name):
        if name in self.y:
            return
        if self.R.remaining[name] > 0:
            self.R.remaining[name] -= 1

    # -- compile -----------------------------------------------------------
    def compile(self):
        self.analyse()
        goals = self.clause.goals
        first_call = next((g for g in goals if g.kind in ('call', 'send')), None)
        self.new_chunk(0, first_call)
        self.head()
        if not goals:
            return self.finish_proceed()
        for i, g in enumerate(goals):
            last = i == len(goals) - 1
            k = g.kind
            if k == 'cut':
                if self.cut(i, last) == 'stop' or last:
                    return
            elif k == 'fail':
                self.asm.pmi(0xfe)
                return
            elif k == 'true':
                if last:
                    return self.finish_proceed()
            elif k in ('call', 'send'):
                self.call(g, last)
                if last:
                    return
                self.after_call = True
                nxt = next((h for h in goals[i + 1:] if h.kind in ('call', 'send')), None)
                self.new_chunk(self.chunk_of_goal[i] + 1, nxt)
            else:
                self.inline(g)
                if last:
                    return self.finish_proceed()

    def finish_proceed(self):
        if self.env:
            self.asm.pmi(0xf1, 8 + self.envsize)
        else:
            self.asm.pmi(0xf0)

    def cut(self, i, last):
        goals = self.clause.goals
        if i + 1 < len(goals) and goals[i + 1].kind == 'fail' and i + 2 == len(goals):
            self.asm.pmi(0xd5)                     # !, fail
            return 'stop'
        if self.env:
            if last:
                self.asm.pmi(0xd4, 8 + self.envsize)
            elif self.after_call:
                self.asm.pmi(0xd3, self.envsize)
            else:
                self.asm.pmi(0xd1, self.envsize)
            return
        if last:
            self.asm.pmi(0xd2)
        elif i == 0 or all(g.kind in ('cut', 'true') for g in goals[:i]):
            self.asm.pmi(0xdc, self.arity)
        else:
            self.asm.pmi(0xd0)

    # -- head --------------------------------------------------------------
    def head(self):
        later = []
        for i, v in enumerate(self.clause.head):
            self.R.set(i, None)
        # first pass: which registers hold first-occurrence temporaries
        first = set()
        for i, v in enumerate(self.clause.head):
            if v[0] == 'var' and v[1] not in self.y and v[1] not in self.seen:
                self.seen.add(v[1])
                first.add(i)
                self.R.set(i, ('var', v[1]))
                self.use(v[1])
            elif v[0] == 'var' and v[1] not in self.y:
                pass
            else:
                self.R.set(i, ('val', ('arg', i)))
        for i, v in enumerate(self.clause.head):
            k = v[0]
            if i in first:
                continue
            if k == 'void':
                self.R.drop(i)
            elif k == 'var':
                name = v[1]
                if name in self.y:
                    if name not in self.seen:
                        self.seen.add(name)
                        self.pending_perm[name] = i
                        self.R.set(i, ('pvar', name))
                    elif name in self.pending_perm:
                        self.asm.pmi(0x23, i, self.R.where[name])
                        self.R.drop(i)
                    else:
                        self.ensure_env()
                        self.asm.pmi(0x22, i, self.y[name])
                        self.R.drop(i)
                elif self.R.holder.get(i) != ('var', name):
                    r = self.R.where[name]
                    self.asm.pmi(0x23, i, r)
                    self.use(name)
                    self.R.drop(i)
            else:
                self.get_value(i, v, later)
        while later:
            r, v = later.pop(0)
            self.get_value(r, v, later)

    def get_value(self, r, v, later):
        """Unify register R (get mode) with the non-variable value V.  R is
        free afterwards (a structure's elements are read by the unify
        instructions that follow)."""
        k = v[0]
        a = self.asm
        h = self.R.holder.get(r)
        if h is None or h[0] == 'val' or (h[0] == 'var' and not self.R.live(r)):
            self.R.drop(r)
        if k == 'atom':
            if v[1] == '[]':
                a.pmi(0x26, r)
            else:
                a.atom('get', r, v[1])
        elif k == 'int' and small(v[1]):
            a.pmi16(0x27, r, v[1])
        elif ground(v):
            a.pool(0x29, r, pool_term(v))
            self.note_refs(v)
        elif k == 'list':
            items, tail = v[1], v[2]
            car = items[0]
            cdr = ('list', items[1:], tail) if len(items) > 1 else tail
            if car[0] == 'var' and cdr[0] == 'var' and car[1] not in self.seen and cdr[1] not in self.seen \
                    and car[1] not in self.y and cdr[1] not in self.y and car[1] != cdr[1]:
                hr = self.R.lowest()
                self.R.set(hr, ('var', car[1]))
                tr = self.R.lowest()
                self.R.set(tr, ('var', cdr[1]))
                self.seen.update((car[1], cdr[1]))
                self.use(car[1])
                self.use(cdr[1])
                a.pmi(0x2b, r, hr, tr)
                return
            a.pmi(0x2a, r)
            self.unify_seq([car, cdr], later, list_cdr=True)
        elif k == 'vec':
            n = len(v[1])
            if n == 2:
                a.pmi(0x32, r)
            elif n == 3:
                a.pmi(0x33, r)
            else:
                a.pmi(0x37, r, 0, n)
            self.unify_seq(v[1], later)
        elif k == 'int':
            a.pool(0x29, r, pool_term(v))
        else:
            raise CompileRefusal('head term', 'a %s in a head' % k)

    def unify_seq(self, els, later, list_cdr=False):
        """unify_* instructions for the elements ELS of a structure being
        read (or, in a body, built).  A nested list in the last (cdr)
        position continues inline with unify_list."""
        a = self.asm
        j = 0
        while j < len(els):
            e = els[j]
            is_cdr = list_cdr and j == len(els) - 1
            k = e[0]
            if k == 'void':
                n = 1
                while j + n < len(els) and els[j + n][0] == 'void' and not (list_cdr and j + n == len(els) - 1):
                    n += 1
                a.pmi16(0x4b, 0, n)
                j += n
                continue
            if k == 'var':
                name = e[1]
                if name in self.y:
                    if name not in self.seen:
                        self.seen.add(name)
                        self.ensure_env()
                        a.pmi(0x40, self.y[name])
                    else:
                        self.ensure_env()
                        a.pmi(0x44, self.y[name])
                else:
                    if name not in self.seen:
                        self.seen.add(name)
                        r = self.R.lowest()
                        self.R.set(r, ('var', name))
                        a.pmi(0x41, r)
                        self.use(name)
                    else:
                        a.pmi(0x45, self.R.where[name])
                        self.use(name)
            elif k == 'atom':
                a.atom('unify', 0, e[1])
            elif k == 'int' and small(e[1]):
                a.pmi16(0x47, 0, e[1])
            elif k == 'list' and is_cdr and not ground(e):
                a.pmi(0x4a)
                items, tail = e[1], e[2]
                car = items[0]
                cdr = ('list', items[1:], tail) if len(items) > 1 else tail
                els = els[:j] + [car, cdr]
                list_cdr = True
                continue
            elif ground(e):
                a.pool(0x49, 0, pool_term(e))
                self.note_refs(e)
            elif k in ('list', 'vec'):
                r = self.R.lowest()
                self.R.set(r, ('val', ('nested', id(e))))
                a.pmi(0x41, r)
                later.append((r, e))
            else:
                raise CompileRefusal('head term', 'a %s inside a structure' % k)
            j += 1

    def note_refs(self, v):
        k = v[0]
        if k == 'class':
            self.cc.ref(v[1])
        elif k == 'vec':
            for x in v[1]:
                self.note_refs(x)
        elif k == 'list':
            for x in v[1]:
                self.note_refs(x)
            self.note_refs(v[2])

    # -- values into registers ---------------------------------------------
    def to_reg(self, v, prefer=None, scratch=False):
        """Code putting value V in a register; -> the register.  The
        register is marked as holding ('val', ...) until released."""
        a = self.asm
        k = v[0]
        R = self.R
        avoid = () if scratch else R.pending

        def pick():
            if prefer is not None and R.free(prefer):
                return prefer
            return R.lowest(avoid)
        if k == 'var':
            name = v[1]
            if name in self.y:
                if name not in self.seen:
                    raise CompileRefusal('unbound input', 'variable %s used before it is bound, as a built-in input' % name)
                r = R.where.get(name)
                if r is not None and R.holder.get(r) in (('perm', name), ('pvar', name)):
                    return r
                self.ensure_env()
                r = pick()
                op = 0xa4 if name in self.unsafe else 0xa2
                self.unsafe.discard(name)
                a.pmi(op, r, self.y[name])
                R.set(r, ('perm', name))
                return r
            if name not in self.seen:
                raise CompileRefusal('unbound input', 'variable %s used before it is bound, as a built-in input' % name)
            return R.where[name]
        if k == 'atom':
            r = pick()
            a.atom('put', r, v[1])
            R.set(r, ('val', id(v)))
            return r
        if k == 'int' and small(v[1]):
            r = pick()
            a.pmi16(0xa7, r, v[1])
            R.set(r, ('val', id(v)))
            return r
        if k == 'class':
            r = pick()
            a.pool(0xa9, r, pool_term(v))
            self.cc.ref(v[1])
            R.set(r, ('val', id(v)))
            return r
        if ground(v):
            r = pick()
            a.pool(0xa9, r, pool_term(v))
            self.note_refs(v)
            R.set(r, ('val', id(v)))
            return r
        if k == 'slot':
            return self.slot_get(v, prefer, avoid)
        if k == 'arith':
            return self.arith(v, prefer, avoid)
        if k in ('list', 'vec'):
            return self.build(v, prefer, avoid)
        raise CompileRefusal('value', 'cannot put a %s' % k)

    def consume(self, v, r):
        """V (just read from register R) has been used once."""
        if v[0] == 'var':
            self.use(v[1])
        elif self.R.holder.get(r) and self.R.holder[r][0] == 'val':
            self.R.drop(r)

    def slot_get(self, v, prefer, avoid):
        obj, name = v[1], v[2]
        o = self.to_reg(obj, scratch=True)
        R = self.R
        held = R.holder.get(o)
        R.set(o, ('val', 'obj'))     # keep it while the name goes in
        n = R.lowest()
        R.set(n, ('val', 'name'))
        self.asm.atom('put', n, name)
        R.set(o, held)
        self.consume(obj, o)
        R.drop(n)
        if prefer is not None and R.free(prefer):
            out = prefer
        else:
            out = R.lowest(avoid)
        self.asm.blt(0x27, o, n, out)
        R.set(out, ('val', id(v)))
        return out

    def arith(self, v, prefer, avoid):
        op, x, y = v[1], v[2], v[3]
        if x[0] == 'int' and y[0] == 'int':
            val = {'+': x[1] + y[1], '-': x[1] - y[1], '*': x[1] * y[1],
                   '/': x[1] // y[1] if y[1] else None}[op]
            if val is None:
                raise CompileRefusal('arithmetic', 'division by zero')
            return self.to_reg(('int', val), prefer)
        if op in ('+', '*') and x[0] == 'int' and y[0] != 'int':
            x, y = y, x
        imm = {'+': 0x45, '-': 0x46, '*': 0x48, '/': 0x49}
        if y[0] == 'int':
            if not 0 <= y[1] < 256:
                raise CompileRefusal('arithmetic immediate', '%s %d: only 0..255 witnessed' % (op, y[1]))
            r = self.dest(x, prefer, avoid)
            self.asm.blt(imm[op], r, y[1], r)
            return r
        if op == '-':
            yr = self.to_reg(y, scratch=False)
            held = self.R.holder.get(yr)
            self.R.set(yr, ('val', 'rhs'))
            r = self.dest(x, prefer, avoid)
            self.R.set(yr, held)
            self.asm.blt(0x41, r, yr, r)
            self.consume(y, yr)
            return r
        raise CompileRefusal('arithmetic X%sY' % op, 'on two registers (no witnessed opcode)')

    def dest(self, x, prefer, avoid):
        """A register holding X's value that may be overwritten (the
        witnessed arithmetic rows write their first operand)."""
        R = self.R
        if x[0] == 'var' and x[1] not in self.y:
            r = self.to_reg(x)
            self.use(x[1])
            if R.free(r) and (prefer is None or r == prefer or not R.free(prefer)):
                R.set(r, ('val', 'arith'))
                return r
            d = prefer if prefer is not None and R.free(prefer) else R.lowest(avoid)
            self.asm.pmi(0xa3, d, r)
            R.set(d, ('val', 'arith'))
            return d
        if x[0] == 'var':
            r = self.to_reg(x)
            if R.holder.get(r) == ('perm', x[1]):
                # the register holds a cached copy of Y: take it over
                R.set(r, ('val', 'arith'))
                return r
            d = prefer if prefer is not None and R.free(prefer) else R.lowest(avoid)
            self.asm.pmi(0xa3, d, r)
            R.set(d, ('val', 'arith'))
            return d
        r = self.to_reg(x, prefer)
        R.set(r, ('val', 'arith'))
        return r

    def build(self, v, prefer, avoid):
        """Build a list or vector in a register (write mode)."""
        k = v[0]
        R = self.R
        if k == 'list':
            items, tail = v[1], v[2]
        else:
            n = len(v[1])
            if n not in (2, 3):
                raise CompileRefusal('vector of %d elements built in a body' % n,
                                     'no witnessed put_vector_n')
        # nested structures (not the list's cdr chain) first, into temporaries
        pre = {}
        chain = []
        if k == 'list':
            t = v
            while True:
                chain.append(t[1][0])
                rest = ('list', t[1][1:], t[2]) if len(t[1]) > 1 else t[2]
                if rest[0] == 'list' and not ground(rest):
                    t = rest
                    continue
                chain.append(rest)
                break
            els = chain
        else:
            els = v[1]
        for idx, e in enumerate(els):
            if e[0] in ('list', 'vec', 'slot', 'arith') and not ground(e):
                pre[idx] = self.to_reg(e, scratch=False)
        r = prefer if prefer is not None and R.free(prefer) else R.lowest(avoid)
        if k == 'list':
            self.asm.pmi(0xaa, r)
        else:
            self.asm.pmi(0xb2 if len(els) == 2 else 0xb3, r)
        R.set(r, ('val', id(v)))
        a = self.asm
        for idx, e in enumerate(els):
            ek = e[0]
            if k == 'list' and idx % 2 == 1 and idx < len(els) - 1:
                pass
            if idx in pre:
                a.pmi(0x45, pre[idx])
                self.consume(e, pre[idx])
            elif ek == 'void':
                a.pmi16(0x4b, 0, 1)
            elif ek == 'var':
                name = e[1]
                if name in self.y:
                    self.ensure_env()
                    if name not in self.seen:
                        self.seen.add(name)
                        a.pmi(0x40, self.y[name])
                    else:
                        a.pmi(0x44, self.y[name])
                        self.unsafe.discard(name)
                else:
                    if name not in self.seen:
                        self.seen.add(name)
                        t = R.lowest(avoid)
                        R.set(t, ('var', name))
                        a.pmi(0x41, t)
                        self.use(name)
                    else:
                        if name not in R.where:
                            # the temporary's register was reused (two kappa2
                            # PCM classes, met once with_macro compiled)
                            raise CompileRefusal('internal', 'temporary %s lost its register' % name)
                        a.pmi(0x45, R.where[name])
                        self.use(name)
            elif ek == 'atom':
                a.atom('unify', 0, e[1])
            elif ek == 'int' and small(e[1]):
                a.pmi16(0x47, 0, e[1])
            elif ground(e):
                a.pool(0x49, 0, pool_term(e))
                self.note_refs(e)
            else:
                raise CompileRefusal('structure element', 'a %s' % ek)
            if k == 'list' and idx < len(els) - 1 and idx >= 1:
                pass
            # a list chain: after each car but the last, the cdr is a list cell
            if k == 'list' and idx < len(els) - 2:
                a.pmi(0x4a)
        return r

    # -- inline goals --------------------------------------------------------
    def inline(self, g):
        k = g.kind
        if k == 'unify':
            return self.unify(g.left, g.right)
        if k == 'compare':
            op, swap = COMPARE[g.op]
            x, y = (g.right, g.left) if swap else (g.left, g.right)
            rx = self.to_reg(x, scratch=True)
            hx = self.R.holder.get(rx)
            self.R.set(rx, ('val', 'cmp'))
            ry = self.to_reg(y, scratch=True)
            self.R.set(rx, hx)
            self.asm.blt(int(op, 16), rx, ry, 0)
            self.consume(x, rx)
            self.consume(y, ry)
            return
        if k == 'slotset':
            vr = self.to_reg(g.value, scratch=True)
            hv = self.R.holder.get(vr)
            self.R.set(vr, ('val', 'v'))
            orr = self.to_reg(g.obj, scratch=True)
            ho = self.R.holder.get(orr)
            self.R.set(orr, ('val', 'o'))
            n = self.R.lowest()
            self.asm.atom('put', n, g.slot)
            self.R.set(vr, hv)
            self.R.set(orr, ho)
            self.asm.blt(0x2f, orr, n, vr)
            self.consume(g.value, vr)
            self.consume(g.obj, orr)
            return
        if k == 'builtin':
            return self.builtin(g)
        raise CompileRefusal('goal', k)

    def builtin(self, g):
        op, roles = BUILTINS[(g.name, len(g.args))]
        regs = []
        keep = []
        if g.name == 'new_heap_vector':
            # witnessed only with V = N: N in a register, which becomes V
            out, n = g.args
            t = self.targets.get(out[1]) if out[0] == 'var' and out[1] not in self.seen else None
            r = self.dest(n, t, self.R.pending)
            self.asm.blt(0x19, r, r, 0)
            return self.bind_out(out, r)
        for v, role in zip(g.args, roles):
            if role == 'in':
                r = self.to_reg(v, scratch=True)
                keep.append((r, self.R.holder.get(r)))
                self.R.set(r, ('val', 'in'))
                regs.append(r)
            else:
                regs.append(None)
        for (r, h), v in zip(keep, [a for a, ro in zip(g.args, roles) if ro == 'in']):
            self.R.set(r, h)
        for v, r, role in zip(g.args, regs, roles):
            if role == 'in':
                self.consume(v, r)
        outs = [i for i, ro in enumerate(roles) if ro == 'out']
        for i in outs:
            v = g.args[i]
            regs[i] = self.out_reg(v)
        ops = regs + [0] * (3 - len(regs))
        self.asm.blt(int(op, 16), *ops[:3])
        for i in outs:
            self.bind_out(g.args[i], regs[i], emitted=True)

    def out_reg(self, v):
        R = self.R
        if v[0] == 'var' and v[1] not in self.y and v[1] not in self.seen:
            t = self.targets.get(v[1])
            if t is not None and R.free(t):
                return t
        return R.lowest(R.pending)

    def bind_out(self, v, r, emitted=True):
        """Register R holds a fresh result; unify it with V."""
        R = self.R
        if v[0] == 'void':
            R.drop(r)
            return
        if v[0] == 'var':
            name = v[1]
            if name in self.y:
                self.ensure_env()
                if name not in self.seen:
                    self.seen.add(name)
                    self.asm.pmi(0x24, r, self.y[name])
                    R.set(r, ('perm', name))
                else:
                    self.asm.pmi(0x22, r, self.y[name])
                    R.drop(r)
                return
            if name not in self.seen:
                self.seen.add(name)
                R.set(r, ('var', name))
                self.use(name)
                return
            self.asm.pmi(0x23, r, R.where[name])
            self.use(name)
            R.drop(r)
            return
        later = []
        self.get_value(r, v, later)
        while later:
            r2, v2 = later.pop(0)
            self.get_value(r2, v2, later)

    def unify(self, x, y):
        def fresh(v):
            return v[0] == 'var' and v[1] not in self.seen
        if fresh(y) and not fresh(x):
            x, y = y, x
        if x[0] == 'void' or y[0] == 'void':
            return
        if fresh(x):
            name = x[1]
            if y[0] == 'var':
                # aliasing: X is Y from now on
                if name in self.y or y[1] in self.y:
                    if fresh(y):
                        r = self.R.lowest(self.R.pending)
                        self.asm.pmi(0xa1, r, r)
                        self.R.set(r, ('val', 'fresh'))
                        self.bind_out(y, r)
                    r = self.to_reg(y)
                    self.consume(y, r)
                    if name in self.y:
                        self.ensure_env()
                        self.seen.add(name)
                        self.asm.pmi(0x24, r, self.y[name])
                        if self.R.free(r):
                            self.R.set(r, ('perm', name))
                    else:
                        self.seen.add(name)
                        if y[1] in self.pending_perm and self.R.where.get(y[1]) == r:
                            # R still holds a head argument waiting to be
                            # saved at the allocate: X gets a copy
                            r2 = self.R.lowest(self.R.pending)
                            self.asm.pmi(0xa3, r2, r)
                            r = r2
                        self.R.set(r, ('var', name))
                        self.use(name)
                    return
                if fresh(y):
                    r = self.R.lowest(self.R.pending)
                    self.asm.pmi(0xa1, r, r)
                    self.seen.add(y[1])
                    self.R.set(r, ('var', y[1]))
                    self.use(y[1])
                r = self.R.where[y[1]]
                self.use(y[1])
                self.seen.add(name)
                if self.R.free(r):
                    self.R.set(r, ('var', name))
                    self.use(name)
                else:
                    r2 = self.R.lowest(self.R.pending)
                    self.asm.pmi(0xa3, r2, r)
                    self.R.set(r2, ('var', name))
                    self.use(name)
                return
            prefer = self.targets.get(name) if name not in self.y else None
            r = self.to_reg(y, prefer=prefer)
            return self.bind_out(x, r)
        # X bound
        if y[0] == 'var' and not fresh(y):
            rx = self.to_reg(x, scratch=True)
            if y[1] in self.y:
                self.ensure_env()
                self.asm.pmi(0x22, rx, self.y[y[1]])
            else:
                self.asm.pmi(0x23, rx, self.R.where[y[1]])
                self.use(y[1])
            self.consume(x, rx)
            return
        if y[0] in ('slot', 'arith'):
            r = self.to_reg(y, scratch=True)
            if x[0] == 'var' and x[1] in self.y and x[1] not in self.pending_perm:
                self.ensure_env()
                self.asm.pmi(0x22, r, self.y[x[1]])
                self.R.drop(r)
                return
            hy = self.R.holder.get(r)
            self.R.set(r, ('val', 'y'))
            rx = self.to_reg(x, scratch=True)
            self.R.set(r, hy)
            self.asm.pmi(0x23, r, rx)
            self.consume(x, rx)
            self.R.drop(r)
            return
        if x[0] == 'var':
            rx = self.to_reg(x, scratch=True)
            self.consume(x, rx)
            later = []
            self.get_value(rx, y, later)
            while later:
                r2, v2 = later.pop(0)
                self.get_value(r2, v2, later)
            return
        # neither side a variable: an expression is evaluated, and the
        # other side read against it
        if x[0] in ('slot', 'arith') and y[0] not in ('slot', 'arith'):
            x, y = y, x
        r = self.to_reg(y, scratch=True)
        if x[0] in ('slot', 'arith'):
            hy = self.R.holder.get(r)
            self.R.set(r, ('val', 'y'))
            rx = self.to_reg(x, scratch=True)
            self.R.set(r, hy)
            self.asm.pmi(0x23, rx, r)
            self.consume(x, rx)
            self.consume(y, r)
            return
        later = []
        self.get_value(r, x, later)
        while later:
            r2, v2 = later.pop(0)
            self.get_value(r2, v2, later)

    # -- calls ----------------------------------------------------------------
    def call(self, g, last):
        a = self.asm
        args = g.args
        n = len(args)
        R = self.R
        if self.need_env:
            self.ensure_env()
        # 1. expressions and structures that are arguments, left to right
        placed = {}
        for i, v in enumerate(args):
            if v[0] in ('slot', 'arith', 'list', 'vec') and not ground(v):
                r = self.to_reg(v, prefer=i)
                placed[i] = r
        # 2. the arguments, highest register first
        for i in reversed(range(n)):
            v = args[i]
            R.pending.discard(i)
            if i in placed:
                src = placed[i]
                if src != i:
                    self.clear_way(i, n, src)
                    a.pmi(0xa3, i, src)
                R.drop(src)
                R.set(i, ('val', 'arg'))
                continue
            k = v[0]
            if k == 'var':
                name = v[1]
                if name in self.y:
                    cached = R.where.get(name)
                    if cached == i and name in self.seen and R.holder.get(i) == ('perm', name):
                        self.unsafe.discard(name)
                        R.set(i, ('val', 'arg'))
                        continue
                    self.clear_way(i, n)
                    self.ensure_env()
                    if name not in self.seen:
                        self.seen.add(name)
                        a.pmi(0xa0, i, self.y[name])
                        self.unsafe.add(name)
                    else:
                        if cached is not None and cached != i and R.holder.get(cached) == ('perm', name):
                            a.pmi(0xa3, i, cached)
                        else:
                            op = (0xa5 if last and self.env else 0xa4) if name in self.unsafe else 0xa2
                            a.pmi(op, i, self.y[name])
                        self.unsafe.discard(name)
                    R.set(i, ('val', 'arg'))
                    continue
                if name not in self.seen:
                    self.seen.add(name)
                    self.clear_way(i, n)
                    a.pmi(0xa1, i, i)
                    R.set(i, ('var', name))
                    self.use(name)
                    continue
                src = R.where[name]
                if src != i:
                    self.clear_way(i, n, src)
                    src = R.where[name]
                    a.pmi(0xa3, i, src)
                self.use(name)
                R.set(i, ('var', name) if R.remaining[name] > 0 else ('val', 'arg'))
                continue
            if k == 'void':
                self.clear_way(i, n)
                a.pmi(0xa1, i, i)
                R.set(i, ('val', 'arg'))
                continue
            self.clear_way(i, n)
            if g.kind == 'send' and i == n - 1 and k == 'class':
                # a class constant as the receiver: put, then class_object
                # (paragraph##profiler_ux_patch get_parameter/2, time_graph_window display_pos/1)
                a.pool(0xa9, i, pool_term(v))
                self.cc.ref(v[1])
                a.blt(0x25, i, i, 0)
            else:
                self.to_reg(v, prefer=i)
                if R.where.get(('x',)) is None:
                    pass
            R.set(i, ('val', 'arg'))
        # 3. the call
        if g.kind == 'send':
            if last:
                if self.env:
                    a.pmi(0x75, n - 1, n)
                else:
                    a.pmi(0x74, n - 1, n)
            else:
                self.ensure_env()
                a.pmi(0x73, n - 1, n)
            a.selector(g.name, n)
        else:
            key = (g.name, n)
            if last:
                if self.env:
                    a.local(0x62, 8 + self.envsize, key)
                else:
                    a.local(0x61, 0, key)
            else:
                self.ensure_env()
                a.local(0x60, 0, key)

    def clear_way(self, i, n, keep=None):
        """Before writing register I: move a live value out of the way."""
        R = self.R
        if R.live(i) and i != keep:
            h = R.holder[i]
            avoid = set(R.pending) | {i}
            r = R.lowest(avoid)
            self.asm.pmi(0xa3, r, i)
            R.set(r, h)
            R.holder[i] = None
            return r
        if R.holder.get(i) and R.holder[i][0] == 'perm':
            R.drop(i)
        return None


# --------------------------------------------------------------------------
# a class

SECTION_KIND = {('class', 'primary'): 0x25, ('class', 'before'): 0x26, ('class', 'after'): 0x27,
                ('instance', 'primary'): 0x35, ('instance', 'before'): 0x36,
                ('instance', 'after'): 0x37, ('class', 'slot_init'): 0x22,
                ('instance', 'slot_init'): 0x32, ('local', 'local'): 0x11, ('local', 'or'): 0x12}


class ClassCompiler:
    def __init__(self, unit, cdef):
        self.unit, self.cdef = unit, cdef
        self.cid = '%s##%s' % (unit.package, cdef['name'])
        self.preds = collections.OrderedDict()    # (name, arity, kind) -> PredDef
        self.nor = 0
        self.or_names = {}
        self.or_path = {}
        self.or_count = collections.Counter()
        self.refs = []
        self.refusals = []                         # (pred key or None, construct, detail)
        self.locals_ = set()

    def ref(self, cid):
        if cid not in self.refs and cid != self.cid:
            self.refs.append(cid)

    # -- goals from body terms ---------------------------------------------
    def goals(self, body, outside):
        """Goals of BODY.  OUTSIDE: the variables of the enclosing head (a
        disjunction's shared variables are those also found in OUTSIDE or
        in another goal of the same conjunction)."""
        out = []
        ts = flat(body)
        tv = [vars_of(t) for t in ts]
        for i, t in enumerate(ts):
            others = list(outside)
            for j in range(len(ts)):
                if j != i:
                    others += [v for v in tv[j] if v not in others]
            out.extend(self.goal(t, others, body))
        return out

    def goal(self, t, outside, body):
        u = self.unit
        k = t[0]
        if k in ('atom', 'qatom'):
            n = t[1]
            if n == '!':
                return [Goal('cut', vars={})]
            if n == 'true':
                return [Goal('true', vars={})]
            if n == 'fail':
                return [Goal('fail', vars={})]
            return [self.local_call(n, [])]
        if k == 'var':
            raise CompileRefusal('call/1', 'a variable as a goal')
        if k != 'cmp':
            raise CompileRefusal('goal', 'a %s as a goal' % k)
        f, args = t[1], t[2]
        if f == ';' and len(args) == 2:
            return [self.disjunction(t, outside, body)]
        if f in ('->',):
            raise CompileRefusal('if-then-else ->', 'not modelled')
        if f in ('not', '\\+') and len(args) == 1:
            raise CompileRefusal('not/1', 'negation as failure: its compiled form is not witnessed here')
        if f == ':' and len(args) == 1:
            m = args[0]
            if m[0] == 'cmp':
                vals = [classify(x, u) for x in m[2]]
                # the receiver is the first source argument and the last register
                regs = vals[1:] + vals[:1]
                return [Goal('send', name=m[1], args=regs, vars=self.vcount(vals))]
            if m[0] == 'cmp' and m[1] == ':':
                raise CompileRefusal(':Class:m()', 'instance method of a named class')
            raise CompileRefusal('method call', 'malformed :%r' % (m[:2],))
        if f == ':' and len(args) == 2:
            raise CompileRefusal('Class:m()', 'class method of a named class')
        if f in ('=', 'is') and len(args) == 2:
            l, r = classify(args[0], u), classify(args[1], u)
            return [Goal('unify', left=l, right=r, vars=self.vcount([l, r]))]
        if f in COMPARE and len(args) == 2:
            l, r = classify(args[0], u), classify(args[1], u)
            return [Goal('compare', op=f, left=l, right=r, vars=self.vcount([l, r]))]
        if f in UNWITNESSED_GOALS:
            raise CompileRefusal('comparison %s' % f, 'no witness of what it compiles to')
        if f == ':=' and len(args) == 2:
            lhs = args[0]
            if lhs[0] == 'cmp' and lhs[1] == '!' and len(lhs[2]) == 2:
                obj = classify(lhs[2][0], u)
                nm = atom_name(lhs[2][1])
                if nm is None:
                    raise CompileRefusal('dynamic slot name', 'Obj!X := V with X not an atom')
                val = classify(args[1], u)
                return [Goal('slotset', obj=obj, slot=nm, value=val, vars=self.vcount([obj, val]))]
            raise CompileRefusal(':=', 'not a slot assignment')
        vals = [classify(x, u) for x in args]
        if (f, len(args)) in BUILTINS:
            return [Goal('builtin', name=f, args=vals, vars=self.vcount(vals))]
        return [self.local_call(f, vals)]

    def local_call(self, name, vals):
        if (name, len(vals)) not in self.locals_:
            raise CompileRefusal('built-in %s/%d' % (name, len(vals)),
                                 'not a local predicate of the class, and no witnessed opcode')
        return Goal('call', name=name, args=vals, vars=self.vcount(vals))

    def vcount(self, vals):
        c = collections.Counter()
        for v in vals:
            value_vars(v, c)
        return c

    def number_ors(self, t, parent):
        """Number the body's disjunctions in source order, outer first
        (MEASURED: has_icon_window :read/2's outer disjunction is $or$0/2,
        the inner one $or$1/4), before anything can be refused, so a
        refused clause does not shift the numbers of the later ones."""
        if t[0] == 'cmp' and t[1] == ';' and len(t[2]) == 2:
            name = '$or$%d' % self.nor
            self.or_names[id(t)] = name
            self.nor += 1
            # where it is called from, for comparison with held code whose
            # numbering is not the source's (see canonical())
            self.or_count[parent] += 1
            path = self.or_path[name] = '%s#%d' % (parent, self.or_count[parent])
            for alt in flat(t, ';'):
                self.number_ors(alt, path)
        elif t[0] == 'cmp' and t[1] == ',' and len(t[2]) == 2:
            for x in t[2]:
                self.number_ors(x, parent)

    def disjunction(self, t, outside, body):
        """(A ; B ; ...) -> a call of a new local $or$N (kind 0x12) whose
        arguments are the variables shared with the rest of the clause."""
        alts = flat(t, ';')
        inner = vars_of(t)
        shared = [v for v in outside if v in inner]
        name = self.or_names[id(t)]
        pred = PredDef(name, len(shared), 0x12)
        self.locals_.add((name, len(shared)))
        self.preds[pred.key] = pred
        head = [('var', v) for v in shared]
        for alt in alts:
            if alt[0] == 'cmp' and alt[1] == '->':
                raise CompileRefusal('if-then-else ->', 'not modelled')
            pred.clauses.append(Clause(head, self.goals(alt, list(shared)), alt))
        vals = [('var', v) for v in shared]
        return Goal('call', name=name, args=vals, vars=self.vcount(vals))

    # -- clauses -------------------------------------------------------------
    def add_clause(self, section, role, name, head_terms, body, receiver_last):
        if section == 'local':
            kind = 0x11
        else:
            kind = SECTION_KIND[(section, role)]
        key = (name, len(head_terms), kind)
        pred = self.preds.get(key)
        if pred is None:
            pred = self.preds[key] = PredDef(name, len(head_terms), kind)
        if pred.refusal:
            return
        try:
            vals = [classify(x, self.unit) for x in head_terms]
            if receiver_last:
                vals = vals[1:] + vals[:1]
            # an expression in a head (`:count(Obj,Obj!count)`) is a fresh
            # variable unified with it after the body: the standard macros'
            # generator goes after the last body goal in a head (TM-388
            # p.66); held list_index_buffer count/2 is `dc 02, put_atom,
            # 27 01 02 01, 23 01 00, f0`
            extra = []

            def lift(v):
                if v[0] in ('slot', 'arith'):
                    nv = ('var', '$head%d' % len(extra))
                    extra.append(Goal('unify', left=nv, right=v, vars=self.vcount([nv, v])))
                    return nv
                if v[0] == 'list':
                    return ('list', [lift(x) for x in v[1]], lift(v[2]))
                if v[0] == 'vec':
                    return ('vec', [lift(x) for x in v[1]])
                return v
            vals = [lift(v) for v in vals]
            if body is not None:
                self.number_ors(body, '%s/%d.%02x' % (name, len(head_terms), kind))
            head_vars = []
            for v in vals:
                for nm in value_vars(v, collections.Counter()):
                    if nm not in head_vars:
                        head_vars.append(nm)
            goals = self.goals(body, head_vars) if body is not None else []
            pred.clauses.append(Clause(vals, goals + extra))
        except CompileRefusal as e:
            pred.refusal = e

    def compile(self):
        """-> a librarian.Template (with .pool), or raises CompileRefusal
        for the class as a whole.  Refused predicates are left out and
        listed in .refusals."""
        cd = self.cdef
        if cd.get('macro_bank'):
            cd = self.cdef = self.expand_macros(cd, self.unit.bank(cd['macro_bank'][1]))
        # locals first, so calls can tell them from built-ins
        for it in cd['clauses']:
            if it['section'] == 'local':
                self.locals_.add((it['name'], len(it['head'])))
        for it in cd['clauses']:
            if it['kind'] == 'slot_init':
                continue
            if it.get('refusal'):
                # a clause that met an unmodelled macro rule refuses its predicate
                kind = 0x11 if it['section'] == 'local' else SECTION_KIND[(it['section'], it['role'])]
                key = (it['name'], len(it['head']), kind)
                if key not in self.preds:
                    self.preds[key] = PredDef(it['name'], len(it['head']), kind)
                self.preds[key].refusal = it['refusal']
                continue
            self.add_clause(it['section'], it['role'], it['name'], it['head'], it['body'],
                            it['section'] != 'local')
        # slot initialisation predicates: (S := V :- Goals) -> S(V) :- Goals
        slots = {'class': [], 'instance': []}
        for sec in ('class', 'instance'):
            for s in cd['slots'][sec]:
                slots[sec].append(self.slot(sec, s))
        # compile every predicate (a $or$ found while compiling is appended)
        done = set()
        bodies = {}
        while True:
            todo = [k for k in self.preds if k not in done]
            if not todo:
                break
            for k in todo:
                done.add(k)
                p = self.preds[k]
                if p.refusal:
                    continue
                try:
                    bodies[k] = PredCompiler(self, p).compile()
                except CompileRefusal as e:
                    p.refusal = e
        # a predicate calling a refused local is refused too
        while True:
            have = {(k[0], k[1]) for k in bodies if k[2] in (0x11, 0x12)}
            bad = [k for k, asm in bodies.items()
                   if any(it[0] == 'local' and it[3] not in have for it in asm.items)]
            if not bad:
                break
            for k in bad:
                miss = sorted({it[3] for it in bodies[k].items if it[0] == 'local' and it[3] not in have})
                self.preds[k].refusal = CompileRefusal(
                    'calls a refused local', ' '.join('%s/%d' % m for m in miss))
                del bodies[k]
        for k, p in self.preds.items():
            if p.refusal:
                self.refusals.append((k, p.refusal.construct, p.refusal.detail))
        return self.layout(bodies, slots)

    def expand_macros(self, cd, bank):
        """CD with BANK's clause-level macros applied (TM-388 §3.7.3) to
        each clause's head arguments and body, and to slot values.  A
        clause that meets an unmodelled rule is kept with its refusal."""
        cd = dict(cd)
        clauses = []
        for it in cd['clauses']:
            it = dict(it)
            try:
                it['head'] = [bank.expand(a) for a in it['head']]
                if it['body'] is not None:
                    it['body'] = bank.expand(it['body'])
            except CompileRefusal as e:
                it['refusal'] = e
            clauses.append(it)
        cd['clauses'] = clauses
        slots = {}
        for sec, sl in cd['slots'].items():
            out = []
            for sd in sl:
                sd = dict(sd)
                try:
                    if sd['init'] is not None:
                        sd['init'] = bank.expand(sd['init'])
                    if sd['body'] is not None:
                        sd['body'] = bank.expand(sd['body'])
                except CompileRefusal as e:
                    sd['refusal'] = e
                out.append(sd)
            slots[sec] = out
        cd['slots'] = slots
        return cd

    def slot(self, sec, s):
        name, init, body, attr = s['name'], s['init'], s['body'], s['attribute']
        u = self.unit
        flag = 0x10 if attr else 0
        full = name if attr else '%s$%s' % (self.cid, name)
        if s.get('refusal'):
            # the slot's value or body met an unmodelled macro rule
            e = s['refusal']
            if body is not None:
                pred = PredDef(name, 1, SECTION_KIND[(sec, 'slot_init')])
                self.preds[pred.key] = pred
                pred.refusal = e
                return dict(name=full, flag=flag | LB.BY_CODE, init=('code', pred), term=None)
            self.refusals.append(((name, 1, 'slot'), e.construct, e.detail))
            return dict(name=full, flag=flag, init=('const', 0), term=('int', 0))
        if body is not None or (init is not None and init[0] == 'cmp' and init[1] == '#'
                                and len(init[2]) == 1 and init[2][0][0] != 'str'):
            # by code: an init predicate of kind 0x22/0x32 named after the slot, arity 1
            kind = SECTION_KIND[(sec, 'slot_init')]
            if body is None:
                # `S := #Class` compiles to an init predicate (MEASURED, kappa: plaintext.py)
                head = [init]
                goals_t = None
            else:
                head = [init]
                goals_t = body
            pred = PredDef(name, 1, kind)
            self.preds[pred.key] = pred
            try:
                vals = [classify(x, u) for x in head]
                hv = vars_of(head[0])
                if goals_t is not None:
                    self.number_ors(goals_t, '%s/1.%02x' % (name, kind))
                goals = self.goals(goals_t, hv) if goals_t is not None else []
                pred.clauses.append(Clause(vals, goals))
            except CompileRefusal as e:
                pred.refusal = e
            return dict(name=full, flag=flag | LB.BY_CODE, init=('code', pred), term=None)
        if init is None:
            return dict(name=full, flag=flag, init=('const', 0), term=('int', 0))
        if init[0] == 'cmp' and init[1] == '#is':
            nm = espscan.name_of(init[2][0])
            q = u.qualify(nm[0], nm[1]) if nm else '?'
            self.ref(q)
            return dict(name=full, flag=flag | LB.IS_CLASS, init=('is', q), term=('atom', q))
        try:
            v = classify(init, u)
        except CompileRefusal as e:
            self.refusals.append(((name, 1, 'slot'), e.construct, e.detail))
            return dict(name=full, flag=flag, init=('const', 0), term=('int', 0))
        if not ground(v):
            self.refusals.append(((name, 1, 'slot'), 'slot value', 'not a constant'))
            return dict(name=full, flag=flag, init=('const', 0), term=('int', 0))
        term = pool_term(v)
        val = LB._value(term) if term[0] in ('int', 'atom', 'str') else term
        if term[0] == 'int' and val & 0x80000000:
            val -= 1 << 32
        return dict(name=full, flag=flag, init=('const', val), term=term)

    # -- layout -----------------------------------------------------------------
    def layout(self, bodies, slots):
        syms = [self.cid, 'template']

        def sym(name):
            if name not in syms:
                syms.append(name)
            return syms.index(name)
        pool, pool_index = [], {}

        def pool_cell(term):
            k = repr(term)
            if k not in pool_index:
                pool_index[k] = len(pool)
                pool.append(term)
            return 13 + pool_index[k]
        # pool entries first (their cell numbers fix the code's start)
        for k, asm in bodies.items():
            for it in asm.items:
                if it[0] == 'pool':
                    pool_cell(it[3])
        n = 13 + len(pool)
        starts = {}
        sizes = {}
        for k, asm in bodies.items():
            n += 4                                     # the header cells
            starts[k] = n
            size = sum(1 for it in asm.items if it[0] != 'label')
            sizes[k] = size
            n += size
        by_sel = {(k[0], k[1]): s for k, s in starts.items() if k[2] in (0x11, 0x12)}
        preds = {}
        for k, asm in bodies.items():
            p = self.preds[k]
            off = starts[k]
            labels, cur = {}, off
            for it in asm.items:
                if it[0] == 'label':
                    labels[it[1]] = cur
                else:
                    cur += 1
            cells, cur = [], off
            for it in asm.items:
                t = it[0]
                if t == 'label':
                    continue
                if t == 'cell':
                    cells.append((cur, it[1], it[2], it[3]))
                elif t == 'sym':
                    cells.append((cur, it[1], it[2], sym(it[3])))
                elif t == 'local':
                    tgt = by_sel.get(it[3])
                    if tgt is None:
                        raise CompileRefusal('internal', 'local %s/%d not compiled' % it[3])
                    d = tgt - (cur + 2)
                    if not -0x8000 <= d < 0x8000:
                        raise CompileRefusal('code size', 'local call displacement %d' % d)
                    cells.append((cur, 0x20, 0, it[1] << 24 | it[2] << 16 | (d & 0xffff)))
                elif t == 'choice':
                    tgt = labels[it[3]]
                    d = tgt - (cur + (3 if it[1] in (0xe4, 0xc4) else 2))
                    cells.append((cur, 0x20, 0, it[1] << 24 | it[2] << 16 | (d & 0xffff)))
                elif t == 'pool':
                    d = pool_cell(it[3]) - cur
                    cells.append((cur, 0x20, 0, it[1] << 24 | it[2] << 16 | (d & 0xffff)))
                cur += 1
            preds[k] = LB.Pred(p.name, p.arity, p.kind, 0, off, cells, label=self.cdef['name'])
        for k, p in self.preds.items():
            sym(p.name)
        natures = []
        for n_ in self.cdef['natures'] or []:
            q = self.cid if n_ == ('', '*') else self.unit.qualify(n_[0] or None, n_[1])
            natures.append(q)
        if self.cid not in natures:
            natures.insert(0, self.cid)
        for x in natures:
            sym(x)
        cslots, islots = [], []
        for sec, out in (('class', cslots), ('instance', islots)):
            # the template lists slots in reverse source order (MEASURED:
            # list_index_buffer, icon_button, time_graph_window)
            for s in reversed(slots[sec]):
                init = s['init']
                if init[0] == 'code':
                    pd = init[1]
                    pr = preds.get(pd.key)
                    init = ('code', pr)
                    if pr is None:
                        self.refusals.append(((s['name'], 1, 'slot'), 'slot init refused',
                                              str(pd.refusal)))
                sym(s['name'])
                out.append(LB.Slot(s['name'], s['flag'], init, s['term']))
        t = LB.Template(self.cid, natures,
                        class_preds=[preds[k] for k in preds if k[2] in (0x25, 0x26, 0x27)],
                        instance_preds=[preds[k] for k in preds if k[2] in (0x35, 0x36, 0x37)],
                        locals_=[preds[k] for k in preds if k[2] in (0x11, 0x12)],
                        class_slots=cslots, instance_slots=islots,
                        refs=list(self.refs),
                        union=[x for x in natures if x != self.cid] + [r for r in self.refs if r not in natures],
                        symbols=syms, origin='espc')
        for r in self.refs:
            sym(r)
        t.symbols = syms
        t.pool = pool
        t.refusals = self.refusals
        t.or_path = self.or_path
        t.source = (self.cdef.get('file'), self.cdef.get('line'))
        return t


# --------------------------------------------------------------------------
# the source side: segments to class definitions

def item_clause(term):
    """-> (role, kind, name, head_args, body) for a clause item, or None.
    kind 'method' or 'local'."""
    role = 'primary'
    t = term
    body = None
    for _ in range(2):
        if t[0] == 'cmp' and t[1] in ('before', 'after') and len(t[2]) == 1:
            role, t = t[1], t[2][0]
        if t[0] == 'cmp' and t[1] == ':-' and len(t[2]) == 2:
            t, body = t[2]
        if t[0] == 'cmp' and t[1] == ':' and len(t[2]) == 2 and atom_name(t[2][0]) in ('before', 'after'):
            role, t = t[2][0][1], ['cmp', ':', [t[2][1]], t[-1]]
    if t[0] == 'cmp' and t[1] == ':' and len(t[2]) == 1:
        m = t[2][0]
        if m[0] == 'cmp':
            return (role, 'method', m[1], m[2], body)
        if m[0] in ('atom', 'qatom'):
            raise CompileRefusal('method head', ':%s with no receiver' % m[1])
        return None
    if t[0] == 'cmp' and t[1] in ('=>', '==>', '-->', 'when', 'where', 'with', 'by'):
        return ('macro', None, t[1], [], None)
    if t[0] == 'cmp':
        return (role, 'local', t[1], t[2], body)
    if t[0] in ('atom', 'qatom'):
        return (role, 'local', t[1], [], body)
    return None


def class_defs(segs, file=None):
    """espscan segments -> [class definition dict]."""
    out = []
    for seg in segs:
        if seg[0] != 'class':
            continue
        _, kw, header, items, line = seg
        name, pkg, mb = espscan.header_info(header)
        d = dict(name=name, pkg=pkg, kw=kw, macro_bank=mb, file=file, line=line, natures=None,
                 slots={'class': [], 'instance': []}, clauses=[], unparsed=[], skipped=[], macros=[])
        for section, toks, term, err in items:
            if term is None:
                d['unparsed'].append((toks[0][2] if toks else line, err))
                continue
            if term[0] == 'cmp' and term[1] == 'nature' and len(term[2]) == 1:
                d['natures'] = d['natures'] or []
                for n in flat(term[2][0]):
                    if n[0] == 'atom' and n[1] == '*':
                        d['natures'].append(('', '*'))
                        continue
                    nm = espscan.name_of(n)
                    d['natures'].append((nm[0] or '', nm[1]) if nm else ('', '?'))
                continue
            if term[0] == 'cmp' and term[1] in ('attribute', 'component') and len(term[2]) == 1:
                sec = 'class' if section == 'class' else 'instance'
                for sl, init, body in espscan.slot_defs(term[2][0]):
                    d['slots'][sec].append(dict(name=str(sl), init=init, body=body,
                                                attribute=term[1] == 'attribute'))
                continue
            if term[0] == 'cmp' and term[1] == ':-' and len(term[2]) == 1:
                d['skipped'].append(('directive', term[2][0][1] if term[2][0][0] == 'cmp' else '?'))
                continue
            try:
                c = item_clause(term)
            except CompileRefusal as e:
                d['unparsed'].append((line, str(e)))
                continue
            if c is None:
                d['unparsed'].append((line, 'not a clause'))
                continue
            role, k, nm, head, body = c
            if role == 'macro':
                d['skipped'].append(('macro', nm))
                d['macros'].append(term)
                continue
            if k == 'method' and section == 'local':
                d['unparsed'].append((line, 'method head in the local part'))
                continue
            if k == 'local' and section != 'local':
                d['unparsed'].append((line, 'local clause %s/%d outside the local part' % (nm, len(head))))
                continue
            d['clauses'].append(dict(section=section, role=role, kind=k, name=nm, head=head, body=body))
        out.append(d)
    return out


def parse_text(text, path='<source>', files=None):
    """ESP source text -> class definitions.  FILES ({relpath: bytes}) serves
    include files, as plaintext.parse_program does."""
    prog = espscan.Program('espc', [])
    prog.allfiles = [(rel, rel) for rel in sorted(files or {})]
    prog.rel = lambda p: p
    if files:
        espscan.open = lambda p, mode='r': io.BytesIO(files[p])
    segs, nerr, _ops = espscan.parse_file(prog, path, text, [])
    return class_defs(segs, path), nerr


def parse_program(name, files):
    """Every class of a held program (plaintext.parse_program's driver)."""
    import plaintext
    parsed, nerr, nfiles = plaintext.parse_program(name, files)
    out = []
    for rel, segs in parsed:
        out.extend(class_defs(segs, rel))
    return out


def banks_of(defs):
    """{macro bank name: definition}, the first definition of a name."""
    out = {}
    for d in defs:
        if d['kw'] == 'macro_bank':
            out.setdefault(d['name'], d)
    return out


def compile_classes(defs, package, known=None):
    """-> (templates, failures) where failures is {class name: CompileRefusal}.
    A class defined twice keeps its first definition."""
    unit = Unit(package, known, banks_of(defs))
    for d in defs:
        if d['kw'] == 'class':
            unit.local_classes.add(d['name'])
    out, failed, seen = [], {}, set()
    for d in defs:
        if d['kw'] != 'class' or d['name'] in seen:
            continue
        seen.add(d['name'])
        try:
            out.append(ClassCompiler(unit, d).compile())
        except CompileRefusal as e:
            failed[d['name']] = e
    return out, failed


def compile_text(text, package, known=None, path='<source>'):
    defs, nerr = parse_text(text, path)
    if nerr:
        raise CompileRefusal('syntax', '%d items not parsed in %s' % (nerr, path))
    return compile_classes(defs, package, known)


def library(templates, base=None):
    """A Librarian holding TEMPLATES (plus BASE's, if given)."""
    lib = base or LB.Librarian()
    for t in templates:
        lib.add(t)
    return lib


STANDIN = os.path.join(HERE, 'standin')


def standins(names=None):
    """The SIMPOS stand-ins of psi/standin/ (scaffolding: OURS, or printed
    source with marked corrections), compiled into package `simpos`; each
    template is flagged `standin`, so kl0 refuses a method it lacks as a
    SIMPOS call, not as 'no method'."""
    out = []
    for f in sorted(os.listdir(STANDIN)):
        if not f.endswith('.esp') or (names is not None and f[:-4] not in names):
            continue
        path = os.path.join(STANDIN, f)
        with open(path, 'rb') as fh:
            text, _enc = esplex.decode(fh.read())
        ts, failed = compile_text(text, 'simpos', path=path)
        if failed:
            raise CompileRefusal('stand-in', '%s: %s' % (f, failed))
        for t in ts:
            t.standin = True
            out.append(t)
    return out


def listing(t):
    rec = dict(syms=t.symbols)
    lines = ['%s natures %s' % (t.id, ' '.join(t.natures))]
    for sec, sl in (('class', t.class_slots), ('instance', t.instance_slots)):
        for s in sl:
            lines.append('%s slot %s flag %02x init %r' % (sec, s.name, s.flag, s.init))
    for p in t.preds():
        if p is None:
            continue
        lines.append('== %r @%x' % (p, p.offset))
        for c in p.cells:
            if c[1] == 0x20 and c[3] >> 24 in (0x29, 0x49, 0xa9):
                d = c[3] & 0xffff
                d = d - 0x10000 if d & 0x8000 else d
                lines.append('%5x  %s   pool %r' % (c[0], P.show(rec, c), t.pool[c[0] + d - 13]))
            else:
                lines.append('%5x  %s' % (c[0], P.show(rec, c)))
    for r in getattr(t, 'refusals', []):
        lines.append('REFUSED %s: %s %s' % r)
    return '\n'.join(lines)


# --------------------------------------------------------------------------
# structural comparison with the held templates (see compare.py-like report)

INDEXING = {('pmi', 0xc9), ('pmi', 0xc7), ('pmi', 0xcc), ('pmi', 0xe5), ('pmi', 0xe3), ('pmi', 0xe1),
            ('pmi', 0xc5), ('pmi', 0xc3), ('pmi', 0xc8), ('pmi', 0xca), ('pmi', 0xcb),
            ('blt', 0xe6), ('blt', 0xf0)}
CHOICE = {0xe4, 0xe2, 0xe0, 0xc4, 0xc2, 0xc0}
MOVES = {0x20, 0x21, 0x24, 0x25, 0xa3, 0xa2, 0xa4, 0xa5, 0xa6, 0x5f, 0xf1, 0xf0, 0x6e}
CUTS = {0xd0, 0xd1, 0xd2, 0xd3, 0xd4, 0xdc, 0xdd, 0xde}
VARIANTS = {0x24: 0x20, 0xa4: 0xa2, 0xa5: 0xa2, 0x42: 0x44, 0x43: 0x45, 0x46: 0x40, 0xc4: 0xe4,
            0xc2: 0xe2, 0xc0: 0xe0, 0xd3: 0xd1, 0xde: 0xdd}


def local_calls(p):
    """Offsets of the predicates P calls locally, in code order."""
    out = []
    for c in p.cells:
        if c[1] == 0x20 and c[3] >> 24 in (0x60, 0x61, 0x62):
            d = c[3] & 0xffff
            out.append(c[0] + 2 + (d - 0x10000 if d & 0x8000 else d))
    return out


def canonical(t):
    """{offset: name} with each `$or$N` renamed by where it is called:
    `parent#k`, the k-th disjunction its parent calls, in code order.
    The held compiler numbers disjunctions in an order that is not the
    source's (MEASURED on paragraph##receiver: send/7's are numbered
    before draw_graph/6's although the source has them after), so the
    numbers themselves are not compared."""
    preds = [q for q in t.preds() if q is not None]
    by_off = {q.offset: q for q in preds}
    names = {q.offset: '%s/%d' % (q.name, q.arity) for q in preds if q.kind != 0x12}
    paths = getattr(t, 'or_path', None)
    if paths is not None:
        # compiled here: the paths were recorded from the source
        for q in preds:
            if q.kind == 0x12:
                names[q.offset] = paths[q.name]
        return names
    queue = [q for q in preds if q.kind != 0x12]
    while queue:
        q = queue.pop(0)
        k = 0
        for off in local_calls(q):
            r = by_off.get(off)
            if r is not None and r.kind == 0x12 and off not in names:
                k += 1
                names[off] = '%s#%d' % (names[q.offset] if q.kind == 0x12 else
                                        '%s.%02x' % (names[q.offset], q.kind), k)
                queue.append(r)
    for q in preds:
        names.setdefault(q.offset, '%s/%d' % (q.name, q.arity))
    return names


def normal(t, p, pool_of, by_off=None):
    """A predicate's cells in a position-independent form."""
    rec = dict(syms=t.symbols)
    if by_off is None:
        by_off = canonical(t)
    out = []
    skip = 0
    cells = p.cells
    for i, c in enumerate(cells):
        if skip:
            skip -= 1
            out.append(('data', 'skip'))
            continue
        n, tag, lo, v = c
        if tag in (0x20, 0x21):
            op = v >> 24
            a, b, cc = (v >> 16) & 255, (v >> 8) & 255, v & 255
            d = v & 0xffff
            d = d - 0x10000 if d & 0x8000 else d
            cls = 'pmi' if tag == 0x20 else 'blt'
            if cls == 'pmi' and op in (0x60, 0x61, 0x62):
                out.append((cls, op, a if op == 0x62 else 0, 'call', by_off.get(n + 2 + d, '?')))
            elif cls == 'pmi' and op in (0x29, 0x49, 0xa9):
                out.append((cls, op, a, 'pool', repr(pool_of(t, n + d))))
            elif cls == 'pmi' and op in CHOICE | {0xe5, 0xe3, 0xe1, 0xc5, 0xc9, 0xc7, 0xcc}:
                base = 3 if op in (0xe4, 0xc4, 0xc7, 0xcc) else 2
                out.append((cls, op, a, 'rel', n + base + d - p.offset))
                if op in (0xc9, 0xc7, 0xcc):
                    skip = 1
            else:
                out.append((cls, op, a, b, cc))
        elif tag == 0x60:
            m = 'put' if lo & 0x80 else ('unify' if lo == 0x4c else 'get')
            out.append(('atom', m, lo & 0x7f if m != 'unify' else 0, P.sym(rec, v)))
        elif tag == 0x01:
            out.append(('sel', P.sym(rec, v), lo))
        elif tag == 0x00:
            out.append(('int', v))
        elif tag == 0xa0:
            out.append(('table',))
        else:
            out.append(('cell', tag, lo, v))
    return out


def semantic(norm):
    """The operations with meaning, whatever the registers, moves,
    environment and indexing: calls, sends, built-ins, constants,
    structures, cuts, fail."""
    out = []
    for x in norm:
        k = x[0]
        if k in ('pmi', 'blt'):
            cls, op = x[0], x[1]
            if (cls, op) in INDEXING or (cls == 'pmi' and op in CHOICE):
                continue
            if cls == 'pmi' and op in MOVES:
                continue
            if cls == 'pmi' and op in (0x60, 0x61, 0x62):
                out.append(('call', x[4]))
            elif cls == 'pmi' and op in (0x73, 0x74, 0x75):
                out.append(('send',))
            elif cls == 'pmi' and op in CUTS:
                out.append(('cut',))
            elif cls == 'pmi' and op in (0x29, 0x49, 0xa9):
                out.append(('const', x[4]))
            elif cls == 'pmi' and op in (0x27, 0x47, 0xa7):
                out.append(('const', 'int'))
            elif cls == 'pmi' and op in (0x40, 0x41, 0x44, 0x45, 0x42, 0x43, 0x46, 0x22, 0x23, 0xa0, 0xa1,
                                         0x4b):
                continue
            elif cls == 'pmi':
                out.append(('pmi', VARIANTS.get(op, op)))
            else:
                out.append(('blt', op))
        elif k == 'atom':
            out.append(('const', x[3]))
        elif k == 'sel':
            out.append(('send', x[1], x[2]))
        elif k in ('int', 'data', 'table'):
            continue
        else:
            out.append(x)
    # a send is its selector
    return [x for x in out if x != ('send',)]


def skeleton(norm):
    """The normal form with register operands removed."""
    out = []
    for x in norm:
        if x[0] in ('pmi', 'blt'):
            if len(x) == 5 and x[3] in ('call', 'pool', 'rel'):
                out.append((x[0], x[1], x[3], x[4] if x[3] != 'rel' else None))
            else:
                out.append((x[0], x[1]))
        elif x[0] == 'atom':
            out.append(('atom', x[1], x[3]))
        else:
            out.append(x)
    return out


def classify_diff(nc, nh):
    if nc == nh:
        return 'exact'
    if skeleton(nc) == skeleton(nh):
        return 'registers'
    sc, sh = semantic(nc), semantic(nh)
    if sc == sh:
        hv = any(x[0] in ('pmi', 'blt') and x[1] in VARIANTS for x in nh)
        return 'moves and environment'
    if sorted(map(repr, sc)) == sorted(map(repr, sh)):
        if any(x[0] in ('pmi', 'blt') and (x[0], x[1]) in INDEXING for x in nh) or any(
                x[0] == 'table' for x in nh):
            return 'indexing'
        return 'clause order'
    if any(x[0] in ('pmi', 'blt') and (x[0], x[1]) in INDEXING for x in nh) or any(
            x[0] == 'table' for x in nh):
        return 'indexing and other'
    return 'other'


def _pool_held(t, cell):
    import kl0
    try:
        code = _HELD_CODE.setdefault(t.id, kl0.Code(None, t))
        if code.pool is None:
            code.pool = kl0.read_pool(t)
        k = cell - 13
        return code.pool[k] if 0 <= k < len(code.pool) else ('?pool', cell)
    except Exception as e:  # noqa: BLE001
        return ('?pool', str(e))


_HELD_CODE = {}


def _pool_ours(t, cell):
    k = cell - 13
    return t.pool[k] if 0 <= k < len(t.pool) else ('?pool', cell)


PROGRAMS = {'paragraph': ['paragraph'], 'kappa2': ['kappa'], 'utter': ['fts', 'qxt', 'sancho2', 'tour']}


def check(program, held_lib=None):
    """Compile PROGRAM's held source and compare it with its held
    templates.  -> dict of counts, rows (one per predicate) and refusals."""
    import held
    import plaintext
    if held_lib is None:
        held_lib = LB.Librarian()
        held_lib.load_held(pkgs=PROGRAMS[program])
    files = held.src_files(program)
    defs = parse_program(program, files)
    by_name = collections.defaultdict(list)
    for d in defs:
        if d['kw'] == 'class':
            by_name[d['name']].append(d)
    banks = banks_of(defs)
    c = collections.Counter()
    rows = []
    refusals = collections.Counter()
    templates = {}
    for cid, ht in held_lib.templates.items():
        if held_lib.packages[ht.package]['file'] not in PROGRAMS[program]:
            continue
        c['templates'] += 1
        ds = by_name.get(ht.name) or [d for n, dd in by_name.items() if n.lower() == ht.name.lower() for d in dd]
        if not ds:
            c['no source'] += 1
            continue
        c['with source'] += 1
        c['held predicates'] += sum(1 for p in ht.preds() if p is not None)
        d = ds[0]
        if d['macro_bank']:
            c['macro bank class'] += 1
        unit = Unit(ht.package, banks=banks)
        unit.local_classes = {n for n in by_name}
        try:
            cc_ = ClassCompiler(unit, d)
            t = cc_.compile()
        except CompileRefusal as e:
            c['class refused'] += 1
            refusals[e.construct] += 1
            rows.append((cid, '*', 'class refused', e.construct))
            continue
        c['classes compiled'] += 1
        templates[cid] = t
        tf_h = plaintext.template_facts(ht)
        tf_c = plaintext.template_facts(t)
        # the method and local sets as declared: refused predicates included
        tf_c['methods'] = {(LB.KIND[k[2]][0], plaintext.norm(k[0]), k[1], LB.KIND[k[2]][1])
                           for k in cc_.preds if k[2] in (0x25, 0x26, 0x27, 0x35, 0x36, 0x37)}
        tf_c['locals'] = {(plaintext.norm(k[0]), k[1]) for k in cc_.preds if k[2] == 0x11}
        for aspect in ('natures', 'slots', 'methods', 'locals'):
            c['%s compared' % aspect] += 1
            if tf_h[aspect] == tf_c[aspect]:
                c['%s agree' % aspect] += 1
            else:
                rows.append((cid, aspect, 'aspect differs', ''))
        dem_h = {m for m in tf_h['methods'] if m[3] != 'primary'}
        dem_c = {m for m in tf_c['methods'] if m[3] != 'primary'}
        c['demon sets compared'] += 1
        c['demon sets agree'] += dem_h == dem_c
        ch, cn = canonical(ht), canonical(t)
        hs = {(ch[p.offset], p.kind): p for p in ht.preds() if p is not None}
        cs = {(cn[p.offset], p.kind): p for p in t.preds() if p is not None}
        # two predicates under one key would be compared with the wrong one
        c['key collisions'] += (sum(1 for p in ht.preds() if p is not None) - len(hs)
                                + sum(1 for p in t.preds() if p is not None) - len(cs))
        for _k, con, _det in t.refusals:
            refusals[con] += 1
        refused = {(k[0], k[1]) for k, p in cc_.preds.items() if p.refusal}
        c['disjunctions held'] += sum(1 for p in ht.locals if p.kind == 0x12)
        c['disjunctions source'] += len(cc_.or_names)
        for k in sorted(set(hs) | set(cs), key=repr):
            label = '%s %02x' % k
            if k not in cs:
                root = re.match(r'(.*)/(\d+)(?:\.[0-9a-f]{2})?(?:#|$)', k[0])
                nm = [root.group(1), root.group(2)] if root else [k[0]]
                if '#' in k[0] and root:
                    cause = ('$or$ of a refused predicate' if (nm[0], int(nm[1])) in refused
                             else 'held $or$ with no compiled counterpart')
                elif len(nm) == 2 and (nm[0], int(nm[1])) in refused:
                    cause = 'refused'
                elif d['unparsed']:
                    cause = 'unparsed source'
                else:
                    cause = 'held only'
                c['pred ' + cause] += 1
                rows.append((cid, label, cause, ''))
                continue
            if k not in hs:
                c['pred compiled only'] += 1
                rows.append((cid, label, 'compiled only', ''))
                continue
            nc = normal(t, cs[k], _pool_ours, cn)
            nh = normal(ht, hs[k], _pool_held, ch)
            if '#' in k[0] and cs[k].arity != hs[k].arity:
                c['$or$ paired with another arity'] += 1
            cls = classify_diff(nc, nh)
            if cls in ('other', 'indexing and other') and any(
                    x[0] in ('pmi', 'blt') and (x[0], '%02x' % x[1]) not in WITNESSED for x in nh):
                cls = 'held uses an unwitnessed opcode'
            c['pred compared'] += 1
            c['pred ' + cls] += 1
            rows.append((cid, label, cls, ''))
    return dict(counts=c, rows=rows, refusals=refusals, templates=templates)


def summary(program, r):
    c = r['counts']
    cmp_ = c['pred compared']
    out = ['%s: %d templates, %d with source, %d classes compiled, %d refused as a whole' % (
        program, c['templates'], c['with source'], c['classes compiled'], c['class refused'])]
    out.append('  class aspects agree: natures %d/%d, slots %d/%d, methods %d/%d, demons %d/%d, locals %d/%d' % (
        c['natures agree'], c['natures compared'], c['slots agree'], c['slots compared'],
        c['methods agree'], c['methods compared'], c['demon sets agree'], c['demon sets compared'],
        c['locals agree'], c['locals compared']))
    hp = c['held predicates']
    out.append('  predicates compared: %d; exact %d (%.1f%% of compared, %.1f%% of the %d held predicates '
               'of the classes with source)' % (
                   cmp_, c['pred exact'], 100.0 * c['pred exact'] / cmp_ if cmp_ else 0,
                   100.0 * c['pred exact'] / hp if hp else 0, hp))
    for k in ('registers', 'moves and environment', 'indexing', 'clause order', 'indexing and other',
              'held uses an unwitnessed opcode', 'other'):
        out.append('    %-32s %d' % (k if k != 'other' else 'other (unclassified)', c['pred ' + k]))
    out.append('  predicates not compared: refused %d, $or$ of a refused predicate %d, '
               'held $or$ with no compiled counterpart %d, unparsed source %d, held only %d, '
               'compiled only %d' % (
                   c['pred refused'], c['pred $or$ of a refused predicate'],
                   c['pred held $or$ with no compiled counterpart'], c['pred unparsed source'],
                   c['pred held only'], c['pred compiled only']))
    out.append('  disjunctions: %d held, %d in the source; %d paired with another arity; key collisions %d' % (
        c['disjunctions held'], c['disjunctions source'], c['$or$ paired with another arity'],
        c['key collisions']))
    out.append('  classes whose aspects differ: ' + (', '.join(
        '%s (%s)' % (cid, n) for cid, n, _cls, _x in r['rows'] if _cls == 'aspect differs') or 'none'))
    out.append('  refusals by construct: ' + ', '.join('%s %d' % kv for kv in r['refusals'].most_common()))
    return '\n'.join(out)


def compiled_program(program):
    """Compile PROGRAM's held source (read in memory) -> (templates, failures)."""
    import held
    defs = parse_program(program, held.src_files(program))
    return compile_classes(defs, PROGRAMS[program][0])


def behave_calls(m):
    """The calls psi/test_kl0.py makes on the paragraph classes, run on
    machine M -> {call label: repr of the answers, or 'REFUSED cause'}."""
    import kl0 as K
    A, V = K.Atom, K.Var
    out = {}

    def send(recv, name, *args):
        regs = list(args) + [recv]
        return [[K.resolve(a) for a in args] for _ in m.solve_send(recv, name, regs)]

    def run(label, f):
        m.reset()
        try:
            out[label] = repr(f())
        except K.Refusal as e:
            out[label] = 'REFUSED %s: %s' % (e.cause, e.detail)
        except K.StepLimit:
            out[label] = 'STEP LIMIT'

    def switch_icon():
        (sol,) = K.call_class_method(m, 'paragraph##predicate_num_switch_icon', 'create',
                                     [100, 200, V()])
        return {y0: send(sol[2], 'get_code', 105, y0, V()) for y0 in (210, 228, 229, 240)}

    def buffer():
        (sol,) = K.call_class_method(m, 'paragraph##list_index_buffer', 'create', [V()])
        b = sol[0]
        r = [len(send(b, 'clear'))]
        send(b, 'add_last', A('a'), A('ka'))
        send(b, 'add_last', A('b'), A('kb'))
        send(b, 'add_first', A('c'), A('kc'))
        r += [send(b, 'count', V()), send(b, 'get_contents', V()),
              send(b, 'get_contents_with_key', V()), send(b, 'search', A('kb'), V()),
              send(b, 'search_num', A('kb'), V(), V()), send(b, 'search', V()),
              len(send(b, 'remove', A('ka'))), send(b, 'remove', A('ka')),
              send(b, 'count', V()), send(b, 'get_contents', V()),
              send(b, 'get_partial_contents', 1, 5, V()),
              send(b, 'get_partial_contents', 5, 5, V()),
              send(b, 'remove_num', A('kb'), V())]
        return r

    def two_primaries():
        icon = K.new_instance(m.lib, 'paragraph##scroll_bottom_icon')
        return [send(icon, 'code', 0, 0, c)
                for c in (V(), A('bottom_predicate'), A('scroll_bottom'), A('other'))]

    def version():
        return K.call_class_method(m, 'paragraph##paragraph_version', 'get_version', [V()])

    run('predicate_num_switch_icon create/3 + get_code/4', switch_icon)
    run('list_index_buffer battery', buffer)
    run('scroll_bottom_icon code/4', two_primaries)
    run('paragraph_version get_version/1', version)
    return out


def behave():
    """The compiled paragraph classes, alone in a library (so every class a
    call reaches is one this compiler produced), against paragraph.ptf
    alone: test_kl0's calls, then kl0's census of every method."""
    import kl0 as K
    ts, _failed = compiled_program('paragraph')
    mc = K.Machine(library(ts))
    hl = LB.Librarian()
    hl.load_held(pkgs=['paragraph'])
    mh = K.Machine(hl)
    calls = (behave_calls(mc), behave_calls(mh))
    # kl0's census of paragraph.ptf (every method of the classes free of
    # anything not loaded, called once with unbound arguments), and the
    # same calls on the compiled classes
    rh = {r[:3]: r[3:] for r in K.census(mh)}
    rc = {}
    for (cid, section, sel) in rh:
        name, n = sel.rsplit('/', 1)
        n = int(n)
        if cid not in mc.lib.templates:
            rc[(cid, section, sel)] = ('refused', 'class not compiled', '')
            continue
        mc.reset()
        try:
            co = mc.lib.build(cid)
            table = co.class_methods if section == 'class' else co.instance_methods
            if (name, n) not in table:
                why = [r[1] for r in mc.lib.templates[cid].refusals if r[0][:2] == (name, n)]
                raise K.Refusal('not compiled', why[0] if why else 'no method')
            recv = K.ClassRef(cid) if section == 'class' else K.make_instance(mc, cid)
            regs = [K.Var() for _ in range(n - 1)] + [recv]
            ok = any(True for _ in mc.solve_send(recv, name, regs))
            rc[(cid, section, sel)] = ('success' if ok else 'failure', '', '')
        except K.Refusal as e:
            rc[(cid, section, sel)] = ('refused', e.cause, e.detail)
        except K.StepLimit:
            rc[(cid, section, sel)] = ('step limit', '', '')
    cen = collections.Counter()
    rows = []
    for k in sorted(rh):
        c, h = rc[k], rh[k]
        if c[0] == h[0] and c[0] != 'refused':
            st = 'same outcome'
        elif c[0] == h[0]:
            st = 'both refused'
        elif c[0] == 'refused' and h[0] != 'refused':
            st = 'refused compiled only'
        elif h[0] == 'refused':
            st = 'refused held only'
        else:
            st = 'outcomes differ'
        cen[st] += 1
        rows.append((k, st, c, h))
    return dict(calls=calls, census=cen, rows=rows, templates=len(ts))


def main(argv):
    if argv and argv[0] == 'behave':
        r = behave()
        c, h = r['calls']
        for k in c:
            print('%s %s' % ('SAME   ' if c[k] == h[k] else 'DIFFER ', k))
            if c[k] != h[k]:
                print('    compiled %s\n    held     %s' % (c[k], h[k]))
        print('census (%d compiled classes, paragraph.ptf alone): %s' % (
            r['templates'], ', '.join('%s %d' % kv for kv in r['census'].most_common())))
        if '-v' in argv:
            for k, st, cc, hh in r['rows']:
                if st not in ('same outcome', 'both refused'):
                    print('  %s %s %s: compiled %s held %s' % (st, k[0], k[2], cc, hh))
        return 0
    if argv and argv[0] == 'compile':
        path = argv[1]
        pkg = argv[argv.index('--package') + 1] if '--package' in argv else 'user'
        with open(path, 'rb') as f:
            text, _enc = esplex.decode(f.read())
        defs, nerr = parse_text(text, path)
        ts, failed = compile_classes(defs, pkg)
        for t in ts:
            print(listing(t) if '--listing' in argv else '%s: %d predicates, %d refused' % (
                t.id, len([p for p in t.preds() if p is not None]), len(t.refusals)))
        for n, e in failed.items():
            print('CLASS REFUSED %s: %s' % (n, e))
        return 0
    if argv and argv[0] == 'check':
        progs = [a for a in argv[1:] if not a.startswith('--') and a in PROGRAMS] or ['paragraph']
        tsv = argv[argv.index('--tsv') + 1] if '--tsv' in argv else None
        allrows = []
        for p in progs:
            r = check(p)
            print(summary(p, r))
            allrows += [(p,) + row for row in r['rows']]
        if tsv:
            with open(tsv, 'w') as f:
                f.write('program\tclass\tpredicate\tclass_of_difference\tnote\n')
                for row in allrows:
                    f.write('\t'.join(row) + '\n')
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
