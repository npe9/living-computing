"""Usage census of the ESP front ends of the held PIMOS (and other non-census) IFS programs.

The required-interface census (`../../required/`) covers the 15 IFS SIMPOS programs. The IFS also
holds ESP code that ran on SIMPOS as the front end of PIMOS applications (gog-kl1, examds, mendels,
cbcdss, desq, helic2, quixote, kappa-p, voronoi, ...) and the PIMOS tree's own ESP (`pimos.tar.Z`
src_util). This tool mines it the same way, more crudely:

  * class sends `:m(#c, ...)` (and `#simpos##c`), arity counted with the receiver;
  * instance sends `:m(V, ...)` where `V` was bound by `:create(#c, V)` earlier in the same clause
    (an ESP clause ends with `;` at the end of a line);

for every class `c` of `../../required/classes.tsv` whose tier is A, B, C, D or M, skipping a class the
same program defines itself. CESP programs and the 15 census programs are skipped.

Usage: python3 -I fe_census.py EXTRACTED_DIR
  EXTRACTED_DIR holds one directory per held archive, named after its path under
  pim/docs/nonlocal/ with '/' replaced by '__' (e.g. ifs__kbms-clp__pimos__quixote.tar.gz/).
Writes ../notes/fixpoint_fe.tsv (grade CENSUS, which coverage.py ignores; one row per class/kind/method/arity) and prints a
summary. Added 2026-11-24 (fixpoint_2026-11-24.md round 1)."""
import sys, os, re, csv, collections
held = sys.argv[1]
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(os.path.dirname(B), 'required')
CENSUS = {'txtstrct', 'chal', 'utter', 'knov', 'disc', 'icotext', 'sum', 'papyrus', 'fuzclust', 'gog-esp',
          'euod', 'kwic-esp', 'cal-esp', 'cil', 'kappa2'}
SKIP = CENSUS | {'kwic-esp-002', 'linguist', 'morphana', 'sdiv', 'kwic-cesp', 'cal-cesp', 'jpnsgen',
                 'kappa2d1', 'kappa2d2', 'kappa2d3'}
tier = {r['class']: r['evidence_tier'] for r in csv.DictReader(open(os.path.join(R, 'classes.tsv')), delimiter='\t')}
classes = {c for c, t in tier.items() if t[:2] in ('A:', 'B:', 'C:', 'D:', 'M:')}
reqkeys = set()
for r in csv.DictReader(open(os.path.join(R, 'requirements.tsv')), delimiter='\t'):
    if r['kind'] in ('class', 'instance'):
        reqkeys.add((r['class'], r['kind'], r['method'], r['arity']))
part = {}
for p in ('window', 'librarian', 'shell', 'other'):
    for r in csv.DictReader(open(os.path.join(B, 'coverage', 'partition_%s.tsv' % p)), delimiter='\t'):
        part[r['class']] = p

def nargs(s, i):
    depth = 0; n = 1; j = i; q = None
    while j < len(s) and j < i + 4000:
        ch = s[j]
        if q:
            if ch == q: q = None
        elif ch in '"\'': q = ch
        elif ch in '([{': depth += 1
        elif ch in ')]}':
            depth -= 1
            if depth == 0: return n
        elif ch == ',' and depth == 1: n += 1
        j += 1
    return None

def strip(l):
    q = None
    for i, ch in enumerate(l):
        if q:
            if ch == q: q = None
        elif ch == '"': q = ch
        elif ch == '%': return l[:i]
    return l

SEND = re.compile(r':([a-z][A-Za-z0-9_]*)\(\s*#(?:simpos##)?([a-z][A-Za-z0-9_]*)\s*[,)]')
CREATE = re.compile(r':create\(\s*#(?:simpos##)?([a-z][A-Za-z0-9_]*)\s*,\s*([A-Z_][A-Za-z0-9_]*)')
CLAUSE_END = re.compile(r';[ \t]*\n')
DEF = re.compile(r'^\s*class\s+([a-z][a-z0-9_]*)\s+(?:has|with)\b', re.M | re.I)
found = collections.defaultdict(lambda: [0, set(), ''])
for top in sorted(os.listdir(held)):
    prog = top.split('__')[-1].split('.')[0]
    if prog in SKIP:
        continue
    # ESP is selected by content, not by suffix: the IFS keeps ESP under .esp, .ESP, .v32, .wkm,
    # .talk, .grape, .slv, .ctl, .esp.1 and others. A file counts if its name ends in .esp or it defines a class.
    files = {}
    for dp, dn, fn in os.walk(os.path.join(held, top)):
        for f in fn:
            p = os.path.join(dp, f)
            try:
                if os.path.islink(p) or os.path.getsize(p) > 4_000_000: continue
                b = open(p, 'rb').read()
            except OSError:
                continue
            s = b.decode('latin-1')
            if f.lower().endswith('.esp') or DEF.search(s): files[p] = s
    texts = {}
    own = set()
    for p, s in sorted(files.items()):
        texts[p] = '\n'.join(strip(l) for l in s.split('\n'))
        own |= {m.group(1).lower() for m in DEF.finditer(texts[p])}
    arch = top.split('__')[-1]
    for p, s in sorted(texts.items()):
        rel = arch + '/' + os.path.relpath(p, os.path.join(held, top))
        def rec(k, pos):
            found[k][0] += 1; found[k][1].add(prog)
            if not found[k][2]:
                found[k][2] = '%s:%d' % (rel, s.count('\n', 0, pos) + 1)
        for m in SEND.finditer(s):
            meth, c = m.group(1), m.group(2)
            if c not in classes or c in own: continue
            n = nargs(s, m.end(1))
            if n: rec((c, 'class', meth, str(n)), m.start())
        for m in CREATE.finditer(s):
            c, v = m.group(1), m.group(2)
            if c not in classes or c in own or v == '_': continue
            e = CLAUSE_END.search(s, m.end())
            seg = s[m.end(): e.start() if e else m.end() + 3000]
            for mm in re.finditer(r':([a-z][A-Za-z0-9_]*)\(\s*' + re.escape(v) + r'\s*[,)]', seg):
                n = nargs(seg, mm.end(1))
                if n: rec((c, 'instance', mm.group(1), str(n)), m.end() + mm.start())
out = os.path.join(B, 'notes', 'fixpoint_fe.tsv')
w = csv.writer(open(out, 'w'), delimiter='\t', lineterminator='\n')
w.writerow(['subsystem', 'class', 'kind', 'member', 'arity', 'natures_or_slots', 'meaning', 'grade', 'citation', 'version_or_year'])
new = 0
for (c, kind, m, a), (n, progs, site) in sorted(found.items()):
    inreq = (c, kind, m, a) in reqkeys
    new += not inreq
    w.writerow([part.get(c, 'other'), c, 'cmethod' if kind == 'class' else 'imethod', m, a, '',
                'called %d times by %s (front-end census; %s the 15-program census); meaning not stated in the source'
                % (n, ','.join(sorted(progs)), 'also in' if inreq else 'NOT in'),
                'CENSUS (front-end call sites; no meaning, so coverage.py does not count it)', site, 'IFS 1989-95'])
print('rows %d, of which not in requirements.tsv: %d' % (len(found), new))
