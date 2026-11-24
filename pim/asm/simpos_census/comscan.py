"""Librarian command files (.COM), login files and other command lists.

python3 -I comscan.py OUT.json NAME=ROOT[+ROOT] ...

A file is read if its name ends in .com (any case, not .comp) or starts
with login, or if its text (after comments) starts with `[` and holds
fxds/make_package/use_package/command(...).  Each is read as Prolog terms
(esplex).  Recorded: list items' functor/arity (the Librarian vocabulary),
login-file clause heads and the functors in their bodies, sends inside
refute(...), strings (pathnames)."""
import json
import os
import re
import sys
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import esplex  # noqa: E402

LIBWORDS = re.compile(r'\b(fxds|make_package|use_package|save_package|make_environment|command|load|compile)\s*\(')


def functors(t, acc, depth=0):
    if t is None:
        return
    if t[0] == 'cmp':
        acc.append(('%s/%d' % (t[1], len(t[2])), t[-1], depth))
        for a in t[2]:
            functors(a, acc, depth + 1)
    elif t[0] == 'list':
        for a in t[1]:
            functors(a, acc, depth + 1)
        functors(t[2], acc, depth + 1)
    elif t[0] == 'brace':
        functors(t[1], acc, depth + 1)


def strings(t, acc):
    if t is None:
        return
    if t[0] in ('str', 'qatom'):
        acc.append((t[1], t[-1]))
    elif t[0] == 'cmp':
        for a in t[2]:
            strings(a, acc)
    elif t[0] == 'list':
        for a in t[1]:
            strings(a, acc)
        strings(t[2], acc)
    elif t[0] == 'brace':
        strings(t[1], acc)


def main():
    out = {}
    for spec in sys.argv[2:]:
        name, roots = spec.split('=', 1)
        rows = []
        for r in roots.split('+'):
            base = os.path.basename(r.rstrip('/'))
            for dp, dn, fn in os.walk(r):
                for f in sorted(fn):
                    p = os.path.join(dp, f)
                    low = f.lower()
                    raw = open(p, 'rb').read()
                    if b'\x00' in raw[:4096] or len(raw) > 2_000_000:
                        continue
                    text, enc = esplex.decode(raw)
                    stripped = re.sub(r'%[^\n]*', '', text).strip()
                    kind = None
                    if re.search(r'\.com(\.\d+)?$', low):
                        kind = 'com'
                    elif low.startswith('login'):
                        kind = 'login'
                    elif stripped.startswith('[') and LIBWORDS.search(stripped[:2000]) \
                            and not re.search(r'(^|\n)\s*class\s', text):
                        kind = 'list'
                    if not kind:
                        continue
                    esplex.reset_ops()
                    toks = esplex.tokenize(text)
                    terms = esplex.read_all(toks)
                    rel = base + p[len(r):]
                    items, heads, body, strs, errs = [], [], [], [], 0
                    for t, err, line in terms:
                        if err:
                            errs += 1
                            continue
                        if t[0] == 'list':
                            for it in t[1]:
                                fs = []
                                functors(it, fs)
                                if fs:
                                    items.append((fs[0][0], fs[0][1]))
                                    for f2, l2, d in fs[1:]:
                                        body.append((f2, l2))
                                elif it[0] == 'atom':
                                    items.append((it[1] + '/0', it[-1]))
                        else:
                            h = t
                            b = None
                            if t[0] == 'cmp' and t[1] == ':-' and len(t[2]) == 2:
                                h, b = t[2]
                            hn = ('%s/%d' % (h[1], len(h[2]))) if h[0] == 'cmp' else '%s/0' % h[1]
                            heads.append((hn, line))
                            fs = []
                            functors(b, fs)
                            body += [(f2, l2) for f2, l2, d in fs]
                        strings(t, strs)
                    rows.append(dict(file=rel, kind=kind, enc=enc, items=items, heads=heads,
                                     body=body, strings=strs, errors=errs, nterms=len(terms)))
        out[name] = rows
        print(name, len(rows), 'command/login files',
              sum(len(x['items']) for x in rows), 'list items',
              sum(x['errors'] for x in rows), 'unparsed terms')
    json.dump(out, open(sys.argv[1], 'w'))


if __name__ == '__main__':
    main()
