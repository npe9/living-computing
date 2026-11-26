#!/usr/bin/env python3
"""A reader of ESP terms from text (step 3l, route step B6).  OURS: SIMPOS's
reader (the one behind standard_input_file gett/2) is lost.  It reads the
held login files' clause syntax (shell.md §4.2.2) and nothing more:

  - atoms (`menu`, quoted `'kappa##kappa_tool'`), integers, strings
    ("..." -> 16-bit strings), variables (`_` and capitalised names);
  - `pkg##name` read as ONE atom 'pkg##name' (INFERENCE: the library takes
    the class name as an atom, kl0 lib_class_named; the login files'
    menu items name classes this way);
  - lists [...] and [H|T]; vectors {a, b, ...};
  - compound terms f(a, b) as the vector {f, a, b}: KNOWN from held
    source, kwic-esp src/systems.esp:380-383 (`get_term_first(SV, First)
    :- stack_vector(SV, _), !, first(SV, First)` on a term gett/2 read)
    and dbUtil.esp:1437 (`sentence(_, _, Sentence) = Term`);
  - the infix operators the login files use: `:-` (1200, xfx), `,`
    (1000, xfy), `:=` (700, xfx); priorities as Prolog's (OURS);
  - `%` comments to the end of the line; a clause ends with `.` followed
    by white space or the end.

read_terms(text) -> [term, ...] with kl0 terms (Atom, int, Str, Var,
Cons, Vec).  A syntax error raises ValueError.
"""
import re

TOKEN = re.compile(r'''
   (?P<ws>\s+|%[^\n]*)
 | (?P<str>"(?:[^"]|"")*")
 | (?P<qatom>'(?:[^']|'')*')
 | (?P<num>\d+)
 | (?P<var>[A-Z_][A-Za-z0-9_]*)
 | (?P<atom>[a-z][A-Za-z0-9_]*(?:\#\#[A-Za-z_][A-Za-z0-9_]*)?)
 | (?P<end>\.(?=\s|$))
 | (?P<op>:-|:=|\#\#)
 | (?P<punct>[()\[\]{},|])
''', re.X)

INFIX = {':-': (1200, 'xfx'), ',': (1000, 'xfy'), ':=': (700, 'xfx')}


def tokens(text):
    i, out = 0, []
    while i < len(text):
        mt = TOKEN.match(text, i)
        if not mt:
            raise ValueError('reader: cannot read %r at %d' % (text[i:i + 20], i))
        i = mt.end()
        k = mt.lastgroup
        if k == 'ws':
            continue
        out.append((k, mt.group(k)))
    return out


class Reader:
    def __init__(self, K, toks):
        self.K, self.t, self.i, self.vars = K, toks, 0, {}

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else ('eof', None)

    def take(self, want=None):
        tok = self.peek()
        if want is not None and tok[1] != want:
            raise ValueError('reader: expected %r, got %r' % (want, tok))
        self.i += 1
        return tok

    def term(self, maxp):
        left, lp = self.primary(), 0
        while True:
            k, v = self.peek()
            if k not in ('op', 'punct') or v not in INFIX:
                return left
            p, typ = INFIX[v]
            if p > maxp or lp >= p:
                return left
            self.take()
            right = self.term(p if typ == 'xfy' else p - 1)
            left, lp = self.K.Vec([self.K.Atom(v), left, right]), p

    def args(self, close):
        out = [self.term(999)]
        while self.peek()[1] == ',':
            self.take()
            out.append(self.term(999))
        self.take(close)
        return out

    def primary(self):
        K = self.K
        k, v = self.take()
        if k == 'num':
            return int(v)
        if k == 'str':
            s = K.Str('')
            s.text = v[1:-1].replace('""', '"')
            return s
        if k == 'var':
            if v == '_':
                return K.Var()
            return self.vars.setdefault(v, K.Var())
        if k in ('atom', 'qatom'):
            name = v[1:-1].replace("''", "'") if k == 'qatom' else v
            if self.peek()[1] == '(':
                self.take()
                return K.Vec([K.Atom(name)] + self.args(')'))
            return K.Atom(name)
        if v == '(':
            t = self.term(1200)
            self.take(')')
            return t
        if v == '{':
            return K.Vec(self.args('}'))
        if v == '[':
            if self.peek()[1] == ']':
                self.take()
                return K.NIL
            items = [self.term(999)]
            while self.peek()[1] == ',':
                self.take()
                items.append(self.term(999))
            tail = K.NIL
            if self.peek()[1] == '|':
                self.take()
                tail = self.term(999)
            self.take(']')
            for x in reversed(items):
                tail = K.Cons(x, tail)
            return tail
        raise ValueError('reader: unexpected %r' % (v,))


def read_terms(K, text):
    toks, out, i = tokens(text), [], 0
    while i < len(toks):
        j = i
        while j < len(toks) and toks[j][0] != 'end':
            j += 1
        if j == len(toks):
            raise ValueError('reader: a clause without its end')
        r = Reader(K, toks[i:j])
        t = r.term(1200)
        if r.i != len(r.t):
            raise ValueError('reader: trailing %r' % (r.t[r.i:],))
        out.append(t)
        i = j + 1
    return out
