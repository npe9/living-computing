"""Class-level coverage per partition, from coverage/coverage_<p>.tsv.

For each required class (coverage/partition_<p>.tsv): its best method
status, ranked DOC-class > DOC-unowned > USAGE > USAGE-unowned > NONE.
A class with no required methods is counted as "no methods required"
(nature-only mixins, references).  Caveats, stated in the specs:
DOC-unowned matches a documented name/arity on ANY class (including the
font editor's own classes and on-screen demo code), and coverage.py does
not read printed/classes.tsv, so some printed methods count as USAGE."""
import csv, os, collections
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RANK = ['DOC-class', 'DOC-unowned', 'USAGE', 'USAGE-unowned', 'NONE']
for p in ('window', 'librarian', 'shell'):
    classes = [r['class'] for r in csv.DictReader(open(os.path.join(B, 'coverage', 'partition_%s.tsv' % p)), delimiter='\t')]
    best = {}
    for r in csv.DictReader(open(os.path.join(B, 'coverage', 'coverage_%s.tsv' % p)), delimiter='\t'):
        s = RANK.index(r['status'])
        best[r['class']] = min(best.get(r['class'], 9), s)
    cnt = collections.Counter(RANK[best[c]] if c in best else 'no methods required' for c in classes)
    print('%-9s classes %3d: %s' % (p, len(classes), ', '.join('%s %d' % (k, cnt[k]) for k in RANK + ['no methods required'])))
