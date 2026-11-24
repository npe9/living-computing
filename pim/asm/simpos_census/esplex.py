"""ESP/KL0 tokenizer and operator-precedence term reader.

Operators: the ESP manual's table of system operators (ESPtex
program-e.tex, "System operators", lines ~7816-7852 of the held TeX),
plus the 700-level comparison/unification operators that table leaves
out (=, \\=, ==, \\==, <, >, =<, >=, =:=, =\\=, :=, is), as in DEC-10
Prolog.  Terms are tuples:
  ('var', name)  ('atom', name)  ('num', text)  ('str', text)
  ('cmp', name, [args])  ('list', [items], tail-or-None)  ('brace', term)
Each term also carries a line number: (kind, ..., line) is avoided;
instead nodes are lists [kind, payload..., line]."""
import re

SYMCH = set('+-*/\\^<>=~:.?@#&$`')
SOLO = set('!;,|')
PUNCT = set('()[]{}')

# name -> (prefix (type, prio) or None, infix (type, prio) or None, postfix)
OPS = {}


def op(name, typ, prio):
    pre, inf, post = OPS.get(name, (None, None, None))
    if typ in ('fx', 'fy'):
        pre = (typ, prio)
    elif typ in ('xf', 'yf'):
        post = (typ, prio)
    else:
        inf = (typ, prio)
    OPS[name] = (pre, inf, post)


for n, t, p in [
        ('class', 'fx', 1180), ('has', 'xfx', 1160), ('instance', 'fx', 1155),
        ('instance', 'xfx', 1155), ('local', 'fx', 1154), (';', 'xfy', 1150),
        (';', 'xf', 1150), ('|', 'xfx', 1150), ('with_macro', 'xfx', 1140),
        ('before', 'fx', 1140), ('after', 'fx', 1140), ('nature', 'fx', 1120),
        ('component', 'fx', 1120), ('attribute', 'fx', 1120), (':-', 'fx', 1100),
        (':-', 'xfx', 1100), ('?-', 'fx', 1100), ('-->', 'xfx', 1100),
        ('=>', 'xfx', 1099), ('==>', 'xfx', 1099), ('when', 'yfx', 1098),
        ('where', 'yfx', 1098), ('with', 'fx', 1098), ('with', 'yfx', 1098),
        ('by', 'fx', 1098), ('by', 'yfx', 1098), ('mode', 'fx', 1080),
        ('public', 'fx', 1080), ('->', 'xfy', 1040), (',', 'xfy', 1000),
        ('`', 'fx', 999), ('spy', 'fy', 900), ('cspy', 'fy', 900),
        ('nospy', 'fy', 900), ('\\+', 'fy', 900), ('=..', 'xfx', 700),
        ('@<', 'xfx', 700), ('@>', 'xfx', 700), ('@=<', 'xfx', 700),
        ('@>=', 'xfx', 700), ('+', 'yfx', 500), ('+', 'fx', 500),
        ('-', 'yfx', 500), ('-', 'fx', 500), ('/\\', 'yfx', 500),
        ('\\/', 'yfx', 500), ('xor', 'yfx', 500), ('*', 'yfx', 400),
        ('/', 'yfx', 400), ('<<', 'yfx', 400), ('>>', 'yfx', 400),
        ('div', 'yfx', 400), ('mod', 'xfx', 400), ('^', 'xfy', 200),
        ('!', 'yfx', 200), (':', 'fy', 100), (':', 'xfx', 100),
        ('#', 'fy', 90), ('#', 'xfx', 90), ('##', 'xfx', 50),
        # not in the manual's table (standard Prolog):
        ('=', 'xfx', 700), ('\\=', 'xfx', 700), ('==', 'xfx', 700),
        ('\\==', 'xfx', 700), ('<', 'xfx', 700), ('>', 'xfx', 700),
        ('=<', 'xfx', 700), ('>=', 'xfx', 700), ('=:=', 'xfx', 700),
        ('=\\=', 'xfx', 700), (':=', 'xfx', 700), ('is', 'xfx', 700),
        ('\\', 'fy', 200), ('//', 'yfx', 400), ('rem', 'yfx', 400)]:
    op(n, t, p)

SYMOPS = []
BASE_OPS = None


def refresh():
    SYMOPS[:] = sorted((k for k in OPS if k and all(c in SYMCH for c in k)), key=len, reverse=True)


def reset_ops():
    """Back to the system operator table (call once per file)."""
    global BASE_OPS
    if BASE_OPS is None:
        BASE_OPS = dict(OPS)
    OPS.clear()
    OPS.update(BASE_OPS)
    refresh()


def remove_op(name, typ):
    pre, inf, post = OPS.get(name, (None, None, None))
    if typ in ('fx', 'fy'):
        pre = None
    elif typ in ('xf', 'yf'):
        post = None
    else:
        inf = None
    if pre or inf or post:
        OPS[name] = (pre, inf, post)
    else:
        OPS.pop(name, None)


refresh()


def jis_decode(raw):
    """Tolerant ISO-2022-JP: ESC ( B/J/H = ASCII, ESC $ @/B = JIS X 0208
    (each pair via EUC-JP; an unmapped pair, e.g. NEC row 13, becomes
    U+3013), ESC ( I = katakana; stray bytes >= 0x80 become U+3013.
    Newlines are kept, so line numbers are those of the file."""
    out, i, n, mode, bad = [], 0, len(raw), 'a', 0
    while i < n:
        b = raw[i]
        if b == 0x1b and i + 2 < n:
            s = raw[i + 1:i + 3]
            if s in (b'(B', b'(J', b'(H'):
                mode = 'a'; i += 3; continue
            if s in (b'$@', b'$B'):
                mode = 'k'; i += 3; continue
            if s == b'(I':
                mode = 'h'; i += 3; continue
            if s == b'$(' and i + 3 < n:
                mode = 'k'; i += 4; continue
        if b in (0x0a, 0x0d):
            out.append(chr(b)); i += 1
            continue
        if mode == 'k' and 0x21 <= b < 0x7f and i + 1 < n and 0x21 <= raw[i + 1] < 0x7f:
            try:
                out.append(bytes([b | 0x80, raw[i + 1] | 0x80]).decode('euc_jp'))
            except UnicodeDecodeError:
                out.append('〓'); bad += 1
            i += 2
            continue
        if mode == 'h' and 0x21 <= b < 0x60:
            out.append(chr(0xff61 + b - 0x21)); i += 1
            continue
        if b >= 0x80:
            out.append('〓'); bad += 1
        else:
            out.append(chr(b))
        i += 1
    return ''.join(out), bad


def decode(raw):
    """bytes -> (str, encoding label)."""
    if b'\x1b' in raw:
        t, bad = jis_decode(raw)
        return t, 'jis' if not bad else 'jis(%d unmapped)' % bad
    for enc in ('ascii', 'utf-8', 'euc_jp', 'shift_jis'):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            pass
    return raw.decode('latin-1'), 'latin-1'


def isalnum_(c):
    return c.isalnum() or c == '_' or ord(c) > 0x7f and not c.isspace() and c not in '　'


def tokenize(text):
    """[(type, value, line, ws_before)].  types: atom var num str qatom punct
    end.  'end' is the clause-terminating full stop."""
    toks = []
    i, n, line = 0, len(text), 1
    ws = True
    while i < n:
        c = text[i]
        if c == '\n':
            line += 1
            i += 1
            ws = True
            continue
        if c.isspace() or c == '　':
            i += 1
            ws = True
            continue
        if c == '%':
            j = text.find('\n', i)
            i = n if j < 0 else j
            ws = True
            continue
        if c == '/' and text.startswith('/*', i):
            j = text.find('*/', i + 2)
            j = n if j < 0 else j + 2
            line += text.count('\n', i, j)
            i = j
            ws = True
            continue
        start_line = line
        if c.isdigit():
            m = re.compile(r"\d+'(\\.|.)|\d+(\.\d+([eE][+-]?\d+)?)?").match(text, i)
            # 0'c character code
            if m.group(0).startswith('0\'') or re.match(r"\d+'", m.group(0)):
                if text.startswith("0'", i):
                    toks.append(('num', text[i:i + 3], line, ws))
                    i += 3
                    ws = False
                    continue
                m = re.compile(r'\d+').match(text, i)
            toks.append(('num', m.group(0), line, ws))
            i = m.end()
        elif c == '_' or c.isascii() and c.isupper():
            j = i + 1
            while j < n and isalnum_(text[j]):
                j += 1
            toks.append(('var', text[i:j], line, ws))
            i = j
        elif isalnum_(c):
            j = i + 1
            while j < n and isalnum_(text[j]):
                j += 1
            toks.append(('atom', text[i:j], line, ws))
            i = j
        elif c in '"\'':
            j = i + 1
            buf = []
            while j < n:
                if text[j] == c:
                    if j + 1 < n and text[j + 1] == c:
                        buf.append(c)
                        j += 2
                        continue
                    break
                if text[j] == '\\' and j + 1 < n:
                    buf.append(text[j:j + 2])
                    j += 2
                    continue
                if text[j] == '\n':
                    line += 1
                buf.append(text[j])
                j += 1
            toks.append(('str' if c == '"' else 'qatom', ''.join(buf), start_line, ws))
            i = j + 1
        elif c in PUNCT:
            toks.append(('punct', c, line, ws))
            i += 1
        elif c in SOLO:
            toks.append(('atom' if c in '!;' else 'punct', c, line, ws))
            i += 1
        elif c in SYMCH:
            j = i
            while j < n and text[j] in SYMCH:
                j += 1
            s = text[i:j]
            if s == '.' and (j >= n or text[j].isspace() or text[j] == '%'):
                toks.append(('end', '.', line, ws))
                i = j
                ws = True
                continue
            # split an unknown symbol run into known operators, longest first
            parts = []
            if s in OPS:
                parts = [s]
            else:
                k = 0
                while k < len(s):
                    for o in SYMOPS:
                        if s.startswith(o, k):
                            parts.append(o)
                            k += len(o)
                            break
                    else:
                        # no operator matches here: keep the remaining run whole
                        parts.append(s[k:])
                        break
            first = True
            for p in parts:
                toks.append(('atom', p, line, ws if first else False))
                first = False
            i = j
        else:
            toks.append(('atom', c, line, ws))
            i += 1
        ws = False
    return toks


class ParseError(Exception):
    pass


TERMINATORS = {')', ']', '}', ',', '|'}


class Reader:
    """Pratt reader over a token slice."""

    def __init__(self, toks):
        self.t = toks
        self.i = 0

    def peek(self, k=0):
        j = self.i + k
        return self.t[j] if j < len(self.t) else ('eof', None, self.t[-1][2] if self.t else 0, True)

    def nxt(self):
        tok = self.peek()
        self.i += 1
        return tok

    def expect(self, v):
        tok = self.nxt()
        if tok[1] != v or tok[0] not in ('punct', 'atom'):
            raise ParseError('expected %r got %r at line %s' % (v, tok[1], tok[2]))

    def starts_term(self, tok):
        typ, v = tok[0], tok[1]
        if typ in ('eof', 'end'):
            return False
        if typ == 'punct':
            return v in '([{'
        if typ == 'atom' and v in OPS:
            pre, inf, post = OPS[v]
            if inf and not pre:
                return False
        return True

    def args(self):
        out = [self.parse(999)]
        while self.peek()[0] == 'punct' and self.peek()[1] == ',':
            self.nxt()
            out.append(self.parse(999))
        return out

    def primary(self, maxp):
        tok = self.nxt()
        typ, v, line = tok[0], tok[1], tok[2]
        if typ == 'var':
            return ['var', v, line], 0
        if typ == 'num':
            return ['num', v, line], 0
        if typ == 'str':
            return ['str', v, line], 0
        if typ == 'punct':
            if v == '(':
                t = self.parse(1200)
                self.expect(')')
                return t, 0
            if v == '[':
                if self.peek()[1] == ']' and self.peek()[0] == 'punct':
                    self.nxt()
                    return self.functor_or_atom('[]', line)
                items = self.args()
                tail = None
                if self.peek()[1] == '|' and self.peek()[0] == 'punct':
                    self.nxt()
                    tail = self.parse(999)
                self.expect(']')
                return ['list', items, tail, line], 0
            if v == '{':
                if self.peek()[1] == '}':
                    self.nxt()
                    return ['atom', '{}', line], 0
                t = self.parse(1200)
                self.expect('}')
                return ['brace', t, line], 0
            raise ParseError('unexpected %r at line %s' % (v, line))
        if typ in ('atom', 'qatom'):
            nt = self.peek()
            if nt[0] == 'punct' and nt[1] == '(' and not nt[3]:
                self.nxt()
                a = self.args()
                self.expect(')')
                return ['cmp', v, a, line], 0
            if typ == 'atom' and v in OPS:
                pre, inf, post = OPS[v]
                if pre:
                    # '-' followed by number: negative literal
                    if v == '-' and nt[0] == 'num' and not nt[3]:
                        self.nxt()
                        return ['num', '-' + nt[1], line], 0
                    if self.starts_term(nt) and not (nt[0] == 'atom' and nt[1] in OPS and OPS[nt[1]][1]
                                                       and not OPS[nt[1]][0] and nt[0] != 'punct'):
                        ptyp, pp = pre
                        argmax = pp - 1 if ptyp == 'fx' else pp
                        # lenient: a prefix operator above maxp (e.g. `instance`
                        # after `;`) is read as if parenthesized
                        rp = pp if pp <= maxp else 0
                        save = self.i
                        try:
                            arg = self.parse(argmax)
                            return ['cmp', v, [arg], line], rp
                        except ParseError:
                            self.i = save
                    return ['atom', v, line], (pre[1] if pre[1] <= maxp else 0)
                return ['atom', v, line], 0
            return ['atom', v, line], 0
        if typ == 'eof' or typ == 'end':
            raise ParseError('unexpected end at line %s' % line)
        raise ParseError('bad token %r line %s' % (tok, line))

    def functor_or_atom(self, name, line):
        return ['atom', name, line], 0

    def parse(self, maxp):
        left, lp = self.primary(maxp)
        while True:
            tok = self.peek()
            typ, v = tok[0], tok[1]
            if typ == 'punct' and v == ',':
                name = ','
            elif typ == 'punct' and v == '|':
                name = '|'
            elif typ == 'atom' and v in OPS:
                name = v
            else:
                break
            pre, inf, post = OPS.get(name, (None, None, None))
            if inf:
                ityp, ip = inf
                la = ip - 1 if ityp[0] == 'x' else ip
                ra = ip - 1 if ityp[2] == 'x' else ip
                if ip <= maxp and lp <= la:
                    nt = self.peek(1)
                    if self.starts_term(nt) or (nt[0] == 'atom' and nt[1] in OPS):
                        save = self.i
                        self.nxt()
                        try:
                            right = self.parse(ra)
                            left = ['cmp', name, [left, right], tok[2]]
                            lp = ip
                            continue
                        except ParseError:
                            self.i = save
                            if not post:
                                raise
            if post:
                ptyp, pp = post
                if pp <= maxp:
                    self.nxt()
                    left = ['cmp', name, [left], tok[2]]
                    lp = pp
                    continue
            break
        return left


def split_top(toks, sep=';'):
    """Split a token list at depth-0 occurrences of atom `sep`."""
    out, cur, depth = [], [], 0
    for tk in toks:
        if tk[0] == 'punct' and tk[1] in '([{':
            depth += 1
        elif tk[0] == 'punct' and tk[1] in ')]}':
            depth -= 1
        if depth == 0 and tk[0] == 'atom' and tk[1] == sep:
            out.append(cur)
            cur = []
            continue
        cur.append(tk)
    if cur:
        out.append(cur)
    return out


def read_all(toks):
    """Split at 'end' tokens and parse each as one term (1200)."""
    out, cur = [], []
    for tk in toks:
        if tk[0] == 'end':
            out.append(cur)
            cur = []
        else:
            cur.append(tk)
    if cur:
        out.append(cur)
    res = []
    for seg in out:
        if not seg:
            continue
        r = Reader(seg)
        try:
            t = r.parse(1200)
            if r.i != len(seg):
                raise ParseError('trailing tokens at line %s' % r.peek()[2])
            res.append((t, None, seg[0][2]))
        except ParseError as e:
            res.append((None, str(e), seg[0][2]))
    return res
