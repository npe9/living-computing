import sys, os, glob, re, collections
A = sys.argv[1]
rows = []
hdr = ['class','inherits_natures','slots','class_methods','instance_methods','tier','report','pdf_page','folio','notes']
bad = []
for f in sorted(glob.glob(os.path.join(A,'parts','*.classes.tsv'))):
    for i,l in enumerate(open(f, encoding='utf-8')):
        l = l.rstrip('\n')
        if not l.strip() or l.startswith('class\t') or l.startswith('#'): continue
        c = l.split('\t')
        if len(c) < 10: c += ['']*(10-len(c))
        if len(c) > 10: c = c[:9] + [' | '.join(c[9:])]
        c = [x.strip() for x in c]
        if c[5] not in ('PRINTED-SOURCE','PRINTED-INTERFACE','PROSE','NAMED'):
            bad.append((os.path.basename(f), i, c[0], c[5]))
        c.append(os.path.basename(f))
        rows.append(c)
order = {'PRINTED-SOURCE':0,'PRINTED-INTERFACE':1,'PROSE':2,'NAMED':3}
rows.sort(key=lambda r:(r[0].lower(), order.get(r[5],9), r[6]))
with open(os.path.join(A,'classes.tsv'),'w',encoding='utf-8') as o:
    o.write('# One row per (class, report). arity = arguments as printed EXCLUDING the receiver (class or instance) argument, written :name/N.\n')
    o.write('# tier: PRINTED-SOURCE body printed; PRINTED-INTERFACE signature/table only; PROSE described in text; NAMED name only.\n')
    o.write('# pdf_page = PDF page index of trtm/<report>.pdf (not printed folio). notes: EXAMPLE = tutorial/test class, not SIMPOS.\n')
    o.write('# Class counts fold "-" to "_" in names and exclude names that occur only in EXAMPLE rows. Rows are as transcribed.\n')
    o.write('\t'.join(hdr+['source_part'])+'\n')
    for r in rows: o.write('\t'.join(r)+'\n')
# Counting rule: class name normalized by strip + '-'->'_'; a name counts as EXAMPLE (excluded)
# only if no row for it is a non-EXAMPLE row.
norm = lambda n: n.strip().replace('-','_')
cls = collections.defaultdict(set); ex = set()
for r in rows:
    if r[9].strip().upper().startswith('EXAMPLE'): ex.add(norm(r[0])); continue
    cls[norm(r[0])].add(r[5])
ex -= set(cls)
best = collections.Counter()
for c,t in cls.items():
    best[min(t, key=lambda x: order.get(x,9))] += 1
print('rows', len(rows), 'reports', len(set(r[6] for r in rows)), 'distinct non-example classes', len(cls), 'example-only names', len(ex))
print('PRINTED-SOURCE', sorted(c for c,t in cls.items() if 'PRINTED-SOURCE' in t))
print('best tier per class', dict(best))
print('rows by tier', collections.Counter(r[5] for r in rows))
print('bad tiers', bad[:20], len(bad))
