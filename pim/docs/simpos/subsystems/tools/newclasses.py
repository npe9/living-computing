"""Class names the dive's notes give from documentary sources (PRINTED*,
PROSE, SCREENSHOT) or from cil's SIMPOS copy, that neither
printed/classes.tsv nor required/classes.tsv lists.  Prints candidates
with their rows for review; the lead decides what goes into
subsystems/classes_added.tsv."""
import csv, glob, os, re, collections
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
known = set()
for line in open(D + 'printed/classes.tsv'):
    if not line.startswith('#'):
        known.add(line.split('\t')[0].strip())
for r in csv.DictReader(open(D + 'required/classes.tsv'), delimiter='\t'):
    known.add(r['class'])
cand = collections.defaultdict(list)
for f in sorted(glob.glob(os.path.join(B, 'notes', '*.tsv'))):
    for r in csv.DictReader(open(f), delimiter='\t'):
        g = (r['grade'] or '').upper()
        txt = (r['meaning'] or '') + (r['natures_or_slots'] or '')
        if 'CESP' in txt:
            continue
        doc = g.startswith(('PRINTED', 'PROSE', 'SCREENSHOT'))
        copy = 'COPY' in g or ('ds_bep' in (r['citation'] or ''))
        if not (doc or copy):
            continue
        names = [r['class'].strip()]
        if r['kind'] in ('class', 'nature'):
            names += [n.strip() for n in re.split(r'[,\s]+', r['natures_or_slots'] or '')]
        for n in names:
            n = n.split('##')[-1].strip('#:{}()[]')
            if not re.fullmatch(r'[a-z][a-z0-9_]*', n) or n in known or len(n) < 3:
                continue
            cand[n].append((os.path.basename(f), r['kind'], r['member'], g, r['citation'], r['version_or_year']))
for n in sorted(cand):
    rows = cand[n]
    print('%s\t%d\t%s' % (n, len(rows), ' | '.join('%s:%s:%s:%s:%s' % (a, b, d, e, v) for a, b, c, d, e, v in rows[:3])))
