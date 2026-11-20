#!/usr/bin/env python3
"""Do the PIMOS object files (.sav) match the held PIMOS source?

Read-only probe for docs/binary_reverse_engineering.md.  For every
module of the 20 .sav files in pimosobj.tar.Z: its name, the set of
predicates in its code area (name/arity of each predicate head), and
the same set read from the source file in pimos.tar.Z that declares
`:- module NAME.`.  Compiler-made predicates (`$...`) are left out of
the comparison.  The source reader is crude (kl1decomp.source_clauses):
it counts every branch of a `:- switch`, so "source only" overstates.

    python3 asm/savsrc.py             per-file summary
    python3 asm/savsrc.py --modules   one line per module
    python3 asm/savsrc.py --patches   patch modules against base and source
    python3 asm/savsrc.py --diff MOD  predicate lists of one module
"""
import collections
import io
import os
import re
import struct
import subprocess
import sys
import tarfile
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import census  # noqa: E402
import kl1decomp  # noqa: E402
import unlsav  # noqa: E402

SRC_TAR = os.path.join(HERE, '..', 'docs', 'nonlocal', 'pimos.tar.Z')


def _jis_name(words):
    out = []
    for w in words:
        if w >> 8 == 0:
            out.append(chr(w))
            continue
        try:
            out.append((b'\x1b$B' + bytes([w >> 8, w & 255])).decode('iso2022_jp'))
        except UnicodeDecodeError:
            out.append('?')
    return unicodedata.normalize('NFKC', ''.join(out))


def _read_atom_name(r):
    """unlsav.read_atom_name, keeping both bytes of each character (the
    original keeps the low byte, which turns `_` into `2`)."""
    aid = r.rd()
    if aid < 0x8000:
        return aid, r.atoms.get(aid, '')
    ln = (r.rd() << 16) | r.rd()
    name = _jis_name([r.rd() for _ in range(ln)])
    r.atoms[aid & 0x7fff] = name
    return aid & 0x7fff, name


def objects():
    """{file: (comment, [(module, package, {pred/arity}, code items)])}"""
    unlsav.read_atom_name = _read_atom_name
    out = collections.OrderedDict()
    for fname, raw in census.sav_files(None):
        words = list(struct.unpack('>%dH' % (len(raw) // 2), raw[:len(raw) // 2 * 2]))
        r = unlsav.Reader(words)
        magic, nmod, _sep = r.rd(), r.rd(), r.rd()
        comment = ''
        if magic in (0x5702, 0x5802):
            clen = (r.rd() << 16) | r.rd()
            comment = _jis_name([r.rd() for _ in range(clen)])
        mods = []
        for _ in range(nmod):
            _mlen, names, _gc, _hs, public, code = unlsav.parse_module(r)
            preds = set()
            for i, it in enumerate(code):
                if it[0] == 'inst' and it[3] == 0x24 and i >= 2 \
                        and code[i - 2][0] == 'atomref':
                    preds.add('%s/%d' % (code[i - 2][3], it[2] >> 24))
            ninst = sum(1 for it in code if it[0] == 'inst'
                        and it[3] in (0x22, 0x23)) + \
                sum(1 for it in code if it[0] == 'atom')
            mods.append((names[0][1], names[1][1], preds, ninst,
                         set('%s/%d' % (n, a) for n, a, _l in public)))
        out[fname] = (comment, mods)
    return out


def sources():
    """{module name: [(path, text)]} for every .kl1 under src/."""
    raw = subprocess.run(['gzip', '-dc', SRC_TAR], stdout=subprocess.PIPE,
                         check=True).stdout
    idx = collections.defaultdict(list)
    with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
        for m in tf.getmembers():
            if not m.isfile() or '/src/' not in m.name:
                continue
            text = tf.extractfile(m).read().decode('latin1')
            for name in re.findall(r'^\s*:-\s*(?:macro_)?module\s*\(?\s*([a-zA-Z0-9_]+)',
                                   text, re.M):
                idx[name].append((m.name, text))
    return idx


def source_preds(text):
    return set(_clauses(text))


def _clauses(text):
    # the reader of kl1decomp.source_clauses, on a text
    text = re.sub(r'"(?:[^"\\\n]|\\.|"")*"', '""', text)
    text = re.sub(r"'(?:[^'\n]|'')*'", 'q', text)
    text = re.sub(r'%.*', '', text)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    out = collections.Counter()
    for cl in re.split(r'\.(?:\s+|$)', text):
        cl = cl.strip()
        if not cl or cl.startswith(':-') or cl in ('otherwise', 'alternatively'):
            continue
        m = re.match(r'([a-z][A-Za-z0-9_]*)\s*(\(?)', cl)
        if not m:
            continue
        ar = 0
        if m.group(2):
            depth, ar = 0, 1
            for ch in cl[m.end() - 1:]:
                if ch in '([{':
                    depth += 1
                elif ch in ')]}':
                    depth -= 1
                    if depth == 0:
                        break
                elif ch == ',' and depth == 1:
                    ar += 1
        out['%s/%d' % (m.group(1), ar)] += 1
    return out


def compare(preds, texts):
    """(object preds not `$`, of those in a source file, object only,
    source only, path of the best-matching source file, object-only
    predicates whose NAME is in the source with another arity: what
    `:- local_implicit` and `-->` clauses give, the compiler adding
    arguments)."""
    mine = set(p for p in preds if not p.startswith('$'))
    best = None
    for path, text in texts:
        sp = source_preds(text)
        names = set(x.rsplit('/', 1)[0] for x in sp)
        only = sorted(mine - sp)
        row = (len(mine & sp), only, sorted(sp - mine), path,
               [x for x in only if x.rsplit('/', 1)[0] in names])
        if best is None or row[0] > best[0]:
            best = row
    return mine, best


def main(argv):
    objs, idx = objects(), sources()
    base = {}
    for fname, (_c, mods) in objs.items():
        if '_patch_' not in fname:
            for m in mods:
                base[m[0]] = (fname, m)
    if '--diff' in argv:
        want = argv[argv.index('--diff') + 1]
        for fname, (_c, mods) in objs.items():
            for name, _pkg, preds, ninst, _pub in mods:
                if name == want:
                    mine, best = compare(preds, idx.get(name, []))
                    print('%s in %s: %d predicates, %d instructions'
                          % (name, fname, len(mine), ninst))
                    if best:
                        print('  source %s: %d in common' % (best[3], best[0]))
                        print('  object only: %s' % ' '.join(best[1]))
                        print('  source only: %s' % ' '.join(best[2]))
        return 0
    if '--patches' in argv:
        for fname, (_c, mods) in objs.items():
            if '_patch_' not in fname:
                continue
            for name, _pkg, preds, ninst, _pub in mods:
                mine, best = compare(preds, idx.get(name, []))
                b = base.get(name)
                if b:
                    bp = set(p for p in b[1][2] if not p.startswith('$'))
                    bs = '%s: %d preds, %d instr; patch adds %d, drops %d' % (
                        b[0].replace('pimm_', '').replace('360E.sav', ''),
                        len(bp), b[1][3], len(mine - bp), len(bp - mine))
                    _m, bbest = compare(b[1][2], idx.get(name, []))
                else:
                    bs, bbest = 'NOT IN A BASE FILE', None
                src = 'no source module' if not best else \
                    'source %s: patch %d/%d in source, base %s' % (
                        best[3].split('/src/')[1], best[0], len(mine),
                        '-' if not bbest else '%d/%d' % (
                            bbest[0], len(bbest[1]) + bbest[0]))
                print('%-10s %-28s %3d preds %6d instr | base %s | %s'
                      % (fname[11:-8], name, len(mine), ninst, bs, src))
                if best and best[1]:
                    print('           patch predicates not in source: %s'
                          % ' '.join(best[1][:12]))
        return 0
    tot = collections.Counter()
    for fname, (comment, mods) in objs.items():
        n = collections.Counter()
        for name, _pkg, preds, ninst, _pub in mods:
            mine, best = compare(preds, idx.get(name, []))
            n['modules'] += 1
            n['preds'] += len(mine)
            if not best:
                n['no_source'] += 1
                n['preds_no_source'] += len(mine)
                if '--modules' in argv:
                    print('%-28s %-30s %4d preds  NO SOURCE MODULE'
                          % (fname[5:-4], name, len(mine)))
                continue
            n['in_source'] += best[0]
            n['name_only'] += len(best[4])
            n['exact'] += not best[1] and not best[2]
            n['object_subset'] += not best[1]
            if '--modules' in argv:
                print('%-28s %-30s %4d preds %4d in source, %3d object only, '
                      '%3d source only  %s' % (
                          fname[5:-4], name, len(mine), best[0], len(best[1]),
                          len(best[2]), best[3].split('/src/')[1]))
        tot.update(n)
        print('%-18s %-34r %3d modules, %2d without a source module; '
              '%5d predicates: %5d in source by name/arity, %4d more by '
              'name; modules with every object predicate in source %3d, '
              'identical sets %3d'
              % (fname[5:-8], comment, n['modules'], n['no_source'],
                 n['preds'], n['in_source'], n['name_only'],
                 n['object_subset'], n['exact']))
    print('TOTAL %d modules, %d without source; %d predicates, %d in '
          'source by name/arity (%.1f%%), %d more by name (%.1f%% '
          'together); every object predicate in source: %d modules; '
          'identical sets: %d' % (
              tot['modules'], tot['no_source'], tot['preds'], tot['in_source'],
              100.0 * tot['in_source'] / max(1, tot['preds']),
              tot['name_only'],
              100.0 * (tot['in_source'] + tot['name_only']) / max(1, tot['preds']),
              tot['object_subset'], tot['exact']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
