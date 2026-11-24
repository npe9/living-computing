"""Probe: predicate-header kind/qualifier census over the held .ptf files,
and listing of named classes' headers.  Read-only; imports the repo's
asm/ptfdump.py (trusted code) and parses the untrusted archives with it.
usage: python3 -I kinds.py REPO_ASM_DIR [PKG CLASS ...]"""
import collections
import sys

sys.path.insert(0, sys.argv[1])
import ptfdump as P  # noqa: E402


def allheads(c, cs):
    """Every (atom, int, head, 0) quadruple, regular or not."""
    out = []
    for k in range(len(cs) - 3):
        a, f, h, z = cs[k:k + 4]
        if a[1] == 1 and a[2] == 0 and f[1] == 0 and h[1] == 0x24 and z[1] == 0:
            out.append((h[3] & 0xffff, (f[3] >> 8) & 255, f[3] >> 16,
                        P.sym(c, a[3]), h[3] >> 24, f[3] & 255, h[0]))
    return out


def main(argv):
    if len(argv) >= 2:
        pkg = argv[0]
        _n, _a, cl = P.parse(pkg)
        for cname in argv[1:]:
            for c in cl:
                if c['id'] and c['id'].endswith('##' + cname):
                    cs = P.cells(c)[0]
                    print('==', c['id'])
                    for h in allheads(c, cs):
                        print('  off %5x kind %02x qual %04x %s/%d (f.arity %d, at cell %x)' % h)
                    _cs, i, _n2, _L, _h1, _h2 = P.cells(c)
                    print('  trailer:', ' '.join(P.trailer(c, i))[:3000])
        return
    tot = collections.Counter()
    ex = {}
    for pkg in P.PKGS:
        _n, _a, cl = P.parse(pkg)
        for c in cl:
            cs = P.cells(c)[0]
            for h in allheads(c, cs):
                key = (h[1], h[2])
                tot[key] += 1
                ex.setdefault(key, []).append('%s %s/%d' % (c['id'], h[3], h[4]))
    for k, v in sorted(tot.items()):
        print('kind %02x qual %04x  %6d   e.g. %s' % (k[0], k[1], v, '; '.join(ex[k][:3])))


main(sys.argv[2:])
