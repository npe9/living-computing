"""Aggregate raw/*.json (espscan), ptf.json (ptfside), com.json (comscan)
into the TSV deliverables.

python3 -I report.py OUTDIR MANUAL_TEX_DIR[+DIR] OLD_CENSUS.tsv

Program -> compiled packages that belong to it (their class ids count as
defined in that program): kappa2: kappa; utter: fts qxt sancho2 tour;
papyrus: pak_*.  The psdpim/pimosobj packages are a separate group
(no source)."""
import collections
import glob
import json
import os
import re
import sys

OUT = sys.argv[1]
MANDIRS = sys.argv[2].split('+')
OLD = sys.argv[3]
OCR = sys.argv[4] if len(sys.argv) > 4 else None
ocr = {}
if OCR:
    for dd in sorted(os.listdir(OCR)):
        buf = []
        for f in sorted(glob.glob(os.path.join(OCR, dd, '*.txt'))):
            buf.append(open(f, encoding='utf-8', errors='replace').read())
        t = re.sub(r'[^a-z0-9]+', '_', ' '.join(buf).lower())
        ocr[dd] = '_' + t + '_'


def in_reports(cls):
    k = '_' + re.sub(r'[^a-z0-9]+', '_', cls.lower()) + '_'
    return sorted(d for d, t in ocr.items() if k in t)
OWN_PTF = {'kappa2': ['kappa'], 'utter': ['fts', 'qxt', 'sancho2', 'tour']}
NOSRC_PTF = ['pimfep', 'pimscsi', 'pimmcsp', 'pimmutil', 'mpsicspR', 'paragraph']

progs = {}
for f in sorted(glob.glob(os.path.join(OUT, 'raw', '*.json'))):
    d = json.load(open(f))
    progs[d['name']] = d
P = json.load(open(os.path.join(OUT, 'ptf.json')))
OWN_PTF['papyrus'] = [k for k in P if k.startswith('pak_')]
COM = json.load(open(os.path.join(OUT, 'com.json')))

# ---------------------------------------------------------------- manual words
manual = set()
for d in MANDIRS:
    for f in glob.glob(os.path.join(d, '*.tex')):
        raw = open(f, 'rb').read()
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import esplex
            txt, _ = esplex.decode(raw)
        except Exception:
            txt = raw.decode('latin-1')
        txt = txt.replace('\\_', '_').replace('{\\tt', ' ')
        manual |= set(re.findall(r'[A-Za-z_][A-Za-z0-9_]*', txt))

# ---------------------------------------------------------------- defined sets
defined = {}      # program -> set of lower-case class names (source + own ptf)
src_defined = {}
for name, d in progs.items():
    s = set(k.lower() for k in d['classes'])
    src_defined[name] = s
    s = set(s)
    for pk in OWN_PTF.get(name, []):
        s |= set(c['id'].split('##')[1].lower() for c in P[pk]['classes'])
    defined[name] = s
ptf_ids = {}
for pk, v in P.items():
    for c in v['classes']:
        ptf_ids.setdefault(c['id'].split('##')[1].lower(), set()).add(pk)


def other_def(prog, cls):
    out = [p for p in progs if p != prog and cls.lower() in defined[p]]
    out += sorted(pk for pk in ptf_ids.get(cls.lower(), ()) if pk in NOSRC_PTF)
    return out


def site(x):
    return '%s:%s' % (x['file'], x['line'])


# ---------------------------------------------------------------- requirements
# key: (class, kind, method, arity)
req = collections.OrderedDict()
internal_ptf = collections.Counter()
xapp = collections.Counter()


def add(key, prog, how, where, extra=None):
    r = req.setdefault(key, dict(uses=0, progs=collections.Counter(), how=collections.Counter(),
                                 site=where, sets=collections.Counter(), psite={}))
    r['psite'].setdefault(prog, where)
    r['uses'] += 1
    r['progs'][prog] += 1
    r['how'][how] += 1
    if extra:
        r['sets'][extra] += 1


# direct attestations, used to refine inherited sets and unattributed sends
direct = collections.defaultdict(set)   # (sec, m, ar) -> classes
for name, d in progs.items():
    for s in d['sends']:
        if s['how'] in ('class', 'create-bound', 'slot', 'fallback-class') and s['cls'].lower() not in defined[name]:
            direct[(s['sec'], s['m'], s['ar'])].add(s['cls'])

unatt_by_prog = collections.defaultdict(collections.Counter)
for name, d in progs.items():
    for s in d['sends']:
        cls, sec, m, ar, how = s['cls'], s['sec'], s['m'], s['ar'], s['how']
        kind = 'slot' if s['kind'] == 'slot' else sec
        if cls.startswith('{') or cls == '<root>':
            members = cls[1:-1].split('|') if cls.startswith('{') else []
            members = [x for x in members if x.lower() not in defined[name]]
            cand = [c for c in members if c in direct.get((sec, m, ar), ())]
            if len(members) == 1:
                add((members[0], kind, m, ar), name, how + '>single-nature', site(s), cls)
            elif len(cand) == 1:
                add((cand[0], kind, m, ar), name, how + '>refined', site(s), cls)
            else:
                add((cls if members else '<root>', kind, m, ar), name, how, site(s), None)
            continue
        if cls == '?' and how == 'untyped-user-defined':
            if direct.get(('instance', m, ar)) or direct.get(('class', m, ar)):
                add(('?', 'ambiguous', m, ar), name, 'ambiguous-user-or-system', site(s))
            else:
                internal_ptf[(name, '?untyped-user')] += 1
            continue
        if cls == '?':
            add(('?', 'unknown', m, ar), name, how, site(s))
            unatt_by_prog[name][(m, ar)] += 1
            continue
        if cls.lower() in defined[name]:
            internal_ptf[(name, cls)] += 1
            continue
        od = other_def(name, cls)
        if od and not all(o in NOSRC_PTF for o in od):
            xapp[(name, cls, ','.join(od))] += 1
            add((cls, kind, m, ar), name, how + '(other-IFS-app:%s)' % ','.join(od), site(s))
            continue
        add((cls, kind, m, ar), name, how, site(s))
    for n in d['natures']:
        if n['user_defined'] or n['cls'].lower() in defined[name]:
            continue
        add((n['cls'], 'nature' if not n.get('macro') else 'macro_bank', '(inherited)', ''), name,
            'nature', site(n))
    for r in d['refs']:
        if r['cls'].lower() in defined[name]:
            continue
        add((r['cls'], 'ref', '(#ref)', ''), name, 'ref' + ('-' + r['how'] if r.get('how') else ''), site(r))

# compiled packages without source: class references only
ptfref = collections.defaultdict(lambda: collections.Counter())
for pk, v in P.items():
    own = set(c['id'].split('##')[0] for c in v['classes'])
    for c in v['classes']:
        for s in c['refs']:
            pkg, nm = s.split('##', 1)
            if pkg in own:
                continue
            ptfref[(pkg, nm)][pk] += 1

# simpos## classes named only by compiled packages (no source sends them)
src_named = set(k[0] for k in req)
for (pkg, nm), cnt in ptfref.items():
    if pkg == 'simpos' and nm not in src_named:
        for pk, n in cnt.items():
            for _ in range(n):
                add((nm, 'ptf-ref', '(simpos## ref in compiled package)', ''), 'ptf:' + pk, 'ptf', 'compiled:' + pk)

# candidates for unattributed sends: classes with the same selector attested directly
for key, r in req.items():
    cls, kind, m, ar = key
    if cls == '?':
        c = set()
        for sec in ('instance', 'class'):
            c |= direct.get((sec, m, ar), set())
        r['cand'] = sorted(c)
    else:
        r['cand'] = []

ptf_by_name = collections.defaultdict(set)
for (pkg, nm), cnt in ptfref.items():
    ptf_by_name[nm].update('%s(%s##)' % (k, pkg) for k in cnt)


def wtsv(path, header, rows):
    with open(path, 'w') as f:
        f.write('\t'.join(header) + '\n')
        for r in rows:
            f.write('\t'.join(str(x) for x in r) + '\n')


rows = []
for key, r in sorted(req.items(), key=lambda kv: (-kv[1]['uses'])):
    cls, kind, m, ar = key
    rows.append([cls, kind, m, ar, r['uses'], len(r['progs']),
                 ','.join('%s:%d' % kv for kv in sorted(r['progs'].items())),
                 ','.join('%s:%d' % kv for kv in r['how'].most_common()),
                 r['site'], ','.join(r['cand'][:12]) + ('...' if len(r['cand']) > 12 else ''),
                 ','.join(sorted(ptf_by_name.get(cls, ())))[:200],
                 ';'.join(k for k in r['sets'])[:300],
                 'yes' if m.lstrip('!') in manual else 'no'])
wtsv(os.path.join(OUT, 'requirements.tsv'),
     ['class', 'kind', 'method', 'arity', 'uses', 'n_programs', 'programs', 'how', 'example_site',
      'candidates_if_unattributed', 'also_in_compiled_packages', 'nature_set_if_refined', 'name_in_ESP_manual_TeX'], rows)

# compiled-package references (no source)
prow = []
for (pkg, nm), cnt in sorted(ptfref.items(), key=lambda kv: (-sum(kv[1].values()), kv[0])):
    insrc = sorted(set(p for p in progs if any(k[0] == nm for k in req if req[k]['progs'].get(p))))
    prow.append([pkg + '##' + nm, nm, sum(cnt.values()), len(cnt), ','.join('%s:%d' % kv for kv in sorted(cnt.items())),
                 'yes' if any(k[0] == nm for k in req) else 'no'])
wtsv(os.path.join(OUT, 'ptf_class_refs.tsv'),
     ['qualified', 'class', 'class_records_referencing', 'n_packages', 'packages', 'also_required_by_source'], prow)

# selectors sent by no-source packages and not defined in them (unattributed)
srow = []
for pk in NOSRC_PTF:
    v = P[pk]
    defs = set()
    for c in v['classes']:
        for k, nm, ar in c['preds']:
            defs.add('%s/%d' % (nm, ar))
    sent = collections.Counter()
    for c in v['classes']:
        sent.update(c['sends'])
    for sel, n in sent.most_common():
        if sel in defs:
            continue
        nm, ar = sel.rsplit('/', 1)
        known = sorted(set(k[0] for k in req if k[2] == nm and str(k[3]) == ar and k[0] != '?'))[:8]
        srow.append([pk, nm, ar, n, ','.join(known)])
wtsv(os.path.join(OUT, 'ptf_unattributed_selectors.tsv'),
     ['package', 'selector', 'arity_cell', 'cells', 'source_side_classes_with_same_selector'], srow)

# ---------------------------------------------------------------- builtins
bi = collections.OrderedDict()
local_any = collections.defaultdict(set)
for name, d in progs.items():
    for cn, c in d['classes'].items():
        for l in c['locals']:
            local_any[name].add(l)
for name, d in progs.items():
    for g in d['goals']:
        k = (g['name'], g['ar'], g['kind'])
        r = bi.setdefault(k, dict(uses=0, progs=collections.Counter(), site=site(g), elsewhere=0))
        r.setdefault('psite', {}).setdefault(name, site(g))
        r['uses'] += 1
        r['progs'][name] += 1
        if '%s/%d' % (g['name'], g['ar']) in local_any[name]:
            r['elsewhere'] += 1
    for c in d['consts']:
        k = (c[0], '', 'constant a#b')
        r = bi.setdefault(k, dict(uses=0, progs=collections.Counter(), site='%s:%s' % (c[1], c[2]), elsewhere=0))
        r['uses'] += 1
        r['progs'][name] += 1
    for x in d['directives']:
        if x['kind'] != 'directive':
            continue
        nm, ar = x['name'].rsplit('/', 1)
        k = (nm, int(ar), 'file-level directive')
        r = bi.setdefault(k, dict(uses=0, progs=collections.Counter(), site='%s:%s' % (x['file'], x['line']), elsewhere=0))
        r['uses'] += 1
        r['progs'][name] += 1
# cil/src/cil_kl0.esp `class builtin` (package kl0) wraps each KL0 built-in as
# `:name(_, A..):- !, name(A..)`: its body goals are a KL0 built-in list.
kl0tab = set()
if 'cil' in progs:
    for g in progs['cil']['goals']:
        if g['file'].endswith('cil_kl0.esp') and g['user'] == 'builtin' and g['kind'] == 'builtin':
            kl0tab.add((g['name'], g['ar']))
brow = []
for (nm, ar, kind), r in sorted(bi.items(), key=lambda kv: -kv[1]['uses']):
    if kind == 'constant a#b':
        att = 'n/a'
    else:
        att = 'yes' if nm in manual else ('operator' if not re.match(r'^[a-z]', nm) else 'no')
    brow.append([nm, ar, kind, r['uses'], len(r['progs']),
                 ','.join('%s:%d' % kv for kv in sorted(r['progs'].items())), r['site'], att,
                 r['elsewhere'], 'yes' if (nm, ar) in kl0tab else ('name-only' if any(k[0] == nm for k in kl0tab) else 'no')])
wtsv(os.path.join(OUT, 'builtins.tsv'),
     ['name', 'arity', 'kind', 'uses', 'n_programs', 'programs', 'example_site', 'word_in_ESP_manual_TeX',
      'uses_where_a_local_of_that_name_exists_in_another_class', 'in_cil_kl0_builtin_wrapper'], brow)

# ---------------------------------------------------------------- pathnames
W = r'[A-Za-z0-9_$.*~-]'
PATH = re.compile(r'^(?:%s+::)?(?:>%s+)+>?$|^%s+:%s*(?:>%s+)+>?$|^%s+:%s+$|^%s+::%s+:%s*$' % ((W,) * 10), re.A)
pth = collections.OrderedDict()


def addpath(s, prog, where, src):
    if not s or len(s) > 120 or ' ' in s.strip() or not PATH.match(s.strip()):
        return
    s = s.strip()
    if s.startswith('>') or '::' in s:
        kind = 'absolute' if '::' not in s else 'node::absolute'
    else:
        kind = 'logical-name:' + s.split(':')[0]
    r = pth.setdefault(s, dict(uses=0, progs=collections.Counter(), site=where, kind=kind, src=set()))
    r['uses'] += 1
    r['progs'][prog] += 1
    r['src'].add(src)


for name, d in progs.items():
    for s, f, l in d['strings']:
        addpath(s, name, '%s:%s' % (f, l), 'esp')
    for x in d['directives']:
        if x['kind'] == 'include':
            addpath(x['name'], name, '%s:%s' % (x['file'], x['line']), 'esp-include')
for name, rows_ in COM.items():
    for r in rows_:
        for s, l in r['strings']:
            addpath(s, name, '%s:%s' % (r['file'], l), r['kind'])
prow = []
for s, r in sorted(pth.items(), key=lambda kv: (kv[1]['kind'], -kv[1]['uses'], kv[0])):
    prow.append([s, r['kind'], r['uses'], ','.join('%s:%d' % kv for kv in sorted(r['progs'].items())),
                 ','.join(sorted(r['src'])), r['site']])
wtsv(os.path.join(OUT, 'pathnames.tsv'), ['pathname', 'kind', 'uses', 'programs', 'found_in', 'example_site'], prow)
# logical-name prefixes summary
lp = collections.Counter()
for s, r in pth.items():
    lp[r['kind']] += r['uses']

# ---------------------------------------------------------------- librarian
lib = collections.OrderedDict()
for name, rows_ in COM.items():
    for r in rows_:
        for f, l in r['items']:
            k = (f, 'command-list item' if r['kind'] != 'login' else 'login list item')
            x = lib.setdefault(k, dict(uses=0, progs=collections.Counter(), site='%s:%s' % (r['file'], l)))
            x['uses'] += 1
            x['progs'][name] += 1
        for f, l in r['heads']:
            k = (f, 'login clause head' if r['kind'] == 'login' else 'command-file clause head')
            x = lib.setdefault(k, dict(uses=0, progs=collections.Counter(), site='%s:%s' % (r['file'], l)))
            x['uses'] += 1
            x['progs'][name] += 1
        for f, l in r['body']:
            k = (f, 'term inside (%s)' % r['kind'])
            x = lib.setdefault(k, dict(uses=0, progs=collections.Counter(), site='%s:%s' % (r['file'], l)))
            x['uses'] += 1
            x['progs'][name] += 1
lrow = [[f, k, x['uses'], ','.join('%s:%d' % kv for kv in sorted(x['progs'].items())), x['site']]
        for (f, k), x in sorted(lib.items(), key=lambda kv: (kv[0][1], -kv[1]['uses']))]
wtsv(os.path.join(OUT, 'librarian.tsv'), ['functor', 'role', 'uses', 'programs', 'example_site'], lrow)
lrow2 = [[name, r['file'], r['kind'], len(r['items']), len(r['heads']), r['errors']] for name, rr in COM.items() for r in rr]
wtsv(os.path.join(OUT, 'command_files.tsv'), ['program', 'file', 'kind', 'list_items', 'clauses', 'unparsed_terms'], lrow2)

# ---------------------------------------------------------------- per program
os.makedirs(os.path.join(OUT, 'per_program'), exist_ok=True)
progreq = {}
appdeps = collections.defaultdict(set)
simpos_ptf0 = set(nm for (pkg, nm) in ptfref if pkg == 'simpos')
# cil defines these under SIMPOS's own names (its copy of the Librarian's
# library_utility, the coordinator, message, and the KL0 `builtin` wrapper);
# other programs' uses are uses of the SIMPOS class (NOTES.md).
simpos_ptf0 |= {'library_utility', 'coordinator', 'message', 'builtin'}


def cover_key(key, r, name):
    """SIMPOS-side key of a requirement row, or None (another IFS app's class).
    Nature sets collapse to (kind, selector, arity); `?` rows to the selector."""
    cls, kind, m, ar = key
    if any('other-IFS-app' in h for h in r['how']) and cls not in simpos_ptf0:
        for h in r['how']:
            if 'other-IFS-app:' in h:
                appdeps[name].add(h.split('other-IFS-app:')[1].rstrip(')'))
        return None
    if kind == 'ref':
        return ('ref', cls)
    if cls.startswith('{'):
        return ('set', kind, m, ar)
    if cls == '?':
        return ('sel', m, ar)
    return ('req', cls, kind, m, ar)


for name in progs:
    keys = set()
    rows_ = []
    for key, r in req.items():
        if r['progs'].get(name):
            cls, kind, m, ar = key
            ck = cover_key(key, r, name)
            if ck:
                keys.add(ck)
            rows_.append(['requirement', cls, kind, m, ar, r['progs'][name], r['psite'].get(name, '')])
    for (nm, ar, kind), r in bi.items():
        if r['progs'].get(name) and kind not in ('control',):
            if kind != 'user-macro':
                keys.add(('bi', nm, ar, kind))
            rows_.append(['builtin', '', kind, nm, ar, r['progs'][name], r.get('psite', {}).get(name, r['site'] if r['site'].startswith(name) else '')])
    progreq[name] = keys
    rows_.sort(key=lambda x: (x[0], -x[5]))
    wtsv(os.path.join(OUT, 'per_program', name + '.tsv'),
         ['category', 'class', 'kind', 'method_or_name', 'arity', 'uses_in_program', 'example_site'], rows_)

# ---------------------------------------------------------------- program summary and cover
summ = []
for name, d in progs.items():
    k = progreq[name]
    cls = set(x[1] for x in k if x[0] in ('req', 'ref') and not x[1].startswith('<')) 
    meth = set(x for x in k if x[0] == 'req' and x[2] in ('class', 'instance'))
    setm = set(x for x in k if x[0] == 'set')
    un = set(x for x in k if x[0] == 'sel')
    slots = set(x for x in k if x[0] == 'req' and x[2] == 'slot')
    bis = set(x for x in k if x[0] == 'bi' and x[3] == 'builtin')
    st = d['stats']
    summ.append([name, st.get('esp_files', 0), len(d['classes']), st.get('items', 0), st.get('parse_failed_items', 0),
                 st.get('fallback_items', 0), len(d['allsends']), len(d['sends']),
                 len(cls), len(meth), len(setm), len(slots), len(un), len(bis), len(k),
                 ','.join(sorted(appdeps.get(name, ())))])
summ.sort(key=lambda x: x[-2])
wtsv(os.path.join(OUT, 'programs.tsv'),
     ['program', 'esp_files', 'classes_defined', 'items', 'items_unparsed', 'items_token_fallback', 'sends_all',
      'sends_external_rows', 'system_classes_named', 'methods_on_named_classes', 'methods_on_nature_sets(collapsed)',
      'slots', 'selectors_unattributed_or_ambiguous', 'builtin_predicates', 'total_simpos_keys',
      'needs_classes_of_other_ifs_apps'], summ)

# greedy cover: add the program that adds fewest new keys
order, have, crow = [], set(), []
left = set(progs)
while left:
    best = min(left, key=lambda p: (len(progreq[p] - have), p))
    new = progreq[best] - have
    have |= progreq[best]
    order.append(best)
    left.discard(best)
    sat = [p for p in progs if progreq[p] <= have]
    crow.append([len(order), best, len(new), len(have), ','.join(sorted(sat))])
wtsv(os.path.join(OUT, 'subset_cover.tsv'),
     ['step', 'program_added', 'new_keys', 'cumulative_keys', 'programs_fully_satisfied_by_cumulative_set'], crow)

# per-unit (archive subdirectory) for the minimal search
urow = []
for name, d in progs.items():
    units = collections.defaultdict(set)
    for key, r in req.items():
        pass
    for s in d['sends']:
        parts = s['file'].split('/')
        u = '/'.join(parts[:2]) if len(parts) > 2 else parts[0]
        units[u].add((s['cls'], s['sec'], s['m'], s['ar']))
    for g in d['goals']:
        if g['kind'] == 'builtin':
            parts = g['file'].split('/')
            u = '/'.join(parts[:2]) if len(parts) > 2 else parts[0]
            units[u].add(('bi', g['name'], g['ar']))
    for u, ks in units.items():
        external = set(k for k in ks if k[0] == 'bi' or k[0].lower() not in defined[name])
        files = sorted(set(f for f in d['esp_files'] if f.startswith(u + '/') or f == u))
        urow.append([name, u, len(files), len([k for k in external if k[0] != 'bi']),
                     len([k for k in external if k[0] == 'bi']), len(external)])
urow.sort(key=lambda x: x[-1])
wtsv(os.path.join(OUT, 'units.tsv'), ['program', 'unit(dir)', 'esp_files', 'send_keys(raw class form)', 'builtin_keys', 'total'], urow)

# ---------------------------------------------------------------- class summary
cs = collections.defaultdict(lambda: dict(uses=0, refs=0, methods=set(), cm=set(), im=set(), slots=set(), progs=set(), nature=0))
for (cls, kind, m, ar), r in req.items():
    if cls == '?':
        continue
    c = cs[cls]
    if kind == 'ref':
        c['refs'] += r['uses']
    else:
        c['uses'] += r['uses']
    c['progs'] |= set(r['progs'])
    if kind == 'class':
        c['cm'].add((m, ar))
    elif kind == 'instance':
        c['im'].add((m, ar))
    elif kind == 'slot':
        c['slots'].add(m)
    elif kind == 'nature':
        c['nature'] += r['uses']
simpos_ptf = set(nm for (pkg, nm) in ptfref if pkg == 'simpos')
xapp_cls = set(k[1] for k in xapp)
held = collections.defaultdict(set)
for pk in NOSRC_PTF:
    for c in P[pk]['classes']:
        held[c['id'].split('##')[1]].add(c['id'])
mannorm = None
mantext = []
for d in MANDIRS:
    for f in glob.glob(os.path.join(d, '*.tex')):
        mantext.append(esplex.decode(open(f, 'rb').read())[0])
mannorm = '_' + re.sub(r'[^a-z0-9]+', '_', ' '.join(mantext).lower().replace('\\_', '_')) + '_'
tier = {}
for cls, c in cs.items():
    if cls.startswith(('{', '<')):
        continue
    rep = in_reports(cls)
    inman = ('_' + re.sub(r'[^a-z0-9]+', '_', cls.lower()) + '_') in mannorm
    if cls in held:
        t = 'P:provided-by-held-package(%s)' % ','.join(sorted(held[cls]))
    elif cls in simpos_ptf:
        t = 'A:simpos##-in-compiled-package'
    elif inman and '_' in cls:
        t = 'M:named-in-ESP-manual-TeX'
    elif cls in xapp_cls:
        t = 'X:defined-in-another-IFS-app'
    elif rep and '_' in cls:
        t = 'B:named-in-SIMPOS-report-OCR'
    elif rep:
        t = 'B?:one-word-name-in-report-OCR(weak)'
    elif len(c['progs']) >= 2:
        t = 'C:used-by-2+-programs'
    else:
        t = 'D:one-program-unconfirmed'
    tier[cls] = (t, rep)
crow2 = []
for cls, c in sorted(cs.items(), key=lambda kv: -(kv[1]['uses'] + kv[1]['refs'])):
    crow2.append([cls, c['uses'], c['refs'], len(c['progs']), ','.join(sorted(c['progs'])), len(c['cm']), len(c['im']),
                  len(c['slots']), c['nature'], ' '.join(sorted('%s/%s' % x for x in c['cm']))[:600],
                  ' '.join(sorted('%s/%s' % x for x in c['im']))[:900],
                  ','.join(sorted(ptf_by_name.get(cls, ())))[:200],
                  tier.get(cls, ('set', []))[0], ','.join(tier.get(cls, ('', []))[1][:10])])
wtsv(os.path.join(OUT, 'classes.tsv'),
     ['class', 'uses_send_slot_nature', 'hash_refs', 'n_programs', 'programs', 'class_methods', 'instance_methods', 'slots', 'as_nature',
      'class_method_list', 'instance_method_list', 'compiled_packages_referencing', 'evidence_tier', 'reports_naming_it'], crow2)
tiers = collections.Counter(v[0] for v in tier.values())

# ---------------------------------------------------------------- old census cross-check
old = {}
for line in open(OLD).read().splitlines()[1:]:
    f = line.split('\t')
    if len(f) < 5:
        continue
    old[f[0]] = dict(uses=int(f[1].split('=')[1]), methods=f[4].split('=', 1)[1].split(',') if '=' in f[4] else [])
mine = set(c for c in cs if not c.startswith(('{', '<')))
setmembers = set()
for c in cs:
    if c.startswith('{'):
        setmembers |= set(c[1:-1].split('|'))
xr = []
alldef = set().union(*defined.values())
for c in sorted(old):
    st = 'in new set' if c in mine else ('only inside a nature set' if c in setmembers else
                                         ('defined in an IFS program (source or ptf)' if c.lower() in alldef else
                                          ('package name, not a class' if any(c == x.get('arg') for d in progs.values() for x in d['directives']) or
                                           any(r['pkg'] == c for d in progs.values() for r in d['refs']) else 'not found by new scan')))
    newm = set(m for (m, a) in cs[c]['cm'] | cs[c]['im']) if c in cs else set()
    oldm = set(x for x in old[c]['methods'] if x)
    xr.append([c, old[c]['uses'], st, cs[c]['uses'] if c in cs else 0, len(oldm), len(newm),
               ' '.join(sorted(oldm - newm))[:300], ' '.join(sorted(newm - oldm))[:300]])
for c in sorted(mine - set(old)):
    xr.append([c, 0, 'new only', cs[c]['uses'], 0, len(set(m for (m, a) in cs[c]['cm'] | cs[c]['im'])), '', ''])
wtsv(os.path.join(OUT, 'old_census_crosscheck.tsv'),
     ['class', 'old_uses', 'status', 'new_uses', 'old_methods', 'new_methods', 'methods_old_only', 'methods_new_only'], xr)

# ---------------------------------------------------------------- headline numbers
known_cls = [c for c in cs if not c.startswith(('{', '<'))]
nm = set((cls, kind, m, ar) for (cls, kind, m, ar) in req if kind in ('class', 'instance') and cls not in ('?',) and not cls.startswith(('{', '<')))
nm_sets = set(k for k in req if k[1] in ('class', 'instance') and k[0].startswith(('{', '<')))
un = set(k for k in req if k[0] == '?')
sl = set(k for k in req if k[1] == 'slot')
bis = [b for b in brow if b[2] == 'builtin']
summary = dict(
    programs=len(progs), esp_files=sum(d['stats'].get('esp_files', 0) for d in progs.values()),
    classes_defined=sum(len(d['classes']) for d in progs.values()),
    items=sum(d['stats'].get('items', 0) for d in progs.values()),
    items_unparsed=sum(d['stats'].get('parse_failed_items', 0) for d in progs.values()),
    sends_all=sum(len(d['allsends']) for d in progs.values()),
    system_classes_named=len(known_cls), tiers=dict(tiers), nature_sets=len([c for c in cs if c.startswith(('{', '<'))]),
    methods_on_named_classes=len(nm), methods_on_nature_sets_or_root=len(nm_sets),
    unattributed_selectors=len(un), slots=len(sl),
    builtin_predicates=len(bis), builtin_attested=len([b for b in bis if b[7] == 'yes']),
    builtin_in_kl0_table=len([b for b in bis if b[9] == 'yes']), kl0_table_size=len(kl0tab),
    builtin_neither=len([b for b in bis if b[7] != 'yes' and b[9] == 'no']),
    constants=len([b for b in brow if b[2] == 'constant a#b']),
    pathnames=len(pth), pathname_kinds=dict(lp.most_common(20)),
    ptf_external_class_refs=len(ptfref), xapp=len(xapp), cover_order=order,
    minimal=summ[0][0], minimal_keys=summ[0][-2], full_keys=len(have),
    ambiguous_rows=len([k for k in req if k[1] == 'ambiguous']),
    ambiguous_uses=sum(r['uses'] for k, r in req.items() if k[1] == 'ambiguous'))
json.dump(summary, open(os.path.join(OUT, 'summary.json'), 'w'), indent=1)
print(json.dumps(summary, indent=1))
for k, v in sorted(xapp.items(), key=lambda kv: -kv[1])[:20]:
    print('xapp', k, v)
