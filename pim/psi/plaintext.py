#!/usr/bin/env python3
"""Known-plaintext check of the loader: class templates against the ESP
source they were compiled from.  OURS.

    python3 -I psi/plaintext.py [--held DIR] [--tsv OUT.tsv] [PROGRAM ...]

PROGRAM is paragraph (pimos.tar.Z src_util/paragraph against
paragraph.ptf), kappa2 (kappa2.tar.Z against kappa.ptf) or utter
(utter.tar.Z against fts, qxt, sancho2 and tour .ptf); default all three.

The ESP side is read with the census's lexer and file driver
(asm/simpos_census/esplex.py, espscan.parse_file: the ESP manual's
operator table, each file's add_operator directives and its include
files); the walk over each class's items is our own, because the
census's collect_classes drops demons and slot kinds.  For each class
whose name matches a template (exactly, else case-folded), it compares:

  natures   the nature list as written (package prefixes dropped; the
            class itself where `*` is, first if omitted) against the
            template's nature vector;
  slots     per section, name, attribute or component, and the form of
            the initial value: none, constant (value compared when it is
            an atom, integer or string), `:- body` (template flag 0x02)
            or `is Class` (flag 0x01).  A slot declared with no initial
            value compiles to the constant 0 (MEASURED here), so
            none == const 0;
  methods   per section, (name, arity with the receiver, primary /
            before / after) against the template's predicate kinds;
  locals    (name, arity) against the kind-0x11 predicates.

A class defined more than once in the source (versions) is compared
against each definition and the closest one is kept.  Disagreements are
written to the TSV (one row each) and counted by direction.
"""
import collections
import re
import unicodedata
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'asm', 'simpos_census'))
import esplex  # noqa: E402
import espscan  # noqa: E402
import held  # noqa: E402
import librarian  # noqa: E402

sys.setrecursionlimit(50000)    # long `,` chains in data tables (esplex is recursive)
PROGRAMS = {'paragraph': ['paragraph'], 'kappa2': ['kappa'],
            'utter': ['fts', 'qxt', 'sancho2', 'tour']}


# ---------------------------------------------------------------------------
# the ESP side

class _Prog(espscan.Program):
    def __init__(self, name, files):
        espscan.Program.__init__(self, name, [])
        self.allfiles = [(rel, rel) for rel in sorted(files)]

    def rel(self, p):
        return p


def parse_program(name, files):
    """[(relpath, segments)] for every ESP file of a program; FILES is
    {relpath: bytes}.  Mirrors espscan.scan_program's driver."""
    prog = _Prog(name, files)
    # espscan.parse_file opens include files by path; serve them from FILES
    espscan.open = lambda p, mode='r': io.BytesIO(files[p])
    texts = []
    for rel in sorted(files):
        raw = files[rel]
        if espscan.is_binary(raw) or len(raw) > 4_000_000:
            continue
        text, _enc = esplex.decode(raw)
        if espscan.CLASSRE.search(text):
            texts.append((rel, text))
    union = []
    for rel, text in texts:
        union += [o for o in espscan.ops_from_text(text) if o[0] == 'add']
    parsed, nerr_total = [], 0
    for rel, text in texts:
        segs, nerr, _ops = espscan.parse_file(prog, rel, text, [])
        if nerr and union:
            segs2, nerr2, _ = espscan.parse_file(prog, rel, text, union)
            if nerr2 < nerr:
                segs, nerr = segs2, nerr2
        nerr_total += nerr
        parsed.append((rel, segs))
    return parsed, nerr_total, len(texts)


def _atomname(t):
    return t[1] if t and t[0] in ('atom', 'qatom') else None


def item_head(t):
    """-> ('method', role, name, arity) | ('local', None, name, arity) | None.
    Arity counts the receiver for methods, as the template does."""
    role = 'primary'
    if t[0] == 'cmp' and t[1] in ('before', 'after') and len(t[2]) == 1:
        role, t = t[1], t[2][0]
    if t[0] == 'cmp' and t[1] == ':-' and len(t[2]) == 2:
        t = t[2][0]
    if t[0] == 'cmp' and t[1] in ('before', 'after') and len(t[2]) == 1:
        role, t = t[1], t[2][0]
    if t[0] == 'cmp' and t[1] == ':' and len(t[2]) == 2 and _atomname(t[2][0]) in ('before', 'after'):
        role, t = t[2][0][1], ('cmp', ':', [t[2][1]])
    if t[0] == 'cmp' and t[1] == ':' and len(t[2]) == 1:
        m = t[2][0]
        if m[0] == 'cmp':
            return ('method', role, m[1], len(m[2]))
        if m[0] in ('atom', 'qatom'):
            return ('method', role, m[1], 0)
        return None
    if t[0] in ('cmp',) and t[1] not in ('=>', '==>', '-->', 'when', 'where', 'with', 'by'):
        return ('local', None, t[1], len(t[2]))
    if t[0] in ('atom', 'qatom'):
        return ('local', None, t[1], 0)
    return None


def _init_form(init, body):
    if body is not None:
        return ('code', None)
    if init is None:
        return ('none', None)
    if init[0] == 'cmp' and init[1] == '#is':
        nm = espscan.name_of(init[2][0])
        return ('is', nm[1] if nm else None)
    if init[0] == 'cmp' and init[1] == '#' and len(init[2]) == 1 and init[2][0][0] != 'str':
        return ('code', '#')       # `slot := #Class` compiles to an init predicate (MEASURED, kappa)
    if init[0] in ('atom', 'qatom', 'num', 'str'):
        return ('const', init[1])
    return ('term', None)          # any other term: constant or predicate, not decided here


def source_classes(parsed):
    """{name: [definition, ...]}; a definition is a dict of natures,
    slots, methods, locals, file and line."""
    out = collections.defaultdict(list)
    for rel, segs in parsed:
        for seg in segs:
            if seg[0] != 'class' or seg[1] != 'class':
                continue
            _, _kw, header, items, line = seg
            name, pkg, mb = espscan.header_info(header)
            d = dict(name=name, pkg=pkg, file=rel, line=line, natures=[], macro_bank=mb,
                     slots={'class': {}, 'instance': {}}, methods=set(), locals=set(),
                     unparsed=0, dynamic=0)
            for section, _toks, term, err in items:
                if term is None:
                    d['unparsed'] += 1
                    continue
                if term[0] == 'cmp' and term[1] == 'nature' and len(term[2]) == 1:
                    for n in espscan.flat(term[2][0]):
                        nm = espscan.name_of(n)
                        d['natures'].append('*' if nm and nm[1] == '*' else (norm(nm[1]) if nm else '?'))
                    continue
                if term[0] == 'cmp' and term[1] in ('attribute', 'component') and len(term[2]) == 1:
                    sec = 'class' if section == 'class' else 'instance'
                    for sl, init, body in espscan.slot_defs(term[2][0]):
                        d['slots'][sec][norm(str(sl))] = (term[1], _init_form(init, body))
                    continue
                if term[0] == 'cmp' and term[1] == ':-' and len(term[2]) == 1:
                    # `:- dynamic(P/N);` declares a local predicate (trailer field 9)
                    g = term[2][0]
                    if g[0] == 'cmp' and g[1] == 'dynamic':
                        for pn in espscan.flat(g[2][0]):
                            if pn[0] == 'cmp' and pn[1] == '/' and pn[2][1][0] == 'num':
                                d['locals'].add((norm(str(pn[2][0][1])), int(pn[2][1][1])))
                                d['dynamic'] += 1
                    continue
                h = item_head(term)
                if h is None:
                    continue
                if h[0] == 'method' and section in ('class', 'instance'):
                    d['methods'].add((section, norm(h[2]), h[3], h[1]))
                elif h[0] == 'local' and section == 'local':
                    d['locals'].add((norm(h[2]), h[3]))
                elif h[0] == 'method' and section == 'local':
                    d['methods'].add(('local?', norm(h[2]), h[3], h[1]))
            out[name].append(d)
    return out


# ---------------------------------------------------------------------------
# the comparison

def _short(cid):
    return cid.split('##')[-1]


_JIS = re.compile(r'<([0-9a-f]{4})>')


def norm(s):
    """Names compared across the two sides: the template's undecoded
    two-byte JIS cells (asm/ptfdump.py prints them <hhhh>) decoded, then
    NFKC (full-width letters in either side)."""
    def one(m):
        w = int(m.group(1), 16)
        try:
            return bytes([(w >> 8) | 0x80, (w & 255) | 0x80]).decode('euc_jp')
        except UnicodeDecodeError:
            return m.group(0)
    return unicodedata.normalize('NFKC', _JIS.sub(one, s))


def template_facts(t):
    nat = [norm(_short(n)) for n in t.natures]
    name = norm(t.name)
    if nat and nat[0] == name:
        nat = nat[1:]
    else:
        nat = ['*' if n == name else n for n in nat]
    slots = {}
    for sec, lst in (('class', t.class_slots), ('instance', t.instance_slots)):
        slots[sec] = {}
        for s in lst:
            kind = 'attribute' if s.attribute else 'component'
            k, v = s.init
            if k == 'code':
                form = ('code', None)
            elif k == 'is':
                form = ('is', _short(v) if isinstance(v, str) else v)
            else:
                form = ('const', v)
            slots[sec][norm(s.short)] = (kind, form)
    methods = set()
    for p in t.class_preds + t.instance_preds:
        methods.add((p.section, norm(p.name), p.arity, p.role))
    locals_ = set((norm(p.name), p.arity) for p in t.locals if p.role == 'local')
    return dict(natures=nat, slots=slots, methods=methods, locals=locals_)


def _slot_agree(src, tpl):
    kind_s, (fs, vs) = src
    kind_t, (ft, vt) = tpl
    if kind_s != kind_t:
        return False
    if fs == 'none':
        return ft == 'const' and vt in (0,)
    if fs == 'term':
        return ft in ('const', 'code')
    if fs != ft:
        return False
    if fs == 'const':
        return norm(str(vs)) == norm(str(vt))
    if fs == 'is':
        return vs is None or vs == vt
    return True


def compare(d, tf):
    """-> list of (aspect, direction, item) disagreements."""
    out = []
    nat_s = list(d['natures'])
    if nat_s != tf['natures']:
        out.append(('natures', 'differ', '%s | %s' % (','.join(nat_s), ','.join(tf['natures']))))
    for sec in ('class', 'instance'):
        ss, ts = d['slots'][sec], tf['slots'][sec]
        for n in sorted(set(ss) | set(ts)):
            if n not in ts:
                out.append(('slot', 'source-only', '%s %s %r' % (sec, n, ss[n])))
            elif n not in ss:
                out.append(('slot', 'template-only', '%s %s %r' % (sec, n, ts[n])))
            elif not _slot_agree(ss[n], ts[n]):
                out.append(('slot', 'differ', '%s %s %r | %r' % (sec, n, ss[n], ts[n])))
    ms, mt = d['methods'], tf['methods']
    for m in sorted(ms - mt):
        out.append(('method', 'source-only', '%s %s/%d %s' % m))
    for m in sorted(mt - ms):
        out.append(('method', 'template-only', '%s %s/%d %s' % m))
    ls, lt = d['locals'], tf['locals']
    for m in sorted(ls - lt):
        out.append(('local', 'source-only', '%s/%d' % m))
    for m in sorted(lt - ls):
        out.append(('local', 'template-only', '%s/%d' % m))
    return out


def run(program, root=None, lib=None):
    """-> dict of counts and the disagreement rows for one program."""
    if lib is None:
        lib = librarian.Librarian()
        lib.load_held(pkgs=PROGRAMS[program], root=root)
    declared = set(p for p, info in lib.packages.items() if info['file'] in PROGRAMS[program])
    files = held.src_files(program, root)
    parsed, nerr, nfiles = parse_program(program, files)
    src = source_classes(parsed)
    by_fold = collections.defaultdict(list)
    for n in src:
        by_fold[n.lower()].append(n)
    c = collections.Counter(esp_files=nfiles, unparsed_items=nerr, source_classes=len(src))
    rows = []
    for cid, t in lib.templates.items():
        if t.package not in declared:
            continue
        c['templates'] += 1
        defs = src.get(t.name)
        how = 'exact'
        if not defs:
            folded = by_fold.get(t.name.lower(), [])
            defs = [d for n in folded for d in src[n]]
            how = 'folded'
        if not defs:
            c['no_source'] += 1
            continue
        c['matched_' + how] += 1
        c['multiply_defined'] += len(defs) > 1
        tf = template_facts(t)
        d = min(defs, key=lambda d: len(compare(d, tf)))
        nd = compare(d, tf)
        c['classes_all_agree'] += not nd
        c['nature_lists'] += 1
        c['nature_lists_agree'] += not any(x[0] == 'natures' for x in nd)
        for sec in ('class', 'instance'):
            for n in set(d['slots'][sec]) | set(tf['slots'][sec]):
                c['slots'] += 1
            c['slots_agree'] += sum(1 for n in d['slots'][sec] if n in tf['slots'][sec]
                                    and _slot_agree(d['slots'][sec][n], tf['slots'][sec][n]))
        c['methods'] += len(d['methods'] | tf['methods'])
        c['methods_agree'] += len(d['methods'] & tf['methods'])
        dem_s = set(m for m in d['methods'] if m[3] != 'primary')
        dem_t = set(m for m in tf['methods'] if m[3] != 'primary')
        c['demons'] += len(dem_s | dem_t)
        c['demons_agree'] += len(dem_s & dem_t)
        c['locals'] += len(d['locals'] | tf['locals'])
        c['locals_agree'] += len(d['locals'] & tf['locals'])
        for aspect, direction, item in nd:
            c['dis_%s_%s' % (aspect, direction)] += 1
            if d['macro_bank'] and direction != 'differ' and aspect in ('method', 'local'):
                cause = 'macro: class uses macro bank %s (expansion not modelled)' % (d['macro_bank'][1],)
            elif d['unparsed'] and direction != 'differ' and aspect in ('method', 'local'):
                cause = 'unparsed: %d source items not parsed by esplex' % d['unparsed']
            elif item.startswith('local? '):
                cause = 'misread: source clause in the local part read as a method head'
            elif cid == 'paragraph##paragraph_version':
                cause = 'version: the source is release 3200, the object 3500 (layers/FORMATS.md §1)'
            else:
                cause = ''
            c['cause_' + (cause.split(':')[0] if cause else 'unexplained')] += 1
            rows.append((program, cid, '%s:%d' % (d['file'], d['line']), aspect, direction, item, cause))
    return dict(counts=c, rows=rows)


def summary_line(program, c):
    def pct(a, b):
        return '%d/%d' % (c[a], c[b])
    return ('%s: %d ESP files (%d items unparsed), %d templates, %d with source (%d exact, %d folded), '
            '%d all-agree; nature lists %s, slots %s, methods %s (demons %s), locals %s'
            % (program, c['esp_files'], c['unparsed_items'], c['templates'],
               c['matched_exact'] + c['matched_folded'], c['matched_exact'], c['matched_folded'],
               c['classes_all_agree'], pct('nature_lists_agree', 'nature_lists'),
               pct('slots_agree', 'slots'), pct('methods_agree', 'methods'),
               pct('demons_agree', 'demons'), pct('locals_agree', 'locals')))


def main(argv):
    root = argv[argv.index('--held') + 1] if '--held' in argv else None
    tsv = argv[argv.index('--tsv') + 1] if '--tsv' in argv else None
    skip = {root, tsv}
    progs = [a for a in argv if not a.startswith('--') and a not in skip] or list(PROGRAMS)
    allrows = []
    for p in progs:
        r = run(p, root)
        c = r['counts']
        print(summary_line(p, c))
        print('    disagreements: ' + ' '.join('%s %d' % (k[4:], v) for k, v in sorted(c.items())
                                                if k.startswith('dis_')))
        allrows += r['rows']
    if tsv:
        with open(tsv, 'w') as f:
            f.write('program\tclass\tsource\taspect\tdirection\titem\tcause\n')
            for row in allrows:
                f.write('\t'.join(str(x) for x in row) + '\n')
        print('%d disagreement rows written to %s' % (len(allrows), tsv))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
