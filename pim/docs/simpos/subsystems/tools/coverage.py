"""Coverage of required/requirements.tsv (class & instance methods on named
classes of each partition) by the dive's notes TSVs.

A requirement (class, kind, method, arity) is
  DOC    if some notes row with a documentary grade (PRINTED*, PROSE,
         SCREENSHOT, HELD-SOURCE: a method body in an application-carried
         copy of SIMPOS source, added 2026-11-24 sweep) names the same method/arity on the same class, or on
         any class when the doc row's class is not a required class name
         (reports often state methods without their owning class);
  USAGE  if only USAGE/INFERENCE rows give it a meaning (same class+method+arity);
  NONE   otherwise.
Writes coverage_<partition>.tsv and prints a summary."""
import csv, glob, os, sys, collections
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'required') + '/'
part = {}
for p in ('window', 'librarian', 'shell', 'other'):
    for r in csv.DictReader(open(os.path.join(B, 'coverage', 'partition_%s.tsv' % p)), delimiter='\t'):
        part[r['class']] = p
reqclasses = set(part)
doc_exact, doc_any, use_exact = set(), set(), set()
use_any = set()
for f in glob.glob(os.path.join(B, 'notes', '*.tsv')):
    for r in csv.DictReader(open(f), delimiter='\t'):
        if r['kind'] not in ('imethod', 'cmethod'):
            continue
        g = (r['grade'] or '').upper()
        if 'CESP' in (r['meaning'] or '') + (r['natures_or_slots'] or ''):
            continue
        m, a, c = r['member'].strip(':'), (r['arity'] or '').strip(), r['class'].strip()
        if '/' in m and not a:
            m, a = m.rsplit('/', 1)
        key = (c, m, a)
        if g.startswith('PRINTED') or g.startswith('PROSE') or g.startswith('SCREENSHOT') or g.startswith('HELD-SOURCE'):
            doc_exact.add(key)
            if c not in reqclasses:
                doc_any.add((m, a))
        elif g.startswith('USAGE') or g.startswith('INFERENCE'):
            use_exact.add(key)
            use_any.add((m, a))
out = collections.defaultdict(list)
for r in csv.DictReader(open(R + 'requirements.tsv'), delimiter='\t'):
    if r['kind'] not in ('class', 'instance'):
        continue
    c = r['class']
    if c not in part:
        continue
    m, a = r['method'], r['arity']
    if (c, m, a) in doc_exact:
        s = 'DOC-class'
    elif (m, a) in doc_any:
        s = 'DOC-unowned'
    elif (c, m, a) in use_exact:
        s = 'USAGE'
    elif (m, a) in use_any:
        s = 'USAGE-unowned'
    else:
        s = 'NONE'
    out[part[c]].append((c, r['kind'], m, a, r['uses'], r['n_programs'], s))
for p, rows in sorted(out.items()):
    cnt = collections.Counter(x[-1] for x in rows)
    uses = collections.Counter()
    for x in rows:
        uses[x[-1]] += int(x[4] or 0)
    print('%-9s methods %4d  DOC-class %4d  DOC-unowned %4d  USAGE %4d  USAGE-unowned %4d  NONE %4d | uses: %s' % (
        p, len(rows), cnt['DOC-class'], cnt['DOC-unowned'], cnt['USAGE'], cnt['USAGE-unowned'], cnt['NONE'],
        ' '.join('%s=%d' % kv for kv in sorted(uses.items()))))
    with open(os.path.join(B, 'coverage', 'coverage_%s.tsv' % p), 'w') as f:
        f.write('class\tkind\tmethod\tarity\tuses\tn_programs\tstatus\n')
        for x in sorted(rows, key=lambda x: -int(x[4] or 0)):
            f.write('\t'.join(map(str, x)) + '\n')
