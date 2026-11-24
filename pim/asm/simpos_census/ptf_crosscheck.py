"""Source scanner vs compiled packages (known plaintext): method arity
convention and send recall.  python3 -I ptf_crosscheck.py OUTDIR"""
import collections, json, os, sys
B = sys.argv[1]
P = json.load(open(os.path.join(B, 'ptf.json')))
pairs = (('kappa2', ['kappa']), ('utter', ['fts', 'qxt', 'sancho2', 'tour']),
         ('papyrus', [k for k in P if k.startswith('pak_')]))
for prog, pks in pairs:
    S = json.load(open(os.path.join(B, 'raw', prog + '.json')))
    src = {k.lower(): v for k, v in S['classes'].items()}
    sends = collections.defaultdict(set)
    for c, n, a in S['allsends']:
        sends[c.lower()].add('%s/%d' % (n, a))
    same = off1 = other = nc = 0
    tp = fn = fp = 0
    other_ex = collections.Counter(); miss = collections.Counter(); extra = collections.Counter()
    for pk in pks:
        for c in P[pk]['classes']:
            n = c['id'].split('##')[1].lower()
            if n not in src:
                continue
            nc += 1
            sm = set()
            for m in src[n]['methods']:
                sec, rest = m.split(':', 1); nm, ar = rest.rsplit('/', 1); sm.add((sec, nm, int(ar)))
            for k, nm, ar in c['preds']:
                if k not in ('class', 'instance'):
                    continue
                if (k, nm, ar) in sm: same += 1
                elif (k, nm, ar - 1) in sm or (k, nm, ar + 1) in sm: off1 += 1
                else: other += 1; other_ex['%s/%d' % (nm, ar)] += 1
            ps = set(c['sends']); ss = sends.get(n, set())
            tp += len(ps & ss); fn += len(ps - ss); fp += len(ss - ps)
            miss.update(ps - ss); extra.update(ss - ps)
    print('%s: %d compiled classes with same-named source class' % (prog, nc))
    print('  compiled class/instance methods: %d same name+arity in source, %d off by one, %d not in source (top: %s)'
          % (same, off1, other, ', '.join('%s x%d' % kv for kv in other_ex.most_common(6))))
    print('  selectors: %d in both, %d compiled-only (recall %.1f%%), %d source-only' % (tp, fn, 100.0 * tp / max(1, tp + fn), fp))
    print('    compiled-only top: ' + ', '.join('%s x%d' % kv for kv in miss.most_common(12)))
    print('    source-only top: ' + ', '.join('%s x%d' % kv for kv in extra.most_common(8)))
