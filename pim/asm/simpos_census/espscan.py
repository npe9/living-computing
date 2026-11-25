"""ESP-aware requirement scanner for the IFS SIMPOS applications.

python3 -I espscan.py OUTDIR NAME=ROOT[+ROOT...] ...

For each program (NAME = one or more extracted archive roots), reads every
non-binary file whose text contains a class (or macro_bank) definition,
parses it with esplex (the ESP manual's operator table, plus each file's
add_operator directives and included files), and records:
  * classes defined (name, natures, slots per section, methods per section
    with arity, local predicates);
  * every method send `:m(R, A2..An)`, with arity n = number of arguments
    INCLUDING the receiver R (the ptf cross-check in ptfside.py shows the
    compiled selector arity counts the receiver too);
  * every goal that is not a method send, not a control construct and not
    a local predicate of the class it is in (= a built-in or macro);
  * `#C` class references, `a#b` constants, `X!slot` accesses, strings.
Writes OUTDIR/raw/<NAME>.json for report.py."""
import json
import os
import re
import sys
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import esplex  # noqa: E402

CLASSRE = re.compile(r'(^|\n)[ \t]*(class|macro_bank)[ \t\r\n]+\S+[ \t\r\n]+(has|with_macro)\b')
ADDOP = re.compile(r"add_operator\(\s*('(?:[^']|'')*'|\([^)]*\)|[^,\s]+)\s*,\s*(\w+)\s*,\s*(\d+)\s*\)")
INCL = re.compile(r'''^[ \t]*include\(\s*["']?([^"')]+)["']?\s*\)\s*\.''', re.M)
CONTROL = {(',', 2), (';', 2), ('->', 2), ('|', 2), ('\\+', 1), ('call', 1), ('not', 1),
           ('!', 0), ('true', 0), ('fail', 0)}
META3 = {'findall', 'bagof', 'setof'}
esplex.op('macro_bank', 'fx', 1180)
esplex.op('high_level_command', 'fx', 1180)
esplex.reset_ops()
PATHRE = re.compile(r'^(?:[\w$.*-]+::)?(?:>[\w$.*~-]+)+>?$|^[\w$.-]+:[\w$.*>-]*>[\w$.*>-]*$|^[\w$.-]+:[\w$.*-]+(\.[\w*]+)+$|^[\w$-]+:[\w$*-]+$')


def unq(s):
    s = s.strip()
    if s.startswith('(') and s.endswith(')'):
        s = s[1:-1].strip()
    if s.startswith("'") and s.endswith("'"):
        s = s[1:-1].replace("''", "'")
    return s


def is_binary(raw):
    return b'\x00' in raw[:4096]


# System class methods, other than create*/new, whose one fresh output is an
# instance of the class.  Each entry is READ from held source that sends an
# instance message to the result:
#   time now/2: gog-esp CH_CLOCK.ESP:33-34 binds `:now(#time,T)` to the slot
#   `time`, and :59-60 send it get_count/2 and set_count/2 (also gog-kl1).
INSTANCE_RESULT = {('time', 'now', 2)}

def name_of(t):
    """Class name from a term: atom, pkg##atom, #atom.  -> (pkg, name) or None."""
    if t is None:
        return None
    if t[0] in ('atom',):
        return (None, t[1])
    if t[0] == 'qatom':
        return (None, t[1])
    if t[0] == 'cmp' and t[1] == '##' and len(t[2]) == 2:
        a, b = t[2]
        if a[0] == 'atom' and b[0] == 'atom':
            return (a[1], b[1])
    if t[0] == 'cmp' and t[1] == '#' and len(t[2]) == 1:
        return name_of(t[2][0])
    return None


def classref(t):
    """#C or #p##C -> (pkg, C)."""
    if t[0] == 'cmp' and t[1] == '#' and len(t[2]) == 1:
        a = t[2][0]
        if a[0] == 'atom':
            return (None, a[1])
        if a[0] == 'cmp' and a[1] == '##' and len(a[2]) == 2 and a[2][0][0] == 'atom' and a[2][1][0] == 'atom':
            return (a[2][0][1], a[2][1][1])
    return None


def flat(t, op=','):
    if t is not None and t[0] == 'cmp' and t[1] == op and len(t[2]) == 2:
        return flat(t[2][0], op) + flat(t[2][1], op)
    return [] if t is None else [t]


def line_of(t):
    return t[-1] if isinstance(t[-1], int) else 0


def vars_in(t, acc):
    if t is None:
        return acc
    k = t[0]
    if k == 'var':
        if t[1] != '_':
            acc.append(t[1])
    elif k == 'cmp':
        for a in t[2]:
            vars_in(a, acc)
    elif k == 'list':
        for a in t[1]:
            vars_in(a, acc)
        vars_in(t[2], acc)
    elif k == 'brace':
        vars_in(t[1], acc)
    return acc


class File:
    pass


class Program:
    def __init__(self, name, roots):
        self.name = name
        self.roots = roots
        self.files = []          # (relpath, abspath)
        self.classes = {}        # name -> info
        self.dupes = collections.Counter()
        self.sends = []          # dict rows
        self.goals = []
        self.refs = []
        self.consts = []
        self.slots = []
        self.strings = []
        self.directives = []
        self.allsends = []
        self.macros = set()
        self.stats = collections.Counter()
        self.parse_fail_sites = []
        self.allops = []

    def rel(self, p):
        for r in self.roots:
            if p.startswith(r):
                return os.path.basename(r.rstrip('/')) + p[len(r):]
        return p


def find_include(prog, name):
    base = re.split(r'[>:/]', name)[-1].lower()
    for rel, p in prog.allfiles:
        if os.path.basename(p).lower() == base or os.path.basename(p).lower().startswith(base + '.'):
            return p
    return None


def ops_from_text(text):
    out = []
    for m in ADDOP.finditer(text):
        out.append(('add', unq(m.group(1)), m.group(2), int(m.group(3))))
    for m in re.finditer(r"remove_operator\(\s*('(?:[^']|'')*'|\([^)]*\)|[^,\s]+)\s*,\s*(\w+)\s*(?:,\s*\d+\s*)?\)", text):
        out.append(('rm', unq(m.group(1)), m.group(2), 0))
    return out


def apply_ops(ops, removes=False):
    for k, n, t, p in ops:
        if k == 'add':
            esplex.op(n, t, p)
        elif removes:
            esplex.remove_op(n, t)
    esplex.refresh()


def parse_file(prog, path, text, extra_ops):
    """-> list of segments: ('class', header, items[(section, toks, term|None, err)]) or ('other', term, err, line)."""
    esplex.reset_ops()
    ops = ops_from_text(text)
    for m in INCL.finditer(text):
        ip = find_include(prog, m.group(1))
        if ip:
            itext, _ = esplex.decode(open(ip, 'rb').read())
            ops = ops_from_text(itext) + ops
            prog.directives.append(dict(kind='include', name=m.group(1), file=prog.rel(path),
                                        line=text.count('\n', 0, m.start()) + 1, resolved=prog.rel(ip)))
    apply_ops([o for o in ops if o[0] == 'add'] + list(extra_ops))
    toks = esplex.tokenize(text)
    segs, cur = [], []
    for t in toks:
        if t[0] == 'end':
            segs.append(cur)
            cur = []
        else:
            cur.append(t)
    if cur:
        segs.append(cur)
    out = []
    nerr = 0
    segs2 = []
    for seg in segs:
        # text before a line-initial `class` (e.g. a pasted editor stamp
        # ">sys>user>kaoru>kk_tr_ed.esp.19, 20-Feb-87 ...") is split off
        cut = None
        for j in range(1, len(seg)):
            t = seg[j]
            if t[0] == 'atom' and t[1] in ('class', 'macro_bank') and seg[j - 1][2] < t[2] \
                    and any(x[0] == 'atom' and x[1] == 'has' for x in seg[j:j + 12]):
                cut = j
                break
        if cut and not (seg[0][0] == 'atom' and seg[0][1] in ('class', 'macro_bank')):
            segs2.append(seg[:cut])
            segs2.append(seg[cut:])
            prog.stats['junk_before_class'] += 1
        else:
            segs2.append(seg)
    for seg in segs2:
        if not seg:
            continue
        if seg[0][0] == 'atom' and seg[0][1] in ('class', 'macro_bank'):
            # header up to depth-0 'has'
            depth, k = 0, None
            for j, t in enumerate(seg):
                if t[0] == 'punct' and t[1] in '([{':
                    depth += 1
                elif t[0] == 'punct' and t[1] in ')]}':
                    depth -= 1
                elif depth == 0 and t[0] == 'atom' and t[1] == 'has':
                    k = j
                    break
            if k is None:
                out.append(('other', None, 'class without has', seg[0][2], seg))
                nerr += 1
                continue
            header = seg[1:k]
            items = []
            section = 'class'
            for it in esplex.split_top(seg[k + 1:]):
                if not it:
                    continue
                while it and it[0][0] == 'atom' and it[0][1] in ('instance', 'local') and \
                        not (len(it) > 1 and it[1][0] == 'punct' and it[1][1] == '(' and not it[1][3]):
                    section = it[0][1]
                    it = it[1:]
                if not it:
                    continue
                if it[0][0] == 'atom' and it[0][1] == 'end' and len(it) == 1:
                    continue
                r = esplex.Reader(it)
                try:
                    term = r.parse(1200)
                    if r.i != len(it):
                        raise esplex.ParseError('trailing tokens at line %s' % r.peek()[2])
                    items.append((section, it, term, None))
                except esplex.ParseError as e:
                    items.append((section, it, None, str(e)))
                    nerr += 1
            out.append(('class', seg[0][1], header, items, seg[0][2]))
        else:
            r = esplex.Reader(seg)
            try:
                term = r.parse(1200)
                if r.i != len(seg):
                    raise esplex.ParseError('trailing')
                out.append(('other', term, None, seg[0][2], seg))
                # in-order operator directives
                if term[0] == 'cmp' and term[1] in ('add_operator', 'remove_operator'):
                    pass
            except esplex.ParseError as e:
                out.append(('other', None, str(e), seg[0][2], seg))
                nerr += 1
    return out, nerr, ops


def header_info(header):
    """tokens between class and has -> (name, pkg, macro_bank)."""
    r = esplex.Reader(header)
    try:
        t = r.parse(1200)
    except esplex.ParseError:
        return (header[0][1] if header else '?'), None, None
    mb = None
    if t[0] == 'cmp' and t[1] == 'with_macro':
        mb = name_of(t[2][1])
        t = t[2][0]
    nm = name_of(t)
    if nm:
        return nm[1], nm[0], mb
    return (header[0][1] if header else '?'), None, mb


def slot_defs(term):
    """attribute/component body -> [(slot, init_term or None, body or None)]."""
    out = []
    for s in flat(term):
        body = None
        if s[0] == 'cmp' and s[1] == ':-' and len(s[2]) == 2:
            s, body = s[2]
        if s[0] == 'cmp' and s[1] == ':=' and len(s[2]) == 2:
            nm = s[2][0]
            out.append((nm[1] if nm[0] in ('atom', 'qatom') else repr(nm[1]), s[2][1], body))
        elif s[0] == 'cmp' and s[1] == 'is' and len(s[2]) == 2 and s[2][0][0] in ('atom', 'qatom'):
            # `slot is Class`: the slot holds an instance of Class
            out.append((s[2][0][1], ['cmp', '#is', [s[2][1]], line_of(s)], None))
        elif s[0] in ('atom', 'qatom'):
            out.append((s[1], None, None))
    return out


def collect_classes(prog, parsed):
    for rel, segs in parsed:
        for seg in segs:
            if seg[0] != 'class':
                continue
            _, kw, header, items, line = seg
            name, pkg, mb = header_info(header)
            info = dict(name=name, pkg=pkg, macro_bank=mb, kw=kw, file=rel, line=line,
                        natures=[], slots={'class': {}, 'instance': {}}, methods=set(), locals=set(),
                        items=items)
            for section, toks, term, err in items:
                if term is None:
                    # token-level: still record method heads for exclusion
                    if toks and toks[0][1] == ':' and len(toks) > 2 and toks[2][1] == '(':
                        info['methods'].add((section, toks[1][1], -1))
                    continue
                t = term
                if t[0] == 'cmp' and t[1] == 'nature':
                    for n in flat(t[2][0]):
                        nm = name_of(n)
                        if nm:
                            info['natures'].append(nm)
                    continue
                if t[0] == 'cmp' and t[1] in ('attribute', 'component'):
                    for sl, init, body in slot_defs(t[2][0]):
                        info['slots']['instance' if section != 'class' else 'class'][sl] = (init, body)
                    continue
                h = head_of(t)
                if h is None:
                    continue
                if h[0] == 'macro':
                    pat = t
                    while pat[0] == 'cmp' and pat[1] in ('when', 'where', ':-') and len(pat[2]) == 2:
                        pat = pat[2][0]
                    if pat[0] == 'cmp' and pat[1] in ('=>', '==>') and pat[2]:
                        lhs = pat[2][0]
                        if lhs[0] == 'cmp':
                            prog.macros.add((lhs[1], len(lhs[2])))
                        elif lhs[0] in ('atom', 'qatom'):
                            prog.macros.add((lhs[1], 0))
                    continue
                kind, nm, ar = h
                if kind == 'method':
                    info['methods'].add((section if section != 'local' else 'instance', nm, ar))
                elif kind == 'demon':
                    pass
                elif kind == 'local':
                    info['locals'].add((nm, ar))
            if name in prog.classes:
                prog.dupes[name] += 1
                # merge (same class defined twice, e.g. two versions)
                old = prog.classes[name]
                old['methods'] |= info['methods']
                old['locals'] |= info['locals']
                for nat in info['natures']:
                    if nat not in old['natures']:
                        old['natures'].append(nat)
                for s in ('class', 'instance'):
                    old['slots'][s].update(info['slots'][s])
                old.setdefault('more_items', []).append((rel, items))
            else:
                prog.classes[name] = info


def head_of(t):
    """-> ('method'|'demon'|'local'|'macro'|None, name, arity)."""
    if t[0] == 'cmp' and t[1] in ('before', 'after') and len(t[2]) == 1:
        inner = t[2][0]
        h = head_of(inner)
        if h and h[0] == 'method':
            return ('demon', h[1], h[2])
        return h
    if t[0] == 'cmp' and t[1] in ('=>', '==>', '-->', 'when', 'where', 'with', 'by'):
        return ('macro', t[1], 0)
    if t[0] == 'cmp' and t[1] == ':-' and len(t[2]) == 2:
        return head_of(t[2][0])
    if t[0] == 'cmp' and t[1] == ':' and len(t[2]) == 1:
        m = t[2][0]
        if m[0] == 'cmp':
            return ('method', m[1], len(m[2]))
        if m[0] == 'atom':
            return ('method', m[1], 0)
        return None
    if t[0] == 'cmp' and t[1] == ':' and len(t[2]) == 2:
        # before:m(...) written as infix
        a, b = t[2]
        if a[0] == 'atom' and a[1] in ('before', 'after') and b[0] == 'cmp':
            return ('demon', b[1], len(b[2]))
    if t[0] == 'cmp':
        return ('local', t[1], len(t[2]))
    if t[0] == 'atom':
        return ('local', t[1], 0)
    return None


def closure(prog, cname, seen=None):
    """User classes reachable by natures (incl. cname) and external natures."""
    if seen is None:
        seen = []
    ext = []
    if cname in seen:
        return seen, ext
    seen.append(cname)
    info = prog.classes.get(cname)
    if info is None:
        return seen, ext
    for pkg, n in info['natures']:
        if n in prog.classes:
            s2, e2 = closure(prog, n, seen)
            for e in e2:
                if e not in ext:
                    ext.append(e)
        else:
            if n not in ext:
                ext.append(n)
    return seen, ext


class Analyzer:
    def __init__(self, prog):
        self.p = prog
        self.method_names = collections.defaultdict(set)   # (name, arity) -> {(class, section)}
        for cn, info in prog.classes.items():
            for sec, nm, ar in info['methods']:
                self.method_names[(nm, ar)].add((cn, sec))
        self.slot_types = collections.defaultdict(dict)   # class -> slot -> ('inst'|'class', C)
        self.local_types = collections.defaultdict(dict)  # (class, name, arity) -> {argpos: type}
        self.clo = {cn: closure(prog, cn) for cn in prog.classes}
        self.desc = collections.defaultdict(set)
        for d, (users, _e) in self.clo.items():
            for u in users:
                if u != d:
                    self.desc[u].add(d)

    def ext_of(self, cname):
        """External natures of cname's closure, then (for a mixin) those of
        the user classes that inherit it."""
        _u, ext = self.clo.get(cname, ([cname], []))
        ext = list(ext)
        if not ext:
            for d in sorted(self.desc.get(cname, ())):
                for e in self.clo[d][1]:
                    if e not in ext:
                        ext.append(e)
        return ext

    def in_descendant(self, cname, section, nm, ar, slot=False):
        for d in self.desc.get(cname, ()):
            if slot and self.user_has_slot(d, nm, False):
                return True
            if not slot and self.user_has_method(d, section, nm, ar, False):
                return True
        return False

    def user_has_method(self, cname, section, nm, ar, desc=True):
        users, _ext = self.clo.get(cname, ([cname], []))
        if desc and self.in_descendant(cname, section, nm, ar):
            self.p.stats['send_mixin_user'] += 1
            return True
        for u in users:
            info = self.p.classes.get(u)
            if info and ((section, nm, ar) in info['methods'] or (section, nm, -1) in info['methods']):
                return True
        return False

    def user_has_slot(self, cname, slot, desc=True):
        users, _ = self.clo.get(cname, ([cname], []))
        if desc and self.in_descendant(cname, None, slot, 0, slot=True):
            self.p.stats['slot_mixin_user'] += 1
            return True
        for u in users:
            info = self.p.classes.get(u)
            if info and (slot in info['slots']['instance'] or slot in info['slots']['class']):
                return True
        return False

    # ---------------- per clause ----------------
    def clause(self, cls, section, term, rel, record=True):
        info = self.p.classes[cls]
        env = {}
        seen = set()
        head, body = term, None
        demon = False
        if term[0] == 'cmp' and term[1] in ('before', 'after') and len(term[2]) == 1:
            head = term[2][0]
            demon = True
        if head[0] == 'cmp' and head[1] == ':-' and len(head[2]) == 2:
            head, body = head[2]
        elif head[0] == 'cmp' and head[1] == ':-' and len(head[2]) == 1:
            head, body = None, head[2][0]
        hkind = None
        if head is not None:
            if head[0] == 'cmp' and head[1] == ':' and len(head[2]) == 1 and head[2][0][0] == 'cmp':
                m = head[2][0]
                hkind = 'method'
                if m[2] and m[2][0][0] == 'var':
                    env[m[2][0][1]] = ('self', cls, 'class' if section == 'class' else 'instance')
            elif head[0] == 'cmp' and head[1] == ':' and len(head[2]) == 2:
                m = head[2][1]
                if m[0] == 'cmp' and m[2] and m[2][0][0] == 'var':
                    env[m[2][0][1]] = ('self', cls, 'class' if section == 'class' else 'instance')
            if hkind is None and section == 'local' and head[0] == 'cmp':
                lt = self.local_types.get((cls, head[1], len(head[2])), {})
                for pos, ty in lt.items():
                    a = head[2][pos]
                    if a[0] == 'var' and a[1] not in env:
                        env[a[1]] = ty
            seen.update(vars_in(head, []))
            self.walk_terms(cls, head, rel, env, record, in_head=True)
        if body is not None:
            self.goal(cls, section, body, rel, env, seen, record)
        if head is not None and hkind is None and section == 'local' and record:
            pass

    def goal(self, cls, section, g, rel, env, seen, record):
        k = g[0]
        if k == 'var':
            if record:
                self.add_goal('call', 1, rel, line_of(g), cls, 'meta-call (variable goal)')
            seen.add(g[1])
            return
        if k == 'cmp' and g[1] in (',', ';', '->', '|') and len(g[2]) == 2:
            self.goal(cls, section, g[2][0], rel, env, seen, record)
            self.goal(cls, section, g[2][1], rel, env, seen, record)
            return
        if k == 'cmp' and g[1] in ('\\+', 'call', 'not') and len(g[2]) == 1:
            if g[1] != '\\+' and record:
                self.add_goal(g[1], 1, rel, line_of(g), cls, 'control')
            self.goal(cls, section, g[2][0], rel, env, seen, record)
            return
        if k == 'cmp' and g[1] == ':' and len(g[2]) == 1:
            self.send(cls, section, g[2][0], rel, env, seen, record, line_of(g))
            return
        if k == 'cmp' and g[1] in META3 and len(g[2]) == 3:
            if record:
                self.add_goal(g[1], 3, rel, line_of(g), cls, 'builtin')
            self.walk_terms(cls, g[2][0], rel, env, record)
            self.goal(cls, section, g[2][1], rel, env, seen, record)
            self.walk_terms(cls, g[2][2], rel, env, record)
            seen.update(vars_in(g, []))
            return
        if k in ('atom', 'qatom'):
            nm, ar, args = g[1], 0, []
        elif k == 'cmp':
            nm, ar, args = g[1], len(g[2]), g[2]
        else:
            if record:
                self.add_goal('<%s>' % k, 0, rel, line_of(g), cls, 'non-callable goal')
            return
        # typing by unification
        if nm == '=' and ar == 2:
            a, b = args
            for x, y in ((a, b), (b, a)):
                if x[0] == 'var' and x[1] not in env:
                    ty = self.type_of(cls, y, env)
                    if ty:
                        env[x[1]] = ty
        if nm == ':=' and ar == 2:
            a, b = args
            if a[0] == 'cmp' and a[1] == '!' and len(a[2]) == 2:
                ty = self.type_of(cls, b, env)
                rt = self.type_of(cls, a[2][0], env)
                if ty and rt and rt[0] == 'self' and a[2][1][0] == 'atom':
                    self.slot_types[cls].setdefault(a[2][1][1], ty)
        if (nm, ar) in CONTROL:
            kind = 'control'
        elif (nm, ar) in self.p.classes[cls]['locals']:
            kind = 'local'
        elif (nm, ar) in self.p.macros:
            kind = 'user-macro'
        else:
            kind = 'builtin'
        if record and kind != 'local':
            self.add_goal(nm, ar, rel, line_of(g), cls, kind)
        if kind == 'local':
            if record:
                self.p.stats['local_calls'] += 1
            lt = self.local_types[(cls, nm, ar)]
            for pos, a in enumerate(args):
                ty = self.type_of(cls, a, env)
                if ty and pos not in lt:
                    lt[pos] = ty
        for a in args:
            self.walk_terms(cls, a, rel, env, record)
        seen.update(vars_in(g, []))

    def type_of(self, cls, t, env):
        if t[0] == 'var':
            return env.get(t[1])
        if t[0] == 'cmp' and t[1] == '#is':
            nm = name_of(t[2][0])
            return ('inst', nm[1], nm[0]) if nm else None
        cr = classref(t)
        if cr:
            return ('class', cr[1], cr[0])
        if t[0] == 'cmp' and t[1] == '!' and len(t[2]) == 2:
            rt = self.type_of(cls, t[2][0], env)
            sl = t[2][1]
            if rt and rt[0] == 'self' and sl[0] == 'atom':
                return self.slot_types.get(rt[1], {}).get(sl[1])
        return None

    def send(self, cls, section, m, rel, env, seen, record, line):
        if m[0] == 'var':
            if record:
                self.add_send('?', 'unknown', '<variable selector>', 0, 'dynamic-selector', rel, line, cls, None)
            return
        if m[0] == 'atom':
            nm, args = m[1], []
        elif m[0] == 'cmp':
            nm, args = m[1], m[2]
        else:
            return
        ar = len(args)
        if record:
            self.p.allsends.append((cls, nm, ar))
        rcv = args[0] if args else None
        ty = self.type_of(cls, rcv, env) if rcv is not None else None
        rtext = None
        if record:
            self.resolve_and_add(cls, nm, ar, ty, rcv, rel, line, args)
        # binding: create*/new on a class -> instance in the single fresh var
        if ty and ty[0] in ('class',) or (ty and ty[0] == 'self' and ty[2] == 'class'):
            cname = ty[1]
            # a user class that defines its own create*/new may be a factory:
            # bind only system-class creates and user classes without one
            factory = cname in self.p.classes and nm != 'new' and \
                self.user_has_method(cname, 'class', nm, ar, False)
            if factory and record:
                self.p.stats['create_not_bound_user_factory'] += 1
            if (nm.startswith('create') or nm == 'new' or (cname, nm, ar) in INSTANCE_RESULT) \
                    and not factory:
                fresh = []
                for a in args[1:]:
                    if a[0] == 'var' and a[1] != '_' and a[1] not in seen and a[1] not in env:
                        fresh.append(a[1])
                if len(fresh) == 1:
                    env[fresh[0]] = ('inst', cname, ty[2] if ty[0] == 'class' else None)
        for a in args:
            self.walk_terms(cls, a, rel, env, record)
        seen.update(vars_in(m, []))

    def resolve_and_add(self, cls, nm, ar, ty, rcv, rel, line, args):
        p = self.p
        if ty is None:
            if (nm, ar) in self.method_names:
                p.stats['send_untyped_user'] += 1
                self.add_send('?', 'unknown', nm, ar, 'untyped-user-defined', rel, line, cls, None)
                return
            self.add_send('?', 'unknown', nm, ar, 'unattributed', rel, line, cls, None)
            return
        kind0 = ty[0]
        if kind0 == 'class':
            target, sec, how = ty[1], 'class', 'class'
        elif kind0 == 'inst':
            target, sec, how = ty[1], 'instance', 'create-bound'
        else:  # self
            target, sec, how = ty[1], ty[2], 'self'
        if target in p.classes:
            if self.user_has_method(target, sec, nm, ar):
                p.stats['send_resolved_user'] += 1
                return
            ext = self.ext_of(target)
            hw = {'class': 'class-inherited', 'create-bound': 'create-bound-inherited',
                  'self': 'self-inherited'}[how]
            tgt = '{%s}' % '|'.join(ext) if ext else '<root>'
            self.add_send(tgt, sec, nm, ar, hw, rel, line, cls, ext)
        else:
            self.add_send(target, sec, nm, ar, how, rel, line, cls, None)

    def walk_terms(self, cls, t, rel, env, record, in_head=False):
        if t is None:
            return
        k = t[0]
        if k == 'str':
            if record:
                self.p.strings.append((t[1], rel, line_of(t)))
            return
        if k == 'list':
            for a in t[1]:
                self.walk_terms(cls, a, rel, env, record, in_head)
            self.walk_terms(cls, t[2], rel, env, record, in_head)
            return
        if k == 'brace':
            self.walk_terms(cls, t[1], rel, env, record, in_head)
            return
        if k != 'cmp':
            return
        if record:
            cr = classref(t)
            if cr:
                self.p.refs.append(dict(cls=cr[1], pkg=cr[0], file=rel, line=line_of(t), user=cls))
                return
            if t[1] == '#' and len(t[2]) == 1 and t[2][0][0] in ('str', 'num'):
                self.p.stats['char_literal'] += 1
                return
            if t[1] == '#' and len(t[2]) == 2:
                a, b = t[2]
                self.p.consts.append(('%s#%s' % (a[1] if a[0] in ('atom', 'var', 'num') else a[0],
                                                   b[1] if b[0] in ('atom', 'num', 'var') else b[0]),
                                      rel, line_of(t), cls))
                return
            if t[1] == '!' and len(t[2]) == 2:
                rt = self.type_of(cls, t[2][0], env)
                sl = t[2][1]
                if sl[0] == 'atom':
                    self.slot_access(cls, rt, sl[1], rel, line_of(t))
            if t[1] == ':' and len(t[2]) == 1 and not in_head:
                # a send in argument position (e.g. inside refute/1)
                self.send(cls, 'instance', t[2][0], rel, env, set(), record, line_of(t))
                return
        for a in t[2]:
            self.walk_terms(cls, a, rel, env, record, in_head)

    def slot_access(self, cls, rt, slot, rel, line):
        p = self.p
        if rt is None:
            p.stats['slot_untyped'] += 1
            return
        if rt[0] == 'self' or rt[0] == 'inst' or rt[0] == 'class':
            target = rt[1]
            sec = 'class' if rt[0] == 'class' or (rt[0] == 'self' and rt[2] == 'class') else 'instance'
            if target in p.classes:
                if self.user_has_slot(target, slot):
                    p.stats['slot_user'] += 1
                    return
                ext = self.ext_of(target)
                tgt = '{%s}' % '|'.join(ext) if ext else '<root>'
                self.add_send(tgt, sec, '!' + slot, 0, 'slot-inherited', rel, line, cls, ext, kind='slot')
            else:
                self.add_send(target, sec, '!' + slot, 0, 'slot', rel, line, cls, None, kind='slot')

    def add_send(self, target, sec, nm, ar, how, rel, line, cls, ext, kind='send'):
        self.p.sends.append(dict(cls=target, sec=sec, m=nm, ar=ar, how=how, file=rel, line=line,
                                 user=cls, kind=kind))

    def add_goal(self, nm, ar, rel, line, cls, kind):
        self.p.goals.append(dict(name=nm, ar=ar, file=rel, line=line, user=cls, kind=kind))

    # ---------------- per class ----------------
    def run_class(self, cname, info, record):
        rels = [(info['file'], info['items'])] + info.get('more_items', [])
        for rel, items in rels:
            for section, toks, term, err in items:
                if term is None:
                    if record:
                        self.token_fallback(cname, toks, rel)
                    continue
                t = term
                if t[0] == 'cmp' and t[1] == 'nature':
                    continue
                if t[0] == 'cmp' and t[1] in ('attribute', 'component'):
                    for sl, init, body in slot_defs(t[2][0]):
                        env, seen = {}, set()
                        if init is not None:
                            if record and init[0] == 'cmp' and init[1] == '#is':
                                nm_ = name_of(init[2][0])
                                if nm_:
                                    self.p.refs.append(dict(cls=nm_[1], pkg=nm_[0], file=rel, line=line_of(init),
                                                            user=cname, how='slot-is'))
                            ty = self.type_of(cname, init, env)
                            if body is not None:
                                self.goal(cname, section, body, rel, env, seen, record)
                                ty = ty or self.type_of(cname, init, env)
                            if ty:
                                self.slot_types[cname].setdefault(sl, ty)
                            if body is None:
                                self.walk_terms(cname, init, rel, env, record)
                    continue
                h = head_of(t)
                if h and h[0] == 'macro':
                    if record:
                        self.p.stats['macro_items'] += 1
                    self.walk_macro(cname, t, rel, record)
                    continue
                self.clause(cname, section, t, rel, record)

    def walk_macro(self, cname, t, rel, record):
        # condition parts after :- are goals; everything else is data
        env, seen = {}, set()
        def rec(x):
            if x is None or x[0] != 'cmp':
                return
            if x[1] == ':-' and len(x[2]) == 2:
                self.walk_terms(cname, x[2][0], rel, env, record, in_head=True)
                self.goal(cname, 'class', x[2][1], rel, env, seen, record)
                return
            if x[1] in ('when', 'where') and len(x[2]) == 2:
                rec(x[2][0])
                self.goal(cname, 'class', x[2][1], rel, env, seen, record)
                return
            if x[1] in ('=>', '==>') and len(x[2]) == 2:
                lhs, rhs = x[2]
                self.walk_terms(cname, lhs, rel, env, record, in_head=True)
                if rhs[0] == 'cmp' and (rhs[1] in (',', ';', '->') or (rhs[1] == ':' and len(rhs[2]) == 1)):
                    if record:
                        self.p.stats['macro_rhs_as_goal'] += 1
                    self.goal(cname, 'class', rhs, rel, env, seen, record)
                else:
                    self.walk_terms(cname, rhs, rel, env, record)
                return
            for a in x[2]:
                rec(a)
        rec(t)

    def token_fallback(self, cname, toks, rel):
        """For an item the reader could not parse: every `: name (` at a goal
        position, arity = depth-1 commas + 1; receiver only if `#C`."""
        p = self.p
        p.stats['fallback_items'] += 1
        prev_ok = {',', '(', ';', ':-', '->', '|', '[', '\\+', '{'}
        n = len(toks)
        for i in range(n - 2):
            t = toks[i]
            if not (t[0] == 'atom' and t[1] == ':'):
                continue
            pv = toks[i - 1][1] if i > 0 else ';'
            if i > 0 and pv not in prev_ok and pv not in ('before', 'after'):
                continue
            a, b = toks[i + 1], toks[i + 2]
            if a[0] not in ('atom', 'qatom') or b[1] != '(' or b[3]:
                continue
            depth, ar, j, first = 0, 1, i + 2, []
            while j < n:
                tk = toks[j]
                if tk[0] == 'punct' and tk[1] in '([{':
                    depth += 1
                elif tk[0] == 'punct' and tk[1] in ')]}':
                    depth -= 1
                    if depth == 0:
                        break
                elif depth == 1 and tk[0] == 'punct' and tk[1] == ',':
                    ar += 1
                elif depth == 1 and ar == 1:
                    first.append(tk)
                j += 1
            if i == 0 or pv in ('before', 'after'):
                continue  # a head
            nm = a[1]
            p.allsends.append((cname, nm, ar))
            if len(first) >= 2 and first[0][1] == '#' and first[-1][0] == 'atom':
                c = first[-1][1]
                if c in p.classes:
                    if self.user_has_method(c, 'class', nm, ar):
                        continue
                    ext = self.ext_of(c)
                    self.add_send('{%s}' % '|'.join(ext) if ext else '<root>', 'class', nm, ar,
                                  'fallback-class-inherited', rel, a[2], cname, ext)
                else:
                    self.add_send(c, 'class', nm, ar, 'fallback-class', rel, a[2], cname, None)
            elif (nm, ar) in self.method_names:
                p.stats['send_untyped_user'] += 1
                self.add_send('?', 'unknown', nm, ar, 'untyped-user-defined', rel, a[2], cname, None)
            else:
                self.add_send('?', 'unknown', nm, ar, 'fallback-unattributed', rel, a[2], cname, None)
        for i in range(n - 1):
            if toks[i][1] == '#' and toks[i + 1][0] == 'atom' and (i == 0 or toks[i - 1][0] in ('punct',) or toks[i - 1][1] in (':', ',')):
                if not (i + 2 < n and toks[i + 2][1] == '##'):
                    p.refs.append(dict(cls=toks[i + 1][1], pkg=None, file=rel, line=toks[i][2], user=cname, how='fallback'))


def scan_program(name, roots):
    prog = Program(name, roots)
    prog.allfiles = []
    for r in roots:
        for dp, dn, fn in os.walk(r):
            dn.sort()
            for f in sorted(fn):
                p = os.path.join(dp, f)
                prog.allfiles.append((prog.rel(p), p))
    texts = []
    for rel, p in prog.allfiles:
        raw = open(p, 'rb').read()
        if is_binary(raw) or len(raw) > 4_000_000:
            continue
        text, enc = esplex.decode(raw)
        if CLASSRE.search(text):
            texts.append((rel, p, text, enc))
            prog.stats['esp_files'] += 1
            prog.stats['enc_' + enc.split('(')[0]] += 1
            if '(' in enc:
                prog.stats['files_with_unmapped_jis'] += 1
    # program-wide operator union (for files that rely on operators set elsewhere)
    union = []
    for rel, p, text, enc in texts:
        union += [o for o in ops_from_text(text) if o[0] == 'add']
    parsed = []
    for rel, p, text, enc in texts:
        segs, nerr, ops = parse_file(prog, p, text, [])
        if nerr and union:
            segs2, nerr2, _ = parse_file(prog, p, text, union)
            if nerr2 < nerr:
                segs, nerr = segs2, nerr2
                prog.stats['files_using_program_ops'] += 1
        prog.stats['parse_failed_items'] += nerr
        parsed.append((rel, segs))
        for seg in segs:
            if seg[0] == 'class':
                prog.stats['items'] += len(seg[3])
                for it in seg[3]:
                    if it[3]:
                        prog.parse_fail_sites.append((rel, it[1][0][2] if it[1] else 0, it[3]))
            else:
                prog.stats['other_segments'] += 1
                term = seg[1]
                if term is not None and term[0] == 'cmp':
                    prog.directives.append(dict(kind='directive', name='%s/%d' % (term[1], len(term[2])),
                                                file=rel, line=seg[3],
                                                arg=(term[2][0][1] if term[2] and term[2][0][0] in ('atom', 'qatom', 'str') else '')))
                elif term is not None and term[0] in ('atom',):
                    prog.directives.append(dict(kind='directive', name=term[1] + '/0', file=rel, line=seg[3], arg=''))
    collect_classes(prog, parsed)
    an = Analyzer(prog)
    # pass 1 learns slot types, pass 2 records
    for _ in range(3):
        for cn, info in list(prog.classes.items()):
            an.run_class(cn, info, False)
    for cn, info in list(prog.classes.items()):
        an.run_class(cn, info, True)
    # natures and macro banks that are not user classes
    natures = []
    for cn, info in prog.classes.items():
        for pkg, n in info['natures']:
            natures.append(dict(cls=n, pkg=pkg, user=cn, file=info['file'], line=info['line'],
                                user_defined=n in prog.classes))
        if info['macro_bank']:
            natures.append(dict(cls=info['macro_bank'][1], pkg=info['macro_bank'][0], user=cn,
                                file=info['file'], line=info['line'], user_defined=info['macro_bank'][1] in prog.classes,
                                macro=True))
    classes_out = {cn: dict(file=i['file'], line=i['line'], pkg=i['pkg'], kw=i['kw'],
                            natures=['%s##%s' % (p, n) if p else n for p, n in i['natures']],
                            methods=sorted('%s:%s/%d' % m for m in i['methods']),
                            locals=sorted('%s/%d' % l for l in i['locals']),
                            slots={s: sorted(i['slots'][s]) for s in i['slots']},
                            macro_bank=i['macro_bank'])
                   for cn, i in prog.classes.items()}
    return dict(name=name, roots=roots, stats=dict(prog.stats), classes=classes_out,
                dupes=dict(prog.dupes), sends=prog.sends, goals=prog.goals, refs=prog.refs,
                consts=prog.consts, strings=prog.strings, directives=prog.directives,
                natures=natures, allsends=prog.allsends, macros=sorted(prog.macros), parse_fail_sites=prog.parse_fail_sites[:2000],
                files=[r for r, _ in prog.allfiles], esp_files=[t[0] for t in texts])


def main():
    out = sys.argv[1]
    os.makedirs(os.path.join(out, 'raw'), exist_ok=True)
    for spec in sys.argv[2:]:
        name, roots = spec.split('=', 1)
        res = scan_program(name, roots.split('+'))
        with open(os.path.join(out, 'raw', name + '.json'), 'w') as f:
            json.dump(res, f)
        s = res['stats']
        print(name, 'classes', len(res['classes']), 'sends', len(res['sends']), 'goals', len(res['goals']),
              'items', s.get('items'), 'failed', s.get('parse_failed_items'), 'esp_files', s.get('esp_files'))


if __name__ == '__main__':
    main()
