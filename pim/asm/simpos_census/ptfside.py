"""Class references and selectors of compiled SIMPOS packages (.ptf/.pak).

python3 -I ptfside.py REPO_ASM OUT.json NAME=PATH|@psdpim:PKG ...

Uses the project's asm/ptfdump.py read-only (its `member` is replaced so
that extracted files can be read; @psdpim:PKG keeps ptfdump's own source,
docs/nonlocal/psdpim.tar.Z / pimosobj.tar.Z).  Per class: class_id,
`pkg##name` symbols, predicates defined (kind, name, arity) and
selectors sent (name/arity cells with a non-zero arity byte)."""
import collections
import json
import sys

sys.path.insert(0, sys.argv[1])
import ptfdump  # noqa: E402

orig = ptfdump.member


def member(tar, suffix):
    if tar == '@file':
        return open(suffix, 'rb').read()
    return orig(tar, suffix)


ptfdump.member = member
out = {}
for spec in sys.argv[3:]:
    name, path = spec.split('=', 1)
    if path.startswith('@psdpim:'):
        key = path.split(':', 1)[1]
    else:
        key = name
        ptfdump.PKGS[key] = ('@file', path)
    pname, pattrs, cl = ptfdump.parse(key)
    classes = []
    for c in cl:
        cs, _i, n, L, h1, h2 = ptfdump.cells(c)
        ps = ptfdump.preds(c, cs)
        sel = collections.Counter()
        for _n, t, b, v in cs:
            if t == 0x01 and b:
                sel['%s/%d' % (ptfdump.sym(c, v), b)] += 1
        classes.append(dict(id=c['id'], exact=(n == L),
                            refs=sorted(s for s in c['syms'] if '##' in s),
                            preds=[(ptfdump.KINDS.get(k, 'kind%02x' % k), nm, ar) for _o, k, _q, nm, ar in ps],
                            sends=dict(sel)))
    out[name] = dict(package=pname, source=path, classes=classes)
    print(name, pname, len(classes), 'classes', sum(c['exact'] for c in classes), 'exact')
json.dump(out, open(sys.argv[2], 'w'))
