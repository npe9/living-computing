"""Probe: per class, which classes outside its own package its template
names.  A trailer token counts as a class reference if it is pkg##class
(other package), or an unqualified atom equal to the name of a class that
exists in some held package but not in this one (resolved through the
package environment).  Classes whose trailer did not parse (no own id and
'template' token) are reported separately, never counted as free.
Read-only; uses repo asm/ptfdump.py.  usage: python3 -I deps.py REPO_ASM_DIR"""
import collections
import sys

sys.path.insert(0, sys.argv[1])
import ptfdump as P  # noqa: E402

allc = {}
for pkg in P.PKGS:
    _n, _a, cl = P.parse(pkg)
    allc[pkg] = cl
local = {pkg: {c['id'].split('##')[1] for c in cl if c['id']} for pkg, cl in allc.items()}
known_simpos = set()
rows = collections.defaultdict(list)
for pkg, cl in allc.items():
    for c in cl:
        cs, i, _n2, _L, _h1, _h2 = P.cells(c)
        items = P.trailer(c, i)
        ok = c['id'] in items and 'template' in items
        q = {t for t in items if '##' in t and not t.startswith('"')
             and t.split('##')[0] != pkg}
        # nature vector: tokens after 'self' up to the next non-name
        unq = set()
        if 'self' in items:
            k = items.index('self') + 1
            while k < len(items) and items[k] and items[k][0].isalpha() \
                    and not items[k].startswith('vector'):
                t = items[k]
                if '##' not in t and t not in local[pkg]:
                    unq.add(t)
                k += 1
        rows[pkg].append((c['id'].split('##')[1], len(cs), ok, q, unq))
tot = collections.Counter()
for pkg in P.PKGS:
    r = rows[pkg]
    bad = [x for x in r if not x[2]]
    free = [x for x in r if x[2] and not any(t.startswith('simpos##') for t in x[3]) and not x[4]]
    unqn = [x for x in r if x[4]]
    print('%-10s %3d classes; trailer unparsed %3d; parsed and name no simpos##/unresolved-nature class %3d (%6d cells); have non-local unqualified natures %3d'
          % (pkg, len(r), len(bad), len(free), sum(x[1] for x in free), len(unqn)))
    for x in sorted(free, key=lambda x: -x[1])[:8]:
        print('     free: %-38s %6d cells other refs: %s' % (x[0], x[1], ' '.join(sorted(x[3]))[:100]))
    for x in unqn[:6]:
        print('     unqualified nature: %-30s %s' % (x[0], ' '.join(sorted(x[4]))[:120]))
    print('     unparsed:', ' '.join(x[0] for x in bad)[:300])
    tot['classes'] += len(r); tot['bad'] += len(bad); tot['free'] += len(free); tot['unq'] += len(unqn)
print('TOTAL', dict(tot))

# transitive: a class depends on simpos if it, or any held class it names
# (qualified, or unqualified local nature), does.
names = {}
for pkg, cl in allc.items():
    for c in cl:
        cs, i, _n2, _L, _h1, _h2 = P.cells(c)
        items = P.trailer(c, i)
        refs = set()
        for t in items:
            if '##' in t and not t.startswith('"'):
                refs.add(t)
            elif t in local[pkg] and t != c['id'].split('##')[1]:
                refs.add(pkg + '##' + t)
        names[c['id']] = refs
held = set(names)
dep = {}
def d(x, seen=()):
    if x in dep: return dep[x]
    if x not in held: return x.startswith('simpos##') or x.split('##')[0] not in allc
    if x in seen: return False
    r = any(d(y, seen + (x,)) for y in names[x])
    dep[x] = r
    return r
free2 = collections.Counter()
for x in held:
    if not d(x): free2[x.split('##')[0]] += 1
print('TRANSITIVE free (no path to simpos## or to an unheld package):', dict(free2), sum(free2.values()))
for x in sorted(held):
    if not d(x) and x.split('##')[0] in ('pimfep', 'pimscsi', 'paragraph'): print('   ', x)
