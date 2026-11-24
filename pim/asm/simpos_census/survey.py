import sys, os, re, collections
sys.path.insert(0, sys.argv[1]); import esplex
roots = sys.argv[2:]
CL = re.compile(r'(^|\n)\s*class\s+[\w#]+.*?\bhas\b', re.S)
lead = collections.Counter(); segs = collections.Counter(); errs = collections.Counter(); ex = {}
nfiles = collections.Counter(); encs = collections.Counter()
for root in roots:
  for dp, dn, fn in os.walk(root):
    for f in fn:
        p = os.path.join(dp, f)
        raw = open(p, 'rb').read()
        if b'\x00' in raw[:4000]: continue
        text, enc = esplex.decode(raw)
        if not re.search(r'(^|\n)[ \t]*class[ \t\n]+\S+[ \t\n]+(has|with_macro)', text): continue
        nfiles[os.path.relpath(p, root).split('/')[0] if len(roots)==1 else root.split('/')[-1]] += 1
        encs[enc] += 1
        toks = esplex.tokenize(text)
        cur = []
        segl = []
        for t in toks:
            if t[0] == 'end': segl.append(cur); cur = []
            else: cur.append(t)
        if cur: segl.append(cur)
        for seg in segl:
            if not seg: continue
            if seg[0][1] != 'class':
                segs['nonclass:' + ' '.join(x[1] for x in seg[:3])] += 1; continue
            segs['class'] += 1
            for it in [x for x in esplex.split_top(seg) if x]:
                k = it[0][1] if it[0][0]=='atom' else it[0][0]
                if it[0][1] == ':' : k = ':'
                k2 = k
                if k in ('instance','local') and len(it)>1: k2 = k + ' ' + (it[1][1] if it[1][1] in ('attribute','component',':','before','after') else '...')
                lead[k2 if k2 in ('class','instance','local',':','nature','attribute','component','end','before','after') or k2.startswith(('instance','local')) else ('OTHER:'+k)] += 1
                r = esplex.Reader(it)
                try:
                    r.parse(1200)
                    if r.i != len(it): raise esplex.ParseError('trailing at %s' % r.peek()[2])
                except esplex.ParseError as e:
                    errs[p] += 1; ex.setdefault(p, str(e))
print('files', sum(nfiles.values()), dict(nfiles)); print(encs)
print(segs.most_common(40))
print(lead.most_common(60))
print('items with parse errors', sum(errs.values()), 'in files', len(errs))
for p, n in errs.most_common(15): print(n, p, ex[p])
